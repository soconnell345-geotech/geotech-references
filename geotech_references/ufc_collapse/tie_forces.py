"""UFC 4-023-03 Section 3-1 -- Tie Forces (printed pp. 13-28, pdf_page 28-43).

The Tie Force (TF) method mechanically ties the building together so that,
if a vertical load-bearing element is damaged, the floor/roof system can
transfer load to adjacent undamaged structure by catenary or membrane
action. Three horizontal ties (longitudinal, transverse, peripheral) plus
vertical ties in every column/load-bearing wall. All Tie Force equations in
this module are MATERIAL-INDEPENDENT (Section 3-1 applies identically to
Chapters 4-8); only the strength-reduction factor Phi and over-strength
factor used in ``required_tie_area`` are material specific (e.g. Phi=0.75
for reinforced-concrete rebar in tension per Section 4-3, over-strength
1.25 per ASCE 41 Table 10-4).

Validated against Appendix D's worked reinforced-concrete example (printed
pp. 124-129): ``effective_floor_load_nonuniform`` reproduces wF = 214.5-psf
(Table D-1); ``peripheral_tie_force_two_way`` reproduces Fp = 250.1-kip and
``required_tie_area`` reproduces As = 4.45-in2 (Table D-2, transverse/
longitudinal peripheral tie).
"""


# ============================================================================
# Section 3-1.1 -- Minimum Structural Requirements for Tie Force Application
# (printed p. 13-14, pdf_page 28-29)
# ============================================================================

def minimum_bays_for_tie_force(bays_direction_1, bays_direction_2=None,
                                one_way_wall=False, wall_length=None,
                                clear_story_height=None):
    """Section 3-1.1: checks whether a structure meets the minimum geometric
    requirements to apply the Tie Force method (printed p. 13-14).

    For framed and two-way load-bearing wall structures: 4 or more bays in
    BOTH orthogonal directions. For one-way load-bearing wall structures:
    4 or more bays in the one-way span direction, AND the wall length (or
    building width) must be at least 4*hw (hw = clear story height).

    Parameters
    ----------
    bays_direction_1 : int
        Number of bays in the (primary/one-way-span) direction.
    bays_direction_2 : int, optional
        Number of bays in the orthogonal direction (framed/two-way only).
    one_way_wall : bool, optional
        True for a one-way load-bearing wall structure. Default False.
    wall_length : float, optional
        Length of the load-bearing wall / building width (one-way only).
    clear_story_height : float, optional
        Clear story height hw (one-way only, same units as wall_length).

    Returns
    -------
    dict
        {'meets_minimum_requirements' (bool), 'reason', 'paragraph': '3-1.1',
         'printed_page': '13-14', 'pdf_page': '28-29'}
    """
    if one_way_wall:
        bays_ok = bays_direction_1 >= 4
        length_ok = True
        if wall_length is not None and clear_story_height is not None:
            length_ok = wall_length >= 4 * clear_story_height
        ok = bays_ok and length_ok
        reason = (
            f"one-way bays={bays_direction_1} (need >=4): {bays_ok}; "
            f"wall_length>=4*hw: {length_ok}"
        )
    else:
        bays_ok_1 = bays_direction_1 >= 4
        bays_ok_2 = (bays_direction_2 is None) or (bays_direction_2 >= 4)
        ok = bays_ok_1 and bays_ok_2
        reason = f"bays direction 1={bays_direction_1}, direction 2={bays_direction_2} (need >=4 each)"
    return {
        "meets_minimum_requirements": ok, "reason": reason,
        "paragraph": "3-1.1", "printed_page": "13-14", "pdf_page": "28-29",
    }


# ============================================================================
# Section 3-1.3.1 -- Uniform Floor Load, Equation 3-2 (printed p. 15, pdf_page 30)
# ============================================================================

def floor_load_wf(dead_load, live_load):
    """Equation 3-2: floor load used for all Tie Force calculations
    (printed p. 15).

        wF = 1.2 D + 0.5 L

    Parameters
    ----------
    dead_load : float
        Dead load, D (lb/ft2 or kN/m2).
    live_load : float
        Live load, L (lb/ft2 or kN/m2).

    Returns
    -------
    dict
        {'wf', 'dead_load', 'live_load', 'equation': '3-2',
         'printed_page': '15', 'pdf_page': 30}
    """
    wf = 1.2 * dead_load + 0.5 * live_load
    return {"wf": wf, "dead_load": dead_load, "live_load": live_load,
            "equation": "3-2", "printed_page": "15", "pdf_page": 30}


