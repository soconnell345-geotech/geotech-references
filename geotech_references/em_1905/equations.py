"""EM 1110-1-1905 (2025) equations of Chapter 5 (ultimate limit states:
bearing pressure, eccentricity, bearing capacity, punching, groundwater, in
situ test methods, sliding, uplift) as functions, each the formula typed in
from the rendered page (manifest ``printed_equations``) and checked against
it. ``settlement.py`` holds Chapters 6 and 7.

Units are the manual's: ft, kips (kips/ft for a continuous footing), ksf,
kcf, degrees. Each function returns a dict with its values, ``units``,
``source`` (equation and printed page), ``valid_for`` and ``notes``, and
raises ValueError for a value outside what the equation covers. A limit
printed as part of a relation ("dc <= 1.5", "Pa,d >= 0") is applied as
printed: the limited value is returned, with the formula's value beside it
(``dc_unlimited``, ``P_ad_unlimited``), ``limit_governs`` and a note quoting
the page. Where a function refuses an input the page prints no condition
on (beta above phi' in Table 5-3, for one), the message and docstring say
it is the library's reading, not a printed condition. A min[] or max[]
inside a formula is computed as printed.

``ultimate_bearing_capacity_drained`` and
``ultimate_bearing_capacity_undrained`` follow the steps of the worked
examples of Appendix B (Tables B-1a to B-7b): the factors of Tables 5-2 to
5-4 by the chosen method, then equation 5-22.
"""

from __future__ import annotations

import math

from geotech_references.em_1905 import tables as _t

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


# ---------------------------------------------------------------------------
# 5-2 Bearing pressure
# ---------------------------------------------------------------------------

def equation_5_1_vertical_load(Q: float, Wf: float) -> dict:
    """Downward vertical load a footing puts on the ground: the column load
    plus the weight of the foundation, including the soil above the bearing
    elevation, V = Q + Wf.

    Print check (Eq. 5-1, p. 93, typed in from the rendered page):

        printed    V = Q + Wf
        here       V = Q + Wf

    Parameters
    ----------
    Q : float
        Vertical column load, kips (kips/ft for a continuous footing);
        positive in compression, negative in uplift.
    Wf : float
        Weight of the foundation including the soil above the bearing
        elevation, kips (kips/ft).

    Returns
    -------
    dict
        V, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If Wf < 0.
    """
    _non_negative("Wf", Wf)
    return {"V": float(Q) + float(Wf),
            "units": {"V": "kips (kips/ft for a continuous footing)"},
            "source": _source("Eq. 5-1", 93),
            "valid_for": "Isolated spread and continuous footings.",
            "notes": "Q is positive in compression and negative in uplift."}


def equation_5_2_equivalent_bearing_pressure(Q: float, Wf: float,
                                             B_eff: float,
                                             L_eff: float | None,
                                             u_d: float) -> dict:
    """Gross equivalent bearing pressure under a footing: the column load
    plus the foundation weight over the effective area, less the pore
    pressure at the base, qeq = (Q + Wf)/A' - ud for an isolated spread
    footing (Eq. 5-2) and (Q + Wf)/B' - ud for a continuous footing
    (Eq. 5-3). With no eccentricity B' = B, A' = A and qeq is the gross
    bearing pressure q.

    Print check (Eqs. 5-2 and 5-3, pp. 93-94, typed in from the rendered
    pages):

        5-2  qeq = (Q + Wf)/A′ − ud = V/A′ − ud = V/(B′ · L′) − ud
        5-3  qeq = (Q + Wf)/B′ − ud = V/B′ − ud
        here the same

    Parameters
    ----------
    Q : float
        Vertical column load, kips (kips/ft for a continuous footing).
    Wf : float
        Foundation weight including soil above the bearing elevation, kips
        (kips/ft).
    B_eff : float
        Effective width B', ft (B with no eccentricity).
    L_eff : float or None
        Effective length L', ft; None for a continuous footing (Eq. 5-3).
    u_d : float
        Pore water pressure at the base of the foundation, ksf; 0 where the
        groundwater table is at or below the base.

    Returns
    -------
    dict
        q_eq, V, A_eff (isolated), equation, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If Wf < 0, u_d < 0, or B' or L' is not positive.
    """
    _non_negative("Wf", Wf)
    u = _non_negative("u_d", u_d)
    B = _positive("B_eff", B_eff)
    V = float(Q) + float(Wf)
    out = {"V": V}
    if L_eff is None:
        out.update(q_eq=V / B - u, equation="5-3 (continuous footing)")
        page = 94
    else:
        A = B * _positive("L_eff", L_eff)
        out.update(q_eq=V / A - u, A_eff=A,
                   equation="5-2 (isolated spread footing)")
        page = 93
    out.update({
        "units": {"q_eq": "ksf", "V": "kips (kips/ft)", "A_eff": "ft^2"},
        "source": _source("Eq. 5-2" if L_eff is not None else "Eq. 5-3", page),
        "valid_for": "Isolated spread (5-2) and continuous (5-3) footings.",
        "notes": ("Gross equivalent bearing pressure; with no eccentricity "
                  "A = A', B = B' and q = qeq (paragraph 5-2b)."),
    })
    return out


# ---------------------------------------------------------------------------
# 5-4 Eccentricity
# ---------------------------------------------------------------------------

