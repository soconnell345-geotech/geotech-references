"""Tests for geotech_references.gsa_collapse.applicability (Chapters 1-2).

Anchors are PRINTED VALUE (Section 2.3's FSL matrix and Section 2.1's
50%-area threshold) or SELF-CONSISTENCY checks.
"""

import pytest

from geotech_references.gsa_collapse.applicability import (
    fsl_applicability,
    counts_as_story,
    addition_triggers_existing_building_evaluation,
)


class TestFslApplicability:
    def test_fsl_i_never_applies(self):
        r = fsl_applicability("I")
        assert r["applies"] is False
        assert r["alternate_path_required"] is False
        assert r["redundancy_required"] is False

    def test_fsl_ii_never_applies(self):
        r = fsl_applicability("II", num_stories=50)
        assert r["applies"] is False

    def test_fsl_iii_below_threshold(self):
        r = fsl_applicability("III", num_stories=3)
        assert r["applies"] is False
        assert r["alternate_path_required"] is False
        assert r["redundancy_required"] is False

    def test_fsl_iii_at_threshold(self):
        r = fsl_applicability("III", num_stories=4)
        assert r["applies"] is True
        assert r["alternate_path_required"] is True
        assert r["redundancy_required"] is True

    def test_fsl_iv_above_threshold(self):
        r = fsl_applicability("IV", num_stories=10)
        assert r["applies"] is True
        assert r["redundancy_required"] is True

    def test_fsl_iii_iv_require_num_stories(self):
        with pytest.raises(ValueError):
            fsl_applicability("III")

    def test_fsl_v_always_applies_regardless_of_stories(self):
        r0 = fsl_applicability("V")
        r1 = fsl_applicability("V", num_stories=1)
        r50 = fsl_applicability("V", num_stories=50)
        for r in (r0, r1, r50):
            assert r["applies"] is True
            assert r["alternate_path_required"] is True

    def test_fsl_v_does_not_require_redundancy(self):
        # PRINTED VALUE: Section 2.3.3 / Commentary C2.3 -- FSL V's
        # whole-building removal scope already meets the redundancy intent.
        r = fsl_applicability("V")
        assert r["redundancy_required"] is False

    def test_invalid_fsl_raises(self):
        with pytest.raises(ValueError):
            fsl_applicability("VI")

    def test_case_insensitive(self):
        assert fsl_applicability("iii", num_stories=4)["fsl"] == "III"


class TestCountsAsStory:
    def test_mechanical_penthouse_excluded(self):
        assert counts_as_story(True)["counts_as_story"] is False

    def test_occupied_floor_counts(self):
        assert counts_as_story(False)["counts_as_story"] is True


class TestAdditionTriggersExistingBuildingEvaluation:
    def test_below_50_pct_never_triggers(self):
        r = addition_triggers_existing_building_evaluation(
            addition_gross_area=4000, existing_gross_area=10000,
            existing_undergoing_major_renovation=True,
        )
        assert r["area_ratio"] == pytest.approx(0.4)
        assert r["existing_portion_must_be_evaluated"] is False

    def test_50_pct_without_major_renovation_does_not_trigger(self):
        r = addition_triggers_existing_building_evaluation(
            addition_gross_area=6000, existing_gross_area=10000,
            existing_undergoing_major_renovation=False,
        )
        assert r["existing_portion_must_be_evaluated"] is False

    def test_50_pct_with_major_renovation_triggers(self):
        # PRINTED VALUE: Commentary C2.1's 50%-of-gross-area threshold,
        # AND concurrent major structural renovation, both required.
        r = addition_triggers_existing_building_evaluation(
            addition_gross_area=5000, existing_gross_area=10000,
            existing_undergoing_major_renovation=True,
        )
        assert r["area_ratio"] == pytest.approx(0.5)
        assert r["existing_portion_must_be_evaluated"] is True

    def test_above_50_pct_with_major_renovation_triggers(self):
        r = addition_triggers_existing_building_evaluation(
            addition_gross_area=12000, existing_gross_area=10000,
            existing_undergoing_major_renovation=True,
        )
        assert r["existing_portion_must_be_evaluated"] is True
