"""UFC 4-023-03 Chapter 4 -- Reinforced Concrete (printed pp. 61-66,
pdf_page 76-81).

Material properties and Phi factors point to ASCE 41 Table 10-4 and ACI
318, respectively (Sections 4-1, 4-2) -- not reprinted here, apply those
codes directly. Tie Force requirements are the material-independent
Section 3-1 equations (``tie_forces.py``) plus a concrete-specific rebar
Phi=0.75 (Section 4-3). The Alternate Path acceptance criteria REPLACE
four ASCE 41 tables with this UFC's own Tables 4-1 through 4-4 (Section
4-4.3): Table 4-1/4-2 for RC beams (replacing ASCE 41 Tables 10-7/10-11),
Table 4-3/4-4 for two-way slabs and slab-column connections (replacing
ASCE 41 Tables 6-14/6-15).

NOTE on table structure (flag for lead visual check): Tables 4-1 and 4-3
print BOTH the nonlinear modeling parameters (a, b, c) and a set of
"Acceptance Criteria" plastic-rotation values for Primary/Secondary
components; as extracted, the acceptance-criteria values are IDENTICAL to
modeling parameters a (primary) and b (secondary) in every row. This
package transcribes the table literally as extracted (acceptance columns
carry the same numeric values); it is plausible by design (this UFC's
combined table serves both nonlinear modeling AND acceptance-criteria
purposes for its single Life-Safety-equivalent performance target) but
has not been independently confirmed against the printed page layout --
verify against printed pp. 63, 65 if precise acceptance-criteria columns
distinct from a/b are needed.
"""

from .._interpolation import _linterp


# ============================================================================
# Sections 4-1, 4-2, 4-3 -- Material Properties, Phi, Tie Force Rebar
# (printed p. 61, pdf_page 76)
# ============================================================================

def tie_rebar_phi():
    """Section 4-3: strength reduction factor Phi for properly anchored,
    embedded, or spliced reinforcement in TENSION providing Tie Force
    strength, based on ACI 318 strut-and-tie models (printed p. 61).

    Returns
    -------
    dict
        {'phi': 0.75, 'basis': 'ACI 318 strut-and-tie', 'paragraph': '4-3',
         'printed_page': '61', 'pdf_page': 76}
    """
    return {"phi": 0.75, "basis": "ACI 318 strut-and-tie", "paragraph": "4-3",
            "printed_page": "61", "pdf_page": 76}


# ============================================================================
# Table 4-1 -- Nonlinear Modeling Parameters and Acceptance Criteria for
# RC Beams, REPLACES ASCE 41 Table 10-7 (printed p. 63, pdf_page 78)
# ============================================================================

# Rows keyed by (transverse_reinf 'C'/'NC', vw_ratio_bin '<=3'/'>=6'); each
# holds the rho_diff=<=0.0 and rho_diff=>=0.5 sub-rows for bilinear
# interpolation over rho_diff in [0.0, 0.5] and vw_ratio in [3, 6].
_TABLE_4_1_FLEXURE = {
    # (transverse_reinf, vw_bin): {'rho0': (a, b, c), 'rho5': (a, b, c)}
    ("C", 3): {"rho0": (0.063, 0.10, 0.2), "rho5": (0.05, 0.06, 0.2)},
    ("C", 6): {"rho0": (0.05, 0.08, 0.2), "rho5": (0.038, 0.04, 0.2)},
    ("NC", 3): {"rho0": (0.05, 0.06, 0.2), "rho5": (0.025, 0.03, 0.2)},
    ("NC", 6): {"rho0": (0.025, 0.03, 0.2), "rho5": (0.013, 0.02, 0.2)},
}

_TABLE_4_1_OTHER = {
    "shear_stirrup_le_d2": {"a": 0.0030, "b": 0.02, "c": 0.2},
    "shear_stirrup_gt_d2": {"a": 0.0030, "b": 0.01, "c": 0.2},
    "development_stirrup_le_d2": {"a": 0.0030, "b": 0.02, "c": 0.0},
    "development_stirrup_gt_d2": {"a": 0.0030, "b": 0.01, "c": 0.0},
    "inadequate_embedment": {"a": 0.015, "b": 0.03, "c": 0.2},
}


