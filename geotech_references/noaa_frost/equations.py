"""NOAA frost depth computation equations.

Physics-based equations for frost penetration depth estimation.
All units SI: meters, Kelvin, Watts, Joules.

References:
    Stefan (1891) frost penetration formula
    Berggren (1943) modified frost depth equation
    Aldrich & Paynter (1953) modified Berggren method
    ASCE 32-01: Design and Construction of Frost-Protected Shallow Foundations
"""

import math


def stefan_frost_depth_m(freezing_index_degC_days: float,
                         k_frozen_W_per_mK: float,
                         L_J_per_m3: float) -> float:
    """Frost penetration depth using the Stefan equation.

    The Stefan equation gives the maximum frost depth assuming a step
    change in surface temperature:

        d = sqrt(2 * k_f * FI * 86400 / L)

    where FI is the freezing index (degree-days), k_f is frozen
    thermal conductivity, and L is volumetric latent heat.

    Parameters
    ----------
    freezing_index_degC_days : float
        Air freezing index (degree-C days). Must be positive.
        Cumulative sum of (0 - T_mean) for days with T_mean < 0 C.
    k_frozen_W_per_mK : float
        Frozen thermal conductivity of soil (W/m-K). Must be positive.
    L_J_per_m3 : float
        Volumetric latent heat of soil (J/m^3). Must be positive.

    Returns
    -------
    float
        Maximum frost penetration depth (m).

    Raises
    ------
    ValueError
        If any parameter is not positive.
    """
    if freezing_index_degC_days <= 0:
        raise ValueError(
            f"freezing_index must be positive, got {freezing_index_degC_days}"
        )
    if k_frozen_W_per_mK <= 0:
        raise ValueError(
            f"k_frozen must be positive, got {k_frozen_W_per_mK}"
        )
    if L_J_per_m3 <= 0:
        raise ValueError(f"L must be positive, got {L_J_per_m3}")

    return math.sqrt(
        2.0 * k_frozen_W_per_mK * freezing_index_degC_days * 86400.0
        / L_J_per_m3
    )


def modified_berggren_frost_depth_m(freezing_index_degC_days: float,
                                    k_avg_W_per_mK: float,
                                    n_factor: float,
                                    L_J_per_m3: float,
                                    lambda_coeff: float) -> float:
    """Frost depth using the modified Berggren equation.

    Accounts for initial soil temperature and surface transfer effects
    via the dimensionless lambda coefficient:

        d = lambda * sqrt(2 * k_avg * n * FI * 86400 / L)

    Parameters
    ----------
    freezing_index_degC_days : float
        Air freezing index (degree-C days). Must be positive.
    k_avg_W_per_mK : float
        Average thermal conductivity of frozen and unfrozen soil (W/m-K).
        Typically k_avg = (k_frozen + k_unfrozen) / 2. Must be positive.
    n_factor : float
        Surface n-factor converting air freezing index to surface
        freezing index (dimensionless, 0 < n <= 1.0).
    L_J_per_m3 : float
        Volumetric latent heat of soil (J/m^3). Must be positive.
    lambda_coeff : float
        Berggren correction factor (dimensionless, 0 < lambda <= 1.0).
        Accounts for initial soil temperature above freezing.

    Returns
    -------
    float
        Maximum frost penetration depth (m).

    Raises
    ------
    ValueError
        If parameters are out of valid range.
    """
    if freezing_index_degC_days <= 0:
        raise ValueError(
            f"freezing_index must be positive, got {freezing_index_degC_days}"
        )
    if k_avg_W_per_mK <= 0:
        raise ValueError(
            f"k_avg must be positive, got {k_avg_W_per_mK}"
        )
    if not (0 < n_factor <= 1.0):
        raise ValueError(
            f"n_factor must be in (0, 1.0], got {n_factor}"
        )
    if L_J_per_m3 <= 0:
        raise ValueError(f"L must be positive, got {L_J_per_m3}")
    if not (0 < lambda_coeff <= 1.0):
        raise ValueError(
            f"lambda_coeff must be in (0, 1.0], got {lambda_coeff}"
        )

    return lambda_coeff * math.sqrt(
        2.0 * k_avg_W_per_mK * n_factor
        * freezing_index_degC_days * 86400.0 / L_J_per_m3
    )


def berggren_lambda(mu: float, alpha: float) -> float:
    """Berggren dimensionless correction factor (lambda).

    Approximation of the Berggren lambda coefficient as a function
    of the thermal ratio mu and the fusion parameter alpha.

    For mu = 0 (initial temperature at freezing), lambda = 1.0.
    For mu > 0 (initial temperature above freezing), lambda < 1.0.

    Approximation (Aldrich & Paynter 1953):
        lambda = 1 / sqrt(1 + mu * (1 + 0.5 * alpha * mu))

    where:
        mu = v_s * t / (FI * n)   (thermal ratio)
        alpha = C / L * v_s       (fusion parameter)

    Parameters
    ----------
    mu : float
        Thermal ratio (dimensionless, >= 0). Ratio of initial soil
        temperature effect to freezing index. mu = 0 means soil starts
        at exactly 0 C.
    alpha : float
        Fusion parameter (dimensionless, >= 0). Ratio of sensible
        heat to latent heat.

    Returns
    -------
    float
        Lambda correction factor (dimensionless, 0 < lambda <= 1.0).

    Raises
    ------
    ValueError
        If mu or alpha is negative.
    """
    if mu < 0:
        raise ValueError(f"mu must be non-negative, got {mu}")
    if alpha < 0:
        raise ValueError(f"alpha must be non-negative, got {alpha}")

    if mu == 0:
        return 1.0

    return 1.0 / math.sqrt(1.0 + mu * (1.0 + 0.5 * alpha * mu))


