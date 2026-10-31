"""GEC-12 figure lookup functions.

Digitized figures from FHWA-NHI-16-009 (GEC-12), Design and Construction
of Driven Pile Foundations.  Follows the DM7 pattern: private data with
``_FIG_*`` prefix, public lookup functions with ``_linterp`` interpolation.

Every chart here was measured off the printed figure (GEC 12 Vol 1; the
figures are 150 dpi rasters inside the PDF, extracted as they are) by the
darkness-weighted centre of the drawn line against the figure's own
gridlines, to about one pixel (REF-49, 2026-10-31; Fig. 7-15 on
2026-10-08). Each lookup refuses a value the chart does not give.
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

    Linear in phi between the tables' rows, then log-linear in V between
    their columns, as Step 3 (c to e) of the Nordlund method prints it
    (GEC-12 p. 243). The printed columns are themselves the log-linear
    interpolation between the V = 0.1, 1.0 and 10 ft^3/ft curves, to the
    tables' 0.01.

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
    log_v = [math.log10(v) for v in v_values]

    # Interpolate: phi first, then log V
    phi_lo = max(p for p in _KD_PHI if p <= phi)
    phi_hi = min(p for p in _KD_PHI if p >= phi)

    if phi_lo == phi_hi:
        return _linterp(math.log10(V), log_v, kd_table[phi_lo])

    kd_lo = _linterp(math.log10(V), log_v, kd_table[phi_lo])
    kd_hi = _linterp(math.log10(V), log_v, kd_table[phi_hi])
    frac = (phi - phi_lo) / (phi_hi - phi_lo)
    return kd_lo + frac * (kd_hi - kd_lo)


# ============================================================================
# Figure 7-14: Correction Factor CF for Kd when delta != phi
# (after Nordlund 1979)
#
# The curves run from about 14 deg to 45 deg; CF falls with phi on the
# delta/phi < 1 curves and rises on the 1.2 and 1.4 curves. Read every
# 2.5 deg from 15 deg.
# ============================================================================

_FIG_7_14_PHI = [15, 17.5, 20, 22.5, 25, 27.5, 30, 32.5, 35, 37.5, 40, 42.5,
                 45]

_FIG_7_14_CF = {
    0.2: [0.815, 0.778, 0.740, 0.701, 0.661, 0.621, 0.580, 0.538, 0.488,
          0.432, 0.370, 0.306, 0.241],
    0.4: [0.888, 0.857, 0.825, 0.793, 0.759, 0.725, 0.689, 0.654, 0.612,
          0.570, 0.525, 0.479, 0.431],
    0.6: [0.942, 0.925, 0.905, 0.886, 0.864, 0.842, 0.817, 0.787, 0.757,
          0.728, 0.691, 0.654, 0.620],
    0.8: [0.988, 0.982, 0.976, 0.973, 0.966, 0.956, 0.945, 0.932, 0.917,
          0.902, 0.886, 0.865, 0.841],
    1.0: [1.0] * 13,
    1.2: [1.005, 1.008, 1.012, 1.015, 1.018, 1.024, 1.030, 1.038, 1.050,
          1.059, 1.074, 1.095, 1.120],
    1.4: [1.012, 1.017, 1.024, 1.033, 1.038, 1.047, 1.061, 1.074, 1.086,
          1.098, 1.115, 1.136, 1.160],
}


def figure_7_14_correction_factor(phi: float, delta_phi_ratio: float) -> float:
    """Correction factor CF for Kd when delta != phi (Figure 7-14).

    Linear in phi along each delta/phi curve, then linear between the
    curves.

    Parameters
    ----------
    phi : float
        Soil friction angle (degrees), 15 to 45 (the curves end at 45 deg).
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
    if phi < _FIG_7_14_PHI[0] or phi > _FIG_7_14_PHI[-1]:
        raise ValueError(
            f"Friction angle phi={phi} deg is outside Figure 7-14, whose "
            f"curves span about 15-45 deg."
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

# Measured off the printed figure (GEC 12 Vol 1, pdf page index 283, the
# embedded image) on 2026-10-08:
# - x was fitted to the 1-degree gridlines and y to the 25-tsf gridlines;
# - the curve was read as the centre of its stroke at each degree, to about
#   +/- 1 tsf;
# - a second, independent pixel read and both vision models agree.
#
# The axis begins at 30 deg and the curve ends at 43.75 deg (about 368 tsf).
# The earlier table carried nodes at 26/28/44/45 deg that are not on the
# chart, and read high at the loose end (10 tsf at 30 deg, +41 %).
_FIG_7_15_PHI = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 43.75]
_FIG_7_15_QL_TSF = [7.1, 10.1, 16.0, 24.5, 35.9, 53.7, 75.2, 102.3, 133.6,
                    168.3, 208.5, 251.6, 296.0, 339.2, 368.0]
