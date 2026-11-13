"""Tests for geotech_references.gec_8 (FHWA-HIF-07-03 GEC-8)."""

import pytest

from geotech_references.gec_8.equations import (
    dd_pile_side_resistance_MPa,
    cfa_allowable_capacity_kN,
    cfa_grout_volume_factor,
)
from geotech_references.gec_8.tables import (
    table_5_4_p_multiplier,
    table_group_efficiency_cohesionless,
)


class TestDDPileSideResistance:
    """dd_pile_side_resistance_MPa — NeSmith 2002."""

    def test_dirty_rounded_n20(self):
        r = dd_pile_side_resistance_MPa(20.0, "dirty_rounded")
        # fs = 0.005*20 + 0 = 0.10 MPa
        assert r["fs_MPa"] == pytest.approx(0.10, abs=0.001)

    def test_dirty_rounded_n20_not_limited(self):
        r = dd_pile_side_resistance_MPa(20.0, "dirty_rounded")
        assert r["fs_limited_MPa"] == r["fs_MPa"]

    def test_dirty_rounded_at_limit(self):
        # N=32: fs = 0.005*32 = 0.160 MPa — exactly at limit
        r = dd_pile_side_resistance_MPa(32.0, "dirty_rounded")
        assert r["fs_limited_MPa"] == pytest.approx(0.160, abs=0.001)

    def test_dirty_rounded_capped(self):
        # N=60 → capped to 50: fs = 0.005*50 = 0.25 → limited to 0.16
        r = dd_pile_side_resistance_MPa(60.0, "dirty_rounded")
        assert r["fs_limited_MPa"] == pytest.approx(0.16, abs=0.001)

    @pytest.mark.parametrize("soil, limit", [("dirty_rounded", 0.16),
                                             ("clean_angular", 0.21)])
    def test_above_n50_held_with_note(self, soil, limit):
        # Eq. 5.29 is printed for N <= 50 (GEC-8 p. 84); the printed limit
        # fs <= 0.16 / 0.21 MPa is reached at N = 32, so above 50 the
        # limited fs is that limit, said in note and out_of_range (REF-76).
        r = dd_pile_side_resistance_MPa(80.0, soil)
        assert r["fs_limited_MPa"] == pytest.approx(limit, abs=0.001)
        assert "N = 50" in r["out_of_range"] and "p. 84" in r["out_of_range"]
        assert "N = 50 is used" in r["note"]
        at_50 = dd_pile_side_resistance_MPa(50.0, soil)
        assert "out_of_range" not in at_50 and "note" not in at_50

    def test_clean_angular_n20(self):
        r = dd_pile_side_resistance_MPa(20.0, "clean_angular")
        # fs = 0.005*20 + 0.05 = 0.15 MPa
        assert r["fs_MPa"] == pytest.approx(0.15, abs=0.001)

    def test_clean_angular_ws(self):
        r = dd_pile_side_resistance_MPa(10.0, "clean_angular")
        assert r["ws_MPa"] == 0.05

    def test_clean_angular_limit(self):
        # N=50: fs = 0.005*50 + 0.05 = 0.30 → limited to 0.21
        r = dd_pile_side_resistance_MPa(50.0, "clean_angular")
        assert r["fs_limited_MPa"] == pytest.approx(0.21, abs=0.001)

    def test_higher_n_higher_fs(self):
        r1 = dd_pile_side_resistance_MPa(10.0, "dirty_rounded")
        r2 = dd_pile_side_resistance_MPa(30.0, "dirty_rounded")
        assert r2["fs_MPa"] > r1["fs_MPa"]

    def test_angular_higher_than_rounded(self):
        r1 = dd_pile_side_resistance_MPa(20.0, "dirty_rounded")
        r2 = dd_pile_side_resistance_MPa(20.0, "clean_angular")
        assert r2["fs_MPa"] > r1["fs_MPa"]

    def test_zero_n_raises(self):
        with pytest.raises(ValueError, match="spt_n must be > 0"):
            dd_pile_side_resistance_MPa(0.0)

    def test_invalid_soil_type_raises(self):
        with pytest.raises(ValueError, match="Unknown soil_type"):
            dd_pile_side_resistance_MPa(20.0, "gravel")

    def test_alias_clean(self):
        r = dd_pile_side_resistance_MPa(20.0, "clean")
        assert r["soil_type"] == "clean_angular"

    def test_print_conditions_carried(self):
        """FHWA-HIF-07-03 p. 83 (PDF page 106): N60 not depth corrected,
        cohesionless materials only; neither was in the result (review
        finding gec-42). Above N = 50 the result says N = 50 is used."""
        r = dd_pile_side_resistance_MPa(20.0, "dirty_rounded")
        assert "should not be depth corrected" in r["print_note"]
        assert "only be applied to cohesionless materials" in r["print_note"]
        assert "note" not in r
        assert "N = 50 is used" in dd_pile_side_resistance_MPa(60.0)["note"]


