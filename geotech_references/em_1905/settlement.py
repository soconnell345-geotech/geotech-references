"""EM 1110-1-1905 (2025) equations of Chapter 6 (stress distribution) and
Chapter 7 (settlement) as functions: stresses and overconsolidation, the
induced vertical stress and its influence factors, consolidation settlement
from e-log-p parameters, the dilatometer (constrained modulus), Menard and
Rousseau pressuremeter, Schmertmann CPT and Burland and Burbidge SPT
methods, excavation rebound, time rate and secondary compression. Each is
the formula typed in from the rendered page (manifest
``printed_equations``) and checked against it.

Units are the manual's: tsf, tcf, ft, years or days as each equation says.
Settlements come back in feet and inches: the lists of symbols give some
settlements in inches while the layer thickness is in feet, so both are
given (feet x 12). Each function returns a dict with its values, ``units``,
``source``, ``valid_for`` and ``notes``, and raises ValueError outside what
the equation covers. A limit printed as part of a relation ("C1 >= 0.5")
is applied as printed: the limited value is returned, with the formula's
value beside it (``C1_unlimited``), ``limit_governs`` and a note quoting
the page. An input outside conditions the page prints (sigma'p below
sigma'zo beside Eqs. 7-7 to 7-9, pp. 159-160) is refused, the message
naming the condition and the page. Where a function refuses an input the
page prints no condition on (t below 3 years in Eq. 7-34; a void ratio that
rises in Eqs. 7-5, 7-6 and 7-46; q below sigma'zD in the settlement
equations), the message and docstring say it is the library's reading.
Eqs. 6-5 and 6-6 return a negative net pressure, flagged ``net_negative``
with a note.
"""

from __future__ import annotations

import math

_REF = "EM 1110-1-1905 (2025)"


def _source(obj: str, page) -> str:
    return f"{_REF} {obj}, p. {page}"


def _positive(name: str, value) -> float:
    v = float(value)
    if not v > 0:
        raise ValueError(f"{name} must be > 0 (got {value})")
    return v


def _non_negative(name: str, value) -> float:
    v = float(value)
    if v < 0:
        raise ValueError(f"{name} must be >= 0 (got {value})")
    return v


def _net_negative_note(qn: float, what: str, where: str) -> str:
    """The note for a net pressure q - sigma'zD below zero (Eqs. 6-5 and
    6-6): computed as printed and flagged, not refused."""
    if qn >= 0:
        return ""
    return (f"q - sigma'zD = {qn:.3f} tsf < 0, so {what} is negative: the "
            f"gross bearing pressure q is below the initial vertical effective "
            f"stress at the bearing elevation. {where} defines q as the gross "
            f"bearing pressure and sigma'zD as that stress and prints no sign "
            f"condition; a negative value is a net unloading (for rebound see "
            f"Eqs. 7-35 to 7-40). The functions for Eqs. 7-11, 7-18, 7-24 "
            f"and 7-26 refuse it, and Eq. 7-10 refuses a negative "
            f"delta_sigma_z.")


def _net_refusal(q, sigma_zD, where: str, strict: bool = False) -> float:
    """q - sigma'zD for a settlement equation, refused below zero (at zero
    too when ``strict``, where the equation divides by it): the page prints
    no condition on it, so the message says the refusal is the library's
    reading."""
    qn = _non_negative("q", q) - _non_negative("sigma_zD", sigma_zD)
    if qn < 0 or (strict and qn == 0):
        raise ValueError(
            f"q ({q}) is {'not above' if strict else 'below'} sigma_zD "
            f"({sigma_zD}), so the net pressure q - sigma'zD in {where} would "
            f"be {'zero or ' if strict else ''}negative. The page prints no "
            f"condition on it; the library refuses it (its reading: the "
            f"settlement equations are not written for a net unloading)")
    return qn


def _rheological(name: str, value) -> float:
    """Menard's rheological factor: Table 7-6 (p. 170) prints 1, 2/3, 1/2,
    1/3 and 1/4, so a value outside 1/4 to 1 is refused."""
    v = float(value)
    if not 0.25 <= v <= 1:
        raise ValueError(f"{name} = {value}: Table 7-6 (p. 170) prints "
                         f"rheological factors from 1/4 to 1 (1, 2/3, 1/2, "
                         f"1/3, 1/4)")
    return v


def _settlement(ft: float) -> dict:
    return {"settlement_ft": ft, "settlement_in": ft * 12}


_SETTLEMENT_UNITS = {"settlement_ft": "ft", "settlement_in": "in"}


# ---------------------------------------------------------------------------
# Chapter 6
# ---------------------------------------------------------------------------

def equation_6_1_total_vertical_stress(thicknesses: list,
                                       unit_weights: list) -> dict:
    """Total vertical stress at a depth, the sum of each overlying layer's
    thickness times its total unit weight, sigma_z = sum(z_i gamma_t,i).

    Print check (Eq. 6-1, p. 124, typed in from the rendered page):

        printed    σz = ∑(i=1 to n) zi · γt,i
        here       the same

    Parameters
    ----------
    thicknesses : list of float
        Thickness of each overlying layer, ft.
    unit_weights : list of float
        Total unit weight of each layer, tcf (pcf/2,000), same order.

    Returns
    -------
    dict
        sigma_z, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If the lists differ in length, are empty, or hold a negative value.
    """
    if len(thicknesses) != len(unit_weights) or not thicknesses:
        raise ValueError("give one unit weight per layer thickness")
    s = 0.0
    for z, g in zip(thicknesses, unit_weights):
        s += _non_negative("thickness", z) * _non_negative("unit weight", g)
    return {"sigma_z": s, "units": {"sigma_z": "tsf (with tcf and ft)"},
            "source": _source("Eq. 6-1", 124),
            "valid_for": "Level ground, layers of uniform unit weight.",
            "notes": ""}


def equation_6_2_effective_vertical_stress(sigma_z: float, u: float) -> dict:
    """Initial vertical effective stress, the total vertical stress less the
    pore pressure, sigma'_v = sigma_z - u (u = gamma_w z_w).

    Print check (Eq. 6-2, p. 124, typed in from the rendered page):

        printed    σ′v = σz − u
        here       the same

    Parameters
    ----------
    sigma_z : float
        Initial total vertical stress, tsf.
    u : float
        Pore pressure, tsf.

    Returns
    -------
    dict
        sigma_v_eff, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a stress is negative or u exceeds sigma_z.
    """
    sz = _non_negative("sigma_z", sigma_z)
    uu = _non_negative("u", u)
    if uu > sz:
        raise ValueError("u exceeds sigma_z")
    return {"sigma_v_eff": sz - uu, "units": {"sigma_v_eff": "tsf"},
            "source": _source("Eq. 6-2", 124),
            "valid_for": "Hydrostatic pore pressure (paragraph 6-4c).",
            "notes": "Also written sigma'_zo."}


def equation_6_3_overconsolidation(sigma_p: float, sigma_zo: float) -> dict:
    """Overconsolidation ratio OCR = sigma'_p/sigma'_z (Eq. 6-3) and
    overconsolidation margin sigma'_m = sigma'_p - sigma'_zo (Eq. 6-4).

    Print check (Eqs. 6-3 and 6-4, p. 126, typed in from the rendered page):

        6-3  OCR = σ′p/σ′z
        6-4  σ′m = σ′p − σ′zo
        here the same

    Parameters
    ----------
    sigma_p : float
        Preconsolidation stress, tsf.
    sigma_zo : float
        Current (initial) vertical effective stress, tsf.

    Returns
    -------
    dict
        OCR, margin, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a stress is not positive.
    """
    sp = _positive("sigma_p", sigma_p)
    sz = _positive("sigma_zo", sigma_zo)
    return {"OCR": sp / sz, "margin": sp - sz,
            "units": {"OCR": "dimensionless", "margin": "tsf"},
            "source": _source("Eqs. 6-3 and 6-4", 126),
            "valid_for": "In situ state of stress (paragraph 6-5d).",
            "notes": ("Example C-1 carries sigma'_m with depth and finds "
                      "sigma'_p = sigma'_m + sigma'_zo at each layer (Table "
                      "C-1, Step 4).")}


def equation_6_5_net_bearing_pressure(q: float, sigma_zD: float) -> dict:
    """Net bearing pressure, the gross bearing pressure less the initial
    vertical effective stress at the bearing elevation, q' = q - sigma'_zD.
    A q below sigma'_zD gives a negative q', returned with net_negative
    True and a note: the page defines q' as the net bearing pressure and
    prints no sign condition; a negative value is a net unloading.

    Print check (Eq. 6-5, p. 127, typed in from the rendered page):

        printed    q′ = q − σ′zD
        here       the same

    Parameters
    ----------
    q : float
        Gross bearing pressure, tsf (qeq for an eccentric load).
    sigma_zD : float
        Initial vertical effective stress at the bearing elevation, tsf.

    Returns
    -------
    dict
        q_net, net_negative, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a stress is negative.
    """
    qn = _non_negative("q", q) - _non_negative("sigma_zD", sigma_zD)
    return {"q_net": qn, "net_negative": qn < 0,
            "units": {"q_net": "tsf"},
            "source": _source("Eq. 6-5", 127),
            "valid_for": "Settlement analysis (paragraph 6-6a(1)).",
            "notes": _net_negative_note(qn, "q'", "Eq. 6-5 (p. 127)")}


