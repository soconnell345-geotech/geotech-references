"""California Trenching and Shoring Manual (Caltrans) design equations.

Earth pressure, apparent earth pressure (AEP), stability, and heave equations
from the Caltrans Trenching and Shoring Manual (June 2011, Revision 2 - July
2025). Units are the manual's native US customary units (psf, pcf, ft, deg).
Angles are degrees on input/output unless noted. Each function cites the source
equation and PDF page.
"""

import math


# ============================================================================
# Chapter 4 — classical earth pressure coefficients
# ============================================================================

def rankine_ka(phi_deg, beta_deg: float = 0.0) -> dict:
    """Rankine active earth pressure coefficient Ka (Eq. 4-3-11 / 4-3-16).

    For level backfill (beta = 0): Ka = tan^2(45 - phi/2). For a sloping
    cohesionless backfill at angle beta (<= phi), the Rankine sloped-backfill
    form is used:

        Ka = cos(beta) * [cos(beta) - sqrt(cos^2(beta) - cos^2(phi))]
                       / [cos(beta) + sqrt(cos^2(beta) - cos^2(phi))]

    Parameters
    ----------
    phi_deg : float
        Effective soil friction angle phi (deg), > 0.
    beta_deg : float, optional
        Backfill slope angle beta (deg) above horizontal. Default 0 (level).
        Must satisfy beta <= phi.

    Returns
    -------
    dict
        {'phi_deg', 'beta_deg', 'ka', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If phi_deg <= 0 or beta_deg > phi_deg.
    """
    if phi_deg <= 0:
        raise ValueError(f"phi_deg must be > 0, got {phi_deg}")
    if beta_deg > phi_deg:
        raise ValueError(
            f"beta_deg ({beta_deg}) must be <= phi_deg ({phi_deg}) for Rankine "
            "active pressure on sloping backfill."
        )
    phi = math.radians(phi_deg)
    if abs(beta_deg) < 1e-9:
        ka = math.tan(math.radians(45.0 - phi_deg / 2.0)) ** 2
        eq = "4-3-11"
    else:
        b = math.radians(beta_deg)
        root = math.sqrt(math.cos(b) ** 2 - math.cos(phi) ** 2)
        ka = math.cos(b) * (math.cos(b) - root) / (math.cos(b) + root)
        eq = "4-3-16"
    return {
        "phi_deg": phi_deg, "beta_deg": beta_deg, "ka": round(ka, 4),
        "equation": eq,
        "reference": "Caltrans T&S Manual Section 4-3 (Rankine)",
        "pdf_page": 58, "printed_page": "4-8",
    }


def rankine_kp(phi_deg, beta_deg: float = 0.0) -> dict:
    """Rankine passive earth pressure coefficient Kp (Eq. 4-3-12 / 4-3-19).

    For level backfill: Kp = tan^2(45 + phi/2). The manual warns NOT to use the
    Rankine passive form for a positive backfill slope (beta > 0) — it gives the
    same Kp for +beta and -beta, which is incorrect — and to avoid it whenever
    significant wall friction can develop. Use the Caquot-Kerisel log-spiral
    chart (Figure 4-20, Matrix 4-1) instead for those cases.

    Parameters
    ----------
    phi_deg : float
        Effective soil friction angle phi (deg), > 0.
    beta_deg : float, optional
        Backfill slope angle beta (deg). Default 0 (level). A warning is added
        if beta != 0.

    Returns
    -------
    dict
        {'phi_deg', 'beta_deg', 'kp', 'equation', 'warning', 'reference', ...}

    Raises
    ------
    ValueError
        If phi_deg <= 0 or |beta_deg| > phi_deg.
    """
    if phi_deg <= 0:
        raise ValueError(f"phi_deg must be > 0, got {phi_deg}")
    if abs(beta_deg) > phi_deg:
        raise ValueError(f"|beta_deg| must be <= phi_deg ({phi_deg}).")
    phi = math.radians(phi_deg)
    warning = None
    if abs(beta_deg) < 1e-9:
        kp = math.tan(math.radians(45.0 + phi_deg / 2.0)) ** 2
        eq = "4-3-12"
    else:
        b = math.radians(beta_deg)
        root = math.sqrt(math.cos(b) ** 2 - math.cos(phi) ** 2)
        kp = math.cos(b) * (math.cos(b) + root) / (math.cos(b) - root)
        eq = "4-3-19"
        warning = (
            "Rankine passive Kp should NOT be used for sloping backfill "
            "(beta != 0); it is identical for +beta and -beta. Use the "
            "Caquot-Kerisel log-spiral chart (Figure 4-20)."
        )
    out = {
        "phi_deg": phi_deg, "beta_deg": beta_deg, "kp": round(kp, 4),
        "equation": eq,
        "reference": "Caltrans T&S Manual Section 4-3 (Rankine)",
        "pdf_page": 58, "printed_page": "4-8",
    }
    if warning:
        out["warning"] = warning
    return out


