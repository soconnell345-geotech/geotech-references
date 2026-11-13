"""Table catalog rows lead to their table, and say truly where its values are
(REF-86, REF-34; built by scripts/build_table_catalog.py).

* Row counts per reference are pinned, so a re-run of the builder that loses
  or adds rows fails here.
* Every row's page prints the table: its label ("Table 5-3") and the first
  words of its caption, read off the page's text layer with PyMuPDF (the
  test skips without it or the PDF), and the page is not a contents page or
  List of Tables. The rule is the builder's own (``row_on_page``), which
  reads an OCR text layer's look-alike letters for the scans that have one.
  A table printed as a picture, or whose page's text layer lost its label or
  caption, has no such text: those rows were checked on the rendered page
  and are listed in RENDER_CHECKED. The list is strict, so a row that moves
  to a page without its label fails, and so does a listed row whose page
  now prints it.
* Every ``values_in`` resolves: a "text" row's section exists (and its
  ``tables`` entry or body names the table), a "lookup" row's
  ``module.function`` is a function of the reference.
* ``values`` never promises cells that are not there: a "text" row's
  section types the numbers, row labels and words its page prints (the
  builder's ``cell_coverage``), unless read against the render; a "lookup"
  row names the function that returns the values, not one that lists the
  table's keys or returns a footnote.
* Every table a stored section lists (its ``tables`` field) is a row,
  except the entries in LISTED_NOT_PRINTED, each a number the manual cites
  and does not print (searched for in the PDF).

PDFs not in this checkout's ``docs/`` are looked for in the folder
``GEOTECH_REFERENCES_DOCS`` names.
"""

import importlib
import json
import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references"
CATALOGS = sorted(d.name for d in PKG.iterdir()
                  if (d / "tables_catalog.json").is_file())

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
import build_table_catalog as builder  # noqa: E402

#: Rows per reference (scripts/build_table_catalog.py, 2026-11-12).
ROW_COUNTS = {
    "aashto_1993": 29, "california_trenching": 39, "dm7_1": 139,
    "dm7_2": 172, "em_1905": 109, "em_2104": 27, "em_2107": 38,
    "eurocode_7_1": 20, "eurocode_7_2": 38, "fema_p2082": 52,
    "fhwa_pavements": 153,
    "fhwa_soils_foundations": 142, "gec_10": 47, "gec_11": 118,
    "gec_12": 262, "gec_13": 82, "gec_4": 23, "gec_5": 127, "gec_6": 50,
    "gec_7": 66, "gec_8": 15, "gec_9": 24, "gsa_collapse": 30,
    "micropile": 37, "ufc_collapse": 29, "ufc_concrete_practice": 16,
    "ufc_flexible_practice": 39, "ufc_pavement": 28, "ufc_stabilization": 10,
    "ufc_structural": 14, "wood_handbook": 124,
}

#: (reference, table number, pdf_page_index) of rows whose page's text layer
#: does not give the label and the caption's first words; each was checked
#: on the rendered page (2026-11-12).
RENDER_CHECKED = {
    # the AASHTO Guide (1993) is a scan with no text layer
    ("aashto_1993", "4.1", 83), ("aashto_1993", "2.2", 98),
    ("aashto_1993", "2.3", 109), ("aashto_1993", "2.4", 114),
    ("aashto_1993", "2.5", 115), ("aashto_1993", "2.6", 115),
    ("aashto_1993", "2.7", 116), ("aashto_1993", "3.1", 123),
    ("aashto_1993", "3.2", 127), ("aashto_1993", "3.3", 132),
    ("aashto_1993", "G.1", 398),
    # Tables D.1 to D.18 on pages D-3 to D-20, one a page
    *{("aashto_1993", f"D.{i}", 361 + i) for i in range(1, 19)},
    # the OCR layer reads the label as "Table Eal"
    ("eurocode_7_2", "E.1", 122),
    # the text layer drops the captions' symbols (Drd, Dm)
    ("fema_p2082", "C17.2-4", 483), ("fema_p2082", "C17.2-5", 483),
}

