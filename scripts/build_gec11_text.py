"""Build GEC-11's chapter text from its printed pages (no API; BACKLOG REF-80).

GEC-11, Design and Construction of Mechanically Stabilized Earth Walls and
Reinforced Soil Slopes (FHWA-NHI-10-024, Volume I, and FHWA-NHI-10-025,
Volume II; November 2009), is an FHWA NHI print like the Soils and
Foundations manual that ``build_printed_text.py`` reads (REF-29), and is
built the same way: sections from the printed contents at every printed
level, each body the print's own words with a ``[p. 3-22]`` marker where
each printed page starts, figures and tables listed under the section that
prints their captions, and every numbered equation typed in by hand from a
rendered page (the manifest's ``printed_equations``). Nothing is summarised,
so ``summary`` is left out and ``key_points`` is empty.

The two volumes are laid out differently from the Soils and Foundations
manual, so this script reads the pages its own way and then uses
``build_printed_text``'s functions for the rest (finding headings, the body
between them, captions, equation entries, splitting):

* the running line is a footer ("FHWA NHI-10-024 / 3 – Soil Reinforcement
  Principles / MSE Walls and RSS – Vol I / 3 – 22 / November 2009"), not a
  header;
* every numbered equation is a drawn object carrying alternative text
  ("Equation 3-10 as discussed above.", "Equations 9-2 and 9-3 as discussed
  in the captioned text."), which the default text layer gives in place of
  the equation's glyphs, a few letters to a line. The pages are read with
  the alternative text ignored, so the glyphs come out (some figures carry
  alternative text too, over their lettering and caption); where the two
  readings differ and the default one is an equation's alternative text,
  the glyph lines are replaced by ``[Eq. 3-10]``, and by the formula typed
  in from the page before it when the manifest gives one;
* Greek letters and signs set in the Symbol font come out as private-use
  characters (U+F066 for φ), the bullets set in WP MathA as "C" and the
  check boxes of the design checklist as NUL; they are put back as printed
  (``SYMBOL``); a bullet set as a line of its own is put back at the start
  of the line printed beside it; a line ending in a hyphen (some set as
  soft hyphens) is joined to the next with no space, since the print breaks
  lines at a word's own hyphen ("long-term", "Figure 2-2"), except before
  "or", "to", "and" ("5- or 10-ft");
* a caption is made a paragraph of its own (the text layer runs it on into
  the text before and after it), ending where the List of Figures or
  Tables caption ends, so no body text is cut with a figure's lettering;
* the contents number a fourth, lettered level ("3.5.2.a"), print a
  dotted leader or none ("10.10.1 Specification Guidelines ... 10-42"),
  and the Lists of Figures and Tables print the number with a full stop
  ("Table 3-6. Summary of ..."); a few headings are printed on their page
  in other words, or under another number, than the contents give: the
  manifest's ``headings`` (contents number -> ``page_title`` and/or
  ``printed_as``) says so, and the section takes the page's wording;
* a section too long for the reference tools is split into parts as
  ``build_printed_text.split_long`` does, lettered ``.a``, ``.b`` ...;
  where those letters are printed section numbers of their own (GEC-11's
  lettered level), the manifest's ``split_ids`` names the part ids.

The manifest (``scripts/manifests/gec_11.json``) adds to the multi-volume
form of ``build_printed_text``: per volume ``volume_title``,
``contents_pages`` and ``lists_pages`` ([first, last], 1-based PDF pages),
``headings``, ``fix_lines`` (a text-layer line, on its PDF page, mended
before the build: a heading printed "11.2.1. Precast ..." with a full
stop), ``printed_equations`` (``number``, ``page``, ``formula``,
``variables``, optional ``notes``: see
``build_printed_text.add_printed_equations``), ``printed_tables`` (a table
whose text-layer cells come out a column at a time or lose signs and
superscripts, typed in row by row from the render: ``number``, ``page``,
``rows``, optional ``resume`` and ``notes``; see ``_type_tables``),
``split_ids`` and ``lookups`` (printed object -> the library function that
codes it, written to the section that prints the object as a section-level
``implemented_in`` mapping; the lookups were checked by opening them).

Usage::

    python scripts/build_gec11_text.py            # write the chapter files
    python scripts/build_gec11_text.py --report   # also list each section
    python scripts/build_gec11_text.py --chapter 3

The figure catalog (``figures_catalog.json``) is not written: it was
checked against the print separately.

Requires PyMuPDF.
"""

