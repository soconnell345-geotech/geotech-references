"""UFC 3-301-01 Chapters 2/3/6/7 + Appendix B -- seismic force-resisting
system design coefficients and height limits.

Three system tables, all keyed by Seismic Design Category (SDC) B/C/D/E/F
height limit in feet ('NL' = not limited, 'NP' = not permitted):

  - **Table 3-1** (printed pp. 49-57, pdf_page 70-78): REPLACES ASCE 7-22
    Table 12.2-1 IN ITS ENTIRETY for every structure under this UFC
    (paragraph 1613.1 [Supplement]; paragraph 12.2.1 [Supplement]). ~85
    systems across categories A (Bearing Wall), B (Building Frame), C
    (Moment-Resisting Frame), D/E (Dual Systems w/ Special/Intermediate
    Moment Frames), F (Shear Wall-Frame Interactive), G (Cantilevered
    Column), H (Steel Not Specifically Detailed).
  - **Table 7-1** (printed pp. 98-99, pdf_page 119-120): REPLACES ASCE
    7-16 Table 12.2-1 for Chapter 6/7 critical healthcare facilities
    (Group I-2 Condition 2 / ambulatory-care emergency-surgery facilities
    assigned to SDC D, E, or F). A curated PERMITTED-ONLY subset of Table
    3-1's systems (paragraph 12.2.1 [Supplement]: "Only the structural
    systems included in Table 7-1 are permitted... within the scope of
    this chapter"); some rows carry different R/Omega0/Cd values than the
    same-named Table 3-1 system.
  - **Table B-1** (printed pp. 124-126, pdf_page 145-147): Appendix B's
    alternate-nonlinear-design permitted-systems table for Risk Category
    IV buildings, which REPLACES BOTH ASCE 7-22 Table 12.2-1 AND this
    UFC's own Table 3-1 when the Appendix B procedure is used. Only
    height/SDC limitations are tabulated -- R, Cd, and Omega0 "are not
    required" for the Appendix B nonlinear procedure (paragraph B-18.4.2.4).

Height-limit units: feet (for SI use 30 m for 100 ft, 50 m for 160 ft, per
each table's own footnote).
"""


def _row(detailing, r, omega0, cd, h_b, h_c, h_d, h_e, h_f, footnotes=None):
    """Build one Table 3-1 / Table 7-1 system row."""
    return {
        "detailing_reference": detailing, "R": r, "omega0": omega0, "cd": cd,
        "height_limits": {"B": h_b, "C": h_c, "D": h_d, "E": h_e, "F": h_f},
        "footnotes": footnotes or [], "permitted": True,
    }


_NOT_PERMITTED_BY_UFC = {
    "permitted": False,
    "note": "This system is not permitted by UFC, but is permitted by ASCE 7-22 for SDC B.",
}

# ============================================================================
# Table 3-1 -- Replacement for ASCE 7-22 Table 12.2-1 (printed pp. 49-57)
# ============================================================================

