# geotech-references / scripts

Build tools for the `geotech-references` library. These are NOT installed
with the package — they live alongside it for content generation and
validation work.

## Overview

The current focus is the **chapter text extraction pipeline**, which converts
source PDF documents into structured JSON files matching the schema used by
`geotech_references._retrieval`. Once a reference has its `text/chapterNN.json`
files in place, the existing `retrieve_section`, `search_sections`,
`list_chapters`, and `load_chapter` functions work for it automatically.

| Script | Purpose |
|---|---|
| `build_chapter_text.py` | Generic PDF → chapter JSON pipeline (LLM-assisted) |
| `audit_chapter_text.py` | Validate generated JSON against the schema and equation index |
| `chapter_schema.json` | JSON schema codifying the chapter file format |
| `manifests/` | Per-reference manifests describing chapter page ranges |

## Quick start: building DM7 chapter text

The first reference scheduled for extraction is DM7 (UFC 3-220-10 and
UFC 3-220-20). Manifests are already in place at
`manifests/dm7_1.json` and `manifests/dm7_2.json`, but their page ranges
are empty until you run `discover` against the source PDFs.

### 1. Discover chapter page ranges

```bash
cd geotech-references

# Reads the PDF outline and fills in page_start/page_end for each chapter.
# Idempotent — re-runs just update the manifest in place.
python scripts/build_chapter_text.py discover scripts/manifests/dm7_1.json
python scripts/build_chapter_text.py discover scripts/manifests/dm7_2.json
```

After running, eyeball the manifests and fix any chapters that came back
as `null` (the discover step does best-effort title matching against the
PDF outline; some titles may need a manual nudge).

### 2. Dry run

Verify the prompt construction works before burning API calls:

```bash
python scripts/build_chapter_text.py extract scripts/manifests/dm7_1.json \
    --chapters 1 --dry-run
```

This splits the PDF, builds the LLM prompt, prints stats, and exits without
calling the API. Use it to confirm the source text comes through cleanly
and the prompt fits in the model context.

### 3. Smoke-test extract one chapter

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/build_chapter_text.py extract scripts/manifests/dm7_1.json \
    --chapters 1
