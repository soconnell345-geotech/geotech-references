"""Tests for GEC-10 figure lookup functions."""

import pytest

from geotech_references.gec_10.figures import (
    figure_13_10_alpha_clay,
    figure_13_8_beta_sand,
    figure_13_18_nc_base_clay,
    figure_13_24_rock_socket_side,
)


# ============================================================================
# Figure 13-10: Alpha Factor for Clay
# ============================================================================

class TestFigure1310:
    """Tests for figure_13_10_alpha_clay()."""

    def test_low_su_returns_055(self):
        """su <= 50 kPa should give alpha ≈ 0.55."""
        assert abs(figure_13_10_alpha_clay(25) - 0.55) < 0.01
        assert abs(figure_13_10_alpha_clay(50) - 0.55) < 0.01

    def test_high_su_decreases(self):
        """Alpha decreases with increasing su."""
        alpha_100 = figure_13_10_alpha_clay(100)
        alpha_200 = figure_13_10_alpha_clay(200)
        assert alpha_100 > alpha_200

    def test_su_100(self):
        alpha = figure_13_10_alpha_clay(100)
        assert abs(alpha - 0.42) < 0.02

    def test_su_150(self):
        alpha = figure_13_10_alpha_clay(150)
        assert abs(alpha - 0.35) < 0.02

    def test_su_250(self):
        alpha = figure_13_10_alpha_clay(250)
        assert abs(alpha - 0.31) < 0.02

    def test_interpolation(self):
        """Intermediate values interpolated smoothly."""
        alpha_75 = figure_13_10_alpha_clay(75)
        assert 0.42 < alpha_75 < 0.55

    def test_below_range_raises(self):
        with pytest.raises(ValueError, match="below"):
            figure_13_10_alpha_clay(10)

    def test_above_range_raises(self):
        with pytest.raises(ValueError, match="exceeds"):
            figure_13_10_alpha_clay(300)


# ============================================================================
# Figure 13-8: Beta Factor vs Depth for Sand
# ============================================================================

class TestFigure138:
    """Tests for figure_13_8_beta_sand()."""

    def test_surface_mean(self):
        beta = figure_13_8_beta_sand(0, "mean")
        assert abs(beta - 1.20) < 0.05

    def test_10m_mean(self):
        beta = figure_13_8_beta_sand(10, "mean")
        assert abs(beta - 0.62) < 0.05

    def test_beta_decreases_with_depth(self):
        beta_5 = figure_13_8_beta_sand(5, "mean")
        beta_20 = figure_13_8_beta_sand(20, "mean")
        assert beta_5 > beta_20

    def test_upper_greater_than_mean(self):
        upper = figure_13_8_beta_sand(10, "upper")
        mean = figure_13_8_beta_sand(10, "mean")
        lower = figure_13_8_beta_sand(10, "lower")
        assert upper > mean > lower

    def test_lower_bound_10m(self):
        beta = figure_13_8_beta_sand(10, "lower")
        assert abs(beta - 0.40) < 0.05

    def test_upper_bound_10m(self):
        beta = figure_13_8_beta_sand(10, "upper")
        assert abs(beta - 0.90) < 0.05

    def test_negative_depth_raises(self):
        with pytest.raises(ValueError, match="outside"):
            figure_13_8_beta_sand(-1)

    def test_beyond_30m_raises(self):
        with pytest.raises(ValueError, match="outside"):
            figure_13_8_beta_sand(35)

    def test_unknown_bound_raises(self):
        with pytest.raises(ValueError, match="Unknown bound"):
            figure_13_8_beta_sand(10, "invalid")


# ============================================================================
# Figure 13-18: Nc* for Base in Clay
# ============================================================================

class TestFigure1318:
    """Tests for figure_13_18_nc_base_clay()."""

    def test_surface(self):
        nc = figure_13_18_nc_base_clay(0)
        assert abs(nc - 6.50) < 0.1

    def test_deep(self):
        nc = figure_13_18_nc_base_clay(5)
        assert abs(nc - 9.0) < 0.1

    def test_nc_increases_with_depth(self):
        nc_1 = figure_13_18_nc_base_clay(1)
        nc_3 = figure_13_18_nc_base_clay(3)
        assert nc_3 > nc_1

    def test_nc_4_db(self):
        nc = figure_13_18_nc_base_clay(4.0)
        assert abs(nc - 8.90) < 0.1

    def test_clamped_above_5(self):
        """D/B > 5 should return max Nc* = 9.0."""
        nc = figure_13_18_nc_base_clay(10)
        assert abs(nc - 9.0) < 0.01

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="must be >= 0"):
            figure_13_18_nc_base_clay(-1)


# ============================================================================
# Figure 13-24: Rock Socket Side Resistance
# ============================================================================

class TestFigure1324:
    """Tests for figure_13_24_rock_socket_side()."""

    def test_intermediate_1mpa(self):
        result = figure_13_24_rock_socket_side(1.0, "intermediate")
        assert abs(result["C"] - 0.30) < 0.01
        assert abs(result["fs_mpa"] - 0.30) < 0.01
        assert abs(result["fs_kpa"] - 300.0) < 1.0

    def test_smooth_lower_than_intermediate(self):
        smooth = figure_13_24_rock_socket_side(4.0, "smooth")
        inter = figure_13_24_rock_socket_side(4.0, "intermediate")
        assert smooth["fs_mpa"] < inter["fs_mpa"]

    def test_rough_higher_than_intermediate(self):
        rough = figure_13_24_rock_socket_side(4.0, "rough")
        inter = figure_13_24_rock_socket_side(4.0, "intermediate")
        assert rough["fs_mpa"] > inter["fs_mpa"]

    def test_smooth_4mpa(self):
        result = figure_13_24_rock_socket_side(4.0, "smooth")
        expected = 0.20 * (4.0 ** 0.5)
        assert abs(result["fs_mpa"] - expected) < 0.01

    def test_rough_10mpa(self):
        result = figure_13_24_rock_socket_side(10.0, "rough")
        expected = 0.45 * (10.0 ** 0.5)
        assert abs(result["fs_mpa"] - expected) < 0.01

    def test_zero_qu(self):
        result = figure_13_24_rock_socket_side(0.0, "intermediate")
        assert result["fs_mpa"] == 0.0

    def test_negative_qu_raises(self):
        with pytest.raises(ValueError, match="must be >= 0"):
            figure_13_24_rock_socket_side(-1.0)

    def test_unknown_roughness_raises(self):
        with pytest.raises(ValueError, match="Unknown roughness"):
            figure_13_24_rock_socket_side(1.0, "extreme")

    def test_result_has_all_keys(self):
        result = figure_13_24_rock_socket_side(5.0, "intermediate")
        assert "C" in result
        assert "qu_mpa" in result
        assert "fs_mpa" in result
        assert "fs_kpa" in result
        assert "roughness" in result
        assert "description" in result
