"""Every figure catalog caption is one caption (BACKLOG REF-27).

The List of Figures parser in ``scripts/build_figure_catalog.py`` used to run
the last entry of a list on into whatever followed it (the list of tables, the
list of symbols, chapter 1) and to miss entries printed with an en-dash
("Figure 2 – 1"), gluing them onto the entry before. A caption of 29,911
characters (GEC-13 Fig 1-3) filled figure search with page text.
``caption_problems`` flags a caption over ``MAX_CAPTION_CHARS`` or one that
carries another entry, a list heading or a running header.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "build_figure_catalog", ROOT / "scripts" / "build_figure_catalog.py")
bfc = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = bfc
_spec.loader.exec_module(bfc)

CATALOGS = sorted((ROOT / "geotech_references").glob("*/figures_catalog.json"))


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", CATALOGS, ids=lambda p: p.parent.name)
def test_every_caption_is_one_caption(path):
    problems = bfc.caption_problems(_load(path))
    assert not problems, "\n".join(problems)


def test_the_filed_captions():
    want = {
        ("gec_13", "1-3"): "Federal Lands Highway project development work process",
        ("gec_8", "A.17"): ("Comparison of Study Results - Axial Capacity in "
                            "Cohesionless Soils"),
        ("gec_12", "8-12"): "One-way beam shear critical sections from pile(s)",
        # the List of Figures drops "shaft"; the figure's page prints it
        ("gec_12", "3-6"): "Nominal shaft resistance and pile support cost",
        ("gec_12", "D-125"): "Inspectors Chart for ICE I-36 V2 at the South Abutment",
        ("micropile", "8-8"): "Baroid Mud Balance Test",
        # REF-50: captions under the figure, not the sentence that cites it
        ("gec_6", "5-12"): ("Distribution of Vertical Stress by the 2:1 Method "
                            "(Chen and McCarron, 1991)"),
        ("gec_6", "4-3"): "Phase Relation Block Diagram",
        ("gec_6", "2-3"): "Spread Footing with Cantilever Stemwall at Bridge Abutment",
        ("gec_6", "2-13"): "Elevation of Mt. Rose Interchange Bridge, I-580, Nevada",
        ("gec_4", "31"): "Flow net for a retaining wall (after CIRIA, 1984)",
        ("gec_14", "B-1"): ("QA of GRDs for Alternative Delivery Methods - DBB, "
                            "CM/GC and Preliminary DB (ACMs)"),
    }
    for (ref, number), caption in want.items():
        figs = _load(ROOT / "geotech_references" / ref / "figures_catalog.json")
        got = [f["caption"] for f in figs["figures"] if f["figure_number"] == number]
        assert got == [caption], (ref, number, got)


def test_gec6_figures_sit_on_their_caption_pages():
    """REF-50: each figure on the page that prints its caption (PDF page index
    = printed page + 5), not the page of a sentence citing it; Figure 5-11,
    whose caption opens "(a)", is catalogued."""
    printed = {"2-8": 12, "2-9": 13, "2-10": 15, "5-1": 48, "5-6": 55,
               "5-11": 77, "5-12": 79, "5-13": 80, "5-17": 87, "5-21": 92,
               "5-22": 101, "8-3": 130, "8-4": 131}
    figs = _load(ROOT / "geotech_references" / "gec_6" / "figures_catalog.json")
    pages = {f["figure_number"]: f["pdf_page_index"] for f in figs["figures"]}
    assert {n: pages.get(n) for n in printed} == {n: p + 5 for n, p in printed.items()}
    five_11 = [f["caption"] for f in figs["figures"] if f["figure_number"] == "5-11"]
    assert five_11[0].startswith("(a) Chart for Use in Determining Vertical Stresses")
    assert figs["figure_count"] == len(figs["figures"]) == 57


def test_micropile_lists_every_printed_figure_once():
    """The printed List of Figures has 132 entries (3, 5, 14, 18, 27, 44, 13
    and 8 in chapters 1-8)."""
    figs = _load(ROOT / "geotech_references" / "micropile" / "figures_catalog.json")
    numbers = [f["figure_number"] for f in figs["figures"]]
    assert len(numbers) == len(set(numbers)) == figs["figure_count"] == 132
    per_chapter = [sum(1 for n in numbers if n.split("-")[0] == str(c))
                   for c in range(1, 9)]
    assert per_chapter == [3, 5, 14, 18, 27, 44, 13, 8]
    assert not any(f["page_estimated"] for f in figs["figures"])


# ---------------------------------------------------------------------------
# the parser's pieces (no PDFs needed)
# ---------------------------------------------------------------------------

def test_chapter_page_numbers_end_an_entry():
    assert bfc._clean_caption(" Micropile Construction Sequence using Casing "
                              "...........1 - 4") == (
        "Micropile Construction Sequence using Casing", 4)
    assert bfc._clean_caption(" Baroid Mud Balance Test........8 - 17") == (
        "Baroid Mud Balance Test", 17)
    # a number inside the caption is not its page
    assert bfc._clean_caption(" Spreadsheet Calculations Based on Eq. 6-12 to "
                              "Obtain Hult for the Example Problem ....6 - 55")[1] == 55


def test_running_headers_are_dropped():
    pages = [["FHWA NHI-05-039", "Micropile Design & Construction", "i - xi",
              "Figure 1 - 1.  A ....1 - 4"],
             ["FHWA NHI-05-039", "Micropile Design & Construction   i-xii",
              "Figure 4 - 11.  B ....4 - 17"]]
    running = bfc._running_lines(pages)
    assert "FHWA NHI-05-039" in running
    assert "Micropile Design & Construction" in running
    assert not any("Figure" in ln for ln in running)


def test_the_caption_printed_on_a_figure_page():
    page = ("labeled\nRs, presented once again in Figure 3-6 and\n"
            "Figure 3-6 presents plots of both\n \n"
            "Figure 3-6 \nNominal shaft resistance and pile support cost.  \n")
    assert bfc._page_caption(page, "3-6") == \
        "Nominal shaft resistance and pile support cost"
    # another number, and an in-text reference only
    assert bfc._page_caption(page, "3-60") is None
    assert bfc._page_caption("as Figure 3-6 shows.\n", "3-6") is None
    # a caption over two lines ends at its period
    assert bfc._page_caption("Figure 7-21 Illustration of the\nprocedure "
                             "(FHWA-TS-78-209).\nNext paragraph.", "7-21") == \
        "Illustration of the procedure (FHWA-TS-78-209)"


def test_a_caption_block_under_a_figure():
    cap = lambda text: bfc._block_caption(text, bfc._FIG_MARKER)
    # a caption over two lines, a word broken at the line end keeps its hyphen
    assert cap("Figure 4-7: Typical Load-\nSettlement Curves for a Test\n"
               "Footing on Sand\n") == (
        "4-7", "Typical Load-Settlement Curves for a Test Footing on Sand")
    # a caption that opens with its first part
    assert cap("Figure 3-2:  (a) Plan View (b) Section A-A") == (
        "3-2", "(a) Plan View (b) Section A-A")
    assert cap("Figure 6-1. Contact Pressure Under a Rigid Plate.\nNext line") == (
        "6-1", "Contact Pressure Under a Rigid Plate")
    # a blank line ends the caption
    assert cap("Figure 2-4. Site Plan\n \nThe borings were drilled in 1990.")[1] == \
        "Site Plan"


def test_a_block_that_is_not_a_caption():
    cap = lambda text: bfc._block_caption(text, bfc._FIG_MARKER)
    assert cap("the stress is shown in Figure 5-9. This is simpler to use") is None
    assert cap("Figure 5-9 shows the stress beneath the footing") is None
    assert cap("Figure 5-9(a) presents the active case") is None
    assert cap("Figure 5-9 (continued)") is None
    assert cap("Figure 5-9. Continued") is None
    assert cap("Figure 5-9  Gradation Chart ........................ 8") is None
    assert cap("Figure 5-9:") is None


def test_rows_join_words_set_on_lines_of_their_own():
    line = lambda text, x, bottom: {"bbox": (x, bottom - 10, x + 40, bottom),
                                    "spans": [{"text": text}]}
    block = {"lines": [line("Figure ", 90, 340), line("6-1. ", 136, 340),
                       line("Example ", 189, 340.5), line("costs", 240, 340),
                       line("second row", 90, 356)]}
    assert bfc._block_rows(block) == ["Figure  6-1.  Example  costs",
                                      "second row"]


def test_captions_set_side_by_side_are_two_captions():
    """REF-51: two captions sharing a row under two figures each keep their
    own words, the second one's credit line included."""
    line = lambda text, x, bottom: {"bbox": (x, bottom - 10, x + 6 * len(text), bottom),
                                    "spans": [{"text": text}]}
    block = {"lines": [line("Figure ", 90, 500), line("2-5. ", 132, 500),
                       line("Grader", 162, 500), line("(credit A).", 200, 500),
                       line("Figure ", 330, 500), line("2-6. ", 372, 500),
                       line("Scraper", 402, 500), line("(credit B)", 340, 514)]}
    cols = bfc._block_columns(block)
    caps = [bfc._block_caption("\n".join(rows), bfc._FIG_MARKER) for rows in cols]
    assert caps == [("2-5", "Grader (credit A)"), ("2-6", "Scraper (credit B)")]
    # a label a space after the text before it is running text, one column
    prose = {"lines": [line("as shown in", 90, 500), line("Figure 2-5. ", 160, 500),
                       line("The next", 232, 500)]}
    assert len(bfc._block_columns(prose)) == 1
    pav = _load(ROOT / "geotech_references" / "fhwa_pavements" / "figures_catalog.json")
    got = {f["figure_number"]: f["caption"] for f in pav["figures"]}
    assert (got["8-8"], got["8-9"]) == ("Bulldozer (photo courtesy of Komatsu)",
                                        "Motor grader (photo courtesy of Caterpillar)")


