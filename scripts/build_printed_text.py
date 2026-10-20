"""Build chapter text and a figure catalog from a manual's printed pages (no API).

For a manual whose PDF carries a usable text layer and a printed table of
contents that numbers every heading (the FHWA NHI-06-088/089 Soils and
Foundations Reference Manual, BACKLOG REF-29), the chapter text can be read
off the print instead of being written by hand:

1. the printed contents (``contents_pages`` in the manifest) give every
   numbered heading with its title and printed page;
2. each heading is found on the page the contents name (or up to three pages
   on), and a section's ``body`` is the printed text from its heading to the
   next one, with the running headers taken off and a ``[p. 6-28]`` marker
   where each printed page starts, so a reader can cite the page;
3. an equation the PDF holds as an equation object (its glyphs come out one
   or two to a line) is replaced by ``[Eq. 9-5]`` and listed in the
   section's ``equations`` with the words that introduce it; the equation
   itself is read on the printed page;
4. the List of Figures and List of Tables give each figure's and table's
   number, caption and printed page; a section lists the figures and tables
   whose captions are printed in it, and the figure catalog
   (``figures_catalog.json``) gets each figure's PDF page from the page
   that prints its caption.

The text is the print's own wording: nothing is summarised or paraphrased,
so ``summary`` is left out and ``key_points`` is empty, and ``applicability``
says where in the manual the section sits. Labels and axis text inside a
figure, which the PDF also holds as text, are left out of a body where they
come as a block of short lines on a page that prints a figure caption.

The manifest is a multi-volume one (``volumes``, each with ``pdf_path``,
``volume_id``, ``contents_pages`` [first, last] (1-based PDF pages) and its
``chapters`` with 1-based ``page_start`` / ``page_end``), plus
``"text_build": "printed"``. Chapters can be left out with
``skip_chapters``.

Usage::

    python scripts/build_printed_text.py fhwa_soils_foundations
    python scripts/build_printed_text.py fhwa_soils_foundations --report

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

_DASH = "–—−"
#: The printed page number in a running header ("6 - 28", "9 - 1").
_PAGE_LABEL = re.compile(rf"^(\d{{1,2}}|[A-E])\s*[-{_DASH}]\s*(\d{{1,3}})$")
_HEADER_END = re.compile(r"^December\s+2006$")
#: A contents line: number, title, dotted leader, printed page.
_CONTENTS = re.compile(
    rf"(?<![\d.])(\d{{1,2}}\.\d{{1,2}}(?:\.\d{{1,2}}){{0,3}})\s*([A-Z\u201c\"].+?)\s*\.*\s*"
    rf"(\d{{1,2}})\s*[-{_DASH}.]\s*(\d{{1,3}})"
    rf"(?=\s+(?:\d{{1,2}}\.\d|APPENDIX|LIST)|\s*$)")
#: A List of Figures / Tables entry: "6-15 Taylor's chart ... ...... 6-28".
_LIST_ENTRY = re.compile(
    rf"(?<![\w.-])(\d{{1,2}}-\d{{1,3}}[a-z]?)\s+(.+?)\s*(?:\.{{2,}}|\s\.)\s*"
    rf"(\d{{1,2}})\s*[-{_DASH}]\s*(\d{{1,3}})(?=\s|$)")
#: A caption as printed under a figure or over a table.
_CAPTION = re.compile(r"^(Figure|Table)\s+(\d{1,2}-\d{1,3})(?:([a-z])|\(([a-z])\))?(?:[.:]\s|$)")


def _caption_number(m) -> str:
    """'9-37' plus the letter printed as '9-37a' or '9-37(a)'."""
    return m.group(2) + (m.group(3) or m.group(4) or "")
#: A bare equation number printed beside an equation object.
_EQ_NUMBER = re.compile(r"^\(?(\d{1,2}-\d{1,3}[a-z]?)\)?$")
#: An equation set in type, its number at the end of the line.
_TYPED_EQ = re.compile(r"^(.*\S)\s+(\d{1,2}-\d{1,3}[a-z]?)$")
#: Words after which "6-17" is a reference, not an equation's number.
_REF_WORD = re.compile(r"(?:Figures?|Tables?|Equations?|Eqs?\.?|Sections?|Examples?"
                       r"|Chapters?|and|to|through|or|,)\s*$", re.I)
#: A body longer than this is split into parts (see ``split_long``), so
#: that a section fetched through the app's reference tools fits its
#: 16,000-character result with the section's other fields.
MAX_BODY_CHARS = 12000

# Words kept in capitals when a heading printed in capitals is title-cased.
_ACRONYMS = {
    "AASHTO", "ASTM", "ASD", "LRFD", "SPT", "CPT", "CPTU", "DMT", "PMT", "VST",
    "USCS", "RQD", "MSE", "RSS", "FHWA", "NHI", "PDA", "WEAP", "CAPWAP", "GDL",
    "OCR", "CRS", "CU", "UU", "CD", "SI", "US", "RMR", "GSI", "UC", "II", "I",
    "III", "IV", "PI", "LL", "PL", "CBR", "QA", "QC", "PS&E", "DOT", "GPS",
    "NCHRP", "ROW", "RC", "CIP", "GRS", "SOE", "IGM", "IGMS", "TV", "CCR",
}
_SMALL = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
          "or", "the", "to", "with", "vs", "versus", "into", "per", "under"}


def title_case(title: str) -> str:
    """Title-case a heading printed in capitals; leave mixed case alone."""
    letters = [c for c in title if c.isalpha()]
    if not letters or sum(c.isupper() for c in letters) < 0.8 * len(letters):
        return title
    out = []
    for i, word in enumerate(title.split()):
        core = re.sub(r"[^\w&]", "", word)
        if core.upper() in _ACRONYMS and core:
            out.append(word)
        elif i and word.lower() in _SMALL:
            out.append(word.lower())
        else:
            out.append("-".join(re.sub(r"[a-z]", lambda c: c.group(0).upper(),
                                       p.lower(), count=1) for p in word.split("-")))
    return " ".join(out)


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _clean_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# reading the volume
# ---------------------------------------------------------------------------

def read_pages(pdf: Path) -> list[dict]:
    """Each page: ``label`` (printed page, e.g. '6-28') and its ``lines``
    with the running header taken off."""
    pages = []
    with fitz.open(str(pdf)) as doc:
        for page in doc:
            lines = [ln.strip() for ln in page.get_text().split("\n")]
            label, cut = None, 0
            for k, ln in enumerate(lines[:12]):
                m = _PAGE_LABEL.match(ln)
                if m and label is None:
                    label = f"{m.group(1)}-{m.group(2)}"
                if _HEADER_END.match(ln):
                    cut = k + 1
                    break
            pages.append({"label": label, "lines": lines[cut:]})
    return pages


def _label_num(label: str | None) -> tuple[int, int] | None:
    if not label or not re.match(r"^\d", label):
        return None
    a, b = label.split("-")
    return int(a), int(b)


def parse_contents(pages: list[dict], first: int, last: int) -> list[dict]:
    text = _clean_ws(" ".join(" ".join(p["lines"]) for p in pages[first - 1:last]))
    out, seen = [], set()
    for m in _CONTENTS.finditer(text):
        sid, title = m.group(1), _clean_ws(m.group(2))
        if sid in seen:
            continue
        seen.add(sid)
        out.append({"sid": sid, "title": title,
                    "page": (int(m.group(3)), int(m.group(4)))})
    return out


def parse_list(pages: list[dict], heading: str) -> dict[str, dict]:
    """The List of Figures or List of Tables of a volume: number -> caption, page."""
    start = None
    for i, p in enumerate(pages[:60]):
        if any(ln.upper() == heading for ln in p["lines"]):
            start = i
            break
    if start is None:
        return {}
    chunk = []
    for p in pages[start:start + 12]:
        lines = p["lines"]
        if p is not pages[start] and any(
                ln.upper().startswith("LIST OF") for ln in lines):
            stop = next(k for k, ln in enumerate(lines)
                        if ln.upper().startswith("LIST OF"))
            chunk.extend(lines[:stop])
            break
        chunk.extend(lines)
    text = _clean_ws(" ".join(chunk))
    out = {}
    for m in _LIST_ENTRY.finditer(text):
        num = m.group(1)
        if num.split("-")[0] != m.group(3):
            continue
        out.setdefault(num, {"caption": _clean_ws(m.group(2)),
                             "page": (int(m.group(3)), int(m.group(4)))})
    return out


# ---------------------------------------------------------------------------
# sections
# ---------------------------------------------------------------------------

def _stream(pages: list[dict], start: int, end: int) -> list[tuple[int, str]]:
    """(page index, line) for the chapter's pages, page index 0-based."""
    out = []
    for i in range(start - 1, end):
        out.extend((i, ln) for ln in pages[i]["lines"])
    return out


