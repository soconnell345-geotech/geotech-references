"""Tests for the lexical query-expansion recall lever (``_query_expansion``)
and its wiring into ``reference_search`` / ``figure_search``.

No API key / embedding model required — pure lexical FTS5.

Two layers:
* ``expand_query`` / ``merge_hits`` — deterministic unit tests.
* search integration — the precision-safe invariants (literal hits stay a
  prefix; expansion only adds) and a concrete synonym-recovery case.
"""

from __future__ import annotations

import pytest

from geotech_references import _retrieval_db, _figures_db
from geotech_references._query_expansion import expand_query, merge_hits


@pytest.fixture(scope="module", autouse=True)
def _ensure_dbs():
    _retrieval_db.rebuild_db()
    _figures_db.rebuild_db()
    yield


@pytest.fixture(autouse=True)
def _baseline_strategy():
    """Pin a known strategy per test so assertions don't depend on the module
    default (which is env-driven). Tests that exercise a specific strategy set
    it explicitly within the test body."""
    import geotech_references._query_expansion as qe
    saved = qe.EXPANSION_STRATEGY
    qe.EXPANSION_STRATEGY = "fill"
    yield
    qe.EXPANSION_STRATEGY = saved


# ---------------------------------------------------------------------------
# expand_query — pure function
# ---------------------------------------------------------------------------

def test_empty_and_whitespace_expand_to_nothing():
    assert expand_query("") == ""
    assert expand_query("   ") == ""


def test_unknown_terms_expand_to_nothing():
    assert expand_query("hello world foobar") == ""


def test_expansion_is_symmetric():
    # A query using ANY member of a group expands to the others.
    assert "wall friction" in expand_query("interface friction at the wall")
    assert "interface friction" in expand_query("wall friction angle delta")


def test_terms_already_present_are_not_repeated():
    exp = expand_query("drilled shaft side resistance")
    # "drilled shaft" and "side resistance" are in the query -> not re-added;
    # their group-mates ARE added.
    assert "drilled shaft" not in exp.split(" OR ")
    assert any(t in exp for t in ("bored pile", "caisson"))
    assert any(t in exp for t in ("skin friction", "shaft resistance"))


def test_single_token_word_boundary_no_false_fire():
    # "ka"/"ko" must match as whole tokens, not inside other words.
    assert expand_query("kayak racing on a lake") == ""
    assert expand_query("make a cake") == ""


def test_notation_token_fires_group():
    # "kp" -> passive earth pressure group
    exp = expand_query("kp value for the wall")
    assert "passive earth pressure" in exp


def test_returned_clause_is_valid_fts_or_syntax():
    exp = expand_query("bored pile downdrag")
    assert " OR " in exp
    # multi-word terms are quoted; bare tokens are not
    assert '"neutral plane"' in exp or '"negative skin friction"' in exp


# ---------------------------------------------------------------------------
# merge_hits — pure function
# ---------------------------------------------------------------------------

def test_merge_preserves_literal_prefix_and_dedups():
    lit = [{"id": 1}, {"id": 2}]
    extra = [{"id": 2}, {"id": 3}, {"id": 4}]
    out = merge_hits(lit, extra, limit=3, key=lambda h: h["id"])
    assert [h["id"] for h in out] == [1, 2, 3]   # literal first, dedup 2, cap 3


def test_merge_respects_limit_with_only_literal():
    lit = [{"id": i} for i in range(10)]
    out = merge_hits(lit, [], limit=4, key=lambda h: h["id"])
    assert [h["id"] for h in out] == [0, 1, 2, 3]


# ---------------------------------------------------------------------------
# search integration — precision-safe invariants
# ---------------------------------------------------------------------------

def _literal(fn, query, **kw):
    """Run a search with expansion disabled (literal baseline)."""
    import geotech_references._query_expansion as qe
    saved = qe.EXPANSION_STRATEGY
    qe.EXPANSION_STRATEGY = "off"
    try:
        return fn(query, **kw)
    finally:
        qe.EXPANSION_STRATEGY = saved


