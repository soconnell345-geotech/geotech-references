"""GEC-11 (FHWA-NHI-10-024 / -025, November 2009): chapter text read off the
print (app BACKLOG REF-80).

The chapter files are built by ``scripts/build_gec11_text.py`` from the
printed pages: sections from the printed contents at every printed level,
bodies in the print's own words with ``[p. 3-22]`` markers, every numbered
equation typed in from a rendered page, and the design tables typed in row
by row. These check the structure, the printed titles and sentences with
their pages, and the statements the review of 2026-11-10 found wrong in the
earlier, paraphrased files (each pinned to the printed page).
"""

import json
import re
from pathlib import Path

import pytest

from geotech_references import _retrieval, _retrieval_db

REF = "gec_11"
ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references" / REF
DOCS = ROOT / "docs"
VOLUMES = {
    1: ("FHWA-NHI-10-024", "GEC 11 Vol 1.pdf", range(1, 8)),
    2: ("FHWA-NHI-10-025", "GEC 11 VOL 2.pdf", range(8, 12)),
}
#: Chapters rebuilt from the print so far.
BUILT = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)


def _chapter(n):
    return json.loads((PKG / "text" / f"chapter{n:02d}.json").read_text(encoding="utf-8"))


def _sections():
    out = {}
    for n in BUILT:
        for s in _chapter(n)["sections"]:
            out[s["section_id"]] = s
    return out


def _equations():
    out = {}
    for sid, s in _sections().items():
        for e in s["equations"]:
            out.setdefault(e["id"][4:], (sid, e))
    return out


# --- structure ------------------------------------------------------------

@pytest.mark.parametrize("n", BUILT)
def test_chapter_carries_its_volume(n):
    c = _chapter(n)
    vol = 1 if n <= 7 else 2
    assert c["volume"] == vol
    assert c["reference_id"] == VOLUMES[vol][0]
    assert c["reference_title"].endswith("Volume I" if vol == 1 else "Volume II")


@pytest.mark.parametrize("n", BUILT)
def test_every_section_carries_its_printed_pages(n):
    for s in _chapter(n)["sections"]:
        assert s["body"] == "" or s["body"].startswith("[p. "), s["section_id"]
        assert "printed p" in s["applicability"] or "Part " in s["applicability"], \
            s["section_id"]
        # the print's own words: nothing summarised
        assert "summary" not in s and s["key_points"] == []


@pytest.mark.parametrize("n", BUILT)
def test_sections_fit_the_reference_tools(n):
    for s in _chapter(n)["sections"]:
        assert len(json.dumps(s)) <= 14000, s["section_id"]


@pytest.mark.parametrize("n", BUILT)
def test_every_listed_equation_is_marked_in_its_section(n):
    for s in _chapter(n)["sections"]:
        for e in s["equations"]:
            assert f"[{e['id']}]" in s["body"], (s["section_id"], e["id"])


def test_section_numbers_and_titles_as_printed():
    secs = _sections()
    expect = {
        "1.1": "Objectives", "1.1.3": "Terminology",
        "1.3": "Load and Resistance Factor Design (LRFD)",
        "2.4": "Description of MSE/RSS Systems",
        "2.8.3": "Performance Criteria", "2.8.4": "Design Life",
        # the page prints these words; the contents give others
        "2.10.3": "SeaTac Airport Runway Extension MSE Wall",
    }
    for sid, title in expect.items():
        assert secs[sid]["title"] == title, sid
    assert "SEATAC Runway Extension Wall" in secs["2.10.3"]["applicability"]
    # a long section is split into lettered parts, the letter not printed
    assert secs["1.2.a"]["title"].startswith("Historical Development (continued")
    assert len([s for s in secs if s.startswith("1.")]) == 7
    assert len([s for s in secs if s.startswith("2.")]) == 44
    assert len([s for s in secs if s.startswith("3.")]) == 37
    assert len([s for s in secs if s.startswith("4.")]) == 48
    assert len([s for s in secs if s.startswith("5.")]) == 26
    assert len([s for s in secs if s.startswith("6.")]) == 13
    assert len([s for s in secs if s.startswith("7.")]) == 12
    assert len([s for s in secs if s.startswith("8.")]) == 27
    assert len([s for s in secs if s.startswith("9.")]) == 14
    # the chapter's first page prints "MSE WALL DETAILS"; the contents and
    # the running footer say "MSE Wall Design Details"
    assert secs["5.0"]["title"] == "MSE Wall Details"
    # the printed lettered level (p. 3-28 ff.)
    for letter in "abcdefgh":
        assert f"3.5.2.{letter}" in secs
    assert secs["3.5.2.f"]["title"] == "LRFD Geosynthetic Reinforcement Resistance Factor, φ"
    assert secs["3.6.1.a"]["title"] == "Segmental Panels"
    # chapter 4's design steps at every printed level (p. 4-9 ff.); the
    # page prints 4.4.11.a-c, the contents 4.11.a-c
    # the page prints "MSE WALL DESIGN GUIDELINES", the contents "WALLS"
    assert secs["4.4"]["title"] == "MSE Wall Design Guidelines"
    assert secs["4.4"]["body"] == "[p. 4-9]"      # a heading with no text of its own
    for letter in "abcdefghijk":
        assert f"4.4.7.{letter}" in secs
    assert secs["4.4.6.b"]["title"] == "Eccentricity Limit Check"
    assert secs["4.4.11.a"]["title"] == "Subsurface Drainage"
    assert "4.11.a" not in secs