def table_4_1_beam_flexure_modeling(rho_diff_over_rho_bal, transverse_reinf,
                                     vw_ratio, condition_governs="minimum"):
    """Table 4-1(i): nonlinear modeling parameters (a, b, c) and
    acceptance-criteria plastic rotations for a reinforced-concrete beam
    controlled by FLEXURE (printed p. 63, replaces ASCE 41 Table 10-7).
    Linear interpolation between the printed grid points is permitted
    (footnote 1) and performed here over rho_diff_over_rho_bal in
    [0.0, 0.5] and vw_ratio in [3, 6].

    Parameters
    ----------
    rho_diff_over_rho_bal : float
        (rho - rho') / rho_bal for the section, clamped to [0.0, 0.5] for
        interpolation.
    transverse_reinf : str
        'C' (conforming) or 'NC' (nonconforming) -- see footnote 4:
        conforming means hoops spaced <= d/3 within the plastic hinge
        region, and (for moderate/high ductility demand) Vs >= 3/4 of the
        design shear.
    vw_ratio : float
        V / (bw * d * sqrt(f'c)) [psi units, f'c in psi], clamped to
        [3, 6] for interpolation.
    condition_governs : str, optional
        Unused placeholder for future multi-condition minimum-governs
        logic (footnote 3: when multiple i-iv conditions occur, use the
        minimum numerical value). Default 'minimum'.

    Returns
    -------
    dict
        {'a', 'b', 'c' (residual strength ratio), 'primary_acceptance'
        (=a per the as-extracted table), 'secondary_acceptance' (=b),
        'table': '4-1', 'printed_page': '63', 'pdf_page': 78}
    """
    key = transverse_reinf.upper().strip()
    if key not in ("C", "NC"):
        raise ValueError("transverse_reinf must be 'C' or 'NC'")
    rho = max(0.0, min(0.5, rho_diff_over_rho_bal))
    vw = max(3.0, min(6.0, vw_ratio))
    row_3 = _TABLE_4_1_FLEXURE[(key, 3)]
    row_6 = _TABLE_4_1_FLEXURE[(key, 6)]

    def _at_vw(row):
        a = _linterp(rho, [0.0, 0.5], [row["rho0"][0], row["rho5"][0]])
        b = _linterp(rho, [0.0, 0.5], [row["rho0"][1], row["rho5"][1]])
        c = _linterp(rho, [0.0, 0.5], [row["rho0"][2], row["rho5"][2]])
        return a, b, c

    a3, b3, c3 = _at_vw(row_3)
    a6, b6, c6 = _at_vw(row_6)
    a = _linterp(vw, [3.0, 6.0], [a3, a6])
    b = _linterp(vw, [3.0, 6.0], [b3, b6])
    c = _linterp(vw, [3.0, 6.0], [c3, c6])
    return {"a": a, "b": b, "c": c, "primary_acceptance": a, "secondary_acceptance": b,
            "table": "4-1", "printed_page": "63", "pdf_page": 78}


def table_4_1_beam_other_modeling(condition, stirrup_spacing_le_d2=True):
    """Table 4-1(ii-iv): nonlinear modeling parameters for RC beams
    controlled by SHEAR, inadequate development/splicing, or inadequate
    embedment into the beam-column joint (printed p. 63).

    Parameters
    ----------
    condition : str
        'shear', 'development', or 'inadequate_embedment'.
    stirrup_spacing_le_d2 : bool, optional
        True if stirrup spacing <= d/2 (governs 'shear' and 'development'
        only). Default True.

    Returns
    -------
    dict
        {'a', 'b', 'c', 'primary_acceptance', 'secondary_acceptance',
         'table': '4-1', 'printed_page': '63', 'pdf_page': 78}
    """
    if condition == "shear":
        key = "shear_stirrup_le_d2" if stirrup_spacing_le_d2 else "shear_stirrup_gt_d2"
    elif condition == "development":
        key = "development_stirrup_le_d2" if stirrup_spacing_le_d2 else "development_stirrup_gt_d2"
    elif condition == "inadequate_embedment":
        key = "inadequate_embedment"
    else:
        raise ValueError("condition must be 'shear', 'development', or 'inadequate_embedment'")
    row = _TABLE_4_1_OTHER[key]
    return {"a": row["a"], "b": row["b"], "c": row["c"],
            "primary_acceptance": row["a"], "secondary_acceptance": row["b"],
            "table": "4-1", "printed_page": "63", "pdf_page": 78}


