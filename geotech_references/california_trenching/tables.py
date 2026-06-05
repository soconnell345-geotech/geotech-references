"""California Trenching and Shoring Manual (Caltrans) table lookups.

Geotech / excavation-engineering tables and design values from the Caltrans
Trenching and Shoring Manual (June 2011, Revision 2 - July 2025). All values are
in the manual's native US customary units (psf, pcf, tsf, degrees); they are NOT
converted to SI. Each function cites the source table and PDF page.

PDF pages below are 0-based fitz page indices into
``docs/California Trenching and Shoring Manual.pdf``; the printed manual page
(e.g. "3-5") is also given.
"""

# ============================================================================
# Cal/OSHA soil classification — Chapter 2, Section 2-3.03
# (PDF p.30-31, printed 2-9..2-10)
#
# Cal/OSHA CSO 1541.1 App A classifies soils as Stable Rock, Type A, B, or C,
# keyed on cohesion / unconfined compressive strength (qu, tsf).
# ============================================================================

_OSHA_SOIL_TYPES = {
    "stable_rock": {
        "type": "Stable Rock",
        "qu_min_tsf": None,
        "qu_max_tsf": None,
        "description": (
            "Natural solid mineral matter that can be excavated with vertical "
            "sides and remain intact while exposed."
        ),
    },
    "a": {
        "type": "A",
        "qu_min_tsf": 1.5,
        "qu_max_tsf": None,
        "description": (
            "Cohesive soil with unconfined compressive strength of 1.5 tsf or "
            "greater (e.g. clay, silty clay, sandy clay, clay loam, caliche, "
            "hardpan). NOT Type A if fissured, subject to vibration/dynamic "
            "loads, previously disturbed, part of a sloped layered system "
            "dipping into the excavation at 4H:1V or steeper, or otherwise "
            "precluded."
        ),
    },
    "b": {
        "type": "B",
        "qu_min_tsf": 0.5,
        "qu_max_tsf": 1.5,
        "description": (
            "Cohesive soil with unconfined compressive strength > 0.5 tsf but "
            "< 1.5 tsf; OR granular cohesionless soils (angular gravel, silt, "
            "silty/sandy loam); OR previously disturbed soils not Type C; OR "
            "soil meeting Type A but fissured or subject to vibration; OR "
            "unstable dry rock."
        ),
    },
    "c": {
        "type": "C",
        "qu_min_tsf": 0.0,
        "qu_max_tsf": 0.5,
        "description": (
            "Cohesive soil with unconfined compressive strength of 0.5 tsf or "
            "less; OR granular soil (gravel, sand, loamy sand); OR submerged "
            "soil or soil from which water is freely seeping; OR submerged "
            "unstable rock; OR material sloped toward the excavation at 4H:1V "
            "or steeper in a layered system."
        ),
    },
}


def osha_soil_classification() -> dict:
    """Return the full Cal/OSHA Type A/B/C soil classification (Section 2-3.03).

    Cal/OSHA CSO 1541.1, Appendix A classifies soils for protective-system
    selection as Stable Rock or Type A, B, or C, keyed on cohesion / unconfined
    compressive strength qu (tsf).

    Returns
    -------
    dict
        {'reference', 'section', 'pdf_page', 'printed_page', 'types': {...}}
    """
    return {
        "reference": "Caltrans T&S Manual Section 2-3.03 / Cal/OSHA CSO 1541.1 App A",
        "section": "2-3.03",
        "pdf_page": 30,
        "printed_page": "2-9",
        "types": {k: dict(v) for k, v in _OSHA_SOIL_TYPES.items()},
    }


def osha_soil_type_from_qu(qu_tsf, cohesive: bool = True) -> dict:
    """Classify a cohesive soil into Cal/OSHA Type A/B/C from qu (Section 2-3.03).

    For COHESIVE soils the Cal/OSHA type is set by the unconfined compressive
    strength qu (tsf): Type A >= 1.5; Type B 0.5 to 1.5; Type C <= 0.5. (Granular
    cohesionless soils are at most Type B and are usually Type C regardless of
    qu — see ``osha_soil_classification`` for the full granular rules.)

    Parameters
    ----------
    qu_tsf : float
        Unconfined compressive strength in tons per square foot (tsf).
    cohesive : bool, optional
        True (default) for cohesive soil (qu governs the type). If False, a note
        is added that granular soils are classified by the granular rules
        (Type B or C) rather than by qu.

    Returns
    -------
    dict
        {'qu_tsf', 'osha_type', 'description', 'boundary', 'reference', ...}

    Raises
    ------
    ValueError
        If qu_tsf is negative.
    """
    if qu_tsf < 0:
        raise ValueError(f"qu_tsf must be >= 0, got {qu_tsf}")
    if qu_tsf >= 1.5:
        t, boundary = "a", "qu >= 1.5 tsf"
    elif qu_tsf > 0.5:
        t, boundary = "b", "0.5 tsf < qu < 1.5 tsf"
    else:
        t, boundary = "c", "qu <= 0.5 tsf"
    info = _OSHA_SOIL_TYPES[t]
    note = (
        "qu governs the type for cohesive soils." if cohesive else
        "For granular cohesionless soils the Cal/OSHA type is set by the "
        "granular rules (at most Type B, usually Type C) rather than by qu; "
        "this qu-based result applies to cohesive soils."
    )
    return {
        "qu_tsf": qu_tsf,
        "osha_type": info["type"],
        "description": info["description"],
        "boundary": boundary,
        "cohesive": cohesive,
        "reference": "Caltrans T&S Manual Section 2-3.03 / Cal/OSHA CSO 1541.1 App A",
        "pdf_page": 30,
        "printed_page": "2-9",
        "note": note,
    }