def test_printed_sentences_with_their_pages():
    secs = _sections()
    body = secs["2.8.4"]["body"]
    assert body.startswith("[p. 2-46]")
    assert ("permanent retaining walls should be designed for a minimum service "
            "life of 75 years") in body
    body = secs["2.8.3"]["body"]
    # the differential settlement limits are printed in 2.8.3 (p. 2-45)
    i = body.index("[p. 2-45]")
    assert body.index("should be limited to differential settlements of 1/500", i) > i
    assert "For walls with welded wire facings, the limiting differential " \
           "settlement should be 1/50." in body
    # a caption is its own paragraph and the text after it is kept (p. 2-44)
    assert "• Seismic Activity. Due to their flexibility" in body


def test_design_tables_typed_in_from_the_page():
    body = _sections()["2.8.3"]["body"]
    assert "[Table 2-1, typed in from p. 2-43, row by row:]\n" \
           "Case | Typical Minimum L/H Ratio\n" in body
    assert "Seismic loading | 0.8 to 1.1" in body
    assert "2H:1V | H/7\n1.5H:1V | H/5" in body
    # Table 2-3: the text layer loses the underline of "≤" (p. 2-46)
    assert "Area ≤ 30 ft² | Limiting Differential Settlement, " \
           "30 ft² < Area ≤ 75 ft²\n¾-in. (20 mm) | 1/100 | 1/200" in body


def test_steel_strength_equations_as_printed():
    # Eqs. 3-10, 3-11a and 3-11b (p. 3-22): no 0.86 factor, no Fu; the
    # earlier file carried both
    eqs = _equations()
    assert eqs["3-10"][1]["formula"] == "Ec = En − ER"
    assert eqs["3-11a"][1]["formula"].startswith("Tal = Fy Ac / b ")
    assert eqs["3-11b"][1]["formula"].startswith("Ptal = Fy Ac ")
    assert eqs["3-10"][0] == eqs["3-11a"][0] == "3.5.1"
    sec = _sections()["3.5.1"]
    text = json.dumps(sec["equations"], ensure_ascii=False) + sec["body"]
    assert "0.86" not in text and "Fu " not in text
    assert "Ec = En − ER [Eq. 3-10]" in sec["body"]
    # the unnumbered equations inside Figure 3-5 (p. 3-24), typed in from
    # the page; its Ac for bars prints no π, kept as printed with a note
    assert "Tmax = φ Rc Tal = φ Rc Fy Ac / b" in sec["body"]
    assert "Ac = (No. of longitudinal bars) × ((D*)² / 4)" in sec["body"]
    assert "the page prints no π" in sec["body"]
    assert "φ R F A" not in sec["body"]


def test_pullout_equations_and_alpha_as_printed():
    eqs = _equations()
    secs = _sections()
    assert eqs["3-2"][1]["formula"] == "Pr = F* α σ′v Le C"
    assert eqs["3-3"][1]["formula"].endswith("F* = Fq · αβ + tan ρ")
    # p. 3-20 and 3-21
    assert eqs["3-4"][1]["formula"].startswith("F* = tan ρ = 1.2 + log Cu at the top")
    assert eqs["3-5"][1]["formula"] == "F* = tan φ at a depth of 20 ft (6 m) and below"
    assert "= 20 (t/St) at the top" in eqs["3-6"][1]["formula"]
    assert "= 10 (t/St) at a depth of 20 ft" in eqs["3-7"][1]["formula"]
    assert eqs["3-8"][1]["formula"] == "F* = (2/3) tan φ"
    # alpha absent test data (p. 3-16)
    body = secs["3.4.2"]["body"]
    assert ("In the absence of test data, α = 0.8 for geogrids and α = 0.6 for "
            "geotextiles (extensible sheets) is recommended") in body
    assert body.index("α = 0.8 for geogrids") < body.index("[p. 3-17]")
    # the "≥" the print sets as an underlined ">" (p. 3-20)
    assert "transverse spacing of St ≥ 6 inches (150 mm)" in secs["3.4.2.a"]["body"]


