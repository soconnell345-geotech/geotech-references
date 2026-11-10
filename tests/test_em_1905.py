"""EM 1110-1-1905, Geotechnical Design of Shallow Foundations on Soils
(USACE, 31 July 2025).

The chapter text is read off the printed pages by
``scripts/build_printed_text.py`` (layout "army") and the figure catalog by
``scripts/build_figure_catalog.py``. These check that the text is there and
findable at every level the app uses (search, section, figure), that the
paragraph numbers address every level, that each figure is on the page that
prints its caption, and that the equations are the ones typed in from the
page.
"""

import json
import unicodedata
from pathlib import Path

import pytest

from geotech_references import _figures_db, _retrieval, _retrieval_db

REF = "em_1905"
ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references" / REF
PDF = ROOT / "docs" / "EM_1110-1-1905_2025.pdf"


def _chapters():
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((PKG / "text").glob("chapter*.json"))]


def _catalog():
    return json.loads((PKG / "figures_catalog.json").read_text(encoding="utf-8"))


def _pdf():
    fitz = pytest.importorskip("fitz")
    if not PDF.exists():
        pytest.skip("PDF not checked out")
    return fitz.open(str(PDF))


def test_twelve_chapters_and_appendices_b_to_d():
    chapters = _chapters()
    assert [c["chapter"] for c in chapters] == list(range(1, 16))
    for c in chapters:
        assert c["reference_id"] == "EM 1110-1-1905"
        assert c["volume"] is None
    titles = {c["chapter"]: c["chapter_title"] for c in chapters}
    assert titles[5] == "Ultimate Limit State for Static Analysis"
    assert titles[7] == "Settlement"
    assert titles[13].startswith("Appendix B: Design Examples")
    assert titles[14] == "Appendix C: Design Examples: Settlement for Static Analysis"
    assert titles[15] == "Appendix D: Common Unit Conversion Factors"
    assert sum(len(c["sections"]) for c in chapters) == 778


def test_every_section_carries_its_printed_pages():
    for c in _chapters():
        for s in c["sections"]:
            # a heading followed straight by its first subparagraph has no text
            assert s["body"] == "" or s["body"].startswith("[p. "), s["section_id"]
            # a split part says which pages it continues over
            assert "printed p" in s["applicability"] or (
                s["applicability"].startswith("Part ")
                and "letter is not printed" in s["applicability"]), s["section_id"]


def test_section_bodies_fit_the_reference_tools():
    # the app sends at most 16,000 characters of a tool's result, and
    # wraps a section in about 300 more
    for c in _chapters():
        for s in c["sections"]:
            assert len(json.dumps(s)) <= 14000, s["section_id"]
    # the three printed paragraphs too long for that are split into
    # lettered parts, the letters not printed
    for sid in ("7-11c(2)", "C-2b", "C-7b"):
        part = _retrieval.retrieve_section(REF, sid + ".a")
        assert part["parent_id"] == sid
        assert "(continued, pp. " in part["title"]


def test_paragraph_numbers_address_every_level():
    sec = _retrieval.retrieve_section(REF, "2-7a(2)")
    assert sec["title"] == "Differential settlement"
    assert sec["parent_id"] == "2-7a"
    assert sec["under"] == ("2-7 Serviceability limit state requirements > "
                            "2-7a Allowable movements")
    kids = [k["section_id"] for k in sec["children"]]
    assert kids[:4] == ["2-7a(2)(a)", "2-7a(2)(b)", "2-7a(2)(c)", "2-7a(2)(d)"]
    assert _retrieval.retrieve_section(REF, "2-7a(2)(c)1")["parent_id"] == "2-7a(2)(c)"
    # an appendix's opening text lists its examples
    sec = _retrieval.retrieve_section(REF, "B")
    assert sec["children"][0]["section_id"] == "B-1"
    # a number not printed names the nearest paragraph above it
    with pytest.raises(KeyError, match="5-5a Shear zone for bearing capacity"):
        _retrieval_db.reference_get(REF, "5-5a(9)")


def test_section_lookup_through_the_database():
    row = _retrieval_db.reference_get(REF, "5-5b")
    assert row["title"] == "Bearing capacity equation"
    assert row["body"].startswith("[p. 104] Bearing capacity equation.")
    assert "[Eq. 5-21]" in row["body"]


