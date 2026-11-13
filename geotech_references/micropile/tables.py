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
# Table 4-2: Dimensions, Yield, and Ultimate Strengths for Standard
# Reinforcing Bars. FHWA-NHI-05-039, p. 4-27 (PDF page 83), read off the
# rendered page:
#
#   Steel Grade   Rebar Size, mm (in)   Area, mm2 (in.2)   Yield Strength, kN (kip)
#   Grade 420(1)  19 (#6)               284 (0.44)         117 (26)
#                 22 (#7)               387 (0.60)         160 (36)
#                 25 (#8)               510 (0.79)         211 (47)
#   Grade 520(2)  19 (#6)               284 (0.44)         147 (33)
#                 22 (#7)               387 (0.60)         200 (45)
#                 25 (#8)               510 (0.79)         264 (59)
#                 29 (#9)               645 (1.0)          334 (75
#                 32 (#10)              819 (1.27)         424 (95)
#                 36 (#11)              1006 (1.56)        520 (117)
#                 43 (#14)              1452 (2.25)        751 (169)
#                 57 (#18)              2581 (4.0)         1335 (3000)
#   Grade 550(3)  63 (2.5 in)           3168 (4.91)        1747 (393)
#
# Notes (1)-(3): fy = 420 MPa (60 ksi), fu = 620 MPa (92 ksi); fy = 520 MPa
# (75 ksi), fu = 690 MPa (102 ksi); fy = 550 MPa (80 ksi), fu = 700 MPa
# (104 ksi). The #18 row prints "1335 (3000)" kip; 1335 kN is 300 kip.
# ============================================================================

# grade: {bar_size: (diameter_mm, area_mm2, yield_kn)}, all as printed
_TABLE_4_2 = {
    420: {
        "#6": (19, 284, 117),
        "#7": (22, 387, 160),
        "#8": (25, 510, 211),
    },
    520: {
        "#6": (19, 284, 147),
        "#7": (22, 387, 200),
        "#8": (25, 510, 264),
        "#9": (29, 645, 334),
        "#10": (32, 819, 424),
        "#11": (36, 1006, 520),
        "#14": (43, 1452, 751),
        "#18": (57, 2581, 1335),
    },
    550: {
        "2.5in": (63, 3168, 1747),
    },
}

# (fy_mpa, fu_mpa) from the table's notes (1)-(3)
_TABLE_4_2_GRADES = {420: (420, 620), 520: (520, 690), 550: (550, 700)}

_TABLE_4_2_SIZE_ALIASES = {"2.5": "2.5in", "2.5in": "2.5in", "2.5in.": "2.5in",
                           "63": "2.5in", "63mm": "2.5in"}

_TABLE_4_2_REFERENCE = ("FHWA-NHI-05-039, Table 4-2 Dimensions, Yield, and "
                        "Ultimate Strengths for Standard Reinforcing Bars, "
                        "p. 4-27")


def table_4_2_rebar_properties(bar_size: str,
                               grade: int = 520) -> dict:
    """Reinforcing bar size (mm), area (mm2) and yield strength (kN) as printed in FHWA-NHI-05-039 Table 4-2, p. 4-27.

    The table prints Grade 420 for #6 to #8, Grade 520 for #6 to #18 and
    Grade 550 for one bar, 63 mm (2.5 in). The yield strength is the
    table's own column, not area times fy. A bar the table does not print
    in the grade asked for is refused.

    Parameters
    ----------
    bar_size : str
        Bar designation as printed: '#6', '#7', '#8', '#9', '#10', '#11',
        '#14', '#18', or '2.5in' (the 63 mm Grade 550 bar).
    grade : int
        Steel grade in MPa: 420, 520, or 550.  Default 520.

    Returns
    -------
    dict
        Keys: bar_size, grade_mpa, diameter_mm, area_mm2, yield_kn (all as
        printed), fu_mpa (the grade's tensile strength, table notes),
        reference.

    Raises
    ------
    ValueError
        If bar_size or grade is invalid, or the table does not print that
        bar in that grade.
    """
    raw = bar_size.strip().lower().replace(" ", "")
    if raw in _TABLE_4_2_SIZE_ALIASES:
        size = _TABLE_4_2_SIZE_ALIASES[raw]
    else:
        size = raw.upper()
        if not size.startswith("#"):
            size = "#" + size
    all_sizes = []
    for rows in _TABLE_4_2.values():
        for k in rows:
            if k not in all_sizes:
                all_sizes.append(k)
    if size not in all_sizes:
        raise ValueError(
            f"Unknown bar size '{bar_size}'. "
            f"Valid sizes: {', '.join(all_sizes)}"
        )
    if grade not in _TABLE_4_2:
        raise ValueError(
            f"Unknown grade {grade}. Valid grades: 420, 520, 550"
        )
    rows = _TABLE_4_2[grade]
    if size not in rows:
        printed_in = [str(g) for g, r in _TABLE_4_2.items() if size in r]
        raise ValueError(
            f"Bar {size} not available in Grade {grade}: Table 4-2 "
            f"(p. 4-27) prints Grade {grade} for {', '.join(rows)} only. "
            f"{size} is printed in Grade {', '.join(printed_in)}."
        )

    diameter, area, yield_kn = rows[size]
    fy, fu = _TABLE_4_2_GRADES[grade]
    return {
        "bar_size": size,
        "grade_mpa": fy,
        "diameter_mm": diameter,
        "area_mm2": area,
        "yield_kn": yield_kn,
        "fu_mpa": fu,
        "reference": _TABLE_4_2_REFERENCE,
    }


