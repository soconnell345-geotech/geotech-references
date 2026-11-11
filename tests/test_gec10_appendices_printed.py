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


def test_appendix_sections_fit_the_tools():
    for s in _appendix(19)["sections"]:
        assert len(s["body"]) <= 12000
        assert len(json.dumps(s)) <= 14000
