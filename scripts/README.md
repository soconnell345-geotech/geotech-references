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

## Phasing of the DM7 effort

This script is **Phase 1** of the DM7 chapter text plan. See
`~/.claude/plans/cozy-pondering-sutton.md` for the full plan.

- **Phase 1 (this commit)**: pipeline scripts, manifests, schema. No JSON
  files generated yet, no adapter changes.
- **Phase 2 (manual)**: Run the pipeline against UFC 3-220-10 and
  UFC 3-220-20 with an Anthropic API key. Audit. Spot-check.
- **Phase 3 (next code commit)**: Split `funhouse_agent/adapters/dm7_adapter.py`
  into `dm7_1_adapter.py` and `dm7_2_adapter.py`, wire `add_text_retrieval`
  for both, update `_REFERENCE_CATALOG` in `references_agent.py` to flip
  `has_text: True`, update `funhouse_agent/reviewer.py` REFERENCE_MODULES,
  ship as `geotech-references` v1.2.0 + main repo v4.6.0.
