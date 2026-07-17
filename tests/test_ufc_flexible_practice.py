"""Tests for UFC 3-250-03 (Standard Practice Manual for Flexible Pavements)
table lookups, equations, and structured reference text retrieval."""

import pytest

from geotech_references.ufc_flexible_practice.tables import (
    spray_application_rate,
    table_2_1_gradation_hma,
    table_2_3_asphalt_grade_by_pti,
    table_2_5_asphalt_grade_by_freezing_index,
    table_2_7_minimum_vma,
    table_2_8_marshall_design_criteria,
    table_2_12_pfc_gradation,
    table_2_15_sma_gradation,
    table_2_17_sma_mix_design_requirements,
    table_3_2_tack_coat_temperature,
    table_4_2_gradation_sbst,
    table_4_3_gradation_dbst,
    table_4_4_slurry_seal_gradation,
    table_4_5_frs_application_rate,
    table_4_7_micro_surfacing_gradation,
    table_6_1_cold_mix_gradation,
    table_6_2_cold_mix_asphalt_selection,
    table_6_3_cold_mix_optimum_ac_selection,
    table_6_4_mixing_temperature,
    table_7_2_ogam_gradation,
    table_7_3_slurry_grout_gradation,
    table_7_4_grout_mix_proportions,
    table_7_5_grout_viscosity,
    table_b1_surface_area_factor,
)
from geotech_references.ufc_flexible_practice.equations import (
    air_voids_vtm,
    bulk_specific_gravity_gmb,
    bulk_specific_gravity_gmb_geometric,
    fuller_thompson_max_density_passing,
    rmp_optimum_asphalt_content,
    rmp_specific_surface_area,
    slurry_seal_asphalt_for_film_thickness,
    slurry_seal_corrected_surface_area,
    slurry_seal_surface_area,
    slurry_seal_total_asphalt_required,
    voids_filled_with_asphalt_vfa,
    voids_in_mineral_aggregate_vma,
)
from geotech_references._retrieval import (
    list_chapters,
    load_chapter,
    retrieve_section,
    search_sections,
)


REF = "ufc_flexible_practice"


# ============================================================================
# Table 2-1: HMA aggregate gradations
# ============================================================================

class TestTable21:
    def test_gradation1_at_475mm(self):
        r = table_2_1_gradation_hma("gradation_1", 4.75)
        assert r["percent_passing_min"] == 45
        assert r["percent_passing_max"] == 67
        assert r["nominal_max_size_mm"] == 19.0

    def test_gradation3_top_sieve_full_pass(self):
        r = table_2_1_gradation_hma("gradation_3", 12.5)
        assert r["percent_passing_min"] == 100
        assert r["percent_passing_max"] == 100

    def test_gradation2_above_nominal_max_raises(self):
        with pytest.raises(ValueError):
            table_2_1_gradation_hma("gradation_2", 25.0)

    def test_finest_sieve_shared_across_gradations(self):
        for g in ("gradation_1", "gradation_2", "gradation_3"):
            r = table_2_1_gradation_hma(g, 0.075)
            assert r["percent_passing_min"] == 3
            assert r["percent_passing_max"] == 6

    def test_no_sieve_returns_full_bands(self):
        r = table_2_1_gradation_hma("gradation_1")
        assert len(r["bands"]) == 11

    def test_invalid_gradation(self):
        with pytest.raises(ValueError):
            table_2_1_gradation_hma("gradation_4", 4.75)

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_2_1_gradation_hma("gradation_1", 3.33)


# ============================================================================
# Table 2-3: Asphalt binder base grade by PTI
# ============================================================================

class TestTable23:
    def test_cold_region(self):
        r = table_2_3_asphalt_grade_by_pti(10.0)
        assert r["temperature_region"] == "cold"

    def test_warm_region_at_boundary(self):
        r = table_2_3_asphalt_grade_by_pti(16.7)
        assert r["temperature_region"] == "warm"

    def test_hot_region(self):
        r = table_2_3_asphalt_grade_by_pti(50.0)
        assert r["temperature_region"] == "hot"
        assert "PG" in r["asphalt_cement_selection_criteria"]

    def test_pti_f_conversion(self):
        r = table_2_3_asphalt_grade_by_pti(0)
        assert r["pti_f"] == 0.0

    def test_negative_pti_raises(self):
        with pytest.raises(ValueError):
            table_2_3_asphalt_grade_by_pti(-1)


