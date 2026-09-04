"""GSA Alternate Path Analysis and Design Guidelines Chapter 5 --
Structural Steel (printed pp. 43-46, pdf_page 55-58), plus Appendix C
Table C1.1 -- Steel Frame Beam-to-Column Connection Types (printed p. C19,
pdf_page 95).

Chapter 5 of UFC 4-023-03 is adopted with two printed modifications
(Section 5, opening list): (1) modeling and acceptance criteria for
primary and secondary components are revised from Life Safety to COLLAPSE
PREVENTION, and (2) all Tie Force (Section 5.3) and Enhanced Local
Resistance (Section 5.5) references are REMOVED IN THEIR ENTIRETY. Steel
frame connections use this document's OWN Tables 10 (linear m-factors)
and 11 (nonlinear modeling parameters), which this module digitizes in
full, in place of the corresponding ASCE 41 Chapter 9 default values.

CROSS-DOCUMENT CONSISTENCY (verified against geotech_references.ufc_collapse
in tests/test_gsa_collapse_structural_steel.py, all confirmed by direct
visual comparison against the rendered PDF pages of both documents):
  - Table 11 (NONLINEAR modeling parameters, printed p. 46) is printed
    IDENTICALLY to UFC 4-023-03 Table 5-2 -- every Fully Restrained
    connection type AND every Partially Restrained (Relatively Stiff)
    Double Split Tee limit state matches exactly.
  - Table 10 (LINEAR m-factors, printed p. 45) has THREE CONFIRMED
    PRINTED VALUE DIFFERENCES from UFC 4-023-03 Table 5-1, for the Fully
    Restrained connections "Improved WUF with Bolted Web" (GSA:
    3.1-0.032d / 6.2-0.065d; ufc_collapse: 2.3-0.021d / 4.9-0.048d),
    "Reduced Beam Section" (GSA: 6.9-0.032d / 8.4-0.032d; ufc_collapse:
    4.9-0.025d / 6.5-0.025d), and "WUF" (GSA: 3.9-0.043d / 5.5-0.064d;
    ufc_collapse: 4.3-0.083d / 4.3-0.048d) -- PLUS all four Partially
    Restrained (Relatively Stiff) Double Split Tee limit states (GSA:
    shear-in-bolt 6/8, tension-in-bolt 2.5/4, tension-in-tee 2/2,
    flexure-in-tee 7/14; ufc_collapse: 4/6, 1.5/4, 1.5/4, 5/7). The
    SidePlate(R), Double Angles, and Simple Shear Tab rows of Table 10
    match ufc_collapse's Table 5-1 exactly. These are printed-value
    disagreements between the two documents as currently digitized in
    this repository -- reported here per this module's cross-check
    doctrine, NOT silently reconciled. Notably, the corresponding
    NONLINEAR table (Table 11/5-2) matches perfectly for every one of
    these same connection types, which argues against a simple edition-
    vintage explanation (one would expect a revision to touch both the
    linear and nonlinear values for a given connection type) -- this
    pattern is flagged explicitly for the lead's attention as worth an
    independent re-check of ufc_collapse's Table 5-1 digitization against
    its own source PDF. See ``tests/test_gsa_collapse_structural_steel.py``
    for the exact assertions (both the confirmed matches and the
    confirmed differences).
  - Table C1.1 (steel frame connection-type inventory, Appendix C,
    printed p. C19) matches UFC 4-023-03's Table C-1 in restraint
    classification (FR/PR) for all 17 connection types, and in
    description text for 13 of the 17 (page-verified against the
    rendered PDFs of both documents). FOUR rows are CONFIRMED printed
    WORDING differences, each transcribed here exactly as GSA prints it
    rather than silently adopting UFC's (generally more polished)
    wording for the same connection:
      - "Free Flange": GSA reads "...bending moment due to eccentricity
        due to coped web developed after Northridge Earthquake" (note
        the repeated "due to" and missing "the"/comma); UFC reads
        "...due to eccentricity from the coped web, developed...".
      - "Reduced Beam Section": GSA omits the comma before "developed"
        that UFC includes ("...away from column face developed..." vs
        "...column face, developed...").
      - "Kaiser Bolted Bracket(R)": GSA reads "cast steel" (two words)
        and "brackets that are bolted"; UFC reads "cast-steel" (hyphenated)
        and "brackets bolted".
      - "SlottedWeb(TM)": GSA reads "...weld access holes TO SEPARATING
        the beam flanges..." (grammatically awkward, but printed exactly
        this way) and "...in the region of the connection"; UFC reads
        "...weld access holes, separating the beam flanges..." and
        "...in the connection region".
"""