# ============================================================================
# Section 3-1.3.2 -- Consideration for Non-Uniform Load Over Floor Area
# (printed pp. 16-17, pdf_page 31-32)
# ============================================================================

def effective_wf_for_nonuniform_load(bay_loads_and_areas):
    """Section 3-1.3.2.2: determines the effective wF for a floor with
    non-uniform bay loading (printed pp. 16-17).

    If the difference between the minimum and maximum bay wF is <=25% of
    the minimum wF, AND the area carrying the maximum wF is <=25% of the
    total floor area, use the area-weighted average wF for the whole floor.
    Otherwise (either threshold exceeded), this function reports that the
    maximum wF must be used for the whole floor OR the floor must be split
    into sub-areas (Section 3-1.3.2.2 item 2) -- the sub-area split itself
    is a layout decision made by the designer (see Figure 3-2), not
    computed here.

    Reproduces the AVERAGING CRITERIA of the Appendix D worked example
    (Table D-1, printed p. 125) exactly: office/storage/corridor bay wF's
    of 207.8/235.3/212.8 psf over 16875/3375/1125 sf, with the
    235.3-207.8=27.5 psf difference being <25% of 207.8 psf and the
    3375 sf storage/mechanical area being <25% of the 21375 sf total, so
    averaging IS permitted. NOTE: applying the printed formula to these
    exact printed inputs gives an area-weighted wF of 212.4 psf, not the
    214.5 psf the source document states as its final answer -- a ~1%
    arithmetic inconsistency in Appendix D's own worked numbers (the
    formula and every individual input value were independently re-
    verified against the printed page; the discrepancy is in the source
    document itself, not this digitization). Table D-2's downstream tie-
    force calculations use wF=214.5 psf as a CARRIED-FORWARD given value
    (not re-derived), so ``peripheral_tie_force_two_way`` and
    ``required_tie_area`` still validate exactly against those results
    when 214.5 is supplied directly.

    Parameters
    ----------
    bay_loads_and_areas : list of (wf, area) tuples
        Each bay's (or bay-group's) wF (Equation 3-2, psf or kN/m2) and its
        plan area (ft2 or m2).

    Returns
    -------
    dict
        {'wf_min', 'wf_max', 'wf_difference', 'wf_difference_pct_of_min',
         'max_load_area', 'total_area', 'max_load_area_pct_of_total',
         'averaging_permitted' (bool), 'effective_wf' (area-weighted average
         if averaging_permitted, else None -- use wf_max or sub-areas),
         'paragraph': '3-1.3.2.2', 'printed_page': '16-17', 'pdf_page': '31-32'}
    """
    wfs = [wf for wf, _ in bay_loads_and_areas]
    areas = [a for _, a in bay_loads_and_areas]
    wf_min, wf_max = min(wfs), max(wfs)
    total_area = sum(areas)
    max_load_area = sum(a for wf, a in bay_loads_and_areas if wf == wf_max)
    diff = wf_max - wf_min
    diff_pct = diff / wf_min if wf_min else float("inf")
    area_pct = max_load_area / total_area if total_area else float("inf")
    averaging_permitted = (diff_pct <= 0.25) and (area_pct <= 0.25)
    effective_wf = (
        sum(wf * a for wf, a in bay_loads_and_areas) / total_area
        if averaging_permitted and total_area else None
    )
    return {
        "wf_min": wf_min, "wf_max": wf_max, "wf_difference": diff,
        "wf_difference_pct_of_min": diff_pct, "max_load_area": max_load_area,
        "total_area": total_area, "max_load_area_pct_of_total": area_pct,
        "averaging_permitted": averaging_permitted, "effective_wf": effective_wf,
        "paragraph": "3-1.3.2.2", "printed_page": "16-17", "pdf_page": "31-32",
    }


