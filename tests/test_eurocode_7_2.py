"""Tests for Eurocode 7-2 (EN 1997-2:2007) table and equation lookup functions."""

import math

import pytest

from geotech_references.eurocode_7_2.tables import (
    table_2_1_test_applicability,
    table_3_1_quality_class,
    table_d1_phi_e_from_qc,
    table_d2_alpha_oedometer,
    table_d3_pile_base_resistance,
    table_d4_pile_shaft_resistance,
    table_d5_alpha_p_alpha_s_sand,
    table_d6_alpha_s_clay_silt_peat,
    table_e1_pmt_bearing_factor_k,
    table_e2_pmt_shape_coefficients,
    table_e3_pmt_rheological_factor,
    table_e4_pmt_pile_compression_factor,
    table_f1_density_index_from_n160,
    table_f2_ageing_factor,
    table_f3_phi_from_density_index,
    table_g1_phi_from_density_index_dp,
    table_h1_phi_e_from_wst,
    table_l1_sample_mass,
    table_l2_min_mass_sieving,
    table_m1_classification_test_count,
    table_min_test_count,
    table_v1_swelling_test_specimens,
)
from geotech_references.eurocode_7_2.equations import (
    equation_4_1_cu_from_cpt,
    equation_4_2_cu_from_cptu,
    equation_4_3_oedometer_modulus_from_qc,
    equation_4_4_cu_from_fvt,
    equation_4_5_cu_from_dmt,
    equation_d2_phi_from_qc,
    equation_d3_youngs_modulus_from_qc,
    equation_d3_settlement_coefficients,
    equation_d5_stiffness_coefficient_from_qc,
    equation_burland_burbridge_icc,
    equation_burland_burbridge_shape_factor,
    equation_burland_burbridge_settlement,
    equation_g1_density_index_from_dp,
    equation_g3_stiffness_coefficient_from_dp,
    equation_i5_fvt_correction_factor,
    equation_j_dmt_oedometer_modulus,
    equation_k1_plt_undrained_shear_strength,
    equation_k2_plt_modulus,
    equation_k3_plt_subgrade_reaction,
    equation_n_caco3_from_co2,
    equation_n_so4_from_so3,
)


# ============================================================================
# Table 2.1: Test applicability
# ============================================================================

class TestTable21:
    def test_shear_strength_cpt(self):
        r = table_2_1_test_applicability("shear_strength", "cpt_cptu")
        assert r["rating"] == "C2F1"

    def test_type_of_rock_not_applicable_to_soil_sampling(self):
        r = table_2_1_test_applicability("type_of_rock", "sampling_soil_a")
        assert r["rating"] == "-"

    def test_groundwater_level_open_system(self):
        r = table_2_1_test_applicability("groundwater_level", "groundwater_open")
        assert r["rating"] == "R2C1F2"

    def test_no_method_returns_all_ratings(self):
        r = table_2_1_test_applicability("compressibility")
        assert "ratings" in r
        assert r["ratings"]["dmt"] == "C2F1"
        assert len(r["ratings"]) == 19

    def test_method_normalization(self):
        r = table_2_1_test_applicability("Shear Strength", "CPT-CPTU")
        assert r["rating"] == "C2F1"

    def test_invalid_property(self):
        with pytest.raises(ValueError):
            table_2_1_test_applicability("nonexistent")

    def test_invalid_method(self):
        with pytest.raises(ValueError):
            table_2_1_test_applicability("density", "nonexistent_method")


# ============================================================================
# Table 3.1: Quality classes
# ============================================================================

class TestTable31:
    def test_class_1_all_unchanged(self):
        r = table_3_1_quality_class(1)
        assert "compressibility_shear_strength" in r["unchanged_properties"]
        assert r["sampling_categories"] == ["A"]

    def test_class_5_nothing_unchanged(self):
        r = table_3_1_quality_class(5)
        assert r["unchanged_properties"] == []
        assert r["determinable_properties"] == ["sequence_of_layers"]
        assert r["sampling_categories"] == ["A", "B", "C"]

    def test_class_3_sampling_categories(self):
        r = table_3_1_quality_class(3)
        assert r["sampling_categories"] == ["A", "B"]

    def test_invalid_class(self):
        with pytest.raises(ValueError):
            table_3_1_quality_class(6)


# ============================================================================
# Table D.1: phi'/E' from CPT qc
# ============================================================================