from __future__ import annotations

import argparse
import difflib
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
PKG = REPO / "geotech_references"
sys.path.insert(0, str(SCRIPTS))

import build_printed_text as bpt  # noqa: E402

PACKAGE = "gec_11"
_DASH = "–—−"

#: Symbol-font characters as the text layer gives them (U+F0xx, the font's
#: own code xx) and as printed. Parenthesis and bracket pieces of a drawn
#: equation are left out: equations are typed in from the page.
SYMBOL = {
    0x20: " ", 0x21: "!", 0x23: "#", 0x25: "%", 0x26: "&", 0x28: "(",
    0x29: ")", 0x2A: "∗", 0x2B: "+", 0x2C: ",", 0x2D: "−", 0x2E: ".",
    0x2F: "/", 0x3A: ":", 0x3B: ";", 0x3C: "<", 0x3D: "=", 0x3E: ">",
    0x3F: "?", 0x40: "≅", 0x44: "Δ", 0x46: "Φ", 0x47: "Γ", 0x4C: "Λ",
    0x50: "Π", 0x51: "Θ", 0x53: "Σ", 0x54: "Τ", 0x57: "Ω", 0x58: "Ξ",
    0x59: "Ψ", 0x5B: "[", 0x5C: "∴", 0x5D: "]", 0x61: "α", 0x62: "β",
    0x63: "χ", 0x64: "δ", 0x65: "ε", 0x66: "φ", 0x67: "γ", 0x68: "η",
    0x69: "ι", 0x6A: "ϕ", 0x6B: "κ", 0x6C: "λ", 0x6D: "μ", 0x6E: "ν",
    0x70: "π", 0x71: "θ", 0x72: "ρ", 0x73: "σ", 0x74: "τ", 0x75: "υ",
    0x77: "ω", 0x78: "ξ", 0x79: "ψ", 0x7A: "ζ", 0x7B: "{", 0x7C: "|",
    0x7D: "}", 0x7E: "∼", 0xA2: "′", 0xA3: "≤", 0xB0: "°", 0xB1: "±",
    0xB2: "″", 0xB3: "≥", 0xB4: "×", 0xB7: "•", 0xB8: "÷", 0xB9: "≠",
    0xBA: "≡", 0xBB: "≈", 0xD2: "®", 0xD7: "·", 0xDE: "⇒",
}
SYMBOL.update({0x30 + d: str(d) for d in range(10)})

#: The alternative text of an equation object, with the spaces taken out.
_ALT = re.compile(r"Equations?((?:\d{1,2}-\d{1,3}[a-z]?|\d{1,2}[a-z]|,|and)+)"
                  r"asdiscussed(?:above|inthecaptionedtext)\.?")
_ALT_NUM = re.compile(r"(\d{1,2}-\d{1,3}[a-z]?|\d{1,2}[a-z])")
#: The first line of the running footer.
_FOOTER = re.compile(r"^FHWA\s+NHI-10-02[45]$")
_PAGE_LABEL = re.compile(rf"^(\d{{1,2}}|[A-F])\s*[-{_DASH}]\s*(\d{{1,3}})$")
#: A contents entry, its page after a dotted leader or straight after it.
_CONTENTS = re.compile(
    rf"(?<![\w.])(\d{{1,2}}(?:\.\d{{1,2}}){{1,3}}(?:\.[a-z])?)\s+"
    rf"((?:[A-Z]|\d+-[A-Za-z])[^\n]*?)\s*(?:\.{{2,}}\s*|\s)(\d{{1,2}})\s*[-{_DASH}]\s*(\d{{1,3}})"
    rf"(?=\s|$)")
#: A caption as printed: "Table 3-6. Summary ...", and also with no full
#: stop ("Table 3-8 Steel Corrosion Rates ...", "Table 1-2 – Representative
#: ..."); the groups are ``build_printed_text._CAPTION``'s.
_CAPTION = re.compile(rf"^(Figure|Table)\s+(\d{{1,2}})[-{_DASH}](\d{{1,3}})(?:([a-z])|\(([a-z])\))?"
                      rf"(?:[.:](?:\s|$|(?=[A-Z]))|\s+[-{_DASH}]\s+|\s+(?=[A-Z])|$)")
