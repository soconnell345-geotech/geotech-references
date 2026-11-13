"""FHWA-NHI-05-037 Geotechnical Aspects of Pavements: chapter text read off
the print (app BACKLOG REF-82).

The chapter text is built by ``scripts/build_printed_text.py`` from the
manifest ``scripts/manifests/fhwa_pavements.json``: every numbered heading
of the printed contents is a section with its printed number and title, the
body is the print's own wording with ``[p. 5-53]`` page markers, every
numbered equation is typed in from the rendered page, and the tables the
text layer scrambles where a design depends on them are typed in from the
page. These tests pin what the page prints.
"""

import json
import re
from pathlib import Path

import pytest

from geotech_references import _retrieval
from tests._build_reader import require_build_reader

REF = "fhwa_pavements"
ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references" / REF
PDF = ROOT / "docs" / "FHWA-NHI-05-037 - Geotech Pavements.pdf"
#: the chapters rebuilt from the print so far
BUILT = [1, 2, 3, 4, 5, 6, 7, 8]


def _manifest():
    return json.loads((ROOT / "scripts" / "manifests" / f"{REF}.json")
                      .read_text(encoding="utf-8"))


def _chapter(n):
    return json.loads((PKG / "text" / f"chapter{n:02d}.json").read_text(encoding="utf-8"))


def _sections(n):
    return {s["section_id"]: s for s in _chapter(n)["sections"]}


def _equations():
    out = {}
    for n in BUILT:
        for s in _chapter(n)["sections"]:
            for e in s["equations"]:
                out[e["id"][4:]] = (s["section_id"], e)
    return out


def test_built_chapters_carry_the_printed_titles():
    titles = {n: _chapter(n)["chapter_title"] for n in BUILT}
    assert titles[1] == "Introduction"
    assert titles[2] == "State Agencies"
    assert titles[3] == "Geotechnical Issues in Pavement Design and Performance"
    for n in BUILT:
        c = _chapter(n)
        assert c["reference_id"] == "FHWA-NHI-05-037 Geotechnical Aspects of Pavements"
        assert c["chapter"] == n


def test_every_printed_heading_is_a_section():
    # the numbered headings of the printed contents (pp. i-3 to i-8)
    s1 = _sections(1)
    assert [k for k in s1 if not re.search(r"\.[a-z]$", k)] == [
        "1.1", "1.2", "1.3", "1.3.1", "1.3.2", "1.3.3", "1.3.4", "1.3.5",
        "1.3.6", "1.4", "1.5", "1.5.1", "1.5.2", "1.6", "1.7"]
    assert s1["1.3.1"]["title"] == "Components of a Pavement System"
    assert s1["1.5.2"]["title"] == "Collapsible Soils"
    s2 = _sections(2)
    assert list(s2) == ["2.1", "2.2"]
    # the page prints "2.2. QUESTIONAIRE ON GEOTECHNICAL PRACTICES IN
    # PAVEMENT DESIGN" (p. 2-2); the contents spell it otherwise
    assert s2["2.2"]["title"] == "Questionaire on Geotechnical Practices in Pavement Design"
    assert "Questionnaire on Geotechncial" in s2["2.2"]["applicability"]


def test_every_section_carries_its_printed_pages():
    for n in BUILT:
        for s in _chapter(n)["sections"]:
            assert s["body"] == "" or s["body"].startswith("[p. "), s["section_id"]
            assert "printed p" in s["applicability"] or "Part " in s["applicability"], \
                s["section_id"]
            assert s["key_points"] == []


def test_section_bodies_fit_the_reference_tools():
    for n in BUILT:
        for s in _chapter(n)["sections"]:
            assert len(json.dumps(s)) <= 14000, s["section_id"]


def test_printed_sentences_with_their_pages():
    s1 = _sections(1)
    body = s1["1.3.1"]["body"]
    assert "[p. 1-5]" in body and "[p. 1-6]" in body
    assert ("The subgrade is the top surface of a roadbed upon which the pavement "
            "structure and shoulders are constructed.") in body
    assert "Figure 1-1: Basic components of a typical pavement system" in s1["1.3.1"]["figures"]
    body = s1["1.4"]["body"]
    assert "Inadequate drainage of water from the base and subgrade is a major cause of " \
           "pavement problems (Cedergren, 1987)." in body
    body = _sections(2)["2.1"]["body"]
    assert body.startswith("[p. 2-1]")
    assert "Various state agencies take different approaches to pavement design." in body


def test_every_listed_equation_is_marked_in_its_section():
    for n in BUILT:
        for s in _chapter(n)["sections"]:
            for e in s["equations"]:
                if e["id"].startswith("Eq. "):
                    assert f"[{e['id']}]" in s["body"], (s["section_id"], e["id"])


def test_manifest_formulas_match_the_text():
    eqs = _equations()
    for vol in _manifest()["volumes"]:
        for p in vol.get("printed_equations", []):
            # "7-5": chapter 7 prints one equation number with a hyphen
            if int(re.split(r"[-.]", p["number"])[0]) in BUILT and p.get("formula"):
                assert eqs[p["number"]][1]["formula"] == p["formula"], p["number"]
                assert eqs[p["number"]][1]["source"] == f"Typed in from p. {p['page']}."


def test_rebuild_reproduces_the_committed_text():
    if not PDF.exists():
        pytest.skip("PDF not checked out")
    # The reader's version is an input of the build (tests/_build_reader.py).
    require_build_reader(REF)
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import build_printed_text as builder
    finally:
        sys.path.remove(str(ROOT / "scripts"))
    chapters, _ = builder.build_chapters(REF)
    assert sorted(chapters) == BUILT
    for n, data in chapters.items():
        assert data.pop("_missing") == [], n
        committed = (PKG / "text" / f"chapter{n:02d}.json").read_text(encoding="utf-8")
        assert builder.chapter_json(data) == committed, f"chapter {n}"


