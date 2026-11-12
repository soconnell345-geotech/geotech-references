"""Micropile manual (FHWA-NHI-05-039, 2005) Appendices D and E pinned to the print.

REF-85 (app backlog): the library held the manual's ten chapters as a
condensed paraphrase and none of its appendices, so the two sample problems
could not be searched or quoted. Appendix D (Sample Problem No. 1, bridge
abutment support, pp. D-1 to D-24) is chapter 14 and Appendix E (Sample
Problem No. 2, a laterally loaded micropile, pp. E-1 to E-6) chapter 15, in
the print's own wording with [p. D-1] markers; every calculation line and
Table S1-1 are typed in from rendered pages (the text layer scatters the
equation-editor objects). Where the print disagrees with itself the stored
text keeps the print and says so "(as printed; ...)". Chapters 11 to 13 are
left for Appendices A to C (Case 2 networks, LPILE output, guide
specification).
"""

import json
import re
from math import pi, sqrt

import pytest

from geotech_references._retrieval import load_chapter, retrieve_section
from geotech_references.micropile import tables


def _section(sid):
    return retrieve_section("micropile", sid)


def _appendix(ch):
    return load_chapter("micropile", ch)


def _scatter_free(body):
    """The patterns a text-layer formula leaves when it scatters."""
    assert not re.search(r"(?m)^\d\s*$", body)                          # a lone digit line
    assert not re.search(r"ca sin g|jo int", body)                       # editor-set subscripts
    for a, b in ("()", "[]"):
        assert body.count(a) == body.count(b)                           # unbalanced brackets
    paras = [p for p in body.split("\n\n") if len(p) > 40]
    assert all(x != y for x, y in zip(paras, paras[1:]))                # a repeated paragraph
    assert not re.search(r"(?<![\d,])\.\d\d? [\d.]", body)              # reversed digits (".7 48")


# ---------------------------------------------------------------- Appendix E

def test_appendix_e_chapter_and_section():
    data = _appendix(15)
    assert data["chapter_title"] == "Appendix E: Sample Problem No. 2, Laterally Loaded Micropile"
    assert data["reference_id"] == "FHWA-NHI-05-039"
    assert [s["section_id"] for s in data["sections"]] == ["E"]
    s = _section("E")
    assert s["title"] == "Sample Problem No. 2 – Laterally Loaded Micropile"
    # E-2 and E-6 hold only figures; E-7 to E-30 are LPILE output, not stored
    assert re.findall(r"\[p\. ([^\]]+)\]", s["body"]) == ["E-1", "E-3", "E-4", "E-5"]
    assert "pp. E-7 to E-30" in s["applicability"]
    _scatter_free(s["body"])
    assert len(s["body"]) <= 12000 and len(json.dumps(s)) <= 14000


@pytest.mark.parametrize("printed", [
    "The micropiles are required to carry a design axial compression load of 1,423 kN and a "
    "design lateral groundline shear load of 44.48 kN.",
    "For the analysis, a 0.305-m embedment depth was conservatively assumed.",
    "Assume buckling potential is negligible, F′e >>> fa",
    "This result indicates that threaded connections should not be placed from the bottom of "
    "the pile cap to approximately 0.5 m below the ground surface where the micropile-footing "
    "connection achieves 100% fixity.",
    "On projects where a second casing is used, the design should require that joints from the "
    "two casings be staggered by at least 1 m.",
])
def test_appendix_e_printed_sentences(printed):
    assert printed in _section("E")["body"]


