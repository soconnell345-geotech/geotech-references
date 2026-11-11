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
#: PDFs not committed to docs/ (the Wood Handbook) are read from the main
#: checkout's docs/ when this is a worktree; the catalog still names
#: ``docs/<file>``.
_FALLBACK_DOCS = [Path("C:/dev/GeotechStaffEngineer/geotech-references/docs")]

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
    markers = [m for m in _LIST_MARKER.finditer(blob)
               if re.search(r"(?:^|\n|\.{2,}[ .]*[\w-]*\d)[ \t]*$",
                            blob[:m.start()][-20:] or "\n")]
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
    "fhwa_pavements": {"list_mode": "bare", "list_pages": (16, 20),
                       "list_noise": r"^Geotechnical Aspects of Pavements"},
    "fhwa_soils_foundations": {"list_mode": "bare", "volumes": [
        {"list_pages": (26, 28)}, {"list_pages": (23, 24)}]},
    # every chapter opens with its own contents and List of Tables
    "gec_13": {"list_all": True},
}

#: (reference, table number, function) a name or docstring search pairs but
#: which does not code that table (it cites another manual's table of the
#: same number, or a table of another chapter), found by opening each.
NOT_IMPLEMENTED_BY: set[tuple[str, str, str]] = set()


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


def _scan_body(doc, start: int, end: int, cfg: dict) -> dict[int, list[dict]]:
    num_ok = re.compile(cfg["numbers"]) if cfg.get("numbers") else None
    out: dict[int, list[dict]] = {}
    for i in range(start, end):
        cands = caption_candidates(page_lines(doc[i]))
        if num_ok is not None:
            cands = [c for c in cands if num_ok.fullmatch(c["number"])]
        if cands:
            out[i] = cands
    return out


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


def _continuations(doc, body: dict, start: int, num: str, caption: str,
                   end: int) -> list[int]:
    """Pages straight after ``start`` that print the table's label again."""
    pages = []
    i = start + 1
    nc = _norm(caption)[:15]
    while i < end:
        hit = False
        for c in body.get(i, []):
            if number_key(c["number"]) != number_key(num):
                continue
            text, _ = caption_text(c, caption)
            if c["continued"] or (nc and _norm(text).startswith(nc)) or \
                    _norm(c["rest"]).startswith("cont"):
                hit = True
        if not hit:
            break
        pages.append(i)
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
        for i, c in by_num.get(key, []):
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
            if key in rows:
                continue
            text, _ = caption_text(c)
            if len(text) < 3:
                continue
            rows[key] = {"table_number": c["number"], "caption": text,
                         "list_page": None, "pdf_page_index": i,
                         "page_caption": text, "ratio": 1.0, "how": "body caption"}
            order.append(key)
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
    return re.compile(r"(?:^|_)table_?" + "_?".join(re.escape(p) for p in parts)
                      + r"(?![0-9a-z])")


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
        found = []
        for path, name, doc in funcs:
            if nrx.search(name) or crx.search(doc.split("\n\n")[0] + "\n" + doc):
                if (package, num, path.rsplit(".", 1)[1]) in NOT_IMPLEMENTED_BY:
                    continue
                found.append(path)
        if found:
            out[num] = sorted(found)
    return out


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
    m = re.match(rf"(?i)^(?:table\s+)?({NUM})(?![\d])", raw)
    return norm_number(m.group(1)) if m else None


def text_sections(package: str) -> dict[str, list[str]]:
    """``{number key: [section ids]}`` of the chapter-text sections whose
    ``tables`` list names the table."""
    out: dict[str, list[str]] = {}
    tdir = _PACKAGE_DIR / package / "text"
    if not tdir.is_dir():
        return out
    for jf in sorted(tdir.glob("*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for sec in _walk(data.get("sections")):
            for t in sec.get("tables") or []:
                num = table_ref_number(t)
                sid = sec.get("section_id")
                if num and sid:
                    bucket = out.setdefault(number_key(num), [])
                    if sid not in bucket:
                        bucket.append(sid)
    return out


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
        if num in caps:
            r["page_caption"] = caps[num]
            r["how"] = r["how"] if r["how"] == "render" else (r["how"] or "") + "+caption render"
        if num in more:
            r["pages"] = more[num]
    for extra in cfg.get("rows_from_renders", []):
        row = dict(extra)
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
    if how == "near caption" and list_cap:
        lost = {ch for ch in list_cap
                if (not ch.isascii() and ch.isalpha()) or ch in "°±≤≥"}
        if lost - set(page_cap):
            return list_cap
    return page_cap


def build_catalog(package: str, audit: "dict | None" = None,
                  write: bool = True) -> dict:
    """Build (and write) ``tables_catalog.json`` for one package."""
    manifest = _load_manifest(package)
    volumes = manifest.get("volumes") or [None]
    rows_out: list[dict] = []
    stats_all = []
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
        finally:
            doc.close()
        stats["pdf"] = rel
        stats_all.append(stats)
        rows_out.extend(rows)

    lookups = find_lookups(package, rows_out)
    sections = text_sections(package)
    prologue = CONFIG.get(package, {}).get("prologue", "P")
    out_rows = []
    for r in rows_out:
        num = r["table_number"]
        cap = choose_caption(r["caption"], r.get("page_caption"), r.get("how"))
        chapter = r.get("chapter", chapter_of(num, prologue))
        starts = CONFIG.get(package, {}).get("chapter_starts")
        if chapter is None and starts and r.get("pdf_page_index") is not None \
                and re.fullmatch(r"\d+", num):
            before = [c for c, p in starts.items() if p <= r["pdf_page_index"]]
            chapter = max(before, key=lambda c: starts[c]) if before else None
        rec = {
            "table_number": num,
            "caption": cap,
            "chapter": chapter,
            "pdf_page_index": r.get("pdf_page_index"),
            "printed_page": r.get("list_page"),
            "page_estimated": r.get("how") in ("estimated", "not found", "label only"),
        }
        if len(r.get("_pages") or []) > 1:
            rec["pages"] = r["_pages"]
        if r.get("_vol"):
            rec["pdf_path"] = r["_pdf"]
            rec["volume"] = r["_vol"].get("volume")
            if r["_vol"].get("reference_id"):
                rec["reference_id"] = r["_vol"]["reference_id"]
        if lookups.get(num):
            rec["implemented_in"] = lookups[num]
        secs = sections.get(number_key(num))
        if secs:
            rec["text_sections"] = secs
        if r.get("note"):
            rec["note"] = r["note"]
        out_rows.append(rec)
        if audit is not None:
            audit.setdefault(package, []).append({
                "table_number": num, "how": r.get("how"),
                "ratio": r.get("ratio"), "list_caption": r["caption"],
                "kept": cap,
                "page_caption": r.get("page_caption"),
                "pdf_page_index": r.get("pdf_page_index"),
                "pages": [p["pdf_page_index"] for p in r.get("_pages") or []],
                "pdf": r["_pdf"], "list_page": r.get("list_page")})

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
          f"with a lookup {n_impl}; continued {sum(1 for r in out_rows if r.get('pages'))})")
    if write:
        out_path = _PACKAGE_DIR / package / "tables_catalog.json"
        out_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    return catalog


def _packages() -> list[str]:
    out = []
    for mf in sorted(_MANIFEST_DIR.glob("*.json")):
        if not (_PACKAGE_DIR / mf.stem).is_dir():
            continue
        data = json.loads(mf.read_text(encoding="utf-8"))
        if (data.get("pdf_path") or data.get("volumes")) \
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
