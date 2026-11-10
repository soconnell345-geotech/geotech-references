"""Tests for geotech_references.wood_handbook.structural_stress (Chapter 9
Stress Equations)."""

import math

import pytest

from geotech_references.wood_handbook.structural_stress import (
    axial_stress,
    section_modulus,
    bending_stress,
    beam_shear_stress,
    tapered_beam_stresses,
    tapered_beam_interaction,
    size_effect_ratio_two_point_vs_concentrated,
    size_effect_midspan_reference,
    size_effect_ratio_uniform_vs_concentrated,
    shear_strength_size_adjusted,
    figure_9_14_coefficients,
    crack_initiation_check,
    combined_bending_axial_stress,
    eccentric_bending_axial_stress,
    torsional_shear_stress_circular,
    torsional_shear_stress_rectangular,
    _beta_rectangular_torsion,
)


class TestAxialAndBendingStress:
    def test_axial_stress_formula(self):
        result = axial_stress(10000.0, 0.02)
        assert result["stress"] == pytest.approx(500000.0)

    def test_section_modulus_rectangular(self):
        result = section_modulus("rectangular", 0.1, 0.3)
        assert result["s"] == pytest.approx(0.1 * 0.3**2 / 6.0)

    def test_section_modulus_circular(self):
        result = section_modulus("circular", 0.2)
        assert result["s"] == pytest.approx(math.pi * 0.2**3 / 32.0)

    def test_bending_stress_formula(self):
        s = section_modulus("rectangular", 0.1, 0.3)["s"]
        result = bending_stress(20000.0, s)
        assert result["bending_stress"] == pytest.approx(20000.0 / s)

    def test_beam_shear_stress_rectangular_k(self):
        result = beam_shear_stress(5000.0, 0.03, shape="rectangular")
        assert result["k"] == 1.5
        assert result["shear_stress"] == pytest.approx(1.5 * 5000.0 / 0.03)

    def test_beam_shear_stress_circular_k(self):
        result = beam_shear_stress(5000.0, 0.03, shape="circular")
        assert result["k"] == pytest.approx(4.0 / 3.0)


class TestTaperedBeam:
    def test_worked_example_from_docstring(self):
        # Printed worked example: b=100 mm, h0=200 mm, tan(theta)=1/10 ->
        # fx=375*M, fxy=37.5*M, fy=3.75*M (M in N*m, stresses in Pa)
        theta = math.atan(0.1)
        result = tapered_beam_stresses(moment=1.0, b=0.1, h0=0.2, theta_rad=theta)
        assert result["fx"] == pytest.approx(375.0)
        assert result["fxy"] == pytest.approx(37.5, rel=1e-6)
        assert result["fy"] == pytest.approx(3.75, rel=1e-6)

    def test_interaction_at_capacity_is_one(self):
        result = tapered_beam_interaction(fx=10.0, fxy=0.0, fy=0.0, fx_allow=10.0, fxy_allow=5.0, fy_allow=2.0)
        assert result["interaction_value"] == pytest.approx(1.0)


class TestSizeEffect:
    def test_ratio_equal_beams_is_one(self):
        result = size_effect_ratio_two_point_vs_concentrated(h1=10, l1=200, a1=0, h2=10, l2=200, a2=0, m=18.0)
        assert result["ratio_r1_r2"] == pytest.approx(1.0)

    def test_worked_example_midspan_reference(self):
        # Printed worked example: h1=10 in, L1=216 in, third-point loading
        # (a1/L1=1/3, so a1=72), R2=10,000 lbf/in^2, m=18 -> R1~7,330 lbf/in^2
        result = size_effect_midspan_reference(
            r2=10000.0, h1=10.0, l1=216.0, a1=72.0, m=18.0, units="inch-pound",
        )
        assert result["r1"] == pytest.approx(7330.0, rel=0.005)

    def test_uniform_vs_concentrated_equal_beams(self):
        result = size_effect_ratio_uniform_vs_concentrated(hu=10, lu=200, hc=10, lc=200, ac=0, m=18.0)
        assert result["ratio_ru_rc"] == pytest.approx((1.0 / 3.876) ** (1.0 / 18.0))

    def test_shear_strength_metric_vs_inch_pound_constants(self):
        metric = shear_strength_size_adjusted(2.0, 5.0, 100.0, units="metric")
        inch_pound = shear_strength_size_adjusted(2.0, 5.0, 100.0, units="inch-pound")
        assert metric["tau"] / inch_pound["tau"] == pytest.approx(1.9 / 1.3)

    def test_bad_units_raise(self):
        with pytest.raises(ValueError):
            shear_strength_size_adjusted(2.0, 5.0, 100.0, units="cgs")


