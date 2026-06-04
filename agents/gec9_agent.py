"""
GEC-9 Agent — Foundry-style wrapper for GEC-9 reference text and lookups.

FHWA-HIF-18-031 (2018), Design, Analysis, and Testing of Laterally Loaded
Deep Foundations that Support Transportation Facilities.

Three entry-point functions:
  1. gec9_agent           - Run a GEC-9 function (text retrieval or lookup)
  2. gec9_list_methods    - Browse available functions by category
  3. gec9_describe_method - Get detailed parameter docs for a specific function
"""

import json
import inspect

try:
    from functions.api import function
except ImportError:
    def function(fn):
        fn.__wrapped__ = fn
        return fn

_METHOD_REGISTRY = None
_METHOD_INFO = None


def _param_type_str(annotation) -> str:
    if annotation is inspect.Parameter.empty: return "float"
    if annotation is float: return "float"
    if annotation is int: return "int"
    if annotation is bool: return "bool"
    if annotation is str: return "str"
    ann = str(annotation)
    if "list" in ann.lower(): return "list"
    if "dict" in ann.lower(): return "dict"
    return ann


def _extract_info(func, category: str, reference: str) -> dict:
    doc = inspect.getdoc(func) or ""
    brief = " ".join(line.strip() for line in doc.split("\n")
                     if line.strip())[:200] or "No description."
    param_descs = {}
    in_params = False
    current_param = None
    for line in doc.split("\n"):
        s = line.strip()
        if s.lower() in ("parameters", "parameters:"):
            in_params = True; continue
        if s.startswith("---"): continue
        if s.lower() in ("returns", "returns:", "raises", "raises:"):
            in_params = False; current_param = None; continue
        if in_params:
            if " : " in s:
                current_param = s.split(" : ")[0].strip()
                param_descs[current_param] = ""
            elif current_param and s:
                param_descs[current_param] = (
                    param_descs[current_param] + " " + s).strip()
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
    return {
        "category": category,
        "brief": brief,
        "reference": reference,
        "parameters": params,
    }


def _load_registry():
    global _METHOD_REGISTRY, _METHOD_INFO
    if _METHOD_REGISTRY is not None:
        return _METHOD_REGISTRY, _METHOD_INFO

    from geotech_references import _retrieval
    from geotech_references.gec_9 import tables

    _METHOD_REGISTRY = {}
    _METHOD_INFO = {}

    def retrieve_section(section_id: str) -> dict:
        """Retrieve a specific GEC-9 section by ID (e.g., '6.3').

        Parameters
        ----------
        section_id : str
            Section identifier as it appears in the source.
        Returns
        -------
        dict
            Full section data including body, key_points, equations, etc.
        """
        return _retrieval.retrieve_section("gec_9", section_id)

    def search_sections(query: str) -> list:
        """Keyword search across all GEC-9 sections.

        Parameters
        ----------
        query : str
            Search query (case-insensitive, AND-matched).
        Returns
        -------
        list of dict
            Matching sections ranked by relevance.
        """
        return _retrieval.search_sections("gec_9", query)

    def list_chapters() -> list:
        """List all GEC-9 chapters and their section IDs.

        Returns
        -------
        list of dict
            Each dict has chapter, chapter_title, and sections list.
        """
        return _retrieval.list_chapters("gec_9")

    def load_chapter(chapter: int) -> dict:
        """Load a full GEC-9 chapter JSON.

        Parameters
        ----------
        chapter : int
            Chapter number (1-13).
        Returns
        -------
        dict
            Full chapter data.
        """
        return _retrieval.load_chapter("gec_9", chapter)

    _text = {
        "retrieve_section": retrieve_section,
        "search_sections": search_sections,
        "list_chapters": list_chapters,
        "load_chapter": load_chapter,
    }
    for name, func in _text.items():
        _METHOD_REGISTRY[name] = func
        _METHOD_INFO[name] = _extract_info(func, "Text Retrieval", "FHWA-HIF-18-031")

    for name, func in inspect.getmembers(tables, inspect.isfunction):
        if name.startswith("_"):
            continue
        _METHOD_REGISTRY[name] = func
        _METHOD_INFO[name] = _extract_info(func, "GEC-9 Tables", "FHWA-HIF-18-031")

    return _METHOD_REGISTRY, _METHOD_INFO


@function
def gec9_agent(method: str, parameters_json: str) -> str:
    """
    GEC-9 Laterally Loaded Deep Foundations reference and lookup tool.

    Provides access to FHWA-HIF-18-031 (GEC-9, 2018) reference text and
    design lookups for laterally loaded piles and drilled shafts.
    Capabilities include:

    - Reference text retrieval (sections, search, chapter listing)
    - Lateral resistance factors for LRFD (Table 4-1)
    - P-multipliers for pile group lateral analysis (Table 7-1)
    - Initial p-y modulus k for stiff clay with free water (Table A-1)
    - Strain at 50% peak deviator stress ε50 for stiff clay (Table A-2)
    - Initial p-y modulus k for sand — loose/medium/dense, submerged/above water (Table A-3)

    Parameters:
        method: The function name. Use gec9_list_methods() to browse.
        parameters_json: JSON string of parameters.

    Returns:
        JSON string with the result or an error message.
    """
    METHOD_REGISTRY, _ = _load_registry()
    try:
        params = json.loads(parameters_json)
    except (json.JSONDecodeError, TypeError) as e:
        return json.dumps({"error": f"Invalid parameters_json: {e}"})
    if method not in METHOD_REGISTRY:
        matches = [m for m in METHOD_REGISTRY if method.lower() in m.lower()]
        if matches:
            return json.dumps({"error": f"Unknown '{method}'. Did you mean: {', '.join(matches[:5])}?"})
        return json.dumps({"error": f"Unknown '{method}'. Use gec9_list_methods()."})
    try:
        result = METHOD_REGISTRY[method](**params)
        if isinstance(result, (dict, list)):
            return json.dumps(result, default=str)
        return json.dumps({"result": result}, default=str)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


@function
def gec9_list_methods(category: str = "") -> str:
    """
    Lists available GEC-9 functions organized by category.

    Parameters:
        category: Optional filter (e.g., 'text', 'tables', 'p-y', 'clay', 'sand').

    Returns:
        JSON string with method names grouped by category.
    """
    _, METHOD_INFO = _load_registry()
    result = {}
    for name, info in METHOD_INFO.items():
        cat = info["category"]
        if category and (category.lower() not in cat.lower()
                         and category.lower() not in name.lower()
                         and category.lower() not in info.get("brief", "").lower()):
            continue
        result.setdefault(cat, {})[name] = info["brief"]
    return json.dumps(result)


@function
def gec9_describe_method(method: str) -> str:
    """
    Returns detailed documentation for a GEC-9 function.

    Parameters:
        method: The method name (e.g., 'table_7_1_p_multiplier', 'search_sections').

    Returns:
        JSON string with parameters, types, defaults, and description.
    """
    _, METHOD_INFO = _load_registry()
    if method not in METHOD_INFO:
        matches = [m for m in METHOD_INFO if method.lower() in m.lower()]
        if matches:
            return json.dumps({"error": f"Unknown '{method}'. Similar: {', '.join(matches[:10])}"})
        return json.dumps({"error": f"Unknown '{method}'. Use gec9_list_methods()."})
    return json.dumps(METHOD_INFO[method], default=str)