class TestTableD1:
    def test_medium_dense(self):
        r = table_d1_phi_e_from_qc(7.0)
        assert r["density_index"] == "medium_dense"
        assert r["phi_min_deg"] == 35
        assert r["phi_max_deg"] == 37
        assert r["e_min_mpa"] == 20
        assert r["e_max_mpa"] == 30

    def test_very_dense_unbounded(self):
        r = table_d1_phi_e_from_qc(35.0)
        assert r["density_index"] == "very_dense"
        assert r["phi_min_deg"] == 40
        assert r["e_max_mpa"] == 90

    def test_silty_reduces_phi(self):
        sand = table_d1_phi_e_from_qc(7.0, "sand")
        silty = table_d1_phi_e_from_qc(7.0, "silty")
        assert silty["phi_min_deg"] == sand["phi_min_deg"] - 3

    def test_gravelly_increases_phi(self):
        sand = table_d1_phi_e_from_qc(7.0, "sand")
        gravelly = table_d1_phi_e_from_qc(7.0, "gravelly")
        assert gravelly["phi_min_deg"] == sand["phi_min_deg"] + 2

    def test_negative_qc_raises(self):
        with pytest.raises(ValueError):
            table_d1_phi_e_from_qc(-1)


# ============================================================================
# Table D.2: alpha for Eoed = alpha*qc
# ============================================================================

class TestTableD2:
    def test_low_plasticity_clay_mid(self):
        r = table_d2_alpha_oedometer("low_plasticity_clay", 1.0)
        assert r["alpha_min"] == 2
        assert r["alpha_max"] == 5

    def test_sand_low_qc(self):
        r = table_d2_alpha_oedometer("sand", 3.0)
        assert r["alpha_min"] == r["alpha_max"] == 2

    def test_sand_high_qc(self):
        r = table_d2_alpha_oedometer("sand", 15.0)
        assert r["alpha_min"] == r["alpha_max"] == 1.5

    def test_sand_gap_raises(self):
        with pytest.raises(ValueError):
            table_d2_alpha_oedometer("sand", 7.0)

    def test_invalid_soil_type(self):
        with pytest.raises(ValueError):
            table_d2_alpha_oedometer("granite", 1.0)


# ============================================================================
# Table D.3 / D.4: pile base/shaft resistance from qc
# ============================================================================

class TestTableD3D4:
    def test_base_resistance_exact_grid_point(self):
        r = table_d3_pile_base_resistance(0.02, 15)
        assert r["pb_mpa"] == pytest.approx(1.05)

    def test_base_resistance_interpolated(self):
        r = table_d3_pile_base_resistance(0.10, 12.5)
        assert r["pb_mpa"] == pytest.approx(2.5)

    def test_base_resistance_enlarged_base(self):
        r = table_d3_pile_base_resistance(0.02, 15, enlarged_base=True)
        assert r["pb_mpa"] == pytest.approx(1.05 * 0.75)

    def test_invalid_settlement_ratio(self):
        with pytest.raises(ValueError):
            table_d3_pile_base_resistance(0.05, 15)

    def test_shaft_resistance_exact(self):
        r = table_d4_pile_shaft_resistance(10)
        assert r["ps_mpa"] == pytest.approx(0.080)

    def test_shaft_resistance_clamped_high(self):
        r = table_d4_pile_shaft_resistance(20)
        assert r["ps_mpa"] == pytest.approx(0.120)


# ============================================================================
# Table D.5 / D.6: Dutch CPT pile method factors
# ============================================================================

class TestTableD5D6:
    def test_driven_prefab(self):
        r = table_d5_alpha_p_alpha_s_sand("driven_prefab")
        assert r["alpha_p"] == 1.0
        assert r["alpha_s"] == 0.010

    def test_flight_auger(self):
        r = table_d5_alpha_p_alpha_s_sand("flight_auger")
        assert r["alpha_p"] == 0.8
        assert r["alpha_s"] == 0.006

    def test_invalid_pile_type(self):
        with pytest.raises(ValueError):
            table_d5_alpha_p_alpha_s_sand("unknown")

    def test_clay_alpha_s(self):
        # Verified against the rendered page (pdf idx 120): clay is qc-banded.
        r = table_d6_alpha_s_clay_silt_peat("clay")
        assert r["alpha_s_max"] == 0.020          # conservative w/o qc
        assert r["alpha_s_qc_above_3"] == 0.030
        assert r["alpha_s_qc_below_3"] == 0.020
        assert table_d6_alpha_s_clay_silt_peat("clay", qc_mpa=5)["alpha_s_max"] == 0.030
        assert table_d6_alpha_s_clay_silt_peat("clay", qc_mpa=2)["alpha_s_max"] == 0.020

    def test_silt_alpha_s(self):
        r = table_d6_alpha_s_clay_silt_peat("silt")
        assert r["alpha_s_max"] == 0.025

    def test_peat_alpha_s_is_zero(self):
        # The printed table credits NO shaft resistance in peat.
        assert table_d6_alpha_s_clay_silt_peat("peat")["alpha_s_max"] == 0.0


