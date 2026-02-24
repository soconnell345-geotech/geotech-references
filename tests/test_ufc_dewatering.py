"""Tests for geotech_references.ufc_dewatering (UFC 3-220-05)."""

import math
import pytest

from geotech_references.ufc_dewatering.equations import (
    thiem_confined_flow_m3_per_s,
    dupuit_unconfined_flow_m3_per_s,
    radius_of_influence_m,
    wellpoint_spacing_m,
    equivalent_well_radius_m,
    superposition_drawdown_m,
)
from geotech_references.ufc_dewatering.tables import (
    table_permeability_by_soil_type,
    table_dewatering_method_selection,
    table_well_screen_slot_size,
)


# ===================================================================
# EQUATION TESTS
# ===================================================================


class TestThiemConfined:
    """thiem_confined_flow_m3_per_s — steady confined well."""

    def test_basic_calculation(self):
        Q = thiem_confined_flow_m3_per_s(1e-4, 10.0, 5.0, 300.0, 0.15)
        # Q = 2*pi*k*H*s / ln(R/rw) = 2*pi*1e-4*10*5 / ln(2000)
        expected = 2 * math.pi * 1e-4 * 10.0 * 5.0 / math.log(300.0 / 0.15)
        assert Q == pytest.approx(expected, rel=1e-6)

    def test_higher_k_more_flow(self):
        Q1 = thiem_confined_flow_m3_per_s(1e-5, 10.0, 5.0, 300.0, 0.15)
        Q2 = thiem_confined_flow_m3_per_s(1e-4, 10.0, 5.0, 300.0, 0.15)
        assert Q2 > Q1

    def test_more_drawdown_more_flow(self):
        Q1 = thiem_confined_flow_m3_per_s(1e-4, 10.0, 3.0, 300.0, 0.15)
        Q2 = thiem_confined_flow_m3_per_s(1e-4, 10.0, 7.0, 300.0, 0.15)
        assert Q2 > Q1

    def test_drawdown_equals_thickness_raises(self):
        with pytest.raises(ValueError, match="drawdown_m.*must be < aquifer"):
            thiem_confined_flow_m3_per_s(1e-4, 10.0, 10.0, 300.0, 0.15)

    def test_drawdown_exceeds_thickness_raises(self):
        with pytest.raises(ValueError, match="drawdown_m.*must be < aquifer"):
            thiem_confined_flow_m3_per_s(1e-4, 10.0, 12.0, 300.0, 0.15)

    def test_zero_k_raises(self):
        with pytest.raises(ValueError, match="k_m_per_s"):
            thiem_confined_flow_m3_per_s(0, 10.0, 5.0, 300.0, 0.15)

    def test_r_less_than_rw_raises(self):
        with pytest.raises(ValueError, match="radius_of_influence.*must be >"):
            thiem_confined_flow_m3_per_s(1e-4, 10.0, 5.0, 0.1, 0.15)

    def test_positive_result(self):
        Q = thiem_confined_flow_m3_per_s(1e-4, 10.0, 5.0, 300.0, 0.15)
        assert Q > 0


class TestDupuitUnconfined:
    """dupuit_unconfined_flow_m3_per_s — steady unconfined well."""

    def test_basic_calculation(self):
        Q = dupuit_unconfined_flow_m3_per_s(1e-4, 10.0, 5.0, 300.0, 0.15)
        expected = math.pi * 1e-4 * (100.0 - 25.0) / math.log(300.0 / 0.15)
        assert Q == pytest.approx(expected, rel=1e-6)

    def test_fully_dewatered_well(self):
        """h=0 means well is fully dewatered to base."""
        Q = dupuit_unconfined_flow_m3_per_s(1e-4, 10.0, 0.0, 300.0, 0.15)
        expected = math.pi * 1e-4 * 100.0 / math.log(300.0 / 0.15)
        assert Q == pytest.approx(expected, rel=1e-6)

    def test_well_head_equals_initial_raises(self):
        with pytest.raises(ValueError, match="well_head_m.*must be < initial"):
            dupuit_unconfined_flow_m3_per_s(1e-4, 10.0, 10.0, 300.0, 0.15)

    def test_negative_well_head_raises(self):
        with pytest.raises(ValueError, match="well_head_m must be >= 0"):
            dupuit_unconfined_flow_m3_per_s(1e-4, 10.0, -1.0, 300.0, 0.15)

    def test_higher_k_more_flow(self):
        Q1 = dupuit_unconfined_flow_m3_per_s(1e-5, 10.0, 5.0, 300.0, 0.15)
        Q2 = dupuit_unconfined_flow_m3_per_s(1e-4, 10.0, 5.0, 300.0, 0.15)
        assert Q2 > Q1

    def test_zero_radius_raises(self):
        with pytest.raises(ValueError, match="radius_of_influence"):
            dupuit_unconfined_flow_m3_per_s(1e-4, 10.0, 5.0, 0, 0.15)


