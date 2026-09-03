"""EM 1110-2-2104 Chapter 2 -- Details of Reinforcement.

Minimum clear cover (Table 2-1), tension butt-splice longitudinal stagger
(Table 2-2), and temperature/shrinkage reinforcement (Table 2-3 + paragraph
2-9 min/max per-face limits). Printed pages cited per the 1 Nov 2023 edition
(pdf_page = printed_page + 5).
"""

import math

# Standard ASTM A615 reinforcing bar areas (sq in), used only to apply the
# min/max No.4 / No.9 per-face bounds of paragraph 2-9a/b. Not printed in
# this manual -- standard rebar geometry, cited for traceability.
_BAR_AREA_IN2 = {
    3: 0.11, 4: 0.20, 5: 0.31, 6: 0.44, 7: 0.60, 8: 0.79,
    9: 1.00, 10: 1.27, 11: 1.56, 14: 2.25, 18: 4.00,
}


# ============================================================================
# Table 2-1 -- Minimum clear cover (printed p. 5, pdf_page 10)
# ============================================================================

_TABLE_2_1 = {
    "unformed_contact_foundation": {"cover_in": 4.0, "cover_cm": 10.0},
    "formed_cavitation_abrasion": {"cover_in": 6.0, "cover_cm": 15.0},
    "formed_ge_24in": {"cover_in": 4.0, "cover_cm": 10.0},
    "formed_12_to_24in": {"cover_in": 3.0, "cover_cm": 7.5},
    "formed_le_12in": {"cover_in": None, "cover_cm": None},  # per ACI 318-19
}


def table_2_1_min_cover(concrete_section, aggregate_size_in=None,
                         bar_diameter_in=None):
    """Table 2-1: minimum clear cover to reinforcement (printed p. 5).

    Parameters
    ----------
    concrete_section : str
        One of: ``'unformed_contact_foundation'`` (unformed surfaces in
        contact with foundation, 4 in.), ``'formed_cavitation_abrasion'``
        (formed/screeded surfaces subject to cavitation or abrasion erosion,
        e.g. baffle blocks and stilling basin slabs, 6 in.),
        ``'formed_ge_24in'`` (formed/screeded, not subject to cavitation/
        abrasion, section >= 24 in. thick, 4 in.), ``'formed_12_to_24in'``
        (same but > 12 in. and < 24 in. thick, 3 in.), or
        ``'formed_le_12in'`` (<= 12 in. thick -- per ACI 318-19, not
        specified numerically in this manual).
    aggregate_size_in, bar_diameter_in : float, optional
        If given, the governing minimum is also checked against the note:
        cover >= 1.5x max aggregate size and >= 2.5x max reinforcement
        diameter.

    Returns
    -------
    dict
        {'concrete_section', 'min_cover_in', 'min_cover_cm', 'governs_by',
         'table': '2-1', 'printed_page': '5', 'pdf_page': 10}
    """
    if concrete_section not in _TABLE_2_1:
        raise ValueError(
            f"concrete_section must be one of {sorted(_TABLE_2_1)}, "
            f"got {concrete_section!r}"
        )
    row = _TABLE_2_1[concrete_section]
    cover_in = row["cover_in"]
    governs_by = "table_2_1"
    if cover_in is None:
        if aggregate_size_in is None and bar_diameter_in is None:
            raise ValueError(
                "formed_le_12in has no Table 2-1 value; this manual defers "
                "to ACI 318-19. Provide aggregate_size_in/bar_diameter_in "
                "to at least apply this manual's floor note, or consult "
                "ACI 318-19 directly."
            )
        cover_in = 0.0
    if aggregate_size_in is not None:
        floor = 1.5 * aggregate_size_in
        if floor > cover_in:
            cover_in, governs_by = floor, "1.5x_max_aggregate"
    if bar_diameter_in is not None:
        floor = 2.5 * bar_diameter_in
        if floor > cover_in:
            cover_in, governs_by = floor, "2.5x_max_bar_diameter"
    return {
        "concrete_section": concrete_section,
        "min_cover_in": round(cover_in, 3),
        "min_cover_cm": round(cover_in * 2.54, 3),
        "governs_by": governs_by,
        "table": "2-1", "printed_page": "5", "pdf_page": 10,
    }


# ============================================================================
# Table 2-2 -- Longitudinal stagger of tension butt splices (printed p. 6)
# ============================================================================

