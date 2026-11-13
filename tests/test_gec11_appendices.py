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
BUILT = {"A": 12, "B": 13, "C": 14, "D": 15, "E": 16}


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
def test_caption_kept_with_its_typed_table(letter):
    """A long section is split into parts, never between a caption and its
    typed-in table or figure lettering; no paragraph mark is left over."""
    for s in _appendix(letter)["sections"]:
        assert "¶" not in s["body"], s["section_id"]
        for num in re.findall(r"\[Table (\S+), typed in from p\.", s["body"]):
            assert re.search(rf"(?:^|\n\n|\] )Table {re.escape(num)}\. ", s["body"]), (
                s["section_id"], num)
        for num in re.findall(r"\[Figure (\S+) lettering, typed in", s["body"]):
            assert re.search(rf"(?:^|\n\n|\] )Figure {re.escape(num)}\. ", s["body"]), (
                s["section_id"], num)


#: Formula lines printed with brackets that do not pair, each noted in the
#: text (p. E5-26).
PRINTED_UNPAIRED = {
    "ΔσH(Z−) = [(2)(5.55 k/ft)/16.29 ft)][16.29 ft – 6.04 ft)/16.29 ft)] [1.00] = 0.43 ksf",
    "ΔσH(Z+) = [(2)(5.55 k/ft)/16.29 ft)][16.29 ft – 8.50 ft)/16.29 ft)] [1.00] = 0.33 ksf",
    "ΔσH(Z−) = [(2)(3.79 k/ft)/16.29 ft)][16.29 ft – 6.04 ft)/16.29 ft)] [1.50] = 0.44 ksf",
    "ΔσH(Z+) = [(2)(3.79 k/ft)/16.29 ft)][16.29 ft – 8.50 ft)/16.29 ft)] [1.50] = 0.33 ksf",
    # Example E6, pp. E6-4 and E6-5
    "σH(Z-) = Kr(z-) [γr (Z(z-) + heq ] γP-EV = (0.707)[ 125 pcf (0 + 2)](1.35) = 239 psf",
    "σH-soil(Z+) = Kr(z+) [γr (Z(z+) + heq ] γP-EV = (0.650)[ 125 pcf (3.12 + 2)](1.35) = 562 psf",
    "σH(Z-) = Kr(z-) [γr (Z(z-) + heq ] γP-EV = (0.650)[ 125 pcf (3.12 + 2)](1.35) = 562 psf",
    "σH-soil(Z+) = Kr(z+) [γr (Z(z+) + heq ] γP-EV = (0.604)[ 125 pcf (5.62 + 2)](1.35) = 777 psf",
}


@pytest.mark.parametrize("letter", sorted(BUILT))
def test_no_scatter_patterns(letter):
    """A formula taken from the text layer that has come apart: a prime on
    its own, a lone number line above a formula, brackets that do not pair
    on a formula line (but for the lines printed so), a line of one or two
    glyphs."""
    bad = []
    for s in _appendix(letter)["sections"]:
        lines = [ln for ln in s["body"].split("\n") if ln not in PRINTED_UNPAIRED]
        for i, ln in enumerate(lines):
            if re.search(r"(?<=\s)['′’](?=\s)", ln):
                bad.append((s["section_id"], ln[:60]))
            if re.fullmatch(r"\s*\d{1,2}\s*", ln):
                bad.append((s["section_id"], f"lone number {ln!r}"))
            if 0 < len(ln.strip()) <= 2:
                bad.append((s["section_id"], f"glyph line {ln!r}"))
            if "=" in ln and re.search(r"[+\-−×/÷^√Σ]", ln):
                t = re.sub(r"\[(?:p|Eq)\. [^\]]+\]", "", ln)
                # a numbered step ("2)  Calculate ...") is not a bracket
                t = re.sub(r"^\s*\d{1,2}\)\s", "", t)
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


# --- Appendix D -------------------------------------------------------------

def test_appendix_d_headings_as_printed():
    secs = _sections("D")
    titles = {sid: s["title"] for sid, s in secs.items() if "(continued" not in s["title"]}
    assert titles == {
        "D.1": "Background",
        "D.2": "Step-by-Step Procedures for Extrapolating Stress Rupture Data – "
               "Conventional Method",
        "D.3": "Procedures for Extrapolating Creep Rupture Data – Stepped "
               "Isothermal Method (SIM)",
        "D.4": "Determination of RFCR",
        "D.5": 'Use of Creep Data from "Similar" Products and Evaluation of Product Lines',
        "D.6": "Creep Extrapolation Examples Using Stress Rupture Data",
        "D.6.1": "Stress Rupture Extrapolation Example",
        "D.7": "Recommended Procedures to Determine Tal"}
    # the title page's credit line is said where the appendix is placed
    # (the appendix's title page holds no text of its own)
    assert "after WSDOT Standard Practice T 925" in secs["D.1"]["applicability"]
    assert _appendix("D")["chapter_title"].startswith(
        "Appendix D: Determination of Creep Strength Reduction Factor, RFCR")
    # the contents' page slips, said on the section they are about
    assert 'on p. "E-16"' in secs["D.6"]["applicability"]


def test_appendix_d_equations_as_printed():
    eqs = {e["id"]: e for s in _appendix("D")["sections"] for e in s["equations"]}
    assert {k: v["formula"] for k, v in eqs.items()} == {
        "Eq. D-1": "RFCR = Tultlot / Tl",
        "Eq. D.2-1": "tamb = (telev) (aT)",
        "Eq. D.2-2": "Tl = Pcl / (1.2)^(x-1)",
        "Eq. D.3-1": "log tL = log treg ± [tα,n-2 √(1/n + (P − P̄)² / Σ(Pi − P̄)²)] × σ",
        "Eq. D.3-2": "σ = √({Σ[log ti − log t̄]² − {Σ[(Pi − P̄)(log ti − log t̄)]}² "
                     "/ Σ(Pi − P̄)²} / (n − 2))",
        "Eq. D.4-1": "RFCR = Tultlot / Tl"}
    assert "log td – log tmax" in eqs["Eq. D.2-2"]["variables"]["x"]
    body = "\n".join(s["body"] for s in _appendix("D")["sections"])
    # p. D-10: the factor may go up to (1.4)^x; p. D-1: the tolerance is ±
    assert "increased to as much as (1.4)^x if" in body
    assert "maintained at ±3.6° F (2° C)" in body


