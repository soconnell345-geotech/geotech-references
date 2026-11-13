"""
Unified References Agent — single Foundry dispatcher for all geotech-references.

Replaces the per-reference agents with three Foundry functions:

  1. lookup_reference          - Run a reference function (table/figure/equation/text)
  2. list_reference_methods    - Browse available functions for a given reference
  3. describe_reference_method - Get detailed parameter docs for a specific function

The `reference` parameter selects which reference library to query: any
subpackage of geotech_references, e.g. "dm7_1", "dm7_2", "gec_6", "gec_12",
"micropile", "ufc_pavement", "eurocode_7_1". list_reference_methods('') lists
them all with their citations; the catalog is read from the installed package.
"""

import json
import inspect

try:
    from functions.api import function
except ImportError:
    def function(fn):
        fn.__wrapped__ = fn
        return fn


# ---------------------------------------------------------------------------
# Reference catalog — read from the installed package, not kept by hand
# ---------------------------------------------------------------------------
# Each entry: {"submodules": [...], "has_text": bool, "citation": str}.
# A reference is any subpackage of geotech_references; its submodules are its
# public modules (tables, figures, equations, chapterN, ...); it has text when
# it ships text/*.json; its citation is the reference_id and reference_title
# of its chapter files, or the first line of its docstring when it has none.
# (The hand-kept catalog this replaces listed 12 of the package's 33
# references and had drifted: GEC-10's edition, GEC-11's and UFC 3-250-01's
# text. It is now read from the package, so it cannot drift.)


def _strip_volume(title: str) -> str:
    import re
    return re.split(r"\s+[\u2013\u2014-]\s+Volume\b", title, maxsplit=1)[0]


def _base_title(title: str) -> str:
    return title.split(" (", 1)[0]


def _shares_name(reference_id: str, title: str) -> bool:
    """True when reference_id and the title share a run of 2+ words."""
    a = reference_id.lower().split()
    b = _base_title(title).lower().split()
    runs = {tuple(a[i:i + 2]) for i in range(len(a) - 1)}
    return any(tuple(b[i:i + 2]) in runs for i in range(len(b) - 1))


def _citation(reference_id: str, title: str) -> str:
    title = _strip_volume(title.strip())
    if not reference_id:
        return title
    if title.startswith(reference_id):
        title = title[len(reference_id):].lstrip(" ,:-\u2013\u2014")
    elif _shares_name(reference_id, title):
        # reference_id already carries the name: keep only the title's
        # parenthetical (edition, date), so the name prints once.
        title = title[len(_base_title(title)):].strip()
        return f"{reference_id} {title}" if title else reference_id
    return f"{reference_id} \u2014 {title}" if title else reference_id


def _build_catalog() -> dict:
    import importlib
    import pkgutil
    from pathlib import Path

    import geotech_references

    catalog = {}
    for sub in sorted(pkgutil.iter_modules(geotech_references.__path__),
                      key=lambda m: m.name):
        if not sub.ispkg or sub.name.startswith("_"):
            continue
        pkg = importlib.import_module(f"geotech_references.{sub.name}")
        pkg_dir = Path(pkg.__file__).parent
        submodules = sorted(m.name for m in pkgutil.iter_modules(pkg.__path__)
                            if not m.ispkg and not m.name.startswith("_"))
        # a chapter file first: an appendix printed in a volume of its own
        # carries that volume's number (GEC-12 Appendix D, FHWA-NHI-16-064;
        # 2026-11-10 review, core-13) and is not the manual's citation
        texts = sorted((pkg_dir / "text").glob("*.json"),
                       key=lambda p: (not p.name.startswith("chapter"),
                                      p.name))
        citation = ""
        if texts:
            with open(texts[0], encoding="utf-8") as f:
                head = json.load(f)
            citation = _citation(head.get("reference_id") or "",
                                 head.get("reference_title") or "")
        if not citation:
            doc = (pkg.__doc__ or "").strip().splitlines()
            citation = doc[0].strip().rstrip(".") if doc else sub.name
        catalog[sub.name] = {
            "submodules": submodules,
            "has_text": bool(texts),
            "citation": citation,
        }
    return catalog


_REFERENCE_CATALOG = _build_catalog()

# Per-reference lazy cache: { ref_name: (METHOD_REGISTRY, METHOD_INFO) }
_LOADED = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _param_type_str(annotation) -> str:
    if annotation is inspect.Parameter.empty:
        return "float"
    if annotation is float:
        return "float"
    if annotation is int:
        return "int"
    if annotation is bool:
        return "bool"
    if annotation is str:
        return "str"
    ann_str = str(annotation)
    if "list" in ann_str.lower():
        return "list"
    if "dict" in ann_str.lower():
        return "dict"
    return ann_str


