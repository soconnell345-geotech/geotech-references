"""Check every chapter JSON's section numbers and titles against the printed PDF.

The chapter text (``geotech_references/<ref>/text/*.json``) was written by
hand across sessions, and some files number their sections differently from
the printed manual (BACKLOG REF-23: GEC-12 chapter 7 dropped the 7.2.1.3
level). This script reads the source PDF named in ``scripts/manifests/`` and
builds the printed list of numbered headings for each chapter from three
sources:

* the PDF's own outline (PyMuPDF ``get_toc``), where it has numbered entries;
* the numbered headings on the pages (a line that starts with a section
  number and a capitalised title), kept only where they run in increasing
  order through the volume, which drops cross-references, table rows, step
  lists and a specification appendix's own "1.0 DESCRIPTION";
* the printed table of contents, used only to find headings the manual
  itself numbers two ways (its contents line says one number, the heading on
  the page another). Only contents lines that carry number and title together
  count, because some PDFs give a bare number's text out of reading order.
  Those headings are never renumbered; they are listed.

Each JSON section is compared with the printed list by number, by title
(words weighted by how rare they are among the printed titles) and by content
(TF-IDF cosine between the JSON text and the printed text under each heading).
Each section gets one status:

``matched``        the number is printed and the title or the text agrees
``misnumbered``    title and text belong to a printed heading with another
                   number (``missing_level`` when the printed number has one
                   more level, e.g. 7.2.1.1 printed as 7.2.1.3.1)
``title_differs``  the number is printed but neither title nor text agree
``extra``          the number is not printed and nothing printed matches
``range``          a JSON section covering a printed range (``5.4-5.6``)

and printed headings that no JSON section covers are counted as ``missing``
(most chapter files are deliberately shorter than the manual).

A renumbering is *definite* only when the title and the text point to the
same printed heading, nothing else claims that number, the print agrees with
itself about it, a nested section stays under its parent's number, and the
chapter's numbers stay unique. In a reference whose print restarts its
numbers in each chapter (GEC-13), a file whose ids mostly follow none of the
printed numbers uses its own scheme, and nothing in it is renumbered. A JSON grouping
section with no printed heading of its own, all of whose children are
renumbered, takes the range of its children (``7.2.1.3.4-7.2.1.3.7``), which
is the convention the library already uses for combined sections.
``--apply`` writes only those, in place, changing the ``section_id`` value
and nothing else, so each file keeps its formatting and line endings. What
the rules cannot settle is listed by ``--detail`` for a reader with the PDF.

Usage::

    python scripts/check_section_numbers.py                 # every reference
    python scripts/check_section_numbers.py gec_12 dm7_1     # some
    python scripts/check_section_numbers.py gec_12 --detail  # the rows to read
    python scripts/check_section_numbers.py gec_12 --apply   # write the fixes
    python scripts/check_section_numbers.py --json out.json  # everything

Parsed PDF text is cached in the temp directory (keyed by file size and
mtime), so a second run takes seconds. No API calls.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import pickle
import re
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PKG = REPO / "geotech_references"
MANIFESTS = REPO / "scripts" / "manifests"
CACHE_VERSION = 3

# References whose printed source cannot be checked this way.
SKIP = {
    "aashto_1993": "scanned PDF with no text layer",
    "wood_handbook": "the printed headings carry no section numbers",
}

# References whose printed numbers restart in every chapter ("1.0", "2.1"):
# a chapter's headings are found by the outline's chapter page ranges, and the
# JSON may carry them with or without a "<chapter>." prefix.
CHAPTER_LOCAL = {"gec_13"}

DASHES = dict.fromkeys(map(ord, "‐‑‒–—−"), "-")
GREEK = {
    "α": " alpha ", "β": " beta ", "γ": " gamma ",
    "δ": " delta ", "φ": " phi ", "ϕ": " phi ",
    "λ": " lambda ", "μ": " mu ", "σ": " sigma ",
    "τ": " tau ", "ε": " epsilon ", "θ": " theta ",
}
STOP = set(
    "a an and as at by for from in into its of on or the to with using based "
    "vs versus via per under over within".split()
)
# Words that make two otherwise similar titles different sections.
OPPOSITES = [
    ("cohesive", "cohesionless"), ("clay", "sand"), ("tension", "compression"),
    ("uplift", "compression"), ("active", "passive"), ("flexible", "rigid"),
    ("static", "dynamic"), ("drained", "undrained"), ("lateral", "axial"),
    ("horizontal", "vertical"), ("single", "group"), ("soil", "rock"),
    ("internal", "external"), ("wet", "dry"), ("hot", "cold"),
]
UNIT_WORDS = {
    "mpa", "kpa", "gpa", "kn", "mn", "m", "mm", "cm", "ft", "in", "psi",
    "ksi", "ksf", "tsf", "pcf", "pci", "lb", "lbs", "kip", "kips", "kg",
    "hz", "sec", "min", "percent", "x", "and", "or", "to",
}

NUM_DOTTED = r"(?:\d{1,2}|[A-Z])(?:\.\d{1,3}){1,6}"
NUM_UFC = r"(?:\d{1,2}|[A-Z])-\d{1,3}(?:\.\d{1,3}){0,5}"
TITLE_START = r"[A-ZΑ-Ωα-ω\"'‘“(]"
LINE_END = re.compile(r"((\.\s?){3,}|\s)\s*[\dA-Z]{1,3}([.\-]\d{1,4})?\s*$")


# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------

def clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(DASHES)
    return re.sub(r"\s+", " ", text).strip()


def strip_leaders(title: str) -> str:
    """Drop TOC dot leaders and a trailing page number from a title."""
    title = re.sub(r"(\s*\.){3,}.*$", "", title)
    title = re.sub(r"\s+\d{1,3}([.\-]\d{1,3})?\s*$", "", title)
    return title.strip(" .:")


def tokens(text: str) -> list[str]:
    text = unicodedata.normalize("NFKC", text.lower())
    for k, v in GREEK.items():
        text = text.replace(k, v)
    out = []
    for w in re.findall(r"[a-z0-9]+", text):
        if w in STOP:
            continue
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


def num_key(num: str) -> tuple:
    """Sort key for a section number in either numbering style."""
    key = []
    for p in re.split(r"[.\-]", num):
        if p.isdigit():
            key.append(int(p))
        elif len(p) == 1 and p.isalpha():
            key.append(1000 + ord(p.upper()))
        else:
            key.append(10_000)
    return tuple(key)


def chapter_of(num: str) -> str:
    return re.split(r"[.\-]", num)[0]


def depth(num: str) -> int:
    return len(re.split(r"[.\-]", num))


def level(num: str) -> int:
    """Heading level: "3.0" heads "3.1" and "3.2", so it sits one level up."""
    return depth(re.sub(r"(\.0)+$", "", num))


def parent_of(num: str) -> str:
    cut = max(num.rfind("."), num.rfind("-"))
    return num[:cut] if cut > 0 else ""


class TitleMatcher:
    """Title similarity with words weighted by rarity among printed titles."""

    def __init__(self, titles: list[str]):
        self.n = max(1, len(titles))
        self.df = Counter()
        for t in titles:
            self.df.update(set(tokens(t)))

    def w(self, tok: str) -> float:
        return math.log(1 + self.n / (1 + self.df.get(tok, 0)))

    def score(self, a: str, b: str) -> tuple[float, str]:
        """(score, grade) with grade 'strong', 'weak' or ''."""
        ta, tb = set(tokens(a)), set(tokens(b))
        if not ta or not tb:
            return 0.0, ""
        inter = ta & tb
        wi = sum(self.w(t) for t in inter)
        wa, wb = sum(self.w(t) for t in ta), sum(self.w(t) for t in tb)
        cmin, cmax = wi / min(wa, wb), wi / max(wa, wb)
        ratio = SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()
        score = max(ratio, 0.5 * (cmin + cmax))
        # a word only one printed title carries (P2A, Nordlund, software)
        unique = any(self.df.get(t, 0) == 1 and len(t) >= 3 and not t.isdigit()
                     for t in inter)
        if ratio >= 0.92 or (len(inter) >= 2 and cmin >= 0.85 and cmax >= 0.5) or (
                len(inter) >= 3 and cmin >= 0.75 and cmax >= 0.55):
            grade = "strong"
        elif ratio >= 0.75 or (cmin >= 0.6 and cmax >= 0.3) or unique or (
                tb <= ta and len(tb) <= 3 and any(len(t) >= 4 for t in tb)):
            grade = "weak"
        else:
            grade = ""
        for x, y in OPPOSITES:
            if (x in ta and y in tb and y not in ta) or (y in ta and x in tb and x not in ta):
                grade = {"strong": "weak", "weak": ""}.get(grade, "")
                score *= 0.6
        return score, grade

    def prefix(self, short: str, long: str) -> bool:
        """A wrapped contents line is the start of the heading's title."""
        ts, tl = tokens(short), tokens(long)
        return len(ts) >= 3 and tl[:len(ts)] == ts


