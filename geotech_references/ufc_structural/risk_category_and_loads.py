"""UFC 3-301-01 Chapter 2 (Section 1604) + Appendix E -- risk category,
deflection limits, and minimum live loads.

Table 2-1 (wind-induced deflection limits, printed p. 10, REPLACEMENT
introduced by Change 4), Table 2-2 (risk category, printed pp. 11-14,
REPLACES IBC Table 1604.5 / ASCE 7-22 Tables 1.5-1 and 1.5-2 -- see
``seismic_force_resisting_systems`` module docstring cross-reference and
``general_provisions.risk_category_v_note`` for the added Risk Category V),
Table E-1 (Appendix E, printed pp. 153-159, REPLACES IBC Table 1607.1),
Section 1609.3.1 wind-speed conversion equations, and the paragraph
1605.1.2 vertical-ground-motion-sensitive-member threshold.
"""

# ============================================================================
# Table 2-1 -- Wind Induced Deflection Limits for Framing Supporting
# Exterior Wall Finishes (printed p. 10, pdf_page 31; \4\/4/ = Change 4)
# ============================================================================

TABLE_2_1_DEFLECTION_LIMITS = {
    "brick_veneer": "L/600",
    "exterior_insulation_finish_systems": "L/240",
    "cement_board": "L/360",
    "stone_masonry": "verify with stone supplier",
    "plywood_and_wood_based_structural_use_panels": "L/240",
    "gypsum_sheathing": "L/240",
    "metal_or_vinyl_siding_and_insulated_metal_panel": "L/120",
}


def table_2_1_wind_deflection_limit(cladding_type):
    """Table 2-1: wind-induced deflection limit for framing supporting a
    given exterior wall finish (printed p. 10, IBC Section 1604.3.1
    replacement).

    Per footnote a, the wind load may be taken as 0.42 times the component-
    and-cladding wind load for this deflection check. Per footnote b,
    L = k*l where k is the theoretical effective length factor and l is the
    member length between supports.

    Parameters
    ----------
    cladding_type : str
        A key of ``TABLE_2_1_DEFLECTION_LIMITS`` (e.g. 'brick_veneer').

    Returns
    -------
    dict
        {'cladding_type', 'deflection_limit', 'wind_load_factor': 0.42,
         'table': '2-1', 'printed_page': '10', 'pdf_page': 31}
    """
    key = cladding_type.lower().strip().replace(" ", "_").replace("-", "_")
    if key not in TABLE_2_1_DEFLECTION_LIMITS:
        raise ValueError(
            f"cladding_type must be one of {sorted(TABLE_2_1_DEFLECTION_LIMITS)}, "
            f"got {cladding_type!r}"
        )
    return {
        "cladding_type": key, "deflection_limit": TABLE_2_1_DEFLECTION_LIMITS[key],
        "wind_load_factor": 0.42, "table": "2-1",
        "printed_page": "10", "pdf_page": 31,
    }


# ============================================================================
# Table 2-2 -- Risk Category of Buildings and Other Structures
# (printed pp. 11-14, pdf_page 32-35). REPLACES IBC Table 1604.5 AND
# ASCE 7-22 Tables 1.5-1/1.5-2 (paragraph 3-1.2). DoD adds Risk Category V
# and the "DoD Sea Level Rise (SLR) Scenario" column (2065-horizon).
# ============================================================================

