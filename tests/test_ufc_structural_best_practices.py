"""Tests for geotech_references.ufc_structural.best_practices (Appendix A)."""

import pytest

from geotech_references.ufc_structural.best_practices import (
    best_practice_guidance,
    list_best_practice_topics,
    shelf_angle_deflection_limit,
    masonry_veneer_ledge_offset,
    gable_bent_tie_rod_force_range,
    BEST_PRACTICE_TOPICS,
)


class TestBestPracticeGuidance:
    def test_building_drift_limits_topic(self):
        r = best_practice_guidance("building_drift_limits")
        assert "12.12" in r["guidance"]
        assert r["paragraph"] == "A-1.1"

    def test_gable_bent_footings_topic(self):
        r = best_practice_guidance("gable_bent_footings")
        assert "tie rod" in r["guidance"].lower()

    def test_unknown_topic_raises(self):
        with pytest.raises(ValueError):
            best_practice_guidance("nonexistent_topic")

    def test_list_topics_matches_dict(self):
        assert list_best_practice_topics() == sorted(BEST_PRACTICE_TOPICS)

    def test_every_topic_has_a_paragraph_citation(self):
        for topic in BEST_PRACTICE_TOPICS:
            r = best_practice_guidance(topic)
            assert r["paragraph"].startswith("A-")


class TestPrintedNumericCriteria:
    """Anchors: the handful of numeric values embedded in Appendix A's
    narrative (printed pp. 105-106)."""

    def test_shelf_angle_deflection_limit(self):
        assert shelf_angle_deflection_limit()["max_deflection_in"] == pytest.approx(1.0 / 16.0)

    def test_masonry_veneer_ledge_offset(self):
        r = masonry_veneer_ledge_offset()
        assert r["min_ledge_drop_in"] == 4
        assert r["min_ledge_width_fraction_of_veneer"] == pytest.approx(2.0 / 3.0)

    def test_gable_bent_tie_rod_force_range(self):
        r = gable_bent_tie_rod_force_range()
        assert r["min_force_kips"] == 40
        assert r["max_force_kips"] == 50
        assert r["min_force_kips"] < r["max_force_kips"]
