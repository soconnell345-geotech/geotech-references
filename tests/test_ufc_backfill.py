"""Tests for geotech_references.ufc_backfill (UFC 3-220-04N)."""

import math
import pytest

from geotech_references.ufc_backfill.tables import (
    table_compaction_requirements,
    table_backfill_material_classification,
    table_maximum_lift_thickness,
    table_compaction_equipment_selection,
    table_drainage_requirements,
)
from geotech_references.ufc_backfill.equations import (
    compaction_induced_pressure_kPa,
    filter_criteria_check,
    relative_compaction_check,
)


# ===================================================================
# TABLE TESTS
# ===================================================================


class TestCompactionRequirements:
    """table_compaction_requirements — 10 applications."""

    def test_under_foundations(self):
        r = table_compaction_requirements("under_foundations")
        assert r["min_compaction_pct"] == 95

    def test_under_floor_slabs(self):
        r = table_compaction_requirements("under_floor_slabs")
        assert r["min_compaction_pct"] == 95

    def test_under_pavements(self):
        r = table_compaction_requirements("under_pavements")
        assert r["min_compaction_pct"] == 95

    def test_adjacent_to_structures(self):
        r = table_compaction_requirements("adjacent_to_structures")
        assert r["min_compaction_pct"] == 90

    def test_pipe_bedding(self):
        r = table_compaction_requirements("pipe_bedding")
        assert r["min_compaction_pct"] == 90

    def test_pipe_haunch(self):
        r = table_compaction_requirements("pipe_haunch")
        assert r["min_compaction_pct"] == 90

    def test_above_pipe(self):
        r = table_compaction_requirements("above_pipe")
        assert r["min_compaction_pct"] == 85

    def test_general_fill(self):
        r = table_compaction_requirements("general_fill")
        assert r["min_compaction_pct"] == 90

    def test_structural_fill(self):
        r = table_compaction_requirements("structural_fill")
        assert r["min_compaction_pct"] == 95

    def test_behind_retaining_walls(self):
        r = table_compaction_requirements("behind_retaining_walls")
        assert r["min_compaction_pct"] == 90

    def test_case_insensitive(self):
        r = table_compaction_requirements("UNDER_FOUNDATIONS")
        assert r["min_compaction_pct"] == 95

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown application"):
            table_compaction_requirements("nonexistent")

    def test_has_standard_key(self):
        r = table_compaction_requirements("general_fill")
        assert "standard" in r
        assert r["standard"] == "ASTM D698"


class TestBackfillMaterialClassification:
    """table_backfill_material_classification — USCS types."""

    def test_gw_excellent(self):
        r = table_backfill_material_classification("GW")
        assert r["type"] == "I"
        assert r["acceptability"] == "excellent"

    def test_sw_excellent(self):
        r = table_backfill_material_classification("SW")
        assert r["type"] == "I"
        assert r["acceptability"] == "excellent"

    def test_sp_good(self):
        r = table_backfill_material_classification("SP")
        assert r["type"] == "I"
        assert r["acceptability"] == "good"

    def test_sm_fair(self):
        r = table_backfill_material_classification("SM")
        assert r["type"] == "II"
        assert r["acceptability"] == "fair"

    def test_cl_poor(self):
        r = table_backfill_material_classification("CL")
        assert r["type"] == "III"
        assert r["acceptability"] == "poor"

    def test_ch_unacceptable(self):
        r = table_backfill_material_classification("CH")
        assert r["type"] == "unacceptable"
        assert r["acceptability"] == "unacceptable"

    def test_pt_unacceptable(self):
        r = table_backfill_material_classification("PT")
        assert r["acceptability"] == "unacceptable"

    def test_dual_symbol_gw_gm(self):
        r = table_backfill_material_classification("GW-GM")
        assert r["type"] == "II"

    def test_dual_symbol_sp_sc(self):
        r = table_backfill_material_classification("SP-SC")
        assert r["type"] == "II"

    def test_case_insensitive(self):
        r = table_backfill_material_classification("gw")
        assert r["type"] == "I"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown USCS"):
            table_backfill_material_classification("XX")

    def test_drainage_field(self):
        r = table_backfill_material_classification("GW")
        assert r["drainage"] == "free_draining"