def _heading_matches(rest: str, title: str) -> bool:
    a, b = _norm(rest), _norm(title)
    if not a or not b:
        return False
    n = min(len(a), len(b), 30)
    if a[:n] == b[:n]:
        return True
    return difflib.SequenceMatcher(None, a[:n], b[:n]).ratio() >= 0.8


def locate_headings(stream, pages, entries, chapter_label_ok) -> list[int]:
    """Position in ``stream`` of each entry's heading (-1 where not found)."""
    pos, cursor = [], 0
    for e in entries:
        found = -1
        for k in range(cursor, len(stream)):
            i, ln = stream[k]
            lab = _label_num(pages[i]["label"])
            if lab and lab[0] == e["page"][0] and lab[1] > e["page"][1] + 3:
                break
            if not ln.startswith(e["sid"]):
                continue
            rest = ln[len(e["sid"]):]
            if rest and not rest[0].isspace():
                continue
            rest = rest.strip()
            if not rest:
                nxt = next((s for _, s in stream[k + 1:k + 4] if s), "")
                rest = nxt
            if _heading_matches(rest, e["title"]):
                found = k
                break
        if found < 0:
            for k in range(cursor, len(stream)):
                i, ln = stream[k]
                lab = _label_num(pages[i]["label"])
                if lab and lab[0] == e["page"][0] and lab[1] > e["page"][1] + 3:
                    break
                m = re.match(r"^(\d{1,2}(?:\.\d{1,2}){1,4})\s+(.+)$", ln)
                if m and m.group(1).split(".")[0] == e["sid"].split(".")[0] \
                        and _norm(m.group(2)) == _norm(e["title"]):
                    found = k
                    e["printed_as"] = m.group(1)
                    break
        pos.append(found)
        if found >= 0:
            cursor = found + 1
    return pos


