"""GEC-4 table lookup functions.

Tables from FHWA-IF-99-015 (GEC-4, 1999), Ground Anchors and Anchored Systems.

Key sources: PTI (1996) Recommendations for Prestressed Rock and Soil Anchors.
AASHTO Task Force 27 (1990) In-Situ Soil Improvement Techniques.
"""


# ============================================================================
# Table 6: Presumptive Ultimate Values of Load Transfer for Preliminary
# Design of Small Diameter Straight Shaft Gravity-Grouted Ground Anchors
# in Soil (Chapter 5, p. 71)
#
# Values are for gravity-grouted (Type A), straight shaft, small diameter
# anchors only.  For pressure-grouted anchors, use Table 7 bond stresses.
# Factor of safety of 2.0 applied to obtain allowable design load:
#   T_allow = transfer_load × bond_length / 2.0
# SPT N values are corrected for overburden pressure.
# ============================================================================

_TABLE_6_SOIL = {
    "sand_and_gravel": {
        "loose": {"spt_range": "4-10", "ultimate_kN_per_m": 145},
        "medium_dense": {"spt_range": "11-30", "ultimate_kN_per_m": 220},
        "dense": {"spt_range": "31-50", "ultimate_kN_per_m": 290},
    },
    "sand": {
        "loose": {"spt_range": "4-10", "ultimate_kN_per_m": 100},
        "medium_dense": {"spt_range": "11-30", "ultimate_kN_per_m": 145},
        "dense": {"spt_range": "31-50", "ultimate_kN_per_m": 190},
    },
    "sand_and_silt": {
        "loose": {"spt_range": "4-10", "ultimate_kN_per_m": 70},
        "medium_dense": {"spt_range": "11-30", "ultimate_kN_per_m": 100},
        "dense": {"spt_range": "31-50", "ultimate_kN_per_m": 130},
    },
    "silt_clay_mixture": {
        # Low plasticity silt-clay mixture or fine micaceous sand/silt
        "stiff": {"spt_range": "10-20", "ultimate_kN_per_m": 30},
        "hard": {"spt_range": "21-40", "ultimate_kN_per_m": 60},
    },
}

_SOIL_ALIASES_T6 = {
    "sand_and_gravel": "sand_and_gravel",
    "sand gravel": "sand_and_gravel",
    "gravel": "sand_and_gravel",
    "sand": "sand",
    "sand_and_silt": "sand_and_silt",
    "sand silt": "sand_and_silt",
    "silty_sand": "sand_and_silt",
    "silty sand": "sand_and_silt",
    "silt_clay_mixture": "silt_clay_mixture",
    "silt clay": "silt_clay_mixture",
    "silty_clay": "silt_clay_mixture",
    "micaceous": "silt_clay_mixture",
}

_DENSITY_ALIASES_T6 = {
    "loose": "loose",
    "medium_dense": "medium_dense",
    "medium dense": "medium_dense",
    "med_dense": "medium_dense",
    "medium": "medium_dense",
    "dense": "dense",
    "stiff": "stiff",
    "hard": "hard",
    "very_stiff": "hard",
    "very stiff": "hard",
}


