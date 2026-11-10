"""
UFS 3-220-10, Chapter 8: Correlations for Soil and Rock

Equations 8-1 through 8-45 covering correlations for estimating soil
engineering properties from index tests, SPT, CPT, and dilatometer data.

Topics include:
    - Effective stress friction angle (coarse-grained and fine-grained soils)
    - Undrained shear strength
    - Consolidation parameters (compression index, constrained modulus)
    - Secondary compression
    - Elastic modulus conversions
    - California Bearing Ratio (CBR)
    - Hydraulic conductivity
    - Shear wave velocity

Reference:
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 January 2026
"""

import math
from typing import List, Tuple

from geotech_references._interpolation import _linterp

# ============================================================================
# SECTION 8-2.1: EFFECTIVE STRESS FRICTION ANGLE -- COARSE-GRAINED SOILS
# ============================================================================


def spt_n_correction_for_pore_pressure(n60: float) -> float:
    """Correct SPT N value for dynamic pore pressure effects (Equation 8-1).

    For saturated very fine or silty sand, the measured SPT N value should
    be corrected for dynamic pore pressure effects before using correlations
    based on Table 8-3.  If N60 <= 15 the blow count is returned unchanged;
    if N60 > 15 the correction of Terzaghi and Peck is applied.

    .. math::
        N' = \\begin{cases}
            N_{60}               & \\text{for } N_{60} \\le 15 \\\\
            15 + 0.5(N_{60}-15)  & \\text{for } N_{60} > 15
        \\end{cases}

    Parameters
    ----------
    n60 : float
        SPT blow count corrected for 60% energy (blows/ft).

    Returns
    -------
    float
        Blow count corrected for dynamic pore pressure effects, N'
        (blows/ft).

    Raises
    ------
    ValueError
        If *n60* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-1, p. 396.
    """
    if n60 < 0.0:
        raise ValueError("n60 must be non-negative.")
    if n60 <= 15.0:
        return n60
    return 15.0 + 0.5 * (n60 - 15.0)


def spt_friction_angle_roads(n60: float) -> float:
    """Effective stress friction angle from SPT N60 for roads and bridges (Equation 8-2).

    Correlation by Shioi and Fukui (1982) relating the effective stress
    friction angle of coarse-grained soils to the SPT N value corrected
    for 60% hammer energy.  This form is recommended for road and bridge
    applications.

    .. math::
        \\phi' = \\sqrt{15 \\cdot N_{60}} + 15

    Parameters
    ----------
    n60 : float
        SPT N value corrected for 60% energy (blows/ft).

    Returns
    -------
    float
        Effective stress friction angle, phi' (degrees).

    Raises
    ------
    ValueError
        If *n60* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-2, p. 397.
    """
    if n60 < 0.0:
        raise ValueError("n60 must be non-negative.")
    return math.sqrt(15.0 * n60) + 15.0


def spt_friction_angle_buildings(n60: float) -> float:
    """Effective stress friction angle from SPT N60 for buildings (Equation 8-3).

    Correlation by Shioi and Fukui (1982) relating the effective stress
    friction angle of coarse-grained soils to the SPT N value corrected
    for 60% hammer energy.  This form is recommended for building
    applications.

    .. math::
        \\phi' = 0.3 \\cdot N_{60} + 27

    Parameters
    ----------
    n60 : float
        SPT N value corrected for 60% energy (blows/ft).

    Returns
    -------
    float
        Effective stress friction angle, phi' (degrees).

    Raises
    ------
    ValueError
        If *n60* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-3, p. 397.
    """
    if n60 < 0.0:
        raise ValueError("n60 must be non-negative.")
    return 0.3 * n60 + 27.0


def spt_friction_angle_kulhawy_mayne(
    n60: float, sigma_v_eff: float, pa: float
) -> float:
    """Effective stress friction angle from SPT using Kulhawy and Mayne (Equation 8-4).

    Kulhawy and Mayne (1990) approximation of the Schmertmann (1975) and
    DeMello (1971) relationships between peak effective stress friction
    angle, overburden pressure, and SPT blow count for sands.

    .. math::
        \\tan(\\phi') = \\left[\\frac{N_{60}}{12.2 + 20.3
        \\left(\\frac{\\sigma'_v}{P_a}\\right)}\\right]^{0.34}

    Parameters
    ----------
    n60 : float
        SPT N value corrected for 60% energy (blows/ft).
    sigma_v_eff : float
        Vertical effective stress (stress units, e.g., kPa, psf).
    pa : float
        Atmospheric pressure in the same units as *sigma_v_eff*
        (e.g., 101.325 kPa or 2116.2 psf).

    Returns
    -------
    float
        Effective stress friction angle, phi' (degrees).

    Raises
    ------
    ValueError
        If *n60* is negative, *sigma_v_eff* is negative, or *pa* is not
        positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-4, p. 398.
    """
    if n60 < 0.0:
        raise ValueError("n60 must be non-negative.")
    if sigma_v_eff < 0.0:
        raise ValueError("sigma_v_eff must be non-negative.")
    if pa <= 0.0:
        raise ValueError("pa must be positive.")
    ratio = n60 / (12.2 + 20.3 * (sigma_v_eff / pa))
    if ratio < 0.0:
        raise ValueError("Computed ratio is negative; check inputs.")
    tan_phi = ratio ** 0.34
    return math.degrees(math.atan(tan_phi))


def spt_friction_angle_wolff(n1_60: float) -> float:
    """Effective stress friction angle from N1,60 using Wolff (Equation 8-5).

    Wolff (1989) approximation of the Peck et al. (1974) correlation
    between effective stress friction angle and SPT N value corrected for
    60% energy and overburden pressure (N1,60).

    .. math::
        \\phi' = 27.1 + 0.3 \\cdot N_{1,60} - 0.00054 \\cdot N_{1,60}^2

    Parameters
    ----------
    n1_60 : float
        SPT N value corrected for 60% energy and 1 atm overburden
        pressure (blows/ft).

    Returns
    -------
    float
        Effective stress friction angle, phi' (degrees).

    Raises
    ------
    ValueError
        If *n1_60* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-5, p. 399.
    """
    if n1_60 < 0.0:
        raise ValueError("n1_60 must be non-negative.")
    return 27.1 + 0.3 * n1_60 - 0.00054 * n1_60 ** 2


def spt_friction_angle_hatanaka_uchida(n1_60: float) -> float:
    """Effective stress friction angle from N1,60 using Hatanaka and Uchida (Equation 8-6).

    Hatanaka and Uchida (1996) correlation for the effective stress friction
    angle of sands based on N1,60, developed from triaxial tests on
    high-quality intact frozen samples of natural sands.  The original
    SPT hammer had an efficiency of 78%.

    .. math::
        \\phi' = \\sqrt{15.4 \\cdot N_{1,60}} + 20

    Parameters
    ----------
    n1_60 : float
        SPT N value corrected for 60% energy and 1 atm overburden
        pressure (blows/ft).

    Returns
    -------
    float
        Effective stress friction angle, phi' (degrees).

    Raises
    ------
    ValueError
        If *n1_60* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-6, p. 399.
    """
    if n1_60 < 0.0:
        raise ValueError("n1_60 must be non-negative.")
    return math.sqrt(15.4 * n1_60) + 20.0


# ============================================================================
# SECTION 8-2.1.3: CORRELATIONS WITH CONE PENETRATION TEST (CPT)
# ============================================================================


def cpt_friction_angle_mayne(
    qt: float, sigma_v_eff: float, pa: float
) -> float:
    """Drained friction angle phi' (degrees) of coarse-grained soil from CPT, Equation 8-7 (Mayne 2007).

    Mayne (2007) correlation using calibration chamber tests to estimate
    the effective stress friction angle of coarse-grained soils from CPT
    corrected tip resistance.  As printed (the vertical stress term is
    under a square root)::

        phi' = 17.6 + 11 * log10[ (qt / Pa) / sqrt(sigma'v / Pa) ]

    .. math::
        \\phi' = 17.6 + 11 \\cdot \\log_{10}\\!
        \\left(\\frac{q_t / P_a}{\\sqrt{\\sigma'_v / P_a}}\\right)

    Parameters
    ----------
    qt : float
        Corrected cone tip resistance, qt = qc + u*(1+a) (stress units).
    sigma_v_eff : float
        Effective vertical stress (same units as *qt*).
    pa : float
        Atmospheric pressure (same units as *qt* and *sigma_v_eff*).

    Returns
    -------
    float
        Effective stress friction angle, phi' (degrees).

    Raises
    ------
    ValueError
        If *qt* is not positive, *sigma_v_eff* is not positive, or *pa*
        is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-7, p. 400.
    """
    if qt <= 0.0:
        raise ValueError("qt must be positive.")
    if sigma_v_eff <= 0.0:
        raise ValueError("sigma_v_eff must be positive.")
    if pa <= 0.0:
        raise ValueError("pa must be positive.")
    return 17.6 + 11.0 * math.log10((qt / pa) / math.sqrt(sigma_v_eff / pa))


