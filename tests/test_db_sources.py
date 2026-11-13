"""What the search databases are built from (2026-11-10 review, core-11
and core-12).

core-11: a database was rebuilt only when a source file was newer than it,
so a chapter file or catalog deleted, added with an older date, or restored
from a copy kept the old text. Each database now keeps the signature of
its source files (``build_meta``) and is rebuilt when they differ.

core-12: a built-in chapter file or catalog the build could not read was
left out without a word. It now fails the build, naming the file, and the
database already there is kept. A local pack's file is still skipped and
named (``tests/test_packs.py``).

The databases these tests build go to the test's own folder; no package
file is changed (the extra and missing files are made in ``tmp_path``).
"""

from __future__ import annotations

import os
import shutil
import sqlite3

import pytest

from geotech_references import _atomic_db, _figures_db, _retrieval_db


@pytest.fixture
def private_dbs(tmp_path, monkeypatch):
    """Point both databases at the test's own folder."""
    text, figs = tmp_path / "fts.sqlite", tmp_path / "figs.sqlite"
    monkeypatch.setattr(_retrieval_db, "_db_path", lambda: text)
    monkeypatch.setattr(_figures_db, "_db_path", lambda: figs)
    monkeypatch.setattr(_atomic_db, "_PENDING", {})
    return text, figs


MODULES = {"text": (_retrieval_db, "_iter_text_jsons"),
           "figures": (_figures_db, "_iter_catalogs")}


def _sources(kind):
    module, name = MODULES[kind]
    return getattr(module, name)()


def _path_of(kind, item):
    return item[1] if kind == "text" else item


def _with(kind, item_path):
    """A source list entry for ``item_path`` in ``kind``'s shape."""
    return ("gec_12", item_path) if kind == "text" else item_path


def _ensure(kind):
    module, _ = MODULES[kind]
    return module._ensure_db()


@pytest.mark.parametrize("kind", ["text", "figures"])
def test_the_database_records_its_sources(private_dbs, kind):
    db = _ensure(kind)
    module, _ = MODULES[kind]
    version, signature = _retrieval_db.db_meta(db)
    assert version == module._SCHEMA_VERSION
    paths = [_path_of(kind, s) for s in _sources(kind)]
    assert signature == _retrieval_db.source_state(paths)[1]
    assert not module._needs_rebuild(db)


@pytest.mark.parametrize("kind", ["text", "figures"])
def test_a_deleted_source_file_rebuilds(private_dbs, monkeypatch, kind):
    db = _ensure(kind)
    module, name = MODULES[kind]
    fewer = _sources(kind)[:-1]
    monkeypatch.setattr(module, name, lambda: fewer)
    # no file is newer than the database: the date rule alone said current
    assert db.stat().st_mtime >= module._newest_source_mtime()
    assert module._needs_rebuild(db)


@pytest.mark.parametrize("kind", ["text", "figures"])
def test_an_added_file_with_an_older_date_rebuilds(private_dbs, monkeypatch,
                                                   tmp_path, kind):
    db = _ensure(kind)
    module, name = MODULES[kind]
    real = _sources(kind)
    copy = tmp_path / "restored.json"
    shutil.copyfile(_path_of(kind, real[0]), copy)
    os.utime(copy, (1.0, 1.0))  # a copy restored with its old date
    monkeypatch.setattr(module, name, lambda: real + [_with(kind, copy)])
    assert db.stat().st_mtime >= module._newest_source_mtime()
    assert module._needs_rebuild(db)


@pytest.mark.parametrize("kind", ["text", "figures"])
def test_a_database_without_a_signature_rebuilds(tmp_path, kind):
    module, _ = MODULES[kind]
    old = tmp_path / "old.sqlite"
    conn = sqlite3.connect(str(old))
    conn.execute("CREATE TABLE x (y INTEGER)")
    conn.execute(f"PRAGMA user_version = {module._SCHEMA_VERSION}")
    conn.commit()
    conn.close()
    assert _retrieval_db.db_meta(old) == (module._SCHEMA_VERSION, None)
    assert module._needs_rebuild(old)


@pytest.mark.parametrize("kind", ["text", "figures"])
def test_an_unreadable_builtin_file_fails_the_build(private_dbs, monkeypatch,
                                                     tmp_path, kind):
    db = _ensure(kind)
    built = db.stat().st_mtime_ns
    module, name = MODULES[kind]
    bad = tmp_path / "broken.json"
    bad.write_text('{"chapter": 1, "sections": [', encoding="utf-8")
    real = _sources(kind)
    monkeypatch.setattr(module, name, lambda: [_with(kind, bad)] + real)
    with pytest.raises(RuntimeError) as e:
        module._fill_db(sqlite3.connect(":memory:"))
    assert str(bad) in str(e.value) and "was not built" in str(e.value)
    # a rebuild fails the same way and keeps the database that was there
    with pytest.raises(RuntimeError):
        module.rebuild_db()
    assert db.stat().st_mtime_ns == built
    assert _atomic_db.temp_files(db) == []
