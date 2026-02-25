"""
UFC Expansive Soils Agent — Foundry-style wrapper for UFC 3-220-07 lookups.

Wraps swell potential classification, free swell and swell pressure
estimation, heave prediction, active zone depth, foundation selection,
and pier design for expansive soils.

Three entry-point functions:
  1. ufc_expansive_agent           - Run a UFC 3-220-07 function
  2. ufc_expansive_list_methods    - Browse available functions by category
  3. ufc_expansive_describe_method - Get detailed parameter docs for a specific function

## FOUNDRY SETUP
Requires: `pip install geotech-references`
Import: `from agents.ufc_expansive_agent import ufc_expansive_agent, ufc_expansive_list_methods, ufc_expansive_describe_method`
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
# Lazy registry — defers geotech_references imports until first call
# ---------------------------------------------------------------------------
_METHOD_REGISTRY = None
_METHOD_INFO = None


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


def _extract_info(func, category: str, reference: str) -> dict:
    doc = inspect.getdoc(func) or ""
    desc_lines = []
    for line in doc.split("\n"):
        if line.strip() == "":
            break
        desc_lines.append(line.strip())
    brief = " ".join(desc_lines) if desc_lines else "No description available."

    param_descs = {}
    doc_lines = doc.split("\n")
    in_params = False
    current_param = None
    for dline in doc_lines:
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

    ret_ann = sig.return_annotation
    info = {
        "category": category,
        "brief": brief,
        "reference": reference,
        "parameters": params,
    }
    if ret_ann is not inspect.Parameter.empty:
        info["returns"] = _param_type_str(ret_ann)
    return info


def _load_registry():
    """Lazily import geotech_references and build registries on first call."""
    global _METHOD_REGISTRY, _METHOD_INFO
    if _METHOD_REGISTRY is not None:
        return _METHOD_REGISTRY, _METHOD_INFO

    from geotech_references.ufc_expansive import equations
    from geotech_references.ufc_expansive import tables

    _METHOD_REGISTRY = {}
    _METHOD_INFO = {}

    _lookup_modules = [
        (equations, "equations", "UFC 3-220-07 expansive soil equations"),
        (tables, "tables", "UFC 3-220-07 expansive soil classification and design tables"),
    ]

    for _mod, _category_prefix, _ref in _lookup_modules:
        for _name, _func in inspect.getmembers(_mod, inspect.isfunction):
            if _name.startswith("_"):
                continue
            _METHOD_REGISTRY[_name] = _func
            cat = f"UFC Expansive {_category_prefix.title()}"
            _METHOD_INFO[_name] = _extract_info(_func, cat, _ref)

    return _METHOD_REGISTRY, _METHOD_INFO


@function
def ufc_expansive_agent(method: str, parameters_json: str) -> str:
    """
    UFC 3-220-07 Foundations in Expansive Soils tool.

    Provides swell potential classification, activity index, free swell
    estimation, swell pressure, heave prediction (layer summation),
    active zone depth by climate, foundation type selection, grade beam
    void space, and pier minimum embedment depth.

    Parameters:
        method: The function name. Use ufc_expansive_list_methods() to browse.
        parameters_json: JSON string of parameters.

    Returns:
        JSON string with the result or an error message.
    """
    METHOD_REGISTRY, METHOD_INFO = _load_registry()
    try:
        parameters = json.loads(parameters_json)
    except (json.JSONDecodeError, TypeError) as e:
        return json.dumps({"error": f"Invalid parameters_json: {str(e)}"})

    if method not in METHOD_REGISTRY:
        matches = [m for m in METHOD_REGISTRY if method.lower() in m.lower()]
        if matches:
            suggestion = ", ".join(matches[:5])
            return json.dumps({
                "error": f"Unknown method '{method}'. Did you mean: {suggestion}?"
            })
        return json.dumps({
            "error": f"Unknown method '{method}'. "
                     "Use ufc_expansive_list_methods() to see available methods."
        })

    try:
        func = METHOD_REGISTRY[method]
        result = func(**parameters)
        if isinstance(result, dict):
            return json.dumps(result, default=str)
        elif isinstance(result, (list, tuple)):
            return json.dumps({"result": result}, default=str)
        else:
            return json.dumps({"result": result}, default=str)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {str(e)}"})


@function
def ufc_expansive_list_methods(category: str = "") -> str:
    """
    Lists available UFC 3-220-07 expansive soil functions by category.

    Parameters:
        category: Optional filter (e.g. 'swell', 'heave', 'foundation', 'pier').

    Returns:
        JSON string with method names grouped by category.
    """
    METHOD_REGISTRY, METHOD_INFO = _load_registry()
    result = {}
    for method_name, info in METHOD_INFO.items():
        cat = info["category"]
        if category and category.lower() not in cat.lower():
            if (category.lower() not in method_name.lower() and
                    category.lower() not in info.get("brief", "").lower()):
                continue
        if cat not in result:
            result[cat] = {}
        result[cat][method_name] = info["brief"]
    return json.dumps(result)


@function
def ufc_expansive_describe_method(method: str) -> str:
    """
    Returns detailed documentation for a UFC 3-220-07 expansive soil function.

    Parameters:
        method: The method name (e.g. 'free_swell_percent',
                'table_swell_potential_classification').

    Returns:
        JSON string with parameters, types, defaults, and description.
    """
    METHOD_REGISTRY, METHOD_INFO = _load_registry()
    if method not in METHOD_INFO:
        matches = [m for m in METHOD_INFO if method.lower() in m.lower()]
        if matches:
            suggestion = ", ".join(matches[:10])
            return json.dumps({
                "error": f"Unknown method '{method}'. Similar: {suggestion}"
            })
        return json.dumps({
            "error": f"Unknown method '{method}'. "
                     "Use ufc_expansive_list_methods() to browse."
        })
    return json.dumps(METHOD_INFO[method], default=str)
