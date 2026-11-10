"""GEC-10 figure and equation lookup functions.

Equations and figure correlations from FHWA-NHI-18-024 (GEC-10, 2018 edition),
Drilled Shafts: Construction Procedures and Design Methods.

Note: Several charts from the 2010 edition (e.g., beta vs. depth for sand) were
replaced in the 2018 edition with rational analytical formulas or tables.  Those
legacy charts are NOT reproduced here.  Core drilled shaft computation is in
GeotechStaffEngineer's drilled_shaft and lateral_pile modules.
"""

import math

from geotech_references._interpolation import _linterp

_PA_KPA = 101.325  # atmospheric pressure, kPa


# ============================================================================
# Section 10.3.5.2 — Cohesive Soil Side Resistance
# Figure 10-6: Alpha Adhesion Factor (Chen et al., 2011)
# ============================================================================

def figure_10_6_alpha_clay(su_ciuc_kpa: float) -> float:
    """Adhesion factor alpha (dimensionless) for drilled shaft side resistance in cohesive soil from the CIUC-equivalent undrained strength in kPa, GEC-10 Eq. 10-18 (FHWA-NHI-18-024, p. 10-16), the regression curve of Figure 10-6 (p. 10-17; Chen et al. 2011).

        α = 0.30 + 0.17 / (su_CIUC / pa)

    where pa = 101.325 kPa.  GEC-10 recommends the expression "as a
    revision to the expressions for alpha currently given in the AASHTO
    LRFD Bridge Design Specifications (2017a)" (p. 10-16).

    Input must be CIUC-equivalent undrained shear strength.  For UC or UU lab
    test results, first convert using su_uu_to_ciuc() or su_uc_to_ciuc().

    Resistance factor (Table 8-4): φ = 0.45 (compression), 0.35 (uplift).

    Parameters
    ----------
    su_ciuc_kpa : float
        CIUC-equivalent undrained shear strength in kPa.  Must be positive.
        Figure 10-6 draws the curve from su(CIUC)/pa of about 0.25 to 5
        (about 25 to 500 kPa); outside that the expression is evaluated
        as written, not refused.

    Returns
    -------
    float
        Adhesion factor α (dimensionless).

    Raises
    ------
    ValueError
        If su_ciuc_kpa is not positive.
    """
    if su_ciuc_kpa <= 0:
        raise ValueError(
            f"su_ciuc_kpa must be positive, got {su_ciuc_kpa}"
        )
    return 0.30 + 0.17 / (su_ciuc_kpa / _PA_KPA)


# ============================================================================
# Equations 10-16 and 10-17 -- UC / UU to CIUC conversion (Chen and Kulhawy,
# 1993), FHWA-NHI-18-024 p. 10-16 (PDF page 296), read off the page:
#
#   su(UC) / su(CIUC) = 0.893 + 0.513 log( su(UC) / sigma'vo )   (10-16)
#   su(UU) / su(CIUC) = 0.911 + 0.499 log( su(UU) / sigma'vo )   (10-17)
#
# GEC-10 prints no range for either. The right-hand side falls to zero at
# su/sigma'vo = 10**(-0.893/0.513) = 0.0182 (UC) and 10**(-0.911/0.499) =
# 0.0149 (UU); below that the relation gives no strength (it returned a
# negative one) and is refused.
# ============================================================================

def _ciuc_from(su_kpa, sigma_v0_kpa, a, b, eq, test):
    if su_kpa <= 0:
        raise ValueError(f"su_{test.lower()}_kpa must be positive, got {su_kpa}")
    if sigma_v0_kpa <= 0:
        raise ValueError(f"sigma_v0_kpa must be positive, got {sigma_v0_kpa}")
    x = su_kpa / sigma_v0_kpa
    ratio = a + b * math.log10(x)
    if ratio <= 0:
        x0 = 10 ** (-a / b)
        raise ValueError(
            f"Eq. {eq} (GEC-10 p. 10-16) gives su({test})/su(CIUC) = "
            f"{ratio:.3f} at su({test})/sigma'vo = {x:.4g}: no strength. The "
            f"relation reaches zero at su({test})/sigma'vo = {x0:.4f}; GEC-10 "
            "prints no range for it.")
    return su_kpa / ratio


