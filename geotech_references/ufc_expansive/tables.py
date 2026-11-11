"""UFC 3-220-07 expansive soil lookup tables.

From UFC 3-220-07, Foundations in Expansive Soils (the reproduced
TM 5-818-7), docs/ufc_3_220_07.pdf. Every value is read off the printed
page named in its result: Table 4-1 (p. 4-1), Figure 4-1 (p. 4-2),
paragraph 5-4c (p. 5-4), Table 6-1 (p. 6-2) and paragraph 6-4, Grade
beams (p. 6-16). The print's
units (inches, feet, tsf) are kept, with SI conversions labelled as
conversions. PDF page (1-based) = 30 + n for printed p. 4-n, 35 + n for
p. 5-n, 42 + n for p. 6-n.

Rebuilt from the print 2026-11-10 (review pave-07, pave-13): the earlier
five-class swell table, climate active-zone depths, swell-class foundation
table and millimetre grade-beam voids were not printed in this manual.
"""

_REF = "UFC 3-220-07 (TM 5-818-7)"
_FT_TO_M = 0.3048
_IN_TO_MM = 25.4

# ---------------------------------------------------------------------------
# Table 4-1 WES Classification of Potential Swell (PDF 31, printed p. 4-1)
# ---------------------------------------------------------------------------

# classification -> printed ranges (potential swell Sp %, LL %, PI %,
# natural soil suction tsf)
_TABLE_4_1 = {
    "low": {"potential_swell_pct": "<0.5", "liquid_limit_pct": "<50",
            "plasticity_index_pct": "<25", "natural_soil_suction_tsf": "<1.5"},
    "marginal": {"potential_swell_pct": "0.5-1.5", "liquid_limit_pct": "50-60",
                 "plasticity_index_pct": "25-35",
                 "natural_soil_suction_tsf": "1.5-4.0"},
    "high": {"potential_swell_pct": ">1.5", "liquid_limit_pct": ">60",
             "plasticity_index_pct": ">35", "natural_soil_suction_tsf": ">4.0"},
}
_RANK = {"low": 0, "marginal": 1, "high": 2}
_TABLE_4_1_NOTE = (
    "Para 4-1a (p. 4-1): The Sp represents the percent increase in the "
    "vertical dimension or the percent potential vertical heave. The "
    "classification may be used without knowing the natural soil suction, "
    "but the accuracy and conservatism of the system are reduced. Soils that "
    "rate low may not require further swell tests, particularly if the LL is "
    "less than 40 percent and the PI is less than 15 percent. Soils with "
    "these Atterberg limits or less are essentially nonexpansive. However, "
    "swell tests may be required for soils of low swelling potential if the "
    "foundation of the structure is required to maintain small differential "
    "movements less than 1 inch (para 4-2c).")


def _band(value, low_below, high_above):
    """'low' below low_below, 'high' above high_above, else 'marginal'."""
    if value < low_below:
        return "low"
    if value > high_above:
        return "high"
    return "marginal"


# ---------------------------------------------------------------------------
# Table 6-1 Foundation Systems (PDF 44, printed p. 6-2)
# ---------------------------------------------------------------------------

_SHALLOW = {
    "foundation_system": "Shallow individual; continuous wall; strip",
    "remarks": "Lightly loaded buildings and residences.",
}
_THIN_MAT_REMARKS = (
    "Residences and lightly loaded structures; on-grade 4- to 5-in. "
    "reinforced concrete slab with stiffening beams; maximum free area "
    "between beams 400 ft2; 1/2 percent reinforcing steel; 10- to "
    "12-in.-thick beams; external beams thickened or deepened, and extra "
    "steel stirrups added to tolerate high edge forces as needed; dimensions "
    "adjusted to resist loading. Beams positioned beneath corners to reduce "
    "slab distortion.")
