"""
UFS 3-220-10, Chapter 5: Analysis of Settlement and Volume Expansion

Equations 5-1 through 5-28 covering consolidation mechanics, settlement
calculations for coarse- and fine-grained soils, time rate of primary
consolidation, secondary compression, surcharge preconsolidation, and
vertical drain design.

Reference:
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 January 2026
"""

import math
from typing import List, Tuple

from geotech_references._interpolation import _linterp


# ---------------------------------------------------------------------------
# 5-1  Overconsolidation Ratio
# ---------------------------------------------------------------------------

def overconsolidation_ratio(sigma_p: float, sigma_z0: float) -> float:
    """Overconsolidation ratio (Equation 5-1).

    The overconsolidation ratio (OCR) is the ratio of the preconsolidation
    stress to the current vertical effective stress.  OCR = 1 indicates a
    normally consolidated soil; OCR > 1 indicates an overconsolidated soil.

    .. math::
        OCR = \\frac{\\sigma'_p}{\\sigma'_{z0}}

    Parameters
    ----------
    sigma_p : float
        Preconsolidation stress (psf, kPa, or any consistent stress unit).
    sigma_z0 : float
        Current vertical effective stress (same stress unit as *sigma_p*).

    Returns
    -------
    float
        Overconsolidation ratio (dimensionless).

    Raises
    ------
    ValueError
        If *sigma_z0* is zero or negative, or if *sigma_p* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-1, p. 224.
    """
    if sigma_z0 <= 0.0:
        raise ValueError("sigma_z0 must be positive.")
    if sigma_p < 0.0:
        raise ValueError("sigma_p must be non-negative.")
    return sigma_p / sigma_z0


# ---------------------------------------------------------------------------
# 5-2  Undrained Shear Strength from OCR
# ---------------------------------------------------------------------------

def undrained_shear_strength_from_ocr(
    usr_nc: float, ocr: float, m: float, sigma_z0: float
) -> float:
    """Undrained shear strength estimated from OCR (Equation 5-2).

    Relates the undrained shear strength of a clay to the in situ vertical
    effective stress and the overconsolidation ratio using the normally
    consolidated undrained strength ratio (USR_NC) and an empirical
    exponent *m*.

    .. math::
        s_u \\approx USR_{NC} \\cdot OCR^m \\cdot \\sigma'_{z0}

    Parameters
    ----------
    usr_nc : float
        Normally consolidated undrained strength ratio (dimensionless).
        Typical range is 0.20 to 0.35 for many clays.
    ocr : float
        Overconsolidation ratio (dimensionless).
    m : float
        Empirical exponent (dimensionless).  See Section 8-3 for guidance.
        Typical value is approximately 0.8.
    sigma_z0 : float
        Current vertical effective stress (psf, kPa, or any consistent
        stress unit).

    Returns
    -------
    float
        Estimated undrained shear strength *s_u* (same stress unit as
        *sigma_z0*).

    Raises
    ------
    ValueError
        If *usr_nc*, *ocr*, or *sigma_z0* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-2, p. 225.
    """
    if usr_nc < 0.0:
        raise ValueError("usr_nc must be non-negative.")
    if ocr < 0.0:
        raise ValueError("ocr must be non-negative.")
    if sigma_z0 < 0.0:
        raise ValueError("sigma_z0 must be non-negative.")
    return usr_nc * (ocr ** m) * sigma_z0


# ---------------------------------------------------------------------------
# 5-3  Preconsolidation Stress from Undrained Shear Strength
# ---------------------------------------------------------------------------

def preconsolidation_stress_from_su(
    su: float, usr_nc: float, m: float, sigma_z0: float
) -> float:
    """Preconsolidation stress estimated from undrained shear strength
    (Equation 5-3).

    Rearrangement of Equation 5-2 to solve for the preconsolidation stress
    given a measured or estimated undrained shear strength.

    .. math::
        \\sigma'_p \\approx \\sigma'_{z0}
        \\left(\\frac{s_u}{USR_{NC} \\cdot \\sigma'_{z0}}\\right)^{1/m}

    Parameters
    ----------
    su : float
        Undrained shear strength (psf, kPa, or any consistent stress unit).
    usr_nc : float
        Normally consolidated undrained strength ratio (dimensionless).
    m : float
        Empirical exponent (dimensionless).
    sigma_z0 : float
        Current vertical effective stress (same stress unit as *su*).

    Returns
    -------
    float
        Estimated preconsolidation stress *sigma_p* (same stress unit as
        *su*).

    Raises
    ------
    ValueError
        If *usr_nc* or *sigma_z0* is zero or negative, or if *m* is zero.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-3, p. 226.
    """
    if usr_nc <= 0.0:
        raise ValueError("usr_nc must be positive.")
    if sigma_z0 <= 0.0:
        raise ValueError("sigma_z0 must be positive.")
    if m == 0.0:
        raise ValueError("m must be non-zero.")
    return sigma_z0 * (su / (usr_nc * sigma_z0)) ** (1.0 / m)


# ---------------------------------------------------------------------------
# 5-4  Settlement from Vertical Strain Summation
# ---------------------------------------------------------------------------

def settlement_from_strain(
    epsilon_z: List[float], H: List[float]
) -> float:
    """Settlement from summation of vertical strains (Equation 5-4).

    Calculates surface settlement as the sum of the vertical strain in each
    compressible layer multiplied by its initial thickness.

    .. math::
        s = \\sum_{i=1}^{n} \\varepsilon_{z,i} \\, H_i = \\sum \\Delta H_i

    Parameters
    ----------
    epsilon_z : list of float
        Vertical strain for each soil layer (dimensionless, decimal form).
    H : list of float
        Initial thickness of each soil layer (ft, m, or any consistent
        length unit).

    Returns
    -------
    float
        Total settlement *s* (same length unit as *H*).

    Raises
    ------
    ValueError
        If the input lists have different lengths or are empty, or if any
        thickness is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-4, p. 227.
    """
    if len(epsilon_z) != len(H):
        raise ValueError("epsilon_z and H must have the same length.")
    if len(epsilon_z) == 0:
        raise ValueError("At least one layer must be provided.")
    if any(h < 0.0 for h in H):
        raise ValueError("Layer thicknesses must be non-negative.")
    return sum(ez * h for ez, h in zip(epsilon_z, H))


# ---------------------------------------------------------------------------
# 5-5  Immediate (Elastic) Settlement
# ---------------------------------------------------------------------------

def immediate_settlement(
    q0: float, B: float, Es: float, mu0: float, mu1: float
) -> float:
    """Immediate (elastic) settlement of a loaded area (Equation 5-5).

    Computes the immediate settlement of a foundation using elastic theory.
    The influence factors *mu0* and *mu1* account for embedment and
    problem geometry / Poisson's ratio, respectively.  Values are obtained
    from Figure 5-6 of the reference.

    .. math::
        s = \\frac{q_0 \\, B}{E_s} \\, \\mu_0 \\, \\mu_1

    Parameters
    ----------
    q0 : float
        Applied stress at the base of the foundation (psf, kPa, or any
        consistent stress unit).
    B : float
        Width (shortest dimension) of the foundation (ft, m, or any
        consistent length unit).
    Es : float
        Soil modulus of elasticity (same stress unit as *q0*).
    mu0 : float
        Influence factor for embedment depth (dimensionless).
    mu1 : float
        Influence factor for geometry and Poisson's ratio (dimensionless).

    Returns
    -------
    float
        Immediate settlement *s* (same length unit as *B*).

    Raises
    ------
    ValueError
        If *Es* is zero or negative, or if *B* is negative.

    Notes
    -----
    Some references incorporate a (1 - nu^2) term; check whether *mu1*
    already includes this factor before applying it separately.  The
    settlement zone is typically limited to 4B to 5B below the loaded
    area (critical depth concept, Section 4-2.1.5).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-5, p. 229.
    """
    if Es <= 0.0:
        raise ValueError("Es must be positive.")
    if B < 0.0:
        raise ValueError("B must be non-negative.")
    return (q0 * B / Es) * mu0 * mu1


# ---------------------------------------------------------------------------
# 5-6  Corrected SPT N' for Dense Saturated Silty Sand
# ---------------------------------------------------------------------------

