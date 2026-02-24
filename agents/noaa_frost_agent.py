"""
NOAA Frost Agent — Foundry-style wrapper for NOAA frost depth lookups.

Wraps frost depth equations and soil thermal property tables for
frost-protected shallow foundation design.

Three entry-point functions:
  1. noaa_frost_agent           - Run a NOAA frost function
  2. noaa_frost_list_methods    - Browse available functions by category
  3. noaa_frost_describe_method - Get detailed parameter docs for a specific function
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
# Import NOAA frost modules
# ---------------------------------------------------------------------------
from geotech_references.noaa_frost import equations
from geotech_references.noaa_frost import tables


# ---------------------------------------------------------------------------
# Build METHOD_REGISTRY and METHOD_INFO
# ---------------------------------------------------------------------------
METHOD_REGISTRY = {}
METHOD_INFO = {}

# --- Equation and table lookup functions ---
_LOOKUP_MODULES = [
    (equations, "equations", "Stefan/Berggren frost depth equations"),
    (tables, "tables", "Kersten/Farouki soil thermal properties"),
]

for _mod, _category_prefix, _ref in _LOOKUP_MODULES:
    for _name, _func in inspect.getmembers(_mod, inspect.isfunction):
        if _name.startswith("_"):
            continue
        METHOD_REGISTRY[_name] = _func


# ---------------------------------------------------------------------------
# Build METHOD_INFO with parameter details
# ---------------------------------------------------------------------------

def _param_type_str(annotation) -> str:
    """Convert a type annotation to a human-readable string."""
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
    """Extract METHOD_INFO entry from a function's docstring and signature."""
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


# Equation and table methods
for _mod, _category_prefix, _ref in _LOOKUP_MODULES:
    for _name, _func in inspect.getmembers(_mod, inspect.isfunction):
        if _name.startswith("_"):
            continue
        cat = f"NOAA Frost {_category_prefix.title()}"
        METHOD_INFO[_name] = _extract_info(_func, cat, _ref)


# ---------------------------------------------------------------------------
# Foundry functions
# ---------------------------------------------------------------------------

@function
def noaa_frost_agent(method: str, parameters_json: str) -> str:
    """
    NOAA frost depth estimation and soil thermal properties tool.

    Provides access to frost depth equations and soil thermal property
    tables for frost-protected shallow foundation design. Capabilities:

    - Stefan equation for frost penetration depth
    - Modified Berggren method with correction factors
    - Berggren lambda dimensionless correction factor
    - Soil latent heat from density and moisture content
    - Simplified frost depth by soil type
    - Soil thermal conductivity (frozen/unfrozen) by soil type
    - Surface n-factor for air-to-surface freezing index conversion
    - Volumetric heat capacity by soil type
    - Combined thermal properties lookup

    Parameters:
        method: The function name. Use noaa_frost_list_methods() to browse.
        parameters_json: JSON string of parameters. Use noaa_frost_describe_method()
                        for details.

    Returns:
        JSON string with the result or an error message.
    """
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
                     "Use noaa_frost_list_methods() to see available methods."
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
def noaa_frost_list_methods(category: str = "") -> str:
    """
    Lists available NOAA frost functions organized by category.

    Parameters:
        category: Optional filter. Partial match on category name
                  (e.g. 'equations', 'tables', 'stefan', 'thermal',
                  'conductivity', 'frost').

    Returns:
        JSON string with method names grouped by category.
    """
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
def noaa_frost_describe_method(method: str) -> str:
    """
    Returns detailed documentation for a NOAA frost function.

    Parameters:
        method: The method name (e.g. 'stefan_frost_depth_m',
                'table_soil_thermal_conductivity', 'berggren_lambda').

    Returns:
        JSON string with parameters, types, defaults, and description.
    """
    if method not in METHOD_INFO:
        matches = [m for m in METHOD_INFO if method.lower() in m.lower()]
        if matches:
            suggestion = ", ".join(matches[:10])
            return json.dumps({
                "error": f"Unknown method '{method}'. Similar: {suggestion}"
            })
        return json.dumps({
            "error": f"Unknown method '{method}'. "
                     "Use noaa_frost_list_methods() to browse."
        })
    return json.dumps(METHOD_INFO[method], default=str)
