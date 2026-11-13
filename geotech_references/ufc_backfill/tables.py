"""UFC 3-220-04FA backfill lookup tables.

From UFC 3-220-04FA, Backfill for Subsurface Structures, 16 January 2004
(the reproduced TM 5-818-4/AFM 88-5, Chap. 5), docs/ufc_3_220_04fa_2004.pdf.
Every value is read off the printed page named in its result: Table 5-1
(p. 5-3), paragraph 5-1b (p. 5-1 and 5-2), paragraph 3-3d (p. 3-5 and 3-6)
and Figure 2-5 (p. 2-7). Units are the print's (inches, pounds, psf, ft),
with SI conversions labelled as conversions. PDF page (1-based) = 7 + n
for printed p. 2-n, 17 + n for p. 3-n, 27 + n for p. 5-n.

Rebuilt from the print 2026-11-10 (review pave-06, pave-14): the earlier
tables (an ASTM D698 compaction table, nine-equipment millimetre lift
thicknesses, drain thicknesses and slopes) were not printed in this manual.
"""

_REF = "UFC 3-220-04FA (TM 5-818-4/AFM 88-5, Chap. 5), 16 January 2004"

# ---------------------------------------------------------------------------
# Paragraph 5-1b(4) Density requirements (PDF 29, printed p. 5-2)
# ---------------------------------------------------------------------------

_DENSITY_REQUIREMENTS = {
    "open_area": {
        "min_compaction_pct": 90, "max_compaction_pct": None,
        "printed": ("In open areas of backfill where structures will not be "
                    "constructed, compaction can be less than that required "
                    "in more critical zones. Compaction to 90 percent of CE "
                    "55 maximum dry density as obtained by MIL-STD-621 "
                    "should be adequate in these areas."),
    },
    "beneath_structures_cohesionless": {
        "min_compaction_pct": 95, "max_compaction_pct": 100,
        "printed": ("If structures are to be constructed on or within the "
                    "backfill, compaction of cohesionless soils to within 95 "
                    "to 100 percent of CE 55 maximum dry density ... should "
                    "be required for the full depth of backfill beneath "
                    "these structures."),
    },
    "beneath_structures_cohesive": {
        "min_compaction_pct": 95, "max_compaction_pct": None,
        "printed": ("If structures are to be constructed on or within the "
                    "backfill, compaction ... of cohesive soils to at least "
                    "95 percent of CE 55 should be required for the full "
                    "depth of backfill beneath these structures."),
    },
    "drainage_blankets_and_filters": {
        "min_compaction_pct": 95, "max_compaction_pct": 100,
        "printed": ("Drainage blankets and filters having special gradation "
                    "requirements should be compacted to within 95 to 100 "
                    "percent of CE 55 maximum dry density."),
    },
}
_DENSITY_NOTE = (
    "The specified degree of compaction should be commensurate with the "
    "tolerable amount of settlement, and the compaction equipment used should "
    "be commensurate with the allowable lateral pressure on the structure.")

# ---------------------------------------------------------------------------
# Table 5-1 Summary of Compaction Criteria (PDF 30, printed p. 5-3)
# ---------------------------------------------------------------------------

_T51_GROUP_TYPES = {
    "pervious": ["GW", "GP", "SW", "SP"],
    # printed GM GC SM SC ML CL OL OH MH CH OH (OH printed twice)
    "semipervious_impervious": ["GM", "GC", "SM", "SC", "ML", "CL", "OL",
                                "OH", "MH", "CH"],
}
_T51_GROUP_LABEL = {"pervious": "Pervious (Free-Draining)",
                    "semipervious_impervious": "Semipervious and Impervious"}

