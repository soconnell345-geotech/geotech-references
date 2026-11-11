"""Build a manual's appendices from its printed pages (no API).

The companion of ``build_printed_text.py`` for appendices that the printed
contents list without page numbers and the Lists of Figures and Tables leave
out (the FHWA NHI-06-089 Soils and Foundations Reference Manual, Appendices
A to E, app BACKLOG REF-85). It reads the pages the same way and reuses that
script's pieces (title case, the split of long sections, the typed-in
equations and their ``fix`` entries), so a chapter built by that script is
untouched. What the appendices need on top:

1. a volume's manifest entry carries ``appendices``, each with ``letter``,
   ``number`` (the chapter number its file is filed under), ``title`` (as
   printed), ``file``, ``page_start`` / ``page_end`` (1-based PDF pages),
   and its printed headings in ``sections`` (``id``, ``title`` as printed,
   ``page`` the printed page, optional ``printed`` when the heading line
   prints something other than the id, e.g. "SECTION A.2", and optional
   ``start_page`` when the section begins at the top of an earlier page than
   its heading, e.g. the overview figure printed before "SECTION A.2");
2. a printed page is labelled as the appendix prints it ("B - 3",
   "A.6 - 12"); a page with no label (a blank page) is left out;
3. ``figures`` and ``tables`` list each one by printed number, page and
   caption as printed (the volume's lists do not carry them); a section
   lists those whose caption is printed in it, and a figure caption's
   paragraph ends where the listed caption ends (what follows is the
   figure's own lettering);
4. ``figure_pages`` are pages that print only a figure (a boring log, a
   chart, a screen shot): only their captions are kept;
5. ``typed_pages`` names a text file of pages typed in from renders of the
   printed page (``=== A.6-8`` then the page's text; a blank line ends a
   paragraph, a line break inside a paragraph is kept), for a calculation
   sheet or table the text layer scrambles; the typed text replaces that
   page's text layer, and an equation the page numbers is marked there as
   ``[Eq. B-2a]``;
6. on the other pages the text layer is read as the chapters are: a run of
   glyphs one or two to a line (an equation object, a table's cells, a
   figure's lettering) is kept as a line of text on a page with no figure
   and dropped on a page with one, and short blocks of lettering on a page
   with a figure are dropped; ``fix`` entries of ``printed_equations``
   (``{"find", "replace"}``) and the appendix's own ``fixes`` mend what the
   text layer lost, each of which must apply. A glyph run kept as text must
   be mended by a fix, or the build stops and names it.

Usage::

    python scripts/build_printed_appendices.py fhwa_soils_foundations
    python scripts/build_printed_appendices.py fhwa_soils_foundations --report
    python scripts/build_printed_appendices.py fhwa_soils_foundations --only B

Requires PyMuPDF.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from build_printed_text import (  # noqa: E402
    PKG, _DASH, _clean_ws, _is_short, _norm,
    add_printed_equations, chapter_json, fitz, fix_printed_equations,
    split_long, title_case)

#: An appendix page's printed number ("B - 3", "A.6 - 12", "A - 1").
_APP_LABEL = re.compile(rf"^([A-E](?:\.\d{{1,2}})?)\s*[-{_DASH}]\s*(\d{{1,3}})$")
_HEADER_END = re.compile(r"^December\s+2006$")
_BLANK = "[THIS PAGE INTENTIONALLY BLANK]"


def read_appendix_pages(pdf: Path, first: int, last: int) -> list[dict]:
    """Each labelled page from ``first`` to ``last`` (1-based): ``label``
    ('A.6-12'), ``index`` (0-based PDF page) and its ``lines`` with the
    running header taken off. Unlabelled pages (the appendix's title page,
    blank pages) are left out."""
    out = []
    with fitz.open(str(pdf)) as doc:
        for i in range(first - 1, last):
            lines = [ln.strip() for ln in doc[i].get_text().split("\n")]
            label, cut = None, 0
            for k, ln in enumerate(lines[:14]):
                m = _APP_LABEL.match(ln)
                if m and label is None:
                    label = f"{m.group(1)}-{m.group(2)}"
                if _HEADER_END.match(ln):
                    cut = k + 1
                    break
            if label is None:
                continue
            body = [ln for ln in lines[cut:] if ln != _BLANK]
            out.append({"label": label, "index": i, "lines": body})
    return out


def read_typed_pages(path: Path) -> dict[str, str]:
    """``{page label: typed text}`` from a file of ``=== <label>`` blocks."""
    if not path.exists():
        raise FileNotFoundError(path)
    out, cur, buf = {}, None, []
    for ln in path.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^=== (\S+)\s*$", ln)
        if m:
            if cur:
                out[cur] = "\n".join(buf).strip("\n")
            cur, buf = m.group(1), []
            if cur in out:
                raise ValueError(f"{path.name}: page {cur} typed twice")
        elif cur:
            buf.append(ln.rstrip())
    if cur:
        out[cur] = "\n".join(buf).strip("\n")
    return out


# ---------------------------------------------------------------------------
# the stream of lines and the headings
# ---------------------------------------------------------------------------

def make_stream(pages: list[dict], typed: dict[str, str]) -> list[tuple]:
    """(page position, line, typed) for every line of the appendix: a typed
    page's lines in place of its text layer."""
    stream = []
    for n, p in enumerate(pages):
        if p["label"] in typed:
            stream.extend((n, ln, True) for ln in typed[p["label"]].split("\n"))
        else:
            stream.extend((n, ln, False) for ln in p["lines"])
    return stream


