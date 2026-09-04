"""Tests for geotech_references.wood_handbook.fastenings (Chapter 8
fastenings: withdrawal and lateral resistance)."""

import math

import pytest

from geotech_references.wood_handbook.fastenings import (
    table_8_1_common_nail_size,
    table_8_9_screw_shank_diameter,
    nail_withdrawal_common,
    nail_withdrawal_annularly_threaded,
    drift_bolt_withdrawal,
    wood_screw_withdrawal,
    lag_screw_withdrawal,
    table_8_4_lateral_load_coefficient,
    nail_lateral_resistance_pre1991,
    screw_lateral_resistance_pre1991,
    lag_screw_lateral_resistance_pre1991,
    table_8_10_thickness_factor,
    table_8_11_perpendicular_factor,
    hankinson_bearing_strength,
    dowel_bearing_strength,
    yield_limit_lateral_strength,
)


class TestTables81And89:
    def test_16d_common_nail(self):
        row = table_8_1_common_nail_size("16d")
        assert row["length_mm"] == 88.9
        assert row["diameter_mm"] == 4.11

    def test_screw_gauge_10(self):
        row = table_8_9_screw_shank_diameter(10)
        assert row["diameter_mm"] == 4.83

    def test_unknown_penny_size_raises(self):
        with pytest.raises(ValueError):
            table_8_1_common_nail_size("99d")

    def test_unknown_gauge_raises(self):
        with pytest.raises(ValueError):
            table_8_9_screw_shank_diameter(13)


class TestWithdrawal:
    def test_nail_withdrawal_common_formula(self):
        result = nail_withdrawal_common(0.5, diameter_mm=3.76, penetration_mm=50.0)
        expected = 54.12 * 0.5**2.5 * 3.76 * 50.0
        assert result["withdrawal_load_n"] == pytest.approx(expected)

    def test_annularly_threaded_exceeds_common_for_same_g(self):
        # Higher-holding threaded nail should exceed a common nail of the
        # same specific gravity/geometry at typical mid-range G.
        common = nail_withdrawal_common(0.45, 3.76, 50.0)["withdrawal_load_n"]
        threaded = nail_withdrawal_annularly_threaded(0.45, 3.76, 50.0)["withdrawal_load_n"]
        assert threaded > common

    def test_drift_bolt_withdrawal_formula(self):
        result = drift_bolt_withdrawal(0.5, diameter_mm=12.7, penetration_mm=100.0)
        expected = 45.51 * 0.5**2 * 12.7 * 100.0
        assert result["withdrawal_load_n"] == pytest.approx(expected)

    def test_wood_screw_withdrawal_formula(self):
        result = wood_screw_withdrawal(0.5, diameter_mm=4.83, penetration_mm=25.0)
        expected = 108.25 * 0.5**2 * 4.83 * 25.0
        assert result["withdrawal_load_n"] == pytest.approx(expected)

    def test_lag_screw_withdrawal_formula(self):
        result = lag_screw_withdrawal(0.5, diameter_mm=9.5, penetration_mm=60.0)
        expected = 125.4 * 0.5**1.5 * 9.5**0.75 * 60.0
        assert result["withdrawal_load_n"] == pytest.approx(expected)

    def test_withdrawal_increases_with_specific_gravity(self):
        low = nail_withdrawal_common(0.35, 3.76, 50.0)["withdrawal_load_n"]
        high = nail_withdrawal_common(0.60, 3.76, 50.0)["withdrawal_load_n"]
        assert high > low


