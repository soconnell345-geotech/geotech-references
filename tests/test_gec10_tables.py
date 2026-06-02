"""Tests for GEC-10 table lookup functions (FHWA-NHI-18-024)."""

import pytest

from geotech_references.gec_10.tables import (
    table_8_4_resistance_factor,
    table_8_4_by_category,
    table_9_1_lateral_resistance_factor,
    table_10_2_nc_base_clay,
    table_11_1_p_multiplier,
    table_11_2_group_efficiency_cohesionless,
    aashto_reliability_index,
)


# ============================================================================
# Table 8-4: Resistance Factors
# ============================================================================

class TestTable84ResistanceFactor:

    # --- Lateral ---
    def test_lateral_individual(self):
        result = table_8_4_resistance_factor("lateral_individual")
        assert result["phi"] == 0.67

    def test_lateral_group(self):
        result = table_8_4_resistance_factor("lateral_group")
        assert result["phi"] == 0.80

    # --- Side resistance ---
    def test_side_cohesionless_compression(self):
        result = table_8_4_resistance_factor("side_cohesionless_compression")
        assert result["phi"] == 0.55

    def test_side_cohesionless_uplift(self):
        result = table_8_4_resistance_factor("side_cohesionless_uplift")
        assert result["phi"] == 0.45

    def test_side_cohesive_compression(self):
        result = table_8_4_resistance_factor("side_cohesive_compression")
        assert result["phi"] == 0.45

    def test_side_cohesive_uplift(self):
        result = table_8_4_resistance_factor("side_cohesive_uplift")
        assert result["phi"] == 0.35

    def test_side_rock_compression(self):
        result = table_8_4_resistance_factor("side_rock_compression")
        assert result["phi"] == 0.50

    def test_side_rock_uplift(self):
        result = table_8_4_resistance_factor("side_rock_uplift")
        assert result["phi"] == 0.40

    def test_side_igm_compression(self):
        result = table_8_4_resistance_factor("side_igm_compression")
        assert result["phi"] == 0.60

    def test_side_igm_uplift(self):
        result = table_8_4_resistance_factor("side_igm_uplift")
        assert result["phi"] == 0.50

    # --- Base resistance ---
    def test_base_cohesionless(self):
        result = table_8_4_resistance_factor("base_cohesionless")
        assert result["phi"] == 0.50

    def test_base_cohesive(self):
        result = table_8_4_resistance_factor("base_cohesive")
        assert result["phi"] == 0.40

    def test_base_rock(self):
        result = table_8_4_resistance_factor("base_rock")
        assert result["phi"] == 0.50

    # --- Load test ---
    def test_load_test_compression(self):
        result = table_8_4_resistance_factor("load_test_compression")
        assert result["phi"] == 0.70

    def test_load_test_uplift(self):
        result = table_8_4_resistance_factor("load_test_uplift")
        assert result["phi"] == 0.60

    # --- Group ---
    def test_group_block_failure(self):
        result = table_8_4_resistance_factor("group_block_failure")
        assert result["phi"] == 0.55

    def test_group_uplift(self):
        result = table_8_4_resistance_factor("group_uplift")
        assert result["phi"] == 0.45

    # --- Structural ---
    def test_structural_compression(self):
        result = table_8_4_resistance_factor("structural_compression")
        assert result["phi"] == 0.75

    def test_structural_shear(self):
        result = table_8_4_resistance_factor("structural_shear")
        assert result["phi"] == 0.90

    # --- Extreme event ---
    def test_extreme_uplift(self):
        result = table_8_4_resistance_factor("extreme_uplift")
        assert result["phi"] == 0.80

    def test_extreme_lateral(self):
        result = table_8_4_resistance_factor("extreme_lateral")
        assert result["phi"] == 0.80

    def test_extreme_other(self):
        result = table_8_4_resistance_factor("extreme_other")
        assert result["phi"] == 1.00

    # --- Service ---
    def test_service(self):
        result = table_8_4_resistance_factor("service")
        assert result["phi"] == 1.00

    # --- Partial matching ---
    def test_partial_match_base_rock(self):
        result = table_8_4_resistance_factor("base_rock")
        assert result["phi"] == 0.50

    def test_partial_match_group_block(self):
        result = table_8_4_resistance_factor("group_block")
        assert result["phi"] == 0.55

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="No matching"):
            table_8_4_resistance_factor("nonexistent_xyz_abc")

    def test_result_has_method_key(self):
        result = table_8_4_resistance_factor("structural_shear")
        assert "method" in result

    def test_result_has_condition(self):
        result = table_8_4_resistance_factor("base_cohesive")
        assert "condition" in result
        assert len(result["condition"]) > 5

    def test_result_has_category(self):
        result = table_8_4_resistance_factor("base_cohesive")
        assert result["category"] == "compression_base"

    def test_compression_higher_than_uplift_cohesionless(self):
        c = table_8_4_resistance_factor("side_cohesionless_compression")["phi"]
        u = table_8_4_resistance_factor("side_cohesionless_uplift")["phi"]
        assert c > u

    def test_compression_higher_than_uplift_rock(self):
        c = table_8_4_resistance_factor("side_rock_compression")["phi"]
        u = table_8_4_resistance_factor("side_rock_uplift")["phi"]
        assert c > u


