"""The result convention every lookup keeps (REF-78; geotech_references._units):
checks shared by the convention tests of each wave.

A dict result carries ``units`` (a unit for every key that holds a number),
``printed_page`` and ``pdf_page_index``; a bare number keeps its type and its
docstring labels it (the Returns entry gives the unit in square brackets in
its first sentence, the References section the printed page and the
pdf_page_index). The docstring reading mirrors the app's (the first sentence
of the Returns text is what its agent is shown).
"""

import importlib
import inspect
import pkgutil
import re

from geotech_references import _units


def lookups(packages):
    """``{"pkg.module.name": function}`` for every public function defined in
    the public modules of ``packages``."""
    found = {}
    for pkg in packages:
        mod = importlib.import_module(f"geotech_references.{pkg}")
        for info in pkgutil.iter_modules(mod.__path__):
            if info.name.startswith("_"):
                continue
            m = importlib.import_module(f"geotech_references.{pkg}.{info.name}")
            for name, func in inspect.getmembers(m, inspect.isfunction):
                if name.startswith("_") or func.__module__ != m.__name__:
                    continue
                found[f"{pkg}.{info.name}.{name}"] = func
    return found


def section(doc, title):
    """The text of a numpy-style docstring section, or ''."""
    m = re.search(rf"^{title}\n-+\n(.*?)(?=^\S[^\n]*\n-+\n|\Z)", doc, re.S | re.M)
    return m.group(1) if m else ""


def returns_first_sentence(func):
    """The first sentence of the Returns text after its type line, as the
    app shows it."""
    text = section(inspect.getdoc(func) or "", "Returns")
    lines = [ln.strip() for ln in text.strip().split("\n")]
    body = " ".join(lines[1:]) if len(lines) > 1 else ""
    return re.split(r"(?<=[.;])\s", body, maxsplit=1)[0]


def bare_docstring_problems(func):
    """What a lookup returning a bare value lacks in its docstring."""
    problems = []
    first = returns_first_sentence(func)
    m = re.search(r"\[([^\]]+)\]", first)
    if not m or not _units.is_unit(m.group(1)):
        problems.append(f"Returns' first sentence names no [unit]: {first!r}")
    refs = section(inspect.getdoc(func) or "", "References")
    if not re.search(r"printed p(p)?\. ?\S+ \(pdf_page_index \d+", refs):
        problems.append("References gives no 'printed p. X (pdf_page_index N)'")
    return problems


def dict_result_problems(result):
    """What a dict result lacks by the convention."""
    problems = []
    units = result.get("units")
    if not isinstance(units, dict):
        return [f"units is {type(units).__name__}, not a dict"]
    for key in sorted(_units.numeric_keys(result)):
        if key not in units:
            problems.append(f"no unit for {key!r}")
    for key, unit in units.items():
        if not _units.is_unit(unit):
            problems.append(f"units[{key!r}] = {unit!r} is not a unit")
    printed = result.get("printed_page")
    if not isinstance(printed, str) or not printed.strip():
        problems.append(f"printed_page is {printed!r}")
    index = result.get("pdf_page_index")
    ok = (isinstance(index, int) and not isinstance(index, bool) and index >= 0
          or isinstance(index, list) and index
          and all(isinstance(i, int) and i >= 0 for i in index))
    if not ok:
        problems.append(f"pdf_page_index is {index!r}")
    if "pdf_page" in result:
        problems.append("carries pdf_page (now pdf_page_index)")
    ref_printed, ref_index = _units.page_from_reference(result.get("reference"))
    if ref_index is not None and ok:
        first = index[0] if isinstance(index, list) else index
        ref_first = ref_index[0] if isinstance(ref_index, list) else ref_index
        if first != ref_first:
            problems.append(f"pdf_page_index {index!r} but the reference "
                            f"cites {ref_index!r}")
    return problems


def signature_names(func):
    """The parameter names a caller sees (the labelled wrapper's own
    signature, ``unit_system`` included)."""
    return set(inspect.signature(func).parameters)
