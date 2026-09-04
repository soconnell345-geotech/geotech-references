"""UFC 4-023-03 Chapters 1-2 -- Applicability, Risk Category, and Design
Requirements (printed pp. 1-11, pdf_page 16-26).

Chapter 1 sets the story-count threshold (mandatory for new construction
of 3+ stories) and defines what counts as a "story". Chapter 2 assigns a
progressive-collapse Risk Category (RC I-IV, Table 2-1) from the RC
already assigned under UFC 3-301-01, then maps RC to the required
combination of Tie Forces (TF), Alternate Path (AP), and Enhanced Local
Resistance (ELR) (Table 2-2).
"""


# ============================================================================
# Section 1-2 -- Applicability, Story Threshold (printed pp. 1-2,
# pdf_page 16-17)
# ============================================================================

def story_count_threshold():
    """Section 1-2: this UFC's requirements are MANDATORY for all new
    construction of 3 or more stories; for existing buildings, application
    is at the discretion of the project proponent or AHJ (printed p. 1).

    Returns
    -------
    dict
        {'minimum_stories': 3, 'new_construction_mandatory': True,
         'existing_construction_mandatory': False, 'paragraph': '1-2',
         'printed_page': '1', 'pdf_page': 16}
    """
    return {"minimum_stories": 3, "new_construction_mandatory": True,
            "existing_construction_mandatory": False, "paragraph": "1-2",
            "printed_page": "1", "pdf_page": 16}


def is_story(has_human_occupancy_egress_light_ventilation):
    """Section 1-2.1: a penthouse or below-grade level counts as a "story"
    (toward the 3-story threshold) only if it is designed for human
    occupancy AND equipped with means of egress, light, and ventilation
    meeting local code (printed p. 1). An unoccupied level (mechanical
    equipment, storage) is OMITTED from the story count.

    Parameters
    ----------
    has_human_occupancy_egress_light_ventilation : bool
        True if the level is designed for human occupancy with the
        listed life-safety features.

    Returns
    -------
    dict
        {'counts_as_story' (bool), 'paragraph': '1-2.1', 'printed_page': '1',
         'pdf_page': 16}
    """
    return {"counts_as_story": bool(has_human_occupancy_egress_light_ventilation),
            "paragraph": "1-2.1", "printed_page": "1", "pdf_page": 16}


def partial_occupancy_threshold():
    """Section 1-2.2: when DoD personnel occupy 25% or more of the net
    interior usable space, this UFC's requirements apply to the ENTIRE
    structure -- not just the DoD-occupied portion -- superseding the
    per-portion rule in UFC 4-010-01 (printed p. 1-2).

    Returns
    -------
    dict
        {'occupancy_threshold_pct': 25, 'applies_to': 'entire structure',
         'paragraph': '1-2.2', 'printed_page': '1-2', 'pdf_page': '16-17'}
    """
    return {"occupancy_threshold_pct": 25, "applies_to": "entire structure",
            "paragraph": "1-2.2", "printed_page": "1-2", "pdf_page": "16-17"}


# ============================================================================
# Table 2-1 -- Risk Categories (printed p. 7, pdf_page 22)
# ============================================================================

TABLE_2_1_RISK_CATEGORY = {
    "I": {
        "nature_of_occupancy": (
            "Buildings in Risk Category I per Table 2-2 of UFC 3-301-01, "
            "or low-occupancy buildings (per UFC 4-010-01)."
        ),
    },
    "II": {
        "nature_of_occupancy": (
            "Buildings in Risk Category II per Table 2-2 of UFC 3-301-01, "
            "or inhabited buildings with fewer than 50 personnel, primary "
            "gathering buildings, billeting, and high-occupancy family "
            "housing (per UFC 4-010-01). Risk Category II is the minimum "
            "for these occupancies -- population or function may require "
            "designation as RC III, IV, or V. IBC Section 1604.5.1 "
            "(multiple occupancies, incl. structurally separated "
            "structures) applies to the RC determination."
        ),
    },
    "III": {
        "nature_of_occupancy": "Buildings in Risk Category III per Table 2-2 of UFC 3-301-01.",
    },
    "IV": {
        "nature_of_occupancy": (
            "Buildings in Risk Category IV OR Risk Category V per Table "
            "2-2 of UFC 3-301-01 (both map to progressive-collapse RC IV)."
        ),
    },
}