def test_section_lookup_through_the_retrieval_layer():
    sec = _retrieval.retrieve_section(REF, "1.3.1")
    assert sec["title"] == "Components of a Pavement System"


def _printed_ids(n):
    return [k for k in _sections(n) if not re.search(r"\.[a-z]$", k)]


def test_chapter_3_headings_as_printed():
    assert _printed_ids(3) == [
        "3.1", "3.2", "3.3", "3.3.1", "3.3.2", "3.4", "3.5", "3.5.1", "3.5.2",
        "3.5.3", "3.5.4", "3.6", "3.7"]
    s3 = _sections(3)
    # the stored text before the rebuild titled these with its own glosses
    assert s3["3.2"]["title"] == "Basic Concepts"
    assert s3["3.4"]["title"] == "Sensitivity of Pavement Design"
    assert s3["3.5.2"]["title"] == "The AASHTO Pavement Design Guides"


def test_chapter_3_equations_typed_from_the_page():
    eqs = _equations()
    assert [k for k in eqs if k.startswith("3.")] == [f"3.{i}" for i in range(1, 11)]
    assert eqs["3.2"][1]["formula"] == "SN = a1D1 + a2D2 + a3D3"
    assert eqs["3.7"][1]["formula"] == "SN = a1D1 + a2D2m2 + a3D3m3"
    assert eqs["3.8"][1]["formula"] == (
        "log10(W18) = ZR S0 + 9.36 log10(SN + 1) – 0.20 + log10[ΔPSI/(4.2 – 1.5)] / "
        "[0.40 + 1094/(SN + 1)^5.19] + 2.32 log10(MR) – 8.07")
    assert eqs["3.8"][1]["source"] == "Typed in from p. 3-28."
    # print slips typed as printed and said
    assert "7.3 log(D + 1)" in eqs["3.5"][1]["formula"]
    assert "7.35" in eqs["3.5"][1]["notes"]
    assert "1.64x10^7" in eqs["3.9"][1]["formula"]
    assert "1.624×10^7" in eqs["3.9"][1]["notes"]
    assert "(log t)^.002" in eqs["3.10"][1]["formula"]
    assert "80 psi" in eqs["3.10"][1]["variables"]["R"]


def test_chapter_3_formulas_stand_in_the_body():
    body = "\n".join(s["body"] for s in _chapter(3)["sections"])
    assert ("The structural number SN is defined as\n\nSN = a1D1 + a2D2 + a3D3 "
            "[Eq. 3.2]") in body
    # the glyphs the text layer left beside an equation are gone
    for glyphs in ("9.36log( 1)", "a D m a D m = + +", "rF R t C C"):
        assert glyphs not in body
    # superscripts the text layer lost (Tables 3-5 and 3-6, pp. 3-31, 3-33)
    assert "10x106" not in body and body.count("10x10^6 ESALs") == 2
    assert "4.2x10^6 psi (29 GPa)" in body
    assert "Reliability Level (%) Reliability Factor Fr 50 1.00 70 1.44 90 2.32" in body


def test_chapter_4_headings_as_printed():
    assert _printed_ids(4) == [
        "4.1", "4.2", "4.2.1", "4.2.2", "4.2.3", "4.2.4", "4.3", "4.4", "4.5",
        "4.5.1", "4.5.2", "4.5.3", "4.5.4", "4.5.5", "4.5.6", "4.5.7", "4.6",
        "4.7", "4.7.1", "4.7.2", "4.7.3", "4.7.4", "4.8"]
    s4 = _sections(4)
    # the stored text filed Table 4-14 under 4.7.3; the print's 4.7.3 is
    # the subsurface profile and Table 4-14 is printed in 4.7.2 (p. 4-65)
    assert s4["4.7.3"]["title"] == "Subsurface Profile"
    assert any(t.startswith("Table 4-14") for t in s4["4.7.2"]["tables"])


def test_dcp_relation_where_the_page_prints_it():
    # finding text-10: the stored 4.5.5 gave the DCP relation and ASTM
    # numbers the section does not print; the relation is printed in Table
    # 4-9 (p. 4-39), after the 4.5.6 heading, and prints no unit
    s4 = _sections(4)
    assert "292" not in s4["4.5.5"]["body"]
    assert "D4429" not in s4["4.5.5"]["body"] and "D6951" not in s4["4.5.5"]["body"]
    body = "\n".join(s["body"] for k, s in s4.items() if k.startswith("4.5.6"))
    assert "[p. 4-39]" in body
    assert ("CBR = 292/(DPI)^1.12 for gravel, sand, and silt\n"
            "CBR = 1/0.002871 DCP for highly plastic clays\n"
            "CBR = 1/(0.017 DCP)^2 for low plasticity clays") in body
    assert "prints no unit for DPI or DCP" in body and "cbr_from_dcp" in body
    links = [e["implemented_in"] for s in s4.values() for e in s["equations"]]
    assert "geotech_references.fhwa_pavements.equations.cbr_from_dcp" in links


def test_table_4_14_typed_from_the_page():
    body = _sections(4)["4.7.2"]["body"]
    assert "[Table 4-14 as printed on p. 4-65, typed in from the page:]" in body
    assert "GM* u | (as GM d) | Good | Slight to medium | Slight | Poor to practically impervious" in body
    assert "CH | Inorganic clays of high plasticity, fat clays | Poor to Fair | Medium to Very High | High | Practically Impervious" in body
    assert "(Pt) | Peat & other highly organic soils | Not Suitable | Slight | Very high | Fair to Poor" in body
    # the SPT energy correction keeps the number the page gives it
    sec = "\n".join(s["body"] for s in _chapter(4)["sections"])
    assert "N60 = (Ef/60) Nmeas (5-1) [numbered (5-1) on the page" in sec