def _is_short(ln: str) -> bool:
    return 0 < len(ln) <= 3


def render_body(stream, start, end, pages, captions_on_page, eq_ids,
                chapter="", figs=None):
    """The printed text of stream[start:end] as paragraphs, with page markers
    and equation markers; equation ids found are appended to ``eq_ids`` as
    (id, preceding words, page label)."""
    paras, cur, last_page = [], [], None
    k = start
    prev_text = ""

    def flush():
        if cur:
            paras.append(" ".join(cur))
            cur.clear()

    while k < end:
        i, ln = stream[k]
        if i != last_page:
            last_page = i
            if pages[i]["label"]:
                cur.append(f"[p. {pages[i]['label']}]")
        # A run of glyphs one or two to a line is an equation object (or a
        # figure's lettering); its printed number, if any, follows it.
        if _is_short(ln):
            j = k
            while j < end and (_is_short(stream[j][1]) or not stream[j][1]) \
                    and stream[j][0] == i:
                j += 1
            n_short = sum(_is_short(stream[t][1]) for t in range(k, j))
            if n_short >= 4:
                nxt = stream[j][1] if j < end else ""
                m = _EQ_NUMBER.match(nxt)
                if m and stream[j][0] == i and m.group(1).split("-")[0] == chapter:
                    eq = m.group(1)
                    cur.append(f"[Eq. {eq}]")
                    eq_ids.append((eq, prev_text, pages[i]["label"]))
                    j += 1
                k = j
                continue
        if not ln:
            flush()
            k += 1
            continue
        m = _TYPED_EQ.match(ln)
        if (m and "=" in m.group(1) and m.group(2).split("-")[0] == chapter
                and not _REF_WORD.search(m.group(1))):
            eq = m.group(2)
            cur.append(f"{m.group(1)} [Eq. {eq}]")
            eq_ids.append((eq, prev_text, pages[i]["label"]))
            prev_text = (prev_text + " " + m.group(1))[-240:]
            k += 1
            continue
        m = _EQ_NUMBER.match(ln)
        if (m and m.group(1).split("-")[0] == chapter and cur
                and "=" in cur[-1] and "[Eq." not in cur[-1]):
            eq = m.group(1)
            cur.append(f"[Eq. {eq}]")
            eq_ids.append((eq, prev_text, pages[i]["label"]))
            k += 1
            continue
        cur.append(ln)
        prev_text = (prev_text + " " + ln)[-240:]
        k += 1
    flush()
    paras = [_clean_ws(p) for p in paras]
    paras = _drop_figure_lettering(paras, captions_on_page)
    paras = [_cut_caption(p, figs or {}) for p in paras]
    text = "\n\n".join(p for p in paras if p)
    return text