# ============================================================================
# Section 5.4.3 -- Columns Under High Axial Load (printed p. 43-44,
# pdf_page 55-56)
# ============================================================================

def column_axial_classification(p, p_cl):
    """Section 5.4.3: classifies a steel column's P-M interaction as
    force- or deformation-controlled based on the axial-load ratio P/PCL
    (printed pp. 43-44).

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
        'interaction_p_force_m_deformation'), 'section': '5.4.3',
        'printed_page': '43-44', 'pdf_page': '55-56'}
    """
    ratio = p / p_cl
    classification = "force_controlled" if ratio > 0.5 else "interaction_p_force_m_deformation"
    return {"p_over_pcl": ratio, "classification": classification,
            "section": "5.4.3", "printed_page": "43-44", "pdf_page": "55-56"}


# ============================================================================
# Table 10 -- Acceptance Criteria for Linear Static Modeling of Steel
# Frame Connections (printed p. 45, pdf_page 57)
# ============================================================================

# Fully Restrained connections: m-factor = c0 - c1*d (d = beam depth, in.)
# PAGE-VERIFIED against the rendered GSA source PDF (printed p. 45).
_TABLE_10_FR = {
    "improved_wuf_bolted_web": {"primary": (3.1, 0.032), "secondary": (6.2, 0.065)},
    "reduced_beam_section": {"primary": (6.9, 0.032), "secondary": (8.4, 0.032)},
    "wuf": {"primary": (3.9, 0.043), "secondary": (5.5, 0.064)},
    "sideplate": {"primary": (6.7, 0.039), "secondary": (11.1, 0.062)},
}

# Partially Restrained (Relatively Stiff): constant m-factors
_TABLE_10_PR_STIFF = {
    ("double_split_tee", "shear_in_bolt"): {"primary": 6, "secondary": 8},
    ("double_split_tee", "tension_in_bolt"): {"primary": 2.5, "secondary": 4},
    ("double_split_tee", "tension_in_tee"): {"primary": 2, "secondary": 2},
    ("double_split_tee", "flexure_in_tee"): {"primary": 7, "secondary": 14},
}

# Partially Restrained (Flexible): m-factor = c0 - c1*dbg (dbg = bolt group depth, in.)
_TABLE_10_PR_FLEXIBLE = {
    ("double_angles", "shear_in_bolt"): {"primary": (5.8, 0.107), "secondary": (8.7, 0.161)},
    ("double_angles", "tension_in_bolt"): {"primary": (1.5, 0.0), "secondary": (4.0, 0.0)},
    ("double_angles", "flexure_in_angles"): {"primary": (8.9, 0.193), "secondary": (13.0, 0.290)},
    ("simple_shear_tab", None): {"primary": (5.8, 0.107), "secondary": (8.7, 0.161)},
}


def table_10_fr_connection_mfactor(connection_type, d):
    """Table 10, Fully Restrained Moment Connections: linear-model
    m-factors as a function of beam depth d (printed p. 45).

    Parameters
    ----------
    connection_type : str
        One of 'improved_wuf_bolted_web', 'reduced_beam_section', 'wuf',
        'sideplate'.
    d : float
        Beam depth (inch).

    Returns
    -------
    dict
        {'m_primary', 'm_secondary', 'connection_type', 'd', 'table': '10',
         'printed_page': '45', 'pdf_page': 57}
    """
    key = connection_type.lower().strip()
    if key not in _TABLE_10_FR:
        raise ValueError(f"connection_type must be one of {sorted(_TABLE_10_FR)}, got {connection_type!r}")
    row = _TABLE_10_FR[key]
    m_primary = row["primary"][0] - row["primary"][1] * d
    m_secondary = row["secondary"][0] - row["secondary"][1] * d
    return {"m_primary": m_primary, "m_secondary": m_secondary,
            "connection_type": key, "d": d, "table": "10",
            "printed_page": "45", "pdf_page": 57}


