"""Tests for geotech_references.em_2104.loads (Chapter 3 loads/strength
design)."""

import pytest

from geotech_references.em_2104.loads import (
    table_3_1_load_inventory,
    table_3_2_permanent_load_factor,
    table_3_2_load_factor,
    required_strength_check,
    load_combination_lrfd,
    earthquake_load_combination,
    table_f2_target_reliability,
    probability_of_failure_from_beta,
)


class TestTable31Loads:
    def test_hs_is_temporary(self):
        assert table_3_1_load_inventory("Hs")["duration"] == "temporary"

    def test_eq_is_dynamic(self):
        assert table_3_1_load_inventory("EQ")["duration"] == "dynamic"

    def test_d_is_permanent(self):
        assert table_3_1_load_inventory("D")["duration"] == "permanent"

    def test_full_table_has_18_loads(self):
        # 4 permanent (D, EV, EH, G) + 7 temporary (Hs, IX, ES, Q, L, T, V)
        # + 7 dynamic (Hd, Hw, IM, BI, W, EQ, HA), Table 3-1 (printed p. 17).
        assert len(table_3_1_load_inventory()["loads"]) == 18

    def test_unknown_load_raises(self):
        with pytest.raises(ValueError):
            table_3_1_load_inventory("ZZZ")


class TestTable32PermanentFactors:
    def test_dead_add_and_subtract(self):
        assert table_3_2_permanent_load_factor("D", "add")["gamma_p"] == 1.2
        assert table_3_2_permanent_load_factor("D", "subtract")["gamma_p"] == 0.9
        assert table_3_2_permanent_load_factor("D", "alone")["gamma_p"] == 1.4

    def test_eh_active_passive(self):
        assert table_3_2_permanent_load_factor("EH_active")["gamma_p"] == 1.5
        assert table_3_2_permanent_load_factor("EH_passive")["gamma_p"] == 0.5

    def test_gravity_can_be_zero(self):
        assert table_3_2_permanent_load_factor("G", "subtract")["gamma_p"] == 0.0


class TestTable32PrincipalCompanionFactors:
    def test_hydrostatic_principal_by_category(self):
        assert table_3_2_load_factor("Hs", "usual")["factor"] == 1.5
        assert table_3_2_load_factor("Hs", "unusual")["factor"] == 1.4
        assert table_3_2_load_factor("Hs", "extreme")["factor"] == 1.3

    def test_hydrostatic_companion(self):
        assert table_3_2_load_factor("Hs", None, role="companion")["factor"] == 1.0

    def test_wave_extreme(self):
        assert table_3_2_load_factor("Hw", "extreme")["factor"] == 1.2

    def test_barge_impact_all_categories(self):
        assert table_3_2_load_factor("BI", "usual")["factor"] == 2.2
        assert table_3_2_load_factor("BI", "unusual")["factor"] == 1.6
        assert table_3_2_load_factor("BI", "extreme")["factor"] == 1.3

    def test_live_load_extreme_not_applicable(self):
        with pytest.raises(ValueError):
            table_3_2_load_factor("L", "extreme")

    def test_vehicle_load_defers_to_aashto(self):
        assert table_3_2_load_factor("V", "unusual")["factor"] == "AASHTO"


class TestEq31RequiredStrength:
    def test_adequate(self):
        r = required_strength_check(u_demand=100.0, phi=0.9, rn_nominal=150.0)
        assert r["phi_rn"] == pytest.approx(135.0)
        assert r["adequate"] is True

    def test_inadequate(self):
        r = required_strength_check(u_demand=200.0, phi=0.9, rn_nominal=150.0)
        assert r["adequate"] is False


class TestEq32LoadCombination:
    def test_simple_combination(self):
        # U = 1.2*D + 1.5*Hs(principal) + 1.0*L(companion)
        r = load_combination_lrfd(
            permanent_terms=[(100.0, 1.2)],
            principal_term=(50.0, 1.5),
            companion_terms=[(10.0, 1.0)],
        )
        assert r["u"] == pytest.approx(1.2 * 100 + 1.5 * 50 + 1.0 * 10)

    def test_no_companion(self):
        r = load_combination_lrfd(
            permanent_terms=[(100.0, 1.2), (20.0, 1.35)],
            principal_term=(50.0, 1.4),
        )
        assert r["u"] == pytest.approx(1.2 * 100 + 1.35 * 20 + 1.4 * 50)


class TestEarthquakeCombinations:
    def test_standard_obe(self):
        r = earthquake_load_combination(permanent_sum=100.0, eq_load=40.0,
                                         method="standard_obe")
        assert r["u"] == pytest.approx(100.0 + 1.5 * 40.0)
        assert r["equation"] == "3-3"

    def test_standard_mde(self):
        r = earthquake_load_combination(permanent_sum=100.0, eq_load=40.0,
                                         method="standard_mde")
        assert r["u"] == pytest.approx(100.0 + 1.25 * 40.0)
        assert r["equation"] == "3-4"

    def test_site_specific(self):
        r = earthquake_load_combination(
            permanent_sum=100.0, eq_load=40.0,
            companion_terms=[(10.0, 1.0)], method="site_specific_mde_mce",
        )
        assert r["u"] == pytest.approx(100.0 + 40.0 + 10.0)
        assert r["equation"] == "3-5"

    def test_bad_method_raises(self):
        with pytest.raises(ValueError):
            earthquake_load_combination(100.0, 40.0, method="bogus")


class TestTableF2Reliability:
    def test_normal_single_load_path(self):
        assert table_f2_target_reliability("normal", "single")["beta"] == 3.5

    def test_critical_single_load_path(self):
        assert table_f2_target_reliability("critical", "single")["beta"] == 4.0

    def test_critical_redundant(self):
        assert table_f2_target_reliability("critical", "redundant")["beta"] == 3.5

    def test_bad_key_raises(self):
        with pytest.raises(ValueError):
            table_f2_target_reliability("normal", "triple")


class TestProbabilityOfFailure:
    def test_beta_zero_is_half(self):
        assert probability_of_failure_from_beta(0.0)["pf"] == pytest.approx(0.5)

    def test_higher_beta_lower_pf(self):
        pf_low = probability_of_failure_from_beta(3.5)["pf"]
        pf_high = probability_of_failure_from_beta(4.0)["pf"]
        assert pf_high < pf_low
