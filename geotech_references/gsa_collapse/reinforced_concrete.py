"""GSA Alternate Path Analysis and Design Guidelines Chapter 4 --
Reinforced Concrete (printed pp. 37-42, pdf_page 49-54).

Chapter 4 of UFC 4-023-03 is adopted with two printed modifications
(Section 4, opening list): (1) modeling and acceptance criteria for
primary and secondary components are revised from ASCE 41's Life Safety
performance level to COLLAPSE PREVENTION (Section 4.4.3; Commentary
C3.2.10.1 explains this reflects the severe-but-survivable damage state
this AP method targets), and (2) all Tie Force (Section 4.3) and Enhanced
Local Resistance (Section 4.5) references are REMOVED IN THEIR ENTIRETY.

Commentary C4.4.3 explains the beam/slab flexure modifications specifically:
for RC beams and slabs controlled by flexure, the ASCE 41 Collapse
Prevention modeling/acceptance values were multiplied by 2.5 (primary
components) and 2.0 (secondary components), based on blast- and
impact-loaded flexural-member test data -- these UFC-derived multipliers
are already baked into the printed Tables 6-9 below (this module digitizes
the printed replacement tables directly, not the underlying ASCE 41
baseline).

CROSS-DOCUMENT CONSISTENCY (verified against geotech_references.ufc_collapse
in tests/test_gsa_collapse_reinforced_concrete.py, all confirmed by direct
visual comparison against the rendered PDF pages of both documents):
  - Table 6 (nonlinear RC beam modeling, replaces ASCE 41 Table 10-7) and
    Table 7 (linear RC beam m-factors, replaces ASCE 41 Table 10-13) are
    printed IDENTICALLY to UFC 4-023-03 Tables 4-1 and 4-2.
  - Table 8 (nonlinear two-way slab modeling, replaces ASCE 41 Table
    10-15) has ONE confirmed printed VALUE DIFFERENCE from UFC 4-023-03
    Table 4-3: none found -- Table 8's modeling parameters (a, b, c) match
    Table 4-3 exactly; see Table 9 below for the slab table that differs.
  - Table 9 (linear two-way slab m-factors, replaces ASCE 41 Table 10-16)
    has TWO confirmed printed VALUE DIFFERENCES from UFC 4-023-03 Table
    4-4 (both visually confirmed against the GSA source PDF, printed
    p. 42): (a) the Vg/Vo<=0.2, No-continuity-reinforcement row prints
    m=3 for BOTH primary and secondary components in this GSA document,
    versus m=(2, 2) in ufc_collapse's Table 4-4 digitization; (b) the
    "inadequate embedment into the slab-column joint" row prints a PRIMARY
    m-factor of "-" (not applicable, identical in form to the "inadequate
    development" row directly above it) in this GSA document, versus a
    primary m-factor of 3 in ufc_collapse's Table 4-4 digitization. These
    are printed-value disagreements between the two documents as
    currently digitized in this repository -- reported here per this
    module's cross-check doctrine, NOT silently reconciled. (GSA's Rev 1
    (Jan 2016) cites UFC 4-023-03 "including change 2, 1 June 2013"
    (Appendix A ref. [31]) as its source, while ufc_collapse digitizes the
    UFC 4-023-03 edition through Change 4 (10 June 2024) -- a plausible,
    but NOT independently confirmed, explanation is that this specific
    table cell was revised in a UFC amendment between Change 2 and Change
    4; see ``tests/test_gsa_collapse_reinforced_concrete.py`` for the
    exact assertions.)

VALIDATED against Appendix D's worked reinforced-concrete example (printed
pp. D11-D13, pdf_page 112-114):
  - Typical beam component (Beam B1, rho=0.011, rho'=0.010,
    rho_bal=0.034 -> (rho-rho')/rho_bal=0.037; conforming transverse
    reinforcement) -- ``table_7_beam_flexure_mfactor`` reproduces the
    printed example's single-axis intermediate result at
    V/(bw*d*sqrt(f'c))=3 EXACTLY: m=15.48.
  - Column component (P/(Ag*f'c)=0.35, rho_v=0.003, assumed deformation-
    controlled for the example) -> m=2.0, reproduced exactly.

FLAGGED PRINTED ARITHMETIC DISCREPANCIES (confirmed by direct execution,
NOT silently corrected), both in the SAME Appendix D beam-example
derivation (printed pp. D12-D13):
  (1) The companion single-axis intermediate result at
      V/(bw*d*sqrt(f'c))=6 is printed as m=8.88, but applying the
      document's own interpolation formula to its own Table 7 corner
      values (9 at rho=0, 6 at rho=0.5) at rho=0.037 gives m=8.778 (which
      would round to 8.78, not 8.88) -- ``table_7_beam_flexure_mfactor``
      returns this mathematically correct 8.778.
  (2) The FINAL step bilinearly interpolates the two intermediate results
      to V/(bw*d*sqrt(f'c))=3.88 and states the answer is m=10.74.
      Independently evaluating the SAME printed formula with the SAME
      printed intermediate values -- m = [(3.88-3)/(6-3)]*(8.88-15.48)
      +15.48 -- gives m=13.54, not 10.74
      (``table_7_beam_flexure_mfactor(0.037, 'C', 3.88)`` returns
      m_primary=13.515, matching this independent hand recomputation,
      not the document's printed final answer).
Both are genuine printed errors in GSA's own worked example, page-
verified against the rendered PDF (printed pp. D12-D13) -- reported here
per this module's doctrine of
never silently reconciling a source-document discrepancy. See
``tests/test_gsa_collapse_reinforced_concrete.py`` for the exact
reproduction of the two correct intermediate values and the
independently-recomputed final value.
"""

