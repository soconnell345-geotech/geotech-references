"""
UFC 3-220-20, Chapter 6: Deep Foundations

Equations 6-1 through 6-80 covering scour critical velocity, pile impedance,
static axial capacity (Beta and Alpha methods), base resistance (semi-empirical
and Vesic), SPT/CPT-based methods, micropiles, rock sockets, group capacity,
uplift, settlement, lateral capacity (Broms method and Characteristic Load
Method), structural capacity, buckling, and dynamic methods.

Reference:
    UFC 3-220-20, Foundations and Earth Structures, 16 January 2025
"""

import math
from typing import List, Tuple

from geotech_references._interpolation import _linterp


# ===========================================================================
# SCOUR
# ===========================================================================

def critical_scour_velocity(D50: float) -> float:
    """Critical velocity v_c in m/s for the onset of scour in
    coarse-grained soil from the median particle size D50 in mm, Equation
    6-1 of UFC 3-220-20: v_c = 0.35 D50^0.45.  The manual says the
    equation "should not be extrapolated below sand-sized particles"
    (0.075 mm in its glossary), so a D50 below 0.075 mm is refused.

    The constant carries the units m / (s mm^0.45).  The critical
    velocity is not correlated to particle size for fine-grained soils.

    .. math::
        v_c = 0.35 \\cdot D_{50}^{0.45}

    Parameters
    ----------
    D50 : float
        Median particle size (mm), at least 0.075 mm.

    Returns
    -------
    float
        Critical velocity (m/s).

    Raises
    ------
    ValueError
        If *D50* is not positive or is below 0.075 mm, the lower size of
        sand-sized particles.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-1, PDF p. 409
    (printed p. 371); Glossary, "Sand-sized – Particle size between
    0.075 mm and 4.75 mm", PDF p. 719 (printed p. 681).
    """
    if D50 <= 0.0:
        raise ValueError("D50 must be positive.")
    if D50 < 0.075:
        raise ValueError(
            f"D50 = {D50:g} mm: Equation 6-1 \"should not be extrapolated "
            "below sand-sized particles\" (0.075 mm); the critical velocity "
            "is not correlated to particle size for fine-grained soils."
        )
    return 0.35 * D50 ** 0.45


# ===========================================================================
# PILE IMPEDANCE
# ===========================================================================

def pile_impedance(E: float, A: float, c: float) -> float:
    """Pile impedance (Equation 6-2).

    A key parameter to assess drivability.  Piles with higher impedance
    transmit more force during driving.

    .. math::
        I = \\frac{E \\cdot A}{c}

    Parameters
    ----------
    E : float
        Elastic modulus of the pile (force/length^2).
    A : float
        Cross-sectional area of the pile (length^2).
    c : float
        Material wave speed (length/time).

    Returns
    -------
    float
        Pile impedance (force * time / length).

    Raises
    ------
    ValueError
        If any input is not positive.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-2, p. 426.
    """
    if E <= 0.0:
        raise ValueError("E must be positive.")
    if A <= 0.0:
        raise ValueError("A must be positive.")
    if c <= 0.0:
        raise ValueError("c must be positive.")
    return E * A / c


# ===========================================================================
# STATIC AXIAL CAPACITY – GENERAL
# ===========================================================================

def nominal_axial_resistance(R_s: float, R_b: float) -> float:
    """Nominal axial resistance of a deep foundation element (Equation 6-3).

    .. math::
        R = R_s + R_b

    Parameters
    ----------
    R_s : float
        Nominal shaft resistance (force).
    R_b : float
        Nominal base resistance (force).

    Returns
    -------
    float
        Total nominal resistance (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-3, p. 444.
    """
    return R_s + R_b


def nominal_shaft_resistance(
    segments: List[Tuple[float, float]],
) -> float:
    """Nominal shaft resistance from discretized segments (Equation 6-4).

    .. math::
        R_s = \\sum f_{s,i} \\cdot A_{s,i}

    Parameters
    ----------
    segments : list of (float, float)
        Each element is ``(f_s_i, A_s_i)`` where *f_s_i* is the unit shaft
        resistance (stress) and *A_s_i* is the surface area (length^2) for
        segment *i*.

    Returns
    -------
    float
        Nominal shaft resistance (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-4, p. 444.
    """
    return sum(f_s * A_s for f_s, A_s in segments)


def nominal_base_resistance(q_b: float, A_b: float) -> float:
    """Nominal base resistance (Equation 6-5).

    .. math::
        R_b = q_b \\cdot A_b

    Parameters
    ----------
    q_b : float
        Unit base resistance (stress).
    A_b : float
        Area of the base (length^2).

    Returns
    -------
    float
        Nominal base resistance (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-5, p. 444.
    """
    return q_b * A_b


# ===========================================================================
# SHAFT RESISTANCE – BETA METHOD (Effective Stress / Drained)
# ===========================================================================

def beta_coefficient(K: float, delta_deg: float) -> float:
    """Beta coefficient for effective stress shaft resistance (Equation 6-6).

    .. math::
        \\beta = K \\cdot \\tan(\\delta)

    Parameters
    ----------
    K : float
        Earth pressure coefficient for the column-soil interface
        (dimensionless).
    delta_deg : float
        Effective interface friction angle (degrees).

    Returns
    -------
    float
        Beta coefficient (dimensionless).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-6, p. 449.
    """
    if K < 0.0:
        raise ValueError("K must be non-negative.")
    return K * math.tan(math.radians(delta_deg))


def beta_method_unit_shaft_resistance(
    beta: float, sigma_z_eff: float
) -> float:
    """Unit shaft resistance by Beta method (Equation 6-7).

    .. math::
        f_s = \\beta \\cdot \\sigma'_z

    Parameters
    ----------
    beta : float
        Beta coefficient (dimensionless).
    sigma_z_eff : float
        Average effective vertical stress over the shaft segment (stress).

    Returns
    -------
    float
        Unit shaft resistance (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-7, p. 450.
    """
    return beta * sigma_z_eff


# ===========================================================================
# SHAFT RESISTANCE – ALPHA METHOD (Total Stress / Undrained)
# ===========================================================================

def alpha_method_unit_shaft_resistance(alpha: float, s_u: float) -> float:
    """Unit shaft resistance by Alpha method (Equation 6-8).

    .. math::
        f_s = \\alpha \\cdot s_u

    Parameters
    ----------
    alpha : float
        Adhesion factor (dimensionless, 0 to 1).
    s_u : float
        Undrained shear strength (stress).

    Returns
    -------
    float
        Unit shaft resistance (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-8, p. 453.
    """
    return alpha * s_u


def alpha_tomlinson_transition(s_u: float, P_a: float) -> float:
    """Alpha for transition zone – driven pile through soft clay into stiff clay
    (Equation 6-9).

    Applies to upper 10b of the stiff clay layer when overlain by soft clay.

    .. math::
        \\alpha = 0.28 \\left(\\frac{s_u}{P_a}\\right)^{-0.44}

    Parameters
    ----------
    s_u : float
        Undrained shear strength of the stiff clay (stress).
    P_a : float
        Atmospheric pressure in same units as *s_u*.

    Returns
    -------
    float
        Adhesion factor alpha (dimensionless).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-9, printed p. 416 (PDF p. 454).
    """
    if s_u <= 0.0:
        raise ValueError("s_u must be positive.")
    if P_a <= 0.0:
        raise ValueError("P_a must be positive.")
    return 0.28 * (s_u / P_a) ** (-0.44)


def alpha_chen_drilled_shaft(s_u_ICU: float, P_a: float) -> float:
    """Adhesion factor alpha (dimensionless) for drilled shafts after Chen
    et al. (2011), Equation 6-10 of UFC 3-220-20:
    alpha = 0.3 + 0.17 Pa / su,ICU, limited to 1 as printed.

    A value of exactly 1 is the printed limit, not the equation.

    .. math::
        \\alpha = 0.3 + \\frac{0.17}{s_{u,ICU}/P_a} \\leq 1

    Parameters
    ----------
    s_u_ICU : float
        Undrained strength from ICU triaxial test (stress).
    P_a : float
        Atmospheric pressure (same units).

    Returns
    -------
    float
        Adhesion factor alpha (dimensionless), capped at 1.0.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-10, PDF p. 456
    (printed p. 418).
    """
    if s_u_ICU <= 0.0:
        raise ValueError("s_u_ICU must be positive.")
    if P_a <= 0.0:
        raise ValueError("P_a must be positive.")
    return min(0.3 + 0.17 / (s_u_ICU / P_a), 1.0)


def su_ICU_from_UC(s_u_UC: float, OCR: float) -> float:
    """Convert UC undrained strength to ICU equivalent (Equation 6-11).

    .. math::
        s_{u,ICU} \\approx 1.74 \\cdot s_{u,UC} \\cdot OCR^{-0.25}

    Parameters
    ----------
    s_u_UC : float
        Undrained strength from unconfined compression test (stress).
    OCR : float
        Overconsolidation ratio (dimensionless).

    Returns
    -------
    float
        Equivalent ICU undrained strength (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-11, p. 456.
    """
    if OCR <= 0.0:
        raise ValueError("OCR must be positive.")
    return 1.74 * s_u_UC * OCR ** (-0.25)


def su_ICU_from_UU(s_u_UU: float, OCR: float) -> float:
    """Convert UU undrained strength to ICU equivalent (Equation 6-12).

    .. math::
        s_{u,ICU} \\approx 1.68 \\cdot s_{u,UU} \\cdot OCR^{-0.25}

    Parameters
    ----------
    s_u_UU : float
        Undrained strength from UU triaxial test (stress).
    OCR : float
        Overconsolidation ratio (dimensionless).

    Returns
    -------
    float
        Equivalent ICU undrained strength (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-12, p. 456.
    """
    if OCR <= 0.0:
        raise ValueError("OCR must be positive.")
    return 1.68 * s_u_UU * OCR ** (-0.25)


def su_ICU_from_DSS(s_u_DSS: float) -> float:
    """Convert DSS undrained strength to ICU equivalent (Equation 6-13).

    .. math::
        s_{u,ICU} \\approx 1.43 \\cdot s_{u,DSS}

    Parameters
    ----------
    s_u_DSS : float
        Undrained strength from direct simple shear test (stress).

    Returns
    -------
    float
        Equivalent ICU undrained strength (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-13, p. 456.
    """
    return 1.43 * s_u_DSS


def alpha_salgado_drilled_shaft(s_u: float, P_a: float) -> float:
    """Adhesion factor alpha (dimensionless) for drilled shafts and CFAs
    after Salgado (2008), Equation 6-14 of UFC 3-220-20:
    alpha = 0.4 [1 - 0.12 ln(su / Pa)].  The manual gives it for soils
    with a clay fraction of at least 50 % and an OCR between 3 and 5 (for
    lower OCR it is expected to be conservative); the function cannot
    check either.

    .. math::
        \\alpha = 0.4 \\left[1 - 0.12 \\ln\\left(\\frac{s_u}{P_a}\\right)\\right]

    Parameters
    ----------
    s_u : float
        Undrained shear strength (stress).
    P_a : float
        Atmospheric pressure (same units).

    Returns
    -------
    float
        Adhesion factor alpha (dimensionless).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-14, PDF p. 456
    (printed p. 418).
    """
    if s_u <= 0.0:
        raise ValueError("s_u must be positive.")
    if P_a <= 0.0:
        raise ValueError("P_a must be positive.")
    return 0.4 * (1.0 - 0.12 * math.log(s_u / P_a))


