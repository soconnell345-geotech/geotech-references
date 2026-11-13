"""REF-78: the optional ``unit_system="SI"`` guard on US-unit lookups, and the
shared vocabulary and page reading of geotech_references._units.

A US-unit equation or chart given an SI number inside its accepted range
returns a believable wrong answer (MR 50,000 meant as kPa reads as psi; a
200 mm slab reads as 200 in). With ``unit_system="SI"`` the named inputs are
converted exactly to the printed units first, the lookup runs as printed,
and the result stays in the printed units and lists each conversion. All
inputs below are made up.
"""

import copy
import inspect

import pytest

from geotech_references import _units
from geotech_references.aashto_1993 import equations as aashto
from geotech_references.em_2104 import design as em_design
from geotech_references.em_2104 import flexure_axial as em_fa
from geotech_references.fhwa_pavements import equations as fhwa
from geotech_references.ufc_concrete_practice import tables as concrete
from geotech_references.ufc_expansive import equations as expansive
from geotech_references.ufc_pavement import equations as ufc_pave
from geotech_references.ufc_stabilization import equations as stab

KPA_PER_PSI = 6.894757293168361     # exact: 0.45359237 kg * 9.80665 / 0.0254^2
KPA_PER_TSF = 2000 * 0.45359237 * 9.80665 / 0.3048 ** 2 / 1000


def printed_part(result):
    """The result without the two keys the SI guard adds."""
    return {k: v for k, v in result.items()
            if k not in ("unit_system", "converted_inputs")}


