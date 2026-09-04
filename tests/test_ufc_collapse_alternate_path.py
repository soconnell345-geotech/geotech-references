"""Tests for geotech_references.ufc_collapse.alternate_path (Section 3-2).

Anchors are labeled by type:
  - WORKED EXAMPLE: reproduces a numeric result from an Appendix's printed
    worked example (Appendix E Table E-3 for the LIF anchors here).
  - PRINTED VALUE / PRINTED TABLE: reproduces a value stated directly in
    the printed text or table.
  - SELF-CONSISTENCY: checks internal logic rather than an external anchor.
"""

import pytest

from geotech_references.ufc_collapse.alternate_path import (
    lrfd_strength_check,
    removed_column_extent,
    removed_wall_extent,
    required_removal_stories,
    adjacent_element_removal_trigger,
    irregularity_check,
    lsp_applicable,
    dcr,
    deformation_controlled_load_lsp,
    gravity_load_away_from_removal,
    force_controlled_load_lsp,
    nonlinear_static_load,
    table_3_4_load_increase_factor,
    table_3_5_dynamic_increase_factor,
    deformation_controlled_capacity_check,
    force_controlled_capacity_check,
    classify_action,
)


class TestLrfdStrengthCheck:
    def test_equation_3_8(self):
        r = lrfd_strength_check(phi=0.9, rn=100, ru=80)
        assert r["adequate"] is True
        assert r["design_strength"] == pytest.approx(90)


class TestRemovalExtent:
    def test_column_full_clear_height(self):
        r = removed_column_extent(12)
        assert r["removed_height"] == 12

    def test_wall_prescribed_always_2h(self):
        r = removed_wall_extent(clear_story_height=10, option="prescribed")
        assert r["removed_length"] == 20

    def test_wall_deficient_shorter_than_2h(self):
        r = removed_wall_extent(clear_story_height=10, deficient_wall_length=15, option="deficient_tie")
        assert r["removed_length"] == 15

    def test_wall_deficient_longer_than_2h(self):
        r = removed_wall_extent(clear_story_height=10, deficient_wall_length=25, option="deficient_tie")
        assert r["removed_length"] == 20

    def test_deficient_requires_length(self):
        with pytest.raises(ValueError):
            removed_wall_extent(clear_story_height=10, option="deficient_tie")


class TestRemovalLocations:
    def test_four_required_stories(self):
        r = required_removal_stories()
        assert len(r["stories"]) == 4
        assert "first story above grade" in r["stories"][0]

    def test_thirty_percent_trigger(self):
        # PRINTED VALUE: within 30% of the bay dimension triggers
        # simultaneous removal.
        r = adjacent_element_removal_trigger(distance=5, reference_dimension=20)
        assert r["triggers_simultaneous_removal"] is True
        r2 = adjacent_element_removal_trigger(distance=7, reference_dimension=20)
        assert r2["triggers_simultaneous_removal"] is False


class TestIrregularityAndLsp:
    def test_regular_structure_no_conditions(self):
        r = irregularity_check()
        assert r["is_irregular"] is False
        assert r["triggered_conditions"] == []

    def test_one_condition_triggers_irregular(self):
        r = irregularity_check(has_asymmetric_bay_stiffness=True)
        assert r["is_irregular"] is True
        assert r["triggered_conditions"] == [2]

    def test_lsp_always_ok_if_regular(self):
        r = lsp_applicable(is_irregular=False)
        assert r["lsp_permitted"] is True

    def test_lsp_gated_by_dcr_if_irregular(self):
        assert lsp_applicable(is_irregular=True, max_dcr=1.5)["lsp_permitted"] is True
        assert lsp_applicable(is_irregular=True, max_dcr=2.5)["lsp_permitted"] is False

    def test_irregular_requires_dcr(self):
        with pytest.raises(ValueError):
            lsp_applicable(is_irregular=True)

    def test_equation_3_9_dcr(self):
        r = dcr(q_udlim=150, q_ce=100)
        assert r["dcr"] == pytest.approx(1.5)


class TestLoadCombinations:
    def test_equation_3_10_deformation_controlled(self):
        r = deformation_controlled_load_lsp(omega_ld=2.72, d=100, l=50)
        expected = 2.72 * (1.2 * 100 + 0.5 * 50)
        assert r["gld"] == pytest.approx(expected)

    def test_equation_3_11_gravity_away(self):
        r = gravity_load_away_from_removal(d=100, l=50)
        assert r["g"] == pytest.approx(1.2 * 100 + 0.5 * 50)

    def test_equation_3_11_snow_alternative(self):
        # SELF-CONSISTENCY: snow load uses the 0.2S term instead of 0.5L
        r = gravity_load_away_from_removal(d=100, s=40)
        assert r["g"] == pytest.approx(1.2 * 100 + 0.2 * 40)

    def test_equation_3_12_force_controlled(self):
        r = force_controlled_load_lsp(omega_lf=2.0, d=100, l=50)
        expected = 2.0 * (1.2 * 100 + 0.5 * 50)
        assert r["glf"] == pytest.approx(expected)

    def test_equation_3_15_nonlinear_static(self):
        r = nonlinear_static_load(omega_n=1.3, d=100, l=50)
        expected = 1.3 * (1.2 * 100 + 0.5 * 50)
        assert r["gn"] == pytest.approx(expected)