def cpt_friction_angle_robertson_campanella(
    qc: float, sigma_v_eff: float
) -> float:
    """Drained friction angle phi' (degrees) of sand from CPT tip resistance, Equation 8-8.

    Robertson and Campanella (1983) correlation for the effective stress
    friction angle from electric cone CPT tip resistance tested in a
    calibration chamber on uncemented, unaged, moderately compressible
    quartz sands (Figure 8-8(a)), approximated by Robertson and Cabal
    (2014).  As printed::

        tan(phi') = (1 / 2.68) * [ log10(qc / sigma'v) + 0.29 ]

    .. math::
        \\tan\\phi' = \\frac{1}{2.68}\\left[
        \\log_{10}\\!\\left(\\frac{q_c}{\\sigma'_v}\\right) + 0.29\\right]

    Parameters
    ----------
    qc : float
        Cone tip resistance (stress units).
    sigma_v_eff : float
        Effective vertical stress (same units as *qc*).

    Returns
    -------
    float
        Drained (effective stress) friction angle, phi' (degrees).

    Raises
    ------
    ValueError
        If *qc* is not positive, *sigma_v_eff* is not positive, or
        log10(qc/sigma'v) + 0.29 is not positive (the equation then gives
        no positive friction angle).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-8, p. 402.
    Robertson and Campanella (1983); Robertson and Cabal (2014).
    """
    if qc <= 0.0:
        raise ValueError("qc must be positive.")
    if sigma_v_eff <= 0.0:
        raise ValueError("sigma_v_eff must be positive.")
    bracket = math.log10(qc / sigma_v_eff) + 0.29
    if bracket <= 0.0:
        raise ValueError(
            "log10(qc/sigma_v_eff) + 0.29 is not positive; qc/sigma_v_eff "
            "is too small for Equation 8-8 (UFS 3-220-10 p. 402)."
        )
    return math.degrees(math.atan(bracket / 2.68))


def cpt_oc_nc_resistance_ratio(ocr: float, beta: float) -> float:
    """Ratio of CPT tip resistance in OC vs NC sand (Equation 8-9).

    Schmertmann (1978) correction factor relating the CPT tip resistance
    in overconsolidated (OC) sand to that in normally consolidated (NC)
    sand via the overconsolidation ratio and an empirical exponent.

    .. math::
        R = \\frac{q_{c,OC}}{q_{c,NC}} = 1 + 0.75 (OCR^\\beta - 1)

    Parameters
    ----------
    ocr : float
        Overconsolidation ratio (dimensionless, >= 1.0).
    beta : float
        Empirical exponent (dimensionless).

    Returns
    -------
    float
        Ratio R = qc,OC / qc,NC (dimensionless).

    Raises
    ------
    ValueError
        If *ocr* is less than 1.0.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-9, p. 403.
    """
    if ocr < 1.0:
        raise ValueError("ocr must be >= 1.0.")
    return 1.0 + 0.75 * (ocr ** beta - 1.0)


# ============================================================================
# SECTION 8-2.1.4: CORRELATIONS WITH DILATOMETER (DMT)
# ============================================================================


def dmt_horizontal_stress_index(
    p0: float, u0: float, sigma_v_eff: float
) -> float:
    """Horizontal stress index from dilatometer test (Equation 8-10).

    Marchetti (1997) definition of the horizontal stress index (KD) used
    as the basis for dilatometer-based correlations for the effective stress
    friction angle.

    .. math::
        K_D = \\frac{p_0 - u_0}{\\sigma'_v}

    Parameters
    ----------
    p0 : float
        Corrected pressure required to initiate movement of the DMT
        membrane against the soil (stress units, e.g., kPa).
    u0 : float
        Hydrostatic (in situ) pore pressure (same stress units as *p0*).
    sigma_v_eff : float
        Effective vertical stress (same stress units as *p0*).

    Returns
    -------
    float
        Horizontal stress index, KD (dimensionless).

    Raises
    ------
    ValueError
        If *sigma_v_eff* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-10, p. 406.
    """
    if sigma_v_eff <= 0.0:
        raise ValueError("sigma_v_eff must be positive.")
    return (p0 - u0) / sigma_v_eff


def dmt_friction_angle_upper_bound(kd: float) -> float:
    """Upper bound effective stress friction angle from DMT (Equation 8-11).

    Upper bound estimate of the effective stress friction angle for clean
    sands from the horizontal stress index (KD) of the dilatometer test,
    as proposed by Ricceri et al. (2002).

    .. math::
        \\phi' = 31 + \\frac{K_D}{0.236 + 0.066 \\cdot K_D}

    Parameters
    ----------
    kd : float
        Horizontal stress index from dilatometer test (dimensionless).

    Returns
    -------
    float
        Effective stress friction angle, phi' (degrees).

    Raises
    ------
    ValueError
        If the denominator (0.236 + 0.066 * kd) is zero or negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-11, p. 406.
    """
    denom = 0.236 + 0.066 * kd
    if denom <= 0.0:
        raise ValueError(
            "Denominator (0.236 + 0.066*KD) is non-positive; check KD value."
        )
    return 31.0 + kd / denom


def dmt_friction_angle_lower_bound(kd: float) -> float:
    """Lower bound effective stress friction angle from DMT (Equation 8-12).

    Lower bound estimate of the effective stress friction angle for clean
    sands from the horizontal stress index (KD) of the dilatometer test,
    as proposed by Marchetti (1997).  May underestimate the in situ friction
    angle by 2 to 4 degrees.

    .. math::
        \\phi' = 28 + 14.6 \\cdot \\log_{10}(K_D)
                 - 2.1 \\cdot [\\log_{10}(K_D)]^2

    Parameters
    ----------
    kd : float
        Horizontal stress index from dilatometer test (dimensionless,
        must be > 0).

    Returns
    -------
    float
        Effective stress friction angle, phi' (degrees).

    Raises
    ------
    ValueError
        If *kd* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-12, p. 406.
    """
    if kd <= 0.0:
        raise ValueError("kd must be positive.")
    log_kd = math.log10(kd)
    return 28.0 + 14.6 * log_kd - 2.1 * log_kd ** 2


# ============================================================================
# SECTION 8-2.2: EFFECTIVE STRESS FRICTION ANGLE -- FINE-GRAINED SOILS
# ============================================================================


def fully_softened_friction_angle(pi: float) -> float:
    """Fully softened friction angle phi'FS (degrees) from plasticity index, Equation 8-13.

    Gibson (1953) relationship for the fully softened friction angle
    (phi'FS), the mean trend line of Figure 8-13 as approximated by
    Carter and Bentley (2016).  The fully softened friction angle is
    taken to be equal to the normally consolidated peak value.  As
    printed (Figure 8-13 plots PI from 0 to 100)::

        phi'FS = 0.0058 * PI^1.73 - 0.32 * PI + 36.2

    .. math::
        \\phi'_{FS} = 0.0058 \\cdot PI^{1.73} - 0.32 \\cdot PI + 36.2

    Parameters
    ----------
    pi : float
        Plasticity index (%, dimensionless number, e.g., 30 for PI = 30%).

    Returns
    -------
    float
        Fully softened friction angle, phi'FS (degrees).

    Raises
    ------
    ValueError
        If *pi* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-13, p. 407.
    """
    if pi < 0.0:
        raise ValueError("pi must be non-negative.")
    return 0.0058 * pi ** 1.73 - 0.32 * pi + 36.2


def secant_friction_angle_shear_strength(
    sigma_ff_eff: float, phi_sec_deg: float
) -> float:
    """Effective stress shear strength using secant friction angle (Equation 8-14).

    Computes the shear strength on a nonlinear failure envelope using
    a stress-dependent secant friction angle.

    .. math::
        s = \\sigma'_{ff} \\cdot \\tan(\\phi'_{sec})

    Parameters
    ----------
    sigma_ff_eff : float
        Effective normal stress on the failure plane (stress units).
    phi_sec_deg : float
        Stress-dependent secant friction angle (degrees).

    Returns
    -------
    float
        Effective stress shear strength, s (same stress units as
        *sigma_ff_eff*).

    Raises
    ------
    ValueError
        If *sigma_ff_eff* is negative or *phi_sec_deg* is outside
        [0, 90).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-14, p. 411.
    """
    if sigma_ff_eff < 0.0:
        raise ValueError("sigma_ff_eff must be non-negative.")
    if phi_sec_deg < 0.0 or phi_sec_deg >= 90.0:
        raise ValueError("phi_sec_deg must be in [0, 90) degrees.")
    return sigma_ff_eff * math.tan(math.radians(phi_sec_deg))