class TestRadiusOfInfluence:
    """radius_of_influence_m — Sichardt formula."""

    def test_basic(self):
        R = radius_of_influence_m(1e-4, 5.0)
        expected = 3000.0 * 5.0 * math.sqrt(1e-4)
        assert R == pytest.approx(expected, rel=1e-6)

    def test_higher_k_larger_radius(self):
        R1 = radius_of_influence_m(1e-5, 5.0)
        R2 = radius_of_influence_m(1e-3, 5.0)
        assert R2 > R1

    def test_higher_drawdown_larger_radius(self):
        R1 = radius_of_influence_m(1e-4, 3.0)
        R2 = radius_of_influence_m(1e-4, 8.0)
        assert R2 > R1

    def test_zero_k_raises(self):
        with pytest.raises(ValueError, match="k_m_per_s"):
            radius_of_influence_m(0, 5.0)

    def test_zero_drawdown_raises(self):
        with pytest.raises(ValueError, match="drawdown_m"):
            radius_of_influence_m(1e-4, 0)

    def test_sand_typical(self):
        """k=1e-4 m/s, s=5m -> R=150m, reasonable for sand."""
        R = radius_of_influence_m(1e-4, 5.0)
        assert 100 < R < 200


class TestWellpointSpacing:
    """wellpoint_spacing_m."""

    def test_basic(self):
        r = wellpoint_spacing_m(0.01, 0.002)
        assert r["number_of_wellpoints"] == 5

    def test_rounds_up(self):
        r = wellpoint_spacing_m(0.01, 0.003)
        # 0.01/0.003 = 3.33 -> ceil = 4
        assert r["number_of_wellpoints"] == 4

    def test_exact_division(self):
        r = wellpoint_spacing_m(0.01, 0.005)
        assert r["number_of_wellpoints"] == 2

    def test_zero_total_raises(self):
        with pytest.raises(ValueError, match="total_flow"):
            wellpoint_spacing_m(0, 0.002)

    def test_zero_per_well_raises(self):
        with pytest.raises(ValueError, match="flow_per_wellpoint"):
            wellpoint_spacing_m(0.01, 0)


class TestEquivalentWellRadius:
    """equivalent_well_radius_m."""

    def test_rectangular(self):
        r = equivalent_well_radius_m(30.0, 20.0)
        expected = math.sqrt(30.0 * 20.0 / math.pi)
        assert r == pytest.approx(expected, rel=1e-6)

    def test_square(self):
        r = equivalent_well_radius_m(20.0, 20.0)
        expected = math.sqrt(400.0 / math.pi)
        assert r == pytest.approx(expected, rel=1e-6)

    def test_linear(self):
        r = equivalent_well_radius_m(100.0)
        expected = 100.0 / math.pi
        assert r == pytest.approx(expected, rel=1e-6)

    def test_zero_length_raises(self):
        with pytest.raises(ValueError, match="length_m"):
            equivalent_well_radius_m(0)

    def test_zero_width_raises(self):
        with pytest.raises(ValueError, match="width_m"):
            equivalent_well_radius_m(30.0, 0)


class TestSuperpositionDrawdown:
    """superposition_drawdown_m — multi-well."""

    def test_single_well(self):
        wells = [{"x_m": 0, "y_m": 0, "Q_m3_per_s": 0.01}]
        r = superposition_drawdown_m(0.001, wells, 10.0, 0.0, 300.0)
        # s = Q/(2*pi*T) * ln(R/r) = 0.01/(2*pi*0.001) * ln(300/10)
        expected = 0.01 / (2 * math.pi * 0.001) * math.log(300.0 / 10.0)
        assert r["total_drawdown_m"] == pytest.approx(expected, abs=0.01)

    def test_two_wells_additive(self):
        wells = [
            {"x_m": -10, "y_m": 0, "Q_m3_per_s": 0.005},
            {"x_m": 10, "y_m": 0, "Q_m3_per_s": 0.005},
        ]
        r = superposition_drawdown_m(0.001, wells, 0.0, 0.0, 300.0)
        assert r["total_drawdown_m"] > 0
        assert len(r["individual_drawdowns_m"]) == 2

    def test_symmetric_wells_equal_drawdown(self):
        wells = [
            {"x_m": -10, "y_m": 0, "Q_m3_per_s": 0.005},
            {"x_m": 10, "y_m": 0, "Q_m3_per_s": 0.005},
        ]
        r = superposition_drawdown_m(0.001, wells, 0.0, 0.0, 300.0)
        assert r["individual_drawdowns_m"][0] == pytest.approx(
            r["individual_drawdowns_m"][1], rel=1e-6
        )

    def test_point_beyond_influence_zero(self):
        wells = [{"x_m": 0, "y_m": 0, "Q_m3_per_s": 0.01}]
        r = superposition_drawdown_m(0.001, wells, 500.0, 0.0, 300.0)
        assert r["total_drawdown_m"] == 0.0

    def test_coincident_point_raises(self):
        wells = [{"x_m": 5, "y_m": 5, "Q_m3_per_s": 0.01}]
        with pytest.raises(ValueError, match="coincides"):
            superposition_drawdown_m(0.001, wells, 5.0, 5.0, 300.0)

    def test_empty_wells_raises(self):
        with pytest.raises(ValueError, match="wells.*empty"):
            superposition_drawdown_m(0.001, [], 0.0, 0.0, 300.0)

    def test_zero_transmissivity_raises(self):
        wells = [{"x_m": 0, "y_m": 0, "Q_m3_per_s": 0.01}]
        with pytest.raises(ValueError, match="transmissivity"):
            superposition_drawdown_m(0, wells, 10.0, 0.0, 300.0)


