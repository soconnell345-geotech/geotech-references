#!/usr/bin/env python3
"""
build_chapter_text.py — Section-level, parallel, tool_use-structured extraction
pipeline from PDF to chapter JSON.

Architecture
------------
1. Read a reference's manifest (chapter page ranges, PDF path).
2. For each chapter, walk the PDF outline to discover its top-level sections
   (e.g., 4-1, 4-2, 4-3). Each top-level section becomes one extraction chunk.
3. For each chunk: pull the text via PyMuPDF, call Claude Sonnet with a
   forced tool_use call that returns a list of section/subsection dicts
   conforming to the chapter schema.
4. Merge the per-chunk section lists back into one chapter JSON and
   post-process equation cross-references against the digitized
   geotech_references equation module.
5. Validate against the schema; write chapterNN.json.

The extraction loop uses concurrent.futures.ThreadPoolExecutor so multiple
section chunks run in parallel, bounded by --parallel (default 8).

Output JSONs go to geotech_references/<package>/text/chapterNN.json and are
consumed automatically by the _retrieval.py / _retrieval_db.py layer.

Usage
-----
    # Discover chapter page ranges from the PDF outline.
    python build_chapter_text.py discover scripts/manifests/dm7_1.json

    # Dry-run: split a single chapter into section chunks and print stats
    # without calling the LLM.
    python build_chapter_text.py extract scripts/manifests/dm7_1.json \
        --chapters 4 --dry-run

    # Extract one chapter (section-parallel).
    python build_chapter_text.py extract scripts/manifests/dm7_1.json \
        --chapters 4

    # Extract everything.
    python build_chapter_text.py extract scripts/manifests/dm7_1.json \
        --parallel 8

Environment
-----------
    ANTHROPIC_API_KEY      required for `extract`
    CHAPTER_TEXT_MODEL     default: claude-sonnet-4-6
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib
import inspect
import json
import os
import re
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths and defaults
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
PACKAGE_DIR = REPO_DIR / "geotech_references"

DEFAULT_MODEL_ANTHROPIC = os.environ.get("CHAPTER_TEXT_MODEL", "claude-sonnet-4-6")
DEFAULT_MODEL_OPENAI = os.environ.get("CHAPTER_TEXT_MODEL_OPENAI", "gpt-4.1")
DEFAULT_PARALLEL = 4
# Maximum chunk size before we recursively subdivide using deeper outline
# levels. Empirically, chunks much larger than ~50k chars / ~20 pages cause
# the model to silently emit empty section arrays under tool_use forcing.
MAX_CHUNK_CHARS = 35_000
MAX_CHUNK_PAGES = 15


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

@dataclass
class ChapterSpec:
    number: int
    title: str
    page_start: int | None
    page_end: int | None
    equation_module: str | None
    filename: str | None = None

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
# PyMuPDF helpers
# ---------------------------------------------------------------------------

def _fitz():
    try:
        import fitz
        return fitz
    except ImportError:
        sys.exit("PyMuPDF required: pip install PyMuPDF")


def discover_chapter_ranges(manifest: Manifest) -> Manifest:
    """Fill chapter page_start/page_end from PDF outline (level 1-2 entries)."""
    fitz = _fitz()
    if not manifest.pdf_path.exists():
        sys.exit(f"PDF not found: {manifest.pdf_path}")
    doc = fitz.open(manifest.pdf_path)
    try:
        toc = doc.get_toc(simple=True)
        n_pages = doc.page_count
    finally:
        doc.close()
    if not toc:
        print("WARNING: PDF has no outline; fill manifest by hand.", file=sys.stderr)
        return manifest
    entries = [(t.strip(), p) for lvl, t, p in toc if lvl <= 2]
    matched: list[tuple[ChapterSpec, int]] = []
    for ch in manifest.chapters:
        page = _match_in_toc(ch, entries)
        if page is not None:
            matched.append((ch, page))
    matched.sort(key=lambda mc: mc[1])
    for i, (ch, page) in enumerate(matched):
        ch.page_start = page
        ch.page_end = matched[i + 1][1] - 1 if i + 1 < len(matched) else n_pages
        print(f"  ch {ch.number}: pp. {ch.page_start}-{ch.page_end} ({ch.title})")
    for ch in manifest.chapters:
        if ch.page_start is None:
            print(f"  ch {ch.number}: NOT FOUND ({ch.title})", file=sys.stderr)
    return manifest


def _match_in_toc(ch: ChapterSpec, entries: list[tuple[str, int]]) -> int | None:
    title_words = set(re.findall(r"[a-z]+", ch.title.lower()))
    if ch.filename == "prologue":
        for t, p in entries:
            if "prologue" in t.lower() or "preface" in t.lower():
                return p
        return None
    chap_pat = re.compile(rf"\bchapter\s*0*{ch.number}\b", re.IGNORECASE)
    best_score = 0
    best_page = None
    for t, p in entries:
        score = 0
        if chap_pat.search(t.lower()):
            score += 5
        common = title_words & set(re.findall(r"[a-z]+", t.lower()))
        score += len(common)
        if score > best_score:
            best_score = score
            best_page = p
    return best_page if best_score >= 3 else None


# ---------------------------------------------------------------------------
# Section-level chunk discovery
# ---------------------------------------------------------------------------

@dataclass
class SectionChunk:
    """One top-level section of a chapter, destined for a single LLM call."""
    chapter_num: int
    chunk_label: str      # e.g. "4-1", "4-2"
    chunk_title: str      # e.g. "Introduction", "Stress Conditions at a Point"
    page_start: int       # 1-indexed
    page_end: int
    text: str             # pulled from PDF


def discover_chunks(manifest: Manifest, ch: ChapterSpec) -> list[SectionChunk]:
    """Walk the PDF outline inside a chapter's page range to find section
    boundaries, recursively subdividing any chunk that exceeds size limits.
    """
    if ch.page_start is None or ch.page_end is None:
        sys.exit(f"Chapter {ch.number} missing page range; run `discover` first.")

    fitz = _fitz()
    doc = fitz.open(manifest.pdf_path)
    try:
        toc = doc.get_toc(simple=True)
        chunks = _split_range(
            doc, toc, ch, ch.page_start, ch.page_end, min_level=2
        )
        if not chunks:
            text = _pull_pages(doc, ch.page_start, ch.page_end)
            chunks = [SectionChunk(
                chapter_num=ch.number, chunk_label=_filename_label(ch),
                chunk_title=ch.title, page_start=ch.page_start,
                page_end=ch.page_end, text=text,
            )]
        return chunks
    finally:
        doc.close()


def _split_range(
    doc, toc, ch: ChapterSpec, page_start: int, page_end: int, min_level: int
) -> list[SectionChunk]:
    """Split a page range using outline entries at `min_level`. Recursively
    subdivides any resulting chunk that exceeds size limits using deeper
    levels (min_level + 1)."""
    inside = [
        (lvl, title.strip(), page)
        for lvl, title, page in toc
        if page_start <= page <= page_end and lvl >= min_level
    ]
    if not inside:
        text = _pull_pages(doc, page_start, page_end)
        return [SectionChunk(
            chapter_num=ch.number,
            chunk_label=f"{ch.number}_p{page_start}-{page_end}",
            chunk_title=f"{ch.title} (pp. {page_start}-{page_end})",
            page_start=page_start, page_end=page_end, text=text,
        )]

    chunk_level = min(lvl for lvl, _, _ in inside)
    starts = [(title, page) for lvl, title, page in inside if lvl == chunk_level]

    # Group consecutive entries that share a start page (e.g., 4-1 and 4-2
    # both at p 211) into a single chunk.
    groups: list[list[tuple[str, int]]] = []
    for entry in starts:
        if groups and groups[-1][-1][1] == entry[1]:
            groups[-1].append(entry)
        else:
            groups.append([entry])

    raw_chunks: list[SectionChunk] = []
    for i, group in enumerate(groups):
        gs_page = group[0][1]
        if i + 1 < len(groups):
            ge_page = groups[i + 1][0][1] - 1
        else:
            ge_page = page_end
        gs_page = max(gs_page, page_start)
        ge_page = min(ge_page, page_end)
        if gs_page > ge_page:
            continue
        labels = [_extract_section_label(t, ch.number) for t, _ in group]
        titles = [t for t, _ in group]
        label = "+".join(labels)
        title = " | ".join(titles)
        text = _pull_pages(doc, gs_page, ge_page)
        raw_chunks.append(SectionChunk(
            chapter_num=ch.number,
            chunk_label=label,
            chunk_title=title,
            page_start=gs_page,
            page_end=ge_page,
            text=text,
        ))

    # Subdivide any oversized chunks using the next deeper outline level.
    final_chunks: list[SectionChunk] = []
    for c in raw_chunks:
        n_pages = c.page_end - c.page_start + 1
        if (len(c.text) > MAX_CHUNK_CHARS or n_pages > MAX_CHUNK_PAGES) and chunk_level < 5:
            sub = _split_range(
                doc, toc, ch, c.page_start, c.page_end,
                min_level=chunk_level + 1,
            )
            # Sub-splits inherit a label prefix from the parent for clarity
            for s in sub:
                s.chunk_label = f"{c.chunk_label}>{s.chunk_label}"
            # If subdivision didn't actually split (one big subsection),
            # keep the original — no point in re-running an identical chunk.
            if len(sub) > 1:
                final_chunks.extend(sub)
            else:
                final_chunks.append(c)
        else:
            final_chunks.append(c)
    return final_chunks


def _pull_pages(doc, start: int, end: int) -> str:
    pages = []
    for i in range(start - 1, end):
        pages.append(f"\n\n[PAGE {i + 1}]\n\n{doc[i].get_text()}")
    return "".join(pages).strip()


def _extract_section_label(title: str, chapter_num: int) -> str:
    """Try to extract '4-1' / '4.1' style label from a TOC entry."""
    # Match patterns like "4-1 Introduction" or "4.1 Scope"
    m = re.match(r"^\s*(\d+[-.]\d+(?:\.\d+)*)\b", title)
    if m:
        return m.group(1)
    # Fallback: use chapter number + title slug
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower())[:40]
    return f"{chapter_num}_{slug}"


def _filename_label(ch: ChapterSpec) -> str:
    return ch.filename or f"chapter{ch.number}"


# ---------------------------------------------------------------------------
# Tool schema — the model is FORCED to emit a list of sections via tool_use
# ---------------------------------------------------------------------------

SECTION_SCHEMA = {
    "type": "object",
    "required": [
        "section_id", "title", "summary", "body", "key_points",
        "equations", "figures", "tables", "applicability",
    ],
    "properties": {
        "section_id": {
            "type": "string",
            "description": "Hierarchical section id matching the source exactly. UFC uses hyphen-then-dot form (4-1, 4-2.1, 4-2.1.3). Prologue sections use P-1, P-2, etc.",
        },
        "title": {"type": "string"},
        "summary": {
            "type": "string",
            "description": "300-500 characters. A tight summary of this section's content, suitable as a search hit preview. Do NOT just repeat the title — explain what the section covers and why it matters.",
        },
        "body": {
            "type": "string",
            "description": "The section's actual narrative text, lightly cleaned. Preserve technical content. Plain text only. Empty string allowed if the section is purely a container for subsections.",
        },
        "key_points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-8 concise bullet points capturing the most important takeaways. Each <= 300 chars.",
        },
        "equations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "description"],
                "properties": {
                    "id": {"type": "string", "description": "Equation label from the source, e.g. 'Eq. 5-12'."},
                    "description": {"type": "string"},
                    "implemented_in": {"type": ["string", "null"]},
                },
            },
        },
        "figures": {"type": "array", "items": {"type": "string"}},
        "tables": {"type": "array", "items": {"type": "string"}},
        "applicability": {
            "type": "string",
            "description": "One sentence describing when this section applies. Be specific.",
        },
    },
}

EMIT_TOOL = {
    "name": "emit_sections",
    "description": (
        "Emit the structured sections extracted from this chunk of chapter "
        "text. Call this tool exactly once with a list of all sections found "
        "in the chunk, in document order."
    ),
    "input_schema": {
        "type": "object",
        "required": ["sections"],
        "properties": {
            "sections": {
                "type": "array",
                "items": SECTION_SCHEMA,
            },
        },
    },
}

EXTRACTION_SYSTEM_PROMPT = """\
You are a technical document extraction assistant. Convert raw PDF text from \
a geotechnical engineering reference into structured sections by calling the \
emit_sections tool. Preserve the source content faithfully — no \
paraphrasing of technical material, no skipped sections, no editorial \
commentary. You are organizing content into a navigable structure, not \
rewriting it."""

# OpenAI-compatible tool format (same schema, different wrapper).
EMIT_TOOL_OPENAI = {
    "type": "function",
    "function": {
        "name": EMIT_TOOL["name"],
        "description": EMIT_TOOL["description"],
        "parameters": EMIT_TOOL["input_schema"],
    },
}


def build_user_prompt(manifest: Manifest, chunk: SectionChunk) -> str:
    vol = manifest.volume if manifest.volume is not None else "N/A"
    return f"""\
