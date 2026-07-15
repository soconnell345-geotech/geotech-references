"""Tests for Eurocode 7 (EN 1997-1:2004) table and equation functions."""

import math

import pytest

from geotech_references.eurocode_7_1.tables import (
    table_a_1_equ_actions,
    table_a_2_equ_soil_parameters,
    table_a_3_str_geo_actions,
    table_a_4_str_geo_soil_parameters,
    table_a_5_spread_foundation_resistance,
    table_a_6_driven_pile_resistance,
    table_a_7_bored_pile_resistance,
    table_a_8_cfa_pile_resistance,
    table_a_9_correlation_static_load_test,
    table_a_10_correlation_ground_test,
    table_a_11_correlation_dynamic_impact_test,
    table_a_12_anchorage_resistance,
    table_a_13_retaining_structure_resistance,
    table_a_14_slope_stability_resistance,
    table_a_15_upl_actions,
    table_a_16_upl_soil_resistance,
    table_a_17_hyd_actions,
    design_approach_sets,
    table_g_1_rock_group,
    table_h_1_limiting_relative_rotation,
    table_h_2_limiting_total_settlement,
)
from geotech_references.eurocode_7_1.equations import (
    active_earth_pressure,
    passive_earth_pressure,
    cohesion_earth_pressure_coefficient,
    mobilised_wall_angle_mw,
    weight_density_coefficient,
    undrained_bearing_resistance,
    bearing_capacity_factors,
    drained_bearing_resistance,
    pressuremeter_bearing_resistance,
    adjusted_elasticity_settlement,
)


# ============================================================================
# Table A.1: EQU partial factors on actions
# ============================================================================

class TestTableA1:
    def test_permanent_unfavourable(self):
        assert table_a_1_equ_actions("permanent", "unfavourable") == 1.1

    def test_permanent_favourable(self):
        assert table_a_1_equ_actions("permanent", "favourable") == 0.9

    def test_variable_unfavourable(self):
        assert table_a_1_equ_actions("variable", "unfavourable") == 1.5

    def test_variable_favourable(self):
        assert table_a_1_equ_actions("variable", "favourable") == 0.0

    def test_case_insensitive(self):
        assert table_a_1_equ_actions("PERMANENT", "UNFAVOURABLE") == 1.1

    def test_invalid_action(self):
        with pytest.raises(ValueError):
            table_a_1_equ_actions("temporary", "unfavourable")


# ============================================================================
# Table A.2: EQU partial factors for soil parameters
# ============================================================================

class TestTableA2:
    def test_phi(self):
        assert table_a_2_equ_soil_parameters("phi") == 1.25

    def test_c(self):
        assert table_a_2_equ_soil_parameters("c") == 1.25

    def test_cu(self):
        assert table_a_2_equ_soil_parameters("cu") == 1.4

    def test_qu(self):
        assert table_a_2_equ_soil_parameters("qu") == 1.4

    def test_gamma(self):
        assert table_a_2_equ_soil_parameters("gamma") == 1.0

    def test_aliases(self):
        assert table_a_2_equ_soil_parameters("phi'") == 1.25
        assert table_a_2_equ_soil_parameters("friction_angle") == 1.25
        assert table_a_2_equ_soil_parameters("effective_cohesion") == 1.25
        assert table_a_2_equ_soil_parameters("undrained_shear_strength") == 1.4
        assert table_a_2_equ_soil_parameters("unit_weight") == 1.0

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_a_2_equ_soil_parameters("nonsense")


# ============================================================================
# Table A.3: STR/GEO partial factors on actions, sets A1/A2
# ============================================================================