def coulomb_ka(phi_deg, delta_deg: float = 0.0, beta_deg: float = 0.0,
               omega_deg: float = 0.0) -> dict:
    """Coulomb active earth pressure coefficient Ka (Eq. 4-3-22).

    Coulomb active coefficient including wall friction delta, backfill slope
    beta, and wall batter omega (angle of the wall face from vertical):

        Ka = cos^2(phi - omega) /
             [ cos^2(omega) cos(omega + delta) *
               (1 + sqrt( sin(phi+delta) sin(phi-beta) /
                          (cos(omega+delta) cos(omega-beta)) ))^2 ]

    Parameters
    ----------
    phi_deg : float
        Soil friction angle phi (deg), > 0.
    delta_deg : float, optional
        Wall friction angle delta (deg). Default 0. See Table 4-2.
    beta_deg : float, optional
        Backfill slope angle beta (deg). Default 0.
    omega_deg : float, optional
        Wall batter omega (deg) from vertical. Default 0 (vertical wall).

    Returns
    -------
    dict
        {'phi_deg', 'delta_deg', 'beta_deg', 'omega_deg', 'ka', 'equation',
         'reference', ...}

    Raises
    ------
    ValueError
        If phi_deg <= 0 or the geometry is invalid (negative radicand).
    """
    if phi_deg <= 0:
        raise ValueError(f"phi_deg must be > 0, got {phi_deg}")
    phi = math.radians(phi_deg)
    d = math.radians(delta_deg)
    b = math.radians(beta_deg)
    w = math.radians(omega_deg)
    num_root = math.sin(phi + d) * math.sin(phi - b)
    den_root = math.cos(w + d) * math.cos(w - b)
    if den_root == 0 or num_root / den_root < 0:
        raise ValueError("Invalid geometry for Coulomb Ka (negative radicand).")
    root = math.sqrt(num_root / den_root)
    ka = (math.cos(phi - w) ** 2) / (
        math.cos(w) ** 2 * math.cos(w + d) * (1 + root) ** 2
    )
    return {
        "phi_deg": phi_deg, "delta_deg": delta_deg, "beta_deg": beta_deg,
        "omega_deg": omega_deg, "ka": round(ka, 4), "equation": "4-3-22",
        "reference": "Caltrans T&S Manual Section 4-3.02B (Coulomb)",
        "pdf_page": 62, "printed_page": "4-12",
    }


def at_rest_k0(phi_deg, beta_deg: float = 0.0, ocr: float = 1.0) -> dict:
    """At-rest earth pressure coefficient K0 (Eq. 4-3-14 / 4-3-15).

    For normally consolidated soils with a vertical wall (Jaky form with the
    manual's sloping-backfill modifier):

        K0 = (1 - sin(phi)) * (1 - sin(beta))     (Eq. 4-3-14)

    For over-consolidated soils with level backfill and a vertical wall:

        K0 = (1 - sin(phi)) * OCR^sin(phi)        (Eq. 4-3-15)

    Parameters
    ----------
    phi_deg : float
        Effective soil friction angle phi (deg), > 0.
    beta_deg : float, optional
        Backfill slope angle beta (deg). Default 0. Used only when ocr == 1.
    ocr : float, optional
        Over-consolidation ratio. Default 1.0 (normally consolidated). If > 1,
        the OCR form (Eq. 4-3-15) is used (level backfill assumed).

    Returns
    -------
    dict
        {'phi_deg', 'beta_deg', 'ocr', 'k0', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If phi_deg <= 0 or ocr < 1.
    """
    if phi_deg <= 0:
        raise ValueError(f"phi_deg must be > 0, got {phi_deg}")
    if ocr < 1.0:
        raise ValueError(f"ocr must be >= 1, got {ocr}")
    phi = math.radians(phi_deg)
    if ocr > 1.0:
        k0 = (1 - math.sin(phi)) * (ocr ** math.sin(phi))
        eq = "4-3-15"
    else:
        k0 = (1 - math.sin(phi)) * (1 - math.sin(math.radians(beta_deg)))
        eq = "4-3-14"
    return {
        "phi_deg": phi_deg, "beta_deg": beta_deg, "ocr": ocr,
        "k0": round(k0, 4), "equation": eq,
        "reference": "Caltrans T&S Manual Section 4-3.01 (at-rest K0)",
        "pdf_page": 59, "printed_page": "4-9",
        "note": "The at-rest coefficient equations in the manual are empirical.",
    }


