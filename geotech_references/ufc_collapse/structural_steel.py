"""UFC 4-023-03 Chapter 5 -- Structural Steel (printed pp. 67-70,
pdf_page 82-85), plus Appendix C Table C-1 -- Steel Frame Beam-to-Column
Connection Types (printed p. 111, pdf_page 126).

Material properties and Phi point to ASCE 41 Table 9-3 and AISC 360,
respectively (Sections 5-1, 5-2) -- not reprinted here. The Alternate Path
acceptance criteria mostly follow ASCE 41 Chapter 9 Life-Safety values
(Section 5-4.3) EXCEPT: (1) beams in flexure or flexure+axial-tension use
Collapse Prevention values, and (2) the Fully/Partially Restrained
connections in this UFC's OWN Tables 5-1 (linear m-factors) and 5-2
(nonlinear modeling parameters), which this module digitizes in full.

CROSS-DOCUMENT NOTE (lead adjudication, 2026-09-04): GSA Alternate Path
2016 (gsa_collapse module) prints DIFFERENT linear m-factors for 3 of 4
fully-restrained connection types and the Double Split Tee limit states,
while the NONLINEAR tables (5-2 vs GSA Table 11) match exactly. Both
modules were visually verified against their own printed pages — this is
genuine divergence between the documents, not a transcription error.
Use the module matching your governing document.
"""


# ============================================================================
# Section 5-4.3 -- Columns Under High Axial Load (printed p. 68,
# pdf_page 83)
# ============================================================================

def column_axial_classification(p, p_cl):
    """Section 5-4.3: classifies a steel column's P-M interaction as
    force- or deformation-controlled based on the axial-load ratio
    P/PCL (printed p. 68).

    P/PCL > 0.5: FORCE-controlled (both P and M taken at their maximum
    analysis values; the P-M interaction equation must not exceed unity).
    P/PCL <= 0.5: the interaction equation is used with M as
    DEFORMATION-controlled and P as FORCE-controlled.

    Parameters
    ----------
    p : float
        Axial load from the analysis (kip or kN).
    p_cl : float
        Lower-bound axial compressive strength, PCL (kip or kN).

    Returns
    -------
    dict
        {'p_over_pcl', 'classification' ('force_controlled' or
        'interaction_p_force_m_deformation'), 'paragraph': '5-4.3',
        'printed_page': '68', 'pdf_page': 83}
    """
    ratio = p / p_cl
    classification = "force_controlled" if ratio > 0.5 else "interaction_p_force_m_deformation"
    return {"p_over_pcl": ratio, "classification": classification,
            "paragraph": "5-4.3", "printed_page": "68", "pdf_page": 83}


# ============================================================================
# Table 5-1 -- Acceptance Criteria for Linear Static Modeling of Steel
# Frame Connections (printed p. 69, pdf_page 84)
# ============================================================================

# Fully Restrained connections: m-factor = c0 - c1*d (d = beam depth, in.)
_TABLE_5_1_FR = {
    "improved_wuf_bolted_web": {"primary": (2.3, 0.021), "secondary": (4.9, 0.048)},
    "reduced_beam_section": {"primary": (4.9, 0.025), "secondary": (6.5, 0.025)},
    "wuf": {"primary": (4.3, 0.083), "secondary": (4.3, 0.048)},
    "sideplate": {"primary": (6.7, 0.039), "secondary": (11.1, 0.062)},
}

# Partially Restrained (Relatively Stiff): constant m-factors
_TABLE_5_1_PR_STIFF = {
    ("double_split_tee", "shear_in_bolt"): {"primary": 4, "secondary": 6},
    ("double_split_tee", "tension_in_bolt"): {"primary": 1.5, "secondary": 4},
    ("double_split_tee", "tension_in_tee"): {"primary": 1.5, "secondary": 4},
    ("double_split_tee", "flexure_in_tee"): {"primary": 5, "secondary": 7},
}

