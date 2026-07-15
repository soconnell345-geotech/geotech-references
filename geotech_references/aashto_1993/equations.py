"""AASHTO Guide for Design of Pavement Structures (1993) - design equations.

Part II, Chapter 3 (Highway Pavement Structural Design) and supporting
sections of Part II, Chapter 2 (Design Requirements) and Part I, Chapter 4
(Reliability). All numbers are traced to a rendered page of
``docs/aashto1993.pdf`` (0-based fitz page index cited in each docstring as
``pdf_page``; the printed guide page, e.g. "II-32", is also given).

UNITS: this guide is US-customary native (psi, pci, inches, kips) -- values
are kept in source units per repo convention (GEC-12 precedent); SI notes are
given where cheap. The structural number SN is a dimensionless index tied to
inch-based layer coefficients; do not convert it.

Two headline equations are the AASHO-Road-Test-derived empirical design
equations (log W18 as a function of pavement structural capacity, reliability,
and serviceability loss):

- Flexible pavements (Figure 3.1, pdf_page 121, printed II-32)
- Rigid pavements (Figure 3.7, pdf_page 134, printed II-45)

Both were algebraically verified against the guide's own printed worked
examples embedded in the two figures (see ``flexible_w18_from_sn`` and
``rigid_w18_from_d`` docstrings and ``tests/test_aashto_1993.py``).
"""

import math


# ============================================================================
# Flexible pavement design equation (Figure 3.1; pdf_page 121, printed II-32)
#
#   log10(W18) = ZR*So + 9.36*log10(SN+1) - 0.20
#                + [log10(dPSI/(4.2-1.5))] / [0.40 + 1094/(SN+1)^5.19]
#                + 2.32*log10(MR) - 8.07
#
# Guide worked example (printed on the same page): W18=5e6, R=95% (ZR=-1.645),
# So=0.35, MR=5000 psi, dPSI=1.9 -> Solution: SN=5.0.
# ============================================================================

_FLEX_PO = 4.2  # AASHO Road Test observed initial serviceability, flexible


def _flexible_log_w18(sn, zr, so, delta_psi, mr_psi):
    if sn <= 0:
        raise ValueError(f"sn must be > 0, got {sn}")
    if not (0 < delta_psi < _FLEX_PO - 1.5):
        raise ValueError(
            f"delta_psi must be in (0, {_FLEX_PO - 1.5}) for flexible "
            f"pavements (po={_FLEX_PO}, pt>=1.5), got {delta_psi}"
        )
    if mr_psi <= 0:
        raise ValueError(f"mr_psi must be > 0, got {mr_psi}")
    term_reliability = zr * so
    term_sn = 9.36 * math.log10(sn + 1) - 0.20
    term_psi = (math.log10(delta_psi / (_FLEX_PO - 1.5))
                / (0.40 + 1094 / (sn + 1) ** 5.19))
    term_mr = 2.32 * math.log10(mr_psi) - 8.07
    return term_reliability + term_sn + term_psi + term_mr


def flexible_w18_from_sn(sn, zr, so, delta_psi, mr_psi) -> dict:
    """18-kip ESAL traffic a flexible SN can carry (Eq. of Fig. 3.1, forward).

    log10(W18) = ZR*So + 9.36*log10(SN+1) - 0.20
                 + [log10(dPSI/2.7)] / [0.40 + 1094/(SN+1)^5.19]
                 + 2.32*log10(MR) - 8.07

    Verified against the guide's printed worked example (Figure 3.1,
    pdf_page 121, printed II-32): SN=5.0, ZR=-1.645 (R=95%), So=0.35,
    MR=5000 psi, dPSI=1.9 -> W18 ~ 5.0-5.2e6 (printed solution 5x10^6;
    the guide's own SN=5.0 is itself a nomograph read-off rounded to 0.1).

    Parameters
    ----------
    sn : float
        Trial structural number (dimensionless), > 0.
    zr : float
        Standard normal deviate for the design reliability (negative for
        R > 50%; see ``tables.standard_normal_deviate_zr``).
    so : float
        Overall standard deviation (0.40-0.50 typical for flexible; see
        ``tables.overall_standard_deviation_range``).
    delta_psi : float
        Design serviceability loss, po - pt. Must be in (0, 2.7) since
        po=4.2 is fixed by the AASHO Road Test and pt >= 1.5.
    mr_psi : float
        Effective roadbed soil resilient modulus (psi), > 0.

    Returns
    -------
    dict
        {'sn', 'zr', 'so', 'delta_psi', 'mr_psi', 'w18', 'log10_w18',
         'equation', 'reference'}.

    Raises
    ------
    ValueError
        If sn/mr_psi <= 0 or delta_psi is out of range.
    """
    log_w18 = _flexible_log_w18(sn, zr, so, delta_psi, mr_psi)
    return {
        "sn": sn, "zr": zr, "so": so, "delta_psi": delta_psi, "mr_psi": mr_psi,
        "log10_w18": round(log_w18, 4), "w18": round(10 ** log_w18, 0),
        "equation": ("log10(W18) = ZR*So + 9.36*log10(SN+1) - 0.20 + "
                     "log10(dPSI/2.7)/[0.40+1094/(SN+1)^5.19] + "
                     "2.32*log10(MR) - 8.07"),
        "reference": "AASHTO 1993 Guide, Figure 3.1 (Part II, Ch 3, printed II-32)",
    }


