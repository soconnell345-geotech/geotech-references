"""Tests for geotech_references.california_trenching (Caltrans Trenching and
Shoring Manual, June 2011, Revision 2 - July 2025).

Covers the geotech / excavation-engineering lookups, with values cross-checked
against the source PDF (worked examples and printed tables):
  - Cal/OSHA Type A/B/C soil classification and maximum allowable slopes (Ch 2).
  - Soil property tables (Ch 3): granular (3-1), simplified/Ka (3-2), cohesive
    (3-3), test reliability (3-4).
  - Earth pressure coefficients and apparent active coefficient (Ch 4).
  - Apparent earth pressure (AEP) envelopes and stability number (Ch 8).
  - Bottom-heave factor of safety (Ch 10), verified vs Example 10-2.

Units are the manual's native US customary units (psf, pcf, tsf, ft, deg).
"""

import math

import pytest

from geotech_references.california_trenching.tables import (
    osha_soil_classification,
    osha_soil_type_from_qu,
    table_2_1_max_allowable_slope,
    osha_timber_shoring_pressure,
    table_3_1_granular_properties,
    table_3_2_simplified_soil_values,
    table_3_3_cohesive_properties,
    table_3_4_test_reliability,
    table_4_1_mobilized_wall_movements,
    table_4_2_wall_friction,
    matrix_4_1_passive_reduction_factor,
    overstress_factor,
    lagging_design_load,
    effective_pile_width_arching,
    factor_of_safety_requirements,
)
from geotech_references.california_trenching.equations import (
    rankine_ka,
    rankine_kp,
    coulomb_ka,
    at_rest_k0,
    log_spiral_passive_kp,
    lateral_earth_pressure_resultant,
    apparent_active_coefficient,
    tension_crack_depth,
    max_allowable_slope_angle,
    uniform_surcharge_pressure,
    minimum_construction_surcharge,
    aep_single_level_cohesionless,
    aep_multi_level_cohesionless,
    stability_number,
    aep_cohesive_max_ordinate,
    heave_factor_of_safety,
)


# ===================================================================
# CAL/OSHA SOIL CLASSIFICATION + MAX ALLOWABLE SLOPES (Chapter 2)
# ===================================================================


class TestOshaSoilClassification:
    def test_three_types_plus_rock(self):
        types = osha_soil_classification()["types"]
        assert set(types) == {"stable_rock", "a", "b", "c"}

    def test_type_a_threshold_1p5_tsf(self):
        a = osha_soil_classification()["types"]["a"]
        assert a["qu_min_tsf"] == 1.5

    @pytest.mark.parametrize("qu, expected", [
        (2.0, "A"), (1.5, "A"),
        (1.0, "B"), (0.51, "B"),
        (0.5, "C"), (0.25, "C"), (0.0, "C"),
    ])
    def test_type_from_qu(self, qu, expected):
        assert osha_soil_type_from_qu(qu)["osha_type"] == expected

    def test_negative_qu_raises(self):
        with pytest.raises(ValueError):
            osha_soil_type_from_qu(-0.1)


class TestMaxAllowableSlope:
    @pytest.mark.parametrize("soil, label, hv", [
        ("stable_rock", "Vertical", 0.0),
        ("A", "3/4:1", 0.75),
        ("B", "1:1", 1.0),
        ("C", "1-1/2:1", 1.5),
    ])
    def test_table_2_1(self, soil, label, hv):
        r = table_2_1_max_allowable_slope(soil)
        assert r["ratio_label"] == label
        assert r["ratio_h_per_v"] == hv

    def test_full_table(self):
        rows = table_2_1_max_allowable_slope()["rows"]
        assert len(rows) == 4

    def test_cites_table_and_page(self):
        r = table_2_1_max_allowable_slope("C")
        assert r["table"] == "2-1"

    def test_type_c_45_degrees(self):
        # 1.5:1 (H:V) -> arctan(1/1.5) ~ 33.7 deg
        assert table_2_1_max_allowable_slope("C")["slope_angle_deg"] == pytest.approx(33.7, abs=0.2)

    def test_bad_type_raises(self):
        with pytest.raises(ValueError):
            table_2_1_max_allowable_slope("Z")


