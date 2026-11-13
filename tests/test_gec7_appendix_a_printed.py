"""GEC-7 (FHWA-NHI-14-007, 2015) Appendix A, Reinforcement Characteristics,
pinned to the print.

REF-85 (app backlog): the property tables an engineer looks up for a soil
nail wall (solid-threaded bars of Grades 60, 75 and 150; CTS/Titan, MAI and
GEO-Drill hollow bars; welded-wire mesh; reinforcing bars; headed studs,
pp. 285 to 293) are chapter 11, every cell typed in from a 300 dpi render of
the page and checked against the text layer, with the units, sources and
notes as printed. The appendix prints no section numbers: sections A.1 to
A.7 are named for the tables they hold. Where a printed number disagrees
with the print's own other numbers the cell keeps the print and says so
"(as printed; ...)"; the tests below recompute those columns from the
stored cells, so each note stands on arithmetic.

No gec_7 lookup (tables.py, figures.py) holds any of these values.
"""

import json
import math
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest

from geotech_references._retrieval import load_chapter, retrieve_section, search_sections

REPO = Path(__file__).resolve().parents[1]

A_IDS = ["A", "A.1", "A.2", "A.3", "A.4", "A.5", "A.6", "A.7"]


def _section(sid):
    return retrieve_section("gec_7", sid)


def _table(label):
    """The stored table string whose title starts with ``label``."""
    for sid in A_IDS:
        for t in _section(sid)["tables"]:
            if t.startswith(label + ":"):
                return t
    raise AssertionError(label + " is not stored")


def _rows(label, n_cols):
    """The table's rows as lists of cells (a note after a row is cut off)."""
    t = _table(label)
    rest = t.split(" - columns: ", 1)[1]
    rest = rest[: rest.rfind(" Source")].rstrip(".")
    chunks = [c.split(" (as printed")[0] for c in rest.split(" | ")]
    first = chunks[0].split("; ")
    head, cell = first[n_cols - 1].rsplit(". ", 1)
    columns = first[: n_cols - 1] + [head]
    rows = [[cell] + first[n_cols:]] + [c.split("; ") for c in chunks[1:]]
    assert all(len(r) == n_cols for r in rows), rows
    return columns, rows


def _notes(label):
    return re.findall(r"\(as printed.*?\)(?=\.? Source| \||$)", _table(label))


# ---------------------------------------------------------------- the chapter

def test_chapter_metadata_and_sections():
    data = load_chapter("gec_7", 11)
    assert data["chapter_title"] == "Appendix A: Reinforcement Characteristics"
    assert data["reference_id"] == "FHWA-NHI-14-007"
    assert [s["section_id"] for s in data["sections"]] == A_IDS
    assert [c["section_id"] for c in _section("A")["children"]] == A_IDS[1:]


@pytest.mark.parametrize("sid,pages", [
    ("A", ["285"]), ("A.1", ["286", "287"]), ("A.2", ["288"]), ("A.3", ["289"]),
    ("A.4", ["290"]), ("A.5", ["291"]), ("A.6", ["292"]), ("A.7", ["293"]),
])
def test_page_markers(sid, pages):
    assert re.findall(r"\[p\. (\d+)\]", _section(sid)["body"]) == pages


def test_manufacturer_note_and_table_list_as_printed():
    body = _section("A")["body"]
    assert body.startswith(
        "[p. 285] Note: Products are occasionally discontinued or modified by manufacturers. Some "
        "properties/sizes originally considered in a design might not be available for construction. "
        "Check availability with manufacturer. In cases where the sizes originally planned were "
        "discontinued, adopt the next available larger size.")
    # the list prints "Reinforcing Bar" and "Headed-Stud"; the tables' own titles are plural
    for line in ("Table A.1c: Properties of Solid-Threaded Bars Grade 150",
                 "Table A.4: Properties of Hollow Bars GEO-Drill Bar Type",
                 "Table A.6: Reinforcing Bar\n", "Table A.7: Headed-Stud"):
        assert line in body
    assert "Table A.6: Reinforcing Bars (p. 292)" in _table("Table A.6")


# ---------------------------------------------------------------- cells