# ============================================================================
# Table 2-5: Asphalt grade by design air-freezing index
# ============================================================================

class TestTable25:
    def test_moderately_cold(self):
        r = table_2_5_asphalt_grade_by_freezing_index(1000)
        assert r["temperature_region"] == "moderately_cold"

    def test_severely_cold_at_boundary(self):
        r = table_2_5_asphalt_grade_by_freezing_index(1667)
        assert r["temperature_region"] == "severely_cold"

    def test_negative_dfi_raises(self):
        with pytest.raises(ValueError):
            table_2_5_asphalt_grade_by_freezing_index(-1)


# ============================================================================
# Table 2-7: Minimum VMA
# ============================================================================

class TestTable27:
    def test_gradation_1(self):
        r = table_2_7_minimum_vma("gradation_1")
        assert r["min_vma_pct"] == 13.0
        assert r["nominal_max_size_mm"] == 25.0

    def test_gradation_3(self):
        r = table_2_7_minimum_vma("gradation_3")
        assert r["min_vma_pct"] == 15.0

    def test_invalid_gradation(self):
        with pytest.raises(ValueError):
            table_2_7_minimum_vma("gradation_9")


# ============================================================================
# Table 2-8: Marshall design criteria
# ============================================================================

class TestTable28:
    def test_hma_50_blows_stability(self):
        r = table_2_8_marshall_design_criteria("hma", "50_blows")
        assert r["marshall_stability_min_kn"] == 6.0
        assert r["vfa_pct_range"] == (75, 85)

    def test_hma_75_blows_stability(self):
        r = table_2_8_marshall_design_criteria("hma", "75_blows")
        assert r["marshall_stability_min_kn"] == 8.0
        assert r["vfa_pct_range"] == (70, 80)

    def test_sand_asphalt_50_blows(self):
        r = table_2_8_marshall_design_criteria("sand_asphalt", "50_blows")
        assert r["marshall_stability_min_lbf"] == 500
        assert "note" in r

    def test_gyration_no_stability(self):
        r = table_2_8_marshall_design_criteria("hma", "50_gyrations")
        assert r["marshall_stability_min_kn"] is None

    def test_single_property_stability(self):
        r = table_2_8_marshall_design_criteria("hma", "50_blows", property="stability")
        assert r["value"]["marshall_stability_min_kn"] == 6.0

    def test_single_property_flow(self):
        r = table_2_8_marshall_design_criteria("hma", "75_blows", property="flow")
        assert r["value"] == 16

    def test_unavailable_combination_raises(self):
        with pytest.raises(ValueError):
            table_2_8_marshall_design_criteria("sand_asphalt", "75_blows")

    def test_invalid_property_raises(self):
        with pytest.raises(ValueError):
            table_2_8_marshall_design_criteria("hma", "50_blows", property="nonsense")


# ============================================================================
# Table 2-12: PFC gradation
# ============================================================================

class TestTable212:
    def test_gradation_a(self):
        r = table_2_12_pfc_gradation("gradation_a", 4.75)
        assert r["percent_passing_min"] == 25
        assert r["percent_passing_max"] == 40

    def test_gradation_b_full_bands(self):
        r = table_2_12_pfc_gradation("gradation_b")
        assert len(r["bands"]) == 7

    def test_invalid_gradation(self):
        with pytest.raises(ValueError):
            table_2_12_pfc_gradation("gradation_z")

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_2_12_pfc_gradation("gradation_a", 1.0)


# ============================================================================
# Table 2-15: SMA gradation guideline
# ============================================================================

class TestTable215:
    def test_top_sieve(self):
        r = table_2_15_sma_gradation(19.0)
        assert r["percent_passing_min"] == 100

    def test_38in_max_only_no_min(self):
        r = table_2_15_sma_gradation(9.5)
        assert r["percent_passing_min"] is None
        assert r["percent_passing_max"] == 75

    def test_full_bands(self):
        r = table_2_15_sma_gradation()
        assert len(r["bands"]) == 8

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_2_15_sma_gradation(1.0)


