"""Catalog rows lead to their figure and are filed under their chapter
(2026-11-10 review, coverage/catalog_rows_failing.md).

Every value here was read off the rendered page:

* the figure is on the page before its caption, so the row named the
  caption's page (UFS 3-220-10 Figures 1-13, 3-1, 5-4, 6-9); the row named
  the next figure's page, the contents page or a page that only cites it
  (GEC-10 4-5, GEC-14 A-1 to A-3, GEC-9 6-17);
* the number as printed: UFC 3-250-01 "Figure C14-5B" (PDF page 165) and
  "Figure D-3 ... (Sheet n of 4)" on four pages (PDF pages 208-211, printed
  188-191); FHWA NHI-06-089 "Figure 9-37(a)" and "Figure 9-37(b)" (PDF
  page 198, printed 9-88) are filed '9-37a' and '9-37b', the form the
  library gives a part letter, and the printed form now finds them;
* the chapter: GEC-7 and GEC-8 number their figures <chapter>.<n> and the
  rows had none; GEC-4 numbers its figures 1-73 through the manual and each
  row had its own number as its chapter. Its chapters open on PDF pages
  22, 25, 40, 47, 67, 145, 158, 177 and 185 (chapters 1-9), its references
  on page 201.

The page check reads each row's page with PyMuPDF and skips without it or
the PDFs. A row whose page's text layer does not print "Figure <number>"
is listed in TEXT_LAYER_LACKS: the caption is part of a picture, the text
layer is a poor scan's, or (UFS 3-220-10 1-13 and 3-1) the caption is on
the next page. The list is strict, so a row that moves to a page without
its number fails, and so does a listed row that no longer needs listing.
"""

import json
import re
from pathlib import Path

import pytest

from geotech_references import _figures_db

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references"
CATALOGS = sorted(d.name for d in PKG.iterdir()
                  if (d / "figures_catalog.json").is_file())


def _catalog(ref):
    return json.loads((PKG / ref / "figures_catalog.json").read_text(
        encoding="utf-8"))


@pytest.mark.parametrize("ref,number,index,printed", [
    ("dm7_1", "1-13", 74, 47),
    ("dm7_1", "3-1", 172, 145),
    ("dm7_1", "5-4", 253, 226),
    ("dm7_1", "6-9", 332, 305),
    ("gec_10", "4-5", 77, "4-6"),
    ("gec_14", "A-1", 45, None),   # printed A1
    ("gec_14", "A-2", 46, None),
    ("gec_14", "A-3", 47, None),
    ("gec_9", "6-17", 100, 97),
])
def test_a_row_names_the_page_its_figure_is_on(ref, number, index, printed):
    row = _figures_db.figure_get(ref, number)
    assert (row["pdf_page_index"], row["printed_page"]) == (index, printed)


def test_numbers_as_printed():
    assert _figures_db.figure_get("ufc_pavement", "C14-5B")[
        "pdf_page_index"] == 164
    for n, index in enumerate(range(207, 211), start=1):
        row = _figures_db.figure_get("ufc_pavement", "D-3",
                                     pdf_page_index=index)
        assert row["caption"].endswith(f"(Sheet {n} of 4)")
        assert row["printed_page"] == 187 + n
    with pytest.raises(KeyError) as e:
        _figures_db.figure_get("ufc_pavement", "D-3")
    assert "4 times" in str(e.value)
    a = _figures_db.figure_get("fhwa_soils_foundations", "Figure 9-37(a).")
    b = _figures_db.figure_get("fhwa_soils_foundations", "9-37 (b)")
    assert a == _figures_db.figure_get("fhwa_soils_foundations", "9-37a")
    assert a["pdf_page_index"] == b["pdf_page_index"] == 197
    assert "fill weight" in a["caption"]
    assert "ground water lowering" in b["caption"]


def test_a_bracketed_part_letter_is_looked_up_both_ways():
    """A catalog (a local pack) that files '9-37(a)' as printed still finds
    it; one that files '9-37a' finds the printed form."""
    assert _figures_db._fig_number_keys("Figure 9-37(a).") == (
        "9-37(A)", "9-37A")
    assert _figures_db._fig_number_keys("9-37a") == ("9-37A",)
    assert _figures_db._fig_number_keys("D-3") == ("D-3",)


def _chapters(ref):
    return {json.loads(p.read_text(encoding="utf-8")).get("chapter")
            for p in (PKG / ref / "text").glob("*.json")}


@pytest.mark.parametrize("ref", ["gec_4", "gec_7", "gec_8"])
def test_every_numbered_figure_is_filed_under_a_chapter_of_the_text(ref):
    have = _chapters(ref)
    for fig in _catalog(ref)["figures"]:
        # GEC-8 Appendix A ("A.1"), GEC-4 Appendices A, B and D ("A-1")
        if re.match(r"[A-Z][-.]", fig["figure_number"]):
            assert fig["chapter"] is None
            continue
        assert fig["chapter"] in have, (ref, fig["figure_number"])


@pytest.mark.parametrize("ref", CATALOGS)
def test_a_figure_numbered_by_chapter_is_filed_under_it(ref):
    """'4-5' and '4.5' are figures of chapter 4 wherever a catalog gives an
    integer chapter (GEC-4 numbers its figures through the manual)."""
    if ref == "gec_4":
        pytest.skip("figures numbered 1-73 through the manual")
    for fig in _catalog(ref)["figures"]:
        m = re.match(r"(\d+)[-.]", fig["figure_number"])
        if m and isinstance(fig.get("chapter"), int):
            assert fig["chapter"] == int(m.group(1)), (
                ref, fig["figure_number"], fig["chapter"])


