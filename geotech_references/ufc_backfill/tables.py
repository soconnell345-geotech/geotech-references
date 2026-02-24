"""UFC 3-220-04N backfill lookup tables.

Digitised from UFC 3-220-04N (Change 1, 2004) — Backfill for
Subsurface Structures.  All units SI.
"""

# ---------------------------------------------------------------------------
# Table data
# ---------------------------------------------------------------------------

_TABLE_COMPACTION_REQUIREMENTS = {
    "under_foundations": {
        "min_compaction_pct": 95,
        "standard": "ASTM D698",
        "notes": "Standard Proctor; within footing influence zone",
    },
    "under_floor_slabs": {
        "min_compaction_pct": 95,
        "standard": "ASTM D698",
        "notes": "Standard Proctor; top 300 mm minimum",
    },
    "under_pavements": {
        "min_compaction_pct": 95,
        "standard": "ASTM D698",
        "notes": "Standard Proctor; subgrade and base course",
    },
    "adjacent_to_structures": {
        "min_compaction_pct": 90,
        "standard": "ASTM D698",
        "notes": "Within 1.5 m of structure; use light equipment",
    },
    "pipe_bedding": {
        "min_compaction_pct": 90,
        "standard": "ASTM D698",
        "notes": "Below pipe springline",
    },
    "pipe_haunch": {
        "min_compaction_pct": 90,
        "standard": "ASTM D698",
        "notes": "Pipe springline to crown; hand or mechanical tamper",
    },
    "above_pipe": {
        "min_compaction_pct": 85,
        "standard": "ASTM D698",
        "notes": "300 mm minimum cover above pipe crown before heavy equipment",
    },
    "general_fill": {
        "min_compaction_pct": 90,
        "standard": "ASTM D698",
        "notes": "General embankment and backfill",
    },
    "structural_fill": {
        "min_compaction_pct": 95,
        "standard": "ASTM D698",
        "notes": "Under or within load-bearing structures",
    },
    "behind_retaining_walls": {
        "min_compaction_pct": 90,
        "standard": "ASTM D698",
        "notes": "Use light equipment within 1 m of wall; heavy equipment beyond",
    },
}

