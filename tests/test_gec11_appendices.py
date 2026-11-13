"""GEC-11 Volume II (FHWA-NHI-10-025, November 2009): the appendices read off
the print (app BACKLOG REF-85).

Each appendix file is built by ``scripts/build_gec11_appendix.py`` from the
printed pages: the print's own words with ``[p. B-3]`` markers, every
formula line, table and figure lettering typed in from a rendered page, the
appendix's numbered equations with their symbols as the page defines them.
These check the structure, the printed headings, sentences with their pages,
the typed formulas and tables, the arithmetic of the worked lines, and that
a rebuild gives the committed files.
"""

import json
import math
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references" / "gec_11"
PDF = ROOT / "docs" / "GEC 11 VOL 2.pdf"
#: Appendices built from the print so far, with the chapter number each
#: file carries (the appendices follow chapter 11).
BUILT = {"A": 12, "B": 13, "C": 14}


def _appendix(letter):
    path = PKG / "text" / f"appendix_{letter.lower()}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _sections(letter):
    return {s["section_id"]: s for s in _appendix(letter)["sections"]}


# --- structure ------------------------------------------------------------

@pytest.mark.parametrize("letter", sorted(BUILT))
def test_appendix_carries_its_volume_and_place(letter):
    a = _appendix(letter)
    assert a["volume"] == 2 and a["reference_id"] == "FHWA-NHI-10-025"
    assert a["reference_title"].endswith("Volume II")
    assert a["chapter"] == BUILT[letter]
    assert a["chapter_title"].startswith(f"Appendix {letter}: ")


@pytest.mark.parametrize("letter", sorted(BUILT))
def test_every_section_carries_its_printed_pages(letter):
    for s in _appendix(letter)["sections"]:
        assert s["section_id"] == letter or s["section_id"].startswith(f"{letter}.")
        assert s["body"] == "" or s["body"].startswith(f"[p. {letter}"), s["section_id"]
        assert f"printed p" in s["applicability"] or "Part " in s["applicability"]
        assert "summary" not in s and s["key_points"] == []
        assert len(json.dumps(s)) <= 14000, s["section_id"]
        for e in s["equations"]:
            assert f"[{e['id']}]" in s["body"], (s["section_id"], e["id"])
        for item in s["figures"] + s["tables"]:
            num = item.split(":")[0]
            assert re.search(rf"(?:^|\n\n|\] ){re.escape(num)}\. ", s["body"]), item


@pytest.mark.parametrize("letter", sorted(BUILT))
def test_no_scatter_patterns(letter):
    """A formula taken from the text layer that has come apart: a prime on
    its own, a lone number line above a formula, brackets that do not pair
    on a formula line, a line of one or two glyphs."""
    bad = []
    for s in _appendix(letter)["sections"]:
        lines = s["body"].split("\n")
        for i, ln in enumerate(lines):
            if re.search(r"(?<=\s)['′’](?=\s)", ln):
                bad.append((s["section_id"], ln[:60]))
            if re.fullmatch(r"\s*\d{1,2}\s*", ln):
                bad.append((s["section_id"], f"lone number {ln!r}"))
            if 0 < len(ln.strip()) <= 2:
                bad.append((s["section_id"], f"glyph line {ln!r}"))
            if "=" in ln and re.search(r"[+\-−×/÷^√Σ]", ln):
                t = re.sub(r"\[(?:p|Eq)\. [^\]]+\]", "", ln)
                for a, b in ("()", "[]", "{}"):
                    if t.count(a) != t.count(b):
                        bad.append((s["section_id"], f"{a}{b} in {ln[:70]!r}"))
    assert bad == []


# --- Appendix A -------------------------------------------------------------

def test_appendix_a_headings_and_notation():
    secs = _sections("A")
    assert {sid: s["title"] for sid, s in secs.items()} == {
        "A.1": "Load Notation", "A.2": "Load Combinations",
        "A.3": "Load Factors for Permanent Loads"}
    body = secs["A.1"]["body"]
    # p. A-2, as printed ("due shrinkage")
    assert "\nSH = Force effects due shrinkage\nTransient Loads\nBR = " in body
    # ten permanent and seventeen transient loads
    assert body.count(" = ") == 27


def test_appendix_a_tables_typed_in():
    secs = _sections("A")
    rows = {r.split(" | ")[0]: r.split(" | ")[1:]
            for r in secs["A.2"]["body"].split("\n") if " | " in r}
    assert len(rows) == 13
    # p. A-3: 13 columns after the limit state
    assert all(len(v) == 13 for v in rows.values())
    assert rows["STRENGTH I (unless noted)"][:3] == ["γp", "1.75", "1.00"]
    assert rows["EXTREME EVENT I"][1] == "γEQ"
    assert rows["SERVICE IV"][-1] == "(blank)"
    # p. A-4: the lambda method row (the letter is drawn, not in the text)
    assert "DD: Downdrag: Piles, λ Method | 1.05 | 0.30" in secs["A.3"]["body"]