TABLE_3_1 = {
    "A": {  # Bearing Wall Systems
        "special_reinforced_concrete_shear_walls": _row("(18.2.1.6)t", 5, 2.5, 5, "NL", "NL", 160, 160, 100, ["g", "h"]),
        "reinforced_concrete_ductile_coupled_walls": _row("(18.10.9)t", 8, 2.5, 8, "NL", "NL", 160, 160, 100, ["q"]),
        "ordinary_reinforced_concrete_shear_walls": _row("(18.2.1.6)t", 4, 2.5, 4, "NL", "NL", "NP", "NP", "NP", ["g"]),
        "detailed_plain_concrete_shear_walls": _row("(1905.5)v", 2, 2.5, 2, "NL", "NP", "NP", "NP", "NP", ["g"]),
        "ordinary_plain_concrete_shear_walls": _row("(Chapter 14)t", 1.5, 2.5, 1.5, "NL", "NP", "NP", "NP", "NP", ["g"]),
        "intermediate_precast_shear_walls": _row("(18.2.1.6)s, (1905.3)v", 4, 2.5, 4, "NL", "NL", "40i", "40i", "40i", ["g"]),
        "ordinary_precast_shear_walls": _row("(Chapter 11)t", 3, 2.5, 3, "NL", "NP", "NP", "NP", "NP", ["g"]),
        "special_reinforced_masonry_shear_walls": _row("(7.3.2.5)u", 5, 2.5, 3.5, "NL", "NL", 160, 160, 100),
        "intermediate_reinforced_masonry_shear_walls": _row("(7.3.2.4)u", 3.5, 2.5, 2.25, "NL", "NL", "NP", "NP", "NP"),
        "ordinary_reinforced_masonry_shear_walls": _row("(7.3.2.3)u", 2, 2.5, 1.75, "NL", 160, "NP", "NP", "NP"),
        "detailed_plain_masonry_shear_walls": dict(_NOT_PERMITTED_BY_UFC),
        "ordinary_plain_masonry_shear_walls": dict(_NOT_PERMITTED_BY_UFC),
        "prestressed_masonry_shear_walls": _row("(7.3.2.9, 7.3.2.10, 7.3.2.11)u", 1.5, 2.5, 1.75, "NL", "NP", "NP", "NP", "NP"),
        "ordinary_reinforced_aac_masonry_shear_walls": _row("(7.3.2.9)t", 2, 2.5, 2, "NL", 35, "NP", "NP", "NP"),
        "ordinary_plain_aac_masonry_shear_walls": _row("(7.3.2.7)t", 1.5, 2.5, 1.5, "NL", "NP", "NP", "NP", "NP"),
        "light_frame_wood_walls_wood_structural_panels": _row("(2301-2307)v", 6.5, 3, 4, "NL", "NL", 65, 65, 65),
        "light_frame_cold_formed_steel_walls_wood_panels_or_steel_sheets": _row("(2206, 2301-2307)v", 6.5, 3, 4, "NL", "NL", 65, 65, 65),
        "light_frame_walls_shear_panels_other_materials": _row("(2206, 2301-2307)v", 2, 2.5, 2, "NL", "NL", 35, "NP", "NP"),
        "light_frame_cold_formed_steel_flat_strap_bracing": _row("(2206, 2301-2307)v", 4, 2, 3.5, "NL", "NL", 65, 65, 65),
        "cross_laminated_timber_shear_walls": _row("4.6w", 3, 3, 3, 65, 65, 65, 65, 65),
        "cross_laminated_timber_shear_walls_high_aspect_ratio_only": _row("4.6w", 4, 3, 4, 65, 65, 65, 65, 65),
    },
    "B": {  # Building Frame Systems
        "steel_eccentrically_braced_frames": _row("(F3)s", 8, 2, 4, "NL", "NL", 160, 160, 100),
        "steel_special_concentrically_braced_frames": _row("(F2)s", 6, 2, 5, "NL", "NL", 160, 160, 100),
        "steel_ordinary_concentrically_braced_frames": _row("(F1)s", 3.25, 2, 3.25, "NL", "NL", "35j", "35j", "NPj"),
        "special_reinforced_concrete_shear_walls": _row("(18.2.1.6)t", 6, 2.5, 5, "NL", "NL", 160, 160, 100, ["g", "h"]),
        "reinforced_concrete_ductile_coupled_walls": _row("(18.10.9)t", 8, 2.5, 8, "NL", "NL", 160, 160, 100, ["q"]),
        "ordinary_reinforced_concrete_shear_walls": _row("(18.2.1.6)t", 5, 2.5, 4.5, "NL", "NL", "NP", "NP", "NP", ["g"]),
        "detailed_plain_concrete_shear_walls": _row("(1905.5)v", 2, 2.5, 2, "NL", "NP", "NP", "NP", "NP", ["g"]),
        "ordinary_plain_concrete_shear_walls": _row("(Chapter 14)t", 1.5, 2.5, 1.5, "NL", "NP", "NP", "NP", "NP", ["g"]),
        "intermediate_precast_shear_walls": _row("(18.2.1.6)t, (1905.3)v", 5, 2.5, 4.5, "NL", "NL", "40i", "40i", "40i", ["g"]),
        "ordinary_precast_shear_walls": _row("(Chapter 11)t", 4, 2.5, 4, "NL", "NP", "NP", "NP", "NP", ["g"]),
        "steel_concrete_composite_eccentrically_braced_frames": _row("(H3)s", 8, 2.5, 4, "NL", "NL", 160, 160, 100),
        "steel_concrete_composite_special_concentrically_braced_frames": _row("(H2)s", 5, 2, 4.5, "NL", "NL", 160, 160, 100),
        "steel_concrete_composite_ordinary_braced_frames": _row("(H1)s", 3, 2, 3, "NL", "NL", "NP", "NP", "NP"),
        "steel_concrete_composite_plate_shear_walls": _row("(H6)s", 6.5, 2.5, 5.5, "NL", "NL", 160, 160, 100),
        "steel_concrete_composite_special_shear_walls": _row("(H5)s", 6, 2.5, 5, "NL", "NL", 160, 160, 100),
        "steel_concrete_composite_ordinary_shear_walls": _row("(H4)s", 5, 2.5, 4.5, "NL", "NL", "NP", "NP", "NP"),
        "special_reinforced_masonry_shear_walls": _row("(7.3.2.5)u", 5.5, 2.5, 4, "NL", "NL", 160, 160, 100),
        "intermediate_reinforced_masonry_shear_walls": _row("(7.3.2.4)u", 4, 2.5, 4, "NL", "NL", "NP", "NP", "NP"),
        "ordinary_reinforced_masonry_shear_walls": _row("(7.3.2.3)u", 2, 2.5, 2, "NL", 160, "NP", "NP", "NP"),
        "detailed_plain_masonry_shear_walls": dict(_NOT_PERMITTED_BY_UFC),
        "ordinary_plain_masonry_shear_walls": dict(_NOT_PERMITTED_BY_UFC),
        "prestressed_masonry_shear_walls": _row("(7.3.2.9, 7.3.2.10, 7.3.2.11)u", 1.5, 2.5, 1.75, "NL", "NP", "NP", "NP", "NP"),
        "light_frame_wood_walls_wood_structural_panels": _row("(2301-2307)v", 7, 2.5, 4.5, "NL", "NL", 65, 65, 65),
        "light_frame_cold_formed_steel_walls_wood_panels_or_steel_sheets": _row("(2206, 2301-2307)v", 7, 2.5, 4.5, "NL", "NL", 65, 65, 65),
        "light_frame_walls_shear_panels_other_materials": _row("(2206, 2301-2307)v", 2.5, 2.5, 2.5, "NL", "NL", 35, "NP", "NP"),
        "steel_buckling_restrained_braced_frames": _row("(F4)s", 8, 2.5, 5, "NL", "NL", 160, 160, 100),
        "steel_special_plate_shear_walls": _row("(F5)s", 7, 2, 6, "NL", "NL", 160, 160, 100),
        "steel_concrete_coupled_composite_plate_shear_walls": _row("(H8)s", 8, 2.5, 5.5, "NL", "NL", 160, 160, 100),
    },
    "C": {  # Moment-Resisting Frame Systems
        "steel_special_moment_frames": _row("(E3)s", 8, 3, 5.5, "NL", "NL", "NL", "NL", "NL"),
        "steel_special_truss_moment_frames": _row("(E4)s", 7, 3, 5.5, "NL", "NL", 160, 100, "NP"),
        "steel_intermediate_moment_frames": _row("(E2)s", 4.5, 3, 4, "NL", "NL", "35k", "NPk", "NPk"),
        "steel_ordinary_moment_frames": _row("(E1)s", 3.5, 3, 3, "NL", "NL", "NPl,r", "NPl,r", "NPl,r"),
        "special_reinforced_concrete_moment_frames": _row("(18.2.1.6)t", 8, 3, 5.5, "NL", "NL", "NL", "NL", "NL", ["m"]),
        "intermediate_reinforced_concrete_moment_frames": _row("(18.2.1.6)t", 5, 3, 4.5, "NL", "NL", "NP", "NP", "NP"),
        "ordinary_reinforced_concrete_moment_frames": _row("(18.2.1.6)t", 3, 3, 2.5, "NL", "NP", "NP", "NP", "NP"),
        "steel_concrete_composite_special_moment_frames": _row("(G3)s", 8, 3, 5.5, "NL", "NL", "NL", "NL", "NL"),
        "steel_concrete_composite_intermediate_moment_frames": _row("(G2)s", 5, 3, 4.5, "NL", "NL", "NP", "NP", "NP"),
        "steel_concrete_composite_partially_restrained_moment_frames": _row("(G4)s", 6, 3, 5.5, 160, 160, 100, "NP", "NP"),
        "steel_concrete_composite_ordinary_moment_frames": _row("(G1)s", 3, 3, 2.5, "NL", "NP", "NP", "NP", "NP"),
        "cold_formed_steel_special_bolted_moment_frame": _row("(2204)v", 3.5, "3o", 3.5, 35, 35, 35, 35, 35, ["n"]),
    },
    "D": {  # Dual Systems w/ Special Moment Frames >=25% [ASCE 7-22 12.2.5.1]
        "steel_eccentrically_braced_frames": _row("(F3)s", 8, 2.5, 4, "NL", "NL", "NL", "NL", "NL"),
        "steel_special_concentrically_braced_frames": _row("(F2)s", 7, 2.5, 5.5, "NL", "NL", "NL", "NL", "NL"),
        "special_reinforced_concrete_shear_walls": _row("(18.2.1.6)t", 7, 2.5, 5.5, "NL", "NL", "NL", "NL", "NL", ["g", "h"]),
        "reinforced_concrete_ductile_coupled_walls": _row("(18.10.9)t", 8, 2.5, 8, "NL", "NL", "NL", "NL", "NL", ["q"]),
        "ordinary_reinforced_concrete_shear_walls": _row("(18.2.1.6)t", 6, 2.5, 5, "NL", "NL", "NP", "NP", "NP", ["g"]),
        "steel_concrete_composite_eccentrically_braced_frames": _row("(H3)s", 8, 2.5, 4, "NL", "NL", "NL", "NL", "NL"),
        "steel_concrete_composite_special_concentrically_braced_frames": _row("(H2)s", 6, 2.5, 5, "NL", "NL", "NL", "NL", "NL"),
        "steel_concrete_composite_plate_shear_walls": _row("(H6)s", 7.5, 2.5, 6, "NL", "NL", "NL", "NL", "NL"),
        "steel_concrete_composite_special_shear_walls": _row("(H5)s", 7, 2.5, 6, "NL", "NL", "NL", "NL", "NL"),
        "steel_concrete_composite_ordinary_shear_walls": _row("(H4)s", 6, 2.5, 5, "NL", "NL", "NP", "NP", "NP"),
        "special_reinforced_masonry_shear_walls": _row("(7.3.2.5)u", 5.5, 3, 5, "NL", "NL", "NL", "NL", "NL"),
        "intermediate_reinforced_masonry_shear_walls": _row("(7.3.2.4)u", 4, 3, 3.5, "NL", "NL", "NP", "NP", "NP"),
        "steel_buckling_restrained_braced_frames": _row("(F4)s", 8, 2.5, 5, "NL", "NL", "NL", "NL", "NL"),
        "steel_special_plate_shear_walls": _row("(F5)s", 8, 2.5, 6.5, "NL", "NL", "NL", "NL", "NL"),
        "steel_concrete_coupled_composite_plate_shear_walls": _row("(H8)s", 8, 2.5, 5.5, "NL", "NL", "NL", "NL", "NL"),
    },
    "E": {  # Dual Systems w/ Intermediate Moment Frames >=25% [ASCE 7-22 12.2.5.1]
        "steel_special_concentrically_braced_frames": _row("(F2)s", 6, 2.5, 5, "NL", "NL", 35, "NP", "NP", ["p"]),
        "special_reinforced_concrete_shear_walls": _row("(18.2.1.6)t", 6.5, 2.5, 5, "NL", "NL", 160, 100, 100, ["g", "h"]),
        "ordinary_reinforced_masonry_shear_walls": _row("(7.3.2.3)u", 3, 3, 2.5, "NL", 160, "NP", "NP", "NP"),
        "intermediate_reinforced_masonry_shear_walls": _row("(7.3.2.4)u", 3.5, 3, 3, "NL", "NL", "NP", "NP", "NP"),
        "steel_concrete_composite_special_concentrically_braced_frames": _row("(H2)s", 5.5, 2.5, 4.5, "NL", "NL", 160, 100, "NP"),
        "steel_concrete_composite_ordinary_braced_frames": _row("(H1)s", 3.5, 2.5, 3, "NL", "NL", "NP", "NP", "NP"),
        "steel_concrete_composite_ordinary_shear_walls": _row("(H4)s", 5, 3, 4.5, "NL", "NL", "NP", "NP", "NP"),
        "ordinary_reinforced_concrete_shear_walls": _row("(18.2.1.6)t", 5.5, 2.5, 4.5, "NL", "NL", "NP", "NP", "NP", ["g"]),
    },
    "F": {  # Shear Wall-Frame Interactive System
        "ordinary_rc_moment_frames_and_ordinary_rc_shear_walls": _row("(18.2.1.6)t", 4.5, 2.5, 4, "NL", "NP", "NP", "NP", "NP", ["g"]),
    },
    "G": {  # Cantilevered Column Systems [ASCE 7-22 12.2.5.2]
        "steel_special_cantilever_column_systems": _row("(E6)s", 2.5, 2.5, 2.5, 35, 35, 35, 35, 35),
        "steel_ordinary_cantilever_column_systems": _row("(E5)s", 1.25, 1.25, 1.25, 35, 35, "NPl", "NPl", "NPl"),
        "special_reinforced_concrete_moment_frames": _row("(18.2.1.6)t", 2.5, 2.5, 2.5, 35, 35, 35, 35, 35, ["m"]),
        "intermediate_reinforced_concrete_moment_frames": _row("(18.2.1.6)t", 1.5, 1.5, 1.5, 35, 35, "NP", "NP", "NP"),
        "ordinary_reinforced_concrete_moment_frames": _row("(18.2.1.6)t", 1, 1.25, 1, 35, "NP", "NP", "NP", "NP"),
        "timber_frames": _row("(2301-2307)v", 1.5, 1.5, 1.5, 35, 35, 35, "NP", "NP"),
    },
    "H": {  # Steel Systems Not Specifically Detailed for Seismic Resistance
        "steel_not_specifically_detailed_excl_cantilever_columns": _row(
            "AISC 360-22, AISI S100, AISI S240, ASCE 8", 3, 3, 3, "NL", "NL", "NP", "NP", "NP"
        ),
    },
}