class TestOshaTimberPressure:
    @pytest.mark.parametrize("soil, slope", [("A", 25), ("B", 45), ("C", 80)])
    def test_pa_slopes(self, soil, slope):
        r = osha_timber_shoring_pressure(soil, 10)
        assert r["slope_psf_per_ft"] == slope
        # PA = m*H + 72
        assert r["pa_psf"] == pytest.approx(slope * 10 + 72)

    def test_bad_type(self):
        with pytest.raises(ValueError):
            osha_timber_shoring_pressure("D", 5)


# ===================================================================
# SOIL PROPERTY TABLES (Chapter 3)
# ===================================================================


class TestGranularProperties:
    def test_five_density_classes(self):
        rows = table_3_1_granular_properties()["rows"]
        assert len(rows) == 5

    def test_dense_friction_angle(self):
        r = table_3_1_granular_properties("dense")
        assert r["friction_angle_min_deg"] == 37
        assert r["friction_angle_max_deg"] == 41

    def test_bad_density(self):
        with pytest.raises(ValueError):
            table_3_1_granular_properties("squishy")

    def test_every_printed_row(self):
        # Table 3-1, Properties of Granular Soils (PDF p. 43, printed p. 3-5).
        # Columns: friction angle (deg), unit weight moist (pcf), unit weight
        # submerged (pcf). An open-ended cell is (None, x) or (x, None).
        printed = {
            "very loose": ((None, 28), (None, 100), (None, 60)),    # <28, <100, <60
            "loose": ((28, 30), (95, 125), (55, 65)),
            "medium dense": ((31, 36), (110, 130), (60, 70)),
            "dense": ((37, 41), (110, 140), (65, 85)),
            "very dense": ((41, None), (130, None), (75, None)),   # >41, >130, >75
        }
        for density, (phi, moist, submerged) in printed.items():
            r = table_3_1_granular_properties(density)
            assert (r["friction_angle_min_deg"], r["friction_angle_max_deg"]) == phi
            assert (r["unit_weight_moist_pcf_min"], r["unit_weight_moist_pcf_max"]) == moist
            assert (r["unit_weight_submerged_pcf_min"],
                    r["unit_weight_submerged_pcf_max"]) == submerged

    def test_very_loose_row_in_the_whole_table(self):
        # The Very Loose row used to read moist: none, submerged: 60 to 100.
        row = table_3_1_granular_properties()["rows"][0]
        assert row["apparent_density"] == "Very Loose"
        assert row["unit_weight_moist_pcf_max"] == 100
        assert row["unit_weight_submerged_pcf_max"] == 60
        assert row["unit_weight_submerged_pcf_min"] is None


class TestSimplifiedSoilValues:
    def test_gravel_dense_ka_and_efp(self):
        # Table 3-2: dense gravel/coarse sand -> phi=41, gamma=130, Ka=0.21, Kw=27
        r = table_3_2_simplified_soil_values("gravel", "dense")
        row = r["rows"][0]
        assert row["friction_angle_deg"] == 41
        assert row["unit_weight_pcf"] == 130
        assert row["ka"] == 0.21
        assert row["equivalent_fluid_weight_pcf"] == 27

    def test_fine_sand_loose(self):
        r = table_3_2_simplified_soil_values("fine sand", "loose")
        row = r["rows"][0]
        assert row["ka"] == 0.41
        assert row["friction_angle_deg"] == 25

    def test_full_table(self):
        assert len(table_3_2_simplified_soil_values()["rows"]) == 15

    def test_bad_class(self):
        with pytest.raises(ValueError):
            table_3_2_simplified_soil_values("moon dust")


class TestCohesiveProperties:
    @pytest.mark.parametrize("consistency, qmin, qmax", [
        ("very soft", 0, 500),
        ("soft", 500, 1000),
        ("medium stiff", 1000, 2000),
        ("stiff", 2000, 4000),
        ("very stiff", 4000, 8000),
        ("hard", 8000, None),
    ])
    def test_qu_ranges(self, consistency, qmin, qmax):
        r = table_3_3_cohesive_properties(consistency)
        assert r["unconfined_compressive_strength_psf_min"] == qmin
        assert r["unconfined_compressive_strength_psf_max"] == qmax