def test_gec4_figures_by_chapter():
    by = {}
    for fig in _catalog("gec_4")["figures"]:
        if not fig["figure_number"].isdigit():   # Appendices A, B and D
            assert fig["chapter"] is None
            continue
        by.setdefault(fig["chapter"], []).append(int(fig["figure_number"]))
    # in order through the manual, each chapter a run of numbers
    assert [n for c in sorted(by) for n in by[c]] == list(range(1, 74))
    assert sorted(by) == [2, 3, 4, 5, 6, 7]
    assert 11 in by[4]   # "These conditions are illustrated in figure 11"


#: Rows whose page's text layer does not print "Figure <number>" (see the
#: module docstring). aashto_1993 is a scan with no text layer, and the
#: wood_handbook PDF is not in docs/.
NO_TEXT_LAYER = {"aashto_1993", "wood_handbook"}
TEXT_LAYER_LACKS = {
    "dm7_1": {
        '1-13', '3-1'},
    "eurocode_7_1": {
        'D.1'},
    "eurocode_7_2": {
        'B.1', 'D.1', 'G.1', 'I.1', 'I.2', 'I.3', 'I.4', 'K.1',
        'B.5'},   # the scan's text layer reads "Figure B.S"
    # the text cites Figure A.7-2; its caption label is printed "A7-2"
    "fhwa_soils_foundations": {
        'A.7-2'},
    "gec_11": {
        '2-5', '2-8', '2-10', '2-15', '2-21', '2-22', '3-2', '3-4', '3-5',
        '4-3', '4-9', '4-12', '4-13', '4-19', '5-1', '5-2', '5-3', '5-4',
        '5-6', '5-8', '5-10', '5-11', '5-13', '5-14', '5-17', '5-18',
        '5-19', '5-20', '5-21', '5-25', '5-27', '5-28', '5-29', '5-30',
        '5-31', '5-32', '5-33', '5-34', '6-1', '6-2', '6-3', '6-6', '6-7',
        '6-8', '6-11', '6-12', '6-13', '6-14', '6-16', '7-2', '8-3',
        '8-5', '8-7', '8-12', '9-2', '9-5', '9-6', '9-8', '9-10', '11-3',
        '11-4', '11-6', '11-7', '11-10'},
    "gec_14": {
        'A-1', 'A-2', 'A-3'},
    "gec_8": {
        '2.2', '2.3', '3.11', '4.1', '4.3', '4.5', '4.11', '4.12', '4.13',
        '4.14', '4.15', '4.17', '4.19', '4.21', '4.22', '5.1', '5.3',
        '5.4', '5.5', '5.6', '5.7', '5.8', '5.9', '5.11', '5.12', '5.13',
        '5.14', '5.15', '5.16', '5.17', '5.18', '5.19', '5.20', '5.21',
        '5.22', '5.24', '5.25', '5.26', '5.27', '5.30', '5.31', '5.32',
        '5.33', '5.34', '5.35', '6.1', '6.2', '6.3', '6.6', '6.8', '6.9',
        '7.6', '7.17', 'A.1', 'A.3', 'A.4', 'A.5', 'A.9', 'A.10', 'A.11',
        'A.12', 'A.13', 'A.15', 'A.16', 'A.17'},
    "ufc_expansive": {
        '1-1', '1-2', '1-3', '1-4', '2-1', '5-3', '5-4', '6-1', '6-2',
        '6-4', '6-5', '6-7', '6-8', '6-10', '6-11', '6-12', '7-1', '7-2',
        '7-3', 'B-1', 'B-2', 'B-3', 'B-4', 'B-5', 'C-1', 'C-2', 'C-3',
        'C-4', 'C-5', 'C-6', 'C-7', 'C-8', 'C-9', 'C-10'},
}


def _pattern(number):
    parts = []
    for p in re.split(r"[-.\s]+", number):
        lettered = re.fullmatch(r"(\d+)([A-Za-z])", p)
        if lettered:   # '9-37a' is printed '9-37(a)'
            parts.append(lettered.group(1) + r"\s*\(?" + lettered.group(2)
                         + r"\)?")
        elif p:
            parts.append(re.escape(p))
    body = r"\s*[-\u2010-\u2015.\s]\s*".join(parts)
    return re.compile(r"fig(?:ure|\.)?\s*" + body + r"(?![0-9])", re.I)


@pytest.mark.parametrize("ref", [c for c in CATALOGS
                                 if c not in NO_TEXT_LAYER])
def test_each_row_page_prints_its_figure_number(ref):
    pymupdf = pytest.importorskip("pymupdf")
    cat = _catalog(ref)
    docs, lacks = {}, set()
    try:
        for fig in cat["figures"]:
            rel = fig.get("pdf_path") or cat.get("pdf_path")
            if not (ROOT / rel).exists():
                pytest.skip(f"{rel} not checked out")
            if rel not in docs:
                docs[rel] = pymupdf.open(str(ROOT / rel))
            text = docs[rel][fig["pdf_page_index"]].get_text()
            if not _pattern(fig["figure_number"]).search(text):
                lacks.add(fig["figure_number"])
    finally:
        for d in docs.values():
            d.close()
    assert lacks == TEXT_LAYER_LACKS.get(ref, set())