def table_6_soil_anchor_transfer_load(soil_type, relative_density_or_consistency):
    """Presumptive ultimate load transfer for soil anchors (Table 6).

    For preliminary design of small diameter, straight shaft, gravity-grouted
    (Type A) ground anchors in soil.  Apply a factor of safety of 2.0 to the
    ultimate value to obtain the allowable design anchor load per unit length:

        T_allow = q_u × L_b / FS  where FS = 2.0

    Typical effective bond lengths: 4.5–12 m.  Bond lengths > 12 m do not
    significantly increase capacity for gravity-grouted anchors.  For
    pressure-grouted or post-grouted anchors use Table 7 bond stresses.

    Parameters
    ----------
    soil_type : str
        Soil description:
        'sand_and_gravel', 'sand', 'sand_and_silt',
        or 'silt_clay_mixture' (low plasticity silt-clay or fine
        micaceous sand/silt mixtures).
    relative_density_or_consistency : str
        Relative density or consistency.  For granular soils:
        'loose', 'medium_dense', or 'dense'.
        For silt-clay mixtures: 'stiff' or 'hard'.

    Returns
    -------
    dict
        {'soil_type': str, 'density_or_consistency': str,
         'spt_range': str,
         'ultimate_transfer_load_kN_per_m': float,
         'factor_of_safety': float,
         'allowable_load_per_m_kN': float,
         'notes': str}

    Raises
    ------
    ValueError
        If soil_type or relative_density is not recognized.
    """
    soil_key = soil_type.lower().strip().replace(" ", "_")
    soil_key = _SOIL_ALIASES_T6.get(soil_key, soil_key)
    if soil_key not in _TABLE_6_SOIL:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. "
            f"Valid: {sorted(_TABLE_6_SOIL)}"
        )

    dens_key = relative_density_or_consistency.lower().strip().replace(" ", "_")
    dens_key = _DENSITY_ALIASES_T6.get(dens_key, dens_key)

    soil_data = _TABLE_6_SOIL[soil_key]
    if dens_key not in soil_data:
        raise ValueError(
            f"Unknown density/consistency '{relative_density_or_consistency}' "
            f"for soil type '{soil_type}'. "
            f"Valid for this soil: {sorted(soil_data)}"
        )

    row = soil_data[dens_key]
    q_u = row["ultimate_kN_per_m"]
    fs = 2.0

    return {
        "soil_type": soil_key,
        "density_or_consistency": dens_key,
        "spt_range": row["spt_range"],
        "ultimate_transfer_load_kN_per_m": float(q_u),
        "factor_of_safety": fs,
        "allowable_load_per_m_kN": round(q_u / fs, 1),
        "notes": (
            "Table 6 (GEC-4): small diameter, straight shaft, gravity-grouted "
            "anchors only; typical bond length 4.5–12 m; SPT corrected for "
            "overburden pressure"
        ),
    }


# ============================================================================
# Table 7: Presumptive Average Ultimate Bond Stress for Ground/Grout
# Interface Along Anchor Bond Zone (after PTI, 1996)
# (Chapter 5, p. 73)
#
# Values are ranges (min, max) in MPa.
# Rock: gravity-grouted assumed.
# Cohesive soil: gravity-grouted (uniform) or pressure-grouted (by sub-type).
# Cohesionless soil: gravity-grouted or pressure-grouted (by sub-type).
# ============================================================================

_TABLE_7_ROCK = {
    "granite_basalt": {"bond_stress_min": 1.7, "bond_stress_max": 3.1},
    "dolomitic_limestone": {"bond_stress_min": 1.4, "bond_stress_max": 2.1},
    "soft_limestone": {"bond_stress_min": 1.0, "bond_stress_max": 1.4},
    "slates_hard_shales": {"bond_stress_min": 0.8, "bond_stress_max": 1.4},
    "soft_shales": {"bond_stress_min": 0.2, "bond_stress_max": 0.8},
    "sandstones": {"bond_stress_min": 0.8, "bond_stress_max": 1.7},
    "weathered_sandstones": {"bond_stress_min": 0.7, "bond_stress_max": 0.8},
    "chalk": {"bond_stress_min": 0.2, "bond_stress_max": 1.1},
    "weathered_marl": {"bond_stress_min": 0.15, "bond_stress_max": 0.25},
    "concrete": {"bond_stress_min": 1.4, "bond_stress_max": 2.8},
}

