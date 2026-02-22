"""GEC-12 figure lookup functions.

Digitized figures from FHWA-NHI-16-009 (GEC-12), Design and Construction
of Driven Pile Foundations.  Follows the DM7 pattern: private data with
``_FIG_*`` prefix, public lookup functions with ``_linterp`` interpolation.
"""

import math

from geotech_references._interpolation import _linterp


# ============================================================================
# Tables 7-6 and 7-7: Kd for omega = 0 deg (uniform cross-section piles)
# Combined into a single lookup function.
# Kd = coefficient of lateral earth pressure for Nordlund method.
# ============================================================================

_TABLE_7_6_V = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
_TABLE_7_7_V = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

_KD_PHI = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]

# Table 7-6: Kd for V = 0.10 to 1.00 ft^3/ft, omega = 0 deg
_TABLE_7_6_KD = {
    25: [0.70, 0.75, 0.77, 0.79, 0.80, 0.82, 0.83, 0.84, 0.84, 0.85],
    26: [0.73, 0.78, 0.82, 0.84, 0.86, 0.87, 0.88, 0.89, 0.90, 0.91],
    27: [0.76, 0.82, 0.86, 0.89, 0.91, 0.92, 0.94, 0.95, 0.96, 0.97],
    28: [0.79, 0.86, 0.90, 0.93, 0.96, 0.98, 0.99, 1.01, 1.02, 1.03],
    29: [0.82, 0.90, 0.95, 0.98, 1.01, 1.03, 1.05, 1.06, 1.08, 1.09],
    30: [0.85, 0.94, 0.99, 1.03, 1.06, 1.08, 1.10, 1.12, 1.14, 1.15],
    31: [0.91, 1.02, 1.08, 1.13, 1.16, 1.19, 1.21, 1.24, 1.25, 1.27],
    32: [0.97, 1.10, 1.17, 1.22, 1.26, 1.30, 1.32, 1.35, 1.37, 1.39],
    33: [1.03, 1.17, 1.26, 1.32, 1.37, 1.40, 1.44, 1.46, 1.49, 1.51],
    34: [1.09, 1.25, 1.35, 1.42, 1.47, 1.51, 1.55, 1.58, 1.61, 1.63],
    35: [1.15, 1.33, 1.44, 1.51, 1.57, 1.62, 1.66, 1.69, 1.72, 1.75],
    36: [1.26, 1.48, 1.61, 1.71, 1.78, 1.84, 1.89, 1.93, 1.97, 2.00],
    37: [1.37, 1.63, 1.79, 1.90, 1.99, 2.05, 2.11, 2.16, 2.21, 2.25],
    38: [1.48, 1.79, 1.97, 2.09, 2.19, 2.27, 2.34, 2.40, 2.45, 2.50],
    39: [1.59, 1.94, 2.14, 2.29, 2.40, 2.49, 2.57, 2.64, 2.70, 2.75],
    40: [1.70, 2.09, 2.32, 2.48, 2.61, 2.71, 2.80, 2.87, 2.94, 3.00],
}

# Table 7-7: Kd for V = 1.0 to 10.0 ft^3/ft, omega = 0 deg
_TABLE_7_7_KD = {
    25: [0.85, 0.90, 0.92, 0.94, 0.95, 0.97, 0.98, 0.99, 0.99, 1.00],
    26: [0.91, 0.96, 1.00, 1.02, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09],
    27: [0.97, 1.03, 1.07, 1.10, 1.12, 1.13, 1.15, 1.16, 1.17, 1.18],
    28: [1.03, 1.10, 1.14, 1.17, 1.20, 1.22, 1.23, 1.25, 1.26, 1.27],
    29: [1.09, 1.17, 1.22, 1.25, 1.28, 1.30, 1.32, 1.33, 1.35, 1.36],
    30: [1.15, 1.24, 1.29, 1.33, 1.36, 1.38, 1.40, 1.42, 1.44, 1.45],
    31: [1.27, 1.38, 1.44, 1.49, 1.52, 1.55, 1.57, 1.60, 1.61, 1.63],
    32: [1.39, 1.52, 1.59, 1.64, 1.68, 1.72, 1.74, 1.77, 1.79, 1.81],
    33: [1.51, 1.65, 1.74, 1.80, 1.85, 1.88, 1.92, 1.94, 1.97, 1.99],
    34: [1.63, 1.79, 1.89, 1.96, 2.01, 2.05, 2.09, 2.12, 2.15, 2.17],
    35: [1.75, 1.93, 2.04, 2.11, 2.17, 2.22, 2.26, 2.29, 2.32, 2.35],
    36: [2.00, 2.22, 2.35, 2.45, 2.52, 2.58, 2.63, 2.67, 2.71, 2.74],
    37: [2.25, 2.51, 2.67, 2.78, 2.87, 2.93, 2.99, 3.04, 3.09, 3.13],
    38: [2.50, 2.81, 2.99, 3.11, 3.21, 3.29, 3.36, 3.42, 3.47, 3.52],
    39: [2.75, 3.10, 3.30, 3.45, 3.56, 3.65, 3.73, 3.80, 3.86, 3.91],
    40: [3.00, 3.39, 3.62, 3.78, 3.91, 4.01, 4.10, 4.17, 4.24, 4.30],
}