# ============================================================================
# Table E.1: PMT bearing resistance factor k
# ============================================================================

class TestTableE1:
    def test_sand_gravel_b_square_footing(self):
        r = table_e1_pmt_bearing_factor_k("sand_and_gravel", "b", b_m=2.0, l_m=2.0, de_m=1.0)
        # k = 1.0*(1+0.5*(0.6+0.4*1)*0.5) = 1.0*(1+0.5*1.0*0.5)=1.25
        assert r["k"] == pytest.approx(1.25)

    def test_clay_silt_a(self):
        r = table_e1_pmt_bearing_factor_k("clay_and_silt", "a", b_m=1.0, l_m=1.0, de_m=0.0)
        assert r["k"] == pytest.approx(0.8)

    def test_invalid_combination(self):
        with pytest.raises(ValueError):
            table_e1_pmt_bearing_factor_k("chalk", "b", b_m=1, l_m=1, de_m=1)


# ============================================================================
# Table E.2 / E.3 / E.4: PMT shape/rheological/pile factors
# ============================================================================

class TestTableE2E3E4:
    def test_shape_coefficients_square_lb3(self):
        # Verified against the rendered page (pdf idx 123):
        # lambda_d = 1.12/1.53/1.78/2.14/2.65, lambda_c = 1.1/1.2/1.3/1.4/1.5.
        r = table_e2_pmt_shape_coefficients(3, "square")
        assert r["lambda_c"] == pytest.approx(1.3)
        assert r["lambda_l"] == pytest.approx(1.78)
        r20 = table_e2_pmt_shape_coefficients(20, "square")
        assert r20["lambda_c"] == pytest.approx(1.5)
        assert r20["lambda_l"] == pytest.approx(2.65)
        r2 = table_e2_pmt_shape_coefficients(2, "square")
        assert r2["lambda_l"] == pytest.approx(1.53)

    def test_shape_coefficients_circle_always_one(self):
        r = table_e2_pmt_shape_coefficients(5, "circle")
        assert r["lambda_l"] == pytest.approx(1.0)
        assert r["lambda_c"] == pytest.approx(1.0)

    def test_shape_coefficients_lb1(self):
        r = table_e2_pmt_shape_coefficients(1, "square")
        assert r["lambda_c"] == pytest.approx(1.1)
        assert r["lambda_l"] == pytest.approx(1.12)

    def test_shape_coefficients_below_one_raises(self):
        with pytest.raises(ValueError):
            table_e2_pmt_shape_coefficients(0.5, "square")

    def test_rheological_factor_sand_dense(self):
        r = table_e3_pmt_rheological_factor("sand_dense")
        assert r["alpha"] == 0.5

    def test_rheological_factor_rock_weathered(self):
        r = table_e3_pmt_rheological_factor("rock_weathered")
        assert r["alpha"] == 0.67

    def test_pile_compression_factor_bored(self):
        r = table_e4_pmt_pile_compression_factor("sand_and_gravel", "a", "bored")
        assert r["k"] == 1.0

    def test_pile_compression_factor_displacement(self):
        r = table_e4_pmt_pile_compression_factor("sand_and_gravel", "a", "displacement")
        assert r["k"] == 4.2


# ============================================================================
# Table F.1 / F.2 / F.3: SPT correlations
# ============================================================================