# ============================================================================
# Table 2-1: Maximum allowable temporary slopes (H:V) for excavations < 20 ft
# (Ch 2, Section 2-3.04; PDF p.32, printed 2-11)
#
# Cal/OSHA CSO 1541.1 App B, Table B-1.
# ============================================================================

# (soil_type_key, label, H:V ratio as H per 1 V, descriptive ratio string)
_TABLE_2_1 = [
    ("stable_rock", "Stable Rock", 0.0, "Vertical"),
    ("a", "Type A", 0.75, "3/4:1"),
    ("b", "Type B", 1.0, "1:1"),
    ("c", "Type C", 1.5, "1-1/2:1"),
]


def table_2_1_max_allowable_slope(soil_type: str = "") -> dict:
    """Maximum allowable temporary slope (H:V) by soil type (Table 2-1).

    Cal/OSHA maximum allowable slopes for excavations less than 20 ft deep
    (CSO 1541.1 Appendix B, Table B-1): Stable Rock = vertical; Type A = 3/4:1;
    Type B = 1:1; Type C = 1-1/2:1 (H:V, horizontal run per unit vertical rise).

    Parameters
    ----------
    soil_type : str, optional
        '', 'stable_rock', 'A', 'B', or 'C'. Empty (default) returns the whole
        table.

    Returns
    -------
    dict
        For a specific type: {'soil_type', 'ratio_h_per_v', 'ratio_label',
        'slope_angle_deg', 'reference', ...}. For '' : {'table': [...]}.

    Raises
    ------
    ValueError
        If soil_type is unrecognized.
    """
    import math
    key = str(soil_type).strip().lower().replace(" ", "_").replace("type_", "")
    rows = []
    for skey, label, hv, ratio in _TABLE_2_1:
        angle = 90.0 if hv == 0.0 else round(math.degrees(math.atan2(1.0, hv)), 1)
        rows.append({
            "soil_type": label,
            "ratio_h_per_v": hv,
            "ratio_label": ratio,
            "slope_angle_deg": angle,
            "_key": skey,
        })
    if key in ("", "all"):
        return {
            "reference": "Caltrans T&S Manual Table 2-1 / Cal/OSHA CSO 1541.1 App B Table B-1",
            "table": "2-1",
            "pdf_page": 32,
            "printed_page": "2-11",
            "applicability": "Maximum allowable slope for excavations less than 20 ft deep",
            "rows": [{k: v for k, v in r.items() if k != "_key"} for r in rows],
        }
    if key in ("stable_rock", "rock", "stablerock"):
        key = "stable_rock"
    match = next((r for r in rows if r["_key"] == key), None)
    if match is None:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. Use '', 'stable_rock', 'A', 'B', or 'C'."
        )
    out = {k: v for k, v in match.items() if k != "_key"}
    out.update({
        "reference": "Caltrans T&S Manual Table 2-1 / Cal/OSHA CSO 1541.1 App B Table B-1",
        "table": "2-1",
        "pdf_page": 32,
        "printed_page": "2-11",
    })
    return out


# OSHA timber-shoring effective lateral pressure PA = m*H + 72 (2-ft surcharge)
# (Ch 2, Section 2-3.03; PDF p.31, printed 2-10)
_OSHA_PA_SLOPE = {"a": 25.0, "b": 45.0, "c": 80.0}  # psf per ft of depth


def osha_timber_shoring_pressure(soil_type: str, depth_ft) -> dict:
    """Cal/OSHA timber-shoring effective lateral pressure PA (Section 2-3.03).

    The Cal/OSHA CSO timber-shoring tables use the effective lateral pressure

        Type A:  PA = 25*H + 72 psf
        Type B:  PA = 45*H + 72 psf
        Type C:  PA = 80*H + 72 psf

    where H is depth (ft) and 72 psf is the equivalent of a 2-ft surcharge.

    Parameters
    ----------
    soil_type : str
        'A', 'B', or 'C' (Cal/OSHA soil type).
    depth_ft : float
        Depth H below the top of the retained soil (ft).

    Returns
    -------
    dict
        {'soil_type', 'depth_ft', 'slope_psf_per_ft', 'surcharge_psf',
         'pa_psf', 'reference', ...}

    Raises
    ------
    ValueError
        If soil_type is not A/B/C or depth_ft is negative.
    """
    key = str(soil_type).strip().lower().replace("type", "").strip()
    if key not in _OSHA_PA_SLOPE:
        raise ValueError(f"soil_type must be 'A', 'B', or 'C', got '{soil_type}'.")
    if depth_ft < 0:
        raise ValueError(f"depth_ft must be >= 0, got {depth_ft}")
    m = _OSHA_PA_SLOPE[key]
    return {
        "soil_type": key.upper(),
        "depth_ft": depth_ft,
        "slope_psf_per_ft": m,
        "surcharge_psf": 72.0,
        "pa_psf": round(m * depth_ft + 72.0, 2),
        "reference": "Caltrans T&S Manual Section 2-3.03 (Cal/OSHA timber-shoring tables)",
        "pdf_page": 31,
        "printed_page": "2-10",
        "note": "72 psf accounts for a 2-ft surcharge; for trenches <= 20 ft deep.",
    }


