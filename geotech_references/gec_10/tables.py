"""GEC-10 table lookup functions.

Digitized tables from FHWA-NHI-10-016 (GEC-10), Drilled Shafts:
Construction Procedures and LRFD Design Methods.  Follows the DM7
pattern: private data with ``_TABLE_*`` prefix, public lookup
functions, case-insensitive keys.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 10-5: Resistance Factors for LRFD Design of Drilled Shafts
# (after AASHTO 2007, Brown et al. 2010)
#
# Comprehensive table of phi factors for strength limit state and
# extreme event limit states.
# ============================================================================

_TABLE_10_5 = {
    # --- Lateral geotechnical resistance ---
    "lateral_pushover_individual": {
        "phi": 0.67,
        "condition": "Single shaft, static lateral analysis (p-y method)",
        "category": "lateral",
    },
    "lateral_pushover_group": {
        "phi": 0.80,
        "condition": "Group lateral analysis with p-multipliers",
        "category": "lateral",
    },
    # --- Compression: Side resistance ---
    "side_sand_beta_static_calculated": {
        "phi": 0.55,
        "condition": "Beta method, sand/gravel, no load test",
        "category": "compression_side",
    },
    "side_sand_beta_static_with_load_test": {
        "phi": 0.45,
        "condition": "Beta method, sand/gravel, with static load test",
        "category": "compression_side",
    },
    "side_clay_alpha_static_calculated": {
        "phi": 0.45,
        "condition": "Alpha method, clay, no load test",
        "category": "compression_side",
    },
    "side_clay_alpha_static_with_load_test": {
        "phi": 0.35,
        "condition": "Alpha method, clay, with static load test",
        "category": "compression_side",
    },
    "side_rock_calculated": {
        "phi": 0.55,
        "condition": "Rock side resistance, Horvath & Kenney or O'Neill & Reese",
        "category": "compression_side",
    },
    "side_rock_with_load_test": {
        "phi": 0.45,
        "condition": "Rock side resistance, with load test",
        "category": "compression_side",
    },
    "side_igm_calculated": {
        "phi": 0.60,
        "condition": "IGM side resistance (intermediate geomaterial)",
        "category": "compression_side",
    },
    "side_igm_with_load_test": {
        "phi": 0.50,
        "condition": "IGM side resistance, with load test",
        "category": "compression_side",
    },
    # --- Compression: Base (tip) resistance ---
    "base_sand_calculated": {
        "phi": 0.50,
        "condition": "Sand/gravel base resistance",
        "category": "compression_base",
    },
    "base_clay_calculated": {
        "phi": 0.40,
        "condition": "Clay base resistance, Nc method",
        "category": "compression_base",
    },
    "base_rock_calculated": {
        "phi": 0.50,
        "condition": "Rock base resistance, Carter & Kulhawy or Goodman",
        "category": "compression_base",
    },
    "base_igm_calculated": {
        "phi": 0.50,
        "condition": "IGM base resistance",
        "category": "compression_base",
    },
    # --- Load test ---
    "load_test_compression": {
        "phi": 0.70,
        "condition": "Compression resistance from static load test (max)",
        "category": "load_test",
    },
    "load_test_uplift": {
        "phi": 0.60,
        "condition": "Uplift resistance from static load test",
        "category": "load_test",
    },
    # --- Group effects ---
    "group_block_failure": {
        "phi": 0.55,
        "condition": "Group block failure in clay",
        "category": "group",
    },
    "group_uplift": {
        "phi": 0.45,
        "condition": "Group uplift resistance",
        "category": "group",
    },
    # --- Structural ---
    "structural_compression": {
        "phi": 0.75,
        "condition": "Axial compression (concrete)",
        "category": "structural",
    },
    "structural_flexure_spiral": {
        "phi": 0.90,
        "condition": "Flexure with spiral reinforcement",
        "category": "structural",
    },
    "structural_flexure_tied": {
        "phi": 0.75,
        "condition": "Flexure with tied reinforcement",
        "category": "structural",
    },
    "structural_shear": {
        "phi": 0.90,
        "condition": "Shear and torsion",
        "category": "structural",
    },
    # --- Extreme event ---
    "extreme_uplift": {
        "phi": 0.80,
        "condition": "Uplift under extreme event (scour, vessel impact)",
        "category": "extreme",
    },
    "extreme_lateral": {
        "phi": 0.80,
        "condition": "Lateral resistance under extreme event",
        "category": "extreme",
    },
}


def table_10_5_resistance_factor(method: str) -> dict:
    """Resistance factor for LRFD drilled shaft design (Table 10-5).

    Parameters
    ----------
    method : str
        Lookup key for the resistance condition.  Partial matching supported.
        Examples: 'side_sand_beta', 'base_clay', 'lateral_pushover',
        'load_test_compression', 'group_block', 'structural_shear',
        'extreme_uplift'.

    Returns
    -------
    dict
        {'method': str, 'phi': float, 'condition': str, 'category': str}

    Raises
    ------
    ValueError
        If no matching method is found.
    """
    key = method.lower().strip().replace(" ", "_").replace("-", "_")

    # Exact match
    if key in _TABLE_10_5:
        result = dict(_TABLE_10_5[key])
        result["method"] = key
        return result

    # Partial match — key appears in table key or vice versa
    for k, v in _TABLE_10_5.items():
        if key in k or k in key:
            result = dict(v)
            result["method"] = k
            return result

    # Word-level match
    key_words = key.split("_")
    for k, v in _TABLE_10_5.items():
        k_words = k.split("_")
        if all(w in k_words for w in key_words):
            result = dict(v)
            result["method"] = k
            return result

    available = ", ".join(sorted(_TABLE_10_5.keys()))
    raise ValueError(
        f"No matching method for '{method}'.\nAvailable: {available}"
    )


def table_10_5_by_category(category: str) -> list:
    """List all resistance factors in a given category (Table 10-5).

    Parameters
    ----------
    category : str
        Category filter: 'lateral', 'compression_side', 'compression_base',
        'load_test', 'group', 'structural', 'extreme', or '' for all.

    Returns
    -------
    list of dict
        All entries matching the category, each with 'method', 'phi',
        'condition', and 'category' keys.
    """
    cat = category.lower().strip()
    results = []
    for k, v in _TABLE_10_5.items():
        if not cat or cat in v["category"]:
            entry = dict(v)
            entry["method"] = k
            results.append(entry)
    return results


# ============================================================================
# Table 12-1: Resistance Factors for Lateral Loading (GEC-10 Table 12-1)
# ============================================================================

_TABLE_12_1 = {
    "p_y_single": {
        "phi": 0.67,
        "description": "p-y method for single shaft",
    },
    "broms_method": {
        "phi": 0.40,
        "description": "Broms method for lateral capacity (simplified)",
    },
    "p_y_group": {
        "phi": 0.80,
        "description": "p-y method for group with p-multipliers",
    },
    "extreme_event": {
        "phi": 0.80,
        "description": "Lateral resistance under extreme event",
    },
}


def table_12_1_lateral_resistance_factor(method: str) -> dict:
    """Resistance factor for lateral loading analysis (Table 12-1).

    Parameters
    ----------
    method : str
        Analysis method: 'p_y_single', 'broms', 'p_y_group', 'extreme'.

    Returns
    -------
    dict
        {'method': str, 'phi': float, 'description': str}

    Raises
    ------
    ValueError
        If method is not recognized.
    """
    key = method.lower().strip().replace(" ", "_").replace("-", "_")

    if key in _TABLE_12_1:
        result = dict(_TABLE_12_1[key])
        result["method"] = key
        return result

    # Partial match
    for k, v in _TABLE_12_1.items():
        if key in k or k in key:
            result = dict(v)
            result["method"] = k
            return result

    raise ValueError(
        f"Unknown method '{method}'. Available: "
        f"{', '.join(_TABLE_12_1.keys())}"
    )


# ============================================================================
# Table 14-1: Group Efficiency for Drilled Shaft Groups at 3D Spacing
# (Brown et al. 2010, after various sources)
# ============================================================================

_TABLE_14_1 = [
    {"configuration": "2x1", "efficiency": 1.10, "notes": "2 shafts in line, 3D spacing"},
    {"configuration": "3x1", "efficiency": 1.10, "notes": "3 shafts in line, 3D spacing"},
    {"configuration": "3_triangular", "efficiency": 1.04, "notes": "3 shafts triangular, 3D spacing"},
    {"configuration": "4_square", "efficiency": 1.00, "notes": "4 shafts square (2x2), 3D spacing"},
    {"configuration": "3x3", "efficiency": 0.90, "notes": "9 shafts (3x3), 3D spacing"},
    {"configuration": "4x4", "efficiency": 0.80, "notes": "16 shafts (4x4), 3D spacing"},
]


def table_14_1_group_efficiency(configuration: str) -> dict:
    """Group efficiency factor for drilled shaft groups at 3D spacing (Table 14-1).

    Parameters
    ----------
    configuration : str
        Group configuration: '2x1', '3x1', '3_triangular', '4_square',
        '3x3', '4x4'.

    Returns
    -------
    dict
        {'configuration': str, 'efficiency': float, 'notes': str}

    Raises
    ------
    ValueError
        If configuration is not recognized.
    """
    key = configuration.lower().strip().replace(" ", "_").replace("-", "_")

    for row in _TABLE_14_1:
        if key == row["configuration"]:
            return dict(row)

    # Partial match
    for row in _TABLE_14_1:
        if key in row["configuration"] or row["configuration"] in key:
            return dict(row)

    configs = [r["configuration"] for r in _TABLE_14_1]
    raise ValueError(
        f"Unknown configuration '{configuration}'. "
        f"Available: {', '.join(configs)}"
    )


# ============================================================================
# Table 14-2: P-Multipliers for Lateral Group Analysis
# (Brown et al. 2010)
#
# Row position within group, with spacing as fraction of shaft diameter (D).
# ============================================================================

_TABLE_14_2_SPACING = [3.0, 4.0, 5.0, 6.0]

_TABLE_14_2 = {
    "lead_row": {
        "p_multiplier": [0.70, 0.85, 1.00, 1.00],
        "notes": "Front (lead) row, closest to loading direction",
    },
    "2nd_row": {
        "p_multiplier": [0.50, 0.65, 0.85, 1.00],
        "notes": "Second row behind lead row",
    },
    "3rd_or_more_row": {
        "p_multiplier": [0.35, 0.50, 0.70, 1.00],
        "notes": "Third and subsequent rows",
    },
}


def table_14_2_p_multiplier(row_position: str,
                             spacing_over_d: float) -> dict:
    """P-multiplier for lateral group analysis (Table 14-2).

    Parameters
    ----------
    row_position : str
        Row position in group: 'lead', '2nd', '3rd', 'trail'.
    spacing_over_d : float
        Center-to-center spacing divided by shaft diameter, 3.0 to 6.0+.

    Returns
    -------
    dict
        {'row_position': str, 'spacing_over_d': float,
         'p_multiplier': float, 'notes': str}

    Raises
    ------
    ValueError
        If row_position is not recognized or spacing is below 3D.
    """
    if spacing_over_d < 3.0:
        raise ValueError(
            f"spacing_over_d={spacing_over_d} is below the minimum "
            "of 3.0D in Table 14-2."
        )

    key = row_position.lower().strip().replace(" ", "_").replace("-", "_")

    # Map common aliases
    row_map = {
        "lead": "lead_row",
        "lead_row": "lead_row",
        "front": "lead_row",
        "1st": "lead_row",
        "1st_row": "lead_row",
        "first": "lead_row",
        "2nd": "2nd_row",
        "2nd_row": "2nd_row",
        "second": "2nd_row",
        "3rd": "3rd_or_more_row",
        "3rd_row": "3rd_or_more_row",
        "3rd_or_more": "3rd_or_more_row",
        "3rd_or_more_row": "3rd_or_more_row",
        "trail": "3rd_or_more_row",
        "trailing": "3rd_or_more_row",
    }

    row_key = row_map.get(key)
    if row_key is None:
        raise ValueError(
            f"Unknown row_position '{row_position}'. "
            f"Use: 'lead', '2nd', '3rd', or 'trail'."
        )

    data = _TABLE_14_2[row_key]

    # Clamp spacing to max 6D (p_multiplier = 1.0 for all rows at >=6D)
    if spacing_over_d >= 6.0:
        pm = 1.0
    else:
        pm = _linterp(spacing_over_d, _TABLE_14_2_SPACING,
                       data["p_multiplier"])

    return {
        "row_position": row_key,
        "spacing_over_d": spacing_over_d,
        "p_multiplier": round(pm, 3),
        "notes": data["notes"],
    }


# ============================================================================
# Table 10-1: Relationship Between Reliability Index and Probability of Failure
# (AASHTO LRFD Bridge Design Specifications)
# ============================================================================

_TABLE_10_1_BETA = [2.0, 2.33, 2.5, 3.0, 3.5, 4.0]
_TABLE_10_1_PF = [2.28e-2, 1.0e-2, 6.2e-3, 1.35e-3, 2.33e-4, 3.17e-5]


def table_10_1_reliability_index(beta: float = None,
                                  pf: float = None) -> dict:
    """Reliability index vs probability of failure (Table 10-1).

    Provide either beta or pf; the other will be interpolated.

    Parameters
    ----------
    beta : float, optional
        Reliability index (2.0 to 4.0).
    pf : float, optional
        Probability of failure.

    Returns
    -------
    dict
        {'beta': float, 'pf': float}

    Raises
    ------
    ValueError
        If neither or both arguments are provided, or value is out of range.
    """
    if beta is not None and pf is not None:
        raise ValueError("Provide either beta or pf, not both.")
    if beta is None and pf is None:
        raise ValueError("Provide either beta or pf.")

    if beta is not None:
        if beta < 2.0 or beta > 4.0:
            raise ValueError(f"beta must be 2.0-4.0, got {beta}")
        # pf decreases as beta increases — reverse for interpolation
        pf_result = _linterp(beta, _TABLE_10_1_BETA,
                              _TABLE_10_1_PF)
        return {"beta": beta, "pf": pf_result}

    # pf given — interpolate to get beta
    if pf < _TABLE_10_1_PF[-1] or pf > _TABLE_10_1_PF[0]:
        raise ValueError(
            f"pf must be {_TABLE_10_1_PF[-1]:.2e} to "
            f"{_TABLE_10_1_PF[0]:.2e}, got {pf}"
        )
    # pf is decreasing with beta, so reverse both for monotonic interp
    pf_rev = list(reversed(_TABLE_10_1_PF))
    beta_rev = list(reversed(_TABLE_10_1_BETA))
    beta_result = _linterp(pf, pf_rev, beta_rev)
    return {"beta": round(beta_result, 3), "pf": pf}
