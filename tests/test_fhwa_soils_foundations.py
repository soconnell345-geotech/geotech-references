"""FHWA NHI-06-088/089 Soils and Foundations Reference Manual (REF-29).

The chapter text and figure catalog are read off the printed pages by
``scripts/build_printed_text.py``. These check that the text is there and
findable at every level the app uses (search, section, figure), that the
sections and figures the app's tools cite exist where they say, and that each
volume's chapters carry the designation printed on that volume's cover.
"""

import json
from pathlib import Path

import pytest

from geotech_references import _figures_db, _retrieval, _retrieval_db

REF = "fhwa_soils_foundations"
ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references" / REF
DOCS = ROOT / "docs"
VOLUMES = {
    1: ("FHWA-NHI-06-088", "FHWA NHI-06-088 Soils and Foundations Vol 1.pdf",
        range(1, 8)),
    2: ("FHWA-NHI-06-089", "FHWA NHI-06-089 Soils and Foundations Vol 2.pdf",
        range(8, 13)),
}


def _chapters():
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((PKG / "text").glob("chapter*.json"))]


def test_twelve_chapters_through_both_volumes():
    chapters = _chapters()
    assert [c["chapter"] for c in chapters] == list(range(1, 13))
    for c in chapters:
        vol = 1 if c["chapter"] <= 7 else 2
        assert c["volume"] == vol
        assert c["reference_id"] == VOLUMES[vol][0]
    titles = {c["chapter"]: c["chapter_title"] for c in chapters}
    assert titles[6] == "Slope Stability"
    assert titles[9] == "Deep Foundations"


def test_every_section_carries_its_printed_pages():
    for c in _chapters():
        for s in c["sections"]:
            # a heading followed straight by its first subsection has no text
            assert s["body"] == "" or s["body"].startswith("[p. "), s["section_id"]
            assert "printed p" in s["applicability"] or "Part " in \
                s["applicability"], s["section_id"]


def test_section_bodies_fit_the_reference_tools():
    # the app sends at most 16,000 characters of a tool's result, and
    # wraps a section in about 300 more
    for c in _chapters():
        for s in c["sections"]:
            assert len(json.dumps(s)) <= 14000, s["section_id"]


def test_every_listed_equation_is_marked_in_its_section():
    # a short paragraph holding an equation on a page with a figure was
    # dropped as figure lettering, leaving Eq. 9-42 (p. 9-132) listed only
    for c in _chapters():
        for s in c["sections"]:
            for e in s["equations"]:
                assert f"[{e['id']}]" in s["body"], (s["section_id"], e["id"])
    sec = _retrieval.retrieve_section(REF, "2.1.7")
    assert "PI = LL – PL [Eq. 2-11]" in sec["body"]


def test_table_cells_read_row_by_row():
    # Table 8-2 (p. 8-20), cited by the bearing capacity worked example
    sec = _retrieval.retrieve_section(REF, "8.4.2")
    assert "[p. 8-20]" in sec["body"]
    assert "0 5.14 1.0 0.0 23 18.1 8.7 8.2 1 5.4 1.1 0.1" in sec["body"]
    assert "30 30.1 18.4 22.4" in sec["body"]
    # the axis of Figure 8-15 on the same page is not a table
    assert "0 5 10 15 20 25 30 35 40 45" not in sec["body"]


def test_table_printed_as_a_picture_carries_its_rows():
    # Table 10-1 (p. 10-18) has no text layer; the manifest supplies its
    # rows, which the retaining-wall module cites for adhesion
    sec = _retrieval.retrieve_section(REF, "10.2.4")
    body = sec["body"]
    cap = body.index("[p. 10-18] Table 10-1 Wall friction and adhesion")
    rows = body[cap:]
    assert "Clean sound rock | 0.70 | 35." in rows
    assert "Medium stiff cohesive soil (24 - 48 kPa) | 24 - 36." in rows
    assert "Very stiff cohesive soil (96 - 192 kPa) | 45 - 62." in rows