from .._interpolation import _linterp


# ============================================================================
# Table 6 -- Nonlinear Modeling Parameters and Acceptance Criteria for
# Reinforced Concrete Beams, REPLACES ASCE 41 Table 10-7 (printed p. 39,
# pdf_page 51)
# ============================================================================

# Rows keyed by (transverse_reinf 'C'/'NC', vw_ratio_bin 3/6); each holds
# the rho_diff<=0.0 and rho_diff>=0.5 sub-rows (a, b, c) for bilinear
# interpolation over rho_diff in [0.0, 0.5] and vw_ratio in [3, 6].
_TABLE_6_FLEXURE = {
    ("C", 3): {"rho0": (0.063, 0.10, 0.2), "rho5": (0.05, 0.06, 0.2)},
    ("C", 6): {"rho0": (0.05, 0.08, 0.2), "rho5": (0.038, 0.04, 0.2)},
    ("NC", 3): {"rho0": (0.05, 0.06, 0.2), "rho5": (0.025, 0.03, 0.2)},
    ("NC", 6): {"rho0": (0.025, 0.03, 0.2), "rho5": (0.013, 0.02, 0.2)},
}

_TABLE_6_OTHER = {
    "shear_stirrup_le_d2": {"a": 0.0030, "b": 0.02, "c": 0.2},
    "shear_stirrup_gt_d2": {"a": 0.0030, "b": 0.01, "c": 0.2},
    "development_stirrup_le_d2": {"a": 0.0030, "b": 0.02, "c": 0.0},
    "development_stirrup_gt_d2": {"a": 0.0030, "b": 0.01, "c": 0.0},
    "inadequate_embedment": {"a": 0.015, "b": 0.03, "c": 0.2},
}