def corrected_spt_silty_sand(N_prime: float) -> float:
    """SPT value N'SM (blows/ft) for settlement of a dense, saturated silty sand, Equation 5-6: N'SM = 15 + 0.5 (N' - 15).

    The elastic method uses an average SPT value N' to predict
    settlement in coarse-grained soils.  In dense, saturated silty
    sands the manual calculates the value N'SM as printed::

        N'SM = 15 + 0.5 (N' - 15)

    .. math::
        N'_{SM} = 15 + 0.5 \\, (N' - 15)

    Parameters
    ----------
    N_prime : float
        Average N60 value N' of a dense, saturated silty sand, from the
        bottom of the loaded area to a depth of B below the load
        (blows/ft or blows/300 mm).  The manual gives the condition in
        words only; below N' = 15 the equation returns a value higher
        than N'.

    Returns
    -------
    float
        Corrected blow count *N'_SM* (blows/ft or blows/300 mm).

    Raises
    ------
    ValueError
        If *N_prime* is negative.

    Notes
    -----
    The manual applies the equation to "dense, saturated silty sands"
    and prints no blow-count limit for it.  The equation leaves N' = 15
    unchanged, lowers a higher N' and raises a lower one (N' = 5 gives
    10), so it is not for a silty sand that is not dense.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-6, p. 229.
    """
    if N_prime < 0.0:
        raise ValueError("N_prime must be non-negative.")
    return 15.0 + 0.5 * (N_prime - 15.0)


# ---------------------------------------------------------------------------
# 5-7  Schmertmann Settlement (CPT Method)
# ---------------------------------------------------------------------------

def schmertmann_settlement(
    C1: float,
    C2: float,
    q0: float,
    sigma_z0: float,
    Iz: List[float],
    Es: List[float],
    dz: List[float],
) -> float:
    """Settlement by the Schmertmann CPT method (Equation 5-7).

    Computes settlement of coarse-grained soils using the strain influence
    factor diagram approach (Schmertmann 1970, Schmertmann et al. 1978).
    The soil beneath the foundation is divided into *n* layers, each
    characterised by an average strain influence factor and modulus.

    .. math::
        s = C_1 \\, C_2 \\, (q_0 - \\sigma'_{z0})
            \\sum_{i=1}^{n} \\frac{I_{z,i}}{E_{s,i}} \\, \\Delta z_i

    Parameters
    ----------
    C1 : float
        Embedment correction factor (dimensionless).
    C2 : float
        Time (creep) correction factor (dimensionless).
    q0 : float
        Applied foundation pressure (psf, kPa, or any consistent stress
        unit).
    sigma_z0 : float
        Existing vertical effective stress at the foundation base (same
        stress unit as *q0*).
    Iz : list of float
        Average strain influence factor for each sub-layer (dimensionless).
    Es : list of float
        Soil modulus for each sub-layer (same stress unit as *q0*).
    dz : list of float
        Thickness of each sub-layer (ft, m, or any consistent length unit).

    Returns
    -------
    float
        Settlement *s* (same length unit as *dz*).

    Raises
    ------
    ValueError
        If input lists differ in length, are empty, or if any modulus is
        zero or negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-7, p. 232.
    """
    if not (len(Iz) == len(Es) == len(dz)):
        raise ValueError("Iz, Es, and dz must have the same length.")
    if len(Iz) == 0:
        raise ValueError("At least one layer must be provided.")
    if any(e <= 0.0 for e in Es):
        raise ValueError("All Es values must be positive.")
    summation = sum(iz / es * z for iz, es, z in zip(Iz, Es, dz))
    return C1 * C2 * (q0 - sigma_z0) * summation


# ---------------------------------------------------------------------------
# 5-8  Schmertmann Embedment Correction Factor
# ---------------------------------------------------------------------------

def schmertmann_embedment_correction(
    sigma_z0: float, q0: float
) -> float:
    """Embedment correction factor C1 for Schmertmann method (Equation 5-8).

    Corrects the calculated settlement to account for the reduced strain
    influence caused by foundation embedment.

    .. math::
        C_1 = 1 - 0.5 \\, \\frac{\\sigma'_{z0}}{q_0 - \\sigma'_{z0}}
              \\geq 0.5

    Parameters
    ----------
    sigma_z0 : float
        Existing vertical effective stress at the foundation base (psf,
        kPa, or any consistent stress unit).
    q0 : float
        Applied foundation pressure (same stress unit as *sigma_z0*).
        Must be greater than *sigma_z0*.

    Returns
    -------
    float
        Embedment correction factor *C1* (dimensionless), minimum 0.5.

    Raises
    ------
    ValueError
        If *q0* is less than or equal to *sigma_z0* (net stress must be
        positive).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-8, p. 232.
    """
    net = q0 - sigma_z0
    if net <= 0.0:
        raise ValueError("q0 must be greater than sigma_z0.")
    return max(1.0 - 0.5 * (sigma_z0 / net), 0.5)


# ---------------------------------------------------------------------------
# 5-9  Schmertmann Time (Creep) Correction Factor
# ---------------------------------------------------------------------------

def schmertmann_time_correction(t_years: float) -> float:
    """Time (creep) correction factor C2 for Schmertmann method
    (Equation 5-9).

    Accounts for time-dependent (creep) settlement of coarse-grained
    soils.  The reference time is 0.1 year.

    .. math::
        C_2 = 1 + 0.2 \\, \\log_{10}\\!\\left(\\frac{t}{0.1}\\right)

    Parameters
    ----------
    t_years : float
        Time after initial loading (years).  Must be greater than zero.

    Returns
    -------
    float
        Time correction factor *C2* (dimensionless).

    Raises
    ------
    ValueError
        If *t_years* is zero or negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-9, p. 232.
    """
    if t_years <= 0.0:
        raise ValueError("t_years must be positive.")
    return 1.0 + 0.2 * math.log10(t_years / 0.1)


# ---------------------------------------------------------------------------
# 5-10  Modified Recompression Index
# ---------------------------------------------------------------------------

def modified_recompression_index(Cr: float, e0: float) -> float:
    """Modified recompression index (Equation 5-10).

    Converts the recompression index (from the e-log sigma' curve) to the
    modified form used in strain-based consolidation settlement
    calculations.

    .. math::
        C_{\\varepsilon r} = \\frac{C_r}{1 + e_0}

    Parameters
    ----------
    Cr : float
        Recompression index (dimensionless).
    e0 : float
        Initial void ratio (dimensionless).

    Returns
    -------
    float
        Modified recompression index *C_epsilon_r* (dimensionless).

    Raises
    ------
    ValueError
        If *e0* is less than or equal to -1 (denominator must be positive),
        or if *Cr* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-10, p. 239.
    """
    if e0 <= -1.0:
        raise ValueError("e0 must be greater than -1.")
    if Cr < 0.0:
        raise ValueError("Cr must be non-negative.")
    return Cr / (1.0 + e0)


# ---------------------------------------------------------------------------
# 5-11  Modified Compression Index
# ---------------------------------------------------------------------------

def modified_compression_index(Cc: float, e0: float) -> float:
    """Modified compression index (Equation 5-11).

    Converts the compression index (from the e-log sigma' curve) to the
    modified form used in strain-based consolidation settlement
    calculations.

    .. math::
        C_{\\varepsilon c} = \\frac{C_c}{1 + e_0}

    Parameters
    ----------
    Cc : float
        Compression index (dimensionless).
    e0 : float
        Initial void ratio (dimensionless).

    Returns
    -------
    float
        Modified compression index *C_epsilon_c* (dimensionless).

    Raises
    ------
    ValueError
        If *e0* is less than or equal to -1 (denominator must be positive),
        or if *Cc* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-11, p. 239.
    """
    if e0 <= -1.0:
        raise ValueError("e0 must be greater than -1.")
    if Cc < 0.0:
        raise ValueError("Cc must be non-negative.")
    return Cc / (1.0 + e0)


# ---------------------------------------------------------------------------
# 5-12  Primary Consolidation Settlement – Normally Consolidated
# ---------------------------------------------------------------------------

