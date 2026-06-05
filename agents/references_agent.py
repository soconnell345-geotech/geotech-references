"""
Unified References Agent — single Foundry dispatcher for all geotech-references.

Replaces the per-reference agents (dm7, gec6, gec7, gec10, gec11, gec12, gec13,
micropile, ufc_backfill, ufc_expansive, ufc_pavement) with three Foundry
functions:

  1. lookup_reference          - Run a reference function (table/figure/equation/text)
  2. list_reference_methods    - Browse available functions for a given reference
  3. describe_reference_method - Get detailed parameter docs for a specific function

The `reference` parameter selects which reference library to query, e.g.:
  "dm7_1", "dm7_2", "gec_6", "gec_7", "gec_10", "gec_11", "gec_12", "gec_13",
  "micropile", "ufc_backfill", "ufc_expansive", "ufc_pavement"
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
# Reference catalog — describes each reference's modules and capabilities
# ---------------------------------------------------------------------------
# Each entry: (submodules to scan, has_text_retrieval, citation)
_REFERENCE_CATALOG = {
    "dm7_1": {
        "submodules": ["chapter1", "chapter2", "chapter3", "chapter4",
                       "chapter5", "chapter6", "chapter7", "chapter8"],
        "has_text": True,
        "citation": "UFC 3-220-10 — Soil Mechanics (2022, Change 1 2025)",
    },
    "dm7_2": {
        "submodules": ["prologue", "chapter2", "chapter3", "chapter4",
                       "chapter5", "chapter6", "chapter7"],
        "has_text": True,
        "citation": "UFC 3-220-20 — Foundations and Earth Structures (2025)",
    },
    "gec_6": {
        "submodules": ["tables", "figures"],
        "has_text": True,
        "citation": "FHWA-SA-02-054 (GEC-6) — Shallow Foundations",
    },
    "gec_7": {
        "submodules": ["tables", "figures"],
        "has_text": True,
        "citation": "FHWA-NHI-14-007 (GEC-7) — Soil Nail Walls",
    },
    "gec_10": {
        "submodules": ["tables", "figures"],
        "has_text": True,
        "citation": "FHWA-NHI-10-016 (GEC-10) — Drilled Shafts",
    },
    "gec_11": {
        "submodules": ["tables", "figures"],
        "has_text": False,
        "citation": "FHWA-NHI-10-024 (GEC-11) — MSE Walls & Slopes",
    },
    "gec_12": {
        "submodules": ["tables", "figures"],
        "has_text": True,
        "citation": "FHWA-NHI-16-009 (GEC-12) — Driven Piles",
    },
    "gec_13": {
        "submodules": ["tables", "figures"],
        "has_text": True,
        "citation": "FHWA-NHI-16-027 (GEC-13) — Ground Modification Methods",
    },
    "micropile": {
        "submodules": ["tables", "figures"],
        "has_text": True,
        "citation": "FHWA-NHI-05-039 — Micropile Design & Construction",
    },
    "ufc_backfill": {
        "submodules": ["equations", "tables"],
        "has_text": False,
        "citation": "UFC 3-220-04N — Backfill for Subsurface Structures",
    },
    "ufc_expansive": {
        "submodules": ["equations", "tables"],
        "has_text": False,
        "citation": "UFC 3-220-07 — Foundations in Expansive Soils",
    },
    "ufc_pavement": {
        "submodules": ["equations", "tables"],
        "has_text": False,
        "citation": "UFC 3-260-02 — Airfield Pavement Design",
    },
}

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


def _load_reference(reference: str):
    """Lazy-load one reference's METHOD_REGISTRY and METHOD_INFO."""
    if reference in _LOADED:
        return _LOADED[reference]

    if reference not in _REFERENCE_CATALOG:
        raise KeyError(
            f"Unknown reference '{reference}'. Available: "
            + ", ".join(sorted(_REFERENCE_CATALOG.keys()))
        )

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
    from NAVFAC DM7, FHWA GEC-6/7/10/11/12/13, FHWA Micropile, and UFC standards
    (backfill, expansive, pavement).

    Use this for any numeric value from a reference table or figure, or to
    retrieve structured reference text. Prefer this over searching uploaded PDFs
    when the value comes from a table/figure that has been digitized.

    Parameters:
        reference: Which reference to query. One of:
            'dm7_1', 'dm7_2', 'gec_6', 'gec_7', 'gec_10', 'gec_11', 'gec_12',
            'gec_13', 'micropile', 'ufc_backfill', 'ufc_expansive',
            'ufc_pavement'
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
        reference: Which reference to list. One of: 'dm7_1', 'dm7_2', 'gec_6',
            'gec_7', 'gec_10', 'gec_11', 'gec_12', 'gec_13', 'micropile',
            'ufc_backfill', 'ufc_expansive', 'ufc_pavement'.
            Pass '' (empty) to list all available references and their citations.
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

@function
def reference_search(query: str, reference: str = "", chapter: int = 0,
                     limit: int = 5) -> str:
    """
    Full-text search across all structured reference text (DM7 + GEC + micropile).
    Returns ranked summary-only hits — call reference_get to fetch the full body.
    This is the noise-reduction lever: use it first, then drill in.

    Parameters:
        query: FTS5 MATCH query. Plain words are AND-matched with porter
            stemming. Use quotes for phrases ("primary consolidation"),
            OR for alternatives, NEAR() for proximity, col:term to scope
            to one column (title/summary/body/key_points/applicability).
        reference: Optional reference id to scope to (e.g. 'dm7_1', 'gec_12').
            Empty string searches all references.
        chapter: Optional chapter number to scope to. Only meaningful when
            reference is set. 0 means no chapter filter.
        limit: Max hits (default 5, capped at 50).

    Returns:
        JSON list of summary hits, each with reference, reference_title,
        chapter, chapter_title, section_id, title, and summary fields.
        On error, returns a one-element list with an 'error' field.
    """
    try:
        from geotech_references import _retrieval_db
        ref = reference if reference else None
        ch = int(chapter) if chapter else None
        hits = _retrieval_db.reference_search(query, reference=ref,
                                               chapter=ch, limit=limit)
        return json.dumps(hits, default=str)
    except Exception as e:
        return json.dumps([{"error": f"{type(e).__name__}: {str(e)}"}])


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
