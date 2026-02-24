"""Tests for geotech_references.ufc_expansive (UFC 3-220-07)."""

import math
import pytest

from geotech_references.ufc_expansive.equations import (
    activity_index,
    free_swell_percent,
    swell_pressure_kPa,
    heave_prediction_mm,
    pier_minimum_embedment_m,
)
from geotech_references.ufc_expansive.tables import (
    table_swell_potential_classification,
    table_active_zone_depth,
    table_foundation_selection,
    table_grade_beam_void_space,
)


# ===================================================================
# EQUATION TESTS
# ===================================================================


class TestActivityIndex:
    """activity_index — Skempton's activity."""

    def test_inactive(self):
        r = activity_index(10.0, 30.0)
        assert r["activity"] == pytest.approx(0.333, abs=0.001)
        assert r["classification"] == "inactive"

    def test_normal(self):
        r = activity_index(30.0, 30.0)
        assert r["activity"] == pytest.approx(1.0, abs=0.001)
        assert r["classification"] == "normal"

    def test_active(self):
        r = activity_index(45.0, 30.0)
        assert r["activity"] == pytest.approx(1.5, abs=0.001)
        assert r["classification"] == "active"

    def test_highly_active(self):
        r = activity_index(60.0, 20.0)
        assert r["activity"] == pytest.approx(3.0, abs=0.001)
        assert r["classification"] == "highly_active"

    def test_boundary_inactive_normal(self):
        r = activity_index(15.0, 20.0)  # A = 0.75
        assert r["classification"] == "normal"

    def test_boundary_normal_active(self):
        r = activity_index(25.0, 20.0)  # A = 1.25
        assert r["classification"] == "active"

    def test_zero_pi_raises(self):
        with pytest.raises(ValueError, match="plasticity_index"):
            activity_index(0, 30.0)

    def test_zero_clay_raises(self):
        with pytest.raises(ValueError, match="clay_fraction_pct"):
            activity_index(30.0, 0)

    def test_clay_over_100_raises(self):
        with pytest.raises(ValueError, match="clay_fraction_pct"):
            activity_index(30.0, 101)


class TestFreeSwellPercent:
    """free_swell_percent — Seed et al. 1962."""

    def test_low_pi(self):
        s = free_swell_percent(10.0)
        assert s > 0
        assert s < 2.0  # low PI = low swell

    def test_medium_pi(self):
        s = free_swell_percent(25.0)
        assert 2.0 < s < 15.0

    def test_high_pi(self):
        s = free_swell_percent(50.0)
        assert s > 15.0

    def test_increases_with_pi(self):
        s1 = free_swell_percent(20.0)
        s2 = free_swell_percent(40.0)
        assert s2 > s1

    def test_formula(self):
        s = free_swell_percent(30.0)
        expected = 2.16e-3 * 30.0 ** 2.44
        assert s == pytest.approx(expected, rel=1e-6)

    def test_zero_pi_raises(self):
        with pytest.raises(ValueError, match="plasticity_index"):
            free_swell_percent(0)

    def test_negative_pi_raises(self):
        with pytest.raises(ValueError, match="plasticity_index"):
            free_swell_percent(-5)


class TestSwellPressure:
    """swell_pressure_kPa — Komornik & David 1969."""

    def test_positive_result(self):
        p = swell_pressure_kPa(40.0, 16.0, 20.0)
        assert p > 0

    def test_higher_pi_more_pressure(self):
        p1 = swell_pressure_kPa(20.0, 16.0, 20.0)
        p2 = swell_pressure_kPa(50.0, 16.0, 20.0)
        assert p2 > p1

    def test_higher_density_more_pressure(self):
        p1 = swell_pressure_kPa(40.0, 14.0, 20.0)
        p2 = swell_pressure_kPa(40.0, 18.0, 20.0)
        assert p2 > p1

    def test_higher_moisture_less_pressure(self):
        p1 = swell_pressure_kPa(40.0, 16.0, 15.0)
        p2 = swell_pressure_kPa(40.0, 16.0, 30.0)
        assert p2 < p1

    def test_zero_pi_raises(self):
        with pytest.raises(ValueError, match="plasticity_index"):
            swell_pressure_kPa(0, 16.0, 20.0)

    def test_zero_density_raises(self):
        with pytest.raises(ValueError, match="dry_density"):
            swell_pressure_kPa(40.0, 0, 20.0)

    def test_zero_moisture_raises(self):
        with pytest.raises(ValueError, match="moisture_content"):
            swell_pressure_kPa(40.0, 16.0, 0)


