"""UFC 4-023-03 Section 3-2 -- Alternate Path Method (printed pp. 28-56,
pdf_page 43-71).

The Alternate Path (AP) method notionally removes a vertical load-bearing
element (column or wall section) and demonstrates, by LRFD-style analysis,
that the structure can bridge over the resulting gap. Three analysis
procedures are permitted: Linear Static (LSP), Nonlinear Static (NSP), and
Nonlinear Dynamic (NDP), all adapted from ASCE 41. This module implements
the general (material-independent) load combinations, load/dynamic
increase factors (Tables 3-4 and 3-5), removal-location/extent rules
(Section 3-2.9), and acceptance-criteria checks (Equations 3-9, 3-13,
3-14, 3-17, 3-19). Material-specific m-factors and modeling parameters are
in ``reinforced_concrete.py`` and ``structural_steel.py``.

Validated against the structural-steel worked example, Appendix E Table
E-3 (printed p. 138): mLIF=1.8 -> ΩLD=2.72; mLIF=1.79 -> ΩLD=2.71
(``table_3_4_load_increase_factor``, steel/framed).
"""


# ============================================================================
# Equation 3-8 (and identically-formed 3-20) -- General LRFD Check
# (printed p. 29, pdf_page 44)
# ============================================================================

def lrfd_strength_check(phi, rn, ru):
    """Equation 3-8: general LRFD design-strength adequacy check used
    throughout the Alternate Path method (printed p. 29).

        Phi*Rn >= Ru

    Parameters
    ----------
    phi : float
        Strength reduction factor from the applicable material code.
    rn : float
        Nominal strength (expected strength QCE for deformation-controlled
        actions, or lower-bound strength QCL for force-controlled
        actions -- see ``deformation_controlled_capacity_check`` and
        ``force_controlled_capacity_check`` for the m-factor and QCL forms).
    ru : float
        Required strength (Sum gamma_i * Q_i).

    Returns
    -------
    dict
        {'design_strength', 'ru', 'adequate' (bool), 'equation': '3-8',
         'printed_page': '29', 'pdf_page': 44}
    """
    design_strength = phi * rn
    return {"design_strength": design_strength, "ru": ru,
            "adequate": design_strength >= ru, "equation": "3-8",
            "printed_page": "29", "pdf_page": 44}


# ============================================================================
# Section 3-2.9 -- Removal of Load-Bearing Elements (printed pp. 35-41,
# pdf_page 50-56)
# ============================================================================

def removed_column_extent(clear_height_between_lateral_restraints):
    """Section 3-2.9.1: for ANY column removal case (RC II Option 1
    deficient tie, or RC II Option 2/III/IV prescribed removal), the
    removed extent is the full clear height between lateral restraints
    (printed p. 36).

    Parameters
    ----------
    clear_height_between_lateral_restraints : float
        Clear column height between lateral restraints (ft or m).

    Returns
    -------
    dict
        {'removed_height', 'paragraph': '3-2.9.1', 'printed_page': '36',
         'pdf_page': 51}
    """
    return {"removed_height": clear_height_between_lateral_restraints,
            "paragraph": "3-2.9.1", "printed_page": "36", "pdf_page": 51}


def removed_wall_extent(clear_story_height, deficient_wall_length=None,
                         option="prescribed"):
    """Section 3-2.9.1: removed load-bearing-wall length (printed p. 36).

    For a PRESCRIBED removal (RC II Option 2, RC III, RC IV -- Section
    3-2.9.1.2): remove a length of 2*H (H = clear story height) at every
    minimum removal location.

    For a DEFICIENT-VERTICAL-TIE removal (RC II Option 1 -- Section
    3-2.9.1.1): remove 2*H if the deficient wall length exceeds 2*H,
    otherwise remove just the deficient portion.

    Parameters
    ----------
    clear_story_height : float
        Clear story height, H (ft or m).
    deficient_wall_length : float, optional
        Length of the wall segment found deficient in vertical tie
        strength. Required when option='deficient_tie'.
    option : str, optional
        'prescribed' (default, RC II Opt 2/III/IV minimum locations) or
        'deficient_tie' (RC II Option 1).

    Returns
    -------
    dict
        {'removed_length', 'basis', 'paragraph': '3-2.9.1',
         'printed_page': '36', 'pdf_page': 51}
    """
    two_h = 2 * clear_story_height
    if option == "deficient_tie":
        if deficient_wall_length is None:
            raise ValueError("deficient_wall_length is required for option='deficient_tie'")
        length = two_h if deficient_wall_length > two_h else deficient_wall_length
        basis = "2H (deficient length > 2H)" if deficient_wall_length > two_h else "full deficient length (<= 2H)"
    elif option == "prescribed":
        length = two_h
        basis = "2H (prescribed minimum removal location)"
    else:
        raise ValueError("option must be 'prescribed' or 'deficient_tie'")
    return {"removed_length": length, "basis": basis, "paragraph": "3-2.9.1",
            "printed_page": "36", "pdf_page": 51}


