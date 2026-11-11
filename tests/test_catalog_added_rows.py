"""The figure catalog rows added from their caption pages (app BACKLOG REF-08
and REF-84, 2026-11-10).

A coverage check found printed figures with no catalog row, so a helper
could neither find nor read them: GEC-5 stopped at Figure 11-9. The rows
were added by ``scripts/build_figure_catalog.py --add-missing`` and their
pages checked: each page prints the figure's label and caption and holds a
picture or a drawing. The pinned rows below were also looked at on the
rendered page.

Captions are the ones printed under the figure. Where the List of Figures
words one differently the page wins, e.g. GEC-5 Figure 12-24, listed as
"Landslide event affecting highway 3 in Taiwan (Petley, 2010)", prints
"Landslide event affecting highway (Courtesy of USGS/Photo by D.
Krammer)" (PDF page 554, printed 12-28). Symbols the text layer garbles
were typed from the rendered page: GEC-5 Figure 11-22's "su/σ′vc" (PDF
page 517, printed 11-46) comes out of the text layer as "suσvc ′ ⁄".
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

from geotech_references import _figures_db

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references"
_spec = importlib.util.spec_from_file_location(
    "build_figure_catalog", ROOT / "scripts" / "build_figure_catalog.py")
bfc = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = bfc
_spec.loader.exec_module(bfc)


def _nums(prefix, first, last, sep="-"):
    return [f"{prefix}{sep}{k}" for k in range(first, last + 1)]


#: The rows added, by catalog.
ADDED = {
    "gec_5": (_nums("11", 10, 26) + _nums("12", 1, 25) + _nums("13", 1, 11)
              + _nums("A2", 1, 40)),
    # chapters 2-5 (Vol I) and 7-10 (Vol II); the catalog held 1 and 6
    "gec_13": (_nums("2", 1, 19) + _nums("3", 1, 18) + _nums("4", 1, 43)
               + _nums("5", 1, 30) + _nums("7", 1, 8) + _nums("8", 1, 51)
               + _nums("9", 1, 18) + _nums("10", 1, 19)),
}

#: Rows whose caption was typed from the rendered page (the text layer
#: garbles a symbol), so only the label is looked for in the text.
TYPED = {
    "gec_5": {"11-17", "11-21", "11-22", "13-8", "A2-8", "A2-28", "A2-29",
              "A2-30", "A2-35", "A2-36", "A2-38"},
}


def _rows(ref):
    cat = json.loads((PKG / ref / "figures_catalog.json").read_text(
        encoding="utf-8"))
    return cat, {f["figure_number"]: f for f in cat["figures"]}


@pytest.mark.parametrize("ref", sorted(ADDED))
def test_every_added_row_is_in_its_catalog_once(ref):
    cat, by = _rows(ref)
    numbers = [f["figure_number"] for f in cat["figures"]]
    for n in ADDED[ref]:
        assert numbers.count(n) == 1, (ref, n)
        assert by[n]["page_estimated"] is False
        assert _figures_db.figure_get(ref, n)["pdf_page_index"] == \
            by[n]["pdf_page_index"]


@pytest.mark.parametrize("ref", sorted(ADDED))
def test_each_added_row_page_prints_its_caption_and_holds_a_figure(ref):
    pymupdf = pytest.importorskip("pymupdf")
    cat, by = _rows(ref)
    docs = {}
    try:
        for n in ADDED[ref]:
            row = by[n]
            rel = row.get("pdf_path") or cat["pdf_path"]
            if not (ROOT / rel).exists():
                pytest.skip(f"{rel} not checked out")
            if rel not in docs:
                docs[rel] = pymupdf.open(str(ROOT / rel))
            page = docs[rel][row["pdf_page_index"]]
            assert bfc.page_graphic(page), (ref, n, "no picture or drawing")
            text = page.get_text()
            if n in TYPED.get(ref, ()):
                assert re.search(rf"Figure\s+{re.escape(n)}(?!\d)", text), n
            else:
                assert bfc.caption_on_page(text, n, row["caption"]), (ref, n)
    finally:
        for d in docs.values():
            d.close()


@pytest.mark.parametrize("ref,number,index,caption", [
    # looked at on the rendered page (seeded draw of one row in five)
    ("gec_5", "12-6", 532, "Stress distribution beneath a square foundation"),
    ("gec_5", "12-24", 553, "Landslide event affecting highway (Courtesy of "
                            "USGS/Photo by D. Krammer)"),
    ("gec_5", "13-10", 574, "Design cross-section showing interpretation of "
                            "stratigraphy"),
    ("gec_5", "A2-14", 650, "Boring location plan"),
    ("gec_5", "A2-19", 657, "p−q diagram for CIUC tests for specimens from "
                            "B-8 at 13-ft depth"),
    ("gec_5", "11-22", 516, "su/σ′vc versus OCR relation used to establish su "
                            "shown in Figure 11-21"),
    ("gec_5", "A2-35", 671, "Relationship between su/σ′vc and OCR for the soft "
                            "clay site from 15 C̅U̅ tests"),
    ("gec_13", "2-14", 125, "PVD Installation showing typical instrumentation "
                            "and monitoring"),
    ("gec_13", "4-10", 247, "12 kip tamper"),
    # listed as "Manitowoc 4000 crane with special lifting drum ..."
    ("gec_13", "4-17", 251, "Crane with special lifting drum attached to rear "
                            "of crane for use with 64 kip tamper"),
    ("gec_13", "5-23", 366, "Relationship between stress ratio causing "
                            "liquefaction and (N1)60 values for silty sands "
                            "for 7.5 magnitude earthquakes"),
    ("gec_13", "8-22", 225, "Rock grouting injection pressures used in Swedish "
                            "grouting practice"),
    ("gec_13", "9-1", 340, "Stabilization aggregate thickness design curves "
                           "for a single wheel load (top) and dual wheel loads "
                           "(bottom)"),
    ("gec_13", "10-17", 543, "Minimum recommended geometry of a stable "
                             "feature MSE (SFMSE) wall system"),
])
def test_pinned_rows(ref, number, index, caption):
    row = _figures_db.figure_get(ref, number)
    assert (row["pdf_page_index"], row["caption"]) == (index, caption)


def test_gec13_rows_carry_their_volume():
    """Vol I (FHWA-NHI-16-027) rows carry no number of their own; Vol II
    rows carry FHWA-NHI-16-028 and its PDF, as the rows before them do."""
    _, by = _rows("gec_13")
    for n in ADDED["gec_13"]:
        row = by[n]
        if int(n.split("-")[0]) <= 5:
            assert (row["volume"], row["pdf_path"]) == (1, "docs/GEC 13 Vol 1.pdf")
            assert "reference_id" not in row
        else:
            assert (row["volume"], row["pdf_path"], row["reference_id"]) == (
                2, "docs/GEC 13 Vol 2.pdf", "FHWA-NHI-16-028")


@pytest.mark.parametrize("ref,number,turn", [
    # printed turned on an upright page, the caption reading from the foot up
    ("gec_5", "A2-6", "clockwise"),
    ("gec_5", "A2-9", "clockwise"),
])
def test_sideways_figures_say_how_to_turn_the_page(ref, number, turn):
    notes = _figures_db.figure_get(ref, number)["read_notes"]
    assert "sideways" in notes and f"quarter turn {turn}" in notes


def test_added_rows_are_found_by_their_captions():
    for ref, query, number in [
        ("gec_5", "karst sinkhole pinnacled bedrock", "12-1"),
        ("gec_5", "seismic refraction subsurface voids", "12-10"),
        ("gec_5", "example CPTU log Caltrans", "13-4"),
        ("gec_5", "strain energy method", "A2-29"),
        ("gec_5", "Mohr-Coulomb curved failure envelope", "11-23"),
        ("gec_13", "Asaoka end of primary consolidation", "2-8"),
        ("gec_13", "EPS-block geofoam slope system components", "3-7"),
        ("gec_13", "Swedish rock grouting injection pressures", "8-22"),
        ("gec_13", "stabilization aggregate thickness design curves", "9-1"),
        ("gec_13", "stable feature MSE wall geometry", "10-17"),
    ]:
        hits = _figures_db.figure_search(query, reference=ref, limit=5)
        assert number in [h["figure_number"] for h in hits], (ref, query)