_THIN_MATS = {
    # type of mat -> (predicted differential movement in., effective PI,
    #                 beam depth in., beam spacing ft), as printed
    "light": ("1/2 to 1", "15 to 25", "16 to 20", "20 to 15"),
    "medium": ("1 to 2", "26 to 40", "20 to 25", "15 to 12"),
    "heavy": ("2 to 4", ">41", "25 to 30", "15 to 12"),
}
_NO_LIMIT = [
    {"foundation_system": "Thick, reinforced mat",
     "predicted_differential_movement_in": "No limit",
     "remarks": ("Large, heavy structures; mats usually 2 ft or more in "
                 "thickness.")},
    {"foundation_system": "Deep foundations, pile or drilled shaft",
     "predicted_differential_movement_in": "No limit",
     "remarks": ("Foundations for any light or heavy structure; grade beams "
                 "span between piles or shafts 6 to 12 in. above ground "
                 "level; suspended floors or on-grade slabs isolated from "
                 "grade beams and walls. Concrete drilled shafts may be "
                 "underreamed or straight, reinforced, and cast in place "
                 "with 3000-psi concrete of 6-in. slump.")},
]


def _thin_mat(mat):
    move, pi, depth, spacing = _THIN_MATS[mat]
    return {
        "foundation_system": "Reinforced and stiffened thin mat",
        "type_of_mat": mat,
        "predicted_differential_movement_in": move,
        "effective_plasticity_index": pi,
        "beam_depth_in": depth,
        "beam_spacing_ft": spacing,
        "remarks": _THIN_MAT_REMARKS,
    }


# ---------------------------------------------------------------------------
# Public lookup functions
# ---------------------------------------------------------------------------

def table_swell_potential_classification(
    plasticity_index=None,
    liquid_limit=None,
    natural_soil_suction_tsf=None,
):
    """WES classification of potential swell, UFC 3-220-07 Table 4-1
    (printed p. 4-1, PDF 31); returns 'low', 'marginal' or 'high' with the
    printed potential swell Sp (percent potential vertical heave).

    Table 4-1 as printed: Low, Sp < 0.5 %, LL < 50, PI < 25, natural soil
    suction < 1.5 tsf; Marginal, Sp 0.5-1.5 %, LL 50-60, PI 25-35, suction
    1.5-4.0 tsf; High, Sp > 1.5 %, LL > 60, PI > 35, suction > 4.0 tsf.
    When the given properties fall in different rows the more severe row is
    returned (the code's choice; the table does not say), with each
    property's own row.

    Parameters
    ----------
    plasticity_index : float, optional
        Plasticity index (%).
    liquid_limit : float, optional
        Liquid limit (%).
    natural_soil_suction_tsf : float, optional
        Natural soil suction, tons per square foot.

    Returns
    -------
    dict
        Keys: classification, potential_swell_pct (the printed range),
        by_property (each given property's row), printed_row, note,
        reference, and the inputs given.

    Raises
    ------
    ValueError
        If no property is given or a value is negative.
    """
    given = {"plasticity_index": plasticity_index,
             "liquid_limit": liquid_limit,
             "natural_soil_suction_tsf": natural_soil_suction_tsf}
    given = {k: v for k, v in given.items() if v is not None}
    if not given:
        raise ValueError(
            "At least one of plasticity_index, liquid_limit or "
            "natural_soil_suction_tsf must be given")
    for k, v in given.items():
        if v < 0:
            raise ValueError(f"{k} must be >= 0, got {v}")
    bounds = {"plasticity_index": (25, 35), "liquid_limit": (50, 60),
              "natural_soil_suction_tsf": (1.5, 4.0)}
    by_prop = {k: _band(v, *bounds[k]) for k, v in given.items()}
    worst = max(by_prop.values(), key=lambda c: _RANK[c])
    result = {
        "classification": worst,
        "potential_swell_pct": _TABLE_4_1[worst]["potential_swell_pct"],
        "by_property": by_prop,
        "printed_row": dict(_TABLE_4_1[worst]),
        "note": _TABLE_4_1_NOTE,
        "reference": f"{_REF}, Table 4-1, printed p. 4-1 (PDF 31)",
    }
    result.update(given)
    return result


