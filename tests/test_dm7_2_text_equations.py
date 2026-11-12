"""DM 7.2 chapter text: equations corrected to the printed forms (app BACKLOG REF-79).

The 2026-11-10 reference review found stored equations in the DM 7.2
(UFC 3-220-20, 16 January 2025) chapter text that were not the printed ones
(text-01), entries filed under sections that do not print them (text-02) and
key points that misread a printed table (text-03). Each case below pins the
printed form, read from the rendered page; the PDF page is the printed page
plus 38. Numeric checks use made-up values or the manual's own example.
"""

import json
import math
from pathlib import Path

import pytest

import geotech_references
from geotech_references.dm7_2 import chapter2, chapter4, chapter5, chapter7

TEXT = Path(geotech_references.__file__).resolve().parent / "dm7_2" / "text"


def _sections(name):
    data = json.loads((TEXT / name).read_text(encoding="utf-8"))
    return {s["section_id"]: s for s in data["sections"]}


_CACHE = {}


def section(name, sid):
    if name not in _CACHE:
        _CACHE[name] = _sections(name)
    return _CACHE[name][sid]


def equation(name, sid, eid):
    hits = [e for e in section(name, sid)["equations"] if e["id"] == eid]
    assert len(hits) == 1, (name, sid, eid, [e["id"] for e in section(name, sid)["equations"]])
    return hits[0]


def filed_under(name, eid):
    return [sid for sid, s in _sections(name).items() for e in s["equations"] if e["id"] == eid]


