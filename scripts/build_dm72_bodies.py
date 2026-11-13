"""Build the section bodies of UFC 3-220-20 (DM 7.2) from the printed pages (REF-94).

UFC 3-220-20, Foundations and Earth Structures (16 January 2025), package
``dm7_2``. Its section bodies were written by hand as condensed accounts; this
script replaces each section's ``body`` with the print's own wording, from the
section's heading to the next heading, and leaves every other field of the
chapter file as it is (section ids, titles, summary, key points,
applicability, equations, figures, tables, links): those were checked against
the print field by field and are not rebuilt here. A rebuild reproduces the
committed bodies; every hand-typed line is in the manifest
(``scripts/manifests/dm7_2_bodies.json``).

The printed page number is the PDF page number less 38 (PDF p. 546 prints
"508"; the build checks each page's printed number against it).

How a page is read (PyMuPDF text layer, one column, single font family):

* the running header ("UFC 3-220-20 / 16 January 2025") and the page number
  are left out; a ``[p. 508]`` marker is put where each printed page's text
  starts;
* prose is set in Arial 12 pt; a line is prose when most of its characters
  are Arial of 11 pt or more. Lines in smaller Arial are a table's cells, a
  table's notes or a figure's lettering, and are left out (a table the old
  bodies held typed in is put back from the manifest, see below). Text
  inside a picture's frame is a figure's lettering and is left out;
* a line set wholly in Times New Roman and Symbol is a piece of an equation
  object (the text layer gives its glyphs one or a few to a line). Those
  pieces are grouped into printed formula lines by their height on the page.
  A group beside a printed number "(7-5)" is that numbered equation: it is
  stored as ``[Eq. 7-5]`` followed by the formula as the section's checked
  ``equations`` entry states it (the manifest's ``equation_formulas`` names
  the words of the entry that are the formula; the build checks they are in
  the entry, so the two cannot disagree). A group with no number is an
  unnumbered formula line, typed in from a 300 dpi render of the page
  (manifest ``formulas``, keyed by printed page and height); the build stops
  if one is not typed in;
* a prose line that carries a formula (an equals sign beside an operator, an
  exponent, a root or a sum) is listed by ``--report``; each such line was
  read on the render, and where the text layer does not give it as printed
  the manifest's ``lines`` (printed page and height) gives the line typed in;
* within a prose line, characters set smaller and raised are superscripts
  (stored as superscript characters, "σ²", or "^(...)" where there is no
  such character) and those set smaller and lowered are subscripts (stored
  in line, "COVw", as the earlier bodies did); a raised number in Arial is a
  footnote mark;
* a numbered footnote (Arial 10 pt at the foot of the page) is taken out of
  the page's text and stored at its mark as ``[Footnote 41: ...]``, in the
  words the earlier bodies held (those were read against the print; the
  manifest's ``footnotes``);
* a heading is a bold line beginning at the heading indent; it starts the
  section of the chapter file whose title it prints (sections are matched in
  order). A numbered heading that has no section in the chapter file
  ("7-6 SUGGESTED READING") ends the section before it, and its text is not
  stored;
* paragraphs are where the print leaves a gap between lines or starts a
  list item (a bullet, an indented "o", "1." or "1)"); a list set in two
  columns reads down the left column, then the right; a paragraph runs on
  across a page, a figure or a table when its last line before them is full
  and does not end a sentence; a blank page's "This Page Intentionally Left
  Blank" is left out;
* a figure's caption ("Figure 7-3 Use of Random Variables ...") is a
  paragraph of its own where the figure is printed. A table's caption is
  followed by the table typed in, where an earlier body held it typed in
  (manifest ``typed_tables``, kept as checked; text tables the earlier
  bodies held as condensed accounts, the prologue's Tables P-2 to P-8 and
  Tables 3-10 and 3-11, typed in from the page instead, row by row), or
  else by the line
  "[Table 7-2: values on printed p. 512; not typed in]"; then the table's
  notes the earlier bodies held (manifest ``table_notes``). A figure or table
  printed inside a paragraph is put after that paragraph, with its page
  marker, and the text after it repeats its own page marker;
* the notes the earlier bodies carried about the print's own slips ("As
  printed ...") are put back after the same words (manifest ``notes``);
* ``fixes`` mend a body where the text layer differs from the rendered page
  (each with the page and why).

Usage::

    python scripts/build_dm72_bodies.py                 # write the built chapters
    python scripts/build_dm72_bodies.py --chapter chapter07 --report
    python scripts/build_dm72_bodies.py --chapter chapter07 --dump out.txt

Requires PyMuPDF.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:  # older PyMuPDF
    import fitz

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
PKG = REPO / "geotech_references" / "dm7_2"
TEXT = PKG / "text"
MANIFEST = SCRIPTS / "manifests" / "dm7_2_bodies.json"

#: Fields of a section that this build never changes.
KEPT = ("section_id", "title", "summary", "key_points", "equations", "figures",
        "tables", "applicability", "implemented_in", "cross_references")
#: A section body is split into lettered parts above this many characters,
#: or when the section as JSON (a Greek letter is six characters there) is
#: over MAX_SECTION_JSON, as build_printed_text.split_long does, so that a
#: section fetched through the app's reference tools fits its result.
MAX_BODY = 12000
MAX_SECTION_JSON = 14000

SUPER = str.maketrans("0123456789+-−=()niax", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁻⁼⁽⁾ⁿⁱᵃˣ")
_SUPER_OK = set("0123456789+-−=()niax")
#: an equation's printed number at the right margin; a few are printed
#: without the brackets ("7-11.", "7-12", p. 535)
# (A-3): the prologue prints its three-parameter power function so (p. 4)
_EQNUM = re.compile(r"^\(?\s*([PAB1-7]-\d+[a-z]?)\s*\)?\s*[.,;:]?$")
_CAPTION = re.compile(r"^(Figure|Table)\s+([PB1-7]-\d+[a-z]?)\b\.?\s*(.*)$")
_HEADNUM = re.compile(r"^([PB1-7]-\d+(?:\.\d+)*)\.?\s+(.*)$")
_OPS = re.compile(r"[+\-−×·*/÷^√Σ∑²³½]")


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def chapter_json(data: dict) -> str:
    """A chapter file's text as the library writes it."""
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def kept_hash(sections: list[dict]) -> str:
    """A digest of every field this build keeps, for every section."""
    rows = [{k: v for k, v in s.items() if k != "body"} for s in sections]
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True)
                          .encode("utf-8")).hexdigest()


