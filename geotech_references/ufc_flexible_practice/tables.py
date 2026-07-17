"""UFC 3-250-03, Standard Practice Manual for Flexible Pavements (30 May 2018) -
table lookup functions.

This is a construction-practice manual, not a design-code, so ``tables.py`` is
deliberately selective: only genuinely lookup-worthy relationships are
digitized here (PG asphalt-cement selection by climate, Marshall mix-design
criteria, aggregate gradation bands, spray/seal application rates, and the
Appendix B surface-area design factors). Static material-specification sheets
with no real lookup dimension (fiber-stabilizer test-method tables, sealer
physical-property acceptance criteria, RMP aggregate physical-property
criteria) are intentionally NOT digitized here -- see the module report for
the full skip list; that content lives in the structured chapter text
instead.

PDF pages cited below are 0-based fitz page indices into
``docs/ufc_3_250_03_2018.pdf``; the printed manual page is also given
(pdf_page_index = printed_page + 13).

Units follow the source document, which is SI-primary with US-customary given
parenthetically (mm, L/m2, degrees C); every function returns BOTH the SI and
the US-customary value so callers can use either.

NOTE ON TABLE NUMBERING: the printed "List of Tables" (front matter, pdf_page
11) and the in-body table captions disagree for Tables 2-13 through 2-16 --
the body actually presents Table 2-13 = "Properties of Cellulose Fibers"
(pdf_page 65, printed p.52), Table 2-14 = "Properties of Mineral Fibers"
(pdf_page 66, printed p.53), Table 2-15 = "SMA Gradation Guideline" (pdf_page
70, printed p.57), Table 2-16 = "Recommended SMA Coarse and Fine Aggregate
Properties" (pdf_page 71, printed p.58) -- the reverse of what the front-matter
List of Tables claims. This module cites the IN-BODY (authoritative) numbering
throughout.
"""


# ============================================================================
# Table 2-1: Aggregate Gradations for HMA Pavements
# (Section 2-1.2; pdf_page 17, printed p.4)
# ============================================================================

_TABLE_2_1_SIEVES_MM = [25.0, 19.0, 12.5, 9.5, 4.75, 2.36, 1.18, 0.60, 0.30, 0.15, 0.075]
_TABLE_2_1_SIEVE_LABELS = ["1 in", "3/4 in", "1/2 in", "3/8 in", "No. 4", "No. 8",
                           "No. 16", "No. 30", "No. 50", "No. 100", "No. 200"]

_TABLE_2_1 = {
    "gradation_1": {  # 19 mm (3/4 in) nominal max aggregate size
        "nominal_max_size_mm": 19.0, "nominal_max_size_in": 0.75,
        "bands": [(100, 100), (90, 100), (68, 88), (60, 82), (45, 67), (32, 54),
                  (22, 44), (15, 35), (9, 25), (6, 18), (3, 6)],
    },
    "gradation_2": {  # 12.5 mm (1/2 in) nominal max aggregate size
        "nominal_max_size_mm": 12.5, "nominal_max_size_in": 0.5,
        "bands": [(None, None), (100, 100), (90, 100), (69, 89), (53, 73), (38, 60),
                  (26, 48), (18, 38), (11, 27), (6, 18), (3, 6)],
    },
    "gradation_3": {  # 9.5 mm (3/8 in) nominal max aggregate size
        "nominal_max_size_mm": 9.5, "nominal_max_size_in": 0.375,
        "bands": [(None, None), (None, None), (100, 100), (90, 100), (58, 78), (40, 60),
                  (28, 48), (18, 38), (11, 27), (6, 18), (3, 6)],
    },
}


def table_2_1_gradation_hma(gradation, sieve_mm=None) -> dict:
    """Aggregate gradation band for HMA pavements (Table 2-1).

    Three gradations by nominal maximum aggregate size, used to select the
    aggregate blend for dense-graded HMA (Section 2-1.2).

    Parameters
    ----------
    gradation : str
        'gradation_1' (19 mm / 3/4 in nominal max), 'gradation_2' (12.5 mm /
        1/2 in), or 'gradation_3' (9.5 mm / 3/8 in).
    sieve_mm : float, optional
        Sieve size, mm (one of 25.0, 19.0, 12.5, 9.5, 4.75, 2.36, 1.18, 0.60,
        0.30, 0.15, 0.075). If given, returns just that sieve's percent-passing
        band. If omitted, returns the full gradation band table.

    Returns
    -------
    dict
        {'gradation', 'nominal_max_size_mm', 'nominal_max_size_in', 'sieve_mm',
         'percent_passing_min', 'percent_passing_max', 'reference'} if
        sieve_mm given, else {'gradation', ..., 'bands': [...], 'reference'}.

    Raises
    ------
    ValueError
        If gradation is unrecognized, sieve_mm is not a tabulated size, or the
        requested sieve is not applicable (above the nominal max) for this
        gradation.
    """
    key = str(gradation).strip().lower().replace(" ", "_")
    if key not in _TABLE_2_1:
        raise ValueError(
            f"Unknown gradation '{gradation}'. Use: {', '.join(_TABLE_2_1)}"
        )
    row = _TABLE_2_1[key]
    ref = "UFC 3-250-03, Table 2-1 (pdf_page 17, printed p.4)"
    if sieve_mm is None:
        return {
            "gradation": key, "nominal_max_size_mm": row["nominal_max_size_mm"],
            "nominal_max_size_in": row["nominal_max_size_in"],
            "bands": [
                {"sieve_mm": s, "sieve_label": lbl, "percent_passing_min": lo,
                 "percent_passing_max": hi}
                for s, lbl, (lo, hi) in zip(_TABLE_2_1_SIEVES_MM, _TABLE_2_1_SIEVE_LABELS,
                                            row["bands"])
            ],
            "reference": ref,
        }
    if sieve_mm not in _TABLE_2_1_SIEVES_MM:
        raise ValueError(
            f"sieve_mm must be one of {_TABLE_2_1_SIEVES_MM}, got {sieve_mm}"
        )
    idx = _TABLE_2_1_SIEVES_MM.index(sieve_mm)
    lo, hi = row["bands"][idx]
    if lo is None:
        raise ValueError(
            f"Sieve {sieve_mm} mm is above the nominal maximum size for '{key}' "
            "(not tabulated -- assumed 100% passing)."
        )
    return {
        "gradation": key, "nominal_max_size_mm": row["nominal_max_size_mm"],
        "nominal_max_size_in": row["nominal_max_size_in"],
        "sieve_mm": sieve_mm, "sieve_label": _TABLE_2_1_SIEVE_LABELS[idx],
        "percent_passing_min": lo, "percent_passing_max": hi,
        "reference": ref,
    }


# ============================================================================
# Table 2-3: Asphalt Binder Base Grade Selection Criteria Based on Pavement
# Temperature Index (PTI) (Section 2-3.1.4.1; pdf_page 29, printed p.16)
# ============================================================================

_TABLE_2_3 = [
    # (pti_upper_c, region, criteria)
    (16.7, "cold", "120-150 penetration, PG (52,58)-xx"),
    (44.4, "warm", "85-100 penetration, PG 64-(22 or 28)"),
    (None, "hot", "60-70 penetration, PG (64, 70 or 76)-22"),
]


def table_2_3_asphalt_grade_by_pti(pti_c) -> dict:
    """Asphalt binder base grade selection by Pavement Temperature Index (Table 2-3).

    PTI is the cumulative sum of monthly average-maximum-temperature
    increments above 23.9 C (75 F) (Section 2-3.1.4.1). Use only when there is
    no local DOT guidance on asphalt cement grade.

    Parameters
    ----------
    pti_c : float
        Pavement Temperature Index, cumulative degrees C. Must be >= 0.

    Returns
    -------
    dict
        {'pti_c', 'pti_f', 'temperature_region', 'asphalt_cement_selection_criteria',
         'reference'}.

    Raises
    ------
    ValueError
        If pti_c < 0.
    """
    if pti_c < 0:
        raise ValueError(f"pti_c must be >= 0, got {pti_c}")
    pti_f = pti_c * 9.0 / 5.0
    for upper, region, criteria in _TABLE_2_3:
        if upper is None or pti_c < upper:
            return {
                "pti_c": pti_c, "pti_f": round(pti_f, 1),
                "temperature_region": region,
                "asphalt_cement_selection_criteria": criteria,
                "reference": "UFC 3-250-03, Table 2-3 (pdf_page 29, printed p.16)",
            }
    raise AssertionError("unreachable")  # pragma: no cover


# ============================================================================
# Table 2-5: Asphalt Cement Selection Criteria Based on Design Air-Freezing
# Index (DFI) (Section 2-3.1.4.3; pdf_page 32, printed p.19)
# ============================================================================