class TestTable84ByCategory:

    def test_all_entries_returned_for_empty_string(self):
        results = table_8_4_by_category("")
        assert len(results) >= 20

    def test_lateral_category(self):
        results = table_8_4_by_category("lateral")
        assert len(results) == 2
        assert all(r["category"] == "lateral" for r in results)

    def test_compression_side_category(self):
        results = table_8_4_by_category("compression_side")
        assert len(results) >= 4

    def test_uplift_side_category(self):
        results = table_8_4_by_category("uplift_side")
        assert len(results) >= 4

    def test_structural_category(self):
        results = table_8_4_by_category("structural")
        assert len(results) >= 3

    def test_extreme_category(self):
        results = table_8_4_by_category("extreme")
        assert len(results) == 3


# ============================================================================
# Table 9-1: Lateral resistance factors
# ============================================================================

class TestTable91LateralResistanceFactor:

    def test_individual(self):
        result = table_9_1_lateral_resistance_factor("individual")
        assert result["phi"] == 0.67

    def test_group(self):
        result = table_9_1_lateral_resistance_factor("group")
        assert result["phi"] == 0.80

    def test_extreme(self):
        result = table_9_1_lateral_resistance_factor("extreme")
        assert result["phi"] == 0.80

    def test_alias_single(self):
        result = table_9_1_lateral_resistance_factor("single")
        assert result["phi"] == 0.67

    def test_alias_seismic(self):
        result = table_9_1_lateral_resistance_factor("seismic")
        assert result["phi"] == 0.80

    def test_alias_extreme_event(self):
        result = table_9_1_lateral_resistance_factor("extreme_event")
        assert result["phi"] == 0.80

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_9_1_lateral_resistance_factor("unknown_xyz")

    def test_result_has_description(self):
        result = table_9_1_lateral_resistance_factor("individual")
        assert "description" in result
        assert len(result["description"]) > 5


# ============================================================================
# Table 10-2: N*c bearing capacity factor for base resistance in cohesive soil
# ============================================================================

