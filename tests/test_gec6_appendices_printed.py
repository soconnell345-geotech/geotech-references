"""GEC-6 (FHWA-SA-02-054, 2002) Appendices B and C pinned to the print.

REF-85 (app backlog): the library held GEC-6's ten chapters and none of its
appendices, so the five spread footing design examples could not be searched
or quoted. Appendix B (Design Examples, pp. B-1 to B-90) is chapter 12, in the
print's own wording with [p. B-1] markers: the introduction is "B", EXAMPLE n
is "B.n" and its Step k "B.n.k" (Step 11a "B.n.11.a"). Appendix C (Load and
Resistance Factor Design, pp. C-1 to C-48) is chapter 13: its opening text is
"C", Sections C.1 to C.6 keep their printed numbers (the first of the two
printed C.4.1, under C.3, is stored as C.3.2), LRFD EXAMPLE C1 is "C-1" (the
appendix's own name for it) with Step k "C-1.k", and LRFD EXAMPLE 2 (Example
C-2) is "C-2" with Step 12a "C-2.12.a". Every calculation line and table is typed in from 200 dpi renders
(the text layer scatters the equation-editor objects). Where the print
disagrees with itself the stored text keeps the print and says so "(as
printed; ...)". Chapter 11 is left for Appendix A.
"""

import json
import re
from math import log10, sqrt, tan, radians

import pytest

from geotech_references._retrieval import load_chapter, retrieve_section
from geotech_references.gec_6 import figures, tables


def _section(sid):
    return retrieve_section("gec_6", sid)


def _appendix():
    return load_chapter("gec_6", 12)


STEPS = {
    1: ["5", "6", "7", "8", "9", "10", "11", "12"],
    2: ["5", "6", "7", "8", "9", "10", "11", "12"],
    3: ["5", "6", "7", "8", "9", "10", "11.a", "11.b", "11.c", "12"],
    4: ["5", "6", "7", "8", "9", "10.a", "11.a", "10.b", "11.b", "10.c", "11.c", "12"],
    5: ["5", "6", "7", "8", "9", "10", "11", "12"],
}


def test_chapter_and_sections():
    data = _appendix()
    assert data["chapter_title"] == "Appendix B: Design Examples"
    assert data["reference_id"] == "FHWA-SA-02-054"
    want = ["B"]
    for n, steps in STEPS.items():
        want += [f"B.{n}"] + [f"B.{n}.{k}" for k in steps]
    assert [s["section_id"] for s in data["sections"]] == want
    marks = [m for s in data["sections"] for m in re.findall(r"\[p\. ([^\]]+)\]", s["body"])]
    assert marks[0] == "B-1" and marks[-1] == "B-90"
    for s in data["sections"]:
        assert len(s["body"]) <= 12000 and len(json.dumps(s)) <= 14000, s["section_id"]
        assert not re.search(r"(?m)^\d\s*$", s["body"])                 # a lone digit line
        assert not re.search(r"(?<![\d,])\.\d\d? [\d.]", s["body"])     # reversed digits
        assert not re.search(r"kN/m3\b|\bm2\b", s["body"])               # a lost superscript


@pytest.mark.parametrize("sid,title", [
    ("B", "Introduction"),
    ("B.1", "Example 1: Interior Bridge Pier on Spread Footing"),
    ("B.2.7", "Example 2, Step 7 – Calculate allowable bearing capacity"),
    ("B.3.11.a", "Example 3, Step 11a – Check overturning (eccentricity), bearing pressure and "
                 "sliding under full loading without PDW and PLL"),
    ("B.4.10.b", "Example 4, Step 10b – Size the footing"),
    ("B.5", "Example 5: Interior Bridge Pier on In-Situ Rock"),
])
def test_titles(sid, title):
    assert _section(sid)["title"] == title


def test_figures_and_tables_listed_where_first_named():
    secs = {s["section_id"]: s for s in _appendix()["sections"]}
    figs = {f.split(":")[0]: sid for sid, s in secs.items() for f in s["figures"]}
    assert len(figs) == 21
    assert figs["Figure B3-4"] == figs["Figure B3-5"] == "B.3.7"
    assert figs["Figure B4-5"] == figs["Figure B4-7"] == "B.4.10.a"
    assert "Figure B3-4: Summary Output of EMBANK Settlement Analysis (typed from the page: " \
           "height of fill H = 32.00 ft" in secs["B.3.7"]["figures"][0]
    tabs = {t.split(":")[0]: sid for sid, s in secs.items() for t in s["tables"]}
    assert len(tabs) == 18
    assert tabs["Table B4-3"] == "B.4.7" and tabs["Table B5-1"] == "B.5.5"


