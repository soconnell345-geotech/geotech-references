"""UFC 3-250-01 pavement design lookup tables.

Pavement Design for Roads and Parking Areas (14 November 2016).
Covers roads, streets, walks, and open storage areas — NOT airfields
(airfields are in UFC 3-260-02).

Tables implement exactly as written in the document; English unit
values are stored directly and SI conversions provided where useful.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 4-1: Representative Subgrade Categories
# (Chapter 4, p. 11)
#
# Used for mixed-traffic calculations in lieu of a specific CBR or k value.
# Categories A–D bracket subgrade strength for flexible and rigid pavements.
# ============================================================================

_TABLE_4_1 = {
    "A": {
        "flexible_cbr_range": "≥ 13",
        "representative_cbr": 15,
        "rigid_k_range_psi_in": "≥ 442",
        "representative_k_psi_in": 552.6,
        "representative_k_kPa_mm": round(552.6 * 0.271, 1),
        "description": "Strong subgrade (CBR ≥ 13 or k ≥ 442 psi/in)",
    },
    "B": {
        "flexible_cbr_range": "8 < CBR < 13",
        "representative_cbr": 10,
        "rigid_k_range_psi_in": "221 < k < 442",
        "representative_k_psi_in": 294.7,
        "representative_k_kPa_mm": round(294.7 * 0.271, 1),
        "description": "Good subgrade (8 < CBR ≤ 13 or 221 < k < 442 psi/in)",
    },
    "C": {
        "flexible_cbr_range": "4 < CBR ≤ 8",
        "representative_cbr": 6,
        "rigid_k_range_psi_in": "92 < k ≤ 221",
        "representative_k_psi_in": 147.4,
        "representative_k_kPa_mm": round(147.4 * 0.271, 1),
        "description": "Fair subgrade (4 < CBR ≤ 8 or 92 < k ≤ 221 psi/in)",
    },
    "D": {
        "flexible_cbr_range": "CBR ≤ 4",
        "representative_cbr": 3,
        "rigid_k_range_psi_in": "k ≤ 92",
        "representative_k_psi_in": 73.7,
        "representative_k_kPa_mm": round(73.7 * 0.271, 1),
        "description": "Poor subgrade (CBR ≤ 4 or k ≤ 92 psi/in)",
    },
}


def table_4_1_subgrade_category(cbr):
    """Classify subgrade strength category for mixed-traffic design (Table 4-1).

    Assigns subgrade category A–D based on CBR for use in PCASE mixed-traffic
    equivalency calculations (Chapter 4).  For final thickness design use the
    specific CBR, not just the category.

    Parameters
    ----------
    cbr : float
        Subgrade California Bearing Ratio (%).

    Returns
    -------
    dict
        {'category': str, 'cbr': float, 'representative_cbr': int,
         'representative_k_psi_in': float, 'representative_k_kPa_mm': float,
         'flexible_cbr_range': str, 'rigid_k_range_psi_in': str,
         'description': str}

    Raises
    ------
    ValueError
        If cbr is not positive.
    """
    if cbr <= 0:
        raise ValueError(f"cbr must be > 0, got {cbr}")

    if cbr >= 13:
        cat = "A"
    elif cbr > 8:
        cat = "B"
    elif cbr > 4:
        cat = "C"
    else:
        cat = "D"

    row = _TABLE_4_1[cat]
    return {"category": cat, "cbr": cbr, **row}


# ============================================================================
# Table 6-1: Maximum Permissible Design Values for Subbases and Select
# Materials (Chapter 6, p. 17)
#
# Design CBR values and gradation/plasticity requirements.
# Select material CBR ≤ 20 (limits are suggested, not mandatory).
# ============================================================================

_TABLE_6_1 = {
    50: {
        "layer_type": "Subbase",
        "max_size_in": 3,
        "max_pct_passing_no10": 50,
        "max_pct_passing_no200": 15,
        "max_liquid_limit": 25,
        "max_plasticity_index": 5,
        "notes": "Subbase CBR 50; gradation requirements mandatory",
    },
    40: {
        "layer_type": "Subbase",
        "max_size_in": 3,
        "max_pct_passing_no10": 80,
        "max_pct_passing_no200": 15,
        "max_liquid_limit": 25,
        "max_plasticity_index": 5,
        "notes": "Subbase CBR 40; gradation requirements mandatory",
    },
    30: {
        "layer_type": "Subbase",
        "max_size_in": 3,
        "max_pct_passing_no10": 100,
        "max_pct_passing_no200": 15,
        "max_liquid_limit": 25,
        "max_plasticity_index": 5,
        "notes": "Subbase CBR 30; gradation requirements mandatory",
    },
    20: {
        "layer_type": "Select material",
        "max_size_in": 3,
        "max_pct_passing_no10": None,  # not specified
        "max_pct_passing_no200": 25,
        "max_liquid_limit": 35,
        "max_plasticity_index": 12,
        "notes": (
            "Select material CBR 20; limits are suggested (not mandatory); "
            "used with subgrade CBR < 4 and large ESAL traffic"
        ),
    },
}


def table_6_1_subbase_permissible_values(design_cbr):
    """Maximum permissible design values for subbases/select materials (Table 6-1).

    Returns gradation, liquid limit, and plasticity index requirements for
    the specified design CBR category.  Materials must meet these requirements
    AND achieve the stated CBR in laboratory tests.

    Parameters
    ----------
    design_cbr : int or float
        Design CBR value.  Must be one of: 20, 30, 40, or 50.

    Returns
    -------
    dict
        {'design_cbr': int, 'layer_type': str,
         'max_size_in': int, 'max_pct_passing_no10': int or None,
         'max_pct_passing_no200': int, 'max_liquid_limit': int,
         'max_plasticity_index': int, 'notes': str}

    Raises
    ------
    ValueError
        If design_cbr is not 20, 30, 40, or 50.
    """
    # Find nearest valid CBR level
    valid = sorted(_TABLE_6_1.keys())
    key = int(round(design_cbr))
    if key not in _TABLE_6_1:
        raise ValueError(
            f"design_cbr must be one of {valid}, got {design_cbr}. "
            "Use one of the standard levels or select the closest."
        )
    row = _TABLE_6_1[key]
    return {"design_cbr": key, **row}


# ============================================================================
# Table 7-1: Design CBR Values for Base Course Materials
# (Chapter 7, p. 20)
#
# Design CBR values assigned to base course materials based on service
# behavior records and in-place test data.
# ============================================================================

_TABLE_7_1_BASE = {
    "graded_crushed_aggregate": {
        "design_cbr": 100,
        "notes": "Graded crushed aggregate; highest quality base",
    },
    "water_bound_macadam": {
        "design_cbr": 100,
        "notes": "Water-bound macadam; permitted only if cost-competitive",
    },
    "dry_bound_macadam": {
        "design_cbr": 100,
        "notes": "Dry-bound macadam; permitted only if cost-competitive",
    },
    "bituminous_binder_surface": {
        "design_cbr": 100,
        "notes": "Hot-mix asphalt binder and surface courses (central plant)",
    },
    "limerock": {
        "design_cbr": 80,
        "notes": "Limerock base course",
    },
    "aggregate": {
        "design_cbr": 80,
        "notes": "Aggregate base course; 80 CBR requires ≥ 50% crushed particles",
    },
}


def table_7_1_base_design_cbr(material_type):
    """Design CBR for flexible pavement base course materials (Table 7-1).

    Do not use laboratory CBR tests for base course materials.  These CBR
    values are assigned from service performance records.  Materials must
    conform to quality requirements in guide specifications.

    Parameters
    ----------
    material_type : str
        Base course material.  Options:
        'graded_crushed_aggregate', 'water_bound_macadam',
        'dry_bound_macadam', 'bituminous_binder_surface',
        'limerock', 'aggregate'.

    Returns
    -------
    dict
        {'material_type': str, 'design_cbr': int, 'notes': str}

    Raises
    ------
    ValueError
        If material_type is not recognized.
    """
    key = material_type.lower().strip().replace(" ", "_").replace("-", "_")
    if key not in _TABLE_7_1_BASE:
        raise ValueError(
            f"Unknown material_type '{material_type}'. "
            f"Valid: {sorted(_TABLE_7_1_BASE)}"
        )
    row = _TABLE_7_1_BASE[key]
    return {"material_type": key, **row}


# ============================================================================
# Table 7-2: Minimum Thickness of Flexible Pavement Sections
# (Chapter 7, p. 21)
#
# Values in inches.  Apply when PCASE is mandatory design tool.
# Surface thicknesses (surface_in):
#   ST = Bituminous surface treatment (spray application)
#   MST = Multiple bituminous surface treatments (spray application)
# Notation: (surface_in, base_in, total_in)
# Use minimum surface of 3 in for any vehicle with tire pressure ≥ 100 psi.
# 50-CBR base course restricted to ≤ 500,000 ESALs.
# ============================================================================

# ESAL bin boundaries (upper exclusive except last)
_TABLE_7_2_ESAL_BINS = [
    (0, 20_000),
    (20_001, 150_000),
    (150_001, 500_000),
    (500_001, 2_000_000),
    (2_000_001, 7_000_000),
    (7_000_001, float("inf")),
]

# (surface_in, base_in, total_in) — 'ST'/'MST' coded as 0 for surface treatment
_TABLE_7_2_CBR100 = [
    ("ST", 4, 4.5),
    (2, 4, 6),
    (2, 4, 6),
    (2.5, 4, 6.5),
    (3.5, 4, 7.5),
    (3.5, 4, 7.5),
]

_TABLE_7_2_CBR80 = [
    ("MST", 4, 4.5),
    (2, 4, 6),
    (2.5, 4, 6.5),
    (3, 4, 7),
    (3.5, 4, 7.5),
    (4, 4, 8),
]

_TABLE_7_2_CBR50 = [
    (2, 4, 6),
    (2.5, 4, 6.5),
    (3.5, 4, 7.5),
    None,  # N/A for > 500,000 ESALs
    None,  # N/A
    None,  # N/A
]


def table_7_2_min_thickness(esal, base_cbr):
    """Minimum flexible pavement section thickness (Table 7-2).

    Returns minimum required surface, base, and total thickness in inches
    for the given ESAL level and base CBR.  Apply when PCASE use is
    mandatory.  For roads using State DOT design procedures, refer to
    UFC 3-201-01 for minimums.

    Note: 50-CBR base course is restricted to ESAL ≤ 500,000 (Roads and
    parking areas only).  Conversion: mm = 25.4 × in.

    Parameters
    ----------
    esal : float
        Design equivalent single axle loads for 25-year design life.
    base_cbr : int
        Design CBR of base course material: 50, 80, or 100.

    Returns
    -------
    dict
        {'esal': float, 'base_cbr': int,
         'surface_in': float or str,  ('ST' or 'MST' for surface treatments)
         'base_in': float,
         'total_in': float,
         'surface_mm': float or None,
         'total_mm': float,
         'notes': str}

    Raises
    ------
    ValueError
        If base_cbr is not 50, 80, or 100.
    ValueError
        If 50-CBR base is specified for ESAL > 500,000.
    """
    if base_cbr not in (50, 80, 100):
        raise ValueError(f"base_cbr must be 50, 80, or 100; got {base_cbr}")
    if base_cbr == 50 and esal > 500_000:
        raise ValueError(
            "50-CBR base course is restricted to ESAL ≤ 500,000 for roads "
            "and parking areas per Table 7-2 footnote 2."
        )

    # Find ESAL bin index
    bin_idx = 0
    for i, (lo, hi) in enumerate(_TABLE_7_2_ESAL_BINS):
        if lo <= esal <= hi:
            bin_idx = i
            break
    else:
        bin_idx = len(_TABLE_7_2_ESAL_BINS) - 1

    if base_cbr == 100:
        row = _TABLE_7_2_CBR100[bin_idx]
    elif base_cbr == 80:
        row = _TABLE_7_2_CBR80[bin_idx]
    else:
        row = _TABLE_7_2_CBR50[bin_idx]

    if row is None:
        raise ValueError(
            f"No minimum thickness defined for base_cbr=50 and ESAL={esal}. "
            "50-CBR base is restricted to ≤ 500,000 ESALs."
        )

    surface_in, base_in, total_in = row

    # Surface treatments don't have a numeric mm conversion
    surface_mm = (
        round(surface_in * 25.4, 0) if isinstance(surface_in, (int, float)) else None
    )

    return {
        "esal": esal,
        "base_cbr": base_cbr,
        "surface_in": surface_in,
        "base_in": base_in,
        "total_in": total_in,
        "surface_mm": surface_mm,
        "base_mm": round(base_in * 25.4, 0),
        "total_mm": round(total_in * 25.4, 0),
        "notes": (
            "ST = bituminous surface treatment; MST = multiple bituminous "
            "surface treatments; use ≥ 3 in surface for tire pressure ≥ 100 psi"
        ),
    }


# ============================================================================
# Table 9-1: Equivalency Factors for Stabilized Material
# (Chapter 9, p. 27)
#
# Equivalency factor E: 1 in (25 mm) of stabilized material replaces E in
# of conventional base or subbase.
# t_stab = t_conventional / E
# Cement content limited to ≤ 4% by weight (prevents reflective cracking).
# * = not used for base course (subbase use only).
# ============================================================================

_TABLE_9_1 = {
    # (stabilizer, uscs_key): {'base': float or None, 'subbase': float}
    # uscs_key = simplified soil group identifier
    ("asphalt", "all"): {"base": 1.15, "subbase": 2.30},

    ("cement", "gw_gp_sw_sp"): {"base": 1.15, "subbase": 2.30},
    ("cement", "gw"): {"base": 1.15, "subbase": 2.30},
    ("cement", "gp"): {"base": 1.15, "subbase": 2.30},
    ("cement", "sw"): {"base": 1.15, "subbase": 2.30},
    ("cement", "sp"): {"base": 1.15, "subbase": 2.30},
    ("cement", "gm_gc"): {"base": 1.00, "subbase": 2.00},
    ("cement", "gm"): {"base": 1.00, "subbase": 2.00},
    ("cement", "gc"): {"base": 1.00, "subbase": 2.00},
    ("cement", "ml"): {"base": None, "subbase": 1.70},
    ("cement", "mh"): {"base": None, "subbase": 1.70},
    ("cement", "cl"): {"base": None, "subbase": 1.70},
    ("cement", "ch"): {"base": None, "subbase": 1.70},
    ("cement", "sc"): {"base": None, "subbase": 1.50},
    ("cement", "sm"): {"base": None, "subbase": 1.50},

    ("lime", "ml"): {"base": None, "subbase": 1.00},
    ("lime", "mh"): {"base": None, "subbase": 1.00},
    ("lime", "cl"): {"base": None, "subbase": 1.00},
    ("lime", "ch"): {"base": None, "subbase": 1.00},
    ("lime", "sc"): {"base": None, "subbase": 1.10},
    ("lime", "sm"): {"base": None, "subbase": 1.10},
    ("lime", "gm"): {"base": None, "subbase": 1.10},
    ("lime", "gc"): {"base": None, "subbase": 1.10},

    ("lime_cement_flyash", "ml"): {"base": None, "subbase": 1.30},
    ("lime_cement_flyash", "mh"): {"base": None, "subbase": 1.30},
    ("lime_cement_flyash", "cl"): {"base": None, "subbase": 1.30},
    ("lime_cement_flyash", "ch"): {"base": None, "subbase": 1.30},
    ("lime_cement_flyash", "sc"): {"base": None, "subbase": 1.40},
    ("lime_cement_flyash", "sm"): {"base": None, "subbase": 1.40},
    ("lime_cement_flyash", "gm"): {"base": None, "subbase": 1.40},
    ("lime_cement_flyash", "gc"): {"base": None, "subbase": 1.40},

    ("unbound_crushed_stone", "all"): {"base": 1.00, "subbase": 2.00},
    ("unbound_aggregate", "all"): {"base": None, "subbase": 1.00},
}

# USCS → simplified group key
_USCS_TO_GROUP_9_1 = {
    "gw": "gw", "gp": "gp", "sw": "sw", "sp": "sp",
    "gm": "gm", "gc": "gc",
    "sm": "sm", "sc": "sc",
    "ml": "ml", "mh": "mh",
    "cl": "cl", "ch": "ch",
    "gw-gm": "gm", "gp-gm": "gm", "gw-gc": "gc", "gp-gc": "gc",
    "sw-sm": "sm", "sp-sm": "sm", "sw-sc": "sc", "sp-sc": "sc",
}

_STABILIZER_ALIASES = {
    "asphalt": "asphalt",
    "asphalt_stabilized": "asphalt",
    "bituminous": "asphalt",
    "bitumen": "asphalt",
    "cement": "cement",
    "portland_cement": "cement",
    "cement_stabilized": "cement",
    "lime": "lime",
    "lime_stabilized": "lime",
    "lime_cement_flyash": "lime_cement_flyash",
    "lime_cement_fly_ash": "lime_cement_flyash",
    "lcfa": "lime_cement_flyash",
    "unbound_crushed_stone": "unbound_crushed_stone",
    "crushed_stone": "unbound_crushed_stone",
    "unbound_aggregate": "unbound_aggregate",
    "aggregate": "unbound_aggregate",
}


def table_9_1_equivalency_factor(stabilizer_type, uscs_class, layer_type):
    """Equivalency factor for stabilized pavement material (Table 9-1).

    An equivalency factor E represents the inches of conventional base or
    subbase that can be replaced by 1 inch of stabilized material.
    Stabilized layer thickness = conventional thickness / E.

    Restrictions:
    - Cement content ≤ 4% by weight (prevents reflective cracking).
    - Many stabilized materials not applicable as base course (None returned).
    - Material must meet strength/durability requirements per UFC 3-250-11.

    Parameters
    ----------
    stabilizer_type : str
        Stabilizer: 'asphalt', 'cement', 'lime', 'lime_cement_flyash',
        'unbound_crushed_stone', or 'unbound_aggregate'.
    uscs_class : str
        USCS classification of soil to be stabilized (e.g. 'CL', 'SM').
        Ignored for 'asphalt', 'unbound_crushed_stone', 'unbound_aggregate'
        (use any USCS or 'all').
    layer_type : str
        Layer being replaced: 'base' or 'subbase'.

    Returns
    -------
    dict
        {'stabilizer': str, 'uscs_class': str, 'layer_type': str,
         'equivalency_factor': float, 'note': str}

    Raises
    ------
    ValueError
        If inputs are not recognized or if the combination is not applicable
        (e.g., lime stabilization is not used for base courses).
    """
    stab_key = stabilizer_type.lower().strip().replace(" ", "_").replace("-", "_")
    stab_resolved = _STABILIZER_ALIASES.get(stab_key)
    if stab_resolved is None:
        raise ValueError(
            f"Unknown stabilizer_type '{stabilizer_type}'. "
            f"Valid: {sorted(set(_STABILIZER_ALIASES.values()))}"
        )

    layer_key = layer_type.lower().strip()
    if layer_key not in ("base", "subbase"):
        raise ValueError(f"layer_type must be 'base' or 'subbase', got '{layer_type}'")

    # Stabilizers that apply to all USCS groups
    all_stabs = {"asphalt", "unbound_crushed_stone", "unbound_aggregate"}
    if stab_resolved in all_stabs:
        uscs_key = "all"
    else:
        uscs_key = uscs_class.lower().strip().replace(" ", "").replace("-", "-")
        uscs_key = _USCS_TO_GROUP_9_1.get(uscs_key.replace("-", "-"), uscs_key.split("-")[0])

    lookup = _TABLE_9_1.get((stab_resolved, uscs_key))
    if lookup is None:
        # Try simple USCS key without dual symbol
        simple_key = uscs_class.lower().strip().split("-")[0].strip()
        lookup = _TABLE_9_1.get((stab_resolved, simple_key))

    if lookup is None:
        raise ValueError(
            f"No equivalency factor for stabilizer='{stab_resolved}', "
            f"uscs='{uscs_class}' in Table 9-1. "
            "Check that the USCS class is covered by this stabilizer."
        )

    e = lookup[layer_key]
    if e is None:
        raise ValueError(
            f"'{stab_resolved}'-stabilized '{uscs_class}' is not used as a "
            f"{layer_key} course per Table 9-1 (marked *)."
        )

    return {
        "stabilizer": stab_resolved,
        "uscs_class": uscs_class.upper(),
        "layer_type": layer_key,
        "equivalency_factor": e,
        "note": (
            f"1 in of this stabilized {layer_key} replaces {e} in of "
            "conventional material; t_stab = t_conventional / E"
        ),
    }


# ============================================================================
# Table 10-1: Modulus of Soil Reaction k (psi/in) for Rigid Pavement Design
# (Chapter 10, p. 31)
#
# k values by soil type and moisture content.  These are guides only;
# field plate-bearing tests are preferred.
# Conversion: kPa/mm = psi/in × 0.271
# Notes:
#   - Dry density < 90% of ASTM D1557 max: reduce k by 50 psi/in (min 25)
#   - Dry density > 95%: slight increase allowed (max 500 psi/in)
#   - Frost area k values per Chapter 19 governs
# ============================================================================

# (soil_group, moisture_range_mid) → k (psi/in)
# Moisture ranges: 1-4, 5-8, 9-12, 13-16, 17-20, 21-24, 25-28, >28
_TABLE_10_1_MOISTURE_MIDS = [2.5, 6.5, 10.5, 14.5, 18.5, 22.5, 26.5, 32.0]

_TABLE_10_1 = {
    # soil_group: [k values at moisture mid-points; None = not applicable]
    "oh_ch_mh": [None, 175, 150, 125, 100, 75, 50, 25],
    "ol_cl_ml": [None, 200, 175, 150, 125, 100, 75, 50],
    "sm_sc":    [300, 250, 225, 200, 150, None, None, None],
    "sw_sp":    [350, 300, 250, None, None, None, None, None],
    "gm_gc":    [400, 350, 300, 250, None, None, None, None],
    "gw_gp":    [500, 450, None, None, None, None, None, None],
}

_USCS_TO_GROUP_10_1 = {
    "oh": "oh_ch_mh", "ch": "oh_ch_mh", "mh": "oh_ch_mh",
    "ol": "ol_cl_ml", "cl": "ol_cl_ml", "ml": "ol_cl_ml",
    "cl-ml": "ol_cl_ml", "cl_ml": "ol_cl_ml",
    "sm": "sm_sc", "sc": "sm_sc",
    "sw": "sw_sp", "sp": "sw_sp",
    "sw-sm": "sw_sp", "sp-sm": "sw_sp",
    "sw-sc": "sw_sp", "sp-sc": "sw_sp",
    "gm": "gm_gc", "gc": "gm_gc",
    "gw-gm": "gm_gc", "gp-gm": "gm_gc",
    "gw-gc": "gm_gc", "gp-gc": "gm_gc",
    "gw": "gw_gp", "gp": "gw_gp",
}


def table_10_1_k_subgrade(uscs_group, moisture_pct):
    """Typical modulus of soil reaction k for rigid pavement design (Table 10-1).

    These are typical values for guidance only.  Field plate-bearing tests
    are preferred for final design.  Values assume dry density = 90–95% of
    ASTM D1557 maximum density.

    Parameters
    ----------
    uscs_group : str
        USCS soil classification (e.g., 'CL', 'SM', 'GW').
    moisture_pct : float
        Soil moisture content (%).  Must be positive.

    Returns
    -------
    dict
        {'uscs_group': str, 'moisture_pct': float,
         'k_psi_in': float, 'k_kPa_mm': float, 'note': str}

    Raises
    ------
    ValueError
        If USCS group is not covered or moisture content is out of range
        for that soil type.
    """
    if moisture_pct <= 0:
        raise ValueError(f"moisture_pct must be > 0, got {moisture_pct}")

    key = uscs_group.lower().strip().replace(" ", "")
    group = _USCS_TO_GROUP_10_1.get(key)
    if group is None:
        raise ValueError(
            f"Unknown USCS group '{uscs_group}' for Table 10-1. "
            f"Valid groups: {sorted(set(_USCS_TO_GROUP_10_1.values()))}"
        )

    values = _TABLE_10_1[group]

    # Find k at the given moisture content by picking the applicable range bin
    # Moisture range mid-points: 2.5, 6.5, 10.5, 14.5, 18.5, 22.5, 26.5, 32.0
    # We simply find the bin that brackets the moisture content
    bin_edges = [0, 4, 8, 12, 16, 20, 24, 28, float("inf")]
    bin_idx = None
    for i in range(len(bin_edges) - 1):
        if bin_edges[i] < moisture_pct <= bin_edges[i + 1]:
            bin_idx = i
            break
    if bin_idx is None:
        bin_idx = 0  # moisture ≤ 4 → bin 0

    k = values[bin_idx]
    if k is None:
        raise ValueError(
            f"Table 10-1 has no data for soil group '{uscs_group}' at "
            f"moisture = {moisture_pct}% (too high for this soil type). "
            "Such soils would not normally be present at those moisture contents."
        )

    return {
        "uscs_group": uscs_group.upper(),
        "moisture_pct": moisture_pct,
        "k_psi_in": float(k),
        "k_kPa_mm": round(k * 0.271, 1),
        "note": (
            "Typical guide values at 90–95% ASTM D1557; reduce by 50 psi/in "
            "if density < 90% (min 25 psi/in); use field plate-bearing tests "
            "for final design"
        ),
    }


# ============================================================================
# Table 19-2: Frost Design Soil Classification
# (Chapter 19, p. 70)
#
# Soils classified into groups based on USCS type and percentage of particles
# finer than 0.02 mm by weight.  Primary inputs: USCS class + fines fraction.
# ============================================================================

# (uscs_simple, fines_pct_range): (frost_group, subgroup, description)
_TABLE_19_2 = {
    # NFS: Non-frost susceptible
    ("gw_gp", "0-1.5"): ("NFS", "a", "Gravels 0-1.5% finer than 0.02 mm"),
    ("crushed_stone", "0-1.5"): ("NFS", "a", "Crushed stone/rock"),
    ("sw_sp", "0-3"): ("NFS", "b", "Sands 0-3% finer than 0.02 mm"),
    # PFS: Possibly frost susceptible (laboratory test needed)
    ("gw_gp", "1.5-3"): ("PFS", "a", "Gravels 1.5-3% finer than 0.02 mm"),
    ("sw_sp", "3-10"): ("PFS", "b", "Sands 3-10% finer than 0.02 mm"),
    # S1 and S2: Low frost susceptibility (suitable for subbase)
    ("gw_gp_gwgm_gpgm", "3-6"): ("S1", "", "Gravelly soils 3-6% finer than 0.02 mm"),
    ("sw_sp_swsm_spsm", "3-6"): ("S2", "", "Sandy soils 3-6% finer than 0.02 mm"),
    # F1: Frost susceptible
    ("gm_gwgm_gpgm", "6-10"): ("F1", "", "Gravelly soils 6-10% finer than 0.02 mm"),
    # F2a and F2b
    ("gm_gwgm_gpgm", "10-20"): ("F2", "a", "Gravelly soils 10-20% finer than 0.02 mm"),
    ("sm_swsm_spsm", "6-15"): ("F2", "b", "Sands 6-15% finer than 0.02 mm"),
    # F3a, F3b, F3c
    ("gm_gc", ">20"): ("F3", "a", "Gravelly soils > 20% finer than 0.02 mm"),
    ("sm_sc", ">15"): ("F3", "b", "Sands (except very fine silty sands) > 15%"),
    ("cl_ch", "pi>12"): ("F3", "c", "Clays PI > 12"),
    # F4a, F4b, F4c, F4d
    ("ml_mh", "all"): ("F4", "a", "All silts ML/MH"),
    ("sm_fine", ">15"): ("F4", "b", "Very fine silty sands SM > 15%"),
    ("cl_clml", "pi>12"): ("F4", "c", "Clays CL/CL-ML PI > 12"),
    ("varved_clay", "all"): ("F4", "d", "Varved clays and other banded fine-grained sediments"),
}

# USCS to frost group — simplified lookup using primary USCS class
# and fines percentage as the key differentiation
_USCS_FROST_RULES = [
    # (uscs_pattern, fines_min, fines_max, frost_group, subgroup)
    # Silts and organic — always F4
    ("ml", 0, 100, "F4", "a"),
    ("mh", 0, 100, "F4", "a"),
    ("ol", 0, 100, "F4", "a"),
    # Clays
    ("ch", 0, 100, "F3", "c"),  # CH is F3c (high plasticity)
    ("cl-ml", 0, 100, "F4", "c"),
    ("cl", 0, 100, "F3", "c"),
    ("oh", 0, 100, "F3", "c"),
    ("pt", 0, 100, "F4", "d"),
    # Sandy soils
    ("sm", 15.01, 100, "F4", "b"),   # very fine silty sands > 15%
    ("sm", 6, 15, "F2", "b"),
    ("sm", 3, 6, "S2", ""),
    ("sm", 0, 3, "NFS", "b"),
    ("sc", 15.01, 100, "F3", "b"),
    ("sc", 0, 15, "F3", "b"),
    ("sw-sm", 6, 15, "F2", "b"),
    ("sw-sm", 3, 6, "S2", ""),
    ("sp-sm", 6, 15, "F2", "b"),
    ("sp-sm", 3, 6, "S2", ""),
    ("sw", 3, 10, "PFS", "b"),
    ("sw", 0, 3, "NFS", "b"),
    ("sp", 3, 10, "PFS", "b"),
    ("sp", 0, 3, "NFS", "b"),
    # Gravelly soils
    ("gm", 20.01, 100, "F3", "a"),
    ("gm", 10, 20, "F2", "a"),
    ("gm", 6, 10, "F1", ""),
    ("gm", 3, 6, "S1", ""),
    ("gc", 20.01, 100, "F3", "a"),
    ("gc", 6, 20, "F2", "a"),
    ("gw-gm", 20.01, 100, "F3", "a"),
    ("gw-gm", 10, 20, "F2", "a"),
    ("gw-gm", 6, 10, "F1", ""),
    ("gw-gm", 3, 6, "S1", ""),
    ("gp-gm", 10, 20, "F2", "a"),
    ("gp-gm", 6, 10, "F1", ""),
    ("gp-gm", 3, 6, "S1", ""),
    ("gw-gc", 6, 20, "F2", "a"),
    ("gp-gc", 6, 20, "F2", "a"),
    ("gw", 3, 6, "S1", ""),
    ("gw", 1.5, 3, "PFS", "a"),
    ("gw", 0, 1.5, "NFS", "a"),
    ("gp", 3, 6, "S1", ""),
    ("gp", 1.5, 3, "PFS", "a"),
    ("gp", 0, 1.5, "NFS", "a"),
]


def table_19_2_frost_classification(uscs_class, finer_than_0_02mm_pct=None):
    """Frost design soil classification for pavement design (Table 19-2).

    Classifies soil into frost susceptibility groups NFS, PFS, S1, S2, or
    F1–F4 for seasonal frost pavement design.  S1 and S2 soils are suitable
    for subbase in frost areas; F-groups require frost thickness design.

    Parameters
    ----------
    uscs_class : str
        USCS soil classification symbol (e.g. 'ML', 'SM', 'GW').
    finer_than_0_02mm_pct : float, optional
        Percentage of particles finer than 0.02 mm by weight.  Required
        for granular soils where group depends on fines content.  For
        fine-grained soils (ML, MH, CL, CH, OL, OH, PT) this is not needed.

    Returns
    -------
    dict
        {'uscs_class': str, 'finer_0_02mm_pct': float or None,
         'frost_group': str, 'subgroup': str, 'description': str}

    Raises
    ------
    ValueError
        If uscs_class is not recognized.
    ValueError
        If finer_than_0_02mm_pct is required but not supplied for
        a soil where the group depends on fines content.
    """
    key = uscs_class.lower().strip()

    fines = finer_than_0_02mm_pct if finer_than_0_02mm_pct is not None else 0.0

    for (uscs_pat, f_min, f_max, group, subgroup) in _USCS_FROST_RULES:
        if key == uscs_pat and f_min <= fines <= f_max:
            row = _TABLE_19_2.get((uscs_pat, _fines_key(fines)))
            if row:
                desc = row[2]
            else:
                desc = f"{uscs_class.upper()} — frost group {group}{subgroup}"
            return {
                "uscs_class": uscs_class.upper(),
                "finer_0_02mm_pct": finer_than_0_02mm_pct,
                "frost_group": group,
                "subgroup": subgroup,
                "description": desc,
            }

    # If no match found
    raise ValueError(
        f"Unable to classify uscs_class='{uscs_class}' with "
        f"finer_0_02mm={finer_than_0_02mm_pct}% using Table 19-2. "
        "Provide finer_than_0_02mm_pct for granular soils."
    )


def _fines_key(fines_pct):
    """Helper to return approximate fines range string."""
    if fines_pct <= 1.5:
        return "0-1.5"
    if fines_pct <= 3:
        return "1.5-3"
    if fines_pct <= 6:
        return "3-6"
    if fines_pct <= 10:
        return "6-10"
    if fines_pct <= 15:
        return "6-15"
    if fines_pct <= 20:
        return "10-20"
    return ">20"


# ============================================================================
# Table 19-3: Frost-Area Soil Support Indexes for Subgrade Soils
# (Chapter 19, p. 80)
#
# Used as if CBR values in the Appendix E design curves (reduced subgrade
# strength method).  These are weighted average values for an annual cycle
# including thaw-weakening; cannot be measured by CBR test.
# ============================================================================

_TABLE_19_3 = {
    ("F1", "S1"): 9.0,
    ("F2", "S2"): 6.5,
    ("F3", ""): 3.5,
    ("F4", ""): 3.5,
}


def table_19_3_frost_support_index(frost_group):
    """Frost-area soil support index for flexible pavement design (Table 19-3).

    Returns the frost-area soil support index, which is used as if it were
    a CBR value when entering Appendix E design curves for the reduced
    subgrade strength method.  These are weighted average values for an
    annual cycle and cannot be determined by CBR testing.

    Parameters
    ----------
    frost_group : str
        Frost susceptibility group: 'F1', 'F2', 'F3', 'F4', 'S1', or 'S2'.
        F3 and F4 both map to 3.5.  S1 and F1 both map to 9.0.

    Returns
    -------
    dict
        {'frost_group': str, 'soil_support_index': float, 'note': str}

    Raises
    ------
    ValueError
        If frost_group is not recognized.
    """
    group_upper = frost_group.upper().strip()
    # Look up by group
    _mapping = {
        "F1": 9.0, "S1": 9.0,
        "F2": 6.5, "S2": 6.5,
        "F3": 3.5, "F4": 3.5,
        "NFS": None, "PFS": None,
    }
    if group_upper not in _mapping:
        raise ValueError(
            f"Unknown frost_group '{frost_group}'. "
            "Valid: F1, F2, F3, F4, S1, S2, NFS, PFS."
        )
    idx = _mapping[group_upper]
    if idx is None:
        raise ValueError(
            f"'{frost_group}' (NFS or PFS) soils do not require frost area "
            "soil support index — use normal subgrade CBR for design."
        )

    return {
        "frost_group": group_upper,
        "soil_support_index": idx,
        "note": (
            "Use as CBR value in Appendix E design curves for reduced "
            "subgrade strength method; this is a weighted annual average — "
            "not measurable by CBR test"
        ),
    }
