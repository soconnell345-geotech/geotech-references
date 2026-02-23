"""GEC-6 table lookup functions.

Digitized tables from FHWA-SA-02-054 (GEC-6), Shallow Foundations.
Follows the DM7 pattern: private data with ``_TABLE_*`` prefix, public
lookup functions, case-insensitive keys.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 4-1: Soil Properties Correlated with SPT Values
# ============================================================================

_TABLE_4_1_SANDS = [
    {"n_min": 0, "n_max": 4, "relative_density": "very_loose"},
    {"n_min": 4, "n_max": 10, "relative_density": "loose"},
    {"n_min": 10, "n_max": 30, "relative_density": "medium"},
    {"n_min": 30, "n_max": 50, "relative_density": "dense"},
    {"n_min": 50, "n_max": 9999, "relative_density": "very_dense"},
]

_TABLE_4_1_CLAYS = [
    {"n_min": 0, "n_max": 2, "consistency": "very_soft"},
    {"n_min": 2, "n_max": 4, "consistency": "soft"},
    {"n_min": 4, "n_max": 8, "consistency": "medium"},
    {"n_min": 8, "n_max": 15, "consistency": "stiff"},
    {"n_min": 15, "n_max": 30, "consistency": "very_stiff"},
    {"n_min": 30, "n_max": 9999, "consistency": "hard"},
]


def table_4_1_spt_soil_properties(n_value: int, soil_type: str = "sand") -> dict:
    """Soil properties correlated with SPT N-values (Table 4-1).

    Parameters
    ----------
    n_value : int
        Standard Penetration Test blow count (blows per 0.3 m).
    soil_type : str
        'sand' or 'clay'.

    Returns
    -------
    dict
        For sands: {'relative_density': str}
        For clays: {'consistency': str}

    Raises
    ------
    ValueError
        If soil_type is not recognized or n_value is negative.
    """
    if n_value < 0:
        raise ValueError(f"N-value must be non-negative, got {n_value}")

    st = soil_type.lower().strip()
    if st in ("sand", "sands", "cohesionless", "granular"):
        for row in _TABLE_4_1_SANDS:
            if row["n_min"] <= n_value < row["n_max"]:
                return {"relative_density": row["relative_density"]}
        return {"relative_density": "very_dense"}
    elif st in ("clay", "clays", "cohesive", "fine_grained"):
        for row in _TABLE_4_1_CLAYS:
            if row["n_min"] <= n_value < row["n_max"]:
                return {"consistency": row["consistency"]}
        return {"consistency": "hard"}
    else:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. Use 'sand' or 'clay'."
        )


# ============================================================================
# Table 5-1: Bearing Capacity Factors (AASHTO, 1996)
# Nc, Nq, Ngamma as functions of friction angle phi (degrees)
# ============================================================================

_TABLE_5_1_PHI = list(range(0, 46))

_TABLE_5_1_NC = [
    5.14, 5.4, 5.6, 5.9, 6.2, 6.5, 6.8, 7.2, 7.5, 7.9,
    8.4, 8.8, 9.3, 9.8, 10.4, 11.0, 11.6, 12.3, 13.1, 13.9,
    14.8, 15.8, 16.9, 18.1, 19.3, 20.7, 22.3, 23.9, 25.8, 27.9,
    30.1, 32.7, 35.5, 38.6, 42.2, 46.1, 50.6, 55.6, 61.4, 67.9,
    75.3, 83.9, 93.7, 105.1, 118.4, 133.9,
]

_TABLE_5_1_NQ = [
    1.0, 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.9, 2.1, 2.3,
    2.5, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.8, 5.3, 5.8,
    6.4, 7.1, 7.8, 8.7, 9.6, 10.7, 11.9, 13.2, 14.7, 16.4,
    18.4, 20.6, 23.2, 26.1, 29.4, 33.3, 37.8, 42.9, 48.9, 56.0,
    64.2, 73.9, 85.4, 99.0, 115.3, 134.9,
]

_TABLE_5_1_NGAMMA = [
    0.0, 0.1, 0.2, 0.2, 0.3, 0.5, 0.6, 0.7, 0.9, 1.0,
    1.2, 1.4, 1.7, 2.0, 2.3, 2.7, 3.1, 3.5, 4.1, 4.7,
    5.4, 6.2, 7.1, 8.2, 9.4, 10.9, 12.5, 14.5, 16.7, 19.3,
    22.4, 26.0, 30.2, 35.2, 41.1, 48.0, 56.3, 66.2, 78.0, 92.3,
    109.4, 130.2, 155.6, 186.5, 224.6, 271.8,
]


def table_5_1_bearing_capacity_factors(phi: float) -> dict:
    """Bearing capacity factors Nc, Nq, Ngamma (Table 5-1, AASHTO 1996).

    Parameters
    ----------
    phi : float
        Friction angle in degrees, 0 to 45.

    Returns
    -------
    dict
        {'Nc': float, 'Nq': float, 'Ngamma': float}

    Raises
    ------
    ValueError
        If phi is outside 0-45 range.
    """
    if phi < 0 or phi > 45:
        raise ValueError(
            f"Friction angle phi must be 0-45 degrees, got {phi}"
        )
    nc = _linterp(phi, _TABLE_5_1_PHI, _TABLE_5_1_NC)
    nq = _linterp(phi, _TABLE_5_1_PHI, _TABLE_5_1_NQ)
    ng = _linterp(phi, _TABLE_5_1_PHI, _TABLE_5_1_NGAMMA)
    return {"Nc": nc, "Nq": nq, "Ngamma": ng}


# ============================================================================
# Table 5-4: Depth Correction Factor (Brinch Hansen, 1970)
# dq as function of phi and Df/Bf
# ============================================================================

_TABLE_5_4_PHI = [32, 37, 42]
_TABLE_5_4_DFBF = [1, 2, 4, 8]
_TABLE_5_4_DQ = {
    32: [1.20, 1.30, 1.35, 1.40],
    37: [1.20, 1.25, 1.30, 1.35],
    42: [1.15, 1.20, 1.25, 1.30],
}


def table_5_4_depth_correction_factor(phi: float, df_bf: float) -> float:
    """Depth correction factor dq (Table 5-4, Brinch Hansen 1970).

    Should only be used when soils above footing bearing elevation are
    as competent as soils beneath the footing level; otherwise use dq = 1.0.

    Parameters
    ----------
    phi : float
        Friction angle in degrees, 32 to 42.
    df_bf : float
        Ratio of embedment depth to footing width (Df/Bf), 1 to 8.

    Returns
    -------
    float
        Depth correction factor dq.

    Raises
    ------
    ValueError
        If phi or df_bf is outside the table range.
    """
    if phi < 32 or phi > 42:
        raise ValueError(
            f"Friction angle must be 32-42 degrees for Table 5-4, got {phi}"
        )
    if df_bf < 1 or df_bf > 8:
        raise ValueError(
            f"Df/Bf must be 1-8 for Table 5-4, got {df_bf}"
        )

    # Interpolate along Df/Bf for each phi, then interpolate between phis
    dq_values = []
    for p in _TABLE_5_4_PHI:
        dq = _linterp(df_bf, _TABLE_5_4_DFBF, _TABLE_5_4_DQ[p])
        dq_values.append(dq)

    return _linterp(phi, _TABLE_5_4_PHI, dq_values)


# ============================================================================
# Table 5-7: Presumptive Bearing Pressures for Rock (NAVFAC, 1986b)
# ============================================================================

_TABLE_5_7 = [
    {
        "type": "massive_crystalline_igneous_metamorphic",
        "consistency": "hard_sound_rock",
        "range_min_mpa": 5.8,
        "range_max_mpa": 9.6,
        "recommended_mpa": 7.7,
    },
    {
        "type": "foliated_metamorphic",
        "consistency": "medium_hard_sound_rock",
        "range_min_mpa": 2.9,
        "range_max_mpa": 3.8,
        "recommended_mpa": 3.4,
    },
    {
        "type": "sedimentary_hard_cemented",
        "consistency": "medium_hard_sound_rock",
        "range_min_mpa": 1.4,
        "range_max_mpa": 2.4,
        "recommended_mpa": 1.9,
    },
    {
        "type": "weathered_broken_bedrock",
        "consistency": "soft_rock",
        "range_min_mpa": 0.8,
        "range_max_mpa": 1.2,
        "recommended_mpa": 1.0,
    },
    {
        "type": "compaction_shale_argillaceous",
        "consistency": "soft_rock",
        "range_min_mpa": 0.8,
        "range_max_mpa": 1.2,
        "recommended_mpa": 1.0,
    },
]


def table_5_7_presumptive_bearing_rock(rock_type: str) -> dict:
    """Presumptive bearing pressures for rock (Table 5-7, NAVFAC 1986b).

    Parameters
    ----------
    rock_type : str
        Rock type or consistency keyword. Partial matching supported.
        Examples: 'massive', 'crystalline', 'foliated', 'sedimentary',
        'weathered', 'shale', 'soft_rock', 'hard_sound'.

    Returns
    -------
    dict
        {'type': str, 'consistency': str, 'range_min_mpa': float,
         'range_max_mpa': float, 'recommended_mpa': float}

    Raises
    ------
    ValueError
        If no matching rock type is found.
    """
    key = rock_type.lower().strip().replace(" ", "_")
    for row in _TABLE_5_7:
        if key in row["type"] or key in row["consistency"]:
            return dict(row)
    raise ValueError(
        f"No match for rock_type '{rock_type}'. Try: 'massive', "
        "'foliated', 'sedimentary', 'weathered', 'shale'."
    )


# ============================================================================
# Table 5-9: Allowable Bearing by RQD (Peck et al., 1974)
# ============================================================================

_TABLE_5_9_RQD = [0, 25, 50, 75, 90, 100]
_TABLE_5_9_PRESSURE_MPA = [1, 3, 6, 12, 19, 29]
_TABLE_5_9_QUALITY = ["soil_like", "very_poor", "poor", "fair", "good", "excellent"]


def table_5_9_rqd_bearing_capacity(rqd: float) -> dict:
    """Allowable bearing capacity based on RQD (Table 5-9, Peck et al. 1974).

    Parameters
    ----------
    rqd : float
        Rock Quality Designation, 0 to 100 percent.

    Returns
    -------
    dict
        {'rqd': float, 'rock_mass_quality': str,
         'allowable_pressure_mpa': float}

    Raises
    ------
    ValueError
        If RQD is outside 0-100 range.
    """
    if rqd < 0 or rqd > 100:
        raise ValueError(f"RQD must be 0-100%, got {rqd}")

    pressure = _linterp(rqd, _TABLE_5_9_RQD, _TABLE_5_9_PRESSURE_MPA)

    # Determine quality category
    quality = "soil_like"
    for i, threshold in enumerate(_TABLE_5_9_RQD):
        if rqd >= threshold:
            quality = _TABLE_5_9_QUALITY[i]

    return {
        "rqd": rqd,
        "rock_mass_quality": quality,
        "allowable_pressure_mpa": round(pressure, 1),
    }


# ============================================================================
# Table 5-12: Shape and Rigidity Factors Cd
# (Winterkorn & Fang, 1975)
# ============================================================================

_TABLE_5_12_SHAPES = {
    "circle": {"center": 1.00, "corner": 0.64, "mid_short": 0.64, "mid_long": 0.64, "average": 0.85},
    "circle_rigid": {"center": 0.79, "corner": 0.79, "mid_short": 0.79, "mid_long": 0.79, "average": 0.79},
    "square": {"center": 1.12, "corner": 0.56, "mid_short": 0.76, "mid_long": 0.76, "average": 0.95},
    "square_rigid": {"center": 0.99, "corner": 0.99, "mid_short": 0.99, "mid_long": 0.99, "average": 0.99},
}

_TABLE_5_12_RECT_LW = [1.5, 2, 3, 5, 10, 100, 1000, 10000]
_TABLE_5_12_RECT_CENTER = [1.36, 1.52, 1.78, 2.10, 2.53, 4.00, 5.47, 6.90]
_TABLE_5_12_RECT_CORNER = [0.67, 0.76, 0.88, 1.05, 1.26, 2.00, 2.75, 3.50]
_TABLE_5_12_RECT_MID_SHORT = [0.89, 0.98, 1.11, 1.27, 1.49, 2.20, 2.94, 3.70]
_TABLE_5_12_RECT_MID_LONG = [0.97, 1.12, 1.35, 1.68, 2.12, 3.60, 5.03, 6.50]
_TABLE_5_12_RECT_AVERAGE = [1.15, 1.30, 1.52, 1.83, 2.25, 3.70, 5.15, 6.60]


def table_5_12_shape_rigidity_factor(shape: str, location: str = "center",
                                     length_width: float = None) -> float:
    """Shape and rigidity factor Cd for settlement on rock (Table 5-12).

    Parameters
    ----------
    shape : str
        'circle', 'circle_rigid', 'square', 'square_rigid',
        or 'rectangle' (requires length_width).
    location : str
        'center', 'corner', 'mid_short', 'mid_long', or 'average'.
    length_width : float, optional
        Length/width ratio for rectangular footings (1.5 to 10000).

    Returns
    -------
    float
        Shape and rigidity factor Cd.

    Raises
    ------
    ValueError
        If shape, location, or length_width is invalid.
    """
    shape_key = shape.lower().strip().replace(" ", "_")
    loc = location.lower().strip().replace(" ", "_")

    if shape_key in _TABLE_5_12_SHAPES:
        data = _TABLE_5_12_SHAPES[shape_key]
        if loc not in data:
            raise ValueError(
                f"Unknown location '{location}'. Use: center, corner, "
                "mid_short, mid_long, average."
            )
        return data[loc]

    if shape_key in ("rectangle", "rectangular", "rect"):
        if length_width is None:
            raise ValueError("length_width required for rectangular footings")
        if length_width < 1.5 or length_width > 10000:
            raise ValueError(
                f"length_width must be 1.5-10000, got {length_width}"
            )
        lookup = {
            "center": _TABLE_5_12_RECT_CENTER,
            "corner": _TABLE_5_12_RECT_CORNER,
            "mid_short": _TABLE_5_12_RECT_MID_SHORT,
            "mid_long": _TABLE_5_12_RECT_MID_LONG,
            "average": _TABLE_5_12_RECT_AVERAGE,
        }
        if loc not in lookup:
            raise ValueError(
                f"Unknown location '{location}'. Use: center, corner, "
                "mid_short, mid_long, average."
            )
        return _linterp(length_width, _TABLE_5_12_RECT_LW, lookup[loc])

    raise ValueError(
        f"Unknown shape '{shape}'. Use: circle, circle_rigid, square, "
        "square_rigid, or rectangle."
    )


# ============================================================================
# Table 5-13: Poisson's Ratio for Intact Rock
# (AASHTO, modified after Kulhawy, 1978)
# ============================================================================

_TABLE_5_13 = {
    "granite": {"max": 0.39, "min": 0.09, "mean": 0.20, "std": 0.08},
    "gabbro": {"max": 0.20, "min": 0.16, "mean": 0.18, "std": 0.02},
    "diabase": {"max": 0.38, "min": 0.20, "mean": 0.29, "std": 0.06},
    "basalt": {"max": 0.32, "min": 0.16, "mean": 0.23, "std": 0.05},
    "quartzite": {"max": 0.22, "min": 0.08, "mean": 0.14, "std": 0.05},
    "marble": {"max": 0.40, "min": 0.17, "mean": 0.28, "std": 0.08},
    "gneiss": {"max": 0.40, "min": 0.09, "mean": 0.22, "std": 0.09},
    "schist": {"max": 0.31, "min": 0.02, "mean": 0.12, "std": 0.08},
    "sandstone": {"max": 0.46, "min": 0.08, "mean": 0.20, "std": 0.11},
    "siltstone": {"max": 0.23, "min": 0.09, "mean": 0.18, "std": 0.06},
    "shale": {"max": 0.18, "min": 0.03, "mean": 0.09, "std": 0.06},
    "limestone": {"max": 0.33, "min": 0.12, "mean": 0.23, "std": 0.06},
    "dolostone": {"max": 0.35, "min": 0.14, "mean": 0.29, "std": 0.08},
}


def table_5_13_poissons_ratio_rock(rock_type: str) -> dict:
    """Poisson's ratio for intact rock (Table 5-13, Kulhawy 1978).

    Parameters
    ----------
    rock_type : str
        Rock type (e.g., 'granite', 'sandstone', 'limestone').

    Returns
    -------
    dict
        {'rock_type': str, 'max': float, 'min': float,
         'mean': float, 'std': float}

    Raises
    ------
    ValueError
        If rock type is not found.
    """
    key = rock_type.lower().strip()
    if key in _TABLE_5_13:
        result = dict(_TABLE_5_13[key])
        result["rock_type"] = key
        return result

    # Try partial match
    for k, v in _TABLE_5_13.items():
        if key in k or k in key:
            result = dict(v)
            result["rock_type"] = k
            return result

    raise ValueError(
        f"Unknown rock_type '{rock_type}'. Options: "
        f"{', '.join(_TABLE_5_13.keys())}"
    )


# ============================================================================
# Table 5-14: Young's Modulus for Intact Rock (kPa x 10^6)
# (Modified after Kulhawy, 1978)
# ============================================================================

_TABLE_5_14 = {
    "granite": {"max": 99.97, "min": 6.41, "mean": 52.67, "std": 24.48},
    "diorite": {"max": 111.69, "min": 17.10, "mean": 51.36, "std": 42.68},
    "gabbro": {"max": 84.11, "min": 67.57, "mean": 75.84, "std": 6.69},
    "diabase": {"max": 104.11, "min": 68.95, "mean": 88.25, "std": 12.27},
    "basalt": {"max": 84.11, "min": 28.96, "mean": 56.12, "std": 17.93},
    "quartzite": {"max": 88.25, "min": 36.47, "mean": 66.12, "std": 16.00},
    "marble": {"max": 73.77, "min": 4.00, "mean": 42.61, "std": 17.17},
    "gneiss": {"max": 82.05, "min": 28.47, "mean": 61.09, "std": 15.93},
    "slate": {"max": 26.13, "min": 2.41, "mean": 9.58, "std": 6.62},
    "schist": {"max": 68.95, "min": 5.93, "mean": 34.27, "std": 21.92},
    "phyllite": {"max": 17.31, "min": 8.62, "mean": 11.79, "std": 3.93},
    "sandstone": {"max": 39.16, "min": 0.62, "mean": 14.69, "std": 8.20},
    "siltstone": {"max": 32.82, "min": 2.62, "mean": 16.48, "std": 11.38},
    "shale": {"max": 38.61, "min": 0.01, "mean": 9.79, "std": 10.00},
    "limestone": {"max": 89.63, "min": 4.48, "mean": 39.30, "std": 25.72},
    "dolostone": {"max": 78.60, "min": 5.72, "mean": 29.10, "std": 23.72},
}


def table_5_14_youngs_modulus_rock(rock_type: str) -> dict:
    """Young's modulus for intact rock in kPa x 10^6 (Table 5-14, Kulhawy 1978).

    Parameters
    ----------
    rock_type : str
        Rock type (e.g., 'granite', 'sandstone', 'limestone').

    Returns
    -------
    dict
        {'rock_type': str, 'max_GPa': float, 'min_GPa': float,
         'mean_GPa': float, 'std_GPa': float}
        Values in GPa (= kPa x 10^6).

    Raises
    ------
    ValueError
        If rock type is not found.
    """
    key = rock_type.lower().strip()
    match = None

    if key in _TABLE_5_14:
        match = key
    else:
        for k in _TABLE_5_14:
            if key in k or k in key:
                match = k
                break

    if match is None:
        raise ValueError(
            f"Unknown rock_type '{rock_type}'. Options: "
            f"{', '.join(_TABLE_5_14.keys())}"
        )

    v = _TABLE_5_14[match]
    return {
        "rock_type": match,
        "max_GPa": v["max"],
        "min_GPa": v["min"],
        "mean_GPa": v["mean"],
        "std_GPa": v["std"],
    }


# ============================================================================
# Table 5-15: Ultimate Friction Factors for Dissimilar Materials
# (NAVFAC, 1986b)
# ============================================================================

_TABLE_5_15 = [
    {
        "interface": "clean_sound_rock",
        "tan_delta_min": 0.70,
        "tan_delta_max": 0.70,
        "delta_min_deg": 35,
        "delta_max_deg": 35,
    },
    {
        "interface": "clean_gravel_coarse_sand",
        "tan_delta_min": 0.55,
        "tan_delta_max": 0.60,
        "delta_min_deg": 29,
        "delta_max_deg": 31,
    },
    {
        "interface": "clean_fine_to_medium_sand_silty_medium_to_coarse_sand",
        "tan_delta_min": 0.45,
        "tan_delta_max": 0.55,
        "delta_min_deg": 24,
        "delta_max_deg": 29,
    },
    {
        "interface": "clean_fine_sand_silty_or_clayey_fine_to_medium_sand",
        "tan_delta_min": 0.35,
        "tan_delta_max": 0.45,
        "delta_min_deg": 19,
        "delta_max_deg": 24,
    },
    {
        "interface": "fine_sandy_silt_nonplastic_silt",
        "tan_delta_min": 0.30,
        "tan_delta_max": 0.35,
        "delta_min_deg": 17,
        "delta_max_deg": 19,
    },
    {
        "interface": "medium_stiff_clay_silty_clay",
        "tan_delta_min": 0.30,
        "tan_delta_max": 0.35,
        "delta_min_deg": 17,
        "delta_max_deg": 19,
    },
    {
        "interface": "very_stiff_hard_residual_preconsolidated_clay",
        "tan_delta_min": 0.40,
        "tan_delta_max": 0.50,
        "delta_min_deg": 22,
        "delta_max_deg": 26,
    },
]


def table_5_15_friction_factor(interface: str) -> dict:
    """Friction factors for concrete on soil/rock (Table 5-15, NAVFAC 1986b).

    Parameters
    ----------
    interface : str
        Interface material description. Partial matching supported.
        Examples: 'rock', 'gravel', 'sand', 'silt', 'clay', 'stiff'.

    Returns
    -------
    dict
        {'interface': str, 'tan_delta_min': float, 'tan_delta_max': float,
         'delta_min_deg': int, 'delta_max_deg': int}

    Raises
    ------
    ValueError
        If no matching interface is found.
    """
    key = interface.lower().strip().replace(" ", "_")

    # Exact match first
    for row in _TABLE_5_15:
        if key == row["interface"]:
            return dict(row)

    # Try matching where the key is a primary word (appears as a
    # standalone segment between underscores), not merely a substring
    # of a compound name. E.g., 'silt' should match
    # 'fine_sandy_silt_nonplastic_silt' not 'silty_medium_to_coarse_sand'.
    key_words = key.replace("_", " ").split()
    for row in _TABLE_5_15:
        iface_words = row["interface"].replace("_", " ").split()
        if all(w in iface_words for w in key_words):
            return dict(row)

    # Fallback: substring match
    for row in _TABLE_5_15:
        if key in row["interface"] or row["interface"] in key:
            return dict(row)

    raise ValueError(
        f"No match for interface '{interface}'. Try: 'rock', "
        "'gravel', 'sand', 'silt', 'clay', 'stiff'."
    )


# ============================================================================
# Table 5-10: Presumptive Bearing Capacity on Compacted Structural Fills
# ============================================================================

_TABLE_5_10 = [
    {
        "agency": "washington_state_dot",
        "bearing_capacity_kpa": 290,
        "max_settlement_mm": 40,
        "fill_material": "gravel_borrow",
    },
    {
        "agency": "nevada_dot",
        "bearing_capacity_kpa": 190,
        "max_settlement_mm": 32,
        "fill_material": "type_1a_aggregate_base",
    },
    {
        "agency": "michigan_dot",
        "bearing_capacity_kpa": 170,
        "max_settlement_mm": None,
        "fill_material": "granular_material_class_iii",
    },
]


def table_5_10_fill_bearing_capacity(agency: str = "") -> list:
    """Presumptive bearing capacity on compacted fills (Table 5-10).

    Parameters
    ----------
    agency : str, optional
        Filter by agency name (partial match). Empty returns all.

    Returns
    -------
    list of dict
        Matching agency entries with bearing_capacity_kpa, max_settlement_mm,
        and fill_material.
    """
    if not agency:
        return [dict(r) for r in _TABLE_5_10]

    key = agency.lower().strip().replace(" ", "_")
    results = [dict(r) for r in _TABLE_5_10 if key in r["agency"]]
    if not results:
        raise ValueError(
            f"No match for agency '{agency}'. Options: "
            f"{', '.join(r['agency'] for r in _TABLE_5_10)}"
        )
    return results