@pytest.mark.parametrize("line", [
    # pp. E-1, E-3, E-4, read from 200 dpi renders
    "Acasing = π/4 (OD² - ID²) = π/4 (0.1969² m² - (0.1969 - 2(0.0151))² m²) = 0.00863 m²",
    "Scasing = Icasing / (OD/2) = 0.00003587 m.⁴ / (0.1969 m/2) = 0.000364 m³",
    "Agrout = π/4 (OD²) - Acasing = π/4 (0.1969² m²) - 0.00863 m² = 0.0218 m²",
    "fa/Fa + fb / ((1 - fa/F′e) Fb) ≤ 1.0",
    "fa = Pc / Acasing = 1,423 kN / 0.00863 m² = 164.89 MPa",
    "fb = Mmax / Scasing = 37.3 kN-m / 0.000364 m³ = 102.47 MPa",
    "Fa = 0.47 Fy = 0.47 (552 MPa) = 259.44 MPa",
    "Fb = 0.55 Fy = 0.55 (552 MPa) = 303.6 MPa",
    "164.89 MPa / 259.44 MPa + 102.47 MPa / 303.6 MPa = 0.97 < 1.0 OK",
    "Pc / Pc-allowable + Mmax / Mallowable ≤ 1.0",
    "Mallowable = 0.55 Fy Scasing = 0.55 (552 MPa) (0.000364 m³) = 110.5 kN-m.",
    "1,423 kN / 2,479 kN + 37.3 kN-m / 110.5 kN-m = 0.91 < 1.0 OK",
    "Sjoint = Ijoint / ((OD - tw)/2) = π/64 ((OD - tw)⁴ - ID⁴) / ((OD - tw)/2)",
])
def test_appendix_e_calculation_lines(line):
    assert line in _section("E")["body"]


def test_appendix_e_results_recompute():
    od, tw = 0.1969, 0.0151
    i_d = od - 2 * tw
    assert round(0.00003587 / (od / 2), 6) == 0.000364
    assert round(pi / 4 * od ** 2 - 0.00863, 4) == 0.0218
    assert round(1423 / 0.00863 / 1000, 2) == 164.89
    assert round(37.3 / 0.000364 / 1000, 2) == 102.47
    assert round(164.89 / 259.44 + 102.47 / 303.6, 2) == 0.97
    assert round(0.55 * 552 * 0.000364 * 1000, 1) == 110.5
    assert round(1423 / 2479 + 37.3 / 110.5, 2) == 0.91
    s_joint = pi / 64 * ((od - tw) ** 4 - 0.1667 ** 4) / ((od - tw) / 2)
    assert round(s_joint, 6) == 0.000173


def test_appendix_e_print_slips_kept_and_noted():
    body = _section("E")["body"]
    # p. E-1: Acasing and Icasing are one unit high in their last printed digit
    od, i_d = 0.1969, 0.1667
    assert "= 0.00863 m² (as printed; π/4 (0.1969² - 0.1667²) = 0.008624)" in body
    assert round(pi / 4 * (od ** 2 - i_d ** 2), 6) == 0.008624
    assert "= 0.00003587 m⁴ (as printed; 0.1969 is in m, and π/64 (0.1969⁴ - 0.1667⁴) = " \
           "0.000035876)" in body
    assert round(pi / 64 * (od ** 4 - i_d ** 4), 9) == 0.000035876
    # p. E-4: the two terms of Pc-allowable give 2,479.6 kN
    assert "= 2,479 kN (as printed; the two terms give 2,479.6 kN)" in body
    assert round(0.4 * 27.6 * 0.0218 + 0.47 * 552 * 0.00863, 5) == 2.47964
    # p. E-4: 0.000173 x (1 - 164.89/259.44) x 303.6 = 0.01914 MN-m; the text uses 19.2
    assert "= 19.2 kN-m (as printed; 0.000173 × (1 - 164.89/259.44) × 303.6 = 0.01914 MN-m, " \
           "19.1 kN-m)" in body
    assert round(0.000173 * (1 - 164.89 / 259.44) * 303.6, 5) == 0.01914
    assert body.count("19.2 kN-m or less") == 1
    # p. E-1: the first term of Icasing prints in.⁴ for a value in m
    assert "0.1969⁴ in.⁴" in body


def test_appendix_e_lpile_table_and_figures():
    s = _section("E")
    assert "Table (not numbered in the print) - columns: Axial Load (kN); Fixity Condition; Pile " \
           "Head Deflection (mm); Maximum Shear Load (kN); Maximum Bending Moment (kN-m). 1,423; " \
           "100%; 3.3; 44.48; -37.3 | 1,423; 50%; 8.4; 44.48; 27.2" in s["body"]
    assert s["figures"] == [
        "Figure S2-1: Micropile Detail for Sample Problem 2",
        "Figure S2-2: Bending Moment Diagram for Sample Problem No. 2",
        "Figure S2-3: Lateral Deflection Profile for Sample Problem No. 2",
    ]
    # the chart lettering is not stored as text
    assert "Free Head" not in s["body"] and "Depth (m)" not in s["body"]


