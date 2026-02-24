"""UFC 3-220-05 dewatering lookup tables.

Typical hydraulic conductivity ranges, dewatering method selection,
and well screen slot sizing.  All units SI.
"""

from .._interpolation import _linterp


# ---------------------------------------------------------------------------
# Table data
# ---------------------------------------------------------------------------

_TABLE_PERMEABILITY = {
    # soil_type -> (k_min_m_per_s, k_max_m_per_s, k_typical_m_per_s, drainage)
    "clean_gravel": {
        "k_min_m_per_s": 1.0e-2,
        "k_max_m_per_s": 1.0,
        "k_typical_m_per_s": 1.0e-1,
        "drainage": "very_high",
    },
    "gravel_sand_mix": {
        "k_min_m_per_s": 1.0e-4,
        "k_max_m_per_s": 1.0e-1,
        "k_typical_m_per_s": 1.0e-2,
        "drainage": "high",
    },
    "clean_sand": {
        "k_min_m_per_s": 1.0e-5,
        "k_max_m_per_s": 1.0e-2,
        "k_typical_m_per_s": 1.0e-3,
        "drainage": "high",
    },
    "fine_sand": {
        "k_min_m_per_s": 1.0e-6,
        "k_max_m_per_s": 1.0e-4,
        "k_typical_m_per_s": 1.0e-5,
        "drainage": "moderate",
    },
    "silty_sand": {
        "k_min_m_per_s": 1.0e-7,
        "k_max_m_per_s": 1.0e-4,
        "k_typical_m_per_s": 1.0e-5,
        "drainage": "moderate",
    },
    "silt": {
        "k_min_m_per_s": 1.0e-8,
        "k_max_m_per_s": 1.0e-5,
        "k_typical_m_per_s": 1.0e-6,
        "drainage": "low",
    },
    "clay": {
        "k_min_m_per_s": 1.0e-11,
        "k_max_m_per_s": 1.0e-7,
        "k_typical_m_per_s": 1.0e-9,
        "drainage": "very_low",
    },
    "glacial_till": {
        "k_min_m_per_s": 1.0e-10,
        "k_max_m_per_s": 1.0e-5,
        "k_typical_m_per_s": 1.0e-7,
        "drainage": "low",
    },
    "fractured_rock": {
        "k_min_m_per_s": 1.0e-7,
        "k_max_m_per_s": 1.0e-2,
        "k_typical_m_per_s": 1.0e-4,
        "drainage": "variable",
    },
    "intact_rock": {
        "k_min_m_per_s": 1.0e-13,
        "k_max_m_per_s": 1.0e-8,
        "k_typical_m_per_s": 1.0e-10,
        "drainage": "negligible",
    },
}

_TABLE_DEWATERING_METHOD = {
    # soil_type -> primary and alternative methods, practical limits
    "clean_gravel": {
        "primary_method": "deep_wells",
        "alternative_methods": ["open_sumps", "eductor_wells"],
        "max_drawdown_m": 30.0,
        "notes": "High flow rates; open sumps viable for shallow excavations",
    },
    "gravel_sand_mix": {
        "primary_method": "deep_wells",
        "alternative_methods": ["wellpoints", "open_sumps"],
        "max_drawdown_m": 25.0,
        "notes": "Deep wells preferred for depths > 5 m",
    },
    "clean_sand": {
        "primary_method": "wellpoints",
        "alternative_methods": ["deep_wells", "vacuum_wellpoints"],
        "max_drawdown_m": 6.0,
        "notes": "Single-stage wellpoints limited to ~5-6 m drawdown",
    },
    "fine_sand": {
        "primary_method": "vacuum_wellpoints",
        "alternative_methods": ["eductor_wells", "wellpoints"],
        "max_drawdown_m": 5.0,
        "notes": "Vacuum assist needed for fine-grained soils",
    },
    "silty_sand": {
        "primary_method": "vacuum_wellpoints",
        "alternative_methods": ["eductor_wells", "electro_osmosis"],
        "max_drawdown_m": 5.0,
        "notes": "Vacuum assist essential; consider multi-stage",
    },
    "silt": {
        "primary_method": "eductor_wells",
        "alternative_methods": ["vacuum_wellpoints", "electro_osmosis"],
        "max_drawdown_m": 15.0,
        "notes": "Eductor wells for low-permeability soils; slow response",
    },
    "clay": {
        "primary_method": "electro_osmosis",
        "alternative_methods": ["eductor_wells"],
        "max_drawdown_m": 5.0,
        "notes": "Gravity dewatering impractical; consider cutoff walls instead",
    },
}