class TestTableA3:
    def test_a1_permanent_unfavourable(self):
        assert table_a_3_str_geo_actions("permanent", "unfavourable", "A1") == 1.35

    def test_a1_permanent_favourable(self):
        assert table_a_3_str_geo_actions("permanent", "favourable", "A1") == 1.0

    def test_a1_variable_unfavourable(self):
        assert table_a_3_str_geo_actions("variable", "unfavourable", "A1") == 1.5

    def test_a1_variable_favourable(self):
        assert table_a_3_str_geo_actions("variable", "favourable", "A1") == 0.0

    def test_a2_permanent_unfavourable(self):
        assert table_a_3_str_geo_actions("permanent", "unfavourable", "A2") == 1.0

    def test_a2_permanent_favourable(self):
        assert table_a_3_str_geo_actions("permanent", "favourable", "A2") == 1.0

    def test_a2_variable_unfavourable(self):
        assert table_a_3_str_geo_actions("variable", "unfavourable", "A2") == 1.3

    def test_a2_variable_favourable(self):
        assert table_a_3_str_geo_actions("variable", "favourable", "A2") == 0.0

    def test_default_set_a1(self):
        assert table_a_3_str_geo_actions("permanent", "unfavourable") == 1.35

    def test_invalid_set(self):
        with pytest.raises(ValueError):
            table_a_3_str_geo_actions("permanent", "unfavourable", "A3")


# ============================================================================
# Table A.4: STR/GEO partial factors for soil parameters, sets M1/M2
# ============================================================================

class TestTableA4:
    def test_m1_all_unity(self):
        for p in ("phi", "c", "cu", "qu", "gamma"):
            assert table_a_4_str_geo_soil_parameters(p, "M1") == 1.0

    def test_m2_phi(self):
        assert table_a_4_str_geo_soil_parameters("phi", "M2") == 1.25

    def test_m2_c(self):
        assert table_a_4_str_geo_soil_parameters("c", "M2") == 1.25

    def test_m2_cu(self):
        assert table_a_4_str_geo_soil_parameters("cu", "M2") == 1.4

    def test_m2_qu(self):
        assert table_a_4_str_geo_soil_parameters("qu", "M2") == 1.4

    def test_m2_gamma(self):
        assert table_a_4_str_geo_soil_parameters("gamma", "M2") == 1.0

    def test_invalid_set(self):
        with pytest.raises(ValueError):
            table_a_4_str_geo_soil_parameters("phi", "M3")


# ============================================================================
# Table A.5: Spread foundation resistance factors R1-R3
# ============================================================================

class TestTableA5:
    def test_bearing(self):
        assert table_a_5_spread_foundation_resistance("bearing", "R1") == 1.0
        assert table_a_5_spread_foundation_resistance("bearing", "R2") == 1.4
        assert table_a_5_spread_foundation_resistance("bearing", "R3") == 1.0

    def test_sliding(self):
        assert table_a_5_spread_foundation_resistance("sliding", "R1") == 1.0
        assert table_a_5_spread_foundation_resistance("sliding", "R2") == 1.1
        assert table_a_5_spread_foundation_resistance("sliding", "R3") == 1.0

    def test_invalid_resistance(self):
        with pytest.raises(ValueError):
            table_a_5_spread_foundation_resistance("uplift", "R1")


# ============================================================================
# Tables A.6/A.7/A.8: Pile resistance factors
# ============================================================================

class TestTableA6DrivenPiles:
    def test_base(self):
        assert table_a_6_driven_pile_resistance("base", "R1") == 1.0
        assert table_a_6_driven_pile_resistance("base", "R2") == 1.1
        assert table_a_6_driven_pile_resistance("base", "R3") == 1.0
        assert table_a_6_driven_pile_resistance("base", "R4") == 1.3

    def test_shaft_compression(self):
        assert table_a_6_driven_pile_resistance("shaft_compression", "R1") == 1.0
        assert table_a_6_driven_pile_resistance("shaft_compression", "R4") == 1.3

    def test_total_compression(self):
        assert table_a_6_driven_pile_resistance("total_compression", "R2") == 1.1

    def test_shaft_tension(self):
        assert table_a_6_driven_pile_resistance("shaft_tension", "R1") == 1.25
        assert table_a_6_driven_pile_resistance("shaft_tension", "R2") == 1.15
        assert table_a_6_driven_pile_resistance("shaft_tension", "R3") == 1.1
        assert table_a_6_driven_pile_resistance("shaft_tension", "R4") == 1.6

    def test_aliases(self):
        assert table_a_6_driven_pile_resistance("shaft", "R1") == 1.0
        assert table_a_6_driven_pile_resistance("tension", "R4") == 1.6

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_a_6_driven_pile_resistance("nonsense", "R1")


