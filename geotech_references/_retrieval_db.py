"""SQLite FTS5 retrieval layer for structured chapter text.

Builds a single FTS5 index over every `<reference>/text/*.json` file in
the package (and in any local reference pack, :mod:`._packs`) and exposes three tools optimized for LLM agent use:

- ``reference_search(query, reference=None, chapter=None, limit=5)`` —
  ranked BM25 hits returning *summary only* (the noise-reduction lever).
- ``reference_get(reference, section_id)`` — full section body.
- ``reference_query(sql)`` — read-only SELECT against the backing tables
  (URI mode read-only connection plus a regex SELECT-only check and a
  server-side LIMIT cap).

The database is built lazily into a per-user temp directory at first
call and rebuilt automatically if any source JSON has been touched
since the build. Its file name is keyed to this copy of the package
(:func:`keyed_db_path`), so another checkout or environment sharing the
temp directory keeps its own. The DB is *not* committed; it is
regenerated on demand.

Coverage caveat (2026-10-21)
----------------------------
Not every reference has ``summary`` fields. DM7 (`dm7_1`, `dm7_2`),
micropile, ufc_pavement and most of gec_13 do; gec_6, gec_7, gec_10, gec_11
and gec_12 are indexed body-only, so search hits against them have empty
``summary`` strings, the noise-reduction lever does not apply, and agents
should drill in via :func:`reference_get` for those hits. Only
``ufc_backfill`` and ``ufc_expansive`` have no narrative text at all.
See ``scripts/README.md`` "Reference text coverage status".

Every level (REF-24)
--------------------
One row per section at EVERY level a chapter file holds, nested
(``subsections``, GEC-12) or listed flat, read through
:func:`geotech_references._retrieval.section_entries`. A row holds the
section's own text only, never its subsections', so a search hit is the
section that holds the words and :func:`reference_get` works on any section
number. Each row knows the section above it (``parent_rowid``), its
``depth`` and the chain above it (``parents_json``); hits carry
``parent_id`` and ``under``, fetches add ``children``. The database's
``PRAGMA user_version`` is :data:`_SCHEMA_VERSION`; a database built to an
older layout is rebuilt on first use. Its ``build_meta`` table holds the
signature of the chapter files it was built from (:func:`source_state`),
and a database whose files have changed since -- one deleted, added, or
restored with an older date -- is rebuilt too (2026-11-10 review, core-11).
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
import re
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

from . import _atomic_db
from . import _packs
from . import _query_expansion as _qe
from . import _retrieval

_PACKAGE_DIR = Path(__file__).parent
_DB_NAME = "geotech_references_fts.sqlite"

#: Layout of the ``sections`` table, kept in ``PRAGMA user_version``.
#: 2 = every level indexed, with parent_rowid / depth / parents_json (REF-24).
#: 3 = a ``build_meta`` table holding the signature of the source files the
#: database was built from (2026-11-10 review, core-11).
#: 4 = each row's ``reference_id``, its chapter file's report number, so a
#: search scoped to a volume's own number searches that volume (2026-11-10
#: review follow-up).
_SCHEMA_VERSION = 4

_INDEXED_COLUMNS = (
    "title",
    "summary",
    "body",
    "key_points",
    "applicability",
)

_STRUCTURAL_COLUMNS = (
    "reference",
    "reference_title",
    "chapter",
    "chapter_title",
    "section_id",
    "equations_json",
    "figures_json",
    "tables_json",
)

_MAX_LIMIT = 50  # server-side cap on reference_query LIMIT
_DEFAULT_SEARCH_LIMIT = 5
_MAX_OFFSET = 500  # deepest page reference_search reaches

_SELECT_ONLY_RE = re.compile(r"^\s*(?:WITH\b|SELECT\b)", re.IGNORECASE)
_FORBIDDEN_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|"
    r"DETACH|PRAGMA|VACUUM|REINDEX|TRIGGER)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# DB build
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def _copy_key(package_dir: str) -> str:
    """Short hash of one copy of the package: its resolved folder plus the
    installed version (blank when no install metadata is found)."""
    try:
        from importlib.metadata import version
        installed = version("geotech-references")
    except Exception:
        installed = ""
    folder = os.path.normcase(str(Path(package_dir).resolve()))
    return hashlib.sha1(f"{folder}|{installed}".encode()).hexdigest()[:12]


def keyed_db_path(name: str, package_dir: Path = _PACKAGE_DIR) -> Path:
    """The temp-folder database for this copy of the package (REF-55).

    The file name carries :func:`_copy_key`, so two checkouts, or two
    environments sharing one temp folder, never serve each other's text.
    A database left under the old fixed name is not read or deleted.

    With local reference packs set (``GEOTECH_REFERENCES_PACKS``, REF-64)
    the key also covers the pack set -- each indexed pack file's path, size
    and modification time (:func:`._packs.key_part`) -- so a pack edit gets
    a database of its own. With none set the key is unchanged, and the
    databases already built stay valid.
    """
    stem, suffix = os.path.splitext(name)
    key = _copy_key(str(package_dir))
    packs = _packs.key_part()
    if packs:
        key = hashlib.sha1(f"{key}|packs|{packs}".encode()).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / f"{stem}_{key}{suffix}"


def _db_path() -> Path:
    return keyed_db_path(_DB_NAME)


#: The folders of the local reference packs indexed beside the built-ins
#: (REF-64); an app tests ``hasattr(_retrieval_db, "pack_dirs")`` to know
#: this version reads packs.
pack_dirs = _packs.pack_dirs


def _iter_text_jsons() -> list[tuple[str, Path]]:
    """Yield (reference, json_path) for every text JSON in the package,
    then every local reference pack's (REF-64; none when unset)."""
    out: list[tuple[str, Path]] = []
    for ref_dir in sorted(_PACKAGE_DIR.iterdir()):
        if not ref_dir.is_dir():
            continue
        text_dir = ref_dir / "text"
        if not text_dir.is_dir():
            continue
        for jf in sorted(text_dir.glob("*.json")):
            out.append((ref_dir.name, jf))
    out.extend(_packs.text_jsons())
    return out


def _newest_source_mtime() -> float:
    return source_state([jf for _, jf in _iter_text_jsons()])[0]


#: ``(PRAGMA user_version, source signature)`` per (database path, file
#: mtime), so a search does not open the database twice to learn them.
_VERSION_SEEN: dict = {}


def _source_label(path: Path) -> str:
    """A source file as the signature names it: its path inside the
    package, or a local pack's full path."""
    try:
        return path.relative_to(_PACKAGE_DIR).as_posix()
    except ValueError:
        return os.path.normcase(str(path))


def source_state(paths) -> tuple[float, str]:
    """``(newest modification time, signature)`` of the source files
    ``paths``: the signature is a sha1 over each file's place, size and
    modification time (ns), so a deleted, added, edited or restored file
    changes it (2026-11-10 review, core-11)."""
    h = hashlib.sha1()
    newest = 0.0
    for p in paths:
        try:
            st = p.stat()
        except OSError:
            h.update(f"{_source_label(p)}|gone\0".encode())
            continue
        newest = max(newest, st.st_mtime)
        h.update(f"{_source_label(p)}|{st.st_size}|{st.st_mtime_ns}\0"
                 .encode())
    return newest, h.hexdigest()


def write_build_meta(cur: sqlite3.Cursor, signature: str,
                     version: int) -> None:
    """Record in a database being built the signature of the sources it
    is built from and its layout version (``PRAGMA user_version``)."""
    cur.execute("CREATE TABLE build_meta (key TEXT PRIMARY KEY, value TEXT)")
    cur.execute("INSERT INTO build_meta VALUES ('sources', ?)", (signature,))
    cur.execute(f"PRAGMA user_version = {int(version)}")


