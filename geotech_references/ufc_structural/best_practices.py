"""UFC 3-301-01 Appendix A -- Best Practices (printed pp. 103-108, pdf_page
124-129).

This appendix is almost entirely narrative recommendations and pointers to
other guidance documents (drift limits, glazing, corrosion protection,
etc.) with no design equations -- it is digitized here as a topic-indexed
guidance lookup (``best_practice_guidance``), plus the handful of genuinely
printed numeric criteria embedded in that narrative
(``shelf_angle_deflection_limit``, ``masonry_veneer_ledge_offset``,
``gable_bent_tie_rod_force_range``).
"""

BEST_PRACTICE_TOPICS = {
    "building_drift_limits": {
        "paragraph": "A-1.1", "printed_page": "103", "pdf_page": 124,
        "guidance": (
            "ASCE 7-22 Section 12.12 (interstory drift under code-prescribed "
            "seismic forces, Table 12.12-1) is the only MANDATORY building "
            "drift limit in the IBC/ASCE 7-22. Wind-drift/serviceability "
            "limits (ASCE 7-22 Appendix C, non-mandatory) require engineering "
            "judgment in consultation with the owner -- overly stringent "
            "limits raise cost, overly lax limits damage rigidly connected "
            "components. See the Metal Building Systems Manual / AISC 360 "
            "Chapter L / AISC Design Guide 3 for pre-engineered metal "
            "building wind-drift guidance."
        ),
    },
    "impact_resistant_glazing": {
        "paragraph": "A-1.2", "printed_page": "103-104", "pdf_page": "124-125",
        "guidance": (
            "ASCE 7-22 Chapter 32 requires protected glazing for Essential "
            "Facilities in tornado-prone regions (Section 32.12.3); this "
            "requirement does not apply to RC I/II structures. Consider "
            "impact-resistant glazing on facilities outside Section "
            "32.12.3's scope but within tornado-prone areas, similar to "
            "windborne-debris-region requirements (IBC Section 1609.2)."
        ),
    },
    "hard_wall_buildings": {
        "paragraph": "A-1.3", "printed_page": "104", "pdf_page": 125,
        "guidance": (
            "Loss of roof diaphragm during a high-wind event can cause "
            "total collapse of load-bearing tilt-up/precast wall buildings. "
            "See FEMA P-1026 (basis for ASCE 7-22 Section 12.10.4)."
        ),
    },
    "photovoltaic_array_loads": {
        "paragraph": "A-1.4", "printed_page": "104", "pdf_page": 125,
        "guidance": (
            "ASCE 7-22 Section 13.6.12 (seismic) and Chapters 29-31 (wind) "
            "govern rooftop PV panel design; SEAOC PV1-2012/PV2-2017 give "
            "additional guidance. UFC 3-110-03 (Roofing) requires supports "
            "permanently affixed to the structure -- ballasted PV systems "
            "are NOT permitted, notwithstanding 2024 IBC Section 1613.3's "
            "general allowance."
        ),
    },
    "wind_loads_large_openings": {
        "paragraph": "A-1.5", "printed_page": "104", "pdf_page": 125,
        "guidance": (
            "For buildings with large openings (overhead doors in "
            "warehouses/maintenance shops), use the aircraft-hangar wind-"
            "load criteria of Section 1609.1.2 (Chapter 2 of this UFC)."
        ),
    },
    "gable_bent_footings": {
        "paragraph": "A-2.1", "printed_page": "105", "pdf_page": 126,
        "guidance": (
            "Moment-frame reactions from metal building gable bents produce "
            "horizontal thrust at column bases, resisted by tie rods "
            "(cost-effective for large thrusts), hairpin reinforcing bars "
            "into the slab (smaller thrusts), or a foundation designed for "
            "the overturning moment. See ``gable_bent_tie_rod_force_range`` "
            "for the printed tie-rod force threshold. Reference: Metal "
            "Building Systems: Design and Specification (Newman)."
        ),
    },
    "footings_on_expansive_soils": {
        "paragraph": "A-2.2", "printed_page": "105", "pdf_page": 126,
        "guidance": (
            "Base design on geotechnical testing/recommendations including "
            "settlement, heave, and mitigation; ensure positive drainage "
            "away from structures. Guidance: UFC 3-220-01, PTI DC 10.5-21."
        ),
    },
    "footing_depth_frost": {
        "paragraph": "A-2.3", "printed_page": "105", "pdf_page": 126,
        "guidance": "Footing depth for frost must be provided by the project geotechnical engineer.",
    },
    "slab_on_ground_guidance": {
        "paragraph": "A-3.1 to A-3.4", "printed_page": "105-106", "pdf_page": "126-127",
        "guidance": (
            "Slab-on-ground concrete strength, joints, drying shrinkage, and "
            "vapor retarder/barrier guidance is in 'Design of Concrete "
            "Floor Slabs-on-Ground for DoD Facilities' (WBDG, UFC 3-301-01 "
            "Related Materials)."
        ),
    },
    "masonry_veneer_base_detail": {
        "paragraph": "A-4.1", "printed_page": "106", "pdf_page": 127,
        "guidance": (
            "Base of masonry veneer on a foundation ledge at least 4 in. "
            "(102 mm) lower than the stud-wall base. See "
            "``masonry_veneer_ledge_offset`` for the printed ledge-width "
            "criterion."
        ),
    },
    "shelf_angles_for_masonry": {
        "paragraph": "A-5.1", "printed_page": "106", "pdf_page": 127,
        "guidance": (
            "Hot-dip galvanized structural steel, ~10 ft (3 m) segments "
            "with thermal-expansion gaps, corner pieces with 4 ft (1.2 m) "
            "legs. See ``shelf_angle_deflection_limit`` for the printed "
            "deflection criterion."
        ),
    },
    "steel_corrosive_environments": {
        "paragraph": "A-5.4", "printed_page": "107", "pdf_page": 128,
        "guidance": (
            "Design box-shaped members for inspection/cleaning/painting or "
            "seal entirely (unless galvanized); minimum 3/8 in. (9.5 mm) "
            "gap between back-to-back angle legs for air circulation; drain "
            "holes in horizontal-member pockets; cathodic protection in "
            "extremely corrosive conditions; galvanize/stainless-steel "
            "embedded members and exterior railings/anchor bolts; isolate "
            "dissimilar metals to prevent galvanic cells; galvanized steel "
            "deck (ASTM A653/A653M) for fireproofing compatibility. "
            "Reference: ASM Handbook Vol. 13B."
        ),
    },
    "steel_arctic_antarctic": {
        "paragraph": "A-5.5", "printed_page": "107-108", "pdf_page": "128-129",
        "guidance": (
            "For cyclic/impact loads in cold climates: ample fillets to "
            "avoid stress risers, prefer bolted joints (preheat/post-cool "
            "welded joints if used), and low-carbon/nickel-alloy steels "
            "with good low-temperature toughness."
        ),
    },
    "steel_base_plate_shear_transfer": {
        "paragraph": "A-5.6", "printed_page": "108", "pdf_page": 129,
        "guidance": (
            "Follow AISC Design Guide 1 (Base Plate and Anchor Rod Design). "
            "See the AISC research report 'Shear Transfer in Exposed Column "
            "Base Plates' (UC Berkeley testing) for shear-friction "
            "coefficient / anchor-rod bending-length / concrete shear-key "
            "bearing guidance."
        ),
    },
    "steel_joist_connections": {
        "paragraph": "A-5.7", "printed_page": "108", "pdf_page": 129,
        "guidance": (
            "Typical joist-supplier connection details may not provide "
            "adequate lateral/uplift capacity -- design each connection "
            "specifically for the project's lateral and uplift loads."
        ),
    },
    "wood_connections": {
        "paragraph": "A-6.1", "printed_page": "108", "pdf_page": 129,
        "guidance": (
            "Ensure a complete load path from roof to foundation when using "
            "prescriptive nailed-connection guidelines; metal plate "
            "connectors for trusses/top plates/sill plates provide a more "
            "robust load path."
        ),
    },
}