def primary_consolidation_settlement_nc(
    C_epsilon_c: float, sigma_z0: float, delta_sigma_z: float, H: float
) -> float:
    """Primary consolidation settlement for normally consolidated soil
    (Equation 5-12).

    Applies when the soil is normally consolidated (sigma'_z0 approx
    sigma'_p).  The entire stress increment loads the soil along the
    virgin compression curve.

    .. math::
        s_c = C_{\\varepsilon c} \\, \\log_{10}\\!
        \\left(\\frac{\\sigma'_{z0} + \\Delta\\sigma_z}{\\sigma'_{z0}}\\right)
        \\, H

    Parameters
    ----------
    C_epsilon_c : float
        Modified compression index (dimensionless).
    sigma_z0 : float
        Initial vertical effective stress at the midpoint of the layer
        (psf, kPa, or any consistent stress unit).
    delta_sigma_z : float
        Change in vertical stress at the layer midpoint (same stress unit
        as *sigma_z0*).
    H : float
        Initial thickness of the soil layer or sublayer (ft, m, or any
        consistent length unit).

    Returns
    -------
    float
        Primary consolidation settlement *s_c* (same length unit as *H*).

    Raises
    ------
    ValueError
        If *sigma_z0* is zero or negative, or if the final stress
        (sigma_z0 + delta_sigma_z) is not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-12, p. 241.
    """
    if sigma_z0 <= 0.0:
        raise ValueError("sigma_z0 must be positive.")
    final_stress = sigma_z0 + delta_sigma_z
    if final_stress <= 0.0:
        raise ValueError("Final stress (sigma_z0 + delta_sigma_z) must be positive.")
    return C_epsilon_c * math.log10(final_stress / sigma_z0) * H


# ---------------------------------------------------------------------------
# 5-13  Primary Consolidation Settlement – Overconsolidated (within recompression)
# ---------------------------------------------------------------------------

def primary_consolidation_settlement_oc_recompression(
    C_epsilon_r: float, sigma_z0: float, delta_sigma_z: float, H: float
) -> float:
    """Primary consolidation settlement for overconsolidated soil when the
    final stress remains at or below the preconsolidation stress
    (Equation 5-13).

    Applies when sigma'_z0 + delta_sigma_z <= sigma'_p.  All loading
    occurs along the recompression curve.

    .. math::
        s_c = C_{\\varepsilon r} \\, \\log_{10}\\!
        \\left(\\frac{\\sigma'_{z0} + \\Delta\\sigma_z}{\\sigma'_{z0}}\\right)
        \\, H

    Parameters
    ----------
    C_epsilon_r : float
        Modified recompression index (dimensionless).
    sigma_z0 : float
        Initial vertical effective stress at the midpoint of the layer
        (psf, kPa, or any consistent stress unit).
    delta_sigma_z : float
        Change in vertical stress at the layer midpoint (same stress unit
        as *sigma_z0*).
    H : float
        Initial thickness of the soil layer or sublayer (ft, m, or any
        consistent length unit).

    Returns
    -------
    float
        Primary consolidation settlement *s_c* (same length unit as *H*).

    Raises
    ------
    ValueError
        If *sigma_z0* is zero or negative, or if the final stress is
        not positive.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-13, p. 241.
    """
    if sigma_z0 <= 0.0:
        raise ValueError("sigma_z0 must be positive.")
    final_stress = sigma_z0 + delta_sigma_z
    if final_stress <= 0.0:
        raise ValueError("Final stress (sigma_z0 + delta_sigma_z) must be positive.")
    return C_epsilon_r * math.log10(final_stress / sigma_z0) * H


# ---------------------------------------------------------------------------
# 5-14  Primary Consolidation Settlement – Overconsolidated (exceeding sigma_p)
# ---------------------------------------------------------------------------

def primary_consolidation_settlement_oc_beyond(
    C_epsilon_r: float,
    C_epsilon_c: float,
    sigma_z0: float,
    delta_sigma_z: float,
    sigma_p: float,
    H: float,
) -> float:
    """Primary consolidation settlement for overconsolidated soil when the
    final stress exceeds the preconsolidation stress (Equation 5-14).

    Applies when sigma'_z0 + delta_sigma_z > sigma'_p.  Loading first
    follows the recompression curve up to sigma'_p, then continues along
    the virgin compression curve.

    .. math::
        s_c = \\left[
            C_{\\varepsilon r} \\, \\log_{10}\\!
            \\left(\\frac{\\sigma'_p}{\\sigma'_{z0}}\\right)
            + C_{\\varepsilon c} \\, \\log_{10}\\!
            \\left(\\frac{\\sigma'_{z0} + \\Delta\\sigma_z}{\\sigma'_p}\\right)
        \\right] H

    Parameters
    ----------
    C_epsilon_r : float
        Modified recompression index (dimensionless).
    C_epsilon_c : float
        Modified compression index (dimensionless).
    sigma_z0 : float
        Initial vertical effective stress at the midpoint of the layer
        (psf, kPa, or any consistent stress unit).
    delta_sigma_z : float
        Change in vertical stress at the layer midpoint (same stress unit
        as *sigma_z0*).
    sigma_p : float
        Preconsolidation stress (same stress unit as *sigma_z0*).
    H : float
        Initial thickness of the soil layer or sublayer (ft, m, or any
        consistent length unit).

    Returns
    -------
    float
        Primary consolidation settlement *s_c* (same length unit as *H*).

    Raises
    ------
    ValueError
        If *sigma_z0* or *sigma_p* is zero or negative, or if the
        final stress does not exceed *sigma_p*.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-14, p. 241.
    """
    if sigma_z0 <= 0.0:
        raise ValueError("sigma_z0 must be positive.")
    if sigma_p <= 0.0:
        raise ValueError("sigma_p must be positive.")
    final_stress = sigma_z0 + delta_sigma_z
    if final_stress <= sigma_p:
        raise ValueError(
            "Final stress must exceed sigma_p for this equation. "
            "Use Equation 5-13 instead."
        )
    recompression = C_epsilon_r * math.log10(sigma_p / sigma_z0)
    virgin = C_epsilon_c * math.log10(final_stress / sigma_p)
    return (recompression + virgin) * H


# ---------------------------------------------------------------------------
# 5-15  Time Factor for Vertical Drainage
# ---------------------------------------------------------------------------

def time_factor_vertical(cv: float, t: float, Hdr: float) -> float:
    """Time factor for vertical drainage (Equation 5-15).

    The dimensionless time factor (*Tv*) relates elapsed time to the
    degree of consolidation for one-dimensional vertical drainage.  Used
    in conjunction with Figure 5-16 to determine the average degree of
    consolidation.

    .. math::
        T_v = \\frac{c_v \\, t}{H_{dr}^2}

    Parameters
    ----------
    cv : float
        Coefficient of consolidation in the vertical direction
        (length^2 / time, e.g., ft^2/day or m^2/year).
    t : float
        Elapsed time after application of load (same time unit as
        used in *cv*).
    Hdr : float
        Drainage path length (same length unit as used in *cv*).
        Equal to the full layer thickness for single drainage and half
        the thickness for double drainage.

    Returns
    -------
    float
        Time factor *T_v* (dimensionless).

    Raises
    ------
    ValueError
        If *Hdr* is zero or negative, or if *cv* or *t* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-15, p. 245.
    """
    if Hdr <= 0.0:
        raise ValueError("Hdr must be positive.")
    if cv < 0.0:
        raise ValueError("cv must be non-negative.")
    if t < 0.0:
        raise ValueError("t must be non-negative.")
    return cv * t / (Hdr ** 2)


# ---------------------------------------------------------------------------
# 5-16  Equivalent Layer Thickness for Layered Profile
# ---------------------------------------------------------------------------

def equivalent_layer_thickness(
    cv_i: float, cv_n: float, Hn: float
) -> float:
    """Equivalent layer thickness for a layer in a multi-layer consolidation
    profile (Equation 5-16).

    Transforms the thickness of a layer with properties (cv_n, Hn) to an
    equivalent thickness having the properties of a selected reference
    layer (cv_i).  Used iteratively for every non-reference layer in a
    layered consolidation system.

    .. math::
        H'_n = H_n \\, \\sqrt{\\frac{c_{v,i}}{c_{v,n}}}

    Parameters
    ----------
    cv_i : float
        Coefficient of consolidation of the reference layer
        (length^2 / time).
    cv_n : float
        Coefficient of consolidation of the layer being transformed
        (length^2 / time, same unit as *cv_i*).
    Hn : float
        Actual thickness of the layer being transformed (ft, m, or any
        consistent length unit).

    Returns
    -------
    float
        Equivalent thickness *H'_n* (same length unit as *Hn*).

    Raises
    ------
    ValueError
        If *cv_n* is zero or negative, or if *cv_i* or *Hn* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-16, p. 251.
    """
    if cv_n <= 0.0:
        raise ValueError("cv_n must be positive.")
    if cv_i < 0.0:
        raise ValueError("cv_i must be non-negative.")
    if Hn < 0.0:
        raise ValueError("Hn must be non-negative.")
    return Hn * math.sqrt(cv_i / cv_n)


# ---------------------------------------------------------------------------
# 5-17  Total Transformed Thickness
# ---------------------------------------------------------------------------