class TestTableA7BoredPiles:
    def test_base(self):
        assert table_a_7_bored_pile_resistance("base", "R1") == 1.25
        assert table_a_7_bored_pile_resistance("base", "R2") == 1.1
        assert table_a_7_bored_pile_resistance("base", "R3") == 1.0
        assert table_a_7_bored_pile_resistance("base", "R4") == 1.6

    def test_shaft_compression(self):
        assert table_a_7_bored_pile_resistance("shaft_compression", "R1") == 1.0
        assert table_a_7_bored_pile_resistance("shaft_compression", "R2") == 1.1
        assert table_a_7_bored_pile_resistance("shaft_compression", "R3") == 1.0
        assert table_a_7_bored_pile_resistance("shaft_compression", "R4") == 1.3

    def test_total_compression(self):
        assert table_a_7_bored_pile_resistance("total_compression", "R1") == 1.15
        assert table_a_7_bored_pile_resistance("total_compression", "R2") == 1.1
        assert table_a_7_bored_pile_resistance("total_compression", "R3") == 1.0
        assert table_a_7_bored_pile_resistance("total_compression", "R4") == 1.5

    def test_shaft_tension(self):
        assert table_a_7_bored_pile_resistance("shaft_tension", "R1") == 1.25
        assert table_a_7_bored_pile_resistance("shaft_tension", "R4") == 1.6


class TestTableA8CfaPiles:
    def test_base(self):
        assert table_a_8_cfa_pile_resistance("base", "R1") == 1.1
        assert table_a_8_cfa_pile_resistance("base", "R2") == 1.1
        assert table_a_8_cfa_pile_resistance("base", "R3") == 1.0
        assert table_a_8_cfa_pile_resistance("base", "R4") == 1.45

    def test_total_compression(self):
        # CFA total/combined R4 = 1.4, distinct from driven/bored's 1.3
        assert table_a_8_cfa_pile_resistance("total_compression", "R1") == 1.1
        assert table_a_8_cfa_pile_resistance("total_compression", "R2") == 1.1
        assert table_a_8_cfa_pile_resistance("total_compression", "R3") == 1.0
        assert table_a_8_cfa_pile_resistance("total_compression", "R4") == 1.4

    def test_shaft_tension(self):
        assert table_a_8_cfa_pile_resistance("shaft_tension", "R1") == 1.25
        assert table_a_8_cfa_pile_resistance("shaft_tension", "R4") == 1.6


# ============================================================================
# Tables A.9/A.10/A.11: Pile correlation factors
# ============================================================================

class TestTableA9StaticLoadTest:
    def test_mean_n1_to_5(self):
        assert table_a_9_correlation_static_load_test("mean", 1) == 1.40
        assert table_a_9_correlation_static_load_test("mean", 2) == 1.30
        assert table_a_9_correlation_static_load_test("mean", 3) == 1.20
        assert table_a_9_correlation_static_load_test("mean", 4) == 1.10
        assert table_a_9_correlation_static_load_test("mean", 5) == 1.00

    def test_min_n1_to_5(self):
        assert table_a_9_correlation_static_load_test("min", 1) == 1.40
        assert table_a_9_correlation_static_load_test("min", 2) == 1.20
        assert table_a_9_correlation_static_load_test("min", 3) == 1.05
        assert table_a_9_correlation_static_load_test("min", 4) == 1.00
        assert table_a_9_correlation_static_load_test("min", 5) == 1.00

    def test_n_greater_than_5_caps_at_5(self):
        assert table_a_9_correlation_static_load_test("mean", 20) == 1.00

    def test_invalid_n(self):
        with pytest.raises(ValueError):
            table_a_9_correlation_static_load_test("mean", 0)

    def test_invalid_factor(self):
        with pytest.raises(ValueError):
            table_a_9_correlation_static_load_test("median", 1)


