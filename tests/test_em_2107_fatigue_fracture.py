"""Tests for geotech_references.em_2107.fatigue_fracture (Chapter 5)."""

import pytest

from geotech_references.em_2107.fatigue_fracture import (
    fatigue_load_factor,
    fatigue_check_required,
    fracture_critical_redundancy_check,
)


class TestFatigueLoadFactor:
    def test_finite(self):
        assert fatigue_load_factor("finite")["gamma"] == 1.0

    def test_infinite(self):
        assert fatigue_load_factor("infinite")["gamma"] == 2.0

    def test_invalid(self):
        with pytest.raises(ValueError):
            fatigue_load_factor("bogus")


class TestFatigueCheckRequired:
    def test_below_half_dead_load_not_required(self):
        r = fatigue_check_required(dead_load_compressive_stress=20.0, live_load_tensile_stress=9.0)
        assert r["required"] is False

    def test_at_half_dead_load_required(self):
        r = fatigue_check_required(dead_load_compressive_stress=20.0, live_load_tensile_stress=10.0)
        assert r["required"] is True

    def test_above_half_dead_load_required(self):
        r = fatigue_check_required(dead_load_compressive_stress=20.0, live_load_tensile_stress=15.0)
        assert r["required"] is True
        assert r["threshold"] == pytest.approx(10.0)


class TestFractureCriticalRedundancyCheck:
    def test_adequate_case(self):
        r = fracture_critical_redundancy_check(q_demand_unfactored_sum=30.0, rn_nominal=40.0, fy=50.0)
        assert r["strength_adequate"] is True
        assert r["yield_cap"] == pytest.approx(45.0)
        assert r["within_yield_cap"] is True
        assert r["adequate"] is True

    def test_exceeds_yield_cap(self):
        r = fracture_critical_redundancy_check(q_demand_unfactored_sum=46.0, rn_nominal=60.0, fy=50.0)
        assert r["strength_adequate"] is True
        assert r["within_yield_cap"] is False
        assert r["adequate"] is False

    def test_exceeds_nominal_strength(self):
        r = fracture_critical_redundancy_check(q_demand_unfactored_sum=41.0, rn_nominal=40.0, fy=50.0)
        assert r["strength_adequate"] is False
        assert r["adequate"] is False