@pytest.mark.parametrize("sid,printed", [
    ("B", "The examples should not be construed as representations of the only approach that "
          "can lead to a satisfactory design."),
    ("B", "In practice, every complete design should consider all applicable load cases."),
    ("B.4.7", "Settlement will therefore limit the allowable bearing capacity for the design of "
              "this footing."),
    ("B.4.10.a", "AASHTO recommends using a minimum Ka of 0.3. However, because this material "
                 "will be a specified compacted select granular material, we will use the "
                 "calculated Ka value of 0.24 for design."),
    ("B.5.7", "In general practice, settlement is not checked for Group VII loads because seismic "
              "loads are transient and temporary in nature."),
    ("B.5.10", "Typically, the minimum footing width should be at least 3 column diameters "
               "[p. B-89] [i.e., 3(0.6 m) = 1.8 m] to provide the required development length"),
])
def test_printed_sentences(sid, printed):
    assert printed in _section(sid)["body"]


@pytest.mark.parametrize("sid,line", [
    # read from 200 dpi renders
    ("B.1.5", "PI = γ [βD(D) + βL (L)] = 1.0 [1.0 (6400 kN) + 1.0 (1670 kN)] = 8070 kN"),
    ("B.1.7", "qult = 45.1 kPa (33.3)(1.0)(1.7)(1.0)(1.0) + 0.5 (19.6 kN/m³)(Bf)(48.0)(0.9)(0.6)"
              "(1.0)"),
    ("B.1.7", "ΔH2 = 2.1 m (1/65) log[(65.7 kPa + 0.55(240 kPa))/65.7 kPa]"),
    ("B.2.7", "Nγq = 17 + (0.69)(80 - 17) ≅ 60"),
    ("B.3.5", "PA = (0.5)Ka γ Habut² = (0.5)(0.26)(19.6 kN/m³)(5.24)² = 69.96 kN/m"),
    ("B.3.11.b", "Mtoe girders = (7274 + 620 + 2138 - 3392) kN·m / Lf = 6640 kN·m / 25 m = "
                 "265.6 kN·m/m"),
    ("B.3.11.c", "Mtoe abut = 315.3 kN·m/m + 41.97 kN·m/m = 357.3 kN·m/m"),
    ("B.4.7", "CWγ = 0.5 + 0.5(4.5 / (1.5(6) + 1.5)) = 0.7"),
    ("B.4.7", "qall = 479 + 178Bf kPa"),
    ("B.4.7", "δv = (1.83)(159 kPa)(10 m)(1 - 0.14²) / (0.53)(9800000 kPa) = 0.0005 m = 0.5 mm"),
    ("B.4.10.b", "armstem = ((5.2 m/3)(8.5 m - 0.9 m - 1.8 m)(1 m) + [(5.2 m/3) + 0.25 m](1.8 m)"
                 "(0.5 m)) / ((8.5 m - 0.9 m)(1 m) - (1.8 m)(0.5 m)) = 1.77 m"),
    ("B.4.10.b", "Mtoe = 2553 kN-m - 762 kN-m = 1791 kN-m"),
    ("B.4.11.c", "FSsliding = FR / Fsliding ≥ 1.5 (Eqn. 5-40) = 0.78(1013 kN/m) / 212 kN/m = "
                 "790 kN/m / 212 kN/m = 3.7"),
    ("B.5.10", "L′f = √(A′/0.3) = √(0.79 m²/0.3) = 1.62 m"),
    ("B.5.11", "FR = 0.7(Wftg + Wcover + Pv OT) = 0.7(228.4 kN + 37 kN + 4729 kN) = 3496 kN"),
])
def test_calculation_lines(sid, line):
    assert line in _section(sid)["body"]