#: (reference, section id, table number as listed) of ``tables`` entries
#: that name a table the manual cites and does not print.
LISTED_NOT_PRINTED = {
    # ASCE 7's Table 1.5-2, which section 11.5 cites
    ("fema_p2082", "11.5", "1.5-2"),
}


def _catalog(ref):
    return json.loads((PKG / ref / "tables_catalog.json").read_text(
        encoding="utf-8"))


def _pdf(rel):
    p = ROOT / rel
    if p.exists():
        return p
    docs = os.environ.get("GEOTECH_REFERENCES_DOCS")
    if docs and (Path(docs) / Path(rel).name).exists():
        return Path(docs) / Path(rel).name
    return None


def test_row_counts_are_pinned():
    got = {ref: len(_catalog(ref)["tables"]) for ref in CATALOGS}
    assert got == ROW_COUNTS


def test_no_number_is_filed_twice_on_one_page():
    for ref in CATALOGS:
        seen = set()
        for t in _catalog(ref)["tables"]:
            key = (t.get("pdf_path"), t["table_number"], t["pdf_page_index"])
            assert key not in seen, (ref, key)
            seen.add(key)


def test_the_render_checked_rows_are_rows():
    rows = {(ref, t["table_number"], t["pdf_page_index"])
            for ref in CATALOGS for t in _catalog(ref)["tables"]}
    assert RENDER_CHECKED <= rows, sorted(RENDER_CHECKED - rows)


@pytest.mark.parametrize("ref", CATALOGS)
def test_every_row_prints_its_label_and_caption_on_its_page(ref):
    fitz = pytest.importorskip("fitz")
    cat = _catalog(ref)
    docs = {}
    missing = []
    lacks = []
    try:
        for t in cat["tables"]:
            rel = t.get("pdf_path") or cat["pdf_path"]
            if rel not in docs:
                p = _pdf(rel)
                docs[rel] = fitz.open(str(p)) if p else None
            doc = docs[rel]
            if doc is None:
                missing.append(rel)
                continue
            text = doc[t["pdf_page_index"]].get_text()
            label, caption = builder.row_on_page(ref, text, t)
            if not (label and caption) or builder.contents_page(text):
                lacks.append((ref, t["table_number"], t["pdf_page_index"]))
    finally:
        for d in docs.values():
            if d is not None:
                d.close()
    if missing and len(missing) == len(cat["tables"]):
        pytest.skip(f"{ref}: PDF not found")
    listed = {k for k in RENDER_CHECKED if k[0] == ref}
    assert set(lacks) == listed, (
        f"not on their page: {sorted(set(lacks) - listed)}; "
        f"listed but now printed: {sorted(listed - set(lacks))}")


def _walk(sections):
    for s in sections or []:
        if isinstance(s, dict):
            yield s
            yield from _walk(s.get("subsections"))


def _sections(ref):
    out = {}
    tdir = PKG / ref / "text"
    for jf in sorted(tdir.glob("*.json")) if tdir.is_dir() else []:
        data = json.loads(jf.read_text(encoding="utf-8"))
        for s in _walk(data.get("sections")):
            out.setdefault(s.get("section_id"), s)
    return out


def _key(num):
    return builder.number_key(str(num))


@pytest.mark.parametrize("ref", CATALOGS)
def test_every_values_in_resolves(ref):
    secs = _sections(ref)
    for t in _catalog(ref)["tables"]:
        num = t["table_number"]
        assert t["values"] in ("text", "lookup", "page"), (ref, num)
        if t["section_id"] is not None:
            assert t["section_id"] in secs, (ref, num, t["section_id"])
        if t["values"] == "text":
            s = secs.get(t["values_in"])
            assert s is not None, (ref, num, t["values_in"])
            wanted = {_key(num), _key(re.sub(r"(?<=\d)[a-z]$", "", num))}
            listed = any(_key(builder.table_ref_number(e) or "") in wanted
                         for e in s.get("tables") or [])
            parts = [re.escape(p) for p in re.split(r"[-.]", num)]
            in_body = re.search(r"(?i)table\s+" + r"\s*[-.–]\s*".join(parts),
                                s.get("body") or "")
            assert listed or in_body, (ref, num, t["values_in"])
        elif t["values"] == "lookup":
            assert t["values_in"] in (t.get("implemented_in") or [
                t["values_in"]]), (ref, num)
        else:
            assert t["values_in"] is None, (ref, num)
        for path in ([t["values_in"]] if t["values"] == "lookup" else []) \
                + list(t.get("implemented_in") or []):
            mod, fn = path.rsplit(".", 1)
            f = getattr(importlib.import_module(
                f"geotech_references.{ref}.{mod}"), fn)
            assert callable(f), (ref, num, path)


