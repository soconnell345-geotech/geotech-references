"""REF-56: the search databases are built where no other process sees them half
built, and moved into place in one step.

Before REF-56 ``_build_db`` deleted the database and rebuilt it in place, so
a second process starting at the same moment could open a half-built file
("table sections already exists", "disk I/O error", or a table with only some
references in it), and a build that stopped part way left no database at all.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

from geotech_references import _atomic_db, _figures_db, _retrieval, _retrieval_db

ROOT = Path(__file__).resolve().parents[1]

QUERIES = ["settlement", "drilled shaft side resistance", "Nordlund",
           "passive earth pressure"]

# Run in a fresh interpreter whose temp folder is the test's empty folder.
# Every process waits for the same start time, and each source file read
# is slowed a little, so the builds overlap however fast the machine is.
_CHILD = textwrap.dedent("""
    import json, sys, time
    from geotech_references import _retrieval, _retrieval_db, _figures_db

    start = float(sys.argv[1])
    queries = json.loads(sys.argv[2])
    real = _retrieval.section_entries

    def slow(data):
        time.sleep(0.003)
        return real(data)

    _retrieval.section_entries = slow
    while time.time() < start:
        time.sleep(0.001)
    out = {"refs": [], "hits": {}, "figs": 0, "error": None}
    try:
        out["refs"] = sorted(r["reference"] for r in
                             _retrieval_db.list_indexed_references())
        for q in queries:
            out["hits"][q] = [[h["reference"], h["section_id"]] for h in
                              _retrieval_db.reference_search(q, limit=10)]
        out["figs"] = sum(r["n_figures"] for r in
                          _figures_db.list_indexed_figures())
    except Exception as exc:  # reported, so the parent can say which
        out["error"] = f"{type(exc).__name__}: {exc}"
    print(json.dumps(out))
""")


def _env(tmp: Path) -> dict:
    env = dict(os.environ)
    for var in ("TMPDIR", "TEMP", "TMP"):
        env[var] = str(tmp)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(ROOT)] + [p for p in env.get("PYTHONPATH", "").split(os.pathsep)
                       if p])
    return env


def _expected() -> dict:
    """The same answers from this process's (complete) databases."""
    return {
        "refs": sorted(r["reference"] for r in
                       _retrieval_db.list_indexed_references()),
        "hits": {q: [[h["reference"], h["section_id"]] for h in
                     _retrieval_db.reference_search(q, limit=10)]
                 for q in QUERIES},
        "figs": sum(r["n_figures"] for r in _figures_db.list_indexed_figures()),
        "error": None,
    }