def total_transformed_thickness(H_prime: List[float]) -> float:
    """Total thickness of the transformed multi-layer system (Equation 5-17).

    Sums the equivalent thicknesses of all layers (after transformation
    using Equation 5-16) to obtain the total thickness used for time-rate
    calculations with a single equivalent layer.

    .. math::
        H'_t = \\sum H'_n

    Parameters
    ----------
    H_prime : list of float
        Equivalent thicknesses of all layers after transformation
        (ft, m, or any consistent length unit).

    Returns
    -------
    float
        Total transformed thickness *H'_t* (same length unit as *H_prime*).

    Raises
    ------
    ValueError
        If the list is empty or if any thickness is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-17, p. 251.
    """
    if len(H_prime) == 0:
        raise ValueError("At least one layer must be provided.")
    if any(h < 0.0 for h in H_prime):
        raise ValueError("All thicknesses must be non-negative.")
    return sum(H_prime)


# ---------------------------------------------------------------------------
# 5-18  Secondary Compression Settlement
# ---------------------------------------------------------------------------

def secondary_compression_settlement(
    C_epsilon_alpha: float, t: float, tp: float, H0: float
) -> float:
    """Secondary compression settlement (Equation 5-18).

    Computes settlement caused by secondary compression (creep) occurring
    after the end of primary consolidation.  Secondary compression is
    assumed to follow a linear trend with the logarithm of time.

    The equation can also be written using the secondary compression
    index *C_alpha* and initial void ratio *e0* as:
    C_epsilon_alpha = C_alpha / (1 + e0).

    .. math::
        s_s = C_{\\varepsilon\\alpha} \\, \\log_{10}\\!
        \\left(\\frac{t}{t_p}\\right) \\, H_0

    Parameters
    ----------
    C_epsilon_alpha : float
        Modified secondary compression index (dimensionless).
        Equals C_alpha / (1 + e0).
    t : float
        Time after loading at which secondary settlement is evaluated
        (days, years, or any consistent time unit).
    tp : float
        Time required to finish primary consolidation (same time unit
        as *t*).
    H0 : float
        Initial layer thickness (ft, m, or any consistent length unit).

    Returns
    -------
    float
        Secondary compression settlement *s_s* (same length unit as *H0*).

    Raises
    ------
    ValueError
        If *tp* is zero or negative, or if *t* is less than *tp*.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-18, p. 254.
    """
    if tp <= 0.0:
        raise ValueError("tp must be positive.")
    if t < tp:
        raise ValueError("t must be greater than or equal to tp.")
    return C_epsilon_alpha * math.log10(t / tp) * H0


# ---------------------------------------------------------------------------
# 5-19  Modified Secondary Compression Index from Water Content
# ---------------------------------------------------------------------------

def modified_secondary_compression_index_from_wn(wn: float) -> float:
    """Estimate of modified secondary compression index from natural water
    content (Equation 5-19).

    An approximate correlation by Mesri (1973) relating the modified
    secondary compression index to the natural water content for clays,
    silts, and organic soils.

    .. math::
        C_{\\varepsilon\\alpha} \\approx 10^{-4} \\, w_n

    Parameters
    ----------
    wn : float
        Natural water content (percent, e.g., 40 for 40% water content).

    Returns
    -------
    float
        Estimated modified secondary compression index *C_epsilon_alpha*
        (dimensionless).

    Raises
    ------
    ValueError
        If *wn* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-19, p. 254.
    """
    if wn < 0.0:
        raise ValueError("wn must be non-negative.")
    return 1.0e-4 * wn


# ---------------------------------------------------------------------------
# 5-20  Degree of Consolidation Required Under Surcharge (Primary Only)
# ---------------------------------------------------------------------------

def surcharge_degree_of_consolidation(
    qf: float, sigma_z0: float, qs: float
) -> float:
    """Degree of consolidation required under surcharge to achieve the
    settlement equivalent to primary consolidation under the final load
    (Equation 5-20).

    Used in preconsolidation by surcharge design to determine the required
    degree of consolidation when only primary consolidation settlement
    needs to be removed.

    .. math::
        U_{f+s} = \\frac{\\log_{10}\\!\\left(1 + \\frac{q_f}{\\sigma'_{z0}}\\right)}
        {\\log_{10}\\!\\left(1 + \\frac{q_f + q_s}{\\sigma'_{z0}}\\right)}

    Parameters
    ----------
    qf : float
        Final applied load (psf, kPa, or any consistent stress unit).
    sigma_z0 : float
        Initial vertical effective stress at the midpoint of the
        consolidating layer (same stress unit as *qf*).
    qs : float
        Additional surcharge load above the final load (same stress unit
        as *qf*).

    Returns
    -------
    float
        Required degree of consolidation *U_f+s* (decimal form, 0 to 1).

    Raises
    ------
    ValueError
        If *sigma_z0* is zero or negative, or if *qf* or *qs* is
        negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-20, p. 263.
    """
    if sigma_z0 <= 0.0:
        raise ValueError("sigma_z0 must be positive.")
    if qf < 0.0:
        raise ValueError("qf must be non-negative.")
    if qs < 0.0:
        raise ValueError("qs must be non-negative.")
    numerator = math.log10(1.0 + qf / sigma_z0)
    denominator = math.log10(1.0 + (qf + qs) / sigma_z0)
    if denominator == 0.0:
        raise ValueError(
            "Denominator is zero; check that qf + qs > 0."
        )
    return numerator / denominator


# ---------------------------------------------------------------------------
# 5-21  Degree of Consolidation Required Under Surcharge
#        (Primary + Secondary)
# ---------------------------------------------------------------------------

def surcharge_degree_of_consolidation_with_secondary(
    qf: float,
    sigma_z0: float,
    qs: float,
    C_alpha_over_Cc: float,
    t: float,
    tp: float,
) -> float:
    """Degree of consolidation required under surcharge including secondary
    compression removal (Equation 5-21).

    Extends Equation 5-20 to account for the secondary compression
    settlement that must also be eliminated by the surcharge.

    .. math::
        U_{f+s} = \\frac{
            \\log_{10}\\!\\left(1 + \\frac{q_f}{\\sigma'_{z0}}\\right)
            + \\frac{C_\\alpha}{C_c} \\, \\log_{10}\\!
              \\left(\\frac{t}{t_p}\\right)
        }{
            \\log_{10}\\!\\left(1 + \\frac{q_f + q_s}{\\sigma'_{z0}}\\right)
        }

    Parameters
    ----------
    qf : float
        Final applied load (psf, kPa, or any consistent stress unit).
    sigma_z0 : float
        Initial vertical effective stress at the midpoint of the
        consolidating layer (same stress unit as *qf*).
    qs : float
        Additional surcharge load above the final load (same stress unit
        as *qf*).
    C_alpha_over_Cc : float
        Ratio of secondary compression index to compression index
        (dimensionless).  Typical values are given in Table 5-6.
    t : float
        Time after loading for which secondary compression is considered
        (days, years, or any consistent time unit).
    tp : float
        Time required for primary consolidation (same time unit as *t*).

    Returns
    -------
    float
        Required degree of consolidation *U_f+s* (decimal form, 0 to 1).

    Raises
    ------
    ValueError
        If *sigma_z0* or *tp* is zero or negative, or if *t* < *tp*.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-21, p. 263.
    """
    if sigma_z0 <= 0.0:
        raise ValueError("sigma_z0 must be positive.")
    if qf < 0.0:
        raise ValueError("qf must be non-negative.")
    if qs < 0.0:
        raise ValueError("qs must be non-negative.")
    if tp <= 0.0:
        raise ValueError("tp must be positive.")
    if t < tp:
        raise ValueError("t must be greater than or equal to tp.")
    primary_term = math.log10(1.0 + qf / sigma_z0)
    secondary_term = C_alpha_over_Cc * math.log10(t / tp)
    denominator = math.log10(1.0 + (qf + qs) / sigma_z0)
    if denominator == 0.0:
        raise ValueError(
            "Denominator is zero; check that qf + qs > 0."
        )
    return (primary_term + secondary_term) / denominator


# ---------------------------------------------------------------------------
# 5-22  Time Factor for Radial Drainage
# ---------------------------------------------------------------------------