# ============================================================================
# Table 2-17: SMA mix design requirements
# ============================================================================

class TestTable217:
    def test_all_parameters(self):
        r = table_2_17_sma_mix_design_requirements()
        assert r["vtm_pct"] == (3, 4)
        assert r["asphalt_content_pct_min"] == 6.0

    def test_single_parameter_stability(self):
        r = table_2_17_sma_mix_design_requirements("stability")
        assert r["value"]["stability_min_n"] == 6200

    def test_single_parameter_draindown(self):
        r = table_2_17_sma_mix_design_requirements("draindown")
        assert r["value"] == 0.3

    def test_invalid_parameter(self):
        with pytest.raises(ValueError):
            table_2_17_sma_mix_design_requirements("nonexistent")


# ============================================================================
# Spray application rates
# ============================================================================

class TestSprayApplicationRate:
    def test_prime_coat(self):
        r = spray_application_rate("prime_coat")
        assert r["rate_l_per_m2"] == (0.45, 1.13)
        assert r["rate_gal_per_yd2"] == (0.10, 0.25)

    def test_tack_coat(self):
        r = spray_application_rate("tack_coat")
        assert r["rate_gal_per_yd2"] == (0.05, 0.15)

    def test_fog_seal(self):
        r = spray_application_rate("fog_seal")
        assert r["rate_gal_per_yd2"] == (0.03, 0.08)

    def test_rejuvenator_has_sand_cover(self):
        r = spray_application_rate("rejuvenator")
        assert r["sand_cover_lb_per_yd2"] == (0.5, 1.0)

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            spray_application_rate("nonexistent")


# ============================================================================
# Table 3-2: Tack coat temperatures
# ============================================================================

class TestTable32:
    def test_cutback_rc70(self):
        r = table_3_2_tack_coat_temperature("cutback", "rc_70")
        assert r["temp_c_min"] == 49
        assert r["temp_c_max"] == 93

    def test_asphalt_cement_min_only(self):
        r = table_3_2_tack_coat_temperature("asphalt_cement", "ac_5")
        assert r["temp_c_min"] == 138
        assert r["temp_c_max"] is None

    def test_emulsion_grade_normalization(self):
        r = table_3_2_tack_coat_temperature("Emulsion", "SS-1h")
        assert r["temp_c_min"] == 21

    def test_invalid_combination(self):
        with pytest.raises(ValueError):
            table_3_2_tack_coat_temperature("cutback", "ss_1")


# ============================================================================
# Table 4-2: SBST gradation
# ============================================================================

class TestTable42:
    def test_no1_top(self):
        r = table_4_2_gradation_sbst("no_1", 19.0)
        assert r["percent_passing_min"] == 90
        assert r["percent_passing_max"] == 100

    def test_no3_top_not_tabulated(self):
        with pytest.raises(ValueError):
            table_4_2_gradation_sbst("no_3", 19.0)

    def test_full_bands(self):
        r = table_4_2_gradation_sbst("no_2")
        assert len(r["bands"]) == 7

    def test_invalid_designation(self):
        with pytest.raises(ValueError):
            table_4_2_gradation_sbst("no_9")


# ============================================================================
# Table 4-3: DBST gradation
# ============================================================================

class TestTable43:
    def test_no1_first_spreading(self):
        r = table_4_3_gradation_dbst("no_1", 4.75)
        assert r["spreading"] == "first"
        assert r["percent_passing_min"] == 0

    def test_no2_second_spreading(self):
        r = table_4_3_gradation_dbst("no_2")
        assert r["spreading"] == "second"

    def test_invalid_designation(self):
        with pytest.raises(ValueError):
            table_4_3_gradation_dbst("no_5")

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_4_3_gradation_dbst("no_1", 1.0)


# ============================================================================
# Table 4-4: Slurry seal gradation
# ============================================================================