class TestTableF1F2F3:
    def test_density_index_medium(self):
        r = table_f1_density_index_from_n160(15)
        assert r["density_category"] == "medium"
        assert r["id_min_pct"] == 35
        assert r["id_max_pct"] == 65

    def test_density_index_very_dense(self):
        r = table_f1_density_index_from_n160(50)
        assert r["density_category"] == "very_dense"

    def test_density_index_out_of_range(self):
        with pytest.raises(ValueError):
            table_f1_density_index_from_n160(60)

    def test_ageing_natural_deposits(self):
        r = table_f2_ageing_factor("natural_deposits")
        assert r["n1_60_over_id2"] == 55

    def test_ageing_invalid(self):
        with pytest.raises(ValueError):
            table_f2_ageing_factor("unknown")

    def test_phi_from_id_fine_uniform(self):
        r = table_f3_phi_from_density_index(40, "fine", "uniform")
        assert r["phi_deg"] == pytest.approx(34)

    def test_phi_from_id_coarse_well_graded(self):
        r = table_f3_phi_from_density_index(100, "coarse", "well_graded")
        assert r["phi_deg"] == pytest.approx(46)

    def test_phi_from_id_interpolated(self):
        r = table_f3_phi_from_density_index(50, "fine", "uniform")
        assert 34 < r["phi_deg"] < 36


# ============================================================================
# Table G.1: DP phi' from density index
# ============================================================================

class TestTableG1:
    def test_poorly_graded_dense(self):
        r = table_g1_phi_from_density_index_dp("poorly_graded", "dense")
        assert r["phi_deg"] == 35

    def test_well_graded_dense(self):
        r = table_g1_phi_from_density_index_dp("well_graded", "dense")
        assert r["phi_deg"] == 38

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_g1_phi_from_density_index_dp("unknown", "dense")


# ============================================================================
# Table H.1: WST correlations
# ============================================================================

class TestTableH1:
    def test_dense_sand(self):
        r = table_h1_phi_e_from_wst("dense")
        assert r["phi_min_deg"] == 37
        assert r["phi_max_deg"] == 40
        assert r["e_min_mpa"] == 30
        assert r["e_max_mpa"] == 60

    def test_gravelly_adjustment(self):
        sand = table_h1_phi_e_from_wst("dense", "sand")
        gravelly = table_h1_phi_e_from_wst("dense", "gravelly")
        assert gravelly["phi_min_deg"] == sand["phi_min_deg"] + 2

    def test_invalid_density_category(self):
        with pytest.raises(ValueError):
            table_h1_phi_e_from_wst("super_dense")


# ============================================================================
# Table L.1 / L.2: sample masses
# ============================================================================

class TestTableL1L2:
    def test_water_content_masses(self):
        r = table_l1_sample_mass("water_content")
        assert r["clay_silt_g"] == 30
        assert r["sand_g"] == 100

    def test_invalid_test(self):
        with pytest.raises(ValueError):
            table_l1_sample_mass("unknown_test")

    def test_min_mass_sieving_20mm(self):
        r = table_l2_min_mass_sieving(20)
        assert r["mms_kg"] == pytest.approx(2.0)

    def test_min_mass_sieving_75mm(self):
        r = table_l2_min_mass_sieving(75)
        assert r["mms_kg"] == pytest.approx(120)

    def test_min_mass_sieving_out_of_range(self):
        with pytest.raises(ValueError):
            table_l2_min_mass_sieving(1.0)


# ============================================================================
# Table M.1 and table_min_test_count (Annexes M/P/Q/S/W)
# ============================================================================

class TestMinTestCounts:
    def test_m1_particle_size_with_experience(self):
        r = table_m1_classification_test_count("particle_size_distribution", True)
        assert r["min_count"] == 4

    def test_m1_particle_size_no_experience(self):
        r = table_m1_classification_test_count("particle_size_distribution", False)
        assert r["min_count"] == 6

    def test_m1_invalid_test(self):
        with pytest.raises(ValueError):
            table_m1_classification_test_count("unknown", True)

    def test_triaxial_phi_low_variability_extensive_experience(self):
        r = table_min_test_count("triaxial_phi", "low", "extensive")
        assert r["min_count"] == 1

    def test_triaxial_phi_high_variability_no_experience(self):
        r = table_min_test_count("triaxial_phi", "high", "none")
        assert r["min_count"] == 4

    def test_oedometer_high_variability_no_experience(self):
        r = table_min_test_count("oedometer", "high", "none")
        assert r["min_count"] == 4

    def test_permeability_high_variability(self):
        r = table_min_test_count("permeability", "high", "none")
        assert r["min_count"] == 5

    def test_rock_uniaxial_low_variability_extensive(self):
        r = table_min_test_count("rock_uniaxial_compression", "low", "extensive")
        assert r["min_count"] == 0

    def test_invalid_family(self):
        with pytest.raises(ValueError):
            table_min_test_count("unknown_family", "low", "none")

    def test_invalid_variability(self):
        with pytest.raises(ValueError):
            table_min_test_count("oedometer", "extreme", "none")


