"""The reference helper can reach everything it is told it has (2026-11-12
reach audit; the owner's acceptance test for the reference release).

A fetched section names figures and tables and points to other parts of
its document. These tests check, across the whole library, that what a
section names is held or flagged (``figures_held``, ``tables_held``,
``not_held``; :mod:`geotech_references._reach`), that every function a
chapter file says implements something exists, that cross-references name
the manuals' own content, that every figure number can be fetched, and that
the wheel ships every data file the code reads. ``tests/reach_baseline.json``
holds the counts of what is not held per reference: they may shrink (lower
the baseline then), never grow.

The rules that read pointers are tested on made-up text (no value or
wording copied from a manual) and on a made-up local pack.
"""

from __future__ import annotations

import fnmatch
import importlib
import json
import os
import re
import sqlite3
import tempfile
from pathlib import Path

import pytest

from geotech_references import _packs, _reach, _retrieval, _retrieval_db

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "geotech_references"
BASELINE = Path(__file__).with_name("reach_baseline.json")


def _walk(sections):
    for sec in sections:
        yield sec
        yield from _walk(sec.get("subsections") or [])


def _chapter_files():
    for ref_dir in sorted(PKG.iterdir()):
        if (ref_dir / "text").is_dir():
            for jf in sorted((ref_dir / "text").glob("*.json")):
                yield ref_dir.name, json.loads(jf.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# The rules, on made-up text
# ---------------------------------------------------------------------------

def test_listing_numbers_in_every_listing_form():
    n = _reach.listing_number
    assert n("Figure 7-7 (a): A made-up caption", "figure") == "7-7"
    assert n("Figure 2-6a: A made-up caption", "figure") == "2-6a"
    assert n("Fig. 4.12 Made up", "figure") == "4.12"
    assert n("4-1", "figure") == "4-1"                    # bare numbers
    assert n({"figure_id": "Figure 2.1", "title": "x"}, "figure") == "2.1"
    assert n({"table_id": "Table C-2a"}, "table") == "C-2a"
    assert n("Table 9-37(a) made up", "table") == "9-37(a)"
    assert n("Analysis period guidelines", "table") is None


def test_the_short_form_and_back():
    held = {"1-1": "catalog", "1-2": "catalog", "1-3": "not held"}
    short = _reach.collapse(held)
    assert short == {"1-3": "not held", "others": "catalog"}
    assert _reach.expand(short, list(held)) == held
    same = {"1-1": "not held", "1-2": "not held"}
    assert _reach.collapse(same) == {"all": "not held"}
    assert _reach.expand({"all": "not held"}, list(same)) == same
    two = {"1-1": "catalog", "1-2": "not held"}
    assert _reach.collapse(two) == two


def _rows(sections, chapter=1, title="Made-Up Chapter"):
    """sqlite rows shaped like the ``sections`` table, for Holdings."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE s (rowid INTEGER PRIMARY KEY, reference TEXT,"
                 " chapter INTEGER, chapter_title TEXT, section_id TEXT,"
                 " body TEXT, equations_json TEXT, figures_json TEXT,"
                 " tables_json TEXT)")
    for sec in sections:
        conn.execute(
            "INSERT INTO s (reference, chapter, chapter_title, section_id, "
            "body, equations_json, figures_json, tables_json) "
            "VALUES (?,?,?,?,?,?,?,?)",
            ("local_madeup", sec.get("chapter", chapter),
             sec.get("chapter_title", title), sec["section_id"],
             sec.get("body", ""), json.dumps(sec.get("equations", [])),
             json.dumps(sec.get("figures", [])),
             json.dumps(sec.get("tables", []))))
    return conn.execute("SELECT * FROM s ORDER BY rowid").fetchall()


@pytest.fixture
def holdings():
    rows = _rows([
        {"section_id": "2-1", "body": "Made-up text.",
         "equations": [{"id": "Eq. 2-1", "description": "x"}],
         "tables": ["Table 2-1 Made up", "Table 2-2a Made up"],
         "figures": ["Figure 2-1 Made up"]},
        {"section_id": "2-2", "body": "q = 3 k (Eq. 2-4). More text.\n"
                                      "11-1.5 Typed Heading: words."},
        {"section_id": "2-3", "body": "", "chapter": 3,
         "chapter_title": "Appendix B: Made-Up Examples"},
    ])
    return _reach.Holdings("local_madeup", rows)


@pytest.mark.parametrize("body, expected", [
    ("See Section 2-9 for the method.", ["Section 2-9"]),
    ("See Section 2-1 and Eq. 2-1.", []),                 # held
    ("Use Eq. 2-4 here.", []),                            # typed with = above
    ("As in Eq. 2-5, the value.", ["Eq. 2-5"]),
    ("Per ASTM D1586 Section 2-9.", []),                  # another document
    ("Smith (1999) Table 2-7 shows it.", []),             # author and year
    ("See Table 2-7 of AASHTO.", []),                     # "of" another
    ("Falsework Manual Section 2-9 applies.", []),        # a named work
    ("See Table 2-\n7 there.", []),                       # split number
    ("See Equation 2- 6 there.", []),                     # split number
    ("Use Eq. 2-1, 1.0 for that case.", []),              # a value follows
    ("Use Eq. 2-1, or 0.56 for that case.", []),          # a value follows
    ("Tables 2-1, 2-7, and 2-8 apply.", ["Table 2-7", "Table 2-8"]),
    ("Table 2-2 holds its parts.", []),                   # 2-2a is listed
    ("See Appendix B.", []),                              # a chapter title
    ("See Appendix C.", ["Appendix C"]),
    ("Appendix C - Made Up Logs", []),                    # contents list
    ("See Chapter 3 and Chapter 9.", ["Chapter 9"]),
    ("See Chapters 4-8.", []),                            # a range
    ("See Section 11-1.5 below.", []),                    # typed heading
    ("See Section X.01 of the sample.", []),              # not a form held
])
def test_which_pointers_are_flagged(holdings, body, expected):
    assert _reach.pointers_not_held(body, holdings) == expected


def test_figure_answers(tmp_path, monkeypatch):
    folder = tmp_path / "local_madeup"
    folder.mkdir()
    (folder / "figures_catalog.json").write_text(json.dumps({"figures": [
        {"figure_number": "1-1", "pdf_page_index": 3},
        {"figure_number": "1-2", "pdf_page_index": 4},
        {"figure_number": "1-2", "pdf_page_index": 5},
        {"figure_number": "1-3A", "pdf_page_index": 6},
        {"figure_number": "1-3B", "pdf_page_index": 6}]}), encoding="utf-8")
    monkeypatch.setattr(_reach, "reference_dir", lambda ref: folder)
    h = _reach.Holdings("local_madeup", _rows([{"section_id": "1-1"}]))
    assert h.figure_flag("1-1") == "catalog"
    assert h.figure_flag("Figure 1-1") == "catalog"
    assert h.figure_flag("1-1(a)") == "catalog (as 1-1)"
    assert h.figure_flag("1-2").startswith("catalog (2 rows")
    assert h.figure_flag("1-3") == "catalog (as parts 1-3A, 1-3B)"
    assert h.figure_flag("1-9") == "not held"
    assert not h.has_tables_catalog
    assert h.table_flag("1-1") == "not held"   # no table catalog
    # pointers: a part of a held figure, a figure held by its parts
    assert _reach.pointers_not_held(
        "See Figure 1-1b, Figure 1-3 and Figure 1-9.", h) == ["Figure 1-9"]


def test_table_answers_from_a_catalog():
    row = {"table_number": "5-1", "values": "text", "values_in": ["5-3.2"]}
    assert _reach.table_values(row) == "text: 5-3.2"
    assert _reach.table_values(
        {"values": "lookup", "values_in": "dm7_1.chapter5.table_5_1"}
    ) == "lookup: dm7_1.chapter5.table_5_1"
    assert _reach.table_values(
        {"values": "page", "pdf_page_index": 41, "printed_page": "5-7"}
    ) == "page: pdf_page_index 41, printed p. 5-7"
    assert _reach.table_values({"values": None}) == "not held"


# ---------------------------------------------------------------------------
# A made-up local pack: the flags on both fetches
# ---------------------------------------------------------------------------

PID = "local_reach_manual"


def _section(sid, title, body, **extra):
    sec = {"section_id": sid, "title": title, "body": body,
           "key_points": [], "equations": [], "figures": [], "tables": [],
           "applicability": "Made-up test text for the reach tests."}
    sec.update(extra)
    return sec


def _pack(root: Path) -> Path:
    folder = root / PID
    (folder / "text").mkdir(parents=True)
    (folder / "pack.json").write_text(json.dumps({
        "id": PID, "reference_id": "RCH-01",
        "reference_title": "Made-Up Reach Manual",
        "edition": "2026 (made up)", "pdf_files": ["reach manual.pdf"],
        "prepared_by": "test", "prepared_on": "2026-11-12",
        "method": "printed", "distribution": "test fixture"}),
        encoding="utf-8")
    chapter = {
        "reference_id": "RCH-01", "reference_title": "Made-Up Reach Manual",
        "volume": None, "chapter": 1, "chapter_title": "Glorp Walls",
        "sections": [
            _section("1.1", "Scope", "Glorp walls are made up. See "
                     "Section 1.2 and Section 1.7; the chart is Figure 1-1.",
                     figures=["Figure 1-1 Glorp chart",
                              "Figure 1-2 Glorp detail"],
                     tables=["Table 1-1 Glorp text table",
                             "Table 1-2 Glorp lookup table",
                             "Table 1-3 Glorp page table",
                             "Table 1-4 Glorp missing table"]),
            _section("1.2", "Glorp Loads", "Loads are made up. See "
                     "ASTM D9999 Section 4.4 for the made-up test.\n"
                     "The load cases are given in Chapter 6."),
            _section("1.2.1", "Wet Glorp", "Wet glorp is made up; see "
                     "Figure 1-9."),
        ]}
    (folder / "text" / "chapter01.json").write_text(json.dumps(chapter),
                                                    encoding="utf-8")
    (folder / "figures_catalog.json").write_text(json.dumps({
        "reference_id": "RCH-01", "reference_title": "Made-Up Reach Manual",
        "package": PID, "volume": None, "pdf_path": "reach manual.pdf",
        "figures": [{"figure_number": "1-1", "caption": "Glorp chart",
                     "chapter": 1, "pdf_page_index": 0, "printed_page": 2,
                     "page_estimated": False, "description": "Made up."}]}),
        encoding="utf-8")
    (folder / "tables_catalog.json").write_text(json.dumps({"tables": [
        {"table_number": "1-1", "caption": "Glorp text table",
         "section_id": "1.1", "pdf_page_index": 0, "printed_page": 2,
         "values": "text", "values_in": ["1.1"]},
        {"table_number": "1-2", "caption": "Glorp lookup table",
         "section_id": "1.1", "pdf_page_index": 0, "printed_page": 2,
         "values": "lookup", "values_in": "local_reach_manual.table_1_2"},
        {"table_number": "1-3", "caption": "Glorp page table",
         "section_id": "1.1", "pdf_page_index": 1, "printed_page": 3,
         "values": "page", "values_in": None}]}), encoding="utf-8")
    return folder


@pytest.fixture(scope="module")
def reach_pack(tmp_path_factory):
    """One made-up pack and a private database folder."""
    root = tmp_path_factory.mktemp("reachpacks")
    _pack(root)
    dbdir = tmp_path_factory.mktemp("reachdb")
    old_env = os.environ.get(_packs.PACKS_ENV)
    old_tmp = tempfile.tempdir
    os.environ[_packs.PACKS_ENV] = str(root)
    tempfile.tempdir = str(dbdir)
    try:
        yield root
    finally:
        tempfile.tempdir = old_tmp
        if old_env is None:
            os.environ.pop(_packs.PACKS_ENV, None)
        else:
            os.environ[_packs.PACKS_ENV] = old_env


@pytest.mark.parametrize("fetch", ["reference_get", "retrieve_section"])
def test_a_fetched_section_says_what_it_reaches(reach_pack, fetch):
    get = (_retrieval_db.reference_get if fetch == "reference_get"
           else _retrieval.retrieve_section)
    sec = get(PID, "1.1")
    assert sec["figures_held"] == {"1-1": "catalog", "1-2": "not held"}
    assert sec["tables_held"] == {
        "1-1": "text: 1.1",
        "1-2": "lookup: local_reach_manual.table_1_2",
        "1-3": "page: pdf_page_index 1, printed p. 3",
        "1-4": "not held"}
    assert sec["not_held"] == ["Section 1.7"]
    assert _reach.NOT_HELD_NOTE in sec["note"]
    # another document's section, and a chapter it does not hold
    assert get(PID, "1.2")["not_held"] == ["Chapter 6"]
    # nothing to say: no keys
    wet = get(PID, "1.2.1")
    assert wet["not_held"] == ["Figure 1-9"]
    assert "figures_held" not in wet and "tables_held" not in wet


@pytest.mark.parametrize("fetch", ["reference_get", "retrieve_section"])
def test_inlined_subsections_carry_their_flags(reach_pack, fetch):
    get = (_retrieval_db.reference_get if fetch == "reference_get"
           else _retrieval.retrieve_section)
    sec = get(PID, "1.2", include_subsections=True)
    sub = sec["subsections"][0]
    assert sub["section_id"] == "1.2.1"
    assert sub["not_held"] == ["Figure 1-9"]
    assert _reach.NOT_HELD_NOTE in sub["note"]
    assert _reach.NOT_HELD_NOTE in sec["note"]


def test_the_fetch_works_without_the_flags(reach_pack, monkeypatch):
    """A database that cannot be built leaves the chapter-file fetch as it
    was before the flags."""
    def broken():
        raise RuntimeError("no database")
    monkeypatch.setattr(_retrieval_db, "_ensure_db", broken)
    monkeypatch.setattr(_reach, "_CHECKED", {})
    sec = _retrieval.retrieve_section(PID, "1.1")
    assert sec["body"].startswith("Glorp walls")
    assert "figures_held" not in sec


# ---------------------------------------------------------------------------
# The whole library
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def library_db():
    """The library's own text database (no local packs)."""
    old = os.environ.pop(_packs.PACKS_ENV, None)
    try:
        yield _retrieval_db._ensure_db()
    finally:
        if old is not None:
            os.environ[_packs.PACKS_ENV] = old


def test_every_section_has_a_body_or_sections_under_it(library_db):
    conn = sqlite3.connect(library_db)
    try:
        empty = conn.execute(
            "SELECT reference, section_id FROM sections s WHERE "
            "trim(coalesce(body, '')) = '' AND NOT EXISTS (SELECT 1 FROM "
            "sections k WHERE k.parent_rowid = s.rowid)").fetchall()
    finally:
        conn.close()
    assert empty == []


def test_every_listed_figure_and_table_has_an_answer(library_db):
    conn = sqlite3.connect(library_db)
    try:
        rows = conn.execute(
            "SELECT s.reference, s.section_id, s.figures_json, s.tables_json,"
            " r.reach_json FROM sections s LEFT JOIN section_reach r "
            "ON r.sec_rowid = s.rowid").fetchall()
    finally:
        conn.close()
    missing = []
    for ref, sid, figs, tabs, flags in rows:
        flags = json.loads(flags or "{}")
        for key, listing, kind in (("figures_held", figs, "figure"),
                                   ("tables_held", tabs, "table")):
            numbers = _reach.listed_numbers(json.loads(listing or "[]"), kind)
            if not numbers:
                continue
            held = _reach.expand(flags.get(key, {}), numbers)
            for num, answer in held.items():
                ok = (answer == _reach.NOT_HELD
                      or answer.startswith(_reach.HELD_IN_CATALOG)
                      or answer.split(":")[0] in ("text", "lookup", "page"))
                if key not in flags or not ok:
                    missing.append((ref, sid, num, answer))
    assert missing == []


def _callable(path: str) -> bool:
    mod, _, name = path.rpartition(".")
    try:
        return callable(getattr(importlib.import_module(mod), name))
    except (ImportError, AttributeError, ValueError):
        return False


def test_every_implemented_in_is_a_function_the_package_has():
    bad, n = [], 0
    for ref, data in _chapter_files():
        for sec in _walk(data.get("sections", [])):
            paths = []
            if sec.get("implemented_in"):
                # section level: "module.function, module.function"
                paths += [f"geotech_references.{ref}.{p.strip()}"
                          for p in str(sec["implemented_in"]).split(",")]
            for eq in sec.get("equations") or []:
                if isinstance(eq, dict) and eq.get("implemented_in"):
                    paths.append(str(eq["implemented_in"]))
            for path in paths:
                n += 1
                if not _callable(path):
                    bad.append((ref, sec.get("section_id"), path))
    assert n > 500
    assert bad == []


_XREF_KEY = re.compile(r"^(?P<ref>[a-z0-9_]+) (?P<kind>Chapter|Section) "
                       r"(?P<num>\S+)$")


def test_cross_references_name_the_manuals_own_content(library_db):
    refs = {ref for ref, _ in _chapter_files()}
    chapters = {}
    for ref, data in _chapter_files():
        chapters.setdefault(ref, set()).add(str(data.get("chapter")))
    conn = sqlite3.connect(library_db)
    bad, n = [], 0
    try:
        for ref, data in _chapter_files():
            for sec in _walk(data.get("sections", [])):
                for key, value in (sec.get("cross_references") or {}).items():
                    n += 1
                    m = _XREF_KEY.match(key)
                    ok = bool(m) and m["ref"] in refs and isinstance(value,
                                                                     str)
                    if ok and m["kind"] == "Chapter":
                        ok = m["num"] in chapters[m["ref"]]
                    elif ok:
                        ok = conn.execute(
                            "SELECT 1 FROM sections WHERE reference = ? AND "
                            "section_id = ?", (m["ref"], m["num"])
                        ).fetchone() is not None
                    if not ok:
                        bad.append((ref, sec.get("section_id"), key))
    finally:
        conn.close()
    assert n > 0
    assert bad == []


def test_every_figure_number_can_be_fetched():
    """A number on several catalog rows is fetched by its page
    (``figure_get(..., pdf_page_index=)``), so the rows must be on
    different pages."""
    bad = []
    for cat in sorted(PKG.glob("*/figures_catalog.json")):
        data = json.loads(cat.read_text(encoding="utf-8"))
        rows = data["figures"] if isinstance(data, dict) else data
        pages = {}
        for row in rows:
            key = str(row.get("figure_number", "")).upper()
            pages.setdefault(key, []).append(row.get("pdf_page_index"))
        for key, idx in pages.items():
            if len(idx) > 1 and (None in idx or len(set(idx)) < len(idx)):
                bad.append((cat.parent.name, key, idx))
    assert bad == []


def test_what_is_not_held_does_not_grow(library_db):
    """Per reference: listed figures and tables and same-document pointers
    not held. A count above the baseline fails (something the helper is
    told about cannot be reached); one below it should be written into
    tests/reach_baseline.json."""
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    now = _reach.reach_counts()
    grew = [(ref, key, baseline.get(ref, {}).get(key, 0), n)
            for ref, counts in now.items() for key, n in counts.items()
            if n > baseline.get(ref, {}).get(key, 0)]
    assert grew == [], ("not held grew (reference, count, baseline, now): "
                        f"{grew}")


# ---------------------------------------------------------------------------
# Sizes and the wheel
# ---------------------------------------------------------------------------

#: Section fetches over the library's 14,000-character budget from their
#: own text, before the flags (2026-11-12; the app's cap is 16,000).
OVER_BUDGET_BEFORE_FLAGS = {("dm7_2", "4-9"),
                            ("fhwa_soils_foundations", "6.6.3"),
                            ("fhwa_soils_foundations", "9.5.1.1")}
BUDGET, APP_CAP = 14000, 16000


def test_flags_keep_the_largest_fetches_in_their_limits(library_db):
    conn = sqlite3.connect(library_db)
    try:
        big = conn.execute(
            "SELECT reference, section_id FROM sections WHERE "
            "coalesce(length(body), 0) + coalesce(length(equations_json), 0)"
            " + coalesce(length(figures_json), 0) + "
            "coalesce(length(tables_json), 0) + "
            "coalesce(length(key_points), 0) + coalesce(length(summary), 0)"
            " > 8000").fetchall()
    finally:
        conn.close()
    assert len(big) > 20
    over = []
    for ref, sid in big:
        for inc in (False, True):
            try:
                sec = _retrieval_db.reference_get(ref, sid,
                                                  include_subsections=inc)
            except KeyError:  # a number held twice
                continue
            size = len(json.dumps(sec, default=str))
            bare = len(json.dumps(
                {k: v for k, v in sec.items()
                 if k not in ("figures_held", "tables_held", "not_held")},
                default=str))
            assert size - bare <= 600, (ref, sid, size - bare)
            assert size <= APP_CAP, (ref, sid, size)
            if size > BUDGET:
                over.append((ref, sid))
    assert set(over) <= OVER_BUDGET_BEFORE_FLAGS


def _package_data_globs() -> list[str]:
    try:
        import tomllib
    except ImportError:  # Python 3.10
        tomllib = pytest.importorskip("tomli")
    with open(ROOT / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return data["tool"]["setuptools"]["package-data"]["geotech_references"]


def _shipped(rel: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, g) for g in globs)


def test_the_wheel_ships_every_data_file_the_code_reads():
    globs = _package_data_globs()
    files = [p.relative_to(PKG).as_posix() for p in PKG.rglob("*")
             if p.is_file() and p.suffix not in (".py", ".pyc")
             and p.name != ".gitkeep" and "__pycache__" not in p.parts]
    assert files
    assert [f for f in files if not _shipped(f, globs)] == []
    # and the names the code reads, whether or not a file exists yet
    for name in ("dm7_1/text/chapter1.json",
                 f"dm7_1/{_reach.FIGURES_CATALOG}",
                 f"dm7_1/{_reach.TABLES_CATALOG}", "chapter_schema.json"):
        assert _shipped(name, globs), name