class TestHeavePrediction:
    """heave_prediction_mm — layer summation."""

    def test_single_layer(self):
        layers = [{"thickness_m": 2.0, "swell_strain_pct": 3.0}]
        r = heave_prediction_mm(layers)
        assert r["total_heave_mm"] == pytest.approx(60.0, abs=0.1)
        assert r["number_of_layers"] == 1

    def test_multiple_layers(self):
        layers = [
            {"thickness_m": 1.0, "swell_strain_pct": 5.0},
            {"thickness_m": 1.5, "swell_strain_pct": 3.0},
            {"thickness_m": 2.0, "swell_strain_pct": 1.0},
        ]
        r = heave_prediction_mm(layers)
        expected = 50.0 + 45.0 + 20.0
        assert r["total_heave_mm"] == pytest.approx(expected, abs=0.1)

    def test_zero_strain_no_heave(self):
        layers = [{"thickness_m": 3.0, "swell_strain_pct": 0.0}]
        r = heave_prediction_mm(layers)
        assert r["total_heave_mm"] == 0.0

    def test_layer_heaves_returned(self):
        layers = [
            {"thickness_m": 1.0, "swell_strain_pct": 2.0},
            {"thickness_m": 1.0, "swell_strain_pct": 4.0},
        ]
        r = heave_prediction_mm(layers)
        assert len(r["layer_heaves_mm"]) == 2
        assert r["layer_heaves_mm"][0] == pytest.approx(20.0, abs=0.1)
        assert r["layer_heaves_mm"][1] == pytest.approx(40.0, abs=0.1)

    def test_empty_layers_raises(self):
        with pytest.raises(ValueError, match="layers.*empty"):
            heave_prediction_mm([])

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError, match="thickness_m"):
            heave_prediction_mm([{"thickness_m": 0, "swell_strain_pct": 3.0}])

    def test_negative_strain_raises(self):
        with pytest.raises(ValueError, match="swell_strain_pct"):
            heave_prediction_mm([{"thickness_m": 1.0, "swell_strain_pct": -1.0}])


class TestPierMinimumEmbedment:
    """pier_minimum_embedment_m."""

    def test_basic(self):
        r = pier_minimum_embedment_m(3.0, factor=1.5)
        assert r["min_embedment_m"] == pytest.approx(4.5, abs=0.01)

    def test_minimum_1m_anchorage(self):
        r = pier_minimum_embedment_m(3.0, factor=1.0)
        # factor=1.0 means total = 3m, anchorage = 0, but min 1m
        assert r["anchorage_below_active_zone_m"] == 1.0
        assert r["min_embedment_m"] == pytest.approx(4.0, abs=0.01)

    def test_deep_active_zone(self):
        r = pier_minimum_embedment_m(6.0, factor=1.5)
        assert r["min_embedment_m"] == pytest.approx(9.0, abs=0.01)

    def test_zero_depth_raises(self):
        with pytest.raises(ValueError, match="active_zone_depth"):
            pier_minimum_embedment_m(0)

    def test_factor_less_than_1_raises(self):
        with pytest.raises(ValueError, match="factor"):
            pier_minimum_embedment_m(3.0, factor=0.5)


