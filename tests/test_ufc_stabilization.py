"""Tests for UFC 3-250-11 (Soil Stabilization and Modification for Pavements)
table and equation lookup functions."""

import pytest

from geotech_references.ufc_stabilization.tables import (
    table_2_1_min_ucs_requirements,
    table_2_2_durability_requirements,
    table_2_3_additive_selection_guide,
    table_3_1_cement_gradation,
    table_3_2_cement_content_by_soil,
    table_3_3_bituminous_subgrade_gradation,
    table_3_4_bituminous_base_subbase_gradation,
    table_3_5_emulsified_asphalt_requirements,
    table_3_6_swell_potential,
    table_a1_equivalency_factors,
)
from geotech_references.ufc_stabilization.equations import (
    equation_cement_content_modifying_soils,
    equation_cement_pi_limit_table_2_3,
    equation_cutback_asphalt_content_estimate,
    equation_gravimetric_percent_so4,
    equation_oven_dry_weight_from_air_dry,
    equation_stabilized_equivalent_thickness,
    equation_turbidimetric_percent_so4,
)


# ============================================================================
# Table 2-1: Minimum UCS requirements
# ============================================================================

class TestTable21:
    def test_base_flexible(self):
        r = table_2_1_min_ucs_requirements("base", "flexible")
        assert r["min_ucs_psi"] == 750
        assert r["min_ucs_mpa"] == 5.17

    def test_base_rigid(self):
        r = table_2_1_min_ucs_requirements("base", "rigid")
        assert r["min_ucs_psi"] == 500

    def test_subbase_flexible(self):
        r = table_2_1_min_ucs_requirements("subbase_or_subgrade", "flexible")
        assert r["min_ucs_psi"] == 250

    def test_subbase_rigid(self):
        r = table_2_1_min_ucs_requirements("subbase_or_subgrade", "rigid")
        assert r["min_ucs_psi"] == 200
        assert r["min_ucs_mpa"] == 1.38

    def test_invalid_layer(self):
        with pytest.raises(ValueError):
            table_2_1_min_ucs_requirements("nonexistent", "flexible")

    def test_invalid_pavement_type(self):
        with pytest.raises(ValueError):
            table_2_1_min_ucs_requirements("base", "nonexistent")


# ============================================================================
# Table 2-2: Durability requirements
# ============================================================================

class TestTable22:
    def test_granular_pi_lt_10(self):
        assert table_2_2_durability_requirements("granular_pi_lt_10")["max_weight_loss_pct"] == 11

    def test_granular_pi_gt_10(self):
        assert table_2_2_durability_requirements("granular_pi_gt_10")["max_weight_loss_pct"] == 8

    def test_silt(self):
        assert table_2_2_durability_requirements("silt")["max_weight_loss_pct"] == 8

    def test_clay(self):
        assert table_2_2_durability_requirements("clay")["max_weight_loss_pct"] == 6

    def test_invalid_soil_type(self):
        with pytest.raises(ValueError):
            table_2_2_durability_requirements("nonexistent")


# ============================================================================
# Table 2-3: Guide for selecting a stabilizing additive
# ============================================================================

class TestTable23:
    def test_area_1c_matches_worked_example(self):
        # Sec 2-1.5.2 worked example: SC soil, 25% passing No.200, 68% sand -> area 1-C.
        r = table_2_3_additive_selection_guide("1c")
        assert "SC" in r["uscs_classes"]
        assert "Portland cement and fiber (a)" in r["stabilizers"]

    def test_area_3_organic_note(self):
        r = table_2_3_additive_selection_guide("3")
        assert "CH" in r["uscs_classes"]
        assert "not susceptible" in r["remark"]

    def test_area_normalization(self):
        r1 = table_2_3_additive_selection_guide("2A")
        r2 = table_2_3_additive_selection_guide(" 2-a ")
        assert r1["uscs_classes"] == r2["uscs_classes"]

    def test_all_areas_resolve(self):
        for area in ("1a", "1b", "1c", "2a", "2b", "2c", "3"):
            r = table_2_3_additive_selection_guide(area)
            assert r["stabilizers"]

    def test_invalid_area(self):
        with pytest.raises(ValueError):
            table_2_3_additive_selection_guide("9z")


# ============================================================================
# Table 3-1: Cement gradation (base/subbase)
# ============================================================================

