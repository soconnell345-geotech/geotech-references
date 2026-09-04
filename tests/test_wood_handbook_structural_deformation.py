"""Tests for geotech_references.wood_handbook.structural_deformation
(Chapter 9 Deformation Equations)."""

import math

import pytest

from geotech_references.wood_handbook.structural_deformation import (
    axial_deformation,
    section_moment_of_inertia,
    section_modified_shear_area,
    table_9_1_kb_ks,
    straight_beam_deflection,
    tapered_beam_shear_deflection,
    ponding_deflection_amplification,
    combined_bending_axial_deflection,
    eccentric_axial_bending_deflection,
    angle_of_twist,
    torsional_constant_circular,
    torsional_constant_rectangular,
    _phi_rectangular_torsion,
)


class TestAxialDeformation:
    def test_formula(self):
        result = axial_deformation(axial_force=10000.0, length=3.0, area=0.01, modulus_of_elasticity=10e9)
        assert result["deformation"] == pytest.approx(10000.0 * 3.0 / (0.01 * 10e9))


class TestSectionProperties:
    def test_rectangular_moment_of_inertia(self):
        result = section_moment_of_inertia("rectangular", 0.1, 0.2)
        assert result["i"] == pytest.approx(0.1 * 0.2**3 / 12.0)

    def test_circular_moment_of_inertia(self):
        result = section_moment_of_inertia("circular", 0.2)
        assert result["i"] == pytest.approx(math.pi * 0.2**4 / 64.0)

    def test_rectangular_requires_h(self):
        with pytest.raises(ValueError):
            section_moment_of_inertia("rectangular", 0.1)

    def test_modified_shear_area_rectangular(self):
        result = section_modified_shear_area("rectangular", 0.1, 0.2)
        assert result["a_prime"] == pytest.approx((5.0 / 6.0) * 0.1 * 0.2)

    def test_modified_shear_area_circular(self):
        result = section_modified_shear_area("circular", 0.2)
        assert result["a_prime"] == pytest.approx((9.0 / 40.0) * math.pi * 0.2**2)


class TestTable91AndBeamDeflection:
    def test_udl_simply_supported(self):
        row = table_9_1_kb_ks("uniformly_distributed", "simply_supported")
        assert row["kb"] == pytest.approx(5.0 / 384)
        assert row["ks"] == pytest.approx(1.0 / 8)

    def test_cantilever_concentrated_free_end(self):
        row = table_9_1_kb_ks("concentrated_free_end", "cantilever")
        assert row["kb"] == pytest.approx(1.0 / 3)
        assert row["ks"] == 1.0

    def test_unknown_combo_raises(self):
        with pytest.raises(ValueError):
            table_9_1_kb_ks("triangular", "simply_supported")

    def test_straight_beam_deflection_sums_bending_and_shear(self):
        i = section_moment_of_inertia("rectangular", 0.1, 0.3)["i"]
        a_prime = section_modified_shear_area("rectangular", 0.1, 0.3)["a_prime"]
        result = straight_beam_deflection(
            kb=5.0 / 384, ks=1.0 / 8, w_total=5000.0, length=4.0,
            moment_of_inertia=i, modified_area=a_prime,
            modulus_of_elasticity=10e9, shear_modulus=0.6e9,
        )
        assert result["deflection_total"] == pytest.approx(
            result["deflection_bending"] + result["deflection_shear"]
        )
        assert result["deflection_total"] > 0


class TestTaperedBeamShearDeflection:
    def test_uniform_load_formula(self):
        result = tapered_beam_shear_deflection(1000.0, 4.0, 0.6e9, 0.1, 0.2, loading="uniform")
        expected = 3.0 * 1000.0 * 4.0 / (20.0 * 0.6e9 * 0.1 * 0.2)
        assert result["shear_deflection"] == pytest.approx(expected)

    def test_concentrated_midspan_formula(self):
        result = tapered_beam_shear_deflection(1000.0, 4.0, 0.6e9, 0.1, 0.2, loading="concentrated_midspan")
        expected = 3.0 * 1000.0 * 4.0 / (10.0 * 0.6e9 * 0.1 * 0.2)
        assert result["shear_deflection"] == pytest.approx(expected)

    def test_bad_loading_raises(self):
        with pytest.raises(ValueError):
            tapered_beam_shear_deflection(1000.0, 4.0, 0.6e9, 0.1, 0.2, loading="point_end")


class TestPondingAndCombinedLoad:
    def test_ponding_amplification_greater_than_one(self):
        result = ponding_deflection_amplification(delta_0=0.01, beam_spacing=1.0, critical_spacing=4.0)
        assert result["delta_total"] == pytest.approx(0.01 / (1.0 - 1.0 / 4.0))

    def test_combined_deflection_compression_amplifies(self):
        result = combined_bending_axial_deflection(delta_0=0.01, axial_load=1000.0, p_critical=4000.0, is_tension=False)
        assert result["delta"] > 0.01

    def test_combined_deflection_tension_reduces(self):
        result = combined_bending_axial_deflection(delta_0=0.01, axial_load=1000.0, p_critical=4000.0, is_tension=True)
        assert result["delta"] < 0.01

    def test_eccentric_deflection_zero_at_zero_load(self):
        result = eccentric_axial_bending_deflection(eccentricity=0.02, axial_load=0.0, p_critical=4000.0, is_tension=False)
        assert result["induced_bending_deflection"] == pytest.approx(0.0)


class TestTorsion:
    def test_angle_of_twist_formula(self):
        result = angle_of_twist(torque=500.0, length=2.0, shear_modulus=0.6e9, torsional_constant=1e-6)
        assert result["theta_rad"] == pytest.approx(500.0 * 2.0 / (0.6e9 * 1e-6))

    def test_torsional_constant_circular(self):
        result = torsional_constant_circular(0.2)
        assert result["k"] == pytest.approx(math.pi * 0.2**4 / 32.0)

    def test_phi_endpoints_match_figure_9_9(self):
        # Figure 9-9 printed endpoints: phi=3.0 at b/h=0, phi~7 at b/h=1.0
        assert _phi_rectangular_torsion(0.0) == pytest.approx(3.0)
        assert _phi_rectangular_torsion(1.0) == pytest.approx(7.09, rel=0.02)

    def test_torsional_constant_rectangular_square_matches_circular_scale(self):
        result = torsional_constant_rectangular(h=0.1, b=0.1)
        assert result["phi"] == pytest.approx(7.09, rel=0.02)
        assert result["k"] == pytest.approx(0.1 * 0.1**3 / result["phi"])

    def test_torsional_constant_rectangular_requires_b_le_h(self):
        with pytest.raises(ValueError):
            torsional_constant_rectangular(h=0.1, b=0.2)
