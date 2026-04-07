#!/usr/bin/env python3
"""
build_chapter_text.py — Generic LLM-assisted PDF → chapter JSON pipeline.

Reads a manifest describing a reference's chapters and source PDF, splits the
PDF by chapter using PyMuPDF, sends each chapter's text to Claude, and writes
the resulting structured JSON to geotech_references/<package>/text/chapterNN.json.

The output schema matches gec_7/text/chapterNN.json and is consumed by the
existing geotech_references._retrieval module — once these files exist, the
retrieve_section / search_sections / list_chapters / load_chapter functions
work automatically.

Usage
-----
    # Discover chapter page ranges from the PDF outline and update the manifest
    python build_chapter_text.py discover scripts/manifests/dm7_1.json

    # Extract one chapter (smoke test)
    python build_chapter_text.py extract scripts/manifests/dm7_1.json --chapters 1

    # Extract all chapters
    python build_chapter_text.py extract scripts/manifests/dm7_1.json

    # Dry-run (split PDF, build prompts, do NOT call the LLM)
    python build_chapter_text.py extract scripts/manifests/dm7_1.json --dry-run

Environment
-----------
    ANTHROPIC_API_KEY   required for `extract` (not for `discover` or --dry-run)
    CHAPTER_TEXT_MODEL  optional; defaults to claude-opus-4-6

Phasing
-------
This script is Phase 1 of the DM7 chapter text effort. Phase 2 is running it
(human, with API key). Phase 3 is splitting the dm7 adapter and wiring text
retrieval into Funhouse + Foundry. See the plan at
~/.claude/plans/cozy-pondering-sutton.md.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import os
import re
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent  # geotech-references/
PACKAGE_DIR = REPO_DIR / "geotech_references"
SCHEMA_PATH = SCRIPT_DIR / "chapter_schema.json"

DEFAULT_MODEL = os.environ.get("CHAPTER_TEXT_MODEL", "claude-opus-4-6")
# Char budget for the user message. Claude Opus 4.6 has a 200k-token context
# window (~800k chars), and the 1M-context variant has 5x that. We reserve
# headroom for the system prompt, the instructions block, and the 16k-token
# response, which leaves ~600k chars for chapter text on the standard model.
# Chapters exceeding this cap are truncated; the auditor will flag missing
# sections so the user can either split the chapter via the manifest or use
# the 1M-context model.
MAX_PROMPT_CHARS = 600_000


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------

@dataclass
class ChapterSpec:
    number: int
    title: str
    page_start: int | None
    page_end: int | None
    equation_module: str | None
    filename: str | None  # override for non-numeric chapters (e.g., "prologue")

    @property
    def output_name(self) -> str:
        if self.filename:
            return f"{self.filename}.json"
        return f"chapter{self.number:02d}.json"


@dataclass
class Manifest:
    reference_id: str
    reference_title: str
    volume: int | None
    pdf_path: Path
    package: str
    chapters: list[ChapterSpec]

    @classmethod
    def load(cls, manifest_path: Path) -> "Manifest":
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pdf_path = (manifest_path.parent / data["pdf_path"]).resolve()
        chapters = [
            ChapterSpec(
                number=ch["number"],
                title=ch["title"],
                page_start=ch.get("page_start"),
                page_end=ch.get("page_end"),
                equation_module=ch.get("equation_module"),
                filename=ch.get("filename"),
            )
            for ch in data["chapters"]
        ]
        return cls(
            reference_id=data["reference_id"],
            reference_title=data["reference_title"],
            volume=data.get("volume"),
            pdf_path=pdf_path,
            package=data["package"],
            chapters=chapters,
        )

    def save(self, manifest_path: Path) -> None:
        out = {
            "reference_id": self.reference_id,
            "reference_title": self.reference_title,
            "volume": self.volume,
            "pdf_path": str(
                Path(os.path.relpath(self.pdf_path, manifest_path.parent))
            ).replace("\\", "/"),
            "package": self.package,
            "chapters": [
                {
                    k: v
                    for k, v in {
                        "number": ch.number,
                        "title": ch.title,
                        "filename": ch.filename,
                        "page_start": ch.page_start,
                        "page_end": ch.page_end,
                        "equation_module": ch.equation_module,
                    }.items()
                    if v is not None or k in ("page_start", "page_end")
                }
                for ch in self.chapters
            ],
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
            f.write("\n")


# ---------------------------------------------------------------------------
# PDF helpers (PyMuPDF, optional dep)
# ---------------------------------------------------------------------------

def _import_fitz():
    try:
        import fitz  # PyMuPDF
        return fitz
    except ImportError:
        sys.exit(
            "PyMuPDF is required. Install with:\n"
            "  pip install PyMuPDF\n"
            "(or `pip install geotech-staff-engineer[pdf]` from the main repo)"
        )


def discover_chapter_ranges(manifest: Manifest) -> Manifest:
    """Use the PDF outline (bookmarks) to fill in chapter page_start/page_end.

    Falls back to None for any chapter whose title cannot be matched in the
    outline; the user must then fill those in by hand.
    """
    fitz = _import_fitz()
    if not manifest.pdf_path.exists():
        sys.exit(f"PDF not found: {manifest.pdf_path}")

    doc = fitz.open(manifest.pdf_path)
    try:
        toc = doc.get_toc(simple=True)  # list of [level, title, page]
        n_pages = doc.page_count
    finally:
        doc.close()

    if not toc:
        print(
            "WARNING: PDF has no outline/bookmarks. Page ranges must be "
            "filled in manually in the manifest.",
            file=sys.stderr,
        )
        return manifest

    # Build a flat list of (title, 1-indexed page) for top-level entries.
    entries = [(title.strip(), page) for level, title, page in toc if level <= 2]

    # Try to match each chapter title against an outline entry.
    matched: list[tuple[ChapterSpec, int]] = []
    for ch in manifest.chapters:
        page = _match_chapter_in_toc(ch, entries)
        if page is not None:
            matched.append((ch, page))

    # Compute end pages from the *next* matched chapter's start, falling back
    # to total page count for the last chapter.
    matched_sorted = sorted(matched, key=lambda mc: mc[1])
    starts: dict[int, int] = {}
    for i, (ch, page) in enumerate(matched_sorted):
        starts[ch.number] = page
    ends: dict[int, int] = {}
    for i, (ch, page) in enumerate(matched_sorted):
        if i + 1 < len(matched_sorted):
            ends[ch.number] = matched_sorted[i + 1][1] - 1
        else:
            ends[ch.number] = n_pages

    # Apply to the manifest
    for ch in manifest.chapters:
        if ch.number in starts:
            ch.page_start = starts[ch.number]
            ch.page_end = ends[ch.number]
            print(f"  ch {ch.number}: pp. {ch.page_start}-{ch.page_end} ({ch.title})")
        else:
            print(
                f"  ch {ch.number}: NOT FOUND in PDF outline ({ch.title})",
                file=sys.stderr,
            )

    return manifest


def _match_chapter_in_toc(
    ch: ChapterSpec, entries: list[tuple[str, int]]
) -> int | None:
    """Best-effort title match between a manifest chapter and PDF outline."""
    title_lower = ch.title.lower()
    title_words = set(re.findall(r"[a-z]+", title_lower))
    if ch.filename == "prologue":
        for entry_title, page in entries:
            if "prologue" in entry_title.lower() or "preface" in entry_title.lower():
                return page
        return None

    chapter_pat = re.compile(rf"\bchapter\s*0*{ch.number}\b", re.IGNORECASE)
    best_score = 0
    best_page = None
    for entry_title, page in entries:
        et_lower = entry_title.lower()
        score = 0
        if chapter_pat.search(et_lower):
            score += 5
        entry_words = set(re.findall(r"[a-z]+", et_lower))
        common = title_words & entry_words
        score += len(common)
        if score > best_score:
            best_score = score
            best_page = page
    if best_score >= 3:
        return best_page
    return None


def extract_chapter_text(manifest: Manifest, ch: ChapterSpec) -> str:
    """Pull the raw text of a chapter from the source PDF."""
    if ch.page_start is None or ch.page_end is None:
        sys.exit(
            f"Chapter {ch.number} ({ch.title}) has no page range. Run "
            f"`discover` first or fill in the manifest manually."
        )
    fitz = _import_fitz()
    doc = fitz.open(manifest.pdf_path)
    try:
        pages_text = []
        for page_num in range(ch.page_start - 1, ch.page_end):  # 0-indexed
            page = doc[page_num]
            pages_text.append(f"\n\n[PAGE {page_num + 1}]\n\n{page.get_text()}")
        text = "".join(pages_text).strip()
    finally:
        doc.close()
    return text


# ---------------------------------------------------------------------------
# Equation cross-reference resolution
# ---------------------------------------------------------------------------

_EQ_NUMBER_PAT = re.compile(r"Eq(?:uation|\.)?\s*([0-9]+[-\u2013][0-9]+[a-z]?)", re.IGNORECASE)


def _normalize_eq_id(raw: str) -> str:
    """Normalize an equation id like 'Eq. 5-12' or 'Equation 5\u201312' to '5-12'."""
    m = _EQ_NUMBER_PAT.search(raw)
    if m:
        return m.group(1).replace("\u2013", "-")
    return raw.strip().lstrip("Eq.").strip().replace("\u2013", "-")


def build_equation_index(equation_module_path: str) -> dict[str, str]:
    """Map equation id (e.g. '5-12') → dotted function path.

    Inspects the digitized equation module, looks at each public function's
    docstring for an equation number reference, and builds a lookup index.
    """
    if not equation_module_path:
        return {}
    try:
        mod = importlib.import_module(equation_module_path)
    except ImportError as e:
        print(f"  WARNING: cannot import {equation_module_path}: {e}", file=sys.stderr)
        return {}

    index: dict[str, str] = {}
    for name, func in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith("_"):
            continue
        if getattr(func, "__module__", "") != mod.__name__:
            continue
        doc = inspect.getdoc(func) or ""
        # Find all equation numbers cited in the docstring
        for match in _EQ_NUMBER_PAT.finditer(doc):
            eq_id = match.group(1).replace("\u2013", "-")
            full_path = f"{equation_module_path}.{name}"
            # First citation wins (avoid overwriting if a function references multiple)
            index.setdefault(eq_id, full_path)
    return index


def inject_equation_links(chapter_json: dict, eq_index: dict[str, str]) -> dict:
    """Walk a chapter dict and fill in `implemented_in` for matched equations."""
    if not eq_index:
        return chapter_json

    def _walk(sections: list) -> None:
        for section in sections:
            equations = section.get("equations", [])
            for i, eq in enumerate(equations):
                if isinstance(eq, str):
                    # Legacy string form — try to extract the id and convert to dict
                    eq_id_norm = _normalize_eq_id(eq)
                    if eq_id_norm in eq_index:
                        equations[i] = {
                            "id": eq.split(":")[0].strip(),
                            "description": eq.split(":", 1)[1].strip() if ":" in eq else eq,
                            "implemented_in": eq_index[eq_id_norm],
                        }
                elif isinstance(eq, dict):
                    if eq.get("implemented_in") is None and eq.get("id"):
                        eq_id_norm = _normalize_eq_id(eq["id"])
                        if eq_id_norm in eq_index:
                            eq["implemented_in"] = eq_index[eq_id_norm]
            if "subsections" in section:
                _walk(section["subsections"])

    _walk(chapter_json.get("sections", []))
    return chapter_json


# ---------------------------------------------------------------------------
# LLM extraction
# ---------------------------------------------------------------------------

EXTRACTION_SYSTEM_PROMPT = """\
You are a technical document extraction assistant. You convert raw PDF text \
of a geotechnical engineering chapter into a structured JSON document \
following an exact schema. You preserve the source content faithfully — \
no paraphrasing into your own words, no editorializing, no skipping sections. \
Your job is to organize the source text into a navigable structure, not to \
rewrite it."""


def build_extraction_prompt(
    manifest: Manifest, ch: ChapterSpec, chapter_text: str
) -> str:
    """Construct the user prompt for one chapter's extraction call."""
    if len(chapter_text) > MAX_PROMPT_CHARS:
        # Truncate with a clear marker; the model will still produce JSON for
        # what it sees, and the auditor will flag missing sections.
        chapter_text = (
            chapter_text[:MAX_PROMPT_CHARS]
            + "\n\n[TRUNCATED — CHAPTER EXCEEDS PROMPT WINDOW]"
        )

    return textwrap.dedent(f"""
        Extract the following chapter from {manifest.reference_title} into structured JSON.

        Reference: {manifest.reference_id}
        Volume: {manifest.volume if manifest.volume is not None else "N/A"}
        Chapter: {ch.number}
        Chapter title: {ch.title}

        OUTPUT REQUIREMENTS

        Return a single JSON object with this exact top-level structure:

        {{
          "reference_id": "{manifest.reference_id}",
          "reference_title": "{manifest.reference_title}",
          "volume": {json.dumps(manifest.volume)},
          "chapter": {ch.number},
          "chapter_title": "{ch.title}",
          "sections": [ ... ]
        }}

        Each entry in `sections` must have:
          - section_id      : hierarchical id ("5.1", "5.7.2", "7.2.1.3.1", or "P.1" for prologue)
          - title           : section heading from the source
          - body            : narrative text from the section, lightly cleaned (preserve technical content)
          - key_points      : 3-8 bullet points capturing the most important takeaways
          - equations       : array of {{id, description, implemented_in}} objects for each equation
                              referenced in the section. Use the source's equation id (e.g., "Eq. 5-12").
                              Set implemented_in to null — it will be filled in by post-processing.
          - figures         : array of strings like "Figure 5-3: caption"
          - tables          : array of strings like "Table 5-2: caption"
          - applicability   : one sentence describing when this section applies

        EXTRACTION RULES

        1. Walk the chapter top-to-bottom. Create one section object per numbered section
           in the source. Do NOT skip sections, even short ones.
        2. Section IDs must match the source numbering exactly. If the source has section
           5.7.2.3, the section_id is "5.7.2.3".
        3. The body should be the actual text from the section, NOT a summary. You may
           remove page headers/footers and obvious OCR artifacts, but preserve all
           technical content. Plain text only — no markdown, no LaTeX.
        4. Equations appearing in the source go into the `equations` array. Use the
           source's equation label as the `id`. The `description` should be a brief
           plain-language description of what the equation computes (NOT a re-derivation
           or restatement of the formula).
        5. If a section has no equations/figures/tables, use an empty array — never null.
        6. The `applicability` field is the most important field for the audit checker.
           Make it specific (e.g., "Saturated, normally consolidated clays under
           one-dimensional loading"), not generic ("Used in geotechnical design").
        7. Output JSON ONLY. No prose before or after. No markdown code fences.

        ===== BEGIN CHAPTER TEXT =====

        {chapter_text}

        ===== END CHAPTER TEXT =====

        Return the JSON object now.
    """).strip()


