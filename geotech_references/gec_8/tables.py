"""GEC-8 table lookup functions.

Tables from FHWA-HIF-07-03 (GEC-8, April 2007), Design and Construction of
Continuous Flight Auger Piles.

ASD (not LRFD) design document.  Primary design tool is PCASE-style analysis
using load tests; these tables provide preliminary capacity estimates.
"""


# ============================================================================
# Table 5.4: P-Multipliers (Pm) for Design of Laterally Loaded Pile Groups
# (Chapter 5, p. 112; Section 5.6.3, p. 111)
#
# Every row as printed: soil type, test type, pile spacing (cent.-cent.),
# Pm for rows 1, 2, 3+, reported lateral group efficiency, deflection (mm),
# reference.  The table prints 3B rows for every soil and 5B rows only for
# M. Dense Sand and Loose M. Sand.  Note (1): V = very, M = medium, F = fine.
# ============================================================================

_TABLE_5_4_ROWS = [
    ("stiff_clay", "Stiff Clay", "Field Study", 3.0, (0.70, 0.50, 0.40),
     "N/A", "51", "Brown et al. (1987)"),
    ("stiff_clay", "Stiff Clay", "Field Study", 3.0, (0.70, 0.60, 0.50),
     "N/A", "30", "Brown et al. (1987)"),
    ("medium_clay", "Medium Clay", "Scale Model (Cyclic Load)", 3.0,
     (0.60, 0.45, 0.40), "N/A", "600 (at 50 cycles)", "Moss (1997)"),
    ("clayey_silt", "Clayey Silt", "Field Study", 3.0, (0.60, 0.40, 0.40),
     "N/A", "25-60", "Rollins et al. (1998)"),
    ("very_dense_sand", "V. Dense Sand", "Field Study", 3.0,
     (0.80, 0.40, 0.30), "75%", "25", "Brown et al. (1998)"),
    ("medium_dense_sand", "M. Dense Sand", "Centrifuge Model", 3.0,
     (0.80, 0.40, 0.30), "74%", "76", "McVay et al. (1995)"),
    ("medium_dense_sand", "M. Dense Sand", "Centrifuge Model", 5.0,
     (1.0, 0.85, 0.70), "95%", "76", "McVay et al. (1995)"),
    ("loose_medium_sand", "Loose M. Sand", "Centrifuge Model", 3.0,
     (0.65, 0.45, 0.35), "73%", "76", "McVay et al. (1995)"),
    ("loose_medium_sand", "Loose M. Sand", "Centrifuge Model", 5.0,
     (1.0, 0.85, 0.70), "92%", "76", "McVay et al. (1995)"),
    ("loose_fine_sand", "Loose F. Sand", "Field Study", 3.0,
     (0.80, 0.70, 0.30), "80%", "25-75", "Ruesta and Townsend (1997)"),
]

_TABLE_5_4_ROW_INDEX = {"lead_row": 0, "2nd_row": 1, "3rd_or_more_row": 2}

_TABLE_5_4_ROW_NAMES = {
    "lead_row": "Front Row (row 1)",
    "2nd_row": "Second Row (row 2)",
    "3rd_or_more_row": "Third and Subsequent Rows (row 3+)",
}

_TABLE_5_4_SOIL_ALIASES = {
    "v_dense_sand": "very_dense_sand", "v._dense_sand": "very_dense_sand",
    "m_dense_sand": "medium_dense_sand", "m._dense_sand": "medium_dense_sand",
    "loose_m_sand": "loose_medium_sand", "loose_m._sand": "loose_medium_sand",
    "loose_f_sand": "loose_fine_sand", "loose_f._sand": "loose_fine_sand",
}


