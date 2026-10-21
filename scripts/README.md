# geotech-references / scripts

Build tools for the `geotech-references` library. These are NOT installed
with the package — they live alongside it for content generation and
validation work.

## Overview

> `build_chapter_text.py` is retired: chapter JSON is now written by hand
> from the printed pages (see the repo's `CLAUDE.md`). `build_printed_text.py`,
> `build_figure_catalog.py` and `check_section_numbers.py` are the live tools.

The **chapter text extraction pipeline** converts source PDF documents into
structured JSON files matching the schema used by `geotech_references._retrieval_db`.
Once a reference has its `text/chapterNN.json` files in place, the existing
`reference_search`, `reference_get`, and `reference_query` tools work for it
automatically.

| Script | Purpose |
|---|---|
| `build_chapter_text.py` | Generic PDF → chapter JSON pipeline (LLM-assisted) |
| `audit_chapter_text.py` | Validate generated JSON against schema and equation index |
| `chapter_schema.json` | JSON schema codifying the chapter file format |
| `manifests/` | Per-reference manifest files (chapter page ranges + PDF paths) |

---

## Quick start

### 1. Check the manifest

All current manifests already have page ranges filled in. You can skip
`discover` unless you're adding a new reference.

```bash
# Only needed for a new reference without page ranges:
python scripts/build_chapter_text.py discover scripts/manifests/<ref>.json
# For PDFs with no embedded TOC (GEC-11, UFC docs), discover scans
# page text for 'CHAPTER N' headings automatically.
```

### 2. Dry run

Verify chunk breakdown before spending API tokens:

```bash
python scripts/build_chapter_text.py extract scripts/manifests/gec_7.json \
    --chapters 6 --dry-run
```

### 3. Extract — Anthropic (local)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/build_chapter_text.py extract scripts/manifests/gec_7.json \
    --chapters 6,7,8,9,10
```

### 4. Extract — OpenAI-compatible endpoint (Foundry / Azure / OpenAI)

```bash
python scripts/build_chapter_text.py extract scripts/manifests/gec_7.json \
    --provider openai \
    --model gpt-4.1 \
    --base-url https://<stack>.palantirfoundry.com/api/v2/aip/openai \
    --api-key <your-foundry-token>
```

Default model for `--provider openai` is `gpt-4.1`. Override with `--model`.

### 5. Audit the output

```bash
python scripts/audit_chapter_text.py dm7_1
python scripts/audit_chapter_text.py gec_7
```

The auditor checks schema validity, equation cross-reference coverage,
`implemented_in` resolvability, and section ID uniqueness. Anything flagged
needs human review against the source PDF.

---

## Adding a new reference

1. Create `manifests/<reference_id>.json` (see existing files for format).
   Set `pdf_path` (relative to the manifest file), `package` (the
   `geotech_references` subpackage name), and a chapter list.
2. If page ranges are unknown: run `discover` to fill them from the PDF
   outline. For PDFs with no embedded TOC, discover falls back to text-scan
   automatically.
3. Dry-run → extract → audit.

No per-reference Python code is needed — the pipeline is generic.

---

## Cost / time notes

- `discover` and `--dry-run` are free (no LLM calls).
- A full extract of a 300-page reference runs ~5-10 minutes at ~$2-3 on
  Sonnet (≈ $0.008/page). Cost scales linearly with page count.
- The auditor is free and runs in seconds.

### What DM7 actually cost (2026-04-07)

~$21 total ($18 Sonnet + $3 Opus) for 1,307 pages across both volumes,
including ~$8 of iteration waste during pipeline development. Inherent
floor is ~$13 for the LLM reads alone. Future references at stable pipeline
should be ~$0.008/page.

---

## Reference text coverage status (2026-10-21)

| Reference | Sections | Summary fields | Status |
|---|---|---|---|
| `dm7_1` | 457 | all | Complete: 8 chapters |
| `dm7_2` | 438 | all | Complete: prologue + 6 chapters |
| `micropile` | 69 | all | Complete: 10 chapters |
| `gec_6` | 127 | none | Body-only, 10 chapters |
| `gec_7` | 37 | none | Body-only, chapters 1-5 |
| `gec_10` | 124 | none | 2018 edition (FHWA-NHI-18-024), all 18 chapters |
| `gec_11` | 183 | none | Vols I and II, 11 chapters |
| `gec_12` | 187 | none | Body-only, chapters 1-8 |
| `gec_13` | 773 | 747 of 773 | 10 chapters, rebuilt from the print |
| `ufc_pavement` | 317 | all | UFC 3-250-01 (2016) rebuilt from the real document; 21 chapters |
| `ufc_backfill`, `ufc_expansive` | - | n/a | No chapter text |

Section and summary counts are from `geotech_references._retrieval_db.list_indexed_references()`
(2026-10-21), which lists all 31 packages that have chapter text; the other
packages (GEC-4, 5, 8, 9, 14, the UFC practice manuals, Eurocode 7, and so on)
are listed there with their own counts. Deleted modules (`fema_p2192`,
`noaa_frost`, `ufc_dewatering`) are no longer in the library.

---

## Schema reference

Every `text/chapterNN.json` conforms to `chapter_schema.json`:

```json
{
  "reference_id": "FHWA-NHI-14-007",
  "reference_title": "Soil Nail Walls Reference Manual",
  "volume": null,
  "chapter": 6,
  "chapter_title": "Design of Soil Nail Walls",
  "sections": [
    {
      "section_id": "6.1",
      "title": "Introduction",
      "summary": "50-700 char search-result preview...",
      "body": "Full narrative text...",
      "key_points": ["bullet 1", "bullet 2"],
      "equations": [{"id": "Eq. 6-1", "description": "...", "implemented_in": null}],
      "figures": ["Figure 6-1: ..."],
      "tables": ["Table 6-1: ..."],
      "applicability": "One sentence on when this section applies."
    }
  ]
}
```

The `summary` field is what `reference_search` returns in ranked hits.
Full `body` is only returned by `reference_get`. This separation is the
noise-reduction lever for agent retrieval.