def test_chapter_5_headings_as_printed():
    assert _chapter(5)["chapter_title"] == "Geotechnical Inputs for Pavement Design"
    assert _printed_ids(5) == [
        "5.1", "5.2", "5.2.1", "5.2.2", "5.2.3", "5.3", "5.3.1", "5.3.2", "5.3.3",
        "5.3.4", "5.4", "5.4.1", "5.4.2", "5.4.3", "5.4.4", "5.4.5", "5.4.6",
        "5.4.7", "5.4.8", "5.4.9", "5.5", "5.5.1", "5.5.2", "5.6", "5.6.1",
        "5.6.2", "5.7", "5.8", "5.8.1", "5.8.2", "5.9"]
    s5 = _sections(5)
    # the stored text before the rebuild filed other subjects under these
    # numbers ("Compaction Characteristics" as 5.3.3, "Swell and Collapse
    # Potential" as 5.4.7); the page prints
    assert s5["5.3.3"]["title"] == "Problem Soil Identification"
    assert s5["5.4.7"]["title"] == "Interface Friction"
    assert s5["5.5"]["title"] == "Thermo-Hydraulic Properties"
    assert "Identification of Problem Soils" in s5["5.3.3"]["applicability"]


def test_chapter_5_printed_sentences_with_their_pages():
    s5 = _sections(5)
    body = s5["5.4.9"]["body"]
    assert body.startswith("[p. 5-83]")
    assert ("Values of K0 predicted by Eq. (5.37) for typical geomaterials range "
            "between 0.4 and 0.6.") in body
    body = s5["5.3.2"]["body"]
    assert "[p. 5-19]" in body
    assert "equivalent dry unit weight is then computed as\n\nγd = γt/(1 + w) [Eq. 5.1]" in body
    body = s5["5.4.7"]["body"]
    assert "frictional resistance between the bottom of the slab and the top of the " \
           "underlying subbase or subgrade" in body


def test_chapter_5_equations_typed_from_the_page():
    eqs = _equations()
    assert [k for k in eqs if k.startswith("5.")] == [f"5.{i}" for i in range(1, 70)]
    # the distinguishing term of each, as the rendered page prints it
    expect = {
        "5.4": "CR = γd/(γd)max × 100%",                       # p. 5-20
        "5.7": "R = 100 – 100/[(2.5/D2)((Pv/Ph) – 1) + 1]",    # p. 5-40
        "5.11": "uf = 1.18×10^8 (MR)^–2.32",                   # p. 5-46
        "5.12": "MR = 3015(uf)^–0.431",                        # p. 5-46
        "5.13": "MR (psi) = 1500 × CBR for CBR ≤ 10",          # p. 5-49
        "5.16": "a2 = 0.249 log10 EBS – 0.977",                # p. 5-59
        "5.18": "a3 = 0.227 log10 ESB – 0.839",                # p. 5-64
        "5.24": "uri = [D^0.75 – 0.39 ki^0.25]^3.42",          # p. 5-70
        "5.26": "keff = kdynamic/2",                           # p. 5-76
        "5.32": "CBR = (MR/2555)^(1/0.64)",                    # p. 5-81
        "5.69": "ksat = C * D10^2",                            # p. 5-103
    }
    for num, formula in expect.items():
        assert eqs[num][1]["formula"] == formula, num
    assert "(E B^4/(Ef I))^(1/12)" in eqs["5.19"][1]["formula"]          # p. 5-67, 12th root
    assert eqs["5.22"][1]["formula"].startswith("ln k∞ = –2.807 + 0.1253(ln DSB)^2")
    assert "51.712(CBR)^(–0.3586(GWT)^0.1192)" in eqs["5.31"][1]["formula"]  # p. 5-81
    assert "(3/4)(OCR/OCRmax)" in eqs["5.39"][1]["formula"]              # p. 5-83
    assert "Mayne and Kulhawy (1982)" in eqs["5.39"][1]["notes"]
    assert "commonly quoted" not in eqs["5.39"][1]["notes"]
    # print slips kept as printed, with a note
    assert eqs["5.34"][1]["formula"].endswith("≤ 1×10^–7")
    assert "never met" in eqs["5.34"][1]["notes"]
    assert "9.7e^–4" in eqs["5.65"][1]["formula"]
    assert "haev" in eqs["5.66"][1]["notes"]
    # recomputed: the inverse of Eq. 5.11 gives the constant of Eq. 5.12
    assert round((1.18e8) ** (1 / 2.32)) == 3015
    assert round(1 / 2.32, 3) == 0.431


def test_chapter_5_tables_typed_from_the_page():
    body = "\n".join(s["body"] for s in _chapter(5)["sections"])
    # Tables 5-3 to 5-6 print check marks the text layer gives as "3"
    assert "[Table 5-3 as printed on p. 5-9, typed in from the page:]" in body
    assert "CBR | California Bearing Ratio | | ✓(d) | | 5.4.1" in body
    assert "kdynamic | Backcalculated modulus of subgrade reaction | ✓(b) | | | 5.4.3" in body
    assert "ksat | Saturated hydraulic conductivity (permeability) | ✓ | | | 5.5.2" in body
    assert "Material type 3 3 3" not in body
    # Table 5-8: the total unit weight identity the text layer dropped
    assert "2. Total Unit Weight: γt = [(1 + w)/(1 + e)] Gs γw" in body
    assert "not legible as a mathematical sign on p. 5-14" in body
    # Table 5-51: the text layer put each percentage before the next category
    assert "None | | 0\nMinor | This option is valid" in body
    assert "Extreme | Generally not used for new or reconstructed pavement levels. | 100" in body
    # Tables 5-40 and 5-42: the exponent the text layer lost (8,000 x 5^0.6 = 21,012)
    assert "Dry 8,000θ^0.6 21,012" in body and "Wet 4,600θ^0.6 12,082" in body
    assert round(8000 * 5 ** 0.6) == 21012
    assert "θ0.6" not in body
    assert "110±5°C" in body and "BTU/ft-hr-°F" in body


