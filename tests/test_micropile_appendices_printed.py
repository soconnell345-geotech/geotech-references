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