def log_spiral_passive_kp(kp_initial, reduction_factor_r) -> dict:
    """Final log-spiral passive coefficient Kp' = R * Kp (Section 4-6, Fig 4-20).

    The Caquot & Kerisel (1948) log-spiral passive earth pressure procedure:
    read the initial Kp from Figure 4-20 using phi and beta/phi, then multiply
    by the wall-friction reduction factor R (from delta/phi; see Matrix 4-1 /
    ``tables.matrix_4_1_passive_reduction_factor``):

        Kp' = R * Kp

    Parameters
    ----------
    kp_initial : float
        Initial passive coefficient Kp read from Figure 4-20 (delta = phi).
    reduction_factor_r : float
        Wall-friction reduction factor R = Kp(delta)/Kp(delta=phi) (<= 1).

    Returns
    -------
    dict
        {'kp_initial', 'reduction_factor_r', 'kp_prime', 'reference', ...}

    Raises
    ------
    ValueError
        If kp_initial <= 0 or R is not in (0, 1].
    """
    if kp_initial <= 0:
        raise ValueError(f"kp_initial must be > 0, got {kp_initial}")
    if not (0 < reduction_factor_r <= 1):
        raise ValueError(f"reduction_factor_r must be in (0, 1], got {reduction_factor_r}")
    return {
        "kp_initial": kp_initial,
        "reduction_factor_r": reduction_factor_r,
        "kp_prime": round(kp_initial * reduction_factor_r, 4),
        "reference": "Caltrans T&S Manual Section 4-6 / Figure 4-20 (Caquot & Kerisel 1948)",
        "pdf_page": 79, "printed_page": "4-29",
    }


# ============================================================================
# Lateral pressure resultant and apparent active coefficient (cohesive)
# ============================================================================

def lateral_earth_pressure_resultant(gamma_pcf, height_ft, k) -> dict:
    """Triangular lateral earth pressure resultant P (Eq. 4-3-2 / 4-3-17).

        sigma_h = gamma * h * K      (linear with depth)
        P = 0.5 * gamma * h^2 * K    (acts at h/3 above the base)

    Parameters
    ----------
    gamma_pcf : float
        Soil unit weight gamma (pcf).
    height_ft : float
        Height h of the pressure surface (ft).
    k : float
        Earth pressure coefficient K (Ka, Kp, or K0).

    Returns
    -------
    dict
        {'gamma_pcf', 'height_ft', 'k', 'sigma_h_base_psf', 'resultant_plf',
         'resultant_height_ft', 'reference', ...}

    Raises
    ------
    ValueError
        If gamma_pcf <= 0, height_ft < 0, or k < 0.
    """
    if gamma_pcf <= 0:
        raise ValueError(f"gamma_pcf must be > 0, got {gamma_pcf}")
    if height_ft < 0:
        raise ValueError(f"height_ft must be >= 0, got {height_ft}")
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")
    sigma_h = gamma_pcf * height_ft * k
    p = 0.5 * gamma_pcf * height_ft ** 2 * k
    return {
        "gamma_pcf": gamma_pcf, "height_ft": height_ft, "k": k,
        "sigma_h_base_psf": round(sigma_h, 2),
        "resultant_plf": round(p, 2),
        "resultant_height_ft": round(height_ft / 3.0, 3),
        "equation": "4-3-2 / 4-3-17",
        "reference": "Caltrans T&S Manual Section 4-3",
        "pdf_page": 56, "printed_page": "4-6",
    }