def _extract_info(func, category: str, citation: str) -> dict:
    doc = inspect.getdoc(func) or ""
    desc_lines = []
    for line in doc.split("\n"):
        if line.strip() == "":
            break
        desc_lines.append(line.strip())
    brief = " ".join(desc_lines) if desc_lines else "No description available."

    param_descs = {}
    in_params = False
    current_param = None
    for dline in doc.split("\n"):
        stripped = dline.strip()
        if stripped.lower() in ("parameters", "parameters:"):
            in_params = True
            continue
        if stripped.startswith("---"):
            continue
        if stripped.lower() in ("returns", "returns:", "raises", "raises:",
                                "examples", "examples:", "notes", "notes:"):
            in_params = False
            current_param = None
            continue
        if in_params:
            if " : " in stripped:
                current_param = stripped.split(" : ")[0].strip()
                param_descs[current_param] = ""
            elif current_param and stripped:
                if param_descs[current_param]:
                    param_descs[current_param] += " " + stripped
                else:
                    param_descs[current_param] = stripped

    sig = inspect.signature(func)
    params = {}
    for pname, p in sig.parameters.items():
        pinfo = {
            "type": _param_type_str(p.annotation),
            "required": p.default is inspect.Parameter.empty,
        }
        if p.default is not inspect.Parameter.empty:
            pinfo["default"] = p.default
        if pname in param_descs and param_descs[pname]:
            pinfo["description"] = param_descs[pname]
        params[pname] = pinfo

    info = {
        "category": category,
        "brief": brief,
        "reference": citation,
        "parameters": params,
    }
    ret_ann = sig.return_annotation
    if ret_ann is not inspect.Parameter.empty:
        info["returns"] = _param_type_str(ret_ann)
    return info


def _catalog_id(reference: str) -> str:
    """The catalog id ``reference`` names, read as the library's searches
    and fetches read it (2026-11-10 review follow-up): the id, another
    spelling of it (``gec12``), or a report number its text or figure
    catalog carries (``FHWA-NHI-16-010`` -> ``gec_12``). Raises ``KeyError``
    naming the ids for a name that means nothing, and with the library's
    refusal for ``dm7`` or a number that could be several."""
    if reference in _REFERENCE_CATALOG:
        return reference
    from geotech_references import _figures_db, _retrieval_db
    key = _retrieval_db.id_key(reference)
    spelled = [r for r in _REFERENCE_CATALOG
               if _retrieval_db.id_key(r) == key]
    if len(spelled) == 1:
        return spelled[0]
    if key in _retrieval_db.SHARED_NAMES:
        _retrieval_db.resolve_text_reference(reference)  # raises, naming both
    for resolve in (_retrieval_db.resolve_text_reference,
                    _figures_db.resolve_reference):
        try:
            found = resolve(reference)
        except KeyError as e:
            if "could be more than one report number" in str(e):
                raise
            continue
        if found in _REFERENCE_CATALOG:
            return found
    raise KeyError(
        f"Unknown reference '{reference}'. Available: "
        + ", ".join(sorted(_REFERENCE_CATALOG.keys())))


