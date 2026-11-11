"""Tests for geotech_references.ufc_expansive (UFC 3-220-07, TM 5-818-7).

Expected values are read off docs/ufc_3_220_07.pdf (PDF page 1-based):
Table 4-1 PDF 31 (printed 4-1); para 5-4c PDF 39 (printed 5-4);
Figure 5-4 PDF 42 (printed 5-7); Table 6-1 PDF 44 (printed 6-2);
para 6-4, Grade beams, PDF 58 (printed 6-16).

Rebuilt 2026-11-10 (review pave-07, pave-13): activity_index,
free_swell_percent, swell_pressure_kPa and pier_minimum_embedment_m were
removed with their tests (not printed in this manual).
"""

import pytest

from geotech_references.ufc_expansive.equations import (
    heave_prediction_mm,
    table_4_2_swell_vijayvergiya_ghazzaly,
    table_4_2_swell_schneider_poor,
    table_4_2_swell_mckeen_lytton,
    table_4_2_swell_johnson,
)
from geotech_references.ufc_expansive.tables import (
    table_swell_potential_classification,
    table_active_zone_depth,
    table_foundation_selection,
    table_grade_beam_void_space,
)


# ===================================================================
# EQUATION TESTS
# ===================================================================


class TestHeavePrediction:
    """heave_prediction_mm: Figure 5-4 (A) step 4, PDF 42 (printed 5-7)."""

    def test_printed_example(self):
        # Figure 5-4: "Total swell = 1/2 x (8.2 - 1.0) x 2.8/100 = 0.10 ft";
        # one 7.2 ft layer at the triangle's mean 1.4 % gives the same area.
        r = heave_prediction_mm(
            [{"thickness_m": 7.2 * 0.3048, "swell_strain_pct": 1.4}])
        assert r["total_heave_ft"] == pytest.approx(0.10, abs=0.005)
        assert "Figure 5-4" in r["reference"]
        assert "p. 5-7" in r["reference"]

    def test_printed_example_two_layers(self):
        # The printed triangle (2.8 % at 1.0 ft, 0 at 8.2 ft) split at
        # 4.6 ft: means 2.1 % and 0.7 % over 3.6 ft each; same 0.10 ft.
        t = 3.6 * 0.3048
        r = heave_prediction_mm([
            {"thickness_m": t, "swell_strain_pct": 2.1},
            {"thickness_m": t, "swell_strain_pct": 0.7},
        ])
        assert r["total_heave_ft"] == pytest.approx(0.10, abs=0.005)

    def test_single_layer(self):
        layers = [{"thickness_m": 2.0, "swell_strain_pct": 3.0}]
        r = heave_prediction_mm(layers)
        assert r["total_heave_mm"] == pytest.approx(60.0, abs=0.1)
        assert r["number_of_layers"] == 1

    def test_multiple_layers(self):
        layers = [
            {"thickness_m": 1.0, "swell_strain_pct": 5.0},
            {"thickness_m": 1.5, "swell_strain_pct": 3.0},
            {"thickness_m": 2.0, "swell_strain_pct": 1.0},
        ]
        r = heave_prediction_mm(layers)
        expected = 50.0 + 45.0 + 20.0
        assert r["total_heave_mm"] == pytest.approx(expected, abs=0.1)

    def test_zero_strain_no_heave(self):
        layers = [{"thickness_m": 3.0, "swell_strain_pct": 0.0}]
        r = heave_prediction_mm(layers)
        assert r["total_heave_mm"] == 0.0

    def test_layer_heaves_returned(self):
        layers = [
            {"thickness_m": 1.0, "swell_strain_pct": 2.0},
            {"thickness_m": 1.0, "swell_strain_pct": 4.0},
        ]
        r = heave_prediction_mm(layers)
        assert len(r["layer_heaves_mm"]) == 2
        assert r["layer_heaves_mm"][0] == pytest.approx(20.0, abs=0.1)
        assert r["layer_heaves_mm"][1] == pytest.approx(40.0, abs=0.1)

    def test_empty_layers_raises(self):
        with pytest.raises(ValueError, match="layers.*empty"):
            heave_prediction_mm([])

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError, match="thickness_m"):
            heave_prediction_mm([{"thickness_m": 0, "swell_strain_pct": 3.0}])

    def test_negative_strain_raises(self):
        with pytest.raises(ValueError, match="swell_strain_pct"):
            heave_prediction_mm([{"thickness_m": 1.0, "swell_strain_pct": -1.0}])


