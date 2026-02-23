"""GEC-6 figure lookup functions.

Digitized figures from FHWA-SA-02-054 (GEC-6), Shallow Foundations.
Follows the DM7 pattern: private data with ``_FIG_*`` prefix, public
lookup functions with ``_linterp`` interpolation.
"""

import math

from geotech_references._interpolation import _linterp


# ============================================================================
# Figure 4-1: Correlation Between Relative Density and SPT Resistance
# (NAVFAC, 1986a, after Gibbs & Holtz)
# X-axis: SPT N (blows/ft), Y-axis: vertical effective stress (ksf)
# Curves for relative density Dr = 15, 40, 50, 60, 70, 80, 85, 90, 100%
#
# Digitized at key stress levels. Original units: ksf and blows/ft.
# The chart assumes a rope and cathead hammer (60% efficiency).
# ============================================================================

_FIG_4_1_DR = [15, 40, 50, 60, 70, 80, 85, 90, 100]

# SPT N values at sigma'v = 0.5 ksf (24 kPa)
_FIG_4_1_N_AT_05 = [1, 3, 5, 7, 10, 15, 18, 22, 33]
# SPT N values at sigma'v = 1.0 ksf (48 kPa)
_FIG_4_1_N_AT_10 = [2, 5, 7, 10, 15, 22, 27, 33, 48]
# SPT N values at sigma'v = 2.0 ksf (96 kPa)
_FIG_4_1_N_AT_20 = [3, 8, 11, 15, 22, 32, 38, 47, 65]
# SPT N values at sigma'v = 4.0 ksf (192 kPa)
_FIG_4_1_N_AT_40 = [4, 12, 16, 22, 33, 47, 55, 65, 80]

_FIG_4_1_STRESS_KSF = [0.5, 1.0, 2.0, 4.0]
_FIG_4_1_N_TABLE = [_FIG_4_1_N_AT_05, _FIG_4_1_N_AT_10,
                    _FIG_4_1_N_AT_20, _FIG_4_1_N_AT_40]


def figure_4_1_relative_density_spt(n_value: float,
                                    sigma_v_kpa: float) -> float:
    """Relative density from SPT N-value and vertical effective stress.

    Figure 4-1 correlation (NAVFAC 1986a, after Gibbs & Holtz).
    Assumes rope and cathead hammer with 60% efficiency.

    Parameters
    ----------
    n_value : float
        SPT blow count (blows per 0.3 m / 1 ft). Uncorrected for
        hammer efficiency (chart assumes 60% efficiency).
    sigma_v_kpa : float
        Vertical effective overburden stress in kPa (24 to 192 kPa).

    Returns
    -------
    float
        Estimated relative density in percent (15 to 100).

    Raises
    ------
    ValueError
        If inputs are outside the chart range.
    """
    if sigma_v_kpa < 24 or sigma_v_kpa > 192:
        raise ValueError(
            f"sigma_v_kpa must be 24-192 kPa (0.5-4.0 ksf), got {sigma_v_kpa}"
        )
    if n_value < 0:
        raise ValueError(f"n_value must be non-negative, got {n_value}")

    # Convert kPa to ksf (1 ksf = 47.88 kPa)
    sigma_v_ksf = sigma_v_kpa / 47.88

    # Interpolate N values for each Dr at the given stress level
    n_at_stress = []
    for i, dr in enumerate(_FIG_4_1_DR):
        n_values_at_stress_levels = [row[i] for row in _FIG_4_1_N_TABLE]
        n_interp = _linterp(sigma_v_ksf, _FIG_4_1_STRESS_KSF,
                            n_values_at_stress_levels)
        n_at_stress.append(n_interp)

    # Now interpolate Dr from N
    if n_value <= n_at_stress[0]:
        return float(_FIG_4_1_DR[0])
    if n_value >= n_at_stress[-1]:
        return float(_FIG_4_1_DR[-1])

    return _linterp(n_value, n_at_stress, [float(d) for d in _FIG_4_1_DR])


# ============================================================================
# Figure 5-19: Bearing Capacity Index C' vs Corrected SPT (Hough, 1959)
# Multiple curves for different soil types.
# Digitized at key N' values.
# ============================================================================