def table_active_zone_depth(profile=None, natural_soil_suction_tsf=None,
                            depth_to_groundwater_ft=None,
                            shaft_base_diameter_ft=None):
    """Depth of the active zone Xa, feet below the base of the foundation,
    UFC 3-220-07 paragraph 5-4c (printed p. 5-4, PDF 39); returns the
    printed estimate with a conversion to metres.

    As printed: (1) for groundwater levels less than 20 feet in clay soil,
    Xa may be assumed equal to the depth of the water table; (2)(a) if
    depths to groundwater exceed 20 feet and no other information is
    available, Xa can be assumed to be between 10 feet (moist profiles or
    soil suctions less than 4 tsf) and 20 feet (dry profiles or soil
    suctions greater than 4 tsf) below the base of the foundation; "the
    depth Xa should not be estimated less than three times the base
    diameter of a shaft foundation". (2)(b)-(c): Xa can also be estimated
    from the suction or water content/plastic limit profile (appendix B).

    Parameters
    ----------
    profile : str, optional
        'moist' (10 ft) or 'dry' (20 ft), for groundwater deeper than
        20 ft.
    natural_soil_suction_tsf : float, optional
        Used in place of *profile*: < 4 tsf -> 10 ft, > 4 tsf -> 20 ft
        (exactly 4 is refused: the print gives none).
    depth_to_groundwater_ft : float, optional
        Below 20 ft, Xa = this depth (paragraph 5-4c(1)).
    shaft_base_diameter_ft : float, optional
        If given, the deep-groundwater Xa is not less than 3 times it
        (printed under 5-4c(2)(a)).

    Returns
    -------
    dict
        Keys: active_zone_depth_ft, active_zone_depth_m (conversion),
        basis, reference.

    Raises
    ------
    ValueError
        If neither a shallow groundwater depth, a profile nor a suction is
        given, or a value is out of range.
    """
    if depth_to_groundwater_ft is not None and depth_to_groundwater_ft < 0:
        raise ValueError(
            f"depth_to_groundwater_ft must be >= 0, got {depth_to_groundwater_ft}")
    if depth_to_groundwater_ft is not None and depth_to_groundwater_ft < 20:
        xa = float(depth_to_groundwater_ft)
        basis = ("5-4c(1) shallow groundwater: Xa may be assumed equal to the "
                 "depth of the water table for groundwater levels less than "
                 "20 feet in clay soil.")
    else:
        if profile is None and natural_soil_suction_tsf is not None:
            if natural_soil_suction_tsf < 0:
                raise ValueError("natural_soil_suction_tsf must be >= 0")
            if natural_soil_suction_tsf < 4:
                profile = "moist"
            elif natural_soil_suction_tsf > 4:
                profile = "dry"
            else:
                raise ValueError(
                    "Paragraph 5-4c(2)(a) gives 10 ft for suctions less "
                    "than 4 tsf and 20 ft for greater than 4 tsf; exactly 4 "
                    "is not stated")
        p = None if profile is None else str(profile).strip().lower()
        if p not in ("moist", "dry"):
            raise ValueError(
                "Give depth_to_groundwater_ft (< 20 ft), or profile "
                "'moist'/'dry' or natural_soil_suction_tsf for groundwater "
                "deeper than 20 ft (paragraph 5-4c, p. 5-4)")
        xa = 10.0 if p == "moist" else 20.0
        basis = ("5-4c(2)(a) deep groundwater, no other information: Xa "
                 "between 10 feet (moist profiles or soil suctions less than "
                 "4 tsf) and 20 feet (dry profiles or soil suctions greater "
                 f"than 4 tsf) below the base of the foundation; {p} -> "
                 f"{xa:g} ft.")
    if shaft_base_diameter_ft is not None:
        if shaft_base_diameter_ft <= 0:
            raise ValueError("shaft_base_diameter_ft must be > 0")
        if basis.startswith("5-4c(1)"):
            basis += (" The three-base-diameter floor for shafts is printed "
                      "under 5-4c(2)(a), deep groundwater; not applied.")
        elif 3 * shaft_base_diameter_ft > xa:
            xa = 3.0 * shaft_base_diameter_ft
            basis += (" Raised to 3 times the shaft base diameter: the depth "
                      "Xa should not be estimated less than three times the "
                      "base diameter of a shaft foundation.")
    return {
        "active_zone_depth_ft": xa,
        "active_zone_depth_m": round(xa * _FT_TO_M, 3),
        "basis": basis,
        "reference": f"{_REF}, para 5-4c, printed p. 5-4 (PDF 39)",
    }


