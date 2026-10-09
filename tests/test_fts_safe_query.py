"""Plain-text queries FTS5 cannot parse as written.

A user's words go straight to FTS5 MATCH, where '-' and similar are query
syntax: "EM 1110-2-1902", "pseudo-static" and "Table 5-2" failed with
"no such column: ..." (GeotechStaffEngineer live smoke wave 1, A11). Such a
query is now run again with those tokens quoted as phrases; valid FTS5 syntax
is untouched.
"""

import sqlite3

import pytest

from geotech_references._figures_db import figure_search
from geotech_references._retrieval_db import (
    fts_safe_query, plain_terms, reference_search, search_fts_safely)

HYPHENATED = [
    "EM 1110-2-1902 rapid drawdown",
    "rapid drawdown pseudo-static",
    "Table 5-2 bearing capacity factors Terzaghi",
    "c'-phi' strength",
    "K0 (at-rest) coefficient",
]


@pytest.mark.parametrize("query", HYPHENATED)
def test_reference_search_answers_hyphenated_queries(query):
    hits = reference_search(query, limit=5)
    assert not any("error" in h for h in hits), hits


@pytest.mark.parametrize("query", HYPHENATED)
def test_figure_search_answers_hyphenated_queries(query):
    hits = figure_search(query, limit=5)
    assert not any("error" in h for h in hits), hits


def test_hyphenated_terms_still_find_their_sections():
    hits = reference_search("rapid drawdown pseudo-static", limit=10)
    assert hits and all("section_id" in h for h in hits)


def test_fts_safe_query_quotes_only_what_fts5_cannot_read():
    assert fts_safe_query("EM 1110-2-1902 rapid") == 'EM "1110 2 1902" rapid'
    assert fts_safe_query("pseudo-static") == '"pseudo static"'
    assert fts_safe_query("Table 5-2") == 'Table "5 2"'
    # valid syntax is kept: phrases, operators, prefix
    assert fts_safe_query('"passive earth" OR wall') == '"passive earth" OR wall'
    assert fts_safe_query("consolid* NOT clay") == "consolid* NOT clay"
    # stray punctuation and dangling operators go
    assert fts_safe_query("(settlement") == "settlement"
    assert fts_safe_query("OR footing -") == "footing"
    assert plain_terms("c'-phi' (5-2)") == "c phi 5 2"


def test_a_valid_query_is_never_rewritten():
    calls = []

    def search(q):
        calls.append(q)
        return ["hit"]

    assert search_fts_safely(search, "slope stability") == ["hit"]
    assert calls == ["slope stability"]


def test_a_query_that_fails_both_ways_raises_the_first_error():
    def search(q):
        raise sqlite3.OperationalError(f"bad: {q}")

    with pytest.raises(sqlite3.OperationalError, match="bad: a-b"):
        search_fts_safely(search, "a-b")
