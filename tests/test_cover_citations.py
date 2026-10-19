"""The designation and date each manual is cited by must be on its cover.

BACKLOG REF-28 (2026-10-19): the ``dm7_1`` data cited DM 7.1 as "UFC
3-220-10, Soil Mechanics, 1 Feb 2022, Change 1" while the PDF in ``docs/``
is "UFS 3-220-10, 16 January 2026, Unified Facilities Supplement, Soil
Mechanics (DM 7.1)", which supersedes the 2022 UFC (its paragraph I-1).
These tests read each manual's cover page and check it against the
designation and date the library cites it by:

* the ``reference_id`` of the package's manifest, figure catalog and chapter
  text files, and the citation in ``agents/references_agent.py``;
* every "<designation>, <title>, <date>" citation in the package's Python
  files (the docstring ``References`` blocks), for the manuals cited that way;
* no citation in the package's own files names the manual with another
  series prefix (UFC for a UFS, or the reverse).

The table is the place to add a manual. Rows marked ``xfail`` are known
mismatches still to be corrected (strict, so fixing one fails the test until
its mark is removed). Skips when the PDFs are not checked out.
"""

import json
import os
import re
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references"
DOCS = ROOT / "docs"

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"])}

# package -> (pdf in docs/, designation as cited, cover date as printed or
# None, whether the package's Python cites "<designation>, <title>, <date>").
COVERS = [
    ("dm7_1", "ufc_3_220_10_2026.pdf", "UFS 3-220-10", "16 January 2026", True),
    ("dm7_2", "ufc_3_220_20_2025.pdf", "UFC 3-220-20", "16 January 2025", True),
    ("ufc_collapse", None, "UFC 4-023-03", "14 July 2009", False),
    ("ufc_concrete_practice", None, "UFC 3-250-04", "29 January 2024", False),
    ("ufc_flexible_practice", None, "UFC 3-250-03", "30 May 2018", False),
    ("ufc_pavement", None, "UFC 3-250-01", "14 November 2016", False),
    ("ufc_stabilization", None, "UFC 3-250-11", "30 November 2020", False),
    ("ufc_structural", None, "UFC 3-301-01", "11 April 2023", False),
    ("em_2104", None, "EM 1110-2-2104", "1 November 2023", False),
    ("gec_12", None, "FHWA-NHI-16-009", None, False),
    ("gec_13", None, "FHWA-NHI-16-027", None, False),
    ("gec_7", None, "FHWA-NHI-14-007", None, False),
    pytest.param(
        "gec_10", None, "FHWA-NHI-18-024", None, False,
        marks=pytest.mark.xfail(strict=True, reason=(
            "manifest, catalog and agents/references_agent.py cite "
            "FHWA-NHI-10-016 (the 2010 GEC 10); the PDF is FHWA-NHI-18-024, "
            "September 2018")), id="gec_10"),
    pytest.param(
        "ufc_backfill", None, "UFC 3-220-04FA", "16 January 2004", False,
        marks=pytest.mark.xfail(strict=True, reason=(
            "the data cites UFC 3-220-04N; the cover reads "
            "UFC 3-220-04FA, 16 January 2004")), id="ufc_backfill"),
]


def _norm(text):
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _date_key(text):
    m = re.fullmatch(r"\s*(\d{1,2})\s+([A-Za-z]{3})[a-z]*\.?,?\s+(\d{4})\s*",
                     text)
    assert m, f"not a date: {text!r}"
    return int(m.group(1)), MONTHS[m.group(2).lower()], int(m.group(3))


def _manifest(pkg):
    for name in (f"{pkg}.json", f"{pkg}_v1.json"):
        p = ROOT / "scripts" / "manifests" / name
        if p.exists():
            return p, json.loads(p.read_text(encoding="utf-8"))
    return None, None


def _pdf(pkg, pdf):
    if pdf:
        return DOCS / pdf
    path, man = _manifest(pkg)
    rel = man.get("pdf_path") or man["volumes"][0]["pdf_path"]
    return (path.parent / rel).resolve()


def _cover_text(path):
    with fitz.open(str(path)) as doc:
        return " ".join(doc[i].get_text() for i in range(min(2, len(doc))))


def _cited_ids(pkg):
    """(where, reference_id) of every data file of the package."""
    out = []
    path, man = _manifest(pkg)
    if man:
        out.append((path.name, man.get("reference_id")))
    for f in sorted((PKG / pkg).glob("figures_catalog.json")) + sorted(
            (PKG / pkg).glob("text/*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        out.append((f"{pkg}/{f.relative_to(PKG / pkg)}",
                    data.get("reference_id")))
    agent = (ROOT / "agents" / "references_agent.py").read_text(
        encoding="utf-8")
    m = re.search(r'"%s":\s*\{.*?"citation":\s*"([^"]+)"' % re.escape(pkg),
                  agent, re.S)
    if m:
        out.append(("agents/references_agent.py",
                    re.split(r"\s+[(—]", m.group(1), maxsplit=1)[0]))
    return out


