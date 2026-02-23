"""Tests for GEC-11 figure lookup functions."""

import pytest

from geotech_references.gec_11.figures import (
    figure_4_10_kr_ka_ratio,
)


# ============================================================================
# Figure 4-10: Kr/Ka vs Depth
# ============================================================================

class TestFigure410:
    """Tests for figure_4_10_kr_ka_ratio()."""

    # --- Geosynthetic (constant Kr/Ka = 1.0) ---

    def test_geosynthetic_surface(self):
        result = figure_4_10_kr_ka_ratio(0.0, "geosynthetic")
        assert result["kr_ka_ratio"] == pytest.approx(1.0)

    def test_geosynthetic_deep(self):
        result = figure_4_10_kr_ka_ratio(10.0, "geosynthetic")
        assert result["kr_ka_ratio"] == pytest.approx(1.0)

    def test_geogrid_alias(self):
        result = figure_4_10_kr_ka_ratio(3.0, "geogrid")
        assert result["kr_ka_ratio"] == pytest.approx(1.0)

    # --- Metal strip (1.7 at top, 1.2 at 6m, 1.2 below) ---

    def test_metal_strip_surface(self):
        result = figure_4_10_kr_ka_ratio(0.0, "metal_strip")
        assert result["kr_ka_ratio"] == pytest.approx(1.7)

    def test_metal_strip_at_6m(self):
        result = figure_4_10_kr_ka_ratio(6.0, "metal_strip")
        assert result["kr_ka_ratio"] == pytest.approx(1.2)

    def test_metal_strip_at_3m(self):
        """Midpoint: should be (1.7+1.2)/2 = 1.45."""
        result = figure_4_10_kr_ka_ratio(3.0, "metal_strip")
        assert result["kr_ka_ratio"] == pytest.approx(1.45, abs=0.01)

    def test_metal_strip_deep(self):
        result = figure_4_10_kr_ka_ratio(15.0, "metal_strip")
        assert result["kr_ka_ratio"] == pytest.approx(1.2)

    def test_strip_alias(self):
        result = figure_4_10_kr_ka_ratio(0.0, "strip")
        assert result["kr_ka_ratio"] == pytest.approx(1.7)

    # --- Metal bar mat (2.5 at top, 1.2 at 6m, 1.2 below) ---

    def test_bar_mat_surface(self):
        result = figure_4_10_kr_ka_ratio(0.0, "metal_bar_mat")
        assert result["kr_ka_ratio"] == pytest.approx(2.5)

    def test_bar_mat_at_6m(self):
        result = figure_4_10_kr_ka_ratio(6.0, "metal_bar_mat")
        assert result["kr_ka_ratio"] == pytest.approx(1.2)

    def test_bar_mat_at_3m(self):
        """Midpoint: should be (2.5+1.2)/2 = 1.85."""
        result = figure_4_10_kr_ka_ratio(3.0, "metal_bar_mat")
        assert result["kr_ka_ratio"] == pytest.approx(1.85, abs=0.01)

    def test_bar_mat_deep(self):
        result = figure_4_10_kr_ka_ratio(12.0, "metal_bar_mat")
        assert result["kr_ka_ratio"] == pytest.approx(1.2)

    def test_welded_wire_alias(self):
        result = figure_4_10_kr_ka_ratio(0.0, "welded_wire")
        assert result["kr_ka_ratio"] == pytest.approx(2.5)

    # --- General behavior ---

    def test_result_has_keys(self):
        result = figure_4_10_kr_ka_ratio(3.0)
        assert "depth_m" in result
        assert "kr_ka_ratio" in result
        assert "reinforcement_type" in result
        assert "description" in result
        assert "reference" in result

    def test_negative_depth_raises(self):
        with pytest.raises(ValueError, match="must be >= 0"):
            figure_4_10_kr_ka_ratio(-1.0)

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown reinforcement_type"):
            figure_4_10_kr_ka_ratio(3.0, "unknown_type")

    def test_strip_always_gte_geosynthetic(self):
        """Metal strips always have Kr/Ka >= geosynthetic Kr/Ka."""
        for depth in [0, 1, 3, 6, 10, 15]:
            strip = figure_4_10_kr_ka_ratio(depth, "metal_strip")
            geo = figure_4_10_kr_ka_ratio(depth, "geosynthetic")
            assert strip["kr_ka_ratio"] >= geo["kr_ka_ratio"]

    def test_bar_mat_gte_strip(self):
        """Bar mats always have Kr/Ka >= metal strips."""
        for depth in [0, 1, 3, 6, 10, 15]:
            bar = figure_4_10_kr_ka_ratio(depth, "metal_bar_mat")
            strip = figure_4_10_kr_ka_ratio(depth, "metal_strip")
            assert bar["kr_ka_ratio"] >= strip["kr_ka_ratio"]