def power_function_shear_strength(
    a: float, sigma_ff_eff: float, pa: float, b: float
) -> float:
    """Nonlinear shear strength using two-parameter power function (Equation 8-15).

    Describes shear strength nonlinearly using empirical parameters *a*
    (steepness) and *b* (curvature).  Commonly used for fully softened
    and residual shear strengths.

    .. math::
        s = a \\cdot P_a \\left(\\frac{\\sigma'_{ff}}{P_a}\\right)^b

    Parameters
    ----------
    a : float
        Empirical coefficient related to steepness (dimensionless).
    sigma_ff_eff : float
        Effective normal stress on the failure plane (stress units).
    pa : float
        Atmospheric pressure (same stress units as *sigma_ff_eff*).
    b : float
        Empirical coefficient related to curvature (dimensionless).

    Returns
    -------
    float
        Effective stress shear strength, s (same stress units as
        *sigma_ff_eff*).

    Raises
    ------
    ValueError
        If *sigma_ff_eff* is negative or *pa* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-15, p. 411.
    """
    if sigma_ff_eff < 0.0:
        raise ValueError("sigma_ff_eff must be non-negative.")
    if pa <= 0.0:
        raise ValueError("pa must be positive.")
    return a * pa * (sigma_ff_eff / pa) ** b


def residual_friction_angle_gibson(pi: float) -> float:
    """Residual friction angle from plasticity index (Equation 8-16).

    Gibson (1953) relationship for the residual friction angle (phi'r),
    approximated by Carter and Bentley (2016).  The polynomial fit agrees
    with the original curve to within 5%.

    .. math::
        \\phi'_r = 0.084 \\cdot PI^{1.4} - 0.75 \\cdot PI + 31.9

    Parameters
    ----------
    pi : float
        Plasticity index (%).

    Returns
    -------
    float
        Residual friction angle, phi'r (degrees).

    Raises
    ------
    ValueError
        If *pi* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-16, p. 413.
    """
    if pi < 0.0:
        raise ValueError("pi must be non-negative.")
    return 0.084 * pi ** 1.4 - 0.75 * pi + 31.9


def residual_friction_angle_stark_hussain(
    ll: float, c0: float, c1: float, c2: float, c3: float
) -> float:
    """Residual friction angle from liquid limit using Stark and Hussain (Equation 8-17).

    Stark and Hussain (2013) correlation providing stress-dependent
    residual secant friction angles.  The coefficients C0 through C3
    depend on the clay fraction, liquid limit range, and effective
    normal stress; they are tabulated in Table 8-6 of the UFC.

    .. math::
        \\phi'_r = C_0 + C_1 \\cdot LL + C_2 \\cdot LL^2 + C_3 \\cdot LL^3

    Parameters
    ----------
    ll : float
        Liquid limit (%).
    c0 : float
        Empirical intercept coefficient (degrees).
    c1 : float
        Empirical first-order coefficient (degrees / %).
    c2 : float
        Empirical second-order coefficient (degrees / %^2).
    c3 : float
        Empirical third-order coefficient (degrees / %^3).

    Returns
    -------
    float
        Residual friction angle, phi'r (degrees).

    Raises
    ------
    ValueError
        If *ll* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-17, Table 8-6, p. 417.
    """
    if ll < 0.0:
        raise ValueError("ll must be non-negative.")
    return c0 + c1 * ll + c2 * ll ** 2 + c3 * ll ** 3


# ============================================================================
# SECTION 8-3: UNDRAINED SHEAR STRENGTH
# ============================================================================


def undrained_strength_ratio_skempton(pi: float) -> float:
    """Undrained shear strength ratio from plasticity index (Equation 8-18).

    Skempton (1957) correlation for the undrained shear strength ratio
    (su/sigma'v) of normally consolidated clays based on the plasticity
    index.  Based primarily on field vane tests (possibly uncorrected).

    .. math::
        \\frac{s_u}{\\sigma'_v} = 0.11 + 0.0037 \\cdot PI

    Parameters
    ----------
    pi : float
        Plasticity index (%).

    Returns
    -------
    float
        Undrained shear strength ratio, su/sigma'v (dimensionless).

    Raises
    ------
    ValueError
        If *pi* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-18, p. 419.
    """
    if pi < 0.0:
        raise ValueError("pi must be non-negative.")
    return 0.11 + 0.0037 * pi


def undrained_strength_ratio_hansbo(ll: float) -> float:
    """Undrained shear strength ratio from liquid limit (Equation 8-19).

    Hansbo (1957) correlation for the undrained shear strength ratio
    (su/sigma'v) of normally consolidated clays using the liquid limit.
    Supported by data from Scandinavian clays collected by Larson (1980).

    .. math::
        \\left(\\frac{s_u}{\\sigma'_v}\\right)_{NC} = 0.0045 \\cdot LL

    Parameters
    ----------
    ll : float
        Liquid limit (%).

    Returns
    -------
    float
        Undrained shear strength ratio for NC clay, su/sigma'v
        (dimensionless).

    Raises
    ------
    ValueError
        If *ll* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-19, p. 420.
    """
    if ll < 0.0:
        raise ValueError("ll must be non-negative.")
    return 0.0045 * ll


def undrained_strength_ratio_oc(
    su_sigma_v_nc: float, ocr: float, m: float
) -> float:
    """Undrained shear strength ratio for OC clays (Equation 8-20).

    Jamiolkowski et al. (1985) and Ladd and DeGroot (2004) relationship
    accounting for the effect of stress history on the undrained shear
    strength ratio.  The normally consolidated ratio is scaled by OCR
    raised to the power *m*.

    .. math::
        \\left(\\frac{s_u}{\\sigma'_v}\\right)_{OC} =
        \\left(\\frac{s_u}{\\sigma'_v}\\right)_{NC} \\cdot OCR^m

    Parameters
    ----------
    su_sigma_v_nc : float
        Undrained shear strength ratio for normally consolidated clay,
        (su/sigma'v)_NC (dimensionless).
    ocr : float
        Overconsolidation ratio (dimensionless, >= 1.0).
    m : float
        Semi-empirical fitting parameter (dimensionless).  Typical value
        is approximately 0.8 based on DSS tests; see Table 8-9 for other
        values.

    Returns
    -------
    float
        Undrained shear strength ratio for OC clay, (su/sigma'v)_OC
        (dimensionless).

    Raises
    ------
    ValueError
        If *su_sigma_v_nc* is negative or *ocr* is less than 1.0.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-20, p. 424.
    """
    if su_sigma_v_nc < 0.0:
        raise ValueError("su_sigma_v_nc must be non-negative.")
    if ocr < 1.0:
        raise ValueError("ocr must be >= 1.0.")
    return su_sigma_v_nc * ocr ** m


def undrained_strength_from_preconsolidation(sigma_p_eff: float) -> float:
    """Undrained shear strength from preconsolidation pressure (Equation 8-21).

    Sabatini et al. (2002) approximation for very soft clays with
    overconsolidation ratios less than 2.  Assumes *m* equals 1 in the
    SHANSEP framework (Equation 8-20).

    .. math::
        s_u \\approx 0.21 \\cdot \\sigma'_p

    Parameters
    ----------
    sigma_p_eff : float
        Preconsolidation pressure (stress units, e.g., kPa, psf).

    Returns
    -------
    float
        Undrained shear strength, su (same stress units as
        *sigma_p_eff*).

    Raises
    ------
    ValueError
        If *sigma_p_eff* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-21, p. 425.
    """
    if sigma_p_eff < 0.0:
        raise ValueError("sigma_p_eff must be non-negative.")
    return 0.21 * sigma_p_eff


def undrained_strength_ratio_acu_from_icu(su_sigma_v_icu: float) -> float:
    """CK0U strength ratio from ICU strength ratio (Equation 8-22).

    Kulhawy and Mayne (1990) relationship to convert the normally
    consolidated undrained strength ratio from isotropically consolidated
    undrained (ICU) triaxial compression tests to anisotropically (K0)
    consolidated undrained (CK0U, or ACU) triaxial compression tests.

    .. math::
        \\left(\\frac{s_u}{\\sigma'_v}\\right)_{ACU} =
        0.15 + 0.49 \\left(\\frac{s_u}{\\sigma'_v}\\right)_{ICU}

    Parameters
    ----------
    su_sigma_v_icu : float
        Undrained strength ratio from ICU triaxial compression tests
        (dimensionless).

    Returns
    -------
    float
        Undrained strength ratio from CK0U triaxial compression tests,
        (su/sigma'v)_ACU (dimensionless).

    Raises
    ------
    ValueError
        If *su_sigma_v_icu* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-22, p. 426.
    """
    if su_sigma_v_icu < 0.0:
        raise ValueError("su_sigma_v_icu must be non-negative.")
    return 0.15 + 0.49 * su_sigma_v_icu


