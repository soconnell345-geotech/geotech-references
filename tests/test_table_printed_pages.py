"""Every table-catalog row stores the page number its page prints.

A helper quotes a row's ``printed_page`` in its citations, so a wrong one
sends an engineer to the wrong page of the manual. The check of 2026-11-12
found 46 rows wrong, each the List of Tables' page and not the one the table
is printed on (41 of UFC 3-220-20's Appendix B tables two or three pages
low, five a page off), and 551 with none; every row's page is now read off
the page itself (``scripts/build_table_catalog.py``,
``page_label``), the rule tests/test_catalog_printed_pages.py checks the
figure catalogs by.

The page's label is read from its text layer: the tokens shaped like a page
label ("112", "4-12", "A-3", "A2-14", "B3") in the lines of the top or
bottom 11 % of the page, or of its outer side strips for a page printed
turned, a line holding only the label ranked first, never a year. A row
whose label that reading does not give (scans with no text layer, labels
the text layer does not hold) is in READ_FROM_RENDER, with the label seen
on a render of its page. Skips a catalog whose PDFs are not checked out, or
without PyMuPDF.
"""
import json
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references"
CATALOGS = sorted(d.name for d in PKG.iterdir()
                  if (d / "tables_catalog.json").is_file())

# (table_number, pdf_page_index): the label seen on a render of the page
# (2026-11-12)
READ_FROM_RENDER = {
    # a scan with no text layer
    "aashto_1993": {
        ("4.1", 83): "I-62", ("2.2", 98): "II-9", ("2.3", 109): "II-20",
        ("2.4", 114): "II-25", ("2.5", 115): "II-26", ("2.6", 115): "II-26",
        ("2.7", 116): "II-27", ("3.1", 123): "II-34", ("3.2", 127): "II-38",
        ("3.3", 132): "II-43", ("G.1", 398): "G-5",
        # Tables D.1 to D.18 on pages D-3 to D-20, one a page
        **{(f"D.{i}", 361 + i): f"D-{i + 2}" for i in range(1, 19)},
    },
    # an OCR text layer: pages printed turned, whose label it reads as "0"
    # and "1", and one whose label it does not hold
    "eurocode_7_2": {("2.1", 26): "25", ("B.1", 103): "102",
                     ("D.1", 112): "111"},
    # a cell or an equation number in the bands is read before the label
    "fema_p2082": {("12.14-1", 75): "38", ("19.3-3", 121): "84"},
    # turned pages whose footer the text layer gives after a cell, and a
    # cell read first
    "fhwa_soils_foundations": {
        ("3-4a", 125): "3-22", ("3-6", 135): "3-32", ("4-13", 226): "4-27",
        ("4-25", 242): "4-43", ("A.5-3", 438): "A.5-11"},
    # Vol III pages whose last table row, printed near the foot, is read
    # before the page number
    "gec_12": {
        ("D-6", 61): "28", ("D-9", 75): "42", ("D-29", 108): "75",
        ("D-79", 190): "157", ("D-81", 193): "160", ("D-117", 257): "224",
        ("D-118", 257): "224", ("D-122", 268): "235"},
    # Appendix B pages whose label the text layer does not hold
    "gec_8": {("B.2", 286): "B-8", ("B.3", 287): "B-9"},
}

_DASHES = "‐‑‒–—−"
_TOKEN = re.compile(
    r"^(?:\d{1,4}"                               # 112
    r"|\d{1,2}-\d{1,3}"                          # 4-12
    r"|[A-Z]{1,2}(?:\.?\d{1,2})?-\d{1,3}"        # A-3, A2-14, I-55
    r"|[A-Z]\d{1,3}"                             # B3
    r"|[ivxlc]{1,7})$")                          # front matter


def _catalog(ref):
    return json.loads((PKG / ref / "tables_catalog.json").read_text(
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
    p = ROOT / rel
    if p.is_file():
        return p
    docs = os.environ.get("GEOTECH_REFERENCES_DOCS")
    if docs and (Path(docs) / Path(rel).name).is_file():
        return Path(docs) / Path(rel).name
    return p


@pytest.mark.parametrize("ref", CATALOGS)
def test_every_row_stores_a_printed_page_and_no_year(ref):
    for row in _catalog(ref)["tables"]:
        page = row.get("printed_page")
        assert page is not None, (ref, row["table_number"])
        assert isinstance(page, str), (ref, row["table_number"], page)
        assert not _is_year(page), (ref, row["table_number"], page)


def test_the_render_table_names_rows_that_exist():
    for ref, rows in READ_FROM_RENDER.items():
        have = {(r["table_number"], r["pdf_page_index"]): r["printed_page"]
                for r in _catalog(ref)["tables"]}
        for key, printed in rows.items():
            assert have.get(key, "missing") == printed, (ref, key)


@pytest.mark.parametrize("ref", CATALOGS)
def test_each_row_page_prints_its_printed_page(ref):
    pymupdf = pytest.importorskip("pymupdf")
    cat = _catalog(ref)
    rendered = READ_FROM_RENDER.get(ref, {})
    docs, labels, wrong = {}, {}, []
    try:
        for row in cat["tables"]:
            key = (row["table_number"], row["pdf_page_index"])
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
    assert not wrong, f"{ref}: (table, index, stored, page prints) {wrong}"