CELLS = {
    "Table A.1a": ["#6; 0.86; 0.44; 1.50; 60; 60; 26", "#11; 1.61; 1.56; 5.31; 60; 60; 93",
                   "#14; 1.86; 2.25; 7.65; 60; 60; 135"],
    "Table A.1b": ["#6; 0.86; 0.44; 1.50; 75; 75; 33", "#9; 1.26; 1.00; 3.40; 75; 75; 75",
                   "#14; 1.86; 2.25; 7.65; 75; 75; 168"],
    "Table A.1c": ["¾; 0.75; 0.37; 1.32; 150; 57", "1⅜; 1.375; 1.58; 5.56; 150; 237",
                   "1¾; 1.75; 2.58; 9.22; 150; 400"],
    "Table A.2": ["30/16; 1.02; 0.53; 1.8; 42.7; 55.1", "52/26; 1.92; 1.94; 6.7; 164.2; 208.0",
                  "73/35; 2.76; 4.20; 14.2; 321.6; 419.4"],
    "Table A.3": ["R25N; 1.00; 0.41; 1.41; 83; 111; 34; 45", "R51L; 1.50; 1.17; 3.97; 86; 106; 101; 124",
                  "T76S; 3.00; 3.88; 13.24; 87; 110; 337; 427"],
    "Table A.4": ["B7X1-32; 1.25; 0.556; 2.10; 47.2; 58.4", "B7X1-51; 2.00; 1.795; 6.26; 152.0; 188.0",
                  "B7X1-76; 3.00; 3.880; 13.79; 329.0; 407.0"],
    "Table A.5": ["4x4 - W 1.4 x W 1.4; 0.042; 31", "4x4 – W 4.0 x W 4.0; 0.120; 88",
                  "6x6 – W 2.9 x W 2.9; 0.058; 42"],
    "Table A.6": ["3; 0.375; 0.11", "9; 1.128; 1.00", "18; 2.257; 4.00"],
    "Table A.7": ["¼ x 4⅛; 4⅛; 0.50; 0.25; 0.19; 4.0; 0.75", "½ x 5 5/16; 5 5/16; 1.00; 0.50; 0.28; 4.0; 0.56",
                  "⅞ x 6 3/16; 6 3/16; 1.40; 0.86; 0.38; 2.5; 0.73"],
}


@pytest.mark.parametrize("label,row", [(k, r) for k, rows in CELLS.items() for r in rows])
def test_cells_as_printed(label, row):
    assert row in _table(label)


ROW_COUNTS = {"Table A.1a": (7, 7), "Table A.1b": (7, 7), "Table A.1c": (6, 5), "Table A.2": (6, 10),
              "Table A.3": (8, 9), "Table A.4": (6, 5), "Table A.5": (3, 8), "Table A.6": (3, 11),
              "Table A.7": (7, 14)}


@pytest.mark.parametrize("label", ROW_COUNTS)
def test_every_row_stored(label):
    n_cols, n_rows = ROW_COUNTS[label]
    assert len(_rows(label, n_cols)[1]) == n_rows


@pytest.mark.parametrize("label,unit", [
    ("Table A.1a", "Minimum Cross-Sectional Area, inch²"), ("Table A.1c", "Ultimate Load (1), kip"),
    ("Table A.2", "Effective Outer Diameter, inch"), ("Table A.3", "Average Ultimate Tensile Stress (1), ksi"),
    ("Table A.4", "Nominal Outer Diameter, inch"),
    ("Table A.5", "Mesh Designation (2) (3) (4), in. × in. – in.²/100 × in.²/100"),
    ("Table A.5", "Weight per Unit Area, lb/cft² (6)"), ("Table A.6", "Nominal Area, inch²"),
    ("Table A.7", "Head Thickness / (Head Diameter-Shaft Diameter), tSH / (DSH - DSC), -"),
])
def test_column_units_as_printed(label, unit):
    assert unit in _rows(label, ROW_COUNTS[label][0])[0]


@pytest.mark.parametrize("label,text", [
    ("Table A.1a", "Dywidag, Williams and Contech"), ("Table A.1c", "Sources: Dywidag, Williams and Stressteel"),
    ("Table A.1c", "Note: (1) Based on ultimate strength."),
    ("Table A.2", "Note: (1) These bars are alloy steel and have nominal yield strength of 87 ksi."),
    ("Table A.3", "Source: Dywidag."),
    ("Table A.4", "(1) These bars have a yield strength of 85 ksi and an ultimate strength of 105 ksi."),
    ("Table A.5", "(6) CSF = 100 square feet."), ("Table A.5", "A prefix “D” would indicate pre-deformed wire."),
    ("Table A.6", "Source: ACI 318-11."),
    ("Table A.7", "For DS ≤ ½\", LS is approximately ⅛\" shorter after welding. For DS > ⅝\"LS is "
                  "approximately 3/16\" shorter after welding."),
])
def test_sources_and_notes_as_printed(label, text):
    assert text in _table(label)