def test_search_finds_the_bearing_capacity_paragraphs():
    hits = _retrieval_db.reference_search("bearing capacity", reference=REF)
    top = [h["section_id"] for h in hits[:5]]
    assert "5-5b" in top and "5-5" in top
    hits = _retrieval_db.reference_search("Menard pressuremeter settlement",
                                          reference=REF)
    assert "7-11c" in [h["section_id"] for h in hits[:5]]


def test_every_listed_equation_is_marked_in_its_section():
    for c in _chapters():
        for s in c["sections"]:
            for e in s["equations"]:
                assert f"[{e['id']}]" in s["body"], (s["section_id"], e["id"])


def test_table_cells_read_row_by_row():
    body = _retrieval.retrieve_section(REF, "2-6b(1)")["body"]
    rows = body[body.index("Table 2-1 Minimum factors of safety for ultimate limit state"):]
    assert "ULS Failure Mode | Minimum Factor of Safety, FS\nBearing capacity | 3.0[1]\n" \
        "Sliding | 2.0[2]\nOverturning moment and eccentricity | Note 3\nUplift | 1.5" in rows
    # a worked example's summary table, row by row (p. 297)
    body = _retrieval.retrieve_section(REF, "B-1c")["body"]
    rows = body[body.index("Table B-1b Summary of calculations for Example B-1"):]
    assert "Row | Symbol | USACE | FHWA\n1 | B (ft) | 7 | 7" in rows
    assert "14 | qult (ksf) | 3.51 | 3.32" in rows
    assert "18 | FS | 3.1 | 3" in rows


def test_table_typed_in_from_the_page():
    # Table 4-10 (p. 89) is printed as two tables side by side; the manifest
    # (printed_tables) gives its rows
    body = _retrieval.retrieve_section(REF, "4-10d(1)(f)")["body"]
    rows = body[body.index("[Table 4-10 is printed as two tables"):]
    assert "Clay | Soft | Medium | Stiff | Very Stiff | Hard\n" \
        "P*L (tsf) | 0 to 2 | 2 to 4 | 4 to 8 | 8 to 16 | > 16" in rows
    assert "Sand | Loose | Compact | Dense | Very Dense" in rows


def test_print_quirk_kept_as_printed():
    # Table 5-3's AASHTO cell for the inclination factor on N-gamma prints iq
    body = _retrieval.retrieve_section(REF, "5-5f")["body"]
    assert "iγ | iγ = [1 − β/φ′]^2 | iq = [1 − tanβ]^(n+1)" in body


# --- figures ----------------------------------------------------------------

#: figure -> (printed page, 0-based PDF page, chapter file). Lettered appendix
#: figures (C-2a) and figures captioned inside a table cell (8-4, C-2c, C-4b)
#: included; Figure 7-10 prints a caption with no picture.
FIGURES = {
    "2-1": (6, 20, 2), "4-7": (85, 99, 4), "6-7": (135, 149, 6),
    "7-6": (159, 173, 7), "7-10": (166, 180, 7), "8-4": (201, 215, 8),
    "8-11": (211, 225, 8), "9-6": (230, 244, 9), "B-1": (295, 309, 13),
    "C-1": (339, 353, 14), "C-2a": (343, 357, 14), "C-2c": (346, 360, 14),
    "C-4b": (361, 375, 14),
}


def test_catalog_covers_every_figure():
    cat = _catalog()
    assert cat["figure_count"] == len(cat["figures"]) == 136
    assert not any(f["page_estimated"] for f in cat["figures"])
    assert all(f["description"] for f in cat["figures"])
    assert cat["pdf_path"] == "docs/EM_1110-1-1905_2025.pdf"
    nums = [f["figure_number"] for f in cat["figures"]]
    assert nums[0] == "2-1" and nums[-1] == "C-7b"
    # every figure the chapter text lists is in the catalog
    listed = {x.split(":")[0].removeprefix("Figure ")
              for c in _chapters() for s in c["sections"] for x in s["figures"]}
    assert listed == set(nums)


def test_figure_lookup():
    for num, (page, idx, chapter) in FIGURES.items():
        fig = _figures_db.figure_get(REF, num)
        assert (fig["printed_page"], fig["pdf_page_index"], fig["chapter"]) == \
            (page, idx, chapter), num
        pdf, i = _figures_db.resolve_pdf(REF, num)
        assert pdf.name == PDF.name and i == idx, num
    # printed page = PDF page - 15 throughout
    for f in _catalog()["figures"]:
        assert f["pdf_page_index"] == f["printed_page"] + 14, f["figure_number"]