def table_2_5_asphalt_grade_by_freezing_index(dfi_c) -> dict:
    """Asphalt cement selection for cold regions by Design Air-Freezing Index (Table 2-5).

    Applies only after Table 2-3 (``table_2_3_asphalt_grade_by_pti``) has
    already classified the project as a "cold" region; the DFI further
    distinguishes moderately-cold from severely-cold climates. Use only when
    there is no local DOT guidance on asphalt cement grade. DFI determination
    itself is per UFC 3-260-02.

    Parameters
    ----------
    dfi_c : float
        Design Air-Freezing Index, cumulative degrees C. Must be >= 0.

    Returns
    -------
    dict
        {'dfi_c', 'dfi_f', 'temperature_region', 'asphalt_cement_selection_criteria',
         'reference'}.

    Raises
    ------
    ValueError
        If dfi_c < 0.
    """
    if dfi_c < 0:
        raise ValueError(f"dfi_c must be >= 0, got {dfi_c}")
    dfi_f = dfi_c * 9.0 / 5.0
    if dfi_c < 1667:
        region, criteria = "moderately_cold", "PG (52, 58)-(28, 34)"
    else:
        region, criteria = "severely_cold", "PG (52, 58)-(34, 40)"
    return {
        "dfi_c": dfi_c, "dfi_f": round(dfi_f, 1),
        "temperature_region": region,
        "asphalt_cement_selection_criteria": criteria,
        "reference": "UFC 3-250-03, Table 2-5 (pdf_page 32, printed p.19)",
    }


# ============================================================================
# Table 2-7: Minimum Percent Voids in Mineral Aggregate (VMA)
# (Section 2-4.2.6/2-4.2.10; pdf_page 49, printed p.36)
# ============================================================================

_TABLE_2_7 = {
    "gradation_1": {"nominal_max_size_mm": 25.0, "nominal_max_size_in": 1.0, "min_vma_pct": 13.0},
    "gradation_2": {"nominal_max_size_mm": 19.0, "nominal_max_size_in": 0.75, "min_vma_pct": 14.0},
    "gradation_3": {"nominal_max_size_mm": 12.5, "nominal_max_size_in": 0.5, "min_vma_pct": 15.0},
}


def table_2_7_minimum_vma(gradation) -> dict:
    """Minimum percent voids in mineral aggregate (VMA) by gradation type (Table 2-7).

    Note: this table's gradation numbering (by nominal max particle size, per
    UFGS 32 12 15.13) does NOT correspond one-to-one with Table 2-1's
    gradation_1/2/3 -- Table 2-1 gradation_1 is 19 mm, this table's
    gradation_1 is 25 mm. Select by nominal_max_size, not by matching gradation
    label across the two tables.

    Parameters
    ----------
    gradation : str
        'gradation_1' (25 mm / 1 in max particle size), 'gradation_2' (19 mm /
        3/4 in), or 'gradation_3' (12.5 mm / 1/2 in).

    Returns
    -------
    dict
        {'gradation', 'nominal_max_size_mm', 'nominal_max_size_in', 'min_vma_pct',
         'reference'}.

    Raises
    ------
    ValueError
        If gradation is unrecognized.
    """
    key = str(gradation).strip().lower().replace(" ", "_")
    if key not in _TABLE_2_7:
        raise ValueError(
            f"Unknown gradation '{gradation}'. Use: {', '.join(_TABLE_2_7)}"
        )
    row = _TABLE_2_7[key]
    return {
        "gradation": key, **row,
        "reference": "UFC 3-250-03, Table 2-7 (pdf_page 49, printed p.36)",
    }


# ============================================================================
# Table 2-8: Design Criteria (Marshall mix design -- optimum-AC determination
# and mix-acceptability criteria, by mix type and compaction level)
# (Section 2-4.2.6/2-4.2.10; pdf_page 52, printed p.39)
# ============================================================================

# Section 2: acceptability criteria (Section 1's optimum-AC-determination
# criteria are all "point of curve", i.e. procedural, not numeric -- not
# digitized as a lookup, see chapter text instead).
_TABLE_2_8 = {
    ("hma", "50_blows"): {
        "marshall_stability_min_kn": 6.0, "marshall_stability_min_lbf": 1350,
        "flow_max_0p25mm": 20, "vtm_pct_range": (3, 5),
        "vma_pct_note": "see table_2_7_minimum_vma",
        "vfa_pct_range": (75, 85),
    },
    ("hma", "75_blows"): {
        "marshall_stability_min_kn": 8.0, "marshall_stability_min_lbf": 1800,
        "flow_max_0p25mm": 16, "vtm_pct_range": (3, 5),
        "vma_pct_note": "see table_2_7_minimum_vma",
        "vfa_pct_range": (70, 80),
    },
    ("hma", "50_gyrations"): {
        "marshall_stability_min_kn": None, "marshall_stability_min_lbf": None,
        "flow_max_0p25mm": None, "vtm_pct_range": (3, 5),
        "vma_pct_note": "see table_2_7_minimum_vma",
        "vfa_pct_range": (75, 85),
        "note": "Superpave (gyratory) -- no flow/stability criteria.",
    },
    ("hma", "75_gyrations"): {
        "marshall_stability_min_kn": None, "marshall_stability_min_lbf": None,
        "flow_max_0p25mm": None, "vtm_pct_range": (3, 5),
        "vma_pct_note": "see table_2_7_minimum_vma",
        "vfa_pct_range": (70, 80),
        "note": "Superpave (gyratory) -- no flow/stability criteria.",
    },
    ("sand_asphalt", "50_blows"): {
        "marshall_stability_min_kn": None, "marshall_stability_min_lbf": 500,
        "flow_max_0p25mm": 20, "vtm_pct_range": (5, 7),
        "vma_pct_note": None, "vfa_pct_range": (65, 75),
        "note": "Not for pavements with tire pressures above 690 kPa (100 psi).",
    },
    ("sand_asphalt", "50_gyrations"): {
        "marshall_stability_min_kn": None, "marshall_stability_min_lbf": None,
        "flow_max_0p25mm": None, "vtm_pct_range": (5, 7),
        "vma_pct_note": None, "vfa_pct_range": (65, 75),
        "note": ("Superpave (gyratory) -- no flow/stability criteria. Not for "
                 "pavements with tire pressures above 690 kPa (100 psi)."),
    },
}


def table_2_8_marshall_design_criteria(mix_type, compaction, property=None) -> dict:
    """Marshall/Superpave mix acceptability criteria by mix type and compaction (Table 2-8).

    Section 2 of Table 2-8 -- criteria for judging whether a mix at its
    determined optimum asphalt content is acceptable. (Section 1, the
    procedure for locating the optimum-AC point on each property curve, is
    purely "point of curve" -- procedural, not a numeric lookup, and is
    covered in the chapter text instead.)

    Parameters
    ----------
    mix_type : str
        'hma' (HMA surface or intermediate course) or 'sand_asphalt'.
    compaction : str
        '50_blows', '75_blows' (Marshall hammer), '50_gyrations', or
        '75_gyrations' (Superpave gyratory compactor). Not every combination
        with mix_type is tabulated (e.g. sand_asphalt has no 75-blow/75-gyration
        row) -- an unavailable combination raises ValueError.
    property : str, optional
        If given, returns just that property's criterion: 'stability', 'flow',
        'vtm', 'vma', or 'vfa'. If omitted, returns the full criteria row.

    Returns
    -------
    dict
        Full row: {'mix_type', 'compaction', 'marshall_stability_min_kn',
        'marshall_stability_min_lbf', 'flow_max_0p25mm', 'vtm_pct_range',
        'vma_pct_note', 'vfa_pct_range', 'note'?, 'reference'}.
        Single property: {'mix_type', 'compaction', 'property', 'value',
        'reference'}.

    Raises
    ------
    ValueError
        If mix_type/compaction is not tabulated, or property is unrecognized.
    """
    mt = str(mix_type).strip().lower().replace(" ", "_")
    cp = str(compaction).strip().lower().replace(" ", "_").replace("-", "_")
    key = (mt, cp)
    if key not in _TABLE_2_8:
        raise ValueError(
            f"Combination mix_type='{mt}', compaction='{cp}' is not tabulated "
            f"(N/A in Table 2-8) or not recognized. Tabulated combinations: "
            f"{sorted(_TABLE_2_8.keys())}"
        )
    row = _TABLE_2_8[key]
    ref = "UFC 3-250-03, Table 2-8 (pdf_page 52, printed p.39)"
    if property is None:
        out = {"mix_type": mt, "compaction": cp, **row, "reference": ref}
        return out
    prop_map = {
        "stability": ("marshall_stability_min_kn", "marshall_stability_min_lbf"),
        "flow": ("flow_max_0p25mm",),
        "vtm": ("vtm_pct_range",),
        "vma": ("vma_pct_note",),
        "vfa": ("vfa_pct_range",),
    }
    pk = str(property).strip().lower()
    if pk not in prop_map:
        raise ValueError(
            f"Unknown property '{property}'. Use: stability, flow, vtm, vma, vfa"
        )
    value = {k: row.get(k) for k in prop_map[pk]}
    if len(value) == 1:
        value = next(iter(value.values()))
    return {"mix_type": mt, "compaction": cp, "property": pk, "value": value,
            "reference": ref}


# ============================================================================
# Table 2-12: Aggregate Gradation for PFCs (Porous Friction Course)
# (Section 2-5.1.1; pdf_page 64, printed p.51)
# ============================================================================