class TestTestReliability:
    def test_vane_shear_very_good_fine(self):
        rows = table_3_4_test_reliability()["rows"]
        vane = next(r for r in rows if "Vane Shear" in r["test_method"])
        assert vane["fine_grained"] == "Very good"

    def test_spt_poor_for_fine(self):
        rows = table_3_4_test_reliability()["rows"]
        spt = next(r for r in rows if r["test_method"].startswith("Standard"))
        assert spt["fine_grained"] == "Poor"


# ===================================================================
# EARTH PRESSURE COEFFICIENTS (Chapter 4)
# ===================================================================


class TestRankine:
    def test_ka_phi_30_is_one_third(self):
        # Ka = tan^2(45-15) = 0.333
        assert rankine_ka(30)["ka"] == pytest.approx(0.3333, abs=1e-3)

    def test_kp_phi_30_is_three(self):
        # Kp = tan^2(45+15) = 3.0
        assert rankine_kp(30)["kp"] == pytest.approx(3.0, abs=1e-3)

    def test_kp_sloping_backfill_warns(self):
        r = rankine_kp(30, 10)
        assert "warning" in r

    def test_beta_gt_phi_raises(self):
        with pytest.raises(ValueError):
            rankine_ka(20, 30)


class TestCoulomb:
    def test_coulomb_reduces_to_rankine_when_no_friction(self):
        # delta=0, beta=0, omega=0 -> Coulomb Ka == Rankine Ka
        ck = coulomb_ka(30, 0, 0, 0)["ka"]
        rk = rankine_ka(30)["ka"]
        assert ck == pytest.approx(rk, abs=1e-3)


class TestAtRest:
    def test_k0_nc_level(self):
        # K0 = 1 - sin(30) = 0.5
        assert at_rest_k0(30)["k0"] == pytest.approx(0.5, abs=1e-3)

    def test_k0_oc_increases(self):
        nc = at_rest_k0(30, ocr=1.0)["k0"]
        oc = at_rest_k0(30, ocr=4.0)["k0"]
        assert oc > nc

    def test_ocr_below_one_raises(self):
        with pytest.raises(ValueError):
            at_rest_k0(30, ocr=0.5)


class TestLogSpiralPassive:
    def test_kp_prime_is_R_times_kp(self):
        # PDF example: Kp=19, R=0.679 -> Kp' = 13 (12.9)
        r = log_spiral_passive_kp(19, 0.679)
        assert r["kp_prime"] == pytest.approx(12.9, abs=0.1)

    def test_example_8_1_kph(self):
        # Example 8-1: Kp=6.3, R=0.746 -> Kph = 4.7
        assert log_spiral_passive_kp(6.3, 0.746)["kp_prime"] == pytest.approx(4.7, abs=0.05)

    def test_matrix_4_1_exact_values(self):
        # Matrix 4-1: phi=32, delta/phi=0.44 -> R = 0.679
        assert matrix_4_1_passive_reduction_factor(32, 0.44)["R"] == 0.679
        assert matrix_4_1_passive_reduction_factor(30, 0.5)["R"] == 0.746
        assert matrix_4_1_passive_reduction_factor(35, 0.4)["R"] == 0.603

    def test_matrix_4_1_untabulated_raises(self):
        with pytest.raises(ValueError):
            matrix_4_1_passive_reduction_factor(40, 0.5)


class TestLateralPressureAndApparent:
    def test_resultant_acts_at_h_over_3(self):
        r = lateral_earth_pressure_resultant(120, 12, 0.33)
        assert r["resultant_height_ft"] == pytest.approx(4.0)
        # P = 0.5 * 120 * 144 * 0.33
        assert r["resultant_plf"] == pytest.approx(0.5 * 120 * 144 * 0.33, abs=1)

    def test_kapparent_floor_025(self):
        # sigma_a so low that Kapparent < 0.25 -> design 0.25
        r = apparent_active_coefficient(100, 120, 20)
        assert r["kapparent_design"] == 0.25
        assert r["floor_governs"] is True

    def test_kapparent_above_floor(self):
        r = apparent_active_coefficient(900, 120, 20)
        assert r["kapparent_design"] > 0.25
        assert r["floor_governs"] is False

    def test_tension_crack_depth(self):
        # hcr = 2c/(gamma*sqrt(Ka)); c=500, gamma=120, Ka=0.33
        r = tension_crack_depth(500, 120, 0.33)
        assert r["hcr_ft"] == pytest.approx(2 * 500 / (120 * 0.33 ** 0.5), abs=0.05)