def equation_5_4_effective_dimensions(B: float, L: float | None, V: float,
                                      M_B: float, M_L: float) -> dict:
    """Effective width, length and area of a rectangular or continuous
    footing under an eccentric load: eB = MB/V, eL = ML/V, B' = B - 2 eB,
    L' = L - 2 eL, A' = B' L'. Also says whether the resultant stays within
    the middle third (eB <= B/6, eL <= L/6), which Table 2-1, note 3,
    requires in place of a factor of safety against overturning.

    Print check (Eqs. 5-4 to 5-8, p. 96, typed in from the rendered page):

        5-4  B′ = B − 2 · eB        5-5  eB = MB/V
        5-6  L′ = L − 2 · eL        5-7  eL = ML/V
        5-8  A′ = B′ · L′
        here the same

    Parameters
    ----------
    B : float
        Footing width, ft.
    L : float or None
        Footing length, ft; None for a continuous footing (M_L must be 0).
    V : float
        Vertical load on the ground, kips (kips/ft), Eq. 5-1.
    M_B : float
        Moment causing eccentricity across the width, kip-ft (kip-ft/ft).
    M_L : float
        Moment causing eccentricity along the length, kip-ft.

    Returns
    -------
    dict
        e_B, e_L, B_eff, L_eff, A_eff, within_middle_third, units, source,
        valid_for, notes.

    Raises
    ------
    ValueError
        If B, L or V is not positive, a moment is negative, M_L is given for
        a continuous footing, or an effective dimension is not positive.
    """
    B = _positive("B", B)
    V = _positive("V", V)
    eB = _non_negative("M_B", M_B) / V
    Be = B - 2 * eB
    if Be <= 0:
        raise ValueError(f"B' = B - 2 eB = {Be:.3f} ft: the resultant is "
                         f"outside the footing")
    out = {"e_B": eB, "B_eff": Be}
    mid = eB <= B / 6
    if L is None:
        if float(M_L) != 0:
            raise ValueError("A continuous footing has no length to take M_L")
        out.update(e_L=0.0, L_eff=None, A_eff=None)
    else:
        Lf = _positive("L", L)
        eL = _non_negative("M_L", M_L) / V
        Le = Lf - 2 * eL
        if Le <= 0:
            raise ValueError(f"L' = L - 2 eL = {Le:.3f} ft: the resultant is "
                             f"outside the footing")
        out.update(e_L=eL, L_eff=Le, A_eff=Be * Le)
        mid = mid and eL <= Lf / 6
    out.update({
        "within_middle_third": mid,
        "units": {"e_B": "ft", "e_L": "ft", "B_eff": "ft", "L_eff": "ft",
                  "A_eff": "ft^2"},
        "source": _source("Eqs. 5-4 to 5-8", 96),
        "valid_for": "Rectangular and continuous footings (paragraph 5-4a).",
        "notes": ("The manual defines B' as the effective base width and L' "
                  "as the effective base length (pp. 96, 106) and does not "
                  "say which is the lesser. The library takes B' as the "
                  "lesser (its convention, not printed): if L' comes out "
                  "less than B', swap them before Tables 5-2 to 5-4, whose "
                  "functions refuse L' < B'. The middle-third check is "
                  "Table 2-1, note 3."),
    })
    return out


def equation_5_9_circular_effective_footing(A: float, e: float) -> dict:
    """Effective rectangle for a circular (or approximately circular)
    footing under an eccentric load: the equivalent radius Req = sqrt(A/pi),
    the effective area A' of the circle segment, the equivalent ellipse
    Beq = 2(Req - e) and Leq, and the rectangle L' = sqrt(A' Leq/Beq),
    B' = L' Beq/Leq used in the bearing capacity equations.

    Print check (Eqs. 5-9 to 5-14, p. 98, typed in from the rendered page):

        5-9   Req = √(A/π)
        5-10  A′ = 2 [Req^2 cos^(−1)(e/Req) − e √(Req^2 − e^2)]
        5-11  Beq = 2(Req − e)
        5-12  Leq = 2 Req √(1 − (1 − Beq/(2Req))^2)
        5-13  L′ = √(A′ (Leq/Beq))
        5-14  B′ = L′ (Beq/Leq)
        here the same (cos^-1 in radians)

    Parameters
    ----------
    A : float
        Base area of the footing, ft^2.
    e : float
        Eccentricity, ft.

    Returns
    -------
    dict
        R_eq, A_eff, B_eq, L_eq, L_eff, B_eff, units, source, valid_for,
        notes.

    Raises
    ------
    ValueError
        If A is not positive, e < 0, or e >= Req.
    """
    A = _positive("A", A)
    e = _non_negative("e", e)
    R = math.sqrt(A / math.pi)
    if e >= R:
        raise ValueError(f"e = {e} ft is not less than Req = {R:.3f} ft")
    Ae = 2 * (R ** 2 * math.acos(e / R) - e * math.sqrt(R ** 2 - e ** 2))
    Beq = 2 * (R - e)
    Leq = 2 * R * math.sqrt(1 - (1 - Beq / (2 * R)) ** 2)
    Le = math.sqrt(Ae * Leq / Beq)
    return {
        "R_eq": R, "A_eff": Ae, "B_eq": Beq, "L_eq": Leq, "L_eff": Le,
        "B_eff": Le * Beq / Leq,
        "units": {"R_eq": "ft", "A_eff": "ft^2", "B_eq": "ft", "L_eq": "ft",
                  "L_eff": "ft", "B_eff": "ft"},
        "source": _source("Eqs. 5-9 to 5-14", 98),
        "valid_for": ("Circular or approximately circular footings with "
                      "eccentric loading (paragraph 5-4b)."),
        "notes": "",
    }


# ---------------------------------------------------------------------------
# 5-5 Bearing capacity
# ---------------------------------------------------------------------------

def equation_5_17_punching_capacity(q_ult_1: float, q_ult_2: float,
                                    H_s: float, B_eff: float,
                                    L_eff: float | None, B: float,
                                    L: float | None) -> dict:
    """Ultimate bearing capacity of a footing on a strong layer over a weak
    one: the lesser of the capacity in the strong surface layer and the
    weak layer's capacity raised by 2V:1H load spreading through the strong
    layer, qult = min(qult,1, (B' + Hs)(L' + Hs)/(B L) qult,2) for an
    isolated footing (Eq. 5-17) and min(qult,1, (B' + Hs)/B' qult,2) for a
    continuous footing (Eq. 5-18).

    Print check (Eqs. 5-17 and 5-18, p. 102, typed in from the rendered
    page):

        5-17  qult = min(qult,1, (((B′ + Hs) · (L′ + Hs))/(B · L)) qult,2)
        5-18  qult = min(qult,1, ((B′ + Hs)/B′) qult,2)
        here the same; 5-17's denominator is B · L without primes, as
        printed, and the list of symbols does not define B or L

    Parameters
    ----------
    q_ult_1 : float
        Ultimate bearing capacity with the strength of the strong surface
        layer, ksf.
    q_ult_2 : float
        Ultimate bearing capacity with the strength of the weak underlying
        layer, ksf.
    H_s : float
        Thickness of the strong surface layer below the footing, ft.
    B_eff : float
        Effective width B', ft.
    L_eff : float or None
        Effective length L', ft; None for a continuous footing (Eq. 5-18).
    B : float
        Footing width, ft (Eq. 5-17's denominator; not used by 5-18).
    L : float or None
        Footing length, ft; None for a continuous footing.

    Returns
    -------
    dict
        q_ult, spreading_factor, governs ('strong layer' or 'punching'),
        units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a capacity or dimension is not positive, H_s < 0, or L / L_eff
        is given for one footing type and not the other.
    """
    q1 = _positive("q_ult_1", q_ult_1)
    q2 = _positive("q_ult_2", q_ult_2)
    Hs = _non_negative("H_s", H_s)
    Be = _positive("B_eff", B_eff)
    if (L_eff is None) != (L is None):
        raise ValueError("Give both L and L_eff (isolated footing) or neither "
                         "(continuous footing)")
    if L_eff is None:
        f = (Be + Hs) / Be
        eq, src = "5-18", _source("Eq. 5-18", 102)
    else:
        f = ((Be + Hs) * (_positive("L_eff", L_eff) + Hs)
             / (_positive("B", B) * _positive("L", L)))
        eq, src = "5-17", _source("Eq. 5-17", 102)
    qp = f * q2
    return {
        "q_ult": min(q1, qp), "q_ult_punching": qp, "spreading_factor": f,
        "governs": "punching" if qp < q1 else "strong layer",
        "equation": eq,
        "units": {"q_ult": "ksf", "q_ult_punching": "ksf",
                  "spreading_factor": "dimensionless"},
        "source": src,
        "valid_for": ("A strong surface layer over a weak layer within the "
                      "shear zone (paragraph 5-5a(2)); 2V:1H spreading."),
        "notes": ("As printed, Eq. 5-17's denominator is B · L, without "
                  "primes, and its list of symbols does not define B or L."),
    }