def test_results_recompute():
    # Example 1
    assert 6400 + 1670 == 8070
    assert round(45.1 * 33.3 * 1.7) == 2553 and round(0.5 * 19.6 * 48.0 * 0.9 * 0.6) == 254
    assert round(2.1 / 65 * log10((65.7 + 0.55 * 240) / 65.7), 3) == 0.015
    # Example 3, Step 11b
    assert (7274 + 620 + 2138 - 3392) == 6640 and round(6640 / 25, 1) == 265.6
    assert round(0.5 * 0.26 * 19.6 * 5.24 ** 2, 2) == 69.96
    # Example 4
    assert round(0.5 + 0.5 * 4.5 / (1.5 * 6 + 1.5), 1) == 0.7
    assert round(29.4 * 48.9) == 1438 and round(0.5 * 19.6 * 78.0 * 0.7) == 535
    assert round(1438 / 3) == 479 and round(535 / 3) == 178
    assert round(1.83 * 159 * 10 * (1 - 0.14 ** 2) / (0.53 * 9.8e6), 4) == 0.0005
    arm = ((5.2 / 3) * 5.8 + (5.2 / 3 + 0.25) * 1.8 * 0.5) / (7.6 - 0.9)
    assert round(arm, 2) == 1.77
    assert round(157 * 1.77 + 110 * 2.6 + 442 * 3.72 + 14.5 * 0.62 + 227 * 1.48) == 2553
    assert round(170 * 2.83 + 41.9 * 6.7) == 762
    assert round(0.78 * 1013) == 790 and round(790 / 212, 1) == 3.7
    # Example 5
    assert round(8071 / 10200, 2) == 0.79 and round(sqrt(0.79 / 0.3), 2) == 1.62
    assert round(1.0 * 1.8 * 5.4 * 23.5, 1) == 228.4
    assert round(0.7 * (228.4 + 37 + 4729)) == 3496 and round(3496 / 971, 1) == 3.6
    assert round(tan(radians(35)), 2) == 0.70


@pytest.mark.parametrize("sid,note", [
    # p. B-6: the MY numbers take L alone
    ("B.1.5", "= 944.5 kN-m (as printed; the numbers take L alone, 196.5 kN-m, the impact load "
              "being neglected)"),
    # p. B-9: the ground water factors cited one equation number high
    ("B.1.7", "(Eqn. 5-10) (as printed; this is Eqn. 5-9, p. 56)"),
    ("B.1.7", "(Eqn. 5-11) (as printed; this is Eqn. 5-10, p. 56)"),
    ("B.1.7", "settlement (Section 5.2) (as printed; settlement estimation is Section 5.3)."),
    ("B.2.6", "= 164.1 kPa (as printed; the terms sum to 164.2 kPa)"),
    ("B.2.11", "qfooting = Pv/B′f = (425.52 kN/m)(2.28 m) (as printed; the value is 425.52 kN/m "
               "divided by 2.28 m)"),
    ("B.3.6", "= 280.7 kPa (as printed; the terms sum to 280.8 kPa)"),
    # Figure B3-4 (the EMBANK output) named for the allowable pressure of B3-5
    ("B.3.10", "From Figure B3-4 (as printed; the allowable bearing pressure is plotted in Figure "
               "B3-5), a bearing pressure of up to 230 kPa"),
    ("B.3.11.a", "ey = 0.53 m < Bf/6 = 2.7 m/6 = 0.45 m (No Good) (as printed; 0.53 m is greater "
                 "than 0.45 m)"),
    ("B.3.11.c", "= 179.4 kN/m (as printed; 0.78 × 229.6 = 179.1)"),
    ("B.4.7", "ΔH1a = 0.0160 m = 16 mm (as printed; the terms give 0.0159 m)"),
    ("B.4.7", "ν = 0.14 and EIR = 9.8 x 10⁶ kPa, from Tables 5-13 and 5-14 (as printed; Table "
              "5-13 gives shale a mean ν of 0.09, from 0.03 to 0.18)."),
    ("B.4.10.a", "= 338 kN (as printed; the terms give 337 kN)"),
    ("B.4.10.a", "Mtoe = 1787 kN-m - 236 kN-m = 1551 kN-m (as printed; the four terms sum to "
                 "1788 kN-m)"),
    ("B.4.10.c", "= 1013 kN (as printed; the terms sum to 1012 kN)"),
    ("B.4.10.c", "Mtoe = 2645 kN-m - 864 kN-m = 1781 kN-m (as printed; the positive terms sum to "
                 "2644 kN-m)"),
    ("B.4.10.c", "= 288 Pa (as printed, for kPa)"),
    ("B.4.11.c", "V (Table B3-2) (as printed; the shear load is given in Table B4-1):"),
    ("B.5.8", "Fsliding = (W + Pv)tan35° = 0.7(W + Pv) (as printed; this is the ultimate sliding "
              "resistance, FR in Step 11)"),
    ("B.5.10", "(1/4)Lf = (1/4)(4.3 m) = 1.01 m (as printed; (1/4)(4.3 m) = 1.075 m) < ez = "
               "1.33 m (not OK)"),
    ("B.5.10", "(as printed; Table 5-14 gives granite a mean EIR of 52.67 x 10⁶ kPa)."),
    ("B.5.10", "= 0.0003 m = 0.3 mm (as printed; the footing width found above is Bf = 1.8 m)"),
])
def test_print_slips_kept_and_noted(sid, note):
    assert note in _section(sid)["body"]


