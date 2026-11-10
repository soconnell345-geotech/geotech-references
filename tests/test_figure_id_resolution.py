"""Figure lookups resolve the reference ids models actually write.

GeotechStaffEngineer live smoke wave 1 (G4): ``read_reference_figure`` failed
9 times in 5 runs because the catalog id (``gec_10``, ``dm7_2``,
``ufc_pavement``) differs from the module name (``gec10``, ``dm7``) and the
document's designation (``UFC 3-250-01``), and a miss said only "Figure not
found". Every figure asked for existed.
"""

import pytest

from geotech_references import _figures_db as fdb


@pytest.mark.parametrize("ref,fig,want", [
    ("gec_10", "10-6", "gec_10"),
    ("gec10", "10-6", "gec_10"),
    ("GEC-10", "Figure 10-6", "gec_10"),
    ("GEC 10", "Fig. 10-6", "gec_10"),
    ("UFC 3-250-01", "E-1", "ufc_pavement"),
    ("ufc_pavement", "F-1", "ufc_pavement"),
])
def test_spellings_of_a_reference_resolve(ref, fig, want):
    rec = fdb.figure_get(ref, fig)
    assert rec["reference"] == want
    assert rec["figure_number"].upper() == fdb._norm_fig_number(fig)


@pytest.mark.parametrize("ref,want", [
    # a manual whose volumes carry their own report numbers was listed once
    # per number, so its own name failed as "in more than one catalog --
    # gec_13; gec_13" (2026-11-10 review, core-09)
    ("GEC-13", "gec_13"), ("gec13", "gec_13"),
    # the report number on a volume's cover, with or without the agency
    ("FHWA-NHI-16-027", "gec_13"), ("FHWA-NHI-16-028", "gec_13"),
    ("NHI-16-028", "gec_13"), ("3-250-01", "ufc_pavement"),
])
def test_a_name_or_report_number_resolves_to_its_one_catalog(ref, want):
    assert fdb.resolve_reference(ref) == want
    number = fdb._ro_connect().execute(
        "SELECT figure_number FROM figures WHERE reference = ? "
        "GROUP BY UPPER(figure_number) HAVING COUNT(*) = 1 LIMIT 1",
        (want,)).fetchone()[0]
    # the result names the catalog it came from, whatever the caller wrote
    assert fdb.figure_get(ref, number)["reference"] == want


@pytest.mark.parametrize("loose", [
    "FHWA",      # began fhwa_pavements and fhwa_soils_foundations
    "gec_1",     # began gec_10 ... gec_14
    "GEC",       # began eleven catalogs
    "UFC",       # began every ufc_* catalog
    "pile",      # a word in several titles
    "Soil Mechanics",   # part of a title
    "GEC-3",     # a manual the library does not hold
])
def test_a_loose_name_resolves_to_nothing(loose):
    """2026-11-10 review, core-09: a name that only began a catalog id, or
    sat inside a title, resolved to whichever catalog held the figure
    number. It now names no catalog, and the caller is given the ids."""
    with pytest.raises(KeyError) as e:
        fdb.figure_get(loose, "5-2")
    assert "Use a catalog id" in str(e.value) and "gec_10" in str(e.value)
    for kwargs in ({}, {"max_chars": 14000}):
        out = fdb.figure_search("pile", reference=loose, **kwargs)
        err = out["error"] if isinstance(out, dict) else out[0]["error"]
        assert "no figure catalog" in err and "dm7_2" in err


def test_a_module_name_covering_two_catalogs_names_both():
    with pytest.raises(KeyError) as e:
        fdb.figure_get("dm7", "4-12")
    msg = str(e.value)
    assert "dm7_1" in msg and "dm7_2" in msg


def test_a_figure_only_one_catalog_holds_is_found_through_the_module_name():
    # find a figure number present in exactly one of dm7_1 / dm7_2
    import sqlite3
    conn = fdb._ro_connect()
    try:
        rows = conn.execute(
            "SELECT UPPER(figure_number) AS n, GROUP_CONCAT(reference) AS r "
            "FROM figures WHERE reference IN ('dm7_1','dm7_2') "
            "GROUP BY UPPER(figure_number) HAVING COUNT(*) = 1 LIMIT 1"
        ).fetchall()
    finally:
        conn.close()
    assert rows
    number, ref = rows[0]["n"], rows[0]["r"]
    assert fdb.figure_get("dm7", number)["reference"] == ref


def test_misses_name_the_valid_ids_and_the_nearest_figures():
    with pytest.raises(KeyError) as e:
        fdb.figure_get("nope", "1-1")
    assert "gec_10" in str(e.value) and "dm7_2" in str(e.value)
    with pytest.raises(KeyError) as e:
        fdb.figure_get("gec_10", "10-99")
    assert "nearest figure numbers" in str(e.value)
    assert "figure_search" in str(e.value)


def test_resolve_pdf_and_search_take_the_same_spellings():
    try:
        path, page = fdb.resolve_pdf("gec10", "10-6")
    except FileNotFoundError:
        pytest.skip("source PDF not present in this checkout")
    assert page >= 0 and path.name.lower().endswith(".pdf")
    hits = fdb.figure_search("alpha adhesion", reference="gec10", limit=3)
    assert hits and all(h["reference"] == "gec_10" for h in hits)
