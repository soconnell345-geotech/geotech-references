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


class TestCFAAllowableCapacity:
    """cfa_allowable_capacity_kN."""

    def test_basic_sf2(self):
        r = cfa_allowable_capacity_kN(400.0)
        assert r["allowable_resistance_kN"] == pytest.approx(200.0, abs=0.1)

    def test_sf2_5(self):
        r = cfa_allowable_capacity_kN(500.0, safety_factor=2.5)
        assert r["allowable_resistance_kN"] == pytest.approx(200.0, abs=0.1)

    def test_returns_safety_factor(self):
        r = cfa_allowable_capacity_kN(300.0, safety_factor=2.0)
        assert r["safety_factor"] == 2.0

    def test_zero_resistance_raises(self):
        with pytest.raises(ValueError, match="ultimate_resistance_kN"):
            cfa_allowable_capacity_kN(0.0)

    def test_sf_below_1_raises(self):
        with pytest.raises(ValueError, match="safety_factor"):
            cfa_allowable_capacity_kN(300.0, safety_factor=0.5)


class TestCFAGroutVolumeFactor:
    """cfa_grout_volume_factor."""

    def test_1_2_gvf(self):
        r = cfa_grout_volume_factor(120.0, 100.0)
        assert r["grout_volume_factor"] == pytest.approx(1.2, abs=0.001)
        assert r["acceptable"] is True

    def test_below_1_not_acceptable(self):
        r = cfa_grout_volume_factor(90.0, 100.0)
        assert r["grout_volume_factor"] < 1.0
        assert r["acceptable"] is False

    def test_target_min(self):
        r = cfa_grout_volume_factor(100.0, 100.0)
        assert r["target_min"] == 1.15

    def test_zero_delivered_raises(self):
        with pytest.raises(ValueError, match="delivered_volume_L"):
            cfa_grout_volume_factor(0.0, 100.0)

    def test_zero_nominal_raises(self):
        with pytest.raises(ValueError, match="nominal_pile_volume_L"):
            cfa_grout_volume_factor(100.0, 0.0)


class TestTable54PMultiplier:
    """table_5_4_p_multiplier."""

    def test_lead_3b(self):
        r = table_5_4_p_multiplier("lead", 3.0)
        assert r["pm"] == pytest.approx(0.8, abs=0.01)

    def test_lead_5b(self):
        r = table_5_4_p_multiplier("lead", 5.0)
        assert r["pm"] == pytest.approx(1.0, abs=0.01)

    def test_2nd_row_3b(self):
        r = table_5_4_p_multiplier("2nd", 3.0)
        assert r["pm"] == pytest.approx(0.4, abs=0.01)

    def test_3rd_row_3b(self):
        r = table_5_4_p_multiplier("3rd", 3.0)
        assert r["pm"] == pytest.approx(0.3, abs=0.01)

    def test_3rd_row_5b(self):
        r = table_5_4_p_multiplier("3rd", 5.0)
        assert r["pm"] == pytest.approx(0.7, abs=0.01)

    def test_interpolation(self):
        r = table_5_4_p_multiplier("lead", 4.0)
        assert 0.8 < r["pm"] < 1.0

    def test_lead_higher_than_trailing(self):
        r1 = table_5_4_p_multiplier("lead", 3.0)
        r2 = table_5_4_p_multiplier("3rd", 3.0)
        assert r1["pm"] > r2["pm"]

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
        r = table_group_efficiency_cohesionless(8.0)
        assert r["group_efficiency"] == pytest.approx(1.0, abs=0.01)

    def test_increases_with_spacing(self):
        r1 = table_group_efficiency_cohesionless(3.0)
        r2 = table_group_efficiency_cohesionless(5.0)
        assert r2["group_efficiency"] > r1["group_efficiency"]

    def test_below_2_5_raises(self):
        with pytest.raises(ValueError, match="2.5"):
            table_group_efficiency_cohesionless(2.0)
