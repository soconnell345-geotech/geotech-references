"""Subsection retrieval: does the librarian reach the section that holds the
answer, and how many characters does it read on the way? (REF-24)

Until REF-24 only the sections at the top level of a chapter file were
indexed, so a section the file nests inside another (GEC-12 holds 76 of them,
every chapter 7 static method among them) could not be searched for or
fetched by its own number. The other references list every level flat, one
entry per section, so their deeper sections were always indexed; what they
lacked was the chain of sections above a hit and the list of sections below a
fetched one.

``QUESTIONS`` are questions whose answer sits in a section below the top
level, across GEC-12 (nested) and seven references that list their levels
flat. For each, the librarian's route is replayed with the library's own
functions:

1. ``reference_search(query, reference=<ref>, limit=5)``, read in full;
2. when the answer's section is a hit, ``reference_get`` of it; otherwise,
   when a hit is a section above it, the walk down from that hit with
   ``reference_get`` at each level -- and where a level cannot be fetched by
   its own number, ``retrieve_section`` of the hit (the per-reference text
   tool, which returned a section with its subsections inlined), cut at the
   app's 16,000-character reference cap as the app cuts it;
3. otherwise the answer is not reached.

Characters are ``len(json.dumps(result, default=str))``, which is what the app
sends the model. The section tree is read off the chapter files here,
independently of the library: a section the file nests sits under its
container; a section the file lists flat sits under the nearest section of the
same file whose number is a prefix of its own.

``--titles`` is the ranking guard: every section at the top level of its file
is searched for by its own title and the first hit is recorded. With
``--save`` the hits are written to a file; ``--compare <file>`` then reports
which sections that found themselves first before no longer do (a deeper,
shorter section winning on its parent's title is exactly the failure).

Run:
    .venv/Scripts/python geotech-references/scripts/eval_subsection_retrieval.py
    .venv/Scripts/python geotech-references/scripts/eval_subsection_retrieval.py --titles --save before.json
    .venv/Scripts/python geotech-references/scripts/eval_subsection_retrieval.py --titles --compare before.json

Test: ``tests/test_subsection_retrieval.py`` keeps these questions answered.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from geotech_references import _retrieval, _retrieval_db  # noqa: E402

PKG = Path(__file__).resolve().parents[1] / "geotech_references"
K = 5
#: The app's cap on a reference tool's result (GeotechStaffEngineer
#: ``funhouse_agent/deep/tools.py`` DEFAULT_REFERENCE_RESULT_CHARS).
APP_REFERENCE_CAP = 16000

# ref, the section that answers, the question, and the search the librarian
# would send for it.
QUESTIONS = [
    dict(ref="gec_12", target="7.2.1.3.1",
         question="Which static method gives shaft and toe resistance of a "
                  "pile driven into cohesionless soil?",
         query="Nordlund method"),
    dict(ref="gec_12", target="7.2.2.1",
         question="How is the efficiency of a pile group in compression found?",
         query="pile group efficiency"),
    dict(ref="gec_12", target="7.3.5.6",
         question="How does the tangent modulus method estimate pile group "
                  "settlement?",
         query="Janbu tangent modulus settlement"),
    dict(ref="gec_12", target="7.2.1.3.6",
         question="How is pile capacity estimated from a CPT with effective "
                  "cone resistance?",
         query="CPT pile capacity effective cone resistance"),
    dict(ref="gec_12", target="7.2.3.2.1",
         question="What controls the uplift resistance of a pile group in "
                  "cohesionless soil?",
         query="group uplift cohesionless"),
    dict(ref="gec_12", target="7.10.7",
         question="At what penetration ratio does an open-end pipe pile plug?",
         query="soil plug open end pipe pile"),
    dict(ref="gec_12", target="7.2.4.2",
         question="Why does pile resistance increase with time after driving "
                  "in clay?",
         query="soil setup pore pressure dissipation"),
    dict(ref="dm7_2", target="6-6.4.1",
         question="How is the lateral capacity of a short rigid free-head pile "
                  "found?",
         query="Broms short rigid free-head pile lateral capacity"),
    dict(ref="dm7_1", target="5-7.4.2",
         question="How are vertical drain type and spacing chosen?",
         query="vertical drain spacing design"),
    dict(ref="gec_6", target="5.3.4.2",
         question="Which settlement method for sand uses an SPT-correlated "
                  "modulus and accounts for preloading?",
         query="settlement modulus SPT preloaded sand"),
    dict(ref="ufc_concrete_practice", target="8-5.2.1.7",
         question="How is the alignment of placed dowel bars checked?",
         query="verify dowel bar alignment"),
    dict(ref="gsa_collapse", target="3.2.12.5",
         question="What dynamic increase factor applies to the nonlinear "
                  "static procedure?",
         query="dynamic increase factor nonlinear static"),
    dict(ref="eurocode_7_1", target="6.5.2.4",
         question="May spread foundations on rock be designed from presumed "
                  "bearing resistance?",
         query="presumed bearing resistance rock"),
    dict(ref="gec_11", target="3.5.2.c",
         question="What does the creep reduction factor of a geosynthetic "
                  "account for?",
         query="creep reduction factor geosynthetic"),
]


# ---------------------------------------------------------------------------
# the section tree, read off the chapter files
# ---------------------------------------------------------------------------

def _id_prefixes(sid: str) -> list[str]:
    """``'4-2.1.3'`` -> ``['4-2.1', '4-2', '4']``, nearest first."""
    out = []
    while True:
        m = re.search(r"[.\-][^.\-]*$", sid)
        if not m or m.start() == 0:
            return out
        sid = sid[:m.start()]
        out.append(sid)


def section_tree(ref: str) -> dict:
    """``{section_id: (parent_id or None, top_level, body)}`` for one
    reference; the first section of an id wins."""
    tree: dict = {}
    for jf in sorted((PKG / ref / "text").glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        seen: dict = {}

        def walk(secs, parent):
            for s in secs or []:
                if not isinstance(s, dict):
                    continue
                sid = s.get("section_id", "")
                if sid not in seen:
                    seen[sid] = (parent, parent is None, s.get("body", ""))
                walk(s.get("subsections"), sid)

        walk(data.get("sections"), None)
        for sid, (parent, top, body) in seen.items():
            if parent is None:
                parent = next((p for p in _id_prefixes(sid) if p in seen), None)
            tree.setdefault(sid, (parent, top, body))
    return tree


def _ancestors(tree: dict, sid: str) -> list[str]:
    out, guard = [], set()
    while sid in tree and tree[sid][0] and sid not in guard:
        guard.add(sid)
        sid = tree[sid][0]
        out.append(sid)
    return out


# ---------------------------------------------------------------------------
# the route
# ---------------------------------------------------------------------------

def _size(obj) -> int:
    return len(json.dumps(obj, default=str))


def _get(ref: str, sid: str):
    try:
        return _retrieval_db.reference_get(ref, sid)
    except KeyError:
        return None


def replay(q: dict, tree: dict | None = None) -> dict:
    """The librarian's route to ``q['target']``: rank, reached, characters."""
    ref, target = q["ref"], q["target"]
    tree = tree if tree is not None else section_tree(ref)
    hits = _retrieval_db.reference_search(q["query"], reference=ref, limit=K)
    ids = [h.get("section_id") for h in hits if "error" not in h]
    out = {"rank": ids.index(target) + 1 if target in ids else None,
           "search_chars": _size(hits), "fetch_chars": 0, "reached": False,
           "route": "search"}
    if out["rank"]:
        got = _get(ref, target)
        if got is not None:
            out.update(fetch_chars=_size(got), reached=True,
                       route=f"search -> get {target}")
        return out
    above = _ancestors(tree, target)
    start = next((i for i in ids if i in above), None)
    if start is None:
        return out
    path = list(reversed(above[:above.index(start) + 1])) + [target]
    steps = []
    for sid in path:
        got = _get(ref, sid)
        if got is None:
            # this level has no number of its own: the per-reference tool
            # returned the hit with everything under it inlined, cut at the
            # app's cap
            text = json.dumps(_retrieval.retrieve_section(ref, start),
                              default=str)
            body = tree[target][2][:80]
            snippet = json.dumps(body)[1:-1]
            out["fetch_chars"] += min(len(text), APP_REFERENCE_CAP)
            out["reached"] = bool(body) and snippet in text[:APP_REFERENCE_CAP]
            steps.append(f"retrieve_section {start} ({len(text):,} chars"
                         + (", cut" if len(text) > APP_REFERENCE_CAP else "")
                         + ")")
            break
        out["fetch_chars"] += _size(got)
        steps.append(f"get {sid}")
    else:
        out["reached"] = True
    out["route"] = "search -> " + " -> ".join(steps)
    return out