def _drop_figure_lettering(paras, captions_on_page):
    """Leave out short blocks of figure lettering: a paragraph of under 60
    characters with no sentence in it, on a page that prints a figure
    caption. ``captions_on_page`` is the set of page labels with one."""
    out, page = [], None
    for p in paras:
        for m in re.finditer(r"\[p\. ([^\]]+)\]", p):
            page = m.group(1)
        body = re.sub(r"\[p\. [^\]]+\]", "", p).strip()
        if (page in captions_on_page and body and len(body) < 60
                and not re.search(r"[.:;]\s*$", body)
                and not body.startswith(("Figure", "Table", "["))
                and not re.match(r"^\d+(\.\d+)*\s", body)):
            marker = " ".join(re.findall(r"\[p\. [^\]]+\]", p))
            if marker:
                out.append(marker)
            continue
        out.append(p)
    return out


def _cut_caption(para: str, figs: dict) -> str:
    """A figure caption paragraph ends where the List of Figures caption
    ends; what follows it is the figure's own lettering."""
    m = re.match(r"^((?:\[p\. [^\]]+\]\s*)?Figure\s+(\d{1,2}-\d{1,3})(?:([a-z])|\(([a-z])\))?"
                 r"(?:\s*\(Continued\))?[.:]\s)", para)
    num = m and m.group(2) + (m.group(3) or m.group(4) or "")
    if not m or num not in figs:
        return para
    tail = _norm(figs[num]["caption"])[-12:]
    if not tail:
        return para
    for w in re.finditer(r"\S+", para[m.end():]):
        end = m.end() + w.end()
        if _norm(para[m.end():end]).endswith(tail):
            return para[:end]
    return para


