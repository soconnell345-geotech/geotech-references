"""EM 1110-2-2107 (1 August 2022) stored chapter text against the print.

Each test pins a printed form, limit or statement the stored text once got
wrong or left out (review of 2026-11-10, findings text-11 and text-17;
app backlog REF-83). Pages are the printed page numbers; the PDF page is the
printed page plus 9 for chapters 1 to 6.
"""

import json

from geotech_references._retrieval import load_chapter


def _section(chapter, section_id):
    for s in load_chapter("em_2107", chapter)["sections"]:
        if s["section_id"] == section_id:
            return s
    raise KeyError(section_id)


def _all_text(section):
    return json.dumps(section, ensure_ascii=False)


class TestChapter1:
    def test_1_11_design_guidance_carries_its_printed_requirements(self):
        # p. 2: 1.11 Design Guidance: non-carbon HSS use this manual's loads,
        # AISC Design Guide 27 for stainless, the Aluminum Design Manual.
        s = _section(1, "1.11")
        assert "For non-carbon HSS, use the loads, load factors, and load combinations in this manual." in s["body"]
        assert "AISC Design Guide 27" in s["body"]
        assert "Aluminum Design Manual" in s["body"]
        assert "no distinct printed content" not in _all_text(s)

    def test_1_10_is_reuse_of_existing_designs(self):
        # p. 2: 1.10 "All newly fabricated HSS must be designed according to this manual."
        s = _section(1, "1.10")
        assert "All newly fabricated HSS must be designed according to this manual." in s["body"]
        assert "Existing designs used for new work must be modified" in s["body"]
        assert "Design Guide 27" not in s["body"]

    def test_1_9_requirement_criterion_defines_the_terms(self):
        # p. 2: 1.9 Requirement Criterion: "will" or "must" mandatory, "should"
        # strong preference, "may" usable; other approved criterion may be used.
        s = _section(1, "1.9")
        assert "denotes a mandatory requirement" in s["body"]
        assert "strong preference" in s["body"]
        assert "Other suitably documented, verified, and approved criterion may also be used" in s["body"]
        assert "strong preference" not in _section(1, "1.8")["body"]


class TestChapter2:
    def test_2_4_prints_chapters_9_to_14(self):
        # p. 6: "Chapters 9-14 provide geometry, details, and other information"
        # and records "should be modified to comply with current design requirements".
        s = _section(2, "2.4")
        assert "Chapters 9-14 provide geometry" in s["body"]
        assert "should be modified to comply" in s["body"]
        assert "must be updated" not in _all_text(s)


class TestChapter3:
    def test_3_2_table_3_1_target_reliability(self):
        # p. 11, Table 3.1: redundant load path 3.0 normal / 3.5 critical,
        # single load path 3.5 / 4.0.
        s = _section(3, "3.2")
        assert "redundant load path 3.0 (normal), 3.5 (critical); single load path 3.5 (normal), 4.0 (critical)" in s["body"]

    def test_3_5_failure_critical_measures_are_to_consider(self):
        # p. 15: "Consider these measures when designing Failure Critical
        # Members"; FCM "must be identified by the Engineer and labeled".
        s = _section(3, "3.5")
        assert "Consider these measures when designing Failure Critical Members" in s["body"]
        assert "must be identified by the Engineer and labeled in the project plans" in s["body"]
        assert "requiring: additional levels of scrutiny" not in s["body"]

    def test_3_3_extreme_keeps_as_long_as(self):
        # p. 13: "some permanent deformation or yielding may result as long as
        # failure critical members remain intact".
        s = _section(3, "3.3")
        assert "as long as failure critical members remain intact" in s["body"]
        assert "members must remain intact" not in _all_text(s)


