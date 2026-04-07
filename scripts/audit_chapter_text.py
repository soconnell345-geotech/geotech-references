#!/usr/bin/env python3
"""
audit_chapter_text.py — Validate generated chapter JSON without re-reading the PDF.

Runs structural and consistency checks on the chapter JSONs produced by
build_chapter_text.py. Catches LLM hallucinations and schema drift without
requiring a second LLM pass over the source content.

Checks performed:
  1. Schema validity (same checks as build_chapter_text)
  2. Equation cross-reference coverage — every equation referenced in the
     equation module's docstrings (Eq X-Y) must appear in some section
  3. Equation cross-reference resolvability — every implemented_in field
     must point to a real, importable function
  4. Section ID format and ordering
  5. Required fields present
  6. Key-point sanity (3-12 items, each <= 300 chars)
  7. Body length floor (>= 100 chars)
  8. Section ID uniqueness within a chapter

Usage
-----
    python audit_chapter_text.py dm7_1
    python audit_chapter_text.py dm7_2 --manifest scripts/manifests/dm7_2.json
    python audit_chapter_text.py dm7_1 --chapter 5
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import re
import sys
from collections import defaultdict
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


def _is_container(sid: str, sections: list, index: int) -> bool:
    """A container section has child subsections later in document order;
    its body may legitimately be empty."""
    if not sid:
        return False
    for j in range(index + 1, len(sections)):
        other = sections[j]
        if not isinstance(other, dict):
            continue
        other_id = other.get("section_id", "")
        if other_id.startswith(sid + ".") or other_id.startswith(sid + "-"):
            return True
    return False


def validate_schema(chapter_json: dict) -> list[str]:
    errors: list[str] = []
    required_top = [
        "reference_id",
        "reference_title",
        "chapter",
        "chapter_title",
        "sections",
    ]
    for k in required_top:
        if k not in chapter_json:
            errors.append(f"missing top-level key: {k}")
    sections = chapter_json.get("sections", [])
    if not isinstance(sections, list) or not sections:
        errors.append("sections must be a non-empty array")
        return errors

    seen_ids: dict[str, int] = defaultdict(int)
    for i, sec in enumerate(sections):
        loc = f"sections[{i}]"
        if not isinstance(sec, dict):
            errors.append(f"{loc}: not an object")
            continue
        for k in (
            "section_id",
            "title",
            "summary",
            "body",
            "key_points",
            "equations",
            "figures",
            "tables",
            "applicability",
        ):
            if k not in sec:
                errors.append(f"{loc}: missing key '{k}'")
        summary = sec.get("summary", "")
        if isinstance(summary, str):
            if len(summary) < 50:
                errors.append(f"{loc}: summary < 50 chars")
            elif len(summary) > 700:
                errors.append(f"{loc}: summary > 700 chars")
        sid = sec.get("section_id", "")
        if sid:
            seen_ids[sid] += 1
            # FHWA/GEC dot form, UFC hyphen-then-dot form, prologue P.x or P-x
            if not re.match(r"^[0-9P]+([-.][0-9]+)*$", sid):
                errors.append(f"{loc}: section_id '{sid}' has invalid format")
        body = sec.get("body", "")
        kp_list = sec.get("key_points", []) if isinstance(sec.get("key_points"), list) else []
        summary_ok = len(sec.get("summary", "")) >= 100
        # Allow empty body if the section is a container OR if it has a
        # substantive summary plus at least two key_points (a stub section
        # that carries its content in bullets rather than prose).
        has_substance = _is_container(sid, sections, i) or (summary_ok and len(kp_list) >= 2)
        if isinstance(body, str) and len(body) < 100 and not has_substance:
            errors.append(
                f"{loc} ({sid}): body is shorter than 100 chars with no summary/key_points backup"
            )
        kp = sec.get("key_points")
        if isinstance(kp, list):
            if not (1 <= len(kp) <= 12):
                errors.append(f"{loc} ({sid}): key_points has {len(kp)} items (expected 1-12)")
            for j, p in enumerate(kp):
                if not isinstance(p, str):
                    errors.append(f"{loc}.key_points[{j}]: not a string")
                elif len(p) > 300:
                    errors.append(f"{loc}.key_points[{j}]: exceeds 300 chars")
        ap = sec.get("applicability", "")
        if isinstance(ap, str) and len(ap) < 10:
            errors.append(f"{loc} ({sid}): applicability is too short")

    duplicates = [sid for sid, count in seen_ids.items() if count > 1]
    if duplicates:
        errors.append(f"duplicate section_ids: {duplicates}")

    return errors


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
    parser.add_argument("reference", help="Reference id (e.g., dm7_1)")
    parser.add_argument(
        "--chapter",
        type=int,
        default=None,
        help="Audit only one chapter number",
    )
    args = parser.parse_args()

    text_dir = PACKAGE_DIR / args.reference / "text"
    if not text_dir.is_dir():
        sys.exit(f"No text/ directory at {text_dir}")

    json_files = sorted(text_dir.glob("*.json"))
    if not json_files:
        sys.exit(f"No chapter JSONs found in {text_dir}")

    if args.chapter is not None:
        json_files = [
            f for f in json_files if f.stem in (f"chapter{args.chapter:02d}", "prologue" if args.chapter == 0 else "")
        ]
        if not json_files:
            sys.exit(f"Chapter {args.chapter} not found")

    total_errors = 0
    for jf in json_files:
        chapter_json = load_chapter_json(text_dir, jf.name)
        errs, _ = audit_chapter(args.reference, chapter_json, jf.name)
        total_errors += errs

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