_TABLE_BACKFILL_MATERIAL = {
    # USCS symbol -> type, acceptability, drainage characteristics
    "gw": {"type": "I", "acceptability": "excellent", "drainage": "free_draining",
            "notes": "Well-graded gravel; best structural backfill"},
    "gp": {"type": "I", "acceptability": "good", "drainage": "free_draining",
            "notes": "Poorly graded gravel; good structural backfill"},
    "sw": {"type": "I", "acceptability": "excellent", "drainage": "free_draining",
            "notes": "Well-graded sand; excellent structural backfill"},
    "sp": {"type": "I", "acceptability": "good", "drainage": "free_draining",
            "notes": "Poorly graded sand; good structural backfill"},
    "gm": {"type": "II", "acceptability": "fair", "drainage": "semi_pervious",
            "notes": "Silty gravel; acceptable for general fill, not ideal near structures"},
    "gw-gm": {"type": "II", "acceptability": "good", "drainage": "semi_pervious",
               "notes": "Well-graded gravel with silt; acceptable for most applications"},
    "gp-gm": {"type": "II", "acceptability": "fair", "drainage": "semi_pervious",
               "notes": "Poorly graded gravel with silt"},
    "sm": {"type": "II", "acceptability": "fair", "drainage": "semi_pervious",
            "notes": "Silty sand; acceptable for general fill"},
    "sw-sm": {"type": "II", "acceptability": "fair", "drainage": "semi_pervious",
              "notes": "Well-graded sand with silt"},
    "sp-sm": {"type": "II", "acceptability": "fair", "drainage": "semi_pervious",
              "notes": "Poorly graded sand with silt"},
    "gc": {"type": "II", "acceptability": "fair", "drainage": "low_permeability",
            "notes": "Clayey gravel; use with caution near structures"},
    "gw-gc": {"type": "II", "acceptability": "fair", "drainage": "low_permeability",
              "notes": "Well-graded gravel with clay"},
    "gp-gc": {"type": "II", "acceptability": "fair", "drainage": "low_permeability",
              "notes": "Poorly graded gravel with clay"},
    "sc": {"type": "II", "acceptability": "fair", "drainage": "low_permeability",
            "notes": "Clayey sand; use with caution near structures"},
    "sw-sc": {"type": "II", "acceptability": "fair", "drainage": "low_permeability",
              "notes": "Well-graded sand with clay"},
    "sp-sc": {"type": "II", "acceptability": "fair", "drainage": "low_permeability",
              "notes": "Poorly graded sand with clay"},
    "ml": {"type": "III", "acceptability": "poor", "drainage": "impervious",
            "notes": "Low-plasticity silt; not recommended near structures"},
    "cl": {"type": "III", "acceptability": "poor", "drainage": "impervious",
            "notes": "Low-plasticity clay; limited use, avoid where drainage needed"},
    "cl-ml": {"type": "III", "acceptability": "poor", "drainage": "impervious",
              "notes": "Silty clay; limited use"},
    "mh": {"type": "unacceptable", "acceptability": "unacceptable", "drainage": "impervious",
            "notes": "High-plasticity silt; not suitable for backfill"},
    "ch": {"type": "unacceptable", "acceptability": "unacceptable", "drainage": "impervious",
            "notes": "High-plasticity clay; not suitable for backfill"},
    "ol": {"type": "unacceptable", "acceptability": "unacceptable", "drainage": "impervious",
            "notes": "Organic silt/clay; never use as backfill"},
    "oh": {"type": "unacceptable", "acceptability": "unacceptable", "drainage": "impervious",
            "notes": "Organic clay; never use as backfill"},
    "pt": {"type": "unacceptable", "acceptability": "unacceptable", "drainage": "impervious",
            "notes": "Peat; never use as backfill"},
}

_TABLE_LIFT_THICKNESS = {
    # equipment -> (max_loose_lift_mm, suitable soil types, notes)
    "hand_tamper": {
        "max_lift_mm": 100,
        "suitable_soils": ["all"],
        "notes": "Confined areas, adjacent to pipes/structures",
    },
    "mechanical_rammer": {
        "max_lift_mm": 150,
        "suitable_soils": ["cohesive", "granular"],
        "notes": "Jumping jack; good for trenches and confined areas",
    },
    "vibratory_plate_small": {
        "max_lift_mm": 200,
        "suitable_soils": ["granular"],
        "notes": "Plate compactor < 100 kg; granular soils only",
    },
    "vibratory_plate_large": {
        "max_lift_mm": 300,
        "suitable_soils": ["granular"],
        "notes": "Plate compactor 100-500 kg; granular soils",
    },
    "walk_behind_roller": {
        "max_lift_mm": 200,
        "suitable_soils": ["granular", "cohesive"],
        "notes": "Smooth drum or padfoot walk-behind",
    },
    "ride_on_smooth_drum": {
        "max_lift_mm": 250,
        "suitable_soils": ["granular"],
        "notes": "Static smooth drum roller; granular soils preferred",
    },
    "vibratory_smooth_drum": {
        "max_lift_mm": 300,
        "suitable_soils": ["granular"],
        "notes": "Vibratory smooth drum roller; best for granular soils",
    },
    "sheepsfoot_roller": {
        "max_lift_mm": 200,
        "suitable_soils": ["cohesive"],
        "notes": "Padfoot/sheepsfoot; cohesive soils only",
    },
    "pneumatic_tired_roller": {
        "max_lift_mm": 250,
        "suitable_soils": ["granular", "cohesive"],
        "notes": "Rubber-tired roller; versatile for mixed soils",
    },
}