# equipment rows: (equipment as printed, footnote, passes or coverages,
# compacted lift thickness in inches as printed)
_TABLE_5_1 = {
    ("pervious", "compacted"): {
        "degree_of_compaction": ["90 to 95% of CE 55 maximum density",
                                 "75 to 85% of relative density"],
        "equipment": [
            ("Vibratory rollers and compactors", None, "Indefinite", "Indefinite"),
            ("Rubber-tired roller", "b", "2-5 coverages", "12"),
            ("Crawler-type tractor", "c", "2-5 coverages", "8"),
            ("Power hand tamper", "d", "Indefinite", "6"),
        ],
        "placement_water_content": "Saturate by flooding",
        "field_control": ("Control tests at intervals to determine degree of "
                          "compaction or relative density"),
    },
    ("pervious", "semicompacted"): {
        "degree_of_compaction": ["85 to 90% of CE 55 maximum density",
                                 "65 to 75% of relative density"],
        "equipment": [
            ("Rubber-tired roller", "b", "2-5 coverages", "14"),
            ("Crawler-type tractor", "c", "1-2 coverages", "10"),
            ("Power hand tamper", "d", "Indefinite", "8"),
            ("Controlled routing of construction equipment", None, "Indefinite", "8-10"),
        ],
        "placement_water_content": "Saturate by flooding",
        "field_control": "Control tests as noted above, if needed",
    },
    ("semipervious_impervious", "compacted"): {
        "degree_of_compaction": ["90 to 95% of CE 55 maximum density"],
        "equipment": [
            ("Rubber-tired roller", "b", "2-5 coverages", "8"),
            ("Sheepsfoot roller", "e", "4-8 passes", "6"),
            ("Power hand tamper", "d", "Indefinite", "4"),
        ],
        "placement_water_content": "Optimum water content",
        "field_control": ("Control tests at intervals to determine degree of "
                          "compaction"),
    },
    ("semipervious_impervious", "semicompacted"): {
        "degree_of_compaction": ["85 to 90% of CE 55 maximum density"],
        "equipment": [
            ("Rubber-tired roller", "b", "2-4 coverages", "10"),
            ("Sheepsfoot roller", "e", "4-8 passes", "8"),
            ("Crawler-type tractor", "c", "3 coverages", "6"),
            ("Power hand tamper", "d", "Indefinite", "6"),
            ("Controlled routing of construction equipment", None, "Indefinite", "6-8"),
        ],
        "placement_water_content": (
            "(A) Optimum water content (B) By observation; wet side-maximum "
            "water content at which material can satisfactorily operate, dry "
            "side-minimum water content required to bond particles and which "
            "will not result in voids or honeycombed material"),
        "field_control": (
            "(A) Control tests as noted above, if needed (B) Field control "
            "exercised by visual inspection of action of compacting "
            "equipment"),
    },
}
_T51_NOTE = (
    "The above requirements will be adequate in relation to most "
    "construction. In special cases where tolerable settlements are unusually "
    "small, it may be necessary to employ additional compaction equivalent to "
    "95 to 100% of compaction effort. A coverage consists of one application "
    "of the wheel of a rubber-tired roller or the threads of a crawler-type "
    "tractor over each point in the area being compacted. For a sheepsfoot "
    "roller, one pass consists of one movement of a sheepsfoot roller drum "
    "over the area being compacted.")
_T51_FOOTNOTES = {
    "a": "From TM 5-818-1.",
    "b": ("Rubber-tired rollers having a wheel load between 18,000 and "
          "25,000 lb and a tire pressure between 80 and 100 psi."),
    "c": ("Crawler-type tractors weighing not less than 20,000 lb and "
          "exerting a foot pressure not less than 6-1/2 psi."),
    "d": ("Power hand tampers weighing more than 100 lb; pneumatic or "
          "operated by gasoline engine."),
    "e": ("Sheepsfoot rollers having a foot pressure between 250 and 500 psi "
          "and tamping feet 7 to 10 in. in length with a face area between 7 "
          "and 16 sq in."),
}

# ---------------------------------------------------------------------------
# Paragraph 5-1b(3) Lift thickness (PDF 28-29, printed p. 5-1 and 5-2)
# ---------------------------------------------------------------------------