def flexible_sn_from_w18(w18, zr, so, delta_psi, mr_psi,
                         sn_bounds=(0.5, 25.0), tol=1e-7, max_iter=200) -> dict:
    """Required flexible structural number SN for a design W18 (bisection).

    Numerically inverts the same Fig. 3.1 equation (log10(W18) is monotonic
    increasing in SN for fixed other inputs) via bisection.

    Verified against the guide's printed worked example (Figure 3.1): with
    W18=5e6, R=95% (ZR=-1.645), So=0.35, MR=5000 psi, dPSI=1.9, the printed
    nomograph solution is SN=5.0; this function returns SN ~ 4.95-5.0.

    Parameters
    ----------
    w18 : float
        Design 18-kip ESAL traffic over the performance period, > 0.
    zr, so, delta_psi, mr_psi : float
        Same as ``flexible_w18_from_sn``.
    sn_bounds : tuple of float, optional
        Bisection search bracket for SN. Default (0.5, 25.0).
    tol : float, optional
        Convergence tolerance on log10(W18) residual.
    max_iter : int, optional
        Maximum bisection iterations.

    Returns
    -------
    dict
        {'sn', 'w18', 'iterations', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If w18 <= 0, inputs are invalid, or the root is not bracketed by
        sn_bounds.
    """
    if w18 <= 0:
        raise ValueError(f"w18 must be > 0, got {w18}")
    target = math.log10(w18)
    lo, hi = sn_bounds
    f_lo = _flexible_log_w18(lo, zr, so, delta_psi, mr_psi) - target
    f_hi = _flexible_log_w18(hi, zr, so, delta_psi, mr_psi) - target
    if f_lo > 0 or f_hi < 0:
        raise ValueError(
            f"W18={w18:g} not bracketed by sn_bounds={sn_bounds}; "
            "widen sn_bounds."
        )
    n = 0
    for n in range(1, max_iter + 1):
        mid = 0.5 * (lo + hi)
        f_mid = _flexible_log_w18(mid, zr, so, delta_psi, mr_psi) - target
        if abs(f_mid) < tol or (hi - lo) < 1e-9:
            break
        if f_mid < 0:
            lo = mid
        else:
            hi = mid
    sn = 0.5 * (lo + hi)
    return {
        "sn": round(sn, 3), "w18": w18, "iterations": n,
        "equation": ("log10(W18) = ZR*So + 9.36*log10(SN+1) - 0.20 + "
                     "log10(dPSI/2.7)/[0.40+1094/(SN+1)^5.19] + "
                     "2.32*log10(MR) - 8.07  (solved for SN)"),
        "reference": "AASHTO 1993 Guide, Figure 3.1 (Part II, Ch 3, printed II-32)",
    }


# ============================================================================
# Rigid pavement design equation (Figure 3.7; pdf_page 134, printed II-45)
#
#   log10(W18) = ZR*So + 7.35*log10(D+1) - 0.06
#                + [log10(dPSI/(4.5-1.5))] / [1 + 1.624e7/(D+1)^8.46]
#                + (4.22-0.32*pt)*log10{
#                     [Sc'*Cd*(D^0.75 - 1.132)]
#                     / [215.63*J*(D^0.75 - 18.42/(Ec/k)^0.25)] }
#
# Guide worked example (printed across the two Figure 3.7 segments):
# k=72 pci, Ec=5e6 psi, Sc'=650 psi, J=3.2, Cd=1.0, So=0.29, R=95%
# (ZR=-1.645), dPSI=4.2-2.5=1.7, W18=5.1e6 -> Solution: D=10.0 in.
# ============================================================================

_RIGID_PO = 4.5  # AASHO Road Test observed initial serviceability, rigid


