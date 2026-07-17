"""Tests for geotech_references.ufc_pavement (UFC 3-250-01).

Pavement Design for Roads, Streets, Walks, and Storage Areas
(14 November 2016). NOT for airfields (airfields = UFC 3-260-02).

Where the guide prints a worked example (Appendix G), that example is
reproduced as a test with the printed answer as the expected value.
"""

import pytest

from geotech_references.ufc_pavement.equations import (
    mixed_traffic_equivalent_esal,
    stabilized_layer_thickness_in,
    free_draining_layer_required,
    plain_concrete_thickness_on_stabilized_foundation,
    rigid_overlay_fully_bonded,
    rigid_overlay_partially_bonded,
    rigid_overlay_non_bonded,
    flexible_overlay_of_rigid_thickness,
    reinforced_pavement_max_slab_length,
    darcy_flow_rate,
    taylor_permeability,
    effective_porosity,
    effective_horizontal_permeability,
    drainage_layer_storage_capacity,
    drainage_layer_drainable_flow,
    time_for_50pct_drainage,
    time_for_85pct_drainage,
    drainage_path_length,
    drainage_path_slope,
    granular_permeability_estimate,
    drainage_layer_thickness_required,
    drainage_layer_thickness_simplified,
    collector_drain_flow,
    pipe_capacity_manning,
    insulation_initial_temperature_differential,
    insulation_mean_soil_temperature_estimate,
)
from geotech_references.ufc_pavement.tables import (
    table_4_1_subgrade_category,
    table_5_1_compaction_depth,
    table_21_2_aggregate_compaction_depth,
    table_6_1_subbase_permissible_values,
    table_7_1_base_design_cbr,
    table_7_2_min_thickness,
    table_9_1_equivalency_factor,
    table_10_1_k_subgrade,
    figure_10_1_k_on_base,
    table_15_condition_factor,
    figure_15_1_cracking_projection_factor,
    table_16_1_joint_spacing,
    table_16_2_dowel_size,
    figure_14_1_reinforced_pavement_design,
    table_19_1_distress_modes,
    table_19_2_frost_classification,
    table_19_3_frost_support_index,
    figure_19_5_design_base_thickness,
    figure_19_6_frost_area_index_of_reaction,
    table_20_1_permeability_estimate,
    table_20_2_frost_susceptible_soils,
    table_20_8_pipe_roughness,
    table_21_1_aggregate_gradation,
    figure_e1_flexible_thickness,
    figure_f1_rigid_thickness,
)


# ===================================================================
# EQUATION TESTS
# ===================================================================


class TestMixedTrafficEquivalentEsal:
    """mixed_traffic_equivalent_esal -- verified vs. Appendix G Table G-1."""

    def _table_g1_vehicles(self):
        return [
            {"name": "18kip_esal", "design_passes": 1_000_000, "required_thickness_in": 16.4},
            {"name": "passenger_car", "design_passes": 20_000_000, "required_thickness_in": 6.1,
             "allowable_passes_at_controlling": float("inf")},
            {"name": "5axle_truck", "design_passes": 100_000, "required_thickness_in": 15.8,
             "allowable_passes_at_controlling": 252_915},
            {"name": "3axle_truck", "design_passes": 500_000, "required_thickness_in": 12.8,
             "allowable_passes_at_controlling": float("inf")},
        ]

    def test_controlling_vehicle_is_18kip(self):
        r = mixed_traffic_equivalent_esal(self._table_g1_vehicles())
        assert r["controlling_vehicle"] == "18kip_esal"
        assert r["controlling_thickness_in"] == 16.4

    def test_total_matches_printed_table_g1(self):
        r = mixed_traffic_equivalent_esal(self._table_g1_vehicles())
        # Printed total: 1,395,400
        assert r["total_equivalent_esal_passes"] == pytest.approx(1_395_400, rel=1e-3)

    def test_5axle_ratio_matches_printed(self):
        r = mixed_traffic_equivalent_esal(self._table_g1_vehicles())
        row = next(row for row in r["rows"] if row["name"] == "5axle_truck")
        assert row["ratio"] == pytest.approx(3.954, abs=0.01)
        assert row["equivalent_passes"] == pytest.approx(395_400, rel=1e-3)

    def test_unlimited_allowable_gives_zero_equivalent(self):
        r = mixed_traffic_equivalent_esal(self._table_g1_vehicles())
        for name in ("passenger_car", "3axle_truck"):
            row = next(row for row in r["rows"] if row["name"] == name)
            assert row["equivalent_passes"] == 0

    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            mixed_traffic_equivalent_esal([])

    def test_missing_allowable_passes_raises(self):
        vehicles = [
            {"name": "a", "design_passes": 100, "required_thickness_in": 10},
            {"name": "b", "design_passes": 50, "required_thickness_in": 5},
        ]
        with pytest.raises(ValueError, match="allowable_passes_at_controlling"):
            mixed_traffic_equivalent_esal(vehicles)


