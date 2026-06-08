"""Measure recall lift from lexical query expansion, and compare strategies.

Compares retrieval strategies on the SAME labeled set:
  off    — pure literal FTS5 (today's behavior)
  fill   — conservative: append synonym hits only to fill empty result slots
  rerank — "shotgun": BM25 ranks the literal+synonym union in one query
  auto   — adaptive: keep a full literal page; shotgun only when literal is thin

Ground truth (per concept): a CANONICAL query phrased in the reference's own
terminology, whose top-1 (in OFF mode) is the target — trusted only if that
hit's title/summary/caption contains a ``gate`` keyword (drops noisy top-1s).
We then ask: does a USER query phrased with SYNONYMS surface that same target in
top-k under each strategy? That is the synonym-recall question.

Also reports a PRECISION proxy: for the canonical (already-good) queries, how
often does a strategy DISTURB the literal top-1? (lower = safer.)

Run:
    .venv/Scripts/python geotech-references/scripts/eval_retrieval_recall.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from geotech_references import _retrieval_db, _figures_db  # noqa: E402
import geotech_references._query_expansion as _qe  # noqa: E402

K = 5
STRATEGIES = ["off", "fill", "rerank", "auto"]

# concept, canonical (source wording), user (synonym wording), gate keyword
TEXT_CASES = [
    dict(c="downdrag",       canon="negative skin friction neutral plane", user="downdrag drag load on pile",     gate="neutral"),
    dict(c="drilled shaft",  canon="drilled shaft side resistance",        user="bored pile skin friction",        gate="shaft"),
    dict(c="seepage/piping", canon="seepage piping erosion",               user="underseepage control",            gate="seep"),
    dict(c="water table",    canon="groundwater table",                    user="phreatic surface",                gate="water"),
    dict(c="wall friction",  canon="wall friction angle delta",            user="interface adhesion on the wall",  gate="friction"),
    dict(c="undrained su",   canon="undrained shear strength",             user="cohesion cu of clay",             gate="strength"),
    dict(c="permeability",   canon="permeability coefficient",             user="hydraulic conductivity",          gate="perm"),
    dict(c="bearing cap.",   canon="bearing capacity factors",             user="ultimate bearing resistance",     gate="bearing"),
    dict(c="compaction",     canon="relative compaction proctor",          user="degree of compaction",            gate="compact"),
    dict(c="liquefaction",   canon="liquefaction triggering",              user="cyclic resistance ratio",         gate="liquef"),
]

# figures: reference-scoped so the canonical top-1 is a clean target.
FIGURE_CASES = [
    dict(c="passive spiral", canon="log spiral passive coefficient", user="interface adhesion passive pressure", gate="passive", ref="dm7_2"),
    dict(c="earth pressure", canon="coefficient of earth pressure",  user="lateral pressure ratio chart",        gate="pressure", ref="dm7_2"),
]


def _set(strategy):
    _qe.EXPANSION_STRATEGY = strategy


def _keys_text(hits):
    return [(h.get("reference"), h.get("section_id")) for h in hits if "error" not in h]


def _keys_fig(hits):
    return [(h.get("reference"), h.get("figure_number")) for h in hits if "error" not in h]


def _blob(hit):
    return f"{hit.get('title','')} {hit.get('summary','')} {hit.get('caption','')}".lower()


def _ground_truth(search_fn, keyer, canon_q, gate, **kw):
    _set("off")
    hits = search_fn(canon_q, **kw)
    if not hits or "error" in hits[0] or gate.lower() not in _blob(hits[0]):
        return None
    return keyer([hits[0]])[0]


def run_block(title, cases, search_fn, keyer, base_kw):
    print(f"\n{'=' * 90}\n{title}   (recall@{K} of the canonical target)\n{'=' * 90}")
    print(f"{'concept':<16}{'target':<24}" + "".join(f"{s:<8}" for s in STRATEGIES))
    print("-" * 90)
    tally = {s: 0 for s in STRATEGIES}
    total = 0
    for case in cases:
        kw = dict(base_kw)
        if case.get("ref"):
            kw["reference"] = case["ref"]
        gt = _ground_truth(search_fn, keyer, case["canon"], case["gate"], **kw)
        if gt is None:
            print(f"{case['c']:<16}{'(no trusted GT)':<24}" + "".join("-".ljust(8) for _ in STRATEGIES))
            continue
        total += 1
        cells = []
        for s in STRATEGIES:
            _set(s)
            hit = gt in keyer(search_fn(case["user"], **kw))
            tally[s] += hit
            cells.append("hit" if hit else "·")
        print(f"{case['c']:<16}{f'{gt[0]}:{gt[1]}':<24}" + "".join(c.ljust(8) for c in cells))
    print("-" * 90)
    if total:
        print(f"{'RECALL@'+str(K):<40}" + "".join(f"{tally[s]}/{total}".ljust(8) for s in STRATEGIES))
    return tally, total


def precision_block(title, cases, search_fn, keyer, base_kw):
    print(f"\n{'-' * 90}\nPRECISION — {title}: strategies that DISTURB the literal top-1 (lower=safer)")
    disturbed = {s: 0 for s in STRATEGIES if s != "off"}
    total = 0
    for case in cases:
        kw = dict(base_kw)
        if case.get("ref"):
            kw["reference"] = case["ref"]
        _set("off")
        base = keyer(search_fn(case["canon"], **kw))
        if not base:
            continue
        total += 1
        for s in disturbed:
            _set(s)
            top = keyer(search_fn(case["canon"], **kw))
            if not top or top[0] != base[0]:
                disturbed[s] += 1
    print("   " + "   ".join(f"{s}: {d}/{total}" for s, d in disturbed.items()))
    return disturbed, total


def main():
    _retrieval_db.rebuild_db()
    _figures_db.rebuild_db()

    tt, ttot = run_block("TEXT — reference_search", TEXT_CASES,
                         _retrieval_db.reference_search, _keys_text, dict(limit=K))
    ft, ftot = run_block("FIGURE — figure_search", FIGURE_CASES,
                         _figures_db.figure_search, _keys_fig, dict(limit=K))
    precision_block("text", TEXT_CASES, _retrieval_db.reference_search, _keys_text, dict(limit=K))
    precision_block("figure", FIGURE_CASES, _figures_db.figure_search, _keys_fig, dict(limit=K))

    T = ttot + ftot
    print(f"\n{'#' * 90}\nOVERALL recall@{K} across {T} trusted cases:")
    for s in STRATEGIES:
        tot = tt[s] + ft[s]
        print(f"   {s:<8} {tot}/{T} = {tot / T:.0%}" if T else f"   {s}: n/a")
    print("#" * 90)
    _set("fill")


if __name__ == "__main__":
    main()