# ============================================================================
# Table 4-5: Dimensions and Yield Strength of Common Micropile Pipe Types and
# Sizes (p. 4-33, PDF page 89). The table prints OD, wall, area and yield
# strength in kN (kip) per pipe, and no Fy column. Note (3): API N-80 Fy =
# 552 MPa (80 ksi). Note (4): ASTM A519 & A106 Fy = "241 MPa (36 ksi)"; 36 ksi
# is 248.2 MPa, which the printed yield strengths imply (1,540/6,208 = 248.1,
# 1,890/7,600 = 248.7, 3,190/12,850 = 248.2; 1,270/5,067 = 250.6). fy_mpa
# 248 for A519/A106 is derived from the note's 36 ksi (lead's ruling,
# 2026-11-10).
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


_TABLE_4_5_A519_FY_NOTE = (
    "Table 4-5 (p. 4-33) prints no Fy column. Note (4) reads \"Nominal yield "
    "stress for ASTM A519 & A106 steel is Fy = 241 MPa (36 ksi).\" 36 ksi is "
    "248 MPa, which the table's printed yield strengths imply (1,540 kN / "
    "6,208 mm2 = 248.1 MPa; 1,890 / 7,600 = 248.7; 3,190 / 12,850 = 248.2; "
    "the 139.7 x 12.7 row's printed 1,270 kN / 5,067 mm2 implies 250.6 "
    "MPa); 248 is returned. The printed yield strengths (kN) are returned "
    "as printed.")