# ============================================================================
# Table V.1: rock swelling test specimens
# ============================================================================

class TestTableV1:
    def test_swelling_pressure(self):
        r = table_v1_swelling_test_specimens("swelling_pressure_zero_volume_change")
        assert r["min_specimens"] == 3
        assert r["min_thickness_mm"] == 15

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_v1_swelling_test_specimens("unknown")


# ============================================================================
# Equations: Eq. 4.1 - 4.5
# ============================================================================

class TestMainEquations:
    def test_eq_4_1_cu_from_cpt(self):
        cu = equation_4_1_cu_from_cpt(1500, 100, 15)
        assert cu == pytest.approx((1500 - 100) / 15)

    def test_eq_4_1_invalid_nk(self):
        with pytest.raises(ValueError):
            equation_4_1_cu_from_cpt(1500, 100, 0)

    def test_eq_4_2_cu_from_cptu(self):
        cu = equation_4_2_cu_from_cptu(1600, 100, 12)
        assert cu == pytest.approx(125.0)

    def test_eq_4_3_oedometer_modulus(self):
        assert equation_4_3_oedometer_modulus_from_qc(2, 5) == 10

    def test_eq_4_4_cu_from_fvt(self):
        assert equation_4_4_cu_from_fvt(0.8, 40) == pytest.approx(32.0)

    def test_eq_4_5_cu_from_dmt(self):
        cu = equation_4_5_cu_from_dmt(100, 5)
        assert cu == pytest.approx(0.22 * 100 * (0.5 * 5) ** 1.25)

    def test_eq_4_5_rejects_high_idmt(self):
        with pytest.raises(ValueError):
            equation_4_5_cu_from_dmt(100, 5, i_dmt=0.9)

    def test_eq_4_5_accepts_low_idmt(self):
        cu = equation_4_5_cu_from_dmt(100, 5, i_dmt=0.5)
        assert cu > 0


# ============================================================================
# Equations: Annex D
# ============================================================================

class TestAnnexDEquations:
    def test_d2_phi_from_qc_10(self):
        phi = equation_d2_phi_from_qc(10.0)
        assert phi == pytest.approx(13.5 * math.log10(10.0) + 23)
        assert phi == pytest.approx(36.5, abs=0.01)

    def test_d2_out_of_range(self):
        with pytest.raises(ValueError):
            equation_d2_phi_from_qc(3.0)
        with pytest.raises(ValueError):
            equation_d2_phi_from_qc(30.0)

    def test_d3_youngs_modulus_axisymmetric(self):
        assert equation_d3_youngs_modulus_from_qc(10, "axisymmetric") == 25.0

    def test_d3_youngs_modulus_plane_strain(self):
        assert equation_d3_youngs_modulus_from_qc(10, "plane_strain") == 35.0

    def test_d3_youngs_modulus_invalid_shape(self):
        with pytest.raises(ValueError):
            equation_d3_youngs_modulus_from_qc(10, "triangular")

    def test_d3_settlement_coefficients_square(self):
        r = equation_d3_settlement_coefficients(50, 150, 10, "square")
        assert r["c1"] == pytest.approx(0.75)
        assert r["c2"] == pytest.approx(1.4)
        assert r["c3"] == 1.25

    def test_d3_settlement_coefficients_strip_requires_lb(self):
        with pytest.raises(ValueError):
            equation_d3_settlement_coefficients(50, 150, 10, "strip", l_over_b=5)

    def test_d3_settlement_coefficients_strip_ok(self):
        r = equation_d3_settlement_coefficients(50, 150, 10, "strip", l_over_b=15)
        assert r["c3"] == 1.75

    def test_d5_poorly_graded_sand(self):
        w1 = equation_d5_stiffness_coefficient_from_qc("poorly_graded_sand", 10)
        assert w1 == pytest.approx(167 * math.log10(10) + 113)
        assert w1 == pytest.approx(280.0)

    def test_d5_well_graded_sand(self):
        w1 = equation_d5_stiffness_coefficient_from_qc("well_graded_sand", 10)
        assert w1 == pytest.approx(463 * math.log10(10) - 13)
        assert w1 == pytest.approx(450.0)

    def test_d5_low_plasticity_clay(self):
        w1 = equation_d5_stiffness_coefficient_from_qc("low_plasticity_clay", 1.0)
        assert w1 == pytest.approx(15.2 * 1.0 + 50)
        assert w1 == pytest.approx(65.2)

    def test_d5_out_of_range(self):
        with pytest.raises(ValueError):
            equation_d5_stiffness_coefficient_from_qc("low_plasticity_clay", 5.0)


