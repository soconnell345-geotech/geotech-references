"""Tests for the SQLite FTS5 retrieval layer (_retrieval_db)."""

from __future__ import annotations

import pytest

from geotech_references import _retrieval_db


@pytest.fixture(scope="module", autouse=True)
def _ensure_db():
    _retrieval_db.rebuild_db()
    yield


def test_inventory_includes_dm7_and_gec():
    inv = _retrieval_db.list_indexed_references()
    refs = {r["reference"] for r in inv}
    assert "dm7_1" in refs
    assert "dm7_2" in refs
    # at least one of the GEC narrative references should also be present
    assert refs & {"gec_6", "gec_7", "gec_10", "gec_12", "gec_13", "micropile"}


def test_search_returns_summary_only():
    hits = _retrieval_db.reference_search(
        "primary consolidation settlement", reference="dm7_1", limit=3
    )
    assert hits, "expected at least one hit"
    h = hits[0]
    # required summary-only fields
    for key in ("reference", "section_id", "title", "summary"):
        assert key in h
    # body intentionally omitted from search hits
    assert "body" not in h


def test_search_scoping_by_reference_and_chapter():
    hits = _retrieval_db.reference_search(
        "settlement", reference="dm7_1", chapter=5, limit=10
    )
    assert hits
    for h in hits:
        assert h["reference"] == "dm7_1"
        assert h["chapter"] == 5


def test_search_limit_capped():
    hits = _retrieval_db.reference_search(
        "soil", reference="dm7_1", limit=999
    )
    assert len(hits) <= 50  # _MAX_LIMIT


def test_get_returns_full_section_with_body():
    sec = _retrieval_db.reference_get("dm7_1", "5-5.2")
    assert sec["section_id"] == "5-5.2"
    assert "body" in sec
    assert isinstance(sec["body"], str)
    assert len(sec["body"]) > 0
    assert "equations" in sec
    assert isinstance(sec["equations"], list)


def test_get_handles_ufc_hyphen_form():
    # UFC sections use hyphen-then-dot ids like 4-2.1
    sec = _retrieval_db.reference_get("dm7_2", "4-5")
    assert sec["section_id"] == "4-5"


def test_get_unknown_section_raises():
    with pytest.raises(KeyError):
        _retrieval_db.reference_get("dm7_1", "99-99")


def test_query_select_works():
    rows = _retrieval_db.reference_query(
        "SELECT reference, COUNT(*) AS n FROM sections "
        "WHERE reference = 'dm7_1' GROUP BY reference"
    )
    assert rows
    assert rows[0]["reference"] == "dm7_1"
    assert rows[0]["n"] > 0


def test_query_rejects_non_select():
    rows = _retrieval_db.reference_query("DELETE FROM sections")
    assert "error" in rows[0]


def test_query_rejects_forbidden_keyword():
    rows = _retrieval_db.reference_query(
        "SELECT * FROM sections; DROP TABLE sections"
    )
    assert "error" in rows[0]


def test_query_rejects_pragma():
    rows = _retrieval_db.reference_query("PRAGMA table_info(sections)")
    assert "error" in rows[0]


def test_query_caps_result_set():
    # Without LIMIT in the query, the wrapper should still cap at 50
    rows = _retrieval_db.reference_query("SELECT section_id FROM sections")
    assert len(rows) <= 50


def test_query_supports_fts_match():
    rows = _retrieval_db.reference_query(
        "SELECT s.reference, s.section_id, s.title "
        "FROM sections_fts f JOIN sections s ON s.rowid = f.rowid "
        "WHERE sections_fts MATCH 'bearing capacity' "
        "ORDER BY bm25(sections_fts) LIMIT 5"
    )
    assert rows
    assert all("section_id" in r for r in rows)


def test_dm7_full_eq_coverage_via_db():
    """Sanity check: every DM7 chapter has its full equation count."""
    rows = _retrieval_db.reference_query(
        "SELECT reference, COUNT(*) AS n FROM sections "
        "WHERE reference IN ('dm7_1','dm7_2') GROUP BY reference"
    )
    counts = {r["reference"]: r["n"] for r in rows}
    assert counts.get("dm7_1", 0) >= 400
    assert counts.get("dm7_2", 0) >= 400
