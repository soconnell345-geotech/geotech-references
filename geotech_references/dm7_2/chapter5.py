"""
UFC 3-220-20, Chapter 5: Shallow Foundations

Equations 5-1 through 5-42 covering gross and net bearing pressure,
eccentricity (effective foundation dimensions), allowable bearing pressure
and factor of safety, bearing capacity theory (Terzaghi, Meyerhof, Hansen,
Vesic bearing capacity factors Nc, Nq, Ngamma), shape/depth/inclination
correction factors, groundwater correction, foundations near slopes,
layered soil bearing capacity, bearing capacity of rock, modulus of
subgrade reaction, and mat/raft foundation design.

Reference:
    UFC 3-220-20, Foundations, 16 January 2025
"""

import math
from typing import Tuple
from geotech_references import _units as _u


# ===========================================================================
# SECTION 5-2: Gross and Net Bearing Pressure (Equations 5-1 through 5-3)
# ===========================================================================


def gross_bearing_pressure(
    Q_DL_LL: float, W_F: float, W_S: float, A: float
) -> float:
    """Gross bearing pressure on a shallow foundation (Equation 5-1).

    The gross bearing pressure applied to the soil by a shallow foundation
    is the total load (structural load + foundation weight + overburden soil
    weight) divided by the bearing surface area.

    .. math::
        q_{gross} = \\frac{Q_{DL+LL} + W_F + W_S}{A}

    Parameters
    ----------
    Q_DL_LL : float
        Structural load: dead load plus live load (lb, kN, or any
        consistent force unit).
    W_F : float
        Weight of the foundation (same force unit as *Q_DL_LL*).
    W_S : float
        Weight of overlying soil (same force unit as *Q_DL_LL*).
    A : float
        Area of the bearing surface (ft^2, m^2, or consistent area unit).

    Returns
    -------
    float
        Gross bearing pressure [consistent units (psf, kPa or another stress
        unit)].

    Raises
    ------
    ValueError
        If *A* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-1,
    printed p. 275 (pdf_page_index 312).
    """
    if A <= 0.0:
        raise ValueError("Bearing surface area A must be positive.")
    return (Q_DL_LL + W_F + W_S) / A


def net_bearing_pressure_from_ultimate(
    q_ult: float, sigma_zD: float
) -> float:
    """Net bearing pressure from ultimate bearing capacity (Equation 5-2).

    The net bearing pressure is the ultimate bearing capacity minus the
    existing vertical overburden pressure at the foundation bearing
    elevation.

    .. math::
        q_{net} = q_{ult} - \\sigma_{zD}

    Parameters
    ----------
    q_ult : float
        Ultimate bearing capacity (psf, kPa, or consistent stress unit).
    sigma_zD : float
        Vertical overburden pressure at the bearing elevation (same unit).

    Returns
    -------
    float
        Net bearing pressure [consistent units (same stress unit)].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-2,
    printed p. 275 (pdf_page_index 312).
    """
    return q_ult - sigma_zD


def net_bearing_pressure(Q_DL_LL: float, A: float) -> float:
    """Simplified net bearing pressure (Equation 5-3).

    When the unit weights of the foundation and soil backfill are assumed
    to be the same as the existing soil, the net bearing pressure simplifies
    to the structural load divided by the foundation area.

    .. math::
        q_{net} \\approx \\frac{Q_{DL+LL}}{A}

    Parameters
    ----------
    Q_DL_LL : float
        Structural load: dead load plus live load (lb, kN, or consistent
        force unit).
    A : float
        Area of the bearing surface (ft^2, m^2, or consistent area unit).

    Returns
    -------
    float
        Net bearing pressure [consistent units (psf, kPa or another stress
        unit)].

    Raises
    ------
    ValueError
        If *A* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-3,
    printed p. 276 (pdf_page_index 313).
    """
    if A <= 0.0:
        raise ValueError("Bearing surface area A must be positive.")
    return Q_DL_LL / A


# ===========================================================================
# SECTION 5-2.3: Eccentricity (Equations 5-4 through 5-12)
# ===========================================================================


def eccentricity(M: float, Q: float) -> float:
    """Eccentricity of foundation loading (Equation 5-4).

    The eccentricity is the horizontal distance between the resultant
    force on the bearing surface and the centerline of the foundation.

    .. math::
        e = \\frac{M}{Q}

    Parameters
    ----------
    M : float
        Applied moment (lb-ft, kN-m, or consistent moment unit).
    Q : float
        Gross vertical load on the footing (lb, kN, or consistent force
        unit).

    Returns
    -------
    float
        Eccentricity [consistent units (ft, m or another length unit)].

    Raises
    ------
    ValueError
        If *Q* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-4,
    printed p. 276 (pdf_page_index 313).
    """
    if Q <= 0.0:
        raise ValueError("Gross vertical load Q must be positive.")
    return M / Q


def check_eccentricity_one_direction(e: float, dimension: float) -> bool:
    """Check one-direction eccentricity limit (Equation 5-5).

    For eccentricity in one direction, the resultant must be in the middle
    one-third of the foundation.

    .. math::
        e_B \\leq \\frac{B}{6} \\quad \\text{or} \\quad e_L \\leq \\frac{L}{6}

    Parameters
    ----------
    e : float
        Eccentricity in B or L direction (ft, m).
    dimension : float
        Corresponding foundation dimension B or L (ft, m).

    Returns
    -------
    bool
        True if eccentricity is within the middle-third limit.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-5,
    printed p. 276 (pdf_page_index 313).
    """
    if dimension <= 0.0:
        raise ValueError("Foundation dimension must be positive.")
    return abs(e) <= dimension / 6.0


def check_eccentricity_two_directions(
    e_B: float, e_L: float, B: float, L: float
) -> bool:
    """Check two-direction eccentricity kern limit (Equation 5-6).

    For cases with eccentricity in two directions, the resultant must fall
    within the diamond-shaped kern area in the middle of the rectangular
    foundation.

    .. math::
        \\frac{6 \\, e_B}{B} + \\frac{6 \\, e_L}{L} \\leq 1

    Parameters
    ----------
    e_B : float
        Eccentricity in B direction (ft, m).
    e_L : float
        Eccentricity in L direction (ft, m).
    B : float
        Foundation width -- shorter dimension (ft, m).
    L : float
        Foundation length -- longer dimension (ft, m).

    Returns
    -------
    bool
        True if eccentricity is within the kern limit.

    Raises
    ------
    ValueError
        If *B* or *L* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-6,
    printed p. 276 (pdf_page_index 313).
    """
    if B <= 0.0 or L <= 0.0:
        raise ValueError("Foundation dimensions B and L must be positive.")
    return (6.0 * abs(e_B) / B + 6.0 * abs(e_L) / L) <= 1.0


@_u.labelled(
    {"q1": "consistent units (the unit of q_gross)",
     "q2": "consistent units (the unit of q_gross)",
     "q3": "consistent units (the unit of q_gross)",
     "q4": "consistent units (the unit of q_gross)"},
    printed_page="277", pdf_page_index=314)
def corner_bearing_pressure(
    q_gross: float, e_B: float, e_L: float, B: float, L: float
) -> dict:
    """Corner bearing pressures for eccentric loading (Equation 5-7).

    Returns the bearing pressure at the four corners of a rectangular
    foundation with two-way eccentricity within the kern.

    .. math::
        q_{corner} = q_{gross} \\left(1 \\pm \\frac{6 |e_B|}{B}
                      \\pm \\frac{6 |e_L|}{L}\\right)

    Eq. 5-7 is printed with the magnitudes |eB| and |eL| (as are the
    limits of Eq. 5-5 and 5-6), so the signs of *e_B* and *e_L* are not
    used: q1 is the maximum and q4 the minimum whatever signs are passed.

    Parameters
    ----------
    q_gross : float
        Gross bearing pressure (psf, kPa, or consistent stress unit).
    e_B : float
        Eccentricity in B direction (ft, m); its magnitude is used.
    e_L : float
        Eccentricity in L direction (ft, m); its magnitude is used.
    B : float
        Foundation width -- shorter dimension (ft, m).
    L : float
        Foundation length -- longer dimension (ft, m).

    Returns
    -------
    dict
        ``q1`` = q_gross(1 + 6|eB|/B + 6|eL|/L), the maximum;
        ``q2`` = q_gross(1 + 6|eB|/B - 6|eL|/L);
        ``q3`` = q_gross(1 - 6|eB|/B + 6|eL|/L);
        ``q4`` = q_gross(1 - 6|eB|/B - 6|eL|/L), the minimum;
        ``note``: that the magnitudes |eB| and |eL| were used.

    Raises
    ------
    ValueError
        If *B* or *L* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-7,
    printed p. 277 (pdf_page_index 314).
    """
    if B <= 0.0 or L <= 0.0:
        raise ValueError("Foundation dimensions B and L must be positive.")
    term_B = 6.0 * abs(e_B) / B
    term_L = 6.0 * abs(e_L) / L
    return {
        "q1": q_gross * (1.0 + term_B + term_L),
        "q2": q_gross * (1.0 + term_B - term_L),
        "q3": q_gross * (1.0 - term_B + term_L),
        "q4": q_gross * (1.0 - term_B - term_L),
        "note": (
            "Eq. 5-7 (p. 277) uses the magnitudes |eB| and |eL|; the signs "
            "of e_B and e_L are not used. q1 is the maximum corner pressure "
            "and q4 the minimum."
        ),
    }


def effective_foundation_width(B: float, e_B: float) -> float:
    """Effective (equivalent) foundation width (Equation 5-8).

    The equivalent width is the width of the bearing area on which the
    resultant bearing force is centered (Meyerhof 1953).

    .. math::
        B' = B - 2 \\, e_B

    Parameters
    ----------
    B : float
        Actual foundation width (ft, m).
    e_B : float
        Eccentricity in B direction (ft, m).

    Returns
    -------
    float
        Effective foundation width B' [consistent units (ft, m)].

    Raises
    ------
    ValueError
        If resulting B' is non-positive.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-8,
    printed p. 277 (pdf_page_index 314).
    """
    B_prime = B - 2.0 * abs(e_B)
    if B_prime <= 0.0:
        raise ValueError(
            "Effective width B' is non-positive; eccentricity is too large."
        )
    return B_prime


def effective_foundation_length(L: float, e_L: float) -> float:
    """Effective (equivalent) foundation length (Equation 5-9).

    The equivalent length is the length of the bearing area on which the
    resultant bearing force is centered (Meyerhof 1953).

    .. math::
        L' = L - 2 \\, e_L

    Parameters
    ----------
    L : float
        Actual foundation length (ft, m).
    e_L : float
        Eccentricity in L direction (ft, m).

    Returns
    -------
    float
        Effective foundation length L' [consistent units (ft, m)].

    Raises
    ------
    ValueError
        If resulting L' is non-positive.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-9,
    printed p. 277 (pdf_page_index 314).
    """
    L_prime = L - 2.0 * abs(e_L)
    if L_prime <= 0.0:
        raise ValueError(
            "Effective length L' is non-positive; eccentricity is too large."
        )
    return L_prime


def equivalent_uniform_bearing_pressure(
    Q_DL_LL: float, W_F: float, W_S: float, B_prime: float, L_prime: float
) -> float:
    """Equivalent uniform bearing pressure for eccentric loading (Equation 5-10).

    The equivalent uniform bearing pressure for a rectangular foundation
    using the equivalent (effective) dimensions.

    .. math::
        q_{unif} = \\frac{Q_{DL+LL} + W_F + W_S}{B' \\cdot L'}

    Parameters
    ----------
    Q_DL_LL : float
        Structural load: dead load plus live load (lb, kN).
    W_F : float
        Weight of the foundation (same force unit).
    W_S : float
        Weight of overlying soil (same force unit).
    B_prime : float
        Effective foundation width (ft, m).
    L_prime : float
        Effective foundation length (ft, m).

    Returns
    -------
    float
        Equivalent uniform bearing pressure [consistent units (psf, kPa)].

    Raises
    ------
    ValueError
        If effective dimensions are non-positive.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-10,
    printed p. 277 (pdf_page_index 314).
    """
    if B_prime <= 0.0 or L_prime <= 0.0:
        raise ValueError("Effective dimensions B' and L' must be positive.")
    return (Q_DL_LL + W_F + W_S) / (B_prime * L_prime)


def circular_effective_length(r: float, e_x: float) -> float:
    """Equivalent length L' (in the length unit of r) of the rectangle
    that stands for an eccentrically loaded circular footing, Equation
    5-11 of UFC 3-220-20, from the radius r and the eccentricity e_x.

    The resultant is centred on the lens-shaped area between two arcs
    (Figure 5-1(b)), whose area is
    A' = 2 r^2 acos(e_x / r) - 2 e_x sqrt(r^2 - e_x^2); the equivalent
    rectangle has that area and the lens's aspect ratio, so L' B' = A'.
    With no eccentricity L' = B' = r sqrt(pi).

    .. math::
        L' = \\sqrt{\\left[ 2 r^2 \\cos^{-1}\\!\\left(\\frac{e_x}{r}\\right)
             - 2 e_x \\sqrt{r^2 - e_x^2}\\,\\right]
             \\left( \\frac{\\sqrt{r^2 - e_x^2}}{r - e_x} \\right)}

    Parameters
    ----------
    r : float
        Radius of the circular foundation (ft, m).
    e_x : float
        Eccentricity (ft, m).  Must be less than *r*.

    Returns
    -------
    float
        Equivalent length L' [consistent units (ft, m)].

    Raises
    ------
    ValueError
        If *e_x* >= *r* or if *r* is non-positive.

    Notes
    -----
    The inverse cosine term must be expressed in radians.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-11,
    printed p. 277 (pdf_page_index 314); Figure 5-1(b),
    printed p. 278 (pdf_page_index 315).
    """
    if r <= 0.0:
        raise ValueError("Radius r must be positive.")
    e_x = abs(e_x)
    if e_x >= r:
        raise ValueError("Eccentricity e_x must be less than radius r.")
    root = math.sqrt(r * r - e_x * e_x)
    area = 2.0 * r * r * math.acos(e_x / r) - 2.0 * e_x * root
    return math.sqrt(area * root / (r - e_x))