_TABLE_7_COHESIVE = {
    "gravity_grouted_all": {
        "bond_stress_min": 0.03, "bond_stress_max": 0.07,
        "description": "Gravity-grouted, straight shaft, all cohesive soils",
    },
    "pressure_soft_silty_clay": {
        "bond_stress_min": 0.03, "bond_stress_max": 0.07,
        "description": "Pressure-grouted: soft silty clay",
    },
    "pressure_silty_clay": {
        "bond_stress_min": 0.03, "bond_stress_max": 0.07,
        "description": "Pressure-grouted: silty clay",
    },
    "pressure_stiff_clay_med_high_plasticity": {
        "bond_stress_min": 0.03, "bond_stress_max": 0.10,
        "description": "Pressure-grouted: stiff clay, medium to high plasticity",
    },
    "pressure_very_stiff_clay_med_high_plasticity": {
        "bond_stress_min": 0.07, "bond_stress_max": 0.17,
        "description": "Pressure-grouted: very stiff clay, medium to high plasticity",
    },
    "pressure_stiff_clay_med_plasticity": {
        "bond_stress_min": 0.10, "bond_stress_max": 0.25,
        "description": "Pressure-grouted: stiff clay, medium plasticity",
    },
    "pressure_very_stiff_clay_med_plasticity": {
        "bond_stress_min": 0.14, "bond_stress_max": 0.35,
        "description": "Pressure-grouted: very stiff clay, medium plasticity",
    },
    "pressure_very_stiff_sandy_silt_med_plasticity": {
        "bond_stress_min": 0.28, "bond_stress_max": 0.38,
        "description": "Pressure-grouted: very stiff sandy silt, medium plasticity",
    },
}

_TABLE_7_COHESIONLESS = {
    "gravity_grouted_all": {
        "bond_stress_min": 0.07, "bond_stress_max": 0.14,
        "description": "Gravity-grouted, straight shaft, all cohesionless soils",
    },
    "pressure_fine_med_sand_med_dense_dense": {
        "bond_stress_min": 0.08, "bond_stress_max": 0.38,
        "description": "Pressure-grouted: fine-medium sand, medium dense–dense",
    },
    "pressure_med_coarse_sand_gravel_med_dense": {
        "bond_stress_min": 0.11, "bond_stress_max": 0.66,
        "description": "Pressure-grouted: medium-coarse sand (w/gravel), medium dense",
    },
    "pressure_med_coarse_sand_gravel_dense": {
        "bond_stress_min": 0.25, "bond_stress_max": 0.97,
        "description": "Pressure-grouted: medium-coarse sand (w/gravel), dense–very dense",
    },
    "pressure_silty_sands": {
        "bond_stress_min": 0.17, "bond_stress_max": 0.41,
        "description": "Pressure-grouted: silty sands",
    },
    "pressure_dense_glacial_till": {
        "bond_stress_min": 0.30, "bond_stress_max": 0.52,
        "description": "Pressure-grouted: dense glacial till",
    },
    "pressure_sandy_gravel_med_dense": {
        "bond_stress_min": 0.21, "bond_stress_max": 1.38,
        "description": "Pressure-grouted: sandy gravel, medium dense–dense",
    },
    "pressure_sandy_gravel_dense": {
        "bond_stress_min": 0.28, "bond_stress_max": 1.38,
        "description": "Pressure-grouted: sandy gravel, dense–very dense",
    },
}