class TestStabilizedLayerThickness:
    def test_basic(self):
        r = stabilized_layer_thickness_in(4.0, 1.15)
        assert r["stabilized_thickness_in"] == pytest.approx(3.48, abs=0.01)

    def test_appendix_g_example_subbase(self):
        # G-4.1: 18 in / 2.30 = 7.83 in
        r = stabilized_layer_thickness_in(18.0, 2.30)
        assert r["stabilized_thickness_in"] == pytest.approx(7.83, abs=0.01)

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError, match="conventional_thickness_in"):
            stabilized_layer_thickness_in(0, 2.0)

    def test_zero_factor_raises(self):
        with pytest.raises(ValueError, match="equivalency_factor"):
            stabilized_layer_thickness_in(4.0, 0)


class TestFreeDrainingLayer:
    def test_required_when_thin(self):
        r = free_draining_layer_required(50.0, 1000)
        assert r["required"] is True

    def test_not_required_when_thick(self):
        r = free_draining_layer_required(100.0, 1000)
        assert r["required"] is False

    def test_threshold_correct(self):
        r = free_draining_layer_required(10.0, 500)
        assert r["threshold_thickness_in"] == pytest.approx(45.0, abs=0.1)

    def test_negative_bound_raises(self):
        with pytest.raises(ValueError, match="bound_layer_thickness_in"):
            free_draining_layer_required(-1.0, 500)

    def test_zero_dfi_raises(self):
        with pytest.raises(ValueError, match="design_freezing_index"):
            free_draining_layer_required(10.0, 0)


class TestEq13_1:
    """plain_concrete_thickness_on_stabilized_foundation -- Eq. 13-1."""

    def test_appendix_g_5_2_exact(self):
        # hd=8.3, Ef=650000, hs=6 -> ho=6.6 (printed)
        r = plain_concrete_thickness_on_stabilized_foundation(8.3, 650_000, 6)
        assert r["ho_in"] == pytest.approx(6.6, abs=0.05)

    def test_zero_hd_raises(self):
        with pytest.raises(ValueError, match="hd_in"):
            plain_concrete_thickness_on_stabilized_foundation(0, 650_000, 6)

    def test_negative_inner_raises(self):
        with pytest.raises(ValueError):
            plain_concrete_thickness_on_stabilized_foundation(3.0, 650_000, 6)


class TestRigidOverlayEquations:
    """Eq. 15-1/15-2/15-3/15-4 -- verified vs. Appendix G, G-7."""

    def test_fully_bonded_exact(self):
        r = rigid_overlay_fully_bonded(8.1, 6)
        assert r["ho_in"] == pytest.approx(2.1, abs=0.01)

    def test_partially_bonded_exact(self):
        r = rigid_overlay_partially_bonded(8.1, 8.1, 6, 1.0)
        assert r["ho_in"] == pytest.approx(3.7, abs=0.1)

    def test_non_bonded_exact(self):
        r = rigid_overlay_non_bonded(8.1, 8.1, 6, 1.0)
        assert r["ho_in"] == pytest.approx(5.4, abs=0.05)

    def test_flexible_overlay_of_rigid_exact(self):
        r = flexible_overlay_of_rigid_thickness(0.93, 8.1, 1.0, 6)
        assert r["to_in"] == pytest.approx(4.6, abs=0.01)

    def test_fully_bonded_min_clamp(self):
        r = rigid_overlay_fully_bonded(6.5, 6.0)
        assert r["ho_in_min_2"] == 2.0

    def test_c_out_of_range_raises(self):
        with pytest.raises(ValueError, match="c must be"):
            rigid_overlay_partially_bonded(8.1, 8.1, 6, 1.5)

    def test_negative_thickness_raises(self):
        with pytest.raises(ValueError):
            rigid_overlay_fully_bonded(-1, 6)