def alpha_coleman_CFA(s_u: float, P_a: float) -> float:
    """Adhesion factor alpha (dimensionless) for CFAs after Coleman and
    Arcement (2002), Equation 6-15 of UFC 3-220-20 (PDF p. 457, printed
    p. 419), coded as alpha = 0.53 / (su/Pa).  The equation is printed as
    alpha = 0.53 (su/Pa), with no exponent; the coded exponent -1 is the
    one Curve E of Figure 6-14 follows.  The manual gives the relation as
    "valid for normalized strengths in the range of 0.24 to 1.42"; su/Pa
    outside that range is refused.

    .. math::
        \\alpha = 0.53 \\left(\\frac{s_u}{P_a}\\right)^{-1}

    Curve E of Figure 6-14 (vector data) is 0.53 / (s_u/P_a): alpha 1.32
    at 0.4, 0.53 at 1.0, 0.39 at 1.37.  As printed, without the exponent,
    alpha would rise with strength (0.53 at su/Pa = 1.0, 0.75 at 1.42),
    which is not the curve.

    Parameters
    ----------
    s_u : float
        Undrained shear strength (stress).
    P_a : float
        Atmospheric pressure (same units).

    Returns
    -------
    float
        Adhesion factor alpha (dimensionless).

    Raises
    ------
    ValueError
        If *s_u* or *P_a* is not positive, or su/Pa is outside 0.24 to
        1.42.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-15, PDF p. 457
    (printed p. 419).
    """
    if s_u <= 0.0:
        raise ValueError("s_u must be positive.")
    if P_a <= 0.0:
        raise ValueError("P_a must be positive.")
    ratio = s_u / P_a
    # 1e-9: a strength entered as exactly 0.24 Pa or 1.42 Pa is in range
    if ratio < 0.24 - 1e-9 or ratio > 1.42 + 1e-9:
        raise ValueError(
            f"su/Pa = {ratio:.3g}: Equation 6-15 (Coleman and Arcement "
            "2002, CFAs) is valid for normalized strengths in the range "
            "of 0.24 to 1.42."
        )
    return 0.53 / ratio


def alpha_API_P2A(s_u: float, sigma_z_eff: float) -> float:
    """Adhesion factor alpha (dimensionless) by the API P2A method
    (Randolph and Murphy 1985), Equations 6-16 and 6-17 of UFC 3-220-20:
    0.5 (su/sigma'z)^-0.5 for su/sigma'z <= 1 and 0.5 (su/sigma'z)^-0.25
    above 1, capped at 1.0 as the manual says for a strength ratio below
    0.25.

    A value of exactly 1 is the printed cap, not the equation.  The
    method was developed from large-diameter (36 inches and more)
    open-end steel pipe piles offshore.

    .. math::
        \\alpha = 0.5 \\left(\\frac{s_u}{\\sigma'_z}\\right)^{-0.5}
        \\quad \\text{for } s_u/\\sigma'_z \\leq 1

        \\alpha = 0.5 \\left(\\frac{s_u}{\\sigma'_z}\\right)^{-0.25}
        \\quad \\text{for } s_u/\\sigma'_z > 1

    Parameters
    ----------
    s_u : float
        Undrained shear strength (stress).
    sigma_z_eff : float
        Effective vertical stress (same units).

    Returns
    -------
    float
        Adhesion factor alpha (dimensionless), capped at 1.0.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equations 6-16 and 6-17, PDF
    p. 457 (printed p. 419).
    """
    if sigma_z_eff <= 0.0:
        raise ValueError("sigma_z_eff must be positive.")
    ratio = s_u / sigma_z_eff
    if ratio <= 1.0:
        alpha = 0.5 * ratio ** (-0.5)
    else:
        alpha = 0.5 * ratio ** (-0.25)
    return min(alpha, 1.0)


def alpha_API_from_OCR(OCR: float) -> float:
    """Adhesion factor alpha (dimensionless) by the API guidance in terms
    of OCR, Equations 6-18 and 6-19 of UFC 3-220-20: 1.07 OCR^-0.4 for
    OCR <= 4.5 and 0.73 OCR^-0.2 above, capped at 1.0 as the manual says
    for an OCR below 1.2.

    A value of exactly 1 is the printed cap, not the equation.

    .. math::
        \\alpha = 1.07 \\cdot OCR^{-0.4} \\quad \\text{for } OCR \\leq 4.5

        \\alpha = 0.73 \\cdot OCR^{-0.2} \\quad \\text{for } OCR > 4.5

    Parameters
    ----------
    OCR : float
        Overconsolidation ratio (dimensionless).

    Returns
    -------
    float
        Adhesion factor alpha (dimensionless), capped at 1.0.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equations 6-18 and 6-19, PDF
    p. 458 (printed p. 420).
    """
    if OCR <= 0.0:
        raise ValueError("OCR must be positive.")
    if OCR <= 4.5:
        alpha = 1.07 * OCR ** (-0.4)
    else:
        alpha = 0.73 * OCR ** (-0.2)
    return min(alpha, 1.0)


# ===========================================================================
# BASE RESISTANCE – DRAINED (Semi-Empirical)
# ===========================================================================

def unit_base_resistance_drained(N_q: float, sigma_zD_eff: float) -> float:
    """Unit base resistance q_b (in the stress unit of sigma'_zD) of a
    deep foundation element (Z/b >= 5) in drained conditions, Equation
    6-20 of UFC 3-220-20: q_b = Nq sigma'_zD.

    .. math::
        q_b = N_q \\cdot \\sigma'_{zD}

    Parameters
    ----------
    N_q : float
        Bearing capacity factor (dimensionless, from Table 6-17).
    sigma_zD_eff : float
        Effective vertical stress at the base elevation (stress).

    Returns
    -------
    float
        Unit base resistance (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-20, PDF p. 459
    (printed p. 421).
    """
    return N_q * sigma_zD_eff


def cheng_Nq(phi_deg: float, Z_over_b: float) -> float:
    """Base resistance factor Nq (dimensionless) for a deep foundation
    element (Z/b >= 5) in drained conditions, from the equation printed
    under Table 6-17 of UFC 3-220-20 (after Cheng 2004):
    Nq = 1.2 (Z/b)^-0.437 exp[6.34 (Z/b)^0.0486 tan phi'], limited to
    200 as the table prints ("unless supported by project-specific
    information").

    The table's own ranges, which the equation reproduces: sand,
    phi' = 32 to 40 degrees, Nq = 37 to 168 at Z/b = 10, 32 to 152 at
    Z/b = 20 and 27 to 139 at Z/b = 40.  A value of exactly 200 is the
    printed limit, not the equation.

    .. math::
        N_q \\approx 1.2 \\left(\\frac{Z}{b}\\right)^{-0.437}
        \\exp\\left[6.34 \\left(\\frac{Z}{b}\\right)^{0.0486}
        \\tan\\phi'\\right] \\le 200

    Parameters
    ----------
    phi_deg : float
        Effective friction angle (degrees).
    Z_over_b : float
        Ratio of embedment depth to pile width (dimensionless).  At
        least 5: Section 6-5.4.3.1 gives the method for deep foundation
        elements, Z/b >= 5.

    Returns
    -------
    float
        Bearing capacity factor Nq (dimensionless), at most 200.

    Raises
    ------
    ValueError
        If *phi_deg* is not between 0 and 90 degrees or *Z_over_b* is
        below 5.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Table 6-17 (Base Resistance
    Factors for Drained Conditions based on Soil Type and Friction
    Angle), PDF p. 459 (printed p. 421).
    """
    if phi_deg <= 0.0 or phi_deg >= 90.0:
        raise ValueError("phi_deg must be between 0 and 90 degrees.")
    if Z_over_b < 5.0:
        raise ValueError(
            f"Z_over_b = {Z_over_b:g}: Section 6-5.4.3.1 and Table 6-17 "
            "give the base resistance of deep foundation elements, "
            "Z/b >= 5."
        )
    tan_phi = math.tan(math.radians(phi_deg))
    N_q = (1.2 * Z_over_b ** (-0.437)
           * math.exp(6.34 * Z_over_b ** 0.0486 * tan_phi))
    return min(N_q, 200.0)


# ===========================================================================
# BASE RESISTANCE – VESIC (Drained)
# ===========================================================================

def unit_base_resistance_vesic_drained(
    N_q_star: float, sigma_m_eff: float
) -> float:
    """Unit base resistance q_b (in the stress unit of sigma'_m) of a deep
    foundation element (Z/b >= 5) in drained conditions by Vesic's
    method, Equation 6-21 of UFC 3-220-20: q_b = N*q sigma'_m.

    .. math::
        q_b = N^*_q \\cdot \\sigma'_m

    Parameters
    ----------
    N_q_star : float
        Modified bearing capacity factor (dimensionless).
    sigma_m_eff : float
        Mean effective stress at b/2 below pile base (stress).

    Returns
    -------
    float
        Unit base resistance (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-21, PDF p. 459
    (printed p. 421).
    """
    return N_q_star * sigma_m_eff


def mean_effective_stress(
    sigma_zD_eff: float, phi_deg: float
) -> float:
    """Mean effective stress sigma'_m (in the stress unit of the input) at
    b/2 below the pile base for K0 conditions, Equation 6-22 of
    UFC 3-220-20: sigma'_m = (1 - (2/3) sin phi') sigma'_zD+b/2.

    Used with Vesic's method (Equations 6-21, 6-23 and 6-24).

    .. math::
        \\sigma'_m = \\left(1 - \\frac{2}{3}\\sin\\phi'\\right)
        \\sigma'_{zD+b/2}

    Parameters
    ----------
    sigma_zD_eff : float
        Effective vertical stress at b/2 below the base prior to pile
        installation (stress).
    phi_deg : float
        Peak effective friction angle within proximity of the base
        (degrees).

    Returns
    -------
    float
        Mean effective stress (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-22, PDF p. 460
    (printed p. 422).
    """
    phi_rad = math.radians(phi_deg)
    return (1.0 - 2.0 / 3.0 * math.sin(phi_rad)) * sigma_zD_eff


def vesic_Nq_star(phi_deg: float, I_rr: float) -> float:
    """Vesic's (1977) modified bearing capacity factor N*q (dimensionless)
    for the base of a deep foundation in drained conditions, Equation 6-23
    of UFC 3-220-20, from the peak friction angle and the reduced rigidity
    index I_rr.

    .. math::
        N^*_q = \\left(\\frac{3}{3 - \\sin\\phi'}\\right)
        e^{\\left(\\frac{\\pi}{2} - \\phi'\\right)\\tan\\phi'}
        \\tan^2\\left(\\frac{\\pi}{4} + \\frac{\\phi'}{2}\\right)
        I_{rr}^{\\frac{4\\sin\\phi'}{3(1+\\sin\\phi')}}

    Parameters
    ----------
    phi_deg : float
        Peak effective friction angle within proximity of the base
        (degrees; the equation takes it in radians).
    I_rr : float
        Reduced rigidity index (dimensionless; Equation 6-25).  For piles
        bearing in soil it normally ranges from 10 to 500.

    Returns
    -------
    float
        Modified bearing capacity factor N*q (dimensionless).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-23, PDF p. 460
    (printed p. 422).
    """
    if I_rr <= 0.0:
        raise ValueError("I_rr must be positive.")
    phi = math.radians(phi_deg)
    sin_phi = math.sin(phi)
    term1 = 3.0 / (3.0 - sin_phi)
    term2 = math.exp((math.pi / 2.0 - phi) * math.tan(phi))
    term3 = math.tan(math.pi / 4.0 + phi / 2.0) ** 2
    exponent = 4.0 * sin_phi / (3.0 * (1.0 + sin_phi))
    term4 = I_rr ** exponent
    return term1 * term2 * term3 * term4


def rigidity_index(E: float, nu: float, sigma_m_eff: float,
                   phi_deg: float) -> float:
    """Rigidity index for coarse-grained soils – Vesic (1977) (Equation 6-24).

    .. math::
        I_r = \\frac{E}{(1 + 2\\nu) \\cdot \\sigma'_m \\cdot \\tan\\phi'}

    Parameters
    ----------
    E : float
        Young's Modulus of the soil (stress).
    nu : float
        Poisson's ratio (dimensionless).
    sigma_m_eff : float
        Mean effective stress (stress).
    phi_deg : float
        Effective friction angle (degrees).

    Returns
    -------
    float
        Rigidity index (dimensionless).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-24, p. 460.
    """
    phi_rad = math.radians(phi_deg)
    denom = (1.0 + 2.0 * nu) * sigma_m_eff * math.tan(phi_rad)
    if denom <= 0.0:
        raise ValueError("Denominator must be positive.")
    return E / denom