TABLE_3_1_FOOTNOTES = {
    "a": "Response modification coefficient, R, for use throughout. R reduces forces to a strength level, not an allowable stress level.",
    "b": "Where the tabulated overstrength factor Omega0 >= 2.5, it is permitted to be reduced by 0.5 for structures with flexible diaphragms.",
    "c": "Deflection amplification factor, Cd, for use in ASCE 7-22 Sections 12.8.6, 12.8.7, 12.9.1.2, 12.12.2, 12.12.3, and 12.12.4.",
    "d": "NL = not limited, NP = not permitted. For metric units, use 30 m for 100 ft and 50 m for 160 ft.",
    "e": "See ASCE 7-22 Section 12.2.5.4 for systems limited to structural height hn <= 240 ft (75 m).",
    "f": "See ASCE 7-22 Section 12.2.5.4 for systems limited to structural height hn <= 160 ft (50 m).",
    "g": "In Section 2.3 of ACI 318-19, a shear wall is defined as a structural wall.",
    "h": "In Section 2.3 of ACI 318-19, 'special structural wall' includes precast and cast-in-place construction.",
    "i": "An increase in structural height hn to 45 ft (14 m) is permitted for single-story storage warehouse facilities.",
    "j": "Steel OCBFs are permitted in single-story buildings up to hn = 60 ft (18 m) where roof dead load <= 20 psf (1.0 kN/m2), and in penthouse structures.",
    "k": "See ASCE 7-22 Section 12.2.5.7 for limitations in SDC D, E, or F.",
    "l": "See ASCE 7-22 Section 12.2.5.6 for limitations in SDC D, E, or F.",
    "m": "In Section 2.3 of ACI 318-19, 'special moment frame' includes precast and cast-in-place construction.",
    "n": "Cold-formed steel special bolted moment frames must be limited to one story per ANSI/AISI S400-20.",
    "o": "Alternately, Emh is permitted to be based on expected strength per ANSI/AISI S400-20.",
    "p": "Ordinary moment frame is permitted in lieu of intermediate moment frame for SDC B or C.",
    "q": "Structural height, hn, shall not be less than 60 ft (18.3 m).",
    "r": "Ordinary moment frames are permitted as part of the structural system transferring forces between isolator units.",
    "s": "ANSI/AISC 341-22 section number.",
    "t": "ACI 318-19 Section 18.2.1.6 cites appropriate sections in ACI 318-19.",
    "u": "TMS 402-22 section number.",
    "v": "2024 IBC section number.",
    "w": "2021 Special Design Provisions for Wind and Seismic with Commentary (SDPWS) section number.",
}


