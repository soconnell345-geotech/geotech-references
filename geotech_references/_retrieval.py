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

Results that fit a size limit (REF-26). A caller with a limit on what one
result may hold (the GeotechStaffEngineer app sends an agent at most 16,000
characters of a reference tool's result and cuts the rest, which leaves
broken JSON) passes ``max_chars``: :func:`search_sections` then returns
ranked hits with a snippet each, as many as fit, and says how many it left
out and the ``offset`` of the next ones; :func:`load_chapter` lists a chapter
too long to send whole instead of sending it; :func:`list_chapters` with
``sections=False`` lists the chapters with their section counts, and with
``chapter`` one chapter's sections. Without ``max_chars`` (and with the
defaults) every function returns what it always did. :func:`fit_hits` and
:func:`fit_record` are the shared rules, used by
:mod:`geotech_references._retrieval_db` and
:mod:`geotech_references._figures_db` too.
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

#: A shaped search hit's text (a snippet, a summary, a caption) is at most
#: this long when the hits do not all fit whole (:func:`fit_hits`); a
#: section's whole text is one fetch away.
HIT_TEXT_CHARS = 300

#: ... and at most this long when not even one hit fits at
#: :data:`HIT_TEXT_CHARS`.
HIT_TEXT_MIN_CHARS = 100

#: Characters a shaped result keeps free for its own keys (the counts, the
#: ``next_offset`` and the ``note``).
_ENVELOPE_CHARS = 700


def json_size(obj) -> int:
    """Characters ``obj`` takes as JSON, measured as the app sends a tool
    result (``json.dumps(obj, default=str)``, non-ASCII escaped)."""
    return len(json.dumps(obj, default=str))


def shorten_text(text, n: int) -> str:
    """``text`` cut to at most ``n`` characters, at a word boundary where
    there is one, ending '...' where it was cut; unchanged when it is that
    short already."""
    text = str(text or "")
    if len(text) <= n:
        return text
    cut = text[:max(0, n - 3)]
    space = cut.rfind(" ")
    if space > n // 2:
        cut = cut[:space]
    return cut.rstrip() + "..."


def _shortened(item: dict, fields, n: int) -> tuple[dict, bool]:
    """``item`` with each of its string ``fields`` cut to ``n`` characters,
    and whether any was."""
    out, changed = item, False
    for f in fields:
        v = item.get(f)
        if isinstance(v, str) and len(v) > n:
            if out is item:
                out = dict(item)
            out[f] = shorten_text(v, n)
            changed = True
    return out, changed


def fit_hits(hits, max_chars: int, *, text_fields=(), offset: int = 0,
             more: bool = False, total=None,
             narrow: str = "narrow the query", fetch: str = "",
             max_offset: int | None = None) -> dict:
    """Ranked ``hits`` cut down to fit ``max_chars`` JSON characters by
    their shape, never cut part-way (REF-26).

    When the hits do not all fit, each hit's ``text_fields`` (a snippet, a
    summary, a caption) are shortened to :data:`HIT_TEXT_CHARS`, then the
    lowest-ranked hits are left out; when not even the first fits, its text
    is shortened to :data:`HIT_TEXT_MIN_CHARS`.

    Parameters
    ----------
    hits : list of dict
        Ranked hits, best first.
    max_chars : int
        The largest the whole returned dict may be, in JSON characters.
    text_fields : tuple of str
        The fields of a hit that may be shortened.
    offset : int
        The rank (0-based) of the first hit given.
    more : bool
        Whether hits exist after the last one given.
    total : int, optional
        How many hits there are in all, when known.
    narrow : str
        How the caller gets fewer, better hits (said in the ``note``).
    fetch : str
        How the caller gets a hit's whole text (said when one was
        shortened).
    max_offset : int, optional
        The deepest ``offset`` the caller's search takes. When the next
        hits would start past it there is no ``next_offset``, and the note
        says the search goes no deeper (never offering a page it cannot
        give).

    Returns
    -------
    dict
        ``hits`` (the hits shown) and ``shown`` (how many); ``total_hits``
        when ``total`` is given; and, when a hit was left out or shortened
        or more exist, ``left_out`` (hits given but not shown),
        ``next_offset`` (where the next hits start; absent when there are
        none) and a ``note`` saying how to get them.
    """
    hits = list(hits)
    budget = max(0, int(max_chars) - _ENVELOPE_CHARS)
    shortened_to = None
    trial = hits
    if _list_size(trial) > budget:
        pairs = [_shortened(h, text_fields, HIT_TEXT_CHARS) for h in hits]
        trial = [p[0] for p in pairs]
        if any(p[1] for p in pairs):
            shortened_to = HIT_TEXT_CHARS
    kept: list = []
    size = 2
    for h in trial:
        s = json_size(h) + (2 if kept else 0)
        if size + s > budget:
            break
        kept.append(h)
        size += s
    if not kept and trial:
        first, changed = _shortened(trial[0], text_fields, HIT_TEXT_MIN_CHARS)
        if json_size([first]) <= budget:
            kept = [first]
            if changed:
                shortened_to = HIT_TEXT_MIN_CHARS
    out: dict = {"hits": kept, "shown": len(kept)}
    if total is not None:
        out["total_hits"] = int(total)
    left_out = len(hits) - len(kept)
    if not (left_out or more or shortened_to):
        return out
    out["left_out"] = left_out
    notes = []
    if left_out or more:
        nxt = offset + len(kept)
        of = f" of {int(total):,}" if total is not None else ""
        shown = (f"hits {offset + 1}-{offset + len(kept)}{of}" if kept
                 else "no hits")
        why = (f"the rest would not fit in {int(max_chars):,} characters"
               if left_out else "as many as asked for")
        if max_offset is not None and nxt > max_offset:
            notes.append(
                f"Showing {shown}, best first ({why}); more match, but this "
                f"search pages no deeper than offset={max_offset}: {narrow}.")
        else:
            out["next_offset"] = nxt
            notes.append(
                f"Showing {shown}, best first ({why}); more match. Call "
                f"again with offset={nxt} for the next ones, or {narrow}.")
    if shortened_to:
        fields = "/".join(f for f in text_fields)
        notes.append(f"Each hit's {fields} is cut to {shortened_to} "
                     f"characters{'; ' + fetch if fetch else ''}.")
    out["note"] = " ".join(notes)
    return out