def reduced_rigidity_index(I_r: float, epsilon_v: float) -> float:
    """Reduced rigidity index (Equation 6-25).

    .. math::
        I_{rr} = \\frac{I_r}{1 + I_r \\cdot \\varepsilon_v}

    Parameters
    ----------
    I_r : float
        Rigidity index (dimensionless).
    epsilon_v : float
        Volumetric strain from foundation loading (dimensionless).

    Returns
    -------
    float
        Reduced rigidity index (dimensionless).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-25, p. 460.
    """
    return I_r / (1.0 + I_r * epsilon_v)


def volumetric_strain(q_b_app: float, E_s: float, F_nu: float) -> float:
    """Volumetric strain estimate for Vesic method (Equation 6-26).

    .. math::
        \\varepsilon_v \\approx \\frac{q_{b,app} \\cdot F_\\nu}{E_s}

    Parameters
    ----------
    q_b_app : float
        Estimated applied bearing pressure at the base (stress).
    E_s : float
        Young's Modulus of the soil near the base (stress).
    F_nu : float
        Strain factor based on Boussinesq theory and Poisson's ratio
        (dimensionless, from Table 6-18).

    Returns
    -------
    float
        Volumetric strain (dimensionless).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-26, p. 461.
    """
    if E_s <= 0.0:
        raise ValueError("E_s must be positive.")
    return q_b_app * F_nu / E_s


# ===========================================================================
# BASE RESISTANCE – UNDRAINED
# ===========================================================================

def unit_base_resistance_undrained(N_c_star: float, s_u: float) -> float:
    """Unit base resistance for undrained conditions (Equation 6-27).

    .. math::
        q_b = N^*_c \\cdot s_u

    Parameters
    ----------
    N_c_star : float
        Modified bearing capacity factor (dimensionless).
    s_u : float
        Undrained strength near the base (stress).

    Returns
    -------
    float
        Unit base resistance (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-27, p. 461.
    """
    return N_c_star * s_u


def vesic_Nc_star(I_rr: float) -> float:
    """Modified bearing capacity factor N*c by Vesic (1977) (Equation 6-28).

    .. math::
        N^*_c = \\frac{4}{3}(\\ln I_{rr} + 1) + \\frac{\\pi}{2} + 1

    Parameters
    ----------
    I_rr : float
        Reduced rigidity index (dimensionless).

    Returns
    -------
    float
        Modified bearing capacity factor N*c (dimensionless).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-28, p. 461.
    """
    if I_rr <= 0.0:
        raise ValueError("I_rr must be positive.")
    return (4.0 / 3.0) * (math.log(I_rr) + 1.0) + math.pi / 2.0 + 1.0


def undrained_rigidity_index(E_u: float, s_u: float) -> float:
    """Rigidity index for undrained conditions (Equation 6-29).

    .. math::
        I_{rr} = I_r = \\frac{E_u}{3 \\cdot s_u}

    Parameters
    ----------
    E_u : float
        Undrained Young's modulus (stress).
    s_u : float
        Undrained shear strength (stress).

    Returns
    -------
    float
        Rigidity index (dimensionless).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-29, p. 461.
    """
    if s_u <= 0.0:
        raise ValueError("s_u must be positive.")
    return E_u / (3.0 * s_u)


def Nc_star_FHWA_from_Ir(I_r: float) -> float:
    """Base resistance factor N*c (dimensionless) from the rigidity index,
    Equation 6-30 of UFC 3-220-20 (after FHWA 1999):
    N*c = 1.33 [ln(Ir) + 1], limited to 9 as printed.  The manual gives it
    for formed-in-place columns bearing on fine-grained soil with an
    undrained shear strength below 2 ksf (96 kPa); otherwise N*c = 9
    (Brinch Hansen 1957, Z/b of at least 2.5).

    A value of exactly 9 is the printed limit, not the equation.  This is
    not Vesic's Equation 6-28 (``vesic_Nc_star``), which adds pi/2 + 1.

    .. math::
        N^*_c = 1.33 \\left[\\ln(I_r) + 1\\right] \\leq 9

    Parameters
    ----------
    I_r : float
        Rigidity index (dimensionless; Equation 6-29, Eu / (3 su)).

    Returns
    -------
    float
        N*c (dimensionless), at most 9.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-30, PDF p. 462
    (printed p. 424).
    """
    if I_r <= 0.0:
        raise ValueError("I_r must be positive.")
    val = 1.33 * (math.log(I_r) + 1.0)
    return min(val, 9.0)


def Nc_star_FHWA_from_su(s_u: float, P_a: float) -> float:
    """Base resistance factor N*c (dimensionless) from the normalized
    undrained shear strength, Equation 6-31 of UFC 3-220-20 (after FHWA
    1999): N*c = 10.2 - 12.4 [0.1 / (0.1 + su/Pa)], limited to 9 as
    printed.  The manual gives it for formed-in-place columns bearing on
    fine-grained soil with su below 2 ksf (96 kPa); the equation reaches
    the limit of 9 (Brinch Hansen 1957) at about that strength.

    A value of exactly 9 is the printed limit, not the equation.

    .. math::
        N^*_c = 10.2 - 12.4 \\left(\\frac{0.1}{0.1 + s_u/P_a}\\right)
        \\leq 9

    Parameters
    ----------
    s_u : float
        Undrained shear strength within proximity of the base (stress).
    P_a : float
        Atmospheric pressure in the unit of *s_u* (101.325 kPa,
        2116 psf).

    Returns
    -------
    float
        N*c (dimensionless), at most 9.

    Raises
    ------
    ValueError
        If *P_a* is not positive or *s_u* is negative.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-31, PDF p. 462
    (printed p. 424).
    """
    if P_a <= 0.0:
        raise ValueError("P_a must be positive.")
    if s_u < 0.0:
        raise ValueError("s_u must be non-negative.")
    ratio = s_u / P_a
    val = 10.2 - 12.4 * (0.1 / (0.1 + ratio))
    return min(val, 9.0)


# ===========================================================================
# SPT AND CPT-BASED METHODS (LCPC)
# ===========================================================================

def lcpc_unit_shaft_resistance(
    q_c: float, P_a: float, k_s: float, fp_over_Pa: float
) -> float:
    """Nominal unit side resistance f_s (in the stress unit of q_c and Pa)
    by the LCPC method from the CPT, Equation 6-32 of UFC 3-220-20:
    f_s = (Pa / ks)(qc / Pa), limited to Pa (fp/Pa) as printed, with ks
    from Table 6-21 and the ratio fp/Pa from Table 6-22.

    A result equal to Pa (fp/Pa) is the printed limit, not qc / ks.  The
    limit is taken as the table gives it, the ratio fp/Pa (0.15 to 1.5),
    so a maximum side resistance entered as a stress is refused.

    .. math::
        f_s = \\frac{P_a}{k_s}\\left(\\frac{q_c}{P_a}\\right)
        \\leq P_a\\left(\\frac{f_p}{P_a}\\right)

    Parameters
    ----------
    q_c : float
        Cone tip resistance (stress).
    P_a : float
        Atmospheric pressure in the unit of *q_c* (101.325 kPa,
        2116 psf).
    k_s : float
        Side resistance factor (dimensionless, from Table 6-21,
        ``table_6_21_ks``).
    fp_over_Pa : float
        Maximum unit side resistance divided by atmospheric pressure
        (dimensionless, from Table 6-22, ``table_6_22_fp``: 0.15 to 1.5).
        Not a stress.

    Returns
    -------
    float
        Unit side resistance (stress), at most Pa (fp/Pa).

    Raises
    ------
    ValueError
        If *k_s* or *P_a* is not positive, or *fp_over_Pa* is not
        positive or is above 1.5, the largest ratio Table 6-22 prints.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-32, PDF p. 463
    (printed p. 425); Table 6-22, PDF p. 465 (printed p. 427).
    """
    if k_s <= 0.0:
        raise ValueError("k_s must be positive.")
    if P_a <= 0.0:
        raise ValueError("P_a must be positive.")
    if fp_over_Pa <= 0.0 or fp_over_Pa > 1.5:
        raise ValueError(
            f"fp_over_Pa = {fp_over_Pa:g}: Equation 6-32 takes the "
            "maximum unit side resistance as the ratio fp/Pa of Table "
            "6-22, which runs from 0.15 to 1.5; a larger number is a "
            "stress, not the ratio."
        )
    f_s = (P_a / k_s) * (q_c / P_a)
    return min(f_s, P_a * fp_over_Pa)


def lcpc_unit_base_resistance(
    q_c_avg: float, P_a: float, k_t: float
) -> float:
    """Nominal unit base resistance q_b (in the stress unit of q_c,a) by
    the LCPC method from the CPT, Equation 6-33 of UFC 3-220-20:
    q_b = Pa kt (qc,a / Pa), that is kt times the average cone tip
    resistance near the base, with kt from Table 6-23 (0.2 to 0.55).

    The average cone tip resistance is taken over 1.5 b above and below
    the base, discarding values above the base until all fall within 70 %
    to 130 % of the average, and values below the base until none exceeds
    130 % of the average.

    .. math::
        q_b = P_a \\, k_t \\left(\\frac{q_{c,a}}{P_a}\\right)

    Parameters
    ----------
    q_c_avg : float
        Average cone tip resistance in the vicinity of the base (stress).
    P_a : float
        Atmospheric pressure (same units).
    k_t : float
        Base bearing factor (dimensionless, from Table 6-23,
        ``table_6_23_kt``: 0.2 to 0.55).

    Returns
    -------
    float
        Unit base resistance (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-33, PDF p. 463
    (printed p. 425).
    """
    if k_t <= 0.0:
        raise ValueError("k_t must be positive.")
    if P_a <= 0.0:
        raise ValueError("P_a must be positive.")
    return P_a * k_t * (q_c_avg / P_a)


# ===========================================================================
# MICROPILES
# ===========================================================================

def micropile_shaft_resistance(
    alpha_bond: float, b: float, Z_b: float
) -> float:
    """Nominal side resistance of a micropile (Equation 6-34).

    .. math::
        R_s = \\alpha_{bond} \\cdot \\pi \\cdot b \\cdot Z_b

    Parameters
    ----------
    alpha_bond : float
        Nominal unit grout-to-ground bond strength (stress).
    b : float
        Diameter of the bond zone (length).
    Z_b : float
        Length of the bond zone (length).

    Returns
    -------
    float
        Nominal side resistance (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-34, p. 466.
    """
    if b <= 0.0:
        raise ValueError("b must be positive.")
    if Z_b <= 0.0:
        raise ValueError("Z_b must be positive.")
    return alpha_bond * math.pi * b * Z_b


# ===========================================================================
# ROCK SOCKETS
# ===========================================================================

def rock_socket_unit_shaft_resistance(
    q_u: float, P_a: float, C: float = 1.0, n: float = 0.5
) -> float:
    """Unit side resistance of a rock socket (Equation 6-35).

    .. math::
        f_s = C \\cdot P_a \\left(\\frac{q_u}{P_a}\\right)^n

    Parameters
    ----------
    q_u : float
        Lesser of unconfined compressive strength of rock and concrete (stress).
    P_a : float
        Atmospheric pressure (same units).
    C : float, optional
        Fitting parameter (default 1.0 for normal rock).
    n : float, optional
        Fitting exponent (default 0.5).

    Returns
    -------
    float
        Unit side resistance (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-35, p. 468.
    """
    if P_a <= 0.0:
        raise ValueError("P_a must be positive.")
    return C * P_a * (q_u / P_a) ** n