TABLE_2_2_RISK_CATEGORY = {
    "I": {
        "nature": (
            "Low hazard to human life in the event of failure (e.g. "
            "agricultural facilities, certain temporary facilities, minor "
            "storage facilities)."
        ),
        "seismic_factor_ie": 1.00, "tsunami_factor_itsu": None,
        "tsunami_note": "Tsunami design not required",
        "slr_scenario": "N/A",
    },
    "II": {
        "nature": "Buildings and other structures except those listed in RC I, III, IV, V.",
        "seismic_factor_ie": 1.00, "tsunami_factor_itsu": 1.00,
        "tsunami_note": None,
        "slr_scenario": "Low (2065)",
    },
    "III": {
        "nature": (
            "Substantial hazard to human life or significant economic loss "
            "in the event of failure (e.g. public assembly >300 occupants, "
            "schools >250 occupants, colleges/universities >500 occupants, "
            "Group I-3 Condition 1, occupancy >5,000, quantities of toxic/"
            "flammable/explosive materials exceeding MAQ per Table "
            "307.1(1)/(2))."
        ),
        "seismic_factor_ie": 1.25, "tsunami_factor_itsu": 1.25,
        "tsunami_note": None,
        "slr_scenario": "Medium (2065)",
    },
    "IV": {
        "nature": (
            "Essential facilities and buildings where loss of function is a "
            "substantial hazard to occupants/users (e.g. Group I-2 "
            "Condition 2, emergency surgery/treatment facilities, Group I-3 "
            "other than Condition 1, fire/rescue/ambulance/police stations, "
            "designated emergency shelters/EOCs, public utility power/water/"
            "wastewater treatment, ATCTs/RACF, highly-toxic-material "
            "quantities exceeding MAQ per Table 307.1(2), DoD mission-"
            "essential command/control/communications/intel functions not "
            "duplicated elsewhere, fire-suppression water storage/pump "
            "structures)."
        ),
        "seismic_factor_ie": 1.50, "tsunami_factor_itsu": 1.25,
        "tsunami_note": None,
        "slr_scenario": "High (2065)",
    },
    "V": {
        "nature": (
            "Facilities designed as national strategic military defensive "
            "assets (e.g. Defense Critical Assets (DCA), facilities "
            "directly supporting operational nuclear armed missile defense, "
            "emergency backup/primary power generation for RC V occupancy, "
            "facilities storing/handling/processing nuclear/chemical/"
            "biological/radiological materials where structural failure "
            "could have widespread catastrophic consequences)."
        ),
        "seismic_factor_ie": 1.00, "tsunami_factor_itsu": 1.25,
        "tsunami_note": None,
        "slr_scenario": "Highest (2065)",
    },
}

TABLE_2_2_NOTES = {
    "a": (
        "For occupant-load calculations, occupancies required by IBC Table "
        "1004.5 to use gross floor area may instead use net floor area; "
        "vehicular drive aisle area in parking garages may be excluded."
    ),
    "b": (
        "Where approved by the AHJ, RC III/IV classification based on "
        "toxic/highly-toxic/explosive material quantity may be reduced to "
        "RC II if a hazard assessment per ASCE 7 Section 1.5.3 shows a "
        "release would not threaten the public."
    ),
    "c": (
        "Risk Category V addresses national strategic military assets; RC "
        "V structures are designed to remain elastic during the MCER. See "
        "UFC 3-301-02 for RC V design."
    ),
    "d": "These facilities may be designed for Tsunami Risk Category I or II as approved by the AHJ.",
    "e": (
        "These facilities may be designed for Tsunami Risk Category I, II "
        "or III as designated by the AHJ if adequate equivalent facilities "
        "are available outside (or designed within) the inundation zone."
    ),
    "f": (
        "Use the site-specific value from the DoD Regional Sea Level "
        "(DRSL) database for the designated 2065 scenario "
        "(low/medium/high/highest); https://sealevelscenarios.serdp-estcp.org"
    ),
    "g": (
        "Subject to AHJ approval, a DoD 2065 SLR scenario of Medium may be "
        "used for RC IV/V structures when designing for combined tsunami "
        "and sea level rise (see paragraph 3-3.1)."
    ),
    "h": (
        "Defense Critical Assets must be explicitly listed in the OSD "
        "approved Mission Assurance tracking system per DODI 3020.40 and "
        "3020.45."
    ),
}


def table_2_2_risk_category(risk_category):
    """Table 2-2: risk category assignment data, REPLACING IBC Table 1604.5
    and ASCE 7-22 Tables 1.5-1/1.5-2 (printed pp. 11-14; paragraph 3-1.2).

    Adds Risk Category V (national strategic military assets, not in the
    2024 IBC/ASCE 7-22) and a DoD Sea Level Rise 2065-scenario column not
    present in the civilian tables.

    Parameters
    ----------
    risk_category : str
        'I', 'II', 'III', 'IV', or 'V'.

    Returns
    -------
    dict
        {'risk_category', 'nature', 'seismic_factor_ie', 'tsunami_factor_itsu',
         'tsunami_note', 'slr_scenario', 'table': '2-2', 'printed_page':
         '11-14', 'pdf_page': '32-35'}
    """
    key = str(risk_category).upper().strip()
    if key not in TABLE_2_2_RISK_CATEGORY:
        raise ValueError(f"risk_category must be one of I/II/III/IV/V, got {risk_category!r}")
    row = dict(TABLE_2_2_RISK_CATEGORY[key])
    row.update({"risk_category": key, "table": "2-2",
                "printed_page": "11-14", "pdf_page": "32-35"})
    return row


