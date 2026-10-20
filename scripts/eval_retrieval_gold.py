"""Recall@k of reference_search on the hand-curated gold set (REF-07).

Each case in ``retrieval_gold.json`` is a question as the agent asks it and
the sections a good search must return (any one of them counts as a hit).
The script reports recall@k for k = 3, 5, 10 under each expansion strategy,
the mean reciprocal rank, and how often each strategy changes the literal
top-1. ``--pins`` also measures ``auto`` with the literal top-N kept in place
(``_query_expansion.EXPANSION_PIN``).

Run:
    python scripts/eval_retrieval_gold.py
    python scripts/eval_retrieval_gold.py --pins 1 2 3 --per-case
    python scripts/eval_retrieval_gold.py --json out.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from geotech_references import _retrieval_db  # noqa: E402
import geotech_references._query_expansion as _qe  # noqa: E402

GOLD = Path(__file__).with_name("retrieval_gold.json")
KS = (3, 5, 10)
LIMIT = max(KS)


def load_cases(path: Path = GOLD) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def _configure(strategy: str, pin: int) -> None:
    _qe.EXPANSION_STRATEGY = strategy
    if hasattr(_qe, "EXPANSION_PIN"):
        _qe.EXPANSION_PIN = pin


def ranked(query: str) -> list[tuple[str, str]]:
    hits = _retrieval_db.reference_search(query, limit=LIMIT)
    return [(h["reference"], h["section_id"]) for h in hits if "error" not in h]


def first_rank(keys: list, relevant: set) -> int | None:
    for i, k in enumerate(keys, 1):
        if k in relevant:
            return i
    return None


def evaluate(cases: list[dict], arms: list[tuple[str, int]]) -> dict:
    """``arms``: (strategy, pin) pairs. Returns per-arm metrics + ranks."""
    out = {}
    _configure("off", 1)
    literal_top = {c["id"]: (ranked(c["query"]) or [None])[0] for c in cases}
    for strategy, pin in arms:
        _configure(strategy, pin)
        ranks, moved = {}, 0
        by_kind = defaultdict(lambda: [0, 0])
        for c in cases:
            rel = {tuple(r) for r in c["relevant"]}
            keys = ranked(c["query"])
            r = first_rank(keys, rel)
            ranks[c["id"]] = r
            moved += bool(keys) and keys[0] != literal_top[c["id"]]
            by_kind[c["kind"]][1] += 1
            by_kind[c["kind"]][0] += r is not None and r <= 5
        n = len(cases)
        name = strategy if strategy != "auto" or pin == 1 else f"auto/pin{pin}"
        out[name] = {
            "recall": {k: sum(1 for r in ranks.values() if r and r <= k) / n
                       for k in KS},
            "mrr@10": sum(1 / r for r in ranks.values() if r) / n,
            "top1_changed": moved,
            "recall5_by_kind": {k: f"{v[0]}/{v[1]}" for k, v in by_kind.items()},
            "ranks": ranks,
        }
    _configure("auto", 1)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pins", type=int, nargs="*", default=[1])
    ap.add_argument("--per-case", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    _retrieval_db.rebuild_db()
    cases = load_cases()
    arms = [("off", 1), ("fill", 1)] + [("auto", p) for p in a.pins] + [("rerank", 1)]
    res = evaluate(cases, arms)
    n = len(cases)
    print("('off' is the pure literal query: no synonyms and no OR-of-terms\n"
          " fallback for a query that matches nothing; the other modes have both)")
    print(f"gold set: {n} cases, {len({r[0] for c in cases for r in c['relevant']})} references")
    print(f"{'mode':<12}" + "".join(f"{'R@' + str(k):<12}" for k in KS) + f"{'MRR@10':<9}top-1 changed")
    for name, m in res.items():
        print(f"{name:<12}" + "".join(
            f"{round(m['recall'][k] * n):>2}/{n} {m['recall'][k]:>4.0%}  "
            for k in KS) + f"{m['mrr@10']:<9.3f}{m['top1_changed']}")
    print("\nrecall@5 by question kind:")
    for name, m in res.items():
        print(f"  {name:<12}" + "  ".join(f"{k}={v}" for k, v in sorted(m["recall5_by_kind"].items())))
    if a.per_case:
        names = list(res)
        print("\n" + f"{'case':<22}" + "".join(f"{x:<12}" for x in names))
        for c in cases:
            print(f"{c['id']:<22}" + "".join(
                f"{str(res[x]['ranks'][c['id']] or '-'):<12}" for x in names))
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