def table_foundation_selection(predicted_differential_movement_in=None,
                               effective_plasticity_index=None):
    """Foundation systems for expansive soils, UFC 3-220-07 Table 6-1
    (printed p. 6-2, PDF 44); returns the printed systems that apply to the
    predicted differential movement (inches) or effective plasticity index,
    with the printed remarks and, for stiffened thin mats, beam depth and
    spacing.

    Table 6-1 as printed: 1/2 in, effective PI < 15, shallow individual,
    continuous wall or strip footings; reinforced and stiffened thin mat:
    light (1/2 to 1 in, PI 15 to 25; beams 16 to 20 in deep at 20 to 15 ft),
    medium (1 to 2 in, PI 26 to 40; 20 to 25 in at 15 to 12 ft), heavy (2 to
    4 in, PI > 41; 25 to 30 in at 15 to 12 ft); thick reinforced mat and
    deep foundations (pile or drilled shaft), no limit. Rows are read as:
    movement <= 1/2, (1/2, 1], (1, 2], (2, 4], over 4 (no-limit systems
    only); PI < 15, 15-25, over 25 to 40, over 40 (the printed 25-26 and
    40-41 gaps go to the higher row; the code's choice). Figure 6-1 (p. 6-3)
    gives the effective PI.

    Parameters
    ----------
    predicted_differential_movement_in : float, optional
        Predicted differential movement, inches.
    effective_plasticity_index : float, optional
        Effective (or average) PI of the top 15 ft (Figure 6-1). Used when
        no movement is given.

    Returns
    -------
    dict
        Keys: predicted_differential_movement_in or
        effective_plasticity_index, systems (list of dicts as printed),
        reference.

    Raises
    ------
    ValueError
        If neither input is given or a value is negative.
    """
    m = predicted_differential_movement_in
    pi = effective_plasticity_index
    if m is None and pi is None:
        raise ValueError(
            "Give predicted_differential_movement_in or "
            "effective_plasticity_index (Table 6-1, p. 6-2)")
    if m is not None:
        if m < 0:
            raise ValueError(f"predicted_differential_movement_in must be >= 0, got {m}")
        if m <= 0.5:
            row = "shallow"
        elif m <= 1:
            row = "light"
        elif m <= 2:
            row = "medium"
        elif m <= 4:
            row = "heavy"
        else:
            row = None
        out = {"predicted_differential_movement_in": m}
    else:
        if pi < 0:
            raise ValueError(f"effective_plasticity_index must be >= 0, got {pi}")
        if pi < 15:
            row = "shallow"
        elif pi <= 25:
            row = "light"
        elif pi <= 40:
            row = "medium"
        else:
            row = "heavy"
        out = {"effective_plasticity_index": pi}
    systems = []
    if row == "shallow":
        systems.append({**_SHALLOW,
                        "predicted_differential_movement_in": "1/2",
                        "effective_plasticity_index": "<15"})
    elif row is not None:
        systems.append(_thin_mat(row))
    systems.extend(dict(s) for s in _NO_LIMIT)
    out["systems"] = systems
    out["reference"] = f"{_REF}, Table 6-1, printed p. 6-2 (PDF 44)"
    return out


