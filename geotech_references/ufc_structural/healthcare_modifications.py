"""UFC 3-301-01 Chapters 6/7 -- modifications for critical healthcare
facilities (Group I-2 Condition 2 / ambulatory care emergency-surgery
facilities assigned to SDC D, E, or F).

Table 6-1 (minimum masonry wall thickness, printed p. 93), the Chapter 7
structural-configuration limits for healthcare facilities (paragraph
12.1.7, printed pp. 95-96), and the retaining-wall lateral-soil-load
provisions of paragraph 1807.2.2 (printed p. 88). These chapters adopt the
2021 IBC / ASCE 7-16 / ACI 318-19 / TMS 402-16 / AISC 360-16 / AISC 341-16
editions (not the 2024 IBC / ASCE 7-22 of Chapters 2/3) because the
applicable 2025 California Building Code edition was not available when
this UFC was finalized (printed p. 87, p. 95).
"""

# ============================================================================
# Table 6-1 -- Minimum Thickness of Masonry Walls (printed p. 93,
# pdf_page 114)
# ============================================================================

TABLE_6_1_MASONRY_WALL_THICKNESS = {
    "stone_masonry_bearing_or_shear": {"max_height_or_length_to_thickness_ratio": 14, "nominal_min_thickness_in": 16},
    "reinforced_grouted_masonry_bearing_or_shear": {"max_height_or_length_to_thickness_ratio": 25, "nominal_min_thickness_in": 6},
    "reinforced_hollow_unit_masonry_bearing_or_shear": {"max_height_or_length_to_thickness_ratio": 25, "nominal_min_thickness_in": 6},
    "exterior_reinforced_nonbearing_walls": {"max_height_or_length_to_thickness_ratio": 30, "nominal_min_thickness_in": 6},
    "interior_reinforced_nonbearing_partitions": {"max_height_or_length_to_thickness_ratio": 36, "nominal_min_thickness_in": 4},
}


def table_6_1_masonry_wall_thickness(wall_type):
    """Table 6-1: minimum masonry wall thickness and maximum unsupported
    height/length-to-thickness ratio, for TMS 402-16 Section 8.3.4.4
    (paragraph 6-5.3, printed p. 93). For varying-thickness walls, use the
    least thickness (note 1); for a cantilevered wall use twice its
    unsupported dimension (note 2); freestanding cantilevered walls
    carrying no applied vertical load are exempt (note 3), subject to
    stress/overturning requirements.

    Parameters
    ----------
    wall_type : str
        A key of ``TABLE_6_1_MASONRY_WALL_THICKNESS`` (e.g.
        'reinforced_hollow_unit_masonry_bearing_or_shear').

    Returns
    -------
    dict
        {'wall_type', 'max_height_or_length_to_thickness_ratio',
         'nominal_min_thickness_in', 'table': '6-1', 'printed_page': '93',
         'pdf_page': 114}
    """
    key = wall_type.lower().strip()
    if key not in TABLE_6_1_MASONRY_WALL_THICKNESS:
        raise ValueError(
            f"wall_type must be one of {sorted(TABLE_6_1_MASONRY_WALL_THICKNESS)}, "
            f"got {wall_type!r}"
        )
    row = dict(TABLE_6_1_MASONRY_WALL_THICKNESS[key])
    row.update({"wall_type": key, "table": "6-1", "printed_page": "93", "pdf_page": 114})
    return row


# ============================================================================
# Paragraph 1807.2.2 -- retaining wall design lateral soil loads
# (Chapter 6 IBC Section 1807, printed p. 88, pdf_page 109)
# ============================================================================

def healthcare_retaining_wall_lateral_load_minimum():
    """Paragraph 1807.2.2 [Replacement]: minimum design lateral soil load
    for retaining walls at critical healthcare facilities, and the SDC
    D/E/F seismic increment trigger (printed p. 88).

    Returns
    -------
    dict
        {'minimum_fraction_of_section_1610_load': 0.80,
         'seismic_increment_backfill_height_threshold_ft': 6,
         'paragraph': '1807.2.2', 'printed_page': '88', 'pdf_page': 109}
    """
    return {
        "minimum_fraction_of_section_1610_load": 0.80,
        "seismic_increment_backfill_height_threshold_ft": 6,
        "paragraph": "1807.2.2", "printed_page": "88", "pdf_page": 109,
    }


# ============================================================================
# Paragraph 12.1.7 -- Chapter 7 healthcare structural configuration limits
# (printed pp. 95-96, pdf_page 116-117)
# ============================================================================

def healthcare_structural_configuration_limits():
    """Paragraph 12.1.7 [Addition]: structural configuration limitations
    for critical healthcare facilities (printed pp. 95-96): uniform bay
    spacing, a restriction on transfer beams/trusses, seismic-joint sizing
    at 125% of the ASCE 7-16 requirement, and adjacent-structure separation.

    Returns
    -------
    dict
        {'seismic_joint_separation_factor': 1.25,
         'adjacent_structure_separation_in_per_story': 2,
         'transfer_beam_restriction', 'bay_spacing_requirement',
         'paragraph': '12.1.7', 'printed_page': '95-96', 'pdf_page': '116-117'}
    """
    return {
        "seismic_joint_separation_factor": 1.25,
        "adjacent_structure_separation_in_per_story": 2,
        "transfer_beam_restriction": (
            "Transfer beams or trusses supporting upper-level columns are "
            "not to be used unless permitted case-by-case by the AHJ."
        ),
        "bay_spacing_requirement": "Bay spacing must be essentially equal and uniform throughout.",
        "paragraph": "12.1.7", "printed_page": "95-96", "pdf_page": "116-117",
    }


def healthcare_elevator_seismic_force_asd():
    """Paragraph 13.6.11.1.1 [Addition]: minimum ASD-level seismic force
    for elevator guide rail support-bracket fastenings and supporting
    structural framing at critical healthcare facilities, and the load
    distribution to top/bottom guiding members (printed pp. 100-101).

    Returns
    -------
    dict
        {'minimum_asd_seismic_force_g': 0.5,
         'counterweight_load_fraction': 0.40,
         'top_guide_member_fraction': 1/3, 'bottom_guide_member_fraction': 2/3,
         'paragraph': '13.6.11.1.1', 'printed_page': '100-101',
         'pdf_page': '121-122'}
    """
    return {
        "minimum_asd_seismic_force_g": 0.5,
        "counterweight_load_fraction": 0.40,
        "top_guide_member_fraction": 1.0 / 3.0,
        "bottom_guide_member_fraction": 2.0 / 3.0,
        "paragraph": "13.6.11.1.1", "printed_page": "100-101", "pdf_page": "121-122",
    }