def circular_effective_width(r: float, e_x: float, L_prime: float) -> float:
    """Equivalent width B' (in the length unit of r) of the rectangle
    that stands for an eccentrically loaded circular footing, Equation
    5-12 of UFC 3-220-20, from the radius r, the eccentricity e_x and
    the equivalent length L' of Equation 5-11.

    B' is L' times the aspect ratio of the lens-shaped area of
    Figure 5-1(b); with L' from Equation 5-11, L' B' is the lens area.

    .. math::
        B' = L' \\left( \\frac{r - e_x}{\\sqrt{r^2 - e_x^2}} \\right)

    Parameters
    ----------
    r : float
        Radius of the circular foundation (ft, m).
    e_x : float
        Eccentricity (ft, m).  Must be less than *r*.
    L_prime : float
        Equivalent length L' from Equation 5-11,
        ``circular_effective_length`` (ft, m).

    Returns
    -------
    float
        Equivalent width B' [consistent units (ft, m)].

    Raises
    ------
    ValueError
        If *r* or *L_prime* is not positive or *e_x* >= *r*.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-12,
    printed p. 278 (pdf_page_index 315).
    """
    if r <= 0.0:
        raise ValueError("Radius r must be positive.")
    e_x = abs(e_x)
    if e_x >= r:
        raise ValueError("Eccentricity e_x must be less than radius r.")
    if L_prime <= 0.0:
        raise ValueError("Effective length L' must be positive.")
    return L_prime * (r - e_x) / math.sqrt(r * r - e_x * e_x)


# ===========================================================================
# SECTION 5-2.4: Allowable Bearing Pressure (Equations 5-13 and 5-14)
# ===========================================================================


def gross_allowable_bearing_pressure(q_ult: float, F_BC: float) -> float:
    """Gross allowable bearing pressure (Equation 5-13).

    The gross allowable bearing pressure is the ultimate bearing capacity
    divided by the bearing capacity factor of safety.

    .. math::
        q_{all,gross} = \\frac{q_{ult}}{F_{BC}}

    Parameters
    ----------
    q_ult : float
        Ultimate bearing capacity (psf, kPa, or consistent stress unit).
    F_BC : float
        Bearing capacity factor of safety (dimensionless, typically 2 to 4).

    Returns
    -------
    float
        Gross allowable bearing pressure [consistent units (same stress unit as
        *q_ult*)].

    Raises
    ------
    ValueError
        If *F_BC* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-13,
    printed p. 279 (pdf_page_index 316).
    """
    if F_BC <= 0.0:
        raise ValueError("Factor of safety F_BC must be positive.")
    return q_ult / F_BC


def net_allowable_bearing_pressure(
    q_ult: float, F_BC: float, sigma_zD: float
) -> float:
    """Net allowable bearing pressure (Equation 5-14).

    The net allowable bearing pressure accounts for the overburden
    pressure at the bearing elevation (Peck et al. 1974).

    .. math::
        q_{all,net} \\leq \\frac{q_{ult}}{F_{BC}} - \\sigma_{zD}

    Parameters
    ----------
    q_ult : float
        Ultimate bearing capacity (psf, kPa, or consistent stress unit).
    F_BC : float
        Bearing capacity factor of safety (dimensionless).
    sigma_zD : float
        Vertical overburden pressure at bearing elevation (same stress
        unit).

    Returns
    -------
    float
        Net allowable bearing pressure [consistent units (same stress unit)].

    Raises
    ------
    ValueError
        If *F_BC* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-14,
    printed p. 279 (pdf_page_index 316).
    """
    if F_BC <= 0.0:
        raise ValueError("Factor of safety F_BC must be positive.")
    return q_ult / F_BC - sigma_zD


# ===========================================================================
# SECTION 5-3.1.2: Ultimate Bearing Capacity (Equations 5-15 through 5-17)
# ===========================================================================


def ultimate_bearing_capacity_drained(
    c_prime: float,
    sigma_zD_prime: float,
    gamma: float,
    B: float,
    Nc: float,
    Nq: float,
    N_gamma: float,
    psi_c: float = 1.0,
    psi_q: float = 1.0,
    psi_gamma: float = 1.0,
) -> float:
    """Ultimate bearing capacity -- effective stress (drained) analysis (Equation 5-15).

    For effective stress or drained analysis, the ultimate bearing capacity
    of the soil uses effective stress parameters and bearing capacity
    factors.

    .. math::
        q_{ult} = c' N_c \\Psi_c + \\sigma'_{zD} N_q \\Psi_q
                  + 0.5 \\gamma B N_\\gamma \\Psi_\\gamma

    Parameters
    ----------
    c_prime : float
        Effective stress cohesion (psf, kPa).
    sigma_zD_prime : float
        Effective vertical stress at bearing elevation (psf, kPa).
    gamma : float
        Average effective unit weight of soil between Df and Df + B
        (pcf, kN/m^3).
    B : float
        Foundation width (ft, m).  Use B' for eccentric loading.
    Nc : float
        Bearing capacity factor for cohesion term (dimensionless).
    Nq : float
        Bearing capacity factor for overburden term (dimensionless).
    N_gamma : float
        Bearing capacity factor for unit weight term (dimensionless).
    psi_c : float, optional
        Lumped correction factor for Nc term (default 1.0).
    psi_q : float, optional
        Lumped correction factor for Nq term (default 1.0).
    psi_gamma : float, optional
        Lumped correction factor for N_gamma term (default 1.0).

    Returns
    -------
    float
        Ultimate bearing capacity [consistent units (psf, kPa)].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-15,
    printed p. 288 (pdf_page_index 325).
    """
    return (
        c_prime * Nc * psi_c
        + sigma_zD_prime * Nq * psi_q
        + 0.5 * gamma * B * N_gamma * psi_gamma
    )


def ultimate_bearing_capacity_undrained_unsaturated(
    c: float,
    sigma_zD: float,
    gamma: float,
    B: float,
    Nc: float,
    Nq: float,
    N_gamma: float,
    psi_c: float = 1.0,
    psi_q: float = 1.0,
    psi_gamma: float = 1.0,
) -> float:
    """Ultimate bearing capacity -- undrained, unsaturated soils (Equation 5-16).

    For undrained conditions in unsaturated soils, the ultimate bearing
    capacity is calculated using total stress parameters (c, phi).

    .. math::
        q_{ult} = c \\cdot N_c \\Psi_c + \\sigma_{zD} N_q \\Psi_q
                  + 0.5 \\gamma B N_\\gamma \\Psi_\\gamma

    Parameters
    ----------
    c : float
        Undrained cohesion (psf, kPa).
    sigma_zD : float
        Total vertical stress at bearing elevation (psf, kPa).
    gamma : float
        Average total unit weight of soil between Df and Df + B
        (pcf, kN/m^3).
    B : float
        Foundation width (ft, m).
    Nc : float
        Bearing capacity factor for cohesion term (dimensionless).
    Nq : float
        Bearing capacity factor for overburden term (dimensionless).
    N_gamma : float
        Bearing capacity factor for unit weight term (dimensionless).
    psi_c : float, optional
        Lumped correction factor for Nc term (default 1.0).
    psi_q : float, optional
        Lumped correction factor for Nq term (default 1.0).
    psi_gamma : float, optional
        Lumped correction factor for N_gamma term (default 1.0).

    Returns
    -------
    float
        Ultimate bearing capacity [consistent units (psf, kPa)].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-16,
    printed p. 288 (pdf_page_index 325).
    """
    return (
        c * Nc * psi_c
        + sigma_zD * Nq * psi_q
        + 0.5 * gamma * B * N_gamma * psi_gamma
    )


def ultimate_bearing_capacity_undrained_saturated(
    s_u: float,
    sigma_zD: float,
    Nc: float,
    psi_c: float = 1.0,
    psi_q: float = 1.0,
) -> float:
    """Ultimate bearing capacity -- undrained, saturated soils (Equation 5-17).

    For undrained conditions in saturated soils (phi = 0), the bearing
    capacity simplifies to the cohesion and overburden terms only (Nq = 1,
    N_gamma = 0 for phi = 0).

    .. math::
        q_{ult} = s_u N_c \\Psi_c + \\sigma_{zD} \\Psi_q

    Parameters
    ----------
    s_u : float
        Undrained shear strength (psf, kPa).
    sigma_zD : float
        Total vertical stress at bearing elevation (psf, kPa).
    Nc : float
        Bearing capacity factor for phi = 0 (5.14 for Meyerhof/Hansen,
        5.7 for Terzaghi).
    psi_c : float, optional
        Lumped correction factor for Nc term (default 1.0).
    psi_q : float, optional
        Lumped correction factor for Nq term (default 1.0).  Nq = 1
        for phi = 0.

    Returns
    -------
    float
        Ultimate bearing capacity [consistent units (psf, kPa)].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-17,
    printed p. 288 (pdf_page_index 325).
    """
    return s_u * Nc * psi_c + sigma_zD * psi_q


# ===========================================================================
# SECTION 5-3.3: Lumped Correction Factors (Equations 5-18 through 5-20)
# ===========================================================================


def lumped_correction_factor_c(
    sc: float = 1.0,
    dc: float = 1.0,
    ic: float = 1.0,
    bc: float = 1.0,
    gc: float = 1.0,
) -> float:
    """Lumped correction factor for Nc term (Equation 5-18).

    Combines individual correction factors for shape, depth, load
    inclination, base inclination, and ground inclination.

    .. math::
        \\Psi_c = s_c \\cdot d_c \\cdot i_c \\cdot b_c \\cdot g_c

    Parameters
    ----------
    sc : float, optional
        Shape factor for Nc (default 1.0).
    dc : float, optional
        Depth factor for Nc (default 1.0).
    ic : float, optional
        Load inclination factor for Nc (default 1.0).
    bc : float, optional
        Sloping base factor for Nc (default 1.0).
    gc : float, optional
        Sloping ground factor for Nc (default 1.0).

    Returns
    -------
    float
        Lumped correction factor psi_c [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-18,
    printed p. 293 (pdf_page_index 330).
    """
    return sc * dc * ic * bc * gc


def lumped_correction_factor_q(
    sq: float = 1.0,
    dq: float = 1.0,
    iq: float = 1.0,
    bq: float = 1.0,
    gq: float = 1.0,
) -> float:
    """Lumped correction factor for Nq term (Equation 5-19).

    Combines individual correction factors for shape, depth, load
    inclination, base inclination, and ground inclination.

    .. math::
        \\Psi_q = s_q \\cdot d_q \\cdot i_q \\cdot b_q \\cdot g_q

    Parameters
    ----------
    sq : float, optional
        Shape factor for Nq (default 1.0).
    dq : float, optional
        Depth factor for Nq (default 1.0).
    iq : float, optional
        Load inclination factor for Nq (default 1.0).
    bq : float, optional
        Sloping base factor for Nq (default 1.0).
    gq : float, optional
        Sloping ground factor for Nq (default 1.0).

    Returns
    -------
    float
        Lumped correction factor psi_q [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-19,
    printed p. 293 (pdf_page_index 330).
    """
    return sq * dq * iq * bq * gq


def lumped_correction_factor_gamma(
    s_gamma: float = 1.0,
    d_gamma: float = 1.0,
    i_gamma: float = 1.0,
    b_gamma: float = 1.0,
    g_gamma: float = 1.0,
) -> float:
    """Lumped correction factor for N_gamma term (Equation 5-20).

    Combines individual correction factors for shape, depth, load
    inclination, base inclination, and ground inclination.

    .. math::
        \\Psi_\\gamma = s_\\gamma \\cdot d_\\gamma \\cdot i_\\gamma
                       \\cdot b_\\gamma \\cdot g_\\gamma

    Parameters
    ----------
    s_gamma : float, optional
        Shape factor for N_gamma (default 1.0).
    d_gamma : float, optional
        Depth factor for N_gamma (default 1.0).
    i_gamma : float, optional
        Load inclination factor for N_gamma (default 1.0).
    b_gamma : float, optional
        Sloping base factor for N_gamma (default 1.0).
    g_gamma : float, optional
        Sloping ground factor for N_gamma (default 1.0).

    Returns
    -------
    float
        Lumped correction factor psi_gamma [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-20,
    printed p. 293 (pdf_page_index 330).
    """
    return s_gamma * d_gamma * i_gamma * b_gamma * g_gamma


# ===========================================================================
# SECTION 5-3.3.3: Brinch Hansen phi=0 Correction (Equation 5-21)
# ===========================================================================