def required_removal_stories():
    """Section 3-2.9.2.2/3-2.9.2.4: for each PLAN location of a prescribed
    column or external-wall removal (RC II Option 2, RC III, RC IV),
    perform an AP analysis for each of these stories (printed pp. 36-38):

    1. First story above grade
    2. Story directly below the roof
    3. Story at mid-height
    4. Story above a column splice / change in column (or wall) size

    Returns
    -------
    dict
        {'stories' (list of str), 'paragraph': '3-2.9.2.2 / 3-2.9.2.4',
         'printed_page': '36-38', 'pdf_page': '51-53'}
    """
    return {
        "stories": [
            "first story above grade", "story directly below roof",
            "story at mid-height",
            "story above the location of a column/wall-size change or splice",
        ],
        "paragraph": "3-2.9.2.2 / 3-2.9.2.4", "printed_page": "36-38",
        "pdf_page": "51-53",
    }


def adjacent_element_removal_trigger(distance, reference_dimension):
    """Section 3-2.9.2.2/3-2.9.2.3 (columns) and 3-2.9.2.4/3-2.9.2.5
    (walls): if another load-bearing element is within 30% of the
    reference dimension from the primary removal location, it must be
    removed SIMULTANEOUSLY (printed pp. 37-41). The reference dimension is
    the largest bay dimension for column removals, or the clear story
    height H for wall removals.

    Parameters
    ----------
    distance : float
        Distance from the primary removal location to the other element
        (ft or m).
    reference_dimension : float
        Largest associated bay dimension (columns) or clear story height H
        (walls), same units as *distance*.

    Returns
    -------
    dict
        {'triggers_simultaneous_removal' (bool), 'threshold_distance',
         'paragraph': '3-2.9.2.2', 'printed_page': '37-41', 'pdf_page': '52-56'}
    """
    threshold = 0.30 * reference_dimension
    return {
        "triggers_simultaneous_removal": distance <= threshold,
        "threshold_distance": threshold, "paragraph": "3-2.9.2.2",
        "printed_page": "37-41", "pdf_page": "52-56",
    }


# ============================================================================
# Section 3-2.11.1.1 -- Irregularity Limitations for LSP use
# (printed p. 42, pdf_page 57)
# ============================================================================

def irregularity_check(has_discontinuity=False, has_asymmetric_bay_stiffness=False,
                        has_asymmetric_wall_stiffness=False, has_nonorthogonal_lateral_elements=False):
    """Section 3-2.11.1.1: a structure is IRREGULAR (restricting Linear
    Static Procedure use, see ``lsp_applicable``) if ANY of the four
    printed conditions is true (printed p. 42):

    1. Significant discontinuities in gravity/lateral systems (out-of-
       plane offsets of primary vertical elements, transfer girders).
       Stepped-back stories are NOT an irregularity.
    2. At an exterior column (except corners), bay stiffness/strength
       ratio from one side to the other <50%, at any story.
    3. For exterior load-bearing walls (except corners), wall stiffness/
       strength ratio from one side of an intersecting wall to the
       other <50%, at any story.
    4. Vertical lateral-load-resisting elements not parallel to the major
       orthogonal axes (skewed/curved frames or walls).

    Parameters
    ----------
    has_discontinuity, has_asymmetric_bay_stiffness,
    has_asymmetric_wall_stiffness, has_nonorthogonal_lateral_elements : bool
        Each corresponds to one printed condition above.

    Returns
    -------
    dict
        {'is_irregular' (bool), 'triggered_conditions' (list of int),
         'paragraph': '3-2.11.1.1', 'printed_page': '42', 'pdf_page': 57}
    """
    flags = [has_discontinuity, has_asymmetric_bay_stiffness,
             has_asymmetric_wall_stiffness, has_nonorthogonal_lateral_elements]
    triggered = [i + 1 for i, f in enumerate(flags) if f]
    return {"is_irregular": any(flags), "triggered_conditions": triggered,
            "paragraph": "3-2.11.1.1", "printed_page": "42", "pdf_page": 57}