def equation_6_6_induced_vertical_stress(I_sigma: float, q: float,
                                         sigma_zD: float) -> dict:
    """Induced vertical stress below a footing or loaded area from the net
    bearing pressure and an influence factor, delta_sigma_z = I_sigma
    (q - sigma'_zD). A q below sigma'_zD gives a negative delta_sigma_z,
    returned with net_negative True and a note (the page prints no sign
    condition; a negative value is a net unloading).

    Print check (Eq. 6-6, p. 131, typed in from the rendered page; printed
    again in Table 7-3, Step 7, p. 161):

        printed    Δσz = Iσ(q − σ′zD)
        here       the same

    Parameters
    ----------
    I_sigma : float
        Influence factor for vertical stress (Eqs. 6-8 to 6-13 or the
        charts, Figures 6-7 to 6-12).
    q : float
        Gross bearing pressure, tsf.
    sigma_zD : float
        Vertical effective stress at the bearing elevation, tsf.

    Returns
    -------
    dict
        delta_sigma_z, net_negative, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If I_sigma is outside 0 to 1 or a stress is negative.
    """
    i = float(I_sigma)
    if not 0 <= i <= 1:
        raise ValueError(f"I_sigma = {I_sigma}: give 0 to 1")
    qn = _non_negative("q", q) - _non_negative("sigma_zD", sigma_zD)
    return {"delta_sigma_z": i * qn, "net_negative": qn < 0,
            "units": {"delta_sigma_z": "tsf"},
            "source": _source("Eq. 6-6", 131),
            "valid_for": "Footings and uniformly loaded areas (6-6e(1)).",
            "notes": _net_negative_note(qn, "delta_sigma_z",
                                        "Eq. 6-6 (p. 131)")}


def equation_6_7_embankment_stress(I_sigma: float, q: float) -> dict:
    """Induced vertical stress beneath the centerline of an embankment,
    delta_sigma_z,fill = 2 I_sigma q, I_sigma from Figure 6-12 and
    q = gamma_m H the unit load of the embankment.

    Print check (Eq. 6-7, p. 140, typed in from the rendered page):

        printed    Δσzfill = 2Iσ · q
        here       the same

    Parameters
    ----------
    I_sigma : float
        Influence factor beneath the centerline, read from Figure 6-12.
    q : float
        Unit load of the embankment, gamma_m H, tsf.

    Returns
    -------
    dict
        delta_sigma_z_fill, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If I_sigma is outside 0 to 0.5 or q is negative.
    """
    i = float(I_sigma)
    if not 0 <= i <= 0.5:
        raise ValueError(f"I_sigma = {I_sigma}: Figure 6-12's factor for "
                         f"one half of the embankment is 0 to 0.5")
    return {"delta_sigma_z_fill": 2 * i * _non_negative("q", q),
            "units": {"delta_sigma_z_fill": "tsf"},
            "source": _source("Eq. 6-7", 140),
            "valid_for": ("Beneath the centerline of an embankment; "
                          "elsewhere by superposition (paragraph 6-8a)."),
            "notes": "Figure 6-12 is a chart, not coded: read it off."}


_SHAPES_6_8 = ("circle", "square", "rectangle", "strip")


def equation_6_8_influence_factor(shape: str, B: float, z: float,
                                  L: float | None) -> dict:
    """Influence factor for the vertical stress beneath the center of a
    uniformly loaded area, within 5 percent of the Boussinesq solution
    (Poulos and Davis 1974): circle (Eq. 6-8), square (6-9), rectangle
    (6-10) and strip (6-11). Example C-1 and the other Appendix C examples
    use the square form.

    Print check (Eqs. 6-8 to 6-11, p. 144, typed in from the rendered page):

        6-8   Iσ = 1 − (1/(1 + (B/(2z))^2))^1.5                 circular
        6-9   Iσ = 1 − (1/(1 + (B/(2z))^2))^1.76                square
        6-10  Iσ = 1 − (1/(1 + (B/(2z))^(1.38 + 0.62 (B/L))))^(2.60 − 0.84 (B/L))
                                                                rectangular
        6-11  Iσ = 1 − (1/(1 + (B/(2z))^1.38))^2.60             strip
        here the same

    Parameters
    ----------
    shape : str
        'circle', 'square', 'rectangle' or 'strip'.
    B : float
        Width or diameter of the loaded area, ft.
    z : float
        Depth below the base, ft (typically the middle of a layer).
    L : float or None
        Length, ft, for 'rectangle'; None otherwise.

    Returns
    -------
    dict
        I_sigma, equation, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown shape, B or z not positive, or L missing, less than
        B, or given for another shape.
    """
    s = str(shape).lower().strip()
    if s not in _SHAPES_6_8:
        raise ValueError(f"Unknown shape {shape!r}: {', '.join(_SHAPES_6_8)}")
    b = _positive("B", B)
    x = b / (2 * _positive("z", z))
    if s == "rectangle":
        if L is None:
            raise ValueError("give L for a rectangle")
        lr = b / _positive("L", L)
        if lr > 1:
            raise ValueError("L is less than B")
        i = 1 - (1 / (1 + x ** (1.38 + 0.62 * lr))) ** (2.60 - 0.84 * lr)
        eq = "6-10"
    else:
        if L is not None:
            raise ValueError(f"L is not used for a {s}; give None")
        if s == "circle":
            i, eq = 1 - (1 / (1 + x ** 2)) ** 1.5, "6-8"
        elif s == "square":
            i, eq = 1 - (1 / (1 + x ** 2)) ** 1.76, "6-9"
        else:
            i, eq = 1 - (1 / (1 + x ** 1.38)) ** 2.60, "6-11"
    return {"I_sigma": i, "equation": eq,
            "units": {"I_sigma": "dimensionless"},
            "source": _source(f"Eq. {eq}", 144),
            "valid_for": ("Beneath the center of a uniformly loaded flexible "
                          "area (paragraph 6-9a)."),
            "notes": ("Within 5 percent of the Boussinesq solution (Poulos "
                      "and Davis 1974).")}


def equation_6_12_two_to_one_influence_factor(shape: str, B: float, z: float,
                                              L: float | None) -> dict:
    """Influence factor by the approximate 2:1 method beneath the center of
    a footing: (B L)/((B + z)(L + z)) for a rectangle (Eq. 6-12) and
    B^2/(B + z)^2 for a circle (Eq. 6-13).

    Print check (Eqs. 6-12 and 6-13, p. 145, typed in from the rendered
    page):

        6-12  Iσ = (B · L)/((B + z)(L + z))     rectangular
        6-13  Iσ = B^2/(B + z)^2                circular
        here the same

    Parameters
    ----------
    shape : str
        'rectangle' or 'circle'.
    B : float
        Width or diameter, ft.
    z : float
        Depth below the base, ft.
    L : float or None
        Length, ft, for 'rectangle'; None for 'circle'.

    Returns
    -------
    dict
        I_sigma, equation, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown shape, a dimension not positive, z < 0, or L missing
        or given for a circle.
    """
    s = str(shape).lower().strip()
    b = _positive("B", B)
    zz = _non_negative("z", z)
    if s == "rectangle":
        if L is None:
            raise ValueError("give L for a rectangle")
        lf = _positive("L", L)
        i, eq = b * lf / ((b + zz) * (lf + zz)), "6-12"
    elif s == "circle":
        if L is not None:
            raise ValueError("L is not used for a circle; give None")
        i, eq = b ** 2 / (b + zz) ** 2, "6-13"
    else:
        raise ValueError(f"Unknown shape {shape!r}: 'rectangle' or 'circle'")
    return {"I_sigma": i, "equation": eq,
            "units": {"I_sigma": "dimensionless"},
            "source": _source(f"Eq. {eq}", 145),
            "valid_for": "Approximate 2:1 method (paragraph 6-9b).",
            "notes": ""}


# ---------------------------------------------------------------------------
# Chapter 7: consolidation
# ---------------------------------------------------------------------------

def equation_7_1_total_settlement(delta_i: float, delta_c: float,
                                  delta_s: float) -> dict:
    """Total settlement as the sum of immediate (distortion), primary
    consolidation and secondary (creep) settlement.

    Print check (Eq. 7-1, p. 146, typed in from the rendered page):

        printed    δT = δi + δc + δs
        here       the same

    Parameters
    ----------
    delta_i : float
        Immediate or distortion settlement, in.
    delta_c : float
        Primary consolidation settlement, in.
    delta_s : float
        Secondary settlement or creep, in.

    Returns
    -------
    dict
        delta_T, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a settlement is negative.
    """
    for n, v in (("delta_i", delta_i), ("delta_c", delta_c),
                 ("delta_s", delta_s)):
        _non_negative(n, v)
    return {"delta_T": delta_i + delta_c + delta_s,
            "units": {"delta_T": "in (the units given)"},
            "source": _source("Eq. 7-1", 146),
            "valid_for": "Settlement components (paragraph 7-3).",
            "notes": ""}


