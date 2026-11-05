# REF-54 (with REF-37): the literal hits that expansion pushed out

Branch `claude/ref-54-literal-hits`, from main 25f7d7f. Cloud session,
2026-11-05. Commits:

- fbd89cd: auto fuses the literal and synonym hits instead of pinning only
  the literal top-1
- 7b4cdd9: REF-37, the synonym entries that change the quantity, pruned
- 890baba: only the literal top 3 vote in the fusion (a fix to fbd89cd,
  after the cross-reference eval fell)

## Cause

In `reference_search`, the default `auto` strategy ran the literal query and
the combined query, `(literal) OR synonyms`. It kept the literal top-1
(`EXPANSION_PIN`) and filled the other nine places from the combined query's
BM25 order (`merge_hits(literal[:1], combined, ...)`). Sections that hold a
synonym but none of the literal words score well in BM25 over the union, and
long Glossary, Primary References and Description sections hold many group
forms. So the literal ranks 2 to 10 were pushed down. "PVD spacing design"
has GEC-13 2.4.2 and 2.4.3 at literal ranks 3 and 5, and they fell to ranks
12 and 26.

Across 789 queries that fire a synonym group and have literal hits (the gold
set plus every section title that fires a group), 287 lost at least one
literal top-5 hit from the top 10, and 218 lost a literal top-3 hit.

Three of the item's examples have another cause, and this branch does not
change them (see "Noted, not fixed"):

- **liq-screen** fires no synonym group;
- **auger-cast** and **spt-def** have no literal hits at all. Their AND form
  matches nothing, so they take the zero-literal path
  (`substituted_query`, then the OR of their words).

## What changed

`_query_expansion.fuse_hits` (new), used by `reference_search` under `auto`
when the literal query has hits and a group fires. It works in three steps:

1. **Pin.** The literal top `EXPANSION_PIN` (1) stays in place, as before.
   The title guard is unchanged.
2. **Fuse.** Every other section gets a reciprocal-rank score,
   `1/(k + combined rank)`. The literal top `FUSION_VOTES` (3) also get
   `+ 1/(k + literal rank)`. `k` = `FUSION_K` = 3 (env
   `GEOTECH_RETRIEVAL_FUSION_K`).
3. **Guarantee.** The literal hit at rank r, for r <= `FUSION_KEEP` (5), is
   placed no lower than 2r. So the literal top 5 always stays in a top 10.

Both lists are fetched at a fixed pool of 50 (`_FUSION_POOL`), not the page
size. A page with `offset` / `max_chars` is therefore cut from the same order
as a plain call (test `test_auto_pages_are_cut_from_one_order`).

Why only the literal top 3 vote: every literal hit is also a hit of the
combined query. When every literal hit voted (fbd89cd), the whole literal
list ranked ahead of every synonym-only hit. `scripts/eval_retrieval_recall.py`
then fell from 4/9 to 2/9 under `auto`:

- "phreatic surface" lost dm7_2 5-3.2 (groundwater table);
- "degree of compaction" lost GEC-6 5.3.5.

Measured variants (`auto`, gold R@5 / R@10, cross-reference eval):

| variant | gold R@5 | gold R@10 | eval_retrieval_recall |
|---|---|---|---|
| main (pin 1, union fills) | 38 | 43 | 4/9 |
| every literal hit votes (fbd89cd) | 42 | 44 | 2/9 |
| literal top 5 vote | 42 | 44 | 2/9 |
| literal top 4 vote | — | — | 3/9 |
| **literal top 3 vote (chosen)** | **41** | **44** | **4/9** |
| combined order + guarantee only | 39 | 44 | 4/9 |

These numbers include the REF-37 pruning, except the fbd89cd row. Rank
constants 0, 5 and 10 give R@5 41 with votes 3 (`--fusion-k`).

`figure_search` is unchanged: it still pins the literal top-1, and no gold
set measures it.

`scripts/eval_retrieval_gold.py` gains `--fusion-k`. CLAUDE.md's "Lexical
Query Expansion" section describes the fusion and the pruning.

## Recall on the gold set (`scripts/retrieval_gold.json`, 54 cases)

`python scripts/eval_retrieval_gold.py --per-case`

| mode | R@3 before | R@3 after | R@5 before | R@5 after | R@10 before | R@10 after | MRR before | MRR after |
|---|---|---|---|---|---|---|---|---|
| off | 30 | 30 | 32 | 32 | 33 | 33 | .477 | .477 |
| fill | 34 | 34 | 37 | 37 | 39 | 39 | .525 | .525 |
| auto | 35 | 37 | 38 | 41 | 43 | 44 | .562 | .570 |
| rerank | 32 | 32 | 36 | 36 | 40 | 40 | .515 | .512 |

"Top-1 changed" stays 8 for auto (all of them queries the literal search
answers with nothing).

Every gold case that moved (rank of the first relevant hit, main -> branch):

| mode | case | before | after | why |
|---|---|---|---|---|
| auto | pvd-spacing | - (12) | 4 | fusion (literal 3, 5) |
| auto | beta-pile | 4 | 2 | fusion (literal 2) |
| auto | phi-cpt | 6 | 3 | fusion (literal 3) |
| auto | rel-compaction | 6 | 3 | fusion (literal 3) |
| auto | ec7-bearing | 7 | 5 | pruning (no "ultimate bearing" in the union) |
| auto | neutral-plane | 2 | 4 | fusion: literal top-3 hits voted ahead (target literal 4) |
| auto | cpt-def | 2 | 3 | fusion: a literal top-3 hit voted ahead (literal 8) |
| auto | dmt-def | 4 | 6 | fusion: literal top-3 hits voted ahead (literal 12); **leaves the top 5** |
| rerank | cfa-piles | 2 | 3 | pruning (rerank is the union alone) |

