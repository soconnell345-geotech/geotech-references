"""REF-78 review fixes: SI calls equal the US call with every input converted
by hand (all values made up), the new exact factors, and aci_beta1's units."""

import pytest

from geotech_references import _units
from geotech_references.dm7_2 import chapter2, chapter4, chapter6
from geotech_references.em_2104 import flexure_axial as em_fa
from geotech_references.ufc_expansive import tables as expansive

FT = 0.3048
IN = 0.0254
LB = 0.45359237
PSI = LB * 9.80665 / IN ** 2          # Pa
KIP_N = 1000 * LB * 9.80665


def test_exact_factors():
    assert _units.from_si(LB, "kg", "lb") == pytest.approx(1.0, rel=1e-15)
    assert _units.from_si(25.4 ** 4 / 0.3048, "mm^4/m", "in^4/ft") == \
        pytest.approx(1.0, rel=1e-12)


def test_active_zone_depth_si_equals_us():
    us = expansive.table_active_zone_depth(depth_to_groundwater_ft=16.4042)
    si = expansive.table_active_zone_depth(
        depth_to_groundwater_ft=5.0, unit_system="SI")
    assert si["active_zone_depth_ft"] == pytest.approx(
        expansive.table_active_zone_depth(
            depth_to_groundwater_ft=5.0 / FT)["active_zone_depth_ft"])
    assert si["active_zone_depth_ft"] == pytest.approx(16.4042, rel=1e-4)
    assert us["active_zone_depth_ft"] == pytest.approx(16.4042)


def test_active_zone_depth_si_shaft_floor():
    # moist profile gives 10 ft; a 2.5 m shaft floors Xa at 3B = 24.6 ft
    us = expansive.table_active_zone_depth(
        profile="moist", shaft_base_diameter_ft=2.5 / FT)
    si = expansive.table_active_zone_depth(
        profile="moist", shaft_base_diameter_ft=2.5, unit_system="SI")
    assert si["active_zone_depth_ft"] == pytest.approx(
        us["active_zone_depth_ft"])
    assert si["active_zone_depth_ft"] == pytest.approx(3 * 2.5 / FT)


def test_scaled_distance():
    d, w = 30.0, 50.0
    us = chapter2.scaled_distance(d / FT, w / LB)
    assert chapter2.scaled_distance(d, w, unit_system="SI") == pytest.approx(us)
    assert chapter2.scaled_distance(100.0, 25.0) == pytest.approx(20.0)
    assert chapter2.scaled_distance(100.0, 25.0, 0.33) == \
        pytest.approx(100.0 / 25.0 ** 0.33)


def test_relative_flexibility():
    h, d, e, i = 3000.0, 2000.0, 200000.0, 5.0e7   # mm, mm, MPa, mm^4/m
    us = chapter4.relative_flexibility_anchored_bulkhead(
        h / (IN * 1000), d / (IN * 1000), e * 1e6 / PSI,
        i * 1e-12 / (IN ** 4 / FT))
    got = chapter4.relative_flexibility_anchored_bulkhead(
        h, d, e, i, unit_system="SI")
    assert got == pytest.approx(us, rel=1e-12)
    assert chapter4.relative_flexibility_anchored_bulkhead(
        100.0, 50.0, 29e6, 200.0) == pytest.approx(150.0 ** 4 / (29e6 * 200.0))


def test_driving_stress_limit_concrete_tension():
    fc, fpe = 40.0, 3.0   # MPa
    us = chapter6.driving_stress_limit_concrete_tension(
        1.0, fc * 1e6 / (1000 * PSI), fpe * 1e6 / (1000 * PSI))
    assert chapter6.driving_stress_limit_concrete_tension(
        1.0, fc, fpe, unit_system="SI") == pytest.approx(us)
    assert chapter6.driving_stress_limit_concrete_tension(
        1.0, 4.0, 1.0) == pytest.approx(0.095 * 2.0 + 1.0)


def test_meyerhof_group_settlement():
    q, b, l = 4000.0, 3.0, 6.0   # kN, m, m
    us = chapter6.meyerhof_group_settlement(
        q * 1000 / KIP_N, b / FT, l / FT, 20.0, 0.8)
    assert chapter6.meyerhof_group_settlement(
        q, b, l, 20.0, 0.8, unit_system="SI") == pytest.approx(us)
    assert chapter6.meyerhof_group_settlement(
        500.0, 10.0, 20.0, 25.0, 0.5) == pytest.approx(
            500.0 * 10.0 ** 0.5 / (10.0 * 20.0 * 25.0) * 0.5)


def test_aci_beta1_units():
    assert em_fa.aci_beta1(50, unit="MPa") == pytest.approx(0.6874, abs=1e-3)
    assert em_fa.aci_beta1(50, unit="MPa") == pytest.approx(
        em_fa.aci_beta1(50e6 / PSI / 1000))
    assert em_fa.aci_beta1(5000, unit="psi") == pytest.approx(0.80)
    assert em_fa.aci_beta1(5.0) == pytest.approx(0.80)
    with pytest.raises(ValueError, match="psi.*ksi.*MPa"):
        em_fa.aci_beta1(5, unit="kPa")