def figure_7_10_to_13_kd(phi: float, V: float, omega: float = 0.0) -> float:
    """Coefficient of lateral earth pressure Kd for Nordlund method.

    Uses Tables 7-6 and 7-7 for omega=0 (uniform piles).  For omega>0
    (tapered piles), values are from the design curves in Figures 7-10
    through 7-13 (not currently supported via tabular interpolation).

    Parameters
    ----------
    phi : float
        Soil friction angle (degrees), 25 to 40.
    V : float
        Displaced soil volume per unit pile length (ft^3/ft), 0.10 to 10.0.
    omega : float
        Pile taper angle from vertical (degrees).  Default 0.0 for uniform
        piles.  Currently only omega=0 is supported via tabular data.

    Returns
    -------
    float
        Kd coefficient (dimensionless).

    Raises
    ------
    ValueError
        If phi or V is outside the supported range, or omega > 0.
    """
    if omega != 0.0:
        raise ValueError(
            "Only omega=0 (uniform piles) is currently supported via "
            "Tables 7-6 and 7-7.  For tapered piles, use the chart directly."
        )
    if phi < 25 or phi > 40:
        raise ValueError(
            f"Friction angle phi={phi} deg is outside the range 25-40 deg."
        )
    if V < 0.10 or V > 10.0:
        raise ValueError(
            f"Displaced volume V={V} ft^3/ft is outside the range 0.10-10.0."
        )

    # Select appropriate table based on V range
    if V <= 1.0:
        v_values = _TABLE_7_6_V
        kd_table = _TABLE_7_6_KD
    else:
        v_values = _TABLE_7_7_V
        kd_table = _TABLE_7_7_KD

    # Interpolate: phi first, then V
    phi_lo = max(p for p in _KD_PHI if p <= phi)
    phi_hi = min(p for p in _KD_PHI if p >= phi)

    if phi_lo == phi_hi:
        return _linterp(V, v_values, kd_table[phi_lo])

    kd_lo = _linterp(V, v_values, kd_table[phi_lo])
    kd_hi = _linterp(V, v_values, kd_table[phi_hi])
    frac = (phi - phi_lo) / (phi_hi - phi_lo)
    return kd_lo + frac * (kd_hi - kd_lo)


# ============================================================================
# Figure 7-14: Correction Factor CF for Kd when delta != phi
# (after Nordlund 1979)
# ============================================================================

_FIG_7_14_PHI = [15, 20, 25, 30, 35, 40, 45, 50]

_FIG_7_14_CF = {
    0.2: [0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.24, 0.30],
    0.4: [0.25, 0.28, 0.32, 0.36, 0.40, 0.45, 0.50, 0.55],
    0.6: [0.45, 0.48, 0.52, 0.56, 0.62, 0.68, 0.74, 0.80],
    0.8: [0.70, 0.73, 0.76, 0.80, 0.84, 0.88, 0.92, 0.95],
    1.0: [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00],
    1.2: [1.05, 1.05, 1.06, 1.06, 1.07, 1.08, 1.09, 1.10],
    1.4: [1.10, 1.10, 1.11, 1.12, 1.13, 1.15, 1.17, 1.20],
}


