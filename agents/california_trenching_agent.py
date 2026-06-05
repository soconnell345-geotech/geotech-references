"""
California Trenching and Shoring Manual Agent — Foundry-style wrapper.

California (Caltrans) Trenching and Shoring Manual (June 2011, Revision 2 -
July 2025), Division of Engineering Services, Structure Construction. Geotech /
excavation-engineering content only:
  - Chapter 2 (Cal/OSHA): Type A/B/C soil classification + maximum allowable
    temporary slopes (Table 2-1) + OSHA timber-shoring pressures.
  - Chapter 3 (Soils): granular/cohesive soil properties, Ka & equivalent fluid
    weight (Tables 3-1/3-2/3-3), test reliability (Table 3-4).
  - Chapter 4 (Earth Pressure): Rankine/Coulomb/Bell Ka/Kp/K0, apparent active
    coefficient (>= 0.25), wall friction (Table 4-2), mobilized movements (Table
    4-1), max allowable slope angle, log-spiral passive Kp (Caquot-Kerisel).
  - Chapter 5 (Surcharges), Chapter 6 (overstress, lagging), Chapter 7 (effective
    pile width / arching), Chapter 8 (apparent earth pressure for braced/anchored
    walls), Chapter 10 (heave, piping, slope stability).

Units are the manual's native US customary units (psf, pcf, tsf, ft, deg).

Three entry-point functions:
  1. california_trenching_agent           - Run a function (lookup or text retrieval)
  2. california_trenching_list_methods    - Browse available functions by category
  3. california_trenching_describe_method - Get detailed parameter docs for a function
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
    from geotech_references.california_trenching import tables, equations

    _METHOD_REGISTRY = {}
    _METHOD_INFO = {}

    def retrieve_section(section_id: str) -> dict:
        """Retrieve a specific Caltrans T&S Manual section by ID (e.g., '4-4', '8-3').

        Parameters
        ----------
        section_id : str
            Section identifier as it appears in the source (hyphen-dot form).
        Returns
        -------
        dict
            Full section data.
        """
        return _retrieval.retrieve_section("california_trenching", section_id)

    def search_sections(query: str) -> list:
        """Keyword search across all Caltrans T&S Manual sections.

        Parameters
        ----------
        query : str
            Search query (case-insensitive, AND-matched).
        Returns
        -------
        list of dict
            Matching sections ranked by relevance.
        """
        return _retrieval.search_sections("california_trenching", query)

    def list_chapters() -> list:
        """List all Caltrans T&S Manual chapters and their section IDs.

        Returns
        -------
        list of dict
            Each dict has chapter, chapter_title, and sections list.
        """
        return _retrieval.list_chapters("california_trenching")

    def load_chapter(chapter: int) -> dict:
        """Load a full Caltrans T&S Manual chapter JSON (2, 3, 4, 6, 7, 8, 10).

        Parameters
        ----------
        chapter : int
            Chapter number (2 Cal/OSHA, 3 Soils, 4 Earth Pressure, 6 Structural,
            7 Unrestrained, 8 Restrained, 10 Special Conditions).
        Returns
        -------
        dict
            Full chapter data.
        """
        return _retrieval.load_chapter("california_trenching", chapter)

    _text = {
        "retrieve_section": retrieve_section,
        "search_sections": search_sections,
        "list_chapters": list_chapters,
        "load_chapter": load_chapter,
    }
    for name, func in _text.items():
        _METHOD_REGISTRY[name] = func
        _METHOD_INFO[name] = _extract_info(func, "Text Retrieval", "Caltrans T&S Manual")

    for mod, category, ref in [
        (tables, "Caltrans T&S Tables", "Caltrans T&S Manual"),
        (equations, "Caltrans T&S Equations", "Caltrans T&S Manual"),
    ]:
        for name, func in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("_"):
                continue
            _METHOD_REGISTRY[name] = func
            _METHOD_INFO[name] = _extract_info(func, category, ref)

    return _METHOD_REGISTRY, _METHOD_INFO


@function
def california_trenching_agent(method: str, parameters_json: str) -> str:
    """
    California (Caltrans) Trenching and Shoring Manual tool.

    Geotech / excavation-engineering content from the Caltrans Trenching and
    Shoring Manual (June 2011, Revision 2 - July 2025), in native US customary
    units (psf, pcf, tsf, ft, deg):

    - Cal/OSHA Type A/B/C soil classification and maximum allowable temporary
      slopes (Stable Rock vertical, A 3/4:1, B 1:1, C 1-1/2:1; Table 2-1).
    - Soil properties: granular density/phi/unit weight vs N60 (Table 3-1),
      simplified Ka and equivalent fluid weight (Table 3-2), cohesive
      consistency vs unconfined compressive strength (Table 3-3).
    - Earth pressure: Rankine/Coulomb/Bell active & passive coefficients,
      at-rest K0, apparent active coefficient (>= 0.25), wall friction (Table
      4-2), maximum allowable slope angle for c-phi soil, log-spiral passive Kp
      (Caquot-Kerisel, Figure 4-20 / Matrix 4-1).
    - Apparent earth pressure (AEP) trapezoidal envelopes for braced/anchored
      walls (cohesionless PT = 1.3P; cohesive by stability number Ns = gamma*H/cu).
    - Structural: 133% overstress, lagging design load (0.6 x pressure, max 400
      psf), soldier-pile effective width / arching (f = 0.08*phi).
    - Special conditions: bottom-heave FS (Terzaghi, Bjerrum-Eide Nc, FS >= 1.5),
      piping, slope stability.
    - Reference text retrieval (sections, search, chapter listing/loading).

    Parameters:
        method: The function name. Use california_trenching_list_methods() to browse.
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
        return json.dumps({"error": f"Unknown '{method}'. Use california_trenching_list_methods()."})
    try:
        result = METHOD_REGISTRY[method](**params)
        if isinstance(result, (dict, list)):
            return json.dumps(result, default=str)
        return json.dumps({"result": result}, default=str)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


@function
def california_trenching_list_methods(category: str = "") -> str:
    """
    Lists available California Trenching and Shoring Manual functions by category.

    Parameters:
        category: Optional filter (e.g., 'soil', 'slope', 'earth pressure', 'aep',
            'heave', 'lagging', 'text').

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
def california_trenching_describe_method(method: str) -> str:
    """
    Returns detailed documentation for a California Trenching and Shoring function.

    Parameters:
        method: The method name (e.g., 'table_2_1_max_allowable_slope',
            'aep_multi_level_cohesionless', 'heave_factor_of_safety').

    Returns:
        JSON string with parameters, types, defaults, and description.
    """
    _, METHOD_INFO = _load_registry()
    if method not in METHOD_INFO:
        matches = [m for m in METHOD_INFO if method.lower() in m.lower()]
        if matches:
            return json.dumps({"error": f"Unknown '{method}'. Similar: {', '.join(matches[:10])}"})
        return json.dumps({"error": f"Unknown '{method}'. Use california_trenching_list_methods()."})
    return json.dumps(METHOD_INFO[method], default=str)