def test_chapter_6_headings_as_printed():
    # chapter 6 was not in the library before the rebuild
    assert _chapter(6)["chapter_title"] == "Pavement Structural Design and Performance"
    assert _printed_ids(6) == [
        "6.1", "6.2", "6.2.1", "6.2.2", "6.2.3", "6.3", "6.3.1", "6.3.2", "6.3.3",
        "6.4", "6.5", "6.5.1", "6.5.2", "6.5.3", "6.6", "6.6.1", "6.6.2", "6.6.3",
        "6.7", "6.7.1", "6.7.2", "6.8", "6.9", "6.10"]
    s6 = _sections(6)
    assert s6["6.3"]["title"] == "Soft Subgrade"
    assert s6["6.7"]["title"] == "Shallow Bedrock"
    body = s6["6.3"]["body"]
    assert body.startswith("[p. 6-21]")
    assert ("The subgrade is now postulated to be a very soft high plasticity clay "
            "(AASHTO A-7-6, USCS CH) with MR = 6000 psi") in body


def test_chapter_6_worked_designs_read_off_the_page():
    s6 = _sections(6)
    # the 1993 AASHTO calculation lines, which the text layer scattered
    # ("SN2 = 1 1 2.28", "2 2 2 2 12.7 inches1"), as typeset (p. 6-5)
    body = s6["6.2.1"]["body"]
    assert "• Required minimum thickness of asphalt D1 = SN1/a1 = 5.3 inches¹" in body
    assert "SN2 = SN – D1a1 = 2.28" in body
    assert "D2 = SN2/(m2a2) = 12.7 inches¹" in body
    assert "(a1/a2 = 0.44/0.18 = 2.44)" in body and "($14,250/$8,200 = 1.74)" in body
    assert "SN2 = 1 1 2.28" not in body
    # recomputed: D1 = 2.35/0.44, SN2 = 4.61 - 5.3 x 0.44, D2 = 2.28/(1.0 x 0.18)
    assert round(2.35 / 0.44, 1) == 5.3
    assert round(4.61 - 5.3 * 0.44, 2) == 2.28
    assert round(2.28 / 0.18, 1) == 12.7
    # the soft subgrade and low quality base lines (pp. 6-22, 6-32); the
    # thickness the text layer dropped is back
    assert "SN2 = m2a2D2 = (1.0)(0.18)(12.7) = 2.28" in s6["6.3.1"]["body"]
    assert "D1 = SN1/a1 = 7.9 inches" in s6["6.3.1"]["body"]
    assert "SN1 = SN – SN2 = 4.61 – 1.07 = 3.54" in s6["6.5.1"]["body"]
    assert "D1 = SN1/a1 = 8.0 inches" in s6["6.5.1"]["body"]
    # the poor drainage line prints 5.67 where the line above gives 5.76 (p. 6-42)
    body = s6["6.6.1"]["body"]
    assert "SN1 = SN – SN2 = 5.67 – 0.91 = 4.76 [as printed on p. 6-42" in body
    assert round(5.76 - 0.91, 2) == 4.85
    # the lost superscripts of the traffic and modulus values
    text = "\n".join(s["body"] for s in _chapter(6)["sections"])
    assert "x106" not in text
    assert "Traffic (W18) 6.1x10^6 ESALs" in text and "4.4x10^6 psi" in text


def test_chapter_6_tables_typed_from_the_page():
    text = "\n".join(s["body"] for s in _chapter(6)["sections"])
    assert "[Table 6-5 as printed on p. 6-13, typed in from the page:] Class 4 | 1.3%" in text
    assert "Class 9 | 74.0%" in text
    assert "Class 10 | 1.19 | 1.09 | 0.89 | 0.00" in text
    assert "Average Axle Spacing (ft) | 12 | 15 | 18" in text
    assert "Truck Class: Axle Weight (lbs) | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13" in text


def test_chapter_7_headings_as_printed():
    ch = _chapter(7)
    # the chapter's first page; the contents prints "Subgrade" for "Construction"
    assert ch["chapter_title"] == ("Design Details and Construction Conditions "
                                   "Requiring Special Design Attention")
    ids = _printed_ids(7)
    assert ids[:3] == ["7.1", "7.2", "7.2.1"] and ids[-1] == "7.8"
    assert [i for i in ids if i.startswith("7.2.")] == [f"7.2.{k}" for k in range(1, 17)]
    s7 = _sections(7)
    # the old file had 7.2, 7.4 and 7.5.6 only, as summaries; 7.4 was
    # "Stabilization (Lime, Cement, Asphalt) and Geosynthetics"
    assert s7["7.4"]["title"] == "Compaction"
    assert s7["7.5.6"]["title"] == "Frost-Susceptible Soils"
    # titles as the page heads them (the contents misspells two)
    assert s7["7.2.8"]["title"] == "Dense-Graded Stabilized Base with Permeable Shoulders"
    assert s7["7.2.16"]["title"] == "Geotextile Separator and Filter Design"
    assert all(len(s["body"]) <= 14000 for s in ch["sections"])


