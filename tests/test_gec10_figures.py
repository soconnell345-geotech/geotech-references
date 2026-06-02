"""Tests for GEC-10 figure and equation lookup functions (FHWA-NHI-18-024)."""

import math
import pytest

from geotech_references.gec_10.figures import (
    figure_10_6_alpha_clay,
    su_uu_to_ciuc,
    su_uc_to_ciuc,
    equation_10_21_rock_socket_side,
    equation_10_22_caving_rock_side,
)

_PA = 101.325  # atmospheric pressure, kPa


# ============================================================================
# Figure 10-6: Alpha factor for cohesive side resistance (Chen et al. 2011)
# α = 0.30 + 0.17 / (su / pa)
# ============================================================================

class TestFigure106AlphaClay:

    def test_formula_su50(self):
        alpha = figure_10_6_alpha_clay(50.0)
        expected = 0.30 + 0.17 / (50.0 / _PA)
        assert abs(alpha - expected) < 1e-9

    def test_formula_su100(self):
        alpha = figure_10_6_alpha_clay(100.0)
        expected = 0.30 + 0.17 / (100.0 / _PA)
        assert abs(alpha - expected) < 1e-9

    def test_formula_su200(self):
        alpha = figure_10_6_alpha_clay(200.0)
        expected = 0.30 + 0.17 / (200.0 / _PA)
        assert abs(alpha - expected) < 1e-9

    def test_alpha_decreases_with_su(self):
        """Higher su → lower alpha."""
        assert figure_10_6_alpha_clay(50) > figure_10_6_alpha_clay(100)
        assert figure_10_6_alpha_clay(100) > figure_10_6_alpha_clay(200)

    def test_su50_value(self):
        """Check representative value: su=50 kPa → α ≈ 0.64."""
        alpha = figure_10_6_alpha_clay(50)
        assert abs(alpha - 0.644) < 0.002

    def test_su100_value(self):
        """su=100 kPa → α ≈ 0.47."""
        alpha = figure_10_6_alpha_clay(100)
        assert abs(alpha - 0.472) < 0.002

    def test_su200_value(self):
        """su=200 kPa → α ≈ 0.39."""
        alpha = figure_10_6_alpha_clay(200)
        assert abs(alpha - 0.386) < 0.002

    def test_su500_value(self):
        """su=500 kPa → α ≈ 0.33 (approaches 0.30 asymptote)."""
        alpha = figure_10_6_alpha_clay(500)
        assert abs(alpha - 0.334) < 0.002

    def test_asymptote_large_su(self):
        """Very high su → alpha approaches 0.30."""
        alpha = figure_10_6_alpha_clay(10000)
        assert abs(alpha - 0.30) < 0.002

    def test_zero_su_raises(self):
        with pytest.raises(ValueError):
            figure_10_6_alpha_clay(0)

    def test_negative_su_raises(self):
        with pytest.raises(ValueError):
            figure_10_6_alpha_clay(-50)


# ============================================================================
# Equations 10-16 / 10-17: su conversion (UU / UC → CIUC)
# ============================================================================

class TestSuUuToCiuc:
    """Equation 10-17: su_UU / su_CIUC = 0.911 + 0.499 * log10(su_UU / σ'v0)."""

    def test_manual_example(self):
        """Replicate the worked example in Section 10.3.5.2.

        su_UU = 2000 psf ≈ 95.76 kPa, σ'v0 = 3697 psf ≈ 177.06 kPa
        Expected su_CIUC ≈ 2571 psf ≈ 123.1 kPa.
        """
        su_uu = 2000 * 0.04788  # psf → kPa
        sigma_v0 = 3697 * 0.04788
        result = su_uu_to_ciuc(su_uu, sigma_v0)
        expected = 2571 * 0.04788  # ≈ 123.1 kPa
        assert abs(result - expected) < 1.0

    def test_ciuc_larger_than_uu(self):
        """For typical su/σ'v0 < 1, CIUC should be larger than UU."""
        result = su_uu_to_ciuc(50, 200)
        assert result > 50

    def test_zero_su_raises(self):
        with pytest.raises(ValueError):
            su_uu_to_ciuc(0, 100)

    def test_zero_sigma_raises(self):
        with pytest.raises(ValueError):
            su_uu_to_ciuc(50, 0)


class TestSuUcToCiuc:
    """Equation 10-16: su_UC / su_CIUC = 0.893 + 0.513 * log10(su_UC / σ'v0)."""

    def test_ciuc_larger_than_uc(self):
        """CIUC typically larger than UC (UC is conservative)."""
        result = su_uc_to_ciuc(50, 200)
        assert result > 50

    def test_formula_explicit(self):
        su_uc, sv0 = 100.0, 200.0
        expected = su_uc / (0.893 + 0.513 * math.log10(su_uc / sv0))
        assert abs(su_uc_to_ciuc(su_uc, sv0) - expected) < 1e-9

    def test_zero_su_raises(self):
        with pytest.raises(ValueError):
            su_uc_to_ciuc(0, 100)

    def test_zero_sigma_raises(self):
        with pytest.raises(ValueError):
            su_uc_to_ciuc(50, 0)