def _load_reference(reference: str):
    """Lazy-load one reference's METHOD_REGISTRY and METHOD_INFO.
    ``reference`` may be any name :func:`_catalog_id` reads."""
    if reference in _LOADED:
        return _LOADED[reference]

    reference = _catalog_id(reference)
    if reference in _LOADED:
        return _LOADED[reference]

    cfg = _REFERENCE_CATALOG[reference]
    citation = cfg["citation"]
    registry = {}
    info = {}

    # --- Auto-discover functions in each submodule ---
    for submod_name in cfg["submodules"]:
        try:
            mod = __import__(
                f"geotech_references.{reference}.{submod_name}",
                fromlist=[submod_name],
            )
        except ImportError:
            continue

        # Category label: capitalize the submodule name
        category = f"{reference.upper()} {submod_name.title()}"

        for fname, func in inspect.getmembers(mod, inspect.isfunction):
            if fname.startswith("_"):
                continue
            # Only register functions defined in this submodule
            # (avoid pulling in re-exported helpers from other modules)
            if getattr(func, "__module__", "") != mod.__name__:
                continue
            registry[fname] = func
            info[fname] = _extract_info(func, category, citation)

    # --- Add text retrieval functions if available ---
    if cfg["has_text"]:
        try:
            from geotech_references import _retrieval

            def _make_text_fns(ref_id):
                def retrieve_section(section_id: str) -> dict:
                    """Retrieve a specific section by its ID (e.g., '5.7.2').

                    Returns the section dict with title, body, key_points,
                    equations, figures, tables, and applicability fields.

                    Parameters
                    ----------
                    section_id : str
                        Section identifier (e.g., '5.7.2', '4.4').
                    """
                    return _retrieval.retrieve_section(ref_id, section_id)

                def search_sections(query: str) -> list:
                    """Keyword search across all sections of this reference.

                    Searches titles, body text, key_points, and applicability.
                    Multiple words are AND-matched.

                    Parameters
                    ----------
                    query : str
                        Search query (case-insensitive).
                    """
                    return _retrieval.search_sections(ref_id, query)

                def list_chapters() -> list:
                    """List all chapters and section IDs for this reference."""
                    return _retrieval.list_chapters(ref_id)

                def load_chapter(chapter: int) -> dict:
                    """Load a full chapter JSON file.

                    Parameters
                    ----------
                    chapter : int
                        Chapter number.
                    """
                    return _retrieval.load_chapter(ref_id, chapter)

                return {
                    "retrieve_section": retrieve_section,
                    "search_sections": search_sections,
                    "list_chapters": list_chapters,
                    "load_chapter": load_chapter,
                }

            text_fns = _make_text_fns(reference)
            for fname, func in text_fns.items():
                registry[fname] = func
                info[fname] = _extract_info(func, "Text Retrieval", citation)
        except ImportError:
            pass

    _LOADED[reference] = (registry, info)
    return registry, info


# ---------------------------------------------------------------------------
# Foundry functions
# ---------------------------------------------------------------------------

@function
def lookup_reference(reference: str, method: str, parameters_json: str) -> str:
    """
    Unified geotechnical reference lookup — tables, figures, equations, and text
    from every reference in geotech-references (DM 7.1/7.2, the GEC series,
    micropiles, the UFC pavement and foundation criteria, Eurocode 7, and the
    others listed by list_reference_methods('')).

    Use this for any numeric value from a reference table or figure, or to
    retrieve structured reference text. Prefer this over searching uploaded PDFs
    when the value comes from a table/figure that has been digitized.

    Parameters:
        reference: Which reference to query, e.g. 'dm7_1', 'dm7_2', 'gec_6',
            'gec_12', 'micropile', 'ufc_pavement', 'eurocode_7_1'. Call
            list_reference_methods('') for the full list.
        method: The function name within that reference (e.g.
            'table_4_4a_bond_strength_coarse', 'figure_4_3_friction_angle_spt',
            'retrieve_section', 'search_sections'). Use list_reference_methods
            to browse.
        parameters_json: JSON string of parameters for the function. Use
            describe_reference_method for details.

    Returns:
        JSON string with the result or an error message.
    """
    try:
        registry, info = _load_reference(reference)
    except KeyError as e:
        return json.dumps({"error": str(e)})

    try:
        parameters = json.loads(parameters_json) if parameters_json else {}
    except (json.JSONDecodeError, TypeError) as e:
        return json.dumps({"error": f"Invalid parameters_json: {str(e)}"})

    if method not in registry:
        matches = [m for m in registry if method.lower() in m.lower()]
        if matches:
            return json.dumps({
                "error": f"Unknown method '{method}' in '{reference}'. "
                         f"Did you mean: {', '.join(matches[:5])}?"
            })
        return json.dumps({
            "error": f"Unknown method '{method}' in '{reference}'. "
                     f"Use list_reference_methods('{reference}') to browse."
        })

    try:
        func = registry[method]
        result = func(**parameters)
        if isinstance(result, dict):
            return json.dumps(result, default=str)
        return json.dumps({"result": result}, default=str)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {str(e)}"})


