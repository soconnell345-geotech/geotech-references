"""GEC-10 (FHWA-NHI-18-024, 2018) appendices pinned to the print.

REF-85 (app backlog): the design example and the other appendices were held
as a condensed paraphrase (Appendix A, three sections) or not at all, so the
references helper could not search or quote them. Each appendix is now built
from the printed pages: bodies in the print's own wording with [p. A-5]
markers, every calculation line, equation and table typed in from a rendered
page (the text layer drops sub- and superscripts and carries equations as
spoken words). Where the print disagrees with itself the stored text keeps
the print and says so "(as printed; ...)". Printed A.2 (pp. A-4 to A-28) is
stored as A.2 and parts A.2.a to A.2.g, the letters not printed, to fit the
reference tools' size limit.
"""

import json
import re

import pytest

from geotech_references._retrieval import load_chapter, retrieve_section


def _section(sid):
    return retrieve_section("gec_10", sid)


def _text(sid):
    s = _section(sid)
    eqs = [e if isinstance(e, str) else json.dumps(e, ensure_ascii=False)
           for e in s["equations"]]
    return " ".join([s["body"]] + s["key_points"] + s["tables"] + s["figures"] + eqs)


def _appendix(ch):
    return load_chapter("gec_10", ch)


def _appendix_text(ch):
    return " ".join(_text(s["section_id"]) for s in _appendix(ch)["sections"])


# ---------------------------------------------------------------- Appendix A

A_IDS = ["A", "A.1", "A.2", "A.2.a", "A.2.b", "A.2.c", "A.2.d", "A.2.e", "A.2.f",
         "A.2.g", "A.3"]


def test_appendix_a_sections_and_titles():
    data = _appendix(19)
    assert data["chapter_title"] == (
        "Appendix A: Design Example: Drilled Shafts for Replacement Bridge")
    assert [s["section_id"] for s in data["sections"]] == A_IDS
    titles = {s["section_id"]: s["title"] for s in data["sections"]}
    # printed headings, pp. A-1, A-4 and A-29
    assert titles["A.1"] == "General"
    assert titles["A.2"] == "Scour and Seismic Considerations"
    assert titles["A.3"] == "Summary"
    for sid in A_IDS[3:10]:
        assert titles[sid].startswith("Scour and Seismic Considerations (continued, ")
        assert "The letter is not printed" in _section(sid)["applicability"]


def test_appendix_a_page_markers_run_in_order():
    pages = []
    for s in _appendix(19)["sections"]:
        pages += [int(p) for p in re.findall(r"\[p\. A-(\d+)\]", s["body"])]
    assert pages[0] == 1 and pages[-1] == 29
    assert pages == sorted(pages)


def test_appendix_a_no_spoken_equations_left():
    # the text layer carries each equation as words ("N sub 60 times ...")
    text = _appendix_text(19)
    for spoken in (" sub ", "equals the square root", "times the fraction", "to the power of"):
        assert spoken not in text


def test_appendix_a_equations_a1_a2():
    # p. A-8 (PDF 591)
    eqs = {e["id"]: e for e in _section("A.2.a")["equations"]}
    assert eqs["Eq. A-1"]["formula"] == "(N1)60 = N60 (pa / σ′vo)^n"
    assert eqs["Eq. A-1"]["variables"]["pa"] == "atmospheric stress (2,116 psf)"
    assert eqs["Eq. A-1"]["variables"]["n"] == "0.5 for sandy soils"
    assert eqs["Eq. A-2"]["formula"] == "φ′ = 27.5 + 9.2 log[(N1)60]"
    body = _section("A.2.a")["body"]
    assert "(N1)60 = N60 (pa / σ′vo)^n (A-1)" in body
    assert "φ′ = 27.5 + 9.2 log[(N1)60] (A-2)" in body
    # the ≤ is a < with an underline in the print
    assert "within the specified limit (≤ 45%)" in body


