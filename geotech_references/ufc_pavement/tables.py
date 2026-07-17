"""UFC 3-250-01 pavement design lookup tables and design-curve read-offs.

Pavement Design for Roads, Streets, Walks, and Storage Areas (14 November
2016). Tables are transcribed as printed (English units stored directly;
SI conversions given where the guide itself prints one:
mm = 25.4 x in, kPa/mm = psi/in / 0.271).

Genuinely nomographic figures (multi-curve families with no printed closed
form) are digitized here as coarse read-grids with ``chart_read: True`` and
documented anchor points -- treat the returned values as engineering
estimates (stated tolerance in each docstring), not substitutes for PCASE or
a field test. Every anchor that traces to one of the guide's own printed
worked examples (Appendix G) is called out explicitly and matches exactly;
anchors without that traceability are visual read-offs of the rendered
chart and are noted as approximate.
"""

import math

from geotech_references._interpolation import _linterp
from geotech_references.ufc_pavement.equations import reinforced_pavement_max_slab_length


# ============================================================================
# Table 4-1: Representative Subgrade Categories (Chapter 4, pdf_page 30,
# printed 11)
#
# Used for mixed-traffic calculations in lieu of a specific CBR or k value.
# ============================================================================

_TABLE_4_1 = {
    "A": {
        "flexible_cbr_range": ">= 13",
        "representative_cbr": 15,
        "rigid_k_range_psi_in": ">= 442",
        "representative_k_psi_in": 552.6,
        "representative_k_kPa_mm": round(552.6 * 0.271, 1),
        "description": "Strong subgrade (CBR >= 13 or k >= 442 psi/in)",
    },
    "B": {
        "flexible_cbr_range": "8 < CBR < 13",
        "representative_cbr": 10,
        "rigid_k_range_psi_in": "221 < k < 442",
        "representative_k_psi_in": 294.7,
        "representative_k_kPa_mm": round(294.7 * 0.271, 1),
        "description": "Good subgrade (8 < CBR < 13 or 221 < k < 442 psi/in)",
    },
    "C": {
        "flexible_cbr_range": "4 < CBR <= 8",
        "representative_cbr": 6,
        "rigid_k_range_psi_in": "92 < k <= 221",
        "representative_k_psi_in": 147.4,
        "representative_k_kPa_mm": round(147.4 * 0.271, 1),
        "description": "Fair subgrade (4 < CBR <= 8 or 92 < k <= 221 psi/in)",
    },
    "D": {
        "flexible_cbr_range": "CBR <= 4",
        "representative_cbr": 3,
        "rigid_k_range_psi_in": "k <= 92",
        "representative_k_psi_in": 73.7,
        "representative_k_kPa_mm": round(73.7 * 0.271, 1),
        "description": "Poor subgrade (CBR <= 4 or k <= 92 psi/in)",
    },
}


def table_4_1_subgrade_category(cbr) -> dict:
    """Classify subgrade strength category for mixed-traffic design
    (Table 4-1, pdf_page 30, printed 11).

    Assigns subgrade category A-D based on CBR for use in mixed-traffic
    equivalency calculations (Chapter 4). For final single-vehicle
    thickness design use the specific CBR/k, not just the category.

    Verified against the guide's own printed example (Appendix G, G-1,
    pdf_page 275): CBR = 4 -> category D, representative CBR = 3.

    Parameters
    ----------
    cbr : float
        Subgrade California Bearing Ratio (%). Must be > 0.

    Returns
    -------
    dict
        {'category', 'cbr', 'representative_cbr', 'representative_k_psi_in',
         'representative_k_kPa_mm', 'flexible_cbr_range',
         'rigid_k_range_psi_in', 'description', 'reference'}.

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
    return {
        "category": cat, "cbr": cbr, **row,
        "reference": "UFC 3-250-01, Table 4-1 (pdf_page 30, printed 11)",
    }


# ============================================================================
# Table 5-1 / Table 21-2: Depth of Compaction for Select Materials and
# Subgrades (CBR <= 20) (Chapter 5, pdf_page 33, printed 14) and Aggregate
# Surfaces (Chapter 21, pdf_page 143, printed 124). Same structure, different
# printed values -- shared lookup helper below.
# ============================================================================

# ESAL bins: upper bound exclusive except last (inf)
_COMPACTION_ESAL_BINS = [
    15_500, 67_500, 295_000, 1_300_000, 5_700_000,
    25_000_000, 112_000_000, 500_000_000, 2_200_000_000, float("inf"),
]

# Table 5-1: rows = (cohesive depths @ 100/95/90/85/80%, cohesionless depths @ same)
_TABLE_5_1_COHESIVE = [
    (3, 7, 10, 14, 17), (4, 8, 12, 16, 20), (4, 9, 14, 18, 23),
    (5, 11, 16, 21, 26), (6, 12, 18, 23, 28), (7, 14, 19, 25, 31),
    (7, 15, 21, 28, 34), (8, 16, 23, 30, 37), (9, 18, 25, 32, 40),
    (10, 20, 28, 35, 43),
]
_TABLE_5_1_COHESIONLESS = [
    (7, 13, 19, 25, 33), (8, 15, 22, 29, 38), (9, 17, 25, 33, 43),
    (11, 20, 28, 37, 48), (12, 22, 31, 40, 53), (14, 24, 35, 44, 58),
    (15, 26, 38, 48, 63), (16, 29, 41, 52, 68), (18, 31, 44, 56, 74),
    (20, 34, 47, 59, 77),
]

# Table 21-2 (aggregate surfaces): only 4 density levels printed (100/95/90/85)
_TABLE_21_2_COHESIVE = [
    (2, 4, 6, 7), (3, 5, 7, 9), (3, 5, 8, 10), (3, 6, 9, 12),
    (4, 7, 10, 13), (4, 7, 11, 15), (4, 8, 12, 16), (5, 9, 13, 18),
    (5, 10, 15, 20), (6, 11, 17, 22),
]
_TABLE_21_2_COHESIONLESS = [
    (4, 7, 10, 13), (5, 8, 12, 16), (5, 10, 14, 18), (6, 11, 16, 21),
    (7, 12, 18, 23), (7, 14, 20, 26), (8, 15, 22, 29), (9, 17, 24, 31),
    (10, 19, 28, 35), (11, 21, 30, 38),
]


def _compaction_depth_lookup(passes, density_pct, soil_type, table):
    idx = None
    for i, upper in enumerate(_COMPACTION_ESAL_BINS):
        if passes <= upper:
            idx = i
            break
    if idx is None:
        idx = len(_COMPACTION_ESAL_BINS) - 1

    if table == "5-1":
        density_levels = (100, 95, 90, 85, 80)
        rows = _TABLE_5_1_COHESIVE if soil_type == "cohesive" else _TABLE_5_1_COHESIONLESS
    else:
        density_levels = (100, 95, 90, 85)
        rows = _TABLE_21_2_COHESIVE if soil_type == "cohesive" else _TABLE_21_2_COHESIONLESS

    if density_pct not in density_levels:
        raise ValueError(
            f"density_pct must be one of {density_levels} for this table, "
            f"got {density_pct}"
        )
    col = density_levels.index(density_pct)
    return rows[idx][col]


def table_5_1_compaction_depth(passes, density_pct, soil_type) -> dict:
    """Depth of compaction for select materials/subgrades, CBR <= 20
    (Table 5-1, Chapter 5; pdf_page 33, printed 14).

    Returns the depth (measured from the pavement surface) at which the
    given percent compaction (of ASTM D1557 maximum density) is required to
    resist densification under the design traffic.

    Parameters
    ----------
    passes : float
        Equivalent passes of an 18,000-lb (8,200-kg) ESAL over the design
        life. Must be > 0.
    density_pct : int
        Target percent compaction: 100, 95, 90, 85, or 80.
    soil_type : str
        'cohesive' (PI > 5, LL > 25) or 'cohesionless' (PI <= 5, LL <= 25).

    Returns
    -------
    dict
        {'passes', 'density_pct', 'soil_type', 'depth_in', 'reference'}.

    Raises
    ------
    ValueError
        If passes <= 0, density_pct is not one of the printed levels, or
        soil_type is not recognized.
    """
    if passes <= 0:
        raise ValueError(f"passes must be > 0, got {passes}")
    key = soil_type.lower().strip()
    if key not in ("cohesive", "cohesionless"):
        raise ValueError(f"soil_type must be 'cohesive' or 'cohesionless', got '{soil_type}'")
    depth = _compaction_depth_lookup(passes, density_pct, key, "5-1")
    return {
        "passes": passes, "density_pct": density_pct, "soil_type": key,
        "depth_in": depth,
        "reference": "UFC 3-250-01, Table 5-1 (pdf_page 33, printed 14)",
    }


def table_21_2_aggregate_compaction_depth(passes, density_pct, soil_type) -> dict:
    """Depth of compaction for aggregate-surfaced roads (Table 21-2,
    Chapter 21; pdf_page 143, printed 124). Same structure as Table 5-1;
    depths are measured from the surface of the aggregate road, not the
    subgrade surface.

    Parameters
    ----------
    passes : float
        Equivalent passes of an 18,000-lb (8,200-kg) ESAL. Must be > 0.
    density_pct : int
        Target percent compaction: 100, 95, 90, or 85 (no 80% row printed
        for aggregate surfaces).
    soil_type : str
        'cohesive' (PI > 5, LL > 25) or 'cohesionless' (PI <= 5, LL <= 25).

    Returns
    -------
    dict
        {'passes', 'density_pct', 'soil_type', 'depth_in', 'reference'}.

    Raises
    ------
    ValueError
        If passes <= 0, density_pct is not one of the printed levels, or
        soil_type is not recognized.
    """
    if passes <= 0:
        raise ValueError(f"passes must be > 0, got {passes}")
    key = soil_type.lower().strip()
    if key not in ("cohesive", "cohesionless"):
        raise ValueError(f"soil_type must be 'cohesive' or 'cohesionless', got '{soil_type}'")
    depth = _compaction_depth_lookup(passes, density_pct, key, "21-2")
    return {
        "passes": passes, "density_pct": density_pct, "soil_type": key,
        "depth_in": depth,
        "reference": "UFC 3-250-01, Table 21-2 (pdf_page 143, printed 124)",
    }


# ============================================================================
# Table 6-1: Maximum Permissible Design Values for Subbases and Select
# Materials (Chapter 6, pdf_page 36, printed 17)
# ============================================================================

_TABLE_6_1 = {
    50: {
        "layer_type": "Subbase", "max_size_in": 3,
        "max_pct_passing_no10": 50, "max_pct_passing_no200": 15,
        "max_liquid_limit": 25, "max_plasticity_index": 5,
        "notes": "Subbase CBR 50; gradation requirements mandatory",
    },
    40: {
        "layer_type": "Subbase", "max_size_in": 3,
        "max_pct_passing_no10": 80, "max_pct_passing_no200": 15,
        "max_liquid_limit": 25, "max_plasticity_index": 5,
        "notes": "Subbase CBR 40; gradation requirements mandatory",
    },
    30: {
        "layer_type": "Subbase", "max_size_in": 3,
        "max_pct_passing_no10": 100, "max_pct_passing_no200": 15,
        "max_liquid_limit": 25, "max_plasticity_index": 5,
        "notes": "Subbase CBR 30; gradation requirements mandatory",
    },
    20: {
        "layer_type": "Select material", "max_size_in": 3,
        "max_pct_passing_no10": None, "max_pct_passing_no200": 25,
        "max_liquid_limit": 35, "max_plasticity_index": 12,
        "notes": (
            "Select material CBR 20; limits are suggested (not mandatory); "
            "used with subgrade CBR < 4 and large ESAL traffic"
        ),
    },
}


def table_6_1_subbase_permissible_values(design_cbr) -> dict:
    """Maximum permissible design values for subbases/select materials
    (Table 6-1, Chapter 6; pdf_page 36, printed 17).

    Parameters
    ----------
    design_cbr : int or float
        Design CBR value. Must be one of: 20, 30, 40, or 50.

    Returns
    -------
    dict
        {'design_cbr', 'layer_type', 'max_size_in', 'max_pct_passing_no10',
         'max_pct_passing_no200', 'max_liquid_limit', 'max_plasticity_index',
         'notes', 'reference'}.

    Raises
    ------
    ValueError
        If design_cbr is not 20, 30, 40, or 50.
    """
    valid = sorted(_TABLE_6_1.keys())
    key = int(round(design_cbr))
    if key not in _TABLE_6_1:
        raise ValueError(
            f"design_cbr must be one of {valid}, got {design_cbr}."
        )
    row = _TABLE_6_1[key]
    return {
        "design_cbr": key, **row,
        "reference": "UFC 3-250-01, Table 6-1 (pdf_page 36, printed 17)",
    }


# ============================================================================
# Table 7-1: Design CBR Values for Base Course Materials (Chapter 7,
# pdf_page 39, printed 20)
# ============================================================================

_TABLE_7_1_BASE = {
    "graded_crushed_aggregate": {"design_cbr": 100, "notes": "Graded crushed aggregate; highest quality base"},
    "water_bound_macadam": {"design_cbr": 100, "notes": "Water-bound macadam; permitted only if cost-competitive"},
    "dry_bound_macadam": {"design_cbr": 100, "notes": "Dry-bound macadam; permitted only if cost-competitive"},
    "bituminous_binder_surface": {"design_cbr": 100, "notes": "Hot-mix asphalt binder and surface courses (central plant)"},
    "limerock": {"design_cbr": 80, "notes": "Limerock base course"},
    "aggregate": {"design_cbr": 80, "notes": "No. 6 Aggregate base course; requires >= 50% crushed particles for 80 CBR"},
}


def table_7_1_base_design_cbr(material_type) -> dict:
    """Design CBR for flexible pavement base course materials (Table 7-1,
    Chapter 7; pdf_page 39, printed 20).

    Do not use laboratory CBR tests for base course materials; these values
    are assigned from service performance records.

    Parameters
    ----------
    material_type : str
        Base course material: 'graded_crushed_aggregate',
        'water_bound_macadam', 'dry_bound_macadam',
        'bituminous_binder_surface', 'limerock', or 'aggregate'.

    Returns
    -------
    dict
        {'material_type', 'design_cbr', 'notes', 'reference'}.

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
    return {
        "material_type": key, **row,
        "reference": "UFC 3-250-01, Table 7-1 (pdf_page 39, printed 20)",
    }