def cpt_undrained_strength_nc(qc: float, nc: float) -> float:
    """Undrained shear strength from CPT using Nc method (Equation 8-23).

    Simplest CPT-based method relating the cone tip resistance directly
    to undrained shear strength through an empirical bearing capacity
    factor.  May be less accurate at depths > 15 m because overburden
    pressure is not considered.

    .. math::
        s_u = \\frac{q_c}{N_c}

    Parameters
    ----------
    qc : float
        Cone tip resistance (stress units, e.g., kPa, tsf).
    nc : float
        Empirical bearing capacity factor (dimensionless).  Typically
        17 to 23 for NC and slightly OC clays.

    Returns
    -------
    float
        Undrained shear strength, su (same stress units as *qc*).

    Raises
    ------
    ValueError
        If *qc* is negative or *nc* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-23, p. 426.
    """
    if qc < 0.0:
        raise ValueError("qc must be non-negative.")
    if nc <= 0.0:
        raise ValueError("nc must be positive.")
    return qc / nc


def cpt_undrained_strength_nk(
    qc: float, sigma_v: float, nk: float
) -> float:
    """Undrained shear strength from CPT using Nk method (Equation 8-24).

    Considers the total overburden pressure at the measurement depth.
    The empirical bearing capacity factor Nk should be calibrated on
    a site- or region-specific basis.

    .. math::
        s_u = \\frac{q_c - \\sigma_v}{N_k}

    Parameters
    ----------
    qc : float
        Cone tip resistance (stress units).
    sigma_v : float
        Total vertical stress at the depth of measurement (same stress
        units as *qc*).
    nk : float
        Empirical bearing capacity factor (dimensionless).  Typical
        range 10 to 19, average about 15.

    Returns
    -------
    float
        Undrained shear strength, su (same stress units as *qc*).

    Raises
    ------
    ValueError
        If *nk* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-24, p. 427.
    """
    if nk <= 0.0:
        raise ValueError("nk must be positive.")
    return (qc - sigma_v) / nk


def cpt_undrained_strength_nkt(
    qt: float, sigma_v: float, nkt: float
) -> float:
    """Undrained shear strength from CPT using Nkt method (Equation 8-25).

    Modification of the Nk method that uses the corrected tip resistance
    (qt) which accounts for pore pressure acting at the cone tip.
    Values of Nkt are often in the range of 14 to 16.

    .. math::
        s_u = \\frac{q_t - \\sigma_v}{N_{kt}}

    Parameters
    ----------
    qt : float
        Corrected cone tip resistance, qt = qc + u*(1+a) (stress units).
    sigma_v : float
        Total vertical stress at the depth of measurement (same stress
        units as *qt*).
    nkt : float
        Empirical bearing capacity factor (dimensionless).  Typical
        range 14 to 16.

    Returns
    -------
    float
        Undrained shear strength, su (same stress units as *qt*).

    Raises
    ------
    ValueError
        If *nkt* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-25, p. 427.
    """
    if nkt <= 0.0:
        raise ValueError("nkt must be positive.")
    return (qt - sigma_v) / nkt


def spt_undrained_strength_stroud_butler(n: float, pi: float) -> float:
    """Undrained shear strength su (kPa) of overconsolidated clay from SPT N and PI, Equation 8-26.

    Carter and Bentley (2016) approximation of the Stroud and Butler
    (1975) trendline (Figure 8-31) relating undrained shear strength of
    overconsolidated clays to SPT N and plasticity index.  The
    relationship exhibits significant scatter.  As printed, with su in
    kPa::

        su / N = 8910 / PI^3 + 4.36

    .. math::
        \\frac{s_u}{N} = \\frac{8910}{PI^3} + 4.36

    Parameters
    ----------
    n : float
        SPT N value (blows/ft).
    pi : float
        Plasticity index (%).  Must be > 0.

    Returns
    -------
    float
        Undrained shear strength, su (kPa).

    Raises
    ------
    ValueError
        If *n* is negative or *pi* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-26, p. 428.
    """
    if n < 0.0:
        raise ValueError("n must be non-negative.")
    if pi <= 0.0:
        raise ValueError("pi must be positive.")
    return n * (8910.0 / pi ** 3 + 4.36)


# ============================================================================
# SECTION 8-4: CONSOLIDATION PARAMETERS
# ============================================================================


def intrinsic_compression_index(e_star_100: float, e_star_1000: float) -> float:
    """Intrinsic compression index from void ratios (Equation 8-27).

    Burland (1990) definition of the intrinsic compression index based
    on the void ratios at 100 and 1000 kPa for reconstituted clays.

    .. math::
        C^*_c = e^*_{100} - e^*_{1000}

    Parameters
    ----------
    e_star_100 : float
        Intrinsic void ratio at 100 kPa (dimensionless).
    e_star_1000 : float
        Intrinsic void ratio at 1000 kPa (dimensionless).

    Returns
    -------
    float
        Intrinsic compression index, C*c (dimensionless).

    Raises
    ------
    ValueError
        If *e_star_100* <= *e_star_1000* (result would be non-positive).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-27, p. 439.
    """
    result = e_star_100 - e_star_1000
    if result <= 0.0:
        raise ValueError(
            "e_star_100 must be greater than e_star_1000 for a positive "
            "compression index."
        )
    return result


def void_index(e: float, e_star_100: float, c_star_c: float) -> float:
    """Void index from void ratio (Equation 8-28).

    Burland (1990) normalization of the current void ratio with respect
    to the intrinsic void ratio at 100 kPa and the intrinsic compression
    index.

    .. math::
        I_v = \\frac{e - e^*_{100}}{C^*_c}

    Parameters
    ----------
    e : float
        Current void ratio (dimensionless).
    e_star_100 : float
        Intrinsic void ratio at 100 kPa (dimensionless).
    c_star_c : float
        Intrinsic compression index (dimensionless).  Must be > 0.

    Returns
    -------
    float
        Void index, Iv (dimensionless).

    Raises
    ------
    ValueError
        If *c_star_c* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-28, p. 439.
    """
    if c_star_c <= 0.0:
        raise ValueError("c_star_c must be positive.")
    return (e - e_star_100) / c_star_c


def intrinsic_void_ratio_at_100kpa(e_l: float) -> float:
    """Intrinsic void ratio at 100 kPa from void ratio at liquid limit (Equation 8-29).

    Burland (1990) correlation to estimate the intrinsic void ratio at
    100 kPa from the void ratio at the liquid limit (eL).

    .. math::
        e^*_{100} = 0.109 + 0.679 \\cdot e_L - 0.089 \\cdot e_L^2
                    + 0.016 \\cdot e_L^3

    Parameters
    ----------
    e_l : float
        Void ratio at water content equal to the liquid limit
        (dimensionless).

    Returns
    -------
    float
        Intrinsic void ratio at 100 kPa, e*100 (dimensionless).

    Raises
    ------
    ValueError
        If *e_l* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-29, p. 439.
    """
    if e_l < 0.0:
        raise ValueError("e_l must be non-negative.")
    return 0.109 + 0.679 * e_l - 0.089 * e_l ** 2 + 0.016 * e_l ** 3


def intrinsic_compression_index_from_el(e_l: float) -> float:
    """Intrinsic compression index from void ratio at liquid limit (Equation 8-30).

    Burland (1990) correlation to estimate the intrinsic compression
    index from the void ratio at the liquid limit (eL).

    .. math::
        C^*_c = 0.256 \\cdot e_L - 0.04

    Parameters
    ----------
    e_l : float
        Void ratio at water content equal to the liquid limit
        (dimensionless).

    Returns
    -------
    float
        Intrinsic compression index, C*c (dimensionless).

    Raises
    ------
    ValueError
        If *e_l* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-30, p. 439.
    """
    if e_l < 0.0:
        raise ValueError("e_l must be non-negative.")
    return 0.256 * e_l - 0.04


# ============================================================================
# SECTION 8-4.3: CONSTRAINED MODULUS
# ============================================================================