# ===================================================================
# MAXIMUM ALLOWABLE SLOPE ANGLE (Chapter 4-5)
# ===================================================================


class TestMaxAllowableSlopeAngle:
    # Eqs. 4-5-1..4-5-4 (PDF p.72): sin(beta) <= sin(phi) + (c/l) cos(phi),
    # with l from Eq. 4-5-2 and sigma_v/sigma_x from Eqs. 4-5-3/4-5-4. The
    # limiting beta is solved (beta depends on l, which depends on beta).
    def test_cohesionless_equals_phi(self):
        # c=0 -> l = sigma_x/cos^2(phi) > 0, RHS = sin(phi) -> beta = phi
        r = max_allowable_slope_angle(30, 0, 120, 10)
        assert r["beta_max_deg"] == pytest.approx(30.0, abs=0.1)

    def test_cohesion_allows_steeper(self):
        # moderate cohesion (l stays > 0 at beta = phi) lets the slope stand
        # steeper than phi
        r = max_allowable_slope_angle(30, 200, 120, 15)
        assert not r["degenerate"]
        assert r["beta_max_deg"] > 30.0

    def test_cosphi_term_present(self):
        # The corrected Eq. 4-5-1 carries the cos(phi) factor on the cohesion
        # term and the stress quantity l (Eq. 4-5-2), not the old c/(gamma*h)
        # form. The result must therefore reflect l, exposed in the output.
        r = max_allowable_slope_angle(30, 200, 120, 15)
        assert "l" in r and "sigma_v" in r and "sigma_x" in r

    def test_large_cohesion_degenerate(self):
        # The printed Eq. 4-5-2 mixes stress / stress^2 terms, so a large c
        # relative to gamma*H drives l <= 0 at beta = phi: the closed form is
        # degenerate and beta_max defaults to phi (use a slope-stability check).
        r = max_allowable_slope_angle(20, 1000, 120, 10)
        assert r["degenerate"] is True
        assert r["beta_max_deg"] == pytest.approx(20.0, abs=0.1)

    def test_the_result_note_opens_with_the_caution(self):
        # Eq. 4-5-2 (PDF p. 73, printed p. 4-22) as typeset adds sigma_x (a
        # stress) to 1/2 sin(2 phi) (a number) and, under the root, a stress
        # term to stress-squared terms. The caution used to sit at the end
        # of a long note; it now opens it, in both forms of the result.
        r = max_allowable_slope_angle(30, 200, 120, 20)
        assert r["note"].startswith("CAUTION: Eq. 4-5-2 is not dimensionally consistent")
        assert "slope stability analysis" in r["note"][:420]
        r = max_allowable_slope_angle(30, 200, 120, 20, beta_deg=35)
        assert r["note"].startswith("CAUTION: Eq. 4-5-2 is not dimensionally consistent")

    def test_the_printed_equations_are_still_solved_as_before(self):
        # No change to the numbers: the lookup is left as the print.
        assert max_allowable_slope_angle(30, 200, 120, 20)["beta_max_deg"] == pytest.approx(40.52, abs=0.01)
        assert max_allowable_slope_angle(30, 0, 120, 20)["beta_max_deg"] == pytest.approx(30.0, abs=0.01)

    def test_single_point_check(self):
        # Evaluating at a supplied beta returns the Eq. 4-5-1 RHS and whether
        # the inequality is satisfied at that beta.
        r = max_allowable_slope_angle(30, 200, 120, 15, beta_deg=35)
        assert "satisfies_4_5_1" in r and "sin_beta_rhs" in r


# ===================================================================
# SURCHARGES (Chapter 5)
# ===================================================================


class TestSurcharge:
    def test_uniform_surcharge(self):
        # sigma_h = K*Q
        assert uniform_surcharge_pressure(300, 0.33)["sigma_h_psf"] == pytest.approx(99.0)

    def test_minimum_construction_surcharge(self):
        r = minimum_construction_surcharge()
        assert r["sigma_h_psf"] == 72.0
        assert r["min_depth_ft"] == 10.0