@pytest.mark.parametrize("pkg,pdf,designation,date,py_dates", COVERS,
                         ids=[c[0] if isinstance(c, tuple) else None
                              for c in COVERS])
def test_cited_designation_and_date_on_cover(pkg, pdf, designation, date,
                                             py_dates):
    path = _pdf(pkg, pdf)
    if not path.exists():
        pytest.skip(f"{path.name} not checked out")
    cover = _cover_text(path)
    assert _norm(designation) in _norm(cover), (
        f"{designation!r} is not on the cover of {path.name}")
    if date:
        cover_dates = {_date_key(d) for d in re.findall(
            r"\d{1,2}\s+[A-Z][a-z]+,?\s+\d{4}", cover)}
        assert _date_key(date) in cover_dates, (
            f"{date!r} is not on the cover of {path.name}")

    cited = _cited_ids(pkg)
    assert cited, f"no citation found for {pkg}"
    wrong = [(w, c) for w, c in cited if _norm(c or "") != _norm(designation)]
    assert not wrong, f"{pkg} cited as something else: {wrong}"

    if py_dates:
        # Any series prefix, so a citation under the wrong one is caught too.
        number = designation.split(" ", 1)[1]
        pat = re.compile(r"\b([A-Z]{2,5})\s+" + re.escape(number) +
                         r",[^\n]*?(\d{1,2}\s+[A-Z][a-z]{2,8}\.?\s+\d{4})")
        seen = 0
        for f in sorted((PKG / pkg).glob("*.py")):
            for m in pat.finditer(f.read_text(encoding="utf-8")):
                seen += 1
                assert f"{m.group(1)} {number}" == designation, (
                    f"{f.name}: {m.group(0)!r} is not cited as "
                    f"{designation}")
                assert _date_key(m.group(2)) == _date_key(date), (
                    f"{f.name}: {m.group(0)!r} gives another date than "
                    f"the cover's {date}")
        assert seen, f"no dated citation of {designation} in {pkg}/*.py"


@pytest.mark.parametrize("pkg,designation", [
    ("dm7_1", "UFS 3-220-10"), ("dm7_2", "UFC 3-220-20")])
def test_no_citation_with_another_series_prefix(pkg, designation):
    series, number = designation.split(" ", 1)
    other = re.compile(r"\b(?!%s\b)UF[A-Z]\s+%s(?![\d])"
                       % (series, re.escape(number)))
    hits = []
    for f in sorted((PKG / pkg).rglob("*")):
        if f.suffix in (".py", ".json"):
            for m in other.finditer(f.read_text(encoding="utf-8")):
                hits.append(f"{f.relative_to(PKG)}: {m.group(0)}")
    assert not hits, hits[:10]


def test_dm7_1_equation_pages_are_the_2026_printed_pages():
    """Every "Equation X-Y, p. N" in dm7_1/*.py is the 2026 printed page.

    REF-28: the pages were from another pagination (e.g. Eq 1-1 cited
    p. 49, printed p. 15; Eq 5-1 p. 257, printed p. 224). The 2026 print
    labels Equations 5-19 and 5-28 "(5-5-19)" and "(5-5-28)".
    """
    path = DOCS / "ufc_3_220_10_2026.pdf"
    if not path.exists():
        pytest.skip(f"{path.name} not checked out")
    with fitz.open(str(path)) as doc:
        pages = [doc[i].get_text() for i in range(len(doc))]

    def printed(i):
        lines = [ln.strip() for ln in pages[i].splitlines() if ln.strip()]
        for ln in lines[2:5]:
            if ln.isdigit():
                return int(ln)

    cites = []
    for f in sorted((PKG / "dm7_1").glob("chapter*.py")):
        cites += [(f.name, eq, int(p)) for eq, p in re.findall(
            r"Equation (\d+-\d+), pp?\. (\d+)", f.read_text(encoding="utf-8"))]
    assert len(cites) > 100
    wrong = []
    for name, eq, p in cites:
        label = re.compile(r"\(\s*(?:5-)?%s\s*\)" % re.escape(eq)
                           if eq in ("5-19", "5-28")
                           else r"\(\s*%s\s*\)" % re.escape(eq))
        where = {printed(i) for i in range(28, len(pages))
                 if label.search(pages[i])}
        if p not in where:
            wrong.append((name, eq, p, sorted(x for x in where if x)))
    assert not wrong, wrong[:10]