_TABLE_EQUIPMENT_SELECTION = {
    # soil_type -> recommended equipment list (best to acceptable)
    "clean_gravel": {
        "recommended": ["vibratory_smooth_drum", "vibratory_plate_large"],
        "acceptable": ["ride_on_smooth_drum", "pneumatic_tired_roller"],
        "not_recommended": ["sheepsfoot_roller"],
        "notes": "Vibratory compaction most effective for clean gravels",
    },
    "clean_sand": {
        "recommended": ["vibratory_smooth_drum", "vibratory_plate_large"],
        "acceptable": ["vibratory_plate_small", "pneumatic_tired_roller"],
        "not_recommended": ["sheepsfoot_roller"],
        "notes": "Vibratory compaction most effective for clean sands",
    },
    "silty_sand": {
        "recommended": ["vibratory_smooth_drum", "pneumatic_tired_roller"],
        "acceptable": ["vibratory_plate_large", "walk_behind_roller"],
        "not_recommended": [],
        "notes": "Combination of vibration and kneading action effective",
    },
    "silty_gravel": {
        "recommended": ["vibratory_smooth_drum", "pneumatic_tired_roller"],
        "acceptable": ["vibratory_plate_large", "ride_on_smooth_drum"],
        "not_recommended": [],
        "notes": "Combination of vibration and kneading action effective",
    },
    "low_plasticity_clay": {
        "recommended": ["sheepsfoot_roller", "pneumatic_tired_roller"],
        "acceptable": ["mechanical_rammer", "walk_behind_roller"],
        "not_recommended": ["vibratory_plate_small", "vibratory_plate_large"],
        "notes": "Kneading action required; vibratory plates ineffective",
    },
    "low_plasticity_silt": {
        "recommended": ["sheepsfoot_roller", "pneumatic_tired_roller"],
        "acceptable": ["mechanical_rammer", "walk_behind_roller"],
        "not_recommended": ["vibratory_plate_small"],
        "notes": "Kneading action preferred; vibration may cause pumping",
    },
    "confined_area": {
        "recommended": ["hand_tamper", "mechanical_rammer"],
        "acceptable": ["vibratory_plate_small", "walk_behind_roller"],
        "not_recommended": ["ride_on_smooth_drum", "vibratory_smooth_drum", "sheepsfoot_roller"],
        "notes": "Space constraints limit equipment size; extra lifts required",
    },
}

_TABLE_DRAINAGE_REQUIREMENTS = {
    "foundation_drain": {
        "min_thickness_mm": 150,
        "min_slope_pct": 1.0,
        "min_k_m_per_s": 1.0e-3,
        "notes": "Perimeter drain around foundations; connect to outlet",
    },
    "retaining_wall_drain": {
        "min_thickness_mm": 300,
        "min_slope_pct": 2.0,
        "min_k_m_per_s": 1.0e-3,
        "notes": "Drainage blanket behind retaining walls; full height preferred",
    },
    "pavement_subdrain": {
        "min_thickness_mm": 100,
        "min_slope_pct": 0.5,
        "min_k_m_per_s": 1.0e-2,
        "notes": "Granular drainage layer under pavement base",
    },
    "pipe_bedding": {
        "min_thickness_mm": 100,
        "min_slope_pct": 0.5,
        "min_k_m_per_s": 1.0e-3,
        "notes": "Free-draining material around pipes; extend to outlet",
    },
    "blanket_drain": {
        "min_thickness_mm": 200,
        "min_slope_pct": 1.0,
        "min_k_m_per_s": 1.0e-2,
        "notes": "Horizontal drainage blanket under structures on wet sites",
    },
}


# ---------------------------------------------------------------------------
# Public lookup functions
# ---------------------------------------------------------------------------

def table_compaction_requirements(application):
    """Return minimum compaction requirements for a given application.

    Parameters
    ----------
    application : str
        One of: under_foundations, under_floor_slabs, under_pavements,
        adjacent_to_structures, pipe_bedding, pipe_haunch, above_pipe,
        general_fill, structural_fill, behind_retaining_walls.

    Returns
    -------
    dict
        Keys: application, min_compaction_pct, standard, notes.

    Raises
    ------
    ValueError
        If *application* is not recognised.
    """
    key = application.lower().strip()
    if key not in _TABLE_COMPACTION_REQUIREMENTS:
        raise ValueError(
            f"Unknown application '{application}'. "
            f"Valid: {sorted(_TABLE_COMPACTION_REQUIREMENTS)}"
        )
    row = _TABLE_COMPACTION_REQUIREMENTS[key]
    return {"application": key, **row}