def test_appendix_d_example_arithmetic():
    """D.6.1 (p. D-17): the creep limit load of 63.4 kN/m, 1.68 log cycles
    beyond the data, and the lot strength of 110 kN/m."""
    body = _sections("D")["D.6.1"]["body"]
    assert "Tl = (63.4 kN/m) / (1.2)^(1.68 − 1) = 56.0 kN/m" in body
    assert round(63.4 / 1.2 ** (1.68 - 1), 1) == 56.0
    assert "RFCR = (110 kN/m) / (56.0 kN/m) = 2.0" in body
    assert round(110 / 56.0, 1) == 2.0
    # 1.68 log cycles short of 1,000,000 hours is about 21,000 hours, the
    # last rupture point on Figure D.6-2
    assert round(10 ** (6 - 1.68), -3) == 21000
    assert "fifteen rupture points" in body and "labelled 63.4 there" in body


def test_appendix_d_print_slips_noted():
    body = "\n".join(s["body"] for s in _appendix("D")["sections"])
    # p. D-9: 0.05 to 0.18 decades per degree over 10 degrees is not 12 to 15
    assert "time shift factor of 12 to 15) and 0.05 to 0.12" in body
    assert round(10 ** (0.05 * 10)) == 3 and round(10 ** (0.18 * 10)) == 63
    assert 0.10 < math.log10(12) / 10 and math.log10(15) / 10 < 0.12
    assert "gives time shift factors of about 3 to 63" in body
    # the equations the text points to by other numbers
    assert 'as printed, "Equation B.2-3"; this appendix has no such equation' in body
    assert "Equation D.2-3 is then used to determine Tl. [Note: as printed;" in body
    assert 'as printed, "Equation D.4"; the formula used is Equation D.2-2.' in body
    assert "the equation is D.3-1 in this appendix" in body
    # p. D-16: the equation that "the following" points to is not printed
    assert "accordance with the following: [Note: as printed; no equation follows" in body
    assert "Tal = P95 / (RFID × RFD)\n\nwhere,\nP95 = " in body


# --- Appendix E -------------------------------------------------------------

def _e_body(example=None):
    secs = _appendix("E")["sections"]
    if example:
        secs = [s for s in secs if s["section_id"] == example
                or s["section_id"].startswith(example + ".")]
    return "\n".join(s["body"] for s in secs)


def test_appendix_e_headings_as_printed():
    secs = _sections("E")
    assert secs["E"]["title"] == "Example Calculations"
    assert secs["E.1"]["title"] == ("MBW Unit Faced, MSE Wall with Broken Backslope "
                                    "and Live Load Surcharge, Reinforced with Geogrids")
    assert "Broken Back Sloping Fill" in secs["E.1"]["applicability"]
    assert secs["E"]["tables"] == ["Table E0: Summary of Example Problems"]
    # the parts of a long example say they are not printed sections
    assert "the letter is not printed" in secs["E.1.a"]["applicability"]


def test_appendix_e1_working_as_printed():
    """Example E1's formula lines as typed in from the pages, and their
    arithmetic (pp. E1-4 to E1-13)."""
    body = _e_body("E.1")
    for line in (
        "Γ = [1 + √( sin(φ′b + δ) sin(φ′b − β) / (sin(θ − δ) sin(θ + β)) )]²",
        "Kab = sin²(θ + φ′b) / [Γ sin²θ sin(θ − δ)] = sin²(90 + 30) / "
        "[2.133 sin²(90) sin(90 − 12.7)] = 0.360",
        "F1 = ½ γb h² Kab = ½ (125 pcf) (29 ft)² (0.360) = 18.92 k/lft",
        "Rr = [γEV (V1 + V2) + γEH (FV1) + γLS (FV2)] × μ",
        "CDRS = Rr / Pd = 36.0 k/lft / 32.15 k/lft = 1.12 ∴O.K.",
        "= 237.00 k-ft / 62.36 k = 3.80 ft",
        "= 226.36 k-ft / 81.65 k = 2.77 ft",
        "qV-F = 81.65 k/lft / [18 ft − 2(2.77 ft)] = 6.55 ksf",
        "Ka = tan²(45 − φ′r/2) = tan²(45 − 34/2) = 0.283",
        "Seq = (½) 0.7H tanβ = (½) 0.7 (20 ft) tan 26.6 = 3.51 ft",
        "Le ≥ TMAX / (φ F* α σv C Rc) ≥ 3 ft (1 m)",
    ):
        assert line in body, line
    r = math.radians
    s = math.sin
    gamma = (1 + math.sqrt(s(r(42.7)) * s(r(17.3)) / (s(r(77.3)) * s(r(102.7))))) ** 2
    assert round(gamma, 3) == 2.133
    assert round(s(r(120)) ** 2 / (2.133 * s(r(77.3))), 3) == 0.360
    assert round(0.5 * 0.125 * 29 ** 2 * 0.360, 2) == 18.92
    assert round(1.50 * 18.46 + 1.75 * 2.55, 2) == 32.15
    assert round((55.12 + 6.24 + 1.75 * 0.57) * 0.577, 1) == 36.0
    assert round(237.00 / 62.36, 2) == 3.80 and round(226.36 / 81.65, 2) == 2.77
    assert round(81.65 / (18 - 2 * 2.77), 2) == 6.55
    assert round(math.tan(r(28)) ** 2, 3) == 0.283
    assert round(0.5 * 0.7 * 20 * math.tan(r(26.6)), 2) == 3.51


def _typed_rows(body, table):
    block = body.split(f"[Table {table}, typed in from p")[1].split("\n\n")[0]
    return [ln.split(" | ") for ln in block.split("\n")[2:] if " | " in ln]


def test_appendix_e1_tables_typed_in():
    body = _e_body("E.1")
    # Table E1-7.4: CDR = Tr / TMAX on every row
    rows = _typed_rows(body, "E1-7.4")
    assert len(rows) == 11
    for layer, z, sv, tmax, grade, tr, cdr in rows:
        assert round(float(tr.replace(",", "")) / float(tmax), 2) == float(cdr), layer
    # Table E1-7.5: CDR = available / required Le
    for row in _typed_rows(body, "E1-7.5"):
        assert abs(float(row[3]) / float(row[6]) / float(row[7]) - 1) < 0.03, row[0]
    # Table E1-7.6: the factored connection strength is 0.90 Talc
    for row in _typed_rows(body, "E1-7.6"):
        talc = float(row[2])
        assert row[3].startswith(str(round(0.9 * talc))), row[0]
    # Table E1-7.3: Tal = Tult / (RFID x RFCR x RFD), Tr = 0.90 Tal
    assert round(3000 / (1.3 * 1.85 * 1.15)) == 1085
    assert round(9000 / (1.2 * 1.85 * 1.15)) == 3525 and round(0.9 * 9000 / (1.2 * 1.85 * 1.15)) == 3173