# ===================================================================
# APPARENT EARTH PRESSURE (Chapter 8)
# ===================================================================


class TestApparentEarthPressure:
    def test_single_level_pt_is_1p3_p(self):
        r = aep_single_level_cohesionless(120, 20, 0.33)
        assert r["pt_trapezoidal_plf"] == pytest.approx(1.3 * r["p_triangular_plf"])

    def test_multi_level_ordinate(self):
        # sigma_a = 1.3P / [H - (1/3)(H1+Hn+1)]
        r = aep_multi_level_cohesionless(120, 30, 0.33, h1_ft=6, hn1_ft=6)
        p = 0.5 * 120 * 30 ** 2 * 0.33
        expected = 1.3 * p / (30 - (6 + 6) / 3.0)
        assert r["sigma_a_psf"] == pytest.approx(expected, abs=1)

    def test_multi_level_bad_geometry_raises(self):
        with pytest.raises(ValueError):
            aep_multi_level_cohesionless(120, 10, 0.33, h1_ft=20, hn1_ft=20)

    def test_stability_number(self):
        # Ns = gamma*H/cu = 120*30/500 = 7.2
        assert stability_number(120, 30, 500)["ns"] == pytest.approx(7.2, abs=0.01)

    def test_cohesive_stiff_envelope(self):
        # Ns <= 4 -> sigma_a = factor * gamma * H
        r = aep_cohesive_max_ordinate(120, 20, ns=3, factor=0.3)
        assert r["sigma_a_psf"] == pytest.approx(0.3 * 120 * 20)

    def test_cohesive_soft_envelope(self):
        # Ns >= 6 -> sigma_a = Ka * gamma * H
        r = aep_cohesive_max_ordinate(120, 20, ns=7, ka=0.3)
        assert r["sigma_a_psf"] == pytest.approx(0.3 * 120 * 20)

    def test_cohesive_soft_requires_ka(self):
        with pytest.raises(ValueError):
            aep_cohesive_max_ordinate(120, 20, ns=7)

    def test_cohesive_ka_floor(self):
        with pytest.raises(ValueError):
            aep_cohesive_max_ordinate(120, 20, ns=7, ka=0.1)


# ===================================================================
# BOTTOM HEAVE (Chapter 10) — verified vs Example 10-2
# ===================================================================