class TestEq17_1:
    """reinforced_pavement_max_slab_length -- verified vs. Appendix G, G-6."""

    def test_s_010_exact(self):
        r = reinforced_pavement_max_slab_length(7, 60_000, 0.10)
        assert r["l_ft_raw"] == pytest.approx(49, abs=0.5)

    def test_s_030_exact_raw(self):
        r = reinforced_pavement_max_slab_length(6, 60_000, 0.30)
        assert r["l_ft_raw"] == pytest.approx(97, abs=0.5)

    def test_s_030_capped_at_75(self):
        r = reinforced_pavement_max_slab_length(6, 60_000, 0.30)
        assert r["l_ft_capped"] == 75.0

    def test_zero_inputs_raise(self):
        with pytest.raises(ValueError):
            reinforced_pavement_max_slab_length(0, 60_000, 0.10)
        with pytest.raises(ValueError):
            reinforced_pavement_max_slab_length(7, 0, 0.10)
        with pytest.raises(ValueError):
            reinforced_pavement_max_slab_length(7, 60_000, 0)


class TestDrainageEquations:
    """Chapter 20 drainage equations (20-1 through 20-23)."""

    def test_darcy_flow_rate(self):
        r = darcy_flow_rate(0.5, 0.02, 10)
        assert r["velocity"] == pytest.approx(0.01)
        assert r["flow_rate"] == pytest.approx(0.1)

    def test_darcy_negative_k_raises(self):
        with pytest.raises(ValueError):
            darcy_flow_rate(-1, 0.01, 10)

    def test_taylor_permeability_positive(self):
        r = taylor_permeability(0.5, 25, 62.4, 1.0, 0.6)
        assert r["k"] > 0

    def test_taylor_permeability_requires_positive(self):
        with pytest.raises(ValueError):
            taylor_permeability(0, 25, 62.4, 1.0, 0.6)

    def test_effective_porosity_typical_range(self):
        r = effective_porosity(110, 2.68, 62.4, 0.05)
        assert 0 < r["effective_porosity"] < 0.35

    def test_effective_horizontal_permeability_weighted_average(self):
        r = effective_horizontal_permeability([(100, 4), (10, 8)])
        expected = (100 * 4 + 10 * 8) / (4 + 8)
        assert r["k_effective"] == pytest.approx(expected)

    def test_effective_horizontal_permeability_empty_raises(self):
        with pytest.raises(ValueError):
            effective_horizontal_permeability([])

    def test_storage_capacity(self):
        r = drainage_layer_storage_capacity(0.25, 4)
        assert r["qs"] == pytest.approx(0.85)

    def test_drainable_flow(self):
        r = drainage_layer_drainable_flow(2, 1000, 0.02, 4, 50)
        assert r["qd"] == pytest.approx((2 * 1000 * 0.02 * 4) / (2 * 50))

    def test_drainable_flow_zero_length_raises(self):
        with pytest.raises(ValueError):
            drainage_layer_drainable_flow(2, 1000, 0.02, 4, 0)

    def test_time_for_50pct(self):
        r = time_for_50pct_drainage(0.25, 50, 0.02, 1000)
        assert r["t50"] == pytest.approx((0.25 * 50) / (0.02 * 1000))

    def test_time_for_85pct(self):
        r = time_for_85pct_drainage(0.25, 50, 0.02, 1000)
        assert r["t85"] > 0

    def test_time_for_50pct_requires_positive(self):
        with pytest.raises(ValueError):
            time_for_50pct_drainage(0, 50, 0.02, 1000)

    def test_drainage_path_length(self):
        r = drainage_path_length(24, 0.02, 0.01)
        import math
        expected = 24 * math.sqrt(1 + (0.01 / 0.02) ** 2)
        assert r["length"] == pytest.approx(expected, abs=0.01)

    def test_drainage_path_slope(self):
        r = drainage_path_slope(0.02, 0.01)
        import math
        assert r["i"] == pytest.approx(math.sqrt(0.02 ** 2 + 0.01 ** 2), abs=1e-4)

    def test_drainage_path_slope_both_zero_raises(self):
        with pytest.raises(ValueError):
            drainage_path_slope(0, 0)

    def test_granular_permeability_mm_sec(self):
        r = granular_permeability_estimate(0.5, 0.35, 5, units="mm_per_sec")
        assert r["k"] > 0

    def test_granular_permeability_ft_day_larger_coefficient(self):
        r1 = granular_permeability_estimate(0.5, 0.35, 5, units="mm_per_sec")
        r2 = granular_permeability_estimate(0.5, 0.35, 5, units="ft_per_day")
        assert r2["k"] > r1["k"]

    def test_granular_permeability_bad_units_raises(self):
        with pytest.raises(ValueError, match="units"):
            granular_permeability_estimate(0.5, 0.35, 5, units="bogus")

    def test_drainage_layer_thickness_required_positive(self):
        r = drainage_layer_thickness_required(0.5, 0.2, 50, 1, 0.25, 1000, 0.02)
        assert r["h"] > 0

    def test_drainage_layer_thickness_simplified_positive(self):
        r = drainage_layer_thickness_simplified(0.5, 0.2, 1, 0.25)
        assert r["h"] == pytest.approx((0.85 * 0.5 * 0.2 * 1) / 0.25)

    def test_collector_drain_flow_ft_day(self):
        r = collector_drain_flow(0.33, 0.02, 1000, units="ft_day")
        assert r["q_per_unit_length"] == pytest.approx(0.33 * 0.02 * 1000)

    def test_collector_drain_flow_mm_sec(self):
        r = collector_drain_flow(0.33, 0.02, 1000, units="mm_sec")
        assert r["q_per_unit_length"] == pytest.approx(1000 * 0.33 * 0.02 * 1000)

    def test_pipe_capacity_manning_us(self):
        r = pipe_capacity_manning(0.013, 0.5, 0.0015, units="us")
        assert r["q"] > 0

    def test_pipe_capacity_manning_smaller_diameter_less_flow(self):
        r1 = pipe_capacity_manning(0.013, 0.5, 0.0015)
        r2 = pipe_capacity_manning(0.013, 1.0, 0.0015)
        assert r2["q"] > r1["q"]

    def test_pipe_capacity_manning_bad_units_raises(self):
        with pytest.raises(ValueError, match="units"):
            pipe_capacity_manning(0.013, 0.5, 0.0015, units="bogus")


