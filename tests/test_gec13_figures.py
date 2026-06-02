"""Tests for GEC-13 figure lookup functions."""

import pytest
import math

from geotech_references.gec_13.figures import (
    figure_4_3_suitability_number,
    figure_5_2_area_replacement_ratio,
    figure_5_5_settlement_improvement,
    equation_7_4_composite_modulus,
    equation_8_1_groutability_ratio,
    equation_11_1_ltds,
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


# ============================================================================
# Equation 7-4: Deep Mixing Composite Modulus
# ============================================================================

class TestEquation74:
    """Tests for equation_7_4_composite_modulus()."""

    def test_typical_values(self):
        """a_s=0.20, E_col=50,000 kPa, E_soil=1,000 kPa."""
        result = equation_7_4_composite_modulus(50000, 1000, 0.20)
        expected = 0.20 * 50000 + 0.80 * 1000
        assert abs(result["e_comp_kpa"] - expected) < 1.0

    def test_stress_concentration_ratio(self):
        """n = E_col / E_soil."""
        result = equation_7_4_composite_modulus(100000, 2000, 0.15)
        assert abs(result["stress_concentration_ratio"] - 50.0) < 0.1

    def test_as_zero_limit(self):
        """Very small a_s → E_comp ≈ E_soil."""
        result = equation_7_4_composite_modulus(100000, 2000, 0.001)
        assert result["e_comp_kpa"] == pytest.approx(2098.0, abs=10)

    def test_as_near_one_limit(self):
        """Very large a_s → E_comp ≈ E_col."""
        result = equation_7_4_composite_modulus(100000, 2000, 0.999)
        assert result["e_comp_kpa"] == pytest.approx(99902.0, abs=10)

    def test_zero_col_modulus_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            equation_7_4_composite_modulus(0, 2000, 0.20)

    def test_zero_soil_modulus_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            equation_7_4_composite_modulus(50000, 0, 0.20)

    def test_as_out_of_range_raises(self):
        with pytest.raises(ValueError, match="between 0 and 1"):
            equation_7_4_composite_modulus(50000, 2000, 1.5)

    def test_result_has_all_keys(self):
        result = equation_7_4_composite_modulus(50000, 1000, 0.20)
        for key in ("e_comp_kpa", "e_col_kpa", "e_soil_kpa",
                    "area_replacement_ratio", "stress_concentration_ratio"):
            assert key in result


# ============================================================================
# Equation 8-1: Groutability Ratio
# ============================================================================

class TestEquation81:
    """Tests for equation_8_1_groutability_ratio()."""

    def test_feasible(self):
        """D15_soil=0.5 mm, D85_grout=0.015 mm → N=33.3 → Feasible."""
        result = equation_8_1_groutability_ratio(0.5, 0.015)
        assert result["groutability_ratio"] == pytest.approx(33.33, abs=0.1)
        assert result["feasibility"] == "Feasible"

    def test_uncertain(self):
        """N between 11 and 25."""
        result = equation_8_1_groutability_ratio(0.3, 0.018)
        assert 11 <= result["groutability_ratio"] <= 25
        assert result["feasibility"] == "Uncertain"

    def test_not_feasible(self):
        """D15_soil=0.1 mm, D85_grout=0.020 mm → N=5 → Not feasible."""
        result = equation_8_1_groutability_ratio(0.1, 0.020)
        assert result["groutability_ratio"] < 11
        assert result["feasibility"] == "Not feasible"

    def test_boundary_exactly_25(self):
        """N exactly 25 → Uncertain (threshold is N > 25 for Feasible)."""
        result = equation_8_1_groutability_ratio(0.25, 0.01)
        assert result["groutability_ratio"] == pytest.approx(25.0, abs=0.01)
        assert result["feasibility"] == "Uncertain"

    def test_boundary_exactly_11(self):
        """N exactly 11 → Uncertain."""
        result = equation_8_1_groutability_ratio(0.11, 0.01)
        assert result["feasibility"] == "Uncertain"

    def test_zero_d15_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            equation_8_1_groutability_ratio(0, 0.015)

    def test_zero_d85_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            equation_8_1_groutability_ratio(0.5, 0)

    def test_result_has_all_keys(self):
        result = equation_8_1_groutability_ratio(0.5, 0.015)
        for key in ("groutability_ratio", "feasibility",
                    "d15_soil_mm", "d85_grout_mm", "description"):
            assert key in result


# ============================================================================
# Equation 11-1: LTDS
# ============================================================================

class TestEquation111:
    """Tests for equation_11_1_ltds()."""

    def test_typical_pet_geogrid(self):
        """T_ult=200 kN/m, RF_ID=1.3, RF_CR=1.8, RF_CBD=1.3 → LTDS≈66 kN/m."""
        result = equation_11_1_ltds(200.0, 1.3, 1.8, 1.3)
        expected = 200.0 / (1.3 * 1.8 * 1.3)
        assert abs(result["ltds_kn_m"] - expected) < 0.1

    def test_combined_rf_product(self):
        """Combined RF = RF_ID * RF_CR * RF_CBD * FS."""
        result = equation_11_1_ltds(100.0, 1.5, 2.0, 1.2, fs=1.0)
        assert abs(result["combined_reduction_factor"] - 3.6) < 0.01

    def test_fs_applied(self):
        """FS doubles the combined RF, halves the LTDS."""
        r1 = equation_11_1_ltds(100.0, 1.5, 2.0, 1.2, fs=1.0)
        r2 = equation_11_1_ltds(100.0, 1.5, 2.0, 1.2, fs=2.0)
        assert abs(r2["ltds_kn_m"] - r1["ltds_kn_m"] / 2.0) < 0.01

    def test_ltds_less_than_t_ult(self):
        """LTDS must always be less than T_ult."""
        result = equation_11_1_ltds(500.0, 1.2, 1.6, 1.1)
        assert result["ltds_kn_m"] < 500.0

    def test_zero_strength_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            equation_11_1_ltds(0, 1.3, 1.8, 1.3)

    def test_zero_rf_id_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            equation_11_1_ltds(200.0, 0, 1.8, 1.3)

    def test_zero_fs_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            equation_11_1_ltds(200.0, 1.3, 1.8, 1.3, fs=0)

    def test_result_has_all_keys(self):
        result = equation_11_1_ltds(200.0, 1.3, 1.8, 1.3)
        for key in ("ltds_kn_m", "combined_reduction_factor",
                    "t_ult_kn_m", "rf_id", "rf_cr", "rf_cbd", "fs"):
            assert key in result