def test_chapter_7_equations_typed_from_the_page():
    s7 = _sections(7)
    eqs = {e["id"]: e for sid in ("7.2.13", "7.2.14", "7.4.1")
           for e in s7[sid]["equations"]}
    assert eqs["Eq. 7.1"]["formula"] == "t = T × m × 24"
    assert eqs["Eq. 7.2"]["formula"] == "S1 = (LR SR)/H"
    assert eqs["Eq. 7.3"]["formula"] == "m = No LR^2/(kH) = No LR^2/ψ"
    assert eqs["Eq. 7.4"]["formula"] == "Q = (53.01/n) D^(8/3) S^(1/2)"
    assert eqs["Eq. 7.5a"]["formula"] == "qi = 2 C R"
    assert eqs["Eq. 7.6"]["formula"] == "qd = qi LR"
    # the relative compaction is numbered "Eq. 7-5" on p. 7-42, a second 7.5
    assert eqs["Eq. 7-5"]["formula"] == "CR = γd/(γd)max × 100%"
    body = s7["7.2.14"]["body"]
    assert "Q = (53.01/n) D^(8/3) S^(1/2) [Eq. 7.4]" in body
    # the Manning coefficient the text layer left on the rainfall line
    assert "= 5301" not in body
    # recomputed: 4-in. smooth pipe at 1% grade, 17800 ft3/day as printed
    assert round(53.01 / 0.012 * 4 ** (8 / 3) * 0.01 ** 0.5, -2) == 17800
    # the worked time-to-drain example (p. 7-25): 0.01 squared, not "0.012"
    body = s7["7.2.13"]["body"]
    assert "(0.01^2 + 0.02^2)^½ = 0.022" in body and "(0.012 + 0.022)" not in body
    assert round((0.01 ** 2 + 0.02 ** 2) ** 0.5, 3) == 0.022
    assert round(24 * (1 + (0.01 / 0.02) ** 2) ** 0.5, 1) == 26.8
    assert round(0.25 * 26.8 ** 2 / (1000 * 0.33), 2) == 0.54
    assert round(0.16 * 0.54 * 24, 1) == 2.1


def test_chapter_7_tables_typed_from_the_page():
    s7 = _sections(7)
    # Table 7-12: the text layer ran "All Silts" into F3; the page puts all
    # silts, very fine silty sands and clays with PI < 12 in F4 (the old file
    # said "clays and all silts F3")
    body = s7["7.5.6"]["body"]
    assert "F4 | Very high | All Silts | — | ML-MH" in body
    assert "F3 | High | Clays PI>12 | — | CL, CH" in body
    assert "F2 | Low to medium | Gravelly soils | 10-20 | GM, GC-GM, GP-GM" in body
    assert "" not in body
    text = "\n".join(s["body"] for s in _chapter(7)["sections"])
    assert "Wet-No Freeze | R | R | F | R | F | F | F | NR | NR" in text
    assert "Cracking | Slippage | Yes | No | Loss of Bond | Yes | Yes, Bond | No | No" in text
    assert "Surface Deformation | Faulting | Yes | Moisture-Suction | Erosion-Settlement" in text
    assert "Lime | Doubtful | Usually suitable | Usually suitable | Usually not suitable" in text
    # footnote marks, not digits of the cost (the text layer gave "85.002")
    assert "Geofoam (EPS) | 12 to 32 | 0.01 to .03 | 40.00 to 85.00²" in text
    assert "85.002" not in text
    # Table 7-20 print slips kept with a note
    assert "0.475-mm (#4) [as printed; Table 7-19 prints the #4 sieve as 4.75-mm]" in text
    # symbol-font glyphs of Table 7-11 written as the page's key
    assert "ï" not in text and "æ" not in text and "™" not in text
    # Table 7-18 is a picture; the text says its values are not typed in
    assert "printed as a picture on p. 7-81" in text


#: lines the scatter check passes on purpose: figure lettering left in the
#: text beside a chart (checked against the page), and one bracket the page
#: itself leaves unclosed (Eq. 7.5, noted in its equation entry)
_SCATTER_ALLOWED = (
    "A Line: PI = 0.73(LL-20)",                      # plasticity chart lettering, 4.7.2, p. 4-62
    "D 60=1 mm P 200PI=0.1",                         # figure lettering, 5.5.2.a
    "qi = C x R x 1/12 (ft/in) x 24 (hr/day) x 1 ft x 1 ft) [Eq. 7.5]",
)


def test_no_scattered_formula_glyphs():
    """The patterns the text layer leaves where it scatters a typeset
    formula: an isolated prime, lone digits beside an equals sign (the
    subscripts of "SN2 = 1 1 2.28"), equals signs with nothing between
    them ("= = ="), a formula line whose brackets do not pair, and a
    sentence repeated back to back."""
    prime = re.compile(r"(^|\s)\(?['′]\)?(\s|$)")
    eq_digits = re.compile(r"(?<![\w.,|/^-])\d \d(?![\w.,%/])|=\s*=")
    formula = re.compile(r"^[^.]{0,40}\b[A-Za-zγσφθτΔ]\w{0,6}\s*=\s*\S")
    sentence = re.compile(r"[^.!?]{30,}[.!?]")
    found = []
    for n in BUILT:
        for s in _chapter(n)["sections"]:
            for para in s["body"].split("\n\n"):
                sents = [x.strip() for x in sentence.findall(para)]
                found += [(s["section_id"], "repeated", a) for a, b in zip(sents, sents[1:])
                          if a == b]
                for line in para.split("\n"):
                    if any(a in line for a in _SCATTER_ALLOWED):
                        continue
                    if prime.search(line):
                        found.append((s["section_id"], "prime", line[:120]))
                    if "=" in line and eq_digits.search(line):
                        found.append((s["section_id"], "digits", line[:120]))
                    rhs = line.split("=", 1)[1] if "=" in line else ""
                    if (formula.search(line) and len(line) < 260 and "[as printed" not in line
                            and not re.search(r"(?:\b[a-z]{2,}\b\W+){3}", rhs)
                            and any(line.count(o) != line.count(c) for o, c in ("()", "[]", "{}"))):
                        found.append((s["section_id"], "brackets", line[:120]))
    assert not found, found


def test_chapters_1_to_4_formula_lines_read_off_the_page():
    # Eq. 3.5's last term with the page's brackets (p. 3-24)
    eqs = _equations()
    assert eqs["3.5"][1]["formula"].endswith(
        "(4.22 – 0.32pt) [log(Sc/(215.63J)) ((D^0.75 – 1.132)/(D^0.75 – 18.42/(Ec/k)^0.25))]")
    # the FWD back-calculation relations in Table 4-2, which the text layer
    # dropped (pp. 4-21, 4-22)
    body = _sections(4)["4.5.4"]["body"]
    assert ("d0 = 1.5pa {1/[MR (1 + ((D/a)(Ep/MR)^(1/3))^2)^(1/2)] + "
            "[1 – 1/(1 + (D/a)^2)^(1/2)]/Ep}") in body
    assert "MR = 0.24P/(dr r)\nr ≥ 0.7ae\nae = [a^2 + (D (Ep/MR)^(1/3))^2]^(1/2)" in body