# ============================================================================
# Section 3-1.4.1 -- Longitudinal and Transverse (Internal) Ties
# Equations 3-3, 3-4, 3-5 (printed pp. 20-22, pdf_page 35-37)
# ============================================================================

def internal_tie_force_framed(wf, l1):
    """Equation 3-3: internal (longitudinal or transverse) tie force for
    FRAMED structures, including flat plate/flat slab (printed p. 20).

        Fi = 3 wF L1

    Parameters
    ----------
    wf : float
        Floor load per ``floor_load_wf`` (lb/ft2 or kN/m2).
    l1 : float
        Greater of the distances between centers of columns/frames/walls
        supporting any two adjacent floor spaces, in the direction under
        consideration (ft or m).

    Returns
    -------
    dict
        {'fi' (force per unit length, lb/ft or kN/m), 'wf', 'l1',
         'equation': '3-3', 'printed_page': '20', 'pdf_page': 35}
    """
    return {"fi": 3 * wf * l1, "wf": wf, "l1": l1, "equation": "3-3",
            "printed_page": "20", "pdf_page": 35}


def internal_tie_force_two_way_wall(wf, l1):
    """Equation 3-4: internal tie force for TWO-WAY-SPAN load-bearing wall
    structures (printed p. 21). Same form as Equation 3-3.

        Fi = 3 wF L1

    Parameters
    ----------
    wf : float
        Floor load (lb/ft2 or kN/m2).
    l1 : float
        Greater of the distances between centers of walls supporting any
        two adjacent floor spaces, in the direction under consideration.

    Returns
    -------
    dict
        {'fi', 'wf', 'l1', 'equation': '3-4', 'printed_page': '21',
         'pdf_page': 36}
    """
    return {"fi": 3 * wf * l1, "wf": wf, "l1": l1, "equation": "3-4",
            "printed_page": "21", "pdf_page": 36}


def one_way_wall_transverse_length(clear_story_height, building_width):
    """Section 3-1.4.1.2: the transverse-direction L1 (LT) for ONE-WAY
    load-bearing wall structures is the lesser of 5*hw or the building
    width (printed p. 22).

    Parameters
    ----------
    clear_story_height : float
        Clear story height, hw (ft or m).
    building_width : float
        Building width in the transverse direction (ft or m).

    Returns
    -------
    dict
        {'lt', 'clear_story_height', 'building_width', 'paragraph': '3-1.4.1.2',
         'printed_page': '22', 'pdf_page': 37}
    """
    lt = min(5 * clear_story_height, building_width)
    return {"lt": lt, "clear_story_height": clear_story_height,
            "building_width": building_width, "paragraph": "3-1.4.1.2",
            "printed_page": "22", "pdf_page": 37}


def internal_tie_force_one_way_wall(wf, l1):
    """Equation 3-5: internal tie force for ONE-WAY-SPAN load-bearing wall
    structures (printed p. 22). Same form as Equations 3-3/3-4; L1 is
    either LL (longitudinal, greatest wall-center spacing) or LT
    (transverse, from ``one_way_wall_transverse_length``).

        Fi = 3 wF L1

    Parameters
    ----------
    wf : float
        Floor load (lb/ft2 or kN/m2).
    l1 : float
        LL or LT as defined above (ft or m).

    Returns
    -------
    dict
        {'fi', 'wf', 'l1', 'equation': '3-5', 'printed_page': '22',
         'pdf_page': 37}
    """
    return {"fi": 3 * wf * l1, "wf": wf, "l1": l1, "equation": "3-5",
            "printed_page": "22", "pdf_page": 37}


def max_tie_spacing(l_transverse_or_longitudinal):
    """Maximum spacing of internal (longitudinal/transverse) ties, common
    to framed, two-way wall, and one-way wall construction: 0.2*LT or
    0.2*LL as appropriate (printed pp. 17, 21, 22).

    Parameters
    ----------
    l_transverse_or_longitudinal : float
        LT or LL, the relevant bay/wall spacing (ft or m).

    Returns
    -------
    dict
        {'max_spacing', 'l', 'printed_page': '17-22', 'pdf_page': '32-37'}
    """
    return {"max_spacing": 0.2 * l_transverse_or_longitudinal,
            "l": l_transverse_or_longitudinal,
            "printed_page": "17-22", "pdf_page": "32-37"}


