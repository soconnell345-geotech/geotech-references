"""Tests for geotech_references.em_2107.loads (Chapter 4: loads/load
factors/load combinations).

Includes reproduction of the Appendix E miter-gate load-combination worked
example (printed pp. 408-409): "Upper gate subjected to maximum hydrostatic
loading" -- 1.2 D + 1.6 G + 1.3 Hs(626.3) + 1.0 Hwc.
"""

import pytest

from geotech_references.em_2107.loads import (
    required_strength_check,
    performance_factor,
    table_4_1_permanent_load_factor,
    table_4_1_load_factor,
    fatigue_serviceability_load_factor,
    principal_load_condition_factor,
    principal_load_factor_self_straining,
    load_combination_lrfd,
    earthquake_load_combination,
)


class TestRequiredStrengthCheck:
    def test_adequate(self):
        r = required_strength_check(u_demand=90.0, phi=0.9, rn_nominal=110.0)
        assert r["alpha_phi_rn"] == pytest.approx(99.0)
        assert r["adequate"] is True

    def test_with_alpha(self):
        r = required_strength_check(u_demand=90.0, phi=0.9, rn_nominal=110.0, alpha=0.90)
        assert r["alpha_phi_rn"] == pytest.approx(89.1)
        assert r["adequate"] is False


class TestPerformanceFactor:
    def test_default_is_one(self):
        assert performance_factor()["alpha"] == 1.0

    def test_override(self):
        assert performance_factor(override=0.90)["alpha"] == 0.90


class TestTable41Permanent:
    def test_dead_add_subtract_alone(self):
        assert table_4_1_permanent_load_factor("D", "add")["gamma"] == 1.2
        assert table_4_1_permanent_load_factor("D", "subtract")["gamma"] == 0.9
        assert table_4_1_permanent_load_factor("D", "alone")["gamma"] == 1.4

    def test_gravity(self):
        assert table_4_1_permanent_load_factor("G", "add")["gamma"] == 1.6
        assert table_4_1_permanent_load_factor("G", "subtract")["gamma"] == 0.0

    def test_invalid_load_id(self):
        with pytest.raises(ValueError):
            table_4_1_permanent_load_factor("X", "add")


class TestTable41TemporaryDynamic:
    def test_hydrostatic_principal(self):
        assert table_4_1_load_factor("Hs", "usual")["factor"] == 1.5
        assert table_4_1_load_factor("Hs", "unusual")["factor"] == 1.4
        assert table_4_1_load_factor("Hs", "extreme")["factor"] == 1.3

    def test_hydrostatic_companion(self):
        assert table_4_1_load_factor("Hs", None, role="companion")["factor"] == 1.0

    def test_ix_only_extreme(self):
        assert table_4_1_load_factor("IX", "extreme")["factor"] == 1.3
        with pytest.raises(ValueError):
            table_4_1_load_factor("IX", "usual")

    def test_live_load_unusual_only(self):
        assert table_4_1_load_factor("L", "unusual")["factor"] == 1.6

    def test_wind_companion_and_extreme(self):
        assert table_4_1_load_factor("W", None, role="companion")["factor"] == 0.5
        assert table_4_1_load_factor("W", "extreme")["factor"] == 1.0

    def test_barge_impact_extreme(self):
        assert table_4_1_load_factor("BI", "extreme")["factor"] == 1.3

    def test_earthquake_unusual_and_extreme(self):
        assert table_4_1_load_factor("EQ", "unusual")["factor"] == 1.5
        assert table_4_1_load_factor("EQ", "extreme")["factor"] == "1.0 or 1.25"

    def test_unknown_load_id(self):
        with pytest.raises(ValueError):
            table_4_1_load_factor("ZZZ", "usual")

    def test_bad_role(self):
        with pytest.raises(ValueError):
            table_4_1_load_factor("Hs", "usual", role="bogus")