def hansen_correction_factor_c_phi0(
    sc: float = 0.0,
    dc: float = 0.0,
    ic: float = 0.0,
    bc: float = 0.0,
    gc: float = 0.0,
) -> float:
    """Brinch Hansen lumped correction factor for Nc term, phi = 0 (Equation 5-21).

    For the Brinch Hansen method with undrained shear strength (phi = 0),
    the lumped correction factor is additive rather than multiplicative.

    .. math::
        \\Psi_{c,BH,\\phi=0} = 1 + s_c + d_c - i_c - b_c - g_c

    Parameters
    ----------
    sc : float, optional
        Shape factor for Nc, phi = 0 (default 0.0).
        For vertical load: sc = 0.2 * (B/L).
    dc : float, optional
        Depth factor for Nc, phi = 0 (default 0.0).
        dc = 0.4 * k where k = Df/B for Df/B < 1,
        k = atan(Df/B) in radians for Df/B >= 1.
    ic : float, optional
        Inclination factor for Nc, phi = 0 (default 0.0).
        ic = 0.5 - 0.5 * sqrt(1 - H / (A' * Ca)).
    bc : float, optional
        Sloping base factor for Nc, phi = 0 (default 0.0).
        bc = eta / (pi/2 + 1).
    gc : float, optional
        Sloping ground factor for Nc, phi = 0 (default 0.0).
        gc = beta / (pi/2 + 1).

    Returns
    -------
    float
        Brinch Hansen correction factor psi_c for phi = 0 [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-21,
    printed p. 295 (pdf_page_index 332).
    """
    return 1.0 + sc + dc - ic - bc - gc


# ===========================================================================
# SECTION 5-3.4: Foundations Near Slopes (Equations 5-22 and 5-23)
# ===========================================================================


def stability_number_undrained(gamma: float, H: float, s_u: float) -> float:
    """Stability number for undrained slope conditions (Equation 5-22).

    The stability number incorporates the influence of slope stability on
    the bearing capacity for saturated undrained conditions (su, phi = 0).

    .. math::
        N_S = \\frac{\\gamma \\cdot H}{s_u}

    Parameters
    ----------
    gamma : float
        Total unit weight of the soil (pcf, kN/m^3).
    H : float
        Height of the slope (ft, m).
    s_u : float
        Undrained shear strength of the soil (psf, kPa).

    Returns
    -------
    float
        Stability number N_S [no unit printed].

    Raises
    ------
    ValueError
        If *s_u* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-22,
    printed p. 297 (pdf_page_index 334).
    """
    if s_u <= 0.0:
        raise ValueError("Undrained shear strength s_u must be positive.")
    return gamma * H / s_u


def stability_number_drained(gamma: float, H: float, c_prime: float) -> float:
    """Stability number for drained slope conditions (Equation 5-23).

    The stability number for soils modeled using an effective stress
    cohesion intercept to incorporate slope influence on bearing capacity.

    .. math::
        N_S = \\frac{\\gamma \\cdot H}{c'}

    Parameters
    ----------
    gamma : float
        Unit weight of the soil considering groundwater effects
        (pcf, kN/m^3).
    H : float
        Height of the slope (ft, m).
    c_prime : float
        Effective stress cohesion intercept (psf, kPa).

    Returns
    -------
    float
        Stability number N_S [no unit printed].

    Raises
    ------
    ValueError
        If *c_prime* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-23,
    printed p. 299 (pdf_page_index 336).
    """
    if c_prime <= 0.0:
        raise ValueError("Effective cohesion c' must be positive.")
    return gamma * H / c_prime


# ===========================================================================
# SECTION 5-3.6.1: Layered Soils -- Increasing su with Depth (Equation 5-24)
# ===========================================================================


def bearing_capacity_factor_Nc_increasing_su(
    k: float, B: float, s_u0: float
) -> float:
    """Modified Nc for clay with increasing su with depth (Equation 5-24).

    Based on an upper bound plasticity solution (Chi and Lin 2020), the
    bearing capacity factor Nc for a perfectly smooth strip footing on
    clay with increasing undrained strength with depth.

    .. math::
        N_c = 5.14 + \\frac{k \\cdot B}{s_{u0}}

    Parameters
    ----------
    k : float
        Rate of increase in undrained shear strength with depth
        (psf/ft, kPa/m).
    B : float
        Footing width (ft, m).
    s_u0 : float
        Undrained shear strength at the surface of the clay layer
        (psf, kPa).

    Returns
    -------
    float
        Modified bearing capacity factor Nc [dimensionless].

    Raises
    ------
    ValueError
        If *s_u0* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-24,
    printed p. 307 (pdf_page_index 344).
    """
    if s_u0 <= 0.0:
        raise ValueError("Surface undrained shear strength s_u0 must be positive.")
    return 5.14 + k * B / s_u0


# ===========================================================================
# SECTION 5-3.6.2: Layered Clay -- Modified Nc (Equation 5-25)
# ===========================================================================


def modified_Nc_rectangular_layered_clay(
    Nc_m_s: float, Nc_m_c: float, B: float, L: float
) -> float:
    """Modified Nc for rectangular footing on layered clay (Equation 5-25).

    For a layered clay soil profile, the modified bearing capacity factor
    for a rectangular foundation (Nc,m,r) can be estimated from the
    circular and strip factors.

    .. math::
        N_{c,m,r} = N_{c,m,c} + \\left(1 - \\frac{B}{L}\\right)
                    \\left(N_{c,m,s} - N_{c,m,c}\\right)

    Equivalently:

    .. math::
        N_{c,m,r} = N_{c,m,s} + \\frac{B}{L}
                    \\left(N_{c,m,c} - N_{c,m,s}\\right)

    Parameters
    ----------
    Nc_m_s : float
        Modified bearing capacity factor for strip footing from
        Figure 5-18(a) (dimensionless).
    Nc_m_c : float
        Modified bearing capacity factor for circular footing from
        Figure 5-18(b) (dimensionless).
    B : float
        Rectangular foundation width (ft, m).
    L : float
        Rectangular foundation length (ft, m).

    Returns
    -------
    float
        Modified bearing capacity factor Nc,m,r for rectangular footing
        [dimensionless].

    Raises
    ------
    ValueError
        If *L* is zero or negative, or if *B* > *L*.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-25,
    printed p. 309 (pdf_page_index 346).
    """
    if L <= 0.0:
        raise ValueError("Foundation length L must be positive.")
    if B <= 0.0:
        raise ValueError("Foundation width B must be positive.")
    if B > L:
        raise ValueError("Width B must not exceed length L.")
    return Nc_m_c + (1.0 - B / L) * (Nc_m_s - Nc_m_c)


# ===========================================================================
# SECTION 5-3.6.3: Mixed Soil Layers (Equations 5-26 through 5-28)
# ===========================================================================


def second_layer_thickness(
    B: float,
    H1: float,
    c1: float,
    c2: float,
    phi1_deg: float,
    phi2_deg: float,
) -> float:
    """Thickness H2 of the second layer (in the length unit of B) for a
    mixed sand and clay profile, Equation 5-26 of UFC 3-220-20 (method
    of Satyanarayana and Garg 1980, unsaturated undrained conditions):
    H2 = (2B - H1) (c1 + tan phi1) / (c2 + tan phi2).

    The equation is coded as printed: it adds a cohesion to a tangent,
    so the result depends on the unit of c1 and c2.  The manual's
    example (Figure 5-20) uses psf: B = 8 ft, H1 = 7 ft, c1 = 200 psf,
    phi1 = 28, c2 = 400 psf, phi2 = 20 gives H2 = 4.5 ft.  It applies
    unless a rigid boundary is met (Figure 5-14(b)).

    .. math::
        H_2 = (2B - H_1) \\left( \\frac{c_1 + \\tan\\phi_1}
              {c_2 + \\tan\\phi_2} \\right)

    Parameters
    ----------
    B : float
        Width of strip footing (ft, m).
    H1 : float
        Thickness of top layer below bearing elevation (ft, m).
    c1 : float
        Undrained cohesion of top layer (psf in the manual's example).
    c2 : float
        Undrained cohesion of bottom layer (same unit as *c1*).
    phi1_deg : float
        Undrained friction angle of top layer (degrees).
    phi2_deg : float
        Undrained friction angle of bottom layer (degrees).

    Returns
    -------
    float
        Thickness of the second layer H2 [consistent units (ft, m)], the unit
        of *B* and *H1*.

    Raises
    ------
    ValueError
        If c2 + tan(phi2) is zero.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-26,
    printed p. 311 (pdf_page_index 348); example in Figure 5-20,
    printed p. 312 (pdf_page_index 349).
    """
    denominator = c2 + math.tan(math.radians(phi2_deg))
    if denominator == 0.0:
        raise ValueError(
            "c2 + tan(phi2) must be non-zero for Equation 5-26."
        )
    numerator = c1 + math.tan(math.radians(phi1_deg))
    return (2.0 * B - H1) * numerator / denominator


def average_cohesion_mixed_layers(
    H1: float, c1: float, H2: float, c2: float
) -> float:
    """Average cohesion for mixed soil layers (Equation 5-27).

    Weighted average shear strength cohesion for the Satyanarayana and
    Garg (1980) method.

    .. math::
        c_{ave} = \\frac{H_1 c_1 + H_2 c_2}{H_1 + H_2}

    Parameters
    ----------
    H1 : float
        Thickness of top layer (ft, m).
    c1 : float
        Undrained cohesion of top layer (psf, kPa).
    H2 : float
        Thickness of second layer (ft, m).
    c2 : float
        Undrained cohesion of bottom layer (psf, kPa).

    Returns
    -------
    float
        Average cohesion c_ave [consistent units (psf, kPa)].

    Raises
    ------
    ValueError
        If *H1 + H2* is zero.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-27,
    printed p. 312 (pdf_page_index 349).
    """
    total_H = H1 + H2
    if total_H <= 0.0:
        raise ValueError("Total layer thickness must be positive.")
    return (H1 * c1 + H2 * c2) / total_H


def average_friction_angle_mixed_layers(
    H1: float, phi1_deg: float, H2: float, phi2_deg: float
) -> float:
    """Average friction angle for mixed soil layers (Equation 5-28).

    Weighted average friction angle for the Satyanarayana and Garg (1980)
    method.  The averaging is performed on the tangent of the friction
    angles.

    .. math::
        \\tan\\phi_{ave} = \\frac{H_1 \\tan\\phi_1 + H_2 \\tan\\phi_2}
                          {H_1 + H_2}

    Parameters
    ----------
    H1 : float
        Thickness of top layer (ft, m).
    phi1_deg : float
        Undrained friction angle of top layer (degrees).
    H2 : float
        Thickness of second layer (ft, m).
    phi2_deg : float
        Undrained friction angle of bottom layer (degrees).

    Returns
    -------
    float
        Average friction angle phi_ave [degrees].

    Raises
    ------
    ValueError
        If *H1 + H2* is zero.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-28,
    printed p. 312 (pdf_page_index 349).
    """
    total_H = H1 + H2
    if total_H <= 0.0:
        raise ValueError("Total layer thickness must be positive.")
    phi1 = math.radians(phi1_deg)
    phi2 = math.radians(phi2_deg)
    tan_ave = (H1 * math.tan(phi1) + H2 * math.tan(phi2)) / total_H
    return math.degrees(math.atan(tan_ave))


# ===========================================================================
# SECTION 5-3.7: Bearing Capacity of Rock (Equations 5-29 through 5-32)
# ===========================================================================


def rock_bearing_capacity_factor_Nc(phi_rf_deg: float) -> float:
    """Bearing capacity factor Nc for rock (Equation 5-29).

    Rock bearing capacity factor per Stagg and Zienkiewicz (1968) based
    on the rock fracture friction angle.

    .. math::
        N_c = 5 \\tan^4\\!\\left(45^\\circ + \\frac{\\phi'_{rf}}{2}\\right)

    Parameters
    ----------
    phi_rf_deg : float
        Rock fracture friction angle including the effect of asperities
        (degrees).

    Returns
    -------
    float
        Bearing capacity factor Nc for rock [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-29,
    printed p. 317 (pdf_page_index 354).
    """
    angle = math.radians(45.0 + phi_rf_deg / 2.0)
    return 5.0 * math.tan(angle) ** 4


def rock_bearing_capacity_factor_Nq(phi_rf_deg: float) -> float:
    """Bearing capacity factor Nq for rock (Equation 5-30).

    Rock bearing capacity factor per Stagg and Zienkiewicz (1968).

    .. math::
        N_q = \\tan^6\\!\\left(45^\\circ + \\frac{\\phi'_{rf}}{2}\\right)

    Parameters
    ----------
    phi_rf_deg : float
        Rock fracture friction angle including the effect of asperities
        (degrees).

    Returns
    -------
    float
        Bearing capacity factor Nq for rock [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-30,
    printed p. 317 (pdf_page_index 354).
    """
    angle = math.radians(45.0 + phi_rf_deg / 2.0)
    return math.tan(angle) ** 6


def rock_bearing_capacity_factor_Ngamma(Nq: float) -> float:
    """Bearing capacity factor N_gamma for rock (Equation 5-31).

    Rock bearing capacity factor per Stagg and Zienkiewicz (1968).

    .. math::
        N_\\gamma = N_q + 1

    Parameters
    ----------
    Nq : float
        Bearing capacity factor Nq for rock (dimensionless).

    Returns
    -------
    float
        Bearing capacity factor N_gamma for rock [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-31,
    printed p. 317 (pdf_page_index 354).
    """
    return Nq + 1.0