# ---------------------------------------------------------------------------
# PDF side
# ---------------------------------------------------------------------------

@dataclass
class Heading:
    num: str
    title: str
    vol: str
    page: int            # 1-based
    line: int            # index into the volume's line stream
    sources: set = field(default_factory=set)
    alt_titles: list = field(default_factory=list)
    chapter: str = ""    # chapter key (number prefix, or outline chapter)
    text: str = ""       # printed text from the heading to the next sibling
    toc_num: str = ""    # set when the printed contents number it otherwise
    path: str = ""       # parent's title + own title ("Bearing resistance General")


def _cache_path(pdf: Path) -> Path:
    st = pdf.stat()
    tag = hashlib.sha1(
        f"{pdf.resolve()}|{st.st_size}|{int(st.st_mtime)}|{CACHE_VERSION}".encode()
    ).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / "geotech_refs_section_check" / f"{tag}.pkl"


def read_pdf(pdf: Path) -> dict:
    """Line stream + outline of one PDF (cached)."""
    cp = _cache_path(pdf)
    if cp.exists():
        try:
            return pickle.loads(cp.read_bytes())
        except Exception:
            pass
    import fitz  # PyMuPDF; only needed when the cache is cold

    doc = fitz.open(str(pdf))
    lines: list[tuple[int, str]] = []
    page_first: list[int] = []
    for i, page in enumerate(doc):
        page_first.append(len(lines))
        for raw in page.get_text("text").splitlines():
            t = clean(raw)
            if t:
                lines.append((i + 1, t))
    toc = [(lvl, clean(t), p) for lvl, t, p in doc.get_toc(simple=True)]
    data = {"lines": lines, "page_first": page_first, "toc": toc,
            "pages": doc.page_count}
    doc.close()
    cp.parent.mkdir(parents=True, exist_ok=True)
    cp.write_bytes(pickle.dumps(data))
    return data