def equation_7_3_constrained_modulus(e0: float, sigma_z: float,
                                     sigma_f: float, sigma_p: float,
                                     Cc: float, Cr: float) -> dict:
    """Constrained modulus M = 1/mv over a stress increment from e-log-p
    parameters: normally consolidated (Eq. 7-3a), overconsolidated
    (Eq. 7-3b) or from overconsolidated to normally consolidated (Eq. 7-4),
    chosen by the stresses as the equations' conditions print them.

    Print check (Eqs. 7-2 to 7-4, p. 150, typed in from the rendered page):

        7-2   M = Δσ′z/Δεz = 1/mv
        7-3a  σ′z ≥ σ′p:  M = (1 + e0) Δσ′z/([log(σ′f/σ′z)] Cc)
        7-3b  σ′f < σ′p:  M = (1 + e0) Δσ′z/([log(σ′f/σ′z)] CR)
        7-4   σ′z < σ′p and σ′f > σ′p:
              M = (1 + e0) Δσ′z/([log(σ′p/σ′z)] CR + [log(σ′f/σ′p)] CC)
        here the same, Δσ′z = σ′f − σ′z, log base 10; σ′f = σ′p exactly
        takes 7-3b (7-4 gives the same there)

    Parameters
    ----------
    e0 : float
        Initial void ratio.
    sigma_z : float
        Initial vertical effective stress, tsf.
    sigma_f : float
        Final vertical effective stress, tsf (> sigma_z).
    sigma_p : float
        Preconsolidation stress, tsf.
    Cc : float
        Compression index.
    Cr : float
        Recompression index.

    Returns
    -------
    dict
        M, m_v, equation, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a stress or index is not positive or sigma_f <= sigma_z.
    """
    e = _non_negative("e0", e0)
    sz = _positive("sigma_z", sigma_z)
    sf = _positive("sigma_f", sigma_f)
    sp = _positive("sigma_p", sigma_p)
    cc = _positive("Cc", Cc)
    cr = _positive("Cr", Cr)
    if sf <= sz:
        raise ValueError("sigma_f must exceed sigma_z")
    ds = sf - sz
    if sz >= sp:
        den, eq = math.log10(sf / sz) * cc, "7-3a"
    elif sf <= sp:
        den, eq = math.log10(sf / sz) * cr, "7-3b"
    else:
        den, eq = math.log10(sp / sz) * cr + math.log10(sf / sp) * cc, "7-4"
    M = (1 + e) * ds / den
    return {"M": M, "m_v": 1 / M, "equation": eq,
            "units": {"M": "tsf", "m_v": "1/tsf"},
            "source": _source(f"Eq. {eq}", 150),
            "valid_for": "Confined (one-dimensional) compression (7-7b).",
            "notes": "M is also denoted D' (p. 150)."}


def equation_7_5_compression_indices(e_1: float, e_2: float,
                                     sigma_1: float, sigma_2: float,
                                     index: str) -> dict:
    """Recompression index Cr = (eH - eG)/log10(sigma'_zG/sigma'_zH)
    (Eq. 7-5) or compression index Cc = (eF - eG')/log10(sigma'_zG'/
    sigma'_zF) (Eq. 7-6) from two points of the reconstructed field
    consolidation curve (Figure 7-4, Table 7-2).

    Print check (Eqs. 7-5 and 7-6, pp. 157-158, typed in from the rendered
    pages):

        7-5  Cr = (eH − eG)/log10(σ′zG/σ′zH)
        7-6  Cc = (eF − eG′)/log10(σ′zG′/σ′zF)
        here the same: point 1 is H (Cr) or F (Cc), point 2 is G or G′

    Parameters
    ----------
    e_1 : float
        Void ratio at point H (Cr) or F (Cc).
    e_2 : float
        Void ratio at point G (Cr) or G' (Cc).
    sigma_1 : float
        Vertical effective stress at point H or F, tsf.
    sigma_2 : float
        Vertical effective stress at point G or G', tsf (> sigma_1).
    index : str
        'Cr' (Eq. 7-5) or 'Cc' (Eq. 7-6).

    Returns
    -------
    dict
        index name and value, equation, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown index, stresses not positive or not increasing, or
        a void ratio that rises from point 1 to point 2 (the library's
        reading; the page prints no condition on it).
    """
    k = str(index).strip()
    if k not in ("Cr", "Cc"):
        raise ValueError(f"Unknown index {index!r}: 'Cr' or 'Cc'")
    s1 = _positive("sigma_1", sigma_1)
    s2 = _positive("sigma_2", sigma_2)
    if s2 <= s1:
        raise ValueError("sigma_2 must exceed sigma_1")
    eq, page = ("7-5", 157) if k == "Cr" else ("7-6", 158)
    if e_2 > e_1:
        raise ValueError(
            f"e_2 ({e_2}) is above e_1 ({e_1}): Eq. {eq} (p. {page}) gives "
            f"{k}, the slope of the reconstructed field consolidation curve "
            f"(Figure 7-4), from a point 1 to a point 2 at higher stress; a "
            f"void ratio that rises with the stress gives a negative {k}. The "
            f"page prints no condition on e_2 against e_1; the library "
            f"refuses it (its reading)")
    return {k: (e_1 - e_2) / math.log10(s2 / s1), "equation": eq,
            "units": {k: "dimensionless"},
            "source": _source(f"Eq. {eq}", page),
            "valid_for": ("The reconstructed field curve (simplified "
                          "Schmertmann 1955 procedure, Table 7-2)."),
            "notes": ""}


def equation_7_7_consolidation_settlement(H: float, e0: float, Cc: float,
                                          Cr: float, sigma_zo: float,
                                          sigma_zf: float,
                                          sigma_p: float) -> dict:
    """Primary consolidation settlement of one layer from e-log-p
    parameters: normally consolidated, sigma'_zo about sigma'_p (Eq. 7-7);
    overconsolidated with sigma'_zf below sigma'_p (Eq. 7-8); or from
    overconsolidated to normally consolidated, sigma'_zo < sigma'_p <
    sigma'_zf (Eq. 7-9). Sum the layers for the total, as Example C-1
    does (Table C-1, Step 9).

    Print check (Eqs. 7-7 to 7-9, pp. 159-160, typed in from the rendered
    pages):

        7-7  δc = ∑ (Cc/(1 + e0)) H · log(σ′zf/σ′zo)        σ′zo ≈ σ′p
        7-8  δc = ∑ (Cr/(1 + e0)) H · log(σ′zf/σ′zo)        σ′zf < σ′p
        7-9  δc = ∑ [(Cr/(1 + e0)) H · log(σ′p/σ′zo)
                     + (Cc/(1 + e0)) H · log(σ′zf/σ′p)]    σ′z0 < σ′p < σ′zf
        here one layer of each, log base 10; σ′p = σ′zo takes 7-7 and
        σ′zf = σ′p takes 7-8 (7-9 gives the same at both)

    Parameters
    ----------
    H : float
        Layer thickness, ft.
    e0 : float
        Initial void ratio.
    Cc : float
        Compression index.
    Cr : float
        Recompression index.
    sigma_zo : float
        Initial vertical effective stress at the middle of the layer, tsf.
    sigma_zf : float
        Final vertical effective stress there, sigma'_zo + delta_sigma_z,
        tsf.
    sigma_p : float
        Preconsolidation stress at the middle of the layer, tsf.

    Returns
    -------
    dict
        settlement_ft, settlement_in, equation, units, source, valid_for,
        notes.

    Raises
    ------
    ValueError
        If a value is not positive, sigma_zf < sigma_zo, or sigma_p is below
        sigma_zo (the equations cover sigma'_zo about sigma'_p and above;
        to use 7-7 for such a soil give sigma_p = sigma_zo, which is the
        engineer's call).
    """
    h = _positive("H", H)
    e = _non_negative("e0", e0)
    cc = _positive("Cc", Cc)
    cr = _positive("Cr", Cr)
    so = _positive("sigma_zo", sigma_zo)
    sf = _positive("sigma_zf", sigma_zf)
    sp = _positive("sigma_p", sigma_p)
    if sf < so:
        raise ValueError("sigma_zf is less than sigma_zo: unloading, see "
                         "equations 7-38 and 7-40")
    if sp < so:
        raise ValueError(
            f"sigma_p ({sigma_p}) is below sigma_zo ({sigma_zo}): the "
            f"conditions printed beside equations 7-7 to 7-9 (pp. 159-160) "
            f"are sigma'_zo about sigma'_p (7-7), sigma'_zf < sigma'_p (7-8) "
            f"and sigma'_zo < sigma'_p < sigma'_zf (7-9), and none covers "
            f"sigma'_p < sigma'_zo; to use 7-7 give sigma_p = sigma_zo")
    if sp == so:
        ft, eq, page = cc / (1 + e) * h * math.log10(sf / so), "7-7", 159
    elif sf <= sp:
        ft, eq, page = cr / (1 + e) * h * math.log10(sf / so), "7-8", 160
    else:
        ft = (cr / (1 + e) * h * math.log10(sp / so)
              + cc / (1 + e) * h * math.log10(sf / sp))
        eq, page = "7-9", 160
    out = _settlement(ft)
    out.update({"equation": eq, "units": dict(_SETTLEMENT_UNITS),
                "source": _source(f"Eq. {eq}", page),
                "valid_for": ("One-dimensional primary consolidation of a "
                              "layer (Table 7-3)."),
                "notes": ("The list of symbols gives delta_c in inches, but "
                          "the formula with H in feet, as listed, gives feet, "
                          "so both are returned (settlement_ft, and "
                          "settlement_in = settlement_ft x 12). Example C-1 "
                          "works in feet: Table C-1, Step 9 (p. 342) sums "
                          "the layers as 'Sum delta_c = 0.0309 ft (0.37 "
                          "inches)'.")})
    return out