def rock_reduced_ultimate_bearing_capacity(
    q_ult: float, RQD: float
) -> float:
    """Reduced ultimate bearing capacity for rock using RQD (Equation 5-32).

    Incorporates Rock Quality Designation as a reduction to the ultimate
    bearing capacity (Bowles 1996).

    .. math::
        q'_{ult} = q_{ult} \\cdot RQD^2

    Parameters
    ----------
    q_ult : float
        Ultimate bearing capacity of intact rock (psf, kPa).
    RQD : float
        Rock Quality Designation expressed as a decimal (0 to 1),
        evaluated to a depth of B below the footing.

    Returns
    -------
    float
        Reduced ultimate bearing capacity [consistent units (psf, kPa)].

    Raises
    ------
    ValueError
        If *RQD* is outside the range [0, 1].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-32,
    printed p. 317 (pdf_page_index 354).
    """
    if RQD < 0.0 or RQD > 1.0:
        raise ValueError("RQD must be between 0 and 1 (decimal, not percent).")
    return q_ult * RQD ** 2


# ===========================================================================
# SECTION 5-4.2.1: Rigid Foundation Criteria (Equations 5-33 and 5-34)
# ===========================================================================


def relative_stiffness_factor(
    E_prime_Ib: float, Es: float, B: float
) -> float:
    """Relative stiffness factor Kr for rigid foundation check (Equation 5-33).

    Determines whether a combined footing or mat foundation may be
    designed as a rigid structure (Meyerhof 1953).  When Kr >= 0.5, the
    foundation may be considered rigid.

    .. math::
        K_r = \\frac{E' I_b}{E_s \\cdot B^3}

    Parameters
    ----------
    E_prime_Ib : float
        Flexural stiffness of the structure, E' * Ib (force-length^2,
        e.g., lb-ft^2 or kN-m^2).
    Es : float
        Soil modulus (psf, kPa, or consistent stress unit).
    B : float
        Width of foundation (ft, m).

    Returns
    -------
    float
        Relative stiffness factor Kr [dimensionless].

    Raises
    ------
    ValueError
        If *Es* or *B* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-33,
    printed p. 320 (pdf_page_index 357).
    """
    if Es <= 0.0:
        raise ValueError("Soil modulus Es must be positive.")
    if B <= 0.0:
        raise ValueError("Foundation width B must be positive.")
    return E_prime_Ib / (Es * B ** 3)


def foundation_stiffness_factor(
    ks: float, B: float, Ec: float, I: float
) -> float:
    """Foundation stiffness factor lambda for rigidity assessment (Equation 5-34).

    Used to determine if continuous foundations may be considered rigid.
    A foundation is rigid if the average spacing of two adjacent column
    spans is less than 1.75 / lambda.

    .. math::
        \\lambda = \\sqrt[4]{\\frac{k_s}{4 E_c I / B}}

    which can be rewritten as:

    .. math::
        \\lambda = \\left(\\frac{k_s}{4 E_c I / B}\\right)^{1/4}

    Parameters
    ----------
    ks : float
        Modulus of subgrade reaction (pci, kN/m^3, or consistent unit,
        force per cubic length).
    B : float
        Width of footing (ft, m, or consistent length unit).
    Ec : float
        Modulus of concrete (psi, kPa, or consistent stress unit).
    I : float
        Moment of inertia of the footing cross-section (in^4, m^4, or
        consistent unit).

    Returns
    -------
    float
        Stiffness factor lambda [consistent units (1/length)].

    Raises
    ------
    ValueError
        If any input is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-34,
    printed p. 321 (pdf_page_index 358).
    """
    if ks <= 0.0:
        raise ValueError("Subgrade modulus ks must be positive.")
    if B <= 0.0:
        raise ValueError("Foundation width B must be positive.")
    if Ec <= 0.0:
        raise ValueError("Concrete modulus Ec must be positive.")
    if I <= 0.0:
        raise ValueError("Moment of inertia I must be positive.")
    return (ks / (4.0 * Ec * I / B)) ** 0.25


# ===========================================================================
# SECTION 5-4.5: Modulus of Subgrade Reaction (Equations 5-35 through 5-37)
# ===========================================================================


def modulus_of_subgrade_reaction(q: float, s: float) -> float:
    """Modulus of subgrade reaction ks (Equation 5-35).

    The ratio of the contact pressure to the corresponding settlement.

    .. math::
        k_s = \\frac{q}{s}

    Parameters
    ----------
    q : float
        Contact pressure acting perpendicular to the contact area
        (psf, kPa).
    s : float
        Soil settlement (ft, m, or consistent length unit).

    Returns
    -------
    float
        Modulus of subgrade reaction ks [consistent units (force/length^3)].

    Raises
    ------
    ValueError
        If *s* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-35,
    printed p. 323 (pdf_page_index 360).
    """
    if s <= 0.0:
        raise ValueError("Settlement s must be positive.")
    return q / s


def subgrade_modulus_from_plate_load_test(
    kp: float, Bp: float, B: float, n: float = 0.5
) -> float:
    """Modulus of subgrade reaction ks (in the unit of kp, force/length^3)
    for a footing from a plate load test, Equation 5-36 of UFC 3-220-20
    (Sowers 1977): ks = kp (Bp/B)^n with n = 0.5 to 0.7.  The manual
    allows it only for a footing no wider than 5 ft on uniform
    soil within the depth of influence, and says plate load test results
    cannot be scaled for larger footings and mats; the function does not
    know the unit of B and does not check this.

    The depth of influence is 2B for square footings or 4B for continuous
    footings.

    .. math::
        k_s = k_p \\left(\\frac{B_p}{B}\\right)^n

    Parameters
    ----------
    kp : float
        Modulus of subgrade reaction from the plate load test
        (force/length^3).
    Bp : float
        Width of the test plate (ft, m).
    B : float
        Width of the foundation (ft, m).
    n : float, optional
        Exponent, typically 0.5 to 0.7 (default 0.5).

    Returns
    -------
    float
        Estimated modulus of subgrade reaction ks [consistent units
        (force/length^3)].

    Raises
    ------
    ValueError
        If *Bp* or *B* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-36,
    printed p. 324 (pdf_page_index 361).
    """
    if Bp <= 0.0 or B <= 0.0:
        raise ValueError("Plate width Bp and foundation width B must be positive.")
    if not (0.0 < n <= 1.0):
        raise ValueError("Exponent n should be between 0 and 1.")
    return kp * (Bp / B) ** n


def subgrade_modulus_from_elastic_parameters(
    B: float, Es: float, mu0: float, mu1: float
) -> float:
    """Subgrade modulus estimated from elastic parameters (Equation 5-37).

    Using the definition of ks and the elastic settlement equation, the
    subgrade modulus can be estimated from the foundation size and soil
    elastic properties.

    .. math::
        k_s = \\frac{1}{B \\, \\mu_0 \\, \\mu_1} \\cdot E_s

    Parameters
    ----------
    B : float
        Width of the foundation (ft, m).
    Es : float
        Elastic modulus of the soil within the zone of influence
        (psf, kPa).
    mu0 : float
        Influence factor related to embedment of the load and Poisson's
        ratio (dimensionless).
    mu1 : float
        Influence factor related to problem geometry and Poisson's ratio
        (dimensionless).

    Returns
    -------
    float
        Estimated modulus of subgrade reaction ks [consistent units
        (force/length^3)].

    Raises
    ------
    ValueError
        If any input is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-37,
    printed p. 325 (pdf_page_index 362).
    """
    if B <= 0.0:
        raise ValueError("Foundation width B must be positive.")
    if Es <= 0.0:
        raise ValueError("Soil elastic modulus Es must be positive.")
    if mu0 <= 0.0 or mu1 <= 0.0:
        raise ValueError("Influence factors mu0 and mu1 must be positive.")
    return Es / (B * mu0 * mu1)


# ===========================================================================
# SECTION 5-4.5.3: Poisson's Ratio from Friction Angle (Equation 5-38)
# ===========================================================================


def poissons_ratio_from_friction_angle(phi_prime_deg: float) -> float:
    """Drained Poisson's ratio nu (dimensionless) from the effective
    friction angle, Equation 5-38 of UFC 3-220-20:
    nu = (1 - sin phi') / (2 - sin phi'); the manual gives its range as
    phi' = 20 to 55 degrees, where nu runs from 0.4 to 0.15, and the
    function answers outside that range without a warning.

    For undrained conditions nu is 0.5; Table 5-16 lists typical values.

    .. math::
        \\nu = \\frac{1 - \\sin\\phi'}{2 - \\sin\\phi'}

    Parameters
    ----------
    phi_prime_deg : float
        Effective friction angle (degrees).

    Returns
    -------
    float
        Drained Poisson's ratio [dimensionless].

    Raises
    ------
    ValueError
        If *phi_prime_deg* is non-positive or >= 90 degrees.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-38,
    printed p. 329 (pdf_page_index 366).
    """
    if phi_prime_deg <= 0.0 or phi_prime_deg >= 90.0:
        raise ValueError(
            "Friction angle must be between 0 and 90 degrees (exclusive)."
        )
    sin_phi = math.sin(math.radians(phi_prime_deg))
    return (1.0 - sin_phi) / (2.0 - sin_phi)


# ===========================================================================
# SECTION 5-4.5.4: Time-Dependent Subgrade Modulus (Equation 5-39)
# ===========================================================================


def subgrade_modulus_time_dependent(
    s: float, sc: float, ks: float
) -> float:
    """Reduced subgrade modulus for time-dependent settlement (Equation 5-39).

    When the structure imposes stresses beyond the preconsolidation stress,
    or when recompression/heave occurs due to excavation, consolidation
    settlement must be added to the elastic settlement.

    .. math::
        k_{sc} = \\frac{s \\cdot k_s}{s + s_c}

    where s is the elastic settlement and s_c is the consolidation
    settlement.

    Parameters
    ----------
    s : float
        Elastic settlement (ft, m, or consistent length unit).
    sc : float
        Consolidation settlement (ft, m, or consistent length unit).
    ks : float
        Modulus of subgrade reaction from elastic analysis
        (force/length^3).

    Returns
    -------
    float
        Reduced subgrade modulus ksc [consistent units (force/length^3)].

    Raises
    ------
    ValueError
        If total settlement (s + sc) is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-39,
    printed p. 330 (pdf_page_index 367).
    """
    total = s + sc
    if total <= 0.0:
        raise ValueError("Total settlement (s + sc) must be positive.")
    return s * ks / total


# ===========================================================================
# SECTION 5-4.6: Node Coupling of Soil Effects (Equation 5-40)
# ===========================================================================


def winkler_spring_stiffness(ks: float, A_cont: float) -> float:
    """Winkler spring stiffness at a node (Equation 5-40).

    At the interface between a mat and the soil, the soil response is
    concentrated at nodes.  The spring stiffness K for each node is the
    subgrade modulus multiplied by the contributing area.

    .. math::
        K = k_s \\cdot A_{cont}

    Parameters
    ----------
    ks : float
        Modulus of subgrade reaction (force/length^3).
    A_cont : float
        Contributing area to the node (ft^2, m^2).

    Returns
    -------
    float
        Winkler spring stiffness K [consistent units (force/length)].

    Raises
    ------
    ValueError
        If *ks* or *A_cont* is negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-40,
    printed p. 330 (pdf_page_index 367).
    """
    if ks < 0.0:
        raise ValueError("Subgrade modulus ks must be non-negative.")
    if A_cont < 0.0:
        raise ValueError("Contributing area A_cont must be non-negative.")
    return ks * A_cont


# ===========================================================================
# SECTION 5-4.7: Indirect Method for Coupling (Equation 5-41)
# ===========================================================================


def subgrade_modulus_coupling(
    ks_edge: float,
    sigma_z_ave_edge: float,
    sigma_z_ave_i: float,
) -> float:
    """Subgrade modulus at interior point using coupling method (Equation 5-41).

    Bowles (1996) indirect method for considering coupling in a mat
    foundation.  The ks at an interior point is scaled from the edge
    ks value using the ratio of average vertical stresses.

    .. math::
        k_{s,i} = k_s \\left(\\frac{\\sigma_{z,ave}(1)}
                  {\\sigma_{z,ave}(i)}\\right)

    Parameters
    ----------
    ks_edge : float
        Modulus of subgrade reaction at the edge point (Point 1)
        (force/length^3).
    sigma_z_ave_edge : float
        Average vertical stress at the edge point (psf, kPa).
    sigma_z_ave_i : float
        Average vertical stress at interior point i (psf, kPa).

    Returns
    -------
    float
        Modulus of subgrade reaction at interior point i [consistent units
        (force/length^3)].

    Raises
    ------
    ValueError
        If *sigma_z_ave_i* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-41,
    printed p. 332 (pdf_page_index 369).
    """
    if sigma_z_ave_i <= 0.0:
        raise ValueError(
            "Average vertical stress at interior point must be positive."
        )
    return ks_edge * (sigma_z_ave_edge / sigma_z_ave_i)


# ===========================================================================
# SECTION 5-4.8: Floating Mat Foundation (Equation 5-42)
# ===========================================================================


def floating_mat_net_pressure(
    W_structure: float, W_excavated: float, A_mat: float
) -> float:
    """Net pressure for a floating mat foundation (Equation 5-42).

    The net pressure that results in settlement for a floating mat
    foundation.  If the structure weight equals the excavated soil weight,
    the net pressure is zero and settlement relates only to recompression
    or heave.

    .. math::
        q_{net} = \\frac{W_{structure} - W_{excavated}}{A_{mat}}

    Parameters
    ----------
    W_structure : float
        Total weight of the structure (lb, kN, or consistent force unit).
    W_excavated : float
        Total weight of excavated soil (same force unit).
    A_mat : float
        Area of the mat foundation (ft^2, m^2).

    Returns
    -------
    float
        Net bearing pressure for settlement analysis [consistent units (psf,
        kPa)].

    Raises
    ------
    ValueError
        If *A_mat* is zero or negative.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Equation 5-42,
    printed p. 334 (pdf_page_index 371).
    """
    if A_mat <= 0.0:
        raise ValueError("Mat area A_mat must be positive.")
    return (W_structure - W_excavated) / A_mat


