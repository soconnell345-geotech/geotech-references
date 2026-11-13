"""What a lookup's result is: the unit of every number, its printed page,
and exact conversions for an SI caller of a US-unit lookup (REF-78, REF-77).

The result convention
---------------------
A lookup that returns a dict (or a list of row dicts: each row) carries:

- ``units``: ``{key: unit}`` for every key that holds a number anywhere in
  the result (a nested dict or a list of rows is keyed by its own key
  names). The unit is the one the print gives. ``"dimensionless"`` is used
  only where the print calls the number a factor, ratio or coefficient;
  a number the print gives no unit for says ``"no unit printed"``; a
  percentage says ``"percent"`` and a fraction ``"fraction"``; a count of
  things says ``"count"``; a number from an equation the print states for
  any consistent set of units says ``"consistent units"`` (it is in the
  units the caller gave). A note in brackets may follow a unit
  (``"ft (or m)"``). The map is empty when the result holds no number.
- ``printed_page``: the page label as the document prints it (a string,
  e.g. ``"II-32"``, ``"5-54"``, ``"27"``).
- ``pdf_page_index``: where that page is in the PDF, counted from 0 as the
  table and figure catalogs count (a PDF viewer shows page
  ``pdf_page_index + 1``); a list where the item spans pages. No other
  name is used for a PDF position.

A lookup that returns a bare number, tuple or bool keeps that type; its
docstring carries the label instead (the Returns entry names the quantity
with its unit in square brackets in its first sentence, and the References
section gives ``printed p. X (pdf_page_index N)``). A tuple names each
element as its own Returns entry, each with its unit in brackets. A text or
true/false result needs no unit, only the page. Both are written where the
app reads them: the first sentence of the Returns text (at most 200
characters) and the first 160 characters of the References text.

:func:`labelled` adds ``units`` and the page keys to a dict result, so a
lookup states them once, beside its ``def``, for every way it returns.

SI callers of US-unit lookups
-----------------------------
A US-unit lookup whose formula or chart is tied to its units, and which an
SI number could pass unnoticed (a resilient modulus in MPa sits inside the
printed psi range), takes ``unit_system="SI"`` through ``labelled(si=...)``:
each named input is converted from the stated SI unit to the printed US
unit by the exact factors below, the printed equation runs unchanged, and
the result keeps its printed units (its ``units`` map says which); a dict
result records each conversion under ``converted_inputs``. The default,
``unit_system="US"``, is unchanged behaviour.

Exact factors: the international inch (0.0254 m) and foot (0.3048 m), the
avoirdupois pound (0.45359237 kg) and standard gravity (9.80665 m/s^2),
so a pound-force is 4.4482216152605 N.
"""

import functools
import inspect
import numbers
import re

# ---------------------------------------------------------------------------
# Exact definitions
# ---------------------------------------------------------------------------

IN_M = 0.0254
FT_M = 0.3048
LB_KG = 0.45359237
G_N = 9.80665
LBF_N = LB_KG * G_N                      # 4.4482216152605 N
PSI_PA = LBF_N / IN_M ** 2               # 6894.757293168361 Pa
PSF_PA = LBF_N / FT_M ** 2               # 47.880258980335840 Pa
PCF_N_PER_M3 = LBF_N / FT_M ** 3         # 157.08746384... N/m^3
PCI_PA_PER_M = PSI_PA / IN_M             # 271447.14... Pa/m (lb/in^3)

