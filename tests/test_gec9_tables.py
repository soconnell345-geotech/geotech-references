"""Tests for GEC-9 table lookup functions (FHWA-HIF-18-031)."""

import pytest

from geotech_references.gec_9.tables import (
    table_4_1_lateral_resistance_factor,
    table_7_1_p_multiplier,
    table_a1_k_stiff_clay,
    table_a2_epsilon50_stiff_clay,
    table_a3_k_sand,
)


# ============================================================================
# Table 4-1: LRFD Lateral Resistance Factors
# ============================================================================

class TestTable41LateralResistanceFactor:

    def test_individual(self):
        result = table_4_1_lateral_resistance_factor("individual")
        assert result["phi_r"] == 0.67
        assert result["condition"] == "individual"

    def test_single_row(self):
        result = table_4_1_lateral_resistance_factor("single_row")
        assert result["phi_r"] == 0.67
        assert result["condition"] == "single_row"

    def test_group(self):
        result = table_4_1_lateral_resistance_factor("group")
        assert result["phi_r"] == 0.80
        assert result["condition"] == "group"

    def test_alias_free_head(self):
        result = table_4_1_lateral_resistance_factor("free_head")
        assert result["phi_r"] == 0.67

    def test_alias_wall(self):
        result = table_4_1_lateral_resistance_factor("wall")
        assert result["phi_r"] == 0.67

    def test_alias_abutment(self):
        result = table_4_1_lateral_resistance_factor("abutment")
        assert result["phi_r"] == 0.67

    def test_alias_multi_row(self):
        result = table_4_1_lateral_resistance_factor("multi_row")
        assert result["phi_r"] == 0.80

    def test_alias_moment_connection(self):
        result = table_4_1_lateral_resistance_factor("moment_connection")
        assert result["phi_r"] == 0.80

    def test_individual_and_single_row_equal(self):
        r1 = table_4_1_lateral_resistance_factor("individual")
        r2 = table_4_1_lateral_resistance_factor("single_row")
        assert r1["phi_r"] == r2["phi_r"]

    def test_result_has_description(self):
        result = table_4_1_lateral_resistance_factor("group")
        assert "description" in result
        assert len(result["description"]) > 0

    def test_invalid_condition(self):
        with pytest.raises(ValueError):
            table_4_1_lateral_resistance_factor("nonexistent")


# ============================================================================
# Table 7-1: P-Multipliers for Group Analysis
# ============================================================================