class TestFatigueServiceabilityLoadFactor:
    def test_finite_life_value_is_one(self):
        assert fatigue_serviceability_load_factor("Hs")["factor"] == 1.0
        assert fatigue_serviceability_load_factor("D")["factor"] == 1.0

    def test_eq_has_no_entry(self):
        with pytest.raises(ValueError):
            fatigue_serviceability_load_factor("EQ")


class TestPrincipalLoadConditions:
    def test_condition_1(self):
        assert principal_load_condition_factor("condition_1")["gamma_pr"] == 1.2

    def test_condition_2_band(self):
        assert principal_load_condition_factor("condition_2_usual")["gamma_pr"] == 1.5
        assert principal_load_condition_factor("condition_2_unusual")["gamma_pr"] == 1.4
        assert principal_load_condition_factor("condition_2_extreme")["gamma_pr"] == 1.3

    def test_condition_3(self):
        assert principal_load_condition_factor("condition_3")["gamma_pr"] == 1.3

    def test_self_straining(self):
        r = principal_load_factor_self_straining()
        assert r["gamma_pr"] == 1.2
        assert r["is_minimum"] is True


class TestLoadCombinationLrfd_AppendixEMiterGate:
    """Reproduces the Appendix E miter-gate worked example (printed
    pp. 408-409): 1.2D + 1.6G + 1.3*Hs(626.3) + 1.0*Hwc.
    """

    def test_reproduces_printed_combination_structure(self):
        d, g, hs, hwc = 100.0, 20.0, 300.0, 15.0
        r = load_combination_lrfd(
            permanent_terms=[(d, 1.2), (g, 1.6)],
            principal_term=(hs, 1.3),
            companion_terms=[(hwc, 1.0)],
        )
        expected = 1.2 * d + 1.6 * g + 1.3 * hs + 1.0 * hwc
        assert r["u"] == pytest.approx(expected)
        assert r["permanent_sum"] == pytest.approx(1.2 * d + 1.6 * g)
        assert r["principal_contribution"] == pytest.approx(1.3 * hs)

    def test_dead_load_only_combination(self):
        # Appendix E "Dead Load Only": 1.4 D (printed p. 409).
        r = load_combination_lrfd(permanent_terms=[], principal_term=(50.0, 1.4))
        assert r["u"] == pytest.approx(70.0)

    def test_live_load_combination(self):
        # Appendix E: 1.2D + 1.6G + 1.6L + 1.0Hsc (printed p. 409).
        d, g, l, hsc = 100.0, 20.0, 30.0, 40.0
        r = load_combination_lrfd(
            permanent_terms=[(d, 1.2), (g, 1.6)],
            principal_term=(l, 1.6),
            companion_terms=[(hsc, 1.0)],
        )
        assert r["u"] == pytest.approx(1.2 * d + 1.6 * g + 1.6 * l + 1.0 * hsc)


class TestEarthquakeLoadCombinations:
    def test_standard_obe(self):
        r = earthquake_load_combination(permanent_sum=100.0, eq_load=50.0,
                                         companion_terms=[(20.0, 1.0)], method="standard_obe")
        assert r["equation"] == "4.7"
        assert r["u"] == pytest.approx(100.0 + 1.5 * 50.0 + 20.0)

    def test_standard_mde(self):
        r = earthquake_load_combination(permanent_sum=100.0, eq_load=50.0, method="standard_mde")
        assert r["equation"] == "4.8"
        assert r["u"] == pytest.approx(100.0 + 1.25 * 50.0)

    def test_site_specific(self):
        r = earthquake_load_combination(permanent_sum=100.0, eq_load=50.0,
                                         companion_terms=[(20.0, 1.0)], method="site_specific")
        assert r["equation"] == "4.9"
        assert r["u"] == pytest.approx(100.0 + 50.0 + 20.0)

    def test_bad_method(self):
        with pytest.raises(ValueError):
            earthquake_load_combination(100.0, 50.0, method="bogus")
