"""SQLite FTS5 retrieval layer for the figure catalog.

Companion to :mod:`geotech_references._retrieval_db` (which indexes chapter
*text*). This module indexes every ``<reference>/figures_catalog.json`` produced
by ``scripts/build_figure_catalog.py`` and exposes tools for finding a figure by
meaning and resolving it to a renderable PDF page:

- ``figure_search(query, reference=None, chapter=None, limit=5)`` — ranked BM25
  hits over figure captions (and any cached descriptions).
- ``figure_get(reference, figure_number)`` — full catalog row for one figure,
  including ``pdf_path`` + ``pdf_page_index`` for vision read-off.
- ``list_indexed_figures()`` — inventory of indexed references.

The DB is built lazily into a per-user temp directory on first call and rebuilt
automatically when any catalog JSON changes. It is *not* committed.

The retrieved page is a chart the caller can render and read off with a vision
model (see ``read_reference_figure`` in ``funhouse_agent``). The figure page
index is a best estimate resolved from the source PDF; if a chart is not on the
returned page, try +/-1.
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

# FTS5 operator words we must not inject as bare terms in the OR fallback.

_PACKAGE_DIR = Path(__file__).parent
_REPO_ROOT = _PACKAGE_DIR.parent
_DB_NAME = "geotech_references_figures_fts.sqlite"
_CATALOG_NAME = "figures_catalog.json"
_MAX_LIMIT = 50
_DEFAULT_SEARCH_LIMIT = 5


# ---------------------------------------------------------------------------
# DB build
# ---------------------------------------------------------------------------

def _db_path() -> Path:
    return Path(tempfile.gettempdir()) / _DB_NAME


def _iter_catalogs() -> list[Path]:
    """Yield every ``<reference>/figures_catalog.json`` in the package."""
    out: list[Path] = []
    for ref_dir in sorted(_PACKAGE_DIR.iterdir()):
        if not ref_dir.is_dir():
            continue
        cat = ref_dir / _CATALOG_NAME
        if cat.is_file():
            out.append(cat)
    return out


def _newest_source_mtime() -> float:
    return max((c.stat().st_mtime for c in _iter_catalogs()), default=0.0)


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
            CREATE TABLE figures (
                rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT NOT NULL,
                reference_id TEXT,
                reference_title TEXT,
                volume INTEGER,
                figure_number TEXT,
                caption TEXT,
                description TEXT,
                chapter INTEGER,
                pdf_path TEXT,
                pdf_page_index INTEGER,
                printed_page INTEGER,
                page_estimated INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE VIRTUAL TABLE figures_fts USING fts5(
                figure_number, caption, description,
                content='figures',
                content_rowid='rowid',
                tokenize='porter unicode61'
            )
            """
        )
        cur.execute("CREATE INDEX idx_fig_ref ON figures(reference)")
        cur.execute("CREATE INDEX idx_fig_ref_chap ON figures(reference, chapter)")
        cur.execute("CREATE INDEX idx_fig_ref_num ON figures(reference, figure_number)")

        for cat_path in _iter_catalogs():
            try:
                data = json.loads(cat_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            reference = data.get("package", cat_path.parent.name)
            ref_id = data.get("reference_id", "")
            ref_title = data.get("reference_title", "")
            volume = data.get("volume")
            pdf_path = data.get("pdf_path", "")
            for fig in data.get("figures", []):
                if not isinstance(fig, dict):
                    continue
                cur.execute(
                    """
                    INSERT INTO figures (
                        reference, reference_id, reference_title, volume,
                        figure_number, caption, description, chapter,
                        pdf_path, pdf_page_index, printed_page, page_estimated
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        reference, ref_id, ref_title, volume,
                        fig.get("figure_number", ""),
                        fig.get("caption", ""),
                        fig.get("description", "") or "",
                        fig.get("chapter"),
                        fig.get("pdf_path") or pdf_path,  # per-figure (multi-volume) wins
                        fig.get("pdf_page_index"),
                        fig.get("printed_page"),
                        1 if fig.get("page_estimated") else 0,
                    ),
                )

        cur.execute(
            """
            INSERT INTO figures_fts(rowid, figure_number, caption, description)
            SELECT rowid, figure_number, caption, description FROM figures
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

def _norm_fig_number(s: str) -> str:
    """Normalize a figure id for lookup ('Figure 4-12', ' 4-12 ' -> '4-12')."""
    s = (s or "").strip()
    if s.lower().startswith("figure"):
        s = s[len("figure"):].strip()
    return s.upper()


# OR-of-terms recall fallback shared with reference_search.
_or_fallback = _qe.or_fallback


def _row_to_hit(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "reference": row["reference"],
        "reference_title": row["reference_title"],
        "figure_number": row["figure_number"],
        "caption": row["caption"],
        "chapter": row["chapter"],
        "pdf_page_index": row["pdf_page_index"],
        "printed_page": row["printed_page"],
    }


def _row_to_full(row: sqlite3.Row) -> dict[str, Any]:
    out = _row_to_hit(row)
    out.update({
        "reference_id": row["reference_id"],
        "volume": row["volume"],
        "description": row["description"],
        "pdf_path": row["pdf_path"],
        "page_estimated": bool(row["page_estimated"]),
    })
    return out


def figure_search(
    query: str,
    reference: str | None = None,
    chapter: int | None = None,
    limit: int = _DEFAULT_SEARCH_LIMIT,
) -> list[dict[str, Any]]:
    """Full-text search the figure catalog by caption/description.

    Parameters
    ----------
    query : str
        FTS5 MATCH query. Plain words are AND-matched with porter stemming;
        FTS5 operators (``"phrase"``, ``OR``, ``NEAR()``, ``col:term``) work.
    reference : str, optional
        Restrict to one reference id (e.g. ``"dm7_2"``).
    chapter : int, optional
        Restrict to one chapter number (prologue figures are chapter 0;
        appendix figures have no chapter).
    limit : int, optional
        Max hits (capped at 50).

    Returns
    -------
    list of dict
        Ranked hits, each with ``reference``, ``reference_title``,
        ``figure_number``, ``caption``, ``chapter``, ``pdf_page_index``,
        ``printed_page``. Call :func:`figure_get` for the full row, or render
        the page for vision read-off.
    """
    if not query or not query.strip():
        return []
    limit = max(1, min(int(limit), _MAX_LIMIT))
    conn = _ro_connect()
    try:
        def run(match_query: str) -> list[sqlite3.Row]:
            sql = (
                "SELECT f.reference, f.reference_title, f.figure_number, "
                "f.caption, f.chapter, f.pdf_page_index, f.printed_page "
                "FROM figures_fts x JOIN figures f ON f.rowid = x.rowid "
                "WHERE figures_fts MATCH ?"
            )
            params: list[Any] = [match_query]
            if reference:
                sql += " AND f.reference = ?"
                params.append(reference)
            if chapter is not None:
                sql += " AND f.chapter = ?"
                params.append(int(chapter))
            sql += " ORDER BY bm25(figures_fts) LIMIT ?"
            params.append(limit)
            return conn.execute(sql, params).fetchall()

        fig_key = lambda r: (r["reference"], r["figure_number"])
        strategy = _qe.EXPANSION_STRATEGY
        try:
            if strategy == "rerank":
                # "shotgun": BM25 ranks the literal+synonym union in one query.
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
                    rows = _qe.merge_hits([literal[0]], run(combined), limit,
                                          key=fig_key)
            else:
                rows = run(query)
                # "fill" (targeted): append synonym hits to remaining slots when
                # the literal AND-query under-returns on a terminology mismatch.
                if strategy == "fill" and len(rows) < limit:
                    expansion = _qe.expand_query(query)
                    if expansion:
                        rows = _qe.merge_hits(rows, run(expansion), limit,
                                              key=fig_key)
            # Broad OR-of-terms ALSO fills remaining slots (all strategies); it
            # is complementary to synonym expansion and must not be suppressed.
            if len(rows) < limit:
                fb = _or_fallback(query)
                if fb and fb != query:
                    rows = _qe.merge_hits(rows, run(fb), limit, key=fig_key)
        except sqlite3.OperationalError as e:
            return [{"error": f"FTS query error: {e}"}]
        return [_row_to_hit(r) for r in rows]
    finally:
        conn.close()


def figure_get(reference: str, figure_number: str) -> dict[str, Any]:
    """Fetch the full catalog row for one figure.

    Parameters
    ----------
    reference : str
        Reference id (e.g. ``"dm7_2"``).
    figure_number : str
        Figure id as in the source (e.g. ``"4-12"``, ``"P-1"``, ``"B-3"``).
        A leading ``"Figure "`` is tolerated.

    Returns
    -------
    dict
        Full row incl. ``caption``, ``description``, ``chapter``, ``pdf_path``,
        ``pdf_page_index`` (0-based), ``printed_page``, ``page_estimated``.

    Raises
    ------
    KeyError
        If no such figure exists.
    """
    num = _norm_fig_number(figure_number)
    conn = _ro_connect()
    try:
        row = conn.execute(
            "SELECT * FROM figures WHERE reference = ? "
            "AND UPPER(figure_number) = ? LIMIT 1",
            (reference, num),
        ).fetchone()
        if row is None:
            raise KeyError(
                f"figure '{figure_number}' not found in reference '{reference}'"
            )
        return _row_to_full(row)
    finally:
        conn.close()


def list_indexed_figures() -> list[dict[str, Any]]:
    """Inventory of references with an indexed figure catalog."""
    conn = _ro_connect()
    try:
        rows = conn.execute(
            "SELECT reference, reference_title, COUNT(*) AS n_figures, "
            "COUNT(DISTINCT chapter) AS n_chapters "
            "FROM figures GROUP BY reference, reference_title ORDER BY reference"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# Env var pointing at the folder holding the source reference PDFs. Set this when
# the package is pip-installed (e.g. Databricks): the PDFs are too large/
# license-sensitive to ship in the wheel, so copy them into a docs folder and set
# GEOTECH_REFERENCES_DOCS to it. Falls back to the repo-relative location for
# source checkouts.
_DOCS_ENV = "GEOTECH_REFERENCES_DOCS"


def resolve_pdf(reference: str, figure_number: str) -> tuple[Path, int]:
    """Resolve a figure to its absolute source PDF path and 0-based page index.

    The PDF is located via the ``GEOTECH_REFERENCES_DOCS`` folder when that env
    var is set (needed when the package is installed and the repo's ``docs/`` is
    absent), otherwise relative to the repo root.

    Raises
    ------
    KeyError
        If the figure is unknown.
    FileNotFoundError
        If the source PDF cannot be found on disk.
    """
    rec = figure_get(reference, figure_number)
    pdf_rel = rec["pdf_path"]
    docs_override = os.environ.get(_DOCS_ENV)
    if docs_override:
        # PDFs live flat in the docs folder; resolve by filename.
        pdf_abs = (Path(docs_override) / Path(pdf_rel).name).resolve()
    else:
        pdf_abs = (_REPO_ROOT / pdf_rel).resolve()
    if not pdf_abs.exists():
        raise FileNotFoundError(
            f"source PDF for {reference} {figure_number} not found: {pdf_abs}. "
            f"Set {_DOCS_ENV} to the folder containing the reference PDFs."
        )
    return pdf_abs, int(rec["pdf_page_index"])


def rebuild_db() -> dict[str, Any]:
    """Force-rebuild the figure FTS DB and return summary stats."""
    db = _db_path()
    _build_db(db)
    return {"db_path": str(db), "indexed": list_indexed_figures()}