def split_long(sec: dict, limit: int = MAX_BODY_CHARS) -> list[dict]:
    """A section whose body is over ``limit`` as the section (its first part)
    and parts lettered ``.a``, ``.b`` ... under it, each cut at a paragraph
    boundary. The letters are not printed: each part's title and
    applicability say which printed pages of the section it holds."""
    body = sec["body"]
    if len(body) <= limit:
        return [sec]
    paras = body.split("\n\n")
    chunks, cur = [], []
    for p in paras:
        if cur and len("\n\n".join(cur + [p])) > limit:
            chunks.append(cur)
            cur = []
        cur.append(p)
    if cur:
        chunks.append(cur)
    out = []
    page = None
    for n, ch in enumerate(chunks):
        text = "\n\n".join(ch)
        first = re.search(r"\[p\. ([^\]]+)\]", text)
        start_page = page if (not first or not text.startswith("[p.")) else first.group(1)
        for m in re.finditer(r"\[p\. ([^\]]+)\]", text):
            page = m.group(1)
        if start_page and not text.startswith("[p."):
            text = f"[p. {start_page}] " + text
        pages = (f"p. {start_page}" if start_page == page
                 else f"pp. {start_page} to {page}")
        part = dict(sec, body=text)
        if n:
            letter = chr(ord("a") + n - 1)
            part = dict(part, section_id=f"{sec['section_id']}.{letter}",
                        title=f"{sec['title']} (continued, {pages})",
                        equations=[e for e in sec["equations"] if f"[Eq. {e['id'][4:]}]" in text],
                        figures=_listed_in(sec["figures"], text),
                        tables=_listed_in(sec["tables"], text),
                        applicability=(f"Part {n + 1} of printed Section {sec['section_id']} "
                                       f"({pages}); the letter is not printed, the "
                                       "section is split here to fit the reference tools."))
        else:
            part = dict(part,
                        equations=[e for e in sec["equations"] if f"[Eq. {e['id'][4:]}]" in text],
                        figures=_listed_in(sec["figures"], text),
                        tables=_listed_in(sec["tables"], text))
        out.append(part)
    return out


def _listed_in(items: list[str], text: str) -> list[str]:
    """The figures or tables of ``items`` whose captions are in ``text``."""
    here = set()
    for line in re.split(r"\n\n|\] ", text):
        m = _CAPTION.match(line.strip())
        if m:
            here.add(f"{m.group(1)} {_caption_number(m)}")
    return [it for it in items if it.split(":")[0] in here]


def _eq_description(words: str, eq: str, label: str | None) -> str:
    words = _clean_ws(re.sub(r"\[[^\]]*\]", " ", words))
    m = re.search(r"([^.]*?[A-Za-z][^.]*)$", words)
    tail = (m.group(1) if m else words).strip()[-200:]
    where = f" (p. {label})" if label else ""
    if len(tail) < 12:
        return f"Equation {eq} as printed{where}."
    return f"Equation {eq}, introduced by: \"{tail}\"{where}."


