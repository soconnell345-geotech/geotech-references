"""Tests for NOAA frost depth equations."""

import math

import pytest

from geotech_references.noaa_frost.equations import (
    stefan_frost_depth_m,
    modified_berggren_frost_depth_m,
    berggren_lambda,
    soil_latent_heat_J_per_m3,
    frost_depth_simplified_m,
)


# ============================================================================
# Stefan Frost Depth
# ============================================================================

class TestStefanFrostDepth:
    """Tests for stefan_frost_depth_m()."""

    def test_known_computation(self):
        """d = sqrt(2 * 2.0 * 500 * 86400 / 1e8) = sqrt(1.728) = 1.3145 m."""
        d = stefan_frost_depth_m(500, 2.0, 1e8)
        expected = math.sqrt(2.0 * 2.0 * 500 * 86400 / 1e8)
        assert d == pytest.approx(expected, rel=1e-6)

    def test_higher_fi_deeper(self):
        """More degree-days → deeper frost."""
        d1 = stefan_frost_depth_m(200, 1.5, 1e8)
        d2 = stefan_frost_depth_m(800, 1.5, 1e8)
        assert d2 > d1

    def test_higher_conductivity_deeper(self):
        """Higher frozen k → deeper frost penetration."""
        d1 = stefan_frost_depth_m(500, 1.0, 1e8)
        d2 = stefan_frost_depth_m(500, 3.0, 1e8)
        assert d2 > d1

    def test_higher_latent_heat_shallower(self):
        """Higher L → shallower frost (more energy to freeze)."""
        d1 = stefan_frost_depth_m(500, 2.0, 0.5e8)
        d2 = stefan_frost_depth_m(500, 2.0, 2.0e8)
        assert d1 > d2

    def test_proportional_to_sqrt_fi(self):
        """Depth scales as sqrt(FI)."""
        d1 = stefan_frost_depth_m(100, 2.0, 1e8)
        d4 = stefan_frost_depth_m(400, 2.0, 1e8)
        assert d4 == pytest.approx(2.0 * d1, rel=1e-6)

    def test_zero_fi_raises(self):
        with pytest.raises(ValueError):
            stefan_frost_depth_m(0, 2.0, 1e8)

    def test_negative_fi_raises(self):
        with pytest.raises(ValueError):
            stefan_frost_depth_m(-100, 2.0, 1e8)

    def test_zero_k_raises(self):
        with pytest.raises(ValueError):
            stefan_frost_depth_m(500, 0, 1e8)

    def test_zero_L_raises(self):
        with pytest.raises(ValueError):
            stefan_frost_depth_m(500, 2.0, 0)


# ============================================================================
# Modified Berggren Frost Depth
# ============================================================================

class TestModifiedBerggrenFrostDepth:
    """Tests for modified_berggren_frost_depth_m()."""

    def test_known_computation(self):
        """d = 0.85 * sqrt(2 * 1.5 * 0.7 * 500 * 86400 / 1e8)."""
        d = modified_berggren_frost_depth_m(500, 1.5, 0.7, 1e8, 0.85)
        expected = 0.85 * math.sqrt(2.0 * 1.5 * 0.7 * 500 * 86400 / 1e8)
        assert d == pytest.approx(expected, rel=1e-6)

    def test_lambda_1_equals_scaled_stefan(self):
        """With lambda=1.0, should equal stefan * sqrt(n_factor) * k_ratio."""
        d = modified_berggren_frost_depth_m(500, 2.0, 1.0, 1e8, 1.0)
        d_stefan = stefan_frost_depth_m(500, 2.0, 1e8)
        assert d == pytest.approx(d_stefan, rel=1e-6)

    def test_lower_lambda_shallower(self):
        """Lower lambda → shallower frost depth."""
        d1 = modified_berggren_frost_depth_m(500, 1.5, 0.7, 1e8, 0.90)
        d2 = modified_berggren_frost_depth_m(500, 1.5, 0.7, 1e8, 0.50)
        assert d1 > d2

    def test_lower_n_factor_shallower(self):
        """Lower n-factor (more insulation) → shallower frost."""
        d1 = modified_berggren_frost_depth_m(500, 1.5, 0.9, 1e8, 0.85)
        d2 = modified_berggren_frost_depth_m(500, 1.5, 0.3, 1e8, 0.85)
        assert d1 > d2

    def test_zero_fi_raises(self):
        with pytest.raises(ValueError):
            modified_berggren_frost_depth_m(0, 1.5, 0.7, 1e8, 0.85)

    def test_zero_k_raises(self):
        with pytest.raises(ValueError):
            modified_berggren_frost_depth_m(500, 0, 0.7, 1e8, 0.85)

    def test_n_factor_too_high_raises(self):
        with pytest.raises(ValueError):
            modified_berggren_frost_depth_m(500, 1.5, 1.5, 1e8, 0.85)

    def test_n_factor_zero_raises(self):
        with pytest.raises(ValueError):
            modified_berggren_frost_depth_m(500, 1.5, 0, 1e8, 0.85)

    def test_lambda_too_high_raises(self):
        with pytest.raises(ValueError):
            modified_berggren_frost_depth_m(500, 1.5, 0.7, 1e8, 1.5)

    def test_lambda_zero_raises(self):
        with pytest.raises(ValueError):
            modified_berggren_frost_depth_m(500, 1.5, 0.7, 1e8, 0)


