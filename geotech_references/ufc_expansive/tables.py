"""UFC 3-220-07 expansive soil lookup tables.

Swell potential classification, active zone depth, foundation
selection guidance, and grade beam void space requirements.
All units SI.
"""

# ---------------------------------------------------------------------------
# Table data
# ---------------------------------------------------------------------------

# Swell potential classification (modified from Holtz & Gibbs 1956,
# Chen 1988, and UFC 3-220-07)
_TABLE_SWELL_POTENTIAL = [
    # (pi_min, pi_max, ll_min, ll_max, classification, typical_swell_pct)
    (0, 10, 0, 30, "very_low", "< 1"),
    (10, 20, 30, 40, "low", "1 - 4"),
    (20, 35, 40, 55, "medium", "4 - 8"),
    (35, 55, 55, 70, "high", "8 - 15"),
    (55, 200, 70, 200, "very_high", "> 15"),
]

_TABLE_ACTIVE_ZONE = {
    # climate -> typical active zone depth (m) and notes
    "arid": {
        "typical_depth_m": 6.0,
        "range_m": (3.0, 9.0),
        "notes": "Deep seasonal moisture change; sparse vegetation",
    },
    "semi_arid": {
        "typical_depth_m": 4.0,
        "range_m": (2.0, 6.0),
        "notes": "Moderate seasonal moisture change",
    },
    "subhumid": {
        "typical_depth_m": 3.0,
        "range_m": (1.5, 4.5),
        "notes": "Moderate rainfall; seasonal variation",
    },
    "humid": {
        "typical_depth_m": 1.5,
        "range_m": (1.0, 3.0),
        "notes": "Shallow moisture fluctuation; consistent rainfall",
    },
    "coastal": {
        "typical_depth_m": 1.0,
        "range_m": (0.5, 2.0),
        "notes": "Shallow active zone; stable moisture conditions",
    },
}

_TABLE_FOUNDATION_SELECTION = {
    # swell_potential -> recommended foundation types
    "very_low": {
        "recommended": ["conventional_slab_on_grade", "strip_footings"],
        "precautions": "Standard design; no special provisions needed",
        "void_space_mm": 0,
    },
    "low": {
        "recommended": ["stiffened_slab_on_grade", "strip_footings"],
        "precautions": "Provide positive drainage away from foundations",
        "void_space_mm": 0,
    },
    "medium": {
        "recommended": ["stiffened_slab_on_grade", "pier_and_beam"],
        "precautions": "Moisture barriers; positive drainage; flexible utilities",
        "void_space_mm": 50,
    },
    "high": {
        "recommended": ["pier_and_beam", "post_tensioned_slab"],
        "precautions": "Deep piers into stable zone; void forms under grade beams; "
                       "moisture barriers; flexible utility connections",
        "void_space_mm": 100,
    },
    "very_high": {
        "recommended": ["pier_and_beam"],
        "precautions": "Deep piers well below active zone; large void space; "
                       "structural floor isolated from soil; moisture barriers; "
                       "flexible utility connections; consider removal and replacement",
        "void_space_mm": 150,
    },
}

_TABLE_GRADE_BEAM_VOID = {
    # swell_potential -> void space under grade beams (mm)
    "very_low": {"void_space_mm": 0, "notes": "No void required"},
    "low": {"void_space_mm": 0, "notes": "No void required; ensure drainage"},
    "medium": {"void_space_mm": 50, "notes": "Minimum 50 mm void with cardboard forms"},
    "high": {"void_space_mm": 100, "notes": "100 mm void; use wax-coated cardboard or foam"},
    "very_high": {"void_space_mm": 150, "notes": "150 mm minimum void; structural floor preferred"},
}


# ---------------------------------------------------------------------------
# Public lookup functions
# ---------------------------------------------------------------------------