class TestHeave:
    def test_example_10_2_resisting_force(self):
        # Example 10-2: c=500, Nc=7.6, gamma=120, H=30, B=15, q=300
        # Qu = c*Nc*(0.7B) = 500*7.6*(0.7*15) = 39,900 plf (PDF "~40 kip/ft")
        r = heave_factor_of_safety(500, 7.6, 120, 30, 15, surcharge_psf=300)
        assert r["resisting_force_Qu_plf"] == pytest.approx(39900.0, abs=1)

    def test_fs_required_1p5(self):
        r = heave_factor_of_safety(500, 7.6, 120, 30, 15, surcharge_psf=300)
        assert r["fs_required"] == 1.5

    def test_high_cohesion_no_heave(self):
        # very high cohesion -> driving force <= 0 -> infinite FS, adequate
        r = heave_factor_of_safety(5000, 7.6, 120, 10, 15)
        assert r["adequate"] is True

    def test_bad_cohesion_raises(self):
        with pytest.raises(ValueError):
            heave_factor_of_safety(0, 7.6, 120, 30, 15)

    def test_no_driving_force_gives_null_not_infinity(self):
        # Eq. 10-3-2 (PDF p. 225, printed p. 10-16): Q = W + (0.7B)q - S with
        # W = gamma H (0.7B) and S = cH. c 5000 psf, H 10 ft, B 15 ft:
        # W = 12,600, S = 50,000 plf, so Q is negative and FS = QU/Q
        # (Eq. 10-3-5, printed p. 10-19) has no value. "fs" used to be
        # float("inf"), which is not valid JSON.
        import json
        r = heave_factor_of_safety(5000, 7.6, 120, 10, 15)
        assert r["weight_W_plf"] == pytest.approx(12600.0)
        assert r["cohesion_resistance_S_plf"] == pytest.approx(50000.0)
        assert r["driving_force_Q_plf"] < 0
        assert r["fs"] is None
        assert r["adequate"] is True
        assert "has no value" in r["note"]
        assert "Infinity" not in json.dumps(r, allow_nan=False)

    def test_adequacy_is_tested_on_the_unrounded_ratio(self):
        # Eq. 10-3-5 (PDF p. 228, printed p. 10-19): FS = QU/Q >= 1.5.
        # c 100 psf, Nc 7.5, H 10 ft, B 10 ft (0.7B = 7 ft): QU = 5,250 plf.
        # gamma 64.299 pcf: Q = 64.299 x 10 x 7 - 100 x 10 = 3,500.93,
        # QU/Q = 1.49960, which reports as 1.5 and is not adequate.
        for gamma in (64.299, 64.29, 64.3):
            r = heave_factor_of_safety(100, 7.5, gamma, 10, 10)
            ratio = 5250.0 / (gamma * 10 * 7 - 1000.0)
            assert 1.4995 < ratio < 1.5
            assert r["fs"] == pytest.approx(1.5)
            assert r["adequate"] is False
        # just above: gamma 64.28 -> QU/Q = 1.50017
        r = heave_factor_of_safety(100, 7.5, 64.28, 10, 10)
        assert 5250.0 / (64.28 * 70 - 1000.0) > 1.5
        assert r["adequate"] is True

    def test_factor_of_safety_from_the_printed_equations(self):
        # Eqs. 10-3-2, 10-3-3, 10-3-5 with made-up values: c 500 psf, Nc 7.6,
        # gamma 120 pcf, H 30 ft, B 15 ft, q 300 psf.
        # W = 120 x 30 x 10.5 = 37,800; S = 500 x 30 = 15,000;
        # Q = 37,800 + 10.5 x 300 - 15,000 = 25,950; QU = 500 x 7.6 x 10.5 = 39,900
        r = heave_factor_of_safety(500, 7.6, 120, 30, 15, surcharge_psf=300)
        assert r["driving_force_Q_plf"] == pytest.approx(25950.0)
        assert r["fs"] == pytest.approx(39900.0 / 25950.0, abs=1e-3)
        assert r["adequate"] is True


# ===================================================================
# STRUCTURAL / PILE-WIDTH / FS SUMMARY (Chapters 6, 7)
# ===================================================================


class TestStructural:
    def test_overstress_factor(self):
        r = overstress_factor()
        assert r["overstress_factor"] == 1.33
        assert len(r["exceptions"]) == 4

    def test_lagging_arching_reduction(self):
        # 0.6 * earth pressure
        r = lagging_design_load(500, surcharge_present=False)
        assert r["lagging_load_psf"] == pytest.approx(300.0)

    def test_lagging_cap_400_no_surcharge(self):
        r = lagging_design_load(1000, surcharge_present=False)
        assert r["lagging_load_psf"] == 400.0
        assert r["cap_applied"] is True

    def test_lagging_no_cap_with_surcharge(self):
        r = lagging_design_load(1000, surcharge_present=True)
        assert r["lagging_load_psf"] == pytest.approx(600.0)
        assert r["cap_applied"] is False

    def test_arching_granular_factor(self):
        # f = 0.08 * phi; phi=35 -> 2.8
        r = effective_pile_width_arching(1.0, phi_deg=35)
        assert r["arching_factor"] == pytest.approx(2.8)

    def test_arching_capped_at_3(self):
        # phi=45 -> 0.08*45 = 3.6 -> capped at 3
        r = effective_pile_width_arching(1.0, phi_deg=45)
        assert r["arching_factor"] == 3.0

    def test_arching_limited_by_spacing(self):
        r = effective_pile_width_arching(2.0, phi_deg=35, pile_spacing_ft=4.0)
        assert r["adjusted_width_ft"] == 4.0
        assert r["limited_by_spacing"] is True

    def test_arching_cohesive_needs_factor(self):
        with pytest.raises(ValueError):
            effective_pile_width_arching(1.0, cohesive=True)

    def test_fs_requirements_summary(self):
        reqs = factor_of_safety_requirements()["requirements"]
        items = {r["item"]: r["fs"] for r in reqs}
        assert any("embedment" in k.lower() and v == 1.3 for k, v in items.items())
        assert any("heave" in k.lower() and v == 1.5 for k, v in items.items())

    def test_anchor_block_factor_of_safety_is_2(self):
        # Section 10-2 (PDF p. 213, printed p. 10-4): "a safety factor of 2
        # is recommended for all anchor blocks". The summary used to say 1.5.
        reqs = factor_of_safety_requirements()["requirements"]
        anchor = [r for r in reqs if "anchor block" in r["item"].lower()]
        assert len(anchor) == 1
        assert anchor[0]["fs"] == 2.0
        assert "safety factor of 2 is recommended for all anchor blocks" in anchor[0]["basis"]
        assert "10-4" in anchor[0]["basis"]


