"""GEC-11 figure lookup functions.

FHWA-NHI-10-024 — Mechanically Stabilized Earth Walls and Reinforced
Soil Slopes, Volume I, November 2009.

Functions
---------
figure_4_10_kr_ka_ratio   Figure 4-10  Kr/Ka ratio vs depth by reinforcement type
"""

from .._interpolation import _linterp


# ============================================================================
# Figure 4-10: Kr/Ka vs Depth for Internal Stability
# ============================================================================
#
# Three reinforcement types:
#   Geosynthetics: Kr/Ka = 1.0 constant
#   Metal strips:  Kr/Ka = 1.7 at z=0, linearly to 1.2 at z=6m (20ft), 1.2 below
#   Metal bar mats & welded wire: Kr/Ka = 2.5 at z=0, linearly to 1.2 at z=6m, 1.2 below

_FIG_4_10_TYPES = {
    "geosynthetic": {
        "description": "Geosynthetic reinforcement (geogrids, geotextiles)",
        "depths_m": [0.0, 20.0],
        "kr_ka": [1.0, 1.0],
    },
    "metal_strip": {
        "description": "Metallic strip reinforcement (ribbed/smooth steel strips)",
        "depths_m": [0.0, 6.0, 20.0],
        "kr_ka": [1.7, 1.2, 1.2],
    },
    "metal_bar_mat": {
        "description": "Metal bar mats and welded wire grids",
        "depths_m": [0.0, 6.0, 20.0],
        "kr_ka": [2.5, 1.2, 1.2],
    },
}

_TYPE_ALIASES = {
    "geosynthetic": "geosynthetic",
    "geogrid": "geosynthetic",
    "geotextile": "geosynthetic",
    "strip": "metal_strip",
    "metal_strip": "metal_strip",
    "metallic_strip": "metal_strip",
    "bar_mat": "metal_bar_mat",
    "metal_bar_mat": "metal_bar_mat",
    "welded_wire": "metal_bar_mat",
    "wire_grid": "metal_bar_mat",
}


def figure_4_10_kr_ka_ratio(
    depth_m: float,
    reinforcement_type: str = "geosynthetic",
) -> dict:
    """Interpolate Kr/Ka ratio vs depth from GEC-11 Figure 4-10.

    Used for internal stability analysis of MSE walls. The Kr/Ka ratio
    relates the lateral earth pressure coefficient at the reinforcement
    level to the active earth pressure coefficient.

    Parameters
    ----------
    depth_m : float
        Depth below top of wall in meters (must be >= 0).
    reinforcement_type : str
        One of 'geosynthetic', 'metal_strip', 'metal_bar_mat' (or
        aliases: 'geogrid', 'geotextile', 'strip', 'bar_mat',
        'welded_wire', 'wire_grid').

    Returns
    -------
    dict
        Kr/Ka ratio at the specified depth, with reinforcement details.

    Raises
    ------
    ValueError
        If depth is negative or reinforcement type is unknown.
    """
    if depth_m < 0:
        raise ValueError("depth_m must be >= 0")

    key = reinforcement_type.lower().strip()
    resolved = _TYPE_ALIASES.get(key)
    if resolved is None:
        valid = sorted(set(_TYPE_ALIASES.keys()))
        raise ValueError(
            f"Unknown reinforcement_type '{reinforcement_type}'. "
            f"Valid options: {valid}"
        )

    data = _FIG_4_10_TYPES[resolved]
    depths = data["depths_m"]
    values = data["kr_ka"]

    if depth_m <= depths[0]:
        kr_ka = values[0]
    elif depth_m >= depths[-1]:
        kr_ka = values[-1]
    else:
        kr_ka = _linterp(depth_m, depths, values)

    return {
        "depth_m": depth_m,
        "kr_ka_ratio": round(kr_ka, 3),
        "reinforcement_type": resolved,
        "description": data["description"],
        "reference": "FHWA-NHI-10-024, Figure 4-10",
    }