# ============================================================================
# Table 4-2 -- Acceptance Criteria (m-factors) for Linear Models of RC
# Beams, REPLACES ASCE 41 Table 10-11 (printed p. 64, pdf_page 79)
# ============================================================================

_TABLE_4_2_FLEXURE = {
    ("C", 3): {"rho0": (16, 19), "rho5": (9, 9)},
    ("C", 6): {"rho0": (9, 9), "rho5": (6, 7)},
    ("NC", 3): {"rho0": (9, 9), "rho5": (6, 7)},
    ("NC", 6): {"rho0": (6, 7), "rho5": (4, 5)},
}

_TABLE_4_2_OTHER = {
    "shear_stirrup_le_d2": (1.5, 3),
    "shear_stirrup_gt_d2": (1.5, 2),
    "development_stirrup_le_d2": (1.5, 3),
    "development_stirrup_gt_d2": (1.5, 2),
    "inadequate_embedment": (2, 3),
}


def table_4_2_beam_flexure_mfactor(rho_diff_over_rho_bal, transverse_reinf, vw_ratio):
    """Table 4-2(i): linear-model m-factors for an RC beam controlled by
    FLEXURE, primary and secondary components (printed p. 64, replaces
    ASCE 41 Table 10-11). Bilinear interpolation over
    rho_diff_over_rho_bal in [0.0, 0.5] and vw_ratio in [3, 6] (footnote 1).

    Parameters
    ----------
    rho_diff_over_rho_bal : float
        (rho - rho') / rho_bal, clamped to [0.0, 0.5].
    transverse_reinf : str
        'C' (conforming) or 'NC' (nonconforming).
    vw_ratio : float
        V / (bw * d * sqrt(f'c)), clamped to [3, 6].

    Returns
    -------
    dict
        {'m_primary', 'm_secondary', 'table': '4-2', 'printed_page': '64',
         'pdf_page': 79}
    """
    key = transverse_reinf.upper().strip()
    if key not in ("C", "NC"):
        raise ValueError("transverse_reinf must be 'C' or 'NC'")
    rho = max(0.0, min(0.5, rho_diff_over_rho_bal))
    vw = max(3.0, min(6.0, vw_ratio))
    row_3 = _TABLE_4_2_FLEXURE[(key, 3)]
    row_6 = _TABLE_4_2_FLEXURE[(key, 6)]

    def _at_vw(row):
        mp = _linterp(rho, [0.0, 0.5], [row["rho0"][0], row["rho5"][0]])
        ms = _linterp(rho, [0.0, 0.5], [row["rho0"][1], row["rho5"][1]])
        return mp, ms

    mp3, ms3 = _at_vw(row_3)
    mp6, ms6 = _at_vw(row_6)
    m_primary = _linterp(vw, [3.0, 6.0], [mp3, mp6])
    m_secondary = _linterp(vw, [3.0, 6.0], [ms3, ms6])
    return {"m_primary": m_primary, "m_secondary": m_secondary, "table": "4-2",
            "printed_page": "64", "pdf_page": 79}