def table_2_1_risk_category(risk_category):
    """Table 2-1: progressive-collapse Risk Category (RC I-IV) and its
    corresponding UFC 3-301-01 nature-of-occupancy description (printed
    p. 7). Note: UFC 3-301-01 Risk Categories IV AND V both map to
    progressive-collapse RC IV -- there is no progressive-collapse RC V.

    Parameters
    ----------
    risk_category : str
        'I', 'II', 'III', or 'IV'.

    Returns
    -------
    dict
        The row data plus {'risk_category', 'table': '2-1',
        'printed_page': '7', 'pdf_page': 22}.
    """
    key = str(risk_category).upper().strip()
    if key not in TABLE_2_1_RISK_CATEGORY:
        raise ValueError(f"risk_category must be one of I/II/III/IV, got {risk_category!r}")
    row = dict(TABLE_2_1_RISK_CATEGORY[key])
    row.update({"risk_category": key, "table": "2-1", "printed_page": "7", "pdf_page": 22})
    return row


# ============================================================================
# Table 2-2 -- Risk Categories and Design Requirements (printed p. 8,
# pdf_page 23)
# ============================================================================

TABLE_2_2_DESIGN_REQUIREMENTS = {
    "I": {
        "requirement": "No specific requirements.",
        "methods": [],
    },
    "II": {
        "requirement": (
            "Option 1: Tie Forces (TF) for the entire structure and "
            "Enhanced Local Resistance (ELR) for the corner and "
            "penultimate columns or walls at the first story. OR "
            "Option 2: Alternate Path (AP) for specified column and wall "
            "removal locations."
        ),
        "methods": [["TF", "ELR"], ["AP"]],
    },
    "III": {
        "requirement": (
            "Alternate Path for specified column and wall removal "
            "locations and Enhanced Local Resistance for all perimeter "
            "first story columns or walls."
        ),
        "methods": [["AP", "ELR"]],
    },
    "IV": {
        "requirement": (
            "Tie Forces and Alternate Path for specified column and wall "
            "removal locations and Enhanced Local Resistance for all "
            "perimeter first story columns or walls. (Footnote A: for "
            "buildings in UFC 3-301-01 Risk Category IV, the minimum "
            "structural requirements for Tie Force application in "
            "Section 3-1.1 may be exempted; for Risk Category V, those "
            "minimum structural requirements remain mandatory.)"
        ),
        "methods": [["TF", "AP", "ELR"]],
    },
}


def table_2_2_design_requirements(risk_category):
    """Table 2-2: the progressive-collapse design requirement (Tie Forces
    / Alternate Path / Enhanced Local Resistance combination) for a given
    Risk Category (printed p. 8).

    Parameters
    ----------
    risk_category : str
        'I', 'II', 'III', or 'IV'.

    Returns
    -------
    dict
        {'requirement' (narrative text), 'methods' (list of alternative
        method-combination lists, e.g. [['TF','ELR'], ['AP']] for RC II's
        two options), 'risk_category', 'table': '2-2', 'printed_page': '8',
        'pdf_page': 23}
    """
    key = str(risk_category).upper().strip()
    if key not in TABLE_2_2_DESIGN_REQUIREMENTS:
        raise ValueError(f"risk_category must be one of I/II/III/IV, got {risk_category!r}")
    row = dict(TABLE_2_2_DESIGN_REQUIREMENTS[key])
    row.update({"risk_category": key, "table": "2-2", "printed_page": "8", "pdf_page": 23})
    return row


def rc4_tie_force_minimum_exempt(ufc_3_301_01_risk_category):
    """Table 2-2 Footnote A: for progressive-collapse RC IV buildings that
    are UFC 3-301-01 Risk Category IV, the Tie Force minimum structural
    requirements (Section 3-1.1: bay-count/wall-length checks) MAY be
    exempted. For UFC 3-301-01 Risk Category V buildings (also mapped to
    progressive-collapse RC IV per Table 2-1), those minimum requirements
    REMAIN mandatory (printed p. 8; restated Section 2-2.4.1, printed
    pp. 10-11).

    Parameters
    ----------
    ufc_3_301_01_risk_category : str
        'IV' or 'V' (the structure's UNDERLYING UFC 3-301-01 Risk
        Category, not the progressive-collapse RC).

    Returns
    -------
    dict
        {'minimum_requirements_may_be_exempted' (bool),
         'ufc_3_301_01_risk_category', 'footnote': 'A, Table 2-2',
         'printed_page': '8', 'pdf_page': 23}
    """
    key = str(ufc_3_301_01_risk_category).upper().strip()
    if key not in ("IV", "V"):
        raise ValueError("ufc_3_301_01_risk_category must be 'IV' or 'V'")
    return {"minimum_requirements_may_be_exempted": key == "IV",
            "ufc_3_301_01_risk_category": key, "footnote": "A, Table 2-2",
            "printed_page": "8", "pdf_page": 23}
