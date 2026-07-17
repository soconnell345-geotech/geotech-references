"""UFC 3-250-04 (Standard Practice for Concrete Pavements) - table lookups.

This is a DoD construction-practice manual for rigid (portland cement
concrete) pavements -- almost entirely procedural/QC narrative rather than
a design manual. Only the genuinely tabular, parametric/classification
lookup content is digitized here. Deliberately NOT digitized: the five
"Troubleshooting Guide" tables (Table 4-1, 5-1, 8-2, 9-2, Table D-1 is the
one exception -- see below) are qualitative, multi-value
problem/probable-cause/corrective-action narratives better served by full
text search (``geotech_references._retrieval.search_sections``) than a
rigid dict lookup; their full row content is captured in the corresponding
chapter JSON text instead.

No dowel bar diameter/length-vs-slab-thickness sizing table is printed
anywhere in this document -- that is DESIGN content covered by UFC 3-250-01
(roads/parking) or UFC 3-260-02 (airfields), out of scope for this
construction-practice UFC. What IS printed and digitized here is
everything this UFC actually specifies about dowel bars: installation
alignment tolerances, misalignment performance impact (Table 8-1), corner
clearance, and drilled-hole oversize for the construction-joint drill-and-
epoxy procedure.

PDF pages cited below are 0-based fitz page indices into
``docs/ufc_3_250_04_2024.pdf``; the printed UFC page is also given.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 3-1: Categorization of Weather Severity
# (Section 3-7.1; pdf_page 31, printed p.14)
# ============================================================================

_WEATHER_SEVERITY_ROWS = [
    # (max_air_freezing_index or None, precip_threshold_in or None, severity)
    (500, None, "moderate"),
    (None, 1.0, "moderate"),
    (None, None, "severe"),
]


def table_3_1_weather_severity(air_freezing_index, avg_monthly_precip_in) -> dict:
    """Categorize weather severity for aggregate deleterious-material limits (Table 3-1).

    Air freezing index <= 500 (coldest year in 30) is 'moderate' regardless
    of precipitation. Above 500, average precipitation for any single month
    during the freezing period governs: < 25 mm (1 in.) is 'moderate',
    >= 25 mm (1 in.) is 'severe'. Note 2 of the printed table: in
    poorly-drained areas, treat weather as severe even if these criteria
    indicate moderate.

    Parameters
    ----------
    air_freezing_index : float
        Air freezing index, coldest year in 30 (degree-days F, per
        UFC 3-260-02 calculation).
    avg_monthly_precip_in : float
        Average precipitation for any single month during the freezing
        period, inches.

    Returns
    -------
    dict
        {'air_freezing_index', 'avg_monthly_precip_in', 'severity',
         'note', 'reference'}.
    """
    if air_freezing_index <= 500:
        severity = "moderate"
    elif avg_monthly_precip_in < 1.0:
        severity = "moderate"
    else:
        severity = "severe"
    return {
        "air_freezing_index": air_freezing_index,
        "avg_monthly_precip_in": avg_monthly_precip_in,
        "severity": severity,
        "note": (
            "In poorly drained areas, treat weather as severe even if "
            "these criteria indicate moderate (Table 3-1, Note 2)."
        ),
        "reference": "UFC 3-250-04, Table 3-1 (pdf_page 31, printed p.14)",
    }


# ============================================================================
# Table 3-2: Deleterious Material Limits in Airfield Aggregates - Percent
# Mass (Section 3-7.1; pdf_page 32-33, printed p.15-16)
# ============================================================================

_TABLE_3_2 = {
    "clay_lumps_and_friable_particles": {"coarse_severe": 0.2, "coarse_moderate": 0.2, "fine": 1.0},
    "shale": {"coarse_severe": 0.1, "coarse_moderate": 0.2, "fine": None},
    "material_finer_than_no_200": {"coarse_severe": 0.5, "coarse_moderate": 0.5, "fine": 3.0},
    "lightweight_particles": {"coarse_severe": 0.2, "coarse_moderate": 0.2, "fine": 0.5},
    "clay_ironstone": {"coarse_severe": 0.1, "coarse_moderate": 0.5, "fine": None},
    "chert_and_cherty_stone": {"coarse_severe": 0.1, "coarse_moderate": 0.5, "fine": None},
    "claystone_mudstone_siltstone": {"coarse_severe": 0.1, "coarse_moderate": 0.1, "fine": None},
    "shaly_argillaceous_limestone": {"coarse_severe": 0.2, "coarse_moderate": 0.2, "fine": None},
    "other_soft_particles": {"coarse_severe": 1.0, "coarse_moderate": 1.0, "fine": None},
    "total_deleterious_excl_minus_200": {"coarse_severe": 1.0, "coarse_moderate": 2.0, "fine": None},
    "total_fine_incl_minus_200": {"coarse_severe": None, "coarse_moderate": None, "fine": 3.0},
}

_TABLE_3_2_ALIASES = {
    "clay_lumps": "clay_lumps_and_friable_particles",
    "friable_particles": "clay_lumps_and_friable_particles",
    "minus_200": "material_finer_than_no_200",
    "no_200": "material_finer_than_no_200",
    "chert": "chert_and_cherty_stone",
    "cherty_stone": "chert_and_cherty_stone",
    "claystone": "claystone_mudstone_siltstone",
    "mudstone": "claystone_mudstone_siltstone",
    "siltstone": "claystone_mudstone_siltstone",
    "shaly_limestone": "shaly_argillaceous_limestone",
    "argillaceous_limestone": "shaly_argillaceous_limestone",
}


def table_3_2_deleterious_material_limit(material, aggregate_category) -> dict:
    """Deleterious material limit, percent mass, airfield aggregates (Table 3-2).

    DoD airfield limits are an order of magnitude lower than ASTM
    C33/CRD-C 133 for roads.

    Parameters
    ----------
    material : str
        Deleterious material key: 'clay_lumps_and_friable_particles'
        (or 'clay_lumps'/'friable_particles'), 'shale',
        'material_finer_than_no_200' (or 'minus_200'/'no_200'),
        'lightweight_particles', 'clay_ironstone', 'chert_and_cherty_stone'
        (or 'chert'/'cherty_stone'), 'claystone_mudstone_siltstone' (or
        'claystone'/'mudstone'/'siltstone'), 'shaly_argillaceous_limestone'
        (or 'shaly_limestone'/'argillaceous_limestone'),
        'other_soft_particles', 'total_deleterious_excl_minus_200',
        'total_fine_incl_minus_200'.
    aggregate_category : str
        'coarse_severe' (coarse aggregate, severe weather),
        'coarse_moderate' (coarse aggregate, moderate weather), or 'fine'
        (fine aggregate, all weather).

    Returns
    -------
    dict
        {'material', 'aggregate_category', 'limit_pct_mass', 'reference'}.
        ``limit_pct_mass`` is None if the printed table cell is "-" (not
        applicable for that material/category combination).

    Raises
    ------
    ValueError
        If material or aggregate_category is unrecognized.
    """
    key = str(material).strip().lower().replace(" ", "_").replace("-", "_")
    key = _TABLE_3_2_ALIASES.get(key, key)
    if key not in _TABLE_3_2:
        raise ValueError(
            f"Unknown material '{material}'. Use: {', '.join(sorted(_TABLE_3_2))}"
        )
    cat = str(aggregate_category).strip().lower().replace(" ", "_")
    if cat not in ("coarse_severe", "coarse_moderate", "fine"):
        raise ValueError(
            "aggregate_category must be 'coarse_severe', 'coarse_moderate', "
            f"or 'fine', got '{aggregate_category}'"
        )
    limit = _TABLE_3_2[key][cat]
    return {
        "material": key,
        "aggregate_category": cat,
        "limit_pct_mass": limit,
        "reference": "UFC 3-250-04, Table 3-2 (pdf_page 32, printed p.15)",
    }


# ============================================================================
# Table 3-3: Testing Time Required (ASR / freeze-thaw)
# (Section 3-8.2; pdf_page 36, printed p.19)
# ============================================================================

_TABLE_3_3 = {
    "astm_c1260": {"time_for_result": "16 days"},
    "astm_c1293": {
        "time_for_result": "1 year for potential aggregate reactivity; "
        "2 years to test effectiveness of mitigation measures"
    },
    "astm_c666": {"time_for_result": "2 to 3 months"},
}

_TABLE_3_3_ALIASES = {
    "c1260": "astm_c1260",
    "crd_c_174": "astm_c1260",
    "c1293": "astm_c1293",
    "crd_c_175": "astm_c1293",
    "c666": "astm_c666",
    "crd_c_20": "astm_c666",
}


def table_3_3_aggregate_test_time(test_method) -> dict:
    """Lead time required for ASR/freeze-thaw aggregate testing (Table 3-3).

    Parameters
    ----------
    test_method : str
        'astm_c1260' (or 'c1260'/'crd_c_174'), 'astm_c1293' (or
        'c1293'/'crd_c_175'), or 'astm_c666' (or 'c666'/'crd_c_20').

    Returns
    -------
    dict
        {'test_method', 'time_for_result', 'reference'}.

    Raises
    ------
    ValueError
        If test_method is unrecognized.
    """
    key = str(test_method).strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
    key = _TABLE_3_3_ALIASES.get(key, key)
    if key not in _TABLE_3_3:
        raise ValueError(
            f"Unknown test_method '{test_method}'. Use: {', '.join(sorted(_TABLE_3_3))}"
        )
    return {
        "test_method": key,
        "time_for_result": _TABLE_3_3[key]["time_for_result"],
        "reference": "UFC 3-250-04, Table 3-3 (pdf_page 36, printed p.19)",
    }


# ============================================================================
# Table 3-4: Types and Uses of Portland Cements (ASTM C150/CRD-C 201)
# (Section 3-9.2; pdf_page 37, printed p.20)
# ============================================================================

_TABLE_3_4 = {
    "type_i": "Most widely available; used when other special properties are not required.",
    "type_ii": "For general use, especially when moderate sulfate resistance or heat of "
               "hydration is required. Some cements meeting requirements for both I and "
               "II are designated Type I/II.",
    "type_iii": "Used for high early strength.",
    "type_iv": "Used when low heat of hydration is required.",
    "type_v": "Used when high sulfate resistance is required.",
}


def table_3_4_portland_cement_type(cement_type) -> dict:
    """Portland cement type application (Table 3-4, ASTM C150/CRD-C 201).

    Parameters
    ----------
    cement_type : str
        'type_i', 'type_ii', 'type_iii', 'type_iv', or 'type_v' (also
        accepts bare numerals/roman numerals, e.g. '1', 'I').

    Returns
    -------
    dict
        {'cement_type', 'application', 'reference'}.

    Raises
    ------
    ValueError
        If cement_type is unrecognized.
    """
    key = _normalize_cement_type(cement_type)
    if key not in _TABLE_3_4:
        raise ValueError(
            f"Unknown cement_type '{cement_type}'. Use: {', '.join(sorted(_TABLE_3_4))}"
        )
    return {
        "cement_type": key,
        "application": _TABLE_3_4[key],
        "reference": "UFC 3-250-04, Table 3-4 (pdf_page 37, printed p.20)",
    }


_ROMAN_TO_ARABIC = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5"}
_ARABIC_TO_WORD = {"1": "i", "2": "ii", "3": "iii", "4": "iv", "5": "v"}


def _normalize_cement_type(cement_type) -> str:
    """Normalize 'Type I', 'I', '1', 'type_1' etc. to 'type_i' form."""
    raw = str(cement_type).strip().lower().replace(" ", "_").replace("-", "_")
    raw = raw.replace("type_", "").replace("type", "")
    if raw in _ROMAN_TO_ARABIC:
        raw = _ROMAN_TO_ARABIC[raw]
    if raw in _ARABIC_TO_WORD:
        raw = _ARABIC_TO_WORD[raw]
    return f"type_{raw}"


# ============================================================================
# Table 3-5: Types of Blended Cements (ASTM C595/CRD-C 203)
# (Section 3-9.3; pdf_page 37, printed p.20)
# ============================================================================

_TABLE_3_5 = {
    "type_il": "Contains 10 to 15 percent ground limestone.",
    "type_is": "Contains 25 to 70 percent blast furnace slag.",
    "type_p": "Contains 15 to 40 percent pozzolan (fly ash or natural pozzolan); used "
              "when higher early strengths are not needed.",
    "type_ip": "Contains 15 to 40 percent pozzolan (fly ash or natural pozzolan); used "
               "when higher early strengths are not needed.",
    "type_i_pm": "Contains less than 15 percent pozzolan. Should not be used when the "
                 "special properties of pozzolan are desired, as it doesn't contain "
                 "enough of this material.",
    "type_i_sm": "Contains less than 25 percent slag. Should not be used when the "
                 "special properties of slag are desired, as it doesn't contain "
                 "enough of this material.",
    "type_s": "Contains at least 70 percent slag.",
}

_TABLE_3_5_ALIASES = {
    "il": "type_il", "il_10": "type_il", "il_15": "type_il",
    "is": "type_is",
    "p": "type_p",
    "ip": "type_ip",
    "i_pm": "type_i_pm", "ipm": "type_i_pm",
    "i_sm": "type_i_sm", "ism": "type_i_sm",
    "s": "type_s",
}


def table_3_5_blended_cement_type(cement_type) -> dict:
    """Blended cement type composition (Table 3-5, ASTM C595/CRD-C 203).

    Parameters
    ----------
    cement_type : str
        'type_il' (or 'il'), 'type_is' (or 'is'), 'type_p' (or 'p'),
        'type_ip' (or 'ip'), 'type_i_pm' (or 'ipm'), 'type_i_sm' (or
        'ism'), 'type_s' (or 's').

    Returns
    -------
    dict
        {'cement_type', 'composition', 'reference'}.

    Raises
    ------
    ValueError
        If cement_type is unrecognized.
    """
    key = str(cement_type).strip().lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
    key = _TABLE_3_5_ALIASES.get(key, key)
    if key not in _TABLE_3_5:
        raise ValueError(
            f"Unknown cement_type '{cement_type}'. Use: {', '.join(sorted(_TABLE_3_5))}"
        )
    return {
        "cement_type": key,
        "composition": _TABLE_3_5[key],
        "reference": "UFC 3-250-04, Table 3-5 (pdf_page 37, printed p.20)",
    }


# ============================================================================
# Table 3-6: Types of Hydraulic Cements (ASTM C1157/CRD-C 271)
# (Section 3-9.4; pdf_page 38, printed p.21)
# ============================================================================

_TABLE_3_6 = {
    "type_gu": "For general use.",
    "type_he": "For high early strength.",
    "type_ms": "For moderate sulfate resistance.",
    "type_hs": "For high sulfate resistance.",
    "type_mh": "For moderate heat of hydration.",
    "type_lh": "For low heat of hydration.",
}

_TABLE_3_6_ALIASES = {
    "gu": "type_gu", "he": "type_he", "ms": "type_ms",
    "hs": "type_hs", "mh": "type_mh", "lh": "type_lh",
}


def table_3_6_hydraulic_cement_type(cement_type) -> dict:
    """Performance-based hydraulic cement type use (Table 3-6, ASTM C1157/CRD-C 271).

    Parameters
    ----------
    cement_type : str
        'type_gu', 'type_he', 'type_ms', 'type_hs', 'type_mh', or
        'type_lh' (also accepts the bare 2-letter code, e.g. 'gu').

    Returns
    -------
    dict
        {'cement_type', 'use', 'reference'}.

    Raises
    ------
    ValueError
        If cement_type is unrecognized.
    """
    key = str(cement_type).strip().lower().replace(" ", "_").replace("-", "_")
    key = _TABLE_3_6_ALIASES.get(key, key)
    if key not in _TABLE_3_6:
        raise ValueError(
            f"Unknown cement_type '{cement_type}'. Use: {', '.join(sorted(_TABLE_3_6))}"
        )
    return {
        "cement_type": key,
        "use": _TABLE_3_6[key],
        "reference": "UFC 3-250-04, Table 3-6 (pdf_page 38, printed p.21)",
    }


# ============================================================================
# Table 3-7: Grades of GGBF Slag (ASTM C989/CRD-C 205)
# (Section 3-9.5.6; pdf_page 39, printed p.22)
# ============================================================================

_TABLE_3_7 = {
    "grade_80": "Least reactive, not normally used for airfield pavements.",
    "grade_100": "Moderately reactive.",
    "grade_120": "Most reactive, through finer grinding. Difficult to obtain in some "
                 "locations in U.S. and Canada.",
}

_TABLE_3_7_ALIASES = {"80": "grade_80", "100": "grade_100", "120": "grade_120"}


def table_3_7_ggbf_slag_grade(grade) -> dict:
    """GGBF slag grade properties (Table 3-7, ASTM C989/CRD-C 205).

    Parameters
    ----------
    grade : str or int
        'grade_80' (or 80), 'grade_100' (or 100), 'grade_120' (or 120).

    Returns
    -------
    dict
        {'grade', 'properties', 'reference'}.

    Raises
    ------
    ValueError
        If grade is unrecognized.
    """
    key = str(grade).strip().lower().replace(" ", "_").replace("-", "_")
    key = _TABLE_3_7_ALIASES.get(key, key)
    if key not in _TABLE_3_7:
        raise ValueError(
            f"Unknown grade '{grade}'. Use: {', '.join(sorted(_TABLE_3_7))}"
        )
    return {
        "grade": key,
        "properties": _TABLE_3_7[key],
        "reference": "UFC 3-250-04, Table 3-7 (pdf_page 39, printed p.22)",
    }


# ============================================================================
# Table 3-8: Types of Admixtures (ASTM C494/CRD-C 87)
# (Section 3-10.1.1; pdf_page 40, printed p.23)
# ============================================================================

_TABLE_3_8 = {
    "type_a": "Water-reducing admixtures.",
    "type_b": "Retarding admixtures.",
    "type_c": "Accelerating admixtures.",
    "type_d": "Water-reducing and retarding admixtures.",
    "type_e": "Water-reducing and accelerating admixtures.",
    "type_f": "Water-reducing and high range admixtures.",
    "type_g": "Water-reducing, high range, and retarding admixtures.",
}

_TABLE_3_8_ALIASES = {"a": "type_a", "b": "type_b", "c": "type_c", "d": "type_d",
                       "e": "type_e", "f": "type_f", "g": "type_g"}


def table_3_8_admixture_type(admixture_type) -> dict:
    """Chemical admixture type use (Table 3-8, ASTM C494/CRD-C 87).

    Parameters
    ----------
    admixture_type : str
        'type_a' through 'type_g' (also accepts the bare letter, e.g. 'a').

    Returns
    -------
    dict
        {'admixture_type', 'use', 'reference'}.

    Raises
    ------
    ValueError
        If admixture_type is unrecognized.
    """
    key = str(admixture_type).strip().lower().replace(" ", "_").replace("-", "_")
    key = _TABLE_3_8_ALIASES.get(key, key)
    if key not in _TABLE_3_8:
        raise ValueError(
            f"Unknown admixture_type '{admixture_type}'. Use: {', '.join(sorted(_TABLE_3_8))}"
        )
    return {
        "admixture_type": key,
        "use": _TABLE_3_8[key],
        "reference": "UFC 3-250-04, Table 3-8 (pdf_page 40, printed p.23)",
    }


# ============================================================================
# Table 8-1: Types of Dowel Bar Misalignment and Impact on Performance
# (Section 8-5.2.1; pdf_page 94, printed p.77)
# ============================================================================

_TABLE_8_1 = {
    "horizontal_translation": {"spalling": False, "cracking": False, "load_transfer": True},
    "longitudinal_translation": {"spalling": False, "cracking": False, "load_transfer": True},
    "vertical_translation": {"spalling": True, "cracking": False, "load_transfer": True},
    "horizontal_skew": {"spalling": True, "cracking": True, "load_transfer": True},
    "vertical_skew": {"spalling": True, "cracking": True, "load_transfer": True},
}


def table_8_1_dowel_misalignment_impact(misalignment_type) -> dict:
    """Dowel bar misalignment type and its impact on performance (Table 8-1).

    Parameters
    ----------
    misalignment_type : str
        'horizontal_translation', 'longitudinal_translation',
        'vertical_translation', 'horizontal_skew', or 'vertical_skew'.

    Returns
    -------
    dict
        {'misalignment_type', 'affects_spalling', 'affects_cracking',
         'affects_load_transfer', 'reference'}. Each ``affects_*`` is a
         bool: True if the printed table marks that performance effect
         ("Yes"), False if marked "---" (no effect noted).

    Raises
    ------
    ValueError
        If misalignment_type is unrecognized.
    """
    key = str(misalignment_type).strip().lower().replace(" ", "_").replace("-", "_")
    if key not in _TABLE_8_1:
        raise ValueError(
            f"Unknown misalignment_type '{misalignment_type}'. Use: "
            f"{', '.join(sorted(_TABLE_8_1))}"
        )
    row = _TABLE_8_1[key]
    return {
        "misalignment_type": key,
        "affects_spalling": row["spalling"],
        "affects_cracking": row["cracking"],
        "affects_load_transfer": row["load_transfer"],
        "reference": "UFC 3-250-04, Table 8-1 (pdf_page 94, printed p.77)",
    }


# ============================================================================
# Dowel bar installation tolerances (inline lookups, no formal table number)
# Section 8-5.2.1.1 (alignment), 8-5.2.1.4 (corner clearance), 8-5.2.3
# (drilled hole oversize); pdf_page 92-93, printed p.75-76
# ============================================================================


def dowel_bar_alignment_tolerance() -> dict:
    """Typical dowel bar alignment specification tolerances (Section 8-5.2.1.1).

    Returns
    -------
    dict
        {'skew_mm_per_m', 'skew_in_per_ft', 'horizontal_longitudinal_translation_mm',
         'horizontal_longitudinal_translation_in', 'vertical_translation_mm',
         'vertical_translation_in', 'reference'}. All values are the
         MAXIMUM (or-less) tolerance.
    """
    return {
        "skew_mm_per_m": 10, "skew_in_per_ft": 0.125,
        "horizontal_longitudinal_translation_mm": 15,
        "horizontal_longitudinal_translation_in": 0.625,
        "vertical_translation_mm": 13, "vertical_translation_in": 0.5,
        "reference": (
            "UFC 3-250-04, Section 8-5.2.1.1 (pdf_page 93, printed p.76)"
        ),
    }


def dowel_bar_corner_clearance() -> dict:
    """Minimum/preferred dowel bar clearance at slab corners (Section 8-5.2.1.4).

    To reduce restraint at slab corners, longitudinal-joint dowel bars are
    offset from the ends of transverse-joint dowel bars.

    Returns
    -------
    dict
        {'minimum_mm', 'minimum_in', 'preferred_mm', 'preferred_in', 'reference'}.
    """
    return {
        "minimum_mm": 150, "minimum_in": 6.0,
        "preferred_mm": 300, "preferred_in": 12.0,
        "reference": (
            "UFC 3-250-04, Section 8-5.2.1.4 (pdf_page 93, printed p.76)"
        ),
    }


def dowel_bar_drilled_hole_oversize() -> dict:
    """Drilled hole oversize for drill-and-epoxy dowel installation (Section 8-5.2.3).

    Holes drilled at construction joints/transverse headers for the
    drill-and-epoxy-grout dowel technique are slightly over-sized relative
    to the dowel bar diameter.

    Returns
    -------
    dict
        {'oversize_min_mm', 'oversize_max_mm', 'oversize_min_in',
         'oversize_max_in', 'reference'}.
    """
    return {
        "oversize_min_mm": 3, "oversize_max_mm": 6,
        "oversize_min_in": 0.125, "oversize_max_in": 0.25,
        "reference": (
            "UFC 3-250-04, Section 8-5.2.3 (pdf_page 95, printed p.78)"
        ),
    }


# ============================================================================
# Table 9-1: Maximum Joint Spacing
# (Section 9-3.2.1; pdf_page 121, printed p.104)
# ============================================================================

_TABLE_9_1 = [
    # (thickness_upper_bound_in or None, spacing_ft_min, spacing_ft_max,
    #  spacing_ft_min_roads)
    (9, 12.5, 15, 10),
    (12, 15, 20, 15),
    (None, 20, 20, 20),
]


def table_9_1_maximum_joint_spacing(slab_thickness_in, facility_type="airfield") -> dict:
    """Maximum joint spacing by slab thickness (Table 9-1).

    Parameters
    ----------
    slab_thickness_in : float
        Concrete slab thickness, inches.
    facility_type : str, optional
        'airfield' (default) or 'road' (roads and parking lots use a
        narrower minimum spacing, 10-15 ft, in the < 9 in. thickness
        category only; the two categories are otherwise identical).

    Returns
    -------
    dict
        {'slab_thickness_in', 'facility_type', 'joint_spacing_min_ft',
         'joint_spacing_max_ft', 'joint_spacing_min_m',
         'joint_spacing_max_m', 'reference'}.

    Raises
    ------
    ValueError
        If slab_thickness_in <= 0 or facility_type is unrecognized.
    """
    if slab_thickness_in <= 0:
        raise ValueError(f"slab_thickness_in must be > 0, got {slab_thickness_in}")
    ft = str(facility_type).strip().lower()
    if ft not in ("airfield", "road"):
        raise ValueError(f"facility_type must be 'airfield' or 'road', got '{facility_type}'")
    for upper, lo, hi, lo_road in _TABLE_9_1:
        if upper is None or slab_thickness_in < upper:
            spacing_min = lo_road if (ft == "road" and upper == 9) else lo
            return {
                "slab_thickness_in": slab_thickness_in, "facility_type": ft,
                "joint_spacing_min_ft": spacing_min, "joint_spacing_max_ft": hi,
                "joint_spacing_min_m": round(spacing_min * 0.3048, 2),
                "joint_spacing_max_m": round(hi * 0.3048, 2),
                "reference": "UFC 3-250-04, Table 9-1 (pdf_page 121, printed p.104)",
            }
    raise AssertionError("unreachable")  # pragma: no cover


# ============================================================================
# Edge slump tolerance (inline lookup, no formal table number)
# Section 8-11 / 10-5.1; pdf_page 100-101 / 141, printed p.83-84 / 124
# ============================================================================


def edge_slump_tolerance() -> dict:
    """Typical edge slump acceptance tolerance (Sections 8-11 and 10-5.1).

    Returns
    -------
    dict
        {'max_pct_of_joint_length_at_local_limit', 'local_limit_mm',
         'local_limit_in', 'absolute_max_mm', 'absolute_max_in',
         'reference'}.
    """
    return {
        "max_pct_of_joint_length_at_local_limit": 15,
        "local_limit_mm": 6, "local_limit_in": 0.25,
        "absolute_max_mm": 10, "absolute_max_in": 0.375,
        "reference": (
            "UFC 3-250-04, Sections 8-11 and 10-5.1 "
            "(pdf_page 100 and 141, printed p.83 and 124)"
        ),
    }


# ============================================================================
# Table D-1: Early Age Cracking Types/Possible Causes/Investigation
# (Appendix D, Section D-1; pdf_page 164-165, printed p.147-148)
# ============================================================================

_TABLE_D_1 = {
    "plastic_shrinkage": [
        "High evaporation rate (warm/low humidity/windy)", "Dry concrete mix",
        "Dry aggregates", "Late/inadequate curing", "Delay in finishing",
        "Sudden cold front/rain",
        "Material incompatibility (high shrinkage + delayed set)",
        "Poor aggregate gradation",
    ],
    "random_no_orientation": [
        "Slab-to-base bonding",
        "Concrete friction/penetration into open-graded base",
        "Reflection cracking from base", "Late/inadequate curing",
        "Late sawing", "Shallow sawing vs. slab thickness",
        "Poor aggregate gradation",
    ],
    "longitudinal": [
        "Late/shallow sawing vs. thickness",
        "Slab too wide for thickness/length", "Cold front/rain",
        "Misaligned/bonded dowels (adjacent longitudinal joints)",
        "Excessive curling/warping", "Poor gradation", "Retarded concrete",
        "Early loading", "Infill lane restraints", "Inadequate curing",
        "High-shrinkage concrete", "Slab-to-base bonding",
    ],
    "transverse": [
        "Late/shallow sawing vs. thickness",
        "Slab too long for thickness/width", "Cold front/rain",
        "Misaligned/bonded dowels (transverse joints)",
        "Excessive curling/warping", "Poor gradation",
        "High-shrinkage concrete", "Early loading",
    ],
    "corner": [
        "Early loading",
        "Excessive curling/warping (temperature/moisture)",
        "Dowel bars too close together at joint intersections",
        "Late/inadequate curing",
        "Misaligned/bonded transverse dowels",
    ],
    "pop_off_ahead_of_sawing": [
        "Late sawing for prevailing conditions", "Sawing against high wind",
    ],
    "late_cracking": [
        "Early-age slab-bottom cracking finally becoming visible",
        "Frost heave", "Foundation settlement",
    ],
    "sympathy_cracks": [
        "Joints in paved lane not matching adjacent lane joints",
        "Different joint cracking patterns in adjacent lanes",
        "Joints matching in location but not type",
    ],
    "settlement_over_dowel_tie_bars": [
        "Higher slump concrete", "Shallow dowel/tie bar cover",
        "Delay in setting time",
    ],
    "re_entrant": [
        "Use of odd-shaped slab panels",
        "Rigid penetrations (in-place structures)",
    ],
}

_TABLE_D_1_ALIASES = {
    "plastic": "plastic_shrinkage",
    "random": "random_no_orientation",
    "random_cracking": "random_no_orientation",
    "longitudinal_cracking": "longitudinal",
    "transverse_cracking": "transverse",
    "corner_cracking": "corner",
    "pop_off": "pop_off_ahead_of_sawing",
    "popoff": "pop_off_ahead_of_sawing",
    "sympathy": "sympathy_cracks",
    "settlement_cracks": "settlement_over_dowel_tie_bars",
    "settlement_over_dowel_bars": "settlement_over_dowel_tie_bars",
    "re_entrant_cracks": "re_entrant",
    "reentrant": "re_entrant",
}


def table_d1_cracking_causes(crack_type) -> dict:
    """Early-age cracking type and possible causes (Table D-1, Appendix D).

    Note: the printed table's caption reads ".../Investigation" but the
    printed columns are only Cracking Type x Possible Causes (stacked rows
    per column); there is no separate populated "Investigation" column.
    Investigation methodology is covered narratively in Appendix D-1's
    3-step process and the D-2 data-gathering checklist (see
    ``geotech_references._retrieval.retrieve_section("ufc_concrete_practice",
    "15-1")`` and section "15-2" onward).

    Parameters
    ----------
    crack_type : str
        'plastic_shrinkage' (or 'plastic'), 'random_no_orientation' (or
        'random'/'random_cracking'), 'longitudinal' (or
        'longitudinal_cracking'), 'transverse' (or 'transverse_cracking'),
        'corner' (or 'corner_cracking'), 'pop_off_ahead_of_sawing' (or
        'pop_off'/'popoff'), 'late_cracking', 'sympathy_cracks' (or
        'sympathy'), 'settlement_over_dowel_tie_bars' (or
        'settlement_cracks'), 're_entrant' (or 're_entrant_cracks'/
        'reentrant').

    Returns
    -------
    dict
        {'crack_type', 'possible_causes', 'reference'}.
        ``possible_causes`` is a list of strings.

    Raises
    ------
    ValueError
        If crack_type is unrecognized.
    """
    key = str(crack_type).strip().lower().replace(" ", "_").replace("-", "_")
    key = _TABLE_D_1_ALIASES.get(key, key)
    if key not in _TABLE_D_1:
        raise ValueError(
            f"Unknown crack_type '{crack_type}'. Use: {', '.join(sorted(_TABLE_D_1))}"
        )
    return {
        "crack_type": key,
        "possible_causes": list(_TABLE_D_1[key]),
        "reference": "UFC 3-250-04, Table D-1 (pdf_page 164, printed p.147)",
    }


# ============================================================================
# Table E-1: Recommended Combined RCC Gradation
# (Appendix E, Section E-5.1; pdf_page 168, printed p.151)
# ============================================================================

_RCC_GRADATION_SIEVES_MM = [25, 19, 12.5, 9.5, 4.75, 2.36, 1.18, 0.60, 0.30, 0.15, 0.075]
_RCC_GRADATION_LABELS = {
    25: "1 in.", 19: "3/4 in.", 12.5: "1/2 in.", 9.5: "3/8 in.",
    4.75: "No. 4", 2.36: "No. 8", 1.18: "No. 16", 0.60: "No. 30",
    0.30: "No. 50", 0.15: "No. 100", 0.075: "No. 200",
}
_RCC_GRADATION_MIN = [100, 85, 70, 55, 40, 30, 20, 15, 10, 5, 2]
_RCC_GRADATION_MAX = [100, 100, 95, 85, 65, 55, 45, 35, 25, 15, 10]


def table_e1_rcc_gradation(sieve_mm=None) -> dict:
    """Recommended combined roller-compacted concrete (RCC) gradation (Table E-1).

    Parameters
    ----------
    sieve_mm : float, optional
        Sieve size, mm, one of 25, 19, 12.5, 9.5, 4.75, 2.36, 1.18, 0.60,
        0.30, 0.15, 0.075 (i.e. 1 in. down to No. 200). If omitted, returns
        the full gradation band table.

    Returns
    -------
    dict
        If sieve_mm given: {'sieve_mm', 'sieve_label', 'pct_passing_min',
        'pct_passing_max', 'reference'}.
        If omitted: {'rows': [...], 'reference'}, each row having the same
        keys as above (minus 'reference').

    Raises
    ------
    ValueError
        If sieve_mm is given but does not match a tabulated sieve size.
    """
    ref = "UFC 3-250-04, Table E-1 (pdf_page 168, printed p.151)"
    if sieve_mm is None:
        rows = [
            {
                "sieve_mm": s, "sieve_label": _RCC_GRADATION_LABELS[s],
                "pct_passing_min": lo, "pct_passing_max": hi,
            }
            for s, lo, hi in zip(
                _RCC_GRADATION_SIEVES_MM, _RCC_GRADATION_MIN, _RCC_GRADATION_MAX
            )
        ]
        return {"rows": rows, "reference": ref}
    for s, lo, hi in zip(_RCC_GRADATION_SIEVES_MM, _RCC_GRADATION_MIN, _RCC_GRADATION_MAX):
        if abs(s - sieve_mm) < 1e-6:
            return {
                "sieve_mm": s, "sieve_label": _RCC_GRADATION_LABELS[s],
                "pct_passing_min": lo, "pct_passing_max": hi,
                "reference": ref,
            }
    raise ValueError(
        f"sieve_mm must be one of {_RCC_GRADATION_SIEVES_MM}, got {sieve_mm}"
    )