#: A List of Figures / Tables entry: "Table 3-6. Summary of ... ..... 3-17".
_LIST_ENTRY = re.compile(
    rf"(Figure|Table)\s+(\d{{1,2}}-\d{{1,3}}[a-z]?)\.\s+(.+?)\s*"
    rf"(?:\.{{2,}}|(?<=[.)])(?=\s))\s*(\d{{1,2}})\s*[-{_DASH}]\s*(\d{{1,3}})(?=\s|$)")


# ---------------------------------------------------------------------------
# reading the pages
# ---------------------------------------------------------------------------

def _span_text(span: dict) -> str:
    text = span["text"]
    font = span["font"]
    if font.startswith("WP-MathA") and text.strip() == "C":
        return text.replace("C", "•")
    if font.startswith("Wingdings"):
        return "".join("▪" if ord(c) == 0xF0A7 else c for c in text)
    out = []
    for c in text:
        o = ord(c)
        if 0xF000 <= o <= 0xF0FF:
            out.append(SYMBOL.get(o - 0xF000, ""))
        elif c == "\x00" and font.startswith("Symbol"):
            out.append("□")
        else:
            out.append(c)
    return "".join(out)


def _page_lines(page, ignore_actualtext: bool, mapped: bool) -> list[str]:
    flags = fitz.TEXTFLAGS_DICT
    if ignore_actualtext:
        flags |= fitz.TEXT_IGNORE_ACTUALTEXT
    found = []
    for b in page.get_text("dict", flags=flags)["blocks"]:
        if b["type"] != 0:
            continue
        for ln in b["lines"]:
            found.append(("".join(_span_text(s) if mapped else s["text"]
                                  for s in ln["spans"]), ln["bbox"]))
    # a bullet set in the Symbol font is a line of its own, which the text
    # layer often puts after its item ("... Note that for sites •"): it is
    # put at the start of the line it is printed beside
    lines = [t for t, _ in found]
    for k, (t, bb) in enumerate(found):
        if t.replace("", "").strip() not in ("", "•"):
            continue
        mid = (bb[1] + bb[3]) / 2
        near = [j for j, (u, cc) in enumerate(found)
                if j != k and lines[j] is not None and cc[0] > bb[2] - 1
                and abs((cc[1] + cc[3]) / 2 - mid) <= 3
                and u.replace("", "").strip() not in ("", "•")]
        if near:
            j = min(near, key=lambda j: found[j][1][0])
            lines[j] = t.strip() + " " + lines[j]
            lines[k] = None
    return [t for t in lines if t is not None]


def _equation_groups(alt: list[str], glyphs: list[str]):
    """Where the default reading ``alt`` and the glyph reading differ, as
    ``(i1, i2, j1, j2)``; blocks parted only by a few blank lines are one."""
    sm = difflib.SequenceMatcher(None, alt, glyphs, autojunk=False)
    groups, pending = [], False
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            if groups and not any(x.strip() for x in alt[i1:i2]) and i2 - i1 <= 6:
                groups[-1][1], groups[-1][3] = i2, j2
                pending = True
            else:
                pending = False
            continue
        if groups and pending:
            groups[-1][1], groups[-1][3] = i2, j2
        else:
            groups.append([i1, i2, j1, j2])
        pending = False
    return groups


def _alt_numbers(text: str) -> list[str]:
    """Equation numbers an alternative text names: "5-5b,5c,and5d" gives
    5-5b, 5-5c, 5-5d; "3-4and3-5" gives 3-4, 3-5."""
    out, chap = [], None
    for tok in (t for t in text.replace("and", ",").split(",") if t):
        if not _ALT_NUM.fullmatch(tok):
            raise ValueError(f"equation alternative text not understood: {text!r}")
        if "-" in tok:
            chap = tok.split("-")[0]
            out.append(tok)
        elif chap:
            out.append(f"{chap}-{tok}")
    return out