def test_appendix_e1_print_slips_noted():
    body = _e_body("E.1")
    assert 'as printed, "F2" in the second line; the value used, 2.55 k/lft, is FH2' in body
    assert "this figure is numbered E.1.6-1" in body
    assert 'as printed, "Step 6.a"; the eccentricity check is Step 6.2.' in body
    assert "limit state is ___ ksf. [Note: as printed, the value is left blank.]" in body
    assert "works with Tult = 3,000, 6,000 and 9,000 lb/ft" in body
    assert "the σH column is not the stress the TMAX column was worked from" in body
    # the worked layer 3 of Table E1-7.2: sigma_H = 391 lb/ft2, TMAX = 781 lb/lft
    sigma = 0.283 * 125 * (4.67 + 3.51) * 1.35
    assert round(sigma) == 391 and round(sigma * 2.0) == 781


def test_appendix_e2_working_as_printed():
    """Example E2's bearing checks as typed in from pp. E2-3 to E2-10, and
    their arithmetic."""
    secs = _sections("E")
    assert secs["E.2"]["title"] == ("Bearing Check for Example E1 MSE Wall without "
                                    "and with High Groundwater, and with a Sloping Toe")
    body = _e_body("E.2")
    for line in (
        "F1 = ½ γb h² Kab = ½ (125 pcf) (29 ft)² (0.360) = 18,922 lb/lft = 18.92 k/lft",
        "[p. E2-4] Step 6. Evaluate Bearing on Foundation",
        "eb-ser = (178.51 k-ft + 36.98 k-ft − 0 − 30.36 k-ft − 42.57 k-ft) / 59.85 k "
        "= 142.55 k-ft / 59.85 k = 2.38 ft",
        "= 59.85 k/lft / 13.24 ft = 4.52 ksf",
        "qn = cf Nc + 0.5 L' γf Nγ = 0 Nc + 0.5 (12.46ft) (125 pcf) (22.4) = 17.44 ksf",
        "CDRStrength = qR / σV-F = 11.34 ksf / 6.55 ksf = 1.73 ∴O.K.",
        "[p. E2-7] E2-2 CALCULATIONS WITH GROUNDWATER NEAR SURFACE",
        "Cwγ = 0.5 + 0.5 (12 ft − 2 ft) / (20.69 ft − 2 ft) = 0.77",
        "= 13,432 psf = 13.43 ksf",
        "CDRStrength = qR / σV-F = 8.73 ksf / 6.55 ksf = 1.33 ∴O.K.",
        "[p. E2-9] E2-3 CALCULATIONS WITH TOE SLOPE AND WITHOUT GROUNDWATER",
        "qn = 0.5 L' γf Nγq = 0.5 (12.46 ft) (125 pcf) (18) = 14,017 psf = 14.02 ksf",
        "CDRStrength = qR / σV-F = 9.11 ksf / 6.55 ksf = 1.39 ∴O.K.",
    ):
        assert line in body, line
    # the Cw-gamma rows typed in from p. E2-7
    assert "Dw | Cwγ\n0.0 | 0.5\nDf | 0.5\n> 1.5 L' + Df | 1.0" in body
    e = (18.46 * 9.67 + 2.55 * 14.5 - 10.12 * 3 - (4.16 + 0.57) * 9) / 59.85
    assert round(e, 2) == 2.38
    assert round(59.85 / (18 - 2 * 2.38), 2) == 4.52
    assert round(0.5 * 12.46 * 0.125 * 22.4, 2) == 17.44
    assert round(0.65 * 17.44, 2) == 11.34 and round(11.34 / 6.55, 2) == 1.73
    assert round(1.5 * (18 - 2 * 2.77) + 2, 2) == 20.69
    assert round(0.5 + 0.5 * 10 / 18.69, 2) == 0.77
    assert round(0.5 * 12.46 * 125 * 22.4 * 0.77) == 13432
    assert round(0.65 * 13.43, 2) == 8.73 and round(8.73 / 6.55, 2) == 1.33
    assert round(0.5 * 12.46 * 125 * 18) == 14018  # printed 14,017
    assert round(0.65 * 14.02, 2) == 9.11 and round(9.11 / 6.55, 2) == 1.39


def test_appendix_e2_print_slips_noted():
    body = _e_body("E.2")
    assert "E2-1 CALCULATIONS\n\n[Note: as printed, numbered E2-1, as is the introduction" in body
    assert "the three terms shown add to 59.28 k/lft; 59.85 k/lft also takes in FV2" in body
    assert round(45 + 10.12 + 4.16, 2) == 59.28 and round(59.28 + 0.57, 2) == 59.85
    assert ('as printed, "Nγq = 20"; the value read from the figure on p. E2-9 and '
            'used below is 18.') in body


