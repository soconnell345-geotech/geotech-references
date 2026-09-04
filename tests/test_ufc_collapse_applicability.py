"""Tests for geotech_references.ufc_collapse.applicability (Chapters 1-2).

All anchors are PRINTED TABLE / PRINTED VALUE (Tables 2-1/2-2 and Chapter
1's narrative thresholds) or SELF-CONSISTENCY checks.
"""

import pytest

from geotech_references.ufc_collapse.applicability import (
    story_count_threshold,
    is_story,
    partial_occupancy_threshold,
    table_2_1_risk_category,
    table_2_2_design_requirements,
    rc4_tie_force_minimum_exempt,
)


class TestStoryThreshold:
    def test_three_stories_mandatory_new_construction(self):
        r = story_count_threshold()
        assert r["minimum_stories"] == 3
        assert r["new_construction_mandatory"] is True
        assert r["existing_construction_mandatory"] is False

    def test_is_story_occupied(self):
        assert is_story(True)["counts_as_story"] is True
        assert is_story(False)["counts_as_story"] is False

    def test_partial_occupancy_25_pct(self):
        r = partial_occupancy_threshold()
        assert r["occupancy_threshold_pct"] == 25


class TestTable21RiskCategory:
    def test_all_four_categories_defined(self):
        for rc in ("I", "II", "III", "IV"):
            r = table_2_1_risk_category(rc)
            assert r["table"] == "2-1"
            assert "nature_of_occupancy" in r

    def test_rc_iv_covers_both_ufc_3_301_01_iv_and_v(self):
        # PRINTED VALUE: progressive-collapse RC IV maps to BOTH
        # UFC 3-301-01 Risk Category IV and V.
        r = table_2_1_risk_category("IV")
        assert "Risk Category V" in r["nature_of_occupancy"]

    def test_unknown_category_raises(self):
        with pytest.raises(ValueError):
            table_2_1_risk_category("V")

    def test_case_insensitive(self):
        assert table_2_1_risk_category("ii")["risk_category"] == "II"


class TestTable22DesignRequirements:
    def test_rc_i_no_requirements(self):
        r = table_2_2_design_requirements("I")
        assert r["methods"] == []

    def test_rc_ii_two_options(self):
        r = table_2_2_design_requirements("II")
        assert ["TF", "ELR"] in r["methods"]
        assert ["AP"] in r["methods"]

    def test_rc_iii_ap_and_elr(self):
        r = table_2_2_design_requirements("III")
        assert r["methods"] == [["AP", "ELR"]]

    def test_rc_iv_all_three(self):
        r = table_2_2_design_requirements("IV")
        assert r["methods"] == [["TF", "AP", "ELR"]]

    def test_unknown_category_raises(self):
        with pytest.raises(ValueError):
            table_2_2_design_requirements("V")


class TestRc4TieForceMinimumExempt:
    def test_ufc_3_301_01_rc_iv_may_be_exempted(self):
        # PRINTED VALUE: Table 2-2 Footnote A
        r = rc4_tie_force_minimum_exempt("IV")
        assert r["minimum_requirements_may_be_exempted"] is True

    def test_ufc_3_301_01_rc_v_remains_mandatory(self):
        r = rc4_tie_force_minimum_exempt("V")
        assert r["minimum_requirements_may_be_exempted"] is False

    def test_invalid_category_raises(self):
        with pytest.raises(ValueError):
            rc4_tie_force_minimum_exempt("III")