# Partially Restrained (Flexible): m-factor = c0 - c1*dbg (dbg = bolt group depth, in.)
_TABLE_5_1_PR_FLEXIBLE = {
    ("double_angles", "shear_in_bolt"): {"primary": (5.8, 0.107), "secondary": (8.7, 0.161)},
    ("double_angles", "tension_in_bolt"): {"primary": (1.5, 0.0), "secondary": (4.0, 0.0)},
    ("double_angles", "flexure_in_angles"): {"primary": (8.9, 0.193), "secondary": (13.0, 0.290)},
    ("simple_shear_tab", None): {"primary": (5.8, 0.107), "secondary": (8.7, 0.161)},
}


def _linear_in_depth(terms, depth, depth_name, source, quantity):
    """Evaluate printed c0 - c1 * depth expressions (depth in inches).

    Refuses a depth that is not positive. An entry whose printed
    expression is zero or negative at this depth is returned as None, with
    a note naming the entry, the expression and the depths at which it is
    positive: the table prints no such m-factor or plastic rotation there,
    the straight line has run past where it applies. The row's other
    entries are returned as printed. Refuses the call only when every
    entry of the row is zero or negative.

    Returns ``(values, notes)``: each entry's value or None, and a list of
    notes.
    """
    if depth <= 0:
        raise ValueError(f"{source}: {depth_name} must be a positive depth in inches, got {depth!r}")
    out, notes = {}, []
    for name, (c0, c1) in terms.items():
        value = c0 - c1 * depth
        if value > 0:
            out[name] = value
            continue
        out[name] = None
        where = (f"positive only for {depth_name} < {c0 / c1:.1f} in" if c1 > 0
                 else "not positive at any depth")
        notes.append(
            f"{name} is None: the printed expression {c0} - {c1} {depth_name} is "
            f"{value:.4g} at {depth_name} = {depth} in, not a positive {quantity}; it is "
            f"{where}, and the table gives no {quantity} beyond that.")
    if all(v is None for v in out.values()):
        raise ValueError(
            f"{source}: no entry of this row is a positive {quantity} at "
            f"{depth_name} = {depth} in. " + " ".join(notes) +
            f" {depth_name} is in inches (table footnote).")
    return out, notes


def _m_below_one_note(m, depth_name, depth, notes=()):
    """The result's 'note': the entries a printed expression gives no
    positive value for (``notes``), and any m-factor below 1."""
    notes = list(notes)
    low = [k for k in ("m_primary", "m_secondary") if m[k] is not None and m[k] < 1]
    if low:
        notes.append(f"{' and '.join(low)} below 1 at {depth_name} = {depth} in: the "
                     f"printed expression gives it and the table prints no lower "
                     f"limit; check that {depth_name} is in inches.")
    return {"note": " ".join(notes)} if notes else {}


def table_5_1_fr_connection_mfactor(connection_type, d):
    """UFC 4-023-03 Table 5-1, Fully Restrained Moment Connections:
    linear-model m-factors (dimensionless), primary and secondary, printed
    as c0 - c1 d with d the beam depth in INCHES (footnote 2)
    (printed p. 69).
    An entry whose printed expression is zero or negative at that depth
    is returned as None, with a note naming it and the depths at which
    it is positive (the table prints no such m-factor there); the call is
    refused only when every entry of the row is. An m below 1
    is returned with a note (the table prints no lower limit).

    Parameters
    ----------
    connection_type : str
        One of 'improved_wuf_bolted_web', 'reduced_beam_section', 'wuf',
        'sideplate'.
    d : float
        Beam depth in inches (footnote 2: "d = depth of beam,
        inch"); a depth in mm or cm gives wrong m-factors.

    Returns
    -------
    dict
        {'m_primary', 'm_secondary' (None where the printed expression
         is zero or negative at d), 'connection_type', 'd', 'd_units':
         'in', 'table': '5-1', 'printed_page': '69', 'pdf_page': 84},
        plus 'note' when an entry is None or an m-factor is below 1.

    Raises
    ------
    ValueError
        Unknown connection_type, d <= 0, or a d at which every printed
        expression of the row is <= 0 (e.g. 'wuf' beyond its zero depth).
    """
    key = connection_type.lower().strip()
    if key not in _TABLE_5_1_FR:
        raise ValueError(f"connection_type must be one of {sorted(_TABLE_5_1_FR)}, got {connection_type!r}")
    row = _TABLE_5_1_FR[key]
    m, notes = _linear_in_depth({"m_primary": row["primary"], "m_secondary": row["secondary"]},
                         d, "d", "UFC 4-023-03 Table 5-1 (printed p. 69)", "m-factor")
    return {"m_primary": m["m_primary"], "m_secondary": m["m_secondary"],
            "connection_type": key, "d": d, "d_units": "in", "table": "5-1",
            "printed_page": "69", "pdf_page": 84, **_m_below_one_note(m, "d", d, notes)}