def test_print_slips_recompute():
    assert round(19.6 * 3.5 + 20.5 * 2.0 + 20.5 * 2.57 + 17.3 * 6.0 + 9.79 * 1.5, 1) == 280.8
    assert round(0.78 * 229.6, 1) == 179.1
    assert round(3 / 108 * log10((58.8 + 0.67 * 240) / 58.8), 4) == 0.0159
    assert round((5.2 * 2 / 3 - 0.5) * 5.8 * 19.6) == 337
    assert round(136 * 1.73 + 110 * 2.6 + 338 * 3.72 + 14.5 * 0.62) == 1788
    assert round(157 + 110 + 442 + 14.5 + 227 + 61.6) == 1012
    assert round(157 * 1.77 + 110 * 2.6 + 442 * 3.72 + 14.5 * 0.62 + 288.6 * 1.48) == 2644
    assert 4.3 / 4 == 1.075


# ------------------------------------------------- the coded lookups agree

def test_table_5_1_factors_the_examples_read():
    # p. B-9 (35 degrees) and p. B-67 (38 degrees)
    f35, f38 = (tables.table_5_1_bearing_capacity_factors(p) for p in (35, 38))
    assert (f35["Ngamma"], f35["Nq"]) == (48.0, 33.3)
    assert (f38["Ngamma"], f38["Nq"]) == (78.0, 48.9)


def test_rock_tables_the_examples_read():
    # p. B-86: sound granite 7.7 MPa from Table 5-7
    assert tables.table_5_7_presumptive_bearing_rock("granite")["recommended_mpa"] == 7.7
    # p. B-70 takes Cd = 1.83 for L/B = 5 (Table 5-12's average column), p. B-89
    # Cd = 1.78 for L/B = 3 (its center column)
    assert tables.table_5_12_shape_rigidity_factor("rectangle", "average", 5) == 1.83
    assert tables.table_5_12_shape_rigidity_factor("rectangle", "center", 3) == 1.78
    # p. B-89: granite nu = 0.2; p. B-70 shale E = 9.8 x 10^6 kPa (Table 5-14 mean 9.79 GPa)
    assert tables.table_5_13_poissons_ratio_rock("granite")["mean"] == 0.20
    assert tables.table_5_14_youngs_modulus_rock("shale")["mean_GPa"] == 9.79
    # the two the examples state otherwise, as noted in the text
    assert tables.table_5_13_poissons_ratio_rock("shale")["mean"] == 0.09
    assert tables.table_5_14_youngs_modulus_rock("granite")["mean_GPa"] == 52.67
    # p. B-87: delta = 35 degrees for concrete on rock (Table 5-15)
    assert tables.table_5_15_friction_factor("clean_sound_rock")["delta_min_deg"] == 35


@pytest.mark.parametrize("n_prime,soil,printed", [
    (24, "well graded fine to medium silty sand", 65),   # p. B-11
    (36, "well graded silty sand and gravel", 120),      # p. B-11
    (30, "well graded silty sand and gravel", 102),      # p. B-11
    (26, "clean uniform medium sand", 110),              # p. B-11
    (32, "well graded silty sand and gravel", 110),      # pp. B-28, B-48
    (32, "well graded silty sand and gravel", 108),      # p. B-69
    (35, "well graded silty sand and gravel", 115),      # p. B-69
    (10, "inorganic silt", 30),                          # p. B-48
    (15, "well graded fine to medium silty sand", 50),   # p. B-49
    (20, "well graded fine to medium silty sand", 58),   # p. B-49
])
def test_figure_5_19_within_two_of_the_examples_readings(n_prime, soil, printed):
    c = figures.figure_5_19_hough_bearing_capacity_index(n_prime, soil)
    assert abs(c - printed) <= 2.0