def lsp_applicable(is_irregular, max_dcr=None):
    """Section 3-2.11.1: determines whether the Linear Static Procedure
    (LSP) may be used (printed p. 41).

    Regular structure: LSP always permitted (no DCR check needed).
    Irregular structure: LSP permitted only if every component DCR
    (``dcr``) is <= 2.0; if any DCR > 2.0, LSP cannot be used (NSP or NDP
    required).

    Parameters
    ----------
    is_irregular : bool
        From ``irregularity_check``.
    max_dcr : float, optional
        Largest component DCR in the structure (required if irregular).

    Returns
    -------
    dict
        {'lsp_permitted' (bool), 'reason', 'paragraph': '3-2.11.1',
         'printed_page': '41', 'pdf_page': 56}
    """
    if not is_irregular:
        return {"lsp_permitted": True, "reason": "structure is regular",
                "paragraph": "3-2.11.1", "printed_page": "41", "pdf_page": 56}
    if max_dcr is None:
        raise ValueError("max_dcr is required when is_irregular=True")
    permitted = max_dcr <= 2.0
    reason = f"irregular structure, max DCR={max_dcr} ({'<=' if permitted else '>'} 2.0)"
    return {"lsp_permitted": permitted, "reason": reason, "paragraph": "3-2.11.1",
            "printed_page": "41", "pdf_page": 56}


def dcr(q_udlim, q_ce):
    """Equation 3-9: Demand-Capacity Ratio, used only to determine LSP
    applicability for an irregular structure (printed p. 42).

        DCR = QUDLim / QCE

    Parameters
    ----------
    q_udlim : float
        Deformation-controlled action from a linear model with gravity
        dead/live loads increased by the Omega_LD load increase factor
        (Section 3-2.11.1.2).
    q_ce : float
        Expected strength of the component (Chapters 4-8).

    Returns
    -------
    dict
        {'dcr', 'equation': '3-9', 'printed_page': '42', 'pdf_page': 57}
    """
    return {"dcr": q_udlim / q_ce, "equation": "3-9", "printed_page": "42",
            "pdf_page": 57}


# ============================================================================
# Section 3-2.11.4 -- LSP Load Cases, Equations 3-10, 3-11, 3-12
# (printed pp. 44-45, pdf_page 59-60)
# ============================================================================

def _gravity_load_extreme_event(d, l=0.0, s=0.0):
    """Common ASCE-7-extraordinary-event gravity combination used (with
    different multipliers) throughout the AP method: 1.2D + (0.5L or
    0.2S). Internal helper; L and S are not combined -- pass whichever
    governs (live or snow) as *l* or *s*, not both nonzero, per the
    printed equations.
    """
    return 1.2 * d + 0.5 * l + 0.2 * s


def deformation_controlled_load_lsp(omega_ld, d, l=0.0, s=0.0):
    """Equation 3-10: increased gravity load for DEFORMATION-controlled
    actions, applied to bays immediately adjacent to and above the
    removed element (printed p. 44).

        GLD = Omega_LD * [1.2 D + (0.5 L or 0.2 S)]

    Parameters
    ----------
    omega_ld : float
        Load increase factor for deformation-controlled actions, from
        ``table_3_4_load_increase_factor``.
    d : float
        Dead load including facade loads (lb/ft2 or kN/m2).
    l : float, optional
        Live load including live-load reduction (lb/ft2 or kN/m2).
        Default 0.
    s : float, optional
        Snow load (lb/ft2 or kN/m2). Default 0. Use L or S, not both.

    Returns
    -------
    dict
        {'gld', 'omega_ld', 'd', 'l', 's', 'equation': '3-10',
         'printed_page': '44', 'pdf_page': 59}
    """
    gld = omega_ld * _gravity_load_extreme_event(d, l, s)
    return {"gld": gld, "omega_ld": omega_ld, "d": d, "l": l, "s": s,
            "equation": "3-10", "printed_page": "44", "pdf_page": 59}