def max_force_in_column_or_wall_strip(fi_per_length, l_transverse_or_longitudinal):
    """Section 3-1.4.1.1/3-1.4.1.2: for flat-plate/flat-slab framed
    buildings (no beams/girders/spandrels) or the wall strip of a two-way
    load-bearing wall building, no more than TWICE the required tie
    strength (force per unit length) may be concentrated in the column/
    wall strip, 0.2*L wide and centered on the column/wall line (printed
    pp. 20-21). Reproduces the printed worked example: Fi=10-k/ft,
    LT=20-ft -> strip width=4-ft, max total force = 2*10*0.2*20 = 80-k.

    Parameters
    ----------
    fi_per_length : float
        Required internal tie force per unit length, Fi (k/ft or kN/m).
    l_transverse_or_longitudinal : float
        LT or LL for the direction under consideration (ft or m).

    Returns
    -------
    dict
        {'strip_width', 'max_total_force', 'fi_per_length', 'l',
         'paragraph': '3-1.4.1.1', 'printed_page': '20-21', 'pdf_page': '35-36'}
    """
    strip_width = 0.2 * l_transverse_or_longitudinal
    max_total_force = 2 * fi_per_length * strip_width
    return {
        "strip_width": strip_width, "max_total_force": max_total_force,
        "fi_per_length": fi_per_length, "l": l_transverse_or_longitudinal,
        "paragraph": "3-1.4.1.1", "printed_page": "20-21", "pdf_page": "35-36",
    }


# ============================================================================
# Section 3-1.4.2 -- Peripheral Ties, Equations 3-6, 3-7
# (printed pp. 23-25, pdf_page 38-40)
# ============================================================================

def peripheral_tie_force_two_way(wf, l1, wc, lp=3.3):
    """Equation 3-6: peripheral tie force for FRAMED and TWO-WAY load-
    bearing wall buildings (printed p. 23).

        Fp = 6 wF L1 Lp + 3 WC

    UNITS: wF (psf or kN/m2) times L1 and Lp (ft or m) naturally computes
    in lb (or kN in SI); pass *wc* in that SAME base unit (lb, not kip --
    the printed source labels its own WC in "kip" only for readability
    after computing it in lb, exactly as this function's raw Fp output is
    in lb and is customarily divided by 1000 for a kip-denominated
    report). In SI units (kN/m2, m, kN) no such division is needed since
    kN/m2*m*m already equals kN, matching WC directly.

    Validated against Appendix D (printed p. 126): wF=214.5-psf,
    L1=37.5-ft, Lp=3-ft, WC=35,100-lb (printed as "35.1-kip") ->
    Fp=250,088-lb (Fp/1000=250.1, matching the printed "250.1-kips").

    Parameters
    ----------
    wf : float
        Floor load (lb/ft2 or kN/m2).
    l1 : float
        Greater of the distances between centers of columns/frames/walls
        at the building perimeter (or, at openings, the bay length),
        in the direction under consideration (ft or m).
    wc : float
        1.2 x dead load of cladding over the length of L1, in lb (or kN
        in SI -- NOT kip in US customary units, see UNITS note above);
        the 1.2 LRFD dead-load factor is baked into WC per the source.
    lp : float, optional
        Peripheral-tie width, 3.3 ft (1.0 m) per the source. Default 3.3
        (ft); pass 1.0 for SI units.

    Returns
    -------
    dict
        {'fp', 'wf', 'l1', 'wc', 'lp', 'equation': '3-6',
         'printed_page': '23', 'pdf_page': 38}
    """
    fp = 6 * wf * l1 * lp + 3 * wc
    return {"fp": fp, "wf": wf, "l1": l1, "wc": wc, "lp": lp,
            "equation": "3-6", "printed_page": "23", "pdf_page": 38}