Reference: {manifest.reference_id} ({manifest.reference_title})
Volume: {vol}
Chapter: {chunk.chapter_num}
Chunk: {chunk.chunk_label} — {chunk.chunk_title}
Pages: {chunk.page_start}-{chunk.page_end}

Walk this chunk top-to-bottom. Create one section object per numbered \
section in the source. Container sections (e.g. "4-2 Stress Conditions at \
a Point" whose children are 4-2.1, 4-2.2, ...) should still get their own \
object, but can have an empty body if all their content is in the \
subsections below them.

Use the SOURCE section ids exactly (e.g. "4-2.1.1"). Do not invent ids, do \
not renumber. If the source uses "4-1" format, keep it; do not convert to \
"4.1".

Summaries must be 300-500 chars and describe what the section covers \
SPECIFICALLY — don't just restate the title. The summary is what a search \
result card will show an engineer.

Key points: 3-8 bullets, each <= 300 chars. Crisp technical takeaways.

Equations: include every NUMBERED equation that appears in the source. \
UFC documents use several conventions — treat ALL of these as equations:

  1. Prose labels: "Equation 5-12" or "Eq. 5-12" introduces the formula
  2. Bare parenthesized trailing labels: the formula appears, and then on \
the same or next line a label like "(3-1)" or "(5-12)" marks it
  3. Equation-number-then-colon format: "3-1  Relative compaction: ..."

