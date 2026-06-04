"""
GEC-5 Agent — Foundry-style wrapper for GEC-5 reference text retrieval.

FHWA NHI-16-072 (2017), Geotechnical Site Characterization.

Three entry-point functions:
  1. gec5_agent           - Run a GEC-5 function (text retrieval)
  2. gec5_list_methods    - Browse available functions by category
  3. gec5_describe_method - Get detailed parameter docs for a specific function
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

    _METHOD_REGISTRY = {}
    _METHOD_INFO = {}

    def retrieve_section(section_id: str) -> dict:
        """Retrieve a specific GEC-5 section by ID (e.g., '4.17').

        Parameters
        ----------
        section_id : str
            Section identifier as it appears in the source.
        Returns
        -------
        dict
            Full section data.
        """
        return _retrieval.retrieve_section("gec_5", section_id)

    def search_sections(query: str) -> list:
        """Keyword search across all GEC-5 sections (site characterization topics).

        Parameters
        ----------
        query : str
            Search query (case-insensitive, AND-matched).
        Returns
        -------
        list of dict
            Matching sections ranked by relevance.
        """
        return _retrieval.search_sections("gec_5", query)

    def list_chapters() -> list:
        """List all GEC-5 chapters and their section IDs.

        Returns
        -------
        list of dict
            Each dict has chapter, chapter_title, and sections list.
        """
        return _retrieval.list_chapters("gec_5")

    def load_chapter(chapter: int) -> dict:
        """Load a full GEC-5 chapter JSON.

        Parameters
        ----------
        chapter : int
            Chapter number (1-13).
        Returns
        -------
        dict
            Full chapter data.
        """
        return _retrieval.load_chapter("gec_5", chapter)

    _text = {
        "retrieve_section": retrieve_section,
        "search_sections": search_sections,
        "list_chapters": list_chapters,
        "load_chapter": load_chapter,
    }
    for name, func in _text.items():
        _METHOD_REGISTRY[name] = func
        _METHOD_INFO[name] = _extract_info(func, "Text Retrieval", "FHWA NHI-16-072")

    return _METHOD_REGISTRY, _METHOD_INFO


@function
def gec5_agent(method: str, parameters_json: str) -> str:
    """
    GEC-5 Geotechnical Site Characterization reference tool.

    Provides access to FHWA NHI-16-072 (GEC-5, 2017) reference text on
    geotechnical site characterization for transportation projects. Coverage:

    - Planning and scoping site investigations
    - Soil and rock identification and classification (USCS, AASHTO, CPT SBT)
    - Problematic soils (collapsible, expansive, organic, liquefiable, sensitive)
    - Consolidation properties (IL/CRS tests, preconsolidation, Cc, cv)
    - Shear strength (Su from UU/CU/FVT/CPT; phi' from triaxial/SPT/CPT)
    - Stiffness properties (Gmax from Vs; modulus reduction)
    - Rock properties (UCS, RMR, GSI, Hoek-Brown, Em)
    - Hydraulic properties and groundwater conditions
    - Design parameter selection and variability quantification
    - Geotechnical hazard identification (karst, seismic, landslides)
    - Documentation and reporting requirements

    Parameters:
        method: The function name. Use gec5_list_methods() to browse.
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
        return json.dumps({"error": f"Unknown '{method}'. Use gec5_list_methods()."})
    try:
        result = METHOD_REGISTRY[method](**params)
        if isinstance(result, (dict, list)):
            return json.dumps(result, default=str)
        return json.dumps({"result": result}, default=str)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


@function
def gec5_list_methods(category: str = "") -> str:
    """
    Lists available GEC-5 functions organized by category.

    Parameters:
        category: Optional filter (e.g., 'text', 'retrieval').

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
def gec5_describe_method(method: str) -> str:
    """
    Returns detailed documentation for a GEC-5 function.

    Parameters:
        method: The method name (e.g., 'search_sections', 'retrieve_section').

    Returns:
        JSON string with parameters, types, defaults, and description.
    """
    _, METHOD_INFO = _load_registry()
    if method not in METHOD_INFO:
        matches = [m for m in METHOD_INFO if method.lower() in m.lower()]
        if matches:
            return json.dumps({"error": f"Unknown '{method}'. Similar: {', '.join(matches[:10])}"})
        return json.dumps({"error": f"Unknown '{method}'. Use gec5_list_methods()."})
    return json.dumps(METHOD_INFO[method], default=str)
