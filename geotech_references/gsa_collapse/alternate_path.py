"""GSA Alternate Path Analysis and Design Guidelines Section 3.2 --
Alternate Path Method (printed pp. 7-31, pdf_page 19-43).

GSA's Alternate Path (AP) method is UFC 4-023-03 Section 3-2's method
"incorporated in its entirety" (Section 1.5) as the SOLE progressive-
collapse design procedure -- these Guidelines employ the Alternate Path
method only (Chapter 3 opening sentence). Section 3.1 (Tie Forces) and
Section 3.3 (Enhanced Local Resistance) are both REMOVED IN THEIR ENTIRETY
(see ``tie_forces_removed``/``enhanced_local_resistance_removed`` below);
Commentary C3.1 explains that GSA considered Tie Forces superfluous given
FSL V's whole-building removal scope and difficult to implement in
existing buildings.

This module implements the general (material-independent) LRFD check,
primary/secondary and force-/deformation-controlled classification
(IDENTICAL wording to UFC 4-023-03 Section 3-2.4/3-2.5), component
capacity tables (Tables 2 and 3, identical in form to UFC's Tables 2/3),
removal-location rules keyed to Facility Security Level (Section 3.2.9 --
GSA's FSL-based scheme REPLACES UFC's Occupancy-Category-based scheme),
the existing-building disproportionate-collapse allowance (Section
3.2.10.2, NOT present in the current UFC 4-023-03 edition -- Commentary
C3.2.10.2 notes the current UFC removed its own prior 15%/30% allowance
while GSA's Guidelines restore it for existing buildings only), the LSP/
NSP/NDP load combinations and Load/Dynamic Increase Factor Tables 4 and 5,
and the acceptance-criteria checks for all three procedures.

CROSS-DOCUMENT CONSISTENCY (verified against geotech_references.ufc_collapse
in tests/test_gsa_collapse_alternate_path.py):
  - Table 4 (Load Increase Factors) and Table 5 (Dynamic Increase Factors)
    are printed IDENTICALLY in GSA and in UFC 4-023-03 (Tables 3-4/3-5) --
    both derive from the same underlying study (Appendix A ref [13],
    McKay/Marchand/Stevens 2008) and neither has been revised since.
  - The force-/deformation-controlled classification rule (Section 3.2.5,
    Figure 3.7/Table 1) is printed with IDENTICAL wording to UFC 4-023-03
    Section 3-2.5/Figure 3-7/Table 3-1.
  - Table 2 and Table 3 (component-capacity calculation basis) are
    IDENTICAL in form to UFC's Tables 3-2/3-3.

VALIDATED against Appendix D's worked reinforced-concrete example (printed
pp. D11-D13, pdf_page 112-114): the column m-factor example
(P/(Ag*f'c)=0.35, rho_v=0.003 -> m=2.0) is reproduced exactly. The
companion typical-beam-component example's single-axis intermediate
result (rho-rho'/rho_bal=0.037, C, at V/(bw*d*sqrt(f'c))=3 -> m=15.48) is
ALSO reproduced exactly by
``geotech_references.gsa_collapse.reinforced_concrete.table_7_beam_flexure_mfactor``
-- but see that module's docstring for two further flagged discrepancies
in the document's own companion result (vw_ratio=6) and its final
bilinearly-interpolated answer.

FLAGGED PRINTED ARITHMETIC ERROR (page-verified against the rendered PDF,
NOT silently corrected): Appendix D's secondary-component pan-joist shear
check (printed p. D47) computes VCL=Av*fy*d/s=42 kips, then states the
force-controlled acceptance check as "Phi*QCL >= QUF: 0.75(80 kips) = 42
kips <= 57.6 kips, NG" -- the printed "80 kips" does not correspond to any
quantity derived earlier on the page, and 0.75*80=60, not 42, so the
printed intermediate equation is internally inconsistent. The document's
own stated "NG" conclusion IS correct and is reproduced exactly using its
own VCL=42 kips: Phi*QCL = 0.75*42 = 31.5 kips < QUF = 57.6 kips (see
``tests/test_gsa_collapse_alternate_path.py::TestAcceptanceCriteria::
test_force_controlled_capacity_check_inadequate``).
"""


# ============================================================================
# Section 3.1 / 3.3 -- Removed Methods (printed pp. 7, 31, pdf_page 19, 43)
# ============================================================================