def test_appendix_e3_working_as_printed():
    """Example E3's formula lines as typed in from pp. E3-3 to E3-18, and
    their arithmetic."""
    secs = _sections("E")
    assert secs["E.3"]["title"] == ("Segmental Precast Panel MSE Wall with Sloping "
                                    "Backfill Surcharge")
    body = _e_body("E.3")
    for line in (
        "Ka = sin²(θ + φ′f) / [Γ sin²θ sin(θ − δ)]",
        "Γ = [1 + √( sin(φ′f + δ) sin(φ′f − β) / (sin(θ − δ) sin(θ + β)) )]²",
        "= [1 + √( (0.834)(0.060) / ((0.894)(0.894)) )]² = 1.563",
        "= 0.750 / [(1.563)(1.0)(0.894)] = 0.537",
        "For this example problem, tanβ = 0.5, and h = 30 ft + 24 ft (0.5) = 42.00 ft.",
        "σv = ΣV / (L − 2eL)",
        "ΔH = (tan β)(0.3H) / (1 − 0.3 tan β)",
        "Zp-ave = Z + 0.5(La tanβ + L tanβ) = Z + 0.5 tanβ (La + L)",
        "σH = Kr (γr Z) γP-EV + Kr (γr S) γP-EV = Kr [γr (Z + S) γP-EV]",
        "Tmax = (σh)(Atrib) = (0.99 ksf)(12.50 ft²) = 12.37 k for panel of 5-ft width",
        "Tn = 65 ksi (0.200 in²) = 13.00 k/strip",
        "ΔH = (tanβ)(0.3H) / (1 − 0.3tanβ) = (0.5)(0.3 x 30 ft) / [1 − 0.3(0.5)] = 5.29 ft",
        "Pr = (1.0)(1.420)(2)(0.164 ft)(13.41 ft)(2.175 ksf) = 13.58 k/strip",
        "Prr = φPr = (0.90)(13.58 k/strip) = 12.23 k/strip",
    ):
        assert line in body, line
    r, s = math.radians, math.sin
    gamma = (1 + math.sqrt(s(r(56.56)) * s(r(3.44)) / (s(r(63.44)) * s(r(116.56))))) ** 2
    assert round(gamma, 3) == 1.563
    assert round(0.750 / (1.563 * 0.894), 3) == 0.537  # with the printed roundings
    beta = math.atan(0.5)  # the 2H:1V backslope
    ft = 0.5 * 0.125 * 42 ** 2 * 0.537
    assert round(ft * math.sin(beta), 2) == 26.48 and round(ft * math.cos(beta), 2) == 52.95
    assert round(0.125 * 30 * 24, 2) == 90.00 and round(0.5 * 24 * 12 * 0.125, 2) == 18.00
    assert round(math.tan(r(28)) ** 2, 3) == 0.283
    assert round(1.2 + math.log10(7.0), 3) == 2.045
    assert round(0.340 + 12.5 * 0.141 / 20, 3) == 0.428
    assert round(0.5 * 0.7 * 30 * math.tan(r(26.56)) * 0.125, 3) == 0.656
    assert round(2 + (3.386 - 2 * 0.58) / 0.16) == 16
    assert round(0.47 * 59 * 2, 2) == 55.46 and round(1.969 * 0.102, 2) == 0.20
    assert round(0.5 * 0.3 * 30 / (1 - 0.15), 2) == 5.29
    assert round(8.75 + 0.25 * (10.59 + 24.00), 2) == 17.40
    assert round(0.675 + 11.25 * 1.325 / 20, 3) == 1.420
    pr = 1.420 * 2 * 0.164 * 13.41 * 2.175
    assert round(pr, 2) == 13.58 and round(0.9 * pr, 2) == 12.23


def test_appendix_e3_tables_typed_in():
    body = _e_body("E.3")
    # Table E3-6.3: B' = L - 2eL and sigma_v = sum V / B'
    rows = {}
    for row in _typed_rows(body, "E3-6.3"):
        rows.setdefault(row[0], row)  # the critical-values rows repeat labels
    total = rows["Total vertical load at base of MSE wall, ΣV = R = VAb1+VAb2"]
    ecc = rows["Eccentricity at base of MSE wall, eL = 0.5*L – a"]
    width = rows["Effective width of base of MSE wall, B' = L-2eL"]
    stress = rows["Bearing stress due to MSE wall =ΣV/(L-2eL) = σv"]
    for col in (2, 3, 4):
        assert abs(24 - 2 * float(ecc[col]) - float(width[col])) <= 0.011
        assert round(float(total[col]) / float(width[col]), 2) == float(stress[col])
    # Table E3-7.3, every level
    rows = _typed_rows(body, "E3-7.3")
    assert [row[0] for row in rows] == [str(n) for n in range(1, 13)]
    for (level, z, zp, sigma, tmax, fstar, le, ppr, ptn,
         n_p, n_t, n_g, sh) in rows:
        z, zp, tmax, le = float(z), float(zp), float(tmax), float(le)
        assert abs(z + 0.25 * (48 - le) - zp) <= 0.0051, level
        f = 0.675 + max(0.0, 20 - z) * 1.325 / 20
        assert abs(f - float(fstar)) < 0.0015, level
        pull = 0.9 * float(fstar) * 2 * (1.969 / 12) * le * 0.125 * zp
        assert abs(pull / float(ppr) - 1) < 0.01, level
        assert abs(tmax - 12.5 * float(sigma)) < 0.07, level
        assert round(tmax / 9.75, 1) == float(n_t) and round(tmax / float(ppr), 1) == float(n_p)
        assert int(n_g) >= max(2, math.ceil(max(float(n_p), float(n_t))))
        assert round(5 / int(n_g), 2) == float(sh), level


def test_appendix_e3_print_slips_noted():
    body = _e_body("E.3")
    assert 'as printed, "Table E4-7.1"; the table is E3-7.1' in body
    assert 'as printed, "18.76" in Level 8' in body
    assert "as printed, γP-ES here; the factor used, 1.35, is γP-EV" in body
    assert "as printed, 13.13 k; Section 7.3 (p. E3-16) gives Tmax = 12.37 k" in body
    assert 'as printed, "dim" under Zp-ave, a depth in ft, and "φs(Tn)"' in body
    assert 'as printed, "Step 8"; the long-form calculations are in Step 7' in body
    assert "as printed, γr in FTV and FTH; Figure E3-2 has FT = ½ γf h² Kaf" in body


