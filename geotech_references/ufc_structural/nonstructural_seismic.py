"""UFC 3-301-01 Appendix C -- Guidance for Seismic Design of Nonstructural
Components (printed pp. 127-148, pdf_page 148-169).

Tables C-1/C-2/C-3 (maximum span for rigid pipe under pinned-pinned,
fixed-pinned, and fixed-fixed support conditions, printed pp. 138-140) with
the underlying rigid-pipe period equation (Eq C-1, printed p. 137), and the
printed numeric seismic-design criteria for pipe systems, elevators,
counterweight brackets, and nonrigid partitions that appear throughout this
appendix's otherwise-narrative guidance.

Span values in Tables C-1/C-2/C-3 are given in feet-inches as printed
(e.g. "7'-0''"); ``table_c1_pipe_span`` etc. return the printed string AND
a decimal-feet float for calculation convenience.
"""

import re


def _parse_feet_inches(s):
    """Parses a printed "F'-I''" span string to decimal feet."""
    m = re.match(r"(\d+)'-\s*(\d+)''", s.strip())
    if not m:
        raise ValueError(f"Cannot parse feet-inches string {s!r}")
    feet, inches = int(m.group(1)), int(m.group(2))
    return feet + inches / 12.0


# ============================================================================
# Eq C-1 -- rigid-pipe fundamental period (printed p. 137, pdf_page 158)
# ============================================================================

PIPE_PERIOD_CONSTANTS = {
    "pinned_pinned": 0.50,
    "fixed_pinned": 0.78,
    "fixed_fixed": 1.125,
}


def rigid_pipe_period_constant(support_condition):
    """Eq C-1 period constant, C, by pipe support condition (printed p. 137,
    excerpted from the Shock and Vibration Handbook, 6th Ed., 2009).

    Parameters
    ----------
    support_condition : str
        'pinned_pinned', 'fixed_pinned', or 'fixed_fixed'.

    Returns
    -------
    dict
        {'support_condition', 'period_constant', 'equation': 'C-1',
         'printed_page': '137', 'pdf_page': 158}
    """
    key = support_condition.lower().strip()
    if key not in PIPE_PERIOD_CONSTANTS:
        raise ValueError(f"support_condition must be one of {sorted(PIPE_PERIOD_CONSTANTS)}, got {support_condition!r}")
    return {"support_condition": key, "period_constant": PIPE_PERIOD_CONSTANTS[key],
            "equation": "C-1", "printed_page": "137", "pdf_page": 158}


def rigid_pipe_fundamental_period(support_condition, length, ei, w):
    """Eq C-1: fundamental period of a pipe span (printed p. 137).

        Ta = C * L * sqrt(w / (EI * g))

    where g is the acceleration of gravity. A pipe is "rigid" per Section
    C-3.1.3.2.1 if Ta <= 0.06 second (ASCE 7-22 Section 11.2 "Component,
    rigid" definition); Tables C-1/C-2/C-3 tabulate the span L that
    produces exactly Ta = 0.06 s for standard pipe/tube sizes.

    Parameters
    ----------
    support_condition : str
        'pinned_pinned', 'fixed_pinned', or 'fixed_fixed'.
    length : float
        Pipe span, L (in. or mm, consistent with `ei`/`w`).
    ei : float
        Flexural rigidity, E*I (consistent units).
    w : float
        Weight of pipe and contents per unit length (lb/in. or N/mm).

    Returns
    -------
    dict
        {'support_condition', 'period_constant', 'length', 'ta_seconds',
         'is_rigid' (bool, Ta <= 0.06 s), 'equation': 'C-1',
         'printed_page': '137', 'pdf_page': 158}
    """
    import math
    c = rigid_pipe_period_constant(support_condition)["period_constant"]
    g = 386.4  # in/s^2 (consistent with in./lb unit convention used by the source tables)
    ta = c * length * math.sqrt(w / (ei * g))
    return {
        "support_condition": support_condition.lower().strip(), "period_constant": c,
        "length": length, "ta_seconds": ta, "is_rigid": ta <= 0.06,
        "equation": "C-1", "printed_page": "137", "pdf_page": 158,
    }


# ============================================================================
# Tables C-1, C-2, C-3 -- Maximum Span for Rigid Pipe (printed pp. 138-140,
# pdf_page 159-161). Values are for water-filled pipes with Ta = 0.06 s
# (Eq C-1).
# ============================================================================

# Each row: diameter (in) -> {pipe_type: "F'-I''" span string}
_PIPE_TYPES = (
    "std_wt_steel_40s", "ex_strong_steel_80s", "copper_tube_type_k",
    "copper_tube_type_l", "copper_tube_type_m", "red_brass_sps_copper",
)