def gravity_load_away_from_removal(d, l=0.0, s=0.0):
    """Equations 3-11 (LSP), 3-16 (NSP) and identical-form 3-18 (NDP,
    applied to the whole structure): gravity load for bays NOT loaded
    with the increased (LIF/DIF) load (printed pp. 44-45, 51, 55).

        G = 1.2 D + (0.5 L or 0.2 S)

    Parameters
    ----------
    d, l, s : float
        Dead, live, and snow loads as in ``deformation_controlled_load_lsp``.

    Returns
    -------
    dict
        {'g', 'd', 'l', 's', 'equation': '3-11 / 3-16 / 3-18',
         'printed_page': '44-45, 51, 55', 'pdf_page': '59-60, 66, 70'}
    """
    g = _gravity_load_extreme_event(d, l, s)
    return {"g": g, "d": d, "l": l, "s": s, "equation": "3-11 / 3-16 / 3-18",
            "printed_page": "44-45, 51, 55", "pdf_page": "59-60, 66, 70"}


def force_controlled_load_lsp(omega_lf, d, l=0.0, s=0.0):
    """Equation 3-12: increased gravity load for FORCE-controlled actions
    in the LSP (printed p. 45).

        GLF = Omega_LF * [1.2 D + (0.5 L or 0.2 S)]

    Parameters
    ----------
    omega_lf : float
        Load increase factor for force-controlled actions (always 2.0 per
        Table 3-4).
    d, l, s : float
        Dead, live, and snow loads.

    Returns
    -------
    dict
        {'glf', 'omega_lf', 'd', 'l', 's', 'equation': '3-12',
         'printed_page': '45', 'pdf_page': 60}
    """
    glf = omega_lf * _gravity_load_extreme_event(d, l, s)
    return {"glf": glf, "omega_lf": omega_lf, "d": d, "l": l, "s": s,
            "equation": "3-12", "printed_page": "45", "pdf_page": 60}


def nonlinear_static_load(omega_n, d, l=0.0, s=0.0):
    """Equation 3-15: increased gravity load for the Nonlinear Static
    Procedure, both deformation- and force-controlled actions together
    (printed p. 51).

        GN = Omega_N * [1.2 D + (0.5 L or 0.2 S)]

    Parameters
    ----------
    omega_n : float
        Dynamic increase factor from ``table_3_5_dynamic_increase_factor``.
    d, l, s : float
        Dead, live, and snow loads.

    Returns
    -------
    dict
        {'gn', 'omega_n', 'd', 'l', 's', 'equation': '3-15',
         'printed_page': '51', 'pdf_page': 66}
    """
    gn = omega_n * _gravity_load_extreme_event(d, l, s)
    return {"gn": gn, "omega_n": omega_n, "d": d, "l": l, "s": s,
            "equation": "3-15", "printed_page": "51", "pdf_page": 66}


# ============================================================================
# Table 3-4 -- Load Increase Factors for Linear Static Analysis
# (printed p. 46, pdf_page 61)
# ============================================================================

_TABLE_3_4 = {
    ("steel", "framed"): {"omega_ld": lambda m: 0.9 * m + 1.1, "omega_lf": 2.0},
    ("reinforced_concrete", "framed"): {"omega_ld": lambda m: 1.2 * m + 0.80, "omega_lf": 2.0},
    ("reinforced_concrete", "load_bearing_wall"): {"omega_ld": lambda m: 2.0 * m, "omega_lf": 2.0},
    ("masonry", "load_bearing_wall"): {"omega_ld": lambda m: 2.0 * m, "omega_lf": 2.0},
    ("wood", "load_bearing_wall"): {"omega_ld": lambda m: 2.0 * m, "omega_lf": 2.0},
    ("cold_formed_steel", "load_bearing_wall"): {"omega_ld": lambda m: 2.0 * m, "omega_lf": 2.0},
}