_TABLE_2_12_SIEVES_MM = [19.0, 12.5, 9.5, 4.75, 2.36, 0.60, 0.075]
_TABLE_2_12_SIEVE_LABELS = ["3/4 in", "1/2 in", "3/8 in", "No. 4", "No. 8", "No. 30", "No. 200"]

_TABLE_2_12 = {
    "gradation_a": {  # 19 mm max, compacted nominal thickness 25 mm (1 in)
        "nominal_max_size_mm": 19.0, "compacted_thickness_mm": 25.0, "compacted_thickness_in": 1.0,
        "bands": [(100, 100), (70, 100), (35, 75), (25, 40), (10, 20), (3, 10), (0, 5)],
    },
    "gradation_b": {  # 12.5 mm max, compacted nominal thickness 19 mm (3/4 in)
        "nominal_max_size_mm": 12.5, "compacted_thickness_mm": 19.0, "compacted_thickness_in": 0.75,
        "bands": [(100, 100), (100, 100), (80, 100), (25, 40), (10, 20), (3, 10), (0, 5)],
    },
}


def table_2_12_pfc_gradation(gradation, sieve_mm=None) -> dict:
    """Aggregate gradation band for Porous Friction Course (PFC) (Table 2-12).

    Parameters
    ----------
    gradation : str
        'gradation_a' (19 mm / 3/4 in max, ~25 mm compacted lift) or
        'gradation_b' (12.5 mm / 1/2 in max, ~19 mm compacted lift).
    sieve_mm : float, optional
        Sieve size, mm (one of 19.0, 12.5, 9.5, 4.75, 2.36, 0.60, 0.075). If
        omitted, returns the full gradation band table.

    Returns
    -------
    dict
        {'gradation', 'nominal_max_size_mm', 'compacted_thickness_mm',
         'compacted_thickness_in', 'sieve_mm', 'percent_passing_min',
         'percent_passing_max', 'reference'} if sieve_mm given, else with
         'bands': [...] instead.

    Raises
    ------
    ValueError
        If gradation is unrecognized or sieve_mm is not a tabulated size.
    """
    key = str(gradation).strip().lower().replace(" ", "_")
    if key not in _TABLE_2_12:
        raise ValueError(
            f"Unknown gradation '{gradation}'. Use: {', '.join(_TABLE_2_12)}"
        )
    row = _TABLE_2_12[key]
    ref = "UFC 3-250-03, Table 2-12 (pdf_page 64, printed p.51)"
    if sieve_mm is None:
        return {
            "gradation": key, "nominal_max_size_mm": row["nominal_max_size_mm"],
            "compacted_thickness_mm": row["compacted_thickness_mm"],
            "compacted_thickness_in": row["compacted_thickness_in"],
            "bands": [
                {"sieve_mm": s, "sieve_label": lbl, "percent_passing_min": lo,
                 "percent_passing_max": hi}
                for s, lbl, (lo, hi) in zip(_TABLE_2_12_SIEVES_MM, _TABLE_2_12_SIEVE_LABELS,
                                            row["bands"])
            ],
            "reference": ref,
        }
    if sieve_mm not in _TABLE_2_12_SIEVES_MM:
        raise ValueError(
            f"sieve_mm must be one of {_TABLE_2_12_SIEVES_MM}, got {sieve_mm}"
        )
    idx = _TABLE_2_12_SIEVES_MM.index(sieve_mm)
    lo, hi = row["bands"][idx]
    return {
        "gradation": key, "nominal_max_size_mm": row["nominal_max_size_mm"],
        "sieve_mm": sieve_mm, "sieve_label": _TABLE_2_12_SIEVE_LABELS[idx],
        "percent_passing_min": lo, "percent_passing_max": hi,
        "reference": ref,
    }


# ============================================================================
# Table 2-15 (in-body numbering): SMA Gradation Guideline
# (Section 2-6.1.1; pdf_page 70, printed p.57)
# ============================================================================

_TABLE_2_15_SIEVES_MM = [19.0, 12.7, 9.5, 4.75, 2.36, 0.60, 0.30, 0.075]
_TABLE_2_15_SIEVE_LABELS = ["3/4 in", "1/2 in", "3/8 in", "No. 4", "No. 8", "No. 30", "No. 50", "No. 200"]
_TABLE_2_15_BANDS = [(100, 100), (85, 95), (None, 75), (20, 28), (16, 24), (12, 16), (12, 15), (8, 10)]


def table_2_15_sma_gradation(sieve_mm=None) -> dict:
    """Stone Matrix Asphalt (SMA) gradation guideline (Table 2-15, per NAPA 1999).

    Note: the front-matter List of Tables mislabels this as "Table 2-13" --
    the in-body caption (authoritative) reads "Table 2-15".

    Parameters
    ----------
    sieve_mm : float, optional
        Sieve size, mm (one of 19.0, 12.7, 9.5, 4.75, 2.36, 0.60, 0.30, 0.075).
        If omitted, returns the full gradation band table. The 9.5 mm (3/8 in)
        row is a maximum-only criterion (75% max, no minimum).

    Returns
    -------
    dict
        {'sieve_mm', 'percent_passing_min', 'percent_passing_max', 'reference'}
        if sieve_mm given, else {'bands': [...], 'reference'}.

    Raises
    ------
    ValueError
        If sieve_mm is not a tabulated size.
    """
    ref = "UFC 3-250-03, Table 2-15 (pdf_page 70, printed p.57)"
    if sieve_mm is None:
        return {
            "bands": [
                {"sieve_mm": s, "sieve_label": lbl, "percent_passing_min": lo,
                 "percent_passing_max": hi}
                for s, lbl, (lo, hi) in zip(_TABLE_2_15_SIEVES_MM, _TABLE_2_15_SIEVE_LABELS,
                                            _TABLE_2_15_BANDS)
            ],
            "reference": ref,
        }
    if sieve_mm not in _TABLE_2_15_SIEVES_MM:
        raise ValueError(
            f"sieve_mm must be one of {_TABLE_2_15_SIEVES_MM}, got {sieve_mm}"
        )
    idx = _TABLE_2_15_SIEVES_MM.index(sieve_mm)
    lo, hi = _TABLE_2_15_BANDS[idx]
    return {
        "sieve_mm": sieve_mm, "sieve_label": _TABLE_2_15_SIEVE_LABELS[idx],
        "percent_passing_min": lo, "percent_passing_max": hi,
        "reference": ref,
    }


# ============================================================================
# Table 2-17: SMA Mix Design Requirements (after NAPA 1995)
# (Section 2-6.2.2; pdf_page 72, printed p.59)
# ============================================================================

_TABLE_2_17 = {
    "vtm_pct": (3, 4),
    "asphalt_content_pct_min": 6.0,
    "vma_pct_min": 17.0,
    "stability_min_n": 6200, "stability_min_lbf": 1400,
    "flow_0p25mm_range": (8, 16),
    "compaction_blows_each_side": 50,
    "draindown_pct_max_1hr": 0.3,
}


def table_2_17_sma_mix_design_requirements(parameter=None) -> dict:
    """Stone Matrix Asphalt (SMA) Marshall mix design requirements (Table 2-17).

    Parameters
    ----------
    parameter : str, optional
        If given, returns just that parameter: 'vtm', 'asphalt_content',
        'vma', 'stability', 'flow', 'compaction', or 'draindown'. If omitted,
        returns all parameters.

    Returns
    -------
    dict
        {'parameter', 'value', 'reference'} if parameter given, else
        {**all parameters, 'reference'}.

    Raises
    ------
    ValueError
        If parameter is given but unrecognized.
    """
    ref = "UFC 3-250-03, Table 2-17 (pdf_page 72, printed p.59)"
    if parameter is None:
        return {**_TABLE_2_17, "reference": ref}
    key_map = {
        "vtm": "vtm_pct", "asphalt_content": "asphalt_content_pct_min",
        "vma": "vma_pct_min", "stability": None, "flow": "flow_0p25mm_range",
        "compaction": "compaction_blows_each_side", "draindown": "draindown_pct_max_1hr",
    }
    pk = str(parameter).strip().lower()
    if pk not in key_map:
        raise ValueError(
            f"Unknown parameter '{parameter}'. Use: {', '.join(key_map)}"
        )
    if pk == "stability":
        value = {"stability_min_n": _TABLE_2_17["stability_min_n"],
                 "stability_min_lbf": _TABLE_2_17["stability_min_lbf"]}
    else:
        value = _TABLE_2_17[key_map[pk]]
    return {"parameter": pk, "value": value, "reference": ref}


# ============================================================================
# Spray application rates -- Chapter 3 (prime coat 3-2.2, tack coat 3-3.2,
# fog seal 3-4.2, rejuvenator 3-5.3). Each is a genuine numeric rate range
# given in the narrative text (no formal table number), consolidated into one
# lookup since they share the same shape.
# ============================================================================