@pytest.mark.parametrize("printed", [
    # Layer 3, beta method, p. A-10
    "φ′ = 27.5 + 9.2 log[(N1)60] = 27.5 + 9.2[log(21)] = 40 degrees",
    "σ'p = pa [0.47 (N60)^m] = 2,116 psf [0.47 (30)^0.6] = 7,654 psf",
    "Ko = (1 – sin φ') OCR^(sin φ') = (1 – sin 40°) 1.65^(sin 40) = 0.49 ≤ Kp",
    "β = K tan δ = 0.49 tan 40° = 0.41",
    "(φs RSN)i = 3 = 0.55 (470,684 lb) = 258,876 lb",
    # Layer 4, alpha method, pp. A-10 and A-11
    "su(UC) / su(CIUC) = 0.893 + 0.513 log(su(UC) / σ̄vo) = "
    "0.893 + 0.513 log(1,750 psf / 2,114 psf) = 0.851",
    "su(CIUC) = 1,750 psf / 0.851 = 2,057 psf",
    "fSN = α su = 0.47 (2,057 psf) = 976 psf",
    "(φs RSN)i = 4 = 0.45 (368,124 lb) = 165,656 lb",
    # base, p. A-11
    "qBN = 0.60 N60 = 0.60 (41) = 24.6 tsf = 49.2 k/ft²",
    "RBN = π/4 (8 ft)² 49.2 k/ft² = 2,473 kips",
    "∑φiRi = 1,087,053 + 1,181,955 + 1,236,531 = 3,505,539 lb = 3,506 kips",
    # Service I, pp. A-13 and A-14
    "“Failure Threshold” L2 = RSN + RBN = (1,976.5 + 2,626.6) + 2,473.1 = 7,076.2 kips",
    "Rservice = 5,519 – W = 5,519 – 885.0 = 4,634 kips",
])
def test_appendix_a_axial_calculations(printed):
    assert printed in _section("A.2.b")["body"]


def test_appendix_a_print_slips_kept_and_noted():
    body = _section("A.2.b")["body"]
    # p. A-10: the RSN line prints 932 lb/ft2 where fSN is 936 psf
    assert "932 lb/ft² = 470,684 lb (as printed; fSN above is 936 psf" in body
    # p. A-11: the RSN line prints 967 lb/ft2 where fSN is 976 psf
    assert "967 lb/ft² = 368,124 lb (as printed; fSN above is 976 psf" in body
    # p. A-11: 2,114 substituted for pa
    assert "(2,057 / 2,114) = 0.47 (as printed; p. A-8 gives pa = 2,116 psf" in body
    # p. A-10 cites Table A-5 for the 0.55 resistance factor
    assert "is 0.55 (Table A-5 as printed;" in body
    # p. A-8: tip elevations
    assert "(elevation -67 ft to elevation -268 ft) (as printed;" in _section("A.2.a")["body"]
    # p. A-21: the bracket evaluates to 18,935.8 kips
    assert "Pr = 18,936.8 kips >> 3,389.5 kips (as printed;" in _section("A.2.e")["body"]


@pytest.mark.parametrize("sid,printed", [
    # resultant demands, pp. A-15, A-18, A-20
    ("A.2.c", "V = √[(Vlongitudinal)² + (Vtransverse)²] = √[(36.98)² + (9.63)²] = 38.21 kips"),
    ("A.2.c", "√[(1,686.87)² + (221.68)²] = 1,701.37 kip-ft"),
    ("A.2.c", "V = √[(Vlongitudinal)² + ((1/3) Vtransverse)²] = √[(144.52)² + (290.48/3)²] "
              "= 173.96 kips"),
    ("A.2.c", "√[(7,776.42)² + (3,212.32/3)²] = 7,849.79 kip-ft"),
    ("A.2.d", "√[(54.65)² + (34.59)²] = 64.68 kips"),
    ("A.2.d", "√[(2,647.17)² + (317.24)²] = 2,666.11 kip-ft"),
    # nominal moment resistance, p. A-19
    ("A.2.d", "for ρ = 1% MN (ft-k) = 27 D³ = 27 (8ft)³ = 13,824 ft-k = 165,888 in-k"),
    ("A.2.d", "for ρ = 1.5% MN (ft-k) = 40 D³ = 40 (8ft)³ = 20,480 ft-k = 245,760 in-k"),
    # axial resistance, p. A-21
    ("A.2.e", "Pr = φPn = φβ [0.85 fc' (Ag – As) + As fy] = 0.75(0.85) "
              "[0.85 x 4(7,238 – 90) + 90(60)]"),
    # shear, pp. A-23 and A-24
    ("A.2.f", "Vc = 0.0632λ √f′c bv dv = 0.0632 √(4 ksi) (96 in)(66.98 in) = 812.8 kips"),
    ("A.2.f", "0.5φVc = 0.50 (0.90) 812.8 kips = 365.7 kips"),
    ("A.2.f", "Av (in²) ≥ 0.0316 λ √f′c (bv s / fy) = 0.0316 (1.0) √(4 ksi) (96 in (s) / 60 ksi) "
              "= 0.101 x s"),
    ("A.2.f", "dv = 0.9 (D/2 + Dr/π) = 0.9 (96/2 + 83/π) = 66.98 in"),
    ("A.2.f", "α = cos⁻¹ [6 in / (π x 84 in)] = 88.7 degrees"),
    ("A.2.f", "Vs = Av fy dv / s = (0.785 in²)(60 ksi)(66.98 in) / 6 in = 525.8 kips"),
    ("A.2.f", "Vn = Vc + Vs = 812.8 + 525.8 = 1,338.6 kips"),
    ("A.2.f", "Vr = φVn = 0.90 (1,338.6 kips) = 1,204.7 kips"),
])
def test_appendix_a_lateral_and_structural_calculations(sid, printed):
    assert printed in _section(sid)["body"]


