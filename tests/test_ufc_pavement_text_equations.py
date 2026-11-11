"""UFC 3-250-01 (2016) chapter text: the equations, factors and limits as printed.

Pins the text corrected against the rendered pages of
docs/ufc_3_250_01_2016.pdf (build of 2026-11-10, app BACKLOG REF-83).
Printed page = PDF page - 20. Each assertion names the page it was read from.
Where the page prints a slip, the text keeps what is printed and says so;
those notes are pinned too, so a later edit cannot silently "fix" them.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from geotech_references._retrieval import retrieve_section

REF = "ufc_pavement"
TEXT_DIR = Path(__file__).resolve().parents[1] / "geotech_references" / REF / "text"


def sec(sid: str) -> dict:
    return retrieve_section(REF, sid)


def eq(sid: str, eid: str) -> str:
    hits = [e["description"] for e in sec(sid)["equations"] if e.get("id") == eid]
    assert hits, f"{eid} not in {sid}"
    return hits[0]


def norm(text: str) -> str:
    return re.sub(r"\s+", "", text)


def all_sections():
    for f in sorted(TEXT_DIR.glob("chapter*.json")):
        for s in json.loads(f.read_text(encoding="utf-8"))["sections"]:
            yield f.name, s


# --- equations, as printed ---------------------------------------------------

def test_eq_13_1_stabilized_foundation():
    # PDF p. 58 (printed 38)
    assert "ho=[hd^1.4-(0.0063*Ef^(1/3)*hs)^1.4]^(1/1.4)" in norm(eq("13-4", "Eq. 13-1"))


@pytest.mark.parametrize("eid, form", [
    ("Eq. 15-1", "ho=hd-hE"),
    ("Eq. 15-2", "ho=[hd^1.4-C*((hd/he)*hE)^1.4]^(1/1.4)"),
    ("Eq. 15-3", "ho=sqrt[hd^2-C*((hd/he)*hE)^2]"),
])
def test_rigid_overlay_equations(eid, form):
    # PDF p. 66 (printed 46)
    assert form in norm(eq("15-4.2.1", eid))


def test_eq_15_4_and_its_he_note():
    # PDF p. 69 (printed 49): the definition says "he", the equation prints hE
    assert "to=3.0*(F*hd-C*hE)" in norm(eq("15-7.2", "Eq. 15-4"))
    body = sec("15-7.2")["body"]
    assert "the factor he represents" in body
    assert "differ on the page" in body


def test_eq_17_1_leading_zero():
    # PDF p. 82 (printed 62): 0.00047, rendered at 250 dpi
    assert "L=[0.00047*hr*(fs*S)^2]^(1/3)" in norm(eq("17-1.4", "Eq. 17-1"))
    assert "L=[0.00047*hr*(fs*S)^2]^(1/3)" in norm(sec("17-1.4")["summary"])


def test_eq_20_3_prints_one_minus_e():
    # PDF p. 113 (printed 93)
    assert "(1-e)" in eq("20-2.2.1", "Eq. 20-3")


def test_eq_20_4_effective_porosity():
    # PDF p. 114 (printed 94)
    assert "ne=1-[gamma_d/(Gs*gamma_w)]*(1+Gs*We)" in norm(eq("20-2.2.3", "Eq. 20-4"))


@pytest.mark.parametrize("eid, form", [
    ("Eq. 20-6", "qs=ne*h"),
    ("Eq. 20-7", "qs=0.85*ne*h"),
    ("Eq. 20-8", "qd=(t*k*i*h)/(2*L)"),
    ("Eq. 20-9", "q=0.85*ne*h+(t*k*i*h)/(2*L)"),
])
def test_drainage_layer_capacity(eid, form):
    # PDF pp. 116-117 (printed 96-97)
    assert form in norm(eq("20-2.3.4", eid))


@pytest.mark.parametrize("eid, form", [
    ("Eq. 20-10", "T50=ne*D^2/(2*k*Ho)"),
    ("Eq. 20-11", "T50=ne*D/(2*i*k)"),
    ("Eq. 20-12", "T85=ne*D/(i*k)"),
])
def test_time_for_drainage(eid, form):
    # PDF pp. 117-118 (printed 97-98)
    assert form in norm(eq("20-2.3.5", eid))


def test_eq_20_13_printed_form():
    # PDF p. 119 (printed 99): L = Lt * sqrt(it^2 + ie^2) / it
    assert "L=Lt*sqrt(it^2+ie^2)/it" in norm(eq("20-2.3.6", "Eq. 20-13"))
    assert "L=Lt*sqrt(it^2+ie^2)/it" in norm(sec("20-2.3.6")["body"])
    assert "i=sqrt(it^2+ie^2)" in norm(eq("20-2.3.6", "Eq. 20-14"))


def test_eq_20_15_16_constants_and_unit_note():
    # PDF p. 126 (printed 106): the two printed constants differ by about 10x once converted
    assert "k=217.5*D10^1.478*n^6.654/P200^0.597" in norm(eq("20-3.3.6", "Eq. 20-15"))
    assert "k=6.214e5*D10^1.478*n^6.654/P200^0.597" in norm(eq("20-3.3.6", "Eq. 20-16"))
    body = sec("20-3.3.6")["body"]
    assert "factor of about 10" in body
    assert "no paragraph numbered 20-3.3.6" in body
    # the arithmetic behind the note: 1 mm/s = 86400 / 304.8 ft/day
    assert 217.5 * 86400 / 304.8 == pytest.approx(6.165e4, rel=1e-3)


def test_drainage_layer_thickness_is_under_20_3_4_3():
    # PDF p. 127 (printed 107): the thickness paragraph and Eqs. 20-17/20-18 are 20-3.4.3
    assert "H=2*F*R*L*t/((1.7*ne*L)+(k*i*t))" in norm(eq("20-3.4.3", "Eq. 20-17"))
    assert "H=F*R*t/(0.85*ne)" in norm(eq("20-3.4.3", "Eq. 20-18"))
    assert sec("20-3.4.1")["equations"] == []
    assert "Equation 20-17" not in sec("20-3.4.1")["body"]
    # the page says "equation 7-17"; kept as printed with a note
    assert "equation 7-17 [as printed" in sec("20-3.4.3")["body"]
    # F = 0.5 may be assumed (p. 107)
    assert "a value of 0.5 may be assumed for design" in sec("20-3.4.1")["body"]


def test_eq_20_19_and_drainage_criteria():
    # PDF p. 129 (printed 109)
    assert "T85=ne*L/(i*k)" in norm(eq("20-3.4.4", "Eq. 20-19"))
    body = sec("20-3.4.4")["body"]
    assert "85 percent drainage within 24 hours" in body
    assert "the time for 85 percent drainage is 10 days" in body
    assert "become saturated. [As printed (p. 109).]" in body


@pytest.mark.parametrize("eid, form", [
    ("Eq. 20-20", "Q=1000*H*i*k"),
    ("Eq. 20-21", "Q=H*i*k"),
])
def test_collector_flow(eid, form):
    # PDF p. 134 (printed 114)
    assert form in norm(eq("20-5.1", eid))


@pytest.mark.parametrize("eid, const", [("Eq. 20-22", "1.486/n"), ("Eq. 20-23", "1.0/n")])
def test_manning_pipe_capacity(eid, const):
    # PDF p. 135 (printed 115)
    assert f"Q=({const})*A*(d/4)^(2/3)*s^(1/2)" in norm(eq("20-5.2.3", eid))


# --- factors and limits, as printed -----------------------------------------

def test_free_draining_layer_threshold():
    # PDF p. 101 (printed 81): combined pavement + contiguous bound base < 0.09 x design air freezing index
    d = eq("19-7", "N/A (19-7 threshold, not numbered)")
    assert "0.09 * design air freezing index" in d
    assert "pavement and contiguous bound base courses" in d
    assert "not less than 4 in" in d


def test_drain_system_exemptions():
    # PDF pp. 126-127 (printed 106-107)
    body = sec("20-3.4")["body"]
    assert "greater than 20 ft/day (6 m/day)" in body
    assert "8 in (200 mm) or less" in body
    assert "a drainage analysis should be conducted" in sec("20-3.4")["summary"]


def test_reinforced_joint_spacing_should():
    # PDF p. 81 (printed 61): "should be constructed ... not less than 25 ft nor more than 75 ft"
    kps = " ".join(sec("17-1.4")["key_points"])
    assert "should be constructed at intervals of not less than 25 ft (7.6 m) nor more than 75 ft (25 m)" in kps
    assert not any(k.startswith("Verified") for k in sec("17-1.4")["key_points"])


def test_slab_length_cap_should():
    # PDF p. 61 (printed 41): L "should not exceed 75 ft"
    assert any("should not exceed 75 ft" in k for k in sec("14-3")["key_points"])
    assert sec("14-3")["equations"] == []


def test_keyed_joint_thickness_wording():
    # PDF p. 31 (printed 11) 4-0 "must not"; PDF p. 75 (printed 55) 16-2.2.3 "should not"
    assert any("must not be used on pavement thinner than 9 in" in k for k in sec("4-0")["key_points"])
    assert any("should not be used in rigid pavements less than 9 in" in k for k in sec("16-2.2.3")["key_points"])


def test_slab_length_to_width_ratio():
    # PDF p. 73 (printed 53): "In no case should ... exceed the width by more than 25 percent"
    assert any(k.startswith("In no case should the slab length") for k in sec("16-2.1.3")["key_points"])


def test_rccp_no_load_transfer():
    # PDF p. 83 (printed 63)
    assert "no load transfer at the joints" in sec("18-2")["body"]
    assert any("not valid for RCCP" in k for k in sec("18-2")["key_points"])


def test_frost_soil_support_indexes():
    # PDF p. 100 (printed 80), Table 19-3
    kp = " ".join(sec("19-6.1")["key_points"])
    for v in ("F1/S1=9.0", "F2/S2=6.5", "F3/F4=3.5"):
        assert v in kp
    assert "up to 10 percent may be permitted" in kp


def test_subgrade_preparation_depth():
    # PDF p. 104 (printed 84): lesser of 24 in or 2/3 frost penetration less the pavement + base + subbase
    assert "24 in (600 mm) or two-thirds of the frost penetration less the actual combined thickness" in sec("19-9")["body"]


# --- print slips kept as printed, with notes --------------------------------

@pytest.mark.parametrize("sid, field, text", [
    ("4-3.1", "key_points", "165 in (420 mm)"),        # PDF p. 30 (printed 10)
    ("5-2", "key_points", "at less than 90 percent"),  # PDF p. 33 (printed 13) against 6-3, p. 36
    ("9-5.2", "body", "Table 7-1 is Design CBR Values"),  # PDF p. 47 (printed 27)
    ("17-2", "body", "the joint sealing paragraph for plain concrete is 16-5"),  # PDF p. 82 (printed 62)
])
def test_print_slip_notes(sid, field, text):
    val = sec(sid)[field]
    joined = val if isinstance(val, str) else " ".join(val)
    assert text in joined


# --- library-wide checks for this reference ---------------------------------

def test_no_verification_notes_or_unprinted_force_words():
    banned = ("Verified", "MANDATORY", "Never doweled", "prohibited", "NEVER place")
    for fname, s in all_sections():
        texts = [s.get("summary") or ""] + list(s.get("key_points") or [])
        for t in texts:
            for b in banned:
                assert b not in t, f"{fname} {s['section_id']}: {b!r} in {t[:80]!r}"


def test_section_bodies_fit():
    for fname, s in all_sections():
        assert len(s.get("body") or "") <= 14000, f"{fname} {s['section_id']}"