def figure_7_14_correction_factor(phi: float, delta_phi_ratio: float) -> float:
    """Correction factor CF for Kd when delta != phi (Figure 7-14).

    Parameters
    ----------
    phi : float
        Soil friction angle (degrees), 15 to 50.
    delta_phi_ratio : float
        Ratio delta/phi, 0.2 to 1.4.

    Returns
    -------
    float
        Correction factor CF (dimensionless).

    Raises
    ------
    ValueError
        If phi or delta_phi_ratio is outside the supported range.
    """
    if phi < 15 or phi > 50:
        raise ValueError(
            f"Friction angle phi={phi} deg is outside the range 15-50 deg."
        )

    ratios = sorted(_FIG_7_14_CF.keys())
    if delta_phi_ratio < ratios[0] or delta_phi_ratio > ratios[-1]:
        raise ValueError(
            f"delta/phi ratio={delta_phi_ratio} is outside the range "
            f"{ratios[0]}-{ratios[-1]}."
        )

    r_lo = max(r for r in ratios if r <= delta_phi_ratio)
    r_hi = min(r for r in ratios if r >= delta_phi_ratio)

    cf_lo = _linterp(phi, _FIG_7_14_PHI, _FIG_7_14_CF[r_lo])
    if r_lo == r_hi:
        return cf_lo

    cf_hi = _linterp(phi, _FIG_7_14_PHI, _FIG_7_14_CF[r_hi])
    frac = (delta_phi_ratio - r_lo) / (r_hi - r_lo)
    return cf_lo + frac * (cf_hi - cf_lo)


# ============================================================================
# Figure 7-15: Limiting Unit Toe Resistance vs Friction Angle
# (after Meyerhof 1976)
# ============================================================================

_FIG_7_15_PHI = [26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 45]
_FIG_7_15_QL_TSF = [2.0, 5.0, 10.0, 20.0, 40.0, 75.0, 130.0, 200.0, 280.0, 360.0, 400.0]


def figure_7_15_limiting_toe_resistance(phi: float) -> float:
    """Limiting unit toe resistance qL for cohesionless soils (Figure 7-15).

    Parameters
    ----------
    phi : float
        Soil friction angle at pile toe (degrees), 26 to 45.

    Returns
    -------
    float
        Limiting unit toe resistance qL in tsf.

    Raises
    ------
    ValueError
        If phi is outside the range 26-45 deg.
    """
    if phi < 26 or phi > 45:
        raise ValueError(
            f"Friction angle phi={phi} deg is outside the range 26-45 deg."
        )
    return _linterp(phi, _FIG_7_15_PHI, _FIG_7_15_QL_TSF)


# ============================================================================
# Figure 7-16(a): alpha_t Coefficient (Dimensionless Factor)
# (after Bowles 1977)
# ============================================================================

_FIG_7_16A_PHI = [15, 20, 25, 30, 35, 40, 45]

_FIG_7_16A_AT = {
    20: [0.25, 0.35, 0.47, 0.60, 0.73, 0.82, 0.88],
    30: [0.22, 0.29, 0.38, 0.50, 0.65, 0.77, 0.85],
    45: [0.18, 0.22, 0.28, 0.38, 0.53, 0.67, 0.77],
}


def figure_7_16a_alpha_t(phi: float, D_over_b: float) -> float:
    """Dimensionless alpha_t coefficient for Nordlund toe resistance (Fig 7-16a).

    Parameters
    ----------
    phi : float
        Soil friction angle at pile toe (degrees), 15 to 45.
    D_over_b : float
        Ratio of embedded pile length D to pile diameter b.
        Supported range: 20 to 45.

    Returns
    -------
    float
        alpha_t coefficient (dimensionless).

    Raises
    ------
    ValueError
        If phi or D_over_b is outside the supported range.
    """
    if phi < 15 or phi > 45:
        raise ValueError(
            f"Friction angle phi={phi} deg is outside the range 15-45 deg."
        )
    if D_over_b < 20 or D_over_b > 45:
        raise ValueError(
            f"D/b ratio={D_over_b} is outside the range 20-45."
        )

    db_values = sorted(_FIG_7_16A_AT.keys())
    db_lo = max(d for d in db_values if d <= D_over_b)
    db_hi = min(d for d in db_values if d >= D_over_b)

    at_lo = _linterp(phi, _FIG_7_16A_PHI, _FIG_7_16A_AT[db_lo])
    if db_lo == db_hi:
        return at_lo

    at_hi = _linterp(phi, _FIG_7_16A_PHI, _FIG_7_16A_AT[db_hi])
    frac = (D_over_b - db_lo) / (db_hi - db_lo)
    return at_lo + frac * (at_hi - at_lo)