def rock_socket_unit_base_resistance(
    N_cr_star: float, q_u: float
) -> float:
    """Unit base resistance for rock-socketed drilled shafts (Equation 6-36).

    .. math::
        q_b = N^*_{cr} \\cdot q_u

    Parameters
    ----------
    N_cr_star : float
        Modified bearing capacity factor for rock (dimensionless,
        typically 2.5 for clean, level sockets).
    q_u : float
        Unconfined compressive strength of rock (stress).

    Returns
    -------
    float
        Unit base resistance (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-36, p. 469.
    """
    return N_cr_star * q_u


# ===========================================================================
# GROUP CAPACITY
# ===========================================================================

def group_axial_capacity(
    n: int, eta_g: float, R_r: float, R_r_gblock: float
) -> float:
    """Factored axial capacity of a pile group (Equation 6-37).

    .. math::
        R_{r,g} = \\min(n \\cdot \\eta_g \\cdot R_r, \\; R_{r,gblock})

    Parameters
    ----------
    n : int
        Number of columns.
    eta_g : float
        Group efficiency factor (dimensionless, typically 1.0).
    R_r : float
        Factored single column capacity (force).
    R_r_gblock : float
        Factored resistance to block failure (force).

    Returns
    -------
    float
        Factored axial capacity of the group (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-37, p. 469.
    """
    return min(n * eta_g * R_r, R_r_gblock)


def block_failure_resistance(
    Z: float, B: float, L: float, f_s1: float,
    s_u2: float, N_c: float
) -> float:
    """Nominal resistance to block failure (Equation 6-38).

    .. math::
        R_{n,gblock} = 2 Z (B + L) f_{s,1} + B \\cdot L \\cdot s_{u,2} \\cdot N_c

    Parameters
    ----------
    Z : float
        Depth of column embedment (length).
    B : float
        Short plan dimension of the group (length).
    L : float
        Long plan dimension of the group (length).
    f_s1 : float
        Weighted average unit shaft resistance (stress).
    s_u2 : float
        Average undrained strength from base to 2B-3B below base (stress).
    N_c : float
        Bearing capacity factor (dimensionless, from Equation 6-39).

    Returns
    -------
    float
        Nominal block failure resistance (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-38, p. 471.
    """
    return 2.0 * Z * (B + L) * f_s1 + B * L * s_u2 * N_c


def block_failure_Nc(B: float, L: float, Z: float) -> float:
    """Bearing capacity factor Nc (dimensionless) for block failure of a
    group of columns (Brinch-Hansen 1957), Equation 6-39 of UFC 3-220-20:
    Nc = 5 (1 + 0.2 B/L)(1 + 0.2 Z/B), limited to 9 as printed.

    A value of exactly 9 is the printed limit, not the equation (the
    manual's Appendix B Example 5: B = L = 18 ft, Z = 60 ft gives 10, so
    9 is used).

    .. math::
        N_c = 5 \\left(1 + \\frac{0.2 B}{L}\\right)
        \\left(1 + \\frac{0.2 Z}{B}\\right) \\leq 9

    Parameters
    ----------
    B : float
        Short plan dimension (length).
    L : float
        Long plan dimension (length).
    Z : float
        Embedment depth (length).

    Returns
    -------
    float
        Nc (dimensionless), capped at 9.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-39, PDF p. 471
    (printed p. 433); Appendix B Example 5, PDF p. 676 (printed p. 638).
    """
    if L <= 0.0:
        raise ValueError("L must be positive.")
    if B <= 0.0:
        raise ValueError("B must be positive.")
    val = 5.0 * (1.0 + 0.2 * B / L) * (1.0 + 0.2 * Z / B)
    return min(val, 9.0)


# ===========================================================================
# UPLIFT CAPACITY
# ===========================================================================

def group_uplift_capacity(
    n: int, R_r_s: float, W_r_e: float, W_r_e_cap: float,
    R_r_ublock: float
) -> float:
    """Combined factored uplift capacity R_r,gu (force) of a group of n
    columns, Equation 6-40 of UFC 3-220-20: the smaller of
    n (R_r,s + W_r,e) + W_r,e,cap and the block capacity R_r,ublock.

    The effective weight of a single column, W_r,e, is counted for each
    of the n columns.

    .. math::
        R_{r,gu} = \\min\\left(n \\left(R_{r,s} + W_{r,e}\\right)
        + W_{r,e,cap}, \\; R_{r,ublock}\\right)

    Parameters
    ----------
    n : int
        Number of columns.
    R_r_s : float
        Factored uplift capacity of a single column (force).
    W_r_e : float
        Factored effective weight of a single column (force).
    W_r_e_cap : float
        Factored effective weight of the pile cap (force).
    R_r_ublock : float
        Factored uplift capacity of block (force).

    Returns
    -------
    float
        Combined factored uplift capacity (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-40, PDF p. 473
    (printed p. 435).
    """
    individual = n * (R_r_s + W_r_e) + W_r_e_cap
    return min(individual, R_r_ublock)


def uplift_block_volume(B: float, L: float, Z: float) -> float:
    """Volume V_block (length^3) of the soil block lifted by a group of
    columns in coarse-grained soil, Equation 6-41 of UFC 3-220-20, for a
    uniform soil profile: V = B L Z + (Z^2 / 4)(B + L) + Z^3 / 12, the
    truncated prism of Figure 6-16(a) with sides at 4V:1H.

    For layered profiles or a water table within the block, the manual
    divides the block into layers: each layer's thickness replaces Z, and
    B and L become the block's dimensions at the bottom of that layer.

    .. math::
        V_{block} = B \\cdot L \\cdot Z + \\frac{Z^2}{4}(B + L)
        + \\frac{Z^3}{12}

    Parameters
    ----------
    B : float
        Short plan dimension of the group (length).
    L : float
        Long plan dimension of the group (length).
    Z : float
        Embedment depth of the group (length).

    Returns
    -------
    float
        Volume of the block (length^3).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-41, PDF p. 474
    (printed p. 436).
    """
    return B * L * Z + Z ** 2 / 4.0 * (B + L) + Z ** 3 / 12.0


def uplift_block_weight_undrained(
    B: float, L: float, Z1: float, Z2: float,
    gamma_m: float, gamma_b: float, W_cap: float
) -> float:
    """Effective weight of uplift block for undrained conditions (Equation 6-42).

    .. math::
        W_{e,g} = B \\cdot L \\cdot (Z_1 \\gamma_m + Z_2 \\gamma_b) + W_{cap}

    Parameters
    ----------
    B : float
        Short plan dimension (length).
    L : float
        Long plan dimension (length).
    Z1 : float
        Depth above water table (length).
    Z2 : float
        Depth below water table (length).
    gamma_m : float
        Moist unit weight (force/length^3).
    gamma_b : float
        Buoyant unit weight (force/length^3).
    W_cap : float
        Weight of the pile cap (force).

    Returns
    -------
    float
        Effective weight of the block (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-42, p. 474.
    """
    return B * L * (Z1 * gamma_m + Z2 * gamma_b) + W_cap


def uplift_block_capacity_undrained(
    Z: float, B: float, L: float, s_u_avg: float, W_e_g: float
) -> float:
    """Uplift block capacity for undrained conditions (Equation 6-43).

    .. math::
        R_{n,block} = 2 Z (B + L) s_{u,avg} + W_{e,g}

    Parameters
    ----------
    Z : float
        Total embedment depth (length).
    B : float
        Short plan dimension (length).
    L : float
        Long plan dimension (length).
    s_u_avg : float
        Average undrained shear strength along block sides (stress).
    W_e_g : float
        Effective weight of the block (force).

    Returns
    -------
    float
        Nominal block uplift capacity (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-43, p. 474.
    """
    return 2.0 * Z * (B + L) * s_u_avg + W_e_g


# ===========================================================================
# SETTLEMENT
# ===========================================================================

def elastic_compression_pile(
    delta_Q: float, Z: float, A_p: float, E_p: float
) -> float:
    """Elastic compression of a foundation element (Equation 6-45).

    .. math::
        \\delta_e = \\frac{\\Delta Q \\cdot Z}{A_p \\cdot E_p}

    Parameters
    ----------
    delta_Q : float
        Average change in load over the element length (force).
    Z : float
        Length of the element (length).
    A_p : float
        Cross-sectional area of pile material (length^2).
    E_p : float
        Young's Modulus of pile material (stress).

    Returns
    -------
    float
        Elastic compression (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-45, p. 479.
    """
    if A_p <= 0.0:
        raise ValueError("A_p must be positive.")
    if E_p <= 0.0:
        raise ValueError("E_p must be positive.")
    return delta_Q * Z / (A_p * E_p)


def meyerhof_group_settlement(
    Q_d: float, B: float, L: float, N1_60: float, I_f: float
) -> float:
    """Settlement of a pile group in coarse-grained soil – Meyerhof (1976)
    (Equation 6-46).

    .. math::
        \\delta_s = \\frac{Q_d \\sqrt{B}}{B \\cdot L \\cdot \\bar{N}_{1,60}} \\cdot I_f

    Parameters
    ----------
    Q_d : float
        Unfactored group design load (kips).
    B : float
        Short dimension of pile group (ft).
    L : float
        Long dimension of pile group (ft).
    N1_60 : float
        Average overburden-corrected N value within B below base (blows/ft).
    I_f : float
        Influence factor (dimensionless, from Equation 6-47).

    Returns
    -------
    float
        Estimated settlement (inches).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-46, p. 480.
    """
    if N1_60 <= 0.0:
        raise ValueError("N1_60 must be positive.")
    if B <= 0.0 or L <= 0.0:
        raise ValueError("B and L must be positive.")
    return Q_d * math.sqrt(B) / (B * L * N1_60) * I_f


def meyerhof_influence_factor(Z: float, B: float) -> float:
    """Influence factor I_f (dimensionless) for the settlement of a pile
    group in coarse-grained soil by Equation 6-46, Equation 6-47 of
    UFC 3-220-20: I_f = the larger of 1 - Z / (12 B) and 0.5, with Z the
    length of the group and B its width in the same unit.

    I_f falls from 1 for a short group to 0.5 at Z = 6 B and stays 0.5
    for longer groups.

    .. math::
        I_f = \\max\\left(1 - \\frac{Z}{12 B}, \\; 0.5\\right)

    Parameters
    ----------
    Z : float
        Length of the pile group (same units as B).
    B : float
        Width of the pile group, as defined in Figure 6-15.

    Returns
    -------
    float
        Influence factor (dimensionless), from 0.5 to 1.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-47, PDF p. 480
    (printed p. 442).
    """
    if B <= 0.0:
        raise ValueError("B must be positive.")
    if Z <= 0.0:
        raise ValueError("Z must be positive.")
    return max(1.0 - Z / (12.0 * B), 0.5)


def drilled_shaft_base_resistance_at_4pct(
    R_b: float, soil_type: str
) -> float:
    """Nominal base resistance R'_b (in the force unit of R_b) of a
    drilled shaft at a displacement of 4 % of its diameter, Equation 6-48
    of UFC 3-220-20: R'_b = R_b for fine-grained (cohesive) soils and
    0.71 R_b for coarse-grained (cohesionless) soils.

    Used with Figure 6-17 and Table 6-31 (Chen and Kulhawy 2002): the
    failure threshold FT is the nominal shaft resistance plus R'_b.

    .. math::
        R'_b = \\begin{cases}
        R_b & \\text{fine-grained (cohesive) soils} \\\\
        0.71 \\cdot R_b & \\text{coarse-grained (cohesionless) soils}
        \\end{cases}

    Parameters
    ----------
    R_b : float
        Nominal base resistance (force): Equation 6-27 for fine-grained
        soils, Reese and O'Neill (1989) in Table 6-20 for cohesionless
        soils.
    soil_type : str
        Either ``'fine'`` or ``'coarse'``.

    Returns
    -------
    float
        Base resistance at 4% displacement (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-48, PDF p. 481
    (printed p. 443).
    """
    if soil_type == "fine":
        return R_b
    elif soil_type == "coarse":
        return 0.71 * R_b
    else:
        raise ValueError("soil_type must be 'fine' or 'coarse'.")


