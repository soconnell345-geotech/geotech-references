"""Tests for geotech_references.ufc_structural.seismic_load_combinations
(Chapters 2/3/7 + Appendix B seismic load combinations and capacity checks)."""

import pytest

from geotech_references.ufc_structural.seismic_load_combinations import (
    vertical_seismic_effect_ev0,
    basic_combination_with_vertical_seismic_lrfd,
    basic_combination_with_vertical_seismic_asd,
    alternate_rc4_seismic_combination,
    coupling_beam_shear_demand,
    structural_separation_healthcare,
)


class TestVerticalSeismicEffect:
    def test_ev0_formula(self):
        r = vertical_seismic_effect_ev0(sds=0.8, d=100.0)
        assert r["ev0"] == pytest.approx(0.67 * 0.8 * 100.0)


class TestLrfdCombinationsWithVerticalSeismic:
    """Anchors: paragraph 2.3.6 additional combinations 8/9 (printed p. 44)."""

    def test_combination_8_formula(self):
        r = basic_combination_with_vertical_seismic_lrfd(d=100, ev0=20, eh=50, l=10, s=5)
        expected_8 = 1.2 * 100 + 1.0 * 20 + 0.3 * 50 + 10 + 0.2 * 5
        assert r["combination_8"] == pytest.approx(expected_8)

    def test_combination_9_formula(self):
        r = basic_combination_with_vertical_seismic_lrfd(d=100, ev0=20, eh=50)
        expected_9 = 0.9 * 100 - 1.0 * 20 + 0.3 * 50
        assert r["combination_9"] == pytest.approx(expected_9)

    def test_no_live_or_snow_defaults_to_zero(self):
        r = basic_combination_with_vertical_seismic_lrfd(d=100, ev0=20, eh=50)
        assert r["combination_8"] == pytest.approx(1.2 * 100 + 20 + 0.3 * 50)


class TestAsdCombinationsWithVerticalSeismic:
    """Anchors: paragraph 2.4.5 additional combinations 11/12/13 (printed pp. 45-46)."""

    def test_combination_11_formula(self):
        r = basic_combination_with_vertical_seismic_asd(d=100, ev0=20, eh=50)
        expected_11 = 1.0 * 100 + 0.7 * 20 + 0.21 * 50
        assert r["combination_11"] == pytest.approx(expected_11)

    def test_combination_12_formula(self):
        r = basic_combination_with_vertical_seismic_asd(d=100, ev0=20, eh=50, l=10, s=5)
        expected_12 = 1.0 * 100 + 0.525 * 20 + 0.1575 * 50 + 0.75 * 10 + 0.75 * 5
        assert r["combination_12"] == pytest.approx(expected_12)

    def test_combination_13_formula(self):
        r = basic_combination_with_vertical_seismic_asd(d=100, ev0=20, eh=50)
        expected_13 = 0.6 * 100 - 0.7 * 20 + 0.21 * 50
        assert r["combination_13"] == pytest.approx(expected_13)


class TestAlternateRC4Combination:
    """Anchors: Appendix B Eq B-1/B-2 (printed p. 112)."""

    def test_eq_b1_additive(self):
        r = alternate_rc4_seismic_combination(d=100, l=20, s=10, e=50, combination="additive")
        expected = 1.1 * (100 + 0.25 * 20 + 0.15 * 10) + 50
        assert r["u"] == pytest.approx(expected)
        assert r["equation"] == "B-1"

    def test_eq_b2_counteractive(self):
        r = alternate_rc4_seismic_combination(d=100, l=20, s=10, e=-50, combination="counteractive")
        expected = 0.9 * 100 - 50
        assert r["u"] == pytest.approx(expected)
        assert r["equation"] == "B-2"

    def test_snow_exception_zero_snow(self):
        # per the printed exception, S may be taken as 0 when < 40 psf
        r = alternate_rc4_seismic_combination(d=100, l=20, s=0, e=50, combination="additive")
        expected = 1.1 * (100 + 0.25 * 20) + 50
        assert r["u"] == pytest.approx(expected)

    def test_bad_combination_raises(self):
        with pytest.raises(ValueError):
            alternate_rc4_seismic_combination(100, 20, 10, 50, combination="bogus")


class TestCouplingBeamShear:
    """Anchors: paragraph 2106.2.3 (printed pp. 36-37)."""

    def test_formula(self):
        r = coupling_beam_shear_demand(mn1=500.0, mn2=500.0, lc=100.0, vg=20.0)
        expected = 1.25 * (500.0 + 500.0) / 100.0 + 1.4 * 20.0
        assert r["required_phi_vn"] == pytest.approx(expected)

    def test_symmetric_moments_simplify(self):
        # symmetric Mn1=Mn2=Mn: phi*Vn >= 2.5*Mn/Lc + 1.4*Vg
        r = coupling_beam_shear_demand(mn1=400.0, mn2=400.0, lc=80.0, vg=0.0)
        assert r["required_phi_vn"] == pytest.approx(2.5 * 400.0 / 80.0)


class TestStructuralSeparationHealthcare:
    """Anchors: Eq 12.12-1 (printed p. 100)."""

    def test_formula(self):
        r = structural_separation_healthcare(cd=5.5, delta_max=2.0)
        assert r["delta_m"] == pytest.approx(5.5 * 2.0)
        assert r["equation"] == "12.12-1"
