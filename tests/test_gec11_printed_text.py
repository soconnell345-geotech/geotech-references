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
BUILT = (1, 2)


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