# ============================================================================
# Berggren Lambda
# ============================================================================

class TestBerggrenLambda:
    """Tests for berggren_lambda()."""

    def test_mu_zero_gives_one(self):
        """mu=0 means soil at freezing, lambda=1.0."""
        assert berggren_lambda(0, 0.5) == 1.0

    def test_mu_zero_any_alpha(self):
        """mu=0 → lambda=1.0 regardless of alpha."""
        assert berggren_lambda(0, 0) == 1.0
        assert berggren_lambda(0, 2.0) == 1.0

    def test_positive_mu_less_than_one(self):
        """Any mu > 0 should give lambda < 1.0."""
        assert berggren_lambda(0.5, 0.3) < 1.0

    def test_higher_mu_lower_lambda(self):
        """Higher mu → more initial heat → lower lambda."""
        lam1 = berggren_lambda(0.2, 0.3)
        lam2 = berggren_lambda(1.0, 0.3)
        assert lam1 > lam2

    def test_known_value(self):
        """lambda = 1/sqrt(1 + 0.5*(1 + 0.5*0.3*0.5)) = 1/sqrt(1.5375)."""
        lam = berggren_lambda(0.5, 0.3)
        expected = 1.0 / math.sqrt(1.0 + 0.5 * (1.0 + 0.5 * 0.3 * 0.5))
        assert lam == pytest.approx(expected, rel=1e-6)

    def test_negative_mu_raises(self):
        with pytest.raises(ValueError):
            berggren_lambda(-0.1, 0.3)

    def test_negative_alpha_raises(self):
        with pytest.raises(ValueError):
            berggren_lambda(0.5, -0.1)


# ============================================================================
# Soil Latent Heat
# ============================================================================

class TestSoilLatentHeat:
    """Tests for soil_latent_heat_J_per_m3()."""

    def test_known_computation(self):
        """L = 1600 * 0.20 * 334000 = 106,880,000 J/m3."""
        L = soil_latent_heat_J_per_m3(1600, 20)
        assert L == pytest.approx(1600 * 0.20 * 334000)

    def test_higher_density_higher_L(self):
        L1 = soil_latent_heat_J_per_m3(1200, 15)
        L2 = soil_latent_heat_J_per_m3(1800, 15)
        assert L2 > L1

    def test_higher_moisture_higher_L(self):
        L1 = soil_latent_heat_J_per_m3(1500, 10)
        L2 = soil_latent_heat_J_per_m3(1500, 30)
        assert L2 > L1

    def test_zero_moisture_gives_zero(self):
        """Dry soil has no latent heat."""
        assert soil_latent_heat_J_per_m3(1500, 0) == 0.0

    def test_zero_density_raises(self):
        with pytest.raises(ValueError):
            soil_latent_heat_J_per_m3(0, 20)

    def test_negative_density_raises(self):
        with pytest.raises(ValueError):
            soil_latent_heat_J_per_m3(-100, 20)

    def test_negative_moisture_raises(self):
        with pytest.raises(ValueError):
            soil_latent_heat_J_per_m3(1500, -5)


# ============================================================================
# Simplified Frost Depth
# ============================================================================

class TestFrostDepthSimplified:
    """Tests for frost_depth_simplified_m()."""

    def test_sand(self):
        r = frost_depth_simplified_m(500, "sand")
        assert r["soil_type"] == "sand"
        assert r["frost_depth_m"] > 0

    def test_clay(self):
        r = frost_depth_simplified_m(500, "clay")
        assert r["soil_type"] == "clay"
        assert r["frost_depth_m"] > 0

    def test_silt(self):
        r = frost_depth_simplified_m(500, "silt")
        assert r["frost_depth_m"] > 0

    def test_gravel(self):
        r = frost_depth_simplified_m(500, "gravel")
        assert r["frost_depth_m"] > 0

    def test_peat(self):
        r = frost_depth_simplified_m(500, "peat")
        assert r["frost_depth_m"] > 0

    def test_higher_fi_deeper(self):
        r1 = frost_depth_simplified_m(200, "sand")
        r2 = frost_depth_simplified_m(800, "sand")
        assert r2["frost_depth_m"] > r1["frost_depth_m"]

    def test_return_keys(self):
        r = frost_depth_simplified_m(500, "sand")
        expected = {"frost_depth_m", "soil_type", "description",
                    "dry_density_kg_m3", "moisture_pct",
                    "k_frozen_W_mK", "latent_heat_J_m3"}
        assert set(r.keys()) == expected

    def test_case_insensitive(self):
        r = frost_depth_simplified_m(500, "SAND")
        assert r["soil_type"] == "sand"

    def test_zero_fi_raises(self):
        with pytest.raises(ValueError):
            frost_depth_simplified_m(0, "sand")

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError):
            frost_depth_simplified_m(500, "bedrock")