# (file, section, where, printed text that must be there, stored text that must be gone)
# where: "body", "kp" (any key point) or an equation id (its description).
PRINTED = [
    # Eq. P-2, PDF p. 42 (printed 4): the consolidation stress subscript is 1,con
    ("prologue.json", "P-2.2.1", "Eq. P-2", "σ'1,con", "σ'con,1"),
    # Figure P-4 worked example, PDF p. 44: the c' line as printed
    ("prologue.json", "P-2.2.3", "body", "((1761 − 1011)/(4000 − 2000)) = 261 psf", "≈ 0 reported"),
    # Eq. 2-10, PDF p. 136 (printed 98): rho = q·γw/Δp
    ("chapter02.json", "2-6.2", "Eq. 2-10", "ρ = q·γw / Δp", "q/(γw"),
    ("chapter02.json", "2-6.2", "body", "ρ = q·γw / Δp", None),
    # Eq. 2-4, PDF p. 122: left side printed εb (prose says εh); kept and noted
    ("chapter02.json", "2-4.4.3", "Eq. 2-4", "printed εb", None),
    # Eq. 2-6, PDF p. 123 (printed 85): the printed piecewise form
    ("chapter02.json", "2-4.4.3", "Eq. 2-6", "0.75H ≤ di ≤ 1.5H", None),
    ("chapter02.json", "2-4.4.3", "body", "0.75H ≤ di ≤ 1.5H", "between 1.5 and 0.75"),
    # Eq. 3-2, PDF p. 147 (printed 109)
    ("chapter03.json", "3-2.1", "Eq. 3-2", "γd = γw·S / (w/100 + S/Gs)", None),
    # Eq. 3-7, PDF p. 162 (printed 124): denominator in printed order
    ("chapter03.json", "3-3.3.1", "Eq. 3-7", "(γdF·PC + GsC·γw·PF)", None),
    # Eq. 3-4, PDF p. 150 (printed 112): printed wopt − wfield; Table 3-11 note A noted
    ("chapter03.json", "3-5.1", "Eq. 3-4", "wopt − wfield", None),
    ("chapter03.json", "3-5.1", "Eq. 3-4", "Footnote A of T", None),
    # Eq. 4-5, PDF p. 216 (printed 178)
    ("chapter04.json", "4-2.2", "Eq. 4-5", "KA = 1/KP", None),
    # Eq. 4-12, PDF p. 229 (printed 191)
    ("chapter04.json", "4-3.2", "Eq. 4-12", "ln(Kp) = ln[(1 + sin φʹ)/(1 − sin φʹ)] · [1.443·(δ/φʹ)·sin φʹ + 1]", None),
    # Eq. 4-20, PDF p. 256 (printed 218)
    ("chapter04.json", "4-4.4.3.1", "Eq. 4-20", "Pw = (7/12) · kh · γw · H²", None),
    # Eq. 4-25, PDF p. 259 (printed 221): 2R/(3x0), stored 3R/(2x0) was 2.25 times the print
    ("chapter04.json", "4-5.1.1", "Eq. 4-25", "qmax = 2R / (3x0)", None),
    # 4-8.3.1 key point, Figure 4-54 note 3 (PDF p. 294-295): 80 % of the simple span moments
    ("chapter04.json", "4-8.3.1", "kp", "80", "80% pressure reduction"),
    # Table 4-7, PDF p. 302-304 (printed 264-266)
    ("chapter04.json", "4-9", "Table 4-7, Sliding at Base", "F = (W'tanδ + PP) / (Pw + PA)", None),
    ("chapter04.json", "4-9", "Table 4-7, Sliding in Weak Layer", "F = (W'tanφ' + c'B + PP) / (Pw + PA)", None),
    ("chapter04.json", "4-9", "Table 4-7, Overturning", "e = (Pw·yw + PA·yA − PP·yP) / W' − xW + B/2", None),
    ("chapter04.json", "4-9", "Table 4-7, Rotation", "ΣP = PW + PA − PP", None),
    ("chapter04.json", "4-9", "Table 4-7, Sheet Pile Interlock Tension (main cell)",
     "p = KA(γ(H − H3) + γ'(H3 − H/4)) + γw(H3 − H/4)", None),
    ("chapter04.json", "4-9", "Table 4-7, Slippage between Sheeting and Cell Fill",
     "F = [3B(PW + PA)tanδ + PP·HB] / (PW·H + PA·He)", None),
    ("chapter04.json", "4-9", "Table 4-7, Shear Failure on Centerline of Cell", "Q = 3M / (2B)", None),
    # Eq. 5-5 to 5-7, PDF p. 314-315 (printed 276-277): absolute values
    ("chapter05.json", "5-2.3", "body", "|eB| ≤ B/6  or  |eL| ≤ L/6", None),
    ("chapter05.json", "5-2.3", "body", "6|eB|/B + 6|eL|/L ≤ 1", "eB/B + eL/L ≤ 1/6"),
    ("chapter05.json", "5-2.3", "body", "(1 ± 6|eB|/B ± 6|eL|/L)", None),
    ("chapter05.json", "5-2.3", "Eq. 5-6", "6|eB|/B + 6|eL|/L ≤ 1", None),
    # Eq. 5-21, PDF p. 333 (printed 295): − ic
    ("chapter05.json", "5-3.3.3", "body", "(1 + sc + dc − ic − bc − gc)", "+ ic"),
    ("chapter05.json", "5-3.3.3", "Eq. 5-21", "(1 + sc + dc − ic − bc − gc)", "+ ic"),
    ("chapter05.json", "5-3.3.3", "kp", "(1 + sc + dc − ic − bc − gc)", "+ ic"),
    # Eq. 5-34, PDF p. 359 (printed 321), in 5-4.2.1
    ("chapter05.json", "5-4.2.1", "body", "λ = ⁴√[ ks·B / (4Ec·I) ]", None),
    ("chapter05.json", "5-4.2.1", "Eq. 5-34", "λ = ⁴√[ks·B/(4Ec·I)]", None),
    # Eq. 5-39, PDF p. 368 (printed 330)
    ("chapter05.json", "5-4.5.4", "body", "ksc = s·ks / (s + sc) = q / [ q·(B/Es)·µ0·µ1 + sc ]", None),
    ("chapter05.json", "5-4.5.4", "Eq. 5-39", "ksc = s·ks/(s + sc)", "q0"),
    # Table 5-22, PDF p. 397-398 (printed 359-360): eleven soil rows
    ("chapter05.json", "5-6.4", "kp", "eleven problem soil types", "seven"),
    ("chapter05.json", "5-6.4", "kp", "Municipal solid waste", None),
    # Eq. 6-53, PDF p. 486 (printed 448)
    ("chapter06.json", "6-5.8.4.3", "body",
     "Cεr · log( min(σʹz0 + Δσʹz, σʹp) / σʹz0 ) + Cεc · log( max(σʹz0 + Δσʹz, σʹp) / σʹp )", "- ...]"),
    ("chapter06.json", "6-5.8.4.3", "Eq. 6-53", "log(min(σʹz0 + Δσʹz, σʹp)/σʹz0)", None),
    # Eq. 6-60, 6-63, 6-64, PDF p. 495-496 (printed 457-458): square and cube roots
    ("chapter06.json", "6-6.4.1.1", "Eq. 6-60", "g = √[(Mt,ult + Pt,ult·(1.5·b + 0.5·f)) / (2.25·b·su*)]", "..."),
    ("chapter06.json", "6-6.4.1.1", "body", "(6-60)", None),
    ("chapter06.json", "6-6.4.1.2", "Eq. 6-63", "[2·(Pt,ult·Zmin + Mt,ult) / (b·γʹ·KP)]^(1/3)", None),
    ("chapter06.json", "6-6.4.1.2", "Eq. 6-64", "f = √[2·Pt,ult / (3·b·γʹ·KP)]", "..."),
    ("chapter06.json", "6-6.4.1.2", "body", "(6-64)", None),
    # Eq. 6-79, PDF p. 514 (printed 476): tcap = Pui/12 + 30
    ("chapter06.json", "6-7.3", "body", "tcap = Pui/12 + 30", "Pui/30 + 12"),
    ("chapter06.json", "6-7.3", "Eq. 6-79", "tcap = Pui/12 + 30", "Pui/30 + 12"),
    ("chapter06.json", "6-7.3", "kp", "tcap = Pui/12 + 30", "Pui/30 + 12"),
    # Eq. 7-6, PDF p. 568 (printed 530), and Eq. 7-16, PDF p. 587 (printed 549)
    ("chapter07.json", "7-4.1.1", "body", "σ = (HCV − LCV) / n   (7-6)", None),
    ("chapter07.json", "7-4.4", "body", "λ(y*) = − ln(1 − P(Y > y*)) / TR   (7-16)", None),
    ("chapter07.json", "7-4.4", "Eq. 7-16", "λ(y*) = −ln(1 − P(Y > y*)) / TR", "force-injected"),
    # Point estimate method, PDF p. 574 (printed 536): 2^n cases
    ("chapter07.json", "7-4.2.2", "kp", "2ⁿ", "2n "),
]


