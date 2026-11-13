"""Build a table catalog (tables_catalog.json) for a reference package.

The companion of ``scripts/build_figure_catalog.py`` for printed TABLES
(app BACKLOG REF-86 / REF-34). For a reference whose manifest carries a
``pdf_path`` (or ``volumes``), this script:

1. Reads the PDF's List of Tables (``LIST OF TABLES``, ``TABLES``, ``Table
   List``) into ``{table_number, caption, list_page}`` entries. A reference
   with no List of Tables takes its rows from the table captions printed in
   the body instead.
2. Finds each table's page: the first body page that prints ``Table <n>``
   followed by the table's caption (a caption is a line that opens with the
   label and a capitalised caption, or the label alone with the caption on
   the next line; "Table 5-1 shows ..." is a citation, not a caption). The
   caption kept is the one printed over the table, which may say more than
   the list does ("Overburden Drilling Methods (after Bruce, 1989)").
3. Lists the further pages of a table that continues: the pages straight
   after its first that print its label again ("Table 1-2 (continued)").
4. Says, where the library has one, the lookup function that codes the table
   (``implemented_in``: a public function named ``table_<n>...`` or whose
   docstring cites the table; each was confirmed by opening it, and the ones
   that cite another manual's table of the same number are listed in
   :data:`NOT_IMPLEMENTED_BY`) and the chapter-text sections whose ``tables``
   list names it (``text_sections``).
5. Writes ``geotech_references/<package>/tables_catalog.json``.

A row whose page the script cannot confirm (the caption's words are not on
the page's text layer: a scan, a table printed as a picture, a list caption
worded differently) keeps the page estimated from its printed page and is
reported; it was then read off the rendered page and its page, number and
caption written into :data:`CONFIG` (``rows_from_renders`` /
``page_from_render``), so that a re-run gives the same catalog. Scanned
manuals with no text layer (the AASHTO 1993 Guide) and the image pages of
UFC 3-220-07 have every row read off renders the same way.

No table's cells are typed in by this script: a row says where the table is,
not what it holds. The ``read_reference_figure`` style vision read-off of the
page gives the values.

Usage
-----
    python scripts/build_table_catalog.py dm7_1
    python scripts/build_table_catalog.py dm7_1 dm7_2
    python scripts/build_table_catalog.py all
    python scripts/build_table_catalog.py --audit audit.json dm7_1

``--audit FILE`` writes, per row, how its page was found (``how``), the
caption ratio and the candidate pages, for checking.

Requires: PyMuPDF.
"""

from __future__ import annotations

import importlib
import inspect
import json
import os
import pkgutil
import re
import statistics
import sys
from difflib import SequenceMatcher
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
_MANIFEST_DIR = _SCRIPTS_DIR / "manifests"
_PACKAGE_DIR = _REPO_ROOT / "geotech_references"
#: PDFs not in this checkout's docs/ (the Wood Handbook is not committed)
#: are read from the folders in GEOTECH_REFERENCES_DOCS (separated by
#: os.pathsep), the variable resolve_table_pdf reads; the catalog still
#: names ``docs/<file>``.
_FALLBACK_DOCS = [Path(p) for p in
                  os.environ.get("GEOTECH_REFERENCES_DOCS", "").split(os.pathsep)
                  if p]

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
from build_figure_catalog import _SMART, _norm, _load_manifest  # noqa: E402
from build_figure_catalog import _repo_relative_pdf_path  # noqa: E402

# ---------------------------------------------------------------------------
# Table numbers
# ---------------------------------------------------------------------------

_DASHES = "\u2010\u2011\u2012\u2013\u2014\u2212"
_SEP = rf"[ \t]*[-.{_DASHES}][ \t]*"
#: A printed table number: "5-3", "P-1", "B-29", "A-7-4", "C22-2", "E7-2",
#: "3.1a", "11.6-1", "D12", "4-1(a)", "1" (numbered through the manual).
NUM = (rf"(?:[A-Z]{{1,2}}\d{{0,3}}{_SEP}\d+(?:{_SEP}\d+)*"
       rf"|[A-Z]{{1,2}}\d{{1,3}}"
       rf"|\d+(?:{_SEP}\d+)*)"
       rf"(?:[a-zA-Z](?![A-Za-z]))?(?:[ \t]?\([a-z]\))?")
_NUM_RX = re.compile(NUM)
#: A body line that opens with a table label.
_CAP_LINE = re.compile(rf"^\W{{0,3}}(?:Table|TABLE|table)[ \t]+({NUM})(?![\d])(.*)$")
#: The label opening a List of Tables entry ("Table 5-3 ...").
_LIST_MARKER = re.compile(rf"(?:Table|TABLE)[ \t]+({NUM})(?![\d])(?![ \t]*[,;)])")
#: A bare table number on a line of its own (lists that print the number in
#: a column with no "Table": NHI-05-037, NHI-06-088/089).
_BARE_NUM = re.compile(rf"^[ \t]*({NUM})[ \t]*$")
#: A dotted leader and the page it leads to ("..... 4-27", "... 2 - 9").
_LEADER = re.compile(
    rf"\.{{2,}}[ .]*((?:(?:[A-Z]{{1,2}}\d{{0,2}}|\d{{1,2}})[ \t]*[-{_DASHES}][ \t]*)?"
    rf"\d{{1,4}})\b")
_CONTINUED = re.compile(
    r"(?i)^[(\[]?\s*(?:cont(?:inued|['\u2019]?d|\.)?|concluded)\b|"
    r"[(\[\u2013\u2014-]\s*(?:cont(?:inued|['\u2019]?d|\.)?|concluded)\s*[)\]]?\s*\.?$")


def norm_number(raw: str) -> str:
    """A table number as filed: dashes as '-', no spaces, a part letter
    printed in brackets as the plain letter ('4-1(a)' -> '4-1a'), the form
    the figure catalogs give one."""
    s = re.sub(rf"[{_DASHES}]", "-", raw.translate(_SMART))
    s = re.sub(r"\s+", "", s)
    return re.sub(r"\(([a-z])\)$", r"\1", s)


def number_key(num: str) -> str:
    """A table number for comparing: upper case, '.' and '-' alike."""
    return re.sub(r"[-.]", "-", norm_number(num)).upper()


def chapter_of(num: str, prologue: str = "P"):
    """The chapter a table number is filed under: 4 for '4-12' or '4.3a',
    0 for a prologue's 'P-1', None for an appendix letter or a number
    printed through the manual."""
    m = re.match(r"(\d+)[-.]", num)
    if m:
        return int(m.group(1))
    if prologue and re.match(rf"{prologue}-\d", num):
        return 0
    return None


# ---------------------------------------------------------------------------
# Page text
# ---------------------------------------------------------------------------

def page_lines(page) -> list[dict]:
    """A page's printed lines in reading order: ``text``, ``font``, ``size``,
    ``bold``, ``block`` (index of its text block), ``first`` (it opens its
    block). Lines of one block whose bottoms are within 2 pt are one line
    (some text layers set each word as a line)."""
    out: list[dict] = []
    for bi, block in enumerate(page.get_text("dict")["blocks"]):
        if "lines" not in block:
            continue
        rows: list[list] = []
        for line in block["lines"]:
            spans = [s for s in line["spans"] if s["text"].strip()]
            if not spans:
                continue
            bottom = line["bbox"][3]
            if rows and abs(rows[-1][0] - bottom) < 2:
                rows[-1][1].extend(spans)
            else:
                rows.append([bottom, list(spans)])
        for k, (_, spans) in enumerate(rows):
            spans.sort(key=lambda s: s["bbox"][0])
            text = ""
            for s in spans:
                if text and not text.endswith(" ") and not s["text"].startswith(" "):
                    text += " "
                text += s["text"]
            text = text.translate(_SMART)
            main = max(spans, key=lambda s: len(s["text"].strip()))
            gaps = [b["bbox"][0] - a["bbox"][2] for a, b in zip(spans, spans[1:])]
            out.append({
                "text": re.sub(r"[ \t]+", " ", text).strip(),
                "font": main["font"], "size": round(main["size"], 1),
                "bold": bool(main["flags"] & 16) or "bold" in main["font"].lower(),
                "block": bi, "first": k == 0,
                "y": spans[0]["bbox"][1],
                # words set apart in columns: a table's row, not a caption's
                "gappy": bool(gaps) and max(gaps) > 14,
            })
    return out


def _starts_lower(s: str) -> bool:
    """A line that goes on a sentence ("shows ...", "and ..."), not a
    caption; a caption may open with a symbol in lower case ("p-Multipliers
    ...", "t-z Curves")."""
    if not s or not (s[0].isascii() and s[0].islower()):
        return False
    return not re.match(r"[a-z]{1,3}[-–/'][A-Za-z0-9]", s)


def caption_candidates(lines: list[dict]) -> list[dict]:
    """The lines of one page that open a table caption: ``number``, the
    caption text that follows (``lines``, the label's line rest first, then
    up to five further lines), ``continued``, ``first`` (opens its block)."""
    out = []
    for i, ln in enumerate(lines):
        m = _CAP_LINE.match(ln["text"])
        if not m:
            continue
        rest = m.group(2)
        number = norm_number(m.group(1))
        if re.search(r"\.{4,}", rest):           # a contents line
            continue
        # a continued label whose dash the text layer drops ("Table 4 2
        # (cont.)", UFS 3-220-10 p. 186)
        gap = re.match(r"^[ \t]+(\d{1,3})[ \t]*(\((?:cont|continued)\b.*)$", rest,
                       re.I)
        if gap and re.fullmatch(r"\d+", number):
            number, rest = f"{number}-{gap.group(1)}", " " + gap.group(2)
        s = rest.strip()
        s = re.sub(rf"^[\s.:{_DASHES}-]+", "", s).strip()
        continued = bool(_CONTINUED.search(s))
        if s and not continued:
            if s[0] in ",;)" or _starts_lower(s) or s.startswith("("):
                continue                           # "Table 5-1 shows ..."
            if re.match(r"(?:and|or|to|of|in|through)\b", s):
                continue
        follow = [x for x in lines[i + 1:i + 7]]
        if not s:
            nxt = next((x["text"] for x in follow if x["text"]), "")
            if not nxt or _starts_lower(nxt) or not (
                    nxt[0].isupper() or nxt[0].isdigit()
                    or nxt[0] in "(\"'" or not nxt[0].isascii()):
                continue
            again = _CAP_LINE.match(nxt)
            if again and number_key(again.group(1)) == number_key(m.group(1)):
                continue        # a bare label the text layer repeats
        out.append({
            "number": number,
            "rest": s,
            "follow": [x["text"] for x in follow],
            "follow_font": [(x["font"], x["size"], x["block"], x["gappy"])
                            for x in follow],
            "font": (ln["font"], ln["size"], ln["block"]),
            "continued": continued,
            "first": ln["first"],
            "bold": ln["bold"],
            "line": i,
        })
    return out


def caption_text(cand: dict, want: str | None = None) -> tuple[str, float]:
    """The caption a candidate prints and how well it matches ``want`` (the
    list's caption; 1.0 when the page prints the list's caption whole).

    With ``want`` the caption is the fewest lines that hold the list's
    caption from its start, run on to close a bracket left open; without it,
    the label line's rest, or the next line when the rest is empty, run on
    over the lines in the same font and block until one ends with a period
    (at most four)."""
    parts = ([cand["rest"]] if cand["rest"] else []) + cand["follow"]
    fonts = ([cand["font"]] if cand["rest"] else []) + cand["follow_font"]
    if not parts:
        return "", 0.0
    if want:
        nw = _norm(want)
        best = (0.0, parts[0])
        for k in range(1, len(parts) + 1):
            text = " ".join(parts[:k])
            nt = _norm(text)
            if nw and nt.startswith(nw):
                j = k
                while j < len(parts) and text.count("(") > text.count(")") \
                        and j < k + 2:
                    j += 1
                    text = " ".join(parts[:j])
                return _tidy(text), 1.0
            r = SequenceMatcher(None, nw, nt).ratio() if nw else 0.0
            if r > best[0]:
                best = (r, text)
            if len(nt) > len(nw) + 60:
                break
        return _tidy(best[1]), round(best[0], 3)
    text = parts[0]
    font0 = fonts[0]
    k = 1
    while k < len(parts) and k < 4 and not text.rstrip().endswith(".") \
            and fonts[k][:2] == font0[:2] and fonts[k][2] == font0[2] \
            and not (len(fonts[k]) > 3 and fonts[k][3]) \
            and not _CAP_LINE.match(parts[k]):
        text += " " + parts[k]
        k += 1
    return _tidy(text), 0.0