# Well screen slot size selection based on D10 of aquifer material
# d10_mm -> slot_size_mm (slot opening = approx 1.0-1.5 * D10)
_TABLE_SCREEN_SLOTS = [
    # (d10_min_mm, d10_max_mm, slot_size_mm, slot_number, notes)
    (0.10, 0.25, 0.25, 10, "No. 10 slot; finest available"),
    (0.25, 0.50, 0.50, 20, "No. 20 slot"),
    (0.50, 1.00, 0.75, 30, "No. 30 slot"),
    (1.00, 2.00, 1.00, 40, "No. 40 slot"),
    (2.00, 4.00, 1.50, 60, "No. 60 slot"),
    (4.00, 8.00, 2.00, 80, "No. 80 slot"),
    (8.00, 16.0, 3.00, 120, "No. 120 slot; coarse material"),
]


# ---------------------------------------------------------------------------
# Public lookup functions
# ---------------------------------------------------------------------------

def table_permeability_by_soil_type(soil_type):
    """Return typical hydraulic conductivity range for a soil type.

    Parameters
    ----------
    soil_type : str
        One of: clean_gravel, gravel_sand_mix, clean_sand, fine_sand,
        silty_sand, silt, clay, glacial_till, fractured_rock, intact_rock.

    Returns
    -------
    dict
        Keys: soil_type, k_min_m_per_s, k_max_m_per_s, k_typical_m_per_s,
        drainage.

    Raises
    ------
    ValueError
        If *soil_type* is not recognised.
    """
    key = soil_type.lower().strip()
    if key not in _TABLE_PERMEABILITY:
        raise ValueError(
            f"Unknown soil type '{soil_type}'. "
            f"Valid: {sorted(_TABLE_PERMEABILITY)}"
        )
    row = _TABLE_PERMEABILITY[key]
    return {"soil_type": key, **row}


def table_dewatering_method_selection(soil_type):
    """Recommend a dewatering method for a given soil type.

    Parameters
    ----------
    soil_type : str
        One of: clean_gravel, gravel_sand_mix, clean_sand, fine_sand,
        silty_sand, silt, clay.

    Returns
    -------
    dict
        Keys: soil_type, primary_method, alternative_methods (list),
        max_drawdown_m, notes.

    Raises
    ------
    ValueError
        If *soil_type* is not recognised.
    """
    key = soil_type.lower().strip()
    if key not in _TABLE_DEWATERING_METHOD:
        raise ValueError(
            f"Unknown soil type '{soil_type}'. "
            f"Valid: {sorted(_TABLE_DEWATERING_METHOD)}"
        )
    row = _TABLE_DEWATERING_METHOD[key]
    return {"soil_type": key, **row}


def table_well_screen_slot_size(d10_mm):
    """Select well screen slot size based on aquifer D10.

    Slot opening is selected to retain the aquifer material while
    allowing free flow.  Follows USACE guidance: slot size approx
    1.0-1.5 times D10 of the aquifer (or filter pack D10 if used).

    Parameters
    ----------
    d10_mm : float
        D10 (effective size) of aquifer material (mm).

    Returns
    -------
    dict
        Keys: d10_mm, slot_size_mm, slot_number, notes.

    Raises
    ------
    ValueError
        If d10_mm is out of the covered range (< 0.10 or > 16.0 mm).
    """
    if d10_mm <= 0:
        raise ValueError(f"d10_mm must be > 0, got {d10_mm}")

    for d10_min, d10_max, slot_mm, slot_no, notes in _TABLE_SCREEN_SLOTS:
        if d10_min <= d10_mm <= d10_max:
            return {
                "d10_mm": d10_mm,
                "slot_size_mm": slot_mm,
                "slot_number": slot_no,
                "notes": notes,
            }

    if d10_mm < 0.10:
        raise ValueError(
            f"d10_mm={d10_mm} is below minimum 0.10 mm; "
            "consider filter pack design instead of natural development"
        )
    raise ValueError(
        f"d10_mm={d10_mm} exceeds maximum 16.0 mm; "
        "use gravel pack or open intake"
    )