def test_chapter_8_headings_as_printed():
    ch = _chapter(8)
    assert ch["chapter_title"] == "Construction and Design Verification for Unbound Pavement Materials"
    assert _printed_ids(8) == [
        "8.1", "8.2", "8.3", "8.3.1", "8.3.2", "8.3.3", "8.4", "8.4.1", "8.4.2",
        "8.4.3", "8.4.4", "8.4.5", "8.4.6", "8.4.7", "8.5", "8.5.1", "8.5.2",
        "8.5.3", "8.5.4", "8.5.5", "8.6", "8.7"]
    s8 = _sections(8)
    assert s8["8.4"]["title"] == "Construction and Construction Monitoring"
    assert s8["8.5.4"]["title"] == "Drainage Inspection (e.g., video logging)"
    assert s8["8.6"]["title"] == "Post-Construction Issues and Special Cases"
    assert all(len(s["body"]) <= 14000 for s in ch["sections"])


def test_chapter_8_tables_typed_from_the_page():
    s8 = _sections(8)
    # Table 8.3: the text layer lost the soil letters, the Atterberg limits
    # and the Unified classes (p. 8-11)
    body = s8["8.3.2"]["body"]
    assert "Liquid Limit, LL | 21 | NL | 35 | 64 | 36" in body
    assert "Plasticity Index, PI | 5 | --- | 21 | 35 | 9" in body
    assert "Unified Soil Classification | SC | SM | CL | CH | SC" in body
    assert "Mr = K1 SV^K2 S3^K3 with SV and S3 in English units" in body
    # PI = LL - PL as printed for A, C, D and E
    assert [21 - 16, 35 - 14, 64 - 29, 36 - 27] == [5, 21, 35, 9]
    body = s8["8.4.4"]["body"]
    assert "Plastic soils, CH, MH (A-7, A-5) | Sheepsfoot or pad foot | Pneumatic | " \
           "Thin lifts usually needed" in body
    assert "" not in body
    assert "Abrasion² | 1 per material type" in s8["8.3"]["body"]
    text = "\n".join(s["body"] for s in _chapter(8)["sections"])
    assert "above 4.4°C (40°F)" in text and "o C" not in text


#: a comparison sign the text layer gives in its symbol-font code, "≥" as
#: "$" and "≤" as "#" ("CU $4 and 1#CC #3e", "contains $ 15%", "AOS # D85");
#: money ("$ 1.50 - 4.00/m", "$14,250/$8,200") and sieve or number signs
#: ("#200", "# of passes") do not match
_COMPARISON_GLYPH = re.compile(
    r"\w[$#]|[$#][A-Za-z]|[$#]\s?\d+(?:\.\d+)?\s?(?:%|and\b|or\b)"
    r"|\b(?:contains|Pl|PI|AOS|CU|CC)\s?[$#]|[$#]\s?D\d")


def test_comparison_signs_as_printed():
    body = _sections(4)["4.7.2"]["body"]
    # Table 4-13 (p. 4-63) and its notes f, i, l, m and n (p. 4-64)
    for crit in ("CU ≥ 4 and 1 ≤ CC ≤ 3", "CU ≤ 4 and 1 ≥ CC ≥ 3",
                 "CU ≥ 6 and 1 ≤ CC ≤ 3", "CU ≤ 6 and 1 ≥ CC ≥ 3"):
        assert crit in body, crit
    assert "If soil contains ≥ 15% sand" in body and "If soil contains ≥ 15% gravel" in body
    assert "If soil contains ≥ 30% plus No. 200, predominantly sand" in body
    assert "If soil contains ≥ 30% plus No. 200, predominantly gravel" in body
    assert "n. Pl ≥ 4 and plots on or above" in body
    # the filter criterion for pumping-susceptible soils (p. 7-30)
    assert "A conservative (smaller) AOS ≤ D85 subgrade is advised" in _sections(7)["7.2.16"]["body"]
    found = [(s["section_id"], s["body"][max(0, m.start() - 30):m.end() + 30])
             for n in BUILT for s in _chapter(n)["sections"]
             for m in _COMPARISON_GLYPH.finditer(s["body"])]
    assert not found, found


def test_table_4_13_typed_from_the_page():
    body = _sections(4)["4.7.2"]["body"]
    assert "[Table 4-13 as printed on p. 4-63, typed in from the page:]" in body
    rows = body.split("[Table 4-13 as printed on p. 4-63, typed in from the page:] ")[1]
    rows = [r.strip() for r in rows.split("\n\n")[0].split("\n")]
    cells = [[c.strip() for c in r.split("|")] for r in rows]
    # one line per group symbol, every cell where the page prints it
    assert [c[3] for c in cells[1:]] == [
        "GW", "GP", "GM", "GC", "SW", "SP", "SM", "SC", "CL", "ML", "OL", "CH", "MH", "OH", "Pt"]
    assert all(len(c) == 5 for c in cells)
    assert rows[1] == ("GRAVELS More than 50% of coarse fraction retained on No. 4 sieve | "
                       "CLEAN GRAVELS Less than 5% fines | CU ≥ 4 and 1 ≤ CC ≤ 3(e) | GW | "
                       "Well-graded Gravel")
    assert rows[5].endswith("| CU ≥ 6 and 1 ≤ CC ≤ 3(e) | SW | Well-graded Sand(i)")
    # the GP and SP criteria print a CC no soil has; kept, and said
    assert "CU ≤ 4 and 1 ≥ CC ≥ 3(e) [as printed; no value of CC is both ≤ 1 and ≥ 3] | GP" in rows[2]
    assert "| PI > 7 and plots on or above \"A\" line(j) | CL | Lean Clay(k,l,m)" in rows[9]
    assert "(Liquid limit - ovendried)/(Liquid limit – not dried) < 0.75 | OL" in rows[11]
    assert rows[15].endswith("| Pt | Peat and Muskeg")
    # the notes of p. 4-64, note e with the formulas the text layer dropped
    assert ("e. CU = D60/D10 = Uniformity Coefficient (also UC)\n"
            "CC = (D30)^2/((D10)(D60)) = Coefficient of Curvature\n"
            "f. If soil contains ≥ 15% sand") in body
    assert "c. Gravels with 5 – 12% fines require dual symbols:\nGW-GM well-graded gravel with silt\n" in body
    assert "q. Pl plots below “A” line." in body
    assert "Uniformity Coefficient alsoUC" not in body