class TestTable44:
    def test_type1_top_not_tabulated(self):
        with pytest.raises(ValueError):
            table_4_4_slurry_seal_gradation("type_1", 9.5)

    def test_type2_top(self):
        r = table_4_4_slurry_seal_gradation("type_2", 9.5)
        assert r["percent_passing_min"] == 100

    def test_type3_finest_sieve(self):
        r = table_4_4_slurry_seal_gradation("type_3", 0.075)
        assert r["percent_passing_min"] == 5
        assert r["percent_passing_max"] == 15

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            table_4_4_slurry_seal_gradation("type_9")


# ============================================================================
# Table 4-5: FRS application rate
# ============================================================================

class TestTable45:
    def test_coarse_rate(self):
        r = table_4_5_frs_application_rate("coarse")
        assert r["min_rate_l_per_m2"] == 1.35
        assert r["min_rate_gal_per_yd2"] == 0.3

    def test_fine_rate_lowest(self):
        r = table_4_5_frs_application_rate("fine")
        assert r["min_rate_gal_per_yd2"] == 0.16

    def test_sieve_lookup(self):
        r = table_4_5_frs_application_rate("medium", 0.60)
        assert r["percent_passing_min"] == 85
        assert r["percent_passing_max"] == 100

    def test_not_applicable_sieve_raises(self):
        with pytest.raises(ValueError):
            table_4_5_frs_application_rate("coarse", 0.212)

    def test_invalid_gradation(self):
        with pytest.raises(ValueError):
            table_4_5_frs_application_rate("extra_coarse")


# ============================================================================
# Table 4-7: Micro-surfacing gradation
# ============================================================================

class TestTable47:
    def test_type2_matches_slurry_seal_type2(self):
        micro = table_4_7_micro_surfacing_gradation("type_2", 4.75)
        slurry = table_4_4_slurry_seal_gradation("type_2", 4.75)
        assert micro["percent_passing_min"] == slurry["percent_passing_min"]
        assert micro["percent_passing_max"] == slurry["percent_passing_max"]

    def test_type3_full_bands(self):
        r = table_4_7_micro_surfacing_gradation("type_3")
        assert len(r["bands"]) == 8

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            table_4_7_micro_surfacing_gradation("type_1")


# ============================================================================
# Table 6-1: Cold-mix gradation
# ============================================================================

class TestTable61:
    def test_dense_graded_center_tolerance(self):
        r = table_6_1_cold_mix_gradation("dense_graded", 1, 9.5)
        assert r["percent_passing_center"] == 86
        assert r["percent_passing_tolerance"] == 9

    def test_open_graded_min_max(self):
        r = table_6_1_cold_mix_gradation("open_graded", 2, 4.75)
        assert r["percent_passing_min"] == 40
        assert r["percent_passing_max"] == 75

    def test_dense_column2_top_not_tabulated(self):
        with pytest.raises(ValueError):
            table_6_1_cold_mix_gradation("dense_graded", 2, 12.5)

    def test_invalid_mix_type(self):
        with pytest.raises(ValueError):
            table_6_1_cold_mix_gradation("semi_graded", 1)

    def test_invalid_column(self):
        with pytest.raises(ValueError):
            table_6_1_cold_mix_gradation("dense_graded", 3)


# ============================================================================
# Table 6-2: Cold-mix asphalt selection by climate
# ============================================================================

class TestTable62:
    def test_cold_climate(self):
        r = table_6_2_cold_mix_asphalt_selection("cold")
        assert r["kerosene_l_per_metric_ton"] == 8.3
        assert r["cutback_range"] == "RC-70-RC-250"

    def test_hot_climate(self):
        r = table_6_2_cold_mix_asphalt_selection("hot")
        assert r["cutback_range"] == "RC-800-RC-3000"

    def test_moderate_has_stockpile_emulsions(self):
        r = table_6_2_cold_mix_asphalt_selection("moderate")
        assert "MS-2h" in r["emulsion_stockpile"]

    def test_invalid_climate(self):
        with pytest.raises(ValueError):
            table_6_2_cold_mix_asphalt_selection("arctic")


# ============================================================================
# Table 6-3: Cold-mix optimum AC selection
# ============================================================================