def test_appendix_e4_working_as_printed():
    """Example E4's formula lines as typed in from pp. E4-3 to E4-17, and
    their arithmetic."""
    secs = _sections("E")
    assert secs["E.4"]["title"].startswith("Segmental Precast Panel MSE Wall with Level Backfill")
    body = _e_body("E.4")
    for line in (
        "Kar = (1 - sin34°)/(1 + sin34°) = 0.283",
        "Kaf = (1 - sin30°)/(1 + sin30°) = 0.333",
        "F1 = ½(Kaf)(γf)H² | EH | H/3",
        "σv = ΣV / (L − 2eL)",
        "σH = Kr (γr Z) γP-EV + Kr (γr heq) γP-EV = Kr [γr (Z + heq) γP-EV]",
        "Tmax = (σh)(Atrib) = (1.02 ksf)(12.50 ft²) = 12.75 k/panel of 5-ft width",
        "For W15 wires\nD75 = 0.437 in. – (0.47 mil/year/side) (59 years) (2 sides)/1000 "
        "= 0.437 in. – 0.056 in.\nD75 = 0.381 in.",
        "equal to (π)(0.381 in.)²/4 = 0.1142 in²/wire",
        "Tn = 65 ksi (0.1142 in²) = 7.42 k/wire.",
        "F* = 0.623 + (20.00 ft – 9.37 ft)(1.246 – 0.623)/20 ft = 0.955",
        "Pr = (1.0)(0.955)(2)(1.00 ft)(10.31 ft)(1.171 ksf) = 23.06 k/ft",
        "Prr = φPr = (0.90)(23.06 k/ft) = 20.75 k/ft",
        "Np = 1 + (Tmax/Prr)/(Sl) = 1 + [(12.75 k/panel of 5 ft width)/(20.75 k/ft)]/(0.5 ft) = 2.2",
    ):
        assert line in body, line
    s = math.sin
    r = math.radians
    assert round((1 - s(r(34))) / (1 + s(r(34))), 3) == 0.283
    h = 23.64 + 2.0
    assert round(0.125 * h * 18, 2) == 57.69 and round(0.125 * 2 * 18, 2) == 4.50
    f1, f2 = 0.5 * 0.333 * 0.125 * h ** 2, 0.333 * 0.125 * 2 * h
    assert round(f1, 2) == 13.68 and round(f2, 2) == 2.13
    assert round(1.5 * f1 + 1.75 * f2, 2) == 24.26 and round(0.9 * f1 + 1.75 * f2, 2) == 16.05
    assert round(math.tan(r(30)) * 1.35 * 57.69, 2) == 44.96
    assert round(0.340 + 11.88 * 0.367 / 20, 3) == 0.558
    assert round(0.558 * 0.125 * 8.12 * 1.35, 2) == 0.76
    assert abs(0.47 * 59 * 2 / 1000 - 0.056) < 0.001 and round(0.437 - 0.056, 3) == 0.381
    assert round(65 * 0.1142, 2) == 7.42 and round(7.42 * 0.65, 2) == 4.82
    assert round(65 * 0.0795, 2) == 5.17 and round(5.17 * 0.65, 2) == 3.36
    assert round(18 - 0.3 * h, 2) == 10.31
    pr = 0.955 * 2 * 1.00 * 10.31 * 1.171
    assert round(pr, 2) == 23.06 and round(0.9 * pr, 2) == 20.75
    assert round(12.75 / 3.36, 1) == 3.8 and round(1 + (12.75 / 20.75) / 0.5, 1) == 2.2


def test_appendix_e4_tables_typed_in():
    body = _e_body("E.4")
    rows = {}
    for row in _typed_rows(body, "E4-6.3"):
        rows.setdefault(row[0], row)
    total = rows["Vertical load at base of MSE wall including LL on top, ΣV = R = V1 + VS"]
    ecc = rows["Eccentricity from center of wall base, eL = 0.5*L – a"]
    width = rows["Effective width of base of MSE wall, B' = L-2eL"]
    stress = rows["Bearing stress due to MSE wall =ΣV/(L-2eL) = σv"]
    resist = rows["Bearing resistance, (qnf-str for strength) or (qnf-ser for service) (given)"]
    cdr = rows["Capacity:Demand Ratio (CDR) = qnf:σv"]
    for col in (2, 3, 4):
        assert abs(18 - 2 * float(ecc[col]) - float(width[col])) <= 0.011
        assert abs(float(total[col]) / float(width[col]) - float(stress[col])) <= 0.006
        assert round(float(resist[col]) / float(stress[col]), 2) == float(cdr[col])
    # Table E4-7.4, every level; the transverse wire spacing from Table E4-7.3
    rows = _typed_rows(body, "E4-7.4")
    assert [row[0] for row in rows] == [str(n) for n in range(1, 11)]
    h = 25.64
    for (level, z, sigma, tmax, fstar, le, ppr, ptn, n_p, n_t, n_g, mat) in rows:
        n = int(level)
        st, wire, step = ((6, "W11", "0.5'") if n <= 4 else (12, "W15", "1'") if n <= 7
                          else (18, "W15", "1.5'"))
        z, tmax, le = float(z), float(tmax), float(le)
        f = 0.374 / st * (10 + 10 * max(0.0, 20 - z) / 20)
        assert abs(f - float(fstar)) < 0.0015, level
        la = 0.3 * h if z <= h / 2 else 0.6 * (h - z)
        assert abs(18 - la - le) < 0.006, level
        pull = 0.9 * float(fstar) * 2 * 1.0 * le * 0.125 * z
        assert abs(pull / float(ppr) - 1) < 0.01, level
        svt = 3.12 if n == 1 else 2.52 if n == 10 else 2.50
        assert abs(tmax - 5 * svt * float(sigma)) < 0.07, level
        assert abs(1 + 2 * tmax / float(ppr) - float(n_p)) <= 0.06, level
        assert abs(tmax / float(ptn) - float(n_t)) <= 0.06, level
        assert int(n_g) == math.ceil(max(float(n_p), float(n_t))), level
        assert mat == f"{n_g}{wire}+W11x{step}", level


def test_appendix_e4_print_slips_noted():
    body = _e_body("E.4")
    assert "as printed, Table 3.11.6.4-1 here; Step 2 cites Table 3.11.6.4-2" in body
    assert 'as printed, "Table E1-6.3"; the table is E4-6.3' in body
    assert 'as printed, "1.7Ka = 0.707"; 0.707 is 2.5Ka' in body
    assert "Steel loss = 0.16 mil/year/side [Note: as printed, 0.16; the rate used below is 0.47" in body
    assert 'as printed, without the "/1000" of the W15 line.' in body
    assert "as printed, 5.14; Tn above is 5.17 k/wire, and 5.17 × 0.65 = 3.36." in body
    assert 'as printed, "φs(Tn)"; the factor applied, 0.65, is φt (Table E4-5.2).' in body
    assert round(2.5 * 0.283, 3) == 0.707 and round(1.7 * 0.283, 3) == 0.481


def _near(a, b, tol=0.006):
    return abs(float(a) - float(b)) <= tol


def _cells(body, table):
    """A typed table's rows with its blank cells kept (stored "| |")."""
    return [[c.strip() for c in " | ".join(row).split("|")]
            for row in _typed_rows(body, table)]