# ===========================================================================
# BEARING CAPACITY FACTOR HELPER FUNCTIONS
# (Supporting equations referenced in Tables 5-2, 5-5, 5-6, 5-8
#  and Figure 5-5 -- Terzaghi, Meyerhof, and Brinch Hansen methods)
# ===========================================================================


def _Kp(phi_deg: float) -> float:
    """Rankine passive earth pressure coefficient.

    .. math::
        K_P = \\tan^2(\\pi/4 + \\phi'/2)

    Used internally by Meyerhof bearing capacity and correction factors.
    """
    return math.tan(math.radians(45.0 + phi_deg / 2.0)) ** 2


# ---------------------------------------------------------------------------
# Meyerhof / Brinch Hansen bearing capacity factors
# ---------------------------------------------------------------------------


def meyerhof_hansen_Nq(phi_deg: float) -> float:
    """Bearing capacity factor Nq -- Meyerhof and Brinch Hansen (Table 5-2).

    .. math::
        N_q = \\tan^2\\!\\left(\\frac{\\pi}{4} + \\frac{\\phi'}{2}\\right)
              e^{\\pi \\tan\\phi'}

    Parameters
    ----------
    phi_deg : float
        Friction angle (degrees).

    Returns
    -------
    float
        Bearing capacity factor Nq [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-2 / Table 5-6 /
    Table 5-8, printed pp. 289-296 (pdf_page_index 326-333).
    """
    phi = math.radians(phi_deg)
    return math.tan(math.pi / 4.0 + phi / 2.0) ** 2 * math.exp(
        math.pi * math.tan(phi)
    )


def meyerhof_hansen_Nc(phi_deg: float) -> float:
    """Bearing capacity factor Nc -- Meyerhof and Brinch Hansen (Table 5-2).

    For phi > 0:

    .. math::
        N_c = (N_q - 1) \\cot\\phi'

    For phi = 0, Nc = 5.14.

    Parameters
    ----------
    phi_deg : float
        Friction angle (degrees).

    Returns
    -------
    float
        Bearing capacity factor Nc [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-2 / Table 5-6 /
    Table 5-8, printed pp. 289-296 (pdf_page_index 326-333).
    """
    if phi_deg == 0.0:
        return 5.14
    Nq = meyerhof_hansen_Nq(phi_deg)
    phi = math.radians(phi_deg)
    return (Nq - 1.0) / math.tan(phi)


def meyerhof_Ngamma(phi_deg: float) -> float:
    """Bearing capacity factor N_gamma -- Meyerhof (Table 5-2 / Table 5-6).

    .. math::
        N_\\gamma = (N_q - 1) \\tan(1.4\\phi')

    Parameters
    ----------
    phi_deg : float
        Friction angle (degrees).

    Returns
    -------
    float
        Bearing capacity factor N_gamma [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-6,
    printed p. 294 (pdf_page_index 331).
    """
    Nq = meyerhof_hansen_Nq(phi_deg)
    return (Nq - 1.0) * math.tan(math.radians(1.4 * phi_deg))


def hansen_Ngamma(phi_deg: float) -> float:
    """Bearing capacity factor N_gamma -- Brinch Hansen (Table 5-2 / Table 5-8).

    .. math::
        N_\\gamma = 1.5 (N_q - 1) \\tan\\phi'

    Parameters
    ----------
    phi_deg : float
        Friction angle (degrees).

    Returns
    -------
    float
        Bearing capacity factor N_gamma [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-8,
    printed p. 296 (pdf_page_index 333).
    """
    Nq = meyerhof_hansen_Nq(phi_deg)
    return 1.5 * (Nq - 1.0) * math.tan(math.radians(phi_deg))


# ---------------------------------------------------------------------------
# Terzaghi bearing capacity factors (Table 5-2, approximations per
# Coduto et al. 2016)
# ---------------------------------------------------------------------------


def terzaghi_Nc(phi_deg: float) -> float:
    """Bearing capacity factor Nc -- Terzaghi (Table 5-2).

    For phi = 0, Nc = 5.7. For phi > 0, uses the Coduto et al. (2016)
    approximation tabulated in the UFC.

    .. math::
        N_c = \\cot\\phi' \\left[\\frac{e^{2(3\\pi/4 - \\phi'/2)\\tan\\phi'}}
              {2\\cos^2(45+\\phi'/2)} - 1\\right]

    Parameters
    ----------
    phi_deg : float
        Friction angle (degrees), 0 to 50.

    Returns
    -------
    float
        Bearing capacity factor Nc [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-2,
    printed p. 289 (pdf_page_index 326).
    """
    if phi_deg == 0.0:
        return 5.7
    phi = math.radians(phi_deg)
    # Terzaghi's Nq
    Nq = terzaghi_Nq(phi_deg)
    return (Nq - 1.0) / math.tan(phi)


def terzaghi_Nq(phi_deg: float) -> float:
    """Bearing capacity factor Nq -- Terzaghi (Table 5-2).

    Uses the exact Terzaghi formulation:

    .. math::
        N_q = \\frac{e^{2(3\\pi/4 - \\phi'/2)\\tan\\phi'}}
              {2\\cos^2(45^\\circ + \\phi'/2)}

    Parameters
    ----------
    phi_deg : float
        Friction angle (degrees).

    Returns
    -------
    float
        Bearing capacity factor Nq [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-2,
    printed p. 289 (pdf_page_index 326).
    """
    if phi_deg == 0.0:
        return 1.0
    phi = math.radians(phi_deg)
    exponent = 2.0 * (3.0 * math.pi / 4.0 - phi / 2.0) * math.tan(phi)
    cos_term = math.cos(math.radians(45.0 + phi_deg / 2.0))
    return math.exp(exponent) / (2.0 * cos_term ** 2)


def terzaghi_Ngamma(phi_deg: float) -> float:
    """Bearing capacity factor N_gamma -- Terzaghi (Table 5-2).

    Uses the approximation by Coduto et al. (2016) that matches the
    tabulated values in the UFC.

    .. math::
        N_\\gamma \\approx 2(N_q + 1)\\tan\\phi' \\cdot \\frac{1}{1 + 0.4\\sin(4\\phi')}

    This is an approximation; for phi = 0, N_gamma = 0.

    Parameters
    ----------
    phi_deg : float
        Friction angle (degrees).

    Returns
    -------
    float
        Bearing capacity factor N_gamma [dimensionless].

    Notes
    -----
    The approximation gives values consistent with Table 5-2 per the
    UFC note that Coduto et al. (2016) approximation is used.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-2,
    printed p. 289 (pdf_page_index 326).
    """
    if phi_deg == 0.0:
        return 0.0
    phi = math.radians(phi_deg)
    Nq = terzaghi_Nq(phi_deg)
    return 2.0 * (Nq + 1.0) * math.tan(phi) / (1.0 + 0.4 * math.sin(4.0 * phi))


# ===========================================================================
# TERZAGHI SHAPE FACTORS (Table 5-5)
# ===========================================================================


def terzaghi_shape_factors(
    shape: str,
) -> Tuple[float, float, float]:
    """Terzaghi shape factors (Table 5-5).

    Returns the shape factors (sc, sq, s_gamma) for the Terzaghi method.

    Parameters
    ----------
    shape : str
        Foundation shape: 'continuous' (strip), 'square', or 'circular'.

    Returns
    -------
    sc : float
        Shape factor s_c [dimensionless].
    sq : float
        Shape factor s_q [dimensionless].
    s_gamma : float
        Shape factor s_gamma [dimensionless].

    Raises
    ------
    ValueError
        If *shape* is not recognized.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-5,
    printed p. 294 (pdf_page_index 331).
    """
    shape_lower = shape.lower().strip()
    if shape_lower in ("continuous", "strip"):
        return (1.0, 1.0, 1.0)
    elif shape_lower == "square":
        return (1.3, 1.0, 0.8)
    elif shape_lower in ("circular", "circle"):
        return (1.3, 1.0, 0.6)
    else:
        raise ValueError(
            f"Unknown shape '{shape}'. Use 'continuous', 'square', or 'circular'."
        )


# ===========================================================================
# MEYERHOF CORRECTION FACTORS (Table 5-6)
# ===========================================================================


def _meyerhof_table_5_6_rows(phi_deg: float, factor: str) -> None:
    """Table 5-6 has two rows for the shape and depth factors, phi = 0 and
    phi' > 10 degrees; a friction angle between them has no row."""
    if 0.0 < phi_deg <= 10.0:
        raise ValueError(
            f"Table 5-6 gives the Meyerhof (1963) {factor} factors for "
            f"phi = 0 and for phi' > 10 degrees only; it has no row for "
            f"phi = {phi_deg:g} degrees."
        )


def meyerhof_shape_factors(
    B: float, L: float, phi_deg: float
) -> Tuple[float, float, float]:
    """Meyerhof (1963) shape factors (sc, sq, s_gamma), dimensionless, in
    that order, from Table 5-6 of UFC 3-220-20, which gives them for
    phi = 0 and for phi' > 10 degrees only (a friction angle between 0
    and 10 degrees is refused).

    phi = 0: sc = 1 + 0.2 (B/L), sq = s_gamma = 1.  phi' > 10 degrees:
    sc = 1 + 0.2 (B/L) KP, sq = s_gamma = 1 + 0.1 (B/L) KP, with
    KP = tan^2(pi/4 + phi'/2).  Note A of the table: use B/L = 1 for a
    circle; do not combine factors for shape and inclined load.

    Parameters
    ----------
    B : float
        Foundation width (ft, m).  Use B/L = 1 for circle.
    L : float
        Foundation length (ft, m).
    phi_deg : float
        Friction angle (degrees): 0, or above 10.

    Returns
    -------
    sc : float
        Shape factor s_c [dimensionless].
    sq : float
        Shape factor s_q [dimensionless].
    s_gamma : float
        Shape factor s_gamma [dimensionless].

    Raises
    ------
    ValueError
        If *phi_deg* is above 0 and not above 10 degrees.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-6,
    printed p. 294 (pdf_page_index 331).
    """
    _meyerhof_table_5_6_rows(phi_deg, "shape")
    Kp = _Kp(phi_deg)
    ratio = B / L if L > 0.0 else 0.0
    if phi_deg == 0.0:
        sc = 1.0 + 0.2 * ratio
        sq = 1.0
        s_gamma = 1.0
    else:
        sc = 1.0 + 0.2 * ratio * Kp
        sq = 1.0 + 0.1 * ratio * Kp
        s_gamma = 1.0 + 0.1 * ratio * Kp
    return (sc, sq, s_gamma)


def meyerhof_depth_factors(
    Df: float, B: float, phi_deg: float
) -> Tuple[float, float, float]:
    """Meyerhof (1963) depth factors (dc, dq, d_gamma), dimensionless, in
    that order, from Table 5-6 of UFC 3-220-20, which gives them for
    phi = 0 and for phi' > 10 degrees only (a friction angle between 0
    and 10 degrees is refused).

    dc = 1 + 0.2 k KP^0.5 in both rows.  phi = 0: dq = d_gamma = 1.
    phi' > 10 degrees: dq = d_gamma = 1 + 0.1 k KP^0.5, with k = Df/B and
    KP = tan^2(pi/4 + phi'/2).

    Parameters
    ----------
    Df : float
        Foundation depth (ft, m).
    B : float
        Foundation width (ft, m).
    phi_deg : float
        Friction angle (degrees): 0, or above 10.

    Returns
    -------
    dc : float
        Depth factor d_c [dimensionless].
    dq : float
        Depth factor d_q [dimensionless].
    d_gamma : float
        Depth factor d_gamma [dimensionless].

    Raises
    ------
    ValueError
        If *B* is not positive, or *phi_deg* is above 0 and not above
        10 degrees.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-6,
    printed p. 294 (pdf_page_index 331).
    """
    _meyerhof_table_5_6_rows(phi_deg, "depth")
    if B <= 0.0:
        raise ValueError("Foundation width B must be positive.")
    k = Df / B
    Kp = _Kp(phi_deg)
    if phi_deg == 0.0:
        dc = 1.0 + 0.2 * k * math.sqrt(Kp)
        dq = 1.0
        d_gamma = 1.0
    else:
        dc = 1.0 + 0.2 * k * math.sqrt(Kp)
        dq = 1.0 + 0.1 * k * math.sqrt(Kp)
        d_gamma = 1.0 + 0.1 * k * math.sqrt(Kp)
    return (dc, dq, d_gamma)