def _typed_rows(body, number, page):
    """Row name -> its cells, of a table typed in from the page."""
    label = f"[Table {number} as printed on p. {page}, typed in from the page:] "
    lines = body.split(label)[1].split("\n\n")[0].split("\n")
    return {r.split("|")[0].strip(): [c.strip() for c in r.split("|")[1:]] for r in lines}


def test_tables_1_1_to_1_3_typed_from_the_page():
    sec = _sections(1)["1.4"]
    # Table 1-2 now starts its own paragraph, so 1.4 lists it (it did not)
    assert [t.split(":")[0] for t in sec["tables"]] == ["Table 1-1", "Table 1-2", "Table 1-3"]
    cols = ["Insufficient Base Stiffness/Strength", "Insufficient Subgrade Stiffness/Strength",
            "Moisture/Drainage Problems", "Freeze/Thaw", "Swelling", "Contamination", "Erosion",
            "Spatial Variability"]

    def marks(rows, name):
        return "".join("X" if c == "X" else "." for c in rows[name])

    # each X under its own column, as printed on pp. 1-18 and 1-19
    t11 = _typed_rows(sec["body"], "1-1", "1-18")
    assert t11[""] == cols
    assert {k: marks(t11, k) for k in t11 if k} == {
        "Fatigue Cracking": "XXXX.X..", "Rutting": "XXXX.X..", "Corrugations": "X.......",
        "Bumps": "...XX..X", "Depressions": "X.XX.X.X", "Potholes": "..XX...X",
        "Roughness": "XXXXXX.X"}
    t12 = _typed_rows(sec["body"], "1-2", "1-18")
    assert {k: marks(t12, k) for k in t12 if k} == {
        "Fatigue Cracking": "XXXX.XX.", "Punchouts (CRCP)": "XXXX.XX.", "Pumping": "..X...X.",
        "Faulting": "X.XXXXX.", "Roughness": "X.XXXXXX"}
    t13 = _typed_rows(sec["body"], "1-3", "1-19")
    assert {k: marks(t13, k) for k in t13 if k} == {
        "Reflection Cracking": "X.X...X.", "Roughness": "X.XXX.XX"}
    assert "\n\nA major effect of the moisture/drainage, freeze/thaw" in sec["body"]


def test_tables_7_23a_and_7_23b_typed_from_the_page():
    body = _sections(7)["7.6.8"]["body"]
    a = _typed_rows(body, "7-23a", "7-99")
    b = _typed_rows(body, "7-23b", "7-100")
    assert a["Method"] == ["Unit Cost", "Cost of Treated Volume $/m³"]
    assert b["Method"] == ["Unit Cost", "Cost of Treated Volume $/yd³"]
    # each cost on its own method's line: the grouting unit cost is printed
    # on the permeation line, the treated-volume costs on compaction and jet
    assert a["Permeation"] == ["$ 65.00/m + $ 0.70/Liter", ""]
    assert a["Compaction"] == ["", "$ 30 - 200"] and a["Jet"] == ["", "$ 200 - 275"]
    assert b["Permeation"] == ["$ 20/ft + $ 2.65/Gallon", ""]
    assert b["Compaction"] == ["", "$ 23 - 153"] and b["Jet"] == ["", "$ 150 - 210"]
    assert a["Dry w/lime-cement"][1] == "$ 60" and a["Wet w/cement"] == ["", "$ 85 -150"]
    assert a["Dry w/lime-cement"][0].startswith("$30.00/m [printed on this line")
    assert a["Geofoam"] == ["$ 35.00 - 65.00/m³", ""]
    assert a["Stone Columns"] == ["$ 40.00 - 60.00/m", "$ 50 - 75"]
    assert b["Vibrocompaction"] == ["$ 4.60 - 7.60/ft", "$ 0.75 – 3.00"]
    assert b["Column Supported Embankments"] == ["$ 81.50/yd² + cost of column", "n/a"]
    assert "Grouting Permeation Compaction Jet" not in body


def test_degree_signs_and_exponents_as_printed():
    # the page raises an "o" for the degree sign and the exponents of the
    # NCHRP 1-37A input tables (pp. 5-113, 6-11, 6-12, 6-17 to 6-19, 6-24, 6-34)
    text = "\n".join(s["body"] for n in BUILT for s in _chapter(n)["sections"])
    assert "Pen @ 77°F" in text and "Reference temperature 70°F" in text
    assert "thermal contraction 5x10^-6/°F" in text and "thermal expansion 5.5x10^-6/°F" in text
    assert "3.25x10^-5 ft/hr" in text and "1.57x10^4 psi" in text and "4.75x10^4 psi" in text
    assert not re.search(r"(?:\d|/|-|\s)o\s?[CFK]\b|x10-?\d", text)


#: The fonts the manual sets its text in; every other font is a symbol font.
_TEXT_FONTS = ("TimesNewRoman", "Arial", "CourierNew", "BookAntiqua", "Verdana", "ComicSansMS")