class TestCFAAllowableCapacity:
    """cfa_allowable_capacity_kN: GEC-8 Section 6.3.1, p. 138."""

    def test_default_sf_2_5(self):
        # p. 138: "a factor of safety of at least 2.5"
        r = cfa_allowable_capacity_kN(400.0)
        assert r["safety_factor"] == 2.5
        assert r["allowable_resistance_kN"] == pytest.approx(160.0, abs=0.1)
        assert r["minimum_safety_factor"] == 2.5
        assert r["meets_gec8_minimum"] is True

    def test_sf2_5(self):
        r = cfa_allowable_capacity_kN(500.0, safety_factor=2.5)
        assert r["allowable_resistance_kN"] == pytest.approx(200.0, abs=0.1)

    def test_sf2_without_conditions_flagged(self):
        r = cfa_allowable_capacity_kN(300.0, safety_factor=2.0)
        assert r["safety_factor"] == 2.0
        assert r["allowable_resistance_kN"] == pytest.approx(150.0, abs=0.1)
        assert r["meets_gec8_minimum"] is False
        assert "four conditions" in r["note"]

    def test_sf2_with_conditions_met(self):
        r = cfa_allowable_capacity_kN(300.0, safety_factor=2.0,
                                      sf_2_conditions_met=True)
        assert r["minimum_safety_factor"] == 2.0
        assert r["meets_gec8_minimum"] is True

    def test_below_2_flagged_even_with_conditions(self):
        r = cfa_allowable_capacity_kN(300.0, safety_factor=1.8,
                                      sf_2_conditions_met=True)
        assert r["meets_gec8_minimum"] is False
        assert "below 2.0" in r["note"]

    def test_cites_eq_6_1(self):
        r = cfa_allowable_capacity_kN(300.0)
        assert "6.3.1" in r["source"] and "Eq. 6.1" in r["source"]

    def test_zero_resistance_raises(self):
        with pytest.raises(ValueError, match="ultimate_resistance_kN"):
            cfa_allowable_capacity_kN(0.0)

    def test_sf_below_1_raises(self):
        with pytest.raises(ValueError, match="safety_factor"):
            cfa_allowable_capacity_kN(300.0, safety_factor=0.5)