mse-pullout (literal 5) stays at 7 under auto. Literal rank 5 is past the
three that vote, so the fusion does not lift it; the guarantee only keeps it
within 2r = 10.

Other guards, run on main and on the branch:

- `scripts/eval_subsection_retrieval.py --titles --compare`: 7,357
  top-level titles; first hit changed for 0; recall@5 15/15 on both.
- `scripts/eval_retrieval_recall.py` (9 trusted cases): auto 4/9 on both;
  off, fill and rerank are also unchanged.
- Literal top 5 kept in the top 10: 694 of 694 synonym queries (main: 287
  of 789 lost one; the count of queries falls because the pruned groups no
  longer fire).

The gold set is in sample (REF-07): it was written beside the synonym
curation. The votes and the rank constant were chosen on it and on the
cross-reference eval, so these numbers flatter the choice.

## Synonym entries removed (REF-37)

| entry | group | why |
|---|---|---|
| `cohesion` | undrained shear strength / su | the drained cohesion c' is another quantity; "drained cohesion" fired su |
| `ultimate bearing` | bearing capacity | "allowable bearing capacity" fired ultimate bearing |
| `tip resistance` | end bearing | the manuals print it for the CPT cone tip resistance qc (UFS 3-220-10 Sec. 2-7.2.1, 8-3.3); 51 sections, nearly all CPT |
| whole group `settlement` / `consolidation settlement` / `compression settlement` | settlement | "immediate settlement" fired consolidation settlement; GEC-6 Sec. 5.2.3.8 and GEC-8 Sec. 5.5.3.2 print "compression settlement" for granular soil, and DM 7.1 for secondary compression |
| `load-transfer curve` | t-z | UFC 3-220-20 Sec. 6-5.8.4.2 prints "load transfer-displacement relationships, i.e., t-z and q-z curves", so the term covers q-z too; its one other use (GEC-10 13.2.3.4.8) is measured side load transfer |
| `active resistance` | active earth pressure | dead: printed nowhere in the library, and not a term (the active side is a pressure) |

Other dead forms (0 sections print them) were **kept on purpose**: `dsm`,
`underseepage`, `pile freeze` and `interface adhesion`. They are terms an
engineer types, and they fire their group from the query. The dsm-geometry
gold case and two existing tests ("groundwater control underseepage",
"interface adhesion on the wall") depend on them. The module docstring
states the rule. If the owner wants every unprinted form gone, delete those
four entries; dsm-geometry will then fail.

Tests pin each near-miss: `test_wrong_quantity_near_misses_do_not_fire`.
`test_added_groups_fire` now checks t-z through "t-z method" -> "t z curve",
not through the removed form.

## Tests

The environment's `python` resolves to 3.11, so all runs use Python 3.13.18
(`python3.13 -m pytest`). numpy, scipy, matplotlib and pymupdf are installed
for the optional-dependency tests.

- Whole suite, branch tip, serial (`-p no:xdist`): **6,485 passed, 2
  xfailed, 0 failed**, exit 0.
- Whole suite, main in a worktree, serial: 6,469 passed, 2 xfailed, exit 0.
  The branch adds 16 tests: 2 fuse_hits unit tests, the votes test, 5
  keep-the-literal-top-5 queries, the paging test, 7 near-miss cases.
- With `-n 4`: 6,468 passed, 2 xfailed, 17 errors (sqlite "disk I/O error"
  / "table sections already exists" in `test_retrieval_db.py` and
  `test_query_expansion.py`). Main has the same errors under xdist (125 on
  the three retrieval test files alone). Their module fixtures call
  `rebuild_db()` on one shared database file from every worker. This is
  pre-existing, so the serial runs above are the verdict.

## Noted, not fixed

- **liq-screen** ("liquefaction susceptibility screening fines content"):
  no group fires and the literal AND form matches nothing, so this is the
  OR-of-words ranking (REF-48's concept count). GEC-5 5.6.1 is at rank 16
  on main and on the branch.
- **auger-cast**: the literal form matches nothing, so `substituted_query`
  and the OR fallback rank it. dm7_2 6-4.3 (gold) is at 4 on both; GEC-8
  3.2 and its subsections stay outside the top 10.
- **spt-def**: the literal form matches nothing. The top hits are SPT
  sections in GEC-12, the soils manual and EN 1997-2 (eurocode_7_2 4.6, gold,
  at 6 on both).
- **dmt-def** leaves the top 5 (4 -> 6), and neutral-plane drops 2 -> 4:
  literal top-3 hits that are not the gold sections now vote ahead of the
  combined query's pick.
- `figure_search` still uses the pin-1 merge. It has the same shape of
  defect, but there is no figure gold set to measure a change on.
- Under pytest-xdist the retrieval tests race on one database file (above).
- `pseudostatic` is printed once (the print has "pseudo-static", which
  tokenizes as two words), and `normalized blow count`, `vibro-flotation` and
  `dmm` once each. They are not dead, so they were left.