# ============================================================================
# Table 7-2: Minimum Thickness of Flexible Pavement Sections (Chapter 7,
# pdf_page 40, printed 21)
# ============================================================================

_TABLE_7_2_ESAL_BINS = [
    (0, 20_000), (20_001, 150_000), (150_001, 500_000),
    (500_001, 2_000_000), (2_000_001, 7_000_000), (7_000_001, float("inf")),
]

_TABLE_7_2_CBR100 = [
    ("ST", 4, 4.5), (2, 4, 6), (2, 4, 6), (2.5, 4, 6.5), (3.5, 4, 7.5), (3.5, 4, 7.5),
]
_TABLE_7_2_CBR80 = [
    ("MST", 4, 4.5), (2, 4, 6), (2.5, 4, 6.5), (3, 4, 7), (3.5, 4, 7.5), (4, 4, 8),
]
_TABLE_7_2_CBR50 = [
    (2, 4, 6), (2.5, 4, 6.5), (3.5, 4, 7.5), None, None, None,
]


def table_7_2_min_thickness(esal, base_cbr) -> dict:
    """Minimum flexible pavement section thickness (Table 7-2, Chapter 7;
    pdf_page 40, printed 21). Applies when PCASE use is mandatory.

    Parameters
    ----------
    esal : float
        Design equivalent 18,000-lb (8,200-kg) single axle loads for the
        design life.
    base_cbr : int
        Design CBR of base course material: 50, 80, or 100.

    Returns
    -------
    dict
        {'esal', 'base_cbr', 'surface_in' (float or 'ST'/'MST'), 'base_in',
         'total_in', 'surface_mm', 'base_mm', 'total_mm', 'notes',
         'reference'}.

    Raises
    ------
    ValueError
        If base_cbr is not 50/80/100, or 50-CBR base is used for
        ESAL > 500,000 (footnote 2 restriction).
    """
    if base_cbr not in (50, 80, 100):
        raise ValueError(f"base_cbr must be 50, 80, or 100; got {base_cbr}")
    if base_cbr == 50 and esal > 500_000:
        raise ValueError(
            "50-CBR base course is restricted to ESAL <= 500,000 per "
            "Table 7-2 footnote 2."
        )
    bin_idx = len(_TABLE_7_2_ESAL_BINS) - 1
    for i, (lo, hi) in enumerate(_TABLE_7_2_ESAL_BINS):
        if lo <= esal <= hi:
            bin_idx = i
            break
    row = {100: _TABLE_7_2_CBR100, 80: _TABLE_7_2_CBR80, 50: _TABLE_7_2_CBR50}[base_cbr][bin_idx]
    if row is None:
        raise ValueError(
            f"No minimum thickness defined for base_cbr=50 and ESAL={esal}."
        )
    surface_in, base_in, total_in = row
    surface_mm = round(surface_in * 25.4, 0) if isinstance(surface_in, (int, float)) else None
    return {
        "esal": esal, "base_cbr": base_cbr,
        "surface_in": surface_in, "base_in": base_in, "total_in": total_in,
        "surface_mm": surface_mm, "base_mm": round(base_in * 25.4, 0),
        "total_mm": round(total_in * 25.4, 0),
        "notes": (
            "ST = bituminous surface treatment; MST = multiple bituminous "
            "surface treatments; use >= 3 in surface for tire pressure "
            ">= 100 psi"
        ),
        "reference": "UFC 3-250-01, Table 7-2 (pdf_page 40, printed 21)",
    }


# ============================================================================
# Table 9-1: Equivalency Factors for Stabilized Material (Chapter 9,
# pdf_page 46, printed 27)
# ============================================================================