def read_pages(pdf: Path) -> list[dict]:
    """Each page: ``label`` (printed page, e.g. '3-22'), its ``lines`` with
    the footer taken off and each equation object as ``[Eq. N]`` lines, and
    ``equations`` (the numbers marked on it)."""
    pages = []
    with fitz.open(str(pdf)) as doc:
        for page in doc:
            alt = _page_lines(page, False, False)
            raw = _page_lines(page, True, False)
            lines = _page_lines(page, True, True)
            eqs = []
            for i1, i2, j1, j2 in reversed(_equation_groups(alt, raw)):
                flat = re.sub(r"\s+", "", "".join(alt[i1:i2]))
                found = list(_ALT.finditer(flat))
                if not found:
                    continue
                nums = [n for m in found for n in _alt_numbers(m.group(1))]
                rest = _ALT.sub("", flat)
                end = j2
                if rest:
                    # other alternative text (a figure's) in the same block:
                    # the equation's lines end with its printed number
                    last = nums[-1]
                    hit = [j for j in range(j1, j2) if f"({last})" in raw[j]]
                    end = hit[-1] + 1 if hit else j2
                lines[j1:end] = [""] + [x for n in nums for x in (f"[Eq. {n}]", "")]
                eqs = nums + eqs
            label, lines = _cut_footer([ln.strip() for ln in lines])
            pages.append({"label": label, "lines": _join_hyphens(lines),
                          "equations": eqs})
    return pages


#: The words after a hyphen that leave it standing ("5- or 10-ft", "2- to
#: 4-in.", "pre- and post-"): there the line break is a space.
_SUSPENDED = re.compile(r"^(?:or|and|to|through|thru|nor)\b")


def _join_hyphens(lines: list[str]) -> list[str]:
    """A line that ends in a hyphen joined to the next line with no space
    ("long-" + "term effects" -> "long-term effects", "Figure 2-" + "2." ->
    "Figure 2-2."): the print breaks lines at a word's own hyphen, and does
    not hyphenate words across lines. Some hyphens are set as soft hyphens
    (U+00AD), which print as "-" and are written as one. A hyphen left
    standing before "or", "to", "and" keeps its space."""
    out = [ln.replace("­", "-") for ln in lines]
    k = 0
    while k < len(out) - 1:
        ln, nxt = out[k], out[k + 1]
        if (re.search(r"[A-Za-z0-9)]-$", ln) and re.match(r"[A-Za-z0-9(]", nxt)
                and not _SUSPENDED.match(nxt)):
            out[k] = ln + nxt
            del out[k + 1]
            continue
        k += 1
    return out


#: Lines of the running footer after its "FHWA NHI-10-02x" line, in any
#: order: the chapter ("3 – Soil Reinforcement Principles"), the short
#: title, the page and the date.
_FOOTER_PART = re.compile(
    rf"^(?:\d{{1,2}}\s*[{_DASH}-]\s*\D.*|MSE Walls and RSS\s*[{_DASH}-]\s*Vol I{{1,2}}"
    rf"|November 2009|Table of Contents)$")


def _cut_footer(lines: list[str]) -> tuple[str | None, list[str]]:
    """The printed page number and the page's lines without the running
    footer, wherever the text layer puts it (mostly last; first on a few
    pages, or before a figure's caption)."""
    label, drop = None, set()
    for k, ln in enumerate(lines):
        if not _FOOTER.match(ln):
            continue
        drop.add(k)
        j, seen = k + 1, 0
        while j < len(lines) and seen < 4:
            nxt = lines[j]
            if not nxt:
                j += 1
                continue
            m = _PAGE_LABEL.match(nxt)
            if m and label is None:
                label = f"{m.group(1)}-{m.group(2)}"
            elif not _FOOTER_PART.match(nxt):
                break
            drop.add(j)
            seen += 1
            j += 1
    return label, [ln for k, ln in enumerate(lines) if k not in drop]


# ---------------------------------------------------------------------------
# contents and lists
# ---------------------------------------------------------------------------

def parse_contents(pages: list[dict], first: int, last: int) -> list[dict]:
    text = bpt._clean_ws(" ".join(" ".join(p["lines"]) for p in pages[first - 1:last]))
    out, seen = [], set()
    for m in _CONTENTS.finditer(text):
        sid, title = m.group(1), bpt._clean_ws(m.group(2))
        if sid in seen:
            continue
        seen.add(sid)
        out.append({"sid": sid, "title": title,
                    "page": (int(m.group(3)), int(m.group(4)))})
    return out


