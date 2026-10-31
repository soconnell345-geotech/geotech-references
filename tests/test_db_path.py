"""REF-55: each copy of the package keeps its own temp-folder databases.

Under one fixed file name, two checkouts on one machine, or two
environments sharing /tmp on a cluster, served each other's text.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from geotech_references import _figures_db, _retrieval_db
from geotech_references._retrieval_db import keyed_db_path

NAME = "geotech_references_fts.sqlite"


def test_two_package_folders_get_different_databases(tmp_path):
    a = keyed_db_path(NAME, tmp_path / "a")
    b = keyed_db_path(NAME, tmp_path / "b")
    assert a != b
    assert a.parent == b.parent == Path(tempfile.gettempdir())


def test_one_package_folder_keeps_one_database(tmp_path):
    (tmp_path / "a" / "sub").mkdir(parents=True)
    first = keyed_db_path(NAME, tmp_path / "a")
    assert keyed_db_path(NAME, tmp_path / "a") == first
    # the same folder spelled another way
    assert keyed_db_path(NAME, tmp_path / "a" / "sub" / "..") == first


def test_text_and_figure_databases_are_keyed_to_this_copy():
    text, figs = _retrieval_db._db_path(), _figures_db._db_path()
    assert text == _retrieval_db._db_path()
    assert text.name.startswith("geotech_references_fts_")
    assert figs.name.startswith("geotech_references_figures_fts_")
    # one copy of the package, one key on both files
    assert text.stem.rsplit("_", 1)[1] == figs.stem.rsplit("_", 1)[1]


def test_a_database_under_the_old_fixed_name_is_left_alone(
        tmp_path, monkeypatch):
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    old = tmp_path / _figures_db._DB_NAME
    old.write_bytes(b"an older library's database")
    built = _figures_db._ensure_db()
    assert built.parent == tmp_path
    assert built != old
    assert old.read_bytes() == b"an older library's database"