def table_6_beam_flexure_modeling(rho_diff_over_rho_bal, transverse_reinf, vw_ratio):
    """Table 6(i): nonlinear modeling parameters (a, b, c) and acceptance-
    criteria plastic rotations for a reinforced-concrete beam controlled
    by FLEXURE (printed p. 39, replaces ASCE 41 Table 10-7). Linear
    interpolation between the printed grid points is permitted (footnote
    1) and performed here over rho_diff_over_rho_bal in [0.0, 0.5] and
    vw_ratio in [3, 6].

    Parameters
    ----------
    rho_diff_over_rho_bal : float
        (rho - rho') / rho_bal for the section, clamped to [0.0, 0.5] for
        interpolation.
    transverse_reinf : str
        'C' (conforming) or 'NC' (nonconforming) -- footnote 4: conforming
        means hoops spaced <= d/3 within the flexural plastic hinge
        region, and (for components of moderate/high ductility demand)
        the strength provided by the hoops (Vs) is at least 3/4 of the
        design shear.
    vw_ratio : float
        V / (bw * d * sqrt(f'c)) [psi units, f'c in psi], clamped to
        [3, 6] for interpolation.

    Returns
    -------
    dict
        {'a', 'b', 'c' (residual strength ratio), 'primary_acceptance'
        (=a per the as-extracted table), 'secondary_acceptance' (=b),
        'table': '6', 'printed_page': '39', 'pdf_page': 51}
    """
    key = transverse_reinf.upper().strip()
    if key not in ("C", "NC"):
        raise ValueError("transverse_reinf must be 'C' or 'NC'")
    rho = max(0.0, min(0.5, rho_diff_over_rho_bal))
    vw = max(3.0, min(6.0, vw_ratio))
    row_3 = _TABLE_6_FLEXURE[(key, 3)]
    row_6 = _TABLE_6_FLEXURE[(key, 6)]

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
            "table": "6", "printed_page": "39", "pdf_page": 51}


def table_6_beam_other_modeling(condition, stirrup_spacing_le_d2=True):
    """Table 6(ii-iv): nonlinear modeling parameters for RC beams
    controlled by SHEAR, inadequate development/splicing, or inadequate
    embedment into the beam-column joint (printed p. 39).

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
         'table': '6', 'printed_page': '39', 'pdf_page': 51}
    """
    if condition == "shear":
        key = "shear_stirrup_le_d2" if stirrup_spacing_le_d2 else "shear_stirrup_gt_d2"
    elif condition == "development":
        key = "development_stirrup_le_d2" if stirrup_spacing_le_d2 else "development_stirrup_gt_d2"
    elif condition == "inadequate_embedment":
        key = "inadequate_embedment"
    else:
        raise ValueError("condition must be 'shear', 'development', or 'inadequate_embedment'")
    row = _TABLE_6_OTHER[key]
    return {"a": row["a"], "b": row["b"], "c": row["c"],
            "primary_acceptance": row["a"], "secondary_acceptance": row["b"],
            "table": "6", "printed_page": "39", "pdf_page": 51}


# ============================================================================
# Table 7 -- Acceptance Criteria (m-factors) for Linear Models of RC
# Beams, REPLACES ASCE 41 Table 10-13 (printed p. 40, pdf_page 52)
# ============================================================================

_TABLE_7_FLEXURE = {
    ("C", 3): {"rho0": (16, 19), "rho5": (9, 9)},
    ("C", 6): {"rho0": (9, 9), "rho5": (6, 7)},
    ("NC", 3): {"rho0": (9, 9), "rho5": (6, 7)},
    ("NC", 6): {"rho0": (6, 7), "rho5": (4, 5)},
}

_TABLE_7_OTHER = {
    "shear_stirrup_le_d2": (1.75, 4),
    "shear_stirrup_gt_d2": (1.75, 3),
    "development_stirrup_le_d2": (1.75, 4),
    "development_stirrup_gt_d2": (1.75, 3),
    "inadequate_embedment": (3, 4),
}


