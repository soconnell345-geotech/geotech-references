"""GEC-10 figure lookup functions.

Digitized figures from FHWA-NHI-10-016 (GEC-10), Drilled Shafts:
Construction Procedures and LRFD Design Methods.  Follows the DM7
pattern: private data with ``_FIG_*`` prefix, public lookup functions
with ``_linterp`` interpolation.

Note: Core drilled shaft computation (alpha, beta, rock socket, end bearing,
p-y curves) is implemented in GeotechStaffEngineer's drilled_shaft and
lateral_pile modules.  This module provides supplementary lookup charts
for design guidance not covered by the computation modules.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Figure 13-10: Alpha Factor vs Undrained Shear Strength (O'Neill & Reese 1999)
# For drilled shafts in cohesive soils.
# Alpha factor for side resistance: f_s = alpha * su
# ============================================================================

_FIG_13_10_SU_KPA = [
    25, 50, 75, 100, 125, 150, 175, 200, 250,
]
_FIG_13_10_ALPHA = [
    0.55, 0.55, 0.49, 0.42, 0.38, 0.35, 0.33, 0.32, 0.31,
]


def figure_13_10_alpha_clay(su_kpa: float) -> float:
    """Alpha factor for drilled shaft side resistance in clay (Figure 13-10).

    Based on O'Neill & Reese (1999) correlation.  For drilled shafts,
    alpha = 0.55 for su <= 50 kPa, then decreases with increasing su.

    Parameters
    ----------
    su_kpa : float
        Undrained shear strength in kPa, 25 to 250.

    Returns
    -------
    float
        Alpha factor (dimensionless, 0 to 0.55).

    Raises
    ------
    ValueError
        If su_kpa is outside the chart range.
    """
    if su_kpa < 25:
        raise ValueError(
            f"su_kpa={su_kpa} is below the chart minimum of 25 kPa."
        )
    if su_kpa > 250:
        raise ValueError(
            f"su_kpa={su_kpa} exceeds the chart range of 250 kPa. "
            "For very stiff clay, use alpha ≈ 0.30 with engineering judgment."
        )
    return _linterp(su_kpa, _FIG_13_10_SU_KPA, _FIG_13_10_ALPHA)


# ============================================================================
# Figure 13-8: Beta Factor vs Depth for Drilled Shafts in Sand
# (O'Neill & Reese 1999, Brown et al. 2010)
# ============================================================================

_FIG_13_8_DEPTH_M = [0, 5, 10, 15, 20, 25, 30]
_FIG_13_8_BETA_UPPER = [1.80, 1.20, 0.90, 0.72, 0.60, 0.52, 0.45]
_FIG_13_8_BETA_LOWER = [0.80, 0.55, 0.40, 0.32, 0.27, 0.23, 0.20]
_FIG_13_8_BETA_MEAN = [1.20, 0.85, 0.62, 0.50, 0.42, 0.36, 0.32]


def figure_13_8_beta_sand(depth_m: float,
                           bound: str = "mean") -> float:
    """Beta factor vs depth for drilled shafts in sand (Figure 13-8).

    Beta = Ks * tan(delta), used for side resistance in cohesionless
    soils: f_s = beta * sigma'_v.

    Parameters
    ----------
    depth_m : float
        Depth below ground surface in meters, 0 to 30.
    bound : str
        'upper', 'lower', or 'mean' (default).

    Returns
    -------
    float
        Beta factor (dimensionless).

    Raises
    ------
    ValueError
        If depth or bound is invalid.
    """
    if depth_m < 0 or depth_m > 30:
        raise ValueError(
            f"depth_m={depth_m} is outside the chart range 0-30 m."
        )

    b = bound.lower().strip()
    if b == "upper":
        return _linterp(depth_m, _FIG_13_8_DEPTH_M, _FIG_13_8_BETA_UPPER)
    elif b == "lower":
        return _linterp(depth_m, _FIG_13_8_DEPTH_M, _FIG_13_8_BETA_LOWER)
    elif b in ("mean", "average", "recommended"):
        return _linterp(depth_m, _FIG_13_8_DEPTH_M, _FIG_13_8_BETA_MEAN)
    else:
        raise ValueError(
            f"Unknown bound '{bound}'. Use: 'upper', 'lower', or 'mean'."
        )


# ============================================================================
# Figure 13-18: Base Resistance Factor (qb/Nc*su) vs Depth/Diameter
# for drilled shafts in clay (O'Neill & Reese 1999)
#
# The bearing capacity factor Nc* increases with D/B from about 6.5
# to the theoretical maximum of 9.0 at D/B >= 4.
# ============================================================================

_FIG_13_18_DB = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
_FIG_13_18_NC = [6.50, 7.00, 7.50, 7.90, 8.20, 8.45, 8.65, 8.90, 9.00]


def figure_13_18_nc_base_clay(depth_over_diameter: float) -> float:
    """Bearing capacity factor Nc* for drilled shaft base in clay (Figure 13-18).

    Nc* transitions from about 6.5 at the surface to 9.0 at D/B >= 4-5.

    Parameters
    ----------
    depth_over_diameter : float
        Ratio of shaft embedment depth to shaft diameter (D/B), 0 to 5+.

    Returns
    -------
    float
        Nc* bearing capacity factor.

    Raises
    ------
    ValueError
        If depth_over_diameter is negative.
    """
    if depth_over_diameter < 0:
        raise ValueError(
            f"depth_over_diameter must be >= 0, got {depth_over_diameter}"
        )

    # Clamp above 5 to max Nc*
    if depth_over_diameter >= _FIG_13_18_DB[-1]:
        return _FIG_13_18_NC[-1]

    return _linterp(depth_over_diameter, _FIG_13_18_DB, _FIG_13_18_NC)


# ============================================================================
# Figure 13-24: Unit Side Resistance Factor for Rock Sockets
# (Horvath & Kenney 1979, O'Neill & Reese 1999)
#
# f_s = C * sqrt(qu) where qu = unconfined compressive strength (MPa)
# and C depends on roughness class.
# ============================================================================

_FIG_13_24_ROUGHNESS = {
    "smooth": {
        "C": 0.20,
        "description": "Smooth rock socket wall",
    },
    "intermediate": {
        "C": 0.30,
        "description": "Intermediate roughness (typical construction)",
    },
    "rough": {
        "C": 0.45,
        "description": "Artificially roughened or naturally rough socket",
    },
}


def figure_13_24_rock_socket_side(qu_mpa: float,
                                    roughness: str = "intermediate") -> dict:
    """Unit side resistance in rock socket (Figure 13-24).

    f_s = C * sqrt(qu) where qu is unconfined compressive strength.

    Parameters
    ----------
    qu_mpa : float
        Unconfined compressive strength of intact rock in MPa.
    roughness : str
        Socket wall roughness: 'smooth', 'intermediate', or 'rough'.

    Returns
    -------
    dict
        {'C': float, 'qu_mpa': float, 'fs_mpa': float, 'fs_kpa': float,
         'roughness': str, 'description': str}

    Raises
    ------
    ValueError
        If qu_mpa < 0 or roughness is invalid.
    """
    if qu_mpa < 0:
        raise ValueError(f"qu_mpa must be >= 0, got {qu_mpa}")

    key = roughness.lower().strip()
    if key not in _FIG_13_24_ROUGHNESS:
        raise ValueError(
            f"Unknown roughness '{roughness}'. "
            f"Use: {', '.join(_FIG_13_24_ROUGHNESS.keys())}"
        )

    data = _FIG_13_24_ROUGHNESS[key]
    fs_mpa = data["C"] * (qu_mpa ** 0.5)

    return {
        "C": data["C"],
        "qu_mpa": qu_mpa,
        "fs_mpa": round(fs_mpa, 4),
        "fs_kpa": round(fs_mpa * 1000, 1),
        "roughness": key,
        "description": data["description"],
    }