def run_questions(verbose: bool = True) -> list[dict]:
    rows = []
    trees: dict = {}
    for q in QUESTIONS:
        tree = trees.setdefault(q["ref"], section_tree(q["ref"]))
        r = replay(q, tree)
        r.update(ref=q["ref"], target=q["target"], query=q["query"])
        rows.append(r)
    if verbose:
        print(f"{'ref':<22}{'target':<11}{'rank':>5}{'reached':>9}"
              f"{'search':>8}{'fetch':>8}{'total':>8}  route")
        for r in rows:
            print(f"{r['ref']:<22}{r['target']:<11}{str(r['rank'] or '-'):>5}"
                  f"{'yes' if r['reached'] else 'no':>9}{r['search_chars']:>8}"
                  f"{r['fetch_chars']:>8}"
                  f"{r['search_chars'] + r['fetch_chars']:>8}  {r['route']}")
        n = len(rows)
        print(f"recall@{K}: {sum(1 for r in rows if r['rank'])}/{n}   "
              f"reached: {sum(1 for r in rows if r['reached'])}/{n}")
    return rows


# ---------------------------------------------------------------------------
# the ranking guard: top-level sections found by their own titles
# ---------------------------------------------------------------------------

def title_top1() -> dict:
    """``{"ref|section_id": first hit's section_id}`` for every section at
    the top level of its file, searched for by its own title."""
    out = {}
    for ref_dir in sorted(PKG.iterdir()):
        if not (ref_dir / "text").is_dir():
            continue
        ref = ref_dir.name
        for sid, (_parent, top, _body) in section_tree(ref).items():
            if not top:
                continue
            title = _title_of(ref, sid)
            if not title:
                continue
            hits = _retrieval_db.reference_search(title, reference=ref,
                                                  limit=K)
            first = hits[0].get("section_id") if hits and "error" not in hits[0] else None
            out[f"{ref}|{sid}"] = first
    return out