def table_2_2_note(note_id):
    """A lettered footnote to Table 2-2 (printed pp. 12-14).

    Parameters
    ----------
    note_id : str
        A key of ``TABLE_2_2_NOTES`` ('a' through 'h').

    Returns
    -------
    dict
        {'note_id', 'text', 'table': '2-2', ...}
    """
    key = note_id.lower().strip()
    if key not in TABLE_2_2_NOTES:
        raise ValueError(f"note_id must be one of {sorted(TABLE_2_2_NOTES)}, got {note_id!r}")
    return {"note_id": key, "text": TABLE_2_2_NOTES[key], "table": "2-2",
            "printed_page": "12-14", "pdf_page": "33-35"}


# ============================================================================
# Section 1609.3.1 -- Wind Speed Conversion (printed p. 19, pdf_page 40)
# ============================================================================

def wind_speed_conversion_asd(v):
    """Eq 16-18a: converts basic (strength-level) wind speed to an
    allowable-stress-design wind speed (printed p. 19).

        Vasd = sqrt(0.6*V)

    Parameters
    ----------
    v : float
        Basic wind speed, V (mph or consistent unit).

    Returns
    -------
    dict
        {'v', 'v_asd', 'equation': '16-18a', 'printed_page': '19',
         'pdf_page': 40}
    """
    v_asd = (0.6 * v) ** 0.5
    return {"v": v, "v_asd": v_asd, "equation": "16-18a",
            "printed_page": "19", "pdf_page": 40}


def wind_speed_conversion_fastest_mile(v):
    """Eq 16-18b: converts basic wind speed to a fastest-mile wind speed
    (printed p. 19).

        Vfm = (sqrt(0.6*V) - 10.5) / 1.05

    Parameters
    ----------
    v : float
        Basic wind speed, V (mph).

    Returns
    -------
    dict
        {'v', 'v_fm', 'equation': '16-18b', 'printed_page': '19',
         'pdf_page': 40}
    """
    v_fm = ((0.6 * v) ** 0.5 - 10.5) / 1.05
    return {"v": v, "v_fm": v_fm, "equation": "16-18b",
            "printed_page": "19", "pdf_page": 40}


def nonpermanent_structure_wind_reduction_factor():
    """Paragraph 1609.3.3: basic-wind-speed reduction factor permitted for
    non-permanent structures (design life <= 5 years) per UFC 1-201-01,
    applicable both inside and outside hurricane-prone regions per this
    UFC's Change (printed pp. 20-21). Supersedes UFC 1-201-01 paragraph
    3-2.1.5 and IBC Section 3103.6.1.2.

    Returns
    -------
    dict
        {'reduction_factor': 0.78, 'paragraph': '1609.3.3', 'printed_page':
         '20', 'pdf_page': 41}
    """
    return {"reduction_factor": 0.78, "paragraph": "1609.3.3",
            "printed_page": "20", "pdf_page": 41}


# ============================================================================
# Paragraph 1605.1.2 -- Structural Members Sensitive to Vertical Ground
# Motion (printed pp. 14-15, pdf_page 35-36)
# ============================================================================

_VGM_SENSITIVE_BUILDING_MEMBERS = [
    "horizontal or nearly horizontal structural members spanning 65 ft or more",
    "horizontal or nearly horizontal cantilever components longer than 16 ft",
    "horizontal or nearly horizontal prestressed components",
    "building components (excluding foundations) where gravity-load demand exceeds 80% of nominal strength",
    "horizontal structural elements supporting discontinuous vertical elements of the gravity load-resisting system",
    "base-isolated structures",
]

_VGM_SENSITIVE_NONBUILDING_MEMBERS = [
    "long-span roof structures (e.g. stadiums, aircraft maintenance hangar header truss)",
    "electric power generation facilities",
]


