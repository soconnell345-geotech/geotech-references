"""A figure number the catalog holds more than once is never answered with
the first row.

2026-11-10 review (core-02): ``figure_get`` took the first row of a number
(``LIMIT 1``), so the read-off of a figure whose number two rows share went
to the first row's page without a word. The rows that share a number are of
two kinds, both from the print:

* a number the print gives two figures: UFC 3-250-01 prints "Figure F-21"
  on PDF page 264 (printed 244, M1078 2-1/2 Ton Cargo Truck) and again on
  PDF page 265 (printed 245, P-22 Crash Truck), and no Figure F-22; GEC-13
  Vol II prints "Figure 6-14" on PDF pages 52 and 54;
* a figure that runs over several pages, one row per page: GEC-12 Vol III
  Figures D-1 (PDF pages 36-41, printed 2-7), D-2 (45-47, printed 11-13),
  D-3 (48-49, printed 14-15) and D-4 (50-52, printed 16-18).

The catalog also numbered GEC-11's Figure 5-11 as a second 5-14, and gave
every continuation row of D-1 to D-4 the first page's index.
"""

import json
from collections import defaultdict
from pathlib import Path

import pytest

from geotech_references import _figures_db

PKG = Path(_figures_db.__file__).parent
CATALOGS = sorted(d.name for d in PKG.iterdir()
                  if (d / "figures_catalog.json").is_file())

#: The numbers the print repeats: (catalog, number) -> how many rows.
PRINT_REPEATS = {
    ("ufc_pavement", "F-21"): 2,
    ("gec_13", "6-14"): 2,
    ("gec_12", "D-1"): 6,
    ("gec_12", "D-2"): 3,
    ("gec_12", "D-3"): 2,
    ("gec_12", "D-4"): 3,
    # "Figure D-3 ... (Sheet n of 4)", PDF pages 208-211 (printed 188-191);
    # catalogued as "D-3 (Sheet n of 4)" before (2026-11-10 review)
    ("ufc_pavement", "D-3"): 4,
}


def _rows_by_number(catalog):
    data = json.loads((PKG / catalog / "figures_catalog.json").read_text(
        encoding="utf-8"))
    by = defaultdict(list)
    for fig in data["figures"]:
        by[_figures_db._norm_fig_number(fig["figure_number"])].append(fig)
    return by


@pytest.mark.parametrize("catalog", CATALOGS)
def test_no_number_is_repeated_unless_the_print_repeats_it(catalog):
    repeated = {n: rows for n, rows in _rows_by_number(catalog).items()
                if len(rows) > 1}
    for number, rows in repeated.items():
        assert PRINT_REPEATS.get((catalog, number)) == len(rows), (
            f"{catalog}: figure {number} is in the catalog {len(rows)} "
            "times; a number repeats only where the print repeats it")
        # each row is its own page of its own PDF, so a page says which
        pages = [(r.get("pdf_path"), r["pdf_page_index"]) for r in rows]
        assert len(set(pages)) == len(pages), (catalog, number, pages)
    assert {n for c, n in PRINT_REPEATS if c == catalog} == set(repeated)


@pytest.mark.parametrize("catalog,number", sorted(PRINT_REPEATS))
def test_a_repeated_number_is_refused_until_a_page_says_which(catalog,
                                                              number):
    rows = _rows_by_number(catalog)[number]
    with pytest.raises(KeyError) as e:
        _figures_db.figure_get(catalog, number)
    msg = str(e.value)
    assert f"{len(rows)} times" in msg and "pdf_page_index" in msg
    for row in rows:
        assert f"page index {row['pdf_page_index']}" in msg
        assert row["caption"][:60] in msg
    with pytest.raises(KeyError):
        _figures_db.resolve_pdf(catalog, number)
    for row in rows:
        got = _figures_db.figure_get(catalog, number,
                                     pdf_page_index=row["pdf_page_index"])
        assert got["caption"] == row["caption"]
        assert got["pdf_page_index"] == row["pdf_page_index"]
        try:
            _, page = _figures_db.resolve_pdf(
                catalog, number, pdf_page_index=row["pdf_page_index"])
        except FileNotFoundError:
            continue  # the PDF is not in this checkout
        assert page == row["pdf_page_index"]


def test_a_page_the_figure_is_not_on_names_its_pages():
    with pytest.raises(KeyError) as e:
        _figures_db.figure_get("ufc_pavement", "F-21", pdf_page_index=10)
    assert "page index 263" in str(e.value) and "page index 264" in str(e.value)
    # a number held once takes the page too, and checks it
    one = _figures_db.figure_get("dm7_2", "4-12")
    assert _figures_db.figure_get(
        "dm7_2", "4-12", pdf_page_index=one["pdf_page_index"]) == one
    with pytest.raises(KeyError, match="is not on page index"):
        _figures_db.figure_get("dm7_2", "4-12",
                               pdf_page_index=one["pdf_page_index"] + 1)


def test_the_two_f21_figures_are_the_printed_ones():
    # UFC 3-250-01 PDF page 264 (printed 244) and PDF page 265 (printed 245)
    first = _figures_db.figure_get("ufc_pavement", "F-21", pdf_page_index=263)
    second = _figures_db.figure_get("ufc_pavement", "F-21", pdf_page_index=264)
    assert first["caption"].startswith("M1078 2-1/2 Ton Cargo Truck")
    assert first["printed_page"] == 244
    assert second["caption"].startswith("P-22 Crash Truck")
    assert second["printed_page"] == 245


