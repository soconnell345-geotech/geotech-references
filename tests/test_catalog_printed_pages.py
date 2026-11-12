"""Every figure-catalog row stores the page number its page prints.

A helper quotes a row's ``printed_page`` in its citations, so a wrong one
sends an engineer to the wrong page of the manual. The 2026-11-12 audit
found edition years stored as pages (GEC-5, GEC-10, GEC-11), DM 7.2's
Appendix B three low, the micropile manual's labels cut to the number
after the dash, and 1,328 rows with none; all were set from the print.

The page's label is read from its text layer: the tokens shaped like a
page label ("112", "4-12", "A-3", "A2-14", "B3") in the lines of the top
or bottom 11 % of the page, or of its outer side strips for a page printed
turned, a line holding only the label ranked first. A row whose label that
reading does not give first (scanned pages with no text layer, labels
drawn as outlines, turned pages whose footer text is out of order) is in
READ_FROM_RENDER, with the label seen on a render of its page.
Skips a catalog whose PDFs are not checked out, or without PyMuPDF.
"""
import json
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references"
CATALOGS = sorted(d.name for d in PKG.iterdir()
                  if (d / "figures_catalog.json").is_file())

# (figure_number, pdf_page_index): the label seen on a render of the page
READ_FROM_RENDER = {
    "aashto_1993": {
        ("4.1", 76): "I-55", ("4.2", 79): "I-58", ("4.3", 80): "I-59",
        ("4.4", 82): "I-61", ("4.5", 85): "I-64", ("2.1", 97): "II-8",
        ("2.2", 100): "II-11", ("2.3", 103): "II-14", ("2.4", 104): "II-15",
        ("2.5", 107): "II-18", ("2.6", 108): "II-19", ("2.7", 110): "II-21",
        ("2.8", 112): "II-23", ("2.9", 113): "II-24", ("3.1", 121): "II-32",
        ("3.2", 125): "II-36", ("3.3", 128): "II-39", ("3.4", 129): "II-40",
        ("3.5", 130): "II-41", ("3.6", 131): "II-42", ("3.7", 134): "II-45",
        ("3.7-2", 135): "II-46", ("D.1", 380): "D-21", ("G.2", 396): "G-3",
        ("G.3", 397): "G-4", ("G.4", 400): "G-7", ("G.6", 402): "G-9",
        ("G.7", 403): "G-10", ("G.8", 404): "G-11",
    },
    "fhwa_soils_foundations": {
        ("6-11b", 368): "6-19", ("11-4", 357): "11-10",
    },
    "gec_11": {
        ("5-2", 230): "5-5",
    },
    "gec_12": {
        ("D-78", 190): 157,
    },
    "gec_14": {
        ("A-1", 45): "A1", ("A-2", 46): "A2", ("A-3", 47): "A3",
    },
    "gec_8": {
        ("5.1", 89): 67,
    },
    "micropile": {
        ("6-36", 233): "6-56",
    },
    "ufc_expansive": {
        ("1-1", 12): "1-3", ("1-4", 15): "1-6", ("2-1", 18): "2-3",
        ("4-1", 31): "4-2", ("4-2", 33): "4-4", ("5-2", 38): "5-4",
        ("5-3", 40): "5-6", ("6-2", 46): "6-5", ("6-3", 46): "6-5",
        ("6-6", 49): "6-8", ("6-7", 49): "6-8", ("6-8", 50): "6-9",
        ("6-9", 51): "6-10", ("6-10", 55): "6-14", ("6-12", 58): "6-17",
        ("6-13", 59): "6-18", ("7-2", 63): "7-4", ("7-3", 64): "7-5",
        ("B-1", 76): "B-3", ("B-2", 77): "B-4", ("B-3", 78): "B-5",
        ("B-5", 82): "B-9", ("C-1", 83): "C-1", ("C-2", 84): "C-2",
        ("C-3", 85): "C-3", ("C-4", 87): "C-5", ("C-5", 88): "C-6",
        ("C-7", 90): "C-8", ("C-8", 91): "C-9", ("C-9", 92): "C-10",
        ("C-10", 93): "C-11",
    },
}