def equation_5_19_effective_unit_weight(gamma_t: float, D_w: float,
                                        D_f: float, B: float,
                                        method: str) -> dict:
    """Effective unit weight of the soil in the shear zone with the water
    table at or below the footing: gamma' = gamma_t min[0.45 + 0.55
    max(Dw - Df, 0)/B, 1] (USACE, Eq. 5-19) or gamma_t CW-gamma = gamma_t
    min[0.5 + 0.5 Dw/(1.5B + Df), 1] (FHWA 2002, Eq. 5-20).

    Print check (Eqs. 5-19 and 5-20, p. 103, typed in from the rendered
    page):

        5-19  γ′ ≈ γt · min[0.45 + 0.55 (max(DW − Df, 0)/B), 1]
        5-20  γ′ ≈ γt · CWγ = γt · min[0.5 + 0.5 (DW/(1.5B + Df)), 1]
        here the same

    Parameters
    ----------
    gamma_t : float
        Total unit weight of the soil beneath the footing, kcf.
    D_w : float
        Depth of the groundwater table below the ground surface, ft.
    D_f : float
        Depth of the footing base below the ground surface, ft.
    B : float
        Footing width, ft.
    method : str
        'usace' (Eq. 5-19) or 'fhwa' (Eq. 5-20; 'aashto' is taken as the
        same).

    Returns
    -------
    dict
        gamma_eff, ratio (gamma'/gamma_t), equation, units, source,
        valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown method or values out of range.
    """
    m = _t._method(method)
    g = _positive("gamma_t", gamma_t)
    Dw = _non_negative("D_w", D_w)
    Df = _non_negative("D_f", D_f)
    B = _positive("B", B)
    if m == "usace":
        ratio = min(0.45 + 0.55 * (max(Dw - Df, 0) / B), 1.0)
        eq, src = "5-19", _source("Eq. 5-19", 103)
    else:
        ratio = min(0.5 + 0.5 * (Dw / (1.5 * B + Df)), 1.0)
        eq, src = "5-20 (FHWA 2002)", _source("Eq. 5-20", 103)
    return {
        "gamma_eff": g * ratio, "ratio": ratio, "equation": eq,
        "units": {"gamma_eff": "kcf", "ratio": "dimensionless"},
        "source": src,
        "valid_for": ("Groundwater in the shear zone below the footing "
                      "(paragraph 5-5a(5)); the surcharge q0 takes the "
                      "effective stress at the base for phi' > 0 (5-5c)."),
        "notes": "",
    }


def equation_5_22_ultimate_bearing_capacity(
        c: float, q0: float, gamma_eff: float, B_eff: float,
        Nc: float, Nq: float, N_gamma: float,
        sc: float, dc: float, ic: float, bc: float, gc: float,
        sq: float, dq: float, iq: float, bq: float, gq: float,
        s_gamma: float, d_gamma: float, i_gamma: float, b_gamma: float,
        g_gamma: float) -> dict:
    """The general bearing capacity equation with its correction factors
    for shape, depth, load inclination, base inclination and ground
    inclination: qult = sc dc ic bc gc c Nc + sq dq iq bq gq q0 Nq +
    s-gamma d-gamma i-gamma b-gamma g-gamma (1/2) B' gamma' N-gamma. With
    every factor 1 it is Eq. 5-21 for a continuous footing. The factors come
    from Tables 5-2 to 5-4 (``tables``); for undrained analysis c = su,
    Nq = 1, N-gamma = 0 and the q factors are 1.

    Print check (Eqs. 5-21 and 5-22, pp. 104-105, typed in from the
    rendered pages):

        5-21  qult = c · Nc + q0 · Nq + (1/2) B · γ′ · Nγ   (Continuous)
        5-22  qult = sc dc ic bc gc c Nc + sq dq iq bq gq q0 Nq
                     + sγ dγ iγ bγ gγ (1/2) B′ γ′ Nγ
        here the same

    Parameters
    ----------
    c : float
        Cohesion of the soil in the shear zone, ksf (su for undrained).
    q0 : float
        Surcharge pressure at the base of the footing, ksf.
    gamma_eff : float
        Effective unit weight of the soil beneath the footing, kcf.
    B_eff : float
        Effective width B', ft.
    Nc, Nq, N_gamma : float
        Bearing capacity factors (Table 5-2 or 5-4).
    sc, dc, ic, bc, gc : float
        Correction factors on the c term.
    sq, dq, iq, bq, gq : float
        Correction factors on the q0 term.
    s_gamma, d_gamma, i_gamma, b_gamma, g_gamma : float
        Correction factors on the gamma term.

    Returns
    -------
    dict
        q_ult, c_term, q_term, gamma_term, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If c, q0, gamma', a bearing factor or a correction factor is
        negative, or B' is not positive.
    """
    for name, v in (("c", c), ("q0", q0), ("gamma_eff", gamma_eff),
                    ("Nc", Nc), ("Nq", Nq), ("N_gamma", N_gamma)):
        _non_negative(name, v)
    B = _positive("B_eff", B_eff)
    facs = (sc, dc, ic, bc, gc, sq, dq, iq, bq, gq,
            s_gamma, d_gamma, i_gamma, b_gamma, g_gamma)
    for name, v in zip(("sc", "dc", "ic", "bc", "gc", "sq", "dq", "iq", "bq",
                        "gq", "s_gamma", "d_gamma", "i_gamma", "b_gamma",
                        "g_gamma"), facs):
        _non_negative(name, v)
    ct = sc * dc * ic * bc * gc * c * Nc
    qt = sq * dq * iq * bq * gq * q0 * Nq
    gt = s_gamma * d_gamma * i_gamma * b_gamma * g_gamma * 0.5 * B * gamma_eff * N_gamma
    return {
        "q_ult": ct + qt + gt, "c_term": ct, "q_term": qt, "gamma_term": gt,
        "units": {"q_ult": "ksf", "c_term": "ksf", "q_term": "ksf",
                  "gamma_term": "ksf"},
        "source": _source("Eq. 5-22", 105),
        "valid_for": ("General shear; the factors of Tables 5-2 to 5-4 by "
                      "one method (paragraph 5-5f)."),
        "notes": ("The manual recommends both methods and the average of "
                  "the results when bearing capacity controls design "
                  "(paragraph 5-5e)."),
    }


