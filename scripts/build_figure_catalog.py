"""Build a figure catalog (figures_catalog.json) for a reference package.

For a reference whose manifest carries a ``pdf_path`` and chapter page ranges,
this script:

1. Parses the PDF's "LIST OF FIGURES" section into ``{figure_number, caption,
   printed_page}`` entries (the authoritative figure list with full captions).
2. Resolves each figure to its 0-based PDF page index by searching the document
   *body* for the page where ``Figure <num>`` is immediately followed by the
   figure's caption text (the caption only appears verbatim on the figure's own
   page; in-text references read "Figure X-Y shows ..."). Front matter is skipped
   using the first chapter's ``page_start`` from the manifest.
3. Backfills any figure the caption search misses, first via the median
   printed-to-PDF page offset, then by monotonic interpolation between resolved
   neighbours, so every figure gets a best-estimate page.
4. Writes ``geotech_references/<package>/figures_catalog.json``.

The catalog is the indexable artifact consumed by
``geotech_references._figures_db`` (FTS5 retrieval) and by the
``read_reference_figure`` vision tool, which renders the resolved page for
on-demand chart read-off. The ``description`` field starts empty and is filled
lazily the first time a figure is read off.

This is a one-time, no-API build step (pure PyMuPDF text parsing).

Usage
-----
    python scripts/build_figure_catalog.py dm7_2
    python scripts/build_figure_catalog.py dm7_1 dm7_2
    python scripts/build_figure_catalog.py all
    python scripts/build_figure_catalog.py --pack <pack dir> [--pdf FILE]
                                           [--sequential]

``--pack`` builds a local reference pack's catalog (BACKLOG REF-64; see
``docs/REFERENCE_PACKS.md``): the PDF is ``--pdf`` or the first of
``pack.json``'s ``pdf_files``, looked for in the pack folder; descriptions are
enriched from the pack's own ``text/``; the catalog goes to
``<pack dir>/figures_catalog.json`` with ``pdf_path`` as the file name only,
keeping any ``bbox`` / ``read_notes`` an earlier catalog gave a figure. Check
the result with ``python -m geotech_references.packs check <pack dir>``.

Requires: PyMuPDF (``pip install PyMuPDF``).
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from difflib import SequenceMatcher
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
_MANIFEST_DIR = _SCRIPTS_DIR / "manifests"
_PACKAGE_DIR = _REPO_ROOT / "geotech_references"

# A figure marker, e.g. "Figure 4-12", "Figure P-1" (DM7/UFC dash), "Figure 2.1"
# (GEC dot), or "Figure 1 - 1" (micropile spaced dash). Matched anywhere (not
# just line start) so inline-glued LoF entries segment too. Spaces around the
# separator are tolerated and stripped from the captured id (see _fig_id).
_FIG_MARKER = re.compile(r"Figure\s+((?:[A-Z]{1,3}|\d+)\s*[-.]\s*\d+)", re.I)


def _fig_id(raw: str) -> str:
    """Normalize a captured figure id: 'Figure '-free, spaces stripped, upper."""
    return re.sub(r"\s+", "", raw).upper()


# Sequential figure numbering used by some older refs (e.g. GEC-4, 1999):
# "Figure 1", "Figure 21" with no chapter dash. Lookaheads exclude longer digit
# runs and dash/dot *ids* ("1-1", "1.5") but still allow a caption period
# ("Figure 1. Components ...").
_SEQ_MARKER = re.compile(r"Figure\s+(\d{1,3})(?!\d)(?![-.]\d)", re.I)
# A dotted leader terminated by the printed page number.
_LEADER_PG = re.compile(r"\.{2,}\s*(\d+)\s*$")
# Trailing bare page number (no dotted leader); guard against caption-internal
# numbers by requiring it to be the very last token.
_TRAIL_PG = re.compile(r"(?<![\d-])(\d{1,4})\s*$")
# A chapter-page number ("1 - 4", "A-28") at the end of an entry, the way the
# micropile manual and the appendices print them. The page is the number after
# the dash; the chapter is the figure's own.
_CHAPTER_PG = re.compile(r"(?<![\w-])(?:\d{1,2}|[A-Z])\s*-\s*(\d{1,4})\s*$")
# Headings that end a List of Figures: the next list, or the body.
_LOF_END = re.compile(
    r"^\s*(?:LIST OF (?:TABLES|SYMBOLS|APPENDICES|ABBREVIATIONS|ACRONYMS)"
    r"|ACRONYMS(?: AND ABBREVIATIONS)?|CHAPTER\s+1)\s*$", re.I)
#: A caption longer than this ran on into the page text (BACKLOG REF-27):
#: the longest real caption in the library is under 500 characters.
MAX_CAPTION_CHARS = 500
# What a caption that ran on carries: another figure's entry, a list heading,
# a running header or a list of symbols.
_RUN_ON = re.compile(
    r"Figure\s+(?:[A-Z]{1,3}|\d+)\s*[-.]\s*\d+\s*[.:]\s+[A-Z]"
    r"|Table\s+\d+\s*[-.]\s*\d+\.\s+[A-Z]"
    r"|LIST OF (?:FIGURES|TABLES|SYMBOLS|APPENDICES)"
    r"|FHWA[- ]NHI-\d\d-\d{3}(?:\s+(?:Chapter|Table of Contents|GEC ?\d)|\s*$)"
    r"|TABLE OF CONTENTS \(continued\)|\bLOF-\d")
# Smart quotes / dashes / replacement char -> ASCII (PyMuPDF emits these; the
# Windows console renders them as the replacement glyph).
_SMART = {0x201C: '"', 0x201D: '"', 0x2018: "'", 0x2019: "'",
          0x2013: "-", 0x2014: "-", 0xFFFD: " "}


def _norm(s: str) -> str:
    """Lowercase and strip everything but alphanumerics (subscript/garble safe)."""
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _is_lof_noise(line: str) -> bool:
    """True for running headers/footers that bleed into the List of Figures."""
    s = line.strip()
    if not s:
        return True
    if re.match(r"(?i)^UF[SC]\s+3-", s):              # "UFC 3-220-20" header (OCR: UFS)
        return True
    if re.match(r"(?i)^\d{1,2}\s+[A-Za-z]+\s+\d{4}$", s):   # "16 January 2025"
        return True
    if re.match(r"(?i)^[ivxlcdm]{1,6}(?:\s*-\s*[ivxlcdm]{1,6})?$", s):
        return True                                   # roman page no. ("i - xii")
    if re.match(r"(?i)^list of (figures|tables)$", s):
        return True
    if re.match(r"^LOF-\d{1,2}$", s):                  # GEC-10's list page label
        return True
    return False


def _clean_caption(seg: str) -> tuple[str, int | None]:
    """Split a between-markers segment into (caption, printed_page)."""
    cap, printed, _ = _split_entry(seg)
    return cap, printed


def _split_entry(seg: str) -> tuple[str, "int | None", "str | None"]:
    """``(caption, printed_page, page_token)`` of a between-markers segment;
    the token is the entry's page as the list prints it ("12-12", "306"),
    None when the entry ends with no page."""
    seg = re.sub(r"\s+", " ", seg).strip()
    printed = token = None
    lm = _LEADER_PG.search(seg)
    if lm:
        printed, token = int(lm.group(1)), lm.group(1)
        seg = _LEADER_PG.sub("", seg)
    else:
        cm = _CHAPTER_PG.search(seg)
        tm = None if cm else _TRAIL_PG.search(seg)
        if cm:
            printed, token = int(cm.group(1)), re.sub(r"\s+", "", cm.group(0))
            seg = seg[:cm.start()]
        elif tm:
            printed, token = int(tm.group(1)), tm.group(1)
            seg = seg[:tm.start()]
    cap = re.sub(r"\.{2,}", "", seg).translate(_SMART)
    # Strip leading colon too: GEC entries read "Figure 2.1: <caption>".
    cap = re.sub(r"\s+", " ", cap).strip(" .-:")
    return cap, printed, token


def prints_after_caption(text: str, figure_number: str, caption: str,
                         token: str) -> bool:
    """True when ``text`` (a figure's page) prints ``token`` right after the
    last word of the figure's caption, on the same line ("Figure 7-31. ...
    Example 7-3"): the number is the caption's own, not the list's page for
    the figure."""
    words = re.findall(r"[A-Za-z0-9]+", caption.translate(_SMART))
    if not words or not token:
        return False
    text = text.translate(_SMART)
    num = r"\s*[-.]\s*".join(re.escape(p) for p in re.split(r"[-.]", figure_number))
    tok = r"[ \t]*-[ \t]*".join(re.escape(p) for p in re.split(r"\s*-\s*", token))
    tail = re.compile(rf"(?i)(?<![A-Za-z0-9]){re.escape(words[-1])}[ \t.,:;)]*"
                      rf"[ \t]{tok}(?!\d)")
    for m in re.finditer(rf"(?i)Figure\s+{num}(?!\d)", text):
        if tail.search(text, m.end(), m.end() + len(caption) + 200):
            return True
    return False


def _running_lines(pages: list[list[str]]) -> set[str]:
    """Lines printed on every page of a multi-page list (its running header and
    footer: "FHWA NHI-05-039", "Micropile Design & Construction", "December
    2005"), which would otherwise join the caption of the entry they follow."""
    if len(pages) < 2:
        return set()
    sets = [{_header_key(ln) for ln in lines if _header_key(ln)} for lines in pages]
    common = set.intersection(*sets)
    return {ln for ln in common if not _FIG_MARKER.search(ln)}


def _header_key(line: str) -> str:
    """A line without the page number a running header carries ("i-xii")."""
    return re.sub(r"(?i)\s+[ivxlc]{1,6}\s*-\s*[ivxlc]{1,6}\s*$", "",
                  line).strip()


def _parse_list_of_figures(doc) -> tuple[list[dict], "int | None"]:
    """Parse the LIST OF FIGURES section into figure entries.

    Segments the section text on figure markers (robust to entries glued
    inline and to header/footer noise across page breaks). Returns
    ``(figs, lof_last_page)``: a list of ``{figure_number, caption,
    printed_page, list_page}`` dicts in document order (``list_page`` is the
    page token the entry ends with, as printed), plus the last PDF page index the
    figure list occupies (so body resolution can start after the front matter).
    ``lof_last_page`` is ``None`` when no list is found.
    """
    lof_pages: list[int] = []
    start = None
    for i in range(min(60, doc.page_count)):
        if re.search(r"^\s*LIST OF FIGURES\s*$", doc[i].get_text(), re.I | re.M):
            start = i
            break
    kept: list[str] = []
    if start is not None:
        pages: list[list[str]] = []
        whole: list[list[str]] = []         # each page as printed, for headers
        for i in range(start, min(start + 14, doc.page_count)):
            lines = [ln.translate(_SMART) for ln in doc[i].get_text().splitlines()]
            if i > start and not _FIG_MARKER.search("\n".join(lines)):
                break                       # a page with no figure entry
            lof_pages.append(i)
            whole.append(lines)
            # on the first page the list starts at its heading (a list of
            # tables may come before it on the same page)
            first = 0
            if i == start:
                first = next(k for k, ln in enumerate(lines) if re.search(
                    r"(?i)^\s*list of figures\s*$", ln))
            end = next((k for k in range(first + 1, len(lines))
                        if _LOF_END.match(lines[k])), None)
            pages.append(lines[first:end])
            if end is not None:
                break
        # A line printed on every page of the list is its running header.
        running = _running_lines(whole)
        for lines in pages:
            kept.extend(ln.strip() for ln in lines
                        if not _is_lof_noise(ln) and _header_key(ln) not in running)
    else:
        # No "LIST OF FIGURES" heading: fall back to the contiguous run of
        # front-matter pages dense with dotted-leader figure entries (some
        # references, e.g. GEC-9, carry the figure list with no heading). Require
        # both several figure markers AND dotted page leaders so the main TOC
        # (chapters, no figure markers) and body pages (no leaders) are skipped.
        dense = [
            i for i in range(min(60, doc.page_count))
            if len(_FIG_MARKER.findall(doc[i].get_text())) >= 3
            and len(re.findall(r"\.{3,}\s*\d{1,4}", doc[i].get_text())) >= 3
        ]
        if not dense:
            return [], None
        run = [dense[0]]
        for i in dense[1:]:
            if i == run[-1] + 1:
                run.append(i)
            else:
                break
        lof_pages = run
        whole = [[ln.translate(_SMART) for ln in doc[i].get_text().splitlines()]
                 for i in run]
        # GEC-11's running head ("FHWA NHI-10-024 / Table of Contents / ...
        # November 2009") would join the last entry on each page (REF-51)
        running = _running_lines(whole)
        for lines in whole:
            kept.extend(ln.strip() for ln in lines
                        if not _is_lof_noise(ln) and _header_key(ln) not in running)

    blob = "\n".join(kept)
    # An entry starts a line or follows the previous entry's page number; a
    # marker inside a caption ("Equations Used in Each Cell in Figure 6-35")
    # is a cross-reference, not an entry.
    markers = [m for m in _FIG_MARKER.finditer(blob)
               if re.search(r"(?:^|\n|[\d.])\s*$", blob[:m.start()][-12:] or "\n")]
    figs: list[dict] = []
    for k, m in enumerate(markers):
        end = markers[k + 1].start() if k + 1 < len(markers) else len(blob)
        cap, printed, token = _split_entry(blob[m.end():end])
        figs.append(
            {"figure_number": _fig_id(m.group(1)),
             "caption": cap, "printed_page": printed, "list_page": token}
        )
    return figs, (max(lof_pages) if lof_pages else None)


def _norm_fig_ref(s) -> str:
    """Normalize a text-cited figure ref to a catalog key ('Figure 4-12'->'4-12').

    Tolerates strings ("Figure 2.1: caption") and dicts ({"number": "2.1", ...}) —
    reference text JSON is not uniform across packages — and trims any trailing
    ": caption" so GEC-style citations match the bare figure id.
    """
    if isinstance(s, dict):
        s = (s.get("number") or s.get("figure_number") or s.get("figure_id")
             or s.get("id") or s.get("label") or s.get("ref") or "")
    s = (str(s) if s is not None else "").strip()
    if s.lower().startswith("figure"):
        s = s[len("figure"):].strip()
    if s:  # keep only the figure-id token; drop any trailing ": caption"
        s = re.split(r"[:\s]", s, maxsplit=1)[0]
    return s.upper()


def _enrich_from_text(package: str, figs: list[dict], max_chars: int = 800,
                      text_dir: "Path | None" = None) -> int:
    """Fold concept vocabulary from the chapter text into figure descriptions.

    Figure captions use notation (``KA``/``KP``) while engineers query by
    concept ("passive earth pressure"). The structured chapter text in
    ``<package>/text/*.json`` cites each figure and carries the concept
    vocabulary in section titles / applicability / key points. We aggregate the
    context of every section that cites a figure into that figure's searchable
    ``description``. No API cost — pure cross-link of curated text.

    Returns the number of figures enriched.
    """
    if text_dir is None:
        text_dir = _PACKAGE_DIR / package / "text"
    if not text_dir.is_dir():
        return 0

    def _walk(sections):
        # Nested subsections cite figures too (e.g. GEC-12 7.3.7.x).
        for sec in sections or []:
            if isinstance(sec, dict):
                yield sec
                yield from _walk(sec.get("subsections"))

    ctx: dict[str, list[str]] = {}
    for jf in sorted(text_dir.glob("*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for sec in _walk(data.get("sections", [])):
            cited = sec.get("figures", []) or []
            if not cited:
                continue
            parts: list[str] = []
            if sec.get("title"):
                parts.append(str(sec["title"]))
            if sec.get("applicability"):
                parts.append(str(sec["applicability"]))
            kps = sec.get("key_points", [])
            if isinstance(kps, list) and kps:
                parts.append(" ".join(str(k) for k in kps))
            snippet = re.sub(r"\s+", " ", " ".join(parts)).strip()
            if not snippet:
                continue
            for c in cited:
                key = _norm_fig_ref(c)
                if key:
                    bucket = ctx.setdefault(key, [])
                    if snippet not in bucket:
                        bucket.append(snippet)

    enriched = 0
    for f in figs:
        snips = ctx.get(f["figure_number"].upper())
        if not snips:
            continue
        desc = re.sub(r"\s+", " ", " ".join(snips)).strip()
        if len(desc) > max_chars:
            desc = desc[:max_chars].rsplit(" ", 1)[0]
        f["description"] = desc
        enriched += 1
    return enriched


def _chapter_of(figure_number: str):
    """Infer an integer chapter from a figure number prefix.

    ``"4-12"`` -> 4, ``"P-1"`` (prologue) -> 0, anything else -> ``None``.
    """
    prefix = figure_number.split("-", 1)[0]
    if prefix.upper() == "P":
        return 0
    if prefix.isdigit():
        return int(prefix)
    return None


def _chapter_key(figure_number: str) -> str:
    """The chapter part of a figure number: "4" of "4-12", "A" of "A.17"."""
    return re.split(r"[-.]", figure_number, maxsplit=1)[0]


#: How alike a List of Figures caption and the caption printed on a figure's
#: page must be (difflib ratio of the normalized text) for that page to be the
#: figure's when the list words the caption differently: GEC-12 Vol I lists
#: Figure 3-6 as "Nominal resistance and pile support cost", and its page
#: (printed p. 60) prints "Nominal shaft resistance and pile support cost".
NEAR_CAPTION_RATIO = 0.8
#: How many pages either side of the page the printed-page offset predicts
#: are searched for such a caption.
NEAR_CAPTION_PAGES = 3
#: Mathematical alphanumeric symbols: a page whose text layer spells a formula
#: glyph by glyph (GEC-5 Figure 7-14's su/sigma'vc in math italic letters)
#: gives the page, but the list's plain caption is kept.
_MATH_ALNUM = re.compile("[\U0001D400-\U0001D7FF]")


def _page_caption(text: str, figure_number: str) -> "str | None":
    """The caption printed under ``Figure <n>`` on one page, or None.

    The marker starts a line and a capitalized caption follows it (a sentence
    such as "Figure 3-6 presents ..." does not count); the caption is the lines
    after it, up to the one that ends with a period (at most four).
    """
    num = r"\s*[-.]\s*".join(re.escape(p) for p in re.split(r"[-.]",
                                                            figure_number))
    for m in re.finditer(
            rf"(?m)^[ \t]*Figure\s+{num}(?!\d)(?![.-]\d)[ \t]*[.:]?[ \t]*",
            text):
        lines = []
        for line in text[m.end():].split("\n"):
            line = line.strip()
            if not line:
                if lines:
                    break
                continue
            lines.append(line)
            if line.endswith(".") or len(lines) == 4:
                break
        cap = re.sub(r"\s+", " ", " ".join(lines)).translate(_SMART)
        cap = cap.strip(" .-:")
        if cap[:1].isupper():
            return cap
    return None


def _resolve_pages(doc, figs: list[dict], body_start: int) -> dict:
    """Resolve a ``pdf_page_index`` for every figure. Mutates ``figs`` in place.

    A figure whose List of Figures caption is not printed word for word on any
    page takes the page near its printed page whose caption is nearly the same,
    else the nearest page with a caption block under its label, and the
    caption as that page prints it (the figure's own page is the record)
    unless the page's text spells a formula in math glyphs. "Near" counts from
    the printed page plus the page offset of the figure's own chapter.

    Returns a small stats dict.
    """
    texts = [doc[i].get_text() for i in range(doc.page_count)]
    norm_pages = [_norm(re.sub(r"\s+", " ", t)) for t in texts]

    for f in figs:
        key = _norm(f"Figure {f['figure_number']}")
        tgt = _norm(f["caption"])[:15]
        idx = None
        if tgt:
            needle = key + tgt
            for i in range(body_start, doc.page_count):
                if needle in norm_pages[i]:
                    idx = i
                    break
        f["pdf_page_index"] = idx
        # The number an entry ends with is its page unless the figure's own
        # page prints it as the end of the caption (REF-51).
        if idx is not None and f.get("list_page") and prints_after_caption(
                texts[idx], f["figure_number"], f["caption"], f["list_page"]):
            f["caption"] = f"{f['caption']} {f['list_page']}"
            f["printed_page"] = None

    # Fallback 1: median printed->index offset for figures still unresolved,
    # over the figure's own chapter: a list that prints chapter-page numbers
    # ("4 - 17", the Micropile manual) restarts them in every chapter, so one
    # offset over the whole list puts a figure chapters away.
    by_chapter: dict[str, list[int]] = {}
    for f in figs:
        if f["pdf_page_index"] is not None and f["printed_page"]:
            by_chapter.setdefault(_chapter_key(f["figure_number"]), []).append(
                f["pdf_page_index"] - f["printed_page"])
    offsets = [o for chap in by_chapter.values() for o in chap]
    offset = int(statistics.median(offsets)) if offsets else 0

    def expected_page(f) -> int:
        own = by_chapter.get(_chapter_key(f["figure_number"]))
        return f["printed_page"] + (int(statistics.median(own)) if own else offset)

    # A list caption worded differently from the figure's page: the page near
    # the predicted one whose printed caption is nearly the same, else the
    # nearest one with a text block that opens with the figure's label and a
    # caption (Micropile lists Figure 4-3 as "Small Track-mounted Rotary
    # Hydraulic Drill Rig"; its page prints "Low Headroom Track-Mounted
    # Rotary Hydraulic Drill Rig ...").
    near_resolved = 0
    for f in figs:
        if f["pdf_page_index"] is not None or not f["caption"] \
                or not f["printed_page"]:
            continue
        want = _norm(f["caption"])
        expected = expected_page(f)
        window = range(max(body_start, expected - NEAR_CAPTION_PAGES),
                       min(doc.page_count, expected + NEAR_CAPTION_PAGES + 1))
        found = None
        for i in window:
            cap = _page_caption(doc[i].get_text(), f["figure_number"])
            if cap and SequenceMatcher(None, want, _norm(cap)).ratio() \
                    >= NEAR_CAPTION_RATIO:
                found = (i, cap)
                break
        if found is None:
            for i in sorted(window, key=lambda i: abs(i - expected)):
                cap = _caption_block(doc[i], f["figure_number"])
                if cap:
                    found = (i, cap)
                    break
        if found:
            f["pdf_page_index"], cap = found
            if not _MATH_ALNUM.search(cap):
                f["caption"] = cap
            near_resolved += 1

    filled_offset = 0
    for f in figs:
        if f["pdf_page_index"] is None and f["printed_page"]:
            f["pdf_page_index"] = max(0, min(doc.page_count - 1, expected_page(f)))
            f["page_estimated"] = True
            filled_offset += 1

    # Fallback 2: monotonic interpolation between resolved neighbours.
    filled_interp = 0
    for i, f in enumerate(figs):
        if f["pdf_page_index"] is not None:
            continue
        prev_idx = next((figs[j]["pdf_page_index"] for j in range(i - 1, -1, -1)
                         if figs[j]["pdf_page_index"] is not None), None)
        nxt_idx = next((figs[j]["pdf_page_index"] for j in range(i + 1, len(figs))
                        if figs[j]["pdf_page_index"] is not None), None)
        if prev_idx is not None and nxt_idx is not None:
            f["pdf_page_index"] = (prev_idx + nxt_idx) // 2
        elif prev_idx is not None:
            f["pdf_page_index"] = prev_idx
        elif nxt_idx is not None:
            f["pdf_page_index"] = nxt_idx
        else:
            f["pdf_page_index"] = body_start
        f["page_estimated"] = True
        filled_interp += 1

    resolved = sum(1 for f in figs if not f.get("page_estimated"))
    return {
        "total": len(figs),
        "caption_resolved": resolved,
        "near_caption_resolved": near_resolved,
        "offset_filled": filled_offset,
        "interp_filled": filled_interp,
        "median_offset": offset,
    }


def _load_manifest(package: str) -> dict:
    mf = _MANIFEST_DIR / f"{package}.json"
    if not mf.exists():
        raise FileNotFoundError(f"No manifest for package '{package}': {mf}")
    return json.loads(mf.read_text(encoding="utf-8"))


def _repo_relative_pdf_path(manifest: dict) -> str:
    """Resolve the manifest pdf_path to a path relative to the repo root.

    Manifests store ``pdf_path`` relative to ``scripts/manifests/`` (e.g.
    ``../../docs/ufc_3_220_20_2025.pdf``). We re-express it relative to the
    repo root (e.g. ``docs/ufc_3_220_20_2025.pdf``) so the catalog is portable
    and resolvable from the installed package.
    """
    raw = manifest.get("pdf_path", "")
    abs_pdf = (_MANIFEST_DIR / raw).resolve()
    try:
        return abs_pdf.relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return abs_pdf.as_posix()


#: Lines a caption printed under a figure may run to (GEC-6 Figure 5-11's
#: takes three).
CAPTION_BLOCK_LINES = 5


#: The least gap (pt) before a label that opens a second caption on the same
#: row; words of running text are a space apart.
COLUMN_GAP = 18


def _row_parts(block: dict) -> list[list[tuple]]:
    """A text block's printed rows, each its lines as ``(left, right, text)``
    left to right; lines whose bottoms are within 3 pt are one row."""
    rows: list[list] = []
    for line in block.get("lines", []):
        text = "".join(s["text"] for s in line["spans"])
        x0, x1, bottom = line["bbox"][0], line["bbox"][2], line["bbox"][3]
        if rows and abs(rows[-1][0] - bottom) < 3:
            rows[-1][1].append((x0, x1, text))
        else:
            rows.append([bottom, [(x0, x1, text)]])
    return [sorted(parts) for _, parts in rows]


def _block_rows(block: dict) -> list[str]:
    """A PyMuPDF ``dict`` text block as the rows it prints, left to right.

    Some text layers put each word on a line of its own (FHWA-NHI-05-037's
    "Figure " "6-18. " "Example " ...); lines whose bottoms are within 3 pt
    are one printed row.
    """
    return [" ".join(t for _, _, t in parts) for parts in _row_parts(block)]


def _block_columns(block: dict, marker=None) -> list[list[str]]:
    """A text block as the columns of rows it prints.

    Two captions set side by side under two figures share a row
    (FHWA-NHI-05-037: "Figure 8-8. Bulldozer (photo courtesy of Komatsu).
    Figure 8-9. Motor grader" over "(photo courtesy of Caterpillar)"). A
    label that opens :data:`COLUMN_GAP` or more after the text before it
    starts a second column, which takes that row and the rows below it from
    the label's left edge on.
    """
    marker = marker or _FIG_MARKER
    split = None
    cols: list[list] = [[], []]
    for parts in _row_parts(block):
        if split is None:
            for j in range(1, len(parts)):
                rest = " ".join(t for _, _, t in parts[j:]).translate(_SMART)
                if parts[j][0] - parts[j - 1][1] >= COLUMN_GAP \
                        and marker.match(rest.lstrip()):
                    split = parts[j][0]
                    break
        if split is None:
            cols[0].append(parts)
            continue
        for k, side in enumerate(([p for p in parts if p[0] < split - 2],
                                  [p for p in parts if p[0] >= split - 2])):
            if side:
                cols[k].append(side)
    return [[" ".join(t for _, _, t in parts) for parts in col]
            for col in cols if col]


def _block_caption(block_text: str, marker) -> "tuple[str, str] | None":
    """``(figure_number, caption)`` when a text block opens with a figure's
    label and a caption, the way a caption printed under a figure does.

    None for a paragraph that only mentions a figure ("Figure 5-6 shows ...",
    "Figure 5-6(a) presents ..."), an entry with a dotted leader (a list of
    figures), a "(continued)" label or a label with no caption. A caption may
    open with its first part ("(a) Chart ..."). The caption is the block's
    lines after the label, up to the one that ends with a period, a blank
    line or the next label, at most :data:`CAPTION_BLOCK_LINES`.
    """
    text = block_text.translate(_SMART).lstrip()
    m = marker.match(text)
    if not m:
        return None
    lines: list[str] = []
    for line in re.sub(r"^[\s:.\-]+", "", text[m.end():]).split("\n"):
        line = line.strip()
        if not line:
            if lines:            # a blank line ends the caption
                break
            continue
        if marker.match(line):
            break
        lines.append(line)
        if line.endswith(".") or len(lines) == CAPTION_BLOCK_LINES:
            break
    # a word broken over two lines keeps its hyphen ("load-" "settlement")
    cap = re.sub(r"\s+", " ", re.sub(r"(?<=[A-Za-z])-\n", "-", "\n".join(lines)))
    if re.search(r"\.{3,}|\.{2,}\s*[\w-]*\d\s*$", cap):
        return None
    cap = cap.strip(" .-:")
    # "Figure 5-11: (a) Chart ..." is a caption; "Figure 10-6(a) presents ..."
    # and "Figure 4-2 (continued)" are not
    words = re.sub(r"^(?:\([a-z0-9]{1,3}\)[.:,]?\s*)+", "", cap)
    if len(cap) < 8 or not words[:1].isupper() \
            or re.match(r"(?i)cont(?:inued|'?d\b|\.)", words):
        return None
    return _fig_id(m.group(1)), cap


def _caption_block(page, figure_number: str) -> "str | None":
    """The caption of the text block on ``page`` that opens with the label of
    ``figure_number`` (see :func:`_block_caption`), or None."""
    want = _fig_id(figure_number)
    for block in page.get_text("dict")["blocks"]:
        if "lines" not in block:
            continue
        for rows in _block_columns(block):
            hit = _block_caption("\n".join(rows), _FIG_MARKER)
            if hit and hit[0] == want:
                return hit[1]
    return None


def _figs_from_body(doc, marker=None) -> list[dict]:
    """Extract figures by scanning the body for labeled captions — used when a
    reference has no parseable List of Figures (e.g. GEC-6, GEC-14). A figure's
    caption appears on its own page. The first text block that opens with the
    figure's label and a caption (see :func:`_block_caption`) gives the page and
    the caption, passing over a contents page where the figure's block also
    appears later; a figure with no such block takes the first page where
    ``Figure X-Y`` is followed by a substantial capitalized caption on the same
    or the next line. A sentence that mentions a figure as a line ends ("...
    as shown in Figure 5-12.  This is much simpler ...") is not a caption, so
    the block comes first. ``marker`` defaults to the dash/dot id pattern; pass
    ``_SEQ_MARKER`` for sequential refs.
    """
    marker = marker or _FIG_MARKER
    blocks: dict[str, list[dict]] = {}
    labels_on_page: dict[int, set] = {}
    by_text: dict[str, dict] = {}
    order = 0
    for i in range(doc.page_count):
        page = doc[i]
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:                        # an image block
                continue
            for rows in _block_columns(block, marker):
                for row in rows:
                    lm = marker.match(row.translate(_SMART).lstrip())
                    if lm:
                        labels_on_page.setdefault(i, set()).add(_fig_id(lm.group(1)))
                hit = _block_caption("\n".join(rows), marker)
                if hit:
                    order += 1
                    blocks.setdefault(hit[0], []).append(
                        {"figure_number": hit[0], "caption": hit[1],
                         "printed_page": None, "pdf_page_index": i,
                         "page_estimated": False, "_order": order})
        text = page.get_text()
        for m in marker.finditer(text):
            num = _fig_id(m.group(1))
            if num in by_text:
                continue
            tail = re.sub(r"^[\s:.\-]+", "", text[m.end():m.end() + 220])
            cap = re.split(r"[\r\n]", tail, maxsplit=1)[0]
            cap = re.sub(r"\.{2,}.*$", "", cap)            # drop dotted-leader tail
            cap = re.sub(r"\s+", " ", cap).strip(" .-:")
            # Caption pages read "Figure X-Y. <Capitalized caption>"; in-text refs
            # ("...in Figure X-Y") leave little/no caption after the marker.
            if len(cap) < 8 or not cap[:1].isupper():
                continue
            order += 1
            by_text[num] = {"figure_number": num, "caption": cap[:200],
                            "printed_page": None, "pdf_page_index": i,
                            "page_estimated": False, "_order": order}
    # A contents page looks like a page of captions; a figure whose caption
    # block sits on a page where three or more labels open lines, and on
    # another page too, takes the other page (GEC-14 B-1).
    by_block = {}
    for num, hits in blocks.items():
        own = [h for h in hits if len(labels_on_page[h["pdf_page_index"]]) < 3]
        by_block[num] = (own or hits)[0]
    figs = [by_block.get(num) or by_text[num] for num in {**by_text, **by_block}]
    figs.sort(key=lambda f: (f["pdf_page_index"], f["_order"]))
    for f in figs:
        del f["_order"]
    return figs


def _figs_from_pdf(pdf_abs, seq=False) -> list[dict]:
    """Parse + page-resolve every figure in one PDF (figs carry page_estimated).

    ``seq=True`` forces sequential body extraction (refs numbered "Figure 1",
    "Figure 2" with no chapter dash, e.g. GEC-4).
    """
    import fitz  # PyMuPDF
    doc = fitz.open(str(pdf_abs))
    try:
        if seq:
            return _figs_from_body(doc, _SEQ_MARKER)
        figs, lof_last = _parse_list_of_figures(doc)
        if figs:
            # Resolve from just after the figure list so a caption matches on its
            # real body page, not its LoF entry.
            body_start = (lof_last + 1) if lof_last is not None else 0
            _resolve_pages(doc, figs, body_start)
            return figs
        # No List of Figures: extract labeled captions from the body directly.
        return _figs_from_body(doc)
    finally:
        doc.close()


def build_catalog(package: str) -> dict:
    """Build and write ``figures_catalog.json`` for one package.

    Single-volume manifests carry a ``pdf_path``. Multi-volume manifests carry a
    ``volumes`` list of ``{pdf_path, volume}``; each figure is tagged with its own
    volume's ``pdf_path`` so read-off resolves to the right PDF, and with the
    volume's ``reference_id`` where the volume carries its own publication
    number (GEC-13 Vol II is FHWA-NHI-16-028; REF-31).
    """
    manifest = _load_manifest(package)
    volumes = manifest.get("volumes")

    if volumes:
        figs: list[dict] = []
        for vol in volumes:
            vrel = _repo_relative_pdf_path({"pdf_path": vol.get("pdf_path", "")})
            vabs = _REPO_ROOT / vrel
            if not vabs.exists():
                raise FileNotFoundError(f"PDF not found for '{package}': {vabs}")
            vfigs = _figs_from_pdf(vabs)
            for f in vfigs:
                f["pdf_path"] = vrel            # per-figure source PDF
                f["volume"] = vol.get("volume")
                if vol.get("reference_id"):     # a volume with its own number
                    f["reference_id"] = vol["reference_id"]
            figs.extend(vfigs)
        if not figs:
            raise ValueError(f"No figures parsed from any volume of '{package}'")
        pdf_rel = _repo_relative_pdf_path({"pdf_path": volumes[0].get("pdf_path", "")})
    else:
        pdf_rel = _repo_relative_pdf_path(manifest)
        pdf_abs = _REPO_ROOT / pdf_rel
        if not pdf_abs.exists():
            raise FileNotFoundError(f"PDF not found for '{package}': {pdf_abs}")
        figs = _figs_from_pdf(
            pdf_abs, seq=manifest.get("figure_numbering") == "sequential")
        if not figs:
            raise ValueError(f"No figures parsed from {pdf_abs}")

    enriched = _enrich_from_text(package, figs)

    out_figs = []
    for f in figs:
        rec = {
            "figure_number": f["figure_number"],
            "caption": f["caption"],
            "chapter": _chapter_of(f["figure_number"]),
            "pdf_page_index": f["pdf_page_index"],
            "printed_page": f["printed_page"],
            "page_estimated": bool(f.get("page_estimated", False)),
            "description": f.get("description", ""),
        }
        if f.get("pdf_path"):              # multi-volume per-figure override
            rec["pdf_path"] = f["pdf_path"]
        if f.get("volume") is not None:
            rec["volume"] = f["volume"]
        if f.get("reference_id"):          # volume printed under its own number
            rec["reference_id"] = f["reference_id"]
        out_figs.append(rec)

    resolved = sum(1 for f in out_figs if not f["page_estimated"])
    catalog = {
        "reference_id": manifest.get("reference_id", ""),
        "reference_title": manifest.get("reference_title", ""),
        "package": package,
        "volume": manifest.get("volume"),
        "pdf_path": pdf_rel,
        "figure_count": len(out_figs),
        "figures": out_figs,
    }

    for problem in caption_problems(catalog):
        print(f"[{package}] caption check: {problem}")

    out_path = _PACKAGE_DIR / package / "figures_catalog.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"[{package}] {len(out_figs)} figures (caption-resolved {resolved}, "
        f"estimated {len(out_figs) - resolved}; text-enriched {enriched}) -> {out_path}"
    )
    return catalog


def build_pack_catalog(pack_dir, pdf: "str | None" = None,
                       sequential: bool = False) -> dict:
    """Build and write a local reference pack's ``figures_catalog.json``
    (REF-64). ``pdf_path`` is the PDF's file name only, so no host path
    reaches the model; ``bbox`` and ``read_notes`` an existing catalog gives
    a figure are kept."""
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from geotech_references._packs import bare_file_name

    pack_dir = Path(pack_dir)
    meta = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    pid = meta.get("id") or pack_dir.name
    if pdf:  # a path given on the command line
        pdf_abs = Path(pdf) if Path(pdf).is_file() else pack_dir / Path(pdf).name
    else:  # pack.json names its PDFs by bare file name, in the pack folder
        listed = meta.get("pdf_files")
        name = next((p for p in (listed if isinstance(listed, list) else [])
                     if bare_file_name(p)), None)
        if not name:
            raise ValueError("give --pdf or list the PDF's file name in "
                             "pack.json pdf_files")
        pdf_abs = pack_dir / name
    if not pdf_abs.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_abs}")
    figs = _figs_from_pdf(pdf_abs, seq=sequential)
    if not figs:
        raise ValueError(f"No figures parsed from {pdf_abs}")
    enriched = _enrich_from_text(pid, figs, text_dir=pack_dir / "text")
    out_path = pack_dir / "figures_catalog.json"
    kept: dict[str, dict] = {}
    if out_path.is_file():
        try:
            for f in json.loads(out_path.read_text(encoding="utf-8")).get(
                    "figures", []):
                extra = {k: f[k] for k in ("bbox", "read_notes") if k in f}
                if extra:
                    kept[str(f.get("figure_number", "")).upper()] = extra
        except (OSError, json.JSONDecodeError, AttributeError):
            pass
    out_figs = []
    for f in figs:
        rec = {
            "figure_number": f["figure_number"],
            "caption": f["caption"],
            "chapter": _chapter_of(f["figure_number"]),
            "pdf_page_index": f["pdf_page_index"],
            "printed_page": f["printed_page"],
            "page_estimated": bool(f.get("page_estimated", False)),
            "description": f.get("description", ""),
        }
        rec.update(kept.get(f["figure_number"].upper(), {}))
        out_figs.append(rec)
    catalog = {
        "reference_id": meta.get("reference_id", ""),
        "reference_title": meta.get("reference_title", ""),
        "package": pid,
        "volume": meta.get("volume"),
        "pdf_path": pdf_abs.name,
        "figure_count": len(out_figs),
        "figures": out_figs,
    }
    for problem in caption_problems(catalog):
        print(f"[{pid}] caption check: {problem}")
    out_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    resolved = sum(1 for f in out_figs if not f["page_estimated"])
    print(f"[{pid}] {len(out_figs)} figures (caption-resolved {resolved}, "
          f"estimated {len(out_figs) - resolved}; text-enriched {enriched}) "
          f"-> {out_path}")
    return catalog


def caption_problems(catalog: dict) -> list[str]:
    """Captions that ran on into the page text (BACKLOG REF-27): longer than
    :data:`MAX_CAPTION_CHARS`, or carrying another figure's entry, a list
    heading or a running header. Empty when every caption is one caption."""
    out = []
    for f in catalog.get("figures", []):
        cap = f.get("caption") or ""
        why = []
        if len(cap) > MAX_CAPTION_CHARS:
            why.append(f"{len(cap):,} characters")
        m = _RUN_ON.search(cap)
        if m:
            why.append(f"runs on into {m.group(0)!r}")
        if why:
            out.append(f"Figure {f.get('figure_number')}: {'; '.join(why)}")
    return out


def _packages_with_pdf() -> list[str]:
    out = []
    for mf in sorted(_MANIFEST_DIR.glob("*.json")):
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("pdf_path") or data.get("volumes"):
            out.append(mf.stem)
    return out


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--pack":
        import argparse
        ap = argparse.ArgumentParser(prog="build_figure_catalog.py --pack")
        ap.add_argument("--pack", required=True)
        ap.add_argument("--pdf")
        ap.add_argument("--sequential", action="store_true",
                        help='figures numbered "Figure 1", "Figure 2"')
        args = ap.parse_args(argv)
        try:
            build_pack_catalog(args.pack, args.pdf, args.sequential)
        except Exception as e:  # noqa: BLE001
            print(f"[{args.pack}] FAILED: {type(e).__name__}: {e}")
            return 1
        return 0
    if not argv:
        print(__doc__)
        print("Packages with a manifest pdf_path:", ", ".join(_packages_with_pdf()))
        return 1
    targets = _packages_with_pdf() if argv == ["all"] else argv
    rc = 0
    for pkg in targets:
        try:
            build_catalog(pkg)
        except Exception as e:  # noqa: BLE001 — surface per-package failures, keep going
            print(f"[{pkg}] FAILED: {type(e).__name__}: {e}")
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