# ============================================================================
# Table 3-1: Properties of Granular Soils  (Ch 3; PDF p.42, printed 3-5)
# Apparent density vs SPT N60, friction angle, and unit weight.
# ============================================================================

# (density, rel_density_pct, n60_label, phi_min, phi_max, gamma_moist, gamma_sub)
_TABLE_3_1 = [
    ("Very Loose", "0-15", "N60 < 5", None, 28, None, None, None, 100, None, 60),
    ("Loose", "16-35", "5 <= N60 < 10", 28, 30, 95, 125, 55, 65, None, None),
    ("Medium Dense", "36-65", "10 <= N60 < 30", 31, 36, 110, 130, 60, 70, None, None),
    ("Dense", "66-85", "30 <= N60 < 50", 37, 41, 110, 140, 65, 85, None, None),
    ("Very Dense", "86-100", "N60 >= 50", 41, None, 130, None, 75, None, None, None),
]


def table_3_1_granular_properties(density: str = "") -> dict:
    """Properties of granular soils vs SPT N60 (Table 3-1).

    Empirical apparent density, relative density (%), SPT N60 range, friction
    angle phi (deg), and unit weight (pcf, moist and submerged) for granular
    soils. Use to estimate basic granular-soil parameters for shoring design.

    Parameters
    ----------
    density : str, optional
        '', 'very loose', 'loose', 'medium dense', 'dense', or 'very dense'.
        Empty (default) returns the whole table.

    Returns
    -------
    dict
        Full table or the matched density row, with friction-angle and unit-
        weight ranges and the source citation.

    Raises
    ------
    ValueError
        If density is unrecognized.
    """
    rows = []
    for (d, rd, n60, pmin, pmax, gm_lo, gm_hi, gs_lo, gs_hi, gm_one, gs_one) in _TABLE_3_1:
        rows.append({
            "apparent_density": d,
            "relative_density_pct": rd,
            "spt_n60": n60,
            "friction_angle_min_deg": pmin,
            "friction_angle_max_deg": pmax,
            "unit_weight_moist_pcf_min": gm_lo if gm_lo is not None else gm_one,
            "unit_weight_moist_pcf_max": gm_hi,
            "unit_weight_submerged_pcf_min": gs_lo if gs_lo is not None else gs_one,
            "unit_weight_submerged_pcf_max": gs_hi,
        })
    key = str(density).strip().lower()
    if key in ("", "all"):
        return {
            "reference": "Caltrans T&S Manual Table 3-1",
            "table": "3-1",
            "pdf_page": 42,
            "printed_page": "3-5",
            "rows": rows,
            "note": (
                "Table is keyed on N60 (energy-corrected SPT). LOTB/boring "
                "records report the field N value, not N60."
            ),
        }
    match = next((r for r in rows if r["apparent_density"].lower() == key), None)
    if match is None:
        raise ValueError(
            f"Unknown density '{density}'. Use 'very loose', 'loose', "
            "'medium dense', 'dense', or 'very dense'."
        )
    out = dict(match)
    out.update({"reference": "Caltrans T&S Manual Table 3-1", "table": "3-1",
                "pdf_page": 42, "printed_page": "3-5"})
    return out


# ============================================================================
# Table 3-2: Simplified Typical Soil Values  (Ch 3; PDF p.43, printed 3-6)
# Friction angle, unit weight, Ka, and equivalent fluid weight Kw = Ka*gamma.
# ============================================================================

# soil_class -> list of (consistency, phi_deg, gamma_pcf, ka, kw_pcf)
_TABLE_3_2 = {
    "gravel, gravel-sand mixture, coarse sand": [
        ("Dense", 41, 130, 0.21, 27),
        ("Medium Dense", 34, 120, 0.28, 34),
        ("Loose", 29, 90, 0.35, 32),
    ],
    "medium sand": [
        ("Dense", 36, 117, 0.26, 30),
        ("Medium Dense", 31, 110, 0.32, 35),
        ("Loose", 27, 90, 0.38, 34),
    ],
    "fine sand": [
        ("Dense", 31, 117, 0.32, 37),
        ("Medium Dense", 27, 100, 0.38, 38),
        ("Loose", 25, 85, 0.41, 34),
    ],
    "fine silty sand, sandy silt": [
        ("Dense", 29, 117, 0.35, 41),
        ("Medium Dense", 27, 100, 0.38, 38),
        ("Loose", 25, 85, 0.41, 34),
    ],
    "silt": [
        ("Dense", 27, 120, 0.38, 45),
        ("Medium Dense", 25, 110, 0.41, 45),
        ("Loose", 23, 85, 0.44, 37),
    ],
}