def tie_forces_removed():
    """Section 3.1: "This UFC section is removed in its entirety,"
    including Figures 3.1 through 3.6 (printed p. 7). GSA's Guidelines do
    not permit Tie Forces as an alternative to, or supplement of, the
    Alternate Path method for ANY Facility Security Level or occupancy
    (Commentary C3.1).

    Returns
    -------
    dict
        {'removed': True, 'removed_figures': ['3.1', ..., '3.6'],
         'section': '3.1', 'printed_page': '7', 'pdf_page': 19}
    """
    return {"removed": True,
            "removed_figures": [f"3.{i}" for i in range(1, 7)],
            "section": "3.1", "printed_page": "7", "pdf_page": 19}


def enhanced_local_resistance_removed():
    """Section 3.3: "This UFC section has been removed in its entirety"
    (printed p. 31). Enhanced Local Resistance (ELR) is likewise removed
    from every material chapter (Sections 4.5, 5.5, 6.5, 7.6, 8.5).

    Returns
    -------
    dict
        {'removed': True, 'section': '3.3', 'printed_page': '31',
         'pdf_page': 43}
    """
    return {"removed": True, "section": "3.3", "printed_page": "31", "pdf_page": 43}


# ============================================================================
# Equation 3.1 -- General LRFD Check (Section 3.2.3, printed p. 8,
# pdf_page 20)
# ============================================================================

def lrfd_strength_check(phi, rn, ru):
    """Equation 3.1: general LRFD design-strength adequacy check used
    throughout the Alternate Path method (printed p. 8).

        Phi*Rn >= Ru

    Parameters
    ----------
    phi : float
        Strength reduction factor from the applicable material-specific
        code.
    rn : float
        Nominal strength -- the expected strength QCE for deformation-
        controlled actions, or the lower-bound strength QCL for force-
        controlled actions (Section 3.2.6).
    ru : float
        Required strength (Sum gamma_i * Q_i).

    Returns
    -------
    dict
        {'design_strength', 'ru', 'adequate' (bool), 'equation': '3.1',
         'printed_page': '8', 'pdf_page': 20}
    """
    design_strength = phi * rn
    return {"design_strength": design_strength, "ru": ru,
            "adequate": design_strength >= ru, "equation": "3.1",
            "printed_page": "8", "pdf_page": 20}


# ============================================================================
# Section 3.2.5 -- Force- and Deformation-Controlled Actions (printed
# pp. 9-10, pdf_page 21-22)
# ============================================================================