# N' (corrected SPT) data points for each soil type curve
_FIG_5_19_N = [0, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# C' values for each soil type at the N' data points
_FIG_5_19_CURVES = {
    "inorganic_silt": [
        0, 10, 20, 30, 40, 55, 68, 78, 87, 95, 102, 108, 114,
    ],
    "sandy_clay": [
        0, 12, 23, 34, 45, 62, 76, 88, 98, 107, 115, 122, 128,
    ],
    "clean_fine_to_medium_sand": [
        0, 14, 27, 40, 53, 75, 93, 108, 121, 133, 144, 154, 163,
    ],
    "well_graded_sand_gravel": [
        0, 18, 35, 50, 65, 92, 115, 135, 152, 168, 182, 195, 207,
    ],
    "clean_uniform_medium_sand": [
        0, 22, 42, 60, 78, 110, 138, 162, 183, 202, 219, 234, 248,
    ],
    "coarse_sand": [
        0, 25, 48, 70, 90, 125, 155, 182, 205, 225, 243, 259, 273,
    ],
}


def figure_5_19_hough_bearing_capacity_index(n_prime: float,
                                             soil_type: str
                                             ) -> float:
    """Bearing capacity index C' from corrected SPT N' (Figure 5-19).

    Used in the Hough method for settlement estimation (Eq 5-24).
    C' is used as: delta_H = H0 * (1/C') * log10((sigma'vo + delta_sigma) / sigma'vo)

    Parameters
    ----------
    n_prime : float
        Corrected SPT N-value (corrected for overburden pressure), 0-100.
    soil_type : str
        Soil type. Options: 'inorganic_silt', 'sandy_clay',
        'clean_fine_to_medium_sand', 'well_graded_sand_gravel',
        'clean_uniform_medium_sand', 'coarse_sand'.

    Returns
    -------
    float
        Bearing capacity index C' (dimensionless).

    Raises
    ------
    ValueError
        If soil_type is not recognized or n_prime is outside range.
    """
    if n_prime < 0 or n_prime > 100:
        raise ValueError(f"n_prime must be 0-100, got {n_prime}")

    key = soil_type.lower().strip().replace(" ", "_")

    if key in _FIG_5_19_CURVES:
        return _linterp(n_prime, _FIG_5_19_N, _FIG_5_19_CURVES[key])

    # Try partial match
    for k, v in _FIG_5_19_CURVES.items():
        if key in k or k in key:
            return _linterp(n_prime, _FIG_5_19_N, v)

    raise ValueError(
        f"Unknown soil_type '{soil_type}'. Options: "
        f"{', '.join(_FIG_5_19_CURVES.keys())}"
    )


# ============================================================================
# Figure 4-2: Friction Angle vs Dry Unit Weight (NAVFAC, 1986a)
# For coarse-grained soils. Approximate curve for Dr=0 (lower bound).
# ============================================================================

_FIG_4_2_GAMMA_D_KNM3 = [12.6, 14.1, 15.7, 17.3, 18.9, 20.4, 22.0, 23.6]
_FIG_4_2_PHI_DR0 = [25, 27, 29, 30, 31, 32, 33, 34]
_FIG_4_2_PHI_DR50 = [29, 31, 33, 34, 35, 36, 37, 38]
_FIG_4_2_PHI_DR100 = [33, 35, 37, 39, 40, 42, 43, 45]


def figure_4_2_friction_angle_from_density(gamma_d_kNm3: float,
                                           relative_density_pct: float = 50
                                           ) -> float:
    """Friction angle from dry unit weight and relative density (Figure 4-2).

    For coarse-grained soils (NAVFAC, 1986a).

    Parameters
    ----------
    gamma_d_kNm3 : float
        Dry unit weight in kN/m^3 (12.6 to 23.6).
    relative_density_pct : float
        Relative density in percent (0 to 100). Default 50%.

    Returns
    -------
    float
        Estimated friction angle in degrees.

    Raises
    ------
    ValueError
        If inputs are outside chart range.
    """
    if gamma_d_kNm3 < 12.6 or gamma_d_kNm3 > 23.6:
        raise ValueError(
            f"gamma_d must be 12.6-23.6 kN/m^3, got {gamma_d_kNm3}"
        )
    if relative_density_pct < 0 or relative_density_pct > 100:
        raise ValueError(
            f"relative_density must be 0-100%, got {relative_density_pct}"
        )

    phi_0 = _linterp(gamma_d_kNm3, _FIG_4_2_GAMMA_D_KNM3, _FIG_4_2_PHI_DR0)
    phi_50 = _linterp(gamma_d_kNm3, _FIG_4_2_GAMMA_D_KNM3, _FIG_4_2_PHI_DR50)
    phi_100 = _linterp(gamma_d_kNm3, _FIG_4_2_GAMMA_D_KNM3, _FIG_4_2_PHI_DR100)

    dr = relative_density_pct
    if dr <= 50:
        return _linterp(dr, [0, 50], [phi_0, phi_50])
    else:
        return _linterp(dr, [50, 100], [phi_50, phi_100])