class TestTable42:
    """Table 4-2 Other Empirical Methods for Prediction of Potential Heave,
    PDF 33 (printed 4-3); expected values worked by hand from the printed
    relations at made-up inputs."""

    def test_vijayvergiya_ghazzaly(self):
        # Log Sp = 1/12(0.44LL - wo + 5.5); 0.1-tsf surcharge
        r = table_4_2_swell_vijayvergiya_ghazzaly(60, 20)
        assert r["log_sp"] == pytest.approx(11.9 / 12, abs=1e-4)
        assert r["potential_swell_pct"] == pytest.approx(9.810, abs=0.002)
        assert table_4_2_swell_vijayvergiya_ghazzaly(50, 30)[
            "potential_swell_pct"] == pytest.approx(0.619, abs=0.001)
        assert "p. 4-3" in r["reference"] and "0.1-tsf" in r["condition"]

    def test_schneider_poor(self):
        # Log Sp = 0.9(PI/wo) - 1.19; no fill or weight
        r = table_4_2_swell_schneider_poor(30, 20)
        assert r["potential_swell_pct"] == pytest.approx(1.445, abs=0.001)
        assert table_4_2_swell_schneider_poor(20, 25)[
            "potential_swell_pct"] == pytest.approx(0.339, abs=0.001)
        with pytest.raises(ValueError, match="initial_water_content"):
            table_4_2_swell_schneider_poor(30, 0)

    def test_mckeen_lytton(self):
        # Sp = -100 gamma_h log10(tau_f/tau_o); tau = 0.5t1 + 0.3t2 + 0.2t3
        assert table_4_2_swell_mckeen_lytton(0.1, 1.0, 10.0)[
            "potential_swell_pct"] == pytest.approx(10.0)
        r = table_4_2_swell_mckeen_lytton(0.1, [1, 1, 1], [12, 10, 5])
        assert r["initial_weighted_suction"] == pytest.approx(10.0)
        assert r["potential_swell_pct"] == pytest.approx(10.0)
        assert table_4_2_swell_mckeen_lytton(0.05, 2.0, 8.0)[
            "potential_swell_pct"] == pytest.approx(3.010, abs=0.001)
        with pytest.raises(ValueError, match="3 suctions"):
            table_4_2_swell_mckeen_lytton(0.1, [1, 1], 10.0)

    def test_johnson(self):
        # PI >= 40 and PI <= 40 forms; 1 psi surcharge; H in feet
        r = table_4_2_swell_johnson(50, 5, 25)
        assert r["form"] == "PI >= 40"
        assert r["potential_swell_pct"] == pytest.approx(18.236, abs=0.001)
        r = table_4_2_swell_johnson(30, 5, 20)
        assert r["form"] == "PI <= 40"
        assert r["potential_swell_pct"] == pytest.approx(12.137, abs=0.001)

    def test_johnson_pi_40_both_forms(self):
        r = table_4_2_swell_johnson(40, 10, 20)
        assert r["potential_swell_pct"] == pytest.approx(16.21, abs=0.001)
        assert "16.426" in r["note"]

    def test_johnson_negative_value_noted(self):
        # PI <= 40 form at made-up PI 20, H 0, wo 40:
        # -9.18 + 31.092 + 4 - 34.56 = -8.648, returned with a note.
        r = table_4_2_swell_johnson(20, 0, 40)
        assert r["potential_swell_pct"] == pytest.approx(-8.648, abs=0.001)
        assert "not a predicted shrinkage" in r["note"]
        assert "shrinkage" not in table_4_2_swell_johnson(30, 5, 20)["note"]

    def test_johnson_print_note_states_the_reading(self):
        # The PI <= 40 form's operators render as "="; read as minus.
        r = table_4_2_swell_johnson(30, 5, 20)
        assert "'='" in r["print_note"] and "minus" in r["print_note"]
        assert "16.21" in r["print_note"] and "16.43" in r["print_note"]