@function
def list_reference_methods(reference: str, category: str = "") -> str:
    """
    Lists available functions for a given reference, organized by category.

    Parameters:
        reference: Which reference to list, e.g. 'dm7_1', 'gec_12',
            'ufc_pavement'. Pass '' (empty) to list all available references
            and their citations.
        category: Optional partial-match filter on category, method name, or
            brief description (e.g. 'bond', 'bearing', 'seismic', 'figures').

    Returns:
        JSON string with method names grouped by category, or — if reference
        is empty — a catalog of all available references.
    """
    if not reference:
        catalog = {
            ref: {"citation": cfg["citation"],
                  "submodules": cfg["submodules"],
                  "has_text_retrieval": cfg["has_text"]}
            for ref, cfg in _REFERENCE_CATALOG.items()
        }
        return json.dumps(catalog)

    try:
        registry, info = _load_reference(reference)
    except KeyError as e:
        return json.dumps({"error": str(e)})

    result = {}
    cat_filter = category.lower() if category else ""
    for method_name, minfo in info.items():
        cat = minfo["category"]
        if cat_filter:
            if (cat_filter not in cat.lower()
                    and cat_filter not in method_name.lower()
                    and cat_filter not in minfo.get("brief", "").lower()):
                continue
        result.setdefault(cat, {})[method_name] = minfo["brief"]
    return json.dumps(result)


@function
def describe_reference_method(reference: str, method: str) -> str:
    """
    Returns detailed documentation for a reference function: parameters,
    types, defaults, descriptions, return type, and citation.

    Parameters:
        reference: Which reference (e.g. 'gec_7', 'dm7_2', 'micropile').
        method: The method name (e.g. 'table_4_4a_bond_strength_coarse').

    Returns:
        JSON string with full method documentation.
    """
    try:
        registry, info = _load_reference(reference)
    except KeyError as e:
        return json.dumps({"error": str(e)})

    if method not in info:
        matches = [m for m in info if method.lower() in m.lower()]
        if matches:
            return json.dumps({
                "error": f"Unknown method '{method}' in '{reference}'. "
                         f"Similar: {', '.join(matches[:10])}"
            })
        return json.dumps({
            "error": f"Unknown method '{method}' in '{reference}'. "
                     f"Use list_reference_methods('{reference}') to browse."
        })
    return json.dumps(info[method], default=str)


# ---------------------------------------------------------------------------
# SQL/FTS retrieval tools (cross-reference, summary-first)
# ---------------------------------------------------------------------------

#: The largest search result the agent tool returns, in JSON characters:
#: the size GeotechStaffEngineer passes, under its 16,000-character cap.
SEARCH_MAX_CHARS = 14_000


@function
def reference_search(query: str, reference: str = "", chapter: int = 0,
                     limit: int = 5, offset: int = 0) -> str:
    """
    Full-text search across all structured reference text (DM7 + GEC + micropile).
    Returns ranked summary-only hits — call reference_get to fetch the full body.
    This is the noise-reduction lever: use it first, then drill in.

    Parameters:
        query: FTS5 MATCH query. Plain words are AND-matched with porter
            stemming. Use quotes for phrases ("primary consolidation"),
            OR for alternatives, NEAR() for proximity, col:term to scope
            to one column (title/summary/body/key_points/applicability).
        reference: Optional reference to scope to: its id (e.g. 'dm7_1',
            'gec_12'), another spelling of it ('GEC-12'), or a report number
            its files carry. A volume's own number ('FHWA-NHI-16-010')
            searches that volume alone. Empty string searches all
            references.
        chapter: Optional chapter number to scope to. Only meaningful when
            reference is set. 0 means no chapter filter.
        limit: Max hits (default 5, capped at 50).
        offset: Hits to skip, for the next page (the note gives it).

    Returns:
        JSON object: "hits" (each with reference, reference_title,
        reference_id, chapter, chapter_title, section_id, title, summary,
        and "match" on a hit that does not hold every word), "shown", and
        a "note" saying how to get more. A reference that was not itself
        an id adds "resolved_reference"; a report number that is one volume
        adds "report_number" and says so in the note. On error,
        {"error": ...}. (Before the 2026-11-10 review follow-up this was a
        plain list of hits, which could not carry the note.)
    """
    try:
        from geotech_references import _retrieval_db
        ref = reference if reference else None
        ch = int(chapter) if chapter else None
        out = _retrieval_db.reference_search(
            query, reference=ref, chapter=ch, limit=limit,
            offset=int(offset or 0), max_chars=SEARCH_MAX_CHARS)
        return json.dumps(out, default=str)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {str(e)}"})


