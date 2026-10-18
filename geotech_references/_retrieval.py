"""Reference text retrieval functions for structured JSON reference data.

Provides load, retrieve, and search operations across all reference texts
(GEC-12, and future references). Each reference stores chapter data as JSON
files following a standard schema.

Every level is addressable (REF-24). A chapter file either nests a section's
subsections inside it (``subsections``, GEC-12) or lists every level flat, one
entry per section (the other references). :func:`section_entries` reads both
into one tree: a nested section sits under the section that contains it, a
flat one under the nearest section of the same file whose number is a prefix
of its own. :func:`retrieve_section` and :func:`search_sections` work on any
section in that tree, and each section they return carries ``parent_id``,
``under`` (the chain of sections above it) and, from
:func:`retrieve_section`, ``children`` (the numbers and titles of the sections
directly under it) instead of their whole text.
"""

import json
import os
import re
from pathlib import Path

# Base directory for reference packages
_PACKAGE_DIR = Path(__file__).parent

#: The last part of a section number and the separator before it: '.1' of
#: '7.2.1', '-2' of '4-2', '.f' of '3.5.2.f'.
_LAST_PART_RE = re.compile(r"[.\-][^.\-]*$")

#: The largest result, in JSON characters, that
#: ``retrieve_section(..., include_subsections=True)`` and
#: ``_retrieval_db.reference_get(..., include_subsections=True)`` return with
#: the subsections inlined. It sits under the 16,000-character cap the
#: GeotechStaffEngineer app puts on a reference tool's result, so an inlined
#: section is never cut part-way; a larger one comes back with its children
#: listed and a note.
SUBSECTIONS_INLINE_MAX_CHARS = 12000


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


# ---------------------------------------------------------------------------
# The section tree of a chapter file (REF-24)
# ---------------------------------------------------------------------------

def id_prefixes(section_id: str) -> list[str]:
    """The numbers above a section number, nearest first:
    ``'4-2.1.3'`` -> ``['4-2.1', '4-2', '4']``, ``'3.5.2.f'`` ->
    ``['3.5.2', '3.5', '3']``."""
    out: list[str] = []
    sid = str(section_id or "")
    while True:
        m = _LAST_PART_RE.search(sid)
        if not m or m.start() == 0:
            return out
        sid = sid[:m.start()]
        out.append(sid)


def section_entries(chapter_data: dict) -> list[dict]:
    """Every section a chapter file holds, at every level, in file order.

    Each entry is ``{"section": <the section's own fields, without
    'subsections'>, "parent": <index of the entry it sits under, or None>,
    "nested": <True when the file nests it inside another section>}``.

    A section the file nests sits under the section that contains it. A
    section the file lists at the top level sits under the nearest section
    of the same file whose number is a prefix of its own ('5-5.2' under
    '5-5'; '7.3.2.1' under '7.3' where there is no '7.3.2'), if there is
    one. Where a number appears twice the first one is the section it
    resolves to.
    """
    entries: list[dict] = []

    def walk(secs, parent):
        for sec in secs or []:
            if not isinstance(sec, dict):
                continue
            own = {k: v for k, v in sec.items() if k != "subsections"}
            entries.append({"section": own, "parent": parent,
                            "nested": parent is not None})
            walk(sec.get("subsections"), len(entries) - 1)

    walk(chapter_data.get("sections"), None)
    first: dict[str, int] = {}
    for i, e in enumerate(entries):
        first.setdefault(str(e["section"].get("section_id", "")), i)
    for i, e in enumerate(entries):
        if e["parent"] is not None:
            continue
        for pid in id_prefixes(e["section"].get("section_id", "")):
            j = first.get(pid)
            if j is not None and not _sits_under(entries, j, i):
                e["parent"] = j
                break
    return entries


def _sits_under(entries: list[dict], j: int, i: int) -> bool:
    """Whether entry ``j`` is entry ``i`` or sits somewhere under it."""
    seen = set()
    while j is not None and j not in seen:
        if j == i:
            return True
        seen.add(j)
        j = entries[j]["parent"]
    return False


def entry_chain(entries: list[dict], i: int) -> list[int]:
    """The entries above entry ``i``, outermost first."""
    out: list[int] = []
    j = entries[i]["parent"]
    while j is not None and j not in out:
        out.append(j)
        j = entries[j]["parent"]
    return list(reversed(out))


def _label(section: dict) -> str:
    return f"{section.get('section_id', '')} {section.get('title', '')}".strip()


def under_text(chain: list[dict]) -> str:
    """``'7.2 Strength Limit States > 7.2.1 Nominal Axial ...'`` for the
    sections above one, outermost first; ``''`` for a top-level section."""
    return " > ".join(_label(s) for s in chain)


def _children(entries: list[dict], i: int) -> list[int]:
    return [k for k, e in enumerate(entries) if e["parent"] == i]


def _subtree(entries: list[dict], i: int) -> list[dict]:
    out = []
    for k in _children(entries, i):
        sec = dict(entries[k]["section"])
        kids = _subtree(entries, k)
        if kids:
            sec["subsections"] = kids
        out.append(sec)
    return out