_SPRAY_RATES = {
    "prime_coat": {
        "rate_l_per_m2": (0.45, 1.13), "rate_gal_per_yd2": (0.10, 0.25),
        "basis": "residual asphalt",
        "reference": "UFC 3-250-03, Section 3-2.2 (pdf_page 80, printed p.67)",
    },
    "tack_coat": {
        "rate_l_per_m2": (0.23, 0.68), "rate_gal_per_yd2": (0.05, 0.15),
        "basis": "residual asphalt",
        "reference": "UFC 3-250-03, Section 3-3.2 (pdf_page 82, printed p.69)",
    },
    "fog_seal": {
        "rate_l_per_m2": (0.14, 0.36), "rate_gal_per_yd2": (0.03, 0.08),
        "basis": "residual asphalt",
        "reference": "UFC 3-250-03, Section 3-4.2 (pdf_page 83, printed p.70)",
    },
    "rejuvenator": {
        "rate_l_per_m2": (0.18, 0.9), "rate_gal_per_yd2": (0.04, 0.2),
        "basis": "total liquid",
        "reference": "UFC 3-250-03, Section 3-5.3 (pdf_page 85, printed p.72)",
        "sand_cover_kg_per_m2": (0.27, 0.54), "sand_cover_lb_per_yd2": (0.5, 1.0),
        "sand_cover_note": ("Only when used as a rejuvenator-sealer; sand-sized "
                            "aggregate cover for initial skid resistance."),
    },
}


def spray_application_rate(application_type) -> dict:
    """Spray application rate range for prime coat / tack coat / fog seal / rejuvenator.

    Consolidates the narrative application-rate guidance from Sections 3-2.2,
    3-3.2, 3-4.2, and 3-5.3 (each a genuine numeric rate range given in prose,
    not a formal numbered table). Actual field rates are determined by test
    section per the source guidance -- these are the guide ranges only.

    Parameters
    ----------
    application_type : str
        'prime_coat', 'tack_coat', 'fog_seal', or 'rejuvenator'.

    Returns
    -------
    dict
        {'application_type', 'rate_l_per_m2', 'rate_gal_per_yd2', 'basis',
         'reference'}; 'rejuvenator' additionally carries
         'sand_cover_kg_per_m2', 'sand_cover_lb_per_yd2', 'sand_cover_note'
         (rejuvenator-sealer variant only).

    Raises
    ------
    ValueError
        If application_type is not recognized.
    """
    key = str(application_type).strip().lower().replace(" ", "_")
    if key not in _SPRAY_RATES:
        raise ValueError(
            f"Unknown application_type '{application_type}'. Use: "
            f"{', '.join(_SPRAY_RATES)}"
        )
    return {"application_type": key, **_SPRAY_RATES[key]}


# ============================================================================
# Table 3-2: Tack Coat Materials and Spray Application Temperatures
# (Section 3-3.1; pdf_page 82, printed p.69)
# ============================================================================

_TABLE_3_2 = {
    ("cutback", "rc_70"): (49, 93, 120, 200),
    ("cutback", "rc_250"): (74, 121, 165, 250),
    ("emulsion", "rs_1"): (21, 60, 70, 140),
    ("emulsion", "ms_1"): (21, 71, 70, 160),
    ("emulsion", "hfms_1"): (21, 71, 70, 160),
    ("emulsion", "ss_1"): (21, 71, 70, 160),
    ("emulsion", "ss_1h"): (21, 71, 70, 160),
    ("emulsion", "crs_1"): (52, 85, 125, 185),
    ("emulsion", "css_1"): (21, 71, 70, 160),
    ("emulsion", "css_1h"): (21, 71, 70, 160),
    ("asphalt_cement", "200_300_pen"): (129, None, 265, None),
    ("asphalt_cement", "120_150_pen"): (132, None, 270, None),
    ("asphalt_cement", "85_100_pen"): (138, None, 280, None),
    ("asphalt_cement", "ac_2.5"): (132, None, 270, None),
    ("asphalt_cement", "ac_5"): (138, None, 280, None),
    ("asphalt_cement", "ac_10"): (138, None, 280, None),
    ("asphalt_cement", "ar_1000"): (135, None, 275, None),
    ("asphalt_cement", "ar_2000"): (141, None, 285, None),
    ("asphalt_cement", "ar_4000"): (143, None, 290, None),
    ("asphalt_cement", "pg_58_22_64_22"): (143, None, 290, None),
}


def table_3_2_tack_coat_temperature(material_type, grade) -> dict:
    """Tack coat spray application temperature by material type and grade (Table 3-2).

    For asphalt-cement grades, only a minimum application temperature is
    given (the "+"-suffixed values in the source table); ``temp_c_max`` and
    ``temp_f_max`` are None in that case.

    Parameters
    ----------
    material_type : str
        'cutback', 'emulsion', or 'asphalt_cement'.
    grade : str
        Grade designation, e.g. 'rc_70', 'rc_250' (cutback); 'rs_1', 'ms_1',
        'hfms_1', 'ss_1', 'ss_1h', 'crs_1', 'css_1', 'css_1h' (emulsion);
        '200_300_pen', '120_150_pen', '85_100_pen', 'ac_2.5', 'ac_5', 'ac_10',
        'ar_1000', 'ar_2000', 'ar_4000', 'pg_58_22_64_22' (asphalt cement).

    Returns
    -------
    dict
        {'material_type', 'grade', 'temp_c_min', 'temp_c_max', 'temp_f_min',
         'temp_f_max', 'reference'}.

    Raises
    ------
    ValueError
        If the material_type/grade combination is not tabulated.
    """
    mt = str(material_type).strip().lower().replace(" ", "_")
    gr = str(grade).strip().lower().replace(" ", "_").replace("-", "_")
    key = (mt, gr)
    if key not in _TABLE_3_2:
        raise ValueError(
            f"Unknown (material_type, grade) combination '{key}'. "
            f"Valid combinations: {sorted(_TABLE_3_2.keys())}"
        )
    c_min, c_max, f_min, f_max = _TABLE_3_2[key]
    return {
        "material_type": mt, "grade": gr,
        "temp_c_min": c_min, "temp_c_max": c_max,
        "temp_f_min": f_min, "temp_f_max": f_max,
        "reference": "UFC 3-250-03, Table 3-2 (pdf_page 82, printed p.69)",
    }


# ============================================================================
# Table 4-2: Gradations for Single Bituminous Surface Treatment (SBST)
# (Section 4-2.1.2; pdf_page 91, printed p.78)
# ============================================================================

_TABLE_4_2_SIEVES_MM = [25.0, 19.0, 12.5, 9.5, 4.75, 2.36, 1.18]
_TABLE_4_2_SIEVE_LABELS = ["1 in", "3/4 in", "1/2 in", "3/8 in", "No. 4", "No. 8", "No. 16"]

_TABLE_4_2 = {
    "no_1": {"astm_d448_no": "6", "bands": [(100, 100), (90, 100), (20, 55), (0, 15), (0, 5), (None, None), (None, None)]},
    "no_2": {"astm_d448_no": "7", "bands": [(None, None), (100, 100), (90, 100), (40, 70), (0, 15), (0, 5), (None, None)]},
    "no_3": {"astm_d448_no": "8", "bands": [(None, None), (None, None), (100, 100), (85, 100), (10, 30), (0, 10), (0, 5)]},
}


def table_4_2_gradation_sbst(designation, sieve_mm=None) -> dict:
    """Aggregate gradation band for Single Bituminous Surface Treatment (SBST) (Table 4-2).

    Parameters
    ----------
    designation : str
        'no_1' (ASTM D448 No. 6), 'no_2' (No. 7), or 'no_3' (No. 8) --
        decreasing aggregate size.
    sieve_mm : float, optional
        Sieve size, mm (one of 25.0, 19.0, 12.5, 9.5, 4.75, 2.36, 1.18). If
        omitted, returns the full gradation band table.

    Returns
    -------
    dict
        {'designation', 'astm_d448_no', 'sieve_mm', 'percent_passing_min',
         'percent_passing_max', 'reference'} if sieve_mm given, else with
         'bands': [...] instead.

    Raises
    ------
    ValueError
        If designation is unrecognized, sieve_mm is not tabulated, or the
        sieve is above the nominal max for that designation.
    """
    key = str(designation).strip().lower().replace(" ", "_").replace(".", "_").replace("-", "_")
    if key not in _TABLE_4_2:
        raise ValueError(
            f"Unknown designation '{designation}'. Use: {', '.join(_TABLE_4_2)}"
        )
    row = _TABLE_4_2[key]
    ref = "UFC 3-250-03, Table 4-2 (pdf_page 91, printed p.78)"
    if sieve_mm is None:
        return {
            "designation": key, "astm_d448_no": row["astm_d448_no"],
            "bands": [
                {"sieve_mm": s, "sieve_label": lbl, "percent_passing_min": lo,
                 "percent_passing_max": hi}
                for s, lbl, (lo, hi) in zip(_TABLE_4_2_SIEVES_MM, _TABLE_4_2_SIEVE_LABELS,
                                            row["bands"])
            ],
            "reference": ref,
        }
    if sieve_mm not in _TABLE_4_2_SIEVES_MM:
        raise ValueError(
            f"sieve_mm must be one of {_TABLE_4_2_SIEVES_MM}, got {sieve_mm}"
        )
    idx = _TABLE_4_2_SIEVES_MM.index(sieve_mm)
    lo, hi = row["bands"][idx]
    if lo is None:
        raise ValueError(
            f"Sieve {sieve_mm} mm is above the nominal maximum for designation "
            f"'{key}' (not tabulated)."
        )
    return {
        "designation": key, "astm_d448_no": row["astm_d448_no"],
        "sieve_mm": sieve_mm, "sieve_label": _TABLE_4_2_SIEVE_LABELS[idx],
        "percent_passing_min": lo, "percent_passing_max": hi,
        "reference": ref,
    }