def table_7_bond_stress_rock(rock_type):
    """Presumptive average ultimate bond stress for rock anchors (Table 7).

    Returns range of bond stresses at the rock/grout interface for
    gravity-grouted anchors in competent rock.  Values after PTI (1996).

    Note: Alternatively, PTI (1996) suggests the ultimate bond stress can
    be approximated as 10% of the unconfined compressive strength of the rock,
    up to a maximum of 3.1 MPa.

    Parameters
    ----------
    rock_type : str
        Rock type: 'granite_basalt', 'dolomitic_limestone', 'soft_limestone',
        'slates_hard_shales', 'soft_shales', 'sandstones',
        'weathered_sandstones', 'chalk', 'weathered_marl', 'concrete'.

    Returns
    -------
    dict
        {'rock_type': str, 'bond_stress_min_MPa': float,
         'bond_stress_max_MPa': float, 'recommended_FS': float,
         'source': str}

    Raises
    ------
    ValueError
        If rock_type is not recognized.
    """
    key = rock_type.lower().strip().replace(" ", "_").replace("-", "_")

    _aliases = {
        "granite": "granite_basalt",
        "basalt": "granite_basalt",
        "granite_and_basalt": "granite_basalt",
        "dolomitic_limestone": "dolomitic_limestone",
        "dolomite": "dolomitic_limestone",
        "soft_limestone": "soft_limestone",
        "limestone": "soft_limestone",
        "slates": "slates_hard_shales",
        "hard_shales": "slates_hard_shales",
        "slate": "slates_hard_shales",
        "soft_shale": "soft_shales",
        "shale": "soft_shales",
        "sandstone": "sandstones",
        "weathered_sandstone": "weathered_sandstones",
        "chalk": "chalk",
        "marl": "weathered_marl",
        "weathered_marl": "weathered_marl",
        "concrete": "concrete",
    }

    resolved = _aliases.get(key, key)
    if resolved not in _TABLE_7_ROCK:
        raise ValueError(
            f"Unknown rock_type '{rock_type}'. "
            f"Valid: {sorted(_TABLE_7_ROCK)}"
        )

    row = _TABLE_7_ROCK[resolved]
    return {
        "rock_type": resolved,
        "bond_stress_min_MPa": row["bond_stress_min"],
        "bond_stress_max_MPa": row["bond_stress_max"],
        "recommended_FS": 3.0,
        "source": "GEC-4 Table 7 (after PTI 1996)",
    }


def table_7_bond_stress_cohesive(sub_type="gravity_grouted_all"):
    """Presumptive average ultimate bond stress for cohesive soil anchors (Table 7).

    Returns range of bond stresses at the soil/grout interface.
    Values after PTI (1996).

    Parameters
    ----------
    sub_type : str
        Cohesive soil sub-type and grouting method. Options:
        'gravity_grouted_all' — gravity-grouted, any cohesive soil;
        'pressure_soft_silty_clay',
        'pressure_silty_clay',
        'pressure_stiff_clay_med_high_plasticity',
        'pressure_very_stiff_clay_med_high_plasticity',
        'pressure_stiff_clay_med_plasticity',
        'pressure_very_stiff_clay_med_plasticity',
        'pressure_very_stiff_sandy_silt_med_plasticity'.

    Returns
    -------
    dict
        {'sub_type': str, 'description': str,
         'bond_stress_min_MPa': float, 'bond_stress_max_MPa': float,
         'source': str}

    Raises
    ------
    ValueError
        If sub_type is not recognized.
    """
    key = sub_type.lower().strip()
    if key not in _TABLE_7_COHESIVE:
        raise ValueError(
            f"Unknown cohesive sub_type '{sub_type}'. "
            f"Valid: {sorted(_TABLE_7_COHESIVE)}"
        )
    row = _TABLE_7_COHESIVE[key]
    return {
        "sub_type": key,
        "description": row["description"],
        "bond_stress_min_MPa": row["bond_stress_min"],
        "bond_stress_max_MPa": row["bond_stress_max"],
        "source": "GEC-4 Table 7 (after PTI 1996)",
    }


def table_7_bond_stress_cohesionless(sub_type="gravity_grouted_all"):
    """Presumptive average ultimate bond stress for cohesionless soil anchors (Table 7).

    Returns range of bond stresses at the soil/grout interface.
    Values after PTI (1996).

    Parameters
    ----------
    sub_type : str
        Cohesionless soil sub-type and grouting method. Options:
        'gravity_grouted_all' — gravity-grouted, any cohesionless soil;
        'pressure_fine_med_sand_med_dense_dense',
        'pressure_med_coarse_sand_gravel_med_dense',
        'pressure_med_coarse_sand_gravel_dense',
        'pressure_silty_sands',
        'pressure_dense_glacial_till',
        'pressure_sandy_gravel_med_dense',
        'pressure_sandy_gravel_dense'.

    Returns
    -------
    dict
        {'sub_type': str, 'description': str,
         'bond_stress_min_MPa': float, 'bond_stress_max_MPa': float,
         'source': str}

    Raises
    ------
    ValueError
        If sub_type is not recognized.
    """
    key = sub_type.lower().strip()
    if key not in _TABLE_7_COHESIONLESS:
        raise ValueError(
            f"Unknown cohesionless sub_type '{sub_type}'. "
            f"Valid: {sorted(_TABLE_7_COHESIONLESS)}"
        )
    row = _TABLE_7_COHESIONLESS[key]
    return {
        "sub_type": key,
        "description": row["description"],
        "bond_stress_min_MPa": row["bond_stress_min"],
        "bond_stress_max_MPa": row["bond_stress_max"],
        "source": "GEC-4 Table 7 (after PTI 1996)",
    }