# ============================================================================
# Equations: Annex F.3 (Burland & Burbridge)
# ============================================================================

class TestBurlandBurbridge:
    def test_icc(self):
        icc = equation_burland_burbridge_icc(20)
        assert icc == pytest.approx(1.71 / 20 ** 1.4)

    def test_icc_invalid(self):
        with pytest.raises(ValueError):
            equation_burland_burbridge_icc(0)

    def test_shape_factor_square(self):
        assert equation_burland_burbridge_shape_factor(1) == pytest.approx(1.0)

    def test_shape_factor_tends_to_1_56(self):
        fs = equation_burland_burbridge_shape_factor(1000)
        assert fs == pytest.approx(1.5625, abs=0.001)

    def test_shape_factor_invalid(self):
        with pytest.raises(ValueError):
            equation_burland_burbridge_shape_factor(0.5)

    def test_settlement_normally_consolidated(self):
        si = equation_burland_burbridge_settlement(2, 0.05, 200, 50)
        assert si == pytest.approx((200 - 50) * 2 ** 0.7 * 0.05)

    def test_settlement_over_consolidated(self):
        si = equation_burland_burbridge_settlement(2, 0.05, 40, 50)
        assert si == pytest.approx(50 * 2 ** 0.7 * 0.05 / 3)

    def test_settlement_invalid_width(self):
        with pytest.raises(ValueError):
            equation_burland_burbridge_settlement(0, 0.05, 200, 50)


# ============================================================================
# Equations: Annex G (dynamic probing)
# ============================================================================

class TestAnnexGEquations:
    def test_g1_poorly_graded_above_dpl(self):
        id_ = equation_g1_density_index_from_dp(10, "poorly_graded", "above", "dpl")
        assert id_ == pytest.approx(0.15 + 0.260 * math.log10(10))

    def test_g1_well_graded_above_dph(self):
        id_ = equation_g1_density_index_from_dp(10, "well_graded", "above", "dph")
        assert id_ == pytest.approx(0.14 + 0.550 * math.log10(10))

    def test_g1_invalid_combination(self):
        with pytest.raises(ValueError):
            equation_g1_density_index_from_dp(10, "well_graded", "below", "dpl")

    def test_g3_sand_dpl(self):
        w1 = equation_g3_stiffness_coefficient_from_dp(10, "sand", "dpl")
        assert w1 == pytest.approx(214 * math.log10(10) + 71)

    def test_g3_clay_dph(self):
        w1 = equation_g3_stiffness_coefficient_from_dp(10, "clay", "dph")
        assert w1 == pytest.approx(6 * 10 + 50)

    def test_g3_invalid(self):
        with pytest.raises(ValueError):
            equation_g3_stiffness_coefficient_from_dp(10, "silt", "dpl")


# ============================================================================
# Equations: Annex I.5 (FVT correction factor)
# ============================================================================

class TestAnnexI5:
    def test_base_formula(self):
        # wL is used as a fraction internally (60% -> 0.60); see the
        # equation's docstring for why (Figure I.1's 0-200% chart range
        # and the mu>=0.5 floor kicking in at wL~200% both confirm this).
        mu = equation_i5_fvt_correction_factor(60)
        assert mu == pytest.approx((0.43 / 0.60) ** 0.45)

    def test_base_formula_floored_at_half(self):
        mu = equation_i5_fvt_correction_factor(200)
        assert mu == pytest.approx(0.5, abs=1e-3)

    def test_roc_variant(self):
        mu = equation_i5_fvt_correction_factor(60, roc=2.0)
        base = (0.43 / 0.60) ** 0.45
        assert mu == pytest.approx(base * (2.0 / 1.3) ** -0.15)

    def test_roc_at_or_below_threshold_raises(self):
        with pytest.raises(ValueError):
            equation_i5_fvt_correction_factor(60, roc=1.2)

    def test_cfv_variant(self):
        mu = equation_i5_fvt_correction_factor(60, cfv_kpa=40, sigma_v0_eff_kpa=50)
        base = (0.43 / 0.60) ** 0.45
        assert mu == pytest.approx(base * (40 / (0.585 * 0.60 * 50)) ** -0.15)

    def test_cfv_without_sigma_raises(self):
        with pytest.raises(ValueError):
            equation_i5_fvt_correction_factor(60, cfv_kpa=40)

    def test_invalid_wl(self):
        with pytest.raises(ValueError):
            equation_i5_fvt_correction_factor(0)


