"""Tests for NOAA frost soil thermal property tables."""

import pytest

from geotech_references.noaa_frost.tables import (
    table_soil_thermal_conductivity,
    table_n_factor,
    table_soil_volumetric_heat_capacity,
    soil_thermal_properties,
)


# ============================================================================
# Soil Thermal Conductivity
# ============================================================================

class TestThermalConductivity:
    """Tests for table_soil_thermal_conductivity()."""

    def test_sand_frozen_at_breakpoint(self):
        """Sand frozen at 15% → 2.2 W/m-K (exact breakpoint)."""
        assert table_soil_thermal_conductivity("sand", 15, frozen=True) == 2.2

    def test_sand_unfrozen_at_breakpoint(self):
        """Sand unfrozen at 15% → 1.8 W/m-K."""
        assert table_soil_thermal_conductivity("sand", 15, frozen=False) == 1.8

    def test_clay_frozen_at_breakpoint(self):
        """Clay frozen at 20% → 1.7 W/m-K."""
        assert table_soil_thermal_conductivity("clay", 20, frozen=True) == 1.7

    def test_clay_unfrozen_at_breakpoint(self):
        """Clay unfrozen at 20% → 1.1 W/m-K."""
        assert table_soil_thermal_conductivity("clay", 20, frozen=False) == 1.1

    def test_silt_frozen(self):
        assert table_soil_thermal_conductivity("silt", 10, frozen=True) == 1.5

    def test_gravel_unfrozen(self):
        assert table_soil_thermal_conductivity("gravel", 10, frozen=False) == 1.8

    def test_peat_frozen(self):
        assert table_soil_thermal_conductivity("peat", 60, frozen=True) == 0.9

    def test_interpolation(self):
        """Sand frozen at 12.5% should interpolate between 10% and 15%."""
        k = table_soil_thermal_conductivity("sand", 12.5, frozen=True)
        assert 2.0 < k < 2.2
        assert k == pytest.approx(2.1)

    def test_frozen_higher_than_unfrozen(self):
        """Ice has higher conductivity than water → frozen > unfrozen."""
        k_f = table_soil_thermal_conductivity("sand", 15, frozen=True)
        k_u = table_soil_thermal_conductivity("sand", 15, frozen=False)
        assert k_f > k_u

    def test_clamped_below_range(self):
        """Moisture below table minimum clamps to first value."""
        k = table_soil_thermal_conductivity("sand", 1, frozen=True)
        assert k == table_soil_thermal_conductivity("sand", 5, frozen=True)

    def test_clamped_above_range(self):
        """Moisture above table maximum clamps to last value."""
        k = table_soil_thermal_conductivity("sand", 50, frozen=True)
        assert k == table_soil_thermal_conductivity("sand", 30, frozen=True)

    def test_case_insensitive(self):
        k = table_soil_thermal_conductivity("SAND", 15, frozen=True)
        assert k == 2.2

    def test_negative_moisture_raises(self):
        with pytest.raises(ValueError):
            table_soil_thermal_conductivity("sand", -5)

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError):
            table_soil_thermal_conductivity("bedrock", 10)


# ============================================================================
# Surface n-factor
# ============================================================================

class TestNFactor:
    """Tests for table_n_factor()."""

    def test_snow_covered(self):
        assert table_n_factor("snow_covered") == 0.20

    def test_turf(self):
        assert table_n_factor("turf") == 0.40

    def test_gravel_surface(self):
        assert table_n_factor("gravel_surface") == 0.60

    def test_bare_soil(self):
        assert table_n_factor("bare_soil") == 0.70

    def test_asphalt(self):
        assert table_n_factor("asphalt") == 0.75

    def test_concrete(self):
        assert table_n_factor("concrete") == 0.80

    def test_sand_gravel_dry(self):
        assert table_n_factor("sand_gravel_dry") == 0.90

    def test_exposed_rock(self):
        assert table_n_factor("exposed_rock") == 1.00

    def test_case_insensitive(self):
        assert table_n_factor("ASPHALT") == 0.75

    def test_partial_match_snow(self):
        """'snow' should partial-match 'snow_covered'."""
        assert table_n_factor("snow") == 0.20

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_n_factor("water")