TABLE_C1_PINNED_PINNED = {
    1: ("7'-0''", "7'-0''", "5'-5''", "5'-4''", "4'-11''", "5'-11''"),
    1.5: ("8'-5''", "8'-6''", "6'-5''", "6'-3''", "5'-12''", "7'-1''"),
    2: ("9'-4''", "9'-5''", "7'-3''", "7'-1''", "6'-10''", "7'-10''"),
    2.5: ("10'-3''", "10'-5''", "7'-11''", "7'-10''", "7'-5''", "8'-8''"),
    3: ("11'-3''", "11'-5''", "8'-8''", "8'-6''", "8'-1''", "9'-6''"),
    3.5: ("11'-12''", "12'-2''", "9'-3''", "9'-1''", "8'-8''", "10'-2''"),
    4: ("12'-8''", "12'-11''", "9'-10''", "9'-9''", "9'-5''", "10'-9''"),
    5: ("13'-11''", "14'-3''", "10'-11''", "10'-8''", "10'-4''", "11'-8''"),
    6: ("15'-1''", "15'-7''", "11'-12''", "11'-6''", "11'-2''", "12'-7''"),
    8: ("16'-12''", "17'-8''", None, None, None, None),
    10: ("18'-9''", "19'-4''", None, None, None, None),
    12: ("20'-1''", "20'-9''", None, None, None, None),
}

TABLE_C2_FIXED_PINNED = {
    1: ("8'-9''", "8'-10''", "6'-9''", "6'-8''", "6'-1''", "7'-5''"),
    1.5: ("10'-6''", "10'-7''", "7'-12''", "7'-10''", "7'-6''", "8'-10''"),
    2: ("11'-7''", "11'-9''", "9'-0''", "8'-10''", "8'-6''", "9'-9''"),
    2.5: ("12'-10''", "12'-12''", "9'-11''", "9'-9''", "9'-4''", "10'-9''"),
    3: ("14'-1''", "14'-3''", "10'-10''", "10'-7''", "10'-1''", "11'-10''"),
    3.5: ("14'-11''", "15'-3''", "11'-7''", "11'-4''", "10'-10''", "12'-8''"),
    4: ("15'-9''", "16'-1''", "12'-4''", "12'-2''", "11'-9''", "13'-5''"),
    5: ("17'-5''", "17'-10''", "13'-8''", "13'-3''", "12'-10''", "14'-7''"),
    6: ("18'-10''", "19'-5''", "14'-11''", "14'-5''", "13'-11''", "15'-8''"),
    8: ("21'-2''", "22'-0''", None, None, None, None),
    10: ("23'-5''", "24'-2''", None, None, None, None),
    12: ("25'-1''", "25'-11''", None, None, None, None),
}

TABLE_C3_FIXED_FIXED = {
    1: ("10'-7''", "10'-7''", "8'-1''", "7'-12''", "7'-4''", "8'-11''"),
    1.5: ("12'-7''", "12'-8''", "9'-7''", "9'-5''", "8'-12''", "10'-8''"),
    2: ("13'-11''", "14'-2''", "10'-10''", "10'-8''", "10'-2''", "11'-9''"),
    2.5: ("15'-5''", "15'-7''", "11'-11''", "11'-9''", "11'-2''", "12'-11''"),
    3: ("16'-11''", "17'-2''", "12'-12''", "12'-9''", "12'-1''", "14'-3''"),
    3.5: ("17'-12''", "18'-4''", "13'-11''", "13'-8''", "13'-1''", "15'-3''"),
    4: ("18'-11''", "19'-4''", "14'-9''", "14'-8''", "14'-2''", "16'-1''"),
    5: ("20'-11''", "21'-5''", "16'-5''", "15'-11''", "15'-5''", "17'-7''"),
    6: ("22'-7''", "23'-4''", "17'-12''", "17'-4''", "16'-9''", "18'-10''"),
    8: ("25'-6''", "26'-5''", None, None, None, None),
    10: ("28'-2''", "29'-0''", None, None, None, None),
    12: ("30'-2''", "31'-1''", None, None, None, None),
}

_PIPE_SPAN_TABLES = {
    "pinned_pinned": (TABLE_C1_PINNED_PINNED, "C-1", "138", 159, "Figure C-6"),
    "fixed_pinned": (TABLE_C2_FIXED_PINNED, "C-2", "139", 160, "Figure C-7"),
    "fixed_fixed": (TABLE_C3_FIXED_FIXED, "C-3", "140", 161, "Figure C-8"),
}