def _table_5_4_soil_pm(soil_rows: list, i_row: int, s: float) -> list:
    """One soil's Table 5.4 Pm entries at spacing ``s`` (B multiples)."""
    from geotech_references._interpolation import _linterp

    def entry(row, pm, basis, efficiency=None):
        return {"soil_type": row[1], "test_type": row[2], "pm": round(pm, 3),
                "basis": basis,
                "reported_lateral_group_efficiency": efficiency or row[5],
                "deflection_mm": row[6], "reference": row[7]}

    at_3b = [r for r in soil_rows if r[3] == 3.0]
    at_5b = [r for r in soil_rows if r[3] == 5.0]
    if at_5b:
        r3, r5 = at_3b[0], at_5b[0]
        pm = _linterp(s, [3.0, 5.0], [r3[4][i_row], r5[4][i_row]])
        if s == 3.0:
            return [entry(r3, pm, "printed at 3B")]
        if s == 5.0:
            return [entry(r5, pm, "printed at 5B")]
        if s > 5.0:
            return [entry(r5, pm, "printed at 5B; the table prints no wider "
                                  "spacing, so the 5B row is held")]
        return [entry(r3, pm, "linear between the printed 3B and 5B rows",
                      f"{r3[5]} at 3B, {r5[5]} at 5B")]
    basis = ("printed at 3B" if s == 3.0 else
             "printed at 3B only; the table prints no wider spacing for this "
             "soil, so the 3B row is held")
    return [entry(r, r[4][i_row], basis) for r in at_3b]


def table_5_4_p_multiplier(
    row_position: str,
    spacing_over_b: float,
    soil_type: str = "",
) -> dict:
    """P-multiplier Pm for lateral analysis of CFA pile groups (GEC-8 Table 5.4).

    The p-y soil resistance of each pile in a laterally loaded group is
    multiplied by Pm (Section 5.6.3, p. 111).  Table 5.4 (p. 112) prints
    Pm for rows 1, 2 and 3+ by soil type, from field studies, a scale
    model and centrifuge models, for cyclic loading and static loading.
    Every soil is printed at 3B spacing; M. Dense Sand and Loose M. Sand
    are also printed at 5B (1.0, .85, .70), and between 3B and 5B their
    Pm is taken linearly between the two printed rows.  A spacing wider
    than a soil's printed rows holds its widest printed row, and every
    value returned states its basis.

    With no soil type, ``pm`` is the lowest Pm the table prints for the
    row at that spacing, and ``rows`` lists every printed soil so a soil
    can be chosen.  Stiff Clay has two printed rows (Brown et al. 1987, at
    51 mm and 30 mm deflection); ``pm`` is the lower and both are listed.

    Parameters
    ----------
    row_position : str
        Row position: 'lead' (or '1st', 'front'), '2nd', '3rd' (or 'trail').
    spacing_over_b : float
        Center-to-center spacing ÷ pile diameter B.  Must be ≥ 3.0.
    soil_type : str, optional
        Table 5.4 soil type: 'stiff_clay', 'medium_clay', 'clayey_silt',
        'very_dense_sand', 'medium_dense_sand', 'loose_medium_sand' or
        'loose_fine_sand'.  Empty (default) lists every soil.

    Returns
    -------
    dict
        {'row_position': str, 'spacing_over_b': float, 'soil_type': str,
         'pm': float, 'basis': str, 'rows': list, 'notes': str,
         'source': str}

    Raises
    ------
    ValueError
        If row_position or soil_type is unrecognized, or
        spacing_over_b < 3.0.
    """
    if spacing_over_b < 3.0:
        raise ValueError(
            f"spacing_over_b={spacing_over_b} is below the minimum of 3.0 "
            "(Table 5.4 prints no spacing closer than 3B)."
        )

    _aliases = {
        "lead": "lead_row", "lead_row": "lead_row", "front": "lead_row",
        "1st": "lead_row", "first": "lead_row", "row1": "lead_row",
        "2nd": "2nd_row", "second": "2nd_row", "row2": "2nd_row",
        "3rd": "3rd_or_more_row", "third": "3rd_or_more_row",
        "trail": "3rd_or_more_row", "trailing": "3rd_or_more_row",
        "3rd_or_more": "3rd_or_more_row", "row3": "3rd_or_more_row",
        "row3+": "3rd_or_more_row", "4th": "3rd_or_more_row",
    }

    key = row_position.lower().strip().replace(" ", "_").replace("-", "_")
    row_key = _aliases.get(key)
    if row_key is None:
        raise ValueError(
            f"Unknown row_position '{row_position}'. "
            "Use: 'lead', '2nd', or '3rd' (or 'trail')."
        )

    soils = list(dict.fromkeys(r[0] for r in _TABLE_5_4_ROWS))
    soil_key = ""
    if soil_type and soil_type.strip():
        soil_key = (soil_type.lower().strip().replace(" ", "_")
                    .replace("-", "_"))
        soil_key = _TABLE_5_4_SOIL_ALIASES.get(soil_key, soil_key)
        if soil_key not in soils:
            raise ValueError(
                f"Unknown soil_type '{soil_type}'. Table 5.4 soil types: "
                + ", ".join(soils) + "."
            )

    i_row = _TABLE_5_4_ROW_INDEX[row_key]
    rows = []
    for key in ([soil_key] if soil_key else soils):
        soil_rows = [r for r in _TABLE_5_4_ROWS if r[0] == key]
        rows.extend(_table_5_4_soil_pm(soil_rows, i_row, spacing_over_b))

    lowest = min(rows, key=lambda e: e["pm"])
    if len(rows) == 1:
        basis = lowest["basis"]
    elif soil_key:
        basis = ("the lower of the soil's two printed rows ("
                 + lowest["basis"] + ")")
    else:
        basis = ("no soil type given: the lowest Pm Table 5.4 prints for "
                 "this row at this spacing (" + lowest["soil_type"] + ", "
                 + lowest["reference"] + "); give soil_type for one soil")

    return {
        "row_position": row_key,
        "spacing_over_b": spacing_over_b,
        "soil_type": lowest["soil_type"] if soil_key else "",
        "pm": lowest["pm"],
        "basis": basis,
        "rows": rows,
        "notes": (
            _TABLE_5_4_ROW_NAMES[row_key] + ". Simplified approach (p. 113, "
            "Brown and O'Neill 2003): a single Pm equal to the average of "
            "all the pile row Pm in the group; analysing a single pile this "
            "way, a 20% increase in the computed maximum bending moment is "
            "recommended for design."
        ),
        "source": "GEC-8 Table 5.4, p. 112 (Section 5.6.3, pp. 111-113)",
    }