def table_3_4_load_increase_factor(material, structure_type, m_lif):
    """Table 3-4: Linear Static load increase factors Omega_LD
    (deformation-controlled) and Omega_LF (force-controlled, always 2.0)
    (printed p. 46).

    mLIF is the SMALLEST m-factor of any primary beam, girder, spandrel,
    or wall element directly connected to the columns/walls directly
    above the removal location (columns themselves are excluded from the
    mLIF determination). For reinforced-concrete framed structures, per
    footnote A, beam-column joints are force-controlled but the
    Omega_LD calculation still uses the m-factor of the beam hinge that
    forms near the column.

    Validated against Appendix E Table E-3 (printed p. 138, steel/framed):
    mLIF=1.8 -> Omega_LD=0.9*1.8+1.1=2.72; mLIF=1.79 -> Omega_LD=2.711 (~2.71).

    Parameters
    ----------
    material : str
        'steel', 'reinforced_concrete', 'masonry', 'wood', or
        'cold_formed_steel'.
    structure_type : str
        'framed' (steel or reinforced_concrete only) or
        'load_bearing_wall'.
    m_lif : float
        Smallest primary-beam/girder/spandrel/wall m-factor per the
        definition above.

    Returns
    -------
    dict
        {'omega_ld', 'omega_lf', 'material', 'structure_type', 'm_lif',
         'table': '3-4', 'printed_page': '46', 'pdf_page': 61}
    """
    key = (material.lower().strip(), structure_type.lower().strip())
    if key not in _TABLE_3_4:
        raise ValueError(
            f"No Table 3-4 row for material={material!r}, structure_type={structure_type!r}; "
            f"valid combinations: {sorted(_TABLE_3_4)}"
        )
    row = _TABLE_3_4[key]
    return {
        "omega_ld": row["omega_ld"](m_lif), "omega_lf": row["omega_lf"],
        "material": key[0], "structure_type": key[1], "m_lif": m_lif,
        "table": "3-4", "printed_page": "46", "pdf_page": 61,
    }


# ============================================================================
# Table 3-5 -- Dynamic Increase Factors for Nonlinear Static Analysis
# (printed p. 52, pdf_page 67)
# ============================================================================

_TABLE_3_5 = {
    ("steel", "framed"): lambda r: 1.08 + 0.76 / (r + 0.83),
    ("reinforced_concrete", "framed"): lambda r: 1.04 + 0.45 / (r + 0.48),
    ("reinforced_concrete", "load_bearing_wall"): lambda r: 2.0,
    ("masonry", "load_bearing_wall"): lambda r: 2.0,
    ("wood", "load_bearing_wall"): lambda r: 2.0,
    ("cold_formed_steel", "load_bearing_wall"): lambda r: 2.0,
}


def table_3_5_dynamic_increase_factor(material, structure_type,
                                       theta_pra=None, theta_y=None):
    """Table 3-5: Nonlinear Static dynamic increase factor Omega_N
    (printed p. 52). For steel-framed and RC-framed structures, Omega_N
    is a function of the normalized rotation ratio theta_pra/theta_y
    (choose the SMALLEST such ratio for any primary element/connection
    within or touching the region loaded with the increased gravity load,
    Figures 3-13/3-14; columns excluded). Load-bearing-wall structures of
    any material, and this equation's derivation, are fixed at 2.0.

        Steel framed:                Omega_N = 1.08 + 0.76/(r + 0.83)
        Reinforced concrete framed:  Omega_N = 1.04 + 0.45/(r + 0.48)
        (r = theta_pra / theta_y)

    The steel equation reproduces Figure C-7's printed fit exactly
    (Appendix C, printed p. 106).

    Parameters
    ----------
    material : str
        'steel', 'reinforced_concrete', 'masonry', 'wood', or
        'cold_formed_steel'.
    structure_type : str
        'framed' or 'load_bearing_wall'.
    theta_pra : float, optional
        Plastic rotation angle acceptance-criteria limit (radians) for the
        governing primary element/connection. Required for framed steel
        or RC.
    theta_y : float, optional
        Yield rotation angle (radians) for the same element. Required for
        framed steel or RC.

    Returns
    -------
    dict
        {'omega_n', 'material', 'structure_type', 'rotation_ratio' (r, or
         None for load-bearing walls), 'table': '3-5', 'printed_page': '52',
         'pdf_page': 67}
    """
    key = (material.lower().strip(), structure_type.lower().strip())
    if key not in _TABLE_3_5:
        raise ValueError(
            f"No Table 3-5 row for material={material!r}, structure_type={structure_type!r}; "
            f"valid combinations: {sorted(_TABLE_3_5)}"
        )
    if key[1] == "framed":
        if theta_pra is None or theta_y is None:
            raise ValueError("theta_pra and theta_y are required for framed structures")
        r = theta_pra / theta_y
        omega_n = _TABLE_3_5[key](r)
    else:
        r = None
        omega_n = _TABLE_3_5[key](r)
    return {"omega_n": omega_n, "material": key[0], "structure_type": key[1],
            "rotation_ratio": r, "table": "3-5", "printed_page": "52", "pdf_page": 67}


# ============================================================================
# Acceptance Criteria -- Equations 3-13, 3-14, 3-17, 3-19
# (printed pp. 49, 53, 56, pdf_page 64, 68, 71)
# ============================================================================