class TestTable63:
    def test_all_properties(self):
        r = table_6_3_cold_mix_optimum_ac_selection()
        assert r["vtm_pct"] == (3, 5)
        assert r["vfa_pct"] == (70, 80)

    def test_single_property(self):
        r = table_6_3_cold_mix_optimum_ac_selection("vfa")
        assert r["value"] == (70, 80)

    def test_invalid_property(self):
        with pytest.raises(ValueError):
            table_6_3_cold_mix_optimum_ac_selection("nonexistent")


# ============================================================================
# Table 6-4: Cold-mix mixing temperature
# ============================================================================

class TestTable64:
    def test_emulsified_ms2(self):
        r = table_6_4_mixing_temperature("emulsified", "ms_2")
        assert r["temp_c_min"] == 38
        assert r["temp_c_max"] == 71

    def test_cutback_rc800(self):
        r = table_6_4_mixing_temperature("cutback", "rc_800")
        assert r["temp_f_min"] == 170
        assert r["temp_f_max"] == 205

    def test_invalid_combination(self):
        with pytest.raises(ValueError):
            table_6_4_mixing_temperature("emulsified", "rc_70")


# ============================================================================
# Table 7-2: RMP open-graded asphalt mixture gradation
# ============================================================================

class TestTable72:
    def test_top_sieve(self):
        r = table_7_2_ogam_gradation(19.0)
        assert r["percent_passing_min"] == 100

    def test_no200_sieve(self):
        r = table_7_2_ogam_gradation(0.075)
        assert r["percent_passing_min"] == 1
        assert r["percent_passing_max"] == 3

    def test_full_bands(self):
        r = table_7_2_ogam_gradation()
        assert len(r["bands"]) == 7

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_7_2_ogam_gradation(1.0)


# ============================================================================
# Table 7-3: RMP slurry grout gradation
# ============================================================================

class TestTable73:
    def test_no16_sieve(self):
        r = table_7_3_slurry_grout_gradation(1.18)
        assert r["percent_passing_min"] == 100

    def test_no200_sieve(self):
        r = table_7_3_slurry_grout_gradation(0.075)
        assert r["percent_passing_max"] == 2

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_7_3_slurry_grout_gradation(4.75)


# ============================================================================
# Table 7-4: RMP grout mix proportions
# ============================================================================

class TestTable74:
    def test_all_materials(self):
        r = table_7_4_grout_mix_proportions()
        assert r["silica_sand"] == (16, 20)
        assert r["cross_polymer_resin"] == (2.5, 3.5)

    def test_single_material(self):
        r = table_7_4_grout_mix_proportions("water")
        assert r["pct_by_weight_min"] == 22
        assert r["pct_by_weight_max"] == 26

    def test_invalid_material(self):
        with pytest.raises(ValueError):
            table_7_4_grout_mix_proportions("nonexistent")


# ============================================================================
# Table 7-5: RMP grout viscosity
# ============================================================================

class TestTable75:
    def test_first_30_min(self):
        r = table_7_5_grout_viscosity("0_30_min")
        assert r["marsh_cone_seconds_min"] == 8
        assert r["marsh_cone_seconds_max"] == 10

    def test_after_30_min(self):
        r = table_7_5_grout_viscosity("after_30_min")
        assert r["marsh_cone_seconds_min"] == 9

    def test_invalid_time(self):
        with pytest.raises(ValueError):
            table_7_5_grout_viscosity("after_1_hour")


# ============================================================================
# Table B-1: Slurry seal surface area factors
# ============================================================================

class TestTableB1:
    def test_no4_sieve(self):
        r = table_b1_surface_area_factor(4.75)
        assert r["factor_m2_per_kg"] == 0.4
        assert r["factor_ft2_per_lb"] == 2

    def test_no200_sieve_highest_factor(self):
        r = table_b1_surface_area_factor(0.075)
        assert r["factor_m2_per_kg"] == 32.8
        assert r["factor_ft2_per_lb"] == 160

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_b1_surface_area_factor(1.0)


# ============================================================================
# Equations: Fuller-Thompson gradation curve
# ============================================================================