class TestTable31:
    def test_base_full_envelope(self):
        r = table_3_1_cement_gradation("base")
        assert r["gradation"]["no200"] == "0-20"

    def test_base_single_sieve(self):
        r = table_3_1_cement_gradation("base", "no40")
        assert r["percent_passing_range"] == "10-40"

    def test_subbase_single_sieve(self):
        r = table_3_1_cement_gradation("subbase", "no4")
        assert r["percent_passing_range"] == "45-100"

    def test_subbase_has_no_0_75in_check(self):
        with pytest.raises(ValueError):
            table_3_1_cement_gradation("subbase", "0.75in")

    def test_invalid_course_type(self):
        with pytest.raises(ValueError):
            table_3_1_cement_gradation("nonexistent")

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_3_1_cement_gradation("base", "nonexistent")


# ============================================================================
# Table 3-2: Cement content by USCS class
# ============================================================================

class TestTable32:
    def test_gw_sw(self):
        assert table_3_2_cement_content_by_soil("GW")["initial_cement_content_pct"] == 5
        assert table_3_2_cement_content_by_soil("SW")["initial_cement_content_pct"] == 5

    def test_gp_group(self):
        assert table_3_2_cement_content_by_soil("GP")["initial_cement_content_pct"] == 6

    def test_sc_group(self):
        assert table_3_2_cement_content_by_soil("SC")["initial_cement_content_pct"] == 7

    def test_cl_group(self):
        assert table_3_2_cement_content_by_soil("CL")["initial_cement_content_pct"] == 9

    def test_ch(self):
        assert table_3_2_cement_content_by_soil("CH")["initial_cement_content_pct"] == 11

    def test_invalid_class(self):
        with pytest.raises(ValueError):
            table_3_2_cement_content_by_soil("ZZ")


# ============================================================================
# Table 3-3: Bituminous subgrade gradation
# ============================================================================

class TestTable33:
    def test_full_envelope(self):
        r = table_3_3_bituminous_subgrade_gradation()
        assert r["gradation"]["no200"] == "2-30"

    def test_single_sieve(self):
        r = table_3_3_bituminous_subgrade_gradation("no30")
        assert r["percent_passing_range"] == "38-100"

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_3_3_bituminous_subgrade_gradation("nonexistent")


# ============================================================================
# Table 3-4: Bituminous base/subbase gradation
# ============================================================================

class TestTable34:
    def test_1_5in_no4(self):
        r = table_3_4_bituminous_base_subbase_gradation("1.5in", "no4")
        assert r["percent_passing_nominal"] == 45
        assert r["tolerance_pct"] == 9

    def test_not_applicable_cell(self):
        r = table_3_4_bituminous_base_subbase_gradation("0.5in", "1.5in")
        assert r["range"] == "not applicable"

    def test_exact_100_cell(self):
        r = table_3_4_bituminous_base_subbase_gradation("1in", "1in")
        assert r["range"] == "100"

    def test_full_envelope(self):
        r = table_3_4_bituminous_base_subbase_gradation("0.75in")
        assert r["gradation"]["no200"] == "5 +/- 2"

    def test_invalid_max_size(self):
        with pytest.raises(ValueError):
            table_3_4_bituminous_base_subbase_gradation("nonexistent")

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_3_4_bituminous_base_subbase_gradation("1in", "nonexistent")


# ============================================================================
# Table 3-5: Emulsified asphalt requirements
# ============================================================================

class TestTable35:
    def test_exact_row_col(self):
        r = table_3_5_emulsified_asphalt_requirements(0, 100)
        assert r["emulsified_asphalt_lb_per_100lb"] == pytest.approx(7.2)

    def test_interpolated_row(self):
        r = table_3_5_emulsified_asphalt_requirements(9, "<50")
        # Between row 8 (7.0) and row 10 (7.2) for the lt_50 column.
        assert r["emulsified_asphalt_lb_per_100lb"] == pytest.approx(7.1)

    def test_lt_50_numeric(self):
        r = table_3_5_emulsified_asphalt_requirements(0, 40)
        assert r["percent_passing_no10_column"] == "lt_50"

    def test_peak_at_row_12(self):
        # Table 3-5 is a "hump" shape peaking at percent_passing_200=12.
        r10 = table_3_5_emulsified_asphalt_requirements(10, 100)
        r12 = table_3_5_emulsified_asphalt_requirements(12, 100)
        r14 = table_3_5_emulsified_asphalt_requirements(14, 100)
        assert r12["emulsified_asphalt_lb_per_100lb"] > r10["emulsified_asphalt_lb_per_100lb"]
        assert r12["emulsified_asphalt_lb_per_100lb"] > r14["emulsified_asphalt_lb_per_100lb"]

    def test_invalid_no10_column(self):
        with pytest.raises(ValueError):
            table_3_5_emulsified_asphalt_requirements(10, 65)