ALL three forms are numbered equations that must be extracted. Use the \
canonical form "Eq. X-Y" as the id in your output, regardless of how the \
source formats it. Set implemented_in to null — it will be populated by \
post-processing.

IMPORTANT — equations vs tables: entries like "Table 4-2" or "Table 5-3" \
are TABLES, not equations, even when they contain formulas or coefficient \
values. Put tables in the `tables` array. Do NOT put "Table X-Y" strings \
in the `equations` array.

Be exhaustive: if a section contains formulas labeled (3-1), (3-2), ..., \
(3-5), all five must appear in the output. Every numbered equation the \
source references must make it into some section's equations array. A \
section may contain multiple equations; a single equation may appear in \
multiple sections if cited from more than one place.

Return by calling emit_sections ONCE with the full section list for this \
chunk.

===== BEGIN CHUNK TEXT =====

{chunk.text}

===== END CHUNK TEXT ====="""


# ---------------------------------------------------------------------------
# LLM backends — pluggable via --provider flag
# ---------------------------------------------------------------------------

class _Backend:
    """Abstract base: call the LLM, return the raw sections list."""
    model: str

    def call(self, system: str, user: str) -> list[dict]:
        raise NotImplementedError


class _AnthropicBackend(_Backend):
    """Anthropic SDK backend (default). Requires ANTHROPIC_API_KEY."""

    def __init__(self, model: str):
        self.model = model
        self._lock = threading.Lock()
        self._client: Any = None

    def _get_client(self):
        with self._lock:
            if self._client is None:
                try:
                    import anthropic
                except ImportError:
                    sys.exit("anthropic SDK required: pip install anthropic")
                self._client = anthropic.Anthropic()
        return self._client

    def call(self, system: str, user: str) -> list[dict]:
        client = self._get_client()
        resp = client.messages.create(
            model=self.model,
            max_tokens=16_000,
            system=system,
            tools=[EMIT_TOOL],
            tool_choice={"type": "tool", "name": "emit_sections"},
            messages=[{"role": "user", "content": user}],
        )
        tool_block = None
        for block in resp.content:
            if getattr(block, "type", "") == "tool_use" and block.name == "emit_sections":
                tool_block = block
                break
        if tool_block is None:
            raise RuntimeError("model did not return an emit_sections tool_use block")
        raw = tool_block.input.get("sections", [])
        if not isinstance(raw, list):
            raise RuntimeError(
                f"emit_sections returned sections as {type(raw).__name__}, not list"
            )
        return raw


class _OpenAIBackend(_Backend):
    """OpenAI-compatible backend. Works with OpenAI, Azure OpenAI, Foundry
    AIP, or any endpoint that speaks the OpenAI chat completions API.

    Set OPENAI_API_KEY (or pass --api-key) and, for non-OpenAI endpoints,
    --base-url pointing at the provider's completions endpoint.

    Foundry example:
        --provider openai \\
        --base-url https://<stack>.palantirfoundry.com/api/v2/aip/openai \\
        --model gpt-4.1 \\
        --api-key <your-foundry-token>
    """

    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        self.model = model
        self._base_url = base_url
        self._api_key = api_key
        self._lock = threading.Lock()
        self._client: Any = None

    def _get_client(self):
        with self._lock:
            if self._client is None:
                try:
                    import openai
                except ImportError:
                    sys.exit("openai SDK required: pip install openai")
                kwargs: dict = {}
                if self._base_url:
                    kwargs["base_url"] = self._base_url
                if self._api_key:
                    kwargs["api_key"] = self._api_key
                self._client = openai.OpenAI(**kwargs)
        return self._client

    def call(self, system: str, user: str) -> list[dict]:
        client = self._get_client()
        resp = client.chat.completions.create(
            model=self.model,
            max_tokens=16_000,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            tools=[EMIT_TOOL_OPENAI],
            tool_choice={"type": "function", "function": {"name": "emit_sections"}},
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            raise RuntimeError("model did not return a tool call for emit_sections")
        tc = next(
            (t for t in msg.tool_calls if t.function.name == "emit_sections"),
            None,
        )
        if tc is None:
            raise RuntimeError("model did not call emit_sections")
        raw = json.loads(tc.function.arguments).get("sections", [])
        if not isinstance(raw, list):
            raise RuntimeError(
                f"emit_sections returned sections as {type(raw).__name__}, not list"
            )
        return raw


def extract_chunk_sections(
    manifest: Manifest, chunk: SectionChunk, backend: _Backend
) -> list[dict]:
    """Call the LLM backend, retry on overload + empty-result.

    Treats three failures equivalently as transient and retries with
    jittered exponential backoff:
      - exception from the SDK (network, 5xx, overload, rate limit)
      - tool call missing entirely from the response
      - backend returns 0 sections from a chunk with substantive input text
        (>5k chars) — some models silently emit an empty array under load
    """
    import random
    user = build_user_prompt(manifest, chunk)
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            raw = backend.call(EXTRACTION_SYSTEM_PROMPT, user)
            valid = [s for s in raw if isinstance(s, dict)]
            if len(valid) != len(raw):
                dump_dir = PACKAGE_DIR / "_build_debug"
                dump_dir.mkdir(exist_ok=True)
                safe = re.sub(r"[^A-Za-z0-9._-]+", "_", chunk.chunk_label)
                with open(dump_dir / f"{safe}.raw.json", "w", encoding="utf-8") as f:
                    json.dump(raw, f, indent=2, default=str)
                print(f"    WARNING [{chunk.chunk_label}]: dropped {len(raw) - len(valid)} non-dict items")
            # Soft failure: empty result from a substantive chunk = retry
            if not valid and len(chunk.text) > 5000:
                raise RuntimeError(
                    f"empty sections from a {len(chunk.text)}-char chunk "
                    f"(likely overload / silent truncation)"
                )
            return valid
        except Exception as e:
            last_error = e
            if attempt < 4:
                # Jittered exponential backoff: 2, 4, 8, 16 seconds plus random 0-3s
                sleep = (2 ** (attempt + 1)) + random.uniform(0, 3)
                print(f"    [{chunk.chunk_label}] retry {attempt+1}/4 after {sleep:.1f}s ({type(e).__name__}: {str(e)[:80]})")
                time.sleep(sleep)
                continue
            raise
    raise last_error  # unreachable


# ---------------------------------------------------------------------------
# Equation cross-reference resolution
# ---------------------------------------------------------------------------

_EQ_NUM_PAT = re.compile(
    r"Eq(?:uation|\.)?\s*([0-9]+[-\u2013][0-9]+[a-z]?)", re.IGNORECASE
)


def _norm_eq(raw: str) -> str:
    m = _EQ_NUM_PAT.search(raw)
    return (m.group(1) if m else raw).replace("\u2013", "-").strip()


def build_equation_index(equation_module: str | None) -> dict[str, str]:
    if not equation_module:
        return {}
    try:
        mod = importlib.import_module(equation_module)
    except ImportError:
        return {}
    index: dict[str, str] = {}
    for name, func in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith("_") or getattr(func, "__module__", "") != mod.__name__:
            continue
        doc = inspect.getdoc(func) or ""
        for m in _EQ_NUM_PAT.finditer(doc):
            eid = m.group(1).replace("\u2013", "-")
            index.setdefault(eid, f"{equation_module}.{name}")
    return index


def inject_links(sections: list[dict], eq_index: dict[str, str]) -> None:
    if not eq_index:
        return
    for sec in sections:
        for eq in sec.get("equations", []):
            if isinstance(eq, dict) and not eq.get("implemented_in") and eq.get("id"):
                nid = _norm_eq(eq["id"])
                if nid in eq_index:
                    eq["implemented_in"] = eq_index[nid]


_PAREN_EQ_PAT = re.compile(
    r"\(([0-9]+[-\u2013][0-9]+(?:[-\u2013][0-9]+)?[a-z]?)\)"
)


def force_inject_chunk_eqs(
    sections: list[dict], chunk_text: str, eq_index: dict[str, str]
) -> None:
    """Safety net: scan chunk text for parenthesized eq labels (e.g. `(3-5)`)
    and force-inject any that the model failed to tag into the largest
    section's equations array. inject_links will then resolve them."""
    if not eq_index or not sections:
        return
    found_in_text: set[str] = set()
    for m in _PAREN_EQ_PAT.finditer(chunk_text):
        raw = m.group(1).replace("\u2013", "-")
        # Try full label, then trailing two-part form (e.g. 5-5-19 → 5-19)
        candidates = [raw]
        parts = raw.split("-")
        if len(parts) >= 3:
            candidates.append("-".join(parts[-2:]))
        for nid in candidates:
            if nid in eq_index:
                found_in_text.add(nid)
                break
    if not found_in_text:
        return
    already_tagged: set[str] = set()
    for sec in sections:
        for eq in sec.get("equations", []):
            if isinstance(eq, dict) and eq.get("id"):
                already_tagged.add(_norm_eq(eq["id"]))
    missing = found_in_text - already_tagged
    if not missing:
        return
    target = max(sections, key=lambda s: len(s.get("body", "")))
    target.setdefault("equations", [])
    for nid in sorted(missing):
        target["equations"].append({
            "id": f"Eq. {nid}",
            "description": "(force-injected from source text)",
            "implemented_in": eq_index[nid],
        })


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def _is_container(sid: str, sections: list, index: int) -> bool:
    if not sid:
        return False
    for j in range(index + 1, len(sections)):
        s = sections[j]
        if not isinstance(s, dict):
            continue
        oid = s.get("section_id", "")
        if oid.startswith(sid + ".") or oid.startswith(sid + "-"):
            return True
    return False