# --- reading a page ---------------------------------------------------------

def _is_arial(font: str) -> bool:
    return font.startswith("Arial")


def _is_bold(font: str) -> bool:
    return "Bold" in font


class Row:
    """One printed line: the text-layer lines that share a baseline."""

    def __init__(self, lines):
        self.lines = sorted([ln for ln in lines if not ln.get("attached")],
                            key=lambda ln: ln["bbox"][0])
        # left to right within a line too: the text layer gives the u of
        # "su" before the s on p. 56 (a blank goes by its right end, as the
        # one after the γ of "γt" starts under the γ)
        def place(s):
            return s["bbox"][0] if s["text"].strip() else s["bbox"][2] - 0.5

        self.spans = [s for ln in self.lines
                      for s in sorted(ln["spans"], key=place) if s["text"]]
        put: list[int] = []  # ids of the spans put back in

        def centre(s):
            return (s["bbox"][0] + s["bbox"][2]) / 2

        for ln in lines:
            if ln.get("attached"):
                for a in ln["spans"]:
                    if not a["text"].strip():
                        continue
                    k = 0
                    # past the spans that end before it, and past one put
                    # back earlier whose middle is left of its middle (the
                    # Vm set under the δ's right side)
                    while k < len(self.spans) and (
                            self.spans[k]["bbox"][2] <= a["bbox"][0] + 1.5
                            or (id(self.spans[k]) in put and centre(self.spans[k]) < centre(a))):
                        k += 1
                    self.spans.insert(k, a)
                    put.append(id(a))
        self.lines = sorted(lines, key=lambda ln: ln["bbox"][0])
        self.x0 = min(ln["bbox"][0] for ln in self.lines)
        self.y0 = min(ln["bbox"][1] for ln in self.lines)
        self.x1 = max(ln["bbox"][2] for ln in self.lines)
        self.y1 = max(ln["bbox"][3] for ln in self.lines)
        self.raw = "".join(s["text"] for s in self.spans)
        chars = [(s, len(s["text"].strip())) for s in self.spans]
        tot = sum(n for _, n in chars) or 1
        self.arial12 = sum(n for s, n in chars if _is_arial(s["font"]) and s["size"] >= 11) / tot
        self.arial_small = sum(n for s, n in chars if _is_arial(s["font"]) and s["size"] < 11) / tot
        self.arial = self.arial12 + self.arial_small
        big = [s for s in self.spans if s["text"].strip()]
        self.size = max((s["size"] for s in big), default=0)
        self.bold = bool(big) and all(_is_bold(s["font"]) for s in big if _is_arial(s["font"]))
        self.kind = ""
        self.text = ""

    @property
    def mid(self):
        return (self.y0 + self.y1) / 2

    def __repr__(self):
        return f"<{self.kind} {self.y0:.0f} {self.raw[:50]!r}>"