# ============================================================================
# Table 3-6: Swell potential
# ============================================================================

class TestTable36:
    def test_high_swell(self):
        r = table_3_6_swell_potential(65, 40)
        assert r["potential_swell"] == "high"

    def test_low_swell(self):
        r = table_3_6_swell_potential(30, 10)
        assert r["potential_swell"] == "low"

    def test_marginal_swell(self):
        r = table_3_6_swell_potential(55, 28)
        assert r["potential_swell"] == "marginal"

    def test_conservative_governs_on_disagreement(self):
        # High LL but low PI: the more severe category should govern.
        r = table_3_6_swell_potential(65, 10)
        assert r["ll_category"] == "high"
        assert r["pi_category"] == "low"
        assert r["potential_swell"] == "high"


# ============================================================================
# Table A-1: Equivalency factors
# ============================================================================

class TestTableA1:
    def test_cement_gp_matches_example_1(self):
        # Appendix A Example 1: cement-stabilized GP, base factor 1.15.
        r = table_a1_equivalency_factors("cement", "gp")
        assert r["base_factor"] == 1.15
        assert r["subbase_factor"] == 2.30

    def test_asphalt_all_bituminous_concrete_matches_example_2(self):
        r = table_a1_equivalency_factors("asphalt", "all_bituminous_concrete")
        assert r["base_factor"] == 1.15
        assert r["subbase_factor"] == 2.30

    def test_base_not_applicable(self):
        r = table_a1_equivalency_factors("cement", "sc")
        assert r["base_factor"] is None
        assert r["subbase_factor"] == 1.50

    def test_lime_group(self):
        r = table_a1_equivalency_factors("lime", "gm")
        assert r["subbase_factor"] == 1.10

    def test_unbound_crushed_stone(self):
        r = table_a1_equivalency_factors("unbound", "crushed_stone")
        assert r["base_factor"] == 1.00
        assert r["subbase_factor"] == 2.00

    def test_invalid_stabilizer_type(self):
        with pytest.raises(ValueError):
            table_a1_equivalency_factors("nonexistent", "gp")

    def test_invalid_soil_class_for_type(self):
        with pytest.raises(ValueError):
            table_a1_equivalency_factors("cement", "all_bituminous_concrete")


# ============================================================================
# Equation: cement content for modifying soils (A = 100*B*C)
# ============================================================================

class TestEquationCementContentModifyingSoils:
    def test_task_worked_check(self):
        r = equation_cement_content_modifying_soils(0.60, 0.08)
        assert r["design_cement_content_pct"] == pytest.approx(4.8)

    def test_equation_string_present(self):
        r = equation_cement_content_modifying_soils(0.5, 0.1)
        assert r["equation"] == "A = 100*B*C"

    def test_invalid_b_out_of_range(self):
        with pytest.raises(ValueError):
            equation_cement_content_modifying_soils(1.5, 0.1)

    def test_invalid_c_out_of_range(self):
        with pytest.raises(ValueError):
            equation_cement_content_modifying_soils(0.5, -0.1)


# ============================================================================
# Equation: cutback asphalt content estimate
# ============================================================================

class TestEquationCutbackAsphaltContentEstimate:
    def test_basic_calc(self):
        r = equation_cutback_asphalt_content_estimate(10, 20, 30, 40, 0)
        expected = (0.02 * 10 + 0.07 * 20 + 0.15 * 30 + 0.20 * 40) / 100 * 100
        assert r["cutback_asphalt_pct"] == pytest.approx(expected)

    def test_solvent_reduces_denominator_increases_result(self):
        r0 = equation_cutback_asphalt_content_estimate(10, 20, 30, 40, 0)
        r50 = equation_cutback_asphalt_content_estimate(10, 20, 30, 40, 50)
        assert r50["cutback_asphalt_pct"] > r0["cutback_asphalt_pct"]

    def test_invalid_solvent(self):
        with pytest.raises(ValueError):
            equation_cutback_asphalt_content_estimate(10, 20, 30, 40, 100)

    def test_negative_input(self):
        with pytest.raises(ValueError):
            equation_cutback_asphalt_content_estimate(-1, 20, 30, 40, 0)