def table_7_beam_flexure_mfactor(rho_diff_over_rho_bal, transverse_reinf, vw_ratio):
    """Table 7(i): linear-model m-factors for an RC beam controlled by
    FLEXURE, primary and secondary components (printed p. 40, replaces
    ASCE 41 Table 10-13). Bilinear interpolation over
    rho_diff_over_rho_bal in [0.0, 0.5] and vw_ratio in [3, 6] (footnote
    1).

    VALIDATED against Appendix D's typical-beam-component example
    (printed pp. D11-D13): rho_diff_over_rho_bal=0.037, transverse_reinf=
    'C' at vw_ratio=3 -> m_primary=15.48, reproduced exactly. The
    example's companion result at vw_ratio=6 (printed as m=8.88) and its
    final bilinearly-interpolated answer at vw_ratio=3.88 (printed as
    m=10.74) are both FLAGGED PRINTED ARITHMETIC DISCREPANCIES -- see
    module docstring; this function returns the mathematically correct
    m_primary=8.778 at vw_ratio=6 and m_primary=13.515 at vw_ratio=3.88,
    matching an independent hand recomputation of the document's own
    printed formula and intermediate values, not its printed answers.

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
        {'m_primary', 'm_secondary', 'table': '7', 'printed_page': '40',
         'pdf_page': 52}
    """
    key = transverse_reinf.upper().strip()
    if key not in ("C", "NC"):
        raise ValueError("transverse_reinf must be 'C' or 'NC'")
    rho = max(0.0, min(0.5, rho_diff_over_rho_bal))
    vw = max(3.0, min(6.0, vw_ratio))
    row_3 = _TABLE_7_FLEXURE[(key, 3)]
    row_6 = _TABLE_7_FLEXURE[(key, 6)]

    def _at_vw(row):
        mp = _linterp(rho, [0.0, 0.5], [row["rho0"][0], row["rho5"][0]])
        ms = _linterp(rho, [0.0, 0.5], [row["rho0"][1], row["rho5"][1]])
        return mp, ms

    mp3, ms3 = _at_vw(row_3)
    mp6, ms6 = _at_vw(row_6)
    m_primary = _linterp(vw, [3.0, 6.0], [mp3, mp6])
    m_secondary = _linterp(vw, [3.0, 6.0], [ms3, ms6])
    return {"m_primary": m_primary, "m_secondary": m_secondary, "table": "7",
            "printed_page": "40", "pdf_page": 52}


def table_7_beam_other_mfactor(condition, stirrup_spacing_le_d2=True):
    """Table 7(ii-iv): linear-model m-factors for an RC beam controlled by
    shear, inadequate development/splicing, or inadequate embedment
    (printed p. 40).

    Parameters
    ----------
    condition : str
        'shear', 'development', or 'inadequate_embedment'.
    stirrup_spacing_le_d2 : bool, optional
        True if stirrup spacing <= d/2. Default True.

    Returns
    -------
    dict
        {'m_primary', 'm_secondary', 'table': '7', 'printed_page': '40',
         'pdf_page': 52}
    """
    if condition == "shear":
        key = "shear_stirrup_le_d2" if stirrup_spacing_le_d2 else "shear_stirrup_gt_d2"
    elif condition == "development":
        key = "development_stirrup_le_d2" if stirrup_spacing_le_d2 else "development_stirrup_gt_d2"
    elif condition == "inadequate_embedment":
        key = "inadequate_embedment"
    else:
        raise ValueError("condition must be 'shear', 'development', or 'inadequate_embedment'")
    m_primary, m_secondary = _TABLE_7_OTHER[key]
    return {"m_primary": m_primary, "m_secondary": m_secondary, "table": "7",
            "printed_page": "40", "pdf_page": 52}


# ============================================================================
# Table 8 -- Modeling Parameters and Acceptance Criteria for Two-Way Slabs
# and Slab-Column Connections, REPLACES ASCE 41 Table 10-15 (printed
# p. 41, pdf_page 53)
# ============================================================================

_TABLE_8_FLEXURE = {
    # (continuity_reinf 'yes'/'no'): {'vg0.2': (a,b,c), 'vg0.4': (a,b,c)}
    "yes": {"vg0.2": (0.05, 0.10, 0.2), "vg0.4": (0.0, 0.04, 0.2)},
    "no": {"vg0.2": (0.02, 0.02, None), "vg0.4": (0.0, 0.0, None)},
}
# Single printed "Acceptance Criteria" column value per row. As printed,
# this equals 'b' (the secondary modeling parameter) for the "yes" rows
# and equals 'a'=='b' (identical for "no" rows, so not distinguishable)
# for the "no" rows -- transcribed here as (primary=a, secondary=b) to
# match the ufc_collapse Table 4-3 convention and enable a direct
# cross-check (see module docstring).
_TABLE_8_ACCEPT = {
    "yes": {"vg0.2": (0.05, 0.10), "vg0.4": (0.0, 0.08)},
    "no": {"vg0.2": (0.015, 0.015), "vg0.4": (0.0, 0.0)},
}