# ============================================================================
# Table 5.3: Group Efficiency (η) for Model Drilled Shafts in CFA Pile Groups
# in Cohesive Soils (Chapter 5, p. 92)
#
# Per AASHTO (2002) Section 10.8.3.9.3 (drilled shaft provisions applied
# to CFA piles in cohesionless soils):
#   η = 0.65 at 2.5D spacing
#   η = 1.0 at 6.0D spacing
#   Linear interpolation between 2.5D and 6.0D.
#   No cap contact adjustment needed — values already conservative.
# ============================================================================

_GROUP_EFF_SPACING = [2.5, 6.0]
_GROUP_EFF_COHESIONLESS = [0.65, 1.00]


def table_group_efficiency_cohesionless(spacing_over_d: float) -> dict:
    """Axial group efficiency for CFA piles in cohesionless soils.

    Per AASHTO (2002) Section 10.8.3.9.3 (drilled shaft provisions
    applied to conventional CFA piles).  Regardless of cap contact
    with the ground:

        η = 0.65 at 2.5D center-to-center spacing
        η = 1.0 at 6.0D center-to-center spacing
        Linear interpolation between 2.5D and 6.0D.

    For DD pile groups in cohesionless soils, η ≈ 1.0 (similar to
    driven pile groups in dense/medium-dense conditions).

    Parameters
    ----------
    spacing_over_d : float
        Center-to-center spacing ÷ pile diameter.  Must be ≥ 2.5.
        Use η = 1.0 for spacing ≥ 6.0D.

    Returns
    -------
    dict
        {'spacing_over_d': float, 'group_efficiency': float,
         'source': str}

    Raises
    ------
    ValueError
        If spacing_over_d < 2.5.
    """
    from geotech_references._interpolation import _linterp

    if spacing_over_d < 2.5:
        raise ValueError(
            f"spacing_over_d={spacing_over_d} is below the minimum of 2.5D."
        )

    eta = _linterp(spacing_over_d, _GROUP_EFF_SPACING, _GROUP_EFF_COHESIONLESS)
    eta = min(eta, 1.0)

    return {
        "spacing_over_d": spacing_over_d,
        "group_efficiency": round(eta, 3),
        "source": (
            "GEC-8 Ch 5 (AASHTO 2002 Section 10.8.3.9.3, drilled shaft "
            "provisions applied to CFA piles in cohesionless soils)"
        ),
    }
