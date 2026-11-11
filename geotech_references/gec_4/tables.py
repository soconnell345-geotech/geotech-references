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
        For silt-clay mixtures: 'stiff' (SPT 10-20) or 'hard' (SPT 21-40),
        the two consistencies Table 6 (p. 71) prints; 'very stiff' names
        neither and is refused (it was answered from the Hard row).

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


_TABLE_7_ROCK_FS_NOTE = (
    "Table 7 prints no factor of safety. P. 74: the allowable load in "
    "competent rock is the bond length times Table 8's ultimate transfer "
    "load divided by a factor of safety of 3.0; weak rocks such as clay "
    "shales, 'intermediate geomaterials' with unconfined compressive "
    "strengths of 0.5 to 5.0 MPa, should use a factor of safety of 2.0.")


def table_7_bond_stress_rock(rock_type):
    """Presumptive average ultimate bond stress range in MPa at the rock/grout interface, by rock type, GEC-4 Table 7 (FHWA-IF-99-015, p. 73; after PTI, 1996).

    Returns range of bond stresses at the rock/grout interface for
    gravity-grouted anchors in competent rock.  Values after PTI (1996).

    Note: Alternatively, PTI (1996) suggests the ultimate bond stress can
    be approximated as 10% of the unconfined compressive strength of the rock,
    up to a maximum of 3.1 MPa (p. 74).

    Table 7 prints no factor of safety. The result quotes p. 74: FS 3.0 on
    Table 8's ultimate transfer load in competent rock, 2.0 in weak rocks
    ("intermediate geomaterials", unconfined compressive strength 0.5 to
    5.0 MPa). 'limestone' and 'shale' name two rows each and are refused.

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
         'bond_stress_max_MPa': float, 'print_note': str, 'source': str}

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
        "slates": "slates_hard_shales",
        "hard_shales": "slates_hard_shales",
        "slates_and_hard_shales": "slates_hard_shales",
        "slate": "slates_hard_shales",
        "soft_shale": "soft_shales",
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
        "print_note": _TABLE_7_ROCK_FS_NOTE,
        "source": "GEC-4 Table 7, p. 73 (after PTI, 1996)",
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
# Design of Ground Anchors in Rock (Chapter 5, p. 74, PDF page 95)
#
# The text above the table gives two factors of safety and assigns neither
# to a row: 3.0 "in competent rock"; 2.0 for weak rocks such as clay shales,
# "intermediate geomaterials" with unconfined compressive strengths of 0.5
# to 5.0 MPa. Table 8 prints no strength for its rows, so every row returns
# both, with their conditions. Below the table PTI (1996) is quoted: the
# ultimate rock/grout bond stress about 10 percent of the rock's unconfined
# compressive strength, up to 3.1 MPa (an alternative to Table 7).
# ============================================================================

_TABLE_8_ROCK = {
    "granite_basalt": {"ultimate_kN_per_m": 730, "printed": "Granite or Basalt"},
    "dolomitic_limestone": {"ultimate_kN_per_m": 580,
                            "printed": "Dolomitic Limestone"},
    "soft_limestone": {"ultimate_kN_per_m": 440, "printed": "Soft Limestone"},
    "sandstone": {"ultimate_kN_per_m": 440, "printed": "Sandstone"},
    "slates_hard_shales": {"ultimate_kN_per_m": 360,
                           "printed": "Slates and Hard Shales"},
    "soft_shales": {"ultimate_kN_per_m": 150, "printed": "Soft Shales"},
}

# p. 74, as printed.
_TABLE_8_FS_COMPETENT = (
    "The maximum allowable anchor design load in competent rock may be "
    "determined by multiplying the bond length by the ultimate transfer load "
    "and dividing by a factor of safety of 3.0.")
_TABLE_8_FS_WEAK = (
    "In weak rocks such as clay shales, bond stress transfer is relatively "
    "uniform as compared to bond stress transfer in more competent rock. "
    "These weak rocks may be termed 'intermediate geomaterials' "
    "and have unconfined compressive strengths defined as varying from 0.5 "
    "to 5.0 MPa. Design values for evaluating anchor bond lengths in these "
    "materials should use a factor of safety of 2.0 on the ultimate load "
    "transfer value.")
_TABLE_8_PRINT_NOTE = (
    "P. 74 gives two factors of safety and Table 8 assigns neither to a "
    "rock type: \"" + _TABLE_8_FS_COMPETENT + "\" \"" + _TABLE_8_FS_WEAK
    + "\" Both are returned; which applies depends on the rock's "
    "unconfined compressive strength, which Table 8 does not print. Also "
    "p. 74: \"Lower values may be recommended after input from a geologist "
    "especially if the rock mass strength is controlled by "
    "discontinuities.\"")

_ROCK_ALIASES_T8 = {
    "granite": "granite_basalt",
    "basalt": "granite_basalt",
    "granite_or_basalt": "granite_basalt",
    "granite_and_basalt": "granite_basalt",
    "dolomite": "dolomitic_limestone",
    "dolomitic_limestone": "dolomitic_limestone",
    "soft_limestone": "soft_limestone",
    "sandstones": "sandstone",
    "sandstone": "sandstone",
    "slates": "slates_hard_shales",
    "hard_shales": "slates_hard_shales",
    "slates_and_hard_shales": "slates_hard_shales",
    "soft_shale": "soft_shales",
    "soft_shales": "soft_shales",
}


def table_8_rock_anchor_transfer_load(rock_type):
    """Presumptive ultimate load transfer in kN per metre of bond length for a ground anchor in rock, by rock type, GEC-4 Table 8 (FHWA-IF-99-015, p. 74), with both factors of safety p. 74 gives (3.0 in competent rock; 2.0 in weak rocks, "intermediate geomaterials" of unconfined compressive strength 0.5 to 5.0 MPa) and the allowable load per metre under each.

    Table 8 assigns neither factor of safety to a rock type and prints no
    strengths, so every row returns both with their printed conditions
    (``factor_of_safety_options``) and decides nothing; the page's
    sentences are quoted in ``print_note``. Allowable design load = bond
    length x ultimate transfer load / factor of safety (p. 74). Typical
    bond lengths 3 to 10 m, minimum 3 m (p. 74).

    In competent rock load is transferred only in the upper 1.5 to 3 m of
    the bond zone, so average bond stresses (Table 7) may give bond lengths
    longer than required (p. 74).

    Parameters
    ----------
    rock_type : str
        Rock type: 'granite_basalt', 'dolomitic_limestone', 'soft_limestone',
        'sandstone', 'slates_hard_shales', or 'soft_shales'.

    Returns
    -------
    dict
        {'rock_type', 'rock_type_printed', 'ultimate_transfer_load_kN_per_m',
         'factor_of_safety_options': [{'factor_of_safety', 'applies_to',
         'allowable_load_per_m_kN'}, ...], 'print_note', 'source'}

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
    return {
        "rock_type": resolved,
        "rock_type_printed": _TABLE_8_ROCK[resolved]["printed"],
        "ultimate_transfer_load_kN_per_m": float(q_u),
        "factor_of_safety_options": [
            {"factor_of_safety": 3.0,
             "applies_to": "competent rock (p. 74)",
             "allowable_load_per_m_kN": round(q_u / 3.0, 1)},
            {"factor_of_safety": 2.0,
             "applies_to": ("weak rocks such as clay shales, 'intermediate "
                            "geomaterials' with unconfined compressive "
                            "strengths of 0.5 to 5.0 MPa (p. 74)"),
             "allowable_load_per_m_kN": round(q_u / 2.0, 1)},
        ],
        "print_note": _TABLE_8_PRINT_NOTE,
        "source": "GEC-4 Table 8, p. 74",
    }


