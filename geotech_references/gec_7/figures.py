"""GEC-7 figure lookup functions.

Digitized figures from FHWA-NHI-14-007 (GEC-7), Soil Nail Walls.
Follows the DM7 pattern: private data with ``_FIG_*`` prefix, public
lookup functions with ``_linterp`` interpolation.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Figure 4.3: Friction Angle vs SPT N60 (Schmertmann, 1975)
# X-axis: SPT N60 (blows/ft), Y-axis: friction angle (degrees)
# Family of curves for sigma'vo/Pa = 0.5, 1.0, 1.5, 2.0, 2.5, 3.0
# where Pa = atmospheric pressure (~101.3 kPa)
#
# Digitized at key N60 values from Figure 4.3 of GEC-7.
# ============================================================================

_FIG_4_3_SIGMA_RATIOS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

_FIG_4_3_N60 = [0, 5, 10, 15, 20, 30, 40, 50, 60, 70]

# Friction angle (degrees) at each N60 value for each sigma'vo/Pa curve
_FIG_4_3_PHI = {
    0.5: [28, 30, 33, 35, 37, 40, 42, 44, 45, 46],
    1.0: [28, 29, 31, 33, 35, 38, 40, 42, 43, 44],
    1.5: [28, 29, 30, 32, 34, 37, 39, 41, 42, 43],
    2.0: [28, 29, 30, 31, 33, 36, 38, 40, 41, 42],
    2.5: [28, 28, 29, 31, 32, 35, 37, 39, 40, 41],
    3.0: [28, 28, 29, 30, 32, 34, 37, 38, 39, 40],
}


def figure_4_3_friction_angle_spt(n60: float,
                                  sigma_v_ratio: float) -> float:
    """Friction angle from SPT N60 and effective overburden stress ratio.

    Figure 4.3 correlation (Schmertmann, 1975). Estimates the drained
    friction angle for cohesionless soils from SPT N60 and vertical
    effective stress normalized by atmospheric pressure.

    Parameters
    ----------
    n60 : float
        SPT blow count corrected for 60% hammer efficiency (blows/ft).
        Range 0 to 70.
    sigma_v_ratio : float
        Ratio of vertical effective overburden stress to atmospheric
        pressure (sigma'vo / Pa). Pa ~ 101.3 kPa. Range 0.5 to 3.0.

    Returns
    -------
    float
        Estimated friction angle in degrees.

    Raises
    ------
    ValueError
        If inputs are outside the chart range.
    """
    if n60 < 0 or n60 > 70:
        raise ValueError(f"n60 must be 0-70, got {n60}")
    if sigma_v_ratio < 0.5 or sigma_v_ratio > 3.0:
        raise ValueError(
            f"sigma_v_ratio must be 0.5-3.0, got {sigma_v_ratio}"
        )

    # Interpolate phi at each stress ratio for the given N60
    phi_at_ratios = []
    for ratio in _FIG_4_3_SIGMA_RATIOS:
        phi = _linterp(n60, _FIG_4_3_N60, _FIG_4_3_PHI[ratio])
        phi_at_ratios.append(phi)

    # Interpolate between stress ratios
    return _linterp(sigma_v_ratio, _FIG_4_3_SIGMA_RATIOS, phi_at_ratios)


# ============================================================================
# Figure 5.11: Bearing Capacity Factor Nc for Basal Heave
# (Terzaghi et al. 1996, Sabatini et al. 1999)
# X-axis: H/Be (excavation depth / excavation width)
# Curves for Be/Le = 0 (long excavation), 0.5, and 1.0 (square)
# ============================================================================

_FIG_5_11_H_BE = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]

# Nc values for each Be/Le ratio
_FIG_5_11_NC = {
    0.0: [5.14, 5.14, 5.5, 5.7, 5.9, 6.0, 6.1, 6.15, 6.2, 6.2],
    0.5: [5.14, 5.6, 6.3, 6.8, 7.1, 7.3, 7.4, 7.45, 7.5, 7.5],
    1.0: [5.14, 6.2, 7.2, 7.9, 8.3, 8.6, 8.8, 8.9, 9.0, 9.0],
}

_FIG_5_11_BE_LE = [0.0, 0.5, 1.0]


def figure_5_11_basal_heave_nc(h_be: float,
                               be_le: float = 0.0) -> float:
    """Bearing capacity factor Nc for basal heave evaluation (Figure 5.11).

    Used to evaluate the potential for basal heave beneath a soil nail
    wall excavation in fine-grained soils. Based on Terzaghi et al.
    (1996) and Sabatini et al. (1999).

    Parameters
    ----------
    h_be : float
        Ratio of excavation depth H to excavation width Be. Range 0 to 5.
    be_le : float
        Ratio of excavation width Be to excavation length Le.
        0 = long rectangular excavation, 1 = square excavation.
        Default 0.0 (conservative, long excavation). Range 0 to 1.

    Returns
    -------
    float
        Bearing capacity factor Nc (dimensionless).

    Raises
    ------
    ValueError
        If inputs are outside the chart range.
    """
    if h_be < 0 or h_be > 5.0:
        raise ValueError(f"h_be must be 0-5.0, got {h_be}")
    if be_le < 0 or be_le > 1.0:
        raise ValueError(f"be_le must be 0-1.0, got {be_le}")

    # Interpolate Nc at each Be/Le ratio for the given H/Be
    nc_at_ratios = []
    for ratio in _FIG_5_11_BE_LE:
        nc = _linterp(h_be, _FIG_5_11_H_BE, _FIG_5_11_NC[ratio])
        nc_at_ratios.append(nc)

    # Interpolate between Be/Le ratios
    return _linterp(be_le, _FIG_5_11_BE_LE, nc_at_ratios)
