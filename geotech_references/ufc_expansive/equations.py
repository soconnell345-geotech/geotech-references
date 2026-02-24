"""UFC 3-220-07 expansive soil equations.

Activity index, free swell estimation (Seed et al. 1962), swell
pressure correlations, heave prediction (layer summation), and
pier minimum embedment.  All units SI.
"""

import math


def activity_index(plasticity_index, clay_fraction_pct):
    """Calculate Skempton's activity index.

    ::

        A = PI / (% finer than 2 um)

    Parameters
    ----------
    plasticity_index : float
        Plasticity index (%).
    clay_fraction_pct : float
        Percentage of particles finer than 2 um (%).

    Returns
    -------
    dict
        Keys: activity, classification (inactive/normal/active/highly_active).

    Raises
    ------
    ValueError
        If inputs are non-positive or clay_fraction_pct > 100.
    """
    if plasticity_index <= 0:
        raise ValueError(
            f"plasticity_index must be > 0, got {plasticity_index}"
        )
    if clay_fraction_pct <= 0:
        raise ValueError(
            f"clay_fraction_pct must be > 0, got {clay_fraction_pct}"
        )
    if clay_fraction_pct > 100:
        raise ValueError(
            f"clay_fraction_pct must be <= 100, got {clay_fraction_pct}"
        )

    A = plasticity_index / clay_fraction_pct

    if A < 0.75:
        classification = "inactive"
    elif A < 1.25:
        classification = "normal"
    elif A < 2.0:
        classification = "active"
    else:
        classification = "highly_active"

    return {
        "activity": round(A, 3),
        "classification": classification,
    }


def free_swell_percent(plasticity_index):
    """Estimate free swell from plasticity index (Seed et al. 1962).

    ::

        S_free (%) = 2.16e-3 * PI^2.44

    Parameters
    ----------
    plasticity_index : float
        Plasticity index (%).  Valid range approx 10-70.

    Returns
    -------
    float
        Estimated free swell (%).

    Raises
    ------
    ValueError
        If plasticity_index <= 0.
    """
    if plasticity_index <= 0:
        raise ValueError(
            f"plasticity_index must be > 0, got {plasticity_index}"
        )

    return 2.16e-3 * plasticity_index ** 2.44


def swell_pressure_kPa(
    plasticity_index,
    dry_density_kN_per_m3,
    moisture_content_pct,
):
    """Estimate swell pressure from index properties (Komornik & David 1969).

    ::

        log10(p_s) = 2.132 + 0.0208 * LL + 0.000665 * gamma_d - 0.0269 * w

    Approximated here using PI in place of LL (LL ~ PI + PL, typical
    PL ~ 20, so LL ~ PI + 20).  Units: p_s in kPa, gamma_d in kN/m³,
    w in %.

    Parameters
    ----------
    plasticity_index : float
        Plasticity index (%).
    dry_density_kN_per_m3 : float
        Dry unit weight (kN/m³).
    moisture_content_pct : float
        Natural moisture content (%).

    Returns
    -------
    float
        Estimated swell pressure (kPa).

    Raises
    ------
    ValueError
        If inputs are non-positive.
    """
    PI = plasticity_index
    gd = dry_density_kN_per_m3
    w = moisture_content_pct

    if PI <= 0:
        raise ValueError(f"plasticity_index must be > 0, got {PI}")
    if gd <= 0:
        raise ValueError(f"dry_density_kN_per_m3 must be > 0, got {gd}")
    if w <= 0:
        raise ValueError(f"moisture_content_pct must be > 0, got {w}")

    # Approximate LL from PI (assume typical PL ~ 20)
    LL = PI + 20.0
    log_ps = 2.132 + 0.0208 * LL + 0.000665 * gd - 0.0269 * w
    return round(10.0 ** log_ps, 1)


def heave_prediction_mm(layers):
    """Predict total heave using the layer summation method.

    ::

        delta_H = sum(epsilon_i * H_i)

    where epsilon_i is the swell strain (decimal) and H_i is layer
    thickness (m) for each layer within the active zone.

    Parameters
    ----------
    layers : list of dict
        Each dict must have:
        - thickness_m (float): layer thickness (m)
        - swell_strain_pct (float): swell strain (%)

    Returns
    -------
    dict
        Keys: total_heave_mm, layer_heaves_mm (list of float),
        number_of_layers.

    Raises
    ------
    ValueError
        If layers is empty or any value is non-positive.
    """
    if not layers:
        raise ValueError("layers list must not be empty")

    layer_heaves = []
    for i, layer in enumerate(layers):
        t = layer["thickness_m"]
        s = layer["swell_strain_pct"]
        if t <= 0:
            raise ValueError(f"Layer {i}: thickness_m must be > 0, got {t}")
        if s < 0:
            raise ValueError(
                f"Layer {i}: swell_strain_pct must be >= 0, got {s}"
            )
        heave_mm = (s / 100.0) * t * 1000.0  # convert m to mm
        layer_heaves.append(round(heave_mm, 1))

    return {
        "total_heave_mm": round(sum(layer_heaves), 1),
        "layer_heaves_mm": layer_heaves,
        "number_of_layers": len(layers),
    }


def pier_minimum_embedment_m(active_zone_depth_m, factor=1.5):
    """Minimum pier embedment depth in expansive soils.

    Piers must extend through the active zone and be anchored into
    stable material below.  Minimum embedment::

        D_min = active_zone_depth + anchorage

    where anchorage = factor * active_zone_depth (typically the pier
    is embedded at least 1.5x the active zone depth, or a minimum of
    1 m into stable soil, whichever is greater).

    Parameters
    ----------
    active_zone_depth_m : float
        Depth of the active (moisture-change) zone (m).
    factor : float, optional
        Multiplier for total embedment (default 1.5, i.e. pier tip
        at 1.5 * active zone depth).

    Returns
    -------
    dict
        Keys: min_embedment_m, active_zone_depth_m,
        anchorage_below_active_zone_m.

    Raises
    ------
    ValueError
        If active_zone_depth_m <= 0 or factor < 1.
    """
    if active_zone_depth_m <= 0:
        raise ValueError(
            f"active_zone_depth_m must be > 0, got {active_zone_depth_m}"
        )
    if factor < 1.0:
        raise ValueError(f"factor must be >= 1.0, got {factor}")

    total = factor * active_zone_depth_m
    # Minimum 1 m anchorage below the active zone
    anchorage = max(total - active_zone_depth_m, 1.0)
    min_embed = active_zone_depth_m + anchorage

    return {
        "min_embedment_m": round(min_embed, 2),
        "active_zone_depth_m": active_zone_depth_m,
        "anchorage_below_active_zone_m": round(anchorage, 2),
    }
