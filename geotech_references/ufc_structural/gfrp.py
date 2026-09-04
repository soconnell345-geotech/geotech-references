"""UFC 3-301-01 Appendix G [ADDITION] -- Glass Fiber-Reinforced Polymer
(GFRP) Bars for Concrete Structures (printed pp. 181-190, pdf_page
202-211).

This Appendix identifies DoD limits on GFRP reinforcement use (beyond what
ACI CODE 440.11-22 itself permits) and Table G-1's material-property
comparison against ASTM A615 steel reinforcement. GFRP design equations
(flexure, shear, serviceability, development) are NOT reprinted here --
this UFC defers entirely to ACI CODE 440.11-22 for those; only the DoD
applicability limits and comparison table are UFC-specific content.
"""

# ============================================================================
# Table G-1 -- Comparison of GFRP and Steel Material Properties
# (printed p. 185, pdf_page 206)
# ============================================================================

TABLE_G_1 = {
    "minimum_yield_strength": {
        "gfrp": "None, elastic until failure", "steel_astm_a615": "40, 60, 80, 100 ksi",
    },
    "ultimate_tensile_strength": {
        "gfrp": "77 ksi to 124 ksi", "steel_astm_a615": "60, 90, 105, 115 ksi",
    },
    "modulus_of_elasticity": {
        "gfrp_ksi": 6500, "steel_astm_a615_ksi": 29000,
    },
    "transverse_shear_strength": {
        "gfrp_ksi": 19, "steel_astm_a615": "same as yield strength",
    },
    "density": {
        "gfrp_lb_per_ft3": "approx. 135 (at 70% fiber mass content)",
        "steel_astm_a615_lb_per_ft3": 493,
    },
}


def table_g1_material_property(property_name):
    """Table G-1: GFRP (ASTM D7957/D7957M) vs. steel (ASTM A615/A615M)
    reinforcing bar material-property comparison (printed p. 185).

    Parameters
    ----------
    property_name : str
        A key of ``TABLE_G_1`` (e.g. 'modulus_of_elasticity',
        'ultimate_tensile_strength').

    Returns
    -------
    dict
        The property's GFRP/steel values plus {'property_name', 'table':
        'G-1', 'printed_page': '185', 'pdf_page': 206}.
    """
    key = property_name.lower().strip()
    if key not in TABLE_G_1:
        raise ValueError(f"property_name must be one of {sorted(TABLE_G_1)}, got {property_name!r}")
    row = dict(TABLE_G_1[key])
    row.update({"property_name": key, "table": "G-1", "printed_page": "185", "pdf_page": 206})
    return row


# ============================================================================
# GFRP applicability limits (paragraph G-1.3, printed pp. 181-182)
# ============================================================================

_GFRP_SEISMIC_PROHIBITED_SDC = ("B", "C", "D", "E", "F")
_GFRP_SEISMIC_PERMITTED_NON_LFRS_SDC = ("A", "B", "C")


def gfrp_seismic_applicability(seismic_design_category, is_part_of_lateral_force_resisting_system):
    """Paragraph G-1.3 / G-4.4: whether GFRP reinforcement is permitted for
    a given Seismic Design Category and structural role (printed pp.
    181-182, 208).

    - GFRP is NOT permitted in the seismic force-resisting system (SFRS)
      for SDC B, C, D, E, or F.
    - GFRP IS permitted in structural members NOT part of the SFRS for
      SDC A, B, or C.

    Parameters
    ----------
    seismic_design_category : str
        'A' through 'F'.
    is_part_of_lateral_force_resisting_system : bool
        True if the member is part of the seismic force-resisting system.

    Returns
    -------
    dict
        {'seismic_design_category', 'is_part_of_lfrs', 'permitted' (bool),
         'paragraph': 'G-1.3 / G-4.4', 'printed_page': '181-182, 208',
         'pdf_page': '202-203, 209'}
    """
    sdc = seismic_design_category.upper().strip()
    if sdc not in ("A", "B", "C", "D", "E", "F"):
        raise ValueError(f"seismic_design_category must be A-F, got {seismic_design_category!r}")
    if is_part_of_lateral_force_resisting_system:
        permitted = sdc not in _GFRP_SEISMIC_PROHIBITED_SDC
    else:
        permitted = sdc in _GFRP_SEISMIC_PERMITTED_NON_LFRS_SDC
    return {
        "seismic_design_category": sdc,
        "is_part_of_lfrs": is_part_of_lateral_force_resisting_system,
        "permitted": permitted, "paragraph": "G-1.3 / G-4.4",
        "printed_page": "181-182, 208", "pdf_page": "202-203, 209",
    }