def test_notes_also_in_the_body():
    assert "(5) The area per unit width is obtained by dividing the wire cross-sectional area by 100" \
        in _section("A.5")["body"]
    assert "(1) Nominal length indicated is before welding." in _section("A.7")["body"]
    assert "Note: (1) Based on ultimate strength." in _section("A.1")["body"]


def test_figure_a1_with_its_catalog_row():
    fig = _section("A.7")["figures"]
    assert len(fig) == 1 and fig[0].startswith("Figure A.1: Illustration. Geometry of headed studs (p. 293)")
    catalog = json.loads((REPO / "geotech_references/gec_7/figures_catalog.json").read_text(encoding="utf-8"))
    rows = catalog if isinstance(catalog, list) else catalog.get("figures", catalog)
    row = [r for r in rows if r["figure_number"] == "A.1"][0]
    assert (row["printed_page"], row["pdf_page_index"]) == (293, 332)


# ---------------------------------------------------------------- the print's arithmetic

def test_a1_yield_loads_are_area_times_stress_rounded_down():
    for label in ("Table A.1a", "Table A.1b"):
        for size, _, area, _, grade, stress, load in _rows(label, 7)[1]:
            assert grade == stress
            assert int(load) == math.floor(float(area) * float(stress) + 1e-9), (label, size)
    assert _notes("Table A.1a") == _notes("Table A.1b") == []


def test_a1c_ultimate_loads_and_the_two_notes():
    off = []
    for size, _, area, _, grade, load in _rows("Table A.1c", 6)[1]:
        if abs(float(area) * float(grade) - float(load)) > 0.5:
            off.append(size)
    assert off == ["¾", "1¾"]
    assert "¾; 0.75; 0.37; 1.32; 150; 57 (as printed; 0.37 × 150 = 55.5)" in _table("Table A.1c")
    assert "1¾; 1.75; 2.58; 9.22; 150; 400 (as printed; 2.58 × 150 = 387)" in _table("Table A.1c")


def test_a2_yield_loads_against_the_87_ksi_note():
    ratios = {r[0]: float(r[4]) / float(r[2]) for r in _rows("Table A.2", 6)[1]}
    assert round(min(ratios.values()), 1) == 76.6 and min(ratios, key=ratios.get) == "73/35"
    assert round(max(ratios.values()), 1) == 91.4 and max(ratios, key=ratios.get) == "30/11"
    assert _notes("Table A.2") == ["(as printed; the yield loads divided by the areas run from 76.6 ksi, "
                                   "73/35, to 91.4 ksi, 30/11, not 87 ksi throughout)"]


def test_a3_loads_follow_the_average_stresses_and_the_r51l_diameter():
    for bar, od, area, _, ys, uts, yl, ul in _rows("Table A.3", 8)[1]:
        tol = float(area) * 0.5 + 0.5          # stresses printed to the ksi, loads to the kip
        assert abs(float(area) * float(ys) - float(yl)) <= tol, bar
        assert abs(float(area) * float(uts) - float(ul)) <= tol, bar
        mm = int(re.search(r"\d+", bar).group())
        if bar == "R51L":
            assert abs(mm / 25.4 - float(od)) > 0.4
        else:
            assert abs(mm / 25.4 - float(od)) < 0.03, bar
    assert len(_notes("Table A.3")) == 1 and "R51N 2.00" in _notes("Table A.3")[0]


def test_a4_loads_follow_85_and_105_ksi():
    for bar, _, area, _, yl, ul in _rows("Table A.4", 6)[1]:
        assert abs(float(area) * 85 - float(yl)) < 1.0, bar
        assert abs(float(area) * 105 - float(ul)) < 1.0, bar