def classify_action(curve_type, e_over_g, is_primary):
    """Section 3.2.5: classifies a component action as deformation- or
    force-controlled from its ASCE-41-style force-deformation curve type
    (Figure 3.7) and its e/g ratio (printed pp. 9-10). Printed with
    IDENTICAL wording and thresholds to UFC 4-023-03 Section 3-2.5 (see
    module docstring cross-check note).

    Primary component: deformation-controlled if (Type 1 or Type 2 curve)
    AND e >= 2g; force-controlled if (Type 1 or Type 2) AND e < 2g, or if
    Type 3.

    Secondary component: deformation-controlled if Type 1 (any e/g), or
    Type 2 AND e >= 2g; force-controlled if Type 2 AND e < 2g, or Type 3.

    Parameters
    ----------
    curve_type : int
        1, 2, or 3 (Figure 3.7 force-deformation curve type).
    e_over_g : float
        Ratio of deformation e to g on the component's curve (Figure 3.7).
    is_primary : bool
        True for a primary component (Section 3.2.4), False for secondary.

    Returns
    -------
    dict
        {'classification' ('deformation_controlled' or 'force_controlled'),
         'curve_type', 'e_over_g', 'is_primary', 'section': '3.2.5',
         'printed_page': '9-10', 'pdf_page': '21-22'}
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
            "section": "3.2.5", "printed_page": "9-10", "pdf_page": "21-22"}


# ============================================================================
# Section 3.2.8 -- Component Force and Deformation Capacities, Tables 2/3
# (printed pp. 11-12, pdf_page 23-24)
# ============================================================================

def component_capacity_nonlinear(deformation_controlled):
    """Table 2: component-capacity basis for the Nonlinear Static and
    Nonlinear Dynamic Procedures (printed p. 11).

    Deformation-controlled: capacity = permissible inelastic deformation
    limit (strength capacity N/A). Force-controlled: capacity =
    Phi*QCL (deformation capacity N/A).

    Parameters
    ----------
    deformation_controlled : bool
        True for a deformation-controlled action, False for force-
        controlled.

    Returns
    -------
    dict
        {'deformation_capacity_basis', 'strength_capacity_basis',
         'table': '2', 'printed_page': '11', 'pdf_page': 23}
    """
    if deformation_controlled:
        return {"deformation_capacity_basis": "deformation_limit",
                "strength_capacity_basis": None, "table": "2",
                "printed_page": "11", "pdf_page": 23}
    return {"deformation_capacity_basis": None,
            "strength_capacity_basis": "phi_qcl", "table": "2",
            "printed_page": "11", "pdf_page": 23}


def component_capacity_linear(deformation_controlled):
    """Table 3: component-capacity basis for the Linear Static Procedure
    (printed p. 12).

    Deformation-controlled: material strength = expected (QCE); strength
    capacity = Phi*m*QCE. Force-controlled: material strength = lower
    bound (QCL); strength capacity = Phi*QCL.

    Parameters
    ----------
    deformation_controlled : bool
        True for a deformation-controlled action, False for force-
        controlled.

    Returns
    -------
    dict
        {'material_strength_basis', 'strength_capacity_formula',
         'table': '3', 'printed_page': '12', 'pdf_page': 24}
    """
    if deformation_controlled:
        return {"material_strength_basis": "expected_strength_qce",
                "strength_capacity_formula": "phi_m_qce", "table": "3",
                "printed_page": "12", "pdf_page": 24}
    return {"material_strength_basis": "lower_bound_strength_qcl",
            "strength_capacity_formula": "phi_qcl", "table": "3",
            "printed_page": "12", "pdf_page": 24}


# ============================================================================
# Section 3.2.9 -- Removal of Load-Bearing Elements, by Facility Security
# Level (printed pp. 12-16, pdf_page 24-28)
# ============================================================================

def removed_element_extent(clear_height_or_story_height):
    """Section 3.2.9.1: for ANY column removal, remove the full clear
    height between lateral restraints. For an external/internal
    load-bearing WALL corner, remove a length equal to the clear story
    height H in each direction (Sections 3.2.9.2.4/3.2.9.2.5); a
    non-corner wall removal (Section 3.2.9.2.4 "as a minimum... near the
    middle") uses the same clear-story-height extent by convention of the
    accompanying figures (printed pp. 12, 14-15).

    Parameters
    ----------
    clear_height_or_story_height : float
        Clear column height between lateral restraints, OR clear story
        height H for a wall removal (ft or m).

    Returns
    -------
    dict
        {'removed_extent', 'section': '3.2.9.1', 'printed_page': '12',
         'pdf_page': 24}
    """
    return {"removed_extent": clear_height_or_story_height,
            "section": "3.2.9.1", "printed_page": "12", "pdf_page": 24}


def removal_locations_fsl_3_4():
    """Section 3.2.9(1): for FSL III and IV, vertical load-bearing
    elements are removed at EXTERIOR locations at the first floor above
    grade, and at ALL elements (interior and exterior) within underground
    parking, loading docks, and areas of uncontrolled public access
    (printed p. 12). "Controlled public access" requires BOTH badge-ID
    access control with guard inspection AND x-ray/magnetometer screening
    of visitors and their property.

    Specific plan locations (Sections 3.2.9.2.2-3.2.9.2.5, printed pp.
    13-16): near the middle of the short side, near the middle of the
    long side, at the corner of the building (columns) / at the corner
    with a length of 2H in each direction (walls), and adjacent to the
    corner (penultimate, columns only); PLUS critical locations governed
    by engineering judgment (plan-geometry changes, vertical load
    discontinuities, lightly-loaded adjacent elements, differing tributary
    bay sizes, differing framing orientations/elevations).

    Returns
    -------
    dict
        {'story_scope': 'first floor above grade (exterior); underground
         parking / loading docks / uncontrolled public access (interior
         and exterior, each affected story)', 'plan_locations' (list of
         str), 'controlled_public_access_criteria' (list of str),
         'section': '3.2.9', 'printed_page': '12-16', 'pdf_page': '24-28'}
    """
    return {
        "story_scope": (
            "first floor above grade (exterior elements only); underground "
            "parking, loading docks, and areas of uncontrolled public access "
            "(interior and exterior elements, at each affected story)"
        ),
        "plan_locations": [
            "near the middle of the short side", "near the middle of the long side",
            "at the corner of the building (columns) / for the corner in each "
            "direction (walls, length = 2H)",
            "adjacent to the corner, i.e. penultimate (columns only)",
            "critical locations per engineering judgment (plan-geometry change, "
            "vertical load discontinuity, lightly-loaded adjacent element, "
            "differing tributary bay size, differing framing orientation/elevation)",
        ],
        "controlled_public_access_criteria": [
            "badge ID system for employee access with guard inspection before entry",
            "x-ray and magnetometer screening for all visitors and their property",
        ],
        "section": "3.2.9", "printed_page": "12-16", "pdf_page": "24-28",
    }


def removal_locations_fsl_5():
    """Section 3.2.9(2): for FSL V, BOTH interior and exterior vertical
    load-bearing elements are removed AT EACH FLOOR LEVEL of the building
    (printed p. 12) -- unlike FSL III/IV, there is no restriction to the
    ground floor or to uncontrolled-access areas. Commentary C2.3 notes
    this whole-building removal scope is why Redundancy Requirements
    (Section 3.4) need not be separately applied to FSL V facilities (see
    ``applicability.fsl_applicability``).

    Returns
    -------
    dict
        {'story_scope': 'every floor level (interior and exterior)',
         'section': '3.2.9', 'printed_page': '12', 'pdf_page': 24}
    """
    return {"story_scope": "every floor level, interior and exterior elements",
            "section": "3.2.9", "printed_page": "12", "pdf_page": 24}


def adjacent_element_removal_trigger(distance, reference_dimension):
    """Sections 3.2.9.2.2/3.2.9.2.3 (columns): if another load-bearing
    column is within a horizontal distance of 30% of the largest dimension
    of the associated bay from the primary removal location, it must be
    removed SIMULTANEOUSLY (printed pp. 13-14).

    Parameters
    ----------
    distance : float
        Distance from the primary removal location to the other column
        (ft or m).
    reference_dimension : float
        Largest dimension of the associated bay, same units as *distance*.

    Returns
    -------
    dict
        {'triggers_simultaneous_removal' (bool), 'threshold_distance',
         'section': '3.2.9.2.2', 'printed_page': '13-14', 'pdf_page': '25-26'}
    """
    threshold = 0.30 * reference_dimension
    return {
        "triggers_simultaneous_removal": distance <= threshold,
        "threshold_distance": threshold, "section": "3.2.9.2.2",
        "printed_page": "13-14", "pdf_page": "25-26",
    }


# ============================================================================
# Section 3.2.10 -- Structural Acceptance Criteria (printed pp. 17-18,
# pdf_page 29-30)
# ============================================================================

def disproportionate_collapse_allowance(is_exterior_removal):
    """Section 3.2.10.2 (Existing Buildings only): if any primary or
    secondary elements exceed the acceptance criteria, the existing
    building may STILL be considered to satisfy the Alternate Path
    requirements provided the resulting extent of collapse is not
    "disproportionate" -- defined as floor framing within a single
    structural bay on each side, immediately adjacent to and at the floor
    level directly above the removed element, not exceeding 15% of the
    total floor area (exterior removal) or 30% of the total floor area
    (interior removal) for each respective floor (printed p. 17, Figures
    3.13/3.14).

    Requires Government approval of the proposed alternative-approach
    methodology prior to commencement of analysis, and third-party or
    Government review of the final analysis (Section 3.2.10.2). Does NOT
    apply to new buildings and additions (Section 3.2.10.1), which must
    meet the acceptance criteria with no collapse allowance.

    Commentary C3.2.10.2 notes this allowance is NOT present in the
    current UFC 4-023-03 edition, which removed its own prior 15%/30%
    allowance entirely -- see module docstring cross-check note.

    Parameters
    ----------
    is_exterior_removal : bool
        True for an exterior column/wall removal scenario, False for
        interior.

    Returns
    -------
    dict
        {'allowable_extent_pct' (15 or 30), 'applies_to': 'existing
         buildings only', 'section': '3.2.10.2', 'printed_page': '17',
         'pdf_page': 29}
    """
    pct = 15 if is_exterior_removal else 30
    return {"allowable_extent_pct": pct, "applies_to": "existing buildings only",
            "section": "3.2.10.2", "printed_page": "17", "pdf_page": 29}


# ============================================================================
# Section 3.2.11.1 -- Limitations on the Use of the Linear Static
# Procedure (printed pp. 19-20, pdf_page 31-32)
# ============================================================================

def lsp_story_limit():
    """Section 3.2.11.1: the Linear Static Procedure (LSP) is limited to
    structures of 10 STORIES OR LESS (printed p. 19) -- a limitation NOT
    present in UFC 4-023-03's own LSP applicability section, which has no
    story-count cap.

    Returns
    -------
    dict
        {'max_stories': 10, 'section': '3.2.11.1', 'printed_page': '19',
         'pdf_page': 31}
    """
    return {"max_stories": 10, "section": "3.2.11.1", "printed_page": "19", "pdf_page": 31}


def irregularity_check(has_discontinuity=False, has_asymmetric_bay_stiffness=False,
                        has_asymmetric_wall_stiffness=False, has_nonorthogonal_lateral_elements=False):
    """Section 3.2.11.1.1: a structure is IRREGULAR (restricting LSP use,
    see ``lsp_applicable``) if ANY of four printed conditions is true
    (printed pp. 19-20):

    1. Significant discontinuities in gravity/lateral systems (out-of-
       plane offsets of primary vertical elements, roof belt-girders,
       transfer girders/non-stacking primary columns). Stepped-back
       stories are NOT an irregularity.
    2. At an exterior column (except corners), bay stiffness/strength
       ratio from one side to the other < 50%, at any story.
    3. For exterior load-bearing walls (except corners), wall stiffness/
       strength ratio from one side of an intersecting wall to the
       other < 50%, at any story.
    4. Horizontal lateral-load-resisting elements not parallel to the
       major orthogonal axes (skewed/curved frames or walls).

    Parameters
    ----------
    has_discontinuity, has_asymmetric_bay_stiffness,
    has_asymmetric_wall_stiffness, has_nonorthogonal_lateral_elements : bool
        Each corresponds to one printed condition above.

    Returns
    -------
    dict
        {'is_irregular' (bool), 'triggered_conditions' (list of int),
         'section': '3.2.11.1.1', 'printed_page': '19-20',
         'pdf_page': '31-32'}
    """
    flags = [has_discontinuity, has_asymmetric_bay_stiffness,
             has_asymmetric_wall_stiffness, has_nonorthogonal_lateral_elements]
    triggered = [i + 1 for i, f in enumerate(flags) if f]
    return {"is_irregular": any(flags), "triggered_conditions": triggered,
            "section": "3.2.11.1.1", "printed_page": "19-20", "pdf_page": "31-32"}


def lsp_applicable(is_irregular, max_dcr=None):
    """Section 3.2.11.1: determines whether the Linear Static Procedure
    (LSP) may be used (printed p. 19), independent of the 10-story limit
    (``lsp_story_limit``).

    Regular structure: LSP always permitted (no DCR check needed).
    Irregular structure: LSP permitted only if every component DCR
    (``dcr``) is <= 2.0; otherwise NSP or NDP is required.

    Parameters
    ----------
    is_irregular : bool
        From ``irregularity_check``.
    max_dcr : float, optional
        Largest component DCR in the structure (required if irregular).

    Returns
    -------
    dict
        {'lsp_permitted' (bool), 'reason', 'section': '3.2.11.1',
         'printed_page': '19', 'pdf_page': 31}
    """
    if not is_irregular:
        return {"lsp_permitted": True, "reason": "structure is regular",
                "section": "3.2.11.1", "printed_page": "19", "pdf_page": 31}
    if max_dcr is None:
        raise ValueError("max_dcr is required when is_irregular=True")
    permitted = max_dcr <= 2.0
    reason = f"irregular structure, max DCR={max_dcr} ({'<=' if permitted else '>'} 2.0)"
    return {"lsp_permitted": permitted, "reason": reason, "section": "3.2.11.1",
            "printed_page": "19", "pdf_page": 31}


def dcr(q_udlim, q_ce):
    """Equation 3.2: Demand-Capacity Ratio, used only to determine LSP
    applicability for an irregular structure (printed p. 20).

        DCR = QUDLim / QCE

    Parameters
    ----------
    q_udlim : float
        Deformation-controlled action from a linear model with gravity
        dead/live loads increased by the Omega_LD load increase factor
        (Section 3.2.11.1.2).
    q_ce : float
        Expected strength of the component (Chapters 4-8).

    Returns
    -------
    dict
        {'dcr', 'equation': '3.2', 'printed_page': '20', 'pdf_page': 32}
    """
    return {"dcr": q_udlim / q_ce, "equation": "3.2", "printed_page": "20", "pdf_page": 32}


# ============================================================================
# Section 3.2.11.4 -- LSP Loading, Equations 3.3, 3.4, 3.5
# (printed pp. 21-22, pdf_page 33-34)
# ============================================================================

def _gravity_load_extreme_event(d, l=0.0, s=0.0):
    """Common ASCE-7-extraordinary-event gravity combination used (with
    different multipliers) throughout the AP method: 1.2D + (0.5L or
    0.2S). Internal helper; L and S are not combined -- pass whichever
    governs (live or snow) as *l* or *s*, not both nonzero, per the
    printed equations. Live load L must already reflect the live-load
    reduction of Section 3.2.3, capped at 50 psf / 2.4 kN/m2 (printed
    pp. 21-22).
    """
    return 1.2 * d + 0.5 * l + 0.2 * s


def deformation_controlled_load_lsp(omega_ld, d, l=0.0, s=0.0):
    """Equation 3.3: increased gravity load for DEFORMATION-controlled
    actions, applied to bays immediately adjacent to and at all floors
    above the removed element (printed p. 21).

        GLD = Omega_LD * [1.2 D + (0.5 L or 0.2 S)]

    Parameters
    ----------
    omega_ld : float
        Load increase factor for deformation-controlled actions, from
        ``table_4_load_increase_factor``.
    d : float
        Dead load including facade loads (lb/ft2 or kN/m2).
    l : float, optional
        Live load including live-load reduction, capped at 50 lb/ft2 (244
        -- printed as kN/m2, though dimensionally this is 2.4 kN/m2; see
        module docstring). Default 0.
    s : float, optional
        Snow load (lb/ft2 or kN/m2). Default 0. Use L or S, not both.

    Returns
    -------
    dict
        {'gld', 'omega_ld', 'd', 'l', 's', 'equation': '3.3',
         'printed_page': '21', 'pdf_page': 33}
    """
    gld = omega_ld * _gravity_load_extreme_event(d, l, s)
    return {"gld": gld, "omega_ld": omega_ld, "d": d, "l": l, "s": s,
            "equation": "3.3", "printed_page": "21", "pdf_page": 33}


def gravity_load_away_from_removal(d, l=0.0, s=0.0):
    """Equation 3.4 (also restated as Equation 3.9 for NSP and Equation
    3.11 for NDP, applied to the whole structure): gravity load for bays
    NOT loaded with the increased (LIF/DIF) load (printed pp. 21, 27, 30).

        G = 1.2 D + (0.5 L or 0.2 S)

    Parameters
    ----------
    d, l, s : float
        Dead, live, and snow loads as in ``deformation_controlled_load_lsp``.

    Returns
    -------
    dict
        {'g', 'd', 'l', 's', 'equation': '3.4 / 3.9 / 3.11',
         'printed_page': '21, 27, 30', 'pdf_page': '33, 39, 42'}
    """
    g = _gravity_load_extreme_event(d, l, s)
    return {"g": g, "d": d, "l": l, "s": s, "equation": "3.4 / 3.9 / 3.11",
            "printed_page": "21, 27, 30", "pdf_page": "33, 39, 42"}


def force_controlled_load_lsp(omega_lf, d, l=0.0, s=0.0):
    """Equation 3.5: increased gravity load for FORCE-controlled actions
    in the LSP (printed pp. 21-22).

        GLF = Omega_LF * [1.2 D + (0.5 L or 0.2 S)]

    Parameters
    ----------
    omega_lf : float
        Load increase factor for force-controlled actions (always 2.0 per
        Table 4).
    d, l, s : float
        Dead, live, and snow loads.

    Returns
    -------
    dict
        {'glf', 'omega_lf', 'd', 'l', 's', 'equation': '3.5',
         'printed_page': '21-22', 'pdf_page': '33-34'}
    """
    glf = omega_lf * _gravity_load_extreme_event(d, l, s)
    return {"glf": glf, "omega_lf": omega_lf, "d": d, "l": l, "s": s,
            "equation": "3.5", "printed_page": "21-22", "pdf_page": "33-34"}


def nonlinear_static_load(omega_n, d, l=0.0, s=0.0):
    """Equation 3.8: increased gravity load for the Nonlinear Static
    Procedure, both deformation- and force-controlled actions together
    (printed p. 27).

        GN = Omega_N * [1.2 D + (0.5 L or 0.2 S)]

    Parameters
    ----------
    omega_n : float
        Dynamic increase factor from ``table_5_dynamic_increase_factor``.
    d, l, s : float
        Dead, live, and snow loads.

    Returns
    -------
    dict
        {'gn', 'omega_n', 'd', 'l', 's', 'equation': '3.8',
         'printed_page': '27', 'pdf_page': 39}
    """
    gn = omega_n * _gravity_load_extreme_event(d, l, s)
    return {"gn": gn, "omega_n": omega_n, "d": d, "l": l, "s": s,
            "equation": "3.8", "printed_page": "27", "pdf_page": 39}


def nonlinear_dynamic_load(d, l=0.0, s=0.0):
    """Equation 3.11: gravity load applied to the ENTIRE structure for the
    Nonlinear Dynamic Procedure, before the column/wall section is removed
    (printed p. 30). Identical form to Equation 3.4/3.9, no load increase
    factor (the dynamic effect is captured by the removal-duration
    requirement of Section 3.2.13.4.2, not a static multiplier).

        GND = 1.2 D + (0.5 L or 0.2 S)

    Parameters
    ----------
    d, l, s : float
        Dead, live, and snow loads.

    Returns
    -------
    dict
        {'gnd', 'd', 'l', 's', 'equation': '3.11', 'printed_page': '30',
         'pdf_page': 42}
    """
    gnd = _gravity_load_extreme_event(d, l, s)
    return {"gnd": gnd, "d": d, "l": l, "s": s, "equation": "3.11",
            "printed_page": "30", "pdf_page": 42}


# ============================================================================
# Table 4 -- Load Increase Factors for Linear Static Analysis (printed
# p. 22, pdf_page 34)
# ============================================================================

_TABLE_4 = {
    ("steel", "framed"): {"omega_ld": lambda m: 0.9 * m + 1.1, "omega_lf": 2.0},
    ("reinforced_concrete", "framed"): {"omega_ld": lambda m: 1.2 * m + 0.80, "omega_lf": 2.0},
    ("reinforced_concrete", "load_bearing_wall"): {"omega_ld": lambda m: 2.0 * m, "omega_lf": 2.0},
    ("masonry", "load_bearing_wall"): {"omega_ld": lambda m: 2.0 * m, "omega_lf": 2.0},
    ("wood", "load_bearing_wall"): {"omega_ld": lambda m: 2.0 * m, "omega_lf": 2.0},
    ("cold_formed_steel", "load_bearing_wall"): {"omega_ld": lambda m: 2.0 * m, "omega_lf": 2.0},
}


def table_4_load_increase_factor(material, structure_type, m_lif):
    """Table 4: Linear Static load increase factors Omega_LD
    (deformation-controlled) and Omega_LF (force-controlled, always 2.0)
    (printed p. 22).

    mLIF is the SMALLEST m-factor of any primary beam, girder, spandrel,
    or wall element directly connected to the columns/walls directly above
    the removal location (columns are excluded from the mLIF
    determination). For reinforced-concrete framed structures, beam-column
    joints are force-controlled per ASCE 41 but the Omega_LD calculation
    still uses the m-factor of the beam hinge forming near the column
    (Footnote A).

    PRINTED IDENTICALLY to UFC 4-023-03 Table 3-4 -- see module docstring
    cross-check note; verified against
    ``geotech_references.ufc_collapse.alternate_path.table_3_4_load_increase_factor``.

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
         'table': '4', 'printed_page': '22', 'pdf_page': 34}
    """
    key = (material.lower().strip(), structure_type.lower().strip())
    if key not in _TABLE_4:
        raise ValueError(
            f"No Table 4 row for material={material!r}, structure_type={structure_type!r}; "
            f"valid combinations: {sorted(_TABLE_4)}"
        )
    row = _TABLE_4[key]
    return {
        "omega_ld": row["omega_ld"](m_lif), "omega_lf": row["omega_lf"],
        "material": key[0], "structure_type": key[1], "m_lif": m_lif,
        "table": "4", "printed_page": "22", "pdf_page": 34,
    }


# ============================================================================
# Table 5 -- Dynamic Increase Factors for Nonlinear Static Analysis
# (printed p. 28, pdf_page 40)
# ============================================================================

_TABLE_5 = {
    ("steel", "framed"): lambda r: 1.08 + 0.76 / (r + 0.83),
    ("reinforced_concrete", "framed"): lambda r: 1.04 + 0.45 / (r + 0.48),
    ("reinforced_concrete", "load_bearing_wall"): lambda r: 2.0,
    ("masonry", "load_bearing_wall"): lambda r: 2.0,
    ("wood", "load_bearing_wall"): lambda r: 2.0,
    ("cold_formed_steel", "load_bearing_wall"): lambda r: 2.0,
}


def table_5_dynamic_increase_factor(material, structure_type, theta_pra=None, theta_y=None):
    """Table 5: Nonlinear Static dynamic increase factor Omega_N (printed
    p. 28). For steel-framed and RC-framed structures, Omega_N is a
    function of the normalized rotation ratio theta_pra/theta_y (choose
    the SMALLEST such ratio for any primary element/connection within or
    touching the region loaded with the increased gravity load; columns
    excluded). Load-bearing-wall structures of any material are fixed
    at 2.0.

        Steel framed:                Omega_N = 1.08 + 0.76/(r + 0.83)
        Reinforced concrete framed:  Omega_N = 1.04 + 0.45/(r + 0.48)
        (r = theta_pra / theta_y)

    PRINTED IDENTICALLY to UFC 4-023-03 Table 3-5 -- see module docstring
    cross-check note; verified against
    ``geotech_references.ufc_collapse.alternate_path.table_3_5_dynamic_increase_factor``.

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
         None for load-bearing walls), 'table': '5', 'printed_page': '28',
         'pdf_page': 40}
    """
    key = (material.lower().strip(), structure_type.lower().strip())
    if key not in _TABLE_5:
        raise ValueError(
            f"No Table 5 row for material={material!r}, structure_type={structure_type!r}; "
            f"valid combinations: {sorted(_TABLE_5)}"
        )
    if key[1] == "framed":
        if theta_pra is None or theta_y is None:
            raise ValueError("theta_pra and theta_y are required for framed structures")
        r = theta_pra / theta_y
        omega_n = _TABLE_5[key](r)
    else:
        r = None
        omega_n = _TABLE_5[key](r)
    return {"omega_n": omega_n, "material": key[0], "structure_type": key[1],
            "rotation_ratio": r, "table": "5", "printed_page": "28", "pdf_page": 40}


# ============================================================================
# Acceptance Criteria -- Equations 3.6, 3.7 (LSP), 3.10 (NSP), 3.12 (NDP)
# (printed pp. 25-26, 28-29, 31, pdf_page 37-38, 40-41, 43)
# ============================================================================

def deformation_controlled_capacity_check(phi, m, q_ce, q_ud):
    """Equation 3.6: Linear Static Procedure acceptance check for
    deformation-controlled actions, all primary and secondary components
    (printed p. 25).

        Phi * m * QCE >= QUD

    Parameters
    ----------
    phi : float
        Strength reduction factor from the applicable material code.
    m : float
        Component/element demand modifier (m-factor) from Chapters 4-8.
    q_ce : float
        Expected strength of the component for the deformation-controlled
        action.
    q_ud : float
        Deformation-controlled action from the Linear Static model.

    Returns
    -------
    dict
        {'capacity' (phi*m*q_ce), 'q_ud', 'adequate' (bool),
         'equation': '3.6', 'printed_page': '25', 'pdf_page': 37}
    """
    capacity = phi * m * q_ce
    return {"capacity": capacity, "q_ud": q_ud, "adequate": capacity >= q_ud,
            "equation": "3.6", "printed_page": "25", "pdf_page": 37}


def force_controlled_capacity_check(phi, q_cl, q_uf):
    """Equations 3.7 (LSP), 3.10 (NSP), 3.12 (NDP): acceptance check for
    force-controlled actions, all primary and secondary components,
    identical in form across all three procedures (printed pp. 25-26,
    28-29, 31).

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
         'equation': '3.7 / 3.10 / 3.12', 'printed_page': '25-26, 28-29, 31',
         'pdf_page': '37-38, 40-41, 43'}
    """
    capacity = phi * q_cl
    return {"capacity": capacity, "q_uf": q_uf, "adequate": capacity >= q_uf,
            "equation": "3.7 / 3.10 / 3.12", "printed_page": "25-26, 28-29, 31",
            "pdf_page": "37-38, 40-41, 43"}


def deformation_controlled_capacity_check_nonlinear(expected_deformation_capacity, demand):
    """Sections 3.2.12.7.1 (NSP) / 3.2.13.6.1 (NDP): for deformation-
    controlled actions, primary and secondary elements must have an
    EXPECTED DEFORMATION CAPACITY greater than the maximum calculated
    deformation demand -- no m-factor or Phi is applied (unlike the LSP's
    Equation 3.6), since the nonlinear analysis itself already produces an
    inelastic deformation demand to compare directly against the
    deformation limit (printed pp. 28, 31).

    Parameters
    ----------
    expected_deformation_capacity : float
        Permissible inelastic deformation limit (e.g. plastic rotation
        angle, radians) per Chapters 4-8.
    demand : float
        Maximum calculated deformation demand from the nonlinear model.

    Returns
    -------
    dict
        {'capacity', 'demand', 'adequate' (bool),
         'section': '3.2.12.7.1 / 3.2.13.6.1', 'printed_page': '28, 31',
         'pdf_page': '40, 43'}
    """
    return {"capacity": expected_deformation_capacity, "demand": demand,
            "adequate": expected_deformation_capacity >= demand,
            "section": "3.2.12.7.1 / 3.2.13.6.1", "printed_page": "28, 31",
            "pdf_page": "40, 43"}