def test_geosynthetic_strength_equations_as_printed():
    eqs = _equations()
    assert eqs["3-12"][1]["formula"].startswith(
        "Tal = Tult / RF = Tult / (RFID × RFCR × RFD)")
    assert eqs["3-13"][1]["formula"] == "Tal = Tult / RF = Tult / 7"
    body = _sections()["3.5.2.g"]["body"]
    # p. 3-39: the limits of RF = 7, "≤" read from the underlined "<"
    assert "• 4.5 ≤ pH ≤ 9 • Site temperature < 85° F (30° C)" in body
    assert "a default value for RF of 3.5 rather than 7 may be considered" in body


def test_chapter_3_tables_typed_in():
    secs = _sections()
    body = secs["3.4.2"]["body"]
    # Table 3-6 (p. 3-17)
    assert ("Inextensible grids (bar mats and welded wire) | t Fq / (2 tan φ) | "
            "St > Sopt | NA | Obtain Fq from tests, or use default values | "
            "t / (2St) | 1.0*") in body
    assert "Extensible sheets | (blank) | NA | Obtain Tan ρ from tests | NA | NA | 0.6" in body
    body = secs["3.2.3"]["body"]
    assert "pH | > 5 and < 10 | AASHTO T-289" in body          # Table 3-3, p. 3-9
    assert "Polyester (PET) | pH | 3 < pH < 9 | AASHTO T-289" in body   # Table 3-4
    body = secs["3.5.1"]["body"]
    assert "Strip | > ¼ in. (6.4 mm) | 3.9 mils (100 μm)" in body      # Table 3-7
    assert "For residual carbon steel/side: | 0.47 mils/yr (12 μm/year)" in body
    # Table 3-8: the page's caption, not the List of Tables' "Mildly"
    assert ("Table 3-8: Steel Corrosion Rates for Moderately Corrosive "
            "Reinforced Fill.") in secs["3.5.1"]["tables"]
    body = secs["3.5.2.b"]["body"]
    assert "Slit film woven PP geotextile(a) | 1.60 - 3.00 | 1.10 - 2.00" in body
    body = secs["3.5.2.d"]["body"]
    assert "Coated geogrids, Geotextiles, Mn > 25,000, CEG < 30 | 1.15 | 1.3" in body
    # a sentence starting "Table 3-13." is not taken for the caption (p. 3-40)
    body = secs["3.5.2.g"]["body"]
    assert "minimum requirements in Table 3-13. It should be noted" in body
    assert "All Polymers | % Post Consumer Recycled Material by Weight" in body


def test_chapter_4_equations_as_printed():
    eqs = _equations()
    # pullout (p. 4-49, 4-51) and the active length (p. 4-51, 4-52)
    assert eqs["4-35"][1]["formula"] == "φ Le ≥ TMAX / (F* α σv C Rc)"
    assert eqs["4-36"][1]["formula"] == "Le ≥ TMAX / (φ F* α σv C Rc) ≥ 3 ft (1 m)"
    assert eqs["4-35"][0] == eqs["4-40"][0] == "4.4.7.h"
    assert eqs["4-38"][1]["formula"] == "La = (H - Z) tan (45 - φ′/2)"
    assert eqs["4-39"][1]["formula"] == "La = 0.6 (H-Z)"
    assert eqs["4-40"][1]["formula"] == "La = 0.3H"
    # tension and its resistance (p. 4-46 to 4-49)
    assert eqs["4-32a"][1]["formula"].startswith("TMAX = σH Sv ")
    assert eqs["4-32c"][1]["formula"] == "PTMAX-D = σH Sv WP / NP"
    assert eqs["4-33"][1]["formula"] == "Tr = φ Tal"
    assert eqs["4-34"][1]["formula"] == "TMAX ≤ Tr"
    # horizontal stress (p. 4-41 to 4-43), γEV-MAX = 1.35
    assert eqs["4-28"][1]["formula"] == "σH = Kr [(γr Z) γEV-MAX]"
    assert "(= 1.35)" in eqs["4-28"][1]["variables"]["γEV-MAX"]
    # external stability: Rankine and Coulomb Kab (p. 4-15), bearing (p. 4-28, 4-30)
    assert eqs["4-1"][1]["formula"] == "Kab = tan²(45 − φ′b / 2)"
    assert eqs["4-22"][1]["formula"] == "qn = cf Nc + 0.5 L′ γf Nγ"
    assert "0.65" in eqs["4-23"][1]["variables"]["φ"]
    assert eqs["4-24"][1]["formula"] == "γr H ≤ 3 cu"
    # Eq. 4-26 as the page prints it, the bracket with no exponent (p. 4-36)
    assert eqs["4-26"][1]["formula"].endswith("{sin³θ [1 + sin φ′r / sin θ]}")
    assert "no exponent" in eqs["4-26"][1]["notes"]