_LIFT_THICKNESS = {
    "cohesive_sheepsfoot_or_pneumatic": {
        "loose_lift_in": "approximately 10", "compacted_lift_in": "approximately 6",
        "printed": ("As a general rule, a loose-lift thickness that will "
                    "result in a 6-inch lift when compacted can be allowed "
                    "for most sheepsfoot and pneumatic-tired rollers. "
                    "Cohesive soils placed in approximately 10-inch loose "
                    "lifts will compact to approximately 6 inches."),
        "page": "5-1, 5-2", "pdf_page_index": [28, 29],
    },
    "cohesionless_sheepsfoot_or_pneumatic": {
        "loose_lift_in": "approximately 8", "compacted_lift_in": "6",
        "printed": ("As a general rule, a loose-lift thickness that will "
                    "result in a 6-inch lift when compacted can be allowed "
                    "for most sheepsfoot and pneumatic-tired rollers. ... "
                    "cohesionless soils placed in approximately 8-inch base "
                    "lifts will compact to 6 inches."),
        "page": "5-1, 5-2", "pdf_page_index": [28, 29],
    },
    "cohesionless_heavy_vibratory": {
        "loose_lift_in": "about 12 to 15", "compacted_lift_in": None,
        "printed": ("Adequate compaction can be achieved in cohesionless "
                    "materials of about 12- to 15-inch loose-lift thickness "
                    "if heavy vibratory equipment is used."),
        "page": "5-2", "pdf_page_index": 29,
    },
    "confined_clean_cohesionless": {
        "loose_lift_in": "4 to 6", "compacted_lift_in": None,
        "printed": ("In confined zones where clean cohesionless backfill "
                    "material is used, a loose-lift thickness of 4 to 6 "
                    "inches and a vibratory plate or walk-behind, dual-drum "
                    "vibratory roller for compaction is recommended."),
        "page": "5-2", "pdf_page_index": 29,
    },
    "confined_cohesive": {
        "loose_lift_in": "not more than 4", "compacted_lift_in": None,
        "printed": ("Where cohesive soils are used as backfill in confined "
                    "zones, use of rammer compactors and a loose-lift "
                    "thickness of not more than 4 inches should be "
                    "specified. Experience has shown that \"two-by-four\" "
                    "wood rammers, or single air tampers (commonly referred "
                    "to as \"powder puffs\" or \"pogo sticks\") do not "
                    "produce sufficient compaction."),
        "page": "5-2", "pdf_page_index": 29,
    },
}
_LIFT_NOTE = (
    "The addition of vibration to rolling equipment used for compacting "
    "cohesive soils generally has little effect on the lift thickness that "
    "can be compacted, although compaction to the desired density can "
    "sometimes be obtained by fewer coverages of the equipment.")

# ---------------------------------------------------------------------------
# Paragraph 5-1b(2) Compaction equipment, backfill material, and zones
# (PDF 28, printed p. 5-1)
# ---------------------------------------------------------------------------