@pytest.mark.parametrize("sid,table,cells", [
    ("A.2", "Table A-1:", ["Extreme Event I: 2,823.04; 2,810.26; 144.52; 290.48; 7,776.42; "
                           "3,212.32"]),
    ("A.2.a", "Table A-2:", ["6: -139; -219.5; 80.5; 110 to 190.5; D and E; cohesive"]),
    ("A.2.b", "Table A-3:", ["(N1)60 25, 26, 14, 16, 20; mean 21; 23%; φ 40"]),
    ("A.2.b", "Table A-4:", ["Σ 1,087,053", "Σ 1,181,955", "1,236,531",
                             "Summation of Factored Resistances = 3,506 kips"]),
    ("A.2.b", "Table A-5:", ["Σ 4,832,242", "Σ 2,626,566",
                             "Summation of Factored Resistances = 9,932 kips"]),
    ("A.2.c", "Table A-6:", ["Moment of inertia: 4,169,220 in^4", "Area: 7,238 in^2"]),
    ("A.2.c", "Table A-7:", ["6: 1.50; 57,320; 30,624,726; 1,836,420; 1.056"]),
    ("A.2.c", "Table A-8:", ["5: 1.25; 217,450; 117,746,908; 2,810,260; 0.512"]),
    ("A.2.e", "Table A-9:", ["Extreme Event I: 1.08E+08; 8,966; 96.48; 8.0"]),
    ("A.2.g", "Table A-10:", ["Type I Portland Cement 526; 2.68", "Water to Cement Ratio 0.41"]),
])
def test_appendix_a_tables_typed_from_the_page(sid, table, cells):
    s = _section(sid)
    rows = [t for t in s["tables"] if t.startswith(table)]
    assert len(rows) == 1
    for cell in cells:
        assert cell in rows[0]
    assert f"[{table[:-1]}]" in s["body"]


def test_appendix_a_figures_listed_once():
    figs = [f for s in _appendix(19)["sections"] for f in s["figures"]]
    assert [f.split(":")[0] for f in figs] == [f"Figure A-{n}" for n in range(1, 15)]
    assert "Figure A-5: Normalized Load-Displacement Curve for Analysis of Service Limit State" \
        in figs


def test_appendix_a_lists_and_tolerance_read_from_the_page():
    text = _appendix_text(19)
    assert "Csm = 0.075" in text and "Site Class: D (stiff soils)\n" in text
    # the ± is a + with an underline in the print, p. A-6
    assert "agreement to within ± 20 percent" in text


# ---------------------------------------------------------------- Appendix B

B_TITLES = {
    # printed headings, pp. B-1 to B-11
    "B": "Drilled Shafts in Challenging Geomaterials",
    "B.1": "Argillaceous Sedimentary Rock",
    "B.2": "Limestone and Other Carbonate Rocks",
    "B.3": "Glacial Till",
    "B.4": "Piedmont Residual Soils",
    "B.5": "Cemented Soils",
    "B.6": "Expansive Soils",
    "B.7": "Summary",
}


def test_appendix_b_sections_and_titles():
    data = _appendix(20)
    assert data["chapter_title"] == "Appendix B: Drilled Shafts in Challenging Geomaterials"
    assert {s["section_id"]: s["title"] for s in data["sections"]} == B_TITLES
    pages = [int(p) for s in data["sections"]
             for p in re.findall(r"\[p\. B-(\d+)\]", s["body"])]
    assert pages[0] == 1 and pages[-1] == 11 and pages == sorted(pages)