# ===================================================================
# TABLE TESTS
# ===================================================================


class TestSwellPotentialClassification:
    """table_swell_potential_classification."""

    def test_very_low_pi(self):
        r = table_swell_potential_classification(plasticity_index=5)
        assert r["classification"] == "very_low"

    def test_low_pi(self):
        r = table_swell_potential_classification(plasticity_index=15)
        assert r["classification"] == "low"

    def test_medium_pi(self):
        r = table_swell_potential_classification(plasticity_index=25)
        assert r["classification"] == "medium"

    def test_high_pi(self):
        r = table_swell_potential_classification(plasticity_index=45)
        assert r["classification"] == "high"

    def test_very_high_pi(self):
        r = table_swell_potential_classification(plasticity_index=60)
        assert r["classification"] == "very_high"

    def test_liquid_limit_only(self):
        r = table_swell_potential_classification(liquid_limit=60)
        assert r["classification"] in ("medium", "high")

    def test_both_parameters_uses_worse(self):
        r = table_swell_potential_classification(plasticity_index=15,
                                                  liquid_limit=60)
        # PI=15 -> low, LL=60 -> high; should use high
        assert r["classification"] in ("medium", "high")

    def test_neither_parameter_raises(self):
        with pytest.raises(ValueError, match="At least one"):
            table_swell_potential_classification()

    def test_negative_pi_raises(self):
        with pytest.raises(ValueError, match="plasticity_index"):
            table_swell_potential_classification(plasticity_index=-5)

    def test_zero_pi(self):
        r = table_swell_potential_classification(plasticity_index=0)
        assert r["classification"] == "very_low"


class TestActiveZoneDepth:
    """table_active_zone_depth."""

    def test_arid(self):
        r = table_active_zone_depth("arid")
        assert r["typical_depth_m"] == 6.0

    def test_humid(self):
        r = table_active_zone_depth("humid")
        assert r["typical_depth_m"] == 1.5

    def test_coastal(self):
        r = table_active_zone_depth("coastal")
        assert r["typical_depth_m"] == 1.0

    def test_semi_arid(self):
        r = table_active_zone_depth("semi_arid")
        assert r["typical_depth_m"] == 4.0

    def test_has_range(self):
        r = table_active_zone_depth("arid")
        assert r["range_m"] == (3.0, 9.0)

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown climate"):
            table_active_zone_depth("tropical")

    def test_case_insensitive(self):
        r = table_active_zone_depth("ARID")
        assert r["climate"] == "arid"


class TestFoundationSelection:
    """table_foundation_selection."""

    def test_very_low(self):
        r = table_foundation_selection("very_low")
        assert "conventional_slab_on_grade" in r["recommended"]

    def test_high(self):
        r = table_foundation_selection("high")
        assert "pier_and_beam" in r["recommended"]

    def test_very_high(self):
        r = table_foundation_selection("very_high")
        assert r["recommended"] == ["pier_and_beam"]
        assert r["void_space_mm"] == 150

    def test_medium(self):
        r = table_foundation_selection("medium")
        assert r["void_space_mm"] == 50

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown swell potential"):
            table_foundation_selection("extreme")


class TestGradeBeamVoidSpace:
    """table_grade_beam_void_space."""

    def test_very_low_no_void(self):
        r = table_grade_beam_void_space("very_low")
        assert r["void_space_mm"] == 0

    def test_medium(self):
        r = table_grade_beam_void_space("medium")
        assert r["void_space_mm"] == 50

    def test_high(self):
        r = table_grade_beam_void_space("high")
        assert r["void_space_mm"] == 100

    def test_very_high(self):
        r = table_grade_beam_void_space("very_high")
        assert r["void_space_mm"] == 150

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown swell potential"):
            table_grade_beam_void_space("moderate")

    def test_case_insensitive(self):
        r = table_grade_beam_void_space("HIGH")
        assert r["swell_potential"] == "high"