def _rigid_log_w18(d, zr, so, delta_psi, sc_psi, cd, j, ec_psi, k_pci, pt):
    if d <= 0:
        raise ValueError(f"d (slab thickness) must be > 0, got {d}")
    if not (0 < delta_psi < _RIGID_PO - 1.5):
        raise ValueError(
            f"delta_psi must be in (0, {_RIGID_PO - 1.5}) for rigid "
            f"pavements (po={_RIGID_PO}, pt>=1.5), got {delta_psi}"
        )
    for name, val in (("sc_psi", sc_psi), ("cd", cd), ("j", j),
                      ("ec_psi", ec_psi), ("k_pci", k_pci)):
        if val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    d075 = d ** 0.75
    ec_k_term = 18.42 / (ec_psi / k_pci) ** 0.25
    inner_denom_bracket = d075 - ec_k_term
    if inner_denom_bracket <= 0:
        raise ValueError(
            "D^0.75 - 18.42/(Ec/k)^0.25 <= 0 (slab too thin / k too low for "
            "these Ec, k inputs) -- the design-strength log term is undefined."
        )
    numerator = sc_psi * cd * (d075 - 1.132)
    if numerator <= 0:
        raise ValueError(
            "Sc'*Cd*(D^0.75 - 1.132) <= 0 -- slab too thin for this Sc'/Cd."
        )
    denominator = 215.63 * j * inner_denom_bracket
    ratio = numerator / denominator
    if ratio <= 0:
        raise ValueError("Design-strength ratio <= 0 -- check inputs.")

    term_reliability = zr * so
    term_d = 7.35 * math.log10(d + 1) - 0.06
    term_psi = (math.log10(delta_psi / (_RIGID_PO - 1.5))
                / (1 + 1.624e7 / (d + 1) ** 8.46))
    term_strength = (4.22 - 0.32 * pt) * math.log10(ratio)
    return term_reliability + term_d + term_psi + term_strength


def rigid_w18_from_d(d, zr, so, delta_psi, sc_psi, cd, j, ec_psi, k_pci,
                     pt=2.5) -> dict:
    """18-kip ESAL traffic a rigid slab thickness D can carry (Fig. 3.7, forward).

    log10(W18) = ZR*So + 7.35*log10(D+1) - 0.06
                 + log10(dPSI/3.0) / [1 + 1.624e7/(D+1)^8.46]
                 + (4.22-0.32*pt)*log10{ [Sc'*Cd*(D^0.75-1.132)]
                                          / [215.63*J*(D^0.75-18.42/(Ec/k)^0.25)] }

    Verified against the guide's printed worked example (Figure 3.7,
    pdf_page 134-135, printed II-45/46): D=10.0 in, k=72 pci, Ec=5e6 psi,
    Sc'=650 psi, J=3.2, Cd=1.0, So=0.29, ZR=-1.645 (R=95%), dPSI=1.7 ->
    W18 ~ 4.9-6.2e6 (printed solution 5.1e6; D=10.0 itself is a nomograph
    read-off "nearest half-inch").

    Parameters
    ----------
    d : float
        Trial slab (PCC) thickness, inches, > 0.
    zr : float
        Standard normal deviate for the design reliability.
    so : float
        Overall standard deviation (0.30-0.40 typical for rigid).
    delta_psi : float
        Design serviceability loss, po - pt. Must be in (0, 3.0) since
        po=4.5 is fixed and pt >= 1.5.
    sc_psi : float
        Mean PCC modulus of rupture (28-day, third-point loading), psi.
    cd : float
        Drainage coefficient (Table 2.5), typically 0.7-1.25.
    j : float
        Load transfer coefficient (Table 2.6), typically 2.3-4.4.
    ec_psi : float
        PCC elastic modulus, psi.
    k_pci : float
        Effective (or design) modulus of subgrade reaction, pci.
    pt : float, optional
        Terminal serviceability index used only in the strength-term
        exponent (4.22-0.32*pt); default 2.5 (matches delta_psi's pt when
        po=4.5, e.g. delta_psi=2.0 for pt=2.5).

    Returns
    -------
    dict
        {'d', 'zr', 'so', 'delta_psi', 'w18', 'log10_w18', 'equation',
         'reference'}.

    Raises
    ------
    ValueError
        If any input is non-physical (see individual checks) or the
        strength-term ratio is non-positive (slab too thin for the inputs).
    """
    log_w18 = _rigid_log_w18(d, zr, so, delta_psi, sc_psi, cd, j, ec_psi,
                             k_pci, pt)
    return {
        "d": d, "zr": zr, "so": so, "delta_psi": delta_psi,
        "log10_w18": round(log_w18, 4), "w18": round(10 ** log_w18, 0),
        "equation": ("log10(W18) = ZR*So + 7.35*log10(D+1) - 0.06 + "
                     "log10(dPSI/3.0)/[1+1.624e7/(D+1)^8.46] + "
                     "(4.22-0.32*pt)*log10{Sc'*Cd*(D^0.75-1.132) / "
                     "[215.63*J*(D^0.75-18.42/(Ec/k)^0.25)]}"),
        "reference": "AASHTO 1993 Guide, Figure 3.7 (Part II, Ch 3, printed II-45/46)",
    }


