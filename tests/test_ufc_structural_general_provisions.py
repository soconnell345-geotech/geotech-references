"""Tests for geotech_references.ufc_structural.general_provisions (Chapter 1)."""

import pytest

from geotech_references.ufc_structural.general_provisions import (
    modification_action_definition,
    progressive_collapse_applicability,
    risk_category_v_note,
    cybersecurity_requirement,
)


class TestModificationActions:
    def test_replacement_definition(self):
        r = modification_action_definition("replacement")
        assert "delete" in r["definition"].lower()
        assert "replace it" in r["definition"].lower()

    def test_addition_definition(self):
        r = modification_action_definition("Addition")
        assert "add new section" in r["definition"].lower()

    def test_case_insensitive(self):
        assert modification_action_definition("SUPPLEMENT")["action"] == "supplement"

    def test_unknown_action_raises(self):
        with pytest.raises(ValueError):
            modification_action_definition("modification")

    def test_all_four_actions_defined(self):
        for action in ("addition", "deletion", "replacement", "supplement"):
            r = modification_action_definition(action)
            assert r["paragraph"] == "1-6"


class TestProgressiveCollapse:
    def test_points_to_ufc_4_023_03(self):
        r = progressive_collapse_applicability()
        assert r["governing_document"] == "UFC 4-023-03"
        assert "when required" in r["requirement"].lower()


class TestRiskCategoryV:
    def test_points_to_table_2_2_and_ufc_3_301_02(self):
        r = risk_category_v_note()
        assert r["risk_category_table"] == "Table 2-2"
        assert r["design_document"] == "UFC 3-301-02"
        assert "elastic" in r["note"].lower()


class TestCybersecurity:
    def test_points_to_ufc_4_010_06(self):
        r = cybersecurity_requirement()
        assert r["governing_document"] == "UFC 4-010-06"
