"""UFC 4-023-03 Chapters 6, 7, 8 -- Masonry, Wood, and Cold-Formed Steel
(printed pp. 71-76, pdf_page 86-91).

All three chapters follow an identical structure: material properties and
Phi point to a civilian code (not reprinted), Tie Force requirements are
the material-independent Section 3-1 equations (``tie_forces.py``), the
Alternate Path method uses the material-independent Section 3-2 procedure
(``alternate_path.py``) with ASCE 41 Life-Safety modeling parameters/
m-factors from ASCE 41 Chapter 11 (masonry) or Chapter 12 (wood, cold-
formed steel) -- NOT reprinted in this UFC, and Enhanced Local Resistance
is the material-independent Section 3-3 procedure (``enhanced_local_
resistance.py``). Each chapter is combined into one module here given how
little material-specific content each one prints (a handful of pointers
and, for wood, two numeric factors).
"""


# ============================================================================
# Chapter 6 -- Masonry (printed pp. 71-72, pdf_page 86-87)
# ============================================================================

def masonry_material_code_references():
    """Sections 6-1, 6-2: masonry over-strength factors and strength
    reduction factor Phi are NOT reprinted in this UFC -- apply ASCE 41
    Table 11-1 (lower-bound-to-expected-strength factors) and ACI 530
    Building Code Requirements for Masonry Structures (Phi, by limit
    state), respectively (printed p. 71).

    Returns
    -------
    dict
        {'overstrength_factor_source': 'ASCE 41 Table 11-1',
         'phi_source': 'ACI 530', 'paragraph': '6-1, 6-2',
         'printed_page': '71', 'pdf_page': 86}
    """
    return {"overstrength_factor_source": "ASCE 41 Table 11-1",
            "phi_source": "ACI 530", "paragraph": "6-1, 6-2",
            "printed_page": "71", "pdf_page": 86}


def masonry_alternate_path_modeling_source():
    """Section 6-4.2: masonry Alternate Path modeling parameters,
    nonlinear acceptance criteria, and linear m-factors are the
    Life-Safety values from ASCE 41 Chapter 11 for primary and secondary
    components -- NOT reprinted in this UFC (printed p. 71).

    Returns
    -------
    dict
        {'source': 'ASCE 41 Chapter 11, Life Safety',
         'paragraph': '6-4.2', 'printed_page': '71', 'pdf_page': 86}
    """
    return {"source": "ASCE 41 Chapter 11, Life Safety", "paragraph": "6-4.2",
            "printed_page": "71", "pdf_page": 86}


# ============================================================================
# Chapter 7 -- Wood (printed pp. 73-74, pdf_page 88-89)
# ============================================================================

def wood_time_effect_factor():
    """Section 7-3: the wood time-effect factor lambda, used (per Section
    3-1.2/3-2.7) in addition to the ASCE 41 Chapter 12 default expected-
    strength values, for both Tie Force and Alternate Path design (printed
    p. 73). Per Appendix C-10.1, this reflects a deliberate choice between
    the permanent-dead-load value (0.6) and the impact-load value (1.25),
    since post-damage stability need only persist long enough for rescue/
    shoring, not permanently.

    Returns
    -------
    dict
        {'lambda': 1.0, 'paragraph': '7-3', 'printed_page': '73',
         'pdf_page': 88}
    """
    return {"lambda": 1.0, "paragraph": "7-3", "printed_page": "73", "pdf_page": 88}


def wood_default_lower_bound_factor():
    """Section 7-1: when default LOWER-BOUND strength values are needed
    for wood (default strengths from AF&PA/ASCE 16 and ASCE 41 are
    otherwise expected-strength values), multiply the expected-strength
    value by 0.85 (printed p. 73).

    Returns
    -------
    dict
        {'lower_bound_factor': 0.85, 'paragraph': '7-1', 'printed_page': '73',
         'pdf_page': 88}
    """
    return {"lower_bound_factor": 0.85, "paragraph": "7-1", "printed_page": "73",
            "pdf_page": 88}


def wood_material_code_references():
    """Section 7-2: wood strength reduction factor Phi is NOT reprinted
    in this UFC -- apply the ANSI/AF&PA National Design Specification
    (NDS) for Wood Construction, for the component/behavior under
    consideration (printed p. 73).

    Returns
    -------
    dict
        {'phi_source': 'ANSI/AF&PA NDS for Wood Construction',
         'paragraph': '7-2', 'printed_page': '73', 'pdf_page': 88}
    """
    return {"phi_source": "ANSI/AF&PA NDS for Wood Construction",
            "paragraph": "7-2", "printed_page": "73", "pdf_page": 88}


def wood_alternate_path_modeling_source():
    """Section 7-5.2: wood Alternate Path modeling parameters, nonlinear
    acceptance criteria, and linear m-factors are the Life-Safety values
    from ASCE 41 Chapter 12 for primary and secondary components -- NOT
    reprinted in this UFC (printed p. 74).

    Returns
    -------
    dict
        {'source': 'ASCE 41 Chapter 12, Life Safety', 'paragraph': '7-5.2',
         'printed_page': '74', 'pdf_page': 89}
    """
    return {"source": "ASCE 41 Chapter 12, Life Safety", "paragraph": "7-5.2",
            "printed_page": "74", "pdf_page": 89}


# ============================================================================
# Chapter 8 -- Cold-Formed Steel (printed pp. 75-76, pdf_page 90-91)
# ============================================================================

def cold_formed_steel_default_lower_bound_factor():
    """Section 8-1: when default LOWER-BOUND strength values are needed
    for cold-formed steel light-metal-framing shear walls (ASCE 41
    defaults are otherwise expected-strength values), multiply the
    expected-strength value by 0.85 -- the SAME rule and factor as wood,
    Section 7-1 (printed p. 75).

    Returns
    -------
    dict
        {'lower_bound_factor': 0.85, 'paragraph': '8-1', 'printed_page': '75',
         'pdf_page': 90}
    """
    return {"lower_bound_factor": 0.85, "paragraph": "8-1", "printed_page": "75",
            "pdf_page": 90}


def cold_formed_steel_material_code_references():
    """Section 8-2: cold-formed steel strength reduction factor Phi is
    NOT reprinted in this UFC -- apply the AISI/COS/NASPEC North American
    Specification for the Design of Cold-Formed Steel Structural Members
    (printed p. 75).

    Returns
    -------
    dict
        {'phi_source': 'AISI/COS/NASPEC North American Specification',
         'paragraph': '8-2', 'printed_page': '75', 'pdf_page': 90}
    """
    return {"phi_source": "AISI/COS/NASPEC North American Specification",
            "paragraph": "8-2", "printed_page": "75", "pdf_page": 90}


def cold_formed_steel_alternate_path_modeling_source():
    """Section 8-4.2: cold-formed steel Alternate Path modeling
    parameters, nonlinear acceptance criteria, and linear m-factors are
    the Life-Safety values from ASCE 41 Chapter 12 for primary and
    secondary components -- NOT reprinted in this UFC (printed p. 75).

    Returns
    -------
    dict
        {'source': 'ASCE 41 Chapter 12, Life Safety', 'paragraph': '8-4.2',
         'printed_page': '75', 'pdf_page': 90}
    """
    return {"source": "ASCE 41 Chapter 12, Life Safety", "paragraph": "8-4.2",
            "printed_page": "75", "pdf_page": 90}
