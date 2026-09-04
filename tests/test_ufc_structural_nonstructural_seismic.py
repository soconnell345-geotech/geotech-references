"""Tests for geotech_references.ufc_structural.nonstructural_seismic
(Appendix C nonstructural component seismic design guidance)."""

import math

import pytest

from geotech_references.ufc_structural.nonstructural_seismic import (
    rigid_pipe_period_constant,
    rigid_pipe_fundamental_period,
    table_c1_pipe_span,
    table_c2_pipe_span,
    table_c3_pipe_span,
    pipe_car_rpo_ratio,
    flexible_pipe_clearance_requirements,
    elevator_guide_rail_deflection_limits,
    elevator_retainer_plate_clearance,
    counterweight_tie_bracket_spacing,
    elevator_equipment_car_rpo_ratio,
    nonrigid_partition_drift_capacity,
    certification_out_of_plane_response_threshold,
    _parse_feet_inches,
)


class TestPeriodConstants:
    """Anchors: Eq C-1 period constants (printed p. 137)."""

    def test_pinned_pinned(self):
        assert rigid_pipe_period_constant("pinned_pinned")["period_constant"] == 0.50

    def test_fixed_pinned(self):
        assert rigid_pipe_period_constant("fixed_pinned")["period_constant"] == 0.78

    def test_fixed_fixed(self):
        assert rigid_pipe_period_constant("fixed_fixed")["period_constant"] == 1.125

    def test_unknown_condition_raises(self):
        with pytest.raises(ValueError):
            rigid_pipe_period_constant("cantilever")

    def test_fundamental_period_formula(self):
        r = rigid_pipe_fundamental_period("pinned_pinned", length=100.0, ei=2.0e6, w=0.5)
        expected = 0.50 * 100.0 * math.sqrt(0.5 / (2.0e6 * 386.4))
        assert r["ta_seconds"] == pytest.approx(expected)

    def test_short_stiff_span_is_rigid(self):
        r = rigid_pipe_fundamental_period("pinned_pinned", length=50.0, ei=5.0e7, w=0.3)
        assert r["is_rigid"] is True


class TestPipeSpanParsing:
    def test_parse_simple(self):
        assert _parse_feet_inches("9'-4''") == pytest.approx(9 + 4 / 12.0)

    def test_parse_zero_inches(self):
        assert _parse_feet_inches("7'-0''") == pytest.approx(7.0)

    def test_parse_double_digit_inches(self):
        # the source prints some spans with "12''" rather than rolling to
        # the next foot -- transcribed as printed, parses to 12/12 = 1.0 ft
        assert _parse_feet_inches("11'-12''") == pytest.approx(12.0)

    def test_unparseable_string_raises(self):
        with pytest.raises(ValueError):
            _parse_feet_inches("not a span")


class TestTableC1PinnedPinned:
    """Anchors: printed Table C-1 (p. 138)."""

    def test_2in_std_steel(self):
        r = table_c1_pipe_span(2, "std_wt_steel_40s")
        assert r["max_span"] == "9'-4''"
        assert r["max_span_ft"] == pytest.approx(9 + 4 / 12.0)

    def test_1in_copper_type_m_shortest(self):
        r = table_c1_pipe_span(1, "copper_tube_type_m")
        assert r["max_span"] == "4'-11''"

    def test_12in_only_steel_tabulated(self):
        r = table_c1_pipe_span(12, "ex_strong_steel_80s")
        assert r["max_span"] == "20'-9''"

    def test_12in_copper_not_tabulated_raises(self):
        with pytest.raises(ValueError):
            table_c1_pipe_span(12, "copper_tube_type_k")

    def test_unknown_diameter_raises(self):
        with pytest.raises(ValueError):
            table_c1_pipe_span(7, "std_wt_steel_40s")


class TestTableC2FixedPinned:
    """Anchors: printed Table C-2 (p. 139)."""

    def test_2in_std_steel(self):
        r = table_c2_pipe_span(2, "std_wt_steel_40s")
        assert r["max_span"] == "11'-7''"


class TestTableC3FixedFixed:
    """Anchors: printed Table C-3 (p. 140)."""

    def test_2in_std_steel(self):
        r = table_c3_pipe_span(2, "std_wt_steel_40s")
        assert r["max_span"] == "13'-11''"


class TestSpanOrderingSelfConsistency:
    """Self-consistency: fixed-fixed spans should exceed fixed-pinned spans,
    which should exceed pinned-pinned spans, for the same pipe (a stiffer
    end condition permits a longer span at the same target period)."""

    @pytest.mark.parametrize("diameter,pipe_type", [
        (2, "std_wt_steel_40s"), (4, "ex_strong_steel_80s"), (6, "copper_tube_type_k"),
    ])
    def test_span_ordering(self, diameter, pipe_type):
        pp = table_c1_pipe_span(diameter, pipe_type)["max_span_ft"]
        fp = table_c2_pipe_span(diameter, pipe_type)["max_span_ft"]
        ff = table_c3_pipe_span(diameter, pipe_type)["max_span_ft"]
        assert pp < fp < ff


class TestPipeDesignFactors:
    def test_rigid_car_rpo_is_one(self):
        assert pipe_car_rpo_ratio(is_rigid=True)["car_rpo_ratio"] == 1.0

    def test_flexible_car_rpo_is_2_5(self):
        assert pipe_car_rpo_ratio(is_rigid=False)["car_rpo_ratio"] == 2.5

    def test_flexible_pipe_clearances(self):
        r = flexible_pipe_clearance_requirements()
        assert r["min_pipe_to_pipe_clearance_in"] == 4
        assert r["min_pipe_to_wall_clearance_in"] == 3


class TestElevatorCriteria:
    """Anchors: Section C-3.3 printed criteria (pp. 144-145)."""

    def test_guide_rail_deflection_limits(self):
        r = elevator_guide_rail_deflection_limits()
        assert r["guide_rail_max_deflection_in"] == 0.5
        assert r["bracket_max_deflection_in"] == 0.25

    def test_retainer_plate_clearance(self):
        r = elevator_retainer_plate_clearance()
        assert r["max_clearance_in"] == pytest.approx(3.0 / 16.0)

    def test_counterweight_tie_bracket_spacing(self):
        r = counterweight_tie_bracket_spacing()
        assert r["max_tie_bracket_spacing_ft"] == 16
        assert r["one_spreader_bracket_above_spacing_ft"] == 10
        assert r["two_spreader_brackets_above_spacing_ft"] == 14

    def test_equipment_car_rpo_ratio(self):
        assert elevator_equipment_car_rpo_ratio(True)["car_rpo_ratio"] == 1.0
        assert elevator_equipment_car_rpo_ratio(False)["car_rpo_ratio"] == 2.5


class TestPartitionAndCertificationCriteria:
    def test_nonrigid_partition_drift_capacity(self):
        r = nonrigid_partition_drift_capacity()
        assert r["drift_capacity_ratio"] == 0.005
        assert r["drift_capacity_in_per_ft"] == pytest.approx(1.0 / 16.0)

    def test_out_of_plane_response_threshold(self):
        assert certification_out_of_plane_response_threshold()["threshold_ratio"] == 0.20