def inline_subsections(view: dict, subsections: list[dict]) -> dict:
    """``view`` with ``subsections`` inlined when the whole stays within
    :data:`SUBSECTIONS_INLINE_MAX_CHARS`; otherwise ``view`` with a note
    (its ``children`` already list them)."""
    if not subsections:
        return view
    trial = dict(view, subsections=subsections)
    size = len(json.dumps(trial, default=str))
    if size <= SUBSECTIONS_INLINE_MAX_CHARS:
        return trial
    out = dict(view)
    out["note"] = (
        f"Subsections not inlined: with them this section is {size:,} "
        f"characters, over the {SUBSECTIONS_INLINE_MAX_CHARS:,}-character "
        "limit. Fetch the one you need by its section_id from 'children'.")
    return out


def section_view(entries: list[dict], i: int,
                 include_subsections: bool = False) -> dict:
    """Entry ``i`` as a retrieval result: its own fields plus ``parent_id``,
    ``under`` and ``children`` (number and title of each section directly
    under it); with ``include_subsections`` the sections under it inlined
    as ``subsections`` when they fit (:func:`inline_subsections`)."""
    chain = [entries[j]["section"] for j in entry_chain(entries, i)]
    out = dict(entries[i]["section"])
    out["parent_id"] = chain[-1].get("section_id") if chain else None
    out["under"] = under_text(chain)
    out["children"] = [
        {"section_id": entries[k]["section"].get("section_id", ""),
         "title": entries[k]["section"].get("title", "")}
        for k in _children(entries, i)]
    if include_subsections:
        out = inline_subsections(out, _subtree(entries, i))
    return out


def retrieve_section(reference: str, section_id: str,
                     include_subsections: bool = False) -> dict:
    """Get a specific section by its ID, at any level (e.g. '7.2',
    '7.2.1', '7.2.1.3.1').

    Searches across all chapters in the reference for a matching section_id.

    Parameters
    ----------
    reference : str
        Reference identifier (e.g., 'gec_12').
    section_id : str
        Section identifier (e.g., '7.2.1', '7.2.1.3.1').
    include_subsections : bool, optional
        Inline the sections under it as ``subsections`` (each with its
        own subsections), as long as the whole result stays within
        :data:`SUBSECTIONS_INLINE_MAX_CHARS`; past that they stay listed
        in ``children`` and a ``note`` says so. Default False: only
        ``children`` (numbers and titles) is given.

    Returns
    -------
    dict
        The section's own fields (title, body, key_points, equations,
        ...) plus ``parent_id``, ``under`` (the sections above it,
        outermost first) and ``children`` (number and title of each
        section directly under it).

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

    def find(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            entries = section_entries(json.load(f))
        for i, e in enumerate(entries):
            if e["section"].get("section_id") == section_id:
                return section_view(entries, i, include_subsections)
        return None

    if chapter_file is not None:
        found = find(chapter_file)
        if found is not None:
            return found

    # If not found in expected chapter, search all chapters (and prologue)
    for json_file in sorted(ref_dir.glob("*.json")):
        found = find(json_file)
        if found is not None:
            return found

    raise KeyError(
        f"Section '{section_id}' not found in reference '{reference}'."
    )


def search_sections(reference: str, query: str) -> list[dict]:
    """Keyword search across every section of a reference, at every level.

    Searches section titles, body text, key_points, and applicability
    fields. Returns matches ranked by relevance (title matches first,
    then body/key_points matches). A section's own text is scored, not
    its subsections', so a subsection that holds the words is a hit of
    its own.

    Parameters
    ----------
    reference : str
        Reference identifier (e.g., 'gec_12').
    query : str
        Search query (case-insensitive). Multiple words are AND-matched.

    Returns
    -------
    list of dict
        Matching sections (own fields, without their subsections' text),
        each augmented with 'chapter', 'chapter_title', 'parent_id' and
        'under' (the sections above it). Sorted by relevance score
        (descending).
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
        entries = section_entries(chapter_data)

        for i, entry in enumerate(entries):
            score = _score_section(entry["section"], query_words)
            if score > 0:
                result = section_view(entries, i)
                result.pop("children", None)
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
        (list of {section_id, title}, every level in file order; a
        section the file nests inside another also has 'parent_id').
    """
    ref_dir = _reference_dir(reference)
    chapters = []

    for json_file in sorted(ref_dir.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            chapter_data = json.load(f)

        section_list = []
        entries = section_entries(chapter_data)
        for entry in entries:
            section = entry["section"]
            item = {
                "section_id": section.get("section_id", ""),
                "title": section.get("title", ""),
            }
            if entry["nested"]:
                item["parent_id"] = (
                    entries[entry["parent"]]["section"].get("section_id", ""))
            section_list.append(item)

        chapters.append({
            "chapter": chapter_data.get("chapter", 0),
            "chapter_title": chapter_data.get("chapter_title", ""),
            "reference_id": chapter_data.get("reference_id", ""),
            "sections": section_list,
        })

    return chapters