# ============================================================================
# Table 20: Corrosion Protection Requirements (modified after PTI, 1996)
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
            "Trumpet",
            "Cover if exposed",
        ],
        "unbonded_length_strand": [
            "Encapsulate tendons composed of individual grease filled "
            "extruded strand sheaths with a common smooth sheath",
            "Encapsulate tendons composed of individual grease filled "
            "strand sheaths with grout filled smooth sheath",
        ],
        "unbonded_length_bar": [
            "Use smooth bondbreaker over grout filled bar sheath",
        ],
        "bond_length": [
            "Grout-filled encapsulation or",
            "Fusion-bonded epoxy",
        ],
        "description": (
            "Full encapsulation provides double barrier against corrosion "
            "throughout anchor length"
        ),
    },
    "class_ii": {
        "name": "Grout Protected Tendon",
        "anchorage": [
            "Trumpet",
            "Cover if exposed",
        ],
        "unbonded_length": [
            "Grease-filled sheath, or",
            "Heat shrink sleeve",
        ],
        "bond_length": [
            "Grout",
        ],
        "description": (
            "Grout provides the primary protective barrier; single barrier system"
        ),
    },
}


def table_20_corrosion_protection(protection_class):
    """Corrosion protection requirements (anchorage, unbonded length, tendon bond length) for a ground anchor protection class, GEC-4 Table 20 (FHWA-IF-99-015, p. 131; modified after PTI, 1996).

    Returns protection requirements for anchorage, unbonded length, and
    tendon bond length for the specified class, in the table's words
    (Class I's unbonded items 1-2 are for strand tendons, item 3 for bar
    tendons). Selection between Class I and Class II per Figure 63
    decision tree (Chapter 6). The section after the table (p. 131) says
    the trumpet should be attached to the bearing plate for a water tight
    seal, usually by welding.

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
    return {"class": resolved, **row,
            "source": "GEC-4 Table 20, p. 131 (modified after PTI, 1996)"}