def equivalent_footing_width(B: float, z2: float) -> float:
    """Width B' (in the length unit of B) of the equivalent footing for
    the settlement of a group of deep foundation elements, Equation 6-49
    of UFC 3-220-20: B' = B + z2 / 2, with z2 the depth interval over
    which the load spreads at 4V:1H above the equivalent footing.

    Below the equivalent footing the load spreads at 2V:1H
    (Equation 6-51, ``stress_change_2V1H``).  With no spreading above the
    footing (z2 = 0) B' = B, as in the manual's Appendix B Example 5.

    .. math::
        B' = B + \\frac{z_2}{2}

    Parameters
    ----------
    B : float
        Width of the group of elements, Figure 6-15 (length).
    z2 : float
        Depth interval of load spreading at 4V:1H (length).

    Returns
    -------
    float
        Equivalent footing width (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-49, PDF p. 483
    (printed p. 445).
    """
    return B + z2 / 2.0


def equivalent_footing_length(L: float, z2: float) -> float:
    """Length L' (in the length unit of L) of the equivalent footing for
    the settlement of a group of deep foundation elements, Equation 6-50
    of UFC 3-220-20: L' = L + z2 / 2, with z2 the depth interval over
    which the load spreads at 4V:1H above the equivalent footing.

    .. math::
        L' = L + \\frac{z_2}{2}

    Parameters
    ----------
    L : float
        Length of the group of elements, Figure 6-15 (length).
    z2 : float
        Depth interval of load spreading at 4V:1H (length).

    Returns
    -------
    float
        Equivalent footing length (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-50, PDF p. 483
    (printed p. 445).
    """
    return L + z2 / 2.0


def stress_change_2V1H(
    Q: float, B_prime: float, L_prime: float, z_prime: float
) -> float:
    """Change in total vertical stress by 2V:1H load spreading (Equation 6-51).

    .. math::
        \\Delta\\sigma_z = \\frac{Q}{(B' + z')(L' + z')}

    Parameters
    ----------
    Q : float
        Applied load (force).
    B_prime : float
        Equivalent footing width (length).
    L_prime : float
        Equivalent footing length (length).
    z_prime : float
        Depth below the equivalent footing (length).

    Returns
    -------
    float
        Change in total vertical stress (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-51, PDF p. 483
    (printed p. 445).
    """
    denom = (B_prime + z_prime) * (L_prime + z_prime)
    if denom <= 0.0:
        raise ValueError("Denominator must be positive.")
    return Q / denom


def stress_change_neutral_plane(
    Q: float, B_prime: float, L_prime: float, z_prime: float,
    delta_sigma_other: float = 0.0
) -> float:
    """Stress change at depth using neutral plane method (Equation 6-52).

    .. math::
        \\Delta\\sigma_z = \\frac{Q}{(B' + z')(L' + z')} + \\Delta\\sigma_{z,other}

    Parameters
    ----------
    Q : float
        Applied load (force).
    B_prime : float
        Equivalent footing width (length).
    L_prime : float
        Equivalent footing length (length).
    z_prime : float
        Depth below equivalent footing (length).
    delta_sigma_other : float, optional
        Additional stress change from other sources (stress), default 0.

    Returns
    -------
    float
        Total stress change (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-52, p. 486.
    """
    return stress_change_2V1H(Q, B_prime, L_prime, z_prime) + delta_sigma_other


def settlement_clay(
    H0: float, C_er: float, C_ec: float,
    sigma_z0_eff: float, sigma_p: float, delta_sigma_z: float
) -> float:
    """Settlement of clay using compression indices (Equation 6-53).

    .. math::
        \\delta_s = C_{\\varepsilon r} H_0 \\log\\frac{\\min(\\sigma'_{z0}+\\Delta\\sigma'_z, \\sigma'_p)}{\\sigma'_{z0}}
        + C_{\\varepsilon c} H_0 \\log\\frac{\\max(\\sigma'_{z0}+\\Delta\\sigma'_z, \\sigma'_p)}{\\sigma'_p}

    Parameters
    ----------
    H0 : float
        Initial thickness of consolidating layer (length).
    C_er : float
        Modified recompression index (dimensionless).
    C_ec : float
        Modified compression index (dimensionless).
    sigma_z0_eff : float
        Initial effective vertical stress (stress).
    sigma_p : float
        Preconsolidation stress (stress).
    delta_sigma_z : float
        Change in effective vertical stress (stress).

    Returns
    -------
    float
        Settlement (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-53, p. 486.
    """
    if sigma_z0_eff <= 0.0:
        raise ValueError("sigma_z0_eff must be positive.")
    if sigma_p <= 0.0:
        raise ValueError("sigma_p must be positive.")
    sigma_final = sigma_z0_eff + delta_sigma_z
    if sigma_final <= 0.0:
        raise ValueError("Final effective stress must be positive.")

    settlement = 0.0
    if sigma_final <= sigma_p:
        # Entirely in recompression range
        settlement = C_er * H0 * math.log10(sigma_final / sigma_z0_eff)
    elif sigma_z0_eff >= sigma_p:
        # Entirely in virgin compression range
        settlement = C_ec * H0 * math.log10(sigma_final / sigma_z0_eff)
    else:
        # Spans both ranges
        settlement = (C_er * H0 * math.log10(sigma_p / sigma_z0_eff)
                      + C_ec * H0 * math.log10(sigma_final / sigma_p))
    return settlement


def settlement_sand_elastic(
    H0: float, nu_s: float, E_s: float, delta_sigma_z: float
) -> float:
    """Elastic settlement of coarse-grained soil (Equation 6-54).

    .. math::
        \\delta_s = \\frac{H_0 (1+\\nu_s)(1-2\\nu_s)}{(1-\\nu_s) E_s} \\Delta\\sigma'_z

    Parameters
    ----------
    H0 : float
        Thickness of the sand layer (length).
    nu_s : float
        Poisson's ratio (dimensionless).
    E_s : float
        Young's Modulus of the soil (stress).
    delta_sigma_z : float
        Average change in effective vertical stress (stress).

    Returns
    -------
    float
        Settlement (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-54, p. 487.
    """
    if E_s <= 0.0:
        raise ValueError("E_s must be positive.")
    return (H0 * (1.0 + nu_s) * (1.0 - 2.0 * nu_s)
            / ((1.0 - nu_s) * E_s) * delta_sigma_z)


# ===========================================================================
# LATERAL CAPACITY – BROMS METHOD
# ===========================================================================

def broms_factored_load(P_dead: float, P_live: float) -> float:
    """Factored ultimate lateral load for Broms analysis (Equation 6-55).

    .. math::
        P_{t,ult} = 1.5 P_{t,dead} + 2.0 P_{t,live}

    Parameters
    ----------
    P_dead : float
        Applied lateral load from dead load (force).
    P_live : float
        Applied lateral load from live load (force).

    Returns
    -------
    float
        Factored ultimate lateral load (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-55, p. 494.
    """
    return 1.5 * P_dead + 2.0 * P_live


def broms_factored_moment(M_dead: float, M_live: float) -> float:
    """Factored ultimate moment for Broms analysis (Equation 6-56).

    .. math::
        M_{t,ult} = 1.5 M_{t,dead} + 2.0 M_{t,live}

    Parameters
    ----------
    M_dead : float
        Applied moment from dead load (force*length).
    M_live : float
        Applied moment from live load (force*length).

    Returns
    -------
    float
        Factored ultimate moment (force*length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-56, p. 494.
    """
    return 1.5 * M_dead + 2.0 * M_live


def broms_factored_su(s_u: float) -> float:
    """Factored undrained shear strength for Broms analysis (Equation 6-57).

    .. math::
        s^*_u = 0.75 \\cdot s_u

    Parameters
    ----------
    s_u : float
        Undrained shear strength (stress).

    Returns
    -------
    float
        Factored undrained shear strength (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-57, p. 494.
    """
    return 0.75 * s_u


def broms_factored_phi(phi_deg: float) -> float:
    """Factored friction angle for Broms analysis (Equation 6-58).

    .. math::
        \\phi'^* = \\arctan(0.75 \\tan\\phi')

    Parameters
    ----------
    phi_deg : float
        Effective friction angle (degrees).

    Returns
    -------
    float
        Factored friction angle (degrees).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-58, p. 494.
    """
    return math.degrees(math.atan(0.75 * math.tan(math.radians(phi_deg))))


def broms_undrained_f(P_t_ult: float, s_u_star: float, b: float) -> float:
    """Length f for Broms method in undrained soil (Equation 6-59).

    Length of pile required to resist the applied lateral load.

    .. math::
        f = \\frac{P_{t,ult}}{9 \\cdot s^*_u \\cdot b}

    Parameters
    ----------
    P_t_ult : float
        Factored ultimate lateral load (force).
    s_u_star : float
        Factored undrained shear strength (stress).
    b : float
        Width or diameter of the pile (length).

    Returns
    -------
    float
        Length f (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-59, p. 494.
    """
    if s_u_star <= 0.0:
        raise ValueError("s_u_star must be positive.")
    if b <= 0.0:
        raise ValueError("b must be positive.")
    return P_t_ult / (9.0 * s_u_star * b)


def broms_undrained_g(
    M_t_ult: float, P_t_ult: float, b: float, f: float,
    s_u_star: float
) -> float:
    """Length g for Broms method in undrained soil (Equation 6-60).

    .. math::
        g = \\sqrt{\\frac{M_{t,ult} + P_{t,ult}(1.5b + 0.5f)}{2.25 \\cdot b \\cdot s^*_u}}

    Parameters
    ----------
    M_t_ult : float
        Factored ultimate moment (force*length).
    P_t_ult : float
        Factored ultimate lateral load (force).
    b : float
        Pile width or diameter (length).
    f : float
        Length f from Equation 6-59 (length).
    s_u_star : float
        Factored undrained shear strength (stress).

    Returns
    -------
    float
        Length g (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-60, p. 495.
    """
    numerator = M_t_ult + P_t_ult * (1.5 * b + 0.5 * f)
    denominator = 2.25 * b * s_u_star
    if denominator <= 0.0:
        raise ValueError("Denominator must be positive.")
    return math.sqrt(numerator / denominator)


def broms_undrained_Zmin(b: float, f: float, g: float) -> float:
    """Minimum pile length for Broms method, undrained (Equation 6-61).

    .. math::
        Z_{min} = 1.5 b + f + g

    Parameters
    ----------
    b : float
        Pile width or diameter (length).
    f : float
        Length f (length).
    g : float
        Length g (length).

    Returns
    -------
    float
        Minimum pile length (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-61, p. 495.
    """
    return 1.5 * b + f + g


def broms_drained_passive(
    gamma_eff: float, b: float, K_P: float, Z_min: float
) -> float:
    """Passive resistance for Broms method, drained soil (Equation 6-62).

    .. math::
        P_P = \\frac{3}{2} \\gamma' b K_P Z_{min}^2

    Parameters
    ----------
    gamma_eff : float
        Effective unit weight (force/length^3).
    b : float
        Pile width or diameter (length).
    K_P : float
        Rankine passive earth pressure coefficient (dimensionless).
    Z_min : float
        Minimum pile length (length).

    Returns
    -------
    float
        Passive resistance (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-62, p. 495.
    """
    return 1.5 * gamma_eff * b * K_P * Z_min ** 2


