"""GEC-10 figure and equation lookup functions.

Equations and figure correlations from FHWA-NHI-18-024 (GEC-10, 2018 edition),
Drilled Shafts: Construction Procedures and LRFD Design Methods.

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
    """Alpha adhesion factor for drilled shaft side resistance in cohesive soil (Figure 10-6).

    Regression equation from Chen et al. (2011) fitted to load test database:

        α = 0.30 + 0.17 / (su_CIUC / pa)

    where pa = 101.325 kPa.  This expression supersedes the AASHTO (2017a) piecewise
    α-method per Section 10.3.5.2 of FHWA-NHI-18-024.

    Input must be CIUC-equivalent undrained shear strength.  For UC or UU lab
    test results, first convert using su_uu_to_ciuc() or su_uc_to_ciuc().

    Resistance factor (Table 8-4): φ = 0.45 (compression), 0.35 (uplift).

    Parameters
    ----------
    su_ciuc_kpa : float
        CIUC-equivalent undrained shear strength in kPa.  Must be positive.
        Typical range: 25 to 500 kPa.

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
# Equations 10-16 and 10-17 — UU / UC to CIUC conversion
# (Chen and Kulhawy, 1993)
# ============================================================================

def su_uu_to_ciuc(su_uu_kpa: float, sigma_v0_kpa: float) -> float:
    """Convert UU triaxial undrained strength to CIUC-equivalent (Equation 10-17).

    Chen and Kulhawy (1993):

        su_UU / su_CIUC = 0.911 + 0.499 × log10(su_UU / σ'v0)

    Used to convert routine UU test results before applying the alpha method
    in Figure 10-6.

    Parameters
    ----------
    su_uu_kpa : float
        UU test undrained shear strength in kPa.  Must be positive.
    sigma_v0_kpa : float
        Effective vertical stress at layer mid-depth in kPa.  Must be positive.

    Returns
    -------
    float
        CIUC-equivalent undrained shear strength in kPa.

    Raises
    ------
    ValueError
        If inputs are not positive.
    """
    if su_uu_kpa <= 0:
        raise ValueError(f"su_uu_kpa must be positive, got {su_uu_kpa}")
    if sigma_v0_kpa <= 0:
        raise ValueError(f"sigma_v0_kpa must be positive, got {sigma_v0_kpa}")
    denom = 0.911 + 0.499 * math.log10(su_uu_kpa / sigma_v0_kpa)
    return su_uu_kpa / denom


def su_uc_to_ciuc(su_uc_kpa: float, sigma_v0_kpa: float) -> float:
    """Convert UC (unconfined compression) strength to CIUC-equivalent (Equation 10-16).

    Chen and Kulhawy (1993):

        su_UC / su_CIUC = 0.893 + 0.513 × log10(su_UC / σ'v0)

    Parameters
    ----------
    su_uc_kpa : float
        UC test undrained shear strength in kPa.  Must be positive.
    sigma_v0_kpa : float
        Effective vertical stress at layer mid-depth in kPa.  Must be positive.

    Returns
    -------
    float
        CIUC-equivalent undrained shear strength in kPa.

    Raises
    ------
    ValueError
        If inputs are not positive.
    """
    if su_uc_kpa <= 0:
        raise ValueError(f"su_uc_kpa must be positive, got {su_uc_kpa}")
    if sigma_v0_kpa <= 0:
        raise ValueError(f"sigma_v0_kpa must be positive, got {sigma_v0_kpa}")
    denom = 0.893 + 0.513 * math.log10(su_uc_kpa / sigma_v0_kpa)
    return su_uc_kpa / denom


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

    Resistance factor (Table 8-4): φ = 0.50 (compression), 0.40 (uplift).

    Parameters
    ----------
    qu_kpa : float
        Mean uniaxial compressive strength of intact rock in kPa.  Must be
        positive.  Should not exceed the compressive strength of the shaft
        concrete.
    C : float
        Regression coefficient.  Default 1.0 for normal sockets; use 1.9 for
        artificially roughened sockets (load test verification required).

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

    Resistance factor (Table 8-4): φ = 0.50 (compression), 0.40 (uplift).

    Parameters
    ----------
    qu_kpa : float
        Mean uniaxial compressive strength of intact rock in kPa.  Must be positive.
    rqd_pct : float
        Rock Quality Designation as a percentage (0–100).
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

    if rqd_pct <= _TABLE_10_3_RQD[0]:
        alpha_e = table[0]
    elif rqd_pct >= _TABLE_10_3_RQD[-1]:
        alpha_e = table[-1]
    else:
        alpha_e = _linterp(rqd_pct, _TABLE_10_3_RQD, table)

    f_sn_kpa = 0.65 * alpha_e * _PA_KPA * math.sqrt(qu_kpa / _PA_KPA)

    return {
        "alpha_E": round(alpha_e, 3),
        "qu_kpa": qu_kpa,
        "f_sn_kpa": round(f_sn_kpa, 2),
        "f_sn_mpa": round(f_sn_kpa / 1000, 5),
        "rqd_pct": rqd_pct,
        "joint_condition": jc,
    }