def parse_lists(pages: list[dict], first: int, last: int) -> tuple[dict, dict]:
    """The List of Tables and List of Figures: kind -> number -> caption, page."""
    text = bpt._clean_ws(" ".join(" ".join(p["lines"]) for p in pages[first - 1:last]))
    out = {"Figure": {}, "Table": {}}
    for m in _LIST_ENTRY.finditer(text):
        kind, num = m.group(1), m.group(2)
        if num.split("-")[0] != m.group(4):
            continue
        out[kind].setdefault(num, {"caption": bpt._clean_ws(m.group(3)),
                                   "page": (int(m.group(4)), int(m.group(5)))})
    return out["Figure"], out["Table"]


# ---------------------------------------------------------------------------
# sections
# ---------------------------------------------------------------------------

#: Words kept in capitals when a heading printed in capitals is title-cased,
#: beside ``build_printed_text``'s (a word of them joined by "/" or in
#: brackets, "MSE/RSS", "(BBMSE)", stays as printed).
_ACRONYMS = bpt._ACRONYMS | {"MSE", "RSS", "MSEW", "BBMSE", "SFMSE", "MBW", "LRFD"}


def title_case(title: str) -> str:
    out = bpt.title_case(title)
    if out == title:
        return title
    words, new = title.split(), out.split()
    for i, w in enumerate(words):
        parts = re.findall(r"[A-Za-z]+", w)
        if parts and all(p.upper() == p and p in _ACRONYMS for p in parts):
            new[i] = w
    return " ".join(new)


def _skip_heading(stream, s: int, t: int, sid: str, title: str) -> int:
    """The stream position after a heading's number and title lines (a
    title printed over two or three lines). A paragraph that starts on the
    heading's own line ("3.5.2.g Preliminary Design Reduction Factor, RF
    For preliminary design ...") keeps its words: that line is cut after
    the title."""
    k = s
    ln = stream[k][1]
    rest = ln[len(sid):].strip() if ln.startswith(sid) else ln
    want = bpt._norm(title)
    got = bpt._norm(rest)
    if len(got) > len(want) and got.startswith(want):
        n = 0
        for c, ch in enumerate(rest):
            n += bool(bpt._norm(ch))
            if n == len(want):
                stream[k] = (stream[k][0], rest[c + 1:].strip())
                return k
    k += 1
    while k < t and len(got) < len(want):
        nxt = stream[k][1]
        if not nxt:
            k += 1
            continue
        cand = got + bpt._norm(nxt)
        if want.startswith(cand) or difflib.SequenceMatcher(
                None, cand, want[:len(cand)]).ratio() >= 0.9:
            got = cand
            k += 1
        else:
            break
    return k


def _caption_end(raw, q: int, m, listed: str) -> int:
    """The stream position of a caption's last line: the lines after the
    caption line that go on with the words the List of Figures or Tables
    gives (a caption printed with more words than the list ends where the
    list's words end; what follows is kept as text)."""
    want = bpt._norm(listed)
    got = bpt._norm(raw[q][1][m.end():])
    end, k = q, q + 1
    while want and len(got) < len(want) and k < len(raw) and raw[k][0] == raw[q][0]:
        nxt = bpt._norm(raw[k][1])
        if not nxt:
            if got:
                break
            k += 1
            continue
        cand = got + nxt
        if difflib.SequenceMatcher(None, cand, want[:len(cand)]).ratio() < 0.8:
            break
        got, end = cand, k
        k += 1
    return end


def _is_caption(lines: list[str], k: int, m, listed: dict) -> bool:
    """``build_printed_text._is_caption``, or a caption printed with fewer
    words than the list gives (Table 3-5 is printed "Reinforcement Pullout
    Performance in Granular ...", listed "Basic Aspects of Reinforcement
    Pullout Performance ...")."""
    if bpt._is_caption(lines, k, m, listed):
        return True
    entry = listed.get(bpt._caption_number(m))
    a = bpt._norm(bpt._caption_text(lines, k, m))[:24]
    return bool(entry) and len(a) >= 16 and a in bpt._norm(entry["caption"])


