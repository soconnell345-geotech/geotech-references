"""UFC 3-250-01 pavement design lookup tables and design-curve read-offs.

Pavement Design for Roads and Parking Areas (14 November
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
chart and are noted as approximate. Figures E-1 and F-1 are read along
every printed curve (REF-58), the vehicle curves E-2 to E-31 and the frost
charts 19-5 and 19-6 likewise (GM-303), and each is checked against every
Appendix G read of it; Table 19-2 refuses a soil it does not list rather
than give it a group.
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

# ESAL bins as printed "< n" (upper bound exclusive), the last ">= n".
# Flexible column of Table 5-1 and the only column of Table 21-2:
_COMPACTION_ESAL_BINS = [
    15_500, 67_500, 295_000, 1_300_000, 5_700_000,
    25_000_000, 112_000_000, 500_000_000, 2_200_000_000, float("inf"),
]
# Rigid column of Table 5-1 (pdf_page 33, printed 14), as printed:
_COMPACTION_ESAL_BINS_RIGID = [
    1_300, 1_500, 34_000, 343_000, 2_100_000,
    9_200_000, 37_000_000, 105_000_000, 290_000_000, float("inf"),
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

# Table 21-2 (aggregate surfaces; pdf_page 143, printed 124): cohesive soils
# at 100/95/90/85/80 %, cohesionless soils at 100/95/90/85 % (no 80 column).
_TABLE_21_2_COHESIVE = [
    (2, 4, 6, 7, 9), (3, 5, 7, 9, 11), (3, 5, 8, 10, 13), (3, 6, 9, 12, 14),
    (4, 7, 10, 13, 16), (4, 7, 11, 15, 18), (4, 8, 12, 16, 20),
    (5, 9, 13, 18, 22), (5, 10, 15, 20, 25), (6, 11, 17, 22, 27),
]
_TABLE_21_2_COHESIONLESS = [
    (4, 7, 10, 13), (5, 8, 12, 16), (5, 10, 14, 18), (6, 11, 16, 21),
    (7, 12, 18, 23), (7, 14, 20, 26), (8, 15, 22, 29), (9, 17, 24, 31),
    (10, 19, 28, 35), (11, 21, 30, 38),
]


def _compaction_depth_lookup(passes, density_pct, soil_type, table,
                             bins=_COMPACTION_ESAL_BINS):
    idx = None
    for i, upper in enumerate(bins):
        if passes < upper:
            idx = i
            break
    if idx is None:
        idx = len(bins) - 1

    if table == "5-1":
        density_levels = (100, 95, 90, 85, 80)
        rows = _TABLE_5_1_COHESIVE if soil_type == "cohesive" else _TABLE_5_1_COHESIONLESS
    elif soil_type == "cohesive":
        density_levels = (100, 95, 90, 85, 80)
        rows = _TABLE_21_2_COHESIVE
    else:
        density_levels = (100, 95, 90, 85)
        rows = _TABLE_21_2_COHESIONLESS

    if density_pct not in density_levels:
        raise ValueError(
            f"density_pct must be one of {density_levels} for this table, "
            f"got {density_pct}"
        )
    col = density_levels.index(density_pct)
    return rows[idx][col]


def table_5_1_compaction_depth(passes, density_pct, soil_type,
                               pavement_type) -> dict:
    """Depth of compaction for select materials and subgrades (CBR <= 20),
    UFC 3-250-01 Table 5-1 (pdf_page 33, printed 14); returns depth_in, the
    depth in inches from the pavement surface to which the given percent
    compaction is required, for a flexible or a rigid pavement.

    The table has one column of traffic for flexible and one for rigid
    pavements (passes of an 18,000-lb ESAL): flexible < 15,500, < 67,500,
    < 295,000, < 1.3 million ... >= 2,200 million; rigid < 1,300, < 1,500,
    < 34,000, < 343,000 ... >= 290 million. Each bound is printed "<", so a
    value equal to a bound falls in the next row. The table gives no
    default column, so pavement_type is required.

    Parameters
    ----------
    passes : float
        Equivalent passes of an 18,000-lb (8,200-kg) ESAL over the design
        life. Must be > 0.
    density_pct : int
        Percent compaction (of ASTM D1557 maximum density): 100, 95, 90, 85,
        or 80.
    soil_type : str
        'cohesive' (PI > 5, LL > 25) or 'cohesionless' (PI <= 5, LL <= 25).
    pavement_type : str
        'flexible' or 'rigid': which printed traffic column to use
        (required; the table prints both and gives no default).

    Returns
    -------
    dict
        {'passes', 'density_pct', 'soil_type', 'pavement_type', 'depth_in',
         'reference'}.

    Raises
    ------
    ValueError
        If passes <= 0, density_pct is not one of the printed levels, or
        soil_type or pavement_type is not recognized.
    """
    if passes <= 0:
        raise ValueError(f"passes must be > 0, got {passes}")
    key = soil_type.lower().strip()
    if key not in ("cohesive", "cohesionless"):
        raise ValueError(f"soil_type must be 'cohesive' or 'cohesionless', got '{soil_type}'")
    ptype = str(pavement_type).lower().strip()
    if ptype not in ("flexible", "rigid"):
        raise ValueError(
            f"pavement_type must be 'flexible' or 'rigid', got '{pavement_type}'")
    bins = _COMPACTION_ESAL_BINS_RIGID if ptype == "rigid" else _COMPACTION_ESAL_BINS
    depth = _compaction_depth_lookup(passes, density_pct, key, "5-1", bins)
    return {
        "passes": passes, "density_pct": density_pct, "soil_type": key,
        "pavement_type": ptype, "depth_in": depth,
        "reference": "UFC 3-250-01, Table 5-1 (pdf_page 33, printed 14)",
    }


def table_21_2_aggregate_compaction_depth(passes, density_pct, soil_type) -> dict:
    """Compaction depth requirements for aggregate surfaces, UFC 3-250-01
    Table 21-2 (pdf_page 143, printed 124); returns depth_in, the depth in
    inches from the surface of the aggregate road (not the subgrade) to
    which the given percent compaction is required.

    Traffic bins are printed "< 15,500" ... ">= 2,200 million" passes; a
    value equal to a bound falls in the next row.

    Parameters
    ----------
    passes : float
        Equivalent passes of an 18,000-lb (8,200-kg) ESAL. Must be > 0.
    density_pct : int
        Percent compaction: 100, 95, 90, 85 or 80 for cohesive soils; 100,
        95, 90 or 85 for cohesionless soils (the print has no 80 column for
        them).
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
    # Asphalt-stabilized, as printed: three rows by material.
    ("asphalt", "all_bituminous_concrete"): {"base": 1.15, "subbase": 2.30},
    ("asphalt", "gw"): {"base": 1.00, "subbase": 2.00},
    ("asphalt", "gp"): {"base": 1.00, "subbase": 2.00},
    ("asphalt", "gm"): {"base": 1.00, "subbase": 2.00},
    ("asphalt", "gc"): {"base": 1.00, "subbase": 2.00},
    ("asphalt", "sw"): {"base": None, "subbase": 1.50},
    ("asphalt", "sp"): {"base": None, "subbase": 1.50},
    ("asphalt", "sm"): {"base": None, "subbase": 1.50},
    ("asphalt", "sc"): {"base": None, "subbase": 1.50},
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
    """Equivalency factor for stabilized material, UFC 3-250-01 Table 9-1
    (pdf_page 46, printed 27); returns the factor E, the inches of
    conventional base or subbase that 1 in of the stabilized material
    replaces (t_stab = t_conventional / E).

    Asphalt-stabilized rows as printed: all-bituminous concrete 1.15 base /
    2.30 subbase; GW, GP, GM, GC 1.00 / 2.00; SW, SP, SM, SC subbase 1.50
    only (* not used for base course material). The cement content must be
    limited to 4 percent by weight or less to prevent excessive reflective
    cracking (para 9-5.1, same page).

    Verified against the guide's printed examples (Appendix G, G-4.1/G-4.2,
    pdf_page 279-280): cement-stabilized base E = 1.15, subbase E = 2.30.

    Parameters
    ----------
    stabilizer_type : str
        'asphalt', 'cement', 'lime', 'lime_cement_flyash',
        'unbound_crushed_stone', or 'unbound_aggregate'.
    uscs_class : str
        USCS classification of the soil to be stabilized (e.g. 'CL', 'SM'),
        or 'all-bituminous concrete' for that asphalt row. Ignored for
        'unbound_crushed_stone' and 'unbound_aggregate'.
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

    all_stabs = {"unbound_crushed_stone", "unbound_aggregate"}
    if stab_resolved in all_stabs:
        uscs_key = "all"
    elif stab_resolved == "asphalt" and "bituminous" in uscs_class.lower():
        uscs_key = "all_bituminous_concrete"
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
# for Non-frost Conditions (Chapter 10; PDF page 52, printed 32)
#
# Traced from the chart (pave-22, 2026-11-10). The earlier table, read by
# eye at 10 in. steps, was up to 29 % low at mid thicknesses and up to 39 %
# high for the 25 to 75 pci curves under bases thinner than about 10 in.
# (their S-shaped start). The chart is one embedded image (1431 x 1453 px,
# about 220 dpi on the page), read at that native resolution (rendering the
# page finer only resamples it). Calibration on the chart's own gridlines:
# the scan is turned about 0.25 degrees, so each gridline was fitted as a
# straight line (scatter 0.3 to 0.5 px); one uniform scale fits the seven
# thickness lines (0 to 60 in.) within 0.07 in. and one log scale fits the
# nine k lines (20 to 500 pci) within 0.7 % of k; readings are taken
# piecewise between neighbouring gridlines. 1 px is 0.26 % of k up the
# chart and 0.055 in. across it. Each of the seven curves was traced column
# by column (about 1,000 readings per curve); where a curve shares a dark
# run with a gridline, a label or another curve, its centre is read from
# its free edge (that rule, tried where the centre is known, errs up to
# 0.54 % of k at the 95th percentile). A local quadratic (+-1 in.) through
# the readings gives the stored values; it lies within 1.0 % of every
# reading (0.35 % of the clean ones). Stored every 0.5 in. to 6 in., every
# 1 in. to 20 in. and every 2 in. to 60 in., where linear interpolation on
# log k stays within 0.28 % of the smooth trace. Each curve starts on its
# own gridline at t = 0 (k on base = k on subgrade). Check: the 200 curve
# passes through the gridline crossing (10 in., 300 pci); the table gives
# 299.7. Stated tolerance: 1 % of k on the curves. Exception: the 200 curve
# beyond 55 in. and the 300 curve beyond 57 in. run together with the 150
# curve and the frame (500 pci) and cannot be seen apart; there they are
# extrapolated from their last 3 in. and held between the 150 curve and 500,
# so within 2 %.
# ============================================================================

_FIG_10_1_THICKNESS = [
    0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7, 8, 9, 10, 11,
    12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 24, 26, 28, 30, 32, 34, 36,
    38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60,
]
_FIG_10_1_CURVES = {
    25: [
        25.0, 25.0, 25.2, 25.6, 26.1, 26.7, 27.5, 28.4, 29.5, 30.8,
        32.4, 34.2, 36.3, 40.8, 45.2, 50.0, 55.3, 61.0, 66.8, 72.8,
        79.3, 85.6, 92.0, 98.5, 105.3, 112.3, 119.5, 134.3, 148.7,
        162.5, 175.9, 189.2, 201.4, 213.4, 225.3, 237.3, 248.0, 259.1,
        269.9, 280.8, 290.9, 302.1, 312.2, 322.9, 333.4, 344.0, 353.1,
    ],
    50: [
        50.0, 50.0, 50.3, 50.8, 51.6, 52.7, 54.2, 55.9, 58.0, 60.5,
        63.3, 66.8, 70.8, 78.9, 87.0, 95.2, 103.7, 112.0, 120.2, 128.3,
        137.1, 145.8, 153.9, 162.2, 170.8, 179.0, 187.2, 203.8, 220.2,
        236.2, 249.4, 262.7, 274.8, 286.7, 297.8, 308.4, 318.5, 328.0,
        337.2, 345.9, 353.7, 362.1, 370.1, 377.9, 385.6, 393.2, 400.9,
    ],
    75: [
        75.0, 75.3, 76.6, 78.2, 80.0, 82.3, 84.7, 87.3, 90.5, 94.3,
        98.5, 103.1, 107.9, 117.9, 127.9, 138.2, 148.5, 159.0, 169.2,
        179.5, 189.8, 199.5, 208.0, 216.6, 225.3, 233.3, 240.9, 256.7,
        272.2, 287.1, 300.2, 313.4, 325.1, 336.6, 346.8, 356.4, 365.5,
        374.3, 382.1, 390.0, 397.4, 404.6, 410.9, 416.8, 423.1, 428.7,
        432.2,
    ],
    100: [
        100.0, 101.8, 104.4, 107.4, 111.0, 115.1, 119.6, 124.3, 129.4,
        134.5, 139.6, 144.9, 150.4, 161.8, 172.8, 183.7, 194.4, 204.3,
        213.6, 223.0, 232.5, 241.6, 250.4, 259.9, 269.2, 277.9, 286.4,
        303.6, 318.9, 333.4, 346.3, 358.9, 369.8, 380.2, 390.1, 399.1,
        406.9, 414.0, 421.2, 428.3, 434.3, 440.3, 446.6, 452.3, 457.3,
        462.5, 467.0,
    ],
    150: [
        150.0, 155.8, 161.3, 166.6, 171.9, 177.1, 182.2, 187.0, 191.9,
        196.9, 201.3, 205.6, 210.3, 219.7, 228.9, 237.9, 246.9, 256.0,
        265.0, 273.7, 283.1, 291.5, 299.9, 308.5, 317.8, 326.4, 334.8,
        350.5, 365.2, 378.9, 391.5, 404.4, 414.2, 424.0, 432.5, 440.0,
        446.4, 452.9, 458.5, 463.9, 468.3, 473.3, 477.1, 480.8, 484.1,
        486.8, 489.7,
    ],
    200: [
        200.0, 204.3, 210.0, 215.6, 221.4, 227.0, 232.5, 237.8, 242.8,
        247.8, 252.7, 257.7, 262.7, 272.5, 281.8, 290.5, 299.7, 308.6,
        317.0, 325.2, 333.1, 340.6, 347.3, 354.2, 361.3, 368.4, 375.1,
        388.1, 400.4, 410.7, 420.0, 429.0, 437.1, 444.4, 451.4, 456.5,
        461.3, 466.4, 470.6, 474.7, 478.7, 481.8, 484.8, 487.3, 490.0,
        491.9, 493.4,
    ],
    300: [
        300.0, 304.2, 307.3, 310.4, 313.6, 316.7, 319.7, 322.6, 325.6,
        328.4, 331.2, 334.0, 336.8, 342.2, 347.3, 352.4, 357.7, 363.3,
        368.8, 373.6, 379.2, 384.2, 389.4, 394.7, 400.3, 405.4, 410.2,
        419.1, 427.5, 434.9, 441.2, 447.6, 452.9, 457.9, 462.3, 466.0,
        469.6, 473.3, 476.9, 479.9, 482.5, 485.4, 488.7, 490.7, 493.4,
        496.3, 499.8,
    ],
}
_FIG_10_1_SUBGRADE_K = sorted(_FIG_10_1_CURVES)
_FIG_10_1_NOTE = (
    "NOTE: k measured on subgrade or base course with 30-in.-diam bearing "
    "plate. Base course is constructed of high-quality material. This "
    "relationship has been developed from results of plate bearing tests on "
    "the surface of base courses constructed on a range of subgrade "
    "strengths.")


def _fig_10_1_log_k_on_curve(k_curve, t):
    """log10 k on base along one drawn curve at thickness t (0-60 in.),
    linear in t between the stored points."""
    import bisect
    import math
    ts, ks = _FIG_10_1_THICKNESS, _FIG_10_1_CURVES[k_curve]
    i = min(max(bisect.bisect_right(ts, t) - 1, 0), len(ts) - 2)
    t0, t1 = ts[i], ts[i + 1]
    l0, l1 = math.log10(ks[i]), math.log10(ks[i + 1])
    return l0 + (t - t0) / (t1 - t0) * (l1 - l0)


def figure_10_1_k_on_base(k_subgrade_psi_in, base_thickness_in) -> dict:
    """Effective modulus of soil reaction k on top of a base course, psi/in,
    for non-frost conditions, from UFC 3-250-01 Figure 10-1 (printed p. 32,
    PDF 52): read off the chart's curves for k measured on the subgrade
    (25, 50, 75, 100, 150, 200 and 300 psi/in) at the base course
    thickness (0 to 60 in.). Paragraph 10-4 (printed p. 30-31): "Where a
    base course is used under the pavement, the k value on top of the
    base (also known as the effective k value) is used to determine the
    pavement thickness. The plate-bearing test may be run on top of the
    base, or Figure 10-1 may be used ... It is good practice to confirm
    adequacy of the k on top of the base from Figure 10-1 by running a
    field plate-load test."

    The chart's note: "k measured on subgrade or base course with
    30-in.-diam bearing plate. Base course is constructed of high-quality
    material. This relationship has been developed from results of plate
    bearing tests on the surface of base courses constructed on a range of
    subgrade strengths."

    Values on a drawn curve are traced from the chart (within 1 % of k;
    2 % for the 200 curve beyond 55 in. and the 300 curve beyond 57 in.,
    where those curves run together with the 150 curve and the frame; see
    the module note). Along a curve, log k is interpolated linearly in
    thickness between the stored points (every 0.5 to 2 in.). Between two
    curves, log k on base is interpolated linearly in log k on subgrade at
    the same thickness. That rule is the library's: the chart does not say
    how to read between its curves (predicting a drawn curve from the
    curves either side of it this way errs by up to about 6 %, so a value
    between curves is less certain than one on a curve).

    Parameters
    ----------
    k_subgrade_psi_in : float
        Modulus of soil reaction measured (or estimated, Table 10-1) on
        the subgrade, psi/in, 25 to 300 (the drawn curves). Below 25
        refused; above 300 the 300 curve is used, with a note (it then
        understates k on the base).
    base_thickness_in : float
        Thickness of base course above the subgrade, inches, 0 to 60 (the
        chart's axis). Above 60 in the 60 in value is used, with a note.

    Returns
    -------
    dict
        {'k_subgrade_psi_in', 'base_thickness_in', 'k_on_base_psi_in',
         'chart_read', 'tolerance', 'interpolation', 'chart_note',
         'reference', 'note'?}.

    Raises
    ------
    ValueError
        If k_subgrade_psi_in is below 25 psi/in (the lowest drawn curve)
        or base_thickness_in is negative.

    Example: k on subgrade 100 psi/in under 10 in. of base gives 194.4
    psi/in; 200 under 10 in. gives 299.7 (the chart's curve passes through
    300 there).
    """
    import math
    if k_subgrade_psi_in < _FIG_10_1_SUBGRADE_K[0]:
        raise ValueError(
            f"k_subgrade_psi_in {k_subgrade_psi_in} is below Figure 10-1's "
            "lowest curve (k on subgrade = 25 pci); the chart covers 25-300.")
    if base_thickness_in < 0:
        raise ValueError(f"base_thickness_in must be >= 0, got {base_thickness_in}")

    notes = []
    if base_thickness_in > 60:
        notes.append(f"Base thickness {base_thickness_in:g} in is past Figure "
                     "10-1's axis (0-60 in); the 60 in value is used.")
    if k_subgrade_psi_in > _FIG_10_1_SUBGRADE_K[-1]:
        notes.append(f"k on subgrade {k_subgrade_psi_in:g} pci is above Figure "
                     "10-1's top curve (300 pci); the 300 curve is used, which "
                     "understates k on the base.")
    t = min(max(base_thickness_in, 0), 60)
    ks = min(k_subgrade_psi_in, _FIG_10_1_SUBGRADE_K[-1])

    lower_k = max(k for k in _FIG_10_1_SUBGRADE_K if k <= ks)
    upper_k = min(k for k in _FIG_10_1_SUBGRADE_K if k >= ks)
    log_lower = _fig_10_1_log_k_on_curve(lower_k, t)
    if upper_k == lower_k:
        log_k = log_lower
        how = f"on the {lower_k} pci curve"
    else:
        log_upper = _fig_10_1_log_k_on_curve(upper_k, t)
        frac = (math.log10(ks) - math.log10(lower_k)) / (
            math.log10(upper_k) - math.log10(lower_k))
        log_k = log_lower + frac * (log_upper - log_lower)
        how = (f"between the {lower_k} and {upper_k} pci curves: log k on "
               "base interpolated linearly in log k on subgrade (the "
               "library's rule; the chart gives none)")

    return {
        "k_subgrade_psi_in": k_subgrade_psi_in,
        "base_thickness_in": base_thickness_in,
        "k_on_base_psi_in": round(10 ** log_k, 1),
        "chart_read": True,
        "tolerance": (
            "traced from the chart: within 1 % of k on a drawn curve (2 % for "
            "the 200 curve beyond 55 in. and the 300 curve beyond 57 in.); "
            "less certain between curves"),
        "interpolation": how,
        "chart_note": _FIG_10_1_NOTE,
        "reference": "UFC 3-250-01, Figure 10-1, printed p. 32 (PDF 52)",
        **({"note": " ".join(notes)} if notes else {}),
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
# CHART READ along each printed curve (pave-01, 2026-11-10). The chart is a
# 594 x 648 px image embedded in the PDF (1-based PDF page 70); each of the
# eleven k curves (25 to 500 psi/in) was traced column by column from that
# image, calibrated on its own gridlines (F 0.4-1.0 every 0.1; passes 100 to
# 10,000,000 on the printed log grid), and F read every 0.1 in
# log10(passes). Measured: trace scatter at most 0.001 on F (0.9 px; 1 px =
# 0.0011 F); where a curve passes under its label box (13 of the 0.2-decade
# points, e.g. k = 200 at 6,300 passes) it is bridged by a quadratic through
# the traced points on both sides, which erred by at most 0.005 on F when
# 32 px gaps were cut out of traced stretches and bridged the same way;
# linear interpolation between the tabulated points stays within 0.0034 of
# the trace. Stated tolerance: 0.005 on F. Checks: k = 100 at 10,000,000
# passes reads 0.930, and Appendix G G-7 (pdf_page 283, printed 264) reads
# 0.93 for k = 100 at 20 million passes.
# ============================================================================

_FIG_15_1_LOG_PASSES = [round(2.0 + 0.1 * i, 1) for i in range(51)]  # 100 .. 1e7
# Where each curve begins (log10 passes, F): at the chart's left edge (100
# passes) for k = 25, 50 and 100, else at its printed lower end.
_FIG_15_1_START = {
    25: (2.0, 0.812),
    50: (2.0, 0.652),
    100: (2.0, 0.408),
    150: (2.161, 0.401),
    200: (2.467, 0.443),
    250: (2.467, 0.401),
    300: (2.941, 0.465),
    350: (2.963, 0.405),
    400: (3.156, 0.401),
    450: (3.446, 0.409),
    500: (3.934, 0.46),
}
_FIG_15_1_CURVES = {
    25: [
        0.812, 0.824, 0.836, 0.848, 0.859, 0.870, 0.880, 0.889, 0.898,
        0.908, 0.915, 0.923, 0.930, 0.936, 0.941, 0.945, 0.949, 0.953,
        0.957, 0.960, 0.963, 0.966, 0.967, 0.969, 0.970, 0.971, 0.972,
        0.973, 0.973, 0.976, 0.976, 0.977, 0.977, 0.978, 0.978, 0.978,
        0.978, 0.978, 0.979, 0.979, 0.979, 0.980, 0.980, 0.980, 0.980,
        0.980, 0.980, 0.980, 0.980, 0.980, 0.980
    ],
    50: [
        0.652, 0.676, 0.696, 0.717, 0.737, 0.756, 0.775, 0.791, 0.809,
        0.827, 0.843, 0.859, 0.873, 0.882, 0.891, 0.899, 0.904, 0.911,
        0.918, 0.924, 0.929, 0.932, 0.936, 0.941, 0.943, 0.945, 0.947,
        0.949, 0.951, 0.952, 0.954, 0.955, 0.956, 0.957, 0.958, 0.958,
        0.959, 0.959, 0.959, 0.960, 0.960, 0.960, 0.960, 0.961, 0.961,
        0.961, 0.961, 0.961, 0.961, 0.961, 0.961
    ],
    100: [
        0.408, 0.451, 0.485, 0.518, 0.550, 0.583, 0.612, 0.639, 0.668,
        0.699, 0.726, 0.748, 0.770, 0.788, 0.804, 0.818, 0.830, 0.842,
        0.854, 0.864, 0.874, 0.880, 0.886, 0.893, 0.897, 0.902, 0.905,
        0.908, 0.910, 0.914, 0.916, 0.918, 0.919, 0.921, 0.922, 0.923,
        0.924, 0.925, 0.926, 0.927, 0.927, 0.928, 0.928, 0.929, 0.929,
        0.929, 0.929, 0.929, 0.929, 0.929, 0.930
    ],
    150: [
        None, None, 0.407, 0.430, 0.452, 0.479, 0.513, 0.545, 0.579,
        0.616, 0.647, 0.675, 0.702, 0.725, 0.746, 0.764, 0.779, 0.794,
        0.809, 0.821, 0.833, 0.841, 0.849, 0.858, 0.863, 0.868, 0.873,
        0.877, 0.881, 0.885, 0.888, 0.890, 0.892, 0.895, 0.896, 0.897,
        0.898, 0.899, 0.899, 0.902, 0.902, 0.904, 0.904, 0.905, 0.905,
        0.905, 0.905, 0.905, 0.905, 0.905, 0.906
    ],
    200: [
        None, None, None, None, None, 0.452, 0.483, 0.514, 0.545, 0.580,
        0.608, 0.637, 0.664, 0.690, 0.712, 0.731, 0.747, 0.763, 0.779,
        0.794, 0.807, 0.817, 0.825, 0.835, 0.841, 0.847, 0.853, 0.858,
        0.863, 0.866, 0.870, 0.872, 0.873, 0.877, 0.879, 0.880, 0.881,
        0.883, 0.883, 0.885, 0.885, 0.886, 0.886, 0.888, 0.889, 0.889,
        0.889, 0.889, 0.889, 0.889, 0.890
    ],
    250: [
        None, None, None, None, None, 0.408, 0.435, 0.461, 0.488, 0.518,
        0.545, 0.577, 0.608, 0.636, 0.661, 0.684, 0.704, 0.722, 0.741,
        0.758, 0.775, 0.787, 0.798, 0.809, 0.818, 0.824, 0.831, 0.838,
        0.843, 0.849, 0.853, 0.858, 0.860, 0.864, 0.865, 0.867, 0.869,
        0.870, 0.871, 0.872, 0.874, 0.876, 0.876, 0.877, 0.878, 0.878,
        0.878, 0.879, 0.879, 0.879, 0.879
    ],
    300: [
        None, None, None, None, None, None, None, None, None, None,
        0.482, 0.513, 0.546, 0.576, 0.604, 0.628, 0.650, 0.672, 0.694,
        0.715, 0.734, 0.749, 0.761, 0.774, 0.785, 0.794, 0.801, 0.809,
        0.816, 0.822, 0.828, 0.831, 0.835, 0.840, 0.842, 0.844, 0.846,
        0.848, 0.849, 0.852, 0.853, 0.855, 0.855, 0.856, 0.857, 0.857,
        0.857, 0.858, 0.858, 0.859, 0.859
    ],
    350: [
        None, None, None, None, None, None, None, None, None, None,
        0.418, 0.447, 0.480, 0.511, 0.540, 0.567, 0.590, 0.614, 0.638,
        0.662, 0.683, 0.701, 0.715, 0.730, 0.744, 0.754, 0.762, 0.771,
        0.779, 0.787, 0.793, 0.798, 0.802, 0.806, 0.809, 0.812, 0.814,
        0.816, 0.818, 0.820, 0.822, 0.823, 0.824, 0.826, 0.827, 0.827,
        0.827, 0.828, 0.828, 0.829, 0.829
    ],
    400: [
        None, None, None, None, None, None, None, None, None, None, None,
        None, 0.412, 0.441, 0.471, 0.497, 0.521, 0.548, 0.574, 0.599,
        0.623, 0.644, 0.662, 0.677, 0.691, 0.704, 0.713, 0.725, 0.733,
        0.742, 0.749, 0.754, 0.758, 0.764, 0.767, 0.769, 0.773, 0.775,
        0.778, 0.780, 0.782, 0.783, 0.784, 0.784, 0.785, 0.786, 0.786,
        0.788, 0.788, 0.789, 0.789
    ],
    450: [
        None, None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, 0.421, 0.445, 0.472, 0.501, 0.529, 0.555,
        0.575, 0.594, 0.613, 0.629, 0.643, 0.654, 0.666, 0.676, 0.686,
        0.694, 0.701, 0.706, 0.712, 0.716, 0.718, 0.722, 0.724, 0.727,
        0.729, 0.731, 0.732, 0.734, 0.735, 0.735, 0.736, 0.736, 0.738,
        0.738, 0.739, 0.739
    ],
    500: [
        None, None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, None, 0.477,
        0.499, 0.520, 0.541, 0.559, 0.574, 0.587, 0.600, 0.610, 0.620,
        0.629, 0.636, 0.643, 0.649, 0.654, 0.658, 0.661, 0.663, 0.666,
        0.668, 0.671, 0.672, 0.674, 0.675, 0.675, 0.676, 0.677, 0.677,
        0.677, 0.678, 0.678
    ],
}


def figure_15_1_cracking_projection_factor(passes, k_existing_psi_in) -> dict:
    """Factor F for projecting cracking in a flexible pavement, UFC 3-250-01
    Figure 15-1 (pdf_page 69, printed 50); returns F (dimensionless, 0.4-1.0).

    F projects the cracking expected in the existing rigid (base) pavement
    during the design life of a flexible overlay; it enters the overlay
    equation 15-4 (printed 49). Read off the printed curves (see the section
    note above; tolerance 0.005 on F), linear in log10(passes) along a curve
    and linear in k between curves.

    Parameters
    ----------
    passes : float
        Design traffic, passes of an 8,164-kg (18-kip) ESAL. Must be at least
        each curve's printed start: 100 for k = 25-100 psi/in, rising to
        about 8,600 for k = 500. Above 10,000,000 (the chart's right edge)
        F is held at its 10,000,000 value, with a note.
    k_existing_psi_in : float
        k-value of the existing rigid pavement, psi/in. Must be within the
        printed curves, 25-500 psi/in.

    Returns
    -------
    dict
        {'passes', 'k_existing_psi_in', 'f', 'chart_read', 'tolerance',
         'reference', 'note'?}.

    Raises
    ------
    ValueError
        If k_existing_psi_in is outside 25-500 psi/in, or passes is below
        where the printed curve (or either curve bracketing k) begins.
    """
    if not (25 <= k_existing_psi_in <= 500):
        raise ValueError(
            f"k_existing_psi_in must be in [25, 500] psi/in (Figure 15-1's "
            f"curves), got {k_existing_psi_in}"
        )
    if passes is None or passes <= 0:
        raise ValueError(f"passes must be > 0, got {passes}")
    log_p = math.log10(passes)
    note = None
    if log_p > 7.0:
        note = (f"{passes:,.0f} passes is beyond Figure 15-1's right edge "
                "(10,000,000); F is held at its 10,000,000-pass value, where "
                "the curves are flat (Appendix G G-7 reads 0.93 for k = 100 "
                "at 20 million passes).")
        log_p = 7.0

    ks = sorted(_FIG_15_1_CURVES)
    lower_k = max(k for k in ks if k <= k_existing_psi_in)
    upper_k = min(k for k in ks if k >= k_existing_psi_in)

    def _on_curve(k):
        start_lp, start_f = _FIG_15_1_START[k]
        if log_p < start_lp - 1e-9:
            return None
        xs, ys = [start_lp], [start_f]
        for x, y in zip(_FIG_15_1_LOG_PASSES, _FIG_15_1_CURVES[k]):
            if y is not None and x > start_lp + 1e-9:
                xs.append(x)
                ys.append(y)
        return _linterp(log_p, xs, ys)

    f_lower = _on_curve(lower_k)
    f_upper = _on_curve(upper_k) if upper_k != lower_k else f_lower
    if f_lower is None or f_upper is None:
        k_short = lower_k if f_lower is None else upper_k
        start = 10 ** _FIG_15_1_START[k_short][0]
        raise ValueError(
            f"passes={passes:g} is below where Figure 15-1's k={k_short} "
            f"curve begins (about {start:,.0f} passes, F "
            f"{_FIG_15_1_START[k_short][1]:.2f}); the chart gives no F there."
        )
    if upper_k == lower_k:
        f = f_lower
    else:
        frac = (k_existing_psi_in - lower_k) / (upper_k - lower_k)
        f = f_lower + frac * (f_upper - f_lower)

    out = {
        "passes": passes, "k_existing_psi_in": k_existing_psi_in,
        "f": round(f, 3), "chart_read": True,
        "tolerance": (
            "read along each printed curve, within 0.005 on F; k = 100 at "
            "10,000,000 passes reads 0.930 (Appendix G G-7: 0.93 at 20 "
            "million)"),
        "reference": "UFC 3-250-01, Figure 15-1 (pdf_page 69, printed 50)",
    }
    if note:
        out["note"] = note
    return out


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
         'reference'}. ``max_spacing_ft`` is capped at 20 ft (the table's
         footnote: the maximum spacing of transverse contraction joints for
         DoD pavements is 20 ft (6.1 m)). Para 16-2.1.3 (same page): in
         regions where the design freezing index is 1,800 or more degree
         days the maximum spacing should be 20 ft (6 m).

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
# printed 70). The rows as printed: frost group, subgroup, kind of soil,
# percentage finer than 0.02 mm by weight, and the typical USCS types.
# Para 19-2 (pdf_page 86, printed 67): "For frost design purposes, soils
# are divided into eight groups as shown in Table 19-2", listed in about the
# order of increasing susceptibility to frost heave.
# ============================================================================

_TABLE_19_2_ROWS = (
    ("NFS", "a", "Gravels, crushed stone, crushed rock", (0.0, 1.5),
     ("GW", "GP")),
    ("NFS", "b", "Sands", (0.0, 3.0), ("SW", "SP")),
    ("PFS", "a", "Gravels, crushed stone, crushed rock", (1.5, 3.0),
     ("GW", "GP")),
    ("PFS", "b", "Sands", (3.0, 10.0), ("SW", "SP")),
    ("S1", "", "Gravelly soils", (3.0, 6.0), ("GW", "GP", "GW-GM", "GP-GM")),
    ("S2", "", "Sandy soils", (3.0, 6.0), ("SW", "SP", "SW-SM", "SP-SM")),
    ("F1", "", "Gravelly soils", (6.0, 10.0), ("GM", "GW-GM", "GP-GM")),
    ("F2", "a", "Gravelly soils", (10.0, 20.0), ("GM", "GW-GM", "GP-GM")),
    ("F2", "b", "Sands", (6.0, 15.0), ("SM", "SW-SM", "SP-SM")),
    ("F3", "a", "Gravelly soils", (20.0, None), ("GM", "GC")),
    ("F3", "b", "Sands, except very fine silty sands", (15.0, None),
     ("SM", "SC")),
    ("F3", "c", "Clays, PI > 12", None, ("CL", "CH")),
    ("F4", "a", "All silts", None, ("ML", "MH")),
    ("F4", "b", "Very fine silty sands", (15.0, None), ("SM",)),
    ("F4", "c", "Clays, PI > 12", None, ("CL", "CL-ML")),
    ("F4", "d", "Varved clays and other fine-grained, banded sediments",
     None, ("CL", "CL-ML")),
)
# Table 20-2 (Chapter 20's drainage table, para 20-3.3.4; pdf_page 124,
# printed 105) prints these dual symbols that Table 19-2 does not. They are
# named in the refusal, never used to classify.
_TABLE_20_2_EXTRA_ROWS = (
    ("F1", "", "Gravelly soils", (6.0, 10.0), ("GW-GC", "GP-GC")),
    ("F2", "a", "Gravelly soils", (10.0, 20.0), ("GM-GC",)),
    ("F2", "b", "Sands", (6.0, 15.0), ("SW-SC", "SP-SC", "SM-SC")),
    ("F3", "a", "Gravelly soils", (20.0, None), ("GM-GC",)),
    ("F3", "b", "Sands, except very fine silty sands", (15.0, None),
     ("SM-SC",)),
    ("F4", "b", "Very fine sands", (15.0, None), ("SM-SC",)),
)
# Table 20-2 writes the dual symbols GC-GM, SC-SM and CL-ML (ASTM D2487
# order) as GM-GC, SM-SC and ML-CL.
_USCS_ORDER_ALIASES = {"GC-GM": "GM-GC", "SC-SM": "SM-SC", "ML-CL": "CL-ML"}
_FROST_GROUPS = ("NFS", "PFS", "S1", "S2", "F1", "F2", "F3", "F4")
_TABLE_19_2_REF = "UFC 3-250-01, Table 19-2 (pdf_page 89, printed 70)"
_TABLE_20_2_REF = "UFC 3-250-01, Table 20-2 (pdf_page 124, printed 105)"
_PARA_19_2_2_REF = "UFC 3-250-01, para 19-2.2 (pdf_page 87, printed 68)"


def _t192_range_text(rng):
    if rng is None:
        return "--"
    lo, hi = rng
    return f"over {lo:g}" if hi is None else f"{lo:g}-{hi:g}"


def _t192_label(row):
    return f"{row[0]} ({row[1]})" if row[1] else row[0]


def table_19_2_frost_classification(uscs_class, finer_than_0_02mm_pct=None,
                                    frost_group=None) -> dict:
    """Frost design soil classification (Table 19-2, Chapter 19; pdf_page 89,
    printed 70), as printed.

    Groups NFS, PFS, S1, S2 and F1-F4. Each row prints a kind of soil, a
    range of percentage finer than 0.02 mm (for the granular soils) and
    the USCS types it covers. A soil the table does not list is refused,
    not given a group: the symbol and percentage must fall in a printed
    row. A printed range "a-b" includes both ends; "Over a" is above a. A
    percentage on an end two rows share (GM at 10 %: F1 6-10 and F2
    10-20) takes the more frost-susceptible row, the later one in the
    table (para 19-2), and names the other.

    Where the print gives more than one row, the first is returned and the
    others are listed in ``also_printed``:

    - SW or SP from 3 to 6 %: PFS (b) (3-10, footnote ***: "requires
      laboratory test to determine frost design soils classification");
      S2 (3-6) also prints SW, SP.
    - SM over 15 %: F4 (b) (very fine silty sands); F3 (b) is "Sands,
      except very fine silty sands". Both take index 3.5 in Table 19-3.
    - CL: F3 (c) "Clays, PI > 12"; F4 (c) also prints "Clays, PI > 12" for
      CL and CL-ML, and F4 (d) varved clays. All take index 3.5.
    - GC at 20 % or less, SC at 15 % or less, or either without a
      percentage: not in a row of the table; para 19-2.2 (pdf_page 87,
      printed 68) says "Occasionally, GC or SC materials may occur within
      the F2 group, although they normally fall into the F3 category", so
      F3 is returned with ``listed_in_table`` False.

    A dual symbol Table 19-2 does not list (GW-GC, GP-GC, GM-GC, SW-SC,
    SP-SC, SM-SC) is refused; the message names the group Table 20-2,
    Chapter 20's drainage table, prints for it. A laboratory frost test
    sets the frost design group (footnote ***), given as ``frost_group``.

    Parameters
    ----------
    uscs_class : str
        USCS soil classification symbol (e.g. 'ML', 'SM', 'GW-GM').
    finer_than_0_02mm_pct : float, optional
        Percentage finer than 0.02 mm by weight. Required for the granular
        symbols (GW, GP, GM, SW, SP, SM and their duals); not used for the
        fine-grained ones (ML, MH, CL, CH, CL-ML).
    frost_group : str, optional
        A frost group set by other means (a laboratory frost test, as
        footnote *** asks for PFS soils, or the Government Civil
        Engineer's classification, para 19-2.4, pdf_page 89, printed 70).
        When given it is returned as the group, with a note; the table is
        not consulted.

    Returns
    -------
    dict
        {'uscs_class', 'finer_0_02mm_pct', 'frost_group', 'subgroup',
         'description', 'listed_in_table', 'also_printed', 'reference',
         'note'?}.

    Raises
    ------
    ValueError
        If the symbol is not in Table 19-2 (e.g. OL, OH, PT, GW-GC), the
        percentage is needed but not given, or the symbol and percentage
        fall in no printed row (e.g. GW over 6 %, SM under 6 %).
    """
    if frost_group is not None:
        g = str(frost_group).strip().upper()
        if g not in _FROST_GROUPS:
            raise ValueError(
                f"Unknown frost_group '{frost_group}'. Valid: "
                f"{', '.join(_FROST_GROUPS)}."
            )
        return {
            "uscs_class": str(uscs_class).strip().upper(),
            "finer_0_02mm_pct": finer_than_0_02mm_pct,
            "frost_group": g, "subgroup": "",
            "description": f"frost group {g}, given",
            "listed_in_table": None, "also_printed": [],
            "note": ("Frost group given by the caller (e.g. set by a "
                     "laboratory frost test, Table 19-2 footnote ***); "
                     "Table 19-2 was not consulted."),
            "reference": _TABLE_19_2_REF,
        }

    lab = ("A laboratory frost test sets the frost design group (Table 19-2 "
           "footnote ***); give it as frost_group.")
    sym = str(uscs_class).strip().upper().replace(" ", "")
    sym = _USCS_ORDER_ALIASES.get(sym, sym)
    rows = [r for r in _TABLE_19_2_ROWS if sym in r[4]]
    if not rows:
        drainage = [r for r in _TABLE_20_2_EXTRA_ROWS if sym in r[4]]
        if drainage:
            printed = "; ".join(f"{_t192_label(r)} ({r[2]}, "
                                f"{_t192_range_text(r[3])} %)"
                                for r in drainage)
            raise ValueError(
                f"Table 19-2, the frost design table (para 19-2), does not "
                f"list {sym}. Table 20-2, Chapter 20's drainage table (para "
                f"20-3.3.4, pdf_page 124, printed 105), prints it under "
                f"{printed}, but it is not the frost design "
                f"classification. {lab}"
            )
        listed = sorted({s for r in _TABLE_19_2_ROWS for s in r[4]}
                        | {"GC", "SC"})
        raise ValueError(
            f"Table 19-2 lists no frost group for '{uscs_class}' (it lists "
            f"{', '.join(listed)}). {lab}"
        )
    fines = finer_than_0_02mm_pct
    base = {"uscs_class": sym, "finer_0_02mm_pct": fines,
            "reference": _TABLE_19_2_REF}

    if all(r[3] is None for r in rows):        # fine-grained: no fines range
        first, others = rows[0], rows[1:]
        out = dict(base, frost_group=first[0], subgroup=first[1],
                   description=f"{first[2]} -- {', '.join(first[4])}",
                   listed_in_table=True,
                   also_printed=[_t192_label(r) for r in others])
        if others:
            out["note"] = (
                f"Table 19-2 also prints {sym} under "
                + "; ".join(f"{_t192_label(r)} ({r[2]})" for r in others)
                + "; F3 and F4 both take index 3.5 in Table 19-3.")
        return out

    def _gc_sc_f3(why):
        return dict(base, frost_group="F3", subgroup="",
                    description=(f"{sym}: normally F3 (para 19-2.2); not in "
                                 "a row of Table 19-2 at this percentage"),
                    listed_in_table=False, also_printed=["F2"],
                    note=(f"{why} Para 19-2.2 (pdf_page 87, printed 68): "
                          "\"Occasionally, GC or SC materials may occur "
                          "within the F2 group, although they normally fall "
                          "into the F3 category.\" F3 is returned. "
                          "(Table 20-2, Chapter 20's drainage table, prints "
                          "GC at 10-20 % and SC at 6-15 % under F2.) " + lab),
                    reference=f"{_TABLE_19_2_REF}; {_PARA_19_2_2_REF}")

    if fines is None:
        if sym in ("GC", "SC"):
            return _gc_sc_f3(
                f"No percentage finer than 0.02 mm given for {sym}.")
        raise ValueError(
            f"Table 19-2 sets the frost group of {sym} by the percentage "
            "finer than 0.02 mm by weight; give finer_than_0_02mm_pct."
        )
    if fines < 0 or fines > 100:
        raise ValueError(
            f"finer_than_0_02mm_pct must be 0-100, got {fines}")

    def _in(rng):
        lo, hi = rng
        return fines > lo if hi is None else lo <= fines <= hi

    hits = [r for r in rows if r[3] is not None and _in(r[3])]
    if not hits:
        if sym in ("GC", "SC"):
            return _gc_sc_f3(
                f"Table 19-2 lists {sym} only "
                + "; ".join(f"{_t192_range_text(r[3])} % ({_t192_label(r)})"
                            for r in rows) + f"; {fines:g} % given.")
        printed = "; ".join(
            f"{_t192_label(r)} {_t192_range_text(r[3])} %" for r in rows)
        raise ValueError(
            f"Table 19-2 has no row for {sym} with {fines:g} % finer than "
            f"0.02 mm (it prints {sym} at: {printed}). {lab}"
        )
    # A row ending where another starts gives way to the later, more
    # frost-susceptible row (para 19-2's order).
    ended = [r for r in hits if r[3][1] == fines
             and any(o[3][0] == fines for o in hits)]
    hits = [r for r in hits if r not in ended]
    if len(hits) > 1 and sym == "SM":
        hits.sort(key=lambda r: r[0] != "F4")     # F4 (b) first
    first, others = hits[0], hits[1:]
    out = dict(base, frost_group=first[0], subgroup=first[1],
               description=(f"{first[2]}, {_t192_range_text(first[3])} % "
                            f"finer than 0.02 mm -- {', '.join(first[4])}"),
               listed_in_table=True,
               also_printed=[_t192_label(r) for r in others + ended])
    notes = []
    if others:
        notes.append(
            f"Table 19-2 also prints {sym} at {fines:g} % under "
            + "; ".join(f"{_t192_label(r)} ({r[2]}, "
                        f"{_t192_range_text(r[3])} %)" for r in others)
            + ".")
    if ended:
        notes.append(
            f"{fines:g} % is an end two rows share: {_t192_label(first)} "
            f"({_t192_range_text(first[3])} %), the more frost-susceptible, "
            "is returned; Table 19-2's "
            + " and ".join(f"{_t192_range_text(r[3])} % row gives "
                           f"{_t192_label(r)}" for r in ended)
            + ".")
    if first[0] == "PFS":
        notes.append("Footnote ***: PFS soils require a laboratory test to "
                     "determine the frost design soils classification.")
    if (first[0], first[1]) == ("F4", "b"):
        notes.append("F4 (b) is for very fine silty sands; both take index "
                     "3.5 in Table 19-3.")
    if notes:
        out["note"] = " ".join(notes)
    return out


# ============================================================================
# Table 19-3: Frost-Area Soil Support Indexes for Subgrade Soils, Flexible
# Pavement Design (Chapter 19, pdf_page 99, printed 80)
# ============================================================================

def table_19_3_frost_support_index(frost_group) -> dict:
    """Frost-area soil support index for flexible pavement design
    (Table 19-3, Chapter 19; pdf_page 99, printed 80).

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
        "reference": "UFC 3-250-01, Table 19-3 (pdf_page 99, printed 80)",
    }


# ============================================================================
# Figure 19-5: Design Depth of Non-frost Susceptible Base for Limited
# Subgrade Frost Penetration (Chapter 19, pdf_page 98, printed 79)
#
# Para 19-5.3 (printed 74-75): c = a - p; r = water content of subgrade /
# water content of base; "Enter Figure 19-5 with C as the abscissa and, at
# the applicable value of r, find on the left scale the design base
# thickness b that will result in the allowable subgrade frost penetration
# shown on the right scale. If r is greater than 3.0 use 3.0." The right
# scale (s, 0-18 in) spans the same height as the left (b, 0-72 in), so
# s = b/4.
#
# CHART READ (GM-303, 2026-11-02): the ten drawn r lines (0.6 to 3.0) were
# tracked on a 300 dpi render from c = 4-11 in to c = 76 in (1,070-1,290
# points each; the axes from their ticks) and each fitted as a straight
# line b = m*c + q: residual 0.07-0.11 in rms, under 0.4 in at worst, and
# no line bends more than 0.14 in over its length. The drawn lines meet
# the c axis near c = 1 in rather than at the origin, so each keeps its
# own intercept. Between drawn lines b is linear in r.
#
# Checked against the three printed reads: the figure's own example (c =
# 32 in, r = 2.0 -> "B = 21", "S = 5.2"; read 21.1 and 5.3) and G-8.11
# (pdf_page 286, printed 267: r = 3, c = 38.5 -> b = 22 in, "about 5.5 in"
# into the subgrade; read 21.8 and 5.4). G-8.9 (same page: r = 3, c = 42)
# prints b = 26 in with "about 6 in" into the subgrade; the r = 3.0 line
# reads 23.8 in and s 5.9 in, and 26 in would give s = 6.5 in, so the
# printed 26 is not on the drawn line.
# ============================================================================

# r: (m, q) of the drawn line b = m*c + q, inches
_FIG_19_5_LINES = {
    0.6: (0.8861, -0.537), 0.8: (0.8543, -0.760), 1.0: (0.8207, -0.907),
    1.2: (0.7894, -0.988), 1.4: (0.7543, -0.727), 1.6: (0.7333, -0.914),
    1.8: (0.7041, -0.679), 2.0: (0.6781, -0.562), 2.5: (0.6207, -0.458),
    3.0: (0.5798, -0.561),
}
_FIG_19_5_C_MAX = 80.0   # the chart's right frame


def figure_19_5_design_base_thickness(c_in, r) -> dict:
    """Design NFS base thickness for the limited subgrade frost penetration
    method (Figure 19-5, Chapter 19; pdf_page 98, printed 79), read off the
    drawn r lines (see the section note above).

        b = m(r) * c + q(r)  (each drawn line);  s = b / 4

    Parameters
    ----------
    c_in : float
        Base thickness for zero frost penetration into the subgrade,
        inches (c = a - p: frost penetration depth less pavement
        thickness), 0 < c <= 80 (the chart's c axis).
    r : float
        Ratio of subgrade water content to base water content, 0.6 or
        more (the lowest drawn line). Above 3.0 the 3.0 line is used, as
        para 19-5.3 instructs; between drawn lines b is linear in r.

    Returns
    -------
    dict
        {'c_in', 'r', 'r_used', 'b_in', 's_in', 'chart_read', 'method',
         'reference', 'note'?}.

    Raises
    ------
    ValueError
        If c_in is not in (0, 80] or r is below 0.6.
    """
    if c_in is None or c_in <= 0:
        raise ValueError(f"c_in must be > 0, got {c_in}")
    if c_in > _FIG_19_5_C_MAX:
        raise ValueError(
            f"c_in {c_in:g} in is past Figure 19-5's c axis (0-80 in).")
    rs = sorted(_FIG_19_5_LINES)
    if r is None or r < rs[0]:
        raise ValueError(
            f"r={r} is below Figure 19-5's lowest drawn line (r = 0.6).")
    note = None
    r_used = r
    if r > rs[-1]:
        r_used = rs[-1]
        note = (f"r = {r:g} is greater than 3.0; the 3.0 line is used (para "
                "19-5.3, printed 75).")

    def b_on(rr):
        m, q = _FIG_19_5_LINES[rr]
        return max(0.0, m * c_in + q)
    lo = max(x for x in rs if x <= r_used)
    hi = min(x for x in rs if x >= r_used)
    b = b_on(lo) if hi == lo else (
        b_on(lo) + (b_on(hi) - b_on(lo)) * (r_used - lo) / (hi - lo))
    out = {
        "c_in": c_in, "r": r, "r_used": r_used,
        "b_in": round(b, 1), "s_in": round(b / 4.0, 1),
        "chart_read": True,
        "method": ("the drawn r lines read off the print (straight-line "
                   "fits, 0.07-0.11 in rms); linear in r between lines"),
        "reference": "UFC 3-250-01, Figure 19-5 (pdf_page 98, printed 79)",
    }
    if note:
        out["note"] = note
    return out


# ============================================================================
# Figure 19-6: Frost-Area Index of Reaction for Design of Rigid Roads and
# Parking Areas (Chapter 19, pdf_page 101, printed 82)
#
# Three straight lines (F1 and S1, F2 and S2, F3 and F4) of frost-area
# index of reaction (psi/in, left scale; MN/m2/m on the right) against
# thickness of base (in, 0-50; meters on the top scale), each starting at
# the dashed "102 mm (4 inches) Min. Base Thickness" line.
#
# CHART READ (GM-303, 2026-11-02): each line tracked on a 300 dpi render
# from 3.9 in to where it leaves the chart (950-1,340 points; the axes from
# the frame, which the 5 in gridlines confirm within 0.08 in) and fitted as
# k = m*t + q: residual 0.2-0.3 psi/in rms, under 1.5 at worst. F1 and S1
# leaves through the top (400 psi/in) at 36.5 in, F2 and S2 at 49.8 in.
# Checked against G-8.12 (pdf_page 287, printed 268): F3 and F4 under 8 in
# of base -> 50 psi/in (read 49.5).
# ============================================================================

# group: (m, q, t_max) of the drawn line k = m*t + q (psi/in; t in inches)
_FIG_19_6_LINES = {
    "F1_S1": (10.8113, 4.921, 36.5),
    "F2_S2": (7.9859, 2.301, 49.8),
    "F3_F4": (5.8902, 2.424, 50.0),
}
_FIG_19_6_GROUPS = {"F1": "F1_S1", "S1": "F1_S1", "F2": "F2_S2",
                    "S2": "F2_S2", "F3": "F3_F4", "F4": "F3_F4"}
_FIG_19_6_T_MIN = 4.0


def figure_19_6_frost_area_index_of_reaction(base_thickness_in, frost_group) -> dict:
    """Frost-area index of reaction for rigid pavement design in frost areas
    (Figure 19-6, Chapter 19; pdf_page 101, printed 82), read off the three
    drawn lines (see the section note above). Para 19-6.2 (printed 81): used
    "as if they were moduli of reaction, k, and have the same units".

    Parameters
    ----------
    base_thickness_in : float
        Thickness of base, inches, from the 4 in minimum the figure marks
        to where the group's line leaves the chart (36.5 in for F1 and S1,
        49.8 for F2 and S2, 50 for F3 and F4).
    frost_group : str
        'F1_S1', 'F2_S2' or 'F3_F4' (one line each), or one group: 'F1',
        'S1', 'F2', 'S2', 'F3', 'F4'.

    Returns
    -------
    dict
        {'base_thickness_in', 'frost_group', 'index_of_reaction_psi_in',
         'index_of_reaction_kPa_mm', 'chart_read', 'reference'}.

    Raises
    ------
    ValueError
        If frost_group is not one of those, or the thickness is below 4 in
        or past the end of the group's line.
    """
    g = str(frost_group).strip().upper().replace(" AND ", "_").replace("&", "_")
    g = _FIG_19_6_GROUPS.get(g, g)
    if g not in _FIG_19_6_LINES:
        raise ValueError(
            f"Unknown frost_group {frost_group!r}. Valid: F1_S1, F2_S2, "
            "F3_F4 (or F1, S1, F2, S2, F3, F4).")
    m, q, t_max = _FIG_19_6_LINES[g]
    t = base_thickness_in
    if t is None or t < _FIG_19_6_T_MIN:
        raise ValueError(
            f"base_thickness_in {t} is below the 4 in minimum base "
            "thickness Figure 19-6 marks.")
    if t > t_max:
        raise ValueError(
            f"base_thickness_in {t:g} is past where Figure 19-6's {g} line "
            f"leaves the chart ({t_max:g} in).")
    k = m * t + q
    return {
        "base_thickness_in": base_thickness_in, "frost_group": g,
        "index_of_reaction_psi_in": round(k, 1),
        "index_of_reaction_kPa_mm": round(k * 0.271, 1),
        "chart_read": True,
        "reference": (
            "UFC 3-250-01, Figure 19-6 (pdf_page 101, printed 82); checked "
            "against Appendix G, G-8.12 (pdf_page 287, printed 268)"
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
# design curve used throughout the guide's own worked examples.
#
# CHART READ off the printed curves (REF-58, from the GM-298 read of
# 2026-10-31): the chart is a raster embedded in the PDF (520 x 664 px; CBR
# 1, 10 and 100 at x = 48, 276 and 504; 0 and 30 in at y = 598 and 28, 19
# px per inch). Each of the eight curves (10 to 10,000,000 passes) was
# followed along its length from the left frame, the curve-number labels
# bridged, then smoothed over three samples and thinned to the points
# below (0.5 px tolerance). Each curve runs from CBR 1 to the CBR where it
# meets the axis; thickness is linear in log(CBR) between points and
# linear in log(passes) between curves.
#
# Checked against every Figure E-1 read printed in Appendix G: G-1
# (pdf_page 275, printed 256) CBR 3 at 1,000,000 passes 16.4 in (read
# 16.4) and CBR 4 at 1,395,400 passes 14 in (13.9); G-3 (pdf_pages
# 277-279, printed 258-260) at 5,000,000 passes CBR 10 7.8 in (7.8), CBR 7
# 9.8 (9.8), CBR 4 14.5 (14.5), CBR 25 3.4 (3.4). G-8.10 (pdf_page 286,
# printed 267) says CBR 3.5 at 1,200,000 passes gives 16 in; the curves
# give 15.1 there.
# ============================================================================

# passes -> ((CBR, thickness in), ...) along the printed curve, CBR 1 to
# the axis.
_FIG_E1 = {
    10_000_000: ((1, 30.00), (1.1, 29.03), (1.28, 27.01), (1.69, 23.73),
                 (2.66, 18.79), (3.85, 15.22), (5.54, 11.90), (6.41, 10.68),
                 (7.34, 9.72), (9.41, 8.31), (13.9, 6.33), (24.9, 3.63),
                 (29, 2.75), (31.4, 2.16), (33.3, 1.51), (34.5, 0.80),
                 (34.7, 0.00)),
    1_000_000: ((1, 28.59), (1.24, 25.80), (1.42, 24.26), (1.65, 22.53),
                (2.19, 19.52), (2.72, 17.44), (3.15, 15.94), (3.94, 13.86),
                (5.63, 10.79), (6.41, 9.82), (8.48, 8.23), (10.6, 7.06),
                (20.3, 4.06), (24.7, 3.06), (27.7, 2.32), (29, 1.91),
                (30.1, 1.48), (31.2, 0.78), (31.5, 0.00)),
    100_000: ((1, 26.55), (1.1, 25.36), (1.49, 21.89), (2.07, 18.48),
              (3.6, 13.26), (4.47, 11.42), (5.5, 9.83), (6.8, 8.58),
              (9.76, 6.75), (20.7, 3.26), (22.6, 2.71), (25.2, 1.95),
              (26.7, 1.29), (27.3, 0.82), (27.6, 0.00)),
    10_000: ((1, 23.92), (1.1, 22.79), (1.24, 21.50), (1.55, 19.16),
             (1.81, 17.69), (2.88, 13.32), (3.96, 10.68), (4.81, 9.34),
             (6.4, 7.78), (8.94, 6.17), (15.1, 3.83), (17.8, 3.01),
             (18.9, 2.65), (20.5, 2.08), (21.9, 1.46), (22.7, 0.76),
             (23, 0.00)),
    1_000: ((1, 20.51), (1.29, 18.03), (1.92, 14.29), (2.31, 12.65),
            (3.12, 10.24), (3.6, 9.30), (4.19, 8.42), (4.93, 7.58),
            (7.16, 5.84), (11.7, 3.69), (14.2, 2.70), (15.6, 2.16),
            (17.1, 1.33), (17.5, 0.88), (17.9, 0.00)),
    100: ((1, 15.89), (1.31, 13.49), (1.42, 12.65), (1.89, 10.49),
          (2.17, 9.53), (2.78, 8.12), (3.28, 7.30), (4.17, 6.17),
          (7.61, 3.60), (9.62, 2.46), (10.5, 1.92), (11.3, 1.31),
          (11.7, 0.86), (11.9, 0.00)),
    50: ((1, 14.16), (1.41, 11.22), (1.76, 9.68), (1.98, 8.94), (2.56, 7.59),
         (3.02, 6.77), (6.85, 3.27), (7.58, 2.79), (8.6, 2.10), (9.32, 1.52),
         (9.75, 1.10), (10, 0.64), (10.1, 0.00)),
    10: ((1, 9.25), (1.42, 7.40), (2.24, 5.41), (4, 3.08), (4.73, 2.27),
         (5.36, 1.56), (5.64, 1.16), (5.84, 0.72), (6.01, 0.00)),
}
_FIG_E1_PASSES = sorted(_FIG_E1)


def _fig_e1_on_curve(passes, cbr):
    pts = _FIG_E1[passes]
    if cbr >= pts[-1][0]:
        return 0.0
    return _linterp(math.log10(cbr), [math.log10(p[0]) for p in pts],
                    [p[1] for p in pts])


def figure_e1_flexible_thickness(cbr, passes) -> dict:
    """Required thickness of cover (in) above a layer of this CBR, for an
    18,000-lb single-axle dual-tire ESAL (Figure E-1, Appendix E; pdf_page
    211, printed 192), read along the printed curves (see the section note
    above).

    Reproduces every Appendix G read of the chart: (CBR 3, 1,000,000) ->
    16.4 in and (CBR 4, 1,395,400) -> 14 in (G-1); at 5,000,000 passes CBR
    10 / 7 / 4 / 25 -> 7.8 / 9.8 / 14.5 / 3.4 in (G-3).

    Parameters
    ----------
    cbr : float
        Subgrade (or frost-area soil support index, Table 19-3) CBR, >= 1
        (the chart's CBR axis runs 1-100). Past the CBR where a curve
        meets the axis the thickness is 0.0 (no cover needed over that
        layer).
    passes : float
        Design passes of an 18,000-lb (8,200-kg) single-axle, dual-tire
        ESAL, 10-10,000,000 (the printed curves). Between curves the
        thickness is linear in log(passes).

    Returns
    -------
    dict
        {'cbr', 'passes', 'thickness_in', 'chart_read', 'tolerance',
         'reference', 'note'?}.

    Raises
    ------
    ValueError
        If cbr is below 1, or passes is outside 10-10,000,000.
    """
    if cbr is None or cbr < 1.0:
        raise ValueError(
            f"CBR {cbr} is below Figure E-1's CBR axis (1-100)."
        )
    if passes is None or not 10 * (1 - 1e-9) <= passes <= 1e7 * (1 + 1e-9):
        raise ValueError(
            f"{passes} passes is outside Figure E-1's curves (10 to "
            "10,000,000 passes of the 18-kip single axle)."
        )
    p = min(max(passes, 10), 10_000_000)
    hi = next(n for n in _FIG_E1_PASSES if n >= p)
    lo = max(n for n in _FIG_E1_PASSES if n <= p)
    t_hi = _fig_e1_on_curve(hi, cbr)
    if hi == lo:
        thickness = t_hi
    else:
        t_lo = _fig_e1_on_curve(lo, cbr)
        f = ((math.log10(p) - math.log10(lo))
             / (math.log10(hi) - math.log10(lo)))
        thickness = t_lo + f * (t_hi - t_lo)
    out = {
        "cbr": cbr, "passes": passes, "thickness_in": round(thickness, 1),
        "chart_read": True,
        "tolerance": (
            "read along each printed curve (about 0.05 in a pixel); every "
            "Appendix G read of it (G-1, G-3) reproduced within 0.1 in; "
            "interpolated in log(passes) between curves"),
        "reference": "UFC 3-250-01, Figure E-1 (pdf_page 211, printed 192)",
    }
    if thickness <= 0.0:
        out["note"] = (
            f"CBR {cbr} is past the end of the curves for {passes:g} passes "
            "(where they meet the axis): no cover is needed over this layer "
            "by Figure E-1; Table 7-2's minimum thicknesses still apply.")
    return out


# ============================================================================
# Figures E-2 to E-31: the flexible design curves of the thirty vehicles in
# Appendix E (pdf_page 210 + N for Figure E-N, printed 191 + N). Each chart
# gives the thickness of cover above a layer of a given CBR for four or
# five pass levels of one vehicle, on a log CBR axis from 1 to 100, and
# prints its own curve legend and gross weight.
#
# How they were read (GM-303, 2026-11-02; replaces the 15-point grids of
# df136bf): every chart is a raster embedded in the PDF (about 520 x 600
# px). The plot frame and gridlines were found from the pixels (CBR 1 and
# 100 at the left and right frame, CBR 10 at the middle gridline; zero and
# the chart's top value at the bottom and top frame). Each curve was
# followed along lines x + y = constant, so a steep and a flat stretch each
# cross every scan line once; the piece above each curve-number label was
# matched to its curve by order, the label gaps bridged straight, the
# points smoothed over five samples and thinned to the points below
# (0.5 px). Each end was followed on the ink, by the centre of the stroke,
# to where it meets the frame or the axis (the left frame's tick marks
# avoided), and the five E-30 curves stop 2 in above the axis as printed.
# Every curve was drawn back over its chart and checked by eye; read
# against the ink column by column, the median offset is 0.12-0.19 px and
# 95 % lie within 0.74 px on every chart, more only across the label gaps.
# Between curves the thickness is interpolated in log(passes).
#
# The grids these replace sampled each curve at 15 CBR values: where a
# curve bends down to the axis they read 2-6 in where the chart is at
# zero, and near CBR 1 up to 9.5 in thin (Figures E-4, E-5); Figures E-16
# and E-30, whose curves start at the top frame at CBR 2 to 6, were off
# throughout (up to 7 and 11 in thin), and Figure E-15's frame top is 15 in
# (the 14 in gridline sits below it), not 14.
#
# Checked against Appendix G, Table G-1 (pdf_page 276, printed 257), at
# CBR 3: the 5-axle truck at 100,000 passes reads 15.6 in (printed 15.8),
# the 3-axle truck at 500,000 reads 12.7 (12.8), the passenger car at
# 20,000,000 reads 6.1 by extrapolating past its 10,000,000 curve (6.1; the
# curve itself is at 6.0); at 16.4 in the 5-axle truck's allowable passes
# read 337,788 (printed 252,915; 312,351 to 365,297 for 16.35 to 16.45 in).
# Appendix G opens (printed 256): "Solutions of the problems using PCASE
# software differ slightly from the solutions determined through the use
# of the pavement design charts."
#
# Figure E-10: the List of Figures and the caption print "M113A1"; the
# chart's own title prints "M113A3". The key is version-neutral.
# ============================================================================

_FIGURES_E = {
    "E-2": {
        "key": "passenger_car",
        "caption": "Passenger Car",
        "gross_weight_lb": 3000, "y_max_in": 10,
        "curves": {
            10_000_000: ((1.031, 10.00), (1.32, 8.94), (1.573, 8.23),
                (2.189, 7.02), (2.551, 6.51), (4.031, 5.07), (7.972, 3.12),
                (9.664, 2.52), (11.22, 2.02), (12.94, 1.37), (13.81, 0.96),
                (14.32, 0.52), (14.7, 0.00)),
            1_000_000: ((1, 9.58), (1.149, 8.98), (1.375, 8.27), (1.933, 7.02),
                (1.98, 6.97), (2.332, 6.40), (3.623, 5.03), (7.89, 2.80),
                (9.877, 2.07), (11.43, 1.45), (12.32, 1.02), (12.78, 0.65),
                (13.25, 0.00)),
            100_000: ((1, 8.89), (1.19, 8.20), (1.606, 7.10), (2.03, 6.31),
                (3.017, 5.09), (6.329, 3.00), (7.777, 2.37), (8.906, 1.90),
                (9.846, 1.48), (10.63, 1.07), (11.06, 0.74), (11.59, 0.00)),
            10_000: ((1, 8.00), (1.347, 6.93), (1.913, 5.79), (2.868, 4.60),
                (4.902, 3.12), (6.148, 2.45), (6.99, 2.04), (7.964, 1.54),
                (8.878, 0.98), (9.177, 0.69), (9.608, 0.00)),
        },
    },
    "E-3": {
        "key": "light_strike_vehicle",
        "caption": "Light Strike Vehicle",
        "gross_weight_lb": 4994, "y_max_in": 10,
        "curves": {
            5_000_000: ((1.499, 10.00), (2.146, 8.44), (3.112, 7.02),
                (4.031, 6.11), (4.762, 5.56), (9.979, 3.23), (12.91, 2.30),
                (14.2, 1.86), (15.11, 1.52), (15.96, 1.13), (16.55, 0.76),
                (17.16, 0.00)),
            1_000_000: ((1.379, 10.00), (1.704, 9.06), (2.015, 8.37),
                (2.865, 7.02), (2.973, 6.92), (3.315, 6.51), (4.424, 5.54),
                (8.906, 3.36), (10.72, 2.73), (12.26, 2.22), (12.97, 1.98),
                (13.98, 1.59), (15.17, 1.02), (15.6, 0.69), (16.13, 0.00)),
            100_000: ((1.187, 10.00), (1.429, 9.18), (1.727, 8.39),
                (2.015, 7.78), (2.723, 6.68), (4.06, 5.35), (8.633, 3.00),
                (10.72, 2.22), (11.37, 1.97), (12.38, 1.54), (13.25, 1.07),
                (13.74, 0.70), (14.25, 0.00)),
            10_000: ((1, 9.83), (1.361, 8.50), (2.013, 7.00), (3.039, 5.61),
                (6.542, 3.25), (7.539, 2.79), (8.906, 2.20), (10.25, 1.55),
                (11.07, 1.07), (11.51, 0.66), (11.95, 0.00)),
            1_000: ((1, 8.58), (1.404, 7.27), (2.009, 6.03), (3.017, 4.75),
                (4.953, 3.27), (6.323, 2.48), (6.947, 2.15), (7.997, 1.53),
                (8.759, 0.98), (8.915, 0.84), (9.419, 0.00)),
        },
    },
    "E-4": {
        "key": "m1a1_main_tank",
        "caption": "M1A1 Main Tank",
        "gross_weight_lb": 126000, "y_max_in": 50,
        "curves": {
            10_000_000: ((1.381, 50.00), (1.646, 42.36), (1.839, 38.14),
                (2.005, 35.04), (2.457, 28.85), (2.995, 23.97), (3.424, 21.19),
                (3.886, 18.92), (4.585, 16.34), (6.1, 12.46), (6.679, 11.48),
                (7.251, 10.80), (8.619, 9.60), (10.15, 8.61), (12.13, 7.65),
                (15.62, 6.42), (28.3, 3.81), (31.77, 3.24), (35.83, 2.52),
                (39.56, 1.70), (40.92, 1.25), (41.68, 0.80), (42.12, 0.00)),
            1_000_000: ((1.256, 50.00), (1.42, 44.54), (1.58, 40.28),
                (1.831, 34.98), (2.172, 29.70), (2.465, 26.38), (3.014, 21.85),
                (3.314, 20.05), (4.228, 16.17), (5.775, 12.06), (6.526, 10.89),
                (6.952, 10.42), (8.896, 8.84), (11.5, 7.46), (19.26, 5.09),
                (26.56, 3.71), (33.63, 2.42), (36.36, 1.80), (38.01, 1.25),
                (38.68, 0.79), (39.14, 0.00)),
            100_000: ((1.119, 50.00), (1.252, 45.01), (1.407, 40.28),
                (1.704, 33.58), (2.007, 28.70), (2.385, 24.35), (2.541, 23.06),
                (2.961, 20.08), (3.248, 18.45), (3.765, 16.17), (4.57, 13.56),
                (4.848, 12.90), (4.978, 12.43), (5.342, 11.65), (6.075, 10.53),
                (7.619, 9.06), (9.885, 7.61), (14.05, 5.95), (24.67, 3.52),
                (28.9, 2.67), (31.97, 1.97), (33.28, 1.57), (34.81, 0.78),
                (35.24, 0.00)),
            10_000: ((1, 48.41), (1.163, 41.98), (1.331, 36.94),
                (1.518, 32.54), (1.806, 27.57), (1.992, 25.13), (2.365, 21.47),
                (2.853, 18.13), (3.464, 15.24), (4.58, 11.69), (5.025, 10.81),
                (5.513, 10.13), (7.313, 8.41), (9.417, 7.08), (14.64, 5.09),
                (19.8, 3.82), (24.16, 2.86), (27.36, 2.08), (29.24, 1.45),
                (30.32, 0.77), (30.71, 0.00)),
            1_000: ((1, 39.75), (1.16, 34.48), (1.296, 31.02), (1.478, 27.38),
                (1.703, 24.01), (1.998, 20.71), (2.223, 18.83), (2.803, 15.32),
                (3.519, 12.35), (3.865, 11.30), (4.192, 10.61), (4.808, 9.66),
                (6.113, 8.22), (9.019, 6.32), (19.16, 3.05), (21.83, 2.33),
                (23.75, 1.67), (24.99, 1.08), (25.68, 0.00)),
        },
    },
    "E-5": {
        "key": "m1a2_main_tank",
        "caption": "M1A2 Main Tank",
        "gross_weight_lb": 139000, "y_max_in": 50,
        "curves": {
            10_000_000: ((1.551, 50.00), (1.772, 44.06), (1.827, 43.05),
                (1.996, 39.26), (2.251, 35.04), (2.753, 28.89), (3.024, 26.42),
                (3.648, 22.23), (4.41, 18.73), (4.983, 16.80), (6.017, 14.14),
                (6.974, 12.24), (8.057, 10.89), (10.06, 9.38), (13.01, 7.91),
                (18.58, 6.18), (31.77, 3.81), (39.98, 2.56), (43.4, 1.87),
                (44.99, 1.44), (46.32, 0.80), (46.77, 0.00)),
            1_000_000: ((1.411, 50.00), (1.595, 44.54), (1.839, 38.90),
                (2.047, 35.04), (2.533, 28.62), (2.995, 24.44), (3.497, 21.19),
                (3.981, 18.85), (4.797, 15.98), (6.464, 12.04), (7.492, 10.71),
                (9.019, 9.44), (11.75, 7.94), (17.35, 6.04), (29.54, 3.72),
                (37.1, 2.45), (39.48, 1.97), (41.48, 1.37), (42.57, 0.80),
                (43.01, 0.00)),
            100_000: ((1.256, 50.00), (1.451, 43.68), (1.735, 36.87),
                (2.005, 32.01), (2.172, 29.70), (2.517, 25.81), (3.014, 21.85),
                (3.534, 18.92), (4.272, 15.98), (5.757, 12.04), (6.336, 11.10),
                (7.145, 10.19), (9.658, 8.35), (11.71, 7.34), (17.06, 5.61),
                (17.83, 5.34), (20.3, 4.88), (29.54, 3.15), (34.1, 2.26),
                (36.32, 1.70), (37.97, 1.05), (38.73, 0.00)),
            10_000: ((1.167, 50.00), (1.319, 44.54), (1.508, 39.11),
                (1.759, 33.86), (1.996, 29.98), (2.401, 25.20), (2.773, 22.05),
                (3.248, 19.11), (3.985, 15.93), (5.404, 11.94), (5.824, 11.19),
                (6.637, 10.19), (8.032, 8.97), (10.02, 7.74), (16.64, 5.38),
                (17.91, 5.08), (18.72, 5.02), (20.32, 4.53), (28.96, 2.88),
                (33.07, 1.99), (34.82, 1.41), (35.93, 0.79), (36.38, 0.00)),
            1_000: ((1, 48.88), (1.227, 40.28), (1.502, 33.30), (1.695, 29.65),
                (1.994, 25.43), (2.319, 22.14), (2.773, 18.83), (3.318, 16.08),
                (4.513, 12.03), (5.062, 10.88), (5.461, 10.33), (6.081, 9.59),
                (7.313, 8.50), (9.417, 7.18), (14.96, 5.09), (19.8, 3.91),
                (24.67, 2.86), (27.62, 2.17), (29.45, 1.61), (30.86, 0.87),
                (31.37, 0.00)),
        },
    },
    "E-6": {
        "key": "m2a3_bradley",
        "caption": "M2A3 Bradley Vehicle Tracked",
        "gross_weight_lb": 58200, "y_max_in": 30,
        "curves": {
            10_000_000: ((1.034, 30.00), (1.148, 27.85), (1.276, 25.91),
                (1.518, 23.10), (1.685, 21.68), (2.05, 19.32), (2.368, 17.83),
                (2.863, 16.12), (3.29, 15.00), (4.331, 13.07), (5.121, 12.05),
                (6.191, 10.97), (8.229, 9.55), (12.96, 7.56), (18.6, 6.16),
                (35.83, 3.73), (43.5, 2.90), (49.36, 2.22), (51.59, 1.89),
                (54.79, 1.13), (56.97, 0.00)),
            1_000_000: ((1, 28.68), (1.13, 26.34), (1.31, 23.84),
                (1.534, 21.62), (1.708, 20.27), (1.998, 18.54), (2.319, 17.09),
                (2.696, 15.80), (3.395, 14.03), (4.019, 12.90), (4.988, 11.62),
                (6.672, 10.06), (8.404, 8.98), (12.95, 7.16), (32.59, 3.73),
                (36.75, 3.24), (43.04, 2.50), (46.29, 2.04), (48.58, 1.62),
                (51.32, 0.72), (52.36, 0.00)),
            100_000: ((1, 26.09), (1.069, 24.89), (1.204, 23.05),
                (1.395, 21.06), (1.553, 19.76), (1.795, 18.21), (2.186, 16.38),
                (2.595, 14.97), (3.024, 13.86), (3.998, 12.07), (4.717, 11.15),
                (5.842, 10.03), (8.023, 8.56), (11.77, 6.99), (29.76, 3.58),
                (37.53, 2.56), (41.26, 1.99), (43.13, 1.60), (45.08, 0.99),
                (46.64, 0.00)),
            10_000: ((1, 23.37), (1.142, 21.51), (1.284, 20.04),
                (1.458, 18.62), (1.655, 17.38), (2.193, 14.97), (3.024, 12.73),
                (3.694, 11.53), (4.327, 10.68), (5.121, 9.83), (5.502, 9.53),
                (5.696, 9.32), (7.048, 8.37), (11.1, 6.56), (23.51, 3.84),
                (27.07, 3.30), (32.38, 2.50), (35.45, 1.97), (37.61, 1.43),
                (38.9, 0.99), (39.69, 0.59), (40.19, 0.00)),
            1_000: ((1, 20.19), (1.272, 17.60), (1.505, 16.07), (1.692, 15.11),
                (2.254, 13.07), (2.869, 11.59), (4.019, 9.83), (4.757, 9.03),
                (6.081, 7.97), (8.134, 6.81), (21.15, 3.39), (25.41, 2.61),
                (27.59, 2.20), (30.46, 1.49), (32.01, 0.85), (32.94, 0.00)),
        },
    },
    "E-7": {
        "key": "m35a2_cargo_truck",
        "caption": "M35A2 2.5-Ton Cargo Truck 6x6",
        "gross_weight_lb": 18800, "y_max_in": 20,
        "curves": {
            10_000_000: ((1, 17.69), (1.166, 16.17), (1.491, 13.91),
                (2.223, 10.47), (2.436, 9.81), (3.201, 8.33), (4.373, 6.88),
                (6.03, 5.58), (11.9, 3.10), (14.63, 2.22), (16.02, 1.71),
                (17.19, 1.13), (17.8, 0.65), (18.24, 0.00)),
            1_000_000: ((1, 16.66), (1.191, 14.99), (1.721, 11.78),
                (2.163, 9.91), (2.294, 9.56), (3.056, 8.05), (4.281, 6.54),
                (6.03, 5.20), (10.71, 3.14), (13.22, 2.27), (14.72, 1.67),
                (15.72, 1.15), (16.19, 0.80), (16.78, 0.00)),
            100_000: ((1, 15.33), (1.217, 13.56), (1.78, 10.31), (2.005, 9.53),
                (2.665, 8.05), (3.733, 6.54), (4.466, 5.82), (4.962, 5.47),
                (5.513, 5.03), (9.618, 3.05), (11.76, 2.23), (13.11, 1.63),
                (13.72, 1.30), (14.41, 0.76), (14.95, 0.00)),
            10_000: ((1, 13.70), (1.536, 10.05), (1.888, 8.87), (2.501, 7.49),
                (3.255, 6.35), (4.777, 4.89), (7.931, 3.12), (9.885, 2.25),
                (10.96, 1.71), (11.7, 1.26), (12.32, 0.73), (12.76, 0.00)),
            1_000: ((1, 11.68), (1.181, 10.28), (1.258, 9.82), (1.657, 8.31),
                (2.071, 7.26), (2.475, 6.50), (3.056, 5.67), (7.328, 2.57),
                (8.466, 1.95), (9.26, 1.44), (9.947, 0.87), (10.44, 0.00)),
        },
    },
    "E-8": {
        "key": "m60a3_main_tank",
        "caption": "M60A3 Main Tank",
        "gross_weight_lb": 116000, "y_max_in": 50,
        "curves": {
            10_000_000: ((1.27, 50.00), (1.41, 45.14), (1.741, 37.11),
                (2.007, 32.52), (2.363, 28.03), (2.863, 23.71), (3.46, 20.21),
                (4.41, 16.52), (5.479, 13.65), (6.068, 12.67), (7.359, 11.29),
                (8.981, 10.05), (12, 8.58), (15.29, 7.54), (20.26, 6.47),
                (31.24, 5.01), (35.94, 4.62), (37.45, 4.42), (52.8, 3.44),
                (73.51, 2.25), (79.73, 1.84), (86.28, 1.23), (89.15, 0.79),
                (91.17, 0.00)),
            1_000_000: ((1.155, 50.00), (1.34, 43.36), (1.608, 36.59),
                (1.92, 30.99), (2.36, 25.85), (2.773, 22.48), (3.147, 20.21),
                (4.027, 16.47), (5.068, 13.42), (5.572, 12.57), (6.081, 11.94),
                (7.716, 10.39), (10.25, 8.87), (12.92, 7.83), (21.27, 5.96),
                (28.09, 5.06), (30.02, 4.99), (30.91, 4.74), (50.09, 3.35),
                (51, 3.22), (69.37, 2.11), (74.45, 1.70), (79.14, 1.21),
                (81.49, 0.83), (83.64, 0.00)),
            100_000: ((1.018, 50.00), (1.137, 44.91), (1.29, 39.91),
                (1.542, 33.85), (1.704, 30.87), (1.932, 27.55), (2.183, 24.77),
                (2.687, 20.78), (3.424, 16.99), (4.148, 14.37), (4.972, 12.50),
                (5.23, 12.10), (6.623, 10.53), (8.032, 9.42), (11.63, 7.73),
                (18.45, 6.01), (30.08, 4.44), (45.08, 3.25), (59.23, 2.30),
                (68.5, 1.52), (71.83, 1.10), (73.64, 0.74), (75.17, 0.00)),
            10_000: ((1, 43.73), (1.102, 39.91), (1.345, 33.19), (1.6, 28.32),
                (1.759, 26.05), (2.087, 22.48), (2.515, 19.23), (3.03, 16.47),
                (3.706, 13.73), (3.902, 13.16), (4.327, 12.29), (5.23, 10.96),
                (6.793, 9.43), (8.342, 8.44), (11.03, 7.26), (14.32, 6.29),
                (20.41, 5.12), (39.98, 3.12), (50.2, 2.33), (58.55, 1.53),
                (62.24, 1.04), (63.51, 0.73), (64.91, 0.00)),
            1_000: ((1, 35.67), (1.148, 31.39), (1.296, 28.13), (1.463, 25.25),
                (1.69, 22.29), (2.009, 19.30), (2.294, 17.28), (3.069, 13.36),
                (3.325, 12.57), (4.062, 11.15), (5.089, 9.77), (6.31, 8.68),
                (7.468, 7.92), (9.497, 6.96), (12.76, 5.92), (16.72, 5.04),
                (35.75, 2.78), (44.99, 1.91), (49.2, 1.39), (51.32, 1.01),
                (52.42, 0.71), (53.65, 0.00)),
        },
    },
    "E-9": {
        "key": "m109a6_howitzer",
        "caption": "M109A6, 155 Howitzer Tracked",
        "gross_weight_lb": 67500, "y_max_in": 30,
        "curves": {
            10_000_000: ((1.339, 30.00), (1.482, 27.57), (1.667, 25.09),
                (1.703, 24.81), (1.722, 24.47), (1.864, 23.02), (2.149, 20.77),
                (2.47, 18.91), (2.908, 17.06), (3.46, 15.39), (4.04, 14.12),
                (4.712, 13.02), (6.068, 11.43), (7.931, 10.03), (10.87, 8.60),
                (14.91, 7.35), (20.35, 6.24), (50.2, 3.39), (61.98, 2.65),
                (69.89, 2.16), (75.95, 1.70), (81.17, 1.15), (82.9, 0.81),
                (83.73, 0.00)),
            1_000_000: ((1.207, 30.00), (1.326, 27.72), (1.505, 25.05),
                (1.643, 23.59), (1.741, 22.42), (1.992, 20.36), (2.294, 18.51),
                (2.631, 16.98), (3.269, 14.97), (3.989, 13.43), (5.015, 11.93),
                (6.068, 10.86), (8.023, 9.47), (9.947, 8.52), (13.85, 7.24),
                (18.1, 6.30), (24.31, 5.33), (45.95, 3.36), (62.24, 2.27),
                (69.01, 1.75), (74.61, 1.15), (76.27, 0.76), (76.95, 0.00)),
            100_000: ((1.063, 30.00), (1.169, 27.72), (1.332, 24.95),
                (1.57, 22.03), (1.778, 20.15), (1.998, 18.62), (2.393, 16.64),
                (2.911, 14.85), (3.293, 13.87), (3.994, 12.52), (4.957, 11.24),
                (6.191, 10.06), (8.683, 8.53), (10.15, 7.89), (15.29, 6.41),
                (22.97, 5.08), (39.69, 3.43), (49.41, 2.68), (57.81, 2.05),
                (62.17, 1.64), (66.44, 1.09), (67.93, 0.76), (68.97, 0.00)),
            10_000: ((1, 29.40), (1.166, 25.94), (1.282, 24.07), (1.44, 22.02),
                (1.651, 19.98), (1.898, 18.23), (2.246, 16.41), (2.584, 15.12),
                (3.293, 13.24), (4.019, 11.93), (5.353, 10.35), (7.251, 8.92),
                (10.08, 7.57), (16.41, 5.88), (39.23, 3.19), (51.48, 2.22),
                (56.01, 1.82), (61.07, 1.20), (63.1, 0.76), (63.7, 0.00)),
            1_000: ((1, 25.24), (1.101, 23.36), (1.256, 21.17), (1.478, 18.93),
                (1.603, 17.94), (1.82, 16.58), (2.131, 15.10), (2.459, 13.94),
                (3.154, 12.22), (3.702, 11.26), (4.683, 10.03), (6.036, 8.84),
                (8.263, 7.58), (12.92, 6.01), (17.28, 5.08), (29.95, 3.44),
                (39.19, 2.56), (42.99, 2.21), (47.82, 1.70), (52.3, 1.05),
                (53.31, 0.76), (53.95, 0.00)),
        },
    },
    "E-10": {
        "key": "m113_armored_carrier",
        "caption": "M113A1 Armored Carrier Tracked",
        "gross_weight_lb": 24500, "y_max_in": 25,
        "curves": {
            10_000_000: ((1, 20.70), (1.179, 18.46), (1.489, 15.87),
                (1.837, 14.02), (2.459, 11.98), (2.841, 11.11), (3.439, 10.08),
                (4.062, 9.26), (5.078, 8.28), (7.026, 6.99), (9.105, 6.08),
                (12.41, 5.06), (21, 3.40), (27.65, 2.41), (31.67, 1.74),
                (33.88, 1.24), (35.3, 0.77), (36.19, 0.00)),
            1_000_000: ((1, 19.19), (1.106, 17.94), (1.256, 16.52),
                (1.457, 15.06), (1.78, 13.45), (2.237, 11.88), (2.584, 11.02),
                (3.056, 10.11), (3.861, 8.99), (4.658, 8.18), (6.062, 7.14),
                (9.172, 5.69), (19.24, 3.34), (24.36, 2.50), (27.65, 1.94),
                (29.61, 1.54), (30.78, 1.24), (32.14, 0.72), (32.91, 0.00)),
            100_000: ((1, 17.62), (1.169, 15.92), (1.398, 14.31),
                (1.62, 13.18), (2.03, 11.65), (2.696, 10.07), (3.04, 9.48),
                (3.915, 8.34), (5.572, 6.95), (9.047, 5.29), (17.55, 3.21),
                (22.82, 2.26), (25.84, 1.64), (28, 1.00), (28.6, 0.72),
                (29.32, 0.00)),
            10_000: ((1, 15.75), (1.078, 15.03), (1.215, 14.01),
                (1.458, 12.66), (1.665, 11.79), (2.035, 10.60), (2.501, 9.55),
                (3.36, 8.22), (4.105, 7.42), (4.797, 6.88), (5.084, 6.63),
                (5.998, 6.05), (8.1, 5.08), (14.48, 3.29), (18.92, 2.36),
                (21.47, 1.80), (22.39, 1.56), (23.78, 1.12), (24.67, 0.67),
                (25.31, 0.00)),
            1_000: ((1, 13.61), (1.099, 12.90), (1.331, 11.63), (1.595, 10.57),
                (2.015, 9.38), (2.93, 7.75), (4.019, 6.57), (6.417, 5.03),
                (12.62, 2.96), (16.32, 2.03), (17.93, 1.55), (19.4, 1.01),
                (19.88, 0.74), (20.3, 0.22), (20.32, 0.00)),
        },
    },
    "E-11": {
        "key": "m923_cargo_truck",
        "caption": "M923 5-Ton Cargo Truck 6x6",
        "gross_weight_lb": 32400, "y_max_in": 25,
        "curves": {
            10_000_000: ((1, 24.32), (1.296, 20.96), (1.785, 17.33),
                (2.863, 12.63), (3.424, 11.07), (4.045, 9.97), (4.762, 9.00),
                (6.062, 7.67), (7.563, 6.58), (13.94, 3.79), (15.49, 3.27),
                (17.37, 2.60), (18.43, 2.20), (19.84, 1.54), (20.63, 0.91),
                (20.94, 0.00)),
            1_000_000: ((1, 22.85), (1.229, 20.29), (1.615, 17.26),
                (2.294, 13.72), (2.631, 12.40), (3.037, 11.15), (3.446, 10.29),
                (4.083, 9.26), (5.398, 7.72), (7.579, 6.07), (12.81, 3.69),
                (14.08, 3.22), (15.82, 2.56), (17.24, 1.95), (18.35, 1.28),
                (18.76, 0.86), (19.05, 0.00)),
            100_000: ((1, 21.24), (1.229, 18.83), (1.57, 16.23),
                (2.418, 12.02), (2.679, 11.15), (3.033, 10.29), (3.857, 8.86),
                (4.513, 8.00), (6.03, 6.56), (11.05, 3.84), (12.54, 3.22),
                (14.22, 2.50), (15.52, 1.90), (16.39, 1.34), (16.88, 0.86),
                (17.15, 0.00)),
            10_000: ((1, 19.14), (1.272, 16.56), (1.458, 15.19),
                (2.032, 11.99), (2.27, 11.07), (2.645, 10.05), (3.056, 9.19),
                (4.066, 7.63), (6.068, 5.73), (10, 3.53), (12.14, 2.50),
                (13.11, 2.00), (14.14, 1.30), (14.58, 0.77), (14.79, 0.00)),
            1_000: ((1, 16.57), (1.489, 12.68), (1.833, 10.89), (2.011, 10.24),
                (2.721, 8.48), (3.655, 6.96), (7.889, 3.55), (9.895, 2.39),
                (10.85, 1.76), (11.34, 1.34), (11.8, 0.72), (11.98, 0.00)),
        },
    },
    "E-12": {
        "key": "m977_hemtt_cargo",
        "caption": "M977 Hemtt 10-Ton Cargo Truck 8x8",
        "gross_weight_lb": 62000, "y_max_in": 35,
        "curves": {
            5_000_000: ((1, 33.48), (1.118, 31.57), (1.285, 29.40),
                (1.413, 28.04), (1.726, 25.45), (2.393, 21.84), (3.259, 18.94),
                (4.083, 17.06), (4.609, 16.14), (6.191, 14.03), (7.765, 12.56),
                (10.38, 10.83), (13.94, 9.19), (31.04, 4.97), (38.73, 3.54),
                (43.59, 2.46), (45.51, 1.79), (46.87, 0.89), (47.1, 0.00)),
            1_000_000: ((1, 31.67), (1.245, 28.31), (1.614, 24.95),
                (1.876, 23.27), (2.338, 21.01), (3.225, 18.12), (4.062, 16.27),
                (4.808, 15.05), (7.1, 12.46), (9.24, 10.89), (11.53, 9.67),
                (26.23, 5.38), (34.42, 3.73), (37.53, 3.06), (39.69, 2.54),
                (41.44, 1.93), (43.08, 0.89), (43.28, 0.00)),
            100_000: ((1, 29.62), (1.109, 28.11), (1.383, 25.25),
                (1.655, 23.21), (2.275, 20.02), (2.809, 18.18), (3.293, 16.89),
                (4.513, 14.57), (4.848, 14.16), (5.009, 13.88), (6.665, 12.05),
                (7.563, 11.30), (12.28, 8.65), (21.24, 5.86), (29.76, 3.95),
                (33.63, 3.04), (35.68, 2.46), (36.82, 2.06), (38.41, 1.24),
                (39.23, 0.00)),
            10_000: ((1, 27.16), (1.189, 24.95), (1.57, 21.91), (1.896, 20.07),
                (2.351, 18.19), (2.809, 16.75), (3.89, 14.37), (6.126, 11.51),
                (9.648, 9.00), (21.24, 4.97), (25.63, 3.87), (29.14, 2.93),
                (30.78, 2.40), (32.11, 1.85), (33.32, 1.00), (33.63, 0.00)),
            1_000: ((1, 24.17), (1.206, 22.12), (1.5, 19.99), (1.683, 18.96),
                (2.181, 16.82), (3.101, 14.26), (4.105, 12.46), (6.191, 10.08),
                (9.047, 8.10), (17.1, 4.93), (21.7, 3.54), (24.34, 2.65),
                (26.01, 1.92), (26.79, 1.43), (27.41, 0.76), (27.53, 0.00)),
        },
    },
    "E-13": {
        "key": "m978_hemtt_fuel",
        "caption": "M978 Hemtt 10-Ton Fuel Truck 8x8",
        "gross_weight_lb": 59000, "y_max_in": 35,
        "curves": {
            10_000_000: ((1, 32.33), (1.232, 29.03), (1.428, 26.98),
                (1.708, 24.73), (2.001, 22.95), (2.277, 21.62), (3.056, 18.79),
                (4.327, 15.95), (6.323, 13.23), (10.5, 10.06), (21.93, 5.89),
                (28.53, 4.17), (32.45, 3.06), (33.85, 2.59), (35.01, 2.08),
                (36.4, 0.93), (36.59, 0.00)),
            1_000_000: ((1, 30.72), (1.117, 29.01), (1.285, 27.05),
                (1.553, 24.67), (2.063, 21.55), (2.251, 20.67), (2.821, 18.62),
                (3.471, 16.88), (4.377, 15.09), (6.191, 12.70), (10.17, 9.67),
                (20.47, 5.72), (26.51, 4.04), (30.02, 2.96), (31.84, 2.21),
                (33.14, 1.34), (33.6, 0.69), (33.64, 0.00)),
            100_000: ((1, 28.63), (1.226, 25.89), (1.598, 22.79),
                (2.011, 20.46), (2.665, 17.93), (3.056, 16.81), (3.977, 14.82),
                (6.068, 11.98), (8.333, 10.07), (19.73, 5.23), (23.85, 3.97),
                (26.56, 3.06), (28.66, 2.14), (29.92, 1.29), (30.28, 0.00)),
            10_000: ((1, 26.28), (1.299, 23.14), (1.603, 20.96),
                (2.069, 18.59), (2.501, 17.00), (3.065, 15.44), (4.192, 13.23),
                (6.062, 10.92), (8.766, 8.80), (15.98, 5.49), (19.84, 4.14),
                (21.22, 3.63), (23.73, 2.61), (24.72, 2.08), (25.87, 1.04),
                (26.12, 0.00)),
            1_000: ((1, 23.39), (1.258, 20.96), (1.575, 18.86), (2.026, 16.74),
                (2.93, 14.03), (4.513, 11.25), (6.665, 9.00), (13.36, 5.23),
                (16.32, 3.97), (17.39, 3.51), (19.22, 2.61), (20.45, 1.81),
                (21.27, 0.80), (21.37, 0.00)),
        },
    },
    "E-14": {
        "key": "m983_hemtt_trailer",
        "caption": "M983 Hemtt With XM860A1 Trailer",
        "gross_weight_lb": 81483, "y_max_in": 35,
        "curves": {
            10_000_000: ((1, 34.01), (1.204, 30.70), (1.553, 26.84),
                (1.799, 24.89), (2.154, 22.76), (2.773, 20.09), (3.989, 16.79),
                (5.873, 13.76), (9.338, 10.55), (17.21, 6.61), (19.69, 5.66),
                (22.87, 4.48), (25.47, 3.42), (27.33, 2.40), (28.6, 1.02),
                (28.71, 0.00)),
            1_000_000: ((1, 32.06), (1.229, 28.69), (1.489, 25.97),
                (1.833, 23.41), (2.093, 21.92), (2.496, 20.09), (3.435, 17.17),
                (4.447, 15.07), (4.869, 14.45), (5.015, 14.16), (7.251, 11.56),
                (15.16, 6.81), (19.73, 4.94), (23.41, 3.35), (24.99, 2.43),
                (26.01, 1.48), (26.28, 1.02), (26.39, 0.00)),
            100_000: ((1, 29.92), (1.258, 26.50), (1.57, 23.70),
                (1.837, 21.93), (2.501, 18.84), (3.435, 16.10), (5.015, 13.23),
                (7.5, 10.50), (15, 6.08), (18.31, 4.60), (20.41, 3.62),
                (21.51, 3.02), (22.49, 2.36), (23.41, 1.42), (23.73, 0.77),
                (23.75, 0.00)),
            10_000: ((1, 27.27), (1.18, 25.03), (1.603, 21.49), (1.839, 20.09),
                (2.285, 18.06), (2.809, 16.30), (3.519, 14.52), (4.327, 13.02),
                (6.03, 10.79), (13.36, 5.74), (16.78, 3.98), (17.99, 3.29),
                (19.73, 2.00), (20.28, 1.18), (20.5, 0.00)),
            1_000: ((1, 24.16), (1.19, 22.14), (1.457, 20.02), (1.91, 17.53),
                (2.563, 15.12), (3.998, 11.92), (10.8, 5.66), (12, 4.93),
                (13.79, 3.81), (15.04, 2.95), (16.22, 1.76), (16.69, 0.81),
                (16.78, 0.00)),
        },
    },
    "E-15": {
        "key": "m998_hmmwv",
        "caption": "M998 HMMWV 1.25-Ton Carrier",
        "gross_weight_lb": 7900, "y_max_in": 15,
        "curves": {
            5_000_000: ((1, 13.46), (1.295, 12.15), (1.761, 10.71),
                (2.744, 8.81), (5.979, 5.69), (7.856, 4.50), (8.887, 3.89),
                (9.874, 3.30), (10.75, 2.73), (11.4, 2.29), (11.92, 1.82),
                (12.48, 1.01), (12.61, 0.61), (12.62, 0.00)),
            1_000_000: ((1, 13.10), (1.253, 11.98), (1.782, 10.37),
                (2.418, 9.07), (5.986, 5.44), (7.5, 4.46), (8.887, 3.61),
                (9.937, 2.95), (10.53, 2.53), (11.1, 2.11), (11.43, 1.79),
                (11.96, 0.98), (12.09, 0.58), (12.1, 0.00)),
            100_000: ((1, 12.49), (1.326, 11.14), (1.69, 10.06), (2.771, 8.02),
                (4.633, 6.03), (5.911, 5.04), (6.75, 4.46), (7.914, 3.69),
                (8.887, 3.04), (9.73, 2.44), (10.45, 1.78), (10.99, 0.92),
                (11.11, 0.50), (11.12, 0.00)),
            10_000: ((1, 11.60), (1.245, 10.60), (1.603, 9.52), (2.275, 8.11),
                (3.915, 6.03), (5.353, 4.77), (6.363, 4.02), (7.085, 3.48),
                (7.856, 2.91), (8.924, 2.03), (9.358, 1.48), (9.648, 0.94),
                (9.799, 0.00)),
            1_000: ((1, 10.44), (1.206, 9.64), (1.765, 8.10), (2.983, 6.14),
                (4.668, 4.40), (5.702, 3.49), (6.75, 2.59), (7.437, 1.91),
                (7.922, 1.23), (8.015, 0.84), (8.1, 0.72), (8.192, 0.00)),
        },
    },
    "E-16": {
        "key": "m988b_rtch_forklift",
        "caption": "M988B RTCH FORKLIFT",
        "gross_weight_lb": 180000, "y_max_in": 50,
        "curves": {
            10_000_000: ((4.47, 50.00), (4.633, 48.88), (5.02, 46.90),
                (6.376, 41.61), (7.548, 38.21), (10.13, 32.75), (15.29, 25.95),
                (29.2, 15.88), (33.49, 13.54), (36.82, 11.69), (39.94, 9.91),
                (42.77, 8.02), (45.03, 6.06), (45.61, 5.30), (45.62, 4.62),
                (47.66, 0.00)),
            1_000_000: ((3.973, 50.00), (4.308, 47.82), (5.089, 44.01),
                (6.376, 39.28), (8.413, 34.06), (10.2, 30.68), (12.78, 27.02),
                (26.59, 15.69), (30.05, 13.61), (33.85, 11.30), (37.29, 9.09),
                (39.56, 7.39), (40.7, 6.20), (41.52, 5.12), (41.92, 3.26),
                (43.37, 0.00)),
            100_000: ((3.467, 50.00), (4.036, 46.25), (5.089, 41.19),
                (5.911, 38.29), (6.043, 37.71), (7.011, 35.10), (7.122, 34.66),
                (10.46, 28.09), (21.11, 17.26), (26.84, 13.35), (29.86, 11.31),
                (33.56, 8.60), (35.19, 7.19), (36.48, 5.77), (38.62, 0.00)),
            10_000: ((2.867, 50.00), (3.575, 44.74), (4.452, 40.05),
                (6.581, 32.76), (7.956, 29.55), (10.64, 24.94), (19.65, 15.72),
                (26.28, 10.62), (29.79, 7.60), (31.11, 6.05), (31.87, 4.82),
                (31.88, 4.13), (33.32, 0.00)),
            1_000: ((2.226, 50.00), (2.491, 47.14), (3.069, 42.45),
                (3.845, 37.92), (4.797, 33.83), (6.444, 28.87), (8.125, 25.23),
                (16.76, 14.45), (18.37, 12.96), (21.56, 9.96), (23.21, 8.31),
                (25.2, 5.76), (25.82, 4.23), (27, 0.00)),
        },
    },
    "E-17": {
        "key": "m1070_het_tractor",
        "caption": "M1070 HET Tractor W/M1000 TRL W/M1A1 Tank",
        "gross_weight_lb": 229750, "y_max_in": 40,
        "curves": {
            10_000_000: ((1, 39.92), (1.055, 38.48), (1.191, 36.18),
                (1.458, 32.71), (1.672, 30.59), (1.918, 28.62), (1.969, 28.36),
                (1.996, 28.08), (2.47, 25.36), (2.924, 23.39), (3.733, 20.76),
                (5.046, 17.85), (6.937, 15.06), (9.066, 12.89), (15.32, 8.86),
                (19.61, 6.85), (22.77, 5.42), (25.15, 4.17), (26.45, 3.85),
                (29.95, 3.38), (35.83, 2.55), (39.48, 1.95), (41.52, 1.48),
                (42.77, 1.09), (43.42, 0.72), (43.76, 0.00)),
            1_000_000: ((1, 37.60), (1.285, 33.17), (1.568, 30.05),
                (1.708, 28.85), (2.065, 26.35), (2.465, 24.21), (3.002, 21.99),
                (3.431, 20.61), (4.513, 17.95), (6.296, 15.05), (8.066, 13.04),
                (13.65, 9.02), (17.76, 6.89), (19.88, 5.89), (21.58, 5.04),
                (23.16, 4.11), (24.57, 3.77), (29.92, 2.99), (34.46, 2.27),
                (36.75, 1.82), (39.6, 0.99), (40.24, 0.00)),
            100_000: ((1, 35.21), (1.258, 31.42), (1.726, 26.95),
                (1.996, 25.12), (2.331, 23.33), (3.164, 20.10), (4.045, 17.77),
                (5.572, 15.00), (7.033, 13.11), (11.17, 9.62), (15.65, 6.97),
                (19.24, 5.05), (20.03, 4.42), (20.58, 4.17), (22.35, 3.70),
                (26.28, 3.05), (29.45, 2.50), (32.66, 1.88), (34.68, 1.33),
                (35.64, 0.92), (36.21, 0.00)),
            10_000: ((1, 32.45), (1.168, 30.05), (1.326, 28.24), (1.57, 26.05),
                (2.02, 23.08), (2.565, 20.56), (3.024, 18.94), (3.813, 16.82),
                (4.561, 15.30), (4.894, 14.81), (5.342, 14.02), (6.665, 12.27),
                (11.29, 8.33), (13.79, 6.74), (16.6, 5.05), (17.76, 4.17),
                (19.28, 3.70), (22.51, 3.07), (25.57, 2.47), (28.84, 1.74),
                (30.85, 1.02), (31.33, 0.63), (31.62, 0.00)),
            1_000: ((1, 29.13), (1.258, 26.05), (1.672, 22.71), (2.136, 20.15),
                (3.024, 16.89), (4.683, 13.30), (8.583, 8.79), (11.29, 6.67),
                (13.31, 5.20), (14.54, 4.17), (16.29, 3.55), (21.15, 2.39),
                (22.87, 1.97), (24.11, 1.59), (25.2, 1.15), (25.71, 0.84),
                (26.12, 0.00)),
        },
    },
    "E-18": {
        "key": "m1074_load_system_crane",
        "caption": "M1074 Load System w/Crane w/M1076 Trailer",
        "gross_weight_lb": 140859, "y_max_in": 40,
        "curves": {
            10_000_000: ((1, 38.22), (1.14, 34.97), (1.296, 32.19),
                (1.457, 30.09), (1.918, 26.21), (2.393, 23.56), (2.762, 21.98),
                (3.36, 20.00), (4.019, 18.37), (5.02, 16.51), (6.771, 14.20),
                (11.17, 10.82), (22.87, 6.38), (29.45, 4.59), (33.49, 3.36),
                (36.13, 2.29), (37.61, 1.03), (37.78, 0.00)),
            1_000_000: ((1, 35.61), (1.204, 31.56), (1.413, 28.93),
                (1.598, 27.20), (1.878, 25.12), (2.538, 21.74), (3.024, 20.00),
                (3.853, 17.82), (4.609, 16.34), (6.068, 14.25), (8.316, 12.06),
                (10.6, 10.51), (19.53, 6.77), (23.36, 5.60), (27.07, 4.51),
                (29.67, 3.71), (31.44, 3.05), (33.25, 2.22), (34.57, 1.03),
                (34.73, 0.00)),
            100_000: ((1, 32.91), (1.157, 30.18), (1.272, 28.70), (1.5, 26.42),
                (1.953, 23.23), (2.645, 20.10), (3.431, 17.74), (4.105, 16.26),
                (5.02, 14.72), (6.39, 13.00), (10.01, 10.09), (19.32, 6.07),
                (24.36, 4.44), (27.07, 3.50), (29.61, 2.37), (30.78, 1.42),
                (31.18, 0.81), (31.26, 0.00)),
            10_000: ((1, 29.74), (1.19, 27.20), (1.553, 23.88), (2.045, 20.91),
                (2.528, 18.91), (3.024, 17.35), (3.702, 15.74), (5.398, 13.00),
                (8.369, 10.16), (17.57, 5.68), (21.42, 4.26), (24.08, 3.18),
                (25.79, 2.29), (26.34, 1.90), (26.98, 1.14), (27.26, 0.00)),
            1_000: ((1, 26.45), (1.206, 24.11), (1.563, 21.28), (2.069, 18.60),
                (2.839, 15.95), (4.023, 13.39), (4.993, 11.95), (7.406, 9.49),
                (13.22, 6.07), (15.65, 4.98), (17.76, 4.05), (19.86, 3.00),
                (21.33, 1.98), (22.09, 1.07), (22.32, 0.00)),
        },
    },
    "E-19": {
        "key": "m1075_load_system",
        "caption": "M1075 Load System",
        "gross_weight_lb": 81660, "y_max_in": 40,
        "curves": {
            10_000_000: ((1, 37.10), (1.148, 33.86), (1.242, 32.19),
                (1.389, 30.13), (1.655, 27.53), (2.045, 24.79), (2.762, 21.51),
                (3.191, 20.09), (4.019, 17.98), (5.015, 16.19), (7.1, 13.62),
                (10.49, 11.05), (21.7, 6.69), (29.42, 4.66), (33.63, 3.47),
                (36.44, 2.51), (37.1, 2.17), (38.01, 1.34), (38.96, 0.00)),
            1_000_000: ((1, 34.54), (1.13, 31.95), (1.228, 30.39),
                (1.474, 27.61), (1.783, 25.13), (1.99, 23.84), (2.696, 20.63),
                (3.325, 18.68), (4.023, 17.05), (4.658, 15.88), (6.336, 13.63),
                (9.143, 11.21), (18.52, 7.00), (22.87, 5.68), (26.79, 4.59),
                (29.45, 3.81), (32.86, 2.60), (34.03, 1.84), (35.47, 0.00)),
            100_000: ((1, 31.80), (1.132, 29.56), (1.326, 27.22),
                (1.458, 25.98), (1.896, 22.86), (2.483, 20.10), (3.027, 18.30),
                (3.579, 16.89), (4.148, 15.72), (6.062, 13.00), (9.537, 10.12),
                (18.92, 6.07), (24.11, 4.44), (27.07, 3.42), (29.33, 2.54),
                (30.3, 1.77), (31.6, 0.00)),
            10_000: ((1, 28.68), (1.203, 26.11), (1.505, 23.41),
                (1.988, 20.48), (2.501, 18.37), (3.255, 16.19), (5.121, 12.92),
                (7.973, 10.12), (17.03, 5.68), (22.16, 3.81), (23.75, 3.16),
                (25.52, 2.29), (26.28, 1.49), (27.25, 0.00)),
            1_000: ((1, 25.27), (1.293, 22.29), (1.66, 19.77), (1.992, 18.12),
                (2.475, 16.34), (2.896, 15.17), (3.504, 13.77), (4.757, 11.75),
                (7.484, 9.03), (12.93, 5.91), (15, 4.98), (17.17, 4.03),
                (19.63, 2.84), (20.41, 2.35), (21.18, 1.53), (22.06, 0.00)),
        },
    },
    "E-20": {
        "key": "m1075_load_system_trailer",
        "caption": "M1075 Load System w/M1076 Trailer",
        "gross_weight_lb": 136159, "y_max_in": 40,
        "curves": {
            10_000_000: ((1, 37.58), (1.217, 33.04), (1.352, 30.94),
                (1.505, 29.09), (1.862, 26.10), (2.368, 23.25), (2.791, 21.51),
                (3.36, 19.69), (4.148, 17.82), (5.015, 16.26), (7.328, 13.46),
                (12.28, 10.12), (23.6, 6.23), (29.42, 4.74), (33.42, 3.66),
                (36.82, 2.51), (38.01, 1.73), (39.05, 0.41), (39.76, 0.00)),
            1_000_000: ((1, 35.05), (1.217, 30.94), (1.34, 29.25),
                (1.521, 27.38), (1.739, 25.64), (2.149, 23.16), (2.872, 20.16),
                (3.655, 17.98), (4.201, 16.82), (5.236, 15.11), (6.595, 13.46),
                (10.16, 10.66), (21.7, 6.15), (25.93, 4.97), (28.18, 4.34),
                (31.04, 3.50), (32.79, 2.89), (34.28, 2.21), (35.3, 1.26),
                (36.22, 0.00)),
            100_000: ((1, 32.26), (1.117, 30.16), (1.219, 28.70),
                (1.458, 26.21), (1.653, 24.65), (1.902, 23.07), (2.536, 20.10),
                (3.694, 16.81), (4.281, 15.64), (5.41, 13.95), (7.328, 11.91),
                (9.699, 10.16), (19.73, 5.99), (23.09, 4.97), (25.36, 4.26),
                (27.04, 3.73), (30.11, 2.58), (31.27, 1.77), (32.62, 0.00)),
            10_000: ((1, 29.29), (1.153, 27.12), (1.474, 24.03),
                (1.774, 21.98), (2.149, 20.05), (2.475, 18.75), (3.431, 16.03),
                (5.23, 13.00), (8.229, 10.12), (13.94, 7.08), (18.29, 5.43),
                (22.87, 3.81), (24.52, 3.16), (26.34, 2.29), (27.13, 1.49),
                (28.13, 0.00)),
            1_000: ((1, 25.86), (1.157, 24.03), (1.494, 21.25), (2.017, 18.41),
                (2.665, 16.11), (3.542, 14.01), (4.833, 11.95), (7.413, 9.35),
                (14.23, 5.60), (18.29, 3.88), (20.56, 2.79), (21.51, 2.19),
                (22.09, 1.53), (23.03, 0.00)),
        },
    },
    "E-21": {
        "key": "m1078_cargo_truck",
        "caption": "M1078 2.5-Ton Cargo Truck 4x4",
        "gross_weight_lb": 22740, "y_max_in": 30,
        "curves": {
            10_000_000: ((1, 25.93), (1.206, 23.80), (1.57, 21.12),
                (2.069, 18.57), (2.85, 15.96), (3.698, 14.01), (4.518, 12.61),
                (6.39, 10.33), (11.41, 6.71), (13.78, 5.42), (16.19, 4.16),
                (17.99, 3.11), (19, 2.30), (19.84, 1.14), (20.12, 0.00)),
            1_000_000: ((1, 24.56), (1.19, 22.68), (1.547, 20.10),
                (1.912, 18.24), (2.704, 15.43), (3.328, 13.90), (4.327, 12.08),
                (6.323, 9.63), (10.6, 6.42), (13.08, 4.96), (14.57, 4.10),
                (16.19, 3.05), (17.1, 2.24), (17.61, 1.47), (18.25, 0.00)),
            100_000: ((1, 22.91), (1.194, 21.12), (1.489, 19.07),
                (1.949, 16.79), (2.431, 15.08), (3.157, 13.20), (4.023, 11.56),
                (8.859, 6.65), (10.78, 5.35), (12.01, 4.55), (13.43, 3.59),
                (14.75, 2.53), (15.36, 1.70), (16.09, 0.00)),
            10_000: ((1, 20.93), (1.206, 19.19), (1.631, 16.66),
                (2.256, 14.19), (3.121, 11.96), (3.773, 10.74), (7.881, 6.24),
                (8.859, 5.49), (10.16, 4.49), (11.47, 3.47), (12.31, 2.75),
                (12.69, 2.34), (13.11, 1.59), (13.75, 0.00)),
            1_000: ((1, 18.29), (1.345, 15.88), (1.938, 13.21), (3.024, 10.33),
                (5.935, 6.30), (7.839, 4.46), (8.915, 3.42), (9.895, 2.31),
                (10.18, 1.70), (10.79, 0.00)),
        },
    },
    "E-22": {
        "key": "p23_crash_truck",
        "caption": "P-23 Crash Truck (Fire Truck)",
        "gross_weight_lb": 77880, "y_max_in": 40,
        "curves": {
            10_000_000: ((1, 38.66), (1.177, 35.14), (1.383, 32.28),
                (1.585, 30.09), (1.78, 28.38), (2.087, 26.29), (2.47, 24.26),
                (3.002, 22.12), (4.236, 18.83), (5.342, 16.89), (7.251, 14.55),
                (10.6, 11.98), (13.94, 10.27), (27.65, 6.23), (35.9, 4.42),
                (39.56, 3.58), (43.22, 2.52), (44.52, 1.81), (46.13, 0.00)),
            1_000_000: ((1, 36.45), (1.258, 32.20), (1.398, 30.49),
                (1.638, 28.16), (2.294, 23.95), (3.002, 21.11), (3.542, 19.53),
                (4.192, 18.05), (6.062, 15.10), (10.05, 11.67), (13.81, 9.74),
                (22.39, 6.93), (27.36, 5.68), (33.07, 4.36), (37.37, 3.24),
                (39.94, 2.40), (41.35, 1.34), (42.39, 0.00)),
            100_000: ((1, 33.97), (1.121, 31.97), (1.285, 29.79),
                (1.713, 25.83), (2.251, 22.72), (3.04, 19.73), (4.192, 16.96),
                (5.37, 15.06), (7.033, 13.16), (11.41, 10.12), (21.7, 6.38),
                (27.07, 4.98), (29.61, 4.32), (33.07, 3.35), (35.68, 2.43),
                (36.63, 1.84), (38.18, 0.00)),
            10_000: ((1, 31.18), (1.109, 29.56), (1.272, 27.61),
                (1.542, 25.14), (2.089, 21.77), (2.75, 19.14), (3.325, 17.51),
                (4.518, 15.11), (6.257, 12.84), (9.009, 10.55), (19.55, 6.08),
                (25.15, 4.44), (27.91, 3.57), (30.46, 2.66), (31.11, 2.35),
                (32.11, 1.57), (33.31, 0.00)),
            1_000: ((1, 27.78), (1.219, 25.20), (1.492, 22.88), (1.812, 20.89),
                (2.181, 19.14), (2.637, 17.51), (3.008, 16.46), (4.236, 13.93),
                (4.833, 13.04), (5.197, 12.64), (5.69, 11.98), (7.725, 10.12),
                (16.83, 5.67), (19.73, 4.67), (21.93, 3.89), (23.58, 3.26),
                (25.47, 2.43), (26.42, 1.61), (27.54, 0.00)),
        },
    },
    "E-23": {
        "key": "r11_refueler",
        "caption": "R-11 Refueler",
        "gross_weight_lb": 67775, "y_max_in": 40,
        "curves": {
            10_000_000: ((1.029, 40.00), (1.242, 36.11), (1.454, 33.22),
                (1.839, 29.30), (2.111, 27.20), (2.651, 24.05), (3.283, 21.35),
                (4.978, 16.54), (6.062, 14.47), (6.945, 13.17), (7.406, 12.73),
                (10.02, 11.04), (13.7, 9.42), (19.28, 7.79), (39.69, 4.49),
                (49.2, 3.31), (55.43, 2.42), (58.79, 1.79), (61.07, 0.77),
                (61.25, 0.00)),
            1_000_000: ((1, 38.15), (1.217, 34.36), (1.505, 30.67),
                (1.8, 27.86), (2.211, 24.95), (2.679, 22.46), (3.46, 19.38),
                (5.084, 15.10), (6.017, 13.43), (6.526, 12.80), (6.952, 12.42),
                (10.65, 10.11), (16.24, 8.07), (32.25, 4.97), (39.19, 4.02),
                (45.37, 3.18), (51.48, 2.20), (53.81, 1.61), (55.54, 0.77),
                (55.79, 0.00)),
            100_000: ((1, 35.32), (1.129, 33.07), (1.326, 30.36),
                (1.458, 28.85), (1.892, 25.04), (1.955, 24.74), (2.013, 24.27),
                (2.444, 21.80), (3.014, 19.30), (4.485, 14.95), (5.291, 13.34),
                (6.081, 12.37), (7.04, 11.53), (9.377, 10.03), (14.97, 7.79),
                (28.72, 4.89), (39.56, 3.26), (44.42, 2.42), (47.42, 1.76),
                (49.57, 0.79), (49.63, 0.00)),
            10_000: ((1, 31.85), (1.232, 28.47), (1.537, 25.29),
                (1.918, 22.41), (2.27, 20.36), (2.998, 17.21), (3.655, 15.08),
                (4.419, 13.26), (4.962, 12.42), (5.347, 11.98), (7.973, 9.85),
                (12.52, 7.71), (23.75, 4.89), (28.72, 3.98), (33.78, 3.11),
                (37.93, 2.27), (39.94, 1.73), (41.57, 0.89), (41.99, 0.00)),
            1_000: ((1, 27.67), (1.308, 23.90), (1.744, 20.36), (2.85, 14.95),
                (3.468, 13.11), (4.023, 12.05), (5.781, 10.11), (9.124, 7.94),
                (19.57, 4.64), (25.93, 3.25), (30.08, 2.27), (31.87, 1.70),
                (33.32, 0.89), (33.67, 0.00)),
        },
    },
    "E-24": {
        "key": "pickup_small",
        "caption": "Truck, Small Pickup, or SUV",
        "gross_weight_lb": 5000, "y_max_in": 15,
        "curves": {
            10_000_000: ((1, 13.38), (1.398, 11.47), (1.85, 10.04),
                (2.244, 9.14), (3.475, 7.28), (4.983, 5.86), (8.142, 4.01),
                (9.802, 3.26), (11.23, 2.63), (12.53, 2.01), (13.21, 1.59),
                (14.11, 0.77), (14.63, 0.00)),
            1_000_000: ((1, 12.62), (1.369, 10.90), (1.814, 9.53),
                (2.328, 8.41), (3.504, 6.73), (7.848, 3.68), (8.934, 3.15),
                (10.51, 2.39), (11.46, 1.86), (11.95, 1.49), (12.7, 0.74),
                (13.17, 0.00)),
            100_000: ((1, 11.68), (1.181, 10.79), (1.392, 9.98), (1.998, 8.34),
                (2.724, 7.08), (3.339, 6.29), (6.707, 3.68), (7.939, 3.00),
                (8.821, 2.52), (9.658, 2.02), (10.26, 1.59), (11.08, 0.72),
                (11.48, 0.00)),
            10_000: ((1, 10.49), (1.104, 9.98), (1.458, 8.72), (1.99, 7.42),
                (3.002, 5.83), (4.658, 4.23), (5.004, 4.01), (7.19, 2.51),
                (7.856, 2.06), (8.619, 1.37), (9.162, 0.69), (9.496, 0.00)),
            1_000: ((1, 8.92), (1.157, 8.29), (1.607, 6.96), (2.028, 6.07),
                (2.75, 5.00), (4.327, 3.35), (5.525, 2.34), (5.911, 2.01),
                (6.554, 1.29), (6.908, 0.78), (7.228, 0.00)),
        },
    },
    "E-25": {
        "key": "pickup_large",
        "caption": "Truck, Large Pickup, or SUV",
        "gross_weight_lb": 7500, "y_max_in": 15,
        "curves": {
            10_000_000: ((1.048, 15.00), (1.258, 13.83), (1.537, 12.64),
                (1.998, 11.18), (2.496, 10.05), (3.985, 7.90), (5.619, 6.47),
                (8.924, 4.62), (11.31, 3.61), (12.7, 3.07), (14.31, 2.43),
                (15.07, 2.09), (15.55, 1.80), (16.53, 0.91), (17.31, 0.00)),
            1_000_000: ((1, 14.48), (1.132, 13.69), (1.443, 12.27),
                (1.878, 10.85), (2.651, 9.16), (4.036, 7.31), (9.874, 3.70),
                (11.31, 3.07), (12.46, 2.57), (13.42, 2.11), (14.11, 1.65),
                (15.04, 0.72), (15.59, 0.00)),
            100_000: ((1, 13.45), (1.258, 12.10), (1.443, 11.36), (1.89, 9.98),
                (2.336, 8.99), (2.747, 8.25), (3.497, 7.24), (7.914, 3.99),
                (10.18, 2.85), (11.31, 2.28), (12.08, 1.80), (12.97, 0.89),
                (13.58, 0.00)),
            10_000: ((1, 12.16), (1.299, 10.76), (1.5, 10.04), (2.013, 8.68),
                (3.046, 6.92), (4.105, 5.74), (5.025, 4.98), (6.93, 3.68),
                (8.448, 2.80), (9.577, 2.11), (10.2, 1.60), (10.85, 0.86),
                (11.36, 0.00)),
            1_000: ((1, 10.48), (1.369, 8.97), (1.708, 8.01), (2.449, 6.53),
                (5.041, 3.76), (5.954, 3.08), (6.609, 2.59), (7.359, 2.00),
                (7.889, 1.45), (8.333, 0.80), (8.729, 0.00)),
        },
    },
    "E-26": {
        "key": "truck_3_axle",
        "caption": "Truck 3-Axle",
        "gross_weight_lb": 35000, "y_max_in": 30,
        "curves": {
            10_000_000: ((1, 26.87), (1.336, 22.93), (1.763, 19.59),
                (2.684, 15.04), (3.269, 13.20), (3.435, 12.85), (4.023, 11.94),
                (5.02, 10.80), (7.328, 9.03), (8.953, 8.18), (14, 6.44),
                (27.82, 3.95), (33.39, 3.23), (38.33, 2.61), (42.41, 2.02),
                (44.99, 1.49), (47.17, 0.72), (48.13, 0.00)),
            1_000_000: ((1, 25.22), (1.194, 22.89), (1.603, 19.36),
                (2.319, 15.39), (3.005, 12.98), (3.468, 12.10), (4.023, 11.31),
                (5.02, 10.23), (6.996, 8.73), (10.16, 7.22), (26.12, 3.78),
                (33.78, 2.73), (37.93, 2.10), (39.69, 1.78), (42.32, 0.99),
                (43.79, 0.00)),
            100_000: ((1, 23.25), (1.34, 19.70), (1.837, 16.29),
                (2.418, 13.57), (2.785, 12.51), (3.579, 11.14), (4.466, 10.06),
                (6.952, 8.12), (10.16, 6.65), (22.3, 3.84), (29.76, 2.67),
                (32.31, 2.26), (34.35, 1.85), (35.75, 1.50), (37.49, 0.85),
                (38.58, 0.00)),
            10_000: ((1, 20.87), (1.121, 19.53), (1.719, 14.97),
                (2.115, 13.07), (2.507, 11.94), (3.655, 10.06), (4.993, 8.67),
                (6.081, 7.86), (9.028, 6.35), (18.45, 3.84), (21.67, 3.23),
                (25.41, 2.56), (28.24, 1.99), (30.46, 1.38), (31.67, 0.85),
                (32.59, 0.00)),
            1_000: ((1, 17.73), (1.285, 15.10), (1.505, 13.62), (1.73, 12.50),
                (2.005, 11.59), (2.75, 10.06), (4.419, 8.01), (6.043, 6.80),
                (8.896, 5.42), (12.7, 4.22), (16.78, 3.22), (19.73, 2.56),
                (22.11, 1.98), (23.65, 1.49), (25.12, 0.79), (25.82, 0.00)),
        },
    },
    "E-27": {
        "key": "truck_4_axle",
        "caption": "Truck 4-Axle",
        "gross_weight_lb": 40000, "y_max_in": 30,
        "curves": {
            10_000_000: ((1, 28.61), (1.285, 25.39), (1.878, 20.95),
                (2.995, 16.03), (3.663, 14.05), (4.011, 13.06), (4.21, 12.69),
                (5.467, 10.98), (6.257, 10.17), (7.328, 9.32), (9.143, 8.24),
                (13.08, 6.70), (20.05, 5.09), (30.59, 3.56), (38.73, 2.56),
                (42.14, 2.10), (44.19, 1.73), (45.95, 1.32), (47.67, 0.72),
                (48.63, 0.00)),
            1_000_000: ((1, 27.12), (1.413, 22.89), (1.998, 19.07),
                (3.572, 13.11), (4.019, 12.22), (4.757, 11.14), (6.068, 9.72),
                (7.251, 8.81), (9.047, 7.78), (13.94, 6.02), (28.21, 3.46),
                (33.74, 2.72), (36.63, 2.31), (39.27, 1.89), (41.35, 1.43),
                (42.77, 0.99), (44.24, 0.00)),
            100_000: ((1, 25.24), (1.285, 22.26), (1.918, 17.94),
                (1.969, 17.74), (2.131, 16.86), (2.59, 14.96), (3.037, 13.26),
                (3.621, 11.94), (4.561, 10.51), (5.467, 9.50), (6.257, 8.81),
                (8.083, 7.63), (12.33, 5.93), (24.26, 3.50), (29.76, 2.67),
                (31.64, 2.38), (34.46, 1.87), (36.82, 1.26), (38.21, 0.66),
                (38.99, 0.00)),
            10_000: ((1, 22.99), (1.489, 18.62), (2.47, 13.51), (2.791, 12.47),
                (3.221, 11.48), (3.813, 10.45), (4.833, 9.18), (5.572, 8.47),
                (7.183, 7.34), (10.02, 6.01), (20.05, 3.55), (23.09, 3.01),
                (27.3, 2.26), (29.45, 1.82), (31.77, 1.09), (32.62, 0.66),
                (33.31, 0.00)),
            1_000: ((1, 20.01), (1.258, 17.60), (1.936, 13.34), (2.251, 12.10),
                (2.637, 11.08), (3.118, 10.11), (4.023, 8.76), (5.519, 7.34),
                (9.019, 5.44), (17.32, 3.16), (21.47, 2.27), (22.87, 1.93),
                (24.67, 1.38), (25.93, 0.79), (26.65, 0.00)),
        },
    },
    "E-28": {
        "key": "truck_5_axle",
        "caption": "Truck 5-Axle",
        "gross_weight_lb": 80000, "y_max_in": 30,
        "curves": {
            10_000_000: ((1.24, 30.00), (1.242, 29.86), (1.373, 28.24),
                (1.634, 25.72), (1.994, 23.04), (2.547, 20.04), (4.006, 15.04),
                (5.036, 12.92), (5.655, 11.95), (6.526, 11.02), (8.066, 9.78),
                (11.53, 8.01), (15.39, 6.78), (20.15, 5.74), (36.98, 3.50),
                (45.37, 2.61), (49.36, 2.16), (53.25, 1.49), (54.79, 1.13),
                (55.89, 0.73), (56.98, 0.00)),
            1_000_000: ((1.106, 30.00), (1.296, 27.53), (1.57, 24.82),
                (2.2, 20.56), (2.457, 19.35), (2.549, 18.85), (3.609, 15.10),
                (4.006, 14.07), (5.052, 12.03), (5.572, 11.36), (6.945, 10.05),
                (8.404, 9.03), (10.82, 7.84), (16.15, 6.19), (29.54, 3.99),
                (35.94, 3.23), (41.05, 2.64), (45.85, 2.05), (48.43, 1.60),
                (50.89, 0.90), (52.35, 0.00)),
            100_000: ((1, 29.43), (1.179, 26.91), (1.394, 24.57),
                (1.69, 22.09), (2.043, 19.82), (3.147, 15.10), (3.725, 13.51),
                (4.47, 11.94), (5.812, 10.28), (7.328, 9.03), (9.009, 8.05),
                (13.42, 6.39), (29.95, 3.44), (37.85, 2.43), (39.52, 2.21),
                (41.96, 1.80), (44.05, 1.32), (45.95, 0.58), (46.63, 0.00)),
            10_000: ((1, 26.67), (1.117, 25.09), (1.474, 21.52),
                (1.998, 17.99), (2.824, 14.40), (3.46, 12.55), (3.733, 11.93),
                (4.196, 11.14), (5.02, 10.06), (6.458, 8.75), (8.057, 7.73),
                (10.08, 6.78), (12.2, 6.05), (26.51, 3.24), (32.31, 2.37),
                (35.83, 1.74), (37.61, 1.26), (38.69, 0.85), (40.04, 0.00)),
            1_000: ((1, 23.30), (1.219, 20.84), (1.413, 19.14), (1.988, 15.47),
                (2.716, 12.55), (3.225, 11.26), (3.853, 10.17), (4.658, 9.15),
                (5.69, 8.18), (7.093, 7.21), (9.679, 5.99), (19.73, 3.47),
                (25.68, 2.39), (28.21, 1.87), (30.46, 1.20), (31.34, 0.85),
                (32.28, 0.00)),
        },
    },
    "E-29": {
        "key": "truck_2_axle_6tire",
        "caption": "Truck 2-Axle, 6-Tire",
        "gross_weight_lb": 25000, "y_max_in": 30,
        "curves": {
            10_000_000: ((1, 29.20), (1.413, 24.76), (1.998, 20.78),
                (3.378, 15.26), (4.036, 13.60), (4.91, 11.93), (5.69, 10.97),
                (6.588, 10.11), (8.404, 8.81), (10.05, 7.95), (14.86, 6.31),
                (29.92, 3.66), (37.14, 2.73), (41.22, 2.15), (44.52, 1.49),
                (46.43, 0.81), (47.64, 0.00)),
            1_000_000: ((1, 27.53), (1.413, 23.28), (1.998, 19.41),
                (3.005, 15.19), (4.036, 12.52), (4.377, 11.88), (5.812, 10.11),
                (7.1, 9.03), (8.674, 8.07), (10.07, 7.40), (13.94, 6.08),
                (24.88, 3.92), (32.72, 2.78), (37.53, 2.05), (39.69, 1.55),
                (41.44, 0.99), (42.87, 0.00)),
            100_000: ((1, 25.57), (1.369, 21.86), (1.878, 18.45),
                (1.984, 17.95), (2.319, 16.30), (2.998, 13.82), (3.675, 12.07),
                (4.019, 11.42), (5.004, 10.10), (5.258, 9.88), (6.458, 8.75),
                (7.644, 7.95), (11.65, 6.19), (24.01, 3.50), (26.76, 3.06),
                (30.65, 2.43), (33.07, 1.99), (35.01, 1.50), (36.71, 0.85),
                (37.8, 0.00)),
            10_000: ((1, 23.04), (1.505, 18.57), (1.839, 16.52),
                (2.118, 15.20), (2.2, 14.76), (2.803, 12.60), (3.293, 11.37),
                (3.813, 10.45), (5.068, 8.92), (6.952, 7.44), (10.04, 5.96),
                (19.67, 3.51), (22.85, 2.89), (25.87, 2.31), (27.62, 1.93),
                (29.54, 1.38), (30.53, 0.93), (31.6, 0.00)),
            1_000: ((1, 19.77), (1.355, 16.64), (1.8, 13.91), (2.277, 11.94),
                (2.665, 10.85), (3.579, 9.20), (4.466, 8.12), (5.637, 7.11),
                (7.931, 5.77), (15.42, 3.39), (19.67, 2.37), (21.7, 1.82),
                (22.92, 1.38), (24.08, 0.79), (24.76, 0.00)),
        },
    },
    "E-30": {
        "key": "tyc850l_container_truck",
        "caption": "TYC-850L Container Truck",
        "gross_weight_lb": 217200, "y_max_in": 50,
        "curves": {
            10_000_000: ((5.558, 50.00), (6.981, 44.64), (9.221, 38.71),
                (11.38, 34.45), (17.17, 26.69), (24.41, 20.38), (37.61, 12.33),
                (38.73, 11.93), (40.23, 11.61), (59.04, 8.71), (78.39, 6.43),
                (88.93, 5.26), (97.37, 4.21), (100, 4.10)),
            1_000_000: ((4.945, 50.00), (5.967, 45.69), (6.062, 45.17),
                (8.032, 39.18), (9.822, 35.11), (12.05, 31.27), (12.53, 30.37),
                (14.16, 28.29), (14.97, 27.16), (34.06, 12.29), (35.68, 11.76),
                (58.98, 7.95), (79.73, 5.35), (89.29, 4.10), (94.53, 3.19),
                (96.95, 2.56), (98.11, 2.50), (100, 2.18)),
            100_000: ((4.271, 50.00), (6.005, 42.24), (9.019, 33.97),
                (12.37, 28.10), (29.83, 12.33), (31.41, 11.75), (48.84, 8.43),
                (67, 5.87), (79.06, 4.14), (84.63, 3.04), (87.93, 1.96)),
            10_000: ((3.533, 50.00), (4.967, 42.24), (6.088, 38.01),
                (6.901, 35.63), (7.003, 35.20), (10.02, 28.48), (23.41, 13.56),
                (24.83, 12.39), (26.28, 11.76), (47.32, 7.29), (61.84, 4.96),
                (68.86, 3.66), (71.45, 3.04), (74.06, 2.04), (74.91, 1.91)),
            1_000: ((2.658, 50.00), (3.005, 47.10), (3.679, 42.67),
                (5.364, 34.98), (8.032, 27.53), (19.28, 12.39), (20.17, 11.85),
                (35.23, 7.67), (42.59, 6.16), (47.07, 5.26), (51.43, 4.35),
                (55.54, 3.33), (59.41, 1.91)),
        },
    },
    "E-31": {
        "key": "mobile_crane_75bfmii",
        "caption": "75BFMII Mobile Crane",
        "gross_weight_lb": 165000, "y_max_in": 50,
        "curves": {
            500_000: ((1.827, 50.00), (2.021, 47.86), (2.717, 42.21),
                (3.386, 38.43), (4.04, 35.58), (4.73, 33.22), (6.551, 28.69),
                (9.112, 24.58), (12.52, 21.02), (18.81, 16.86), (39.48, 9.75),
                (46.13, 8.04), (52.45, 6.36), (57.08, 4.95), (59.45, 4.00),
                (61.28, 2.47), (62.98, 0.00)),
            100_000: ((1.646, 50.00), (2.073, 45.34), (2.475, 42.03),
                (3.034, 38.48), (4.129, 33.69), (6.058, 28.36), (8.604, 24.06),
                (11.51, 20.83), (18.04, 16.29), (31.38, 11.08), (38.26, 9.09),
                (45.5, 7.06), (49.47, 5.93), (53.11, 4.58), (55.26, 3.52),
                (57.92, 0.00)),
            10_000: ((1.35, 50.00), (1.7, 45.34), (2.325, 39.66),
                (3.079, 35.10), (4.04, 31.13), (5.072, 28.08), (6.436, 25.12),
                (10.05, 20.17), (15.42, 15.91), (29.47, 9.85), (37.71, 7.16),
                (43.64, 5.08), (45.93, 3.93), (47.25, 2.86), (49.17, 0.00)),
            1_000: ((1.03, 50.00), (1.344, 44.63), (1.673, 40.65),
                (2.33, 35.23), (3.031, 31.36), (4.078, 27.42), (4.617, 25.90),
                (6.316, 22.30), (7.465, 20.50), (11.7, 16.05), (23.79, 9.52),
                (29.53, 7.22), (33.3, 5.65), (35.12, 4.81), (36.7, 3.88),
                (37.67, 3.08), (38.94, 0.61), (39.56, 0.00)),
            100: ((1, 42.46), (1.292, 38.02), (1.772, 33.12), (2.517, 28.35),
                (3.025, 26.04), (4.142, 22.45), (6.153, 18.37), (7.048, 17.05),
                (15.57, 9.93), (19.82, 7.58), (22.23, 6.25), (24.5, 4.95),
                (26.44, 3.47), (27.17, 2.29), (28.14, 0.00)),
        },
    },
}


# vehicle key -> figure
_VEHICLES_E = {v["key"]: fig for fig, v in _FIGURES_E.items()}


def _figure_e_ref(fig):
    n = int(fig.split("-")[1])
    return (f"UFC 3-250-01, Figure {fig} (pdf_page {210 + n}, "
            f"printed {191 + n})")


def _resolve_vehicle_figure(vehicle):
    """The figure ('E-2' to 'E-31') for a figure number or vehicle key."""
    s = str(vehicle).strip().lower().replace(" ", "_").replace("-", "_")
    if s in _VEHICLES_E:
        return _VEHICLES_E[s]
    s = s.replace("figure", "").replace("_", "")
    if s.startswith("e") and s[1:].isdigit() and f"E-{s[1:]}" in _FIGURES_E:
        return f"E-{s[1:]}"
    raise ValueError(
        f"Unknown vehicle {vehicle!r}. Give a figure number 'E-2' to "
        f"'E-31' or one of: {', '.join(sorted(_VEHICLES_E))}.")


def _fig_e_on_curve(fig, passes, cbr):
    """Thickness on one printed curve; None above the chart's top."""
    pts = _FIGURES_E[fig]["curves"][passes]
    if cbr < pts[0][0]:
        return None
    if cbr >= pts[-1][0]:
        if pts[-1][1] <= 0.0:
            return 0.0
        if cbr == pts[-1][0]:
            return pts[-1][1]
        raise ValueError(
            f"Figure {fig}'s {passes:,} pass curve ends at CBR "
            f"{pts[-1][0]:g} ({pts[-1][1]:.1f} in); the chart gives no "
            f"thickness at CBR {cbr:g}.")
    lc = math.log10(cbr)
    for (c0, t0), (c1, t1) in zip(pts, pts[1:]):
        if cbr <= c1:
            f = (lc - math.log10(c0)) / (math.log10(c1) - math.log10(c0))
            return t0 + f * (t1 - t0)
    return 0.0  # pragma: no cover


def _fig_e_thickness(fig, cbr, passes):
    """Unrounded thickness and a note (or None); None above the chart."""
    levels = sorted(_FIGURES_E[fig]["curves"])
    note = None
    if passes <= levels[0]:
        if passes < levels[0]:
            note = (f"{passes:,.0f} passes is below Figure {fig}'s lowest "
                    f"curve ({levels[0]:,}); read on that curve (the safe "
                    "side).")
        return _fig_e_on_curve(fig, levels[0], cbr), note
    if passes > levels[-1]:
        lo, hi = levels[-2], levels[-1]
        note = (f"{passes:,.0f} passes is above Figure {fig}'s highest "
                f"curve ({hi:,}); extrapolated in log(passes) from its two "
                "highest curves, as Table G-1 reads the passenger car at "
                "20,000,000 passes (6.1 in).")
    else:
        hi = next(p for p in levels if p >= passes)
        lo = max(p for p in levels if p <= passes)
    t_hi = _fig_e_on_curve(fig, hi, cbr)
    if hi == lo:
        return t_hi, note
    t_lo = _fig_e_on_curve(fig, lo, cbr)
    if t_lo is None or t_hi is None:
        return None, note
    f = ((math.log10(passes) - math.log10(lo))
         / (math.log10(hi) - math.log10(lo)))
    return t_lo + f * (t_hi - t_lo), note


def figure_e_vehicle_thickness(vehicle, cbr, passes) -> dict:
    """Thickness of cover (in) above a layer of this CBR for this many
    passes of one Appendix E vehicle, read off its chart (Figures E-2 to
    E-31; see the section note above).

    Parameters
    ----------
    vehicle : str
        Vehicle key (e.g. ``"passenger_car"``, ``"truck_3_axle"``) or its
        figure number (e.g. ``"E-2"``, ``"e26"``).
    cbr : float
        CBR of the layer, 1-100 (log axis).
    passes : float
        Passes of this vehicle (its own legend, not 18-kip passes). Between
        curves the thickness is interpolated in log(passes); below the
        lowest curve that curve is read, and above the highest it is
        extrapolated in log(passes) from the two highest (as Table G-1
        does), each with a note.

    Returns
    -------
    dict
        {'vehicle', 'figure', 'caption', 'cbr', 'passes', 'thickness_in',
         'chart_read', 'tolerance', 'reference', 'note'?}. 0.0 where the
         CBR lies past the point where the curve meets the axis.

    Raises
    ------
    ValueError
        If the vehicle is not recognized; passes is not positive; the CBR
        is below 1; the thickness is above the chart's top; or the CBR is
        past the end of a curve that stops above the axis (Figure E-30).
    """
    fig = _resolve_vehicle_figure(vehicle)
    if cbr is None or cbr < 1.0:
        raise ValueError(f"CBR {cbr} is below Figure {fig}'s CBR axis "
                         "(1-100).")
    if passes is None or passes <= 0:
        raise ValueError(f"passes must be > 0, got {passes}")
    data = _FIGURES_E[fig]
    t, note = _fig_e_thickness(fig, cbr, passes)
    if t is None:
        raise ValueError(
            f"At CBR {cbr:g} and {passes:,.0f} passes the {data['caption']} "
            f"needs more than Figure {fig}'s {data['y_max_in']:g} in (the "
            "curve is above the chart); use a stronger layer or fewer "
            "passes.")
    out = {
        "vehicle": data["key"],
        "figure": fig,
        "caption": data["caption"],
        "cbr": cbr,
        "passes": passes,
        "thickness_in": round(t, 1),
        "chart_read": True,
        "tolerance": (
            "each printed curve traced on the ink (median offset 0.12-0.19 "
            "px); interpolated in log(passes) between curves"),
        "reference": _figure_e_ref(fig),
    }
    if note:
        out["note"] = note
    return out


def figure_e_vehicle_allowable_passes(vehicle, cbr, thickness_in,
                                      tol=1e-6, max_iter=60) -> dict:
    """Allowable passes of one Appendix E vehicle on this thickness over a
    layer of this CBR: the chart read in reverse, as Appendix G does
    (Tables G-1/G-2), by bisection in log(passes) on the unrounded read.

    Parameters
    ----------
    vehicle : str
        Vehicle key or figure number, as in ``figure_e_vehicle_thickness``.
    cbr : float
        CBR of the layer, 1-100.
    thickness_in : float
        Thickness of cover above the layer, in.
    tol : float, optional
        Stop when the read is within this many inches of ``thickness_in``
        (default 0.000001).
    max_iter : int, optional
        Maximum bisection steps (default 60).

    Returns
    -------
    dict
        {'vehicle', 'figure', 'cbr', 'thickness_in', 'allowable_passes',
         'chart_read', 'reference', 'clamped'?}. At or above the thickness
         of the vehicle's highest curve the passes are past the chart
         (``clamped='above_max_passes_curve'``, that curve's passes; Table
         G-1 calls them unlimited); at or below its lowest curve, or where
         every curve is above the chart, they are fewer than that curve's
         (``clamped='below_min_passes_curve'``, that curve's passes).

    Raises
    ------
    ValueError
        If the vehicle is not recognized; the CBR is below 1; thickness_in
        is not positive; or thickness_in is above the chart's top where the
        curves at this CBR are off the chart.
    """
    fig = _resolve_vehicle_figure(vehicle)
    if cbr is None or cbr < 1.0:
        raise ValueError(f"CBR {cbr} is below Figure {fig}'s CBR axis "
                         "(1-100).")
    if thickness_in is None or thickness_in <= 0:
        raise ValueError(f"thickness_in must be > 0, got {thickness_in}")
    data = _FIGURES_E[fig]
    levels = sorted(data["curves"])
    base = {"vehicle": data["key"], "figure": fig, "cbr": cbr,
            "thickness_in": thickness_in, "chart_read": True,
            "reference": _figure_e_ref(fig)}
    # None: the curve is above the chart's top at this CBR.
    t_lo = _fig_e_on_curve(fig, levels[0], cbr)
    t_hi = _fig_e_on_curve(fig, levels[-1], cbr)
    if t_hi is not None and thickness_in >= t_hi:
        return dict(base, allowable_passes=levels[-1],
                    clamped="above_max_passes_curve")
    if thickness_in > data["y_max_in"]:
        raise ValueError(
            f"{thickness_in:g} in is above Figure {fig}'s "
            f"{data['y_max_in']:g} in top, where its curves at CBR {cbr:g} "
            "are off the chart.")
    if t_lo is None or thickness_in <= t_lo:
        return dict(base, allowable_passes=levels[0],
                    clamped="below_min_passes_curve")
    lo, hi = math.log10(levels[0]), math.log10(levels[-1])
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        t, _note = _fig_e_thickness(fig, cbr, 10 ** mid)
        if t is not None and abs(t - thickness_in) < tol:
            lo = hi = mid
            break
        if t is not None and t < thickness_in:
            lo = mid
        else:
            hi = mid
    return dict(base, allowable_passes=round(10 ** (0.5 * (lo + hi))))


# ============================================================================
# Figure F-1: Rigid Pavement Design Curve -- Single Axle, Dual Tire Load
# (Appendix F; pdf_page 243, printed 224). CHART READ off the print.
#
# Worked as para 13-3 (pdf_page 56, printed 37) says: from the 28-day
# flexural strength across to the k curve, down (or up) to the pass-level
# line, across to the thickness scale.
#
# How it was read (REF-58, from the GM-298 read of 2026-10-31): the chart
# is a raster embedded in the PDF (560 x 696 px; flexural strength 1,000
# and 100 psi at y = 51 and 660, thickness 12 and 4 in at the same
# heights; frame x = 58 to 506). Each pass-level line is straight: fitted
# by least squares to its ink (residual 0.5-0.9 px). Each k curve was
# tracked row by row from the top edge, the curve labels masked, and
# fitted with one smooth curve (residual 0.3 px); its x is tabled below
# every 25 psi from 1,000 psi down to where it leaves the chart. Between k
# curves x is interpolated in log(k); between pass-level lines the height
# in log(passes).
#
# Checked against every Figure F-1 read printed in Appendix G: G-7
# (pdf_page 283, printed 264) 650 psi, k 100, 20,000,000 passes 8.1 in
# (read 8.1); G-8.11 (pdf_page 286, printed 267) 650 psi, k 325, 1,200,000
# passes 6.3 in (6.3); G-8.12 (pdf_pages 286-287) 650 psi, k 50, 1,200,000
# passes "a pavement slab 8 in thick" (7.8, 8 in once rounded up).
# ============================================================================

_FIG_F1_Y1000, _FIG_F1_Y100 = 51.0, 660.0
_FIG_F1_PX_T = (_FIG_F1_Y100 - _FIG_F1_Y1000) / 8.0   # px per inch
_FIG_F1_R_STEP = 25.0
_FIG_F1_K_MAX = 500.0   # Table 10-1 note 2 (pdf_page 50, printed 31): "a k
#                         of 500 psi/in will be the maximum used for design"

# k (pci) -> x (chart px) of the k curve at R = 1000, 975, ... psi, down to
# where the curve leaves the chart at its right edge.
_FIG_F1_K_X = {
    500: (58.1, 61.8, 65.9, 70.5, 75.4, 80.6, 86.1, 91.8, 97.7, 103.9, 110.4,
          117.3, 124.5, 132.1, 140.2, 148.8, 158.1, 167.9, 178.6, 190.0,
          202.3, 215.6, 230.1, 245.9, 263.3, 282.4, 303.7, 327.6, 354.6,
          385.4, 420.8, 461.8),
    400: (75.5, 80.4, 85.4, 90.5, 95.7, 101.2, 106.9, 112.8, 119.0, 125.5,
          132.3, 139.5, 147.0, 155.1, 163.6, 172.7, 182.4, 192.8, 204.0,
          216.0, 229.0, 243.0, 258.3, 274.9, 293.1, 313.1, 335.4, 360.2,
          388.2, 420.1, 456.7),
    300: (97.4, 102.5, 107.4, 112.5, 117.7, 123.3, 129.2, 135.4, 142.0, 148.9,
          156.2, 163.9, 171.9, 180.5, 189.5, 199.1, 209.3, 220.2, 231.8,
          244.4, 258.0, 272.6, 288.5, 305.8, 324.8, 345.6, 368.7, 394.5,
          423.4, 456.4, 494.2),
    200: (122.1, 127.2, 132.6, 138.1, 144.0, 150.0, 156.4, 163.0, 169.9,
          177.2, 184.8, 192.8, 201.2, 210.1, 219.6, 229.7, 240.4, 251.9,
          264.1, 277.2, 291.3, 306.5, 322.9, 340.8, 360.3, 381.9, 405.9,
          433.0, 463.7),
    100: (146.0, 152.0, 157.5, 163.0, 168.7, 174.7, 181.2, 188.0, 195.1,
          202.5, 210.3, 218.4, 226.9, 235.9, 245.4, 255.5, 266.4, 278.0,
          290.6, 304.1, 318.7, 334.4, 351.3, 369.7, 389.8, 412.0, 436.9,
          465.4),
    50: (167.1, 172.1, 177.5, 183.3, 189.4, 195.8, 202.5, 209.5, 216.7, 224.3,
         232.2, 240.6, 249.3, 258.6, 268.4, 278.9, 290.2, 302.3, 315.5, 329.7,
         345.2, 362.0, 380.3, 400.3, 422.0, 445.6, 471.3),
    25: (184.7, 191.0, 196.9, 202.8, 208.9, 215.2, 222.0, 229.2, 236.9, 245.1,
         253.8, 263.0, 272.7, 282.8, 293.5, 304.7, 316.5, 329.0, 342.2, 356.3,
         371.4, 387.6, 405.1, 423.9, 444.4, 466.5, 490.4),
}
# passes -> (slope, intercept) of the pass-level line, y = slope * x + b.
_FIG_F1_LINES = {
    50_000_000: (-1.5215, 700.3),
    10_000_000: (-1.4552, 715.7),
    1_000_000: (-1.3564, 738.0),
    100_000: (-1.2542, 762.9),
    30_000: (-1.1972, 775.8),
    10_000: (-1.1430, 787.8),
    3_000: (-1.0844, 803.4),
    1_000: (-1.0249, 816.2),
}
_FIG_F1_KS = sorted(_FIG_F1_K_X)
_FIG_F1_NS = sorted(_FIG_F1_LINES)


def _fig_f1_x_on_k(k, flexural_psi):
    xs = _FIG_F1_K_X[k]
    i = (1000.0 - flexural_psi) / _FIG_F1_R_STEP
    if i > len(xs) - 1 + 1e-9:
        return None
    i0 = min(int(math.floor(i)), len(xs) - 2)
    f = i - i0
    return xs[i0] + f * (xs[i0 + 1] - xs[i0])


def _fig_f1_bracket(values, v):
    hi = next(p for p in values if p >= v)
    lo = max(p for p in values if p <= v)
    return lo, hi


def figure_f1_rigid_thickness(flexural_psi, k_psi_in, passes) -> dict:
    """Required plain-concrete slab thickness (in) for an 18,000-lb
    single-axle dual-tire load (Figure F-1, Appendix F; pdf_page 243,
    printed 224), read off the printed chart as para 13-3 works it (see
    the section note above).

    Reproduces every Appendix G read of the chart: (650 psi, k 100,
    20,000,000) -> 8.1 in (G-7); (650 psi, k 325, 1,200,000) -> 6.3 in
    (G-8.11); (650 psi, k 50, 1,200,000) -> 7.8 in, "a pavement slab 8 in
    thick" once rounded up (G-8.12).

    Parameters
    ----------
    flexural_psi : float
        28-day concrete flexural strength, psi, 100-1,000 (the printed
        scale).
    k_psi_in : float
        Modulus of subgrade (or subgrade+base) reaction, psi/in (pci), at
        least 25 (the lowest curve; Table 10-1 note 1 makes 25 the minimum
        used for design). Above 500 it is taken as 500 (Table 10-1 note 2).
    passes : float
        Design equivalent 18,000-lb single-axle, dual-tire passes,
        1,000-50,000,000 (the printed pass-level lines).

    Returns
    -------
    dict
        {'flexural_psi', 'k_psi_in', 'passes', 'thickness_in',
         'below_chart', 'chart_read', 'tolerance', 'reference', 'note'?}.
        A reading under the chart's 4 in is returned as 4.0 with
        ``below_chart`` set (para 13-3's 6 in minimum slab governs).

    Raises
    ------
    ValueError
        If k is below 25 pci, the flexural strength is outside 100-1,000
        psi, passes are outside 1,000-50,000,000, or the reading is off
        the chart (a k curve that has left it, or more than 12 in).
    """
    notes = []
    k = k_psi_in
    if k is None or k < 25.0:
        raise ValueError(
            f"k {k_psi_in} pci is below Figure F-1's lowest curve (25 pci; "
            "Table 10-1 note 1 makes 25 the minimum used for design)."
        )
    if k > _FIG_F1_K_MAX:
        notes.append(
            f"k {k_psi_in:g} pci taken as {_FIG_F1_K_MAX:g} pci, the maximum "
            "used for design (Table 10-1 note 2, pdf_page 50, printed 31).")
        k = _FIG_F1_K_MAX
    if flexural_psi is None or not 100.0 <= flexural_psi <= 1000.0:
        raise ValueError(
            f"Flexural strength {flexural_psi} psi is outside Figure F-1's "
            "scale (100-1,000 psi)."
        )
    if passes is None or not 1000 * (1 - 1e-9) <= passes <= 5e7 * (1 + 1e-9):
        raise ValueError(
            f"{passes} passes is outside Figure F-1's pass-level lines "
            "(1,000 to 50,000,000)."
        )
    p = min(max(passes, 1000), 50_000_000)

    k_lo, k_hi = _fig_f1_bracket(_FIG_F1_KS, k)
    x_lo = _fig_f1_x_on_k(k_lo, flexural_psi)
    x_hi = _fig_f1_x_on_k(k_hi, flexural_psi)
    if x_lo is None or x_hi is None:
        raise ValueError(
            f"At {flexural_psi:g} psi the k {k:g} curve has left Figure "
            "F-1 (beyond its right edge); the chart gives no thickness."
        )
    if k_hi == k_lo:
        x = x_lo
    else:
        f = ((math.log10(k) - math.log10(k_lo))
             / (math.log10(k_hi) - math.log10(k_lo)))
        x = x_lo + f * (x_hi - x_lo)

    n_lo, n_hi = _fig_f1_bracket(_FIG_F1_NS, p)
    y_lo = _FIG_F1_LINES[n_lo][0] * x + _FIG_F1_LINES[n_lo][1]
    y_hi = _FIG_F1_LINES[n_hi][0] * x + _FIG_F1_LINES[n_hi][1]
    if n_hi == n_lo:
        y = y_lo
    else:
        f = ((math.log10(p) - math.log10(n_lo))
             / (math.log10(n_hi) - math.log10(n_lo)))
        y = y_lo + f * (y_hi - y_lo)
    t = 12.0 - (y - _FIG_F1_Y1000) / _FIG_F1_PX_T
    if t > 12.0 + 1e-6:
        raise ValueError(
            f"Figure F-1 reads {t:.1f} in, above its 12 in scale, for "
            f"{flexural_psi:g} psi, k {k:g} pci, {p:,.0f} passes."
        )
    below = t < 4.0
    if below:
        notes.append(
            f"Figure F-1 reads {t:.1f} in, under its 4 in scale; 4.0 is "
            "returned (the 6 in minimum slab of para 13-3, pdf_page 56, "
            "printed 37, governs).")
        t = 4.0
    out = {
        "flexural_psi": flexural_psi, "k_psi_in": k_psi_in, "passes": passes,
        "thickness_in": round(t, 1),
        "below_chart": below,
        "chart_read": True,
        "tolerance": (
            "read off the printed Figure F-1 (about 0.02 in a pixel); "
            "every Appendix G read of it (G-7, G-8.11, G-8.12) reproduced; "
            "interpolated in log(k) and log(passes) between the drawn "
            "curves and lines"),
        "reference": "UFC 3-250-01, Figure F-1 (pdf_page 243, printed 224)",
    }
    if notes:
        out["note"] = " ".join(notes)
    return out
