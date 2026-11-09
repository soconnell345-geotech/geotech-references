"""Local reference packs (REF-64): indexing, lookup, the database key and
the checker.

Every value here is made up: a fictitious "Example Practice Manual" about a
fictitious material, zorblite, built in ``tmp_path``. No real manual is used.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from geotech_references import _figures_db, _packs, _retrieval, _retrieval_db
from geotech_references import _schema, packs

try:
    import pymupdf
except ImportError:  # pragma: no cover
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None

PID = "local_example_manual"
REF_ID = "EPM-01"
TITLE = "Example Practice Manual"
PDF_NAME = "example practice manual.pdf"
TERM = "zorblite"  # made up; printed in no built-in reference


def _section(sid, title, body, **extra):
    sec = {"section_id": sid, "title": title, "body": body,
           "key_points": [], "equations": [], "figures": [], "tables": [],
           "applicability": "Made-up test text for the pack tests."}
    sec.update(extra)
    return sec


def _chapter(chapter=1, ref_id=REF_ID, title=TITLE):
    return {
        "reference_id": ref_id,
        "reference_title": title,
        "volume": None,
        "chapter": chapter,
        "chapter_title": "Zorblite Embankments",
        "sections": [
            _section("1.1", "Scope",
                     "[p. 1-1] This chapter covers embankments built of "
                     "zorblite, a made-up fill used only in these tests."),
            _section("1.2", "Zorblite Settlement",
                     "[p. 1-2] Zorblite fill settles under its own weight; "
                     "the settlement chart is Figure 1-1.",
                     equations=[{"id": "Eq. 1-1",
                                 "description": "made-up settlement ratio",
                                 "formula": "s = 0.01 H",
                                 "source": "p. 1-2",
                                 "implemented_in": None}],
                     figures=["Figure 1-1 Zorblite settlement chart"]),
            _section("1.2.1", "Settlement of Wet Zorblite",
                     "[p. 1-3] Wet zorblite settles faster than dry "
                     "zorblite; see Figure 1-2."),
        ],
    }


def _catalog():
    return {
        "reference_id": REF_ID,
        "reference_title": TITLE,
        "package": PID,
        "volume": None,
        "pdf_path": PDF_NAME,
        "figures": [
            {"figure_number": "1-1", "caption": "Zorblite settlement chart",
             "chapter": 1, "pdf_page_index": 0, "printed_page": 2,
             "page_estimated": False,
             "description": "Settlement of zorblite fill against height.",
             "bbox": [72.0, 100.0, 400.0, 400.0],
             "read_notes": "The x axis is logarithmic."},
            {"figure_number": "1-2", "caption": "Wet zorblite settlement",
             "chapter": 1, "pdf_page_index": 0, "printed_page": 3,
             "page_estimated": False,
             "description": "Settlement of wet zorblite fill."},
        ],
    }


def _pack_json(pid=PID):
    return {"id": pid, "reference_id": REF_ID, "reference_title": TITLE,
            "edition": "2026 (made up)", "pdf_files": [PDF_NAME],
            "prepared_by": "test", "prepared_on": "2026-11-09",
            "method": "printed", "distribution": "test fixture"}


def _write_pdf(path: Path) -> None:
    if pymupdf is None:
        path.write_bytes(b"%PDF-1.4\n% placeholder\n")
        return
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 80), "Figure 1-1 Zorblite settlement chart")
    page.insert_text((72, 500), "Figure 1-2 Wet zorblite settlement")
    doc.save(str(path))
    doc.close()


def make_pack(root: Path, pid: str = PID, pdf: bool = True) -> Path:
    folder = root / pid
    (folder / "text").mkdir(parents=True)
    (folder / "pack.json").write_text(json.dumps(_pack_json(pid)),
                                      encoding="utf-8")
    (folder / "text" / "chapter01.json").write_text(
        json.dumps(_chapter()), encoding="utf-8")
    (folder / "figures_catalog.json").write_text(
        json.dumps(_catalog()), encoding="utf-8")
    if pdf:
        _write_pdf(folder / PDF_NAME)
    return folder


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def no_packs(monkeypatch):
    monkeypatch.delenv(_packs.PACKS_ENV, raising=False)


@pytest.fixture(scope="module")
def pack_env(tmp_path_factory):
    """One pack set and one pair of databases for the lookup tests. The
    databases go to a private temp folder, not the shared one."""
    root = tmp_path_factory.mktemp("packs")
    folder = make_pack(root)
    dbdir = tmp_path_factory.mktemp("db")
    old_env = os.environ.get(_packs.PACKS_ENV)
    old_tmp = tempfile.tempdir
    os.environ[_packs.PACKS_ENV] = str(root)
    tempfile.tempdir = str(dbdir)
    try:
        yield folder
    finally:
        tempfile.tempdir = old_tmp
        if old_env is None:
            os.environ.pop(_packs.PACKS_ENV, None)
        else:
            os.environ[_packs.PACKS_ENV] = old_env


# ---------------------------------------------------------------------------
# unset: exactly what the library did before packs
# ---------------------------------------------------------------------------

def _old_text_jsons():
    out = []
    for ref_dir in sorted(_retrieval_db._PACKAGE_DIR.iterdir()):
        if ref_dir.is_dir() and (ref_dir / "text").is_dir():
            out.extend((ref_dir.name, jf)
                       for jf in sorted((ref_dir / "text").glob("*.json")))
    return out


def _old_catalogs():
    return [d / "figures_catalog.json"
            for d in sorted(_figures_db._PACKAGE_DIR.iterdir())
            if d.is_dir() and (d / "figures_catalog.json").is_file()]


def _old_key(name, package_dir=_retrieval_db._PACKAGE_DIR):
    stem, suffix = os.path.splitext(name)
    return (Path(tempfile.gettempdir())
            / f"{stem}_{_retrieval_db._copy_key(str(package_dir))}{suffix}")


@pytest.mark.parametrize("setting", [None, "", os.pathsep])
def test_unset_is_unchanged(monkeypatch, setting):
    if setting is None:
        monkeypatch.delenv(_packs.PACKS_ENV, raising=False)
    else:
        monkeypatch.setenv(_packs.PACKS_ENV, setting)
    assert _retrieval_db._iter_text_jsons() == _old_text_jsons()
    assert _figures_db._iter_catalogs() == _old_catalogs()
    for name in (_retrieval_db._DB_NAME, _figures_db._DB_NAME):
        assert _retrieval_db.keyed_db_path(name) == _old_key(name)
    assert _retrieval_db._db_path() == _old_key(_retrieval_db._DB_NAME)
    assert _figures_db._db_path() == _old_key(_figures_db._DB_NAME)
    assert _packs.key_part() == ""
    assert _packs.pack_dirs() == [] and _packs.problems() == []


def test_folder_with_no_valid_pack_keeps_the_key(monkeypatch, tmp_path):
    (tmp_path / "local_bad").mkdir()
    (tmp_path / "local_bad" / "pack.json").write_text("{not json")
    monkeypatch.setenv(_packs.PACKS_ENV, str(tmp_path))
    assert _retrieval_db.keyed_db_path("x.sqlite") == _old_key("x.sqlite")
    assert _retrieval_db._iter_text_jsons() == _old_text_jsons()
    assert len(_packs.problems()) == 1


def test_builtin_figure_has_no_new_fields(no_packs):
    rec = _figures_db.figure_get("dm7_2", "4-12")
    assert "bbox" not in rec and "read_notes" not in rec


# ---------------------------------------------------------------------------
# with the setting: the pack is searched, fetched and read like a built-in
# ---------------------------------------------------------------------------

def test_pack_is_listed(pack_env):
    refs = {r["reference"]: r for r in _retrieval_db.list_indexed_references()}
    assert refs[PID]["reference_title"] == TITLE
    assert refs[PID]["n_chapters"] == 1 and refs[PID]["n_sections"] == 3
    assert "gec_12" in refs  # the built-ins are still there
    figs = {r["reference"] for r in _figures_db.list_indexed_figures()}
    assert PID in figs and "dm7_2" in figs


def test_made_up_term_found_only_in_pack(pack_env):
    hits = _retrieval_db.reference_search(TERM, limit=10)
    assert hits and all(h["reference"] == PID for h in hits)
    assert {h["section_id"] for h in hits} == {"1.1", "1.2", "1.2.1"}


def test_reference_get_with_children(pack_env):
    sec = _retrieval_db.reference_get(PID, "1.2")
    assert sec["reference"] == PID and sec["title"] == "Zorblite Settlement"
    assert [c["section_id"] for c in sec["children"]] == ["1.2.1"]
    child = _retrieval_db.reference_get(PID, "1.2.1")
    assert child["parent_id"] == "1.2"
    # the file-based retrieval layer reads the pack too
    assert _retrieval.retrieve_section(PID, "1.1")["title"] == "Scope"


def test_figure_search_and_get(pack_env):
    hits = _figures_db.figure_search(TERM, limit=10)
    assert hits and all(h["reference"] == PID for h in hits)
    assert "bbox" not in hits[0]  # search hits are unchanged in shape
    rec = _figures_db.figure_get(PID, "Figure 1-1")
    assert rec["pdf_path"] == PDF_NAME and rec["pdf_page_index"] == 0
    assert rec["bbox"] == [72.0, 100.0, 400.0, 400.0]
    assert rec["read_notes"] == "The x axis is logarithmic."
    plain = _figures_db.figure_get(PID, "1-2")
    assert "bbox" not in plain and "read_notes" not in plain


def test_resolve_pdf_finds_pack_pdf(pack_env, monkeypatch, tmp_path):
    monkeypatch.setenv("GEOTECH_REFERENCES_DOCS", str(tmp_path))  # empty
    path, page = _figures_db.resolve_pdf(PID, "1-1")
    assert path == (pack_env / PDF_NAME).resolve() and page == 0


def test_resolve_pdf_falls_back_to_docs(tmp_path, monkeypatch):
    root = tmp_path / "packs"
    root.mkdir()
    make_pack(root, pdf=False)
    docs = tmp_path / "docs"
    docs.mkdir()
    _write_pdf(docs / PDF_NAME)
    monkeypatch.setenv(_packs.PACKS_ENV, str(root))
    monkeypatch.setenv("GEOTECH_REFERENCES_DOCS", str(docs))
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path / "db"))
    (tmp_path / "db").mkdir()
    path, _ = _figures_db.resolve_pdf(PID, "1-2")
    assert path == (docs / PDF_NAME).resolve()


def _private_db(monkeypatch, tmp_path):
    (tmp_path / "db").mkdir(exist_ok=True)
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path / "db"))


@pytest.mark.parametrize("where", ["catalog", "figure"])
@pytest.mark.parametrize("bad", ["../../outside.pdf", "absolute"])
def test_a_pdf_path_cannot_lead_outside_the_pack(tmp_path, monkeypatch,
                                                 where, bad):
    """A catalog naming its PDF by a path ('..', a drive or a folder) is
    skipped and named; the repo-relative step that would have reached the
    file is never taken for a pack; a good pack beside it still resolves."""
    outside = tmp_path / "outside.pdf"
    _write_pdf(outside)
    # the repo-relative step would reach `outside` through either path
    monkeypatch.setattr(_figures_db, "_REPO_ROOT", tmp_path / "a" / "b")
    if bad == "absolute":
        bad = str(outside)
    root = tmp_path / "packs"
    escaping = make_pack(root, "local_escaping", pdf=False)
    good = make_pack(root, "local_good")
    cat = _catalog()
    if where == "catalog":
        cat["pdf_path"] = bad
    else:
        cat["figures"][0]["pdf_path"] = bad
    _write_json(escaping / "figures_catalog.json", cat)
    monkeypatch.setenv(_packs.PACKS_ENV, str(root))
    monkeypatch.delenv("GEOTECH_REFERENCES_DOCS", raising=False)
    _private_db(monkeypatch, tmp_path)
    assert any("local_escaping" in p and "is not a bare file name; skipped"
               in p for p in _packs.problems())
    with pytest.raises(KeyError):
        _figures_db.resolve_pdf("local_escaping", "1-1")
    assert "local_escaping" not in {
        r["reference"] for r in _figures_db.list_indexed_figures()}
    assert "pdf_path must be a file name only" in _errors(escaping)
    path, _ = _figures_db.resolve_pdf("local_good", "1-1")
    assert path == (good / PDF_NAME).resolve()
    assert _figures_db.figure_get("local_good", "1-1")["pdf_path"] == PDF_NAME


def test_a_pack_pdf_is_never_found_relative_to_the_repo(tmp_path,
                                                        monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_pdf(repo / PDF_NAME)
    monkeypatch.setattr(_figures_db, "_REPO_ROOT", repo)
    root = tmp_path / "packs"
    make_pack(root, pdf=False)
    monkeypatch.setenv(_packs.PACKS_ENV, str(root))
    monkeypatch.delenv("GEOTECH_REFERENCES_DOCS", raising=False)
    _private_db(monkeypatch, tmp_path)
    with pytest.raises(FileNotFoundError) as e:
        _figures_db.resolve_pdf(PID, "1-1")
    assert f"'{PDF_NAME}' is not in the pack's folder or in " \
           "GEOTECH_REFERENCES_DOCS" in str(e.value)
    assert str(tmp_path) not in str(e.value)  # no host path in the message


@pytest.mark.parametrize("bad", ["../x.pdf", "sub/x.pdf", "C:\\x.pdf", ".."])
def test_pdf_files_take_bare_names_only(tmp_path, monkeypatch, bad):
    folder = make_pack(tmp_path, pdf=False)
    _write_json(folder / "pack.json", dict(_pack_json(), pdf_files=[bad]))
    assert "'pdf_files' must be a list of file names" in _errors(folder)
    monkeypatch.setenv(_packs.PACKS_ENV, str(tmp_path))
    assert [p for p, _ in _packs.packs()] == [PID]  # used, the entry ignored
    assert any("pdf_files" in p and "ignored" in p for p in _packs.problems())


# ---------------------------------------------------------------------------
# the key and the problems
# ---------------------------------------------------------------------------

def test_key_changes_with_a_pack_edit(tmp_path, monkeypatch):
    folder = make_pack(tmp_path, pdf=False)
    monkeypatch.setenv(_packs.PACKS_ENV, str(tmp_path))
    first = _retrieval_db.keyed_db_path("x.sqlite")
    assert first != _old_key("x.sqlite")
    assert _retrieval_db.keyed_db_path("x.sqlite") == first  # stable
    chapter = folder / "text" / "chapter01.json"
    data = _chapter()
    data["sections"][0]["body"] += " Edited."
    _write_json(chapter, data)
    second = _retrieval_db.keyed_db_path("x.sqlite")
    assert second != first
    # a copy that keeps the old size but a new modification time
    st = chapter.stat()
    os.utime(chapter, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))
    assert _retrieval_db.keyed_db_path("x.sqlite") != second


def test_pack_folder_or_folder_of_packs(tmp_path, monkeypatch):
    a = make_pack(tmp_path / "one", "local_a", pdf=False)
    make_pack(tmp_path / "many", "local_b", pdf=False)
    make_pack(tmp_path / "many", "local_c", pdf=False)
    monkeypatch.setenv(_packs.PACKS_ENV,
                       os.pathsep.join([str(a), str(tmp_path / "many")]))
    assert [p for p, _ in _packs.packs()] == ["local_a", "local_b", "local_c"]
    assert _packs.pack_dir("local_b") == tmp_path / "many" / "local_b"
    assert _packs.pack_dir("local_z") is None


def test_bad_packs_are_skipped_and_named(tmp_path, monkeypatch):
    make_pack(tmp_path / "r1", "local_good", pdf=False)
    make_pack(tmp_path / "r1", "noprefix", pdf=False)
    builtin = make_pack(tmp_path / "r1", "local_builtin", pdf=False)
    _write_json(builtin / "pack.json", dict(_pack_json(), id="gec_12"))
    dup = make_pack(tmp_path / "r2", "local_dup", pdf=False)
    _write_json(dup / "pack.json", dict(_pack_json(), id="local_good"))
    missing = tmp_path / "not_there"
    monkeypatch.setenv(_packs.PACKS_ENV, os.pathsep.join(
        [str(tmp_path / "r1"), str(tmp_path / "r2"), str(missing)]))
    assert [p for p, _ in _packs.packs()] == ["local_good"]
    probs = "\n".join(_packs.problems())
    assert "'gec_12' is a built-in" in probs
    assert "'noprefix' does not start with 'local_'" in probs
    assert "'local_good' repeats" in probs
    assert "not_there: not found" in probs
    assert [r for r, _ in _retrieval_db._iter_text_jsons()
            if r.startswith("local_")] == ["local_good"]


# ---------------------------------------------------------------------------
# the checker
# ---------------------------------------------------------------------------

def test_check_passes_the_good_pack(pack_env, capsys):
    assert packs.main(["check", str(pack_env)]) == 0
    out = capsys.readouterr().out
    assert "PASSED: 0 errors" in out
    assert "chapter 1 'Zorblite Embankments': found" in out
    assert "figure_get 1-1" in out


def _errors(folder, smoke=False):
    return "\n".join(packs.check_pack(folder, smoke=smoke)["errors"])


def test_check_catches_pack_json_errors(tmp_path):
    folder = make_pack(tmp_path, pdf=False)
    _write_json(folder / "pack.json", dict(_pack_json(), id="example"))
    assert "must start with 'local_'" in _errors(folder)
    _write_json(folder / "pack.json", dict(_pack_json(), id="local_other"))
    assert "is not the folder's name" in _errors(folder)
    meta = _pack_json()
    del meta["reference_title"]
    _write_json(folder / "pack.json", meta)
    assert "'reference_title' is missing" in _errors(folder)
    _write_json(folder / "pack.json", dict(_pack_json(), pdf_files=["a/b.pdf"]))
    assert "'pdf_files' must be a list of file names" in _errors(folder)
    (folder / "pack.json").write_text("{")
    assert "pack.json: cannot be read" in _errors(folder)


def test_check_catches_text_errors(tmp_path):
    folder = make_pack(tmp_path, pdf=False)
    bad = _chapter()
    del bad["sections"][0]["body"]
    _write_json(folder / "text" / "chapter01.json", bad)
    assert "missing key 'body'" in _errors(folder)
    _write_json(folder / "text" / "chapter01.json", _chapter(ref_id="EPM-02"))
    assert "reference_id 'EPM-02' is not pack.json's" in _errors(folder)
    _write_json(folder / "text" / "chapter01.json", _chapter())
    _write_json(folder / "text" / "chapter02.json", _chapter())
    assert "chapter 1 repeats" in _errors(folder)
    shutil.rmtree(folder / "text")
    assert "no chapter files" in _errors(folder)


def test_check_warns_on_print_fidelity(tmp_path):
    folder = make_pack(tmp_path, pdf=False)
    data = _chapter()
    data["sections"][0]["body"] = "No page marker in this made-up body."
    data["sections"][1]["equations"][0].pop("source")
    _write_json(folder / "text" / "chapter01.json", data)
    report = packs.check_pack(folder, smoke=False)
    assert not report["errors"]
    warnings = "\n".join(report["warnings"])
    assert "1.1: body has no page marker" in warnings
    assert "has a formula but no 'source'" in warnings


def test_check_catches_catalog_errors(tmp_path):
    folder = make_pack(tmp_path, pdf=False)
    cat = _catalog()
    cat["figures"][1]["figure_number"] = "Figure 1-1"
    cat["figures"][0]["read_notes"] = "x" * 501
    cat["figures"][0]["pdf_page_index"] = -1
    cat["pdf_path"] = "docs/" + PDF_NAME
    _write_json(folder / "figures_catalog.json", cat)
    errors = _errors(folder)
    assert "number repeats figures[0]" in errors
    assert "read_notes must be text of at most 500" in errors
    assert "pdf_page_index must be an integer 0 or more" in errors
    assert "pdf_path must be a file name only" in errors
    cat = _catalog()
    cat["figures"][0]["bbox"] = [10, 10, 5, 50]
    _write_json(folder / "figures_catalog.json", cat)
    assert "x0 < x1" in _errors(folder)


@pytest.mark.skipif(pymupdf is None, reason="PyMuPDF not installed")
def test_check_against_the_pdf(tmp_path):
    folder = make_pack(tmp_path)
    cat = _catalog()
    cat["figures"][0]["bbox"] = [72, 100, 700, 400]  # wider than the page
    cat["figures"][1]["pdf_page_index"] = 3  # the PDF has one page
    _write_json(folder / "figures_catalog.json", cat)
    errors = _errors(folder)
    assert "is not inside the page" in errors
    assert "is past the PDF's 1 pages" in errors
    cat = _catalog()
    cat["figures"][1]["figure_number"] = "1-9"  # not printed on the page
    _write_json(folder / "figures_catalog.json", cat)
    report = packs.check_pack(folder, smoke=False)
    assert not report["errors"]
    assert any("'1-9' is not printed" in w for w in report["warnings"])
    cat["figures"][1]["page_estimated"] = True
    _write_json(folder / "figures_catalog.json", cat)
    report = packs.check_pack(folder, smoke=False)
    assert not any("'1-9'" in w for w in report["warnings"])


def test_check_refuses_a_pack_inside_the_package():
    inside = _packs._PACKAGE_DIR / "dm7_1"
    assert "inside the installed geotech_references" in \
        packs.location_problem(inside)


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_check_refuses_a_public_repo_work_tree(tmp_path):
    repo = tmp_path / "clone"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "remote", "add", "origin",
                    "https://example.invalid/someone/GeotechStaffEngineer.git"],
                   check=True)
    folder = make_pack(repo / "packs", pdf=False)
    assert "public repository geotechstaffengineer" in _errors(folder)
    subprocess.run(["git", "-C", str(repo), "remote", "set-url", "origin",
                    "https://example.invalid/someone/private-deploy.git"],
                   check=True)
    assert "public repository" not in _errors(folder)


def test_new_writes_a_skeleton(tmp_path, capsys):
    folder = tmp_path / "local_new_manual"
    assert packs.main(["new", str(folder), "--title", "New Made-up Manual",
                       "--pdf", "/somewhere/new manual.pdf"]) == 0
    meta = json.loads((folder / "pack.json").read_text())
    assert meta["id"] == "local_new_manual"
    assert meta["pdf_files"] == ["new manual.pdf"]
    assert (folder / "text").is_dir()
    assert packs.main(["check", str(folder), "--no-smoke"]) == 1
    assert "no chapter files" in capsys.readouterr().out
    assert packs.main(["new", str(tmp_path / "plain"), "--title", "x"]) == 1


def test_list(tmp_path, monkeypatch, capsys):
    make_pack(tmp_path, pdf=False)
    make_pack(tmp_path, "noprefix", pdf=False)
    monkeypatch.setenv(_packs.PACKS_ENV, str(tmp_path))
    assert packs.main(["list"]) == 0
    out = capsys.readouterr().out
    assert f"{PID}: {TITLE} -- 1 chapters, 3 sections, 2 figures" in out
    assert "skipped:" in out and "noprefix" in out


def test_module_runs_as_a_script(tmp_path):
    folder = make_pack(tmp_path, pdf=False)
    done = subprocess.run(
        [sys.executable, "-m", "geotech_references.packs", "check",
         str(folder), "--no-smoke"], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    _write_json(folder / "pack.json", dict(_pack_json(), id="bad"))
    done = subprocess.run(
        [sys.executable, "-m", "geotech_references.packs", "check",
         str(folder), "--no-smoke"], capture_output=True, text=True)
    assert done.returncode == 1


# ---------------------------------------------------------------------------
# one schema validator
# ---------------------------------------------------------------------------

def test_audit_script_uses_the_package_validator():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    try:
        import audit_chapter_text
    finally:
        sys.path.pop(0)
    assert audit_chapter_text.validate_schema is _schema.validate_schema
    assert audit_chapter_text.SECTION_ID is _schema.SECTION_ID


def test_validator_passes_every_builtin_chapter():
    bad = {}
    for jf in sorted(_packs._PACKAGE_DIR.glob("*/text/*.json")):
        errs = _schema.validate_schema(json.loads(jf.read_text("utf-8")))
        if errs:
            bad[str(jf)] = errs
    assert bad == {}


@pytest.mark.skipif(pymupdf is None, reason="PyMuPDF not installed")
def test_build_figure_catalog_for_a_pack(tmp_path):
    """scripts/build_figure_catalog.py --pack reads a made-up List of
    Figures, finds each caption's page, writes the file name only and keeps
    a figure's bbox / read_notes."""
    folder = make_pack(tmp_path, pdf=False)
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "LIST OF FIGURES")
    page.insert_text((72, 100), "Figure 1-1 Zorblite settlement chart ...... 2")
    page.insert_text((72, 120), "Figure 1-2 Wet zorblite settlement ...... 3")
    doc.new_page().insert_text((72, 72), "CHAPTER 1")
    for text, num in (("Figure 1-1 Zorblite settlement chart", "2"),
                      ("Figure 1-2 Wet zorblite settlement", "3")):
        page = doc.new_page()
        page.insert_text((72, 400), text)
        page.insert_text((300, 770), num)
    doc.save(str(folder / PDF_NAME))
    doc.close()
    script = Path(__file__).resolve().parents[1] / "scripts" / \
        "build_figure_catalog.py"
    done = subprocess.run([sys.executable, str(script), "--pack", str(folder)],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    cat = json.loads((folder / "figures_catalog.json").read_text())
    assert cat["pdf_path"] == PDF_NAME and cat["package"] == PID
    figs = {f["figure_number"]: f for f in cat["figures"]}
    assert figs["1-1"]["pdf_page_index"] == 2
    assert figs["1-2"]["pdf_page_index"] == 3
    assert figs["1-1"]["read_notes"] == "The x axis is logarithmic."
    assert "bbox" not in figs["1-2"]
    assert not packs.check_pack(folder, smoke=False)["errors"]


def test_no_pack_is_tracked_in_this_repo():
    """A pack is private deployment data: no pack.json in the public repo."""
    root = Path(__file__).resolve().parents[1]
    try:
        out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True,
                             text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("not a git checkout")
    tracked = [f for f in out.splitlines() if Path(f).name == "pack.json"]
    assert tracked == []


def test_pack_records_and_feature_flag(tmp_path, monkeypatch):
    assert _retrieval_db.pack_dirs is _packs.pack_dirs
    monkeypatch.delenv(_packs.PACKS_ENV, raising=False)
    assert _packs.pack_records() == []
    folder = make_pack(tmp_path, pdf=False)
    monkeypatch.setenv(_packs.PACKS_ENV, str(tmp_path))
    (rec,) = _packs.pack_records()
    assert rec["id"] == PID and rec["title"] == TITLE
    assert rec["reference_id"] == REF_ID and rec["edition"]
    assert rec["files"] == ["pack.json", "text/chapter01.json",
                            "figures_catalog.json"]
    _write_json(folder / "text" / "chapter01.json", _chapter(chapter=2))
    assert _packs.pack_records()[0]["sha"] != rec["sha"]