def table_5_1_pr_stiff_connection_mfactor(connection_type, limit_state):
    """Table 5-1, Partially Restrained Moment Connections (Relatively
    Stiff): constant linear-model m-factors by limit state (printed
    p. 69).

    Parameters
    ----------
    connection_type : str
        'double_split_tee'.
    limit_state : str
        'shear_in_bolt', 'tension_in_bolt', 'tension_in_tee', or
        'flexure_in_tee'.

    Returns
    -------
    dict
        {'m_primary', 'm_secondary', 'connection_type', 'limit_state',
         'table': '5-1', 'printed_page': '69', 'pdf_page': 84}
    """
    key = (connection_type.lower().strip(), limit_state.lower().strip())
    if key not in _TABLE_5_1_PR_STIFF:
        raise ValueError(f"No Table 5-1 row for {key}; valid: {sorted(_TABLE_5_1_PR_STIFF)}")
    row = _TABLE_5_1_PR_STIFF[key]
    return {"m_primary": row["primary"], "m_secondary": row["secondary"],
            "connection_type": key[0], "limit_state": key[1], "table": "5-1",
            "printed_page": "69", "pdf_page": 84}


def table_5_1_pr_flexible_connection_mfactor(connection_type, dbg, limit_state=None):
    """UFC 4-023-03 Table 5-1: linear-model m-factors (dimensionless),
    primary and secondary, for Partially Restrained Simple Connections (Flexible),
    printed as constants or as c0 - c1 dbg with dbg the bolt-group depth
    in INCHES (footnote 3) (printed p. 69).
    An entry whose printed expression is zero or negative at that depth
    is returned as None, with a note naming it and the depths at which
    it is positive (the table prints no such m-factor there); the call is
    refused only when every entry of the row is. An m below 1 is
    returned with a note (the table prints no lower limit).

    Parameters
    ----------
    connection_type : str
        'double_angles' (requires limit_state) or 'simple_shear_tab'.
    dbg : float
        Depth of the bolt group in inches (footnote 3: "dbg = depth
        of bolt group, inch"); a depth in mm or cm gives wrong
        m-factors.
    limit_state : str, optional
        For 'double_angles': 'shear_in_bolt', 'tension_in_bolt', or
        'flexure_in_angles'. Not used for 'simple_shear_tab'.

    Returns
    -------
    dict
        {'m_primary', 'm_secondary', 'connection_type', 'limit_state',
         'dbg', 'dbg_units': 'in', 'table': '5-1', 'printed_page': '69',
         'pdf_page': 84}; an m-factor is None where its printed
        expression is zero or negative at dbg; plus 'note' when an
        entry is None or an m-factor is below 1.

    Raises
    ------
    ValueError
        Unknown row, dbg <= 0, or a dbg at which every printed
        expression of the row is <= 0.
    """
    conn = connection_type.lower().strip()
    ls = limit_state.lower().strip() if limit_state else None
    key = (conn, ls) if conn == "double_angles" else (conn, None)
    if key not in _TABLE_5_1_PR_FLEXIBLE:
        raise ValueError(f"No Table 5-1 row for {key}; valid: {sorted(_TABLE_5_1_PR_FLEXIBLE)}")
    row = _TABLE_5_1_PR_FLEXIBLE[key]
    m, notes = _linear_in_depth({"m_primary": row["primary"], "m_secondary": row["secondary"]},
                         dbg, "dbg", "UFC 4-023-03 Table 5-1 (printed p. 69)", "m-factor")
    return {"m_primary": m["m_primary"], "m_secondary": m["m_secondary"],
            "connection_type": conn, "limit_state": ls, "dbg": dbg, "dbg_units": "in",
            "table": "5-1", "printed_page": "69", "pdf_page": 84,
            **_m_below_one_note(m, "dbg", dbg, notes)}