_TABLE_3_2_ALIASES = {
    "gravel": "gravel, gravel-sand mixture, coarse sand",
    "coarse sand": "gravel, gravel-sand mixture, coarse sand",
    "gravel-sand": "gravel, gravel-sand mixture, coarse sand",
    "medium sand": "medium sand",
    "fine sand": "fine sand",
    "silty sand": "fine silty sand, sandy silt",
    "sandy silt": "fine silty sand, sandy silt",
    "fine silty sand": "fine silty sand, sandy silt",
    "silt": "silt",
}


def table_3_2_simplified_soil_values(soil_class: str = "",
                                     density: str = "") -> dict:
    """Simplified typical soil values incl. Ka and equivalent fluid weight (Table 3-2).

    Caltrans Geotechnical Services "simplified typical soil values" for average
    trench conditions: friction angle phi (deg), unit weight gamma (pcf), active
    earth pressure coefficient Ka, and equivalent fluid weight Kw = Ka*gamma
    (pcf, also called EFP), keyed on soil class and density/consistency.

    Parameters
    ----------
    soil_class : str, optional
        '', 'gravel'/'coarse sand', 'medium sand', 'fine sand',
        'silty sand'/'sandy silt', or 'silt'. Empty returns the whole table.
    density : str, optional
        '', 'dense', 'medium dense', or 'loose'. Filters to one row when both
        soil_class and density are given.

    Returns
    -------
    dict
        Full table or a filtered set of rows.

    Raises
    ------
    ValueError
        If soil_class or density is unrecognized.

    Notes
    -----
    For active-pressure design use gamma = 115 pcf minimum when soils data is
    insufficient (per the table's footnote).
    """
    def _rows(cls):
        return [
            {"soil_class": cls, "density": c, "friction_angle_deg": phi,
             "unit_weight_pcf": g, "ka": ka, "equivalent_fluid_weight_pcf": kw}
            for (c, phi, g, ka, kw) in _TABLE_3_2[cls]
        ]

    cls_key = str(soil_class).strip().lower()
    den_key = str(density).strip().lower()

    if cls_key in ("", "all"):
        all_rows = []
        for cls in _TABLE_3_2:
            all_rows.extend(_rows(cls))
        return {
            "reference": "Caltrans T&S Manual Table 3-2",
            "table": "3-2", "pdf_page": 43, "printed_page": "3-6",
            "rows": all_rows,
            "note": "For active pressure use gamma >= 115 pcf when data is insufficient.",
        }

    cls = _TABLE_3_2_ALIASES.get(cls_key)
    if cls is None:
        raise ValueError(
            f"Unknown soil_class '{soil_class}'. Use 'gravel', 'medium sand', "
            "'fine sand', 'silty sand', or 'silt'."
        )
    rows = _rows(cls)
    if den_key not in ("", "all"):
        rows = [r for r in rows if r["density"].lower() == den_key]
        if not rows:
            raise ValueError(
                f"Unknown density '{density}'. Use 'dense', 'medium dense', or 'loose'."
            )
    return {
        "reference": "Caltrans T&S Manual Table 3-2",
        "table": "3-2", "pdf_page": 43, "printed_page": "3-6",
        "rows": rows,
    }


# ============================================================================
# Table 3-3: Simplified Typical Properties of Cohesive Soils
# (Ch 3; PDF p.44, printed 3-7)
# Consistency vs unconfined compressive strength (psf) and moist unit weight.
# ============================================================================

# (consistency, qu_min_psf, qu_max_psf, gamma_min_pcf, gamma_max_pcf)
_TABLE_3_3 = [
    ("Very Soft", 0, 500, None, 110),
    ("Soft", 500, 1000, 100, 120),
    ("Medium Stiff", 1000, 2000, 110, 125),
    ("Stiff", 2000, 4000, 115, 130),
    ("Very Stiff", 4000, 8000, 120, 140),
    ("Hard", 8000, None, 132, None),
]