def _page_pos(pages, label: str) -> int:
    for n, p in enumerate(pages):
        if p["label"] == label:
            return n
    raise ValueError(f"no printed page {label}")


def locate_heading(stream, pages, sec: dict, cursor: int) -> tuple[int, int, str]:
    """(first line, line after the heading, text printed after the title on
    the heading line) of a manifest heading, searched from its printed page
    to three pages on."""
    start_page = _page_pos(pages, sec["page"])
    printed = sec.get("printed", sec["id"])
    title = _norm(sec["title"])
    for k in range(cursor, len(stream)):
        n, ln, _ = stream[k]
        if n < start_page:
            continue
        if n > start_page + 3:
            break
        if not (ln == printed or ln.startswith(printed + " ")):
            continue
        rest = ln[len(printed):].strip()
        got, j = _norm(rest), k + 1
        if got.startswith(title):
            # the title on the heading line, which may go on after it
            # ("A.2-1 RELEVANT CONCEPTS AND PROCEDURES (Refer to ...)")
            extra, acc = "", ""
            words = rest.split()
            for w_i, w in enumerate(words):
                acc += _norm(w)
                if len(acc) >= len(title):
                    extra = " ".join(words[w_i + 1:])
                    break
            return k, k + 1, extra
        if got and not title.startswith(got):
            continue
        # the title on the lines after the heading line, a word or more each
        while len(got) < len(title) and j < len(stream):
            nxt = stream[j][1]
            if not nxt:
                j += 1
                continue
            if not title.startswith(got + _norm(nxt)):
                break
            got, j = got + _norm(nxt), j + 1
        if got == title:
            return k, j, ""
    raise ValueError(f"heading {sec['id']} ({sec['title']}) not found from p. {sec['page']}")


# ---------------------------------------------------------------------------
# the body
# ---------------------------------------------------------------------------

def _caption_line(ln: str, kind: str, number: str) -> bool:
    return bool(re.match(rf"^{kind}\s+{re.escape(number)}(?!\d|[.-]\d)\s*(?:\(Continued\))?\s*[.:]?",
                         ln)) and not re.match(rf"^{kind}\s+{re.escape(number)}\s*\)", ln)