def apparent_active_coefficient(sigma_a_psf, gamma_pcf, height_ft) -> dict:
    """Apparent active earth pressure coefficient Kapparent (Eq. 4-4-16).

    For shoring supporting COHESIVE backfill, the tension-crack zone is ignored
    and a modified (apparent) coefficient is used along the full wall height:

        Kapparent = sigma_a / (gamma * h)   and   Kapparent >= 0.25

    The 0.25 floor must be met unless a lower value is justified by multiple lab
    tests for c, the excavation time frame, and other site conditions.

    Parameters
    ----------
    sigma_a_psf : float
        Active horizontal stress sigma_a at the base of the pressure diagram
        (psf), from the Bell cohesive solution (Eq. 4-4-4..4-4-10).
    gamma_pcf : float
        Soil unit weight gamma (pcf).
    height_ft : float
        Wall height h / pressure-surface height (ft).

    Returns
    -------
    dict
        {'sigma_a_psf', 'gamma_pcf', 'height_ft', 'kapparent_computed',
         'kapparent_design', 'floor_governs', 'reference', ...}

    Raises
    ------
    ValueError
        If gamma_pcf <= 0 or height_ft <= 0.
    """
    if gamma_pcf <= 0:
        raise ValueError(f"gamma_pcf must be > 0, got {gamma_pcf}")
    if height_ft <= 0:
        raise ValueError(f"height_ft must be > 0, got {height_ft}")
    k_computed = sigma_a_psf / (gamma_pcf * height_ft)
    floor_governs = k_computed < 0.25
    k_design = max(k_computed, 0.25)
    return {
        "sigma_a_psf": sigma_a_psf,
        "gamma_pcf": gamma_pcf,
        "height_ft": height_ft,
        "kapparent_computed": round(k_computed, 4),
        "kapparent_design": round(k_design, 4),
        "minimum": 0.25,
        "floor_governs": floor_governs,
        "equation": "4-4-16",
        "reference": "Caltrans T&S Manual Section 4-4 (Eq. 4-4-16)",
        "pdf_page": 71, "printed_page": "4-21",
        "note": ("Kapparent must be >= 0.25 unless a lower value is justified by "
                 "lab tests for c and the excavation conditions."),
    }


def tension_crack_depth(cohesion_psf, gamma_pcf, ka) -> dict:
    """Depth of the cohesive tension crack zone hcr (Eq. 4-4-13).

        hcr = 2 c / (gamma * sqrt(Ka))

    Parameters
    ----------
    cohesion_psf : float
        Soil cohesion c (psf).
    gamma_pcf : float
        Soil unit weight gamma (pcf).
    ka : float
        Active earth pressure coefficient Ka (> 0).

    Returns
    -------
    dict
        {'cohesion_psf', 'gamma_pcf', 'ka', 'hcr_ft', 'reference', ...}

    Raises
    ------
    ValueError
        If gamma_pcf <= 0 or ka <= 0.
    """
    if gamma_pcf <= 0:
        raise ValueError(f"gamma_pcf must be > 0, got {gamma_pcf}")
    if ka <= 0:
        raise ValueError(f"ka must be > 0, got {ka}")
    hcr = 2.0 * cohesion_psf / (gamma_pcf * math.sqrt(ka))
    return {
        "cohesion_psf": cohesion_psf, "gamma_pcf": gamma_pcf, "ka": ka,
        "hcr_ft": round(hcr, 3), "equation": "4-4-13",
        "reference": "Caltrans T&S Manual Section 4-4 (Eq. 4-4-13)",
        "pdf_page": 68, "printed_page": "4-18",
    }


# ============================================================================
# Chapter 4-5 — maximum allowable embankment slope angle (c-phi soil)
# ============================================================================

def max_allowable_slope_angle(phi_deg, cohesion_psf, gamma_pcf, height_ft) -> dict:
    """Maximum allowable embankment slope angle for c-phi soil (Eq. 4-5-1).

    None of the earth-pressure theories work when the slope angle beta exceeds
    the friction angle phi; cohesion lets a stable slope stand steeper. The
    manual's limit (ASCE JGGE Feb 1997) is:

        sin(beta) <= sin(phi) + c / (gamma * h)        (Eq. 4-5-1)

    i.e. beta_max = arcsin( sin(phi) + c/(gamma*h) ), capped at 90 deg.

    Parameters
    ----------
    phi_deg : float
        Soil friction angle phi (deg), >= 0.
    cohesion_psf : float
        Soil cohesion c (psf), >= 0.
    gamma_pcf : float
        Soil unit weight gamma (pcf), > 0.
    height_ft : float
        Slope / excavation height h (ft), > 0.

    Returns
    -------
    dict
        {'phi_deg', 'cohesion_psf', 'gamma_pcf', 'height_ft',
         'sin_beta_max', 'beta_max_deg', 'vertical', 'reference', ...}

    Raises
    ------
    ValueError
        If gamma_pcf <= 0 or height_ft <= 0.
    """
    if gamma_pcf <= 0:
        raise ValueError(f"gamma_pcf must be > 0, got {gamma_pcf}")
    if height_ft <= 0:
        raise ValueError(f"height_ft must be > 0, got {height_ft}")
    sin_beta = math.sin(math.radians(phi_deg)) + cohesion_psf / (gamma_pcf * height_ft)
    vertical = sin_beta >= 1.0
    beta_max = 90.0 if vertical else math.degrees(math.asin(sin_beta))
    return {
        "phi_deg": phi_deg, "cohesion_psf": cohesion_psf,
        "gamma_pcf": gamma_pcf, "height_ft": height_ft,
        "sin_beta_max": round(sin_beta, 4),
        "beta_max_deg": round(beta_max, 2),
        "vertical": vertical,
        "equation": "4-5-1",
        "reference": "Caltrans T&S Manual Section 4-5 (Eq. 4-5-1, ASCE JGGE Feb 1997)",
        "pdf_page": 72, "printed_page": "4-22",
        "note": ("If sin(phi) + c/(gamma*h) >= 1 the soil can stand vertical for "
                 "the given height. This is an estimate; a slope-stability "
                 "analysis is still recommended."),
    }