def table_4_2_beam_other_mfactor(condition, stirrup_spacing_le_d2=True):
    """Table 4-2(ii-iv): linear-model m-factors for an RC beam controlled
    by shear, inadequate development/splicing, or inadequate embedment
    (printed p. 64).

    Parameters
    ----------
    condition : str
        'shear', 'development', or 'inadequate_embedment'.
    stirrup_spacing_le_d2 : bool, optional
        True if stirrup spacing <= d/2. Default True.

    Returns
    -------
    dict
        {'m_primary', 'm_secondary', 'table': '4-2', 'printed_page': '64',
         'pdf_page': 79}
    """
    if condition == "shear":
        key = "shear_stirrup_le_d2" if stirrup_spacing_le_d2 else "shear_stirrup_gt_d2"
    elif condition == "development":
        key = "development_stirrup_le_d2" if stirrup_spacing_le_d2 else "development_stirrup_gt_d2"
    elif condition == "inadequate_embedment":
        key = "inadequate_embedment"
    else:
        raise ValueError("condition must be 'shear', 'development', or 'inadequate_embedment'")
    m_primary, m_secondary = _TABLE_4_2_OTHER[key]
    return {"m_primary": m_primary, "m_secondary": m_secondary, "table": "4-2",
            "printed_page": "64", "pdf_page": 79}


# ============================================================================
# Table 4-3 -- Modeling Parameters and Acceptance Criteria for Two-Way
# Slabs and Slab-Column Connections, REPLACES ASCE 41 Table 6-14
# (printed p. 65, pdf_page 80)
# ============================================================================

_TABLE_4_3_FLEXURE = {
    # (continuity_reinf 'yes'/'no'): {'vg0.2': (a,b,c), 'vg0.4': (a,b,c)}
    "yes": {"vg0.2": (0.05, 0.10, 0.2), "vg0.4": (0.0, 0.04, 0.2)},
    "no": {"vg0.2": (0.02, 0.02, None), "vg0.4": (0.0, 0.0, None)},
}
# Acceptance-criteria (primary, secondary) at the same grid points:
_TABLE_4_3_ACCEPT = {
    "yes": {"vg0.2": (0.05, 0.10), "vg0.4": (0.0, 0.08)},
    "no": {"vg0.2": (0.015, 0.015), "vg0.4": (0.0, 0.0)},
}

_TABLE_4_3_OTHER = {
    "development": {"a": 0.0, "b": 0.02, "c": 0.0, "primary": 0.0, "secondary": 0.01},
    "inadequate_embedment": {"a": 0.015, "b": 0.03, "c": 0.2, "primary": 0.01, "secondary": 0.02},
}


def table_4_3_slab_flexure_modeling(vg_over_vo, continuity_reinforcement):
    """Table 4-3(i): nonlinear modeling parameters and acceptance criteria
    for a two-way slab or slab-column connection controlled by FLEXURE
    (printed p. 65, replaces ASCE 41 Table 6-14). Interpolated over
    Vg/Vo in [0.2, 0.4] (footnote 1); the residual strength ratio c is
    undefined ('-') when continuity_reinforcement=False, matching the
    printed table (no residual capacity without continuity reinforcement).

    Parameters
    ----------
    vg_over_vo : float
        Ratio of gravity shear on the slab critical section (Vg, per ACI
        318) to the direct punching shear strength (Vo, per ACI 318),
        clamped to [0.2, 0.4].
    continuity_reinforcement : bool
        True ('Yes') if at least one main bottom bar (or, for
        post-tensioned slabs, one tendon) in each direction is
        effectively continuous through the column cage; else False ('No').

    Returns
    -------
    dict
        {'a', 'b', 'c' (residual strength ratio, or None if undefined),
         'primary_acceptance', 'secondary_acceptance', 'table': '4-3',
         'printed_page': '65', 'pdf_page': 80}
    """
    key = "yes" if continuity_reinforcement else "no"
    vg = max(0.2, min(0.4, vg_over_vo))
    row = _TABLE_4_3_FLEXURE[key]
    accept = _TABLE_4_3_ACCEPT[key]
    a = _linterp(vg, [0.2, 0.4], [row["vg0.2"][0], row["vg0.4"][0]])
    b = _linterp(vg, [0.2, 0.4], [row["vg0.2"][1], row["vg0.4"][1]])
    c = None if row["vg0.2"][2] is None else _linterp(vg, [0.2, 0.4], [row["vg0.2"][2], row["vg0.4"][2]])
    pa = _linterp(vg, [0.2, 0.4], [accept["vg0.2"][0], accept["vg0.4"][0]])
    sa = _linterp(vg, [0.2, 0.4], [accept["vg0.2"][1], accept["vg0.4"][1]])
    return {"a": a, "b": b, "c": c, "primary_acceptance": pa, "secondary_acceptance": sa,
            "table": "4-3", "printed_page": "65", "pdf_page": 80}


