"""AASHTO Guide for Design of Pavement Structures (1993): chapter text as printed.

Pins the text rebuilt from the printed pages of the Guide (build of 2026-11-12,
app BACKLOG REF-83): Part I chapters 1 to 5 and Part II chapters 1 to 4 read
from 200 and 300 dpi renders of the scan, Parts III and IV kept as stubs that
say so. Tables are typed cell by cell into the body; where the page prints a
slip, the text keeps what is printed and says so in a note, and those notes
are pinned too. Page numbers are the printed ones (I-50, II-82).
"""
from __future__ import annotations

import re

import pytest

from geotech_references._retrieval import retrieve_section

REF = "aashto_1993"


def sec(sid: str) -> dict:
    return retrieve_section(REF, sid)


def body(sid: str) -> str:
    return sec(sid)["body"]


def formulas(sid: str) -> list[str]:
    return [e.get("formula", "") for e in sec(sid).get("equations") or []]


def table_para(sid: str, label: str) -> str:
    b = body(sid)
    i = b.index("[" + label)
    return b[i:b.index("]\n", i) if "]\n" in b[i:] else len(b)]


# --- Part I ---------------------------------------------------------------------

def test_design_equations_as_printed():
    # pp. I-5 and I-6: equations (1.2.1) and (1.2.2)
    b = body("I-1.2")
    for t in ("9.36 × log10(SN + 1) − 0.20", "log10[ΔPSI / (4.2 − 1.5)]", "[0.40 + 1094 / (SN + 1)^5.19]",
              "2.32 × log10(MR) − 8.07   (1.2.1)", "7.35 × log10(D + 1) − 0.06", "log10[ΔPSI / (4.5 − 1.5)]",
              "[1 + 1.624 × 10^7 / (D + 1)^8.46]", "(4.22 − 0.32 × pt)", "215.63 × J", "18.42 / (Ec/"):
        assert t in b, t
    # the same constants in the equations printed on Figures 3.1 (p. II-32) and 3.7 (pp. II-45 to II-46)
    f31, f37 = formulas("II-3.1.1")[0], formulas("II-3.2.2")[0]
    assert "1094/(SN + 1)^5.19" in f31 and "9.36" in f31
    assert "1.624 × 10^7/(D + 1)^8.46" in f37 and "7.35" in f37


def test_present_worth_sum_limit_note():
    # p. I-50: equation (3.9.3) prints the upper limit of the sum as "t = 1"
    b = body("I-3.9.2")
    assert "Σ (t = 0 to t = 1) pwf(i,t)" in b
    assert 'the upper limit of the sum is printed "t = 1" on p. I-50' in b


def test_economic_analysis_in_its_printed_subsections():
    # pp. I-49 to I-51: 3.9 opens with one paragraph, then 3.9.1 to 3.9.3
    assert body("I-3.9").startswith("[p. I-49] For this report only the annual cost and present worth methods")
    assert [c["section_id"] for c in sec("I-3.9")["children"]] == ["I-3.9.1", "I-3.9.2", "I-3.9.3"]
    assert [e["id"] for e in sec("I-3.9.1")["equations"]] == ["Eq. 3.9.1"]
    assert [e["id"] for e in sec("I-3.9.2")["equations"]] == [f"Eq. 3.9.{n}" for n in range(2, 8)]
    assert body("I-3.9.3").startswith("[p. I-51] Either the net present worth value or the equivalent uniform annual cost")


def test_reliability_section_4_2_in_its_printed_subsections():
    # p. I-56: the 4.2 heading has no text of its own; 4.2.1 (p. I-56), 4.2.2 (p. I-57), 4.2.3 (p. I-60)
    with pytest.raises(KeyError):
        sec("I-4.2")
    assert body("I-4.2.1").startswith("[p. I-56] As far as reliability is concerned")
    assert body("I-4.2.2").startswith("[p. I-57] It is assumed that the set of all possible outcomes")
    assert body("I-4.2.3").startswith("[p. I-60] The probability distribution for the overall design-performance deviation")
    assert [e["id"] for e in sec("I-4.2.3")["equations"]] == [f"Eq. 4.2.{n}" for n in range(1, 6)]


def test_table_4_1_standard_normal_deviates():
    # p. I-62
    t = table_para("I-4.2.3", "Table 4.1.")
    for cell in ("50 | -0.000", "75 | -0.674", "90 | -1.282", "95 | -1.645", "99 | -2.327",
                 "99.9 | -3.090", "99.99 | -3.750"):
        assert cell in t, cell


def test_part_i_chapter_5_is_one_section():
    # p. I-65: chapter 5 prints no numbered subsections
    assert body("I-5").startswith("[p. I-65] This chapter concludes Part I of the Guide")
    with pytest.raises(KeyError):
        sec("I-5.1")