def time_factor_radial(
    Ur: float, Fn: float, Fs: float = 0.0, Fr: float = 0.0
) -> float:
    """Time factor for radial drainage to vertical drains (Equation 5-22).

    Calculates the time factor (*Tr*) required to achieve a specified
    degree of radial consolidation (*Ur*) in a vertical drain system,
    using the method presented by FHWA (2017) based on Barron (1948).

    .. math::
        T_r = \\frac{1}{8} \\, (F_n + F_s + F_r) \\,
        \\ln\\!\\left(\\frac{1}{1 - U_r}\\right)

    Parameters
    ----------
    Ur : float
        Desired degree of radial consolidation (decimal form, 0 to < 1).
    Fn : float
        Factor related to drain spacing (dimensionless).  See Equation 5-23.
    Fs : float, optional
        Factor related to soil disturbance / smear (dimensionless).
        Default is 0.0 (smear ignored).  See Equation 5-25.
    Fr : float, optional
        Factor related to well resistance in the drain (dimensionless).
        Default is 0.0 (well resistance ignored).  See Equation 5-26.

    Returns
    -------
    float
        Time factor for radial drainage *T_r* (dimensionless).

    Raises
    ------
    ValueError
        If *Ur* is not in the range [0, 1).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-22, p. 266.
    """
    if Ur < 0.0 or Ur >= 1.0:
        raise ValueError("Ur must be in the range [0, 1).")
    return (1.0 / 8.0) * (Fn + Fs + Fr) * math.log(1.0 / (1.0 - Ur))


# ---------------------------------------------------------------------------
# 5-23  Drain Spacing Factor
# ---------------------------------------------------------------------------

def drain_spacing_factor(n: float, approximate: bool = True) -> float:
    """Drainage factor Fn (dimensionless) for vertical drains from the ratio n = dc/dw, Equation 5-23.

    Computes the drainage factor as a function of the ratio *n* of
    effective drainage diameter (*dc*) to drain diameter (*dw*).  Both
    the full expression and its approximation are printed::

        Fn = [n^2 / (n^2 - 1)] ln(n) - (3 n^2 - 1) / (4 n^2)
           ~ ln(n) - 0.75

    Full expression (n^2/(n^2 - 1) multiplies ln(n) only):

    .. math::
        F_n = \\frac{n^2}{n^2 - 1} \\ln(n) - \\frac{3 n^2 - 1}{4 n^2}

    Approximate (error < 10% for n > 4, < 1% for n > 12):

    .. math::
        F_n \\approx \\ln(n) - 0.75

    Parameters
    ----------
    n : float
        Ratio of the effective drainage diameter *dc* to the drain
        diameter *dw* (dimensionless).  Typically in the range of 20
        to 50 for modern PVDs.
    approximate : bool, optional
        If True (default), use the simplified approximation.  If False,
        use the exact expression.

    Returns
    -------
    float
        Drain spacing factor *Fn* (dimensionless).

    Raises
    ------
    ValueError
        If *n* is less than or equal to 1.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-23, p. 267.
    """
    if n <= 1.0:
        raise ValueError("n must be greater than 1.")
    if approximate:
        return math.log(n) - 0.75
    else:
        n2 = n ** 2
        return (n2 / (n2 - 1.0)) * math.log(n) - (3.0 * n2 - 1.0) / (4.0 * n2)


# ---------------------------------------------------------------------------
# 5-24  Equivalent Drain Diameter for Rectangular PVD
# ---------------------------------------------------------------------------

def equivalent_drain_diameter(a: float, b: float) -> float:
    """Equivalent circular drain diameter for a rectangular prefabricated
    vertical drain (Equation 5-24).

    Converts the rectangular cross-section dimensions of a PVD to an
    equivalent circular drain diameter, following Hansbo (1979).

    .. math::
        d_w = \\frac{2 \\, (a + b)}{\\pi}

    Parameters
    ----------
    a : float
        Width of the PVD cross section (in, mm, or any consistent length
        unit).
    b : float
        Thickness of the PVD cross section (same length unit as *a*).

    Returns
    -------
    float
        Equivalent drain diameter *d_w* (same length unit as *a*).
        Typical values range from 1.5 to 5.5 inches for modern PVDs.

    Raises
    ------
    ValueError
        If *a* or *b* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-24, p. 267.
    """
    if a < 0.0:
        raise ValueError("a must be non-negative.")
    if b < 0.0:
        raise ValueError("b must be non-negative.")
    return 2.0 * (a + b) / math.pi


# ---------------------------------------------------------------------------
# 5-25  Soil Disturbance (Smear) Factor
# ---------------------------------------------------------------------------

def smear_factor(kh: float, ks: float, s: float) -> float:
    """Soil disturbance (smear) factor Fs for vertical drains
    (Equation 5-25).

    Accounts for the reduction in hydraulic conductivity within the
    disturbed zone around a vertical drain caused by the installation
    process.  Smear is most significant in high-plasticity clays or
    sensitive soils.

    .. math::
        F_s \\approx \\frac{k_h}{k_s} \\, \\ln(s)

    Parameters
    ----------
    kh : float
        Hydraulic conductivity of the undisturbed soil in the horizontal
        direction (ft/day, m/s, or any consistent permeability unit).
    ks : float
        Hydraulic conductivity of the disturbed (smear) zone (same unit
        as *kh*).  Typically less than *kh*.
    s : float
        Ratio of the diameter of the disturbed zone to the diameter of
        the drain (dimensionless).  Typically 2 to 5.

    Returns
    -------
    float
        Smear factor *Fs* (dimensionless).

    Raises
    ------
    ValueError
        If *ks* is zero or negative, or if *s* is less than or equal
        to 1.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-25, p. 267.
    """
    if ks <= 0.0:
        raise ValueError("ks must be positive.")
    if s <= 1.0:
        raise ValueError("s must be greater than 1.")
    return (kh / ks) * math.log(s)


# ---------------------------------------------------------------------------
# 5-26  Well Resistance Factor
# ---------------------------------------------------------------------------

def well_resistance_factor(
    kh: float, z: float, Lm: float, qw: float
) -> float:
    """Well resistance factor Fr (dimensionless) for vertical drains, Equation 5-26: Fr = pi z (2 Lm - z) kh / qw.

    Estimates the loss in drainage efficiency due to the finite discharge
    capacity of a vertical drain.  Well resistance becomes important for
    long drains or drains with low discharge capacity.  As printed::

        Fr = pi * z * (2 Lm - z) * kh / qw

    .. math::
        F_r = \\pi \\, z \\, (2 L_m - z) \\, \\frac{k_h}{q_w}

    Parameters
    ----------
    kh : float
        Horizontal hydraulic conductivity of the soil layer (ft/day, m/s,
        or any consistent permeability unit).
    z : float
        Depth along the drain at the point of interest (ft, m, or any
        consistent length unit).
    Lm : float
        Maximum distance water must flow through the drain (same length
        unit as *z*).  Equals the full drain length for one-way drainage
        or half the length for two-way drainage.
    qw : float
        Discharge capacity of the drain (length^3 / time, e.g., ft^3/day
        or m^3/s).  Units must be consistent with *kh* and *z*.

    Returns
    -------
    float
        Well resistance factor *Fr* (dimensionless).

    Raises
    ------
    ValueError
        If *qw* is zero or negative, or if *z* > *Lm*.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-26, p. 268.
    """
    if qw <= 0.0:
        raise ValueError("qw must be positive.")
    if z < 0.0:
        raise ValueError("z must be non-negative.")
    if z > Lm:
        raise ValueError("z must not exceed Lm.")
    return math.pi * z * (2.0 * Lm - z) * (kh / qw)


# ---------------------------------------------------------------------------
# 5-27  Combined Degree of Consolidation (Vertical + Radial)
# ---------------------------------------------------------------------------

def combined_degree_of_consolidation(Uz: float, Ur: float) -> float:
    """Combined degree of consolidation from vertical and radial drainage
    (Equation 5-27).

    Combines the independent contributions of vertical and horizontal
    (radial) drainage using the method proposed by Carrillo (1942).
    Both inputs and the output are expressed as percentages.

    .. math::
        U_c = 100 - \\frac{(100 - U_z)(100 - U_r)}{100}

    Parameters
    ----------
    Uz : float
        Degree of consolidation for vertical drainage (percent, 0 to 100).
    Ur : float
        Degree of consolidation for radial drainage (percent, 0 to 100).

    Returns
    -------
    float
        Combined degree of consolidation *Uc* (percent, 0 to 100).

    Raises
    ------
    ValueError
        If *Uz* or *Ur* is outside [0, 100].

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-27, p. 268.
    """
    if not (0.0 <= Uz <= 100.0):
        raise ValueError("Uz must be between 0 and 100.")
    if not (0.0 <= Ur <= 100.0):
        raise ValueError("Ur must be between 0 and 100.")
    return 100.0 - (100.0 - Uz) * (100.0 - Ur) / 100.0


