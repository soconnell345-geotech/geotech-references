"""Micropile table lookup functions.

Digitized tables from FHWA-NHI-05-039, Micropile Design & Construction
(December 2005).  Follows the DM7 pattern: private data with ``_TABLE_*``
prefix, public lookup functions with string-matched keys.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 2-1: Micropile Classification Based on Type of Grouting
# (after Pearlman and Wolosick, 1992)
# ============================================================================

_TABLE_2_1 = {
    "a1": {
        "type": "A", "subtype": 1,
        "grouting": "Gravity grout only",
        "drill_casing": "Temporary or unlined (open hole or auger)",
        "reinforcement": "None, single bar, cage, tube or structural section",
        "grout_description": (
            "Sand/cement mortar or neat cement grout tremied to base of "
            "hole (or casing), no excess pressure applied"
        ),
    },
    "a2": {
        "type": "A", "subtype": 2,
        "grouting": "Gravity grout only",
        "drill_casing": "Permanent, full length",
        "reinforcement": "Drill casing itself",
        "grout_description": (
            "Sand/cement mortar or neat cement grout tremied to base of "
            "hole (or casing), no excess pressure applied"
        ),
    },
    "a3": {
        "type": "A", "subtype": 3,
        "grouting": "Gravity grout only",
        "drill_casing": "Permanent, upper shaft only",
        "reinforcement": (
            "Drill casing in upper shaft, bar(s) or tube in lower shaft "
            "(may extend full length)"
        ),
        "grout_description": (
            "Sand/cement mortar or neat cement grout tremied to base of "
            "hole (or casing), no excess pressure applied"
        ),
    },
    "b1": {
        "type": "B", "subtype": 1,
        "grouting": "Pressure - grouted through casing or auger during withdrawal",
        "drill_casing": "Temporary or unlined (open hole or auger)",
        "reinforcement": (
            "Monobar(s) or tube (cages rare due to lower structural capacity)"
        ),
        "grout_description": (
            "Neat cement grout is first tremied into drill casing/auger. "
            "Excess pressure (up to 1 MPa / 145 psi) is typically applied to "
            "additional grout injected during withdrawal of casing/auger"
        ),
    },
    "b2": {
        "type": "B", "subtype": 2,
        "grouting": "Pressure - grouted through casing or auger during withdrawal",
        "drill_casing": "Permanent, partial length",
        "reinforcement": "Drill casing itself",
        "grout_description": (
            "Neat cement grout is first tremied into drill casing/auger. "
            "Excess pressure (up to 1 MPa / 145 psi) is typically applied to "
            "additional grout injected during withdrawal of casing/auger"
        ),
    },
    "b3": {
        "type": "B", "subtype": 3,
        "grouting": "Pressure - grouted through casing or auger during withdrawal",
        "drill_casing": "Permanent, upper shaft only",
        "reinforcement": (
            "Drill casing in upper shaft, bar(s) or tube in lower shaft "
            "(may extend full length)"
        ),
        "grout_description": (
            "Neat cement grout is first tremied into drill casing/auger. "
            "Excess pressure (up to 1 MPa / 145 psi) is typically applied to "
            "additional grout injected during withdrawal of casing/auger"
        ),
    },
    "c1": {
        "type": "C", "subtype": 1,
        "grouting": (
            "Primary grout placed under gravity head, then one phase of "
            "secondary global pressure grouting"
        ),
        "drill_casing": "Temporary or unlined (open hole or auger)",
        "reinforcement": (
            "Single bars or tube (cages rare due to lower structural capacity)"
        ),
        "grout_description": (
            "Neat cement grout is first tremied into hole (or casing/auger). "
            "Between 15 to 25 minutes later, similar grout injected through "
            "tube (or reinforcing pipe) from head, once pressure is greater "
            "than 1 MPa (145 psi)"
        ),
    },
    "c2": {
        "type": "C", "subtype": 2,
        "grouting": (
            "Primary grout placed under gravity head, then one phase of "
            "secondary global pressure grouting"
        ),
        "drill_casing": "Not conducted",
        "reinforcement": "-",
        "grout_description": (
            "Neat cement grout is first tremied into hole (or casing/auger). "
            "Between 15 to 25 minutes later, similar grout injected through "
            "tube (or reinforcing pipe) from head, once pressure is greater "
            "than 1 MPa (145 psi)"
        ),
    },
    "c3": {
        "type": "C", "subtype": 3,
        "grouting": (
            "Primary grout placed under gravity head, then one phase of "
            "secondary global pressure grouting"
        ),
        "drill_casing": "Not conducted",
        "reinforcement": "-",
        "grout_description": (
            "Neat cement grout is first tremied into hole (or casing/auger). "
            "Between 15 to 25 minutes later, similar grout injected through "
            "tube (or reinforcing pipe) from head, once pressure is greater "
            "than 1 MPa (145 psi)"
        ),
    },
    "d1": {
        "type": "D", "subtype": 1,
        "grouting": (
            "Primary grout placed under gravity head (Type A) or under "
            "pressure (Type B). Then one or more phases of secondary "
            "global pressure grouting"
        ),
        "drill_casing": "Temporary or unlined (open hole or auger)",
        "reinforcement": (
            "Single bars or tube (cages rare due to lower structural capacity)"
        ),
        "grout_description": (
            "Neat cement grout is first tremied (Type A) and/or pressurized "
            "(Type B) into hole or casing/auger. Several hours later, "
            "similar grout injected through sleeved pipe (or sleeved "
            "reinforcement) via packers, as many times as necessary to "
            "achieve bond"
        ),
    },
    "d2": {
        "type": "D", "subtype": 2,
        "grouting": (
            "Primary grout placed under gravity head (Type A) or under "
            "pressure (Type B). Then one or more phases of secondary "
            "global pressure grouting"
        ),
        "drill_casing": "Possible only if regrout tube placed full-length outside casing",
        "reinforcement": "Drill casing itself",
        "grout_description": (
            "Neat cement grout is first tremied (Type A) and/or pressurized "
            "(Type B) into hole or casing/auger. Several hours later, "
            "similar grout injected through sleeved pipe (or sleeved "
            "reinforcement) via packers, as many times as necessary to "
            "achieve bond"
        ),
    },
    "d3": {
        "type": "D", "subtype": 3,
        "grouting": (
            "Primary grout placed under gravity head (Type A) or under "
            "pressure (Type B). Then one or more phases of secondary "
            "global pressure grouting"
        ),
        "drill_casing": "Permanent, upper shaft only",
        "reinforcement": (
            "Drill casing in upper shaft, bar(s) or tube in lower shaft "
            "(may extend full length)"
        ),
        "grout_description": (
            "Neat cement grout is first tremied (Type A) and/or pressurized "
            "(Type B) into hole or casing/auger. Several hours later, "
            "similar grout injected through sleeved pipe (or sleeved "
            "reinforcement) via packers, as many times as necessary to "
            "achieve bond"
        ),
    },
}


def table_2_1_classification(type_letter: str, subtype: int = 1) -> dict:
    """Micropile classification details by grouting type (Table 2-1).

    Returns drill casing, reinforcement, and gruting method details for the
    specified micropile type and subtype.

    Parameters
    ----------
    type_letter : str
        Micropile grouting type: 'A', 'B', 'C', or 'D'.
    subtype : int
        Subtype number: 1, 2, or 3.

    Returns
    -------
    dict
        Classification details with keys: type, subtype, grouting,
        drill_casing, reinforcement, grout_description.

    Raises
    ------
    ValueError
        If type_letter or subtype is invalid.
    """
    key = f"{type_letter.strip().lower()}{subtype}"
    if key not in _TABLE_2_1:
        valid = sorted(_TABLE_2_1.keys())
        raise ValueError(
            f"Invalid classification '{key}'. "
            f"Valid keys: {', '.join(valid)}"
        )
    return dict(_TABLE_2_1[key])


# ============================================================================
# Table 4-2: Standard Reinforcing Bar Dimensions and Yield Strengths
# ASTM A615 / A706 rebar.  Areas and diameters are standard ASTM values.
# ============================================================================

_TABLE_4_2_BARS = {
    # bar_size: {diameter_mm, area_mm2}
    "#6":  {"diameter_mm": 19.1, "area_mm2": 284},
    "#7":  {"diameter_mm": 22.2, "area_mm2": 387},
    "#8":  {"diameter_mm": 25.4, "area_mm2": 510},
    "#9":  {"diameter_mm": 28.7, "area_mm2": 645},
    "#10": {"diameter_mm": 32.3, "area_mm2": 819},
    "#11": {"diameter_mm": 35.8, "area_mm2": 1006},
    "#14": {"diameter_mm": 43.0, "area_mm2": 1452},
    "#18": {"diameter_mm": 57.3, "area_mm2": 2581},
}

# Available grades and their yield stress (MPa)
_TABLE_4_2_GRADES = {
    420: {"fy_mpa": 420, "available": ["#6", "#7", "#8"]},
    520: {"fy_mpa": 520, "available": [
        "#6", "#7", "#8", "#9", "#10", "#11", "#14", "#18"
    ]},
    550: {"fy_mpa": 550, "available": ["#14", "#18"]},
}


def table_4_2_rebar_properties(bar_size: str,
                               grade: int = 520) -> dict:
    """Reinforcing bar properties for micropile design (Table 4-2).

    Returns cross-sectional area, nominal diameter, and yield strength
    for standard ASTM reinforcing bars used in micropiles.

    Parameters
    ----------
    bar_size : str
        Bar designation, e.g., '#10', '#14', '#18'.
    grade : int
        Steel grade in MPa: 420, 520, or 550.  Default 520.

    Returns
    -------
    dict
        Keys: bar_size, grade_mpa, diameter_mm, area_mm2, yield_kn.

    Raises
    ------
    ValueError
        If bar_size or grade is invalid, or bar not available in that grade.
    """
    size = bar_size.strip().upper()
    if not size.startswith("#"):
        size = "#" + size
    if size not in _TABLE_4_2_BARS:
        raise ValueError(
            f"Unknown bar size '{bar_size}'. "
            f"Valid sizes: {', '.join(sorted(_TABLE_4_2_BARS.keys()))}"
        )
    if grade not in _TABLE_4_2_GRADES:
        raise ValueError(
            f"Unknown grade {grade}. Valid grades: 420, 520, 550"
        )
    grade_info = _TABLE_4_2_GRADES[grade]
    if size not in grade_info["available"]:
        raise ValueError(
            f"Bar {size} not available in Grade {grade}. "
            f"Available: {', '.join(grade_info['available'])}"
        )

    bar = _TABLE_4_2_BARS[size]
    fy = grade_info["fy_mpa"]
    yield_kn = round(bar["area_mm2"] * fy / 1000, 1)

    return {
        "bar_size": size,
        "grade_mpa": fy,
        "diameter_mm": bar["diameter_mm"],
        "area_mm2": bar["area_mm2"],
        "yield_kn": yield_kn,
    }


# ============================================================================
# Table 4-5: Pipe Dimensions and Yield Strengths
# API N-80 (Fy = 552 MPa) and ASTM A519/A106 (Fy = 248 MPa)
# ============================================================================

_TABLE_4_5_API_N80 = [
    # (od_mm, wall_mm, area_mm2, yield_kn)
    (139.7, 9.17, 3760, 2070),
    (139.7, 10.5, 4280, 2360),
    (177.8, 12.6, 6560, 3620),
    (177.8, 18.5, 9280, 5120),
    (244.5, 12.0, 8760, 4830),
]

_TABLE_4_5_ASTM_A519 = [
    # (od_mm, wall_mm, area_mm2, yield_kn)
    (139.7, 12.7, 5067, 1270),
    (168.3, 12.7, 6208, 1540),
    (203.2, 12.7, 7600, 1890),
    (273.1, 16.0, 12850, 3190),
]


def table_4_5_pipe_properties(od_mm: float,
                              wall_mm: float = 0.0,
                              steel_type: str = "n80") -> dict:
    """Pipe dimensions and yield strength for micropile casing (Table 4-5).

    Looks up the closest matching pipe size from the table.

    Parameters
    ----------
    od_mm : float
        Outside diameter in mm (e.g., 139.7, 177.8, 244.5).
    wall_mm : float
        Wall thickness in mm.  If 0, returns all pipes with that OD.
    steel_type : str
        'n80' for API N-80 (Fy=552 MPa) or 'a519' for ASTM A519/A106
        (Fy=248 MPa).  Case-insensitive.

    Returns
    -------
    dict or list of dict
        Pipe properties: od_mm, wall_mm, area_mm2, yield_kn, fy_mpa.
        Returns a list if wall_mm=0 and multiple sizes match.

    Raises
    ------
    ValueError
        If no matching pipe is found.
    """
    st = steel_type.strip().lower().replace("-", "").replace(" ", "")
    if st in ("n80", "apin80", "api"):
        table = _TABLE_4_5_API_N80
        fy = 552
    elif st in ("a519", "a106", "astm", "astma519", "astma106"):
        table = _TABLE_4_5_ASTM_A519
        fy = 248
    else:
        raise ValueError(
            f"Unknown steel_type '{steel_type}'. Use 'n80' or 'a519'."
        )

    matches = []
    for od, wall, area, yld in table:
        if abs(od - od_mm) < 1.0:
            if wall_mm > 0 and abs(wall - wall_mm) > 0.5:
                continue
            matches.append({
                "od_mm": od,
                "wall_mm": wall,
                "area_mm2": area,
                "yield_kn": yld,
                "fy_mpa": fy,
                "steel_type": "API N-80" if fy == 552 else "ASTM A519/A106",
            })

    if not matches:
        valid_ods = sorted({od for od, *_ in table})
        raise ValueError(
            f"No pipe found for OD={od_mm}mm, wall={wall_mm}mm in "
            f"{steel_type}. Available ODs: {valid_ods}"
        )
    if len(matches) == 1:
        return matches[0]
    return matches


# ============================================================================
# Table 5-3: Grout-to-Ground Bond Strength (alpha_bond) by Soil/Rock Type
# Ultimate bond stress in kPa for micropile Types A, B, C, D.
# Rock types generally only use Type A (gravity grout).
# ============================================================================

_TABLE_5_3_SOIL_TYPES = {
    "silt_clay_soft": "Silt & Clay (soft, medium plastic)",
    "silt_clay_stiff": "Silt & Clay (stiff, dense to very dense)",
    "sand_fine_loose": "Sand (some silt), fine, loose-medium dense",
    "sand_coarse_dense": "Sand (some silt/gravel), fine-coarse, medium-very dense",
    "gravel": "Gravel (some sand), medium-very dense",
    "glacial_till": "Glacial Till (silt, sand, gravel, dense-very dense)",
    "soft_shale": "Soft Shales",
    "hard_shale": "Slates and Hard Shales",
    "limestone": "Limestone",
    "sandstone": "Sandstone",
    "granite_basalt": "Granite and Basalt",
}

# {soil_key: {micropile_type: (min_kPa, max_kPa)}}
_TABLE_5_3_BOND = {
    "silt_clay_soft":    {"A": (35, 70),   "B": (35, 95),   "C": (50, 120),  "D": (50, 145)},
    "silt_clay_stiff":   {"A": (50, 120),  "B": (70, 190),  "C": (95, 190),  "D": (95, 190)},
    "sand_fine_loose":   {"A": (70, 145),  "B": (70, 190),  "C": (95, 190),  "D": (95, 240)},
    "sand_coarse_dense": {"A": (95, 215),  "B": (120, 360), "C": (145, 360), "D": (145, 385)},
    "gravel":            {"A": (95, 265),  "B": (120, 360), "C": (145, 360), "D": (145, 385)},
    "glacial_till":      {"A": (95, 190),  "B": (95, 310),  "C": (120, 310), "D": (120, 335)},
    "soft_shale":        {"A": (205, 550)},
    "hard_shale":        {"A": (515, 1380)},
    "limestone":         {"A": (1035, 2070)},
    "sandstone":         {"A": (520, 1725)},
    "granite_basalt":    {"A": (1380, 4200)},
}


def table_5_3_alpha_bond(soil_type: str,
                         micropile_type: str = "B") -> dict:
    """Grout-to-ground ultimate bond strength for micropiles (Table 5-3).

    Returns the range of alpha_bond (ultimate grout-to-ground bond stress)
    in kPa for the given soil/rock type and micropile grouting type.

    Parameters
    ----------
    soil_type : str
        Soil or rock type key.  Accepts snake_case or partial match:
        'silt_clay_soft', 'silt_clay_stiff', 'sand_fine_loose',
        'sand_coarse_dense', 'gravel', 'glacial_till', 'soft_shale',
        'hard_shale', 'limestone', 'sandstone', 'granite_basalt'.
    micropile_type : str
        Grouting type: 'A', 'B', 'C', or 'D'.  Default 'B'.
        Rock types only support Type A.

    Returns
    -------
    dict
        Keys: soil_type, soil_description, micropile_type,
        alpha_bond_min_kpa, alpha_bond_max_kpa.

    Raises
    ------
    ValueError
        If soil_type or micropile_type is invalid.
    """
    key = soil_type.strip().lower().replace(" ", "_")
    mp = micropile_type.strip().upper()

    # Try exact match first
    if key not in _TABLE_5_3_BOND:
        # Try partial match
        matches = [k for k in _TABLE_5_3_BOND if key in k]
        if len(matches) == 1:
            key = matches[0]
        elif matches:
            raise ValueError(
                f"Ambiguous soil_type '{soil_type}'. "
                f"Matches: {', '.join(matches)}"
            )
        else:
            raise ValueError(
                f"Unknown soil_type '{soil_type}'. "
                f"Valid types: {', '.join(sorted(_TABLE_5_3_BOND.keys()))}"
            )

    bond_data = _TABLE_5_3_BOND[key]
    if mp not in bond_data:
        available = sorted(bond_data.keys())
        raise ValueError(
            f"Micropile type '{mp}' not available for {key}. "
            f"Available: {', '.join(available)}"
        )

    lo, hi = bond_data[mp]
    return {
        "soil_type": key,
        "soil_description": _TABLE_5_3_SOIL_TYPES[key],
        "micropile_type": mp,
        "alpha_bond_min_kpa": lo,
        "alpha_bond_max_kpa": hi,
    }


# ============================================================================
# Table 5-4: Efficiency Factors for Micropile Groups in Cohesive Soils
# ============================================================================

_TABLE_5_4 = {
    "cap_firm_contact": {
        "description": "Cap in firm contact with ground, any spacing",
        "efficiency": 1.0,
    },
    "cap_no_contact_stiff": {
        "description": (
            "Cap not in firm contact, stiff cohesive soil (su > 95 kPa)"
        ),
        "efficiency": 1.0,
    },
    "cap_no_contact_soft_2.5d": {
        "description": (
            "Cap not in firm contact, soft cohesive soil, s/Db = 2.5"
        ),
        "efficiency": 0.65,
    },
    "cap_no_contact_soft_3d": {
        "description": (
            "Cap not in firm contact, soft cohesive soil, s/Db = 3.0"
        ),
        "efficiency": 0.70,
    },
    "cap_no_contact_soft_6d": {
        "description": (
            "Cap not in firm contact, soft cohesive soil, s/Db >= 6.0"
        ),
        "efficiency": 1.0,
    },
}


def table_5_4_group_efficiency(condition: str = "") -> dict:
    """Group efficiency factors for micropiles in cohesive soils (Table 5-4).

    Parameters
    ----------
    condition : str
        Condition key.  If empty, returns all conditions.
        Valid keys: 'cap_firm_contact', 'cap_no_contact_stiff',
        'cap_no_contact_soft_2.5d', 'cap_no_contact_soft_3d',
        'cap_no_contact_soft_6d'.

    Returns
    -------
    dict
        Efficiency factor(s).  If condition specified, returns single
        entry with description and efficiency.  Otherwise returns all.

    Raises
    ------
    ValueError
        If condition is not recognized.
    """
    if not condition:
        return {k: dict(v) for k, v in _TABLE_5_4.items()}

    key = condition.strip().lower().replace(" ", "_")
    if key not in _TABLE_5_4:
        raise ValueError(
            f"Unknown condition '{condition}'. "
            f"Valid: {', '.join(sorted(_TABLE_5_4.keys()))}"
        )
    return dict(_TABLE_5_4[key])


# ============================================================================
# Table 5-5: Criteria for Assessing Corrosion Potential
# ============================================================================

_TABLE_5_5 = {
    "ph": {"parameter": "pH", "aggressive_if": "< 5.0 or > 10.0",
            "threshold_low": 5.0, "threshold_high": 10.0,
            "unit": "-"},
    "resistivity": {"parameter": "Resistivity", "aggressive_if": "< 3000",
                    "threshold": 3000, "unit": "ohm-cm"},
    "sulfates": {"parameter": "Sulfate concentration", "aggressive_if": "> 200",
                 "threshold": 200, "unit": "ppm"},
    "chlorides": {"parameter": "Chloride concentration", "aggressive_if": "> 100",
                  "threshold": 100, "unit": "ppm"},
}


def table_5_5_corrosion_criteria() -> dict:
    """Criteria for assessing corrosion potential of soils (Table 5-5).

    Returns criteria that indicate an aggressive environment for micropile
    corrosion.  Any single criterion exceeded indicates potential for
    aggressive conditions.

    Returns
    -------
    dict
        Corrosion criteria keyed by parameter name.
    """
    return {k: dict(v) for k, v in _TABLE_5_5.items()}


# ============================================================================
# Table 5-7: Representative Values of epsilon_50 for Intact Clays
# (after Matlock, 1970, and Reese & Welch, 1975)
# ============================================================================

_TABLE_5_7 = {
    "soft": {"consistency": "Soft clay", "su_range_kpa": (0, 48),
             "epsilon_50": 0.020},
    "medium": {"consistency": "Medium clay", "su_range_kpa": (48, 96),
               "epsilon_50": 0.010},
    "stiff": {"consistency": "Stiff clay", "su_range_kpa": (96, 192),
              "epsilon_50": 0.005},
}


def table_5_7_epsilon_50(consistency: str) -> float:
    """Representative epsilon_50 for intact clays (Table 5-7).

    Used in p-y curve construction for lateral loading analysis.

    Parameters
    ----------
    consistency : str
        Clay consistency: 'soft', 'medium', or 'stiff'.

    Returns
    -------
    float
        Representative epsilon_50 value.

    Raises
    ------
    ValueError
        If consistency is not recognized.
    """
    key = consistency.strip().lower()
    if key not in _TABLE_5_7:
        raise ValueError(
            f"Unknown consistency '{consistency}'. "
            f"Valid: soft, medium, stiff"
        )
    return _TABLE_5_7[key]["epsilon_50"]


# ============================================================================
# Table 5-8: Representative Values of epsilon_50 for Stiff Clays
# (refined by undrained shear strength range)
# ============================================================================

_TABLE_5_8_SU = [50, 100, 200, 300, 400]
_TABLE_5_8_EPS = [0.007, 0.005, 0.004, 0.004, 0.004]


def table_5_8_epsilon_50_stiff(su_kpa: float) -> float:
    """Epsilon_50 for stiff clays by undrained shear strength (Table 5-8).

    Provides more refined epsilon_50 values for stiff to hard clays
    based on undrained shear strength.

    Parameters
    ----------
    su_kpa : float
        Undrained shear strength in kPa.  Range 50 to 400.

    Returns
    -------
    float
        Interpolated epsilon_50 value.

    Raises
    ------
    ValueError
        If su_kpa is outside the valid range.
    """
    if su_kpa < 50 or su_kpa > 400:
        raise ValueError(f"su_kpa must be 50-400, got {su_kpa}")
    return _linterp(su_kpa, _TABLE_5_8_SU, _TABLE_5_8_EPS)


# ============================================================================
# Table 5-9: Soil Modulus k for Sand (kPa/m)
# Used for lateral load analysis with p-y curves.
# ============================================================================

_TABLE_5_9 = {
    # (density, submerged): k_kpa_per_m
    ("loose", True): 5430,
    ("medium", True): 16300,
    ("dense", True): 33900,
    ("loose", False): 6790,
    ("medium", False): 24430,
    ("dense", False): 61000,
}


def table_5_9_soil_modulus_k_sand(density: str,
                                  submerged: bool = False) -> float:
    """Soil modulus k for sands for p-y curves (Table 5-9).

    Parameters
    ----------
    density : str
        Sand density: 'loose', 'medium', or 'dense'.
    submerged : bool
        True for submerged (below water table), False for above.

    Returns
    -------
    float
        Soil modulus k in kPa/m.

    Raises
    ------
    ValueError
        If density is not recognized.
    """
    d = density.strip().lower()
    if d not in ("loose", "medium", "dense"):
        raise ValueError(
            f"Unknown density '{density}'. Valid: loose, medium, dense"
        )
    return float(_TABLE_5_9[(d, submerged)])


# ============================================================================
# Table 5-10: Soil Modulus k for Clays (kPa/m)
# Static and cyclic loading values.
# ============================================================================

_TABLE_5_10 = {
    # consistency: {loading: k_kpa_per_m}
    "soft": {"static": 8140, "cyclic": 8140},
    "medium": {"static": 27150, "cyclic": 27150},
    "stiff": {"static": 136000, "cyclic": 54300},
    "very_stiff": {"static": 271000, "cyclic": 108500},
    "hard": {"static": 543000, "cyclic": 217000},
}


def table_5_10_soil_modulus_k_clay(consistency: str,
                                   loading: str = "static") -> float:
    """Soil modulus k for clays for p-y curves (Table 5-10).

    Parameters
    ----------
    consistency : str
        Clay consistency: 'soft', 'medium', 'stiff', 'very_stiff',
        or 'hard'.
    loading : str
        Loading type: 'static' or 'cyclic'.  Default 'static'.

    Returns
    -------
    float
        Soil modulus k in kPa/m.

    Raises
    ------
    ValueError
        If consistency or loading is not recognized.
    """
    c = consistency.strip().lower().replace(" ", "_")
    lo = loading.strip().lower()

    if c not in _TABLE_5_10:
        raise ValueError(
            f"Unknown consistency '{consistency}'. "
            f"Valid: soft, medium, stiff, very_stiff, hard"
        )
    if lo not in ("static", "cyclic"):
        raise ValueError(
            f"Unknown loading '{loading}'. Valid: static, cyclic"
        )
    return float(_TABLE_5_10[c][lo])


# ============================================================================
# Table 5-11: Fixity Guidance for Micropile-to-Footing Connections
# ============================================================================

_TABLE_5_11 = {
    0:   {"fixity_pct": 0,   "embedment_mm": 300,
          "description": "Pinned connection (minimal moment transfer)"},
    50:  {"fixity_pct": 50,  "embedment_mm": 450,
          "description": "Partially fixed connection"},
    100: {"fixity_pct": 100, "embedment_mm": 600,
          "description": "Fully fixed connection (requires additional detailing)"},
}


def table_5_11_fixity(fixity_pct: int) -> dict:
    """Fixity guidance for micropile-to-footing connections (Table 5-11).

    Parameters
    ----------
    fixity_pct : int
        Desired fixity level: 0 (pinned), 50 (partial), or 100 (fixed).

    Returns
    -------
    dict
        Keys: fixity_pct, embedment_mm, description.

    Raises
    ------
    ValueError
        If fixity_pct is not 0, 50, or 100.
    """
    if fixity_pct not in _TABLE_5_11:
        raise ValueError(
            f"fixity_pct must be 0, 50, or 100, got {fixity_pct}"
        )
    return dict(_TABLE_5_11[fixity_pct])


# ============================================================================
# Table 5-12: Elastic Constants of Various Soils Based on Soil Type
# (modified after AASHTO, 2002)
# Returns range of equivalent elastic modulus Es in kPa.
# ============================================================================

_TABLE_5_12 = {
    # soil_type: {density/consistency: (Es_min_kPa, Es_max_kPa)}
    "clay_soft": (2400, 14400),
    "clay_medium_stiff": (14400, 48000),
    "clay_very_stiff": (48000, 96000),
    "loess": (14400, 57500),
    "silt": (1900, 19000),
    "fine_sand_loose": (7600, 11500),
    "fine_sand_medium_dense": (11500, 19000),
    "fine_sand_dense": (19000, 29000),
    "sand_loose": (9600, 29000),
    "sand_medium_dense": (29000, 48000),
    "sand_dense": (48000, 76000),
    "gravel_loose": (29000, 76000),
    "gravel_medium_dense": (76000, 96000),
    "gravel_dense": (96000, 192000),
}

_TABLE_5_12_DESCRIPTIONS = {
    "clay_soft": "Clay, soft sensitive",
    "clay_medium_stiff": "Clay, medium stiff",
    "clay_very_stiff": "Clay, very stiff",
    "loess": "Loess",
    "silt": "Silt",
    "fine_sand_loose": "Fine Sand, loose",
    "fine_sand_medium_dense": "Fine Sand, medium dense",
    "fine_sand_dense": "Fine Sand, dense",
    "sand_loose": "Sand, loose",
    "sand_medium_dense": "Sand, medium dense",
    "sand_dense": "Sand, dense",
    "gravel_loose": "Gravel, loose",
    "gravel_medium_dense": "Gravel, medium dense",
    "gravel_dense": "Gravel, dense",
}


def table_5_12_elastic_modulus(soil_type: str) -> dict:
    """Elastic modulus range for soils by type (Table 5-12).

    Used for buckling evaluation of micropiles (Eq. 5-28, 5-29).

    Parameters
    ----------
    soil_type : str
        Soil type key.  Use snake_case, e.g., 'clay_soft',
        'sand_medium_dense', 'gravel_dense'.

    Returns
    -------
    dict
        Keys: soil_type, description, es_min_kpa, es_max_kpa.

    Raises
    ------
    ValueError
        If soil_type is not recognized.
    """
    key = soil_type.strip().lower().replace(" ", "_")
    if key not in _TABLE_5_12:
        # Try partial match
        matches = [k for k in _TABLE_5_12 if key in k]
        if len(matches) == 1:
            key = matches[0]
        elif matches:
            raise ValueError(
                f"Ambiguous soil_type '{soil_type}'. "
                f"Matches: {', '.join(matches)}"
            )
        else:
            raise ValueError(
                f"Unknown soil_type '{soil_type}'. "
                f"Valid: {', '.join(sorted(_TABLE_5_12.keys()))}"
            )

    lo, hi = _TABLE_5_12[key]
    return {
        "soil_type": key,
        "description": _TABLE_5_12_DESCRIPTIONS[key],
        "es_min_kpa": lo,
        "es_max_kpa": hi,
    }


# ============================================================================
# Table 5-13: Elastic Constants of Various Soils Based on SPT N Value
# (modified after AASHTO, 2002)
# Es = factor * (N1)_60  in kPa
# ============================================================================

_TABLE_5_13 = {
    "silts_sandy_silts": {
        "description": "Silts, sandy silts, slightly cohesive mixtures",
        "factor_kpa": 400,
    },
    "clean_fine_medium_sand": {
        "description": "Clean fine to medium sands, slightly silty sands",
        "factor_kpa": 700,
    },
    "coarse_sand_gravel": {
        "description": "Coarse sands and sands with little gravel",
        "factor_kpa": 1000,
    },
    "sandy_gravels": {
        "description": "Sandy gravels",
        "factor_kpa": 1200,
    },
}


def table_5_13_elastic_modulus_spt(soil_type: str,
                                   n1_60: float) -> dict:
    """Elastic modulus from SPT N-value by soil type (Table 5-13).

    Computes equivalent elastic modulus Es = factor * (N1)_60.

    Parameters
    ----------
    soil_type : str
        Soil type key: 'silts_sandy_silts', 'clean_fine_medium_sand',
        'coarse_sand_gravel', or 'sandy_gravels'.
    n1_60 : float
        Corrected SPT blow count (N1)_60.  Must be > 0.

    Returns
    -------
    dict
        Keys: soil_type, description, factor_kpa, n1_60, es_kpa.

    Raises
    ------
    ValueError
        If soil_type is not recognized or n1_60 <= 0.
    """
    key = soil_type.strip().lower().replace(" ", "_")
    if key not in _TABLE_5_13:
        matches = [k for k in _TABLE_5_13 if key in k]
        if len(matches) == 1:
            key = matches[0]
        elif matches:
            raise ValueError(
                f"Ambiguous soil_type '{soil_type}'. "
                f"Matches: {', '.join(matches)}"
            )
        else:
            raise ValueError(
                f"Unknown soil_type '{soil_type}'. "
                f"Valid: {', '.join(sorted(_TABLE_5_13.keys()))}"
            )
    if n1_60 <= 0:
        raise ValueError(f"n1_60 must be > 0, got {n1_60}")

    info = _TABLE_5_13[key]
    es = info["factor_kpa"] * n1_60
    return {
        "soil_type": key,
        "description": info["description"],
        "factor_kpa": info["factor_kpa"],
        "n1_60": n1_60,
        "es_kpa": es,
    }