# ============================================================================
# Figure 7-16(b): N'q Bearing Capacity Factor for Nordlund Method
# (after Bowles 1977)
# ============================================================================

_FIG_7_16B_PHI = [15, 20, 25, 30, 35, 40, 45]
_FIG_7_16B_NQ = [5.0, 8.0, 14.0, 28.0, 60.0, 150.0, 500.0]


def figure_7_16b_nq(phi: float) -> float:
    """Bearing capacity factor N'q for Nordlund toe resistance (Figure 7-16b).

    Uses log-linear interpolation since N'q varies over orders of magnitude.

    Parameters
    ----------
    phi : float
        Soil friction angle at pile toe (degrees), 15 to 45.

    Returns
    -------
    float
        N'q bearing capacity factor (dimensionless).

    Raises
    ------
    ValueError
        If phi is outside the range 15-45 deg.
    """
    if phi < 15 or phi > 45:
        raise ValueError(
            f"Friction angle phi={phi} deg is outside the range 15-45 deg."
        )
    log_nq = [math.log10(v) for v in _FIG_7_16B_NQ]
    log_result = _linterp(phi, _FIG_7_16B_PHI, log_nq)
    return 10 ** log_result


# ============================================================================
# Figure 7-9: delta/phi vs V for Various Pile Types
# (after Nordlund 1979)
#
# Provides typical delta/phi ratios.  In practice, V and pile type
# together determine delta/phi from the chart.  This function returns
# the commonly used ratio for each pile type.
# ============================================================================

_FIG_7_9_PILE_TYPES = {
    "pipe_pile": {
        "description": "Pipe piles and non-tapered portion of monotube piles",
        "delta_phi_ratio": 0.70,
    },
    "timber": {
        "description": "Timber piles",
        "delta_phi_ratio": 0.80,
    },
    "precast_concrete": {
        "description": "Precast concrete piles",
        "delta_phi_ratio": 0.85,
    },
    "raymond_step_taper": {
        "description": "Raymond step-taper piles",
        "delta_phi_ratio": 0.90,
    },
    "raymond_uniform_taper": {
        "description": "Raymond uniform taper piles",
        "delta_phi_ratio": 1.15,
    },
    "h_pile": {
        "description": "H-piles and augercast piles",
        "delta_phi_ratio": 0.60,
    },
    "monotube_tapered": {
        "description": "Tapered portion of monotube piles",
        "delta_phi_ratio": 0.95,
    },
}


def figure_7_9_delta_phi_ratio(pile_type: str) -> dict:
    """Typical delta/phi ratio for a given pile type (Figure 7-9).

    Parameters
    ----------
    pile_type : str
        Pile type.  Options: 'pipe_pile', 'timber', 'precast_concrete',
        'raymond_step_taper', 'raymond_uniform_taper', 'h_pile',
        'monotube_tapered'.

    Returns
    -------
    dict
        Keys: delta_phi_ratio, description.

    Raises
    ------
    ValueError
        If pile type is not recognized.
    """
    key = pile_type.lower().strip().replace(" ", "_").replace("-", "_")

    if key in _FIG_7_9_PILE_TYPES:
        return dict(_FIG_7_9_PILE_TYPES[key])

    # Partial match
    for k, v in _FIG_7_9_PILE_TYPES.items():
        if key in k or k in key:
            return dict(v)

    raise ValueError(
        f"Unknown pile type '{pile_type}'. "
        f"Available: {', '.join(_FIG_7_9_PILE_TYPES.keys())}"
    )


# ============================================================================
# Figure 7-17: Adhesion Ca for Piles in Cohesive Soils
# (after Tomlinson 1979)
#
# Curves for concrete/timber/corrugated steel and smooth steel piles
# at D/b = 10 and D/b = 40.  Recommended for routine design.
# ============================================================================

_FIG_7_17_SU = [0.0, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75,
                2.00, 2.50, 3.00, 3.50, 4.00]

# Ca (ksf) — concrete, timber, corrugated steel piles
_FIG_7_17_CA_CONCRETE_D10 = [
    0.0, 0.20, 0.38, 0.55, 0.68, 0.78, 0.85, 0.90,
    0.93, 0.95, 0.95, 0.93, 0.90,
]
_FIG_7_17_CA_CONCRETE_D40 = [
    0.0, 0.22, 0.45, 0.68, 0.88, 1.05, 1.20, 1.33,
    1.42, 1.55, 1.60, 1.58, 1.55,
]