class TestMaximumLiftThickness:
    """table_maximum_lift_thickness — equipment types."""

    def test_hand_tamper(self):
        r = table_maximum_lift_thickness("hand_tamper")
        assert r["max_lift_mm"] == 100

    def test_mechanical_rammer(self):
        r = table_maximum_lift_thickness("mechanical_rammer")
        assert r["max_lift_mm"] == 150

    def test_vibratory_plate_small(self):
        r = table_maximum_lift_thickness("vibratory_plate_small")
        assert r["max_lift_mm"] == 200

    def test_vibratory_plate_large(self):
        r = table_maximum_lift_thickness("vibratory_plate_large")
        assert r["max_lift_mm"] == 300

    def test_vibratory_smooth_drum(self):
        r = table_maximum_lift_thickness("vibratory_smooth_drum")
        assert r["max_lift_mm"] == 300

    def test_sheepsfoot(self):
        r = table_maximum_lift_thickness("sheepsfoot_roller")
        assert r["max_lift_mm"] == 200

    def test_pneumatic_tired(self):
        r = table_maximum_lift_thickness("pneumatic_tired_roller")
        assert r["max_lift_mm"] == 250

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown equipment"):
            table_maximum_lift_thickness("bulldozer")

    def test_has_suitable_soils(self):
        r = table_maximum_lift_thickness("sheepsfoot_roller")
        assert "cohesive" in r["suitable_soils"]


class TestCompactionEquipmentSelection:
    """table_compaction_equipment_selection — soil types."""

    def test_clean_gravel(self):
        r = table_compaction_equipment_selection("clean_gravel")
        assert "vibratory_smooth_drum" in r["recommended"]

    def test_clean_sand(self):
        r = table_compaction_equipment_selection("clean_sand")
        assert "vibratory_smooth_drum" in r["recommended"]

    def test_low_plasticity_clay(self):
        r = table_compaction_equipment_selection("low_plasticity_clay")
        assert "sheepsfoot_roller" in r["recommended"]

    def test_confined_area(self):
        r = table_compaction_equipment_selection("confined_area")
        assert "hand_tamper" in r["recommended"]

    def test_not_recommended_key(self):
        r = table_compaction_equipment_selection("clean_gravel")
        assert "sheepsfoot_roller" in r["not_recommended"]

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown soil type"):
            table_compaction_equipment_selection("organic_muck")


class TestDrainageRequirements:
    """table_drainage_requirements — applications."""

    def test_foundation_drain(self):
        r = table_drainage_requirements("foundation_drain")
        assert r["min_thickness_mm"] == 150
        assert r["min_k_m_per_s"] == 1e-3

    def test_retaining_wall_drain(self):
        r = table_drainage_requirements("retaining_wall_drain")
        assert r["min_thickness_mm"] == 300
        assert r["min_slope_pct"] == 2.0

    def test_pavement_subdrain(self):
        r = table_drainage_requirements("pavement_subdrain")
        assert r["min_k_m_per_s"] == 1e-2

    def test_blanket_drain(self):
        r = table_drainage_requirements("blanket_drain")
        assert r["min_thickness_mm"] == 200

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown application"):
            table_drainage_requirements("swimming_pool")


# ===================================================================
# EQUATION TESTS
# ===================================================================


class TestCompactionInducedPressure:
    """compaction_induced_pressure_kPa — Broms 1971."""

    def test_compaction_controlled_shallow(self):
        r = compaction_induced_pressure_kPa(30.0, 0.5, 18.0, 0.5)
        assert r["regime"] == "compaction_controlled"
        assert r["sigma_h_kPa"] == r["sigma_h_max_kPa"]

    def test_overburden_controlled_deep(self):
        r = compaction_induced_pressure_kPa(30.0, 5.0, 18.0, 0.5)
        assert r["regime"] == "overburden_controlled"
        assert r["sigma_h_kPa"] == pytest.approx(0.5 * 18.0 * 5.0, rel=0.01)

    def test_critical_depth_formula(self):
        r = compaction_induced_pressure_kPa(30.0, 1.0, 18.0, 0.5)
        expected_max = math.sqrt(2.0 * 30.0 * 18.0 * 0.5 / math.pi)
        assert r["sigma_h_max_kPa"] == pytest.approx(expected_max, rel=0.01)

    def test_higher_roller_load(self):
        r1 = compaction_induced_pressure_kPa(20.0, 0.5, 18.0, 0.5)
        r2 = compaction_induced_pressure_kPa(50.0, 0.5, 18.0, 0.5)
        assert r2["sigma_h_max_kPa"] > r1["sigma_h_max_kPa"]

    def test_k0_affects_result(self):
        r1 = compaction_induced_pressure_kPa(30.0, 0.5, 18.0, 0.3)
        r2 = compaction_induced_pressure_kPa(30.0, 0.5, 18.0, 0.6)
        # Higher K0 = different sigma_h_max
        assert r1["sigma_h_max_kPa"] != r2["sigma_h_max_kPa"]

    def test_zero_depth_raises(self):
        with pytest.raises(ValueError, match="depth_m"):
            compaction_induced_pressure_kPa(30.0, 0, 18.0, 0.5)

    def test_negative_load_raises(self):
        with pytest.raises(ValueError, match="roller_line_load"):
            compaction_induced_pressure_kPa(-10.0, 1.0, 18.0, 0.5)

    def test_k0_out_of_range_raises(self):
        with pytest.raises(ValueError, match="K0"):
            compaction_induced_pressure_kPa(30.0, 1.0, 18.0, 1.5)

    def test_transition_at_critical_depth(self):
        """At exactly z_cr, both regimes give the same pressure."""
        r = compaction_induced_pressure_kPa(30.0, 1.0, 18.0, 0.5)
        z_cr = r["z_cr_m"]
        r_at_zcr = compaction_induced_pressure_kPa(30.0, z_cr, 18.0, 0.5)
        # At z_cr, compaction pressure = K0*gamma*z
        expected = 0.5 * 18.0 * z_cr
        assert r_at_zcr["sigma_h_kPa"] == pytest.approx(expected, rel=0.02)