def _rows(page) -> tuple[list[Row], list]:
    d = page.get_text("dict")
    lines, images = [], []
    for b in d["blocks"]:
        if b["type"] != 0:
            images.append(fitz.Rect(b["bbox"]))
            continue
        for ln in b["lines"]:
            if "".join(s["text"] for s in ln["spans"]).strip():
                lines.append(ln)
    # a line set at the baseline of another (a heading's number and its
    # title, a caption's number and its words) is the same printed line
    lines.sort(key=lambda ln: (round(ln["bbox"][3], 0), ln["bbox"][0]))
    groups: list[list] = []
    for ln in lines:
        base = _baseline(ln)
        for g in groups:
            if (_is_text_line(ln) and _is_text_line(g[0])
                    and abs(_baseline(g[0]) - base) < 1.5):
                g.append(ln)
                break
        else:
            groups.append([ln])
    # a subscript or superscript the text layer gives as a line of its own
    # (the R of "TR", p. 549) goes back into the prose line it is set in
    # and so does a symbol set in the Symbol font on the line's baseline
    # (the δ of "δVm = 2%·H", p. 82)
    text_groups = [g for g in groups if _is_text_line(g[0])]
    keep = []
    for g in groups:
        sizes = [s["size"] for ln in g for s in ln["spans"] if s["text"].strip()]
        if not _is_text_line(g[0]) and sizes and max(sizes) < 13.5:
            x0 = min(ln["bbox"][0] for ln in g)
            y0 = min(ln["bbox"][1] for ln in g)
            y1 = max(ln["bbox"][3] for ln in g)
            small = max(sizes) < 9
            host = None
            for tg in text_groups:
                tx0 = min(ln["bbox"][0] for ln in tg)
                tx1 = max(ln["bbox"][2] for ln in tg)
                ty0 = min(ln["bbox"][1] for ln in tg)
                ty1 = max(ln["bbox"][3] for ln in tg)
                if not tx0 - 2 < x0 < tx1 + 2 or _equation_word(tg):
                    continue
                over = min(y1, ty1) - max(y0, ty0)
                if (small and y0 < ty1 - 1 and y1 > ty0 + 1) or \
                        (over > 0.6 * min(y1 - y0, ty1 - ty0) and abs(y0 - ty0) < 3):
                    host = tg
                    break
            if host is not None:
                host.append({"bbox": g[0]["bbox"], "spans": [s for ln in g for s in ln["spans"]],
                             "attached": True})
                continue
        keep.append(g)
    rows = [Row(g) for g in keep]
    rows.sort(key=lambda r: (r.y0, r.x0))
    return rows, images


def _equation_word(group) -> bool:
    """A short Arial word set inside an equation object ("for" in Eq. 2-6)."""
    text = "".join(s["text"] for ln in group for s in ln.get("spans", [])).strip()
    x0 = min(ln["bbox"][0] for ln in group)
    return x0 > 150 and len(text) <= 15 and not _EQNUM.match(text)


def _baseline(ln) -> float:
    spans = [s for s in ln["spans"] if s["text"].strip()]
    big = max(spans, key=lambda s: s["size"])
    return big["origin"][1]


def _is_text_line(ln) -> bool:
    text = "".join(s["text"] for s in ln["spans"]).strip()
    return text in ("•", "o", "") or any(
        _is_arial(s["font"]) and s["size"] >= 11 and s["text"].strip() for s in ln["spans"])


def _sup(text: str) -> str:
    t = text.strip()
    if t in ("*", "ʹ", "′", "'"):  # y*, a raised prime
        return "ʹ" if t != "*" else "*"
    if t and all(c in _SUPER_OK for c in t):
        return t.translate(SUPER)
    return f"^({t})"


def row_text(row: Row, foot_marks: set[int], marks_out: list) -> str:
    """The row's text with superscripts and subscripts as stored; a footnote
    mark becomes a placeholder ``\u0000FN<n>\u0000``."""
    main = [s for s in row.spans if s["size"] >= 11 and s["text"].strip()]
    if not main:
        return re.sub(r"\s+", " ", row.raw).strip()
    base = max(main, key=lambda s: len(s["text"]))["origin"][1]
    out = []
    for s in row.spans:
        t = s["text"]
        small = s["size"] < 10.5
        dy = s["origin"][1] - base
        if small and t.strip() and dy < -1.5:
            if _is_arial(s["font"]) and t.strip().isdigit() and int(t.strip()) in foot_marks:
                marks_out.append(int(t.strip()))
                out.append(f"\u0000FN{int(t.strip())}\u0000" + (" " if t.endswith(" ") else ""))
                continue
            out.append(_sup(t) + (" " if t.endswith(" ") else ""))
            continue
        out.append(t)
    text = "".join(out)
    text = text.replace(" ", " ").replace("­", "")
    return re.sub(r"\s+", " ", text).strip()


# --- classifying the rows of a page -------------------------------------------

_FEET: set | None = None