def equation_7_10_constrained_modulus_settlement(layers: list) -> dict:
    """Settlement from the constrained modulus of each layer (the
    dilatometer method of Table 7-4), delta = sum(delta_sigma_z/M H) with
    delta_sigma_z = I_sigma (q - sigma'_zD) at the middle of each layer.

    Print check (Eq. 7-10, p. 164, typed in from the rendered page):

        printed    δ = ∑ (Iσ(q − σ′zD)/M) H = ∑ (Δσz/M) H
        here       the same

    Parameters
    ----------
    layers : list of (float, float, float)
        For each layer (H in ft, delta_sigma_z in tsf, M in tsf).

    Returns
    -------
    dict
        settlement_ft, settlement_in, per_layer_ft, units, source,
        valid_for, notes.

    Raises
    ------
    ValueError
        If no layers are given or a value is out of range.
    """
    if not layers:
        raise ValueError("give at least one layer (H, delta_sigma_z, M)")
    per = []
    for h, ds, m in layers:
        per.append(_non_negative("delta_sigma_z", ds) / _positive("M", m)
                   * _positive("H", h))
    out = _settlement(sum(per))
    out.update({"per_layer_ft": per, "units": dict(_SETTLEMENT_UNITS),
                "source": _source("Eq. 7-10", 164),
                "valid_for": ("Layers with a constrained modulus, e.g. from "
                              "the DMT (Table 7-4, paragraph 7-10)."),
                "notes": ("q is the gross (or gross equivalent) bearing "
                          "pressure or qult/FS, whichever is less (p. 164). "
                          "The list of symbols gives delta in inches, but "
                          "the formula with H in feet, as listed, gives "
                          "feet, so both are returned (settlement_ft, and "
                          "settlement_in = settlement_ft x 12). Example C-6 "
                          "converts the same way: Table C-6b, Step 7 (p. "
                          "373) multiplies by (12 in/1 ft).")})
    return out


# ---------------------------------------------------------------------------
# Menard and Rousseau pressuremeter method
# ---------------------------------------------------------------------------

def equation_7_13_harmonic_mean(moduli: list) -> dict:
    """Harmonic mean of pressuremeter moduli, n/(1/E1 + 1/E2 + ... + 1/En),
    for a combined layer (Eq. 7-13) or a soft or loose layer (Eq. 7-15).

    Print check (Eqs. 7-13 and 7-15, pp. 168-169, typed in from the rendered
    pages):

        7-13  Ek = n/(1/E1 + 1/E2 + ⋯+ 1/En)
        7-15  EL = n/(1/E1 + 1/E2 + ⋯1/En)   (no plus before the last term,
              as printed)
        here the harmonic mean of the n values

    Parameters
    ----------
    moduli : list of float
        The moduli E1 ... En, tsf.

    Returns
    -------
    dict
        E, n, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If no moduli are given or one is not positive.
    """
    vals = [_positive("each modulus", v) for v in moduli]
    if not vals:
        raise ValueError("give at least one modulus")
    return {"E": len(vals) / sum(1 / v for v in vals), "n": len(vals),
            "units": {"E": "tsf"},
            "source": _source("Eqs. 7-13 and 7-15", 168),
            "valid_for": "Table 7-5, Steps 7 and 13.",
            "notes": "Equation 7-15 is printed without the last plus sign."}


def equation_7_14_equivalent_distortion_modulus(E1: float, E2: float,
                                                E345: float, E678: float,
                                                E916: float) -> dict:
    """Equivalent distortion modulus within the zone of the deviatoric
    tensor (to 8B), from the five combined layers of Figure 7-12:
    1/Ed = (1/4)(1/E1 + 1/(0.85 E2) + 1/E3/4/5 + 1/(2.5 E6/7/8) +
    1/(2.5 E9/16)).

    Print check (Eq. 7-14, p. 168, typed in from the rendered page):

        printed    1/Ed = (1/4)(1/E1 + 1/(0.85E2) + 1/(E3/4/5)
                          + 1/(2.5E6/7/8) + 1/(2.5E9/16))
        here       the same

    Parameters
    ----------
    E1, E2, E345, E678, E916 : float
        Harmonic-mean moduli of the combined layers 0-B/2, B/2-B, B-2.5B,
        2.5B-4B and 4B-8B below the footing, tsf (Eq. 7-13).

    Returns
    -------
    dict
        E_d, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a modulus is not positive.
    """
    vals = [_positive(n, v) for n, v in (("E1", E1), ("E2", E2),
                                         ("E345", E345), ("E678", E678),
                                         ("E916", E916))]
    inv = 0.25 * (1 / vals[0] + 1 / (0.85 * vals[1]) + 1 / vals[2]
                  + 1 / (2.5 * vals[3]) + 1 / (2.5 * vals[4]))
    return {"E_d": 1 / inv, "units": {"E_d": "tsf"},
            "source": _source("Eq. 7-14", 168),
            "valid_for": "Table 7-5, Step 9.", "notes": ""}


def equation_7_11_menard_settlement(q: float, sigma_zD: float, B: float,
                                    E_d: float, E_c: float, alpha_d: float,
                                    alpha_c: float, lambda_d: float,
                                    lambda_c: float,
                                    soft_layers: list) -> dict:
    """Settlement by the Menard and Rousseau pressuremeter method: a
    deviatoric term (2/(9 Ed))(q - sigma'_zD) B0 (lambda_d B/B0)^alpha_d with
    B0 = 2.0 ft, plus a spherical term (alpha_c/(9 Ec))(q - sigma'_zD)
    lambda_c B (Eq. 7-11), plus for a soft layer within 2B the sum of
    alpha_L (1/EL - 1/Ed) I_sigma (q - sigma'_zD) H over such layers
    (Eq. 7-12). alpha from Table 7-6; lambda_d and lambda_c are read off
    Figure 7-11 (a chart, not coded) for the footing's L/B.

    Print check (Eqs. 7-11 and 7-12, p. 167, typed in from the rendered
    page):

        7-11  δ = [(2/(9Ed)) (q − σ′zD) B0 (λd B/B0)^αd]
                  + [(∝c/(9Ec)) (q − σ′zD) λc · B]
        7-12  δ = 7-11 + [∑ αL (1/EL − 1/Ed) Iσ (q − σ′zD) H]
        here the same, B0 = 2.0 ft; the print sets the spherical term's
        factor as ∝c (a proportional-to sign), meaning αc

    Parameters
    ----------
    q : float
        Gross bearing pressure, tsf (or qult/FS, whichever is less).
    sigma_zD : float
        Vertical effective stress at the bearing elevation, tsf.
    B : float
        Footing width, ft.
    E_d : float
        Equivalent distortion modulus to 8B, tsf (Eq. 7-14).
    E_c : float
        Modulus within B/2 below the footing, tsf.
    alpha_d, alpha_c : float
        Rheological factors (Table 7-6).
    lambda_d, lambda_c : float
        Shape factors read off Figure 7-11.
    soft_layers : list of (float, float, float, float)
        For each soft or loose layer within 2B: (alpha_L, E_L in tsf,
        I_sigma, H in ft). An empty list gives Eq. 7-11.

    Returns
    -------
    dict
        settlement_ft, settlement_in, deviatoric_ft, spherical_ft,
        soft_layers_ft, equation, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a modulus, B or a shape factor is not positive, a rheological
        factor is outside 1/4 to 1 (the range of the values Table 7-6
        prints), I_sigma is outside 0 to 1, or q < sigma_zD (the
        library's reading). An E_L above
        E_d is computed as printed, with a note (the page prints no
        condition on it).
    """
    qn = _net_refusal(q, sigma_zD, "Eqs. 7-11 and 7-12 (p. 167)")
    b = _positive("B", B)
    ed = _positive("E_d", E_d)
    ec = _positive("E_c", E_c)
    for n, v in (("alpha_d", alpha_d), ("alpha_c", alpha_c)):
        _rheological(n, v)
    ld = _positive("lambda_d", lambda_d)
    lc = _positive("lambda_c", lambda_c)
    B0 = 2.0
    dev = 2 / (9 * ed) * qn * B0 * (ld * b / B0) ** alpha_d
    sph = alpha_c / (9 * ec) * qn * lc * b
    soft = 0.0
    stiff = []
    for aL, eL, isg, h in soft_layers:
        _rheological("alpha_L", aL)
        i = float(isg)
        if not 0 <= i <= 1:
            raise ValueError(f"I_sigma = {isg}: give 0 to 1")
        el = _positive("E_L", eL)
        if el > ed:
            stiff.append(el)
        soft += aL * (1 / el - 1 / ed) * i * qn * _positive("H", h)
    eq = "7-12" if soft_layers else "7-11"
    stiff_note = ""
    if stiff:
        stiff_note = (f" E_L above E_d ({', '.join(f'{e:g}' for e in stiff)} "
                      f"tsf against {ed:g} tsf) makes that layer's term "
                      f"negative, so it lowers the settlement. The page "
                      f"defines EL as the modulus of a soft/loose layer "
                      f"(p. 167) but prints no condition EL <= Ed; the term "
                      f"is computed as printed.")
    out = _settlement(dev + sph + soft)
    out.update({"deviatoric_ft": dev, "spherical_ft": sph,
                "soft_layers_ft": soft, "equation": eq,
                "units": dict(_SETTLEMENT_UNITS, deviatoric_ft="ft",
                              spherical_ft="ft", soft_layers_ft="ft"),
                "source": _source(f"Eq. {eq}", 167),
                "valid_for": ("Deep relatively uniform deposits (7-11); a "
                              "soft layer within 2B (7-12); Table 7-5."),
                "notes": ("B0 = 2.0 ft. lambda_d and lambda_c come from "
                          "Figure 7-11, a chart not coded here: Example C-5 "
                          "reads 1.1 for both at L/B = 1." + stiff_note)})
    return out


# ---------------------------------------------------------------------------
# Schmertmann CPT method
# ---------------------------------------------------------------------------