class TestInsulationEquations:
    def test_initial_temperature_differential(self):
        r = insulation_initial_temperature_differential(40)
        assert r["vo_f"] == 8

    def test_mean_soil_temperature_estimate(self):
        r = insulation_mean_soil_temperature_estimate(33)
        assert r["mean_annual_soil_temp_f_estimate"] == 40


# ===================================================================
# TABLE TESTS
# ===================================================================


class TestSubgradeCategory:
    def test_category_a_high_cbr(self):
        assert table_4_1_subgrade_category(20.0)["category"] == "A"

    def test_category_d_matches_appendix_g(self):
        # Appendix G, G-1: CBR=4 -> category D, representative CBR=3
        r = table_4_1_subgrade_category(4.0)
        assert r["category"] == "D"
        assert r["representative_cbr"] == 3

    def test_zero_cbr_raises(self):
        with pytest.raises(ValueError, match="cbr must be > 0"):
            table_4_1_subgrade_category(0.0)


class TestCompactionDepth:
    def test_table_5_1_basic(self):
        r = table_5_1_compaction_depth(1_000_000, 95, "cohesive")
        assert r["depth_in"] > 0

    def test_table_5_1_cohesionless_deeper_than_cohesive(self):
        r_cl = table_5_1_compaction_depth(1_000_000, 90, "cohesive")
        r_cs = table_5_1_compaction_depth(1_000_000, 90, "cohesionless")
        assert r_cs["depth_in"] > r_cl["depth_in"]

    def test_table_5_1_bad_soil_type_raises(self):
        with pytest.raises(ValueError, match="soil_type"):
            table_5_1_compaction_depth(1_000_000, 95, "bogus")

    def test_table_5_1_zero_passes_raises(self):
        with pytest.raises(ValueError, match="passes"):
            table_5_1_compaction_depth(0, 95, "cohesive")

    def test_table_21_2_basic(self):
        r = table_21_2_aggregate_compaction_depth(1_000_000, 95, "cohesionless")
        assert r["depth_in"] > 0

    def test_table_21_2_no_80pct_level(self):
        with pytest.raises(ValueError):
            table_21_2_aggregate_compaction_depth(1_000_000, 80, "cohesive")


class TestSubbasePermissibleValues:
    def test_cbr_50_subbase(self):
        r = table_6_1_subbase_permissible_values(50)
        assert r["layer_type"] == "Subbase"
        assert r["max_pct_passing_no200"] == 15

    def test_cbr_20_select_material(self):
        r = table_6_1_subbase_permissible_values(20)
        assert r["layer_type"] == "Select material"

    def test_invalid_cbr_raises(self):
        with pytest.raises(ValueError, match="design_cbr must be one of"):
            table_6_1_subbase_permissible_values(60)


class TestBaseDesignCBR:
    def test_graded_crushed_aggregate_100(self):
        assert table_7_1_base_design_cbr("graded_crushed_aggregate")["design_cbr"] == 100

    def test_limerock_80(self):
        assert table_7_1_base_design_cbr("limerock")["design_cbr"] == 80

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown material_type"):
            table_7_1_base_design_cbr("concrete")