def test_chapter_4_text_and_tables_as_printed():
    secs = _sections()
    body = secs["4.4.6.b"]["body"]
    assert ("within the middle one-half of the base width for soil foundations "
            "(i.e., emax = L / 4) and middle three-fourths of the base width for "
            "rock foundations (i.e., emax = 3/8 L)") in body
    # Kr/Ka from the top of the reinforced fill to 20 ft (6 m) (p. 4-35)
    assert ("decreases from the top of the reinforced wall fill to a constant "
            "value 20 ft (6 m) below this elevation") in secs["4.4.7.c"]["body"]
    # temporary walls (p. 4-66): RFD 1.0, not the earlier file's RF = 3.5
    body = secs["4.5"]["body"]
    assert "36 month or less service life" in body
    assert "minimum durability reduction factor of 1.0 in lieu of 1.1" in body
    assert "3.5" not in body
    # Tables 4-2, 4-4, 4-5, 4-6, 4-7 typed in (pp. 4-4, 4-17, 4-19, 4-29, 4-48)
    assert ("EV: Vertical Earth Pressure: Retaining Walls and Abutments | 1.35 | 1.00"
            in secs["4.2"]["body"])
    assert "10.0 | 3.0\n≥ 20.0 | 2.0" in secs["4.4.4"]["body"]
    assert "Bearing Resistance | (blank) | 0.65\nSliding | (blank) | 1.0" in secs["4.4.6"]["body"]
    body = secs["4.4.6.c"]["body"]
    assert "[Table 4-6, typed in from p. 4-29, row by row:]\nφ | Nc | Nq | Nγ\n" in body
    assert "30 | 30.1 | 18.4 | 22.4" in body
    assert "39 | 37.9 | 56.0 | 92.3" in body      # as printed; noted
    body = secs["4.4.7.f"]["body"]
    assert ("Metallic reinforcement and connectors: Grid reinforcements (A, C): "
            "Static loading | 0.65") in body
    assert ("Pullout resistance of tensile reinforcement (metallic and geosynthetic): "
            "Combined static/traffic barrier impact (B) | 1.00") in body
    # the page's caption, with the φ and the Kr the lists drop
    assert secs["4.4.7.f"]["tables"][0].startswith("Table 4-7: Resistance Factors, φ, ")
    assert "(Kr/Ka)" in secs["4.4.7.c"]["figures"][0]


def test_chapter_5_filter_criteria_as_printed():
    eqs = _equations()
    secs = _sections()
    # the geotextile retention criterion (p. 5-26), B from Tables 5-1, 5-2
    assert eqs["5-4"][1]["formula"] == "AOS ≤ B D85"
    assert eqs["5-4"][0] == "5.3.3"
    assert "AOS ≤ B D85 [Eq. 5-4]" in secs["5.3.3"]["body"]
    assert "The B coefficient ranges from 0.5 to 2" in secs["5.3.3"]["body"]
    assert "2 ≤ Cu ≤ 4 | 0.5 Cu\n4 < Cu < 8 | 8 / Cu" in secs["5.3.3"]["body"]
    assert "Nonwoven | B = 1.8 | AOS ≤ 1.8D85" in secs["5.3.3"]["body"]
    # granular filters (p. 5-25, 5-26)
    assert eqs["5-1"][1]["formula"] == "D15(filter) / D85(soil) < 5"
    assert eqs["5-2"][1]["formula"] == "4 < D15(filter) / D15(soil) < 20"
    assert eqs["5-3"][1]["formula"] == "D50(filter) / D50(soil) < 25"
    # permeability, permittivity and clogging (p. 5-28)
    assert "kgeotextile ≥ 10 ksoil (Critical / Severe)" in eqs["5-5a"][1]["formula"]
    assert eqs["5-5c"][1]["formula"].startswith("Ψ ≥ 0.2 sec⁻¹ for 15% to 50%")
    assert eqs["5-6"][1]["formula"] == "AOS ≥ 3 D15(upstream soil)"
    # drains (p. 5-31, 5-32)
    assert eqs["5-7"][1]["formula"] == "q = k i A"
    assert eqs["5-11"][1]["formula"] == "q = (0.463 / n) d^(8/3) s^(1/2)"
    # Table 5-3 (p. 5-29)
    assert ("Grab Strength | ASTM D4632 | N (lb) | 1400 (315) | 900 (200) | "
            "1100 (250) | 700 (157)") in secs["5.3.3.a"]["body"]