def equation_7_16_cpt_modulus(qc: float, footing: str) -> dict:
    """Equivalent Young's modulus from the CPT tip resistance for
    Schmertmann's method: Es = 2.5 qc for square and axisymmetric footings
    (Eq. 7-16), 3.5 qc for strip footings with L/B > 10 (Eq. 7-17); for
    1 < L/B < 10 the manual says Es can be interpolated (paragraph 7-12a).

    Print check (Eqs. 7-16 and 7-17, p. 172, typed in from the rendered
    page; 7-16 is printed again on p. 173):

        7-16  Es = 2.5qc   (Axisymmetric Footings)
        7-17  Es = 3.5qc   (Plane Strain Footings)
        here the same

    Parameters
    ----------
    qc : float
        Measured cone tip resistance, tsf.
    footing : str
        'axisymmetric' (square, circular) or 'plane strain' (strip).

    Returns
    -------
    dict
        E_s, equation, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown footing type or qc not positive.
    """
    f = str(footing).lower().strip()
    c = _positive("qc", qc)
    if f == "axisymmetric":
        es, eq = 2.5 * c, "7-16"
    elif f == "plane strain":
        es, eq = 3.5 * c, "7-17"
    else:
        raise ValueError(f"Unknown footing {footing!r}: 'axisymmetric' or "
                         f"'plane strain'")
    return {"E_s": es, "equation": eq, "units": {"E_s": "tsf"},
            "source": _source(f"Eq. {eq}", 172),
            "valid_for": ("Young (< 100 years), normally consolidated, clean "
                          "silica sands; generally conservative (7-12a)."),
            "notes": "Interpolate for 1 < L/B < 10 (paragraph 7-12a)."}


def equation_7_18_peak_strain_influence(q: float, sigma_zD: float,
                                        sigma_zp: float) -> dict:
    """Peak strain influence factor for Schmertmann's method,
    Izp = 0.5 + 0.1 sqrt((q - sigma'_zD)/sigma'_zp), with sigma'_zp the
    vertical effective stress at the depth of the peak (D + B/2 for
    axisymmetric footings, D + B for plane strain footings).

    Print check (Eq. 7-18, p. 173, typed in from the rendered page):

        printed    Izp = 0.5 + 0.1√((q − σ′zD)/σ′zp)
        here       the same

    Parameters
    ----------
    q : float
        Gross bearing pressure, tsf (or qult/FS, whichever is less).
    sigma_zD : float
        Vertical effective stress at the bearing elevation, tsf.
    sigma_zp : float
        Vertical effective stress at the depth of peak strain influence,
        tsf.

    Returns
    -------
    dict
        I_zp, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If q < sigma_zD (the library's reading) or sigma_zp is not
        positive.
    """
    qn = _net_refusal(q, sigma_zD, "Eq. 7-18 (p. 173)")
    return {"I_zp": 0.5 + 0.1 * math.sqrt(qn / _positive("sigma_zp", sigma_zp)),
            "units": {"I_zp": "dimensionless"},
            "source": _source("Eq. 7-18", 173),
            "valid_for": "Schmertmann's CPT method (Table 7-8).",
            "notes": "Peak at B/2 (axisymmetric) or B (plane strain)."}


def equation_7_19_strain_influence_factor(footing: str, z: float, B: float,
                                          I_zp: float,
                                          L: float | None) -> dict:
    """Vertical strain influence factor at depth z below the footing for
    Schmertmann's method: axisymmetric (Eqs. 7-19, 7-20, to 2B), plane
    strain (Eqs. 7-21, 7-22, to 4B) and rectangular footings
    (Eq. 7-23, Izr = Iza + 0.111 (Izc - Iza)(L/B - 1)).

    Print check (Eqs. 7-19 to 7-23, pp. 173-174, typed in from the rendered
    pages):

        7-19  Iza = 0.1 + (z/B)(2 · Izp − 0.2)      z = 0 to B/2
        7-20  Iza = 0.667 · Izp (2 − z/B)            z = B/2 to 2B
        7-21  Izc = 0.2 + (z/B)(Izp − 0.2)          z = 0 to B
        7-22  Izc = 0.331 · Izp (4 − z/B)            z = B to 4B
        7-23  Izr = Iza + 0.111 (Izc − Iza)(L/B − 1)
        here the same; a rectangular footing needs Iza, so z to 2B, and
        1 <= L/B <= 10 (at 10 the formula gives Izc to 0.999)

    Parameters
    ----------
    footing : str
        'axisymmetric', 'plane strain' or 'rectangular'.
    z : float
        Depth from the bottom of the footing to the middle of the layer, ft.
    B : float
        Footing width, ft.
    I_zp : float
        Peak strain influence factor (Eq. 7-18).
    L : float or None
        Footing length, ft, for 'rectangular'; None otherwise.

    Returns
    -------
    dict
        I_z, equation, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown footing, z beyond the printed depth range, or L
        missing, out of 1 to 10 B, or given for another footing type.
    """
    f = str(footing).lower().strip()
    zz = _non_negative("z", z)
    b = _positive("B", B)
    izp = _positive("I_zp", I_zp)
    r = zz / b

    def iza():
        if r <= 0.5:
            return 0.1 + r * (2 * izp - 0.2), "7-19"
        if r <= 2:
            return 0.667 * izp * (2 - r), "7-20"
        raise ValueError(f"z/B = {r:.3f}: Iza is printed for z = 0 to 2B")

    def izc():
        if r <= 1:
            return 0.2 + r * (izp - 0.2), "7-21"
        if r <= 4:
            return 0.331 * izp * (4 - r), "7-22"
        raise ValueError(f"z/B = {r:.3f}: Izc is printed for z = 0 to 4B")

    if f in ("axisymmetric", "plane strain"):
        if L is not None:
            raise ValueError(f"L is not used for a {f} footing; give None")
        val, eq = iza() if f == "axisymmetric" else izc()
    elif f == "rectangular":
        if L is None:
            raise ValueError("give L for a rectangular footing")
        lb = _positive("L", L) / b
        if not 1 <= lb <= 10:
            raise ValueError(f"L/B = {lb:.3f}: give 1 to 10 (above 10 the "
                             f"footing is a strip, paragraph 7-12a)")
        a, _ = iza()
        c, _ = izc()
        val, eq = a + 0.111 * (c - a) * (lb - 1), "7-23"
    else:
        raise ValueError(f"Unknown footing {footing!r}: 'axisymmetric', "
                         f"'plane strain' or 'rectangular'")
    page = 173 if eq == "7-19" else 174
    return {"I_z": val, "equation": eq, "units": {"I_z": "dimensionless"},
            "source": _source(f"Eq. {eq}", page),
            "valid_for": "Schmertmann's CPT method (Figure 7-13, Table 7-8).",
            "notes": ""}


def equation_7_24_embedment_factor(q: float, sigma_zD: float) -> dict:
    """Embedment correction factor for Schmertmann's method,
    C1 = 1 - 0.5 sigma'_zD/(q - sigma'_zD), which the equation limits to at
    least 0.5. The limit is applied as printed: where the formula gives
    less, C1 = 0.5 is returned, with the formula's value in C1_unlimited
    and limit_governs True.

    Print check (Eq. 7-24, p. 174, typed in from the rendered page):

        printed    C1 = 1 − 0.5 (σ′zD/(q − σ′zD)) ≥ 0.5
        here       the same; below 0.5, C1 = 0.5, the formula's value in
                   C1_unlimited

    Parameters
    ----------
    q : float
        Gross bearing pressure, tsf.
    sigma_zD : float
        Vertical effective stress at the bearing elevation, tsf.

    Returns
    -------
    dict
        C1, C1_unlimited, limit_governs, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If q <= sigma_zD (the library's reading; the formula divides by
        q - sigma'zD).
    """
    s = _non_negative("sigma_zD", sigma_zD)
    qn = _net_refusal(q, s, "Eq. 7-24 (p. 174)", strict=True)
    c1 = 1 - 0.5 * s / qn
    governs = c1 < 0.5
    notes = ""
    if governs:
        notes = (f"The formula gives C1 = {c1:.3f}; Eq. 7-24 (p. 174) prints "
                 f"'C1 = 1 - 0.5 (sigma'zD/(q - sigma'zD)) >= 0.5', so C1 = "
                 f"0.5 is returned (C1_unlimited holds the formula's value).")
    return {"C1": max(c1, 0.5), "C1_unlimited": c1, "limit_governs": governs,
            "units": {"C1": "dimensionless", "C1_unlimited": "dimensionless"},
            "source": _source("Eq. 7-24", 174),
            "valid_for": "Schmertmann's CPT method.", "notes": notes}


def equation_7_25_creep_factor(t_years: float) -> dict:
    """Creep correction factor for Schmertmann's method,
    C2 = 1 + 0.2 log10(t/0.1) for t >= 0.1 year and 1.0 for t < 0.1 year
    (paragraph 7-12d); typically computed for 50 years, C2 = 1.54.

    Print check (Eq. 7-25 and paragraph 7-12d, p. 174, typed in from the
    rendered page):

        printed    C2 = 1 + 0.2 log10(t/0.1)   for t ≥ 0.1 year
                   "For t < 0.1 years, C2 = 1.0."
        here       the same

    Parameters
    ----------
    t_years : float
        Time after foundation loading, years.

    Returns
    -------
    dict
        C2, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If t is negative.
    """
    t = _non_negative("t_years", t_years)
    c2 = 1.0 if t < 0.1 else 1 + 0.2 * math.log10(t / 0.1)
    return {"C2": c2, "units": {"C2": "dimensionless"},
            "source": _source("Eq. 7-25", 174),
            "valid_for": "Schmertmann's CPT method.",
            "notes": "t < 0.1 year: C2 = 1.0 (paragraph 7-12d)."}


