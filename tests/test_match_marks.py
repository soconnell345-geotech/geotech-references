"""Search results say how they matched (2026-11-10 review, core-05 and
core-07).

``reference_search`` and ``figure_search`` fill the places a query's every
word leaves with synonym hits and any-word hits, and ``search_sections``
gave an empty list where no section held every word. A hit that does not
hold every word now says so (``match``, ``lacks``); a size-fitted result
adds ``matched``, ``words_not_found`` and a sentence on its note, and an
empty one names the scope and the words nothing there holds. The marks are
worked out after the ranking: no hit moves.
"""

from __future__ import annotations

import pytest

from geotech_references import _figures_db, _retrieval, _retrieval_db
from geotech_references import _query_expansion as _qe

BUDGET = 14_000
NONSENSE = "zzzqqq xyzzyplugh"  # two made-up words printed nowhere


@pytest.fixture(autouse=True)
def _built():
    _retrieval_db._ensure_db()
    _figures_db._ensure_db()


@pytest.fixture
def auto(monkeypatch):
    monkeypatch.setattr(_qe, "EXPANSION_STRATEGY", "auto")


def _ids(hits):
    return [(h["reference"], h["section_id"]) for h in hits]


def test_a_hit_holding_every_word_is_not_marked(auto):
    hits = _retrieval_db.reference_search("Nordlund", limit=5)
    assert hits and all("match" not in h and "lacks" not in h for h in hits)
    out = _retrieval_db.reference_search("Nordlund", limit=5,
                                         max_chars=BUDGET)
    assert "matched" not in out and "words_not_found" not in out
    assert _ids(out["hits"]) == _ids(hits)


def test_any_word_hits_name_the_words_they_lack(auto):
    q = "micropile underwater basket weaving"
    words = ["micropile", "underwater", "basket", "weaving"]
    hits = _retrieval_db.reference_search(q, limit=5)
    assert hits
    for h in hits:
        assert h["match"] == "any word"
        assert h["lacks"] and set(h["lacks"]) < set(words)
        # the index finds each word it holds in its row, and none it lacks
        for w in words:
            found = _retrieval_db.reference_query(
                "SELECT s.section_id FROM sections_fts f JOIN sections s "
                f"ON s.rowid = f.rowid WHERE sections_fts MATCH '{w}' "
                f"AND s.reference = '{h['reference']}' "
                f"AND s.section_id = '{h['section_id']}'")
            assert bool(found) == (w not in h["lacks"]), (h, w)
    out = _retrieval_db.reference_search(q, limit=5, max_chars=BUDGET)
    assert _ids(out["hits"]) == _ids(hits)
    assert out["matched"] == "any word"
    assert set(out["words_not_found"]) == set.intersection(
        *(set(h["lacks"]) for h in hits))
    assert "do not hold every word" in out["note"]
    assert "more were found" in out["note"]


def test_a_synonym_hit_says_so(auto):
    # "wick drain" is in the PVD group; every word, a synonym for the term
    hits = _retrieval_db.reference_search("wick drain smear zone", limit=5)
    assert any(h.get("match") == "synonyms" for h in hits)
    assert all("lacks" not in h for h in hits if h.get("match") == "synonyms")


def test_an_empty_search_names_its_scope_and_the_missing_words(auto):
    out = _retrieval_db.reference_search(NONSENSE, reference="gec_12",
                                         max_chars=BUDGET)
    assert out["hits"] == [] and out["shown"] == 0
    assert out["words_not_found"] == ["zzzqqq", "xyzzyplugh"]
    assert "reference 'gec_12'" in out["note"]
    assert "any one of the words" in out["note"]
    # the plain call is still an empty list
    assert _retrieval_db.reference_search(NONSENSE, reference="gec_12") == []


def test_an_empty_search_with_synonyms_off_says_what_was_tried(monkeypatch):
    monkeypatch.setattr(_qe, "EXPANSION_STRATEGY", "off")
    out = _retrieval_db.reference_search(
        "micropile underwater basket weaving", max_chars=BUDGET)
    assert out["hits"] == []
    assert "GEOTECH_RETRIEVAL_EXPANSION=off" in out["note"]
    # every word is somewhere in the library, just not all in one section
    assert "words_not_found" not in out
    assert "no entry holds them as the query asks" in out["note"]


def test_figure_hits_are_marked_the_same_way(auto):
    q = "wick drain discharge capacity chart"
    hits = _figures_db.figure_search(q, limit=5)
    assert hits and all(h.get("match") in ("any word", "synonyms")
                        for h in hits)
    out = _figures_db.figure_search(q, limit=5, max_chars=BUDGET)
    assert [(h["reference"], h["figure_number"]) for h in out["hits"]] == \
        [(h["reference"], h["figure_number"]) for h in hits]
    assert out["matched"] in ("any word", "synonyms")
    empty = _figures_db.figure_search(NONSENSE, max_chars=BUDGET)
    assert empty["hits"] == [] and empty["words_not_found"] == [
        "zzzqqq", "xyzzyplugh"]
    assert "the figure catalogs" in empty["note"]
    lit = _figures_db.figure_search("radial drainage", limit=3)
    assert lit and all("match" not in h for h in lit)


# ---------------------------------------------------------------------------
# search_sections: no section holds every word -> the ranked search (core-07)
# ---------------------------------------------------------------------------

def test_search_sections_with_hits_is_unchanged():
    plain = _retrieval.search_sections("gec_12", "Nordlund")
    assert plain and all("match" not in s for s in plain)
    out = _retrieval.search_sections("gec_12", "Nordlund", max_chars=BUDGET)
    assert "total_hits" in out and "matched" not in out
    assert all("match" not in h for h in out["hits"])


def test_search_sections_falls_back_to_the_ranked_search(auto):
    q = "what is the nordlund method"  # "what" is in no gec_12 section
    ranked = _retrieval_db.reference_search(q, reference="gec_12", limit=3)
    plain = _retrieval.search_sections("gec_12", q, limit=3)
    # the same sections, in the ranked search's order, each whole
    assert [s["section_id"] for s in plain] == [h["section_id"]
                                                for h in ranked]
    for s, h in zip(plain, ranked):
        assert s["match"] == h.get("match", "all words")
        assert s.get("lacks") == h.get("lacks")
        assert "body" in s and s["chapter"] == h["chapter"]
    assert any(s["match"] == "any word" and s["lacks"] == ["what"]
               for s in plain)
    out = _retrieval.search_sections("gec_12", q, limit=3, max_chars=BUDGET)
    assert [h["section_id"] for h in out["hits"]] == [s["section_id"]
                                                      for s in plain]
    assert "total_hits" not in out and out["next_offset"] == 3
    assert out["matched"] == "any word" and out["words_not_found"] == ["what"]
    assert out["note"].startswith("No section holds every word as typed")
    assert all("snippet" in h for h in out["hits"])


def test_search_sections_default_limit_for_the_fallback(auto):
    plain = _retrieval.search_sections("gec_12", "what is the nordlund method")
    assert len(plain) == _retrieval.FALLBACK_LIMIT


def test_search_sections_with_no_word_found_is_still_empty(auto):
    assert _retrieval.search_sections("gec_12", NONSENSE) == []
    out = _retrieval.search_sections("gec_12", NONSENSE, max_chars=BUDGET)
    assert out["hits"] == [] and out["total_hits"] == 0
    assert out["words_not_found"] == ["zzzqqq", "xyzzyplugh"]
    assert "reference 'gec_12'" in out["note"]