def _field(name, sid, where):
    s = section(name, sid)
    if where == "body":
        return s["body"]
    if where == "kp":
        return "\n".join(s["key_points"])
    return equation(name, sid, where)["description"]


@pytest.mark.parametrize("name,sid,where,printed,stored", PRINTED,
                         ids=[f"{n[:-5]}-{s}-{w}" for n, s, w, _, _ in PRINTED])
def test_printed_form_stored(name, sid, where, printed, stored):
    text = _field(name, sid, where)
    assert printed in text
    if stored is not None:
        assert stored not in text


@pytest.mark.parametrize("name,eid,sid", [
    ("chapter04.json", "Eq. 4-20", "4-4.4.3.1"),   # PDF p. 256; was an empty entry under 4-5.1.1
    ("chapter04.json", "Eq. 4-21", "4-4.4.3.2"),   # PDF p. 256
    ("chapter04.json", "Eq. 4-22", "4-4.4.3.2"),   # PDF p. 256
    ("chapter05.json", "Eq. 5-34", "5-4.2.1"),     # PDF p. 359, above the 5-4.3 heading
    ("chapter06.json", "Eq. 6-38", "6-5.5"),       # PDF p. 471, before the 6-5.6 heading
    ("chapter06.json", "Eq. 6-39", "6-5.5"),
    ("chapter07.json", "Eq. 7-6", "7-4.1.1"),      # PDF p. 568, before the 7-4.2 heading
    ("chapter07.json", "Eq. 7-16", "7-4.4"),       # PDF p. 587
])
def test_equation_filed_where_printed(name, eid, sid):
    assert filed_under(name, eid) == [sid]


def test_section_4_4_4_3_2_low_hydraulic_conductivity_soils():
    # PDF p. 256 (printed 218): a printed section missing from the text
    s = section("chapter04.json", "4-4.4.3.2")
    assert s["title"] == "Low Hydraulic Conductivity Soils"
    assert "(1 − ru)" in equation("chapter04.json", "4-4.4.3.2", "Eq. 4-21")["description"]
    assert "γ = (γsat − γw)(1 − ru)" in equation("chapter04.json", "4-4.4.3.2", "Eq. 4-22")["description"]


def test_table_4_7_entries_named_by_printed_rows():
    ids = [e["id"] for e in section("chapter04.json", "4-9")["equations"]]
    assert all(i.startswith("Table 4-7, ") for i in ids), ids
    assert len(ids) == 8
    assert not any("Pullout" in i for i in ids)


def test_no_empty_force_injected_entries():
    for path in sorted(TEXT.glob("*.json")):
        assert "force-injected" not in path.read_text(encoding="utf-8"), path.name


