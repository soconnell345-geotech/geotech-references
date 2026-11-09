"""Local reference packs (BACKLOG REF-64).

A pack is a deployment's own reference, kept outside this package and its
public repository, in the library's own layout minus the Python::

    <pack folder>/               # folder name = pack id, e.g. local_agency_gdm
      pack.json                  # id, reference_id, reference_title, edition, ...
      text/chapterNN.json        # scripts/chapter_schema.json, unchanged
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

``docs/REFERENCE_PACKS.md`` describes the format and how to check a pack
(``python -m geotech_references.packs check <dir>``).
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

_PACKAGE_DIR = Path(__file__).parent

#: The setting naming where packs live.
PACKS_ENV = "GEOTECH_REFERENCES_PACKS"
#: Every pack id starts with this, so it never collides with a built-in (or
#: a future built-in) and every citation shows it is the deployment's own.
PACK_PREFIX = "local_"
PACK_FILE = "pack.json"
CATALOG_NAME = "figures_catalog.json"


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
    packs: list[tuple[str, Path]] = []
    problems: list[str] = []
    builtins = None
    seen: dict[str, Path] = {}
    for root in _roots():
        folders, root_problems = _candidates(root)
        problems.extend(root_problems)
        for folder in folders:
            try:
                data = read_pack_json(folder)
            except (OSError, ValueError) as e:
                problems.append(f"{folder}: pack.json unreadable ({e}); skipped")
                continue
            pid = str(data.get("id") or folder.name)
            if builtins is None:
                builtins = builtin_ids()
            if pid in builtins:
                problems.append(f"{folder}: id '{pid}' is a built-in "
                                "reference's name; skipped")
                continue
            if not pid.startswith(PACK_PREFIX):
                problems.append(f"{folder}: id '{pid}' does not start with "
                                f"'{PACK_PREFIX}'; skipped")
                continue
            if pid in seen:
                problems.append(f"{folder}: id '{pid}' repeats the pack at "
                                f"{seen[pid]}; skipped")
                continue
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
    """What the current setting names that is not a usable pack, and why."""
    return scan()[1]


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
