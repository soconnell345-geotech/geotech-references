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
        ("gec_12", "D-125"): "Inspectors Chart for ICE I-36 V2 at the South Abutment",
        ("micropile", "8-8"): "Baroid Mud Balance Test",
    }
    for (ref, number), caption in want.items():
        figs = _load(ROOT / "geotech_references" / ref / "figures_catalog.json")
        got = [f["caption"] for f in figs["figures"] if f["figure_number"] == number]
        assert got == [caption], (ref, number, got)


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