class TestTable102NcBaseClay:

    def test_su500_returns_65(self):
        result = table_10_2_nc_base_clay(500)
        assert abs(result["nc_star"] - 6.5) < 0.01

    def test_su1000_returns_80(self):
        result = table_10_2_nc_base_clay(1000)
        assert abs(result["nc_star"] - 8.0) < 0.01

    def test_su2000_returns_90(self):
        result = table_10_2_nc_base_clay(2000)
        assert abs(result["nc_star"] - 9.0) < 0.01

    def test_su_above_2000_clamped_to_90(self):
        result = table_10_2_nc_base_clay(5000)
        assert abs(result["nc_star"] - 9.0) < 0.01

    def test_su_low_clamped_to_65(self):
        result = table_10_2_nc_base_clay(100)
        assert abs(result["nc_star"] - 6.5) < 0.01

    def test_interpolation_su750(self):
        """750 psf is halfway between 500 and 1000; Nc* should be ~7.25."""
        result = table_10_2_nc_base_clay(750)
        assert abs(result["nc_star"] - 7.25) < 0.1

    def test_nc_increases_with_su(self):
        assert table_10_2_nc_base_clay(600)["nc_star"] > table_10_2_nc_base_clay(500)["nc_star"]
        assert table_10_2_nc_base_clay(1500)["nc_star"] > table_10_2_nc_base_clay(1000)["nc_star"]

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            table_10_2_nc_base_clay(0)

    def test_result_has_note(self):
        result = table_10_2_nc_base_clay(2000)
        assert "note" in result


# ============================================================================
# Table 11-1: P-multipliers for lateral group analysis
# ============================================================================

class TestTable111PMult:

    def test_lead_3d(self):
        result = table_11_1_p_multiplier("lead", 3.0)
        assert result["pm"] == 0.70

    def test_lead_4d(self):
        result = table_11_1_p_multiplier("lead", 4.0)
        assert result["pm"] == 0.85

    def test_lead_5d(self):
        result = table_11_1_p_multiplier("lead", 5.0)
        assert result["pm"] == 1.00

    def test_2nd_3d(self):
        result = table_11_1_p_multiplier("2nd", 3.0)
        assert result["pm"] == 0.50

    def test_2nd_4d(self):
        result = table_11_1_p_multiplier("2nd", 4.0)
        assert result["pm"] == 0.65

    def test_2nd_5d(self):
        result = table_11_1_p_multiplier("2nd", 5.0)
        assert result["pm"] == 0.85

    def test_3rd_3d(self):
        result = table_11_1_p_multiplier("3rd", 3.0)
        assert result["pm"] == 0.35

    def test_3rd_4d(self):
        result = table_11_1_p_multiplier("3rd", 4.0)
        assert result["pm"] == 0.50

    def test_3rd_5d(self):
        result = table_11_1_p_multiplier("3rd", 5.0)
        assert result["pm"] == 0.70

    def test_all_rows_6d_equal_1(self):
        for row in ("lead", "2nd", "3rd"):
            assert table_11_1_p_multiplier(row, 6.0)["pm"] == 1.0

    def test_alias_trail(self):
        result = table_11_1_p_multiplier("trail", 3.0)
        assert result["pm"] == 0.35

    def test_alias_front(self):
        result = table_11_1_p_multiplier("front", 3.0)
        assert result["pm"] == 0.70

    def test_interpolation_35d(self):
        result = table_11_1_p_multiplier("lead", 3.5)
        assert 0.70 < result["pm"] < 0.85

    def test_spacing_above_6d(self):
        result = table_11_1_p_multiplier("2nd", 8.0)
        assert result["pm"] == 1.0

    def test_spacing_below_3d_raises(self):
        with pytest.raises(ValueError, match="minimum"):
            table_11_1_p_multiplier("lead", 2.5)

    def test_unknown_row_raises(self):
        with pytest.raises(ValueError):
            table_11_1_p_multiplier("invalid_row", 3.0)

    def test_result_has_notes(self):
        result = table_11_1_p_multiplier("lead", 4.0)
        assert "notes" in result

    def test_lead_row_higher_than_trailing(self):
        """Lead row Pm > 2nd row Pm > 3rd row Pm at same spacing."""
        lead = table_11_1_p_multiplier("lead", 3.0)["pm"]
        second = table_11_1_p_multiplier("2nd", 3.0)["pm"]
        third = table_11_1_p_multiplier("3rd", 3.0)["pm"]
        assert lead > second > third

    def test_2x2_group_weighted_average(self):
        """2x2 group: average Pm = [2(lead) + 2(2nd)] / 4 = (0.7+0.5)/2 = 0.60 at 3D."""
        lead = table_11_1_p_multiplier("lead", 3.0)["pm"]
        second = table_11_1_p_multiplier("2nd", 3.0)["pm"]
        avg = (2 * lead + 2 * second) / 4
        assert abs(avg - 0.60) < 0.01

    def test_2x3_group_weighted_average(self):
        """2x3 group: [2(0.7)+2(0.5)+2(0.35)]/6 = 0.52 at 3D (manual example)."""
        lead = table_11_1_p_multiplier("lead", 3.0)["pm"]
        second = table_11_1_p_multiplier("2nd", 3.0)["pm"]
        third = table_11_1_p_multiplier("3rd", 3.0)["pm"]
        avg = (2 * lead + 2 * second + 2 * third) / 6
        assert abs(avg - 0.517) < 0.01


