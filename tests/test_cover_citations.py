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

The table is the place to add a manual. A manual whose volumes are printed
under their own numbers is checked one volume at a time (``"gec_13/2"``: the
volume's manifest entry, its chapter files and its figures). Rows marked
``xfail`` are known mismatches still to be corrected (strict, so fixing one
fails the test until its mark is removed). Skips when the PDFs are not checked
out.

REF-31 (2026-11-06): GEC-10 is cited as FHWA-NHI-18-024 (its data is the
2018 edition) and GEC-13 Vol II as FHWA-NHI-16-028. ufc_backfill, rebuilt
from the held UFC 3-220-04FA (review pave-14, 2026-11-10), cites its cover.
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
    # REF-75: the held PDF is the 2025 UFC; the package cites the 2026 UFS
    # reissue, the same text and pages (see CITED_AS).
    ("dm7_2", "ufc_3_220_20_2025.pdf", "UFC 3-220-20", "16 January 2025", False),
    ("ufc_collapse", None, "UFC 4-023-03", "14 July 2009", False),
    ("ufc_concrete_practice", None, "UFC 3-250-04", "29 January 2024", False),
    ("ufc_flexible_practice", None, "UFC 3-250-03", "30 May 2018", False),
    ("ufc_pavement", None, "UFC 3-250-01", "14 November 2016", False),
    ("ufc_stabilization", None, "UFC 3-250-11", "30 November 2020", False),
    ("ufc_structural", None, "UFC 3-301-01", "11 April 2023", False),
    ("em_2104", None, "EM 1110-2-2104", "1 November 2023", False),
    ("em_1905", None, "EM 1110-1-1905", "31 July 2025", False),
    # 2026-11-10 review, core-13: each volume by its own cover. GEC-12
    # Vol II is read on its documentation page (READ_PAGES): its cover
    # prints FHWA-NHI-16-009, Vol I's number.
    ("gec_12/1", None, "FHWA-NHI-16-009", None, False),
    ("gec_12/2", None, "FHWA-NHI-16-010", None, False),
    ("gec_12/3", None, "FHWA-NHI-16-064", None, False),
    ("gec_11/1", None, "FHWA-NHI-10-024", None, False),
    ("gec_11/2", None, "FHWA-NHI-10-025", None, False),
    ("fhwa_soils_foundations/1", None, "FHWA-NHI-06-088", None, False),
    ("fhwa_soils_foundations/2", None, "FHWA-NHI-06-089", None, False),
    ("gec_13/1", None, "FHWA-NHI-16-027", None, False),
    ("gec_13/2", None, "FHWA-NHI-16-028", None, False),
    ("gec_7", None, "FHWA-NHI-14-007", None, False),
    ("gec_4", None, "FHWA-IF-99-015", None, False),
    ("gec_5", None, "FHWA-NHI-16-072", None, False),
    ("gec_6", None, "FHWA-SA-02-054", None, False),
    ("gec_8", None, "FHWA-HIF-07-03", None, False),
    ("gec_9", None, "FHWA-HIF-18-031", None, False),
    ("gec_14", None, "FHWA-HIF-17-016", None, False),
    ("micropile", None, "FHWA-NHI-05-039", None, False),
    ("em_2107", None, "EM 1110-2-2107", None, False),
    ("fema_p2082", None, "FEMA P-2082-1", None, False),
    ("ufc_expansive", None, "UFC 3-220-07", None, False),
    ("eurocode_7_1", None, "EN 1997-1:2004", None, False),
    ("eurocode_7_2", None, "EN 1997-2:2007", None, False),
    # Not in the table: fhwa_pavements,
    # gsa_collapse and california_trenching cite a title, not a designation;
    # aashto_1993 is a scan with no text layer; the wood_handbook PDF is not
    # in docs/.
    ("gec_10", None, "FHWA-NHI-18-024", None, False),
    # REF-31 kept the 04N citation while the package's tables were not the
    # held 04FA's; review pave-14 (2026-11-10) rebuilt them from the 04FA
    # print, so it cites the cover.
    ("ufc_backfill", None, "UFC 3-220-04FA", "16 January 2004", False),
]


#: Packages cited under a designation other than the held PDF's cover.
CITED_AS = {"dm7_2": "UFS 3-220-20"}


