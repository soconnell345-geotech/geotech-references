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

* A term is found as a whole word or phrase (an optional plural ending
  allowed), and **longest match wins**: a term found only inside a longer
  matched term of another group ("skin friction" inside "negative skin
  friction") does not fire its group.
* Under ``auto``, a query whose literal AND form matches nothing is run with
  its named terms swapped for their groups (:func:`substituted_query`), so the
  words the groups do not cover still have to match.

A form the library never prints stays only as a word an engineer types
that should fire its group ("dsm", "underseepage", "pile freeze",
"interface adhesion"); a form that is neither printed nor a term in use is
removed (REF-37: "active resistance").

Keep entries DEFENSIBLE (true equivalences a geotechnical engineer would accept)
and spelled as the manuals print them; check a new form against the chapter
text before adding it. Measure with ``scripts/eval_retrieval_gold.py`` (the
hand-curated gold set, REF-07).
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
    # (REF-37: "active resistance" removed: printed nowhere, and the active
    # side is a pressure, not a resistance)
    ["active earth pressure", "active coefficient", "ka"],
    ["at-rest earth pressure", "at rest earth pressure",
     "coefficient of earth pressure at rest", "ko"],
    ["lateral earth pressure", "earth pressure coefficient", "horizontal stress"],
    # --- strength / index ---------------------------------------------------
    # No bare "cu": it is also the coefficient of uniformity (UFS 3-220-10
    # Sec. 1-3.3.2, Cu = D60/D10) and the CU triaxial test (Sec. 3-2.4.1.3).
    # No "cohesion" (REF-37): the drained cohesion c' is another quantity,
    # and "drained cohesion" fired su.
    ["undrained shear strength", "undrained strength", "su"],
    ["friction angle", "angle of internal friction", "effective friction angle",
     "phi"],
    ["relative density", "density index"],
    ["overconsolidation ratio", "ocr", "preconsolidation"],
    # No bare "qu": FHWA-NHI-14-007 Sec. 4.5 uses qu for the soil-nail bond
    # strength, and other manuals for the ultimate bearing pressure.
    ["unconfined compressive strength", "uniaxial compressive strength", "ucs",
     "unconfined compression test"],
    ["rock quality designation", "rqd"],
    # --- in situ tests ------------------------------------------------------
    ["standard penetration test", "spt"],
    # Not "cone penetrometer": the dynamic cone penetrometer (DCP) is another
    # test (UFS 3-220-10 Sec. 2-7.4).
    ["cone penetration test", "cpt", "cptu", "piezocone"],
    ["dilatometer", "dmt"],
    ["pressuremeter", "pmt"],
    # (N1)60 is printed (N1)60, N1(60) and N1,60; all index as "n1 60".
    # Not "corrected blow count": UFS 3-220-10 uses it for N60, the
    # energy-corrected count (Sec. 5-11, 8-5.3.1); "normalized" is the
    # overburden-corrected (N1)60 (Sec. 2-7.1.1).
    ["(n1)60", "n1(60)", "n160", "normalized blow count",
     "normalised blow count"],
    # --- foundations --------------------------------------------------------
    # No "ultimate bearing" (REF-37): "allowable bearing capacity" fired it.
    # No settlement group: "immediate settlement" fired consolidation
    # settlement, and GEC-6 Sec. 5.2.3.8 and GEC-8 Sec. 5.5.3.2 print
    # "compression settlement" for granular soil, not consolidation.
    ["bearing capacity", "bearing resistance"],
    ["drilled shaft", "bored pile", "caisson"],
    ["driven pile", "displacement pile"],
    ["continuous flight auger", "cfa", "auger cast", "augered cast-in-place",
     "acip"],
    ["pile setup", "soil setup", "pile freeze", "setup factor"],
    ["downdrag", "negative skin friction", "neutral plane"],
    ["side resistance", "skin friction", "shaft resistance", "unit side resistance"],
    # No "tip resistance" (REF-37): the manuals print it for the CPT cone
    # tip resistance qc (UFS 3-220-10 Sec. 2-7.2.1, 8-3.3), not pile toes.
    ["end bearing", "toe resistance", "base resistance"],
    ["p-y curve", "p-y"],
    # No "load-transfer curve" (REF-37): UFC 3-220-20 Sec. 6-5.8.4.2 prints
    # "load transfer-displacement relationships, i.e., t-z and q-z curves",
    # so it names the base (q-z) curves too.
    ["t-z curve", "t-z"],
    ["pullout resistance", "pullout capacity"],
    ["bond strength", "grout to ground bond", "bond stress"],
    # --- walls / reinforcement ---------------------------------------------
    ["soil nail", "soil nail wall", "nailed wall"],
    ["ground anchor", "tieback", "anchored wall"],
    ["mse wall", "mse", "mechanically stabilized earth", "reinforced soil wall"],
    # --- ground improvement (FHWA-NHI-16-027 wording) -----------------------
    ["prefabricated vertical drain", "pvd", "wick drain", "vertical drain"],
    ["stone column", "aggregate column", "aggregate pier", "vibro-replacement"],
    ["vibro-compaction", "vibroflotation", "vibro-flotation"],
    ["deep mixing", "deep soil mixing", "dsm", "dmm"],
    ["geofoam", "eps", "expanded polystyrene"],
    # --- water / seepage ----------------------------------------------------
    ["groundwater", "water table", "phreatic surface", "gwt"],
    ["permeability", "hydraulic conductivity"],
    ["seepage", "underseepage", "piping"],
    # --- safety / design ----------------------------------------------------
    ["factor of safety", "safety factor"],
    ["resistance factor", "lrfd resistance factor"],
    # --- seismic ------------------------------------------------------------
    # Demand and capacity stay apart: CSR is the load, CRR the resistance
    # (FHWA-NHI-16-027 Sec. 4.1.6).
    ["cyclic stress ratio", "csr"],
    ["cyclic resistance ratio", "crr", "liquefaction resistance"],
    ["seismic", "earthquake", "pseudostatic"],
    ["site class", "site classification", "vs30"],
    # --- earthwork ----------------------------------------------------------
    # No bare "compaction": it fires on deep dynamic compaction and
    # vibro-compaction (ground improvement), not compaction control.
    ["relative compaction", "degree of compaction", "proctor"],
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
#   "auto"   — fuse the literal hits with the literal+synonym union by
#              reciprocal rank (:func:`fuse_hits`, REF-54), PIN the literal
#              top-1, and keep the literal hit at rank r <= 5 no lower than
#              2r, so expansion adds hits without pushing out what the
#              literal search ranked well. (Before REF-54 only the top-1 was
#              kept and the union filled the rest.)
#   "off"    — pure literal, no expansion.
#
# Default is "auto" (best recall/precision trade in scripts/eval_retrieval_recall.py);
# override per-deployment with the GEOTECH_RETRIEVAL_EXPANSION env var.
_VALID_STRATEGIES = {"off", "fill", "rerank", "auto"}
EXPANSION_STRATEGY = os.environ.get("GEOTECH_RETRIEVAL_EXPANSION", "auto").strip().lower()
if EXPANSION_STRATEGY not in _VALID_STRATEGIES:
    EXPANSION_STRATEGY = "auto"

# How many literal hits ``auto`` keeps in place before the reranked union
# (env GEOTECH_RETRIEVAL_PIN). 1 is the measured default; see
# scripts/eval_retrieval_gold.py --pins.
try:
    EXPANSION_PIN = max(1, int(os.environ.get("GEOTECH_RETRIEVAL_PIN", "1")))
except ValueError:
    EXPANSION_PIN = 1

# The rank constant of ``auto``'s reciprocal-rank fusion (:func:`fuse_hits`,
# REF-54; env GEOTECH_RETRIEVAL_FUSION_K). Measured on the gold set with
# scripts/eval_retrieval_gold.py --fusion-k.
try:
    FUSION_K = max(0, int(os.environ.get("GEOTECH_RETRIEVAL_FUSION_K", "3")))
except ValueError:
    FUSION_K = 3

# How many of the literal hits ``auto`` is sure to keep, the one at rank r
# no lower than 2r (REF-54): 5 keeps the literal top 5 in a top 10.
FUSION_KEEP = 5


def combined_query(query: str) -> str:
    """Build the single 'rerank' MATCH: the literal AND-group OR the synonyms.

    Returns ``query`` unchanged if there is nothing to add.
    """
    exp = expand_query(query)
    if not exp:
        return query
    return f"({query}) OR {exp}"


def _term_pattern(term: str) -> re.Pattern:
    """A term found as a whole word or phrase, with an optional plural ending
    ("pvds", "p-y curves"), so ``ka`` does not fire inside ``make``."""
    return re.compile(rf"(?<![\w]){re.escape(term)}(?:e?s)?(?![\w])")


def _spans(norm_query: str, term: str) -> list[tuple[int, int]]:
    return [m.span() for m in _term_pattern(term).finditer(norm_query)]


def _contains_term(norm_query: str, term: str) -> bool:
    """True if ``term`` appears in the already-normalized (lower, single-space)
    query, as a whole word or phrase."""
    return bool(_spans(norm_query, term))


def _as_fts_term(term: str) -> str:
    """A bare token stays bare; anything else becomes an FTS5 phrase of its
    word characters, the way the index tokenizes it ("(n1)60" -> "n1 60")."""
    if re.fullmatch(r"[a-z0-9]+", term):
        return term
    return '"' + " ".join(re.findall(r"[a-z0-9]+", term)) + '"'


def _matches(norm_query: str) -> list[tuple[int, int, int]]:
    """``(start, end, group)`` of every term the query names, longest match
    first: a term found only inside a longer matched term of ANOTHER group
    ("skin friction" inside "negative skin friction") is left out."""
    found = []
    for gi, group in enumerate(SYNONYM_GROUPS):
        for term in group:
            found.extend((a, b, gi) for a, b in _spans(norm_query, term))
    return [(a, b, gi) for a, b, gi in found
            if not any(a2 <= a and b <= b2 and (b2 - a2) > (b - a) and g2 != gi
                       for a2, b2, g2 in found)]


def _matched_groups(norm_query: str) -> list[int]:
    """The groups the query names (see :func:`_matches`)."""
    return sorted({gi for _, _, gi in _matches(norm_query)})


def substituted_query(query: str) -> str | None:
    """The query AND-matched with each named term replaced by its group's
    forms: "wick drain smear zone" -> ``("prefabricated vertical drain" OR
    pvd OR "wick drain" OR "vertical drain") AND smear AND zone``. None when no
    group fires or the query already uses FTS5 syntax (quotes, operators)."""
    if not query or '"' in query or re.search(r"\b(OR|AND|NOT|NEAR)\b", query):
        return None
    norm = re.sub(r"\s+", " ", query.lower()).strip()
    spans = sorted(_matches(norm), key=lambda m: (m[0], -(m[1] - m[0])))
    if not spans:
        return None
    parts, pos = [], 0
    for a, b, gi in spans:
        if a < pos:
            continue  # overlaps a span already taken
        parts += [t for t in re.findall(r"[a-z0-9]+", norm[pos:a])
                  if t not in _FTS_OPS]
        forms = list(dict.fromkeys(_as_fts_term(t) for t in SYNONYM_GROUPS[gi]))
        parts.append("(" + " OR ".join(forms) + ")")
        pos = b
    parts += [t for t in re.findall(r"[a-z0-9]+", norm[pos:]) if t not in _FTS_OPS]
    return " AND ".join(parts)


def query_concepts(query: str) -> list[str]:
    """The query's concepts as FTS5 expressions: a named term's whole group
    and each other word (the AND-ed parts of :func:`substituted_query`), or
    the query's words when no group fires."""
    sub = substituted_query(query)
    if sub:
        return sub.split(" AND ")
    fb = or_fallback(query)
    return fb.split(" OR ") if fb else []


def zero_literal_hits(query: str, run, want: int, key, run_or=None) -> list:
    """Hits for a query whose literal (AND) form matched nothing: first the
    query with its named terms swapped for their groups
    (:func:`substituted_query`), then the query's words OR-ed with the
    synonyms, each filling the slots the one before left. The words stay in
    the second query so a group that fires cannot crowd out the OR-of-words
    fallback the query would have had without it ("DSM column layout for
    embankment support" keeps "layout" and "embankment"). ``run_or``, when
    given, runs that second, OR-ed query instead of ``run`` (the text search
    ranks it by the concepts each hit holds)."""
    rows: list = []
    sub = substituted_query(query)
    if sub:
        rows = run(sub)
    exp = expand_query(query)
    if exp and len(rows) < want:
        words = or_fallback(query)
        rows = merge_hits(rows,
                          (run_or or run)(f"{words} OR {exp}" if words else exp),
                          want, key)
    return rows


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
    # a form the query already uses, in any spelling ("N1(60)" and "(N1)60"
    # are one phrase to the index), is not added again
    seen: set[str] = {_as_fts_term(t) for g in SYNONYM_GROUPS for t in g
                      if _contains_term(norm, t)}
    for gi in _matched_groups(norm):
        for term in SYNONYM_GROUPS[gi]:
            if _contains_term(norm, term):
                continue  # already expressed in the query
            fts = _as_fts_term(term)
            if fts in seen:
                continue
            seen.add(fts)
            added.append(fts)

    if not added:
        return ""
    return " OR ".join(added)


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


def fuse_hits(literal: list, combined: list, limit: int, key,
              pin: int = 1, k: int | None = None,
              keep: int | None = None) -> list:
    """``auto``'s merge of the literal hits with the literal-OR-synonyms hits
    (REF-54): the literal top ``pin`` stay in place, and the rest are ranked
    by reciprocal-rank fusion, ``1/(k + literal rank) + 1/(k + combined
    rank)``, so a section the literal search ranked well keeps a place even
    when the synonym query ranks it low or not at all.

    Before REF-54 only the literal top-1 was kept and the synonym query
    filled the other places, which dropped sections the literal search
    ranked 3rd and 5th out of the top 10 ("PVD spacing design").

    The fusion alone keeps nearly every literal hit near the top, but a
    section the synonym query also ranks just below it can still pass it,
    so the literal hit at rank r (r <= ``keep``) is in any case placed no
    lower than 2r: the literal top 5 always stays in the top 10. Ties keep
    the literal order first.
    """
    k = FUSION_K if k is None else k
    keep = FUSION_KEEP if keep is None else keep
    pin = max(0, pin)
    out = list(literal[:pin])
    seen = {key(h) for h in out}
    score: dict = {}
    first: dict = {}
    order: dict = {}
    for lst in (literal, combined):
        for r, h in enumerate(lst, 1):
            kk = key(h)
            if kk in seen:
                continue
            first.setdefault(kk, h)
            order.setdefault(kk, len(order))
            score[kk] = score.get(kk, 0.0) + 1.0 / (k + r)
    ranked = sorted(score, key=lambda kk: (-score[kk], order[kk]))
    # the guarantee: the literal hit at rank r <= keep is placed no lower
    # than 2r, whatever the fusion scores say
    due = [(2 * r, key(h)) for r, h in enumerate(literal[:keep], 1)
           if key(h) not in seen]
    for kk in ranked:
        while due and due[0][1] in seen:
            due.pop(0)
        while due and due[0][0] <= len(out) + 1:
            out.append(first[due[0][1]])
            seen.add(due.pop(0)[1])
            while due and due[0][1] in seen:
                due.pop(0)
        if kk not in seen:
            out.append(first[kk])
            seen.add(kk)
    return out[:limit]


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