def vertical_ground_motion_threshold_check(sds):
    """Paragraph 1605.1.2: determines whether the design short-period
    spectral response acceleration, SDS, triggers the additional load
    combinations of paragraph 2.3.6/2.4.5 for vertical-ground-motion-
    sensitive members (printed pp. 14-15). Threshold: SDS > 0.6g (derived
    from a 2004 Eurocode 8 peak-vertical-ground-acceleration criterion,
    avg > 0.25g, per the [C] commentary).

    Nonbuilding structures addressed by ASCE 7-22 Section 15.1.4 are exempt
    regardless of SDS.

    Parameters
    ----------
    sds : float
        Design spectral response acceleration at short periods, in units
        of g (e.g. 0.65 for 0.65g).

    Returns
    -------
    dict
        {'sds', 'threshold': 0.6, 'triggers_additional_combinations' (bool),
         'sensitive_building_members', 'sensitive_nonbuilding_members',
         'paragraph': '1605.1.2', 'printed_page': '14-15', 'pdf_page': '35-36'}
    """
    triggers = sds > 0.6
    return {
        "sds": sds, "threshold": 0.6,
        "triggers_additional_combinations": triggers,
        "sensitive_building_members": list(_VGM_SENSITIVE_BUILDING_MEMBERS),
        "sensitive_nonbuilding_members": list(_VGM_SENSITIVE_NONBUILDING_MEMBERS),
        "paragraph": "1605.1.2", "printed_page": "14-15", "pdf_page": "35-36",
    }


# ============================================================================
# Table E-1 -- Minimum Uniformly Distributed Live Loads, Lo, and Minimum
# Concentrated Live Loads (Appendix E, printed pp. 153-159, pdf_page
# 174-180). REPLACES IBC Table 1607.1; occupancies shown bold-italic in the
# source (military-specific additions) are flagged ``military_added=True``.
#
# Each entry: {'uniform_psf', 'uniform_kpa', 'concentrated_lb',
# 'concentrated_kn', 'notes' (list of TABLE_E1_NOTES keys), 'pointer' (str,
# only for rows that defer entirely to an IBC section), 'military_added'
# (bool)}. A None value means "no requirement / dash (---) in the printed
# table" for that load type. A few sub-rows near the page 157-158 break
# (some "Roofs" occupancy-other-than-assembly / PV-shade-structure entries)
# have an ambiguous text-extraction order and are DELIBERATELY OMITTED --
# see the module docstring gap note; consult the printed table directly.
# ============================================================================

TABLE_E1_NOTES = {
    "a": "Where snow loads exceed design conditions, design for the increased drift/snow load per the AHJ (see IBC Section 1608).",
    "b": "See IBC Section 1604.8.3 for decks attached to exterior walls.",
    "c": "Occupiable-roof areas (other than roof gardens/assembly) are designed for AHJ-approved loads; unoccupied landscaped roof areas per IBC Section 1607.13.3.",
    "d": "Live load reduction is not permitted.",
    "e": "Live load reduction is only permitted per Section 1607.13.1.2 or Item 1 of Section 1607.13.2.",
    "f": "Live load reduction is only permitted per Section 1607.13.1.3 or Item 2 of Section 1607.13.2.",
    "g": "Helipads supporting military aircraft must be designed for the actual aircraft weight and landing impact.",
    "h": "All attics with mechanical units must be designed for mechanical equipment room loading.",
    "i": "For pedestrian bridge live loads, see AASHTO LRFD Guide Specifications for the Design of Pedestrian Bridges.",
    "j": "High-density data center rack space should be verified per project; some systems exceed 400 psf.",
}