# ---------------------------------------------------------------------------
# 5-28  Required Effective Drain Diameter from Time Factor
# ---------------------------------------------------------------------------

def required_drain_diameter(ch: float, t: float, Tr: float) -> float:
    """Required effective drain diameter from the radial time factor
    (Equation 5-28).

    Given the horizontal coefficient of consolidation, the time available
    for consolidation, and the design radial time factor (from
    Equation 5-22 or Figure 5-30/5-31), this equation determines the
    required effective drainage diameter for the vertical drain pattern.

    .. math::
        d_c = \\sqrt{\\frac{c_h \\, t}{T_r}}

    Parameters
    ----------
    ch : float
        Coefficient of consolidation in the horizontal direction
        (length^2 / time, e.g., ft^2/day or m^2/year).
    t : float
        Time available for consolidation (same time unit as used in *ch*).
    Tr : float
        Time factor for radial drainage (dimensionless).  Obtained from
        Equation 5-22 or Figures 5-30 / 5-31.

    Returns
    -------
    float
        Required effective drain diameter *dc* (same length unit as used
        in *ch*).

    Raises
    ------
    ValueError
        If *Tr* is zero or negative, or if *ch* or *t* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Equation 5-28, p. 268.
    """
    if Tr <= 0.0:
        raise ValueError("Tr must be positive.")
    if ch < 0.0:
        raise ValueError("ch must be non-negative.")
    if t < 0.0:
        raise ValueError("t must be non-negative.")
    return math.sqrt(ch * t / Tr)


# ===========================================================================
# FIGURE 5-16: Average Degree of Consolidation vs Time Factor
# ===========================================================================

def figure_5_16_U_from_Tv(Tv: float) -> float:
    """Average degree of consolidation from the time factor (Figure 5-16).

    Uses the Terzaghi (1943) closed-form solution for one-dimensional
    consolidation with an initially uniform excess pore-pressure
    distribution and double drainage.

    For U < 60 %:

    .. math::
        T_v = \\frac{\\pi}{4}\\left(\\frac{U}{100}\\right)^2

    For U >= 60 %:

    .. math::
        T_v = -0.9332\\,\\log_{10}(1 - U/100) - 0.0851

    This function inverts those relationships to return U given Tv.

    Parameters
    ----------
    Tv : float
        Time factor (dimensionless, >= 0).

    Returns
    -------
    float
        Average degree of consolidation U (percent, 0 to ~100).

    Raises
    ------
    ValueError
        If *Tv* is negative.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Figure 5-16, p. 245.
    Terzaghi, K. (1943). Theoretical Soil Mechanics.
    """
    if Tv < 0.0:
        raise ValueError("Tv must be non-negative.")
    # Transition point: U = 60 % → Tv_60 = pi/4 * 0.36 = 0.2827
    Tv_60 = math.pi / 4.0 * 0.36
    if Tv <= Tv_60:
        # U/100 = sqrt(4*Tv/pi)
        return 100.0 * math.sqrt(4.0 * Tv / math.pi)
    else:
        # Tv = -0.9332*log10(1 - U/100) - 0.0851
        # log10(1 - U/100) = -(Tv + 0.0851) / 0.9332
        val = 10.0 ** (-(Tv + 0.0851) / 0.9332)
        U = 100.0 * (1.0 - val)
        return min(U, 100.0)


def figure_5_16_Tv_from_U(U: float) -> float:
    """Time factor from average degree of consolidation (Figure 5-16).

    Forward evaluation of the Terzaghi (1943) closed-form relationships.

    Parameters
    ----------
    U : float
        Average degree of consolidation (percent, 0 to < 100).

    Returns
    -------
    float
        Time factor Tv (dimensionless).

    Raises
    ------
    ValueError
        If *U* is not in the range [0, 100).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Figure 5-16, p. 245.
    Terzaghi, K. (1943). Theoretical Soil Mechanics.
    """
    if U < 0.0 or U >= 100.0:
        raise ValueError("U must be in the range [0, 100).")
    if U < 60.0:
        return math.pi / 4.0 * (U / 100.0) ** 2
    else:
        return -0.9332 * math.log10(1.0 - U / 100.0) - 0.0851


# ===========================================================================
# FIGURE 5-30/31: Convenience Wrapper for Radial Time Factor
# ===========================================================================

def figure_5_30_Tr(
    Ur: float, n: float, Fs: float = 0.0, Fr: float = 0.0,
    approximate: bool = True
) -> float:
    """Radial time factor Tr from Figures 5-30 / 5-31.

    Convenience wrapper that computes the drain spacing factor Fn
    (Equation 5-23), then evaluates the analytical expression for Tr
    (Equation 5-22) in a single call.

    Parameters
    ----------
    Ur : float
        Desired degree of radial consolidation (decimal, 0 to < 1).
    n : float
        Ratio of effective drainage diameter (dc) to drain diameter (dw).
    Fs : float, optional
        Smear factor (default 0).
    Fr : float, optional
        Well resistance factor (default 0).
    approximate : bool, optional
        Whether to use the approximate Fn formula (default True).

    Returns
    -------
    float
        Radial time factor Tr (dimensionless).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Figures 5-30 / 5-31, pp. 269-270.
    """
    Fn = drain_spacing_factor(n, approximate=approximate)
    return time_factor_radial(Ur, Fn, Fs, Fr)


# ===========================================================================
# TABLE 5-6: Secondary Compression Ratio Calpha/Cc
# ===========================================================================

_TABLE_5_6_CALPHA_CC = {
    # Soil type: Calpha / Cc; the table gives each value +/- 0.01 (p. 254)
    "granular": 0.02,                # Granular soils including rockfill
    "shale_mudstone": 0.03,          # Shale and mudstone
    "inorganic_clays_silts": 0.04,   # Inorganic clays and silts
    "organic_clays_silts": 0.05,     # Organic clays and silts
    "peat": 0.06,                    # Peat and muskeg
}


def table_5_6_Calpha_Cc(soil_type: str) -> float:
    """Typical ratio Calpha/Cc (dimensionless; the table gives each value +/- 0.01) of secondary compression index to compression index by soil type, Table 5-6 "Typical Values of Calpha / Cc (after Terzaghi et al. 1996)".

    The five printed rows are: granular soils including rockfill
    0.02 +/- 0.01; shale and mudstone 0.03 +/- 0.01; inorganic clays
    and silts 0.04 +/- 0.01; organic clays and silts 0.05 +/- 0.01;
    peat and muskeg 0.06 +/- 0.01.  The function returns the central
    value.

    Parameters
    ----------
    soil_type : str
        One of ``"granular"`` (granular soils including rockfill),
        ``"shale_mudstone"``, ``"inorganic_clays_silts"``,
        ``"organic_clays_silts"`` or ``"peat"`` (peat and muskeg).

    Returns
    -------
    float
        Typical Calpha / Cc ratio (dimensionless), the central value of
        the printed "value +/- 0.01".

    Raises
    ------
    ValueError
        If *soil_type* is not recognised.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Table 5-6, p. 254 (after Terzaghi et al. 1996).
    """
    key = soil_type.lower().strip()
    if key not in _TABLE_5_6_CALPHA_CC:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. "
            f"Choose from: {list(_TABLE_5_6_CALPHA_CC.keys())}"
        )
    return _TABLE_5_6_CALPHA_CC[key]


# ===========================================================================
# FIGURE 5-6: Elastic Influence Factors for nu = 0.5 for (a) mu1 (after
#             Giroud 1972) and (b) mu0 (after Burland 1970)
# ===========================================================================

# (b) mu0 against D/B, read off the curve of Figure 5-6(b) (p. 230).
# Axes: D/B 0 to 20, mu0 0.85 to 1.00.  Read to about +/-0.003.
_FIG_5_6_DB = [
    0.0, 0.16, 0.24, 0.37, 0.47, 0.66, 1.0, 1.5, 2.0, 2.5, 3.0,
    4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0,
]
_FIG_5_6_MU0 = [
    1.00, 0.97, 0.96, 0.945, 0.94, 0.93, 0.92, 0.908, 0.901, 0.896, 0.891,
    0.883, 0.877, 0.872, 0.868, 0.866, 0.863, 0.862, 0.860, 0.859, 0.859,
]


