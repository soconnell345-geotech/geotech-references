"""UFC 4-023-03 Section 3-3 -- Enhanced Local Resistance (printed pp. 56-59,
pdf_page 71-74).

Enhanced Local Resistance (ELR) is an indirect design approach applied to
perimeter columns/walls (and their connections) so that shear failure
cannot precede full flexural hinging -- i.e. a ductile failure mechanism
forms if the element is loaded laterally to failure. Required for RC II
Option 1 (corner + penultimate, first story), RC III (all perimeter, first
story), and RC IV (all perimeter, first story, with an added flexural
demand multiplier).

Validated against Appendix D's worked ELR check for a 7-story RC corner
column (printed pp. 129-131): the pinned-fixed shear-demand equation
(Eq D-1) reproduces Vu = 367-kip from Mn = 783-ft-kip and L = 16-ft.
"""


# ============================================================================
# Equation 3-20 -- ELR LRFD Check (printed p. 56, pdf_page 71)
# ============================================================================

def elr_lrfd_check(rn, ru):
    """Equation 3-20: ELR design-strength adequacy check (printed p. 56).
    Phi is always 1.0 for ELR (Section 3-3.1) and expected material
    strengths are used throughout, so this reduces to Rn >= Ru.

        Phi*Rn >= Ru,  Phi = 1.0

    Parameters
    ----------
    rn : float
        Nominal strength using expected material strength and appropriate
        over-strength factors (Phi=1.0 baked in per Section 3-3.1).
    ru : float
        Required strength (shear or flexural demand).

    Returns
    -------
    dict
        {'design_strength' (=rn), 'ru', 'adequate' (bool),
         'equation': '3-20', 'printed_page': '56', 'pdf_page': 71}
    """
    return {"design_strength": rn, "ru": ru, "adequate": rn >= ru,
            "equation": "3-20", "printed_page": "56", "pdf_page": 71}


# ============================================================================
# Equation D-1 -- Shear Demand from a Pinned-Fixed Column Mechanism
# (Appendix D, printed p. 129, pdf_page 144)
# ============================================================================

def shear_demand_pinned_fixed_column(mn, l):
    """Equation D-1 (Appendix D, printed p. 129): the ELR shear demand for
    a column considered pinned at its base and fixed (via floor-diaphragm
    continuity) at the first level above grade, developing a three-hinge
    mechanism (one hinge at the pin, one at the fixed end, one within the
    column). Derived from PDC TR-06-01 Table 4-4: the largest reaction for
    a pinned-fixed, uniformly loaded beam is Vu = 5*ru*L/8 with
    ru = 12*Mn/L^2, which rearranges to:

        Vu = 7.5 * Mn / L

    Reproduces the Appendix D worked example: Mn=783-ft-kip, L=16-ft ->
    Vu=367-kip.

    Parameters
    ----------
    mn : float
        Nominal flexural strength of the column cross-section, accounting
        for coexisting axial load (ft-kip or kN-m). In no case should the
        governing Mn be less than that with zero axial load (Section
        3-3.1.2).
    l : float
        Column clear height (ft or m).

    Returns
    -------
    dict
        {'vu', 'mn', 'l', 'equation': 'D-1', 'printed_page': '129',
         'pdf_page': 144}
    """
    vu = 7.5 * mn / l
    return {"vu": vu, "mn": mn, "l": l, "equation": "D-1",
            "printed_page": "129", "pdf_page": 144}


# ============================================================================
# Section 3-3.5.1 -- RC IV Flexural Demand Multipliers (printed p. 58-59,
# pdf_page 73-74)
# ============================================================================

def rc4_column_flexural_demand(baseline_gravity_only_mn, current_design_mn):
    """Section 3-3.5.1: for RC IV columns, the ELR flexural demand is the
    LARGER of (1) the baseline gravity-only-design nominal flexural
    strength multiplied by 2.0, and (2) the current (all-loads) design's
    nominal flexural strength (printed pp. 58-59). If condition 1
    governs, the column must be redesigned to meet it.

    Parameters
    ----------
    baseline_gravity_only_mn : float
        Nominal flexural strength of the column when designed for gravity
        loads only, after the AP procedure is applied.
    current_design_mn : float
        Nominal flexural strength of the column as designed for all
        applicable loads (wind, seismic, gravity, etc.) after AP.

    Returns
    -------
    dict
        {'flexural_demand', 'governing_condition' (1 or 2),
         'baseline_x2', 'current_design_mn', 'paragraph': '3-3.5.1',
         'printed_page': '58-59', 'pdf_page': '73-74'}
    """
    baseline_x2 = 2.0 * baseline_gravity_only_mn
    governing = 1 if baseline_x2 >= current_design_mn else 2
    return {
        "flexural_demand": max(baseline_x2, current_design_mn),
        "governing_condition": governing, "baseline_x2": baseline_x2,
        "current_design_mn": current_design_mn, "paragraph": "3-3.5.1",
        "printed_page": "58-59", "pdf_page": "73-74",
    }