# --- Part II, chapters 1 and 2 --------------------------------------------------

def test_part_ii_limitations_and_organization():
    # p. II-4
    assert body("II-1.3").startswith("[p. II-4] The limitations inherent in the original AASHO Road Test equations")
    assert body("II-1.4").startswith("[p. II-4] Basically, the material contained herein is presented in a modular form")


def test_table_2_2_reliability_levels():
    # p. II-9
    t = table_para("II-2.1.3", "Table 2.2.")
    for cell in ("Interstate and Other Freeways | 85-99.9 | 80-99.9", "Principal Arterials | 80-99 | 75-95",
                 "Collectors | 80-95 | 75-95", "Local | 50-80 | 50-80"):
        assert cell in t, cell
    assert "Results based on a survey of the AASHTO Pavement Design Task Force" in t


def test_base_modulus_relation_note():
    # p. II-20: k2 printed on the line; the Road Test values show it is the exponent
    b = body("II-2.3.5")
    assert "EBS = k1θ^k2" in b
    assert "show k2 is the exponent of θ (p. II-20)" in b


def test_layer_coefficients_in_two_parts():
    # pp. II-17 to II-24: Section 2.3.5 in two parts, split at the run-in heading of p. II-21
    assert body("II-2.3.5.a").startswith("[p. II-21] Granular Subbase Layers.")
    assert "Granular Subbase Layers." not in body("II-2.3.5")
    assert "letter is not printed" in sec("II-2.3.5.a")["applicability"]
    eqs = {e["id"]: e for p in ("II-2.3.5", "II-2.3.5.a") for e in sec(p)["equations"]}
    assert eqs["SN = sum(ai*Di)"]["variables"]["Di"] == "thickness of layer i"
    assert "EBS" in eqs["a2 = 0.249*log10(EBS) - 0.977"]["variables"]
    assert "ESB" in eqs["a3 = 0.227*log10(ESB) - 0.839"]["variables"]
    assert "a2 = 0.14, EBS = 30,000 psi" in " ".join(sec("II-2.3.5")["key_points"])
    assert "a3 = 0.11, ESB = 15,000 psi" in " ".join(sec("II-2.3.5.a")["key_points"])
    assert [f[:10] for f in sec("II-2.3.5.a")["figures"]] == ["Figure 2.7", "Figure 2.8", "Figure 2.9"]


# --- Part II, chapter 3 ---------------------------------------------------------

def test_table_3_1_performance_period_iterations():
    # p. II-34
    t = table_para("II-3.1.3", "Table 3.1.")
    assert "ΔPSI = po − pt = 4.4 − 2.5 = 1.9" in t
    for row in ("1 | 13.0 | 0.73 | 1.17 | 2.0 × 10^6 | 6.3", "2 | 9.7 | 0.63 | 1.27 | 2.3 × 10^6 | 7.2",
                "3 | 8.5 | 0.56 | 1.34 | 2.6 × 10^6 | 8.2"):
        assert row in t, row


def test_table_3_3_effective_k_example():
    # p. II-43
    t = table_para("II-3.2.1", "Table 3.3.")
    assert "Jan | 20,000 | 50,000 | 1,100 | 1,350 | 0.35" in t
    assert "Mar | 2,500 | 15,000 | 160 | 230 | 0.86" in t
    assert "Table 3.3 enters the relative damage as 0.35, 0.86, 0.78 and 0.60" in body("II-3.2.1")


def test_table_3_4_rigid_performance_period():
    # p. II-48
    assert "ΔPSI = po − pt = 4.2 − 2.5 = 1.7" in table_para("II-3.2.4", "Table 3.4.")


def test_table_3_7_allowable_steel_stress():
    # p. II-56
    t = table_para("II-3.4.2.b", "Table 3.7.")
    for row in ("300 (or less) | 65 | 57 | 54", "500 | 67 | 61 | 56", "800 (or greater) | 67 | 67 | 60"):
        assert row in t, row


def test_crcp_section_split_in_three_lettered_parts():
    # Section 3.4.2 (pp. II-51 to II-62) is over the app's result size limit as one section;
    # the letters are not printed
    titles = {p: sec(f"II-3.4.2.{p}")["title"] for p in "abc"}
    assert titles == {
        "a": "Continuously Reinforced Concrete Pavements (part a: inputs and limiting criteria)",
        "b": "Continuously Reinforced Concrete Pavements (part b: design procedure)",
        "c": "Continuously Reinforced Concrete Pavements (part c: design example)",
    }
    assert body("II-3.4.2.a").startswith("[p. II-51] This section is for the design of longitudinal reinforcing steel")
    assert body("II-3.4.2.b").startswith("[p. II-53] Design Procedure.")
    assert body("II-3.4.2.c").startswith("[p. II-56] Design Example.")
    assert 'both formulas are printed with "D/φ/²" (p. II-56)' in body("II-3.4.2.b")
    assert len(sec("II-3.4.2.b")["equations"]) == 4