def table_swell_potential_classification(
    plasticity_index=None,
    liquid_limit=None,
):
    """Classify swell potential from plasticity index or liquid limit.

    At least one of *plasticity_index* or *liquid_limit* must be given.
    If both are given, the classification is based on the more severe
    (higher swell potential) of the two.

    Parameters
    ----------
    plasticity_index : float, optional
        Plasticity index (%).
    liquid_limit : float, optional
        Liquid limit (%).

    Returns
    -------
    dict
        Keys: classification, typical_swell_pct, pi_range, ll_range.

    Raises
    ------
    ValueError
        If neither parameter is given or values are negative.
    """
    if plasticity_index is None and liquid_limit is None:
        raise ValueError(
            "At least one of plasticity_index or liquid_limit must be given"
        )

    classifications = []

    if plasticity_index is not None:
        if plasticity_index < 0:
            raise ValueError(
                f"plasticity_index must be >= 0, got {plasticity_index}"
            )
        for pi_min, pi_max, _, _, cls, swell in _TABLE_SWELL_POTENTIAL:
            if pi_min <= plasticity_index < pi_max:
                classifications.append((cls, swell, f"{pi_min}-{pi_max}"))
                break
        else:
            # Above the last range
            _, _, _, _, cls, swell = _TABLE_SWELL_POTENTIAL[-1]
            pi_min = _TABLE_SWELL_POTENTIAL[-1][0]
            classifications.append((cls, swell, f">{pi_min}"))

    if liquid_limit is not None:
        if liquid_limit < 0:
            raise ValueError(
                f"liquid_limit must be >= 0, got {liquid_limit}"
            )
        for _, _, ll_min, ll_max, cls, swell in _TABLE_SWELL_POTENTIAL:
            if ll_min <= liquid_limit < ll_max:
                classifications.append((cls, swell, f"LL {ll_min}-{ll_max}"))
                break
        else:
            _, _, _, _, cls, swell = _TABLE_SWELL_POTENTIAL[-1]
            ll_min = _TABLE_SWELL_POTENTIAL[-1][2]
            classifications.append((cls, swell, f"LL >{ll_min}"))

    # Use the more severe classification
    rank = {"very_low": 0, "low": 1, "medium": 2, "high": 3, "very_high": 4}
    worst = max(classifications, key=lambda x: rank.get(x[0], 0))

    result = {
        "classification": worst[0],
        "typical_swell_pct": worst[1],
    }
    if plasticity_index is not None:
        result["plasticity_index"] = plasticity_index
    if liquid_limit is not None:
        result["liquid_limit"] = liquid_limit
    return result


def table_active_zone_depth(climate):
    """Return typical active zone depth for a given climate.

    The active zone is the depth of seasonal moisture change that
    drives shrink-swell movements.

    Parameters
    ----------
    climate : str
        One of: arid, semi_arid, subhumid, humid, coastal.

    Returns
    -------
    dict
        Keys: climate, typical_depth_m, range_m (tuple), notes.

    Raises
    ------
    ValueError
        If *climate* is not recognised.
    """
    key = climate.lower().strip()
    if key not in _TABLE_ACTIVE_ZONE:
        raise ValueError(
            f"Unknown climate '{climate}'. "
            f"Valid: {sorted(_TABLE_ACTIVE_ZONE)}"
        )
    row = _TABLE_ACTIVE_ZONE[key]
    return {"climate": key, **row}


def table_foundation_selection(swell_potential):
    """Recommend foundation type based on swell potential.

    Parameters
    ----------
    swell_potential : str
        One of: very_low, low, medium, high, very_high.

    Returns
    -------
    dict
        Keys: swell_potential, recommended (list), precautions,
        void_space_mm.

    Raises
    ------
    ValueError
        If *swell_potential* is not recognised.
    """
    key = swell_potential.lower().strip()
    if key not in _TABLE_FOUNDATION_SELECTION:
        raise ValueError(
            f"Unknown swell potential '{swell_potential}'. "
            f"Valid: {sorted(_TABLE_FOUNDATION_SELECTION)}"
        )
    row = _TABLE_FOUNDATION_SELECTION[key]
    return {"swell_potential": key, **row}


def table_grade_beam_void_space(swell_potential):
    """Return required void space under grade beams for expansive soils.

    Void space allows upward soil movement without loading the grade
    beam.  Typically created with wax-coated cardboard void forms that
    degrade after construction.

    Parameters
    ----------
    swell_potential : str
        One of: very_low, low, medium, high, very_high.

    Returns
    -------
    dict
        Keys: swell_potential, void_space_mm, notes.

    Raises
    ------
    ValueError
        If *swell_potential* is not recognised.
    """
    key = swell_potential.lower().strip()
    if key not in _TABLE_GRADE_BEAM_VOID:
        raise ValueError(
            f"Unknown swell potential '{swell_potential}'. "
            f"Valid: {sorted(_TABLE_GRADE_BEAM_VOID)}"
        )
    row = _TABLE_GRADE_BEAM_VOID[key]
    return {"swell_potential": key, **row}
