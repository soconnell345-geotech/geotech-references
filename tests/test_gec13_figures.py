"""Tests for GEC-13 figure lookup functions."""

import pytest
import math

from geotech_references.gec_13.figures import (
    figure_4_3_suitability_number,
    figure_5_2_area_replacement_ratio,
    figure_5_5_settlement_improvement,
)


# ============================================================================
# Figure 4-3: Vibro-Compaction Suitability Number
# ============================================================================

class TestFigure43:
    """Tests for figure_4_3_suitability_number()."""

    def test_clean_sand_excellent(self):
        """Clean medium sand: D50=0.5, D20=0.3, D10=0.15."""
        result = figure_4_3_suitability_number(0.5, 0.3, 0.15)
        assert result["suitability_number"] < 20
        assert result["rating"] in ("Excellent", "Good")

    def test_fine_sand_fair(self):
        """Fine sand with fines: D50=0.2, D20=0.08, D10=0.04."""
        result = figure_4_3_suitability_number(0.2, 0.08, 0.04)
        assert result["suitability_number"] > 20

    def test_silt_not_suitable(self):
        """Silt: D50=0.03, D20=0.01, D10=0.005."""
        result = figure_4_3_suitability_number(0.03, 0.01, 0.005)
        assert result["suitability_number"] > 50
        assert result["rating"] == "Not suitable"

    def test_coarse_sand_excellent(self):
        """Coarse sand: D50=2.0, D20=0.8, D10=0.4."""
        result = figure_4_3_suitability_number(2.0, 0.8, 0.4)
        assert result["rating"] == "Excellent"
        assert result["suitability_number"] < 10

    def test_zero_grain_size_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            figure_4_3_suitability_number(0.5, 0.3, 0)

    def test_wrong_order_raises(self):
        with pytest.raises(ValueError, match="D10 <= D20 <= D50"):
            figure_4_3_suitability_number(0.1, 0.3, 0.5)

    def test_result_has_all_keys(self):
        result = figure_4_3_suitability_number(1.0, 0.5, 0.2)
        assert "suitability_number" in result
        assert "rating" in result
        assert "d50_mm" in result
        assert "d20_mm" in result
        assert "d10_mm" in result
        assert "description" in result


# ============================================================================
# Figure 5-2: Area Replacement Ratio
# ============================================================================

class TestFigure52:
    """Tests for figure_5_2_area_replacement_ratio()."""

    def test_triangular_typical(self):
        """0.9 m column at 2.4 m triangular spacing."""
        result = figure_5_2_area_replacement_ratio(0.9, 2.4, "triangular")
        expected = (math.pi / 4 * 0.9**2) / (0.866 * 2.4**2)
        assert abs(result["area_replacement_ratio"] - expected) < 0.001

    def test_square_typical(self):
        """0.9 m column at 2.4 m square spacing."""
        result = figure_5_2_area_replacement_ratio(0.9, 2.4, "square")
        expected = (math.pi / 4 * 0.9**2) / (2.4**2)
        assert abs(result["area_replacement_ratio"] - expected) < 0.001

    def test_triangular_higher_than_square(self):
        """Triangular has smaller tributary area, so higher as."""
        tri = figure_5_2_area_replacement_ratio(0.6, 1.8, "triangular")
        sq = figure_5_2_area_replacement_ratio(0.6, 1.8, "square")
        assert tri["area_replacement_ratio"] > sq["area_replacement_ratio"]

    def test_zero_diameter_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            figure_5_2_area_replacement_ratio(0, 2.0)

    def test_spacing_less_than_diameter_raises(self):
        with pytest.raises(ValueError, match="must exceed"):
            figure_5_2_area_replacement_ratio(1.0, 0.8)

    def test_unknown_pattern_raises(self):
        with pytest.raises(ValueError, match="Unknown pattern"):
            figure_5_2_area_replacement_ratio(0.6, 1.8, "hexagonal")

    def test_result_has_all_keys(self):
        result = figure_5_2_area_replacement_ratio(0.6, 1.8)
        assert "area_replacement_ratio" in result
        assert "column_area_m2" in result
        assert "tributary_area_m2" in result
        assert "pattern" in result


# ============================================================================
# Figure 5-5: Settlement Improvement Factor
# ============================================================================

class TestFigure55:
    """Tests for figure_5_5_settlement_improvement()."""

    def test_typical_values(self):
        """as=0.20, n=3 -> SRF = 1/(1+0.2*2) = 1/1.4 = 0.714."""
        result = figure_5_5_settlement_improvement(0.20, 3.0)
        expected_srf = 1.0 / (1.0 + 0.20 * 2.0)
        assert abs(result["settlement_reduction_factor"] - expected_srf) < 0.001

    def test_improvement_factor_inverse(self):
        """SIF = 1/SRF."""
        result = figure_5_5_settlement_improvement(0.25, 4.0)
        srf = result["settlement_reduction_factor"]
        sif = result["settlement_improvement_factor"]
        assert abs(sif - 1.0 / srf) < 0.01

    def test_higher_as_lower_srf(self):
        """Higher area replacement ratio -> lower SRF (more improvement)."""
        r1 = figure_5_5_settlement_improvement(0.10, 3.0)
        r2 = figure_5_5_settlement_improvement(0.30, 3.0)
        assert r2["settlement_reduction_factor"] < r1["settlement_reduction_factor"]

    def test_higher_n_lower_srf(self):
        """Higher stress ratio -> lower SRF."""
        r1 = figure_5_5_settlement_improvement(0.20, 2.0)
        r2 = figure_5_5_settlement_improvement(0.20, 5.0)
        assert r2["settlement_reduction_factor"] < r1["settlement_reduction_factor"]

    def test_n_equals_1_no_improvement(self):
        """n=1 means no stress concentration, SRF=1."""
        result = figure_5_5_settlement_improvement(0.20, 1.0)
        assert abs(result["settlement_reduction_factor"] - 1.0) < 0.001

    def test_zero_as_raises(self):
        with pytest.raises(ValueError, match="between 0 and 1"):
            figure_5_5_settlement_improvement(0.0, 3.0)

    def test_as_above_1_raises(self):
        with pytest.raises(ValueError, match="between 0 and 1"):
            figure_5_5_settlement_improvement(1.0, 3.0)

    def test_n_below_1_raises(self):
        with pytest.raises(ValueError, match="must be >= 1"):
            figure_5_5_settlement_improvement(0.20, 0.5)