def render(stream, a: int, b: int, pages, figure_pages: set, caption_pages: set,
           figures: list[dict], log: list) -> str:
    """The printed text of stream[a:b] as paragraphs with ``[p. B-3]``
    markers. See the module docstring for the rules."""
    paras, cur, last_page = [], [], None
    page_of_para = []

    def flush():
        if cur:
            paras.append(cur[:])
            cur.clear()

    k = a
    prev_whole = False  # whether the page before was typed or a figure page
    while k < b:
        n, ln, typed = stream[k]
        label = pages[n]["label"]
        if n != last_page:
            last_page = n
            whole = typed or label in figure_pages
            if whole or prev_whole:
                flush()
            prev_whole = whole
            cur.append(f"[p. {label}]")
        if label in figure_pages and not typed:
            # only the caption lines (a figure's first page or its
            # "(Continued)" pages): from a caption start to a blank line
            if any(_caption_line(ln, "Figure", f["number"]) for f in figures):
                flush()
                while k < b and stream[k][0] == n and stream[k][1]:
                    cur.append(stream[k][1])
                    k += 1
                flush()
                continue
            if ln:
                if log and log[-1][:2] == ("figure lettering left out", label):
                    log[-1] = (log[-1][0], label, log[-1][2] + " / " + ln)
                else:
                    log.append(("figure lettering left out", label, ln))
            k += 1
            continue
        if typed:
            if not ln:
                flush()
            else:
                cur.append(ln if not cur or cur[-1].startswith("[p. ")
                           else "\n" + ln)
            k += 1
            continue
        if _is_short(ln):
            j = k
            while j < b and stream[j][0] == n and not stream[j][2] \
                    and (_is_short(stream[j][1]) or not stream[j][1]):
                j += 1
            run = [stream[t][1] for t in range(k, j) if stream[t][1]]
            if len(run) >= 4:
                if label in caption_pages:
                    log.append(("glyph run left out (figure page)", label, " ".join(run)))
                else:
                    joined = " ".join(run)
                    cur.append(joined)
                    log.append(("glyph run kept", label, joined))
                k = j
                continue
        if not ln:
            flush()
            k += 1
            continue
        if (cur and re.search(r"\w-$", cur[-1]) and re.match(r"[a-z0-9]", ln)
                and not cur[-1].startswith("[p. ")):
            # a word the print hyphenates at the end of a line
            # ("live-" / "dead load", "non-" / "redundant", "Figure B-" / "2")
            cur[-1] += ln
        else:
            cur.append(ln)
        k += 1
    flush()
    out = []
    for p in paras:
        text = " ".join(p).replace(" \n", "\n")
        text = re.sub(r"[ \t]+", " ", text).strip()
        text = re.sub(r" *\n *", "\n", text)
        out.append(text)
    return "\n\n".join(x for x in out if x)


def drop_lettering(body: str, caption_pages: set, figures: list[dict],
                   typed_pages: set, log: list) -> str:
    """Leave out a figure's lettering on a text-layer page that prints a
    figure caption: a paragraph under 60 characters with no sentence in it,
    and what a caption paragraph prints after the listed caption."""
    caps = {f["number"]: f for f in figures}
    out, page = [], None
    for p in body.split("\n\n"):
        for m in re.finditer(r"\[p\. ([^\]]+)\]", p):
            page = m.group(1)
        text = re.sub(r"\[p\. [^\]]+\]", "", p).strip()
        markers = " ".join(re.findall(r"\[p\. [^\]]+\]", p))
        if page in typed_pages or page not in caption_pages:
            out.append(p)
            continue
        m = re.match(r"^Figure\s+([A-E](?:\.\d+)?-\d+)\s*(?:\(Continued\))?\s*[.:]?\s*", text)
        if m and m.group(1) in caps:
            cap = _norm(caps[m.group(1)]["caption"])
            tail = cap[-12:]
            cut = None
            for w in re.finditer(r"\S+", text[m.end():]):
                if _norm(text[m.end():m.end() + w.end()]).endswith(tail):
                    cut = m.end() + w.end()
                    break
            if cut is not None and text[cut:].strip():
                log.append(("lettering after caption left out", page, text[cut:].strip()))
                p = (markers + " " if markers else "") + text[:cut]
            out.append(p)
            continue
        if (text and len(text) < 60 and not re.search(r"[.:;]\s*$", text)
                and not text.startswith(("Figure", "Table", "["))
                and "[Eq. " not in text):
            log.append(("lettering left out", page, text))
            if markers:
                out.append(markers)
            continue
        out.append(p)
    return "\n\n".join(out)