# ============================================================================
# Table 5-2 -- Modeling Parameters and Acceptance Criteria for Nonlinear
# Modeling of Steel Frame Connections (printed p. 70, pdf_page 85)
# ============================================================================

# Fully Restrained: (a0,a1), (b0,b1) each as c0 - c1*d; c is a constant.
_TABLE_5_2_FR = {
    "improved_wuf_bolted_web": {"a": (0.021, 0.0003), "b": (0.050, 0.0006), "c": 0.2},
    "reduced_beam_section": {"a": (0.050, 0.0003), "b": (0.070, 0.0003), "c": 0.2},
    "wuf": {"a": (0.0284, 0.0004), "b": (0.043, 0.0006), "c": 0.2},
    "sideplate": {"a": (0.089, 0.0005), "b": (0.169, 0.0001), "c": 0.6},
}

_TABLE_5_2_PR_STIFF = {
    ("double_split_tee", "shear_in_bolt"): {"a": 0.036, "b": 0.048, "c": 0.2, "primary": 0.03, "secondary": 0.040},
    ("double_split_tee", "tension_in_bolt"): {"a": 0.016, "b": 0.024, "c": 0.8, "primary": 0.013, "secondary": 0.020},
    ("double_split_tee", "tension_in_tee"): {"a": 0.012, "b": 0.018, "c": 0.8, "primary": 0.010, "secondary": 0.015},
    ("double_split_tee", "flexure_in_tee"): {"a": 0.042, "b": 0.084, "c": 0.2, "primary": 0.035, "secondary": 0.070},
}

# Flexible PR: a/b/primary/secondary are c0 - c1*dbg; c is a constant.
_TABLE_5_2_PR_FLEXIBLE = {
    ("double_angles", "shear_in_bolt"): {
        "a": (0.0502, 0.0015), "b": (0.072, 0.0022), "c": 0.2,
        "primary": (0.0502, 0.0015), "secondary": (0.0503, 0.0011),
    },
    ("double_angles", "tension_in_bolt"): {
        "a": (0.0502, 0.0015), "b": (0.072, 0.0022), "c": 0.2,
        "primary": (0.0502, 0.0015), "secondary": (0.0503, 0.0011),
    },
    ("double_angles", "flexure_in_angles"): {
        "a": (0.1125, 0.0027), "b": (0.150, 0.0036), "c": 0.4,
        "primary": (0.1125, 0.0027), "secondary": (0.150, 0.0036),
    },
    ("simple_shear_tab", None): {
        "a": (0.0502, 0.0015), "b": (0.1125, 0.0027), "c": 0.2,
        "primary": (0.0502, 0.0015), "secondary": (0.1125, 0.0027),
    },
}


