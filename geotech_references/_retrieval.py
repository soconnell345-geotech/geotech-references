"""Reference text retrieval functions for structured JSON reference data.

Provides load, retrieve, and search operations across all reference texts
(GEC-12, and future references). Each reference stores chapter data as JSON
files following a standard schema.
"""

import json
import os
from pathlib import Path

# Base directory for reference packages
_PACKAGE_DIR = Path(__file__).parent


def _reference_dir(reference: str) -> Path:
    """Return the package directory for a reference (e.g., 'gec_12')."""
    ref_dir = _PACKAGE_DIR / reference / "text"
    if not ref_dir.is_dir():
        raise FileNotFoundError(
            f"Reference '{reference}' not found. "
            f"Expected directory: {ref_dir}"
        )
    return ref_dir


def load_chapter(reference: str, chapter: int) -> dict:
    """Load a chapter JSON file and return the full chapter dict.

    Parameters
    ----------
    reference : str
        Reference identifier (e.g., 'gec_12').
    chapter : int
        Chapter number.

    Returns
    -------
    dict
        Full chapter data including sections, equations, figures, tables.

    Raises
    ------
    FileNotFoundError
        If the chapter JSON file does not exist.
    """
    ref_dir = _reference_dir(reference)
    chapter_file = ref_dir / f"chapter{chapter:02d}.json"
    if not chapter_file.exists():
        raise FileNotFoundError(
            f"Chapter {chapter} not found for reference '{reference}'. "
            f"Expected file: {chapter_file}"
        )
    with open(chapter_file, "r", encoding="utf-8") as f:
        return json.load(f)


def retrieve_section(reference: str, section_id: str) -> dict:
    """Get a specific section by its ID (e.g., '7.2.1').

    Searches across all chapters in the reference for a matching section_id.

    Parameters
    ----------
    reference : str
        Reference identifier (e.g., 'gec_12').
    section_id : str
        Section identifier (e.g., '7.2.1', '7.2.1.3.1').

    Returns
    -------
    dict
        The section dict with title, body, key_points, equations, etc.

    Raises
    ------
    KeyError
        If the section_id is not found in any chapter.
    """
    ref_dir = _reference_dir(reference)

    # Determine which chapter to search based on the section_id prefix.
    # Handles dot form ('5.3.2'), UFC hyphen-then-dot form ('4-2.1'), and
    # prologue ('P-1' / 'P.1' → prologue.json).
    head = section_id.split(".")[0].split("-")[0]
    chapter_file = None
    if head.upper() == "P":
        cand = ref_dir / "prologue.json"
        if cand.exists():
            chapter_file = cand
    else:
        try:
            chapter_num = int(head)
            cand = ref_dir / f"chapter{chapter_num:02d}.json"
            if cand.exists():
                chapter_file = cand
        except ValueError:
            pass

    if chapter_file is not None:
        with open(chapter_file, "r", encoding="utf-8") as f:
            chapter_data = json.load(f)
        for section in chapter_data.get("sections", []):
            if section.get("section_id") == section_id:
                return section

    # If not found in expected chapter, search all chapters (and prologue)
    for json_file in sorted(ref_dir.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            chapter_data = json.load(f)
        for section in chapter_data.get("sections", []):
            if section.get("section_id") == section_id:
                return section

    raise KeyError(
        f"Section '{section_id}' not found in reference '{reference}'."
    )


def search_sections(reference: str, query: str) -> list[dict]:
    """Keyword search across all sections in a reference.

    Searches section titles, body text, key_points, and applicability
    fields. Returns matches ranked by relevance (title matches first,
    then body/key_points matches).

    Parameters
    ----------
    reference : str
        Reference identifier (e.g., 'gec_12').
    query : str
        Search query (case-insensitive). Multiple words are AND-matched.

    Returns
    -------
    list of dict
        Matching sections, each augmented with 'chapter' and
        'chapter_title' fields. Sorted by relevance score (descending).
    """
    ref_dir = _reference_dir(reference)
    query_lower = query.lower()
    query_words = query_lower.split()
    results = []

    for json_file in sorted(ref_dir.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            chapter_data = json.load(f)

        ch_num = chapter_data.get("chapter", 0)
        ch_title = chapter_data.get("chapter_title", "")

        for section in chapter_data.get("sections", []):
            score = _score_section(section, query_words)
            if score > 0:
                result = dict(section)
                result["chapter"] = ch_num
                result["chapter_title"] = ch_title
                result["_score"] = score
                results.append(result)

    # Sort by score descending, then by section_id for stable ordering
    results.sort(key=lambda r: (-r["_score"], r.get("section_id", "")))

    # Remove internal score from output
    for r in results:
        r.pop("_score", None)

    return results


def _score_section(section: dict, query_words: list[str]) -> int:
    """Score a section against query words. Higher = more relevant."""
    title = section.get("title", "").lower()
    body = section.get("body", "").lower()
    key_points = " ".join(section.get("key_points", [])).lower()
    applicability = section.get("applicability", "").lower()

    # All query words must appear in at least one field
    combined = f"{title} {body} {key_points} {applicability}"
    for word in query_words:
        if word not in combined:
            return 0

    # Score: title matches are worth more
    score = 0
    for word in query_words:
        if word in title:
            score += 10
        if word in body:
            score += 3
        if word in key_points:
            score += 5
        if word in applicability:
            score += 2

    return score


def list_chapters(reference: str) -> list[dict]:
    """List all chapters and their section IDs for a reference.

    Parameters
    ----------
    reference : str
        Reference identifier (e.g., 'gec_12').

    Returns
    -------
    list of dict
        Each dict has 'chapter', 'chapter_title', and 'sections'
        (list of {section_id, title}).
    """
    ref_dir = _reference_dir(reference)
    chapters = []

    for json_file in sorted(ref_dir.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            chapter_data = json.load(f)

        section_list = []
        for section in chapter_data.get("sections", []):
            section_list.append({
                "section_id": section.get("section_id", ""),
                "title": section.get("title", ""),
            })

        chapters.append({
            "chapter": chapter_data.get("chapter", 0),
            "chapter_title": chapter_data.get("chapter_title", ""),
            "reference_id": chapter_data.get("reference_id", ""),
            "sections": section_list,
        })

    return chapters