def _volume_cfg(ref, row):
    vols = builder._load_manifest(ref).get("volumes") or [None]
    idx = next((i for i, v in enumerate(vols)
                if v and v.get("volume") == row.get("volume")), 0)
    return builder._cfg(ref, idx)


@pytest.mark.parametrize("ref", CATALOGS)
def test_a_text_row_types_every_cell_its_page_prints(ref):
    """``values`` never promises cells that are not there: a "text" row's
    section carries the numbers, row labels and words of the table as its
    page prints them (``coverage_ok``: 90 % of the numbers and row labels,
    80 % of the words but a ruled table's column heads, six cells or more),
    or was read against the render (``text_by_render``)."""
    fitz = pytest.importorskip("fitz")
    cat = _catalog(ref)
    rows = [t for t in cat["tables"] if t["values"] == "text"]
    if not rows:
        return
    sections = builder.text_sections(ref)
    docs, short = {}, []
    try:
        for t in rows:
            num, cfg = t["table_number"], _volume_cfg(ref, t)
            if cfg.get("text_by_render", {}).get(num) == t["values_in"] \
                    or cfg.get("values", {}).get(num):
                continue
            rel = t.get("pdf_path") or cat["pdf_path"]
            if rel not in docs:
                p = _pdf(rel)
                docs[rel] = fitz.open(str(p)) if p else None
            if docs[rel] is None:
                pytest.skip(f"{rel} not found")
            secs = builder._row_sections(sections, num, t.get("volume"))
            sec = next(s for s in builder.typed_sections(cfg, num, secs)
                       if s["section_id"] == t["values_in"])
            region = builder.table_region(docs[rel], t["pages"], num,
                                          bool(cfg.get("ocr")))
            cov = builder.cell_coverage(region, builder.typed_text(sec))
            if not builder.coverage_ok(cov):
                short.append((num, t["values_in"], cov["cov"], cov["wall"]))
    finally:
        for d in docs.values():
            if d is not None:
                d.close()
    assert not short, f"{ref}: text rows short of their page's cells {short}"


@pytest.mark.parametrize("ref", CATALOGS)
def test_a_lookup_row_names_the_function_that_returns_the_values(ref):
    """Not the one that lists the table's keys or returns a footnote, where
    a function returning its values is among ``implemented_in``."""
    for t in _catalog(ref)["tables"]:
        if t["values"] != "lookup":
            continue
        values = [p for p in t["implemented_in"] if not builder._helper_function(p)]
        if values:
            assert t["values_in"] in values, (ref, t["table_number"], t["values_in"])


@pytest.mark.parametrize("ref", CATALOGS)
def test_every_listed_table_is_a_row(ref):
    rows = {_key(t["table_number"]) for t in _catalog(ref)["tables"]}
    # a listed "5-4" printed as parts 5-4a and 5-4b
    rows |= {k[:-1] for k in rows if re.search(r"\d[A-Z]$", k)}
    missing = set()
    for sid, s in _sections(ref).items():
        for e in s.get("tables") or []:
            num = builder.table_ref_number(e)
            if num and _key(num) not in rows:
                missing.add((ref, sid, _key(num)))
    allowed = {(r, s, _key(n)) for r, s, n in LISTED_NOT_PRINTED if r == ref}
    assert missing == allowed, (
        f"listed, not a row: {sorted(missing - allowed)}; "
        f"allowed but now a row: {sorted(allowed - missing)}")
