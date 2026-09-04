"""Tests for geotech_references.wood_handbook.mechanical_properties
(Chapter 5 mechanical properties of wood)."""

import pytest

from geotech_references.wood_handbook.mechanical_properties import (
    TABLE_5_3_PROPERTIES,
    table_5_3_mechanical_properties,
    table_5_13_intersection_mc,
    adjust_property_for_moisture_content,
    table_5_15_temperature_effect,
    table_5_16_temperature_adjustment,
)


class TestTable53Properties:
    def test_douglas_fir_coast_12pct(self):
        row = table_5_3_mechanical_properties("douglas-fir, coast", "12")
        assert row["sg"] == 0.48
        assert row["mor_kpa"] == 85000
        assert row["moe_mpa"] == 13400

    def test_douglas_fir_coast_green(self):
        row = table_5_3_mechanical_properties("douglas-fir, coast", "green")
        assert row["sg"] == 0.45
        assert row["mor_kpa"] == 53000

    def test_default_moisture_condition_is_12pct(self):
        row = table_5_3_mechanical_properties("pine, loblolly")
        assert row["moisture_condition"] == "12"

    def test_species_subset_covers_expected_groups(self):
        # Southern Pine group constituents present
        for sp in ["pine, loblolly", "pine, longleaf", "pine, shortleaf", "pine, slash"]:
            assert sp in TABLE_5_3_PROPERTIES
        # Hem-Fir group constituents present
        for sp in ["hemlock, western", "fir, california red", "fir, grand",
                   "fir, noble", "fir, pacific silver", "fir, white"]:
            assert sp in TABLE_5_3_PROPERTIES
        # SPF group constituents present
        for sp in ["spruce, engelmann", "pine, lodgepole", "pine, jack", "fir, subalpine"]:
            assert sp in TABLE_5_3_PROPERTIES

    def test_missing_value_is_none(self):
        # Fir, subalpine has no printed work-to-max-load / impact bending value
        row = table_5_3_mechanical_properties("fir, subalpine", "green")
        assert row["wml_kj_m3"] is None

    def test_unknown_species_raises(self):
        with pytest.raises(ValueError):
            table_5_3_mechanical_properties("not a species")

    def test_invalid_moisture_condition_raises(self):
        with pytest.raises(ValueError):
            table_5_3_mechanical_properties("douglas-fir, coast", "15")


class TestTable513AndMoistureAdjustment:
    def test_douglas_fir_mp_tabulated(self):
        row = table_5_13_intersection_mc("douglas-fir")
        assert row["mp_pct"] == 24
        assert row["is_tabulated"] is True

    def test_default_mp_for_untabulated_species(self):
        row = table_5_13_intersection_mc("pine, lodgepole")
        assert row["mp_pct"] == 25
        assert row["is_tabulated"] is False

    def test_white_ash_worked_example(self):
        # Printed worked example (p. 5-34): white ash MOR at 8% MC.
        # P12=103,000 kPa, Pg=66,000 kPa, Mp=24 -> P8 = 119,500 kPa
        result = adjust_property_for_moisture_content(
            p12=103000, pg=66000, moisture_content_pct=8, mp_pct=24
        )
        assert result["property_value"] == pytest.approx(119500, rel=0.002)

    def test_property_at_12pct_returns_p12(self):
        result = adjust_property_for_moisture_content(
            p12=85000, pg=53000, moisture_content_pct=12, mp_pct=24
        )
        assert result["property_value"] == pytest.approx(85000)

    def test_property_increases_as_moisture_decreases(self):
        # Strength should increase as MC drops below 12%, toward Mp
        lower = adjust_property_for_moisture_content(103000, 66000, 10, 24)["property_value"]
        higher = adjust_property_for_moisture_content(103000, 66000, 6, 24)["property_value"]
        assert higher > lower


class TestTable515TemperatureEffect:
    def test_bending_strength_above_fsp(self):
        row = table_5_15_temperature_effect("bending_strength", ">fsp")
        assert row["change_at_minus50c_pct"] == 110
        assert row["change_at_plus50c_pct"] == -25

    def test_moe_perpendicular_12pct(self):
        row = table_5_15_temperature_effect("moe_perpendicular", "12")
        assert row["change_at_minus50c_pct"] is None
        assert row["change_at_plus50c_pct"] == -35

    def test_unknown_combination_raises(self):
        with pytest.raises(ValueError):
            table_5_15_temperature_effect("bending_strength", "999")


class TestTable516TemperatureAdjustment:
    def test_moe_at_70f_gives_zero_change(self):
        # P70 defined at 21 degC (70 degF); the printed dry-MOE row should
        # give ~0% change at exactly 70 degF (within the fitted quadratic).
        result = table_5_16_temperature_adjustment("moe", "all", "12", temp_f=70.0)
        assert result["percent_change"] == pytest.approx(0.0, abs=1.0)

    def test_select_structural_mor_dry_range_is_flat(self):
        result = table_5_16_temperature_adjustment("mor", "select structural", "12", temp_f=50.0)
        assert result["percent_change"] == pytest.approx(0.0)

    def test_out_of_range_temperature_raises(self):
        with pytest.raises(ValueError):
            table_5_16_temperature_adjustment("moe", "all", "12", temp_f=500.0)

    def test_unknown_combination_raises(self):
        with pytest.raises(ValueError):
            table_5_16_temperature_adjustment("mor", "clear wood", "12", temp_f=70.0)