class TestChapter4:
    def test_4_1_alpha_090_list_is_printed(self):
        # p. 17: 4.1.1.1 normally submerged HSS hard to inspect (Tainter valves,
        # vertical lift gate leaves) and 4.1.1.2 brackish water or seawater.
        s = _section(4, "4.1")
        assert "sum(gamma_i*Q_ni) <= alpha*phi*R_n (Equation 4.1)" in s["body"]
        assert "Examples of this type of HSS include Tainter valves and leaves of vertical lift gates" in s["body"]
        assert "4.1.1.2. For HSS in brackish water or seawater." in s["body"]
        assert "source gap" not in _all_text(s)

    def test_4_2_impact_not_on_skin_plates_and_barge_risk(self):
        # p. 21-22: impact loads need not be applied to skin plates; barge
        # impact loads should be determined through risk assessment.
        s = _section(4, "4.2")
        assert "These loads need not be applied to the design of skin plates." in s["body"]
        assert "design barge impact loads should be determined through risk assessment" in s["body"]
        assert "5,000 lbs/ft" in s["body"]

    def test_4_2_3_hydrostatic_principal_load(self):
        # p. 19: principal hydrostatic design water levels must create the
        # maximum loading that is geometrically and hydrologically possible.
        s = _section(4, "4.2.3")
        assert "geometrically and hydrologically possible" in s["body"]
        assert "treated as a temporary load" in s["body"]

    def test_4_3_equation_4_2_and_companion_rule(self):
        # p. 23-24: Equation 4.2; Ld not a companion when the principal load is dynamic.
        s = _section(4, "4.3")
        assert "U = sum(gamma_p*Lp) + gamma_pr*Lpr + sum(gamma_c*Lt_c) + gamma_c*Ld_c (Equation 4.2)" in s["body"]
        assert "Ld is not included as a companion load when the principal load is a dynamic load." in s["body"]
        assert "Earthquake EQ NA; NA; NA; 1.5; 1.0 or 1.25 (6)" in s["body"]

    def test_4_4_equations_4_3_to_4_9(self):
        # p. 28-32: Westergaard with 7/8; Eq 4.4 with C = 0.75; Eq 4.6 printed
        # without C; Eqs 4.7-4.9 earthquake combinations.
        s = _section(4, "4.4")
        b = s["body"]
        assert "p = (7/8)*gamma_w*a_c*sqrt(H*y) (Equation 4.3)" in b
        assert "a_c = C*[(S_A(T1, zeta)*Gamma~ - PGA)*phi(z) + PGA] (Equation 4.4)" in b
        assert "C = Pseudo Static Correction Factor = 0.75" in b
        assert "phi(z) = 23.41*sin^2(2*pi*z/(32.18*H_s) + 0.0122) (Equation 4.5)" in b
        assert "a_c = [S_A(T1, zeta)*Gamma~ - PGA]*23.41*sin^2(2*pi*z/(32.18*H_s) + 0.0122) + PGA (Equation 4.6)" in b
        assert "U = sum(gamma_p*Lp) + 1.5*EQ + gamma_c*Lt_c (Equation 4.7)" in b
        assert "U = sum(gamma_p*Lp) + 1.25*EQ + gamma_c*Lt_c (Equation 4.8)" in b
        assert "U = sum(gamma_p*Lp) + 1.0*EQ + 1.0*Lt (Equation 4.9)" in b
        assert "For standard and site-specific OBE ground motion analysis" in b


class TestChapter5:
    def test_5_1_infinite_life_alternative(self):
        # p. 34: load factor 2.0 on the stress magnitude, or the maximum
        # operational load with 1.0; the lesser can be used; 100-year limit.
        s = _section(5, "5.1")
        assert "apply a load factor of 2.0 to the stress magnitude defined in paragraph 5.1.3" in s["body"]
        assert "The lesser of these factored loads can be used for design." in s["body"]
        assert "100-year average annual return period" in s["body"]

    def test_5_2_ninety_percent_of_yield_keeps_should(self):
        # p. 35: "in no case should the resulting stresses exceed 90% of yield".
        s = _section(5, "5.2")
        assert "in no case should the resulting stresses exceed 90% of yield" in s["body"]


class TestChapter6:
    def test_6_1_3_slip_critical_includes_category_b(self):
        # p. 40: slip-critical also required for connections designed as
        # fatigue category B; lifting lugs, dogging brackets, gudgeon anchorages.
        s = _section(6, "6.1.3")
        assert "fatigue category B connection" in s["body"]
        assert "lifting lugs, dogging brackets, or gudgeon anchorages" in s["body"]

    def test_6_1_aws_d11_may_be_used(self):
        # p. 38: "AWS D1.1 may be used on redundant, non-cyclically loaded HSS".
        s = _section(6, "6.1")
        assert "AWS D1.1 may be used on redundant, non-cyclically loaded HSS" in s["body"]
        assert "may be used only on" not in _all_text(s)