def test_a_contents_page_does_not_place_a_figure(tmp_path):
    """The first caption block on a page that is not a list of entries wins:
    a contents page's block, an in-text mention and a "(continued)" label do
    not place the figure."""
    fitz = pytest.importorskip("fitz")
    doc = fitz.open()
    contents = doc.new_page()
    for k, y in enumerate((72, 200, 330)):
        contents.insert_text((72, y), f"Figure 9-{k + 1}: Entry Number {k + 1}")
    mention = doc.new_page()
    mention.insert_text((72, 72), "The wall moves as shown in Figure 9-1.")
    mention.insert_text((72, 86), "This is a reasonable approximation.")
    figure = doc.new_page()
    figure.insert_text((72, 400), "Figure 9-1: Wall Movement Versus Depth")
    later = doc.new_page()
    later.insert_text((72, 400), "Figure 9-1 (continued)")
    figs = {f["figure_number"]: f for f in bfc._figs_from_body(doc)}
    assert figs["9-1"]["pdf_page_index"] == 2
    assert figs["9-1"]["caption"] == "Wall Movement Versus Depth"
    # figures with no other caption stay on the page that lists them
    assert figs["9-2"]["pdf_page_index"] == 0


def test_a_run_on_caption_is_flagged():
    catalog = {"figures": [
        {"figure_number": "1-3", "caption": "Work process. 1-28 Table 1-1. "
                                            "Technical Categories"},
        {"figure_number": "8-12", "caption": "Shear sections. 478 LIST OF "
                                             "SYMBOLS A - Pile area"},
        {"figure_number": "2-1", "caption": "x" * (bfc.MAX_CAPTION_CHARS + 1)},
        {"figure_number": "6-36", "caption": "Equations Used in Each Cell in "
                                             "Figure 6-35"},
    ]}
    flagged = [p.split(":")[0] for p in bfc.caption_problems(catalog)]
    assert flagged == ["Figure 1-3", "Figure 8-12", "Figure 2-1"]