def table_2_2_splice_stagger(bar_size):
    """Table 2-2: longitudinal stagger of tension butt splices (printed p. 6).

    Parameters
    ----------
    bar_size : int
        ASTM bar size number (e.g. 8, 11, 14, 18).

    Returns
    -------
    dict
        {'bar_size', 'category' ('<=No.11' or '>No.11'), 'stagger_rule',
         'min_stagger_ft' (None for <=No.11, governed by ACI 318-19 lap
         length instead), 'table': '2-2', 'printed_page': '6', 'pdf_page': 11}

    Notes
    -----
    Bars larger than No. 11 must be butt spliced (may not be lap spliced,
    paragraph 2-8b/c). No more than half the bars may be spliced at any one
    section, either category (footnote to Table 2-2).
    """
    if bar_size <= 11:
        return {
            "bar_size": bar_size, "category": "<=No.11",
            "stagger_rule": "ACI 318-19 required lap length",
            "min_stagger_ft": None,
            "note": "No more than half of bars spliced at any one section.",
            "table": "2-2", "printed_page": "6", "pdf_page": 11,
        }
    return {
        "bar_size": bar_size, "category": ">No.11",
        "stagger_rule": "no less than 5 ft (1.5 m)",
        "min_stagger_ft": 5.0, "min_stagger_m": 1.5,
        "note": "No more than half of bars spliced at any one section. "
                "Bars > No. 11 must be butt spliced (not lap spliced).",
        "table": "2-2", "printed_page": "6", "pdf_page": 11,
    }


# ============================================================================
# Table 2-3 -- Minimum shrinkage/temperature reinforcement ratio (printed p. 7)
# ============================================================================

def table_2_3_temp_shrinkage_ratio(joint_spacing_ft):
    """Table 2-3: minimum shrinkage/temperature reinforcement ratio by
    control-joint spacing, Grade 60 (printed p. 7).

    Parameters
    ----------
    joint_spacing_ft : float
        Length between control joints (monolith joints, expansion joints,
        contraction joints, construction joints), ft.

    Returns
    -------
    dict
        {'joint_spacing_ft', 'min_ratio', 'band', 'table': '2-3',
         'printed_page': '7', 'pdf_page': 12}
    """
    if joint_spacing_ft < 0:
        raise ValueError(f"joint_spacing_ft must be >= 0, got {joint_spacing_ft}")
    if joint_spacing_ft < 30:
        ratio, band = 0.003, "< 30 ft (9 m)"
    elif joint_spacing_ft <= 40:
        ratio, band = 0.004, "30-40 ft (9-12 m)"
    else:
        ratio, band = 0.005, "> 40 ft (12 m)"
    return {
        "joint_spacing_ft": joint_spacing_ft, "min_ratio": ratio,
        "band": band, "table": "2-3", "printed_page": "7", "pdf_page": 12,
    }


def shrinkage_temperature_reinforcement(joint_spacing_ft, gross_thickness_in,
                                         unit_width_in=12.0):
    """Required shrinkage/temperature steel area per face (paragraph 2-9,
    printed pp. 6-7).

    Per paragraph 2-9a the area (from Table 2-3's ratio x gross section, half
    in each face) must be no less than the equivalent of No. 4 bars at 12 in.
    o.c. in each face; per 2-9b it need not exceed the equivalent of No. 9
    bars at 12 in. o.c. in each face (thicker sections are mass concrete,
    paragraph 2-9h, and are governed by thermal studies instead).

    Parameters
    ----------
    joint_spacing_ft : float
        Length between control joints, ft (selects the Table 2-3 ratio).
    gross_thickness_in : float
        Gross section thickness, in.
    unit_width_in : float, optional
        Design strip width, in. Default 12 in. (per-foot basis).

    Returns
    -------
    dict
        {'ratio' (Table 2-3), 'as_total_in2', 'as_per_face_in2' (clamped to
         the No.4/No.9-at-12in bounds), 'governs_by', 'unit_width_in',
         'reference': 'EM 1110-2-2104 paragraph 2-9', 'printed_page': '6-7'}
    """
    tbl = table_2_3_temp_shrinkage_ratio(joint_spacing_ft)
    ratio = tbl["min_ratio"]
    as_total = ratio * gross_thickness_in * unit_width_in
    as_per_face = as_total / 2.0

    min_per_face = _BAR_AREA_IN2[4] * (unit_width_in / 12.0)
    max_per_face = _BAR_AREA_IN2[9] * (unit_width_in / 12.0)
    as_per_face_raw = as_per_face
    governs_by = "table_2_3_ratio"
    if as_per_face < min_per_face:
        as_per_face, governs_by = min_per_face, "min_no4_at_12in_2-9a"
    elif as_per_face > max_per_face:
        as_per_face, governs_by = max_per_face, "max_no9_at_12in_2-9b"

    return {
        "joint_spacing_ft": joint_spacing_ft, "ratio": ratio,
        "as_total_in2": round(as_total, 4),
        "as_per_face_raw_in2": round(as_per_face_raw, 4),
        "as_per_face_in2": round(as_per_face, 4),
        "governs_by": governs_by, "unit_width_in": unit_width_in,
        "reference": "EM 1110-2-2104 paragraph 2-9", "printed_page": "6-7",
        "pdf_page": "11-12",
    }