def rigid_d_from_w18(w18, zr, so, delta_psi, sc_psi, cd, j, ec_psi, k_pci,
                     pt=2.5, d_bounds=(4.0, 20.0), tol=1e-7,
                     max_iter=200) -> dict:
    """Required rigid slab thickness D for a design W18 (bisection).

    Numerically inverts the Fig. 3.7 equation (log10(W18) is monotonic
    increasing in D for fixed other inputs) via bisection.

    Verified against the guide's printed worked example (Figure 3.7): with
    W18=5.1e6, k=72 pci, Ec=5e6 psi, Sc'=650 psi, J=3.2, Cd=1.0, So=0.29,
    ZR=-1.645 (R=95%), dPSI=1.7, the printed nomograph solution is D=10.0 in
    (nearest half-inch); this function returns D ~ 9.7-10.0 in.

    Parameters
    ----------
    w18 : float
        Design 18-kip ESAL traffic, > 0.
    zr, so, delta_psi, sc_psi, cd, j, ec_psi, k_pci, pt : float
        Same as ``rigid_w18_from_d``.
    d_bounds : tuple of float, optional
        Bisection search bracket for D (inches). Default (4.0, 20.0).
    tol, max_iter : float, int, optional
        Bisection convergence controls.

    Returns
    -------
    dict
        {'d', 'w18', 'iterations', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If w18 <= 0 or the root is not bracketed by d_bounds.
    """
    if w18 <= 0:
        raise ValueError(f"w18 must be > 0, got {w18}")
    target = math.log10(w18)
    lo, hi = d_bounds
    f_lo = _rigid_log_w18(lo, zr, so, delta_psi, sc_psi, cd, j, ec_psi,
                          k_pci, pt) - target
    f_hi = _rigid_log_w18(hi, zr, so, delta_psi, sc_psi, cd, j, ec_psi,
                          k_pci, pt) - target
    if f_lo > 0 or f_hi < 0:
        raise ValueError(
            f"W18={w18:g} not bracketed by d_bounds={d_bounds}; "
            "widen d_bounds."
        )
    n = 0
    for n in range(1, max_iter + 1):
        mid = 0.5 * (lo + hi)
        f_mid = _rigid_log_w18(mid, zr, so, delta_psi, sc_psi, cd, j,
                               ec_psi, k_pci, pt) - target
        if abs(f_mid) < tol or (hi - lo) < 1e-9:
            break
        if f_mid < 0:
            lo = mid
        else:
            hi = mid
    d = 0.5 * (lo + hi)
    return {
        "d": round(d, 3), "w18": w18, "iterations": n,
        "equation": ("log10(W18) = ZR*So + 7.35*log10(D+1) - 0.06 + "
                     "log10(dPSI/3.0)/[1+1.624e7/(D+1)^8.46] + "
                     "(4.22-0.32*pt)*log10{...}  (solved for D)"),
        "reference": "AASHTO 1993 Guide, Figure 3.7 (Part II, Ch 3, printed II-45/46)",
    }


# ============================================================================
# Structural number composition (Section 2.3.5 / 3.1.4; pdf_page 118,
# printed II-35): SN = a1*D1 + a2*D2*m2 + a3*D3*m3
# ============================================================================

def structural_number(a1, d1, a2=0.0, d2=0.0, m2=1.0,
                      a3=0.0, d3=0.0, m3=1.0) -> dict:
    """Flexible pavement structural number from layer coefficients (Section 3.1.4).

        SN = a1*D1 + a2*D2*m2 + a3*D3*m3

    Parameters
    ----------
    a1 : float
        Surface course layer coefficient (see
        ``tables.layer_coefficient_a1_asphalt``).
    d1 : float
        Surface course thickness, inches.
    a2, d2, m2 : float, optional
        Base course layer coefficient, thickness (inches), and drainage
        coefficient (Table 2.4). Default a2=d2=0 (no base), m2=1.0.
    a3, d3, m3 : float, optional
        Subbase course layer coefficient, thickness (inches), and drainage
        coefficient. Default a3=d3=0 (no subbase), m3=1.0.

    Returns
    -------
    dict
        {'sn', 'a1', 'd1', 'a2', 'd2', 'm2', 'a3', 'd3', 'm3', 'equation',
         'reference'}.

    Raises
    ------
    ValueError
        If any thickness or coefficient is negative.
    """
    for name, val in (("a1", a1), ("d1", d1), ("a2", a2), ("d2", d2),
                      ("m2", m2), ("a3", a3), ("d3", d3), ("m3", m3)):
        if val < 0:
            raise ValueError(f"{name} must be >= 0, got {val}")
    sn = a1 * d1 + a2 * d2 * m2 + a3 * d3 * m3
    return {
        "sn": round(sn, 3),
        "a1": a1, "d1": d1, "a2": a2, "d2": d2, "m2": m2,
        "a3": a3, "d3": d3, "m3": m3,
        "equation": "SN = a1*D1 + a2*D2*m2 + a3*D3*m3",
        "reference": "AASHTO 1993 Guide, Section 3.1.4 (pdf_page 118, printed II-35)",
    }