@pytest.mark.parametrize("sid,printed", [
    # p. B-1: TCP hammer
    ("B.1", "the TCP test should be performed using a special 170 lb drop hammer with 24-inch "
            "drop height (Texas DOT, 2018)"),
    # p. B-2: the Colorado SPT limit, italic N printed as a plain letter
    ("B.1", "as long as the number of blows required to penetrate six inches is 50 or less "
            "(corresponding to N < 100)"),
    # p. B-2: Florida pullout test
    ("B.2", "a grout plug is formed in a 5.5-inch diameter cored hole at the bottom of a "
            "6.5-inch diameter hole"),
    # p. B-4: PMT modulus against triaxial
    ("B.3", "modulus values from PMT were 2.6 to 6 times those obtained from triaxial tests"),
    # p. B-8: caliche side resistance
    ("B.5", "unit side resistances in the range of 30 to 55 ksf in competent caliche layers, "
            "compared to 8 to 22 ksf in uncemented dense sand and gravel, and 4 ksf in stiff "
            "clay layers (Gura et al., 2007)"),
    ("B.5", "a range of 576 ksf to 1,440 ksf (4,000 to 10,000 psi)"),
    # p. B-8: force kept
    ("B.5", "If so, soil strength should be evaluated for the uncemented state."),
    # p. B-10: the parenthesis is empty in the print
    ("B.6", "the full strength of the soil can be mobilized (i.e., ) (as printed"),
])
def test_appendix_b_printed_sentences(sid, printed):
    assert printed in _section(sid)["body"]


def test_appendix_b_page_breaks_join_sentences():
    # a sentence running over a page is one paragraph with the marker inside
    assert "the compressive strength of [p. B-2] upper Cretaceous formation clay shales" \
        in _section("B.1")["body"]
    assert "(3) the Southwest, and (4) the Great Plains" in _section("B.6")["body"]


def test_appendix_b_tables():
    t1 = _section("B.5")["tables"]
    assert len(t1) == 1 and t1[0].startswith("Table B-1: Example Classification")
    assert "fresh caliche; very hard; 700; 70;" in t1[0]
    assert "weathered caliche; hard; 6 to 30; 3 to 6;" in t1[0]
    t2 = _section("B.6")["tables"]
    assert len(t2) == 1 and t2[0].startswith("Table B-2: Method of Identifying")
    for row in ("< 50; < 25; < 1.5; < 0.5; low", "50 – 60; 25 - 35; 1.5 – 4.0; 0.5 – 1.5; marginal",
                "> 60; > 35; > 4.0; > 1.5; high"):
        assert row in t2[0]


def test_appendix_b_figures():
    figs = [f for s in _appendix(20)["sections"] for f in s["figures"]]
    assert [f.split(":")[0] for f in figs] == [f"Figure B-{n}" for n in range(1, 6)]
    assert "Figure B-2: Features of Karstic Terrane (Knott et al., 1993)" in figs


# ---------------------------------------------------------------- Appendix C

C_IDS = ["C", "C.1", "C.2", "C.3", "C.3.1", "C.3.1.a", "C.3.2"]


def test_appendix_c_sections_and_titles():
    data = _appendix(21)
    assert data["chapter_title"] == "Appendix C: Analysis of Axial Load-Deformation Response"
    assert [s["section_id"] for s in data["sections"]] == C_IDS
    titles = {s["section_id"]: s["title"] for s in data["sections"]}
    # printed headings, pp. C-1, C-2, C-6 and C-10
    assert titles["C.1"] == "Simple Formulas"
    assert titles["C.2"] == "Numerical Simulation of Load Transfer"
    assert titles["C.3"] == "Approximate Closed-Form Solutions"
    assert titles["C.3.1"] == "Rock Sockets (Kulhawy and Carter 1992)"
    assert titles["C.3.1.a"].startswith("Rock Sockets (Kulhawy and Carter 1992) (continued, ")
    assert "The letter is not printed" in _section("C.3.1.a")["applicability"]
    assert titles["C.3.2"] == "Dense Residual Piedmont Soils (Mayne and Harris 1993)"
    # p. C-11 holds only Figure C-6
    pages = [int(p) for s in data["sections"]
             for p in re.findall(r"\[p\. C-(\d+)\]", s["body"])]
    assert pages == sorted(pages) and pages[0] == 1 and pages[-1] == 13
    assert set(pages) == set(range(1, 14)) - {11}


def test_appendix_c_numbered_equations_all_held_once():
    data = _appendix(21)
    ids = [e["id"] for s in data["sections"] for e in s["equations"]]
    assert ids == [f"Eq. C-{n}" for n in range(1, 43)]
    body = " ".join(s["body"] for s in data["sections"])
    for n in range(1, 43):
        assert body.count(f"(C-{n})") == 1