def test_chapter_7_seismic_and_impact_equations_as_printed():
    eqs = _equations()
    secs = _sections()
    # Anderson et al. (2008) procedure (pp. 7-2 to 7-8)
    assert eqs["7-1"][1]["formula"] == "kmax = Fpga (PGA)"
    assert eqs["7-2"][1]["formula"] == "PGV (in/sec) = 38 Fv S1"
    assert eqs["7-4"][1]["formula"] == "α = 1 + 0.01H [0.5 (Fv S1 / kmax) − 1]"
    assert eqs["7-4"][1]["source"] == "Typed in from p. 7-2."
    assert eqs["7-7"][1]["formula"] == "PIR = 0.5 (kav) (W)"
    assert eqs["7-8"][1]["formula"].startswith("log(d) = -1.51 – 0.74 log(ky/kmax)")
    assert eqs["7-9"][1]["formula"].endswith("0.46 log(kmax) + 1.12 log(PGV)")
    assert ("ξ = tan⁻¹ [kh / (1 − kv)] with kh = horizontal seismic "
            "coefficient") in secs["7.1.1"]["body"]
    assert "h = H + [tan I (0.5H)] / (1 − 0.5 tan I)" in secs["7.1.1"]["body"]
    assert "CDRsliding = Rτ / THF" in secs["7.1.1.a"]["body"]
    assert "0.46 log(kmax) + 1.12log(PGV)" not in secs["7.1.1.a"]["body"]
    # internal stability (pp. 7-9 to 7-14): pullout with 0.8 F*, the
    # frictional connection with 0.8 φ, φ = 1.20
    assert eqs["7-11"][1]["formula"] == "Tmd = Pi / n"
    assert eqs["7-14"][1]["formula"] == "Srt ≥ Tmd RFID RFD / (φ Rc)"
    assert eqs["7-16"][1]["formula"] == "Le ≥ Ttotal / [φ (0.8 F* α σv C Rc)]"
    assert eqs["7-16"][0] == "7.1.2.b"
    assert "= 1.20 from Table 11.5.6-1" in eqs["7-16"][1]["variables"]["φ"]
    assert eqs["7-17"][1]["formula"] == "Srs ≥ Tmax RFD / [0.8 φ (CRcr) Rc]"
    assert eqs["7-18"][1]["formula"] == "Srt ≥ Tmd RFD / [0.8 φ (CRu) Rc]"
    # traffic barrier impact (p. 7-16)
    assert eqs["7-20b"][1]["formula"] == (
        "Ttotal = SV Kr γr [(Z + heq) γEV-MAX] + ti (γCT)")
    assert "2,300 lb/lft (33.5 kN/m)" in secs["7.2.1"]["body"]


def test_chapter_8_rss_equations_and_facing_table_as_printed():
    eqs = _equations()
    secs = _sections()
    # Vol II pp. 8-7, 8-8
    assert eqs["8-1"][1]["formula"] == "FSR = (MR + TS R) / MD"
    assert eqs["8-2"][1]["formula"] == "FS = MR / (MD − TS R)"
    assert eqs["8-1"][0] == eqs["8-2"][0] == "8.3.4"
    assert "Tal = TULT / (FSR ×RF)" in secs["8.3.4"]["body"]
    # Table 8-1 (p. 8-14)
    body = secs["8.4"]["body"]
    assert ("> 50° (> ~0.9H:1V), All Soil Types | Not Recommended | Gabions | "
            "Sod, Permanent Erosion Blanket w/ seed | Wire Baskets,(3) Stone, "
            "Shotcrete") in body
    assert "3. 18 in. (450 mm) high wire baskets are recommended." in body
    assert secs["8.5.2"]["figures"] == [
        "Figure 8-6: Components of a vegetated reinforced slope (VRSS) system"]


def test_chapter_9_rss_design_equations_as_printed():
    eqs = _equations()
    secs = _sections()
    # Vol II pp. 9-7 to 9-24; the print numbers no Eqs. 9-10 to 9-13
    assert eqs["9-1"][1]["formula"] == "TS = (FSR − FSU) MD / D"
    assert eqs["9-6"][1]["formula"] == "TTop = 1/6 TS-MAX"
    assert eqs["9-7"][1]["formula"] == "Tmax = Tzone Sv / Hzone = Tzone / N ≤ Tal Rc"
    assert eqs["9-9"][1]["formula"] == "Le = Tmax FS / (F* α σ′v Rc C)"
    assert eqs["9-15"][1]["formula"] == (
        "FSsqueezing = 2 cu / (γ Ds tan θ) + 4.14 cu / (H γ) ≥ 1.3")
    assert eqs["9-17"][1]["formula"] == "FS = MR / (MD − Ts D)"
    assert not any(n in eqs for n in ("9-10", "9-11", "9-12", "9-13"))
    # Eq. 9-1 where the page sets it, before its "where" list
    body = secs["9.2.6"]["body"]
    assert body.index("TS = (FSR − FSU) MD / D [Eq. 9-1]") < body.index("where:")
    assert "TS-MAX = 0.5 K γr (H’)²" in body
    assert "φf = tan⁻¹ (tan φr / FRR)" in body
    assert "[Unnumbered equation, p. 9-18:] F.S. dynamic ≥ 1.1" in secs["9.2.8"]["body"]
    assert secs["9.2.3"]["title"].endswith("the retained backfill")
    assert secs["9.2.7"]["body"].startswith("[p. 9-16] (see discussion in Chapter 8.)")
    assert "Overexcavation | yd3 (m3 |" in secs["9.4"]["body"]
    # the unnumbered equations set inside Figures 9-4 and 9-8 (pp. 9-8,
    # 9-17), typed in from the page; Figure 9-4 prints "TS + D", kept with
    # a note against Eq. 9-1
    body = secs["9.2.6"]["body"]
    assert "FSR = FSU + (TS + D) / MD [as printed: the page sets a plus sign" in body
    assert "gives FSR = FSU + TS D / MD]" in body
    assert body.index("[Equations and definitions printed in Figure 9-4") < \
        body.index("Figure 9-4. Rotational shear approach")
    body = secs["9.2.7"]["body"]
    assert "σz = 2τx / Ds; τ = Cu" in body
    assert "may be used.\n\n[Figure 9-8 text, typed in from p. 9-17:]" in body
    # a section lists its figures in the order printed
    assert secs["9.2.9"]["figures"] == [
        "Figure 9-9: Seismic stability analysis.",
        "Figure 9-10: Subsurface drainage considerations."]