def minimum_layer_thicknesses(sn_over_base, sn_over_subbase, sn_over_roadbed,
                              a1, a2, m2, a3, m3) -> dict:
    """Minimum layer thicknesses from a layered SN analysis (Figure 3.2).

    Given the required SN evaluated at three successive foundation
    strengths -- SN required directly over the base (using the base's own
    MR in the design equation), over the subbase, and over the roadbed
    (= the overall design SN using the roadbed MR) -- returns the minimum
    thickness of each layer per the printed procedure:

        D*1 >= SN1/a1;                 SN*1 = a1*D*1
        D*2 >= (SN2 - SN*1)/(a2*m2);   SN*1 + SN*2 >= SN2
        D*3 >= (SN3 - (SN*1+SN*2))/(a3*m3)

    Parameters
    ----------
    sn_over_base : float
        SN1: structural number required over the base course (i.e. the
        design SN computed using the base course's MR as the "roadbed").
    sn_over_subbase : float
        SN2: structural number required over the subbase course.
    sn_over_roadbed : float
        SN3: structural number required over the actual roadbed soil
        (the overall design SN).
    a1, a2, a3 : float
        Layer coefficients for surface, base, subbase.
    m2, m3 : float
        Drainage coefficients for base, subbase.

    Returns
    -------
    dict
        {'d1_min', 'd2_min', 'd3_min', 'sn1_actual', 'sn1_2_actual',
         'equation', 'reference'}. d2_min/d3_min are clamped to 0.0 (with a
         note) if the upstream layer alone already satisfies the deeper SN
         requirement.

    Raises
    ------
    ValueError
        If a1 <= 0, or sn_over_base/subbase/roadbed are not
        non-decreasing (SN1 <= SN2 <= SN3), or a2/a3 <= 0 while a
        positive thickness is required from that layer.
    """
    if a1 <= 0:
        raise ValueError(f"a1 must be > 0, got {a1}")
    if not (sn_over_base <= sn_over_subbase <= sn_over_roadbed):
        raise ValueError(
            "Expected sn_over_base <= sn_over_subbase <= sn_over_roadbed "
            f"(weaker foundation -> larger required SN), got "
            f"{sn_over_base}, {sn_over_subbase}, {sn_over_roadbed}"
        )
    notes = []
    d1_min = sn_over_base / a1
    sn1_actual = a1 * d1_min

    need2 = sn_over_subbase - sn1_actual
    if need2 <= 0:
        d2_min = 0.0
        notes.append("Layer 1 alone satisfies SN2; d2_min clamped to 0.")
    else:
        if a2 <= 0:
            raise ValueError("a2 must be > 0 when a base layer is required")
        d2_min = need2 / (a2 * m2)
    sn1_2_actual = sn1_actual + a2 * d2_min * m2

    need3 = sn_over_roadbed - sn1_2_actual
    if need3 <= 0:
        d3_min = 0.0
        notes.append("Layers 1+2 alone satisfy SN3; d3_min clamped to 0.")
    else:
        if a3 <= 0:
            raise ValueError("a3 must be > 0 when a subbase layer is required")
        d3_min = need3 / (a3 * m3)

    out = {
        "d1_min": round(d1_min, 3), "d2_min": round(d2_min, 3),
        "d3_min": round(d3_min, 3),
        "sn1_actual": round(sn1_actual, 3),
        "sn1_2_actual": round(sn1_2_actual, 3),
        "equation": ("D1>=SN1/a1; D2>=(SN2-SN1*)/(a2*m2); "
                     "D3>=(SN3-(SN1*+SN2*))/(a3*m3)"),
        "reference": "AASHTO 1993 Guide, Figure 3.2 (pdf_page 125, printed II-36)",
    }
    if notes:
        out["notes"] = notes
    return out