def classify(rows: list[Row], images: list, pno: int, feet: set | None = None) -> None:
    """Give each row its kind (running, caption, figtext, eqnum, heading,
    prose, small, math, math+eqnum, footnote, footnote+)."""
    global _FEET
    if feet is None:
        if _FEET is None:
            _FEET = {int(k) for k in load_manifest().get("footnotes", {})}
        feet = _FEET
    for r in rows:
        txt = r.raw.strip()
        if r.y0 < 60 or r.y0 > 735 or txt == "This Page Intentionally Left Blank":
            r.kind = "running"
            continue
        cap = _CAPTION.match(txt)
        if cap and r.bold and r.size >= 11:
            r.kind = "caption"
            continue
        inside = any(im.contains(fitz.Point(r.x0 + 1, r.mid)) and im.height > 40
                     for im in images)
        if inside:
            r.kind = "figtext"
            continue
        if r.arial12 >= 0.5 and _EQNUM.match(txt) and r.x0 > 380:
            r.kind = "eqnum"
            continue
        if r.arial12 >= 0.4:
            r.kind = "heading" if (r.bold and _heading_like(r)) else "prose"
            continue
        if r.arial_small >= 0.4:
            r.kind = "small"
            continue
        if r.arial == 0:
            r.kind = "math"
            continue
        r.kind = "small"
    # a short word set inside an equation object ("for" in Eq. 2-6) is part
    # of it
    for k, r in enumerate(rows):
        if r.kind == "prose" and _equation_word(r.lines):
            near = [x for x in rows[max(0, k - 2):k + 3] if x is not r]
            if any(x.kind in ("math", "eqnum") for x in near):
                r.kind = "math"
    # an equation number set at the end of a line of glyphs comes as one row
    for r in rows:
        if r.kind in ("math", "small") and re.search(r"\(\s*[PAB1-7]-\d+[a-z]?\s*\)\s*[.,;:]?\s*$", r.raw):
            last = [s for s in r.spans if s["text"].strip()][-1]
            if _is_arial(last["font"]) and last["bbox"][0] > 380:
                r.kind = "math+eqnum"
    # a run of glyph rows next to a table's cells (small rows) is part of
    # the table, unless it holds an equation number
    k = 0
    while k < len(rows):
        if rows[k].kind != "math":
            k += 1
            continue
        j = k
        while j < len(rows) and rows[j].kind in ("math", "eqnum", "math+eqnum"):
            j += 1
        run = rows[k:j]
        before = next((r for r in reversed(rows[:k]) if r.kind != "running"), None)
        after = next((r for r in rows[j:] if r.kind != "running"), None)
        if not any(r.kind != "math" for r in run) and any(
                x is not None and x.kind == "small" for x in (before, after)):
            for r in run:
                r.kind = "small"
        k = j
    # footnotes: rows at the foot of the page (Arial 10 pt, a few in 12 pt),
    # the first opening at the left margin with a small number in Arial
    # that is one of the manual's footnotes; the rows after it to the
    # running footer are its text
    for i, r in enumerate(rows):
        if r.kind in ("running", "footnote", "footnote+") or r.y0 < 560 or r.x0 > 80:
            continue
        if _footnote_start(r, feet):
            r.kind = "footnote"
            for r2 in rows[i + 1:]:
                if r2.kind == "running":
                    continue
                r2.kind = "footnote" if _footnote_start(r2, feet) else "footnote+"
            break
    _ = pno


def _footnote_start(r: Row, feet: set) -> bool:
    first = [s for s in r.spans if s["text"].strip()]
    return bool(first) and first[0]["size"] < 9 and _is_arial(first[0]["font"]) \
        and first[0]["text"].strip().isdigit() and int(first[0]["text"].strip()) in feet \
        and len(first) > 1


def _heading_like(r: Row) -> bool:
    return r.x0 < 150 and (r.x0 > 140 or _HEADNUM.match(r.raw.strip()) or r.x0 < 76)


# --- tokens -----------------------------------------------------------------

def page_tokens(doc, pno: int, man: dict, foot_marks: set[int], report: list) -> list[tuple]:
    """The page's content in reading order as tokens."""
    page = doc[pno - 1]
    printed = pno - man["page_offset"]
    rows, images = _rows(page)
    classify(rows, images, pno)
    rows = _two_column_lists(rows)
    # a raised number is a footnote mark only where the page prints that
    # footnote (the 6 of "10⁶" on p. 541 is an exponent)
    printed_feet = set()
    for r in rows:
        if r.kind == "footnote":
            first = [s for s in r.spans if s["text"].strip()][0]["text"].strip()
            printed_feet.add(int(first))
    foot_marks = foot_marks & printed_feet
    running = [r.raw.strip() for r in rows if r.kind == "running"]
    if str(printed) not in running:
        report.append(f"PDF p. {pno}: printed number {printed} not found in {running}")
    lines_fix = man.get("lines", {})
    kinds = man.get("row_kinds", {})
    toks: list[tuple] = [("page", printed)]
    i = 0
    n = len(rows)
    while i < n:
        r = rows[i]
        key = f"{printed}@{round(r.y0)}"
        if key in kinds:
            r.kind = kinds[key]
        if r.kind in ("running", "figtext", "small", "footnote+"):
            i += 1
            continue
        if r.kind == "footnote":
            i += 1
            continue
        if r.kind == "caption":
            m = _CAPTION.match(r.raw.strip())
            words = [m.group(3).strip()]
            j = i + 1
            while j < n and rows[j].kind in ("heading", "prose", "caption") and rows[j].bold \
                    and rows[j].y0 - rows[j - 1].y1 < 6 and not _CAPTION.match(rows[j].raw.strip()):
                words.append(rows[j].raw.strip())
                rows[j].kind = "caption+"
                j += 1
            title = re.sub(r"\s+", " ", " ".join(w for w in words if w)).strip()
            toks.append(("caption", m.group(1), m.group(2), title, printed, r.y0))
            i = j
            continue
        if r.kind == "caption+":
            i += 1
            continue
        if r.kind in ("math", "eqnum", "math+eqnum"):
            j = i
            group = []
            while j < n and rows[j].kind in ("math", "eqnum", "math+eqnum"):
                group.append(rows[j])
                j += 1
            for tok in _formula_tokens(group, printed, man, report):
                toks.append(tok)
            i = j
            continue
        if r.kind in ("prose", "heading"):
            marks: list = []
            if key in lines_fix:
                text = lines_fix[key]["text"]
                marks = [int(x) for x in re.findall(r"\u0000FN(\d+)\u0000", text)]
            else:
                text = row_text(r, foot_marks, marks)
            toks.append((r.kind, text, printed, r, key))
            i += 1
            continue
        i += 1
    return toks