def broms_drained_Zmin(
    P_t_ult: float, M_t_ult: float, gamma_eff: float,
    b: float, K_P: float, Z_min_guess: float = 10.0,
    tol: float = 1e-6, max_iter: int = 100
) -> float:
    """Minimum pile length for Broms method, drained (Equation 6-63).

    Iteratively solves:

    .. math::
        Z_{min} = \\left(\\frac{2(P_{t,ult} Z_{min} + M_{t,ult})}
        {\\gamma' b K_P}\\right)^{1/3}

    Parameters
    ----------
    P_t_ult : float
        Factored ultimate lateral load (force).
    M_t_ult : float
        Factored ultimate moment (force*length).
    gamma_eff : float
        Effective unit weight (force/length^3).
    b : float
        Pile width or diameter (length).
    K_P : float
        Rankine passive earth pressure coefficient (dimensionless).
    Z_min_guess : float, optional
        Initial guess for Z_min (length), default 10.
    tol : float, optional
        Convergence tolerance, default 1e-6.
    max_iter : int, optional
        Maximum iterations, default 100.

    Returns
    -------
    float
        Minimum pile length (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-63, p. 496.
    """
    denom = gamma_eff * b * K_P
    if denom <= 0.0:
        raise ValueError("gamma_eff, b, and K_P must all be positive.")
    Z = Z_min_guess
    for _ in range(max_iter):
        Z_new = (2.0 * (P_t_ult * Z + M_t_ult) / denom) ** (1.0 / 3.0)
        if abs(Z_new - Z) < tol:
            return Z_new
        Z = Z_new
    return Z


def broms_drained_zero_shear_depth(
    P_t_ult: float, gamma_eff: float, b: float, K_P: float
) -> float:
    """Depth of zero shear for Broms method, drained (Equation 6-64).

    .. math::
        f = \\sqrt{\\frac{P_{t,ult}}{3 \\gamma' b K_P / 2}}

    Parameters
    ----------
    P_t_ult : float
        Factored ultimate lateral load (force).
    gamma_eff : float
        Effective unit weight (force/length^3).
    b : float
        Pile width or diameter (length).
    K_P : float
        Rankine passive earth pressure coefficient (dimensionless).

    Returns
    -------
    float
        Depth of zero shear f (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-64, p. 496.
    """
    denom = 1.5 * gamma_eff * b * K_P
    if denom <= 0.0:
        raise ValueError("gamma_eff, b, and K_P must all be positive.")
    return math.sqrt(P_t_ult / denom)


def broms_drained_max_moment(
    M_t_ult: float, P_t_ult: float, f: float,
    gamma_eff: float, b: float, K_P: float
) -> float:
    """Maximum moment for Broms method, drained (Equation 6-65).

    .. math::
        M_{max,ult} = M_{t,ult} + P_{t,ult} f
        - \\frac{\\gamma' b K_P f^3}{2}

    Parameters
    ----------
    M_t_ult : float
        Factored ultimate moment (force*length).
    P_t_ult : float
        Factored ultimate lateral load (force).
    f : float
        Depth of zero shear (length).
    gamma_eff : float
        Effective unit weight (force/length^3).
    b : float
        Pile width or diameter (length).
    K_P : float
        Rankine passive earth pressure coefficient (dimensionless).

    Returns
    -------
    float
        Maximum moment (force*length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-65, p. 497.
    """
    return M_t_ult + P_t_ult * f - gamma_eff * b * K_P * f ** 3 / 2.0


# ===========================================================================
# LATERAL CAPACITY – CHARACTERISTIC LOAD METHOD (CLM)
# ===========================================================================

def clm_deflection_from_load(
    P_t: float, P_c: float, b: float, a: float, n: float
) -> float:
    """Lateral deflection from applied load – CLM (Equation 6-66).

    .. math::
        \\frac{y_t}{b} = a \\left(\\frac{P_t}{P_c}\\right)^n

    Parameters
    ----------
    P_t : float
        Applied ground line load (force).
    P_c : float
        Characteristic load (force).
    b : float
        Pile width or diameter (length).
    a : float
        Constant from Table 6-36.
    n : float
        Exponent from Table 6-36.

    Returns
    -------
    float
        Lateral deflection at pile top (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-66, p. 500.
    """
    if P_c <= 0.0:
        raise ValueError("P_c must be positive.")
    return b * a * (P_t / P_c) ** n


def clm_load_from_deflection(
    y_t: float, b: float, P_c: float, a: float, n: float
) -> float:
    """Load from deflection – CLM (Equation 6-67).

    .. math::
        P_t = P_c \\left(\\frac{y_t}{a \\cdot b}\\right)^{1/n}

    Parameters
    ----------
    y_t : float
        Lateral deflection at pile top (length).
    b : float
        Pile width or diameter (length).
    P_c : float
        Characteristic load (force).
    a : float
        Constant from Table 6-36.
    n : float
        Exponent from Table 6-36.

    Returns
    -------
    float
        Applied load (force).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-67, p. 500.
    """
    if a <= 0.0 or b <= 0.0:
        raise ValueError("a and b must be positive.")
    return P_c * (y_t / (a * b)) ** (1.0 / n)


def clm_deflection_from_moment(
    M_t: float, M_c: float, b: float, a: float, n: float
) -> float:
    """Lateral deflection from applied moment – CLM (Equation 6-68).

    .. math::
        \\frac{y_t}{b} = a \\left(\\frac{M_t}{M_c}\\right)^n

    Parameters
    ----------
    M_t : float
        Applied moment at ground line (force*length).
    M_c : float
        Characteristic moment (force*length).
    b : float
        Pile width or diameter (length).
    a : float
        Constant from Table 6-36.
    n : float
        Exponent from Table 6-36.

    Returns
    -------
    float
        Lateral deflection at pile top (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-68, p. 500.
    """
    if M_c <= 0.0:
        raise ValueError("M_c must be positive.")
    return b * a * (M_t / M_c) ** n


def clm_moment_from_deflection(
    y_t: float, b: float, M_c: float, a: float, n: float
) -> float:
    """Moment from deflection – CLM (Equation 6-69).

    .. math::
        M_t = M_c \\left(\\frac{y_t}{a \\cdot b}\\right)^{1/n}

    Parameters
    ----------
    y_t : float
        Lateral deflection at pile top (length).
    b : float
        Pile width or diameter (length).
    M_c : float
        Characteristic moment (force*length).
    a : float
        Constant from Table 6-36.
    n : float
        Exponent from Table 6-36.

    Returns
    -------
    float
        Applied moment (force*length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-69, p. 500.
    """
    if a <= 0.0 or b <= 0.0:
        raise ValueError("a and b must be positive.")
    return M_c * (y_t / (a * b)) ** (1.0 / n)


def clm_max_moment(
    P_t: float, P_c: float, M_c: float, a: float, n: float
) -> float:
    """Maximum moment from applied load – CLM (Equation 6-70).

    .. math::
        \\frac{M_{max}}{M_c} \\approx a \\left(\\frac{P_t}{P_c}\\right)^n

    Parameters
    ----------
    P_t : float
        Applied ground line load (force).
    P_c : float
        Characteristic load (force).
    M_c : float
        Characteristic moment (force*length).
    a : float
        Constant from Table 6-37.
    n : float
        Exponent from Table 6-37.

    Returns
    -------
    float
        Maximum moment (force*length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-70, p. 501.
    """
    if P_c <= 0.0:
        raise ValueError("P_c must be positive.")
    return M_c * a * (P_t / P_c) ** n


def mobilized_passive_resistance(
    P_P_ult: float, y: float, H_cap: float
) -> float:
    """Mobilized passive resistance P_P,mob (in the force unit of P_P,ult)
    on a pile cap that has moved laterally by y, Equation 6-71 of
    UFC 3-220-20: P_P,mob / P_P,ult = y / (0.85 y + 0.006 H_cap), limited
    to 1 as printed.

    A result equal to P_P,ult is the printed limit: the hyperbola
    (Mokwa 1999, Duncan and Mokwa 2001; failure ratio 0.85, full
    resistance at a displacement of 4 % of the cap height) passes it at
    y = 0.04 H_cap.

    .. math::
        \\frac{P_{P,mob}}{P_{P,ult}} =
        \\left(\\frac{y}{0.85 y + 0.006 H_{cap}}\\right) \\leq 1

    Parameters
    ----------
    P_P_ult : float
        Fully mobilized passive resistance (force).
    y : float
        Average lateral movement of the pile cap (length).
    H_cap : float
        Height of the pile cap (same units as y).

    Returns
    -------
    float
        Mobilized passive resistance (force), capped at P_P_ult.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-71, PDF p. 505
    (printed p. 467).
    """
    if P_P_ult <= 0.0:
        raise ValueError("P_P_ult must be positive.")
    if H_cap <= 0.0:
        raise ValueError("H_cap must be positive.")
    if y <= 0.0:
        return 0.0
    P_mob = P_P_ult * y / (0.85 * y + 0.006 * H_cap)
    return min(P_mob, P_P_ult)


# ===========================================================================
# STRUCTURAL CAPACITY – DRIVING STRESSES
# ===========================================================================

def driving_stress_limit_steel(phi_da: float, f_y: float) -> float:
    """Maximum driving stress for steel piles (Equation 6-72).

    .. math::
        \\sigma_{dr} \\leq \\phi_{da} \\cdot 0.9 f_y

    Parameters
    ----------
    phi_da : float
        Resistance factor for pile driving (typically 1.0).
    f_y : float
        Yield strength of steel (stress).

    Returns
    -------
    float
        Maximum allowable driving stress (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-72, p. 507.
    """
    return phi_da * 0.9 * f_y


def driving_stress_limit_concrete_compression(
    phi_da: float, f_c_prime: float, f_pe: float
) -> float:
    """Maximum compressive driving stress for concrete piles (Equation 6-73).

    .. math::
        \\sigma_{dr,comp} \\leq \\phi_{da}(0.85 f'_c - f_{pe})

    Parameters
    ----------
    phi_da : float
        Resistance factor for pile driving (typically 1.0).
    f_c_prime : float
        Design compressive strength of concrete (stress).
    f_pe : float
        Effective prestress (stress).

    Returns
    -------
    float
        Maximum allowable compressive driving stress (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-73, p. 508.
    """
    return phi_da * (0.85 * f_c_prime - f_pe)


def driving_stress_limit_concrete_tension(
    phi_da: float, f_c_prime: float, f_pe: float
) -> float:
    """Maximum tensile driving stress for concrete piles (Equation 6-74).

    .. math::
        \\sigma_{dr,tensile} \\leq \\phi_{da}(0.095 \\sqrt{f'_c} + f_{pe})

    Parameters
    ----------
    phi_da : float
        Resistance factor for pile driving (typically 1.0).
    f_c_prime : float
        Design compressive strength of concrete (ksi).
    f_pe : float
        Effective prestress (ksi).

    Returns
    -------
    float
        Maximum allowable tensile driving stress (ksi).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-74, p. 508.
    """
    return phi_da * (0.095 * math.sqrt(f_c_prime) + f_pe)


def driving_stress_limit_timber(phi_da: float, f_cto: float) -> float:
    """Maximum driving stress for timber piles (Equation 6-75).

    .. math::
        \\sigma_{dr} \\leq \\phi_{da} \\cdot 2.6 \\cdot f_{cto}

    Parameters
    ----------
    phi_da : float
        Resistance factor for pile driving (typically 1.15).
    f_cto : float
        Reference compressive strength parallel to grain (stress).

    Returns
    -------
    float
        Maximum allowable driving stress (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-75, p. 508.
    """
    return phi_da * 2.6 * f_cto


# ===========================================================================
# BUCKLING – DEPTH TO FIXITY
# ===========================================================================

def depth_to_fixity_undrained(
    E_p: float, I_p: float, b: float, k_h: float
) -> float:
    """Depth to fixity Z_f (length) of a pile element in uniform undrained
    soil, Equation 6-76 of UFC 3-220-20 (Davisson and Robinson 1965):
    Z_f = sqrt(2) (Ep Ip / (b kh))^0.25, in any consistent units.

    Z_f is the embedded length that adds to the unbraced length for
    buckling.  The moment of inertia is for the weak axis unless bending
    is only expected in the strong direction; b kh may be taken as the
    soil modulus Es = C su (Equation 6-77).

    .. math::
        Z_f = \\sqrt{2} \\left(\\frac{E_p I_p}{b \\cdot k_h}\\right)^{0.25}

    Parameters
    ----------
    E_p : float
        Elastic modulus of the pile (force/length^2).
    I_p : float
        Moment of inertia of the pile (length^4).
    b : float
        Pile width (length).
    k_h : float
        Coefficient of horizontal subgrade reaction (force/length^3).

    Returns
    -------
    float
        Depth to fixity (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-76, PDF p. 512
    (printed p. 474).
    """
    if b <= 0.0 or k_h <= 0.0:
        raise ValueError("b and k_h must be positive.")
    return math.sqrt(2.0) * (E_p * I_p / (b * k_h)) ** 0.25