def figure_5_6_mu0(D_over_B: float) -> float:
    """Influence factor mu0 (dimensionless) for embedment of the load in the elastic settlement s = mu0 mu1 q0 B / Es (Equation 5-5), read from Figure 5-6(b) at D/B, for Poisson's ratio 0.5.

    Figure 5-6, "Elastic Influence Factors for nu = 0.5 for (a) mu1
    (after Giroud 1972) and (b) mu0 (after Burland 1970)".  Panel (b)
    plots mu0 against D/B from 0 to 20: 1.00 at D/B = 0, 0.92 at 1,
    0.90 at 2, 0.877 at 5, 0.862 at 10 and 0.859 from about 13 to 20.
    This function interpolates linearly between points read off that
    curve (to about +/-0.003).

    Parameters
    ----------
    D_over_B : float
        Ratio of the depth D of the load below the ground surface to
        its width B, from 0 to 20 (the range of the figure's axis).

    Returns
    -------
    float
        Influence factor mu0 (dimensionless, 0.859 to 1.0).

    Raises
    ------
    ValueError
        If *D_over_B* is negative or above 20 (the figure's axis ends
        there).

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Figure 5-6(b), p. 230 (after Burland 1970).
    """
    if D_over_B < 0.0:
        raise ValueError("D_over_B must be non-negative.")
    if D_over_B > _FIG_5_6_DB[-1]:
        raise ValueError(
            "D_over_B is above 20, the end of the D/B axis of Figure "
            "5-6(b) (UFS 3-220-10 p. 230)."
        )
    return _linterp(D_over_B, _FIG_5_6_DB, _FIG_5_6_MU0)


# (a) mu1 against H/B, read off the curves of Figure 5-6(a) (p. 230).
# Axes: H/B 0.1 to 1000 (logarithmic), mu1 0 to 2.0.  Curves: Square,
# L/B = 2, L/B = 5, L/B = 10 and Infinite (drawn to H/B = 20).
#
# Below H/B of about 1.5 the five curves run together in one band about
# 0.06 wide and cannot be told apart on the print: every curve is given
# the middle of the band there (+/-0.03).  The L/B = 5, L/B = 10 and
# Infinite curves stay together in the same way up to H/B = 5.  Where a
# curve stands alone it is read to about +/-0.01.
_FIG_5_6_HB = [
    0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2,
    1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0, 15.0, 20.0,
    25.0, 30.0, 40.0, 50.0, 70.0, 100.0, 150.0, 200.0, 300.0, 500.0,
    700.0, 1000.0,
]
_FIG_5_6_LOG_HB = [math.log10(_hb) for _hb in _FIG_5_6_HB]

# H/B 0.1 to 1.2: the band of all five curves
_FIG_5_6_MU1_BAND = [
    0.01, 0.02, 0.035, 0.05, 0.07, 0.11, 0.15, 0.19, 0.23, 0.27, 0.30,
    0.34, 0.40,
]
# H/B 1.5 to 1000
_FIG_5_6_MU1_SQUARE = _FIG_5_6_MU1_BAND + [
    0.455, 0.515, 0.555, 0.585, 0.62, 0.645, 0.65, 0.66, 0.665, 0.675,
    0.68, 0.685, 0.69, 0.695, 0.695, 0.70, 0.705, 0.705, 0.71, 0.71,
    0.71, 0.71, 0.71, 0.71, 0.71,
]
_FIG_5_6_MU1_LB2 = _FIG_5_6_MU1_BAND + [
    0.49, 0.59, 0.67, 0.72, 0.79, 0.83, 0.845, 0.86, 0.87, 0.89,
    0.905, 0.92, 0.935, 0.94, 0.945, 0.955, 0.96, 0.965, 0.97, 0.97,
    0.97, 0.975, 0.975, 0.975, 0.975,
]
_FIG_5_6_MU1_LB5 = _FIG_5_6_MU1_BAND + [
    0.49, 0.62, 0.715, 0.795, 0.93, 1.00, 1.045, 1.08, 1.10, 1.14,
    1.175, 1.21, 1.25, 1.265, 1.28, 1.295, 1.305, 1.315, 1.33, 1.335,
    1.345, 1.35, 1.36, 1.365, 1.37,
]
_FIG_5_6_MU1_LB10 = _FIG_5_6_MU1_BAND + [
    0.49, 0.62, 0.715, 0.795, 0.93, 1.02, 1.085, 1.135, 1.18, 1.265,
    1.325, 1.39, 1.455, 1.49, 1.515, 1.545, 1.57, 1.595, 1.62, 1.635,
    1.645, 1.655, 1.67, 1.675, 1.685,
]
# H/B 1.5 to 20, where the Infinite curve ends
_FIG_5_6_MU1_INFINITE = _FIG_5_6_MU1_BAND + [
    0.49, 0.62, 0.715, 0.795, 0.93, 1.02, 1.12, 1.195, 1.255, 1.345,
    1.425, 1.535, 1.67,
]
_FIG_5_6_HB_INFINITE_MAX = 20.0

_FIG_5_6_LB = [1.0, 2.0, 5.0, 10.0]  # the Square, L/B = 2, 5 and 10 curves
_FIG_5_6_MU1_CURVES = [
    _FIG_5_6_MU1_SQUARE, _FIG_5_6_MU1_LB2, _FIG_5_6_MU1_LB5,
    _FIG_5_6_MU1_LB10,
]


def _fig_5_6_is_infinite(L_over_B) -> bool:
    """True if *L_over_B* names the Infinite curve of Figure 5-6(a)."""
    if isinstance(L_over_B, str):
        return L_over_B.lower().strip() in ("infinite", "infinity", "inf")
    return math.isinf(L_over_B) and L_over_B > 0.0


def figure_5_6_mu1(
    H_over_B: float, L_over_B, nu: float = 0.5
) -> float:
    """Influence factor mu1 (dimensionless) for the problem geometry in the elastic settlement s = mu0 mu1 q0 B / Es (Equation 5-5), read from Figure 5-6(a) at H/B and L/B, for Poisson's ratio 0.5 only.

    Figure 5-6, "Elastic Influence Factors for nu = 0.5 for (a) mu1
    (after Giroud 1972) and (b) mu0 (after Burland 1970)".  Panel (a)
    plots mu1 against H/B (0.1 to 1000, logarithmic) with one curve
    each for Square, L/B = 2, L/B = 5, L/B = 10 and Infinite; the
    Infinite curve is drawn to H/B = 20 only.  At large H/B the curves
    level off near 0.71 (Square), 0.975 (L/B = 2), 1.37 (L/B = 5) and
    1.685 (L/B = 10).

    This function interpolates between points read off those curves,
    linearly in log(H/B) along a curve and linearly in L/B between two
    printed curves.  Where a curve stands alone the reading is good to
    about +/-0.01.  Below H/B of about 1.5 the five curves run together
    in one band and cannot be told apart on the print; the value
    returned there is the middle of the band, +/-0.03, whatever the
    L/B.  The same holds for L/B of 5 and more up to H/B = 5.

    The manual notes (p. 229) that the zone that contributes to
    settlement typically has a thickness of 4B to 5B below the loaded
    area, so the use of H/B ratios greater than 4 to 5 may overestimate
    settlement, and that the user of any mu1 chart must check whether a
    (1 - nu^2) term is included and what nu was assumed.

    Parameters
    ----------
    H_over_B : float
        Ratio of the thickness H of the layer below the load to the
        width B of the load, from 0.1 to 1000 (to 20 on the Infinite
        curve).
    L_over_B : float or str
        Ratio of the length L of the load to its width B: 1 (the
        Square curve) to 10, or ``"infinite"`` for the Infinite curve.
        A ratio above 10 is refused: it lies between the L/B = 10 and
        Infinite curves, and the figure gives nothing to interpolate
        with.
    nu : float, optional
        Poisson's ratio.  Must be 0.5, the only value the figure is
        drawn for (default 0.5).

    Returns
    -------
    float
        Influence factor mu1 (dimensionless).

    Raises
    ------
    ValueError
        If *nu* is not 0.5, *H_over_B* is outside 0.1 to 1000 (or above
        20 on the Infinite curve), or *L_over_B* is below 1, or above 10
        and not infinite.

    References
    ----------
    UFS 3-220-10, Soil Mechanics (DM 7.1), 16 Jan 2026,
    Chapter 5, Figure 5-6(a), p. 230 (after Giroud 1972).
    """
    if abs(nu - 0.5) > 1e-9:
        raise ValueError(
            "nu must be 0.5: Figure 5-6 (UFS 3-220-10 p. 230) is drawn "
            "for a Poisson's ratio of 0.5 only."
        )
    if H_over_B <= 0.0:
        raise ValueError("H_over_B must be positive.")
    if H_over_B < _FIG_5_6_HB[0] or H_over_B > _FIG_5_6_HB[-1]:
        raise ValueError(
            "H_over_B is outside 0.1 to 1000, the H/B axis of Figure "
            "5-6(a) (UFS 3-220-10 p. 230)."
        )
    log_hb = math.log10(H_over_B)

    if _fig_5_6_is_infinite(L_over_B):
        if H_over_B > _FIG_5_6_HB_INFINITE_MAX:
            raise ValueError(
                "H_over_B is above 20, where the Infinite curve of "
                "Figure 5-6(a) (UFS 3-220-10 p. 230) ends."
            )
        n = len(_FIG_5_6_MU1_INFINITE)
        return _linterp(log_hb, _FIG_5_6_LOG_HB[:n], _FIG_5_6_MU1_INFINITE)

    if isinstance(L_over_B, str):
        key = L_over_B.lower().strip()
        if key == "square":
            L_over_B = 1.0
        else:
            try:
                L_over_B = float(key)
            except ValueError:
                raise ValueError(
                    f"Unknown L_over_B '{L_over_B}'. Give a ratio from 1 "
                    "to 10, or 'infinite'."
                ) from None
    if L_over_B < 1.0:
        raise ValueError("L_over_B must be >= 1.0.")
    if L_over_B > _FIG_5_6_LB[-1]:
        raise ValueError(
            "L_over_B is above 10 and not infinite: Figure 5-6(a) (UFS "
            "3-220-10 p. 230) prints curves for Square, L/B = 2, 5, 10 "
            "and Infinite, and gives nothing to interpolate with between "
            "the last two. Use 10 or 'infinite' and say which."
        )
    values = [
        _linterp(log_hb, _FIG_5_6_LOG_HB, curve)
        for curve in _FIG_5_6_MU1_CURVES
    ]
    return _linterp(L_over_B, _FIG_5_6_LB, values)