def _pipe_span_lookup(support_condition, diameter_in, pipe_type):
    table, table_id, printed_page, pdf_page, figure = _PIPE_SPAN_TABLES[support_condition]
    if diameter_in not in table:
        raise ValueError(f"diameter_in must be one of {sorted(table)}, got {diameter_in!r}")
    if pipe_type not in _PIPE_TYPES:
        raise ValueError(f"pipe_type must be one of {_PIPE_TYPES}, got {pipe_type!r}")
    idx = _PIPE_TYPES.index(pipe_type)
    span_str = table[diameter_in][idx]
    if span_str is None:
        raise ValueError(
            f"Table {table_id} has no entry for diameter {diameter_in} in. "
            f"pipe_type {pipe_type!r} (not tabulated above 6 in. for copper/brass)"
        )
    return {
        "support_condition": support_condition, "diameter_in": diameter_in,
        "pipe_type": pipe_type, "max_span": span_str,
        "max_span_ft": _parse_feet_inches(span_str), "table": table_id,
        "support_figure": figure, "printed_page": printed_page, "pdf_page": pdf_page,
    }


def table_c1_pipe_span(diameter_in, pipe_type):
    """Table C-1: maximum span for rigid pipe with pinned-pinned support
    conditions (Figure C-6), based on water-filled pipes at Ta = 0.06 s
    (printed p. 138).

    Parameters
    ----------
    diameter_in : float
        Nominal pipe/tube diameter in inches (a key of
        ``TABLE_C1_PINNED_PINNED``, e.g. 1, 1.5, 2, ..., 12).
    pipe_type : str
        One of 'std_wt_steel_40s', 'ex_strong_steel_80s',
        'copper_tube_type_k', 'copper_tube_type_l', 'copper_tube_type_m',
        'red_brass_sps_copper'.

    Returns
    -------
    dict
        {'diameter_in', 'pipe_type', 'max_span' (printed "F'-I''" string),
         'max_span_ft' (float), 'table': 'C-1', 'support_figure':
         'Figure C-6', 'printed_page': '138', 'pdf_page': 159}
    """
    return _pipe_span_lookup("pinned_pinned", diameter_in, pipe_type)


def table_c2_pipe_span(diameter_in, pipe_type):
    """Table C-2: maximum span for rigid pipe with fixed-pinned support
    conditions (Figure C-7) (printed p. 139). See ``table_c1_pipe_span``
    for parameter/return convention.
    """
    return _pipe_span_lookup("fixed_pinned", diameter_in, pipe_type)


def table_c3_pipe_span(diameter_in, pipe_type):
    """Table C-3: maximum span for rigid pipe with fixed-fixed support
    conditions (Figure C-8) (printed p. 140). See ``table_c1_pipe_span``
    for parameter/return convention.
    """
    return _pipe_span_lookup("fixed_fixed", diameter_in, pipe_type)


# ============================================================================
# Flexible/rigid piping system design factors (Section C-3.1.3.2, printed
# pp. 136-137, pdf_page 157-158)
# ============================================================================

def pipe_car_rpo_ratio(is_rigid):
    """Section C-3.1.3.2.1/2.2: the component-resonance-ductility-factor to
    component-strength-factor ratio, CAR/Rpo, used in ASCE 7-22 Eq 13.3-1
    for pipe seismic force calculation (printed pp. 137, 138).

    Parameters
    ----------
    is_rigid : bool
        True if the piping system's fundamental period <= 0.06 s (rigid,
        CAR/Rpo = 1.0); False if flexible (period > 0.06 s, CAR/Rpo = 2.5).

    Returns
    -------
    dict
        {'is_rigid', 'car_rpo_ratio', 'printed_page': '137, 138',
         'pdf_page': '158, 159'}
    """
    ratio = 1.0 if is_rigid else 2.5
    return {"is_rigid": is_rigid, "car_rpo_ratio": ratio,
            "printed_page": "137, 138", "pdf_page": "158, 159"}


def flexible_pipe_clearance_requirements():
    """Section C-3.1.3.2.2 [guidance]: minimum clearance requirements for
    flexible piping systems (printed pp. 137-138).

    Returns
    -------
    dict
        {'min_pipe_to_pipe_clearance_x_displacement': 4,
         'min_pipe_to_pipe_clearance_in': 4,
         'min_pipe_to_wall_clearance_x_displacement': 3,
         'min_pipe_to_wall_clearance_in': 3, 'printed_page': '137-138',
         'pdf_page': '158-159'}
    """
    return {
        "min_pipe_to_pipe_clearance_x_displacement": 4, "min_pipe_to_pipe_clearance_in": 4,
        "min_pipe_to_wall_clearance_x_displacement": 3, "min_pipe_to_wall_clearance_in": 3,
        "printed_page": "137-138", "pdf_page": "158-159",
    }


# ============================================================================
# Elevator, counterweight, and equipment seismic criteria
# (Section C-3.3, printed pp. 144-145, pdf_page 165-166)
# ============================================================================