class TestMinThickness:
    def test_low_esal_cbr100(self):
        r = table_7_2_min_thickness(10_000, 100)
        assert r["base_in"] == 4
        assert r["total_in"] == 4.5

    def test_appendix_g3_matches(self):
        # G-3.2: 5,000,000 passes -> min base 4in, min pavement 3.5in (CBR100)
        r = table_7_2_min_thickness(5_000_000, 100)
        assert r["base_in"] == 4
        assert r["surface_in"] == 3.5

    def test_cbr50_high_esal_raises(self):
        with pytest.raises(ValueError, match="restricted to ESAL"):
            table_7_2_min_thickness(1_000_000, 50)

    def test_invalid_cbr_raises(self):
        with pytest.raises(ValueError, match="base_cbr must be 50, 80, or 100"):
            table_7_2_min_thickness(100_000, 70)


class TestEquivalencyFactor:
    def test_asphalt_base(self):
        assert table_9_1_equivalency_factor("asphalt", "gm", "base")["equivalency_factor"] == 1.15

    def test_appendix_g4_cement_base(self):
        # G-4.1: cement-stabilized base E=1.15
        r = table_9_1_equivalency_factor("cement", "GP", "base")
        assert r["equivalency_factor"] == 1.15

    def test_appendix_g4_asphalt_subbase(self):
        # G-4.2: subbase E=2.30
        r = table_9_1_equivalency_factor("asphalt", "GW", "subbase")
        assert r["equivalency_factor"] == 2.30

    def test_lime_cl_base_raises(self):
        with pytest.raises(ValueError, match="not used as a base"):
            table_9_1_equivalency_factor("lime", "CL", "base")

    def test_invalid_stabilizer_raises(self):
        with pytest.raises(ValueError, match="Unknown stabilizer_type"):
            table_9_1_equivalency_factor("epoxy", "CL", "base")


class TestKSubgrade:
    def test_cl_10pct(self):
        assert table_10_1_k_subgrade("CL", 10)["k_psi_in"] == 175

    def test_gw_2pct(self):
        assert table_10_1_k_subgrade("GW", 2)["k_psi_in"] == 500

    def test_high_moisture_unavailable_raises(self):
        with pytest.raises(ValueError, match="no data"):
            table_10_1_k_subgrade("GW", 25)

    def test_invalid_uscs_raises(self):
        with pytest.raises(ValueError, match="Unknown USCS group"):
            table_10_1_k_subgrade("XX", 10)


class TestFigure10_1:
    def test_k_on_base_exceeds_subgrade_k(self):
        r = figure_10_1_k_on_base(100, 20)
        assert r["k_on_base_psi_in"] > 100

    def test_zero_thickness_equals_subgrade_k(self):
        r = figure_10_1_k_on_base(100, 0)
        assert r["k_on_base_psi_in"] == pytest.approx(100, abs=1)

    def test_more_base_gives_more_k(self):
        r1 = figure_10_1_k_on_base(100, 10)
        r2 = figure_10_1_k_on_base(100, 40)
        assert r2["k_on_base_psi_in"] > r1["k_on_base_psi_in"]

    def test_negative_inputs_raise(self):
        with pytest.raises(ValueError):
            figure_10_1_k_on_base(-1, 10)
        with pytest.raises(ValueError):
            figure_10_1_k_on_base(100, -1)


class TestConditionFactor:
    def test_rigid_plain_good(self):
        r = table_15_condition_factor("rigid", "plain", 1.00)
        assert "Good condition" in r["description"]

    def test_flexible_plain_multiple_cracking(self):
        r = table_15_condition_factor("flexible", "plain", 0.50)
        assert r["c"] == 0.50

    def test_invalid_combination_raises(self):
        with pytest.raises(ValueError, match="Unknown combination"):
            table_15_condition_factor("bogus", "plain", 1.0)

    def test_invalid_c_raises(self):
        with pytest.raises(ValueError):
            table_15_condition_factor("rigid", "plain", 0.50)