#: (SI unit, US unit) -> (multiplier, divisor): ``us = si * multiplier /
#: divisor``, the SI value taken to base units and divided by the US unit's
#: exact size in them (kept apart so 25.4 mm gives 1.0 in exactly).
_SI_TO_US = {
    ("MPa", "psi"): (1.0e6, PSI_PA),
    ("kPa", "psi"): (1.0e3, PSI_PA),
    ("MPa", "ksi"): (1.0e6, 1000.0 * PSI_PA),
    ("kPa", "psf"): (1.0e3, PSF_PA),
    ("kPa", "ksf"): (1.0e3, 1000.0 * PSF_PA),
    ("kPa", "tsf"): (1.0e3, 2000.0 * PSF_PA),
    ("MPa/m", "pci"): (1.0e6, PCI_PA_PER_M),
    ("MPa/m", "psi/in"): (1.0e6, PCI_PA_PER_M),
    ("kN/m^3", "pcf"): (1.0e3, PCF_N_PER_M3),
    ("mm", "in"): (1.0e-3, IN_M),
    ("m", "in"): (1.0, IN_M),
    ("m", "ft"): (1.0, FT_M),
    ("mm", "ft"): (1.0e-3, FT_M),
    ("kN", "kips"): (1.0e3, 1000.0 * LBF_N),
    ("kN", "lb"): (1.0e3, LBF_N),
    ("N", "lb"): (1.0, LBF_N),
    ("kg", "lb"): (1.0, LB_KG),
    # kg to lb: 1 lb = 0.45359237 kg exactly.
    # mm^4/m to in^4/ft: 1 in = 25.4 mm and 1 ft = 0.3048 m exactly, so
    # 1 in^4/ft = 25.4^4 mm^4 / 0.3048 m = 416231.4256 mm^4 / 0.3048 m
    # = 1365588.67 mm^4/m; in base units (m^4/m), 1 mm^4/m = 1e-12 and
    # 1 in^4/ft = IN_M**4 / FT_M, so us = si * 1e-12 / (IN_M**4 / FT_M).
    ("mm^4/m", "in^4/ft"): (1.0e-12, IN_M ** 4 / FT_M),
    ("kN-m", "kip-in"): (1.0e3, 1000.0 * LBF_N * IN_M),
    ("mm^2", "in^2"): (1.0e-6, IN_M ** 2),
    ("m^3/m", "ft^3/ft"): (1.0, FT_M ** 2),
    ("degC-days", "degF-days"): (1.8, 1.0),
}

#: What a ``units`` value may say beyond a unit symbol.
WORDS = ("dimensionless", "no unit printed", "percent", "fraction",
         "count", "consistent units")

#: Unit symbols a ``units`` value is built from (joined by "/", "-", "*",
#: "^" or a space; a note in brackets may follow).
SYMBOLS = frozenset("""
in in. inch inches ft feet yd mi mile miles mm cm m km
psi ksi psf ksf tsf pci pcf pcy lb lbs lbf kip kips ton tons
N kN MN Pa kPa MPa GPa kg g Mg t
s sec min hr h day days yr year years
deg degF degC rad radian radians F C degree degrees
gal gpm cfs L mL ml ppm ohm um mil mils blows bpf
ESAL ESALs 18-kip
""".split())


def _is_number_text(text) -> bool:
    try:
        float(text)
    except (TypeError, ValueError):
        return False
    return True


def from_si(value, si_unit, us_unit):
    """``value`` in ``si_unit`` converted exactly to ``us_unit``.

    ``degC`` to ``degF`` is affine (F = 1.8 C + 32); every other pair is a
    factor from :data:`_SI_TO_US`. A list or tuple is converted item by
    item (a list comes back)."""
    if isinstance(value, (list, tuple)):
        return [from_si(v, si_unit, us_unit) for v in value]
    if (si_unit, us_unit) == ("degC", "degF"):
        return 1.8 * float(value) + 32.0
    try:
        mult, div = _SI_TO_US[(si_unit, us_unit)]
    except KeyError:
        raise ValueError(
            f"no exact conversion from {si_unit} to {us_unit}") from None
    return float(value) * mult / div


def is_unit(text) -> bool:
    """Whether ``text`` names a unit by this convention: one of
    :data:`WORDS`, or unit symbols (:data:`SYMBOLS`) joined by "/", "-",
    "*", "^" or spaces, optionally followed by a note in brackets."""
    if not isinstance(text, str) or not text.strip():
        return False
    head = text.split(" (")[0].strip()
    if head in WORDS:
        return True
    for sep in ("/", "*", "^", "-", "·"):
        head = head.replace(sep, " ")
    tokens = [t for t in head.split() if t]
    return (bool(tokens) and any(t in SYMBOLS for t in tokens)
            and all(t in SYMBOLS or _is_number_text(t) for t in tokens))


def numeric_keys(result) -> set:
    """The key names that hold a number (not a bool) anywhere in
    ``result``; ``units`` itself and ``pdf_page_index`` are left out. A
    list of numbers counts under the key that holds it, and so does a dict
    keyed by numbers (a curve keyed by its parameter's value)."""
    found: set = set()

    def walk(obj, key=None):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("units", "pdf_page_index", "converted_inputs"):
                    continue
                named = isinstance(k, str) and not _is_number_text(k)
                walk(v, k if named else key)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                walk(v, key)
        elif isinstance(obj, numbers.Number) and not isinstance(obj, bool):
            if key is not None:
                found.add(key)

    walk(result)
    return found


