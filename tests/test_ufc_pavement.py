"""Tests for geotech_references.ufc_pavement (UFC 3-250-01).

Pavement Design for Roads and Parking Areas
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
    figure_e_vehicle_thickness,
    figure_e_vehicle_allowable_passes,
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

    def test_taylor_permeability_note_names_both_forms(self):
        # Eq. 20-3, PDF 113 (printed 93), prints (1-e); the code keeps (1+e).
        note = taylor_permeability(0.5, 25, 62.4, 1.0, 0.6)["note"]
        assert "(1-e)" in note and "(1+e)" in note and "owner" in note

    def test_taylor_permeability_requires_positive(self):
        with pytest.raises(ValueError):
            taylor_permeability(0, 25, 62.4, 1.0, 0.6)

    def test_effective_porosity_typical_range(self):
        r = effective_porosity(110, 2.68, 62.4, 0.05)
        assert 0 < r["effective_porosity"] < 0.35

    def test_effective_porosity_eq_20_4_as_printed(self):
        # Eq. 20-4, UFC 3-250-01 PDF 114 (printed 94):
        # ne = 1 - gamma_d/(Gs*gamma_w) * (1 + Gs*We). Made-up inputs.
        r = effective_porosity(110, 2.65, 62.4, 0.05)
        expected = 1 - 110 / (2.65 * 62.4) * (1 + 2.65 * 0.05)
        assert r["effective_porosity"] == pytest.approx(expected, abs=1e-4)
        assert r["effective_porosity"] == pytest.approx(0.2466, abs=1e-4)
        r2 = effective_porosity(100, 2.70, 62.4, 0.02)
        assert r2["effective_porosity"] == pytest.approx(
            1 - 100 / (2.70 * 62.4) * (1 + 2.70 * 0.02), abs=1e-4)
        assert "printed 94" in r["reference"]

    def test_effective_porosity_no_drainable_pore_space_raises(self):
        # Eq. 20-4 (printed 94) at made-up inputs 125 pcf, Gs 2.65, We 0.2
        # gives 1 - 125/(2.65*62.4)*(1 + 0.53) = -0.157: no drainable voids.
        with pytest.raises(ValueError, match="no drainable pore space"):
            effective_porosity(125, 2.65, 62.4, 0.2)

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
        # Eq. 20-11, UFC 3-250-01 PDF 118 (printed 98): T50 = ne*D/(2*i*k).
        r = time_for_50pct_drainage(0.25, 50, 0.02, 1000)
        assert r["t50"] == pytest.approx((0.25 * 50) / (2 * 0.02 * 1000))
        r2 = time_for_50pct_drainage(0.30, 20, 0.015, 40)
        assert r2["t50"] == pytest.approx((0.30 * 20) / (2 * 0.015 * 40))

    def test_time_for_85pct(self):
        # Eq. 20-12, same page: T85 = ne*D/(i*k), twice T50 of Eq. 20-11.
        r = time_for_85pct_drainage(0.25, 50, 0.02, 1000)
        assert r["t85"] == pytest.approx((0.25 * 50) / (0.02 * 1000))
        t50 = time_for_50pct_drainage(0.25, 50, 0.02, 1000)["t50"]
        assert r["t85"] == pytest.approx(2 * t50)

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
        # Eq. 20-17, UFC 3-250-01 PDF 127 (printed 107):
        # H = 2*F*R*L*t / [(1.7*ne*L) + (k*i*t)]. Made-up inputs.
        r = drainage_layer_thickness_required(0.5, 0.2, 50, 1, 0.25, 1000, 0.02)
        assert r["h"] == pytest.approx(
            (2 * 0.5 * 0.2 * 50 * 1) / (1.7 * 0.25 * 50 + 1000 * 0.02 * 1))
        r2 = drainage_layer_thickness_required(0.5, 0.1, 30, 1, 0.3, 50, 0.01)
        assert r2["h"] == pytest.approx(
            (2 * 0.5 * 0.1 * 30 * 1) / (1.7 * 0.3 * 30 + 50 * 0.01 * 1))
        assert "printed 107" in r["reference"]

    def test_drainage_layer_thickness_simplified_positive(self):
        # Eq. 20-18, same page: H = F*R*t / (0.85*ne).
        r = drainage_layer_thickness_simplified(0.5, 0.2, 1, 0.25)
        assert r["h"] == pytest.approx((0.5 * 0.2 * 1) / (0.85 * 0.25))

    def test_eq_20_18_is_eq_20_17_without_kit(self):
        # Eq. 20-17 with k = 0 reduces to Eq. 20-18 (PDF 127, printed 107).
        full = drainage_layer_thickness_required(0.5, 0.2, 50, 1, 0.25, 0, 0.02)
        simple = drainage_layer_thickness_simplified(0.5, 0.2, 1, 0.25)
        assert full["h"] == pytest.approx(simple["h"])

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
        r = table_5_1_compaction_depth(1_000_000, 95, "cohesive", "flexible")
        assert r["depth_in"] > 0

    def test_table_5_1_cohesionless_deeper_than_cohesive(self):
        r_cl = table_5_1_compaction_depth(1_000_000, 90, "cohesive", "flexible")
        r_cs = table_5_1_compaction_depth(1_000_000, 90, "cohesionless", "flexible")
        assert r_cs["depth_in"] > r_cl["depth_in"]

    def test_table_5_1_bad_soil_type_raises(self):
        with pytest.raises(ValueError, match="soil_type"):
            table_5_1_compaction_depth(1_000_000, 95, "bogus", "flexible")

    def test_table_5_1_zero_passes_raises(self):
        with pytest.raises(ValueError, match="passes"):
            table_5_1_compaction_depth(0, 95, "cohesive", "flexible")

    def test_table_5_1_rigid_column(self):
        # Table 5-1, UFC 3-250-01 PDF 34 (pdf_page_index 33), printed 14: rigid
        # column < 1,300 / < 1,500 / < 34,000 / < 343,000 / ... >= 290 million.
        r = table_5_1_compaction_depth(1_000_000, 95, "cohesive", "rigid")
        assert r["depth_in"] == 12      # < 2.1 million row (flexible 11)
        assert table_5_1_compaction_depth(
            1_000_000, 95, "cohesive", "flexible")["depth_in"] == 11   # < 1.3 million
        assert table_5_1_compaction_depth(
            300_000_000, 80, "cohesionless", "rigid")["depth_in"] == 77
        assert table_5_1_compaction_depth(
            1_400, 100, "cohesive", "rigid")["depth_in"] == 4
        with pytest.raises(ValueError, match="pavement_type"):
            table_5_1_compaction_depth(1_000, 95, "cohesive", "composite")
        # The table prints both columns and no default: the type is required.
        with pytest.raises(TypeError):
            table_5_1_compaction_depth(1_000, 95, "cohesive")

    def test_table_5_1_bounds_are_strict(self):
        # Printed "< 15,500": 15,500 itself is in the "< 67,500" row.
        assert table_5_1_compaction_depth(15_499, 100, "cohesive", "flexible")["depth_in"] == 3
        assert table_5_1_compaction_depth(15_500, 100, "cohesive", "flexible")["depth_in"] == 4
        assert table_5_1_compaction_depth(
            1_300, 95, "cohesionless", "rigid")["depth_in"] == 15

    def test_table_21_2_basic(self):
        # Table 21-2, PDF 144 (pdf_page_index 143), printed 124.
        r = table_21_2_aggregate_compaction_depth(1_000_000, 95, "cohesionless")
        assert r["depth_in"] == 11

    def test_table_21_2_cohesive_80pct_column(self):
        # Cohesive 80 % column as printed: 9, 11, 13, 14, 16, 18, 20, 22, 25, 27.
        assert table_21_2_aggregate_compaction_depth(
            1_000_000, 80, "cohesive")["depth_in"] == 14
        assert table_21_2_aggregate_compaction_depth(
            10_000, 80, "cohesive")["depth_in"] == 9
        assert table_21_2_aggregate_compaction_depth(
            3e9, 80, "cohesive")["depth_in"] == 27

    def test_table_21_2_no_80pct_level_cohesionless(self):
        with pytest.raises(ValueError):
            table_21_2_aggregate_compaction_depth(1_000_000, 80, "cohesionless")


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
    # Table 9-1, UFC 3-250-01 PDF 47 (pdf_page_index 46), printed 27. Asphalt-
    # stabilized: all-bituminous concrete 1.15/2.30; GW, GP, GM, GC
    # 1.00/2.00; SW, SP, SM, SC */1.50 (* not used for base course).
    def test_asphalt_base(self):
        assert table_9_1_equivalency_factor("asphalt", "gm", "base")["equivalency_factor"] == 1.00
        assert table_9_1_equivalency_factor("asphalt", "GW", "subbase")["equivalency_factor"] == 2.00
        assert table_9_1_equivalency_factor("asphalt", "SM", "subbase")["equivalency_factor"] == 1.50
        with pytest.raises(ValueError, match="not used as a base"):
            table_9_1_equivalency_factor("asphalt", "SP", "base")
        with pytest.raises(ValueError, match="No equivalency factor"):
            table_9_1_equivalency_factor("asphalt", "CL", "subbase")

    def test_appendix_g4_cement_base(self):
        # G-4.1 (PDF 280, printed 260): cement-stabilized GP base E=1.15
        r = table_9_1_equivalency_factor("cement", "GP", "base")
        assert r["equivalency_factor"] == 1.15

    def test_appendix_g4_asphalt_subbase(self):
        # G-4.2 (PDF 280, printed 260), bituminous pavement: base 1.15,
        # subbase 2.30 = the all-bituminous concrete row.
        r = table_9_1_equivalency_factor("asphalt", "all-bituminous concrete", "subbase")
        assert r["equivalency_factor"] == 2.30
        r = table_9_1_equivalency_factor("asphalt", "All-bituminous concrete", "base")
        assert r["equivalency_factor"] == 1.15

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


# Figure 10-1 (UFC 3-250-01 PDF 52, printed 32), traced from the chart
# image 2026-11-10 (pave-22). Reading points: off the stored grid, a line
# through the traced readings near each thickness (raw readings, not the
# stored table). Stated tolerance 1 % of k.
_FIG_10_1_READS = [
    (25, [(2.7, 27.0), (8.3, 46.6), (15.5, 88.7), (25.1, 155.8), (37.7, 235.5), (51.3, 308.4)]),
    (50, [(2.7, 53.3), (8.3, 89.4), (15.5, 149.9), (25.1, 229.4), (37.7, 306.8), (51.3, 367.4)]),
    (75, [(2.7, 83.2), (8.3, 130.9), (15.5, 203.5), (25.1, 280.7), (37.7, 354.9), (51.3, 408.8)]),
    (100, [(2.7, 116.8), (8.3, 176.0), (15.5, 245.9), (25.1, 326.9), (37.7, 397.8), (51.3, 444.1)]),
    (150, [(2.7, 179.1), (8.3, 231.5), (15.5, 295.9), (25.1, 372.7), (37.7, 439.1), (51.3, 475.2)]),
    (200, [(2.7, 229.2), (8.3, 284.3), (15.5, 344.4), (25.1, 406.3), (37.7, 455.8), (51.3, 483.8)]),
    (300, [(2.7, 317.9), (8.3, 348.8), (15.5, 386.9), (25.1, 431.8), (37.7, 465.2), (51.3, 488.0)]),
]


class TestFigure10_1:
    @pytest.mark.parametrize(
        "k, t, read", [(k, t, v) for k, rows in _FIG_10_1_READS for t, v in rows])
    def test_reads_on_each_curve(self, k, t, read):
        r = figure_10_1_k_on_base(k, t)
        assert r["k_on_base_psi_in"] == pytest.approx(read, rel=0.01)
        assert r["interpolation"] == f"on the {k} pci curve"

    def test_200_curve_through_gridline_crossing(self):
        # The 200 curve is drawn through the crossing of the 10 in. and
        # 300 pci gridlines.
        assert figure_10_1_k_on_base(200, 10)["k_on_base_psi_in"] == pytest.approx(300, rel=0.01)

    def test_values_that_changed(self):
        # pave-22: the earlier table gave 41.0, 160, 255, 246 and 225 here.
        assert figure_10_1_k_on_base(25, 4)["k_on_base_psi_in"] == pytest.approx(29.5, abs=0.1)
        assert figure_10_1_k_on_base(100, 10)["k_on_base_psi_in"] == pytest.approx(194.4, abs=0.1)
        assert figure_10_1_k_on_base(200, 10)["k_on_base_psi_in"] == pytest.approx(299.7, abs=0.1)
        assert figure_10_1_k_on_base(100, 28)["k_on_base_psi_in"] == pytest.approx(346.3, abs=0.1)
        assert figure_10_1_k_on_base(75, 30)["k_on_base_psi_in"] == pytest.approx(313.4, abs=0.1)

    def test_zero_thickness_equals_subgrade_k(self):
        for k in (25, 50, 75, 100, 125, 150, 200, 260, 300):
            assert figure_10_1_k_on_base(k, 0)["k_on_base_psi_in"] == pytest.approx(k, abs=0.1)

    def test_between_curves_log_log(self):
        # Between curves: log k on base linear in log k on subgrade (the
        # library's rule); halfway in log between 100 and 150 is the
        # geometric mean of the two curves.
        import math
        for t in (5, 15, 33):
            lo = figure_10_1_k_on_base(100, t)["k_on_base_psi_in"]
            hi = figure_10_1_k_on_base(150, t)["k_on_base_psi_in"]
            r = figure_10_1_k_on_base(math.sqrt(100 * 150), t)
            assert r["k_on_base_psi_in"] == pytest.approx(math.sqrt(lo * hi), abs=0.15)
            assert lo < r["k_on_base_psi_in"] < hi
            assert "library's rule" in r["interpolation"]

    def test_rises_with_thickness_and_subgrade_k(self):
        for k in (25, 50, 75, 100, 150, 200, 300):
            vals = [figure_10_1_k_on_base(k, t)["k_on_base_psi_in"] for t in range(0, 61, 3)]
            assert vals == sorted(vals)
        for t in (1, 10, 30, 59):
            vals = [figure_10_1_k_on_base(k, t)["k_on_base_psi_in"] for k in (25, 50, 75, 100, 150, 200, 300)]
            assert vals == sorted(vals)

    def test_top_corner_and_frame(self):
        # At 60 in. the curves run together near the 500 pci frame.
        assert figure_10_1_k_on_base(150, 60)["k_on_base_psi_in"] == pytest.approx(489.7, rel=0.01)
        assert figure_10_1_k_on_base(300, 60)["k_on_base_psi_in"] <= 500

    def test_negative_inputs_raise(self):
        with pytest.raises(ValueError):
            figure_10_1_k_on_base(-1, 10)
        with pytest.raises(ValueError):
            figure_10_1_k_on_base(100, -1)

    def test_limits_just_inside_and_outside(self):
        # Drawn curves k on subgrade 25-300 pci; thickness axis 0-60 in.
        r = figure_10_1_k_on_base(25, 10)
        assert r["k_on_base_psi_in"] == pytest.approx(55.3, abs=0.1) and "note" not in r
        with pytest.raises(ValueError, match="lowest curve"):
            figure_10_1_k_on_base(24.99, 10)
        assert "note" not in figure_10_1_k_on_base(300, 10)
        with pytest.raises(ValueError, match="top curve"):
            figure_10_1_k_on_base(300.01, 10)
        assert "note" not in figure_10_1_k_on_base(100, 60)
        with pytest.raises(ValueError, match="past Figure 10-1's axis"):
            figure_10_1_k_on_base(100, 60.01)
        assert "note" not in figure_10_1_k_on_base(100, 0)
        with pytest.raises(ValueError, match=">= 0"):
            figure_10_1_k_on_base(100, -0.01)

    def test_printed_range(self):
        # REF-76: outside the drawn curves (25-300 pci) and the axis (0-60
        # in) the chart gives no k and the text no rule: refused. Past the
        # top curve and the axis the edge used to be read, with a note.
        with pytest.raises(ValueError, match="lowest curve"):
            figure_10_1_k_on_base(20, 10)
        with pytest.raises(ValueError, match=r"top curve \(300 pci"):
            figure_10_1_k_on_base(400, 10)
        with pytest.raises(ValueError, match="500 psi/in"):
            figure_10_1_k_on_base(400, 10)
        with pytest.raises(ValueError, match=r"0-60 in, printed p. 32"):
            figure_10_1_k_on_base(100, 70)
        assert "note" not in figure_10_1_k_on_base(100, 30)

    def test_result_carries_the_chart_note_and_page(self):
        r = figure_10_1_k_on_base(100, 20)
        assert "high-quality material" in r["chart_note"]
        assert "printed p. 32" in r["reference"]
        assert "1 %" in r["tolerance"]


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
    # Figure 15-1, UFC 3-250-01 PDF page 70 (pdf_page_index 69), printed 50: F
    # read along each printed curve; measured tolerance 0.005 on F.
    PRINT = {  # k psi/in: {passes: F read off the printed curve}
        25: {100: 0.812, 10_000: 0.963, 10_000_000: 0.980},
        100: {1_000: 0.726, 10_000: 0.874, 100_000: 0.916,
              1_000_000: 0.927, 10_000_000: 0.930},
        200: {1_000: 0.608, 10_000: 0.807, 100_000: 0.870,
              1_000_000: 0.885, 10_000_000: 0.890},
        300: {1_000: 0.482, 10_000: 0.734, 100_000: 0.828,
              1_000_000: 0.853, 10_000_000: 0.859},
        500: {10_000: 0.477, 100_000: 0.629, 1_000_000: 0.671,
              10_000_000: 0.678},
    }

    def test_printed_curves(self):
        for k, pts in self.PRINT.items():
            for passes, f in pts.items():
                r = figure_15_1_cracking_projection_factor(passes, k)
                assert r["f"] == pytest.approx(f, abs=0.005), (k, passes)

    def test_verified_anchor(self):
        # Appendix G, G-7 (PDF 284, printed 264): k=100, 20 million passes
        # -> F = 0.93; beyond the chart's 10,000,000 edge F is held, noted.
        r = figure_15_1_cracking_projection_factor(20_000_000, 100)
        assert r["f"] == pytest.approx(0.93, abs=0.005)
        assert "held" in r["note"]
        # The hold is the guide's own (rule 2): the note quotes G-7's page.
        assert "printed 264" in r["note"] and "0.93" in r["note"]

    def test_between_curves_linear_in_k(self):
        r = figure_15_1_cracking_projection_factor(100_000, 250)
        assert r["f"] == pytest.approx(0.853, abs=0.005)
        r = figure_15_1_cracking_projection_factor(100_000, 225)
        lo = figure_15_1_cracking_projection_factor(100_000, 200)["f"]
        hi = figure_15_1_cracking_projection_factor(100_000, 250)["f"]
        assert r["f"] == pytest.approx((lo + hi) / 2, abs=0.001)

    def test_higher_k_lower_f(self):
        r_soft = figure_15_1_cracking_projection_factor(1_000_000, 50)
        r_stiff = figure_15_1_cracking_projection_factor(1_000_000, 300)
        assert r_stiff["f"] < r_soft["f"]

    def test_below_printed_curve_start_raises(self):
        # The k = 500 curve begins at about 8,600 passes (F 0.46); k = 150
        # at about 145 passes; k = 25-100 at the chart's 100-pass edge.
        with pytest.raises(ValueError, match="k=500 curve begins"):
            figure_15_1_cracking_projection_factor(5_000, 500)
        assert figure_15_1_cracking_projection_factor(9_000, 500)["f"] == \
            pytest.approx(0.46, abs=0.01)
        with pytest.raises(ValueError, match="k=150 curve begins"):
            figure_15_1_cracking_projection_factor(120, 150)

    def test_low_passes_raises(self):
        with pytest.raises(ValueError, match="curve begins"):
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
        # Appendix G, G-6 (printed 264): hd=7.9, S=0.30 -> hr=6, L=97 raw,
        # capped 75. On the nomograph the line meets the hr scale just
        # below its 6 in end, so paragraph 14-3's 6 in minimum (printed 42)
        # gives the 6 in, and the result says so.
        r = figure_14_1_reinforced_pavement_design(7.9, 0.30)
        assert r["hr_in"] == 6.0
        assert r["l_ft_raw"] == pytest.approx(97, abs=0.5)
        assert r["l_ft_capped"] == 75.0
        assert r["minimum_thickness_governs"] is True
        assert "paragraph 14-3, printed 42" in r["note"]

    def test_nomograph_read_at_five_points(self):
        # Figure 14-1 (printed 41, ufc_3_250_01_2016.pdf page 61) read off a
        # 300 dpi render with a straight line through hd and S = 0.10 %, the S of
        # the dashed example drawn on the figure: hr 7.05, 10.65, 15.1,
        # 21.4, 26.9 in at hd 8, 12, 17, 24, 30 in. The function coded as
        # hd less a fixed reduction gave 7.1, 11.1, 16.1, 23.1, 29.1.
        for hd, hr in ((8, 7.05), (12, 10.65), (17, 15.1), (24, 21.4),
                       (30, 26.9)):
            r = figure_14_1_reinforced_pavement_design(hd, 0.10)
            assert r["hr_in"] == pytest.approx(hr, abs=0.06)
            assert r["minimum_thickness_governs"] is False and "note" not in r
        # the dashed example as drawn: hd 16.9, S 0.10 -> hr 15.0; the
        # line crosses the As scale near 0.185 and the L scale near 64 ft
        r = figure_14_1_reinforced_pavement_design(16.9, 0.10)
        assert r["hr_in"] == pytest.approx(15.0, abs=0.06)
        assert r["as_sq_in_per_ft"] == pytest.approx(0.185, abs=0.005)
        assert r["l_ft_raw"] == pytest.approx(64, abs=1)
        # other steel percentages, across the S scale (0.05 to 0.50 %)
        for hd, s, hr in ((10, 0.05, 9.8), (12, 0.20, 9.6), (20, 0.30, 15.15),
                          (30, 0.30, 22.85), (17, 0.50, 11.95),
                          (30, 0.50, 21.2)):
            r = figure_14_1_reinforced_pavement_design(hd, s)
            assert r["hr_in"] == pytest.approx(hr, abs=0.06)

    def test_nomograph_line_worked_by_hand(self):
        # hd 17 in is the tick at y 389.88 on the hd scale (x 185.33), S
        # 0.10 % the tick at y 511.57 on the S scale (x 489.57); the line
        # through them reaches the hr scale (x 118.40) at y 363.11, between
        # its 15 in tick (366.03) and 15.5 in tick (354.62). Points on
        # printed 41, y downward.
        y = 389.88 + (389.88 - 511.57) * (185.33 - 118.40) / (489.57 - 185.33)
        assert y == pytest.approx(363.11, abs=0.01)
        hr = 15.0 + 0.5 * (366.03 - y) / (366.03 - 354.62)
        r = figure_14_1_reinforced_pavement_design(17.0, 0.10)
        assert hr == pytest.approx(15.13, abs=0.005)
        assert r["hr_in"] == pytest.approx(hr, abs=0.006)

    def test_more_steel_or_less_plain_thickness_never_thickens(self):
        prev = None
        for s in (0.05, 0.075, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50):
            hr = figure_14_1_reinforced_pavement_design(20.0, s)["hr_in"]
            assert prev is None or hr < prev
            prev = hr
        prev = None
        for hd in (6, 8, 10.3, 14, 19.7, 25, 30):
            hr = figure_14_1_reinforced_pavement_design(hd, 0.15)["hr_in"]
            assert hr <= hd and (prev is None or hr >= prev)
            prev = hr

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

    def test_off_the_nomograph_refused(self):
        # REF-76 (fit sweep): Figure 14-1 (printed 41) scales hd and hr 6-30
        # in and S 0.05-0.50 %. Since the nomograph was re-traced the whole
        # S scale is read (it was refused outside the worked examples' 0.10
        # to 0.30 %).
        figure_14_1_reinforced_pavement_design(30.0, 0.10)
        figure_14_1_reinforced_pavement_design(7.9, 0.20)
        for hd in (5.9, 30.1, 40.0):
            with pytest.raises(ValueError, match="plain-concrete thickness "
                               r"scale, 6 to 30 in \(printed 41\)"):
                figure_14_1_reinforced_pavement_design(hd, 0.10)
        for s_pct in (0.04, 0.049, 0.51, 1.0):
            with pytest.raises(ValueError, match=r"S scale, 0.05 to 0.50 % "
                               r"\(printed 41\)"):
                figure_14_1_reinforced_pavement_design(10.0, s_pct)
        for s_pct in (0.05, 0.09, 0.31, 0.50):
            figure_14_1_reinforced_pavement_design(10.0, s_pct)

    def test_below_the_reinforced_scale_is_the_6_in_minimum(self):
        # A line that meets the hr scale below its 6 in end (it was
        # refused): paragraph 14-3 (printed 42) sets the minimum thickness
        # of reinforced concrete pavement at 6 in.
        for hd, s in ((6.5, 0.10), (6.0, 0.05), (7.0, 0.50)):
            r = figure_14_1_reinforced_pavement_design(hd, s)
            assert r["hr_in"] == 6.0 and r["minimum_thickness_governs"] is True
            assert "below its 6 in end (printed 41)" in r["note"]
        # just above it: hd 9 in, S 0.50 % reads 6.3 in
        r = figure_14_1_reinforced_pavement_design(9.0, 0.50)
        assert r["hr_in"] == pytest.approx(6.3, abs=0.06)
        assert r["minimum_thickness_governs"] is False


class TestDistressModes:
    def test_cracking(self):
        r = table_19_1_distress_modes("cracking")
        assert "traffic_load_associated" in r

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            table_19_1_distress_modes("bogus")


class TestFrostClassification:
    """Table 19-2 (pdf_page_index 89, printed 70) as printed: a soil the table
    does not list is refused, not given a group."""

    @pytest.mark.parametrize("uscs,group,sub", [
        ("ML", "F4", "a"), ("MH", "F4", "a"), ("CH", "F3", "c"),
        ("CL", "F3", "c"), ("CL-ML", "F4", "c"),
    ])
    def test_fine_grained_rows(self, uscs, group, sub):
        r = table_19_2_frost_classification(uscs)
        assert (r["frost_group"], r["subgroup"]) == (group, sub)
        assert r["listed_in_table"] is True

    def test_cl_lists_the_other_printed_rows(self):
        # F3 (c) and F4 (c) both print "Clays, PI > 12"; F4 (d) varved.
        r = table_19_2_frost_classification("CL")
        assert r["also_printed"] == ["F4 (c)", "F4 (d)"]

    @pytest.mark.parametrize("uscs,pct,group", [
        ("GW", 1.0, "NFS"), ("GP", 2.0, "PFS"), ("GW", 4.0, "S1"),
        ("SW", 2.0, "NFS"), ("SP", 8.0, "PFS"), ("SW-SM", 4.0, "S2"),
        ("GP-GM", 5.0, "S1"), ("GM", 8.0, "F1"), ("GW-GM", 15.0, "F2"),
        ("SM", 10.0, "F2"), ("SP-SM", 12.0, "F2"), ("GM", 25.0, "F3"),
        ("SC", 20.0, "F3"), ("GC", 30.0, "F3"),
    ])
    def test_granular_rows(self, uscs, pct, group):
        r = table_19_2_frost_classification(uscs, pct)
        assert r["frost_group"] == group
        assert r["listed_in_table"] is True

    @pytest.mark.parametrize("uscs,pct,group,other", [
        ("GM", 10.0, "F2", "F1"), ("GW", 3.0, "S1", "PFS (a)"),
        ("GP", 1.5, "PFS", "NFS (a)"), ("GW-GM", 6.0, "F1", "S1"),
        ("GP-GM", 10.0, "F2", "F1"), ("SW-SM", 6.0, "F2", "S2"),
    ])
    def test_shared_end_goes_to_more_susceptible_row(self, uscs, pct, group,
                                                     other):
        # A percentage on an end two rows share takes the later, more
        # frost-susceptible row (para 19-2's order) and names the other.
        r = table_19_2_frost_classification(uscs, pct)
        assert r["frost_group"] == group
        assert other in r["also_printed"]
        assert f"row gives {other}" in r["note"]

    def test_sands_at_3_are_pfs_naming_s2_and_nfs(self):
        r = table_19_2_frost_classification("SP", 3.0)
        assert r["frost_group"] == "PFS"
        assert r["also_printed"] == ["S2", "NFS (b)"]

    @pytest.mark.parametrize("uscs,pct,group", [
        ("GM", 6.0, "F1"), ("GM", 20.0, "F2"), ("SM", 6.0, "F2"),
        ("SM", 15.0, "F2"), ("GW", 6.0, "S1"), ("SW", 0.0, "NFS"),
    ])
    def test_unshared_ends_are_in_their_row(self, uscs, pct, group):
        r = table_19_2_frost_classification(uscs, pct)
        assert r["frost_group"] == group
        assert "end two rows share" not in r.get("note", "")

    def test_sw_3_to_6_is_pfs_with_s2_also_printed(self):
        r = table_19_2_frost_classification("SW", 5.0)
        assert r["frost_group"] == "PFS"
        assert r["also_printed"] == ["S2"]
        assert "laboratory test" in r["note"]

    def test_sm_over_15_is_f4_with_f3_also_printed(self):
        r = table_19_2_frost_classification("SM", 20.0)
        assert (r["frost_group"], r["subgroup"]) == ("F4", "b")
        assert r["also_printed"] == ["F3 (b)"]

    def test_gc_sc_below_their_rows_follow_para_19_2_2(self):
        # Para 19-2.2 (pdf_page_index 87, printed 68): GC or SC "normally fall
        # into the F3 category", occasionally F2.
        r = table_19_2_frost_classification("SC", 10.0)
        assert r["frost_group"] == "F3"
        assert r["listed_in_table"] is False
        assert "19-2.2" in r["note"]
        assert table_19_2_frost_classification("GC")["frost_group"] == "F3"

    def test_gc_10_to_20_is_f3_naming_table_20_2s_f2(self):
        # Table 20-2 (pdf_page_index 124, printed 105) prints GC 10-20 % under
        # F2; para 19-2.2 says GC normally falls in F3.
        r = table_19_2_frost_classification("GC", 15.0)
        assert r["frost_group"] == "F3"
        assert r["also_printed"] == ["F2"]
        assert "drainage table" in r["note"]

    @pytest.mark.parametrize("uscs,pct,printed", [
        ("GW-GC", 8.0, "F1 (Gravelly soils, 6-10 %)"),
        ("GP-GC", 8.0, "F1 (Gravelly soils, 6-10 %)"),
        ("SC-SM", 10.0, "F2 (b) (Sands, 6-15 %)"),
        ("GC-GM", 15.0, "F2 (a) (Gravelly soils, 10-20 %)"),
    ])
    def test_duals_only_table_20_2_prints_refused_naming_it(self, uscs, pct,
                                                            printed):
        # Table 20-2 is Chapter 20's drainage table (para 20-3.3.4); para
        # 19-2 makes Table 19-2 the frost design table. The refusal names
        # what the drainage table prints and the laboratory frost test.
        with pytest.raises(ValueError) as exc:
            table_19_2_frost_classification(uscs, pct)
        msg = str(exc.value)
        assert "drainage table" in msg
        assert printed in msg
        assert "frost_group" in msg

    @pytest.mark.parametrize("uscs", ["OL", "OH", "PT"])
    def test_unlisted_symbols_refused(self, uscs):
        with pytest.raises(ValueError, match="lists no frost group"):
            table_19_2_frost_classification(uscs, 10.0)

    @pytest.mark.parametrize("uscs,pct", [
        ("SM", 4.0), ("SM", 0.0), ("GM", 4.0), ("GW", 8.0), ("SW", 12.0),
        ("SW-SM", 20.0), ("GW-GM", 2.0),
    ])
    def test_percentages_outside_the_printed_rows_refused(self, uscs, pct):
        with pytest.raises(ValueError, match="no row"):
            table_19_2_frost_classification(uscs, pct)

    def test_granular_without_percentage_refused(self):
        with pytest.raises(ValueError, match="finer_than_0_02mm_pct"):
            table_19_2_frost_classification("SW")

    def test_given_frost_group_returned(self):
        r = table_19_2_frost_classification("SW", 5.0, frost_group="s2")
        assert r["frost_group"] == "S2"
        assert "laboratory" in r["note"]
        with pytest.raises(ValueError):
            table_19_2_frost_classification("SW", 5.0, frost_group="F5")


class TestFrostSupportIndex:
    def test_f1_returns_9(self):
        assert table_19_3_frost_support_index("F1")["soil_support_index"] == 9.0

    def test_f3_returns_3_5(self):
        assert table_19_3_frost_support_index("F3")["soil_support_index"] == 3.5

    def test_nfs_raises(self):
        with pytest.raises(ValueError, match="NFS"):
            table_19_3_frost_support_index("NFS")

    def test_reference_page(self):
        # Table 19-3 is on pdf_page_index 99, printed 80.
        r = table_19_3_frost_support_index("F2")
        assert "pdf_page_index 99, printed 80" in r["reference"]


class TestFigure19_5:
    def test_figure_example(self):
        # The figure's own example: c = 32 in, r = 2.0 -> "B = 21", "S = 5.2".
        r = figure_19_5_design_base_thickness(32, 2.0)
        assert r["b_in"] == pytest.approx(21.0, abs=0.2)
        assert r["s_in"] == pytest.approx(5.2, abs=0.15)
        assert "pdf_page_index 98, printed 79" in r["reference"]

    def test_g811(self):
        # G-8.11 (printed 267): r = 3, c = 38.5 -> b = 22 in, "about 5.5 in"
        # of frost penetration into the subgrade.
        r = figure_19_5_design_base_thickness(38.5, 3.0)
        assert r["b_in"] == pytest.approx(22, abs=0.3)
        assert r["s_in"] == pytest.approx(5.5, abs=0.15)

    def test_g89_r_above_3(self):
        # G-8.9 (printed 267): r = 20/5 = 4, "the maximum allowable r of 3
        # is used", c = 42. The print says b = 26 in with "about 6 in" into
        # the subgrade; the drawn r = 3.0 line gives 23.8 in and s 5.9 in
        # (26 in would give 6.5 in), so 26 is not on the line.
        r = figure_19_5_design_base_thickness(42, 4.0)
        assert r["r_used"] == 3.0
        assert "greater than 3.0" in r["note"]
        assert r["b_in"] == pytest.approx(23.8, abs=0.2)
        assert r["s_in"] == pytest.approx(6.0, abs=0.15)

    def test_every_drawn_line_and_between(self):
        bs = [figure_19_5_design_base_thickness(50, r)["b_in"]
              for r in (0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0)]
        assert bs == sorted(bs, reverse=True)
        mid = figure_19_5_design_base_thickness(50, 2.25)["b_in"]
        assert bs[-3] > mid > bs[-2]

    def test_outside_the_chart_raises(self):
        with pytest.raises(ValueError, match="lowest drawn line"):
            figure_19_5_design_base_thickness(30, 0.5)
        with pytest.raises(ValueError, match="c axis"):
            figure_19_5_design_base_thickness(81, 2.0)
        with pytest.raises(ValueError):
            figure_19_5_design_base_thickness(0, 2.0)


class TestFigure19_6:
    def test_g812(self):
        # G-8.12 (printed 268): F3 and F4 under 8 in of base -> 50 psi/in.
        r = figure_19_6_frost_area_index_of_reaction(8, "F3_F4")
        assert r["index_of_reaction_psi_in"] == pytest.approx(50, abs=0.6)
        assert "pdf_page_index 101, printed 82" in r["reference"]

    def test_the_three_lines(self):
        # Made-up thickness; the lines as drawn, at 20 in of base.
        reads = [figure_19_6_frost_area_index_of_reaction(20, g)
                 ["index_of_reaction_psi_in"] for g in ("F1", "S2", "F3_F4")]
        assert reads == pytest.approx([221, 162, 120], abs=1.5)

    def test_outside_the_chart_raises(self):
        with pytest.raises(ValueError, match="4 in minimum"):
            figure_19_6_frost_area_index_of_reaction(3, "F3_F4")
        with pytest.raises(ValueError, match="leaves the chart"):
            figure_19_6_frost_area_index_of_reaction(40, "F1_S1")
        with pytest.raises(ValueError, match="Unknown frost_group"):
            figure_19_6_frost_area_index_of_reaction(10, "NFS")


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
    """figure_e1_flexible_thickness, read along the printed curves; every
    Appendix G read of Figure E-1 reproduced."""

    def test_g1_anchor_cbr3(self):
        # G-1: CBR=3, passes=1,000,000 -> 16.4 in
        r = figure_e1_flexible_thickness(3, 1_000_000)
        assert r["thickness_in"] == pytest.approx(16.4, abs=0.1)

    def test_g1_anchor_cbr4(self):
        # G-1: CBR=4, passes=1,395,400 -> 14 in
        r = figure_e1_flexible_thickness(4, 1_395_400)
        assert r["thickness_in"] == pytest.approx(14.0, abs=0.15)

    @pytest.mark.parametrize("cbr,thickness", [
        (10, 7.8), (7, 9.8), (4, 14.5), (25, 3.4),
    ])
    def test_g3_anchors(self, cbr, thickness):
        # G-3: 5,000,000 passes
        r = figure_e1_flexible_thickness(cbr, 5_000_000)
        assert r["thickness_in"] == pytest.approx(thickness, abs=0.1)

    def test_higher_cbr_less_thickness(self):
        r_low = figure_e1_flexible_thickness(4, 1_000_000)
        r_high = figure_e1_flexible_thickness(20, 1_000_000)
        assert r_high["thickness_in"] < r_low["thickness_in"]

    def test_more_passes_more_thickness(self):
        # CBR 5 lies on every curve (the 10-pass curve meets the axis at
        # CBR about 6).
        prev = 0.0
        for n in (10, 100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000):
            t = figure_e1_flexible_thickness(5, n)["thickness_in"]
            assert t > prev
            prev = t

    def test_past_curve_end_is_zero_with_note(self):
        r = figure_e1_flexible_thickness(40, 1_000_000)
        assert r["thickness_in"] == 0.0
        assert "no cover" in r["note"]

    def test_cbr_below_axis_raises(self):
        with pytest.raises(ValueError):
            figure_e1_flexible_thickness(0.5, 1000)

    def test_negative_cbr_raises(self):
        with pytest.raises(ValueError):
            figure_e1_flexible_thickness(-1, 1000)

    @pytest.mark.parametrize("passes", [0, 5, 20_000_000])
    def test_passes_outside_curves_raise(self, passes):
        with pytest.raises(ValueError):
            figure_e1_flexible_thickness(10, passes)


class TestFigureF1:
    """figure_f1_rigid_thickness, read off the printed chart as para 13-3
    works it; every Appendix G read of Figure F-1 reproduced."""

    def test_g7_anchor(self):
        # G-7: flexural=650, k=100, passes=20,000,000 -> hd=8.1 in
        r = figure_f1_rigid_thickness(650, 100, 20_000_000)
        assert r["thickness_in"] == pytest.approx(8.1, abs=0.1)

    def test_g8_11_anchor(self):
        # G-8.11: flexural=650, k=325, passes=1,200,000 -> 6.3 in
        r = figure_f1_rigid_thickness(650, 325, 1_200_000)
        assert r["thickness_in"] == pytest.approx(6.3, abs=0.1)

    def test_g8_12_anchor(self):
        # G-8.12: flexural=650, k=50, passes=1,200,000 -> "a pavement slab
        # 8 in thick" (rounded up to the half inch)
        r = figure_f1_rigid_thickness(650, 50, 1_200_000)
        assert 7.5 < r["thickness_in"] <= 8.0

    def test_chart_read_flag_and_reference(self):
        r = figure_f1_rigid_thickness(650, 100, 20_000_000)
        assert r["chart_read"] is True
        assert "Figure F-1" in r["reference"]
        assert "tolerance" in r
        assert r["below_chart"] is False

    def test_flexural_strength_moves_thickness(self):
        # The chart's k curves fan out across the strength scale: 400 psi
        # needs well over 2 in more slab than 900 psi at k 100, 1,000,000
        # passes (the old two-anchor fit gave 0.4 in).
        r_weak = figure_f1_rigid_thickness(400, 100, 1_000_000)
        r_strong = figure_f1_rigid_thickness(900, 100, 1_000_000)
        assert r_weak["thickness_in"] - r_strong["thickness_in"] > 2.0

    def test_all_eight_printed_passes_levels_monotonic(self):
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

    def test_k_above_500_taken_as_500(self):
        # Table 10-1 note 2: a k of 500 psi/in is the maximum used for design
        r_over = figure_f1_rigid_thickness(650, 800, 5_000_000)
        r_500 = figure_f1_rigid_thickness(650, 500, 5_000_000)
        assert r_over["thickness_in"] == r_500["thickness_in"]
        assert "maximum used for design" in r_over["note"]

    def test_under_4_in_returned_as_4_flagged(self):
        r = figure_f1_rigid_thickness(1000, 500, 1_000)
        assert r["thickness_in"] == 4.0
        assert r["below_chart"] is True

    def test_k_below_25_raises(self):
        with pytest.raises(ValueError, match="25"):
            figure_f1_rigid_thickness(650, 20, 1_000_000)

    @pytest.mark.parametrize("flexural", [-1, 50, 1100])
    def test_flexural_outside_scale_raises(self, flexural):
        with pytest.raises(ValueError):
            figure_f1_rigid_thickness(flexural, 100, 1_000_000)

    @pytest.mark.parametrize("passes", [0, 500, 60_000_000])
    def test_passes_outside_lines_raise(self, passes):
        with pytest.raises(ValueError):
            figure_f1_rigid_thickness(650, 100, passes)

    def test_k_curve_off_the_chart_raises(self):
        # At 150 psi the 500 pci curve has left the chart's right edge.
        with pytest.raises(ValueError, match="left Figure F-1"):
            figure_f1_rigid_thickness(150, 500, 1_000_000)


# ============================================================================
# Appendix E vehicle curves (E-2..E-31): figure_e_vehicle_thickness /
# figure_e_vehicle_allowable_passes, every printed curve traced (GM-303).
# Anchors: Appendix G Table G-1 (pdf_page_index 276, printed 257) at CBR 3; the
# other values are made up and test the reading rules only.
# ============================================================================

_ALL_E_VEHICLES = [
    "passenger_car", "light_strike_vehicle", "m1a1_main_tank",
    "m1a2_main_tank", "m2a3_bradley", "m35a2_cargo_truck", "m60a3_main_tank",
    "m109a6_howitzer", "m113_armored_carrier", "m923_cargo_truck",
    "m977_hemtt_cargo", "m978_hemtt_fuel", "m983_hemtt_trailer",
    "m998_hmmwv", "m988b_rtch_forklift", "m1070_het_tractor",
    "m1074_load_system_crane", "m1075_load_system",
    "m1075_load_system_trailer", "m1078_cargo_truck", "p23_crash_truck",
    "r11_refueler", "pickup_small", "pickup_large", "truck_3_axle",
    "truck_4_axle", "truck_5_axle", "truck_2_axle_6tire",
    "tyc850l_container_truck", "mobile_crane_75bfmii",
]


class TestFigureEVehicleTableG1:
    """Table G-1 prints PCASE solutions, which "differ slightly from the
    solutions determined through the use of the pavement design charts"
    (printed 256)."""

    def test_truck_5_axle(self):
        r = figure_e_vehicle_thickness("truck_5_axle", cbr=3, passes=100_000)
        assert r["thickness_in"] == pytest.approx(15.8, abs=0.25)

    def test_truck_3_axle(self):
        r = figure_e_vehicle_thickness("truck_3_axle", cbr=3, passes=500_000)
        assert r["thickness_in"] == pytest.approx(12.8, abs=0.15)

    def test_passenger_car_extrapolated(self):
        # 20,000,000 passes is past E-2's highest curve (10,000,000); Table
        # G-1 reads 6.1 in by going on past it.
        r = figure_e_vehicle_thickness("passenger_car", cbr=3, passes=20_000_000)
        assert r["thickness_in"] == pytest.approx(6.1, abs=0.05)
        assert "extrapolated" in r["note"]
        assert r["reference"] == \
            "UFC 3-250-01, Figure E-2 (pdf_page_index 212, printed 193)"

    def test_truck_5_axle_allowable_at_16_4_in(self):
        # Printed 252,915 (PCASE); the curves give 312,351-365,297 for
        # 16.35-16.45 in. The grids replaced in GM-303 stopped at the first
        # bisection midpoint, 10**5.5 = 316,228.
        r = figure_e_vehicle_allowable_passes(
            "truck_5_axle", cbr=3, thickness_in=16.4)
        assert r["allowable_passes"] == pytest.approx(337_788, rel=0.001)
        assert "clamped" not in r


class TestFigureEVehicleLookup:
    def test_figure_number_lookup(self):
        by_slug = figure_e_vehicle_thickness("passenger_car", cbr=5, passes=100_000)
        by_figure = figure_e_vehicle_thickness("E-2", cbr=5, passes=100_000)
        assert by_slug["thickness_in"] == by_figure["thickness_in"]
        assert by_figure["vehicle"] == "passenger_car"

    @pytest.mark.parametrize("name", ["E-28", "e28", "Figure E-28",
                                      "truck_5_axle", "Truck 5 Axle"])
    def test_names(self, name):
        assert figure_e_vehicle_thickness(name, 5, 1e4)["figure"] == "E-28"

    def test_unknown_vehicle_raises_with_valid_list(self):
        with pytest.raises(ValueError, match="Unknown vehicle"):
            figure_e_vehicle_thickness("not_a_real_vehicle", cbr=5, passes=1000)
        with pytest.raises(ValueError, match="Unknown vehicle"):
            figure_e_vehicle_thickness("E-1", cbr=5, passes=1000)

    def test_result_shape(self):
        r = figure_e_vehicle_thickness("truck_3_axle", cbr=5, passes=100_000)
        assert r["chart_read"] is True
        assert "Figure E-26" in r["reference"]
        assert "traced" in r["tolerance"]
        assert r["vehicle"] == "truck_3_axle"


class TestFigureEVehicleCurves:
    def test_legends_and_frames_as_printed(self):
        from geotech_references.ufc_pavement.tables import _FIGURES_E
        assert len(_FIGURES_E) == 30
        assert sorted(d["key"] for d in _FIGURES_E.values()) == \
            sorted(_ALL_E_VEHICLES)
        for fig, data in _FIGURES_E.items():
            levels = sorted(data["curves"])
            if fig == "E-2":
                assert levels == [10_000, 100_000, 1_000_000, 10_000_000]
            elif fig in ("E-3", "E-12", "E-15"):
                assert levels == [1_000, 10_000, 100_000, 1_000_000,
                                  5_000_000]
            elif fig == "E-31":
                assert levels == [100, 1_000, 10_000, 100_000, 500_000]
            else:
                assert levels == [1_000, 10_000, 100_000, 1_000_000,
                                  10_000_000]
        # E-15's frame top is 15 in; the 14 in gridline sits below it.
        assert _FIGURES_E["E-15"]["y_max_in"] == 15

    def test_curves_never_cross_or_rise(self):
        from geotech_references.ufc_pavement.tables import _FIGURES_E
        for fig, data in _FIGURES_E.items():
            levels = sorted(data["curves"])
            for i in range(60):
                cbr = 10 ** (2 * i / 59)
                last = -1.0
                for p in levels:
                    try:
                        t = figure_e_vehicle_thickness(fig, cbr, p)["thickness_in"]
                    except ValueError:
                        continue
                    assert t >= last - 1e-9, (fig, cbr, p)
                    last = t
            for p, pts in data["curves"].items():
                assert all(b[0] > a[0] and b[1] <= a[1]
                           for a, b in zip(pts, pts[1:])), (fig, p)

    def test_between_curves_log_passes(self):
        lo = figure_e_vehicle_thickness("E-27", 6, 1e4)["thickness_in"]
        hi = figure_e_vehicle_thickness("E-27", 6, 1e5)["thickness_in"]
        mid = figure_e_vehicle_thickness("E-27", 6, 10 ** 4.5)["thickness_in"]
        assert mid == pytest.approx((lo + hi) / 2, abs=0.06)

    @pytest.mark.parametrize("vehicle", _ALL_E_VEHICLES)
    def test_thickness_decreases_with_cbr(self, vehicle):
        # CBR 5: the TYC-850L's 100,000 curve is above its chart at CBR 4.
        r_low = figure_e_vehicle_thickness(vehicle, cbr=5, passes=100_000)
        r_high = figure_e_vehicle_thickness(vehicle, cbr=10, passes=100_000)
        assert r_high["thickness_in"] <= r_low["thickness_in"]

    @pytest.mark.parametrize("vehicle", _ALL_E_VEHICLES)
    def test_thickness_nondecreasing_with_passes(self, vehicle):
        # From the chart's lowest curve (10,000 passes on E-2): fewer are
        # refused (REF-76).
        from geotech_references.ufc_pavement.tables import (
            _FIGURES_E, _resolve_vehicle_figure)
        lowest = min(_FIGURES_E[_resolve_vehicle_figure(vehicle)]["curves"])
        r_few = figure_e_vehicle_thickness(vehicle, cbr=10, passes=lowest)
        r_many = figure_e_vehicle_thickness(vehicle, cbr=10, passes=1_000_000)
        assert r_many["thickness_in"] >= r_few["thickness_in"]

    @pytest.mark.parametrize("vehicle", _ALL_E_VEHICLES)
    def test_result_has_expected_fields(self, vehicle):
        r = figure_e_vehicle_thickness(vehicle, cbr=10, passes=100_000)
        assert set(r) == {"vehicle", "figure", "caption", "cbr", "passes",
                          "thickness_in", "chart_read", "tolerance",
                          "reference", "units", "printed_page",
                          "pdf_page_index"}
        assert r["thickness_in"] > 0


class TestFigureEVehicleOffTheChart:
    def test_negative_cbr_raises(self):
        with pytest.raises(ValueError):
            figure_e_vehicle_thickness("passenger_car", -1, 1000)

    def test_zero_passes_raises(self):
        with pytest.raises(ValueError):
            figure_e_vehicle_thickness("passenger_car", 10, 0)

    def test_below_the_cbr_axis(self):
        with pytest.raises(ValueError, match="below Figure E-28's CBR axis"):
            figure_e_vehicle_thickness("E-28", 0.9, 1e4)

    def test_above_the_chart(self):
        # The TYC-850L needs more than its 50 in at CBR 1 even at its
        # lowest curve; E-16's curves enter at the top frame at CBR 2+.
        with pytest.raises(ValueError, match="above the chart"):
            figure_e_vehicle_thickness("tyc850l_container_truck", cbr=1, passes=1000)
        with pytest.raises(ValueError, match="above the chart"):
            figure_e_vehicle_thickness("E-16", 1.5, 1e3)

    def test_curve_stops_above_the_axis(self):
        # E-30's curves stop 2 in above the axis.
        with pytest.raises(ValueError, match="ends at CBR"):
            figure_e_vehicle_thickness("E-30", 95, 1e3)

    def test_past_the_axis_no_cover(self):
        assert figure_e_vehicle_thickness("E-28", 80, 1e3)["thickness_in"] == 0.0
        r = figure_e_vehicle_thickness("passenger_car", cbr=100, passes=10_000_000)
        assert r["thickness_in"] == 0.0

    def test_below_the_lowest_curve(self):
        # Ruling 41 (REF-76): below a chart's lowest curve that curve's
        # thickness is given with out_of_range and a note; thickness rises
        # with passes on every chart, so it is the safe side.
        at_lowest = figure_e_vehicle_thickness("E-28", 5, 1e3)
        assert "note" not in at_lowest and "out_of_range" not in at_lowest
        few = figure_e_vehicle_thickness("E-28", 5, 500)
        assert few["thickness_in"] == at_lowest["thickness_in"]
        assert few["out_of_range"] is True
        assert "lowest curve is for 1,000 passes" in few["note"]
        assert "prints no curve below it" in few["note"]
        assert "not less than" in few["note"]
        # E-31's lowest curve is 100 passes, E-2's 10,000.
        assert "100 passes" in figure_e_vehicle_thickness(
            "E-31", 10, 50)["note"]
        assert figure_e_vehicle_thickness("passenger_car", 3, 1_000)[
            "out_of_range"] is True
        # Where the lowest curve is above the chart there is nothing to give.
        with pytest.raises(ValueError, match="lowest curve of Figure E-16 "
                           r"\(1,000 passes"):
            figure_e_vehicle_thickness("E-16", 1.5, 500)
        # Past the end of an E-30 curve that stops above the axis: refused.
        with pytest.raises(ValueError, match="ends at CBR"):
            figure_e_vehicle_thickness("E-30", 95, 500)

    def test_thickness_rises_with_passes_on_every_chart(self):
        # The basis of ruling 41: no curve for more passes lies below one
        # for fewer, at any CBR, on any of Figures E-2 to E-31.
        from geotech_references.ufc_pavement.tables import (
            _FIGURES_E, _fig_e_on_curve)
        for fig, data in _FIGURES_E.items():
            levels = sorted(data["curves"])
            for i in range(0, 401, 4):
                cbr = 10 ** (i / 200)
                prev = None
                for p in levels:
                    try:
                        t = _fig_e_on_curve(fig, p, cbr)
                    except ValueError:
                        continue
                    t = float("inf") if t is None else t
                    if prev is not None:
                        assert t >= prev - 1e-9, (fig, cbr, p)
                    prev = t

    def test_above_the_highest_curve_as_table_g1(self):
        # Rule 2: Table G-1 (printed 257) reads the passenger car at
        # 20,000,000 passes by extrapolating past its 10,000,000 curve.
        r = figure_e_vehicle_thickness("passenger_car", 3, 20_000_000)
        assert r["thickness_in"] == pytest.approx(6.1, abs=0.05)
        assert "Table G-1 (printed 257)" in r["note"]


class TestFigureEVehicleAllowablePasses:
    def test_inversion_round_trip(self):
        fwd = figure_e_vehicle_thickness("truck_3_axle", cbr=5, passes=250_000)
        inv = figure_e_vehicle_allowable_passes(
            "truck_3_axle", cbr=5, thickness_in=fwd["thickness_in"])
        # within ~15% given the 0.1in rounding on the forward call
        assert inv["allowable_passes"] == pytest.approx(250_000, rel=0.15)

    def test_reverses_the_unrounded_read(self):
        import math
        from geotech_references.ufc_pavement.tables import _fig_e_thickness
        t, _note = _fig_e_thickness("E-27", 5, 3e4)
        r = figure_e_vehicle_allowable_passes("E-27", 5, t)
        assert math.log10(r["allowable_passes"]) == pytest.approx(
            math.log10(3e4), abs=0.001)

    def test_under_the_lowest_curve_refused(self):
        # REF-76: under the lowest curve the allowable passes are fewer
        # than its passes, by how many the chart does not say; they used
        # to be returned as the lowest curve's passes (overstated).
        from geotech_references.ufc_pavement.tables import _fig_e_on_curve
        with pytest.raises(ValueError, match="under Figure E-2's lowest "
                           "curve"):
            figure_e_vehicle_allowable_passes(
                "passenger_car", cbr=7, thickness_in=0.01)
        # Every E-16 curve is above the chart at CBR 1.5.
        with pytest.raises(ValueError, match="every curve at this CBR is "
                           "above the chart"):
            figure_e_vehicle_allowable_passes("E-16", 1.5, 45)
        # On the lowest curve, as read to 0.1 in, its passes are given.
        t_lo = _fig_e_on_curve("E-2", 10_000, 7)
        for t in (t_lo, t_lo - 0.04):
            r = figure_e_vehicle_allowable_passes("passenger_car", 7, t)
            assert r["allowable_passes"] == 10_000  # E-2's lowest curve
            assert r["clamped"] == "below_min_passes_curve"
        with pytest.raises(ValueError):
            figure_e_vehicle_allowable_passes("passenger_car", 7, t_lo - 0.06)

    def test_clamped_above_max_curve(self):
        r = figure_e_vehicle_allowable_passes(
            "passenger_car", cbr=3, thickness_in=9.0)
        assert r["clamped"] == "above_max_passes_curve"
        assert r["allowable_passes"] == 10_000_000  # passenger_car's max printed level

    def test_above_the_chart_top_raises(self):
        with pytest.raises(ValueError, match="above Figure E-16's"):
            figure_e_vehicle_allowable_passes("E-16", 1.5, 60)

    def test_more_thickness_allows_more_passes(self):
        r_thin = figure_e_vehicle_allowable_passes(
            "truck_5_axle", cbr=10, thickness_in=6.0)
        r_thick = figure_e_vehicle_allowable_passes(
            "truck_5_axle", cbr=10, thickness_in=8.0)
        assert r_thick["allowable_passes"] >= r_thin["allowable_passes"]

    def test_negative_cbr_raises(self):
        with pytest.raises(ValueError):
            figure_e_vehicle_allowable_passes("passenger_car", -1, 5.0)

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError):
            figure_e_vehicle_allowable_passes("passenger_car", 10, 0)


# ---------------------------------------------------------------------------
# DOC-09: the title is the one printed on the cover
# ---------------------------------------------------------------------------

PRINTED_TITLE = "Pavement Design for Roads and Parking Areas"


def test_data_files_use_the_printed_title():
    """Manifest, figure catalog and every chapter file carry the cover's
    title (the cover and revision summary sheet print "PAVEMENT DESIGN FOR
    ROADS AND PARKING AREAS"; "Roads, Streets, Walks, and Storage Areas" is
    printed nowhere in this UFC)."""
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    pkg = root / "geotech_references" / "ufc_pavement"
    files = [root / "scripts" / "manifests" / "ufc_pavement.json",
             pkg / "figures_catalog.json", *sorted(pkg.glob("text/*.json"))]
    assert len(files) > 2
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data["reference_title"] == PRINTED_TITLE, f.name
        assert "Streets, Walks" not in f.read_text(encoding="utf-8"), f.name


def test_printed_title_is_on_the_cover():
    fitz = pytest.importorskip("fitz")
    from pathlib import Path

    pdf = Path(__file__).resolve().parents[1] / "docs" / "ufc_3_250_01_2016.pdf"
    if not pdf.exists():
        pytest.skip("ufc_3_250_01_2016.pdf not checked out")
    with fitz.open(str(pdf)) as doc:
        cover = " ".join(doc[0].get_text().split()).lower()
    assert PRINTED_TITLE.lower() in cover


def test_refusal_messages_name_the_page():
    # REF-76 checker: these refusals named the range but not the page.
    from geotech_references.ufc_pavement import tables as t
    with pytest.raises(ValueError, match="printed p. 32"):
        t.figure_10_1_k_on_base(20, 10)
    with pytest.raises(ValueError, match=r"1-100, printed 193"):
        t.figure_e_vehicle_allowable_passes("E-2", 0.5, 10)
    with pytest.raises(ValueError, match="10,000 passes, printed 193"):
        t.figure_e_vehicle_allowable_passes("E-2", 5, 0.5)