@pytest.mark.parametrize("n,ksf,printed", [
    (20, 1.4, 75), (24, 0.58, 95), (5.2, 0.54, 50), (22, 0.9, 85),   # pp. B-8, B-26, B-44, B-67
])
def test_figure_4_1_near_the_examples_about_values(n, ksf, printed):
    dr = figures.figure_4_1_relative_density_spt(n, ksf * 47.88)
    assert abs(dr - printed) <= 3.5


# ------------------------------------------------------------- Appendix C

C_STEPS = {
    "C-1": ["5", "6", "7", "8", "9", "10", "11", "12", "13", "14"],
    "C-2": ["5", "6", "7", "8", "9", "10", "11", "12.a", "12.b", "13", "14"],
}


def _appendix_c():
    return load_chapter("gec_6", 13)


def test_appendix_c_chapter_and_sections():
    data = _appendix_c()
    assert data["chapter_title"] == "Appendix C: Load and Resistance Factor Design"
    assert data["reference_id"] == "FHWA-SA-02-054"
    want = ["C", "C.1", "C.2", "C.3", "C.3.1", "C.3.2", "C.4", "C.4.1", "C.4.2", "C.4.3",
            "C.4.5", "C.5", "C.5.1", "C.5.2", "C.5.3", "C.5.4", "C.6"]
    for ex, steps in C_STEPS.items():
        want += [ex] + [f"{ex}.{k}" for k in steps]
    assert [s["section_id"] for s in data["sections"]] == want
    marks = [m for s in data["sections"] for m in re.findall(r"\[p\. ([^\]]+)\]", s["body"])]
    assert marks[0] == "C-1" and marks[-1] == "C-48"
    for s in data["sections"]:
        assert len(s["body"]) <= 12000 and len(json.dumps(s)) <= 14000, s["section_id"]
        assert not re.search(r"(?m)^\d\s*$", s["body"])
        assert not re.search(r"(?<![\d,])\.\d\d? [\d.]", s["body"])
        assert not re.search(r"kN/m3\b|\bm2\b", s["body"])


@pytest.mark.parametrize("sid,title", [
    ("C", "Load and Resistance Factor Design"),
    ("C.3.2", "Active Lateral Earth Pressures"),
    ("C.4.1", "Service Limit State Bearing Stress"),
    ("C-1", "LRFD Example C1: Interior Bridge Pier on Spread Footing"),
    ("C-1.5", "Example C-1, Step 5 – Determine the loads applied to the footing"),
    ("C-2", "LRFD Example 2 (Example C-2): Stub Seat-Type Bridge Abutment on Structural Fill"),
    ("C-2.12.b", "Example C-2, Step 12b – Check the bearing pressure, maximum eccentricity and "
                "sliding at the Strength I limit state without the bridge loading from the "
                "girders"),
])
def test_appendix_c_titles(sid, title):
    assert _section(sid)["title"] == title


def test_appendix_c_printed_numbers_said():
    assert "Printed as C.4.1" in _section("C.3.2")["applicability"]
    assert "no Section C.4.4" in _section("C.4.5")["applicability"]