def call_claude(system: str, user: str, model: str) -> str:
    """Call Claude via the anthropic SDK and return the text response.

    Requires ANTHROPIC_API_KEY in env.
    """
    try:
        import anthropic
    except ImportError:
        sys.exit(
            "anthropic SDK is required for `extract`. Install with:\n"
            "  pip install anthropic"
        )
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=16_000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(
        block.text for block in resp.content if getattr(block, "type", "") == "text"
    )
    return text.strip()


def parse_llm_json(raw: str) -> dict:
    """Extract and parse a JSON object from an LLM response, tolerating fences."""
    text = raw.strip()
    if text.startswith("```"):
        # strip ```json ... ``` fences
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try to find the first { and last } and reparse
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            return json.loads(text[first : last + 1])
        raise RuntimeError(f"LLM did not return valid JSON: {e}\n\n{text[:500]}")


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def validate_against_schema(chapter_json: dict) -> list[str]:
    """Lightweight in-process validation. Returns a list of error messages.

    Avoids the jsonschema dep so the script runs with stdlib only.
    """
    errors: list[str] = []
    required_top = ["reference_id", "reference_title", "chapter", "chapter_title", "sections"]
    for k in required_top:
        if k not in chapter_json:
            errors.append(f"missing top-level key: {k}")
    sections = chapter_json.get("sections", [])
    if not isinstance(sections, list) or not sections:
        errors.append("sections must be a non-empty array")
        return errors
    for i, sec in enumerate(sections):
        loc = f"sections[{i}]"
        if not isinstance(sec, dict):
            errors.append(f"{loc}: not an object")
            continue
        for k in (
            "section_id",
            "title",
            "body",
            "key_points",
            "equations",
            "figures",
            "tables",
            "applicability",
        ):
            if k not in sec:
                errors.append(f"{loc}: missing key '{k}'")
        sid = sec.get("section_id", "")
        if sid and not re.match(r"^[0-9P]+(\.[0-9]+)*$", sid):
            errors.append(f"{loc}: section_id '{sid}' has invalid format")
        if isinstance(sec.get("body"), str) and len(sec["body"]) < 100:
            errors.append(f"{loc}: body is shorter than 100 chars (likely placeholder)")
        kp = sec.get("key_points")
        if isinstance(kp, list):
            if not (1 <= len(kp) <= 12):
                errors.append(f"{loc}: key_points has {len(kp)} items (expected 1-12)")
            for j, p in enumerate(kp):
                if not isinstance(p, str) or len(p) > 300:
                    errors.append(f"{loc}.key_points[{j}]: invalid")
    return errors


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_discover(manifest_path: Path) -> int:
    print(f"Discovering chapter ranges from {manifest_path.name}...")
    manifest = Manifest.load(manifest_path)
    print(f"  PDF: {manifest.pdf_path}")
    manifest = discover_chapter_ranges(manifest)
    manifest.save(manifest_path)
    print(f"\nManifest updated: {manifest_path}")
    print("Review the page ranges above; fill in any NOT FOUND entries by hand.")
    return 0