def validate_chapter(chapter_json: dict) -> list[str]:
    errors: list[str] = []
    for k in ("reference_id", "reference_title", "chapter", "chapter_title", "sections"):
        if k not in chapter_json:
            errors.append(f"missing top-level key: {k}")
    sections = chapter_json.get("sections", [])
    if not isinstance(sections, list) or not sections:
        errors.append("sections must be non-empty")
        return errors
    seen: dict[str, int] = {}
    for i, sec in enumerate(sections):
        loc = f"sections[{i}]"
        if not isinstance(sec, dict):
            errors.append(f"{loc}: not an object")
            continue
        for k in ("section_id", "title", "summary", "body", "key_points",
                  "equations", "figures", "tables", "applicability"):
            if k not in sec:
                errors.append(f"{loc}: missing '{k}'")
        sid = sec.get("section_id", "")
        if sid:
            seen[sid] = seen.get(sid, 0) + 1
            if not re.match(r"^[0-9P]+([-.][0-9]+)*$", sid):
                errors.append(f"{loc}: invalid section_id '{sid}'")
        summary = sec.get("summary", "")
        if isinstance(summary, str):
            if len(summary) < 50:
                errors.append(f"{loc} ({sid}): summary < 50 chars")
            if len(summary) > 700:
                errors.append(f"{loc} ({sid}): summary > 700 chars")
        body = sec.get("body", "")
        kp_list = sec.get("key_points", []) if isinstance(sec.get("key_points"), list) else []
        has_substance = (
            _is_container(sid, sections, i)
            or (len(sec.get("summary", "")) >= 100 and len(kp_list) >= 2)
        )
        if isinstance(body, str) and len(body) < 100 and not has_substance:
            errors.append(f"{loc} ({sid}): body < 100 chars with no summary/key_points backup")
        kp = sec.get("key_points", [])
        if isinstance(kp, list):
            if not (1 <= len(kp) <= 12):
                errors.append(f"{loc} ({sid}): key_points has {len(kp)} items")
            for j, p in enumerate(kp):
                if not isinstance(p, str) or len(p) > 300:
                    errors.append(f"{loc} ({sid}).key_points[{j}] invalid")
    dups = [s for s, n in seen.items() if n > 1]
    if dups:
        errors.append(f"duplicate section_ids: {dups}")
    return errors