def equation_7_26_schmertmann_settlement(C1: float, C2: float, q: float,
                                         sigma_zD: float,
                                         layers: list) -> dict:
    """Settlement of a footing on sand by Schmertmann's CPT method,
    delta = C1 C2 (q - sigma'_zD) sum(Iz H/Es) over the layers within the
    strain influence diagram.

    Print check (Eq. 7-26, p. 175, typed in from the rendered page):

        printed    δ = C1 · C2(q − σ′zD) ∑[(Iz · H)/Es]
        here       the same

    Parameters
    ----------
    C1 : float
        Embedment factor (Eq. 7-24).
    C2 : float
        Creep factor (Eq. 7-25).
    q : float
        Gross bearing pressure, tsf.
    sigma_zD : float
        Vertical effective stress at the bearing elevation, tsf.
    layers : list of (float, float, float)
        For each layer (I_z, H in ft, E_s in tsf).

    Returns
    -------
    dict
        settlement_ft, settlement_in, sum_Iz_H_over_Es, per_layer, units,
        source, valid_for, notes.

    Raises
    ------
    ValueError
        If no layers are given, a factor is out of range, or q < sigma_zD
        (the library's reading).
    """
    if not layers:
        raise ValueError("give at least one layer (I_z, H, E_s)")
    if float(C1) < 0.5:
        raise ValueError("C1 is at least 0.5 (Eq. 7-24)")
    if float(C2) < 1:
        raise ValueError("C2 is at least 1.0 (Eq. 7-25)")
    qn = _net_refusal(q, sigma_zD, "Eq. 7-26 (p. 175)")
    per = [_non_negative("I_z", iz) * _positive("H", h) / _positive("E_s", es)
           for iz, h, es in layers]
    s = sum(per)
    out = _settlement(C1 * C2 * qn * s)
    out.update({"sum_Iz_H_over_Es": s, "per_layer": per,
                "units": dict(_SETTLEMENT_UNITS, sum_Iz_H_over_Es="ft/tsf"),
                "source": _source("Eq. 7-26", 175),
                "valid_for": "Cohesionless soils, Schmertmann's CPT method "
                             "(Table 7-8).",
                "notes": ""})
    return out


# ---------------------------------------------------------------------------
# Burland and Burbidge SPT method
# ---------------------------------------------------------------------------

def equation_7_27_depth_of_influence(B: float) -> dict:
    """Depth of influence for the Burland and Burbidge method,
    ZI = 1.43 B^0.7 (B and ZI in feet), valid only where N60 increases or
    is constant with depth; where it decreases, ZI may be taken as 2B or
    the bottom of the loose layer, whichever is less (paragraph 7-13a).

    Print check (Eq. 7-27, p. 176, typed in from the rendered page):

        printed    ZI = 1.43B^0.7
        here       the same, B in ft

    Parameters
    ----------
    B : float
        Footing width, ft.

    Returns
    -------
    dict
        Z_I, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If B is not positive.
    """
    return {"Z_I": 1.43 * _positive("B", B) ** 0.7, "units": {"Z_I": "ft"},
            "source": _source("Eq. 7-27", 176),
            "valid_for": ("N60 increasing or constant with depth; B in feet "
                          "(the coefficient 1.43 is for feet)."),
            "notes": ("Where N60 decreases with depth, ZI may be assumed as "
                      "2B or to the bottom of the loose layer, whichever is "
                      "less (paragraph 7-13a).")}


def equation_7_28_compressibility_index(N60_mean: float) -> dict:
    """Soil compressibility index for the Burland and Burbidge method,
    Ic = 0.35/N60^1.4 with N60 the arithmetic mean of the measured N60
    within the depth of influence.

    Print check (Eq. 7-28, p. 176, typed in from the rendered page):

        printed    Ic = 0.35/(N̅60)^1.4
        here       the same

    Parameters
    ----------
    N60_mean : float
        Arithmetic mean of the measured N60 within ZI, blows/ft.

    Returns
    -------
    dict
        I_c, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If N60 is not positive.
    """
    return {"I_c": 0.35 / _positive("N60_mean", N60_mean) ** 1.4,
            "units": {"I_c": "1/tsf"},
            "source": _source("Eq. 7-28", 176),
            "valid_for": "Sands and gravels (Table 7-9).", "notes": ""}


def equation_7_32_shape_factor(footing: str, L: float | None,
                               B: float | None) -> dict:
    """Shape correction factor for the Burland and Burbidge method:
    C1 = [1.25 (L/B)/((L/B) + 0.25)]^2 for a rectangular footing (at least
    1), 1 for an axisymmetric footing and 1.56 for a strip (paragraph
    7-13e).

    Print check (Eq. 7-32 and paragraph 7-13e, p. 177, typed in from the
    rendered page):

        printed    C1 = [1.25 (L/B)/((L/B) + 0.25)]^2 ≥ 1
                   "For axisymmetric footings, use C1 = 1. For strip
                   footings where L/B tends to infinity, use C1 = 1.56."
        here       the same

    Parameters
    ----------
    footing : str
        'axisymmetric', 'rectangular' or 'strip'.
    L : float or None
        Length, ft, for 'rectangular'; None otherwise.
    B : float or None
        Width, ft, for 'rectangular'; None otherwise.

    Returns
    -------
    dict
        C1, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown footing, or L and B missing, given for another type,
        or L < B.
    """
    f = str(footing).lower().strip()
    if f in ("axisymmetric", "strip"):
        if L is not None or B is not None:
            raise ValueError(f"L and B are not used for a {f} footing")
        c1 = 1.0 if f == "axisymmetric" else 1.56
    elif f == "rectangular":
        if L is None or B is None:
            raise ValueError("give L and B for a rectangular footing")
        lb = _positive("L", L) / _positive("B", B)
        if lb < 1:
            raise ValueError("L is less than B")
        c1 = (1.25 * lb / (lb + 0.25)) ** 2
    else:
        raise ValueError(f"Unknown footing {footing!r}: 'axisymmetric', "
                         f"'rectangular' or 'strip'")
    return {"C1": c1, "units": {"C1": "dimensionless"},
            "source": _source("Eq. 7-32", 177),
            "valid_for": "Burland and Burbidge method (Table 7-9).",
            "notes": "Strip 1.56 and axisymmetric 1 per paragraph 7-13e."}


def equation_7_33_thickness_factor(H_s: float, Z_I: float) -> dict:
    """Layer thickness correction factor for the Burland and Burbidge
    method when the granular layer below the footing is thinner than the
    depth of influence: C2 = (Hs/ZI)(2 - Hs/ZI). Paragraph 7-13f computes it
    only when Hs < ZI; for Hs >= ZI no correction is made (C2 = 1,
    ``applies`` False).

    Print check (Eq. 7-33 and paragraph 7-13f, p. 177, typed in from the
    rendered page):

        printed    C2 = (Hs/ZI)(2 − Hs/ZI) ≤ 1
                   "When the thickness of the granular layer (Hs) ... is
                   less than the zone of influence (ZI), a layer thickness
                   correction factor (C2) is computed per equation 7-33."
        here       the same for Hs < ZI; 1 otherwise

    Parameters
    ----------
    H_s : float
        Thickness of the granular layer below the base, ft.
    Z_I : float
        Depth of influence, ft (Eq. 7-27).

    Returns
    -------
    dict
        C2, applies, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a value is not positive.
    """
    hs = _positive("H_s", H_s)
    zi = _positive("Z_I", Z_I)
    if hs < zi:
        r = hs / zi
        c2, applies = r * (2 - r), True
    else:
        c2, applies = 1.0, False
    return {"C2": c2, "applies": applies, "units": {"C2": "dimensionless"},
            "source": _source("Eq. 7-33", 177),
            "valid_for": "Burland and Burbidge method (Table 7-9).",
            "notes": ("Computed only when Hs < ZI (paragraph 7-13f); "
                      "Example C-7e prints C2 = 1.0 for Hs = ZI.")}


def equation_7_34_time_factor(R3: float, Rt: float, t_years: float) -> dict:
    """Time-dependent factor for the Burland and Burbidge method,
    C3 = 1 + R3 + Rt log10(t/3), t in years from loading. The manual gives
    conservative values: static loads R3 = 0.3, Rt = 0.2 (C3 = 1.5 at 30
    years); fluctuating loads such as bridges R3 = 0.7, Rt = 0.8 (C3 = 2.5
    at 30 years); the choice is the engineer's.

    Range: p. 178 prints no range for t. It says R3 accounts for the
    settlement within the first 3 years and Rt for the settlement after
    them. The function refuses t below 3 years, where log10(t/3) turns
    negative; that refusal is the library's reading, not a printed
    condition.

    Print check (Eq. 7-34 and paragraph 7-13g, p. 178, typed in from the
    rendered page):

        printed    C3 = 1 + R3 + Rt · log10(t/3)
        here       the same

    Parameters
    ----------
    R3 : float
        Time-dependent factor for the first 3 years.
    Rt : float
        Time-dependent factor after the first 3 years.
    t_years : float
        Time after foundation loading, years (at least 3: the library's
        reading).

    Returns
    -------
    dict
        C3, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If R3 or Rt is negative or t < 3 years (the library's reading).
    """
    r3 = _non_negative("R3", R3)
    rt = _non_negative("Rt", Rt)
    t = float(t_years)
    if t < 3:
        raise ValueError(
            f"t = {t_years} years: p. 178 says R3 accounts for the settlement "
            f"within the first 3 years and Rt for the settlement after them, "
            f"and log10(t/3) turns negative below 3 years. The library refuses "
            f"t below 3 years; this is the library's reading, not a condition "
            f"the page prints")
    return {"C3": 1 + r3 + rt * math.log10(t / 3),
            "units": {"C3": "dimensionless"},
            "source": _source("Eq. 7-34", 178),
            "valid_for": "Burland and Burbidge method (Table 7-9).",
            "notes": ("Static loads R3 = 0.3, Rt = 0.2; fluctuating loads "
                      "R3 = 0.7, Rt = 0.8 (conservative, paragraph 7-13g).")}


