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

REF = "fhwa_pavements"
ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references" / REF
PDF = ROOT / "docs" / "FHWA-NHI-05-037 - Geotech Pavements.pdf"
#: the chapters rebuilt from the print so far
BUILT = [1, 2, 3, 4]


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
            if int(p["number"].split(".")[0]) in BUILT and p.get("formula"):
                assert eqs[p["number"]][1]["formula"] == p["formula"], p["number"]
                assert eqs[p["number"]][1]["source"] == f"Typed in from p. {p['page']}."


def test_rebuild_reproduces_the_committed_text():
    pytest.importorskip("fitz")
    if not PDF.exists():
        pytest.skip("PDF not checked out")
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
