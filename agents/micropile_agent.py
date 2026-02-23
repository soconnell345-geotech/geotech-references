"""
Micropile Agent — Foundry-style wrapper for micropile reference text and lookups.

Wraps reference text retrieval, figure lookups, and table lookups from
FHWA-NHI-05-039, Micropile Design & Construction.

Three entry-point functions:
  1. micropile_agent           - Run a micropile function (text retrieval or lookup)
  2. micropile_list_methods    - Browse available functions by category
  3. micropile_describe_method - Get detailed parameter docs for a specific function
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
# Import micropile modules
# ---------------------------------------------------------------------------
from geotech_references import _retrieval
from geotech_references.micropile import figures
from geotech_references.micropile import tables


# ---------------------------------------------------------------------------
# Build METHOD_REGISTRY and METHOD_INFO
# ---------------------------------------------------------------------------
METHOD_REGISTRY = {}
METHOD_INFO = {}

# --- Text retrieval functions (from _retrieval.py) ---


def retrieve_section(section_id: str) -> dict:
    """Retrieve a specific section from the micropile reference by its ID.

    Returns the section dict with title, body, key_points, equations,
    figures, tables, and applicability fields.

    Parameters
    ----------
    section_id : str
        Section identifier (e.g., '5.7.2', '4.4').

    Returns
    -------
    dict
        The section data.
    """
    return _retrieval.retrieve_section("micropile", section_id)


def search_sections(query: str) -> list:
    """Keyword search across all micropile sections.

    Searches section titles, body text, key_points, and applicability.
    Returns matches ranked by relevance (title matches score highest).
    Multiple words are AND-matched.

    Parameters
    ----------
    query : str
        Search query (case-insensitive).

    Returns
    -------
    list of dict
        Matching sections with chapter and chapter_title fields added.
    """
    return _retrieval.search_sections("micropile", query)


def list_chapters() -> list:
    """List all micropile chapters and their section IDs.

    Returns
    -------
    list of dict
        Each dict has chapter, chapter_title, reference_id, and
        sections (list of {section_id, title}).
    """
    return _retrieval.list_chapters("micropile")


def load_chapter(chapter: int) -> dict:
    """Load a full micropile chapter JSON file.

    Parameters
    ----------
    chapter : int
        Chapter number (1-10).

    Returns
    -------
    dict
        Full chapter data including all sections.
    """
    return _retrieval.load_chapter("micropile", chapter)


# Register text retrieval functions
_TEXT_METHODS = {
    "retrieve_section": retrieve_section,
    "search_sections": search_sections,
    "list_chapters": list_chapters,
    "load_chapter": load_chapter,
}

for _name, _func in _TEXT_METHODS.items():
    METHOD_REGISTRY[_name] = _func

# --- Figure and table lookup functions ---
_LOOKUP_MODULES = [
    (figures, "figures", "FHWA-NHI-05-039, Micropile Figures"),
    (tables, "tables", "FHWA-NHI-05-039, Micropile Tables"),
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


# Text retrieval methods
for _name, _func in _TEXT_METHODS.items():
    METHOD_INFO[_name] = _extract_info(
        _func, "Text Retrieval", "FHWA-NHI-05-039"
    )

# Figure and table lookup methods
for _mod, _category_prefix, _ref in _LOOKUP_MODULES:
    for _name, _func in inspect.getmembers(_mod, inspect.isfunction):
        if _name.startswith("_"):
            continue
        cat = f"Micropile {_category_prefix.title()}"
        METHOD_INFO[_name] = _extract_info(_func, cat, _ref)


# ---------------------------------------------------------------------------
# Foundry functions
# ---------------------------------------------------------------------------

@function
def micropile_agent(method: str, parameters_json: str) -> str:
    """
    Micropile reference and lookup tool.

    Provides access to FHWA-NHI-05-039 micropile reference text and
    design table/figure lookups. Capabilities include:

    - Reference text retrieval (sections, search, chapter listing)
    - Grout-to-ground bond stress (alpha_bond) by soil/rock type & micropile type
    - Pipe casing properties (API N-80, ASTM A519/A106)
    - Reinforcing bar properties (ASTM A615/A706)
    - Elastic modulus by soil type or SPT N-value
    - Group efficiency factors for cohesive soils
    - Lateral loading parameters (epsilon_50, soil modulus k)
    - Fixity guidance for micropile-to-footing connections
    - Corrosion potential criteria
    - Micropile classification (Type A/B/C/D, subtypes 1-3)
    - Limiting lateral modulus for buckling evaluation

    Parameters:
        method: The function name. Use micropile_list_methods() to browse.
        parameters_json: JSON string of parameters. Use micropile_describe_method()
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
                     "Use micropile_list_methods() to see available methods."
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
def micropile_list_methods(category: str = "") -> str:
    """
    Lists available micropile functions organized by category.

    Parameters:
        category: Optional filter. Partial match on category name
                  (e.g. 'text', 'figures', 'tables', 'bond',
                  'pipe', 'rebar', 'elastic', 'group').

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
def micropile_describe_method(method: str) -> str:
    """
    Returns detailed documentation for a micropile function.

    Parameters:
        method: The method name (e.g. 'table_5_3_alpha_bond',
                'table_4_5_pipe_properties', 'search_sections').

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
                     "Use micropile_list_methods() to browse."
        })
    return json.dumps(METHOD_INFO[method], default=str)