class TestFullerThompson:
    def test_at_max_size_is_100_pct(self):
        r = fuller_thompson_max_density_passing(19.0, 19.0)
        assert r["percent_passing"] == 100.0

    def test_typical_value(self):
        r = fuller_thompson_max_density_passing(4.75, 19.0)
        assert r["percent_passing"] == pytest.approx(53.59, abs=0.01)

    def test_sieve_larger_than_max_raises(self):
        with pytest.raises(ValueError):
            fuller_thompson_max_density_passing(25.0, 19.0)

    def test_zero_sieve_raises(self):
        with pytest.raises(ValueError):
            fuller_thompson_max_density_passing(0, 19.0)


# ============================================================================
# Equations: Marshall/Superpave volumetric mixture properties
# ============================================================================

class TestMarshallVolumetrics:
    def test_bulk_specific_gravity(self):
        r = bulk_specific_gravity_gmb(1237.9, 1240.2, 510.9)
        assert r["gmb"] == pytest.approx(1237.9 / (1240.2 - 510.9), abs=1e-3)

    def test_bulk_specific_gravity_invalid_weights(self):
        with pytest.raises(ValueError):
            bulk_specific_gravity_gmb(1000, 500, 600)

    def test_gmb_geometric(self):
        r = bulk_specific_gravity_gmb_geometric(2500, 15.24, 6.35)
        assert r["volume_cc"] == pytest.approx(
            (3.14159265 / 4.0) * 15.24 ** 2 * 6.35, abs=1.0
        )

    def test_gmb_geometric_invalid_dims(self):
        with pytest.raises(ValueError):
            bulk_specific_gravity_gmb_geometric(2500, 0, 6.35)

    def test_air_voids(self):
        r = air_voids_vtm(2.421, 2.519)
        assert r["vv_percent"] == pytest.approx(3.89, abs=0.01)

    def test_air_voids_invalid_gmm(self):
        with pytest.raises(ValueError):
            air_voids_vtm(2.4, 0)

    def test_vma(self):
        r = voids_in_mineral_aggregate_vma(2.421, 2.700, 0.05)
        vma = 100.0 - (2.421 * (1 - 0.05) / 2.700) * 100.0
        assert r["vma_percent"] == pytest.approx(vma, abs=0.01)

    def test_vma_invalid_gsb(self):
        with pytest.raises(ValueError):
            voids_in_mineral_aggregate_vma(2.4, 0, 0.05)

    def test_vma_invalid_pb(self):
        with pytest.raises(ValueError):
            voids_in_mineral_aggregate_vma(2.4, 2.7, 1.0)

    def test_vfa(self):
        r = voids_filled_with_asphalt_vfa(14.8, 3.9)
        vfa = 100.0 * (14.8 - 3.9) / 14.8
        assert r["vfa_percent"] == pytest.approx(vfa, abs=0.01)

    def test_vfa_invalid_vma(self):
        with pytest.raises(ValueError):
            voids_filled_with_asphalt_vfa(0, 3.9)


# ============================================================================
# Equations: RMP French optimum-asphalt-content method
# ============================================================================

class TestRmpFrenchMethod:
    def test_specific_surface_area(self):
        r = rmp_specific_surface_area(30, 40, 20, 10)
        expected = 0.21 * 30 + 5.4 * 40 + 7.2 * 20 + 135.0 * 10
        assert r["sigma"] == pytest.approx(expected, abs=0.01)

    def test_optimum_asphalt_content(self):
        sigma = rmp_specific_surface_area(30, 40, 20, 10)["sigma"]
        r = rmp_optimum_asphalt_content(sigma, 2.65)
        assert r["alpha"] == pytest.approx(1.0, abs=1e-6)
        assert r["optimum_asphalt_content_pct"] > 0

    def test_optimum_ac_invalid_sigma(self):
        with pytest.raises(ValueError):
            rmp_optimum_asphalt_content(0, 2.65)

    def test_optimum_ac_invalid_sg(self):
        with pytest.raises(ValueError):
            rmp_optimum_asphalt_content(100, 0)


# ============================================================================
# Equations: Appendix B slurry-seal surface-area design method
# (end-to-end verified against the source's own worked example, Section
# B-1.4.3: SA~9.28, CSA=8.310, t=8, SGA=1.028, KA=5.7 -> AR=12.53 percent)
# ============================================================================