def undrained_subgrade_modulus(C: float, s_u: float) -> float:
    """Soil modulus for undrained buckling analysis (Equation 6-77).

    .. math::
        E_s = b \\cdot k_h = C \\cdot s_u

    Parameters
    ----------
    C : float
        Constant (dimensionless, Davisson 1970 recommends 67).
    s_u : float
        Undrained shear strength (stress).

    Returns
    -------
    float
        Soil modulus E_s = b*k_h (stress).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-77, p. 512.
    """
    return C * s_u


def depth_to_fixity_drained(
    E_p: float, I_p: float, n_h: float
) -> float:
    """Depth to fixity for drained (coarse-grained) soil (Equation 6-78).

    .. math::
        Z_f = 1.8 \\left(\\frac{E_p I_p}{n_h}\\right)^{0.2}

    Parameters
    ----------
    E_p : float
        Elastic modulus of the pile (force/length^2).
    I_p : float
        Moment of inertia of the pile (length^4).
    n_h : float
        Rate of increase of subgrade modulus with depth (force/length^3).

    Returns
    -------
    float
        Depth to fixity (length).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-78, p. 513.
    """
    if n_h <= 0.0:
        raise ValueError("n_h must be positive.")
    return 1.8 * (E_p * I_p / n_h) ** 0.2


# ===========================================================================
# DRAG FORCE / DOWNDRAG
# ===========================================================================

def drag_force_check(
    Q_d: float, Q_np: float, P_r: float
) -> bool:
    """Whether a pile passes the structural strength check with drag
    force, Equation 6-80 of UFC 3-220-20 (True or False):
    1.25 Q_d + 1.10 (Q_np - Q_d) <= P_r, all three in one force unit.

    The drag force is Q_np - Q_d, the load at the neutral plane less the
    unfactored permanent load (Figure 6-26); it is not a separate input.
    The 1.10 factor on the drag force is one the manual reports from FHWA
    (2016).  The manual's Appendix B Example 5: Q_d = 40 kips,
    Q_np = 133 kips, P_r = 200 kips gives 152 kips <= 200 kips.

    .. math::
        1.25 Q_d + 1.10 (Q_{np} - Q_d) \\leq P_r

    Parameters
    ----------
    Q_d : float
        Unfactored permanent load on the pile (force).
    Q_np : float
        Maximum load in the pile, at the neutral plane (force).
    P_r : float
        Factored structural resistance of the pile in compression (force).

    Returns
    -------
    bool
        True if the check passes (demand <= capacity).

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Equation 6-80 and Figure 6-26,
    PDF p. 516 (printed p. 478); Appendix B Example 5, PDF p. 678
    (printed p. 640).
    """
    demand = 1.25 * Q_d + 1.10 * (Q_np - Q_d)
    return demand <= P_r


# ===========================================================================
# TABLE 6-18: Factors for Approximating Volumetric Strain
# ===========================================================================