def table_3_1_seismic_system(category, system):
    """Table 3-1: seismic force-resisting system design coefficients (R,
    Omega0, Cd) and structural-height limits by Seismic Design Category,
    REPLACING ASCE 7-22 Table 12.2-1 in its entirety (printed pp. 49-57).

    Parameters
    ----------
    category : str
        'A' through 'H' (a key of ``TABLE_3_1``).
    system : str
        A system key within that category (see ``list_table_3_1_systems``).

    Returns
    -------
    dict
        The system's row (R/omega0/cd/height_limits/permitted/footnotes)
        plus {'category', 'system', 'table': '3-1', 'printed_page':
        '49-57', 'pdf_page': '70-78'}.
    """
    cat = category.upper().strip()
    if cat not in TABLE_3_1:
        raise ValueError(f"category must be one of {sorted(TABLE_3_1)}, got {category!r}")
    key = system.lower().strip()
    if key not in TABLE_3_1[cat]:
        raise ValueError(
            f"Unknown system {system!r} in category {cat!r}; see "
            f"list_table_3_1_systems({cat!r})"
        )
    row = dict(TABLE_3_1[cat][key])
    row.update({"category": cat, "system": key, "table": "3-1",
                "printed_page": "49-57", "pdf_page": "70-78"})
    return row