def test_every_symbol_font_glyph_is_read_off_the_page():
    # WordPerfect symbol fonts give their glyphs as ordinary characters
    # ("$" for ≥ in WP-MathA, "3" for a check mark in Wingdings2): the
    # manifest's "symbol_fonts" maps them in the build, "symbol_fonts_checked"
    # names every other character a symbol font sets (looked at on 300-dpi
    # crops). A glyph in neither, or a private-use character, fails here.
    fitz = pytest.importorskip("fitz")
    if not PDF.exists():
        pytest.skip("PDF not checked out")
    vol = _manifest()
    vol = vol["volumes"][0] if "volumes" in vol else vol
    known ={f: set(vol["symbol_fonts"].get(f, {})) | set(vol["symbol_fonts_checked"].get(f, {}))
             for f in set(vol["symbol_fonts"]) | set(vol["symbol_fonts_checked"])}
    unread = set()
    with fitz.open(str(PDF)) as doc:
        for page in doc:
            for b in page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]:
                for ln in b["lines"]:
                    for s in ln["spans"]:
                        symbol = not s["font"].startswith(_TEXT_FONTS)
                        for c in s["text"]:
                            if c != " " and (symbol or 0xE000 <= ord(c) <= 0xF8FF) \
                                    and c not in known.get(s["font"], ()):
                                unread.add((s["font"], c))
    assert not unread, sorted(unread)
    text = "\n".join(s["body"] for n in BUILT for s in _chapter(n)["sections"])
    assert not re.search("[-\x80-\x9f]", text)
    assert "AOS ≤ D85" in text and "f. If soil contains ≥ 15% sand" in text
    assert "❹ Reinforcement usually applicable" in text and "⑤ Geotextile component" in text
    # the raised "o" the page prints for a degree sign ("raised_o_degree")
    assert "conical tip with 60° angle apex" in text
    assert text.count("Latitude 38.98°") == 2 and text.count("Longitude -76.94°") == 2
    assert not re.search(r"\d\s?o(?![A-Za-z])", text.replace("0.90 o Fresh", "").replace(
        "0.98 o Aged", ""))


def test_captions_keep_the_printed_source_and_units():
    # the List of Figures leaves out what a caption prints after its words
    # (manifest "captions_as_printed", and text_fixes for 3-5 and 5-5): 86
    # captions restored from the page, and Figure 8-9's, dropped, put back
    text = "\n".join(s["body"] for n in BUILT for s in _chapter(n)["sections"])
    for caption in (
        "Figure 1-3. Some common variations of flexible pavement sections (NCHRP 1-37A, 2002).",
        "Figure 5-25. Chart to modify modulus of subgrade reaction to consider effects of rigid "
        "foundation near surface (within 10 ft) (AASHTO, 1993).",
        "Figure 5-10. Influence of subgrade stiffness on critical pavement strains. (Elastic solution, "
        "6 in./150 mm AC over 18 in./450 mm granular base.",
        "Figure 8-11. Stress distributions under rollers over different foundations (after Rollings "
        "and Rollings, 1996). (1 ton = 8.9 kPa",
        "Figure 8-2. Process control, field density and moisture. (3.3 ft = 1 m)",
        "Figure 3-5. Impact of base strength on pavement structural design design (AASHTO 93 Design "
        "Guide: W18=10M, 85% reliability, So=0.4, ∆PSI=1.7, a1=0.44, m2=1, subgrade CBR=4).",
        "Figure 5-5. Laboratory sieves for mechanical analysis of grain size distribution. Shown "
        "(right to left) are sieve Nos. 3/8-in. (9.5-mm), No. 10 (2.0-mm), No. 40 (250-µm) and "
        "No. 200 (750-µm)",
        "Figure 8-8. Bulldozer (photo courtesy of Komatsu).\n\n"
        "Figure 8-9. Motor grader (photo courtesy of Caterpillar)\n\nFigure 8-10.",
    ):
        assert caption in text, caption[:40]
    # the conversions the restored captions print wrongly carry a note
    assert text.count("1 pci = 284 MN/m3 [as printed; 1 pci = 0.271 MN/m³]") == 3
    assert "8.9 kPa [as printed; a 2,000-lb ton is 8.9 kN]" in text
    assert "[As printed; the No. 40 sieve opening is 425 µm" in text


def test_every_printed_caption_is_listed_in_its_section():
    # a caption printed "Figure 4.4." or "Table 8.3.", one the List of
    # Figures gives otherwise (6-10) or leaves out (7-23a, 7-23b), one whose
    # number the text layer sets on its own line (6-13, 6-18): manifest
    # "captions_listed"; Figure 7-21 printed after its panel letters and
    # Table 4-12 cut from its rows: text_fixes
    cap = re.compile(r"(?:^|\n\n|\] )(Figure|Table)\s+(\d+)[-–.](\d+)([a-z]?)\.\s")
    listed_somewhere = set()
    for n in BUILT:
        for s in _chapter(n)["sections"]:
            listed = {x.split(":")[0] for x in s["figures"] + s["tables"]}
            listed_somewhere |= listed
            for m in cap.finditer(s["body"]):
                if m.group(2) == str(n):
                    num = f"{m.group(1)} {m.group(2)}-{m.group(3)}{m.group(4)}"
                    assert num in listed, (s["section_id"], num)
    for num in ("Figure 4-4", "Figure 6-10", "Figure 6-13", "Figure 6-18", "Figure 7-21",
                "Figure 8-9", "Table 7-23a", "Table 7-23b", "Table 8-3"):
        assert num in listed_somewhere, num
    sec = _sections(4)
    assert sec["4.5.6.d"]["body"].startswith(
        "[p. 4-53] Table 4-12. Frequently-used standards for field investigations. "
        "Standard AASHTO ASTM Title M 146 C 294")
    assert sec["4.5.6.d"]["tables"] == ["Table 4-12: Frequently-used standards for field investigations"]