_EQUIPMENT = {
    ("coarse_grained_slightly_plastic", "open"): (
        "In open zones, coarse-grained soils that exhibit slight plasticity "
        "(clayey sands, silty sands, clayey gravels, and silty gravels) "
        "should be compacted with either sheepsfoot or rubber-tired rollers; "
        "close control of water content is required where silt is present "
        "in substantial amounts. The addition of vibration to any of the "
        "means of compaction mentioned above will usually improve the "
        "compaction of soils in this category."),
    ("sands_little_or_no_fines", "open"): (
        "For sands and gravelly sands with little or no fines, good "
        "compaction results are obtained with tractor compaction. The "
        "addition of vibration to any of the means of compaction mentioned "
        "above will usually improve the compaction of soils in this "
        "category."),
    ("gravels", "open"): (
        "Good compaction can also be achieved in gravels and gravel-sand "
        "mixtures with either a crawler tractor or rubber-tired and "
        "steel-wheeled rollers. The addition of vibration to any of the "
        "means of compaction mentioned above will usually improve the "
        "compaction of soils in this category."),
    ("cohesionless", "confined"): (
        "In confined zones, adequate compaction of cohesionless soils in "
        "either the air-dried or saturated condition can be achieved by "
        "vibratory-plate compactors with a static weight of at least 100 "
        "pounds. If the material is compacted in the saturated condition, "
        "good compaction can be achieved by internal vibration (for example, "
        "by using concrete vibrators). Downward drainage is required to "
        "maintain seepage forces in a downward direction if the placed "
        "material is saturated to aid in compaction."),
    ("fine_grained_low_to_medium_plasticity", "open"): (
        "Inorganic clays, inorganic silts, and very fine sands of low to "
        "medium plasticity are fairly easily compacted in open zones with "
        "sheepsfoot or rubber-tired rollers in the 15,000-pound and above "
        "wheel-load class."),
    ("fine_grained_low_to_medium_plasticity", "confined"): (
        "Some inorganic clays can be adequately compacted in confined zones "
        "using rammer or impact compactors with a static weight of at least "
        "100 pounds provided close control of lift thickness and water "
        "content is maintained."),
    ("fine_grained_highly_plastic", "open"): (
        "Fine-grained, highly plastic materials, though not good backfill "
        "materials, can best be compacted in open zones with sheepsfoot "
        "rollers. Sheepsfoot rollers leave the surface of the backfill in a "
        "rough condition, which provides an excellent bond between lifts."),
    ("fine_grained_highly_plastic", "confined"): (
        "In confined areas the best results, which are not considered good, "
        "are obtained with rammer or impact compactors."),
}

# ---------------------------------------------------------------------------
# Paragraph 3-3d Types of backfill material (PDF 22-23, printed p. 3-5, 3-6)
# ---------------------------------------------------------------------------

_MATERIAL_CATEGORIES = {
    "coarse_grained": {
        "uscs": ["GW", "GP", "GM", "GC", "SW", "SP", "SM", "SC"],
        "paragraph": "3-3d(1)", "page": "3-5", "pdf_page_index": 22,
        "printed": (
            "Coarse-grained soils include gravelly and sandy soils and range "
            "from clayey sands (SC) through the well-graded gravels of "
            "gravel-sand mixtures (GW) with little or no fines (table 3-1). "
            "They will exhibit slight to no plasticity. All of the "
            "well-graded soils falling in this category have fairly good "
            "compaction characteristics and when adequately compacted "
            "provide good backfill and foundation support. One difficulty "
            "that might arise with soils in this category would be in "
            "obtaining good compaction of the poorly graded sands and "
            "gravels. ... Coarse-grained materials compacted to a low "
            "relative density are susceptible upon saturation to "
            "liquefaction under dynamic loads. ... Clean, granular, "
            "well-graded materials having a maximum size of 1 inch with 95 "
            "percent passing the No. 4 sieve and 5 percent or less passing "
            "the No. 200 sieve are excellent for use in these [confined] "
            "zones."),
    },
    "fine_grained_low_to_medium_plasticity": {
        "uscs": ["CL", "ML"],
        "paragraph": "3-3d(2)", "page": "3-5, 3-6", "pdf_page_index": [22, 23],
        "printed": (
            "Inorganic clays (CL) of low to medium plasticity ... and "
            "inorganic silts and very fine sands (ML) of low plasticity ... "
            "are included in this category. The inorganic clays are "
            "relatively impervious and can be compacted fairly easily with "
            "heavy compaction equipment to provide a good stable backfill. "
            "Soils in the CL group can be compacted in confined areas to a "
            "fairly high degree of compaction with proper water content and "
            "lift thickness control. The clayey sands of the SC group and "
            "clayey silts of the ML group can be compacted to fairly high "
            "densities, but close control of water content is essential and "
            "sometimes critical ... Some ML soils, if compacted on the dry "
            "side of optimum, may lose considerable strength upon saturation "
            "after compaction. Considerable settlement may occur. Caution "
            "must therefore be exercised in the use of such soils as "
            "backfill, particularly below the groundwater level. Also, "
            "saturated ML soils are likely to be highly susceptible to "
            "liquefaction when dynamically loaded."),
    },
    "marginal_fine_grained_high_plasticity": {
        "uscs": ["CH", "MH", "OH"],
        "paragraph": "3-3d(5)(a)", "page": "3-6", "pdf_page_index": 23,
        "printed": (
            "Marginal materials are these materials that because of either "
            "their poor compaction, consolidation, or swelling "
            "characteristics would not normally be used as backfill if "
            "sources of suitable material were available. Material "
            "considered to be marginal include fine-grained soils of high "
            "plasticity and expansive clays. ... The fine-grained, highly "
            "plastic materials make poor backfill because of the difficulty "
            "in handling, exercising water-content control, and compacting. "
            "... The only soil type in this category that might be "
            "considered suitable as backfill is inorganic clay (CH). Use of "
            "CH soils should be avoided in confined areas if a high degree "
            "of compaction is needed to minimize backfill settlement or to "
            "provide a high compression modulus."),
    },
}