def table_3_1_footnote(footnote_id):
    """A lettered footnote to Table 3-1 (printed p. 57)."""
    key = footnote_id.lower().strip()
    if key not in TABLE_3_1_FOOTNOTES:
        raise ValueError(f"footnote_id must be one of {sorted(TABLE_3_1_FOOTNOTES)}, got {footnote_id!r}")
    return {"footnote_id": key, "text": TABLE_3_1_FOOTNOTES[key], "table": "3-1",
            "printed_page": "57", "pdf_page": 78}


def list_table_3_1_systems(category=None):
    """Lists Table 3-1 system keys.

    Parameters
    ----------
    category : str, optional
        If given, list only systems in that category ('A'-'H'). If
        omitted, return {category: [systems...]} for all categories.

    Returns
    -------
    list of str, or dict
    """
    if category is None:
        return {cat: sorted(systems) for cat, systems in TABLE_3_1.items()}
    cat = category.upper().strip()
    if cat not in TABLE_3_1:
        raise ValueError(f"category must be one of {sorted(TABLE_3_1)}, got {category!r}")
    return sorted(TABLE_3_1[cat])


# ============================================================================
# Table 7-1 -- Replacement for ASCE 7-16 Table 12.2-1, critical healthcare
# facilities (printed pp. 98-99, pdf_page 119-120). Permitted-only subset.
# ============================================================================