def test_appendix_c_figures_tables_and_equations():
    secs = {s["section_id"]: s for s in _appendix_c()["sections"]}
    figs = {f.split(":")[0]: sid for sid, s in secs.items() for f in s["figures"]}
    assert len(figs) == 9
    assert figs["Figure C-1"] == "C.6" and figs["Figure C1-3"] == "C-1.6"
    assert figs["Figure C1-4"] == "C-1.8" and figs["Figure C2-4"] == "C-2.8"
    tabs = {t.split(":")[0]: sid for sid, s in secs.items() for t in s["tables"]}
    assert len(tabs) == 10
    assert tabs["Table C-5"] == "C.5.2" and tabs["Table C-6"] == "C.6"
    assert tabs["Table C1-2"] == "C-1.8" and tabs["Table C2-2"] == "C-2.5"
    eqs = {e["id"]: (sid, e["formula"]) for sid, s in secs.items() for e in s["equations"]}
    assert eqs == {
        "Eq. C-1": ("C.1", "ΣQi = Rn / FS"),
        "Eq. C-2": ("C.1", "Σ ηiγiQi ≤ φRn = Rr"),
        "Eq. C-3": ("C.5.4", "QR = φTQT+φepQep"),
        "Eq. C-4": ("C.5.4", "QT = Pv tan φ"),
        "Eq. C-5": ("C.5.4", "QT = Pv(0.8)tan φ"),
    }
    # Table C-3, the permanent load factors the examples take (p. C-5)
    t3 = secs["C.3"]["tables"][1]
    assert t3.startswith("Table C-3:")
    for row in ("DC: Component and Attachment; 1.25; 0.90", "DW: Wearing Surfaces and "
                "Utilities; 1.50; 0.65", "EV: Vertical Earth Pressure, Retaining Walls and "
                "Abutments; 1.35; 1.00", "EH: Horizontal Earth Pressure, Active; 1.50; 0.90"):
        assert row in t3


@pytest.mark.parametrize("sid,printed", [
    ("C.1", "The use of ηi other than 1.0 will therefore result in factored loads that are not "
            "consistent with the calibration, and should be done with caution or in accordance "
            "with the policies and procedures of the owner agency."),
    ("C.4.2", "Increasing the presumptive values with arbitrary factors for use in strength and "
              "extreme limit state design checks is unwise and could be unsafe."),
    ("C.4.5", "All slopes supporting footings should have a global factor of safety of at least "
              "1.5."),
    ("C.5.3", "less than one-fourth of the corresponding footing dimension, B or L, on soil and "
              "less than three-eights of the corresponding footing dimension, B or L, on rock"),
    ("C-2.12.a", "From Figure C2-3, the nominal bearing resistance at the strength limit state for "
                "an effective footing width of 2.32 m is about 1300 kPa."),
])
def test_appendix_c_printed_sentences(sid, printed):
    assert printed in _section(sid)["body"]


@pytest.mark.parametrize("sid,line", [
    # read from 200 dpi renders
    ("C-1.5", "P = 1.0[1.0 (6400 kN) + 1.0 (1670 kN) + 1.0(0 kN) + 0.3(884 kN) + 1.0 (18 kN) + "
             "0(1671 kN)]"),
    ("C-1.5", "PEmin = 1.0[1.25 (6400 kN) + 0 (1670 kN) + 1.0(0 kN) + 0(884 kN) + 0 (18 kN) - "
             "1.0(1671 kN)]"),
    ("C-1.7", "CWγ = 0.5 + 0.5 (9.1 / (1.5(6) + 2.3)) = 0.9"),
    ("C-1.7", "qult = 254Bf + 2553 kPa"),
    ("C-1.8", "ΔH2 = 2.1 m(1/65) log[(65.7 kPa + 0.55(600 kPa))/65.7 kPa)]"),
    ("C-1.8", "ΣΔHi = 25 mm + 9 mm + 3 mm + 1 mm = 38 mm"),
    ("C-1.11", "qapplied = P ÷ A′ = 8353 kN ÷ 23.0 m² = 363 kPa"),
    ("C-1.12", "qult = 254(4.766 m) + 2553 kPa = 3764 kPa"),
    ("C-1.12", "QR = 0.8(0.7(5760 kN)) = 3226 kN"),
    ("C-1.13", "qapplied = PEmax ÷ A′ = 9671 kN ÷ 16.8 m² = 576 kPa"),
    ("C-1.13", "QR = 1.0(0.7(6329 kN)) = 4430 kN"),
    ("C-2.5", "PLS = (Kaγheq)Habut = (0.26)(19.6 kN/m³)(0.70 m)(5.24 m) = 18.69 kN/m"),
    ("C-2.5", "Mtoe = 0.4(PA)(Habut) = 0.4(-69.96 kN/m)(5.24 m) = -146.6 kN·m/m"),
    ("C-2.7", "qult = 0.5γBfNγqCWγsγbγ = (0.5)(20.5 kN/m³)(2.0)(60)(1)(1)(1) = 1230 kPa"),
    ("C-2.11", "armR = Mtoe / Pv = (549.7 kN·m/m)/(518.3 kN/m) = 1.06 m"),
    ("C-2.12.a", "ey = Bf/2 - armR = 3.2 m/2 - 0.866 m = 1.6 m - 0.866 m = 0.73 m"),
    ("C-2.12.a", "Vmax = 1.5(EH) + 1.75(LS) + 0.5(TU + SH + CR) = 1.5(69.96) + 1.75(18.69) + "
                "0.5(1047/25) = 158.6 kN < 255.1 kN (OK)"),
    ("C-2.12.b", "qapplied = Pv/B′f = 300.8 kN/2.18 m = 138 kPa"),
    ("C-2.12.b", "Vmax = 1.5(EH) = 1.5(69.96) = 104.9 kN < 137.5 kN (OK)"),
])
def test_appendix_c_calculation_lines(sid, line):
    assert line in _section(sid)["body"]


