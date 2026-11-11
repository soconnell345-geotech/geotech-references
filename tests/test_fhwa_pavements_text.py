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
BUILT = [1, 2]


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