TABLE_7_1 = {
    "B": {  # Building Frame Systems
        "steel_eccentrically_braced_frames": _row("(F3)r", 8, 2, 4, "NL", "NL", 160, 160, 100),
        "steel_special_concentrically_braced_frames": _row("(F2)r", 6, 2, 5, "NL", "NL", 160, 160, 100),
        "special_reinforced_concrete_shear_walls": _row("(18.2.1.6)s", 6, 2.5, 5, "NL", "NL", 160, 160, 100, ["g", "h"]),
        "reinforced_concrete_ductile_coupled_walls": _row("(18.10.9)s", 8, 2.5, 8, "NL", "NL", 160, 160, 100, ["w"]),
        "special_reinforced_masonry_shear_walls": _row("(7.3.2.5)t", 5.5, 2.5, 4, "NL", "NL", 160, 160, 100),
        "light_frame_wood_walls_wood_structural_panels": _row("(2301-2307)u", 7, 2.5, 4.5, "NL", "NL", 65, 65, 65, ["v"]),
        "light_frame_cold_formed_steel_walls_wood_panels_or_steel_sheets": _row("(2206, 2301-2307)u", 7, 2.5, 4.5, "NL", "NL", 65, 65, 65, ["v"]),
        "steel_buckling_restrained_braced_frames": _row("(F4)r", 8, 2.5, 5, "NL", "NL", 160, 160, 100),
    },
    "C": {  # Moment-Resisting Frame Systems
        "steel_special_moment_frames": _row("(E3)r", 8, 3, 5.5, "NL", "NL", "NL", "NL", "NL"),
        "special_reinforced_concrete_moment_frames": _row("(18.2.1.6)s", 8, 3, 5.5, "NL", "NL", "NL", "NL", "NL", ["m"]),
    },
    "D": {  # Dual Systems w/ Special Moment Frames >=25% [ASCE 7-16 12.2.5.1]
        "steel_eccentrically_braced_frames": _row("(F3)r", 8, 2.5, 4, "NL", "NL", "NL", "NL", "NL"),
        "special_reinforced_concrete_shear_walls": _row("(18.2.1.6)s", 7, 2.5, 5.5, "NL", "NL", "NL", "NL", "NL", ["g", "h"]),
        "reinforced_concrete_ductile_coupled_walls": _row("(18.10.9)s", 8, 2.5, 8, "NL", "NL", "NL", "NL", "NL", ["w"]),
        "special_reinforced_masonry_shear_walls": _row("(7.3.2.5)t", 5.5, 3, 5, "NL", "NL", "NL", "NL", "NL"),
        "steel_buckling_restrained_braced_frames": _row("(F4)r", 8, 2.5, 5, "NL", "NL", "NL", "NL", "NL"),
    },
}

TABLE_7_1_FOOTNOTES = {
    "a": "Response modification coefficient, R, for use throughout; reduces forces to strength level, not allowable-stress level.",
    "b": "Where Omega0 >= 2.5, it is permitted to be reduced by 0.5 for structures with flexible diaphragms.",
    "c": "Deflection amplification factor, Cd, for use in ASCE 7 Sections 12.8.6, 12.8.7, 12.9.1.2, 12.12.3, and 12.12.4.",
    "d": "NL = not limited, NP = not permitted. For metric units, use 30 m for 100 ft and 50 m for 160 ft.",
    "e": "See ASCE 7-16 Section 12.2.5.4 for systems limited to hn <= 240 ft (75 m).",
    "f": "See ASCE 7-16 Section 12.2.5.4 for systems limited to hn <= 160 ft (50 m).",
    "g": "In Section 2.3 of ACI 318, a shear wall is defined as a structural wall.",
    "h": "In Section 2.3 of ACI 318, 'special structural wall' includes precast and cast-in-place construction.",
    "m": "In Section 2.3 of ACI 318, 'special moment frame' includes precast and cast-in-place construction.",
    "r": "ANSI/AISC 341-16 section number.",
    "s": "ACI 318-19 Section 18.2.1.6 cites appropriate sections in ACI 318-19.",
    "t": "TMS 402-16 section number.",
    "u": "2021 IBC section numbers.",
    "v": "Permitted only for structures up to two stories.",
    "w": "Structural height, hn, shall not be less than 60 ft (18.3 m).",
}


def table_7_1_healthcare_seismic_system(category, system):
    """Table 7-1: permitted seismic force-resisting systems and design
    coefficients for Chapter 6/7 critical healthcare facilities, REPLACING
    ASCE 7-16 Table 12.2-1 for those facilities (printed pp. 98-99). Only
    systems listed in this table are permitted within the Chapter 7 scope
    (paragraph 12.2.1 [Supplement]).

    Parameters
    ----------
    category : str
        'B', 'C', or 'D' (the only categories with permitted healthcare
        systems).
    system : str
        A system key within that category (see
        ``list_table_7_1_systems``).

    Returns
    -------
    dict
        The system's row plus {'category', 'system', 'table': '7-1',
        'printed_page': '98-99', 'pdf_page': '119-120'}.
    """
    cat = category.upper().strip()
    if cat not in TABLE_7_1:
        raise ValueError(f"category must be one of {sorted(TABLE_7_1)}, got {category!r}")
    key = system.lower().strip()
    if key not in TABLE_7_1[cat]:
        raise ValueError(
            f"Unknown system {system!r} in category {cat!r}; see "
            f"list_table_7_1_systems({cat!r})"
        )
    row = dict(TABLE_7_1[cat][key])
    row.update({"category": cat, "system": key, "table": "7-1",
                "printed_page": "98-99", "pdf_page": "119-120"})
    return row


def list_table_7_1_systems(category=None):
    """Lists Table 7-1 (healthcare) system keys; see
    ``list_table_3_1_systems`` for the parameter/return convention."""
    if category is None:
        return {cat: sorted(systems) for cat, systems in TABLE_7_1.items()}
    cat = category.upper().strip()
    if cat not in TABLE_7_1:
        raise ValueError(f"category must be one of {sorted(TABLE_7_1)}, got {category!r}")
    return sorted(TABLE_7_1[cat])