# ===================================================================
# TABLE TESTS
# ===================================================================


class TestSwellPotentialClassification:
    """table_swell_potential_classification: Table 4-1, PDF 31 (printed 4-1).

    Low: Sp <0.5 %, LL <50, PI <25, suction <1.5 tsf; Marginal: 0.5-1.5,
    50-60, 25-35, 1.5-4.0; High: >1.5, >60, >35, >4.0.
    """

    def test_very_low_pi(self):
        # Was "very_low"; Table 4-1 has no such class: PI 5 < 25 is low.
        r = table_swell_potential_classification(plasticity_index=5)
        assert r["classification"] == "low"
        assert r["potential_swell_pct"] == "<0.5"

    def test_low_pi(self):
        r = table_swell_potential_classification(plasticity_index=15)
        assert r["classification"] == "low"

    def test_medium_pi(self):
        # Was "medium"; PI 25 opens the printed 25-35 marginal row.
        r = table_swell_potential_classification(plasticity_index=25)
        assert r["classification"] == "marginal"
        assert r["potential_swell_pct"] == "0.5-1.5"

    def test_marginal_pi_30(self):
        r = table_swell_potential_classification(plasticity_index=30)
        assert r["classification"] == "marginal"

    def test_marginal_pi_35_top_of_row(self):
        r = table_swell_potential_classification(plasticity_index=35)
        assert r["classification"] == "marginal"

    def test_high_pi(self):
        r = table_swell_potential_classification(plasticity_index=45)
        assert r["classification"] == "high"
        assert r["potential_swell_pct"] == ">1.5"

    def test_very_high_pi(self):
        # Was "very_high"; PI 60 > 35 is the printed high row.
        r = table_swell_potential_classification(plasticity_index=60)
        assert r["classification"] == "high"

    def test_liquid_limit_rows(self):
        assert table_swell_potential_classification(
            liquid_limit=45)["classification"] == "low"
        assert table_swell_potential_classification(
            liquid_limit=55)["classification"] == "marginal"
        assert table_swell_potential_classification(
            liquid_limit=65)["classification"] == "high"

    def test_liquid_limit_only(self):
        # LL 60 is the top of the printed 50-60 marginal row.
        r = table_swell_potential_classification(liquid_limit=60)
        assert r["classification"] == "marginal"

    def test_suction_rows(self):
        assert table_swell_potential_classification(
            natural_soil_suction_tsf=1.0)["classification"] == "low"
        assert table_swell_potential_classification(
            natural_soil_suction_tsf=2.0)["classification"] == "marginal"
        assert table_swell_potential_classification(
            natural_soil_suction_tsf=5.0)["classification"] == "high"

    def test_both_parameters_uses_worse(self):
        r = table_swell_potential_classification(plasticity_index=15,
                                                  liquid_limit=60)
        # PI 15 -> low, LL 60 -> marginal; the more severe row is returned
        assert r["classification"] == "marginal"
        assert r["by_property"] == {"plasticity_index": "low",
                                    "liquid_limit": "marginal"}

    def test_reference_and_note(self):
        r = table_swell_potential_classification(plasticity_index=30)
        assert "Table 4-1" in r["reference"] and "p. 4-1" in r["reference"]
        assert "LL is less than 40" in r["note"]
        assert "less than 1 inch" in r["note"]  # para 4-1a, p. 4-1
        assert r["printed_row"]["plasticity_index_pct"] == "25-35"

    def test_neither_parameter_raises(self):
        with pytest.raises(ValueError, match="At least one"):
            table_swell_potential_classification()

    def test_negative_pi_raises(self):
        with pytest.raises(ValueError, match="plasticity_index"):
            table_swell_potential_classification(plasticity_index=-5)

    def test_zero_pi(self):
        r = table_swell_potential_classification(plasticity_index=0)
        assert r["classification"] == "low"