def constrained_modulus_linear(m: float, sigma_v_eff: float) -> float:
    """Constrained modulus -- linear form (Equation 8-31).

    Janbu (1963) linear relationship between the secant drained
    constrained modulus and the vertical effective stress for normally
    consolidated clays, silts, and sands.

    .. math::
        M_{ds} = m \\cdot \\sigma'_v

    Parameters
    ----------
    m : float
        Modulus number (dimensionless).
    sigma_v_eff : float
        Vertical effective stress (stress units, e.g., kPa).

    Returns
    -------
    float
        Constrained modulus, Mds (same stress units as *sigma_v_eff*).

    Raises
    ------
    ValueError
        If *m* is negative or *sigma_v_eff* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-31, p. 442.
    """
    if m < 0.0:
        raise ValueError("m must be non-negative.")
    if sigma_v_eff < 0.0:
        raise ValueError("sigma_v_eff must be non-negative.")
    return m * sigma_v_eff


def constrained_modulus_nonlinear(
    m: float, sigma_v_eff: float, pa: float
) -> float:
    """Constrained modulus -- nonlinear form (Equation 8-32).

    Janbu (1963) nonlinear (square-root) relationship between the
    secant drained constrained modulus and the vertical effective stress
    for normally consolidated clays, silts, and sands.

    .. math::
        M_{ds} = m \\cdot P_a \\cdot
        \\left(\\frac{\\sigma'_v}{P_a}\\right)^{0.5}

    Parameters
    ----------
    m : float
        Modulus number (dimensionless).
    sigma_v_eff : float
        Vertical effective stress (stress units).
    pa : float
        Atmospheric pressure (same stress units as *sigma_v_eff*).

    Returns
    -------
    float
        Constrained modulus, Mds (same stress units as *sigma_v_eff*).

    Raises
    ------
    ValueError
        If *m* is negative, *sigma_v_eff* is negative, or *pa* is not
        positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-32, p. 442.
    """
    if m < 0.0:
        raise ValueError("m must be non-negative.")
    if sigma_v_eff < 0.0:
        raise ValueError("sigma_v_eff must be non-negative.")
    if pa <= 0.0:
        raise ValueError("pa must be positive.")
    return m * pa * (sigma_v_eff / pa) ** 0.5


def constrained_modulus_spt(f: float, n: float, pa: float) -> float:
    """Constrained modulus from SPT using Stroud (Equation 8-33).

    Stroud (1974) correlation for the constrained modulus of clays from
    SPT N value.  The empirical coefficient *f* depends on the plasticity
    index (see Figure 8-46 of the UFC).  According to Kulhawy and Mayne
    (1990), this correlation is not very reliable.

    .. math::
        M_{ds} = f \\cdot N \\cdot P_a

    Parameters
    ----------
    f : float
        Empirical coefficient related to plasticity index (dimensionless,
        from Figure 8-46).
    n : float
        SPT blow count (blows/ft).
    pa : float
        Atmospheric pressure (stress units, e.g., kPa).

    Returns
    -------
    float
        Constrained modulus, Mds (same stress units as *pa*).

    Raises
    ------
    ValueError
        If *f* is negative, *n* is negative, or *pa* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-33, p. 442.
    """
    if f < 0.0:
        raise ValueError("f must be non-negative.")
    if n < 0.0:
        raise ValueError("n must be non-negative.")
    if pa <= 0.0:
        raise ValueError("pa must be positive.")
    return f * n * pa


def constrained_modulus_cpt(alpha: float, qc: float) -> float:
    """Constrained modulus from CPT tip resistance (Equation 8-34).

    General correlation relating the constrained modulus to the CPT tip
    resistance via an empirical coefficient alpha, as compiled by
    Mitchell and Gardner (1975).  Alpha can range from 0.4 to 8, but is
    most commonly between 1 and 3.

    .. math::
        M_{ds} = \\alpha \\cdot q_c

    Parameters
    ----------
    alpha : float
        Empirical coefficient (dimensionless).  Typically 1 to 3.
    qc : float
        Cone tip resistance (stress units).

    Returns
    -------
    float
        Constrained modulus, Mds (same stress units as *qc*).

    Raises
    ------
    ValueError
        If *alpha* is negative or *qc* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-34, p. 445.
    """
    if alpha < 0.0:
        raise ValueError("alpha must be non-negative.")
    if qc < 0.0:
        raise ValueError("qc must be non-negative.")
    return alpha * qc


# ============================================================================
# SECTION 8-4.4: COEFFICIENT OF SECONDARY COMPRESSION
# ============================================================================


def secondary_compression_ratio(wn: float) -> float:
    """Modified secondary compression index from natural water content (Equation 8-35).

    Mesri (1973) correlation to estimate the modified coefficient of
    secondary compression (Cepsilon-alpha) for normally consolidated
    clays based on the natural water content.

    .. math::
        C_{\\varepsilon\\alpha} = 0.0001 \\cdot w_n

    Parameters
    ----------
    wn : float
        Natural water content (%, e.g., 40 for w = 40%).

    Returns
    -------
    float
        Modified secondary compression ratio, C_epsilon_alpha
        (dimensionless strain / log cycle of time).

    Raises
    ------
    ValueError
        If *wn* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-35, p. 446.
    """
    if wn < 0.0:
        raise ValueError("wn must be non-negative.")
    return 0.0001 * wn


# ============================================================================
# SECTION 8-5: ELASTIC MODULUS
# ============================================================================


def drained_youngs_modulus_from_undrained(
    eu: float, nu: float
) -> float:
    """Drained Young's modulus from undrained Young's modulus (Equation 8-36).

    Converts the undrained Young's modulus (obtained from field testing
    of fine-grained soils) to the drained Young's modulus using the
    drained Poisson's ratio.  Assumes an undrained Poisson's ratio of
    0.5.

    .. math::
        E = \\frac{2(1+\\nu)}{3} \\cdot E_u

    Parameters
    ----------
    eu : float
        Young's modulus for undrained conditions (stress units, e.g.,
        kPa, MPa).
    nu : float
        Poisson's ratio for drained conditions (dimensionless).
        Must be in the range (-1, 0.5).

    Returns
    -------
    float
        Young's modulus for drained conditions, E (same stress units
        as *eu*).

    Raises
    ------
    ValueError
        If *eu* is negative or *nu* is outside (-1, 0.5).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-36, p. 449.
    """
    if eu < 0.0:
        raise ValueError("eu must be non-negative.")
    if nu <= -1.0 or nu >= 0.5:
        raise ValueError("nu must be in the range (-1, 0.5).")
    return 2.0 * (1.0 + nu) / 3.0 * eu


# ============================================================================
# SECTION 8-6: CALIFORNIA BEARING RATIO (CBR)
# ============================================================================


def cbr_from_dcp_power(a_coeff: float, dcp: float, x: float) -> float:
    """CBR from dynamic cone penetration index -- power form (Equation 8-37).

    General power-law correlation used by many researchers to estimate
    the California Bearing Ratio from DCP index.  Values of *a_coeff*
    and *x* from various sources are tabulated in Table 8-24.

    .. math::
        CBR = A \\cdot DCP^x

    Parameters
    ----------
    a_coeff : float
        Empirical coefficient, A (dimensionless).
    dcp : float
        Dynamic cone penetration index (mm/blow).  Must be > 0.
    x : float
        Empirical exponent (dimensionless, typically negative).

    Returns
    -------
    float
        California Bearing Ratio, CBR (%).

    Raises
    ------
    ValueError
        If *a_coeff* is negative or *dcp* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-37, Table 8-24, p. 456.
    """
    if a_coeff < 0.0:
        raise ValueError("a_coeff must be non-negative.")
    if dcp <= 0.0:
        raise ValueError("dcp must be positive.")
    return a_coeff * dcp ** x


def cbr_from_dcp_nazzal(dcp: float) -> float:
    """California Bearing Ratio CBR (%) from the DCP index in mm/blow, Equation 8-38 (Nazzal 2003).

    Nazzal (2003) correlation for soils with DCP values between 6.3
    and 67 mm/blow.  As printed::

        CBR = 2559 / (DCP^1.84 - 7.35) + 1

    .. math::
        CBR = \\frac{2559}{DCP^{1.84} - 7.35} + 1

    Parameters
    ----------
    dcp : float
        Dynamic cone penetration index (mm/blow), between 6.3 and
        67 mm/blow, the range the manual gives for this correlation.

    Returns
    -------
    float
        California Bearing Ratio, CBR (%).

    Raises
    ------
    ValueError
        If *dcp* is not positive, or is outside 6.3 to 67 mm/blow (the
        denominator DCP^1.84 - 7.35 passes through zero near 3 mm/blow,
        so the equation has no meaning below its stated range).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-38, p. 456.
    """
    if dcp <= 0.0:
        raise ValueError("dcp must be positive.")
    if dcp < 6.3 or dcp > 67.0:
        raise ValueError(
            "dcp is outside 6.3 to 67 mm/blow, the range UFS 3-220-10 "
            "p. 456 gives for Equation 8-38 (Nazzal 2003)."
        )
    return 2559.0 / (dcp ** 1.84 - 7.35) + 1.0


