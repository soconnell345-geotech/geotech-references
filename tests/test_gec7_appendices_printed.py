"""GEC-7 (FHWA-NHI-14-007, 2015) Appendices B and C pinned to the print.

REF-85 (app backlog): the library held GEC-7's ten chapters but not its
appendices, so the preliminary design charts' procedure and the design
example could not be searched or quoted. Appendix B (charts for preliminary
design, pp. 295 to 300) is chapter 12 and Appendix C (design example, pp.
301 to 317) chapter 13, in the print's own wording with [p. 301] markers;
every equation, calculation line and table is typed in from a rendered page
(the text layer carries the example's equations as scattered glyphs and
spoken words). Where the print disagrees with itself the stored text keeps
the print and says so "(as printed; ...)". Appendix A is chapter 11, pinned
in tests/test_gec7_appendix_a_printed.py.
"""

import json
import re

import pytest

from geotech_references._retrieval import load_chapter, retrieve_section
from geotech_references.gec_7 import tables


def _section(sid):
    return retrieve_section("gec_7", sid)


def _appendix(ch):
    return load_chapter("gec_7", ch)


def _all_text(ch):
    out = []
    for s in _appendix(ch)["sections"]:
        eqs = [json.dumps(e, ensure_ascii=False) for e in s["equations"]]
        out += [s["body"]] + s["tables"] + s["figures"] + eqs
    return " ".join(out)


def _scatter_free(body):
    """The patterns a text-layer formula leaves when it scatters."""
    assert not re.search(r"(^|\s)[′']($|\s)|\(['′]\)", body)          # a detached prime
    assert not re.search(r"(?m)^\d\s*$", body)                         # a lone digit line
    for a, b in ("()", "[]"):
        assert body.count(a) == body.count(b)                          # unbalanced brackets
    paras = [p for p in body.split("\n\n") if len(p) > 40]
    assert all(x != y for x, y in zip(paras, paras[1:]))               # a repeated paragraph
    for spoken in (" sub ", "as previously described", "fraction", "squared"):
        assert spoken not in body


B_EQS = {
    "Eq. B.1": "μ = qU DDH / (FSPO γs SH SV)",
    "Eq. B.2": "L/H (corrected) = C1L × C2L × C3L × L/H (from charts)",
    "Eq. B.3": "C1L = 1.50 - 0.15 DDH + 0.0065 DDH²",
    "Eq. B.4": "C2L = -4.0 c* + 1.09 ≥ 0.85",
    "Eq. B.5": "C3L = 0.52 FSOS + 0.30 ≥ 1.0",
    "Eq. B.6": "tmax (corrected) = C1F × C2F × tmax (from charts)",
    "Eq. B.7": "C1F = -0.3 + 0.4 DDH - 0.017 DDH²",
    "Eq. B.8": "C2F = -4.0 c* + 1.09 ≥ 0.85",
}

C_IDS = ["C", "C.1", "C.2", "C.3", "C.3.a", "C.3.b", "C.4", "C.4.a", "C.4.e", "C.4.f", "C.5",
         "C.6", "C.6.a", "C.6.b", "C.6.c", "C.7", "C.7.a", "C.7.b", "C.7.c", "C.7.d", "C.7.e",
         "C.7.f", "C.7.g", "C.8", "C.8.a", "C.8.b"]


# ---------------------------------------------------------------- Appendix B

def test_appendix_b_chapter_and_section():
    data = _appendix(12)
    assert data["chapter_title"] == "Appendix B: Charts for Preliminary Design"
    assert data["reference_id"] == "FHWA-NHI-14-007"
    assert [s["section_id"] for s in data["sections"]] == ["B"]
    body = _section("B")["body"]
    # pp. 298 to 300 hold only the charts
    assert re.findall(r"\[p\. (\d+)\]", body) == ["295", "296", "297"]
    _scatter_free(body)