def ultimate_bearing_capacity_drained(method: str, phi_deg: float, c: float,
                                      q0: float, gamma_eff: float,
                                      B_eff: float, L_eff: float | None,
                                      Df: float, H: float, V: float,
                                      theta_deg: float | None,
                                      alpha_b_deg: float, alpha_g_deg: float,
                                      d_g: float | None) -> dict:
    """Drained ultimate bearing capacity of a shallow footing by one of the
    manual's two methods, as the worked examples of Appendix B compute it:
    the bearing capacity factors and the shape and depth factors of Table
    5-2, the load, base and ground inclination factors of Table 5-3, then
    equation 5-22. Every factor is returned, in the rows of the examples'
    summary tables.

    Print check: the factors are those of Tables 5-2 and 5-3 (pp. 107-108)
    and the equation 5-22 (p. 105), each compared with the rendered page
    (see the functions in ``tables`` and ``equation_5_22``). Checked against
    Examples B-3, B-6 and B-7 (Tables B-3c, B-6c, B-7c), USACE and FHWA
    columns.

    Parameters
    ----------
    method : str
        'usace' or 'aashto' ('fhwa' is taken as the same).
    phi_deg : float
        Friction angle phi' in the shear zone, degrees.
    c : float
        Cohesion c', ksf (0 for c = 0).
    q0 : float
        Surcharge (effective stress) at the base of the footing, ksf.
    gamma_eff : float
        Effective unit weight beneath the footing, kcf (Eq. 5-19 or 5-20).
    B_eff : float
        Effective width B', ft.
    L_eff : float or None
        Effective length L', ft; None for a continuous footing.
    Df : float
        Depth of the footing base, ft.
    H : float
        Horizontal load, kips; 0 for a vertical load.
    V : float
        Vertical load, kips (used for the load inclination).
    theta_deg : float or None
        Direction of H from the side of length L, degrees; needed by the
        AASHTO method when H > 0.
    alpha_b_deg : float
        Base inclination, degrees; 0 for a flat base.
    alpha_g_deg : float
        Ground inclination, degrees; 0 for level ground.
    d_g : float or None
        Distance to the slope, ft; needed when alpha_g > 0 (USACE only).

    Returns
    -------
    dict
        q_ult, the bearing factors (N, Nq, Nc, N_gamma) and every
        correction factor (sq ... g_gamma), limit_governs (True where the
        AASHTO dq <= 1.4 of Table 5-2 note a governs, with dq_unlimited
        then given), method, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        As the table functions and equation 5-22 do; and for a slope with
        the AASHTO/FHWA method, whose ground factors are in AASHTO (2020),
        not printed here.
    """
    m = _t._method(method)
    bf = _t.table_5_2_bearing_capacity_factors(phi_deg, m)
    if m == "usace":
        sd = _t.table_5_2_usace_shape_depth_factors(bf["N"], B_eff, L_eff, Df)
    else:
        sd = _t.table_5_2_aashto_shape_depth_factors(phi_deg, B_eff, L_eff, Df)
    if float(H) > 0:
        if m == "usace":
            inc = _t.table_5_3_usace_load_inclination_factors(H, V, phi_deg)
        else:
            if theta_deg is None:
                raise ValueError("theta_deg is needed by the AASHTO method "
                                 "when H > 0 (Figure 5-9)")
            inc = _t.table_5_3_aashto_load_inclination_factors(
                H, V, B_eff, L_eff, c, phi_deg, theta_deg)
    else:
        _non_negative("H", H)
        inc = {"iq": 1.0, "ic": 1.0, "i_gamma": 1.0}
    base = _t.table_5_3_base_inclination_factors(alpha_b_deg, phi_deg)
    if float(alpha_g_deg) > 0:
        if m != "usace":
            raise ValueError(
                "The AASHTO (2020)/FHWA (2002) ground inclination factors are "
                "'See tables in AASHTO (2020)' (Table 5-3), not printed in "
                "this manual")
        if d_g is None:
            raise ValueError("d_g is needed when alpha_g > 0")
        gr = _t.table_5_3_usace_ground_inclination_factors(
            alpha_g_deg, d_g, B_eff, phi_deg)
    else:
        _non_negative("alpha_g_deg", alpha_g_deg)
        gr = {"gq": 1.0, "gc": 1.0, "g_gamma": 1.0}
    f = {"sc": sd["sc"], "dc": sd["dc"], "ic": inc["ic"], "bc": base["bc"],
         "gc": gr["gc"], "sq": sd["sq"], "dq": sd["dq"], "iq": inc["iq"],
         "bq": base["bq"], "gq": gr["gq"], "s_gamma": sd["s_gamma"],
         "d_gamma": sd["d_gamma"], "i_gamma": inc["i_gamma"],
         "b_gamma": base["b_gamma"], "g_gamma": gr["g_gamma"]}
    q = equation_5_22_ultimate_bearing_capacity(
        c, q0, gamma_eff, B_eff, bf["Nc"], bf["Nq"], bf["N_gamma"], **f)
    out = {"q_ult": q["q_ult"], "c_term": q["c_term"], "q_term": q["q_term"],
           "gamma_term": q["gamma_term"], "N": bf["N"], "Nq": bf["Nq"],
           "Nc": bf["Nc"], "N_gamma": bf["N_gamma"]}
    out.update(f)
    governs = bool(sd.get("limit_governs", False))
    out["limit_governs"] = governs
    units = dict({"q_ult": "ksf", "c_term": "ksf", "q_term": "ksf",
                  "gamma_term": "ksf"},
                 **{k: "dimensionless" for k in
                    ["N", "Nq", "Nc", "N_gamma"] + list(f)})
    notes = ("The worked examples round each factor to two decimals before "
             "multiplying, so their qult can differ from this one in the "
             "third figure. The manual recommends both methods and the "
             "average when bearing capacity controls (paragraph 5-5e).")
    if governs:
        out["dq_unlimited"] = sd["dq_unlimited"]
        units["dq_unlimited"] = "dimensionless"
        notes += (f" The formula gives dq = {sd['dq_unlimited']:.3f}; note a "
                  f"to Table 5-2 (p. 107) limits the AASHTO (2020) dq to "
                  f"1.4, and q_ult uses dq = 1.4.")
    if str(method).lower().strip() == "fhwa":
        notes += (" Method 'fhwa' is computed as the AASHTO (2020)/FHWA "
                  "(2002) column: the dq formula and its 1.4 limit, both "
                  "applied here, are AASHTO (2020)'s, while note a to Table "
                  "5-2 (p. 107) says "
                  "FHWA (2002) presents tabulated depth factors, which this "
                  "manual does not print.")
    out.update({
        "method": bf["method"],
        "units": units,
        "source": (f"{_REF} Eq. 5-22, p. 105, with Table 5-2, p. 107 and "
                   f"Table 5-3, p. 108"),
        "valid_for": ("Drained (effective stress) analysis, phi' > 0, "
                      "general shear in a uniform shear zone; check a weak "
                      "layer below with equation 5-17 or 5-18."),
        "notes": notes,
    })
    return out


