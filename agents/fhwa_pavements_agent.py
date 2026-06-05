"""
FHWA-NHI-05-037 "Geotechnical Aspects of Pavements" Agent — Foundry-style wrapper.

Geotechnical Aspects of Pavements (FHWA-NHI-05-037, Reference Manual /
Participant Workbook, NHI Course No. 132040, FHWA, May 2006). This is the broad
GEOTECHNICAL-aspects pavement reference (DISTINCT from the narrower UFC 3-250-01
roads/parking design module). Soil/geotech-input content:
  - Resilient modulus Mr: default values by AASHTO/USCS soil class (Table 5-35),
    correlations from CBR / R-value / DCP / plasticity+gradation (Table 5-34),
    the stress-dependent granular Mr model (Eq. 5.9), seasonal effective Mr, and
    backcalculated-to-design adjustment factors.
  - CBR: typical field CBR by USCS soil class (Table 5-28) and DCP correlation.
  - Soil suitability as a pavement material by USCS class (Table 4-14).
  - Drainage: AASHTO drainage modifier mi (flexible, Table 5-49) and coefficient
    Cd (rigid, Table 5-50); drainage-quality definitions (Table 7-4); typical
    saturated hydraulic conductivity (Tables 5-56/5-57).
  - Frost susceptibility classification F1-F4 (Table 7-12).
  - Swell/expansive soils (Tables 5-24, 7-17) and stabilization guidance.
  - Compaction: dry unit weight & OMC by AASHTO class (Table 5-18).

Units follow the source (Mr in psi, CBR/R-value in %, unit weight in pcf).

Three entry-point functions:
  1. fhwa_pavements_agent           - Run a function (lookup or text retrieval)
  2. fhwa_pavements_list_methods    - Browse available functions by category
  3. fhwa_pavements_describe_method - Get detailed parameter docs for a function
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
        if p.kind in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL):
            continue
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
    from geotech_references.fhwa_pavements import tables, equations

    _METHOD_REGISTRY = {}
    _METHOD_INFO = {}

    def retrieve_section(section_id: str) -> dict:
        """Retrieve a specific FHWA-NHI-05-037 section by ID (e.g., '5.4.3', '7.5').

        Parameters
        ----------
        section_id : str
            Section identifier as it appears in the source.
        Returns
        -------
        dict
            Full section data.
        """
        return _retrieval.retrieve_section("fhwa_pavements", section_id)

    def search_sections(query: str) -> list:
        """Keyword search across all FHWA-NHI-05-037 sections.

        Parameters
        ----------
        query : str
            Search query (case-insensitive, AND-matched).
        Returns
        -------
        list of dict
            Matching sections ranked by relevance.
        """
        return _retrieval.search_sections("fhwa_pavements", query)

    def list_chapters() -> list:
        """List all FHWA-NHI-05-037 chapters and their section IDs.

        Returns
        -------
        list of dict
            Each dict has chapter, chapter_title, and sections list.
        """
        return _retrieval.list_chapters("fhwa_pavements")

    def load_chapter(chapter: int) -> dict:
        """Load a full FHWA-NHI-05-037 chapter JSON (4, 5, 7).

        Parameters
        ----------
        chapter : int
            Chapter number (4 Exploration & Testing, 5 Geotechnical Inputs,
            7 Design Details & Construction).
        Returns
        -------
        dict
            Full chapter data.
        """
        return _retrieval.load_chapter("fhwa_pavements", chapter)

    _text = {
        "retrieve_section": retrieve_section,
        "search_sections": search_sections,
        "list_chapters": list_chapters,
        "load_chapter": load_chapter,
    }
    for name, func in _text.items():
        _METHOD_REGISTRY[name] = func
        _METHOD_INFO[name] = _extract_info(func, "Text Retrieval", "FHWA-NHI-05-037")

    for mod, category, ref in [
        (tables, "FHWA Pavements Tables", "FHWA-NHI-05-037"),
        (equations, "FHWA Pavements Equations", "FHWA-NHI-05-037"),
    ]:
        for name, func in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("_"):
                continue
            _METHOD_REGISTRY[name] = func
            _METHOD_INFO[name] = _extract_info(func, category, ref)

    return _METHOD_REGISTRY, _METHOD_INFO


@function
def fhwa_pavements_agent(method: str, parameters_json: str) -> str:
    """
    FHWA-NHI-05-037 "Geotechnical Aspects of Pavements" tool.

    Geotechnical inputs for pavement design from FHWA-NHI-05-037 (FHWA, 2006),
    in the source's units (Mr in psi, CBR/R-value in %, unit weight in pcf):

    - Resilient modulus Mr: default values by AASHTO/USCS soil class (Table
      5-35), correlations from CBR (Mr = 2555*CBR^0.64), R-value, DCP, and
      plasticity+gradation (Table 5-34), the stress-dependent granular Mr model
      Mr = k1*theta^k2 (Eq. 5.9), seasonal effective Mr, and backcalculated->
      design adjustment factors.
    - CBR: typical field CBR by USCS soil class (Table 5-28); CBR from DCP.
    - Soil suitability as a pavement material by USCS class - subgrade strength,
      frost action, compressibility, drainage (Table 4-14).
    - Drainage: AASHTO modifier mi (flexible, Table 5-49) and coefficient Cd
      (rigid, Table 5-50); quality definitions (Table 7-4); permeability of
      soils/materials (Tables 5-56/5-57).
    - Frost susceptibility F1-F4 (Table 7-12).
    - Swell potential (Tables 5-24, 7-17) and lime/cement/asphalt stabilization.
    - Compaction: dry unit weight & OMC by AASHTO class (Table 5-18).
    - Reference text retrieval (sections, search, chapter listing/loading).

    NOTE: distinct from the UFC 3-250-01 roads/parking pavement-DESIGN module.

    Parameters:
        method: The function name. Use fhwa_pavements_list_methods() to browse.
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
        return json.dumps({"error": f"Unknown '{method}'. Use fhwa_pavements_list_methods()."})
    try:
        result = METHOD_REGISTRY[method](**params)
        if isinstance(result, (dict, list)):
            return json.dumps(result, default=str)
        return json.dumps({"result": result}, default=str)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


@function
def fhwa_pavements_list_methods(category: str = "") -> str:
    """
    Lists available FHWA-NHI-05-037 (Geotechnical Aspects of Pavements) functions.

    Parameters:
        category: Optional filter (e.g., 'resilient modulus', 'cbr', 'frost',
            'drainage', 'swell', 'permeability', 'compaction', 'text').

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
def fhwa_pavements_describe_method(method: str) -> str:
    """
    Returns detailed documentation for an FHWA-NHI-05-037 function.

    Parameters:
        method: The method name (e.g., 'table_5_35_default_resilient_modulus',
            'resilient_modulus_from_cbr', 'table_7_12_frost_susceptibility').

    Returns:
        JSON string with parameters, types, defaults, and description.
    """
    _, METHOD_INFO = _load_registry()
    if method not in METHOD_INFO:
        matches = [m for m in METHOD_INFO if method.lower() in m.lower()]
        if matches:
            return json.dumps({"error": f"Unknown '{method}'. Similar: {', '.join(matches[:10])}"})
        return json.dumps({"error": f"Unknown '{method}'. Use fhwa_pavements_list_methods()."})
    return json.dumps(METHOD_INFO[method], default=str)