FIG_7_15_PHI_MIN = _FIG_7_15_PHI[0]
FIG_7_15_PHI_MAX = _FIG_7_15_PHI[-1]


def figure_7_15_limiting_toe_resistance(phi: float) -> float:
    """Limiting unit toe resistance qL for cohesionless soils (Figure 7-15).

    Parameters
    ----------
    phi : float
        Soil friction angle at pile toe (degrees), 30 to 43.75 -- the span of
        the printed curve.

    Returns
    -------
    float
        Limiting unit toe resistance qL in tsf.

    Raises
    ------
    ValueError
        If phi is outside 30-43.75 deg. The chart gives no value there:
        below 30 deg the limit is lower than 7.1 tsf, and the curve stops at
        43.75 deg (about 368 tsf).
    """
    if phi < FIG_7_15_PHI_MIN or phi > FIG_7_15_PHI_MAX:
        raise ValueError(
            f"Friction angle phi={phi} deg is outside Figure 7-15, which "
            f"spans {FIG_7_15_PHI_MIN:g}-{FIG_7_15_PHI_MAX:g} deg (the axis "
            f"starts at 30 deg; the curve ends at 43.75 deg, about 368 tsf). "
            f"The chart gives no value here."
        )
    return _linterp(phi, _FIG_7_15_PHI, _FIG_7_15_QL_TSF)


# ============================================================================
# Figure 7-16(a): alpha_t Coefficient (Dimensionless Factor)
# (after Bowles 1977)
#
# Three curves, D/b = 20, 30 and 45, on a log axis; they start at 20 deg
# and merge at about 37 deg. Read at every degree.
# ============================================================================

_FIG_7_16A_PHI = list(range(20, 46))

_FIG_7_16A_AT = {
    20: [0.365, 0.386, 0.406, 0.426, 0.448, 0.470, 0.491, 0.513, 0.536,
         0.559, 0.580, 0.602, 0.625, 0.649, 0.665, 0.682, 0.695, 0.707,
         0.721, 0.736, 0.750, 0.762, 0.774, 0.786, 0.791, 0.800],
    30: [0.257, 0.280, 0.306, 0.333, 0.361, 0.390, 0.418, 0.446, 0.475,
         0.502, 0.531, 0.559, 0.591, 0.621, 0.645, 0.669, 0.690, 0.707,
         0.721, 0.736, 0.750, 0.762, 0.774, 0.786, 0.791, 0.800],
    45: [0.178, 0.202, 0.229, 0.257, 0.288, 0.320, 0.351, 0.384, 0.420,
         0.455, 0.491, 0.526, 0.563, 0.595, 0.625, 0.657, 0.686, 0.707,
         0.721, 0.736, 0.750, 0.762, 0.774, 0.786, 0.791, 0.800],
}