# ===========================================================================
# PLOT FUNCTIONS: Reproduce UFC Figures from Digitised Data
# ===========================================================================

def plot_figure_5_16(Tv=None, U=None, ax=None, show=True, **kwargs):
    """Reproduce UFC Figure 5-16: Average Degree of Consolidation vs Tv.

    Plots the Terzaghi (1943) consolidation curve from analytical
    equations.  Optionally highlights a query point.

    Parameters
    ----------
    Tv : float, optional
        Time factor query point.  Computes and marks the corresponding U.
    U : float, optional
        Degree of consolidation (%) query point.  Computes and marks
        the corresponding Tv.  Ignored if *Tv* is also provided.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on.  Creates a new figure if None.
    show : bool, optional
        If True, calls plt.show().  Default True.

    Returns
    -------
    matplotlib.axes.Axes
    """
    from geotech_references._plotting import get_pyplot, setup_engineering_plot
    plt = get_pyplot()
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    # Generate smooth analytical curve
    u_vals = [i * 0.5 for i in range(0, 199)]  # 0 to 99.0 %
    tv_vals = [figure_5_16_Tv_from_U(u) for u in u_vals]
    ax.plot(tv_vals, u_vals, 'b-', linewidth=1.5, label='Terzaghi (1943)')

    # Mark known reference points
    ref_U = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    ref_Tv = [figure_5_16_Tv_from_U(u) for u in ref_U]
    ax.plot(ref_Tv, ref_U, 'ko', markersize=4, label='Reference points')

    # Query point
    if Tv is not None:
        u_q = figure_5_16_U_from_Tv(Tv)
        ax.plot(Tv, u_q, 's', color='red', markersize=10, zorder=5,
                label=f'Tv={Tv:.3f} → U={u_q:.1f}%')
        ax.axhline(u_q, color='red', linestyle=':', alpha=0.4)
        ax.axvline(Tv, color='red', linestyle=':', alpha=0.4)
    elif U is not None:
        tv_q = figure_5_16_Tv_from_U(U)
        ax.plot(tv_q, U, 's', color='red', markersize=10, zorder=5,
                label=f'U={U:.1f}% → Tv={tv_q:.3f}')
        ax.axhline(U, color='red', linestyle=':', alpha=0.4)
        ax.axvline(tv_q, color='red', linestyle=':', alpha=0.4)

    ax.legend(fontsize=8)
    setup_engineering_plot(
        ax, 'Figure 5-16: Average Degree of Consolidation',
        'Time Factor, Tv', 'Average Degree of Consolidation, U (%)')
    if show:
        plt.tight_layout()
        plt.show()
    return ax


def plot_figure_5_6_mu0(D_over_B=None, ax=None, show=True, **kwargs):
    """Reproduce UFC Figure 5-6(b): Influence Factor mu0 vs D/B (nu = 0.5).

    Plots the points read off the mu0 curve of Figure 5-6(b) (after
    Burland 1970).

    Parameters
    ----------
    D_over_B : float, optional
        Query point (0 to 20).  If provided, highlights the
        interpolated mu0.
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

    # The read-off curve
    ax.plot(_FIG_5_6_DB, _FIG_5_6_MU0, 'b-', linewidth=1.5,
            label='Curve of Figure 5-6(b) (after Burland 1970)')

    # Query point
    if D_over_B is not None:
        mu0_q = figure_5_6_mu0(D_over_B)
        ax.plot(D_over_B, mu0_q, 's', color='red', markersize=10, zorder=5,
                label=f'D/B={D_over_B:.2f} → μ₀={mu0_q:.3f}')
        ax.axhline(mu0_q, color='red', linestyle=':', alpha=0.4)
        ax.axvline(D_over_B, color='red', linestyle=':', alpha=0.4)

    ax.set_xlim(0, 20)
    ax.set_ylim(0.85, 1.0)
    ax.legend(fontsize=8)
    setup_engineering_plot(
        ax, 'Figure 5-6(b): Influence Factor, μ₀ (ν = 0.5)',
        'D / B', 'μ₀')
    if show:
        plt.tight_layout()
        plt.show()
    return ax


def plot_figure_5_6_mu1(H_over_B=None, L_over_B=None, nu=0.5,
                         ax=None, show=True, **kwargs):
    """Reproduce UFC Figure 5-6(a): Influence Factor mu1 vs H/B (nu = 0.5).

    Plots the points read off the five mu1 curves of Figure 5-6(a)
    (after Giroud 1972): Square, L/B = 2, 5, 10 and Infinite.

    Parameters
    ----------
    H_over_B : float, optional
        Query H/B.  If provided together with *L_over_B*, highlights
        the interpolated mu1 on the plot.
    L_over_B : float or str, optional
        Query L/B (1 to 10, or "infinite").  Required if *H_over_B* is
        given.
    nu : float, optional
        Poisson's ratio.  Must be 0.5, the only value the figure is
        drawn for (default 0.5).
    ax : matplotlib.axes.Axes, optional
        Axes to plot on.
    show : bool, optional
        If True, calls plt.show().

    Returns
    -------
    matplotlib.axes.Axes
    """
    if abs(nu - 0.5) > 1e-9:
        raise ValueError(
            "nu must be 0.5: Figure 5-6 (UFS 3-220-10 p. 230) is drawn "
            "for a Poisson's ratio of 0.5 only."
        )
    from geotech_references._plotting import get_pyplot, setup_engineering_plot
    plt = get_pyplot()
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    # One curve per printed L/B
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    labels = ['Square', 'L/B = 2', 'L/B = 5', 'L/B = 10', 'Infinite']
    curves = _FIG_5_6_MU1_CURVES + [_FIG_5_6_MU1_INFINITE]
    for j, curve in enumerate(curves):
        ax.plot(_FIG_5_6_HB[:len(curve)], curve, '-',
                color=colors[j % len(colors)], linewidth=1.5,
                label=labels[j])

    # Query point
    if H_over_B is not None and L_over_B is not None:
        mu1_q = figure_5_6_mu1(H_over_B, L_over_B, nu)
        ax.plot(H_over_B, mu1_q, 's', color='red', markersize=10, zorder=5,
                label=f'H/B={H_over_B:g}, L/B={L_over_B} → μ₁={mu1_q:.3f}')
        ax.axhline(mu1_q, color='red', linestyle=':', alpha=0.4)
        ax.axvline(H_over_B, color='red', linestyle=':', alpha=0.4)

    ax.set_xscale('log')
    ax.set_xlim(0.1, 1000)
    ax.set_ylim(0, 2.0)
    ax.legend(fontsize=8, loc='upper left')
    setup_engineering_plot(
        ax, 'Figure 5-6(a): Influence Factor, μ₁ (ν = 0.5)',
        'H / B', 'μ₁')
    if show:
        plt.tight_layout()
        plt.show()
    return ax