_LABEL = r"[^,;()\[\]]+?"
_PAGE_FWD = re.compile(
    r"pdf_page_index\s+(\d+)(?:\s*[-–]\s*(\d+))?\s*[,;]\s*printed\s+"
    r"(?:pp?\.\s*)?(" + _LABEL + r")\s*(?=[,;()\[\]]|$)")
_PAGE_REV = re.compile(
    r"printed\s+(?:pp?\.\s*)?(" + _LABEL + r")\s*[,;]?\s*\(?pdf_page_index\s+"
    r"(\d+)(?:\s*[-–]\s*(\d+))?")


def page_from_reference(reference):
    """``(printed_page, pdf_page_index)`` read from a reference string that
    cites ``pdf_page_index N, printed X`` (either order; ``N-M`` gives the
    list of every page), or ``(None, None)``. The first citation wins."""
    if not isinstance(reference, str):
        return None, None
    found = []
    m = _PAGE_FWD.search(reference)
    if m:
        found.append((m.start(), m.group(3).strip(), int(m.group(1)),
                      m.group(2)))
    m = _PAGE_REV.search(reference)
    if m:
        found.append((m.start(), m.group(1).strip(), int(m.group(2)),
                      m.group(3)))
    if not found:
        return None, None
    _, printed, first, last = min(found)
    if last is None:
        return printed, first
    return printed, list(range(first, int(last) + 1))


_PRINTED_ONLY = re.compile(
    r"(?:printed\s+)?\bpp?\.\s*(" + _LABEL + r")\s*(?=[,;()\[\]]|$)")


def printed_from_reference(reference):
    """The printed page a reference cites as ``p. X`` (or ``printed p. X``)
    with no pdf_page_index beside it, or None: used only for a result whose
    body already gives its pdf_page_index."""
    if not isinstance(reference, str):
        return None
    m = _PRINTED_ONLY.search(reference)
    return m.group(1).strip() if m else None


def _check_unit_system(unit_system):
    if unit_system not in ("US", "SI"):
        raise ValueError(
            f"unit_system must be 'US' (the printed units, the default) or "
            f"'SI', got {unit_system!r}")
    return unit_system


def _split_path(name):
    """``"p"`` -> (p, None, None); ``"p.k"`` -> (p, "dict", k); ``"p[].k"``
    -> (p, "list", k): a key inside a dict argument or inside each dict of
    a list argument."""
    if "[]." in name:
        param, key = name.split("[].", 1)
        return param, "list", key
    if "." in name:
        param, key = name.split(".", 1)
        return param, "dict", key
    return name, None, None


def _convert(bound, name, si_unit, us_unit):
    """Convert one ``si`` entry in ``bound`` (copying what it changes);
    ``(given, used)`` or None when the argument is absent or None."""
    param, kind, key = _split_path(name)
    val = bound.arguments.get(param)
    if val is None:
        return None
    if kind is None:
        used = from_si(val, si_unit, us_unit)
        bound.arguments[param] = used
        return val, used
    if kind == "dict":
        if not isinstance(val, dict) or val.get(key) is None:
            return None
        new = dict(val)
        new[key] = from_si(val[key], si_unit, us_unit)
        bound.arguments[param] = new
        return val[key], new[key]
    if not isinstance(val, (list, tuple)):
        return None
    items, given, used = list(val), [], []
    for i, item in enumerate(items):
        if isinstance(item, dict) and item.get(key) is not None:
            new = dict(item)
            new[key] = from_si(item[key], si_unit, us_unit)
            items[i] = new
            given.append(item[key])
            used.append(new[key])
    if not given:
        return None
    bound.arguments[param] = items
    return given, used