# ============================================================================
# Volumetric Heat Capacity
# ============================================================================

class TestVolumetricHeatCapacity:
    """Tests for table_soil_volumetric_heat_capacity()."""

    def test_sand_frozen_at_breakpoint(self):
        """Sand frozen at 10% → 1.6 MJ/m3-K."""
        assert table_soil_volumetric_heat_capacity("sand", 10, frozen=True) == 1.6

    def test_sand_unfrozen_at_breakpoint(self):
        """Sand unfrozen at 10% → 1.9 MJ/m3-K."""
        assert table_soil_volumetric_heat_capacity("sand", 10, frozen=False) == 1.9

    def test_clay_frozen(self):
        assert table_soil_volumetric_heat_capacity("clay", 20, frozen=True) == 1.6

    def test_clay_unfrozen(self):
        assert table_soil_volumetric_heat_capacity("clay", 20, frozen=False) == 2.0

    def test_silt_frozen(self):
        assert table_soil_volumetric_heat_capacity("silt", 15, frozen=True) == 1.6

    def test_peat_unfrozen(self):
        assert table_soil_volumetric_heat_capacity("peat", 60, frozen=False) == 2.5

    def test_interpolation(self):
        """Sand frozen at 7.5% interpolates between 5% and 10%."""
        c = table_soil_volumetric_heat_capacity("sand", 7.5, frozen=True)
        assert 1.4 < c < 1.6
        assert c == pytest.approx(1.5)

    def test_unfrozen_higher_than_frozen(self):
        """Water has higher heat capacity than ice → unfrozen > frozen."""
        c_f = table_soil_volumetric_heat_capacity("sand", 15, frozen=True)
        c_u = table_soil_volumetric_heat_capacity("sand", 15, frozen=False)
        assert c_u > c_f

    def test_negative_moisture_raises(self):
        with pytest.raises(ValueError):
            table_soil_volumetric_heat_capacity("sand", -5)

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError):
            table_soil_volumetric_heat_capacity("limestone", 10)


# ============================================================================
# Combined Thermal Properties
# ============================================================================

class TestSoilThermalProperties:
    """Tests for soil_thermal_properties()."""

    def test_sand_15pct(self):
        r = soil_thermal_properties("sand", 15)
        assert r["k_frozen_W_mK"] == 2.2
        assert r["k_unfrozen_W_mK"] == 1.8
        assert r["k_avg_W_mK"] == pytest.approx(2.0)

    def test_clay_20pct(self):
        r = soil_thermal_properties("clay", 20)
        assert r["k_frozen_W_mK"] == 1.7
        assert r["k_unfrozen_W_mK"] == 1.1
        assert r["k_avg_W_mK"] == pytest.approx(1.4)

    def test_return_keys(self):
        r = soil_thermal_properties("silt", 20)
        expected = {"soil_type", "moisture_pct",
                    "k_frozen_W_mK", "k_unfrozen_W_mK", "k_avg_W_mK",
                    "C_frozen_MJ_m3K", "C_unfrozen_MJ_m3K"}
        assert set(r.keys()) == expected

    def test_k_avg_is_mean(self):
        """k_avg should be (k_frozen + k_unfrozen) / 2."""
        r = soil_thermal_properties("gravel", 10)
        assert r["k_avg_W_mK"] == pytest.approx(
            (r["k_frozen_W_mK"] + r["k_unfrozen_W_mK"]) / 2.0
        )

    def test_heat_capacity_included(self):
        r = soil_thermal_properties("sand", 15)
        assert r["C_frozen_MJ_m3K"] > 0
        assert r["C_unfrozen_MJ_m3K"] > 0

    def test_case_insensitive(self):
        r = soil_thermal_properties("CLAY", 20)
        assert r["soil_type"] == "clay"

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError):
            soil_thermal_properties("granite", 10)

    def test_negative_moisture_raises(self):
        with pytest.raises(ValueError):
            soil_thermal_properties("sand", -5)
