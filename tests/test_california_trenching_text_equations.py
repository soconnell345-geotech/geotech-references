"""Caltrans Trenching and Shoring Manual (July 2025) stored chapter text against the print.

Each test pins a printed form or statement the stored text once got wrong
(review of 2026-11-10, finding text-14 and REF-83). Pages are the printed
page numbers ("4-22"); the PDF page differs by chapter.
"""

import json

import pytest

from geotech_references._retrieval import load_chapter


def _section(chapter, section_id):
    for s in load_chapter("california_trenching", chapter)["sections"]:
        if s["section_id"] == section_id:
            return s
    raise KeyError(section_id)


def _equation(section, equation_id):
    for e in section["equations"]:
        if e["id"] == equation_id:
            return e
    raise KeyError(equation_id)


def _all_text(section):
    return json.dumps(section, ensure_ascii=False)


class TestEarthPressure:
    def test_max_slope_angle_is_the_printed_eq_4_5_1(self):
        # p. 4-22: sin(beta) <= sin(phi) + (c/l) cos(phi) (4-5-1), l from (4-5-2).
        s = _section(4, "4-5")
        assert "sin(beta) <= sin(phi) + (c/l)*cos(phi) (Eq. 4-5-1)" in s["body"]
        assert "(c/l)*cos(phi)" in _equation(s, "Eq. 4-5-1")["description"]
        # The stored text once gave c/(gamma*h), which is not printed.
        assert "c/(gamma*h)" not in _all_text(s)

    def test_eq_4_5_2_kept_as_printed_with_note(self):
        # p. 4-22 prints sigma_x + (1/2) sin(2 phi) inside the bracket.
        body = _section(4, "4-5")["body"]
        assert "[sigma_x + (1/2)*sin(2 phi) - sqrt(" in body
        assert "not dimensionally consistent" in body

    def test_eq_4_5_1_worked_value(self):
        # Made-up values: phi 30 deg, c/l = 0.1 gives sin(beta) <= 0.5 + 0.1*0.866.
        import math
        phi = math.radians(30.0)
        assert math.sin(phi) + 0.1 * math.cos(phi) == pytest.approx(0.58660, rel=1e-4)

    def test_tension_crack_depth_printed_form(self):
        # p. 4-19: hcr = 2c sqrt(Ka)/(gamma Ka) (4-4-13).
        s = _section(4, "4-4")
        assert "2c*sqrt(Ka)/(gamma*Ka)" in _equation(s, "Eq. 4-4-13")["description"]

    def test_rankine_passive_force_word(self):
        # p. 4-12: "one should not use the Rankine method ... when beta > 0".
        s = _section(4, "4-3")
        assert "must NOT" not in _all_text(s)
        assert "should not use the Rankine method" in s["body"]

    def test_log_spiral_section_is_for_granular_soils(self):
        # p. 4-28: Kp "in granular soils can be accomplished using the chart in Figure 4-20".
        s = _section(4, "4-6")
        assert "granular soils" in s["applicability"]
        assert "trial wedge" in s["body"]


class TestSoilsAndSlopes:
    def test_type_c_fallback_not_printed(self):
        # pp. 2-10, 2-11 print no default slope for unclassified soil.
        kps = " ".join(_section(2, "2-3.04")["key_points"])
        assert "fallback" not in kps.lower()

    def test_su_equals_qu_over_2_not_in_3_7(self):
        # pp. 3-10, 3-11: Section 3-7 prints no Su = qu/2 relation.
        s = _section(3, "3-7")
        assert "qu / 2" not in _all_text(s)
        assert "Extreme caution" not in s["body"]

    def test_cohesion_submittal_conditions_in_3_6(self):
        # p. 3-10: three conditions recommended with each submittal using c.
        body = _section(3, "3-6")["body"]
        assert "prevent tension cracks" in body
        assert "consistent and homogeneous" in body

    def test_cpt_figures_attributed_to_3_5(self):
        # pp. 3-7, 3-8: Figures 3-1 and 3-2 are printed in Section 3-5.
        figs = " ".join(_section(3, "3-6")["figures"])
        assert "Section 3-5" in figs