class TestFilterCriteriaCheck:
    """filter_criteria_check — Terzaghi/USACE criteria."""

    def test_all_pass(self):
        r = filter_criteria_check(2.0, 0.5, d15_soil_mm=0.1,
                                  d50_filter_mm=5.0, d50_soil_mm=0.3,
                                  cu_filter=4.0)
        assert r["all_pass"] is True
        assert len(r["criteria_checked"]) == 4

    def test_retention_fail(self):
        r = filter_criteria_check(10.0, 1.0)  # ratio = 10 > 5
        assert r["retention_pass"] is False
        assert r["all_pass"] is False

    def test_retention_pass(self):
        r = filter_criteria_check(2.0, 1.0)  # ratio = 2 <= 5
        assert r["retention_pass"] is True

    def test_permeability_fail(self):
        r = filter_criteria_check(1.0, 0.5, d15_soil_mm=0.5)
        # ratio = 1.0/0.5 = 2.0 < 5
        assert r["permeability_pass"] is False

    def test_permeability_pass(self):
        r = filter_criteria_check(5.0, 2.0, d15_soil_mm=0.5)
        # ratio = 5.0/0.5 = 10.0 >= 5
        assert r["permeability_pass"] is True

    def test_uniformity_fail(self):
        r = filter_criteria_check(2.0, 1.0, d50_filter_mm=50.0,
                                  d50_soil_mm=1.0)
        # ratio = 50 > 25
        assert r["uniformity_pass"] is False

    def test_uniformity_pass(self):
        r = filter_criteria_check(2.0, 1.0, d50_filter_mm=10.0,
                                  d50_soil_mm=1.0)
        # ratio = 10 <= 25
        assert r["uniformity_pass"] is True

    def test_segregation_fail(self):
        r = filter_criteria_check(2.0, 1.0, cu_filter=25.0)
        assert r["segregation_pass"] is False

    def test_segregation_pass(self):
        r = filter_criteria_check(2.0, 1.0, cu_filter=10.0)
        assert r["segregation_pass"] is True

    def test_retention_only(self):
        r = filter_criteria_check(2.0, 1.0)
        assert r["criteria_checked"] == ["retention"]

    def test_zero_d15_filter_raises(self):
        with pytest.raises(ValueError, match="d15_filter"):
            filter_criteria_check(0, 1.0)

    def test_zero_d85_soil_raises(self):
        with pytest.raises(ValueError, match="d85_soil"):
            filter_criteria_check(1.0, 0)

    def test_boundary_retention_exactly_5(self):
        r = filter_criteria_check(5.0, 1.0)
        assert r["retention_ratio"] == 5.0
        assert r["retention_pass"] is True


class TestRelativeCompactionCheck:
    """relative_compaction_check — field QC."""

    def test_passes(self):
        r = relative_compaction_check(18.0, 19.0, 95.0)
        # RC = 18/19 * 100 = 94.7% < 95% -> fails
        assert r["passes"] is False

    def test_passes_above_required(self):
        r = relative_compaction_check(18.5, 19.0, 95.0)
        # RC = 18.5/19 * 100 = 97.4%
        assert r["passes"] is True

    def test_exact_boundary(self):
        r = relative_compaction_check(19.0, 20.0, 95.0)
        # RC = 95.0% exactly
        assert r["passes"] is True
        assert r["deficit_pct"] == 0.0

    def test_deficit_calculated(self):
        r = relative_compaction_check(17.0, 19.0, 95.0)
        # RC = 89.5%, deficit = 95 - 89.5 = 5.5
        assert r["deficit_pct"] == pytest.approx(5.5, abs=0.1)

    def test_custom_required_pct(self):
        r = relative_compaction_check(17.0, 20.0, 85.0)
        # RC = 85.0%
        assert r["passes"] is True

    def test_zero_density_raises(self):
        with pytest.raises(ValueError, match="dry_density"):
            relative_compaction_check(0, 19.0, 95.0)

    def test_zero_max_density_raises(self):
        with pytest.raises(ValueError, match="max_dry_density"):
            relative_compaction_check(18.0, 0, 95.0)

    def test_invalid_required_pct(self):
        with pytest.raises(ValueError, match="required_pct"):
            relative_compaction_check(18.0, 19.0, 0)
