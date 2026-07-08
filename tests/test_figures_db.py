"""Tests for the figure-catalog FTS5 retrieval layer (_figures_db).

No API key / vision model required — these exercise the catalog parse and
lexical search only. Read-off (vision) is exercised in funhouse_agent tests.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from geotech_references import _figures_db

_PKG_DIR = Path(_figures_db.__file__).parent


@pytest.fixture(scope="module", autouse=True)
def _ensure_db():
    _figures_db.rebuild_db()
    yield


# ---------------------------------------------------------------------------
# Catalog integrity (committed figures_catalog.json files)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("package", ["dm7_1", "dm7_2"])
def test_catalog_file_exists_and_well_formed(package):
    cat = json.loads((_PKG_DIR / package / "figures_catalog.json")
                      .read_text(encoding="utf-8"))
    assert cat["package"] == package
    assert cat["figure_count"] == len(cat["figures"])
    assert cat["figure_count"] > 100


@pytest.mark.parametrize("package", ["dm7_1", "dm7_2"])
def test_every_figure_has_caption_and_page(package):
    cat = json.loads((_PKG_DIR / package / "figures_catalog.json")
                     .read_text(encoding="utf-8"))
    for f in cat["figures"]:
        assert f["caption"], f"empty caption for {f['figure_number']}"
        assert isinstance(f["pdf_page_index"], int)
        assert f["pdf_page_index"] >= 0


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

def test_inventory_includes_both_dm7_volumes():
    inv = {r["reference"]: r for r in _figures_db.list_indexed_figures()}
    assert "dm7_1" in inv and "dm7_2" in inv
    assert inv["dm7_1"]["n_figures"] >= 200
    assert inv["dm7_2"]["n_figures"] >= 200


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def test_search_finds_log_spiral_chart():
    """The motivating case: find Fig 4-12 (Kerisel/Absi log-spiral Ka/Kp)."""
    hits = _figures_db.figure_search("log spiral wall", reference="dm7_2", limit=5)
    nums = [h["figure_number"] for h in hits]
    assert "4-12" in nums


def test_or_fallback_recovers_when_a_term_is_absent():
    """A term not present in the text ('coefficient') must not zero the result."""
    strict = _figures_db.figure_search(
        "passive earth pressure coefficient log spiral", reference="dm7_2", limit=5
    )
    nums = [h["figure_number"] for h in strict]
    assert "4-12" in nums, "OR-fallback should still surface the log-spiral chart"


def test_search_hit_shape():
    hits = _figures_db.figure_search("bearing capacity", reference="dm7_2", limit=3)
    assert hits
    for key in ("reference", "figure_number", "caption",
                "chapter", "pdf_page_index"):
        assert key in hits[0]


def test_search_scoped_by_reference():
    hits = _figures_db.figure_search("settlement", reference="dm7_1", limit=10)
    assert hits
    assert all(h["reference"] == "dm7_1" for h in hits)


def test_search_scoped_by_chapter():
    hits = _figures_db.figure_search("earth pressure", reference="dm7_2",
                                     chapter=4, limit=10)
    assert hits
    assert all(h["chapter"] == 4 for h in hits)


def test_search_limit_capped():
    hits = _figures_db.figure_search("soil", limit=999)
    assert len(hits) <= 50


def test_search_empty_query_returns_empty():
    assert _figures_db.figure_search("   ") == []


# ---------------------------------------------------------------------------
# Get / resolve
# ---------------------------------------------------------------------------

def test_get_figure_4_12():
    g = _figures_db.figure_get("dm7_2", "4-12")
    assert g["figure_number"] == "4-12"
    assert g["chapter"] == 4
    assert g["pdf_page_index"] == 229
    assert g["pdf_path"].endswith("ufc_3_220_20_2025.pdf")
    assert "passive" in g["description"].lower()  # text-enriched


def test_get_tolerates_figure_prefix():
    g = _figures_db.figure_get("dm7_2", "Figure 4-12")
    assert g["figure_number"] == "4-12"


def test_get_prologue_figure_chapter_zero():
    g = _figures_db.figure_get("dm7_2", "P-1")
    assert g["chapter"] == 0


def test_get_appendix_figure_chapter_none():
    g = _figures_db.figure_get("dm7_2", "B-1")
    assert g["chapter"] is None


def test_get_unknown_raises():
    with pytest.raises(KeyError):
        _figures_db.figure_get("dm7_2", "99-99")


def test_resolve_pdf_points_at_existing_file():
    pdf_abs, page = _figures_db.resolve_pdf("dm7_2", "4-12")
    assert pdf_abs.exists()
    assert page == 229


# ---------------------------------------------------------------------------
# ufc_expansive Appendix C (TM 5-818-7) — scanned construction-detail figures
# added by vision read-off of the scanned pages (confirmed labels + printed
# footers). Pins the 0-based PDF page of each so the read-off renders the
# correct page.
# ---------------------------------------------------------------------------

# figure_number -> (0-based pdf page, printed page)
_UFC_EXP_APPENDIX_C = {
    "C-1": (83, "C-1"), "C-2": (84, "C-2"), "C-3": (85, "C-3"),
    "C-4": (87, "C-5"), "C-5": (88, "C-6"), "C-6": (89, "C-7"),
    "C-7": (90, "C-8"), "C-8": (91, "C-9"), "C-9": (92, "C-10"),
    "C-10": (93, "C-11"),
}


def test_ufc_expansive_catalog_complete():
    cat = json.loads((_PKG_DIR / "ufc_expansive" / "figures_catalog.json")
                     .read_text(encoding="utf-8"))
    assert cat["package"] == "ufc_expansive"
    assert cat["figure_count"] == len(cat["figures"]) == 42
    for f in cat["figures"]:
        assert f["caption"], f"empty caption for {f['figure_number']}"
        assert isinstance(f["pdf_page_index"], int) and f["pdf_page_index"] >= 0
        assert f["page_estimated"] is False, f"{f['figure_number']} still estimated"


def test_ufc_expansive_appendix_c_pages():
    for num, (page, printed) in _UFC_EXP_APPENDIX_C.items():
        g = _figures_db.figure_get("ufc_expansive", num)
        assert g["figure_number"] == num
        assert g["chapter"] == "C"
        assert g["pdf_page_index"] == page, f"{num}: {g['pdf_page_index']} != {page}"
        assert g["printed_page"] == printed


def test_ufc_expansive_appendix_c_resolves_to_existing_pages():
    for num, (page, _printed) in _UFC_EXP_APPENDIX_C.items():
        pdf_abs, resolved = _figures_db.resolve_pdf("ufc_expansive", num)
        assert pdf_abs.exists() and str(pdf_abs).endswith("ufc_3_220_07.pdf")
        assert resolved == page


def test_ufc_expansive_appendix_c_searchable():
    steel = [h["figure_number"] for h in _figures_db.figure_search(
        "wall ties to steel beam", reference="ufc_expansive", limit=5)]
    assert "C-4" in steel
    mat = [h["figure_number"] for h in _figures_db.figure_search(
        "ribbed mat foundation", reference="ufc_expansive", limit=5)]
    assert "C-9" in mat