@pytest.mark.parametrize("n", [4])
def test_processes_started_at_once_on_an_empty_temp_folder_agree(tmp_path, n):
    cache = tmp_path / "tmp"
    cache.mkdir()
    script = tmp_path / "child.py"
    script.write_text(_CHILD, encoding="utf-8")
    start = time.time() + 3.0
    procs = [subprocess.Popen(
        [sys.executable, str(script), repr(start), json.dumps(QUERIES)],
        env=_env(cache), cwd=str(tmp_path),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for _ in range(n)]
    results = []
    for p in procs:
        out, err = p.communicate(timeout=300)
        assert p.returncode == 0, err
        results.append(json.loads(out.strip().splitlines()[-1]))

    expected = _expected()
    for r in results:
        assert r == expected
    # one database of each kind, and no build file left behind
    names = sorted(p.name for p in cache.iterdir())
    assert len([x for x in names if x.endswith(".sqlite")]) == 2, names
    assert not [x for x in names if "building" in x or "journal" in x], names


@pytest.fixture
def private_db(tmp_path, monkeypatch):
    """Point the text database at an empty folder of the test's own."""
    db = tmp_path / "fts.sqlite"
    monkeypatch.setattr(_retrieval_db, "_db_path", lambda: db)
    monkeypatch.setattr(_atomic_db, "_PENDING", {})
    return db


@pytest.mark.skipif(os.name != "posix", reason="POSIX file modes")
def test_other_users_can_read_the_database(private_db):
    _retrieval_db._ensure_db()
    assert private_db.stat().st_mode & 0o044 == 0o044


def _search(q="settlement"):
    return [(h["reference"], h["section_id"])
            for h in _retrieval_db.reference_search(q, limit=10)]


def test_an_interrupted_build_leaves_the_old_database_usable(private_db,
                                                              monkeypatch):
    _retrieval_db._ensure_db()
    before = _search()
    assert before
    built = private_db.stat().st_mtime_ns

    real, calls = _retrieval.section_entries, []

    def stop_part_way(data):
        calls.append(1)
        if len(calls) > 20:
            raise KeyboardInterrupt("stopped part way")
        return real(data)

    monkeypatch.setattr(_retrieval, "section_entries", stop_part_way)
    with pytest.raises(KeyboardInterrupt):
        _retrieval_db.rebuild_db()
    monkeypatch.setattr(_retrieval, "section_entries", real)

    assert private_db.stat().st_mtime_ns == built
    assert _search() == before
    assert _atomic_db.temp_files(private_db) == []
    assert sorted(p.name for p in private_db.parent.iterdir()) == [
        private_db.name]


def test_a_killed_build_leaves_the_old_database_and_its_file_is_swept(
        private_db, monkeypatch, tmp_path):
    _retrieval_db._ensure_db()
    before = _search()
    # a build in another process killed part way: a half-written file
    left = private_db.parent / f".{private_db.name}.abc123.building"
    conn = sqlite3.connect(str(left))
    conn.execute("CREATE TABLE sections (x INTEGER)")
    conn.commit()
    conn.close()
    assert _search() == before          # never read
    # the next build removes it once it is old enough to be a dead one's
    old = time.time() - _atomic_db.STALE_SECONDS - 60
    os.utime(left, (old, old))
    _retrieval_db.rebuild_db()
    assert not left.exists()
    assert _search() == before


def test_a_fresh_build_file_of_another_process_is_not_swept(private_db):
    busy = private_db.parent / f".{private_db.name}.busy.building"
    busy.write_bytes(b"")
    _retrieval_db.rebuild_db()
    assert busy.exists()                # might be another live build


def test_a_held_file_on_windows_never_raises_and_is_moved_in_later(
        private_db, monkeypatch):
    """os.replace refuses to replace a file another process has open."""
    _retrieval_db._ensure_db()
    expected = _search()
    # the database there is out of date and held open by "another process"
    os.utime(private_db, (1.0, 1.0))
    assert _retrieval_db._needs_rebuild(private_db)
    real_replace = os.replace

    def refuse(src, dst):
        raise PermissionError(32, "being used by another process")

    monkeypatch.setattr(_atomic_db, "REPLACE_RETRY_SECONDS", 0.05)
    monkeypatch.setattr(_atomic_db.os, "replace", refuse)
    # our own complete copy is read; the file at the real name is untouched
    used = _retrieval_db._ensure_db()
    assert used != private_db
    assert used.exists()
    pending = _atomic_db.temp_files(private_db)
    assert pending == [used]
    # later calls read the same copy instead of building again
    assert _retrieval_db._ensure_db() == used

    # the lock is gone: the next call moves the copy into place
    monkeypatch.setattr(_atomic_db.os, "replace", real_replace)
    assert _retrieval_db._ensure_db() == private_db
    assert _atomic_db.temp_files(private_db) == []
    assert _search() == expected


def test_a_held_file_that_is_now_current_is_used_and_the_copy_removed(
        private_db, monkeypatch):
    _retrieval_db._ensure_db()
    expected = _search()

    def refuse(src, dst):
        raise PermissionError(5, "access denied")

    monkeypatch.setattr(_atomic_db, "REPLACE_RETRY_SECONDS", 0.05)
    monkeypatch.setattr(_atomic_db.os, "replace", refuse)
    # another process put a current database there while this one built
    assert _retrieval_db._build_db(private_db) == private_db
    assert _atomic_db.temp_files(private_db) == []
    assert _search() == expected


def test_a_held_file_is_retried_until_the_reader_lets_go(private_db,
                                                         monkeypatch):
    real_replace, tries = os.replace, []

    def busy_twice(src, dst):
        tries.append(1)
        if len(tries) <= 2:
            raise PermissionError(32, "being used by another process")
        return real_replace(src, dst)

    monkeypatch.setattr(_atomic_db.os, "replace", busy_twice)
    assert _retrieval_db._build_db(private_db) == private_db
    assert len(tries) == 3
    assert _atomic_db.temp_files(private_db) == []


def test_pending_copies_are_removed_when_the_process_ends(tmp_path,
                                                          monkeypatch):
    monkeypatch.setattr(_atomic_db, "_PENDING", {})
    copy = tmp_path / ".x.sqlite.1.building"
    copy.write_bytes(b"")
    _atomic_db._PENDING[str(tmp_path / "x.sqlite")] = copy
    _atomic_db._cleanup_pending()
    assert not copy.exists()


def test_the_figure_database_is_built_the_same_way(tmp_path, monkeypatch):
    db = tmp_path / "figs.sqlite"
    monkeypatch.setattr(_figures_db, "_db_path", lambda: db)
    _figures_db._ensure_db()
    n = sum(r["n_figures"] for r in _figures_db.list_indexed_figures())
    def stop(conn):
        conn.execute("CREATE TABLE figures (x INTEGER)")
        raise RuntimeError("stopped part way")

    monkeypatch.setattr(_figures_db, "_fill_db", stop)
    with pytest.raises(RuntimeError):
        _figures_db.rebuild_db()
    monkeypatch.undo()
    monkeypatch.setattr(_figures_db, "_db_path", lambda: db)
    assert sum(r["n_figures"] for r in _figures_db.list_indexed_figures()) == n
    assert sorted(p.name for p in tmp_path.iterdir()) == ["figs.sqlite"]