def test_chapter_10_specification_tables_as_printed():
    secs = _sections()
    assert len([s for s in secs if s.startswith("10.")]) == 33
    # the page prints the long title; the contents give "MSE Walls"
    assert secs["10.9"]["title"] == (
        "Example Specification for Mechanically Stabilized Earth (MSE) Walls")
    assert secs["10.9"]["body"].startswith("[p. 10-15]\n\nThe following specification")
    assert secs["10.10.1"]["title"].startswith("Specification Guidelines For RSS")
    # Table 1 of the example specification (p. 10-19), typed in row by row
    body = secs["10.9.a"]["body"]
    assert "Description | Limit State | Value | Note*\n1. Design Life | All limit states | 75 Years |" in body
    assert ("2. Effective (Drained) Friction Angle – b. Reinforced Backfill | "
            "All limit states | 34° to max 40° | 1") in body
    assert "4. Limiting eccentricity | Service I | B/6 (soil), B/4 (rock) |" in body
    assert "5. Coefficient of Sliding Friction | Strength (all) | tan[min(φr, φf, φi)] | 3" in body
    assert ("II. Combined static/earthquake – Grid reinforcement | Strength (all) | "
            "0.85 | 8,9") in body
    # Table 1.1 note 6 (p. 10-20) and the heading after the table kept apart
    assert "6 | For earthquake loading condition, a resistance factor of 0.90 shall be used." in body
    assert "\n\n(B) Subsurface Drainage Systems:\n\nWalls shall be provided" in body
    # Tables 2 to 7 (pp. 10-28, 10-30, 10-33)
    body = secs["10.9.c"]["body"]
    assert "Sieve Size | Percent Passing\n4 inch (Note 1) | 100\nNo. 40 | 0-60\nNo. 200 | 0-15" in body
    assert "Resistivity, min. | 3,000 ohm-cm | AASHTO T-288" in body
    assert "Polyester | pH | > 3 and < 9 | AASHTO T-289" in body
    assert "Gradation (AASHTO T 27), / Plasticity Index (AASHTO T 90) | One per 5,000 CY" in body
    assert "AASHTO T 26 for gradation as printed" in body
    assert "¾-inch | 50-75\nNo. 4 | 0-60" in secs["10.9.d"]["body"]
    # the tie strips' steel as printed (p. 10-26): A1101, not A1011
    assert "ASTM A1101, Grade 50 minimum" in secs["10.9.b"]["body"]
    # Tables S-1 and S-2 (p. 10-43): the strength equation set in note 3
    body = secs["10.10.1"]["body"]
    assert body.count("Tal = TULT / (RFD × RFID × RFCR) where RFCR") == 2
    assert "A | (blank) | (blank) | GW-GM\nA | (blank) | (blank) | SW-SM-SC" in body
    # Table S3 (p. 10-50) and the erosion mat types (p. 10-46)
    body = secs["10.10.3"]["body"]
    assert "Geotextile: Puncture, CLASS 2⁶ | ASTM D6241 | 310 lb (1375 N)" in body
    assert "Geotextile: Permeability⁴ | ASTM D4491⁵ | ______ cm/s" in body
    body = secs["10.10.2"]["body"]
    assert "(i) Type __. Long-term duration (Longer than 2 Years)" in body
    assert "Shear Stress (td) > 2 psf (95 Pa) to < 5 psf (240 Pa)" in body