# ============================================================================
# Equation: Table 2-3 footnote (c) PI limit
# ============================================================================

class TestEquationCementPiLimitTable23:
    def test_worked_narrative_example(self):
        # Sec 2-1.5.2: 25% passing No.200 -> PI limit 45; PI=9 < 45 so cement qualifies.
        r = equation_cement_pi_limit_table_2_3(25)
        assert r["pi_limit"] == 45

    def test_zero_percent_passing(self):
        r = equation_cement_pi_limit_table_2_3(0)
        assert r["pi_limit"] == 70

    def test_invalid_range(self):
        with pytest.raises(ValueError):
            equation_cement_pi_limit_table_2_3(150)


# ============================================================================
# Equation: stabilized-layer equivalent thickness
# ============================================================================

class TestEquationStabilizedEquivalentThickness:
    def test_appendix_a_example_1(self):
        r = equation_stabilized_equivalent_thickness(4, 1.15)
        assert r["stabilized_thickness_in"] == pytest.approx(3.48, abs=0.01)

    def test_appendix_a_example_2(self):
        r = equation_stabilized_equivalent_thickness(16.88, 2.30)
        assert r["stabilized_thickness_in"] == pytest.approx(7.34, abs=0.01)

    def test_invalid_thickness(self):
        with pytest.raises(ValueError):
            equation_stabilized_equivalent_thickness(0, 1.15)

    def test_invalid_factor(self):
        with pytest.raises(ValueError):
            equation_stabilized_equivalent_thickness(4, 0)


# ============================================================================
# Equation: oven-dry weight from air-dry weight
# ============================================================================

class TestEquationOvenDryWeightFromAirDry:
    def test_appendix_a_sample_calc(self):
        # Sec A-3.2.4: air-dry 10.12 g, moisture 9.36% -> printed dry weight 9.27 g.
        r = equation_oven_dry_weight_from_air_dry(10.12, 9.36)
        assert r["oven_dry_weight_g"] == pytest.approx(9.27, abs=0.02)

    def test_zero_moisture_no_change(self):
        r = equation_oven_dry_weight_from_air_dry(10.0, 0.0)
        assert r["oven_dry_weight_g"] == pytest.approx(10.0)

    def test_invalid_weight(self):
        with pytest.raises(ValueError):
            equation_oven_dry_weight_from_air_dry(0, 5)

    def test_invalid_moisture(self):
        with pytest.raises(ValueError):
            equation_oven_dry_weight_from_air_dry(10, -1)


# ============================================================================
# Equation: gravimetric percent SO4
# ============================================================================

class TestEquationGravimetricPercentSo4:
    def test_basic_calc(self):
        r = equation_gravimetric_percent_so4(0.1, 10)
        assert r["percent_so4"] == pytest.approx(0.1 / 10 * 411.6)

    def test_zero_residue(self):
        r = equation_gravimetric_percent_so4(0, 10)
        assert r["percent_so4"] == 0

    def test_invalid_residue(self):
        with pytest.raises(ValueError):
            equation_gravimetric_percent_so4(-1, 10)

    def test_invalid_oven_dry_weight(self):
        with pytest.raises(ValueError):
            equation_gravimetric_percent_so4(0.1, 0)


# ============================================================================
# Equation: turbidimetric percent SO4
# ============================================================================

class TestEquationTurbidimetricPercentSo4:
    def test_appendix_a_sample_calc(self):
        # Sec A-3.2.4: C=80.0 ppm, V=39.1 ml, W=9.27 g -> printed 0.0338 percent.
        r = equation_turbidimetric_percent_so4(80.0, 39.1, 9.27)
        assert r["percent_so4"] == pytest.approx(0.0338, abs=0.0002)

    def test_scales_linearly_with_concentration(self):
        r1 = equation_turbidimetric_percent_so4(40.0, 39.1, 9.27)
        r2 = equation_turbidimetric_percent_so4(80.0, 39.1, 9.27)
        assert r2["percent_so4"] == pytest.approx(r1["percent_so4"] * 2)

    def test_invalid_volume(self):
        with pytest.raises(ValueError):
            equation_turbidimetric_percent_so4(80.0, 0, 9.27)

    def test_invalid_dry_weight(self):
        with pytest.raises(ValueError):
            equation_turbidimetric_percent_so4(80.0, 39.1, -1)