# ============================================================================
# Chapter 5 — surcharge loads
# ============================================================================

def uniform_surcharge_pressure(q_psf, k) -> dict:
    """Constant horizontal pressure from a uniform surcharge (Eq. 5-1-1).

        sigma_h = K * Q

    where K is Ka (active) or K0 (at-rest) and Q is the uniform surcharge over
    the active failure wedge.

    Parameters
    ----------
    q_psf : float
        Uniform surcharge Q applied to the backfill surface (psf).
    k : float
        Lateral earth pressure coefficient (Ka for active, K0 for at-rest).

    Returns
    -------
    dict
        {'q_psf', 'k', 'sigma_h_psf', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If q_psf < 0 or k < 0.
    """
    if q_psf < 0:
        raise ValueError(f"q_psf must be >= 0, got {q_psf}")
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")
    return {
        "q_psf": q_psf, "k": k, "sigma_h_psf": round(k * q_psf, 2),
        "equation": "5-1-1",
        "reference": "Caltrans T&S Manual Section 5-1.02 (Eq. 5-1-1)",
        "pdf_page": 84, "printed_page": "5-3",
    }


def minimum_construction_surcharge() -> dict:
    """Minimum lateral construction surcharge (Section 5-1.01).

    A minimum lateral construction surcharge of 72 psf (sigma_h) must always be
    applied to the shoring system, over a minimum depth of 10 ft (Hs) below the
    top of the retained soil.

    Returns
    -------
    dict
        {'sigma_h_psf', 'min_depth_ft', 'reference', ...}
    """
    return {
        "sigma_h_psf": 72.0,
        "min_depth_ft": 10.0,
        "reference": "Caltrans T&S Manual Section 5-1.01",
        "pdf_page": 83, "printed_page": "5-2",
        "note": "Applied as a uniform 72 psf over the top 10 ft of the retained soil.",
    }


def boussinesq_strip_load_pressure(q_psf, alpha_deg, beta_deg) -> dict:
    """Horizontal pressure from a Boussinesq/Wayne C. Teng strip load (Section 5-1.03A).

    For a strip surcharge (e.g. a parallel highway/railroad) the horizontal
    pressure at a point on the wall is the Wayne C. Teng / Boussinesq form:

        sigma_h = (q / pi) * [ beta_R - sin(beta) cos(2*alpha) ]

    where alpha is the angle from the wall to the center of the strip, beta is
    the angle subtended by the strip at the point, and beta_R is beta in radians.

    Parameters
    ----------
    q_psf : float
        Strip surcharge intensity q (psf).
    alpha_deg : float
        Angle alpha (deg) from the wall to the center of the surcharge strip.
    beta_deg : float
        Angle beta (deg) subtended by the strip at the point of interest.

    Returns
    -------
    dict
        {'q_psf', 'alpha_deg', 'beta_deg', 'sigma_h_psf', 'reference', ...}

    Raises
    ------
    ValueError
        If q_psf < 0 or beta_deg <= 0.
    """
    if q_psf < 0:
        raise ValueError(f"q_psf must be >= 0, got {q_psf}")
    if beta_deg <= 0:
        raise ValueError(f"beta_deg must be > 0, got {beta_deg}")
    beta_r = math.radians(beta_deg)
    alpha = math.radians(alpha_deg)
    sigma_h = (q_psf / math.pi) * (beta_r - math.sin(beta_r) * math.cos(2 * alpha))
    return {
        "q_psf": q_psf, "alpha_deg": alpha_deg, "beta_deg": beta_deg,
        "sigma_h_psf": round(sigma_h, 3),
        "reference": "Caltrans T&S Manual Section 5-1.03A (Wayne C. Teng / Boussinesq)",
        "pdf_page": 85, "printed_page": "5-4",
        "note": "beta_R is beta in radians; the 2D elastic (Boussinesq) strip-load form.",
    }