# Table 6-18 (PDF p. 461, printed p. 423): strain factor F_nu by pile shape
# at Poisson's ratio 0.2, 0.25, 0.3, 0.35, 0.4, 0.45 and 0.5.
_TABLE_6_18_NU = [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
_TABLE_6_18_FNU = {
    "square": [0.59, 0.54, 0.48, 0.41, 0.30, 0.17, 0.0],
    "circular": [0.63, 0.58, 0.52, 0.44, 0.33, 0.18, 0.0],
}


def table_6_18_Fnu(poisson_ratio: float, pile_shape: str) -> float:
    """Strain factor F_nu (dimensionless) for approximating the volumetric
    strain below a pile base (Equation 6-26), Table 6-18 of UFC 3-220-20,
    by pile shape ("square" or "circular") for Poisson's ratio from 0.2
    to 0.5, the columns the table prints.

    Square: 0.59, 0.54, 0.48, 0.41, 0.30, 0.17, 0 and circular: 0.63,
    0.58, 0.52, 0.44, 0.33, 0.18, 0 at nu = 0.2, 0.25, 0.3, 0.35, 0.4,
    0.45, 0.5.  Between two printed columns the value is interpolated
    linearly; below 0.2 the table has no column and the function refuses.

    Parameters
    ----------
    poisson_ratio : float
        Poisson's ratio of the soil, from 0.2 to 0.5.
    pile_shape : str
        ``"square"`` or ``"circular"``, the table's two rows.

    Returns
    -------
    float
        Strain factor F_nu (dimensionless), for
        epsilon_v = F_nu q_b,app / E_s (``volumetric_strain``).

    Raises
    ------
    ValueError
        If *poisson_ratio* is outside 0.2 to 0.5 or *pile_shape* is not
        one of the two rows.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Table 6-18 (Factors for
    Approximating Volumetric Strain), PDF p. 461 (printed p. 423).
    """
    shape = pile_shape.lower().strip()
    if shape not in _TABLE_6_18_FNU:
        raise ValueError(
            f"Table 6-18 has no row for pile_shape '{pile_shape}'. "
            f"Choose from: {list(_TABLE_6_18_FNU.keys())}"
        )
    if poisson_ratio < 0.2 or poisson_ratio > 0.5:
        raise ValueError(
            f"poisson_ratio = {poisson_ratio:g} is outside Table 6-18, "
            "which prints the strain factor for Poisson's ratio from 0.2 "
            "to 0.5."
        )
    return _linterp(poisson_ratio, _TABLE_6_18_NU, _TABLE_6_18_FNU[shape])


# ===========================================================================
# TABLES 6-21 / 6-22 / 6-23: LCPC Method Factors
# ===========================================================================

# The three tables (PDF p. 465, printed p. 427, after Bustamante and
# Gianeselli 1982) share eight soil rows, each defined by the soil type and
# a range of qc/Pa, and four foundation groups (printed p. 425):
#   Group I-A   drilled shafts without permanent casing, CFAs,
#               gravity-grouted micropiles, and barrettes
#   Group I-B   drilled shafts with permanent casing
#   Group II-A  driven and jacked concrete piles
#   Group II-B  driven and jacked steel piles

_LCPC_SOIL_ROWS = {
    # key: (printed row name, printed qc/Pa range)
    "soft_clay_and_mud": ("Soft clay and mud", "<10"),
    "moderately_compact_clay": ("Moderately compact clay", "10 to 50"),
    "silt_and_loose_sand": ("Silt and loose sand", "<= 50"),
    "compact_to_stiff_clay_and_compact_silt": (
        "Compact to stiff clay and compact silt", "> 50"),
    "soft_chalk": ("Soft chalk", "<= 50"),
    "moderately_compact_sand_and_gravel": (
        "Moderately compact sand and gravel", "50 to 120"),
    "weathered_to_fragmented_chalk": (
        "Weathered to fragmented chalk", "> 50"),
    "compact_to_very_compact_sand_and_gravel": (
        "Compact to very compact sand and gravel", "> 120"),
}

_LCPC_GROUPS = ("I-A", "I-B", "II-A", "II-B")

# Table 6-21, side resistance factor ks: (I-A, I-B, II-A, II-B)
_TABLE_6_21_KS = {
    "soft_clay_and_mud": (30, 30, 30, 30),
    "moderately_compact_clay": (40, 80, 40, 80),
    "silt_and_loose_sand": (60, 150, 60, 120),
    "compact_to_stiff_clay_and_compact_silt": (60, 120, 60, 120),
    "soft_chalk": (100, 120, 100, 120),
    "moderately_compact_sand_and_gravel": (100, 200, 100, 200),
    "weathered_to_fragmented_chalk": (60, 80, 60, 80),
    "compact_to_very_compact_sand_and_gravel": (150, 300, 150, 200),
}

# Table 6-22, maximum unit side resistance fp/Pa: (I-A, I-B, II-A, II-B),
# each cell (value, value in parentheses or None).  "Note: Values in
# parentheses reflect careful construction."
_TABLE_6_22_FP_OVER_PA = {
    "soft_clay_and_mud": (
        (0.15, None), (0.15, None), (0.15, None), (0.15, None)),
    "moderately_compact_clay": (
        (0.35, 0.8), (0.35, 0.8), (0.35, 0.8), (0.35, None)),
    "silt_and_loose_sand": (
        (0.35, None), (0.35, None), (0.35, None), (0.35, None)),
    "compact_to_stiff_clay_and_compact_silt": (
        (0.35, 0.8), (0.35, 0.8), (0.35, 0.8), (0.35, None)),
    "soft_chalk": (
        (0.35, None), (0.35, None), (0.35, None), (0.35, None)),
    "moderately_compact_sand_and_gravel": (
        (0.8, 1.2), (0.35, 0.8), (0.8, 1.2), (0.8, None)),
    "weathered_to_fragmented_chalk": (
        (1.2, 1.5), (0.8, 1.2), (1.2, 1.5), (1.2, None)),
    "compact_to_very_compact_sand_and_gravel": (
        (1.2, 1.5), (0.8, 1.2), (1.2, 1.5), (1.2, None)),
}

# The largest fp/Pa the table prints (in parentheses).
_TABLE_6_22_FP_OVER_PA_MAX = 1.5

# Table 6-23, base bearing factor kt: (Group I-A&B, Group II-A&B)
_TABLE_6_23_KT = {
    "soft_clay_and_mud": (0.4, 0.5),
    "moderately_compact_clay": (0.35, 0.45),
    "silt_and_loose_sand": (0.4, 0.5),
    "compact_to_stiff_clay_and_compact_silt": (0.45, 0.55),
    "soft_chalk": (0.2, 0.3),
    "moderately_compact_sand_and_gravel": (0.4, 0.5),
    "weathered_to_fragmented_chalk": (0.2, 0.4),
    "compact_to_very_compact_sand_and_gravel": (0.3, 0.4),
}


def _lcpc_soil_row(soil_type: str, table: str) -> str:
    key = soil_type.lower().strip().replace("-", "_").replace(" ", "_")
    if key not in _LCPC_SOIL_ROWS:
        rows = "; ".join(
            f"'{k}' (qc/Pa {v[1]})" for k, v in _LCPC_SOIL_ROWS.items())
        raise ValueError(
            f"{table} has no row for soil_type '{soil_type}'. Its rows, "
            f"each for a range of qc/Pa: {rows}."
        )
    return key


def _lcpc_group(group: str, table: str, merged: bool = False) -> int:
    """Column index of a foundation group.  With ``merged`` (Table 6-23,
    whose columns are Group I-A&B and Group II-A&B) the index is 0 for
    Group I and 1 for Group II."""
    text = str(group).upper()
    for junk in ("GROUP", " ", "_", "-", "&"):
        text = text.replace(junk, "")
    index = {"IA": 0, "IB": 1, "IIA": 2, "IIB": 3}.get(text)
    if merged:
        if text in ("I", "IAB"):
            return 0
        if text in ("II", "IIAB"):
            return 1
        if index is not None:
            return index // 2
    elif index is not None:
        return index
    choices = ("'I' (I-A and I-B) or 'II' (II-A and II-B)" if merged
               else "'I-A', 'I-B', 'II-A' or 'II-B'")
    raise ValueError(
        f"{table} has no column for group '{group}'. Choose {choices}: "
        "Group I-A is drilled shafts without permanent casing, CFAs, "
        "gravity-grouted micropiles and barrettes; I-B drilled shafts "
        "with permanent casing; II-A driven and jacked concrete piles; "
        "II-B driven and jacked steel piles."
    )


def table_6_21_ks(soil_type: str, group: str) -> float:
    """Side resistance factor ks (dimensionless) of the LCPC CPT method,
    Table 6-21 of UFC 3-220-20 (after Bustamante and Gianeselli 1982), by
    the table's soil row and foundation group (I-A, I-B, II-A, II-B); used
    in Equation 6-32, f_s = (Pa / ks)(qc / Pa).

    Each soil row holds for a range of qc/Pa, the cone tip resistance
    over atmospheric pressure; the caller picks the row that matches both
    the soil and its qc/Pa.

    Parameters
    ----------
    soil_type : str
        One of the table's eight rows (qc/Pa range in brackets):
        ``"soft_clay_and_mud"`` (<10), ``"moderately_compact_clay"``
        (10 to 50), ``"silt_and_loose_sand"`` (<= 50),
        ``"compact_to_stiff_clay_and_compact_silt"`` (> 50),
        ``"soft_chalk"`` (<= 50),
        ``"moderately_compact_sand_and_gravel"`` (50 to 120),
        ``"weathered_to_fragmented_chalk"`` (> 50),
        ``"compact_to_very_compact_sand_and_gravel"`` (> 120).
    group : str
        Foundation group: ``"I-A"`` drilled shafts without permanent
        casing, CFAs, gravity-grouted micropiles and barrettes;
        ``"I-B"`` drilled shafts with permanent casing; ``"II-A"`` driven
        and jacked concrete piles; ``"II-B"`` driven and jacked steel
        piles.

    Returns
    -------
    float
        Side resistance factor ks (dimensionless, 30 to 300).

    Raises
    ------
    ValueError
        If the soil row or the group is not in the table.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Table 6-21 (Side Resistance
    Factor), PDF p. 465 (printed p. 427); groups on PDF p. 463 (printed
    p. 425).
    """
    row = _lcpc_soil_row(soil_type, "Table 6-21")
    return float(_TABLE_6_21_KS[row][_lcpc_group(group, "Table 6-21")])


def table_6_22_fp(
    soil_type: str, group: str, careful_construction: bool = False
) -> float:
    """Maximum unit side resistance of the LCPC CPT method as the ratio
    fp/Pa (dimensionless, NOT a stress), Table 6-22 of UFC 3-220-20 (after
    Bustamante and Gianeselli 1982), by the table's soil row and
    foundation group; the limit in Equation 6-32 is Pa (fp/Pa).

    Some cells print a second value in parentheses: "Values in
    parentheses reflect careful construction".  That value is returned
    only when *careful_construction* is True and the cell has one;
    otherwise the cell's first value is returned.  Pass the result to
    ``lcpc_unit_shaft_resistance`` as ``fp_over_Pa``.

    Parameters
    ----------
    soil_type : str
        One of the table's eight rows, as for ``table_6_21_ks``:
        ``"soft_clay_and_mud"`` (qc/Pa <10),
        ``"moderately_compact_clay"`` (10 to 50),
        ``"silt_and_loose_sand"`` (<= 50),
        ``"compact_to_stiff_clay_and_compact_silt"`` (> 50),
        ``"soft_chalk"`` (<= 50),
        ``"moderately_compact_sand_and_gravel"`` (50 to 120),
        ``"weathered_to_fragmented_chalk"`` (> 50),
        ``"compact_to_very_compact_sand_and_gravel"`` (> 120).
    group : str
        Foundation group ``"I-A"``, ``"I-B"``, ``"II-A"`` or ``"II-B"``,
        as for ``table_6_21_ks``.
    careful_construction : bool, optional
        True to take the value the table prints in parentheses, which
        reflects careful construction.  Default False: the first value.

    Returns
    -------
    float
        fp/Pa (dimensionless, 0.15 to 1.5): the maximum unit side
        resistance divided by atmospheric pressure.

    Raises
    ------
    ValueError
        If the soil row or the group is not in the table.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Table 6-22 (Maximum Unit Side
    Resistance), PDF p. 465 (printed p. 427).
    """
    row = _lcpc_soil_row(soil_type, "Table 6-22")
    value, careful = _TABLE_6_22_FP_OVER_PA[row][
        _lcpc_group(group, "Table 6-22")]
    if careful_construction and careful is not None:
        return careful
    return value


def table_6_23_kt(soil_type: str, group: str) -> float:
    """Base bearing factor kt (dimensionless) of the LCPC CPT method,
    Table 6-23 of UFC 3-220-20 (after Bustamante and Gianeselli 1982), by
    the table's soil row and foundation group (I or II); used in
    Equation 6-33, q_b = Pa kt (qc,a / Pa), so q_b is kt times the average
    cone tip resistance near the base.

    The table has one column for Group I-A&B and one for Group II-A&B.
    Each soil row holds for a range of qc,a/Pa.

    Parameters
    ----------
    soil_type : str
        One of the table's eight rows, as for ``table_6_21_ks``:
        ``"soft_clay_and_mud"`` (qca/Pa <10),
        ``"moderately_compact_clay"`` (10 to 50),
        ``"silt_and_loose_sand"`` (<= 50),
        ``"compact_to_stiff_clay_and_compact_silt"`` (> 50),
        ``"soft_chalk"`` (<= 50),
        ``"moderately_compact_sand_and_gravel"`` (50 to 120),
        ``"weathered_to_fragmented_chalk"`` (> 50),
        ``"compact_to_very_compact_sand_and_gravel"`` (> 120).
    group : str
        ``"I"`` (Groups I-A and I-B: drilled shafts, CFAs, gravity-grouted
        micropiles, barrettes) or ``"II"`` (Groups II-A and II-B: driven
        and jacked piles); ``"I-A"``, ``"I-B"``, ``"II-A"`` and ``"II-B"``
        are taken as their group.

    Returns
    -------
    float
        Base bearing factor kt (dimensionless, 0.2 to 0.55).

    Raises
    ------
    ValueError
        If the soil row or the group is not in the table.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Table 6-23 (Base Bearing
    Factor), PDF p. 465 (printed p. 427).
    """
    row = _lcpc_soil_row(soil_type, "Table 6-23")
    return _TABLE_6_23_KT[row][_lcpc_group(group, "Table 6-23", merged=True)]


# ===========================================================================
# TABLE 6-36: Constants for Load and Moment Deflection Equations
# ===========================================================================

# Table 6-36 (PDF p. 500, printed p. 462, after Brettmann and Duncan 1996):
# (soil type, ratio, fixity) -> (a, n).  The Mt/Mc rows print fixity "N/A".
_TABLE_6_36_CLM = {
    ("clay", "pt/pc", "free"): (50.0, 1.822),
    ("clay", "pt/pc", "fixed"): (14.0, 1.846),
    ("clay", "mt/mc", "n/a"): (21.0, 1.412),
    ("sand", "pt/pc", "free"): (119.0, 1.523),
    ("sand", "pt/pc", "fixed"): (28.8, 1.500),
    ("sand", "mt/mc", "n/a"): (36.0, 1.308),
}

_TABLE_6_36_EQUATIONS = {
    "pt/pc": ("y_t/b = a (P_t/P_c)^n (Eq. 6-66); "
              "P_t/P_c = [(1/a)(y_t/b)]^(1/n) (Eq. 6-67)"),
    "mt/mc": ("y_t/b = a (M_t/M_c)^n (Eq. 6-68); "
              "M_t/M_c = [(1/a)(y_t/b)]^(1/n) (Eq. 6-69)"),
}


def table_6_36_clm(soil_type: str, ratio: str, fixity: str) -> dict:
    """Constant a and exponent n (both dimensionless) of the Characteristic
    Load Method deflection equations, Table 6-36 of UFC 3-220-20 (after
    Brettmann and Duncan 1996), by soil type, ratio (Pt/Pc or Mt/Mc) and
    fixity: y_t/b = a (P_t/P_c)^n (Eq. 6-66) or y_t/b = a (M_t/M_c)^n
    (Eq. 6-68).

    The table's six rows: clay, Pt/Pc, free 50.0, 1.822 and fixed 14.0,
    1.846; clay, Mt/Mc (fixity N/A) 21.0, 1.412; sand, Pt/Pc, free 119.0,
    1.523 and fixed 28.8, 1.500; sand, Mt/Mc (N/A) 36.0, 1.308.  y_t is
    the lateral deflection at the top of the element and b its width.

    Parameters
    ----------
    soil_type : str
        ``"clay"`` or ``"sand"``.
    ratio : str
        ``"Pt/Pc"`` (applied load over characteristic load) or
        ``"Mt/Mc"`` (applied moment over characteristic moment).
    fixity : str
        ``"free"`` or ``"fixed"`` for the Pt/Pc rows; ``"n/a"`` for the
        Mt/Mc rows, which the table prints without a fixity.

    Returns
    -------
    dict
        ``{"a": float, "n": float, "equations": str}``: the constants and
        the two printed equations they belong to.

    Raises
    ------
    ValueError
        If the combination is not one of the table's six rows.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Table 6-36 (Constants for Load
    and Moment Deflection Equations) and Equations 6-66 to 6-69, PDF
    p. 500 (printed p. 462).
    """
    key = (
        soil_type.lower().strip(),
        ratio.lower().replace(" ", ""),
        "n/a" if fixity is None else str(fixity).lower().strip(),
    )
    if key not in _TABLE_6_36_CLM:
        raise ValueError(
            f"Table 6-36 has no row for soil_type='{soil_type}', "
            f"ratio='{ratio}', fixity='{fixity}'. Its six rows are "
            "(clay or sand) with ratio 'Pt/Pc' and fixity 'free' or "
            "'fixed', and (clay or sand) with ratio 'Mt/Mc' and fixity "
            "'n/a'."
        )
    a, n = _TABLE_6_36_CLM[key]
    return {"a": a, "n": n, "equations": _TABLE_6_36_EQUATIONS[key[1]]}


# ===========================================================================
# TABLE 6-37: Coefficients for Estimating the Maximum Moment
# ===========================================================================

# Table 6-37 (PDF p. 502, printed p. 464): (soil, fixity) -> (a, n)
_TABLE_6_37_CLM = {
    ("clay", "free"): (0.855, 1.288),
    ("clay", "fixed"): (0.782, 1.249),
    ("sand", "free"): (4.28, 1.384),
    ("sand", "fixed"): (2.64, 1.300),
}


def table_6_37_clm(soil_type: str, fixity: str) -> dict:
    """Coefficient a and exponent n (both dimensionless) for the maximum
    moment by the Characteristic Load Method, Table 6-37 of UFC 3-220-20,
    by soil (clay or sand) and fixity (free or fixed):
    M_max / M_c = a (P_t / P_c)^n (Eq. 6-70).

    The table's four rows: clay, free 0.855, 1.288 and fixed 0.782,
    1.249; sand, free 4.28, 1.384 and fixed 2.64, 1.300.  The maximum
    moment is at the top of the element for 100 % fixity and at a depth
    below the top for 0 % fixity; the equation is for an applied load
    P_t with no applied moment.

    Parameters
    ----------
    soil_type : str
        ``"clay"`` or ``"sand"``.
    fixity : str
        ``"free"`` or ``"fixed"``.

    Returns
    -------
    dict
        ``{"a": float, "n": float, "equations": str}``: the constants and
        the printed equation they belong to.

    Raises
    ------
    ValueError
        If the combination is not one of the table's four rows.

    References
    ----------
    UFC 3-220-20, 16 Jan 2025, Chapter 6, Table 6-37 (Coefficients for
    Estimating the Maximum Moment), PDF p. 502 (printed p. 464);
    Equation 6-70, PDF p. 501 (printed p. 463).
    """
    key = (soil_type.lower().strip(), str(fixity).lower().strip())
    if key not in _TABLE_6_37_CLM:
        raise ValueError(
            f"Table 6-37 has no row for soil_type='{soil_type}', "
            f"fixity='{fixity}'. Its four rows are clay or sand with "
            "fixity 'free' or 'fixed'."
        )
    a, n = _TABLE_6_37_CLM[key]
    return {"a": a, "n": n,
            "equations": "M_max/M_c = a (P_t/P_c)^n (Eq. 6-70)"}