_TITLES: dict = {}


def _title_of(ref: str, sid: str) -> str:
    if ref not in _TITLES:
        titles = {}
        for jf in sorted((PKG / ref / "text").glob("*.json")):
            for s in json.loads(jf.read_text(encoding="utf-8")).get("sections", []):
                if isinstance(s, dict):
                    titles.setdefault(s.get("section_id", ""), s.get("title", ""))
        _TITLES[ref] = titles
    return _TITLES[ref].get(sid, "")


def compare_titles(before: dict, after: dict) -> None:
    keys = sorted(set(before) & set(after))
    self_before = [k for k in keys if before[k] == k.split("|", 1)[1]]
    lost = [k for k in self_before if after[k] != before[k]]
    gained = [k for k in keys if after[k] == k.split("|", 1)[1]
              and before[k] != after[k]]
    changed = [k for k in keys if before[k] != after[k]]
    print(f"top-level sections searched by title: {len(keys)}")
    print(f"  found themselves first before: {len(self_before)}")
    print(f"  ... and no longer: {len(lost)}")
    for k in lost:
        print(f"      {k}  now first: {after[k]}")
    print(f"  found themselves first only after: {len(gained)}")
    print(f"  first hit changed at all: {len(changed)}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--titles", action="store_true",
                    help="also run the ranking guard over every top-level "
                         "section's title")
    ap.add_argument("--save", help="write the results to this JSON file")
    ap.add_argument("--compare", help="a file --save wrote earlier")
    args = ap.parse_args(argv)
    _retrieval_db.rebuild_db()
    result = {"questions": run_questions()}
    if args.titles:
        result["titles"] = title_top1()
        if args.compare:
            before = json.loads(Path(args.compare).read_text(encoding="utf-8"))
            compare_titles(before.get("titles", {}), result["titles"])
    if args.save:
        Path(args.save).write_text(json.dumps(result, indent=1),
                                   encoding="utf-8")


if __name__ == "__main__":
    main()