class TestTableA10GroundTest:
    def test_mean_tabulated_points(self):
        assert table_a_10_correlation_ground_test("mean", 1) == 1.40
        assert table_a_10_correlation_ground_test("mean", 2) == 1.35
        assert table_a_10_correlation_ground_test("mean", 3) == 1.33
        assert table_a_10_correlation_ground_test("mean", 4) == 1.31
        assert table_a_10_correlation_ground_test("mean", 5) == 1.29
        assert table_a_10_correlation_ground_test("mean", 7) == 1.27
        assert table_a_10_correlation_ground_test("mean", 10) == 1.25

    def test_min_tabulated_points(self):
        assert table_a_10_correlation_ground_test("min", 1) == 1.40
        assert table_a_10_correlation_ground_test("min", 2) == 1.27
        assert table_a_10_correlation_ground_test("min", 3) == 1.23
        assert table_a_10_correlation_ground_test("min", 4) == 1.20
        assert table_a_10_correlation_ground_test("min", 5) == 1.15
        assert table_a_10_correlation_ground_test("min", 7) == 1.12
        assert table_a_10_correlation_ground_test("min", 10) == 1.08

    def test_interpolation_between_points(self):
        # n=6 halfway between n=5 (1.29) and n=7 (1.27) -> 1.28
        assert table_a_10_correlation_ground_test("mean", 6) == pytest.approx(1.28)

    def test_n_greater_than_10_caps_at_10(self):
        assert table_a_10_correlation_ground_test("mean", 50) == 1.25

    def test_invalid_n(self):
        with pytest.raises(ValueError):
            table_a_10_correlation_ground_test("mean", 0)


class TestTableA11DynamicImpactTest:
    def test_mean_tabulated_points(self):
        assert table_a_11_correlation_dynamic_impact_test("mean", 2) == 1.60
        assert table_a_11_correlation_dynamic_impact_test("mean", 5) == 1.50
        assert table_a_11_correlation_dynamic_impact_test("mean", 10) == 1.45
        assert table_a_11_correlation_dynamic_impact_test("mean", 15) == 1.42
        assert table_a_11_correlation_dynamic_impact_test("mean", 20) == 1.40

    def test_min_tabulated_points(self):
        assert table_a_11_correlation_dynamic_impact_test("min", 2) == 1.50
        assert table_a_11_correlation_dynamic_impact_test("min", 5) == 1.35
        assert table_a_11_correlation_dynamic_impact_test("min", 10) == 1.30
        assert table_a_11_correlation_dynamic_impact_test("min", 15) == 1.25
        assert table_a_11_correlation_dynamic_impact_test("min", 20) == 1.25

    def test_model_factor_signal_matching(self):
        xi = table_a_11_correlation_dynamic_impact_test("mean", 2, "signal_matching")
        assert xi == pytest.approx(1.60 * 0.85)

    def test_model_factor_formula_with_measurement(self):
        xi = table_a_11_correlation_dynamic_impact_test("mean", 2, "formula_with_measurement")
        assert xi == pytest.approx(1.60 * 1.10)

    def test_model_factor_formula_without_measurement(self):
        xi = table_a_11_correlation_dynamic_impact_test("mean", 2, "formula_without_measurement")
        assert xi == pytest.approx(1.60 * 1.20)

    def test_no_model_factor_default(self):
        assert table_a_11_correlation_dynamic_impact_test("mean", 2) == 1.60

    def test_n_below_2_raises(self):
        with pytest.raises(ValueError):
            table_a_11_correlation_dynamic_impact_test("mean", 1)

    def test_invalid_model_factor(self):
        with pytest.raises(ValueError):
            table_a_11_correlation_dynamic_impact_test("mean", 2, "bogus")


# ============================================================================
# Table A.12: Pre-stressed anchorage resistance factors
# ============================================================================

class TestTableA12Anchorages:
    def test_temporary(self):
        assert table_a_12_anchorage_resistance("temporary", "R1") == 1.1
        assert table_a_12_anchorage_resistance("temporary", "R2") == 1.1
        assert table_a_12_anchorage_resistance("temporary", "R3") == 1.0
        assert table_a_12_anchorage_resistance("temporary", "R4") == 1.1

    def test_permanent(self):
        assert table_a_12_anchorage_resistance("permanent", "R1") == 1.1
        assert table_a_12_anchorage_resistance("permanent", "R2") == 1.1
        assert table_a_12_anchorage_resistance("permanent", "R3") == 1.0
        assert table_a_12_anchorage_resistance("permanent", "R4") == 1.1

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            table_a_12_anchorage_resistance("removable", "R1")