def gfrp_fire_rating_limitation():
    """Paragraph G-1.3: DoD does not allow GFRP reinforcement in structures
    with a fire rating above zero, or in similar structures without a fire
    rating that could collapse due to fire and threaten life safety
    (printed pp. 181-182). Also prohibited in architectural cast-in-place
    concrete; permitted in architectural precast concrete only if all
    connections use steel.

    Returns
    -------
    dict
        {'max_fire_rating': 0, 'notes', 'paragraph': 'G-1.3',
         'printed_page': '181-182', 'pdf_page': '202-203'}
    """
    return {
        "max_fire_rating": 0,
        "notes": (
            "Not permitted in structures with fire rating above zero, nor "
            "in similar unrated structures that could collapse due to fire "
            "and threaten life safety (e.g. upper deck of double-deck "
            "piers). Not permitted in architectural cast-in-place concrete. "
            "Permitted in architectural precast concrete only if all "
            "connections use steel."
        ),
        "paragraph": "G-1.3", "printed_page": "181-182", "pdf_page": "202-203",
    }


# ============================================================================
# GFRP design factors (paragraphs G-3.2, G-4.2, G-5.1, G-5.3;
# printed pp. 184-188, pdf_page 205-209)
# ============================================================================

def gfrp_bend_strength_reduction_factor():
    """Paragraph G-3.2: minimum guaranteed ultimate tensile force of a bent
    portion of a GFRP bar, as a fraction of the straight-portion ultimate
    tensile force (ASTM D7957/D7957M) (printed p. 184). ACI CODE 440.11-22
    limits shear reinforcement stress to be compatible with this limit.

    Returns
    -------
    dict
        {'bend_strength_fraction': 0.60, 'paragraph': 'G-3.2',
         'printed_page': '184', 'pdf_page': 205}
    """
    return {"bend_strength_fraction": 0.60, "paragraph": "G-3.2",
            "printed_page": "184", "pdf_page": 205}


def gfrp_sustained_stress_limit():
    """Paragraph G-4.2: maximum sustained-stress limit on GFRP
    reinforcement, as a fraction of ultimate tensile stress, to address
    creep rupture and static fatigue (ACI CODE 440.11-22 Chapter 24)
    (printed pp. 185-186).

    Returns
    -------
    dict
        {'sustained_stress_fraction': 0.30, 'paragraph': 'G-4.2',
         'printed_page': '185-186', 'pdf_page': '206-207'}
    """
    return {"sustained_stress_fraction": 0.30, "paragraph": "G-4.2",
            "printed_page": "185-186", "pdf_page": "206-207"}


def gfrp_environmental_reduction_factor():
    """Paragraph G-5.1: environmental reduction factor, CE, applied to the
    guaranteed ultimate tensile strength of GFRP reinforcement to account
    for uncertainty in long-term durability predictive models (ACI CODE
    440.11-22 Chapter 20) (printed p. 187).

    Returns
    -------
    dict
        {'ce': 0.85, 'paragraph': 'G-5.1', 'printed_page': '187',
         'pdf_page': 208}
    """
    return {"ce": 0.85, "paragraph": "G-5.1", "printed_page": "187", "pdf_page": 208}


def gfrp_temperature_limits():
    """Paragraph G-5.3: minimum required glass transition temperature
    (ASTM D7957/D7957M) and the ACI CODE 440.11-22 suggested in-service
    temperature limit, 27 deg F below the glass transition temperature
    (printed pp. 187-188).

    Returns
    -------
    dict
        {'min_glass_transition_temp_f': 212, 'in_service_margin_below_tg_f': 27,
         'in_service_limit_f': 185, 'paragraph': 'G-5.3', 'printed_page':
         '187-188', 'pdf_page': '208-209'}
    """
    return {
        "min_glass_transition_temp_f": 212, "in_service_margin_below_tg_f": 27,
        "in_service_limit_f": 185, "paragraph": "G-5.3",
        "printed_page": "187-188", "pdf_page": "208-209",
    }


def gfrp_uv_exposure_storage_limit():
    """Paragraph G-5.3 / G-6: maximum outdoor storage duration before GFRP
    bars must be covered with opaque plastic, per the UFC's construction-
    specification limit (UFGS 03 30 00), which is more conservative than
    ACI 440.5's recommendation (printed pp. 188, 189).

    Returns
    -------
    dict
        {'ufgs_03_30_00_limit_months': 2, 'aci_440_5_limit_months': 4,
         'paragraph': 'G-5.3 / G-6', 'printed_page': '188, 189',
         'pdf_page': '209, 210'}
    """
    return {"ufgs_03_30_00_limit_months": 2, "aci_440_5_limit_months": 4,
            "paragraph": "G-5.3 / G-6", "printed_page": "188, 189", "pdf_page": "209, 210"}