def table_5_2_fr_connection_modeling(connection_type, d):
    """UFC 4-023-03 Table 5-2, Fully Restrained Moment Connections:
    nonlinear modeling parameters a, b (plastic rotation, radians) and c
    (residual strength ratio), and the acceptance-criteria plastic
    rotations (radians; printed equal to a and b), with a and b printed as
    c0 - c1 d and d the beam depth in INCHES (footnote 3) (printed
    p. 70).
    An entry whose printed expression is zero or negative at that depth
    is returned as None, with a note naming it and the depths at which
    it is positive (the table prints no such plastic rotation there); the call is
    refused only when every entry of the row is.

    Parameters
    ----------
    connection_type : str
        One of 'improved_wuf_bolted_web', 'reduced_beam_section', 'wuf',
        'sideplate'.
    d : float
        Beam depth in inches (footnote 3: "d = depth of beam, inch");
        a depth in mm or cm gives wrong rotations.

    Returns
    -------
    dict
        {'a', 'b', 'c', 'primary_acceptance' (=a), 'secondary_acceptance'
        (=b), 'connection_type', 'd', 'd_units': 'in', 'table': '5-2',
        'printed_page': '70', 'pdf_page': 85}; a or b (and its
        acceptance) is None where its printed expression is zero or
        negative at d, with a 'note'.

    Raises
    ------
    ValueError
        Unknown connection_type, d <= 0, or a d at which both a and b are <= 0.
    """
    key = connection_type.lower().strip()
    if key not in _TABLE_5_2_FR:
        raise ValueError(f"connection_type must be one of {sorted(_TABLE_5_2_FR)}, got {connection_type!r}")
    row = _TABLE_5_2_FR[key]
    v, notes = _linear_in_depth({"a": row["a"], "b": row["b"]}, d, "d",
                         "UFC 4-023-03 Table 5-2 (printed p. 70)",
                         "plastic rotation")
    a, b = v["a"], v["b"]
    return {"a": a, "b": b, "c": row["c"], "primary_acceptance": a,
            "secondary_acceptance": b, "connection_type": key, "d": d,
            "d_units": "in", "table": "5-2", "printed_page": "70", "pdf_page": 85,
            **({"note": " ".join(notes)} if notes else {})}


def table_5_2_pr_stiff_connection_modeling(connection_type, limit_state):
    """Table 5-2, Partially Restrained Moment Connections (Relatively
    Stiff): constant nonlinear modeling parameters and acceptance
    criteria by limit state (printed p. 70).

    Parameters
    ----------
    connection_type : str
        'double_split_tee'.
    limit_state : str
        'shear_in_bolt', 'tension_in_bolt', 'tension_in_tee', or
        'flexure_in_tee'.

    Returns
    -------
    dict
        {'a', 'b', 'c', 'primary_acceptance', 'secondary_acceptance',
         'connection_type', 'limit_state', 'table': '5-2',
         'printed_page': '70', 'pdf_page': 85}
    """
    key = (connection_type.lower().strip(), limit_state.lower().strip())
    if key not in _TABLE_5_2_PR_STIFF:
        raise ValueError(f"No Table 5-2 row for {key}; valid: {sorted(_TABLE_5_2_PR_STIFF)}")
    row = _TABLE_5_2_PR_STIFF[key]
    return {"a": row["a"], "b": row["b"], "c": row["c"],
            "primary_acceptance": row["primary"], "secondary_acceptance": row["secondary"],
            "connection_type": key[0], "limit_state": key[1], "table": "5-2",
            "printed_page": "70", "pdf_page": 85}


