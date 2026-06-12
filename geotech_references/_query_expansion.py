"""Lexical query expansion for the FTS5 retrieval layers.

The figure/text indexes are lexical (FTS5 + BM25 + porter stemming). Porter
stemming closes *morphological* gaps ("pressures" -> "pressure") but **not**
*synonym* gaps: a query for "interface friction" will not match a section that
only ever says "wall friction" or "delta", because they share no stem.

This module supplies the missing recall lever without adding any dependency or
embedding model: a small, curated table of geotechnical term-equivalence groups.
``expand_query`` detects any group member present in a query and returns an
FTS5 ``OR`` clause of the *other* members of those groups — the surface forms the
literal query did not use.

Design contract (so precision is preserved):

* This is used as a **recall fallback**, not a rewrite. The caller runs the
  literal query first and only consults the expansion to fill remaining result
  slots (see ``reference_search`` / ``figure_search``). Literal BM25 hits always
  rank first; synonym-only hits are appended.
* Expansion is **opt-out safe**: an empty/whitespace query, or a query that
  matches no group, yields ``""`` (the caller then changes nothing).
* Groups are intentionally conservative — distinctive multi-word phrases plus a
  few standard, corpus-unambiguous notations (``su``, ``phi``, ``ka``, ``kp``,
  ``ko``). Avoid bare ambiguous single letters here.

Keep entries DEFENSIBLE (true equivalences a geotechnical engineer would accept).
Add groups as real recall misses are observed (see
``scripts/eval_retrieval_recall.py``).
"""

from __future__ import annotations

import os
import re

# Each inner list is a set of mutually substitutable surface forms for one
# concept. Membership is symmetric: a query using ANY form expands to the others.
SYNONYM_GROUPS: list[list[str]] = [
    # --- earth pressure -----------------------------------------------------
    ["wall friction", "interface friction", "interface adhesion", "wall adhesion"],
    ["passive earth pressure", "passive resistance", "passive coefficient", "kp"],
    ["active earth pressure", "active resistance", "active coefficient", "ka"],
    ["at-rest earth pressure", "at rest earth pressure",
     "coefficient of earth pressure at rest", "ko"],
    ["lateral earth pressure", "earth pressure coefficient", "horizontal stress"],
    # --- strength / index ---------------------------------------------------
    ["undrained shear strength", "undrained strength", "su", "cu", "cohesion"],
    ["friction angle", "angle of internal friction", "effective friction angle",
     "phi"],
    ["relative density", "density index"],
    ["overconsolidation ratio", "ocr", "preconsolidation"],
    # --- foundations --------------------------------------------------------
    ["bearing capacity", "ultimate bearing", "bearing resistance"],
    ["settlement", "consolidation settlement", "compression settlement"],
    ["drilled shaft", "bored pile", "caisson"],
    ["driven pile", "displacement pile"],
    ["pile setup", "soil setup", "pile freeze", "setup factor"],
    ["downdrag", "negative skin friction", "neutral plane"],
    ["side resistance", "skin friction", "shaft resistance", "unit side resistance"],
    ["end bearing", "toe resistance", "tip resistance", "base resistance"],
    ["pullout resistance", "pullout capacity"],
    ["bond strength", "grout to ground bond", "bond stress"],
    # --- walls / reinforcement ---------------------------------------------
    ["soil nail", "soil nail wall", "nailed wall"],
    ["ground anchor", "tieback", "anchored wall"],
    ["mse wall", "mechanically stabilized earth", "reinforced soil wall"],
    # --- water / seepage ----------------------------------------------------
    ["groundwater", "water table", "phreatic surface", "gwt"],
    ["permeability", "hydraulic conductivity"],
    ["seepage", "underseepage", "piping"],
    # --- safety / design ----------------------------------------------------
    ["factor of safety", "safety factor"],
    ["resistance factor", "lrfd resistance factor"],
    # --- seismic ------------------------------------------------------------
    ["liquefaction", "cyclic resistance ratio", "crr", "liquefaction triggering"],
    ["seismic", "earthquake", "pseudostatic"],
    ["site class", "site classification", "vs30"],
    # --- earthwork ----------------------------------------------------------
    ["compaction", "relative compaction", "proctor"],
    ["slope stability", "slope failure", "circular failure surface"],
    ["scour", "erosion"],
]