# ============================================================================
# Table B-1 -- Permitted Systems for RC IV Buildings Designed Using the
# Appendix B Alternate Procedure (printed pp. 124-126, pdf_page 145-147).
# R/Cd/Omega0 do not apply to this nonlinear procedure (paragraph
# B-18.4.2.4) -- only height/SDC limitations are tabulated.
# ============================================================================

def _b1_row(h_b, h_c, h_d, h_e, h_f, footnotes=None):
    return {"height_limits": {"B": h_b, "C": h_c, "D": h_d, "E": h_e, "F": h_f},
            "footnotes": footnotes or []}


TABLE_B_1 = {
    "Bearing Wall Systems": {
        "ordinary_steel_braced_frames_light_frame_construction": _b1_row("NL", "NL", 65, 65, 65),
        "reinforced_concrete_ductile_coupled_walls": _b1_row("NL", "NL", 160, 160, 100, ["7"]),
        "special_reinforced_concrete_shear_walls": _b1_row("NL", "NL", 160, 160, 100),
        "ordinary_reinforced_concrete_shear_walls": _b1_row("NL", "NL", "NP", "NP", "NP"),
        "special_reinforced_masonry_shear_walls": _b1_row("NL", "NL", 160, 160, 100),
        "light_framed_walls_shear_panels_wood_or_sheet_steel": _b1_row("NL", "NL", 65, 65, 65),
        "light_framed_walls_shear_panels_all_other_materials": _b1_row("NL", "NL", 35, "NP", "NP"),
        "light_framed_walls_shear_panels_flat_strap_bracing": _b1_row("NL", "NL", 65, 65, 65),
    },
    "Building Frame Systems": {
        "steel_eccentrically_braced_frames": _b1_row("NL", "NL", 160, 160, 100),
        "special_steel_concentrically_braced_frames": _b1_row("NL", "NL", 160, 160, 100),
        "ordinary_steel_concentrically_braced_frames": _b1_row("NL", "NL", 35, 35, "NP", ["3"]),
        "special_reinforced_concrete_shear_walls": _b1_row("NL", "NL", 160, 160, 160),
        "reinforced_concrete_ductile_coupled_walls": _b1_row("NL", "NL", 160, 160, 100, ["7"]),
        "ordinary_reinforced_concrete_shear_walls": _b1_row("NL", "NL", "NP", "NP", "NP"),
        "composite_eccentrically_braced_frames": _b1_row("NL", "NL", 160, 160, 100),
        "composite_special_concentrically_braced_frames": _b1_row("NL", "NL", 160, 160, 100),
        "ordinary_composite_braced_frames": _b1_row("NL", "NL", "NP", "NP", "NP"),
        "composite_steel_plate_shear_walls": _b1_row("NL", "NL", 160, 160, 100),
        "special_composite_reinforced_concrete_shear_walls_with_steel_elements": _b1_row("NL", "NL", 160, 160, 100),
        "special_reinforced_masonry_shear_walls": _b1_row("NL", "NL", 160, 160, 100),
        "light_framed_walls_shear_panels_wood_or_sheet_steel": _b1_row("NL", "NL", 65, 65, 65),
        "light_framed_walls_shear_panels_all_other_materials": _b1_row("NL", "NL", 35, "NP", "NP"),
        "steel_concrete_coupled_composite_plate_shear_walls": _b1_row("NL", "NL", 160, 160, 100, ["7"]),
    },
    "Moment-Resisting Frame Systems": {
        "special_steel_moment_frames": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "special_steel_truss_moment_frames": _b1_row("NL", "NL", 160, 100, "NP"),
        "intermediate_steel_moment_frames": _b1_row("NL", "NL", 35, "NP", "NP", ["5"]),
        "ordinary_steel_moment_frames": _b1_row("NL", "NL", "NP", "NP", "NP", ["6"]),
        "special_reinforced_concrete_moment_frames": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "intermediate_reinforced_concrete_moment_frames": _b1_row("NL", "NL", "NP", "NP", "NP"),
        "special_composite_moment_frames": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "intermediate_composite_moment_frames": _b1_row("NL", "NL", "NP", "NP", "NP"),
        "composite_partially_restrained_moment_frames": _b1_row(160, 160, 100, "NP", "NP"),
    },
    "Dual Systems with Special Moment Frames (>=25%)": {
        "steel_eccentrically_braced_frames": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "special_steel_concentrically_braced_frames": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "special_reinforced_concrete_shear_walls": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "reinforced_concrete_ductile_coupled_walls": _b1_row("NL", "NL", "NL", "NL", "NL", ["7"]),
        "ordinary_reinforced_concrete_shear_walls": _b1_row("NL", "NL", "NP", "NP", "NP"),
        "composite_eccentrically_braced_frames": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "composite_special_concentrically_braced_frames": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "composite_steel_plate_shear_walls": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "special_composite_reinforced_concrete_shear_walls_with_steel_elements": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "ordinary_composite_reinforced_concrete_shear_walls_with_steel_elements": _b1_row("NL", "NL", "NP", "NP", "NP"),
        "special_reinforced_masonry_shear_walls": _b1_row("NL", "NL", "NL", "NL", "NL"),
        "steel_concrete_coupled_composite_plate_shear_walls": _b1_row("NL", "NL", "NL", "NL", "NL", ["7"]),
    },
    "Dual Systems with Intermediate Moment Frames (>=25%)": {
        "special_steel_concentrically_braced_frames": _b1_row("NL", "NL", 35, "NP", "NP", ["4"]),
        "special_reinforced_concrete_shear_walls": _b1_row("NL", "NL", 160, 100, 100),
        "ordinary_reinforced_concrete_shear_walls": _b1_row("NL", "NL", "NP", "NP", "NP"),
        "composite_special_concentrically_braced_frames": _b1_row("NL", "NL", 160, 100, "NP"),
        "ordinary_composite_braced_frames": _b1_row("NL", "NL", "NP", "NP", "NP"),
        "ordinary_composite_reinforced_concrete_shear_walls_with_steel_elements": _b1_row("NL", "NL", "NP", "NP", "NP"),
    },
    "Cantilevered Column Systems": {
        "special_steel_cantilever_column_systems": _b1_row(35, 35, 35, 35, 35),
        "special_reinforced_concrete_moment_frames": _b1_row(35, 35, 35, 35, 35),
    },
}