_TABLE_8_OTHER = {
    "development": {"a": 0.0, "b": 0.02, "c": 0.0, "primary": 0.0, "secondary": 0.01},
    "inadequate_embedment": {"a": 0.015, "b": 0.03, "c": 0.2, "primary": 0.01, "secondary": 0.02},
}


def table_8_slab_flexure_modeling(vg_over_vo, continuity_reinforcement):
    """Table 8(i): nonlinear modeling parameters and acceptance criteria
    for a two-way slab or slab-column connection controlled by FLEXURE
    (printed p. 41, replaces ASCE 41 Table 10-15). Interpolated over
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
        post-tensioned slabs, one tendon) in each direction is effectively
        continuous through the column cage; else False ('No').

    Returns
    -------
    dict
        {'a', 'b', 'c' (residual strength ratio, or None if undefined),
         'primary_acceptance', 'secondary_acceptance', 'table': '8',
         'printed_page': '41', 'pdf_page': 53}
    """
    key = "yes" if continuity_reinforcement else "no"
    vg = max(0.2, min(0.4, vg_over_vo))
    row = _TABLE_8_FLEXURE[key]
    accept = _TABLE_8_ACCEPT[key]
    a = _linterp(vg, [0.2, 0.4], [row["vg0.2"][0], row["vg0.4"][0]])
    b = _linterp(vg, [0.2, 0.4], [row["vg0.2"][1], row["vg0.4"][1]])
    c = None if row["vg0.2"][2] is None else _linterp(vg, [0.2, 0.4], [row["vg0.2"][2], row["vg0.4"][2]])
    pa = _linterp(vg, [0.2, 0.4], [accept["vg0.2"][0], accept["vg0.4"][0]])
    sa = _linterp(vg, [0.2, 0.4], [accept["vg0.2"][1], accept["vg0.4"][1]])
    return {"a": a, "b": b, "c": c, "primary_acceptance": pa, "secondary_acceptance": sa,
            "table": "8", "printed_page": "41", "pdf_page": 53}


def table_8_slab_other_modeling(condition):
    """Table 8(ii-iii): nonlinear modeling parameters for a two-way slab
    controlled by inadequate development/splicing, or inadequate
    embedment into the slab-column joint (printed p. 41).

    Parameters
    ----------
    condition : str
        'development' or 'inadequate_embedment'.

    Returns
    -------
    dict
        {'a', 'b', 'c', 'primary_acceptance', 'secondary_acceptance',
         'table': '8', 'printed_page': '41', 'pdf_page': 53}
    """
    if condition not in _TABLE_8_OTHER:
        raise ValueError("condition must be 'development' or 'inadequate_embedment'")
    row = _TABLE_8_OTHER[condition]
    return {"a": row["a"], "b": row["b"], "c": row["c"],
            "primary_acceptance": row["primary"], "secondary_acceptance": row["secondary"],
            "table": "8", "printed_page": "41", "pdf_page": 53}


# ============================================================================
# Table 9 -- Acceptance Criteria (m-factors) for Linear Models of Two-Way
# Slabs, REPLACES ASCE 41 Table 10-16 (printed p. 42, pdf_page 54)
# ============================================================================

# PAGE-VERIFIED (rendered PDF, printed p. 42): the <=0.2/No row prints
# m=(3, 3) -- see module docstring cross-check note (ufc_collapse's
# Table 4-4 digitization has (2, 2) for the same cell).
_TABLE_9_FLEXURE = {
    "yes": {"vg0.2": (6, 7), "vg0.4": (1, 5)},
    "no": {"vg0.2": (3, 3), "vg0.4": (1, 1)},
}