def _two_column_lists(rows: list[Row]) -> list[Row]:
    """A bullet list set in two columns (p. 37: "• Aggregate columns" beside
    "• Jet grouting") reads down the left column, then down the right; the
    text layer gives each printed line across both."""
    def bullet(ln):
        return "".join(s["text"] for s in ln["spans"]).strip().startswith(("•", ""))

    out: list[Row] = []
    k = 0
    while k < len(rows):
        r = rows[k]
        two = r.kind == "prose" and bullet(r.lines[0]) and any(
            bullet(ln) and ln["bbox"][0] > 250 for ln in r.lines[1:])
        if not two:
            out.append(r)
            k += 1
            continue
        split = min(ln["bbox"][0] for ln in r.lines[1:] if bullet(ln) and ln["bbox"][0] > 250) - 2
        run = [r]
        j = k + 1
        while j < len(rows) and rows[j].kind == "prose" and rows[j].y0 - run[-1].y1 < 6 and (
                any(ln["bbox"][0] >= split for ln in rows[j].lines) or rows[j].x0 > 76):
            run.append(rows[j])
            j += 1
        left, right = [], []
        for x in run:
            lft = [ln for ln in x.lines if ln["bbox"][0] < split]
            rgt = [ln for ln in x.lines if ln["bbox"][0] >= split]
            for part, side in ((lft, left), (rgt, right)):
                if part:
                    nr = Row(part)
                    nr.kind = "prose"
                    side.append(nr)
        out.extend(left + right)
        k = j
    return out


def _formula_tokens(group: list[Row], printed: int, man: dict, report: list):
    """Printed formula lines from a run of glyph rows: rows are clustered by
    height; a cluster beside an equation number is that equation."""
    group = sorted(group, key=lambda r: r.y0)
    clusters: list[list[Row]] = []
    for r in group:
        if clusters and r.y0 <= max(x.y1 for x in clusters[-1]) + 3.5:
            clusters[-1].append(r)
        else:
            clusters.append([r])
    out = []
    for c in clusters:
        nums = []
        for r in c:
            if r.kind == "eqnum":
                nums.append(_EQNUM.match(r.raw.strip()).group(1))
            elif r.kind == "math+eqnum":
                nums.append(re.search(r"\(\s*([PAB1-7]-\d+[a-z]?)\s*\)\s*[.,;:]?\s*$", r.raw).group(1))
        y0 = min(r.y0 for r in c)
        y1 = max(r.y1 for r in c)
        if nums:
            for num in nums:
                out.append(("eq", num, printed, y0))
        else:
            out.append(("formula", f"{printed}@{round(y0)}", printed, y0, y1,
                        " ".join(r.raw.strip() for r in c)))
    return out


# --- a chapter --------------------------------------------------------------

def _norm_title(t: str) -> str:
    t = t.replace("ʹ", "'").replace("’", "'")
    return re.sub(r"[^a-z0-9]+", "", t.lower())


def _heading_title(text: str) -> str:
    t = text.strip()
    m = _HEADNUM.match(t)
    if m:
        t = m.group(2)
    return t.rstrip(".").strip()


def chapter_tokens(doc, man: dict, stem: str, report: list) -> list[tuple]:
    lo, hi = man["chapters"][stem]["pages"]
    foot = {int(k) for k in man.get("footnotes", {})}
    toks = []
    for p in range(lo, hi + 1):
        toks += page_tokens(doc, p, man, foot, report)
    return toks