def cbr_from_spt(n: float) -> float:
    """California Bearing Ratio CBR (%) from the SPT blow count N, Equation 8-39 (Livneh 1989).

    Livneh (1989) correlation to estimate the California Bearing Ratio
    from SPT blow count.  As printed (the exponent -0.26 is on the
    logarithm)::

        log10(CBR) = -5.13 + 6.55 * [log10(300 / N)]^(-0.26)

    .. math::
        \\log CBR = -5.13 + 6.55
        \\left(\\log\\frac{300}{N}\\right)^{-0.26}

    Figure 8-57 (p. 458) plots this curve with the data behind it for N
    from about 5 to about 68.

    Parameters
    ----------
    n : float
        SPT blow count (blows/ft).  Use N60 for modern hammers.
        Must be > 0 and < 300.

    Returns
    -------
    float
        California Bearing Ratio, CBR (%).

    Raises
    ------
    ValueError
        If *n* is not positive, or is 300 or more (log(300/N) is then
        not positive and the equation cannot be evaluated).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-39, p. 457; Figure 8-57, p. 458.
    """
    if n <= 0.0:
        raise ValueError("n must be positive.")
    if n >= 300.0:
        raise ValueError(
            "n must be less than 300: Equation 8-39 (UFS 3-220-10 p. 457) "
            "raises log(300/N) to the power -0.26."
        )
    log_cbr = -5.13 + 6.55 * math.log10(300.0 / n) ** -0.26
    return 10.0 ** log_cbr


# ============================================================================
# SECTION 8-7: HYDRAULIC CONDUCTIVITY
# ============================================================================


def hydraulic_conductivity_hazen(d10: float, c: float = 1.0) -> float:
    """Hydraulic conductivity from Hazen equation (Equation 8-40).

    Hazen (1911) correlation for saturated clean sands with fines
    content less than 5% and D10 values from 0.1 to 3 mm.

    .. math::
        k = C \\cdot D_{10}^2

    Parameters
    ----------
    d10 : float
        Grain size corresponding to 10% passing (mm).  Valid range
        is 0.1 to 3 mm.
    c : float, optional
        Empirical coefficient, usually taken to be 1.0 (cm/s/mm^2).
        Default is 1.0.

    Returns
    -------
    float
        Hydraulic conductivity, k (cm/s).

    Raises
    ------
    ValueError
        If *d10* is not positive or *c* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-40, p. 458.
    """
    if d10 <= 0.0:
        raise ValueError("d10 must be positive.")
    if c <= 0.0:
        raise ValueError("c must be positive.")
    return c * d10 ** 2


def hydraulic_conductivity_kozeny_carman(
    fractions: List[Tuple[float, float, float]],
    e: float,
    s: float = 6.0,
) -> float:
    """Hydraulic conductivity k (cm/s) of coarse-grained soil from its grain-size distribution, Equation 8-41 (Kozeny-Carman, Carrier 2003).

    Carrier (2003) modified version of the Kozeny-Carman equation
    (Kozeny 1927; Carman 1938, 1956) using the full grain-size
    distribution.  As printed, with particle sizes in mm and k in cm/s::

        k = 1.99e2 [cm/(s mm^2)]
            * [ 100% / sum( fi / (D_li^0.404 * D_si^0.596) ) ]^2
            * (1 / S^2) * (e^3 / (1 + e))

    .. math::
        k = 1.99 \\times 10^{2}
        \\left[\\frac{100\\%}{\\sum \\dfrac{f_i}
        {D_{li}^{0.404} \\times D_{si}^{0.596}}}\\right]^2
        \\left(\\frac{1}{S^2}\\right)
        \\left(\\frac{e^3}{1+e}\\right)

    Parameters
    ----------
    fractions : list of (fi, d_li, d_si) tuples
        One (fi, d_li, d_si) tuple per pair of adjacent sieves: fi =
        fraction of particles (by mass) between the two sieves, d_li =
        particle size of the coarser sieve (mm), d_si = particle size of
        the finer sieve (mm).  The fi are either decimals that add up to
        1.0 (0.15 for 15%) or percentages that add up to 100; the whole
        grain-size distribution must be given.
    e : float
        Void ratio (dimensionless).
    s : float, optional
        Surface area factor S (dimensionless), ranging from 6 for
        spheres to 8.5 for angular particles.  Default is 6.0 (spheres),
        which gives the highest k of that range.

    Returns
    -------
    float
        Hydraulic conductivity, k (cm/s).

    Raises
    ------
    ValueError
        If *e* is negative, *s* is not positive, any sieve size is
        not positive, or the fractions add up to neither 1.0 nor 100.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-41, p. 462.
    """
    if e < 0.0:
        raise ValueError("e must be non-negative.")
    if s <= 0.0:
        raise ValueError("s must be positive.")

    summation = 0.0
    total = 0.0
    for fi, d_li, d_si in fractions:
        if d_li <= 0.0 or d_si <= 0.0:
            raise ValueError(
                "All sieve sizes (d_li, d_si) must be positive."
            )
        summation += fi / (d_li ** 0.404 * d_si ** 0.596)
        total += fi

    if summation <= 0.0:
        raise ValueError(
            "Sum of fi/(d_li^0.404 * d_si^0.596) is zero; check input "
            "fractions."
        )
    if abs(total - 1.0) <= 0.005:
        hundred_percent = 1.0
    elif abs(total - 100.0) <= 0.5:
        hundred_percent = 100.0
    else:
        raise ValueError(
            f"The fractions add up to {total:g}; they must add up to 1.0 "
            "(decimals) or 100 (percent). Equation 8-41 (UFS 3-220-10 "
            "p. 462) divides 100% by the sum over the whole grain-size "
            "distribution."
        )

    k = (
        1.99e2
        * (hundred_percent / summation) ** 2
        * (1.0 / s ** 2)
        * (e ** 3 / (1.0 + e))
    )
    return k


def hydraulic_conductivity_carrier_beckman(
    e: float, pl: float, pi: float
) -> float:
    """Hydraulic conductivity k (m/s) of fine-grained soil from void ratio and Atterberg limits, Equation 8-42 (Carrier and Beckman 1984).

    Carrier and Beckman (1984) correlation relating the hydraulic
    conductivity of fine-grained soils to the void ratio, plastic limit,
    and plasticity index.  As printed (the plasticity index divides
    inside the bracket that is raised to 4.29)::

        k = 0.0174 * { [e - 0.027 (PL - 0.242 PI)] / PI }^4.29 * 1 / (1 + e)

    .. math::
        k = 0.0174 \\left[
        \\frac{e - 0.027 (PL - 0.242 PI)}{PI} \\right]^{4.29}
        \\left(\\frac{1}{1+e}\\right)

    Parameters
    ----------
    e : float
        Void ratio (dimensionless).
    pl : float
        Plastic limit (%).
    pi : float
        Plasticity index (%).  Must be > 0.

    Returns
    -------
    float
        Hydraulic conductivity, k (m/s).

    Raises
    ------
    ValueError
        If *e* is negative, *pi* is not positive, or
        e - 0.027 (PL - 0.242 PI) is not positive (the void ratio is
        then too low for the equation to be evaluated).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-42, p. 462.
    """
    if e < 0.0:
        raise ValueError("e must be non-negative.")
    if pi <= 0.0:
        raise ValueError("pi must be positive.")
    numerator = e - 0.027 * (pl - 0.242 * pi)
    if numerator <= 0.0:
        raise ValueError(
            "e - 0.027 (PL - 0.242 PI) is not positive; Equation 8-42 "
            "(UFS 3-220-10 p. 462) raises it to the power 4.29 and cannot "
            "be evaluated at this void ratio."
        )
    return 0.0174 * (numerator / pi) ** 4.29 / (1.0 + e)


