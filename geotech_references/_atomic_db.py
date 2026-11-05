"""Build a search database where no other process can see it half built (REF-56).

The text and figure search databases are built lazily in the temp folder on
first use. They used to be deleted and rebuilt in place, so a second process
starting at the same moment (two users' first calls on a shared cluster after
an install, or two pytest-xdist workers on an empty temp folder) could open a
half-built file, see no tables or only some of the rows, or delete the file
the first process was still writing.

Now a database is built under a temporary name in the same folder and moved
into place with :func:`os.replace`, which is atomic on one file system, so the
real name only ever names a complete database.

Two processes that start at once each build their own temporary copy and the
last move wins. The copies are identical (the same source files, the same
code), so whichever lands is right. Waiting for the first builder instead
would need a lock file: ``fcntl`` on Linux and ``msvcrt`` on Windows behave
differently, and a builder that dies leaves a stale lock that the others must
detect and break, which is the same kind of race again. A build takes a few
seconds and only happens on first use after an install or an edit, so
building it twice now and then costs less than getting a lock wrong.

On Windows :func:`os.replace` refuses to replace a file another process has
open. Readers here open a connection per call and close it, so the move is
retried for a short while. If the file is still held, the database at the
real name is used when it is now current (another process put it there);
otherwise this process keeps reading its own complete copy, removes it when
the process ends, and tries the move again on its next call. The build never
raises for a held file and never leaves a partial file at the real name.

A temporary file is removed when its build fails. A process killed part way
through cannot remove its own, so each build first removes temporary files
of the same database older than :data:`STALE_SECONDS`.
"""

from __future__ import annotations

import atexit
import os
import sqlite3
import tempfile
import time
from pathlib import Path
from typing import Callable

#: Suffix of a database still being built (``.<name>.<random>.building``).
BUILDING_SUFFIX = ".building"

#: A temporary build file older than this was left by a process that died.
STALE_SECONDS = 15 * 60

#: How long to keep retrying a move Windows refuses (seconds, in total).
REPLACE_RETRY_SECONDS = 2.0

#: Built databases this process could not move into place (Windows: the
#: file at the real name was held open), by real path -> the copy in use.
_PENDING: dict[str, Path] = {}


def _remove_quietly(path: Path) -> None:
    for p in (path, Path(f"{path}-journal")):
        try:
            p.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass


def temp_files(db_path: Path) -> list[Path]:
    """Temporary build files of ``db_path`` in its folder (any process)."""
    prefix = f".{db_path.name}."
    try:
        return sorted(p for p in db_path.parent.iterdir()
                      if p.name.startswith(prefix)
                      and (p.name.endswith(BUILDING_SUFFIX)
                           or p.name.endswith(BUILDING_SUFFIX + "-journal")))
    except OSError:
        return []


def _sweep_stale(db_path: Path) -> None:
    """Remove build files a killed process left (older than STALE_SECONDS)."""
    now = time.time()
    mine = {str(p) for p in _PENDING.values()}
    for p in temp_files(db_path):
        if str(p) in mine:
            continue
        try:
            if now - p.stat().st_mtime > STALE_SECONDS:
                p.unlink()
        except OSError:
            pass


def _replace(src: Path, dst: Path,
             retry_seconds: float | None = None) -> bool:
    """Move ``src`` over ``dst``; False if Windows kept refusing it."""
    if retry_seconds is None:
        retry_seconds = REPLACE_RETRY_SECONDS
    deadline = time.monotonic() + retry_seconds
    pause = 0.02
    while True:
        try:
            os.replace(src, dst)
            return True
        except PermissionError:
            # Windows: dst is open in another process (a reader), or src is
            # being scanned. Readers here hold a file for one call only.
            if time.monotonic() >= deadline:
                return False
            time.sleep(pause)
            pause = min(pause * 2, 0.25)


def _forget_pending(key: str) -> None:
    old = _PENDING.pop(key, None)
    if old is not None:
        _remove_quietly(old)


def _cleanup_pending() -> None:
    for key in list(_PENDING):
        _forget_pending(key)


atexit.register(_cleanup_pending)


def build_atomically(db_path: Path,
                     fill: Callable[[sqlite3.Connection], None],
                     is_current: Callable[[Path], bool] | None = None) -> Path:
    """Build a database with ``fill`` and move it into place at ``db_path``.

    ``fill`` gets an open connection to an empty database; it is committed
    and closed here. Returns the path to read: ``db_path``, or, only when
    Windows would not let the finished copy replace a file held open and
    ``is_current(db_path)`` says the file there is out of date, this
    process's own complete copy (see the module docstring).

    If ``fill`` raises, the temporary file is removed, the database at
    ``db_path`` (if any) is left as it was, and the error is raised.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    _sweep_stale(db_path)
    fd, name = tempfile.mkstemp(dir=str(db_path.parent),
                                prefix=f".{db_path.name}.",
                                suffix=BUILDING_SUFFIX)
    os.close(fd)
    tmp = Path(name)
    try:
        conn = sqlite3.connect(str(tmp))
        try:
            fill(conn)
            conn.commit()
        finally:
            conn.close()
    except BaseException:
        _remove_quietly(tmp)
        raise

    key = str(db_path)
    try:
        moved = _replace(tmp, db_path)
    except BaseException:
        _remove_quietly(tmp)
        raise
    if moved:
        _forget_pending(key)
        return db_path
    # Windows kept the file at db_path open past the retries.
    if is_current is not None and is_current(db_path):
        _remove_quietly(tmp)
        _forget_pending(key)
        return db_path
    previous = _PENDING.get(key)
    _PENDING[key] = tmp
    if previous is not None and previous != tmp:
        _remove_quietly(previous)
    return tmp


def ensure_built(db_path: Path,
                 needs_rebuild: Callable[[Path], bool],
                 fill: Callable[[sqlite3.Connection], None]) -> Path:
    """The path of a complete, current database for ``db_path``.

    Builds it with :func:`build_atomically` when ``needs_rebuild(db_path)``.
    A copy an earlier call could not move into place is moved now if it
    can be, and read meanwhile, so it is not built again on every call.
    """
    db_path = Path(db_path)
    key = str(db_path)
    if not needs_rebuild(db_path):
        _forget_pending(key)
        return db_path
    pending = _PENDING.get(key)
    if pending is not None and pending.exists():
        if needs_rebuild(pending):
            _forget_pending(key)
        else:
            # one try: this runs on every call while the copy is pending
            if _replace(pending, db_path, retry_seconds=0.0):
                _PENDING.pop(key, None)
                return db_path
            return pending
    return build_atomically(
        db_path, fill, is_current=lambda p: not needs_rebuild(p))