class TestCFAGroutVolumeFactor:
    """cfa_grout_volume_factor: GEC-8 pp. 167, 215-216."""

    def test_1_2_gvf(self):
        r = cfa_grout_volume_factor(120.0, 100.0)
        assert r["grout_volume_factor"] == pytest.approx(1.2, abs=0.001)
        assert r["acceptable"] is True
        assert r["above_1_5"] is False

    def test_below_1_not_acceptable(self):
        r = cfa_grout_volume_factor(90.0, 100.0)
        assert r["grout_volume_factor"] < 1.0
        assert r["acceptable"] is False

    def test_between_1_and_1_15_not_acceptable(self):
        # p. 215 commentary: 1.15 "is considered to be a minimum value"
        r = cfa_grout_volume_factor(110.0, 100.0)
        assert r["acceptable"] is False
        assert "1.15" in r["basis"]

    def test_target_min(self):
        r = cfa_grout_volume_factor(100.0, 100.0)
        assert r["target_min"] == 1.15
        assert r["typical_range"] == [1.15, 1.2]

    def test_above_1_5_flagged(self):
        # p. 215: greater than 1.5 suggests soil mining
        r = cfa_grout_volume_factor(160.0, 100.0)
        assert r["above_1_5"] is True
        assert "soil mining" in r["note"]

    def test_target_band_inside(self):
        # p. 216: within 7.5% of the target volume factor
        r = cfa_grout_volume_factor(123.0, 100.0, target_factor=1.18)
        assert r["target_band"] == pytest.approx([1.0915, 1.2685], abs=0.001)
        assert r["acceptable"] is True

    def test_target_band_outside(self):
        r = cfa_grout_volume_factor(130.0, 100.0, target_factor=1.18)
        assert r["acceptable"] is False

    def test_negative_target_raises(self):
        with pytest.raises(ValueError, match="target_factor"):
            cfa_grout_volume_factor(120.0, 100.0, target_factor=-1.0)

    def test_zero_delivered_raises(self):
        with pytest.raises(ValueError, match="delivered_volume_L"):
            cfa_grout_volume_factor(0.0, 100.0)

    def test_zero_nominal_raises(self):
        with pytest.raises(ValueError, match="nominal_pile_volume_L"):
            cfa_grout_volume_factor(100.0, 0.0)