class TestFigure15_1:
    def test_verified_anchor(self):
        # Appendix G, G-7: k=100, passes=20e6 -> F=0.93
        r = figure_15_1_cracking_projection_factor(20_000_000, 100)
        assert r["f"] == pytest.approx(0.93, abs=0.03)

    def test_higher_k_lower_f(self):
        r_soft = figure_15_1_cracking_projection_factor(1_000_000, 50)
        r_stiff = figure_15_1_cracking_projection_factor(1_000_000, 300)
        assert r_stiff["f"] < r_soft["f"]

    def test_low_passes_raises(self):
        with pytest.raises(ValueError, match="passes must be >= 100"):
            figure_15_1_cracking_projection_factor(10, 100)

    def test_k_out_of_range_raises(self):
        with pytest.raises(ValueError, match="k_existing_psi_in"):
            figure_15_1_cracking_projection_factor(1_000_000, 600)


class TestJointSpacing:
    def test_thin_pavement(self):
        r = table_16_1_joint_spacing(6)
        assert r["max_spacing_ft"] == 15.0

    def test_thick_pavement_capped_at_20(self):
        r = table_16_1_joint_spacing(20)
        assert r["max_spacing_ft"] == 20.0

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError):
            table_16_1_joint_spacing(0)


class TestDowelSize:
    def test_thin_slab(self):
        r = table_16_2_dowel_size(6)
        assert "0.75" in r["dowel"]

    def test_medium_slab(self):
        r = table_16_2_dowel_size(9)
        assert "1 in" in r["dowel"]

    def test_thick_slab(self):
        r = table_16_2_dowel_size(14)
        assert r["min_dowel_length_in"] == 20

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            table_16_2_dowel_size(20)


class TestFigure14_1:
    def test_verified_s_010(self):
        # Appendix G, G-6: hd=7.9, S=0.10 -> hr=7, L=49
        r = figure_14_1_reinforced_pavement_design(7.9, 0.10)
        assert r["hr_in"] == pytest.approx(7.0, abs=0.1)
        assert r["l_ft_raw"] == pytest.approx(49, abs=0.5)

    def test_verified_s_030(self):
        # Appendix G, G-6: hd=7.9, S=0.30 -> hr=6, L=97 raw, capped 75
        r = figure_14_1_reinforced_pavement_design(7.9, 0.30)
        assert r["hr_in"] == pytest.approx(6.0, abs=0.1)
        assert r["l_ft_capped"] == 75.0

    def test_transverse_half_longitudinal(self):
        r = figure_14_1_reinforced_pavement_design(7.9, 0.10)
        assert r["transverse_s_pct"] == pytest.approx(0.05)

    def test_as_definition(self):
        r = figure_14_1_reinforced_pavement_design(7.9, 0.10)
        expected_as = (0.10 / 100.0) * 12.0 * r["hr_in"]
        assert r["as_sq_in_per_ft"] == pytest.approx(expected_as, abs=0.01)

    def test_s_out_of_range_raises(self):
        with pytest.raises(ValueError, match="s_pct"):
            figure_14_1_reinforced_pavement_design(7.9, 0.60)


class TestDistressModes:
    def test_cracking(self):
        r = table_19_1_distress_modes("cracking")
        assert "traffic_load_associated" in r

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            table_19_1_distress_modes("bogus")


class TestFrostClassification:
    def test_ml_is_f4(self):
        r = table_19_2_frost_classification("ML", 50)
        assert r["frost_group"] == "F4"

    def test_sm_low_fines_s2(self):
        assert table_19_2_frost_classification("SM", 4.0)["frost_group"] == "S2"

    def test_gw_nfs(self):
        assert table_19_2_frost_classification("GW", 1.0)["frost_group"] == "NFS"


class TestFrostSupportIndex:
    def test_f1_returns_9(self):
        assert table_19_3_frost_support_index("F1")["soil_support_index"] == 9.0

    def test_f3_returns_3_5(self):
        assert table_19_3_frost_support_index("F3")["soil_support_index"] == 3.5

    def test_nfs_raises(self):
        with pytest.raises(ValueError, match="NFS"):
            table_19_3_frost_support_index("NFS")


class TestFigure19_5:
    def test_r2_exact(self):
        # Figure's own printed worked example: c=32, r=2.0 -> b=21, s=5.2
        r = figure_19_5_design_base_thickness(32, 2.0)
        assert r["b_in"] == pytest.approx(21.0, abs=0.2)
        assert r["s_in"] == pytest.approx(5.2, abs=0.2)

    def test_r3_matches_g89(self):
        # Appendix G, G-8.9: c=42, r=3 -> b=26 (within read-off tolerance)
        r = figure_19_5_design_base_thickness(42, 3.0)
        assert r["b_in"] == pytest.approx(26, abs=3)

    def test_r3_matches_g811(self):
        # Appendix G, G-8.11: c=38.5, r=3 -> b=22
        r = figure_19_5_design_base_thickness(38.5, 3.0)
        assert r["b_in"] == pytest.approx(22, abs=3)

    def test_undigitized_r_raises(self):
        with pytest.raises(ValueError, match="not digitized"):
            figure_19_5_design_base_thickness(30, 1.0)


