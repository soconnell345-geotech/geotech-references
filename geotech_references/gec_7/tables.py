"""GEC-7 table lookup functions.

Digitized tables from FHWA-NHI-14-007 (GEC-7), Soil Nail Walls.
Follows the DM7 pattern: private data with ``_TABLE_*`` prefix, public
lookup functions with string matching and ``_linterp`` interpolation.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 4.2a: SPT Correlations for Cohesionless Soils
# N60 → relative density, friction angle range
# ============================================================================

_TABLE_4_2A = [
    {"n_min": 0, "n_max": 4, "density": "very_loose",
     "dr_pct": "<20", "phi_min": 25, "phi_max": 30},
    {"n_min": 4, "n_max": 10, "density": "loose",
     "dr_pct": "20-40", "phi_min": 30, "phi_max": 35},
    {"n_min": 10, "n_max": 30, "density": "medium",
     "dr_pct": "40-60", "phi_min": 35, "phi_max": 40},
    {"n_min": 30, "n_max": 50, "density": "dense",
     "dr_pct": "60-80", "phi_min": 40, "phi_max": 45},
    {"n_min": 50, "n_max": 9999, "density": "very_dense",
     "dr_pct": ">80", "phi_min": 45, "phi_max": 50},
]


def table_4_2a_spt_soil_properties(n60: float) -> dict:
    """Soil properties from SPT N60 for cohesionless soils (Table 4.2a).

    Parameters
    ----------
    n60 : float
        SPT blow count corrected for 60% hammer efficiency.

    Returns
    -------
    dict
        Keys: density, relative_density_pct, phi_min_deg, phi_max_deg.

    Raises
    ------
    ValueError
        If n60 is negative.
    """
    if n60 < 0:
        raise ValueError(f"n60 must be non-negative, got {n60}")

    for row in _TABLE_4_2A:
        if row["n_min"] <= n60 < row["n_max"]:
            return {
                "density": row["density"],
                "relative_density_pct": row["dr_pct"],
                "phi_min_deg": row["phi_min"],
                "phi_max_deg": row["phi_max"],
            }
    # Fallback for very large values
    row = _TABLE_4_2A[-1]
    return {
        "density": row["density"],
        "relative_density_pct": row["dr_pct"],
        "phi_min_deg": row["phi_min"],
        "phi_max_deg": row["phi_max"],
    }


# ============================================================================
# Table 4.3a: Elastic Properties of Various Soils
# Es in ksf (original units), Poisson's ratio dimensionless
# Conversion: 1 ksf = 47.88 kPa
# ============================================================================

_TABLE_4_3A = {
    "clay_soft": {
        "description": "Clay, soft sensitive",
        "Es_min_kPa": 2394, "Es_max_kPa": 14364,
        "nu_min": 0.4, "nu_max": 0.5,
    },
    "clay_medium_stiff": {
        "description": "Clay, medium stiff to stiff",
        "Es_min_kPa": 14364, "Es_max_kPa": 47880,
        "nu_min": 0.4, "nu_max": 0.5,
    },
    "clay_very_stiff": {
        "description": "Clay, very stiff",
        "Es_min_kPa": 47880, "Es_max_kPa": 95760,
        "nu_min": 0.4, "nu_max": 0.5,
    },
    "loess": {
        "description": "Loess",
        "Es_min_kPa": 14364, "Es_max_kPa": 57456,
        "nu_min": 0.1, "nu_max": 0.3,
    },
    "silt": {
        "description": "Silt",
        "Es_min_kPa": 1915, "Es_max_kPa": 19152,
        "nu_min": 0.3, "nu_max": 0.35,
    },
    "fine_sand_loose": {
        "description": "Fine sand, loose",
        "Es_min_kPa": 7661, "Es_max_kPa": 11491,
        "nu_min": 0.25, "nu_max": 0.25,
    },
    "fine_sand_medium_dense": {
        "description": "Fine sand, medium dense",
        "Es_min_kPa": 11491, "Es_max_kPa": 19152,
        "nu_min": 0.25, "nu_max": 0.25,
    },
    "fine_sand_dense": {
        "description": "Fine sand, dense",
        "Es_min_kPa": 19152, "Es_max_kPa": 28728,
        "nu_min": 0.25, "nu_max": 0.25,
    },
    "sand_loose": {
        "description": "Sand, loose",
        "Es_min_kPa": 9576, "Es_max_kPa": 28728,
        "nu_min": 0.20, "nu_max": 0.36,
    },
    "sand_medium_dense": {
        "description": "Sand, medium dense",
        "Es_min_kPa": 28728, "Es_max_kPa": 47880,
        "nu_min": 0.20, "nu_max": 0.36,
    },
    "sand_dense": {
        "description": "Sand, dense",
        "Es_min_kPa": 47880, "Es_max_kPa": 76608,
        "nu_min": 0.30, "nu_max": 0.40,
    },
    "gravel_loose": {
        "description": "Gravel, loose",
        "Es_min_kPa": 28728, "Es_max_kPa": 76608,
        "nu_min": 0.20, "nu_max": 0.35,
    },
    "gravel_medium_dense": {
        "description": "Gravel, medium dense",
        "Es_min_kPa": 76608, "Es_max_kPa": 95760,
        "nu_min": 0.20, "nu_max": 0.35,
    },
    "gravel_dense": {
        "description": "Gravel, dense",
        "Es_min_kPa": 95760, "Es_max_kPa": 191520,
        "nu_min": 0.30, "nu_max": 0.40,
    },
}


def table_4_3a_elastic_properties(soil_type: str) -> dict:
    """Elastic properties for various soil types (Table 4.3a).

    Returns Young's modulus range and Poisson's ratio range.
    Original data in ksf, converted to kPa (1 ksf = 47.88 kPa).

    Parameters
    ----------
    soil_type : str
        Soil type description. Examples: 'clay_soft', 'sand_loose',
        'gravel_dense', 'fine_sand_medium_dense', 'loess', 'silt'.

    Returns
    -------
    dict
        Keys: description, Es_min_kPa, Es_max_kPa, nu_min, nu_max.

    Raises
    ------
    ValueError
        If soil_type is not recognized.
    """
    key = soil_type.lower().strip().replace(" ", "_")

    if key in _TABLE_4_3A:
        return dict(_TABLE_4_3A[key])

    # Partial match
    for k, v in _TABLE_4_3A.items():
        if key in k or k in key:
            return dict(v)

    raise ValueError(
        f"Unknown soil_type '{soil_type}'. Options: "
        f"{', '.join(_TABLE_4_3A.keys())}"
    )


# ============================================================================
# Table 4.3b: Elastic Modulus from SPT
# Es = multiplier * (N1)60, in ksf (original). Convert to kPa.
# Multiplier in ksf per blow; 1 ksf = 47.88 kPa
# ============================================================================

_TABLE_4_3B = {
    "silts_sandy_silts": {
        "description": "Silts, sandy silts, slightly cohesive mixtures",
        "multiplier_ksf": 8,
    },
    "clean_fine_to_medium_sand": {
        "description": "Clean fine to medium sands and slightly silty sands",
        "multiplier_ksf": 14,
    },
    "coarse_sand": {
        "description": "Coarse sands and sands with little gravel",
        "multiplier_ksf": 20,
    },
    "sandy_gravel": {
        "description": "Sandy gravel and gravels",
        "multiplier_ksf": 24,
    },
}


def table_4_3b_elastic_modulus_spt(soil_type: str,
                                   n1_60: float) -> float:
    """Elastic modulus from SPT (N1)60 value (Table 4.3b).

    Es = multiplier * (N1)60. Original multiplier in ksf/blow,
    result returned in kPa. Conversion: 1 ksf = 47.88 kPa.

    Parameters
    ----------
    soil_type : str
        Soil type. Options: 'silts_sandy_silts', 'clean_fine_to_medium_sand',
        'coarse_sand', 'sandy_gravel'.
    n1_60 : float
        Overburden-corrected SPT blow count (N1)60.

    Returns
    -------
    float
        Elastic modulus Es in kPa.

    Raises
    ------
    ValueError
        If soil_type is not recognized or n1_60 is negative.
    """
    if n1_60 < 0:
        raise ValueError(f"n1_60 must be non-negative, got {n1_60}")

    key = soil_type.lower().strip().replace(" ", "_")

    entry = None
    if key in _TABLE_4_3B:
        entry = _TABLE_4_3B[key]
    else:
        for k, v in _TABLE_4_3B.items():
            if key in k or k in key:
                entry = v
                break

    if entry is None:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. Options: "
            f"{', '.join(_TABLE_4_3B.keys())}"
        )

    # Convert from ksf to kPa
    return entry["multiplier_ksf"] * n1_60 * 47.88


# ============================================================================
# Table 4.4a: Nominal Bond Strength for Soil Nails — Coarse-Grained Soils
# Original units: psi. Conversion: 1 psi = 6.895 kPa
# Construction methods: Rotary Drilled, Driven Casing, Augered
# ============================================================================

_TABLE_4_4A_DATA = [
    # Rotary Drilled
    {"method": "rotary_drilled", "soil": "sand_gravel",
     "description": "Sand/gravel",
     "min_psi": 15, "max_psi": 26},
    {"method": "rotary_drilled", "soil": "silty_sand",
     "description": "Silty sand",
     "min_psi": 15, "max_psi": 22},
    {"method": "rotary_drilled", "soil": "silt",
     "description": "Silt",
     "min_psi": 9, "max_psi": 11},
    {"method": "rotary_drilled", "soil": "piedmont_residual",
     "description": "Piedmont residual",
     "min_psi": 6, "max_psi": 17},
    {"method": "rotary_drilled", "soil": "fine_colluvium",
     "description": "Fine colluvium",
     "min_psi": 11, "max_psi": 22},
    # Driven Casing
    {"method": "driven_casing", "soil": "sand_gravel_low_overburden",
     "description": "Sand/gravel with low overburden",
     "min_psi": 28, "max_psi": 35},
    {"method": "driven_casing", "soil": "sand_gravel_high_overburden",
     "description": "Sand/gravel with high overburden",
     "min_psi": 41, "max_psi": 62},
    {"method": "driven_casing", "soil": "dense_moraine",
     "description": "Dense moraine",
     "min_psi": 55, "max_psi": 70},
    {"method": "driven_casing", "soil": "colluvium",
     "description": "Colluvium",
     "min_psi": 15, "max_psi": 26},
    # Augered
    {"method": "augered", "soil": "silty_sand_fill",
     "description": "Silty sand fill",
     "min_psi": 3, "max_psi": 6},
    {"method": "augered", "soil": "silty_fine_sand",
     "description": "Silty fine sand",
     "min_psi": 8, "max_psi": 13},
    {"method": "augered", "soil": "silty_clayey_sand",
     "description": "Silty clayey sand",
     "min_psi": 9, "max_psi": 20},
]


def table_4_4a_bond_strength_coarse(construction_method: str,
                                    soil_type: str) -> dict:
    """Nominal bond strength for soil nails in coarse-grained soils (Table 4.4a).

    Returns the range of nominal bond strength (qu) between the grout
    and the surrounding soil. Used to compute pullout resistance per
    unit nail length: Qu = pi * DDH * qu.

    Parameters
    ----------
    construction_method : str
        Installation method: 'rotary_drilled', 'driven_casing', or 'augered'.
    soil_type : str
        Soil type within the chosen method. Examples:
        - rotary_drilled: 'sand_gravel', 'silty_sand', 'silt',
          'piedmont_residual', 'fine_colluvium'
        - driven_casing: 'sand_gravel_low_overburden',
          'sand_gravel_high_overburden', 'dense_moraine', 'colluvium'
        - augered: 'silty_sand_fill', 'silty_fine_sand', 'silty_clayey_sand'

    Returns
    -------
    dict
        Keys: method, soil, description, min_kPa, max_kPa.

    Raises
    ------
    ValueError
        If the combination is not found.
    """
    method_key = construction_method.lower().strip().replace(" ", "_")
    soil_key = soil_type.lower().strip().replace(" ", "_")

    # Exact match
    for row in _TABLE_4_4A_DATA:
        if row["method"] == method_key and row["soil"] == soil_key:
            return {
                "method": row["method"],
                "soil": row["soil"],
                "description": row["description"],
                "min_kPa": round(row["min_psi"] * 6.895, 1),
                "max_kPa": round(row["max_psi"] * 6.895, 1),
            }

    # Partial match on soil within method
    for row in _TABLE_4_4A_DATA:
        if row["method"] == method_key:
            if soil_key in row["soil"] or row["soil"] in soil_key:
                return {
                    "method": row["method"],
                    "soil": row["soil"],
                    "description": row["description"],
                    "min_kPa": round(row["min_psi"] * 6.895, 1),
                    "max_kPa": round(row["max_psi"] * 6.895, 1),
                }

    methods = sorted(set(r["method"] for r in _TABLE_4_4A_DATA))
    soils_for_method = [
        r["soil"] for r in _TABLE_4_4A_DATA if r["method"] == method_key
    ]
    if soils_for_method:
        raise ValueError(
            f"Unknown soil_type '{soil_type}' for method '{construction_method}'. "
            f"Options: {', '.join(soils_for_method)}"
        )
    raise ValueError(
        f"Unknown construction_method '{construction_method}'. "
        f"Options: {', '.join(methods)}"
    )


# ============================================================================
# Table 4.4b: Nominal Bond Strength for Soil Nails — Fine-Grained Soils
# Original units: psi. Conversion: 1 psi = 6.895 kPa
# ============================================================================

_TABLE_4_4B_DATA = [
    # Rotary Drilled
    {"method": "rotary_drilled", "soil": "silty_clay",
     "description": "Silty clay",
     "min_psi": 5, "max_psi": 7},
    # Driven Casing
    {"method": "driven_casing", "soil": "clayey_silt",
     "description": "Clayey silt",
     "min_psi": 13, "max_psi": 20},
    # Augered
    {"method": "augered", "soil": "loess",
     "description": "Loess",
     "min_psi": 4, "max_psi": 11},
    {"method": "augered", "soil": "soft_clay",
     "description": "Soft clay",
     "min_psi": 3, "max_psi": 4},
    {"method": "augered", "soil": "stiff_clay",
     "description": "Stiff clay",
     "min_psi": 6, "max_psi": 9},
    {"method": "augered", "soil": "stiff_clayey_silt",
     "description": "Stiff clayey silt",
     "min_psi": 6, "max_psi": 15},
    {"method": "augered", "soil": "calcareous_sandy_clay",
     "description": "Calcareous sandy clay",
     "min_psi": 13, "max_psi": 20},
]


def table_4_4b_bond_strength_fine(construction_method: str,
                                  soil_type: str) -> dict:
    """Nominal bond strength for soil nails in fine-grained soils (Table 4.4b).

    Returns the range of nominal bond strength (qu) between the grout
    and surrounding fine-grained soil.

    Parameters
    ----------
    construction_method : str
        Installation method: 'rotary_drilled', 'driven_casing', or 'augered'.
    soil_type : str
        Soil type within the chosen method. Examples:
        - rotary_drilled: 'silty_clay'
        - driven_casing: 'clayey_silt'
        - augered: 'loess', 'soft_clay', 'stiff_clay',
          'stiff_clayey_silt', 'calcareous_sandy_clay'

    Returns
    -------
    dict
        Keys: method, soil, description, min_kPa, max_kPa.

    Raises
    ------
    ValueError
        If the combination is not found.
    """
    method_key = construction_method.lower().strip().replace(" ", "_")
    soil_key = soil_type.lower().strip().replace(" ", "_")

    # Exact match
    for row in _TABLE_4_4B_DATA:
        if row["method"] == method_key and row["soil"] == soil_key:
            return {
                "method": row["method"],
                "soil": row["soil"],
                "description": row["description"],
                "min_kPa": round(row["min_psi"] * 6.895, 1),
                "max_kPa": round(row["max_psi"] * 6.895, 1),
            }

    # Partial match on soil within method
    for row in _TABLE_4_4B_DATA:
        if row["method"] == method_key:
            if soil_key in row["soil"] or row["soil"] in soil_key:
                return {
                    "method": row["method"],
                    "soil": row["soil"],
                    "description": row["description"],
                    "min_kPa": round(row["min_psi"] * 6.895, 1),
                    "max_kPa": round(row["max_psi"] * 6.895, 1),
                }

    methods = sorted(set(r["method"] for r in _TABLE_4_4B_DATA))
    soils_for_method = [
        r["soil"] for r in _TABLE_4_4B_DATA if r["method"] == method_key
    ]
    if soils_for_method:
        raise ValueError(
            f"Unknown soil_type '{soil_type}' for method '{construction_method}'. "
            f"Options: {', '.join(soils_for_method)}"
        )
    raise ValueError(
        f"Unknown construction_method '{construction_method}'. "
        f"Options: {', '.join(methods)}"
    )


# ============================================================================
# Table 4.5: Nominal Bond Strength for Soil Nails — Rock
# All entries are Rotary Drilled.
# Original units: psi. Conversion: 1 psi = 6.895 kPa
# ============================================================================

_TABLE_4_5 = {
    "marl_limestone": {
        "description": "Marl/limestone",
        "min_psi": 44, "max_psi": 58,
    },
    "phyllite": {
        "description": "Phyllite",
        "min_psi": 15, "max_psi": 44,
    },
    "chalk": {
        "description": "Chalk",
        "min_psi": 73, "max_psi": 87,
    },
    "soft_dolomite": {
        "description": "Soft dolomite",
        "min_psi": 58, "max_psi": 87,
    },
    "fissured_dolomite": {
        "description": "Fissured dolomite",
        "min_psi": 87, "max_psi": 145,
    },
    "weathered_sandstone": {
        "description": "Weathered sandstone",
        "min_psi": 29, "max_psi": 44,
    },
    "weathered_shale": {
        "description": "Weathered shale",
        "min_psi": 15, "max_psi": 22,
    },
    "weathered_schist": {
        "description": "Weathered schist",
        "min_psi": 15, "max_psi": 25,
    },
    "basalt": {
        "description": "Basalt",
        "min_psi": 73, "max_psi": 87,
    },
    "slate_hard_shale": {
        "description": "Slate/hard shale",
        "min_psi": 44, "max_psi": 58,
    },
}


def table_4_5_bond_strength_rock(rock_type: str) -> dict:
    """Nominal bond strength for soil nails in rock (Table 4.5).

    All entries assume rotary drilled installation method.
    Returns the range of nominal bond strength (qu).

    Parameters
    ----------
    rock_type : str
        Rock type. Options: 'marl_limestone', 'phyllite', 'chalk',
        'soft_dolomite', 'fissured_dolomite', 'weathered_sandstone',
        'weathered_shale', 'weathered_schist', 'basalt', 'slate_hard_shale'.

    Returns
    -------
    dict
        Keys: rock_type, description, min_kPa, max_kPa.

    Raises
    ------
    ValueError
        If rock_type is not recognized.
    """
    key = rock_type.lower().strip().replace(" ", "_")

    if key in _TABLE_4_5:
        entry = _TABLE_4_5[key]
        return {
            "rock_type": key,
            "description": entry["description"],
            "min_kPa": round(entry["min_psi"] * 6.895, 1),
            "max_kPa": round(entry["max_psi"] * 6.895, 1),
        }

    # Partial match
    for k, v in _TABLE_4_5.items():
        if key in k or k in key:
            return {
                "rock_type": k,
                "description": v["description"],
                "min_kPa": round(v["min_psi"] * 6.895, 1),
                "max_kPa": round(v["max_psi"] * 6.895, 1),
            }

    raise ValueError(
        f"Unknown rock_type '{rock_type}'. Options: "
        f"{', '.join(_TABLE_4_5.keys())}"
    )


# ============================================================================
# Table 4.6: Estimated Pullout Resistance per Unit Length (Qu/L)
# For preliminary design. Original units: kip/ft.
# Conversion: 1 kip/ft = 14.594 kN/m
# ============================================================================

_TABLE_4_6_DATA = [
    {"soil": "sand_and_gravel", "density": "loose",
     "n60_min": 4, "n60_max": 10, "qu_kip_ft": 10},
    {"soil": "sand_and_gravel", "density": "medium_dense",
     "n60_min": 11, "n60_max": 30, "qu_kip_ft": 15},
    {"soil": "sand_and_gravel", "density": "dense",
     "n60_min": 31, "n60_max": 50, "qu_kip_ft": 20},
    {"soil": "sand", "density": "loose",
     "n60_min": 4, "n60_max": 10, "qu_kip_ft": 7},
    {"soil": "sand", "density": "medium_dense",
     "n60_min": 11, "n60_max": 30, "qu_kip_ft": 10},
    {"soil": "sand", "density": "dense",
     "n60_min": 31, "n60_max": 50, "qu_kip_ft": 13},
    {"soil": "sand_and_silt", "density": "loose",
     "n60_min": 4, "n60_max": 10, "qu_kip_ft": 5},
    {"soil": "sand_and_silt", "density": "medium_dense",
     "n60_min": 11, "n60_max": 30, "qu_kip_ft": 7},
    {"soil": "sand_and_silt", "density": "dense",
     "n60_min": 31, "n60_max": 50, "qu_kip_ft": 9},
    {"soil": "silt_clay_low_pi", "density": "stiff",
     "n60_min": 10, "n60_max": 20, "qu_kip_ft": 2},
    {"soil": "silt_clay_low_pi", "density": "hard",
     "n60_min": 21, "n60_max": 40, "qu_kip_ft": 4},
]


def table_4_6_pullout_resistance(soil_type: str,
                                 density: str) -> dict:
    """Estimated pullout resistance per unit length for preliminary design (Table 4.6).

    Returns the nominal pullout resistance Qu per unit nail length.
    Original data in kip/ft, converted to kN/m (1 kip/ft = 14.594 kN/m).

    Parameters
    ----------
    soil_type : str
        Soil type: 'sand_and_gravel', 'sand', 'sand_and_silt',
        'silt_clay_low_pi'.
    density : str
        Soil density: 'loose', 'medium_dense', 'dense', 'stiff', 'hard'.

    Returns
    -------
    dict
        Keys: soil_type, density, n60_min, n60_max, qu_kN_per_m.

    Raises
    ------
    ValueError
        If the combination is not found.
    """
    soil_key = soil_type.lower().strip().replace(" ", "_")
    density_key = density.lower().strip().replace(" ", "_")

    for row in _TABLE_4_6_DATA:
        if row["soil"] == soil_key and row["density"] == density_key:
            return {
                "soil_type": row["soil"],
                "density": row["density"],
                "n60_min": row["n60_min"],
                "n60_max": row["n60_max"],
                "qu_kN_per_m": round(row["qu_kip_ft"] * 14.594, 1),
            }

    # Partial match
    for row in _TABLE_4_6_DATA:
        if (soil_key in row["soil"] or row["soil"] in soil_key) and \
           row["density"] == density_key:
            return {
                "soil_type": row["soil"],
                "density": row["density"],
                "n60_min": row["n60_min"],
                "n60_max": row["n60_max"],
                "qu_kN_per_m": round(row["qu_kip_ft"] * 14.594, 1),
            }

    soils = sorted(set(r["soil"] for r in _TABLE_4_6_DATA))
    densities = sorted(set(r["density"] for r in _TABLE_4_6_DATA))
    raise ValueError(
        f"Combination soil='{soil_type}', density='{density}' not found. "
        f"Soil options: {', '.join(soils)}. "
        f"Density options: {', '.join(densities)}."
    )


# ============================================================================
# Table 4.9: Site Coefficient F_PGA (AASHTO 2014, as cited in GEC-7)
# Interpolates between PGA values for each site class.
# ============================================================================

_TABLE_4_9_PGA = [0.25, 0.50, 0.75, 1.00, 1.25]

_TABLE_4_9_FPGA = {
    "A": [0.8, 0.8, 0.8, 0.8, 0.8],
    "B": [1.0, 1.0, 1.0, 1.0, 1.0],
    "C": [1.2, 1.2, 1.1, 1.0, 1.0],
    "D": [1.6, 1.4, 1.2, 1.1, 1.0],
    "E": [2.5, 1.7, 1.2, 0.9, 0.9],
}


def table_4_9_site_coefficient_fpga(site_class: str,
                                    pga: float) -> float:
    """Site coefficient F_PGA from AASHTO 2014, as cited in GEC-7 Table 4.9.

    Parameters
    ----------
    site_class : str
        AASHTO site class: 'A', 'B', 'C', 'D', or 'E'.
    pga : float
        Peak ground acceleration coefficient (dimensionless, g units).
        Values <= 0.25 use the first column; >= 1.25 use the last.

    Returns
    -------
    float
        Site coefficient F_PGA.

    Raises
    ------
    ValueError
        If site_class is not recognized.
    """
    key = site_class.upper().strip()
    if key not in _TABLE_4_9_FPGA:
        raise ValueError(
            f"Unknown site_class '{site_class}'. Options: A, B, C, D, E"
        )

    pga_clamped = max(0.25, min(1.25, pga))
    return _linterp(pga_clamped, _TABLE_4_9_PGA, _TABLE_4_9_FPGA[key])


# ============================================================================
# Table 4.10: Site Coefficient F_v (AASHTO 2014, as cited in GEC-7)
# ============================================================================

_TABLE_4_10_S1 = [0.1, 0.2, 0.3, 0.4, 0.5]

_TABLE_4_10_FV = {
    "A": [0.8, 0.8, 0.8, 0.8, 0.8],
    "B": [1.0, 1.0, 1.0, 1.0, 1.0],
    "C": [1.7, 1.6, 1.5, 1.4, 1.3],
    "D": [2.4, 2.0, 1.8, 1.6, 1.5],
    "E": [3.5, 3.2, 2.8, 2.4, 2.4],
}


def table_4_10_site_coefficient_fv(site_class: str,
                                   s1: float) -> float:
    """Site coefficient F_v from AASHTO 2014, as cited in GEC-7 Table 4.10.

    Parameters
    ----------
    site_class : str
        AASHTO site class: 'A', 'B', 'C', 'D', or 'E'.
    s1 : float
        Spectral acceleration at 1-second period (dimensionless, g units).
        Values <= 0.1 use the first column; >= 0.5 use the last.

    Returns
    -------
    float
        Site coefficient F_v.

    Raises
    ------
    ValueError
        If site_class is not recognized.
    """
    key = site_class.upper().strip()
    if key not in _TABLE_4_10_FV:
        raise ValueError(
            f"Unknown site_class '{site_class}'. Options: A, B, C, D, E"
        )

    s1_clamped = max(0.1, min(0.5, s1))
    return _linterp(s1_clamped, _TABLE_4_10_S1, _TABLE_4_10_FV[key])


# ============================================================================
# Table 5.1: Minimum Recommended Factors of Safety (ASD)
# ============================================================================

_TABLE_5_1 = {
    "overall_stability": {
        "description": "Overall stability",
        "symbol": "FS_OS",
        "fs_static": 1.5,
        "fs_seismic": 1.1,
    },
    "short_term_excavation": {
        "description": "Short-term condition, excavation",
        "symbol": "FS_OS",
        "fs_static": 1.25,
        "fs_seismic": None,
    },
    "basal_heave_short_term": {
        "description": "Basal heave, permanent wall short-term",
        "symbol": "FS_BH",
        "fs_static": 2.0,
        "fs_seismic": 2.3,
    },
    "basal_heave_long_term": {
        "description": "Basal heave, permanent wall long-term",
        "symbol": "FS_BH",
        "fs_static": 2.5,
        "fs_seismic": 2.3,
    },
    "pullout_resistance": {
        "description": "Pullout resistance",
        "symbol": "FS_PO",
        "fs_static": 2.0,
        "fs_seismic": 1.5,
    },
    "lateral_sliding": {
        "description": "Lateral sliding",
        "symbol": "FS_LS",
        "fs_static": 1.5,
        "fs_seismic": 1.1,
    },
    "tendon_tensile_grade_60_75": {
        "description": "Tendon tensile strength (Grades 60 and 75, ASTM A615)",
        "symbol": "FS_T",
        "fs_static": 1.8,
        "fs_seismic": 1.35,
    },
    "tendon_tensile_grade_95_150": {
        "description": "Tendon tensile strength (Grades 95 and 150, ASTM A722)",
        "symbol": "FS_T",
        "fs_static": 2.0,
        "fs_seismic": 1.50,
    },
    "facing_flexure": {
        "description": "Facing flexural",
        "symbol": "FS_FF",
        "fs_static": 1.5,
        "fs_seismic": 1.1,
    },
    "facing_punching_shear": {
        "description": "Facing punching shear",
        "symbol": "FS_FP",
        "fs_static": 1.5,
        "fs_seismic": 1.1,
    },
    "headed_stud_a307": {
        "description": "Headed stud tensile (A307 bolt)",
        "symbol": "FS_FH",
        "fs_static": 2.0,
        "fs_seismic": 1.5,
    },
    "headed_stud_a325": {
        "description": "Headed stud tensile (A325 bolt)",
        "symbol": "FS_FH",
        "fs_static": 1.7,
        "fs_seismic": 1.3,
    },
}


def table_5_1_factors_of_safety(limit_state: str) -> dict:
    """Minimum recommended factors of safety for ASD design (Table 5.1).

    Parameters
    ----------
    limit_state : str
        Limit state name. Options: 'overall_stability', 'short_term_excavation',
        'basal_heave_short_term', 'basal_heave_long_term', 'pullout_resistance',
        'lateral_sliding', 'tendon_tensile_grade_60_75',
        'tendon_tensile_grade_95_150', 'facing_flexure',
        'facing_punching_shear', 'headed_stud_a307', 'headed_stud_a325'.

    Returns
    -------
    dict
        Keys: description, symbol, fs_static, fs_seismic.

    Raises
    ------
    ValueError
        If limit_state is not recognized.
    """
    key = limit_state.lower().strip().replace(" ", "_")

    if key in _TABLE_5_1:
        return dict(_TABLE_5_1[key])

    # Partial match
    for k, v in _TABLE_5_1.items():
        if key in k or k in key:
            return dict(v)

    raise ValueError(
        f"Unknown limit_state '{limit_state}'. Options: "
        f"{', '.join(_TABLE_5_1.keys())}"
    )


# ============================================================================
# Table 5.3: Load Factors for Permanent Loads (AASHTO 2014)
# ============================================================================

_TABLE_5_3 = {
    "dc_dead_loads": {
        "description": "DC: Dead loads",
        "max_factor": 1.25, "min_factor": 0.90,
    },
    "dw_wearing_surfaces": {
        "description": "DW: Loads from wearing surfaces and utilities",
        "max_factor": 1.50, "min_factor": 0.65,
    },
    "eh_active": {
        "description": "EH: Horizontal earth pressure (active condition)",
        "max_factor": 1.50, "min_factor": 0.90,
    },
    "eh_at_rest": {
        "description": "EH: Horizontal earth pressure (at-rest condition)",
        "max_factor": 1.35, "min_factor": 0.90,
    },
    "ev_overall_stability": {
        "description": "EV: Vertical earth pressure (overall stability)",
        "max_factor": 1.00, "min_factor": None,
    },
    "ev_retaining_walls": {
        "description": "EV: Vertical earth pressure (retaining walls and abutments)",
        "max_factor": 1.35, "min_factor": 1.00,
    },
    "es_earth_surcharge": {
        "description": "ES: Earth surcharge",
        "max_factor": 1.50, "min_factor": 0.75,
    },
}


def table_5_3_load_factors_permanent(load_type: str) -> dict:
    """Load factors for permanent loads from AASHTO 2014 (Table 5.3).

    Parameters
    ----------
    load_type : str
        Load type. Options: 'dc_dead_loads', 'dw_wearing_surfaces',
        'eh_active', 'eh_at_rest', 'ev_overall_stability',
        'ev_retaining_walls', 'es_earth_surcharge'.

    Returns
    -------
    dict
        Keys: description, max_factor, min_factor.

    Raises
    ------
    ValueError
        If load_type is not recognized.
    """
    key = load_type.lower().strip().replace(" ", "_")

    if key in _TABLE_5_3:
        return dict(_TABLE_5_3[key])

    # Partial match
    for k, v in _TABLE_5_3.items():
        if key in k or k in key:
            return dict(v)

    raise ValueError(
        f"Unknown load_type '{load_type}'. Options: "
        f"{', '.join(_TABLE_5_3.keys())}"
    )


# ============================================================================
# Tables 5.4 - 5.11: LRFD Resistance Factors
# Combined into a single comprehensive lookup.
# ============================================================================

_TABLE_5_RESISTANCE_FACTORS = {
    "overall_stability": {
        "table": "5.4",
        "description": "Overall stability",
        "symbol": "phi_OS",
        "static": 0.65,
        "seismic": 0.90,
    },
    "basal_heave_short_term": {
        "table": "5.5",
        "description": "Basal heave, permanent wall short-term",
        "symbol": "phi_BH",
        "static": 0.65,
        "seismic": None,
    },
    "basal_heave_long_term": {
        "table": "5.5",
        "description": "Basal heave, permanent wall long-term",
        "symbol": "phi_BH",
        "static": 0.50,
        "seismic": None,
    },
    "pullout": {
        "table": "5.6",
        "description": "Pullout resistance",
        "symbol": "phi_PO",
        "static": 0.65,
        "seismic": 0.65,
    },
    "lateral_sliding": {
        "table": "5.7",
        "description": "Lateral sliding",
        "symbol": "phi_LS",
        "static": 1.00,
        "seismic": 0.90,
    },
    "tendon_grade_60_75": {
        "table": "5.8",
        "description": "Tendon in tension, Grades 60/75 (ASTM A615)",
        "symbol": "phi_T",
        "static": 0.75,
        "seismic": 0.75,
    },
    "tendon_grade_95_150": {
        "table": "5.8",
        "description": "Tendon in tension, Grade 95/150 (ASTM A722)",
        "symbol": "phi_T",
        "static": 0.65,
        "seismic": 0.65,
    },
    "facing_flexure": {
        "table": "5.9",
        "description": "Flexure resistance at facing",
        "symbol": "phi_FF",
        "static": 0.90,
        "seismic": 0.90,
    },
    "facing_punching_shear": {
        "table": "5.10",
        "description": "Punching shear at facing",
        "symbol": "phi_FP",
        "static": 0.90,
        "seismic": 0.90,
    },
    "headed_stud_a307": {
        "table": "5.11",
        "description": "Headed stud in tension, A307 steel bolt",
        "symbol": "phi_FH",
        "static": 0.70,
        "seismic": 0.65,
    },
    "headed_stud_a325": {
        "table": "5.11",
        "description": "Headed stud in tension, A325 steel bolt",
        "symbol": "phi_FH",
        "static": 0.80,
        "seismic": 0.75,
    },
}


def table_5_resistance_factors(limit_state: str) -> dict:
    """LRFD resistance factors for soil nail wall design (Tables 5.4-5.11).

    Returns the resistance factor (phi) for the specified limit state,
    for both static and seismic loading conditions.

    Parameters
    ----------
    limit_state : str
        Limit state. Options: 'overall_stability', 'basal_heave_short_term',
        'basal_heave_long_term', 'pullout', 'lateral_sliding',
        'tendon_grade_60_75', 'tendon_grade_95_150', 'facing_flexure',
        'facing_punching_shear', 'headed_stud_a307', 'headed_stud_a325'.

    Returns
    -------
    dict
        Keys: table, description, symbol, static, seismic.

    Raises
    ------
    ValueError
        If limit_state is not recognized.
    """
    key = limit_state.lower().strip().replace(" ", "_")

    if key in _TABLE_5_RESISTANCE_FACTORS:
        return dict(_TABLE_5_RESISTANCE_FACTORS[key])

    # Partial match
    for k, v in _TABLE_5_RESISTANCE_FACTORS.items():
        if key in k or k in key:
            return dict(v)

    raise ValueError(
        f"Unknown limit_state '{limit_state}'. Options: "
        f"{', '.join(_TABLE_5_RESISTANCE_FACTORS.keys())}"
    )


# ============================================================================
# Table 5.12: Wall Displacement Parameters
# (delta_h / H)_i and C as functions of soil conditions
# From Clouterre (1993) and Byrne et al. (1998)
# ============================================================================

_TABLE_5_12 = {
    "weathered_rock_stiff_soil": {
        "description": "Weathered rock and stiff soil",
        "delta_h_over_H": 1.0 / 1000,
        "C": 0.8,
    },
    "sandy_soil": {
        "description": "Sandy soil",
        "delta_h_over_H": 1.0 / 500,
        "C": 1.25,
    },
    "fine_grained_soil": {
        "description": "Fine-grained soil",
        "delta_h_over_H": 1.0 / 333,
        "C": 1.5,
    },
}


def table_5_12_wall_displacement(soil_condition: str) -> dict:
    """Wall displacement parameters by soil condition (Table 5.12).

    Used to estimate maximum horizontal and vertical displacements
    at the top of a soil nail wall:
      delta_h = delta_v = (delta_h/H)_i * H
      D_DEF = C * (1 - tan(alpha)) * H
    where H = wall height, alpha = wall batter angle.

    Parameters
    ----------
    soil_condition : str
        Soil condition: 'weathered_rock_stiff_soil', 'sandy_soil',
        or 'fine_grained_soil'.

    Returns
    -------
    dict
        Keys: description, delta_h_over_H, C.

    Raises
    ------
    ValueError
        If soil_condition is not recognized.
    """
    key = soil_condition.lower().strip().replace(" ", "_")

    if key in _TABLE_5_12:
        return dict(_TABLE_5_12[key])

    # Partial match
    for k, v in _TABLE_5_12.items():
        if key in k or k in key:
            return dict(v)

    raise ValueError(
        f"Unknown soil_condition '{soil_condition}'. Options: "
        f"{', '.join(_TABLE_5_12.keys())}"
    )