def test_appendix_e_cites_the_chapter_5_equations():
    # Eqs. 5-3, 5-6, 5-26 and 5-27 as chapter 5 stores them (p. 5-15 to p. 5-61)
    eqs = " ".join(e for s in _appendix(5)["sections"] for e in s["equations"])
    for n in ("5-3", "5-6", "5-26", "5-27"):
        assert f"Eq. {n}:" in eqs
        assert f"(Eq. {n}" in _section("E")["body"]


# ---------------------------------------------------------------- Appendix D

D_IDS = ["D"] + [f"D.{n}" for n in range(1, 11)]


def test_appendix_d_sections_and_titles():
    data = _appendix(14)
    assert data["chapter_title"] == ("Appendix D: Sample Problem No. 1, Bridge Foundation "
                                     "Abutment Support")
    assert [s["section_id"] for s in data["sections"]] == D_IDS
    titles = {s["section_id"]: s["title"] for s in data["sections"]}
    # printed headings, pp. D-1 to D-22
    assert titles["D"] == "Sample Problem No. 1 – Bridge Abutment Foundation Support"
    assert titles["D.3"] == "Step 3 – Evaluate Allowable Structural Capacity of Cased Length"
    assert titles["D.8"] == "Step 8 – Micropile to Footing Connection Design"
    assert titles["D.10"] == "Step 10 – Prepare Drawings"
    labels = [int(p) for s in data["sections"] for p in re.findall(r"\[p\. D-(\d+)\]", s["body"])]
    # D-2 to D-5, D-23 and D-24 hold only figures and drawings
    assert labels == sorted(labels)
    assert set(labels) == {1} | set(range(6, 23))
    for s in data["sections"]:
        _scatter_free(s["body"])
        assert "LENGTH" not in s["body"]
        assert len(s["body"]) <= 12000 and len(json.dumps(s)) <= 14000


@pytest.mark.parametrize("sid,printed", [
    ("D", "This example also does not illustrate construction load cases (e.g., full backfill "
          "prior to girder placement) that need to be incorporated into actual designs."),
    ("D", "a unit weight of 17.5 kN/m³. The unit weight of the concrete is 23.6 kN/m³. Figure "
          "S1-1 shows the dimensions of the abutment. The pile details are shown on Figure S1-2."),
    ("D", "Type B3 (pressure grouted through the casing during casing withdrawal) micropiles will "
          "be used."),
    ("D.1", "To be conservative, neglect the vertical portion of PEQ over the footing heel."),
    ("D.2", "A more refined analysis would utilize the vertical stiffness of the batter pile."),
    ("D.3", "To maintain strain compatibility between the reinforcing bar and casing in the upper "
            "pile length, a yield strength (Fy-steel) of 241 MPa is used for both members."),
    ("D.3", "Reduce outside diameter by 1.6 mm to account for corrosion."),
    ("D.5", "From Table 5-3 select an ultimate unit grout-to-ground bond strength α bond = 265 kPa. "
            "This represents an approximate average value for gravels."),
    ("D.6", "The lateral resisting load is greater than the lateral design load therefore the pile "
            "lateral design is OK."),
    ("D.8", "Note – edge distance limitations and other requirements of ACI 349 Appendix B must be "
            "satisfied."),
    ("D.8", "Weld bending stress must be analyzed for other conditions."),
    ("D.9", "* Do not reduce by 1.6 mm for corrosion."),
    ("D.9", "The design pile is OK for the proof test at 952 kN and the verification test at "
            "1,190 kN."),
])
def test_appendix_d_printed_sentences(sid, printed):
    assert printed in _section(sid)["body"]