def test_appendix_e5_working_as_printed():
    """Example E5's formula lines as typed in from pp. E5-6 to E5-29, and
    their arithmetic from the Step 2 values."""
    secs = _sections("E")
    assert secs["E.5"]["title"].startswith("Bridge Abutment Supported on Spread Footing")
    body = _e_body("E.5")
    for line in (
        "Ka1 = (1 - sin34°)/(1 + sin34°) = 0.283",
        "Ka3 = (1 - sin30°)/(1 + sin30°) = 0.333",
        "V0 = (γ2)(h2+h3)(b5) | EV | b5/2 + (bf − b5) | b5/2 + (bf + cf − b5)",
        "FA = F1 + F2 + FS1 | Based on each component | - | H (for external stability); "
        "H – (L1/3) (for internal stability)",
        "PnL = VA– hγ2(bf+cf)",
        "Δσv-footing = PwL / [(bf − 2ef) + (cf + H/2)]",
        "σv = ΣV / (L − 2eL)",
        "σvmax = σv + Δσv-footing",
        "σH = Kr [γr (Z + h + heqM) γP-EV + (Δσv-footing) γP-ES] + (ΔσH) γP-ES",
        "z− = Z− + h = 6.04 ft + 10.35 ft = 16.39 ft",
        "Δσv-footing = PwL / [(bf − 2ef) + (cf + Z/2)]",
        "σH-footing(Z−) = [Kr(Z−)Δσv-footing(Z−)] γP-ES = (0.365)(1.29 ksf)(1.00) = 0.47 ksf",
        "σH = 1.06 ksf + 0.12 ksf + 0.49 ksf + 0.39 ksf = 2.06 ksf",
        "Tmax = (σH)(Atrib) = (2.06 ksf)(24.60 ft²) = 50.7 k/panel of 10 ft width",
        "ER = (0.47 mil/year/side) (84 years) (2 sides) = 78.96 mils = 0.079 in., and",
        "Pr = (1.0)(0.832)(2)(0.164 ft)(15.06 ft)(2.20 ksf) = 9.04 k/strip",
        "Prr = φPr = (0.90)(9.04 k/strip) = 8.14 k/strip",
    ):
        assert line in body, line
    r = math.radians
    ka = (1 - math.sin(r(34))) / (1 + math.sin(r(34)))
    assert round(ka, 3) == 0.283
    # Table E5-4.3 and E5-4.4 from Step 2 (h = 10.35 ft, H = 25.5 ft, L = 26 ft)
    h, H, L, g, gc = 10.35, 25.5, 26.0, 0.125, 0.150
    assert _near(g * (3.85 + 5.00) * 5.25, 5.81) and _near(gc * 10.75 * 1.50, 2.42)
    assert _near(gc * 4.00 * 3.85, 2.31) and _near(g * H * L, 82.88)
    assert _near(g * h * L, 33.64) and _near(g * 2.96 * L, 9.62)
    assert _near(0.5 * ka * g * h ** 2, 1.89) and _near(g * h * H / 3, 11.00)
    assert _near(0.5 * g * H ** 2 / 3, 13.55) and _near(ka * g * 2.96 * h, 1.08)
    # Tables E5-6.1 to E5-6.3, Strength I (max)
    assert _near(1.5 * 6.53 + 1.75 * 5.60 + 4.43, 24.03)
    assert _near(1.35 * 5.81 + 1.25 * (2.42 + 2.31 + 0.75 + 10.60), 27.94)
    assert _near(1.5 * 1.89 + 1.75 * 1.08 + 0.82, 5.55)
    assert _near(27.94 + 1.75 * (5.70 + 2.31), 41.96)
    assert _near((0.5 + 8.16) * math.tan(r(45 + 34 / 2)), 16.29)
    # Table E5-7.1: the net bridge load PwL; Table E5-7.3: its spread to the base
    assert _near(h * 11.25 * g, 14.55) and _near(41.96 - 1.35 * 14.55 - 1.75 * 4.16, 15.03, 0.011)
    assert _near(8.16 + 0.5 + H / 2, 21.41) and _near(15.03 / 21.41, 0.70)
    # Step 8: Level 4, Strength I (max)
    assert _near(0.340 + 3.61 * 0.141 / 20, 0.365, 0.001)
    assert _near(0.365 * g * 16.39 * 1.35, 1.01, 0.01)
    assert _near(15.03 / (8.16 + 0.5 + 6.04 / 2), 1.29) and _near(11.18 / (8.66 + 4.25), 0.87)
    assert _near(2 * 5.55 / 16.29 * (16.29 - 6.04) / 16.29, 0.43)
    assert _near(2 * 3.79 / 16.29 * (16.29 - 6.04) / 16.29 * 1.5, 0.44)
    assert _near(2.06 * 24.60, 50.7, 0.05)
    assert round(2 + (3.386 - 2 * 0.58) / 0.16) == 16
    assert _near(0.47 * 84 * 2, 78.96) and _near(1.969 * 0.078, 0.154, 0.001)
    assert _near(65 * 0.154, 10.00, 0.011) and _near(10.00 * 0.75, 7.50)
    assert _near(0.675 + 2.38 * 1.325 / 20, 0.832, 0.001)
    assert _near(H - 11.25 / 0.6, 6.75) and _near(L - 0.6 * (H - 7.27), 15.06)
    pr = 0.832 * 2 * 0.164 * 15.06 * 2.20
    assert _near(pr, 9.04) and _near(0.9 * pr, 8.14)
    assert round(50.7 / 7.50, 1) == 6.8 and round(50.7 / 8.14, 1) == 6.2