# ---------------------------------------------------------------------------
# Figure 2-5a Maximum induced lateral pressures (PDF 14, printed p. 2-7)
# ---------------------------------------------------------------------------

# equipment -> (critical depth Dc, ft; critical lateral pressure (sigma_H)c, psf)
_FIG_2_5A = {
    "10-ton smooth wheel roller": (1.9, 420),
    "3.2-ton vibratory roller": (1.7, 400),
    "1.4-ton vibratory roller": (1.2, 260),
    "400-kg vibratory plate": (1.5, 340),
    "120-kg vibratory plate": (1.0, 240),
}
_FT_TO_M = 0.3048
_PSF_TO_KPA = 0.04788026


def _key(text):
    return str(text).strip().lower().replace("-", "_").replace(" ", "_")


# ---------------------------------------------------------------------------
# Public lookup functions
# ---------------------------------------------------------------------------

def table_compaction_requirements(application):
    """Density requirement for backfill as a percent of CE 55 maximum dry
    density, UFC 3-220-04FA paragraph 5-1b(4) (printed p. 5-2, PDF 29);
    returns min_compaction_pct and max_compaction_pct (percent of CE 55
    maximum dry density by MIL-STD-621; max None where the print gives only
    a minimum) with the printed sentence.

    As printed: open areas where structures will not be constructed, 90;
    beneath structures, cohesionless soils 95 to 100 and cohesive soils at
    least 95, for the full depth of backfill; drainage blankets and filters
    with special gradation requirements, 95 to 100. Table 5-1 (p. 5-3) gives
    the equipment, coverages and lift thicknesses
    (``table_5_1_compaction_criteria``).

    Parameters
    ----------
    application : str
        'open_area', 'beneath_structures_cohesionless',
        'beneath_structures_cohesive' or 'drainage_blankets_and_filters'.

    Returns
    -------
    dict
        Keys: application, min_compaction_pct, max_compaction_pct, basis,
        printed, note, reference.

    Raises
    ------
    ValueError
        If *application* is not one of the printed cases.
    """
    key = _key(application)
    if key not in _DENSITY_REQUIREMENTS:
        raise ValueError(
            f"Unknown application '{application}'. Paragraph 5-1b(4) "
            f"(p. 5-2) prints: {sorted(_DENSITY_REQUIREMENTS)}")
    row = _DENSITY_REQUIREMENTS[key]
    return {
        "application": key,
        "min_compaction_pct": row["min_compaction_pct"],
        "max_compaction_pct": row["max_compaction_pct"],
        "basis": "percent of CE 55 maximum dry density (MIL-STD-621)",
        "printed": row["printed"],
        "note": _DENSITY_NOTE,
        "reference": f"{_REF}, para 5-1b(4), printed p. 5-2 (PDF 29)",
    }