@pytest.mark.parametrize("printed", [
    # p. 295
    "However, the charts should not replace the use of soil nail design computer programs for "
    "more complex conditions and for other drastically different conditions.",
    "• normalized cohesion, c* = c′/γs H = 0.02",
    "• factor of safety for overall stability, FSOS = 1.35",
    "• drill hole diameter, DDH = 4 in.",
    # p. 296
    "• Factor of safety for pullout (FSPO, usually 2.0).",
    "Interpolate between φs = 27, 31, 35 or 39 degrees as needed.",
    "Note that only sufficiently high values of φs will achieve the selected FSOS for relatively "
    "large values of β.",
    "8. Calculate the soil nail maximum force (Tmax) by multiplying tmax read from the chart by "
    "γs, H, SV and SH.",
])
def test_appendix_b_printed_sentences(printed):
    assert printed in _section("B")["body"]


def test_appendix_b_equations_typed_from_the_page():
    # pp. 296 and 297 (PDF 336, 337), 200 dpi renders
    eqs = _section("B")["equations"]
    assert [e["id"] for e in eqs] == list(B_EQS)
    body = _section("B")["body"]
    for e in eqs:
        assert e["formula"] == B_EQS[e["id"]]
        assert e["implemented_in"] is None
        assert body.count(e["formula"] + " (Equation B." + e["id"][-1] + ":") == 1
    # the corrections are 1 for the charts' assumptions (DDH = 4 in., c* = 0.02,
    # FSOS = 1.35), within the print's rounding, except C1F = 1.028
    assert abs(1.50 - 0.15 * 4 + 0.0065 * 16 - 1.0) < 0.01
    assert abs(-4.0 * 0.02 + 1.09 - 1.0) < 0.02
    assert abs(0.52 * 1.35 + 0.30 - 1.0) < 0.01
    assert round(-0.3 + 0.4 * 4 - 0.017 * 16, 3) == 1.028
    assert "(\"correction correction\" as printed)" in body


def test_appendix_b_figures():
    figs = _section("B")["figures"]
    assert figs == [
        "Figure B.1: Illustration. Conditions for calculations with charts",
        "Figure B.2: Chart. Batter = 0 deg. - Backslope 0 deg",
        "Figure B.3: Chart. Batter = 0 deg. - Backslope 10 deg",
        "Figure B.4: Chart. Batter = 0 deg. - Backslope 30 deg",
    ]


# ---------------------------------------------------------------- Appendix C

def test_appendix_c_sections_and_titles():
    data = _appendix(13)
    assert data["chapter_title"] == "Appendix C: Design Example"
    assert [s["section_id"] for s in data["sections"]] == C_IDS
    titles = {s["section_id"]: s["title"] for s in data["sections"]}
    # printed headings, pp. 301 to 317
    assert titles["C"] == "Overview"
    assert titles["C.2"] == ("Step 2: Subsurface Exploration and Development of Parameters "
                             "for Design")
    assert titles["C.4.a"] == "Develop Wall Layout, Cross-Sections, Nail Pattern, and Splaying"
    assert "Printed 4.a/b/c/d" in _section("C.4.a")["applicability"]
    assert titles["C.7.d"] == "Verify Facing Bending/Flexure Resistance"
    assert titles["C.8.b"] == "Evaluate Lateral Squeeze (if applicable)"
    # the step headings print no text of their own
    for sid in ("C.3", "C.4", "C.6", "C.7", "C.8"):
        assert _section(sid)["body"] == ""
    pages = [int(p) for s in data["sections"] for p in re.findall(r"\[p\. (\d+)\]", s["body"])]
    assert pages == sorted(pages) and set(pages) == set(range(301, 318))
    for s in data["sections"]:
        _scatter_free(s["body"])