def cmd_extract(
    manifest_path: Path,
    chapter_filter: list[int] | None,
    dry_run: bool,
    model: str,
) -> int:
    manifest = Manifest.load(manifest_path)
    output_dir = PACKAGE_DIR / manifest.package / "text"
    output_dir.mkdir(parents=True, exist_ok=True)

    chapters_to_run = manifest.chapters
    if chapter_filter:
        chapters_to_run = [ch for ch in chapters_to_run if ch.number in chapter_filter]

    if not chapters_to_run:
        sys.exit(f"No chapters matched filter {chapter_filter}")

    print(f"Reference: {manifest.reference_title}")
    print(f"Output dir: {output_dir}")
    print(f"Chapters to extract: {[ch.number for ch in chapters_to_run]}")
    print(f"Mode: {'DRY RUN (no LLM calls)' if dry_run else f'LIVE (model={model})'}")
    print()

    failures: list[tuple[ChapterSpec, str]] = []

    for ch in chapters_to_run:
        print(f"--- Chapter {ch.number}: {ch.title} ---")
        try:
            text = extract_chapter_text(manifest, ch)
            print(f"  source text: {len(text):,} chars")
            prompt = build_extraction_prompt(manifest, ch, text)
            print(f"  prompt: {len(prompt):,} chars")

            if dry_run:
                print("  [dry run — skipping LLM call]")
                continue

            t0 = time.time()
            raw = call_claude(EXTRACTION_SYSTEM_PROMPT, prompt, model)
            elapsed = time.time() - t0
            print(f"  LLM call: {elapsed:.1f}s, {len(raw):,} chars returned")

            chapter_json = parse_llm_json(raw)

            # Inject equation cross-references
            eq_index = build_equation_index(ch.equation_module)
            chapter_json = inject_equation_links(chapter_json, eq_index)
            print(f"  equation index: {len(eq_index)} entries")

            # Validate
            errs = validate_against_schema(chapter_json)
            if errs:
                print(f"  VALIDATION FAILED ({len(errs)} errors):")
                for e in errs[:10]:
                    print(f"    - {e}")
                if len(errs) > 10:
                    print(f"    ... and {len(errs) - 10} more")
                failures.append((ch, "schema validation"))
                # Save the raw output to a .draft file for inspection
                draft_path = output_dir / f"{ch.output_name}.draft"
                with open(draft_path, "w", encoding="utf-8") as f:
                    json.dump(chapter_json, f, indent=2, ensure_ascii=False)
                print(f"  draft saved: {draft_path}")
                continue

            output_path = output_dir / ch.output_name
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(chapter_json, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"  WRITTEN: {output_path}")

        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}", file=sys.stderr)
            failures.append((ch, str(e)))

    print()
    print(f"Done. {len(chapters_to_run) - len(failures)} succeeded, "
          f"{len(failures)} failed.")
    if failures:
        for ch, reason in failures:
            print(f"  ch {ch.number}: {reason}")
        return 1
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_disc = sub.add_parser("discover", help="Discover chapter page ranges from PDF outline")
    p_disc.add_argument("manifest", type=Path)

    p_ext = sub.add_parser("extract", help="Extract chapter JSON from PDF")
    p_ext.add_argument("manifest", type=Path)
    p_ext.add_argument(
        "--chapters",
        type=lambda s: [int(x) for x in s.split(",")],
        default=None,
        help="Comma-separated chapter numbers to extract (default: all)",
    )
    p_ext.add_argument("--dry-run", action="store_true", help="Skip LLM calls")
    p_ext.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")

    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    if not manifest_path.exists():
        sys.exit(f"Manifest not found: {manifest_path}")

    if args.command == "discover":
        return cmd_discover(manifest_path)
    elif args.command == "extract":
        return cmd_extract(
            manifest_path=manifest_path,
            chapter_filter=args.chapters,
            dry_run=args.dry_run,
            model=args.model,
        )
    else:
        parser.error(f"unknown command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