def _tidy(text: str) -> str:
    text = re.sub(r"(?<=[A-Za-z])- (?=[a-z])", "-", text)   # "load- settlement"
    # a UFC change mark around revised words ("\4\ ... /4/")
    text = re.sub(r"\\\d{1,2}\\|/\d{1,2}/", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s*\(\s*cont(?:inued|'d|\.)?\s*\)\s*$", "", text, flags=re.I)
    return text.strip(" .:-")


# ---------------------------------------------------------------------------
# The List of Tables
# ---------------------------------------------------------------------------

_LIST_HEADING = re.compile(
    r"(?i)^\s*(?:LIST OF TABLES|TABLES|TABLE LIST)(?:\s*[-\u2013\u2014(].*)?\s*$")
_LIST_END = re.compile(
    r"(?i)^\s*(?:LIST OF (?:FIGURES|ILLUSTRATIONS|SYMBOLS|ABBREVIATIONS|ACRONYMS|"
    r"APPENDICES|EQUATIONS|PHOTOS|EXHIBITS)|FIGURES|FIGURE LIST|ACRONYMS(?: AND "
    r"ABBREVIATIONS)?|ABBREVIATIONS|CHAPTER\s+1|PREFACE|FOREWORD|EXECUTIVE SUMMARY)\s*$")


def _noise(line: str, extra: "re.Pattern | None") -> bool:
    s = line.strip()
    if not s:
        return True
    if extra is not None and extra.search(s):
        return True
    if re.match(r"(?i)^(?:UF[SC]|TM)\s+\d-", s):
        return True
    if re.match(r"(?i)^\d{1,2}\s+[A-Za-z]+\s+\d{4}$", s):        # 16 January 2026
        return True
    if re.match(r"(?i)^(?:January|February|March|April|May|June|July|August|"
                r"September|October|November|December)\s+\d{4}$", s):
        return True
    if re.match(r"(?i)^(?:page\s+)?[ivxlcdm]{1,7}(?:\s*-\s*[ivxlcdm]{1,6})?$", s):
        return True
    if re.match(r"(?i)^(?:table|no\.?|number|title|caption|page|table\s+page)"
                r"(?:\s+(?:title|caption|page))*\s*$", s):
        return True
    if re.match(r"(?i)^list of tables\b", s) or re.match(r"(?i)^tables?$", s):
        return True
    return False


def find_list_runs(doc, cfg: dict) -> list[list[int]]:
    """The PDF pages of each List of Tables, one run per list:
    ``cfg["list_pages"]`` when the reference names them (a ``(first,
    last)`` pair or a list of pairs), else the page with its heading in the
    first 80 and the pages after it that carry table entries; with
    ``list_all`` every list in the PDF (GEC-13 prints one per chapter)."""
    if "list_pages" in cfg:
        lp = cfg["list_pages"]
        if not lp:
            return []
        ranges = lp if isinstance(lp[0], (list, tuple)) else [lp]
        return [list(range(a, b + 1)) for a, b in ranges]
    runs: list[list[int]] = []
    last = doc.page_count if cfg.get("list_all") else min(80, doc.page_count)
    i = 0
    while i < last:
        if _is_list_start(doc[i].get_text().splitlines()):
            run = _list_run_from(doc, i)
            runs.append(run)
            if not cfg.get("list_all"):
                break
            i = run[-1] + 1
        else:
            i += 1
    return runs


def _is_list_start(lines: list[str]) -> bool:
    for k, ln in enumerate(lines):
        if _LIST_HEADING.match(ln):
            rest = "\n".join(lines[k + 1:k + 30])
            if _LIST_MARKER.search(rest) or re.search(
                    rf"(?m)^[ \t]*{NUM}[ \t]*$", rest):
                return True
    return False


def _list_run_from(doc, start: int) -> list[int]:
    pages = [start]
    for i in range(start + 1, min(start + 20, doc.page_count)):
        t = doc[i].get_text()
        if _LIST_HEADING.search(t) is None and not re.search(r"\.{4,}", t):
            break
        first = [ln for ln in t.splitlines() if ln.strip()][:12]
        if any(_LIST_END.match(ln) for ln in first) and not _LIST_MARKER.search(
                "\n".join(t.splitlines()[:6])):
            break
        if not (_LIST_MARKER.search(t) or re.search(rf"(?m)^[ \t]*{NUM}[ \t]*$", t)):
            break
        pages.append(i)
    return pages


def parse_list(doc, pages: list[int], cfg: dict) -> list[dict]:
    """``[{table_number, caption, list_page}]`` from the List of Tables
    pages, in printed order."""
    if not pages:
        return []
    extra = re.compile(cfg["list_noise"]) if cfg.get("list_noise") else None
    kept: list[str] = []
    started = False
    mode = cfg.get("list_mode", "prefix")
    if mode == "bare":
        # each printed line with where it starts across the page: a bare
        # number at the right is a page, at the left a table's number
        texts, right = {}, set()
        for i in pages:
            texts[i] = []
            width = doc[i].rect.width
            for block in doc[i].get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    t = "".join(s["text"] for s in line["spans"]).translate(_SMART)
                    if not t.strip():
                        continue
                    if line["bbox"][0] > 0.55 * width and _BARE_NUM.match(t):
                        t = "\x00" + t.strip()      # marked as a page
                    texts[i].append(t)
    else:
        texts = {i: [ln.translate(_SMART) for ln in doc[i].get_text().splitlines()]
                 for i in pages}
    # a line printed on every page of the list is its running head
    running: set = set()
    if len(pages) > 1:
        running = set.intersection(*({ln.strip() for ln in texts[i] if ln.strip()}
                                     for i in pages))
        running = {ln for ln in running if not _LIST_MARKER.match(ln)
                   and not _BARE_NUM.match(ln)}
    for i in pages:
        lines = [ln for ln in texts[i] if ln.strip() not in running]
        for ln in lines:
            if not started:
                if _LIST_HEADING.match(ln) or "list_pages" in cfg:
                    started = True
                    if _LIST_HEADING.match(ln):
                        continue
                else:
                    continue
            if _LIST_END.match(ln) and kept:
                started = None
                break
            if _noise(ln, extra):
                continue
            kept.append(ln.strip())
        if started is None:
            break
    mode = cfg.get("list_mode", "prefix")
    if mode == "bare":
        return _parse_bare(kept)
    blob = "\n".join(kept)
    # an entry opens a line or follows the previous entry's leader and page;
    # "Replacement for ASCE 7-22 Table 12.2-1" inside a caption is a citation
    # as is one on the line after a caption that wraps after "per" ("...
    # method per" / "Table 7-4 .... 379", EM 1110-1-1905 Table C-7b)
    markers = [m for m in _LIST_MARKER.finditer(blob)
               if re.search(r"(?:^|\n|\.{2,}[ .]*[\w-]*\d)[ \t]*$",
                            blob[:m.start()][-20:] or "\n")
               and not re.search(r"\b(?:per|in|of|see|from|after|using|with)[ \t]*\n[ \t]*$",
                                 blob[:m.start()][-30:])]
    out = []
    for k, m in enumerate(markers):
        end = markers[k + 1].start() if k + 1 < len(markers) else len(blob)
        cap, token = _split_list_entry(blob[m.end():end])
        if _CONTINUED.search(cap[:12]):
            continue            # the list naming a table's continued page
        out.append({"table_number": norm_number(m.group(1)), "caption": cap,
                    "list_page": token})
    return out


def _split_list_entry(seg: str) -> tuple[str, "str | None"]:
    """``(caption, page token)`` of one list entry: the caption up to its
    dotted leader, the page the leader leads to; with no leader, a page
    number or chapter-page number ending the entry."""
    seg = re.sub(r"\s+", " ", seg).strip()
    m = _LEADER.search(seg)
    token = None
    if m:
        token = re.sub(r"\s+", "", m.group(1))
        token = re.sub(rf"[{_DASHES}]", "-", token)
        seg = seg[:m.start()]
    else:
        m2 = re.search(rf"(?<![\w-])((?:[A-Z]{{1,2}}\d{{0,2}}\s*[-{_DASHES}]\s*)?\d{{1,4}})\s*$", seg)
        # a page number glued to the caption's last word ("Unit Weight455")
        m2 = m2 or re.search(r"(?<=[a-z])(\d{1,4})\s*$", seg)
        if m2 and m2.start() > 0:
            token = re.sub(rf"\s+|[{_DASHES}]", lambda x: "-" if x.group(0).strip() else "", m2.group(1))
            seg = seg[:m2.start()]
    cap = re.sub(r"\.{2,}", "", seg)
    cap = re.sub(r"\s+", " ", cap).strip(" .:-\u2013")
    return cap, token


def _parse_bare(lines: list[str]) -> list[dict]:
    """A list that prints the number, the caption and the page each on lines
    of their own (NHI-05-037: "1-1" / caption / "1-18"), or the caption and
    its page on one line (NHI-06-088: "1-1" / "caption ..... 1-9")."""
    out: list[dict] = []
    cur = None
    for ln in lines:
        if ln.startswith("\x00"):                 # a page number at the right
            if cur is not None and cur["list_page"] is None:
                cur["list_page"] = norm_number(ln[1:])
            continue
        bare = _BARE_NUM.match(ln)
        if bare:
            if cur is not None:
                out.append(cur)
            cur = {"table_number": norm_number(bare.group(1)), "_cap": [],
                   "list_page": None}
            continue
        if cur is None or cur["list_page"] is not None:
            continue            # a running head after an entry's page
        cur["_cap"].append(ln)
        m = _LEADER.search(ln)
        if m:
            cur["list_page"] = norm_number(m.group(1))
    if cur is not None:
        out.append(cur)
    for e in out:
        cap = re.sub(r"\.{2,}.*$", "", " ".join(e.pop("_cap")))
        cap = re.sub(r"\s+", " ", cap).strip(" .:-")
        # a page number printed on the caption's last line ("... layers 5-64")
        e["caption"] = re.sub(r"\s+(?:\d{1,2}|[A-Z])-\d{1,3}$", "", cap).strip(" .:-")
    # a number with no caption is a page the list printed at the left
    return [e for e in out if e["caption"]]


# ---------------------------------------------------------------------------
# Per-reference settings (found by reading each PDF's lists and pages)
# ---------------------------------------------------------------------------

#: Settings a reference needs beyond the defaults:
#:   list_pages        (first, last) PDF pages of its List of Tables, or None
#:                     for a reference that prints none
#:   list_mode         "prefix" (entries open "Table <n>") or "bare"
#:   list_noise        a regex for running heads the list pages carry
#:   body_start        first PDF page of the body (default: after the list)
#:   body_end          last PDF page searched (exclusive)
#:   block_start_only  a caption must open its text block (references whose
#:                     rows come from the body)
#:   numbers           a regex a table number must match (keeps another
#:                     manual's "Table 10.4.2-1" cited in the text out)
#:   page_from_render  {number: pdf_page_index} read off the rendered page
#:   caption_from_render {number: caption} read off the rendered page
#:   rows_from_renders [{table_number, caption, pdf_page_index, printed_page}]
#:                     for pages with no text layer
#:   drop              numbers a list or body scan gives that are not tables
#:                     of this manual
#:   chapter_starts    {chapter: first pdf page} for tables numbered through
#:                     the manual
CONFIG: dict[str, dict] = {
    # every chapter opens with its own contents and List of Tables
    # Table 9-8 (section 9.3.3.2.2) is typed cell for cell and right on the page
    # (read on the render 2026-11-13); the cell check cannot read its
    # superscripts, so it is kept as text (``text_by_render``).
    "gec_13": {"list_all": True, "text_by_render": {"9-8": "9.3.3.2.2"}},
    # DM 7.1 (read against the renders 2026-11-13): chapters 5 to 8 type
    # their printed tables into the chapter text (REF-97). Three are right
    # on the page, but the cell check cannot count them: Table 6-2 is
    # drawings (its three rows are typed as text), Table 6-12's text layer
    # splits D15 and D85 from their subscripts, and the text layer of
    # printed p. 441 has "Table 8-16." as a citation in the body of the
    # text, which the scan takes for the caption (the caption printed over
    # the table is the list's). Table 6-4 runs on to PDF page 326 (printed
    # p. 299), where its shell column continues; Table 4-3 (REF-116) has
    # its values on PDF pages 222 and 223. Chapters 1 to 4 type theirs too
    # (REF-97); two are right on the page but not countable: Table 1-3 has
    # no numbers and two-letter labels, and Table 4-13's text layer reads
    # the sigma-1 subscript as a cell. Table 4-6 also prints on PDF page
    # 229 (printed p. 202: note 5 and the drawing).
    "dm7_1": {
        "text_by_render": {"6-2": "6-2.6.2", "6-12": "6-5.3.1",
                           "8-16": "8-4.2", "1-3": "1-3.2.2.1",
                           "4-13": "4-6.3"},
        "caption_from_render": {
            "8-16": "Compressibility Data for Six Sands (Been et al. 1987)"},
        "pages_from_render": {"6-4": [325, 326], "4-3": [222, 223],
                              "4-6": [228, 229]}},
    # Table 6-38 is printed on PDF page 503 (printed 466) under Figure 6-25;
    # the scan took a page that cites it (read off the render)
    "dm7_2": {"page_from_render": {"6-38": 503}},
    # The List of Tables gives 16-3 to "Proposed CSL Rating Criteria (DFI,
    # 2018)", which is not printed (p. 16-4 refers the reader to DFI), and
    # 16-4 to the TIP table, which is printed as TABLE 16-3 (PDF page 500,
    # p. 16-11; read off the render). The stored text files it as 16-3.
    # Tables 18-3 and 13-1: section 18.4 leaves out the Quantity column,
    # section 13.1.2 paraphrases (read 2026-11-12)
    # Rows the cell check fails that hold every cell, each read against its
    # render (2026-11-12) and kept as text (``text_by_render``): subscripts
    # the check cannot count (Q10), the next heading taken into the table,
    # tables printed as pictures, worded footnote marks.
    "gec_10": {"text_by_render": {"10-4": "10.5.2", "C-1": "C.1"},
               "values": {"18-3": ("page", None), "13-1": ("page", None)},
               "notes": {
                   "18-3": "Section 18.4 types this table's projects, average "
                           "unit prices and numbers of projects but not its "
                           "Quantity (linear feet) column; read the "
                           "quantities off the page.",
                   "13-1": "Section 13.1.2 paraphrases this table's benefits "
                           "and limitations; read its wording off the page."},
               "drop": ["16-3", "16-4"], "rows_from_renders": [
        {"table_number": "16-3", "chapter": 16,
         "caption": "DRILLED SHAFT INTEGRITY FEATURES DETERMINED BY TIP",
         "pdf_page_index": 500, "printed_page": "16-11",
         "note": ("Printed as TABLE 16-3. The List of Tables numbers it 16-4 "
                  "and lists as 16-3 'Proposed CSL Rating Criteria (DFI, "
                  "2018)', which the manual does not print (p. 16-4 refers "
                  "the reader to DFI).")}]},
    # Vol I: "Table 11.5.6-1" and "Table 10.6.3.1.2a-1" are AASHTO tables
    # named inside captions. Vol II: p. 21 is the contents' line for Vol I's
    # Table 5-1; the specification's "Table4" (no space; PDF page 115,
    # p. 10-28) is read off the render; Table E0's caption ran into its head
    "gec_11": {"volumes": [
        {"drop": ["11.5.6", "10.6.3.1.2a"],
         # the table is below the column the check reads (render)
         "text_by_render": {"4-6": "4.4.6.c"},
         # the text layer gives the phi as a private-use character
         "caption_from_render": {
             "4-7": "Resistance Factors, φ, for Tensile and Pullout "
                    "Resistance for MSE Walls (after Table 11.5.6-1, "
                    "AASHTO {2007})"}},
        {"drop": ["5-1"],
         "caption_from_render": {"E0": "Summary of Example Problems"},
         # Tables 1, 1.1 ("NOTES FOR TABLE 1") and 4 are printed in the
         # example specification of section 10.9; section 10.9 restates
         # part of Table 1 (read 2026-11-12)
         "chapter_from_render": {"1": 10, "1.1": 10, "4": 10},
         # the page after Table E.1-1 is the example's text, whose step
         # headings repeat the table's lines (render 2026-11-12)
         "pages_from_render": {"E.1-1": [243]},
         "section_from_render": {"1.1": "10.9"},
         "values": {"1": ("page", None)},
         "notes": {"1": "Section 10.9 restates some of this table's values "
                        "in short form; its Limit State and Note columns, "
                        "the limiting eccentricity and the coefficient of "
                        "sliding friction are not typed; read the table off "
                        "the page."},
         "rows_from_renders": [
             {"table_number": "4", "chapter": None,
              "caption": "ELECTROCHEMICAL REQUIREMENTS FOR GEOSYNTHETIC "
                         "REINFORCEMENTS",
              "pdf_page_index": 115, "printed_page": "10-28"}]}]},
    # Rows the scan took from a sentence or a front-matter table that cites
    # the number, each checked on the render (2026-11-12): dropped where
    # the manual does not print the table, moved where it prints it on
    # another page.
    # GSA: "Table 10-3 of ASCE 41 [10]" and the like are ASCE 41's tables
    "gsa_collapse": {"drop": ["10-3", "10-1", "9-3"]},
    # "Table 1604.5 [Replacement]" heads the paragraph that replaces the
    # IBC table with the UFC's Table 2-2 (1607.1 with Table E-1)
    "ufc_structural": {"drop": ["1604.5", "1607.1"]},
    # the text layer drops the dash of "Table 21 1" (PDF page 140)
    "ufc_pavement": {"page_from_render": {"21-1": 140},
                     "caption_from_render": {
                         "21-1": "Gradation for Aggregate Surface Courses"}},
    # the List of Tables gives 2-13 to 2-16 the captions of other tables;
    # the pages print them as below (and Table 2-15's lookup is the SMA
    # gradation the page prints)
    "ufc_flexible_practice": {
        "caption_from_render": {
            "2-13": "Properties of Cellulose Fibers (after NAPA 1999)",
            "2-14": "Properties of Mineral Fibers (after NAPA 1999)",
            "2-15": "SMA Gradation Guideline (after NAPA 1999*)",
            "2-16": "Recommended SMA Coarse and Fine Aggregate Properties "
                    "(after NAPA 1999)"},
        "notes": {n: f"The List of Tables gives Table {n} the caption "
                     f"'{c}'; the page prints the caption above."
                  for n, c in (("2-13", "SMA Gradation Guideline"),
                               ("2-14", "Recommended SMA Coarse and Fine "
                                        "Aggregate Properties"),
                               ("2-15", "Properties of Cellulose Fibers"),
                               ("2-16", "Properties of Mineral Fibers"))}},
    # 7-13 found on its render; the list's Table 7-23 is printed only as
    # 7-23a (SI) and 7-23b (U.S. customary), each a row of its own
    "fhwa_pavements": {"list_mode": "bare", "list_pages": (16, 20),
                       "list_noise": r"^Geotechnical Aspects of Pavements",
                       "page_from_render": {"7-13": 417},
                       # Table 5-31 runs on to p. 5-49 (render); its lookup
                       # codes only the Commentary row's factors
                       "pages_from_render": {"5-31": [225, 226]},
                       "values": {"5-31": ("page", None)},
                       "notes": {"5-31": (
                           "equations.backcalculated_to_design_modulus codes "
                           "the factors of the table's Commentary row (p. "
                           "5-49); its other rows are read off the pages.")},
                       "drop": ["7-23"]},
    "em_2107": {"page_from_render": {"4.2": 39}},
    # cells read against the renders (2026-11-12): Table 10-4's footnote
    # marks are the numbers the check misses
    "micropile": {"text_by_render": {"5-1": "5.1", "10-4": "10.3.1"},
                  "notes": {"5-1": "Section 5.1 lists each step in fewer "
                                   "words; the page has its wording."}},
    # Table 5-3's notes (the base and ground inclinations) are printed at
    # the top of the next page, above Table 5-4 (render 2026-11-12)
    "em_1905": {"pages_from_render": {"5-3": [122, 123]}},
    # the page prints another caption than the List of Tables
    "gec_5": {"caption_from_render": {
        "5-15": "Typical Numerical Corrosivity Scoring System"},
        # 4-13, 9-5, 9-6 and 12-5 are printed as pictures (renders)
        "text_by_render": {
            "4-13": "4.16.2", "6-10": "6.14.1", "7-2": "7.4.5",
            "7-6": "7.6.9", "7-7": "7.8", "9-4": "9.4.5", "9-5": "9.6.3",
            "9-6": "9.6.3", "9-10": "9.8", "12-3": "12.4.2",
            "12-4": "12.4.2", "12-5": "12.4.2"},
        "notes": {"5-15": "The List of Tables gives the caption 'Numerical "
                          "Corrosivity Scoring (from Earth Contact "
                          "Products)'; the page prints the caption above.",
                  "9-10": "The footnote's second sentence, that mi will be "
                          "significantly different if failure occurs along "
                          "a weakness plane, is not in Section 9.8's entry."}},
    "gec_6": {"text_by_render": {"4-1": "4.3.1", "5-2": "5.2.3.1",
                                 "5-3": "5.2.3.2", "5-5": "5.2.3.5",
                                 "5-11": "5.3.3", "6-2": "6.3"},
              "page_from_render": {"5-3": 62, "B5-1": 242},
              "caption_from_render": {
                  "5-3": "CORRECTION FACTOR FOR LOCATION",
                  "B5-1": "LOADS AT COLUMN BASE",
                  "B2-3": "STRESS INCREASE DUE TO BRIDGE LOADING"}},
    # "Table 18–" ends a line before "3. Charring rate data ..."; "all data
    # from Table 5–3" (printed as 5-3a and 5-3b) and "(Table 19–3)" cite
    "wood_handbook": {
        "drop": ["5-3", "18"],
        "page_from_render": {"19-3": 473},
        "caption_from_render": {
            "19-3": "Coefficients of linear thermal expansion per degree "
                    "Celsius of wood, hydrolyzed wood, and paper products"},
        "rows_from_renders": [
            {"table_number": "18-3", "chapter": 18,
             "caption": "Charring rate data for selected wood species",
             "pdf_page_index": 455, "printed_page": None}]},
    # p. 32 is a table of the provisions' changes that cites ASCE 7's
    # Tables 12.3-2 and 12.6-1 (the latter eliminated, not printed);
    # "Table 15.4-2" on p. 410 is commentary citing ASCE 7
    "fema_p2082": {"drop": ["12.6-1", "15.4-2"],
                   "not_printed": {"1.5-2": "ASCE 7's Table 1.5-2, which "
                                            "section 11.5 cites"},
                   "page_from_render": {"12.3-2": 66},
                   # page labels the text layer's reading misses (a cell or
                   # an equation number read first; renders 2026-11-12)
                   "printed_from_render": {("12.14-1", 75): "38",
                                           ("19.3-3", 121): "84"},
                   # Table C17.2-5's rows 27.7 to 39.5 are printed at the top
                   # of the next page, with no heading (render 2026-11-12)
                   "pages_from_render": {"C17.2-5": [483, 484]},
                   "caption_from_render": {
                       "12.3-2": "Vertical Structural Irregularities",
                       # the text layer drops the italic D_rd and D_m
                       "C17.2-4": "Permanent Residual Displacement, Drd, for "
                                  "a Maximum Earthquake Displacement, Dm, of "
                                  "10 in. (250 mm)",
                       "C17.2-5": "Permanent Residual Displacements, Drd, "
                                  "for a Maximum Earthquake Displacement, "
                                  "Dm, of 20 in. (500 mm)",
                       # the text layer gives these symbols as private-use
                       # characters, or not at all (renders 2026-11-12)
                       "19.3-2": "Effective Shear Modulus Ratio (G/G0)",
                       "19.3-3": "Soil Hysteretic Damping Ratio, βs",
                       "C16.4-4": "Required Ratios of λ/φ to Achieve the 10% "
                                  "Collapse Probability Objective",
                       "C22-7": "Examples of 84th-percentile ground motions "
                                "(abbreviated 84th GM) calculated using "
                                "epsilons from hazard deaggregations (ε) and "
                                "the corresponding probabilistic ground "
                                "motions, at a site class BC location in San "
                                "Jose, California"}},
    # section 4.9's entry for Table 4.9 describes its column heads and
    # names the lookup, without the values
    # Table 3.1a: section 3.3.3 sums it up in a sentence (read 2026-11-12)
    "gec_7": {"values": {"4.9": ("lookup",
                                 "tables.table_4_9_site_coefficient_fpga"),
                         "3.1a": ("page", None)},
              "notes": {"3.1a": "Section 3.3.3 summarizes this table in a "
                                "sentence; read its entries off the page."}},
    # prints no numbered table (its one "Table" line is "Table of Contents")
    "gec_14": {"no_tables": True},
    # Appendix B pages whose label the text layer does not hold (renders
    # 2026-11-12)
    "gec_8": {"printed_from_render": {("B.2", 286): "B-8", ("B.3", 287): "B-9"}},
    # A scan with no text layer: the tables a section lists or a lookup
    # codes, each placed and its caption read off the render (2026-11-12);
    # the coded functions give these PDF pages, 0-based, and the renders
    # confirm them. Tables the guide prints that neither lists nor codes
    # are not rows.
    "aashto_1993": {"rows_from_renders": [
        {"table_number": n, "caption": c, "pdf_page_index": p,
         "printed_page": pp, "picture": True}
        for n, c, p, pp in (
            ("4.1", "Standard Normal Deviate (ZR) Values Corresponding to "
                    "Selected Levels of Reliability", 83, "I-62"),
            ("2.2", "Suggested Levels of Reliability for Various Functional "
                    "Classifications", 98, "II-9"),
            ("2.3", "Typical Values for k1 and k2 for Unbound Base and "
                    "Subbase Materials (MR = k1 θ^k2)", 109, "II-20"),
            ("2.4", "Recommended mi Values for Modifying Structural Layer "
                    "Coefficients of Untreated Base and Subbase Materials in "
                    "Flexible Pavements", 114, "II-25"),
            ("2.5", "Recommended Values of Drainage Coefficient, Cd, for "
                    "Rigid Pavement Design", 115, "II-26"),
            ("2.6", "Recommended Load Transfer Coefficient for Various "
                    "Pavement Types and Design Conditions", 115, "II-26"),
            ("2.7", "Typical Ranges of Loss of Support (LS) Factors for "
                    "Various Types of Materials", 116, "II-27"),
            ("3.1", "Example of Process Used to Predict the Performance "
                    "Period of an Initial Pavement Structure Considering "
                    "Swelling and/or Frost Heave", 123, "II-34"),
            ("3.2", "Table for Estimating Effective Modulus of Subgrade "
                    "Reaction", 127, "II-38"),
            ("3.3", "Example Application of Method for Estimating Effective "
                    "Modulus of Subgrade Reaction", 132, "II-43"),
            ("G.1", "Table for Estimating Swell Parameters to Use for "
                    "Design", 398, "G-5"))
    ] + [
        {"table_number": f"D.{k}", "caption":
            f"Axle Load Equivalency Factors for {kind} Pavements, {axle} "
            f"Axles and pt of {pt}",
         "pdf_page_index": 361 + k, "printed_page": f"D-{k + 2}",
         "picture": True}
        for k, (kind, axle, pt) in enumerate(
            [(kd, ax, p) for kd in ("Flexible", "Rigid")
             for p in ("2.0", "2.5", "3.0")
             for ax in ("Single", "Tandem", "Triple")], start=1)],
        "notes": {"G.1": "Printed turned on the page; a blank form."}},
    # EN 1997-1 and -2 are scans with an OCR text layer, which prints
    # "Table A.S" for A.5, "Table H.l" for H.1 and "Table 0.5" for D.5, and
    # garbles symbols and letters in captions. Rows the body scan misses or
    # misplaces are placed here from the pages that print them; captions
    # are the stored sections' titles where most of their words are on the
    # page (``caption_from_text``), else as printed.
    "eurocode_7_1": {
        # the stored sections' titles add words ("for EQU"): the captions
        # are read off the renders, every row (2026-11-12)
        "ocr": True,
        "caption_from_render": {
            "A.1": "Partial factors on actions (γF)",
            "A.2": "Partial factors for soil parameters (γM)",
            "A.3": "Partial factors on actions (γF) or the effects of "
                   "actions (γE)",
            "A.4": "Partial factors for soil parameters (γM)",
            "A.5": "Partial resistance factors (γR) for spread foundations",
            "A.6": "Partial resistance factors (γR) for driven piles",
            "A.7": "Partial resistance factors (γR) for bored piles",
            "A.8": "Partial resistance factors (γR) for continuous flight "
                   "auger (CFA) piles",
            "A.9": "Correlation factors ξ to derive characteristic values "
                   "from static pile load tests (n - number of tested piles)",
            "A.10": "Correlation factors ξ to derive characteristic values "
                    "from ground test results (n - the number of profiles "
                    "of tests)",
            "A.11": "Correlation factors ξ to derive characteristic values "
                    "from dynamic impact tests (n - number of tested piles)",
            "A.12": "Partial resistance factors (γR) for pre-stressed "
                    "anchorages",
            "A.13": "Partial resistance factors (γR) for retaining structures",
            "A.14": "Partial resistance factors (γR) for slopes and overall "
                    "stability",
            "A.15": "Partial factors on actions (γF)",
            "A.16": "Partial factors for soil parameters and resistances",
            "A.17": "Partial factors on actions (γF)",
            "C.1": "Ratios va/h for non-cohesive soils",
            "C.2": "Ratios vp/h and v/h for 0.5σp for non-cohesive soils",
            "G.1": "Grouping of weak and broken rocks"},
        # "Table A.11." on p. 134 is the sentence that cites it
        "page_from_render": {"A.11": 135},
        "rows_from_renders": [
            {"table_number": "A.5", "caption": "",
             "pdf_page_index": 132, "printed_page": "131"}]},
    "eurocode_7_2": {
        "ocr": True, "caption_from_text": True,
        # "Table 0.5" is D.5, "Table 0.1" is O.1; "Table L.2." on p. 144 is
        # a sentence citing it (printed on PDF page 146)
        "drop": ["0.5", "0.1"],
        "page_from_render": {"L.2": 146},
        "rows_from_renders": [
            {"table_number": n, "caption": "", "pdf_page_index": p,
             "pages": [103, 104] if n == "B.1" else [p],
             "printed_page": str(p - 1)}
            for n, p in (("2.1", 26), ("3.1", 35), ("A.1", 99), ("B.1", 103),
                         ("D.1", 112), ("D.5", 119), ("E.1", 122),
                         ("E.5", 125), ("F.1", 126), ("G.1", 130),
                         ("H.1", 133), ("L.5", 148), ("M.1", 151),
                         ("O.1", 163), ("P.1", 164), ("Q.1", 166),
                         ("S.1", 169), ("V.1", 174), ("W.1", 177))],
        # the caption at the foot of p. 115, the table on p. 116 (render)
        "pages_from_render": {"D.4": [116, 117]},
        # Read against the renders (2026-11-12): the OCR text layer garbles
        # the words ("inaximmn", "nlm") and numbers ("1S0", "1 200" as one)
        # the check counts, but every cell of these is in the entry.
        "text_by_render": {
            "2.1": "2.4.1.1", "2.2": "2.4.2.6", "2.3": "2.4.2.6",
            "3.1": "3.4.1", "4.1": "4.4.3", "A.1": "A", "B.1": "B.2",
            "D.1": "D.1", "D.2": "D.4", "D.3": "D.6", "D.4": "D.6",
            "D.5": "D.7", "D.6": "D.7", "E.1": "E.1", "E.2": "E.2",
            "E.3": "E.2", "E.5": "E.3", "F.2": "F.1", "G.1": "G.2",
            "L.1": "L.2.4", "L.3": "L.4.1", "L.4": "L.4.1", "L.5": "L.4.1",
            "M.1": "M.1", "M.2": "M.1", "M.3": "M.3.1", "O.1": "O",
            "P.2": "P.2.2", "Q.1": "Q.1", "V.1": "V.1"},
        # the entry has the five columns, not footnote a under them; the
        # lookup returns the category and ID range alone
        "values": {"F.1": ("page", None)},
        "notes": {
            "F.1": "Section F.1 types the table's cells, and "
                   "tables.table_f1_density_index_from_n160 returns them, "
                   "but neither gives its footnote a, the ratios the "
                   "N-values of fine and of coarse sands are changed by. "
                   "Read the footnote off the page.",
            "M.2": "Section M.1 restates each item of the checklist in fewer "
                   "words; the page has its wording.",
            "O.1": "Section O restates each item of the checklist in fewer "
                   "words; the page has its wording."}},
    # Vol II's entries restate each table; three only describe it or give
    # one row of it (Table 12-1 one of ten resistances, 12-7 a few depths,
    # 15-1 the column heads alone): their values are on the page
    # Read against the page (2026-11-12): sections that summarize or
    # paraphrase a table, or type part of it, leave its values on the page.
    # Vol III pages whose last table row, printed near the foot, is read
    # before the page number (renders 2026-11-12)
    "gec_12": {"printed_from_render": {
        ("D-6", 61): "28", ("D-9", 75): "42", ("D-29", 108): "75",
        ("D-79", 190): "157", ("D-81", 193): "160", ("D-117", 257): "224",
        ("D-118", 257): "224", ("D-122", 268): "235"},
        # every cell typed: D-60's symbols (Q/n, Mux y) are not words the
        # check finds, D-121 has four cells (renders)
        "text_by_render": {"D-60": "D.23", "D-121": "D.39.b"},
        "values": {n: ("page", None) for n in (
        "12-1", "12-7", "15-1", "12-11", "12-12", "18-7", "18-6", "13-4",
        "13-5", "13-6")},
        "notes": {
            "12-11": "Section 12.10 summarizes this table's problems and "
                     "solutions; read its wording off the page.",
            "12-12": "Section 12.10 summarizes this table's problems and "
                     "solutions; read its wording off the page.",
            "18-7": "Section 18.9 summarizes this table's problems and "
                    "solutions; read its wording off the page.",
            "18-6": "Section 18.7.7 paraphrases this table's problems and "
                    "indicators; read its wording off the page.",
            "13-4": "Section 13.4 types this table's nominal resistances but "
                    "not its resistance factor column and only some of its "
                    "differences from the static load test; read those off "
                    "the page.",
            "13-5": "Section 13.4 types this table's end-of-drive (EOD) "
                    "values and a few others; its resistance factor column "
                    "and most of its BOR-1, EOR-1 and BOR-2 rows are not "
                    "typed; read them off the page.",
            "13-6": "Section 13.6 types this table's two method columns but "
                    "not all of its Totals column; read the totals off the "
                    "page."}},
    # bodies carry the text layer's cells of most tables; Tables 4-8 and
    # 10-1, printed as pictures, were typed in from the render
    "fhwa_soils_foundations": {"list_mode": "bare", "dump_note": True,
                               # turned pages whose footer the text layer
                               # gives after a cell; a cell read first
                               # (renders 2026-11-12)
                               "printed_from_render": {
                                   ("3-4a", 125): "3-22", ("3-6", 135): "3-32",
                                   ("4-13", 226): "4-27", ("4-25", 242): "4-43",
                                   ("A.5-3", 438): "A.5-11"},
                               "caption_from_render": {
                                   "3-4b": "Rock core drilling methods "
                                           "(FHWA, 2002a)"},
                               # printed as pictures, typed in from the page
                               "text_by_render": {"4-8": "4.2.1",
                                                  "10-1": "10.2.4"},
                               # p. 5-9 prints Table 5-3's column heads
                               # again over its last rows (render)
                               "volumes": [{"list_pages": (26, 28),
                                            "pages_from_render": {
                                                "5-3": [257, 258]}},
                                           {"list_pages": (23, 24)}]},
}

#: (reference, table number, function) a name or docstring search pairs but
#: which does not return that table, found by opening each: it takes a
#: value of the table as an input (a consumer, "kt from Table 6-23"), it
#: computes a quantity the table only defines in a heading, or it cites
#: another manual's table of the same number.
NOT_IMPLEMENTED_BY: set[tuple[str, str, str]] = {
    # UFC 3-220-20: Delta w is defined in Table 3-11's heading; the table's
    # compaction specifications are not coded
    ("dm7_2", "3-11", "relative_water_content"),
    # the LCPC method's resistances take ks, fp and kt as inputs
    ("dm7_2", "6-21", "lcpc_unit_shaft_resistance"),
    ("dm7_2", "6-22", "lcpc_unit_shaft_resistance"),
    ("dm7_2", "6-23", "lcpc_unit_base_resistance"),
    # functions that cite a table in their opening paragraph without
    # returning its values: an equation the table tabulates or a worked
    # example checks, a footnote or paragraph, another table's lookup
    # (read 2026-11-12)
    ("em_2107", "F.3", "hydrostatic_horizontal_component"),
    ("em_2107", "F.3", "resultant_angle_from_horizontal"),
    ("ufc_structural", "2-1", "table_4_1a_structural_performance_objective"),
    ("ufc_structural", "2-1", "table_4_1b_nonstructural_performance_objective"),
    ("ufc_structural", "2-2", "risk_category_v_note"),
    ("ufc_structural", "3-1", "table_b1_rc4_permitted_system"),
    ("ufc_collapse", "2-1", "rc4_tie_force_minimum_exempt"),
    # applies the Section 3-2.5 rule; the package says Table 3-1 is not
    # digitised (2026-11-12 check)
    ("ufc_collapse", "3-1", "classify_action"),
    ("ufc_collapse", "4-4", "shear_demand_pinned_fixed_column"),
    ("gsa_collapse", "D17", "column_deformation_controlled_shear_check"),
    ("ufc_pavement", "G-1", "figure_e_vehicle_allowable_passes"),
    ("wood_handbook", "4-2", "equilibrium_moisture_content"),
    ("wood_handbook", "8-8", "wood_screw_withdrawal"),
    # a lookup's numbers checked against its table's page (2026-11-12):
    # Tables 7-12 and 7-13 are the steps of reading cv off a test curve and
    # Table C-1 a worked example; the functions compute Eqs. 7-43 and 7-7
    ("em_1905", "7-12", "equation_7_43_coefficient_of_consolidation"),
    ("em_1905", "7-13", "equation_7_43_coefficient_of_consolidation"),
    ("em_1905", "C-1", "equation_7_7_consolidation_settlement"),
}


def _cfg(package: str, volume_index: int = 0) -> dict:
    c = CONFIG.get(package, {})
    if "volumes" in c:
        return {**{k: v for k, v in c.items() if k != "volumes"},
                **c["volumes"][volume_index]}
    return c


# ---------------------------------------------------------------------------
# Resolving pages
# ---------------------------------------------------------------------------

#: How alike the list's caption and the caption printed on a page must be
#: (difflib ratio of the normalized text) for the page to be the table's
#: when the two are worded differently.
NEAR_CAPTION_RATIO = 0.75


def _open_pdf(rel: str):
    import fitz  # PyMuPDF
    p = _REPO_ROOT / rel
    if not p.exists():
        for d in _FALLBACK_DOCS:
            if (d / Path(rel).name).exists():
                p = d / Path(rel).name
                break
    if not p.exists():
        raise FileNotFoundError(f"PDF not found: {p}")
    return fitz.open(str(p))


def _label_of(doc, i: int) -> "str | None":
    try:
        lab = doc[i].get_label()
    except Exception:  # noqa: BLE001
        lab = ""
    return lab or None


#: A token shaped like a printed page label: "112", "4-12", "A-3", "A2-14",
#: "I-55", "B3", or front matter "xiv" (the rule the figure catalogs'
#: printed pages were read by, tests/test_catalog_printed_pages.py).
_PAGE_TOKEN = re.compile(
    r"^(?:\d{1,4}"
    r"|\d{1,2}-\d{1,3}"
    r"|[A-Z]{1,2}(?:\.?\d{1,2})?-\d{1,3}"
    r"|[A-Z]\d{1,3}"
    r"|[ivxlc]{1,7})$")


def _norm_label(label) -> str:
    s = str(label).strip()
    for d in _DASHES:
        s = s.replace(d, "-")
    s = re.sub(r"\s*-\s*", "-", s)
    return re.sub(r"^(?:page|p\.)\s*", "", s, flags=re.I)


def _is_year(tok: str) -> bool:
    return tok.isdigit() and len(tok) == 4 and 1950 <= int(tok) <= 2035


def page_label(page, zone: float = 0.11) -> "str | None":
    """The page number a page prints, read from its text layer: the tokens
    shaped like a page label in the lines of its top or bottom 11 percent,
    or of its outer side strips for a page printed turned, a line holding
    only the label first, never a year. None when the text layer gives
    none (a scan; a label drawn as outlines)."""
    import fitz  # PyMuPDF
    frames = [(page.rect, fitz.Identity)]
    if page.rotation:
        frames.append(((page.rect * page.rotation_matrix).normalize(),
                       page.rotation_matrix))
        frames.append((page.mediabox, fitz.Identity))
    found = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            in_band = side = False
            for r, m in frames:
                x0, y0, x1, y1 = (fitz.Rect(line["bbox"]) * m).normalize()
                in_band |= (y1 < r.y0 + zone * r.height
                            or y0 > r.y1 - zone * r.height)
                side |= (x1 < r.x0 + 0.09 * r.width
                         or x0 > r.x1 - 0.09 * r.width)
            if not (in_band or side):
                continue
            toks = _norm_label("".join(s["text"] for s in line["spans"])).split()
            for k, tok in enumerate(toks):
                tok = tok.strip(",;:()[]")
                if not tok or _is_year(tok) or not _PAGE_TOKEN.match(tok):
                    continue
                score = ((2 if len(toks) == 1 else 1 if k in (0, len(toks) - 1)
                          else 0) + (1 if in_band else 0))
                found.append((score, len(found), tok))
    return min(found, key=lambda f: (-f[0], f[1]))[2] if found else None


def _printed_page(cfg: dict, r: dict) -> "str | None":
    """A row's printed page: the label read off the render where CONFIG
    ``printed_from_render`` gives one (by number, or by number and page
    index) or the row was placed on a render with its page; else the
    label its page's text layer prints (:func:`page_label`)."""
    pins = cfg.get("printed_from_render", {})
    num = r["table_number"]
    for key in ((num, r.get("pdf_page_index")), num):
        if key in pins:
            return pins[key]
    if r.get("_render_page"):
        return r.get("list_page")
    return r.get("_label")


def _list_like(cands: list[dict]) -> bool:
    """Whether a page's captions are a list of tables: four or more, each
    within two lines of the last (an appendix's own list on its title
    page, GEC-7 Appendix A; a chapter's List of Tables whose dot leaders
    fall on the next line, GEC-13)."""
    lines = sorted(c["line"] for c in cands if not c["continued"])
    if len(lines) < 4:
        return False
    gaps = [b - a for a, b in zip(lines, lines[1:])]
    return statistics.median(gaps) <= 2


def _scan_body(doc, start: int, end: int, cfg: dict) -> dict[int, list[dict]]:
    num_ok = re.compile(cfg["numbers"]) if cfg.get("numbers") else None
    out: dict[int, list[dict]] = {}
    for i in range(start, end):
        cands = caption_candidates(page_lines(doc[i]))
        if num_ok is not None:
            cands = [c for c in cands if num_ok.fullmatch(c["number"])]
        if cands:
            if _list_like(cands):
                for c in cands:
                    c["list_like"] = True
            out[i] = cands
    return out


def _prefer_printed(found: list[tuple[int, dict]]) -> list[tuple[int, dict]]:
    """A number's candidates with those on a list-like page last, so a
    table printed on a later page wins over the list that names it."""
    return sorted(found, key=lambda x: bool(x[1].get("list_like")))


def _page_token_holds(doc, i: int, token: "str | None") -> bool:
    """Whether page ``i`` prints ``token`` (its printed page) on a line of
    its own or at a line's end, the way a page number is printed."""
    if not token:
        return False
    parts = [re.escape(p) for p in re.split(r"-", token)]
    rx = re.compile(r"(?m)(?:^|\s)" + rf"[ \t]*[-{_DASHES}][ \t]*".join(parts)
                    + r"[ \t]*$")
    return bool(rx.search(doc[i].get_text().translate(_SMART)))


def _shift_token(token: "str | None", k: int) -> "str | None":
    if not token:
        return None
    m = re.match(r"^(.*?)(\d+)$", token)
    if not m:
        return None
    return f"{m.group(1)}{int(m.group(2)) + k}"


def _top_lines(page, share: float = 0.3, skip: float = 0.07) -> list[str]:
    """A page's lines in its top ``share``, past the running header (the
    top ``skip``, 7 percent), in reading order from the top."""
    h = page.rect.height
    out = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            y = ln["bbox"][1]
            if skip * h <= y < share * h:
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if t:
                    out.append((y, t))
    return [t for _, t in sorted(out)]


def _head_lines(doc, start: int, num: str, caption: str) -> set[str]:
    """The first eight lines printed under a table's caption on its first
    page (its column heads), normalized, those with a letter and four
    characters or more that are not part of the caption; none when the
    page's text does not print the caption's label."""
    rx = _caption_rx(num)
    ncap = _norm(caption)
    page = doc[start]
    h = page.rect.height
    lines = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            y = ln["bbox"][1]
            if 0.09 * h < y < 0.91 * h:     # past the running header and footer
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if t:
                    lines.append((y, t))
    lines = [t for _, t in sorted(lines)]
    k0 = next((k for k, t in enumerate(lines) if rx.search(t)), None)
    if k0 is None:
        return set()
    rest = lines[k0 + 1:]
    while rest and _norm(rest[0]) and _norm(rest[0]) in ncap:
        rest = rest[1:]                 # the caption's own further lines
    out = set()
    for t in rest[:8]:
        n = _norm(t)
        if len(n) >= 4 and re.search(r"[a-z]", n):
            out.add(n)
    return out


def _ruled_frames(page) -> list[tuple]:
    """``(x0, y0, x1, y1, columns)`` of each ruled table PyMuPDF finds."""
    try:
        return [(*t.bbox, t.col_count) for t in page.find_tables().tables]
    except Exception:       # a page find_tables cannot take
        return []


def _text_lines(page) -> list[tuple]:
    """``(x0, y0, x1, y1, text)`` of each line of a page's text layer."""
    out = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            t = "".join(s["text"] for s in ln["spans"]).strip()
            if t:
                out.append((*ln["bbox"], t))
    return out


def _ruled_runs_on(doc, i: int, caption_rx, starts_before: bool) -> bool:
    """Whether the table on page ``i - 1`` is a ruled table that reaches
    the foot of the page (its last fifth), and page ``i`` opens with a
    ruled table of the same width and columns with nothing printed above
    it but the running head (its top 9 percent): a ruled table carried on
    with no label or column heads printed again (EM 1110-1-1905's worked
    examples). On page ``i - 1`` only the ruled tables below the caption
    count when the table starts there (``starts_before``), and the one at
    the foot must be the table's: nothing printed between it and the ruled
    table above it, or the table's own caption among what is ("Table 3-1
    (cont.)"; a heading and a notation list are another table)."""
    prev_page, page = doc[i - 1], doc[i]
    prev = _ruled_frames(prev_page)
    plines = _text_lines(prev_page)
    if starts_before:
        tops = [ln[1] for ln in plines if caption_rx.search(ln[4])]
        if tops:
            prev = [f for f in prev if f[1] > min(tops)]
    if not prev:
        return False
    last = max(prev, key=lambda f: f[3])
    for f in prev:
        if f is last or f[3] > last[1]:
            continue
        between = [ln[4] for ln in plines if ln[1] >= f[3] - 1 and ln[3] <= last[1] + 1]
        if between and not any(caption_rx.search(t) for t in between):
            return False
    if last[3] < 0.8 * prev_page.rect.height:
        return False
    nxt = _ruled_frames(page)
    if not nxt:
        return False
    first = min(nxt, key=lambda f: f[1])
    h = page.rect.height
    if first[1] > 0.25 * h:
        return False
    # a heading or text above it ("P-4 NOTATION."): another table
    if any(0.09 * h < ln[1] and ln[3] <= first[1] + 1 for ln in _text_lines(page)):
        return False
    return (abs(first[0] - last[0]) <= 6 and abs(first[2] - last[2]) <= 6
            and first[4] == last[4])


def _continuations(doc, body: dict, start: int, num: str, caption: str,
                   end: int) -> list[int]:
    """Pages straight after ``start`` that carry the table on: they print
    its label again; or, with no other table's caption or a new section
    at their top, "(continued)" near their top, its caption, or two of the
    lines printed under its caption on the first page (the column heads
    printed again: UFC 3-301-01 Table E-1, seven pages); or, with no other
    table's caption on them at all, a ruled table that carries on the one
    filling the foot of the page before (:func:`_ruled_runs_on`). A table
    with another caption below it on its page, or on a page it runs onto,
    does not run on past that page by the last four tests."""
    pages = []
    i = start + 1
    nc = _norm(caption)[:15]
    ncap = _norm(caption)
    heads = None
    key = number_key(num)
    own = [c["line"] for c in body.get(start, []) if number_key(c["number"]) == key]
    blocked = bool(own) and any(
        number_key(c["number"]) != key and not c["continued"] and c["line"] > min(own)
        for c in body.get(start, []))
    while i < end:
        hit = False
        for c in body.get(i, []):
            if number_key(c["number"]) != key:
                continue
            text, _ = caption_text(c, caption)
            if c["continued"] or (nc and _norm(text).startswith(nc)) or \
                    _norm(c["rest"]).startswith("cont"):
                hit = True
        if not hit and not blocked:
            # the lines at the page's top above any other table's caption
            # (a caption can sit inside the top 7 percent: Wood Handbook)
            top = _top_lines(doc[i], skip=0.0)[:14]
            for k, t in enumerate(top):
                m = re.match(rf"^\W{{0,3}}(?:Table|TABLE)\s+({NUM})", t)
                if m and number_key(norm_number(m.group(1))) != key:
                    top = top[:k]
                    break
            top = top[:10]
            ntop = [_norm(t) for t in top]
            # a new section opens the page: not ours
            opens_other = any(
                re.match(r"^\d+[-.]\d+(?:\.\d+)*\.?\s+[A-Z][A-Z ,&/-]{6,}", t.strip())
                for t in top[:5])
            if top and not opens_other:
                # (a line holding the whole caption: its first words alone
                # can be another table's caption, UFC 3-220-20 Table 5-8;
                # and little more: a sentence can open with its words,
                # "Bearing capacity factor N*c can be taken as 9.0", GEC-10)
                if any(_CONTINUED.search(t.strip()) for t in top[:8]) or any(
                        len(ncap) >= 12 and n.startswith(ncap)
                        and len(n) - len(ncap) <= 12 for n in ntop[:8]):
                    hit = True
                else:
                    if heads is None:
                        heads = _head_lines(doc, start, num, caption)
                    # the page opens with two lines the first page prints
                    # under the caption: the column heads printed again
                    same = [n for n in ntop if n in heads]
                    if len(same) >= 2 and sum(len(n) for n in same) >= 16:
                        hit = True
            if not hit and not opens_other and not any(
                    number_key(c["number"]) != key for c in body.get(i, [])) \
                    and _ruled_runs_on(doc, i, _caption_rx(num), i - 1 == start):
                hit = True
        if not hit:
            break
        pages.append(i)
        # another table starts on this page: the pages after it are its
        if any(number_key(c["number"]) != key and not c["continued"]
               for c in body.get(i, [])):
            break
        i += 1
    return pages


def resolve_rows(doc, entries: list[dict], body: dict, cfg: dict,
                 body_start: int, end: int) -> list[dict]:
    """Give every list entry its page (mutates and returns ``entries``)."""
    by_num: dict[str, list[tuple[int, dict]]] = {}
    for i in sorted(body):
        for c in body[i]:
            by_num.setdefault(number_key(c["number"]), []).append((i, c))
    used: set = set()
    for e in entries:
        key = number_key(e["table_number"])
        e["how"] = None
        best = None
        for i, c in _prefer_printed(by_num.get(key, [])):
            if c["continued"] or (i, key) in used:
                continue
            text, r = caption_text(c, e["caption"])
            if r >= 1.0 or r >= NEAR_CAPTION_RATIO:
                best = (i, c, text, r)
                break
        if best is not None:
            i, c, text, r = best
            used.add((i, key))
            e.update(pdf_page_index=i, page_caption=text, ratio=r,
                     how="caption" if r >= 1.0 else "near caption")
    # the printed-to-PDF page offset of each chapter, from the rows found
    offs: dict = {}
    for e in entries:
        if e.get("pdf_page_index") is not None and e.get("list_page"):
            m = re.match(r"^(.*?)(\d+)$", e["list_page"])
            if m:
                offs.setdefault(m.group(1), []).append(
                    e["pdf_page_index"] - int(m.group(2)))
    for e in entries:
        if e.get("pdf_page_index") is not None:
            continue
        key = number_key(e["table_number"])
        m = re.match(r"^(.*?)(\d+)$", e.get("list_page") or "")
        expected = None
        if m and offs.get(m.group(1)):
            expected = int(m.group(2)) + int(statistics.median(offs[m.group(1)]))
        # a caption under the label near the expected page, worded
        # differently from the list (read off the render to confirm)
        near = [(i, c) for i, c in by_num.get(key, [])
                if not c["continued"] and (i, key) not in used
                and (expected is None or abs(i - expected) <= 3)]
        if near:
            i, c = min(near, key=lambda x: abs(x[0] - (expected or x[0])))
            text, r = caption_text(c, e["caption"])
            used.add((i, key))
            e.update(pdf_page_index=i, page_caption=text, ratio=r,
                     how="label only")
        elif expected is not None:
            e.update(pdf_page_index=max(body_start, min(doc.page_count - 1, expected)),
                     how="estimated")
        else:
            e.update(pdf_page_index=None, how="not found")
    return entries


def rows_from_body(doc, body: dict, cfg: dict) -> list[dict]:
    """Rows for a reference that prints no List of Tables: the first caption
    of each number in the body (a caption that opens its text block when
    ``block_start_only``)."""
    rows: dict[str, dict] = {}
    order = []
    for i in sorted(body):
        for c in body[i]:
            if c["continued"]:
                continue
            # a caption opens its text block, stands as a label on a line of
            # its own, or is set in bold; a sentence that cites a table does
            # none of these
            if cfg.get("block_start_only", True) and not (
                    c["first"] or not c["rest"] or c["bold"]):
                continue
            key = number_key(c["number"])
            # the first caption of each number, unless that one is on a
            # page that lists tables and a later page prints it
            if key in rows and not rows[key]["_list_like"]:
                continue
            if key in rows and c.get("list_like"):
                continue
            text, _ = caption_text(c)
            if len(text) < 3:
                continue
            if key not in rows:
                order.append(key)
            rows[key] = {"table_number": c["number"], "caption": text,
                         "list_page": None, "pdf_page_index": i,
                         "page_caption": text, "ratio": 1.0, "how": "body caption",
                         "_list_like": bool(c.get("list_like"))}
    return [rows[k] for k in order]


# ---------------------------------------------------------------------------
# Lookups and text sections
# ---------------------------------------------------------------------------

def _public_functions(package: str) -> list[tuple[str, str, str]]:
    """``(dotted path, name, docstring)`` of every public function the
    package's public modules define."""
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    out = []
    try:
        pkg = importlib.import_module(f"geotech_references.{package}")
    except Exception:  # noqa: BLE001
        return out
    for m in pkgutil.iter_modules(pkg.__path__):
        if m.name.startswith("_") or m.ispkg:
            continue
        try:
            mod = importlib.import_module(f"geotech_references.{package}.{m.name}")
        except Exception:  # noqa: BLE001
            continue
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("_") or fn.__module__ != mod.__name__:
                continue
            out.append((f"{mod.__name__}.{name}", name, inspect.getdoc(fn) or ""))
    return out


def _cite_rx(num: str) -> "re.Pattern":
    parts = [re.escape(p) for p in re.split(r"[-.]", norm_number(num))]
    body = rf"[ \t]*[-.{_DASHES}][ \t]*".join(parts)
    return re.compile(rf"(?i)\btables?\s*{body}(?![\w.-]?\d)(?![a-z])")


def _name_rx(num: str) -> "re.Pattern":
    parts = [p for p in re.split(r"[-.]", norm_number(num).lower()) if p]
    # 'table_3_1_x' is Table 3-1, not Table 3 (a further number part)
    return re.compile(r"(?:^|_)table_?" + "_?".join(re.escape(p) for p in parts)
                      + r"(?![0-9a-z])(?!_\d)")


def _helper_function(path: str) -> int:
    """1 for a function that lists a table's keys or returns one of its
    footnotes ('list_table_3_1_systems', 'table_e1_note'), else 0."""
    name = path.rsplit(".", 1)[-1]
    return 1 if name.startswith("list_") or re.search(r"_(?:foot)?notes?$", name) else 0


def find_lookups(package: str, rows: list[dict]) -> dict[str, list[str]]:
    """``{table number: [dotted function paths]}``: a public function named
    for the table or whose docstring cites it, less the pairs in
    :data:`NOT_IMPLEMENTED_BY`."""
    funcs = _public_functions(package)
    out: dict[str, list[str]] = {}
    for r in rows:
        num = r["table_number"]
        if not re.search(r"\d", num):
            continue
        nrx, crx = _name_rx(num), _cite_rx(num)
        named, cited = [], []
        for path, name, doc in funcs:
            if (package, num, name) in NOT_IMPLEMENTED_BY:
                continue
            if nrx.search(name):
                named.append(path)
            # cited in its summary (first paragraph): the function is that
            # table; a table cited further down ("coefficients are
            # tabulated in Table 8-26", "see Table 6-5") is one whose values
            # the caller passes in, which the function does not return
            elif crx.search(doc.split("\n\n")[0]):
                cited.append(path)
        extra = [f"geotech_references.{package}.{p}"
                 for p in CONFIG.get(package, {}).get("lookups", {}).get(num, [])]
        # the function that returns the values first; one that lists the
        # table's keys or returns a footnote after it
        found = list(dict.fromkeys(extra + sorted(
            sorted(named) + sorted(cited), key=_helper_function)))
        if found:
            out[num] = found
    return out


def _plain_call(dotted: str) -> bool:
    """False for a function that takes Python functions as inputs (it
    carries ``needs_python_callables``): a caller with plain values cannot
    run it, so it is not where a reader finds a table's values."""
    mod, _, name = dotted.rpartition(".")
    try:
        fn = getattr(importlib.import_module(mod), name)
    except (ImportError, AttributeError):
        return True
    return not getattr(fn, "needs_python_callables", False)


def _short_path(package: str, dotted: str) -> str:
    """'geotech_references.gec_10.tables.table_8_4' -> 'tables.table_8_4'."""
    prefix = f"geotech_references.{package}."
    return dotted[len(prefix):] if dotted.startswith(prefix) else dotted


def _walk(sections):
    for s in sections or []:
        if isinstance(s, dict):
            yield s
            yield from _walk(s.get("subsections"))


def table_ref_number(t) -> "str | None":
    """The table number a chapter-text ``tables`` entry names: a string
    ("Table 5-3", "Table 4.1: caption", "5-3") or a dict (``table_id``,
    ``id``, ``number``)."""
    if isinstance(t, dict):
        raw = str(t.get("table_id") or t.get("number") or t.get("id") or "")
    else:
        raw = str(t or "")
    raw = raw.strip()
    # "10.2-conformance" is a section's id for a table printed without a
    # number (gec_11 10.2), not Table 10-2
    m = re.match(rf"(?i)^(?:table\s+)?({NUM})(?![\d])", raw)
    if not m or re.match(r"-[A-Za-z]{2}", raw[m.end():]):
        return None
    return norm_number(m.group(1))


def _entry_text(t) -> str:
    """The text of a chapter-text ``tables`` entry: the string, or a dict's
    title and content fields."""
    if isinstance(t, dict):
        return " ".join(str(t.get(k) or "") for k in
                        ("table_id", "id", "number", "title", "description",
                         "content", "cells", "rows", "data", "values"))
    return str(t or "")


def _entry_title(t) -> str:
    """The title a ``tables`` entry gives its table: a dict's ``title``, or
    a string's words after the number up to its first " - ", " (p." or
    ": " ("Table E.2: The shape coefficients ... - L/B circle ...")."""
    if isinstance(t, dict):
        return str(t.get("title") or "").strip()
    s = re.sub(rf"(?i)^\s*(?:table\s+)?{NUM}\s*[:.{_DASHES}-]?\s*", "", str(t or ""))
    return re.split(rf"\s[-{_DASHES}]\s|\s\(p+\.|:\s", s, maxsplit=1)[0].strip()


_NUMS = re.compile(r"(?<![\w.])[-+]?\d+(?:[.,]\d+)?")


def entry_has_cells(t) -> bool:
    """Whether a ``tables`` entry carries the table's cells, not only its
    number and title: past its title it runs on with cells set apart
    (';' or '|') or a run of values. Each entry this passes was then read
    (the report's 'text' rows); a reference whose entries describe a table
    in words is set ``entries_describe`` in :data:`CONFIG`."""
    if isinstance(t, dict):
        bodies = [" ".join(str(t.get(k) or "") for k in
                           ("description", "content", "cells", "rows", "data",
                            "values"))]
    else:
        s = str(t or "")
        bodies = []
        # "Table 6-1: Title (p. 6-3) - columns: ..." -> what follows the title
        m = re.search(r"\(p+\.\s*[\w-]+\)\s*[-:–]?\s*|\s[-–]\s", s)
        if m:
            bodies.append(s[m.end():])
        # "Table 4-3: Title: cells ..." -> what follows the title's colon
        rest = re.sub(rf"(?i)^\s*(?:table\s+)?{NUM}\s*[:.{_DASHES}-]?\s*", "", s)
        m = re.search(r":\s", rest)
        if m:
            bodies.append(rest[m.end():])
    for body in bodies:
        body = body.strip()
        if len(body) < 80:
            continue
        seps = body.count(";") + body.count("|")
        if seps >= 3 or len(_NUMS.findall(body)) >= 8:
            return True
    return False


# ---------------------------------------------------------------------------
# Whether a stored entry holds every printed cell (REF-86 review, 1c)
# ---------------------------------------------------------------------------

#: words too common to say whether a table's cells are typed in
_STOP = set("""the and for with from that this are not all any per its into
than then when where which who whom have has had was were been being but also
may can shall should will would use used using see each other such these
those there their them they our out off one two three four five six seven
eight nine ten table tables figure note notes after source continued cont
page""".split())
#: A line opening with a table's or figure's label ("Table 5-3", "Table
#: B-13", "Figure D.2"): where the table above it ends.
_ANY_CAP = re.compile(rf"^\W{{0,3}}(?:Table|TABLE|Figure|FIGURE|Exhibit)\s+"
                      rf"[A-Z]{{0,2}}[-.{_DASHES}]?\d")


def _norm_value(t: str) -> str:
    """A printed number for comparing: '0.30', '.3' and '0.3' alike, no
    thousands commas."""
    t = t.replace(",", "")
    if t.startswith("."):
        t = "0" + t
    if "." in t:
        t = t.rstrip("0").rstrip(".") or "0"
    return t


def cell_tokens(text: str) -> tuple[set, set]:
    """``(numbers, words)`` of a text: every number as :func:`_norm_value`
    gives it, and every word of three letters or more, lower case, less
    :data:`_STOP`. A decimal comma ("0,03", "2,5": Eurocode 7) reads as
    a point; a comma before three digits stays a thousands comma."""
    text = _plain_math(str(text).translate(_SMART))
    text = re.sub(r"(?<![\d,.])(0|\d+(?=,\d{1,2}(?!\d|,\d))),(\d+)(?!\d|,\d)",
                  r"\1.\2", text)
    nums = {_norm_value(m) for m in
            re.findall(r"(?<![\w.])\d*\.?\d+(?:,\d{3})*(?:\.\d+)?", text)}
    words = {w.lower() for w in re.findall(r"[A-Za-z]{3,}", text)} - _STOP
    return nums, words


def _caption_rx(num: str, ocr: bool = False) -> "re.Pattern":
    """A line opening with the table's label. ``ocr``: the text layer is a
    scan's OCR, which prints "Table A.l" or "Table 0.5" for A.1 and D.5
    (:func:`_ocr_part`)."""
    parts = [_ocr_part(p) if ocr else re.escape(p)
             for p in re.split(r"[-.]", num) if p]
    return re.compile(r"^\W{0,3}(?:Table|TABLE|table)\s*"
                      + rf"\s*[-.{_DASHES}]?\s*".join(parts) + r"(?![\d])")


def table_region(doc, pages: list[int], num: str, ocr: bool = False) -> list[dict]:
    """The printed table on each of its pages: ``text`` (its words),
    ``labels`` (the first column of a ruled table, its row labels, or None)
    ``head`` (a ruled table's column heads, its first row) and ``rects``
    (where it is). A ruled table is PyMuPDF's
    ``find_tables`` box below the caption; else the lines from the caption
    down to the next caption or the first paragraph after the table (a
    line of twelve words or more across most of the page), headers and
    footers left out. ``ocr`` as for :func:`_caption_rx`."""
    rx = _caption_rx(num, ocr)
    out = []
    for k, pi in enumerate(pages):
        page = doc[pi]
        h, w = page.rect.height, page.rect.width
        lines = []
        for blk in page.get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if t:
                    lines.append((fitz_rect(ln["bbox"]), t, ln.get("dir", (1, 0))))
        lines.sort(key=lambda x: (round(x[0][1]), x[0][0]))
        turned = bool(page.rotation) or (
            bool(lines) and sum(1 for ln in lines if abs(ln[2][1]) > 0.9) > len(lines) / 2)
        top = None
        if k == 0 and not turned:
            for bb, t, _ in lines:
                if rx.search(t):
                    top = bb[1]     # the caption (a later line citing the
                    break           # table is not its top)
        bottom = h
        for bb, t, _ in lines:
            if (top is None or bb[1] > top + 2) and _ANY_CAP.search(t) \
                    and not rx.search(t):
                bottom = bb[1]
                break
        tabs = []
        if not turned:
            try:
                tabs = [t for t in page.find_tables().tables
                        if (top is None or t.bbox[3] > top) and t.bbox[1] < bottom]
            except Exception:       # a page find_tables cannot take
                tabs = []
        if tabs:
            for t in tabs:
                labels, cells, head = [], 0, []
                try:
                    data = t.extract()
                    labels = [str(row[0]) for row in data[1:] if row and row[0]]
                    cells = sum(1 for row in data for c in row if c and str(c).strip())
                    head = [str(c) for c in (data[0] if data else []) if c]
                    head += [str(c) for c in (t.header.names or []) if c]
                except Exception:
                    pass
                out.append({"page": pi, "how": "ruled",
                            "text": page.get_text("text", clip=t.bbox),
                            "labels": "\n".join(labels), "cells": cells,
                            "head": "\n".join(head),
                            "rects": [tuple(t.bbox)]})
            continue
        keep, rects = [], []
        for bb, t, _ in lines:
            if not turned and (bb[3] < 0.08 * h or bb[1] > 0.92 * h):
                continue
            if top is not None and bb[1] < top - 1:
                continue
            if bb[1] >= bottom:
                break
            if not turned and len(t.split()) >= 12 and (bb[2] - bb[0]) > 0.6 * w:
                if len(keep) >= 3:
                    break       # the paragraph after the table
                continue
            keep.append(t)
            rects.append(tuple(bb))
        out.append({"page": pi, "how": "lines", "text": "\n".join(keep),
                    "labels": None, "cells": len(keep), "rects": rects})
    return out


def fitz_rect(bbox) -> tuple:
    return tuple(float(v) for v in bbox)


def _word_hit(w: str, have: set, stems: set) -> bool:
    if w in have or w[:6] in stems:
        return True
    # an OCR text layer's "infonnative" for "informative"
    return any(abs(len(e) - len(w)) <= 2 and SequenceMatcher(None, w, e).ratio() >= 0.8
               for e in have)


def cell_coverage(region: list[dict], entry: str) -> dict:
    """How much of a printed table a stored entry holds: ``cov`` (share of
    the table's numbers and row labels found in the entry; every word of
    the table where it is not ruled), ``ncov`` (its numbers alone),
    ``wall`` (every word of the table but a ruled table's column heads,
    which an entry may restate in its own words), ``lenratio`` (the
    entry's letters and digits over the table's), ``n_tok`` and the tokens
    not found."""
    pn, pw, allw = set(), set(), set()
    rchars = 0
    for part in region:
        n_, w_ = cell_tokens(part["text"])
        pn |= n_
        allw |= w_ - cell_tokens(part.get("head") or "")[1]
        pw |= cell_tokens(part["labels"])[1] if part["labels"] is not None else w_
        rchars += len(re.findall(r"[A-Za-z0-9]", part["text"]))
    en, ew = cell_tokens(entry)
    stems = {w[:6] for w in ew}
    mn = pn & en
    mw = {w for w in pw if _word_hit(w, ew, stems)}
    tot = len(pn) + len(pw)
    return {
        "n_tok": tot,
        # the table's cells (a ruled table's), or its lines
        "n_cells": sum(part.get("cells") or 0 for part in region),
        "cov": round((len(mn) + len(mw)) / tot, 3) if tot else 0.0,
        "ncov": round(len(mn) / len(pn), 3) if pn else None,
        "wall": round(sum(1 for w in allw if _word_hit(w, ew, stems)) / len(allw), 3)
        if allw else None,
        "lenratio": round(len(re.findall(r"[A-Za-z0-9]", entry)) / rchars, 2)
        if rchars else None,
        "miss_num": sorted(pn - en),
        "miss_word": sorted(w for w in pw if w not in mw),
        "miss_all": sorted(w for w in allw if not _word_hit(w, ew, stems)),
    }


def coverage_ok(c: dict) -> bool:
    """Whether a coverage record says every cell is typed in: 90 percent of
    the numbers and row labels, 80 percent of the table's words (but a
    ruled table's column heads), an
    entry at least 60 percent of the table's length, and six cells or
    more to judge by. A row that fails is read on the render
    (:data:`CONFIG` ``text_by_render``)."""
    return (c.get("n_cells", c["n_tok"]) >= 6 and c["cov"] >= 0.9
            and (c["ncov"] is None or c["ncov"] >= 0.9)
            and (c["wall"] is None or c["wall"] >= 0.8)
            and (c["lenratio"] is None or c["lenratio"] >= 0.6))


#: A table typed into a section body as rows of cells set apart by '|'
#: (three such rows within 1,500 characters after the table's label).
def body_has_cells(body: str, num: str) -> bool:
    rx = _cite_rx(num)
    for m in rx.finditer(body or ""):
        seg = body[m.end():m.end() + 1500]
        rows = [ln for ln in seg.splitlines() if ln.count("|") >= 2]
        if len(rows) >= 3:
            return True
    return False


def text_sections(package: str) -> dict[str, list[dict]]:
    """``{number key: [section records]}``: every chapter-text section whose
    ``tables`` list names the table, each ``{section_id, title, chapter,
    cells}`` (``cells``: the entry carries the table's cells,
    :func:`entry_has_cells`), and every section whose body types the table
    as rows of cells (``{..., "body_cells": True}``)."""
    out: dict[str, list[dict]] = {}
    tdir = _PACKAGE_DIR / package / "text"
    if not tdir.is_dir():
        return out
    for jf in sorted(tdir.glob("*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for sec in _walk(data.get("sections")):
            sid = sec.get("section_id")
            if not sid:
                continue
            base = {"section_id": sid, "title": sec.get("title") or "",
                    "chapter": data.get("chapter"), "file": jf.name,
                    "volume": data.get("volume")}
            for t in sec.get("tables") or []:
                num = table_ref_number(t)
                if not num:
                    continue
                bucket = out.setdefault(number_key(num), [])
                rec = dict(base, cells=entry_has_cells(t),
                           entry=_entry_text(t)[:400],
                           entry_full=_entry_text(t),
                           entry_title=_entry_title(t))
                if not any(b["section_id"] == sid and b.get("listed")
                           for b in bucket):
                    rec["listed"] = True
                    bucket.append(rec)
                else:
                    # a second entry for the same table in this section
                    for b in bucket:
                        if b["section_id"] == sid and b.get("listed"):
                            b["entry_full"] += "\n" + rec["entry_full"]
                            b["cells"] = b["cells"] or rec["cells"]
            body = sec.get("body") or ""
            base = dict(base, body_text=body)
            # a table printed as a picture whose rows a build typed in from
            # the render ("[Table 4-8 is printed as a picture; its rows, read
            # off the page:]", fhwa_soils_foundations)
            for m in re.finditer(rf"\[Table\s+({NUM})[^\]]{{0,80}}read off the page",
                                 body):
                bucket = out.setdefault(number_key(norm_number(m.group(1))), [])
                if not any(b["section_id"] == sid and b.get("body_cells")
                           for b in bucket):
                    bucket.append(dict(base, body_cells=True))
            # the cells of a table as the text layer gives them, in reading
            # order without its columns (fhwa_soils_foundations bodies):
            # the label, then the caption's first words
            for m in re.finditer(rf"(?<![\[\w])Table\s+({NUM})(?![\d])\s*\n*\s*(\S[^\n]{{0,60}})",
                                 body):
                bucket = out.setdefault(number_key(norm_number(m.group(1))), [])
                for b in bucket:
                    if b["section_id"] == sid:
                        b.setdefault("dump_head", m.group(2))
                if not any(b["section_id"] == sid for b in bucket):
                    bucket.append(dict(base, dump_head=m.group(2), cited=True))
            if body.count("|") >= 6:
                for m in re.finditer(rf"(?i)\btables?\s+({NUM})(?![\d])", body):
                    num = norm_number(m.group(1))
                    if body_has_cells(body, num):
                        bucket = out.setdefault(number_key(num), [])
                        if not any(b["section_id"] == sid and b.get("body_cells")
                                   for b in bucket):
                            bucket.append(dict(base, body_cells=True))
    return out


def choose_section(secs: list[dict], chapter, volume=None) -> "dict | None":
    """The stored section a row names: one that lists the table, in the
    table's own chapter (and volume) first; else one whose body types it."""
    listed = [s for s in secs if s.get("listed")]
    pool = listed or [s for s in secs if s.get("body_cells")]
    if not pool:
        return None
    if volume is not None:
        same_vol = [s for s in pool if s.get("volume") in (None, volume)]
        pool = same_vol or pool
    same = [s for s in pool if chapter is not None
            and str(s.get("chapter")) == str(chapter)]
    return (same or pool)[0]


def typed_sections(cfg: dict, num: str, secs: list[dict]) -> list[dict]:
    """The sections whose ``tables`` entry or body carries cells of the
    table (before the check that they carry all of them); ``cfg`` is the
    row's :data:`CONFIG` (its volume's, :func:`_cfg`)."""
    typed = [s for s in secs
             if (s.get("cells") and not cfg.get("entries_describe"))
             or s.get("body_cells")]
    return [s for s in typed
            if s["section_id"] not in cfg.get("not_typed", {}).get(num, [])]


def typed_text(s: dict) -> str:
    """What a typed section holds of a table: its ``tables`` entry, or its
    body where the body types the table."""
    return s.get("entry_full") if s.get("cells") else s.get("body_text") or ""


def choose_values(cfg: dict, num: str, secs: list[dict],
                  lookups: list[str],
                  coverage: "dict | None" = None) -> tuple[str, "str | None"]:
    """``(values, values_in)`` of one row: "text" and the section when a
    stored section types every cell of the table (a ``tables`` entry or
    the body; :func:`coverage_ok` on the page, or read on the render,
    ``text_by_render``), else "lookup" and the first confirmed function,
    else "page". ``cfg`` is the row's :data:`CONFIG` (its volume's)."""
    forced = cfg.get("values", {}).get(num)
    if forced:
        return forced[0], forced[1]
    by_render = cfg.get("text_by_render", {}).get(num)
    typed = [s for s in typed_sections(cfg, num, secs)
             if s["section_id"] == by_render
             or (coverage is not None and s["section_id"] in coverage
                 and coverage_ok(coverage[s["section_id"]]))]
    if typed:
        return "text", typed[0]["section_id"]
    if lookups:
        return "lookup", lookups[0]
    return "page", None


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def _rows_from_pdf(doc, cfg: dict) -> tuple[list[dict], dict]:
    """Rows and stats for one PDF."""
    runs = find_list_runs(doc, cfg)
    list_pages = [p for run in runs for p in run]
    entries = [e for run in runs for e in parse_list(doc, run, cfg)]
    drop = {number_key(n) for n in cfg.get("drop", [])}
    entries = [e for e in entries if number_key(e["table_number"]) not in drop]
    start = cfg.get("body_start", (runs[0][-1] + 1) if runs else 0)
    end = min(cfg.get("body_end", doc.page_count), doc.page_count)
    body = _scan_body(doc, start, end, cfg)
    for p in list_pages:        # a chapter's List of Tables inside the body
        body.pop(p, None)
    if entries:
        rows = resolve_rows(doc, entries, body, cfg, start, end)
        # tables the body prints under a caption that the list leaves out
        # (UFS 3-220-10 lists no appendix tables)
        listed = {number_key(e["table_number"]) for e in rows}
        for extra in rows_from_body(doc, body, cfg):
            key = number_key(extra["table_number"])
            if key not in listed and key not in drop \
                    and not cfg.get("list_complete"):
                extra["how"] = "not in list"
                rows.append(extra)
                listed.add(key)
    else:
        rows = rows_from_body(doc, body, cfg)
        rows = [r for r in rows if number_key(r["table_number"]) not in drop]
    for r in rows:
        if r.get("pdf_page_index") is not None:
            cap = r.get("page_caption") or r["caption"]
            r["pages"] = [r["pdf_page_index"]] + _continuations(
                doc, body, r["pdf_page_index"], r["table_number"], cap, end)
    stats = {"list_pages": list_pages, "list_entries": len(entries),
             "body_start": start}
    return rows, stats


def _apply_renders(rows: list[dict], cfg: dict, doc) -> list[dict]:
    """Pages, captions and rows read off the rendered pages (CONFIG)."""
    pages = cfg.get("page_from_render", {})
    caps = cfg.get("caption_from_render", {})
    more = cfg.get("pages_from_render", {})
    for r in rows:
        num = r["table_number"]
        if num in pages:
            got = pages[num]
            r["pdf_page_index"] = got[0] if isinstance(got, list) else got
            r["pages"] = got if isinstance(got, list) else [got]
            r["how"] = "render"
            # the caption matched on the wrong page is not this table's;
            # the list's caption stands unless one was read off the render
            r["page_caption"] = None
        if num in caps:
            r["page_caption"] = caps[num]
            r["how"] = r["how"] if r["how"] == "render" else (r["how"] or "") + "+caption render"
        if num in more:
            r["pages"] = more[num]
    for extra in cfg.get("rows_from_renders", []):
        row = dict(extra)
        if row.get("printed_page"):
            row["_render_page"] = True      # read off the render with the row
        row.setdefault("list_page", row.pop("printed_page", None))
        row.setdefault("pages", [row["pdf_page_index"]])
        row["page_caption"] = row["caption"]
        row["how"] = "render"
        rows.append(row)
    if cfg.get("rows_from_renders") and cfg.get("renders_replace"):
        rows = [r for r in rows if r["how"] == "render"]
    return rows


def choose_caption(list_cap: str, page_cap: "str | None", how: "str | None") -> str:
    """The caption a row keeps: the one printed over the table, unless the
    page's text layer lost a symbol the list prints ("when T = 0 E" for
    "when ω = 0°", NHI-06-089 Table 9-6a) or the page's caption was not
    matched to the list's (``how`` "label only", read off the render)."""
    if not page_cap or how in ("label only", "estimated", "not found"):
        return list_cap or page_cap or ""
    if how in ("near caption", "caption") and list_cap:
        # (UFC 3-220-20 Table 4-2: the page's "( - = - =0 ° )" for the
        # list's "(β=θ=0°)")
        lost = {ch for ch in list_cap
                if (not ch.isascii() and ch.isalpha()) or ch in "°±≤≥"}
        if lost - set(page_cap):
            return list_cap
    return page_cap


def _plain_math(text: str) -> str:
    """Letters and digits set in the Unicode mathematical alphanumeric
    block (a caption's italic "𝑵 𝟔𝟎", GEC-5 Appendix A2) as the plain
    characters they are, so a search for "N60" finds them; nothing else
    changes."""
    import unicodedata
    return "".join(unicodedata.normalize("NFKC", ch)
                   if 0x1D400 <= ord(ch) <= 0x1D7FF else ch
                   for ch in text or "")


def _row_sections(sections: dict, num: str, vol=None) -> list[dict]:
    """The stored sections that name a table number (:func:`text_sections`)."""
    secs = sections.get(number_key(num), [])
    if not secs and re.search(r"\d[A-Za-z]$", num):
        # a section that lists "Table 5-4" for the parts 5-4a and 5-4b
        secs = sections.get(number_key(num[:-1]), [])
    if vol is not None:
        # a number printed in both volumes: the sections of this volume
        secs = [s for s in secs if s.get("volume") in (None, vol)] or secs
    return secs


def build_catalog(package: str, audit: "dict | None" = None,
                  write: bool = True) -> dict:
    """Build (and write) ``tables_catalog.json`` for one package."""
    manifest = _load_manifest(package)
    volumes = manifest.get("volumes") or [None]
    rows_out: list[dict] = []
    stats_all = []
    sections = text_sections(package)
    for vi, vol in enumerate(volumes):
        cfg = _cfg(package, vi)
        if cfg.get("skip"):
            continue
        rel = _repo_relative_pdf_path(vol if vol else manifest)
        doc = _open_pdf(rel)
        try:
            rows, stats = _rows_from_pdf(doc, cfg)
            rows = _apply_renders(rows, cfg, doc)
            for r in rows:
                pages = r.get("pages") or ([r["pdf_page_index"]]
                                           if r.get("pdf_page_index") is not None else [])
                token = r.get("list_page")
                plist = []
                for k, p in enumerate(pages):
                    t = _shift_token(token, p - pages[0]) if token else None
                    if k and t and not _page_token_holds(doc, p, t):
                        t = None
                    plist.append({"pdf_page_index": p, "printed_page": t})
                r["_pages"] = plist
                r["_pdf"] = rel
                r["_vol"] = vol
                r["_confirmed_text"] = r.get("how") in ("caption", "near caption",
                                                         "body caption")
                if cfg.get("caption_from_text") and pages:
                    r["_text"] = doc[pages[0]].get_text()
                r["_cfg"] = cfg
                if r.get("pdf_page_index") is not None:
                    r["_label"] = page_label(doc[r["pdf_page_index"]])
                typed = typed_sections(cfg, r["table_number"], _row_sections(
                    sections, r["table_number"], vol.get("volume") if vol else None))
                if typed and pages:
                    region = table_region(doc, pages, r["table_number"],
                                          bool(cfg.get("ocr")))
                    r["_coverage"] = {
                        s["section_id"]: {**cell_coverage(region, typed_text(s)),
                                          "entry": bool(s.get("cells"))}
                        for s in typed}
        finally:
            doc.close()
        stats["pdf"] = rel
        stats_all.append(stats)
        rows_out.extend(rows)

    lookups = find_lookups(package, rows_out)
    cfg_all = CONFIG.get(package, {})
    prologue = cfg_all.get("prologue", "P")
    out_rows = []
    for r in rows_out:
        num = r["table_number"]
        # the row's own volume's settings (a number may be printed in both)
        rc = r.get("_cfg") or cfg_all
        cap = rc.get("caption_from_render", {}).get(num) or choose_caption(
            r["caption"], r.get("page_caption"), r.get("how"))
        cap = _plain_math(cap)
        chapter = r.get("chapter", chapter_of(num, prologue))
        if num in rc.get("chapter_from_render", {}):
            chapter = rc["chapter_from_render"][num]
        starts = cfg_all.get("chapter_starts")
        if chapter is None and starts and r.get("pdf_page_index") is not None \
                and re.fullmatch(r"\d+", num):
            before = [c for c, p in starts.items() if p <= r["pdf_page_index"]]
            chapter = max(before, key=lambda c: starts[c]) if before else None
        vol = r["_vol"].get("volume") if r.get("_vol") else None
        secs = _row_sections(sections, num, vol)
        sec = choose_section(secs, chapter, vol)
        if num in rc.get("section_from_render", {}):
            sid = rc["section_from_render"][num]
            sec = next((s for ss in sections.values() for s in ss
                        if s["section_id"] == sid
                        and s.get("volume") in (None, vol)), None)
            if sec is None:
                raise KeyError(f"{package}: section {sid} for Table {num} "
                               "is not in the chapter text")
        if r.get("_text") and num not in rc.get("caption_from_render", {}):
            # an OCR text layer garbles the caption ("settlenlent"): the
            # stored section's title for the table, where most of its words
            # are on the page
            for s in [x for x in secs if x.get("listed")]:
                title = s.get("entry_title") or ""
                if len(title) >= 8 and words_on_page(r["_text"], title):
                    cap = _plain_math(title)
                    break
        impl = [_short_path(package, p) for p in lookups.get(num, [])]
        plain = [_short_path(package, p) for p in lookups.get(num, [])
                 if _plain_call(p)]
        values, values_in = choose_values(rc, num, secs, plain,
                                          r.get("_coverage"))
        pages = [p["pdf_page_index"] for p in r.get("_pages") or []]
        rec = {
            "table_number": num,
            "caption": cap,
            "chapter": chapter,
            "section_id": sec["section_id"] if sec else None,
            "section_title": sec["title"] if sec else None,
            "pdf_page_index": r.get("pdf_page_index"),
            "pages": pages or ([r["pdf_page_index"]]
                               if r.get("pdf_page_index") is not None else []),
            "printed_page": _printed_page(rc, r),
            "page_estimated": r.get("how") in ("estimated", "not found"),
            "values": values,
            "values_in": values_in,
        }
        if impl:
            rec["implemented_in"] = impl
        if r.get("_vol"):
            rec["pdf_path"] = r["_pdf"]
            rec["volume"] = vol
            if r["_vol"].get("reference_id"):
                rec["reference_id"] = r["_vol"]["reference_id"]
        if r.get("picture") or num in rc.get("pictures", ()):
            rec["printed_as_picture"] = True
        note = r.get("note") or rc.get("notes", {}).get(num)
        if not note and values == "page" and impl and not plain:
            note = (f"{impl[0]} codes this table for a Python caller: it "
                    "takes functions as inputs, so a call with plain values "
                    "cannot run it. Read the table off the page.")
        if not note and values == "page" and rc.get("dump_note"):
            # the body holds the text layer's cells of this table
            head = _norm(" ".join(re.findall(r"[A-Za-z0-9]+", cap)[:3]))
            dumps = [s for s in secs if s.get("dump_head") and head
                     and _norm(s["dump_head"]).startswith(head)]
            if dumps:
                note = (f"Section {dumps[0]['section_id']} carries this "
                        "table's cells as the PDF text layer gives them, in "
                        "reading order without its rows and columns; read "
                        "the table off the page.")
        entries = {sid: c for sid, c in (r.get("_coverage") or {}).items()
                   if c["entry"] and c["cov"] >= 0.3}
        if not note and values == "page" and entries:
            # a section's entry for the table types part of it: a third of
            # its numbers and row labels or more, not all (cell_coverage,
            # coverage_ok)
            best = max(entries, key=lambda sid: entries[sid]["cov"])
            note = (f"Section {best} types part of this table: a check "
                    "against the page did not find all of its cells in the "
                    "section's entry. Read the values off the page.")
        if note:
            rec["note"] = note
        out_rows.append(rec)
        if audit is not None:
            audit.setdefault(package, []).append({
                "table_number": num, "how": r.get("how"),
                "ratio": r.get("ratio"), "list_caption": r["caption"],
                "kept": cap,
                "page_caption": r.get("page_caption"),
                "pdf_page_index": r.get("pdf_page_index"),
                "pages": [p["pdf_page_index"] for p in r.get("_pages") or []],
                "pdf": r["_pdf"], "list_page": r.get("list_page"),
                "printed_page": rec["printed_page"], "label": r.get("_label"),
                "values": values, "values_in": values_in,
                "section_id": rec["section_id"], "impl": impl,
                "coverage": r.get("_coverage"),
                "secs": [{k: s.get(k) for k in ("section_id", "listed", "cells",
                                                 "body_cells", "entry")}
                         for s in secs]})
    # every table a stored section lists must be a row (or be reported)
    have = {number_key(r["table_number"]) for r in out_rows}
    # a listed "5-4" printed as parts 5-4a and 5-4b is a row
    have |= {k[:-1] for k in have if re.search(r"\d[A-Z]$", k)}
    # a table a section names that the manual cites and does not print
    have |= {number_key(n) for n in cfg_all.get("not_printed", {})}
    unlisted = sorted({s["section_id"] + " -> " + k for k, ss in sections.items()
                       for s in ss if s.get("listed") and k not in have})
    if audit is not None:
        audit.setdefault("_listed_not_rows", {})[package] = unlisted
    if unlisted:
        print(f"[{package}] listed in the text but not a row: {len(unlisted)}: "
              + "; ".join(unlisted[:40]))

    first = volumes[0]
    catalog = {
        "reference_id": manifest.get("reference_id", ""),
        "reference_title": manifest.get("reference_title", ""),
        "package": package,
        "volume": manifest.get("volume"),
        "pdf_path": _repo_relative_pdf_path(first if first else manifest),
        "table_count": len(out_rows),
        "tables": out_rows,
    }
    n_est = sum(1 for r in out_rows if r["page_estimated"])
    n_impl = sum(1 for r in out_rows if r.get("implemented_in"))
    print(f"[{package}] {len(out_rows)} tables (list entries "
          f"{sum(s['list_entries'] for s in stats_all)}; page estimated {n_est}; "
          f"with a lookup {n_impl}; continued "
          f"{sum(1 for r in out_rows if len(r.get('pages') or []) > 1)}; values "
          f"{dict(sorted((v, sum(1 for r in out_rows if r['values'] == v)) for v in ('text', 'lookup', 'page')))})")
    if write:
        out_path = _PACKAGE_DIR / package / "tables_catalog.json"
        out_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    return catalog


# ---------------------------------------------------------------------------
# Verify a written catalog against its pages
# ---------------------------------------------------------------------------

#: characters an OCR text layer prints for a digit or annex letter
#: (EN 1997-1/-2 scans: "Table A.S" for A.5, "Table H.l" for H.1,
#: "Table 0.5" for D.5, "'rable 3.1")
_OCR_ALIKE = {"1": "1iIl!", "5": "5sS", "0": "0oO", "O": "OD0", "D": "DO0"}


def _ocr_part(p: str) -> str:
    return "".join(f"[{re.escape(_OCR_ALIKE[c])}]" if c in _OCR_ALIKE
                   else re.escape(c) for c in p)


def label_on_page(text: str, num: str, ocr: bool = False) -> bool:
    """Whether a page's text prints the label ``Table <num>`` (any dash or
    '.', spaces inside, upper or lower case). ``ocr``: the page's text
    layer is a scan's OCR, so a digit may read as its look-alike letter
    and the word as "'rable"."""
    n = norm_number(num)
    letter = ""
    m = re.search(r"(?<=\d)([a-zA-Z])$", n)
    if m:
        n, letter = n[:-1], m.group(1)
    parts = [(_ocr_part(p) if ocr else re.escape(p))
             for p in re.split(r"[-.]", n) if p]
    sep = rf"\s*[-.,{_DASHES}]?\s*" if ocr else rf"\s*[-.{_DASHES}]?\s*"
    body = sep.join(parts)
    if letter:
        body += rf"\s*\(?{letter}\)?"
    word = r"(?:table|\Sable|ta\Sle|tab\Se)" if ocr else r"\btable"
    rx = re.compile(rf"(?i){word}\s*{body}(?![\d])")
    return bool(rx.search(text.translate(_SMART)))


def words_on_page(text: str, phrase: str, share: float = 0.7) -> bool:
    """Whether at least ``share`` of a phrase's words (three letters or
    more, the first ten) are in a page's text: a caption checked against
    an OCR text layer that misreads a letter here and there."""
    words = [w.lower() for w in re.findall(r"[A-Za-z]{3,}", phrase or "")][:10]
    if len(words) < 2:
        return False
    page = re.sub(r"\s+", " ", _plain_math(text.translate(_SMART)).lower())
    return sum(1 for w in words if w in page) / len(words) >= share


def contents_page(text: str) -> bool:
    """Whether a page is a contents page or List of Tables (four or more
    lines ending in dot leaders and a page number): it names a table
    without printing it."""
    return len(re.findall(rf"\.{{5,}}[ \t]*[A-Za-z]{{0,2}}[-{_DASHES}]?\d{{1,4}}"
                          rf"(?:[-{_DASHES}]\d{{1,4}})?[ \t]*$", text, re.M)) >= 4


def row_on_page(package: str, text: str, row: dict) -> tuple[bool, bool]:
    """``(label, caption)``: whether a catalog row's label and caption are
    on its page's text, by the rule its reference's text layer allows
    (:data:`CONFIG` ``ocr``)."""
    ocr = bool(CONFIG.get(package, {}).get("ocr"))
    lab = label_on_page(text, row["table_number"], ocr=ocr)
    cap = caption_on_page(text, row["caption"])
    if not cap and ocr:
        cap = words_on_page(text, row["caption"])
    return lab, cap


def caption_on_page(text: str, caption: str, words: int = 4) -> bool:
    """Whether a page's text prints the caption's first ``words`` words
    (letters and digits only, so line breaks and garbled symbols do not
    count)."""
    toks = re.findall(r"[A-Za-z0-9]+", caption or "")
    want = _norm(" ".join(toks[:words]))
    if len(want) < 6:
        want = _norm(" ".join(toks[:words + 3]))
    return bool(want) and want in _norm(_plain_math(text.translate(_SMART)))


def verify_catalog(package: str) -> list[dict]:
    """Check every row of a written catalog on its page: the label and the
    caption's first words on ``pdf_page_index``. Returns the rows that fail
    either, each with ``label`` / ``caption`` booleans (a table printed as
    a picture has no text layer: both fail, and the row is read off the
    render)."""
    cat = json.loads((_PACKAGE_DIR / package / "tables_catalog.json")
                     .read_text(encoding="utf-8"))
    out = []
    docs: dict = {}
    try:
        for r in cat["tables"]:
            rel = r.get("pdf_path") or cat["pdf_path"]
            if rel not in docs:
                docs[rel] = _open_pdf(rel)
            doc = docs[rel]
            text = doc[r["pdf_page_index"]].get_text()
            lab, cap = row_on_page(package, text, r)
            contents = contents_page(text)
            if not (lab and cap) or contents:
                out.append({"table_number": r["table_number"],
                            "pdf_page_index": r["pdf_page_index"],
                            "pdf": rel, "label": lab and not contents,
                            "caption": cap,
                            "caption_text": r["caption"][:90],
                            "picture": bool(r.get("printed_as_picture"))})
    finally:
        for d in docs.values():
            d.close()
    return out


def _packages() -> list[str]:
    out = []
    for mf in sorted(_MANIFEST_DIR.glob("*.json")):
        if not (_PACKAGE_DIR / mf.stem).is_dir():
            continue
        data = json.loads(mf.read_text(encoding="utf-8"))
        # a reference with chapter text and a PDF (the tables a section
        # lists are what the catalog must resolve)
        if (data.get("pdf_path") or data.get("volumes")) \
                and (_PACKAGE_DIR / mf.stem / "text").is_dir() \
                and not CONFIG.get(mf.stem, {}).get("no_tables"):
            out.append(mf.stem)
    return out


def main(argv: list[str]) -> int:
    audit_path = None
    if argv[:1] == ["--audit"]:
        audit_path, argv = argv[1], argv[2:]
    dry = False
    if argv[:1] == ["--dry-run"]:
        dry, argv = True, argv[1:]
    if argv[:1] == ["--verify"]:
        targets = _packages() if argv[1:] == ["all"] else argv[1:]
        bad = 0
        for pkg in targets:
            flagged = verify_catalog(pkg)
            bad += len(flagged)
            print(f"[{pkg}] rows not confirmed on their page: {len(flagged)}")
            for f in flagged:
                print(f"   {f['table_number']:>8} p={f['pdf_page_index']} "
                      f"label={f['label']} caption={f['caption']} "
                      f"picture={f['picture']} \"{f['caption_text']}\"")
        return 1 if bad else 0
    if not argv:
        print(__doc__)
        print("Packages:", ", ".join(_packages()))
        return 1
    targets = _packages() if argv == ["all"] else argv
    audit: dict = {}
    rc = 0
    for pkg in targets:
        try:
            build_catalog(pkg, audit, write=not dry)
        except Exception as e:  # noqa: BLE001
            print(f"[{pkg}] FAILED: {type(e).__name__}: {e}")
            rc = 1
    if audit_path:
        Path(audit_path).write_text(json.dumps(audit, indent=1, ensure_ascii=False),
                                    encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