def test_section_lookup_janbu_charts():
    sec = _retrieval.retrieve_section(REF, "6.6.3")
    assert sec["title"] == "Janbu’s Stability Charts"
    # the passage the slope search cites (NHI-06-088 p. 6-38)
    assert "[p. 6-38]" in sec["body"]
    assert "If there is a weak layer above the toe of the slope" in sec["body"]
    figs = [f.split(":")[0] for f in sec["figures"]]
    assert "Figure 6-16" in figs and "Figure 6-19" in figs
    ids = [e["id"] for e in sec["equations"]]
    assert "Eq. 6-27" in ids and "Eq. 6-28" in ids


def test_section_lookup_through_the_database():
    row = _retrieval_db.reference_get(REF, "9.5.1.1")
    assert row["title"] == "Nordlund Method"
    assert "Nordlund" in row["body"]


def test_heading_printed_under_another_number_keeps_the_page_number():
    # the contents print 9.11.1.1, the page prints 9.11.2.1 (p. 9-126)
    sec = _retrieval.retrieve_section(REF, "9.11.2.1")
    assert sec["title"] == "Special Considerations for Drilled Shafts"


def test_search_finds_taylor_and_janbu():
    hits = _retrieval_db.reference_search("Janbu stability chart", reference=REF)
    assert "6.6.3" in [h["section_id"] for h in hits[:5]]
    hits = _retrieval_db.reference_search("Taylor stability number", reference=REF)
    assert "6.6.2" in [h["section_id"] for h in hits[:5]]


def test_figure_lookup_cited_figures():
    # cited by the app: slope Figs. 6-14 to 6-16 and 6-19, sheet pile 10-10
    # 7-12's list entry has no dotted leader; 9-17's caption is on p. 9-55
    expected = {"6-14": ("6-27", 1, 376), "6-15": ("6-28", 1, 377),
                "6-16": ("6-34", 1, 383), "6-19": ("6-39", 1, 388),
                "10-10": ("10-22", 2, 311), "10-17": ("10-39", 2, 328),
                "7-12": ("7-27", 1, 436), "9-17": ("9-55", 2, 164)}
    for num, (page, vol, idx) in expected.items():
        fig = _figures_db.figure_get(REF, num)
        assert fig["printed_page"] == page, num
        assert fig["pdf_page_index"] == idx, num
        pdf, page = _figures_db.resolve_pdf(REF, num)
        assert pdf.name == VOLUMES[vol][1] and page == idx, num


def test_figure_search_finds_janbu_charts():
    hits = _figures_db.figure_search("Janbu stability chart", reference=REF)
    nums = [h["figure_number"] for h in hits[:5]]
    assert "6-16" in nums or "6-19" in nums


def test_catalog_pages_are_the_caption_pages():
    cat = json.loads((PKG / "figures_catalog.json").read_text(encoding="utf-8"))
    assert cat["figure_count"] == len(cat["figures"]) > 280
    assert not any(f["page_estimated"] for f in cat["figures"])
    fitz = pytest.importorskip("fitz")
    pdf = DOCS / VOLUMES[1][1]
    if not pdf.exists():
        pytest.skip("PDF not checked out")
    with fitz.open(str(pdf)) as doc:
        text = doc[383].get_text()
    assert "Figure 6-16." in text and "6 - 34" in text


@pytest.mark.parametrize("vol", [1, 2])
def test_volume_cover_designation(vol):
    fitz = pytest.importorskip("fitz")
    rid, pdf, chapters = VOLUMES[vol]
    path = DOCS / pdf
    if not path.exists():
        pytest.skip("PDF not checked out")
    with fitz.open(str(path)) as doc:
        cover = doc[0].get_text()
    assert rid.replace("-", " ", 1) in cover.replace("No. ", "")
    assert "December 2006" in cover
    for c in _chapters():
        if c["chapter"] in chapters:
            assert c["reference_id"] == rid
