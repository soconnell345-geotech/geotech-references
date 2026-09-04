"""Tests for geotech_references.ufc_structural.risk_category_and_loads
(Chapter 2 Table 2-1/2-2, Appendix E Table E-1, Section 1609.3.1)."""

import pytest

from geotech_references.ufc_structural.risk_category_and_loads import (
    table_2_1_wind_deflection_limit,
    table_2_2_risk_category,
    table_2_2_note,
    wind_speed_conversion_asd,
    wind_speed_conversion_fastest_mile,
    nonpermanent_structure_wind_reduction_factor,
    vertical_ground_motion_threshold_check,
    table_e1_live_load,
    table_e1_note,
    list_table_e1_occupancies,
    TABLE_E1_LIVE_LOADS,
)


class TestTable21DeflectionLimits:
    """Anchors: printed Table 2-1 values (p. 10)."""

    def test_brick_veneer(self):
        assert table_2_1_wind_deflection_limit("brick_veneer")["deflection_limit"] == "L/600"

    def test_metal_vinyl_siding(self):
        r = table_2_1_wind_deflection_limit("metal_or_vinyl_siding_and_insulated_metal_panel")
        assert r["deflection_limit"] == "L/120"

    def test_stone_masonry_is_qualitative(self):
        r = table_2_1_wind_deflection_limit("stone_masonry")
        assert "supplier" in r["deflection_limit"].lower()

    def test_wind_load_factor(self):
        assert table_2_1_wind_deflection_limit("brick_veneer")["wind_load_factor"] == 0.42

    def test_unknown_cladding_raises(self):
        with pytest.raises(ValueError):
            table_2_1_wind_deflection_limit("aluminum_panel")


class TestTable22RiskCategory:
    """Anchors: printed Table 2-2 values (pp. 11-14)."""

    def test_rc_i_ie_1(self):
        assert table_2_2_risk_category("I")["seismic_factor_ie"] == 1.00

    def test_rc_iii_ie_1_25(self):
        r = table_2_2_risk_category("III")
        assert r["seismic_factor_ie"] == 1.25
        assert r["tsunami_factor_itsu"] == 1.25

    def test_rc_iv_ie_1_5(self):
        r = table_2_2_risk_category("IV")
        assert r["seismic_factor_ie"] == 1.50
        assert r["slr_scenario"] == "High (2065)"

    def test_rc_v_is_dod_addition_ie_1(self):
        # RC V has Ie=1.0 (elastic-design philosophy substitutes for a higher Ie)
        r = table_2_2_risk_category("V")
        assert r["seismic_factor_ie"] == 1.00
        assert r["slr_scenario"] == "Highest (2065)"
        assert "national strategic" in r["nature"].lower()

    def test_rc_i_tsunami_not_required(self):
        r = table_2_2_risk_category("I")
        assert r["tsunami_factor_itsu"] is None
        assert "not" in r["tsunami_note"].lower()

    def test_case_insensitive_and_unknown(self):
        assert table_2_2_risk_category("ii")["seismic_factor_ie"] == 1.00
        with pytest.raises(ValueError):
            table_2_2_risk_category("VI")

    def test_note_c_describes_rc_v(self):
        r = table_2_2_note("c")
        assert "national strategic" in r["text"].lower()

    def test_unknown_note_raises(self):
        with pytest.raises(ValueError):
            table_2_2_note("z")


class TestWindSpeedConversion:
    """Anchors: Eq 16-18a/16-18b algebraic identities."""

    def test_asd_conversion_matches_formula(self):
        v = 140.0
        r = wind_speed_conversion_asd(v)
        assert r["v_asd"] == pytest.approx((0.6 * v) ** 0.5)
        assert r["equation"] == "16-18a"

    def test_fastest_mile_conversion_matches_formula(self):
        v = 140.0
        r = wind_speed_conversion_fastest_mile(v)
        expected = ((0.6 * v) ** 0.5 - 10.5) / 1.05
        assert r["v_fm"] == pytest.approx(expected)
        assert r["equation"] == "16-18b"

    def test_asd_speed_less_than_basic_speed(self):
        # sqrt(0.6*V) < V for any positive V > 0.6
        r = wind_speed_conversion_asd(120.0)
        assert r["v_asd"] < 120.0

    def test_nonpermanent_reduction_factor(self):
        assert nonpermanent_structure_wind_reduction_factor()["reduction_factor"] == 0.78