def table_4_5_pipe_properties(od_mm: float,
                              wall_mm: float = 0.0,
                              steel_type: str = "n80") -> dict:
    """Dimensions, area (mm2) and yield strength (kN) of a micropile casing pipe, FHWA-NHI-05-039 Table 4-5 (p. 4-33), with the nominal yield stress fy_mpa from the table's notes: 552 MPa for API N-80 (note 3) and 248 MPa for ASTM A519/A106, derived from note (4)'s 36 ksi; note (4) prints "241 MPa (36 ksi)" and the A519/A106 results carry a print_note.

    Looks up the printed pipe size (OD within 1 mm, wall within 0.5 mm).

    Parameters
    ----------
    od_mm : float
        Outside diameter in mm (e.g., 139.7, 177.8, 244.5).
    wall_mm : float
        Wall thickness in mm.  If 0, returns all pipes with that OD.
    steel_type : str
        'n80' for API N-80 (Fy = 552 MPa, note 3) or 'a519' for ASTM
        A519/A106 (Fy = 248 MPa, from note 4's 36 ksi; the note prints
        "241 MPa (36 ksi)").  Case-insensitive.

    Returns
    -------
    dict or list of dict
        Pipe properties: od_mm, wall_mm, area_mm2, yield_kn, fy_mpa,
        fy_basis, steel_type, and print_note for A519/A106. Returns a list
        if wall_mm=0 and multiple sizes match.

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
            row = {
                "od_mm": od,
                "wall_mm": wall,
                "area_mm2": area,
                "yield_kn": yld,
                "fy_mpa": fy,
                "steel_type": "API N-80" if fy == 552 else "ASTM A519/A106",
            }
            if fy == 552:
                row["fy_basis"] = "Table 4-5 note (3): Fy = 552 MPa (80 ksi)"
            else:
                row["fy_basis"] = ("Table 4-5 note (4)'s 36 ksi (248.2 MPa); "
                                   "the note prints 241 MPa (36 ksi)")
                row["print_note"] = _TABLE_4_5_A519_FY_NOTE
            matches.append(row)

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
    "glacial_till": "Glacial Till (silt, sand, gravel), medium-very dense, cemented",
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
# Table 5-8: Values of epsilon_50 for stiff clays (after Reese et al. 2005)
# FHWA-NHI-05-039, p. 5-56 (PDF page 148), read off the rendered page:
#
#   Undrained shear strength (kPa)   (psi)          epsilon_50
#   50 - 100                         7.3 - 14.5     0.007
#   100 - 200                        14.5 - 29.0    0.005
#   300 - 400                        43.5 - 58.1    0.004
#
# The table prints three ranges, each with one value, and no row for 200 to
# 300 kPa.
# ============================================================================


def table_5_8_epsilon_50_stiff(su_kpa: float) -> float:
    """Strain epsilon_50 (dimensionless) for a stiff clay of undrained shear strength su, as printed in FHWA-NHI-05-039 Table 5-8, p. 5-56.

    The table (after Reese et al. 2005) gives one value for each range of
    undrained shear strength: 50 to 100 kPa 0.007, 100 to 200 kPa 0.005,
    300 to 400 kPa 0.004. The printed value of the range is returned; the
    table gives ranges, so nothing is interpolated. It prints no row
    for 200 to 300 kPa, and a strength there is refused. A strength of
    exactly 100 kPa, on the edge of two ranges, takes the 100 to 200 value.

    Parameters
    ----------
    su_kpa : float
        Undrained shear strength in kPa, 50 to 200 or 300 to 400.

    Returns
    -------
    float
        epsilon_50 of the printed range holding su_kpa.

    Raises
    ------
    ValueError
        If su_kpa is outside 50 to 400 kPa, or between 200 and 300 kPa,
        where the table prints no row.
    """
    if su_kpa < 50 or su_kpa > 400:
        raise ValueError(
            f"su_kpa must be 50-400 (Table 5-8, p. 5-56), got {su_kpa}")
    if 200 < su_kpa < 300:
        raise ValueError(
            f"su_kpa = {su_kpa}: Table 5-8 (p. 5-56) prints no row between "
            "200 and 300 kPa (its ranges are 50-100, 100-200 and 300-400 "
            "kPa: epsilon_50 0.007, 0.005 and 0.004)")
    if su_kpa < 100:
        return 0.007
    if su_kpa <= 200:
        return 0.005
    return 0.004


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
# Table 5-10: Soil-modulus parameter (k) for clays (after Reese et al., 2005)
# FHWA-NHI-05-039, p. 5-56 (PDF page 148). Static and cyclic k in kPa/m.
# The Cyclic columns print "-" for Soft and Medium clay: no value.
#
#   Consistency  su (kPa)    Static (kPa/m)  Cyclic (kPa/m)
#   Soft         12 - 24     8,140           -
#   Medium       24 - 48     27,150          -
#   Stiff        48 - 96     136,000         54,300
#   Very Stiff   96 - 192    271,000         108,500
#   Hard         192 - 383   543,000         217,000
# ============================================================================

_TABLE_5_10 = {
    # consistency: {loading: k_kpa_per_m}; None = the print's "-"
    "soft": {"static": 8140, "cyclic": None},
    "medium": {"static": 27150, "cyclic": None},
    "stiff": {"static": 136000, "cyclic": 54300},
    "very_stiff": {"static": 271000, "cyclic": 108500},
    "hard": {"static": 543000, "cyclic": 217000},
}


def table_5_10_soil_modulus_k_clay(consistency: str,
                                   loading: str = "static") -> float:
    """Soil-modulus parameter k for clays, in kPa/m, for p-y curves, as printed in FHWA-NHI-05-039 Table 5-10, p. 5-56.

    Static: soft 8,140, medium 27,150, stiff 136,000, very stiff 271,000,
    hard 543,000 kPa/m. Cyclic: stiff 54,300, very stiff 108,500, hard
    217,000 kPa/m. The table prints "-" for the cyclic k of soft and medium
    clay, so those two are refused.

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
        If consistency or loading is not recognized, or for the cyclic k
        of soft or medium clay, which the table does not print.
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
    k = _TABLE_5_10[c][lo]
    if k is None:
        raise ValueError(
            f"Table 5-10 (p. 5-56) prints no cyclic k for {c} clay (the "
            "Cyclic columns show '-' for Soft and Medium); its static k is "
            f"{_TABLE_5_10[c]['static']} kPa/m")
    return float(k)


# ============================================================================
# Table 5-11: Fixity Guidance for Micropile-to-Footing Connections
# ============================================================================