# ============================================================================
# Table A.13: Retaining structure resistance factors
# ============================================================================

class TestTableA13RetainingStructures:
    def test_bearing(self):
        assert table_a_13_retaining_structure_resistance("bearing", "R1") == 1.0
        assert table_a_13_retaining_structure_resistance("bearing", "R2") == 1.4
        assert table_a_13_retaining_structure_resistance("bearing", "R3") == 1.0

    def test_sliding(self):
        assert table_a_13_retaining_structure_resistance("sliding", "R2") == 1.1

    def test_earth_resistance(self):
        assert table_a_13_retaining_structure_resistance("earth_resistance", "R2") == 1.4


# ============================================================================
# Table A.14: Slope/overall stability resistance factor
# ============================================================================

class TestTableA14SlopeStability:
    def test_all_sets(self):
        assert table_a_14_slope_stability_resistance("R1") == 1.0
        assert table_a_14_slope_stability_resistance("R2") == 1.1
        assert table_a_14_slope_stability_resistance("R3") == 1.0

    def test_invalid_set(self):
        with pytest.raises(ValueError):
            table_a_14_slope_stability_resistance("R4")


# ============================================================================
# Table A.15: UPL partial factors on actions
# ============================================================================

class TestTableA15Upl:
    def test_permanent_unfavourable(self):
        assert table_a_15_upl_actions("permanent", "unfavourable") == 1.0

    def test_permanent_favourable(self):
        assert table_a_15_upl_actions("permanent", "favourable") == 0.9

    def test_variable_unfavourable(self):
        assert table_a_15_upl_actions("variable", "unfavourable") == 1.5

    def test_variable_favourable_not_defined(self):
        with pytest.raises(ValueError):
            table_a_15_upl_actions("variable", "favourable")


# ============================================================================
# Table A.16: UPL soil parameters / resistances
# ============================================================================

class TestTableA16Upl:
    def test_phi(self):
        assert table_a_16_upl_soil_resistance("phi") == 1.25

    def test_c(self):
        assert table_a_16_upl_soil_resistance("c") == 1.25

    def test_cu(self):
        assert table_a_16_upl_soil_resistance("cu") == 1.40

    def test_shaft_tension(self):
        assert table_a_16_upl_soil_resistance("shaft_tension") == 1.40

    def test_anchorage(self):
        assert table_a_16_upl_soil_resistance("anchorage") == 1.40


# ============================================================================
# Table A.17: HYD partial factors on actions
# ============================================================================

class TestTableA17Hyd:
    def test_permanent_unfavourable(self):
        assert table_a_17_hyd_actions("permanent", "unfavourable") == 1.35

    def test_permanent_favourable(self):
        assert table_a_17_hyd_actions("permanent", "favourable") == 0.90

    def test_variable_unfavourable(self):
        assert table_a_17_hyd_actions("variable", "unfavourable") == 1.50


# ============================================================================
# Design Approach combinations
# ============================================================================

class TestDesignApproachSets:
    def test_da1_c1(self):
        r = design_approach_sets("DA1-C1")
        assert r["action_set"] == "A1"
        assert r["material_set"] == "M1"
        assert r["resistance_set"] == "R1"

    def test_da1_c2(self):
        r = design_approach_sets("DA1-C2")
        assert r["action_set"] == "A2"
        assert r["material_set"] == "M2"
        assert r["resistance_set"] == "R1"
        assert r["pile_anchor_resistance_set"] == "R4"

    def test_da2(self):
        r = design_approach_sets("DA2")
        assert r["action_set"] == "A1"
        assert r["material_set"] == "M1"
        assert r["resistance_set"] == "R2"

    def test_da3(self):
        r = design_approach_sets("DA3")
        assert r["structural_action_set"] == "A1"
        assert r["geotechnical_action_set"] == "A2"
        assert r["material_set"] == "M2"
        assert r["resistance_set"] == "R3"

    def test_da1_alias(self):
        assert design_approach_sets("DA1") == design_approach_sets("DA1-C1")

    def test_invalid(self):
        with pytest.raises(ValueError):
            design_approach_sets("DA4")