def _list_size(items) -> int:
    return 2 + sum(json_size(i) for i in items) + 2 * max(0, len(items) - 1)


def fit_record(record: dict, max_chars: int, text_fields=None):
    """``record`` fitted to ``max_chars`` JSON characters by shortening its
    longest text fields (``text_fields``; every string field when None),
    the longest first, never below 200 characters.

    Returns ``(record, shortened)``: the record (the same object when it
    already fits) and ``{field: its length before}`` for each field cut.
    """
    shortened: dict = {}
    if json_size(record) <= max_chars:
        return record, shortened
    out = dict(record)
    fields = [k for k, v in out.items() if isinstance(v, str)
              and (text_fields is None or k in text_fields)]
    while json_size(out) > max_chars:
        cands = [k for k in fields if len(out[k]) > 203]
        if not cands:
            break
        k = max(cands, key=lambda f: len(out[f]))
        excess = json_size(out) - max_chars
        shortened.setdefault(k, len(record[k]))
        out[k] = shorten_text(out[k], max(200, len(out[k]) - excess - 20))
    return out, shortened


def _reference_dir(reference: str) -> Path:
    """Return the package directory for a reference (e.g., 'gec_12')."""
    ref_dir = _PACKAGE_DIR / reference / "text"
    if not ref_dir.is_dir():
        raise FileNotFoundError(
            f"Reference '{reference}' not found. "
            f"Expected directory: {ref_dir}"
        )
    return ref_dir


