"""UFC 3-260-02 pavement design lookup tables.

Frost susceptibility classification, frost design CBR reduction,
aircraft classification, pavement layer structural coefficients,
and subgrade quality classification.  All units SI.
"""

# ---------------------------------------------------------------------------
# Table data
# ---------------------------------------------------------------------------

_TABLE_FROST_SUSCEPTIBILITY = {
    # USCS class -> frost susceptibility data
    # Groups: NFS, S1, S2, F1, F2, F3, F4
    "gw": {"frost_group": "NFS", "description": "Non-frost susceptible",
            "fines_limit_pct": 3, "notes": "Excellent subgrade; no frost action"},
    "gp": {"frost_group": "NFS", "description": "Non-frost susceptible",
            "fines_limit_pct": 3, "notes": "Excellent subgrade; no frost action"},
    "sw": {"frost_group": "S1", "description": "Slightly frost susceptible",
            "fines_limit_pct": 6, "notes": "Negligible frost heave if fines < 6%"},
    "sp": {"frost_group": "S1", "description": "Slightly frost susceptible",
            "fines_limit_pct": 6, "notes": "Negligible frost heave if fines < 6%"},
    "gm": {"frost_group": "F1", "description": "Frost susceptible — gravelly soils with 3-20% fines",
            "fines_limit_pct": 20, "notes": "Moderate heave potential"},
    "gw-gm": {"frost_group": "F1", "description": "Frost susceptible — gravelly soils with fines",
               "fines_limit_pct": 15, "notes": "Moderate heave potential"},
    "gp-gm": {"frost_group": "F1", "description": "Frost susceptible — gravelly soils with fines",
               "fines_limit_pct": 15, "notes": "Moderate heave potential"},
    "gc": {"frost_group": "F2", "description": "Frost susceptible — gravelly soils with > 20% fines",
            "fines_limit_pct": 35, "notes": "Significant heave potential"},
    "gw-gc": {"frost_group": "F2", "description": "Frost susceptible — gravelly soils with clay",
              "fines_limit_pct": 35, "notes": "Significant heave potential"},
    "gp-gc": {"frost_group": "F2", "description": "Frost susceptible — gravelly soils with clay",
              "fines_limit_pct": 35, "notes": "Significant heave potential"},
    "sm": {"frost_group": "F2", "description": "Frost susceptible — sandy soils with fines",
            "fines_limit_pct": 35, "notes": "Significant heave potential"},
    "sw-sm": {"frost_group": "F2", "description": "Frost susceptible — sandy soils with silt",
              "fines_limit_pct": 15, "notes": "Moderate to significant heave"},
    "sp-sm": {"frost_group": "F2", "description": "Frost susceptible — sandy soils with silt",
              "fines_limit_pct": 15, "notes": "Moderate to significant heave"},
    "sc": {"frost_group": "F2", "description": "Frost susceptible — sandy soils with clay",
            "fines_limit_pct": 35, "notes": "Significant heave potential"},
    "sw-sc": {"frost_group": "F2", "description": "Frost susceptible — sandy soils with clay",
              "fines_limit_pct": 35, "notes": "Significant heave potential"},
    "sp-sc": {"frost_group": "F2", "description": "Frost susceptible — sandy soils with clay",
              "fines_limit_pct": 35, "notes": "Significant heave potential"},
    "ml": {"frost_group": "F3", "description": "Frost susceptible — silts and low-PI clays",
            "fines_limit_pct": 100, "notes": "High heave potential; worst frost susceptibility"},
    "cl": {"frost_group": "F3", "description": "Frost susceptible — low-plasticity clay",
            "fines_limit_pct": 100, "notes": "High heave potential"},
    "cl-ml": {"frost_group": "F3", "description": "Frost susceptible — silty clay",
              "fines_limit_pct": 100, "notes": "High heave potential"},
    "mh": {"frost_group": "F4", "description": "Frost susceptible — high-plasticity silt",
            "fines_limit_pct": 100, "notes": "Very high heave potential"},
    "ch": {"frost_group": "F4", "description": "Frost susceptible — high-plasticity clay",
            "fines_limit_pct": 100, "notes": "Very high heave potential"},
    "ol": {"frost_group": "F4", "description": "Frost susceptible — organic",
            "fines_limit_pct": 100, "notes": "Very high heave; very poor subgrade"},
    "oh": {"frost_group": "F4", "description": "Frost susceptible — organic",
            "fines_limit_pct": 100, "notes": "Very high heave; very poor subgrade"},
    "pt": {"frost_group": "F4", "description": "Frost susceptible — peat",
            "fines_limit_pct": 100, "notes": "Unsuitable as subgrade; must be removed"},
}

