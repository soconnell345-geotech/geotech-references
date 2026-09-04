"""Tests for geotech_references.wood_handbook.moisture_relations (Chapter 4
moisture relations and physical properties)."""

import math

import pytest

from geotech_references.wood_handbook.moisture_relations import (
    table_4_1_green_moisture_content,
    max_moisture_content,
    sink_moisture_content,
    equilibrium_moisture_content,
    equilibrium_moisture_content_glass,
    relative_humidity_from_emc,
    table_4_3_shrinkage,
    shrinkage_at_moisture_content,
    convert_specific_gravity,
    specific_gravity_from_basic,
    estimate_total_shrinkage_from_basic_sg,
    density_from_specific_gravity,
    density_from_ovendry_density,
    estimate_total_shrinkage_from_ovendry_density,
    thermal_conductivity,
)


class TestTable41GreenMC:
    def test_douglas_fir_coast(self):
        row = table_4_1_green_moisture_content("Douglas-fir, coast")
        assert row["heartwood_mc_pct"] == 37
        assert row["sapwood_mc_pct"] == 115

    def test_unknown_species_raises(self):
        with pytest.raises(ValueError):
            table_4_1_green_moisture_content("not a species")


class TestMaxAndSinkMoistureContent:
    def test_max_moisture_content_anchor_low_sg(self):
        # Printed anchor: ~267% at Gb=0.30
        result = max_moisture_content(0.30)
        assert result["mc_max_pct"] == pytest.approx(267.0, rel=0.02)

    def test_max_moisture_content_anchor_high_sg(self):
        # Printed anchor: ~44% at Gb=0.90
        result = max_moisture_content(0.90)
        assert result["mc_max_pct"] == pytest.approx(44.0, rel=0.05)

    def test_sink_moisture_content(self):
        # MCsink = 100*(1-Gb)/Gb
        result = sink_moisture_content(0.50)
        assert result["mc_sink_pct"] == pytest.approx(100.0)

    def test_max_moisture_content_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            max_moisture_content(0.0)


class TestEquilibriumMoistureContent:
    def test_emc_table_4_2_anchor(self):
        # Table 4-2 printed row: 21.1 degC (70 degF), 40% RH -> 7.7% MC
        result = equilibrium_moisture_content(21.1, 0.40)
        assert result["emc_pct"] == pytest.approx(7.7, abs=0.15)

    def test_emc_increases_with_relative_humidity(self):
        low = equilibrium_moisture_content(21.1, 0.30)["emc_pct"]
        high = equilibrium_moisture_content(21.1, 0.80)["emc_pct"]
        assert high > low

    def test_emc_rejects_out_of_range_rh(self):
        with pytest.raises(ValueError):
            equilibrium_moisture_content(21.1, 1.0)

    def test_glass_equation_reasonable_range(self):
        # Cross-checked by hand against Table 4-2 (21.1 degC/65% RH -> 12.0%
        # from the Hailwood-Horrobin fit); the Glass et al. model is a
        # different fit, so only a nearby range is asserted here.
        result = equilibrium_moisture_content_glass(21.1, 0.65)
        assert 5.0 < result["emc_pct"] < 20.0

    def test_relative_humidity_from_emc_round_trip(self):
        temp_c, emc_target = 21.1, 12.0
        rh = relative_humidity_from_emc(temp_c, emc_target)["relative_humidity"]
        back = equilibrium_moisture_content_glass(temp_c, rh)["emc_pct"]
        assert back == pytest.approx(emc_target, rel=0.01)


class TestTable43Shrinkage:
    def test_douglas_fir_coast(self):
        row = table_4_3_shrinkage("douglas-fir, coast")
        assert row["radial_pct"] == 4.8
        assert row["tangential_pct"] == 7.6
        assert row["volumetric_pct"] == 12.4

    def test_unknown_species_raises(self):
        with pytest.raises(ValueError):
            table_4_3_shrinkage("not a species")