# ---------------------------------------------------------------------------
# Extraction driver
# ---------------------------------------------------------------------------

def extract_chapter(
    manifest: Manifest,
    ch: ChapterSpec,
    backend: _Backend,
    parallel: int,
    dry_run: bool,
    chunk_label_filter: list[str] | None = None,
    existing_chapter: dict | None = None,
) -> tuple[dict | None, list[str]]:
    """Extract one chapter in parallel across its section chunks.

    Returns (chapter_json, errors). chapter_json is None if extraction
    failed before validation.

    If chunk_label_filter is set, only chunks whose label contains any of
    the given substrings are extracted, and results are merged into
    `existing_chapter` (which must be supplied).
    """
    chunks = discover_chunks(manifest, ch)
    print(f"  chunks: {len(chunks)}")
    for c in chunks:
        print(f"    {c.chunk_label} ({c.page_end - c.page_start + 1} pp, "
              f"{len(c.text):,} chars): {c.chunk_title}")

    if chunk_label_filter:
        keep = [
            c for c in chunks
            if any(pat in c.chunk_label for pat in chunk_label_filter)
        ]
        if not keep:
            print(f"  no chunks matched labels {chunk_label_filter}")
            return None, [f"no chunks matched {chunk_label_filter}"]
        print(f"  filtered to {len(keep)} chunk(s): "
              f"{[c.chunk_label for c in keep]}")
        chunks = keep

    if dry_run:
        return None, []

    # Parallel extract
    results: dict[int, list[dict]] = {}
    errors: list[str] = []
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=parallel) as ex:
        futures = {
            ex.submit(extract_chunk_sections, manifest, c, backend): i
            for i, c in enumerate(chunks)
        }
        for fut in cf.as_completed(futures):
            idx = futures[fut]
            chunk = chunks[idx]
            try:
                secs = fut.result()
                results[idx] = secs
                print(f"    [{chunk.chunk_label}] OK — {len(secs)} sections")
            except Exception as e:
                print(f"    [{chunk.chunk_label}] FAIL — {type(e).__name__}: {e}")
                errors.append(f"chunk {chunk.chunk_label}: {e}")
                results[idx] = []
    elapsed = time.time() - t0
    print(f"  chapter elapsed: {elapsed:.1f}s")

    # Per-chunk safety net: scan source text for parenthesized eq labels
    # the model may have missed and force-inject them.
    eq_index_for_inject = build_equation_index(ch.equation_module)
    for i, c in enumerate(chunks):
        force_inject_chunk_eqs(results.get(i, []), c.text, eq_index_for_inject)

    # Merge in chunk order. Deduplicate on section_id — if the same id
    # appears twice (occasional model repetition within a large chunk),
    # keep whichever copy has the longer body. When merging into an
    # existing chapter, seed `merged` with its sections so newly-extracted
    # ids replace stale copies and unaffected sections are preserved.
    merged: list[dict] = []
    seen: dict[str, int] = {}
    if chunk_label_filter and existing_chapter:
        for sec in existing_chapter.get("sections", []):
            sid = sec.get("section_id") if isinstance(sec, dict) else None
            if sid:
                seen[sid] = len(merged)
            merged.append(sec)
    for i in range(len(chunks)):
        for sec in results.get(i, []):
            sid = sec.get("section_id") if isinstance(sec, dict) else None
            if not sid:
                merged.append(sec)
                continue
            if sid in seen:
                prev_idx = seen[sid]
                prev = merged[prev_idx]
                # In spot-fix mode, new extraction always wins over the
                # existing chapter copy (we're fixing gaps).
                if chunk_label_filter and existing_chapter:
                    merged[prev_idx] = sec
                elif len(sec.get("body", "")) > len(prev.get("body", "")):
                    merged[prev_idx] = sec
                continue
            seen[sid] = len(merged)
            merged.append(sec)

    # Inject equation cross-references
    eq_index = build_equation_index(ch.equation_module)
    inject_links(merged, eq_index)
    print(f"  equation index: {len(eq_index)} entries")
    print(f"  merged sections: {len(merged)}")

    chapter_json = {
        "reference_id": manifest.reference_id,
        "reference_title": manifest.reference_title,
        "volume": manifest.volume,
        "chapter": ch.number,
        "chapter_title": ch.title,
        "sections": merged,
    }
    verrs = validate_chapter(chapter_json)
    errors.extend(verrs)
    return chapter_json, errors