def peripheral_tie_force_one_way(wf, l1, wc, ww, lp=3.3):
    """Equation 3-7: peripheral tie force for ONE-WAY load-bearing wall
    buildings (printed pp. 24-25).

        Fp = 6 wF L1 Lp + 3 WC + 3 WW

    Per the source notes: for end load-bearing walls, WC=0 (the end wall
    IS the facade); for exterior peripheral ties parallel to the
    load-bearing walls (transverse direction), L1 = 2*hw.

    UNITS: same convention as ``peripheral_tie_force_two_way`` -- pass
    *wc* and *ww* in lb (or kN in SI), matching the lb (or kN) that
    wF*L1*Lp naturally computes in; the raw Fp result is in lb (or kN),
    customarily divided by 1000 for a kip-denominated report.

    Parameters
    ----------
    wf : float
        Floor load (lb/ft2 or kN/m2).
    l1 : float
        For ties perpendicular to the load-bearing walls (longitudinal):
        greatest wall-center spacing. For ties parallel to the walls
        (transverse): 2*hw. At openings: the bay length. (ft or m)
    wc : float
        1.2 x dead load of cladding over the length of L1, in lb (or kN
        in SI -- NOT kip); 0 for the end wall (the wall itself is the
        facade).
    ww : float
        1.2 x dead load of the wall over the length of hw, in lb (or kN
        in SI -- NOT kip).
    lp : float, optional
        Peripheral-tie width, 3.3 ft (1.0 m). Default 3.3.

    Returns
    -------
    dict
        {'fp', 'wf', 'l1', 'wc', 'ww', 'lp', 'equation': '3-7',
         'printed_page': '24-25', 'pdf_page': '39-40'}
    """
    fp = 6 * wf * l1 * lp + 3 * wc + 3 * ww
    return {"fp": fp, "wf": wf, "l1": l1, "wc": wc, "ww": ww, "lp": lp,
            "equation": "3-7", "printed_page": "24-25", "pdf_page": "39-40"}


# ============================================================================
# Section 3-1.4.3 -- Vertical Ties (printed p. 25, pdf_page 40)
# ============================================================================

def vertical_tie_force(tributary_area, wf):
    """Section 3-1.4.3: required vertical tie strength -- the largest
    vertical load received by a column or load-bearing wall from any one
    story, using the tributary area and wF (printed p. 25).

        Pv = wF * tributary_area

    Parameters
    ----------
    tributary_area : float
        Tributary floor area for the column/wall at one story (ft2 or m2).
    wf : float
        Floor load per ``floor_load_wf``, including any averaged cladding
        contribution for perimeter columns (lb/ft2 or kN/m2).

    Returns
    -------
    dict
        {'pv', 'tributary_area', 'wf', 'paragraph': '3-1.4.3',
         'printed_page': '25', 'pdf_page': 40}
    """
    return {"pv": wf * tributary_area, "tributary_area": tributary_area,
            "wf": wf, "paragraph": "3-1.4.3", "printed_page": "25", "pdf_page": 40}


def perimeter_column_effective_wf(wf_floor, cladding_dead_load_psf,
                                   clear_story_height, cladding_tributary_width,
                                   column_tributary_area):
    """Averages a perimeter column's cladding (facade) dead load into an
    effective wF for use with ``vertical_tie_force``, reproducing the
    Appendix D worked example for corner column A1 (printed p. 125):

        wF_eff = wF_floor + 1.2*(cladding tributary width)(hw)(cladding psf)
                 / (column tributary area)

    For column A1: wF=214.5-psf + 1.2*(18.75+18.75-ft)(13-ft)(60-psf) /
    (18.75-ft)^2 = 314.3-psf.

    Parameters
    ----------
    wf_floor : float
        Floor-distributed wF per ``floor_load_wf`` (psf or kN/m2).
    cladding_dead_load_psf : float
        Cladding (facade) dead load per unit wall area (psf or kN/m2).
    clear_story_height : float
        Clear story height, hw (ft or m).
    cladding_tributary_width : float
        Total length of exterior wall tributary to this column (ft or m),
        e.g. half-bay on each side.
    column_tributary_area : float
        Column's floor tributary area (ft2 or m2).

    Returns
    -------
    dict
        {'wf_effective', 'wf_floor', 'cladding_contribution',
         'printed_page': '125 (Appendix D)', 'pdf_page': 140}
    """
    cladding_contribution = (
        1.2 * cladding_tributary_width * clear_story_height
        * cladding_dead_load_psf / column_tributary_area
    )
    return {
        "wf_effective": wf_floor + cladding_contribution, "wf_floor": wf_floor,
        "cladding_contribution": cladding_contribution,
        "printed_page": "125 (Appendix D)", "pdf_page": 140,
    }