def test_a5_area_per_width_from_the_designation():
    for mesh, per_width, _ in _rows("Table A.5", 3)[1]:
        spacing, wire = re.match(r"(\d)x\d [-–] W (\d\.\d) x W \2", mesh).groups()
        assert round(float(wire) / 100 / (int(spacing) / 12), 3) == float(per_width), mesh


def test_a6_nominal_areas_from_the_diameters():
    for bar, d, area in _rows("Table A.6", 3)[1]:
        q = Decimal(repr(math.pi * float(d) ** 2 / 4)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        assert q == Decimal(area), bar


def test_a7_ratio_columns_and_the_seven_eighths_note():
    for size, _, dsh, dsc, tsh, ar, tr in _rows("Table A.7", 7)[1]:
        a = round((float(dsh) / float(dsc)) ** 2, 1)
        t = round(float(tsh) / (float(dsh) - float(dsc)), 2)
        if size.startswith("⅞"):
            assert abs(a - float(ar)) > 0.1 + 1e-9 and abs(t - float(tr)) > 0.02, size
            assert round((1.40 / 0.88) ** 2, 1) == float(ar) and round(0.38 / 0.52, 2) == float(tr)
        else:
            assert abs(a - float(ar)) <= 0.1 + 1e-9 and abs(t - float(tr)) <= 0.01 + 1e-9, size
    assert _notes("Table A.7") == ["(as printed, the three ⅞ rows: with DSH 1.40 and DSC 0.86, "
                                   "(1.40/0.86)² = 2.65 and 0.38/(1.40 - 0.86) = 0.70; the printed 2.5 and "
                                   "0.73 agree with DSC = 0.88)"]


def test_only_the_five_notes():
    text = json.dumps(load_chapter("gec_7", 11), ensure_ascii=False)
    assert text.count("(as printed") == 5


# ---------------------------------------------------------------- the design example's citations agree

@pytest.mark.parametrize("sid,cited,label,row", [
    ("C.4.e", "The nominal diameter for #7 bars, including threads, is 0.99 in. (see Table A.1b)",
     "Table A.1b", "#7; 0.99;"),
    ("C.7.d", "For a 6 × 6 - W2.9 × W2.9 WWM, avm is 0.058 in.²/ft, from Table A.5",
     "Table A.5", "6x6 – W 2.9 x W 2.9; 0.058;"),
    ("C.7.d", "AVN = 2 × 0.31 = 0.62 in.²", "Table A.6", "5; 0.625; 0.31"),
    ("C.7.d", "avm = avn = 0.20 in.²/ft (from Table A.6)", "Table A.6", "4; 0.500; 0.20"),
])
def test_appendix_c_values_agree_with_appendix_a(sid, cited, label, row):
    assert cited in _section(sid)["body"]
    assert row in _table(label)


def test_appendix_c_stud_head_thickness_noted():
    c3 = [t for t in _section("C.6.a")["tables"] if t.startswith("Table C.3:")][0]
    assert ("head thickness: tSH = 0.31 in. (as printed; Table A.7 gives 0.28 in. for the ½ x 4⅛ stud, "
            "and hc in Step 7e is 4.8 in. with either)") in c3
    assert "½ x 4⅛; 4⅛; 1.00; 0.50; 0.28;" in _table("Table A.7")
    for t in (0.28, 0.31):
        assert round(4.125 + 1 - t, 1) == 4.8


# ---------------------------------------------------------------- found by search

@pytest.mark.parametrize("query,sid", [
    ("GEO-Drill hollow bars", "A.4"), ("R51N", "A.3"), ("CTS/Titan", "A.2"),
    ("welded-wire mesh area per unit width", "A.5"), ("headed stud head thickness", "A.7"),
    ("Grade 75 #8 bar yield load", "A.1"), ("nominal area reinforcing bars ACI 318-11", "A.6"),
])
def test_search_finds_the_table(query, sid):
    hits = search_sections("gec_7", query, max_chars=6000)["hits"]
    assert hits[0]["section_id"] == sid


def test_manifest_row_and_not_built_list():
    m = json.loads((REPO / "scripts/manifests/gec_7.json").read_text(encoding="utf-8"))
    row = [c for c in m["chapters"] if c["number"] == 11][0]
    assert row == {"number": 11, "title": "Appendix A: Reinforcement Characteristics",
                   "page_start": 325, "page_end": 334}
    assert "Appendix A" not in m["appendices_not_built"]