def test_appendix_e5_tables_typed_in():
    body = _e_body("E.5")
    # Tables E5-4.3 and E5-4.4: each moment is the force times its arm, to
    # the rounding of the printed force and arm; F2's are noted in the text
    def product(value, arm, m):
        v, a = float(value), float(arm)
        return abs(v * a - float(m)) <= 0.005 * (v + a) + 0.006

    for force, value, arm_a, arm_b, _, m_a, m_b in (_cells(body, "E5-4.3")
                                                     + _cells(body, "E5-4.4")[:-1]):
        for arm, m in ((arm_a, m_a), (arm_b, m_b)):
            if arm and force != "F2 =":
                assert product(value, arm, m), force
    # F2's moments are those of 0.815 k/ft, not Step 2's 0.82 (noted)
    f2 = _cells(body, "E5-4.4")[1]
    assert f2[0] == "F2 =" and f2[1] == "0.82"
    assert round(0.815 * 5.43, 2) == float(f2[5]) and round(0.815 * 30.93, 2) == float(f2[6])
    rows = {}
    for row in _typed_rows(body, "E5-6.3"):
        rows.setdefault(row[0], row)
    ecc = rows["Eccentricity from center of footing, ef = 0.5*bf - awl"]
    width = rows["Effective width of spread footing, bf'=bf -2ef ="]
    stress = rows["Bearing stress, σv = VAb / (bf-2ef)"]
    load = rows["Sum of vertical forces from the footing for bearing stress "
                "analysis=VAb=V0+V1+V2+V3+DL+LL+VS1"]
    cdr = rows["Capacity:Demand Ratio (CDR) = qR:σv"]
    for col, q in ((2, 7.0), (3, 7.0), (4, 4.0)):
        assert _near(10.75 - 2 * float(ecc[col]), width[col], 0.011)
        assert _near(float(load[col]) / float(width[col]), stress[col])
        assert round(q / float(stress[col]), 2) == float(cdr[col])
    rows = {}
    for row in _typed_rows(body, "E5-7.1"):
        rows.setdefault(row[0], row)
    mrb = rows["Resisting moments about Point B without LL surcharge= MRB =MV4+MV5+MPnL"]
    mob = rows["Overturning moments about Point B = MOB = MFS3+MF3+MF4 +MFA (For MFA See Note 1)"]
    vb = rows["Vertical load at base of MSE wall without LL, VB = V4+V5 + PnL"]
    b = rows["Location of the resultant force on base of MSE wall from Point B, b =(MRB - MOB)/VB"]
    for col in (2, 3, 4):
        assert _near((float(mrb[col]) - float(mob[col])) / float(vb[col]), b[col])
    # the sum the row names, from Table E5-4.4 and Table E5-5.1, is Table E5-7.3's
    named = 1.75 * 27.09 + 1.5 * (140.21 + 115.15) + 5.55 * 25.5
    assert abs(named - 571.95) < 0.1 and float(mob[2]) > named
    rows = {}
    for row in _typed_rows(body, "E5-7.3"):
        rows.setdefault(row[0], row)
    v = rows["Vertical load at base of MSE wall including LL on top, V = V4+V5+VS"]
    ecc = rows["Eccentricity from center of wall, eL = 0.5*L – b"]
    width = rows["Effective width of base of MSE wall, B' = L-2eL"]
    wall = rows["Factored bearing stress due to MSE wall = V/(L-2eL)"]
    bridge = rows["Bearing stress due to PwL"]
    total = rows["Total bearing stress due to Component 1 + 2 = σvmax"]
    cdr = rows["Capacity:Demand Ratio (CDR) = qR:σvmax"]
    for col, q in ((2, 15.0), (3, 15.0), (4, 7.0)):
        assert _near(26 - 2 * float(ecc[col]), width[col], 0.011)
        assert _near(float(v[col]) / float(width[col]), wall[col])
        assert _near(float(bridge[col]) + float(wall[col]), total[col], 0.011)
        assert round(q / float(total[col]), 2) == float(cdr[col])
    # Table E5-8.1: Svt = Z+ − Z−
    for level, z, zm, zp, svt in _typed_rows(body, "E5-8.1"):
        lo, hi = float(zm.split("=")[-1]), float(zp.split("=")[-1])
        assert _near(hi - lo, svt, 0.001), level
    svts = {row[0]: float(row[4]) for row in _typed_rows(body, "E5-8.1")}
    # Table E5-8.3, every level
    rows = _typed_rows(body, "E5-8.3")
    assert [row[0] for row in rows] == [str(n) for n in range(1, 12)]
    ka = math.tan(math.radians(45 - 34 / 2)) ** 2
    tan_phi = math.tan(math.radians(34))
    for (level, z, kr, sigma, tmax, fstar, le, ppr, ptn, n_p, n_t, n_g, sh) in rows:
        zz = float(z) + 10.35
        f = max(0.0, 20 - zz) / 20
        assert _near(1.2 * ka + f * 0.5 * ka, kr, 0.0011), level
        assert _near(tan_phi + f * (2.0 - tan_phi), fstar, 0.0011), level
        z_dash = 25.5 - 11.25 / 0.6
        assert _near(26 - (11.25 if float(z) <= z_dash else 0.6 * (25.5 - float(z))), le), level
        pull = 0.9 * float(fstar) * 2 * 0.164 * float(le) * 0.125 * zz
        assert abs(pull / float(ppr) - 1) < 0.01, level
        assert abs(float(tmax) - 10 * svts[level] * float(sigma)) < 0.15, level
        assert _near(float(tmax) / float(ppr), n_p, 0.06), level
        assert _near(float(tmax) / float(ptn), n_t, 0.06), level
        assert int(n_g) == math.ceil(max(float(tmax) / float(ppr), float(tmax) / 7.50)), level
        assert _near(10 / int(n_g), sh, 0.051), level


def test_appendix_e5_print_slips_noted():
    body = _e_body("E.5")
    for note in (
        "as printed, MF2 = 4.43 and 25.21 k-ft/ft; with F2 = 0.82 k/ft as given in Step 2, "
        "0.82 k/ft × 5.43 ft = 4.45",
        'as printed, "anl" in the critical eccentricity row, which uses awl',
        'The overturning-moment row prints "MFS3" (Table E5-4.4 has MFS2)',
        "as printed, the overturning-moment row names MFS2+MF3+MF4, but its values also hold MFA",
        "as printed, 6.4; this is the settlement analysis of the MSE wall, listed as 7.4",
        'as printed, "Article 3.116"; the AASHTO article on surcharge loads, ES, is 3.11.6.',
        "as printed, 0.339 for 1.2Ka in these lines, where Step 8.1 gives 1.2(0.283) = 0.340",
        "as printed, the brackets of these ΔσH lines and of Method B's do not pair",
        'as printed, "(0.5 ft + 10.75 ft)0.6"',
        'as printed, "φs(Tn)"; the factor applied, 0.75, is φt (Table E5-5.2).',
        "\"Table E-4-8.3\", for this example's Table E5-8.3, and 12.5 ft, where "
        "25.5 ft/2 = 12.75 ft",
    ):
        assert note in body, note
    assert round(0.82 * 5.43, 2) == 4.45 and round(0.82 * 30.93, 2) == 25.36
    assert round(1.2 * 0.283, 3) == 0.340 and 25.5 / 2 == 12.75
    # the lines the scatter test lets pass are in the text as printed
    for line in PRINTED_UNPAIRED:
        if line.startswith("ΔσH"):
            assert line in body.split("\n"), line