def test_gec11_figure_5_11_is_the_inundation_detail():
    # GEC-11 Vol I PDF page 243 (printed 5-17): "Figure 5-11. Example detail
    # for wall that may experience inundation."; the catalog had it as a
    # second 5-14 (Figure 5-14 is the geomembrane barrier, PDF page 248)
    fig = _figures_db.figure_get("gec_11", "5-11")
    assert fig["caption"] == ("Example detail for wall that may experience "
                              "inundation")
    assert fig["pdf_page_index"] == 242 and fig["volume"] == 1
    barrier = _figures_db.figure_get("gec_11", "5-14")
    assert "geomembrane barrier" in barrier["caption"]
    assert barrier["pdf_page_index"] == 247


@pytest.mark.parametrize("number,printed_page,page_index,caption", [
    # GEC-12 Vol III: PDF page = printed page + 34 (index + 33)
    ("D-1", 2, 35, "Design process flow chart"),
    ("D-1", 4, 37, "Design process flow chart (continued)"),
    ("D-1", 7, 40, "Design process flow chart (continued)"),
    ("D-2", 12, 45, "Boring Log S-1, Page 2 of 3"),
    ("D-2", 13, 46, "Boring Log S-1, Page 3 of 3"),
    ("D-3", 15, 48, "Boring Log S-2, Page 2 of 2"),
    ("D-4", 17, 50, "Boring Log S-3, Page 2 of 3"),
    ("D-4", 18, 51, "Boring Log S-3, Page 3 of 3"),
])
def test_gec12_appendix_d_rows_point_at_their_own_pages(
        number, printed_page, page_index, caption):
    fig = _figures_db.figure_get("gec_12", number, pdf_page_index=page_index)
    assert fig["caption"] == caption
    assert fig["printed_page"] == printed_page and fig["volume"] == 3


def test_search_lists_both_rows_of_a_number_with_their_pages():
    hits = _figures_db.figure_search("F-21 truck plain concrete RCCP",
                                     reference="ufc_pavement", limit=50)
    pages = sorted(h["pdf_page_index"] for h in hits
                   if h["figure_number"] == "F-21")
    assert pages == [263, 264]


# A figure printed over several pages is one search hit (2026-11-10 review
# follow-up): core-02 kept every row of a repeated number in figure_search,
# so the continuation sheets of GEC-12 D-1 to D-4 and UFC 3-250-01 D-3 took
# the places of other figures. The rows of one number whose captions differ
# only by a sheet label are one hit listing their pages; two figures printed
# under one number (F-21, GEC-13 6-14) stay two.

SHEETS = {
    ("gec_12", "D-1"): [35, 36, 37, 38, 39, 40],
    ("gec_12", "D-2"): [44, 45, 46],
    ("gec_12", "D-3"): [47, 48],
    ("gec_12", "D-4"): [49, 50, 51],
    ("ufc_pavement", "D-3"): [207, 208, 209, 210],
}


@pytest.mark.parametrize("kwargs", [{}, {"max_chars": 14000}])
@pytest.mark.parametrize("query,reference", [
    ("design process flow chart continued", "gec_12"),
    ("Boring Log S-1, Page 2", "gec_12"),
    ("boring log SPT", "gec_12"),
    ("frost penetration insulation base", "ufc_pavement"),
])
def test_a_figure_over_several_pages_is_one_hit(query, reference, kwargs):
    out = _figures_db.figure_search(query, reference=reference, limit=10,
                                    **kwargs)
    hits = out["hits"] if isinstance(out, dict) else out
    seen = [(h["reference"], h["figure_number"]) for h in hits]
    assert len(seen) == len(set(seen)), seen
    sheeted = [h for h in hits if (h["reference"], h["figure_number"])
               in SHEETS]
    assert sheeted
    for h in sheeted:
        pages = SHEETS[(h["reference"], h["figure_number"])]
        assert [p["pdf_page_index"] for p in h["pages"]] == pages
        assert h["pdf_page_index"] in pages


def test_the_best_ranked_sheet_is_the_hit_s_page():
    hit = next(h for h in _figures_db.figure_search(
        "Boring Log S-1, Page 2", reference="gec_12", limit=5)
        if h["figure_number"] == "D-2")
    assert (hit["pdf_page_index"], hit["caption"]) == (
        45, "Boring Log S-1, Page 2 of 3")
    assert hit["pages"][1] == {"pdf_page_index": 45, "printed_page": 12}


def test_two_figures_under_one_number_stay_two_hits():
    f21 = [h for h in _figures_db.figure_search(
        "F-21", reference="ufc_pavement", limit=10)
        if h["figure_number"] == "F-21"]
    assert sorted(h["pdf_page_index"] for h in f21) == [263, 264]
    assert not any("pages" in h for h in f21)
    for query, page in (("triangular column arrangements biaxial", 51),
                        ("beam method", 53)):
        hit = next(h for h in _figures_db.figure_search(
            query, reference="gec_13", limit=10)
            if h["figure_number"] == "6-14")
        assert hit["pdf_page_index"] == page and "pages" not in hit


def test_sheets_no_longer_crowd_out_main_s_top_ten():
    """'driven pile design process flow chart' in gec_12: main's tenth
    figure (7-32) had been pushed out by D-1's second sheet."""
    numbers = [h["figure_number"] for h in _figures_db.figure_search(
        "driven pile design process flow chart", reference="gec_12",
        limit=10)]
    assert "7-32" in numbers and numbers.count("D-1") == 1
