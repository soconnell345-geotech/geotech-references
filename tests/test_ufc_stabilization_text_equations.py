"""UFC 3-250-11 (2020) chapter text: the printed text, equations and limits.

Pins the text set from the printed pages of docs/ufc_3_250_11_2020.pdf (build of
2026-11-10, app BACKLOG REF-83). Each section body now holds its printed text,
with printed sub-paragraphs that have no section of their own kept in their
parent with their numbers; the three sections too long for one search row
(4-1.4, 4-2.2, 4-4.2) hold their full text in lettered parts (2026-11-12).
Printed page = PDF page - 8. Where the page prints a
slip, the text keeps what is printed and says so; those notes are pinned too.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from geotech_references._retrieval import retrieve_section

REF = "ufc_stabilization"
TEXT_DIR = Path(__file__).resolve().parents[1] / "geotech_references" / REF / "text"


def sec(sid: str) -> dict:
    return retrieve_section(REF, sid)


def body(sid: str) -> str:
    return sec(sid)["body"]


def kps(sid: str) -> str:
    return " | ".join(sec(sid)["key_points"])


def all_sections():
    for f in sorted(TEXT_DIR.glob("*.json")):
        for s in json.loads(f.read_text(encoding="utf-8"))["sections"]:
            yield f.name, s


# --- equations, as printed ---------------------------------------------------

def test_cement_content_for_pi_reduction():
    # PDF p. 24 (printed 16): A = 100BC, B and C as decimals
    assert "expressed as: A = 100BC where A = design cement content" in body("3-1.4.1")
    assert "A = 100*B*C" in sec("3-1.4.1")["equations"][0]["description"]


def test_cutback_asphalt_estimate():
    # PDF p. 33 (printed 25)
    form = "p = [0.02(a) + 0.07(b) + 0.15(c) + 0.20(d)] / (100 - S) x 100"
    assert form in body("3-4.4")
    assert "[0.02(a)+0.07(b)+0.15(c)+0.20(d)]/(100-S)*100" in sec("3-4.4")["equations"][0]["description"]


def test_gravimetric_sulfate_and_its_notes():
    # PDF pp. 74-75 (printed 66-67): x 411.6 as printed; malformed oven-dry expression
    b = body("A-3.1")
    assert "(Weight of residue / Oven dry weight of initial sample) x 411.6" in b
    assert "1 + [(air-dry weight of initial sample / air-dry moisture content (percent)) / 100 percent]" in b
    assert "dilute combined filtrate and washings to 50 ml. [As printed (p. 66)" in b
    # the note's arithmetic: 100 x SO4/BaSO4 x (500/100) x (200/100)
    so4, baso4 = 32.06 + 4 * 16.00, 137.33 + 32.06 + 4 * 16.00
    assert 100 * so4 / baso4 * (500 / 100) * (200 / 100) == pytest.approx(411.6, rel=1e-3)
    eq = sec("A-3.1")["equations"]
    assert "* 411.6" in eq[0]["description"]
    assert "does not give a weight" in eq[1]["description"]


def test_turbidimetric_example_as_printed():
    # PDF p. 76 (printed 68): only a numeric example is printed
    b = body("A-3.2")
    assert "(80.0 x 39.1 x 100) / (1,000 x 1,000 x 9.27) x 0.0338 percent [as printed (p. 68)" in b
    assert 80.0 * 39.1 * 100 / (1000 * 1000 * 9.27) == pytest.approx(0.0337, abs=5e-5)
    assert "prints only the example" in sec("A-3.2")["equations"][0]["description"]


def test_cement_pi_limit_footnote_note():
    # PDF p. 16 (printed 8) and Table 2-3 footnote (c), PDF p. 22 (printed 14)
    b = body("2-1.5.2")
    assert "indicate the PI is less than the equation indicated in footnote b. [Table 2-3 prints" in b
    assert "26.25 for this soil" in b
    assert 20 + (50 - 25) / 4 == 26.25


# --- limits, as printed -------------------------------------------------------

def test_sulfate_limits_both_sentences():
    # PDF p. 13 (printed 5): 0.1 percent, with and without DWG authorization
    b = body("2-1.2.2")
    assert "If sulfate concentration exceeds 0.1 percent by weight do not use cement or fly ash stabilization without prior authorization" in b
    assert "Do not design, specify, construct, or install soil cement, lime, or fly ash for soils containing more than 0.1 percent sulfate" in b
    k = kps("2-1.2.2")
    assert "without prior authorization by the Pavements DWG" in k
    assert "soil cement, lime, or fly ash for soils containing more than 0.1 percent sulfate" in k


def test_organics_limits_and_ph_thresholds():
    # PDF p. 13 (printed 5): pH at least 12.0, organics <= 2 percent, pH >= 5.3; PDF p. 73 (printed 65): 12.1
    b = body("2-1.2.1")
    assert "is at least 12.0" in b
    assert "maximum of 2 percent by weight and a minimum pH of 5.3" in b
    assert "If the pH is 12.1 or greater" in body("A-2")
    assert "2-1.2.1 prints at least 12.0" in kps("A-2")


def test_cement_criteria_should():
    # PDF p. 13 (printed 5): "should" for PI < 30 and > 45 percent passing No. 4; 13 ft joints, PDF p. 14
    k = kps("2-1.3.1")
    assert "should have a PI less than 30" in k
    assert "should be greater than 45 percent" in k
    assert "joint spacing greater than 13 ft (4 m)" in k
    assert "must" not in k


@pytest.mark.parametrize("sid, text", [
    ("2-1.3.2", "PI greater than 12 and more than 25 percent of the soil passing the No. 200"),  # p. 6
    ("2-1.3.3", "the PI cannot be greater than 25 and remain effective"),                     # p. 6
    ("2-1.3.4", "less than 30 percent passing the No. 200 (0.075 mm) sieve and have a PI less than 10"),  # p. 6
    ("2-3", "minimum unconfined compressive strength of 400 psi (2.76 MPa)"),                 # p. 10
    ("3-2.2", "minimum of 25 percent passing the No. 200"),                                   # p. 19
    ("3-3.3", "PI less than 25 and less than 50 percent passing the No. 200"),                # p. 21
    ("3-4.4", "The minimum Marshall Stability recommended for subgrades is 500 lb (227 kg)"),  # p. 26
    ("3-5.3", "less than 1 percent swell"),                                                   # p. 30
    ("3-6", "starting dosage is 0.1 percent with a maximum of 0.8 percent"),                  # p. 31
    ("A-1.1", "Limit the cement content to 4 percent by weight or less"),                     # p. 63
])
def test_printed_limits(sid, text):
    assert text in body(sid)


def test_lime_stabilization_summary_has_no_only():
    # PDF p. 27 (printed 19): "Consider lime stabilization of soils containing a minimum of 25 percent"
    assert "only" not in sec("3-2.2")["summary"]


def test_frost_cutoff_and_temperatures():
    # PDF p. 18 (printed 10)
    b = body("2-2.3")
    assert "less than 60 degF (16 degC)" in b and "less than 40 degF (4 degC)" in b
    assert "(e.g., 30 days)" in b
    assert "Do not stabilize soils to improve the strength at the expense" in kps("2-2.2")


#: The three sections whose printed text is over one row of reference_query
#: (13,300 characters): each holds its full printed text in lettered parts
#: split at printed sub-paragraph headings, the original number the first part
#: (2026-11-12; the letters are the library's, not printed).
LETTERED = {
    "4-1.4": (["4-1.4", "4-1.4.a", "4-1.4.b"],
              ["4-1.4.1 Preparation.", "4-1.4.2 Processing.", "4-1.4.2.1 Handling and Spreading Cement.",
               "4-1.4.2.2 Mixing and Applying Water.", "4-1.4.2.3 Central Mixing Plant.", "4-1.4.3 Compaction.",
               "4-1.4.4 Finishing.", "4-1.4.5 Curing.", "4-1.4.6 Construction Joints.",
               "4-1.4.7 Multiple-Layer Construction."]),
    "4-2.2": (["4-2.2", "4-2.2.a"],
              ["4-2.2.1 Soil Preparation.", "4-2.2.2 Lime Application."]
              + [f"4-2.2.2.{i} " for i in range(1, 10)]
              + ["4-2.2.3 Pulverization and Mixing."] + [f"4-2.2.3.{i} " for i in range(1, 6)]
              + ["4-2.2.4 Compaction.", "4-2.2.5 Curing."]),
    "4-4.2": (["4-4.2", "4-4.2.a"],
              ["4-4.2.1 Windrows.", "4-4.2.2 Determining Liquid Stabilizer Application Rate.",
               "4-4.2.3 Control of Liquid Stabilizers.", "4-4.2.4 Mixing.", "4-4.2.4.1 Travel Plant Mixing.",
               "4-4.2.4.2 Rotary Mixing.", "4-4.2.4.3 Blade Mixing.", "4-4.2.5 Aeration.",
               "4-4.2.5.1 Emulsified Asphalts and Polymers.", "4-4.2.5.2 Cutback Asphalt Mixes.",
               "4-4.2.6 Spreading and Compacting."]),
}


@pytest.mark.parametrize("sid", sorted(LETTERED))
def test_long_sections_hold_their_full_text_in_lettered_parts(sid):
    ids, headings = LETTERED[sid]
    assert [c["section_id"] for c in sec(sid)["children"]] == ids[1:]
    for part in ids[1:]:
        assert body(part).startswith("4-"), part  # each later part opens at a printed heading
        assert "letter is not printed" in sec(part)["applicability"], part
    full = " ".join(body(p) for p in ids)
    assert "[...]" not in full
    at = [full.find(h) for h in headings]
    assert -1 not in at and at == sorted(at), dict(zip(headings, at))
    for p in ids:
        assert len(body(p)) <= 13000, p


def test_soil_cement_construction_limits():
    # PDF pp. 40-47 (printed 32-39): 4-1.4 in three parts (4-1.4, 4-1.4.a, 4-1.4.b)
    b, ba, bb = body("4-1.4"), body("4-1.4.a"), body("4-1.4.b")
    assert "100 percent of the soil-cement mixture will pass a 1 inch (25 mm) sieve and a minimum of 80 percent will pass a No. 4" in b
    assert "do not allow more than 60 minutes to elapse between the start of moist-mixing and the start of compaction" in ba
    assert "Haul time is usually limited to 30 minutes" in ba
    assert "Construct all layers to be less than 4 inches (100 mm) thick. [As printed (p. 39).]" in bb
    assert "Do not construct the edge slope steeper than 2:1" in bb
    # printed sentences the extracts of 2026-11-10 and 2026-11-12 left out
    assert "Use compressed air of 2- to 4-lb/in.2 pressure to prevent arching of cement in the silo and the surge tank." in b
    assert "For grids, space the bags at approximately equal transverse and longitudinal intervals" in b
    assert "Less preferable is the use of one piece of spreading equipment operating one lane at a time" in ba
    assert "Scratching may be done on all soil-cement mixtures except those containing appreciable quantities of gravel." in bb
    assert "Heavy three-wheeled steel rollers can be used to compact coarse granular materials" in bb


def test_lime_and_mixed_in_place_restored_sentences():
    # PDF pp. 50-57 and 59-63 (printed 42-49, 51-55)
    assert "It has greater bulk density for smaller-sized silos." in body("4-2.2")
    assert "The added heat when slurry is made from quicklime speeds the drying action" in body("4-2.2")
    assert "The exception to excess watering is in cool, damp weather when evaporation is at a minimum." in body("4-2.2.a")
    assert '"pulverization and mixing to the satisfaction of the engineer" clause is employed' in body("4-2.2.a")
    assert "Carry as much material in a roll as possible ahead of the blade" in body("4-4.2")
    assert "at a rate of approximately 0.10 gal/sq yd (0.45 liter/sq m)" in body("4-4.2.a")


def test_lime_deep_stabilization_restored():
    # PDF p. 49 (printed 41): two approaches; the airfield caution is printed under 4-2.2.4, not 4-2.1
    b = body("4-2.1")
    assert "One increment of lime is applied to modify soil to a depth of 24 inches (600 mm)" in b
    assert "6 to 12 inches (130 to 300 mm) [as printed (p. 41); 6 inches is 150 mm]" in b
    assert "frost-susceptible material that can produce a weak sublayer" in b
    assert "normal 8- to 9-inch (200 to 230 mm) lifts" in b
    k = kps("4-2.1")
    assert "routine" not in k and "airfield" not in k
    assert "8- to 9-in" in k and "frost-susceptible" in k
    assert "horizontal seams" in k
    assert "do not use deep mixing techniques routinely for airfield projects" in body("4-2.2.a")
    assert "Do not use deep mixing techniques routinely for airfield projects" in kps("4-2.2.a")


def test_lime_compaction_and_curing():
    # PDF pp. 56-57 (printed 48-49), in the second part of 4-2.2
    b = body("4-2.2.a")
    assert "at least 95 percent of ASTM D698" in b and "90 percent for bases for roads and non-traffic areas" in b
    assert "0.10 to 0.25 gal/sq yd (0.45 to 1.13 liter/sq m)" in b


def test_equivalency_example_numbers_and_notes():
    # PDF p. 72 (printed 64)
    b = body("A-1.2.1")
    for t in ("4 inches / 1.15 = 3.48 inches", "0.52 inches * 2.3 = 1.12 inches", "10 inches - 1.12 inches = 8.88 inches",
              "8.88 inches / 2.3 = 3.86 inches"):
        assert t in b
    assert "the millimetre values do not follow one another" in b
    assert "18 inches is given as 458 and 459 mm" in body("A-1.2.2")
    # 0.52 x 2.3 = 1.196, printed 1.12 in both examples (recomputed, rule 2a)
    for sid in ("A-1.2.1", "A-1.2.2"):
        assert "0.52 inches * 2.3 is 1.196 inches, printed 1.12" in body(sid), sid


def test_heading_only_parents():
    for sid in ("2-1.3", "2-1.4", "2-1.5", "2-2", "2-4", "3-1.4", "4-1", "4-2", "A-1", "A-3"):
        b = body(sid)
        assert b.startswith("[Printed as a heading only"), sid
        assert sec(sid)["key_points"] == [], sid


def test_bodies_hold_print_not_tables():
    # tables are stored as tables; their cell text is not run into the bodies
    assert "Base course 750 (5.17)" not in body("2-3")
    assert "Table 2-1 (minimum unconfined compressive strength) and Table 2-2" in body("2-3")
    assert "GW, SW 5" not in body("3-1.5")
    assert "Area 2A" not in body("2-1.5.2")


def test_no_unprinted_emphasis():
    banned = ("Hard limit", "Hard requirement", "NOT routine", "Never improve", "must 'float'", "always test")
    for fname, s in all_sections():
        for t in [s.get("summary") or ""] + list(s.get("key_points") or []) + [s.get("applicability") or ""]:
            for w in banned:
                assert w not in t, f"{fname} {s['section_id']}: {w!r}"


def test_section_bodies_fit_and_are_ascii():
    for fname, s in all_sections():
        b = s.get("body") or ""
        assert len(b) <= 14000, f"{fname} {s['section_id']}"
        assert not re.search(r"[^\x00-\x7e]", b), f"{fname} {s['section_id']}"