# ============================================================================
# Table 4-3: Gradations for Double Bituminous Surface Treatment (DBST)
# (Section 4-2.1.2; pdf_page 91, printed p.78)
# ============================================================================

_TABLE_4_3_SIEVES_MM = [25.0, 19.0, 12.5, 9.5, 4.75, 2.36, 1.18, 0.30]
_TABLE_4_3_SIEVE_LABELS = ["1 in", "3/4 in", "1/2 in", "3/8 in", "No. 4", "No. 8", "No. 16", "No. 50"]

_TABLE_4_3 = {
    "no_1": {"astm_d448_no": "6", "spreading": "first",
             "bands": [(100, 100), (90, 100), (20, 55), (0, 15), (0, 5), (None, None), (None, None), (None, None)]},
    "no_2": {"astm_d448_no": "8", "spreading": "second",
             "bands": [(None, None), (None, None), (100, 100), (85, 100), (10, 30), (0, 10), (0, 5), (None, None)]},
    "no_3": {"astm_d448_no": "7", "spreading": "first",
             "bands": [(None, None), (100, 100), (90, 100), (40, 70), (0, 15), (0, 5), (None, None), (None, None)]},
    "no_4": {"astm_d448_no": "9", "spreading": "second",
             "bands": [(None, None), (None, None), (None, None), (100, 100), (85, 100), (10, 40), (0, 10), (0, 5)]},
}


def table_4_3_gradation_dbst(designation, sieve_mm=None) -> dict:
    """Aggregate gradation band for Double Bituminous Surface Treatment (DBST) (Table 4-3).

    DBST uses two paired spreadings: designations 'no_1' (first spreading) +
    'no_2' (second spreading) form one aggregate-size pairing; 'no_3' (first
    spreading) + 'no_4' (second spreading) form the other, coarser pairing.

    Parameters
    ----------
    designation : str
        'no_1', 'no_2', 'no_3', or 'no_4' (see ``spreading`` in the returned
        dict for whether it is the first or second spreading of its pairing).
    sieve_mm : float, optional
        Sieve size, mm (one of 25.0, 19.0, 12.5, 9.5, 4.75, 2.36, 1.18, 0.30).
        If omitted, returns the full gradation band table.

    Returns
    -------
    dict
        {'designation', 'astm_d448_no', 'spreading', 'sieve_mm',
         'percent_passing_min', 'percent_passing_max', 'reference'} if
         sieve_mm given, else with 'bands': [...] instead.

    Raises
    ------
    ValueError
        If designation is unrecognized, sieve_mm is not tabulated, or the
        sieve is above the nominal max for that designation.
    """
    key = str(designation).strip().lower().replace(" ", "_").replace(".", "_").replace("-", "_")
    if key not in _TABLE_4_3:
        raise ValueError(
            f"Unknown designation '{designation}'. Use: {', '.join(_TABLE_4_3)}"
        )
    row = _TABLE_4_3[key]
    ref = "UFC 3-250-03, Table 4-3 (pdf_page 91, printed p.78)"
    if sieve_mm is None:
        return {
            "designation": key, "astm_d448_no": row["astm_d448_no"],
            "spreading": row["spreading"],
            "bands": [
                {"sieve_mm": s, "sieve_label": lbl, "percent_passing_min": lo,
                 "percent_passing_max": hi}
                for s, lbl, (lo, hi) in zip(_TABLE_4_3_SIEVES_MM, _TABLE_4_3_SIEVE_LABELS,
                                            row["bands"])
            ],
            "reference": ref,
        }
    if sieve_mm not in _TABLE_4_3_SIEVES_MM:
        raise ValueError(
            f"sieve_mm must be one of {_TABLE_4_3_SIEVES_MM}, got {sieve_mm}"
        )
    idx = _TABLE_4_3_SIEVES_MM.index(sieve_mm)
    lo, hi = row["bands"][idx]
    if lo is None:
        raise ValueError(
            f"Sieve {sieve_mm} mm is above the nominal maximum for designation "
            f"'{key}' (not tabulated)."
        )
    return {
        "designation": key, "astm_d448_no": row["astm_d448_no"],
        "spreading": row["spreading"], "sieve_mm": sieve_mm,
        "sieve_label": _TABLE_4_3_SIEVE_LABELS[idx],
        "percent_passing_min": lo, "percent_passing_max": hi,
        "reference": ref,
    }


# ============================================================================
# Table 4-4: Slurry Seal Aggregate Gradations
# (Section 4-3.2.2; pdf_page 95, printed p.82)
# ============================================================================

_TABLE_4_4_SIEVES_MM = [9.5, 4.75, 2.36, 1.18, 0.60, 0.30, 0.15, 0.075]
_TABLE_4_4_SIEVE_LABELS = ["3/8 in", "No. 4", "No. 8", "No. 16", "No. 30", "No. 50", "No. 100", "No. 200"]

_TABLE_4_4 = {
    "type_1": [(None, None), (100, 100), (90, 100), (65, 90), (40, 65), (25, 42), (15, 30), (10, 20)],
    "type_2": [(100, 100), (90, 100), (65, 90), (45, 70), (30, 50), (18, 30), (10, 21), (5, 15)],
    "type_3": [(100, 100), (70, 90), (45, 70), (28, 50), (19, 34), (12, 25), (7, 18), (5, 15)],
}


def table_4_4_slurry_seal_gradation(type_, sieve_mm=None) -> dict:
    """Slurry seal aggregate gradation band by type (Table 4-4).

    Type 1 is the finest gradation (not used for micro-surfacing, see
    ``table_4_7_micro_surfacing_gradation``); Type 3 is the coarsest.

    Parameters
    ----------
    type_ : str
        'type_1', 'type_2', or 'type_3'.
    sieve_mm : float, optional
        Sieve size, mm (one of 9.5, 4.75, 2.36, 1.18, 0.60, 0.30, 0.15, 0.075).
        If omitted, returns the full gradation band table.

    Returns
    -------
    dict
        {'type', 'sieve_mm', 'percent_passing_min', 'percent_passing_max',
         'reference'} if sieve_mm given, else with 'bands': [...] instead.

    Raises
    ------
    ValueError
        If type_ is unrecognized, sieve_mm is not tabulated, or (Type 1 only)
        the sieve is above its nominal maximum.
    """
    key = str(type_).strip().lower().replace(" ", "_")
    if key not in _TABLE_4_4:
        raise ValueError(
            f"Unknown type_ '{type_}'. Use: {', '.join(_TABLE_4_4)}"
        )
    bands = _TABLE_4_4[key]
    ref = "UFC 3-250-03, Table 4-4 (pdf_page 95, printed p.82)"
    if sieve_mm is None:
        return {
            "type": key,
            "bands": [
                {"sieve_mm": s, "sieve_label": lbl, "percent_passing_min": lo,
                 "percent_passing_max": hi}
                for s, lbl, (lo, hi) in zip(_TABLE_4_4_SIEVES_MM, _TABLE_4_4_SIEVE_LABELS, bands)
            ],
            "reference": ref,
        }
    if sieve_mm not in _TABLE_4_4_SIEVES_MM:
        raise ValueError(
            f"sieve_mm must be one of {_TABLE_4_4_SIEVES_MM}, got {sieve_mm}"
        )
    idx = _TABLE_4_4_SIEVES_MM.index(sieve_mm)
    lo, hi = bands[idx]
    if lo is None:
        raise ValueError(
            f"Sieve {sieve_mm} mm is above the nominal maximum for type '{key}' "
            "(not tabulated)."
        )
    return {
        "type": key, "sieve_mm": sieve_mm, "sieve_label": _TABLE_4_4_SIEVE_LABELS[idx],
        "percent_passing_min": lo, "percent_passing_max": hi,
        "reference": ref,
    }


# ============================================================================
# Table 4-5: Fuel-Resistant Sealer (FRS) Minimum Application Rates and
# Corresponding Aggregate Gradations (Section 4-4.4.1; pdf_page 99, printed p.86)
# ============================================================================

_TABLE_4_5_SIEVES_MM = [1.18, 0.85, 0.60, 0.425, 0.30, 0.212, 0.15, 0.106]
_TABLE_4_5_SIEVE_LABELS = ["No. 16", "No. 20", "No. 30", "No. 40", "No. 50", "No. 70", "No. 100", "No. 140"]