# ============================================================================
# Layer coefficient regressions -- PRINTED closed-form fits (not chart
# read-offs) for the granular base (a2) and granular subbase (a3)
# coefficients, given as text equations alongside Figures 2.6/2.7.
# (Section 2.3.5; pdf_page 109/111, printed II-20/22)
# ============================================================================

def layer_coefficient_a2_granular_base(ebs_psi) -> dict:
    """Granular base layer coefficient a2 from resilient modulus (printed eq.).

        a2 = 0.249*log10(EBS) - 0.977

    Printed as an explicit alternative to the Figure 2.6 nomograph (same
    page gives a worked check: EBS=30,000 psi -> a2=0.14, CBR~100 (approx),
    R-value~85 (approx)).

    Parameters
    ----------
    ebs_psi : float
        Granular base resilient modulus, psi, > 0.

    Returns
    -------
    dict
        {'ebs_psi', 'a2', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If ebs_psi <= 0.
    """
    if ebs_psi <= 0:
        raise ValueError(f"ebs_psi must be > 0, got {ebs_psi}")
    a2 = 0.249 * math.log10(ebs_psi) - 0.977
    return {
        "ebs_psi": ebs_psi, "a2": round(a2, 4),
        "equation": "a2 = 0.249*log10(EBS) - 0.977",
        "reference": "AASHTO 1993 Guide, Section 2.3.5 (pdf_page 109, printed II-20)",
    }


def layer_coefficient_a3_granular_subbase(esb_psi) -> dict:
    """Granular subbase layer coefficient a3 from resilient modulus (printed eq.).

        a3 = 0.227*log10(ESB) - 0.839

    Printed as an explicit alternative to the Figure 2.7 nomograph (same
    page gives a worked check: ESB=15,000 psi -> a3=0.11, CBR~30 (approx),
    R-value~60 (approx)).

    Parameters
    ----------
    esb_psi : float
        Granular subbase resilient modulus, psi, > 0.

    Returns
    -------
    dict
        {'esb_psi', 'a3', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If esb_psi <= 0.
    """
    if esb_psi <= 0:
        raise ValueError(f"esb_psi must be > 0, got {esb_psi}")
    a3 = 0.227 * math.log10(esb_psi) - 0.839
    return {
        "esb_psi": esb_psi, "a3": round(a3, 4),
        "equation": "a3 = 0.227*log10(ESB) - 0.839",
        "reference": "AASHTO 1993 Guide, Section 2.3.5 (pdf_page 111, printed II-22)",
    }


# ============================================================================
# Effective roadbed soil resilient modulus (Section 2.3.1; Figure 2.3/2.4;
# pdf_page 103-104, printed II-14/15)
#
#   uf = 1.18e8 * MR^-2.32          (relative damage for a seasonal MR)
#   MR_eff = (1.18e8 / uf_avg)^(1/2.32)
# ============================================================================

def relative_damage_uf(mr_psi) -> dict:
    """Relative damage uf for a seasonal roadbed resilient modulus (Fig. 2.3).

        uf = 1.18 x 10^8 * MR^-2.32

    Parameters
    ----------
    mr_psi : float
        Seasonal roadbed soil resilient modulus, psi, > 0.

    Returns
    -------
    dict
        {'mr_psi', 'uf', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If mr_psi <= 0.
    """
    if mr_psi <= 0:
        raise ValueError(f"mr_psi must be > 0, got {mr_psi}")
    uf = 1.18e8 * mr_psi ** -2.32
    return {
        "mr_psi": mr_psi, "uf": uf,
        "equation": "uf = 1.18e8 * MR^-2.32",
        "reference": "AASHTO 1993 Guide, Figure 2.3 (pdf_page 103, printed II-14)",
    }