# ===================================================================
# TEXT RETRIEVAL — chapter JSON
# ===================================================================


class TestTextRetrieval:
    def test_chapter_4_loads(self):
        from geotech_references import _retrieval
        ch = _retrieval.load_chapter("california_trenching", 4)
        assert ch["chapter"] == 4
        assert any(s["section_id"] == "4-4" for s in ch["sections"])

    def test_chapter_8_loads(self):
        from geotech_references import _retrieval
        ch = _retrieval.load_chapter("california_trenching", 8)
        assert any(s["section_id"] == "8-3" for s in ch["sections"])

    def test_search_finds_apparent_pressure(self):
        from geotech_references import _retrieval
        hits = _retrieval.search_sections("california_trenching", "apparent earth pressure trapezoidal")
        assert len(hits) > 0

    def test_list_chapters(self):
        from geotech_references import _retrieval
        chs = {c["chapter"] for c in _retrieval.list_chapters("california_trenching")}
        assert {2, 3, 4, 6, 7, 8, 10}.issubset(chs)


# ===================================================================
# Review fixes of 2026-11-10 (ec7-11, ec7-16, ec7-18)
# ===================================================================


class TestWallFrictionConcreteGroups:
    def test_bare_concrete_is_refused(self):
        # Table 4-2 (PDF p. 66, printed p. 4-15) prints two concrete groups:
        # "Mass concrete on the following foundation materials" and "Formed
        # or precast concrete or concrete sheet piling against the following
        # soils". "concrete" alone used to return the mass concrete group.
        with pytest.raises(ValueError, match="formed or precast concrete"):
            table_4_2_wall_friction("concrete")

    def test_the_two_concrete_groups_as_printed(self):
        mass = table_4_2_wall_friction("mass concrete")["rows"]
        formed = table_4_2_wall_friction("formed or precast concrete")["rows"]
        # Mass concrete: clean gravel, gravel-sand mixtures, coarse sand 29 to 31
        gravel = [r for r in mass if r["interface"].startswith("Clean gravel")][0]
        assert (gravel["delta_min_deg"], gravel["delta_max_deg"]) == (29, 31)
        # Formed or precast concrete: clean gravel ... rock fill with spalls 22 to 26
        gravel = [r for r in formed if r["interface"].startswith("Clean gravel")][0]
        assert (gravel["delta_min_deg"], gravel["delta_max_deg"]) == (22, 26)
        # Formed or precast concrete, the four printed rows: 22 to 26, 17 to 22, 17, 14
        assert [(r["delta_min_deg"], r["delta_max_deg"]) for r in formed] == [
            (22, 26), (17, 22), (17, 17), (14, 14)]


class TestAtRestK0AsPrinted:
    def test_normally_consolidated_sloping_backfill(self):
        # Eq. 4-3-14 (PDF p. 60, printed p. 4-9): K0 = (1 - sin phi)(1 - sin beta)
        r = at_rest_k0(30, beta_deg=20)
        assert r["equation"] == "4-3-14"
        assert r["k0"] == pytest.approx(0.5 * (1 - math.sin(math.radians(20))), abs=1e-4)

    def test_over_consolidated_level_backfill(self):
        # Eq. 4-3-15 (printed p. 4-9): K0 = (1 - sin phi)(OCR)^sin phi
        r = at_rest_k0(30, ocr=2.0)
        assert r["equation"] == "4-3-15"
        assert r["k0"] == pytest.approx(0.5 * 2 ** 0.5, abs=1e-4)

    def test_over_consolidated_with_a_slope_is_refused(self):
        # Eq. 4-3-15 is printed "for over-consolidated soils, level backfill,
        # and a vertical wall". beta 20 with OCR 2 used to return 0.7071
        # with beta echoed and not used.
        with pytest.raises(ValueError, match="level backfill"):
            at_rest_k0(30, beta_deg=20, ocr=2.0)