def _merge_markers(body: str) -> str:
    """A paragraph that is only a page marker joins the next paragraph."""
    paras = body.split("\n\n")
    out, hold = [], ""
    for p in paras:
        if re.fullmatch(r"(?:\[p\. [^\]]+\]\s*)+", p.strip()):
            hold = (hold + " " + p.strip()).strip()
            continue
        if hold:
            p = hold + " " + p if not p.startswith("[p. ") else hold + " " + p
            hold = ""
        out.append(p)
    if hold:
        out.append(hold)
    return "\n\n".join(out)


def _introduced_by(before: str, num: str, label: str | None) -> str:
    """'Equation B-3g, introduced by: "The reciprocal of Eq. B-3f yields:"
    (p. B-10).': the last sentence of the paragraph before the one that
    holds the equation (the equation's own line starts that paragraph)."""
    paras = [p for p in before.split("\n\n")]
    prev = paras[-2] if len(paras) > 1 else ""
    words = _clean_ws(re.sub(r"\[[^\]]*\]", " ", prev))
    # sentence ends that are not an abbreviation ("Eq. B-3f", "e.g. lateral")
    ends = [m.end() for m in re.finditer(
        r"(?<!\bEq)(?<!\bEqs)(?<!\bFig)(?<!\bNo)(?<!e\.g)(?<!i\.e)[.!?]\s+(?=[A-Z“(•])", words)]
    tail = words[ends[-1]:] if ends else words
    tail = tail[-200:].strip()
    where = f" (p. {label})" if label else ""
    if len(tail) < 12:
        return f"Equation {num} as printed{where}."
    return f"Equation {num}, introduced by: \"{tail}\"{where}."


def _listed(items: list[dict], kind: str, text: str) -> list[str]:
    """The figures or tables of ``items`` whose caption is printed in
    ``text``: a paragraph or line that starts with the number and goes on
    with the listed caption ("Figure A.2-5 (Continued). Field log ...",
    "Table A.6-2 Summary of ..."), not a sentence that cites it."""
    out = []
    for it in items:
        cap = _norm(it["caption"])[:12]
        for m in re.finditer(rf"(?:^|\n|\] ){kind}\s+{re.escape(it['number'])}(?!\d|[.-]\d)"
                             r"\s*(?:\(Continued\))?\s*[.:]?\s*", text):
            if _norm(text[m.end():m.end() + 60]).startswith(cap):
                # a table printed with no caption is listed by its number
                out.append(f"{kind} {it['number']}: {it['caption']}".rstrip(": "))
                break
    return out


# ---------------------------------------------------------------------------
# one appendix
# ---------------------------------------------------------------------------