def ultimate_bearing_capacity_undrained(method: str, su: float, q0: float,
                                        B_eff: float, L_eff: float | None,
                                        Df: float, H: float, V: float,
                                        theta_deg: float | None,
                                        alpha_b_deg: float,
                                        alpha_g_deg: float,
                                        d_g: float | None) -> dict:
    """Undrained (phi = 0) ultimate bearing capacity of a shallow footing
    by one of the manual's two methods, as Examples B-1, B-2, B-4 and B-5
    compute it: qult = sc dc ic bc gc su Nc + q0, equation 5-22 with Nq = 1,
    N-gamma = 0 and the q factors 1, the factors from Table 5-4.

    Print check: Table 5-4 (p. 109) and equation 5-22 (p. 105), each
    compared with the rendered page; Example B-1 Step 3 (p. 296) prints the
    simplified form qult = sc · dc · ic · bc · gc · su · Nc + q0. Checked
    against Tables B-1b, B-2b, B-4c and B-5e, USACE and FHWA columns.

    Parameters
    ----------
    method : str
        'usace' or 'aashto' ('fhwa' is taken as the same).
    su : float
        Undrained strength c = su of the soil in the shear zone, ksf.
    q0 : float
        Total stress at the base of the footing, ksf (paragraph 5-5c).
    B_eff : float
        Effective width B', ft.
    L_eff : float or None
        Effective length L', ft; None for a continuous footing.
    Df : float
        Depth of the footing base, ft.
    H : float
        Horizontal load, kips; 0 for a vertical load.
    V : float
        Vertical load, kips.
    theta_deg : float or None
        Direction of H from the side of length L, degrees; needed by the
        AASHTO method when H > 0.
    alpha_b_deg : float
        Base inclination, degrees.
    alpha_g_deg : float
        Ground inclination, degrees.
    d_g : float or None
        Distance to the slope, ft; needed when alpha_g > 0 (USACE only).

    Returns
    -------
    dict
        q_ult, Nc, sc, dc, ic, bc, gc, limit_governs (True where the USACE
        dc <= 1.5 of Table 5-4 governs, with dc_unlimited then given),
        method, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        As ``tables.table_5_4_undrained_factors`` does (for one, a slope
        with the AASHTO/FHWA method).
    """
    f = _t.table_5_4_undrained_factors(method, B_eff, L_eff, Df, H, V, su,
                                       theta_deg, alpha_b_deg, alpha_g_deg,
                                       d_g)
    q = equation_5_22_ultimate_bearing_capacity(
        su, q0, 0.0, B_eff, f["Nc"], 1.0, 0.0,
        f["sc"], f["dc"], f["ic"], f["bc"], f["gc"],
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    out = {"q_ult": q["q_ult"]}
    out.update({k: f[k] for k in ("Nc", "sc", "dc", "ic", "bc", "gc")})
    out["limit_governs"] = f["limit_governs"]
    units = {"q_ult": "ksf", "Nc": "dimensionless", "sc": "dimensionless",
             "dc": "dimensionless", "ic": "dimensionless",
             "bc": "dimensionless", "gc": "dimensionless"}
    notes = ("The worked examples round each factor to two decimals before "
             "multiplying, so their qult can differ from this one in the "
             "third figure.")
    if f["limit_governs"]:
        out["dc_unlimited"] = f["dc_unlimited"]
        units["dc_unlimited"] = "dimensionless"
        notes += (f" The formula gives dc = {f['dc_unlimited']:.3f}; Table "
                  f"5-4 (p. 109) limits the USACE dc to 1.5, and q_ult uses "
                  f"dc = 1.5.")
    out.update({
        "method": f["method"],
        "units": units,
        "source": (f"{_REF} Eq. 5-22, p. 105, with Table 5-4, p. 109"),
        "valid_for": ("Undrained (total stress) analysis, phi = 0, c = su; "
                      "q0 is the total stress at the footing base."),
        "notes": notes,
    })
    return out


def equation_5_23_factor_of_safety(q_ult: float, q_eq: float) -> dict:
    """Calculated factor of safety against bearing capacity failure,
    FS = qult/qeq, to be compared with the minimum of Table 2-1 (3.0).

    Print check (Eq. 5-23, p. 113, typed in from the rendered page):

        printed    FS = qult/qeq
        here       FS = qult/qeq

    Parameters
    ----------
    q_ult : float
        Ultimate bearing pressure, ksf.
    q_eq : float
        Gross equivalent bearing pressure, ksf (Eq. 5-2 or 5-3).

    Returns
    -------
    dict
        FS, fs_min (Table 2-1), meets_minimum, units, source, valid_for,
        notes.

    Raises
    ------
    ValueError
        If q_ult < 0 or q_eq is not positive.
    """
    qu = _non_negative("q_ult", q_ult)
    qe = _positive("q_eq", q_eq)
    fs = qu / qe
    fs_min = _t.table_2_1_minimum_factor_of_safety("bearing capacity")["fs_min"]
    return {"FS": fs, "fs_min": fs_min, "meets_minimum": fs >= fs_min,
            "units": {"FS": "dimensionless", "fs_min": "dimensionless"},
            "source": _source("Eq. 5-23", 113),
            "valid_for": "Bearing capacity; minimum per Table 2-1 (p. 10).",
            "notes": "Table 2-1 note 1 covers allowable-stress increases."}


def equation_5_24_geometric_mean(values: list) -> dict:
    """Equivalent in situ test value in the bearing capacity shear zone:
    the geometric mean of the measured values, s = (P*L1 x P*L2 x ...
    P*Ly)^(1/y) for the net limit pressure of the PMT, and the same for
    N60 pref and the net cone tip resistance.

    Print check (Eq. 5-24, p. 114, typed in from the rendered page):

        printed    s = pne = ʸ√(P*L1 × P*L2 × … P*Ly)
        here       the y-th root of the product of the y values

    Parameters
    ----------
    values : list of float
        The measured values within the shear zone (ksf for P*L and qn;
        N60 pref in ksf for the SPT).

    Returns
    -------
    dict
        s, count, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If no values are given or one is not positive.
    """
    vals = [float(v) for v in values]
    if not vals:
        raise ValueError("give at least one value")
    for v in vals:
        _positive("each value", v)
    s = math.exp(sum(math.log(v) for v in vals) / len(vals))
    return {"s": s, "count": len(vals),
            "units": {"s": "units of the values (ksf)"},
            "source": _source("Eq. 5-24", 114),
            "valid_for": ("In situ test values within the bearing capacity "
                          "shear zone (paragraph 5-5i(2))."),
            "notes": "Also used for pne in a soft layer (Table 7-5, Step 15)."}


def equation_5_25_in_situ_bearing_capacity(drainage: str, k: float, s: float,
                                           q0: float, s_factor: float,
                                           d_factor: float, i_factor: float,
                                           b_factor: float,
                                           g_factor: float) -> dict:
    """Ultimate bearing capacity straight from in situ test results:
    qult = k sq dq iq-gamma bq gq s + q0 (drained, Eq. 5-25) or
    k sc dc ic bc gc s + q0 (undrained, Eq. 5-26), with k from Table 5-5,
    s the equivalent in situ value (Eq. 5-24) and the USACE (Meyerhof based)
    correction factors (N = 3 where no friction angle is estimated;
    iq-gamma from Eq. 5-27).

    Print check (Eqs. 5-25 and 5-26, p. 114, typed in from the rendered
    page):

        5-25  qult = k · sq · dq · iqγ · bq · gq · s + q0   (drained)
        5-26  qult = k · sc · dc · ic · bc · gc · s + q0    (undrained)
        here the same

    Parameters
    ----------
    drainage : str
        'drained' (Eq. 5-25) or 'undrained' (Eq. 5-26).
    k : float
        Bearing capacity factor, Table 5-5.
    s : float
        Equivalent in situ parameter, ksf: N60e pref, qne or pne.
    q0 : float
        Surcharge at the base of the footing, ksf.
    s_factor, d_factor, i_factor, b_factor, g_factor : float
        Shape, depth, inclination, base and ground factors: sq, dq, iq-gamma,
        bq, gq (drained) or sc, dc, ic, bc, gc (undrained).

    Returns
    -------
    dict
        q_ult, equation, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown drainage condition or a negative value.
    """
    d = str(drainage).lower().strip()
    if d not in ("drained", "undrained"):
        raise ValueError(f"Unknown drainage {drainage!r}: 'drained' or "
                         f"'undrained'")
    vals = {"k": k, "s": s, "q0": q0, "s_factor": s_factor,
            "d_factor": d_factor, "i_factor": i_factor,
            "b_factor": b_factor, "g_factor": g_factor}
    for name, v in vals.items():
        _non_negative(name, v)
    q = (k * s_factor * d_factor * i_factor * b_factor * g_factor * s + q0)
    eq = "5-25" if d == "drained" else "5-26"
    return {"q_ult": q, "equation": eq, "units": {"q_ult": "ksf"},
            "source": _source(f"Eq. {eq}", 114),
            "valid_for": ("SPT, CPT or PMT results in the shear zone; the "
                          "drainage during critical loading should match "
                          "the test's (paragraph 5-5i(3))."),
            "notes": ("Use the USACE (Meyerhof based) correction factors of "
                      "Tables 5-2 to 5-4, not Briaud's (1992) (paragraph "
                      "5-5i(4)); N = 3 where no friction angle is estimated "
                      "(p. 115).")}


def equation_5_27_in_situ_inclination_factor(Df: float, B_eff: float,
                                             iq: float,
                                             i_gamma: float) -> dict:
    """Combined load inclination factor for the drained in situ bearing
    capacity equation, weighting iq and i-gamma by the embedment:
    iq-gamma = min(Df/B', 1) iq + max(1 - Df/B', 0) i-gamma.

    Print check (Eq. 5-27, p. 114, typed in from the rendered page):

        printed    iqγ = min(Df/B′, 1) · iq + max(1 − Df/B′, 0) · iγ
        here       the same

    Parameters
    ----------
    Df : float
        Depth of the footing base, ft.
    B_eff : float
        Effective width B', ft.
    iq : float
        Load inclination factor on q (Table 5-3).
    i_gamma : float
        Load inclination factor on gamma (Table 5-3).

    Returns
    -------
    dict
        iq_gamma, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If Df < 0, B' is not positive, or a factor is negative.
    """
    r = _non_negative("Df", Df) / _positive("B_eff", B_eff)
    _non_negative("iq", iq)
    _non_negative("i_gamma", i_gamma)
    return {"iq_gamma": min(r, 1) * iq + max(1 - r, 0) * i_gamma,
            "units": {"iq_gamma": "dimensionless"},
            "source": _source("Eq. 5-27", 114),
            "valid_for": "Equation 5-25 (drained in situ method).",
            "notes": ""}


# ---------------------------------------------------------------------------
# 5-6 Sliding, 5-7 Uplift
# ---------------------------------------------------------------------------

def equation_5_29_sliding_factor_of_safety_drained(
        N: float, U: float, delta_deg: float, ca_over_c: float,
        c_eff: float, A: float, H: float, P_ad: float,
        P_pd: float) -> dict:
    """Drained factor of safety against sliding: the base friction on the
    effective normal force plus the base adhesion, over the horizontal load
    plus the developed active force less the developed passive force,
    FS = ((N - U) tan(delta') + (ca/c') c' A)/(H + Pa,d - Pp,d) (Eq. 5-29;
    Eq. 5-28 is the general form with T in the denominator).

    Print check (Eqs. 5-28 and 5-29, pp. 118-119, typed in from the rendered
    pages):

        5-28  FS = ((N − U) tan(δ′) + (ca/c′) · c′ · A)/T
        5-29  FS = ((N − U) tan(δ′) + (ca/c′) · c′ · A)/(H + Pa,d − Pp,d)
        here 5-29

    Parameters
    ----------
    N : float
        Component of the resultant force normal to the base, kips (kips/ft).
    U : float
        Water uplift force on the base, kips.
    delta_deg : float
        Interface friction angle delta', degrees.
    ca_over_c : float
        Ratio of interface adhesion to the effective cohesion intercept.
    c_eff : float
        Effective cohesion intercept c', ksf.
    A : float
        Base area, ft^2 (B x 1 ft for a continuous footing).
    H : float
        Externally applied horizontal force, kips (kips/ft).
    P_ad : float
        Developed active force on the back of the footing, kips/ft (Eq.
        5-35).
    P_pd : float
        Developed passive force on the front of the footing, kips/ft (Eq.
        5-34).

    Returns
    -------
    dict
        FS, resisting, driving, fs_min (Table 2-1), units, source,
        valid_for, notes.

    Raises
    ------
    ValueError
        If N - U < 0, a strength or area is negative, delta' is outside 0 to
        90 degrees, or the denominator is not positive.
    """
    n_eff = float(N) - _non_negative("U", U)
    if n_eff < 0:
        raise ValueError("N - U < 0: the uplift exceeds the normal force")
    dl = float(delta_deg)
    if not 0 <= dl < 90:
        raise ValueError(f"delta_deg = {delta_deg}: give 0 to 90 degrees")
    for name, v in (("ca_over_c", ca_over_c), ("c_eff", c_eff), ("A", A),
                    ("P_ad", P_ad), ("P_pd", P_pd)):
        _non_negative(name, v)
    drive = float(H) + float(P_ad) - float(P_pd)
    if drive <= 0:
        raise ValueError(f"H + Pa,d - Pp,d = {drive:.3f}: not positive")
    res = n_eff * math.tan(math.radians(dl)) + ca_over_c * c_eff * A
    return {"FS": res / drive, "resisting": res, "driving": drive,
            "fs_min": _t.table_2_1_minimum_factor_of_safety("sliding")["fs_min"],
            "units": {"FS": "dimensionless", "resisting": "kips (kips/ft)",
                      "driving": "kips (kips/ft)"},
            "source": _source("Eq. 5-29", 119),
            "valid_for": "Drained sliding (paragraph 5-6d).",
            "notes": ("Table 2-1: minimum 2.0, which may be reduced to 1.1 "
                      "for load combinations with earthquake loads.")}


def equation_5_30_sliding_factor_of_safety_undrained(
        ca_over_su: float, su: float, A: float, H: float, P_ad: float,
        P_pd: float) -> dict:
    """Undrained (phi = 0) factor of safety against sliding:
    FS = ((ca/su) A su)/(H + Pa,d - Pp,d), with H + Pa,d >= Pp,d.

    Print check (Eq. 5-30, p. 119, typed in from the rendered page):

        printed    FS = ((ca/su) · A · su)/(H + Pa,d − Pp,d)
        here       the same

    Parameters
    ----------
    ca_over_su : float
        Ratio of interface adhesion to undrained strength.
    su : float
        Undrained strength in the shear zone, ksf.
    A : float
        Base area, ft^2 (B x 1 ft for a continuous footing).
    H : float
        Externally applied horizontal force, kips (kips/ft).
    P_ad : float
        Developed active force, kips/ft (Eq. 5-35).
    P_pd : float
        Developed passive force, kips/ft (Eq. 5-34).

    Returns
    -------
    dict
        FS, fs_min, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a value is negative or H + Pa,d - Pp,d is not positive (the list
        of symbols requires H + Pa,d >= Pp,d).
    """
    for name, v in (("ca_over_su", ca_over_su), ("su", su), ("A", A),
                    ("P_ad", P_ad), ("P_pd", P_pd)):
        _non_negative(name, v)
    drive = float(H) + float(P_ad) - float(P_pd)
    if drive <= 0:
        raise ValueError(f"H + Pa,d - Pp,d = {drive:.3f}: the list of "
                         f"symbols requires H + Pa,d >= Pp,d (p. 119)")
    return {"FS": ca_over_su * A * su / drive,
            "fs_min": _t.table_2_1_minimum_factor_of_safety("sliding")["fs_min"],
            "units": {"FS": "dimensionless"},
            "source": _source("Eq. 5-30", 119),
            "valid_for": "Undrained sliding, phi = 0 (paragraph 5-6d).",
            "notes": ""}


def equation_5_31_developed_strength(fs_slide: float, phi_deg: float,
                                     c_eff: float) -> dict:
    """Strength developed in the passive zone at the sliding factor of
    safety: phi'd = atan(tan(phi')/FSslide) and c'd = c'/FSslide (Eqs. 5-31,
    5-32); for undrained analysis give phi_deg = 0 and c_eff = su for
    su,d = su/FSslide (Eq. 5-33).

    Print check (Eqs. 5-31 to 5-33, p. 120, typed in from the rendered
    page):

        5-31  φ′d = tan^(−1)(tan φ′/FSslide)
        5-32  c′d = c′/FSslide
        5-33  su,d = su/FSslide
        here the same

    Parameters
    ----------
    fs_slide : float
        Minimum factor of safety for sliding from Table 2-1.
    phi_deg : float
        Friction angle in the passive zone, degrees (0 for undrained).
    c_eff : float
        Cohesion c' (or su for undrained) in the passive zone, ksf.

    Returns
    -------
    dict
        phi_d_deg, c_d, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If FSslide is not positive, phi' is outside 0 to 90, or c < 0.
    """
    fs = _positive("fs_slide", fs_slide)
    phi = float(phi_deg)
    if not 0 <= phi < 90:
        raise ValueError(f"phi_deg = {phi_deg}: give 0 to 90 degrees")
    c = _non_negative("c_eff", c_eff)
    return {"phi_d_deg": math.degrees(math.atan(math.tan(math.radians(phi)) / fs)),
            "c_d": c / fs,
            "units": {"phi_d_deg": "degrees", "c_d": "ksf"},
            "source": _source("Eqs. 5-31 to 5-33", 120),
            "valid_for": "Passive resistance in sliding (paragraph 5-6e).",
            "notes": "Kp,d and Ka,d use the developed parameters (p. 121)."}


def equation_5_34_developed_earth_forces(gamma_eff: float, Df: float,
                                         Kp_d: float, Ka_d: float,
                                         c_d: float, L: float) -> dict:
    """Developed passive force on the front and active force on the back of
    a footing for sliding: Pp,d = ((1/2) gamma' Df Kp,d + 2c'd) Df L and
    Pa,d = ((1/2) gamma' Df Ka,d - 2c'd) Df L, which must be >= 0. The
    limit is applied as printed: where the formula gives a negative Pa,d,
    Pa,d = 0 is returned, with the formula's value in P_ad_unlimited and
    limit_governs True. As printed, the cohesion terms are 2c'd, without
    the square root of Kp,d or Ka,d: the Rankine pressures in UFC 3-220-20
    (2025), Eqs. 4-6 and 4-7 (p. 178), carry 2c' sqrt(KA) and
    2c' sqrt(KP), so for Kp,d > 1 and Ka,d < 1 the printed form gives less
    passive force and a smaller active force than those pressures
    integrated over Df.

    Print check (Eqs. 5-34 and 5-35, p. 121, rendered and compared):

        5-34  Pp,d = ((1/2) γ′ · Df · Kp,d + 2c′d) Df · L
        5-35  Pa,d = ((1/2) γ′ · Df · Ka,d − 2c′d) Df · L ≥ 0
        here the same (2c′d, no square root); a negative Pa,d is 0 (the
        list of symbols: "must be ≥ 0"), the formula's value in
        P_ad_unlimited

    Parameters
    ----------
    gamma_eff : float
        Effective unit weight between the footing base and the ground
        surface, kcf.
    Df : float
        Depth of the footing base, ft.
    Kp_d : float
        Passive earth pressure coefficient with the developed parameters.
    Ka_d : float
        Active earth pressure coefficient with the developed parameters.
    c_d : float
        Developed cohesion c'd (su,d for undrained), ksf, Eq. 5-32/5-33.
    L : float
        Footing length, ft (B for a circular footing, 1 for continuous).

    Returns
    -------
    dict
        P_pd, P_ad, P_ad_unlimited, limit_governs, units, source,
        valid_for, notes.

    Raises
    ------
    ValueError
        If a value is negative or L is not positive.
    """
    for name, v in (("gamma_eff", gamma_eff), ("Df", Df), ("Kp_d", Kp_d),
                    ("Ka_d", Ka_d), ("c_d", c_d)):
        _non_negative(name, v)
    Lf = _positive("L", L)
    Pp = (0.5 * gamma_eff * Df * Kp_d + 2 * c_d) * Df * Lf
    Pa = (0.5 * gamma_eff * Df * Ka_d - 2 * c_d) * Df * Lf
    notes = ("As printed (p. 121), the cohesion term is 2c'd, without the "
             "square root of Kp,d or Ka,d; the Rankine pressures of UFC "
             "3-220-20 (2025) Eqs. 4-6 and 4-7 (p. 178) carry 2c' sqrt(KA) "
             "and 2c' sqrt(KP). For Kp,d > 1 and Ka,d < 1 the printed form "
             "gives less passive force and a smaller active force.")
    if Pa < 0:
        notes += (f" The formula gives Pa,d = {Pa:.3f}; the list of symbols "
                  f"(p. 121) says Pa,d 'must be >= 0', so Pa,d = 0 is "
                  f"returned (P_ad_unlimited holds the formula's value).")
    unit = "kips (kips/ft for L = 1)"
    return {"P_pd": Pp, "P_ad": max(Pa, 0.0), "P_ad_unlimited": Pa,
            "limit_governs": Pa < 0,
            "units": {"P_pd": unit, "P_ad": unit, "P_ad_unlimited": unit},
            "source": _source("Eqs. 5-34 and 5-35", 121),
            "valid_for": "Sliding resistance (paragraph 5-6f(2)).",
            "notes": notes}


def equation_5_36_uplift_factor_of_safety(Wf: float, Ws: float, Wc: float,
                                          U: float) -> dict:
    """Factor of safety against uplift: the weights of the foundation (with
    the soil above it), the structure and any contained water over the
    uplift force, FS = (Wf + Ws + Wc)/U; minimum 1.5 (Table 2-1).

    Print check (Eq. 5-36, p. 122, typed in from the rendered page):

        printed    FS = (Wf + Ws + Wc)/U
        here       the same

    Parameters
    ----------
    Wf : float
        Weight of the foundation including soil above the bearing
        elevation, kips (kips/ft).
    Ws : float
        Weight of the structure with fixed equipment and soil above it,
        kips (kips/ft).
    Wc : float
        Weight of water inside a hydraulic structure at the design load
        case, kips (kips/ft).
    U : float
        Uplift force on the base, kips.

    Returns
    -------
    dict
        FS, fs_min, meets_minimum, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If a weight is negative or U is not positive.
    """
    for name, v in (("Wf", Wf), ("Ws", Ws), ("Wc", Wc)):
        _non_negative(name, v)
    u = _positive("U", U)
    fs = (Wf + Ws + Wc) / u
    fs_min = _t.table_2_1_minimum_factor_of_safety("uplift")["fs_min"]
    return {"FS": fs, "fs_min": fs_min, "meets_minimum": fs >= fs_min,
            "units": {"FS": "dimensionless"},
            "source": _source("Eq. 5-36", 122),
            "valid_for": "Uplift (paragraph 5-7).",
            "notes": "Soil strength is often not counted (paragraph 5-7a)."}