def table_backfill_material_classification(uscs_class):
    """Classify a backfill material by its USCS symbol.

    Parameters
    ----------
    uscs_class : str
        Unified Soil Classification System symbol (e.g. 'GW', 'SP-SM', 'CH').

    Returns
    -------
    dict
        Keys: uscs_class, type (I/II/III/unacceptable), acceptability,
        drainage, notes.

    Raises
    ------
    ValueError
        If *uscs_class* is not recognised.
    """
    key = uscs_class.lower().strip()
    if key not in _TABLE_BACKFILL_MATERIAL:
        raise ValueError(
            f"Unknown USCS class '{uscs_class}'. "
            f"Valid: {sorted(_TABLE_BACKFILL_MATERIAL)}"
        )
    row = _TABLE_BACKFILL_MATERIAL[key]
    return {"uscs_class": key, **row}


def table_maximum_lift_thickness(equipment_type):
    """Return maximum loose lift thickness for a compaction equipment type.

    Parameters
    ----------
    equipment_type : str
        One of: hand_tamper, mechanical_rammer, vibratory_plate_small,
        vibratory_plate_large, walk_behind_roller, ride_on_smooth_drum,
        vibratory_smooth_drum, sheepsfoot_roller, pneumatic_tired_roller.

    Returns
    -------
    dict
        Keys: equipment_type, max_lift_mm, suitable_soils, notes.

    Raises
    ------
    ValueError
        If *equipment_type* is not recognised.
    """
    key = equipment_type.lower().strip()
    if key not in _TABLE_LIFT_THICKNESS:
        raise ValueError(
            f"Unknown equipment type '{equipment_type}'. "
            f"Valid: {sorted(_TABLE_LIFT_THICKNESS)}"
        )
    row = _TABLE_LIFT_THICKNESS[key]
    return {"equipment_type": key, **row}


def table_compaction_equipment_selection(soil_type):
    """Recommend compaction equipment for a given soil type.

    Parameters
    ----------
    soil_type : str
        One of: clean_gravel, clean_sand, silty_sand, silty_gravel,
        low_plasticity_clay, low_plasticity_silt, confined_area.

    Returns
    -------
    dict
        Keys: soil_type, recommended (list), acceptable (list),
        not_recommended (list), notes.

    Raises
    ------
    ValueError
        If *soil_type* is not recognised.
    """
    key = soil_type.lower().strip()
    if key not in _TABLE_EQUIPMENT_SELECTION:
        raise ValueError(
            f"Unknown soil type '{soil_type}'. "
            f"Valid: {sorted(_TABLE_EQUIPMENT_SELECTION)}"
        )
    row = _TABLE_EQUIPMENT_SELECTION[key]
    return {"soil_type": key, **row}


def table_drainage_requirements(application):
    """Return drainage layer requirements for a given application.

    Parameters
    ----------
    application : str
        One of: foundation_drain, retaining_wall_drain, pavement_subdrain,
        pipe_bedding, blanket_drain.

    Returns
    -------
    dict
        Keys: application, min_thickness_mm, min_slope_pct,
        min_k_m_per_s, notes.

    Raises
    ------
    ValueError
        If *application* is not recognised.
    """
    key = application.lower().strip()
    if key not in _TABLE_DRAINAGE_REQUIREMENTS:
        raise ValueError(
            f"Unknown application '{application}'. "
            f"Valid: {sorted(_TABLE_DRAINAGE_REQUIREMENTS)}"
        )
    row = _TABLE_DRAINAGE_REQUIREMENTS[key]
    return {"application": key, **row}