def table_5_2_pr_flexible_connection_modeling(connection_type, dbg, limit_state=None):
    """UFC 4-023-03 Table 5-2: nonlinear modeling parameters a, b
    (plastic rotation, radians) and c, and the acceptance-criteria plastic
    rotations (radians, primary and secondary), for
    Partially Restrained Simple Connections (Flexible), printed as c0 - c1 dbg with dbg
    the bolt-group depth in INCHES (footnote 4) (printed p. 70).
    An entry whose printed expression is zero or negative at that depth
    is returned as None, with a note naming it and the depths at which
    it is positive (the table prints no such rotation there); the call is
    refused only when every entry of the row is.

    Parameters
    ----------
    connection_type : str
        'double_angles' (requires limit_state) or 'simple_shear_tab'.
    dbg : float
        Depth of the bolt group in inches (footnote 4: "dbg = depth
        of bolt group, inch"); a depth in mm or cm gives wrong rotations.
    limit_state : str, optional
        For 'double_angles': 'shear_in_bolt', 'tension_in_bolt', or
        'flexure_in_angles'.

    Returns
    -------
    dict
        {'a', 'b', 'c', 'primary_acceptance', 'secondary_acceptance',
         'connection_type', 'limit_state', 'dbg', 'dbg_units': 'in',
         'table': '5-2', 'printed_page': '70', 'pdf_page': 85}; an
         entry is None where its printed expression is zero or negative
         at dbg, with a 'note'.

    Raises
    ------
    ValueError
        Unknown row, dbg <= 0, or a dbg at which every printed
        expression of the row is <= 0.
    """
    conn = connection_type.lower().strip()
    ls = limit_state.lower().strip() if limit_state else None
    key = (conn, ls) if conn == "double_angles" else (conn, None)
    if key not in _TABLE_5_2_PR_FLEXIBLE:
        raise ValueError(f"No Table 5-2 row for {key}; valid: {sorted(_TABLE_5_2_PR_FLEXIBLE)}")
    row = _TABLE_5_2_PR_FLEXIBLE[key]
    v, notes = _linear_in_depth({"a": row["a"], "b": row["b"], "primary_acceptance": row["primary"],
                          "secondary_acceptance": row["secondary"]},
                         dbg, "dbg", "UFC 4-023-03 Table 5-2 (printed p. 70)",
                         "plastic rotation")
    return {"a": v["a"], "b": v["b"], "c": row["c"],
            "primary_acceptance": v["primary_acceptance"],
            "secondary_acceptance": v["secondary_acceptance"], "connection_type": conn,
            "limit_state": ls, "dbg": dbg, "dbg_units": "in", "table": "5-2",
            "printed_page": "70", "pdf_page": 85,
            **({"note": " ".join(notes)} if notes else {})}


# ============================================================================
# Appendix C Table C-1 -- Steel Frame Beam-to-Column Connection Types
# (printed p. 111, pdf_page 126)
# ============================================================================