def test_chapter_11_checklists_and_tables_as_printed():
    secs = _sections()
    assert len([s for s in secs if s.startswith("11.")]) == 23
    # Table 11-1 (p. 11-2), one item to a line
    body = secs["11.1"]["body"]
    assert "□ 5. On site, check reinforcements" in body
    assert "- compressive strength < specification requirements\n- molding defects" in body
    # Tables 11-2 and 11-3 (pp. 11-5 to 11-10), numbered as printed
    body = secs["11.1.2"]["body"]
    assert "1.0 DOCUMENTS\n1.1 Have you thoroughly reviewed the design drawings?" in body
    assert "8.10 Do you understand any erosion control details?" in body
    assert "2.1.4 Drainage aggregate\n2.1.4 Graded granular filters (if applicable)" in body
    assert "numbered as printed: 2.1.4 twice" in body
    assert "6.10 Do the QA test results for the reinforcing materials" in secs["11.1.2.a"]["body"]
    # the alignment tolerances (p. 11-26) as printed, with a note on the metric
    body = secs["11.3.5"]["body"]
    assert "1/2-inch per 10 ft (6 mm per m)" in body
    assert "1/2 inch per 10 ft is about 4 mm per m" in body
    # Table 11-4 (pp. 11-30, 11-31): each condition with its causes
    assert ("5. Wall out of horizontal alignment tolerance, or bulging. | 5. a. See Causes "
            "3c, 3d, 3e, 3j, 3k.") in body
    assert "presented in Table 11-4.\n\nTable 11-4. Out-of-Tolerance" in body
    # Table 11-5 (pp. 11-32 to 11-34): the item the text layer dropped
    assert secs["11.3.5.a"]["body"].startswith(
        "[p. 11-34] [Table 11-5 continued, p. 11-34:]\n7.2 Where applicable")
    # Table 11-6 (pp. 11-38, 11-39)
    body = secs["11.4.4"]["body"]
    assert "Stress distribution at base of structure | Earth pressure cells" in body
    assert "Barometric pressure | Barometric pressure gauge" in body


def test_figure_text_typed_in_from_the_page():
    secs = _sections()
    # the List of Figures numbers Figure 5-11 "Figure 5-14"; the page
    # prints 5-11 (p. 5-17)
    assert ("Figure 5-11: Example detail for wall that may experience "
            "inundation") in secs["5.3.1"]["figures"]
    assert secs["5.3.2"]["figures"][2].startswith(
        "Figure 5-14: (a) Example geomembrane barrier details")
    # RFCR ranges (p. 3-33) and the FS equivalents (p. 4-60)
    assert ("Polypropylene (PP): 5 to 4.0. High Density Polyethylene (HDPE): "
            "5 to 2.6.") in secs["3.5.2.c"]["body"]
    assert "φ = 0.75 ⇒ 1/0.75 ≈ 1.3 = FS" in secs["4.4.9"]["body"]
    # the unnumbered SMSE equations printed in Figure 6-14 (p. 6-25)
    body = secs["6.5"]["body"]
    assert ("Case 3: For LW ≥ H tanβ: Tmax = [H tan β (γH + 2q) + 2FV] / "
            "(2 tan(φ′ + β)) + FH.") in body
    assert "a. φp = 0.90 for L/H > 0.4 b. φp = 0.65 for L/H ≤ 0.4" in body
    assert "10 tan(φ′ + β) Case 3" not in body
    # Figure 6-16's dimensions (p. 6-28)
    assert "Lt = 0.8 H min; Lb = Greater of 0.3H or 5 ft" in secs["6.6"]["body"]
    assert "Lt 3 ft min H" not in secs["6.6"]["body"]


def test_lookups_linked_from_the_section_that_prints_the_table():
    import importlib
    seen = {}
    for sid, s in _sections().items():
        for obj, path in s.get("implemented_in", {}).items():
            assert any(x.split(":")[0] == obj for x in s["tables"] + s["figures"]), \
                (sid, obj)
            mod, fn = path.rsplit(".", 1)
            assert callable(getattr(importlib.import_module(mod), fn)), path
            seen[obj] = sid
    assert seen.get("Table 2-1") == "2.8.3" and seen.get("Table 2-2") == "2.8.3"
    assert seen.get("Table 3-1") == "3.2.1" and seen.get("Table 3-6") == "3.4.2"
    assert seen.get("Table 3-3") == seen.get("Table 3-4") == "3.2.3"
    assert seen.get("Table 3-7") == seen.get("Table 3-8") == "3.5.1"
    assert seen.get("Table 3-9") == "3.5.2.b" and seen.get("Table 3-11") == "3.5.2.d"
    assert seen.get("Table 4-1") == seen.get("Table 4-2") == "4.2"
    assert seen.get("Table 4-4") == "4.4.4" and seen.get("Table 4-5") == "4.4.6"
    assert seen.get("Table 4-6") == "4.4.6.c" and seen.get("Table 4-7") == "4.4.7.f"
    assert seen.get("Figure 4-10") == "4.4.7.c"
    # 16 tables in tables.py and Figure 4-10 in figures.py
    assert len(seen) == 17