def elevator_guide_rail_deflection_limits():
    """Section C-3.3 [guidance]: maximum horizontal deflection of elevator
    guide rails (between supports) and of their support brackets (printed
    p. 144).

    Returns
    -------
    dict
        {'guide_rail_max_deflection_in': 0.5,
         'bracket_max_deflection_in': 0.25, 'printed_page': '144',
         'pdf_page': 165}
    """
    return {"guide_rail_max_deflection_in": 0.5, "bracket_max_deflection_in": 0.25,
            "printed_page": "144", "pdf_page": 165}


def elevator_retainer_plate_clearance():
    """Section C-3.3 [guidance]: for SDC D/E/F, maximum clearance between
    the machined faces of elevator guide rail and retainer plates (printed
    p. 145).

    Returns
    -------
    dict
        {'max_clearance_in': 0.1875, 'printed_page': '145', 'pdf_page': 166}
    """
    return {"max_clearance_in": 3.0 / 16.0, "printed_page": "145", "pdf_page": 166}


def counterweight_tie_bracket_spacing():
    """Section C-3.3 [guidance]: for SDC D/E/F, maximum counterweight rail
    tie-bracket spacing tied to the building structure, and the
    intermediate-spreader-bracket thresholds (printed p. 145).

    Returns
    -------
    dict
        {'max_tie_bracket_spacing_ft': 16,
         'one_spreader_bracket_above_spacing_ft': 10,
         'two_spreader_brackets_above_spacing_ft': 14, 'printed_page': '145',
         'pdf_page': 166}
    """
    return {
        "max_tie_bracket_spacing_ft": 16,
        "one_spreader_bracket_above_spacing_ft": 10,
        "two_spreader_brackets_above_spacing_ft": 14,
        "printed_page": "145", "pdf_page": 166,
    }


def elevator_equipment_car_rpo_ratio(is_rigid_and_rigidly_attached):
    """Section C-3.3 [guidance]: CAR/Rpo for elevator machinery and
    equipment (printed p. 145).

    Parameters
    ----------
    is_rigid_and_rigidly_attached : bool
        True for rigid/rigidly-attached equipment (CAR/Rpo = 1.0); False
        for non-rigid/flexibly-mounted equipment with period > 0.06 s
        (CAR/Rpo = 2.5).

    Returns
    -------
    dict
        {'is_rigid_and_rigidly_attached', 'car_rpo_ratio', 'printed_page':
         '145', 'pdf_page': 166}
    """
    ratio = 1.0 if is_rigid_and_rigidly_attached else 2.5
    return {"is_rigid_and_rigidly_attached": is_rigid_and_rigidly_attached,
            "car_rpo_ratio": ratio, "printed_page": "145", "pdf_page": 166}


# ============================================================================
# Nonrigid partition wall in-plane drift capacity (printed p. 132,
# pdf_page 153)
# ============================================================================

def nonrigid_partition_drift_capacity():
    """Section C-2.2 [guidance]: assumed in-plane story-drift capacity of a
    standard-practice nonrigid partition wall (stud-and-drywall,
    stud-and-plaster, movable partitions) before damage occurs (printed
    p. 132). Much less than the most restrictive ASCE 7-22 Table 12.12-1
    story-drift limit -- damage should be expected unless the partition is
    isolated from in-plane building motion.

    Returns
    -------
    dict
        {'drift_capacity_ratio': 0.005, 'drift_capacity_in_per_ft': 1/16.0,
         'printed_page': '132', 'pdf_page': 153}
    """
    return {"drift_capacity_ratio": 0.005, "drift_capacity_in_per_ft": 1.0 / 16.0,
            "printed_page": "132", "pdf_page": 153}


# ============================================================================
# Certification testing out-of-plane response threshold
# (Appendix D, printed p. 150, pdf_page 171)
# ============================================================================

def certification_out_of_plane_response_threshold():
    """Appendix D [guidance]: the out-of-plane-to-in-plane response ratio
    threshold used to decide whether ICC-ES AC156 shake-table qualification
    testing must be triaxial (significant cross-coupling) or may be biaxial
    (printed p. 150).

    Returns
    -------
    dict
        {'threshold_ratio': 0.20, 'above_threshold': 'triaxial simultaneous phase-incoherent testing required',
         'below_threshold': 'biaxial testing permitted (one horizontal + vertical, both horizontal directions)',
         'printed_page': '150', 'pdf_page': 171}
    """
    return {
        "threshold_ratio": 0.20,
        "above_threshold": "triaxial simultaneous phase-incoherent testing required",
        "below_threshold": "biaxial testing permitted (one horizontal + vertical, both horizontal directions)",
        "printed_page": "150", "pdf_page": 171,
    }