def figure_7_16a_alpha_t(phi: float, D_over_b: float) -> float:
    """Dimensionless alpha_t coefficient for Nordlund toe resistance (Fig 7-16a).

    Linear in phi along each D/b curve, then linear in D/b between the
    curves.

    Parameters
    ----------
    phi : float
        Soil friction angle at pile toe (degrees), 20 to 45 (the curves
        start at 20 deg).
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
    if phi < _FIG_7_16A_PHI[0] or phi > _FIG_7_16A_PHI[-1]:
        raise ValueError(
            f"Friction angle phi={phi} deg is outside Figure 7-16(a), whose "
            f"curves span 20-45 deg."
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
#
# Read at every degree (and checked at every half degree, within 1 %;
# a pixel is 1.3 % in N'q on the log axis). The earlier seven nodes read
# 4-7 % low at 30-40 deg (150 at 40 deg, the figure 160.4).
# ============================================================================

_FIG_7_16B_PHI = list(range(15, 46))
_FIG_7_16B_NQ = [4.83, 5.32, 5.90, 6.56, 7.31, 8.18, 9.19, 10.34, 11.70,
                 13.24, 15.00, 17.1, 19.6, 22.6, 26.0, 30.1, 34.6, 40.0,
                 46.5, 54.3, 63.8, 75.5, 89.8, 107.9, 130.9, 160.4, 194.8,
                 238.7, 296.5, 374.0, 475.0]


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
# One curve per pile type, delta/phi against the displaced volume V
# (ft^3/ft). Curves a to e and g run from V = 0.3 to 1.9 ft^3/ft; curve f
# (H-piles and augercast piles) from 0.08 to 0.52. Read every 0.1 ft^3/ft
# (curve f at its own nodes). The chart gives no single ratio for a pile
# type: delta/phi follows V.
# ============================================================================

_FIG_7_9_V = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4,
              1.5, 1.6, 1.7, 1.8, 1.9]

_FIG_7_9_PILE_TYPES = {
    "pipe_pile": {
        "curve": "a",
        "description": "Pipe piles and non-tapered portion of monotube piles",
        "V": _FIG_7_9_V,
        "delta_phi": [0.344, 0.411, 0.464, 0.514, 0.560, 0.594, 0.627, 0.655,
                      0.678, 0.700, 0.717, 0.735, 0.749, 0.763, 0.777, 0.788,
                      0.798],
    },
    "timber": {
        "curve": "b",
        "description": "Timber piles",
        "V": _FIG_7_9_V,
        "delta_phi": [0.406, 0.467, 0.517, 0.561, 0.603, 0.636, 0.666, 0.694,
                      0.714, 0.734, 0.751, 0.767, 0.781, 0.793, 0.805, 0.816,
                      0.823],
    },
    "precast_concrete": {
        "curve": "c",
        "description": "Precast concrete piles",
        "V": _FIG_7_9_V,
        "delta_phi": [0.467, 0.525, 0.579, 0.629, 0.672, 0.706, 0.738, 0.767,
                      0.789, 0.813, 0.832, 0.849, 0.864, 0.878, 0.892, 0.904,
                      0.913],
    },
    "raymond_step_taper": {
        "curve": "d",
        "description": "Raymond step-taper piles",
        "V": _FIG_7_9_V,
        "delta_phi": [0.574, 0.637, 0.689, 0.737, 0.777, 0.814, 0.846, 0.873,
                      0.895, 0.917, 0.936, 0.953, 0.970, 0.984, 0.998, 1.013,
                      1.023],
    },
    "raymond_uniform_taper": {
        "curve": "e",
        "description": "Raymond uniform taper piles",
        "V": _FIG_7_9_V,
        "delta_phi": [0.803, 0.845, 0.888, 0.925, 0.960, 0.993, 1.025, 1.053,
                      1.081, 1.111, 1.136, 1.160, 1.184, 1.207, 1.230, 1.253,
                      1.270],
    },
    "h_pile": {
        "curve": "f",
        "description": "H-piles and augercast piles",
        "V": [0.08, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.52],
        "delta_phi": [0.731, 0.747, 0.791, 0.823, 0.858, 0.887, 0.933, 0.971,
                      0.979],
    },
    "monotube_tapered": {
        "curve": "g",
        "description": "Tapered portion of monotube piles",
        "V": _FIG_7_9_V,
        "delta_phi": [0.645, 0.696, 0.748, 0.793, 0.827, 0.860, 0.888, 0.914,
                      0.938, 0.959, 0.976, 0.994, 1.009, 1.024, 1.038, 1.052,
                      1.062],
    },
}


def figure_7_9_delta_phi_ratio(pile_type: str, V: float) -> dict:
    """delta/phi for a pile type at displaced volume V (Figure 7-9).

    Linear in V along the pile type's curve.

    Parameters
    ----------
    pile_type : str
        Pile type.  Options: 'pipe_pile' (curve a), 'timber' (b),
        'precast_concrete' (c), 'raymond_step_taper' (d),
        'raymond_uniform_taper' (e), 'h_pile' (f, H-piles and augercast
        piles), 'monotube_tapered' (g, the tapered portion of monotube
        piles).
    V : float
        Displaced soil volume per unit pile length (ft^3/ft): 0.3 to 1.9
        on curves a to e and g, 0.08 to 0.52 on curve f.

    Returns
    -------
    dict
        Keys: delta_phi_ratio, curve, description, V_range.

    Raises
    ------
    ValueError
        If pile type is not recognized, or V is outside its curve.
    """
    key = pile_type.lower().strip().replace(" ", "_").replace("-", "_")

    entry = _FIG_7_9_PILE_TYPES.get(key)
    if entry is None:
        # Partial match
        for k, v in _FIG_7_9_PILE_TYPES.items():
            if key in k or k in key:
                entry = v
                break
    if entry is None:
        raise ValueError(
            f"Unknown pile type '{pile_type}'. "
            f"Available: {', '.join(_FIG_7_9_PILE_TYPES.keys())}"
        )

    vs = entry["V"]
    if V < vs[0] or V > vs[-1]:
        raise ValueError(
            f"Displaced volume V={V} ft^3/ft is outside Figure 7-9's curve "
            f"{entry['curve']} ({entry['description']}), which spans "
            f"{vs[0]:g}-{vs[-1]:g} ft^3/ft. The chart gives no value here."
        )
    return {
        "delta_phi_ratio": _linterp(V, vs, entry["delta_phi"]),
        "curve": entry["curve"],
        "description": entry["description"],
        "V_range": (vs[0], vs[-1]),
    }


# ============================================================================
# Figure 7-17: Adhesion Ca for Piles in Cohesive Soils
# (after Tomlinson 1979)
#
# Solid curves: concrete, timber and corrugated steel piles; dashed: smooth
# steel piles; each at D = 10b and D = 40b, D from the ground surface to
# the bottom of the clay layer. The curves start at su = 0.25 ksf. The
# solid D = 10b curve runs to 3.45 ksf; the solid D = 40b curve starts at
# su = 1.0 ksf (below it the chart has the one solid curve) and runs to
# 3.45 ksf; the dashed curves end at about 3.05 ksf. Ca rises to a peak
# near su = 2 ksf and falls after it. Read every 0.1 ksf.
# ============================================================================

_FIG_7_17_SU = [0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3,
                1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5,
                2.6, 2.7, 2.8, 2.9, 3.0]
_FIG_7_17_SU_SOLID = _FIG_7_17_SU + [3.1, 3.2, 3.3, 3.4, 3.45]
_FIG_7_17_SU_SOLID_40 = _FIG_7_17_SU[8:] + [3.1, 3.2, 3.3, 3.4, 3.45]
_FIG_7_17_SU_STEEL = _FIG_7_17_SU + [3.05]

# Ca (ksf) — concrete, timber, corrugated steel piles
_FIG_7_17_CA_CONCRETE_D10 = [
    0.26, 0.324, 0.413, 0.503, 0.598, 0.691, 0.784, 0.875, 0.948, 1.013,
    1.082, 1.14, 1.188, 1.249, 1.296, 1.333, 1.359, 1.367, 1.369, 1.354,
    1.328, 1.289, 1.222, 1.164, 1.104, 1.052, 1.004, 0.961, 0.922, 0.892,
    0.862, 0.844, 0.832, 0.827,
]
_FIG_7_17_CA_CONCRETE_D40 = [
    1.106, 1.181, 1.263, 1.346, 1.419, 1.497, 1.566, 1.626, 1.695, 1.749,
    1.799, 1.819, 1.819, 1.814, 1.797, 1.767, 1.724, 1.685, 1.633, 1.586,
    1.514, 1.465, 1.429, 1.402, 1.376, 1.367,
]

# Ca (ksf) — smooth steel piles
_FIG_7_17_CA_STEEL_D10 = [
    0.23, 0.257, 0.317, 0.403, 0.49, 0.575, 0.66, 0.737, 0.801, 0.859,
    0.92, 0.965, 1.009, 1.063, 1.108, 1.14, 1.164, 1.168, 1.17, 1.152,
    1.127, 1.084, 1.045, 1.0, 0.946, 0.896, 0.858, 0.821, 0.786, 0.78,
]
_FIG_7_17_CA_STEEL_D40 = [
    0.26, 0.324, 0.413, 0.503, 0.598, 0.691, 0.784, 0.875, 0.948, 1.013,
    1.082, 1.14, 1.243, 1.295, 1.344, 1.406, 1.456, 1.497, 1.516, 1.555,
    1.581, 1.578, 1.555, 1.524, 1.486, 1.464, 1.408, 1.352, 1.294, 1.279,
]

_FIG_7_17_CURVES = {
    "concrete": ("concrete, timber and corrugated steel piles",
                 _FIG_7_17_SU_SOLID, _FIG_7_17_CA_CONCRETE_D10,
                 _FIG_7_17_SU_SOLID_40, _FIG_7_17_CA_CONCRETE_D40),
    "steel": ("smooth steel piles",
              _FIG_7_17_SU_STEEL, _FIG_7_17_CA_STEEL_D10,
              _FIG_7_17_SU_STEEL, _FIG_7_17_CA_STEEL_D40),
}


def figure_7_17_adhesion(su_ksf: float, D_over_b: float = 10.0,
                         pile_surface: str = "concrete") -> float:
    """Pile adhesion Ca for piles in cohesive soils (Figure 7-17).

    Recommended for routine design.  For special stratigraphy cases
    (sand over stiff clay, soft clay over stiff clay, stiff clay only),
    see figure_7_18_adhesion_factor().

    Ca is read as drawn: the D = 40b solid curve passes above Ca = su
    below about 1.5 ksf.

    Parameters
    ----------
    su_ksf : float
        Undrained shear strength (ksf): 0.25 to 3.45 for concrete, timber
        and corrugated steel piles, 0.25 to 3.05 for smooth steel piles.
    D_over_b : float
        Ratio of pile embedment D to pile diameter b.
        Interpolated between D/b=10 and D/b=40.  Clamped to this range.
        Below su = 1.0 ksf the solid D = 40b curve is not drawn and the
        one solid curve is read.
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
        If su_ksf is outside the curves, or pile surface is unknown.
    """
    surface = pile_surface.lower().strip()
    if surface in ("concrete", "timber", "corrugated"):
        name, s10, c10, s40, c40 = _FIG_7_17_CURVES["concrete"]
    elif surface in ("steel", "smooth_steel", "smooth"):
        name, s10, c10, s40, c40 = _FIG_7_17_CURVES["steel"]
    else:
        raise ValueError(
            f"Unknown pile surface '{pile_surface}'. "
            "Use 'concrete' or 'steel'."
        )
    if su_ksf < s10[0] or su_ksf > s10[-1]:
        raise ValueError(
            f"su_ksf={su_ksf} is outside Figure 7-17's curves for {name} "
            f"({s10[0]:g}-{s10[-1]:g} ksf). The chart gives no value here; "
            "past the curves GEC-12 recommends the API method for highly "
            "overconsolidated clays (Section 7.2.1.3.3)."
        )

    D_b = max(10.0, min(40.0, D_over_b))
    ca_d10 = _linterp(su_ksf, s10, c10)
    ca_d40 = ca_d10 if su_ksf < s40[0] else _linterp(su_ksf, s40, c40)

    frac = (D_b - 10.0) / 30.0
    return ca_d10 + frac * (ca_d40 - ca_d10)


# ============================================================================
# Figure 7-18: Adhesion Factor alpha for Driven Piles in Clay
# (Tomlinson 1980) — Three stratigraphy cases
#
# Case 1 (top graph): sands or sandy gravels over stiff clay; curves
#   D < 10b (alpha = 1.0 across the chart), D = 20b and D > 40b.
# Case 2 (middle graph): soft clay over stiff clay; curves D = 10b
#   (su 0.45-4.56 ksf) and D > 20b (su 0.52-4.76 ksf).
# Case 3 (bottom graph): stiff clay without different overlying strata;
#   curves D = 10b and D > 40b.
# D is the penetration into the stiff clay (Case 3: from the ground
# surface). Each curve as (su nodes in ksf, alpha); the Case 1 and Case 3
# curves run along the top of the chart (alpha 1.0) before they fall and
# level off to su = 5 ksf. Read every 0.1 ksf.
# ============================================================================


def _tenths(a: float, b: float) -> list:
    return [round(a + 0.1 * i, 1) for i in range(int(round((b - a) * 10)) + 1)]


# Each case: (D/b, su nodes, alpha nodes) for each curve, shallowest first.
_FIG_7_18_CASES = {
    "sand_over_stiff_clay": [
        (10.0, [0.0, 5.0], [1.0, 1.0]),
        (20.0, [0.0, 1.67, 1.8] + _tenths(1.9, 3.0) + [5.0],
         [1.0, 1.0, 0.982, 0.969, 0.955, 0.938, 0.918, 0.897, 0.866, 0.839,
          0.813, 0.790, 0.770, 0.757, 0.754, 0.752]),
        (40.0, [0.0, 0.57, 0.7] + _tenths(0.8, 3.4) + [5.0],
         [1.0, 1.0, 0.982, 0.969, 0.956, 0.939, 0.922, 0.901, 0.881, 0.856,
          0.830, 0.801, 0.771, 0.744, 0.713, 0.680, 0.647, 0.616, 0.589,
          0.562, 0.532, 0.500, 0.469, 0.444, 0.428, 0.415, 0.403, 0.394,
          0.392, 0.390, 0.390]),
    ],
    "soft_over_stiff_clay": [
        (10.0, [0.45] + _tenths(0.5, 4.5) + [4.56],
         [0.530, 0.519, 0.493, 0.467, 0.439, 0.412, 0.396, 0.380, 0.368,
          0.354, 0.342, 0.333, 0.324, 0.316, 0.307, 0.300, 0.296, 0.295,
          0.291, 0.282, 0.276, 0.272, 0.270, 0.266, 0.258, 0.249, 0.245,
          0.241, 0.237, 0.233, 0.229, 0.225, 0.221, 0.217, 0.213, 0.209,
          0.207, 0.201, 0.199, 0.195, 0.191, 0.185, 0.183]),
        (20.0, [0.52] + _tenths(0.6, 4.7) + [4.76],
         [0.833, 0.814, 0.791, 0.771, 0.756, 0.743, 0.732, 0.720, 0.709,
          0.700, 0.692, 0.685, 0.680, 0.679, 0.676, 0.674, 0.672, 0.670,
          0.666, 0.660, 0.654, 0.650, 0.644, 0.640, 0.632, 0.624, 0.617,
          0.610, 0.606, 0.601, 0.594, 0.589, 0.584, 0.577, 0.571, 0.567,
          0.561, 0.555, 0.551, 0.545, 0.539, 0.533, 0.527, 0.524]),
    ],
    "stiff_clay_only": [
        (10.0, [0.5] + _tenths(0.6, 3.6) + [5.0],
         [0.985, 0.972, 0.959, 0.951, 0.940, 0.924, 0.907, 0.893, 0.876,
          0.854, 0.830, 0.805, 0.782, 0.757, 0.726, 0.691, 0.646, 0.592,
          0.536, 0.487, 0.442, 0.403, 0.372, 0.348, 0.321, 0.295, 0.281,
          0.267, 0.255, 0.247, 0.243, 0.239, 0.238]),
        (40.0, [0.5, 1.55] + _tenths(1.7, 4.2) + [5.0],
         [1.0, 1.0, 0.980, 0.962, 0.936, 0.902, 0.861, 0.819, 0.781, 0.741,
          0.703, 0.662, 0.617, 0.572, 0.535, 0.500, 0.472, 0.446, 0.425,
          0.406, 0.388, 0.373, 0.355, 0.339, 0.326, 0.313, 0.305, 0.299,
          0.300]),
    ],
}

_FIG_7_18_ALIASES = {
    "case1": "sand_over_stiff_clay", "case_1": "sand_over_stiff_clay",
    "case2": "soft_over_stiff_clay", "case_2": "soft_over_stiff_clay",
    "soft_clay_over_stiff_clay": "soft_over_stiff_clay",
    "case3": "stiff_clay_only", "case_3": "stiff_clay_only",
    "stiff_clay": "stiff_clay_only",
}


def figure_7_18_adhesion_factor(
    su_ksf: float,
    D_over_b: float,
    stratigraphy: str = "sand_over_stiff_clay",
) -> float:
    """Adhesion factor alpha for driven piles in clay (Figure 7-18).

    Use only for the specific stratigraphy cases shown.  For routine
    design, prefer figure_7_17_adhesion().

    Linear in su along each curve, then linear in D/b between the
    bracketing curves; D/b outside the curves takes the nearest curve
    (the legends' "D < 10b", "D > 20b" and "D > 40b").

    Parameters
    ----------
    su_ksf : float
        Undrained shear strength of the stiff clay (ksf), within the
        curves read: 0 to 5.0 in Case 1; 0.45-4.56 (D = 10b) and 0.52-4.76
        (D > 20b) in Case 2; 0.5 to 5.0 in Case 3.
    D_over_b : float
        Ratio of pile penetration into the stiff clay to pile diameter
        (Case 3: from the ground surface).
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
        If su_ksf is outside the curves read, or stratigraphy is invalid.
    """
    case = stratigraphy.lower().strip().replace(" ", "_").replace("-", "_")
    case = _FIG_7_18_ALIASES.get(case, case)
    if case not in _FIG_7_18_CASES:
        raise ValueError(
            f"Unknown stratigraphy '{stratigraphy}'. Use: "
            "'sand_over_stiff_clay', 'soft_over_stiff_clay', "
            "or 'stiff_clay_only'."
        )

    curves = _FIG_7_18_CASES[case]
    if D_over_b <= curves[0][0]:
        used = [(1.0, curves[0])]
    elif D_over_b >= curves[-1][0]:
        used = [(1.0, curves[-1])]
    else:
        for lo, hi in zip(curves[:-1], curves[1:]):
            if D_over_b <= hi[0]:
                w = (D_over_b - lo[0]) / (hi[0] - lo[0])
                used = [(1.0 - w, lo), (w, hi)]
                break

    start = max(c[1][0] for w, c in used if w > 0)
    end = min(c[1][-1] for w, c in used if w > 0)
    if su_ksf < start or su_ksf > end:
        raise ValueError(
            f"su_ksf={su_ksf} is outside Figure 7-18's {case} curves read "
            f"at D/b={D_over_b} ({start:g}-{end:g} ksf). The chart gives no "
            "value here."
        )
    return sum(w * _linterp(su_ksf, c[1], c[2]) for w, c in used)