@pytest.mark.parametrize("sid,printed", [
    ("C.2", "• bond strength, qU = 14.5 psi"),
    ("C.2", "the Owner prefers to specify a Class B corrosion protection, consisting of epoxy "
            "coating or galvanizing over steel bars."),
    ("C.3.a", "It is assumed that the live load consists of a uniform load, QLS equal to 150 psf, "
              "extending from the wall to 25 ft behind the wall."),
    ("C.4.a", "However, the reader is reminded that the lowermost rows of nails should be ideally "
              "shorter than the upper rows"),
    ("C.4.e", "Therefore, the available space for grout cover is 0.5 × (6.0 - 0.99) = 2.50 in., "
              "not accounting for couplers."),
    ("C.6.a", "Mean values of the soil resistance should be considered."),
    ("C.6.a", "The wall-soil interface friction is estimated to be 2/3 φs′ in SNAP-2."),
    ("C.6.a", "After a few trial runs, the length of the nails was modified to L = 18 ft"),
    ("C.6.a", "The soil nail lengths were selected, from the top down, as L = 25, 21, 19, 15, 13 "
              "ft. The following was calculated: FSOS =1.50, Tmax = 15.9 kip, and minimum nail "
              "load 10.2 kip."),
    ("C.7.f", "The verifications indicate that for all strength limit states, the existing "
              "factored resistances are greater than the factored loads."),
])
def test_appendix_c_printed_sentences(sid, printed):
    assert printed in _section(sid)["body"]


@pytest.mark.parametrize("sid,line", [
    # every formula line read from a 200 dpi render, pp. 303 to 317
    ("C.4.a", "• Adopt SH = SV = 5 ft; Check: SH × SV = 25 ft² ≤ 36 to 42 ft²"),
    ("C.4.a", "• L = 0.7 H = 17.5 ft; ok (L between 0.6 H and 1.2H)"),
    ("C.6.a", "The nail head force at this nail is estimated as To = 0.7 × 24.7 = 17.3 kip."),
    ("C.7.a", "RPO = rPO LP = π qU DDH LP"),
    ("C.7.a", "RPO = π × 14.5 × 144 × 0.5 × 15.6/1000 = 51.2 kip"),
    ("C.7.a", "CDR = φPO RPO / (γ Tmax) ≥ 1.0"),
    ("C.7.a", "CDR = (0.65 × 51.2) / (1.35 × 24.7) = 1.0; ok"),
    ("C.7.c", "RT = At fy"),
    ("C.7.c", "RT = 0.60 × 75 = 45 kip"),
    ("C.7.c", "CDR = (0.75 × 45) / (1.35 × 24.7) = 1.01 > 1.0; ok"),
    ("C.7.d", "RFF [kip] = 3.8 × CF × fy [ksi] × F"),
    ("C.7.d", "F = (avn + avm) [in²/ft] x hi [ft]"),
    ("C.7.d", "avn = avm + AVN / SH"),
    ("C.7.d", "avn = 0.058 + 0.62/5 = 0.18 in.²/ft"),
    ("C.7.d", "RFF = 3.8 × 2 × 60 × 0.079 = 36 kip"),
    ("C.7.d", "ρTOT (%) = [(avn + avm) / (12 (hi/2))] × 100 = (0.058 + 0.18)/ (12 × 2) × 100 = "
              "0.99%"),
    ("C.7.d", "ρmin [%] = 0.24 √(f′c [psi]) / fy [ksi] = 0.24 √4,000 / 60 = 0.25 %"),
    ("C.7.d", "ρmax [%] = 0.05 (f′c [psi] / fy [ksi]) (90 / (90 + fy [ksi])) = 0.05 (4,000/60) "
              "(90/(90 + 60)) = 2 %"),
    ("C.7.d", "RFF = 3.8 × 1 × 60 × 2 × 0.20 × (8/12) = 60.8 kip"),
    ("C.7.d", "CDR = (0.90 × 60.8) / (1.35 × 17.3) = 2.34 > 1.0; ok"),
    ("C.7.e", "VF [kip] = 0.58 √(f′c [psi]) π D′c [ft] hi [ft]"),
    ("C.7.e", "VF = 0.58 √4000 π × ((9 + 4)/12) × (4/12) = 41.6 kip"),
    ("C.7.e", "RFP = CP VF"),
    ("C.7.e", "hc = LS + tP – tSH = 4.125 + 1 - 0.31 = 4.8 in."),
    ("C.7.e", "D'c = min (6 + 4.8, 2 × 4.8) = min (10.8, 9.6) = 9.6 in."),
    ("C.7.e", "VF = 0.58 √4000 π (9.6/12) (4.8/12) = 36.9 kip"),
    ("C.7.e", "CDR = (0.90 × 36.9) / (1.35 × 17.3) = 1.42 > 1.0; ok"),
    ("C.7.f", "RFH = N AS fy = 4 × (π DSC²/4) × 60 = 4 × (π 0.5²/4) × 60 = 47.1 kips."),
    ("C.8.a", "δh = δv = H / 500 = 25 × 12 /500 = 0.6 in."),
])
def test_appendix_c_calculation_lines(sid, line):
    assert line in _section(sid)["body"]