class TestFigure19_6:
    def test_verified_anchor(self):
        r = figure_19_6_frost_area_index_of_reaction(8, "F3_F4")
        assert r["index_of_reaction_psi_in"] == 50.0

    def test_other_input_raises(self):
        with pytest.raises(ValueError, match="Only the verified"):
            figure_19_6_frost_area_index_of_reaction(12, "F3_F4")


class TestPermeabilityTable:
    def test_pct_10(self):
        r = table_20_1_permeability_estimate(10)
        assert r["permeability_ft_per_min"] == 1e-3

    def test_invalid_pct_raises(self):
        with pytest.raises(ValueError):
            table_20_1_permeability_estimate(7)


class TestFrostSusceptibleSoilsCh20:
    def test_f1(self):
        r = table_20_2_frost_susceptible_soils("F1")
        assert "GW-GM" in r["uscs_types"]

    def test_f4d(self):
        r = table_20_2_frost_susceptible_soils("F4d")
        assert r["frost_group"] == "F4d"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            table_20_2_frost_susceptible_soils("F9")


class TestPipeRoughness:
    def test_smooth_pipe(self):
        r = table_20_8_pipe_roughness("clay_concrete_smooth_plastic_asbestos_cement")
        assert r["n"] == 0.013

    def test_corrugated(self):
        assert table_20_8_pipe_roughness("corrugated_metal")["n"] == 0.024

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            table_20_8_pipe_roughness("bogus")


class TestAggregateGradation:
    def test_gradation_1(self):
        r = table_21_1_aggregate_gradation(1)
        assert r["pct_passing"]["no200"] == (8, 15)

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            table_21_1_aggregate_gradation(5)


class TestFigureE1:
    """figure_e1_flexible_thickness -- verified vs. multiple Appendix G points."""

    def test_g1_anchor_cbr3(self):
        # G-1: CBR=3, passes=1,000,000 -> 16.4 in
        r = figure_e1_flexible_thickness(3, 1_000_000)
        assert r["thickness_in"] == pytest.approx(16.4, abs=0.1)

    def test_g3_anchor_cbr10(self):
        # G-3.1: CBR=10, passes=5,000,000 -> 7.8 in
        r = figure_e1_flexible_thickness(10, 5_000_000)
        assert r["thickness_in"] == pytest.approx(7.8, abs=0.3)

    def test_g3_anchor_cbr7(self):
        # G-3.1: CBR=7, passes=5,000,000 -> 9.8 in
        r = figure_e1_flexible_thickness(7, 5_000_000)
        assert r["thickness_in"] == pytest.approx(9.8, abs=0.3)

    def test_g3_anchor_cbr4(self):
        # G-3.1: CBR=4, passes=5,000,000 -> 14.5 in
        r = figure_e1_flexible_thickness(4, 5_000_000)
        assert r["thickness_in"] == pytest.approx(14.5, abs=0.3)

    def test_g3_anchor_cbr25(self):
        # G-3.1: CBR=25, passes=5,000,000 -> 3.4 in
        r = figure_e1_flexible_thickness(25, 5_000_000)
        assert r["thickness_in"] == pytest.approx(3.4, abs=0.3)

    def test_higher_cbr_less_thickness(self):
        r_low = figure_e1_flexible_thickness(4, 1_000_000)
        r_high = figure_e1_flexible_thickness(20, 1_000_000)
        assert r_high["thickness_in"] < r_low["thickness_in"]

    def test_more_passes_more_thickness(self):
        r_few = figure_e1_flexible_thickness(10, 100)
        r_many = figure_e1_flexible_thickness(10, 1_000_000)
        assert r_many["thickness_in"] > r_few["thickness_in"]

    def test_negative_cbr_raises(self):
        with pytest.raises(ValueError):
            figure_e1_flexible_thickness(-1, 1000)

    def test_zero_passes_raises(self):
        with pytest.raises(ValueError):
            figure_e1_flexible_thickness(10, 0)