class TestTable34LoadIncreaseFactor:
    def test_steel_framed_worked_example_1(self):
        # WORKED EXAMPLE: Appendix E Table E-3 (printed p. 138), column
        # removal 1: mLIF=1.8 -> Omega_LD=0.9*1.8+1.1=2.72.
        r = table_3_4_load_increase_factor("steel", "framed", m_lif=1.8)
        assert r["omega_ld"] == pytest.approx(2.72, abs=0.005)
        assert r["omega_lf"] == 2.0

    def test_steel_framed_worked_example_2_and_3(self):
        # WORKED EXAMPLE: Appendix E Table E-3, column removals 2 and 3:
        # mLIF=1.79 -> Omega_LD=0.9*1.79+1.1=2.711 (printed as 2.71).
        r = table_3_4_load_increase_factor("steel", "framed", m_lif=1.79)
        assert r["omega_ld"] == pytest.approx(2.711, abs=0.001)

    def test_rc_framed_formula(self):
        # PRINTED TABLE: RC framed Omega_LD = 1.2*mLIF + 0.80
        r = table_3_4_load_increase_factor("reinforced_concrete", "framed", m_lif=5)
        assert r["omega_ld"] == pytest.approx(1.2 * 5 + 0.80)

    def test_load_bearing_wall_formula_all_materials(self):
        # PRINTED TABLE: load-bearing wall Omega_LD = 2.0*mLIF for RC,
        # masonry, wood, and cold-formed steel.
        for material in ("reinforced_concrete", "masonry", "wood", "cold_formed_steel"):
            r = table_3_4_load_increase_factor(material, "load_bearing_wall", m_lif=3)
            assert r["omega_ld"] == pytest.approx(6.0)
            assert r["omega_lf"] == 2.0

    def test_unknown_combination_raises(self):
        with pytest.raises(ValueError):
            table_3_4_load_increase_factor("masonry", "framed", m_lif=3)


class TestTable35DynamicIncreaseFactor:
    def test_steel_framed_matches_figure_c7_fit(self):
        # PRINTED VALUE: the steel DIF equation reproduces Figure C-7's
        # own printed recommended equation exactly.
        r = table_3_5_dynamic_increase_factor("steel", "framed", theta_pra=0.05, theta_y=0.01)
        ratio = 0.05 / 0.01
        assert r["omega_n"] == pytest.approx(1.08 + 0.76 / (ratio + 0.83))

    def test_rc_framed_formula(self):
        r = table_3_5_dynamic_increase_factor("reinforced_concrete", "framed", theta_pra=0.03, theta_y=0.01)
        ratio = 0.03 / 0.01
        assert r["omega_n"] == pytest.approx(1.04 + 0.45 / (ratio + 0.48))

    def test_load_bearing_wall_fixed_at_2(self):
        # PRINTED TABLE: all load-bearing wall structures use Omega_N=2
        for material in ("reinforced_concrete", "masonry", "wood", "cold_formed_steel"):
            r = table_3_5_dynamic_increase_factor(material, "load_bearing_wall")
            assert r["omega_n"] == 2.0

    def test_framed_requires_rotation_inputs(self):
        with pytest.raises(ValueError):
            table_3_5_dynamic_increase_factor("steel", "framed")


class TestAcceptanceCriteria:
    def test_equation_3_13_deformation_controlled(self):
        r = deformation_controlled_capacity_check(phi=0.9, m=6, q_ce=100, q_ud=500)
        assert r["capacity"] == pytest.approx(540)
        assert r["adequate"] is True

    def test_equation_3_14_force_controlled(self):
        r = force_controlled_capacity_check(phi=0.75, q_cl=200, q_uf=140)
        assert r["capacity"] == pytest.approx(150)
        assert r["adequate"] is True

    def test_equation_3_14_inadequate(self):
        r = force_controlled_capacity_check(phi=0.75, q_cl=100, q_uf=140)
        assert r["adequate"] is False


class TestClassifyAction:
    def test_primary_deformation_controlled(self):
        r = classify_action(curve_type=1, e_over_g=3, is_primary=True)
        assert r["classification"] == "deformation_controlled"

    def test_primary_force_controlled_low_e_g(self):
        r = classify_action(curve_type=1, e_over_g=1, is_primary=True)
        assert r["classification"] == "force_controlled"

    def test_primary_type_3_always_force_controlled(self):
        r = classify_action(curve_type=3, e_over_g=10, is_primary=True)
        assert r["classification"] == "force_controlled"

    def test_secondary_type_1_always_deformation_controlled(self):
        # SELF-CONSISTENCY: secondary Type 1 is deformation-controlled
        # regardless of e/g (unlike primary, which needs e/g>=2)
        r = classify_action(curve_type=1, e_over_g=0.5, is_primary=False)
        assert r["classification"] == "deformation_controlled"

    def test_secondary_type_2_needs_e_over_g(self):
        r_low = classify_action(curve_type=2, e_over_g=1, is_primary=False)
        r_high = classify_action(curve_type=2, e_over_g=3, is_primary=False)
        assert r_low["classification"] == "force_controlled"
        assert r_high["classification"] == "deformation_controlled"

    def test_invalid_curve_type_raises(self):
        with pytest.raises(ValueError):
            classify_action(curve_type=4, e_over_g=3, is_primary=True)