class TestNotchCrackInitiation:
    def test_figure_9_14_traced_values(self):
        # Figure 9-14 (FPL-GTR-282 pdf 244 / printed 9-12), traced off the
        # rendered figure; units 1e-4 (kPa sqrt(mm))^-1, +/-0.01e-4.
        t = figure_9_14_coefficients(0.1, edge="tension")
        c = figure_9_14_coefficients(0.1, edge="compression")
        assert t["a_coefficient"] == pytest.approx(0.177e-4, abs=0.015e-4)
        assert c["a_coefficient"] == pytest.approx(0.074e-4, abs=0.015e-4)
        assert t["b_coefficient"] == pytest.approx(0.277e-4, abs=0.015e-4)
        end = figure_9_14_coefficients(0.55, edge="tension")
        assert end["a_coefficient"] == pytest.approx(0.589e-4, abs=0.015e-4)
        assert end["b_coefficient"] == pytest.approx(1.948e-4, abs=0.015e-4)
        assert figure_9_14_coefficients(0.55, edge="compression")["a_coefficient"] == pytest.approx(0.160e-4, abs=0.015e-4)

    def test_figure_9_14_out_of_range_raises(self):
        with pytest.raises(ValueError):
            figure_9_14_coefficients(0.9)
        # Below a/h 0.02 the curves run together at the origin.
        with pytest.raises(ValueError, match="0.02"):
            figure_9_14_coefficients(0.0)

    def test_crack_initiation_no_load_not_predicted(self):
        result = crack_initiation_check(h=0.3, b=0.1, moment=0.0, shear_force=0.0, a_coefficient=1e-5, b_coefficient=1e-5)
        assert result["criterion_value"] == pytest.approx(0.0)
        assert result["crack_predicted"] is False


class TestCombinedBendingAxialStress:
    def test_tension_case_matches_printed_example_form(self):
        # ft_max = fb0/(1+P/Pcr) + P/A ; fc_max = fb0/(1+P/Pcr) - P/A
        result = combined_bending_axial_stress(fb0=1e6, axial_load=5000.0, area=0.02, p_critical=50000.0, is_tension=True)
        fb = 1e6 / (1.0 + 5000.0 / 50000.0)
        assert result["ft_max"] == pytest.approx(fb + 5000.0 / 0.02)
        assert result["fc_max"] == pytest.approx(fb - 5000.0 / 0.02)

    def test_eccentric_reduces_to_concentric_at_zero_eccentricity(self):
        s = section_modulus("rectangular", 0.1, 0.3)["s"]
        concentric = combined_bending_axial_stress(1e6, 5000.0, 0.02, 50000.0, True)
        eccentric = eccentric_bending_axial_stress(1e6, 0.0, s, 5000.0, 0.02, 50000.0, True)
        assert eccentric["ft_max"] == pytest.approx(concentric["ft_max"])
        assert eccentric["fc_max"] == pytest.approx(concentric["fc_max"])

    def test_compression_case_superposes_eq_9_12(self):
        # FPL-GTR-282 pdf 244 / printed 9-12: total stress = Eq 9-12 + Eq
        # 9-22. A compressive P adds P/A on the concave edge: fb0 = 10,
        # P/A = 2 (P = 4, A = 2), P/Pcr = 0.2 gives fb 12.5, ft_max 10.5,
        # fc_max 14.5 (the edges were swapped: 14.5 and 10.5).
        r = combined_bending_axial_stress(10.0, 4.0, 2.0, 20.0, is_tension=False)
        assert r["fb"] == pytest.approx(12.5)
        assert r["ft_max"] == pytest.approx(10.5)
        assert r["fc_max"] == pytest.approx(14.5)

    def test_eccentric_compression_adds_the_moment(self):
        # fb0 augmented by +/-P e0/S (pdf 244): the printed tensile case
        # subtracts; a compressive P at the same e0 adds. fb0 = 10,
        # P e0/S = 1 (P = 4, e0 = 0.5, S = 2), P/A = 2, P/Pcr = 0.2:
        # (10 + 1)/0.8 = 13.75, ft_max 11.75, fc_max 15.75.
        r = eccentric_bending_axial_stress(10.0, 0.5, 2.0, 4.0, 2.0, 20.0, is_tension=False)
        assert r["ft_max"] == pytest.approx(11.75)
        assert r["fc_max"] == pytest.approx(15.75)
        # The printed tensile case is unchanged: (10 - 1)/1.2 + 2, - 2.
        t = eccentric_bending_axial_stress(10.0, 0.5, 2.0, 4.0, 2.0, 20.0, is_tension=True)
        assert t["ft_max"] == pytest.approx(9.0 / 1.2 + 2.0)
        assert t["fc_max"] == pytest.approx(9.0 / 1.2 - 2.0)


class TestTorsionalShearStress:
    def test_circular_formula(self):
        result = torsional_shear_stress_circular(500.0, 0.1)
        assert result["shear_stress"] == pytest.approx(16.0 * 500.0 / (math.pi * 0.1**3))

    def test_beta_endpoints_match_figure_9_15(self):
        assert _beta_rectangular_torsion(0.0) == pytest.approx(3.0)
        assert _beta_rectangular_torsion(1.0) == pytest.approx(4.80, abs=0.05)

    def test_rectangular_requires_b_le_h(self):
        with pytest.raises(ValueError):
            torsional_shear_stress_rectangular(500.0, h=0.1, b=0.2)

    def test_rectangular_square_section(self):
        result = torsional_shear_stress_rectangular(500.0, h=0.1, b=0.1)
        assert result["beta"] == pytest.approx(4.80, abs=0.05)