def split_sections(toks: list[tuple], sections: list[dict], stem: str, man: dict,
                   report: list) -> dict[str, list[tuple]]:
    """Each section's tokens: from its printed heading to the next heading."""
    titles = [(s["section_id"], _norm_title(s["title"])) for s in sections]
    alias = man.get("heading_alias", {})
    out: dict[str, list[tuple]] = {sid: [] for sid, _ in titles}
    nxt = 0
    cur = None
    page = None
    stop = set(man["chapters"][stem].get("stop_headings", []))
    for t in toks:
        if t[0] == "page":
            page = t
            if cur:
                out[cur].append(t)
            continue
        if t[0] == "heading":
            ht = _heading_title(t[1])
            nt = _norm_title(alias.get(t[4], ht))
            hit = None
            for k in range(nxt, min(nxt + 3, len(titles))):
                if titles[k][1] and (nt == titles[k][1] or (len(nt) > 12 and nt.startswith(titles[k][1]))):
                    hit = k
                    break
            if hit is not None:
                for k in range(nxt, hit):
                    report.append(f"{stem}: heading of {titles[k][0]} not found")
                cur = titles[hit][0]
                nxt = hit + 1
                if page:
                    out[cur].append(page)
                continue
            if _norm_title(ht) in stop or t[4] in stop:
                cur = None
                continue
            if cur is None:
                continue  # the chapter's title, before its first section
            if t[4] not in man.get("headings_as_text", {}):
                report.append(f"{stem}: bold line kept as text in {cur}: {t[1][:70]!r} ({t[4]})")
            t = ("prose",) + t[1:]
        if cur:
            out[cur].append(t)
    for k in range(nxt, len(titles)):
        report.append(f"{stem}: heading of {titles[k][0]} not found")
    return out


def _item_start(text: str, row) -> bool:
    """A list item starts here: a bullet ("•"), or the hollow "o" of a
    second-level list set at its indent."""
    return text.startswith(("•", "", "▪", "■")) or (
        row is not None and row.x0 > 85 and (
            text.startswith("o ") or bool(re.match(r"\d{1,2}[.)] \S", text))))


def _continues(prev_row, prev_text: str, row, text: str) -> bool:
    """Whether a paragraph runs on from prev_row to row (across a page, a
    figure or a table, or a gap)."""
    if _item_start(text, row):
        return False
    if text[:1].islower():
        return True
    end = prev_text.rstrip()
    return prev_row.x1 > 470 and not end.endswith((".", ":", "?", ";")) and not end.endswith(".)")


def assemble(sid: str, toks: list[tuple], sec: dict, man: dict, report: list,
             eq_entries: dict) -> str:
    paras: list[str] = []
    cur: list[str] = []
    deferred: list[str] = []
    prev = None  # (row, text) of the last prose row
    page = None
    page_marked = None
    formulas = man.get("formulas", {})
    eqf = man.get("equation_formulas", {})
    typed = man.get("typed_tables", {})
    tnotes = man.get("table_notes", {})
    feet = man.get("footnotes", {})

    def flush():
        nonlocal cur
        if cur:
            paras.append(" ".join(cur))
            cur = []
        if deferred:
            paras.extend(deferred)
            deferred.clear()

    def marker():
        nonlocal page_marked
        if page != page_marked:
            page_marked = page
            return f"[p. {page}] "
        return ""

    def block(text):
        """A paragraph of its own (caption, formula): put after the open
        paragraph when the text runs on past it."""
        nonlocal page_marked
        if cur:
            deferred.append(f"[p. {page}] {text}")
            page_marked = None  # the text after it repeats its marker
        else:
            paras.append(marker() + text)

    for t in toks:
        kind = t[0]
        if kind == "page":
            page = t[1]
            continue
        if kind in ("prose", "heading"):
            text, row = t[1], t[3]
            new_para = True
            if prev is not None and cur:
                prow, ptext = prev
                same_page = prow is not None and getattr(prow, "_page", None) == page
                gap = row.y0 - prow.y1 if same_page else None
                if same_page and gap is not None and gap < 6 and not _item_start(text, row) \
                        and not _where_item(text, ptext):
                    new_para = False
                elif not same_page and _continues(prow, ptext, row, text):
                    new_para = False
                elif same_page and gap is not None and gap >= 6 and _continues(prow, ptext, row, text) \
                        and deferred_pending(deferred):
                    new_para = False
            row._page = page
            if new_para:
                flush()
                cur.append(marker() + text)
            else:
                m = marker()
                if cur and cur[-1].endswith("-") and not cur[-1].endswith(" -") and not m and (
                        text[:1].islower() or (text[:1].isdigit() and re.search(r"\d-$", cur[-1]))):
                    cur[-1] = cur[-1] + text
                else:
                    cur.append(m + text)
            prev = (row, text)
            continue
        if kind == "eq":
            num = t[1]
            eid = f"Eq. {num}"
            ent = eq_entries.get(eid)
            f = eqf.get(eid)
            if ent is None:
                report.append(f"{sid}: [{eid}] printed on p. {t[2]} but not in this section's equations")
            if f is None:
                report.append(f"{sid}: no equation_formulas entry for {eid}")
                f = "?"
            elif ent is not None and f not in ent["description"]:
                report.append(f"{sid}: formula for {eid} is not in its equations entry")
            flush()
            paras.append(marker() + f"[{eid}] {f}")
            prev = None
            continue
        if kind == "formula":
            key = t[1]
            f = formulas.get(key)
            if f is None:
                report.append(f"{sid}: unnumbered formula not typed in: {key} glyphs {t[5][:80]!r}")
                f = f"[[FORMULA {key}: {t[5][:60]}]]"
            elif isinstance(f, dict):
                f = f["text"]
            if f == "":
                continue  # a glyph run that is not a formula line (checked on the render)
            flush()
            paras.append(marker() + f)
            prev = None
            continue
        if kind == "caption":
            what, num, title, pg = t[1], t[2], t[3], t[4]
            cap = f"{what} {num} {title}".strip()
            if what == "Table":
                tid = f"Table {num}"
                spec = man.get("table_pages", {}).get(tid)
                pages = spec if spec else f"p. {pg}"
                parts = [cap]
                if tid in typed:
                    parts.append(typed[tid])
                else:
                    parts.append(f"[{tid}: values on printed {pages}; not typed in]")
                if tid in tnotes:
                    parts.append("\n".join(tnotes[tid]))
                text = "\n\n".join(parts)
            else:
                text = cap
            cont = man.get("caption_continued", {}).get(f"{what} {num}@{pg}")
            if cont is not None:
                text = cont
            if text:
                block(text)
            continue
    flush()
    paras = _join_where_lists([p.strip() for p in paras if p.strip()])
    body = "\n\n".join(paras)
    # footnotes at their marks
    for n in re.findall(r"\u0000FN(\d+)\u0000", body):
        fn = feet.get(n)
        if fn is None:
            report.append(f"{sid}: footnote mark {n} with no footnote text")
            fn = f"[Footnote {n}: ?]"
        body = body.replace(f"\u0000FN{n}\u0000", f" {fn}", 1)
    body = re.sub(r" +", " ", body)
    body = re.sub(r" ([,.;:)])", r"\1", body) if False else body
    return body