#: Volumes checked against another page than the cover (0-based PDF pages).
#: GEC-12 Vol II's cover (PDF page 1) prints "Publication No.
#: FHWA-NHI-16-009", Vol I's number; its Technical Report Documentation Page
#: (PDF page 3) prints "1. REPORT NO. FHWA-NHI-16-010", and Vol III's
#: documentation page names "FHWA-NHI-16-009 and FHWA-NHI-16-010" as the
#: two volumes it supplements. The volume is cited as 16-010 and the cover's
#: number taken as a misprint (2026-11-10 review).
READ_PAGES = {"gec_12/2": (2,)}


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


def _split(pkg):
    """``"gec_13/2"`` -> ``("gec_13", 2)``; ``"gec_10"`` -> ``("gec_10", None)``."""
    name, _, vol = pkg.partition("/")
    return name, int(vol) if vol else None


def _volume_entry(man, volume):
    for v in man.get("volumes") or []:
        if v.get("volume") == volume:
            return v
    raise KeyError(f"no volume {volume} in the manifest")


def _pdf(pkg, pdf):
    if pdf:
        return DOCS / pdf
    pkg, volume = _split(pkg)
    path, man = _manifest(pkg)
    if volume is not None:
        rel = _volume_entry(man, volume)["pdf_path"]
    else:
        rel = man.get("pdf_path") or man["volumes"][0]["pdf_path"]
    return (path.parent / rel).resolve()


def _cover_text(path, pages=None):
    with fitz.open(str(path)) as doc:
        if pages is None:
            pages = range(min(2, len(doc)))
        return " ".join(doc[i].get_text() for i in pages)


