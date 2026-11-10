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
automatically when any catalog JSON changes. Its file name is keyed to this copy
of the package, as the text DB's is. It is *not* committed.

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
from pathlib import Path
from typing import Any

from . import _atomic_db
from . import _packs
from . import _query_expansion as _qe
from ._retrieval import fit_hits, fit_record
from ._retrieval_db import (TRIED_ALL, absent_words_note, db_meta,
                            keyed_db_path, match_marks, match_summary,
                            plain_terms, query_words, search_fts_safely,
                            source_state, unreadable_source,
                            with_match_summary, write_build_meta)

# FTS5 operator words we must not inject as bare terms in the OR fallback.

_PACKAGE_DIR = Path(__file__).parent
_REPO_ROOT = _PACKAGE_DIR.parent
_DB_NAME = "geotech_references_figures_fts.sqlite"
_CATALOG_NAME = "figures_catalog.json"
_MAX_LIMIT = 50
_DEFAULT_SEARCH_LIMIT = 5
_MAX_OFFSET = 500  # deepest page figure_search reaches


# ---------------------------------------------------------------------------
# DB build
# ---------------------------------------------------------------------------

def _db_path() -> Path:
    return keyed_db_path(_DB_NAME, _PACKAGE_DIR)


def _iter_catalogs() -> list[Path]:
    """Yield every ``<reference>/figures_catalog.json`` in the package, then
    every local reference pack's (REF-64; none when unset)."""
    out: list[Path] = []
    for ref_dir in sorted(_PACKAGE_DIR.iterdir()):
        if not ref_dir.is_dir():
            continue
        cat = ref_dir / _CATALOG_NAME
        if cat.is_file():
            out.append(cat)
    out.extend(cat for _, cat in _packs.catalogs())
    return out


#: Layout of the figures database, kept in ``PRAGMA user_version``.
#: 1 = a ``build_meta`` table holding the signature of the catalogs it was
#: built from (2026-11-10 review, core-11); 0 = a database built before.
_SCHEMA_VERSION = 1


def _newest_source_mtime() -> float:
    return source_state(_iter_catalogs())[0]