def _toc_pages(data: dict) -> set[int]:
    """Pages that look like a table of contents or list of figures."""
    per_page = defaultdict(int)
    named = set()
    for page, t in data["lines"]:
        if re.search(r"(\.\s?){4,}\s*[\dA-Z]", t):
            per_page[page] += 1
        if re.fullmatch(r"(TABLE OF )?CONTENTS|LIST OF (FIGURES|TABLES)|"
                        r"Table of Contents|Contents", t):
            named.add(page)
    return {p for p, n in per_page.items() if n >= 4} | named


def _heading_re(style: str) -> re.Pattern:
    num = NUM_UFC if style == "ufc" else NUM_DOTTED
    return re.compile(
        rf"^(?:Section\s+|SECTION\s+)?(?P<num>{num})\.?\s+(?P<title>{TITLE_START}.*)$"
    )


def _num_only_re(style: str) -> re.Pattern:
    num = NUM_UFC if style == "ufc" else NUM_DOTTED
    return re.compile(rf"^(?P<num>{num})\.?$")


def _plausible_title(title: str) -> bool:
    if len(title) < 2 or len(title) > 160:
        return False
    first = re.split(r"[\s,;:]", title, maxsplit=1)[0].lower().strip("().")
    if first in UNIT_WORDS:
        return False
    if sum(c.isdigit() for c in title) > 0.3 * len(title):
        return False
    words = title.split()
    long_words = [w for w in words if len(w) > 3 and w[0].isalpha()]
    if len(words) >= 8 and long_words and (
            sum(w[0].islower() for w in long_words) > 0.6 * len(long_words)):
        return False  # a sentence that happens to start with a number
    return not re.search(r"(\.\s?){4,}", title)


def _lis(items: list, key) -> list:
    """Longest strictly increasing subsequence (by key), in input order."""
    tails: list = []
    tails_idx: list[int] = []
    prev = [-1] * len(items)
    for i, it in enumerate(items):
        k = key(it)
        j = bisect.bisect_left(tails, k)
        if j == len(tails):
            tails.append(k)
            tails_idx.append(i)
        else:
            tails[j] = k
            tails_idx[j] = i
        prev[i] = tails_idx[j - 1] if j > 0 else -1
    out = []
    i = tails_idx[-1] if tails_idx else -1
    while i >= 0:
        out.append(items[i])
        i = prev[i]
    return out[::-1]


def _chapter_ranges_from_outline(toc: list) -> list[tuple[int, int, str]]:
    """(first_page, last_page, chapter) from 'Chapter N' outline entries."""
    starts = sorted(
        (p, m.group(1)) for _, t, p in toc
        if p > 0 and (m := re.match(r"chapter[\s_]*(\d+)", t, re.I))
    )
    return [(p, (starts[i + 1][0] - 1 if i + 1 < len(starts) else 10**6), ch)
            for i, (p, ch) in enumerate(starts)]


def _contents_entries(data: dict, pages: set[int], head_re,
                      only_re) -> list[tuple[str, str, bool]]:
    """(number, title, inline) from the printed contents, wrapped lines
    joined. ``inline`` is True where the number and the title start on one
    line; a bare number's title is the next line only when the PDF gives the
    text in reading order, which not every PDF does."""
    lines = [t for page, t in data["lines"] if page in pages]
    out: list[list] = []
    cur = None
    for t in lines:
        m = head_re.match(t) or only_re.match(t)
        if m:
            cur = [m.group("num"), m.groupdict().get("title") or "", 0, bool(
                m.groupdict().get("title"))]
            out.append(cur)
        elif cur is not None and cur[2] < 3 and not cur[1].endswith("\0"):
            cur[1] = (cur[1] + " " + t).strip()
            cur[2] += 1
        else:
            continue
        if LINE_END.search(t):
            cur[1] += "\0"
    return [(n, strip_leaders(t.rstrip("\0")), inline) for n, t, _, inline in out]