# ============================================================================
# Chapter 8 — apparent earth pressure (AEP) for restrained walls
# ============================================================================

def aep_single_level_cohesionless(gamma_pcf, height_ft, ka) -> dict:
    """Trapezoidal AEP maximum ordinate, single-level braced/anchored wall,
    cohesionless soil (Eq. 8-2-1..8-2-5; Fig 8-2).

    The triangular Rankine/Coulomb distribution (resultant P = 0.5*gamma*H^2*Ka)
    is converted to a trapezoid whose resultant PT = 1.3 P. For a single level of
    anchors/braces with the trapezoid spanning 0.2H..0.8H (the manual's f-factor
    that gives PT = 0.65*gamma*H^2*Ka = 1.3 P), the maximum ordinate is:

        sigma_a = PT / (0.8 * H) = 0.65*gamma*H^2*Ka / (0.8 H)

    Parameters
    ----------
    gamma_pcf : float
        Soil unit weight gamma (pcf).
    height_ft : float
        Wall height H (ft).
    ka : float
        Active earth pressure coefficient Ka.

    Returns
    -------
    dict
        {'gamma_pcf', 'height_ft', 'ka', 'p_triangular_plf', 'pt_trapezoidal_plf',
         'sigma_a_psf', 'reference', ...}

    Raises
    ------
    ValueError
        If gamma_pcf <= 0, height_ft <= 0, or ka < 0.
    """
    if gamma_pcf <= 0:
        raise ValueError(f"gamma_pcf must be > 0, got {gamma_pcf}")
    if height_ft <= 0:
        raise ValueError(f"height_ft must be > 0, got {height_ft}")
    if ka < 0:
        raise ValueError(f"ka must be >= 0, got {ka}")
    p = 0.5 * gamma_pcf * height_ft ** 2 * ka
    pt = 1.3 * p
    sigma_a = pt / (0.8 * height_ft)
    return {
        "gamma_pcf": gamma_pcf, "height_ft": height_ft, "ka": ka,
        "p_triangular_plf": round(p, 2),
        "pt_trapezoidal_plf": round(pt, 2),
        "sigma_a_psf": round(sigma_a, 2),
        "equation": "8-2-1..8-2-5",
        "reference": "Caltrans T&S Manual Section 8-2 (Fig 8-2)",
        "pdf_page": 153, "printed_page": "8-3",
        "note": ("Trapezoid spans 0.2H to 0.8H; PT = 1.3 P. sigma_a here uses the "
                 "0.8H trapezoid base height."),
    }


def aep_multi_level_cohesionless(gamma_pcf, height_ft, ka, h1_ft, hn1_ft) -> dict:
    """Trapezoidal AEP maximum ordinate, multi-level braced/anchored wall,
    cohesionless soil (Eq. 8-2-6; Fig 8-3).

        sigma_a = 1.3 P / [ H - (1/3)(H1 + Hn+1) ]

    where P = 0.5*gamma*H^2*Ka, H1 is the distance from the ground surface to the
    uppermost anchor level, and Hn+1 is the distance from the bottom of the wall
    to the lowermost anchor level.

    Parameters
    ----------
    gamma_pcf : float
        Soil unit weight gamma (pcf).
    height_ft : float
        Wall height H (ft).
    ka : float
        Active earth pressure coefficient Ka.
    h1_ft : float
        Distance H1 from the ground surface to the uppermost anchor/brace (ft).
    hn1_ft : float
        Distance Hn+1 from the bottom of the wall to the lowermost anchor (ft).

    Returns
    -------
    dict
        {'gamma_pcf', 'height_ft', 'ka', 'h1_ft', 'hn1_ft', 'p_triangular_plf',
         'sigma_a_psf', 'reference', ...}

    Raises
    ------
    ValueError
        If inputs are invalid or the denominator is non-positive.
    """
    if gamma_pcf <= 0:
        raise ValueError(f"gamma_pcf must be > 0, got {gamma_pcf}")
    if height_ft <= 0:
        raise ValueError(f"height_ft must be > 0, got {height_ft}")
    if ka < 0:
        raise ValueError(f"ka must be >= 0, got {ka}")
    denom = height_ft - (h1_ft + hn1_ft) / 3.0
    if denom <= 0:
        raise ValueError(
            "Denominator H - (1/3)(H1 + Hn+1) must be > 0; check H1 and Hn+1."
        )
    p = 0.5 * gamma_pcf * height_ft ** 2 * ka
    sigma_a = 1.3 * p / denom
    return {
        "gamma_pcf": gamma_pcf, "height_ft": height_ft, "ka": ka,
        "h1_ft": h1_ft, "hn1_ft": hn1_ft,
        "p_triangular_plf": round(p, 2),
        "sigma_a_psf": round(sigma_a, 2),
        "equation": "8-2-6",
        "reference": "Caltrans T&S Manual Section 8-2 (Eq. 8-2-6, Fig 8-3)",
        "pdf_page": 154, "printed_page": "8-4",
    }