def su_uu_to_ciuc(su_uu_kpa: float, sigma_v0_kpa: float) -> float:
    """CIUC-equivalent undrained shear strength in kPa from a UU triaxial strength, GEC-10 Eq. 10-17 (FHWA-NHI-18-024, p. 10-16; Chen and Kulhawy 1993).

        su(UU) / su(CIUC) = 0.911 + 0.499 log10( su(UU) / sigma'vo )

    Used to convert UU test results before the alpha method (Eq. 10-18,
    Figure 10-6). Illustrative Example 10-2 (p. 10-18): su(UU) 2,000 psf
    at sigma'vo 3,697 psf gives su(CIUC) 2,571 psf.

    Parameters
    ----------
    su_uu_kpa : float
        UU test undrained shear strength in kPa.  Must be positive.
    sigma_v0_kpa : float
        Vertical effective stress (at layer mid-depth in Example 10-2) in
        kPa.  Must be positive.

    Returns
    -------
    float
        CIUC-equivalent undrained shear strength in kPa.

    Raises
    ------
    ValueError
        If inputs are not positive, or su(UU)/sigma'vo is 0.0149 or less,
        where Eq. 10-17 gives a ratio of zero or less (no strength).
    """
    return _ciuc_from(su_uu_kpa, sigma_v0_kpa, 0.911, 0.499, "10-17", "UU")


def su_uc_to_ciuc(su_uc_kpa: float, sigma_v0_kpa: float) -> float:
    """CIUC-equivalent undrained shear strength in kPa from an unconfined compression (UC) strength, GEC-10 Eq. 10-16 (FHWA-NHI-18-024, p. 10-16; Chen and Kulhawy 1993).

        su(UC) / su(CIUC) = 0.893 + 0.513 log10( su(UC) / sigma'vo )

    Parameters
    ----------
    su_uc_kpa : float
        UC test undrained shear strength in kPa.  Must be positive.
    sigma_v0_kpa : float
        Vertical effective stress in kPa.  Must be positive.

    Returns
    -------
    float
        CIUC-equivalent undrained shear strength in kPa.

    Raises
    ------
    ValueError
        If inputs are not positive, or su(UC)/sigma'vo is 0.0182 or less,
        where Eq. 10-16 gives a ratio of zero or less (no strength).
    """
    return _ciuc_from(su_uc_kpa, sigma_v0_kpa, 0.893, 0.513, "10-16", "UC")


# ============================================================================
# Section 10.3.5.3 — Rock Socket Side Resistance
# Equation 10-21: normal (clean) sockets
# Equation 10-22 + Table 10-3: caving / fractured rock
# ============================================================================

def equation_10_21_rock_socket_side(qu_kpa: float, C: float = 1.0) -> dict:
    """Unit side resistance in a rock socket — normal conditions (Equation 10-21).

    For sockets with nominally clean sidewalls constructed with conventional
    equipment:

        f_SN / pa = C × sqrt(qu / pa)

    where pa = 101.325 kPa.  The mean regression coefficient from Kulhawy et al.
    (2005) is C = 1.0, recommended for normal ("clean") sockets.  For
    artificially roughened sockets, C = 1.9 may be used with load test
    verification (Kulhawy and Prakoso, 2007).

    Resistance factor: Table 8-4 (p. 8-14) prints 0.50 (compression) and
    0.40 (uplift) for rock side resistance by Eq. 10-21; the text of p.
    10-21 says 0.55 for Eqs. 10-21 and 10-22 "as presented in Table 8-4".
    Both are printed; they are not reconciled here.

    Parameters
    ----------
    qu_kpa : float
        Mean uniaxial compressive strength of the rock layer in kPa.  Must
        be positive.  "For design, the value of qu used in Equation 10-21
        should not exceed the compressive strength of the drilled shaft
        concrete" (p. 10-21); the function does not check it.
    C : float
        Regression coefficient.  Default 1.0, recommended for "normal"
        sockets (p. 10-20).  For roughened sockets p. 10-22 gives Kulhawy
        and Prakoso's (2007) mean C = 1.9 "with use of Equation 10-22" (C
        appears only in Eq. 10-21) and strongly recommends load tests or
        local experience to verify C greater than 1.0.

    Returns
    -------
    dict
        {'C': float, 'qu_kpa': float, 'qu_mpa': float,
         'f_sn_kpa': float, 'f_sn_mpa': float, 'condition': str}

    Raises
    ------
    ValueError
        If qu_kpa or C is not positive.
    """
    if qu_kpa <= 0:
        raise ValueError(f"qu_kpa must be positive, got {qu_kpa}")
    if C <= 0:
        raise ValueError(f"C must be positive, got {C}")

    f_sn_kpa = C * _PA_KPA * math.sqrt(qu_kpa / _PA_KPA)
    if abs(C - 1.0) < 0.05:
        condition = "normal"
    elif C >= 1.7:
        condition = "artificially roughened"
    else:
        condition = "custom"

    return {
        "C": C,
        "qu_kpa": qu_kpa,
        "qu_mpa": round(qu_kpa / 1000, 4),
        "f_sn_kpa": round(f_sn_kpa, 2),
        "f_sn_mpa": round(f_sn_kpa / 1000, 5),
        "condition": condition,
    }