# ============================================================================
# Table G.1: Rock grouping
# ============================================================================

class TestTableG1RockGroup:
    def test_group_1(self):
        r = table_g_1_rock_group("pure limestone")
        assert r["group"] == 1

    def test_group_2(self):
        r = table_g_1_rock_group("igneous")
        assert r["group"] == 2

    def test_group_3(self):
        r = table_g_1_rock_group("poorly cemented sandstone")
        assert r["group"] == 3

    def test_group_4(self):
        r = table_g_1_rock_group("uncemented mudstone")
        assert r["group"] == 4

    def test_no_match(self):
        with pytest.raises(ValueError):
            table_g_1_rock_group("granite")

    def test_ambiguous(self):
        with pytest.raises(ValueError):
            table_g_1_rock_group("limestone")


# ============================================================================
# Table H.1/H.2: Limiting movement values
# ============================================================================

class TestTableH1RelativeRotation:
    def test_range_min(self):
        assert table_h_1_limiting_relative_rotation("range_min") == pytest.approx(1 / 2000)

    def test_range_max(self):
        assert table_h_1_limiting_relative_rotation("range_max") == pytest.approx(1 / 300)

    def test_acceptable_many_structures(self):
        assert table_h_1_limiting_relative_rotation("acceptable_many_structures") == pytest.approx(1 / 500)

    def test_ultimate_limit_state(self):
        assert table_h_1_limiting_relative_rotation("ultimate_limit_state") == pytest.approx(1 / 150)

    def test_hogging_is_half_sagging(self):
        sag = table_h_1_limiting_relative_rotation("acceptable_many_structures", "sagging")
        hog = table_h_1_limiting_relative_rotation("acceptable_many_structures", "hogging")
        assert hog == pytest.approx(sag / 2)

    def test_invalid_limit_type(self):
        with pytest.raises(ValueError):
            table_h_1_limiting_relative_rotation("nonsense")

    def test_invalid_mode(self):
        with pytest.raises(ValueError):
            table_h_1_limiting_relative_rotation("range_min", "diagonal")


class TestTableH2TotalSettlement:
    def test_value(self):
        assert table_h_2_limiting_total_settlement() == 0.050


# ============================================================================
# Equations: Annex C (legible subset)
# ============================================================================