# Frost design CBR reduction factors by frost group
_TABLE_FROST_REDUCTION = {
    # frost_group -> weakened CBR as fraction of normal CBR
    "NFS": {"reduction_factor": 1.00, "design_cbr_method": "Use full CBR",
             "notes": "No frost weakening"},
    "S1":  {"reduction_factor": 0.90, "design_cbr_method": "90% of normal CBR",
             "notes": "Minor spring thaw weakening"},
    "S2":  {"reduction_factor": 0.80, "design_cbr_method": "80% of normal CBR",
             "notes": "Moderate spring thaw weakening"},
    "F1":  {"reduction_factor": 0.65, "design_cbr_method": "65% of normal CBR",
             "notes": "Significant thaw weakening; increased pavement required"},
    "F2":  {"reduction_factor": 0.50, "design_cbr_method": "50% of normal CBR",
             "notes": "Significant thaw weakening; thick non-frost-susceptible base"},
    "F3":  {"reduction_factor": 0.35, "design_cbr_method": "35% of normal CBR",
             "notes": "Severe thaw weakening; silts are the worst case"},
    "F4":  {"reduction_factor": 0.25, "design_cbr_method": "25% of normal CBR",
             "notes": "Very severe weakening; consider full-depth replacement"},
}

_TABLE_AIRCRAFT = {
    # aircraft_type -> design parameters
    "c-130": {
        "gross_weight_kN": 700.0,
        "max_wheel_load_kN": 97.0,
        "tire_pressure_kPa": 690.0,
        "gear_type": "tandem",
        "notes": "C-130 Hercules tactical transport",
    },
    "c-17": {
        "gross_weight_kN": 2650.0,
        "max_wheel_load_kN": 221.0,
        "tire_pressure_kPa": 1035.0,
        "gear_type": "tandem_tridem",
        "notes": "C-17 Globemaster III strategic airlifter",
    },
    "c-5": {
        "gross_weight_kN": 3490.0,
        "max_wheel_load_kN": 145.0,
        "tire_pressure_kPa": 690.0,
        "gear_type": "complex",
        "notes": "C-5 Galaxy; 28 wheels, complex gear",
    },
    "f-15": {
        "gross_weight_kN": 300.0,
        "max_wheel_load_kN": 135.0,
        "tire_pressure_kPa": 2070.0,
        "gear_type": "single",
        "notes": "F-15 Eagle fighter; high tire pressure",
    },
    "f-16": {
        "gross_weight_kN": 170.0,
        "max_wheel_load_kN": 77.0,
        "tire_pressure_kPa": 2240.0,
        "gear_type": "single",
        "notes": "F-16 Falcon fighter; very high tire pressure",
    },
    "b-747": {
        "gross_weight_kN": 3560.0,
        "max_wheel_load_kN": 223.0,
        "tire_pressure_kPa": 1380.0,
        "gear_type": "dual_tandem",
        "notes": "Boeing 747; 16 main gear wheels",
    },
    "b-737": {
        "gross_weight_kN": 780.0,
        "max_wheel_load_kN": 195.0,
        "tire_pressure_kPa": 1310.0,
        "gear_type": "dual",
        "notes": "Boeing 737; dual main gear",
    },
    "uh-60": {
        "gross_weight_kN": 100.0,
        "max_wheel_load_kN": 50.0,
        "tire_pressure_kPa": 520.0,
        "gear_type": "tailwheel",
        "notes": "UH-60 Black Hawk helicopter",
    },
}

_TABLE_LAYER_COEFFICIENTS = {
    # material_type -> structural coefficient (a) per AASHTO/UFC
    "asphalt_concrete": {
        "coefficient": 0.44,
        "typical_thickness_mm": (75, 200),
        "notes": "Hot-mix asphalt surface course; a1 = 0.44/inch",
    },
    "crushed_stone_base": {
        "coefficient": 0.14,
        "typical_thickness_mm": (150, 300),
        "notes": "Crushed aggregate base course; CBR >= 80; a2 = 0.14/inch",
    },
    "cement_treated_base": {
        "coefficient": 0.23,
        "typical_thickness_mm": (150, 250),
        "notes": "Cement-stabilized base; UCS >= 4.5 MPa; a2 = 0.23/inch",
    },
    "bituminous_treated_base": {
        "coefficient": 0.34,
        "typical_thickness_mm": (100, 200),
        "notes": "Bituminous-stabilized base; a2 = 0.34/inch",
    },
    "lime_treated_subbase": {
        "coefficient": 0.11,
        "typical_thickness_mm": (150, 300),
        "notes": "Lime-stabilized subbase; a3 = 0.11/inch",
    },
    "granular_subbase": {
        "coefficient": 0.11,
        "typical_thickness_mm": (150, 450),
        "notes": "Select granular material; CBR >= 20; a3 = 0.11/inch",
    },
    "sand_subbase": {
        "coefficient": 0.08,
        "typical_thickness_mm": (150, 450),
        "notes": "Clean sand subbase; CBR >= 10; a3 = 0.08/inch",
    },
}