def build_appendix(vol: dict, app: dict, manifest_dir: Path, log: list,
                   strict: bool = True) -> dict:
    pdf = (manifest_dir / vol["pdf_path"]).resolve()
    pages = read_appendix_pages(pdf, app["page_start"], app["page_end"])
    typed = (read_typed_pages(manifest_dir / app["typed_pages"])
             if app.get("typed_pages") else {})
    labels = {p["label"] for p in pages}
    unknown = sorted(set(typed) - labels)
    if unknown:
        raise ValueError(f"Appendix {app['letter']}: typed pages not in its range: {unknown}")
    figures = app.get("figures", [])
    tables = app.get("tables", [])
    figure_pages = set(app.get("figure_pages", []))
    caption_pages = {f["page"] for f in figures}
    stream = make_stream(pages, typed)

    secs = app["sections"]
    heads, cursor = [], 0
    for sec in secs:
        k0, k1, extra = locate_heading(stream, pages, sec, cursor)
        start = k0
        if sec.get("start_page"):
            n0 = _page_pos(pages, sec["start_page"])
            start = next(k for k, it in enumerate(stream) if it[0] == n0)
        heads.append((sec, start, k0, k1, extra))
        cursor = k1
    printed_eqs = app.get("printed_equations", [])
    fixes = app.get("fixes", [])
    fixes_applied: set = set()
    own_fixes: set = set()
    attached: set = set()
    sections = []
    for i, (sec, start, k0, k1, extra) in enumerate(heads):
        end = heads[i + 1][1] if i + 1 < len(heads) else len(stream)
        sub = []
        local_log: list = []
        body = ""
        if start < k0:
            body = render(stream, start, k0, pages, figure_pages, caption_pages,
                          figures, local_log)
        rest = render(stream, k1, end, pages, figure_pages, caption_pages,
                      figures, local_log)
        if extra:
            # the words printed after the title on the heading line
            m = re.match(r"^((?:\[p\. [^\]]+\]\s*)*)", rest)
            lead = m.group(1)
            rest = (f"{lead}{extra}\n\n{rest[m.end():]}" if lead
                    else f"{extra}\n\n{rest}")
        if not rest.startswith("[p. "):
            rest = f"[p. {pages[stream[k0][0]]['label']}] " + rest
        body = "\n\n".join(x for x in (body, rest) if x)
        body = drop_lettering(body, caption_pages, figures, set(typed), local_log)
        body = _merge_markers(body)
        body = fix_printed_equations(body, printed_eqs, fixes_applied)
        for n_f, f in enumerate(fixes):
            if f["find"] in body:
                body = body.replace(f["find"], f["replace"], 1)
                own_fixes.add(n_f)
        body = _merge_markers(body).strip()
        for kind, label, text in local_log:
            log.append((app["letter"], sec["id"], kind, label, text))
            if kind == "glyph run kept" and text in body and strict:
                raise ValueError(
                    f"Appendix {app['letter']} p. {label}: glyph run left in the "
                    f"text of {sec['id']}, mend it with a fix or type the page: {text[:80]}")
        labels_in = [pages[stream[q][0]]["label"] for q in range(start, end)]
        page_from, page_to = labels_in[0], labels_in[-1]
        pages_txt = (f"p. {page_from}" if page_from == page_to
                     else f"pp. {page_from} to {page_to}")
        text_only = re.sub(r"\[p\. [^\]]*\]", "", body).strip()
        if sec["id"] == app["letter"] and len(text_only) < 20:
            continue
        if not text_only:
            # a heading followed straight by the next one, as in the chapters
            body = ""
        eq_list, seen = [], set()
        for m in re.finditer(r"\[Eq\. ([^\]]+)\]", body):
            num = m.group(1)
            if num in seen:
                continue
            seen.add(num)
            before = body[:m.start()]
            pm = list(re.finditer(r"\[p\. ([^\]]+)\]", before))
            eq_list.append({"id": f"Eq. {num}",
                            "description": _introduced_by(before, num,
                                                          pm[-1].group(1) if pm else None),
                            "implemented_in": None})
        record = {
            "section_id": sec["id"],
            "title": title_case(sec["title"]),
            "body": body,
            "key_points": [],
            "equations": add_printed_equations(body, eq_list, printed_eqs, attached),
            "figures": _listed(figures, "Figure", body),
            "tables": _listed(tables, "Table", body),
            "applicability": (f"{vol['volume_id']}, Appendix {app['letter']} "
                              f"({title_case(app['title'])}), printed {pages_txt}."),
        }
        for part in split_long(record):
            part["figures"] = _listed(figures, "Figure", part["body"])
            part["tables"] = _listed(tables, "Table", part["body"])
            sections.append(part)
    problems = []
    for e in printed_eqs:
        fx = e.get("fix") or []
        for k in range(len([fx] if isinstance(fx, dict) else fx)):
            if (e["number"], k) not in fixes_applied:
                problems.append(f"Eq. {e['number']}: fix {k} found no text to mend")
        if e.get("formula") and e["number"] not in attached:
            problems.append(f"Eq. {e['number']}: no section marks it")
    for n_f, f in enumerate(fixes):
        if n_f not in own_fixes:
            problems.append(f"fix {n_f} found no text to mend: {f['find'][:60]}")
    listed_f = {x.split(":")[0] for s in sections for x in s["figures"]}
    listed_t = {x.split(":")[0] for s in sections for x in s["tables"]}
    for f in figures:
        if f"Figure {f['number']}" not in listed_f:
            problems.append(f"Figure {f['number']}: no section prints its caption")
    for t in tables:
        if f"Table {t['number']}" not in listed_t:
            problems.append(f"Table {t['number']}: no section prints its caption")
    ids = [s["section_id"] for s in sections]
    if len(ids) != len(set(ids)):
        problems.append("section ids repeated: " + ", ".join(
            sorted({x for x in ids if ids.count(x) > 1})))
    if problems and strict:
        raise ValueError(f"Appendix {app['letter']}: " + "; ".join(problems))
    for p in problems:
        log.append((app["letter"], "-", "PROBLEM", "-", p))
    return {
        "reference_id": vol["volume_id"],
        "reference_title": vol.get("volume_title", ""),
        "volume": vol["volume"],
        "chapter": app["number"],
        "chapter_title": f"Appendix {app['letter']}: {title_case(app['title'])}",
        "sections": sections,
    }