# Ca (ksf) — smooth steel piles
_FIG_7_17_CA_STEEL_D10 = [
    0.0, 0.18, 0.33, 0.45, 0.56, 0.64, 0.70, 0.74,
    0.76, 0.78, 0.78, 0.76, 0.74,
]
_FIG_7_17_CA_STEEL_D40 = [
    0.0, 0.20, 0.40, 0.58, 0.75, 0.90, 1.02, 1.12,
    1.20, 1.30, 1.35, 1.33, 1.30,
]


def figure_7_17_adhesion(su_ksf: float, D_over_b: float = 10.0,
                         pile_surface: str = "concrete") -> float:
    """Pile adhesion Ca for piles in cohesive soils (Figure 7-17).

    Recommended for routine design.  For special stratigraphy cases
    (sand over stiff clay, soft clay over stiff clay, stiff clay only),
    see figure_7_18_adhesion_factor().

    Parameters
    ----------
    su_ksf : float
        Undrained shear strength (ksf), 0 to 4.0.
    D_over_b : float
        Ratio of pile embedment D to pile diameter b.
        Interpolated between D/b=10 and D/b=40.  Clamped to this range.
    pile_surface : str
        'concrete' (includes timber and corrugated steel) or 'steel'
        (smooth steel piles).

    Returns
    -------
    float
        Pile adhesion Ca (ksf).

    Raises
    ------
    ValueError
        If su_ksf is negative or exceeds 4.0, or pile surface is unknown.
    """
    if su_ksf < 0:
        raise ValueError(f"su_ksf={su_ksf} must be >= 0.")
    if su_ksf > 4.0:
        raise ValueError(
            f"su_ksf={su_ksf} exceeds chart range of 4.0 ksf. "
            "For higher strengths, see API method (Section 7.2.1.3.3)."
        )

    surface = pile_surface.lower().strip()
    D_b = max(10.0, min(40.0, D_over_b))

    if surface in ("concrete", "timber", "corrugated"):
        ca_d10 = _linterp(su_ksf, _FIG_7_17_SU, _FIG_7_17_CA_CONCRETE_D10)
        ca_d40 = _linterp(su_ksf, _FIG_7_17_SU, _FIG_7_17_CA_CONCRETE_D40)
    elif surface in ("steel", "smooth_steel", "smooth"):
        ca_d10 = _linterp(su_ksf, _FIG_7_17_SU, _FIG_7_17_CA_STEEL_D10)
        ca_d40 = _linterp(su_ksf, _FIG_7_17_SU, _FIG_7_17_CA_STEEL_D40)
    else:
        raise ValueError(
            f"Unknown pile surface '{pile_surface}'. "
            "Use 'concrete' or 'steel'."
        )

    frac = (D_b - 10.0) / 30.0
    return ca_d10 + frac * (ca_d40 - ca_d10)


# ============================================================================
# Figure 7-18: Adhesion Factor alpha for Driven Piles in Clay
# (Tomlinson 1980) — Three stratigraphy cases
#
# Case 1: Piles driven through sand/gravel into stiff clay
# Case 2: Piles driven through soft clay into stiff clay
# Case 3: Piles driven in stiff clay only (no overlying strata)
# ============================================================================

_FIG_7_18_SU = [0.0, 0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 3.50, 4.00, 4.50, 5.00]

# Case 1: Sand/gravel overlying stiff clay
# D < 10b gives highest alpha (more granular drag-in)
# D > 40b gives lowest alpha
_FIG_7_18_CASE1_D_LT_10 = [1.00, 0.98, 0.82, 0.62, 0.48, 0.38, 0.32, 0.28, 0.26, 0.24, 0.22]
_FIG_7_18_CASE1_D20 = [1.00, 0.95, 0.72, 0.52, 0.40, 0.32, 0.27, 0.24, 0.22, 0.20, 0.19]
_FIG_7_18_CASE1_D_GT_40 = [1.00, 0.90, 0.60, 0.42, 0.32, 0.26, 0.22, 0.20, 0.18, 0.17, 0.16]

# Case 2: Soft clay overlying stiff clay
# D > 20b gives highest alpha; D = 10b gives lowest
_FIG_7_18_CASE2_D10 = [1.00, 0.62, 0.38, 0.26, 0.20, 0.17, 0.15, 0.14, 0.13, 0.12, 0.12]
_FIG_7_18_CASE2_D_GT_20 = [1.00, 0.72, 0.52, 0.38, 0.30, 0.25, 0.22, 0.20, 0.18, 0.17, 0.16]