@pytest.mark.parametrize("sid,line", [
    # every formula line read from a 200 dpi render, pp. D-6 to D-22
    ("D.1", "Coefficient of active soil pressure Ka = tan²[45° - φ/2] = 0.271"),
    ("D.1", "Resultant load PE = 0.5 × 4.74 kN/m³ × (5.25m)² = 65.32 kN/m"),
    ("D.1", "Moment about centroid 65.32 kN/m × 5.25m/3 = 114.31 kN-m/m"),
    ("D.1", "Seismic coefficients kh = 1.5 × A = 0.15 and kv = 0 (assumed value)"),
    ("D.1", "Seismic inertia angle θ = tan⁻¹[kh / (1 - kv)] = 8.53°"),
    ("D.1", "Ψ = [1 + √(sin(φ + δ) × sin(φ - θ - i) / (cos(δ + β + θ) × cos(i - β)))]² = 2.65"),
    ("D.1", "KAE = [cos²(φ - θ) / (Ψ × cos(θ) × cos(θ + δ))] = 0.34"),
    ("D.1", "Resultant seismic force PEQ = [0.5 × 5.95 kN/m³ × (5.25m)²] - PE = 16.68 kN/m"),
    ("D.1", "PEQ-H = 16.68 kN/m (cos δ) = 15.91 kN/m"),
    ("D.1", "IA = kh (DC + DS) = 0.15 × (97.0 + 108.68) = 30.9 kN/m"),
    ("D.2", "I = 1/1.5 (0.74)² + 1/2.25 (1.11)² = 0.9127"),
    ("D.2", "Front Pile Vertical Load = [457.4/1.111 + [266 - 457.4 × 0.185] 0.74 / 0.9127] = "
            "559 kN"),
    ("D.2", "Front Pile Axial Load = 559 / cos(20°) = 595 kN compression"),
    ("D.3", "Pile casing steel area Acasing = π/4 [OD²casing - ID²casing] = 3,224 mm²"),
    ("D.3", "Grout area Agrout = π/4 ID²casing - Abar = 10,240 mm²"),
    ("D.3", "Pt-allowable = 0.55 Fy-steel (Abar + Acasing) = 620 kN"),
    ("D.3", "Pc-allowable = [0.4 f′c-grout × Agrout + 0.47 Fy-steel (Abar + Acasing)] = 671 kN"),
    ("D.4", "Pc-allowable = (0.4 × 34.5 MPa × 27,200 mm² + 0.47 × 520 MPa × 1,452 mm²) = 730 kN"),
    ("D.5", "Lb = PG-allowable × FS / (αbond × π × Db)"),
    ("D.5", "Lb = 595 kN × 2.0 / (265 kPa × π × 0.191 m) = 7.48 m"),
    ("D.5", "PG-allowable = 265 kPa / 2.0 × 3.14 × 0.191m × 7.5m = 596 kN"),
    ("D.6", "Lateral resisting load = 559 kN × tan(20°) = 204 kN per pile"),
    ("D.7", "Max pile length from footing to top of gravel Lupper = 3.35 m / cos(Φbatter) = 3.6 m"),
    ("D.7", "Δtelastic = Pcompression × Lb / AEuncased length = 595 kN × (1/2 × 7.5 m) / "
            "1,133,000 kN = 2.0 mm"),
    ("D.8", "ACP = π/4 [d2² - d1²] = π/4 [1086² - 286²] = 862,053 mm²"),
    ("D.8", "LF = 1.3 [1.0 × 0.62 + 1.67 × 0.16 + 1.3 × 0.22] = 1.53"),
    ("D.8", "Pcone allowable = 1,504 kN / 2.35 = 640 kN > 594.6 kN .... OK"),
    ("D.8", "Mmax = 10 mm × 1/2 [(Platewidth - ODcasing) / 2]² × Bearingcompression = 0.147 kNm"),
    ("D.8", "Required plate thickness - treq = √(6 Sx-req / 10 mm) = 21.6 mm"),
    ("D.8", "Pweld-top = 0.707 tweld-top Φ F Lweld = 598 kN > 595 kN . . . OK"),
    ("D.9", "Pc-allowable = [0.68 × 34.5MPa × 10,240 mm² + 241MPa / 1.25 (1,452 mm² + 3,925 mm²)] "
            "= 1,277 kN"),
    ("D.9", "Pc-allowable = 0.68 × 34.5 MPa × 27,200 mm² + 0.80 × 520 MPa × 1,452 mm² = 1,242 kN"),
])
def test_appendix_d_calculation_lines(sid, line):
    assert line in _section(sid)["body"]