@pytest.mark.parametrize("sid,eq,formula", [
    # typed from renders of pp. C-1 to C-13 (PDF 630 to 642)
    ("C.1", "Eq. C-1", "wT = wc + wbb + wbs"),
    ("C.1", "Eq. C-2", "wc = (Qh - 0.5 Qms) L / (AE)shaft"),
    ("C.1", "Eq. C-4", "wbb = Cp (Qmb / (B qmax))"),
    ("C.1", "Eq. C-5", "wbs = (0.93 + 0.16 √(L/B)) Cp (Qms / (L qmax))"),
    ("C.2", "Eq. C-6", "EA d²z/dy² = πBt"),
    ("C.3.1", "Eq. C-10", "(μL)² = (2/(ζλ)) (2L/B)²"),
    ("C.3.1", "Eq. C-11", "ζ = ln [5(1 - νr)L/B]"),
    ("C.3.1.a", "Eq. C-22", "λ1,2 = [-β ± (β² + 4α)^(1/2)] / (2α)"),
    ("C.3.1.a", "Eq. C-26", "a2 = [(1 - νc)(Er/Ec) + (1 + νr)] (1/(2 tan φ tan ψ))"),
    ("C.3.1.a", "Eq. C-31", "c/pa = 0.1 (qu/pa)^(2/3)"),
    ("C.3.1.a", "Eq. C-32", "tan φ tan ψ = 0.001 (qu/pa)^(2/3)"),
    ("C.3.2", "Eq. C-33", "Es/pa = 22 (N60)^0.82"),
    ("C.3.2", "Eq. C-36", "μL = (L/B) 2 √(2/(ζ λ))"),
    ("C.3.2", "Eq. C-39", "ξ = EsL/Eb = 2.5"),
    ("C.3.2", "Eq. C-41", "RN = fSN (πBL) + qBN (πB²/4)"),
])
def test_appendix_c_equations_typed_from_the_page(sid, eq, formula):
    eqs = {e["id"]: e for e in _section(sid)["equations"]}
    assert eqs[eq]["formula"] == formula
    assert eqs[eq]["implemented_in"] is None
    assert formula in _section(sid)["body"]


def test_appendix_c_table_c1():
    t = _section("C.1")["tables"]
    assert len(t) == 1 and t[0].startswith("Table C-1: Values of Cp")
    for row in ("Sand (dense to loose); 0.09 – 0.18", "Clay (stiff to soft); 0.03 – 0.06",
                "Silt (dense to loose); 0.09 – 0.12"):
        assert row in t[0]


def test_appendix_c_print_slips_kept_and_noted():
    # p. C-7: no parenthesis closes in Eqs. C-13 and C-15
    assert "Gr = Er / [2(1 + νr] = elastic shear modulus of rock mass (C-13) (as printed" \
        in _section("C.3.1")["body"]
    a = _section("C.3.1.a")["body"]
    # p. C-9: the point (QC1, wC1) is drawn in Figure C-5b
    assert "in Figure C-3b (as printed; the point (QC1, wC1) is drawn in Figure C-5b)" in a
    # p. C-10 against Figure C-6 (p. C-11)
    assert "Illustrative Example 19-4 Chapter 10) (as printed; the caption of Figure C-6 " \
           "cites Illustrative Example 10-4)" in a
    assert "was 1,751 kips (as printed; the spreadsheet of Figure C-6 is for a complete socket " \
           "with B = 6 ft (72 in), D = 10 ft (120 in)" in a
    # p. C-13: QT and QT1 in Eq. C-42
    assert "Δw = (QT - QT1) (1 - ν²) / (Eb B) (C-42) (as printed" in _section("C.3.2")["body"]


def test_appendix_c_printed_sentences_keep_their_force():
    assert "To be valid, closed form solutions should be verified by reasonable agreement" \
        in _section("C.3")["body"]
    assert "Rock mass modulus and its variation with depth must, therefore, be assessed " \
           "carefully" in _section("C.3.1.a")["body"]
    assert "was recommended for dense cohesionless soils with N-values greater than 50" \
        in _section("C.3.2")["body"]
    assert "reasonable results for diameters up to 5 ft" in _section("C.3.2")["body"]


def test_appendix_c_figures():
    figs = {s["section_id"]: [f.split(":")[0] for f in s["figures"]]
            for s in _appendix(21)["sections"]}
    assert figs["C.2"] == ["Figure C-1", "Figure C-2", "Figure C-3", "Figure C-4"]
    assert figs["C.3.1"] == ["Figure C-5"]
    assert figs["C.3.1.a"] == ["Figure C-6"]
    assert figs["C.3.2"] == ["Figure C-7"]


@pytest.mark.parametrize("ch", [19, 20, 21])
def test_appendix_sections_fit_the_tools(ch):
    for s in _appendix(ch)["sections"]:
        assert len(s["body"]) <= 12000
        assert len(json.dumps(s)) <= 14000