def stability_number(gamma_pcf, height_ft, cu_psf) -> dict:
    """Stability number Ns = gamma*H / cu (Eq. 8-3-1 / 10-3-1).

    Governs the cohesive AEP envelope selection and the bottom-heave check.
    Ns <= 4: stiff-to-hard clay (use sigma_a = 0.2..0.4 gamma H). Ns >= 6:
    soft-to-medium clay (use sigma_a = Ka gamma H). 4 < Ns < 6: take the larger.
    Heave/slip-circle should be checked when Ns > 6.

    Parameters
    ----------
    gamma_pcf : float
        Total soil unit weight gamma (pcf).
    height_ft : float
        Wall / excavation height H (ft).
    cu_psf : float
        Average undrained shear strength (cohesion) cu (psf), > 0. (cu equals
        the unconfined compressive strength divided by 2 when phi_u = 0.)

    Returns
    -------
    dict
        {'gamma_pcf', 'height_ft', 'cu_psf', 'ns', 'regime', 'reference', ...}

    Raises
    ------
    ValueError
        If cu_psf <= 0 or other inputs invalid.
    """
    if gamma_pcf <= 0:
        raise ValueError(f"gamma_pcf must be > 0, got {gamma_pcf}")
    if height_ft < 0:
        raise ValueError(f"height_ft must be >= 0, got {height_ft}")
    if cu_psf <= 0:
        raise ValueError(f"cu_psf must be > 0, got {cu_psf}")
    ns = gamma_pcf * height_ft / cu_psf
    if ns <= 4:
        regime = "stiff to hard (Ns <= 4): sigma_a = 0.2 to 0.4 * gamma * H"
    elif ns >= 6:
        regime = "soft to medium stiff (Ns >= 6): sigma_a = Ka * gamma * H; check heave"
    else:
        regime = "4 < Ns < 6: use the larger sigma_a of the two cohesive envelopes"
    return {
        "gamma_pcf": gamma_pcf, "height_ft": height_ft, "cu_psf": cu_psf,
        "ns": round(ns, 3), "regime": regime, "equation": "8-3-1 / 10-3-1",
        "reference": "Caltrans T&S Manual Section 8-3 / 10-3",
        "pdf_page": 155, "printed_page": "8-5",
    }


def aep_cohesive_max_ordinate(gamma_pcf, height_ft, ns, factor: float = 0.3,
                              ka=None) -> dict:
    """Trapezoidal AEP maximum ordinate for cohesive backfill (Eq. 8-3-2 / 8-3-3).

    Selects the cohesive AEP envelope from the stability number Ns:
      - Ns <= 4 (stiff to hard): sigma_a = factor * gamma * H, factor in 0.2..0.4
        (Eq. 8-3-2).
      - Ns >= 6 (soft to medium stiff): sigma_a = Ka * gamma * H (Eq. 8-3-3),
        with Ka per FHWA (>= 0.25).
      - 4 < Ns < 6: caller should take the larger of the two; this returns the
        Ns-regime result and notes the rule.

    Parameters
    ----------
    gamma_pcf : float
        Total soil unit weight gamma (pcf).
    height_ft : float
        Wall height H (ft).
    ns : float
        Stability number Ns (= gamma*H/cu); selects the envelope.
    factor : float, optional
        The 0.2-0.4 coefficient for the stiff-hard envelope (Eq. 8-3-2).
        Default 0.3. Best engineering judgment per field conditions.
    ka : float, optional
        Active coefficient Ka for the soft-medium envelope (Eq. 8-3-3, >= 0.25).
        Required when Ns >= 6.

    Returns
    -------
    dict
        {'sigma_a_psf', 'envelope', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If inputs are invalid or Ka is missing when needed.
    """
    if gamma_pcf <= 0:
        raise ValueError(f"gamma_pcf must be > 0, got {gamma_pcf}")
    if height_ft <= 0:
        raise ValueError(f"height_ft must be > 0, got {height_ft}")
    if not (0.2 <= factor <= 0.4):
        raise ValueError("factor (Eq. 8-3-2) must be between 0.2 and 0.4.")

    def stiff():
        return factor * gamma_pcf * height_ft

    def soft(k):
        return k * gamma_pcf * height_ft

    if ns <= 4:
        sigma_a = stiff()
        envelope = f"stiff-hard (Ns<=4): sigma_a = {factor}*gamma*H (Eq. 8-3-2)"
        eq = "8-3-2"
    elif ns >= 6:
        if ka is None:
            raise ValueError("ka is required for the soft-medium envelope (Ns >= 6).")
        if ka < 0.25:
            raise ValueError("Ka must be >= 0.25 (FHWA floor) per Eq. 8-3-4.")
        sigma_a = soft(ka)
        envelope = "soft-medium (Ns>=6): sigma_a = Ka*gamma*H (Eq. 8-3-3)"
        eq = "8-3-3"
    else:
        s1 = stiff()
        s2 = soft(ka) if ka is not None else None
        sigma_a = max(s1, s2) if s2 is not None else s1
        envelope = ("transition 4<Ns<6: take the LARGER of Eq. 8-3-2 and 8-3-3 "
                    "(Ka required for the full comparison)")
        eq = "8-3-2 / 8-3-3"
    return {
        "gamma_pcf": gamma_pcf, "height_ft": height_ft, "ns": ns,
        "factor": factor, "ka": ka,
        "sigma_a_psf": round(sigma_a, 2),
        "envelope": envelope, "equation": eq,
        "reference": "Caltrans T&S Manual Section 8-3",
        "pdf_page": 155, "printed_page": "8-5",
    }