def rc4_wall_flexural_demand(baseline_gravity_only_mn, current_design_mn):
    """Section 3-3.5.1: for RC IV load-bearing walls, the ELR flexural
    demand is the LARGER of (1) the baseline gravity-only-design nominal
    flexural strength multiplied by 1.5, and (2) the current (all-loads)
    design's nominal flexural strength (printed p. 59).

    Parameters
    ----------
    baseline_gravity_only_mn : float
        Nominal flexural strength of the wall when designed for gravity
        loads only, after the AP procedure is applied.
    current_design_mn : float
        Nominal flexural strength of the wall as designed for all
        applicable loads after AP.

    Returns
    -------
    dict
        {'flexural_demand', 'governing_condition' (1 or 2),
         'baseline_x1_5', 'current_design_mn', 'paragraph': '3-3.5.1',
         'printed_page': '59', 'pdf_page': 74}
    """
    baseline_x1_5 = 1.5 * baseline_gravity_only_mn
    governing = 1 if baseline_x1_5 >= current_design_mn else 2
    return {
        "flexural_demand": max(baseline_x1_5, current_design_mn),
        "governing_condition": governing, "baseline_x1_5": baseline_x1_5,
        "current_design_mn": current_design_mn, "paragraph": "3-3.5.1",
        "printed_page": "59", "pdf_page": 74,
    }


# ============================================================================
# Section 3-3.6 -- Rebound Reaction Force (printed p. 59, pdf_page 74)
# ============================================================================

def rebound_reaction_force(inbound_reaction_force):
    """Section 3-3.6: connections at the top and bottom of ELR columns/
    walls must be designed for a rebound reaction force equal to 50% of
    the inbound value, to resist the initial-inbound-then-rebound dynamic
    loading (printed p. 59).

    Parameters
    ----------
    inbound_reaction_force : float
        Design reaction force for the inbound (loading) phase (kip or kN).

    Returns
    -------
    dict
        {'rebound_force', 'inbound_reaction_force', 'factor': 0.5,
         'paragraph': '3-3.6', 'printed_page': '59', 'pdf_page': 74}
    """
    return {"rebound_force": 0.5 * inbound_reaction_force,
            "inbound_reaction_force": inbound_reaction_force, "factor": 0.5,
            "paragraph": "3-3.6", "printed_page": "59", "pdf_page": 74}


# ============================================================================
# Section 3-3.2 -- ELR Location and Extent Requirements
# (printed pp. 57-58, pdf_page 72-73)
# ============================================================================

_ELR_LOCATIONS = {
    ("II", None): {
        "framed_or_two_way": "perimeter corner and penultimate columns/walls, first story above grade",
        "one_way_wall": "entire length of the end wall and penultimate wall (first story)",
    },
    ("III", None): {
        "framed_or_two_way": "all perimeter columns/walls, first story above grade",
        "one_way_wall": "entire length of the end wall and penultimate wall (first story)",
    },
    ("IV", None): {
        "framed_or_two_way": "all perimeter columns/walls, first story above grade",
        "one_way_wall": "entire length of the end wall and penultimate wall (first story)",
    },
}


def elr_location_requirement(risk_category, one_way_wall=False):
    """Section 3-3.2: identifies where Enhanced Local Resistance must be
    applied for a given Risk Category (printed pp. 57-58). RC II ELR
    applies only under Option 1 (Tie Force + ELR); RC III and RC IV both
    require ELR at ALL perimeter first-story columns/walls (RC III via
    the Alternate Path option; RC IV in addition to Tie Force + AP).

    Parameters
    ----------
    risk_category : str
        'II', 'III', or 'IV' (ELR is not applicable to RC I; RC II Option
        2 does not require ELR at all -- see ``applicability`` module).
    one_way_wall : bool, optional
        True for a one-way load-bearing wall building. Default False
        (framed or two-way load-bearing wall).

    Returns
    -------
    dict
        {'location', 'risk_category', 'paragraph': '3-3.2', 'printed_page':
         '57-58', 'pdf_page': '72-73'}
    """
    key = (str(risk_category).upper().strip(), None)
    if key not in _ELR_LOCATIONS:
        raise ValueError(f"risk_category must be 'II', 'III', or 'IV', got {risk_category!r}")
    row = _ELR_LOCATIONS[key]
    location = row["one_way_wall"] if one_way_wall else row["framed_or_two_way"]
    return {"location": location, "risk_category": key[0], "paragraph": "3-3.2",
            "printed_page": "57-58", "pdf_page": "72-73"}