_SYNONYM_QUERIES = [
    "negative skin friction on a pile",
    "bored pile skin friction",
    "phreatic surface drawdown",
    "interface adhesion against the wall",
    "underseepage control",
]


@pytest.mark.parametrize("query", _SYNONYM_QUERIES)
def test_reference_expansion_never_shrinks_results(query):
    lit = _literal(_retrieval_db.reference_search, query, limit=5)
    exp = _retrieval_db.reference_search(query, limit=5)
    assert len(exp) >= len(lit)


@pytest.mark.parametrize("query", _SYNONYM_QUERIES)
def test_reference_literal_hits_are_a_prefix(query):
    """Precision-safe: expansion appends; it never reorders/drops literal hits."""
    lit = _literal(_retrieval_db.reference_search, query, limit=5)
    exp = _retrieval_db.reference_search(query, limit=5)
    lit_keys = [(h.get("reference"), h.get("section_id")) for h in lit]
    exp_keys = [(h.get("reference"), h.get("section_id")) for h in exp]
    assert exp_keys[: len(lit_keys)] == lit_keys


def test_synonym_query_recovers_when_literal_is_empty():
    """The headline case: a pure synonym miss returns nothing literally but is
    recovered by expansion."""
    q = "groundwater control underseepage"
    lit = _literal(_retrieval_db.reference_search, q, limit=5)
    exp = _retrieval_db.reference_search(q, limit=5)
    assert len(lit) == 0          # literal AND-match finds nothing
    assert len(exp) > 0           # expansion recovers real sections


def test_at_least_one_query_shows_strict_recall_lift():
    lifted = 0
    for q in _SYNONYM_QUERIES + ["groundwater control underseepage"]:
        lit = _literal(_retrieval_db.reference_search, q, limit=5)
        exp = _retrieval_db.reference_search(q, limit=5)
        if len(exp) > len(lit):
            lifted += 1
    assert lifted >= 1


# ---------------------------------------------------------------------------
# figure search — regression + invariant
# ---------------------------------------------------------------------------

def _with_strategy(strategy, fn, query, **kw):
    import geotech_references._query_expansion as qe
    saved = qe.EXPANSION_STRATEGY
    qe.EXPANSION_STRATEGY = strategy
    try:
        return fn(query, **kw)
    finally:
        qe.EXPANSION_STRATEGY = saved


def test_auto_pins_literal_top1():
    """'auto' reranks the union but keeps the literal top-1 — so an already-good
    query's best hit is never displaced."""
    q = "undrained shear strength of clay"
    off = _literal(_retrieval_db.reference_search, q, limit=5)
    auto = _with_strategy("auto", _retrieval_db.reference_search, q, limit=5)
    assert off and auto
    assert (off[0]["reference"], off[0]["section_id"]) == \
           (auto[0]["reference"], auto[0]["section_id"])


def test_auto_recovers_empty_literal():
    """When the literal query returns nothing, 'auto' falls through to the
    reranked union (it must not return empty just because there's no top-1)."""
    q = "groundwater control underseepage"
    off = _literal(_retrieval_db.reference_search, q, limit=5)
    auto = _with_strategy("auto", _retrieval_db.reference_search, q, limit=5)
    assert len(off) == 0
    assert len(auto) > 0


def test_zero_hit_or_fallback_in_auto_not_off():
    """A query whose tokens never co-occur (and whose synonyms add nothing
    matchable) returns nothing literally — 'auto' must recover via the
    OR-of-terms fallback, while 'off' stays the pure-literal anchor."""
    # (was "liquefaction triggering CRR", which GEC-13 Ch. 4 Sec. 1.6 now
    # holds in one section since REF-25 rebuilt it from the print)
    q = "tieback triggering CRR"
    off = _literal(_retrieval_db.reference_search, q, limit=5)
    auto = _with_strategy("auto", _retrieval_db.reference_search, q, limit=5)
    assert len(off) == 0
    assert len(auto) > 0