def labelled(units, *, printed_page=None, pdf_page_index=None, si=None,
             si_fixed=None):
    """Decorate a lookup that returns a dict (or a list of row dicts, each
    labelled the same way) so its result says what each number is and
    where it is printed.

    Parameters
    ----------
    units : dict
        ``{key: unit}`` for every key that can hold a number in the
        result (see the module docstring for the words). Only the keys a
        result holds are copied into it; a ``units`` dict the function
        returns itself wins for its own keys.
    printed_page : str, optional
        The page label as printed; added when the result has none.
    pdf_page_index : int or list of int, optional
        The 0-based PDF page index; added when the result has none.
    si : dict, optional
        ``{parameter: (si_unit, us_unit)}``: the lookup takes
        ``unit_system="US"`` (default) or ``"SI"``; with ``"SI"`` each named
        parameter is converted from ``si_unit`` to the printed ``us_unit``
        before the function runs (:func:`from_si`), and a dict result gets
        ``unit_system`` and ``converted_inputs``. The result keeps its
        printed units. ``"p.k"`` names key ``k`` of a dict argument ``p``
        and ``"p[].k"`` key ``k`` of each dict in a list argument ``p``.
    si_fixed : dict, optional
        ``{parameter: value}`` that ``unit_system="SI"`` requires (a lookup
        with its own unit selector converts to one of its units only).

    The wrapper keeps the function's name, docstring and source (so
    ``inspect.getsource`` and ``inspect.signature`` read the function), and
    adds ``unit_system`` to the signature when ``si`` is given.
    """
    units = dict(units)
    for k, v in units.items():
        if not is_unit(v):
            raise ValueError(f"units[{k!r}] = {v!r} is not a unit by the "
                             f"convention (geotech_references._units)")
    si = dict(si or {})
    si_fixed = dict(si_fixed or {})
    for name, pair in si.items():
        if (tuple(pair) not in _SI_TO_US
                and tuple(pair) != ("degC", "degF")):
            raise ValueError(f"no exact conversion for {name}: {pair}")

    def deco(func):
        sig = inspect.signature(func)
        if si:
            missing = [p for p in list(si) + list(si_fixed)
                       if _split_path(p)[0] not in sig.parameters]
            if missing:
                raise TypeError(f"{func.__name__} has no parameter "
                                f"{missing} to convert")
            if "unit_system" in sig.parameters:
                raise TypeError(f"{func.__name__} has its own unit_system")

        def label(out, conv):
            if isinstance(out, dict):
                return label_one(out, conv)
            if (isinstance(out, (list, tuple)) and out
                    and all(isinstance(row, dict) for row in out)):
                # a list of rows: each row is labelled as a dict result
                return type(out)(label_one(row, conv) for row in out)
            return out

        def label_one(out, conv):
            out = dict(out)     # never write into a table the module holds
            have = numeric_keys(out)
            mine = {k: v for k, v in units.items() if k in have}
            given = out.get("units")
            if isinstance(given, dict):
                mine.update(given)
            out["units"] = mine     # empty when nothing holds a number
            if "printed_page" not in out or "pdf_page_index" not in out:
                cited = out.get("reference") or out.get("source")
                ref_printed, ref_index = page_from_reference(cited)
                if ref_index is None and "pdf_page_index" in out:
                    ref_printed = printed_from_reference(cited)
                if ref_index is None and ref_printed is None:
                    ref_printed, ref_index = printed_page, pdf_page_index
                if ref_printed is not None and "printed_page" not in out:
                    out["printed_page"] = ref_printed
                if ref_index is not None and "pdf_page_index" not in out:
                    out["pdf_page_index"] = ref_index
            if conv is not None:
                out["unit_system"] = "SI"
                out["converted_inputs"] = conv
            return out

        if not si:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return label(func(*args, **kwargs), None)
            wrapper.__result_units__ = units
            return wrapper

        @functools.wraps(func)
        def wrapper(*args, unit_system="US", **kwargs):
            if _check_unit_system(unit_system) == "US":
                return label(func(*args, **kwargs), None)
            bound = sig.bind(*args, **kwargs)
            for name, value in si_fixed.items():
                have = bound.arguments.get(name, sig.parameters[name].default)
                if have != value:
                    raise ValueError(
                        f"with unit_system='SI' leave {name} at {value!r} "
                        f"(the SI inputs are converted to it), got {have!r}")
            conv = {}
            for name, (si_unit, us_unit) in si.items():
                done = _convert(bound, name, si_unit, us_unit)
                if done is not None:
                    conv[name] = {"given": done[0], "given_unit": si_unit,
                                  "used": done[1], "used_unit": us_unit}
            return label(func(*bound.args, **bound.kwargs), conv)

        params = list(sig.parameters.values())
        extra = inspect.Parameter("unit_system", inspect.Parameter.KEYWORD_ONLY,
                                  default="US", annotation=str)
        if params and params[-1].kind is inspect.Parameter.VAR_KEYWORD:
            params.insert(len(params) - 1, extra)
        else:
            params.append(extra)
        wrapper.__signature__ = sig.replace(parameters=params)
        wrapper.__result_units__ = units
        wrapper.__si_inputs__ = si
        return wrapper

    return deco