def build_volume(vol: dict, manifest_dir: Path, skip: set[int]) -> tuple[dict, list]:
    pdf = (manifest_dir / vol["pdf_path"]).resolve()
    pages = read_pages(pdf)
    first, last = vol["contents_pages"]
    entries = parse_contents(pages, first, last)
    figs = parse_list(pages, "LIST OF FIGURES")
    tabs = parse_list(pages, "LIST OF TABLES")

    # where each caption is printed: the page whose lines start with it
    printed_at: dict[tuple[str, str], list[int]] = {}
    for i, p in enumerate(pages):
        for ln in p["lines"]:
            m = _CAPTION.match(ln)
            if m:
                printed_at.setdefault((m.group(1), _caption_number(m)), []).append(i)
    captions_on_page = {pages[i]["label"] for (kind, _), idx in printed_at.items()
                        if kind == "Figure" for i in idx}

    chapters, catalog = {}, []
    for ch in vol["chapters"]:
        n = ch["number"]
        if n in skip:
            continue
        stream = _stream(pages, ch["page_start"], ch["page_end"])
        ch_entries = [e for e in entries if e["sid"].split(".")[0] == str(n)
                      and e["sid"] != f"{n}.0"]
        pos = locate_headings(stream, pages, ch_entries, None)
        found = [(e, p) for e, p in zip(ch_entries, pos) if p >= 0]
        missing = [e["sid"] for e, p in zip(ch_entries, pos) if p < 0]
        # the chapter's opening text, before its first numbered section
        sections = []
        bounds = [p for _, p in found] + [len(stream)]
        intro_end = bounds[0]
        heads = [{"sid": f"{n}.0", "title": ch["title"], "page": None}]
        starts = [0]
        for e, p in found:
            heads.append(e)
            starts.append(p)
        starts.append(len(stream))
        for h, s, t in zip(heads, starts, starts[1:]):
            # skip the heading's own lines (number line and title lines)
            k = s
            if h["sid"] != f"{n}.0":
                k += 1
                if stream[s][1].strip() == h["sid"]:
                    while k < t and not stream[k][1]:
                        k += 1
                    k += 1
            else:
                while k < t and (not stream[k][1] or stream[k][1].upper().startswith("CHAPTER")
                                 or _norm(stream[k][1]) in _norm(ch["title"])):
                    k += 1
            eq_ids: list = []
            body = render_body(stream, k, t, pages, captions_on_page, eq_ids,
                               chapter=str(n), figs=figs)
            page_from = pages[stream[s][0]]["label"] if s < len(stream) else None
            page_to = pages[stream[max(s, t - 1)][0]]["label"] if t > s else page_from
            seg_idx = {stream[q][0] for q in range(s, t)}
            sec_figs = [f"Figure {num}: {figs[num]['caption'] if num in figs else ''}".rstrip(": ")
                        for (kind, num), idx in sorted(printed_at.items(), key=lambda x: (x[1][0], x[0]))
                        if kind == "Figure" and any(i in seg_idx for i in idx)
                        and _caption_in_segment(stream, s, t, "Figure", num)]
            sec_tabs = [f"Table {num}: {tabs[num]['caption'] if num in tabs else ''}".rstrip(": ")
                        for (kind, num), idx in sorted(printed_at.items(), key=lambda x: (x[1][0], x[0]))
                        if kind == "Table" and any(i in seg_idx for i in idx)
                        and _caption_in_segment(stream, s, t, "Table", num)]
            title = title_case(h["title"])
            if h["sid"] == f"{n}.0" and len(re.sub(r"\[[^\]]*\]", "", body).strip()) < 20:
                continue
            pages_txt = (f"p. {page_from}" if page_from == page_to
                         else f"pp. {page_from} to {page_to}")
            sections.extend(split_long({
                "section_id": h.get("printed_as", h["sid"]),
                "title": title,
                "body": body,
                "key_points": [],
                "equations": [
                    {"id": f"Eq. {eq}", "description": _eq_description(w, eq, lab),
                     "implemented_in": None}
                    for eq, w, lab in _unique_eqs(eq_ids)],
                "figures": sec_figs,
                "tables": sec_tabs,
                "applicability": (f"{vol['volume_id']}, Chapter {n} "
                                  f"({ch['title']}), printed {pages_txt}."),
            }))
        chapters[n] = {
            "reference_id": vol["volume_id"],
            "reference_title": vol.get("volume_title", ""),
            "volume": vol["volume"],
            "chapter": n,
            "chapter_title": ch["title"],
            "sections": sections,
            "_missing": missing,
        }
    for num, f in figs.items():
        idx = printed_at.get(("Figure", num), [])
        target = None
        for i in idx:
            lab = _label_num(pages[i]["label"])
            if lab == f["page"]:
                target = i
                break
        estimated = False
        if target is None and idx:
            target = min(idx, key=lambda i: abs((_label_num(pages[i]["label"]) or (0, 0))[1] - f["page"][1]))
        if target is None:
            target = next((i for i, p in enumerate(pages)
                           if _label_num(p["label"]) == f["page"]), None)
            estimated = True
        catalog.append({
            "figure_number": num,
            "caption": f["caption"],
            "chapter": int(num.split("-")[0]),
            "pdf_page_index": target,
            "printed_page": f"{f['page'][0]}-{f['page'][1]}",
            "page_estimated": estimated,
            "description": "",
            "pdf_path": str(pdf.relative_to(REPO)).replace("\\", "/"),
            "volume": vol["volume"],
        })
    return chapters, catalog