class TestAnnexCEarthPressure:
    def test_active_earth_pressure_no_cohesion(self):
        # sigma_a = Ka*(gamma*z + q)
        val = active_earth_pressure(K_a=0.33, gamma=18.0, depth=3.0, q=10.0)
        assert val == pytest.approx(0.33 * (18.0 * 3.0 + 10.0))

    def test_active_earth_pressure_with_u_and_cohesion(self):
        val = active_earth_pressure(K_a=0.33, gamma=18.0, depth=3.0, q=0.0,
                                    u=15.0, c=20.0, K_ac=1.15)
        assert val == pytest.approx(0.33 * 18.0 * 3.0 + 15.0 - 20.0 * 1.15)

    def test_passive_earth_pressure_no_cohesion(self):
        val = passive_earth_pressure(K_p=4.6, gamma=18.0, depth=2.0, q=5.0)
        assert val == pytest.approx(4.6 * (18.0 * 2.0 + 5.0))

    def test_passive_earth_pressure_with_cohesion(self):
        val = passive_earth_pressure(K_p=4.6, gamma=18.0, depth=2.0,
                                     u=8.0, c=25.0, K_pc=3.1)
        assert val == pytest.approx(4.6 * 18.0 * 2.0 + 8.0 + 25.0 * 3.1)

    def test_cohesion_coefficient_no_adhesion(self):
        # Kac = 2*sqrt(Ka), when a=0
        Ka = 0.33
        val = cohesion_earth_pressure_coefficient(Ka, adhesion=0.0, cohesion=20.0)
        assert val == pytest.approx(2.0 * math.sqrt(Ka))

    def test_cohesion_coefficient_cap(self):
        # With large adhesion, value should be capped at 2.56*sqrt(K)
        Ka = 0.33
        val = cohesion_earth_pressure_coefficient(Ka, adhesion=1000.0, cohesion=1.0)
        assert val == pytest.approx(2.56 * math.sqrt(Ka))

    def test_cohesion_coefficient_zero_cohesion_raises(self):
        with pytest.raises(ValueError):
            cohesion_earth_pressure_coefficient(0.33, adhesion=5.0, cohesion=0.0)

    def test_mobilised_wall_angle_mw_matches_equation(self):
        phi_deg, delta_deg = 30.0, 20.0
        mw_deg = mobilised_wall_angle_mw(phi_deg, delta_deg)
        # Verify: cos(2*mw + phi + delta) == sin(delta)/sin(phi)
        lhs = math.cos(math.radians(2 * mw_deg + phi_deg + delta_deg))
        rhs = math.sin(math.radians(delta_deg)) / math.sin(math.radians(phi_deg))
        assert lhs == pytest.approx(rhs, abs=1e-9)

    def test_mobilised_wall_angle_mw_zero_phi_raises(self):
        with pytest.raises(ValueError):
            mobilised_wall_angle_mw(0.0, 10.0)

    def test_mobilised_wall_angle_mw_no_solution_raises(self):
        # delta > phi makes |sin(delta)/sin(phi)| > 1 for these angles
        with pytest.raises(ValueError):
            mobilised_wall_angle_mw(10.0, 80.0)

    def test_weight_density_coefficient_vertical_wall_horizontal_ground(self):
        # beta=0, theta=0 -> Kgamma = Kn
        assert weight_density_coefficient(K_n=5.0, beta_deg=0.0, theta_deg=0.0) == pytest.approx(5.0)

    def test_weight_density_coefficient_with_slope(self):
        Kn, beta, theta = 5.0, 10.0, 0.0
        expected = Kn * math.cos(math.radians(beta)) * math.cos(math.radians(beta - theta))
        assert weight_density_coefficient(Kn, beta, theta) == pytest.approx(expected)


# ============================================================================
# Equations: Annex D (bearing resistance)
# ============================================================================

class TestBearingCapacityFactors:
    def test_phi_30_textbook_values(self):
        # Classic textbook check: phi'=30 deg -> Nq ~ 18.40, Nc ~ 30.14
        f = bearing_capacity_factors(30.0)
        assert f["Nq"] == pytest.approx(18.40, abs=0.01)
        assert f["Nc"] == pytest.approx(30.14, abs=0.01)
        assert f["Ngamma"] == pytest.approx(20.09, abs=0.01)

    def test_phi_0_raises(self):
        with pytest.raises(ValueError):
            bearing_capacity_factors(0.0)

    def test_negative_phi_raises(self):
        with pytest.raises(ValueError):
            bearing_capacity_factors(-5.0)


class TestUndrainedBearingResistance:
    def test_square_footing(self):
        r = undrained_bearing_resistance(cu=50.0, q=30.0, B=2.0)
        # Nc = pi+2, bc=1, sc=1.2 (square/circular), ic=1 (H=0)
        expected = (math.pi + 2.0) * 50.0 * 1.0 * 1.2 * 1.0 + 30.0
        assert r["bearing_pressure_kpa"] == pytest.approx(expected)
        assert r["sc"] == pytest.approx(1.2)
        assert r["Nc"] == pytest.approx(math.pi + 2.0)

    def test_rectangular_footing_shape_factor(self):
        r = undrained_bearing_resistance(cu=40.0, q=0.0, B=2.0, L=4.0, shape="rectangular")
        assert r["sc"] == pytest.approx(1.0 + 0.2 * (2.0 / 4.0))

    def test_base_inclination_reduces_bc(self):
        r0 = undrained_bearing_resistance(cu=40.0, q=0.0, B=2.0, alpha_deg=0.0)
        r10 = undrained_bearing_resistance(cu=40.0, q=0.0, B=2.0, alpha_deg=10.0)
        assert r10["bc"] < r0["bc"]

    def test_load_inclination_h_exceeds_limit_raises(self):
        with pytest.raises(ValueError):
            undrained_bearing_resistance(cu=40.0, q=0.0, B=2.0, H=1000.0)