def test_appendix_e6_working_as_printed():
    """Example E6, the traffic barrier impact on Example E4's wall: its
    formula lines as typed in from pp. E6-1 to E6-9, and their arithmetic."""
    secs = _sections("E")
    assert secs["E.6"]["title"].startswith("Traffic Barrier Impact Loading on Segmental")
    body = _e_body("E.6")
    for line in (
        "Kar = (1 - sin34°)/(1 + sin34°) = 0.283",
        "Atrib = (wp)(Svt)",
        "Tmax = σH Atrib + γCT (TCT)",
        "At Z+ = 3.12 ft, Kr(z+)= 0.340 + (20.00 ft – 3.12 ft)(0.707-0.340)/20.00 ft = 0.650",
        "σH = 0.5(239 psf + 562 psf) = 400 psf",
        "Tmax-R = (σH)(Atrib) + γCT (2,300 wp) = (400 psf)(15.60 ft²) + 1.0 [2,300 lb/ft (5 ft)]",
        "= 6,240 + 11,500 = 17.74 k/panel of 5-ft width",
        "Tmax-R = (σH)(Atrib) + γCT (600 wp) = (670 psf)(12.50 ft²) + 1.0 [600 lb/ft (5 ft)]",
        "Tn = 65 ksi (0.0795 in²) = 5.17 k/wire.",
        "Pr = α(F*)(2b)(Le)[(σv)(γP-EV)]",
        "F* = 0.623 + (20.00 ft – 1.87 ft)(1.247 – 0.623)/20 ft = 1.189",
        "Pr = (1.0)(1.189)(2)(1.00 ft)(18 ft)(484 psf) = 20,717 lb/ft",
        "Tmax-PO = (σH)(Atrib) + γCT (1,300 wp) = (400 psf)(15.60 ft²) + 1.0 [1,300 lb/ft (5 ft)]",
        "Pr = (1.0)(1.111)(2)(1.00 ft)(18 ft)(796 psf) = 31,836 lb/ft",
        "Np = 1 + (Tmax-PO/Prr)/(Sl)",
    ):
        assert line in body, line
    # the lines the scatter test lets pass are in the text as printed
    for line in PRINTED_UNPAIRED:
        if line.startswith("σH"):
            assert line in body.split("\n"), line
    r = math.radians
    ka = (1 - math.sin(r(34))) / (1 + math.sin(r(34)))
    assert round(ka, 3) == 0.283
    assert round(2.5 * 0.283, 3) == 0.707 and round(1.2 * 0.283, 3) == 0.340

    def kr(z):
        return 0.340 + (20 - z) * (0.707 - 0.340) / 20

    # Table E6-7.1
    rows = _cells(body, "E6-7.1")
    assert [row[0] for row in rows] == ["1", "2", "3"]
    assert _near(1.87 + 0.5 * (4.37 - 1.87), 3.12, 0.001)
    assert _near(4.37 + 0.5 * (6.87 - 4.37), 5.62, 0.001)
    assert rows[0][4] == "3.12" and rows[1][4] == "2.50"
    # Level 1 (Z− = 0, Z+ = 3.12 ft) and Level 2 (Z− = 3.12 ft, Z+ = 5.62 ft)
    g = 125
    assert round(kr(3.12), 3) == 0.650 and round(kr(5.62), 3) == 0.604
    assert round(0.707 * g * 2 * 1.35) == 239 and round(0.650 * g * 5.12 * 1.35) == 562
    assert round(0.604 * g * 7.62 * 1.35) == 777
    assert round(0.5 * (239 + 562)) == 400 and round(0.5 * (562 + 777)) == 670
    assert round(400 * 3.12 * 5.00 + 2300 * 5) == 17740
    assert round(670 * 2.50 * 5.00 + 600 * 5) == 11375
    assert round(400 * 3.12 * 5.00 + 1300 * 5) == 12740
    # Step 7.4 and 7.5
    assert round(65 * 0.0795, 2) == 5.17
    t_st = 0.374 / 6
    assert round(t_st, 4) == 0.0623
    assert round(20 * t_st, 3) == 1.247 and round(10 * t_st, 3) == 0.623

    def fstar(z):
        return 0.623 + (20 - z) * (1.247 - 0.623) / 20

    assert round(fstar(1.87), 3) == 1.189 and round(fstar(4.37), 3) == 1.111
    assert round(g * (1.87 + 2)) == 484 and round(g * (4.37 + 2)) == 796
    assert abs(1.189 * 2 * 1.00 * 18 * 484 - 20717) < 1
    assert abs(1.111 * 2 * 1.00 * 18 * 796 - 31836) < 1
    # Step 7.6
    assert round(17.74 / 5.17, 1) == 3.4 and round(11.38 / 5.17, 1) == 2.2
    assert math.ceil(17.74 / 5.17) == 4 and math.ceil(11.38 / 5.17) == 3


def test_appendix_e6_tables_typed_in():
    body = _e_body("E.6")

    def rows_of(table):
        # every row, those printed with a blank first cell ("| 7.3 ...") too
        block = body.split(f"[Table {table}, typed in from p")[1].split("\n\n")[0]
        return [[c.strip() for c in ln.split("|")] for ln in block.split("\n")[2:]]

    assert rows_of("E6-1")[0] == ["4", "Estimate unfactored loads"]
    assert [row[0] for row in rows_of("E6-1")] == ["4", "5", "7", "", "", "", "", "8"]
    assert rows_of("E6-1")[3][1].startswith("7.3 Calculate horizontal stress")
    assert rows_of("E6-5.1")[1] == ["Extreme II", "γP = 1.35", "0.50", "1.00"]
    rows = rows_of("E6-5.2")
    assert [row[2] for row in rows] == ["φt = 0.65", "φt = 1.0", "φp = 0.90", "φt = 1.0"]
    assert [row[3] for row in rows] == ["Table 11.5.6-1", "Article 11.5.7"] * 2


def test_appendix_e6_print_slips_noted():
    body = _e_body("E.6")
    for note in (
        "as printed; Example E6 has no Section E6-2",
        'as printed, "Table E4-5.1"; the table is E6-5.1, below.',
        'as printed, "φt = 1.0" in the pullout row; the pullout resistance factor is φp',
        'as printed, "EQ 4-34": the relation is Chapter 4\'s Eq. 4-30',
        "as printed, Z+ = 3.12 ft; Table E6-7.1 gives Z+ = 5.62 ft at Level 2",
        "as printed, 0.3748 in.; the diameter given above is 0.374 in.",
        'as printed, "600 lb/lft" in the line above; the pullout impact load at Level 1 '
        "is 1,300 lb/lft",
        "as printed, 1.4 and 2.4; (12.74/20.72)/0.5 = 1.23, which gives Np = 2.2.",
        "as printed, 0.87; (11.38/31.84)/0.5 = 0.71, and 1 + 0.71 = 1.7 as printed.",
        'as printed, "Ng, is 4.0"; here Nt = 2.2 governs, and 3 wires are selected.',
    ):
        assert note in body, note
    assert round(1 + (12.74 / 20.72) / 0.5, 1) == 2.2
    assert round((11.38 / 31.84) / 0.5, 2) == 0.71


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