def soil_latent_heat_J_per_m3(dry_density_kg_per_m3: float,
                              moisture_content_pct: float) -> float:
    """Volumetric latent heat of soil from dry density and moisture content.

    L = rho_d * (w / 100) * L_water

    where L_water = 334,000 J/kg (latent heat of fusion of water).

    Parameters
    ----------
    dry_density_kg_per_m3 : float
        Dry density of soil (kg/m^3). Must be positive.
        Typical range: 1200-2000 kg/m^3.
    moisture_content_pct : float
        Gravimetric moisture content (%). Must be non-negative.
        Typical range: 5-40%.

    Returns
    -------
    float
        Volumetric latent heat (J/m^3).

    Raises
    ------
    ValueError
        If dry_density is not positive or moisture_content is negative.
    """
    if dry_density_kg_per_m3 <= 0:
        raise ValueError(
            f"dry_density must be positive, got {dry_density_kg_per_m3}"
        )
    if moisture_content_pct < 0:
        raise ValueError(
            f"moisture_content must be non-negative, got {moisture_content_pct}"
        )

    L_WATER = 334000.0  # J/kg
    return dry_density_kg_per_m3 * (moisture_content_pct / 100.0) * L_WATER


# ============================================================================
# Typical soil properties for simplified estimation
# ============================================================================

_TYPICAL_SOILS = {
    "gravel": {
        "description": "Clean gravel",
        "dry_density_kg_m3": 1900,
        "moisture_pct": 8,
        "k_frozen_W_mK": 2.2,
        "k_unfrozen_W_mK": 1.8,
    },
    "sand": {
        "description": "Medium sand",
        "dry_density_kg_m3": 1700,
        "moisture_pct": 12,
        "k_frozen_W_mK": 2.0,
        "k_unfrozen_W_mK": 1.5,
    },
    "silt": {
        "description": "Silt (low plasticity)",
        "dry_density_kg_m3": 1500,
        "moisture_pct": 20,
        "k_frozen_W_mK": 1.8,
        "k_unfrozen_W_mK": 1.2,
    },
    "clay": {
        "description": "Clay (medium plasticity)",
        "dry_density_kg_m3": 1400,
        "moisture_pct": 25,
        "k_frozen_W_mK": 1.6,
        "k_unfrozen_W_mK": 1.0,
    },
    "peat": {
        "description": "Peat / organic soil",
        "dry_density_kg_m3": 500,
        "moisture_pct": 80,
        "k_frozen_W_mK": 1.0,
        "k_unfrozen_W_mK": 0.5,
    },
}


def frost_depth_simplified_m(freezing_index_degC_days: float,
                             soil_type: str) -> dict:
    """Simplified frost depth estimate using typical soil properties.

    Convenience function that combines the Stefan equation with
    representative thermal properties for common soil types. Useful
    for preliminary estimates when site-specific data is unavailable.

    Parameters
    ----------
    freezing_index_degC_days : float
        Air freezing index (degree-C days). Must be positive.
    soil_type : str
        Soil type: 'gravel', 'sand', 'silt', 'clay', or 'peat'.

    Returns
    -------
    dict
        Keys: frost_depth_m, soil_type, description,
        dry_density_kg_m3, moisture_pct, k_frozen_W_mK,
        latent_heat_J_m3.

    Raises
    ------
    ValueError
        If freezing_index is not positive or soil_type is unknown.
    """
    if freezing_index_degC_days <= 0:
        raise ValueError(
            f"freezing_index must be positive, got {freezing_index_degC_days}"
        )

    key = soil_type.lower().strip().replace(" ", "_")

    props = None
    if key in _TYPICAL_SOILS:
        props = _TYPICAL_SOILS[key]
    else:
        # Partial match
        for k, v in _TYPICAL_SOILS.items():
            if key in k or k in key:
                props = v
                key = k
                break

    if props is None:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. "
            f"Options: {', '.join(_TYPICAL_SOILS.keys())}"
        )

    L = soil_latent_heat_J_per_m3(
        props["dry_density_kg_m3"], props["moisture_pct"]
    )
    depth = stefan_frost_depth_m(
        freezing_index_degC_days, props["k_frozen_W_mK"], L
    )

    return {
        "frost_depth_m": round(depth, 3),
        "soil_type": key,
        "description": props["description"],
        "dry_density_kg_m3": props["dry_density_kg_m3"],
        "moisture_pct": props["moisture_pct"],
        "k_frozen_W_mK": props["k_frozen_W_mK"],
        "latent_heat_J_m3": round(L, 0),
    }