def hydraulic_conductivity_benson_landfill(
    cf: float,
    gc: float,
    w_compactor: float,
    pi: float,
    w: float,
    gamma_w: float,
    gamma_d: float,
    gs: float,
) -> float:
    """Hydraulic conductivity k (m/s) of a compacted clay liner, Equation 8-43 (Benson et al. 1994).

    Benson et al. (1994) measured the hydraulic conductivity of intact
    specimens from compacted clay liners at 67 landfills in North
    America and related it to other measured properties of the clays.
    As printed::

        ln k = -18.35 + 894 / W - 0.08 PI
               - 2.87 * [ w / (gamma_w / gamma_d - 1 / Gs) ]
               + 0.32 * sqrt(GC) + 0.02 CF

    .. math::
        \\ln k = -18.35 + \\frac{894}{W} - 0.08\\,PI
        - 2.87 \\left( \\frac{w}{\\gamma_w / \\gamma_d - 1 / G_s} \\right)
        + 0.32 \\sqrt{GC} + 0.02\\,CF

    The term in brackets is the degree of saturation at molding.  The
    manual gives no unit for the molding water content *w*; this
    function takes it as a decimal, which makes the bracket the degree
    of saturation as a decimal (a percentage there would give k below
    1e-100 m/s).

    Parameters
    ----------
    cf : float
        Clay-sized fraction CF (percent by mass smaller than 0.002 mm).
    gc : float
        Gravel content GC (percent retained between 75 mm and the No. 4
        sieve).
    w_compactor : float
        Weight of field compactor, W (kN).  Must be > 0.
    pi : float
        Plasticity index (%).
    w : float
        Molding water content as a decimal (0.20 for 20%).
    gamma_w : float
        Unit weight of water (kN/m^3, e.g., 9.81).
    gamma_d : float
        Dry unit weight (same units as *gamma_w*).
    gs : float
        Specific gravity of the solids (dimensionless).

    Returns
    -------
    float
        Hydraulic conductivity, k (m/s).

    Raises
    ------
    ValueError
        If *gamma_d*, *gamma_w*, *gs* or *w_compactor* is not positive,
        *gc* is negative, or gamma_w/gamma_d - 1/Gs is not positive
        (the dry unit weight is then above the zero-void-ratio value).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-43, p. 463.
    Benson et al. (1994).
    """
    if gamma_d <= 0.0:
        raise ValueError("gamma_d must be positive.")
    if gamma_w <= 0.0:
        raise ValueError("gamma_w must be positive.")
    if gs <= 0.0:
        raise ValueError("gs must be positive.")
    if w_compactor <= 0.0:
        raise ValueError("w_compactor must be positive.")
    if gc < 0.0:
        raise ValueError("gc must be non-negative.")

    denominator = gamma_w / gamma_d - 1.0 / gs
    if denominator <= 0.0:
        raise ValueError(
            "gamma_w/gamma_d - 1/gs is not positive (the void ratio is "
            "non-positive); check gamma_d, gamma_w, gs."
        )
    saturation = w / denominator

    ln_k = (-18.35 + 894.0 / w_compactor - 0.08 * pi - 2.87 * saturation
            + 0.32 * math.sqrt(gc) + 0.02 * cf)
    return math.exp(ln_k)


def hydraulic_conductivity_benson_trast(
    pi: float,
    cf: float,
    e_effort: float,
    w: float,
    gamma_w: float,
    gamma_d: float,
    gs: float,
) -> float:
    """Not evaluated: Equation 8-44 (Benson and Trast 1995), hydraulic conductivity k (m/s) of compacted clay. Always raises ValueError, because the manual does not give the unit of the molding water content.

    Benson and Trast (1995) tested 13 compacted clays used for
    compacted clay liners around the United States, prepared at
    different water contents.  As printed::

        ln k = -15 - 0.087 * [ w / (gamma_w / gamma_d - 1 / Gs) ]
               - 0.054 PI + 0.022 CF + 0.91 E

    .. math::
        \\ln k = -15
        - 0.087 \\left( \\frac{w}{\\gamma_w / \\gamma_d - 1 / G_s} \\right)
        - 0.054\\,PI + 0.022\\,CF + 0.91\\,E

    where E is the compactive effort index, equal to -1, 0 and 1 for
    modified, standard and reduced Proctor compactive effort.

    The term in brackets is the degree of saturation at molding.  The
    manual gives the molding water content *w* no unit, and here the
    two readings both give a possible k: with *w* as a decimal the term
    is about 0.6 to 1.0 and changes k by a few percent; with *w* in
    percent it is about 60 to 100 and lowers k by a factor of about 200
    to 5,000.  The page does not settle which is meant, so the function
    refuses rather than return either.

    Parameters
    ----------
    pi : float
        Plasticity index (%).
    cf : float
        Clay-sized fraction (%).
    e_effort : float
        Compactive effort index E: -1 for modified Proctor, 0 for
        standard Proctor, +1 for reduced Proctor.
    w : float
        Molding water content (unit not given by the manual).
    gamma_w : float
        Unit weight of water.
    gamma_d : float
        Dry unit weight (same units as *gamma_w*).
    gs : float
        Specific gravity of the solids (dimensionless).

    Raises
    ------
    ValueError
        Always.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-44, p. 463.
    Benson and Trast (1995).
    """
    raise ValueError(
        "Equation 8-44 (Benson and Trast 1995) is not evaluated: UFS "
        "3-220-10 p. 463 prints ln k = -15 - 0.087 [w/(gamma_w/gamma_d - "
        "1/Gs)] - 0.054 PI + 0.022 CF + 0.91 E (k in m/s) without the unit "
        "of the molding water content w, and k differs by a factor of "
        "about 200 to 5,000 (degree of saturation 60 to 100 %) between w "
        "as a decimal and w in percent."
    )


# ============================================================================
# SECTION 8-8: SHEAR WAVE VELOCITY
# ============================================================================


def shear_wave_velocity_spt(
    b: float, n: float, x: float, z: float = 1.0, y: float = 0.0
) -> float:
    """Shear wave velocity from SPT N value (Equation 8-45).

    General correlation form used by many researchers to estimate the
    shear wave velocity from SPT N values.  Specific coefficients are
    tabulated in Tables 8-26 and 8-27.

    .. math::
        V_s = B \\cdot N^x \\cdot z^y

    Parameters
    ----------
    b : float
        Empirical coefficient, B.
    n : float
        SPT blow count (blows/ft).  Use N60 for modern hammers.
    x : float
        Empirical exponent on N.
    z : float, optional
        Depth to the soil layer (m).  Default is 1.0 (no depth effect).
    y : float, optional
        Empirical exponent on depth (dimensionless).  Default is 0.0
        (no depth effect).

    Returns
    -------
    float
        Shear wave velocity, Vs (m/s).

    Raises
    ------
    ValueError
        If *b* is negative, *n* is negative, or *z* is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Equation 8-45, Tables 8-26 and 8-27, pp. 464-465.
    """
    if b < 0.0:
        raise ValueError("b must be non-negative.")
    if n < 0.0:
        raise ValueError("n must be non-negative.")
    if z <= 0.0:
        raise ValueError("z must be positive.")
    return b * n ** x * z ** y


# ===========================================================================
# TABLE 8-6: Stark & Hussain (2013) Coefficients
# ===========================================================================

_TABLE_8_6_STARK_HUSSAIN = {
    ("lt_20", "50_kpa"):  {"c0": 35.2, "c1": -0.1440, "c2": 0.000564, "c3": -0.00000116},
    ("lt_20", "100_kpa"): {"c0": 33.4, "c1": -0.1330, "c2": 0.000495, "c3": -0.00000092},
    ("lt_20", "400_kpa"): {"c0": 35.3, "c1": -0.1460, "c2": 0.000567, "c3": -0.00000115},
    ("20_to_50", "50_kpa"):  {"c0": 42.8, "c1": -0.2980, "c2": 0.001390, "c3": -0.00000251},
    ("20_to_50", "100_kpa"): {"c0": 38.5, "c1": -0.2220, "c2": 0.000880, "c3": -0.00000137},
    ("20_to_50", "400_kpa"): {"c0": 38.8, "c1": -0.2330, "c2": 0.001010, "c3": -0.00000168},
    ("gt_50", "50_kpa"):  {"c0": 53.5, "c1": -0.6100, "c2": 0.004060, "c3": -0.00000925},
    ("gt_50", "100_kpa"): {"c0": 49.2, "c1": -0.4820, "c2": 0.002870, "c3": -0.00000600},
    ("gt_50", "400_kpa"): {"c0": 44.1, "c1": -0.3400, "c2": 0.001780, "c3": -0.00000345},
}


def table_8_6_stark_hussain(cf_range: str, sigma_n_range: str) -> dict:
    """Stark & Hussain (2013) polynomial coefficients for residual
    friction angle (Table 8-6).

    Returns the four coefficients (C0, C1, C2, C3) for use with
    ``residual_friction_angle_stark_hussain`` (Equation 8-17).

    Parameters
    ----------
    cf_range : str
        Clay fraction range: ``"lt_20"`` (< 20 %), ``"20_to_50"``
        (20-50 %), or ``"gt_50"`` (> 50 %).
    sigma_n_range : str
        Effective normal stress level: ``"50_kPa"``, ``"100_kPa"``,
        or ``"400_kPa"``.

    Returns
    -------
    dict
        ``{"c0": float, "c1": float, "c2": float, "c3": float}``.

    Raises
    ------
    ValueError
        If the combination is not recognised.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Table 8-6, p. 417.
    Stark & Hussain (2013).
    """
    key = (cf_range.lower().strip(), sigma_n_range.lower().strip())
    if key not in _TABLE_8_6_STARK_HUSSAIN:
        raise ValueError(
            f"Unknown combination cf_range='{cf_range}', "
            f"sigma_n_range='{sigma_n_range}'."
        )
    return dict(_TABLE_8_6_STARK_HUSSAIN[key])


