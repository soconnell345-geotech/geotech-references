"""Tests for micropile figure lookup functions."""

import pytest

from geotech_references.micropile.figures import (
    figure_5_23_limiting_lateral_modulus,
)


# ============================================================================
# Figure 5-23: Limiting Lateral Modulus Values
# ============================================================================

class TestFigure523:
    """Tests for figure_5_23_limiting_lateral_modulus()."""

    def test_casing_n80(self):
        r = figure_5_23_limiting_lateral_modulus("5.5x0.36_n80")
        assert r["es_limit_kpa"] == 669
        assert "N-80" in r["description"]

    def test_casing_a519(self):
        r = figure_5_23_limiting_lateral_modulus("5.5_a519")
        assert r["es_limit_kpa"] == 186
        assert "A519" in r["description"]

    def test_bar_14(self):
        r = figure_5_23_limiting_lateral_modulus("#14")
        assert r["es_limit_kpa"] == 4207
        assert "#14" in r["description"]

    def test_bar_18(self):
        r = figure_5_23_limiting_lateral_modulus("#18")
        assert r["es_limit_kpa"] == 4207

    def test_hollow_bar(self):
        r = figure_5_23_limiting_lateral_modulus("73/53")
        assert r["es_limit_kpa"] == 2414

    def test_bars_higher_than_casings(self):
        """Reinforcing bars have higher limiting Es than casings."""
        bar = figure_5_23_limiting_lateral_modulus("#14")
        casing = figure_5_23_limiting_lateral_modulus("7x0.5_n80")
        assert bar["es_limit_kpa"] > casing["es_limit_kpa"]

    def test_n80_higher_than_a519(self):
        """N-80 casings have higher limiting Es than A519 (higher strength)."""
        n80 = figure_5_23_limiting_lateral_modulus("5.5x0.36_n80")
        a519 = figure_5_23_limiting_lateral_modulus("5.5_a519")
        assert n80["es_limit_kpa"] > a519["es_limit_kpa"]

    def test_all_returns_categories(self):
        r = figure_5_23_limiting_lateral_modulus("all")
        assert "casings" in r
        assert "bars" in r
        assert "hollow_bars" in r
        assert len(r["casings"]) >= 5
        assert len(r["bars"]) >= 4

    def test_empty_returns_all(self):
        r = figure_5_23_limiting_lateral_modulus("")
        assert "casings" in r

    def test_invalid_section(self):
        with pytest.raises(ValueError):
            figure_5_23_limiting_lateral_modulus("nonexistent_bar")

    def test_returns_float(self):
        r = figure_5_23_limiting_lateral_modulus("#10")
        assert isinstance(r["es_limit_kpa"], int)