def test_appendix_c_results_recompute():
    # Example C-1, Step 5
    assert round(6400 + 1670 + 0.3 * 884 + 18) == 8353
    assert round(1.25 * 6400 + 1.75 * 1670 + 0.5) == 10923      # 10922.5, a half case
    assert 1.25 * 6400 + 1671 == 9671 and 1.25 * 6400 - 1671 == 6329
    assert round(1.25 * 167 + 804) == 1013 and round(1.25 * 211 + 1675) == 1939
    assert 1.25 * 748 + 5546 == 6481
    # Steps 7 and 8
    assert round(0.5 + 0.5 * 9.1 / (1.5 * 6 + 2.3), 1) == 0.9
    assert round(0.5 * 19.6 * 48.0 * 0.9 * 0.6) == 254 and round(45.1 * 33.3 * 1.7) == 2553
    assert [round(9 / (3 + z) ** 2, 2) for z in (1.05, 4.45, 8.3, 11.3)] == [0.55, 0.16, 0.07, 0.04]
    dh = [h / c * log10((s + f * 600) / s) for h, c, s, f in
          ((2.1, 65, 65.7, 0.55), (4.7, 120, 132, 0.16), (3.0, 102, 193, 0.07), (3, 110, 222, 0.04))]
    assert [round(x * 1000) for x in dh] == [25, 9, 3, 1]
    # Steps 11 to 13
    assert round(4.844 * 4.752, 1) == 23.0 and round(8353 / 23.0) == 363
    assert round(4.82 * 4.766, 1) == 23.0 and round(10923 / 23.0) == 475
    assert round(254 * 4.766 + 2553) == 3764 and round(0.35 * 3764) == 1317
    assert round(0.8 * 0.7 * 5760) == 3226
    assert round(1939 / 9671, 3) == 0.200 and round(6481 / 9671, 3) == 0.670
    assert round(4.60 * 3.66, 1) == 16.8 and round(9671 / 16.8) == 576
    assert round(254 * 3.66 + 2553) == 3483 and round(0.7 * 6329) == 4430
    # Example C-2
    assert round(0.26 * 19.6 * 0.70 * 5.24, 2) == 18.69 and round(18.69 * 2.62, 2) == 48.97
    assert round(0.4 * 69.96 * 5.24, 1) == 146.6
    assert round(17 + 0.685 * 63) == 60 and round(0.5 * 20.5 * 2.0 * 60) == 1230
    assert round(0.5 * 20.5 * 2.5 * 51.5, -1) == 1320
    assert round((5233 + 446 + 1538) / 25, 1) == 288.7 and round((10032 - 3392) / 25, 1) == 265.6
    assert round(57.29 + 10.81 * 3.2 + 93.69 * 1.47, 1) == 229.6
    m11 = 84.79 + 5.41 * 3.2 ** 2 + 93.69 * 1.47 * (0.865 + 1.6) - 146.6 - 48.97
    assert round(m11, 1) == 284.1 and round(549.7 / 518.3, 2) == 1.06
    # Step 12a, eccentricity with minimum factors
    m12 = 0.9 * 84.79 + 0.9 * 5.41 * 3.2 ** 2 + 93.69 * 1.47 * 2.465 - 1.5 * 146.6 - 1.75 * 48.97
    assert round(0.9 * 5233 / 25, 1) == 188.4 and round((0.9 * 7274 - 0.5 * 3392) / 25, 1) == 194.0
    assert round(0.9 * 57.29 + 0.9 * 10.81 * 3.2 + 93.69 * 1.47, 1) == 220.4
    assert round(m12, 1) == 160.1 and round(354.1 / 408.8, 3) == 0.866
    # Step 12a, bearing with maximum factors
    pg = (1.25 * 5233 + 1.5 * 446 + 1.75 * 1538) / 25
    mg = (1.25 * 7274 + 1.5 * 620 + 1.75 * 2138 - 0.5 * 3392) / 25
    pa = 1.25 * 57.29 + 1.25 * 10.81 * 3.2 + 1.35 * 93.69 * 1.47
    ma = 1.25 * 84.79 + 1.25 * 5.41 * 3.2 ** 2 + 1.35 * 93.69 * 1.47 * 2.465 - 1.5 * 146.6 \
        - 1.75 * 48.97
    assert [round(x, 1) for x in (pg, mg, pa, ma)] == [396.1, 482.7, 300.8, 328.0]
    assert round(810.7 / 696.9, 3) == 1.163 and round(696.9 / 2.32) == 300
    assert round(0.8 * 0.78 * 408.8, 1) == 255.1
    assert round(1.5 * 69.96 + 1.75 * 18.69 + 0.5 * 1047 / 25, 1) == 158.6
    # Step 12b
    m12b = 0.9 * 84.79 + 0.9 * 5.41 * 3.2 ** 2 + 93.69 * 1.47 * 2.465 - 1.5 * 146.6
    assert round(m12b, 1) == 245.8 and round(245.8 / 220.4, 2) == 1.12
    assert round(328.0 / 300.8, 3) == 1.090 and round(300.8 / 2.18) == 138
    assert round(0.8 * 0.78 * 220.4, 1) == 137.5 and round(1.5 * 69.96, 1) == 104.9
    assert round(tan(radians(38)), 2) == 0.78