_TABLE_4_5 = {
    "coarse": {
        "min_rate_l_per_m2": 1.35, "min_rate_gal_per_yd2": 0.3,
        "bands": [(100, 100), (85, 100), (25, 85), (5, 25), (2, 10), (None, None), (0, 2), (None, None)],
    },
    "medium": {
        "min_rate_l_per_m2": 1.0, "min_rate_gal_per_yd2": 0.22,
        "bands": [(100, 100), (98, 100), (85, 100), (25, 85), (5, 25), (2, 10), (0, 4), (0, 2)],
    },
    "fine": {
        "min_rate_l_per_m2": 0.72, "min_rate_gal_per_yd2": 0.16,
        "bands": [(100, 100), (100, 100), (98, 100), (85, 100), (25, 85), (5, 25), (2, 10), (0, 2)],
    },
}


def table_4_5_frs_application_rate(gradation, sieve_mm=None) -> dict:
    """Fuel-Resistant Sealer (FRS) minimum application rate and gradation (Table 4-5).

    The coarser the gradation, the thicker (higher-rate) the application
    required to embed the aggregate (Section 4-4.4.1).

    Parameters
    ----------
    gradation : str
        'coarse', 'medium', or 'fine'.
    sieve_mm : float, optional
        Sieve size, mm (one of 1.18, 0.85, 0.60, 0.425, 0.30, 0.212, 0.15,
        0.106). If given, returns just that sieve's percent-passing band
        (plus the rate); if omitted, returns the full gradation band table
        (plus the rate).

    Returns
    -------
    dict
        {'gradation', 'min_rate_l_per_m2', 'min_rate_gal_per_yd2', 'sieve_mm',
         'percent_passing_min', 'percent_passing_max', 'reference'} if
         sieve_mm given, else with 'bands': [...] instead.

    Raises
    ------
    ValueError
        If gradation is unrecognized, sieve_mm is not tabulated, or the sieve
        is not applicable for that gradation.
    """
    key = str(gradation).strip().lower()
    if key not in _TABLE_4_5:
        raise ValueError(
            f"Unknown gradation '{gradation}'. Use: {', '.join(_TABLE_4_5)}"
        )
    row = _TABLE_4_5[key]
    ref = "UFC 3-250-03, Table 4-5 (pdf_page 99, printed p.86)"
    base = {"gradation": key, "min_rate_l_per_m2": row["min_rate_l_per_m2"],
            "min_rate_gal_per_yd2": row["min_rate_gal_per_yd2"]}
    if sieve_mm is None:
        base["bands"] = [
            {"sieve_mm": s, "sieve_label": lbl, "percent_passing_min": lo,
             "percent_passing_max": hi}
            for s, lbl, (lo, hi) in zip(_TABLE_4_5_SIEVES_MM, _TABLE_4_5_SIEVE_LABELS, row["bands"])
        ]
        base["reference"] = ref
        return base
    if sieve_mm not in _TABLE_4_5_SIEVES_MM:
        raise ValueError(
            f"sieve_mm must be one of {_TABLE_4_5_SIEVES_MM}, got {sieve_mm}"
        )
    idx = _TABLE_4_5_SIEVES_MM.index(sieve_mm)
    lo, hi = row["bands"][idx]
    if lo is None:
        raise ValueError(
            f"Sieve {sieve_mm} mm is not applicable for gradation '{key}' "
            "(not tabulated)."
        )
    base.update({"sieve_mm": sieve_mm, "sieve_label": _TABLE_4_5_SIEVE_LABELS[idx],
                "percent_passing_min": lo, "percent_passing_max": hi, "reference": ref})
    return base


# ============================================================================
# Table 4-7: Gradation Types for Micro-Surfacing
# (Section 4-5.2.3; pdf_page 102, printed p.89)
# ============================================================================

_TABLE_4_7 = {
    "type_2": [(100, 100), (90, 100), (65, 90), (45, 70), (30, 50), (18, 30), (10, 21), (5, 15)],
    "type_3": [(100, 100), (70, 90), (45, 70), (28, 50), (19, 34), (12, 25), (7, 18), (5, 15)],
}


def table_4_7_micro_surfacing_gradation(type_, sieve_mm=None) -> dict:
    """Micro-surfacing aggregate gradation band by type (Table 4-7).

    Same gradation bands as slurry seal Types 2 and 3 (Table 4-4) -- Type 1
    (finest slurry-seal gradation) is not used for micro-surfacing.

    Parameters
    ----------
    type_ : str
        'type_2' or 'type_3'.
    sieve_mm : float, optional
        Sieve size, mm (one of 9.5, 4.75, 2.36, 1.18, 0.60, 0.30, 0.15,
        0.075). If omitted, returns the full gradation band table.

    Returns
    -------
    dict
        {'type', 'sieve_mm', 'percent_passing_min', 'percent_passing_max',
         'reference'} if sieve_mm given, else with 'bands': [...] instead.

    Raises
    ------
    ValueError
        If type_ is unrecognized or sieve_mm is not tabulated.
    """
    key = str(type_).strip().lower().replace(" ", "_")
    if key not in _TABLE_4_7:
        raise ValueError(f"Unknown type_ '{type_}'. Use: {', '.join(_TABLE_4_7)}")
    bands = _TABLE_4_7[key]
    ref = "UFC 3-250-03, Table 4-7 (pdf_page 102, printed p.89)"
    if sieve_mm is None:
        return {
            "type": key,
            "bands": [
                {"sieve_mm": s, "sieve_label": lbl, "percent_passing_min": lo,
                 "percent_passing_max": hi}
                for s, lbl, (lo, hi) in zip(_TABLE_4_4_SIEVES_MM, _TABLE_4_4_SIEVE_LABELS, bands)
            ],
            "reference": ref,
        }
    if sieve_mm not in _TABLE_4_4_SIEVES_MM:
        raise ValueError(
            f"sieve_mm must be one of {_TABLE_4_4_SIEVES_MM}, got {sieve_mm}"
        )
    idx = _TABLE_4_4_SIEVES_MM.index(sieve_mm)
    lo, hi = bands[idx]
    return {
        "type": key, "sieve_mm": sieve_mm, "sieve_label": _TABLE_4_4_SIEVE_LABELS[idx],
        "percent_passing_min": lo, "percent_passing_max": hi,
        "reference": ref,
    }


# ============================================================================
# Table 6-1: Typical Aggregate Gradations for Plant-Mix Cold-Laid Asphalt
# Mixtures (Section 6-5.1.2; pdf_page 115, printed p.102)
# ============================================================================

_TABLE_6_1_SIEVES_MM = [12.5, 9.5, 4.75, 2.36, 1.18, 0.60, 0.30, 0.15, 0.075]
_TABLE_6_1_SIEVE_LABELS = ["1/2 in", "3/8 in", "No. 4", "No. 8", "No. 16", "No. 30", "No. 50", "No. 100", "No. 200"]

# Dense-graded columns are center +/- tolerance; open-graded columns are min-max ranges.
_TABLE_6_1_DENSE = {
    1: [(100, 0), (86, 9), (66, 9), (53, 9), (41, 9), (31, 9), (21, 8), (13, 6), (4.5, 1.5)],
    2: [(None, None), (100, 0), (85, 9), (71, 9), (57, 9), (43, 9), (31, 8), (19, 6), (6, 3)],
}
_TABLE_6_1_OPEN = {
    1: [(100, 100), (90, 100), (20, 55), (5, 30), (0, 10), (None, None), (0, 5), (None, None), (0, 2)],
    2: [(100, 100), (90, 100), (40, 75), (25, 55), (10, 30), (None, None), (3, 15), (None, None), (0, 6)],
}


def table_6_1_cold_mix_gradation(mix_type, column, sieve_mm=None) -> dict:
    """Typical aggregate gradation for plant-mix cold-laid asphalt mixtures (Table 6-1).

    Open gradations provide greater workability in colder weather than dense
    gradations (Section 6-5.1.2). Two columns are tabulated for each mix_type
    (two representative gradings); dense-graded bands are given as center +/-
    tolerance in the source, open-graded bands as explicit min-max ranges.

    Parameters
    ----------
    mix_type : str
        'dense_graded' or 'open_graded'.
    column : int
        1 or 2 (the two tabulated gradings for that mix_type).
    sieve_mm : float, optional
        Sieve size, mm (one of 12.5, 9.5, 4.75, 2.36, 1.18, 0.60, 0.30, 0.15,
        0.075). If omitted, returns the full gradation band table.

    Returns
    -------
    dict
        For dense_graded: {'mix_type', 'column', 'sieve_mm',
        'percent_passing_center', 'percent_passing_tolerance', 'reference'}
        (or 'bands': [...] of the same shape if sieve_mm omitted).
        For open_graded: {'mix_type', 'column', 'sieve_mm',
        'percent_passing_min', 'percent_passing_max', 'reference'} (or
        'bands': [...] if sieve_mm omitted).

    Raises
    ------
    ValueError
        If mix_type/column is unrecognized, sieve_mm is not tabulated, or the
        sieve is not applicable for that column.
    """
    mt = str(mix_type).strip().lower().replace(" ", "_")
    if mt not in ("dense_graded", "open_graded"):
        raise ValueError(f"mix_type must be 'dense_graded' or 'open_graded', got '{mix_type}'")
    col = int(column)
    table = _TABLE_6_1_DENSE if mt == "dense_graded" else _TABLE_6_1_OPEN
    if col not in table:
        raise ValueError(f"column must be one of {sorted(table.keys())}, got {col}")
    bands = table[col]
    ref = "UFC 3-250-03, Table 6-1 (pdf_page 115, printed p.102)"
    is_dense = mt == "dense_graded"
    key1, key2 = ("percent_passing_center", "percent_passing_tolerance") if is_dense else \
                 ("percent_passing_min", "percent_passing_max")

    def _row(s, lbl, pair):
        a, b = pair
        return {"sieve_mm": s, "sieve_label": lbl, key1: a, key2: b}

    if sieve_mm is None:
        return {
            "mix_type": mt, "column": col,
            "bands": [_row(s, lbl, p) for s, lbl, p in
                     zip(_TABLE_6_1_SIEVES_MM, _TABLE_6_1_SIEVE_LABELS, bands)],
            "reference": ref,
        }
    if sieve_mm not in _TABLE_6_1_SIEVES_MM:
        raise ValueError(f"sieve_mm must be one of {_TABLE_6_1_SIEVES_MM}, got {sieve_mm}")
    idx = _TABLE_6_1_SIEVES_MM.index(sieve_mm)
    a, b = bands[idx]
    if a is None:
        raise ValueError(
            f"Sieve {sieve_mm} mm is not tabulated for mix_type='{mt}', column={col}."
        )
    out = {"mix_type": mt, "column": col, "sieve_mm": sieve_mm,
           "sieve_label": _TABLE_6_1_SIEVE_LABELS[idx], key1: a, key2: b, "reference": ref}
    return out