def test_figure_search_finds_the_influence_charts():
    hits = _figures_db.figure_search("influence factor vertical stress", reference=REF)
    assert {"6-7", "6-8", "6-10"} <= {h["figure_number"] for h in hits[:5]}


def _squash(text):
    # a caption on its page sets symbols in mathematical bold italic letters
    # and numbers with en dashes, and may print a dash the Figure List prints
    # as a hyphen (Figure 7-19, "void ratio—logarithm time"); letters and
    # digits are compared
    text = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in text.lower() if ch.isalnum())


def test_catalog_pages_are_the_caption_pages():
    with _pdf() as doc:
        for f in _catalog()["figures"]:
            page = _squash(doc[f["pdf_page_index"]].get_text())
            want = _squash(f"Figure {f['figure_number']}. {f['caption']}")[:40]
            assert want in page, f["figure_number"]


def test_cover_designation():
    with _pdf() as doc:
        cover = doc[0].get_text()
    assert "EM 1110-1-1905 ● 31 July 2025" in cover
    assert "Geotechnical Design of Shallow Foundations on Soils" in cover
    for c in _chapters():
        assert c["reference_id"] == "EM 1110-1-1905"


# --- the equations as printed ---------------------------------------------


def _equations():
    out = {}
    for c in _chapters():
        for s in c["sections"]:
            for e in s["equations"]:
                out.setdefault(e["id"][4:], (s["section_id"], e))
    return out


def test_every_equation_has_its_printed_formula():
    eqs = _equations()
    assert len(eqs) == 213
    per_chapter = {}
    for num, (sid, e) in eqs.items():
        per_chapter[int(num.split("-")[0])] = per_chapter.get(int(num.split("-")[0]), 0) + 1
        assert e.get("formula"), num
        assert e["source"].startswith("Typed in from p. "), num
        assert "variables" in e, num
    assert per_chapter == {2: 8, 3: 51, 4: 21, 5: 36, 6: 13, 7: 48, 8: 31, 9: 5}


def test_formulas_as_printed():
    # spot checks against the rendered pages
    eqs = _equations()
    assert eqs["5-21"][1]["formula"] == \
        "qult = c · Nc + q0 · Nq + (1/2) B · γ′ · Nγ   (Continuous Footing)"
    assert "ksf" in eqs["5-21"][1]["variables"]["qult"]
    assert eqs["3-21"][1]["formula"] == "Hydraulic Conductivity, k = Cv · mv · γw"
    assert eqs["8-19"][1]["formula"] == "D = (EC · t^3)/(12(1 − μC^2))"
    assert eqs["6-9"][1]["formula"] == \
        "Iσ = 1 − (1/(1 + (B/(2z))^2))^1.76   (Square Loaded Area)"
    # a formula that differs from its neighbours is typed as printed and said
    assert eqs["7-15"][1]["formula"] == "EL = n/(1/E1 + 1/E2 + ⋯1/En)"
    assert eqs["7-15"][1]["notes"].startswith("As printed")
    assert "As printed" in eqs["5-17"][1]["notes"]
    assert "As printed" in eqs["9-5"][1]["notes"]


def test_manifest_formulas_match_the_text():
    manifest = json.loads((ROOT / "scripts" / "manifests" / f"{REF}.json")
                          .read_text(encoding="utf-8"))
    eqs = _equations()
    n = 0
    for vol in manifest["volumes"]:
        for p in vol.get("printed_equations", []):
            assert eqs[p["number"]][1]["formula"] == p["formula"], p["number"]
            n += 1
    assert n == 213


def test_rebuild_reproduces_the_committed_text():
    # the formulas, passages and Table 4-10 live in the manifest, so a
    # rebuild keeps them
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
    assert sorted(chapters) == list(range(1, 16))
    for n, data in chapters.items():
        assert data.pop("_missing") == [], f"chapter {n}"
        committed = (PKG / "text" / f"chapter{n:02d}.json").read_text(encoding="utf-8")
        assert builder.chapter_json(data) == committed, f"chapter {n}"