def meyerhof_inclination_factors(
    theta_deg: float, phi_deg: float
) -> Tuple[float, float, float]:
    """Meyerhof (1963) load inclination factors (Table 5-6).

    Parameters
    ----------
    theta_deg : float
        Angle of load inclination from vertical (degrees).
        theta = atan(H/V) where H = horizontal load, V = vertical load.
        Must be less than phi' for i_gamma.
    phi_deg : float
        Friction angle (degrees).

    Returns
    -------
    ic : float
        Inclination factor i_c [dimensionless].
    iq : float
        Inclination factor i_q [dimensionless].
    i_gamma : float
        Inclination factor i_gamma [dimensionless].

    Raises
    ------
    ValueError
        If *theta_deg* >= *phi_deg* for frictional soils.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-6,
    printed p. 294 (pdf_page_index 331).
    """
    theta = math.radians(theta_deg)
    ic = (1.0 - 2.0 * theta / math.pi) ** 2
    iq = (1.0 - 2.0 * theta / math.pi) ** 2
    if phi_deg > 0.0:
        if theta_deg >= phi_deg:
            raise ValueError(
                "Load inclination angle theta must be less than phi'."
            )
        i_gamma = (1.0 - theta / math.radians(phi_deg)) ** 2
    else:
        i_gamma = 1.0
    return (ic, iq, i_gamma)


# ===========================================================================
# BRINCH HANSEN CORRECTION FACTORS (Tables 5-7 and 5-8)
# ===========================================================================


def _hansen_k(Df: float, B: float) -> float:
    """Depth parameter k for Brinch Hansen factors (Table 5-7/5-8 note).

    For Df/B < 1: k = Df/B.
    For Df/B >= 1: k = atan(Df/B) in radians.
    """
    if B <= 0.0:
        raise ValueError("Foundation width B must be positive.")
    ratio = Df / B
    if ratio < 1.0:
        return ratio
    return math.atan(ratio)


def hansen_shape_factors_phi0(
    B: float, L: float
) -> Tuple[float, float]:
    """Brinch Hansen shape factors for phi = 0, vertical load (Table 5-7).

    Parameters
    ----------
    B : float
        Foundation width (ft, m).
    L : float
        Foundation length (ft, m).

    Returns
    -------
    sc : float
        Shape factor s_c = 0.2 (B/L) [dimensionless].
    sq : float
        Shape factor s_q [dimensionless], 0 (no correction for the q term at
        phi = 0).

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-7,
    printed p. 295 (pdf_page_index 332).
    """
    if L <= 0.0:
        raise ValueError("Foundation length L must be positive.")
    sc = 0.2 * (B / L)
    return (sc, 0.0)


def hansen_depth_factor_phi0(Df: float, B: float) -> float:
    """Brinch Hansen depth factor for phi = 0 (Table 5-7).

    .. math::
        d_c = 0.4 k

    Parameters
    ----------
    Df : float
        Foundation depth (ft, m).
    B : float
        Foundation width (ft, m).

    Returns
    -------
    float
        Depth factor dc for phi = 0 [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-7,
    printed p. 295 (pdf_page_index 332).
    """
    k = _hansen_k(Df, B)
    return 0.4 * k


def hansen_inclination_factor_phi0(
    H: float, A_prime: float, Ca: float
) -> float:
    """Brinch Hansen inclination factor for phi = 0 (Table 5-7).

    .. math::
        i_c = 0.5 - 0.5\\sqrt{1 - \\frac{H}{A' \\cdot C_a}}

    Parameters
    ----------
    H : float
        Horizontal component of the load (lb, kN).
    A_prime : float
        Equivalent bearing area (ft^2, m^2).
    Ca : float
        Base adhesion (psf, kPa).

    Returns
    -------
    float
        Inclination factor ic for phi = 0 [dimensionless].

    Raises
    ------
    ValueError
        If H / (A' * Ca) > 1.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-7,
    printed p. 295 (pdf_page_index 332).
    """
    if A_prime <= 0.0 or Ca <= 0.0:
        raise ValueError("A_prime and Ca must be positive.")
    ratio = H / (A_prime * Ca)
    if ratio > 1.0:
        raise ValueError("H / (A' * Ca) must not exceed 1.0.")
    return 0.5 - 0.5 * math.sqrt(1.0 - ratio)


def hansen_base_factor_phi0(eta_rad: float) -> float:
    """Brinch Hansen sloping base factor for phi = 0 (Table 5-7).

    .. math::
        b_c = \\frac{\\eta}{\\pi/2 + 1}

    Parameters
    ----------
    eta_rad : float
        Base inclination angle (radians).

    Returns
    -------
    float
        Base inclination factor bc for phi = 0 [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-7,
    printed p. 295 (pdf_page_index 332).
    """
    return eta_rad / (math.pi / 2.0 + 1.0)


def hansen_ground_factor_phi0(beta_rad: float) -> float:
    """Brinch Hansen sloping ground factor for phi = 0 (Table 5-7).

    .. math::
        g_c = \\frac{\\beta}{\\pi/2 + 1}

    Parameters
    ----------
    beta_rad : float
        Ground inclination angle (radians).

    Returns
    -------
    float
        Ground inclination factor gc for phi = 0 [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-7,
    printed p. 295 (pdf_page_index 332).
    """
    return beta_rad / (math.pi / 2.0 + 1.0)


# ---------------------------------------------------------------------------
# Brinch Hansen factors for phi > 0 (Table 5-8)
# ---------------------------------------------------------------------------


def hansen_shape_factors(
    B: float, L: float, phi_deg: float
) -> Tuple[float, float, float]:
    """Brinch Hansen shape factors for phi > 0, vertical load (Table 5-8).

    Parameters
    ----------
    B : float
        Foundation width (ft, m).  Use B/L = 1 for circular.
    L : float
        Foundation length (ft, m).
    phi_deg : float
        Effective friction angle (degrees).

    Returns
    -------
    sc : float
        Shape factor s_c [dimensionless].
    sq : float
        Shape factor s_q [dimensionless].
    s_gamma : float
        Shape factor s_gamma [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-8,
    printed p. 296 (pdf_page_index 333).
    """
    if L <= 0.0:
        raise ValueError("Foundation length L must be positive.")
    phi = math.radians(phi_deg)
    Nq = meyerhof_hansen_Nq(phi_deg)
    Nc = meyerhof_hansen_Nc(phi_deg)
    ratio = B / L
    sc = 1.0 + ratio * (Nq / Nc) * math.cos(phi) if Nc != 0.0 else 1.0
    sq = 1.0 + math.sin(phi) * ratio
    s_gamma = 1.0 - 0.4 * ratio
    return (sc, sq, s_gamma)


def hansen_depth_factors(
    Df: float, B: float, phi_deg: float
) -> Tuple[float, float, float]:
    """Brinch Hansen depth factors for phi > 0 (Table 5-8).

    Parameters
    ----------
    Df : float
        Foundation depth (ft, m).
    B : float
        Foundation width (ft, m).
    phi_deg : float
        Effective friction angle (degrees).

    Returns
    -------
    dc : float
        Depth factor d_c [dimensionless].
    dq : float
        Depth factor d_q [dimensionless].
    d_gamma : float
        Depth factor d_gamma [dimensionless], always 1.0.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-8,
    printed p. 296 (pdf_page_index 333).
    """
    k = _hansen_k(Df, B)
    phi = math.radians(phi_deg)
    sin_phi = math.sin(phi)
    tan_phi = math.tan(phi)
    Nq = meyerhof_hansen_Nq(phi_deg)
    Nc = meyerhof_hansen_Nc(phi_deg)
    dq = 1.0 + 2.0 * k * tan_phi * (1.0 - sin_phi) ** 2
    dc = 1.0 + k * (1.0 - sin_phi) ** 2 * (Nq / Nc) if Nc != 0.0 else 1.0
    d_gamma = 1.0
    return (dc, dq, d_gamma)


def hansen_inclination_factors(
    H: float,
    V: float,
    A_prime: float,
    Ca: float,
    phi_deg: float,
    eta_rad: float = 0.0,
) -> Tuple[float, float, float]:
    """Brinch Hansen load inclination factors for phi > 0 (Table 5-8).

    .. math::
        i_q = \\left(1 - \\frac{0.5 H}{V + A' C_a \\cot\\phi'}\\right)^5

    .. math::
        i_\\gamma = \\left(1 - \\frac{(0.7 - \\eta/450^\\circ) H}
                   {V + A' C_a \\cot\\phi'}\\right)^5

    .. math::
        i_c = \\frac{i_q N_q - 1}{N_q - 1}

    Parameters
    ----------
    H : float
        Horizontal component of load (lb, kN).
    V : float
        Vertical component of load (lb, kN).
    A_prime : float
        Equivalent bearing area (ft^2, m^2).
    Ca : float
        Base adhesion (psf, kPa).  Use 0 if no adhesion.
    phi_deg : float
        Effective friction angle (degrees).
    eta_rad : float, optional
        Base inclination angle (radians, default 0.0).

    Returns
    -------
    ic : float
        Inclination factor i_c [dimensionless].
    iq : float
        Inclination factor i_q [dimensionless].
    i_gamma : float
        Inclination factor i_gamma [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-8,
    printed p. 296 (pdf_page_index 333).
    """
    if phi_deg <= 0.0:
        raise ValueError("Use hansen_inclination_factor_phi0 for phi = 0.")
    phi = math.radians(phi_deg)
    cot_phi = 1.0 / math.tan(phi)
    denom = V + A_prime * Ca * cot_phi
    if denom <= 0.0:
        raise ValueError(
            "Denominator (V + A' Ca cot(phi)) must be positive."
        )
    iq = (1.0 - 0.5 * H / denom) ** 5
    # eta factor: (0.7 - eta/450deg) where 450deg = 2.5*pi radians
    eta_factor = 0.7 - eta_rad / (2.5 * math.pi)
    i_gamma = (1.0 - eta_factor * H / denom) ** 5
    Nq = meyerhof_hansen_Nq(phi_deg)
    ic = (iq * Nq - 1.0) / (Nq - 1.0) if Nq != 1.0 else 1.0
    return (ic, iq, i_gamma)


def hansen_base_factors(
    eta_rad: float, phi_deg: float
) -> Tuple[float, float]:
    """Brinch Hansen sloping base factors for phi > 0 (Table 5-8).

    .. math::
        b_q = e^{-2 \\eta \\tan\\phi'}

    .. math::
        b_\\gamma = e^{-2.7 \\eta \\tan\\phi'}

    Note: c factors for inclined base are not provided by Brinch Hansen
    for phi > 0.

    Parameters
    ----------
    eta_rad : float
        Base inclination angle (radians).
    phi_deg : float
        Effective friction angle (degrees).

    Returns
    -------
    bq : float
        Base inclination factor b_q [dimensionless].
    b_gamma : float
        Base inclination factor b_gamma [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-8,
    printed p. 296 (pdf_page_index 333).
    """
    tan_phi = math.tan(math.radians(phi_deg))
    bq = math.exp(-2.0 * eta_rad * tan_phi)
    b_gamma = math.exp(-2.7 * eta_rad * tan_phi)
    return (bq, b_gamma)


def hansen_ground_factors(beta_deg: float) -> Tuple[float, float]:
    """Brinch Hansen sloping ground factors for phi > 0 (Table 5-8).

    .. math::
        g_q = (1 - 0.5 \\tan\\beta)^5

    .. math::
        g_\\gamma = (1 - 0.5 \\tan\\beta)^5

    Note: c factors for sloping ground are not provided by Brinch Hansen
    for phi > 0.

    Parameters
    ----------
    beta_deg : float
        Ground inclination angle (degrees).

    Returns
    -------
    gq : float
        Ground inclination factor g_q [dimensionless].
    g_gamma : float
        Ground inclination factor g_gamma [dimensionless].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-8,
    printed p. 296 (pdf_page_index 333).
    """
    tan_beta = math.tan(math.radians(beta_deg))
    gq = (1.0 - 0.5 * tan_beta) ** 5
    g_gamma = (1.0 - 0.5 * tan_beta) ** 5
    return (gq, g_gamma)


# ===========================================================================
# LOCAL SHEAR CORRECTIONS (Table 5-4)
# ===========================================================================


def local_shear_terzaghi(
    c_prime: float, phi_prime_deg: float
) -> Tuple[float, float]:
    """Local shear reduced strength parameters -- Terzaghi (Table 5-4).

    For local or punching shear failure modes, the shear strength
    parameters are reduced.

    .. math::
        c^* = 0.67 \\, c'

    .. math::
        \\phi^* = \\tan^{-1}(0.67 \\tan\\phi')

    Parameters
    ----------
    c_prime : float
        Effective stress cohesion (psf, kPa).
    phi_prime_deg : float
        Effective stress friction angle (degrees).

    Returns
    -------
    c_star : float
        Reduced cohesion c* [consistent units (the unit of c_prime)].
    phi_star_deg : float
        Reduced friction angle phi* [degrees].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-4,
    printed p. 291 (pdf_page_index 328).
    """
    c_star = 0.67 * c_prime
    phi_star = math.degrees(
        math.atan(0.67 * math.tan(math.radians(phi_prime_deg)))
    )
    return (c_star, phi_star)


def local_shear_vesic(
    c_prime: float, phi_prime_deg: float, Dr: float
) -> Tuple[float, float]:
    """Local shear reduced strength parameters -- Vesic (Table 5-4).

    Variable reduction based on relative density (Dr).

    For Dr < 0.67: R = 0.67 + Dr - 0.75 * Dr^2
    For Dr >= 0.67: R = 1

    .. math::
        c^* = R \\cdot c'

    .. math::
        \\phi^* = \\tan^{-1}(R \\cdot \\tan\\phi')

    Parameters
    ----------
    c_prime : float
        Effective stress cohesion (psf, kPa).
    phi_prime_deg : float
        Effective stress friction angle (degrees).
    Dr : float
        Relative density (decimal, 0 to 1).

    Returns
    -------
    c_star : float
        Reduced cohesion c* [consistent units (the unit of c_prime)].
    phi_star_deg : float
        Reduced friction angle phi* [degrees].

    Raises
    ------
    ValueError
        If *Dr* is outside [0, 1].

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Table 5-4,
    printed p. 291 (pdf_page_index 328).
    """
    if Dr < 0.0 or Dr > 1.0:
        raise ValueError("Relative density Dr must be between 0 and 1.")
    if Dr < 0.67:
        R = 0.67 + Dr - 0.75 * Dr ** 2
    else:
        R = 1.0
    c_star = R * c_prime
    phi_star = math.degrees(
        math.atan(R * math.tan(math.radians(phi_prime_deg)))
    )
    return (c_star, phi_star)