class TestActiveZoneDepth:
    """table_active_zone_depth: para 5-4c, PDF 39 (printed 5-4)."""

    def test_moist_profile_10_ft(self):
        # 5-4c(2)(a): 10 feet for moist profiles (suction < 4 tsf)
        r = table_active_zone_depth("moist")
        assert r["active_zone_depth_ft"] == 10.0
        assert r["active_zone_depth_m"] == pytest.approx(3.048)
        assert "p. 5-4" in r["reference"]

    def test_dry_profile_20_ft(self):
        # 5-4c(2)(a): 20 feet for dry profiles (suction > 4 tsf)
        r = table_active_zone_depth("dry")
        assert r["active_zone_depth_ft"] == 20.0

    def test_suction_selects_profile(self):
        assert table_active_zone_depth(
            natural_soil_suction_tsf=3.0)["active_zone_depth_ft"] == 10.0
        assert table_active_zone_depth(
            natural_soil_suction_tsf=5.0)["active_zone_depth_ft"] == 20.0

    def test_suction_exactly_4_raises(self):
        with pytest.raises(ValueError, match="4 tsf"):
            table_active_zone_depth(natural_soil_suction_tsf=4.0)

    def test_shallow_groundwater(self):
        # 5-4c(1): Xa equal to the water table depth when less than 20 ft
        r = table_active_zone_depth(depth_to_groundwater_ft=12.0)
        assert r["active_zone_depth_ft"] == 12.0

    def test_deep_groundwater_uses_profile(self):
        r = table_active_zone_depth("dry", depth_to_groundwater_ft=25.0)
        assert r["active_zone_depth_ft"] == 20.0

    def test_three_shaft_base_diameters(self):
        # "should not be estimated less than three times the base diameter"
        r = table_active_zone_depth("moist", shaft_base_diameter_ft=5.0)
        assert r["active_zone_depth_ft"] == 15.0
        r = table_active_zone_depth("moist", shaft_base_diameter_ft=2.0)
        assert r["active_zone_depth_ft"] == 10.0

    def test_shaft_floor_printed_under_deep_groundwater_only(self):
        # The three-diameter sentence is in 5-4c(2)(a), deep groundwater.
        r = table_active_zone_depth(depth_to_groundwater_ft=8.0,
                                    shaft_base_diameter_ft=5.0)
        assert r["active_zone_depth_ft"] == 8.0
        assert "not applied" in r["basis"]

    def test_invalid_raises(self):
        # Was a climate table (arid ... coastal); para 5-4c has none.
        with pytest.raises(ValueError, match="moist"):
            table_active_zone_depth("arid")
        with pytest.raises(ValueError, match="moist"):
            table_active_zone_depth("tropical")

    def test_case_insensitive(self):
        r = table_active_zone_depth("MOIST")
        assert r["active_zone_depth_ft"] == 10.0


