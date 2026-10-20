"""SQLite FTS5 retrieval layer for structured chapter text.

Builds a single FTS5 index over every `<reference>/text/*.json` file in
the package and exposes three tools optimized for LLM agent use:

- ``reference_search(query, reference=None, chapter=None, limit=5)`` —
  ranked BM25 hits returning *summary only* (the noise-reduction lever).
- ``reference_get(reference, section_id)`` — full section body.
- ``reference_query(sql)`` — read-only SELECT against the backing tables
  (URI mode read-only connection plus a regex SELECT-only check and a
  server-side LIMIT cap).

The database is built lazily into a per-user temp directory at first
call and rebuilt automatically if any source JSON has been touched
since the build. The DB is *not* committed; it is regenerated on
demand.

Coverage caveat (2026-04-08)
----------------------------
Only DM7 (`dm7_1`, `dm7_2`) was extracted with the new schema, so only
DM7 sections have populated ``summary``/``key_points``/``applicability``
fields. Pre-existing GEC narrative (gec_6/7/10/12/13, micropile) is
indexed body-only — search hits against those references will have
empty ``summary`` strings, so the noise-reduction lever does not apply
and agents should drill in via :func:`reference_get` for non-DM7 hits.
``gec_11`` and the FEMA / NOAA / UFC references have no narrative text
at all. See ``scripts/README.md`` "Reference text coverage status".

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
older layout is rebuilt on first use.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

from . import _query_expansion as _qe
from . import _retrieval

_PACKAGE_DIR = Path(__file__).parent
_DB_NAME = "geotech_references_fts.sqlite"

#: Layout of the ``sections`` table, kept in ``PRAGMA user_version``.
#: 2 = every level indexed, with parent_rowid / depth / parents_json (REF-24).
_SCHEMA_VERSION = 2

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

def _db_path() -> Path:
    return Path(tempfile.gettempdir()) / _DB_NAME


def _iter_text_jsons() -> list[tuple[str, Path]]:
    """Yield (reference, json_path) for every text JSON in the package."""
    out: list[tuple[str, Path]] = []
    for ref_dir in sorted(_PACKAGE_DIR.iterdir()):
        if not ref_dir.is_dir():
            continue
        text_dir = ref_dir / "text"
        if not text_dir.is_dir():
            continue
        for jf in sorted(text_dir.glob("*.json")):
            out.append((ref_dir.name, jf))
    return out


def _newest_source_mtime() -> float:
    return max(
        (jf.stat().st_mtime for _, jf in _iter_text_jsons()),
        default=0.0,
    )


#: ``PRAGMA user_version`` per (database path, file mtime), so a search
#: does not open the database twice to learn its layout.
_VERSION_SEEN: dict = {}


def _schema_version(db_path: Path) -> int:
    try:
        key = (str(db_path), db_path.stat().st_mtime_ns)
    except OSError:
        return -1
    if key not in _VERSION_SEEN:
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            try:
                version = int(conn.execute("PRAGMA user_version").fetchone()[0])
            finally:
                conn.close()
        except sqlite3.Error:
            return -1
        _VERSION_SEEN[key] = version
    return _VERSION_SEEN[key]


def _needs_rebuild(db_path: Path) -> bool:
    if not db_path.exists():
        return True
    if db_path.stat().st_mtime < _newest_source_mtime():
        return True
    # a database an older version of this module built (one row per
    # top-level section only) is rebuilt, however new its file is
    return _schema_version(db_path) != _SCHEMA_VERSION


def _build_db(db_path: Path) -> None:
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    try:
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
                parents_json TEXT
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

        for reference, jf in _iter_text_jsons():
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            ref_title = data.get("reference_title", "")
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
                        tables_json, depth, parents_json
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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

        cur.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")
        cur.execute(
            """
            INSERT INTO sections_fts(rowid, title, summary, body,
                                     key_points, applicability)
            SELECT rowid, title, summary, body, key_points, applicability
            FROM sections
            """
        )
        conn.commit()
    finally:
        conn.close()


def _ensure_db() -> Path:
    db = _db_path()
    if _needs_rebuild(db):
        _build_db(db)
    return db


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
        FTS5 MATCH query. Plain words are AND-matched with porter
        stemming. Use FTS5 operators (``"phrase"``, ``OR``, ``NEAR()``,
        ``col:term``) for advanced queries.
    reference : str, optional
        Restrict to a single reference id (e.g. ``"dm7_1"``).
    chapter : int, optional
        Restrict to a single chapter number (only meaningful with
        ``reference``).
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
        some are not shown or more match, ``next_offset`` and a ``note``;
        an error is ``{"error": ...}``.

    Returns
    -------
    list of dict, or dict with ``max_chars``
        Each hit has ``reference``, ``reference_title``, ``chapter``,
        ``chapter_title``, ``section_id``, ``title``, ``parent_id``,
        ``under`` (the sections above it, outermost first, e.g.
        ``"7.2 Strength Limit States > 7.2.1 Nominal Axial ..."``; ``""``
        at the top level) and ``summary``. With ``max_chars``, the dict
        described above.
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
        def run(match_query: str) -> list[sqlite3.Row]:
            sql = (
                "SELECT s.reference, s.reference_title, s.chapter, "
                "s.chapter_title, s.section_id, s.title, s.summary, "
                "s.parents_json "
                "FROM sections_fts f JOIN sections s ON s.rowid = f.rowid "
                "WHERE sections_fts MATCH ?"
            )
            params: list[Any] = [match_query]
            if reference:
                sql += " AND s.reference = ?"
                params.append(reference)
            if chapter is not None:
                sql += " AND s.chapter = ?"
                params.append(int(chapter))
            sql += " ORDER BY bm25(sections_fts) LIMIT ?"
            params.append(want)
            return conn.execute(sql, params).fetchall()

        strategy = _qe.EXPANSION_STRATEGY

        def search(q: str, relaxed: bool = False) -> list[sqlite3.Row]:
            if strategy == "rerank":
                # "shotgun": one combined query, BM25 ranks literal+synonym union.
                rows = run(_qe.combined_query(q))
            elif strategy == "auto":
                # Rerank the literal+synonym union (recall), but PIN the literal
                # top-N (EXPANSION_PIN, default 1) so an already-good query keeps its best hit (precision).
                literal = run(q)
                combined = _qe.combined_query(q)
                if combined == q:
                    rows = literal            # no synonyms to add
                elif not literal:
                    # nothing to pin: the query with its terms swapped for
                    # their synonyms, then its words OR-ed with the synonyms
                    rows = _qe.zero_literal_hits(q, run, want, key=lambda r: (r["reference"], r["section_id"]))
                else:
                    rows = _qe.merge_hits(
                        literal[:_qe.EXPANSION_PIN], run(combined), want,
                        key=lambda r: (r["reference"], r["section_id"]),
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
                            rows, run(expansion), want,
                            key=lambda r: (r["reference"], r["section_id"]),
                        )
            # Zero-hit recall fallback (mirrors figure_search): if the
            # AND-matched query (and any expansion) found nothing, retry as
            # OR-of-terms. Fires only when there would otherwise be no
            # results, so existing rankings are never disturbed. NOT applied
            # in 'off' — that strategy is the pure-literal anchor used by the
            # recall eval and the precision invariants.
            if not rows and strategy != "off":
                fb = _qe.or_fallback(q)
                if not fb and relaxed:
                    # a query re-quoted by fts_safe_query: its words, OR-ed
                    fb = _qe.or_fallback(plain_terms(q))
                if fb and fb != q:
                    rows = run(fb)
            return rows

        try:
            rows = search_fts_safely(
                search, query, retry=lambda q: search(q, relaxed=True))
        except sqlite3.OperationalError as e:
            if max_chars is not None:
                return {"error": f"FTS query error: {e}"}
            return [{"error": f"FTS query error: {e}"}]
        more = len(rows) > offset + limit
        hits = [_row_to_summary(r) for r in rows[offset:offset + limit]]
        if max_chars is None:
            return hits
        return _retrieval.fit_hits(
            hits, max_chars, text_fields=("summary",), offset=offset,
            more=more, max_offset=_MAX_OFFSET,
            narrow=("narrow the query (more specific words, a 'reference' "
                    "or a 'chapter')"),
            fetch="reference_get returns a section's whole text")
    finally:
        conn.close()


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
        Reference id (e.g. ``"dm7_1"``).
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
        above that number and any sections numbered under it.
    """
    conn = _ro_connect()
    try:
        row = conn.execute(
            "SELECT * FROM sections WHERE reference = ? "
            "AND section_id = ? ORDER BY rowid LIMIT 1",
            (reference, section_id),
        ).fetchone()
        if row is None:
            raise KeyError(
                f"section_id '{section_id}' not found in reference "
                f"'{reference}'" + _nearby(conn, reference, section_id)
            )
        out = _row_to_full(row)
        out["children"] = [
            {"section_id": c["section_id"], "title": c["title"]}
            for c in _child_rows(conn, row["rowid"])]
        if include_subsections:
            out = _retrieval.inline_subsections(
                out, _subtree(conn, row["rowid"], {row["rowid"]}))
        return out
    finally:
        conn.close()


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
    return _retrieval.nearby_note(
        above, [(r["section_id"], r["title"]) for r in below])


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

    Useful for agents to discover what's available before searching.
    """
    conn = _ro_connect()
    try:
        rows = conn.execute(
            "SELECT reference, reference_title, "
            "COUNT(DISTINCT chapter) AS n_chapters, "
            "COUNT(*) AS n_sections "
            "FROM sections GROUP BY reference, reference_title "
            "ORDER BY reference"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def rebuild_db() -> dict[str, Any]:
    """Force-rebuild the FTS DB and return summary stats."""
    db = _db_path()
    _build_db(db)
    return {"db_path": str(db), "indexed": list_indexed_references()}