# Case 3: Stiff clay only (no overlying strata)
# D > 40b gives highest alpha; D = 10b gives lowest
_FIG_7_18_CASE3_D10 = [1.00, 0.55, 0.35, 0.22, 0.16, 0.13, 0.11, 0.10, 0.09, 0.08, 0.08]
_FIG_7_18_CASE3_D_GT_40 = [1.00, 0.72, 0.55, 0.42, 0.35, 0.30, 0.27, 0.24, 0.22, 0.20, 0.19]


def figure_7_18_adhesion_factor(
    su_ksf: float,
    D_over_b: float,
    stratigraphy: str = "sand_over_stiff_clay",
) -> float:
    """Adhesion factor alpha for driven piles in clay (Figure 7-18).

    Use only for the specific stratigraphy cases shown.  For routine
    design, prefer figure_7_17_adhesion().

    Parameters
    ----------
    su_ksf : float
        Undrained shear strength of the stiff clay (ksf), 0 to 5.0.
    D_over_b : float
        Ratio of pile embedment in the clay to pile diameter.
    stratigraphy : str
        Soil stratigraphy case:
        - 'sand_over_stiff_clay' (Case 1): sand/gravel overlying stiff clay
        - 'soft_over_stiff_clay' (Case 2): soft clay overlying stiff clay
        - 'stiff_clay_only' (Case 3): stiff clay without overlying strata

    Returns
    -------
    float
        Adhesion factor alpha (dimensionless, 0 to 1).

    Raises
    ------
    ValueError
        If su_ksf or stratigraphy is invalid.
    """
    if su_ksf < 0:
        raise ValueError(f"su_ksf={su_ksf} must be >= 0.")
    if su_ksf > 5.0:
        raise ValueError(
            f"su_ksf={su_ksf} exceeds chart range of 5.0 ksf."
        )

    case = stratigraphy.lower().strip().replace(" ", "_").replace("-", "_")

    if case in ("sand_over_stiff_clay", "case1", "case_1"):
        if D_over_b <= 10:
            return _linterp(su_ksf, _FIG_7_18_SU, _FIG_7_18_CASE1_D_LT_10)
        elif D_over_b >= 40:
            return _linterp(su_ksf, _FIG_7_18_SU, _FIG_7_18_CASE1_D_GT_40)
        else:
            # Interpolate between D=10 and D=20, or D=20 and D=40
            if D_over_b <= 20:
                a_lo = _linterp(su_ksf, _FIG_7_18_SU, _FIG_7_18_CASE1_D_LT_10)
                a_hi = _linterp(su_ksf, _FIG_7_18_SU, _FIG_7_18_CASE1_D20)
                frac = (D_over_b - 10.0) / 10.0
            else:
                a_lo = _linterp(su_ksf, _FIG_7_18_SU, _FIG_7_18_CASE1_D20)
                a_hi = _linterp(su_ksf, _FIG_7_18_SU, _FIG_7_18_CASE1_D_GT_40)
                frac = (D_over_b - 20.0) / 20.0
            return a_lo + frac * (a_hi - a_lo)

    elif case in ("soft_over_stiff_clay", "case2", "case_2"):
        D_b = max(10.0, min(20.0, D_over_b))
        a_lo = _linterp(su_ksf, _FIG_7_18_SU, _FIG_7_18_CASE2_D10)
        a_hi = _linterp(su_ksf, _FIG_7_18_SU, _FIG_7_18_CASE2_D_GT_20)
        frac = (D_b - 10.0) / 10.0
        return a_lo + frac * (a_hi - a_lo)

    elif case in ("stiff_clay_only", "case3", "case_3"):
        D_b = max(10.0, min(40.0, D_over_b))
        a_lo = _linterp(su_ksf, _FIG_7_18_SU, _FIG_7_18_CASE3_D10)
        a_hi = _linterp(su_ksf, _FIG_7_18_SU, _FIG_7_18_CASE3_D_GT_40)
        frac = (D_b - 10.0) / 30.0
        return a_lo + frac * (a_hi - a_lo)

    else:
        raise ValueError(
            f"Unknown stratigraphy '{stratigraphy}'. Use: "
            "'sand_over_stiff_clay', 'soft_over_stiff_clay', "
            "or 'stiff_clay_only'."
        )