def effective_roadbed_resilient_modulus(monthly_mr_psi) -> dict:
    """Effective roadbed soil resilient modulus from monthly seasonal values.

    Averages the relative damage uf over the seasonal (monthly) MR values
    and inverts back to a single effective design MR (Figure 2.3/2.4
    procedure). Applies only to flexible pavements designed using the
    serviceability criteria (per the guide's own caveat).

    Verified against the guide's printed worked example (Figure 2.4,
    pdf_page 104, printed II-15): monthly MR (psi) =
    [20000,20000,2500,4000,4000,7000,7000,7000,7000,7000,4000,20000] ->
    sum(uf)=3.72, avg uf=0.31, effective MR = 5,000 psi (printed solution).

    Parameters
    ----------
    monthly_mr_psi : list of float
        Roadbed soil resilient modulus for each of the (typically 12)
        seasonal increments, psi. All values must be > 0.

    Returns
    -------
    dict
        {'monthly_mr_psi', 'uf_values', 'uf_sum', 'uf_avg',
         'effective_mr_psi', 'n_seasons', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If monthly_mr_psi is empty or contains a non-positive value.
    """
    if not monthly_mr_psi:
        raise ValueError("monthly_mr_psi must be a non-empty list")
    uf_values = []
    for mr in monthly_mr_psi:
        if mr <= 0:
            raise ValueError(f"All MR values must be > 0, got {mr}")
        uf_values.append(1.18e8 * mr ** -2.32)
    uf_sum = sum(uf_values)
    n = len(monthly_mr_psi)
    uf_avg = uf_sum / n
    mr_eff = (1.18e8 / uf_avg) ** (1 / 2.32)
    return {
        "monthly_mr_psi": list(monthly_mr_psi),
        "uf_values": [round(u, 4) for u in uf_values],
        "uf_sum": round(uf_sum, 4), "uf_avg": round(uf_avg, 4),
        "effective_mr_psi": round(mr_eff, 0), "n_seasons": n,
        "equation": ("uf=1.18e8*MR^-2.32; MR_eff = "
                     "(1.18e8/mean(uf))^(1/2.32)"),
        "reference": ("AASHTO 1993 Guide, Figure 2.3/2.4 "
                     "(pdf_page 103-104, printed II-14/15)"),
    }


def modulus_subgrade_reaction_simple(mr_psi) -> dict:
    """Theoretical k-value from roadbed MR alone (no subbase/rigid foundation).

        k = MR / 19.4

    This is the simplified relationship used only when the slab bears
    directly on the roadbed (no subbase); for the general case (subbase
    present, and/or a shallow rigid foundation) the guide's iterative
    Table 3.2 / Figures 3.3-3.6 process is required (not digitized here --
    it is a 4-nomograph seasonal-weighting procedure; see the printed guide,
    pdf_page 128-133).

    Parameters
    ----------
    mr_psi : float
        Roadbed soil resilient modulus, psi, > 0.

    Returns
    -------
    dict
        {'mr_psi', 'k_pci', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If mr_psi <= 0.
    """
    if mr_psi <= 0:
        raise ValueError(f"mr_psi must be > 0, got {mr_psi}")
    k = mr_psi / 19.4
    return {
        "mr_psi": mr_psi, "k_pci": round(k, 1),
        "equation": "k (pci) = MR (psi) / 19.4",
        "reference": "AASHTO 1993 Guide, Section 3.2.1 (pdf_page 129, printed II-44)",
        "note": ("Theoretical relation for a slab bearing directly on the "
                 "roadbed (no subbase, no shallow rigid foundation)."),
    }


# ============================================================================
# Serviceability
# ============================================================================

def design_serviceability_loss(po, pt) -> dict:
    """Design serviceability loss dPSI = po - pt (Section 2.2.1).

    Parameters
    ----------
    po : float
        Initial serviceability index (AASHO Road Test observed: 4.2
        flexible, 4.5 rigid).
    pt : float
        Terminal serviceability index (2.0-3.0 typical; see
        ``tables.terminal_serviceability_guidance``).

    Returns
    -------
    dict
        {'po', 'pt', 'delta_psi', 'reference'}.

    Raises
    ------
    ValueError
        If pt >= po.
    """
    if pt >= po:
        raise ValueError(f"pt ({pt}) must be < po ({po})")
    return {
        "po": po, "pt": pt, "delta_psi": round(po - pt, 3),
        "reference": "AASHTO 1993 Guide, Section 2.2.1 (pdf_page 99, printed II-10)",
    }


def stage_reliability(overall_reliability_pct, n_stages) -> dict:
    """Required per-stage reliability to reach a compounded overall reliability.

        R_stage = (R_overall)^(1/n)     (fractions, Eq. 4.5.1)

    Reliabilities compound multiplicatively across stages (initial pavement
    + planned overlay(s)), so each stage must be designed to a higher
    reliability than the desired overall value.

    Verified against the guide's printed example (Section 4.5, pdf_page 84,
    printed I-63): overall R=95% desired with 2 stages -> per-stage R =
    (0.95)^(1/2) = 97.5%; also the reverse-direction example: two 90%
    stages compound to 0.90*0.90 = 81%.

    Parameters
    ----------
    overall_reliability_pct : float
        Desired overall (compounded) reliability, percent (0-100).
    n_stages : int
        Number of stages, including the initial pavement, >= 1.

    Returns
    -------
    dict
        {'overall_reliability_pct', 'n_stages', 'stage_reliability_pct',
         'equation', 'reference'}.

    Raises
    ------
    ValueError
        If overall_reliability_pct is out of (0, 100] or n_stages < 1.
    """
    if not (0 < overall_reliability_pct <= 100):
        raise ValueError(
            f"overall_reliability_pct must be in (0, 100], got "
            f"{overall_reliability_pct}"
        )
    if n_stages < 1:
        raise ValueError(f"n_stages must be >= 1, got {n_stages}")
    r_overall_frac = overall_reliability_pct / 100.0
    r_stage_frac = r_overall_frac ** (1.0 / n_stages)
    return {
        "overall_reliability_pct": overall_reliability_pct,
        "n_stages": n_stages,
        "stage_reliability_pct": round(r_stage_frac * 100.0, 2),
        "equation": "R_stage = (R_overall)^(1/n)  (fractions)",
        "reference": "AASHTO 1993 Guide, Eq. 4.5.1 (pdf_page 84, printed I-63)",
    }