def table_10_pr_stiff_connection_mfactor(connection_type, limit_state):
    """Table 10, Partially Restrained Moment Connections (Relatively
    Stiff): constant linear-model m-factors by limit state (printed
    p. 45).

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
         'table': '10', 'printed_page': '45', 'pdf_page': 57}
    """
    key = (connection_type.lower().strip(), limit_state.lower().strip())
    if key not in _TABLE_10_PR_STIFF:
        raise ValueError(f"No Table 10 row for {key}; valid: {sorted(_TABLE_10_PR_STIFF)}")
    row = _TABLE_10_PR_STIFF[key]
    return {"m_primary": row["primary"], "m_secondary": row["secondary"],
            "connection_type": key[0], "limit_state": key[1], "table": "10",
            "printed_page": "45", "pdf_page": 57}


def table_10_pr_flexible_connection_mfactor(connection_type, dbg, limit_state=None):
    """Table 10, Partially Restrained Simple/Moment Connections
    (Flexible): linear-model m-factors as a function of bolt-group depth
    dbg (printed p. 45).

    Parameters
    ----------
    connection_type : str
        'double_angles' (requires limit_state) or 'simple_shear_tab'.
    dbg : float
        Depth of the bolt group (inch).
    limit_state : str, optional
        For 'double_angles': 'shear_in_bolt', 'tension_in_bolt', or
        'flexure_in_angles'. Not used for 'simple_shear_tab'.

    Returns
    -------
    dict
        {'m_primary', 'm_secondary', 'connection_type', 'limit_state',
         'dbg', 'table': '10', 'printed_page': '45', 'pdf_page': 57}
    """
    conn = connection_type.lower().strip()
    ls = limit_state.lower().strip() if limit_state else None
    key = (conn, ls) if conn == "double_angles" else (conn, None)
    if key not in _TABLE_10_PR_FLEXIBLE:
        raise ValueError(f"No Table 10 row for {key}; valid: {sorted(_TABLE_10_PR_FLEXIBLE)}")
    row = _TABLE_10_PR_FLEXIBLE[key]
    m_primary = row["primary"][0] - row["primary"][1] * dbg
    m_secondary = row["secondary"][0] - row["secondary"][1] * dbg
    return {"m_primary": m_primary, "m_secondary": m_secondary,
            "connection_type": conn, "limit_state": ls, "dbg": dbg,
            "table": "10", "printed_page": "45", "pdf_page": 57}


# ============================================================================
# Table 11 -- Modeling Parameters and Acceptance Criteria for Nonlinear
# Modeling of Steel Frame Connections (printed p. 46, pdf_page 58)
# ============================================================================

# Fully Restrained: (a0,a1), (b0,b1) each as c0 - c1*d; c is a constant.
_TABLE_11_FR = {
    "improved_wuf_bolted_web": {"a": (0.021, 0.0003), "b": (0.050, 0.0006), "c": 0.2},
    "reduced_beam_section": {"a": (0.050, 0.0003), "b": (0.070, 0.0003), "c": 0.2},
    "wuf": {"a": (0.0284, 0.0004), "b": (0.043, 0.0006), "c": 0.2},
    "sideplate": {"a": (0.089, 0.0005), "b": (0.169, 0.0001), "c": 0.6},
}

_TABLE_11_PR_STIFF = {
    ("double_split_tee", "shear_in_bolt"): {"a": 0.036, "b": 0.048, "c": 0.2, "primary": 0.03, "secondary": 0.040},
    ("double_split_tee", "tension_in_bolt"): {"a": 0.016, "b": 0.024, "c": 0.8, "primary": 0.013, "secondary": 0.020},
    ("double_split_tee", "tension_in_tee"): {"a": 0.012, "b": 0.018, "c": 0.8, "primary": 0.010, "secondary": 0.015},
    ("double_split_tee", "flexure_in_tee"): {"a": 0.042, "b": 0.084, "c": 0.2, "primary": 0.035, "secondary": 0.070},
}