def test_appendix_a_agrees_with_the_chapter_4_lookups():
    """Tables 4-1 and 4-2 (p. 4-4) give a subset of the appendix's AASHTO
    tables; the lookups that code them agree with pp. A-3 and A-4."""
    from geotech_references.gec_11 import tables
    body = _sections("A")["A.3"]["body"]
    names = {"DC": "DC: Component and Attachments",
             "EH Active": "EH: Horizontal Earth Pressure: Active",
             "EV Overall Stability": "EV: Vertical Earth Pressure: Overall Stability",
             "EV Retaining Walls": "EV: Vertical Earth Pressure: Retaining Walls and Abutments",
             "ES": "ES: Earth Surcharge"}
    for r in tables.table_4_2_permanent_load_factors():
        lo = "N/A" if r["gamma_min"] is None else f"{r['gamma_min']:.2f}"
        assert f"{names[r['load_type']]} | {r['gamma_max']:.2f} | {lo}" in body


# --- Appendix B -------------------------------------------------------------

def test_appendix_b_headings_as_printed():
    secs = _sections("B")
    assert {sid: s["title"] for sid, s in secs.items()} == {
        "B": ("Determination of Pullout Resistance Factors and MBW Unit – "
              "Geosynthetic Connection Strength"),
        "B.1": "Empirical Procedures to Determine F* and α",
        "B.2": "Experimental Procedures to Determine F* and α",
        "B.3": ("Connection Resistance and Strength of Partial and Full Friction "
                "Segmental Block/Reinforcement Facing Connections"),
        "B.4": "Connection Resistance Defined with Short-Term Testing",
        "B.4.1": "Protocol",
        "B.4.2": "Example Calculation",
    }
    # the contents list a B.5 References that the pages do not print
    assert "no B.5 is printed" in secs["B"]["applicability"]


def test_appendix_b_sentences_with_their_pages():
    secs = _sections("B")
    # p. B-2: the default alpha values
    assert ("[p. B-2] where Tan ρ is an apparent friction coefficient"
            in secs["B.1"]["body"])
    assert ("a default value of 1.0 can be used for α for inextensible reinforcements "
            "and a default value of 0.6 to 0.8 can be used for extensible "
            "reinforcements.") in secs["B.1"]["body"]
    # p. B-5: the deflection criteria
    assert ("[p. B-5] It is recommended that for inextensible reinforcements, a "
            "maximum deflection of ¾-inch (20 mm) measured at the front of the "
            "specimen") in secs["B.2"]["body"]
    # a sentence going on over a page break keeps its marker inline (p. B-6)
    assert "in general accordance with [p. B-6] Appendix D." in secs["B.3"]["body"]
    # p. B-12, printed with its stray full stop
    assert "long-term or short-term tests. as described below." in secs["B.4.1"]["body"]
    # p. B-17: the limits of the example's test program
    assert ("the limits of this test program are approximate wall heights of 2.4 "
            "to 14.9 ft.") in secs["B.4.2"]["body"]
    # p. B-18, as printed ("fro")
    assert "should not be used fro transportation works." in secs["B.4.2"]["body"]


def test_appendix_b_equations_as_printed():
    eqs = {e["id"]: e for s in _sections("B").values() for e in s["equations"]}
    assert sorted(eqs) == ["Eq. 4-41", "Eq. 4-43", "Eq. B-1", "Eq. B-2", "Eq. B-3", "Eq. B-4"]
    # p. B-6
    assert eqs["Eq. B-1"]["formula"] == "CRcr = Tcrc / Tlot"
    assert eqs["Eq. B-2"]["formula"] == "CRult = Tultconn / Tlot"
    # p. B-13
    assert eqs["Eq. B-3"]["formula"] == "CRu = Tultconn / Tlot"
    assert eqs["Eq. B-4"]["formula"] == "CRcr = CRu / RFCR"
    # chapter 4's equations printed again (pp. B-12 and B-13)
    assert eqs["Eq. 4-43"]["formula"] == "CRcr = Tultconn / (RFcr Tlot)"
    assert eqs["Eq. 4-41"]["formula"] == "Talc = Tult × CRcr / RFD"
    assert "printed again in Appendix B, p. B-12" in eqs["Eq. 4-43"]["notes"]
    assert eqs["Eq. B-1"]["variables"]["Tcrc"] == \
        "the extrapolated (75 - 100 year) connection test strength"


def test_appendix_b_tables_typed_in():
    body = _sections("B")["B.4.2"]["body"]
    assert ("[Table B-1, typed in from p. B-14, row by row:]\nStep | Item\n"
            "1 | Separate laboratory test data by failure mode – pullout and rupture"
            ) in body
    assert "8 | Define limits of applicability (i.e., limits of testing program " \
           "normal loading)" in body
    # the example's connection test data (p. B-16)
    rows = re.findall(r"^(\d) \| (\d+) \| ([\d.]+) \| (\d+) \| (\d+)$", body, re.M)
    assert len(rows) == 8
    assert rows[0] == ("1", "816", "2.4", "557", "1073")
    assert rows[7] == ("8", "5074", "14.9", "859", "1637")
    # tests 4 and 5 at one normal load: "7 normal loads", "Two tests at one
    # normal load" (p. B-15)
    assert len({r[1] for r in rows}) == 7
    assert "7 normal loads; Two tests at one normal load" in body


