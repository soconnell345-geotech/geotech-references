"""Tests for geotech_references.wood_handbook.structural_stability
(Chapter 9 Stability Equations)."""

import math

import pytest

from geotech_references.wood_handbook.structural_stability import (
    euler_critical_stress,
    radius_of_gyration,
    ylinen_critical_stress_fourth_power,
    ylinen_strain,
    ylinen_buckling_stress,
    built_up_column_capacity,
    flange_instability_stress,
    critical_ponding_spacing,
    lateral_torsional_buckling_stress,
    table_9_2_effective_length,
    slenderness_factor,
    deck_shear_stiffness_parameter,
    elastic_buckling_stress_edgewise_flatwise,
    elastic_buckling_stress_edgewise_bending,
    moment_magnification_edgewise,
    moment_magnification_flatwise,
    biaxial_beam_column_interaction,
)


class TestAxialCompression:
    def test_euler_formula(self):
        r = radius_of_gyration("rectangular", b=0.1)["r"]
        result = euler_critical_stress(10e9, 3.0, r)
        assert result["fcr"] == pytest.approx(math.pi**2 * 10e9 / (3.0 / r) ** 2)

    def test_radius_of_gyration_rectangular(self):
        result = radius_of_gyration("rectangular", b=0.1)
        assert result["r"] == pytest.approx(0.1 / math.sqrt(12.0))

    def test_radius_of_gyration_circular(self):
        result = radius_of_gyration("circular", d=0.2)
        assert result["r"] == pytest.approx(0.05)

    def test_radius_of_gyration_general(self):
        result = radius_of_gyration("general", moment_of_inertia=8.0, area=2.0)
        assert result["r"] == pytest.approx(2.0)

    def test_euler_stress_decreases_with_slenderness(self):
        low_slender = euler_critical_stress(10e9, 1.0, 0.05)["fcr"]
        high_slender = euler_critical_stress(10e9, 5.0, 0.05)["fcr"]
        assert high_slender < low_slender

    def test_ylinen_c_0957_close_to_fourth_power(self):
        # Printed text: Eq 9-29 agrees closely with the FPL fourth-power
        # formula (Eq 9-27) if c=0.957.
        fc, e_l = 30e6, 10e9
        r = radius_of_gyration("rectangular", b=0.1)["r"]
        length = 2.0
        fourth_power = ylinen_critical_stress_fourth_power(fc, length, r, e_l)["fcr"]
        fe = euler_critical_stress(e_l, length, r)["fcr"]
        ylinen = ylinen_buckling_stress(fc, fe, c=0.957)["fcr"]
        # "Closely" per the printed text means the two curves track each
        # other in Fig. 9-18, not that they coincide exactly at every L/r;
        # a generous tolerance is used here rather than pinning to a tight
        # numeric match not claimed by the source.
        assert ylinen == pytest.approx(fourth_power, rel=0.10)

    def test_ylinen_strain_positive_below_fc(self):
        result = ylinen_strain(fc=30e6, stress=15e6, modulus_of_elasticity=10e9, c=0.8)
        assert result["strain"] > 0

    def test_built_up_column_reduced_by_kf(self):
        fc, fe = 30e6, 20e6
        full = ylinen_buckling_stress(fc, fe, c=0.8)["fcr"]
        built_up = built_up_column_capacity(fc, fe, c=0.8, k_f=0.6)["fcr"]
        assert built_up == pytest.approx(0.6 * full)

    def test_flange_instability_formula(self):
        result = flange_instability_stress(10e9, flange_thickness=0.02, flange_width=0.1)
        assert result["fcr"] == pytest.approx(0.044 * 10e9 * 0.02**2 / 0.1**2)