# ============================================================================
# Table 8: Presumptive Ultimate Values of Load Transfer for Preliminary
# Design of Ground Anchors in Rock (Chapter 5, p. 74)
#
# Factor of safety for design = 3.0 on ultimate transfer load.
# For intermediate geomaterials (qu = 0.5–5.0 MPa), use FS = 2.0.
# Alternatively, use 10% of UCS up to a maximum of 3.1 MPa (Table 7 approach).
# ============================================================================

_TABLE_8_ROCK = {
    "granite_basalt": {"ultimate_kN_per_m": 730},
    "dolomitic_limestone": {"ultimate_kN_per_m": 580},
    "soft_limestone": {"ultimate_kN_per_m": 440},
    "sandstone": {"ultimate_kN_per_m": 440},
    "slates_hard_shales": {"ultimate_kN_per_m": 360},
    "soft_shales": {"ultimate_kN_per_m": 150},
}

_ROCK_ALIASES_T8 = {
    "granite": "granite_basalt",
    "basalt": "granite_basalt",
    "granite_or_basalt": "granite_basalt",
    "granite_and_basalt": "granite_basalt",
    "dolomite": "dolomitic_limestone",
    "dolomitic_limestone": "dolomitic_limestone",
    "limestone": "soft_limestone",
    "soft_limestone": "soft_limestone",
    "sandstones": "sandstone",
    "sandstone": "sandstone",
    "slates": "slates_hard_shales",
    "hard_shales": "slates_hard_shales",
    "slates_and_hard_shales": "slates_hard_shales",
    "shale": "soft_shales",
    "soft_shale": "soft_shales",
    "soft_shales": "soft_shales",
}


def table_8_rock_anchor_transfer_load(rock_type):
    """Presumptive ultimate load transfer for rock anchors (Table 8).

    For preliminary design of grouted anchors in competent rock.  Apply a
    factor of safety of 3.0 to obtain the allowable design anchor load:

        T_allow = q_u × L_b / 3.0

    For weak or intermediate geomaterials (qu = 0.5–5.0 MPa), use FS = 2.0.
    Typical bond lengths: 3–10 m; minimum 3 m.

    Note: In competent rock, load transfer is concentrated in the upper
    1.5–3 m of the anchor bond zone.  Using average bond stresses over the
    full bond length is conservative.

    Parameters
    ----------
    rock_type : str
        Rock type: 'granite_basalt', 'dolomitic_limestone', 'soft_limestone',
        'sandstone', 'slates_hard_shales', or 'soft_shales'.

    Returns
    -------
    dict
        {'rock_type': str, 'ultimate_transfer_load_kN_per_m': float,
         'factor_of_safety': float, 'allowable_load_per_m_kN': float,
         'notes': str}

    Raises
    ------
    ValueError
        If rock_type is not recognized.
    """
    key = rock_type.lower().strip().replace(" ", "_").replace("-", "_")
    resolved = _ROCK_ALIASES_T8.get(key, key)
    if resolved not in _TABLE_8_ROCK:
        raise ValueError(
            f"Unknown rock_type '{rock_type}'. "
            f"Valid: {sorted(_TABLE_8_ROCK)}"
        )

    q_u = _TABLE_8_ROCK[resolved]["ultimate_kN_per_m"]
    fs = 3.0

    return {
        "rock_type": resolved,
        "ultimate_transfer_load_kN_per_m": float(q_u),
        "factor_of_safety": fs,
        "allowable_load_per_m_kN": round(q_u / fs, 1),
        "notes": (
            "Table 8 (GEC-4): bond length 3–10 m minimum 3 m; FS = 3.0 for "
            "competent rock; FS = 2.0 for weak/intermediate geomaterials "
            "(qu = 0.5–5.0 MPa)"
        ),
    }