def deformation_controlled_capacity_check(phi, m, q_ce, q_ud):
    """Equation 3-13: Linear Static Procedure acceptance check for
    deformation-controlled actions, all primary and secondary components
    (printed p. 49).

        Phi * m * QCE >= QUD

    Parameters
    ----------
    phi : float
        Strength reduction factor from the applicable material code.
    m : float
        Component/element m-factor (Chapters 4-8).
    q_ce : float
        Expected strength of the component for the deformation-controlled
        action.
    q_ud : float
        Deformation-controlled action from the Linear Static model.

    Returns
    -------
    dict
        {'capacity' (phi*m*q_ce), 'q_ud', 'adequate' (bool),
         'equation': '3-13', 'printed_page': '49', 'pdf_page': 64}
    """
    capacity = phi * m * q_ce
    return {"capacity": capacity, "q_ud": q_ud, "adequate": capacity >= q_ud,
            "equation": "3-13", "printed_page": "49", "pdf_page": 64}


def force_controlled_capacity_check(phi, q_cl, q_uf):
    """Equations 3-14 (LSP), 3-17 (NSP), 3-19 (NDP): acceptance check for
    force-controlled actions, all primary and secondary components,
    identical in form across all three procedures (printed pp. 49, 53, 56).

        Phi * QCL >= QUF

    Parameters
    ----------
    phi : float
        Strength reduction factor from the applicable material code.
    q_cl : float
        Lower-bound strength of the component for the force-controlled
        action.
    q_uf : float
        Force-controlled action from the analysis model (LSP, NSP, or
        NDP).

    Returns
    -------
    dict
        {'capacity' (phi*q_cl), 'q_uf', 'adequate' (bool),
         'equation': '3-14 / 3-17 / 3-19', 'printed_page': '49, 53, 56',
         'pdf_page': '64, 68, 71'}
    """
    capacity = phi * q_cl
    return {"capacity": capacity, "q_uf": q_uf, "adequate": capacity >= q_uf,
            "equation": "3-14 / 3-17 / 3-19", "printed_page": "49, 53, 56",
            "pdf_page": "64, 68, 71"}


# ============================================================================
# Section 3-2.5 -- Force- and Deformation-Controlled Action Classification
# (printed pp. 31-32, pdf_page 46-47)
# ============================================================================

def classify_action(curve_type, e_over_g, is_primary):
    """Section 3-2.5: classifies a component action as deformation- or
    force-controlled from its ASCE-41-style force-deformation curve type
    (Figure 3-7) and its e/g ratio (printed pp. 31-32). This is the
    UFC's OPERATIVE classification rule; Table 3-1 ("Examples of
    Deformation Controlled and Force-Controlled Actions, from ASCE 41",
    printed p. 33) is an illustrative example table reproduced from ASCE
    41 with a merged/bulleted layout that does not extract unambiguously
    -- consult the printed page directly for that table; classification
    should be performed with this function instead.

    Primary component: deformation-controlled if (Type 1 or Type 2 curve)
    AND e/g >= 2; force-controlled if (Type 1 or Type 2) AND e/g < 2, or
    if Type 3.

    Secondary component: deformation-controlled if Type 1 (any e/g), or
    Type 2 AND e/g >= 2; force-controlled if Type 2 AND e/g < 2, or Type 3.

    Parameters
    ----------
    curve_type : int
        1, 2, or 3 (ASCE 41 / Figure 3-7 force-deformation curve type).
    e_over_g : float
        Ratio of deformation e to g on the component's curve (Figure 3-7).
    is_primary : bool
        True for a primary component (see Section 3-2.4), False for
        secondary.

    Returns
    -------
    dict
        {'classification' ('deformation_controlled' or 'force_controlled'),
         'curve_type', 'e_over_g', 'is_primary', 'paragraph': '3-2.5',
         'printed_page': '31-32', 'pdf_page': '46-47'}
    """
    if curve_type not in (1, 2, 3):
        raise ValueError("curve_type must be 1, 2, or 3")
    if is_primary:
        deformation_controlled = curve_type in (1, 2) and e_over_g >= 2
    else:
        deformation_controlled = (curve_type == 1) or (curve_type == 2 and e_over_g >= 2)
    classification = "deformation_controlled" if deformation_controlled else "force_controlled"
    return {"classification": classification, "curve_type": curve_type,
            "e_over_g": e_over_g, "is_primary": is_primary,
            "paragraph": "3-2.5", "printed_page": "31-32", "pdf_page": "46-47"}