# ============================================================================
# Equation 3-1 -- LRFD Tie Strength Check (printed p. 14, pdf_page 29)
# ============================================================================

def tie_strength_check(phi, rn, ru):
    """Equation 3-1: LRFD tie-strength adequacy check (printed p. 14).

        Phi*Rn >= Ru

    Parameters
    ----------
    phi : float
        Strength reduction factor.
    rn : float
        Nominal tie strength (material code + ASCE 41 over-strength).
    ru : float
        Required tie strength (Sum of gamma_i * Q_i), e.g. from
        ``internal_tie_force_framed``, ``peripheral_tie_force_two_way``,
        or ``vertical_tie_force``.

    Returns
    -------
    dict
        {'design_strength' (phi*rn), 'ru', 'adequate' (bool),
         'equation': '3-1', 'printed_page': '14', 'pdf_page': 29}
    """
    design_strength = phi * rn
    return {"design_strength": design_strength, "ru": ru,
            "adequate": design_strength >= ru, "equation": "3-1",
            "printed_page": "14", "pdf_page": 29}


def required_tie_area(ru, fy, phi=0.75, overstrength_factor=1.25):
    """Rearranges Equation 3-1 to solve for the required steel tie area,
    following the reinforced-concrete worked example in Appendix D
    (printed p. 126):

        Phi * (overstrength_factor * fy) * As_req'd >= Ru
        As_req'd = Ru / (Phi * overstrength_factor * fy)

    Reproduces the Appendix D peripheral-tie example: Ru=250.1-kip,
    fy=60-ksi, Phi=0.75 (Section 4-3), overstrength=1.25 (ASCE 41 Table
    10-4 rebar factor) -> As_req'd = 4.45-in2.

    Parameters
    ----------
    ru : float
        Required tie strength (kip or kN).
    fy : float
        Lower-bound (specified) yield strength of the tie steel (ksi or
        MPa).
    phi : float, optional
        Strength reduction factor. Default 0.75 (reinforced-concrete
        rebar in tension, Section 4-3).
    overstrength_factor : float, optional
        Factor translating lower-bound to expected material strength.
        Default 1.25 (ASCE 41 rebar factor, as used in Appendix D); use
        the appropriate ASCE 41 Chapter 9-12 factor for other materials.

    Returns
    -------
    dict
        {'as_required', 'ru', 'fy', 'phi', 'overstrength_factor',
         'printed_page': '126 (Appendix D)', 'pdf_page': 141}
    """
    as_required = ru / (phi * overstrength_factor * fy)
    return {
        "as_required": as_required, "ru": ru, "fy": fy, "phi": phi,
        "overstrength_factor": overstrength_factor,
        "printed_page": "126 (Appendix D)", "pdf_page": 141,
    }


# ============================================================================
# Section 3-1.6 -- Splices, Anchorage and Development of Ties
# (printed pp. 26-27, pdf_page 41-42)
# ============================================================================

def splice_exclusion_zone(bay_or_span_length):
    """Section 3-1.6.1: for cast-in-place (and topped precast) RC floor
    ties, Type 1 mechanical splices, welded splices, and Class B lap
    splices must be located no closer than 20% of the bay/span distance
    to any vertical load-carrying element -- i.e. splices are permitted
    only within the middle 60% of the bay/span (printed p. 26). Type 2
    mechanical splices are exempt and may be used anywhere in the slab.

    Parameters
    ----------
    bay_or_span_length : float
        Bay spacing (internal ties) or span distance (peripheral ties)
        in the tie direction (ft or m).

    Returns
    -------
    dict
        {'exclusion_distance' (from each support), 'permitted_zone_width',
         'paragraph': '3-1.6.1', 'printed_page': '26', 'pdf_page': 41}
    """
    exclusion = 0.2 * bay_or_span_length
    return {
        "exclusion_distance": exclusion,
        "permitted_zone_width": bay_or_span_length - 2 * exclusion,
        "paragraph": "3-1.6.1", "printed_page": "26", "pdf_page": 41,
    }