_DASHES = "–—‒‑‐−"
_TOKEN = re.compile(
    r"^(?:\d{1,4}"                               # 112
    r"|\d{1,2}-\d{1,3}"                          # 4-12
    r"|[A-Z]{1,2}(?:\.?\d{1,2})?-\d{1,3}"        # A-3, A2-14, I-55
    r"|[A-Z]\d{1,3}"                             # B3
    r"|[ivxlc]{1,7})$")                          # front matter


def _catalog(ref):
    return json.loads((PKG / ref / "figures_catalog.json").read_text(
        encoding="utf-8"))


def _norm(label):
    s = str(label).strip()
    for d in _DASHES:
        s = s.replace(d, "-")
    s = re.sub(r"\s*-\s*", "-", s)
    return re.sub(r"^(?:page|p\.)\s*", "", s, flags=re.I)


def _is_year(tok):
    return tok.isdigit() and len(tok) == 4 and 1950 <= int(tok) <= 2035


def _page_label(pymupdf, page, zone=0.11):
    """The label the page prints, as read from its text layer, or None."""
    frames = [(page.rect, pymupdf.Identity)]
    if page.rotation:
        frames.append(((page.rect * page.rotation_matrix).normalize(),
                       page.rotation_matrix))
        frames.append((page.mediabox, pymupdf.Identity))
    found = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            in_band = side = False
            for r, m in frames:
                x0, y0, x1, y1 = (pymupdf.Rect(line["bbox"]) * m).normalize()
                in_band |= (y1 < r.y0 + zone * r.height
                            or y0 > r.y1 - zone * r.height)
                side |= (x1 < r.x0 + 0.09 * r.width
                         or x0 > r.x1 - 0.09 * r.width)
            if not (in_band or side):
                continue
            toks = _norm("".join(s["text"] for s in line["spans"])).split()
            for k, tok in enumerate(toks):
                tok = tok.strip(",;:()[]")
                if not tok or _is_year(tok) or not _TOKEN.match(tok):
                    continue
                score = ((2 if len(toks) == 1 else 1 if k in (0, len(toks) - 1)
                          else 0) + (1 if in_band else 0))
                found.append((score, len(found), tok))
    return min(found, key=lambda f: (-f[0], f[1]))[2] if found else None


def _pdf(rel):
    docs = os.environ.get("GEOTECH_REFERENCES_DOCS")
    if docs and (Path(docs) / Path(rel).name).is_file():
        return Path(docs) / Path(rel).name
    return ROOT / rel


@pytest.mark.parametrize("ref", CATALOGS)
def test_every_row_stores_a_printed_page_and_no_year(ref):
    for row in _catalog(ref)["figures"]:
        page = row.get("printed_page")
        assert page is not None, (ref, row["figure_number"])
        assert not _is_year(str(page)), (ref, row["figure_number"], page)


def test_the_render_table_names_rows_that_exist():
    for ref, rows in READ_FROM_RENDER.items():
        have = {(r["figure_number"], r["pdf_page_index"]): r["printed_page"]
                for r in _catalog(ref)["figures"]}
        for key, printed in rows.items():
            assert have.get(key, "missing") == printed, (ref, key)


@pytest.mark.parametrize("ref", CATALOGS)
def test_each_row_page_prints_its_printed_page(ref):
    pymupdf = pytest.importorskip("pymupdf")
    cat = _catalog(ref)
    rendered = READ_FROM_RENDER.get(ref, {})
    docs, labels, wrong = {}, {}, []
    try:
        for row in cat["figures"]:
            key = (row["figure_number"], row["pdf_page_index"])
            if key in rendered:
                continue
            rel = row.get("pdf_path") or cat["pdf_path"]
            if rel not in docs:
                path = _pdf(rel)
                if not path.is_file():
                    pytest.skip(f"{rel} not checked out")
                docs[rel] = pymupdf.open(str(path))
            at = (rel, row["pdf_page_index"])
            if at not in labels:
                labels[at] = _page_label(pymupdf, docs[rel][row["pdf_page_index"]])
            if _norm(row["printed_page"]) != labels[at]:
                wrong.append((*key, row["printed_page"], labels[at]))
    finally:
        for d in docs.values():
            d.close()
    assert not wrong, f"{ref}: (figure, index, stored, page prints) {wrong}"