_TABLE_SUBGRADE_CLASS = {
    # (cbr_min, cbr_max, quality, description)
    (0, 3): {"quality": "very_poor", "description": "Organic soils, high-plasticity clays (OH, CH, PT)"},
    (3, 7): {"quality": "poor", "description": "Fine-grained soils, silts (MH, ML, CL)"},
    (7, 20): {"quality": "fair", "description": "Sandy/silty soils, low-plasticity clays (SM, SC, GM, GC)"},
    (20, 50): {"quality": "good", "description": "Gravelly soils, well-graded sands (GW, GP, SW, SP)"},
    (50, 100): {"quality": "excellent", "description": "Well-compacted gravel, stabilized soils"},
}


# ---------------------------------------------------------------------------
# Public lookup functions
# ---------------------------------------------------------------------------

def table_frost_susceptibility(uscs_class):
    """Classify frost susceptibility by USCS soil classification.

    Parameters
    ----------
    uscs_class : str
        Unified Soil Classification System symbol (e.g. 'ML', 'GW').

    Returns
    -------
    dict
        Keys: uscs_class, frost_group (NFS/S1/S2/F1-F4),
        description, fines_limit_pct, notes.

    Raises
    ------
    ValueError
        If *uscs_class* is not recognised.
    """
    key = uscs_class.lower().strip()
    if key not in _TABLE_FROST_SUSCEPTIBILITY:
        raise ValueError(
            f"Unknown USCS class '{uscs_class}'. "
            f"Valid: {sorted(_TABLE_FROST_SUSCEPTIBILITY)}"
        )
    row = _TABLE_FROST_SUSCEPTIBILITY[key]
    return {"uscs_class": key, **row}


def table_frost_design_reduction(frost_group):
    """Return CBR reduction factor for frost design.

    During spring thaw, frost-susceptible subgrades lose strength.
    The design CBR is reduced by the factor for the given frost group.

    Parameters
    ----------
    frost_group : str
        Frost susceptibility group: NFS, S1, S2, F1, F2, F3, or F4.

    Returns
    -------
    dict
        Keys: frost_group, reduction_factor, design_cbr_method, notes.

    Raises
    ------
    ValueError
        If *frost_group* is not recognised.
    """
    key = frost_group.upper().strip()
    if key not in _TABLE_FROST_REDUCTION:
        raise ValueError(
            f"Unknown frost group '{frost_group}'. "
            f"Valid: {sorted(_TABLE_FROST_REDUCTION)}"
        )
    row = _TABLE_FROST_REDUCTION[key]
    return {"frost_group": key, **row}


def table_aircraft_classification(aircraft_type):
    """Return design parameters for a military or civilian aircraft.

    Parameters
    ----------
    aircraft_type : str
        One of: c-130, c-17, c-5, f-15, f-16, b-747, b-737, uh-60.

    Returns
    -------
    dict
        Keys: aircraft_type, gross_weight_kN, max_wheel_load_kN,
        tire_pressure_kPa, gear_type, notes.

    Raises
    ------
    ValueError
        If *aircraft_type* is not recognised.
    """
    key = aircraft_type.lower().strip()
    if key not in _TABLE_AIRCRAFT:
        raise ValueError(
            f"Unknown aircraft type '{aircraft_type}'. "
            f"Valid: {sorted(_TABLE_AIRCRAFT)}"
        )
    row = _TABLE_AIRCRAFT[key]
    return {"aircraft_type": key, **row}


def table_pavement_layer_coefficients(material_type):
    """Return AASHTO structural layer coefficient for a pavement material.

    Parameters
    ----------
    material_type : str
        One of: asphalt_concrete, crushed_stone_base, cement_treated_base,
        bituminous_treated_base, lime_treated_subbase, granular_subbase,
        sand_subbase.

    Returns
    -------
    dict
        Keys: material_type, coefficient, typical_thickness_mm (tuple),
        notes.

    Raises
    ------
    ValueError
        If *material_type* is not recognised.
    """
    key = material_type.lower().strip()
    if key not in _TABLE_LAYER_COEFFICIENTS:
        raise ValueError(
            f"Unknown material type '{material_type}'. "
            f"Valid: {sorted(_TABLE_LAYER_COEFFICIENTS)}"
        )
    row = _TABLE_LAYER_COEFFICIENTS[key]
    return {"material_type": key, **row}


def table_subgrade_class(cbr):
    """Classify subgrade quality from CBR value.

    Parameters
    ----------
    cbr : float
        California Bearing Ratio (%).

    Returns
    -------
    dict
        Keys: cbr, quality, description.

    Raises
    ------
    ValueError
        If cbr < 0 or > 100.
    """
    if cbr < 0:
        raise ValueError(f"cbr must be >= 0, got {cbr}")
    if cbr > 100:
        raise ValueError(f"cbr must be <= 100, got {cbr}")

    for (cmin, cmax), row in _TABLE_SUBGRADE_CLASS.items():
        if cmin <= cbr < cmax:
            return {"cbr": cbr, **row}

    # cbr >= 50 and <= 100
    return {"cbr": cbr, "quality": "excellent",
            "description": "Well-compacted gravel, stabilized soils"}