def table_3_3_cohesive_properties(consistency: str = "") -> dict:
    """Simplified typical properties of cohesive soils (Table 3-3).

    Cohesive-soil consistency vs unconfined compressive strength qu (psf) and
    moist unit weight (pcf): Very Soft (0-500), Soft (500-1,000), Medium Stiff
    (1,000-2,000), Stiff (2,000-4,000), Very Stiff (4,000-8,000), Hard (>8,000).

    Parameters
    ----------
    consistency : str, optional
        '', 'very soft', 'soft', 'medium stiff', 'stiff', 'very stiff', or
        'hard'. Empty (default) returns the whole table.

    Returns
    -------
    dict
        Full table or the matched consistency row.

    Raises
    ------
    ValueError
        If consistency is unrecognized.
    """
    rows = [
        {"consistency": c, "unconfined_compressive_strength_psf_min": qmin,
         "unconfined_compressive_strength_psf_max": qmax,
         "moist_unit_weight_pcf_min": gmin, "moist_unit_weight_pcf_max": gmax}
        for (c, qmin, qmax, gmin, gmax) in _TABLE_3_3
    ]
    key = str(consistency).strip().lower()
    if key in ("", "all"):
        return {
            "reference": "Caltrans T&S Manual Table 3-3",
            "table": "3-3", "pdf_page": 44, "printed_page": "3-7",
            "rows": rows,
            "note": "Undrained shear strength su = qu / 2 (when phi_u = 0).",
        }
    match = next((r for r in rows if r["consistency"].lower() == key), None)
    if match is None:
        raise ValueError(
            f"Unknown consistency '{consistency}'. Use 'very soft', 'soft', "
            "'medium stiff', 'stiff', 'very stiff', or 'hard'."
        )
    out = dict(match)
    out.update({"reference": "Caltrans T&S Manual Table 3-3", "table": "3-3",
                "pdf_page": 44, "printed_page": "3-7"})
    return out


# ============================================================================
# Table 3-4: Field and Laboratory Test Reliability  (Ch 3; PDF p.46, printed 3-9)
# ============================================================================

_TABLE_3_4 = [
    ("Standard Penetration Test (SPT)", "ASTM D1586", "Good", "Poor"),
    ("Cone Penetration Test (CPT)", "ASTM D3441", "Good", "Fair"),
    ("Pocket Penetrometer", "", "Not applicable", "Fair"),
    ("Torvane (shearvane)", "", "Not applicable", "Fair"),
    ("Vane Shear", "ASTM D2573", "Not applicable", "Very good"),
    ("Triaxial Compression (UU, CU)", "ASTM D2850", "Very good*", "Very good"),
    ("Unconfined Compression", "ASTM D2166", "Not applicable", "Very good"),
    ("Direct Shear", "ASTM D3080", "Good*", "Fair"),
]


def table_3_4_test_reliability() -> dict:
    """Field/laboratory test reliability for soil shear strength (Table 3-4).

    Reliability rating of each test method for measuring/estimating shear
    strength in coarse-grained vs fine-grained soils.

    Returns
    -------
    dict
        {'reference', 'table', 'pdf_page', 'printed_page', 'rows': [...]}
    """
    rows = [
        {"test_method": t, "astm": astm,
         "coarse_grained": coarse, "fine_grained": fine}
        for (t, astm, coarse, fine) in _TABLE_3_4
    ]
    return {
        "reference": "Caltrans T&S Manual Table 3-4",
        "table": "3-4", "pdf_page": 46, "printed_page": "3-9",
        "rows": rows,
        "note": "* Recovery of undisturbed samples can be difficult.",
    }


# ============================================================================
# Table 4-1: Mobilized Wall Movements (Clough 1991)  (Ch 4; PDF p.54, printed 4-4)
# Delta/H to reach minimum active or maximum passive pressure.
# ============================================================================

# (backfill, active_ratio, passive_ratio)
_TABLE_4_1 = [
    ("Dense Sand", 0.001, 0.01),
    ("Medium Dense Sand", 0.002, 0.02),
    ("Loose Sand", 0.004, 0.04),
    ("Compacted Silt", 0.002, 0.02),
    ("Compacted Lean Clay", 0.01, 0.05),
    ("Compacted Fat Clay", 0.01, 0.05),
]


def table_4_1_mobilized_wall_movements(backfill: str = "") -> dict:
    """Mobilized wall movements delta/H for active/passive pressure (Table 4-1).

    Typical wall-top movement (delta/H, by tilting or translation) required to
    reach the minimum active or maximum passive earth pressure, by backfill type
    (Clough 1991). Note far more movement is needed to mobilize full passive
    pressure than active.

    Parameters
    ----------
    backfill : str, optional
        '', 'dense sand', 'medium dense sand', 'loose sand', 'compacted silt',
        'compacted lean clay', or 'compacted fat clay'. Empty returns the table.

    Returns
    -------
    dict
        Full table or the matched backfill row.

    Raises
    ------
    ValueError
        If backfill is unrecognized.
    """
    rows = [
        {"backfill": b, "active_delta_over_h": a, "passive_delta_over_h": p}
        for (b, a, p) in _TABLE_4_1
    ]
    key = str(backfill).strip().lower()
    if key in ("", "all"):
        return {
            "reference": "Caltrans T&S Manual Table 4-1 (Clough 1991)",
            "table": "4-1", "pdf_page": 54, "printed_page": "4-4",
            "rows": rows,
        }
    match = next((r for r in rows if r["backfill"].lower() == key), None)
    if match is None:
        raise ValueError(
            f"Unknown backfill '{backfill}'. Use 'dense sand', 'medium dense "
            "sand', 'loose sand', 'compacted silt', 'compacted lean clay', or "
            "'compacted fat clay'."
        )
    out = dict(match)
    out.update({"reference": "Caltrans T&S Manual Table 4-1 (Clough 1991)",
                "table": "4-1", "pdf_page": 54, "printed_page": "4-4"})
    return out