def test_combined_query_unions_literal_and_synonyms():
    from geotech_references._query_expansion import combined_query
    cq = combined_query("bored pile downdrag")
    assert cq.startswith("(bored pile downdrag) OR ")
    # no concept -> unchanged
    assert combined_query("hello world") == "hello world"


def test_rerank_strategy_runs_and_returns_hits():
    import geotech_references._query_expansion as qe
    saved = qe.EXPANSION_STRATEGY
    qe.EXPANSION_STRATEGY = "rerank"
    try:
        hits = _retrieval_db.reference_search("interface adhesion on the wall",
                                              limit=5)
        assert hits and all("error" not in h for h in hits)
    finally:
        qe.EXPANSION_STRATEGY = saved


def test_figure_search_still_finds_log_spiral_chart():
    """Existing behavior preserved: Fig 4-12 still surfaces."""
    hits = _figures_db.figure_search("passive earth pressure log spiral",
                                     reference="dm7_2", limit=5)
    assert "4-12" in [h["figure_number"] for h in hits]


def test_figure_fill_preserves_literal_top_and_never_shrinks():
    """Precision-safe (figures): 'fill' appends only — so when the literal run is
    non-empty, the rank-1 hit is unchanged, and the result never shrinks.

    (The full prefix invariant that holds for text does NOT hold for figures,
    because even 'off' mode runs the pre-existing OR-of-terms fallback; only the
    literal run(query) results — and thus rank-1 — are guaranteed preserved.)"""
    q = "passive earth pressure on a wall"
    off = _literal(_figures_db.figure_search, q, reference="dm7_2", limit=5)
    fill = _figures_db.figure_search(q, reference="dm7_2", limit=5)
    assert off and fill
    assert off[0]["figure_number"] == fill[0]["figure_number"]
    assert len(fill) >= len(off)


# ---------------------------------------------------------------------------
# REF-03: the curated map
# ---------------------------------------------------------------------------

def test_bare_cu_does_not_fire_undrained_strength():
    # Cu is also the coefficient of uniformity (UFC 3-220-10 Sec. 1-3.3.2)
    assert "undrained" not in expand_query("coefficient of uniformity cu")
    assert "undrained shear strength" in expand_query("su of soft clay")


def test_bare_compaction_does_not_fire_compaction_control():
    # deep dynamic compaction / vibro-compaction are ground improvement
    assert "proctor" not in expand_query("dynamic compaction depth of improvement")
    assert "proctor" not in expand_query("vibro-compaction of loose sand")
    assert "relative compaction" in expand_query("degree of compaction of fill")


def test_term_inside_a_longer_matched_term_does_not_fire_its_group():
    exp = expand_query("negative skin friction on piles")
    assert "downdrag" in exp
    assert "side resistance" not in exp and "shaft resistance" not in exp
    # the shorter term alone still fires its own group
    assert "side resistance" in expand_query("skin friction of piles")


def test_liquefaction_demand_and_capacity_stay_apart():
    assert "crr" not in expand_query("csr from the earthquake")
    assert "csr" not in expand_query("crr of the sand")
    assert expand_query("liquefaction") == ""  # no dead triggering forms


@pytest.mark.parametrize("query, expected", [
    ("PVD spacing", "wick drain"),
    ("PVDs spacing", "wick drain"),
    ("CSR", "cyclic stress ratio"),
    ("(N1)60 to phi", "n160"),
    ("N160 to phi", '"n1 60"'),
    ("p-y method", '"p y curve"'),
    ("t-z curves", '"load transfer curve"'),
    ("CPT", "cone penetration test"),
    ("SPT", "standard penetration test"),
    ("DMT", "dilatometer"),
    ("PMT", "pressuremeter"),
    ("UCS of rock", "uniaxial compressive strength"),
    ("RQD", "rock quality designation"),
    ("EPS blocks", "geofoam"),
    ("stone column", "aggregate pier"),
    ("vibroflotation", '"vibro compaction"'),
    ("DSM", "deep mixing"),
    ("CFA piles", "continuous flight auger"),
    ("MSE", "mechanically stabilized earth"),
])
def test_added_groups_fire(query, expected):
    assert expected in expand_query(query)