# ============================================================================
# Table 6-2: Selection of Asphalt Type and Grade for cold-mix asphalt
# (Section 6-5.1.2; pdf_page 116, printed p.103)
# ============================================================================

_TABLE_6_2 = {
    "cold": {
        "kerosene_l_per_metric_ton": 8.3, "kerosene_gal_per_ton": 2.0,
        "kerosene_added_to": "AC-20, 85-100 pen, and PG 58-22",
        "cutback_range": "RC-70-RC-250",
        "emulsion_immediate_use": ["MS-2h", "SS-1h"],
        "emulsion_stockpile": [],
    },
    "moderate": {
        "kerosene_l_per_metric_ton": 7.1, "kerosene_gal_per_ton": 1.7,
        "kerosene_added_to": "AC-20, 85-100 pen, and PG 58-22",
        "cutback_range": "RC-250-RC-800",
        "emulsion_immediate_use": ["MS-2", "SS-1"],
        "emulsion_stockpile": ["MS-2h", "SS-1h"],
    },
    "hot": {
        "kerosene_l_per_metric_ton": 6.3, "kerosene_gal_per_ton": 1.5,
        "kerosene_added_to": "AC-20, 85-100 pen, and PG 58-22",
        "cutback_range": "RC-800-RC-3000",
        "emulsion_immediate_use": ["MS-2", "SS-1"],
        "emulsion_stockpile": [],
    },
}

_TABLE_6_2_CLIMATE_BOUNDS = {"cold": (None, 16), "moderate": (16, 27), "hot": (27, None)}


def table_6_2_cold_mix_asphalt_selection(climate) -> dict:
    """Asphalt type and grade selection for cold-mix asphalt by climate (Table 6-2).

    Parameters
    ----------
    climate : str
        'cold' (< 16 C / 60 F), 'moderate' (16-27 C / 60-80 F), or 'hot'
        (> 27 C / 80 F) -- climatic conditions during construction or storage.

    Returns
    -------
    dict
        {'climate', 'temp_c_range', 'kerosene_l_per_metric_ton',
         'kerosene_gal_per_ton', 'kerosene_added_to', 'cutback_range',
         'emulsion_immediate_use', 'emulsion_stockpile', 'reference'}.
        ``emulsion_stockpile`` lists emulsions specifically formulated for
        stockpiling (empty list where the source gives none for that
        climate); ``kerosene_*`` applies when the mix is stockpiled for
        future use.

    Raises
    ------
    ValueError
        If climate is not recognized.
    """
    key = str(climate).strip().lower()
    if key not in _TABLE_6_2:
        raise ValueError(f"Unknown climate '{climate}'. Use: {', '.join(_TABLE_6_2)}")
    return {
        "climate": key, "temp_c_range": _TABLE_6_2_CLIMATE_BOUNDS[key],
        **_TABLE_6_2[key],
        "reference": "UFC 3-250-03, Table 6-2 (pdf_page 116, printed p.103)",
    }


# ============================================================================
# Table 6-3: Selection of Optimum Asphalt Content (cold-mix asphalt)
# (Section 6-5.1.3.3; pdf_page 117, printed p.104)
# ============================================================================

_TABLE_6_3 = {
    "unit_weight": "peak_of_curve",
    "vtm_pct": (3, 5),  # 4 +/- 1
    "vfa_pct": (70, 80),  # 75 +/- 5
}


def table_6_3_cold_mix_optimum_ac_selection(property_=None) -> dict:
    """Criteria for selecting optimum asphalt content, cold-mix asphalt (Table 6-3).

    The optimum AC content is the average of the asphalt contents
    corresponding to these mix properties (Section 6-5.1.3.3).

    Parameters
    ----------
    property_ : str, optional
        If given, returns just that criterion: 'unit_weight', 'vtm', or
        'vfa'. If omitted, returns all three.

    Returns
    -------
    dict
        {'property', 'value', 'reference'} if property_ given, else
        {'unit_weight', 'vtm_pct', 'vfa_pct', 'reference'}.

    Raises
    ------
    ValueError
        If property_ is given but unrecognized.
    """
    ref = "UFC 3-250-03, Table 6-3 (pdf_page 117, printed p.104)"
    if property_ is None:
        return {**_TABLE_6_3, "reference": ref}
    key_map = {"unit_weight": "unit_weight", "vtm": "vtm_pct", "vfa": "vfa_pct"}
    pk = str(property_).strip().lower()
    if pk not in key_map:
        raise ValueError(f"Unknown property_ '{property_}'. Use: unit_weight, vtm, vfa")
    return {"property": pk, "value": _TABLE_6_3[key_map[pk]], "reference": ref}


# ============================================================================
# Table 6-4: Mixing Temperatures for Asphalt Materials (cold-mix asphalt)
# (Section 6-5.2.1; pdf_page 118, printed p.105)
# ============================================================================

_TABLE_6_4 = {
    ("emulsified", "ms_2"): (38, 71, 100, 160),
    ("emulsified", "ms_2h"): (38, 71, 100, 160),
    ("emulsified", "ss_1"): (24, 54, 75, 130),
    ("emulsified", "ss_1h"): (24, 54, 75, 130),
    ("cutback", "rc_70"): (38, 57, 100, 135),
    ("cutback", "rc_250"): (57, 79, 135, 175),
    ("cutback", "rc_800"): (77, 96, 170, 205),
    ("cutback", "mc_70"): (38, 57, 100, 135),
    ("cutback", "mc_250"): (57, 79, 135, 175),
    ("cutback", "mc_800"): (77, 96, 170, 205),
}


def table_6_4_mixing_temperature(material_type, grade) -> dict:
    """Mixing temperature range for asphalt materials, cold-mix asphalt pugmill (Table 6-4).

    Parameters
    ----------
    material_type : str
        'emulsified' or 'cutback'.
    grade : str
        'ms_2', 'ms_2h', 'ss_1', 'ss_1h' (emulsified); 'rc_70', 'rc_250',
        'rc_800', 'mc_70', 'mc_250', 'mc_800' (cutback).

    Returns
    -------
    dict
        {'material_type', 'grade', 'temp_c_min', 'temp_c_max', 'temp_f_min',
         'temp_f_max', 'reference'}.

    Raises
    ------
    ValueError
        If the material_type/grade combination is not tabulated.
    """
    mt = str(material_type).strip().lower()
    gr = str(grade).strip().lower().replace(" ", "_").replace("-", "_")
    key = (mt, gr)
    if key not in _TABLE_6_4:
        raise ValueError(
            f"Unknown (material_type, grade) combination '{key}'. "
            f"Valid combinations: {sorted(_TABLE_6_4.keys())}"
        )
    c_min, c_max, f_min, f_max = _TABLE_6_4[key]
    return {
        "material_type": mt, "grade": gr,
        "temp_c_min": c_min, "temp_c_max": c_max,
        "temp_f_min": f_min, "temp_f_max": f_max,
        "reference": "UFC 3-250-03, Table 6-4 (pdf_page 118, printed p.105)",
    }


# ============================================================================
# Table 7-2: Gradation Limits for Open-Graded Asphalt Mixture (RMP)
# (Section 7-2.1.1; pdf_page 123, printed p.110)
# ============================================================================

_TABLE_7_2_SIEVES_MM = [19.0, 12.5, 9.5, 4.75, 2.36, 0.60, 0.075]
_TABLE_7_2_SIEVE_LABELS = ["3/4 in", "1/2 in", "3/8 in", "No. 4", "No. 8", "No. 30", "No. 200"]
_TABLE_7_2_BANDS = [(100, 100), (54, 76), (38, 60), (10, 26), (8, 16), (4, 10), (1, 3)]