def _caption_in_segment(stream, s, t, kind, num, caption_lines) -> bool:
    for q in range(s, t):
        m = _CAPTION.match(stream[q][1])
        if (m and m.group(1) == kind and bpt._caption_number(m) == num
                and stream[q] in caption_lines):
            return True
    return False


def _fill_equations(body: str, printed: list[dict]) -> str:
    """Put the typed formula before each ``[Eq. N]`` marker that stands
    alone (an equation object's place)."""
    by_num = {e["number"]: e for e in printed if e.get("formula")}

    def rep(m):
        e = by_num.get(m.group(1))
        return f"{e['formula']} [Eq. {m.group(1)}]" if e else m.group(0)
    return re.sub(r"(?m)^\[Eq\. ([^\]]+)\]$", rep, body)


def _type_tables(body: str, printed: list[dict], done: set) -> str:
    """Each table typed in from the page (the manifest's ``printed_tables``:
    ``number``, ``page``, ``rows``, optional ``resume`` and ``notes``) put in
    place of its text-layer cells, which come out a column at a time or
    with signs and superscripts lost: after the caption's paragraph, the
    text up to ``resume`` (the words that start the print's next paragraph
    after the table) or, without one, the next paragraph, is replaced by
    the typed rows, one to a line, cells parted by " | ". Page markers in
    the replaced text are kept. Numbers typed in are added to ``done``."""
    for t in printed:
        cap = re.search(rf"(?:^|\n\n)(?:\[p\. [^\]]+\]\s*)?Table {re.escape(t['number'])}"
                        rf"(?![\d])[^\n]*", body)
        if not cap:
            continue
        start = body.find("\n\n", cap.end())
        if start < 0:
            start = len(body)
        start += 2
        if t.get("resume"):
            end = body.find(t["resume"], start)
            if end < 0:
                raise ValueError(f"Table {t['number']}: resume text not found")
        else:
            end = body.find("\n\n", start)
            end = len(body) if end < 0 else end
        markers = " ".join(re.findall(r"\[p\. [^\]]+\]", body[start:end]))
        typed = (f"[Table {t['number']}, typed in from p. {t['page']}, row by row:]\n"
                 + "\n".join(t["rows"]))
        if t.get("notes"):
            typed += f"\n[Note on the table: {t['notes']}]"
        tail = body[end:]
        sep = "\n\n" if tail and not tail.startswith("\n") else ""
        body = (body[:start] + typed + (f"\n\n{markers}" if markers else "")
                + sep + tail)
        done.add(t["number"])
    return body


def _split(sec: dict, split_ids: dict) -> list[dict]:
    parts = bpt.split_long(sec)
    ids = split_ids.get(sec["section_id"])
    if len(parts) > 1 and ids:
        if len(ids) != len(parts) - 1:
            raise ValueError(f"{sec['section_id']}: split into {len(parts)} parts, "
                             f"split_ids names {len(ids)}")
        for p, new in zip(parts[1:], ids):
            p["section_id"] = new
    if len(parts) > 1 and sec.get("implemented_in"):
        for p in parts:
            listed = {x.split(":")[0] for x in p["figures"] + p["tables"]}
            links = {k: v for k, v in sec["implemented_in"].items() if k in listed}
            if links:
                p["implemented_in"] = links
            else:
                p.pop("implemented_in", None)
    return parts