# PAGE-VERIFIED (rendered PDF, printed p. 42): BOTH "development" and
# "inadequate embedment" rows print primary='-' (not applicable),
# secondary=4 -- see module docstring cross-check note (ufc_collapse's
# Table 4-4 digitization has primary=3 for "inadequate_embedment").
_TABLE_9_OTHER = {
    "development": (None, 4),
    "inadequate_embedment": (None, 4),
}


def table_9_slab_flexure_mfactor(vg_over_vo, continuity_reinforcement):
    """Table 9(i): linear-model m-factors for a two-way slab or
    slab-column connection controlled by FLEXURE (printed p. 42, replaces
    ASCE 41 Table 10-16). Interpolated over Vg/Vo in [0.2, 0.4].

    Parameters
    ----------
    vg_over_vo : float
        Vg/Vo per ACI 318, clamped to [0.2, 0.4].
    continuity_reinforcement : bool
        True ('Yes') or False ('No') per the continuity-reinforcement
        definition in ``table_8_slab_flexure_modeling``.

    Returns
    -------
    dict
        {'m_primary', 'm_secondary', 'table': '9', 'printed_page': '42',
         'pdf_page': 54}
    """
    key = "yes" if continuity_reinforcement else "no"
    vg = max(0.2, min(0.4, vg_over_vo))
    row = _TABLE_9_FLEXURE[key]
    mp = _linterp(vg, [0.2, 0.4], [row["vg0.2"][0], row["vg0.4"][0]])
    ms = _linterp(vg, [0.2, 0.4], [row["vg0.2"][1], row["vg0.4"][1]])
    return {"m_primary": mp, "m_secondary": ms, "table": "9",
            "printed_page": "42", "pdf_page": 54}


def table_9_slab_other_mfactor(condition):
    """Table 9(ii-iii): linear-model m-factors for a two-way slab
    controlled by inadequate development/splicing or inadequate embedment
    into the slab-column joint (printed p. 42). BOTH conditions print a
    primary m-factor of "-" (not applicable) and a secondary m-factor of
    4 -- see module docstring cross-check note.

    Parameters
    ----------
    condition : str
        'development' or 'inadequate_embedment'.

    Returns
    -------
    dict
        {'m_primary' (None, not applicable), 'm_secondary',
         'table': '9', 'printed_page': '42', 'pdf_page': 54}
    """
    if condition not in _TABLE_9_OTHER:
        raise ValueError("condition must be 'development' or 'inadequate_embedment'")
    m_primary, m_secondary = _TABLE_9_OTHER[condition]
    return {"m_primary": m_primary, "m_secondary": m_secondary, "table": "9",
            "printed_page": "42", "pdf_page": 54}


# ============================================================================
# Appendix D worked-example helper -- column axial/shear classification
# (printed p. D13, pdf_page 114)
# ============================================================================

def column_deformation_controlled_shear_check(vp, vo):
    """Appendix D worked example (printed p. D13): for PRELIMINARY column
    m-factor evaluation, a column may be assumed deformation-controlled if
    the shear-demand-to-shear-capacity ratio Vp/Vo <= 0.6 (per ASCE 41
    Table 10-9 guidance, cross-referenced by Section 4.4.3). This
    assumption must be VERIFIED after the column-removal analysis is
    performed (Section 3.2.10/D4.3): any column with Vp/Vo >= 0.6 must be
    reclassified as force-controlled and reevaluated under the
    force-controlled modeling assumptions -- consistent with every column
    in the Appendix D example ultimately being governed as force-
    controlled (Table D17).

    Parameters
    ----------
    vp : float
        Column shear demand.
    vo : float
        Column shear capacity using expected material properties.

    Returns
    -------
    dict
        {'vp_over_vo', 'assumed_deformation_controlled' (bool),
         'printed_page': 'D13', 'pdf_page': 114}
    """
    ratio = vp / vo
    return {"vp_over_vo": ratio, "assumed_deformation_controlled": ratio <= 0.6,
            "printed_page": "D13", "pdf_page": 114}