class TestShrinkageAndSpecificGravity:
    def test_shrinkage_zero_at_fsp(self):
        result = shrinkage_at_moisture_content(12.4, moisture_content_pct=30.0, mc_fs=30.0)
        assert result["shrinkage_pct"] == pytest.approx(0.0)

    def test_shrinkage_full_at_zero_mc(self):
        result = shrinkage_at_moisture_content(12.4, moisture_content_pct=0.0, mc_fs=30.0)
        assert result["shrinkage_pct"] == pytest.approx(12.4)

    def test_convert_specific_gravity_identity(self):
        result = convert_specific_gravity(0.50, sx_prime_pct=10.0, sx_double_prime_pct=10.0)
        assert result["gx_double_prime"] == pytest.approx(0.50)

    def test_specific_gravity_from_basic_eq_4_13(self):
        # White ash example (chapter docstring anchor): Gb=0.55, x=12% -> G12~0.605
        result = specific_gravity_from_basic(0.55, moisture_content_pct=12.0)
        assert result["equation"] == "4-13"
        assert result["gx"] == pytest.approx(0.603, abs=0.01)

    def test_specific_gravity_from_basic_with_explicit_s0(self):
        result = specific_gravity_from_basic(0.55, moisture_content_pct=0.0, volumetric_s0_pct=13.3)
        assert result["equation"] == "4-11"
        assert result["gx"] == pytest.approx(0.55 / (1 - 0.133), rel=1e-6)

    def test_estimate_total_shrinkage_from_basic_sg(self):
        result = estimate_total_shrinkage_from_basic_sg(0.50)
        assert result["s0_pct"] == pytest.approx(13.25)


class TestDensity:
    def test_density_from_specific_gravity_table_4_6a_anchor_mc12(self):
        # Table 4-6a exact anchor: MC=12%, Gx=0.60 -> 672 kg/m^3
        result = density_from_specific_gravity(0.60, moisture_content_pct=12.0)
        assert result["density_kg_m3"] == pytest.approx(672.0, rel=1e-6)

    def test_density_from_specific_gravity_table_4_6a_anchor_mc100(self):
        # Table 4-6a exact anchor: MC=100%, Gx=0.40 -> 800 kg/m^3
        result = density_from_specific_gravity(0.40, moisture_content_pct=100.0)
        assert result["density_kg_m3"] == pytest.approx(800.0, rel=1e-6)

    def test_density_from_ovendry_density_matches_eq_4_14_route(self):
        rho_0 = 500.0
        s0 = estimate_total_shrinkage_from_ovendry_density(rho_0)["s0_pct"]
        result = density_from_ovendry_density(rho_0, moisture_content_pct=0.0, s0_pct=s0)
        assert result["density_kg_m3"] == pytest.approx(rho_0, rel=1e-3)

    def test_estimate_total_shrinkage_from_ovendry_density_formula(self):
        # Eq 4-16: S0 = 26.5*rho_0 / (rho_w + 0.265*rho_0). This is the
        # ovendry-density-based estimator; it is NOT algebraically identical
        # to Eq 4-12 (S0=26.5*Gb) even when rho_0=1000*Gb -- the two are
        # independent printed approximations, not required to match.
        rho_0 = 450.0
        result = estimate_total_shrinkage_from_ovendry_density(rho_0)
        expected = 26.5 * rho_0 / (1000.0 + 0.265 * rho_0)
        assert result["s0_pct"] == pytest.approx(expected)


class TestThermalConductivity:
    def test_thermal_conductivity_positive(self):
        result = thermal_conductivity(0.45, moisture_content_pct=12.0)
        assert 0.05 < result["k_w_per_mK"] < 0.25

    def test_thermal_conductivity_increases_with_moisture(self):
        low = thermal_conductivity(0.45, moisture_content_pct=0.0)["k_w_per_mK"]
        high = thermal_conductivity(0.45, moisture_content_pct=20.0)["k_w_per_mK"]
        assert high > low