class TestTable84AndPre1991Lateral:
    def test_softwood_low_range_nails(self):
        row = table_8_4_lateral_load_coefficient("softwoods", 0.40, fastener="nails")
        assert row["k"] == 50.04

    def test_hardwood_high_range_screws(self):
        row = table_8_4_lateral_load_coefficient("hardwoods", 0.60, fastener="screws")
        assert row["k"] == 44.13

    def test_sg_out_of_range_raises(self):
        with pytest.raises(ValueError):
            table_8_4_lateral_load_coefficient("softwoods", 0.99, fastener="nails")

    def test_nail_lateral_pre1991_formula(self):
        result = nail_lateral_resistance_pre1991(k_coefficient=62.55, diameter_mm=3.76)
        assert result["lateral_load_n"] == pytest.approx(62.55 * 3.76**1.5)

    def test_screw_lateral_pre1991_formula(self):
        result = screw_lateral_resistance_pre1991(k_coefficient=29.79, diameter_mm=4.83)
        assert result["lateral_load_n"] == pytest.approx(29.79 * 4.83**2)

    def test_lag_screw_lateral_pre1991_formula(self):
        result = lag_screw_lateral_resistance_pre1991(k_coefficient=26.34, diameter_mm=9.5)
        assert result["lateral_load_n"] == pytest.approx(26.34 * 9.5**2)

    def test_table_8_10_thickness_factor(self):
        row = table_8_10_thickness_factor(3.5)
        assert row["factor"] == 1.00

    def test_table_8_11_perpendicular_factor(self):
        row = table_8_11_perpendicular_factor(12.7)
        assert row["factor"] == 0.65

    def test_table_8_10_bad_ratio_raises(self):
        with pytest.raises(ValueError):
            table_8_10_thickness_factor(1.0)


class TestHankinsonFormula:
    def test_zero_angle_gives_p(self):
        result = hankinson_bearing_strength(p_parallel=100.0, q_perpendicular=20.0, theta_deg=0.0)
        assert result["n_value"] == pytest.approx(100.0)

    def test_90_degree_gives_q(self):
        result = hankinson_bearing_strength(p_parallel=100.0, q_perpendicular=20.0, theta_deg=90.0)
        assert result["n_value"] == pytest.approx(20.0)

    def test_intermediate_angle_between_p_and_q(self):
        result = hankinson_bearing_strength(100.0, 20.0, 45.0)
        assert 20.0 < result["n_value"] < 100.0


class TestYieldLimitModel:
    def test_dowel_bearing_strength_formula(self):
        result = dowel_bearing_strength(0.5)
        assert result["fe_mpa"] == pytest.approx(114.5 * 0.5**1.84)

    def test_nail_yield_governing_mode_is_minimum(self):
        fem = dowel_bearing_strength(0.5)["fe_mpa"]
        fes = dowel_bearing_strength(0.5)["fe_mpa"]
        result = yield_limit_lateral_strength(
            "nail", diameter_mm=3.76, fem_mpa=fem, fes_mpa=fes, fyb_mpa=650.0,
            side_member_thickness_mm=19.0, main_member_penetration_mm=38.0,
        )
        computed_min = min(v for k, v in result.items() if k.startswith("z_") and k != "z_governing" and v is not None)
        assert result["z_governing"] == pytest.approx(computed_min)
        assert result["governing_mode"] in ("is", "iiim", "iiis", "iv")

    def test_screw_has_no_mode_iiim(self):
        fem = dowel_bearing_strength(0.5)["fe_mpa"]
        result = yield_limit_lateral_strength(
            "screw", diameter_mm=4.83, fem_mpa=fem, fes_mpa=fem, fyb_mpa=780.0,
            side_member_thickness_mm=19.0,
        )
        assert result["z_iiim"] is None

    def test_no_side_member_thickness_still_computes_mode_iv(self):
        # Mode IV (two plastic hinges) does not require ts or p, so it is
        # always computable even with no member-thickness/penetration
        # geometry supplied; it becomes the sole (governing) mode.
        fem = dowel_bearing_strength(0.5)["fe_mpa"]
        result = yield_limit_lateral_strength("nail", 3.76, fem, fem, 650.0)
        assert result["z_is"] is None
        assert result["z_iiim"] is None
        assert result["z_iiis"] is None
        assert result["governing_mode"] == "iv"

    def test_higher_specific_gravity_increases_dowel_bearing_strength(self):
        low = dowel_bearing_strength(0.35)["fe_mpa"]
        high = dowel_bearing_strength(0.60)["fe_mpa"]
        assert high > low