# Retrieval strategy for how expansion is applied (set by the search layer /
# experiments; see scripts/eval_retrieval_recall.py):
#   "fill"   — conservative: run the literal query, then append synonym hits
#              only to fill remaining slots. Literal BM25 order is untouched, so
#              precision is preserved; helps most when literal recall is thin.
#   "rerank" — "shotgun": run ONE combined query, "(literal) OR synonyms", and
#              let BM25 rank the union. More recall, some precision risk.
#   "auto"   — rerank the literal+synonym union for recall, but PIN the literal
#              top-1 so an already-good query keeps its best hit. Targets
#              rerank's recall with fill's precision on the top result.
#   "off"    — pure literal, no expansion.
#
# Default is "auto" (best recall/precision trade in scripts/eval_retrieval_recall.py);
# override per-deployment with the GEOTECH_RETRIEVAL_EXPANSION env var.
_VALID_STRATEGIES = {"off", "fill", "rerank", "auto"}
EXPANSION_STRATEGY = os.environ.get("GEOTECH_RETRIEVAL_EXPANSION", "auto").strip().lower()
if EXPANSION_STRATEGY not in _VALID_STRATEGIES:
    EXPANSION_STRATEGY = "auto"


def combined_query(query: str) -> str:
    """Build the single 'rerank' MATCH: the literal AND-group OR the synonyms.

    Returns ``query`` unchanged if there is nothing to add.
    """
    exp = expand_query(query)
    if not exp:
        return query
    return f"({query}) OR {exp}"


def _contains_term(norm_query: str, term: str) -> bool:
    """True if ``term`` appears in the already-normalized (lower, single-space)
    query. Multi-word / hyphenated terms match as substrings; single tokens match
    on word boundaries so ``ka`` does not fire inside ``make``."""
    if " " in term or "-" in term:
        return term in norm_query
    return re.search(rf"\b{re.escape(term)}\b", norm_query) is not None


def _as_fts_term(term: str) -> str:
    """Quote multi-word / hyphenated terms as FTS5 phrases; leave tokens bare."""
    return f'"{term}"' if (" " in term or "-" in term) else term


def expand_query(query: str) -> str:
    """Return an FTS5 ``OR`` clause of synonym surface forms not already in
    ``query``, or ``""`` if the query matches no known concept group.

    Examples
    --------
    >>> expand_query("interface friction angle on the wall")
    '"wall friction" OR "interface adhesion" OR "wall adhesion"'
    >>> expand_query("hello world")
    ''
    """
    if not query or not query.strip():
        return ""
    norm = re.sub(r"\s+", " ", query.lower()).strip()

    added: list[str] = []
    seen: set[str] = set()
    for group in SYNONYM_GROUPS:
        if not any(_contains_term(norm, t) for t in group):
            continue
        for term in group:
            if _contains_term(norm, term):
                continue  # already expressed in the query
            key = term.lower()
            if key in seen:
                continue
            seen.add(key)
            added.append(term)

    if not added:
        return ""
    return " OR ".join(_as_fts_term(t) for t in added)


_FTS_OPS = {"or", "and", "not", "near"}


def or_fallback(query: str) -> str | None:
    """Build an OR-of-terms query from a plain query, or None if not applicable.

    Used as a recall fallback when strict (AND) matching returns nothing: a
    natural query like "liquefaction triggering CRR" should still surface the
    liquefaction sections even though the literal token "CRR" is absent from
    the corpus. Only ever applied to a ZERO-hit primary query, so it cannot
    disturb the ranking of any query that already returns results.
    """
    if '"' in query:  # respect explicit phrase/operator queries
        return None
    toks = [t for t in re.findall(r"[A-Za-z0-9]+", query)
            if t.lower() not in _FTS_OPS]
    if len(toks) < 2:
        return None
    return " OR ".join(toks)


def merge_hits(literal: list, extra: list, limit: int, key) -> list:
    """Merge expansion hits into literal hits: literal first, deduped by ``key``,
    capped at ``limit``. ``key`` maps a hit -> hashable id."""
    out = list(literal[:limit])
    seen = {key(h) for h in out}
    for h in extra:
        if len(out) >= limit:
            break
        k = key(h)
        if k in seen:
            continue
        seen.add(k)
        out.append(h)
    return out
