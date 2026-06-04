"""GEC-9 table lookup functions.

Tables from FHWA-HIF-18-031 (GEC-9, April 2018), Design, Analysis, and Testing
of Laterally Loaded Deep Foundations that Support Transportation Facilities.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 4-1: Resistance Factors for Lateral Geotechnical and Strength Limit
# State (from Brown et al. 2010)
#
# Note: Resistance factors for lateral analysis have not been calibrated per
# AASHTO; these values are based on engineering judgment (Brown et al. 2010)
# to ensure ductile response and adequate reserve capacity beyond AASHTO (2014).
# Applies to p-y method (load-displacement analyses) for driven piles or shafts.
# ============================================================================

_TABLE_4_1 = {
    "individual": {
        "phi_r": 0.67,
        "description": (
            "Pushover of individual deep foundation element; "
            "head free to rotate"
        ),
    },
    "single_row": {
        "phi_r": 0.67,
        "description": (
            "Pushover of single row, retaining wall or abutment; "
            "head free to rotate"
        ),
    },
    "group": {
        "phi_r": 0.80,
        "description": (
            "Pushover of element within multiple-row group "
            "with moment connection to cap"
        ),
    },
}


def table_4_1_lateral_resistance_factor(condition: str) -> dict:
    """Resistance factor φr for lateral geotechnical/strength limit state (Table 4-1).

    Based on engineering judgment (Brown et al. 2010).  AASHTO (2014) specifies
    φ = 1.0 for lateral resistance; GEC-9 recommends lower values to ensure
    ductile response.  Applies to p-y method static pushover analysis.

    Parameters
    ----------
    condition : str
        Foundation condition:
        - 'individual' (or 'free_head', 'single'): individual element, free head
        - 'single_row' (or 'wall', 'abutment'): single row / retaining wall /
          abutment, free head
        - 'group' (or 'multi_row', 'moment'): element in multi-row group with
          moment connection to cap

    Returns
    -------
    dict
        {'condition': str, 'phi_r': float, 'description': str}

    Raises
    ------
    ValueError
        If condition is not recognized.
    """
    _aliases = {
        "individual": "individual",
        "free_head": "individual",
        "single": "individual",
        "pushover": "individual",
        "single_row": "single_row",
        "wall": "single_row",
        "retaining_wall": "single_row",
        "abutment": "single_row",
        "row": "single_row",
        "group": "group",
        "multi_row": "group",
        "moment": "group",
        "moment_connection": "group",
        "fixed_head": "group",
    }

    key = condition.lower().strip().replace(" ", "_").replace("-", "_")
    resolved = _aliases.get(key)

    if resolved is None:
        for k in _TABLE_4_1:
            if key in k or k in key:
                resolved = k
                break

    if resolved is None or resolved not in _TABLE_4_1:
        raise ValueError(
            f"Unknown condition '{condition}'. "
            "Use: 'individual', 'single_row', or 'group'."
        )

    result = dict(_TABLE_4_1[resolved])
    result["condition"] = resolved
    return result


# ============================================================================
# Table 7-1: P-Multipliers for Analysis of Groups of Deep Foundation Elements
# (from AASHTO 2014, modified from Hannigan et al. 2006)
#
# Spacing is center-to-center in the direction of loading.
# B = foundation element width or diameter.
# Applicable to vertical piles/shafts only.
# Linear interpolation allowed between 3B and 5B.
# ============================================================================

_TABLE_7_1_SPACING = [3.0, 5.0]

_TABLE_7_1 = {
    "lead_row": {
        "pm": [0.8, 1.0],
        "notes": "Row 1 (lead/front row — least affected by group shadowing)",
    },
    "2nd_row": {
        "pm": [0.4, 0.85],
        "notes": "Row 2",
    },
    "3rd_or_more_row": {
        "pm": [0.3, 0.7],
        "notes": "Row 3 and all subsequent (trailing) rows",
    },
}


def table_7_1_p_multiplier(row_position: str, spacing_over_b: float) -> dict:
    """P-multiplier Pm for group lateral analysis (Table 7-1).

    Scales the p-y resistance of each element in a laterally loaded group:

        p_group = Pm × p_single

    Values from AASHTO (2014), modified from Hannigan et al. (2006).  Applicable
    to all subsurface conditions (soil type does not significantly affect Pm).
    Valid for vertical piles and drilled shafts only.  Linear interpolation
    applies between 3B and 5B spacing.

    Parameters
    ----------
    row_position : str
        Row position in direction of loading:
        'lead' (or '1st', 'front', 'row1'), '2nd' (or 'second', 'row2'),
        '3rd' (or 'trail', 'trailing', '3rd_or_more', 'row3+').
    spacing_over_b : float
        Center-to-center spacing ÷ pile width/diameter.  Must be ≥ 3.0.
        Use 5.0 or more for no group reduction.

    Returns
    -------
    dict
        {'row_position': str, 'spacing_over_b': float,
         'pm': float, 'notes': str}

    Raises
    ------
    ValueError
        If row_position is unrecognized or spacing_over_b < 3.0.
    """
    if spacing_over_b < 3.0:
        raise ValueError(
            f"spacing_over_b={spacing_over_b} is below the minimum of 3.0B "
            "(Table 7-1 applies for 3B ≤ spacing ≤ 5B; use Pm=1.0 beyond 5B)."
        )

    _aliases = {
        "lead": "lead_row",
        "lead_row": "lead_row",
        "front": "lead_row",
        "1st": "lead_row",
        "first": "lead_row",
        "row1": "lead_row",
        "row_1": "lead_row",
        "2nd": "2nd_row",
        "second": "2nd_row",
        "row2": "2nd_row",
        "row_2": "2nd_row",
        "3rd": "3rd_or_more_row",
        "third": "3rd_or_more_row",
        "trail": "3rd_or_more_row",
        "trailing": "3rd_or_more_row",
        "3rd_or_more": "3rd_or_more_row",
        "3rd_or_more_row": "3rd_or_more_row",
        "row3": "3rd_or_more_row",
        "row3+": "3rd_or_more_row",
        "row_3": "3rd_or_more_row",
        "4th": "3rd_or_more_row",
        "fifth": "3rd_or_more_row",
    }

    key = row_position.lower().strip().replace(" ", "_").replace("-", "_")
    row_key = _aliases.get(key)
    if row_key is None:
        raise ValueError(
            f"Unknown row_position '{row_position}'. "
            "Use: 'lead', '2nd', or '3rd' (or 'trail')."
        )

    data = _TABLE_7_1[row_key]

    # _linterp clamps at endpoint values for out-of-range queries.
    # Row 1 is already 1.0 at 5B; rows 2 and 3+ clamp at their 5B values
    # beyond the table range (no extrapolation assumed).
    pm = _linterp(spacing_over_b, _TABLE_7_1_SPACING, data["pm"])

    return {
        "row_position": row_key,
        "spacing_over_b": spacing_over_b,
        "pm": round(pm, 3),
        "notes": data["notes"],
    }


# ============================================================================
# Table A-1: Representative Values of k for Stiff Clays
# (Reese et al. 1975), cited in GEC-9 Appendix A Section A.2
#
# Units: pci (lb/in³).  Ca = average undrained shear strength (ton/ft²).
# Used in the initial linear portion of the p-y curve: p = (k × z) × y
# ============================================================================

_TABLE_A1_CA_MIDPOINTS = [0.75, 1.5, 3.0]  # midpoints of 0.5-1, 1-2, 2-4 ton/ft²
_TABLE_A1_CA_BOUNDS = [0.5, 1.0, 2.0, 4.0]  # bin boundaries

_TABLE_A1_K_STATIC = [500.0, 1000.0, 2000.0]
_TABLE_A1_K_CYCLIC = [200.0, 400.0, 800.0]


def _ca_bin_index(ca_tsf: float) -> int:
    """Return 0, 1, or 2 for Ca bins 0.5-1, 1-2, 2-4 ton/ft²."""
    if ca_tsf < _TABLE_A1_CA_BOUNDS[1]:
        return 0
    if ca_tsf < _TABLE_A1_CA_BOUNDS[2]:
        return 1
    return 2


def table_a1_k_stiff_clay(ca_tsf: float, loading: str = "static") -> dict:
    """Initial p-y modulus k for stiff clay with free water (Table A-1).

    Provides the proportionality coefficient k (pci) for constructing the
    initial linear portion of the Reese et al. (1975) p-y curve:

        p = (k × z) × y   [z in inches, y in inches, p in lb/in]

    Values are bin-based (not interpolated) per Reese et al. (1975).
    For Ca < 0.5 ton/ft², the soft clay Matlock (1970) criterion is more
    appropriate.  For Ca > 4 ton/ft², use k = 2000 (static) or 800 (cyclic).

    Parameters
    ----------
    ca_tsf : float
        Average undrained shear strength over depth z (ton/ft²).
        Must be positive.  Typical stiff clay range: 0.5–4 ton/ft².
    loading : str
        Loading type: 'static' or 'cyclic'.  Default 'static'.

    Returns
    -------
    dict
        {'ca_tsf': float, 'loading': str, 'k_pci': float,
         'ca_range_tsf': str, 'source': str}

    Raises
    ------
    ValueError
        If ca_tsf is not positive or loading is unrecognized.
    """
    if ca_tsf <= 0:
        raise ValueError(f"ca_tsf must be positive, got {ca_tsf}")

    load_key = loading.lower().strip()
    if load_key not in ("static", "cyclic"):
        raise ValueError(f"loading must be 'static' or 'cyclic', got '{loading}'")

    idx = _ca_bin_index(ca_tsf)
    k = _TABLE_A1_K_STATIC[idx] if load_key == "static" else _TABLE_A1_K_CYCLIC[idx]

    bounds = _TABLE_A1_CA_BOUNDS
    lo = bounds[idx]
    hi = bounds[idx + 1]
    ca_range = f"{lo}–{hi} ton/ft²"

    return {
        "ca_tsf": ca_tsf,
        "loading": load_key,
        "k_pci": k,
        "ca_range_tsf": ca_range,
        "source": "GEC-9 Table A-1 (Reese et al. 1975)",
    }


# ============================================================================
# Table A-2: Representative Values of ε50 for Stiff Clays
# (Reese et al. 1975), cited in GEC-9 Appendix A Section A.2
#
# ε50 = axial strain at 50% of peak deviator stress (triaxial test).
# Used to compute y50 = ε50 × D for p-y curve construction.
# ============================================================================

_TABLE_A2_EPS50 = [0.007, 0.005, 0.004]


def table_a2_epsilon50_stiff_clay(ca_tsf: float) -> dict:
    """Strain at 50% peak deviatoric stress ε50 for stiff clay (Table A-2).

    Used in Reese et al. (1975) p-y curve construction:

        y50 = ε50 × D

    where D is the pile/shaft diameter.  Values are bin-based per Table A-2.

    Parameters
    ----------
    ca_tsf : float
        Average undrained shear strength (ton/ft²).  Must be positive.

    Returns
    -------
    dict
        {'ca_tsf': float, 'epsilon_50': float,
         'ca_range_tsf': str, 'source': str}

    Raises
    ------
    ValueError
        If ca_tsf is not positive.
    """
    if ca_tsf <= 0:
        raise ValueError(f"ca_tsf must be positive, got {ca_tsf}")

    idx = _ca_bin_index(ca_tsf)
    eps50 = _TABLE_A2_EPS50[idx]

    bounds = _TABLE_A1_CA_BOUNDS
    lo = bounds[idx]
    hi = bounds[idx + 1]
    ca_range = f"{lo}–{hi} ton/ft²"

    return {
        "ca_tsf": ca_tsf,
        "epsilon_50": eps50,
        "ca_range_tsf": ca_range,
        "source": "GEC-9 Table A-2 (Reese et al. 1975)",
    }


# ============================================================================
# Table A-3: Representative Values of k for Sand
# (Reese et al. 1974), cited in GEC-9 Appendix A Section A.4
#
# Units: pci.  Applies to initial straight-line portion of p-y curve:
#   p = (k × z) × y
# 'condition' = 'submerged' (below water table) or 'above_water'.
# ============================================================================

_TABLE_A3 = {
    "loose": {
        "submerged": 20.0,
        "above_water": 25.0,
    },
    "medium": {
        "submerged": 60.0,
        "above_water": 90.0,
    },
    "dense": {
        "submerged": 125.0,
        "above_water": 225.0,
    },
}


def table_a3_k_sand(relative_density: str, condition: str = "submerged") -> dict:
    """Initial p-y modulus k for sand (Table A-3).

    Provides k (pci) for the initial linear segment of the Reese et al. (1974)
    sand p-y curve:

        p = (k × z) × y   [z in inches, y in inches, p in lb/in]

    Parameters
    ----------
    relative_density : str
        Relative density category: 'loose', 'medium' (or 'medium_dense'),
        or 'dense'.
    condition : str
        Groundwater condition: 'submerged' (below water table) or
        'above_water'.  Default 'submerged'.

    Returns
    -------
    dict
        {'relative_density': str, 'condition': str,
         'k_pci': float, 'source': str}

    Raises
    ------
    ValueError
        If relative_density or condition is not recognized.
    """
    _rd_aliases = {
        "loose": "loose",
        "medium": "medium",
        "medium_dense": "medium",
        "med": "medium",
        "dense": "dense",
    }

    _cond_aliases = {
        "submerged": "submerged",
        "below_water": "submerged",
        "below_water_table": "submerged",
        "saturated": "submerged",
        "above_water": "above_water",
        "above_water_table": "above_water",
        "dry": "above_water",
        "moist": "above_water",
    }

    rd_key = relative_density.lower().strip().replace(" ", "_").replace("-", "_")
    rd_resolved = _rd_aliases.get(rd_key)
    if rd_resolved is None:
        raise ValueError(
            f"Unknown relative_density '{relative_density}'. "
            "Use: 'loose', 'medium', or 'dense'."
        )

    cond_key = condition.lower().strip().replace(" ", "_").replace("-", "_")
    cond_resolved = _cond_aliases.get(cond_key)
    if cond_resolved is None:
        raise ValueError(
            f"Unknown condition '{condition}'. "
            "Use: 'submerged' or 'above_water'."
        )

    k = _TABLE_A3[rd_resolved][cond_resolved]

    return {
        "relative_density": rd_resolved,
        "condition": cond_resolved,
        "k_pci": k,
        "source": "GEC-9 Table A-3 (Reese et al. 1974)",
    }