class TestSlurrySealSurfaceAreaMethod:
    PCT_PASSING = {
        9.5: 100, 4.75: 99.5, 2.36: 95.6, 1.18: 77.8,
        0.60: 52.0, 0.30: 24.5, 0.15: 10.7, 0.075: 6.4,
    }

    def test_surface_area(self):
        r = slurry_seal_surface_area(self.PCT_PASSING)
        assert r["surface_area_m2_per_kg"] == pytest.approx(9.28, abs=0.1)

    def test_surface_area_empty_raises(self):
        with pytest.raises(ValueError):
            slurry_seal_surface_area({})

    def test_surface_area_invalid_sieve_raises(self):
        with pytest.raises(ValueError):
            slurry_seal_surface_area({1.0: 50})

    def test_corrected_surface_area(self):
        sa = slurry_seal_surface_area(self.PCT_PASSING)["surface_area_m2_per_kg"]
        r = slurry_seal_corrected_surface_area(sa, 2.96)
        assert r["csa_m2_per_kg"] == pytest.approx(8.31, abs=0.1)

    def test_corrected_surface_area_invalid_asg(self):
        with pytest.raises(ValueError):
            slurry_seal_corrected_surface_area(9.0, 0)

    def test_asphalt_for_film_thickness_matches_worked_example(self):
        r = slurry_seal_asphalt_for_film_thickness(8.310, 8, 1.028)
        assert r["saa_pct"] == pytest.approx(6.83, abs=0.05)

    def test_total_asphalt_required_matches_worked_example(self):
        saa = slurry_seal_asphalt_for_film_thickness(8.310, 8, 1.028)["saa_pct"]
        r = slurry_seal_total_asphalt_required(saa, 5.7)
        assert r["ar_pct"] == pytest.approx(12.53, abs=0.05)

    def test_full_chain_reproduces_worked_example(self):
        sa = slurry_seal_surface_area(self.PCT_PASSING)["surface_area_m2_per_kg"]
        csa = slurry_seal_corrected_surface_area(sa, 2.96)["csa_m2_per_kg"]
        saa = slurry_seal_asphalt_for_film_thickness(csa, 8, 1.028)["saa_pct"]
        ar = slurry_seal_total_asphalt_required(saa, 5.7)["ar_pct"]
        assert ar == pytest.approx(12.53, abs=0.6)


# ============================================================================
# Structured chapter text retrieval
# ============================================================================

class TestTextRetrieval:
    def test_list_chapters_count(self):
        chs = list_chapters(REF)
        assert len(chs) == 10
        numbers = {c["chapter"] for c in chs}
        assert numbers == set(range(1, 11))

    def test_load_chapter_1_introduction(self):
        ch = load_chapter(REF, 1)
        assert ch["chapter_title"] == "Introduction"
        assert len(ch["sections"]) >= 7

    def test_load_chapter_2_hot_mix_asphalt(self):
        ch = load_chapter(REF, 2)
        assert ch["chapter_title"] == "Hot-Mix Asphalt"
        assert len(ch["sections"]) > 50

    def test_load_chapter_9_appendix_b(self):
        ch = load_chapter(REF, 9)
        assert "Best Practices" in ch["chapter_title"]

    def test_load_chapter_10_glossary(self):
        ch = load_chapter(REF, 10)
        assert "Glossary" in ch["chapter_title"]

    def test_retrieve_section_marshall_mix_design(self):
        s = retrieve_section(REF, "2-4.2")
        assert s is not None
        assert "body" in s

    def test_retrieve_section_missing_raises(self):
        with pytest.raises(KeyError):
            retrieve_section(REF, "99-99")

    def test_search_sections_marshall_stability(self):
        hits = search_sections(REF, "Marshall stability")
        assert len(hits) > 0

    def test_search_sections_prime_coat(self):
        hits = search_sections(REF, "prime coat application rate")
        assert len(hits) > 0

    def test_search_sections_resin_modified_pavement(self):
        hits = search_sections(REF, "resin modified pavement grout")
        assert len(hits) > 0