# ============================================================================
# Table 4-2: Wall Friction angle delta  (Ch 4; PDF p.65, printed 4-15)
# Reprint of AASHTO LRFD BDS Table C3.11.5.3-1.
# ============================================================================

# group -> list of (interface, delta_min_deg, delta_max_deg)
_TABLE_4_2 = {
    "mass concrete": [
        ("Clean sound rock", 35, 35),
        ("Clean gravel, gravel-sand mixtures, coarse sand", 29, 31),
        ("Clean fine to medium sand, silty medium to coarse sand, silty or clayey gravel", 24, 29),
        ("Clean fine sand, silty or clayey fine to medium sand", 19, 24),
        ("Fine sandy silt, nonplastic silt", 17, 19),
        ("Very stiff and hard residual or preconsolidated clay", 22, 26),
        ("Medium stiff and stiff clay and silty clay", 17, 19),
    ],
    "steel sheet piles": [
        ("Clean gravel, gravel-sand mixtures, well-graded rock fill with spalls", 22, 22),
        ("Clean sand, silty sand-gravel mixture, single-size hard rock fill", 17, 17),
        ("Silty sand, gravel or sand mixed with silt or clay", 14, 14),
        ("Fine sandy silt, nonplastic silt", 11, 11),
    ],
    "formed or precast concrete": [
        ("Clean gravel, gravel-sand mixture, well-graded rock fill with spalls", 22, 26),
        ("Clean sand, silty sand-gravel mixture, single-size hard rock fill", 17, 22),
        ("Silty sand, gravel or sand mixed with silt or clay", 17, 17),
        ("Fine sandy silt, nonplastic silt", 14, 14),
    ],
}


def table_4_2_wall_friction(interface_material: str = "") -> dict:
    """Wall friction angle delta for dissimilar materials (Table 4-2).

    Ultimate wall friction angle delta (deg) between common wall materials
    (mass concrete, steel sheet piles, formed/precast concrete) and foundation
    soils/rock. Reprint of AASHTO LRFD BDS Table C3.11.5.3-1.

    Parameters
    ----------
    interface_material : str, optional
        '', 'mass concrete', 'steel sheet piles', or 'formed or precast
        concrete'. Empty (default) returns all groups.

    Returns
    -------
    dict
        Full table or the matched material group's rows.

    Raises
    ------
    ValueError
        If interface_material is unrecognized.
    """
    key = str(interface_material).strip().lower()
    aliases = {
        "concrete": "mass concrete", "mass concrete": "mass concrete",
        "steel": "steel sheet piles", "steel sheet piles": "steel sheet piles",
        "sheet pile": "steel sheet piles",
        "precast": "formed or precast concrete",
        "formed or precast concrete": "formed or precast concrete",
        "precast concrete": "formed or precast concrete",
    }
    if key in ("", "all"):
        groups = {
            g: [{"interface": i, "delta_min_deg": d0, "delta_max_deg": d1}
                for (i, d0, d1) in rows]
            for g, rows in _TABLE_4_2.items()
        }
        return {
            "reference": "Caltrans T&S Manual Table 4-2 (AASHTO LRFD BDS Table C3.11.5.3-1)",
            "table": "4-2", "pdf_page": 65, "printed_page": "4-15",
            "groups": groups,
        }
    grp = aliases.get(key)
    if grp is None:
        raise ValueError(
            f"Unknown interface_material '{interface_material}'. Use 'mass "
            "concrete', 'steel sheet piles', or 'formed or precast concrete'."
        )
    rows = [{"interface": i, "delta_min_deg": d0, "delta_max_deg": d1}
            for (i, d0, d1) in _TABLE_4_2[grp]]
    return {
        "reference": "Caltrans T&S Manual Table 4-2 (AASHTO LRFD BDS Table C3.11.5.3-1)",
        "table": "4-2", "pdf_page": 65, "printed_page": "4-15",
        "interface_group": grp, "rows": rows,
    }


# ============================================================================
# Fig 4-20 (Caquot & Kerisel 1948) log-spiral passive Kp wall-friction
# reduction factor R (Matrix 4-1)  (Ch 4-6; PDF p.79, printed 4-29)
#
# R = Kp(delta)/Kp(delta=phi), tabulated by phi and the ratio delta/phi.
# Only the three columns printed in Matrix 4-1 are quoted exactly.
# ============================================================================

# phi_deg -> {delta_over_phi: R}
_MATRIX_4_1_R = {
    30: {0.5: 0.746, 0.44: 0.710, 0.4: 0.686},
    32: {0.5: 0.717, 0.44: 0.679, 0.4: 0.653},
    35: {0.5: 0.674, 0.44: 0.631, 0.4: 0.603},
}