def table_7_2_ogam_gradation(sieve_mm=None) -> dict:
    """Gradation limits for the open-graded asphalt mixture (OGAM) course of RMP (Table 7-2).

    Parameters
    ----------
    sieve_mm : float, optional
        Sieve size, mm (one of 19.0, 12.5, 9.5, 4.75, 2.36, 0.60, 0.075). If
        omitted, returns the full gradation band table.

    Returns
    -------
    dict
        {'sieve_mm', 'percent_passing_min', 'percent_passing_max', 'reference'}
        if sieve_mm given, else {'bands': [...], 'reference'}.

    Raises
    ------
    ValueError
        If sieve_mm is not a tabulated size.
    """
    ref = "UFC 3-250-03, Table 7-2 (pdf_page 123, printed p.110)"
    if sieve_mm is None:
        return {
            "bands": [
                {"sieve_mm": s, "sieve_label": lbl, "percent_passing_min": lo,
                 "percent_passing_max": hi}
                for s, lbl, (lo, hi) in zip(_TABLE_7_2_SIEVES_MM, _TABLE_7_2_SIEVE_LABELS,
                                            _TABLE_7_2_BANDS)
            ],
            "reference": ref,
        }
    if sieve_mm not in _TABLE_7_2_SIEVES_MM:
        raise ValueError(f"sieve_mm must be one of {_TABLE_7_2_SIEVES_MM}, got {sieve_mm}")
    idx = _TABLE_7_2_SIEVES_MM.index(sieve_mm)
    lo, hi = _TABLE_7_2_BANDS[idx]
    return {
        "sieve_mm": sieve_mm, "sieve_label": _TABLE_7_2_SIEVE_LABELS[idx],
        "percent_passing_min": lo, "percent_passing_max": hi,
        "reference": ref,
    }


# ============================================================================
# Table 7-3: Aggregate Gradation for Slurry Grout (RMP)
# (Section 7-2.2.1; pdf_page 124, printed p.111)
# ============================================================================

_TABLE_7_3_SIEVES_MM = [1.18, 0.60, 0.075]
_TABLE_7_3_SIEVE_LABELS = ["No. 16", "No. 30", "No. 200"]
_TABLE_7_3_BANDS = [(100, 100), (95, 100), (0, 2)]


def table_7_3_slurry_grout_gradation(sieve_mm=None) -> dict:
    """Silica sand gradation for the cement slurry grout course of RMP (Table 7-3).

    Parameters
    ----------
    sieve_mm : float, optional
        Sieve size, mm (one of 1.18, 0.60, 0.075). If omitted, returns the
        full gradation band table.

    Returns
    -------
    dict
        {'sieve_mm', 'percent_passing_min', 'percent_passing_max', 'reference'}
        if sieve_mm given, else {'bands': [...], 'reference'}.

    Raises
    ------
    ValueError
        If sieve_mm is not a tabulated size.
    """
    ref = "UFC 3-250-03, Table 7-3 (pdf_page 124, printed p.111)"
    if sieve_mm is None:
        return {
            "bands": [
                {"sieve_mm": s, "sieve_label": lbl, "percent_passing_min": lo,
                 "percent_passing_max": hi}
                for s, lbl, (lo, hi) in zip(_TABLE_7_3_SIEVES_MM, _TABLE_7_3_SIEVE_LABELS,
                                            _TABLE_7_3_BANDS)
            ],
            "reference": ref,
        }
    if sieve_mm not in _TABLE_7_3_SIEVES_MM:
        raise ValueError(f"sieve_mm must be one of {_TABLE_7_3_SIEVES_MM}, got {sieve_mm}")
    idx = _TABLE_7_3_SIEVES_MM.index(sieve_mm)
    lo, hi = _TABLE_7_3_BANDS[idx]
    return {
        "sieve_mm": sieve_mm, "sieve_label": _TABLE_7_3_SIEVE_LABELS[idx],
        "percent_passing_min": lo, "percent_passing_max": hi,
        "reference": ref,
    }


# ============================================================================
# Table 7-4: Resin Modified Cement Slurry Grout Mixture Proportions (RMP)
# (Section 7-3.2; pdf_page 126, printed p.113)
# ============================================================================

_TABLE_7_4 = {
    "silica_sand": (16, 20),
    "fly_ash": (16, 20),
    "water": (22, 26),
    "type_i_cement": (34, 40),
    "cross_polymer_resin": (2.5, 3.5),
}


def table_7_4_grout_mix_proportions(material=None) -> dict:
    """Resin Modified Pavement (RMP) cement slurry grout mix proportions, percent by weight (Table 7-4).

    Parameters
    ----------
    material : str, optional
        If given, returns just that material's range: 'silica_sand',
        'fly_ash', 'water', 'type_i_cement', or 'cross_polymer_resin'. If
        omitted, returns all five ranges.

    Returns
    -------
    dict
        {'material', 'pct_by_weight_min', 'pct_by_weight_max', 'reference'}
        if material given, else {**all materials as (min, max) tuples,
        'reference'}.

    Raises
    ------
    ValueError
        If material is given but unrecognized.
    """
    ref = "UFC 3-250-03, Table 7-4 (pdf_page 126, printed p.113)"
    if material is None:
        return {**_TABLE_7_4, "reference": ref}
    key = str(material).strip().lower().replace(" ", "_")
    if key not in _TABLE_7_4:
        raise ValueError(
            f"Unknown material '{material}'. Use: {', '.join(_TABLE_7_4)}"
        )
    lo, hi = _TABLE_7_4[key]
    return {"material": key, "pct_by_weight_min": lo, "pct_by_weight_max": hi,
            "reference": ref}


# ============================================================================
# Table 7-5: Slurry Grout Viscosity (RMP)
# (Section 7-3.2; pdf_page 127, printed p.114)
# ============================================================================

_TABLE_7_5 = {
    "0_30_min": (8, 10),
    "after_30_min": (9, 11),
}


def table_7_5_grout_viscosity(time_elapsed) -> dict:
    """RMP cement slurry grout viscosity acceptance range, Marsh cone flow time (Table 7-5).

    Parameters
    ----------
    time_elapsed : str
        '0_30_min' (0 to 30 minutes after polymer addition) or
        'after_30_min'.

    Returns
    -------
    dict
        {'time_elapsed', 'marsh_cone_seconds_min', 'marsh_cone_seconds_max',
         'reference'}.

    Raises
    ------
    ValueError
        If time_elapsed is not recognized.
    """
    key = str(time_elapsed).strip().lower().replace(" ", "_").replace("-", "_")
    if key not in _TABLE_7_5:
        raise ValueError(
            f"Unknown time_elapsed '{time_elapsed}'. Use: {', '.join(_TABLE_7_5)}"
        )
    lo, hi = _TABLE_7_5[key]
    return {
        "time_elapsed": key, "marsh_cone_seconds_min": lo, "marsh_cone_seconds_max": hi,
        "reference": "UFC 3-250-03, Table 7-5 (pdf_page 127, printed p.114)",
    }


# ============================================================================
# Table B-1: Factors Used in Calculating Surface Area of Slurry Seal Aggregate
# (Appendix B-1.2.1; pdf_page 137, printed p.124)
# ============================================================================

_TABLE_B1_SIEVES_MM = [9.5, 4.75, 2.36, 1.18, 0.60, 0.30, 0.15, 0.075]
_TABLE_B1_SIEVE_LABELS = ["3/8 in", "No. 4", "No. 8", "No. 16", "No. 30", "No. 50", "No. 100", "No. 200"]
_TABLE_B1 = {
    9.5: (0.4, 2), 4.75: (0.4, 2), 2.36: (0.8, 4), 1.18: (1.6, 8),
    0.60: (2.9, 14), 0.30: (6.1, 30), 0.15: (12.2, 60), 0.075: (32.8, 160),
}


def table_b1_surface_area_factor(sieve_mm) -> dict:
    """Surface area factor for slurry-seal aggregate, by sieve size (Table B-1).

    Used in the Appendix B surface-area design method for slurry seals:
    total surface area SA = sum over sieves of (fraction passing) x (factor).
    See ``equations.slurry_seal_surface_area``.

    Parameters
    ----------
    sieve_mm : float
        Sieve size, mm (one of 9.5, 4.75, 2.36, 1.18, 0.60, 0.30, 0.15,
        0.075).

    Returns
    -------
    dict
        {'sieve_mm', 'sieve_label', 'factor_m2_per_kg', 'factor_ft2_per_lb',
         'reference'}.

    Raises
    ------
    ValueError
        If sieve_mm is not a tabulated size.
    """
    if sieve_mm not in _TABLE_B1:
        raise ValueError(
            f"sieve_mm must be one of {_TABLE_B1_SIEVES_MM}, got {sieve_mm}"
        )
    idx = _TABLE_B1_SIEVES_MM.index(sieve_mm)
    m2_kg, ft2_lb = _TABLE_B1[sieve_mm]
    return {
        "sieve_mm": sieve_mm, "sieve_label": _TABLE_B1_SIEVE_LABELS[idx],
        "factor_m2_per_kg": m2_kg, "factor_ft2_per_lb": ft2_lb,
        "reference": "UFC 3-250-03, Table B-1 (pdf_page 137, printed p.124)",
    }