class TestDrainedBearingResistance:
    def test_square_footing_no_cohesion_matches_manual_calc(self):
        phi, q, gamma, B = 30.0, 50.0, 18.0, 2.0
        f = bearing_capacity_factors(phi)
        r = drained_bearing_resistance(phi_deg=phi, c=0.0, q=q, gamma=gamma, B=B)
        # square/circular: bq=bgamma=1 (alpha=0), sq=1+sin(phi), sgamma=0.7
        phi_rad = math.radians(phi)
        sq = 1.0 + math.sin(phi_rad)
        sgamma = 0.7
        sc = (sq * f["Nq"] - 1.0) / (f["Nq"] - 1.0)
        expected = (0.0 + q * f["Nq"] * 1.0 * sq * 1.0
                   + 0.5 * gamma * B * f["Ngamma"] * 1.0 * sgamma * 1.0)
        assert r["bearing_pressure_kpa"] == pytest.approx(expected)
        assert r["sq"] == pytest.approx(sq)
        assert r["sgamma"] == pytest.approx(sgamma)
        assert r["sc"] == pytest.approx(sc)

    def test_rectangular_shape_factors(self):
        r = drained_bearing_resistance(phi_deg=30.0, c=0.0, q=50.0, gamma=18.0,
                                       B=2.0, L=4.0, shape="rectangular")
        phi_rad = math.radians(30.0)
        assert r["sq"] == pytest.approx(1.0 + (2.0 / 4.0) * math.sin(phi_rad))
        assert r["sgamma"] == pytest.approx(1.0 - 0.3 * (2.0 / 4.0))

    def test_load_inclination_reduces_bearing(self):
        r0 = drained_bearing_resistance(phi_deg=30.0, c=0.0, q=50.0, gamma=18.0, B=2.0)
        rH = drained_bearing_resistance(phi_deg=30.0, c=0.0, q=50.0, gamma=18.0,
                                        B=2.0, H=50.0, V=500.0)
        assert rH["bearing_pressure_kpa"] < r0["bearing_pressure_kpa"]
        assert rH["m"] is not None

    def test_h_without_v_raises(self):
        with pytest.raises(ValueError):
            drained_bearing_resistance(phi_deg=30.0, c=0.0, q=50.0, gamma=18.0,
                                       B=2.0, H=50.0)

    def test_invalid_load_direction_raises(self):
        with pytest.raises(ValueError):
            drained_bearing_resistance(phi_deg=30.0, c=0.0, q=50.0, gamma=18.0,
                                       B=2.0, H=10.0, V=500.0, load_direction="Z")

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            drained_bearing_resistance(phi_deg=0.0, c=10.0, q=50.0, gamma=18.0, B=2.0)


# ============================================================================
# Equations: Annex E (pressuremeter)
# ============================================================================

class TestPressuremeterBearingResistance:
    def test_basic(self):
        assert pressuremeter_bearing_resistance(sigma_v0=50.0, k=1.0, p_le_star=800.0) == 850.0

    def test_zero_k(self):
        assert pressuremeter_bearing_resistance(sigma_v0=50.0, k=0.0, p_le_star=800.0) == 50.0


# ============================================================================
# Equations: Annex F.2 (adjusted elasticity settlement)
# ============================================================================

class TestAdjustedElasticitySettlement:
    def test_basic(self):
        s = adjusted_elasticity_settlement(p=100.0, B=2.0, f=0.6, E_m=20000.0)
        assert s == pytest.approx(100.0 * 2.0 * 0.6 / 20000.0)

    def test_zero_modulus_raises(self):
        with pytest.raises(ValueError):
            adjusted_elasticity_settlement(p=100.0, B=2.0, f=0.6, E_m=0.0)

    def test_negative_modulus_raises(self):
        with pytest.raises(ValueError):
            adjusted_elasticity_settlement(p=100.0, B=2.0, f=0.6, E_m=-1.0)