TABLE_C1_CONNECTION_TYPES = {
    "wuf": {
        "description": "Full-penetration welds between beams and columns flanges, bolted or welded web, designed prior to code changes following the Northridge earthquake.",
        "restraint": "FR", "figure": "C-8(a)",
    },
    "welded_flange_plates": {
        "description": "Flange plate with full-penetration weld at column and fillet welded to beam flange.",
        "restraint": "FR", "figure": "C-8(b)",
    },
    "welded_cover_plated_flanges": {
        "description": "Beam flange and cover-plate are welded to column flange.",
        "restraint": "FR", "figure": "C-8(c)",
    },
    "bolted_flange_plates": {
        "description": "Flange plate with full-penetration weld at column and field bolted to beam flange.",
        "restraint": "FR or PR", "figure": "C-8(d)",
    },
    "improved_wuf_bolted_web": {
        "description": "Full-penetration welds between beam and column flanges, bolted web, developed after Northridge Earthquake.",
        "restraint": "FR", "figure": "C-8(a)",
    },
    "improved_wuf_welded_web": {
        "description": "Full-penetration welds between beam and column flanges, welded web developed after Northridge Earthquake.",
        "restraint": "FR", "figure": "C-8(a)",
    },
    "free_flange": {
        "description": "Web is coped at ends of beam to separate flanges; welded web tab resists shear and bending moment due to eccentricity from the coped web, developed after Northridge Earthquake.",
        "restraint": "FR", "figure": "C-8(e)",
    },
    "welded_top_and_bottom_haunches": {
        "description": "Haunched connection at top and bottom flanges developed after Northridge Earthquake.",
        "restraint": "FR", "figure": "C-8(f)",
    },
    "reduced_beam_section": {
        "description": "Connection in which net area of beam flange is reduced to force plastic hinging away from column face, developed after Northridge Earthquake.",
        "restraint": "FR", "figure": "C-8(g)",
    },
    "top_and_bottom_clip_angles": {
        "description": "Clip angle bolted or riveted to beam flange and column flange.",
        "restraint": "PR", "figure": "C-9(a)",
    },
    "double_split_tee": {
        "description": "Split tees bolted or riveted to beam flange and column flange.",
        "restraint": "PR", "figure": "C-9(b)",
    },
    "composite_top_and_clip_angle_bottom": {
        "description": "Clip angle bolted or riveted to column flange and beam bottom flange with composite slab.",
        "restraint": "PR", "figure": "C-9(a) similar",
    },
    "bolted_end_plate": {
        "description": "Stiffened or unstiffened end plate welded to beam and bolted to column flange.",
        "restraint": "PR", "figure": "C-8(c)",
    },
    "shear_tab_connection": {
        "description": "Simple gravity connection with shear tab, may have composite floor deck.",
        "restraint": "PR", "figure": "C-8(d)",
    },
    "kaiser_bolted_bracket": {
        "description": "SMF moment connection with fastened cast-steel haunch brackets bolted to the column flange and either fillet-welded or bolted to both beam flanges.",
        "restraint": "FR", "figure": "C-11",
    },
    "sideplate": {
        "description": "SMF moment connection with full-depth side plates and fillet welds, developed following the 1994 Northridge earthquake.",
        "restraint": "FR", "figure": "C-12",
    },
    "slottedweb": {
        "description": "SMF moment connection similar to WUF with extended web slots at weld access holes, separating the beam flanges from the beam web in the connection region.",
        "restraint": "FR", "figure": "C-13",
    },
}


def table_c1_connection_type(connection_type):
    """Table C-1: steel frame beam-to-column connection-type inventory --
    description, Fully/Partially Restrained (FR/PR) classification, and
    illustrating figure (printed p. 111). This is a descriptive/
    classification inventory (Appendix C commentary); the corresponding
    numeric m-factors and modeling parameters, where this UFC specifies
    its own values, are in ``table_5_1_*``/``table_5_2_*`` above.

    Parameters
    ----------
    connection_type : str
        A key of ``TABLE_C1_CONNECTION_TYPES`` (e.g. 'reduced_beam_section',
        'shear_tab_connection').

    Returns
    -------
    dict
        The row data plus {'connection_type', 'table': 'C-1',
        'printed_page': '111', 'pdf_page': 126}.
    """
    key = connection_type.lower().strip()
    if key not in TABLE_C1_CONNECTION_TYPES:
        raise ValueError(f"connection_type must be one of {sorted(TABLE_C1_CONNECTION_TYPES)}, got {connection_type!r}")
    row = dict(TABLE_C1_CONNECTION_TYPES[key])
    row.update({"connection_type": key, "table": "C-1", "printed_page": "111", "pdf_page": 126})
    return row


def list_table_c1_connection_types(restraint=None):
    """Lists the connection-type keys in ``TABLE_C1_CONNECTION_TYPES``.

    Parameters
    ----------
    restraint : str, optional
        Filter to 'FR' or 'PR' (matches connections classified purely as
        that type; the one 'FR or PR' entry, bolted_flange_plates, is
        excluded from both filters -- request it directly by name).
        Default None (return all).

    Returns
    -------
    list of str
    """
    if restraint is None:
        return sorted(TABLE_C1_CONNECTION_TYPES)
    return sorted(k for k, v in TABLE_C1_CONNECTION_TYPES.items() if v["restraint"] == restraint.upper())