class TestVerticalGroundMotionThreshold:
    """Anchors: paragraph 1605.1.2 SDS > 0.6g threshold."""

    def test_above_threshold_triggers(self):
        r = vertical_ground_motion_threshold_check(0.75)
        assert r["triggers_additional_combinations"] is True
        assert r["threshold"] == 0.6

    def test_at_threshold_does_not_trigger(self):
        # strictly greater-than per the printed provision
        r = vertical_ground_motion_threshold_check(0.6)
        assert r["triggers_additional_combinations"] is False

    def test_below_threshold_does_not_trigger(self):
        r = vertical_ground_motion_threshold_check(0.4)
        assert r["triggers_additional_combinations"] is False

    def test_sensitive_member_lists_nonempty(self):
        r = vertical_ground_motion_threshold_check(0.7)
        assert len(r["sensitive_building_members"]) == 6
        assert len(r["sensitive_nonbuilding_members"]) == 2


class TestTableE1LiveLoads:
    """Anchors: printed Table E-1 values (pp. 153-159)."""

    def test_office_offices(self):
        r = table_e1_live_load("office_offices")
        assert r["uniform_psf"] == 50
        assert r["uniform_kpa"] == 2.4
        assert r["concentrated_lb"] == 2000

    def test_hospital_patient_rooms(self):
        r = table_e1_live_load("hospitals_patient_rooms")
        assert r["uniform_psf"] == 40
        assert r["concentrated_lb"] == 1000

    def test_storage_warehouse_pipe_and_metal(self):
        # a large, distinctive value -- good anchor against silent transcription errors
        r = table_e1_live_load("storage_warehouses_pipe_and_metal")
        assert r["uniform_psf"] == 1000
        assert r["uniform_kpa"] == 48

    def test_ammunition_storage_is_military_added(self):
        r = table_e1_live_load("ammunition_storage_torpedo_one_story")
        assert r["military_added"] is True
        assert r["uniform_psf"] == 350

    def test_office_offices_not_military_added(self):
        r = table_e1_live_load("office_offices")
        assert r.get("military_added") is None

    def test_pointer_row_has_no_numeric_load(self):
        r = table_e1_live_load("vehicle_barriers")
        assert "1607.11" in r["pointer"]
        assert "uniform_psf" not in r

    def test_unknown_occupancy_raises(self):
        with pytest.raises(ValueError):
            table_e1_live_load("nonexistent_occupancy")

    def test_note_d_no_reduction(self):
        r = table_e1_note("d")
        assert "not permitted" in r["text"].lower()

    def test_list_occupancies_nonempty(self):
        occupancies = list_table_e1_occupancies()
        assert len(occupancies) == len(TABLE_E1_LIVE_LOADS)
        assert "office_offices" in occupancies

    def test_list_military_added_only(self):
        military = list_table_e1_occupancies(military_added_only=True)
        assert len(military) > 0
        assert all(TABLE_E1_LIVE_LOADS[k].get("military_added") for k in military)
        assert "office_offices" not in military

    def test_all_rows_have_at_least_one_load_or_pointer(self):
        # self-consistency: every row is either a numeric load row or a pointer row
        for key, row in TABLE_E1_LIVE_LOADS.items():
            has_load = any(k in row for k in ("uniform_psf", "concentrated_lb", "concentrated_pointer"))
            has_pointer = "pointer" in row
            assert has_load or has_pointer, f"{key} has neither a load value nor a pointer"