def matrix_4_1_passive_reduction_factor(phi_deg, delta_over_phi) -> dict:
    """Log-spiral passive Kp wall-friction reduction factor R (Matrix 4-1).

    From the Caquot & Kerisel (1948) passive earth pressure chart (Figure 4-20),
    the final passive coefficient is Kp_prime = R * Kp, where Kp is the initial
    (delta = phi) value read from the chart and R reduces it for the actual wall
    friction ratio delta/phi. This returns the exact R values printed in Matrix
    4-1 (the chart's upper-left interpolation table); only phi = 30/32/35 deg and
    delta/phi = 0.4/0.44/0.5 are tabulated there.

    Parameters
    ----------
    phi_deg : float
        Soil friction angle phi (deg). Tabulated values: 30, 32, 35.
    delta_over_phi : float
        Wall friction ratio delta/phi. Tabulated values: 0.4, 0.44, 0.5.

    Returns
    -------
    dict
        {'phi_deg', 'delta_over_phi', 'R', 'reference', ...}

    Raises
    ------
    ValueError
        If (phi_deg, delta_over_phi) is not an exact tabulated entry. For other
        values read Figure 4-20 directly (use figure_db / read_reference_figure).
    """
    phi_key = int(round(phi_deg))
    if phi_key not in _MATRIX_4_1_R:
        raise ValueError(
            f"phi_deg={phi_deg} not in Matrix 4-1 (tabulated: 30, 32, 35). "
            "Read Figure 4-20 directly for other phi."
        )
    row = _MATRIX_4_1_R[phi_key]
    match = next((v for k, v in row.items()
                  if abs(k - float(delta_over_phi)) < 1e-6), None)
    if match is None:
        raise ValueError(
            f"delta_over_phi={delta_over_phi} not in Matrix 4-1 (tabulated: "
            "0.4, 0.44, 0.5). Read Figure 4-20 directly for other ratios."
        )
    return {
        "phi_deg": phi_key,
        "delta_over_phi": float(delta_over_phi),
        "R": match,
        "reference": "Caltrans T&S Manual Matrix 4-1 / Figure 4-20 (Caquot & Kerisel 1948)",
        "pdf_page": 79, "printed_page": "4-29",
        "note": "Kp_prime = R * Kp(initial, read from Figure 4-20).",
    }


# ============================================================================
# Chapter 6 — structural design constants  (PDF p.98, p.100; printed 6-4, 6-6)
# ============================================================================

def overstress_factor() -> dict:
    """Short-term allowable-stress increase (overstress) factor (Section 6-4).

    Short-term increases to allowable stresses are permitted up to 133% (a 1.33
    factor) EXCEPT when: (1) the excavation is in place > 90 days, (2) dynamic
    loadings are present (pile driving, traffic), (3) the excavation is adjacent
    to railroads, or (4) analyzing horizontal struts.

    Returns
    -------
    dict
        {'overstress_factor', 'overstress_percent', 'exceptions', 'reference', ...}
    """
    return {
        "overstress_factor": 1.33,
        "overstress_percent": 133,
        "exceptions": [
            "Excavation in place more than 90 days",
            "Dynamic loadings present (pile driving, traffic, etc.)",
            "Excavation adjacent to railroads",
            "Analyzing horizontal struts",
        ],
        "reference": "Caltrans T&S Manual Section 6-4",
        "pdf_page": 98, "printed_page": "6-4",
    }


def lagging_design_load(earth_pressure_psf, surcharge_present: bool = False) -> dict:
    """Lagging design load with soil arching reduction (Section 6-5).

    Because of soil arching behind the lagging, the lagging design load may be
    taken as 0.6 times the theoretical/calculated earth pressure. When no
    surcharge is present the lagging load may be capped at 400 psf. Without soil
    arching (e.g. adjacent to existing facilities/railroads), the reduction
    does not apply.

    Parameters
    ----------
    earth_pressure_psf : float
        Theoretical/calculated earth pressure on the lagging (psf).
    surcharge_present : bool, optional
        If False (default) and no surcharge is present, the 400 psf cap applies.
        If True, analyze the surcharge separately (cap not applied here).

    Returns
    -------
    dict
        {'earth_pressure_psf', 'arching_factor', 'lagging_load_psf',
         'cap_applied', 'reference', ...}

    Raises
    ------
    ValueError
        If earth_pressure_psf is negative.
    """
    if earth_pressure_psf < 0:
        raise ValueError(f"earth_pressure_psf must be >= 0, got {earth_pressure_psf}")
    load = 0.6 * earth_pressure_psf
    cap_applied = False
    if not surcharge_present and load > 400.0:
        load = 400.0
        cap_applied = True
    return {
        "earth_pressure_psf": earth_pressure_psf,
        "arching_factor": 0.6,
        "lagging_load_psf": round(load, 2),
        "cap_psf": 400.0,
        "cap_applied": cap_applied,
        "surcharge_present": surcharge_present,
        "reference": "Caltrans T&S Manual Section 6-5",
        "pdf_page": 100, "printed_page": "6-6",
        "note": ("Reduction applies only where soil arching develops; not for "
                 "excavations adjacent to existing facilities/railroads."),
    }


# ============================================================================
# Chapter 7 — effective pile width / arching  (PDF p.110; printed 7-4)
# ============================================================================

