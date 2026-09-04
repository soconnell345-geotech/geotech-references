"""Tests for geotech_references.ufc_structural.evaluation_retrofit
(Chapter 4 Table 4-1(a)/(b), trigger thresholds, IEBC roof-diaphragm trigger)."""

import pytest

from geotech_references.ufc_structural.evaluation_retrofit import (
    performance_level_definition,
    table_4_1a_structural_performance_objective,
    table_4_1b_nonstructural_performance_objective,
    evaluation_trigger_cost_threshold,
    rp10_incidental_occupancy_exemption,
    roof_diaphragm_high_wind_retrofit_trigger,
    TABLE_4_1A,
    TABLE_4_1B,
)


class TestPerformanceLevelDefinitions:
    def test_cp_is_collapse_prevention(self):
        assert performance_level_definition("CP")["definition"] == "Collapse Prevention"

    def test_lms_distinct_from_ls(self):
        assert performance_level_definition("LmS")["definition"] == "Limited Safety"
        assert performance_level_definition("LS")["definition"] == "Life Safety"

    def test_hr_is_hazard_reduced(self):
        assert performance_level_definition("HR")["definition"] == "Hazard Reduced"

    def test_unknown_abbreviation_raises(self):
        with pytest.raises(ValueError):
            performance_level_definition("XX")


class TestTable41AStructuralObjectives:
    """Anchors: printed Table 4-1(a) trigger rows (pp. 72-73); the
    Evaluation/Retrofit split for RC I/II and III is stored as literal
    printed cell text per the module's documented caveat."""

    def test_all_thirteen_trigger_rows_present(self):
        assert len(TABLE_4_1A) == 13

    def test_change_of_occupancy_uses_n_level_hazard(self):
        r = table_4_1a_structural_performance_objective("a")
        assert "BSE-2N" in r["rc1_2_evaluation"]
        assert "BSE-1N" in r["rc1_2_retrofit"]

    def test_alteration_uses_e_level_hazard(self):
        r = table_4_1a_structural_performance_objective("b_alteration")
        assert "BSE-2E" in r["rc1_2_evaluation"]
        assert "BSE-1E" in r["rc1_2_retrofit"]

    def test_unacceptable_risk_exposure_is_urm_focused(self):
        r = table_4_1a_structural_performance_objective("i")
        assert r["rc1_2_evaluation"] == "CP in BSE-1E"
        assert r["rc3_evaluation"] == "CP in BSE-1E"
        assert r["rc4_evaluation"] == "CP in BSE-1E"

    def test_n_level_and_e_level_triggers_are_self_consistent(self):
        # self-consistency: every trigger using the N-level objective set
        # must show the SAME rc4_evaluation string (they share one constant)
        n_level_triggers = ("a", "b_addition", "c_addition", "d_addition", "h")
        values = {table_4_1a_structural_performance_objective(t)["rc4_evaluation"] for t in n_level_triggers}
        assert len(values) == 1

    def test_unknown_trigger_raises(self):
        with pytest.raises(ValueError):
            table_4_1a_structural_performance_objective("zz")


class TestTable41BNonstructuralObjectives:
    """Anchors: printed Table 4-1(b) (pp. 74-75); Evaluation == Retrofit for
    every risk category (confirmed via structured table extraction)."""

    def test_all_thirteen_trigger_rows_present(self):
        assert len(TABLE_4_1B) == 13

    def test_change_of_occupancy_rc4_is_operational(self):
        r = table_4_1b_nonstructural_performance_objective("a", "IV")
        assert r["lower_tier"] == "OP in BSE-1N"
        assert r["higher_tier"] == "HR in BSE-2N"

    def test_change_of_occupancy_rc1_2_is_position_retention(self):
        r = table_4_1b_nonstructural_performance_objective("a", "I_II")
        assert "PR in BSE-1N" in r["lower_tier"]

    def test_alteration_uses_e_level_hazard(self):
        r = table_4_1b_nonstructural_performance_objective("b_alteration", "III")
        assert "BSE-1E" in r["lower_tier"]
        assert "BSE-2E" in r["higher_tier"]

    def test_unacceptable_risk_exposure_not_required(self):
        r = table_4_1b_nonstructural_performance_objective("i", "IV")
        assert r["lower_tier"] == "Not required"
        assert r["higher_tier"] == "Not required"

    def test_risk_category_i_and_ii_equivalent(self):
        r_i = table_4_1b_nonstructural_performance_objective("e", "I")
        r_ii = table_4_1b_nonstructural_performance_objective("e", "II")
        assert r_i["lower_tier"] == r_ii["lower_tier"]

    def test_unknown_risk_category_raises(self):
        with pytest.raises(ValueError):
            table_4_1b_nonstructural_performance_objective("a", "V")


class TestEvaluationTriggerCostThreshold:
    """Anchors: RP 10 Section 1.2.1 Items c/d (printed p. 69)."""

    def test_sdc_c_is_50_percent(self):
        assert evaluation_trigger_cost_threshold("C")["cost_threshold_fraction"] == 0.50

    @pytest.mark.parametrize("sdc", ["D", "E", "F"])
    def test_sdc_def_is_30_percent(self, sdc):
        assert evaluation_trigger_cost_threshold(sdc)["cost_threshold_fraction"] == 0.30

    def test_sdc_a_b_raises(self):
        with pytest.raises(ValueError):
            evaluation_trigger_cost_threshold("B")


class TestExemptionsAndTriggers:
    def test_incidental_occupancy_exemption(self):
        r = rp10_incidental_occupancy_exemption()
        assert r["max_persons_per_100_sf"] == 2
        assert r["max_hours_per_day"] == 2

    def test_roof_diaphragm_not_high_wind(self):
        r = roof_diaphragm_high_wind_retrofit_trigger(basic_wind_speed_mph=110)
        assert r["high_wind_region"] is False
        assert r["evaluation_required"] is False

    def test_roof_diaphragm_high_wind_and_cost_trigger(self):
        r = roof_diaphragm_high_wind_retrofit_trigger(basic_wind_speed_mph=140, cost_fraction=0.6)
        assert r["high_wind_region"] is True
        assert r["cost_trigger"] is True
        assert r["evaluation_required"] is True

    def test_roof_diaphragm_high_wind_but_no_cost_or_reroof_trigger(self):
        r = roof_diaphragm_high_wind_retrofit_trigger(basic_wind_speed_mph=140, cost_fraction=0.2, reroofing_fraction=0.1)
        assert r["evaluation_required"] is False

    def test_roof_diaphragm_reroofing_trigger(self):
        r = roof_diaphragm_high_wind_retrofit_trigger(basic_wind_speed_mph=140, reroofing_fraction=0.6)
        assert r["reroofing_trigger"] is True
        assert r["evaluation_required"] is True

    def test_capacity_check_fraction(self):
        r = roof_diaphragm_high_wind_retrofit_trigger(basic_wind_speed_mph=140, cost_fraction=0.6)
        assert r["capacity_check_fraction"] == 0.75

    def test_exempt_building_types_listed(self):
        r = roof_diaphragm_high_wind_retrofit_trigger(basic_wind_speed_mph=140)
        assert any("risk category i" in t.lower() for t in r["exempt_building_types"])