def db_meta(db_path: Path) -> tuple[int, str | None]:
    """``(layout version, source signature)`` a database was built with;
    ``(-1, None)`` when it cannot be read, and no signature for one built
    before databases kept it."""
    try:
        key = (str(db_path), db_path.stat().st_mtime_ns)
    except OSError:
        return -1, None
    if key not in _VERSION_SEEN:
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            try:
                version = int(conn.execute("PRAGMA user_version").fetchone()[0])
                try:
                    row = conn.execute("SELECT value FROM build_meta "
                                       "WHERE key = 'sources'").fetchone()
                except sqlite3.Error:
                    row = None
            finally:
                conn.close()
        except sqlite3.Error:
            return -1, None
        _VERSION_SEEN[key] = (version, row[0] if row else None)
    return _VERSION_SEEN[key]


def _schema_version(db_path: Path) -> int:
    return db_meta(db_path)[0]


def _needs_rebuild(db_path: Path) -> bool:
    """Whether the text database at ``db_path`` must be built (again): it
    is not there, a source file is newer than it, it was built to an older
    layout (one row per top-level section only, or no signature), or the
    source files are not the ones it was built from -- a chapter file
    deleted or added, or restored with an older date, which the date rule
    alone missed (2026-11-10 review, core-11)."""
    if not db_path.exists():
        return True
    newest, signature = source_state([jf for _, jf in _iter_text_jsons()])
    if db_path.stat().st_mtime < newest:
        return True
    version, built_from = db_meta(db_path)
    return version != _SCHEMA_VERSION or built_from != signature


def _build_db(db_path: Path) -> Path:
    """Build the database and move it into place at ``db_path`` (REF-56).

    Built under a temporary name beside it and moved in with
    ``os.replace``, so another process never opens a half-built file
    (:mod:`geotech_references._atomic_db`). Returns the path to read.
    """
    return _atomic_db.build_atomically(
        db_path, _fill_db, is_current=lambda p: not _needs_rebuild(p))


def _fill_db(conn: sqlite3.Connection) -> None:
    """Create the tables and index every source file into ``conn``."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE sections (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT NOT NULL,
            reference_title TEXT,
            chapter INTEGER,
            chapter_title TEXT,
            section_id TEXT,
            title TEXT,
            summary TEXT,
            body TEXT,
            key_points TEXT,
            applicability TEXT,
            equations_json TEXT,
            figures_json TEXT,
            tables_json TEXT,
            parent_rowid INTEGER,
            depth INTEGER,
            parents_json TEXT,
            reference_id TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE VIRTUAL TABLE sections_fts USING fts5(
            title, summary, body, key_points, applicability,
            content='sections',
            content_rowid='rowid',
            tokenize='porter unicode61'
        )
        """
    )
    cur.execute(
        "CREATE INDEX idx_sections_ref ON sections(reference)"
    )
    cur.execute(
        "CREATE INDEX idx_sections_ref_chap ON sections(reference, chapter)"
    )
    cur.execute(
        "CREATE INDEX idx_sections_ref_sid ON sections(reference, section_id)"
    )
    cur.execute(
        "CREATE INDEX idx_sections_parent ON sections(parent_rowid)"
    )

    pack_files = {jf for _, jf in _packs.text_jsons()}
    sources = _iter_text_jsons()
    # taken before the files are read: one changed during the build makes
    # the next check build again
    signature = source_state([jf for _, jf in sources])[1]
    write_build_meta(cur, signature, _SCHEMA_VERSION)
    for reference, jf in sources:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            if jf in pack_files:
                continue  # named in _packs.problems()
            raise unreadable_source(jf, e) from e
        if jf not in pack_files:
            _index_chapter(cur, reference, data)
        # a local pack's file the index cannot take is skipped and named in
        # _packs.problems(); one that still fails is rolled back (REF-64)
        elif _packs.chapter_problem(data) is None:
            _packs.index_pack_file(
                cur, jf, lambda: _index_chapter(cur, reference, data))

    cur.execute(
        """
        INSERT INTO sections_fts(rowid, title, summary, body,
                                 key_points, applicability)
        SELECT rowid, title, summary, body, key_points, applicability
        FROM sections
        """
    )


def unreadable_source(path: Path, error: Exception) -> RuntimeError:
    """The error both search databases raise for a built-in source file
    (a chapter file, a figure catalog) the build cannot read. It used to be
    left out without a word, so its reference simply had less text or no
    figures (2026-11-10 review, core-12); the database already built, if
    any, is left as it was. A local pack's file is still skipped and named
    in ``_packs.problems()``."""
    return RuntimeError(
        f"the search database was not built: the package file {path} cannot "
        f"be read ({type(error).__name__}: {error}). Restore it from the "
        "release (reinstall geotech-references) or fix the file.")