_WHERE_ITEM = re.compile(r"^(?:\[p\. \d+\] )?([^\s=][^=]{0,24}?) [=≈] ")


def _join_where_lists(paras: list[str]) -> list[str]:
    """A "where" list as one paragraph, a line to each symbol, as printed."""
    out: list[str] = []
    open_list = False
    for p in paras:
        m = _WHERE_ITEM.match(p)
        if open_list and m and m.group(1).count(" ") <= 3 and not p.startswith("[Eq."):
            out[-1] = out[-1] + "\n" + p
            continue
        out.append(p)
        bare = re.sub(r"^\[p\. \d+\] ", "", p)
        open_list = bare.rstrip().endswith(("where:", "where")) or (open_list and bool(m))
    return out


def deferred_pending(deferred) -> bool:
    return bool(deferred)


def _where_item(text: str, prev_text: str) -> bool:
    """A line of a "where" list ("COVw = coefficient of ...") starts a line;
    a line that opens with a word of the sentence ("of Kwall = 10 to 50",
    p. 76) does not."""
    first = text.split(" ", 1)[0]
    if first in ("of", "to", "in", "at", "by", "is", "as", "for", "and", "or", "the", "with",
                 "from", "on", "be", "than", "that"):
        return False
    # the line before ends a list line or opens the list ("where:"); "This
    # strength is associated with a" / "φ = 0 strength model" (p. 11) runs on
    prev = prev_text.rstrip()
    if not (prev.endswith((":", ",", ";", ".", " and", " or")) or _WHERE_LINE.match(prev)):
        return False
    # "... by a factor of four (i.e.," / "DB/DA = 4) produced ..." (p. 126)
    if prev.endswith(("i.e.,", "e.g.,")):
        return False
    return bool(_WHERE_LINE.match(text)) and not prev.endswith(("=", "+", "−", "-"))


#: "su = ...", "δVi, δVj = ...", "au and bu = ..." (p. 4)
_WHERE_LINE = re.compile(r"^\S{1,14}(?: \S{1,8}){0,2}\s?[=≈]\s")


def apply_fixes(sid: str, body: str, man: dict, report: list, used: set) -> str:
    for k, fx in enumerate(man.get("fixes", [])):
        if fx["section"] != sid:
            continue
        if fx["find"] not in body:
            report.append(f"{sid}: fix not applied: {fx['find'][:60]!r}")
            continue
        body = body.replace(fx["find"], fx["replace"], 1)
        used.add(k)
    for k, tb in enumerate(man.get("typed_blocks", [])):
        # a table printed with no number (a notation list), kept typed in
        if tb["section"] != sid:
            continue
        if tb.get("after"):
            if tb["after"] not in body:
                report.append(f"{sid}: typed block not placed, anchor missing: {tb['after'][:60]!r}")
                continue
            i = body.index(tb["after"]) + len(tb["after"])
            body = body[:i] + "\n\n" + tb["text"] + body[i:]
        else:
            body = tb["text"] + ("\n\n" + body if body else "")
        used.add(("block", k))
    for k, nt in enumerate(man.get("notes", [])):
        if nt["section"] != sid:
            continue
        if nt["after"] not in body:
            report.append(f"{sid}: note not placed, anchor missing: {nt['after'][:60]!r}")
            continue
        i = body.index(nt["after"]) + len(nt["after"])
        body = body[:i] + " " + nt["text"] + body[i:]
        used.add(("note", k))
    return body