def test_appendix_d_printed_results_recompute():
    from math import atan, cos, degrees, radians, sin, tan
    assert round(tan(radians(27.5)) ** 2, 3) == 0.271
    assert round(0.5 * 4.74 * 5.25 ** 2, 2) == 65.32
    assert round(degrees(atan(0.15)), 2) == 8.53
    ph, d, th = radians(35), radians(17.5), atan(0.15)
    psi = (1 + sqrt(sin(ph + d) * sin(ph - th) / cos(d + th))) ** 2
    assert round(psi, 2) == 2.65
    assert round(cos(ph - th) ** 2 / (psi * cos(th) * cos(th + d)), 2) == 0.34
    assert round(0.5 * 5.95 * 5.25 ** 2 - 65.32, 2) == 16.68
    assert round(16.68 * cos(d), 2) == 15.91
    assert round(97.0 + 108.7 + 178.7 + 73.0, 1) == 457.4
    rear = 457.4 / 1.111 - (266 - 457.4 * 0.185) * 1.11 / 0.9127
    front = 457.4 / 1.111 + (266 - 457.4 * 0.185) * 0.74 / 0.9127
    assert (round(rear), round(front), round(front / cos(radians(20)))) == (191, 559, 595)
    assert round(pi / 4 * (137.8 ** 2 - 122 ** 2)) == 3224
    assert round(0.55 * 241 * (1452 + 3224) / 1000) == 620
    assert round((0.4 * 34.5 * 10240 + 0.47 * 241 * (1452 + 3224)) / 1000) == 671
    assert round((0.4 * 34.5 * 27200 + 0.47 * 520 * 1452) / 1000) == 730
    assert round(595 * 2 / (265 * pi * 0.191), 2) == 7.48
    assert round(265 / 2 * 3.14 * 0.191 * 7.5) == 596
    assert round(595 * 4.6 / 1252000 * 1000, 1) == 2.2
    assert round(pi / 4 * (1086 ** 2 - 286 ** 2)) == 862053
    assert round(10.5 * sqrt(27600) * 862053e-6) == 1504
    assert round(1.3 * (0.62 + 1.67 * 0.16 + 1.3 * 0.22), 2) == 1.53
    assert round(sqrt(6 * 775 / 10), 1) == 21.6
    assert round((0.68 * 34.5 * 10240 + 241 / 1.25 * (1452 + 3925)) / 1000) == 1277
    assert round((0.68 * 34.5 * 27200 + 0.80 * 520 * 1452) / 1000) == 1242


def test_appendix_d_print_slips_kept_and_noted():
    two = _section("D.2")["body"]
    # p. D-9: the loads are in Table S1-1, which gives HL = 14.91 kN and 39.13 kN-m
    assert "shown in Table 5-4 (as printed; the abutment loads are in Table S1-1)." in two
    assert "Fx = 15.0 + 65.3 = 80.3 kN/m (as printed; Table S1-1 gives HL = 14.91 kN, and " \
           "14.91 + 65.32 = 80.23)" in two
    assert "= 266.0 kN/m (as printed; Table S1-1 gives 39.13 for HL, and its six moments sum " \
           "to 265.85)" in two
    assert round(26.19 - 59.77 + 103.65 + 42.34 + 39.13 + 114.31, 2) == 265.85
    # p. D-8: the moment of PEQ against Table S1-1's PEQ-H row
    assert "= 52.54 kNm/m (as printed; Table S1-1 gives the moment of the horizontal " \
           "component, PEQ-H: 15.91 × 3.15 = 50.12 kN-m)" in _section("D.1")["body"]
    seven = _section("D.7")["body"]
    assert "= 1,252,000 kN (as printed; 10,240 × 31,000 + 4,676 × 200,000 N gives 1,252,640 " \
           "kN)" in seven
    assert 10240 * 31000 + 4676 * 200000 == 1_252_640_000
    assert "= 1,133,000 kN (as printed; 27,200 × 31,000 + 1,452 × 200,000 N gives 1,133,600 " \
           "kN)" in seven
    eight = _section("D.8")["body"]
    assert "= 286mm (as printed; √(4 × 254² / π) = 286.6)" in eight
    assert round(sqrt(4 * 254 ** 2 / pi), 1) == 286.6
    assert "= 603 kN (as printed; 0.707 × 6.35 × 111.8 × 1,200 = 602,305 N, 602 kN)" in eight
    assert round(0.707 * 6.35 * 111.8 * 1200) == 602305
    assert "Pcone nominal strength = 10.5 φ √(f′c) kPa × ACP (as printed; the line below " \
           "leaves φ out, and φ enters through FS = LF/φ)" in eight