def same(a, b):
    """Equal, numbers to 1e-12 relative, at any depth."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return a == pytest.approx(b, rel=1e-12, abs=1e-12)
    return a == b


# ---------------------------------------------------------------- the traps

def test_flexible_sn_takes_mr_in_mpa():
    kw = dict(w18=5.0e6, zr=-1.645, so=0.35, delta_psi=1.9)
    si = aashto.flexible_sn_from_w18(mr_psi=50.0, unit_system="SI", **kw)
    us = aashto.flexible_sn_from_w18(mr_psi=50.0e3 / KPA_PER_PSI, **kw)
    assert si["sn"] == pytest.approx(us["sn"], rel=1e-12)
    assert si["converted_inputs"]["mr_psi"] == {
        "given": 50.0, "given_unit": "MPa",
        "used": pytest.approx(7251.886886, rel=1e-9), "used_unit": "psi"}
    assert si["unit_system"] == "SI"
    assert si["units"]["sn"] == us["units"]["sn"]
    # the trap: the same 50,000 read as psi gives a much thinner pavement
    trap = aashto.flexible_sn_from_w18(mr_psi=50.0e3, **kw)
    assert trap["sn"] < 0.7 * si["sn"]


def test_joint_spacing_takes_slab_in_mm():
    si = concrete.table_9_1_maximum_joint_spacing(
        200, facility_type="airfield", unit_system="SI")
    us = concrete.table_9_1_maximum_joint_spacing(
        200 / 25.4, facility_type="airfield")
    assert same(printed_part(si), us)
    assert si["converted_inputs"]["slab_thickness_in"]["used"] == \
        pytest.approx(7.874015748, rel=1e-9)


# ------------------------------------------------------- one per package

def test_ufc_pavement_overlay_in_mm():
    si = ufc_pave.rigid_overlay_fully_bonded(254.0, 152.4, unit_system="SI")
    us = ufc_pave.rigid_overlay_fully_bonded(10.0, 6.0)
    assert si["ho_in"] == pytest.approx(us["ho_in"], rel=1e-12)
    assert si["units"]["ho_in"] == "in"


def test_fhwa_bulk_stress_in_kpa():
    si = fhwa.granular_resilient_modulus_bulk_stress(
        k1=5000, k2=0.6, theta_psi=150.0, unit_system="SI")
    us = fhwa.granular_resilient_modulus_bulk_stress(
        k1=5000, k2=0.6, theta_psi=150.0 / KPA_PER_PSI)
    assert same(printed_part(si), us)


def test_concrete_weather_severity_in_mm_and_degc_days():
    si = concrete.table_3_1_weather_severity(
        avg_monthly_precip_in=50.8, air_freezing_index=300.0,
        unit_system="SI")
    us = concrete.table_3_1_weather_severity(
        avg_monthly_precip_in=2.0, air_freezing_index=540.0)
    assert same(printed_part(si), us)


def test_expansive_layers_in_m_and_kpa_and_input_left_alone():
    layers_si = [{"thickness_ft": 0.6096, "swell_index": 0.08,
                  "initial_void_ratio": 0.9,
                  "swell_pressure_tsf": 3.0 * KPA_PER_TSF,
                  "total_vertical_pressure_tsf": 0.5 * KPA_PER_TSF}]
    before = copy.deepcopy(layers_si)
    si = expansive.eq_5_8_consolidometer_heave(layers_si, unit_system="SI")
    layers_us = [{"thickness_ft": 2.0, "swell_index": 0.08,
                  "initial_void_ratio": 0.9, "swell_pressure_tsf": 3.0,
                  "total_vertical_pressure_tsf": 0.5}]
    us = expansive.eq_5_8_consolidometer_heave(layers_us)
    assert same(printed_part(si), us)
    assert layers_si == before
    assert set(si["converted_inputs"]) == {
        "layers[].thickness_ft", "layers[].swell_pressure_tsf",
        "layers[].total_vertical_pressure_tsf"}


def test_stabilized_thickness_in_mm():
    si = stab.equation_stabilized_equivalent_thickness(
        101.6, 1.3, unit_system="SI")
    us = stab.equation_stabilized_equivalent_thickness(4.0, 1.3)
    assert same(printed_part(si), us)


def test_em_2104_effective_depth_in_si():
    kd = 0.2
    si = em_design.minimum_effective_depth(
        200.0, 300.0, 28.0, kd, unit_system="SI")
    us = em_design.minimum_effective_depth(
        200.0 / (_units.LBF_N * _units.IN_M), 300.0 / 25.4,
        28.0 / KPA_PER_PSI, kd)
    assert si["dd"] == pytest.approx(us["dd"], rel=1e-12)
    assert si["units"]["dd"] == "in"


def test_beta1_takes_mpa_only_with_the_ksi_selector():
    assert em_fa.aci_beta1(28.0, unit_system="SI") == pytest.approx(
        em_fa.aci_beta1(28.0 / KPA_PER_PSI), rel=1e-12)
    with pytest.raises(ValueError):
        em_fa.aci_beta1(28.0, unit="psi", unit_system="SI")


# ------------------------------------------------------------ the guard

def test_guard_adds_a_keyword_only_parameter():
    p = inspect.signature(aashto.flexible_sn_from_w18).parameters["unit_system"]
    assert p.kind is inspect.Parameter.KEYWORD_ONLY
    assert p.default == "US"
    assert p.annotation is str


def test_us_default_result_is_unchanged():
    r = ufc_pave.rigid_overlay_fully_bonded(10.0, 6.0)
    assert "unit_system" not in r and "converted_inputs" not in r


def test_unknown_unit_system_is_refused():
    with pytest.raises(ValueError, match="unit_system"):
        ufc_pave.rigid_overlay_fully_bonded(10.0, 6.0, unit_system="metric")


def test_guard_refuses_a_function_with_its_own_unit_system():
    def f(x, unit_system="US"):
        return {"x": x}
    with pytest.raises(TypeError):
        _units.labelled({"x": "in"}, si={"x": ("mm", "in")})(f)


# ------------------------------------------------- conversions and pages

@pytest.mark.parametrize("value,si_unit,us_unit,expected", [
    (25.4, "mm", "in", 1.0),
    (0.3048, "m", "ft", 1.0),
    (KPA_PER_PSI, "kPa", "psi", 1.0),
    (KPA_PER_PSI, "MPa", "ksi", 1.0),
    (0.0, "degC", "degF", 32.0),
    (100.0, "degC", "degF", 212.0),
    (100.0, "degC-days", "degF-days", 180.0),
    ([25.4, 50.8], "mm", "in", [1.0, 2.0]),
])
def test_from_si_is_exact(value, si_unit, us_unit, expected):
    assert _units.from_si(value, si_unit, us_unit) == pytest.approx(
        expected, rel=1e-15)


def test_from_si_refuses_an_unknown_pair():
    with pytest.raises((KeyError, ValueError)):
        _units.from_si(1.0, "furlong", "in")


@pytest.mark.parametrize("reference,expected", [
    ("UFC 3-250-01, Table 19-2 (pdf_page_index 89, printed 70)", ("70", 89)),
    ("X, para 5-1b(4), printed p. 5-2 (pdf_page_index 28)", ("5-2", 28)),
    ("X, Sec 2.4 (pdf_page_index 134-135, printed II-45)",
     ("II-45", [134, 135])),
    ("UFC 3-250-11, Table 3-2, p.17", (None, None)),
    (None, (None, None)),
])
def test_page_from_reference(reference, expected):
    assert _units.page_from_reference(reference) == expected


def test_printed_from_reference():
    assert _units.printed_from_reference("UFC 3-250-11, Table 3-2, p.17") == "17"
    assert _units.printed_from_reference("no page here") is None


def test_numeric_keys_walk_nested_results():
    r = {"a": 1.0, "flag": True, "rows": [{"b": 2, "c": "x"}],
         "curve": {"10": 3.0}, "units": {"a": "in"}, "pdf_page_index": 4}
    assert _units.numeric_keys(r) == {"a", "b", "curve"}


@pytest.mark.parametrize("text,ok", [
    ("psi", True), ("percent", True), ("no unit printed", True),
    ("ft (or m)", True), ("banana", False), ("", False),
])
def test_is_unit(text, ok):
    assert _units.is_unit(text) is ok


def test_label_adds_units_and_pages_without_touching_the_source():
    table = {"k": 2.0, "reference": "X (pdf_page_index 9, printed 4)"}

    @_units.labelled({"k": "pci"})
    def f():
        return table
    r = f()
    assert r["units"] == {"k": "pci"}
    assert (r["printed_page"], r["pdf_page_index"]) == ("4", 9)
    assert "units" not in table


def test_label_gives_an_empty_units_map_when_nothing_is_a_number():
    @_units.labelled({}, printed_page="7", pdf_page_index=12)
    def f():
        return {"class": "F4"}
    assert f() == {"class": "F4", "units": {}, "printed_page": "7",
                   "pdf_page_index": 12}