# ============================================================================
# Table 20: Corrosion Protection Requirements (after PTI 1996)
# (Chapter 6, p. 131)
#
# Two protection classes:
#   Class I (Encapsulated Tendon): full double-barrier protection
#   Class II (Grout Protected Tendon): grout as primary barrier
# Use decision tree (Figure 63) to select class.
# ============================================================================

_TABLE_20_CORROSION = {
    "class_i": {
        "name": "Encapsulated Tendon",
        "anchorage": [
            "Trumpet (attached to bearing plate with watertight weld)",
            "Cover if exposed",
        ],
        "unbonded_length_strand": [
            "Encapsulate: individual grease-filled extruded strand sheaths "
            "with a common smooth sheath; or",
            "Encapsulate: individual grease-filled strand sheaths with "
            "grout-filled smooth sheath",
        ],
        "unbonded_length_bar": [
            "Smooth bondbreaker over grout-filled bar sheath",
        ],
        "bond_length": [
            "Corrugated HDPE or polypropylene encapsulation (grout-filled); or",
            "Fusion-bonded epoxy coating",
        ],
        "description": (
            "Full encapsulation provides double barrier against corrosion "
            "throughout anchor length"
        ),
    },
    "class_ii": {
        "name": "Grout Protected Tendon",
        "anchorage": [
            "Trumpet (attached to bearing plate)",
            "Cover if exposed",
        ],
        "unbonded_length": [
            "Grease-filled sheath; or",
            "Heat-shrink sleeve",
        ],
        "bond_length": [
            "Grout (primary and only barrier; no encapsulation)",
        ],
        "description": (
            "Grout provides the primary protective barrier; single barrier system"
        ),
    },
}


def table_20_corrosion_protection(protection_class):
    """Corrosion protection requirements for ground anchors (Table 20).

    Returns protection requirements for anchorage, unbonded length, and
    tendon bond length for the specified class.  Selection between
    Class I and Class II per Figure 63 decision tree (Chapter 6).

    Decision summary: aggressive/unknown ground → Class I (permanent);
    non-aggressive + consequences not serious → Class II acceptable;
    temporary SOE anchors in non-aggressive ground → none required.

    Parameters
    ----------
    protection_class : str
        Corrosion protection class: 'class_i' or 'class_ii'
        (also accepts 'i', 'ii', '1', '2', 'encapsulated', 'grout_protected').

    Returns
    -------
    dict
        {'class': str, 'name': str, 'description': str,
         'anchorage': list, 'bond_length': list, ...}

    Raises
    ------
    ValueError
        If protection_class is not recognized.
    """
    _aliases = {
        "class_i": "class_i",
        "class i": "class_i",
        "i": "class_i",
        "1": "class_i",
        "encapsulated": "class_i",
        "encapsulated_tendon": "class_i",
        "class_ii": "class_ii",
        "class ii": "class_ii",
        "ii": "class_ii",
        "2": "class_ii",
        "grout_protected": "class_ii",
        "grout_protected_tendon": "class_ii",
    }

    key = protection_class.lower().strip().replace(" ", "_")
    resolved = _aliases.get(key)
    if resolved is None:
        raise ValueError(
            f"Unknown protection_class '{protection_class}'. "
            "Use: 'class_i' or 'class_ii'."
        )

    row = _TABLE_20_CORROSION[resolved]
    return {"class": resolved, **row}