def test_appendix_c_printed_results_recompute():
    # the printed results the notes do not mark, recomputed from their lines
    from math import pi, sqrt
    assert round(pi * 14.5 * 144 * 0.5 * 15.6 / 1000, 1) == 51.2
    assert round(0.65 * 51.2 / (1.35 * 24.7), 1) == 1.0
    assert round(0.75 * 45 / (1.35 * 24.7), 2) == 1.01
    assert round(3.8 * 2 * 60 * 0.079) == 36
    assert round((0.058 + 0.18) / 24 * 100, 2) == 0.99
    assert round(0.90 * 36 / (1.35 * 17.3), 2) == 1.39
    assert round(3.8 * 60 * 2 * 0.20 * 8 / 12, 1) == 60.8
    assert round(0.90 * 60.8 / (1.35 * 17.3), 2) == 2.34
    assert round(0.58 * sqrt(4000) * pi * 13 / 12 * 4 / 12, 1) == 41.6
    assert round(0.58 * sqrt(4000) * pi * 9.6 / 12 * 4.8 / 12, 1) == 36.9
    assert round(0.90 * 36.9 / (1.35 * 17.3), 2) == 1.42
    assert round(4 * pi * 0.5 ** 2 / 4 * 60, 1) == 47.1
    # Table C.5: Lfail + Lp = L = 18 ft for every nail
    for lf, lp in ((16.1, 1.9), (13.6, 4.4), (10.4, 7.6), (6.4, 11.6), (2.4, 15.6)):
        assert round(lf + lp, 1) == 18.0


def test_appendix_c_print_slips_kept_and_noted():
    # p. 308: 1/1.51 = 0.66
    assert "φOS = 1/ FSOS = 1/1.51 ~ 0.60; ok (matches value of Table C.2 for static loads) " \
           "(as printed; 1/1.51 = 0.66, and Table C.2 gives φOS = 0.65)" in _section("C.6.a")["body"]
    assert round(1 / 1.51, 2) == 0.66
    # p. 315: 0.90 x 41.6 / (1.35 x 17.3) = 1.60
    assert "= 1.58 > 1.0; ok (as printed; 0.90 × 41.6 / (1.35 × 17.3) = 1.60)" \
        in _section("C.7.e")["body"]
    assert round(0.90 * 41.6 / (1.35 * 17.3), 2) == 1.60
    # pp. 316 and 317: RFS in the CDR line, and 0.70 x 47.1 / (1.35 x 17.3) = 1.41
    f = _section("C.7.f")["body"]
    assert "CDR = φFH RFS / (γ To) ≥ 1.0 (as printed; RFS here, RFH in the line above)" in f
    assert "= 1.42 > 1.0; ok (as printed; 0.70 × 47.1 / (1.35 × 17.3) = 1.41)" in f
    assert round(0.70 * 47.1 / (1.35 * 17.3), 2) == 1.41


