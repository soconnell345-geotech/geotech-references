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


# ---------------------------------------------------------------------------
# The app's reading of a docstring: what its agent is shown beside a bare
# result (GeotechStaffEngineer funhouse_agent/adapters/_reference_common.py,
# result_label and the parsers under it, copied 2026-11-13). The label is
# only seen if it is inside these limits.
# ---------------------------------------------------------------------------

APP_RETURNS_CHARS = 200
APP_REFERENCE_CHARS = 160
_APP_SECTIONS = {
    "parameters": "parameters", "args": "parameters",
    "arguments": "parameters", "other parameters": "parameters",
    "returns": "returns", "return": "returns", "yields": "returns",
    "raises": "raises", "notes": "notes", "note": "notes",
    "references": "references", "reference": "references",
    "examples": "examples", "example": "examples",
}
_DASHES = re.compile(r"-{3,}")
_ENTRY_NAMES = re.compile(r"\*{0,2}[A-Za-z_]\w*(\s*,\s*\*{0,2}[A-Za-z_]\w*)*")
_PAGE_CITED = re.compile(r"printed pp?\. ?[^\s(]+ \(pdf_page_index \d+")


def app_sections(doc):
    lines = doc.split("\n")
    out = {"": []}
    current = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        key = stripped.rstrip(":").strip().lower()
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        underlined = bool(_DASHES.fullmatch(nxt))
        if key in _APP_SECTIONS and not line[:1].isspace() and (
                underlined or stripped.endswith(":")
                or (i > 0 and not lines[i - 1].strip())):
            current = _APP_SECTIONS[key]
            out.setdefault(current, [])
            i += 2 if underlined else 1
            continue
        out.setdefault(current, []).append(line)
        i += 1
    return out


def app_entries(lines):
    lines = list(lines or [])
    entries = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if not line[:1].isspace():
            head, sep, typ = stripped.partition(" : ")
            if sep:
                names = [n.strip().lstrip("*") for n in head.split(",")
                         if n.strip()]
                entries.append([names, typ.strip(), []])
                continue
            nxt = next((n for n in lines[i + 1:] if n.strip()), "")
            alone = not nxt and not entries and len(stripped) <= 60 \
                and not stripped.endswith(".")
            if nxt[:1].isspace() or alone or _ENTRY_NAMES.fullmatch(stripped):
                entries.append([[], stripped, []])
                continue
        if entries:
            entries[-1][2].append(stripped)
        else:
            entries.append([[], "", [stripped]])
    return [(names, head, " ".join(desc)) for names, head, desc in entries]


def _app_trim(text, limit):
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[:limit - 3].rstrip() + "..."


def app_first_sentence(text, limit=APP_RETURNS_CHARS):
    text = " ".join(str(text or "").split())
    m = re.search(r"(?<=[\w)]\.)\s+(?=[A-Z(])", text[20:])
    if m:
        text = text[:20 + m.start()]
    return _app_trim(text, limit)


def app_returns(func):
    """``text`` (the Returns text as the app shows it: its first sentence,
    at most 200 characters), ``entries`` and ``elements`` (a tuple's
    element names)."""
    entries = app_entries(app_sections(inspect.getdoc(func) or "")
                          .get("returns"))
    named = [e for e in entries if e[0]]
    if len(named) > 1:
        text = "; ".join(f"{', '.join(n)} ({t}): {d}".replace(
            " (): ", ": ").rstrip(": ") for n, t, d in named)
        elements = [n for names, _t, _d in named for n in names]
    else:
        text = " ".join(d for _n, _t, d in entries if d)
        if len(named) == 1:
            text = f"{', '.join(named[0][0])}: {text}" if text else \
                ", ".join(named[0][0])
        elements = []
    return {"text": app_first_sentence(text), "entries": named or entries,
            "elements": elements}


def app_reference(func):
    """The References text as the app shows it (its first 160
    characters)."""
    lines = app_sections(inspect.getdoc(func) or "").get("references") or []
    return _app_trim(" ".join(" ".join(lines).split()), APP_REFERENCE_CHARS)


def _unit_in(text):
    """The first text in square brackets that names a unit, or None."""
    for m in re.finditer(r"\[([^\]]+)\]", text or ""):
        if _units.is_unit(m.group(1)):
            return m.group(1)
    return None


def bare_docstring_problems(func, kind="number"):
    """What a lookup returning a bare value lacks in its docstring, as the
    app reads it. ``kind``: "number" (the unit in brackets in the first
    sentence of the Returns text), "tuple" (each element its own named
    entry, each entry's unit in brackets, all inside the text the app
    shows) or "text" (a string or true/false: no unit)."""
    problems = []
    ret = app_returns(func)
    if kind == "number" and not _unit_in(ret["text"]):
        problems.append(f"Returns' first sentence names no [unit]: "
                        f"{ret['text']!r}")
    if kind == "tuple":
        if len(ret["elements"]) < 2:
            problems.append("Returns does not name each element")
        for names, _t, desc in ret["entries"]:
            unit = _unit_in(app_first_sentence(desc))
            if not unit:
                problems.append(f"Returns entry {names} names no [unit]")
            elif f"[{unit}]" not in ret["text"]:
                problems.append(f"Returns entry {names}'s unit is past the "
                                f"{APP_RETURNS_CHARS} characters the app shows")
    if not _PAGE_CITED.search(app_reference(func)):
        problems.append("References gives no 'printed p. X (pdf_page_index "
                        "N)' in its first 160 characters")
    return problems
