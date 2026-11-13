"""REF-78 wave 1b: every lookup of DM 7.1, DM 7.2, the micropile manual
and GEC-6, 9, 10, 11 and 12 keeps the result convention
(geotech_references._units).

A dict result, and each row of a list of rows, carries a unit for every
number, ``printed_page`` and ``pdf_page_index``; each such lookup is called
once below with made-up inputs. A bare number, tuple, text or true/false
result is labelled in its docstring where the app reads it (the unit in
brackets in the first sentence of the Returns text, each element of a tuple
its own named entry, the page in the first 160 characters of the
References). A new dict lookup in these packages fails
``test_every_dict_lookup_has_one_call`` until it is added here.
"""

import inspect
import re

import pytest

from geotech_references import _units
from tests import _result_convention as rc

PACKAGES = ("dm7_1", "dm7_2", "micropile", "gec_9", "gec_10", "gec_6",
            "gec_11", "gec_12")
LOOKUPS = rc.lookups(PACKAGES)

# Bare results that are tuples (each element a named Returns entry) and
# text or true/false (a page, no unit).
TUPLES = {
    "dm7_2.chapter5.hansen_base_factors", "dm7_2.chapter5.hansen_depth_factors",
    "dm7_2.chapter5.hansen_ground_factors",
    "dm7_2.chapter5.hansen_inclination_factors",
    "dm7_2.chapter5.hansen_shape_factors",
    "dm7_2.chapter5.hansen_shape_factors_phi0",
    "dm7_2.chapter5.local_shear_terzaghi", "dm7_2.chapter5.local_shear_vesic",
    "dm7_2.chapter5.meyerhof_depth_factors",
    "dm7_2.chapter5.meyerhof_inclination_factors",
    "dm7_2.chapter5.meyerhof_shape_factors",
    "dm7_2.chapter5.terzaghi_shape_factors",
    "dm7_2.chapter7.first_order_second_moment",
    "dm7_2.chapter7.monte_carlo_simulation",
    "dm7_2.chapter7.point_estimate_method",
}
TEXT = {
    "dm7_1.chapter4.table_4_9_tunnel_behavior", "dm7_1.chapter6.laplace_check_2d",
    "dm7_2.chapter5.check_eccentricity_one_direction",
    "dm7_2.chapter5.check_eccentricity_two_directions",
    "dm7_2.chapter6.drag_force_check",
}