def _needs_rebuild(db_path: Path) -> bool:
    """Whether the figures database at ``db_path`` must be built (again):
    it is not there, a catalog is newer than it, it was built before
    databases kept their sources' signature, or the catalogs are not the
    ones it was built from -- one deleted, added, or restored with an
    older date, which the date rule alone missed (core-11)."""
    if not db_path.exists():
        return True
    newest, signature = source_state(_iter_catalogs())
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
            page_estimated INTEGER,
            bbox TEXT,
            read_notes TEXT
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

    # a local pack's figures are filed under its pack id (REF-64)
    pack_of = {cat: pid for pid, cat in _packs.catalogs()}
    sources = _iter_catalogs()
    write_build_meta(cur, source_state(sources)[1], _SCHEMA_VERSION)
    for cat_path in sources:
        try:
            data = json.loads(cat_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            if cat_path in pack_of:
                continue  # named in _packs.problems()
            raise unreadable_source(cat_path, e) from e
        if cat_path not in pack_of:
            _index_catalog(cur, data.get("package", cat_path.parent.name),
                           data)
        # a local pack's catalog the index cannot take (a PDF named by a
        # path, a field of the wrong kind) is skipped and named in
        # _packs.problems(); one that still fails is rolled back (REF-64)
        elif _packs.catalog_problem(data) is None:
            _packs.index_pack_file(
                cur, cat_path,
                lambda: _index_catalog(cur, pack_of[cat_path], data))

    cur.execute(
        """
        INSERT INTO figures_fts(rowid, figure_number, caption, description)
        SELECT rowid, figure_number, caption, description FROM figures
        """
    )


def _index_catalog(cur: sqlite3.Cursor, reference: str, data: dict) -> None:
    """Insert one figure catalog's figures into ``figures``."""
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
                pdf_path, pdf_page_index, printed_page, page_estimated,
                bbox, read_notes
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                # A volume printed under its own number (GEC-13 Vol II,
                # FHWA-NHI-16-028) carries it per figure; it wins (REF-31).
                reference, fig.get("reference_id") or ref_id, ref_title,
                fig.get("volume", volume),
                fig.get("figure_number", ""),
                fig.get("caption", ""),
                fig.get("description", "") or "",
                fig.get("chapter"),
                fig.get("pdf_path") or pdf_path,  # per-figure (multi-volume) wins
                fig.get("pdf_page_index"),
                fig.get("printed_page"),
                1 if fig.get("page_estimated") else 0,
                # two optional fields a catalog may give any figure
                # (REF-64): a crop for the vision read and notes on
                # reading it; carried to figure_get as given
                (json.dumps(fig["bbox"]) if fig.get("bbox") is not None
                 else None),
                fig.get("read_notes") or None,
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
# Public API
# ---------------------------------------------------------------------------

def _norm_fig_number(s: str) -> str:
    """Normalize a figure id for lookup ('Figure 4-12', 'Fig. 4-12',
    ' 4-12 ' -> '4-12')."""
    s = (str(s or "")).strip()
    low = s.lower()
    for prefix in ("figure", "fig."):
        if low.startswith(prefix):
            s = s[len(prefix):].strip()
            break
    else:
        if low.startswith("fig "):
            s = s[3:].strip()
    return s.strip(" .:").upper()


def _fig_number_keys(s: str) -> tuple:
    """The normalized forms a figure id is looked up by: itself and, for a
    part letter printed in brackets, the plain letter the catalogs file
    ('Figure 9-37(a)' -> ('9-37(A)', '9-37A'); 2026-11-10 review: the
    printed form was not found)."""
    num = _norm_fig_number(s)
    plain = re.sub(r"\s*\(([A-Z])\)$", r"\1", num)
    return (num, plain) if plain != num else (num,)


def _number_clause(keys: tuple) -> str:
    return "UPPER(figure_number) IN (" + ", ".join("?" * len(keys)) + ")"


def _id_key(text: str) -> str:
    """A reference id or title reduced to lower-case letters and digits
    ('gec_10', 'GEC-10', 'gec10' -> 'gec10'; 'UFC 3-250-01' -> 'ufc325001')."""
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


def _catalog_refs(conn: sqlite3.Connection) -> list[tuple[str, str, tuple]]:
    """``(reference, reference_title, report numbers)`` of every catalog,
    each catalog once. A manual whose volumes are printed under their own
    report numbers (GEC-13: FHWA-NHI-16-027 and -028) has several numbers;
    it used to be listed once per number, so its own name ("GEC-13") was
    refused as "in more than one catalog -- gec_13; gec_13"."""
    rows = conn.execute(
        "SELECT DISTINCT reference, reference_title, reference_id "
        "FROM figures ORDER BY rowid"
    ).fetchall()
    titles: dict[str, str] = {}
    numbers: dict[str, list[str]] = {}
    for r in rows:
        titles.setdefault(r["reference"], r["reference_title"] or "")
        held = numbers.setdefault(r["reference"], [])
        if r["reference_id"] and r["reference_id"] not in held:
            held.append(r["reference_id"])
    return [(ref, titles[ref], tuple(numbers[ref])) for ref in titles]


#: A name callers use for a manual that is two catalogs here: the app's
#: module ``dm7`` covers UFS 3-220-10 (``dm7_1``) and UFC 3-220-20
#: (``dm7_2``). The figure asked for says which (resolve_reference).
_SHARED_NAMES = {"dm7": ("dm7_1", "dm7_2")}


def _is_report_number(key: str, doc_key: str) -> bool:
    """Whether ``key`` is the report number ``doc_key`` (both reduced by
    :func:`_id_key`): the whole of it ('fhwanhi16009', 'ufc325001') or the
    number without its agency ('nhi16009', '325001')."""
    if not doc_key:
        return False
    return key == doc_key or (
        len(key) >= 5 and any(c.isdigit() for c in key)
        and doc_key.endswith(key))


def _reference_candidates(conn: sqlite3.Connection,
                          reference: str) -> list[str]:
    """The catalog ids a caller's ``reference`` can mean.

    The catalog id itself; the same id spelled another way (``gec10``,
    ``GEC-10`` for ``gec_10``); the app's module name for a manual in two
    catalogs (``dm7`` -> ``dm7_1``, ``dm7_2``); or the document's own
    report number, with or without its agency (``UFC 3-250-01`` ->
    ``ufc_pavement``; ``NHI-16-028`` -> ``gec_13``). GeotechStaffEngineer
    live smoke wave 1, G4: 9 figure reads failed on exactly these
    spellings.

    Nothing looser: until the 2026-11-10 review (core-09) a name also
    matched any catalog id it began ("FHWA" -> two catalogs, "gec_1" ->
    GEC-10 to GEC-14) and any title or report number that contained it
    ("pile"), and the catalog that happened to hold the figure number
    answered. Such a name now resolves to nothing, and the caller is given
    the ids to choose from.
    """
    refs = _catalog_refs(conn)
    ids = [r[0] for r in refs]
    if reference in ids:
        return [reference]
    key = _id_key(reference)
    if not key:
        return []
    exact = [r for r in ids if _id_key(r) == key]
    if exact:
        return exact
    shared = [r for r in _SHARED_NAMES.get(key, ()) if r in ids]
    if shared:
        return shared
    return [r for r, _, numbers in refs
            if any(_is_report_number(key, _id_key(n)) for n in numbers)]


def _unknown_reference(conn: sqlite3.Connection, reference: str) -> str:
    """What a lookup says for a ``reference`` that names no figure catalog."""
    valid = sorted(r[0] for r in _catalog_refs(conn))
    skipped = _packs.problems_by_pack().get(reference)
    why = (" The reference packs setting names it, but the index skipped "
           "it: " + "; ".join(skipped) + "." if skipped else "")
    return (f"no figure catalog '{reference}'.{why} Use a catalog id: "
            f"{', '.join(valid)} (or figure_search with no reference to "
            "find the figure)")


def resolve_reference(reference: str, figure_number: str | None = None) -> str:
    """The catalog id ``reference`` means (see :func:`_reference_candidates`);
    when it could mean several catalogs, the one holding ``figure_number``.

    Raises ``KeyError`` naming the valid ids, or the candidates when the
    figure is in more than one of them."""
    conn = _ro_connect()
    try:
        cands = _reference_candidates(conn, reference)
        if len(cands) == 1:
            return cands[0]
        if not cands:
            raise KeyError(_unknown_reference(conn, reference))
        if figure_number:
            keys = _fig_number_keys(figure_number)
            holding = [c for c in cands if conn.execute(
                "SELECT 1 FROM figures WHERE reference = ? AND "
                + _number_clause(keys) + " LIMIT 1", (c, *keys)).fetchone()]
            if len(holding) == 1:
                return holding[0]
            if holding:
                shown = []
                for c in holding:
                    row = conn.execute(
                        "SELECT caption, reference_title FROM figures WHERE "
                        "reference = ? AND " + _number_clause(keys)
                        + " LIMIT 1", (c, *keys)).fetchone()
                    shown.append(f"{c} ({str(row['reference_title'])[:40]}: "
                                 f"{str(row['caption'])[:70]})")
                raise KeyError(
                    f"'{reference}' figure {figure_number} exists in more "
                    f"than one catalog -- {'; '.join(shown)}. Give the id of "
                    "the one you mean")
        raise KeyError(
            f"'{reference}' could mean {', '.join(cands)}: give one of those "
            "ids")
    finally:
        conn.close()


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
    # Only a figure whose catalog gives them carries these (REF-64); a
    # database built before they existed has no such columns.
    keys = row.keys()
    if "bbox" in keys and row["bbox"] is not None:
        out["bbox"] = json.loads(row["bbox"])
    if "read_notes" in keys and row["read_notes"]:
        out["read_notes"] = row["read_notes"]
    return out


def figure_search(
    query: str,
    reference: str | None = None,
    chapter: int | None = None,
    limit: int = _DEFAULT_SEARCH_LIMIT,
    offset: int = 0,
    max_chars: int | None = None,
):
    """Full-text search the figure catalog by caption/description.

    Parameters
    ----------
    query : str
        FTS5 MATCH query, words matched with porter stemming. The figures
        whose caption or description holds every word come first; unless
        the expansion strategy is ``"off"``, figures holding a synonym of a
        named term are added; and the places left are filled by figures
        holding any one of the words. A hit that does not hold every word
        says so in ``match`` (below). FTS5 operators (``"phrase"``,
        ``OR``, ``NEAR()``, ``col:term``) work.
    reference : str, optional
        Restrict to one reference id (e.g. ``"dm7_2"``); another spelling
        of it, the app's module name ``dm7`` or the document's report
        number resolve as in :func:`figure_get`. A name that means no
        catalog is an error naming the catalog ids, not an empty result.
    chapter : int or str, optional
        Restrict to one chapter as the catalog files it (prologue figures
        are chapter 0; the AASHTO 1993 Guide's are ``"II-2"``; appendix
        figures have no chapter). A chapter with no figures in the scope
        is an error naming the chapters that have some.
    limit : int, optional
        Max hits (capped at 50).
    offset : int, optional
        Skip this many of the best hits first (the next page). Past 500
        the result is an error saying to narrow the query; a page whose
        next hits would start past it says so instead of offering
        ``next_offset``.
    max_chars : int, optional
        The largest result the caller can take, in JSON characters (a few
        catalog captions run on into the page text, one to 29,911
        characters). With it the result is a dict of the hits that fit
        (:func:`_retrieval.fit_hits`: captions cut to 300 characters
        first, then the lowest-ranked hits left out) with, when some are
        not shown or more were found, ``next_offset`` and a ``note``. When
        some hits do not hold every word it adds ``matched``,
        ``words_not_found`` and a sentence on the note, and an empty
        result names the scope and the words no figure there holds, as
        :func:`_retrieval_db.reference_search` does. An error is
        ``{"error": ...}``.

    Returns
    -------
    list of dict, or dict with ``max_chars``
        Ranked hits, each with ``reference``, ``reference_title``,
        ``figure_number``, ``caption``, ``chapter``, ``pdf_page_index``,
        ``printed_page``; a hit that does not hold every word of the query
        also has ``match`` (``"synonyms"``, or ``"any word"`` with
        ``lacks``, the words it does not hold), worked out after the
        ranking (2026-11-10 review, core-05). Call :func:`figure_get` for
        the full row, or render
        the page for vision read-off. With ``max_chars``, the dict
        described above, plus ``resolved_reference`` (the catalog id or
        ids searched) when ``reference`` was not itself a catalog id. An
        unknown ``reference`` or ``chapter`` is ``[{"error": ...}]``
        (``{"error": ...}`` with ``max_chars``).
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
        return {"error": message} if max_chars is not None             else [{"error": message}]
    # rows wanted: the page, after the offset, and one more to learn
    # whether more match (a plain call asks for exactly the page, as before)
    want = limit if not (offset or max_chars is not None) \
        else offset + limit + 1
    conn = _ro_connect()
    try:
        def refuse(message: str):
            return ({"error": message} if max_chars is not None
                    else [{"error": message}])

        # 'gec10', 'dm7', 'UFC 3-250-01' filter the catalogs they mean (G4).
        # A name that means no catalog, or a chapter with no figures, is an
        # error naming the choices: it used to be an empty list, the same
        # answer as "no figure shows this" (2026-11-10 review, core-06).
        refs = _reference_candidates(conn, reference) if reference else []
        if reference and not refs:
            return refuse(_unknown_reference(conn, reference))
        chapters: list = []
        if chapter is not None:
            in_refs = (" WHERE reference IN ("
                       + ", ".join("?" for _ in refs) + ")") if refs else ""
            have = [r[0] for r in conn.execute(
                "SELECT DISTINCT chapter FROM figures" + in_refs, refs)
                if r[0] is not None]
            chapters = [c for c in have if str(c) == str(chapter).strip()]
            if not chapters:
                have.sort(key=lambda c: (isinstance(c, str), c))
                where = (", ".join(refs) if refs else "any catalog")
                return refuse(
                    f"no figures filed under chapter {chapter!r} in {where}; "
                    "chapters with figures there: "
                    + ", ".join(str(c) for c in have[:40])
                    + " (appendix figures may have no chapter: search "
                    "without one)")

        def run(match_query: str) -> list[sqlite3.Row]:
            sql = (
                "SELECT f.rowid AS rid, f.reference, f.reference_title, "
                "f.figure_number, "
                "f.caption, f.chapter, f.pdf_page_index, f.printed_page "
                "FROM figures_fts x JOIN figures f ON f.rowid = x.rowid "
                "WHERE figures_fts MATCH ?"
            )
            params: list[Any] = [match_query]
            if refs:
                sql += (" AND f.reference IN ("
                        + ", ".join("?" for _ in refs) + ")")
                params.extend(refs)
            if chapters:
                sql += (" AND f.chapter IN ("
                        + ", ".join("?" for _ in chapters) + ")")
                params.extend(chapters)
            sql += " ORDER BY bm25(figures_fts) LIMIT ?"
            params.append(want)
            return conn.execute(sql, params).fetchall()

        # by catalog row, not by number: a number two rows hold (a figure
        # over several pages, a number printed twice) keeps both rows
        fig_key = lambda r: r["rid"]
        strategy = _qe.EXPANSION_STRATEGY
        ran = {"q": query}  # the query as last run (re-quoted when it failed)

        def search(q: str, relaxed: bool = False) -> list[sqlite3.Row]:
            ran["q"] = q
            if strategy == "rerank":
                # "shotgun": BM25 ranks the literal+synonym union in one query.
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
                    rows = _qe.zero_literal_hits(q, run, want, fig_key)
                else:
                    rows = _qe.merge_hits(literal[:_qe.EXPANSION_PIN],
                                          run(combined), want, key=fig_key)
            else:
                rows = run(q)
                # "fill" (targeted): append synonym hits to remaining slots when
                # the literal AND-query under-returns on a terminology mismatch.
                if strategy == "fill" and len(rows) < want:
                    expansion = _qe.expand_query(q)
                    if expansion:
                        rows = _qe.merge_hits(rows, run(expansion), want,
                                              key=fig_key)
            # Broad OR-of-terms ALSO fills remaining slots (all strategies); it
            # is complementary to synonym expansion and must not be suppressed.
            if len(rows) < want:
                fb = _or_fallback(q)
                if not fb and relaxed:
                    # a query re-quoted by fts_safe_query: its words, OR-ed
                    fb = _or_fallback(plain_terms(q))
                if fb and fb != q:
                    rows = _qe.merge_hits(rows, run(fb), want, key=fig_key)
            return rows

        # A query FTS5 cannot parse as written ("pseudo-static", "Table
        # 5-2") is run again with those tokens quoted (_retrieval_db,
        # live smoke wave 1 A11).
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
        marks, absent = match_marks(conn, "figures_fts",
                                    [r["rid"] for r in page], ran["q"])
        hits = []
        for r in page:
            hit = _row_to_hit(r)
            hit.update(marks.get(r["rid"], {}))
            hits.append(hit)
        if max_chars is None:
            return hits
        if not rows:
            scope = ("the catalog of " + ", ".join(refs) if refs
                     else "the figure catalogs")
            if chapters:
                scope += f", chapter {chapter}"
            tried = TRIED_ALL if strategy != "off" else (
                "every word, then any one of the words; synonyms are off: "
                "GEOTECH_RETRIEVAL_EXPANSION=off")
            out = dict({"hits": [], "shown": 0}, **absent_words_note(
                _words_in_no_figure(conn, ran["q"], refs, chapters),
                scope, tried, [p for r in refs
                               for p in _packs.problems_by_pack().get(r, [])
                               if r.startswith(_packs.PACK_PREFIX)]))
        else:
            out = with_match_summary(fit_hits(
                hits, max_chars, text_fields=("caption",), offset=offset,
                more=more, max_offset=_MAX_OFFSET,
                narrow=("narrow the query (more specific words, or a "
                        "'reference')"),
                fetch="figure_get returns a figure's whole catalog row",
                more_text="more match" if not marks else "more were found"),
                match_summary(list(marks.values()), absent))
        if reference and refs != [reference]:
            # the catalog(s) a loosely spelled reference was read as
            out["resolved_reference"] = refs[0] if len(refs) == 1 else refs
        return out
    finally:
        conn.close()


def _words_in_no_figure(conn: sqlite3.Connection, query: str, refs: list,
                        chapters: list) -> list:
    """The query's words that no catalog row in the scope holds."""
    out = []
    for w in query_words(query):
        sql = ("SELECT 1 FROM figures_fts x JOIN figures f "
               "ON f.rowid = x.rowid WHERE figures_fts MATCH ?")
        params: list[Any] = [w]
        if refs:
            sql += (" AND f.reference IN ("
                    + ", ".join("?" for _ in refs) + ")")
            params.extend(refs)
        if chapters:
            sql += (" AND f.chapter IN ("
                    + ", ".join("?" for _ in chapters) + ")")
            params.extend(chapters)
        try:
            if conn.execute(sql + " LIMIT 1", params).fetchone() is None:
                out.append(w)
        except sqlite3.OperationalError:
            continue
    return out


def _page_label(row: sqlite3.Row) -> str:
    """``'page index 263 (printed page 244) "caption"'`` for one row."""
    printed = (f" (printed page {row['printed_page']})"
               if row["printed_page"] not in (None, "") else "")
    return (f"page index {row['pdf_page_index']}{printed} "
            f"\"{str(row['caption'] or '')[:80]}\"")


def figure_get(reference: str, figure_number: str,
               max_chars: int | None = None,
               pdf_page_index: int | None = None) -> dict[str, Any]:
    """Fetch the full catalog row for one figure.

    Parameters
    ----------
    reference : str
        Reference id (e.g. ``"dm7_2"``). Other spellings resolve
        (:func:`resolve_reference`): ``gec10`` / ``GEC-10`` for ``gec_10``,
        ``dm7`` for whichever of ``dm7_1`` / ``dm7_2`` holds the figure, or
        the document's designation (``UFC 3-250-01``).
    figure_number : str
        Figure id as in the source (e.g. ``"4-12"``, ``"P-1"``, ``"B-3"``).
        A leading ``"Figure "`` / ``"Fig. "`` is tolerated.
    max_chars : int, optional
        The largest result the caller can take, in JSON characters. A row
        longer than that (a few catalog captions run on into the page
        text) comes back with its caption / description cut to fit and a
        ``note`` naming what was cut. Default None: the whole row.
    pdf_page_index : int, optional
        Which page, for a number the catalog holds more than once: a figure
        that continues over several pages (GEC-12 Figure D-1, six pages)
        or a number the print gives two figures (UFC 3-250-01 prints two
        Figures F-21). A search hit carries each row's ``pdf_page_index``.

    Returns
    -------
    dict
        Full row incl. ``caption``, ``description``, ``chapter``, ``pdf_path``,
        ``pdf_page_index`` (0-based), ``printed_page``, ``page_estimated``;
        plus ``bbox`` (``[x0, y0, x1, y1]``, PDF points, top-left origin: the
        chart's box on the page) and ``read_notes`` (how to read the chart)
        only where the catalog gives them (local packs, REF-64).

    Raises
    ------
    KeyError
        If no such figure exists -- naming the valid catalog ids, or the
        nearest figure numbers in the catalog. Also if the catalog holds
        the number more than once and ``pdf_page_index`` does not say
        which (before, the first row came back, and a read-off went to
        its page): the message names each row's page and caption.
    """
    num = _norm_fig_number(figure_number)
    keys = _fig_number_keys(figure_number)
    ref = resolve_reference(reference, figure_number)
    conn = _ro_connect()
    try:
        rows = conn.execute(
            "SELECT * FROM figures WHERE reference = ? "
            "AND " + _number_clause(keys) + " ORDER BY rowid",
            (ref, *keys),
        ).fetchall()
        if rows and pdf_page_index is not None:
            on_page = [r for r in rows
                       if r["pdf_page_index"] == int(pdf_page_index)]
            if not on_page:
                raise KeyError(
                    f"figure '{figure_number}' of '{ref}' is not on page "
                    f"index {pdf_page_index}; the catalog has it on "
                    + "; ".join(_page_label(r) for r in rows))
            rows = on_page
        if len(rows) > 1:
            raise KeyError(
                f"the catalog of '{ref}' holds figure '{figure_number}' "
                f"{len(rows)} times (a figure that runs over several "
                "pages, or a number the print uses twice): "
                + "; ".join(_page_label(r) for r in rows)
                + ". Say which with pdf_page_index=<its page index>")
        row = rows[0] if rows else None
        if row is None:
            import difflib
            numbers = [r["figure_number"] for r in conn.execute(
                "SELECT figure_number FROM figures WHERE reference = ?",
                (ref,)).fetchall()]
            near = difflib.get_close_matches(num, [n.upper() for n in numbers],
                                             n=5, cutoff=0.5)
            raise KeyError(
                f"figure '{figure_number}' not found in reference '{ref}'"
                + (f"; nearest figure numbers there: {', '.join(near)}"
                   if near else "")
                + " (figure_search finds a figure by what it shows)")
        out = _row_to_full(row)
        if max_chars is None:
            return out
        out, cut = fit_record(out, max_chars - 400,
                              text_fields=("caption", "description"))
        if cut:
            out["note"] = (
                "Cut to fit " + f"{max_chars:,} characters: " + ", ".join(
                    f"{k} (from {n:,} characters)" for k, n in cut.items())
                + ". The catalog's text for this figure runs on past its "
                "caption; the figure itself is on the page given "
                "(pdf_page_index).")
        return out
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


def resolve_pdf(reference: str, figure_number: str,
                pdf_page_index: int | None = None) -> tuple[Path, int]:
    """Resolve a figure to its absolute source PDF path and 0-based page index.

    ``pdf_page_index`` says which page for a number the catalog holds more
    than once (:func:`figure_get`); without it such a number raises
    ``KeyError`` naming each page.

    A built-in reference's PDF is located via the ``GEOTECH_REFERENCES_DOCS``
    folder when that env var is set (needed when the package is installed and
    the repo's ``docs/`` is absent), otherwise relative to the repo root.

    A local reference pack's PDF (REF-64) is looked for by its bare file name
    in the pack's own folder, then in ``GEOTECH_REFERENCES_DOCS``, and nowhere
    else: never relative to the repo root, so a pack cannot lead outside
    those two folders.

    Raises
    ------
    KeyError
        If the figure is unknown.
    FileNotFoundError
        If the source PDF cannot be found on disk.
    """
    rec = figure_get(reference, figure_number, pdf_page_index=pdf_page_index)
    pdf_rel = rec["pdf_path"]
    folder = _packs.pack_dir(rec["reference"])
    if folder is not None:
        docs = os.environ.get(_DOCS_ENV)
        if _packs.bare_file_name(pdf_rel):
            for base in (folder, Path(docs) if docs else None):
                if base is not None and (base / pdf_rel).is_file():
                    return ((base / pdf_rel).resolve(),
                            int(rec["pdf_page_index"]))
        raise FileNotFoundError(
            f"source PDF for {reference} {figure_number} not found: "
            f"'{pdf_rel}' is not in the pack's folder or in {_DOCS_ENV}."
        )
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