def effective_pile_width_arching(effective_width_ft, phi_deg=None,
                                 cohesive: bool = False,
                                 arching_factor_cohesive=None,
                                 pile_spacing_ft=None) -> dict:
    """Adjusted soldier-pile width from soil arching for passive resistance (Section 7-2).

    Soil arching between soldier piles increases the effective width available
    for passive resistance below the excavation. For granular soils the arching
    factor f = 0.08*phi, capped at 3 (i.e. up to 3x the effective width). For
    cohesive soils the arching capability ranges 1 to 2 (read from Figure 7-4,
    supplied via ``arching_factor_cohesive``). The adjusted pile width is limited
    to the actual pile spacing.

    Parameters
    ----------
    effective_width_ft : float
        Effective pile width d (ft): the pile dimension parallel to the wall
        (driven/gravel-backfilled), or the drilled-hole diameter for 4-sack+
        concrete below the excavation line.
    phi_deg : float, optional
        Soil friction angle phi (deg) for granular soils. Required if
        cohesive=False.
    cohesive : bool, optional
        If True, use the cohesive arching factor (1 to 2) instead of 0.08*phi.
    arching_factor_cohesive : float, optional
        Cohesive arching factor (1 to 2), read from Figure 7-4. Required if
        cohesive=True.
    pile_spacing_ft : float, optional
        Actual pile spacing (ft). Caps the adjusted width if provided.

    Returns
    -------
    dict
        {'effective_width_ft', 'arching_factor', 'adjusted_width_ft',
         'limited_by_spacing', 'reference', ...}

    Raises
    ------
    ValueError
        If required inputs are missing or invalid.
    """
    if effective_width_ft <= 0:
        raise ValueError(f"effective_width_ft must be > 0, got {effective_width_ft}")
    if cohesive:
        if arching_factor_cohesive is None:
            raise ValueError(
                "arching_factor_cohesive (1 to 2, from Figure 7-4) is required "
                "for cohesive soils."
            )
        f = float(arching_factor_cohesive)
        if not (1.0 <= f <= 2.0):
            raise ValueError("Cohesive arching factor must be between 1 and 2.")
        basis = "cohesive (Figure 7-4, 1 to 2)"
    else:
        if phi_deg is None:
            raise ValueError("phi_deg is required for granular soils (f = 0.08*phi).")
        f = min(0.08 * float(phi_deg), 3.0)
        basis = "granular (f = 0.08*phi, capped at 3)"
    adjusted = effective_width_ft * f
    limited = False
    if pile_spacing_ft is not None and adjusted > pile_spacing_ft:
        adjusted = float(pile_spacing_ft)
        limited = True
    return {
        "effective_width_ft": effective_width_ft,
        "arching_factor": round(f, 4),
        "arching_basis": basis,
        "adjusted_width_ft": round(adjusted, 4),
        "limited_by_spacing": limited,
        "pile_spacing_ft": pile_spacing_ft,
        "reference": "Caltrans T&S Manual Section 7-2",
        "pdf_page": 110, "printed_page": "7-4",
        "note": ("Adjusted width is used for PASSIVE resistance below the "
                 "excavation only; active loads behind the pile use the "
                 "effective width (arching factor = 1). Adjusted width <= pile "
                 "spacing."),
    }


# ============================================================================
# Factor-of-safety / design-value summary  (cross-chapter)
# ============================================================================

_FS_REQUIREMENTS = [
    {"item": "Anchored/braced wall embedment depth", "fs": 1.3,
     "basis": "External stability; take moments about the anchor (Section 8-4)."},
    {"item": "Anchored wall — ground anchor load T", "fs": 1.0,
     "basis": "Embedment with FS=1.0 to back-calculate the anchor force (Section 8-4)."},
    {"item": "Bottom heave (braced cut in clay)", "fs": 1.5,
     "basis": "FS = Qu/Q minimum recommended (Section 10-3.01)."},
    {"item": "Anchor block (deadman) capacity", "fs": 1.5,
     "basis": "Typical minimum FS on ultimate anchor-block resistance (Section 10-2)."},
    {"item": "Cantilever (unrestrained) embedment", "fs": None,
     "basis": ("D = 1.2*D0 — the 20% increase on the point-of-rotation depth D0 "
               "is NOT a factor of safety; it accounts for rotation below point O "
               "(Section 7-5).")},
]


def factor_of_safety_requirements() -> dict:
    """Summary of factor-of-safety and key embedment requirements across the manual.

    Collects the design FS / embedment rules an engineer needs for a shoring
    review: anchored-wall embedment (FS = 1.3) and anchor-load (FS = 1.0)
    moment calculations (Ch 8), bottom-heave FS (>= 1.5, Ch 10-3), anchor-block
    FS, and the cantilever embedment rule D = 1.2*D0 (the 20% increase that is
    explicitly NOT a factor of safety, Ch 7-5).

    Returns
    -------
    dict
        {'reference', 'requirements': [{item, fs, basis}, ...]}
    """
    return {
        "reference": "Caltrans T&S Manual (Chapters 7, 8, 10)",
        "requirements": [dict(r) for r in _FS_REQUIREMENTS],
    }
