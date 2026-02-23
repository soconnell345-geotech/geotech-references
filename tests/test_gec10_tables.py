"""Tests for GEC-10 table lookup functions."""

import pytest

from geotech_references.gec_10.tables import (
    table_10_5_resistance_factor,
    table_10_5_by_category,
    table_12_1_lateral_resistance_factor,
    table_14_1_group_efficiency,
    table_14_2_p_multiplier,
    table_10_1_reliability_index,
)


# ============================================================================
# Table 10-5: LRFD Resistance Factors
# ============================================================================

class TestTable105:
    """Tests for table_10_5_resistance_factor()."""

    def test_lateral_pushover_individual(self):
        result = table_10_5_resistance_factor("lateral_pushover_individual")
        assert result["phi"] == 0.67

    def test_lateral_pushover_group(self):
        result = table_10_5_resistance_factor("lateral_pushover_group")
        assert result["phi"] == 0.80

    def test_side_sand_beta(self):
        result = table_10_5_resistance_factor("side_sand_beta_static_calculated")
        assert result["phi"] == 0.55

    def test_side_clay_alpha(self):
        result = table_10_5_resistance_factor("side_clay_alpha_static_calculated")
        assert result["phi"] == 0.45

    def test_side_rock(self):
        result = table_10_5_resistance_factor("side_rock_calculated")
        assert result["phi"] == 0.55

    def test_side_igm(self):
        result = table_10_5_resistance_factor("side_igm_calculated")
        assert result["phi"] == 0.60

    def test_base_sand(self):
        result = table_10_5_resistance_factor("base_sand_calculated")
        assert result["phi"] == 0.50

    def test_base_clay(self):
        result = table_10_5_resistance_factor("base_clay_calculated")
        assert result["phi"] == 0.40

    def test_base_rock(self):
        result = table_10_5_resistance_factor("base_rock_calculated")
        assert result["phi"] == 0.50

    def test_load_test_compression(self):
        result = table_10_5_resistance_factor("load_test_compression")
        assert result["phi"] == 0.70

    def test_load_test_uplift(self):
        result = table_10_5_resistance_factor("load_test_uplift")
        assert result["phi"] == 0.60

    def test_group_block_failure(self):
        result = table_10_5_resistance_factor("group_block_failure")
        assert result["phi"] == 0.55

    def test_group_uplift(self):
        result = table_10_5_resistance_factor("group_uplift")
        assert result["phi"] == 0.45

    def test_structural_compression(self):
        result = table_10_5_resistance_factor("structural_compression")
        assert result["phi"] == 0.75

    def test_structural_shear(self):
        result = table_10_5_resistance_factor("structural_shear")
        assert result["phi"] == 0.90

    def test_extreme_uplift(self):
        result = table_10_5_resistance_factor("extreme_uplift")
        assert result["phi"] == 0.80

    def test_extreme_lateral(self):
        result = table_10_5_resistance_factor("extreme_lateral")
        assert result["phi"] == 0.80

    def test_partial_match_side_sand(self):
        """Partial match 'side_sand' should find side_sand_beta_static_calculated."""
        result = table_10_5_resistance_factor("side_sand")
        assert result["phi"] in (0.55, 0.45)

    def test_partial_match_base(self):
        """Partial match 'base_sand' should find base_sand_calculated."""
        result = table_10_5_resistance_factor("base_sand")
        assert result["phi"] == 0.50

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError, match="No matching method"):
            table_10_5_resistance_factor("nonexistent_xyz")

    def test_result_has_method_key(self):
        result = table_10_5_resistance_factor("structural_shear")
        assert "method" in result
        assert result["method"] == "structural_shear"

    def test_result_has_condition(self):
        result = table_10_5_resistance_factor("base_clay_calculated")
        assert "condition" in result
        assert len(result["condition"]) > 0

    def test_result_has_category(self):
        result = table_10_5_resistance_factor("base_clay_calculated")
        assert result["category"] == "compression_base"


class TestTable105ByCategory:
    """Tests for table_10_5_by_category()."""

    def test_all_categories(self):
        results = table_10_5_by_category("")
        assert len(results) > 20

    def test_lateral_category(self):
        results = table_10_5_by_category("lateral")
        assert len(results) == 2
        assert all(r["category"] == "lateral" for r in results)

    def test_compression_side(self):
        results = table_10_5_by_category("compression_side")
        assert len(results) >= 8

    def test_compression_base(self):
        results = table_10_5_by_category("compression_base")
        assert len(results) >= 4

    def test_structural(self):
        results = table_10_5_by_category("structural")
        assert len(results) >= 4

    def test_extreme(self):
        results = table_10_5_by_category("extreme")
        assert len(results) == 2


# ============================================================================
# Table 12-1: Lateral Resistance Factors
# ============================================================================

