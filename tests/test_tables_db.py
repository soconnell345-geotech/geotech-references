"""Tests for the table-catalog FTS5 retrieval layer (_tables_db, REF-86).

The pattern of tests/test_figures_db.py: the committed catalogs' shape, the
search, the fetch, the scope rules shared with the figure and text layers,
a number held more than once, and results that fit a size limit. A small
made-up catalog (tmp_path) covers what the real catalogs need not hold.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from geotech_references import _tables_db

_PKG_DIR = Path(_tables_db.__file__).parent
CATALOGS = sorted(d.name for d in _PKG_DIR.iterdir()
                  if (d / "tables_catalog.json").is_file())


@pytest.fixture(scope="module", autouse=True)
def _ensure_db():
    _tables_db._ensure_db()
    yield


def _catalog(ref):
    return json.loads((_PKG_DIR / ref / "tables_catalog.json")
                      .read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Catalog shape (committed tables_catalog.json files)
# ---------------------------------------------------------------------------

def test_the_catalogs_ship_with_the_package():
    tomllib = pytest.importorskip("tomllib")
    data = tomllib.loads((_PKG_DIR.parent / "pyproject.toml")
                         .read_text(encoding="utf-8"))
    shipped = data["tool"]["setuptools"]["package-data"]["geotech_references"]
    assert "*/tables_catalog.json" in shipped


def test_the_most_used_references_have_a_catalog():
    for ref in ("dm7_1", "dm7_2", "gec_10", "gec_11", "gec_12", "gec_13",
                "fhwa_soils_foundations"):
        assert ref in CATALOGS


@pytest.mark.parametrize("ref", CATALOGS)
def test_catalog_envelope_and_rows(ref):
    cat = _catalog(ref)
    assert cat["package"] == ref
    assert cat["table_count"] == len(cat["tables"]) > 0
    for key in ("reference_id", "reference_title", "pdf_path"):
        assert cat[key], key
    for t in cat["tables"]:
        num = t["table_number"]
        assert num and t["caption"], num
        assert isinstance(t["pdf_page_index"], int) and t["pdf_page_index"] >= 0
        assert t["pages"][0] == t["pdf_page_index"], num
        assert t["pages"] == sorted(set(t["pages"])), num
        assert t["values"] in _tables_db.VALUES_KINDS, num
        if t["values"] == "page":
            assert t["values_in"] is None, num
        else:
            assert t["values_in"], num
        assert "section_id" in t and "printed_page" in t, num
        assert t.get("page_estimated") is False, f"{ref} {num} page estimated"


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

def test_inventory_lists_every_catalog_with_counts():
    inv = {r["reference"]: r for r in _tables_db.list_indexed_tables()}
    assert set(inv) == set(CATALOGS)
    for ref, r in inv.items():
        assert r["n_tables"] == len(_catalog(ref)["tables"])
        assert r["n_text"] + r["n_lookup"] + r["n_page"] == r["n_tables"]


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def test_search_finds_a_table_by_its_caption():
    hits = _tables_db.table_search("bearing capacity factors",
                                   reference="dm7_2", limit=5)
    assert "5-2" in [h["table_number"] for h in hits]


def test_search_finds_a_table_by_its_number():
    hits = _tables_db.table_search("Table 6-23", reference="dm7_2", limit=3)
    assert hits[0]["table_number"] == "6-23"


def test_search_finds_a_table_by_the_section_that_lists_it():
    # Table 6-36's caption says "Constants for Load and Moment Deflection
    # Equations"; the section that lists it is on the characteristic load
    # method, which the caption does not name
    hits = _tables_db.table_search("characteristic load method",
                                   reference="dm7_2", limit=10)
    assert "6-36" in [h["table_number"] for h in hits]


def test_search_hit_shape():
    hits = _tables_db.table_search("bearing capacity", reference="dm7_2",
                                   limit=3)
    assert hits
    for key in ("reference", "reference_title", "reference_id",
                "table_number", "caption", "chapter", "section_id",
                "pdf_page_index", "printed_page", "values", "values_in"):
        assert key in hits[0], key


def test_search_scoped_by_reference():
    hits = _tables_db.table_search("soil", reference="dm7_1", limit=20)
    assert hits and all(h["reference"] == "dm7_1" for h in hits)


def test_search_scoped_by_chapter():
    hits = _tables_db.table_search("resistance", reference="dm7_2",
                                   chapter=6, limit=20)
    assert hits and all(h["chapter"] == 6 for h in hits)


def test_search_limit_capped_and_empty_query():
    assert len(_tables_db.table_search("soil", limit=999)) <= 50
    assert _tables_db.table_search("   ") == []
    assert _tables_db.table_search("", max_chars=2000) == {"hits": [],
                                                           "shown": 0}


def test_a_hit_that_lacks_a_word_says_so():
    hits = _tables_db.table_search("bearing capacity zzyzxq",
                                   reference="dm7_2", limit=5)
    assert hits
    for h in hits:
        assert h["match"] == "any word" and "zzyzxq" in h["lacks"]


def test_a_volume_number_searches_that_volume_alone():
    hits = _tables_db.table_search("resistance factors",
                                   reference="FHWA-NHI-16-010", limit=20,
                                   max_chars=14000)
    assert hits["hits"], hits
    assert {h["reference"] for h in hits["hits"]} == {"gec_12"}
    assert {h["reference_id"] for h in hits["hits"]} == {"FHWA-NHI-16-010"}
    assert hits["report_number"] == "FHWA-NHI-16-010"


# ---------------------------------------------------------------------------
# Scope refusals (the rules of the figure and text searches)
# ---------------------------------------------------------------------------

def test_an_unknown_reference_is_refused_naming_the_catalogs():
    out = _tables_db.table_search("soil", reference="no_such_manual")
    assert "error" in out[0] and "dm7_2" in out[0]["error"]
    out = _tables_db.table_search("soil", reference="no_such_manual",
                                  max_chars=2000)
    assert "dm7_2" in out["error"]


def test_dm7_is_refused_naming_both_volumes_in_a_search():
    out = _tables_db.table_search("soil", reference="dm7", max_chars=2000)
    assert "dm7_1" in out["error"] and "dm7_2" in out["error"]


def test_a_chapter_with_no_tables_is_refused():
    out = _tables_db.table_search("soil", reference="dm7_2", chapter=99)
    assert "error" in out[0] and "chapters with tables" in out[0]["error"]


def test_a_loose_name_is_not_read_as_a_catalog():
    # 'gec_1' only begins gec_10 ... gec_14: it names nothing (core-09)
    out = _tables_db.table_search("soil", reference="gec_1", max_chars=2000)
    assert "error" in out


def test_another_spelling_reads_as_the_catalog():
    out = _tables_db.table_search("resistance", reference="GEC-10",
                                  max_chars=14000)
    assert out["resolved_reference"] == "gec_10"
    assert all(h["reference"] == "gec_10" for h in out["hits"])


# ---------------------------------------------------------------------------
# Get / resolve
# ---------------------------------------------------------------------------

def test_get_a_table_and_how_to_read_it():
    g = _tables_db.table_get("dm7_2", "Table 6-23")
    assert g["table_number"] == "6-23" and g["chapter"] == 6
    assert g["values"] == "lookup"
    assert g["values_in"] == "chapter6.table_6_23_kt"
    assert g["pdf_path"].endswith("ufc_3_220_20_2025.pdf")
    assert "table_6_23_kt" in g["how_to_read"]


def test_get_tolerates_a_dash_of_any_kind_and_a_prefix():
    a = _tables_db.table_get("dm7_2", "6-23")
    assert _tables_db.table_get("dm7_2", "TABLE 6–23") == a
    assert _tables_db.table_get("dm7_2", " table 6-23. ") == a


def test_get_reads_dot_and_dash_alike_when_the_number_is_not_filed():
    a = _tables_db.table_get("gec_7", "3.1a")
    assert _tables_db.table_get("gec_7", "Table 3-1a") == a
    assert _tables_db.table_get("gec_7", "3.1(a)") == a


def test_dm7_reads_by_the_table_asked_for():
    # Table P-1 is printed in UFC 3-220-20 alone
    assert _tables_db.table_get("dm7", "P-1")["reference"] == "dm7_2"
    with pytest.raises(KeyError) as e:
        _tables_db.table_get("dm7", "1-1")      # printed in both
    assert "more than one catalog" in str(e.value)


def test_get_unknown_raises_naming_the_nearest():
    with pytest.raises(KeyError) as e:
        _tables_db.table_get("dm7_2", "6-99")
    assert "nearest table numbers" in str(e.value)
    with pytest.raises(KeyError):
        _tables_db.table_get("no_such_manual", "1-1")


def test_a_page_only_table_says_to_read_the_page():
    rows = [t for t in _catalog("dm7_1")["tables"] if t["values"] == "page"]
    g = _tables_db.table_get("dm7_1", rows[0]["table_number"])
    assert g["values"] == "page" and g["values_in"] is None
    assert str(g["pdf_page_index"]) in g["how_to_read"]


def test_resolve_table_pdf_points_at_the_page():
    g = _tables_db.table_get("dm7_2", "6-23")
    try:
        pdf_abs, page = _tables_db.resolve_table_pdf("dm7_2", "6-23")
    except FileNotFoundError:
        pytest.skip("the UFC 3-220-20 PDF is not checked out")
    assert pdf_abs.exists() and page == g["pdf_page_index"]


# ---------------------------------------------------------------------------
# A made-up catalog: a number printed twice, a table over three pages,
# a long caption, and a rebuild when the catalog changes
# ---------------------------------------------------------------------------

_MADE_UP = {
    "reference_id": "XX-00-001", "reference_title": "Made-up Manual",
    "package": "made_up", "volume": None, "pdf_path": "docs/made_up.pdf",
    "table_count": 3,
    "tables": [
        {"table_number": "2-1", "caption": "Widget Grades", "chapter": 2,
         "section_id": "2.1", "section_title": "Widgets",
         "pdf_page_index": 10, "pages": [10, 11, 12], "printed_page": "2-4",
         "page_estimated": False, "values": "page", "values_in": None},
        {"table_number": "A-1", "caption": "Gadget Sizes", "chapter": None,
         "section_id": None, "section_title": None,
         "pdf_page_index": 40, "pages": [40], "printed_page": "A-2",
         "page_estimated": False, "values": "text", "values_in": "A.1"},
        {"table_number": "A-1", "caption": "Sprocket Teeth " + "x" * 3000,
         "chapter": None, "section_id": None, "section_title": None,
         "pdf_page_index": 44, "pages": [44], "printed_page": "A-6",
         "page_estimated": False, "values": "page", "values_in": None},
    ],
}


@pytest.fixture()
def made_up(tmp_path, monkeypatch):
    pkg = tmp_path / "made_up"
    pkg.mkdir()
    cat = pkg / "tables_catalog.json"
    cat.write_text(json.dumps(_MADE_UP), encoding="utf-8")
    monkeypatch.setattr(_tables_db, "_iter_catalogs", lambda: [cat])
    monkeypatch.setattr(_tables_db, "_db_path",
                        lambda: tmp_path / "tables.sqlite")
    return cat


def test_a_number_printed_twice_needs_its_page(made_up):
    with pytest.raises(KeyError) as e:
        _tables_db.table_get("made_up", "A-1")
    assert "2 times" in str(e.value)
    assert "page index 40" in str(e.value) and "page index 44" in str(e.value)
    assert _tables_db.table_get("made_up", "A-1", pdf_page_index=40)[
        "caption"] == "Gadget Sizes"
    with pytest.raises(KeyError) as e:
        _tables_db.table_get("made_up", "A-1", pdf_page_index=41)
    assert "not on page index 41" in str(e.value)


def test_any_sheet_of_a_table_finds_it(made_up):
    g = _tables_db.table_get("made_up", "2-1", pdf_page_index=12)
    assert g["pdf_page_index"] == 10 and g["pages"] == [10, 11, 12]
    hit = _tables_db.table_search("widget", reference="made_up")[0]
    assert hit["pages"] == [10, 11, 12]


def test_one_hit_per_table_whatever_its_sheets(made_up):
    hits = _tables_db.table_search("widget grades", limit=10)
    assert len(hits) == 1


def test_results_fit_a_size_limit(made_up):
    out = _tables_db.table_search("sprocket", max_chars=1200)
    assert len(json.dumps(out)) <= 1200
    assert out["hits"][0]["table_number"] == "A-1"
    g = _tables_db.table_get("made_up", "A-1", pdf_page_index=44,
                             max_chars=1500)
    assert len(json.dumps(g)) <= 1500 and "Cut to fit" in g["note"]


def test_an_empty_result_names_the_scope_and_the_missing_words(made_up):
    out = _tables_db.table_search("qqqq", reference="made_up",
                                  max_chars=2000)
    assert out["hits"] == [] and out["words_not_found"] == ["qqqq"]
    assert "made_up" in out["note"]


def test_the_database_is_rebuilt_when_the_catalog_changes(made_up):
    assert _tables_db.table_search("gizmo", reference="made_up") == []
    data = json.loads(made_up.read_text(encoding="utf-8"))
    data["tables"][0]["caption"] = "Gizmo Grades"
    made_up.write_text(json.dumps(data), encoding="utf-8")
    hits = _tables_db.table_search("gizmo", reference="made_up")
    assert [h["table_number"] for h in hits] == ["2-1"]


def test_paging_lists_the_plain_calls_hits_in_order():
    plain = _tables_db.table_search("soil", limit=10)
    first = _tables_db.table_search("soil", limit=5, max_chars=14000)
    second = _tables_db.table_search("soil", limit=5, offset=5,
                                     max_chars=14000)
    key = lambda h: (h["reference"], h["table_number"],  # noqa: E731
                     h["pdf_page_index"])
    assert [key(h) for h in first["hits"] + second["hits"]] == \
        [key(h) for h in plain]
    assert first["next_offset"] == 5
