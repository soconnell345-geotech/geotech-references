"""
FEMA P-2082 Agent — Foundry-style wrapper for the 2020 NEHRP Provisions.

FEMA P-2082-1 (2020), NEHRP Recommended Seismic Provisions for New Buildings
and Other Structures. Geotech-relevant seismic-site content only:
  - Chapter 20: Site Classification Procedure (Vs30 -> Site Class; the REVISED
    2020 scheme with the new intermediate classes BC, CD, DE).
  - Chapter 11: Seismic Design Criteria (SDS/SD1, two-period design spectrum,
    Seismic Design Category from SDS and SD1, Risk Category / Importance Factor).

Three entry-point functions:
  1. fema_p2082_agent           - Run a function (text retrieval or lookup)
  2. fema_p2082_list_methods    - Browse available functions by category
  3. fema_p2082_describe_method - Get detailed parameter docs for a function
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
    from geotech_references.fema_p2082 import tables, equations

    _METHOD_REGISTRY = {}
    _METHOD_INFO = {}

    def retrieve_section(section_id: str) -> dict:
        """Retrieve a specific FEMA P-2082 section by ID (e.g., '20.2', '11.6').

        Parameters
        ----------
        section_id : str
            Section identifier as it appears in the source.
        Returns
        -------
        dict
            Full section data.
        """
        return _retrieval.retrieve_section("fema_p2082", section_id)

    def search_sections(query: str) -> list:
        """Keyword search across all FEMA P-2082 sections.

        Parameters
        ----------
        query : str
            Search query (case-insensitive, AND-matched).
        Returns
        -------
        list of dict
            Matching sections ranked by relevance.
        """
        return _retrieval.search_sections("fema_p2082", query)

    def list_chapters() -> list:
        """List all FEMA P-2082 chapters and their section IDs.

        Returns
        -------
        list of dict
            Each dict has chapter, chapter_title, and sections list.
        """
        return _retrieval.list_chapters("fema_p2082")

    def load_chapter(chapter: int) -> dict:
        """Load a full FEMA P-2082 chapter JSON (11 or 20).

        Parameters
        ----------
        chapter : int
            Chapter number (11 = Seismic Design Criteria, 20 = Site Classification).
        Returns
        -------
        dict
            Full chapter data.
        """
        return _retrieval.load_chapter("fema_p2082", chapter)

    _text = {
        "retrieve_section": retrieve_section,
        "search_sections": search_sections,
        "list_chapters": list_chapters,
        "load_chapter": load_chapter,
    }
    for name, func in _text.items():
        _METHOD_REGISTRY[name] = func
        _METHOD_INFO[name] = _extract_info(func, "Text Retrieval", "FEMA P-2082")

    for mod, category, ref in [
        (tables, "FEMA P-2082 Tables", "FEMA P-2082"),
        (equations, "FEMA P-2082 Equations", "FEMA P-2082"),
    ]:
        for name, func in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("_"):
                continue
            _METHOD_REGISTRY[name] = func
            _METHOD_INFO[name] = _extract_info(func, category, ref)

    return _METHOD_REGISTRY, _METHOD_INFO


@function
def fema_p2082_agent(method: str, parameters_json: str) -> str:
    """
    FEMA P-2082 (2020 NEHRP Provisions) seismic site-design tool.

    Provides geotech-relevant seismic-site content from FEMA P-2082-1 (2020):

    - Site classification (Table 20.2-1): the REVISED 2020 NEHRP scheme with the
      new intermediate site classes BC, CD, DE; Vs30 -> Site Class A/B/BC/C/CD/D/
      DE/E/F. Site Class BC is the new reference (baseline) site condition.
    - Site Class F triggers (Section 20.2.1) and Site Class E soft-clay override.
    - Design spectral parameters: SDS = 2/3 SMS, SD1 = 2/3 SM1; two-period design
      response spectrum (Section 11.4.5.2).
    - Seismic Design Category (Tables 11.6-1 and 11.6-2) from SDS and SD1, the
      more-severe rule, and the S1 >= 0.75 override (SDC E / F).
    - Risk Category Importance Factor Ie.
    - Reference text retrieval (sections, search, chapter listing/loading).

    NOTE: P-2082 DELETED the ASCE 7-16 Fa/Fv site coefficients; SMS/SM1 come
    directly from the USGS Seismic Design Geodatabase per site class.

    Parameters:
        method: The function name. Use fema_p2082_list_methods() to browse.
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
        return json.dumps({"error": f"Unknown '{method}'. Use fema_p2082_list_methods()."})
    try:
        result = METHOD_REGISTRY[method](**params)
        if isinstance(result, (dict, list)):
            return json.dumps(result, default=str)
        return json.dumps({"result": result}, default=str)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


@function
def fema_p2082_list_methods(category: str = "") -> str:
    """
    Lists available FEMA P-2082 functions organized by category.

    Parameters:
        category: Optional filter (e.g., 'site', 'sdc', 'spectral', 'text').

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
def fema_p2082_describe_method(method: str) -> str:
    """
    Returns detailed documentation for a FEMA P-2082 function.

    Parameters:
        method: The method name (e.g., 'site_class_from_vs30', 'seismic_design_category').

    Returns:
        JSON string with parameters, types, defaults, and description.
    """
    _, METHOD_INFO = _load_registry()
    if method not in METHOD_INFO:
        matches = [m for m in METHOD_INFO if method.lower() in m.lower()]
        if matches:
            return json.dumps({"error": f"Unknown '{method}'. Similar: {', '.join(matches[:10])}"})
        return json.dumps({"error": f"Unknown '{method}'. Use fema_p2082_list_methods()."})
    return json.dumps(METHOD_INFO[method], default=str)