class TestTable54PMultiplier:
    """table_5_4_p_multiplier: GEC-8 Table 5.4, p. 112, as printed."""

    def test_m_dense_sand_lead_3b(self):
        r = table_5_4_p_multiplier("lead", 3.0, "medium_dense_sand")
        assert r["pm"] == pytest.approx(0.80, abs=0.001)
        assert r["rows"][0]["reference"] == "McVay et al. (1995)"

    def test_m_dense_sand_lead_5b(self):
        r = table_5_4_p_multiplier("lead", 5.0, "M. Dense Sand")
        assert r["pm"] == pytest.approx(1.0, abs=0.001)

    def test_loose_m_sand_rows_3b(self):
        pms = [table_5_4_p_multiplier(p, 3.0, "loose_medium_sand")["pm"]
               for p in ("lead", "2nd", "3rd")]
        assert pms == pytest.approx([0.65, 0.45, 0.35], abs=0.001)

    def test_loose_f_sand_3b(self):
        pms = [table_5_4_p_multiplier(p, 3.0, "loose_fine_sand")["pm"]
               for p in ("lead", "2nd", "3rd")]
        assert pms == pytest.approx([0.80, 0.70, 0.30], abs=0.001)

    def test_medium_clay_3b(self):
        r = table_5_4_p_multiplier("2nd", 3.0, "medium_clay")
        assert r["pm"] == pytest.approx(0.45, abs=0.001)
        assert r["rows"][0]["test_type"] == "Scale Model (Cyclic Load)"

    def test_stiff_clay_two_rows_lower_returned(self):
        r = table_5_4_p_multiplier("2nd", 3.0, "stiff_clay")
        assert [e["pm"] for e in r["rows"]] == pytest.approx([0.50, 0.60])
        assert r["pm"] == pytest.approx(0.50, abs=0.001)

    def test_interpolation_only_between_printed_rows(self):
        r = table_5_4_p_multiplier("lead", 4.0, "medium_dense_sand")
        assert r["pm"] == pytest.approx(0.90, abs=0.001)
        assert "linear" in r["basis"]

    def test_3b_only_soil_held_wider(self):
        r = table_5_4_p_multiplier("3rd", 5.0, "clayey_silt")
        assert r["pm"] == pytest.approx(0.40, abs=0.001)
        assert "held" in r["basis"]
        # REF-76: Table 5.4 (GEC-8 p. 112) prints Clayey Silt at 3B only; the
        # held row is said in note and out_of_range.
        assert "Clayey Silt" in r["out_of_range"]
        assert "3B for every soil" in r["out_of_range"]
        assert "safe" in r["note"]

    def test_printed_or_interpolated_has_no_out_of_range(self):
        for args in (("lead", 3.0, "clayey_silt"),
                     ("lead", 4.0, "medium_dense_sand"),
                     ("2nd", 5.0, "loose_medium_sand"),
                     ("3rd", 3.0)):
            r = table_5_4_p_multiplier(*args)
            assert "out_of_range" not in r and "note" not in r

    def test_sand_past_5b_held_with_note(self):
        r = table_5_4_p_multiplier("2nd", 8.0, "loose_medium_sand")
        assert r["pm"] == pytest.approx(0.85, abs=0.001)
        assert "Loose M. Sand" in r["out_of_range"]

    def test_3b_only_soil_not_1_0_at_5b(self):
        # The old summary returned an unprinted Pm = 1.0 at 5B for every soil.
        r = table_5_4_p_multiplier("lead", 5.0, "very_dense_sand")
        assert r["pm"] == pytest.approx(0.80, abs=0.001)

    def test_no_soil_lists_every_soil_and_gives_lowest(self):
        r = table_5_4_p_multiplier("lead", 3.0)
        # seven soils at 3B, Stiff Clay with two rows
        assert len(r["rows"]) == 8
        assert len({e["soil_type"] for e in r["rows"]}) == 7
        assert r["pm"] == pytest.approx(0.60, abs=0.001)
        assert "no soil type given" in r["basis"]

    def test_no_soil_wider_spacing_says_row_held(self):
        # No soil is printed at 6B: the basis says the widest printed row is
        # held, not that the table prints a value at this spacing.
        r = table_5_4_p_multiplier("2nd", 6.0)
        assert r["pm"] == pytest.approx(0.40, abs=0.001)
        assert "held" in r["basis"]
        assert "at this spacing" not in r["basis"]

    def test_lead_higher_than_trailing(self):
        r1 = table_5_4_p_multiplier("lead", 3.0, "very_dense_sand")
        r2 = table_5_4_p_multiplier("3rd", 3.0, "very_dense_sand")
        assert r1["pm"] > r2["pm"]

    def test_invalid_soil_raises(self):
        with pytest.raises(ValueError, match="Unknown soil_type"):
            table_5_4_p_multiplier("lead", 3.0, "gravel")

    def test_spacing_below_3_raises(self):
        with pytest.raises(ValueError, match="3.0"):
            table_5_4_p_multiplier("lead", 2.0)

    def test_invalid_row_raises(self):
        with pytest.raises(ValueError, match="Unknown row_position"):
            table_5_4_p_multiplier("5th", 3.0)


class TestGroupEfficiencyCohesionless:
    """table_group_efficiency_cohesionless."""

    def test_2_5d(self):
        r = table_group_efficiency_cohesionless(2.5)
        assert r["group_efficiency"] == pytest.approx(0.65, abs=0.01)

    def test_6d(self):
        r = table_group_efficiency_cohesionless(6.0)
        assert r["group_efficiency"] == pytest.approx(1.0, abs=0.01)

    def test_interpolation(self):
        r = table_group_efficiency_cohesionless(4.25)
        assert 0.65 < r["group_efficiency"] < 1.0

    def test_beyond_6d_caps_at_1(self):
        # GEC-8 p. 90: "eta = 1.0 for a center-to-center spacing of 6.0
        # diameters or more" (printed open-ended; REF-76 keeps it).
        r = table_group_efficiency_cohesionless(8.0)
        assert r["group_efficiency"] == pytest.approx(1.0, abs=0.01)

    def test_increases_with_spacing(self):
        r1 = table_group_efficiency_cohesionless(3.0)
        r2 = table_group_efficiency_cohesionless(5.0)
        assert r2["group_efficiency"] > r1["group_efficiency"]

    def test_below_2_5_raises(self):
        with pytest.raises(ValueError, match="2.5"):
            table_group_efficiency_cohesionless(2.0)