CALLS = {
    "dm7_1.chapter4.table_4_3_trench_fill": {
        "fill_type": "partially_compacted_moist_topsoil"},
    "dm7_1.chapter8.table_8_24_cbr_dcp": {"source": "gabr_2000"},
    "dm7_1.chapter8.table_8_6_stark_hussain": {
        "cf_range": "lt_20", "sigma_n_range": "50_kPa"},
    "dm7_1.chapter8.table_8_9_shansep_m": {"soil": "theoretical"},
    "dm7_2.chapter5.corner_bearing_pressure": {
        "B": 6.0, "L": 12.0, "e_B": 0.5, "e_L": 1.0, "q_gross": 10.0},
    "dm7_2.chapter5.figure_5_18a_Ncm_strip": {
        "H_over_B": 1.0, "cu2_over_cu1": 0.2},
    "dm7_2.chapter5.figure_5_18b_Ncm_circular": {
        "H_over_B": 1.0, "cu2_over_cu1": 0.2},
    "dm7_2.chapter6.table_6_36_clm": {
        "fixity": "free", "ratio": "Pt/Pc", "soil_type": "clay"},
    "dm7_2.chapter6.table_6_37_clm": {"fixity": "free", "soil_type": "clay"},
    "gec_10.figures.equation_10_21_rock_socket_side": {
        "C": 1.9, "qu_kpa": 1000.0},
    "gec_10.figures.equation_10_22_caving_rock_side": {
        "joint_condition": "closed", "qu_kpa": 5000.0, "rqd_pct": 100},
    "gec_10.tables.table_10_2_nc_base_clay": {"su_psf": 500},
    "gec_10.tables.table_11_1_p_multiplier": {
        "row_position": "lead", "spacing_over_d": 3.0},
    "gec_10.tables.table_11_2_group_efficiency_cohesionless": {
        "spacing_over_d": 2.5},
    "gec_10.tables.table_8_4_by_category": {"category": ""},
    "gec_10.tables.table_8_4_resistance_factor": {
        "method": "lateral_individual"},
    "gec_10.tables.table_9_1_lateral_resistance_factor": {
        "method": "individual"},
    "gec_11.figures.figure_4_10_kr_ka_ratio": {
        "depth_m": 0.0, "reinforcement_type": "geosynthetic"},
    "gec_11.tables.table_2_1_min_reinforcement_length": {"condition": ""},
    "gec_11.tables.table_2_2_min_embedment_depth": {"condition": ""},
    "gec_11.tables.table_3_11_pet_durability": {"product": ""},
    "gec_11.tables.table_3_1_select_fill_gradation": {},
    "gec_11.tables.table_3_3_electrochemical_steel": {},
    "gec_11.tables.table_3_4_electrochemical_geosynth": {"polymer": ""},
    "gec_11.tables.table_3_6_pullout_parameters": {"reinforcement": ""},
    "gec_11.tables.table_3_7_galvanization": {},
    "gec_11.tables.table_3_8_corrosion_rates": {"material": ""},
    "gec_11.tables.table_3_9_installation_damage": {"geosynthetic": ""},
    "gec_11.tables.table_4_1_load_combinations": {"limit_state": ""},
    "gec_11.tables.table_4_2_permanent_load_factors": {"load_type": ""},
    "gec_11.tables.table_4_4_traffic_surcharge": {"abutment_height_ft": 0.0},
    "gec_11.tables.table_4_5_external_resistance": {"failure_mode": ""},
    "gec_11.tables.table_4_6_bearing_capacity_factors": {"phi_deg": 0},
    "gec_11.tables.table_4_7_internal_resistance": {"reinforcement_type": ""},
    "gec_12.figures.figure_7_9_delta_phi_ratio": {
        "V": 0.3, "pile_type": "pipe_pile"},
    "gec_12.tables.table_7_10_brown_method_factors": {
        "installation": "impact", "loading": "compression",
        "soil_type": "clay_to_sand"},
    "gec_12.tables.table_7_16_soil_setup_factor": {"soil_type": "clay"},
    "gec_12.tables.table_7_3_static_analysis_methods": {"soil_type": ""},
    "gec_12.tables.table_7_8_api_design_parameters": {"delta_deg": 15},
    "gec_12.tables.table_7_9_beta_nt_coefficients": {"soil_type": "clay"},
    "gec_6.tables.table_4_1_spt_soil_properties": {
        "n_value": 2, "soil_type": "sand"},
    "gec_6.tables.table_5_10_fill_bearing_capacity": {"agency": ""},
    "gec_6.tables.table_5_13_poissons_ratio_rock": {"rock_type": "granite"},
    "gec_6.tables.table_5_14_youngs_modulus_rock": {"rock_type": "shale"},
    "gec_6.tables.table_5_15_friction_factor": {
        "interface": "clean_sound_rock"},
    "gec_6.tables.table_5_1_bearing_capacity_factors": {"phi": 35},
    "gec_6.tables.table_5_7_presumptive_bearing_rock": {
        "rock_type": "granite"},
    "gec_6.tables.table_5_9_rqd_bearing_capacity": {"rqd": 100},
    "gec_9.tables.table_4_1_lateral_resistance_factor": {
        "condition": "individual"},
    "gec_9.tables.table_7_1_p_multiplier": {
        "row_position": "lead", "spacing_over_b": 3.0},
    "gec_9.tables.table_a1_k_stiff_clay": {
        "ca_tsf": 0.75, "loading": "static"},
    "gec_9.tables.table_a2_epsilon50_stiff_clay": {"ca_tsf": 0.75},
    "gec_9.tables.table_a3_k_sand": {
        "condition": "submerged", "relative_density": "loose"},
    "micropile.figures.figure_5_23_limiting_lateral_modulus": {
        "section": "all"},
    "micropile.tables.table_2_1_classification": {
        "subtype": 1, "type_letter": "A"},
    "micropile.tables.table_4_2_rebar_properties": {
        "bar_size": "#14", "grade": 520},
    "micropile.tables.table_4_5_pipe_properties": {
        "od_mm": 139.7, "steel_type": "n80", "wall_mm": 0},
    "micropile.tables.table_5_11_fixity": {"fixity_pct": 0},
    "micropile.tables.table_5_12_elastic_modulus": {"soil_type": "clay_soft"},
    "micropile.tables.table_5_13_elastic_modulus_spt": {
        "n1_60": 20, "soil_type": "silts_sandy_silts"},
    "micropile.tables.table_5_3_alpha_bond": {
        "micropile_type": "B", "soil_type": "gravel"},
    "micropile.tables.table_5_4_group_efficiency": {"condition": ""},
    "micropile.tables.table_5_5_corrosion_criteria": {},
}


def returns_head(func):
    """The type the Returns section gives first (the app's reading)."""
    entries = rc.app_returns(func)["entries"]
    return entries[0][1].split(" ")[0] if entries else ""


BARE = sorted(n for n in LOOKUPS if n not in CALLS and ".plot_" not in n)


def test_every_dict_lookup_has_one_call():
    rows = {n for n, f in LOOKUPS.items() if returns_head(f) in ("dict", "list")}
    assert rows == set(CALLS)


