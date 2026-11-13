"""SQLite FTS5 retrieval layer for the table catalogs (app BACKLOG REF-86,
REF-34).

The companion of :mod:`geotech_references._figures_db` for printed TABLES.
It indexes every ``<reference>/tables_catalog.json`` written by
``scripts/build_table_catalog.py`` and gives every printed table what a
figure has: a way to find it by its caption or number, and the page it is
printed on, so that a table whose cells are not typed in anywhere can still
be read off the rendered page.

- ``table_search(query, reference=None, chapter=None, limit=5)`` -- ranked
  BM25 hits over table numbers, captions and the title of the section that
  lists the table.
- ``table_get(reference, table_number)`` -- the whole catalog row of one
  table, with ``pdf_path`` and ``pdf_page_index`` for reading the page.
- ``resolve_table_pdf(reference, table_number)`` -- ``(pdf_abs_path,
  page_index)``.
- ``list_indexed_tables()`` -- the references with a table catalog.

Each row says where the table's values can be had (``values``):

- ``"text"``: its cells are typed in a stored section (``values_in`` is the
  section id; ``reference_get`` returns it);
- ``"lookup"``: a coded function returns them (``values_in`` is
  ``"module.function"``; ``lookup_reference`` runs it);
- ``"page"``: only on the printed page (render ``pdf_page_index`` of
  ``pdf_path`` and read it; a table that runs over several sheets lists
  them all in ``pages``).

The database is built lazily into the temp folder on first call, under a
temporary name and moved into place (:mod:`._atomic_db`), and rebuilt when a
catalog is added, removed or changed (the source signature kept in
``build_meta``), exactly as the figure database is. It is not committed.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

from . import _atomic_db
from . import _query_expansion as _qe
from ._retrieval import fit_hits, fit_record
from ._retrieval_db import (SHARED_NAMES, TRIED_ALL, absent_words_note,
                            db_meta, id_key, keyed_db_path, match_marks,
                            match_summary, plain_terms, query_words,
                            scope_clause, search_fts_safely, search_scope,
                            source_state, unreadable_source,
                            with_match_summary, with_scope, write_build_meta)

_PACKAGE_DIR = Path(__file__).parent
_REPO_ROOT = _PACKAGE_DIR.parent
_DB_NAME = "geotech_references_tables_fts.sqlite"
_CATALOG_NAME = "tables_catalog.json"
_MAX_LIMIT = 50
_DEFAULT_SEARCH_LIMIT = 5
_MAX_OFFSET = 500  # deepest page table_search reaches

#: Where a table's values are (a row's ``values``).
VALUES_TEXT = "text"
VALUES_LOOKUP = "lookup"
VALUES_PAGE = "page"
VALUES_KINDS = (VALUES_TEXT, VALUES_LOOKUP, VALUES_PAGE)


# ---------------------------------------------------------------------------
# DB build
# ---------------------------------------------------------------------------

def _db_path() -> Path:
    return keyed_db_path(_DB_NAME, _PACKAGE_DIR)


def _iter_catalogs() -> list[Path]:
    """Every ``<reference>/tables_catalog.json`` in the package."""
    out: list[Path] = []
    for ref_dir in sorted(_PACKAGE_DIR.iterdir()):
        if not ref_dir.is_dir():
            continue
        cat = ref_dir / _CATALOG_NAME
        if cat.is_file():
            out.append(cat)
    return out


#: Layout of the tables database, kept in ``PRAGMA user_version``.
_SCHEMA_VERSION = 1


def _needs_rebuild(db_path: Path) -> bool:
    """Whether the tables database at ``db_path`` must be built (again): it
    is not there, a catalog is newer than it, or the catalogs are not the
    ones it was built from (one deleted, added or restored with an older
    date), as for the figure database (core-11)."""
    if not db_path.exists():
        return True
    newest, signature = source_state(_iter_catalogs())
    if db_path.stat().st_mtime < newest:
        return True
    version, built_from = db_meta(db_path)
    return version != _SCHEMA_VERSION or built_from != signature


def _build_db(db_path: Path) -> Path:
    """Build the database and move it into place at ``db_path`` (REF-56)."""
    return _atomic_db.build_atomically(
        db_path, _fill_db, is_current=lambda p: not _needs_rebuild(p))


def _fill_db(conn: sqlite3.Connection) -> None:
    """Create the tables and index every catalog into ``conn``."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE tables (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT NOT NULL,
            reference_id TEXT,
            reference_title TEXT,
            volume INTEGER,
            table_number TEXT,
            caption TEXT,
            section_title TEXT,
            chapter INTEGER,
            section_id TEXT,
            pdf_path TEXT,
            pdf_page_index INTEGER,
            pages TEXT,
            printed_page TEXT,
            page_estimated INTEGER,
            value_source TEXT,
            values_in TEXT,
            implemented_in TEXT,
            printed_as_picture INTEGER,
            note TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE VIRTUAL TABLE tables_fts USING fts5(
            table_number, caption, section_title,
            content='tables',
            content_rowid='rowid',
            tokenize='porter unicode61'
        )
        """
    )
    cur.execute("CREATE INDEX idx_tab_ref ON tables(reference)")
    cur.execute("CREATE INDEX idx_tab_ref_chap ON tables(reference, chapter)")
    cur.execute("CREATE INDEX idx_tab_ref_num ON tables(reference, table_number)")

    sources = _iter_catalogs()
    write_build_meta(cur, source_state(sources)[1], _SCHEMA_VERSION)
    for cat_path in sources:
        try:
            data = json.loads(cat_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            raise unreadable_source(cat_path, e) from e
        _index_catalog(cur, data.get("package", cat_path.parent.name), data)

    cur.execute(
        """
        INSERT INTO tables_fts(rowid, table_number, caption, section_title)
        SELECT rowid, table_number, caption, section_title FROM tables
        """
    )


def _index_catalog(cur: sqlite3.Cursor, reference: str, data: dict) -> None:
    """Insert one table catalog's rows into ``tables``."""
    ref_id = data.get("reference_id", "")
    ref_title = data.get("reference_title", "")
    volume = data.get("volume")
    pdf_path = data.get("pdf_path", "")
    for row in data.get("tables", []):
        if not isinstance(row, dict):
            continue
        first = row.get("pdf_page_index")
        pages = row.get("pages") or ([first] if first is not None else [])
        impl = row.get("implemented_in") or []
        cur.execute(
            """
            INSERT INTO tables (
                reference, reference_id, reference_title, volume,
                table_number, caption, section_title, chapter, section_id,
                pdf_path, pdf_page_index, pages, printed_page,
                page_estimated, value_source, values_in, implemented_in,
                printed_as_picture, note
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                # a volume printed under its own number carries it per row
                reference, row.get("reference_id") or ref_id, ref_title,
                row.get("volume", volume),
                row.get("table_number", ""),
                row.get("caption", ""),
                row.get("section_title", "") or "",
                row.get("chapter"),
                row.get("section_id"),
                row.get("pdf_path") or pdf_path,
                first,
                json.dumps(pages),
                (None if row.get("printed_page") is None
                 else str(row.get("printed_page"))),
                1 if row.get("page_estimated") else 0,
                row.get("values") or VALUES_PAGE,
                row.get("values_in"),
                json.dumps(impl) if impl else None,
                1 if row.get("printed_as_picture") else 0,
                row.get("note") or None,
            ),
        )


def _ensure_db() -> Path:
    return _atomic_db.ensure_built(_db_path(), _needs_rebuild, _fill_db)


def _ro_connect() -> sqlite3.Connection:
    db = _ensure_db()
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Table numbers
# ---------------------------------------------------------------------------

_DASHES = "‐‑‒–—−"


def _norm_table_number(s: str) -> str:
    """A table id as filed, for lookup: no "Table" / "Tab." in front, dashes
    as '-', no spaces, upper case ('Table 4-12', 'TABLE 4–1', ' 4-12 '
    -> '4-12')."""
    s = str(s or "").strip()
    s = re.sub(r"(?i)^(?:table|tab\.?)\s*", "", s)
    s = re.sub(f"[{_DASHES}]", "-", s)
    s = re.sub(r"\s+", "", s)
    return s.strip(" .:").upper()


def _table_number_keys(s: str) -> tuple:
    """The forms a table id is looked up by: itself and, for a part letter
    printed in brackets, the plain letter the catalogs file ('4-1(a)' ->
    '4-1A')."""
    num = _norm_table_number(s)
    plain = re.sub(r"\(([A-Z])\)$", r"\1", num)
    return (num, plain) if plain != num else (num,)


def _number_clause(keys: tuple) -> str:
    return "UPPER(table_number) IN (" + ", ".join("?" * len(keys)) + ")"


def _loose_clause(keys: tuple) -> str:
    """The same, with '.' and '-' read alike ('3-1A' finds GEC-7's '3.1a'),
    tried only when the number as given finds nothing."""
    return ("REPLACE(UPPER(table_number), '.', '-') IN ("
            + ", ".join("?" * len(keys)) + ")")


def _loose(keys: tuple) -> tuple:
    return tuple(dict.fromkeys(k.replace(".", "-") for k in keys))


# ---------------------------------------------------------------------------
# References
# ---------------------------------------------------------------------------

def _catalog_refs(conn: sqlite3.Connection) -> list[tuple[str, str, tuple]]:
    """``(reference, reference_title, report numbers)`` of every catalog,
    each catalog once (a manual whose volumes carry their own report
    numbers has several)."""
    rows = conn.execute(
        "SELECT DISTINCT reference, reference_title, reference_id "
        "FROM tables ORDER BY rowid").fetchall()
    titles: dict[str, str] = {}
    numbers: dict[str, list[str]] = {}
    for r in rows:
        titles.setdefault(r["reference"], r["reference_title"] or "")
        held = numbers.setdefault(r["reference"], [])
        if r["reference_id"] and r["reference_id"] not in held:
            held.append(r["reference_id"])
    return [(ref, titles[ref], tuple(numbers[ref])) for ref in titles]


def _reference_candidates(conn: sqlite3.Connection,
                          reference: str) -> list[str]:
    """The catalog ids a caller's ``reference`` can mean, read as the figure
    layer reads it (:func:`._figures_db._reference_candidates`): the id,
    another spelling of it (``gec10``), the app's module name for a manual
    in two catalogs (``dm7``), or a report number its rows carry. A number
    that could be more than one raises ``KeyError`` naming them."""
    refs = _catalog_refs(conn)
    ids = [r[0] for r in refs]
    if reference in ids:
        return [reference]
    key = id_key(reference)
    if not key:
        return []
    shared = [r for r in SHARED_NAMES.get(key, ()) if r in ids]
    if shared and not any(id_key(r) == key for r in ids):
        return shared
    found, _numbers, error = search_scope(reference, refs)
    if error:
        raise KeyError(error)
    return found


def _unknown_reference(conn: sqlite3.Connection, reference: str) -> str:
    """What a lookup says for a ``reference`` that names no table catalog."""
    valid = sorted(r[0] for r in _catalog_refs(conn))
    return (f"no table catalog '{reference}'. Use a catalog id: "
            f"{', '.join(valid)} (or table_search with no reference to "
            "find the table)")


def _rows_for(conn: sqlite3.Connection, reference: str, keys: tuple) -> list:
    rows = conn.execute(
        "SELECT * FROM tables WHERE reference = ? AND "
        + _number_clause(keys) + " ORDER BY rowid",
        (reference, *keys)).fetchall()
    if not rows:
        loose = _loose(keys)
        rows = conn.execute(
            "SELECT * FROM tables WHERE reference = ? AND "
            + _loose_clause(loose) + " ORDER BY rowid",
            (reference, *loose)).fetchall()
    return rows


def resolve_reference(reference: str, table_number: str | None = None) -> str:
    """The catalog id ``reference`` means; when it could mean several
    catalogs (``dm7``), the one holding ``table_number``.

    Raises ``KeyError`` naming the valid ids, or the candidates when the
    table is in more than one of them."""
    conn = _ro_connect()
    try:
        cands = _reference_candidates(conn, reference)
        if len(cands) == 1:
            return cands[0]
        if not cands:
            raise KeyError(_unknown_reference(conn, reference))
        if table_number:
            keys = _table_number_keys(table_number)
            holding = [c for c in cands if _rows_for(conn, c, keys)]
            if len(holding) == 1:
                return holding[0]
            if holding:
                shown = []
                for c in holding:
                    row = _rows_for(conn, c, keys)[0]
                    shown.append(f"{c} ({str(row['reference_title'])[:40]}: "
                                 f"{str(row['caption'])[:70]})")
                raise KeyError(
                    f"'{reference}' table {table_number} exists in more "
                    f"than one catalog -- {'; '.join(shown)}. Give the id of "
                    "the one you mean")
        raise KeyError(
            f"'{reference}' could mean {', '.join(cands)}: give one of those "
            "ids")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Rows
# ---------------------------------------------------------------------------

def _pages(row) -> list:
    try:
        pages = json.loads(row["pages"] or "[]")
    except (TypeError, ValueError):
        pages = []
    return pages or ([row["pdf_page_index"]]
                     if row["pdf_page_index"] is not None else [])


def _row_to_hit(row: sqlite3.Row) -> dict[str, Any]:
    out = {
        "reference": row["reference"],
        "reference_title": row["reference_title"],
        "table_number": row["table_number"],
        "caption": row["caption"],
        "chapter": row["chapter"],
        "section_id": row["section_id"],
        "pdf_page_index": row["pdf_page_index"],
        "printed_page": row["printed_page"],
        "values": row["value_source"],
        "values_in": row["values_in"],
        # the volume's own report number where the volumes carry their own
        "reference_id": row["reference_id"],
    }
    pages = _pages(row)
    if len(pages) > 1:
        out["pages"] = pages
    return out


def _row_to_full(row: sqlite3.Row) -> dict[str, Any]:
    out = _row_to_hit(row)
    out.update({
        "volume": row["volume"],
        "section_title": row["section_title"] or None,
        "pdf_path": row["pdf_path"],
        "pages": _pages(row),
        "page_estimated": bool(row["page_estimated"]),
    })
    if row["implemented_in"]:
        out["implemented_in"] = json.loads(row["implemented_in"])
    if row["printed_as_picture"]:
        out["printed_as_picture"] = True
    if row["note"]:
        out["note"] = row["note"]
    out["how_to_read"] = _how_to_read(out)
    return out


def _how_to_read(rec: dict) -> str:
    """One sentence on where this table's values are."""
    if rec["values"] == VALUES_TEXT:
        return (f"Its cells are typed in section {rec['values_in']} of "
                f"{rec['reference']} (reference_get).")
    if rec["values"] == VALUES_LOOKUP:
        return (f"A coded lookup returns it: {rec['values_in']} "
                f"(lookup_reference on {rec['reference']}).")
    pages = rec.get("pages") or [rec["pdf_page_index"]]
    where = ("page index " + str(pages[0]) if len(pages) == 1 else
             "page indexes " + ", ".join(str(p) for p in pages))
    return (f"Its values are only on the printed page: read {where} of "
            f"{rec['pdf_path']} (the page-reading tool renders it).")


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

_or_fallback = _qe.or_fallback


def table_search(
    query: str,
    reference: str | None = None,
    chapter: int | None = None,
    limit: int = _DEFAULT_SEARCH_LIMIT,
    offset: int = 0,
    max_chars: int | None = None,
):
    """Full-text search of the table catalogs by number, caption and the
    title of the section that lists the table.

    Parameters
    ----------
    query : str
        FTS5 MATCH query, words matched with porter stemming. The tables
        whose number, caption or section title holds every word come first;
        unless the expansion strategy is ``"off"``, tables holding a synonym
        of a named term are added; and the places left are filled by tables
        holding any one of the words. A hit that does not hold every word
        says so in ``match``. FTS5 operators work.
    reference : str, optional
        Restrict to one reference id (``"dm7_2"``), another spelling of it
        (``"GEC-10"``), or a report number its rows carry, read as
        :func:`._figures_db.figure_search` reads it. A volume's own report
        number searches that volume alone. A name that means no catalog is
        an error naming the catalog ids, not an empty result; ``"dm7"`` (two
        catalogs) is an error naming ``dm7_1`` and ``dm7_2``.
    chapter : int or str, optional
        Restrict to one chapter as the catalog files it (prologue tables
        are chapter 0; appendix tables have none). A chapter with no tables
        in the scope is an error naming the chapters that have some.
    limit : int, optional
        Max hits (capped at 50).
    offset : int, optional
        Skip this many of the best hits first (the next page); past 500 the
        result is an error saying to narrow the query.
    max_chars : int, optional
        The largest result the caller can take, in JSON characters. With it
        the result is a dict of the hits that fit
        (:func:`._retrieval.fit_hits`) with ``next_offset`` and a ``note``
        when some are not shown, the ``match`` summary, and for an empty
        result the scope and the words no table there holds. An error is
        ``{"error": ...}``.

    Returns
    -------
    list of dict, or dict with ``max_chars``
        Ranked hits, each with ``reference``, ``reference_title``,
        ``table_number``, ``caption``, ``chapter``, ``section_id``,
        ``pdf_page_index``, ``printed_page``, ``values`` (``"text"``,
        ``"lookup"`` or ``"page"``), ``values_in`` and ``reference_id``; a
        table printed over several pages also ``pages``. Each table is one
        hit whatever its number of sheets. Call :func:`table_get` for the
        whole row. An unknown ``reference`` or ``chapter`` is
        ``[{"error": ...}]`` (``{"error": ...}`` with ``max_chars``).
    """
    if not query or not query.strip():
        return [] if max_chars is None else {"hits": [], "shown": 0}
    limit = max(1, min(int(limit), _MAX_LIMIT))
    offset = max(0, int(offset or 0))
    if offset > _MAX_OFFSET:
        message = (f"offset={offset} is past the deepest page this search "
                   f"gives (its offset goes no higher than {_MAX_OFFSET}): "
                   "narrow the query (more specific words, or a "
                   "'reference') instead.")
        return {"error": message} if max_chars is not None \
            else [{"error": message}]
    want = limit if not (offset or max_chars is not None) \
        else offset + limit + 1
    conn = _ro_connect()
    try:
        def refuse(message: str):
            return ({"error": message} if max_chars is not None
                    else [{"error": message}])

        refs: list = []
        numbers: list = []
        held: list = []
        if reference:
            held = _catalog_refs(conn)
            refs, numbers, error = search_scope(reference, held)
            if error:
                return refuse(error)
            if not refs:
                return refuse(_unknown_reference(conn, reference))
        in_scope, scope_params = scope_clause("t", refs, numbers)
        chapters: list = []
        if chapter is not None:
            have = [r[0] for r in conn.execute(
                "SELECT DISTINCT chapter FROM tables t WHERE 1" + in_scope,
                scope_params) if r[0] is not None]
            chapters = [c for c in have if str(c) == str(chapter).strip()]
            if not chapters:
                have.sort(key=lambda c: (isinstance(c, str), c))
                where = (", ".join(refs) if refs else "any catalog")
                return refuse(
                    f"no tables filed under chapter {chapter!r} in {where}; "
                    "chapters with tables there: "
                    + ", ".join(str(c) for c in have[:40])
                    + " (appendix tables may have no chapter: search "
                    "without one)")

        def run(match_query: str) -> list[sqlite3.Row]:
            sql = (
                "SELECT t.rowid AS rid, t.* "
                "FROM tables_fts x JOIN tables t ON t.rowid = x.rowid "
                "WHERE tables_fts MATCH ?"
            )
            params: list[Any] = [match_query]
            sql += in_scope
            params.extend(scope_params)
            if chapters:
                sql += (" AND t.chapter IN ("
                        + ", ".join("?" for _ in chapters) + ")")
                params.extend(chapters)
            sql += " ORDER BY bm25(tables_fts) LIMIT ?"
            params.append(want)
            return conn.execute(sql, params).fetchall()

        row_key = lambda r: r["rid"]  # noqa: E731 - one row per table
        strategy = _qe.EXPANSION_STRATEGY
        ran = {"q": query}

        def search(q: str, relaxed: bool = False) -> list[sqlite3.Row]:
            ran["q"] = q
            if strategy == "rerank":
                rows = run(_qe.combined_query(q))
            elif strategy == "auto":
                literal = run(q)
                combined = _qe.combined_query(q)
                if combined == q:
                    rows = literal
                elif not literal:
                    rows = _qe.zero_literal_hits(q, run, want, row_key)
                else:
                    rows = _qe.merge_hits(literal[:_qe.EXPANSION_PIN],
                                          run(combined), want, key=row_key)
            else:
                rows = run(q)
                if strategy == "fill" and len(rows) < want:
                    expansion = _qe.expand_query(q)
                    if expansion:
                        rows = _qe.merge_hits(rows, run(expansion), want,
                                              key=row_key)
            if len(rows) < want:
                fb = _or_fallback(q)
                if not fb and relaxed:
                    fb = _or_fallback(plain_terms(q))
                if fb and fb != q:
                    rows = _qe.merge_hits(rows, run(fb), want, key=row_key)
            return rows

        try:
            rows = search_fts_safely(
                search, query, retry=lambda q: search(q, relaxed=True))
        except sqlite3.OperationalError as e:
            return refuse(f"FTS query error: {e}")
        more = len(rows) > offset + limit
        page = rows[offset:offset + limit]
        marks, absent = match_marks(conn, "tables_fts",
                                    [r["rid"] for r in page], ran["q"])
        hits = []
        for r in page:
            hit = _row_to_hit(r)
            hit.update(marks.get(r["rid"], {}))
            hits.append(hit)
        if max_chars is None:
            return hits
        if not rows:
            scope = ("the table catalog of " + ", ".join(refs) if refs
                     else "the table catalogs")
            if numbers:
                scope += f" ({', '.join(numbers)})"
            if chapters:
                scope += f", chapter {chapter}"
            tried = TRIED_ALL if strategy != "off" else (
                "every word, then any one of the words; synonyms are off: "
                "GEOTECH_RETRIEVAL_EXPANSION=off")
            out = dict({"hits": [], "shown": 0}, **absent_words_note(
                _words_in_no_table(conn, ran["q"], refs, chapters, numbers),
                scope, tried))
        else:
            out = with_match_summary(fit_hits(
                hits, max_chars, text_fields=("caption",), offset=offset,
                more=more, max_offset=_MAX_OFFSET,
                narrow=("narrow the query (more specific words, or a "
                        "'reference')"),
                fetch="table_get returns a table's whole catalog row",
                more_text="more match" if not marks else "more were found"),
                match_summary(list(marks.values()), absent))
        return with_scope(out, reference, refs, numbers, held, "tables")
    finally:
        conn.close()


def _words_in_no_table(conn: sqlite3.Connection, query: str, refs: list,
                       chapters: list, numbers: list = ()) -> list:
    """The query's words that no catalog row in the scope holds."""
    in_scope, scope_params = scope_clause("t", refs, list(numbers))
    out = []
    for w in query_words(query):
        sql = ("SELECT 1 FROM tables_fts x JOIN tables t "
               "ON t.rowid = x.rowid WHERE tables_fts MATCH ?" + in_scope)
        params: list[Any] = [w] + scope_params
        if chapters:
            sql += (" AND t.chapter IN ("
                    + ", ".join("?" for _ in chapters) + ")")
            params.extend(chapters)
        try:
            if conn.execute(sql + " LIMIT 1", params).fetchone() is None:
                out.append(w)
        except sqlite3.OperationalError:
            continue
    return out


# ---------------------------------------------------------------------------
# Get / resolve
# ---------------------------------------------------------------------------

def _page_label(row: sqlite3.Row) -> str:
    printed = (f" (printed page {row['printed_page']})"
               if row["printed_page"] not in (None, "") else "")
    return (f"page index {row['pdf_page_index']}{printed} "
            f"\"{str(row['caption'] or '')[:80]}\"")


def table_get(reference: str, table_number: str,
              pdf_page_index: int | None = None,
              max_chars: int | None = None) -> dict[str, Any]:
    """Fetch the whole catalog row of one table.

    Parameters
    ----------
    reference : str
        Reference id (``"dm7_2"``); other spellings resolve as for
        :func:`._figures_db.figure_get`: ``gec10``, ``dm7`` (whichever of
        ``dm7_1`` / ``dm7_2`` holds the table), or the document's
        designation (``UFC 3-250-01``).
    table_number : str
        Table id as printed (``"6-11"``, ``"A.7"``, ``"C-2a"``); a leading
        ``"Table "`` is tolerated, and '.' and '-' are read alike when the
        number as given is not filed.
    pdf_page_index : int, optional
        Which table, for a number the catalog holds more than once (two
        tables printed under one number, or one number in two volumes): any
        page of the table wanted (a search hit carries it).
    max_chars : int, optional
        The largest result the caller can take, in JSON characters; a row
        longer than that comes back with its caption cut and a ``note``.

    Returns
    -------
    dict
        The row: ``table_number``, ``caption``, ``chapter``, ``section_id``
        and ``section_title`` (the stored section that lists or prints it,
        or None), ``pdf_path``, ``pdf_page_index`` (0-based, the page where
        the table starts), ``pages`` (every page it is printed on),
        ``printed_page``, ``values`` and ``values_in`` (where its values
        are, module docstring), ``implemented_in`` (every coded lookup of
        it, where there is one), ``printed_as_picture`` (no text layer on
        its page), ``note``, and ``how_to_read``, one sentence on where its
        values are.

    Raises
    ------
    KeyError
        If no such table exists (naming the nearest numbers), or the
        catalog holds the number more than once and ``pdf_page_index`` does
        not say which (naming each row's page and caption).
    """
    keys = _table_number_keys(table_number)
    ref = resolve_reference(reference, table_number)
    conn = _ro_connect()
    try:
        rows = _rows_for(conn, ref, keys)
        if rows and pdf_page_index is not None:
            on_page = [r for r in rows if int(pdf_page_index) in _pages(r)]
            if not on_page:
                raise KeyError(
                    f"table '{table_number}' of '{ref}' is not on page "
                    f"index {pdf_page_index}; the catalog has it on "
                    + "; ".join(_page_label(r) for r in rows))
            rows = on_page
        if len(rows) > 1:
            raise KeyError(
                f"the catalog of '{ref}' holds table '{table_number}' "
                f"{len(rows)} times (a number the print uses for more than "
                "one table): " + "; ".join(_page_label(r) for r in rows)
                + ". Say which with pdf_page_index=<its page index>")
        if not rows:
            import difflib
            numbers = [r["table_number"] for r in conn.execute(
                "SELECT table_number FROM tables WHERE reference = ?",
                (ref,)).fetchall()]
            near = difflib.get_close_matches(
                keys[0], [n.upper() for n in numbers], n=5, cutoff=0.5)
            raise KeyError(
                f"table '{table_number}' not found in reference '{ref}'"
                + (f"; nearest table numbers there: {', '.join(near)}"
                   if near else "")
                + " (table_search finds a table by its caption)")
        out = _row_to_full(rows[0])
        if max_chars is None:
            return out
        out, cut = fit_record(out, max_chars - 400,
                              text_fields=("caption", "section_title"))
        if cut:
            out["note"] = (
                "Cut to fit " + f"{max_chars:,} characters: " + ", ".join(
                    f"{k} (from {n:,} characters)" for k, n in cut.items())
                + ". The table itself is on the page given "
                "(pdf_page_index).")
        return out
    finally:
        conn.close()


def list_indexed_tables() -> list[dict[str, Any]]:
    """Inventory of references with an indexed table catalog: per
    reference, ``n_tables``, ``n_chapters`` and how many rows have their
    values typed in a section (``n_text``), coded (``n_lookup``) or only on
    the page (``n_page``)."""
    conn = _ro_connect()
    try:
        rows = conn.execute(
            "SELECT reference, reference_title, COUNT(*) AS n_tables, "
            "COUNT(DISTINCT chapter) AS n_chapters, "
            "SUM(value_source = 'text') AS n_text, "
            "SUM(value_source = 'lookup') AS n_lookup, "
            "SUM(value_source = 'page') AS n_page "
            "FROM tables GROUP BY reference ORDER BY reference"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


#: The folder holding the source PDFs when the package is installed (the
#: figure layer's setting, :data:`._figures_db._DOCS_ENV`).
_DOCS_ENV = "GEOTECH_REFERENCES_DOCS"


def resolve_table_pdf(reference: str, table_number: str,
                      pdf_page_index: int | None = None) -> tuple[Path, int]:
    """Resolve a table to its absolute source PDF path and 0-based page.

    The page is where the table starts, or ``pdf_page_index`` when that is
    one of the table's pages (a sheet of a table that runs on; it also says
    which table for a number held more than once, :func:`table_get`).

    The PDF is found in the ``GEOTECH_REFERENCES_DOCS`` folder when that is
    set (an installed package has no ``docs/``), else relative to the
    repository root, as :func:`._figures_db.resolve_pdf` finds it.

    Raises
    ------
    KeyError
        If the table is unknown (:func:`table_get`).
    FileNotFoundError
        If the source PDF cannot be found on disk.
    """
    rec = table_get(reference, table_number, pdf_page_index=pdf_page_index)
    pdf_rel = rec["pdf_path"]
    docs_override = os.environ.get(_DOCS_ENV)
    if docs_override:
        pdf_abs = (Path(docs_override) / Path(pdf_rel).name).resolve()
    else:
        pdf_abs = (_REPO_ROOT / pdf_rel).resolve()
    if not pdf_abs.exists():
        raise FileNotFoundError(
            f"source PDF for {reference} table {table_number} not found: "
            f"{pdf_abs}. Set {_DOCS_ENV} to the folder containing the "
            "reference PDFs.")
    page = (int(pdf_page_index) if pdf_page_index is not None
            and int(pdf_page_index) in rec["pages"]
            else int(rec["pdf_page_index"]))
    return pdf_abs, page


def rebuild_db() -> dict[str, Any]:
    """Force-rebuild the tables FTS DB and return summary stats."""
    db = _db_path()
    _build_db(db)
    return {"db_path": str(db), "indexed": list_indexed_tables()}