def _index_chapter(cur: sqlite3.Cursor, reference: str, data: dict) -> None:
    """Insert one chapter file's sections, every level, into ``sections``."""
    ref_title = data.get("reference_title", "")
    ref_id = data.get("reference_id", "")
    ch_num = data.get("chapter", 0)
    ch_title = data.get("chapter_title", "")
    entries = _retrieval.section_entries(data)
    rowids: list[int] = []
    for i, entry in enumerate(entries):
        sec = entry["section"]
        chain = [entries[j]["section"]
                 for j in _retrieval.entry_chain(entries, i)]
        kps = sec.get("key_points", [])
        if isinstance(kps, list):
            key_points_text = "\n".join(
                str(p) for p in kps if isinstance(p, (str, int, float))
            )
        else:
            key_points_text = str(kps)
        cur.execute(
            """
            INSERT INTO sections (
                reference, reference_title, chapter, chapter_title,
                section_id, title, summary, body, key_points,
                applicability, equations_json, figures_json,
                tables_json, depth, parents_json, reference_id
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                reference,
                ref_title,
                ch_num,
                ch_title,
                sec.get("section_id", ""),
                sec.get("title", ""),
                sec.get("summary", ""),
                sec.get("body", ""),
                key_points_text,
                sec.get("applicability", ""),
                json.dumps(sec.get("equations", []), ensure_ascii=False),
                json.dumps(sec.get("figures", []), ensure_ascii=False),
                json.dumps(sec.get("tables", []), ensure_ascii=False),
                len(chain),
                json.dumps([[s.get("section_id", ""), s.get("title", "")]
                            for s in chain], ensure_ascii=False),
                ref_id if isinstance(ref_id, str) else str(ref_id),
            ),
        )
        rowids.append(cur.lastrowid)
    # a flat-listed section's parent may come later in its file, so
    # parents are linked once the whole file is in
    cur.executemany(
        "UPDATE sections SET parent_rowid = ? WHERE rowid = ?",
        [(rowids[e["parent"]], rowids[i])
         for i, e in enumerate(entries) if e["parent"] is not None],
    )


def _ensure_db() -> Path:
    return _atomic_db.ensure_built(_db_path(), _needs_rebuild, _fill_db)


def _ro_connect() -> sqlite3.Connection:
    db = _ensure_db()
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _row_to_summary(row: sqlite3.Row) -> dict[str, Any]:
    chain = json.loads(row["parents_json"] or "[]")
    return {
        "reference": row["reference"],
        "reference_title": row["reference_title"],
        # the report number of the section's volume, as on figure hits
        # (2026-11-10 review follow-up)
        "reference_id": row["reference_id"],
        "chapter": row["chapter"],
        "chapter_title": row["chapter_title"],
        "section_id": row["section_id"],
        "title": row["title"],
        "parent_id": chain[-1][0] if chain else None,
        "under": _retrieval.under_text(
            [{"section_id": sid, "title": title} for sid, title in chain]),
        "summary": row["summary"],
    }


def _row_text(row: sqlite3.Row) -> dict[str, Any]:
    """A section's own text fields."""
    return {
        "body": row["body"],
        "key_points": [
            kp for kp in (row["key_points"] or "").split("\n") if kp
        ],
        "applicability": row["applicability"],
        "equations": json.loads(row["equations_json"] or "[]"),
        "figures": json.loads(row["figures_json"] or "[]"),
        "tables": json.loads(row["tables_json"] or "[]"),
    }


def _row_to_full(row: sqlite3.Row) -> dict[str, Any]:
    out = _row_to_summary(row)
    out.update(_row_text(row))
    return out


def _child_rows(conn: sqlite3.Connection, rowid: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM sections WHERE parent_rowid = ? ORDER BY rowid",
        (rowid,),
    ).fetchall()


def _subtree(conn: sqlite3.Connection, rowid: int,
             seen: set | None = None) -> list[dict[str, Any]]:
    """The sections under row ``rowid``, each with its own subsections."""
    seen = set() if seen is None else seen
    out = []
    for child in _child_rows(conn, rowid):
        if child["rowid"] in seen:
            continue
        seen.add(child["rowid"])
        sec = {"section_id": child["section_id"], "title": child["title"],
               "summary": child["summary"]}
        sec.update(_row_text(child))
        kids = _subtree(conn, child["rowid"], seen)
        if kids:
            sec["subsections"] = kids
        out.append(sec)
    return out


#: How many of an OR-ed query's best BM25 hits are re-ordered by the
#: concepts they hold (REF-48): the most one page shows. Hits past it keep
#: their BM25 order, so every page of a search is cut from the same order.
_BEST_MATCH_POOL = _MAX_LIMIT

#: How many hits of the literal and of the literal-OR-synonyms query ``auto``
#: fuses (REF-54). Fixed, not the page size, so a page is cut from the same
#: order whatever ``limit`` asked for.
_FUSION_POOL = _MAX_LIMIT


def _by_concepts_held(conn: sqlite3.Connection, rows: list,
                      concepts: list[str]) -> list:
    """The first :data:`_BEST_MATCH_POOL` of ``rows`` (each with its
    ``rid``) re-ordered by how many of ``concepts`` (FTS5 expressions) each
    holds, most first, keeping their order within a count; the rest after
    them as they were."""
    head, tail = rows[:_BEST_MATCH_POOL], rows[_BEST_MATCH_POOL:]
    if len(head) < 2:
        return rows
    held = dict.fromkeys((r["rid"] for r in head), 0)
    for concept in concepts:
        for (rid,) in conn.execute(
                "SELECT rowid FROM sections_fts WHERE sections_fts MATCH ?",
                (concept,)):
            if rid in held:
                held[rid] += 1
    return sorted(head, key=lambda r: -held[r["rid"]]) + tail


def reference_search(
    query: str,
    reference: str | None = None,
    chapter: int | None = None,
    limit: int = _DEFAULT_SEARCH_LIMIT,
    offset: int = 0,
    max_chars: int | None = None,
):
    """Full-text search across structured chapter text.

    Returns ranked summary-only hits (no `body`) — call
    :func:`reference_get` to fetch the full section. Every section is
    indexed at every level with its own text only, so the hit is the
    section that holds the words (a method's own subsection, not just the
    chapter section it sits in); ``under`` names the sections above it.

    Parameters
    ----------
    query : str
        FTS5 MATCH query, words matched with porter stemming. The sections
        that hold every word come first. Unless the expansion strategy is
        ``"off"``, sections holding a synonym of a named term are added
        (``"auto"`` keeps the best of the every-word hits in place), and
        when no section holds every word the search relaxes to the
        synonyms, then to any one of the words, the sections holding more
        of them first. A hit that does not hold every word says so in
        ``match`` (below). Use FTS5 operators (``"phrase"``, ``OR``,
        ``NEAR()``, ``col:term``) for advanced queries.
    reference : str, optional
        Restrict to a single reference id (e.g. ``"dm7_1"``), another
        spelling of it (``"GEC-10"``) or a report number its files carry
        (``"FHWA-NHI-06-089"``, with or without the agency), read as
        :func:`figure_search` reads it (:func:`search_scope`). A report
        number that is one volume of a manual searches that volume's
        chapters alone. A name that is not indexed is an error naming the
        ids, not an empty result; ``"dm7"`` (two references here) is an
        error naming ``dm7_1`` and ``dm7_2``.
    chapter : int, optional
        Restrict to a single chapter number (only meaningful with
        ``reference``). A chapter the reference does not have is an
        error naming its chapters.
    limit : int, optional
        Max hits (capped at ``50``).
    offset : int, optional
        Skip this many of the best hits first (the next page). Past
        :data:`_MAX_OFFSET` the result is an error saying to narrow the
        query; a page whose next hits would start past it says so instead
        of offering ``next_offset``.
    max_chars : int, optional
        The largest result the caller can take, in JSON characters (50
        hits run to about 36,000). With it the result is a dict of the
        hits that fit (:func:`_retrieval.fit_hits`: summaries cut to 300
        characters first, then the lowest-ranked hits left out) with, when
        some are not shown or more were found, ``next_offset`` and a
        ``note``. When some hits do not hold every word it adds
        ``matched`` (``"synonyms"``, or ``"any word"`` when a hit holds
        only some of the words), ``words_not_found`` (the query words no
        hit holds) and a sentence on the ``note``. An empty result names
        the scope searched and what was tried in a ``note``, with
        ``words_not_found`` (the words no section there holds) and, for a
        local pack, the files the index skipped. A ``reference`` that is
        not itself an id adds ``resolved_reference``, and a report number
        that is one volume adds ``report_number`` and a sentence on the
        note saying so. An error is ``{"error": ...}``.

    Returns
    -------
    list of dict, or dict with ``max_chars``
        Each hit has ``reference``, ``reference_title``, ``reference_id``
        (the report number of the section's volume, so a plain list shows
        the volume a report-number scope kept to), ``chapter``,
        ``chapter_title``, ``section_id``, ``title``, ``parent_id``,
        ``under`` (the sections above it, outermost first, e.g.
        ``"7.2 Strength Limit States > 7.2.1 Nominal Axial ..."``; ``""``
        at the top level) and ``summary``. A hit that does not hold every
        word of the query also has ``match``: ``"synonyms"`` (every word,
        a named term as one of its synonyms), ``"all words"`` (every word,
        not as the phrase typed, ``not_as_phrase`` naming it) or ``"any
        word"`` (only some of the words, ``lacks`` naming the ones it does
        not hold). The marks are worked out after the ranking and never
        move a hit (2026-11-10 review, core-05). With ``max_chars``, the
        dict described above; it alone carries the note on the scope.
    """
    if not query or not query.strip():
        return [] if max_chars is None else {"hits": [], "shown": 0}
    limit = max(1, min(int(limit), _MAX_LIMIT))
    offset = max(0, int(offset or 0))
    if offset > _MAX_OFFSET:
        return _past_deepest_page(offset, max_chars)
    # rows wanted: the page, after the offset, and one more to learn
    # whether more match (a plain call asks for exactly the page, as before)
    want = limit if not (offset or max_chars is not None) \
        else offset + limit + 1
    conn = _ro_connect()
    try:
        def refuse(message: str):
            return ({"error": message} if max_chars is not None
                    else [{"error": message}])

        # A reference that is not indexed, or a chapter it does not have, is
        # an error naming the choices: it used to be an empty list, the
        # same answer as "no section says this" (2026-11-10 review, core-06).
        # The name is read as figure_search reads it (search_scope): another
        # spelling of the id, or a report number, which keeps the search to
        # that volume's chapters.
        refs: list = []
        numbers: list = []
        held: list = []
        if reference:
            held = _held(conn)
            refs, numbers, error = search_scope(reference, held)
            if error:
                return refuse(error)
            if not refs:
                return refuse(_unknown_reference(conn, reference))
        in_scope, scope_params = scope_clause("s", refs, numbers)
        chapter_no = None
        if chapter is not None:
            try:
                chapter_no = int(chapter)
            except (TypeError, ValueError):
                chapter_no = None
            have = sorted(r[0] for r in conn.execute(
                "SELECT DISTINCT chapter FROM sections s WHERE 1"
                + in_scope, scope_params) if r[0] is not None)
            if chapter_no not in have:
                return refuse(
                    f"no chapter {chapter!r} in "
                    f"{reference or 'any reference'}; chapters there: "
                    + ", ".join(str(c) for c in have)
                    + " (list_chapters gives their titles; an appendix or "
                    "a prologue is filed under a number of its own)")

        def run(match_query: str, pool: int | None = None) -> list[sqlite3.Row]:
            sql = (
                "SELECT s.rowid AS rid, s.reference, s.reference_title, "
                "s.chapter, s.chapter_title, s.section_id, s.title, s.summary, "
                "s.parents_json, s.reference_id "
                "FROM sections_fts f JOIN sections s ON s.rowid = f.rowid "
                "WHERE sections_fts MATCH ?"
            )
            params: list[Any] = [match_query]
            sql += in_scope
            params.extend(scope_params)
            if chapter is not None:
                sql += " AND s.chapter = ?"
                params.append(chapter_no)
            sql += " ORDER BY bm25(sections_fts) LIMIT ?"
            params.append(pool or want)
            return conn.execute(sql, params).fetchall()

        def best_match(concepts: list[str]):
            """``run`` for a query whose words are OR-ed (REF-48): the
            sections that hold more of the query's concepts first, so a short
            section holding four of six words densely no longer outranks one
            holding five; BM25 orders the sections within a count."""
            def run_or(match_query: str) -> list[sqlite3.Row]:
                if len(concepts) < 2:
                    return run(match_query)
                rows = run(match_query, pool=max(want, _BEST_MATCH_POOL))
                return _by_concepts_held(conn, rows, concepts)[:want]
            return run_or

        strategy = _qe.EXPANSION_STRATEGY
        # by row, not by number: a number two sections of a local pack hold
        # keeps both rows (core-01; no built-in reference repeats one)
        row_key = lambda r: r["rid"]
        ran = {"q": query}  # the query as last run (re-quoted when it failed)

        def search(q: str, relaxed: bool = False) -> list[sqlite3.Row]:
            ran["q"] = q
            if strategy == "rerank":
                # "shotgun": one combined query, BM25 ranks literal+synonym union.
                rows = run(_qe.combined_query(q))
            elif strategy == "auto":
                # Fuse the literal hits with the literal+synonym union
                # (recall), PINNING the literal top-N (EXPANSION_PIN, default
                # 1) so an already-good query keeps its best hit (precision).
                combined = _qe.combined_query(q)
                pool = max(want, _FUSION_POOL)
                literal = run(q) if combined == q else run(q, pool=pool)
                if combined == q:
                    rows = literal            # no synonyms to add
                elif not literal:
                    # nothing to pin: the query with its terms swapped for
                    # their synonyms, then its words OR-ed with the synonyms
                    rows = _qe.zero_literal_hits(
                        q, run, want, key=row_key,
                        run_or=best_match(_qe.query_concepts(q)))
                else:
                    # REF-54: the literal hits keep their places by
                    # reciprocal-rank fusion with the combined query, so the
                    # synonyms add hits without pushing out what the literal
                    # search ranked well (top EXPANSION_PIN pinned)
                    rows = _qe.fuse_hits(
                        literal, run(combined, pool=pool), want,
                        key=row_key, pin=_qe.EXPANSION_PIN,
                    )
            else:
                rows = run(q)
                # "fill": the literal query is AND-matched, so it under-returns
                # exactly when the query's terminology differs from the source
                # text (a synonym miss). Append synonym hits to fill remaining
                # slots; literal BM25 hits keep their rank (precision preserved).
                if strategy == "fill" and len(rows) < want:
                    expansion = _qe.expand_query(q)
                    if expansion:
                        rows = _qe.merge_hits(
                            rows, run(expansion), want, key=row_key,
                        )
            # Zero-hit recall fallback (mirrors figure_search): if the
            # AND-matched query (and any expansion) found nothing, retry as
            # OR-of-terms. Fires only when there would otherwise be no
            # results, so existing rankings are never disturbed. NOT applied
            # in 'off' — that strategy is the pure-literal anchor used by the
            # recall eval and the precision invariants.
            if not rows and strategy != "off":
                fb, words = _qe.or_fallback(q), q
                if not fb and relaxed:
                    # a query re-quoted by fts_safe_query: its words, OR-ed
                    words = plain_terms(q)
                    fb = _qe.or_fallback(words)
                if fb and fb != q:
                    rows = best_match(_qe.query_concepts(words))(fb)
            return rows

        try:
            rows = search_fts_safely(
                search, query, retry=lambda q: search(q, relaxed=True))
        except sqlite3.OperationalError as e:
            if max_chars is not None:
                return {"error": f"FTS query error: {e}"}
            return [{"error": f"FTS query error: {e}"}]
        more = len(rows) > offset + limit
        page = rows[offset:offset + limit]
        # how each hit matched, worked out after the ranking (core-05)
        marks, absent = match_marks(conn, "sections_fts",
                                    [r["rid"] for r in page], ran["q"])
        hits = []
        for r in page:
            hit = _row_to_summary(r)
            hit.update(marks.get(r["rid"], {}))
            hits.append(hit)
        if max_chars is None:
            return hits
        if not rows:
            scope = (f"reference '{', '.join(refs)}'" if refs
                     else "the text index")
            if numbers:
                scope += f" ({', '.join(numbers)})"
            if chapter is not None:
                scope += f", chapter {chapter_no}"
            tried = TRIED_ALL if strategy != "off" else (
                "every word as typed; synonym and any-word matching are "
                "off: GEOTECH_RETRIEVAL_EXPANSION=off")
            out = dict({"hits": [], "shown": 0}, **absent_words_note(
                _words_in_no_section(conn, ran["q"], refs, chapter_no,
                                     numbers),
                scope, tried,
                _pack_problems(refs[0] if len(refs) == 1 else None)))
        else:
            out = with_match_summary(_retrieval.fit_hits(
                hits, max_chars, text_fields=("summary",), offset=offset,
                more=more, max_offset=_MAX_OFFSET,
                narrow=("narrow the query (more specific words, a "
                        "'reference' or a 'chapter')"),
                fetch="reference_get returns a section's whole text",
                more_text="more match" if not marks else "more were found"),
                match_summary(list(marks.values()), absent))
        return with_scope(out, reference, refs, numbers, held, "sections")
    finally:
        conn.close()


def with_scope(out: dict, reference, refs: list, numbers: list, held: list,
               what: str) -> dict:
    """A size-fitted search result with what a ``reference`` that is not
    itself an id was read as: ``resolved_reference`` (the id or ids), and
    for a report number that is one volume ``report_number`` and a sentence
    on the note (:func:`volume_note`)."""
    if reference and refs != [reference]:
        out["resolved_reference"] = refs[0] if len(refs) == 1 else refs
    sentence = volume_note(refs, numbers, held, what)
    if sentence:
        out["report_number"] = designation(numbers[0])
        out["note"] = (sentence + " " + out.get("note", "")).strip()
    return out


def _words_in_no_section(conn: sqlite3.Connection, query: str,
                         refs: list, chapter: int | None,
                         numbers: list = ()) -> list:
    """The query's words that no section in the scope holds."""
    in_scope, scope_params = scope_clause("s", refs, list(numbers))
    out = []
    for w in query_words(query):
        sql = ("SELECT 1 FROM sections_fts f JOIN sections s "
               "ON s.rowid = f.rowid WHERE sections_fts MATCH ?" + in_scope)
        params: list[Any] = [w] + scope_params
        if chapter is not None:
            sql += " AND s.chapter = ?"
            params.append(chapter)
        try:
            if conn.execute(sql + " LIMIT 1", params).fetchone() is None:
                out.append(w)
        except sqlite3.OperationalError:
            continue
    return out


def _pack_problems(reference: str | None) -> list[str]:
    """What the index skipped of local pack ``reference`` (core-10); none
    for a built-in reference or a search of everything."""
    if not reference or not str(reference).startswith(_packs.PACK_PREFIX):
        return []
    return _packs.problems_by_pack().get(reference, [])


def _is_indexed(conn: sqlite3.Connection, reference: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sections WHERE reference = ? LIMIT 1",
        (reference,)).fetchone() is not None


def _unknown_reference(conn: sqlite3.Connection, reference: str) -> str:
    """What a search or a fetch says for a ``reference`` that is not in
    the text index."""
    ids = [r[0] for r in conn.execute(
        "SELECT DISTINCT reference FROM sections ORDER BY reference")]
    skipped = _packs.problems_by_pack().get(reference)
    why = (" The reference packs setting names it, but the index skipped "
           "it: " + "; ".join(skipped) + "." if skipped else "")
    return (f"no reference '{reference}' in the text index.{why} Use one "
            f"of: {', '.join(ids)} (or search with no reference to look in "
            "all of them)")


# ---------------------------------------------------------------------------
# What a search's ``reference`` names: one rule for reference_search and
# figure_search (2026-11-10 review follow-up)
# ---------------------------------------------------------------------------

#: A name callers use for a manual that is two references here: the app's
#: module ``dm7`` covers UFS 3-220-10 (``dm7_1``) and UFC 3-220-20
#: (``dm7_2``). Both searches refuse it, naming the two; a figure lookup
#: reads it by the figure asked for (``_figures_db.resolve_reference``).
SHARED_NAMES = {"dm7": ("dm7_1", "dm7_2")}


def id_key(text) -> str:
    """A reference id, title or report number reduced to lower-case letters
    and digits ('gec_10', 'GEC-10', 'gec10' -> 'gec10'; 'UFC 3-250-01' ->
    'ufc325001')."""
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


def is_report_number(key: str, doc_key: str) -> bool:
    """Whether ``key`` is the report number ``doc_key`` (both reduced by
    :func:`id_key`): the whole of it ('fhwanhi16009', 'ufc325001') or the
    number without its agency ('nhi16009', '325001')."""
    if not doc_key:
        return False
    return key == doc_key or (
        len(key) >= 5 and any(c.isdigit() for c in key)
        and doc_key.endswith(key))


#: The designation a stored report number begins with: everything up to the
#: first space after its number ("FHWA-NHI-05-037 Geotechnical Aspects of
#: Pavements" -> "FHWA-NHI-05-037"; "UFC 3-250-01" and "EN 1997-1:2004"
#: whole). A stored id with no number is its own designation.
_DESIGNATION = re.compile(r"^\D*?\d\S*")
#: The year a standard's number carries ("EN 1997-1:2004").
_STANDARD_YEAR = re.compile(r":(?:19|20)\d\d$")


def designation(number) -> str:
    """The designation of a stored report number (:data:`_DESIGNATION`)."""
    text = str(number or "").strip()
    m = _DESIGNATION.match(text)
    return m.group(0) if m else text


def number_forms(number) -> list[str]:
    """The forms a caller may give for stored report ``number``, reduced by
    :func:`id_key`: the whole stored text, its designation, and a
    standard's designation without its year ("EN 1997-1"). Before the
    2026-11-10 review follow-up only the whole stored text matched, so
    "FHWA-NHI-05-037" was refused for fhwa_pavements and "EN 1997-1" for
    eurocode_7_1."""
    text = str(number or "").strip()
    d = designation(text)
    return list(dict.fromkeys(
        k for k in (id_key(text), id_key(d), id_key(_STANDARD_YEAR.sub("", d)))
        if k))


def _volumes(numbers) -> dict:
    """``{designation key: [stored numbers]}``: a reference's stored report
    numbers grouped by the volume each names (one spelling per volume
    can differ between the indexes: "FHWA NHI-16-072", "FHWA-NHI-16-072")."""
    out: dict[str, list] = {}
    for n in numbers:
        out.setdefault(id_key(designation(n)), []).append(n)
    return out


def shared_name_refusal(name: str, named: list) -> str:
    """What both searches say for a name that is two references here
    (:data:`SHARED_NAMES`); ``named`` is ``(id, title)`` of each."""
    listed = " and ".join(f"{rid} ({title})" if title else rid
                          for rid, title in named)
    return (f"'{name}' names {len(named)} references here: {listed}. Give "
            "the id of the one you mean, or search with no reference to "
            "look in all of them.")


def search_scope(reference: str, held: list) -> tuple[list, list, str | None]:
    """What a search's ``reference`` names, given ``held``: ``(id, title,
    report numbers)`` of each reference the index holds.

    The id itself; another spelling of it (``gec10``, ``GEC-10``); or a
    report number the reference's files carry, with or without its agency
    (``NHI-16-028``, ``UFC 3-250-01``). Returns ``(refs, numbers, error)``:

    * ``refs``, the reference ids to search (empty: the name means nothing
      indexed);
    * ``numbers``, the report numbers whose rows alone are searched when
      the name is a report number. A volume printed under a number of its
      own is that volume: FHWA-NHI-06-089 is Volume II of the Soils and
      Foundations manual, and the reference id searches both volumes.
      Before, the figure search read such a number as the whole manual and
      the text search refused it;
    * ``error``, what to return instead: the app's module name ``dm7``
      names two references (:func:`shared_name_refusal`), or a number
      that is the designation of more than one volume or reference
      (:func:`ambiguous_number_refusal`).

    A report number matches a stored one by any of its forms
    (:func:`number_forms`: the stored text, its designation up to the
    first space after the number, a standard's number without its year),
    whole or without its agency. ``numbers`` is empty when the reference
    has one designation: the number names all of it.

    Nothing looser: a name that only begins an id or sits in a title means
    nothing (2026-11-10 review, core-09)."""
    ids = [h[0] for h in held]
    if reference in ids:
        return [reference], [], None
    key = id_key(reference)
    if not key:
        return [], [], None
    exact = [i for i in ids if id_key(i) == key]
    if exact:
        return exact, [], None
    shared = [h for h in held if h[0] in SHARED_NAMES.get(key, ())]
    if shared:
        return [], [], shared_name_refusal(
            reference, [(h[0], h[1]) for h in shared])
    matched = [(rid, n) for rid, _, numbers in held for n in numbers
               if any(is_report_number(key, k) for k in number_forms(n))]
    volumes = list(dict.fromkeys((rid, id_key(designation(n)))
                                 for rid, n in matched))
    if len(volumes) > 1:
        return [], [], ambiguous_number_refusal(reference, matched)
    if not volumes:
        return [], [], None
    rid = volumes[0][0]
    of = dict((h[0], h[2]) for h in held)
    if len(_volumes(of.get(rid, ()))) < 2:
        return [rid], [], None
    return [rid], list(dict.fromkeys(n for _, n in matched)), None


def ambiguous_number_refusal(name: str, matched: list) -> str:
    """What every lookup says for a report number that is the designation
    of more than one volume or reference; ``matched`` is ``(reference,
    stored number)`` of each."""
    listed = "; ".join(f"{designation(n)} ({rid})"
                       for rid, n in dict.fromkeys(
                           (rid, designation(n)) for rid, n in matched))
    return (f"'{name}' could be more than one report number here: {listed}. "
            "Give the whole number, or the reference id.")


def volume_note(refs: list, numbers: list, held: list, what: str) -> str:
    """The sentence a result scoped by a report number carries when that
    number is one volume of a reference whose volumes carry their own
    (``what``: "sections" or "figures"); '' otherwise."""
    if not numbers:
        return ""
    of = {h[0]: h[2] for h in held}
    out = []
    for rid in refs:
        vols = _volumes(of.get(rid, ()))
        if len(vols) < 2:
            continue
        mine = designation(numbers[0])
        out.append(
            f"{mine} is one volume of {rid} (its volumes carry "
            f"{', '.join(designation(v[0]) for v in vols.values())}), so "
            f"only that volume's {what} were searched; reference='{rid}' "
            "searches all of them.")
    return " ".join(out)


def scope_clause(alias: str, refs: list, numbers: list) -> tuple[str, list]:
    """The SQL (`` AND ...``) and parameters that keep a query to ``refs``
    and, when given, the rows of report ``numbers``."""
    sql, params = "", []
    if refs:
        sql += (f" AND {alias}.reference IN ("
                + ", ".join("?" for _ in refs) + ")")
        params += list(refs)
    if numbers:
        sql += (f" AND {alias}.reference_id IN ("
                + ", ".join("?" for _ in numbers) + ")")
        params += list(numbers)
    return sql, params


def resolve_name(reference: str, held: list, unknown) -> str:
    """The one reference id ``reference`` names, read as the searches read
    it (:func:`search_scope`), for a function that fetches from one
    reference. Raises ``KeyError``: ``unknown`` (a function of the name
    giving the layer's refusal naming its ids) for a name that means
    nothing; the search's refusal for ``dm7`` or a number that could be
    several; and a refusal naming the ids when a spelling means more than
    one. A report number names its reference here: a fetch finds a section
    or figure by its number in the whole reference."""
    refs, _numbers, error = search_scope(reference, held)
    if error:
        raise KeyError(error)
    if not refs:
        raise KeyError(unknown(reference))
    if len(refs) > 1:
        raise KeyError(f"'{reference}' could mean {', '.join(refs)}: give "
                       "one of those ids")
    return refs[0]


def resolve_text_reference(reference: str) -> str:
    """The text reference id ``reference`` names (:func:`resolve_name`):
    the id, another spelling of it (``gec12``), or a report number its
    files carry. The fetches and listings of both text layers read a
    reference this way, as :func:`reference_search` does; before the
    2026-11-10 review follow-up only the searches did, so
    ``reference_get("gec12", "7.2")`` was refused. Raises ``KeyError`` with
    the refusal :func:`reference_search` gives."""
    conn = _ro_connect()
    try:
        if _is_indexed(conn, reference):
            return reference
        return resolve_name(reference, _held(conn),
                            lambda name: _unknown_reference(conn, name))
    finally:
        conn.close()


def _held(conn: sqlite3.Connection) -> list:
    """``(reference, title, report numbers)`` of each reference the text
    index holds, each once, in index order."""
    titles: dict[str, str] = {}
    numbers: dict[str, list] = {}
    for ref, title, rid in conn.execute(
            "SELECT reference, reference_title, reference_id FROM sections "
            "GROUP BY reference, reference_id ORDER BY MIN(rowid)"):
        titles.setdefault(ref, title or "")
        held = numbers.setdefault(ref, [])
        if rid and rid not in held:
            held.append(rid)
    return [(ref, titles[ref], tuple(numbers[ref])) for ref in titles]


def _past_deepest_page(offset: int, max_chars):
    """reference_search's error for an ``offset`` past the deepest page it
    gives (a dict with ``max_chars``, a one-item list without, as its other
    errors)."""
    message = (f"offset={offset} is past the deepest page this search "
               f"gives (its offset goes no higher than {_MAX_OFFSET}): "
               "narrow the query (more specific words, a 'reference' or a "
               "'chapter') instead.")
    return {"error": message} if max_chars is not None         else [{"error": message}]


# ---------------------------------------------------------------------------
# Plain-text queries that FTS5 cannot parse as written
# ---------------------------------------------------------------------------
# A user's words go straight to FTS5 MATCH, where '-', '.', '/', ':' and the
# like are query syntax: "EM 1110-2-1902", "pseudo-static" and "Table 5-2"
# failed with "no such column: 2" / "no such column: static" (GeotechStaff-
# Engineer live smoke wave 1, A11). A query that fails is run again with
# every such token quoted as a phrase -- the tokenizer then matches its parts
# in order, which is what the words meant -- so valid FTS5 syntax (phrases,
# OR / NOT / NEAR, prefix*) keeps working exactly as before.

#: A token FTS5 accepts bare: word characters, optionally a trailing '*'.
_BAREWORD_RE = re.compile(r"^\w+\*?$", re.UNICODE)
_FTS_OPERATORS = {"AND", "OR", "NOT"}


def fts_safe_query(query: str) -> str:
    """``query`` with every token FTS5 would read as syntax quoted as a
    phrase (``1110-2-1902`` -> ``"1110-2-1902"``); quoted phrases, the
    upper-case operators and bare words are kept. Stray quotes and brackets
    are dropped."""
    out: list[str] = []
    for m in re.finditer(r'"[^"]*"|\S+', str(query or "")):
        tok = m.group(0)
        if tok.startswith('"') and tok.endswith('"') and len(tok) >= 2:
            inner = tok[1:-1].strip()
            if inner:
                out.append(f'"{inner}"')
            continue
        tok = tok.strip('"()[]{}')
        if not tok:
            continue
        if tok in _FTS_OPERATORS or _BAREWORD_RE.match(tok):
            out.append(tok)
            continue
        words = re.findall(r"\w+", tok, re.UNICODE)
        if not words:
            continue
        out.append(f'"{" ".join(words)}"' if len(words) > 1 else words[0])
    # An operator cannot open or close the query.
    while out and out[0] in _FTS_OPERATORS:
        out.pop(0)
    while out and out[-1] in _FTS_OPERATORS:
        out.pop()
    return " ".join(out)


def plain_terms(query: str) -> str:
    """The query's words alone (letters and digits), for the OR fallback."""
    return " ".join(re.findall(r"[A-Za-z0-9]+", str(query or "")))


# ---------------------------------------------------------------------------
# How each hit matched (2026-11-10 review, core-05)
# ---------------------------------------------------------------------------
# When no section holds every word, the search relaxes: to the query with a
# named term swapped for its synonyms, then to any one of the words. Those
# hits used to look exactly like the hits that hold every word, and the note
# said "more match". Each hit that does not hold every word of the query (as
# run) now says so; the marks are worked out AFTER the hits are ranked and
# cut, so they can never move a hit.

#: The ``match`` mark of a hit that holds every word of the query, as typed
#: (given by ``search_sections``' fallback; a ``reference_search`` or
#: ``figure_search`` hit without a ``match`` mark holds every word).
MATCH_ALL_WORDS = "all words"
#: ... of a hit that holds every word, a named term as one of its synonyms.
MATCH_SYNONYMS = "synonyms"
#: ... of a hit that holds only some of the words (``lacks`` names the rest).
MATCH_ANY_WORD = "any word"


def query_words(query: str) -> list[str]:
    """The query's plain words (letters and digits), each once, as typed,
    leaving out the FTS5 operator words the any-word search leaves out."""
    seen: dict[str, str] = {}
    for w in plain_terms(query).split():
        if w.lower() not in _qe._FTS_OPS:
            seen.setdefault(w.lower(), w)
    return list(seen.values())


def match_marks(conn: sqlite3.Connection, table: str, rids: list,
                query: str) -> tuple[dict, list[str]]:
    """How each hit ``rids`` (rowids of FTS5 table ``table``) of a search
    for ``query``, as run, matched.

    Returns ``({rid: mark}, words_not_found)``. A hit that holds every
    word of the query gets no mark. Any other hit gets ``{"match":
    "synonyms"}`` when it holds every word with a named term as one of its
    synonyms (:func:`._query_expansion.substituted_query`); ``{"match":
    "all words", "not_as_phrase": [phrases]}`` when it holds every word
    but not a phrase the query was run with (a term typed with a hyphen or
    other punctuation runs as the phrase of its parts: 'Table 5-2 bearing'
    runs '"5 2"', and a caption with "5" and "2" apart holds every word,
    not that phrase; it was marked "any word" with nothing in ``lacks``,
    2026-11-10 review follow-up); else ``{"match": "any word", "lacks":
    [the query words it does not hold]}``. ``words_not_found`` lists the
    query words no hit holds; it is empty when every hit holds every word.
    Nothing is marked when the query cannot be run as an FTS5 expression
    here (an OperationalError)."""
    rids = [int(r) for r in rids]
    if not rids:
        return {}, []
    in_page = ",".join(str(r) for r in rids)

    def held(expr: str) -> set:
        return {r for (r,) in conn.execute(
            f"SELECT rowid FROM {table} WHERE {table} MATCH ? "
            f"AND rowid IN ({in_page})", (expr,))}

    try:
        literal = held(query)
        rest = [r for r in rids if r not in literal]
        if not rest:
            return {}, []
        words = query_words(query)
        has = {w: held(w) for w in words}
        sub = _qe.substituted_query(query)
        synonym = held(sub) if sub else set()
        phrases = list(dict.fromkeys(
            p for p in re.findall(r'"([^"]+)"', query) if " " in p.strip()))
        as_phrase = {p: held(f'"{p}"') for p in phrases}
    except sqlite3.OperationalError:
        return {}, []
    marks: dict = {}
    for r in rest:
        lacks = [w for w in words if r not in has[w]]
        if r in synonym:
            marks[r] = {"match": MATCH_SYNONYMS}
        elif not lacks and phrases:
            marks[r] = {"match": MATCH_ALL_WORDS, "not_as_phrase": [
                p for p in phrases if r not in as_phrase[p]]}
        else:
            marks[r] = {"match": MATCH_ANY_WORD, "lacks": lacks}
    return marks, [w for w in words if not has[w]]


def match_summary(marks: list[dict], words_not_found: list[str]) -> dict:
    """The keys a size-fitted result adds when some of its hits do not hold
    every word as the query was run (``marks``, those hits' marks):
    ``matched`` (the loosest: "any word" when any hit holds only some
    words, else "synonyms", else "all words" when the hits hold every
    word but not a phrase of the query), ``words_not_found`` when some
    query word is in no hit, and the sentence for the note. Empty when
    every hit holds the query as run."""
    if not marks:
        return {}
    kinds = {m["match"] for m in marks}
    out: dict = {"matched": next(
        k for k in (MATCH_ANY_WORD, MATCH_SYNONYMS, MATCH_ALL_WORDS)
        if k in kinds)}
    said = [f"{len(marks)} of these hits do not hold "
            + ("the query as typed" if MATCH_ALL_WORDS in kinds
               else "every word of the query")
            + ", and say so in 'match':"]
    if MATCH_ALL_WORDS in kinds:
        said.append("'all words' holds every word but not as the phrase "
                    "typed, which 'not_as_phrase' names (a term typed with "
                    "a hyphen is searched as the phrase of its parts);")
    if MATCH_SYNONYMS in kinds:
        said.append("'synonyms' holds every word with a named term as one "
                    "of its synonyms;")
    if MATCH_ANY_WORD in kinds:
        said.append("'any word' holds only some of the words, and 'lacks' "
                    "names the ones it does not hold;")
    said[-1] = said[-1].rstrip(";") + "."
    if words_not_found:
        out["words_not_found"] = list(words_not_found)
        said.append("No hit here holds "
                    + ", ".join(f"'{w}'" for w in words_not_found) + ".")
    out["sentence"] = " ".join(said)
    return out


def with_match_summary(out: dict, summary: dict) -> dict:
    """``out`` (a :func:`_retrieval.fit_hits` dict) with ``summary``
    (:func:`match_summary`) added: its keys, and its sentence on the
    note."""
    if not summary:
        return out
    sentence = summary.get("sentence", "")
    out.update({k: v for k, v in summary.items() if k != "sentence"})
    out["note"] = (out.get("note", "") + " " + sentence).strip()
    return out


#: What a search that relaxes tried before it gave up (absent_words_note).
TRIED_ALL = ("every word, then the synonyms of a named term, then any one of "
             "the words")


def absent_words_note(words: list[str], scope: str, tried: str = TRIED_ALL,
                      problems=()) -> dict:
    """What a size-fitted search that found nothing in a scope that exists
    adds: ``words_not_found`` (the query words no section or figure in the
    scope holds) and a ``note`` naming the scope and what was ``tried``,
    and any pack file of that scope the index skipped (core-10)."""
    note = f"Nothing in {scope} matches this query (tried {tried})."
    if words:
        note += (" No entry there holds "
                 + ", ".join(f"'{w}'" for w in words) + ".")
    else:
        note += (" Each word is in some entry there, but no entry holds "
                 "them as the query asks.")
    if problems:
        note += (" Some of its files were skipped when the index was built: "
                 + "; ".join(problems))
    out: dict = {"note": note}
    if words:
        out["words_not_found"] = list(words)
    return out


def search_fts_safely(search, query: str, retry=None):
    """``search(query)``; when FTS5 cannot parse the query, ``retry`` (default
    ``search``) on :func:`fts_safe_query` of it. A query that fails both ways
    raises the first error."""
    try:
        return search(query)
    except sqlite3.OperationalError as first:
        safe = fts_safe_query(query)
        if not safe or safe == query:
            raise
        try:
            return (retry or search)(safe)
        except sqlite3.OperationalError:
            raise first


def reference_get(reference: str, section_id: str,
                  include_subsections: bool = False) -> dict[str, Any]:
    """Fetch the full section by id, including body, key_points, equations.

    Works at every level: a chapter section (``"7.2"``) or a section
    nested inside it (``"7.2.1.3.1"``). The result is the section's own
    text; the sections under it are listed in ``children`` by number and
    title, to be fetched by their own ids.

    Parameters
    ----------
    reference : str
        Reference id (e.g. ``"dm7_1"``), another spelling of it
        (``"gec12"``) or a report number its files carry, read as
        :func:`reference_search` reads it (:func:`resolve_name`). A name
        that means nothing, ``"dm7"``, or a number that could be several
        is a ``KeyError`` with the search's refusal.
    section_id : str
        Section id as it appears in the source (e.g. ``"4-2.1"``,
        ``"5.3"``, ``"P-1"``, ``"7.2.1.3.1"``).
    include_subsections : bool, optional
        Inline the sections under it as ``subsections`` (each with its
        own), as long as the whole result stays within
        ``_retrieval.SUBSECTIONS_INLINE_MAX_CHARS`` (12,000) characters;
        past that they stay listed in ``children`` and a ``note`` says
        so. Default False.

    Returns
    -------
    dict
        Full section dict, plus ``parent_id``, ``under`` (the sections
        above it) and ``children`` (``section_id`` and ``title`` of each
        section directly under it).

    Raises
    ------
    KeyError
        If no such section exists; the message names the nearest section
        above that number, any sections numbered under it, and the
        sections that carry it under a part or appendix letter ('2.3.5'
        -> 'II-2.3.5'). Also if more than one section of the reference
        holds that number: the message names each, and neither is
        returned (before, the first one indexed was).
    TypeError
        If ``section_id`` is not text (a number loses its trailing zero:
        7.10 arrives as 7.1, another section).
    """
    _retrieval.require_text_id(section_id)
    conn = _ro_connect()
    try:
        # another spelling or a report number reads as the searches read it
        if not _is_indexed(conn, reference):
            reference = resolve_name(
                reference, _held(conn),
                lambda name: _unknown_reference(conn, name))
        rows = conn.execute(
            "SELECT * FROM sections WHERE reference = ? "
            "AND section_id = ? ORDER BY rowid LIMIT 9",
            (reference, section_id),
        ).fetchall()
        if not rows:
            raise KeyError(
                f"section_id '{section_id}' not found in reference "
                f"'{reference}'" + _nearby(conn, reference, section_id)
            )
        if len(rows) > 1:
            raise KeyError(_retrieval.held_twice_note(
                reference, section_id,
                [(r["chapter"], r["title"]) for r in rows]))
        row = rows[0]
        out = _row_to_full(row)
        out["children"] = [
            {"section_id": c["section_id"], "title": c["title"]}
            for c in _child_rows(conn, row["rowid"])]
        if include_subsections:
            out = _retrieval.inline_subsections(
                out, _subtree(conn, row["rowid"], {row["rowid"]}))
        # the section a chapter prints under the same number (GEC-13
        # chapter 1's printed 8.2.7 is 1.8.2.7), as retrieve_section says
        return _retrieval.with_printed_note(
            out, reference, _retrieval.prefixed_matches(
                reference, section_id, _title_of(conn, reference)))
    finally:
        conn.close()


def _title_of(conn: sqlite3.Connection, reference: str):
    """A function giving the title of a section id of ``reference``, or
    None when the reference holds no such id."""
    def title(section_id: str):
        r = conn.execute(
            "SELECT title FROM sections WHERE reference = ? AND "
            "section_id = ? ORDER BY rowid LIMIT 1",
            (reference, section_id)).fetchone()
        return None if r is None else r["title"]
    return title


def _nearby(conn: sqlite3.Connection, reference: str,
            section_id: str) -> str:
    """For a section number that is not there: the nearest section above
    it, and up to eight sections numbered under it
    (:func:`_retrieval.nearby_note`)."""
    above = None
    for pid in _retrieval.id_prefixes(section_id):
        r = conn.execute(
            "SELECT section_id, title FROM sections WHERE reference = ? "
            "AND section_id = ? ORDER BY rowid LIMIT 1",
            (reference, pid),
        ).fetchone()
        if r is not None:
            above = (r["section_id"], r["title"])
            break
    below = conn.execute(
        "SELECT section_id, title FROM sections WHERE reference = ? "
        "AND (section_id LIKE ? OR section_id LIKE ?) ORDER BY rowid "
        "LIMIT 8",
        (reference, f"{section_id}.%", f"{section_id}-%"),
    ).fetchall()
    lettered = conn.execute(
        "SELECT section_id, title FROM sections WHERE reference = ? "
        "AND section_id LIKE ? ORDER BY rowid",
        (reference, f"%-{section_id}"),
    ).fetchall()
    return _retrieval.nearby_note(
        above, [(r["section_id"], r["title"]) for r in below],
        _retrieval.lettered_matches(
            section_id, [(r["section_id"], r["title"]) for r in lettered]),
        _retrieval.prefixed_matches(reference, section_id,
                                    _title_of(conn, reference)),
        reference)


def reference_query(sql: str, limit: int = _MAX_LIMIT,
                    max_chars: int | None = None):
    """Run a read-only SELECT against the retrieval DB.

    Tables available:

    - ``sections`` — one row per section, at every level. Columns:
      ``rowid``, ``reference``, ``reference_title``, ``chapter``,
      ``chapter_title``, ``section_id``, ``title``, ``summary``, ``body``,
      ``key_points``, ``applicability``, ``equations_json``,
      ``figures_json``, ``tables_json``, ``parent_rowid`` (the row of the
      section above it, NULL at the top level), ``depth`` (0 at the top
      level) and ``parents_json`` (``[[section_id, title], ...]`` above
      it, outermost first).
    - ``sections_fts`` — FTS5 virtual table over title/summary/body/
      key_points/applicability. Use ``sections_fts MATCH '...'``.

    Only ``SELECT`` (and top-level ``WITH ... SELECT``) statements are
    accepted. The connection is opened read-only and the result set is
    capped at ``limit`` rows (max ``50``).

    Parameters
    ----------
    sql : str
        SELECT statement.
    limit : int, optional
        Max rows to return (default and max ``50``).
    max_chars : int, optional
        The largest result the caller can take, in JSON characters (50
        rows of ``SELECT *`` run past 250,000). With it the result is
        ``{"rows": [...], "shown": n}``: whole rows, as many as fit; when
        not even the first fits, that row with its longest text values
        cut (named in the note). When rows are left out or cut it adds
        ``left_out`` and a ``note`` (select fewer or shorter columns, or
        page with ``LIMIT``/``OFFSET`` in the SQL); an error is
        ``{"error": ...}``.

    Returns
    -------
    list of dict, or dict with ``max_chars``
        Result rows as dicts. On a query error, returns a single-element
        list ``[{"error": "..."}]``. With ``max_chars``, the dict described
        above.
    """
    def refuse(message):
        return ([{"error": message}] if max_chars is None
                else {"error": message})

    if not sql or not sql.strip():
        return refuse("empty query")
    if not _SELECT_ONLY_RE.match(sql):
        return refuse("only SELECT (or WITH ... SELECT) statements allowed")
    if _FORBIDDEN_RE.search(sql):
        return refuse("query contains forbidden keyword")
    if ";" in sql.rstrip(";\n\r\t "):
        return refuse("multiple statements not allowed")
    limit = max(1, min(int(limit), _MAX_LIMIT))
    conn = _ro_connect()
    try:
        try:
            cur = conn.execute(sql)
        except sqlite3.OperationalError as e:
            return refuse(f"SQL error: {e}")
        rows = [dict(r) for r in cur.fetchmany(limit)]
        if max_chars is None:
            return rows
        return _fit_rows(rows, max_chars)
    finally:
        conn.close()


def _fit_rows(rows: list[dict], max_chars: int) -> dict[str, Any]:
    """``reference_query``'s rows fitted to ``max_chars`` (whole rows; the
    first cut when even it does not fit; an error when even cut it does
    not, as a row of very many columns)."""
    budget = max_chars - _retrieval._ENVELOPE_CHARS
    kept: list = []
    size = 2
    for r in rows:
        s = _retrieval.json_size(r) + (2 if kept else 0)
        if size + s > budget:
            break
        kept.append(r)
        size += s
    cut: dict = {}
    if not kept and rows:
        first, cut = _retrieval.fit_record(rows[0], budget - 2)
        if _retrieval.json_size([first]) > budget:
            return {"error": (
                f"One row of this query is {_retrieval.json_size(rows[0]):,} "
                f"characters and, with every long value cut, still over the "
                f"{max_chars:,}-character limit ({len(rows[0])} columns): "
                "select fewer columns (name the ones you need, not *).")}
        kept = [first]
    out: dict[str, Any] = {"rows": kept, "shown": len(kept)}
    left_out = len(rows) - len(kept)
    if not (left_out or cut):
        return out
    out["left_out"] = left_out
    notes = []
    if left_out:
        notes.append(
            f"{len(kept)} of the {len(rows)} rows are shown: the rest would "
            f"not fit in {max_chars:,} characters. Select fewer or shorter "
            "columns (substr(body, 1, 500), not body), or page with LIMIT "
            f"and OFFSET in the SQL (raise its OFFSET by {len(kept)} for the "
            "next rows).")
    if cut:
        notes.append(
            "The first row alone would not fit, so its longest values are "
            "cut: " + ", ".join(f"{k} (from {n:,} characters)"
                                for k, n in cut.items())
            + ". reference_get returns a section's whole text.")
    out["note"] = " ".join(notes)
    return out


def list_indexed_references() -> list[dict[str, Any]]:
    """Inventory of references currently indexed in the FTS DB.

    Useful for agents to discover what's available before searching. One
    entry per reference: ``reference``, ``reference_title`` (its first
    chapter file's), ``n_chapters``, ``n_sections``; a reference whose
    files carry more than one title (a manual in volumes) also has
    ``reference_titles``, each once, in file order. Before the 2026-11-10
    review (core-13) such a reference was listed once per title, each
    entry counting only that title's chapters. With local reference packs
    set (REF-64), a pack whose
    files the index skipped in part carries ``problems`` (what was skipped
    and why), and a pack skipped whole, or none of whose chapter files
    could be indexed, is listed too, with no sections and its ``problems``
    (2026-11-10 review, core-10: they were left out without a word). A
    folder the setting names that is not there is listed the same way,
    under the folder as written.
    """
    conn = _ro_connect()
    try:
        # one entry per reference: a manual whose volumes' files carry
        # titles of their own was listed once per title, each with a part
        # of its chapters (2026-11-10 review, core-13)
        rows = [dict(r) for r in conn.execute(
            "SELECT reference, "
            "(SELECT t.reference_title FROM sections t "
            " WHERE t.reference = s.reference ORDER BY t.rowid LIMIT 1) "
            "AS reference_title, "
            "COUNT(DISTINCT chapter) AS n_chapters, "
            "COUNT(*) AS n_sections "
            "FROM sections s GROUP BY reference ORDER BY reference"
        ).fetchall()]
        titles: dict[str, list] = {}
        for ref, title in conn.execute(
                "SELECT reference, reference_title FROM sections "
                "ORDER BY rowid"):
            seen = titles.setdefault(ref, [])
            if title not in seen:
                seen.append(title)
    finally:
        conn.close()
    for r in rows:
        if len(titles.get(r["reference"], [])) > 1:
            r["reference_titles"] = titles[r["reference"]]
    listed = {r["reference"]: r for r in rows}
    for key, problems in _packs.problems_by_pack().items():
        if key in listed:
            listed[key]["problems"] = problems
        else:
            rows.append({"reference": key, "reference_title": "",
                         "n_chapters": 0, "n_sections": 0,
                         "problems": problems})
    return rows


def rebuild_db() -> dict[str, Any]:
    """Force-rebuild the FTS DB and return summary stats."""
    db = _db_path()
    _build_db(db)
    return {"db_path": str(db), "indexed": list_indexed_references()}