# ===========================================================================
# FIGURE 5-18: Modified Nc for Layered Clay (Brown & Meyerhof 1969)
# ===========================================================================

# Figure 5-18 (PDF p. 348, printed p. 310) plots the modified bearing
# capacity factor N_c,m against su2/su1 (0 to 2.0), one curve per H/B for a
# strip footing (a) and per H/2R for a circular footing (b).
#
# Top layer stiff, bottom layer soft (su2/su1 < 1): the figure prints the
# equation of its straight lines in a box:
#   (a) strip footings:     N_c,m,s = 1.5 H/B + 5.14 su2/su1 <= 5.14
#   (b) circular footings:  N_c,m,c = 1.5 H/R + 6.05 su2/su1 <= 6.05
# N_cm on this side is the equation's value.  The drawn lines follow the
# equation, except one curve per panel: H/B = 0.5 in (a) follows its line
# to about su2/su1 = 0.70 and H/2R = 0.25 in (b) to about 0.63; each then
# bends below its line to meet the uniform value at su2/su1 = 1.0.  Those
# two curves were read off a 300 dpi render of PDF p. 348 against the
# figure's own gridlines, to about +/- 0.05 (the value at 1.0 is the
# labelled line where all curves meet).  On the same render the straight
# lines nearby read 0.02 to 0.05 below their equations, so part of each
# difference is drafting.  They give "N_cm_drawn_curve" at that one H/B
# only; no values for other H/B are built from them.
#
# Top layer soft, bottom layer stiff (su2/su1 > 1): curves are drawn for
# H/B (H/2R) = 0, 0.1, 0.2 and 0.3, and the value is 5.14 for H/B >= 0.7
# (6.05 for H/2R >= 0.4).  The figure is an image in the PDF, so the
# values below were read off its pixels against its own gridlines, to
# about +/- 0.05.  Where a curve is hidden by its own label the values lie
# on a straight line between the readings on either side of the label.
# The H/B = 0 and H/2R = 0 curves leave the top of the chart (N = 10) at
# su2/su1 of about 1.97 and 1.66; their last points are the last readings
# on the chart.  Each curve: [(su2/su1, N_c,m), ...].

_FIG_5_18_RATIO_MAX = 2.0

_FIG_5_18A_SOFT_OVER_STIFF = {
    0.0: [(1.0, 5.14), (1.1, 5.58), (1.2, 6.07), (1.3, 6.58), (1.4, 7.08),
          (1.5, 7.59), (1.6, 8.10), (1.7, 8.61), (1.8, 9.11), (1.9, 9.64),
          (1.95, 9.89)],
    0.1: [(1.0, 5.14), (1.1, 5.46), (1.2, 5.79), (1.3, 6.07), (1.4, 6.32),
          (1.5, 6.49), (1.6, 6.67), (1.7, 6.80), (1.8, 6.94), (1.9, 7.07),
          (2.0, 7.15)],
    0.2: [(1.0, 5.14), (1.1, 5.39), (1.2, 5.55), (1.3, 5.67), (1.4, 5.78),
          (1.5, 5.91), (1.6, 5.97), (1.7, 6.03), (1.8, 6.10), (1.9, 6.14),
          (2.0, 6.18)],
    0.3: [(1.0, 5.14), (1.1, 5.24), (1.2, 5.33), (1.3, 5.42), (1.4, 5.51),
          (1.5, 5.56), (1.6, 5.60), (1.7, 5.63), (1.8, 5.66), (1.9, 5.69),
          (2.0, 5.72)],
}

_FIG_5_18B_SOFT_OVER_STIFF = {
    0.0: [(1.0, 6.05), (1.1, 6.62), (1.2, 7.22), (1.3, 7.81), (1.4, 8.41),
          (1.5, 9.00), (1.6, 9.64), (1.65, 9.94)],
    0.1: [(1.0, 6.05), (1.1, 6.39), (1.2, 6.71), (1.3, 6.96), (1.4, 7.15),
          (1.5, 7.29), (1.6, 7.39), (1.7, 7.50), (1.8, 7.57), (1.9, 7.62),
          (2.0, 7.66)],
    0.2: [(1.0, 6.05), (1.1, 6.33), (1.2, 6.45), (1.3, 6.54), (1.4, 6.60),
          (1.5, 6.67), (1.6, 6.70), (1.7, 6.73), (1.8, 6.73), (1.9, 6.74),
          (2.0, 6.75)],
    0.3: [(1.0, 6.05), (1.1, 6.13), (1.2, 6.18), (1.3, 6.22), (1.4, 6.24),
          (1.5, 6.25), (1.6, 6.26), (1.7, 6.27), (1.8, 6.27), (1.9, 6.28),
          (2.0, 6.27)],
}

# Top layer stiff: the one drawn curve per panel that leaves the equation's
# line, [(su2/su1, N_c,m), ...], used from su2/su1 = 0.68 to 1.0.
_FIG_5_18A_STIFF_OVER_SOFT_DRAWN = [
    (0.68, 4.22), (0.70, 4.32), (0.72, 4.38), (0.75, 4.48), (0.80, 4.62),
    (0.85, 4.74), (0.90, 4.87), (0.95, 4.98), (1.0, 5.14)]

_FIG_5_18B_STIFF_OVER_SOFT_DRAWN = [
    (0.68, 4.76), (0.70, 4.85), (0.72, 4.95), (0.75, 5.09), (0.80, 5.30),
    (0.85, 5.50), (0.90, 5.68), (0.95, 5.85), (1.0, 6.05)]

_FIG_5_18_DRAWN_FROM = 0.68     # N_cm_drawn_curve from this su2/su1 to 1.0
_FIG_5_18_PRINT_NOTE_ABOVE = 0.65   # print_note for 0.65 < su2/su1 < 1

_FIG_5_18_CHARTS = {
    "a": {
        "name": "Figure 5-18(a), strip footings",
        "symbol": "N_c,m,s",
        "uniform": 5.14,
        # N = intercept_per_depth * (H/B) + uniform * su2/su1
        "intercept_per_depth": 1.5,
        "equation": "N_c,m,s = 1.5 H/B + 5.14 su2/su1 <= 5.14",
        "depth": "H/B",
        "curves": _FIG_5_18A_SOFT_OVER_STIFF,
        "drawn_depth": 0.5,
        "drawn_curve": _FIG_5_18A_STIFF_OVER_SOFT_DRAWN,
        "print_note_depth_below": 1.0,
        "print_note": (
            "Figure 5-18(a) draws one curve in this region that is not the "
            "printed equation's straight line: H/B = 0.5 follows the line "
            "to about su2/su1 = 0.70, then runs below it to meet 5.14 at "
            "su2/su1 = 1.0, by up to about 7.5 percent (read off the "
            "figure, +/- 0.05: at su2/su1 = 0.80 the equation gives 4.86 "
            "and the curve about 4.62; at 0.85, 5.12 and about 4.74).  "
            "N_cm is the equation's value; N_cm_drawn_curve gives the "
            "curve's value at H/B = 0.5 only.  The manual's text (printed "
            "p. 309) says it is prudent to reduce the values by 10 percent "
            "when 0.7 < su2/su1 < 1; on the drawn curve the reduced value "
            "is at or below the curve."),
        "no_effect_from": 0.7,
        "table_note": (" Table 5-11 on the same page gives ranges of "
                       "N_c,m,s for a strip at H/B = 0.125, 0.50, 0.75 and "
                       "1.5 and su2/su1 up to 5.0."),
    },
    "b": {
        "name": "Figure 5-18(b), circular footings",
        "symbol": "N_c,m,c",
        "uniform": 6.05,
        # the printed equation is in H/R; the curves are labelled H/2R,
        # and H/R = 2 (H/2R), so the intercept is 3.0 per unit of H/2R
        "intercept_per_depth": 3.0,
        "equation": "N_c,m,c = 1.5 H/R + 6.05 su2/su1 <= 6.05",
        "depth": "H/2R",
        "curves": _FIG_5_18B_SOFT_OVER_STIFF,
        "drawn_depth": 0.25,
        "drawn_curve": _FIG_5_18B_STIFF_OVER_SOFT_DRAWN,
        "print_note_depth_below": 0.5,
        "print_note": (
            "Figure 5-18(b) draws one curve in this region that is not the "
            "printed equation's straight line: H/2R = 0.25 follows the "
            "line to about su2/su1 = 0.63, then runs below it to meet 6.05 "
            "at su2/su1 = 1.0, by up to about 7.5 percent (read off the "
            "figure, +/- 0.05: at su2/su1 = 0.80 the equation gives 5.59 "
            "and the curve about 5.30; at 0.85, 5.89 and about 5.50).  "
            "N_cm is the equation's value; N_cm_drawn_curve gives the "
            "curve's value at H/2R = 0.25 only.  The manual's text "
            "(printed p. 309) says it is prudent to reduce the values by "
            "10 percent when 0.7 < su2/su1 < 1; on the drawn curve the "
            "reduced value is at or below the curve."),
        "no_effect_from": 0.4,
        "table_note": "",
    },
}

_FIG_5_18_REDUCTION_NOTE = (
    "When 0.7 < su2/su1 < 1, it is prudent to reduce the values of "
    "N_c,m,s and N_c,m,c by 10 percent (UFC 3-220-20, printed p. 309). "
    "N_cm is the value by the figure's equation or curves; "
    "N_cm_reduced_10_percent is 0.9 of it."
)


def _fig_5_18_on_curve(points, ratio, chart, depth_value):
    """Value on one drawn soft-over-stiff curve, by straight lines between
    its tabulated points; refused beyond the curve's last point on the
    chart."""
    last_ratio = points[-1][0]
    if ratio > last_ratio:
        raise ValueError(
            f"{chart['name']}: the {chart['depth']} = {depth_value:g} curve "
            f"leaves the top of the chart (N = 10) just past su2/su1 = "
            f"{last_ratio:g}; it cannot be read at su2/su1 = {ratio:g}."
        )
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= ratio <= x1:
            return y0 + (y1 - y0) * (ratio - x0) / (x1 - x0)
    return points[0][1]


def _fig_5_18_lookup(which, ratio, depth_ratio):
    chart = _FIG_5_18_CHARTS[which]
    depth = chart["depth"]
    uniform = chart["uniform"]
    if ratio <= 0.0:
        raise ValueError("cu2_over_cu1 must be positive.")
    if depth_ratio < 0.0:
        raise ValueError("H_over_B must be non-negative.")
    if ratio > _FIG_5_18_RATIO_MAX:
        raise ValueError(
            f"{chart['name']} is drawn for su2/su1 from 0 to 2.0; "
            f"su2/su1 = {ratio:g} is off the chart." + chart["table_note"]
        )
    reduced = None
    note = None
    drawn_value = None
    print_note = None
    on_drawn_curve = abs(depth_ratio - chart["drawn_depth"]) <= 1e-9
    if depth_ratio > 3.0:
        value = uniform
        layering = ("the second layer is more than three foundation widths "
                    "below the bearing elevation")
        basis = ("text, printed p. 309: for H/B > 3 the bearing capacity is "
                 f"not affected by the deeper layer, so {chart['symbol']} = "
                 f"{uniform:g}")
    elif ratio < 1.0:
        value = min(uniform,
                    chart["intercept_per_depth"] * depth_ratio
                    + uniform * ratio)
        layering = "top layer stiff, bottom layer soft"
        basis = (f"N_cm: by the equation printed in {chart['name']}: "
                 f"{chart['equation']}")
        if ratio > 0.7:
            reduced = 0.9 * value
            note = _FIG_5_18_REDUCTION_NOTE
        if (ratio > _FIG_5_18_PRINT_NOTE_ABOVE
                and 0.0 < depth_ratio < chart["print_note_depth_below"]):
            print_note = chart["print_note"]
        if on_drawn_curve and ratio >= _FIG_5_18_DRAWN_FROM:
            drawn_value = _fig_5_18_on_curve(chart["drawn_curve"], ratio,
                                             chart, chart["drawn_depth"])
    elif ratio == 1.0:
        value = uniform
        layering = "uniform (su2/su1 = 1)"
        basis = f"{chart['name']}: all curves meet at {uniform:g}"
        if on_drawn_curve:
            drawn_value = uniform
    else:
        layering = "top layer soft, bottom layer stiff"
        curves = chart["curves"]
        drawn = sorted(curves)
        no_effect = chart["no_effect_from"]
        if depth_ratio >= no_effect:
            value = uniform
            basis = (f"{chart['name']}: {uniform:g} for {depth} >= "
                     f"{no_effect:g}")
        elif depth_ratio > drawn[-1]:
            top = _fig_5_18_on_curve(curves[drawn[-1]], ratio, chart,
                                     drawn[-1])
            raise ValueError(
                f"{chart['name']} draws its top-layer-soft curves for "
                f"{depth} = 0, 0.1, 0.2 and 0.3 and gives {uniform:g} for "
                f"{depth} >= {no_effect:g}; it draws nothing between 0.3 "
                f"and {no_effect:g}, so {depth} = {depth_ratio:g} cannot be "
                f"read.  At su2/su1 = {ratio:g} the {depth} = 0.3 curve "
                f"reads {top:.2f}, so the value lies between {uniform:g} "
                f"and {top:.2f}." + chart["table_note"]
            )
        else:
            lower = max(d for d in drawn if d <= depth_ratio)
            upper = min(d for d in drawn if d >= depth_ratio)
            v_lower = _fig_5_18_on_curve(curves[lower], ratio, chart, lower)
            if upper == lower:
                value = v_lower
            else:
                v_upper = _fig_5_18_on_curve(curves[upper], ratio, chart,
                                             upper)
                value = v_lower + (v_upper - v_lower) * (
                    (depth_ratio - lower) / (upper - lower))
            basis = (f"curves of {chart['name']} for {depth} = 0, 0.1, 0.2 "
                     "and 0.3, read off the chart (about +/- 0.05) and "
                     "interpolated linearly")
    return {
        "N_cm": value,
        "N_cm_reduced_10_percent": reduced,
        "N_cm_drawn_curve": drawn_value,
        "layering": layering,
        "basis": basis,
        "note": note,
        "print_note": print_note,
    }