# ============================================================================
# Group efficiency for cohesionless soils (AASHTO 10.8.3.6.3)
# ============================================================================

class TestTable112GroupEfficiency:

    def test_spacing_25d(self):
        result = table_11_2_group_efficiency_cohesionless(2.5)
        assert abs(result["eta"] - 0.65) < 0.001

    def test_spacing_3d(self):
        result = table_11_2_group_efficiency_cohesionless(3.0)
        assert abs(result["eta"] - 0.80) < 0.001

    def test_spacing_4d(self):
        result = table_11_2_group_efficiency_cohesionless(4.0)
        assert abs(result["eta"] - 1.00) < 0.001

    def test_spacing_above_4d_clamped(self):
        result = table_11_2_group_efficiency_cohesionless(6.0)
        assert abs(result["eta"] - 1.00) < 0.001

    def test_interpolation_275d(self):
        """2.75D is between 2.5 and 3.0; should interpolate to ~0.725."""
        result = table_11_2_group_efficiency_cohesionless(2.75)
        assert abs(result["eta"] - 0.725) < 0.01

    def test_eta_increases_with_spacing(self):
        eta_25 = table_11_2_group_efficiency_cohesionless(2.5)["eta"]
        eta_3 = table_11_2_group_efficiency_cohesionless(3.0)["eta"]
        eta_4 = table_11_2_group_efficiency_cohesionless(4.0)["eta"]
        assert eta_25 < eta_3 < eta_4

    def test_below_minimum_raises(self):
        with pytest.raises(ValueError, match="minimum"):
            table_11_2_group_efficiency_cohesionless(2.0)

    def test_result_has_note(self):
        result = table_11_2_group_efficiency_cohesionless(3.0)
        assert "note" in result


# ============================================================================
# Reliability index ↔ probability of failure
# ============================================================================

class TestAashtoReliabilityIndex:

    def test_beta_3(self):
        result = aashto_reliability_index(beta=3.0)
        assert result["beta"] == 3.0
        assert abs(result["pf"] - 1.35e-3) < 1e-4

    def test_beta_2(self):
        result = aashto_reliability_index(beta=2.0)
        assert abs(result["pf"] - 2.28e-2) < 1e-3

    def test_pf_given(self):
        result = aashto_reliability_index(pf=1.0e-2)
        assert abs(result["beta"] - 2.33) < 0.01

    def test_both_raises(self):
        with pytest.raises(ValueError, match="not both"):
            aashto_reliability_index(beta=3.0, pf=1e-3)

    def test_neither_raises(self):
        with pytest.raises(ValueError, match="either"):
            aashto_reliability_index()

    def test_beta_out_of_range(self):
        with pytest.raises(ValueError):
            aashto_reliability_index(beta=5.0)