class TestSurchargeAndStructure:
    def test_minimum_surcharge_depth_wording(self):
        # p. 5-2: 72 psf applied to a minimum depth of 10 ft (Hs) below the uppermost level.
        e = _equation(_section(5, "5-1.01"), "Minimum construction surcharge")
        assert "minimum depth of 10 ft (Hs) below the" in e["description"]

    def test_timber_reference_is_falsework_manual(self):
        # p. 6-2: timber analysis references the Falsework Manual, Chapter 5.
        s = _section(6, "6-2")
        assert "NDS, 2018" not in _all_text(s)
        assert "Falsework Manual, Chapter 5" in s["body"]
        assert "AREMA manual, Chapter 7, Timber Structures" in s["body"]

    def test_deflection_calculations_required_near_railroad(self):
        # p. 7-6: deflection calculations are required adjacent to the railroad or high-risk structures.
        assert "Deflection calculations are required" in _section(7, "7-3")["body"]

    def test_twenty_percent_increase_is_simplified_method(self):
        # p. 7-11: D = 1.2 D0 belongs to the Simplified Method (7-5.02).
        s = _section(7, "7-5")
        assert "Simplified Method (Section 7-5.02)" in _equation(s, "D = 1.2*D0")["description"]
        assert "In the Rigorous Method the depth to the point of rotation" not in s["body"]

    def test_single_level_aep_eq_8_2_1(self):
        # p. 8-3: sigma_a = 1.3 x P/((2/3)H) (8-2-1).
        assert "1.3 x P/((2/3)H) (Eq. 8-2-1)" in _section(8, "8-2")["body"]

    def test_fhwa_ka_eq_8_3_4(self):
        # p. 8-6: Ka = 1 - 4cu1/(gamma H) + 2 sqrt(2)(D/H)[1 - 5.14cu2/(gamma H)] >= 0.25.
        d = _equation(_section(8, "8-3"), "Eq. 8-3-4")["description"]
        assert "5.14(cu2)" in d and "2 sqrt(2)" in d

    def test_eq_8_3_4_worked_value(self):
        # Made-up values: gamma H = 2000 psf, cu1 = 300, cu2 = 200, D/H = 0.5.
        import math
        ka = 1 - 4 * 300 / 2000 + 2 * math.sqrt(2) * 0.5 * (1 - 5.14 * 200 / 2000)
        assert ka == pytest.approx(1.0870, rel=1e-3)


class TestSpecialConditionsAndAnchors:
    def test_heave_fs_is_recommended(self):
        # p. 10-19: "it is recommended that a minimum safety factor of 1.5 should be used".
        s = _section(10, "10-3")
        assert "must be >= 1.5" not in _all_text(s)
        assert "recommended" in s["summary"]

    def test_slope_failure_exception_attributed_to_10_1(self):
        # p. 10-2 (Section 10-1): two-sided systems in level ground are the exception.
        kps = " ".join(_section(10, "10-5")["key_points"])
        assert "(Section 10-1)" in kps

    def test_slope_stability_eq_10_5_1(self):
        # p. 10-28: FS = [C L + tan(phi) sum N_i]/sum(W_i sin theta_i).
        d = _equation(_section(10, "10-5"), "Eq. 10-5-1")["description"]
        assert "C_bar*L + tan(phi_bar)*sum(N_bar_i)" in d

    def test_shim_thickness_as_printed(self):
        # p. 11-17: tshim = (Pproof - Plockoff) Lu'/(AE) - Delta_L (11-3-4).
        s = _section(11, "11-3.07")
        assert "(Pproof - Plockoff)*Lu'/(A*E) - Delta_L" in _equation(s, "Eq. 11-3-4")["description"]
        assert "stored as printed" in s["body"]

    def test_creep_formulas_printed_in_11_3_05c(self):
        # pp. 11-15, 11-16: Eqs. 11-3-1 to 11-3-3 are in 11-3.05C; 11-3.10 holds the examples.
        assert "Delta_2-3 = C*[log10(T3/T2)] (Eq. 11-3-1)" in _section(11, "11-3.05")["body"]
        s = _section(11, "11-3.10")
        assert "11-3.05C" in _equation(s, "Eq. 11-3-1")["description"]
        assert "Example '10-1B' as printed" in s["body"]

    def test_creep_example_values(self):
        # p. 11-20: C = 0.1/log10(10/1) = 0.1; Delta = 0.1 log10(525,600/10) = 0.47.
        import math
        assert 0.1 * math.log10(525600 / 10) == pytest.approx(0.47, abs=0.005)

    def test_culmann_wedge_weight(self):
        # p. A-19: W = ABDEFA_area(gamma) + q(l) + V, l = length of surcharge (Figure A-16).
        d = _equation(_section(12, "12-3"), "Eq. A-3-1")["description"]
        assert "q(l)" in d and "length of surcharge" in d
