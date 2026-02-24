"""UFC 3-220-05 dewatering equations.

Steady-state well flow (Thiem/Dupuit), radius of influence,
wellpoint spacing, equivalent well radius, and superposition
of drawdown from multiple wells.  All units SI.
"""

import math


def thiem_confined_flow_m3_per_s(
    k_m_per_s,
    aquifer_thickness_m,
    drawdown_m,
    radius_of_influence_m,
    well_radius_m,
):
    """Steady-state pumping rate for a single well in a confined aquifer.

    Thiem (1906) equation::

        Q = 2 * pi * T * s / ln(R / r_w)

    where T = k * H (transmissivity).

    Parameters
    ----------
    k_m_per_s : float
        Hydraulic conductivity (m/s).
    aquifer_thickness_m : float
        Confined aquifer thickness, H (m).
    drawdown_m : float
        Drawdown at the well, s (m).  Must be < aquifer_thickness_m.
    radius_of_influence_m : float
        Radius of influence, R (m).
    well_radius_m : float
        Well radius, r_w (m).

    Returns
    -------
    float
        Pumping rate Q (m³/s).

    Raises
    ------
    ValueError
        If inputs are non-positive, drawdown >= aquifer thickness,
        or R <= r_w.
    """
    k, H, s, R, rw = (k_m_per_s, aquifer_thickness_m, drawdown_m,
                       radius_of_influence_m, well_radius_m)
    if k <= 0:
        raise ValueError(f"k_m_per_s must be > 0, got {k}")
    if H <= 0:
        raise ValueError(f"aquifer_thickness_m must be > 0, got {H}")
    if s <= 0:
        raise ValueError(f"drawdown_m must be > 0, got {s}")
    if s >= H:
        raise ValueError(
            f"drawdown_m ({s}) must be < aquifer_thickness_m ({H})"
        )
    if R <= 0:
        raise ValueError(f"radius_of_influence_m must be > 0, got {R}")
    if rw <= 0:
        raise ValueError(f"well_radius_m must be > 0, got {rw}")
    if R <= rw:
        raise ValueError(
            f"radius_of_influence_m ({R}) must be > well_radius_m ({rw})"
        )

    T = k * H
    Q = 2.0 * math.pi * T * s / math.log(R / rw)
    return Q


def dupuit_unconfined_flow_m3_per_s(
    k_m_per_s,
    initial_head_m,
    well_head_m,
    radius_of_influence_m,
    well_radius_m,
):
    """Steady-state pumping rate for a single well in an unconfined aquifer.

    Dupuit (1863) equation::

        Q = pi * k * (H² - h²) / ln(R / r_w)

    Parameters
    ----------
    k_m_per_s : float
        Hydraulic conductivity (m/s).
    initial_head_m : float
        Initial (static) water table height above base, H (m).
    well_head_m : float
        Water level in the well above base, h (m).  Must be < H.
    radius_of_influence_m : float
        Radius of influence, R (m).
    well_radius_m : float
        Well radius, r_w (m).

    Returns
    -------
    float
        Pumping rate Q (m³/s).

    Raises
    ------
    ValueError
        If inputs are non-positive, h >= H, or R <= r_w.
    """
    k, H, h, R, rw = (k_m_per_s, initial_head_m, well_head_m,
                       radius_of_influence_m, well_radius_m)
    if k <= 0:
        raise ValueError(f"k_m_per_s must be > 0, got {k}")
    if H <= 0:
        raise ValueError(f"initial_head_m must be > 0, got {H}")
    if h < 0:
        raise ValueError(f"well_head_m must be >= 0, got {h}")
    if h >= H:
        raise ValueError(
            f"well_head_m ({h}) must be < initial_head_m ({H})"
        )
    if R <= 0:
        raise ValueError(f"radius_of_influence_m must be > 0, got {R}")
    if rw <= 0:
        raise ValueError(f"well_radius_m must be > 0, got {rw}")
    if R <= rw:
        raise ValueError(
            f"radius_of_influence_m ({R}) must be > well_radius_m ({rw})"
        )

    Q = math.pi * k * (H**2 - h**2) / math.log(R / rw)
    return Q


def radius_of_influence_m(k_m_per_s, drawdown_m):
    """Estimate radius of influence using Sichardt (1928) formula.

    ::

        R = 3000 * s * sqrt(k)

    where k is in m/s, s in m, R in m.

    Parameters
    ----------
    k_m_per_s : float
        Hydraulic conductivity (m/s).
    drawdown_m : float
        Drawdown at the well (m).

    Returns
    -------
    float
        Estimated radius of influence R (m).

    Raises
    ------
    ValueError
        If inputs are non-positive.
    """
    if k_m_per_s <= 0:
        raise ValueError(f"k_m_per_s must be > 0, got {k_m_per_s}")
    if drawdown_m <= 0:
        raise ValueError(f"drawdown_m must be > 0, got {drawdown_m}")

    return 3000.0 * drawdown_m * math.sqrt(k_m_per_s)