TABLE_E1_LIVE_LOADS = {
    "access_floor_office_use": {"uniform_psf": 50, "uniform_kpa": 2.4, "concentrated_lb": 2000, "concentrated_kn": 8.9},
    "access_floor_computer_use": {"uniform_psf": 100, "uniform_kpa": 4.8, "concentrated_lb": 2000, "concentrated_kn": 8.9},
    "ammunition_storage_high_explosives_one_story": {"uniform_psf": 500, "uniform_kpa": 23.9, "military_added": True},
    "ammunition_storage_inert_explosives_one_story": {"uniform_psf": 500, "uniform_kpa": 23.9, "military_added": True},
    "ammunition_storage_pyrotechnics_one_story": {"uniform_psf": 500, "uniform_kpa": 23.9, "military_added": True},
    "ammunition_storage_small_arms_one_story": {"uniform_psf": 500, "uniform_kpa": 23.9, "military_added": True},
    "ammunition_storage_torpedo_one_story": {"uniform_psf": 350, "uniform_kpa": 16.8, "military_added": True},
    "armories_and_drill_rooms": {"uniform_psf": 150, "uniform_kpa": 7.2, "notes": ["d"]},
    "assembly_fixed_seats": {"uniform_psf": 60, "uniform_kpa": 2.9, "notes": ["d"]},
    "assembly_lobbies": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
    "assembly_movable_seats": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
    "assembly_stage_floors": {"uniform_psf": 150, "uniform_kpa": 7.2, "notes": ["d"]},
    "assembly_platforms": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
    "assembly_other_areas": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
    "balconies_and_decks": {
        "uniform_psf": "1.5x live load of area served, not required to exceed 100",
        "uniform_kpa": "1.5x live load of area served, not required to exceed 4.8",
        "notes": ["b"],
        "note_text": "Balconies serving as primary means of egress for multiple rooms must be considered corridors.",
    },
    "battery_charging_room": {"uniform_psf": 200, "uniform_kpa": 9.6},
    "boiler_houses": {"uniform_psf": 200, "uniform_kpa": 9.6},
    "catwalks_maintenance_service_access": {"uniform_psf": 40, "uniform_kpa": 1.9, "concentrated_lb": 300, "concentrated_kn": 1.33},
    "cleaning_gear_trash_room_compactor": {"uniform_psf": 75, "uniform_kpa": 3.6},
    "cold_storage_first_floor": {"uniform_psf": 400, "uniform_kpa": 19.2},
    "cold_storage_upper_floors": {"uniform_psf": 300, "uniform_kpa": 14.4},
    "command_duty_officer_day_room": {"uniform_psf": 60, "uniform_kpa": 2.9, "military_added": True},
    "cornices": {"uniform_psf": 60, "uniform_kpa": 2.9},
    "corridors_first_floor": {"uniform_psf": 100, "uniform_kpa": 4.8},
    "corridors_other_floors": {"pointer": "Same as occupancy served, except as otherwise indicated in this table."},
    "court_rooms": {"uniform_psf": 80, "uniform_kpa": 3.8},
    "dining_rooms_and_restaurants": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
    "elevator_machine_room_control_room_grating": {"concentrated_lb": 300, "concentrated_kn": 1.33, "note_text": "On area 2 in. x 2 in. (50.8 x 50.8 mm)."},
    "finish_light_floor_plate_construction": {"concentrated_lb": 200, "concentrated_kn": 0.89, "note_text": "On area 1 in. x 1 in. (25.4 x 25.4 mm)."},
    "fire_escapes": {"uniform_psf": 100, "uniform_kpa": 4.8},
    "fire_escapes_single_family_dwellings": {"uniform_psf": 40, "uniform_kpa": 1.9},
    "fixed_ladders": {"pointer": "See IBC Section 1607.10 for uniform and concentrated loads."},
    "galleys_dishwashing_rooms": {"uniform_psf": 300, "uniform_kpa": 14.4, "military_added": True},
    "galleys_general_kitchen_area": {"uniform_psf": 250, "uniform_kpa": 12.0, "military_added": True},
    "galleys_provision_storage_not_refrigerated": {"uniform_psf": 200, "uniform_kpa": 9.6, "military_added": True},
    "galleys_preparation_room_meat": {"uniform_psf": 250, "uniform_kpa": 12.0, "military_added": True},
    "galleys_preparation_room_vegetable": {"uniform_psf": 100, "uniform_kpa": 4.8, "military_added": True},
    "garages_passenger_vehicle": {"uniform_psf": 40, "uniform_kpa": 1.9, "notes": ["f"]},
    "garages_trucks_and_buses": {"pointer": "See IBC Section 1607.8."},
    "garages_fire_trucks_and_emergency_vehicles": {"pointer": "See IBC Section 1607.8."},
    "garages_forklifts_and_movable_equipment": {"pointer": "See IBC Section 1607.8."},
    "generator_rooms": {"uniform_psf": 200, "uniform_kpa": 9.6},
    "guard_house": {"uniform_psf": 75, "uniform_kpa": 3.6, "military_added": True},
    "handrails_guards_and_grab_bars": {"pointer": "See IBC Section 1607.9."},
    "helipads_takeoff_weight_le_3000lb": {"uniform_psf": 40, "uniform_kpa": 1.9, "notes": ["d", "g"], "concentrated_pointer": "See IBC Section 1607.6.1."},
    "helipads_takeoff_weight_gt_3000lb": {"uniform_psf": 60, "uniform_kpa": 2.9, "notes": ["d", "g"], "concentrated_pointer": "See IBC Section 1607.6.1."},
    "hospitals_corridors_above_first_floor": {"uniform_psf": 80, "uniform_kpa": 3.8, "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "hospitals_operating_rooms_laboratories": {"uniform_psf": 60, "uniform_kpa": 2.9, "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "hospitals_patient_rooms": {"uniform_psf": 40, "uniform_kpa": 1.9, "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "incinerators_charging_room": {"uniform_psf": 150, "uniform_kpa": 7.2},
    "laboratories_normal_scientific_equipment": {"uniform_psf": 125, "uniform_kpa": 6.0},
    "latrines_heads_toilets_washroom": {"uniform_psf": 75, "uniform_kpa": 3.6, "military_added": True},
    "libraries_reading_rooms": {"uniform_psf": 60, "uniform_kpa": 2.9, "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "libraries_stack_rooms": {"uniform_psf": 150, "uniform_kpa": 7.2, "notes": ["e"], "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "libraries_corridors_above_first_floor": {"uniform_psf": 80, "uniform_kpa": 3.8, "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "manufacturing_light": {"uniform_psf": 125, "uniform_kpa": 6.0, "notes": ["d"], "concentrated_lb": 2000, "concentrated_kn": 8.90},
    "manufacturing_heavy": {"uniform_psf": 250, "uniform_kpa": 12.0, "notes": ["d"], "concentrated_lb": 3000, "concentrated_kn": 13.34},
    "marquees": {"uniform_psf": 75, "uniform_kpa": 3.6},
    "mechanical_equipment_room_general": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["h"]},
    "mechanical_room_hvac_elevator_machine": {"uniform_psf": 125, "uniform_kpa": 6.0},
    "mechanical_telephone_radio_equipment_room": {"uniform_psf": 150, "uniform_kpa": 7.2},
    "morgue": {"uniform_psf": 100, "uniform_kpa": 4.8, "military_added": True},
    "office_file_and_computer_rooms": {"pointer": "Design for heavier loads based on anticipated occupancy."},
    "office_lobbies_first_floor_corridors": {"uniform_psf": 100, "uniform_kpa": 4.8, "concentrated_lb": 2000, "concentrated_kn": 8.9},
    "office_offices": {"uniform_psf": 50, "uniform_kpa": 2.4, "concentrated_lb": 2000, "concentrated_kn": 8.9},
    "office_corridors_above_first_floor": {"uniform_psf": 80, "uniform_kpa": 3.8, "concentrated_lb": 2000, "concentrated_kn": 8.9},
    "penal_institutions_cell_blocks": {"uniform_psf": 40, "uniform_kpa": 1.9},
    "penal_institutions_corridors": {"uniform_psf": 100, "uniform_kpa": 4.8},
    "post_offices_general_area": {"uniform_psf": 100, "uniform_kpa": 4.8},
    "post_offices_work_rooms": {"uniform_psf": 125, "uniform_kpa": 6.0},
    "power_plants": {"uniform_psf": 200, "uniform_kpa": 9.6},
    "projection_booths": {"uniform_psf": 100, "uniform_kpa": 4.8},
    "pump_houses": {"uniform_psf": 100, "uniform_kpa": 4.8},
    "recreation_room": {"uniform_psf": 100, "uniform_kpa": 4.8, "military_added": True},
    "recreational_bowling_alleys_poolrooms": {"uniform_psf": 75, "uniform_kpa": 3.6, "notes": ["d"]},
    "recreational_dance_halls_ballrooms": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
    "recreational_gymnasiums": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
    "recreational_theater_projection_control_rooms": {"uniform_psf": 50, "uniform_kpa": 2.4},
    "recreational_ice_skating_rink": {"uniform_psf": 250, "uniform_kpa": 12, "notes": ["e"]},
    "recreational_reviewing_stands_grandstands_bleachers": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"], "pointer": "See IBC Section 1607.18."},
    "recreational_roller_skating_rink": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
    "recreational_stadiums_arenas_fixed_seats": {"uniform_psf": 60, "uniform_kpa": 2.9, "notes": ["d"], "pointer": "See IBC Section 1607.18."},
    "receiving_rooms_radio_incl_antenna_roof_areas": {"uniform_psf": 150, "uniform_kpa": 7.2},
    "refrigeration_storage_dairy": {"uniform_psf": 200, "uniform_kpa": 9.6},
    "refrigeration_storage_meat": {"uniform_psf": 250, "uniform_kpa": 12.0},
    "refrigeration_storage_vegetable": {"uniform_psf": 275, "uniform_kpa": 13.2},
    "residential_1_2_family_uninhabitable_attics_no_storage": {"uniform_psf": 10, "uniform_kpa": 0.5},
    "residential_1_2_family_uninhabitable_attics_with_storage": {"uniform_psf": 20, "uniform_kpa": 1.0},
    "residential_1_2_family_habitable_attics_sleeping_areas": {"uniform_psf": 30, "uniform_kpa": 1.4},
    "residential_1_2_family_canopies_incl_marquees": {"uniform_psf": 20, "uniform_kpa": 1.0},
    "residential_1_2_family_all_other_areas_except_stairs": {"uniform_psf": 40, "uniform_kpa": 1.9},
    "residential_hotel_multifamily_private_rooms_and_corridors": {"uniform_psf": 40, "uniform_kpa": 1.9},
    "residential_hotel_multifamily_corridors_egress_multiple_rooms": {"uniform_psf": 80, "uniform_kpa": 3.8, "notes": ["d"]},
    "residential_hotel_multifamily_public_rooms": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
    "residential_hotel_multifamily_corridors_serving_public_rooms": {"uniform_psf": 100, "uniform_kpa": 4.8},
    "roofs_all_surfaces_subject_to_maintenance_workers": {"concentrated_lb": 300, "concentrated_kn": 1.33},
    "roofs_awnings_canopies_fabric_construction": {"uniform_psf": 5, "uniform_kpa": 0.23, "notes": ["d"]},
    "roofs_awnings_canopies_other_construction": {"uniform_psf": 20, "uniform_kpa": 1.0},
    "roofs_ordinary_flat_pitched_curved_not_occupiable": {"uniform_psf": 20, "uniform_kpa": 1.0},
    "roofs_primary_members_single_panel_point_over_manufacturing_storage_garages": {"concentrated_lb": 2000, "concentrated_kn": 8.9},
    "roofs_primary_members_all_other": {"concentrated_lb": 300, "concentrated_kn": 1.33},
    "roofs_vegetative_roof_gardens": {"uniform_psf": 100, "uniform_kpa": 4.8},
    "roofs_vegetative_not_intended_for_occupancy": {"uniform_psf": 20, "uniform_kpa": 1.0},
    "roofs_vegetative_used_for_assembly": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
    "schools_classrooms": {"uniform_psf": 40, "uniform_kpa": 1.9, "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "schools_corridors_above_first_floor": {"uniform_psf": 80, "uniform_kpa": 3.8, "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "schools_first_floor_corridors": {"uniform_psf": 100, "uniform_kpa": 4.8, "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "scuttles_skylight_ribs_accessible_ceilings": {"concentrated_lb": 200, "concentrated_kn": 0.89},
    "shops_aircraft_utility": {"uniform_psf": 200, "uniform_kpa": 9.6, "military_added": True},
    "shops_assembly_and_repair": {"uniform_psf": 250, "uniform_kpa": 12.0, "military_added": True},
    "shops_bombsight_without_shielding": {"uniform_psf": 125, "uniform_kpa": 6.0, "military_added": True},
    "shops_carpenter": {"uniform_psf": 125, "uniform_kpa": 6.0, "military_added": True},
    "shops_electrical": {"uniform_psf": 300, "uniform_kpa": 14.4, "military_added": True},
    "shops_engine_overhaul": {"uniform_psf": 300, "uniform_kpa": 14.4, "military_added": True},
    "sidewalks_vehicular_driveways_yards_trucking": {"uniform_psf": 250, "uniform_kpa": 12.0, "notes": ["e"], "concentrated_lb": 8000, "concentrated_kn": 35.6},
    "stairs_exits_1_2_family_dwellings": {"uniform_psf": 40, "uniform_kpa": 1.9, "concentrated_lb": 300, "concentrated_kn": 1.3},
    "stairs_exits_all_other": {"uniform_psf": 100, "uniform_kpa": 4.8, "concentrated_lb": 300, "concentrated_kn": 1.3},
    "storage_warehouses_general_light": {"uniform_psf": 125, "uniform_kpa": 6.0, "notes": ["e"]},
    "storage_warehouses_general_heavy": {"uniform_psf": 250, "uniform_kpa": 12},
    "storage_warehouses_aircraft": {"uniform_psf": 200, "uniform_kpa": 9.6, "military_added": True},
    "storage_warehouses_building_materials": {"uniform_psf": 250, "uniform_kpa": 12},
    "storage_warehouses_drugs_paint_oil": {"uniform_psf": 200, "uniform_kpa": 9.6},
    "storage_warehouses_dry_provisions": {"uniform_psf": 300, "uniform_kpa": 14.4, "military_added": True},
    "storage_warehouses_groceries_wine_liquor": {"uniform_psf": 300, "uniform_kpa": 14.4},
    "storage_warehouses_light_tools": {"uniform_psf": 150, "uniform_kpa": 7.2, "military_added": True},
    "storage_warehouses_pipe_and_metal": {"uniform_psf": 1000, "uniform_kpa": 48, "military_added": True},
    "storage_warehouses_paint_and_oil_one_story": {"uniform_psf": 500, "uniform_kpa": 24},
    "storage_warehouses_hardware": {"uniform_psf": 300, "uniform_kpa": 14.4},
    "stores_retail_first_floor": {"uniform_psf": 100, "uniform_kpa": 4.8, "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "stores_retail_upper_floors": {"uniform_psf": 75, "uniform_kpa": 3.6, "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "stores_wholesale_all_floors": {"uniform_psf": 125, "uniform_kpa": 6.0, "notes": ["e"], "concentrated_lb": 1000, "concentrated_kn": 4.45},
    "tailor_shop": {"uniform_psf": 75, "uniform_kpa": 3.6, "military_added": True},
    "telephone_exchange_rooms": {"uniform_psf": 150, "uniform_kpa": 7.2, "concentrated_lb": 2000, "concentrated_kn": 8.9},
    "computer_server_high_density_data_center_rack_space": {
        "uniform_psf": 300, "concentrated_lb": 3000, "notes": ["j"],
        "note_text": (
            "Change 4 addition; SI (kPa/kN) columns did not resolve in "
            "text extraction for this row -- verify against the printed "
            "table (p. 158) if metric units are needed."
        ),
    },
    "vehicle_barriers": {"pointer": "See IBC Section 1607.11."},
    "walkways_elevated_platforms_range_climbing_training_towers": {"uniform_psf": 60, "uniform_kpa": 2.9, "military_added": True},
    "walkways_pedestrian_bridges": {"pointer": "AASHTO LRFD Guide Specifications for the Design of Pedestrian Bridges.", "notes": ["i"]},
    "yards_and_terraces_pedestrian": {"uniform_psf": 100, "uniform_kpa": 4.8, "notes": ["d"]},
}


def table_e1_live_load(occupancy):
    """Table E-1: minimum uniformly distributed live load and minimum
    concentrated live load for an occupancy or use classification
    (Appendix E, printed pp. 153-159). REPLACES IBC Table 1607.1;
    occupancies with ``military_added=True`` are DoD-specific additions to
    the base IBC table (shown bold-italic in the source).

    Parameters
    ----------
    occupancy : str
        A key of ``TABLE_E1_LIVE_LOADS`` (e.g. 'office_offices',
        'hospitals_patient_rooms').

    Returns
    -------
    dict
        The occupancy's row data plus {'occupancy', 'table': 'E-1',
        'printed_page': '153-159', 'pdf_page': '174-180'}.
    """
    key = occupancy.lower().strip()
    if key not in TABLE_E1_LIVE_LOADS:
        raise ValueError(f"Unknown occupancy {occupancy!r}; see list_table_e1_occupancies()")
    row = dict(TABLE_E1_LIVE_LOADS[key])
    row.update({"occupancy": key, "table": "E-1",
                "printed_page": "153-159", "pdf_page": "174-180"})
    return row


def table_e1_note(note_id):
    """A lettered footnote to Table E-1 (printed pp. 158-159).

    Parameters
    ----------
    note_id : str
        A key of ``TABLE_E1_NOTES`` ('a' through 'j').

    Returns
    -------
    dict
        {'note_id', 'text', 'table': 'E-1', ...}
    """
    key = note_id.lower().strip()
    if key not in TABLE_E1_NOTES:
        raise ValueError(f"note_id must be one of {sorted(TABLE_E1_NOTES)}, got {note_id!r}")
    return {"note_id": key, "text": TABLE_E1_NOTES[key], "table": "E-1",
            "printed_page": "158-159", "pdf_page": "179-180"}


def list_table_e1_occupancies(military_added_only=False):
    """Lists the occupancy keys in ``TABLE_E1_LIVE_LOADS``.

    Parameters
    ----------
    military_added_only : bool, optional
        If True, return only DoD/military-specific additions to the base
        IBC Table 1607.1 (shown bold-italic in the source). Default False
        (return all).

    Returns
    -------
    list of str
    """
    if not military_added_only:
        return sorted(TABLE_E1_LIVE_LOADS)
    return sorted(k for k, v in TABLE_E1_LIVE_LOADS.items() if v.get("military_added"))