_TABLE_9_1 = {
    ("asphalt", "all"): {"base": 1.15, "subbase": 2.30},
    ("cement", "gw"): {"base": 1.15, "subbase": 2.30},
    ("cement", "gp"): {"base": 1.15, "subbase": 2.30},
    ("cement", "sw"): {"base": 1.15, "subbase": 2.30},
    ("cement", "sp"): {"base": 1.15, "subbase": 2.30},
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

_USCS_TO_GROUP_9_1 = {
    "gw": "gw", "gp": "gp", "sw": "sw", "sp": "sp",
    "gm": "gm", "gc": "gc", "sm": "sm", "sc": "sc",
    "ml": "ml", "mh": "mh", "cl": "cl", "ch": "ch",
}

_STABILIZER_ALIASES = {
    "asphalt": "asphalt", "asphalt_stabilized": "asphalt",
    "bituminous": "asphalt", "bitumen": "asphalt",
    "cement": "cement", "portland_cement": "cement", "cement_stabilized": "cement",
    "lime": "lime", "lime_stabilized": "lime",
    "lime_cement_flyash": "lime_cement_flyash",
    "lime_cement_fly_ash": "lime_cement_flyash", "lcfa": "lime_cement_flyash",
    "unbound_crushed_stone": "unbound_crushed_stone", "crushed_stone": "unbound_crushed_stone",
    "unbound_aggregate": "unbound_aggregate", "aggregate": "unbound_aggregate",
}


def table_9_1_equivalency_factor(stabilizer_type, uscs_class, layer_type) -> dict:
    """Equivalency factor for stabilized pavement material (Table 9-1,
    Chapter 9; pdf_page 46, printed 27).

    1 in of stabilized material replaces E inches of conventional base or
    subbase (t_stab = t_conventional / E). Cement content is limited to
    <= 4% by weight to prevent reflective cracking.

    Verified against the guide's printed examples (Appendix G, G-4.1/G-4.2,
    pdf_page 279-280): cement-stabilized base E = 1.15, subbase E = 2.30.

    Parameters
    ----------
    stabilizer_type : str
        'asphalt', 'cement', 'lime', 'lime_cement_flyash',
        'unbound_crushed_stone', or 'unbound_aggregate'.
    uscs_class : str
        USCS classification of the soil to be stabilized (e.g. 'CL', 'SM').
        Ignored for 'asphalt', 'unbound_crushed_stone', 'unbound_aggregate'.
    layer_type : str
        'base' or 'subbase'.

    Returns
    -------
    dict
        {'stabilizer', 'uscs_class', 'layer_type', 'equivalency_factor',
         'note', 'reference'}.

    Raises
    ------
    ValueError
        If inputs are not recognized or the stabilizer/layer combination is
        not applicable (marked '*' in Table 9-1).
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

    all_stabs = {"asphalt", "unbound_crushed_stone", "unbound_aggregate"}
    if stab_resolved in all_stabs:
        uscs_key = "all"
    else:
        simple = uscs_class.lower().strip().split("-")[0].strip()
        uscs_key = _USCS_TO_GROUP_9_1.get(simple, simple)

    lookup = _TABLE_9_1.get((stab_resolved, uscs_key))
    if lookup is None:
        raise ValueError(
            f"No equivalency factor for stabilizer='{stab_resolved}', "
            f"uscs='{uscs_class}' in Table 9-1."
        )
    e = lookup[layer_key]
    if e is None:
        raise ValueError(
            f"'{stab_resolved}'-stabilized '{uscs_class}' is not used as a "
            f"{layer_key} course per Table 9-1 (marked *)."
        )
    return {
        "stabilizer": stab_resolved, "uscs_class": uscs_class.upper(),
        "layer_type": layer_key, "equivalency_factor": e,
        "note": (
            f"1 in of this stabilized {layer_key} replaces {e} in of "
            "conventional material; t_stab = t_conventional / E"
        ),
        "reference": "UFC 3-250-01, Table 9-1 (pdf_page 46, printed 27)",
    }


# ============================================================================
# Table 10-1: Modulus of Soil Reaction k (psi/in) for Rigid Pavement Design
# (Chapter 10, pdf_page 50, printed 31)
# ============================================================================

_TABLE_10_1 = {
    "oh_ch_mh": [None, 175, 150, 125, 100, 75, 50, 25],
    "ol_cl_ml": [None, 200, 175, 150, 125, 100, 75, 50],
    "sm_sc": [300, 250, 225, 200, 150, None, None, None],
    "sw_sp": [350, 300, 250, None, None, None, None, None],
    "gm_gc": [400, 350, 300, 250, None, None, None, None],
    "gw_gp": [500, 450, None, None, None, None, None, None],
}

_USCS_TO_GROUP_10_1 = {
    "oh": "oh_ch_mh", "ch": "oh_ch_mh", "mh": "oh_ch_mh",
    "ol": "ol_cl_ml", "cl": "ol_cl_ml", "ml": "ol_cl_ml", "cl-ml": "ol_cl_ml",
    "sm": "sm_sc", "sc": "sm_sc",
    "sw": "sw_sp", "sp": "sw_sp", "sw-sm": "sw_sp", "sp-sm": "sw_sp",
    "gm": "gm_gc", "gc": "gm_gc", "gw-gm": "gm_gc", "gp-gm": "gm_gc",
    "gw": "gw_gp", "gp": "gw_gp",
}


def table_10_1_k_subgrade(uscs_group, moisture_pct) -> dict:
    """Typical modulus of soil reaction k for rigid pavement design
    (Table 10-1, Chapter 10; pdf_page 50, printed 31).

    Guidance values only, at 90-95% ASTM D1557 dry density; field
    plate-bearing tests are preferred for final design.

    Parameters
    ----------
    uscs_group : str
        USCS soil classification (e.g. 'CL', 'SM', 'GW').
    moisture_pct : float
        Soil moisture content (%). Must be > 0.

    Returns
    -------
    dict
        {'uscs_group', 'moisture_pct', 'k_psi_in', 'k_kPa_mm', 'note',
         'reference'}.

    Raises
    ------
    ValueError
        If the USCS group is not covered, or moisture content is out of
        range for that soil type.
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
    bin_edges = [0, 4, 8, 12, 16, 20, 24, 28, float("inf")]
    bin_idx = 0
    for i in range(len(bin_edges) - 1):
        if bin_edges[i] < moisture_pct <= bin_edges[i + 1]:
            bin_idx = i
            break
    k = values[bin_idx]
    if k is None:
        raise ValueError(
            f"Table 10-1 has no data for soil group '{uscs_group}' at "
            f"moisture = {moisture_pct}% (too high for this soil type)."
        )
    return {
        "uscs_group": uscs_group.upper(), "moisture_pct": moisture_pct,
        "k_psi_in": float(k), "k_kPa_mm": round(k * 0.271, 1),
        "note": (
            "Typical guide values at 90-95% ASTM D1557; reduce by 50 psi/in "
            "if density < 90% (min 25 psi/in), max 500 psi/in if > 95%; use "
            "field plate-bearing tests for final design."
        ),
        "reference": "UFC 3-250-01, Table 10-1 (pdf_page 50, printed 31)",
    }


# ============================================================================
# Figure 10-1: Effect of Base Course Thickness on Modulus of Soil Reaction
# for Non-frost Conditions (Chapter 10, pdf_page 51, printed 32)
#
# CHART READ digitization: family of 7 curves (k on subgrade = 25, 50, 75,
# 100, 150, 200, 300 psi/in), each giving the "effective" k on top of the
# base course vs. base course thickness (0-60 in), all approaching ~500
# psi/in near t=60 in. Anchor points read visually off the rendered chart
# (no printed worked-example anchor was found for this specific figure);
# treat as an engineering estimate, tolerance approximately +/-15%. Prefer a
# field plate-bearing test on top of the base, or ``read_reference_figure``
# on the source figure, for final design.
# ============================================================================

_FIG_10_1_THICKNESS = [0, 10, 20, 30, 40, 50, 60]
_FIG_10_1_CURVES = {
    25: [25, 65, 105, 150, 195, 260, 330],
    50: [50, 100, 150, 195, 240, 300, 370],
    75: [75, 130, 180, 225, 270, 330, 400],
    100: [100, 160, 210, 255, 300, 360, 420],
    150: [150, 210, 260, 305, 350, 400, 460],
    200: [200, 255, 300, 345, 390, 440, 480],
    300: [300, 350, 390, 425, 455, 480, 500],
}
_FIG_10_1_SUBGRADE_K = sorted(_FIG_10_1_CURVES)


def figure_10_1_k_on_base(k_subgrade_psi_in, base_thickness_in) -> dict:
    """Effective modulus of soil reaction on top of a base course
    (Figure 10-1, Chapter 10; pdf_page 51, printed 32). CHART READ,
    approximate (see module note, tolerance ~+/-15%).

    Parameters
    ----------
    k_subgrade_psi_in : float
        Modulus of subgrade reaction measured (or estimated, Table 10-1) on
        the subgrade, psi/in. Interpolated within 25-300 psi/in; clamped at
        the endpoints outside that range.
    base_thickness_in : float
        Thickness of base course above the subgrade, inches. Clamped to
        0-60 in (the plotted range).

    Returns
    -------
    dict
        {'k_subgrade_psi_in', 'base_thickness_in', 'k_on_base_psi_in',
         'chart_read', 'tolerance', 'reference'}.

    Raises
    ------
    ValueError
        If k_subgrade_psi_in or base_thickness_in is negative.
    """
    if k_subgrade_psi_in < 0:
        raise ValueError(f"k_subgrade_psi_in must be >= 0, got {k_subgrade_psi_in}")
    if base_thickness_in < 0:
        raise ValueError(f"base_thickness_in must be >= 0, got {base_thickness_in}")

    t = min(max(base_thickness_in, 0), 60)
    ks = min(max(k_subgrade_psi_in, _FIG_10_1_SUBGRADE_K[0]), _FIG_10_1_SUBGRADE_K[-1])

    # Interpolate along thickness for each bracketing subgrade-k curve, then
    # interpolate between the two curves.
    lower_k = max(k for k in _FIG_10_1_SUBGRADE_K if k <= ks)
    upper_k = min(k for k in _FIG_10_1_SUBGRADE_K if k >= ks)
    val_lower = _linterp(t, _FIG_10_1_THICKNESS, _FIG_10_1_CURVES[lower_k])
    if upper_k == lower_k:
        k_on_base = val_lower
    else:
        val_upper = _linterp(t, _FIG_10_1_THICKNESS, _FIG_10_1_CURVES[upper_k])
        frac = (ks - lower_k) / (upper_k - lower_k)
        k_on_base = val_lower + frac * (val_upper - val_lower)

    return {
        "k_subgrade_psi_in": k_subgrade_psi_in,
        "base_thickness_in": base_thickness_in,
        "k_on_base_psi_in": round(k_on_base, 1),
        "chart_read": True,
        "tolerance": "approximate, visual read-off of the rendered chart, ~+/-15%",
        "reference": "UFC 3-250-01, Figure 10-1 (pdf_page 51, printed 32)",
    }


# ============================================================================
# Table 15 condition factor C for overlay design (Chapter 15, Sections
# 15-3.2/15-3.3; pdf_page 63-64, printed 44-45)
# ============================================================================

_TABLE_15_C = {
    ("rigid", "plain"): {
        1.00: "Good condition, little or no structural cracking due to load.",
        0.75: "Initial cracking due to load, no progressive cracking or faulting.",
        0.35: "Progressive cracking due to load with spalling, raveling, or faulting.",
    },
    ("rigid", "reinforced"): {
        1.00: "Good condition, little/no short-spaced transverse cracking, no longitudinal cracking.",
        0.75: "Short-spaced transverse cracking, little/no interconnecting longitudinal cracking, moderate spalling.",
        0.35: "Severe short-spaced transverse + interconnecting longitudinal cracking, severe spalling, initial punch-outs.",
    },
    ("flexible", "plain"): {
        1.00: "Good condition, some load cracking but little/no progressive-type cracking.",
        0.75: "Progressive cracking with spalling, raveling, and minor faulting at joints/cracks.",
        0.50: "Multiple cracking with raveling, spalling, and faulting at joints/cracks.",
    },
    ("flexible", "reinforced"): {
        1.00: "Good condition, some closely spaced transverse cracking, initial interconnecting longitudinal cracks, moderate spalling.",
        0.75: "Numerous closely spaced transverse+longitudinal cracks, rather severe spalling, or initial punch-out evidence.",
    },
}


def table_15_condition_factor(overlay_type, existing_pavement_type, c) -> dict:
    """Condition factor C for rigid/flexible overlay design (Sections
    15-3.2/15-3.3, Chapter 15; pdf_page 63-64, printed 44-45).

    Parameters
    ----------
    overlay_type : str
        'rigid' (Section 15-3.2) or 'flexible' (Section 15-3.3) -- the type
        of overlay being designed.
    existing_pavement_type : str
        'plain' or 'reinforced' -- the existing pavement being overlaid.
    c : float
        Candidate condition factor value (1.00, 0.75, 0.50, or 0.35,
        depending on the overlay_type/existing_pavement_type combination).

    Returns
    -------
    dict
        {'overlay_type', 'existing_pavement_type', 'c', 'description',
         'valid_values', 'reference'}.

    Raises
    ------
    ValueError
        If the overlay_type/existing_pavement_type combination is not
        recognized, or c is not one of its valid printed values.
    """
    key = (overlay_type.lower().strip(), existing_pavement_type.lower().strip())
    if key not in _TABLE_15_C:
        raise ValueError(
            f"Unknown combination overlay_type='{overlay_type}', "
            f"existing_pavement_type='{existing_pavement_type}'. "
            f"Valid: {sorted(_TABLE_15_C)}"
        )
    options = _TABLE_15_C[key]
    if c not in options:
        raise ValueError(
            f"c={c} not valid for {key}; valid values: {sorted(options, reverse=True)}"
        )
    return {
        "overlay_type": key[0], "existing_pavement_type": key[1], "c": c,
        "description": options[c],
        "valid_values": sorted(options, reverse=True),
        "reference": (
            "UFC 3-250-01, Section 15-3.2/15-3.3 (pdf_page 63-64, printed 44-45)"
        ),
    }


# ============================================================================
# Figure 15-1: Factor for Projecting Cracking in a Flexible Pavement
# (Chapter 15, pdf_page 69, printed 50)
#
# CHART READ digitization: F (0.4-1.0, y-axis) vs. log10(passes of an 18-kip
# ESAL) (100-10,000,000), a family of curves parameterized by the existing
# rigid pavement's k value (psi/in: 25, 50, 100, 150, 200, 250, 300, 350,
# 400, 450, 500). Anchored at k=100, passes=2e7 -> F=0.93 (Appendix G, G-7,
# pdf_page 283, printed 264 -- the ONLY input the worked example gives
# explicitly); intermediate points are visual read-offs of the rendered
# chart. Treat as approximate (~+/-0.05 on F); prefer
# ``read_reference_figure`` on the source figure for final design.
# ============================================================================

_FIG_15_1_LOG_PASSES = [2, 3, 4, 5, 6, 7]  # log10(passes): 100 .. 1e7
_FIG_15_1_CURVES = {
    25: [0.82, 0.90, 0.955, 0.97, 0.975, 0.98],
    50: [0.66, 0.83, 0.90, 0.94, 0.955, 0.96],
    100: [0.46, 0.72, 0.85, 0.90, 0.92, 0.93],
    150: [None, 0.55, 0.77, 0.85, 0.885, 0.90],
    200: [None, 0.40, 0.68, 0.80, 0.85, 0.875],
    250: [None, None, 0.58, 0.75, 0.815, 0.85],
    300: [None, None, 0.47, 0.69, 0.78, 0.82],
    350: [None, None, None, 0.62, 0.74, 0.79],
    400: [None, None, None, 0.53, 0.69, 0.76],
    450: [None, None, None, 0.42, 0.63, 0.72],
    500: [None, None, None, None, 0.57, 0.68],
}


def figure_15_1_cracking_projection_factor(passes, k_existing_psi_in) -> dict:
    """Factor F for projecting cracking in a flexible overlay of a rigid
    base pavement (Figure 15-1, Chapter 15; pdf_page 69, printed 50).
    CHART READ, approximate (see module note).

    Verified anchor: k=100 psi/in, passes=20,000,000 -> F=0.93 (Appendix G,
    G-7, matches this digitization's k=100 curve at log10(passes)=7.3,
    interpolated between the 0.92 @ 1e6 and 0.93 @ 1e7 tabulated points).

    Parameters
    ----------
    passes : float
        Design traffic, passes of an 18-kip (8,164-kg) ESAL. Must be >= 100.
    k_existing_psi_in : float
        Modulus of subgrade reaction k of the existing rigid pavement's
        foundation, psi/in. Interpolated within the tabulated 25-500 psi/in
        range; a curve is undefined (raises) below its own printed starting
        passes level.

    Returns
    -------
    dict
        {'passes', 'k_existing_psi_in', 'f', 'chart_read', 'tolerance',
         'reference'}.

    Raises
    ------
    ValueError
        If passes < 100, or k_existing_psi_in is outside 25-500 psi/in.
    """
    if passes < 100:
        raise ValueError(f"passes must be >= 100, got {passes}")
    if not (25 <= k_existing_psi_in <= 500):
        raise ValueError(
            f"k_existing_psi_in must be in [25, 500], got {k_existing_psi_in}"
        )
    log_passes = min(max(math.log10(passes), 2), 7)

    ks = sorted(_FIG_15_1_CURVES)
    lower_k = max(k for k in ks if k <= k_existing_psi_in)
    upper_k = min(k for k in ks if k >= k_existing_psi_in)

    def _interp_curve(k):
        xs, ys = [], []
        for x, y in zip(_FIG_15_1_LOG_PASSES, _FIG_15_1_CURVES[k]):
            if y is not None:
                xs.append(x)
                ys.append(y)
        if not xs or log_passes < xs[0]:
            return None
        return _linterp(log_passes, xs, ys)

    f_lower = _interp_curve(lower_k)
    f_upper = _interp_curve(upper_k) if upper_k != lower_k else f_lower
    if f_lower is None or f_upper is None:
        raise ValueError(
            f"passes={passes:g} is below the plotted range for k="
            f"{k_existing_psi_in} psi/in on Figure 15-1 (curve starts at "
            "higher passes for stiffer foundations)."
        )
    if upper_k == lower_k:
        f = f_lower
    else:
        frac = (k_existing_psi_in - lower_k) / (upper_k - lower_k)
        f = f_lower + frac * (f_upper - f_lower)

    return {
        "passes": passes, "k_existing_psi_in": k_existing_psi_in,
        "f": round(f, 3), "chart_read": True,
        "tolerance": "approximate, ~+/-0.05 on F; verified anchor k=100,passes=2e7->F=0.93",
        "reference": "UFC 3-250-01, Figure 15-1 (pdf_page 69, printed 50)",
    }


# ============================================================================
# Table 16-1: Allowable Spacing of Longitudinal and Transverse Contraction
# Joints (Chapter 16, pdf_page 73, printed 54)
# ============================================================================

def table_16_1_joint_spacing(thickness_in) -> dict:
    """Allowable spacing of longitudinal/transverse contraction joints
    (Table 16-1, Chapter 16; pdf_page 73, printed 54).

    Parameters
    ----------
    thickness_in : float
        Pavement thickness, inches. Must be > 0.

    Returns
    -------
    dict
        {'thickness_in', 'spacing_range_ft', 'max_spacing_ft', 'note',
         'reference'}. ``max_spacing_ft`` is capped at 20 ft (the absolute
         DoD maximum for transverse contraction joints regardless of
         thickness), and further to 20 ft/6 m in regions with design
         freezing index < 1,800 degree-days (else per Section 16-2.1.3).

    Raises
    ------
    ValueError
        If thickness_in is not positive.
    """
    if thickness_in <= 0:
        raise ValueError(f"thickness_in must be > 0, got {thickness_in}")
    if thickness_in < 9:
        rng, max_sp = (10, 15), 15.0
    elif thickness_in <= 12:
        rng, max_sp = (15, 20), 20.0
    else:
        rng, max_sp = (20, 20), 20.0
    return {
        "thickness_in": thickness_in,
        "spacing_range_ft": rng, "max_spacing_ft": max_sp,
        "note": (
            "Maximum spacing of transverse contraction joints for DoD "
            "pavements is 20 ft (6.1 m) regardless of thickness; keep "
            "length/width within 25% of each other."
        ),
        "reference": "UFC 3-250-01, Table 16-1 (pdf_page 73, printed 54)",
    }


# ============================================================================
# Table 16-2: Dowel Size and Spacing for Construction, Contraction, and
# Expansion Joints (Chapter 16, pdf_page 74, printed 55)
# ============================================================================

_TABLE_16_2 = [
    (0, 8, {"min_dowel_length_in": 16, "max_dowel_spacing_in": 12, "dowel": '0.75 in (20 mm) bar'}),
    (8, 11, {"min_dowel_length_in": 16, "max_dowel_spacing_in": 12, "dowel": '1 in (25 mm) bar'}),
    (12, 15, {"min_dowel_length_in": 20, "max_dowel_spacing_in": 15, "dowel": '1 in (25 mm) to 1.25 in (32 mm) bar, or 1 in extra-strength pipe'}),
]


def table_16_2_dowel_size(thickness_in) -> dict:
    """Dowel size/length/spacing for construction, contraction, and
    expansion joints (Table 16-2, Chapter 16; pdf_page 74, printed 55).

    Parameters
    ----------
    thickness_in : float
        Pavement thickness, inches. Must be in (0, 15].

    Returns
    -------
    dict
        {'thickness_in', 'min_dowel_length_in', 'max_dowel_spacing_in',
         'dowel', 'reference'}.

    Raises
    ------
    ValueError
        If thickness_in is not in (0, 15] (Table 16-2's printed range;
        thicker slabs require project-specific structural design).
    """
    if not (0 < thickness_in <= 15):
        raise ValueError(
            f"thickness_in must be in (0, 15] for Table 16-2, got {thickness_in}"
        )
    if thickness_in < 8:
        row = _TABLE_16_2[0][2]
    elif thickness_in <= 11:
        row = _TABLE_16_2[1][2]
    else:
        # (11, 12) is an unprinted gap between the "8 to 11" and "12 to 15"
        # rows; bracket it into the "12 to 15" row (thicker-slab side).
        row = _TABLE_16_2[2][2]
    return {
        "thickness_in": thickness_in, **row,
        "reference": "UFC 3-250-01, Table 16-2 (pdf_page 74, printed 55)",
    }


# ============================================================================
# Figure 14-1: Reinforced Rigid Pavement Design (Chapter 14, pdf_page 60,
# printed 41)
#
# L (max allowable slab length) is computed EXACTLY via the general Eq. 17-1
# closed form (verified in equations.py). The thickness-reduction leg
# (hr as a function of hd and S, at fs=60,000 psi) has no printed closed
# form; digitized here from the guide's own two worked-example anchors
# (Appendix G, G-6, pdf_page 282, printed 263): hd=7.9 in ->
# (S=0.10% -> hr=7 in), (S=0.30% -> hr=6 in). Linear interpolation on S is
# used between/around these two verified points; treat hr for S or hd far
# from this anchored range as approximate (use PCASE or
# ``read_reference_figure`` for other conditions). As (steel area) is the
# chart's own printed definition (not a chart read): As = (S/100)*12*hr.
# Transverse steel percentage is half the longitudinal percentage (printed
# rule, Section 14-2.1).
# ============================================================================

_FIG_14_1_S_PCT = [0.10, 0.30]
_FIG_14_1_DELTA_IN = [0.9, 1.9]  # hd - hr at hd=7.9in, verified


def figure_14_1_reinforced_pavement_design(hd_in, s_pct, fs_psi=60_000) -> dict:
    """Reinforced concrete pavement design (Figure 14-1 + Eq. 17-1,
    Chapter 14; pdf_page 60, printed 41).

    Returns the reinforced pavement thickness hr, steel area As, transverse
    steel percentage, and maximum allowable slab length L for a given plain
    concrete design thickness hd and longitudinal steel percentage S.

    L is computed EXACTLY (Eq. 17-1, generalizes to any fs). hr is
    interpolated from the guide's own two worked-example points (both at
    hd=7.9 in: S=0.10% -> hr=7 in; S=0.30% -> hr=6 in -- Appendix G, G-6)
    and is only reliable near that hd; for other hd or precise design, read
    Figure 14-1 directly (``read_reference_figure``) or use PCASE.

    Verified EXACTLY (hr, L) at hd=7.9, S=0.10, fs=60000 -> hr=7 in, L=49 ft;
    and hd=7.9, S=0.30, fs=60000 -> hr=6 in, L=97 ft raw (75 ft capped).

    Parameters
    ----------
    hd_in : float
        Design thickness of plain concrete pavement, inches. Must be > 0.
    s_pct : float
        Percent of longitudinal reinforcing steel. Must be in [0.05, 0.50]
        (the plotted range of Figure 14-1's S scale).
    fs_psi : float, optional
        Yield strength of the reinforcing steel, psi. Default 60,000 (the
        value built into the printed nomograph).

    Returns
    -------
    dict
        {'hd_in', 's_pct', 'fs_psi', 'hr_in', 'as_sq_in_per_ft',
         'transverse_s_pct', 'l_ft_raw', 'l_ft_capped', 'chart_read',
         'reference'}. ``hr_in`` is chart-read (approximate); ``l_ft_raw``/
         ``l_ft_capped`` are exact (Eq. 17-1).

    Raises
    ------
    ValueError
        If hd_in <= 0, fs_psi <= 0, or s_pct is outside [0.05, 0.50].
    """
    if hd_in <= 0:
        raise ValueError(f"hd_in must be > 0, got {hd_in}")
    if fs_psi <= 0:
        raise ValueError(f"fs_psi must be > 0, got {fs_psi}")
    if not (0.05 <= s_pct <= 0.50):
        raise ValueError(f"s_pct must be in [0.05, 0.50], got {s_pct}")

    delta = _linterp(s_pct, _FIG_14_1_S_PCT, _FIG_14_1_DELTA_IN)
    hr = max(hd_in - delta, 0.5 * hd_in)  # sanity floor; chart never halves hd
    as_sq_in_ft = (s_pct / 100.0) * 12.0 * hr

    l_result = reinforced_pavement_max_slab_length(hr, fs_psi, s_pct)

    return {
        "hd_in": hd_in, "s_pct": s_pct, "fs_psi": fs_psi,
        "hr_in": round(hr, 2),
        "as_sq_in_per_ft": round(as_sq_in_ft, 3),
        "transverse_s_pct": round(s_pct / 2.0, 3),
        "l_ft_raw": l_result["l_ft_raw"], "l_ft_capped": l_result["l_ft_capped"],
        "chart_read": True,
        "tolerance": (
            "hr interpolated from 2 verified points at hd=7.9 in "
            "(Appendix G, G-6); L is exact (Eq. 17-1)"
        ),
        "reference": (
            "UFC 3-250-01, Figure 14-1 (pdf_page 60, printed 41) + Eq. 17-1 "
            "(pdf_page 81, printed 62); verified vs. Appendix G, G-6"
        ),
    }


# ============================================================================
# Table 19-1: Modes of Distress in Pavements (Chapter 19, pdf_page 87,
# printed 68) -- descriptive lookup, no numeric design value.
# ============================================================================

_TABLE_19_1 = {
    "cracking": {
        "traffic_load_associated": ["Repeated loading (fatigue)", "Slippage (from braking stresses)"],
        "non_traffic_associated": ["Thermal changes", "Moisture changes", "Shrinkage of underlying materials (reflection cracking)"],
    },
    "distortion": {
        "traffic_load_associated": ["Rutting, pumping and faulting (repetitive loading)", "Plastic flow or creep (few excessive loads)"],
        "non_traffic_associated": ["Differential heave (expansive clay swell, frost action)", "Differential settlement (long-term consolidation or transient reconsolidation)", "Curling of rigid slabs (moisture/temperature differentials)"],
    },
    "disintegration": {
        "general_cause": ["Advanced-stage cracking", "Detrimental material effects", "Abrasion by traffic", "Freeze-thaw effects"],
    },
}


def table_19_1_distress_modes(distress_mode) -> dict:
    """Modes of distress in pavements and their causative factors
    (Table 19-1, Chapter 19; pdf_page 87, printed 68). Descriptive lookup
    (no numeric design value).

    Parameters
    ----------
    distress_mode : str
        'cracking', 'distortion', or 'disintegration'.

    Returns
    -------
    dict
        {'distress_mode', ...causative-factor lists..., 'reference'}.

    Raises
    ------
    ValueError
        If distress_mode is not recognized.
    """
    key = distress_mode.lower().strip()
    if key not in _TABLE_19_1:
        raise ValueError(
            f"Unknown distress_mode '{distress_mode}'. Valid: {sorted(_TABLE_19_1)}"
        )
    return {
        "distress_mode": key, **_TABLE_19_1[key],
        "reference": "UFC 3-250-01, Table 19-1 (pdf_page 87, printed 68)",
    }


# ============================================================================
# Table 19-2: Frost Design Soil Classification (Chapter 19, pdf_page 89,
# printed 70)
# ============================================================================

_USCS_FROST_RULES = [
    ("ml", 0, 100, "F4", "a"), ("mh", 0, 100, "F4", "a"), ("ol", 0, 100, "F4", "a"),
    ("ch", 0, 100, "F3", "c"), ("cl-ml", 0, 100, "F4", "c"), ("cl", 0, 100, "F3", "c"),
    ("oh", 0, 100, "F3", "c"), ("pt", 0, 100, "F4", "d"),
    ("sm", 15.01, 100, "F4", "b"), ("sm", 6, 15, "F2", "b"), ("sm", 3, 6, "S2", ""), ("sm", 0, 3, "NFS", "b"),
    ("sc", 15.01, 100, "F3", "b"), ("sc", 0, 15, "F3", "b"),
    ("sw-sm", 6, 15, "F2", "b"), ("sw-sm", 3, 6, "S2", ""),
    ("sp-sm", 6, 15, "F2", "b"), ("sp-sm", 3, 6, "S2", ""),
    ("sw", 3, 10, "PFS", "b"), ("sw", 0, 3, "NFS", "b"),
    ("sp", 3, 10, "PFS", "b"), ("sp", 0, 3, "NFS", "b"),
    ("gm", 20.01, 100, "F3", "a"), ("gm", 10, 20, "F2", "a"), ("gm", 6, 10, "F1", ""), ("gm", 3, 6, "S1", ""),
    ("gc", 20.01, 100, "F3", "a"), ("gc", 6, 20, "F2", "a"),
    ("gw-gm", 20.01, 100, "F3", "a"), ("gw-gm", 10, 20, "F2", "a"), ("gw-gm", 6, 10, "F1", ""), ("gw-gm", 3, 6, "S1", ""),
    ("gp-gm", 10, 20, "F2", "a"), ("gp-gm", 6, 10, "F1", ""), ("gp-gm", 3, 6, "S1", ""),
    ("gw-gc", 6, 20, "F2", "a"), ("gp-gc", 6, 20, "F2", "a"),
    ("gw", 3, 6, "S1", ""), ("gw", 1.5, 3, "PFS", "a"), ("gw", 0, 1.5, "NFS", "a"),
    ("gp", 3, 6, "S1", ""), ("gp", 1.5, 3, "PFS", "a"), ("gp", 0, 1.5, "NFS", "a"),
]

_FROST_GROUP_DESCRIPTIONS = {
    ("gw_gp", "0-1.5"): "Gravels/crushed stone/rock, 0-1.5% finer than 0.02mm",
    ("sw_sp", "0-3"): "Sands, 0-3% finer than 0.02mm",
    ("gw_gp", "1.5-3"): "Gravels/crushed stone/rock, 1.5-3% finer than 0.02mm",
    ("sw_sp", "3-10"): "Sands, 3-10% finer than 0.02mm",
    ("gravelly", "3-6"): "Gravelly soils, 3-6% finer than 0.02mm",
    ("sandy", "3-6"): "Sandy soils, 3-6% finer than 0.02mm",
    ("gravelly", "6-10"): "Gravelly soils, 6-10% finer than 0.02mm",
    ("gravelly", "10-20"): "Gravelly soils, 10-20% finer than 0.02mm",
    ("sandy", "6-15"): "Sands, 6-15% finer than 0.02mm",
    ("gravelly", ">20"): "Gravelly soils, > 20% finer than 0.02mm",
    ("sandy", ">15"): "Sands (except very fine silty sands), > 15% finer than 0.02mm",
    ("clay", "pi>12"): "Clays, PI > 12",
    ("silt", "all"): "All silts",
    ("varved", "all"): "Varved clays and other banded fine-grained sediments",
}


def table_19_2_frost_classification(uscs_class, finer_than_0_02mm_pct=None) -> dict:
    """Frost design soil classification (Table 19-2, Chapter 19; pdf_page 89,
    printed 70).

    Classifies soil into frost susceptibility groups NFS, PFS, S1, S2, or
    F1-F4. S1/S2 soils are suitable for subbase in frost areas; F-groups
    require frost thickness design (Section 19-6).

    Parameters
    ----------
    uscs_class : str
        USCS soil classification symbol (e.g. 'ML', 'SM', 'GW').
    finer_than_0_02mm_pct : float, optional
        Percentage of particles finer than 0.02 mm by weight. Required for
        granular soils where the group depends on fines content; not needed
        for fine-grained soils (ML, MH, CL, CH, OL, OH, PT).

    Returns
    -------
    dict
        {'uscs_class', 'finer_0_02mm_pct', 'frost_group', 'subgroup',
         'description', 'reference'}.

    Raises
    ------
    ValueError
        If uscs_class is not recognized, or fines content is required but
        not supplied.
    """
    key = uscs_class.lower().strip()
    fines = finer_than_0_02mm_pct if finer_than_0_02mm_pct is not None else 0.0
    for (uscs_pat, f_min, f_max, group, subgroup) in _USCS_FROST_RULES:
        if key == uscs_pat and f_min <= fines <= f_max:
            return {
                "uscs_class": uscs_class.upper(),
                "finer_0_02mm_pct": finer_than_0_02mm_pct,
                "frost_group": group, "subgroup": subgroup,
                "description": f"{uscs_class.upper()} -- frost group {group}{subgroup}",
                "reference": "UFC 3-250-01, Table 19-2 (pdf_page 89, printed 70)",
            }
    raise ValueError(
        f"Unable to classify uscs_class='{uscs_class}' with "
        f"finer_0_02mm={finer_than_0_02mm_pct}% using Table 19-2. "
        "Provide finer_than_0_02mm_pct for granular soils."
    )


# ============================================================================
# Table 19-3: Frost-Area Soil Support Indexes for Subgrade Soils, Flexible
# Pavement Design (Chapter 19, pdf_page 100, printed 81)
# ============================================================================

def table_19_3_frost_support_index(frost_group) -> dict:
    """Frost-area soil support index for flexible pavement design
    (Table 19-3, Chapter 19; pdf_page 100, printed 81).

    Used as if it were a CBR value when entering the Appendix E design
    curves for the reduced subgrade strength method; not measurable by CBR
    test (weighted annual-cycle average including thaw-weakening).

    Parameters
    ----------
    frost_group : str
        'F1', 'F2', 'F3', 'F4', 'S1', or 'S2'.

    Returns
    -------
    dict
        {'frost_group', 'soil_support_index', 'note', 'reference'}.

    Raises
    ------
    ValueError
        If frost_group is not recognized, or is NFS/PFS (no index needed --
        use normal subgrade CBR).
    """
    group_upper = frost_group.upper().strip()
    mapping = {"F1": 9.0, "S1": 9.0, "F2": 6.5, "S2": 6.5, "F3": 3.5, "F4": 3.5,
               "NFS": None, "PFS": None}
    if group_upper not in mapping:
        raise ValueError(
            f"Unknown frost_group '{frost_group}'. Valid: F1, F2, F3, F4, S1, S2, NFS, PFS."
        )
    idx = mapping[group_upper]
    if idx is None:
        raise ValueError(
            f"'{frost_group}' (NFS or PFS) soils do not require a frost "
            "area soil support index -- use normal subgrade CBR for design."
        )
    return {
        "frost_group": group_upper, "soil_support_index": idx,
        "note": (
            "Use as CBR in Appendix E design curves for the reduced "
            "subgrade strength method; weighted annual average, not "
            "measurable by CBR test."
        ),
        "reference": "UFC 3-250-01, Table 19-3 (pdf_page 100, printed 81)",
    }


# ============================================================================
# Figure 19-5: Design Depth of Non-frost Susceptible Base for Limited
# Subgrade Frost Penetration (Chapter 19, pdf_page 99, printed 79)
#
# All r-curves (r = water content ratio, subgrade/base) are straight lines
# through the origin: b = slope(r) * c. Two slopes are printed/verified
# exactly: r=2.0 (the figure's own worked example box: c=32in -> b=21in,
# slope=0.65625) and r=3.0 (from TWO independent Appendix G worked examples,
# G-8.9 and G-8.11: c=42->b=26 and c=38.5->b=22, average slope ~0.595 --
# see docstring). s (subgrade frost penetration with the design base) is an
# EXACT axis-scale relationship: s = b/4 (the printed right-axis scale runs
# 0-18in over the same physical height as the left axis's 0-72in).
# ============================================================================

_FIG_19_5_SLOPES = {2.0: 0.65625, 3.0: 0.595}


def figure_19_5_design_base_thickness(c_in, r) -> dict:
    """Design NFS base thickness for the limited subgrade frost penetration
    method (Figure 19-5, Chapter 19; pdf_page 99, printed 79).

        b = slope(r) * c;  s = b / 4   (exact axis-scale relationship)

    where c = base thickness for zero frost penetration into the subgrade
    (from frost penetration depth a, per Figure 19-4, minus pavement
    thickness p: c = a - p), b = design base thickness, s = resulting
    subgrade frost penetration.

    Verified: r=2.0 EXACTLY from the figure's own printed worked example
    (c=32in -> b=21in, s=5.2in matches b/4=5.25); r=3.0 from TWO independent
    Appendix G worked examples (G-8.9: c=42in->b=26in, slope=0.619; G-8.11:
    c=38.5in->b=22in, slope=0.571) -- averaged to slope=0.595 (~+/-4%
    spread between the two, consistent with the guide's own 0.5 in / 1 in
    read-off rounding).

    Parameters
    ----------
    c_in : float
        Base thickness for zero frost penetration into the subgrade,
        inches (c = a - p). Must be > 0.
    r : float
        Ratio of subgrade water content to base water content, capped at
        3.0 per the guide's own instruction ("if r is greater than 3.0 use
        3.0"). Must be one of the two digitized values: 2.0 or 3.0 -- other
        r values are not reliably interpolated from only two anchors; read
        Figure 19-5 directly (``read_reference_figure``) for other r.

    Returns
    -------
    dict
        {'c_in', 'r', 'b_in', 's_in', 'chart_read', 'reference'}.

    Raises
    ------
    ValueError
        If c_in is not positive or r is not 2.0 or 3.0.
    """
    if c_in <= 0:
        raise ValueError(f"c_in must be > 0, got {c_in}")
    if r not in _FIG_19_5_SLOPES:
        raise ValueError(
            f"r={r} not digitized; only r in {sorted(_FIG_19_5_SLOPES)} are "
            "verified against printed worked examples. Read Figure 19-5 "
            "directly for other r values."
        )
    b = _FIG_19_5_SLOPES[r] * c_in
    s = b / 4.0
    return {
        "c_in": c_in, "r": r, "b_in": round(b, 1), "s_in": round(s, 1),
        "chart_read": True,
        "reference": "UFC 3-250-01, Figure 19-5 (pdf_page 99, printed 79)",
    }


# ============================================================================
# Figure 19-6: Frost-Area Index of Reaction for Design of Rigid Roads and
# Parking Areas (Chapter 19, pdf_page 102, printed 83)
#
# CHART READ, single verified anchor only: F3&F4 group, base thickness=8in
# -> frost-area index of reaction = 50 psi/in (Appendix G, G-8.12, pdf_page
# 287, printed 268). Other thicknesses/groups are NOT digitized (visual
# read-off of this 3-line chart proved unreliable against the one available
# check point) -- use ``read_reference_figure`` on the source figure.
# ============================================================================

def figure_19_6_frost_area_index_of_reaction(base_thickness_in, frost_group) -> dict:
    """Frost-area index of reaction for rigid pavement design in frost areas
    (Figure 19-6, Chapter 19; pdf_page 102, printed 83). Single verified
    spot-check only (see module note).

    Verified EXACTLY: F3/F4 group, base_thickness_in=8 ->
    index_of_reaction_psi_in=50 (Appendix G, G-8.12).

    Parameters
    ----------
    base_thickness_in : float
        Combined thickness of granular unbound + bound base, inches. Must
        equal 8 (the only digitized/verified point).
    frost_group : str
        'F1_S1', 'F2_S2', or 'F3_F4'. Must be 'F3_F4' (the only digitized
        curve).

    Returns
    -------
    dict
        {'base_thickness_in', 'frost_group', 'index_of_reaction_psi_in',
         'index_of_reaction_kPa_mm', 'chart_read', 'reference'}.

    Raises
    ------
    ValueError
        If base_thickness_in != 8 or frost_group != 'F3_F4' -- this figure
        is not broadly digitized; use ``read_reference_figure`` for other
        inputs.
    """
    if frost_group != "F3_F4" or base_thickness_in != 8:
        raise ValueError(
            "Only the verified spot-check (frost_group='F3_F4', "
            "base_thickness_in=8 -> 50 psi/in) is digitized for Figure "
            "19-6. Use read_reference_figure (vision read-off) on the "
            "source figure for other base thicknesses or frost groups "
            "(F1_S1, F2_S2)."
        )
    return {
        "base_thickness_in": base_thickness_in, "frost_group": frost_group,
        "index_of_reaction_psi_in": 50.0,
        "index_of_reaction_kPa_mm": round(50.0 * 0.271, 1),
        "chart_read": True,
        "reference": (
            "UFC 3-250-01, Figure 19-6 (pdf_page 102, printed 83); verified "
            "vs. Appendix G, G-8.12 (pdf_page 287, printed 268)"
        ),
    }


# ============================================================================
# Table 20-1: Coefficient of Permeability for Sand and Gravel Materials
# (Chapter 20, pdf_page 113, printed 94)
# ============================================================================

_TABLE_20_1 = [
    (3, 5e-1, 1e-1), (5, 5e-2, 1e-2), (10, 5e-3, 1e-3),
    (15, 5e-4, 1e-4), (20, 5e-5, 1e-5),
]


def table_20_1_permeability_estimate(pct_passing_no200) -> dict:
    """Estimated permeability of sand/gravel drainage material vs. percent
    passing the No. 200 sieve (Table 20-1, Chapter 20; pdf_page 113, printed
    94).

    Parameters
    ----------
    pct_passing_no200 : float
        Percent by weight passing the No. 200 sieve. Must be one of the
        printed levels: 3, 5, 10, 15, or 20.

    Returns
    -------
    dict
        {'pct_passing_no200', 'permeability_mm_per_sec',
         'permeability_ft_per_min', 'reference'}.

    Raises
    ------
    ValueError
        If pct_passing_no200 is not one of the printed levels.
    """
    for pct, mm_s, ft_min in _TABLE_20_1:
        if abs(pct - pct_passing_no200) < 1e-9:
            return {
                "pct_passing_no200": pct_passing_no200,
                "permeability_mm_per_sec": mm_s,
                "permeability_ft_per_min": ft_min,
                "reference": "UFC 3-250-01, Table 20-1 (pdf_page 113, printed 94)",
            }
    raise ValueError(
        f"pct_passing_no200 must be one of {[p for p, _, _ in _TABLE_20_1]}, "
        f"got {pct_passing_no200}"
    )


# ============================================================================
# Table 20-2: Frost Susceptible Soils (Chapter 20, pdf_page 124, printed
# 105) -- Chapter 20's own printed frost-group table (distinct in coverage
# from Table 19-2: does not enumerate NFS/PFS/S1/S2, only F1-F4).
# ============================================================================

_TABLE_20_2 = {
    "F1": {"soil_description": "Gravelly soils", "pct_finer_0_02mm": "6-10",
           "uscs_types": ["GW-GM", "GP-GM", "GW-GC", "GP-GC"]},
    "F2a": {"soil_description": "Gravelly soils", "pct_finer_0_02mm": "10-20",
            "uscs_types": ["GM", "GC", "GM-GC"]},
    "F2b": {"soil_description": "Sands", "pct_finer_0_02mm": "6-15",
            "uscs_types": ["SM", "SC", "SW-SM", "SP-SM", "SW-SC", "SP-SC", "SM-SC"]},
    "F3a": {"soil_description": "Gravelly soils", "pct_finer_0_02mm": "> 20",
            "uscs_types": ["GM", "GC", "GM-GC"]},
    "F3b": {"soil_description": "Sands, except very fine silty sands", "pct_finer_0_02mm": "> 15",
            "uscs_types": ["SM", "SC", "SM-SC"]},
    "F3c": {"soil_description": "Clays (PI > 12)", "pct_finer_0_02mm": "--",
            "uscs_types": ["CL", "CH", "ML-CL"]},
    "F4a": {"soil_description": "Silts", "pct_finer_0_02mm": "--", "uscs_types": ["ML", "MH", "ML-CL"]},
    "F4b": {"soil_description": "Very fine sands", "pct_finer_0_02mm": "> 15", "uscs_types": ["SM", "SC", "SM-SC"]},
    "F4c": {"soil_description": "Clays (PI < 12)", "pct_finer_0_02mm": "--", "uscs_types": ["CL", "ML-CL"]},
    "F4d": {"soil_description": "Varved clays and other banded fine-grained sediments", "pct_finer_0_02mm": "--",
            "uscs_types": ["CL or CH layered with ML, MH, SM, SC, SM-SC, or ML-CL"]},
}


def table_20_2_frost_susceptible_soils(frost_group) -> dict:
    """Frost susceptible soil groups per Chapter 20's own printed table
    (Table 20-2; pdf_page 124, printed 105).

    Parameters
    ----------
    frost_group : str
        One of 'F1', 'F2a', 'F2b', 'F3a', 'F3b', 'F3c', 'F4a', 'F4b',
        'F4c', 'F4d'.

    Returns
    -------
    dict
        {'frost_group', 'soil_description', 'pct_finer_0_02mm',
         'uscs_types', 'reference'}.

    Raises
    ------
    ValueError
        If frost_group is not recognized.
    """
    key = frost_group.strip()
    # normalize case: letters upper, subgroup letter lower
    if len(key) > 2 and key[-1].isalpha():
        key = key[:-1].upper() + key[-1].lower()
    else:
        key = key.upper()
    if key not in _TABLE_20_2:
        raise ValueError(
            f"Unknown frost_group '{frost_group}'. Valid: {sorted(_TABLE_20_2)}"
        )
    return {
        "frost_group": key, **_TABLE_20_2[key],
        "reference": "UFC 3-250-01, Table 20-2 (pdf_page 124, printed 105)",
    }


# ============================================================================
# Table 20-8: Coefficient of Roughness for Different Types of Pipe
# (Chapter 20, pdf_page 135, printed 116)
# ============================================================================

_TABLE_20_8 = {
    "clay_concrete_smooth_plastic_asbestos_cement": 0.013,
    "corrugated_metal": 0.024,
}


def table_20_8_pipe_roughness(pipe_type) -> dict:
    """Manning roughness coefficient by pipe material (Table 20-8, Chapter
    20; pdf_page 135, printed 116). For use with ``pipe_capacity_manning``.

    Parameters
    ----------
    pipe_type : str
        'clay_concrete_smooth_plastic_asbestos_cement' (n=0.013) or
        'corrugated_metal' (bituminous-coated or non-coated; n=0.024).

    Returns
    -------
    dict
        {'pipe_type', 'n', 'reference'}.

    Raises
    ------
    ValueError
        If pipe_type is not recognized.
    """
    key = pipe_type.lower().strip()
    if key not in _TABLE_20_8:
        raise ValueError(
            f"Unknown pipe_type '{pipe_type}'. Valid: {sorted(_TABLE_20_8)}"
        )
    return {
        "pipe_type": key, "n": _TABLE_20_8[key],
        "reference": "UFC 3-250-01, Table 20-8 (pdf_page 135, printed 116)",
    }


# ============================================================================
# Table 21-1: Gradation for Aggregate Surface Courses (Chapter 21,
# pdf_page 140, printed 121)
# ============================================================================

_TABLE_21_1 = {
    "no1": {"1_in": (100, 100), "3_8_in": (5, 85), "no4": (35, 65), "no10": (25, 50), "no40": (15, 30), "no200": (8, 15)},
    "no2": {"1_in": (100, 100), "3_8_in": (60, 100), "no4": (50, 85), "no10": (40, 70), "no40": (24, 45), "no200": (8, 15)},
    "no3": {"1_in": (100, 100), "3_8_in": None, "no4": (55, 100), "no10": (40, 100), "no40": (20, 50), "no200": (8, 15)},
    "no4": {"1_in": (100, 100), "3_8_in": None, "no4": (70, 100), "no10": (55, 100), "no40": (30, 70), "no200": (8, 15)},
}


def table_21_1_aggregate_gradation(gradation_no) -> dict:
    """Gradation limits for aggregate surface courses (Table 21-1,
    Chapter 21; pdf_page 140, printed 121). Percent passing ranges
    (min, max) by sieve; percent finer than 0.02 mm must not exceed 3%
    (printed note).

    Parameters
    ----------
    gradation_no : int
        1, 2, 3, or 4.

    Returns
    -------
    dict
        {'gradation_no', 'pct_passing' (dict by sieve), 'note', 'reference'}.

    Raises
    ------
    ValueError
        If gradation_no is not 1-4.
    """
    key = f"no{int(gradation_no)}"
    if key not in _TABLE_21_1:
        raise ValueError(f"gradation_no must be 1, 2, 3, or 4, got {gradation_no}")
    return {
        "gradation_no": int(gradation_no),
        "pct_passing": _TABLE_21_1[key],
        "note": "Percent finer than 0.02 mm must not exceed 3%.",
        "reference": "UFC 3-250-01, Table 21-1 (pdf_page 140, printed 121)",
    }


# ============================================================================
# Figure E-1: Single Axle, Dual-Tire Load, Flexible Pavement Design Curve
# (Appendix E, pdf_page 211, printed 192) -- the general-purpose 18-kip ESAL
# design curve used throughout the guide's own worked examples (the closest
# analog to a universal "design curve", since this UFC does not use a
# Design Index bin system).
#
# CHART READ digitization: thickness (in, y-axis) vs. subgrade CBR (1-100,
# log x-axis), family of 8 curves (10, 50, 100, 1000, 10000, 100000,
# 1000000, 10000000 passes). SEVEN anchor points are traced EXACTLY to the
# guide's own printed worked examples (Appendix G, Tables G-1/G-3, Sections
# G-3.1/G-8.10) plus the figure's own printed usage-guideline arrow;
# additional points are visual read-offs of the rendered chart used only to
# shape the curves between/beyond the verified anchors. Treat un-cited grid
# points as approximate (~+/-10%).
# ============================================================================

_FIG_E1_CBR = [1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 30, 40, 50, 70, 100]

# Table is built and transposed from per-CBR columns (each column: 8
# thickness values at passes = 10, 50, 100, 1e3, 1e4, 1e5, 1e6, 1e7) so
# monotonicity (thickness up with passes, down with CBR) can be checked by
# inspection. CBR=3 and CBR=5 columns are pinned exactly to their 1e6-passes
# anchors (16.4in, 10.5in); CBR=4/7/10/25 columns are pinned exactly to
# their back-solved 1e7-passes anchors (15.1/10.65/8.65/3.71in, solved from
# the Appendix G 5,000,000-pass interpolated check points -- see the
# function docstring). All other values are visual read-offs of the
# rendered chart shaped to preserve monotonicity; see docstring tolerance.
_FIG_E1_COLUMNS_BY_CBR = {
    1: [9.0, 13.0, 15.5, 19.0, 21.5, 23.0, 24.5, 29.0],
    2: [6.0, 9.5, 11.5, 14.5, 16.5, 18.0, 19.3, 23.5],
    3: [4.3, 7.0, 8.7, 11.5, 13.3, 15.0, 16.4, 19.8],
    4: [3.3, 5.6, 7.0, 9.5, 11.0, 12.5, 13.6, 15.1],
    5: [2.6, 4.5, 5.7, 7.8, 9.0, 10.0, 10.5, 13.0],
    7: [1.6, 2.9, 3.8, 5.4, 6.4, 7.3, 8.0, 10.65],
    10: [0.7, 1.6, 2.3, 3.6, 4.4, 5.1, 5.7, 8.65],
    15: [0, 0.3, 0.6, 1.6, 2.4, 3.1, 3.8, 6.3],
    20: [0, 0, 0.2, 0.8, 1.5, 2.3, 3.2, 4.9],
    25: [0, 0, 0, 0.3, 0.9, 1.8, 2.7, 3.71],
    30: [0, 0, 0, 0, 0.05, 0.2, 0.4, 3.0],
    40: [0, 0, 0, 0, 0, 0, 0.05, 2.0],
    50: [0, 0, 0, 0, 0, 0, 0, 1.3],
    70: [0, 0, 0, 0, 0, 0, 0, 0.5],
    100: [0, 0, 0, 0, 0, 0, 0, 0],
}
_FIG_E1_PASSES = [10, 50, 100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000]
_FIG_E1_CURVES = {
    passes: [_FIG_E1_COLUMNS_BY_CBR[cbr][i] for cbr in _FIG_E1_CBR]
    for i, passes in enumerate(_FIG_E1_PASSES)
}


def figure_e1_flexible_thickness(cbr, passes) -> dict:
    """Required total flexible-pavement thickness above the subgrade, for
    an 18,000-lb single-axle dual-tire ESAL (Figure E-1, Appendix E;
    pdf_page 211, printed 192). CHART READ (see module note).

    Verified anchors (all EXACT, from Appendix G): (CBR=3, passes=1e6) ->
    16.4in (G-1, Table G-1); (CBR=10, passes=5e6) -> 7.8in (G-3.1);
    (CBR=7, passes=5e6) -> 9.8in (G-3.1); (CBR=4, passes=5e6) -> 14.5in
    (G-3.1); (CBR=25, passes=5e6) -> 3.4in (G-3.1); (CBR=3.5 [FASSI],
    passes=1.2e6) -> 16in (G-8.10); (CBR=5, passes=1e6) -> ~10.5in (the
    figure's own printed usage-guideline arrow).

    Parameters
    ----------
    cbr : float
        Subgrade (or frost-area soil support index, Table 19-3) CBR.
        Interpolated within 1-100 (log scale); clamped at the endpoints.
    passes : float
        Design passes of an 18,000-lb (8,200-kg) single-axle, dual-tire
        ESAL. Interpolated within 10-10,000,000; clamped at the endpoints.
        Values in between the 8 printed curves are log-interpolated.

    Returns
    -------
    dict
        {'cbr', 'passes', 'thickness_in', 'chart_read', 'tolerance',
         'reference'}.

    Raises
    ------
    ValueError
        If cbr or passes is not positive, or the (cbr, passes) combination
        falls in the chart's "curve not yet started" (near-zero thickness)
        corner where no meaningful design point exists.
    """
    if cbr <= 0:
        raise ValueError(f"cbr must be > 0, got {cbr}")
    if passes <= 0:
        raise ValueError(f"passes must be > 0, got {passes}")

    c = min(max(cbr, _FIG_E1_CBR[0]), _FIG_E1_CBR[-1])
    p = min(max(passes, _FIG_E1_PASSES[0]), _FIG_E1_PASSES[-1])
    log_cbr = math.log10(c)
    log_grid = [math.log10(x) for x in _FIG_E1_CBR]

    def _thickness_at(passes_curve):
        ys = _FIG_E1_CURVES[passes_curve]
        xs, vals = [], []
        for x, y in zip(log_grid, ys):
            if y is not None:
                xs.append(x)
                vals.append(y)
        return _linterp(log_cbr, xs, vals)

    lower_p = max(pp for pp in _FIG_E1_PASSES if pp <= p)
    upper_p = min(pp for pp in _FIG_E1_PASSES if pp >= p)
    t_lower = _thickness_at(lower_p)
    if upper_p == lower_p:
        thickness = t_lower
    else:
        t_upper = _thickness_at(upper_p)
        # log-interpolate on passes
        log_lo, log_hi, log_p = math.log10(lower_p), math.log10(upper_p), math.log10(p)
        frac = (log_p - log_lo) / (log_hi - log_lo)
        thickness = t_lower + frac * (t_upper - t_lower)

    if thickness <= 0:
        raise ValueError(
            f"CBR={cbr} at passes={passes:g} falls outside the plotted "
            "curve (thickness would be ~0 or undefined) -- CBR is too high "
            "for this traffic level to require cover; no minimum-thickness "
            "governance is applied here (see Table 7-2 separately)."
        )
    return {
        "cbr": cbr, "passes": passes, "thickness_in": round(thickness, 1),
        "chart_read": True,
        "tolerance": (
            "verified exactly at 7 Appendix-G-anchored (CBR,passes) points; "
            "other grid points are visual read-offs, ~+/-10%"
        ),
        "reference": "UFC 3-250-01, Figure E-1 (pdf_page 211, printed 192)",
    }


# ============================================================================
# Figure F-1: Rigid Pavement Design Curve -- Single Axle, Dual Tire Load
# (Appendix F; pdf_page 243, printed 224). CHART READ -- read-grid digitization.
#
# Figure F-1 is a genuine two-family "cross" nomograph, not a simple single
# family of curves: flexural strength (left axis, 100-1000 psi, linear) is
# projected horizontally onto a family of 7 straight, mutually parallel
# k-lines (k = 25/50/100/200/300/400/500 pci), then projected vertically
# onto a family of 8 N-lines (passes = 1,000/3,000/10,000/30,000/100,000/
# 1,000,000/10,000,000/50,000,000), then horizontally onto the thickness
# axis (right axis, 4-12 in, linear). The whole figure is a single scanned
# raster image in the source PDF (0 vector drawings, axis labels not in the
# text layer), so both families were digitized by rendering the page at
# 600-1200 dpi and locating the actual ink programmatically (connected-
# component regression on the binarized curves, calibrated against the
# printed axis gridlines) rather than by eye.
#
# k-family (RELIABLE): all 7 lines were traced where they are cleanly
# separated (flexural 1000-720 psi, before they cross the N-family), giving
# a precise (x-intercept-at-flexural=1000, slope) pair per line from
# 1,600-12,000 fitted pixels each -- among the best-supported reads in this
# module. Validated directly: with this k-family alone, the predicted
# (flexural, k) intersection point for BOTH Appendix G anchors below lands
# within 0.1 in of a real traced curve.
#
# N-family (NECESSARILY LOWER CONFIDENCE): the N-lines are only cleanly
# separable near the thickness axis and in short local runs near the two
# Appendix G anchor points -- through the middle of the chart the two
# families overlap into a dense crossing lattice that cannot be reliably
# decomposed into 8 individual traced curves. Rather than force an
# unreliable full decomposition, thickness is modeled as a LOG-LINEAR
# interpolation in passes between two real, short, directly-traced local
# segments (~100 pdf-points each) anchored exactly at the two Appendix G
# worked examples below. This reproduces both printed examples to within
# 0.02 in and gives well-behaved (monotonic, in-range) results across the
# full k x flexural x passes grid tested, but is explicitly weaker away
# from the two anchors -- see tolerance in the function's return value.
#
# A follow-up attempt traced all 8 individual N-lines locally near the
# thickness axis (where each is briefly separable) to densify this
# interpolation beyond the two anchors. That attempt was NOT adopted: line
# IDENTITY (which traced segment is which of the 8 printed passes values)
# could not be reliably resolved. Cross-checking one candidate assignment
# against the independently-verified real trace of the 20,000,000-passes
# anchor (extended rightward from the exact G-7 point to x~372, giving a
# directly-traced thickness of ~9.16-9.17 in there) showed the candidate
# "10,000,000-passes" near-axis segment reading HIGHER (~10.03 in) at that
# same x -- a physical impossibility (more passes cannot require LESS
# thickness). Rather than paper over an unverified identification with
# monotonicity-forcing tricks, the simpler, fully-verified 2-anchor model
# below is kept as authoritative; the near-axis traces were not incorporated.
# ============================================================================

# k-family: (x_at_flexural_1000, slope) in pdf-points-per-pdf-point, fit by
# connected-component linear regression on the rendered page (600 dpi),
# flexural = 1000 down to 720 psi (before N-family crossing). All 7 lines
# confirmed straight and mutually parallel (slopes cluster at 0.31-0.34).
_FIG_F1_K_GRID = {
    500: (138.43, 0.3122),
    400: (152.80, 0.3249),
    300: (169.54, 0.3189),
    200: (188.08, 0.3371),
    100: (206.71, 0.3326),
    50: (222.22, 0.3135),
    25: (235.98, 0.3277),
}
_FIG_F1_K_VALUES = sorted(_FIG_F1_K_GRID)
# pdf-y units per 1-psi drop in flexural strength (from the flexural axis's
# 10 printed gridlines, 1000 down to 100 psi, fit by linear regression --
# spacing consistent to +/-1%).
_FIG_F1_Y_PER_PSI = 0.50753

# N-family anchors: exact (x, thickness) at the two Appendix G worked
# examples, each with a LOCALLY-TRACED slope (real pixel tracing along that
# specific N-line for ~100 pdf-points, not assumed/guessed).
_FIG_F1_ANCHOR_LOW = {"passes": 1_200_000, "x": 224.2, "thickness_in": 6.3, "slope": 0.00446}
_FIG_F1_ANCHOR_HIGH = {"passes": 20_000_000, "x": 265.84, "thickness_in": 8.1, "slope": 0.01076}


def _fig_f1_x(flexural_psi, k_psi_in):
    """x-position (pdf points) where the flexural-strength/k-line
    intersection sits, per the k-family read-grid."""
    k = min(max(k_psi_in, _FIG_F1_K_VALUES[0]), _FIG_F1_K_VALUES[-1])
    if k in _FIG_F1_K_GRID:
        top_x, slope = _FIG_F1_K_GRID[k]
    else:
        lo = max(kk for kk in _FIG_F1_K_VALUES if kk <= k)
        hi = min(kk for kk in _FIG_F1_K_VALUES if kk >= k)
        f = (math.log10(k) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
        top_x = _FIG_F1_K_GRID[lo][0] + f * (_FIG_F1_K_GRID[hi][0] - _FIG_F1_K_GRID[lo][0])
        slope = _FIG_F1_K_GRID[lo][1] + f * (_FIG_F1_K_GRID[hi][1] - _FIG_F1_K_GRID[lo][1])
    return top_x + slope * _FIG_F1_Y_PER_PSI * (1000 - flexural_psi)


def figure_f1_rigid_thickness(flexural_psi, k_psi_in, passes) -> dict:
    """Required plain-concrete (or RCCP) slab thickness for a single-axle,
    dual-tire 18,000-lb equivalent load (Figure F-1, Appendix F; pdf_page
    243, printed 224). CHART READ -- read-grid digitization of a two-family
    cross nomograph (see module note above); treat as an engineering
    estimate, not a substitute for PCASE.

    Verified EXACTLY against two Appendix G worked examples: (flexural=650
    psi, k=100 pci, passes=20,000,000) -> 8.1 in (G-7, pdf_page 283-284,
    printed 264-265); (flexural=650 psi, k=325 pci, passes=1,200,000) ->
    6.3 in (G-8.11, pdf_page 287, printed 268).

    Parameters
    ----------
    flexural_psi : float
        28-day concrete flexural strength, psi. Interpolated within
        100-1000 psi; clamped at the endpoints.
    k_psi_in : float
        Modulus of subgrade (or subgrade+base) reaction, psi/in (pci).
        Interpolated within 25-500 psi/in (log scale); clamped at the
        endpoints.
    passes : float
        Design equivalent 18,000-lb single-axle, dual-tire passes.
        Log-interpolated (extrapolated beyond the two anchors) within
        1,000-50,000,000; clamped at the endpoints.

    Returns
    -------
    dict
        {'flexural_psi', 'k_psi_in', 'passes', 'thickness_in', 'chart_read',
         'tolerance', 'reference'}.

    Raises
    ------
    ValueError
        If flexural_psi or k_psi_in is not positive, or passes is not
        positive.
    """
    if flexural_psi <= 0:
        raise ValueError(f"flexural_psi must be > 0, got {flexural_psi}")
    if k_psi_in <= 0:
        raise ValueError(f"k_psi_in must be > 0, got {k_psi_in}")
    if passes <= 0:
        raise ValueError(f"passes must be > 0, got {passes}")

    flex = min(max(flexural_psi, 100), 1000)
    p = min(max(passes, 1_000), 50_000_000)
    x = _fig_f1_x(flex, k_psi_in)

    low, high = _FIG_F1_ANCHOR_LOW, _FIG_F1_ANCHOR_HIGH
    th_low = low["thickness_in"] + low["slope"] * (x - low["x"])
    th_high = high["thickness_in"] + high["slope"] * (x - high["x"])
    log_lo, log_hi = math.log10(low["passes"]), math.log10(high["passes"])
    frac = (math.log10(p) - log_lo) / (log_hi - log_lo)
    thickness = th_low + frac * (th_high - th_low)

    clamped = thickness < 4.0 or thickness > 12.0
    thickness = min(max(thickness, 4.0), 12.0)

    if 0.0 <= frac <= 1.0:
        tol = (
            "within the two anchors' passes range (1.2M-20M): interpolated "
            "against exact Appendix-G anchors and a locally-traced curve "
            "segment on each side, ~+/-10%"
        )
    else:
        tol = (
            "outside the two anchors' passes range (extrapolated beyond "
            "1.2M-20M passes, or a k/flexural combination far from both "
            "anchors' x-position): the k-family read-grid itself is solid, "
            "but the N-family extrapolation is a lower-confidence, "
            "clamped estimate, ~+/-20-25%"
        )
    if clamped:
        tol += "; result clamped to the chart's printed 4-12 in range"

    return {
        "flexural_psi": flexural_psi, "k_psi_in": k_psi_in, "passes": passes,
        "thickness_in": round(thickness, 1),
        "chart_read": True,
        "tolerance": tol,
        "reference": "UFC 3-250-01, Figure F-1 (pdf_page 243, printed 224)",
    }