@pytest.mark.parametrize("name,sid,eid,func", [
    ("chapter02.json", "2-4.4.3", "Eq. 2-5", "movement_stiff_clay_sand"),
    ("chapter02.json", "2-5.3.1", "Eq. 2-7", "scaled_distance"),
    ("chapter02.json", "2-5.3.1", "Eq. 2-8", "peak_particle_velocity"),
    ("chapter04.json", "4-3.1", "Eq. 4-10", "coulomb_active_earth_pressure"),
    ("chapter04.json", "4-3.1", "Eq. 4-11", "coulomb_passive_earth_pressure"),
    ("chapter04.json", "4-3.2", "Eq. 4-12", "log_spiral_passive_coefficient"),
    ("chapter04.json", "4-4.4.1", "Eq. 4-16", "mononobe_okabe_active_force"),
    ("chapter04.json", "4-5.1.1", "Eq. 4-25", "base_pressure_max_triangular"),
    ("chapter05.json", "5-4.2.1", "Eq. 5-34", "foundation_stiffness_factor"),
    ("chapter07.json", "7-4.4", "Eq. 7-16", "rate_of_exceedance_from_probability"),
])
def test_implemented_in_names_the_equation_function(name, sid, eid, func):
    assert equation(name, sid, eid)["implemented_in"].rsplit(".", 1)[1] == func


# ---- the functions agree with the printed forms (made-up values) ----

def test_eq_2_10_function_matches_print():
    q, gamma_w, delta_p = 0.02, 9.81, 40.0
    assert chapter2.inverse_specific_resistance_sheet_piling(q, gamma_w, delta_p) == pytest.approx(
        q * gamma_w / delta_p)


def test_eq_4_25_function_matches_print():
    R, x0 = 300.0, 1.2
    assert chapter4.base_pressure_max_triangular(R, x0) == pytest.approx(2.0 * R / (3.0 * x0))


def test_eq_5_21_function_subtracts_ic():
    assert chapter5.hansen_correction_factor_c_phi0(sc=0.1, dc=0.2, ic=0.05, bc=0.0, gc=0.0) == pytest.approx(1.25)


def test_eq_5_34_function_matches_print():
    ks, B, Ec, I = 20000.0, 1.5, 2.5e7, 0.05
    assert chapter5.foundation_stiffness_factor(ks, B, Ec, I) == pytest.approx((ks * B / (4.0 * Ec * I)) ** 0.25)


def test_eq_5_39_function_matches_print():
    s, sc, ks = 0.02, 0.03, 15000.0
    assert chapter5.subgrade_modulus_time_dependent(s, sc, ks) == pytest.approx(s * ks / (s + sc))


def test_eq_7_16_manual_example():
    # PDF p. 587 (printed 549): 10 % in 50 years gives 2.1e-3 per year, R of 475 years
    lam = chapter7.rate_of_exceedance_from_probability(0.10, 50.0)
    assert lam == pytest.approx(2.1e-3, abs=0.05e-3)
    assert 1.0 / lam == pytest.approx(475.0, abs=1.0)


def test_eq_7_6_function_matches_print():
    assert chapter7.std_dev_from_range(42.0, 18.0) == pytest.approx((42.0 - 18.0) / 6.0)


def test_eq_6_79_printed_values():
    # PDF p. 514 (printed 476): no function implements Eq. 6-79; the printed form
    # gives 130 in. for Pui = 1,200 kips where the old text gave 52 in.
    body = section("chapter06.json", "6-7.3")["body"]
    assert "(in inches)" in body and "(in kips)" in body
    assert math.isclose(1200.0 / 12.0 + 30.0, 130.0)


def test_eq_6_79_not_coded():
    assert equation("chapter06.json", "6-7.3", "Eq. 6-79")["implemented_in"] is None


def test_5_3_6_2_applicability_printed_limits():
    # PDF p. 346-347 (printed 308-309): H/B >= 0.7 (soft on top), H/B > 3 (stiff on top)
    app = section("chapter05.json", "5-3.6.2")["applicability"]
    assert "H / B ≥ 0.7" in app and "H / B > 3" in app
    assert "within depth B" not in app


def test_5_6_2_2_floor_slab_condition_kept():
    # PDF p. 391 (printed 353)
    kps = section("chapter05.json", "5-6.2.2")["key_points"]
    assert any(k.startswith("Where heave of the floor slab is not a critical concern") for k in kps)


def test_7_4_2_4_printed_beta_kept_with_marked_check():
    # PDF p. 579 (printed 541) prints beta = 4.26 with Pu = 0.0001; kept, with a marked note
    from statistics import NormalDist
    s = section("chapter07.json", "7-4.2.4")
    assert "β = 4.26 (Pu = 0.0001)" in s["body"]
    assert "not printed" in s["body"]
    assert NormalDist().inv_cdf(1 - 1e-4) == pytest.approx(3.72, abs=0.005)
    assert NormalDist().cdf(-4.26) == pytest.approx(1e-5, rel=0.03)