@pytest.mark.parametrize("query", [
    "(N1)60 to phi", "N1(60) correlation", "p-y curves", "t-z curves",
    "augered cast-in-place piles", "MSE wall", "what is RQD",
])
def test_expanded_queries_are_valid_fts(query):
    for strategy in ("fill", "auto", "rerank"):
        hits = _with_strategy(strategy, _retrieval_db.reference_search,
                              query, limit=5)
        assert hits and all("error" not in h for h in hits), (strategy, hits)


def test_spelling_of_a_form_already_used_is_not_added_again():
    exp = expand_query("N1(60) correlation")
    assert '"n1 60"' not in exp and "n160" in exp


def test_substituted_query():
    from geotech_references._query_expansion import substituted_query
    assert substituted_query("wick drain smear zone") == (
        '("prefabricated vertical drain" OR pvd OR "wick drain" OR '
        '"vertical drain") AND smear AND zone')
    assert substituted_query("hello world") is None
    assert substituted_query('"wick drain" smear') is None
    assert substituted_query("pvd OR smear") is None


def test_auto_zero_literal_keeps_the_words_the_groups_do_not_cover():
    # The literal AND query matches nothing; swapping "wick drain" for its
    # group keeps "smear zone" in the query (FHWA-NHI-16-027 Sec. 2.4.3).
    q = "wick drain smear zone"
    assert _literal(_retrieval_db.reference_search, q, limit=5) == []
    auto = _with_strategy("auto", _retrieval_db.reference_search, q, limit=5)
    assert ("gec_13", "2.4.3") in [(h["reference"], h["section_id"]) for h in auto]


def test_auto_pin_n_keeps_the_literal_top_n():
    import geotech_references._query_expansion as qe
    q = "undrained shear strength of clay"
    off = _literal(_retrieval_db.reference_search, q, limit=5)
    saved = qe.EXPANSION_PIN
    try:
        for pin in (1, 2, 3):
            qe.EXPANSION_PIN = pin
            auto = _with_strategy("auto", _retrieval_db.reference_search, q, limit=5)
            key = lambda h: (h["reference"], h["section_id"])
            assert [key(h) for h in auto[:pin]] == [key(h) for h in off[:pin]]
    finally:
        qe.EXPANSION_PIN = saved


# ---------------------------------------------------------------------------
# REF-07: the gold set
# ---------------------------------------------------------------------------

def _gold():
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "scripts" / "eval_retrieval_gold.py"
    spec = importlib.util.spec_from_file_location("eval_retrieval_gold", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_gold_set_is_well_formed():
    cases = _gold().load_cases()
    assert len(cases) >= 40
    assert len({c["id"] for c in cases}) == len(cases)
    assert {c["kind"] for c in cases} == {
        "method", "table value", "figure", "definition", "limit"}
    assert len({r[0] for c in cases for r in c["relevant"]}) >= 12
    for c in cases:
        for ref, sid in c["relevant"]:
            assert "error" not in _retrieval_db.reference_get(ref, sid), (c["id"], ref, sid)


def test_gold_recall_expansion_never_loses_to_literal():
    mod = _gold()
    res = mod.evaluate(mod.load_cases(), [("off", 1), ("fill", 1), ("auto", 1)])
    for k in mod.KS:
        assert res["auto"]["recall"][k] >= res["off"]["recall"][k]
        assert res["auto"]["recall"][k] >= res["fill"]["recall"][k]