def build_volume(vol: dict, manifest_dir: Path, only: set[int] | None = None):
    pdf = (manifest_dir / vol["pdf_path"]).resolve()
    pages = read_pages(pdf)
    for f in vol.get("fix_lines", []):
        lines = pages[f["pdf_page"] - 1]["lines"]
        if f["find"] not in lines:
            raise ValueError(f"fix_lines: {f['find']!r} not on PDF page {f['pdf_page']}")
        lines[lines.index(f["find"])] = f["replace"]
    entries = parse_contents(pages, *vol["contents_pages"])
    figs, tabs = parse_lists(pages, *vol["lists_pages"])
    headings = vol.get("headings", {})
    for e in entries:
        h = headings.get(e["sid"], {})
        e["contents_title"] = e["title"]
        if h.get("page_title"):
            e["title"] = h["page_title"]
        if h.get("printed_as"):
            e["contents_sid"] = e["sid"]
            e["sid"] = h["printed_as"]

    printed_at: dict[tuple[str, str], list[int]] = {}
    caption_lines: set[tuple[int, str]] = set()
    for i, p in enumerate(pages):
        lines = p["lines"]
        for k, ln in enumerate(lines):
            m = _CAPTION.match(ln)
            if m and _is_caption(lines, k, m, figs if m.group(1) == "Figure" else tabs):
                printed_at.setdefault((m.group(1), bpt._caption_number(m)), []).append(i)
                caption_lines.add((i, ln))
    captions_on_page = {pages[i]["label"] for (kind, _), idx in printed_at.items()
                        if kind == "Figure" for i in idx}
    tables_on_page = {pages[i]["label"] for (kind, _), idx in printed_at.items()
                      if kind == "Table" for i in idx}

    printed_eqs = vol.get("printed_equations", [])
    printed_tabs = vol.get("printed_tables", [])
    lookups = vol.get("lookups", {})
    split_ids = vol.get("split_ids", {})
    eqs_attached: set = set()
    tables_typed: set = set()
    lookups_done: set = set()
    chapters = {}
    for ch in vol["chapters"]:
        n = ch["number"]
        if only and n not in only:
            continue
        # a caption is a paragraph of its own (the text layer runs it on
        # from the line before and into the text after), so a split part
        # lists the objects it prints and no body text is taken for caption
        raw = bpt._stream(pages, ch["page_start"], ch["page_end"])
        stream, q = [], 0
        while q < len(raw):
            i, ln = raw[q]
            if (i, ln) not in caption_lines:
                stream.append((i, ln))
                q += 1
                continue
            m = _CAPTION.match(ln)
            entry = (figs if m.group(1) == "Figure" else tabs).get(bpt._caption_number(m), {})
            end = _caption_end(raw, q, m, entry.get("caption", ""))
            stream.append((i, ""))
            stream.extend(raw[q:end + 1])
            stream.append((raw[end][0], ""))
            q = end + 1
        ch_entries = [e for e in entries if e["sid"].split(".")[0] == str(n)]
        pos = bpt.locate_headings(stream, pages, ch_entries, None)
        found = [(e, p) for e, p in zip(ch_entries, pos) if p >= 0]
        missing = [e["sid"] for e, p in zip(ch_entries, pos) if p < 0]
        heads = [{"sid": f"{n}.0", "title": ch["title"], "page": None}]
        starts = [0]
        for e, p in found:
            heads.append(e)
            starts.append(p)
        starts.append(len(stream))
        sections = []
        for h, s, t in zip(heads, starts, starts[1:]):
            if h["sid"] == f"{n}.0":
                k = s
                while k < t and (not stream[k][1]
                                 or stream[k][1].upper().startswith("CHAPTER")
                                 or bpt._norm(stream[k][1]) in bpt._norm(ch["title"])):
                    k += 1
            else:
                k = _skip_heading(stream, s, t, h["sid"], h["title"])
            eq_ids: list = []
            body = bpt.render_body(stream, k, t, pages, captions_on_page, eq_ids,
                                   chapter=str(n), figs={},
                                   tables_on_page=tables_on_page)
            body = _type_tables(body, printed_tabs, tables_typed)
            body = _fill_equations(body, printed_eqs)
            labels = [pages[stream[q][0]]["label"] for q in range(s, t)
                      if pages[stream[q][0]]["label"]]
            page_from = labels[0] if labels else None
            page_to = labels[-1] if labels else None
            seg_idx = {stream[q][0] for q in range(s, t)}
            sec_figs = [f"Figure {num}: {figs[num]['caption'] if num in figs else ''}".rstrip(": ")
                        for (kind, num), idx in sorted(printed_at.items(), key=lambda x: (x[1][0], x[0]))
                        if kind == "Figure" and any(i in seg_idx for i in idx)
                        and _caption_in_segment(stream, s, t, "Figure", num, caption_lines)]
            sec_tabs = [f"Table {num}: {tabs[num]['caption'] if num in tabs else ''}".rstrip(": ")
                        for (kind, num), idx in sorted(printed_at.items(), key=lambda x: (x[1][0], x[0]))
                        if kind == "Table" and any(i in seg_idx for i in idx)
                        and _caption_in_segment(stream, s, t, "Table", num, caption_lines)]
            if h["sid"] == f"{n}.0" and len(re.sub(r"\[[^\]]*\]", "", body).strip()) < 20:
                continue
            pages_txt = (f"p. {page_from}" if page_from == page_to
                         else f"pp. {page_from} to {page_to}")
            where = (f"{vol['volume_id']} (Volume {'I' if vol['volume'] == 1 else 'II'}), "
                     f"Chapter {n} ({ch['title']}), printed {pages_txt}.")
            if h.get("contents_sid"):
                where += (f" The contents list this section as {h['contents_sid']}; "
                          f"the page prints {h['sid']}.")
            if h.get("contents_title") and bpt._norm(h["contents_title"]) != bpt._norm(h["title"]):
                where += (f" The contents give its title as "
                          f"\"{title_case(h['contents_title'])}\".")
            sec = {
                "section_id": h["sid"],
                "title": title_case(h["title"]),
                "body": body,
                "key_points": [],
                "equations": bpt.add_printed_equations(body, [], printed_eqs, eqs_attached),
                "figures": sec_figs,
                "tables": sec_tabs,
                "applicability": where,
            }
            links = {obj: fn for obj, fn in lookups.items()
                     if any(x.split(":")[0] == obj for x in sec_figs + sec_tabs)}
            if links:
                sec["implemented_in"] = links
                lookups_done |= set(links)
            sections.extend(_split(sec, split_ids))
        chapters[n] = {
            "reference_id": vol["volume_id"],
            "reference_title": vol.get("volume_title", ""),
            "volume": vol["volume"],
            "chapter": n,
            "chapter_title": ch["title"],
            "sections": sections,
            "_missing": missing,
        }
    built = set(chapters)
    problems = []
    for e in printed_eqs:
        if int(e["number"].split("-")[0]) in built and e.get("formula") \
                and e["number"] not in eqs_attached:
            problems.append(f"Eq. {e['number']}: no section marks it")
    for t in printed_tabs:
        if int(t["number"].split("-")[0]) in built and t["number"] not in tables_typed:
            problems.append(f"Table {t['number']}: no section prints its caption")
    for obj in lookups:
        if int(obj.split()[1].split("-")[0]) in built and obj not in lookups_done:
            problems.append(f"{obj}: no section prints it, so its lookup is unlinked")
    if problems:
        raise ValueError(f"{vol['volume_id']}: " + "; ".join(problems))
    return chapters, pages, entries, figs, tabs