def _cited_ids(pkg):
    """(where, reference_id) of every data file of the package (or volume)."""
    pkg, volume = _split(pkg)
    out = []
    path, man = _manifest(pkg)
    if man:
        if volume is None:
            out.append((path.name, man.get("reference_id")))
        else:
            out.append((f"{path.name} volume {volume}",
                        _volume_entry(man, volume).get("reference_id")
                        or man.get("reference_id")))
    for f in sorted((PKG / pkg).glob("figures_catalog.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        where = f"{pkg}/{f.name}"
        if volume is None or volume == 1:
            out.append((where, data.get("reference_id")))
        for fig in data.get("figures", []):
            if volume is not None and fig.get("volume") != volume:
                continue
            if volume is not None or fig.get("reference_id"):
                out.append((f"{where} figure {fig.get('figure_number')}",
                            fig.get("reference_id")
                            or data.get("reference_id")))
    for f in sorted((PKG / pkg).glob("text/*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        if volume is not None and data.get("volume") != volume:
            continue
        out.append((f"{pkg}/{f.relative_to(PKG / pkg)}",
                    data.get("reference_id")))
    from agents.references_agent import _REFERENCE_CATALOG
    entry = _REFERENCE_CATALOG.get(pkg)
    if entry and volume in (None, 1):
        out.append(("agents/references_agent.py",
                    re.split(r"\s+[(—]", entry["citation"], maxsplit=1)[0]))
    return out


@pytest.mark.parametrize("pkg,pdf,designation,date,py_dates", COVERS,
                         ids=[c[0] if isinstance(c, tuple) else None
                              for c in COVERS])
def test_cited_designation_and_date_on_cover(pkg, pdf, designation, date,
                                             py_dates):
    path = _pdf(pkg, pdf)
    if not path.exists():
        pytest.skip(f"{path.name} not checked out")
    cover = _cover_text(path, READ_PAGES.get(pkg))
    assert _norm(designation) in _norm(cover), (
        f"{designation!r} is not on the cover of {path.name}")
    if date:
        cover_dates = {_date_key(d) for d in re.findall(
            r"\d{1,2}\s+[A-Z][a-z]+,?\s+\d{4}", cover)}
        assert _date_key(date) in cover_dates, (
            f"{date!r} is not on the cover of {path.name}")

    cited = _cited_ids(pkg)
    assert cited, f"no citation found for {pkg}"
    wrong = [(w, c) for w, c in cited if _norm(c or "") != _norm(CITED_AS.get(pkg, designation))]
    assert not wrong, f"{pkg} cited as something else: {wrong}"

    if py_dates:
        # Any series prefix, so a citation under the wrong one is caught too.
        number = designation.split(" ", 1)[1]
        pat = re.compile(r"\b([A-Z]{2,5})\s+" + re.escape(number) +
                         r",[^\n]*?(\d{1,2}\s+[A-Z][a-z]{2,8}\.?\s+\d{4})")
        seen = 0
        for f in sorted((PKG / _split(pkg)[0]).glob("*.py")):
            for m in pat.finditer(f.read_text(encoding="utf-8")):
                seen += 1
                assert f"{m.group(1)} {number}" == designation, (
                    f"{f.name}: {m.group(0)!r} is not cited as "
                    f"{designation}")
                assert _date_key(m.group(2)) == _date_key(date), (
                    f"{f.name}: {m.group(0)!r} gives another date than "
                    f"the cover's {date}")
        assert seen, f"no dated citation of {designation} in {pkg}/*.py"


def test_gec12_vol2_cover_and_documentation_page():
    """The two numbers GEC-12 Vol II prints (READ_PAGES): if the PDF in
    docs/ is replaced by a printing that corrects either, this says so."""
    path = _pdf("gec_12/2", None)
    if not path.exists():
        pytest.skip(f"{path.name} not checked out")
    cover, doc_page = _norm(_cover_text(path, (0,))), _norm(
        _cover_text(path, (2,)))
    assert _norm("FHWA-NHI-16-009") in cover
    assert _norm("FHWA-NHI-16-010") not in cover
    assert _norm("REPORT NO. FHWA-NHI-16-010") in doc_page


@pytest.mark.parametrize("pkg,designation", [
    ("dm7_1", "UFS 3-220-10"), ("dm7_2", "UFS 3-220-20")])
def test_no_citation_with_another_series_prefix(pkg, designation):
    series, number = designation.split(" ", 1)
    other = re.compile(r"\b(?<!= )(?<!pages of )(?!%s\b)UF[A-Z]\s+%s(?![\d])"
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
        # "Equation 1-3, printed p. 17 (pdf_page_index 44)" (REF-78)
        cites += [(f.name, eq, int(p), idx) for eq, p, idx in re.findall(
            r"Equation (\d+-\d+),\s+(?:printed\s+)?pp?\.\s+(\d+)"
            r"(?:-\d+)?(?:\s+\(pdf_page_index\s+(\d+))?",
            f.read_text(encoding="utf-8"))]
    assert len(cites) > 100
    wrong = []
    for name, eq, p, idx in cites:
        if idx and printed(int(idx)) != p:
            wrong.append((name, eq, p, f"pdf_page_index {idx} prints "
                          f"{printed(int(idx))}"))
        label = re.compile(r"\(\s*(?:5-)?%s\s*\)" % re.escape(eq)
                           if eq in ("5-19", "5-28")
                           else r"\(\s*%s\s*\)" % re.escape(eq))
        where = {printed(i) for i in range(28, len(pages))
                 if label.search(pages[i])}
        if p not in where:
            wrong.append((name, eq, p, sorted(x for x in where if x)))
    assert not wrong, wrong[:10]


def test_dm7_2_is_cited_as_ufs_3_220_20_not_the_2025_ufc():
    """REF-75: no dm7_2 lookup's ``reference`` string or docstring
    References section cites "UFC 3-220-20" without the UFS designation (the
    2025 UFC is named only as what the UFS reissues: "UFS 3-220-20 (2026; =
    UFC 3-220-20, 2025)")."""
    import importlib
    import inspect

    from agents import dm7_agent

    bare = []
    for name in sorted(p.stem for p in (PKG / "dm7_2").glob("*.py")
                       if p.stem != "__init__"):
        mod = importlib.import_module(f"geotech_references.dm7_2.{name}")
        for fname, fn in inspect.getmembers(mod, inspect.isfunction):
            if fn.__module__ != mod.__name__:
                continue
            doc = inspect.getdoc(fn) or ""
            refs = doc.split("References\n----------")[-1] \
                if "References\n----------" in doc else ""
            for text in (refs,):
                if "UFC 3-220-20" in text and "UFS 3-220-20" not in text:
                    bare.append(f"{name}.{fname}")
    src = (Path(dm7_agent.__file__)).read_text(encoding="utf-8")
    for m in re.finditer(r'"reference":\s*"([^"]*)"', src):
        if "UFC 3-220-20" in m.group(1) and "UFS 3-220-20" not in m.group(1):
            bare.append(m.group(0))
    assert not bare, bare[:10]