# ============================================================================
# Aggregate-surfaced road performance (Section 2.2.2/2.2.3; pdf_page 102,
# printed II-13) -- rutting/aggregate-loss models. Low-priority / secondary
# to the main SN/slab-thickness design (Part II Ch 4 low-volume roads).
# ============================================================================

def aggregate_loss_army_corps(bladings, ladt, radius_ft, grade_pct) -> dict:
    """Aggregate loss for an aggregate-surfaced road (US Army/road-grading model).

        GL (in) = (B/25.4) / (0.0045*LADT + 3380.6/R + 0.467*G)

    Parameters
    ----------
    bladings : float
        Number of bladings during the period of time being considered.
    ladt : float
        Average daily traffic in the design lane (one-lane road: total
        traffic in both directions).
    radius_ft : float
        Average radius of curves, feet, > 0.
    grade_pct : float
        Absolute value of grade, percent.

    Returns
    -------
    dict
        {'bladings', 'ladt', 'radius_ft', 'grade_pct', 'gl_in', 'equation',
         'reference'}.

    Raises
    ------
    ValueError
        If radius_ft <= 0 or the denominator is non-positive.
    """
    if radius_ft <= 0:
        raise ValueError(f"radius_ft must be > 0, got {radius_ft}")
    denom = 0.0045 * ladt + 3380.6 / radius_ft + 0.467 * grade_pct
    if denom <= 0:
        raise ValueError("Denominator (0.0045*LADT + 3380.6/R + 0.467*G) <= 0")
    gl = (bladings / 25.4) / denom
    return {
        "bladings": bladings, "ladt": ladt, "radius_ft": radius_ft,
        "grade_pct": grade_pct, "gl_in": round(gl, 3),
        "equation": "GL (in) = (B/25.4) / (0.0045*LADT + 3380.6/R + 0.467*G)",
        "reference": "AASHTO 1993 Guide, Section 2.2.3 (pdf_page 102, printed II-13)",
    }


def annual_aggregate_loss_kenya(traffic_thousands, rainfall_in, grade_pct,
                                gravel_type="lateritic") -> dict:
    """Annual aggregate (gravel) loss, Kenya study model (low-truck-traffic roads).

        AGL = [T^2/(T^2+50)] * f * (4.2 + 0.92*T + 0.889*R^2 + 1.88*VC)

    Parameters
    ----------
    traffic_thousands : float
        Annual traffic volume in both directions, thousands of vehicles.
    rainfall_in : float
        Annual rainfall, inches.
    grade_pct : float
        Average percentage gradient of the road.
    gravel_type : str, optional
        'lateritic' (f=0.37, default), 'quartzitic' (f=0.43), 'volcanic'
        (f=0.28), or 'coral' (f=0.59).

    Returns
    -------
    dict
        {'traffic_thousands', 'rainfall_in', 'grade_pct', 'gravel_type',
         'f', 'agl_in_per_year', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If gravel_type is unrecognized.
    """
    f_table = {"lateritic": 0.37, "quartzitic": 0.43, "volcanic": 0.28,
              "coral": 0.59}
    key = str(gravel_type).strip().lower()
    if key not in f_table:
        raise ValueError(
            f"Unknown gravel_type '{gravel_type}'. Use one of: "
            f"{', '.join(f_table)}"
        )
    f = f_table[key]
    t = traffic_thousands
    r = rainfall_in
    vc = grade_pct
    agl = (t ** 2 / (t ** 2 + 50)) * f * (4.2 + 0.92 * t + 0.889 * r ** 2
                                          + 1.88 * vc)
    return {
        "traffic_thousands": t, "rainfall_in": r, "grade_pct": vc,
        "gravel_type": key, "f": f, "agl_in_per_year": round(agl, 3),
        "equation": ("AGL = [T^2/(T^2+50)] * f * "
                     "(4.2+0.92T+0.889R^2+1.88VC)"),
        "reference": "AASHTO 1993 Guide, Section 2.2.3 (pdf_page 102, printed II-13)",
    }