def table_grade_beam_void_space(predicted_total_heave_in=None):
    """Void space beneath grade beams spanning between shafts, UFC 3-220-07
    paragraph 6-4, Grade beams (printed p. 6-16, PDF 58); returns the
    printed rule "6 to 12 inches or 2 times the predicted total heave of
    soil located above the base of the shaft foundation (whichever is
    larger)" and, given the heave, the void in inches.

    With a predicted total heave h (in.): void_space_low_in = max(6, 2h),
    void_space_high_in = max(12, 2h). Figure 6-12 (p. 6-17) shows typical
    void details (a 6-in. void). Grade beams resting on the soil without
    void spaces are not recommended.

    Parameters
    ----------
    predicted_total_heave_in : float, optional
        Predicted total heave of the soil above the base of the shaft
        foundation, inches.

    Returns
    -------
    dict
        Keys: void_space_low_in, void_space_high_in, void_space_low_mm,
        void_space_high_mm (conversions), predicted_total_heave_in, printed,
        reference.

    Raises
    ------
    ValueError
        If the heave is negative.
    """
    h = predicted_total_heave_in
    if h is not None and h < 0:
        raise ValueError(f"predicted_total_heave_in must be >= 0, got {h}")
    lo, hi = (6.0, 12.0) if h is None else (max(6.0, 2.0 * h), max(12.0, 2.0 * h))
    return {
        "predicted_total_heave_in": h,
        "void_space_low_in": lo,
        "void_space_high_in": hi,
        "void_space_low_mm": round(lo * _IN_TO_MM, 1),
        "void_space_high_mm": round(hi * _IN_TO_MM, 1),
        "printed": (
            "These grade beams should be isolated from the underlying "
            "swelling soil with a void space beneath the beams of 6 to 12 "
            "inches or 2 times the predicted total heave of soil located "
            "above the base of the shaft foundation (whichever is larger). "
            "... Grade beams resting on the soil without void spaces are "
            "subject to distortion from uplift pressure of swelling "
            "foundation soil and are not recommended."),
        "reference": f"{_REF}, para 6-4, Grade beams, printed p. 6-16 (PDF 58)",
    }


# ---------------------------------------------------------------------------
# Figure 4-1 Van Der Merwe potential expansiveness (PDF 32, printed p. 4-2)
# ---------------------------------------------------------------------------

#: PE (inch/foot of depth) per level, para 4-1c (p. 4-1 to 4-2): "assumed
#: values of PE = 0, 1/4, 1/2, and 1 inch/foot for low, medium, high, and
#: very high levels, respectively, of potential expansiveness".
_FIG_4_1_PE = {"low": 0.0, "medium": 0.25, "high": 0.5, "very high": 1.0}
#: Each region's lower-left corner, from the axis ticks (clay fraction 12,
#: 18, 27 %; PI 12.5, 23, 32). Every region is bounded below and to the
#: right by the sloped line through the ticks (24, 12.5), (45, 23) and
#: (63, 32), PI = 0.5 x clay + 0.5.
_FIG_4_1_CORNERS = (("very high", 27.0, 32.0), ("high", 18.0, 23.0),
                    ("medium", 12.0, 12.5))