def equation_7_29_burland_burbidge_settlement(state: str, q: float,
                                              sigma_zo_mean: float,
                                              sigma_p: float | None,
                                              Z_I: float, I_c: float,
                                              C1: float, C2: float,
                                              C3: float) -> dict:
    """Settlement of a footing on sand or gravel by the Burland and
    Burbidge SPT method, for an axisymmetric footing corrected by C1, C2 and
    C3: normally consolidated, C1 C2 C3 (q + sigma'_zo) ZI Ic (Eq. 7-29);
    overconsolidated with q + sigma'_zo <= sigma'_p, the same with Ic/3
    (Eq. 7-30); overconsolidated with q + sigma'_zo > sigma'_p,
    C1 C2 C3 [(q + sigma'_zo) - (2/3) sigma'_p] ZI Ic (Eq. 7-31);
    sigma'_zo is the average initial vertical effective stress within ZI.
    Example C-7e follows Eq. 7-30 so.

    Print check (Eqs. 7-29 to 7-31, p. 177, typed in from the rendered
    page):

        7-29  Δ = C1 · C2 · C3 · (q + σ̅′zo) · ZI · Ic     σ̅′zo = σ′p
        7-30  δ = C1 · C2 · C3 (q + σ̅′zo) ZI (Ic/3)        (q + σ̅′zo) ≤ σ′p
        7-31  δ = C1 · C2 · C3 [(q + σ̅′z0) − (2/3) σ′p] ZI · Ic
                                                          (q + σ̅′zo) > σ′p
        here the same; 7-29 prints Δ where δ (settlement, ft) is meant

    Parameters
    ----------
    state : str
        'normally consolidated' (Eq. 7-29) or 'overconsolidated' (7-30 or
        7-31, chosen by q + sigma'_zo against sigma'_p).
    q : float
        Gross bearing pressure, tsf (or qult/FS, whichever is less).
    sigma_zo_mean : float
        Average initial vertical effective stress within ZI, tsf.
    sigma_p : float or None
        Preconsolidation stress, tsf; None for 'normally consolidated'.
    Z_I : float
        Depth of influence, ft (Eq. 7-27).
    I_c : float
        Compressibility index, 1/tsf (Eq. 7-28).
    C1, C2, C3 : float
        Shape, layer thickness and time factors (Eqs. 7-32 to 7-34).

    Returns
    -------
    dict
        settlement_ft, settlement_in, equation, units, source, valid_for,
        notes.

    Raises
    ------
    ValueError
        For an unknown state, sigma_p missing or not above sigma_zo for an
        overconsolidated soil (or given for a normally consolidated one), or
        values out of range.
    """
    st = " ".join(str(state).lower().split())
    qq = _non_negative("q", q)
    so = _positive("sigma_zo_mean", sigma_zo_mean)
    zi = _positive("Z_I", Z_I)
    ic = _positive("I_c", I_c)
    if float(C1) < 1 or float(C3) < 1 or not 0 < float(C2) <= 1:
        raise ValueError("C1 >= 1, 0 < C2 <= 1 and C3 >= 1 (Eqs. 7-32 to 7-34)")
    k = C1 * C2 * C3
    if st == "normally consolidated":
        if sigma_p is not None:
            raise ValueError("sigma_p is not used for a normally consolidated "
                             "soil (Eq. 7-29 has sigma'_zo = sigma'_p)")
        ft, eq = k * (qq + so) * zi * ic, "7-29"
    elif st == "overconsolidated":
        if sigma_p is None:
            raise ValueError("give sigma_p for an overconsolidated soil")
        sp = _positive("sigma_p", sigma_p)
        if sp <= so:
            raise ValueError("sigma_p must exceed sigma_zo for an "
                             "overconsolidated soil")
        if qq + so <= sp:
            ft, eq = k * (qq + so) * zi * ic / 3, "7-30"
        else:
            ft, eq = k * ((qq + so) - 2 / 3 * sp) * zi * ic, "7-31"
    else:
        raise ValueError(f"Unknown state {state!r}: 'normally consolidated' "
                         f"or 'overconsolidated'")
    out = _settlement(ft)
    out.update({"equation": eq, "units": dict(_SETTLEMENT_UNITS),
                "source": _source(f"Eq. {eq}", 177),
                "valid_for": ("Sands and gravels; equations for axisymmetric "
                              "footings (L/B = 1) with C1 for other shapes "
                              "(paragraphs 7-13d, 7-13e)."),
                "notes": ("As printed, the stress term is (q + sigma'_zo), "
                          "q the gross bearing pressure, and Eq. 7-29's left "
                          "side is printed as a capital delta.")})
    return out


# ---------------------------------------------------------------------------
# Excavation rebound, time rate, secondary compression
# ---------------------------------------------------------------------------

def equation_7_35_excavation_unloading(gamma_t: float, D: float,
                                       I_sigma: float,
                                       sigma_zgw: float) -> dict:
    """Stress relief from an excavation and the vertical effective stress
    after it: q'exc = gamma_t D (Eq. 7-35), delta_sigma_z,exc = I_sigma
    q'exc (Eq. 7-36), sigma'_z,exc = sigma'_z,gw - delta_sigma_z,exc
    (Eq. 7-37).

    Print check (Eqs. 7-35 to 7-37, p. 181, typed in from the rendered
    page):

        7-35  q′exc = γt · D
        7-36  Δσzexc = Iσ(q′exc)
        7-37  σ′zexc = σ′zgw − Δσzexc
        here the same

    Parameters
    ----------
    gamma_t : float
        Total unit weight of the soil removed, tcf.
    D : float
        Depth of excavation, ft.
    I_sigma : float
        Influence factor for vertical stress at the point (paragraph 6-7).
    sigma_zgw : float
        Vertical effective stress after dewatering, tsf.

    Returns
    -------
    dict
        q_exc, delta_sigma_z_exc, sigma_z_exc, units, source, valid_for,
        notes.

    Raises
    ------
    ValueError
        If a value is out of range or the unloading exceeds sigma_zgw.
    """
    q = _non_negative("gamma_t", gamma_t) * _non_negative("D", D)
    i = float(I_sigma)
    if not 0 <= i <= 1:
        raise ValueError(f"I_sigma = {I_sigma}: give 0 to 1")
    ds = i * q
    s = _non_negative("sigma_zgw", sigma_zgw) - ds
    if s < 0:
        raise ValueError("the unloading exceeds sigma'_zgw")
    return {"q_exc": q, "delta_sigma_z_exc": ds, "sigma_z_exc": s,
            "units": {"q_exc": "tsf", "delta_sigma_z_exc": "tsf",
                      "sigma_z_exc": "tsf"},
            "source": _source("Eqs. 7-35 to 7-37", 181),
            "valid_for": "Excavation rebound (Table 7-10).", "notes": ""}


def equation_7_38_void_ratio_change_settlement(H: float, delta_e: float,
                                               e: float, kind: str) -> dict:
    """Movement of a layer from the change of its void ratio read off the
    oedometer curve: rebound R = H delta_e/(1 + e_zo) (Eq. 7-38,
    delta_e = e_zo - e_zexc, Table 7-10, Step 7) or recompression
    settlement delta_r = H delta_e/(1 + e_zexc) (Eq. 7-40,
    delta_e = e_zexc - e_zf).

    Print check (Eqs. 7-38 and 7-40, pp. 182-183, typed in from the
    rendered pages):

        7-38  R = H (Δe/(1 + ezo))         Δe = ezo − ezexc
        7-40  δr = H (Δe/(1 + ezexc))      Δe = ezExc − ezf
        here the same; 7-38's list of symbols gives R and H as stresses
        (tsf), as printed: R is the rebound and H the layer thickness (ft)
        as Table 7-10, Step 7 and Eq. 7-40 use them

    Parameters
    ----------
    H : float
        Layer thickness, ft.
    delta_e : float
        Change of void ratio (positive).
    e : float
        Void ratio in the denominator: e_zo (rebound) or e_zexc
        (recompression).
    kind : str
        'rebound' (Eq. 7-38) or 'recompression' (Eq. 7-40).

    Returns
    -------
    dict
        movement_ft, movement_in, equation, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown kind or a value out of range.
    """
    k = str(kind).lower().strip()
    if k not in ("rebound", "recompression"):
        raise ValueError(f"Unknown kind {kind!r}: 'rebound' or 'recompression'")
    ft = _positive("H", H) * _non_negative("delta_e", delta_e) / (
        1 + _non_negative("e", e))
    eq, page = ("7-38", 182) if k == "rebound" else ("7-40", 183)
    return {"movement_ft": ft, "movement_in": ft * 12, "equation": eq,
            "units": {"movement_ft": "ft", "movement_in": "in"},
            "source": _source(f"Eq. {eq}", page),
            "valid_for": "Excavation rebound and recompression (Table 7-10).",
            "notes": ("As printed, the list of symbols of Eq. 7-38 defines "
                      "R and H as vertical effective stresses (tsf).")}