class TestCohesiveAepNeedsItsInputs:
    def test_stiff_envelope_needs_the_factor(self):
        # Eq. 8-3-2 (PDF p. 156, printed p. 8-5): sigma_a = 0.2(gamma)(H) to
        # 0.4(gamma)(H), the factor by "best engineering judgment". The
        # factor used to default to 0.3, which the manual does not print.
        with pytest.raises(ValueError, match="480.0 to 960.0 psf"):
            aep_cohesive_max_ordinate(120, 20, ns=3)
        assert aep_cohesive_max_ordinate(120, 20, ns=3, factor=0.2)["sigma_a_psf"] == pytest.approx(480.0)
        assert aep_cohesive_max_ordinate(120, 20, ns=3, factor=0.4)["sigma_a_psf"] == pytest.approx(960.0)

    def test_transition_takes_the_larger_and_needs_both(self):
        # Printed p. 8-6: "For soils with 4 < Ns < 6, use the larger sigma_a
        # from Equations 8-3-2 and 8-3-3". Without Ka the stiff value alone
        # used to be returned.
        with pytest.raises(ValueError, match="larger sigma_a"):
            aep_cohesive_max_ordinate(120, 20, ns=5, factor=0.3)
        with pytest.raises(ValueError, match="factor is required"):
            aep_cohesive_max_ordinate(120, 20, ns=5, ka=0.5)
        r = aep_cohesive_max_ordinate(120, 20, ns=5, factor=0.3, ka=0.5)
        assert r["sigma_a_8_3_2_psf"] == pytest.approx(720.0)
        assert r["sigma_a_8_3_3_psf"] == pytest.approx(1200.0)
        assert r["sigma_a_psf"] == pytest.approx(1200.0)
        r = aep_cohesive_max_ordinate(120, 20, ns=5, factor=0.4, ka=0.25)
        assert r["sigma_a_psf"] == pytest.approx(960.0)

    def test_soft_envelope_needs_no_factor(self):
        # Eq. 8-3-3 (PDF p. 157, printed p. 8-6): sigma_a = Ka gamma H
        r = aep_cohesive_max_ordinate(120, 20, ns=7, ka=0.4)
        assert r["sigma_a_psf"] == pytest.approx(960.0)
        assert r["printed_page"] == "8-6"


class TestPrintedPagesOfEquations:
    def test_rankine_pages(self):
        # Eqs. 4-3-11 and 4-3-12 are on printed p. 4-8 (PDF p. 59), Eq. 4-3-16
        # on p. 4-10 (PDF p. 61), Eq. 4-3-19 on p. 4-11 (PDF p. 62). pdf_page
        # is the 0-based page index, as elsewhere in this package.
        assert rankine_ka(30)["printed_page"] == "4-8"
        sloping = rankine_ka(30, beta_deg=20)
        assert (sloping["equation"], sloping["printed_page"], sloping["pdf_page"]) == ("4-3-16", "4-10", 60)
        assert rankine_kp(30)["printed_page"] == "4-8"
        sloping = rankine_kp(30, beta_deg=10)
        assert (sloping["equation"], sloping["printed_page"], sloping["pdf_page"]) == ("4-3-19", "4-11", 61)

    def test_tension_crack_page_and_equation(self):
        # Eq. 4-4-13 (PDF p. 70, printed p. 4-19): hcr = 2c sqrt(Ka) / (gamma Ka)
        r = tension_crack_depth(500, 120, 0.36)
        assert r["hcr_ft"] == pytest.approx(2 * 500 * 0.6 / (120 * 0.36), abs=1e-3)
        assert (r["printed_page"], r["pdf_page"]) == ("4-19", 69)