def test_appendix_d_table_s1_1_typed_from_the_page():
    s = _section("D.1")
    assert len(s["tables"]) == 1 and "[Table S1-1]" in s["body"]
    t = s["tables"][0]
    assert t.startswith("Table S1-1: Sample Problem No. 1- Summary of Abutment Loads Per Meter "
                        "Length (p. D-7)")
    for row in ("Dc; Dead load of concrete abutment; D; —; 97.00; 0.27; —; 26.19",
                "VDL; Dead load from bridge superstructure; D; —; 178.70; 0.58; —; 103.65",
                "PE; Earth pressure; E; 65.32; —; —; 1.75; 114.31",
                "IS; Seismic inertial force of the superstructure; EQ; 26.8; —; —; 3.55; 95.14"):
        assert row in t
    assert t.endswith("*Moment is calculated about the center of the footing at its base.")
    # the HL row's moment, which Step 2 quotes, is noted against its force and arm
    assert "HL; Earth pressure due to live load surcharge; L; 14.91; —; —; 2.63; 39.13 (as " \
           "printed; 14.91 × 2.625 = 39.14, and 14.91 × 2.63 = 39.21)" in t
    assert (round(14.91 * 2.625, 2), round(14.91 * 2.63, 2)) == (39.14, 39.21)
    # moment = force x arm, row by row (IA from its unrounded 30.852 kN)
    for f, arm, m in ((97.00, 0.27, 26.19), (108.68, -0.55, -59.77), (178.70, 0.58, 103.65),
                      (73.00, 0.58, 42.34), (65.32, 1.75, 114.31), (15.91, 3.15, 50.12),
                      (30.852, 2.35, 72.50), (26.8, 3.55, 95.14)):
        assert f * arm == pytest.approx(m, abs=0.011)


def test_appendix_d_figures():
    figs = {s["section_id"]: [f.split(":")[0] for f in s["figures"]]
            for s in _appendix(14)["sections"] if s["figures"]}
    assert figs == {"D": ["Figure S1-1", "Figure S1-2", "Figure S1-3", "Figure S1-4"],
                    "D.8": ["Figure S1-5"], "D.10": ["Figure S1-6", "Figure S1-7"]}
    s13 = _section("D")["figures"][2]
    # the figure's legend carries the given loads (p. D-4)
    assert "VDL = 178.70 kN/m (dead load from bridge structure)" in s13
    assert "VLL = 73.00 kN/m (live load from bridge structure)" in s13


def test_appendix_d_lookups_agree_with_the_example():
    # p. D-12: a 43 mm Grade 520 bar of 1,452 mm2 (Table 4-2, p. 4-27, #14)
    bar = tables.table_4_2_rebar_properties("#14", 520)
    assert bar["diameter_mm"] == 43 and bar["area_mm2"] == 1452
    # p. D-13: 265 kPa for gravel with Type B grouting lies in Table 5-3's range
    bond = tables.table_5_3_alpha_bond("gravel", "B")
    assert bond["alpha_bond_min_kpa"] <= 265 <= bond["alpha_bond_max_kpa"]