class TestTable71PMuliplier:

    # --- Tabulated values at 3B ---
    def test_lead_row_3b(self):
        result = table_7_1_p_multiplier("lead", 3.0)
        assert result["pm"] == 0.8

    def test_2nd_row_3b(self):
        result = table_7_1_p_multiplier("2nd", 3.0)
        assert result["pm"] == 0.4

    def test_3rd_row_3b(self):
        result = table_7_1_p_multiplier("3rd", 3.0)
        assert result["pm"] == 0.3

    # --- Tabulated values at 5B ---
    def test_lead_row_5b(self):
        result = table_7_1_p_multiplier("lead", 5.0)
        assert result["pm"] == 1.0

    def test_2nd_row_5b(self):
        result = table_7_1_p_multiplier("2nd", 5.0)
        assert result["pm"] == 0.85

    def test_3rd_row_5b(self):
        result = table_7_1_p_multiplier("3rd", 5.0)
        assert result["pm"] == 0.7

    # --- Beyond 5B: clamp at 5B values (no extrapolation beyond table range) ---
    def test_lead_row_beyond_5b(self):
        result = table_7_1_p_multiplier("lead", 6.0)
        assert result["pm"] == 1.0  # 5B value for row 1 is already 1.0

    def test_2nd_row_beyond_5b(self):
        result = table_7_1_p_multiplier("2nd", 6.0)
        assert result["pm"] == 0.85  # clamped at 5B tabulated value

    def test_3rd_row_beyond_5b(self):
        result = table_7_1_p_multiplier("3rd", 6.0)
        assert result["pm"] == 0.7  # clamped at 5B tabulated value

    # --- Interpolation at 4B ---
    def test_lead_row_4b_interpolated(self):
        result = table_7_1_p_multiplier("lead", 4.0)
        assert abs(result["pm"] - 0.9) < 1e-6

    def test_2nd_row_4b_interpolated(self):
        result = table_7_1_p_multiplier("2nd", 4.0)
        assert abs(result["pm"] - 0.625) < 1e-6

    def test_3rd_row_4b_interpolated(self):
        result = table_7_1_p_multiplier("3rd", 4.0)
        assert abs(result["pm"] - 0.5) < 1e-6

    # --- Aliases ---
    def test_alias_front(self):
        result = table_7_1_p_multiplier("front", 3.0)
        assert result["row_position"] == "lead_row"

    def test_alias_trailing(self):
        result = table_7_1_p_multiplier("trailing", 3.0)
        assert result["row_position"] == "3rd_or_more_row"

    def test_alias_second(self):
        result = table_7_1_p_multiplier("second", 3.0)
        assert result["row_position"] == "2nd_row"

    def test_alias_4th_is_3rd_or_more(self):
        result = table_7_1_p_multiplier("4th", 3.0)
        assert result["row_position"] == "3rd_or_more_row"

    # --- Error cases ---
    def test_spacing_below_3b(self):
        with pytest.raises(ValueError):
            table_7_1_p_multiplier("lead", 2.5)

    def test_invalid_row_position(self):
        with pytest.raises(ValueError):
            table_7_1_p_multiplier("seventh", 3.0)

    # --- Return dict structure ---
    def test_result_has_expected_keys(self):
        result = table_7_1_p_multiplier("lead", 3.0)
        assert "row_position" in result
        assert "spacing_over_b" in result
        assert "pm" in result
        assert "notes" in result


# ============================================================================
# Table A-1: k for Stiff Clay (pci)
# ============================================================================

class TestTableA1KStiffClay:

    def test_static_low_ca(self):
        result = table_a1_k_stiff_clay(0.75, "static")
        assert result["k_pci"] == 500.0

    def test_static_mid_ca(self):
        result = table_a1_k_stiff_clay(1.5, "static")
        assert result["k_pci"] == 1000.0

    def test_static_high_ca(self):
        result = table_a1_k_stiff_clay(3.0, "static")
        assert result["k_pci"] == 2000.0

    def test_cyclic_low_ca(self):
        result = table_a1_k_stiff_clay(0.75, "cyclic")
        assert result["k_pci"] == 200.0

    def test_cyclic_mid_ca(self):
        result = table_a1_k_stiff_clay(1.5, "cyclic")
        assert result["k_pci"] == 400.0

    def test_cyclic_high_ca(self):
        result = table_a1_k_stiff_clay(3.0, "cyclic")
        assert result["k_pci"] == 800.0

    # --- Bin boundary checks ---
    def test_at_boundary_1tsf_goes_to_mid(self):
        # Ca=1.0 is boundary between 0.5-1 and 1-2; GEC-9 bin is [0.5,1) so 1.0 → mid bin
        result = table_a1_k_stiff_clay(1.0, "static")
        assert result["k_pci"] == 1000.0

    def test_at_boundary_2tsf_goes_to_high(self):
        result = table_a1_k_stiff_clay(2.0, "static")
        assert result["k_pci"] == 2000.0

    def test_static_at_max_range(self):
        # ca=4.0 → high bin → k=2000
        result = table_a1_k_stiff_clay(4.0, "static")
        assert result["k_pci"] == 2000.0

    def test_result_has_expected_keys(self):
        result = table_a1_k_stiff_clay(1.0, "static")
        assert "ca_tsf" in result
        assert "loading" in result
        assert "k_pci" in result
        assert "ca_range_tsf" in result

    def test_invalid_ca(self):
        with pytest.raises(ValueError):
            table_a1_k_stiff_clay(-0.5, "static")

    def test_invalid_loading(self):
        with pytest.raises(ValueError):
            table_a1_k_stiff_clay(1.0, "monotonic")