@function
def reference_get(reference: str, section_id: str) -> str:
    """
    Fetch the full body of one reference section by its id.

    Use after reference_search to drill into a specific hit. Returns the
    full body text plus key_points, applicability, equations array (with
    implemented_in pointing to Python functions), figures, and tables.

    Parameters:
        reference: Reference id (e.g. 'dm7_1', 'gec_12', 'micropile').
        section_id: Section id as it appears in the source. Examples:
            UFC hyphen-then-dot form: '4-2.1', '5-5.4'
            FHWA dot form: '5.7.2', '4.4'
            Prologue: 'P-1', 'P-2'

    Returns:
        JSON dict with the full section, or {"error": "..."} if not found.
    """
    try:
        from geotech_references import _retrieval_db
        return json.dumps(_retrieval_db.reference_get(reference, section_id),
                          default=str)
    except KeyError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {str(e)}"})


@function
def table_search(query: str, reference: str = "", chapter: int = 0,
                 limit: int = 5, offset: int = 0) -> str:
    """
    Find a printed table by its caption, number or the section that lists it,
    in the table catalogs of every reference (REF-86). Each hit says where the
    table's values are: "text" (typed in a stored section: reference_get with
    values_in), "lookup" (a coded function: lookup_reference with values_in)
    or "page" (only on the printed page: render pdf_page_index and read it).

    Parameters:
        query: FTS5 MATCH query over table numbers, captions and section
            titles (plain words AND-matched with porter stemming; quotes for
            phrases, OR for alternatives).
        reference: Optional reference to scope to: its id ('dm7_2'), another
            spelling ('GEC-10'), or a report number its rows carry. Empty
            string searches all references.
        chapter: Optional chapter number to scope to; 0 means no filter.
        limit: Max hits (default 5, capped at 50).
        offset: Hits to skip, for the next page (the note gives it).

    Returns:
        JSON object: "hits" (each with reference, reference_title,
        reference_id, table_number, caption, chapter, section_id,
        pdf_page_index, printed_page, values, values_in, and "pages" for a
        table over several pages, "match" on a hit that does not hold every
        word), "shown", and a "note" saying how to get more. On error,
        {"error": ...}.
    """
    try:
        from geotech_references import _tables_db
        ref = reference if reference else None
        ch = int(chapter) if chapter else None
        out = _tables_db.table_search(
            query, reference=ref, chapter=ch, limit=limit,
            offset=int(offset or 0), max_chars=SEARCH_MAX_CHARS)
        return json.dumps(out, default=str)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {str(e)}"})


@function
def table_get(reference: str, table_number: str,
              pdf_page_index: int = -1) -> str:
    """
    Fetch the catalog row of one printed table: its caption, chapter, the
    section that lists it, the PDF and page(s) it is printed on, and where its
    values are ("values", "values_in", and a one-sentence "how_to_read").

    Parameters:
        reference: Reference id (e.g. 'dm7_2', 'gec_10'), or another spelling
            or report number of it.
        table_number: Table number as printed (e.g. '6-11', 'A.7', 'C-2a');
            a leading 'Table ' is tolerated.
        pdf_page_index: Only for a number the catalog holds more than once
            (the error names each page): any page of the table wanted. -1
            (default) means not given.

    Returns:
        JSON dict with the row, or {"error": "..."} if not found.
    """
    try:
        from geotech_references import _tables_db
        page = None if pdf_page_index is None or int(pdf_page_index) < 0 \
            else int(pdf_page_index)
        return json.dumps(_tables_db.table_get(
            reference, table_number, pdf_page_index=page,
            max_chars=SEARCH_MAX_CHARS), default=str)
    except KeyError as e:
        return json.dumps({"error": str(e).strip("\"'")})
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {str(e)}"})


@function
def reference_query(sql: str) -> str:
    """
    Run a read-only SELECT against the reference text database.

    For advanced queries that the simple search/get tools can't express:
    counts, GROUP BY, JOIN with FTS, custom filters, etc.

    Tables available:
      - sections: one row per section. Columns: reference, reference_title,
        chapter, chapter_title, section_id, title, summary, body, key_points
        (newline-joined), applicability, equations_json, figures_json,
        tables_json.
      - sections_fts: FTS5 virtual table over title/summary/body/key_points/
        applicability. Use 'sections_fts MATCH ?' and 'bm25(sections_fts)'.

    Only single SELECT (or WITH ... SELECT) statements are accepted. The
    connection is opened read-only. Result set is capped at 50 rows.

    Parameters:
        sql: SELECT statement. Use ? placeholders are not available — embed
            literal values directly. Multiple statements are rejected.

    Returns:
        JSON list of result rows as dicts, or [{"error": "..."}].
    """
    try:
        from geotech_references import _retrieval_db
        return json.dumps(_retrieval_db.reference_query(sql), default=str)
    except Exception as e:
        return json.dumps([{"error": f"{type(e).__name__}: {str(e)}"}])