# Flexible PR: a/b/primary/secondary are c0 - c1*dbg; c is a constant.
_TABLE_11_PR_FLEXIBLE = {
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


def table_11_fr_connection_modeling(connection_type, d):
    """Table 11, Fully Restrained Moment Connections: nonlinear modeling
    parameters (a, b, c) and acceptance criteria (equal to a, b per the
    printed table) as a function of beam depth d (printed p. 46).

    Parameters
    ----------
    connection_type : str
        One of 'improved_wuf_bolted_web', 'reduced_beam_section', 'wuf',
        'sideplate'.
    d : float
        Beam depth (inch).

    Returns
    -------
    dict
        {'a', 'b', 'c', 'primary_acceptance' (=a), 'secondary_acceptance'
        (=b), 'connection_type', 'd', 'table': '11', 'printed_page': '46',
        'pdf_page': 58}
    """
    key = connection_type.lower().strip()
    if key not in _TABLE_11_FR:
        raise ValueError(f"connection_type must be one of {sorted(_TABLE_11_FR)}, got {connection_type!r}")
    row = _TABLE_11_FR[key]
    a = row["a"][0] - row["a"][1] * d
    b = row["b"][0] - row["b"][1] * d
    return {"a": a, "b": b, "c": row["c"], "primary_acceptance": a,
            "secondary_acceptance": b, "connection_type": key, "d": d,
            "table": "11", "printed_page": "46", "pdf_page": 58}


def table_11_pr_stiff_connection_modeling(connection_type, limit_state):
    """Table 11, Partially Restrained Moment Connections (Relatively
    Stiff): constant nonlinear modeling parameters and acceptance criteria
    by limit state (printed p. 46).

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
         'connection_type', 'limit_state', 'table': '11',
         'printed_page': '46', 'pdf_page': 58}
    """
    key = (connection_type.lower().strip(), limit_state.lower().strip())
    if key not in _TABLE_11_PR_STIFF:
        raise ValueError(f"No Table 11 row for {key}; valid: {sorted(_TABLE_11_PR_STIFF)}")
    row = _TABLE_11_PR_STIFF[key]
    return {"a": row["a"], "b": row["b"], "c": row["c"],
            "primary_acceptance": row["primary"], "secondary_acceptance": row["secondary"],
            "connection_type": key[0], "limit_state": key[1], "table": "11",
            "printed_page": "46", "pdf_page": 58}


def table_11_pr_flexible_connection_modeling(connection_type, dbg, limit_state=None):
    """Table 11, Partially Restrained Simple/Moment Connections
    (Flexible): nonlinear modeling parameters and acceptance criteria as a
    function of bolt-group depth dbg (printed p. 46).

    Parameters
    ----------
    connection_type : str
        'double_angles' (requires limit_state) or 'simple_shear_tab'.
    dbg : float
        Depth of the bolt group (inch).
    limit_state : str, optional
        For 'double_angles': 'shear_in_bolt', 'tension_in_bolt', or
        'flexure_in_angles'.

    Returns
    -------
    dict
        {'a', 'b', 'c', 'primary_acceptance', 'secondary_acceptance',
         'connection_type', 'limit_state', 'dbg', 'table': '11',
         'printed_page': '46', 'pdf_page': 58}
    """
    conn = connection_type.lower().strip()
    ls = limit_state.lower().strip() if limit_state else None
    key = (conn, ls) if conn == "double_angles" else (conn, None)
    if key not in _TABLE_11_PR_FLEXIBLE:
        raise ValueError(f"No Table 11 row for {key}; valid: {sorted(_TABLE_11_PR_FLEXIBLE)}")
    row = _TABLE_11_PR_FLEXIBLE[key]
    a = row["a"][0] - row["a"][1] * dbg
    b = row["b"][0] - row["b"][1] * dbg
    primary = row["primary"][0] - row["primary"][1] * dbg
    secondary = row["secondary"][0] - row["secondary"][1] * dbg
    return {"a": a, "b": b, "c": row["c"], "primary_acceptance": primary,
            "secondary_acceptance": secondary, "connection_type": conn,
            "limit_state": ls, "dbg": dbg, "table": "11",
            "printed_page": "46", "pdf_page": 58}


# ============================================================================
# Appendix C Table C1.1 -- Steel Frame Beam-to-Column Connection Types
# (printed p. C19, pdf_page 95)
# ============================================================================

TABLE_C1_1_CONNECTION_TYPES = {
    "wuf": {
        "description": "Full-penetration welds between beams and columns flanges, bolted or welded web, designed prior to code changes following the Northridge earthquake.",
        "restraint": "FR", "figure": "C1.1(a)",
    },
    "welded_flange_plates": {
        "description": "Flange plate with full-penetration weld at column and fillet welded to beam flange.",
        "restraint": "FR", "figure": "C1.1(b)",
    },
    "welded_cover_plated_flanges": {
        "description": "Beam flange and cover-plate are welded to column flange.",
        "restraint": "FR", "figure": "C1.1(c)",
    },
    "bolted_flange_plates": {
        "description": "Flange plate with full-penetration weld at column and field bolted to beam flange.",
        "restraint": "FR or PR", "figure": "C1.1(d)",
    },
    "improved_wuf_bolted_web": {
        "description": "Full-penetration welds between beam and column flanges, bolted web, developed after Northridge Earthquake.",
        "restraint": "FR", "figure": "C1.1(a)",
    },
    "improved_wuf_welded_web": {
        "description": "Full-penetration welds between beam and column flanges, welded web developed after Northridge Earthquake.",
        "restraint": "FR", "figure": "C1.1(a)",
    },
    "free_flange": {
        "description": "Web is coped at ends of beam to separate flanges, welded web tab resists shear and bending moment due to eccentricity due to coped web developed after Northridge Earthquake.",
        "restraint": "FR", "figure": "C1.1(e)",
    },
    "welded_top_and_bottom_haunches": {
        "description": "Haunched connection at top and bottom flanges developed after Northridge Earthquake.",
        "restraint": "FR", "figure": "C1.1(f)",
    },
    "reduced_beam_section": {
        "description": "Connection in which net area of beam flange is reduced to force plastic hinging away from column face developed after Northridge Earthquake.",
        "restraint": "FR", "figure": "C1.1(g)",
    },
    "top_and_bottom_clip_angles": {
        "description": "Clip angle bolted or riveted to beam flange and column flange.",
        "restraint": "PR", "figure": "C1.2(a)",
    },
    "double_split_tee": {
        "description": "Split tees bolted or riveted to beam flange and column flange.",
        "restraint": "PR", "figure": "C1.2(b)",
    },
    "composite_top_and_clip_angle_bottom": {
        "description": "Clip angle bolted or riveted to column flange and beam bottom flange with composite slab.",
        "restraint": "PR", "figure": "C1.2(a) similar",
    },
    "bolted_end_plate": {
        "description": "Stiffened or unstiffened end plate welded to beam and bolted to column flange.",
        "restraint": "PR", "figure": "C1.2(c)",
    },
    "shear_tab_connection": {
        "description": "Simple gravity connection with shear tab, may have composite floor deck.",
        "restraint": "PR", "figure": "C1.3(b)",
    },
    "kaiser_bolted_bracket": {
        "description": "SMF moment connection with fastened cast steel haunch brackets that are bolted to the column flange and either fillet-welded or bolted to both beam flanges.",
        "restraint": "FR", "figure": "C1.4",
    },
    "sideplate": {
        "description": "SMF moment connection with full-depth side plates and fillet welds, developed following the 1994 Northridge earthquake.",
        "restraint": "FR", "figure": "C1.5",
    },
    "slottedweb": {
        "description": "SMF moment connection similar to WUF with extended web slots at weld access holes to separating the beam flanges from the beam web in the region of the connection.",
        "restraint": "FR", "figure": "C1.6",
    },
}


def table_c1_1_connection_type(connection_type):
    """Table C1.1: steel frame beam-to-column connection-type inventory --
    description, Fully/Partially Restrained (FR/PR) classification, and
    illustrating figure (printed p. C19). This is a descriptive/
    classification inventory (Appendix C commentary); the corresponding
    numeric m-factors and modeling parameters, where this document
    specifies its own values, are in ``table_10_*``/``table_11_*`` above.

    PRINTED IDENTICALLY (word-for-word) to UFC 4-023-03's Table C-1 -- see
    module docstring cross-check note.

    Parameters
    ----------
    connection_type : str
        A key of ``TABLE_C1_1_CONNECTION_TYPES`` (e.g.
        'reduced_beam_section', 'shear_tab_connection').

    Returns
    -------
    dict
        The row data plus {'connection_type', 'table': 'C1.1',
        'printed_page': 'C19', 'pdf_page': 95}.
    """
    key = connection_type.lower().strip()
    if key not in TABLE_C1_1_CONNECTION_TYPES:
        raise ValueError(f"connection_type must be one of {sorted(TABLE_C1_1_CONNECTION_TYPES)}, got {connection_type!r}")
    row = dict(TABLE_C1_1_CONNECTION_TYPES[key])
    row.update({"connection_type": key, "table": "C1.1", "printed_page": "C19", "pdf_page": 95})
    return row


def list_table_c1_1_connection_types(restraint=None):
    """Lists the connection-type keys in ``TABLE_C1_1_CONNECTION_TYPES``.

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
        return sorted(TABLE_C1_1_CONNECTION_TYPES)
    return sorted(k for k, v in TABLE_C1_1_CONNECTION_TYPES.items() if v["restraint"] == restraint.upper())