def build_chapters(only: set[int] | None = None) -> dict:
    """Every chapter (number -> chapter dict, with ``_missing``), built from
    the manifest without writing anything; the check that a rebuild
    reproduces the committed files."""
    mf = SCRIPTS / "manifests" / f"{PACKAGE}.json"
    manifest = json.loads(mf.read_text(encoding="utf-8"))
    chapters = {}
    for vol in manifest["volumes"]:
        chs, *_ = build_volume(vol, mf.parent, only)
        chapters.update(chs)
    return chapters


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--chapter", type=int, action="append")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and report without writing the chapter files")
    args = ap.parse_args(argv)
    only = set(args.chapter) if args.chapter else None
    text_dir = PKG / PACKAGE / "text"
    for n, data in sorted(build_chapters(only).items()):
        missing = data.pop("_missing")
        if not args.dry_run:
            (text_dir / f"chapter{n:02d}.json").write_text(
                bpt.chapter_json(data), encoding="utf-8")
        sizes = [len(json.dumps(s, ensure_ascii=False)) for s in data["sections"]]
        print(f"[{PACKAGE}] ch {n}: {len(data['sections'])} sections, "
              f"largest {max(sizes) if sizes else 0} chars as JSON, "
              f"headings not found: {missing or 'none'}")
        if args.report:
            for s in data["sections"]:
                print(f"   {s['section_id']:10s} {len(s['body']):6d}  {s['title'][:60]}"
                      f"  eqs={[e['id'][4:] for e in s['equations']]}"
                      f"  figs={len(s['figures'])} tabs={[t.split(':')[0][6:] for t in s['tables']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