def table_5_1_compaction_criteria(soil_group, compaction="compacted"):
    """Summary of compaction criteria, UFC 3-220-04FA Table 5-1 (printed
    p. 5-3, PDF 30); returns the printed degree of compaction and, for each
    typical piece of equipment, the number of passes or coverages and the
    compacted lift thickness in inches, with the placement water content,
    field control, note and footnotes.

    Soil groups as printed: pervious (free-draining) GW, GP, SW, SP;
    semipervious and impervious GM, GC, SM, SC, ML, CL, OL, OH, MH, CH.
    Compaction: 'compacted' (90 to 95% of CE 55 maximum density; pervious
    also 75 to 85% of relative density) or 'semicompacted' (85 to 90%;
    pervious also 65 to 75% of relative density).

    Parameters
    ----------
    soil_group : str
        'pervious', 'semipervious_impervious', or a USCS symbol from the
        table's soil types (e.g. 'SP', 'CL').
    compaction : str, optional
        'compacted' (default) or 'semicompacted'.

    Returns
    -------
    dict
        Keys: soil_group, soil_group_printed, soil_types,
        degree_of_compaction (list of str), equipment (list of dicts:
        equipment, footnote, passes_or_coverages,
        compacted_lift_thickness_in), placement_water_content,
        field_control, note, footnotes, reference.

    Raises
    ------
    ValueError
        If soil_group or compaction is not in the table.
    """
    g = _key(soil_group)
    if g in ("semipervious_and_impervious", "impervious", "semipervious"):
        g = "semipervious_impervious"
    if g not in _T51_GROUP_TYPES:
        sym = str(soil_group).strip().upper()
        found = [k for k, v in _T51_GROUP_TYPES.items() if sym in v]
        if not found:
            raise ValueError(
                f"Unknown soil group '{soil_group}'. Table 5-1 (p. 5-3) has "
                f"'pervious' {_T51_GROUP_TYPES['pervious']} and "
                f"'semipervious_impervious' "
                f"{_T51_GROUP_TYPES['semipervious_impervious']}")
        g = found[0]
    c = _key(compaction)
    if (g, c) not in _TABLE_5_1:
        raise ValueError(
            f"compaction must be 'compacted' or 'semicompacted', got "
            f"'{compaction}'")
    row = _TABLE_5_1[(g, c)]
    used = sorted({fn for _, fn, _, _ in row["equipment"] if fn})
    return {
        "soil_group": g,
        "soil_group_printed": _T51_GROUP_LABEL[g],
        "soil_types": list(_T51_GROUP_TYPES[g]),
        "compaction": c,
        "degree_of_compaction": list(row["degree_of_compaction"]),
        "equipment": [
            {"equipment": e, "footnote": fn, "passes_or_coverages": p,
             "compacted_lift_thickness_in": t}
            for e, fn, p, t in row["equipment"]],
        "placement_water_content": row["placement_water_content"],
        "field_control": row["field_control"],
        "note": _T51_NOTE,
        "footnotes": {k: _T51_FOOTNOTES[k] for k in ["a"] + used},
        "reference": f"{_REF}, Table 5-1, printed p. 5-3 (PDF 30)",
    }


