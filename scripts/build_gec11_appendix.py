"""Build GEC-11's appendices from their printed pages (no API; BACKLOG REF-85).

The appendices of Volume II (FHWA-NHI-10-025, November 2009) are read as
``build_gec11_text.py`` reads the chapters (its ``read_pages``: the running
footer taken off, Symbol-font letters put back, lines broken at a word's own
hyphen joined), but they are laid out more loosely than the chapters, so
this script keeps every line of the page and takes all structure from the
manifest's ``appendices`` (in the Volume II entry of
``scripts/manifests/gec_11.json``), each with:

* ``letter``, ``number`` (the ``chapter`` the file carries: the appendices
  follow chapter 11, A = 12 ... F = 17), ``title`` (as printed, in title
  case), ``page_start`` and ``page_end`` (1-based PDF pages);
* ``fix_lines`` (as the chapters', see ``build_gec11_text.apply_fix_lines``):
  every formula line, table and figure caption is typed in here from a
  rendered page: a formula line as printed, with ``[Eq. B-1]`` where the
  page numbers it; a table as ``[Table B-1, typed in from p. B-14, row by
  row:]`` and its rows, one to a line (``\\n``), cells parted by " | "; a
  caption as one line, "Figure B-1. ..." (a caption paragraph lists the
  figure or table under its section); a figure's lettering, where it says
  something the text does not, as ``[Figure B-1 lettering, typed in from
  p. B-4:] ...``;
* ``sections``: each printed heading under the appendix's own (``sid``,
  ``title`` as printed, in title case, ``pdf_page`` and the heading's
  ``find`` and optional ``through`` lines, which are taken out); the text
  before the first is the section numbered with the letter alone;
* ``printed_equations``: the equations the appendix numbers (and those it
  prints again from a chapter, with a note), as the chapters'.

Each body is the page's lines, a paragraph wherever the text layer leaves
a blank line, with ``[p. B-3]`` where each printed page starts. Nothing is
summarised: ``key_points`` is empty. A section over the reference tools'
size is split into lettered parts (``build_printed_text.split_long``).

Usage::

    python scripts/build_gec11_appendix.py              # every appendix
    python scripts/build_gec11_appendix.py --appendix B
    python scripts/build_gec11_appendix.py --appendix B --dry-run

Writes ``geotech_references/gec_11/text/appendix_b.json`` and so on.
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

import build_gec11_text as gt  # noqa: E402

bpt = gt.bpt
MANIFEST = SCRIPTS / "manifests" / f"{gt.PACKAGE}.json"
TEXT_DIR = gt.PKG / gt.PACKAGE / "text"

#: A caption paragraph: "Figure B-1. ...", "Table E1-3. ...", "Figure D.2-1. ...".
_CAPTION = re.compile(r"^(?:\[p\. [^\]]+\]\s*)?(Figure|Table)\s+([A-F][\d.]*-\d+[a-z]?)\.\s+(.+)$")
#: A line that starts a list item, a step or a note, which keeps its own
#: line in the paragraph ("1.  Determine index ...", "a.  Wide width ...",
#: "iv.  The temperature ...", "• Using ...", "Step 4:", "Note: ...").
_ITEM = re.compile(r"^(?:[•▪]\s|\d{1,2}\.\s|[a-h]\.\s|[ivx]{1,4}\.\s|Step \d{1,2}[.:]|Note:)")
_MARK = re.compile(r"\[p\. [^\]]+\]")


#: The end of a paragraph's last line that ends it at a page break: a
#: sentence's stop, a colon, a closing bracket of a typed-in note.
_ENDS = re.compile(r"[.:;?!\]]\)?[\"”’]?$")


def _paragraphs(stream, pages) -> str:
    """The lines of ``stream`` ((page index, line) pairs) as paragraphs, a
    ``[p. N]`` marker where each printed page's text starts. Blank lines
    part paragraphs on a page; across a page break the paragraph goes on
    unless the text before it ends a sentence, or is a caption, a typed
    table or a note in brackets."""
    paras, cur = [], []
    last_page, gap = None, False
    row = gt._ROW

    def flush():
        if cur:
            paras.append(bpt._clean_ws(" ".join(cur)).strip(row + " "))
            cur.clear()

    def block_ends():
        # a caption, a typed table or a note in brackets ends at a page
        # break, and so does a sentence
        first = next((c for c in cur if not _MARK.fullmatch(c)), "")
        return (first.startswith("[") or bool(_CAPTION.match(first))
                or bool(_ENDS.search(cur[-1])))

    for i, ln in stream:
        if not ln.strip():
            gap = True
            continue
        mark = None
        if i != last_page:
            last_page = i
            if pages[i]["label"]:
                mark = f"[p. {pages[i]['label']}]"
            if cur and block_ends():
                flush()
        elif gap:
            flush()
        gap = False
        # a replacement line that starts with a line break ("\nRFD = ...",
        # a list going on over a page) keeps it before the page marker
        if ln.startswith(row):
            ln = ln.lstrip(row)
            if cur:
                cur.append(row)
        elif _CAPTION.match(ln) and cur:
            # a caption is a paragraph of its own
            flush()
        elif _ITEM.match(ln) and cur:
            cur.append(row)
        if mark:
            cur.append(mark)
        cur.append(ln)
    flush()
    body = "\n\n".join(paras)
    return re.sub(rf"[ \t]*{gt._ROW}[ \t]*", "\n", body)


def _listed(body: str, kind: str) -> list[str]:
    out = []
    for para in body.split("\n\n"):
        m = _CAPTION.match(para.split("\n")[0])
        if m and m.group(1) == kind:
            out.append(f"{kind} {m.group(2)}: {m.group(3).rstrip('.')}")
    return out


def _split(sec: dict) -> list[dict]:
    """``build_printed_text.split_long``, each part listing the figures and
    tables whose captions it holds (the lettered appendix numbers are not
    the chapters' form)."""
    parts = bpt.split_long(sec)
    if len(parts) > 1:
        for p in parts:
            p["figures"] = _listed(p["body"], "Figure")
            p["tables"] = _listed(p["body"], "Table")
    return parts


def build_appendix(app: dict, vol: dict, pages: list[dict]) -> dict:
    letter = app["letter"]
    first, last = app["page_start"], app["page_end"]
    stream = [(i, ln) for i in range(first - 1, last) for ln in pages[i]["lines"]]
    # each heading: the stream position of its "find" line on its page,
    # its lines taken out
    starts = [(0, {"sid": letter, "title": app["title"], "note": app.get("note")})]
    for s in app.get("sections", []):
        idx = s["pdf_page"] - 1
        hits = [q for q, (i, ln) in enumerate(stream) if i == idx and ln == s["find"]]
        if not hits:
            raise ValueError(f"Appendix {letter}: heading {s['sid']} ({s['find']!r}) "
                             f"not on PDF page {s['pdf_page']}")
        q = hits[0]
        end = q
        if s.get("through"):
            later = [r for r in range(q, len(stream))
                     if stream[r][0] == idx and stream[r][1] == s["through"]]
            if not later:
                raise ValueError(f"Appendix {letter}: {s['through']!r} not after "
                                 f"{s['find']!r} on PDF page {s['pdf_page']}")
            end = later[0]
        for r in range(q, end + 1):
            stream[r] = (stream[r][0], "")
        starts.append((q, s))
    if [q for q, _ in starts] != sorted(q for q, _ in starts):
        raise ValueError(f"Appendix {letter}: headings out of printed order")
    starts.append((len(stream), None))

    printed_eqs = app.get("printed_equations", [])
    attached: set = set()
    sections = []
    vol_name = "I" if vol["volume"] == 1 else "II"
    for (s, head), (t, _) in zip(starts, starts[1:]):
        body = _paragraphs(stream[s:t], pages)
        # a heading with no text before the next (B.4, then B.4.1) is on
        # its heading's page
        labels = (re.findall(r"\[p\. ([^\]]+)\]", body)
                  or [pages[head.get("pdf_page", first) - 1]["label"]])
        if head["sid"] == letter and not re.sub(r"\[[^\]]*\]", "", body).strip():
            continue
        pages_txt = (f"p. {labels[0]}" if len(set(labels)) == 1
                     else f"pp. {labels[0]} to {labels[-1]}")
        where = (f"{vol['volume_id']} (Volume {vol_name}), Appendix {letter} "
                 f"({app['title']}), printed {pages_txt}.")
        if head.get("note"):
            where += " " + head["note"]
        sec = {
            "section_id": head["sid"],
            "title": head["title"],
            "body": body,
            "key_points": [],
            "equations": bpt.add_printed_equations(body, [], printed_eqs, attached),
            "figures": _listed(body, "Figure"),
            "tables": _listed(body, "Table"),
            "applicability": where,
        }
        sections.extend(_split(sec))
    missing = [e["number"] for e in printed_eqs if e["number"] not in attached]
    if missing:
        raise ValueError(f"Appendix {letter}: no section marks Eq. {', '.join(missing)}")
    return {
        "reference_id": vol["volume_id"],
        "reference_title": vol.get("volume_title", ""),
        "volume": vol["volume"],
        "chapter": app["number"],
        "chapter_title": f"Appendix {letter}: {app['title']}",
        "sections": sections,
    }


def build_appendices(only: set[str] | None = None) -> dict:
    """Every appendix in the manifest (letter -> file dict), built without
    writing anything; the check that a rebuild reproduces the committed
    files."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out = {}
    for vol in manifest["volumes"]:
        apps = [a for a in vol.get("appendices", [])
                if not only or a["letter"] in only]
        if not apps:
            continue
        pdf = (MANIFEST.parent / vol["pdf_path"]).resolve()
        wanted = set()
        for a in apps:
            wanted |= set(range(a["page_start"], a["page_end"] + 1))
        pages = gt.read_pages(pdf, only=range(min(wanted), max(wanted) + 1))
        for a in apps:
            gt.apply_fix_lines(pages, a.get("fix_lines", []), pad=False)
            out[a["letter"]] = build_appendix(a, vol, pages)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--appendix", action="append", type=str.upper)
    ap.add_argument("--dry-run", action="store_true",
                    help="build and report without writing the files")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args(argv)
    only = set(args.appendix) if args.appendix else None
    for letter, data in sorted(build_appendices(only).items()):
        if not args.dry_run:
            (TEXT_DIR / f"appendix_{letter.lower()}.json").write_text(
                bpt.chapter_json(data), encoding="utf-8")
        sizes = [len(json.dumps(s, ensure_ascii=False)) for s in data["sections"]]
        print(f"[{gt.PACKAGE}] appendix {letter}: {len(data['sections'])} sections, "
              f"largest {max(sizes) if sizes else 0} chars as JSON")
        if args.report:
            for s in data["sections"]:
                print(f"   {s['section_id']:10s} {len(s['body']):6d}  {s['title'][:60]}"
                      f"  eqs={[e['id'][4:] for e in s['equations']]}"
                      f"  figs={[f.split(':')[0] for f in s['figures']]}"
                      f"  tabs={[t.split(':')[0] for t in s['tables']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