def printed_headings(ref: str, pdfs: list[tuple[str, Path]], style: str):
    """({chapter: [Heading]}, {chapter: [(num, title)] from the contents})."""
    by_chapter: dict[str, list[Heading]] = defaultdict(list)
    contents: dict[str, list[tuple[str, str]]] = defaultdict(list)
    head_re, only_re = _heading_re(style), _num_only_re(style)
    local = ref in CHAPTER_LOCAL
    for vol, pdf in pdfs:
        data = read_pdf(pdf)
        lines, page_first = data["lines"], data["page_first"]
        skip = _toc_pages(data)
        ranges = _chapter_ranges_from_outline(data["toc"]) if local else []

        def chapter_for(num: str, page: int) -> str | None:
            if not local:
                return chapter_of(num)
            for a, b, ch in ranges:
                if a <= page <= b:
                    return ch
            return None

        if not local:
            for num, title, inline in _contents_entries(data, skip, head_re, only_re):
                contents[chapter_of(num)].append((num, title, inline))

        # 1. headings printed on the pages
        cands: list[Heading] = []
        for i, (page, t) in enumerate(lines):
            if page in skip:
                continue
            m = head_re.match(t)
            title = None
            if m:
                title = m.group("title")
            else:
                m = only_re.match(t)
                if m and i + 1 < len(lines) and lines[i + 1][0] == page:
                    nxt = lines[i + 1][1]
                    if re.match(TITLE_START, nxt) and not only_re.match(nxt):
                        title = nxt
            if title is None:
                continue
            title = strip_leaders(title)
            if not _plausible_title(title):
                continue
            num = m.group("num")
            ch = chapter_for(num, page)
            if ch is not None:
                cands.append(Heading(num, title, vol, page, i, {"page"}, chapter=ch))

        # 2. the outline. An entry whose number does not sit under the
        #    numbered entry the outline nests it in is a misprint of the
        #    sub-number (GEC-13 ch 10 prints "2.1.2.1 Advantages" under
        #    "2.2.1"); it and the page heading it came from are left out, so
        #    the increasing-run filter keeps the real numbers around it.
        outline: list[Heading] = []
        stack: list[tuple[int, str]] = []
        misprinted: set[tuple[str, int]] = set()
        for lvl, t, p in data["toc"]:
            m = head_re.match(t) if p > 0 else None
            while stack and stack[-1][0] >= lvl:
                stack.pop()
            if not m:
                continue
            num = m.group("num")
            above = stack[-1][1] if stack else None
            if above and above.endswith(".0"):
                above = above[:-2]        # "2.0" is the chapter-level "2"
            if (above and level(num) == level(above) + 1
                    and parent_of(num) != above):
                misprinted.add((num, p))
                continue
            stack.append((lvl, num))
            ch = chapter_for(num, p)
            if ch is None:
                continue
            idx = page_first[p - 1] if p - 1 < len(page_first) else len(lines) - 1
            end = page_first[p] if p < len(page_first) else len(lines)
            for j in range(idx, end):
                if re.match(rf"^{re.escape(num)}\.?(\s|$)", lines[j][1]):
                    idx = j
                    break
            outline.append(Heading(num, strip_leaders(m.group("title")), vol, p, idx,
                                   {"outline"}, chapter=ch))

        cands = [h for h in cands if (h.num, h.page) not in misprinted]
        groups: dict[str, list[Heading]] = defaultdict(list)
        if not local:
            cands = _lis(cands, key=lambda h: num_key(h.num))
        for h in cands:
            groups[h.chapter].append(h)
        ogroups: dict[str, list[Heading]] = defaultdict(list)
        if not local:
            outline = _lis(outline, key=lambda h: num_key(h.num))
        for h in outline:
            ogroups[h.chapter].append(h)
        for ch in set(groups) | set(ogroups):
            merged: dict[str, Heading] = {}
            for h in _lis(ogroups.get(ch, []), key=lambda h: num_key(h.num)):
                merged[h.num] = h
            for h in _lis(groups.get(ch, []), key=lambda h: num_key(h.num)):
                if h.num in merged:
                    o = merged[h.num]
                    o.sources.add("page")
                    if tokens(o.title) != tokens(h.title):
                        o.alt_titles.append(h.title)
                    o.line, o.page = h.line, h.page
                else:
                    merged[h.num] = h
            by_chapter[ch].extend(sorted(merged.values(), key=lambda h: num_key(h.num)))

        # 3. the printed text under each heading, up to the next heading at
        #    the same or a higher level (so a parent's text holds its children)
        vol_heads = sorted((h for hs in by_chapter.values() for h in hs if h.vol == vol),
                           key=lambda h: h.line)
        for k, h in enumerate(vol_heads):
            end = h.line + 4000
            for h2 in vol_heads[k + 1:]:
                if h2.line > h.line and level(h2.num) <= level(h.num):
                    end = min(end, h2.line)
                    break
            h.text = " ".join(t for _, t in lines[h.line:min(end, len(lines))])
    # a chapter lives in one volume; the others only cite its numbers
    for ch, hs in by_chapter.items():
        vols = Counter(h.vol for h in hs)
        if len(vols) > 1:
            home = vols.most_common(1)[0][0]
            by_chapter[ch] = [h for h in hs if h.vol == home]
    for hs in by_chapter.values():
        heads = {h.num: h for h in hs}
        for h in hs:
            par = heads.get(parent_of(h.num))
            h.path = f"{par.title} {h.title}" if par else ""
    return by_chapter, contents