def table_backfill_material_classification(uscs_class):
    """Backfill category of a USCS soil group as UFC 3-220-04FA paragraph
    3-3d describes it (printed p. 3-5 and 3-6, PDF 22-23); returns the
    category (coarse-grained; fine-grained of low to medium plasticity;
    marginal fine-grained of high plasticity) and the printed text on its
    suitability as backfill.

    The print names the groups in each category: coarse-grained "range from
    clayey sands (SC) through the well-graded gravels ... (GW)"; CL and ML;
    and fine-grained soils of high plasticity, of which "the only soil type
    ... that might be considered suitable as backfill is inorganic clay
    (CH)". Table 3-1, which the text cites, "Typical Engineering Properties
    of Compacted Materials", is printed on p. 3-3 (PDF 20); this package
    does not code it. Groups the paragraph does not place (OL, Pt) are
    refused.

    Parameters
    ----------
    uscs_class : str
        USCS symbol (e.g. 'GW', 'CL'); a dual symbol (e.g. 'SP-SM') is
        accepted when both symbols are in the same category.

    Returns
    -------
    dict
        Keys: uscs_class, category, paragraph, printed, reference.

    Raises
    ------
    ValueError
        If the symbol is not placed by paragraph 3-3d, or a dual symbol
        spans two categories.
    """
    sym = str(uscs_class).strip().upper()
    parts = [p for p in sym.split("-") if p]
    cats = set()
    for p in parts:
        found = [k for k, v in _MATERIAL_CATEGORIES.items() if p in v["uscs"]]
        if not found:
            raise ValueError(
                f"USCS class '{uscs_class}': paragraph 3-3d (p. 3-5, 3-6) "
                f"places only "
                f"{sorted(s for v in _MATERIAL_CATEGORIES.values() for s in v['uscs'])}")
        cats.add(found[0])
    if len(cats) != 1:
        raise ValueError(
            f"USCS class '{uscs_class}' spans two paragraph 3-3d categories "
            f"({sorted(cats)}); look each symbol up separately")
    cat = cats.pop()
    row = _MATERIAL_CATEGORIES[cat]
    return {
        "uscs_class": sym,
        "category": cat,
        "paragraph": row["paragraph"],
        "printed": row["printed"],
        "reference": (f"{_REF}, para {row['paragraph']}, printed p. "
                      f"{row['page']} (PDF {row['pdf_page_index']})"),
    }


def table_maximum_lift_thickness(case):
    """Loose-lift thickness, inches, UFC 3-220-04FA paragraph 5-1b(3)
    (printed p. 5-1 and 5-2, PDF 28-29); returns the printed loose-lift
    (and, where printed, compacted-lift) thickness for the material,
    equipment and zone.

    As printed: cohesive soils, sheepsfoot and pneumatic-tired rollers,
    approximately 10 in loose to approximately 6 in compacted;
    cohesionless, approximately 8 in to 6 in; cohesionless with heavy
    vibratory equipment, about 12 to 15 in loose; confined zones, clean
    cohesionless, 4 to 6 in loose (vibratory plate or walk-behind dual-drum
    vibratory roller); confined zones, cohesive, not more than 4 in loose
    (rammer compactors). Table 5-1 gives compacted lift thicknesses by
    equipment (``table_5_1_compaction_criteria``).

    Parameters
    ----------
    case : str
        'cohesive_sheepsfoot_or_pneumatic',
        'cohesionless_sheepsfoot_or_pneumatic',
        'cohesionless_heavy_vibratory', 'confined_clean_cohesionless' or
        'confined_cohesive'.

    Returns
    -------
    dict
        Keys: case, loose_lift_in, compacted_lift_in (None where not
        printed), printed, note, reference. The thicknesses are the printed
        words (e.g. 'approximately 10', '4 to 6').

    Raises
    ------
    ValueError
        If *case* is not one of the printed cases.
    """
    key = _key(case)
    if key not in _LIFT_THICKNESS:
        raise ValueError(
            f"Unknown case '{case}'. Paragraph 5-1b(3) (p. 5-1, 5-2) "
            f"prints: {sorted(_LIFT_THICKNESS)}")
    row = _LIFT_THICKNESS[key]
    return {
        "case": key,
        "loose_lift_in": row["loose_lift_in"],
        "compacted_lift_in": row["compacted_lift_in"],
        "printed": row["printed"],
        "note": _LIFT_NOTE,
        "reference": (f"{_REF}, para 5-1b(3), printed p. {row['page']} "
                      f"(PDF {row['pdf_page_index']})"),
    }