def equation_7_41_settlement_at_time(U_percent: float,
                                     delta_c: float) -> dict:
    """Primary consolidation settlement reached at a time, the average
    degree of consolidation times the full primary settlement,
    delta_ct = (U%/100) delta_c.

    Print check (Eq. 7-41, p. 184, typed in from the rendered page):

        printed    δct = (U%/100) δc
        here       the same

    Parameters
    ----------
    U_percent : float
        Average degree of consolidation, percent (0 to 100).
    delta_c : float
        Primary consolidation settlement, in (Eqs. 7-7 to 7-9).

    Returns
    -------
    dict
        delta_ct, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If U is outside 0 to 100 or delta_c < 0.
    """
    u = float(U_percent)
    if not 0 <= u <= 100:
        raise ValueError(f"U_percent = {U_percent}: give 0 to 100")
    return {"delta_ct": u / 100 * _non_negative("delta_c", delta_c),
            "units": {"delta_ct": "in (the units of delta_c)"},
            "source": _source("Eq. 7-41", 184),
            "valid_for": "Time rate of consolidation (Table 7-11).",
            "notes": ""}


def equation_7_42_time_for_consolidation(T_v: float, H_dr: float,
                                         cv_ft2_per_day: float) -> dict:
    """Time for a degree of consolidation by vertical drainage,
    t = Tv Hdr^2/Cv, Tv from Figure 7-16 (``figures``), Hdr the longest
    drainage distance in ft (half the layer for drainage at top and
    bottom), Cv in ft^2/day.

    Print check (Eq. 7-42, p. 184, typed in from the rendered page):

        printed    t = (Tv · Hdr^2)/Cv
        here       the same

    Parameters
    ----------
    T_v : float
        Time factor for vertical drainage (Figure 7-16).
    H_dr : float
        Longest distance to a drainage boundary, ft.
    cv_ft2_per_day : float
        Coefficient of consolidation in ft^2/day, as p. 184 lists it. The
        oedometer equations 7-43 and 7-44 give Cv in in^2/day: pass their
        ``cv_ft2_per_day``, not ``cv_in2_per_day`` (that would give a time
        144 times too short).

    Returns
    -------
    dict
        t_days, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If T_v < 0 or H_dr or cv_ft2_per_day is not positive.
    """
    return {"t_days": _non_negative("T_v", T_v) * _positive("H_dr", H_dr) ** 2
            / _positive("cv_ft2_per_day", cv_ft2_per_day),
            "units": {"t_days": "days"},
            "source": _source("Eq. 7-42", 184),
            "valid_for": ("Vertical drainage, linear initial excess pore "
                          "pressure with depth (Figure 7-16)."),
            "notes": ("Hdr = H/2 for two-way drainage, H for one-way (p. "
                      "184). Cv is in ft^2/day (p. 184); Eqs. 7-43 and 7-44 "
                      "give it in in^2/day and ft^2/day.")}


def equation_7_43_coefficient_of_consolidation(method: str, H_dr: float,
                                               t: float) -> dict:
    """Coefficient of consolidation from an oedometer stress increment:
    Casagrande's log-time method, Cv = T50 Hdr^2/t50 with T50 = 0.197
    (Eq. 7-43, Table 7-12), or Taylor's square-root-of-time method,
    Cv = T90 Hdr^2/t90 with T90 = 0.848 (Eq. 7-44, Table 7-13). The root-time
    method typically gives higher values; both give bounds (7-18c). With
    Hdr in inches the result is in in^2/day, as pp. 186 and 188 print; it
    comes back in ft^2/day too (/144), the unit Eq. 7-42 takes.

    Print check (Eqs. 7-43 and 7-44, pp. 186 and 188, typed in from the
    rendered pages):

        7-43  Cv = T50 (Hdr)^2/t50     T50 = 0.197
        7-44  Cv = T90 (Hdr)^2/t90     T90 = 0.848
        here the same

    Parameters
    ----------
    method : str
        'log time' (Eq. 7-43) or 'root time' (Eq. 7-44).
    H_dr : float
        Longest drainage distance of the specimen, in (half its height for
        two-way drainage).
    t : float
        t50 or t90, days.

    Returns
    -------
    dict
        cv_in2_per_day, cv_ft2_per_day, T, equation, units, source,
        valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown method or a value not positive.
    """
    m = str(method).lower().replace("-", " ").strip()
    if m == "log time":
        T, eq, page = 0.197, "7-43", 186
    elif m == "root time":
        T, eq, page = 0.848, "7-44", 188
    else:
        raise ValueError(f"Unknown method {method!r}: 'log time' or "
                         f"'root time'")
    cv = T * _positive("H_dr", H_dr) ** 2 / _positive("t", t)
    return {"cv_in2_per_day": cv, "cv_ft2_per_day": cv / 144.0,
            "T": T, "equation": eq,
            "units": {"cv_in2_per_day": "in^2/day",
                      "cv_ft2_per_day": "ft^2/day"},
            "source": _source(f"Eq. {eq}", page),
            "valid_for": "Laboratory oedometer time-deformation data.",
            "notes": (f"Eq. {eq} (p. {page}) gives Cv in in^2/day with Hdr "
                      f"in inches. Eq. 7-42 (p. 184) takes Cv in ft^2/day: "
                      f"pass cv_ft2_per_day (in^2/day / 144); passing "
                      f"cv_in2_per_day gives a time 144 times too short.")}


def equation_7_45_void_ratio_from_dial(H0: float, e0: float, d0: float,
                                       dt: float) -> dict:
    """Void ratio of an oedometer specimen at a dial reading,
    e = ((H0 - Hs) - (d0 - dt))/Hs with Hs = H0/(1 + e0) the height of
    solids. Give the dial readings in inches (the print reads them in units
    of 10^-4 inch).

    Print check (Eq. 7-45, p. 190, typed in from the rendered page):

        printed    e = ((H0 − Hs) − (d0 − dt))/Hs,  Hs = H0/(1 + e0)
        here       the same, all lengths in inches

    Parameters
    ----------
    H0 : float
        Original height of the specimen, in.
    e0 : float
        Initial void ratio.
    d0 : float
        Initial dial reading, in.
    dt : float
        Dial reading at time t, in.

    Returns
    -------
    dict
        e, H_s, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If H0 is not positive or e0 < 0.
    """
    h0 = _positive("H0", H0)
    hs = h0 / (1 + _non_negative("e0", e0))
    return {"e": ((h0 - hs) - (float(d0) - float(dt))) / hs, "H_s": hs,
            "units": {"e": "dimensionless", "H_s": "in"},
            "source": _source("Eq. 7-45", 190),
            "valid_for": "Table 7-14, Step 1.",
            "notes": "The print lists d0 and dt in units of 10^-4 inch."}


def equation_7_46_secondary_compression_index(e1: float, e2: float,
                                              t1: float, t2: float) -> dict:
    """Coefficient of secondary compression from the void ratio against
    log-time after primary consolidation, C_alpha = (e1 - e2)/log10(t2/t1).

    Print check (Eq. 7-46, p. 191, typed in from the rendered page):

        printed    Cα = (e1 − e2)/log10(t2 lab/t1 lab)
        here       the same

    Parameters
    ----------
    e1, e2 : float
        Void ratios at t1 and t2.
    t1, t2 : float
        Laboratory times, minutes (t2 > t1, typically one log cycle).

    Returns
    -------
    dict
        C_alpha, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If the times are not positive and increasing, or e2 > e1 (a void
        ratio that rises with time gives a negative C_alpha; refused, as
        equation 7-5 refuses a rising void ratio: the library's reading,
        the page printing no condition on it).
    """
    a = _positive("t1", t1)
    b = _positive("t2", t2)
    if b <= a:
        raise ValueError("t2 must exceed t1")
    if float(e2) > float(e1):
        raise ValueError(
            f"e2 ({e2}) is above e1 ({e1}): Eq. 7-46 (p. 191) is the "
            f"coefficient of secondary compression, e1 and e2 the void ratios "
            f"at t1 and the later t2; a void ratio that rises with time gives "
            f"a negative C_alpha. The page prints no condition on e2 against "
            f"e1; the library refuses it (its reading)")
    return {"C_alpha": (e1 - e2) / math.log10(b / a),
            "units": {"C_alpha": "dimensionless"},
            "source": _source("Eq. 7-46", 191),
            "valid_for": "Table 7-14, Step 3.", "notes": ""}


def equation_7_47_secondary_settlement(C_alpha: float, e_p: float, H: float,
                                       t1: float, t2: float) -> dict:
    """Secondary compression settlement of a layer,
    delta_s = (C_alpha/(1 + e_p)) H log10(t2/t1), from the end of primary
    consolidation in the field (t1) to the time of interest (t2).

    Print check (Eq. 7-47, p. 191, typed in from the rendered page):

        printed    δs = (C∝/(1 + ep)) H · log10(t2/t1)
        here       the same (C∝, a proportional-to sign as printed, is Cα)

    Parameters
    ----------
    C_alpha : float
        Coefficient of secondary compression (Eq. 7-46).
    e_p : float
        Void ratio at the end of primary consolidation.
    H : float
        Thickness of the compressible layer, ft.
    t1 : float
        Time to complete primary consolidation in the field, minutes
        (Eq. 7-42).
    t2 : float
        Service life or other time of interest, minutes.

    Returns
    -------
    dict
        settlement_ft, settlement_in, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a value is out of range or t2 <= t1.
    """
    a = _positive("t1", t1)
    b = _positive("t2", t2)
    if b <= a:
        raise ValueError("t2 must exceed t1")
    ft = (_non_negative("C_alpha", C_alpha) / (1 + _non_negative("e_p", e_p))
          * _positive("H", H) * math.log10(b / a))
    out = _settlement(ft)
    out.update({"units": dict(_SETTLEMENT_UNITS),
                "source": _source("Eq. 7-47", 191),
                "valid_for": "Secondary compression (Table 7-14).",
                "notes": "The print sets the coefficient as C∝ here."})
    return out