# FHWA-NHI-05-039, p. 5-58 (PDF page 150), the three columns as printed.
_TABLE_5_11_NOTE = (
    "(1) Guidance provided assumes that footing itself is restrained. For "
    "example, if only one row of piles in direction of loading then 0% "
    "fixity should be assumed (Table 5-11 footnote, printed on the 50 % and "
    "100 % columns)."
)

_TABLE_5_11 = {
    0:   {"fixity_pct": 0,   "embedment_mm": 300,
          "embedment_limit": "300 mm (12 in.) or less",
          "description": (
              "0 % Fixity (Pinned Head Condition): Casing embedment of "
              "300 mm (12 in.) or less, or Reinforcing bar embedment with or "
              "without bearing plate, or Any detail where top of micropile "
              "embedment is at or below the level of the bottom "
              "reinforcement of the footing")},
    50:  {"fixity_pct": 50,  "embedment_mm": 450,
          "embedment_limit": "450 mm (18 in.)",
          "description": (
              "50 % Fixity: Casing embedment of 450 mm (18 in.), or Shear "
              "connection between casing and existing footing with minimum "
              "casing embedment of 450 mm (18 in.)"),
          "note": _TABLE_5_11_NOTE},
    100: {"fixity_pct": 100, "embedment_mm": 600,
          "embedment_limit": "600 mm (24 in.) or more",
          "description": (
              "100 % Fixity (Fixed Head Condition): Casing embedment of "
              "600 mm (24 in.) or more"),
          "note": _TABLE_5_11_NOTE},
}


def table_5_11_fixity(fixity_pct: int) -> dict:
    """Casing embedment (mm) for 0, 50 or 100 % head fixity of a micropile-footing connection, in the words of FHWA-NHI-05-039 Table 5-11, p. 5-58.

    0 %: casing embedment of 300 mm or less (or the two other details the
    table lists); 50 %: 450 mm; 100 %: 600 mm or more. ``embedment_mm`` is
    the printed number and ``embedment_limit`` says whether it is a
    maximum, a value or a minimum.

    Parameters
    ----------
    fixity_pct : int
        Desired fixity level: 0 (pinned), 50 (partial), or 100 (fixed).

    Returns
    -------
    dict
        Keys: fixity_pct, embedment_mm, embedment_limit, description (the
        column as printed); note (the table's footnote) for 50 and 100.

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

# Table 5-12, p. 5-69 (PDF page 161): in the two sand rows below the kPa
# column disagrees with the ksf column printed beside it. Elsewhere the kPa
# is the ksf converted and rounded (kPa/ksf 47.5 to 48.3; 1 ksf = 47.88
# kPa), and the table prints the same kPa wherever a ksf value recurs: 600
# ksf as 29,000 (fine sand dense, sand loose, gravel loose), 1,000 as 48,000
# (clay medium stiff, very stiff), 1,600 as 76,000 (gravel loose, medium
# dense). The values held for the two sand rows are those printed kPa
# values of their ksf ends: 29,000 - 48,000 and 48,000 - 76,000.
_TABLE_5_12_PRINT_NOTES = {
    "sand_medium_dense": (
        "Table 5-12 (p. 5-69) prints '29,000 - 96,000 (600 - 1,000)' for "
        "this row, kPa (ksf): the upper kPa value disagrees with the ksf "
        "beside it. The value here, 29,000 - 48,000 kPa, is the kPa the "
        "table prints for 600 and 1,000 ksf in its other rows (fine sand "
        "dense, sand loose, gravel loose; clay medium stiff and very "
        "stiff); 600 and 1,000 ksf are 28,728 and 47,880 kPa."),
    "sand_dense": (
        "Table 5-12 (p. 5-69) prints '96,000 - 76,000 (1,000 - 1,600)' for "
        "this row, kPa (ksf): the lower kPa value disagrees with the ksf "
        "beside it. The value here, 48,000 - 76,000 kPa, is the kPa the "
        "table prints for 1,000 and 1,600 ksf in its other rows (clay "
        "medium stiff and very stiff; gravel loose and medium dense); "
        "1,000 and 1,600 ksf are 47,880 and 76,608 kPa."),
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
    out = {
        "soil_type": key,
        "description": _TABLE_5_12_DESCRIPTIONS[key],
        "es_min_kpa": lo,
        "es_max_kpa": hi,
    }
    if key in _TABLE_5_12_PRINT_NOTES:
        out["note"] = _TABLE_5_12_PRINT_NOTES[key]
    return out


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