#: The chart's frame: clay fraction 0 to about 70 %, PI 0 to about 70.
_FIG_4_1_MAX = 70.0
_FIG_4_1_TRACE = (
    "Region boundaries taken at the axis ticks of Figure 4-1 (clay fraction "
    "12, 18, 24, 27, 45, 63 %; PI 12.5, 23, 32): medium from clay 12 and "
    "PI 12.5, high from clay 18 and PI 23, very high from clay 27 and PI "
    "32, each above the sloped line PI = 0.5 x clay + 0.5 through (24, "
    "12.5), (45, 23) and (63, 32). The drawn lines do not sit exactly on "
    "these values. Read at 400 dpi (two traces in the build and an "
    "independent one), the vertical lines lie 0.2 to 0.7 % clay to the "
    "right of the ticks 12, 18 and 27, and the sloped line meets the "
    "horizontal lines at clay about 24.8, 45.0 to 45.5 and 63.7 to 63.8. "
    "The chart's own PI marks (the bottom axis and the dashes at 12.5, 23 "
    "and 32) do not fit one scale closer than about 0.5 PI, so the PI "
    "readings depend on the marks used: the lowest horizontal line reads "
    "12.4 to 13.0, the others 22.8 to 23.0 and 32.0 to 32.4, and the "
    "sloped line 0 to 0.6 PI below PI = 0.5 x clay + 0.5. A point within "
    "about 1 % clay or 1 PI of a boundary may therefore lie in the "
    "neighbouring region on the drawn chart. A point on a boundary is "
    "given the higher level (the code's choice). The frame runs to about "
    "70 on both axes; no value is drawn beyond it.")


def figure_4_1_potential_expansiveness(plasticity_index, clay_fraction_pct):
    """Potential expansiveness PE (inch per foot of depth) for Van Der
    Merwe's method, UFC 3-220-07 Figure 4-1 (printed p. 4-2, PDF 32), from
    the PI and the clay fraction (percent finer than 2 microns) of the
    whole sample; returns the level (low, medium, high or very high) and
    PE = 0, 1/4, 1/2 or 1 inch/foot.

    Paragraph 4-1c (p. 4-1 to 4-2): "The PE is found by assumed values of
    PE = 0, 1/4, 1/2, and 1 inch/foot for low, medium, high, and very high
    levels, respectively, of potential expansiveness, defined in figure
    4-1 as functions of the PI and the minus 2 micron fraction. The PE
    values are based on consolidometer swell test results and field
    observations. This method does not consider variations in initial
    moisture conditions." PE feeds Eq. 4-1
    (equations.eq_4_1_van_der_merwe_heave).

    The chart is read as regions bounded at its axis ticks: medium from
    clay 12 % and PI 12.5, high from clay 18 % and PI 23, very high from
    clay 27 % and PI 32, each region lying above the sloped line through
    (24, 12.5), (45, 23) and (63, 32), PI = 0.5 x clay + 0.5; everything
    else is low. The drawn lines sit up to about 0.8 % clay and 0.6 PI
    off these values, and the chart's own PI marks agree with one another
    only to about 0.5 PI (trace_note gives the readings), so a point
    within about 1 % clay or 1 PI of a boundary may lie in the
    neighbouring region on the drawn chart. A point on a boundary takes
    the higher level.

    Parameters
    ----------
    plasticity_index : float
        PI of the whole sample, percent (0 to 70, the chart's frame).
    clay_fraction_pct : float
        Clay fraction of the whole sample, percent finer than 2 microns
        (0 to 70, the chart's frame).

    Returns
    -------
    dict
        Keys: level, pe_in_per_ft, plasticity_index, clay_fraction_pct,
        trace_note, source.

    Raises
    ------
    ValueError
        If either input is outside 0 to 70, the chart's drawn range.
    """
    pi, c = plasticity_index, clay_fraction_pct
    for name, v in (("plasticity_index", pi), ("clay_fraction_pct", c)):
        if v is None or not (0.0 <= v <= _FIG_4_1_MAX):
            raise ValueError(
                f"{name} must be within 0 to {_FIG_4_1_MAX:g}, the range "
                f"Figure 4-1 (p. 4-2) draws; got {v}")
    level = "low"
    if pi >= 0.5 * c + 0.5:
        for name, c0, pi0 in _FIG_4_1_CORNERS:
            if c >= c0 and pi >= pi0:
                level = name
                break
    return {
        "plasticity_index": pi,
        "clay_fraction_pct": c,
        "level": level,
        "pe_in_per_ft": _FIG_4_1_PE[level],
        "trace_note": _FIG_4_1_TRACE,
        "source": f"{_REF}, Figure 4-1 and para 4-1c, printed p. 4-2 (PDF 32)",
    }