# ============================================================================
# Chapter 10 — bottom heave (Terzaghi / Bjerrum & Eide)
# ============================================================================

def heave_factor_of_safety(cohesion_psf, nc, gamma_pcf, height_ft, width_ft,
                           surcharge_psf: float = 0.0) -> dict:
    """Factor of safety against bottom heave of a braced cut in clay (Eq. 10-3-2..10-3-5).

        Driving force  Q  = W + (0.7B) q - S,
                       W  = gamma * H * (0.7B),  S = c * H
        Resisting      Qu = c * Nc * (0.7B)   (Terzaghi bearing-capacity form)
        FS = Qu / Q  >= 1.5 (recommended minimum)

    Parameters
    ----------
    cohesion_psf : float
        Undrained cohesion c (psf), > 0.
    nc : float
        Bearing capacity factor Nc (Bjerrum & Eide, Fig 10-15; function of H/B
        and L/B).
    gamma_pcf : float
        Soil unit weight gamma (pcf).
    height_ft : float
        Excavation depth H (ft).
    width_ft : float
        Open-excavation width B (ft).
    surcharge_psf : float, optional
        Surcharge q (psf). Default 0.

    Returns
    -------
    dict
        {'driving_force_Q_plf', 'resisting_force_Qu_plf', 'fs', 'adequate',
         'reference', ...}

    Raises
    ------
    ValueError
        If inputs are invalid (non-positive c, gamma, H, B, or Nc).
    """
    if cohesion_psf <= 0:
        raise ValueError(f"cohesion_psf must be > 0, got {cohesion_psf}")
    if nc <= 0:
        raise ValueError(f"nc must be > 0, got {nc}")
    if gamma_pcf <= 0 or height_ft <= 0 or width_ft <= 0:
        raise ValueError("gamma_pcf, height_ft, and width_ft must all be > 0.")
    b07 = 0.7 * width_ft
    w = gamma_pcf * height_ft * b07
    s = cohesion_psf * height_ft
    q_drive = w + b07 * surcharge_psf - s
    qu = cohesion_psf * nc * b07
    if q_drive <= 0:
        fs = float("inf")
    else:
        fs = qu / q_drive
    return {
        "cohesion_psf": cohesion_psf, "nc": nc, "gamma_pcf": gamma_pcf,
        "height_ft": height_ft, "width_ft": width_ft,
        "surcharge_psf": surcharge_psf,
        "weight_W_plf": round(w, 2),
        "cohesion_resistance_S_plf": round(s, 2),
        "driving_force_Q_plf": round(q_drive, 2),
        "resisting_force_Qu_plf": round(qu, 2),
        "fs": (fs if fs == float("inf") else round(fs, 3)),
        "fs_required": 1.5,
        "adequate": fs >= 1.5,
        "equation": "10-3-2..10-3-5",
        "reference": "Caltrans T&S Manual Section 10-3 (Terzaghi; Bjerrum & Eide Nc)",
        "pdf_page": 224, "printed_page": "10-16",
        "note": "Check heave when the stability number Ns = gamma*H/c exceeds 6.",
    }