def test_every_dict_lookup_is_labelled():
    assert [n for n in CALLS if not hasattr(LOOKUPS[n], "__result_units__")] == []


@pytest.mark.parametrize("name", sorted(CALLS))
def test_result_follows_the_convention(name):
    result = LOOKUPS[name](**CALLS[name])
    found = result if isinstance(result, list) else [result]
    assert found and all(isinstance(r, dict) for r in found)
    for row in found:
        assert rc.dict_result_problems(row) == []


def test_bare_kinds_are_bare():
    assert TUPLES | TEXT <= set(BARE)
    assert {returns_head(LOOKUPS[n]) for n in TEXT} == {"str", "bool"}


@pytest.mark.parametrize("name", BARE)
def test_bare_result_is_labelled_where_the_app_reads_it(name):
    kind = "tuple" if name in TUPLES else "text" if name in TEXT else "number"
    assert rc.bare_docstring_problems(LOOKUPS[name], kind) == []


def test_plots_are_the_only_lookups_left_out():
    assert sorted(n for n in LOOKUPS if ".plot_" in n) == [
        "dm7_1.chapter5.plot_figure_5_16", "dm7_1.chapter5.plot_figure_5_6_mu0",
        "dm7_1.chapter5.plot_figure_5_6_mu1", "dm7_1.chapter8.plot_figure_8_46",
        "dm7_2.chapter4.plot_figure_4_36", "dm7_2.chapter5.plot_figure_5_18a",
        "dm7_2.chapter5.plot_figure_5_18b"]


@pytest.mark.parametrize("name", sorted(
    n for n, f in LOOKUPS.items() if "unit_system" in rc.signature_names(f)))
def test_unit_system_is_documented(name):
    doc = inspect.getdoc(LOOKUPS[name])
    assert re.search(r"^unit_system : str, optional$", doc, re.M)
    assert "With unit_system='SI' the" in " ".join(doc.split())


def test_the_si_guards_are_these():
    assert sorted(n for n, f in LOOKUPS.items()
                  if "unit_system" in rc.signature_names(f)) == [
        "dm7_2.chapter2.scaled_distance",
        "dm7_2.chapter4.relative_flexibility_anchored_bulkhead",
        "dm7_2.chapter6.driving_stress_limit_concrete_tension",
        "dm7_2.chapter6.meyerhof_group_settlement",
        "gec_10.tables.table_10_2_nc_base_clay",
        "gec_11.tables.table_4_4_traffic_surcharge",
        "gec_12.figures.figure_7_10_to_13_kd",
        "gec_12.figures.figure_7_9_delta_phi_ratio"]


M2_TO_FT2 = 1.0 / _units.FT_M ** 2          # m^3/m to ft^3/ft


def test_kd_si_converts_the_displaced_volume():
    kd = LOOKUPS["gec_12.figures.figure_7_10_to_13_kd"]
    # made-up pile: 0.2 m^3/m displaced, 2.15 ft^3/ft
    assert kd(30.0, 0.2, unit_system="SI") == pytest.approx(
        kd(30.0, 0.2 * M2_TO_FT2))
    # the SI number read as ft^3/ft gives another Kd: the trap the guard closes
    assert kd(30.0, 0.2) != pytest.approx(kd(30.0, 0.2, unit_system="SI"))


@pytest.mark.parametrize("name, args, param, si_value, us_value", [
    ("gec_12.figures.figure_7_9_delta_phi_ratio", {"pile_type": "pipe_pile"},
     "V", 0.06, 0.06 * M2_TO_FT2),
    ("gec_10.tables.table_10_2_nc_base_clay", {}, "su_psf", 50.0,
     50.0e3 / _units.PSF_PA),
    ("gec_11.tables.table_4_4_traffic_surcharge", {}, "abutment_height_ft",
     6.0, 6.0 / _units.FT_M),
])
def test_si_dict_result_keeps_printed_units(name, args, param, si_value,
                                            us_value):
    func = LOOKUPS[name]
    si = func(**args, **{param: si_value}, unit_system="SI")
    us = func(**args, **{param: us_value})
    assert si["unit_system"] == "SI"
    assert si["converted_inputs"][param]["used"] == pytest.approx(us_value)
    assert {k: v for k, v in si.items()
            if k not in ("unit_system", "converted_inputs")} == us
    assert rc.dict_result_problems(si) == []


@pytest.mark.parametrize("name, printed, index", [
    # the cited pages were two out: the equations are on these (render)
    ("dm7_2.chapter6.alpha_method_unit_shaft_resistance", "414", 451),
    ("dm7_2.chapter6.rock_socket_unit_base_resistance", "430", 467),
])
def test_moved_pages(name, printed, index):
    assert f"printed p. {printed} (pdf_page_index {index})" in (
        rc.app_reference(LOOKUPS[name]))