# Table 10-3 data: αE (joint modification factor) for Equation 10-22
_TABLE_10_3_RQD = [20, 30, 50, 70, 100]
_TABLE_10_3_AE_CLOSED = [0.45, 0.50, 0.60, 0.85, 1.00]
_TABLE_10_3_AE_OPEN   = [0.45, 0.50, 0.55, 0.55, 0.85]


def equation_10_22_caving_rock_side(qu_kpa: float,
                                     rqd_pct: float,
                                     joint_condition: str = "closed") -> dict:
    """Unit side resistance in a rock socket — caving or fractured rock (Equation 10-22).

    For rock that requires artificial support (casing or plug-ahead) during
    excavation (O'Neill and Reese, 1999):

        f_SN / pa = 0.65 × αE × sqrt(qu / pa)

    αE is the joint modification factor from Table 10-3, which depends on RQD
    and the condition of discontinuity surfaces.

    Resistance factor: Table 8-4 (p. 8-14) lists rock side resistance
    under Eq. 10-21 only (0.50 / 0.40); the text of p. 10-21 says 0.55 for
    Eqs. 10-21 and 10-22. Both are printed; they are not reconciled here.

    Parameters
    ----------
    qu_kpa : float
        Mean uniaxial compressive strength of intact rock in kPa.  Must be positive.
    rqd_pct : float
        Rock Quality Designation as a percentage (0–100).  Table 10-3
        (p. 10-21) prints RQD 100, 70, 50, 30 and 20; between rows alpha_E
        is interpolated linearly, and below 20 the 20 row is used, with a
        note in the result.
    joint_condition : str
        Discontinuity condition: 'closed' (tight joints) or 'open'
        (open or gouge-filled joints).  Default 'closed'.

    Returns
    -------
    dict
        {'alpha_E': float, 'qu_kpa': float, 'f_sn_kpa': float,
         'f_sn_mpa': float, 'rqd_pct': float, 'joint_condition': str}

    Raises
    ------
    ValueError
        If inputs are out of range.
    """
    if qu_kpa <= 0:
        raise ValueError(f"qu_kpa must be positive, got {qu_kpa}")
    if not (0 <= rqd_pct <= 100):
        raise ValueError(f"rqd_pct must be 0–100, got {rqd_pct}")

    jc = joint_condition.lower().strip()
    if jc not in ("closed", "open"):
        raise ValueError(
            f"joint_condition must be 'closed' or 'open', got '{joint_condition}'"
        )

    table = _TABLE_10_3_AE_CLOSED if jc == "closed" else _TABLE_10_3_AE_OPEN

    note = None
    if rqd_pct < _TABLE_10_3_RQD[0]:
        alpha_e = table[0]
        note = ("Table 10-3 prints no row below RQD 20; the RQD 20 row's "
                "alpha_E is used.")
    elif rqd_pct >= _TABLE_10_3_RQD[-1]:
        alpha_e = table[-1]
    else:
        alpha_e = _linterp(rqd_pct, _TABLE_10_3_RQD, table)

    f_sn_kpa = 0.65 * alpha_e * _PA_KPA * math.sqrt(qu_kpa / _PA_KPA)

    out = {
        "alpha_E": round(alpha_e, 3),
        "qu_kpa": qu_kpa,
        "f_sn_kpa": round(f_sn_kpa, 2),
        "f_sn_mpa": round(f_sn_kpa / 1000, 5),
        "rqd_pct": rqd_pct,
        "joint_condition": jc,
    }
    if note:
        out["note"] = note
    return out
