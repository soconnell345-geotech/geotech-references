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

_PACKAGE_DIR = Path(__file__).parent
_DB_NAME = "geotech_references_fts.sqlite"

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


def _needs_rebuild(db_path: Path) -> bool:
    if not db_path.exists():
        return True
    return db_path.stat().st_mtime < _newest_source_mtime()


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
                tables_json TEXT
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

        for reference, jf in _iter_text_jsons():
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            ref_title = data.get("reference_title", "")
            ch_num = data.get("chapter", 0)
            ch_title = data.get("chapter_title", "")
            for sec in data.get("sections", []):
                if not isinstance(sec, dict):
                    continue
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
                        tables_json
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
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
                    ),
                )

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
    return {
        "reference": row["reference"],
        "reference_title": row["reference_title"],
        "chapter": row["chapter"],
        "chapter_title": row["chapter_title"],
        "section_id": row["section_id"],
        "title": row["title"],
        "summary": row["summary"],
    }


def _row_to_full(row: sqlite3.Row) -> dict[str, Any]:
    out = _row_to_summary(row)
    out["body"] = row["body"]
    out["key_points"] = [
        kp for kp in (row["key_points"] or "").split("\n") if kp
    ]
    out["applicability"] = row["applicability"]
    out["equations"] = json.loads(row["equations_json"] or "[]")
    out["figures"] = json.loads(row["figures_json"] or "[]")
    out["tables"] = json.loads(row["tables_json"] or "[]")
    return out


def reference_search(
    query: str,
    reference: str | None = None,
    chapter: int | None = None,
    limit: int = _DEFAULT_SEARCH_LIMIT,
) -> list[dict[str, Any]]:
    """Full-text search across structured chapter text.

    Returns ranked summary-only hits (no `body`) — call
    :func:`reference_get` to fetch the full section.

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

    Returns
    -------
    list of dict
        Each hit has ``reference``, ``reference_title``, ``chapter``,
        ``chapter_title``, ``section_id``, ``title``, and ``summary``.
    """
    if not query or not query.strip():
        return []
    limit = max(1, min(int(limit), _MAX_LIMIT))
    conn = _ro_connect()
    try:
        def run(match_query: str) -> list[sqlite3.Row]:
            sql = (
                "SELECT s.reference, s.reference_title, s.chapter, "
                "s.chapter_title, s.section_id, s.title, s.summary "
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
            params.append(limit)
            return conn.execute(sql, params).fetchall()

        strategy = _qe.EXPANSION_STRATEGY
        try:
            if strategy == "rerank":
                # "shotgun": one combined query, BM25 ranks literal+synonym union.
                rows = run(_qe.combined_query(query))
            elif strategy == "auto":
                # Rerank the literal+synonym union (recall), but PIN the literal
                # top-1 so an already-good query keeps its best hit (precision).
                literal = run(query)
                combined = _qe.combined_query(query)
                if combined == query:
                    rows = literal            # no synonyms to add
                elif not literal:
                    rows = run(combined)      # nothing to pin; rerank the union
                else:
                    rows = _qe.merge_hits(
                        [literal[0]], run(combined), limit,
                        key=lambda r: (r["reference"], r["section_id"]),
                    )
            else:
                rows = run(query)
                # "fill": the literal query is AND-matched, so it under-returns
                # exactly when the query's terminology differs from the source
                # text (a synonym miss). Append synonym hits to fill remaining
                # slots; literal BM25 hits keep their rank (precision preserved).
                if strategy == "fill" and len(rows) < limit:
                    expansion = _qe.expand_query(query)
                    if expansion:
                        rows = _qe.merge_hits(
                            rows, run(expansion), limit,
                            key=lambda r: (r["reference"], r["section_id"]),
                        )
        except sqlite3.OperationalError as e:
            return [{"error": f"FTS query error: {e}"}]
        return [_row_to_summary(r) for r in rows]
    finally:
        conn.close()


def reference_get(reference: str, section_id: str) -> dict[str, Any]:
    """Fetch the full section by id, including body, key_points, equations.

    Parameters
    ----------
    reference : str
        Reference id (e.g. ``"dm7_1"``).
    section_id : str
        Section id as it appears in the source (e.g. ``"4-2.1"``,
        ``"5.3"``, ``"P-1"``).

    Returns
    -------
    dict
        Full section dict.

    Raises
    ------
    KeyError
        If no such section exists.
    """
    conn = _ro_connect()
    try:
        row = conn.execute(
            "SELECT * FROM sections WHERE reference = ? AND section_id = ? "
            "LIMIT 1",
            (reference, section_id),
        ).fetchone()
        if row is None:
            raise KeyError(
                f"section_id '{section_id}' not found in reference "
                f"'{reference}'"
            )
        return _row_to_full(row)
    finally:
        conn.close()


def reference_query(sql: str, limit: int = _MAX_LIMIT) -> list[dict[str, Any]]:
    """Run a read-only SELECT against the retrieval DB.

    Tables available:

    - ``sections`` — one row per section. Columns: ``reference``,
      ``reference_title``, ``chapter``, ``chapter_title``, ``section_id``,
      ``title``, ``summary``, ``body``, ``key_points``, ``applicability``,
      ``equations_json``, ``figures_json``, ``tables_json``.
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

    Returns
    -------
    list of dict
        Result rows as dicts. On a query error, returns a single-element
        list ``[{"error": "..."}]``.
    """
    if not sql or not sql.strip():
        return [{"error": "empty query"}]
    if not _SELECT_ONLY_RE.match(sql):
        return [{"error": "only SELECT (or WITH ... SELECT) statements allowed"}]
    if _FORBIDDEN_RE.search(sql):
        return [{"error": "query contains forbidden keyword"}]
    if ";" in sql.rstrip(";\n\r\t "):
        return [{"error": "multiple statements not allowed"}]
    limit = max(1, min(int(limit), _MAX_LIMIT))
    conn = _ro_connect()
    try:
        try:
            cur = conn.execute(sql)
        except sqlite3.OperationalError as e:
            return [{"error": f"SQL error: {e}"}]
        rows = cur.fetchmany(limit)
        return [dict(r) for r in rows]
    finally:
        conn.close()


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