# ============================================================================
# Equation 10-21: Rock socket side resistance, normal conditions
# f_SN / pa = C * sqrt(qu / pa),  C = 1.0 default
# ============================================================================

class TestEquation1021RockSocketSide:

    def test_normal_1000kpa(self):
        """qu=1000 kPa, C=1.0: f_sn = pa * sqrt(1000/pa) ≈ 318.4 kPa."""
        result = equation_10_21_rock_socket_side(1000.0)
        expected = _PA * math.sqrt(1000.0 / _PA)
        assert abs(result["f_sn_kpa"] - expected) < 0.5

    def test_normal_condition_label(self):
        result = equation_10_21_rock_socket_side(1000.0, C=1.0)
        assert result["condition"] == "normal"

    def test_roughened_condition_label(self):
        result = equation_10_21_rock_socket_side(1000.0, C=1.9)
        assert result["condition"] == "artificially roughened"

    def test_higher_c_gives_higher_resistance(self):
        r1 = equation_10_21_rock_socket_side(5000.0, C=1.0)
        r2 = equation_10_21_rock_socket_side(5000.0, C=1.9)
        assert r2["f_sn_kpa"] > r1["f_sn_kpa"]

    def test_higher_qu_gives_higher_resistance(self):
        r1 = equation_10_21_rock_socket_side(500.0)
        r2 = equation_10_21_rock_socket_side(5000.0)
        assert r2["f_sn_kpa"] > r1["f_sn_kpa"]

    def test_result_keys(self):
        result = equation_10_21_rock_socket_side(2000.0)
        for key in ("C", "qu_kpa", "qu_mpa", "f_sn_kpa", "f_sn_mpa", "condition"):
            assert key in result

    def test_qu_mpa_conversion(self):
        result = equation_10_21_rock_socket_side(5000.0)
        assert abs(result["qu_mpa"] - 5.0) < 0.001

    def test_f_sn_mpa_consistent(self):
        result = equation_10_21_rock_socket_side(3000.0)
        assert abs(result["f_sn_kpa"] / 1000 - result["f_sn_mpa"]) < 0.0001

    def test_zero_qu_raises(self):
        with pytest.raises(ValueError, match="positive"):
            equation_10_21_rock_socket_side(0.0)

    def test_negative_c_raises(self):
        with pytest.raises(ValueError):
            equation_10_21_rock_socket_side(1000.0, C=-1.0)


# ============================================================================
# Equation 10-22 + Table 10-3: Rock socket side resistance, caving rock
# f_SN / pa = 0.65 * αE * sqrt(qu / pa)
# ============================================================================

class TestEquation1022CavingRockSide:

    def test_rqd100_closed_gives_max_alpha(self):
        """RQD=100%, closed joints → αE = 1.00."""
        result = equation_10_22_caving_rock_side(1000.0, 100, "closed")
        assert abs(result["alpha_E"] - 1.00) < 0.01

    def test_rqd100_open_gives_085(self):
        """RQD=100%, open joints → αE = 0.85."""
        result = equation_10_22_caving_rock_side(1000.0, 100, "open")
        assert abs(result["alpha_E"] - 0.85) < 0.01

    def test_rqd20_both_045(self):
        """RQD=20%: αE = 0.45 for both closed and open."""
        r1 = equation_10_22_caving_rock_side(1000.0, 20, "closed")
        r2 = equation_10_22_caving_rock_side(1000.0, 20, "open")
        assert abs(r1["alpha_E"] - 0.45) < 0.01
        assert abs(r2["alpha_E"] - 0.45) < 0.01

    def test_rqd70_closed_vs_open(self):
        """Closed joints stronger than open at RQD=70%."""
        rc = equation_10_22_caving_rock_side(1000.0, 70, "closed")
        ro = equation_10_22_caving_rock_side(1000.0, 70, "open")
        assert rc["alpha_E"] > ro["alpha_E"]

    def test_caving_lower_than_normal(self):
        """Caving equation should give lower resistance than normal (C=1.0) for αE<1."""
        normal = equation_10_21_rock_socket_side(1000.0, C=1.0)
        caving = equation_10_22_caving_rock_side(1000.0, 50, "closed")
        assert caving["f_sn_kpa"] < normal["f_sn_kpa"]

    def test_result_keys(self):
        result = equation_10_22_caving_rock_side(2000.0, 70, "closed")
        for key in ("alpha_E", "qu_kpa", "f_sn_kpa", "f_sn_mpa",
                    "rqd_pct", "joint_condition"):
            assert key in result

    def test_rqd_below_minimum_clamped(self):
        """RQD below table minimum (20%) should return the minimum αE value."""
        result = equation_10_22_caving_rock_side(1000.0, 10, "closed")
        assert abs(result["alpha_E"] - 0.45) < 0.01

    def test_zero_qu_raises(self):
        with pytest.raises(ValueError):
            equation_10_22_caving_rock_side(0.0, 70)

    def test_rqd_out_of_range_raises(self):
        with pytest.raises(ValueError, match="0"):
            equation_10_22_caving_rock_side(1000.0, 120)

    def test_invalid_joint_condition_raises(self):
        with pytest.raises(ValueError, match="joint_condition"):
            equation_10_22_caving_rock_side(1000.0, 70, "tight")
