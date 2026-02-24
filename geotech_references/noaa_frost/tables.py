"""NOAA frost depth table lookup functions.

Soil thermal property tables from published sources for frost penetration
analysis. Follows the DM7 pattern: private data with ``_TABLE_*`` prefix,
public lookup functions.

References:
    Kersten (1949) thermal conductivity correlations
    Farouki (1981) thermal properties of soils
    ASCE 32-01 Table 4
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Soil Thermal Conductivity (W/m-K)
# From Kersten (1949) and Farouki (1981) correlations.
# Values at discrete moisture contents for interpolation.
# ============================================================================

_TABLE_THERMAL_CONDUCTIVITY = {
    # soil_type: {frozen: {moisture_pct: [breakpoints], k: [values]},
    #             unfrozen: {moisture_pct: [...], k: [...]}}
    "gravel": {
        "description": "Clean gravel / gravelly sand",
        "frozen": {
            "moisture_pct": [5, 10, 15, 20, 30],
            "k_W_mK": [1.8, 2.2, 2.4, 2.5, 2.6],
        },
        "unfrozen": {
            "moisture_pct": [5, 10, 15, 20, 30],
            "k_W_mK": [1.2, 1.8, 2.0, 2.1, 2.2],
        },
    },
    "sand": {
        "description": "Medium to coarse sand",
        "frozen": {
            "moisture_pct": [5, 10, 15, 20, 30],
            "k_W_mK": [1.5, 2.0, 2.2, 2.4, 2.5],
        },
        "unfrozen": {
            "moisture_pct": [5, 10, 15, 20, 30],
            "k_W_mK": [1.0, 1.5, 1.8, 2.0, 2.1],
        },
    },
    "silt": {
        "description": "Silt / silty soil",
        "frozen": {
            "moisture_pct": [5, 10, 15, 20, 30, 40],
            "k_W_mK": [1.2, 1.5, 1.8, 2.0, 2.1, 2.2],
        },
        "unfrozen": {
            "moisture_pct": [5, 10, 15, 20, 30, 40],
            "k_W_mK": [0.7, 1.0, 1.2, 1.4, 1.6, 1.7],
        },
    },
    "clay": {
        "description": "Clay (medium to high plasticity)",
        "frozen": {
            "moisture_pct": [5, 10, 15, 20, 30, 40, 50],
            "k_W_mK": [1.0, 1.3, 1.5, 1.7, 1.9, 2.0, 2.1],
        },
        "unfrozen": {
            "moisture_pct": [5, 10, 15, 20, 30, 40, 50],
            "k_W_mK": [0.6, 0.8, 1.0, 1.1, 1.3, 1.4, 1.5],
        },
    },
    "peat": {
        "description": "Peat / organic soil",
        "frozen": {
            "moisture_pct": [20, 40, 60, 80, 100],
            "k_W_mK": [0.5, 0.7, 0.9, 1.0, 1.1],
        },
        "unfrozen": {
            "moisture_pct": [20, 40, 60, 80, 100],
            "k_W_mK": [0.3, 0.4, 0.5, 0.5, 0.6],
        },
    },
}


def table_soil_thermal_conductivity(soil_type: str,
                                    moisture_pct: float,
                                    frozen: bool = True) -> float:
    """Soil thermal conductivity from soil type and moisture content.

    Interpolates from Kersten (1949) and Farouki (1981) data.
    Clamped at table endpoints for out-of-range moisture values.

    Parameters
    ----------
    soil_type : str
        Soil type: 'gravel', 'sand', 'silt', 'clay', or 'peat'.
    moisture_pct : float
        Gravimetric moisture content (%). Must be non-negative.
    frozen : bool
        True for frozen conductivity (default), False for unfrozen.

    Returns
    -------
    float
        Thermal conductivity (W/m-K).

    Raises
    ------
    ValueError
        If soil_type is unknown or moisture is negative.
    """
    if moisture_pct < 0:
        raise ValueError(
            f"moisture_pct must be non-negative, got {moisture_pct}"
        )

    key = soil_type.lower().strip().replace(" ", "_")

    entry = None
    if key in _TABLE_THERMAL_CONDUCTIVITY:
        entry = _TABLE_THERMAL_CONDUCTIVITY[key]
    else:
        for k, v in _TABLE_THERMAL_CONDUCTIVITY.items():
            if key in k or k in key:
                entry = v
                break

    if entry is None:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. "
            f"Options: {', '.join(_TABLE_THERMAL_CONDUCTIVITY.keys())}"
        )

    state = "frozen" if frozen else "unfrozen"
    data = entry[state]
    return _linterp(moisture_pct, data["moisture_pct"], data["k_W_mK"])


# ============================================================================
# Surface n-factor: Air Freezing Index → Surface Freezing Index
# n_surface = n * FI_air
# From ASCE 32-01 and Departments of the Army/Air Force TM 5-852-6
# ============================================================================

_TABLE_N_FACTOR = {
    "snow_covered": {
        "description": "Snow-covered surface (undisturbed)",
        "n_factor": 0.20,
    },
    "turf": {
        "description": "Turf / grass-covered ground",
        "n_factor": 0.40,
    },
    "gravel_surface": {
        "description": "Gravel or crushed stone surface",
        "n_factor": 0.60,
    },
    "bare_soil": {
        "description": "Bare soil (no vegetation or cover)",
        "n_factor": 0.70,
    },
    "asphalt": {
        "description": "Asphalt pavement",
        "n_factor": 0.75,
    },
    "concrete": {
        "description": "Concrete pavement or slab",
        "n_factor": 0.80,
    },
    "sand_gravel_dry": {
        "description": "Dry sand or gravel (no snow)",
        "n_factor": 0.90,
    },
    "exposed_rock": {
        "description": "Exposed rock surface",
        "n_factor": 1.00,
    },
}


def table_n_factor(surface_type: str) -> float:
    """Surface n-factor for air-to-surface freezing index conversion.

    The surface freezing index is the product of the air freezing index
    and the n-factor: FI_surface = n * FI_air.

    Snow cover insulates the ground (low n), while bare or paved surfaces
    transmit more cold (high n).

    Parameters
    ----------
    surface_type : str
        Surface type: 'snow_covered', 'turf', 'gravel_surface',
        'bare_soil', 'asphalt', 'concrete', 'sand_gravel_dry',
        'exposed_rock'.

    Returns
    -------
    float
        n-factor (dimensionless, 0 to 1.0).

    Raises
    ------
    ValueError
        If surface_type is not recognized.
    """
    key = surface_type.lower().strip().replace(" ", "_")

    if key in _TABLE_N_FACTOR:
        return _TABLE_N_FACTOR[key]["n_factor"]

    # Partial match
    for k, v in _TABLE_N_FACTOR.items():
        if key in k or k in key:
            return v["n_factor"]

    raise ValueError(
        f"Unknown surface_type '{surface_type}'. "
        f"Options: {', '.join(_TABLE_N_FACTOR.keys())}"
    )


# ============================================================================
# Volumetric Heat Capacity (J/m^3-K)
# From Farouki (1981) and Andersland & Ladanyi (2004)
# C = rho_d * (c_s + w/100 * c_w)  where c_s ~ 840 J/kg-K, c_w varies
# Tabulated values at discrete moisture contents.
# ============================================================================

_TABLE_HEAT_CAPACITY = {
    "gravel": {
        "description": "Clean gravel / gravelly sand",
        "frozen": {
            "moisture_pct": [5, 10, 15, 20, 30],
            "C_MJ_m3K": [1.5, 1.7, 1.9, 2.0, 2.2],
        },
        "unfrozen": {
            "moisture_pct": [5, 10, 15, 20, 30],
            "C_MJ_m3K": [1.8, 2.1, 2.3, 2.5, 2.8],
        },
    },
    "sand": {
        "description": "Medium to coarse sand",
        "frozen": {
            "moisture_pct": [5, 10, 15, 20, 30],
            "C_MJ_m3K": [1.4, 1.6, 1.7, 1.9, 2.1],
        },
        "unfrozen": {
            "moisture_pct": [5, 10, 15, 20, 30],
            "C_MJ_m3K": [1.6, 1.9, 2.1, 2.3, 2.6],
        },
    },
    "silt": {
        "description": "Silt / silty soil",
        "frozen": {
            "moisture_pct": [5, 10, 15, 20, 30, 40],
            "C_MJ_m3K": [1.3, 1.4, 1.6, 1.7, 1.9, 2.0],
        },
        "unfrozen": {
            "moisture_pct": [5, 10, 15, 20, 30, 40],
            "C_MJ_m3K": [1.5, 1.7, 1.9, 2.1, 2.4, 2.6],
        },
    },
    "clay": {
        "description": "Clay (medium to high plasticity)",
        "frozen": {
            "moisture_pct": [5, 10, 15, 20, 30, 40, 50],
            "C_MJ_m3K": [1.2, 1.3, 1.4, 1.6, 1.7, 1.9, 2.0],
        },
        "unfrozen": {
            "moisture_pct": [5, 10, 15, 20, 30, 40, 50],
            "C_MJ_m3K": [1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6],
        },
    },
    "peat": {
        "description": "Peat / organic soil",
        "frozen": {
            "moisture_pct": [20, 40, 60, 80, 100],
            "C_MJ_m3K": [0.8, 1.0, 1.2, 1.4, 1.5],
        },
        "unfrozen": {
            "moisture_pct": [20, 40, 60, 80, 100],
            "C_MJ_m3K": [1.5, 2.0, 2.5, 3.0, 3.5],
        },
    },
}


def table_soil_volumetric_heat_capacity(soil_type: str,
                                        moisture_pct: float,
                                        frozen: bool = True) -> float:
    """Volumetric heat capacity from soil type and moisture content.

    Interpolates from Farouki (1981) tabulated data.
    Clamped at table endpoints for out-of-range moisture values.

    Parameters
    ----------
    soil_type : str
        Soil type: 'gravel', 'sand', 'silt', 'clay', or 'peat'.
    moisture_pct : float
        Gravimetric moisture content (%). Must be non-negative.
    frozen : bool
        True for frozen heat capacity (default), False for unfrozen.

    Returns
    -------
    float
        Volumetric heat capacity (MJ/m^3-K).

    Raises
    ------
    ValueError
        If soil_type is unknown or moisture is negative.
    """
    if moisture_pct < 0:
        raise ValueError(
            f"moisture_pct must be non-negative, got {moisture_pct}"
        )

    key = soil_type.lower().strip().replace(" ", "_")

    entry = None
    if key in _TABLE_HEAT_CAPACITY:
        entry = _TABLE_HEAT_CAPACITY[key]
    else:
        for k, v in _TABLE_HEAT_CAPACITY.items():
            if key in k or k in key:
                entry = v
                break

    if entry is None:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. "
            f"Options: {', '.join(_TABLE_HEAT_CAPACITY.keys())}"
        )

    state = "frozen" if frozen else "unfrozen"
    data = entry[state]
    return _linterp(moisture_pct, data["moisture_pct"], data["C_MJ_m3K"])


# ============================================================================
# Combined thermal properties lookup
# ============================================================================

def soil_thermal_properties(soil_type: str,
                            moisture_pct: float) -> dict:
    """All thermal properties for a soil type in one call.

    Returns frozen and unfrozen thermal conductivity and volumetric
    heat capacity, plus a convenience average conductivity for the
    modified Berggren method.

    Parameters
    ----------
    soil_type : str
        Soil type: 'gravel', 'sand', 'silt', 'clay', or 'peat'.
    moisture_pct : float
        Gravimetric moisture content (%). Must be non-negative.

    Returns
    -------
    dict
        Keys: soil_type, moisture_pct,
        k_frozen_W_mK, k_unfrozen_W_mK, k_avg_W_mK,
        C_frozen_MJ_m3K, C_unfrozen_MJ_m3K.

    Raises
    ------
    ValueError
        If soil_type is unknown or moisture is negative.
    """
    k_f = table_soil_thermal_conductivity(soil_type, moisture_pct, frozen=True)
    k_u = table_soil_thermal_conductivity(soil_type, moisture_pct, frozen=False)
    c_f = table_soil_volumetric_heat_capacity(
        soil_type, moisture_pct, frozen=True
    )
    c_u = table_soil_volumetric_heat_capacity(
        soil_type, moisture_pct, frozen=False
    )

    return {
        "soil_type": soil_type.lower().strip(),
        "moisture_pct": moisture_pct,
        "k_frozen_W_mK": round(k_f, 3),
        "k_unfrozen_W_mK": round(k_u, 3),
        "k_avg_W_mK": round((k_f + k_u) / 2.0, 3),
        "C_frozen_MJ_m3K": round(c_f, 3),
        "C_unfrozen_MJ_m3K": round(c_u, 3),
    }