# ===========================================================================
# TABLE 8-9: SHANSEP Exponent m
# ===========================================================================

_TABLE_8_9_SHANSEP_M = {
    "ciuc": 0.85,
    "ck0uc": 0.80,
    "dss": 0.80,
    "ck0ue": 0.70,
    "field_vane": 0.85,
}


def table_8_9_shansep_m(test_type: str) -> float:
    """SHANSEP exponent m for undrained strength ratio (Table 8-9).

    Returns the semi-empirical exponent *m* for use with
    ``undrained_strength_ratio_oc`` (Equation 8-20).

    Parameters
    ----------
    test_type : str
        One of ``"CIUC"``, ``"CK0UC"``, ``"DSS"``, ``"CK0UE"``,
        ``"field_vane"``.

    Returns
    -------
    float
        Exponent m (dimensionless).

    Raises
    ------
    ValueError
        If *test_type* is not recognised.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Table 8-9, p. 425.
    """
    key = test_type.lower().strip()
    if key not in _TABLE_8_9_SHANSEP_M:
        raise ValueError(
            f"Unknown test_type '{test_type}'. "
            f"Choose from: {list(_TABLE_8_9_SHANSEP_M.keys())}"
        )
    return _TABLE_8_9_SHANSEP_M[key]


# ===========================================================================
# TABLE 8-24: CBR-DCP Correlation Coefficients
# ===========================================================================

_TABLE_8_24_CBR_DCP = {
    # key: A, x, and the row's "Reference / Comment" as printed (p. 456)
    "gabr_2000": {
        "a": 25.0, "x": -0.55,
        "reference": "Gabr et al. (2000)"},
    "feleke_araya_2016_fine_a47": {
        "a": 47.0, "x": -0.90,
        "reference": "Feleke and Araya (2016), fine-grained soils"},
    "george_2009": {
        "a": 47.0, "x": -0.79,
        "reference": "George et al. (2009)"},
    "white_2018_cl_cbr_lt_10": {
        "a": 59.0, "x": -2.00,
        "reference": "White et al. (2018), CL with CBR < 10"},
    "feleke_araya_2016_coarse_a90": {
        "a": 90.0, "x": -1.17,
        "reference": "Feleke and Araya (2016), coarse-grained soils"},
    "feleke_araya_2016_fine_a104": {
        "a": 104.0, "x": -0.91,
        "reference": "Feleke and Araya (2016), fine-grained soils"},
    "feleke_araya_2016_coarse_a157": {
        "a": 157.0, "x": -0.85,
        "reference": "Feleke and Araya (2016), coarse-grained soils"},
    "george_kumar_2018": {
        "a": 246.0, "x": -1.35,
        "reference": "George and Kumar (2018)"},
    "white_2018_all_except_cl_cbr_lt_10": {
        "a": 292.0, "x": -1.12,
        "reference": "White et al. (2018), All soils except CL with CBR < 10"},
    "smith_pratt_1983": {
        "a": 363.0, "x": -1.15,
        "reference": "Smith and Pratt (1983)"},
    "harrison_1986_clay_dcp_lt_10": {
        "a": 501.0, "x": -1.12,
        "reference": "Harrison (1986), clay-like soils with DCP < 10 mm/blow"},
    "harrison_1986_clay_dcp_gt_10": {
        "a": 363.0, "x": -1.16,
        "reference": "Harrison (1986), clay-like soils with DCP > 10 mm/blow"},
    "kleyn_van_heerden_1983": {
        "a": 425.0, "x": -1.27,
        "reference": "Kleyn and Van Heerden (1983)"},
}


def table_8_24_cbr_dcp(source: str) -> dict:
    """Coefficient A and exponent x of CBR = A * DCP^x (DCP in mm/blow), Table 8-24 "CBR Correlations with DCP".

    Returns one row of Table 8-24 for use with ``cbr_from_dcp_power``
    (Equation 8-37): the empirical coefficient *a*, the exponent *x*
    (both dimensionless) and the row's reference as printed.  The table
    has thirteen rows; Feleke and Araya (2016) appear in four of them
    (two for fine-grained and two for coarse-grained soils, told apart
    here by their A value).

    Parameters
    ----------
    source : str
        Row of the table, one of:
        ``"gabr_2000"`` (A 25, x -0.55),
        ``"feleke_araya_2016_fine_a47"`` (47, -0.90),
        ``"george_2009"`` (47, -0.79),
        ``"white_2018_cl_cbr_lt_10"`` (59, -2.00),
        ``"feleke_araya_2016_coarse_a90"`` (90, -1.17),
        ``"feleke_araya_2016_fine_a104"`` (104, -0.91),
        ``"feleke_araya_2016_coarse_a157"`` (157, -0.85),
        ``"george_kumar_2018"`` (246, -1.35),
        ``"white_2018_all_except_cl_cbr_lt_10"`` (292, -1.12),
        ``"smith_pratt_1983"`` (363, -1.15),
        ``"harrison_1986_clay_dcp_lt_10"`` (501, -1.12),
        ``"harrison_1986_clay_dcp_gt_10"`` (363, -1.16),
        ``"kleyn_van_heerden_1983"`` (425, -1.27).

    Returns
    -------
    dict
        ``{"a": float, "x": float, "reference": str}``.

    Raises
    ------
    ValueError
        If *source* is not a row of the table.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Table 8-24, p. 456.
    """
    key = source.lower().strip()
    if key not in _TABLE_8_24_CBR_DCP:
        raise ValueError(
            f"Unknown source '{source}'. "
            f"Choose from: {list(_TABLE_8_24_CBR_DCP.keys())}"
        )
    return dict(_TABLE_8_24_CBR_DCP[key])


# ===========================================================================
# FIGURE 8-46: Stroud (1974) f-coefficient for Constrained Modulus
# ===========================================================================

# Digitised from Figure 8-46 (f vs PI)
_FIG_8_46_PI = [10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 80.0]
_FIG_8_46_F  = [500.0, 450.0, 400.0, 350.0, 300.0, 250.0, 225.0, 200.0, 175.0]


def figure_8_46_f(pi: float) -> float:
    """Stroud (1974) f-coefficient from plasticity index (Figure 8-46).

    Returns the empirical coefficient *f* for use with
    ``constrained_modulus_spt`` (Equation 8-30).

    Parameters
    ----------
    pi : float
        Plasticity index (%).  Typically 10 to 80.

    Returns
    -------
    float
        Coefficient f (dimensionless).

    Raises
    ------
    ValueError
        If *pi* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 8, Figure 8-46, p. 444.
    Stroud, M.A. (1974).
    """
    if pi < 0.0:
        raise ValueError("pi must be non-negative.")
    return _linterp(pi, _FIG_8_46_PI, _FIG_8_46_F)


def plot_figure_8_46(PI=None, ax=None, show=True, **kwargs):
    """Reproduce UFC Figure 8-46: Stroud f-coefficient vs Plasticity Index.

    Parameters
    ----------
    PI : float, optional
        Plasticity index query point.  If provided, highlights the
        interpolated f value.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on.
    show : bool, optional
        If True, calls plt.show().

    Returns
    -------
    matplotlib.axes.Axes
    """
    from geotech_references._plotting import get_pyplot, setup_engineering_plot
    plt = get_pyplot()
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))

    # Smooth interpolated curve
    pi_smooth = [i * 1.0 for i in range(5, 86)]
    f_smooth = [figure_8_46_f(p) for p in pi_smooth]
    ax.plot(pi_smooth, f_smooth, 'b-', linewidth=1.5, label='Stroud (1974)')

    # Digitised data points
    ax.plot(_FIG_8_46_PI, _FIG_8_46_F, 'ko', markersize=6,
            label='Digitised points')

    # Query point
    if PI is not None:
        f_q = figure_8_46_f(PI)
        ax.plot(PI, f_q, 's', color='red', markersize=10, zorder=5,
                label=f'PI={PI:.0f} → f={f_q:.0f}')
        ax.axhline(f_q, color='red', linestyle=':', alpha=0.4)
        ax.axvline(PI, color='red', linestyle=':', alpha=0.4)

    ax.legend(fontsize=8)
    setup_engineering_plot(
        ax, 'Figure 8-46: Stroud f-Coefficient',
        'Plasticity Index, PI (%)', 'f (dimensionless)')
    if show:
        plt.tight_layout()
        plt.show()
    return ax