TABLE_B_1_FOOTNOTES = {
    "1": "Any system restricted by this table may be permitted if approved by the Design Review Panel (Section B-1.2).",
    "2": "See Table 3-1 for detailing references for seismic force-resisting systems.",
    "3": "Steel ordinary concentrically braced frames are permitted in single-story buildings up to hn = 60 ft, roof dead load <= 20 psf, and in penthouse structures.",
    "4": "Ordinary moment frames may be used in lieu of intermediate moment frames for SDC B or C.",
    "5": "See ASCE 7-22 Section 12.2.5.7 for limitations in SDC D, E, or F.",
    "6": "See ASCE 7-22 Section 12.2.5.6 for limitations in SDC D, E, or F.",
    "7": "Structural height, hn, shall not be less than 60 ft (18.3 m).",
}


def table_b1_rc4_permitted_system(category, system):
    """Table B-1: permitted seismic force-resisting systems and height
    limits for Risk Category IV buildings using the Appendix B alternate
    nonlinear-design procedure (printed pp. 124-126). This table REPLACES
    both ASCE 7-22 Table 12.2-1 and this UFC's own Table 3-1 when the
    Appendix B procedure is used; R, Cd, and Omega0 do not apply (paragraph
    B-18.4.2.4).

    Parameters
    ----------
    category : str
        A key of ``TABLE_B_1`` (e.g. 'Building Frame Systems'). Matched
        case-insensitively.
    system : str
        A system key within that category (see
        ``list_table_b1_systems``).

    Returns
    -------
    dict
        {'height_limits', 'footnotes', 'category', 'system', 'table':
         'B-1', 'printed_page': '124-126', 'pdf_page': '145-147'}
    """
    cat_match = next((c for c in TABLE_B_1 if c.lower() == category.lower().strip()), None)
    if cat_match is None:
        raise ValueError(f"category must be one of {sorted(TABLE_B_1)}, got {category!r}")
    key = system.lower().strip()
    if key not in TABLE_B_1[cat_match]:
        raise ValueError(
            f"Unknown system {system!r} in category {cat_match!r}; see "
            f"list_table_b1_systems({cat_match!r})"
        )
    row = dict(TABLE_B_1[cat_match][key])
    row.update({"category": cat_match, "system": key, "table": "B-1",
                "printed_page": "124-126", "pdf_page": "145-147"})
    return row


def table_b1_footnote(footnote_id):
    """A numbered footnote to Table B-1 (printed p. 126)."""
    key = str(footnote_id).strip()
    if key not in TABLE_B_1_FOOTNOTES:
        raise ValueError(f"footnote_id must be one of {sorted(TABLE_B_1_FOOTNOTES)}, got {footnote_id!r}")
    return {"footnote_id": key, "text": TABLE_B_1_FOOTNOTES[key], "table": "B-1",
            "printed_page": "126", "pdf_page": 147}


def list_table_b1_systems(category=None):
    """Lists Table B-1 (RC IV alternate design) system keys; see
    ``list_table_3_1_systems`` for the parameter/return convention
    (category names here are the full Table B-1 section headers)."""
    if category is None:
        return {cat: sorted(systems) for cat, systems in TABLE_B_1.items()}
    cat_match = next((c for c in TABLE_B_1 if c.lower() == category.lower().strip()), None)
    if cat_match is None:
        raise ValueError(f"category must be one of {sorted(TABLE_B_1)}, got {category!r}")
    return sorted(TABLE_B_1[cat_match])