class TestFigureF1:
    """figure_f1_rigid_thickness -- verified vs. two Appendix G worked
    examples, plus read-grid anchor-grid / monotonicity checks."""

    def test_g7_anchor_exact(self):
        # G-7: flexural=650, k=100, passes=20,000,000 -> hd=8.1 in
        r = figure_f1_rigid_thickness(650, 100, 20_000_000)
        assert r["thickness_in"] == pytest.approx(8.1, abs=0.05)

    def test_g8_11_anchor_exact(self):
        # G-8.11: flexural=650, k=325, passes=1,200,000 -> 6.3 in
        r = figure_f1_rigid_thickness(650, 325, 1_200_000)
        assert r["thickness_in"] == pytest.approx(6.3, abs=0.05)

    def test_chart_read_flag_and_reference(self):
        r = figure_f1_rigid_thickness(650, 100, 20_000_000)
        assert r["chart_read"] is True
        assert "Figure F-1" in r["reference"]
        assert "tolerance" in r

    def test_anchor_tolerance_note_within_range(self):
        # Both anchors sit inside the 1.2M-20M passes span they define.
        r = figure_f1_rigid_thickness(650, 100, 20_000_000)
        assert "+/-10%" in r["tolerance"]

    def test_extrapolated_passes_gets_wider_tolerance_note(self):
        # 500,000 passes is well below the 1.2M low anchor -> extrapolated.
        r = figure_f1_rigid_thickness(650, 200, 500_000)
        assert "+/-20-25%" in r["tolerance"]

    def test_all_eight_printed_passes_levels_monotonic(self):
        # Sanity check across all 8 printed N-line levels at a representative
        # (flexural,k): monotonic increase in thickness, all within the
        # chart's printed 4-12in axis range. (The model interpolates/
        # extrapolates log-linearly between the two Appendix G anchors, so
        # this must hold for any single fixed (flexural,k).)
        levels = [1_000, 3_000, 10_000, 30_000, 100_000, 1_000_000,
                  10_000_000, 50_000_000]
        thicknesses = [figure_f1_rigid_thickness(650, 150, n)["thickness_in"]
                       for n in levels]
        assert thicknesses == sorted(thicknesses)
        assert all(4.0 <= t <= 12.0 for t in thicknesses)

    def test_higher_k_less_thickness(self):
        r_soft = figure_f1_rigid_thickness(650, 50, 5_000_000)
        r_stiff = figure_f1_rigid_thickness(650, 400, 5_000_000)
        assert r_stiff["thickness_in"] < r_soft["thickness_in"]

    def test_more_passes_more_thickness(self):
        r_few = figure_f1_rigid_thickness(650, 100, 10_000)
        r_many = figure_f1_rigid_thickness(650, 100, 50_000_000)
        assert r_many["thickness_in"] > r_few["thickness_in"]

    def test_higher_flexural_less_thickness(self):
        r_weak = figure_f1_rigid_thickness(400, 100, 1_000_000)
        r_strong = figure_f1_rigid_thickness(900, 100, 1_000_000)
        assert r_strong["thickness_in"] < r_weak["thickness_in"]

    def test_anchor_grid_k_endpoints_reproduce_read_points(self):
        # Sanity check on the k-family read-grid endpoints (25 and 500 pci)
        # stay within the chart's printed 4-12 in axis range.
        r_25 = figure_f1_rigid_thickness(500, 25, 10_000_000)
        r_500 = figure_f1_rigid_thickness(500, 500, 10_000_000)
        assert 4.0 <= r_25["thickness_in"] <= 12.0
        assert 4.0 <= r_500["thickness_in"] <= 12.0
        assert r_25["thickness_in"] > r_500["thickness_in"]

    def test_result_clamped_within_chart_axis_range(self):
        # Extreme corner (softest k, weakest flexural, lowest passes) must
        # still clamp into the chart's printed 4-12 in range, not go negative.
        r = figure_f1_rigid_thickness(100, 25, 1_000)
        assert 4.0 <= r["thickness_in"] <= 12.0

    def test_k_and_flexural_clamp_at_chart_bounds(self):
        # k and flexural far outside the chart's printed range clamp to the
        # nearest printed line rather than extrapolating indefinitely.
        r_k_over = figure_f1_rigid_thickness(650, 5000, 5_000_000)
        r_k_at_bound = figure_f1_rigid_thickness(650, 500, 5_000_000)
        assert r_k_over["thickness_in"] == r_k_at_bound["thickness_in"]

    def test_negative_flexural_raises(self):
        with pytest.raises(ValueError):
            figure_f1_rigid_thickness(-1, 100, 1_000_000)

    def test_negative_k_raises(self):
        with pytest.raises(ValueError):
            figure_f1_rigid_thickness(650, -1, 1_000_000)

    def test_zero_passes_raises(self):
        with pytest.raises(ValueError):
            figure_f1_rigid_thickness(650, 100, 0)