def cmd_extract(
    manifest_path: Path,
    chapter_filter: list[int] | None,
    dry_run: bool,
    backend: _Backend,
    parallel: int,
    chunk_label_filter: list[str] | None = None,
) -> int:
    manifest = Manifest.load(manifest_path)
    output_dir = PACKAGE_DIR / manifest.package / "text"
    output_dir.mkdir(parents=True, exist_ok=True)

    to_run = manifest.chapters
    if chapter_filter:
        to_run = [c for c in to_run if c.number in chapter_filter]
    if not to_run:
        sys.exit(f"no chapters matched filter {chapter_filter}")

    provider = "openai" if isinstance(backend, _OpenAIBackend) else "anthropic"
    print(f"Reference: {manifest.reference_title}")
    print(f"Output: {output_dir}")
    print(f"Chapters: {[c.number for c in to_run]}")
    print(f"Mode: {'DRY RUN' if dry_run else f'LIVE (provider={provider}, model={backend.model}, parallel={parallel})'}")
    print()

    total_errors = 0
    for ch in to_run:
        print(f"--- Chapter {ch.number}: {ch.title} ---")
        existing = None
        if chunk_label_filter:
            existing_path = output_dir / ch.output_name
            if existing_path.exists():
                with open(existing_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                print(f"  loaded existing: {existing_path.name} "
                      f"({len(existing.get('sections', []))} sections)")
            else:
                print(f"  WARNING: --chunk-labels set but no existing "
                      f"{existing_path.name} found; will write fresh")
        chapter_json, errs = extract_chapter(
            manifest, ch, backend, parallel, dry_run,
            chunk_label_filter=chunk_label_filter,
            existing_chapter=existing,
        )
        if dry_run or chapter_json is None:
            continue
        if errs:
            print(f"  VALIDATION: {len(errs)} errors")
            for e in errs[:8]:
                print(f"    - {e}")
            if len(errs) > 8:
                print(f"    ... and {len(errs) - 8} more")
            draft = output_dir / f"{ch.output_name}.draft"
            with open(draft, "w", encoding="utf-8") as f:
                json.dump(chapter_json, f, indent=2, ensure_ascii=False)
            print(f"  draft saved: {draft}")
            total_errors += len(errs)
            continue
        out = output_dir / ch.output_name
        with open(out, "w", encoding="utf-8") as f:
            json.dump(chapter_json, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  WRITTEN: {out}")
        print()

    print(f"Done. {total_errors} total validation errors.")
    return 1 if total_errors else 0


def cmd_discover(manifest_path: Path) -> int:
    print(f"Discovering from {manifest_path.name}...")
    manifest = Manifest.load(manifest_path)
    print(f"  PDF: {manifest.pdf_path}")
    manifest = discover_chapter_ranges(manifest)
    manifest.save(manifest_path)
    print(f"\nSaved: {manifest_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)

    pd = sub.add_parser("discover")
    pd.add_argument("manifest", type=Path)

    pe = sub.add_parser("extract")
    pe.add_argument("manifest", type=Path)
    pe.add_argument(
        "--chapters",
        type=lambda s: [int(x) for x in s.split(",")],
        default=None,
    )
    pe.add_argument("--dry-run", action="store_true")
    pe.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        default="anthropic",
        help="LLM provider. 'anthropic' uses ANTHROPIC_API_KEY. 'openai' uses "
             "OPENAI_API_KEY and works with any OpenAI-compatible endpoint "
             "(OpenAI, Azure, Foundry AIP, etc.).",
    )
    pe.add_argument(
        "--model",
        default=None,
        help=f"Model ID. Defaults: anthropic={DEFAULT_MODEL_ANTHROPIC}, "
             f"openai={DEFAULT_MODEL_OPENAI}. Override for Foundry (e.g. "
             f"--model gpt-4.1 or whatever your stack exposes).",
    )
    pe.add_argument(
        "--base-url",
        default=None,
        help="Base URL for OpenAI-compatible endpoint. Example for Foundry: "
             "https://<stack>.palantirfoundry.com/api/v2/aip/openai",
    )
    pe.add_argument(
        "--api-key",
        default=None,
        help="API key override (openai provider). Defaults to OPENAI_API_KEY env var.",
    )
    pe.add_argument("--parallel", type=int, default=DEFAULT_PARALLEL)
    pe.add_argument(
        "--chunk-labels",
        type=lambda s: [x.strip() for x in s.split(",") if x.strip()],
        default=None,
        help="Comma-separated chunk label substrings. Only matching chunks "
             "are extracted; results merge into the existing chapter JSON.",
    )

    args = ap.parse_args()
    mp = args.manifest.resolve()
    if not mp.exists():
        sys.exit(f"manifest not found: {mp}")

    if args.command == "discover":
        return cmd_discover(mp)

    # Build the backend from provider + model + optional OpenAI overrides.
    if args.provider == "openai":
        model = args.model or DEFAULT_MODEL_OPENAI
        backend: _Backend = _OpenAIBackend(
            model, base_url=args.base_url, api_key=args.api_key
        )
    else:
        model = args.model or DEFAULT_MODEL_ANTHROPIC
        backend = _AnthropicBackend(model)

    return cmd_extract(
        mp, args.chapters, args.dry_run, backend, args.parallel,
        chunk_label_filter=args.chunk_labels,
    )


if __name__ == "__main__":
    sys.exit(main())
