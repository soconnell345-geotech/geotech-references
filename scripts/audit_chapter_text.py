#!/usr/bin/env python3
"""
audit_chapter_text.py — Validate generated chapter JSON without re-reading the PDF.

Runs structural and consistency checks on the chapter JSONs produced by
build_chapter_text.py. Catches LLM hallucinations and schema drift without
requiring a second LLM pass over the source content.

Checks performed (on every section at every level, nested ``subsections``
included):
  1. Required fields present (``REQUIRED_FIELDS``; a nested subsection needs
     only its number, title and body). ``summary`` is optional: it is the
     short text a ``reference_search`` hit shows, written for some
     references, and a reference without it is searched on its title and
     body (BACKLOG REF-05; REF-06 is the summaries still to write). When a
     summary is there it is at most 700 characters, and at least 50 unless
     the body it summarises is short.
  2. Equation cross-reference coverage — every equation referenced in the
     equation module's docstrings (Eq X-Y) must appear in some section
  3. Equation cross-reference resolvability — every implemented_in field
     must point to a real, importable function (fully qualified,
     ``geotech_references.<ref>.<module>.<function>``)
  4. Section ID format (``SECTION_ID``: dot, UFC hyphen-then-dot, prologue,
     a combined range, GEC-11's lettered level "3.5.2.a", a split part of a
     lettered section "4.4.6.c.a")
  5. Key points: at most 12, each <= 300 chars (a section may have none)
  6. Body floor: a section with no subsections has a body of at least a
     sentence (20 chars), or a summary or key points that say what a
     one-line printed section ("See UFC 3-250-07.") covers
  7. Applicability at least 10 chars where present
  8. Section ID uniqueness within a chapter

Usage
-----
    python audit_chapter_text.py              # every reference with text
    python audit_chapter_text.py dm7_1
    python audit_chapter_text.py dm7_1 --chapter 5
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import inspect
import io
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
PACKAGE_DIR = REPO_DIR / "geotech_references"

_EQ_NUMBER_PAT = re.compile(
    r"Eq(?:uation|\.)?\s*([0-9]+[-\u2013][0-9]+[a-z]?)", re.IGNORECASE
)


def _normalize_eq_id(raw: str) -> str:
    m = _EQ_NUMBER_PAT.search(raw)
    if m:
        return m.group(1).replace("\u2013", "-")
    return raw.strip().replace("\u2013", "-")


def load_chapter_json(text_dir: Path, filename: str) -> dict:
    with open(text_dir / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_referenced_eq_ids(chapter_json: dict) -> set[str]:
    """Set of normalized equation ids referenced anywhere in the chapter."""
    found: set[str] = set()

    def _walk(sections: list) -> None:
        for sec in sections:
            for eq in sec.get("equations", []):
                if isinstance(eq, dict):
                    if eq.get("id"):
                        found.add(_normalize_eq_id(eq["id"]))
                elif isinstance(eq, str):
                    found.add(_normalize_eq_id(eq))
            if "subsections" in sec:
                _walk(sec["subsections"])

    _walk(chapter_json.get("sections", []))
    return found


def collect_implemented_in_paths(chapter_json: dict) -> set[str]:
    """Set of dotted import paths claimed by `implemented_in` fields."""
    paths: set[str] = set()

    def _walk(sections: list) -> None:
        for sec in sections:
            for eq in sec.get("equations", []):
                if isinstance(eq, dict) and eq.get("implemented_in"):
                    paths.add(eq["implemented_in"])
            if "subsections" in sec:
                _walk(sec["subsections"])

    _walk(chapter_json.get("sections", []))
    return paths


def expected_eq_ids_from_module(equation_module_path: str) -> set[str]:
    """Scan the equation module's docstrings for all Eq X-Y references."""
    if not equation_module_path:
        return set()
    try:
        mod = importlib.import_module(equation_module_path)
    except ImportError:
        return set()
    found: set[str] = set()
    for name, func in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith("_"):
            continue
        if getattr(func, "__module__", "") != mod.__name__:
            continue
        doc = inspect.getdoc(func) or ""
        for match in _EQ_NUMBER_PAT.finditer(doc):
            found.add(match.group(1).replace("\u2013", "-"))
    return found


def can_resolve_path(dotted_path: str) -> bool:
    """Return True if a dotted path resolves to an importable function."""
    if "." not in dotted_path:
        return False
    parts = dotted_path.split(".")
    # Try progressively shorter module paths
    for split in range(len(parts) - 1, 0, -1):
        module_path = ".".join(parts[:split])
        attr_path = parts[split:]
        try:
            obj = importlib.import_module(module_path)
        except ImportError:
            continue
        for attr in attr_path:
            obj = getattr(obj, attr, None)
            if obj is None:
                break
        else:
            return callable(obj)
    return False