@_u.labelled(
    {"N_cm": "dimensionless", "N_cm_drawn_curve": "dimensionless",
     "N_cm_reduced_10_percent": "dimensionless"},
    printed_page="310", pdf_page_index=347)
def figure_5_18a_Ncm_strip(cu2_over_cu1: float, H_over_B: float) -> dict:
    """Modified bearing capacity factor N_c,m,s (dimensionless) for a strip
    footing on two layers of clay, Figure 5-18(a) of UFC 3-220-20 (after
    Brown and Meyerhof 1969), returned as a dict whose "N_cm" is the
    factor by the figure's printed equation or read off its curves;
    q_ult = su1 N_c,m with su1 the top layer's strength.  Where the top
    layer is stiff, 0.65 < su2/su1 < 1 and 0 < H/B < 1.0, "print_note"
    says the figure's one drawn curve there (H/B = 0.5) runs below the
    equation by up to about 7.5 percent, and at H/B = 0.5 with
    0.68 <= su2/su1 <= 1.0 "N_cm_drawn_curve" gives that curve's value.

    Top layer stiff, bottom layer soft (su2/su1 < 1): the equation printed
    in the figure, N_c,m,s = 1.5 H/B + 5.14 su2/su1 <= 5.14.  Top layer
    soft, bottom layer stiff (su2/su1 > 1): the figure's curves for
    H/B = 0, 0.1, 0.2 and 0.3, read off the chart to about +/- 0.05, and
    5.14 for H/B >= 0.7; the figure draws nothing between 0.3 and 0.7 and
    the function refuses there.  The chart ends at su2/su1 = 2.0.  The
    text (printed p. 309) adds: "When 0.7 < su2/su1 < 1, it is prudent to
    reduce the values of N_c,m,s and N_c,m,c by 10 percent", and for
    H/B > 3 the deeper layer has no effect (5.14).  The 10 percent
    reduction is NOT applied to "N_cm"; where it applies the reduced value
    is given beside it.  Inclination factors should not be combined with
    these factors.

    Parameters
    ----------
    cu2_over_cu1 : float
        su2/su1: undrained shear strength of the lower layer over that of
        the upper layer (dimensionless, > 0, at most 2.0).
    H_over_B : float
        H/B: thickness of the upper layer below the footing base over the
        footing width (dimensionless, >= 0).

    Returns
    -------
    dict
        ``N_cm``: N_c,m,s (dimensionless); top layer stiff: by the
        equation printed in the figure; top layer soft: read off the
        figure's curves.  ``N_cm_reduced_10_percent``: 0.9 N_cm when
        0.7 < su2/su1 < 1, otherwise None.  ``N_cm_drawn_curve``: the
        value read off the figure's drawn H/B = 0.5 curve (+/- 0.05) when
        H/B = 0.5 and 0.68 <= su2/su1 <= 1.0, otherwise None.
        ``layering``: which side of the chart was read.  ``basis``: the
        printed equation, the curves or the text used.  ``note``: the
        manual's sentence on the 10 percent reduction when it applies,
        otherwise None.  ``print_note``: where the drawn curve departs
        from the printed equation (top layer stiff, 0.65 < su2/su1 < 1,
        0 < H/B < 1.0), otherwise None.

    Raises
    ------
    ValueError
        If *cu2_over_cu1* is not positive or above 2.0, *H_over_B* is
        negative, the top layer is soft and H/B is between 0.3 and 0.7,
        or the H/B = 0 curve is needed past where it leaves the chart.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Figure 5-18(a) (Modified
    Bearing Capacity Factors for Two-Layer Clay Stratigraphy),
    printed p. 310 (pdf_page_index 347); text on
    printed p. 309 (pdf_page_index 346); worked example in Figure 5-19,
    printed p. 311 (pdf_page_index 348).
    """
    return _fig_5_18_lookup("a", cu2_over_cu1, H_over_B)


@_u.labelled(
    {"N_cm": "dimensionless", "N_cm_reduced_10_percent": "dimensionless",
     "N_cm_drawn_curve": "dimensionless"},
    printed_page="310", pdf_page_index=347)
def figure_5_18b_Ncm_circular(cu2_over_cu1: float, H_over_B: float) -> dict:
    """Modified bearing capacity factor N_c,m,c (dimensionless, shape
    factor included) for a circular footing on two layers of clay, Figure
    5-18(b) of UFC 3-220-20 (after Brown and Meyerhof 1969), returned as a
    dict whose "N_cm" is the factor by the figure's printed equation or
    read off its curves; q_ult = su1 N_c,m.  Where the top layer is stiff,
    0.65 < su2/su1 < 1 and 0 < H/2R < 0.5, "print_note" says the figure's
    one drawn curve there (H/2R = 0.25) runs below the equation by up to
    about 7.5 percent, and at H/2R = 0.25 with 0.68 <= su2/su1 <= 1.0
    "N_cm_drawn_curve" gives that curve's value.

    Top layer stiff, bottom layer soft (su2/su1 < 1): the equation printed
    in the figure, N_c,m,c = 1.5 H/R + 6.05 su2/su1 <= 6.05, with R the
    footing radius (the curves are labelled H/2R, and H/R = 2 H/2R).  Top
    layer soft, bottom layer stiff (su2/su1 > 1): the figure's curves for
    H/2R = 0, 0.1, 0.2 and 0.3, read off the chart to about +/- 0.05, and
    6.05 for H/2R >= 0.4; the figure draws nothing between 0.3 and 0.4
    and the function refuses there.  The chart ends at su2/su1 = 2.0.
    The text (printed p. 309) adds: "When 0.7 < su2/su1 < 1, it is
    prudent to reduce the values of N_c,m,s and N_c,m,c by 10 percent".
    The reduction is NOT applied to "N_cm"; where it applies the reduced
    value is given beside it.  For a rectangular footing the manual's
    example uses 2R = B (Figure 5-19) with Equation 5-25.

    Parameters
    ----------
    cu2_over_cu1 : float
        su2/su1: undrained shear strength of the lower layer over that of
        the upper layer (dimensionless, > 0, at most 2.0).
    H_over_B : float
        H/2R: thickness of the upper layer below the footing base over the
        footing DIAMETER (dimensionless, >= 0).  Not H/R.

    Returns
    -------
    dict
        ``N_cm``: N_c,m,c (dimensionless); top layer stiff: by the
        equation printed in the figure; top layer soft: read off the
        figure's curves.  ``N_cm_reduced_10_percent``: 0.9 N_cm when
        0.7 < su2/su1 < 1, otherwise None.  ``N_cm_drawn_curve``: the
        value read off the figure's drawn H/2R = 0.25 curve (+/- 0.05)
        when H/2R = 0.25 and 0.68 <= su2/su1 <= 1.0, otherwise None.
        ``print_note``: as for ``figure_5_18a_Ncm_strip``, for
        0 < H/2R < 0.5.  ``layering``, ``basis``, ``note``: as for
        ``figure_5_18a_Ncm_strip``.

    Raises
    ------
    ValueError
        If *cu2_over_cu1* is not positive or above 2.0, *H_over_B* is
        negative, the top layer is soft and H/2R is between 0.3 and 0.4,
        or the H/2R = 0 curve is needed past where it leaves the chart.

    References
    ----------
    UFC 3-220-20, Foundations, 16 Jan 2025, Chapter 5, Figure 5-18(b),
    printed p. 310 (pdf_page_index 347); text on
    printed p. 309 (pdf_page_index 346); worked example in Figure 5-19,
    printed p. 311 (pdf_page_index 348).
    """
    return _fig_5_18_lookup("b", cu2_over_cu1, H_over_B)


def _plot_figure_5_18(which, stiff_depths, cu2_over_cu1, H_over_B, ax, show):
    from geotech_references._plotting import get_pyplot, setup_engineering_plot
    plt = get_pyplot()
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    chart = _FIG_5_18_CHARTS[which]
    depth = chart["depth"]
    uniform = chart["uniform"]

    # top layer stiff: the printed straight lines, su2/su1 from 0 to 1
    for d in stiff_depths:
        intercept = chart["intercept_per_depth"] * d
        if intercept >= uniform:
            xs, ys = [0.0, 1.0], [uniform, uniform]
        else:
            # the line meets the cap where intercept + uniform x = uniform
            x_cap = (uniform - intercept) / uniform
            xs, ys = [0.0, x_cap, 1.0], [intercept, uniform, uniform]
        ax.plot(xs, ys, '-', color='#1f77b4', linewidth=1.2)
        ax.annotate(f'{depth}={d:g}', (xs[0], ys[0]), fontsize=7,
                    xytext=(3, 2), textcoords='offset points')
    # top layer soft: the drawn curves
    for d, points in sorted(chart["curves"].items()):
        ax.plot([p[0] for p in points], [p[1] for p in points], '-',
                color='#ff7f0e', linewidth=1.2)
        ax.annotate(f'{depth}={d:g}', points[-1], fontsize=7,
                    xytext=(-34, 3), textcoords='offset points')
    ax.plot([1.0, _FIG_5_18_RATIO_MAX], [uniform, uniform], '-',
            color='black', linewidth=2.0,
            label=f'{uniform:g} ({depth} ≥ {chart["no_effect_from"]:g}, '
                  'top layer soft)')

    # Query point
    if cu2_over_cu1 is not None and H_over_B is not None:
        ncm_q = _fig_5_18_lookup(which, cu2_over_cu1, H_over_B)["N_cm"]
        ax.plot(cu2_over_cu1, ncm_q, 's', color='red', markersize=10,
                zorder=5,
                label=f'su₂/su₁={cu2_over_cu1:.2f}, {depth}={H_over_B:.2f}'
                      f' → Nc,m={ncm_q:.2f}')
        ax.axhline(ncm_q, color='red', linestyle=':', alpha=0.4)
        ax.axvline(cu2_over_cu1, color='red', linestyle=':', alpha=0.4)

    ax.set_xlim(0.0, _FIG_5_18_RATIO_MAX)
    ax.set_ylim(0.0, 10.0)
    ax.legend(fontsize=7, loc='lower right')
    setup_engineering_plot(
        ax,
        'Figure 5-18(%s): Modified Nc — %s Footing (Two-Layer Clay)'
        % (which, 'Strip' if which == 'a' else 'Circular'),
        'Lower Layer Shear Strength / Upper Layer Shear Strength '
        '(su₂ / su₁)',
        'Modified Bearing Capacity Factor, Nc,m')
    if show:
        plt.tight_layout()
        plt.show()
    return ax


def plot_figure_5_18a(cu2_over_cu1=None, H_over_B=None, ax=None,
                       show=True, **kwargs):
    """Draw UFC 3-220-20 Figure 5-18(a): N_c,m,s for a strip footing on
    two-layer clay against su2/su1 (0 to 2.0), one line per H/B, from the
    printed equation (top layer stiff) and the curves read off the figure
    (top layer soft).

    Parameters
    ----------
    cu2_over_cu1 : float, optional
        su2/su1 of a point to mark.
    H_over_B : float, optional
        H/B of the point to mark.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on.
    show : bool, optional
        If True, calls plt.show().

    Returns
    -------
    matplotlib.axes.Axes
    """
    return _plot_figure_5_18("a", (0.0, 0.5, 1.0, 1.5, 2.0, 2.5),
                             cu2_over_cu1, H_over_B, ax, show)


def plot_figure_5_18b(cu2_over_cu1=None, H_over_B=None, ax=None,
                       show=True, **kwargs):
    """Draw UFC 3-220-20 Figure 5-18(b): N_c,m,c for a circular footing on
    two-layer clay against su2/su1 (0 to 2.0), one line per H/2R, from the
    printed equation (top layer stiff) and the curves read off the figure
    (top layer soft).

    Parameters
    ----------
    cu2_over_cu1 : float, optional
        su2/su1 of a point to mark.
    H_over_B : float, optional
        H/2R (upper layer thickness over footing diameter) of the point
        to mark.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on.
    show : bool, optional
        If True, calls plt.show().

    Returns
    -------
    matplotlib.axes.Axes
    """
    return _plot_figure_5_18("b", (0.0, 0.25, 0.5, 1.0, 1.5),
                             cu2_over_cu1, H_over_B, ax, show)