def test_appendix_b_example_arithmetic():
    """p. B-17: CRcr and Talc from Tultconn = 1068 + N tan 6°, RFcr = 1.9,
    Tlot = 1.10 Tult-MARV (4,730 = 1.10 x 4,300, p. B-15) and RFD = 1.15."""
    body = _sections("B")["B.4.2"]["body"]
    assert ("CRcr = Tultconn / (RFcr Tlot) = (1068 + N tan 6°) / (1.9 × 1.10 "
            "(Tult−MARV)) = (1068 + N tan 6°) / (2.09 (Tult−MARV))") in body
    assert ("Talc = (Tult × CRcr) / RFD = [Tult−MARV × (1068 + N tan 6°) / "
            "(2.09 (Tult−MARV))] / 1.15 = 444 + 0.044 N") in body
    assert round(1.9 * 1.10, 2) == 2.09 and round(4300 * 1.10) == 4730
    assert round(1068 / (2.09 * 1.15)) == 444
    assert round(math.tan(math.radians(6)) / (2.09 * 1.15), 3) == 0.044


def test_appendix_b_print_slips_noted():
    secs = _sections("B")
    # p. B-10: 75 years is about 657,000 hours, printed 670,000
    assert ("extrapolate to 75 years (670,000 hrs), per Appendix D. [Note: as "
            "printed; 75 years is about 657,000 hours.]") in secs["B.3"]["body"]
    assert round(75 * 365.25 * 24, -3) == 657000
    # p. B-18: the figure's line through the test data against the text's
    # tan 6 degrees
    x = [816, 1665, 2498, 2509, 2509, 3353, 4219, 5074]
    y = [1073, 1431, 1259, 1445, 1293, 1390, 1582, 1637]
    mx, my = sum(x) / 8, sum(y) / 8
    b = (sum((a - mx) * (c - my) for a, c in zip(x, y))
         / sum((a - mx) ** 2 for a in x))
    assert (round(b, 4), round(my - b * mx, 1)) == (0.1132, 1068.2)
    assert "gives y = 0.1132x + 1068.2, the figure's line" in secs["B.4.2"]["body"]


def test_appendix_b_figures_listed_with_their_lettering():
    secs = _sections("B")
    assert secs["B.2"]["figures"] == [
        "Figure B-1: Experimental procedure to determine F* and α for soil "
        "reinforcement using pullout test"]
    assert [f.split(":")[0] for f in secs["B.3"]["figures"]] == \
        ["Figure B-2", "Figure B-3", "Figure B-4"]
    assert secs["B.4.2"]["tables"] == [
        "Table B-1: Summary of steps for data reduction of MBW connection "
        "strength, with short-term (quick) test data"]
    # the symbols Figure B-1 defines (p. B-4)
    assert ("F* = Fq αβ if passive resistance controls pullout capacity (grids "
            "if St ≥ Sopt.)") in secs["B.2"]["body"]
    assert "α = F*m / F*peak" in secs["B.2"]["body"]


# --- Appendix C -------------------------------------------------------------

def test_appendix_c_steel_dimensions_typed_in():
    body = _sections("C")["C"]["body"]
    rows = re.findall(r"^(W[\d.]+\*?) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+)$",
                      body, re.M)
    # eleven welded wire sizes and four bar mat sizes (p. C-1)
    assert len(rows) == 15
    assert ("W4.5*", "0.045", "0.239", "29.0", "6.0") in rows
    assert "*Typical min. size for permanent walls" in body
    # each diameter is the area's circle; the metric cells convert the inch
    # cells (W4.5's 6.07 mm printed 6.0, noted)
    for name, a_in, d_in, a_mm, d_mm in rows:
        assert abs(math.sqrt(4 * float(a_in) / math.pi) - float(d_in)) < 0.0006, name
        assert abs(float(a_in) * 645.16 - float(a_mm)) < 0.6, name
        if name != "W4.5*":
            assert abs(float(d_in) * 25.4 - float(d_mm)) < 0.051, name
    assert "W4.5's diameter of 0.239 in. is 6.07 mm; printed 6.0." in body
    # the yield and tensile strengths as printed: welded wire 65/80 ksi,
    # strips and bar mats 65/75 ksi
    assert "Fy/Fu: 65/80 ksi (450/550 MPa)" in body
    assert body.count("65/75 ksi (450/520 MPa)") == 2


# --- the build ------------------------------------------------------------

def test_rebuild_reproduces_the_committed_files():
    pytest.importorskip("fitz")
    if not PDF.exists():
        pytest.skip("PDF not checked out")
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import build_gec11_appendix as builder
    finally:
        sys.path.remove(str(ROOT / "scripts"))
    built = builder.build_appendices(set(BUILT))
    assert sorted(built) == sorted(BUILT)
    for letter, data in built.items():
        committed = (PKG / "text" / f"appendix_{letter.lower()}.json").read_text(encoding="utf-8")
        assert builder.bpt.chapter_json(data) == committed, letter