def flag_contents_disagreements(pool: list[Heading], toc: list[tuple[str, str, bool]],
                                matcher: TitleMatcher) -> set[str]:
    """Numbers the printed manual gives two ways (contents vs. page heading)."""
    if not toc:
        return set()

    def agrees(h: Heading, t: str) -> bool:
        return any(matcher.score(x, t)[1] == "strong" or matcher.prefix(t, x)
                   for x in [h.title] + h.alt_titles)

    by_num = defaultdict(list)
    for n, t, _ in toc:
        by_num[n].append(t)
    heads = {h.num: h for h in pool}
    # contents lines that no page heading of the same number agrees with
    orphans = [(n, t) for n, t, inline in toc
               if inline and not (n in heads and agrees(heads[n], t))]
    ambiguous = set()
    for h in pool:
        if any(agrees(h, t) for t in by_num.get(h.num, [])):
            continue
        for n, t in orphans:
            if n != h.num and agrees(h, t):
                h.toc_num = n
                ambiguous.update({h.num, n})
                break
    return ambiguous


# ---------------------------------------------------------------------------
# JSON side
# ---------------------------------------------------------------------------

@dataclass
class JSec:
    sid: str
    title: str
    text: str
    chapter_key: str
    parent: str | None


def json_sections(ref: str) -> dict[Path, list[JSec]]:
    out: dict[Path, list[JSec]] = {}
    for jf in sorted((PKG / ref / "text").glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        ch = str(data.get("chapter", ""))
        secs: list[JSec] = []

        def walk(items, parent):
            for s in items or []:
                if not isinstance(s, dict):
                    continue
                sid = str(s.get("section_id", "")).strip()
                text = " ".join(
                    [s.get("title", ""), s.get("summary", "") or "", s.get("body", "") or ""]
                    + [str(k) for k in (s.get("key_points") or [])]
                )
                secs.append(JSec(sid, s.get("title", ""), text, ch, parent))
                walk(s.get("subsections"), sid)

        walk(data.get("sections"), None)
        out[jf] = secs
    return out


def numbering_style(secs: list[JSec]) -> str:
    ufc = sum(bool(re.match(r"^(\d+|[A-Z])-\d", s.sid)) for s in secs)
    return "ufc" if ufc > len(secs) / 2 else "dotted"


def ref_pdfs(ref: str) -> list[tuple[str, Path]]:
    found: dict[Path, str] = {}
    for mf in sorted(MANIFESTS.glob("*.json")):
        m = json.loads(mf.read_text(encoding="utf-8"))
        if m.get("package") != ref:
            continue
        entries = [(m.get("volume"), m.get("pdf_path"))]
        entries += [(v.get("volume"), v.get("pdf_path")) for v in m.get("volumes", [])]
        for vol, rel in entries:
            if rel:
                p = (mf.parent / rel).resolve()
                if p.exists() and p not in found:
                    found[p] = str(vol if vol is not None else 1)
    return [(v, p) for p, v in found.items()]


# ---------------------------------------------------------------------------
# comparison
# ---------------------------------------------------------------------------

class Tfidf:
    def __init__(self, docs: list[str]):
        toks = [self._count(d) for d in docs]
        self.df = Counter()
        for c in toks:
            self.df.update(c.keys())
        self.n = max(1, len(docs))
        self.vecs = [self.vec(c) for c in toks]

    @staticmethod
    def _count(text: str) -> Counter:
        return Counter(t for t in tokens(text) if len(t) > 2 and not t.isdigit())

    def vec(self, c: Counter) -> dict:
        v = {w: (1 + math.log(f)) * math.log(1 + self.n / (1 + self.df.get(w, 0)))
             for w, f in c.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {w: x / norm for w, x in v.items()}

    def query(self, text: str) -> list[float]:
        q = self.vec(self._count(text))
        return [sum(q[w] * d.get(w, 0.0) for w in q) for d in self.vecs]


def is_range(sid: str, style: str) -> tuple[str, str] | None:
    num = NUM_DOTTED if style == "dotted" else NUM_UFC
    sep = r"-" if style == "dotted" else r"\s*(?:to|,|--)\s*"
    m = re.fullmatch(rf"({num}){sep}({num})", sid)
    return (m.group(1), m.group(2)) if m else None


def compare_reference(ref: str) -> dict:
    files = json_sections(ref)
    all_secs = [s for v in files.values() for s in v]
    style = numbering_style(all_secs)
    pdfs = ref_pdfs(ref)
    result = {"reference": ref, "style": style, "pdfs": [p.name for _, p in pdfs],
              "chapters": [], "skipped": None}
    if ref in SKIP:
        result["skipped"] = SKIP[ref]
        return result
    if not pdfs:
        result["skipped"] = "source PDF not in docs/"
        return result
    printed, contents = printed_headings(ref, pdfs, style)
    matcher = TitleMatcher([t for hs in printed.values() for h in hs
                            for t in [h.title] + h.alt_titles])

    groups = []
    for jf, secs in files.items():
        if ref in CHAPTER_LOCAL:
            groups.append((jf, _chapter_key(ref, secs) if secs else "", secs))
            continue
        by_ch: dict[str, list[JSec]] = defaultdict(list)
        for s in secs:
            rng = is_range(s.sid, style)
            by_ch[chapter_of(rng[0] if rng else s.sid)].append(s)
        groups += [(jf, ch, ss) for ch, ss in by_ch.items()]

    for jf, ch_key, secs in groups:
        if not secs:
            continue
        pool = printed.get(ch_key, [])
        prefixed = ref in CHAPTER_LOCAL and _uses_prefix(ch_key, secs, pool)

        def jnum(h: Heading) -> str:
            return f"{ch_key}.{h.num}" if prefixed else h.num

        ambiguous = {f"{ch_key}.{n}" if prefixed else n
                     for n in flag_contents_disagreements(pool, contents.get(ch_key, []), matcher)}
        by_num = {}
        for h in pool:
            by_num.setdefault(jnum(h), h)
        tf = Tfidf([h.text for h in pool]) if pool else None
        sids = [s.sid for s in secs]
        parents = {a for a in sids if any(b.startswith(a + ".") for b in sids)}
        rows = [_classify(s, pool, by_num, tf, style, matcher, jnum, parents) for s in secs]
        for r in rows:
            if r["sid"] in ambiguous:
                h = by_num.get(r["sid"])
                r["print_ambiguous"] = (
                    f"page heading {r['sid']}, contents {h.toc_num}" if h and h.toc_num
                    else "the contents number this heading differently")
        singles = [r for r in rows if r["status"] != "range"]
        own_scheme = ref in CHAPTER_LOCAL and bool(singles) and (
            sum(r["status"] == "matched" for r in singles) < 0.5 * len(singles))
        if own_scheme:
            for r in rows:
                if r["status"] in ("misnumbered", "missing_level"):
                    r["hold"] = ("the file numbers its sections its own way (the print "
                                 "restarts in each chapter); renumber it by hand")
        _decide_fixes(rows, ambiguous, by_num)
        covered = set()
        for r in rows:
            covered.add(r.get("new") or r["sid"])
            if r["status"] in ("misnumbered", "missing_level") and r.get("target"):
                covered.add(r["target"])
            covered.update(r.get("covers", []))
            if r.get("new") and is_range(r["new"], style):
                a, b = is_range(r["new"], style)
                nums = [jnum(h) for h in pool]
                if a in nums and b in nums:
                    covered.update(nums[nums.index(a): nums.index(b) + 1])
        missing = [{"num": jnum(h), "title": h.title} for h in pool if jnum(h) not in covered]
        result["chapters"].append({
            "file": jf.relative_to(PKG).as_posix(),
            "chapter_key": ch_key,
            "printed": len(pool),
            "own_scheme": own_scheme,
            "sources": sorted({src for h in pool for src in h.sources}),
            "ambiguous": sorted(ambiguous, key=num_key),
            "rows": rows,
            "missing": missing,
        })
    return result


def _uses_prefix(ch: str, secs: list[JSec], pool: list[Heading]) -> bool:
    nums = {h.num for h in pool}
    plain = sum(s.sid in nums for s in secs)
    pref = sum(s.sid.startswith(ch + ".") and s.sid[len(ch) + 1:] in nums for s in secs)
    return pref > plain


def _chapter_key(ref: str, secs: list[JSec]) -> str:
    if ref in CHAPTER_LOCAL:
        return secs[0].chapter_key
    return Counter(chapter_of(s.sid) for s in secs if s.sid).most_common(1)[0][0]


def _classify(s: JSec, pool, by_num, tf, style, matcher: TitleMatcher, jnum,
              parents: set[str]) -> dict:
    row = {"sid": s.sid, "title": s.title, "status": "", "target": None,
           "target_title": None, "evidence": "", "parent": s.parent}
    rng = is_range(s.sid, style)
    if rng:
        nums = [jnum(h) for h in pool]
        a, b = rng
        if a in nums and b in nums and nums.index(a) <= nums.index(b):
            row["status"] = "range"
            row["covers"] = nums[nums.index(a): nums.index(b) + 1]
        else:
            row["status"] = "extra"
            row["evidence"] = "a range whose ends are not both printed"
        return row
    if not pool:
        row["status"] = "extra"
        row["evidence"] = "no printed headings found for this chapter"
        return row

    content = tf.query(s.text)
    order = sorted(range(len(pool)), key=lambda i: -content[i])
    rank = {i: r for r, i in enumerate(order)}
    best_c = order[0]
    margin = content[best_c] - (content[order[1]] if len(order) > 1 else 0.0)

    def tscore(h: Heading, with_path: bool = False):
        best = (0.0, "")
        own = [h.title] + h.alt_titles
        path = [h.path] if with_path and h.path and len(tokens(h.title)) <= 2 else []
        for t in own + path:
            sc = matcher.score(s.title, t)
            if t not in own and sc[1] != "strong":
                continue
            if (sc[1] == "strong", sc[1] == "weak", sc[0]) > (
                    best[1] == "strong", best[1] == "weak", best[0]):
                best = sc
        return best

    tit = [tscore(h) for h in pool]
    same = by_num.get(s.sid)
    same_i = pool.index(same) if same is not None else None
    if same_i is not None:
        tit[same_i] = tscore(same, with_path=True)
    same_grade = tit[same_i][1] if same_i is not None else ""
    if same_grade == "strong" or (same_grade == "weak" and rank[same_i] <= 2):
        row["status"] = "matched"
        row["evidence"] = f"title {same_grade}"
        return row

    target = ev = None
    # never a heading inside the section's own number (a parent matches its
    # children's words), and against a weak same-number title only a strong
    # title the text also ranks first
    strong = sorted((i for i, t in enumerate(tit) if t[1] == "strong"
                     and not (s.sid in parents and jnum(pool[i]).startswith(s.sid + "."))
                     and (same_grade != "weak" or rank[i] == 0)),
                    key=lambda i: (rank[i], -tit[i][0]))
    if strong:
        cand = strong[0]
        unique = len(strong) == 1 or rank[strong[1]] > rank[cand] + 2
        if rank[cand] <= 2 and unique:
            target, ev = cand, f"title strong, content rank {rank[cand] + 1}"
        elif len(strong) == 1 and content[best_c] < 0.08:
            target, ev = cand, "title strong, too little printed text to compare"
        else:
            row["evidence"] = (f"title matches {', '.join(jnum(pool[i]) for i in strong[:3])}; "
                               f"content best {jnum(pool[best_c])}")
    if target is None and not same_grade and tit[best_c][1] == "weak" \
            and margin >= 0.05 and content[best_c] >= 0.2 \
            and not (s.sid in parents and jnum(pool[best_c]).startswith(s.sid + ".")):
        target, ev = best_c, f"title weak, content best (margin {margin:.2f})"

    if target is not None and jnum(pool[target]) != s.sid:
        row["target"] = jnum(pool[target])
        row["target_title"] = pool[target].title
        row["evidence"] = ev
        t = row["target"]
        row["status"] = ("missing_level"
                         if depth(t) == depth(s.sid) + 1 and parent_of(s.sid)
                         and parent_of(parent_of(t)) == parent_of(s.sid)
                         and re.split(r"[.\-]", t)[-1] == re.split(r"[.\-]", s.sid)[-1]
                         else "misnumbered")
        return row
    if same_i is not None:
        if same_grade == "weak":
            row["status"] = "matched"
            row["evidence"] = "title weak"
        elif rank[same_i] == 0 and content[same_i] >= 0.15:
            row["status"] = "matched"
            row["evidence"] = "content best (title paraphrased)"
        else:
            row["status"] = "title_differs"
            row["target_title"] = same.title
            row["evidence"] = row["evidence"] or (
                f"printed '{same.title}'; content best {jnum(pool[best_c])}")
        return row
    row["status"] = "extra"
    row["evidence"] = row["evidence"] or (
        f"content best {jnum(pool[best_c])} '{pool[best_c].title}'")
    return row


def _decide_fixes(rows: list[dict], ambiguous: set[str], by_num: dict) -> None:
    """Choose the renumberings that need no guess; set row['new'] on them."""
    moving = [r for r in rows if r["status"] in ("misnumbered", "missing_level")]
    for r in moving:
        if r.get("hold"):
            continue
        if r["target"] in ambiguous or r["sid"] in ambiguous:
            r["hold"] = "the printed manual numbers this heading two ways"
    cands = [r for r in moving if not r.get("hold")]
    kids_of = defaultdict(list)
    for x in rows:
        if x.get("parent"):
            kids_of[x["parent"]].append(x)

    def container_ids() -> dict[str, str]:
        """A grouping section with no printed heading of its own, all of whose
        children move, takes the range of their new numbers."""
        out = {}
        for r in rows:
            kids = kids_of.get(r["sid"], [])
            if r["status"] in ("title_differs", "extra") and kids and all(
                    k in cands for k in kids):
                first, last = kids[0]["target"], kids[-1]["target"]
                out[r["sid"]] = f"{first}-{last}" if first != last else first
        return out

    changed = True
    while changed:
        changed = False
        cont = container_ids()
        final = {x["sid"]: cont.get(x["sid"], x["sid"]) for x in rows}
        for r in cands:
            final[r["sid"]] = r["target"]
        # 1. a nested section must stay under its parent's number
        for r in list(cands):
            if not r.get("parent"):
                continue
            pnew = final.get(r["parent"], r["parent"])
            if re.search(r"\.\d+-\d", pnew):
                pnew = parent_of(pnew.split("-")[0])
            if not r["target"].startswith(pnew + "."):
                r["hold"] = (f"it would sit under section {pnew} in this file "
                             "(the file nests sections)")
                cands.remove(r)
                changed = True
        if changed:
            continue
        # 2. one claimant per printed number
        claims = Counter(r["target"] for r in cands)
        for r in list(cands):
            if claims[r["target"]] > 1:
                rivals = [x for x in cands if x["target"] == r["target"]]
                split = all(x["sid"].startswith(r["target"] + ".") for x in rivals)
                r["hold"] = (f"the file splits printed {r['target']} into parts" if split
                             else "another JSON section claims the same printed number")
                cands.remove(r)
                changed = True
        if changed:
            continue
        # 3. the number must be free once everything else has moved
        taken = Counter(final.values())
        for r in list(cands):
            if taken[r["target"]] > 1:
                holder = next(x for x in rows if x is not r and final[x["sid"]] == r["target"])
                r["hold"] = f"{r['target']} is held by '{holder['title']}' ({holder['status']})"
                cands.remove(r)
                changed = True
    cont = container_ids()
    for r in rows:
        if r["sid"] in cont:
            r["new"], r["container"] = cont[r["sid"]], True
    for r in cands:
        r["new"] = r["target"]
    for r in rows:
        r["fix"] = bool(r.get("new")) and r["new"] != r["sid"]


# ---------------------------------------------------------------------------
# applying fixes
# ---------------------------------------------------------------------------

def apply_fixes(result: dict) -> list[tuple[str, str, str]]:
    """Rewrite the definite renumberings in place; returns (file, old, new)."""
    done = []
    for ch in result["chapters"]:
        fixes = {r["sid"]: r["new"] for r in ch["rows"] if r.get("fix")}
        if not fixes:
            continue
        rewrite_ids(PKG / ch["file"], fixes)
        done += [(ch["file"], o, n) for o, n in fixes.items()]
    return done


def rewrite_ids(path: Path, fixes: dict[str, str]) -> None:
    """Change ``section_id`` values {old: new} in one chapter file, touching
    only those characters (formatting and line endings stay as they are)."""
    text = path.read_bytes().decode("utf-8")
    spans = []
    for old, new in fixes.items():
        pat = re.compile(r'("section_id"\s*:\s*)"' + re.escape(old) + '"')
        hits = list(pat.finditer(text))
        if len(hits) != 1:
            raise SystemExit(f"{path}: section_id {old!r} found {len(hits)} times")
        spans.append((hits[0].start(), hits[0].end(), hits[0].group(1) + json.dumps(new)))
    out, pos = [], 0
    for a, b, rep in sorted(spans):
        out += [text[pos:a], rep]
        pos = b
    new_text = "".join(out) + text[pos:]
    _assert_only_ids_changed(json.loads(text), json.loads(new_text), fixes)
    path.write_bytes(new_text.encode("utf-8"))


def _assert_only_ids_changed(a, b, fixes: dict) -> None:
    if isinstance(a, dict):
        assert isinstance(b, dict) and list(a) == list(b), "keys changed"
        for k in a:
            if k == "section_id" and a[k] != b[k]:
                assert fixes.get(a[k]) == b[k], f"unexpected id change {a[k]}"
            else:
                _assert_only_ids_changed(a[k], b[k], fixes)
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), "list length changed"
        for x, y in zip(a, b):
            _assert_only_ids_changed(x, y, fixes)
    else:
        assert a == b, "value changed"


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

STATUSES = ["matched", "range", "misnumbered", "missing_level", "title_differs", "extra"]


def summarize(result: dict) -> dict:
    c = Counter()
    for ch in result["chapters"]:
        for r in ch["rows"]:
            c[r["status"]] += 1
            c["fixable"] += bool(r.get("fix"))
            c["ambiguous"] += bool(r.get("print_ambiguous"))
        c["missing"] += len(ch["missing"])
        c["printed"] += ch["printed"]
    return dict(c)


def run(refs: list[str], apply: bool = False) -> list[dict]:
    results = []
    for ref in refs:
        res = compare_reference(ref)
        if apply and not res["skipped"]:
            res["applied"] = apply_fixes(res)
        results.append(res)
    return results


def all_refs() -> list[str]:
    return sorted({p.parent.parent.name for p in PKG.glob("*/text/*.json")})


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("refs", nargs="*")
    ap.add_argument("--detail", action="store_true", help="print every row to read")
    ap.add_argument("--apply", action="store_true", help="write the definite fixes")
    ap.add_argument("--json", help="write the full result to this file")
    args = ap.parse_args(argv)
    results = run(args.refs or all_refs(), apply=args.apply)
    cols = ["printed"] + STATUSES + ["missing", "fixable", "ambiguous"]
    print(f"{'reference':22s} " + " ".join(f"{c[:9]:>9s}" for c in cols))
    for res in results:
        if res["skipped"]:
            print(f"{res['reference']:22s}  skipped: {res['skipped']}")
            continue
        sm = summarize(res)
        print(f"{res['reference']:22s} " + " ".join(f"{sm.get(c, 0):9d}" for c in cols))
    if args.detail:
        for res in results:
            for ch in res["chapters"]:
                for r in ch["rows"]:
                    if r["status"] in ("matched", "range") and not r.get("print_ambiguous"):
                        continue
                    flag = "FIX " if r.get("fix") else ("HOLD" if r.get("target") else "    ")
                    tgt = (f"-> {r['new']}" if r.get("fix") else
                           f"-> {r['target']} '{r['target_title']}'" if r.get("target") else "")
                    note = r.get("hold") or r.get("print_ambiguous") or ""
                    print(f"{flag} {ch['file']:36s} {r['status']:13s} {r['sid']:11s} "
                          f"'{r['title'][:48]}' {tgt} [{r['evidence']}]"
                          + (f" ({note})" if note else ""))
    if args.apply:
        for res in results:
            for f, o, n in res.get("applied", []):
                print(f"renumbered {f}: {o} -> {n}")
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