class TestTable121:
    """Tests for table_12_1_lateral_resistance_factor()."""

    def test_p_y_single(self):
        result = table_12_1_lateral_resistance_factor("p_y_single")
        assert result["phi"] == 0.67

    def test_broms(self):
        result = table_12_1_lateral_resistance_factor("broms")
        assert result["phi"] == 0.40

    def test_p_y_group(self):
        result = table_12_1_lateral_resistance_factor("p_y_group")
        assert result["phi"] == 0.80

    def test_extreme(self):
        result = table_12_1_lateral_resistance_factor("extreme")
        assert result["phi"] == 0.80

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown method"):
            table_12_1_lateral_resistance_factor("unknown_xyz")


# ============================================================================
# Table 14-1: Group Efficiency
# ============================================================================

class TestTable141:
    """Tests for table_14_1_group_efficiency()."""

    def test_2x1(self):
        result = table_14_1_group_efficiency("2x1")
        assert result["efficiency"] == 1.10

    def test_3x1(self):
        result = table_14_1_group_efficiency("3x1")
        assert result["efficiency"] == 1.10

    def test_3_triangular(self):
        result = table_14_1_group_efficiency("3_triangular")
        assert result["efficiency"] == 1.04

    def test_4_square(self):
        result = table_14_1_group_efficiency("4_square")
        assert result["efficiency"] == 1.00

    def test_3x3(self):
        result = table_14_1_group_efficiency("3x3")
        assert result["efficiency"] == 0.90

    def test_4x4(self):
        result = table_14_1_group_efficiency("4x4")
        assert result["efficiency"] == 0.80

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown configuration"):
            table_14_1_group_efficiency("99x99")


# ============================================================================
# Table 14-2: P-Multipliers
# ============================================================================

class TestTable142:
    """Tests for table_14_2_p_multiplier()."""

    def test_lead_row_3d(self):
        result = table_14_2_p_multiplier("lead", 3.0)
        assert result["p_multiplier"] == 0.70

    def test_lead_row_5d(self):
        result = table_14_2_p_multiplier("lead", 5.0)
        assert result["p_multiplier"] == 1.00

    def test_2nd_row_3d(self):
        result = table_14_2_p_multiplier("2nd", 3.0)
        assert result["p_multiplier"] == 0.50

    def test_2nd_row_4d(self):
        result = table_14_2_p_multiplier("2nd", 4.0)
        assert result["p_multiplier"] == 0.65

    def test_3rd_row_3d(self):
        result = table_14_2_p_multiplier("3rd", 3.0)
        assert result["p_multiplier"] == 0.35

    def test_3rd_row_5d(self):
        result = table_14_2_p_multiplier("3rd", 5.0)
        assert result["p_multiplier"] == 0.70

    def test_trailing_row_alias(self):
        result = table_14_2_p_multiplier("trail", 3.0)
        assert result["p_multiplier"] == 0.35

    def test_all_rows_6d_equal_1(self):
        for row in ["lead", "2nd", "3rd"]:
            result = table_14_2_p_multiplier(row, 6.0)
            assert result["p_multiplier"] == 1.0

    def test_interpolation_35d(self):
        result = table_14_2_p_multiplier("lead", 3.5)
        assert 0.70 < result["p_multiplier"] < 0.85

    def test_spacing_above_6d(self):
        result = table_14_2_p_multiplier("2nd", 8.0)
        assert result["p_multiplier"] == 1.0

    def test_spacing_below_3d_raises(self):
        with pytest.raises(ValueError, match="below the minimum"):
            table_14_2_p_multiplier("lead", 2.5)

    def test_unknown_row_raises(self):
        with pytest.raises(ValueError, match="Unknown row_position"):
            table_14_2_p_multiplier("invalid", 3.0)

    def test_result_has_notes(self):
        result = table_14_2_p_multiplier("lead", 4.0)
        assert "notes" in result
        assert "Lead" in result["notes"] or "lead" in result["notes"].lower()


# ============================================================================
# Table 10-1: Reliability Index
# ============================================================================

class TestTable101:
    """Tests for table_10_1_reliability_index()."""

    def test_beta_3(self):
        result = table_10_1_reliability_index(beta=3.0)
        assert result["beta"] == 3.0
        assert abs(result["pf"] - 1.35e-3) < 1e-4

    def test_beta_2(self):
        result = table_10_1_reliability_index(beta=2.0)
        assert abs(result["pf"] - 2.28e-2) < 1e-3

    def test_pf_given(self):
        result = table_10_1_reliability_index(pf=1.0e-2)
        assert abs(result["beta"] - 2.33) < 0.01

    def test_both_raises(self):
        with pytest.raises(ValueError, match="not both"):
            table_10_1_reliability_index(beta=3.0, pf=1e-3)

    def test_neither_raises(self):
        with pytest.raises(ValueError, match="either"):
            table_10_1_reliability_index()

    def test_beta_out_of_range(self):
        with pytest.raises(ValueError, match="2.0-4.0"):
            table_10_1_reliability_index(beta=5.0)