def table_compaction_equipment_selection(soil_type, zone="open"):
    """Compaction equipment for a backfill material and zone, UFC 3-220-04FA
    paragraph 5-1b(2) (printed p. 5-1, PDF 28); returns the printed
    recommendation.

    Materials as printed: coarse-grained soils with slight plasticity
    (clayey/silty sands and gravels); sands and gravelly sands with little
    or no fines; gravels and gravel-sand mixtures; cohesionless soils in
    confined zones; inorganic clays, silts and very fine sands of low to
    medium plasticity; fine-grained, highly plastic materials. Table 5-1
    lists equipment with coverages and lift thicknesses
    (``table_5_1_compaction_criteria``).

    Parameters
    ----------
    soil_type : str
        'coarse_grained_slightly_plastic', 'sands_little_or_no_fines',
        'gravels', 'cohesionless', 'fine_grained_low_to_medium_plasticity'
        or 'fine_grained_highly_plastic'.
    zone : str, optional
        'open' (default) or 'confined'. The print gives 'cohesionless' for
        confined zones only, and the three coarse-grained open-zone cases
        for open zones only.

    Returns
    -------
    dict
        Keys: soil_type, zone, printed, reference.

    Raises
    ------
    ValueError
        If the soil type and zone are not a printed case.
    """
    key = (_key(soil_type), _key(zone))
    if key not in _EQUIPMENT:
        raise ValueError(
            f"No printed case for soil_type '{soil_type}', zone '{zone}'. "
            f"Paragraph 5-1b(2) (p. 5-1) prints: {sorted(_EQUIPMENT)}")
    return {
        "soil_type": key[0],
        "zone": key[1],
        "printed": _EQUIPMENT[key],
        "reference": f"{_REF}, para 5-1b(2), printed p. 5-1 (PDF 28)",
    }


def figure_2_5_compaction_induced_lateral_pressure(equipment):
    """Maximum lateral pressure induced by compaction against a vertical
    wall, UFC 3-220-04FA Figure 2-5a (printed p. 2-7, PDF 14); returns the
    printed critical depth Dc (ft) and critical lateral pressure (sigma_H)c
    (psf), with SI conversions.

    Figure 2-5a draws the lateral pressure in excess of active pressure
    induced by compaction: from zero at the top of the backfill it rises to
    (sigma_H)c at the critical depth Dc, then runs straight down at
    (sigma_H)c until the active pressure line K_A sigma_v crosses it, near
    the base of the wall as drawn. Paragraph 2-3d(2) (p. 2-6): the diagram assumes the equipment
    can operate to within 6 inches of the wall; for an operating distance 5
    feet from the wall the induced pressure is much less than that caused
    by the backfill (Figure 2-5b). The figure gives no equation.

    Parameters
    ----------
    equipment : str
        As printed: '10-ton smooth wheel roller', '3.2-ton vibratory
        roller', '1.4-ton vibratory roller', '400-kg vibratory plate' or
        '120-kg vibratory plate'.

    Returns
    -------
    dict
        Keys: equipment, critical_depth_ft, critical_lateral_pressure_psf,
        critical_depth_m, critical_lateral_pressure_kPa (conversions),
        printed_basis, reference.

    Raises
    ------
    ValueError
        If *equipment* is not one of the five printed rows.
    """
    want = _key(equipment)
    match = [e for e in _FIG_2_5A if _key(e) == want]
    if not match:
        raise ValueError(
            f"Unknown equipment '{equipment}'. Figure 2-5a (p. 2-7) prints: "
            f"{list(_FIG_2_5A)}")
    e = match[0]
    dc_ft, sig_psf = _FIG_2_5A[e]
    return {
        "equipment": e,
        "critical_depth_ft": dc_ft,
        "critical_lateral_pressure_psf": sig_psf,
        "critical_depth_m": round(dc_ft * _FT_TO_M, 3),
        "critical_lateral_pressure_kPa": round(sig_psf * _PSF_TO_KPA, 2),
        "printed_basis": (
            "Lateral pressure in excess of active pressure induced by "
            "compaction; the diagram assumes the equipment can operate to "
            "within 6 inches of the wall (para 2-3d(2), p. 2-6)."),
        "reference": f"{_REF}, Figure 2-5a, printed p. 2-7 (PDF 14)",
    }