# ===================================================================
# TABLE TESTS
# ===================================================================


class TestPermeabilityBysoilType:
    """table_permeability_by_soil_type."""

    def test_clean_gravel(self):
        r = table_permeability_by_soil_type("clean_gravel")
        assert r["k_typical_m_per_s"] == 1e-1
        assert r["drainage"] == "very_high"

    def test_clean_sand(self):
        r = table_permeability_by_soil_type("clean_sand")
        assert r["k_typical_m_per_s"] == 1e-3

    def test_clay(self):
        r = table_permeability_by_soil_type("clay")
        assert r["k_typical_m_per_s"] == 1e-9
        assert r["drainage"] == "very_low"

    def test_silt(self):
        r = table_permeability_by_soil_type("silt")
        assert r["k_typical_m_per_s"] == 1e-6

    def test_fractured_rock(self):
        r = table_permeability_by_soil_type("fractured_rock")
        assert r["drainage"] == "variable"

    def test_range_min_less_than_max(self):
        r = table_permeability_by_soil_type("silty_sand")
        assert r["k_min_m_per_s"] < r["k_max_m_per_s"]

    def test_case_insensitive(self):
        r = table_permeability_by_soil_type("CLEAN_GRAVEL")
        assert r["soil_type"] == "clean_gravel"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown soil type"):
            table_permeability_by_soil_type("quicksand")


class TestDewateringMethodSelection:
    """table_dewatering_method_selection."""

    def test_clean_gravel(self):
        r = table_dewatering_method_selection("clean_gravel")
        assert r["primary_method"] == "deep_wells"

    def test_clean_sand(self):
        r = table_dewatering_method_selection("clean_sand")
        assert r["primary_method"] == "wellpoints"

    def test_fine_sand(self):
        r = table_dewatering_method_selection("fine_sand")
        assert r["primary_method"] == "vacuum_wellpoints"

    def test_silt(self):
        r = table_dewatering_method_selection("silt")
        assert r["primary_method"] == "eductor_wells"

    def test_clay(self):
        r = table_dewatering_method_selection("clay")
        assert r["primary_method"] == "electro_osmosis"

    def test_has_max_drawdown(self):
        r = table_dewatering_method_selection("clean_sand")
        assert r["max_drawdown_m"] == 6.0

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown soil type"):
            table_dewatering_method_selection("bedrock")


class TestWellScreenSlotSize:
    """table_well_screen_slot_size."""

    def test_fine_sand(self):
        r = table_well_screen_slot_size(0.15)
        assert r["slot_size_mm"] == 0.25
        assert r["slot_number"] == 10

    def test_medium_sand(self):
        r = table_well_screen_slot_size(0.5)
        assert r["slot_size_mm"] == 0.50

    def test_coarse_sand(self):
        r = table_well_screen_slot_size(1.5)
        assert r["slot_size_mm"] == 1.00

    def test_gravel(self):
        r = table_well_screen_slot_size(5.0)
        assert r["slot_size_mm"] == 2.00

    def test_coarse_gravel(self):
        r = table_well_screen_slot_size(10.0)
        assert r["slot_size_mm"] == 3.00

    def test_below_range_raises(self):
        with pytest.raises(ValueError, match="below minimum"):
            table_well_screen_slot_size(0.05)

    def test_above_range_raises(self):
        with pytest.raises(ValueError, match="exceeds maximum"):
            table_well_screen_slot_size(20.0)

    def test_zero_raises(self):
        with pytest.raises(ValueError, match="d10_mm must be > 0"):
            table_well_screen_slot_size(0)