@pytest.mark.parametrize("sid,note", [
    # p. C-11, Table C-6: two section citations
    ("C.6", "(Section 5.4) (as printed; global stability is Section 5.5)"),
    ("C.6", "(Sections 6.4.3 and 6.4.4) (as printed; Chapter 6 has no Section 6.4.4"),
    # p. C-15, Table C1-1's first row
    ("C-1.5", "Dead load components (DW) (as printed; the load equations use DC"),
    ("C-1.7", "below the ground surface (Df) (as printed; the symbol defined is Dw) = 9.1 m"),
    ("C-1.7", "CWq = 0.5 + 0.5 (6.8 / 2.3) = 2.0 (as printed; 6.8 m = 9.1 m - 2.3 m"),
    ("C-1.11", "ez = 1038 kN-m ÷ 8353 k (as printed, for kN) = 0.124 m"),
    ("C-1.12", "ey = 980 kN-m ÷ 10923 kN = 0.089 m (as printed; 980 ÷ 10923 = 0.0897)"),
    ("C-1.12", "Vmin = 224 kN (as printed; Step 5 gives Vmin = 150 kN and Vmax = 282 kN) < 3226 "
              "kN (OK)"),
    ("C-2.5", "γP for DW = γmin = 0 (as printed; Table C-3 gives 0.65 as the minimum for DW)"),
    ("C-2.11", "= 518.3 kN·m/m (as printed, for kN/m)"),
    ("C-2.11", "= 246.8 kPa (as printed; 518.3 ÷ 2.12 = 244.5 kPa)"),
    ("C-2.12.a", "γLS(LS)] (as printed; the factors used, 1.25 and 1.35, are the maximums)"),
])
def test_appendix_c_print_slips_kept_and_noted(sid, note):
    sec = _section(sid)
    assert note in sec["body"] + " ".join(sec["tables"])


def test_appendix_c_print_slips_recompute():
    assert round(980 / 10923, 4) == 0.0897
    assert round(518.3 / 2.12, 1) == 244.5
    assert round(0.9 * 167) == 150 and round(1.25 * 167 + 1.75 * 42) == 282
    assert round(0.5 + 0.5 * 9.1 / 2.3, 1) > 1.0 and 9.1 - 2.3 == pytest.approx(6.8)
