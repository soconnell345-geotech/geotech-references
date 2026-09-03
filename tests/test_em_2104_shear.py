"""Tests for geotech_references.em_2104.shear (Chapter 5).

Worked-example validation: Appendix D-6 (special straight member,
Vc = 134.9 kips) and Appendix D-7 (curved member, Vc = 192.1 kips).
"""

import pytest

from geotech_references.em_2104.shear import (
    shear_capacity_one_way_slab,
    shear_capacity_special_straight_member,
    shear_capacity_curved_member,
    table_g1_shear_coefficient,
)


class TestOneWaySlabShear:
    def test_zero_axial_load(self):
        r = shear_capacity_one_way_slab(fc_prime=4000, nu=0.0, ag=336, b=12, d=24)
        expected = 2 * (4000 ** 0.5) * 12 * 24
        assert r["vc"] == pytest.approx(expected)

    def test_axial_compression_increases_capacity(self):
        r0 = shear_capacity_one_way_slab(fc_prime=4000, nu=0.0, ag=336, b=12, d=24)
        r1 = shear_capacity_one_way_slab(fc_prime=4000, nu=50000.0, ag=336, b=12, d=24)
        assert r1["vc"] > r0["vc"]

    def test_si_units(self):
        r = shear_capacity_one_way_slab(fc_prime=28.0, nu=0.0, ag=100000.0,
                                         b=300.0, d=600.0, unit="si")
        expected = 0.17 * (28.0 ** 0.5) * 300.0 * 600.0
        assert r["vc"] == pytest.approx(expected)

    def test_bad_unit_raises(self):
        with pytest.raises(ValueError):
            shear_capacity_one_way_slab(4000, 0, 336, 12, 24, unit="bogus")


class TestSpecialStraightMember_AppendixD6:
    def test_matches_printed_vc(self):
        r = shear_capacity_special_straight_member(
            fc_prime=4000, ln=120, nu=31700, ag=336, b=12, d=24
        )
        assert r["ln_over_d"] == pytest.approx(5.0)
        assert r["vc"] == pytest.approx(134906, rel=1e-4)
        assert r["applicable"] is True

    def test_absolute_cap_not_governing(self):
        r = shear_capacity_special_straight_member(
            fc_prime=4000, ln=120, nu=31700, ag=336, b=12, d=24
        )
        assert r["vc_limit_abs"] == pytest.approx(182147, rel=1e-4)
        assert r["vc_governing"] == pytest.approx(r["vc"])

    def test_phi_vc_check_matches_example(self):
        # Vu = 52.5 kips <= phi*Vc = 0.75*134.9 = 101.2 kips (printed p. 89).
        r = shear_capacity_special_straight_member(
            fc_prime=4000, ln=120, nu=31700, ag=336, b=12, d=24
        )
        phi_vc = 0.75 * r["vc_governing"] / 1000.0  # lb -> kip
        assert phi_vc == pytest.approx(101.2, abs=0.1)
        assert 52.5 <= phi_vc

    def test_applicability_flags_out_of_range_ln_over_d(self):
        r = shear_capacity_special_straight_member(
            fc_prime=4000, ln=15, nu=0, ag=336, b=12, d=24
        )  # ln/d = 0.625 < 1.25
        assert r["applicable"] is False


class TestCurvedMember_AppendixD7:
    def test_matches_printed_vc(self):
        r = shear_capacity_curved_member(
            fc_prime=4000, nu=162500, ag=576, b=12, d=43.5
        )
        assert r["vc"] == pytest.approx(192058, rel=1e-4)

    def test_absolute_cap_not_governing(self):
        r = shear_capacity_curved_member(
            fc_prime=4000, nu=162500, ag=576, b=12, d=43.5
        )
        assert r["vc_limit_abs"] == pytest.approx(330142, rel=1e-4)
        assert r["vc_governing"] == pytest.approx(r["vc"])

    def test_phi_vc_check_matches_example(self):
        r = shear_capacity_curved_member(
            fc_prime=4000, nu=162500, ag=576, b=12, d=43.5
        )
        phi_vc = 0.75 * r["vc_governing"] / 1000.0
        assert phi_vc == pytest.approx(144.1, abs=0.1)

    def test_radius_applicability_check(self):
        r = shear_capacity_curved_member(
            fc_prime=4000, nu=162500, ag=576, b=12, d=43.5, radius=200.0,
        )
        assert r["applicable"] is True
        r2 = shear_capacity_curved_member(
            fc_prime=4000, nu=162500, ag=576, b=12, d=43.5, radius=50.0,
        )
        assert r2["applicable"] is False

    def test_radius_omitted_gives_none(self):
        r = shear_capacity_curved_member(fc_prime=4000, nu=162500, ag=576, b=12, d=43.5)
        assert r["applicable"] is None


class TestTableG1ShearCoefficient:
    def test_thin_section(self):
        assert table_g1_shear_coefficient(12)["coefficient"] == 1.54

    def test_thick_section_below_2(self):
        r = table_g1_shear_coefficient(120)
        assert r["coefficient"] == 0.61
        assert r["coefficient"] < 2.0  # illustrates why ACI 318-19's newer
        # coefficient was not adopted for thick RCHS members (Appendix G).

    def test_untabulated_thickness_raises(self):
        with pytest.raises(ValueError):
            table_g1_shear_coefficient(50)