def test_appendix_c_ddef_against_table_5_12():
    # p. 317 works DDEF with C = 0.8 for sandy soil; Table 5.12 (p. 141) prints
    # C = 1.25 for sandy soil and 0.8 for weathered rock and stiff soil
    body = _section("C.8.a")["body"]
    assert "DDEF = C H (1- tan α) = 0.8 H = 20 ft (as printed; Table 5.12, p. 141, gives " \
           "C = 1.25 for sandy soil, for which 1.25 H = 31.25 ft" in body
    # the note names what the coded lookup returns, so the example does not lead to 0.8
    assert "and C = 0.8 for weathered rock and stiff soil; the coded " \
           "table_5_12_wall_displacement(\"sandy_soil\") returns the table's 1.25)" in body
    sandy = tables.table_5_12_wall_displacement("sandy_soil")
    assert sandy["C"] == 1.25
    assert tables.table_5_12_wall_displacement("weathered_rock_stiff_soil")["C"] == 0.8
    # the example's H/500 for sandy soil agrees with the lookup
    assert sandy["delta_h_over_H"] == pytest.approx(1 / 500)
    # p. 317 cites Figure 5.15 (p. 138, the facing's bending section); p. 141 names
    # Figure 5.16 (p. 142, deformation of soil nail walls) for DDEF
    assert "estimated as (Figure 5.15) (as printed; Figure 5.15, p. 138, is the section showing " \
           "the bending mechanism in the initial facing; DDEF is drawn in Figure 5.16, p. 142, " \
           "the figure p. 141 names for it):" in body
    assert round(25 * 12 * sandy["delta_h_over_H"], 1) == 0.6


@pytest.mark.parametrize("table,cells", [
    ("C.1", ["Overall Stability; Internal; FSOS; FS; 1.5",
             "Strength – Facing; A307 steel bolt (assumed); FSFH; HT-FoS; 2.0"]),
    ("C.2", ["Overall Stability; Wall is permanent and critical; φOS; 0.65",
             "Nail in Tension; Grade 75; φT; 0.75",
             "Facing Headed Stud Tensile; A307 steel bolt; φFH; 0.70"]),
    ("C.3", ["Headed stud type; 4 × (1/2 × 4 1/8); Grade A307 steel",
             "head thickness: tSH = 0.31 in."]),
    ("C.4", ["5; 1.24; Temporary; 4 upper rows installed, 5th lift exposed",
             "7; 1.51; Final; 5 rows installed, with surcharge"]),
    ("C.5", ["5; 24.7; Tensile; 2.4; 15.6", "1; 3.2; Pullout; 16.1; 1.9"]),
])
def test_appendix_c_tables_typed_from_the_page(table, cells):
    rows = [(s["section_id"], t) for s in _appendix(13)["sections"] for t in s["tables"]
            if t.startswith(f"Table {table}:")]
    assert len(rows) == 1
    sid, text = rows[0]
    for cell in cells:
        assert cell in text
    assert f"[Table {table}]" in _section(sid)["body"]


def test_appendix_c_lookups_agree_with_tables_c1_c2():
    # Table C.2 (p. 305) against the coded Tables 5.4 to 5.11
    for state, phi in (("overall_stability", 0.65), ("pullout", 0.65),
                       ("tendon_grade_60_75", 0.75), ("facing_flexure", 0.90),
                       ("facing_punching_shear", 0.90), ("headed_stud_a307", 0.70)):
        assert tables.table_5_resistance_factors(state)["static"] == phi
    # Table C.1 (p. 305) against the coded Table 5.1
    for state, fs in (("overall_stability", 1.5), ("pullout_resistance", 2.0),
                      ("tendon_tensile_grade_60_75", 1.8), ("facing_flexure", 1.5),
                      ("facing_punching_shear", 1.5), ("headed_stud_a307", 2.0)):
        assert tables.table_5_1_factors_of_safety(state)["fs_static"] == fs


def test_appendix_c_figures():
    figs = {s["section_id"]: [f.split(":")[0] for f in s["figures"]]
            for s in _appendix(13)["sections"] if s["figures"]}
    assert figs == {"C.1": ["Figure C.1"], "C.6.a": ["Figure C.2", "Figure C.3"]}


@pytest.mark.parametrize("ch", [12, 13])
def test_appendix_sections_fit_the_tools(ch):
    for s in _appendix(ch)["sections"]:
        assert len(s["body"]) <= 12000
        assert len(json.dumps(s)) <= 14000