def best_practice_guidance(topic):
    """Appendix A: topic-indexed best-practice guidance (printed
    pp. 103-108).

    Parameters
    ----------
    topic : str
        A key of ``BEST_PRACTICE_TOPICS`` (e.g. 'building_drift_limits',
        'gable_bent_footings').

    Returns
    -------
    dict
        {'topic', 'paragraph', 'guidance', 'printed_page', 'pdf_page'}
    """
    key = topic.lower().strip()
    if key not in BEST_PRACTICE_TOPICS:
        raise ValueError(f"topic must be one of {sorted(BEST_PRACTICE_TOPICS)}, got {topic!r}")
    row = dict(BEST_PRACTICE_TOPICS[key])
    row["topic"] = key
    return row


def list_best_practice_topics():
    """Lists the Appendix A best-practice topic keys."""
    return sorted(BEST_PRACTICE_TOPICS)


# ============================================================================
# Printed numeric criteria embedded in the Appendix A narrative
# ============================================================================

def shelf_angle_deflection_limit():
    """Paragraph A-5.1: maximum deflection of the horizontal leg of a
    masonry shelf angle under masonry loading, at the end of the leg
    (including support rotation) (printed p. 106).

    Returns
    -------
    dict
        {'max_deflection_in': 0.0625, 'paragraph': 'A-5.1', 'printed_page':
         '106', 'pdf_page': 127}
    """
    return {"max_deflection_in": 1.0 / 16.0, "paragraph": "A-5.1",
            "printed_page": "106", "pdf_page": 127}


def masonry_veneer_ledge_offset():
    """Paragraph A-4.1: masonry veneer foundation ledge criteria (printed
    p. 106) -- the ledge must be at least 4 in. lower than the stud-wall
    base, and at least (2/3 * veneer thickness + minimum air space) wide.

    Returns
    -------
    dict
        {'min_ledge_drop_in': 4, 'min_ledge_width_fraction_of_veneer': 2/3,
         'paragraph': 'A-4.1', 'printed_page': '106', 'pdf_page': 127}
    """
    return {"min_ledge_drop_in": 4, "min_ledge_width_fraction_of_veneer": 2.0 / 3.0,
            "paragraph": "A-4.1", "printed_page": "106", "pdf_page": 127}


def gable_bent_tie_rod_force_range():
    """Paragraph A-2.1: the horizontal thrust force range above which tie
    rods (rather than hairpin bars) are usually the cost-effective choice
    for resisting metal-building gable-bent column-base reactions (printed
    p. 105).

    Returns
    -------
    dict
        {'min_force_kips': 40, 'max_force_kips': 50, 'min_force_kn': 118,
         'max_force_kn': 222, 'paragraph': 'A-2.1', 'printed_page': '105',
         'pdf_page': 126}
    """
    return {"min_force_kips": 40, "max_force_kips": 50, "min_force_kn": 118,
            "max_force_kn": 222, "paragraph": "A-2.1", "printed_page": "105", "pdf_page": 126}