# ============================================================================
# Equations: Annex J (DMT oedometer modulus)
# ============================================================================

class TestAnnexJ:
    def test_low_idmt(self):
        r = equation_j_dmt_oedometer_modulus(0.5, 5, 10)
        expected_rm = 0.14 + 2.36 * math.log10(5)
        assert r["rm"] == pytest.approx(expected_rm, abs=1e-3)
        assert r["eoed_mpa"] == pytest.approx(expected_rm * 10, abs=1e-2)

    def test_mid_idmt(self):
        r = equation_j_dmt_oedometer_modulus(1.5, 5, 10)
        rm0 = 0.14 + 0.15 * (1.5 - 0.6)
        expected_rm = rm0 + (2.5 - rm0) * math.log10(5)
        assert r["rm"] == pytest.approx(expected_rm, abs=1e-3)

    def test_high_idmt(self):
        r = equation_j_dmt_oedometer_modulus(4.0, 5, 10)
        expected_rm = 0.5 + 2 * math.log10(5)
        assert r["rm"] == pytest.approx(expected_rm, abs=1e-3)

    def test_high_kdmt_override(self):
        r = equation_j_dmt_oedometer_modulus(0.5, 20, 10)
        expected_rm = 0.32 + 2.18 * math.log10(20)
        assert r["rm"] == pytest.approx(expected_rm, abs=1e-3)

    def test_rm_floor(self):
        r = equation_j_dmt_oedometer_modulus(0.5, 1.0, 10)
        assert r["rm"] == 0.85

    def test_invalid_kdmt(self):
        with pytest.raises(ValueError):
            equation_j_dmt_oedometer_modulus(0.5, 0, 10)


# ============================================================================
# Equations: Annex K (PLT)
# ============================================================================

class TestAnnexK:
    def test_k1_surface(self):
        cu = equation_k1_plt_undrained_shear_strength(300, 20, "surface")
        assert cu == pytest.approx((300 - 20) / 6)

    def test_k1_deep_borehole(self):
        cu = equation_k1_plt_undrained_shear_strength(300, 20, "borehole_deep")
        assert cu == pytest.approx((300 - 20) / 9)

    def test_k1_invalid_condition(self):
        with pytest.raises(ValueError):
            equation_k1_plt_undrained_shear_strength(300, 20, "midway")

    def test_k2_modulus_surface(self):
        e = equation_k2_plt_modulus(100, 5, 0.3, poisson=0.3)
        assert e == pytest.approx((100 / 5) * math.pi * 0.3 * (1 - 0.3 ** 2) / 4)

    def test_k2_modulus_borehole_with_cz(self):
        e_no_cz = equation_k2_plt_modulus(100, 5, 0.3, poisson=0.3, cz=1.0)
        e_cz = equation_k2_plt_modulus(100, 5, 0.3, poisson=0.3, cz=0.8)
        assert e_cz == pytest.approx(e_no_cz * 0.8)

    def test_k2_invalid_settlement(self):
        with pytest.raises(ValueError):
            equation_k2_plt_modulus(100, 0, 0.3)

    def test_k3_subgrade_reaction(self):
        ks = equation_k3_plt_subgrade_reaction(100, 5)
        assert ks == pytest.approx(20.0)

    def test_k3_invalid(self):
        with pytest.raises(ValueError):
            equation_k3_plt_subgrade_reaction(100, 0)


# ============================================================================
# Equations: Annex N (chemical unit conversions)
# ============================================================================

class TestAnnexN:
    def test_caco3_from_co2(self):
        assert equation_n_caco3_from_co2(10) == pytest.approx(22.73)

    def test_caco3_negative_raises(self):
        with pytest.raises(ValueError):
            equation_n_caco3_from_co2(-1)

    def test_so4_from_so3(self):
        assert equation_n_so4_from_so3(10) == pytest.approx(12.0)

    def test_so4_negative_raises(self):
        with pytest.raises(ValueError):
            equation_n_so4_from_so3(-1)