# --- Part II, chapter 4 ---------------------------------------------------------

def test_section_4_1_heading_holds_no_text():
    # p. II-69: 4.1 is printed as a heading only; its text is in 4.1.1 and 4.1.2
    with pytest.raises(KeyError):
        sec("II-4.1")
    assert sec("II-4.1.1")["title"] and sec("II-4.1.2")["title"]


def test_table_4_1_seasons_rows_add_to_twelve_months():
    # p. II-71
    t = table_para("II-4.1.1", "Table 4.1.")
    num = r"(\d+(?:\.\d+)?)"
    rows = re.findall(r"(?:^|; |\. )(I|II|III|IV|V|VI) \| " + num + r"\*? \| " + " \\| ".join([num] * 3), t)
    assert [r[0] for r in rows] == ["I", "II", "III", "IV", "V", "VI"]
    for r in rows:
        assert sum(float(x) for x in r[1:]) == pytest.approx(12.0), r
    assert "III | 2.5 | 1.5 | 4.0 | 4.0" in t


def test_aggregate_loss_design_thickness():
    # p. II-77
    b = body("II-4.1.2")
    assert "DBS = D̄BS + (0.5 × GL)" in b
    assert "GL = total estimated aggregate (gravel) loss (in inches) over the performance period" in b
    assert "DBS = D̄BS + (0.5 × GL)" in formulas("II-4.1.2")


def test_flexible_catalog_tables_4_6_and_4_7():
    # p. II-80
    t46 = table_para("II-4.2.1", "Table 4.6.")
    assert "Very good, High | 2.3-2.5* | 2.5-2.7 | 2.8-3.0 | 2.1-2.3 | 2.4-2.6 | 2.8-3.0" in t46
    assert "Fair, Medium | 2.6-2.8 | 2.8-3.0 | 2.9-3.1 | 2.5-2.7 | 2.6-2.8 | 2.8-3.0" in t46
    t47 = table_para("II-4.2.1", "Table 4.7.")
    assert "Very good, High | 2.6-2.7* | 2.8-2.9 | 3.0-3.2 | 2.4-2.5 | 2.7-2.8 | 3.0-3.2" in t47
    assert "Fair, Medium | 2.8-3.1 | 2.9-3.2 | 2.7-3.3 | 2.7-3.0 | 2.8-3.1 | 3.0-3.3" in t47
    assert "Table 4.7 (75 percent) prints 2.7-3.3 for Fair, Medium, Region III" in body("II-4.2.1")


def test_rigid_catalog_tables_4_8_and_4_9():
    # pp. II-81 to II-85
    b = body("II-4.2.2")
    assert "leaving 350 to 400 pci unassigned (p. II-81)" in b
    t = table_para("II-4.2.2", "Table 4.8(a).")
    assert "Inherent reliability: 50 percent; Without Granular Subbase" in t
    assert "High Traffic: Very good & good | 7 | 6.25 | 6.25 | 5.25 | 6.5 | 6 | 5.75 | 5.25" in t
    t = table_para("II-4.2.2", "Table 4.9(b).")
    assert "Poor & very poor | 7.25 | 6.75 | 6.75 | 6 | 6.75 | 6.25 | 6.25 | 5.5" in t


def test_aggregate_catalog_table_4_10():
    # p. II-86
    t = table_para("II-4.2.3", "Table 4.10.")
    assert "Very good, High | 8* | 10 | 15 | 7 | 9 | 15" in t
    assert "Good, Low | 4 | 5 | 7 | 4 | 5 | 7" in t


# --- Parts III and IV: stubs ----------------------------------------------------

def test_part_iii_stub_and_remaining_life_equations():
    s = sec("III")
    assert s["title"] == "Part III (stub): contents, and the remaining life equations of Section 5.3.3"
    b = s["body"]
    assert b.startswith("[Stub: this library does not hold the text of Part III.")
    # p. III-89
    for t in ("RL = 100[1 − (Np/N1.5)]", "CF = SCn/SCo", "SNeff = CF * SNo"):
        assert t in b, t
    assert 'N1.5 = total traffic to pavement "failure" (P2 = 1.5), 18-kip ESAL' in b
    # no Deff equation is printed with them ("SNeff or Deff" is named in the prose)
    assert "Deff =" not in b and not any("Deff" in f for f in formulas("III"))


def test_part_iv_stub():
    s = sec("IV")
    assert s["title"] == "Part IV (stub): contents and overview"
    b = s["body"]
    assert b.startswith("[Stub: this library does not hold the text of Part IV.")
    assert "This issue (1986) of the [p. IV-4] Guide has indirectly used mechanistic procedures" in b
    assert '"This issue (1986)" is printed so in the 1993 Guide' in b