```

This calls Claude (default model: `claude-opus-4-6`), parses the JSON,
runs equation cross-reference injection, validates against the schema,
and writes `geotech_references/dm7_1/text/chapter01.json`. Failed
validations write a `chapter01.json.draft` file you can inspect by hand.

### 4. Full extraction

Once chapter 1 looks right, run the full extraction:

```bash
python scripts/build_chapter_text.py extract scripts/manifests/dm7_1.json
python scripts/build_chapter_text.py extract scripts/manifests/dm7_2.json
```

Cost estimate: each chapter is roughly 30-80 pages × ~2k chars/page ≈
60-160k input tokens. UFC 3-220-10 has 8 chapters; UFC 3-220-20 has
prologue + 6 chapters. Total: ~15 LLM calls. With Claude Opus 4.6
input pricing this is on the order of $5-15 for both volumes combined.

**Oversized chapters.** Three chapters exceed a single 200k-token context
window when extracted as raw text:

- `dm7_1` ch 8 (Correlations) — 155 pp, ~289k chars
- `dm7_2` ch 6 (Deep Foundations) — 144 pp, ~302k chars
- `dm7_2` ch 7 (Probability and Reliability) — 179 pp, ~346k chars
  (mostly appendices that follow the actual chapter content)

These all fit within the script's 600k char cap **on the 1M-context Opus
variant** (`CHAPTER_TEXT_MODEL=claude-opus-4-6[1m]`). On the standard
200k-context model, the script will truncate at 600k chars and the
auditor will flag the missing sections — you can either:

1. Use the 1M-context model: `export CHAPTER_TEXT_MODEL='claude-opus-4-6[1m]'`
2. Manually trim the manifest's `page_end` for ch7 of dm7_2 to exclude
   appendices (the actual reliability content ends well before page 724)
3. Split the chapter into multiple manifest entries with sub-page ranges
   (not currently supported by the script — would need a small extension)

### 5. Audit the output

```bash
python scripts/audit_chapter_text.py dm7_1
python scripts/audit_chapter_text.py dm7_2
```

The auditor checks:

- Schema validity (required fields, section_id format, body length, key_points sanity)
- Equation cross-reference coverage (every `Eq X-Y` in the equation module's
  docstrings must appear in some section's `equations` array)
- `implemented_in` resolvability (every claimed function path must import successfully)
- Section ID uniqueness within a chapter

Anything flagged needs human review against the source PDF. The body
narrative is trusted unless flagged — the auditor never re-reads the PDF
because that defeats the cost benefit of automation.

### 6. Spot-check (recommended)

After the auditor is clean, randomly sample ~10% of sections and verify
them against the source PDF by hand. This catches LLM fidelity issues
that the auditor cannot detect (e.g., paraphrased technical content,
omitted nuance).

## Adding a new reference

To run the pipeline against a new reference (gec_10, gec_11, future
references):

1. Create a manifest at `manifests/<reference_id>.json` following the
   `dm7_1.json` format. Set `pdf_path` (relative to the manifest file),
   `package` (the `geotech_references` subpackage name), and a chapter
   list with `null` page ranges.
2. Run `build_chapter_text.py discover` to fill in page ranges.
3. Proceed through dry-run → smoke test → full extract → audit.

The pipeline is generic — no per-reference Python code is needed.

## Cost / time notes

- `discover` is free and fast (PyMuPDF outline parse).
- `--dry-run` is free.
- A full `extract` of UFC 3-220-10 (8 chapters, 583 pages) takes ~5-10
  minutes of wall clock time and a few dollars of API spend.
- The auditor is free and runs in seconds.

## Current state — DM7 (2026-04-07)

After this commit, both UFC 3-220-10 (`dm7_1`) and UFC 3-220-20 (`dm7_2`)
have substantially complete chapter text:

| File | Sections | Equation refs | Status |
|---|---|---|---|
| `dm7_1/text/chapter01.json` | 65 | 6/6 | OK |
| `dm7_1/text/chapter02.json` | 77 | 3/3 | OK |
| `dm7_1/text/chapter03.json` | 43 | 4/5 | missing 1 eq |
| `dm7_1/text/chapter04.json` | 58 | 11/12 | missing Eq 4-12 |
| `dm7_1/text/chapter05.json` | 63 | 27/28 | missing Eq 5-19 |
| `dm7_1/text/chapter06.json` | 52 | 15/15 | OK |
| `dm7_1/text/chapter07.json` | 52 | 5/6 | missing Eq 7-2 |
| `dm7_1/text/chapter08.json` | 47 | 45/45 | OK |
| `dm7_2/text/prologue.json` | 40 | 3/0 | OK |
| `dm7_2/text/chapter02.json` | 51 | 10/10 | OK |
| `dm7_2/text/chapter03.json` | 68 | 10/10 | OK |
| `dm7_2/text/chapter04.json` | 61 | 26/31 | missing 4-20, 4-21, 4-22, 4-29, 4-30 |
| `dm7_2/text/chapter05.json` | 75 | 42/42 | OK |
| `dm7_2/text/chapter06.json` | 103 | 72/74 | missing 6-38, 6-39 |
| `dm7_2/text/chapter07.json` | 40 | 15/16 | missing 7-16; appendices NOT extracted |

**Totals:** 895 sections, 295/307 equations cross-referenced (96.1%), built
on Sonnet 4.6 with section-level chunking, parallel execution, and
automatic recursive subdivision of oversized chunks. Chunks above 35k
chars / 15 pages are auto-split using deeper PDF outline levels.

The two original chapter-scoped extracts (Opus 4.6, ch1 and ch4 of
`dm7_1`) are quarantined under `dm7_1/text/_v0_chapter_scoped/` for
diffing against the section-level output. They are not loaded by the
retrieval layer.

## What's still TODO for DM7

### Phase 2 leftovers (small API spend)

1. **Spot-fix 12 missing equations** by re-extracting just the chunks
   containing them. Each chunk is ~5-10 pages and runs in 30-60 s on
   Sonnet. Total cost ~$1. Equation IDs:
   - dm7_1: Eq 3-? (ch3), Eq 4-12, Eq 5-19, Eq 7-2
   - dm7_2: Eqs 4-20/21/22/29/30, Eqs 6-38/39, Eq 7-16

2. **Decide on UFC 3-220-20 appendices** (pp ~595-724). The PDF outline
   doesn't have entries for the appendices, so they all got lumped
   under the `7-6 SUGGESTED READING` chunk which failed extraction
   (130 pages, 256k chars). Pages ~600-650 contain real engineering
   content (Appendix B on retaining-structure analysis, glossary). Two
   options:
   - Skip them as out-of-scope (no API cost).
   - Add explicit appendix entries to `manifests/dm7_2.json` with
     manual page ranges and run them through the pipeline as
     pseudo-chapters (~$3-5 of API).

### Phase 3 (no API spend, mechanical wiring + SQL layer)

This is the biggest remaining piece and is what makes the JSON files
actually queryable by the agent.

1. **Build SQLite FTS5 retrieval layer** at
   `geotech_references/_retrieval_db.py`:
   - Lazy build from chapter JSONs at first call (not committed as
     binary; rebuilt on demand).
   - Single FTS5 virtual table indexing `title`, `summary`, `body`,
     `key_points`, `applicability` with porter stemming and BM25 ranking.
     Structural columns (`reference`, `chapter`, `section_id`, etc.)
     stored UNINDEXED.
   - New tools: `reference_search(query, reference=None, chapter=None,
     limit=5)` returns ranked summary-only hits, `reference_get(reference,
     section_id)` returns full body, `reference_query(sql)` runs read-only
     constrained SELECTs (URI mode read-only conn, regex SELECT-only
     check, server-side LIMIT cap).
   - **Crucially: search hits return `summary` only, not `body`.** This
     is the noise-reduction lever for the agent retrieval surface.

2. **Wire DM7 text retrieval into Funhouse adapters.** Split
   `funhouse_agent/adapters/dm7_adapter.py` into `dm7_1_adapter.py` and
   `dm7_2_adapter.py`. Each calls `add_text_retrieval(registry, info,
   "dm7_1", "UFC 3-220-10")` etc. Update
   `funhouse_agent/adapters/__init__.py` MODULE_REGISTRY (replace `dm7`
   entry with `dm7_1` + `dm7_2`). Update `funhouse_agent/reviewer.py`
   REFERENCE_MODULES.

3. **Wire DM7 text retrieval into Foundry side.** Update
   `geotech-references/agents/dm7_agent.py` analogously. Flip
   `has_text: True` for `dm7_1` and `dm7_2` in
   `geotech-references/agents/references_agent.py` `_REFERENCE_CATALOG`.

4. **Add the new SQL tool surface to both Funhouse and Foundry agents**
   alongside the existing four (Option A — backward-compat, no migration
   of existing references' callers). The Foundry SQL tool is gated to
   read-only SELECTs the same way as the Funhouse one.

5. **Tests:** add `geotech-references/tests/test_dm7_text.py` and
   `funhouse_agent/tests/test_dm7_text_retrieval.py`.

6. **Fix DM7 source citation bug** (todo item 6). DESIGN.md and chapter
   docstrings claim NAVFAC DM 7.01/7.02 (1986); the actual source is
   UFC 3-220-10 (2022) and UFC 3-220-20 (2025). Audit and correct.

7. **Bump versions.** `geotech-references/pyproject.toml` 1.1.0 → 1.2.0
   (additive: new chapter JSONs + new retrieval module). Main repo
   `pyproject.toml` → 4.6.0.

## Phasing of the DM7 effort

See `~/.claude/plans/cozy-pondering-sutton.md` for the original plan and
its mid-flight redesign notes.

- **Phase 1 (DONE)**: pipeline scripts, manifests, schema.
- **Phase 2 (~95% DONE)**: pipeline runs that produced the 895 sections
  above. Remaining: spot-fix 12 missing equations and decide on
  appendices.
- **Phase 3 (NOT STARTED)**: SQLite FTS5 retrieval layer + adapter
  wiring + version bump + Foundry/Funhouse integration.