class TestPondingAndLateralTorsionalBuckling:
    def test_critical_ponding_spacing_fixed_gt_simple(self):
        simple = critical_ponding_spacing(10e9, 5e-5, 4.0, end_condition="simple")["s_cr"]
        fixed = critical_ponding_spacing(10e9, 5e-5, 4.0, end_condition="fixed")["s_cr"]
        assert fixed > simple

    def test_lateral_torsional_buckling_formula(self):
        result = lateral_torsional_buckling_stress(10e9, alpha=20.0)
        assert result["fb_cr"] == pytest.approx(math.pi**2 * 10e9 / 20.0**2)

    def test_table_9_2_equal_end_moments_is_length(self):
        row = table_9_2_effective_length("simple_support", "equal_end_moments", length=6.0, depth=0.3)
        assert row["le"] == pytest.approx(6.0)

    def test_table_9_2_concentrated_center(self):
        row = table_9_2_effective_length("simple_support", "concentrated_center", length=6.0, depth=0.3)
        expected = 0.742 * 6.0 / (1.0 - 2.0 * 0.3 / 6.0)
        assert row["le"] == pytest.approx(expected)

    def test_table_9_2_bad_combo_raises(self):
        with pytest.raises(ValueError):
            table_9_2_effective_length("simple_support", "concentrated_end", length=6.0, depth=0.3)

    def test_slenderness_factor_formula(self):
        result = slenderness_factor(ei_y=5e5, gj=2e5, le=6.0, h=0.3, b=0.1)
        expected = math.sqrt(2.0 * math.pi) * (5e5 / 2e5) ** 0.25 * math.sqrt(6.0 * 0.3) / 0.1
        assert result["alpha"] == pytest.approx(expected)

    def test_deck_shear_stiffness_parameter_formula(self):
        result = deck_shear_stiffness_parameter(beam_spacing=0.6, deck_shear_rigidity=1e6, length=6.0, ei_y=5e5)
        assert result["tau"] == pytest.approx(0.6 * 1e6 * 6.0**2 / 5e5)


class TestInteractionOfBucklingModes:
    def test_elastic_buckling_stress_edgewise_flatwise(self):
        result = elastic_buckling_stress_edgewise_flatwise(10e9, le=3.0, d=0.3)
        assert result["f_double_prime"] == pytest.approx(0.822 * 10e9 / (3.0 / 0.3) ** 2)

    def test_elastic_buckling_stress_edgewise_bending(self):
        result = elastic_buckling_stress_edgewise_bending(10e9, le=3.0, d1=0.3, d2=0.05)
        assert result["fb1_double_prime"] == pytest.approx(1.44 * 10e9 / 3.0 * 0.05 / 0.3)

    def test_moment_magnification_edgewise_no_load_is_one(self):
        result = moment_magnification_edgewise(fc=0.0, fc1_double_prime=1e7, beam_spacing=0.0, s_cr=4.0)
        assert result["theta_c1"] == pytest.approx(1.0)

    def test_moment_magnification_flatwise_no_load_is_one(self):
        result = moment_magnification_flatwise(fc=0.0, fc2_double_prime=1e7, fb1=0.0, e1_over_d1=0.0, fb1_double_prime=1e7)
        assert result["theta_c2"] == pytest.approx(1.0)

    def test_biaxial_interaction_axial_only(self):
        # With no bending, the interaction reduces to (fc/Fc')^2
        result = biaxial_beam_column_interaction(
            fc=1e6, fc_prime=2e6, fb1=0.0, e1_over_d1=0.0, theta_c1=1.0, fb1_prime=1e7,
            fb2=0.0, e2_over_d2=0.0, theta_c2=1.0, fb2_allow=1e7,
        )
        assert result["interaction_value"] == pytest.approx((1e6 / 2e6) ** 2)
        assert result["adequate"] is True

    def test_biaxial_interaction_exceeds_capacity(self):
        result = biaxial_beam_column_interaction(
            fc=1.9e6, fc_prime=2e6, fb1=9e6, e1_over_d1=0.0, theta_c1=1.0, fb1_prime=1e7,
            fb2=9e6, e2_over_d2=0.0, theta_c2=1.0, fb2_allow=1e7,
        )
        assert result["adequate"] is False