def table_4_3_slab_other_modeling(condition):
    """Table 4-3(ii-iii): nonlinear modeling parameters for a two-way slab
    controlled by inadequate development/splicing, or inadequate
    embedment into the slab-column joint (printed p. 65).

    Parameters
    ----------
    condition : str
        'development' or 'inadequate_embedment'.

    Returns
    -------
    dict
        {'a', 'b', 'c', 'primary_acceptance', 'secondary_acceptance',
         'table': '4-3', 'printed_page': '65', 'pdf_page': 80}
    """
    if condition not in _TABLE_4_3_OTHER:
        raise ValueError("condition must be 'development' or 'inadequate_embedment'")
    row = _TABLE_4_3_OTHER[condition]
    return {"a": row["a"], "b": row["b"], "c": row["c"],
            "primary_acceptance": row["primary"], "secondary_acceptance": row["secondary"],
            "table": "4-3", "printed_page": "65", "pdf_page": 80}


# ============================================================================
# Table 4-4 -- Acceptance Criteria (m-factors) for Linear Models of
# Two-Way Slabs, REPLACES ASCE 41 Table 6-15 (printed p. 66, pdf_page 81)
# ============================================================================

_TABLE_4_4_FLEXURE = {
    "yes": {"vg0.2": (6, 7), "vg0.4": (1, 5)},
    "no": {"vg0.2": (2, 2), "vg0.4": (1, 1)},
}

_TABLE_4_4_OTHER = {
    "development": (None, 4),  # primary m-factor '-' (not applicable) per printed table
    "inadequate_embedment": (3, 4),
}


def table_4_4_slab_flexure_mfactor(vg_over_vo, continuity_reinforcement):
    """Table 4-4(i): linear-model m-factors for a two-way slab or
    slab-column connection controlled by FLEXURE (printed p. 66, replaces
    ASCE 41 Table 6-15). Interpolated over Vg/Vo in [0.2, 0.4].

    Parameters
    ----------
    vg_over_vo : float
        Vg/Vo per ACI 318, clamped to [0.2, 0.4].
    continuity_reinforcement : bool
        True ('Yes') or False ('No') per the continuity-reinforcement
        definition in ``table_4_3_slab_flexure_modeling``.

    Returns
    -------
    dict
        {'m_primary', 'm_secondary', 'table': '4-4', 'printed_page': '66',
         'pdf_page': 81}
    """
    key = "yes" if continuity_reinforcement else "no"
    vg = max(0.2, min(0.4, vg_over_vo))
    row = _TABLE_4_4_FLEXURE[key]
    mp = _linterp(vg, [0.2, 0.4], [row["vg0.2"][0], row["vg0.4"][0]])
    ms = _linterp(vg, [0.2, 0.4], [row["vg0.2"][1], row["vg0.4"][1]])
    return {"m_primary": mp, "m_secondary": ms, "table": "4-4",
            "printed_page": "66", "pdf_page": 81}


def table_4_4_slab_other_mfactor(condition):
    """Table 4-4(ii-iii): linear-model m-factors for a two-way slab
    controlled by inadequate development/splicing (primary m-factor not
    applicable, '-' in the printed table -- secondary only) or inadequate
    embedment into the slab-column joint (printed p. 66).

    Parameters
    ----------
    condition : str
        'development' or 'inadequate_embedment'.

    Returns
    -------
    dict
        {'m_primary' (None if not applicable), 'm_secondary',
         'table': '4-4', 'printed_page': '66', 'pdf_page': 81}
    """
    if condition not in _TABLE_4_4_OTHER:
        raise ValueError("condition must be 'development' or 'inadequate_embedment'")
    m_primary, m_secondary = _TABLE_4_4_OTHER[condition]
    return {"m_primary": m_primary, "m_secondary": m_secondary, "table": "4-4",
            "printed_page": "66", "pdf_page": 81}