class TestFoundationSelection:
    """table_foundation_selection: Table 6-1, PDF 44 (printed 6-2)."""

    def test_half_inch_shallow(self):
        r = table_foundation_selection(predicted_differential_movement_in=0.5)
        assert r["systems"][0]["foundation_system"].startswith("Shallow")
        assert r["systems"][0]["effective_plasticity_index"] == "<15"
        assert "Table 6-1" in r["reference"] and "p. 6-2" in r["reference"]

    def test_light_mat(self):
        r = table_foundation_selection(predicted_differential_movement_in=0.75)
        mat = r["systems"][0]
        assert mat["type_of_mat"] == "light"
        assert mat["beam_depth_in"] == "16 to 20"
        assert mat["beam_spacing_ft"] == "20 to 15"

    def test_medium_mat(self):
        r = table_foundation_selection(predicted_differential_movement_in=1.5)
        mat = r["systems"][0]
        assert mat["type_of_mat"] == "medium"
        assert mat["beam_depth_in"] == "20 to 25"
        assert mat["beam_spacing_ft"] == "15 to 12"

    def test_heavy_mat(self):
        r = table_foundation_selection(predicted_differential_movement_in=3.0)
        mat = r["systems"][0]
        assert mat["type_of_mat"] == "heavy"
        assert mat["beam_depth_in"] == "25 to 30"
        assert mat["effective_plasticity_index"] == ">41"

    def test_over_4_in_no_limit_systems_only(self):
        r = table_foundation_selection(predicted_differential_movement_in=6.0)
        names = [s["foundation_system"] for s in r["systems"]]
        assert names == ["Thick, reinforced mat",
                         "Deep foundations, pile or drilled shaft"]

    def test_effective_pi_rows(self):
        assert table_foundation_selection(
            effective_plasticity_index=10)["systems"][0][
                "foundation_system"].startswith("Shallow")
        assert table_foundation_selection(
            effective_plasticity_index=20)["systems"][0]["type_of_mat"] == "light"
        assert table_foundation_selection(
            effective_plasticity_index=30)["systems"][0]["type_of_mat"] == "medium"
        assert table_foundation_selection(
            effective_plasticity_index=45)["systems"][0]["type_of_mat"] == "heavy"

    def test_deep_foundation_remarks(self):
        r = table_foundation_selection(predicted_differential_movement_in=1.0)
        deep = r["systems"][-1]
        assert "6 to 12 in. above ground level" in deep["remarks"]
        assert deep["predicted_differential_movement_in"] == "No limit"

    def test_neither_raises(self):
        with pytest.raises(ValueError, match="Table 6-1"):
            table_foundation_selection()

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="predicted_differential"):
            table_foundation_selection(predicted_differential_movement_in=-1)


class TestGradeBeamVoidSpace:
    """table_grade_beam_void_space: para 6-4, Grade beams, PDF 58 (printed
    6-16): "6 to 12 inches or 2 times the predicted total heave ...
    (whichever is larger)"."""

    def test_no_heave_given(self):
        r = table_grade_beam_void_space()
        assert (r["void_space_low_in"], r["void_space_high_in"]) == (6.0, 12.0)
        assert "p. 6-16" in r["reference"]

    def test_small_heave_keeps_6_to_12(self):
        r = table_grade_beam_void_space(predicted_total_heave_in=2.0)
        assert (r["void_space_low_in"], r["void_space_high_in"]) == (6.0, 12.0)

    def test_medium_heave(self):
        # 2 x 4 in = 8 in > 6 in
        r = table_grade_beam_void_space(predicted_total_heave_in=4.0)
        assert (r["void_space_low_in"], r["void_space_high_in"]) == (8.0, 12.0)

    def test_large_heave(self):
        # 2 x 8 in = 16 in > 12 in
        r = table_grade_beam_void_space(predicted_total_heave_in=8.0)
        assert (r["void_space_low_in"], r["void_space_high_in"]) == (16.0, 16.0)

    def test_mm_conversion(self):
        r = table_grade_beam_void_space(predicted_total_heave_in=0.0)
        assert r["void_space_low_mm"] == pytest.approx(152.4)
        assert r["void_space_high_mm"] == pytest.approx(304.8)

    def test_printed_text(self):
        r = table_grade_beam_void_space()
        assert "whichever is larger" in r["printed"]

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="predicted_total_heave_in"):
            table_grade_beam_void_space(-1.0)