# The schema check lives in the package so local packs share it (REF-64).
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))
from geotech_references._schema import (  # noqa: E402,F401
    BODY_MIN_CHARS,
    REQUIRED_FIELDS,
    REQUIRED_NESTED_FIELDS,
    SECTION_ID,
    SUMMARY_MAX_CHARS,
    SUMMARY_MIN_CHARS,
    SUMMARY_STUB_BODY_CHARS,
    _flat_sections,
    _is_container,
    validate_schema,
)


def find_equation_module(reference: str, chapter: int, filename: str | None) -> str:
    """Heuristic: map a chapter to its equation module path."""
    if filename == "prologue":
        return f"geotech_references.{reference}.prologue"
    return f"geotech_references.{reference}.chapter{chapter}"


def audit_chapter(
    reference: str,
    chapter_json: dict,
    filename: str,
) -> tuple[int, int]:
    """Audit one chapter. Returns (errors, warnings)."""
    print(f"\n=== {reference}/{filename} ===")
    chapter_num = chapter_json.get("chapter", 0)
    title = chapter_json.get("chapter_title", "?")
    print(f"  Chapter {chapter_num}: {title}")

    errors = validate_schema(chapter_json)

    sections = chapter_json.get("sections", [])
    print(f"  Sections: {len(sections)}")

    referenced = collect_referenced_eq_ids(chapter_json)
    print(f"  Referenced equations: {len(referenced)}")

    eq_module = find_equation_module(
        reference,
        chapter_num,
        "prologue" if filename.startswith("prologue") else None,
    )
    expected = expected_eq_ids_from_module(eq_module)
    print(f"  Expected equations (from module {eq_module}): {len(expected)}")

    missing = expected - referenced
    if missing:
        for eq in sorted(missing):
            errors.append(f"equation Eq {eq} from {eq_module} not referenced in any section")

    paths = collect_implemented_in_paths(chapter_json)
    print(f"  implemented_in paths: {len(paths)}")
    # Paths are stored fully qualified (e.g., geotech_references.dm7_1.chapter5.foo)
    unresolved = [p for p in paths if not can_resolve_path(p)]
    if unresolved:
        for p in unresolved:
            errors.append(f"implemented_in path does not resolve: {p}")

    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("  OK")

    return len(errors), 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("reference", nargs="?", default=None,
                        help="Reference id (e.g., dm7_1); every reference "
                             "with chapter text when left out")
    parser.add_argument(
        "--chapter",
        type=int,
        default=None,
        help="Audit only one chapter number",
    )
    args = parser.parse_args()

    if args.reference is None:
        if args.chapter is not None:
            sys.exit("--chapter needs a reference")
        refs = sorted(d.parent.name for d in PACKAGE_DIR.glob("*/text")
                      if any(d.glob("*.json")))
        failed = []
        for ref in refs:
            if audit_reference(ref, None, quiet=True):
                failed.append(ref)
        print("=" * 60)
        if failed:
            print(f"AUDIT FAILED — {len(failed)} of {len(refs)} references: "
                  + ", ".join(failed))
            return 1
        print(f"AUDIT PASSED — {len(refs)} references, 0 errors")
        return 0
    return audit_reference(args.reference, args.chapter)


def audit_reference(reference: str, chapter: int | None,
                    quiet: bool = False) -> int:
    """Audit one reference's chapters; 0 when every chapter passes."""
    text_dir = PACKAGE_DIR / reference / "text"
    if not text_dir.is_dir():
        sys.exit(f"No text/ directory at {text_dir}")

    json_files = sorted(text_dir.glob("*.json"))
    if not json_files:
        sys.exit(f"No chapter JSONs found in {text_dir}")

    if chapter is not None:
        json_files = [
            f for f in json_files if f.stem in (f"chapter{chapter:02d}", "prologue" if chapter == 0 else "")
        ]
        if not json_files:
            sys.exit(f"Chapter {chapter} not found")

    total_errors = 0
    for jf in json_files:
        chapter_json = load_chapter_json(text_dir, jf.name)
        if quiet:
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                errs, _ = audit_chapter(reference, chapter_json, jf.name)
            if errs:
                print(buf.getvalue(), end="")
        else:
            errs, _ = audit_chapter(reference, chapter_json, jf.name)
        total_errors += errs

    if quiet:
        verdict = "passed" if not total_errors else f"{total_errors} errors"
        print(f"{reference}: {len(json_files)} chapters, {verdict}")
        return 1 if total_errors else 0
    print()
    print("=" * 60)
    if total_errors == 0:
        print(f"AUDIT PASSED — {len(json_files)} chapters, 0 errors")
        return 0
    else:
        print(f"AUDIT FAILED — {len(json_files)} chapters, {total_errors} errors total")
        return 1


if __name__ == "__main__":
    sys.exit(main())