# ============================================================================
# Table A-2: ε50 for Stiff Clay
# ============================================================================

class TestTableA2Epsilon50StiffClay:

    def test_low_ca(self):
        result = table_a2_epsilon50_stiff_clay(0.75)
        assert result["epsilon_50"] == 0.007

    def test_mid_ca(self):
        result = table_a2_epsilon50_stiff_clay(1.5)
        assert result["epsilon_50"] == 0.005

    def test_high_ca(self):
        result = table_a2_epsilon50_stiff_clay(3.0)
        assert result["epsilon_50"] == 0.004

    def test_higher_su_gives_lower_eps50(self):
        r1 = table_a2_epsilon50_stiff_clay(0.75)
        r2 = table_a2_epsilon50_stiff_clay(3.0)
        assert r1["epsilon_50"] > r2["epsilon_50"]

    def test_result_has_expected_keys(self):
        result = table_a2_epsilon50_stiff_clay(1.5)
        assert "ca_tsf" in result
        assert "epsilon_50" in result
        assert "ca_range_tsf" in result

    def test_invalid_ca(self):
        with pytest.raises(ValueError):
            table_a2_epsilon50_stiff_clay(0.0)


# ============================================================================
# Table A-3: k for Sand (pci)
# ============================================================================

class TestTableA3KSand:

    def test_loose_submerged(self):
        result = table_a3_k_sand("loose", "submerged")
        assert result["k_pci"] == 20.0

    def test_loose_above_water(self):
        result = table_a3_k_sand("loose", "above_water")
        assert result["k_pci"] == 25.0

    def test_medium_submerged(self):
        result = table_a3_k_sand("medium", "submerged")
        assert result["k_pci"] == 60.0

    def test_medium_above_water(self):
        result = table_a3_k_sand("medium", "above_water")
        assert result["k_pci"] == 90.0

    def test_dense_submerged(self):
        result = table_a3_k_sand("dense", "submerged")
        assert result["k_pci"] == 125.0

    def test_dense_above_water(self):
        result = table_a3_k_sand("dense", "above_water")
        assert result["k_pci"] == 225.0

    def test_above_water_greater_than_submerged(self):
        for rd in ("loose", "medium", "dense"):
            r_sub = table_a3_k_sand(rd, "submerged")
            r_ab = table_a3_k_sand(rd, "above_water")
            assert r_ab["k_pci"] > r_sub["k_pci"]

    def test_denser_gives_higher_k(self):
        r_loose = table_a3_k_sand("loose", "submerged")
        r_medium = table_a3_k_sand("medium", "submerged")
        r_dense = table_a3_k_sand("dense", "submerged")
        assert r_loose["k_pci"] < r_medium["k_pci"] < r_dense["k_pci"]

    def test_alias_medium_dense(self):
        result = table_a3_k_sand("medium_dense", "submerged")
        assert result["k_pci"] == 60.0
        assert result["relative_density"] == "medium"

    def test_alias_below_water(self):
        result = table_a3_k_sand("dense", "below_water")
        assert result["k_pci"] == 125.0

    def test_default_condition_is_submerged(self):
        result = table_a3_k_sand("dense")
        assert result["condition"] == "submerged"

    def test_result_has_expected_keys(self):
        result = table_a3_k_sand("medium", "submerged")
        assert "relative_density" in result
        assert "condition" in result
        assert "k_pci" in result
        assert "source" in result

    def test_invalid_relative_density(self):
        with pytest.raises(ValueError):
            table_a3_k_sand("very_dense", "submerged")

    def test_invalid_condition(self):
        with pytest.raises(ValueError):
            table_a3_k_sand("loose", "wet")