def build_chapter(doc, man: dict, stem: str, report: list) -> dict:
    """The chapter file with every section's body built from the print; the
    other fields are read from the committed file and kept. Lettered parts
    of an earlier build (no section id of the print ends in a letter) are
    made again from the section they continue."""
    path = TEXT / f"{stem}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    sections = [s for s in data["sections"] if not re.search(r"\.[a-z]$", s["section_id"])]
    toks = chapter_tokens(doc, man, stem, report)
    per = split_sections(toks, sections, stem, man, report)
    used: set = set()
    new_sections = []
    for s in sections:
        eqs = {e["id"]: e for e in s.get("equations", [])}
        body = assemble(s["section_id"], per[s["section_id"]], s, man, report, eqs)
        body = apply_fixes(s["section_id"], body, man, report, used)
        s2 = dict(s, body=body)
        new_sections.extend(split_long(s2))
    data["sections"] = new_sections
    return data


def split_long(sec: dict) -> list[dict]:
    """A body over MAX_BODY as the section and lettered parts (.a, .b ...)
    cut at paragraph boundaries; the parts carry no fields of their own but
    the body, a title and an applicability saying which printed pages they
    hold. The section keeps every checked field."""
    body = sec["body"]
    overhead = len(json.dumps(dict(sec, body="")))

    def fits(text):
        return len(text) <= MAX_BODY and len(json.dumps(text)) + overhead <= MAX_SECTION_JSON

    if fits(body):
        return [sec]
    paras = body.split("\n\n")
    chunks, cur = [], []
    for p in paras:
        if cur and not fits("\n\n".join(cur + [p])):
            chunks.append(cur)
            cur = []
        cur.append(p)
    if cur:
        chunks.append(cur)
    out = []
    page = None
    for n, ch in enumerate(chunks):
        text = "\n\n".join(ch)
        start_page = page
        first = re.match(r"\[p\. (\d+)\]", text)
        if first:
            start_page = first.group(1)
        for m in re.finditer(r"\[p\. (\d+)\]", text):
            page = m.group(1)
        if not first and start_page:
            text = f"[p. {start_page}] " + text
        pages = f"p. {start_page}" if start_page == page else f"pp. {start_page} to {page}"
        if n == 0:
            out.append(dict(sec, body=text))
            continue
        letter = chr(ord("a") + n - 1)
        out.append({
            "section_id": f"{sec['section_id']}.{letter}",
            "title": f"{sec['title']} (continued, {pages})",
            "body": text,
            "key_points": [],
            "equations": [],
            "figures": [],
            "tables": [],
            "applicability": (f"Part {n + 1} of printed Section {sec['section_id']} ({pages}); "
                              "the letter is not printed, the section is split here to fit "
                              "the reference tools."),
        })
    return out


def formula_rows(data: dict) -> list[tuple[str, str]]:
    """Body lines that carry a formula (rule 2a), for the report."""
    out = []
    for s in data["sections"]:
        for para in s["body"].split("\n"):
            for m in re.finditer("=", para):
                if _OPS.search(para[max(0, m.start() - 30): m.end() + 30]):
                    out.append((s["section_id"], para))
                    break
    return out


def build_chapters(stems: list[str] | None = None) -> tuple[dict, list[str]]:
    """The built chapters (stem -> chapter dict) and the build's report;
    by default the chapters the manifest marks built."""
    man = load_manifest()
    stems = stems or [k for k, v in man["chapters"].items() if v.get("built")]
    pdf = REPO / "docs" / man["pdf"]
    report: list[str] = []
    built = {}
    with fitz.open(str(pdf)) as doc:
        for stem in stems:
            built[stem] = build_chapter(doc, man, stem, report)
    return built, report


def build(stems: list[str], write: bool, report_path: str | None, dump: str | None) -> int:
    built, report = build_chapters(stems)
    for stem, data in built.items():
        if write:
            (TEXT / f"{stem}.json").write_text(chapter_json(data), encoding="utf-8")
        if dump:
            with open(dump, "w", encoding="utf-8") as fh:
                for s in data["sections"]:
                    fh.write(f"\n=== {s['section_id']} {s['title']} ({len(s['body'])})\n{s['body']}\n")
    if report_path:
        Path(report_path).write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report[:60]:
        print(line)
    print(f"{len(report)} report lines")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", action="append")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report")
    ap.add_argument("--dump")
    a = ap.parse_args(argv)
    man = load_manifest()
    stems = a.chapter or [k for k, v in man["chapters"].items() if v.get("built")]
    return build(stems, a.write, a.report, a.dump)


if __name__ == "__main__":
    sys.exit(main())