def build_appendices(package: str, only: set | None = None,
                     log: list | None = None, strict: bool = True) -> dict[str, dict]:
    """``{file name: appendix dict}`` for every appendix of the manifest,
    built without writing anything; the check that a rebuild reproduces the
    committed files."""
    mf = SCRIPTS / "manifests" / f"{package}.json"
    manifest = json.loads(mf.read_text(encoding="utf-8"))
    out = {}
    log = [] if log is None else log
    for vol in manifest["volumes"]:
        for app in vol.get("appendices", []):
            if only and app["letter"] not in only:
                continue
            out[app["file"]] = build_appendix(vol, app, mf.parent, log, strict)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("package")
    ap.add_argument("--only", nargs="*", help="appendix letters to build")
    ap.add_argument("--report", action="store_true",
                    help="list what was left out as figure lettering or kept as glyph runs")
    ap.add_argument("--draft", metavar="DIR",
                    help="write to DIR without stopping on unmended glyph runs or "
                         "unused fixes (they are listed), to see what needs mending")
    args = ap.parse_args(argv)
    log: list = []
    built = build_appendices(args.package, set(args.only or []) or None, log,
                             strict=not args.draft)
    text_dir = Path(args.draft) if args.draft else PKG / args.package / "text"
    text_dir.mkdir(parents=True, exist_ok=True)
    for name, data in built.items():
        (text_dir / name).write_text(chapter_json(data), encoding="utf-8")
        sizes = [len(json.dumps(s, ensure_ascii=False)) for s in data["sections"]]
        print(f"[{args.package}] {name}: {len(data['sections'])} sections, "
              f"largest {max(sizes)} characters as JSON")
    if args.report or args.draft:
        for letter, sid, kind, label, text in log:
            print(f"  {letter} {sid} p. {label}: {kind}: {text[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
