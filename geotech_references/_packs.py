"""Local reference packs (BACKLOG REF-64).

A pack is a deployment's own reference, kept outside this package and its
public repository, in the library's own layout minus the Python::

    <pack folder>/               # folder name = pack id, e.g. local_agency_gdm
      pack.json                  # id, reference_id, reference_title, edition, ...
      text/chapterNN.json        # chapter_schema.json (this package), unchanged
      figures_catalog.json       # optional; pdf_path is a file name only
      <the PDF>                  # optional here; else found as built-ins are

``GEOTECH_REFERENCES_PACKS`` names one or more folders, separated by
``os.pathsep``. Each is a pack (it holds ``pack.json``) or a folder of packs.
It is read at call time, as ``GEOTECH_REFERENCES_DOCS`` is, so the search
databases (:mod:`._retrieval_db`, :mod:`._figures_db`) index the packs beside
the built-in references.

A pack is skipped, and named in :func:`problems`, when its ``pack.json``
cannot be read, its id lacks the ``local_`` prefix, its id is a built-in
reference's name, or an earlier pack has the same id. Unset (or with no
valid pack), every function here returns nothing and the library behaves
exactly as it did before packs existed.

A pack names its PDFs by bare file name only (``pdf_files``, a catalog's
``pdf_path``), so no path read from a pack leads outside it: a catalog
that gives a folder, ``..`` or a drive is skipped by the figure index and
named in :func:`problems`, and a pack's PDF is looked for only in the
pack's folder and in ``GEOTECH_REFERENCES_DOCS``.

A pack file cannot break the search indexes: one the indexes cannot take
(unreadable JSON, a list or an object where text belongs) is skipped and
named in :func:`problems`, and each pack file is indexed under its own
SAVEPOINT, so one that fails anyway is rolled back and named while the
built-ins and the other packs still index.

``docs/REFERENCE_PACKS.md`` describes the format and how to check a pack
(``python -m geotech_references.packs check <dir>``).
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from pathlib import Path

_PACKAGE_DIR = Path(__file__).parent

#: The setting naming where packs live.
PACKS_ENV = "GEOTECH_REFERENCES_PACKS"
#: Every pack id starts with this, so it never collides with a built-in (or
#: a future built-in) and every citation shows it is the deployment's own.
PACK_PREFIX = "local_"
PACK_FILE = "pack.json"
CATALOG_NAME = "figures_catalog.json"


def bare_file_name(value) -> bool:
    """True for a file name with no folder part: no separator, no drive,
    not ``.`` or ``..``. Pack PDFs are named this way, so a name read from a
    pack can only lead to a file in a folder the library chose."""
    return (isinstance(value, str) and value.strip() != ""
            and value not in (".", "..")
            and not any(c in value for c in "/\\:"))


def builtin_ids() -> set[str]:
    """The names of the built-in reference folders in this package."""
    return {p.name for p in _PACKAGE_DIR.iterdir()
            if p.is_dir() and not p.name.startswith(("_", "."))}


def _roots() -> list[Path]:
    raw = os.environ.get(PACKS_ENV, "")
    return [Path(part).expanduser() for part in raw.split(os.pathsep)
            if part.strip()]


def _candidates(root: Path) -> tuple[list[Path], list[str]]:
    """The pack folders ``root`` names, and what was wrong with it."""
    if (root / PACK_FILE).is_file():
        return [root], []
    if root.is_dir():
        return sorted(p for p in root.iterdir()
                      if p.is_dir() and (p / PACK_FILE).is_file()), []
    return [], [f"{root}: not found (named in {PACKS_ENV})"]


def read_pack_json(folder: Path) -> dict:
    """``folder``'s ``pack.json`` as a dict (raises OSError / ValueError)."""
    data = json.loads((folder / PACK_FILE).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("pack.json is not a JSON object")
    return data


def scan() -> tuple[list[tuple[str, Path]], list[str]]:
    """``([(pack id, folder), ...], [problem, ...])`` for the current setting.

    The id is ``pack.json``'s ``id`` (the folder name when it has none).
    """
    packs, keyed = _scan()
    return packs, [message for _, message in keyed]


def _scan() -> tuple[list[tuple[str, Path]], list[tuple[str, str]]]:
    """:func:`scan`, each problem with the pack it belongs to: the pack's
    id (``pack.json``'s, else its folder's name), or the setting's folder
    for one that is not there. A folder named as a built-in reference is
    keyed by its whole path, so its problems are never filed under the
    built-in's id (2026-11-10 review follow-up)."""
    packs: list[tuple[str, Path]] = []
    problems: list[tuple[str, str]] = []
    builtins = None
    seen: dict[str, Path] = {}

    def key_of(folder: Path) -> str:
        return str(folder) if folder.name in builtins else folder.name

    for root in _roots():
        folders, root_problems = _candidates(root)
        problems.extend((str(root), p) for p in root_problems)
        for folder in folders:
            if builtins is None:
                builtins = builtin_ids()
            try:
                data = read_pack_json(folder)
            except (OSError, ValueError) as e:
                problems.append((key_of(folder), f"{folder}: pack.json "
                                 f"unreadable ({e}); skipped"))
                continue
            pid = str(data.get("id") or folder.name)
            if pid in builtins:
                problems.append((key_of(folder), f"{folder}: id '{pid}' is a "
                                 "built-in reference's name; skipped"))
                continue
            if not pid.startswith(PACK_PREFIX):
                problems.append((pid, f"{folder}: id '{pid}' does not start "
                                 f"with '{PACK_PREFIX}'; skipped"))
                continue
            if pid in seen:
                problems.append((pid, f"{folder}: id '{pid}' repeats the "
                                 f"pack at {seen[pid]}; skipped"))
                continue
            pdfs = data.get("pdf_files") or []
            bad = ([p for p in pdfs if not bare_file_name(p)]
                   if isinstance(pdfs, list) else [pdfs])
            if bad:
                problems.append((pid, f"{folder}: pack.json pdf_files "
                                 f"{bad!r}: not bare file names; ignored"))
            seen[pid] = folder
            packs.append((pid, folder))
    return packs, problems


def packs() -> list[tuple[str, Path]]:
    """``(pack id, folder)`` of every valid pack, in the setting's order."""
    return scan()[0]


def pack_dirs() -> list[Path]:
    """The folder of every valid pack."""
    return [folder for _, folder in packs()]


def pack_dir(pack_id: str) -> Path | None:
    """The folder of pack ``pack_id``, or None when there is no such pack."""
    for pid, folder in packs():
        if pid == pack_id:
            return folder
    return None


def problems() -> list[str]:
    """What the current setting names that is not a usable pack, or a pack
    file the search indexes skip, and why."""
    return scan()[1] + file_problems()


def problems_by_pack() -> dict[str, list[str]]:
    """:func:`problems` by the pack each belongs to (its id; the folder's
    name for a pack whose ``pack.json`` gives no usable id; the setting's
    folder for one that is not there). The search results quote them, so a
    skipped pack or pack file is not met with silence (2026-11-10 review,
    core-10). Empty with no pack setting."""
    out: dict[str, list[str]] = {}
    for key, message in _scan()[1] + _file_problems():
        out.setdefault(key, []).append(message)
    return out


#: What SQLite stores as given. Anything else (a list, an object) in a field
#: the search indexes store would fail the whole build, built-ins included.
_SCALARS = (str, int, float, type(None))
#: What indexing one pack file can raise; the file is then rolled back.
PACK_FILE_ERRORS = (sqlite3.Error, TypeError, ValueError, AttributeError,
                    KeyError, IndexError)
#: Pack files this process could not index, by path (see index_pack_file).
_INDEX_FAILURES: dict[str, str] = {}


def _kind(value) -> str:
    return {list: "a list", dict: "an object"}.get(type(value),
                                                   type(value).__name__)


def chapter_problem(data) -> str | None:
    """Why the text index skips a pack's chapter file, or None."""
    if not isinstance(data, dict):
        return "not a JSON object"
    for key in ("reference_title", "chapter", "chapter_title"):
        if not isinstance(data.get(key), _SCALARS):
            return f"'{key}' is {_kind(data[key])}, not text"
    from . import _retrieval
    try:
        entries = _retrieval.section_entries(data)
    except PACK_FILE_ERRORS as e:
        return f"its sections cannot be read ({type(e).__name__}: {e})"
    for entry in entries:
        sec = entry["section"]
        for key in ("section_id", "title", "summary", "body", "applicability"):
            if not isinstance(sec.get(key), _SCALARS):
                return (f"section {sec.get('section_id')!r}: '{key}' is "
                        f"{_kind(sec[key])}, not text")
        for key in ("equations", "figures", "tables"):  # read back as lists
            if not isinstance(sec.get(key), (list, type(None))):
                return (f"section {sec.get('section_id')!r}: '{key}' is "
                        f"{_kind(sec[key])}, not a list")
    return None


def catalog_problem(data) -> str | None:
    """Why the figure index skips a pack's catalog, or None."""
    if not isinstance(data, dict):
        return "not a JSON object"
    figures = data.get("figures", [])
    if not isinstance(figures, list):
        return f"'figures' is {_kind(figures)}, not a list"
    figures = [f for f in figures if isinstance(f, dict)]
    for name in [data.get("pdf_path")] + [f.get("pdf_path") for f in figures]:
        if name not in (None, "") and not bare_file_name(name):
            return f"pdf_path {name!r} is not a bare file name"
    for key in ("reference_id", "reference_title", "volume"):
        if not isinstance(data.get(key), _SCALARS):
            return f"'{key}' is {_kind(data[key])}, not text"
    for fig in figures:
        for key in ("figure_number", "caption", "description", "chapter",
                    "reference_id", "volume", "pdf_page_index",
                    "printed_page", "read_notes"):
            if not isinstance(fig.get(key), _SCALARS):
                return (f"figure {fig.get('figure_number')!r}: '{key}' is "
                        f"{_kind(fig[key])}, not text or a number")
    return None


def index_pack_file(cur, path: Path, index) -> None:
    """Run ``index()``, the INSERTs of one pack file, under a SAVEPOINT on
    cursor ``cur``. A file that fails anyway is rolled back and named in
    :func:`problems`, and the built-ins and the other packs still index."""
    cur.execute("SAVEPOINT pack_file")
    try:
        index()
    except PACK_FILE_ERRORS as e:
        cur.execute("ROLLBACK TO pack_file")
        _INDEX_FAILURES[str(path)] = f"{type(e).__name__}: {e}"
    else:
        _INDEX_FAILURES.pop(str(path), None)
    cur.execute("RELEASE pack_file")


def file_problems() -> list[str]:
    """Each pack file the search indexes skip, and why: the same checks the
    indexes run, so every process names the same files."""
    return [message for _, message in _file_problems()]


def _file_problems() -> list[tuple[str, str]]:
    """:func:`file_problems`, each with its pack's id."""
    out: list[tuple[str, str]] = []
    files = [(pid, jf, chapter_problem) for pid, jf in text_jsons()]
    files += [(pid, cat, catalog_problem) for pid, cat in catalogs()]
    for pid, path, problem in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            out.append((pid, f"{path}: not readable JSON ({e}); skipped"))
            continue
        why = problem(data)
        if why is None and str(path) in _INDEX_FAILURES:
            why = f"could not be indexed ({_INDEX_FAILURES[str(path)]})"
        if why:
            out.append((pid, f"{path}: {why}; skipped"))
    return out


def text_jsons() -> list[tuple[str, Path]]:
    """``(pack id, chapter file)`` for every pack's ``text/*.json``."""
    out: list[tuple[str, Path]] = []
    for pid, folder in packs():
        text_dir = folder / "text"
        if text_dir.is_dir():
            out.extend((pid, jf) for jf in sorted(text_dir.glob("*.json")))
    return out


def catalogs() -> list[tuple[str, Path]]:
    """``(pack id, figures_catalog.json)`` for every pack that has one."""
    return [(pid, folder / CATALOG_NAME) for pid, folder in packs()
            if (folder / CATALOG_NAME).is_file()]


def indexed_files(folder: Path) -> list[Path]:
    """The files of one pack the search databases read."""
    files = [folder / PACK_FILE]
    if (folder / "text").is_dir():
        files.extend(sorted((folder / "text").glob("*.json")))
    if (folder / CATALOG_NAME).is_file():
        files.append(folder / CATALOG_NAME)
    return files


def key_part() -> str:
    """A short hash of the pack set: each indexed file's path, size and
    modification time. Empty when there is no valid pack, so the database
    key is then exactly what it was before packs existed."""
    found = packs()
    if not found:
        return ""
    h = hashlib.sha1()
    for pid, folder in found:
        h.update(f"{pid}\0".encode())
        for f in indexed_files(folder):
            try:
                st = f.stat()
            except OSError:
                continue
            path = os.path.normcase(str(f.resolve()))
            h.update(f"{path}|{st.st_size}|{st.st_mtime_ns}\0".encode())
    return h.hexdigest()[:12]


def pack_records() -> list[dict]:
    """One record per valid pack for an app's build record (REF-64):
    ``{"id", "title", "reference_id", "edition", "files", "sha"}``, where
    ``files`` are the indexed files' paths inside the pack and ``sha`` is a
    sha256 over their contents, so a reviewer can tell which edition of a
    pack was in force. Empty when there is no valid pack."""
    out = []
    for pid, folder in packs():
        try:
            meta = read_pack_json(folder)
        except (OSError, ValueError):
            meta = {}
        h = hashlib.sha256()
        files = []
        for f in indexed_files(folder):
            rel = f.relative_to(folder).as_posix()
            try:
                data = f.read_bytes()
            except OSError:
                continue
            files.append(rel)
            h.update(rel.encode() + b"\0" + data + b"\0")
        out.append({"id": pid, "title": meta.get("reference_title", ""),
                    "reference_id": meta.get("reference_id", ""),
                    "edition": meta.get("edition") or meta.get("date") or "",
                    "files": files, "sha": h.hexdigest()})
    return out