def load_chapter(reference: str, chapter: int,
                 max_chars: int | None = None) -> dict:
    """Load a chapter JSON file and return the full chapter dict.

    Parameters
    ----------
    reference : str
        Reference identifier (e.g., 'gec_12').
    chapter : int
        Chapter number.
    max_chars : int, optional
        The largest result the caller can take, in JSON characters. A
        chapter longer than that is not returned whole: the result is its
        outline (:func:`chapter_outline`: its sections by number and title,
        ``chapter_chars`` and a ``note`` to fetch the sections needed with
        :func:`retrieve_section`). Default None: the whole chapter, however
        long (the largest is over 200,000 characters).

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
    chapter_file = ref_dir / f"chapter{int(chapter):02d}.json"
    if not chapter_file.exists():
        raise FileNotFoundError(
            f"Chapter {chapter} not found for reference '{reference}'. "
            f"Expected file: {chapter_file}"
        )
    with open(chapter_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    if max_chars is None:
        return data
    size = json_size(data)
    if size <= max_chars:
        return data
    out = chapter_outline(data, max_chars)
    out["chapter_chars"] = size
    out["note"] = (
        f"Chapter {data.get('chapter', chapter)} is {size:,} characters, "
        f"over the {int(max_chars):,}-character limit, so its text is not "
        "returned whole: its sections are listed by number and title. "
        "Fetch the ones you need with retrieve_section(section_id)."
        + _top_level_note(out))
    return out


def chapter_outline(chapter_data: dict, max_chars: int | None = None) -> dict:
    """A chapter file without its text: its own fields (reference, chapter,
    title, volume), ``n_sections`` (at every level) and ``sections`` (number
    and title of each, a nested one with its ``parent_id``).

    With ``max_chars``, an outline longer than that lists the top-level
    sections only, each with ``n_subsections`` (:func:`_top_level_note`
    words it)."""
    entries = section_entries(chapter_data)
    out = {k: v for k, v in chapter_data.items() if k != "sections"}
    out["n_sections"] = len(entries)
    out["sections"] = _section_list(entries)
    if max_chars is not None and json_size(out) > max_chars - _ENVELOPE_CHARS:
        out["sections"] = [
            {"section_id": e["section"].get("section_id", ""),
             "title": e["section"].get("title", ""),
             "n_subsections": _count_under(entries, i)}
            for i, e in enumerate(entries) if e["parent"] is None]
    return out


def _top_level_note(outline: dict) -> str:
    """What an outline that lists its top-level sections only says."""
    listed = len(outline.get("sections") or [])
    if listed >= outline.get("n_sections", 0):
        return ""
    return (f" Only its {listed} top-level sections are listed (all "
            f"{outline['n_sections']} would not fit); a section's "
            "subsections are its 'children' in retrieve_section.")


def _section_list(entries: list[dict]) -> list[dict]:
    """Number and title of every entry, a nested one with its parent_id."""
    out = []
    for entry in entries:
        section = entry["section"]
        item = {
            "section_id": section.get("section_id", ""),
            "title": section.get("title", ""),
        }
        if entry["nested"]:
            item["parent_id"] = (
                entries[entry["parent"]]["section"].get("section_id", ""))
        out.append(item)
    return out


def _count_under(entries: list[dict], i: int) -> int:
    """How many entries sit anywhere under entry ``i``."""
    return sum(1 for k in range(len(entries))
               if k != i and i in entry_chain(entries, k))


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
        If the section_id is not found in any chapter; the message names
        the nearest section above that number and up to eight sections
        numbered under it, as :func:`_retrieval_db.reference_get` does.
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
        f"Section '{section_id}' not found in reference '{reference}'"
        + _nearby(ref_dir, section_id)
    )


def _nearby(ref_dir: Path, section_id: str) -> str:
    """For a section number that is not there: the nearest section above
    it and up to eight sections numbered under it (:func:`nearby_note`)."""
    numbered: list[tuple[str, str]] = []
    for json_file in sorted(ref_dir.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            numbered += [(str(e["section"].get("section_id", "")),
                          e["section"].get("title", ""))
                         for e in section_entries(json.load(f))]
    titles: dict[str, str] = {}
    for sid, title in numbered:
        titles.setdefault(sid, title)
    above = next(((pid, titles[pid]) for pid in id_prefixes(section_id)
                  if pid in titles), None)
    below = [(sid, title) for sid, title in numbered
             if sid.startswith(f"{section_id}.")
             or sid.startswith(f"{section_id}-")][:8]
    return nearby_note(above, below)


def nearby_note(above, below) -> str:
    """``'; nearest section above it: 7.2.1 Title; sections numbered under
    it: 7.2.1.3.1 Title; ...'`` from ``above`` (a ``(section_id, title)``
    or None) and ``below`` (a list of them); ``''`` when both are empty.
    The wording of a missing section number in both retrieval layers."""
    parts = []
    if above:
        parts.append(f"nearest section above it: {above[0]} {above[1]}")
    if below:
        parts.append("sections numbered under it: " + "; ".join(
            f"{sid} {title}" for sid, title in below))
    return ("; " + "; ".join(parts)) if parts else ""


def search_sections(reference: str, query: str, limit: int | None = None,
                    offset: int = 0, max_chars: int | None = None):
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
    limit : int, optional
        At most this many matches. Default None: every match ("pile" in
        GEC-12 is over 300,000 characters of sections).
    offset : int, optional
        Skip this many of the best matches first (the next page).
    max_chars : int, optional
        The largest result the caller can take, in JSON characters. With
        it the result is a dict of hits that fits (:func:`fit_hits`): each
        hit is the section's number, title, chapter, ``parent_id``,
        ``under`` and a ``snippet`` of its text around the first query
        word, never its whole text (:func:`retrieve_section` fetches that);
        as many as fit, best first, with ``total_hits`` and, when some are
        not shown, ``next_offset`` and a ``note``.

    Returns
    -------
    list of dict, or dict with ``max_chars``
        Matching sections (own fields, without their subsections' text),
        each augmented with 'chapter', 'chapter_title', 'parent_id' and
        'under' (the sections above it). Sorted by relevance score
        (descending). With ``max_chars``, the dict described above.
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

    offset = max(0, int(offset or 0))
    total = len(results)
    if limit is not None or offset:
        end = None if limit is None else offset + max(1, int(limit))
        results = results[offset:end]
    if max_chars is None:
        return results
    hits = [_search_hit(r, query_words) for r in results]
    return fit_hits(
        hits, max_chars, text_fields=("snippet",), offset=offset,
        more=offset + len(hits) < total, total=total,
        narrow="narrow the query (more, or more specific, words)",
        fetch="retrieve_section(section_id) returns a section's whole text")


def _search_hit(section: dict, query_words: list[str]) -> dict:
    """A search match without its text: where it is and a snippet."""
    hit = {k: section.get(k) for k in (
        "section_id", "title", "chapter", "chapter_title", "parent_id",
        "under")}
    hit["snippet"] = _snippet(section, query_words)
    return hit


def _snippet(section: dict, query_words: list[str],
             n: int = HIT_TEXT_CHARS) -> str:
    """Up to ``n`` characters of a section's text, from a little before the
    first query word in it (its body, else its key points, else its
    applicability), or its opening where none is."""
    kps = section.get("key_points") or []
    texts = [str(section.get("body") or ""),
             " ".join(str(k) for k in kps) if isinstance(kps, list)
             else str(kps),
             str(section.get("applicability") or "")]
    for text in texts:
        low = text.lower()
        found = [p for p in (low.find(w) for w in query_words) if p >= 0]
        if found:
            start = max(0, min(found) - 80)
            if start:
                space = text.find(" ", start)
                start = space + 1 if 0 <= space < min(found) else start
            piece = shorten_text(text[start:], n - (3 if start else 0))
            return ("..." + piece) if start else piece
    return shorten_text(next((t for t in texts if t), ""), n)


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


def list_chapters(reference: str, chapter: int | None = None,
                  sections: bool = True,
                  max_chars: int | None = None) -> list[dict]:
    """List all chapters and their section IDs for a reference.

    Parameters
    ----------
    reference : str
        Reference identifier (e.g., 'gec_12').
    chapter : int, optional
        List this chapter only (a list of one, or of each file with that
        chapter number). A number the reference has no chapter for raises
        ``KeyError`` naming the chapters it has.
    sections : bool, optional
        False lists each chapter with its title and ``n_sections`` only,
        without its sections: the shape for a caller with a size limit,
        since every chapter with its sections runs to 27,820 characters
        (ufc_concrete_practice) where one chapter's sections are at most
        7.7 k. Default True.
    max_chars : int, optional
        A chapter whose listing is longer than this lists its top-level
        sections only, each with ``n_subsections``, and says so in a
        ``note``. Default None: every section, however long.

    Returns
    -------
    list of dict
        Each dict has 'chapter', 'chapter_title', 'reference_id',
        'n_sections' (how many sections it holds, at every level) and,
        unless ``sections`` is False, 'sections' (list of {section_id,
        title}, every level in file order; a section the file nests
        inside another also has 'parent_id').
    """
    ref_dir = _reference_dir(reference)
    chapters = []
    numbers = []

    for json_file in sorted(ref_dir.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            chapter_data = json.load(f)
        number = chapter_data.get("chapter", 0)
        numbers.append(number)
        if chapter is not None and str(number) != str(chapter).strip():
            continue

        item = {
            "chapter": number,
            "chapter_title": chapter_data.get("chapter_title", ""),
            "reference_id": chapter_data.get("reference_id", ""),
        }
        if not sections:
            item["n_sections"] = len(section_entries(chapter_data))
        else:
            outline = chapter_outline(chapter_data, max_chars)
            item["n_sections"] = outline["n_sections"]
            item["sections"] = outline["sections"]
            if _top_level_note(outline):
                item["note"] = _top_level_note(outline).strip()
        chapters.append(item)

    if chapter is not None and not chapters:
        raise KeyError(
            f"Chapter {chapter} not found in reference '{reference}'; its "
            f"chapters: {', '.join(str(n) for n in dict.fromkeys(numbers))}")
    return chapters
