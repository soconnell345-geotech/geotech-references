"""UFC 3-250-11, Soil Stabilization and Modification for Pavements - tables.

Digitized tables from UFC 3-250-11 (30 Nov 2020 edition). Follows the DM7/GEC
pattern: private data with ``_TABLE_*`` prefix, public lookup functions with
string-matched keys (``.strip().lower()`` normalization), ``ValueError`` on
bad keys listing valid options. Page citations are the 0-based fitz page
index of ``docs/ufc_3_250_11_2020.pdf`` (cited as ``pdf_page``) plus the
printed page number; ``pdf_page_index = printed_page + 7`` throughout this
document (verified at printed pp. 1, 8, 13, 63, 69, 75).

UNITS: this document is US-customary native (inches, percent by weight); mm
given parenthetically in the source is kept as noted, not force-converted.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 2-1: Minimum Unconfined Compressive Strength for Cement-, Lime-,
# Lime-Cement-, and Lime-Cement-Fly-Ash-Stabilized Soils (printed p.10,
# pdf_page 17). Footnote a: UCS at 7 days for cement, 28 days for lime/LF/LCF.
# ============================================================================

_TABLE_2_1 = {
    "base": {"flexible": {"psi": 750, "mpa": 5.17}, "rigid": {"psi": 500, "mpa": 3.45}},
    "subbase_or_subgrade": {"flexible": {"psi": 250, "mpa": 1.72}, "rigid": {"psi": 200, "mpa": 1.38}},
}


def table_2_1_min_ucs_requirements(layer: str, pavement_type: str) -> dict:
    """Minimum unconfined compressive strength for stabilized soil (Table 2-1).

    Applies to cement-, lime-, lime-cement-, and lime-cement-fly-ash (LCF)
    stabilized soils qualifying for reduced-thickness design. UCS measured
    at 7 days for cement stabilization, 28 days for lime/LF/LCF (footnote a).

    Parameters
    ----------
    layer : str
        'base' or 'subbase_or_subgrade' (subbase course, select material,
        or subgrade).
    pavement_type : str
        'flexible' or 'rigid'.

    Returns
    -------
    dict
        {'layer', 'pavement_type', 'min_ucs_psi', 'min_ucs_mpa',
         'test_age_note', 'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If layer or pavement_type is not recognized.
    """
    lyr = layer.strip().lower().replace(" ", "_")
    pt = pavement_type.strip().lower()
    if lyr not in _TABLE_2_1:
        raise ValueError(f"Unknown layer '{layer}'. Valid: {', '.join(_TABLE_2_1)}")
    if pt not in _TABLE_2_1[lyr]:
        raise ValueError(f"Unknown pavement_type '{pavement_type}'. Valid: flexible, rigid")
    row = _TABLE_2_1[lyr][pt]
    return {
        "layer": lyr, "pavement_type": pt,
        "min_ucs_psi": row["psi"], "min_ucs_mpa": row["mpa"],
        "test_age_note": "UCS at 7 days for cement stabilization, 28 days for lime/LF/LCF stabilization",
        "reference": "UFC 3-250-11, Table 2-1, p.10",
        "pdf_page": 17,
    }


# ============================================================================
# Table 2-2: Durability Requirements (printed p.11, pdf_page 18)
# ============================================================================

_TABLE_2_2 = {
    "granular_pi_lt_10": 11,
    "granular_pi_gt_10": 8,
    "silt": 8,
    "clay": 6,
}


def table_2_2_durability_requirements(soil_type: str) -> dict:
    """Maximum allowable weight loss after 12 wet-dry/freeze-thaw cycles (Table 2-2).

    Parameters
    ----------
    soil_type : str
        'granular_pi_lt_10' (granular, PI < 10), 'granular_pi_gt_10'
        (granular, PI > 10), 'silt', or 'clay'.

    Returns
    -------
    dict
        {'soil_type', 'max_weight_loss_pct', 'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If soil_type is not recognized.
    """
    key = soil_type.strip().lower().replace(" ", "_")
    if key not in _TABLE_2_2:
        raise ValueError(f"Unknown soil_type '{soil_type}'. Valid: {', '.join(_TABLE_2_2)}")
    return {
        "soil_type": key,
        "max_weight_loss_pct": _TABLE_2_2[key],
        "reference": "UFC 3-250-11, Table 2-2, p.11",
        "pdf_page": 18,
    }


# ============================================================================
# Table 2-3: Guide for Selecting a Stabilizing Additive (printed p.13,
# pdf_page 20). Area keys correspond to Figure 2-1's gradation-triangle
# areas (a chart read-off, catalogued for vision read-off in
# figures_catalog.json -- NOT reproduced numerically here; the user reads
# percent passing No. 200 and percent sand [No.4-No.200] off the triangle to
# get the area, then calls this function).
#
# Footnotes (as printed):
#   (a) Monofilament polypropylene fiber - length/denier vary by soil type.
#   (b) Soil classification corresponds to ASTM D2487-17; LL/PI restriction
#       per ASTM D4318-17e1.
#   (c) PI <= 20 + 50 - percent passing No. 200 (0.075 mm) sieve
#       (see equations.equation_cement_pi_limit_table_2_3).
# ============================================================================

_TABLE_2_3_FOOTNOTES = {
    "a": "Monofilament polypropylene fiber - Length and denier will vary depending on soil type",
    "b": "Soil classification corresponds to ASTM D2487-17. Restriction on liquid limit (LL) and "
         "plasticity index (PI) is in accordance with ASTM D4318-17e1.",
    "c": "PI <= 20 + 50 - percent passing No. 200 (0.075 mm) sieve",
}

_TABLE_2_3 = {
    "1a": {
        "uscs_classes": ["SW", "SP"],
        "stabilizers": ["Polymer/bituminous emulsion and cement", "Portland cement",
                        "Lime-cement-fly ash", "2 and 3 with fiber (a)"],
        "restriction_ll_pi": "PI not to exceed 25",
        "restriction_pass_200": "3 & 4. Lime requires at least 25% passing the No. 200 (0.075 mm) sieve",
        "remark": "Soils near or above their optimum moisture content may require drying prior to "
                  "emulsion stabilization.",
    },
    "1b": {
        "uscs_classes": ["SW-SM", "SP-SW", "SW-SC", "SP-SC"],
        "stabilizers": ["Polymer/bituminous emulsion and cement", "Portland cement and fiber (a)",
                        "Lime and fiber (a)", "Lime-cement-fly ash and fiber (a)",
                        "2, 3, and 4 with fiber (a)"],
        "restriction_ll_pi": ("1. PI not to exceed 10\n2. PI not to exceed 30\n"
                               "3. PI not less than 12\n4. PI not to exceed 25"),
        "restriction_pass_200": "3, 4, 5. Lime requires at least 25% passing the No. 200 (0.075 mm) sieve",
        "remark": "Soils near or above their optimum moisture content may require drying prior to "
                  "emulsion stabilization.",
    },
    "1c": {
        "uscs_classes": ["SM", "SC", "SM-SC"],
        "stabilizers": ["Polymer/bituminous emulsion and cement", "Portland cement and fiber (a)",
                        "Lime and fiber (a)", "Lime-cement-fly ash and fiber (a)",
                        "2, 3, and 4 with fiber (a)"],
        "restriction_ll_pi": ("1. PI not to exceed 10\n2. (b)\n"
                               "3. PI not less than 12\n4. PI not to exceed 25"),
        "restriction_pass_200": ("1. Not to exceed 30% by weight\n"
                                  "3, 4, 5. Lime requires at least 25% passing the No. 200 (0.075 mm) sieve"),
        "remark": "Soils near or above their optimum moisture content may require drying prior to "
                  "emulsion stabilization.",
    },
    "2a": {
        "uscs_classes": ["GW", "GP"],
        "stabilizers": ["Polymer/bituminous emulsion and cement", "Portland cement and fiber (a)",
                        "Lime-cement-fly ash and fiber (a)", "2 and 3 with fiber (a)"],
        "restriction_ll_pi": "PI not to exceed 25",
        "restriction_pass_200": "3 & 4. Lime requires at least 25% passing the No. 200 (0.075 mm) sieve",
        "remark": "Well-graded material only. Material to contain at least 45% by weight of material "
                  "passing No. 4 (4.75 mm) sieve. Soils near or above their optimum moisture content "
                  "may require drying prior to emulsion stabilization.",
    },
    "2b": {
        "uscs_classes": ["GW-GM", "GP-GM", "GW-GC", "GP-GC"],
        "stabilizers": ["Polymer/bituminous emulsion and cement", "Portland cement and fiber (a)",
                        "Lime and fiber (a)", "Lime-cement-fly ash and fiber (a)",
                        "2, 3, and 4 with fiber (a)"],
        "restriction_ll_pi": ("1. PI not to exceed 10\n2. PI not to exceed 30\n"
                               "3. PI not less than 12\n4. PI not to exceed 25"),
        "restriction_pass_200": "3, 4, 5. Lime requires at least 25% passing the No. 200 (0.075 mm) sieve",
        "remark": "Well-graded material only. Material to contain at least 45% by weight of material "
                  "passing No. 4 (4.75 mm) sieve. Soils near or above their optimum moisture content "
                  "may require drying prior to emulsion stabilization.",
    },
    "2c": {
        "uscs_classes": ["GM", "GC", "GM-GC"],
        "stabilizers": ["Polymer/bituminous emulsion and cement", "Portland cement and fiber (a)",
                        "Lime and fiber (a)", "Lime-cement-fly ash and fiber (a)",
                        "2, 3, and 4 with fiber (a)"],
        "restriction_ll_pi": ("1. PI not to exceed 10\n2. (c)\n"
                               "3. PI not less than 12\n4. PI not to exceed 25"),
        "restriction_pass_200": ("1. Not to exceed 30% by weight\n"
                                  "3, 4, 5. Lime requires at least 25% passing the No. 200 (0.075 mm) sieve"),
        "remark": "Well-graded material only. Select Material to contain at least 45% by weight of "
                  "material passing No. 4 (4.75 mm) sieve.",
    },
    "3": {
        "uscs_classes": ["CH", "CL", "MH", "ML", "OH", "OL", "ML-CL"],
        "stabilizers": ["Portland cement and fiber (a)", "Lime (a)", "2 with fiber (a)"],
        "restriction_ll_pi": "1. LL less than 40 and PI less than 20\n2. PI not less than 12",
        "restriction_pass_200": "2 & 3. Lime requires at least 25% passing the No. 200 (0.075 mm) sieve",
        "remark": "Organic and strongly acidic soils falling within this area are not susceptible to "
                  "stabilization by conventional means.",
    },
}


def table_2_3_additive_selection_guide(area: str) -> dict:
    """Guide for selecting a stabilizing additive by gradation-triangle area (Table 2-3).

    The flagship stabilizer-selection table. Its ``area`` key comes from
    Figure 2-1 (a gradation triangle: entered with percent passing the
    No. 200 sieve and percent sand [material between No. 4 and No. 200]) --
    a chart read-off, not implemented numerically here (see
    ``figures_catalog.json`` / the ``read_reference_figure`` vision-tool
    convention). Worked example (Sec 2-1.5.2, printed p.9): SC soil, 25%
    passing No. 200, 68% sand -> area '1c'.

    Parameters
    ----------
    area : str
        '1a', '1b', '1c', '2a', '2b', '2c', or '3' (Figure 2-1 area).

    Returns
    -------
    dict
        {'area', 'uscs_classes', 'stabilizers' (numbered-list order matching
        the source), 'restriction_ll_pi' (raw text, numbered items align
        with 'stabilizers' list positions when multi-line), 'restriction_pass_200',
        'remark', 'footnotes' (dict of the (a)/(b)/(c) footnote texts
        referenced by this area), 'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If area is not recognized.
    """
    key = area.strip().lower().replace(" ", "").replace("-", "")
    if key not in _TABLE_2_3:
        raise ValueError(f"Unknown area '{area}'. Valid: {', '.join(sorted(_TABLE_2_3))}")
    row = _TABLE_2_3[key]
    return {
        "area": key,
        "uscs_classes": list(row["uscs_classes"]),
        "stabilizers": list(row["stabilizers"]),
        "restriction_ll_pi": row["restriction_ll_pi"],
        "restriction_pass_200": row["restriction_pass_200"],
        "remark": row["remark"],
        "footnotes": dict(_TABLE_2_3_FOOTNOTES),
        "reference": "UFC 3-250-11, Table 2-3, p.13",
        "pdf_page": 20,
    }


# ============================================================================
# Table 3-1: Gradation Requirements for Cement-Stabilized Base and Subbase
# Courses (printed p.15, pdf_page 22)
# ============================================================================

_TABLE_3_1 = {
    "base": {
        "1.5in": "100", "0.75in": "70-100", "no4": "45-70", "no40": "10-40", "no200": "0-20",
    },
    "subbase": {
        "1.5in": "100", "no4": "45-100", "no40": "10-50", "no200": "0-20",
    },
}

_TABLE_3_1_SIEVE_LABELS = {
    "1.5in": "1.5 inch (37.5 mm)", "0.75in": "0.75 inch (19 mm)",
    "no4": "No. 4 (4.75 mm)", "no40": "No. 40 (0.425 mm)", "no200": "No. 200 (0.075 mm)",
}


def table_3_1_cement_gradation(course_type: str, sieve: str = "") -> dict:
    """Gradation requirements for cement-stabilized base/subbase courses (Table 3-1).

    Parameters
    ----------
    course_type : str
        'base' or 'subbase'.
    sieve : str, optional
        '1.5in', '0.75in' (base only), 'no4', 'no40', or 'no200'. If empty,
        returns the full gradation envelope for the course type.

    Returns
    -------
    dict
        If sieve given: {'course_type', 'sieve', 'sieve_label',
        'percent_passing_range'}.
        If sieve omitted: {'course_type', 'gradation': {sieve: range, ...}}.

    Raises
    ------
    ValueError
        If course_type or sieve is not recognized.
    """
    ct = course_type.strip().lower()
    if ct not in _TABLE_3_1:
        raise ValueError(f"Unknown course_type '{course_type}'. Valid: base, subbase")
    row = _TABLE_3_1[ct]
    if not sieve:
        return {
            "course_type": ct, "gradation": dict(row),
            "reference": "UFC 3-250-11, Table 3-1, p.15", "pdf_page": 22,
        }
    key = sieve.strip().lower().replace(" ", "").replace(".", "").replace("inch", "in")
    key = key.replace("15in", "1.5in").replace("075in", "0.75in")
    if key not in row:
        raise ValueError(
            f"Unknown sieve '{sieve}' for course_type '{ct}'. Valid: {', '.join(row)}"
        )
    return {
        "course_type": ct, "sieve": key,
        "sieve_label": _TABLE_3_1_SIEVE_LABELS[key],
        "percent_passing_range": row[key],
        "reference": "UFC 3-250-11, Table 3-1, p.15", "pdf_page": 22,
    }


# ============================================================================
# Table 3-2: Cement Requirements for Various Soils (printed p.17, pdf_page 24)
# ============================================================================

_TABLE_3_2 = {
    "gw": 5, "sw": 5,
    "gp": 6, "gw-gc": 6, "gw-gm": 6, "sw-sc": 6, "sw-sm": 6,
    "gc": 7, "gm": 7, "gp-gc": 7, "gp-gm": 7, "gm-gc": 7, "sc": 7, "sm": 7,
    "sp-sc": 7, "sp-sm": 7, "sm-sc": 7, "sp": 7,
    "cl": 9, "ml": 9, "mh": 9,
    "ch": 11,
}


def table_3_2_cement_content_by_soil(uscs_class: str) -> dict:
    """Initial estimated cement content for moisture-density tests, by USCS class (Table 3-2).

    Used as the starting point (Step 2) of the cement-stabilized-soil design
    procedure (Sec 3-1.5); moisture-density tests are then also run at
    +/- 2 percent of this value (Step 3).

    Parameters
    ----------
    uscs_class : str
        USCS classification symbol, e.g. 'GW', 'SC', 'CH'. Valid: gw, sw,
        gp, gw-gc, gw-gm, sw-sc, sw-sm, gc, gm, gp-gc, gp-gm, gm-gc, sc, sm,
        sp-sc, sp-sm, sm-sc, sp, cl, ml, mh, ch.

    Returns
    -------
    dict
        {'uscs_class', 'initial_cement_content_pct', 'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If uscs_class is not recognized.
    """
    key = uscs_class.strip().lower()
    if key not in _TABLE_3_2:
        raise ValueError(f"Unknown uscs_class '{uscs_class}'. Valid: {', '.join(sorted(_TABLE_3_2))}")
    return {
        "uscs_class": key.upper(),
        "initial_cement_content_pct": _TABLE_3_2[key],
        "reference": "UFC 3-250-11, Table 3-2, p.17",
        "pdf_page": 24,
    }


# ============================================================================
# Table 3-3: Recommended Gradations for Bituminous-Stabilized Subgrade
# Materials (printed p.25, pdf_page 32)
# ============================================================================

_TABLE_3_3 = {
    "3in": "100", "no4": "50-100", "no30": "38-100", "no200": "2-30",
}

_TABLE_3_3_SIEVE_LABELS = {
    "3in": "3 inch (75 mm)", "no4": "No. 4 (4.75 mm)",
    "no30": "No. 30 (0.600 mm)", "no200": "No. 200 (0.075 mm)",
}


def table_3_3_bituminous_subgrade_gradation(sieve: str = "") -> dict:
    """Recommended gradations for bituminous-stabilized subgrade materials (Table 3-3).

    Parameters
    ----------
    sieve : str, optional
        '3in', 'no4', 'no30', or 'no200'. If empty, returns the full
        gradation envelope.

    Returns
    -------
    dict
        If sieve given: {'sieve', 'sieve_label', 'percent_passing_range'}.
        If sieve omitted: {'gradation': {sieve: range, ...}}.

    Raises
    ------
    ValueError
        If sieve is given but not recognized.
    """
    if not sieve:
        return {
            "gradation": dict(_TABLE_3_3),
            "reference": "UFC 3-250-11, Table 3-3, p.25", "pdf_page": 32,
        }
    key = sieve.strip().lower().replace(" ", "").replace("inch", "in")
    if key not in _TABLE_3_3:
        raise ValueError(f"Unknown sieve '{sieve}'. Valid: {', '.join(_TABLE_3_3)}")
    return {
        "sieve": key, "sieve_label": _TABLE_3_3_SIEVE_LABELS[key],
        "percent_passing_range": _TABLE_3_3[key],
        "reference": "UFC 3-250-11, Table 3-3, p.25", "pdf_page": 32,
    }


# ============================================================================
# Table 3-4: Recommended Gradations for Bituminous-Stabilized Base and
# Subbase Materials (printed p.25, pdf_page 32). Values are (nominal, +/-
# tolerance) percent passing; "100" = exactly 100; None = not applicable
# (max size smaller than this sieve).
# ============================================================================

_TABLE_3_4 = {
    "1.5in": {"1.5in": (100, 0), "1in": (84, 9), "0.75in": (76, 9), "0.5in": (66, 9),
              "3/8in": (59, 9), "no4": (45, 9), "no8": (35, 9), "no16": (27, 9),
              "no30": (20, 9), "no50": (14, 7), "no100": (9, 5), "no200": (5, 2)},
    "1in": {"1.5in": None, "1in": (100, 0), "0.75in": (83, 9), "0.5in": (73, 9),
            "3/8in": (64, 9), "no4": (48, 9), "no8": (36, 9), "no16": (28, 9),
            "no30": (21, 9), "no50": (16, 7), "no100": (11, 5), "no200": (5, 2)},
    "0.75in": {"1.5in": None, "1in": None, "0.75in": (100, 0), "0.5in": (82, 9),
               "3/8in": (72, 9), "no4": (54, 9), "no8": (41, 9), "no16": (32, 9),
               "no30": (24, 9), "no50": (17, 7), "no100": (12, 5), "no200": (5, 2)},
    "0.5in": {"1.5in": None, "1in": None, "0.75in": None, "0.5in": (100, 0),
              "3/8in": (83, 9), "no4": (62, 9), "no8": (47, 9), "no16": (36, 9),
              "no30": (28, 9), "no50": (20, 7), "no100": (14, 5), "no200": (5, 2)},
}

_SIEVE_ORDER = ["1.5in", "1in", "0.75in", "0.5in", "3/8in", "no4", "no8",
                "no16", "no30", "no50", "no100", "no200"]


def table_3_4_bituminous_base_subbase_gradation(max_size: str, sieve: str = "") -> dict:
    """Recommended gradations for bituminous-stabilized base/subbase materials (Table 3-4).

    Four gradation bands, keyed by nominal maximum aggregate size.

    Parameters
    ----------
    max_size : str
        '1.5in', '1in', '0.75in', or '0.5in' (nominal maximum aggregate
        size / column of Table 3-4).
    sieve : str, optional
        One of: 1.5in, 1in, 0.75in, 0.5in, 3/8in, no4, no8, no16, no30,
        no50, no100, no200. If empty, returns the full envelope for
        max_size.

    Returns
    -------
    dict
        If sieve given: {'max_size', 'sieve', 'percent_passing_nominal',
        'tolerance_pct', 'range' (string "nominal +/- tol" or "100" or
        "not applicable" if the sieve is coarser than max_size)}.
        If sieve omitted: {'max_size', 'gradation': {sieve: range_str, ...}}.

    Raises
    ------
    ValueError
        If max_size or sieve is not recognized.
    """
    ms = max_size.strip().lower().replace(" ", "").replace("inch", "in")
    if ms not in _TABLE_3_4:
        raise ValueError(f"Unknown max_size '{max_size}'. Valid: {', '.join(_TABLE_3_4)}")
    col = _TABLE_3_4[ms]

    def _fmt(v):
        if v is None:
            return "not applicable"
        nom, tol = v
        return f"{nom}" if tol == 0 else f"{nom} +/- {tol}"

    if not sieve:
        return {
            "max_size": ms,
            "gradation": {s: _fmt(col[s]) for s in _SIEVE_ORDER},
            "reference": "UFC 3-250-11, Table 3-4, p.25", "pdf_page": 32,
        }
    key = sieve.strip().lower().replace(" ", "").replace("inch", "in")
    if key not in col:
        raise ValueError(f"Unknown sieve '{sieve}'. Valid: {', '.join(_SIEVE_ORDER)}")
    val = col[key]
    return {
        "max_size": ms, "sieve": key,
        "percent_passing_nominal": None if val is None else val[0],
        "tolerance_pct": None if val is None else val[1],
        "range": _fmt(val),
        "reference": "UFC 3-250-11, Table 3-4, p.25", "pdf_page": 32,
    }


# ============================================================================
# Table 3-5: Emulsified Asphalt Requirements (printed p.27, pdf_page 34).
# lb of emulsified asphalt per 100 lb dry aggregate, by percent passing
# No. 200 sieve (row, interpolated) and percent passing No. 10 sieve
# (column, categorical: <50/60/70/80/90/100 -- no interpolation across
# columns since '<50' is an open-ended bin, not a numeric breakpoint).
# ============================================================================

_TABLE_3_5_ROWS_P200 = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25]
_TABLE_3_5_COLS = {
    "lt_50": [6.0, 6.3, 6.5, 6.7, 7.0, 7.2, 7.5, 7.2, 7.0, 6.7, 6.5, 6.3, 6.0, 6.2],
    "60": [6.3, 6.5, 6.7, 7.0, 7.2, 7.5, 7.7, 7.5, 7.2, 7.0, 6.7, 6.5, 6.3, 6.4],
    "70": [6.5, 6.7, 7.0, 7.2, 7.5, 7.7, 7.9, 7.7, 7.5, 7.2, 7.0, 6.7, 6.5, 6.6],
    "80": [6.7, 7.0, 7.2, 7.5, 7.7, 7.9, 8.2, 7.9, 7.7, 7.5, 7.2, 7.0, 6.7, 6.9],
    "90": [7.0, 7.2, 7.5, 7.7, 7.9, 8.2, 8.4, 8.2, 7.9, 7.7, 7.5, 7.2, 7.0, 7.1],
    "100": [7.2, 7.5, 7.7, 7.9, 8.2, 8.4, 8.6, 8.4, 8.2, 7.9, 7.6, 7.5, 7.2, 7.3],
}


def table_3_5_emulsified_asphalt_requirements(percent_passing_200: float, percent_passing_no10) -> dict:
    """Preliminary emulsified-asphalt content for subgrade stabilization (Table 3-5).

    lb (kg) of emulsified asphalt per 100 lb (45 kg) dry aggregate. Select
    the final design content from the Marshall Stability Test (Sec 3-4.4).

    Parameters
    ----------
    percent_passing_200 : float
        Percent of the aggregate passing the No. 200 (0.075 mm) sieve.
        Interpolated over the tabulated range 0-25%; clamped at endpoints.
    percent_passing_no10 : float or str
        Percent passing the No. 10 (2 mm) sieve. The table's column axis is
        categorical, not continuously interpolated: pass a numeric value
        < 50 (mapped to the '<50' column) or exactly one of 60, 70, 80, 90,
        100; or pass the string 'lt_50' directly.

    Returns
    -------
    dict
        {'percent_passing_200', 'percent_passing_no10_column',
         'emulsified_asphalt_lb_per_100lb', 'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If percent_passing_no10 is not < 50 or one of 60/70/80/90/100 (or
        'lt_50').
    """
    if isinstance(percent_passing_no10, str) and percent_passing_no10.strip().lower() in ("lt_50", "<50"):
        col_key = "lt_50"
    else:
        p10 = float(percent_passing_no10)
        if p10 < 50:
            col_key = "lt_50"
        elif p10 in (60, 70, 80, 90, 100):
            col_key = str(int(p10))
        else:
            raise ValueError(
                f"percent_passing_no10 must be < 50, or exactly one of 60, 70, 80, 90, 100 "
                f"(tabulated columns), got {percent_passing_no10}"
            )
    value = _linterp(percent_passing_200, _TABLE_3_5_ROWS_P200, _TABLE_3_5_COLS[col_key])
    return {
        "percent_passing_200": percent_passing_200,
        "percent_passing_no10_column": col_key,
        "emulsified_asphalt_lb_per_100lb": round(value, 3),
        "reference": "UFC 3-250-11, Table 3-5, p.27",
        "pdf_page": 34,
    }


# ============================================================================
# Table 3-6: Swell Potential of Soils (printed p.30, pdf_page 37)
# ============================================================================

_TABLE_3_6_LL_BANDS = [(60, "high"), (50, "marginal"), (0, "low")]  # LL lower bound -> category (high first)
_TABLE_3_6_PI_BANDS = [(35, "high"), (25, "marginal"), (0, "low")]
_TABLE_3_6_SEVERITY = {"low": 0, "marginal": 1, "high": 2}


def table_3_6_swell_potential(liquid_limit: float, plasticity_index: float) -> dict:
    """Swell potential of a soil from its Atterberg limits (Table 3-6).

    The source table lists LL and PI bands together (LL>60 & PI>35 -> High;
    LL 50-60 & PI 25-35 -> Marginal; LL<50 & PI<25 -> Low) without stating
    which criterion governs when they disagree. This function conservatively
    reports the MORE SEVERE of the two single-criterion categories (a
    standard interpretive convention for this kind of dual-criterion swell
    chart), plus both individual categories for transparency.

    Parameters
    ----------
    liquid_limit : float
        Liquid limit, percent.
    plasticity_index : float
        Plasticity index, percent.

    Returns
    -------
    dict
        {'liquid_limit', 'plasticity_index', 'll_category', 'pi_category',
         'potential_swell' (the more severe of the two), 'reference',
         'pdf_page'}.
    """
    # Bands are listed highest-severity-first, so the first band whose lower
    # bound is met by the input is the governing category for that criterion.
    ll_cat = next(cat for lo, cat in _TABLE_3_6_LL_BANDS if liquid_limit >= lo)
    pi_cat = next(cat for lo, cat in _TABLE_3_6_PI_BANDS if plasticity_index >= lo)
    governing = ll_cat if _TABLE_3_6_SEVERITY[ll_cat] >= _TABLE_3_6_SEVERITY[pi_cat] else pi_cat
    return {
        "liquid_limit": liquid_limit, "plasticity_index": plasticity_index,
        "ll_category": ll_cat, "pi_category": pi_cat,
        "potential_swell": governing,
        "reference": "UFC 3-250-11, Table 3-6, p.30",
        "pdf_page": 37,
    }


# ============================================================================
# Table A-1: Equivalency Factors for Stabilized Material (printed p.63,
# pdf_page 70). "Not used for base course material" (*) -> base=None.
# ============================================================================

_TABLE_A1 = {
    "asphalt": {
        "all_bituminous_concrete": {"base": 1.15, "subbase": 2.30},
        "gw_gp_gm_gc": {"base": 1.00, "subbase": 2.00},
        "sw_sp_sm_sc": {"base": None, "subbase": 1.50},
    },
    "cement": {
        "gw_gp_sw_sp": {"base": 1.15, "subbase": 2.30},
        "gm_gc": {"base": 1.00, "subbase": 2.00},
        "ml_mh_cl_ch": {"base": None, "subbase": 1.70},
        "sc_sm": {"base": None, "subbase": 1.50},
    },
    "lime": {
        "ml_mh_cl_ch": {"base": None, "subbase": 1.00},
        "sc_sm_gm_gc": {"base": None, "subbase": 1.10},
    },
    "lime_cement_fly_ash": {
        "ml_mh_cl_ch": {"base": None, "subbase": 1.30},
        "sc_sm_gm_gc": {"base": None, "subbase": 1.40},
    },
    "unbound": {
        "crushed_stone": {"base": 1.00, "subbase": 2.00},
        "aggregate": {"base": None, "subbase": 1.00},
    },
}

# Map an individual USCS class (or special key) to its Table A-1 soil_group,
# per stabilizer_type (a class can fall in a different group depending on
# which stabilizer is being used, matching the source table's row grouping).
_A1_CLASS_MAP = {
    "asphalt": {
        "all_bituminous_concrete": "all_bituminous_concrete", "abc": "all_bituminous_concrete",
        "gw": "gw_gp_gm_gc", "gp": "gw_gp_gm_gc", "gm": "gw_gp_gm_gc", "gc": "gw_gp_gm_gc",
        "sw": "sw_sp_sm_sc", "sp": "sw_sp_sm_sc", "sm": "sw_sp_sm_sc", "sc": "sw_sp_sm_sc",
    },
    "cement": {
        "gw": "gw_gp_sw_sp", "gp": "gw_gp_sw_sp", "sw": "gw_gp_sw_sp", "sp": "gw_gp_sw_sp",
        "gm": "gm_gc", "gc": "gm_gc",
        "ml": "ml_mh_cl_ch", "mh": "ml_mh_cl_ch", "cl": "ml_mh_cl_ch", "ch": "ml_mh_cl_ch",
        "sc": "sc_sm", "sm": "sc_sm",
    },
    "lime": {
        "ml": "ml_mh_cl_ch", "mh": "ml_mh_cl_ch", "cl": "ml_mh_cl_ch", "ch": "ml_mh_cl_ch",
        "sc": "sc_sm_gm_gc", "sm": "sc_sm_gm_gc", "gm": "sc_sm_gm_gc", "gc": "sc_sm_gm_gc",
    },
    "unbound": {
        "crushed_stone": "crushed_stone", "aggregate": "aggregate",
    },
}
_A1_CLASS_MAP["lime_cement_fly_ash"] = dict(_A1_CLASS_MAP["lime"])


def table_a1_equivalency_factors(stabilizer_type: str, soil_class: str) -> dict:
    """Equivalency factors for stabilized material thickness design (Table A-1).

    An equivalency factor is the number of inches of a CONVENTIONAL base or
    subbase that can be replaced by 1 inch of stabilized material
    (equivalent_thickness = conventional_thickness / EF; see
    ``equations.equation_stabilized_equivalent_thickness``). Limit cement
    content to 4% by weight or less to prevent excessive reflective cracking
    when applying these factors (Sec A-1.1).

    Hand-verified against Appendix A's two printed worked examples: Example
    1 (cement-stabilized GP soil, base) -> EF=1.15; Example 2
    (all-bituminous-concrete, base and subbase) -> EF=1.15 (base),
    2.30 (subbase).

    Parameters
    ----------
    stabilizer_type : str
        'asphalt', 'cement', 'lime', 'lime_cement_fly_ash', or 'unbound'.
    soil_class : str
        A USCS class (e.g. 'GP', 'SC') appropriate to stabilizer_type, or
        'all_bituminous_concrete' (asphalt only), or 'crushed_stone' /
        'aggregate' (unbound only).

    Returns
    -------
    dict
        {'stabilizer_type', 'soil_class', 'soil_group', 'base_factor'
         (None if "(*) Not used for base course material"), 'subbase_factor',
         'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If stabilizer_type or soil_class is not recognized for that type.
    """
    st = stabilizer_type.strip().lower().replace(" ", "_").replace("-", "_")
    if st not in _TABLE_A1:
        raise ValueError(f"Unknown stabilizer_type '{stabilizer_type}'. Valid: {', '.join(_TABLE_A1)}")
    sc_key = soil_class.strip().lower().replace(" ", "_").replace("-", "_")
    class_map = _A1_CLASS_MAP[st]
    if sc_key not in class_map:
        raise ValueError(
            f"Unknown soil_class '{soil_class}' for stabilizer_type '{st}'. "
            f"Valid: {', '.join(sorted(class_map))}"
        )
    group = class_map[sc_key]
    row = _TABLE_A1[st][group]
    return {
        "stabilizer_type": st, "soil_class": sc_key.upper(), "soil_group": group,
        "base_factor": row["base"], "subbase_factor": row["subbase"],
        "reference": "UFC 3-250-11, Table A-1, p.63",
        "pdf_page": 70,
    }