def _caption_in_segment(stream, s, t, kind, num) -> bool:
    for q in range(s, t):
        m = _CAPTION.match(stream[q][1])
        if m and m.group(1) == kind and _caption_number(m) == num:
            return True
    return False


def _unique_eqs(eq_ids):
    seen, out = set(), []
    for eq, w, lab in eq_ids:
        if eq not in seen:
            seen.add(eq)
            out.append((eq, w, lab))
    return out


def describe_figures(text_dir: Path, figs: list[dict], max_chars: int = 600) -> int:
    """Each figure's ``description``: the title of the section that prints
    it and the manual's own sentences that refer to it, so a search by
    concept finds a chart whose caption gives only its symbols."""
    sections = []
    for jf in sorted(text_dir.glob("*.json")):
        sections += json.loads(jf.read_text(encoding="utf-8"))["sections"]
    sentences = []
    for sec in sections:
        body = re.sub(r"\[(?:p|Eq)\. [^\]]+\]", " ", sec["body"])
        sentences += [_clean_ws(x) for x in re.split(r"(?<=[.;:])\s+", body)]
    n = 0
    for f in figs:
        num = f["figure_number"]
        ref = re.compile(rf"Figures?\s+(?:\d+-\d+[a-z]?(?:,|\s+and|\s+through|\s+to)?\s+)*"
                         rf"{re.escape(num)}(?![\d])")
        where = next((sec["title"] for sec in sections if any(
            x.startswith(f"Figure {num}:") for x in sec["figures"])), "")
        said = [x for x in sentences if ref.search(x)
                and not re.match(rf"^Figure\s+{re.escape(num)}[.:(]", x)]
        desc = _clean_ws(" ".join([where + "." if where else ""] + said[:3]))
        if len(desc) > max_chars:
            desc = desc[:max_chars].rsplit(" ", 1)[0]
        f["description"] = desc
        n += bool(desc)
    return n


def build(package: str, report: bool = False) -> int:
    mf = SCRIPTS / "manifests" / f"{package}.json"
    manifest = json.loads(mf.read_text(encoding="utf-8"))
    skip = set(manifest.get("skip_chapters", []))
    text_dir = PKG / package / "text"
    text_dir.mkdir(parents=True, exist_ok=True)
    all_figs = []
    for vol in manifest["volumes"]:
        chapters, catalog = build_volume(vol, mf.parent, skip)
        all_figs.extend(catalog)
        for n, data in chapters.items():
            missing = data.pop("_missing")
            (text_dir / f"chapter{n:02d}.json").write_text(
                json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            sizes = [len(s["body"]) for s in data["sections"]]
            print(f"[{package}] ch {n}: {len(data['sections'])} sections, "
                  f"largest body {max(sizes) if sizes else 0}, "
                  f"headings not found: {missing or 'none'}")
    all_figs.sort(key=lambda f: (f["volume"], f["chapter"],
                                 int(re.match(r"\d+-(\d+)", f["figure_number"]).group(1)),
                                 f["figure_number"]))
    catalog = {
        "reference_id": manifest["reference_id"],
        "reference_title": manifest["reference_title"],
        "package": package,
        "volume": None,
        "pdf_path": all_figs[0]["pdf_path"] if all_figs else "",
        "figure_count": len(all_figs),
        "figures": all_figs,
    }
    enriched = describe_figures(text_dir, catalog["figures"])
    try:
        from build_figure_catalog import caption_problems
        problems = caption_problems(catalog)
    except ImportError:
        problems = []
    (PKG / package / "figures_catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    est = sum(f["page_estimated"] for f in all_figs)
    print(f"[{package}] {len(all_figs)} figures ({est} page estimated, "
          f"{enriched} text-enriched); caption problems: {problems or 'none'}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("packages", nargs="+")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args(argv)
    for p in args.packages:
        build(p, args.report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