def wellpoint_spacing_m(
    total_flow_m3_per_s,
    flow_per_wellpoint_m3_per_s,
):
    """Calculate required wellpoint spacing from flow rates.

    Parameters
    ----------
    total_flow_m3_per_s : float
        Total inflow to be intercepted (m³/s).
    flow_per_wellpoint_m3_per_s : float
        Capacity of a single wellpoint (m³/s).

    Returns
    -------
    dict
        Keys: number_of_wellpoints (int, rounded up),
        spacing_m (float, assuming perimeter installation),
        notes.

    Raises
    ------
    ValueError
        If inputs are non-positive.
    """
    if total_flow_m3_per_s <= 0:
        raise ValueError(
            f"total_flow_m3_per_s must be > 0, got {total_flow_m3_per_s}"
        )
    if flow_per_wellpoint_m3_per_s <= 0:
        raise ValueError(
            f"flow_per_wellpoint_m3_per_s must be > 0, got "
            f"{flow_per_wellpoint_m3_per_s}"
        )

    n = math.ceil(total_flow_m3_per_s / flow_per_wellpoint_m3_per_s)
    return {
        "number_of_wellpoints": n,
        "notes": "Spacing depends on perimeter length; divide perimeter by n",
    }


def equivalent_well_radius_m(length_m, width_m=None):
    """Equivalent radius for a rectangular or linear well array.

    For a rectangular excavation of dimensions *L x W*::

        r_eq = sqrt(L * W / pi)

    For a long, narrow (linear) array of length *L*::

        r_eq = L / pi

    Parameters
    ----------
    length_m : float
        Length of excavation or array (m).
    width_m : float, optional
        Width of excavation (m).  If None, assumes a linear array.

    Returns
    -------
    float
        Equivalent well radius r_eq (m).

    Raises
    ------
    ValueError
        If length_m <= 0 or width_m <= 0.
    """
    if length_m <= 0:
        raise ValueError(f"length_m must be > 0, got {length_m}")

    if width_m is not None:
        if width_m <= 0:
            raise ValueError(f"width_m must be > 0, got {width_m}")
        return math.sqrt(length_m * width_m / math.pi)

    return length_m / math.pi


def superposition_drawdown_m(
    transmissivity_m2_per_s,
    wells,
    point_x_m,
    point_y_m,
    radius_of_influence_m,
):
    """Drawdown at a point due to multiple pumping wells (superposition).

    Assumes steady-state confined conditions.  Drawdown from each well::

        s_i = Q_i / (2 * pi * T) * ln(R / r_i)

    where *r_i* is the distance from well *i* to the observation point.

    Parameters
    ----------
    transmissivity_m2_per_s : float
        Aquifer transmissivity T (m²/s).
    wells : list of dict
        Each dict has keys: x_m, y_m, Q_m3_per_s (pumping rate, positive
        for extraction).
    point_x_m : float
        X-coordinate of observation point (m).
    point_y_m : float
        Y-coordinate of observation point (m).
    radius_of_influence_m : float
        Radius of influence R (m).

    Returns
    -------
    dict
        Keys: total_drawdown_m, individual_drawdowns_m (list of float).

    Raises
    ------
    ValueError
        If T <= 0, R <= 0, wells list is empty, or observation point
        coincides with a well.
    """
    T = transmissivity_m2_per_s
    R = radius_of_influence_m

    if T <= 0:
        raise ValueError(
            f"transmissivity_m2_per_s must be > 0, got {T}"
        )
    if R <= 0:
        raise ValueError(
            f"radius_of_influence_m must be > 0, got {R}"
        )
    if not wells:
        raise ValueError("wells list must not be empty")

    individual = []
    for i, w in enumerate(wells):
        dx = point_x_m - w["x_m"]
        dy = point_y_m - w["y_m"]
        r = math.sqrt(dx**2 + dy**2)
        if r < 1e-6:
            raise ValueError(
                f"Observation point coincides with well {i} "
                f"at ({w['x_m']}, {w['y_m']})"
            )
        # Clamp r to R — beyond R, drawdown is zero
        if r >= R:
            individual.append(0.0)
        else:
            s_i = w["Q_m3_per_s"] / (2.0 * math.pi * T) * math.log(R / r)
            individual.append(round(s_i, 4))

    return {
        "total_drawdown_m": round(sum(individual), 4),
        "individual_drawdowns_m": individual,
    }