def test_search_and_fetch_through_the_database():
    row = _retrieval_db.reference_get(REF, "2.8.4")
    assert row["title"] == "Design Life"
    assert "75 years" in row["body"]
    sec = _retrieval.retrieve_section(REF, "2.10.3")
    assert "SeaTac" in sec["title"]


# --- the build ------------------------------------------------------------

def _builder():
    pytest.importorskip("fitz")
    for _, pdf, _ in VOLUMES.values():
        if not (DOCS / pdf).exists():
            pytest.skip("PDF not checked out")
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import build_gec11_text as builder
    finally:
        sys.path.remove(str(ROOT / "scripts"))
    return builder


def test_rebuild_reproduces_the_committed_text():
    # the formulas and typed tables live in the manifest, so a rebuild
    # keeps them; the figure catalog is not written by the build
    builder = _builder()
    chapters = builder.build_chapters(set(BUILT))
    assert sorted(chapters) == list(BUILT)
    for n, data in chapters.items():
        assert data.pop("_missing") == [], n
        committed = (PKG / "text" / f"chapter{n:02d}.json").read_text(encoding="utf-8")
        assert builder.bpt.chapter_json(data) == committed, f"chapter {n}"


@pytest.mark.parametrize("vol", [1, 2])
def test_volume_cover_designation(vol):
    fitz = pytest.importorskip("fitz")
    rid, pdf, chapters = VOLUMES[vol]
    path = DOCS / pdf
    if not path.exists():
        pytest.skip("PDF not checked out")
    with fitz.open(str(path)) as doc:
        cover = doc[0].get_text()
    assert f"Publication No. {rid}" in cover
    assert "November 2009" in cover


# --- scatter patterns (build rule 2a) ---------------------------------------
# What a formula taken from the text layer looks like when it has come apart:
# a prime parted from its symbol or subscript, a number left on a line of its
# own above the formula, brackets that do not pair, a sentence that follows a
# table copied into each row.

_PRIMES = (re.compile(r"(?<=\s)['′’](?=\s)"), re.compile(r"\(['′’]\)"),
           re.compile(r"[φσ]['′’] [a-z]\b(?![a-z])"))
_OPS = re.compile(r"[+\-−×·*/÷^√Σ²³½]")
# an enumerator ("2)", "b)", "iii)") at the start of a line, after a stop,
# a colon or a bullet, or before a capitalised word
_ENUM = re.compile(r"(?:^|(?<=[.:;•\]] )|(?<=\s)(?=\d{1,2}\)\s[A-Z]))"
                   r"(?:\d{1,2}|[a-zA-Z]|[ivx]{1,4})\)(?=\s)")
#: brackets the page itself leaves unpaired (checked on the render)
_PRINTED_UNPAIRED = {
    ("9.2.6", "cohesionless soil, c = 0)"),  # Figure 9-5, p. 9-10
}


def _formula_lines(body):
    for line in body.split("\n"):
        for m in re.finditer("=", line):
            if _OPS.search(line[max(0, m.start() - 30): m.end() + 30]):
                yield line
                break


def test_no_scatter_patterns_in_the_bodies():
    bad = []
    for sid, s in _sections().items():
        body = s["body"]
        for r in _PRIMES:
            bad += [f"{sid}: prime parted {body[max(0, m.start() - 20):m.end() + 8]!r}"
                    for m in r.finditer(body)]
        lines = body.split("\n")
        for i, ln in enumerate(lines):
            if re.fullmatch(r"\s*\d{1,2}\s*", ln):
                nxt = next((x for x in lines[i + 1:] if x.strip()), "")
                if "=" in nxt:
                    bad.append(f"{sid}: lone number {ln!r} above {nxt[:50]!r}")
        for ln in _formula_lines(body):
            if any(i == sid and snip in ln for i, snip in _PRINTED_UNPAIRED):
                continue
            t = re.sub(r"\[p\. [^\]]+\]|\[Eq\. [^\]]+\]", "", _ENUM.sub("", ln))
            for a, b in ("()", "[]", "{}"):
                if t.count(a) != t.count(b):
                    bad.append(f"{sid}: {a}{b} unpaired in {ln[:80]!r}")
        prev = None
        for ln in lines:
            cells = [c.strip() for c in ln.split(" | ")] if " | " in ln else None
            if cells and prev:
                bad += [f"{sid}: sentence repeated in rows {c[:60]!r}"
                        for c in set(cells) & set(prev)
                        if len(c) >= 60 and re.search(r"[.?!]\)?$", c)]
            prev = cells
    assert bad == []
