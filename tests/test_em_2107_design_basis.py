"""Tests for geotech_references.em_2107.design_basis (Chapter 3)."""

import pytest

from geotech_references.em_2107.design_basis import (
    table_3_1_target_reliability,
    load_category_from_return_period,
    aep_from_return_period,
)


class TestTable31TargetReliability:
    def test_all_four_combinations(self):
        assert table_3_1_target_reliability("normal", "redundant")["beta"] == 3.0
        assert table_3_1_target_reliability("normal", "single")["beta"] == 3.5
        assert table_3_1_target_reliability("critical", "redundant")["beta"] == 3.5
        assert table_3_1_target_reliability("critical", "single")["beta"] == 4.0

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            table_3_1_target_reliability("unknown", "single")


class TestLoadCategoryFromReturnPeriod:
    def test_usual_boundary(self):
        r = load_category_from_return_period(10.0, "normal")
        assert r["category"] == "usual"

    def test_unusual_normal(self):
        r = load_category_from_return_period(100.0, "normal")
        assert r["category"] == "unusual"

    def test_extreme_normal_beyond_300(self):
        r = load_category_from_return_period(301.0, "normal")
        assert r["category"] == "extreme"

    def test_unusual_critical_up_to_750(self):
        r = load_category_from_return_period(750.0, "critical")
        assert r["category"] == "unusual"

    def test_extreme_critical_beyond_750(self):
        r = load_category_from_return_period(751.0, "critical")
        assert r["category"] == "extreme"

    def test_aep_computed(self):
        r = load_category_from_return_period(10.0, "normal")
        assert r["aep"] == pytest.approx(0.10)

    def test_invalid_structure_class(self):
        with pytest.raises(ValueError):
            load_category_from_return_period(50.0, "bogus")

    def test_invalid_return_period(self):
        with pytest.raises(ValueError):
            load_category_from_return_period(0, "normal")


class TestAepFromReturnPeriod:
    def test_reciprocal(self):
        assert aep_from_return_period(300.0)["aep"] == pytest.approx(1.0 / 300.0)
