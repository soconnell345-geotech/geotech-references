"""FHWA-NHI-05-037 "Geotechnical Aspects of Pavements" table lookups.

Soil/geotech-input tables from FHWA-NHI-05-037 (FHWA, May 2006): resilient
modulus (Mr) default values and correlations, typical CBR by soil class, soil
suitability as a pavement material, drainage coefficients and permeability,
frost-susceptibility classification, swell potential, and compaction
characteristics. Each function cites the source table and the PDF page.

UNITS: values are kept in the source's primary units — Mr in psi, CBR and
R-value in percent, unit weight in pcf, permeability in cm/s or m/s as printed.
SI equivalents from the source (1 psi = 6.9 kPa) are noted, not applied.

PDF pages below are 0-based fitz page indices into
``docs/FHWA-NHI-05-037 - Geotech Pavements.pdf``; the printed manual page
(e.g. "5-54") is also given.
"""


# ============================================================================
# Table 5-35: Default MR values for unbound granular and subgrade materials at
# unsoaked optimum moisture content and density (NCHRP 1-37A, 2004).
# (Chapter 5; PDF p.231, printed 5-54)
#
# Mr range and typical value (psi) keyed on AASHTO and USCS soil class.
# Multiply by 0.069 to convert to MPa.
# ============================================================================

# AASHTO class -> (mr_min_psi, mr_max_psi, mr_typical_psi)
_TABLE_5_35_AASHTO = {
    "A-1-a": (38500, 42000, 40000),
    "A-1-b": (35500, 40000, 38000),
    "A-2-4": (28000, 37500, 32000),
    "A-2-5": (24000, 33000, 28000),
    "A-2-6": (21500, 31000, 26000),
    "A-2-7": (21500, 28000, 24000),
    "A-3": (24500, 35500, 29000),
    "A-4": (21500, 29000, 24000),
    "A-5": (17000, 25500, 20000),
    "A-6": (13500, 24000, 17000),
    "A-7-5": (8000, 17500, 12000),
    "A-7-6": (5000, 13500, 8000),
}

# USCS class -> (mr_min_psi, mr_max_psi, mr_typical_psi)
_TABLE_5_35_USCS = {
    "GW": (39500, 42000, 41000),
    "GP": (35500, 40000, 38000),
    "GM": (33000, 42000, 38500),
    "GC": (24000, 37500, 31000),
    "GW-GM": (35500, 40500, 38500),
    "GP-GM": (31000, 40000, 36000),
    "GW-GC": (28000, 40000, 34500),
    "GP-GC": (28000, 39000, 34000),
    "SW": (28000, 37500, 32000),
    "SP": (24000, 33000, 28000),
    "SM": (28000, 37500, 32000),
    "SC": (21500, 28000, 24000),
    "SW-SM": (24000, 33000, 28000),
    "SP-SM": (24000, 33000, 28000),
    "SW-SC": (21500, 31000, 25500),
    "SP-SC": (21500, 31000, 25500),
    "ML": (17000, 25500, 20000),
    "CL": (13500, 24000, 17000),
    "MH": (8000, 17500, 11500),
    "CH": (5000, 13500, 8000),
}


def table_5_35_default_resilient_modulus(soil_class: str = "",
                                         classification: str = "") -> dict:
    """Default resilient modulus Mr by AASHTO/USCS soil class (Table 5-35).

    NCHRP 1-37A (Level 3) default Mr ranges and typical values (psi) for unbound
    granular base/subbase and subgrade materials, at unsoaked optimum moisture
    content and density. Keyed on AASHTO soil class (A-1-a .. A-7-6) or USCS soil
    class (GW .. CH). Multiply psi by 0.069 to obtain MPa.

    Parameters
    ----------
    soil_class : str, optional
        A specific class, e.g. 'A-2-4', 'A-7-6', 'GW', 'CL', 'CH'. Empty
        (default) returns the whole table for the requested classification
        system (or both).
    classification : str, optional
        '', 'aashto', or 'uscs'. When ``soil_class`` is empty this selects which
        system's full table to return ('' returns both). When ``soil_class`` is
        given it is auto-detected and this is ignored.

    Returns
    -------
    dict
        For a specific class: {'soil_class', 'classification', 'mr_min_psi',
        'mr_max_psi', 'mr_typical_psi', 'reference', ...}. Otherwise the table(s).

    Raises
    ------
    ValueError
        If soil_class or classification is unrecognized.
    """
    def _row(system, cls, vals):
        lo, hi, typ = vals
        return {
            "classification": system, "soil_class": cls,
            "mr_min_psi": lo, "mr_max_psi": hi, "mr_typical_psi": typ,
        }

    sc_raw = str(soil_class).strip()
    sc = sc_raw.upper()
    sys_key = str(classification).strip().lower()
    # Case-insensitive resolution to the canonical AASHTO/USCS keys (AASHTO keys
    # carry a lowercase suffix, e.g. 'A-1-a', so an upper() match would miss).
    _aashto_ci = {k.upper(): k for k in _TABLE_5_35_AASHTO}
    _uscs_ci = {k.upper(): k for k in _TABLE_5_35_USCS}

    if sc in ("", "ALL"):
        out = {
            "reference": "FHWA-NHI-05-037 Table 5-35 (NCHRP 1-37A, 2004)",
            "table": "5-35", "pdf_page": 231, "printed_page": "5-54",
            "note": ("Mr in psi at unsoaked optimum moisture/density "
                     "(NCHRP 1-37A Level 3 defaults). Multiply by 0.069 for MPa."),
        }
        if sys_key in ("", "all", "aashto"):
            out["aashto_rows"] = [_row("AASHTO", k, v)
                                  for k, v in _TABLE_5_35_AASHTO.items()]
        if sys_key in ("", "all", "uscs"):
            out["uscs_rows"] = [_row("USCS", k, v)
                                for k, v in _TABLE_5_35_USCS.items()]
        if sys_key not in ("", "all", "aashto", "uscs"):
            raise ValueError(
                f"Unknown classification '{classification}'. Use 'aashto' or 'uscs'."
            )
        return out

    if sc in _aashto_ci:
        key = _aashto_ci[sc]
        row = _row("AASHTO", key, _TABLE_5_35_AASHTO[key])
    elif sc in _uscs_ci:
        key = _uscs_ci[sc]
        row = _row("USCS", key, _TABLE_5_35_USCS[key])
    else:
        raise ValueError(
            f"Unknown soil_class '{soil_class}'. AASHTO A-1-a..A-7-6 or "
            "USCS GW..CH (see table for the full list)."
        )
    row.update({
        "reference": "FHWA-NHI-05-037 Table 5-35 (NCHRP 1-37A, 2004)",
        "table": "5-35", "pdf_page": 231, "printed_page": "5-54",
        "note": "Mr in psi at unsoaked optimum moisture/density. x0.069 -> MPa.",
    })
    return row


# ============================================================================
# Table 5-34: Correlations between resilient modulus and material strength/index
# properties (NCHRP 1-37A, 2004).  (Chapter 5; PDF p.230, printed 5-53)
# ============================================================================

# key -> (label, model_psi, model_si, comments, test_standard)
_TABLE_5_34 = {
    "cbr": (
        "California Bearing Ratio",
        "MR (psi) = 2555 * CBR^0.64",
        "MR (MPa) = 17.6 * CBR^0.64",
        "CBR = California Bearing Ratio (%). NCHRP 1-37A's most-preferred Mr "
        "correlation (longest history, most supporting data).",
        "AASHTO T193",
    ),
    "r_value": (
        "Stabilometer R-value",
        "MR (psi) = 1155 + 555 * R",
        "MR (MPa) = 8.0 + 3.8 * R",
        "R = R-value.",
        "AASHTO T190",
    ),
    "layer_coefficient": (
        "AASHTO layer coefficient",
        "MR (psi) = 30000 * (ai/0.14)^3",
        "MR (MPa) = 207 * (ai/0.14)^3",
        "ai = AASHTO structural layer coefficient.",
        "AASHTO Guide for the Design of Pavement Structures (1993)",
    ),
    "plasticity_gradation": (
        "Plasticity index and gradation",
        "CBR = 75 / (1 + 0.728 * wPI)  [then use the CBR->Mr model]",
        "CBR = 75 / (1 + 0.728 * wPI)",
        "wPI = P200 * PI, where P200 = % passing the No. 200 sieve (as a "
        "decimal) and PI = plasticity index (%).",
        "AASHTO T27 / AASHTO T90",
    ),
    "dcp": (
        "Dynamic Cone Penetration",
        "CBR = 292 / DCP^1.12  [then use the CBR->Mr model]",
        "CBR = 292 / DCP^1.12",
        "DCP = penetration index (in./blow). Estimates of CBR are used to "
        "estimate Mr.",
        "ASTM D6951",
    ),
}


def table_5_34_resilient_modulus_correlations(property: str = "") -> dict:
    """Resilient modulus Mr correlations with strength/index properties (Table 5-34).

    NCHRP 1-37A (Level 2) correlation models for estimating Mr from CBR,
    Stabilometer R-value, AASHTO layer coefficient, plasticity index + gradation,
    or the Dynamic Cone Penetrometer. The CBR correlation is the most preferred.
    Use ``resilient_modulus_from_cbr`` / ``..._from_r_value`` for the numeric
    evaluation.

    Parameters
    ----------
    property : str, optional
        '', 'cbr', 'r_value', 'layer_coefficient', 'plasticity_gradation', or
        'dcp'. Empty (default) returns all correlations.

    Returns
    -------
    dict
        Full table or the matched correlation row (model in psi and SI, comments,
        and test standard).

    Raises
    ------
    ValueError
        If property is unrecognized.
    """
    def _row(key):
        label, mpsi, msi, comments, std = _TABLE_5_34[key]
        return {"property": key, "label": label, "model_psi": mpsi,
                "model_si": msi, "comments": comments, "test_standard": std}

    aliases = {
        "cbr": "cbr", "california bearing ratio": "cbr",
        "r": "r_value", "r-value": "r_value", "r_value": "r_value",
        "rvalue": "r_value", "stabilometer": "r_value",
        "layer coefficient": "layer_coefficient",
        "layer_coefficient": "layer_coefficient", "ai": "layer_coefficient",
        "pi": "plasticity_gradation", "plasticity": "plasticity_gradation",
        "plasticity_gradation": "plasticity_gradation",
        "gradation": "plasticity_gradation", "wpi": "plasticity_gradation",
        "dcp": "dcp", "dynamic cone": "dcp", "dynamic_cone": "dcp",
    }
    key = str(property).strip().lower()
    if key in ("", "all"):
        return {
            "reference": "FHWA-NHI-05-037 Table 5-34 (NCHRP 1-37A, 2004)",
            "table": "5-34", "pdf_page": 230, "printed_page": "5-53",
            "rows": [_row(k) for k in _TABLE_5_34],
            "note": ("Correlations are in rough order of preference; Mr-from-CBR "
                     "is most preferred. NCHRP 1-37A recommends AGAINST the older "
                     "Heukelom & Klomp (1962) Mr = 1500*CBR form (Eq. 5.13)."),
        }
    mapped = aliases.get(key)
    if mapped is None:
        raise ValueError(
            f"Unknown property '{property}'. Use 'cbr', 'r_value', "
            "'layer_coefficient', 'plasticity_gradation', or 'dcp'."
        )
    out = _row(mapped)
    out.update({"reference": "FHWA-NHI-05-037 Table 5-34 (NCHRP 1-37A, 2004)",
                "table": "5-34", "pdf_page": 230, "printed_page": "5-53"})
    return out


# ============================================================================
# Table 5-28: Typical field CBR values by USCS soil class
# (after U.S. Army Corps of Engineers, 1953).  (Chapter 5; PDF p.215, printed 5-39)
# ============================================================================

# uscs_class -> (cbr_min, cbr_max)
_TABLE_5_28 = {
    "GW": (60, 80),
    "GP": (35, 60),
    "GM": (40, 80),
    "GC": (20, 40),
    "SW": (20, 40),
    "SP": (15, 25),
    "SM": (20, 40),
    "SC": (10, 20),
    "ML": (5, 15),
    "CL": (5, 15),
    "OL": (4, 8),
    "MH": (4, 8),
    "CH": (3, 5),
    "OH": (3, 5),
}


def table_5_28_typical_cbr(soil_class: str = "") -> dict:
    """Typical field CBR values by USCS soil class (Table 5-28).

    Typical field California Bearing Ratio (CBR, %) ranges by USCS soil class
    (after U.S. Army Corps of Engineers, 1953). For reference, the AASHO Road
    Test granular base had CBR ~ 100 and the granular subbase ~ 30.

    Parameters
    ----------
    soil_class : str, optional
        '', or a USCS class: 'GW','GP','GM','GC','SW','SP','SM','SC','ML','CL',
        'OL','MH','CH','OH'. Empty (default) returns the whole table.

    Returns
    -------
    dict
        For a specific class: {'soil_class', 'cbr_min', 'cbr_max', ...}. For '':
        {'rows': [...]}.

    Raises
    ------
    ValueError
        If soil_class is unrecognized.
    """
    sc = str(soil_class).strip().upper()
    rows = [{"soil_class": k, "cbr_min": lo, "cbr_max": hi}
            for k, (lo, hi) in _TABLE_5_28.items()]
    if sc in ("", "ALL"):
        return {
            "reference": "FHWA-NHI-05-037 Table 5-28 (USACE, 1953)",
            "table": "5-28", "pdf_page": 215, "printed_page": "5-39",
            "rows": rows,
            "note": "Field CBR (%). AASHO Road Test: base CBR ~ 100, subbase ~ 30.",
        }
    if sc not in _TABLE_5_28:
        raise ValueError(
            f"Unknown soil_class '{soil_class}'. Use a USCS class such as 'GW', "
            "'SC', 'CL', or 'CH'."
        )
    lo, hi = _TABLE_5_28[sc]
    return {
        "soil_class": sc, "cbr_min": lo, "cbr_max": hi,
        "reference": "FHWA-NHI-05-037 Table 5-28 (USACE, 1953)",
        "table": "5-28", "pdf_page": 215, "printed_page": "5-39",
    }


# ============================================================================
# Table 4-14: Summary of soil characteristics as a pavement material
# (from NCHRP 1-37A).  (Chapter 4; PDF p.166, printed 4-65)
#
# Subgrade strength, potential frost action, compressibility/expansion, and
# drainage by USCS soil class (gravels and sands only in the printed table).
# ============================================================================

# uscs_class -> (name, subgrade_strength, frost_action, compressibility, drainage)
_TABLE_4_14 = {
    "GW": ("Well-graded gravels or gravel-sand mixtures, little or no fines",
           "Excellent", "None to very slight", "Almost none", "Excellent"),
    "GP": ("Poorly graded gravels or gravel-sand mixtures, little or no fines",
           "Good to excellent", "None to very slight", "Almost none", "Excellent"),
    "GM": ("Silty gravels, gravel-sand-silt mixtures",
           "Good to excellent", "Slight to medium", "Very slight",
           "Fair to poor"),
    "GC": ("Clayey gravels, gravel-sand-clay mixtures",
           "Good", "Slight to medium", "Slight",
           "Poor to practically impervious"),
    "SW": ("Well-graded sands or gravelly sands, little or no fines",
           "Good", "None to very slight", "Almost none", "Excellent"),
    "SP": ("Poorly graded sands or gravelly sands, little or no fines",
           "Fair to good", "None to very slight", "Almost none", "Excellent"),
    "SM": ("Silty sands, sand-silt mixtures",
           "Fair to good", "Slight to high", "Very slight", "Fair to poor"),
    "SC": ("Clayey sands, sand-clay mixtures",
           "Poor to fair", "Slight to high", "Slight to medium",
           "Poor to practically impervious"),
}


def table_4_14_soil_as_pavement_material(soil_class: str = "") -> dict:
    """Soil characteristics as a pavement material by USCS class (Table 4-14).

    Summary of subgrade strength (when not subject to frost action), potential
    frost action, compressibility & expansion, and drainage characteristics by
    USCS soil class (gravels and sands; from NCHRP 1-37A). Use to judge a soil's
    suitability as subgrade/subbase.

    Parameters
    ----------
    soil_class : str, optional
        '', or a USCS class: 'GW','GP','GM','GC','SW','SP','SM','SC'. Empty
        (default) returns the whole table.

    Returns
    -------
    dict
        For a specific class: {'soil_class','name','subgrade_strength',
        'potential_frost_action','compressibility_expansion','drainage', ...}.
        For '': {'rows': [...]}.

    Raises
    ------
    ValueError
        If soil_class is unrecognized.
    """
    def _row(cls):
        name, strength, frost, comp, drain = _TABLE_4_14[cls]
        return {"soil_class": cls, "name": name,
                "subgrade_strength": strength,
                "potential_frost_action": frost,
                "compressibility_expansion": comp, "drainage": drain}

    sc = str(soil_class).strip().upper()
    if sc in ("", "ALL"):
        return {
            "reference": "FHWA-NHI-05-037 Table 4-14 (NCHRP 1-37A)",
            "table": "4-14", "pdf_page": 166, "printed_page": "4-65",
            "rows": [_row(k) for k in _TABLE_4_14],
            "note": ("Subgrade strength is for soils NOT subject to frost action. "
                     "Printed table covers gravels (G*) and sands (S*) only."),
        }
    if sc not in _TABLE_4_14:
        raise ValueError(
            f"Unknown soil_class '{soil_class}'. Use a USCS gravel/sand class: "
            "'GW','GP','GM','GC','SW','SP','SM','SC'."
        )
    out = _row(sc)
    out.update({"reference": "FHWA-NHI-05-037 Table 4-14 (NCHRP 1-37A)",
                "table": "4-14", "pdf_page": 166, "printed_page": "4-65"})
    return out


# ============================================================================
# Table 7-12: Frost susceptibility classification of soils (NCHRP 1-37A).
# (Chapter 7; PDF p.411, printed 7-60)
# ============================================================================

# (frost_group, degree, soil_type, percent_finer_0p075mm, typical_classification)
_TABLE_7_12 = [
    ("F1", "Negligible to low", "Gravelly soils", "3-10",
     "GC, GP, GC-GM, GP-GM"),
    ("F1", "Negligible to low", "Gravelly soils", "10-20",
     "GM, GC-GM, GP-GM"),
    ("F2", "Low to medium", "Sands", "3-15",
     "SW, SP, SM, SW-SM, SP-SM"),
    ("F2", "Low to medium", "Gravelly soils", "Greater than 20", "GM-GC"),
    ("F2", "Low to medium", "Sands, except very fine silty sands",
     "Greater than 15", "SM, SC"),
    ("F3", "High", "Clays, PI > 12", "", "CL, CH"),
    ("F3", "High", "All silts", "", "ML-MH"),
    ("F3", "High", "Very fine silty sands", "Greater than 15", "SM"),
    ("F3", "High", "Clays, PI < 12", "", "CL, CL-ML"),
    ("F4", "Very high",
     "Varved clays and other fine-grained, banded sediments", "",
     "CL, ML, SM, CH"),
]


def table_7_12_frost_susceptibility(frost_group: str = "") -> dict:
    """Frost susceptibility classification of soils, F1-F4 (Table 7-12).

    NCHRP 1-37A frost-susceptibility groups F1 (negligible to low) through F4
    (very high), keyed on soil type, percentage finer than 0.075 mm (No. 200),
    and typical USCS classification. F4 (varved/banded fine-grained sediments) is
    the most frost-susceptible.

    Parameters
    ----------
    frost_group : str, optional
        '', 'F1', 'F2', 'F3', or 'F4'. Empty (default) returns the whole table.

    Returns
    -------
    dict
        For a specific group: {'frost_group', 'degree', 'entries': [...], ...}.
        For '': {'rows': [...]}.

    Raises
    ------
    ValueError
        If frost_group is unrecognized.
    """
    def _row(t):
        fg, deg, soil, finer, cls = t
        return {"frost_group": fg, "degree_of_frost_susceptibility": deg,
                "type_of_soil": soil, "percent_finer_0p075mm": finer,
                "typical_classification": cls}

    fg = str(frost_group).strip().upper().replace(" ", "")
    rows = [_row(t) for t in _TABLE_7_12]
    if fg in ("", "ALL"):
        return {
            "reference": "FHWA-NHI-05-037 Table 7-12 (NCHRP 1-37A)",
            "table": "7-12", "pdf_page": 411, "printed_page": "7-60",
            "rows": rows,
            "note": ("Increasing frost susceptibility F1 < F2 < F3 < F4. The "
                     "USACE uses a >= 3% finer-than-0.02 mm threshold for a frost-"
                     "susceptible soil (see chapter text)."),
        }
    if fg not in {"F1", "F2", "F3", "F4"}:
        raise ValueError(
            f"Unknown frost_group '{frost_group}'. Use 'F1', 'F2', 'F3', or 'F4'."
        )
    entries = [r for r in rows if r["frost_group"] == fg]
    return {
        "frost_group": fg,
        "degree_of_frost_susceptibility": entries[0]["degree_of_frost_susceptibility"],
        "entries": entries,
        "reference": "FHWA-NHI-05-037 Table 7-12 (NCHRP 1-37A)",
        "table": "7-12", "pdf_page": 411, "printed_page": "7-60",
    }


# ============================================================================
# Table 5-49 / 5-50: AASHTO 1993 drainage modifier mi (flexible) and drainage
# coefficient Cd (rigid).  (Chapter 5; PDF p.264, printed 5-87)
#
# Keyed on quality of drainage and the % of time the pavement is near saturation.
# ============================================================================

# Saturation columns shared by both tables.
_DRAINAGE_COLS = ["<1%", "1-5%", "5-25%", ">25%"]

# quality -> (water_removed_within, [vals for each saturation column])
_TABLE_5_49_MI = {
    "excellent": ("2 hours", ["1.40-1.35", "1.35-1.30", "1.30-1.20", "1.20"]),
    "good": ("1 day", ["1.35-1.25", "1.25-1.15", "1.15-1.00", "1.00"]),
    "fair": ("1 week", ["1.25-1.15", "1.15-1.05", "1.00-0.80", "0.80"]),
    "poor": ("1 month", ["1.05-0.80", "1.05-0.80", "0.80-0.60", "0.60"]),
    "very poor": ("no drainage", ["0.95-0.75", "0.95-0.75", "0.75-0.40", "0.40"]),
}

_TABLE_5_50_CD = {
    "excellent": ("2 hours", ["1.25-1.20", "1.20-1.15", "1.15-1.10", "1.10"]),
    "good": ("1 day", ["1.20-1.15", "1.15-1.10", "1.10-1.00", "1.00"]),
    "fair": ("1 week", ["1.15-1.10", "1.10-1.00", "1.00-0.90", "0.90"]),
    "poor": ("1 month", ["1.10-1.00", "1.00-0.90", "0.90-0.80", "0.80"]),
    "very poor": ("no drainage", ["1.00-0.90", "0.90-0.80", "0.80-0.70", "0.70"]),
}


def _drainage_lookup(data, quality, table_no, coeff_key, label):
    def _row(q):
        within, vals = data[q]
        return {"quality_of_drainage": q.title(),
                "water_removed_within": within,
                coeff_key: dict(zip(_DRAINAGE_COLS, vals))}

    qk = str(quality).strip().lower()
    if qk in ("", "all"):
        return {
            "reference": f"FHWA-NHI-05-037 Table {table_no} (AASHTO, 1993)",
            "table": table_no, "pdf_page": 264, "printed_page": "5-87",
            "saturation_columns": list(_DRAINAGE_COLS),
            "rows": [_row(q) for q in data],
            "note": (f"{label}. Columns are the % of time the pavement structure "
                     "is exposed to moisture levels approaching saturation."),
        }
    if qk not in data:
        raise ValueError(
            f"Unknown quality '{quality}'. Use 'excellent', 'good', 'fair', "
            "'poor', or 'very poor'."
        )
    out = _row(qk)
    out.update({"reference": f"FHWA-NHI-05-037 Table {table_no} (AASHTO, 1993)",
                "table": table_no, "pdf_page": 264, "printed_page": "5-87",
                "saturation_columns": list(_DRAINAGE_COLS)})
    return out


def table_5_49_drainage_modifier_mi(quality: str = "") -> dict:
    """AASHTO 1993 drainage modifier mi for FLEXIBLE pavements (Table 5-49).

    Recommended mi values that modify the structural layer coefficients of
    untreated base and subbase materials in flexible pavements (AASHTO 1993,
    Eq. SN = a1 D1 + a2 D2 m2 + a3 D3 m3), as a function of the quality of
    drainage and the % of time the structure is near saturation.

    Parameters
    ----------
    quality : str, optional
        '', 'excellent', 'good', 'fair', 'poor', or 'very poor'. Empty (default)
        returns the whole table.

    Returns
    -------
    dict
        Full table or the matched quality row (mi per saturation column).

    Raises
    ------
    ValueError
        If quality is unrecognized.
    """
    return _drainage_lookup(_TABLE_5_49_MI, quality, "5-49", "mi",
                            "Drainage modifier mi (untreated base/subbase, "
                            "flexible pavements)")


def table_5_50_drainage_coefficient_cd(quality: str = "") -> dict:
    """AASHTO 1993 drainage coefficient Cd for RIGID pavements (Table 5-50).

    Recommended drainage coefficient Cd values used in the AASHTO 1993 rigid
    pavement design equation, as a function of the quality of drainage and the %
    of time the structure is near saturation.

    Parameters
    ----------
    quality : str, optional
        '', 'excellent', 'good', 'fair', 'poor', or 'very poor'. Empty (default)
        returns the whole table.

    Returns
    -------
    dict
        Full table or the matched quality row (Cd per saturation column).

    Raises
    ------
    ValueError
        If quality is unrecognized.
    """
    return _drainage_lookup(_TABLE_5_50_CD, quality, "5-50", "cd",
                            "Drainage coefficient Cd (rigid pavements)")


# ============================================================================
# Table 7-4: AASHTO quality-of-drainage definitions (time to remove water).
# (Chapter 7; PDF p.360, printed 7-9)
# ============================================================================

# (quality, water_removed_within)
_TABLE_7_4 = [
    ("Excellent", "2 hours"),
    ("Good", "1 day"),
    ("Fair", "1 week"),
    ("Poor", "1 month"),
    ("Very Poor", "Does not drain"),
]


def table_7_4_drainage_quality_definitions() -> dict:
    """AASHTO definitions of quality of pavement drainage (Table 7-4).

    The AASHTO 1993 quality-of-drainage classes, defined by the time needed to
    remove water (based on 50% time-to-drain). These classes key the mi and Cd
    drainage tables (5-49 / 5-50).

    Returns
    -------
    dict
        {'reference', 'table', 'pdf_page', 'printed_page', 'rows': [...]}
    """
    return {
        "reference": "FHWA-NHI-05-037 Table 7-4 (AASHTO, 1993)",
        "table": "7-4", "pdf_page": 360, "printed_page": "7-9",
        "rows": [{"quality_of_drainage": q, "water_removed_within": w}
                 for q, w in _TABLE_7_4],
        "note": "Based on 50% time-to-drain.",
    }


# ============================================================================
# Table 5-56 / 5-57: Typical saturated hydraulic conductivity (permeability).
# (Chapter 5; PDF p.281/280, printed 5-104/5-103)
# ============================================================================

# Table 5-56: soils (Coduto, 1999) — (description, k_cm_s, k_ft_s)
_TABLE_5_56 = [
    ("Clean gravel", "1 - 100", "3e-2 - 3"),
    ("Sand-gravel mixtures", "1e-2 - 10", "3e-4 - 0.3"),
    ("Clean coarse sand", "1e-2 - 1", "3e-4 - 3e-2"),
    ("Fine sand", "1e-3 - 1e-1", "3e-5 - 3e-3"),
    ("Silty sand", "1e-3 - 1e-2", "3e-5 - 3e-4"),
    ("Clayey sand", "1e-4 - 1e-2", "3e-6 - 3e-4"),
    ("Silt", "1e-8 - 1e-3", "3e-10 - 3e-5"),
    ("Clay", "1e-10 - 1e-6", "3e-12 - 3e-8"),
]

# Table 5-57: highway materials (Carter & Bentley, 1991) — (material, k_m_s)
_TABLE_5_57 = [
    ("Uniformly graded coarse aggregate", "0.4 - 4e-3"),
    ("Well-graded aggregate without fines", "4e-3 - 4e-5"),
    ("Concrete sand, low dust content", "7e-4 - 7e-6"),
    ("Concrete sand, high dust content", "7e-6 - 7e-8"),
    ("Silty and clayey sands", "1e-7 - 1e-9"),
    ("Compacted silt", "7e-8 - 7e-10"),
    ("Compacted clay", "< 1e-9"),
    ("Bituminous concrete", "4e-5 - 4e-8"),
    ("Portland cement concrete", "< 1e-10"),
]


def table_5_56_permeability_soils(soil_description: str = "") -> dict:
    """Typical saturated hydraulic conductivity (permeability) for soils (Table 5-56).

    Typical saturated hydraulic conductivity k for soils (Coduto, 1999), in cm/s
    and ft/s, from clean gravel (high k) to clay (very low k). Used to assess
    subgrade/subbase drainage capacity. (1 cm/s ~ 0.0328 ft/s.)

    Parameters
    ----------
    soil_description : str, optional
        '', or a soil description such as 'clean gravel', 'fine sand', 'silt',
        'clay'. Empty (default) returns the whole table.

    Returns
    -------
    dict
        Full table or the matched soil row (k in cm/s and ft/s, as printed
        ranges).

    Raises
    ------
    ValueError
        If soil_description is unrecognized.
    """
    rows = [{"soil_description": d, "k_cm_s": kc, "k_ft_s": kf}
            for d, kc, kf in _TABLE_5_56]
    key = str(soil_description).strip().lower()
    if key in ("", "all"):
        return {
            "reference": "FHWA-NHI-05-037 Table 5-56 (Coduto, 1999)",
            "table": "5-56", "pdf_page": 281, "printed_page": "5-104",
            "rows": rows,
        }
    match = next((r for r in rows if r["soil_description"].lower() == key), None)
    if match is None:
        raise ValueError(
            f"Unknown soil_description '{soil_description}'. Use e.g. 'clean "
            "gravel', 'fine sand', 'silt', or 'clay'."
        )
    out = dict(match)
    out.update({"reference": "FHWA-NHI-05-037 Table 5-56 (Coduto, 1999)",
                "table": "5-56", "pdf_page": 281, "printed_page": "5-104"})
    return out


def table_5_57_permeability_highway_materials(material: str = "") -> dict:
    """Typical saturated hydraulic conductivity for highway materials (Table 5-57).

    Typical saturated hydraulic conductivity k (m/s) for highway materials
    (Carter & Bentley, 1991), from open-graded aggregate (free-draining) down to
    Portland cement concrete. Used to evaluate permeable base/subbase and
    drainage-layer materials. (1 m/s = 3.25 ft/s.)

    Parameters
    ----------
    material : str, optional
        '', or a material such as 'well-graded aggregate without fines',
        'compacted clay', 'bituminous concrete'. Empty returns the whole table.

    Returns
    -------
    dict
        Full table or the matched material row (k in m/s, as printed ranges).

    Raises
    ------
    ValueError
        If material is unrecognized.
    """
    rows = [{"material": m, "k_m_s": k} for m, k in _TABLE_5_57]
    key = str(material).strip().lower()
    if key in ("", "all"):
        return {
            "reference": "FHWA-NHI-05-037 Table 5-57 (Carter & Bentley, 1991)",
            "table": "5-57", "pdf_page": 280, "printed_page": "5-103",
            "rows": rows,
            "note": "1 m/s = 3.25 ft/s.",
        }
    match = next((r for r in rows if r["material"].lower() == key), None)
    if match is None:
        raise ValueError(
            f"Unknown material '{material}'. Use e.g. 'well-graded aggregate "
            "without fines', 'compacted clay', or 'bituminous concrete'."
        )
    out = dict(match)
    out.update({"reference": "FHWA-NHI-05-037 Table 5-57 (Carter & Bentley, 1991)",
                "table": "5-57", "pdf_page": 280, "printed_page": "5-103"})
    return out


# ============================================================================
# Table 5-23 / 5-24 / 7-17: Swell (expansion) potential from Atterberg limits.
# (Chapter 5/7; PDF p.210/430, printed 5-33/7-79)
# ============================================================================

# Table 5-24 (Holtz & Gibbs 1956): rows of expansion criteria.
# (potential, finer_0p001mm_pct, pi_pct, sl_pct, probable_expansion_pct)
_TABLE_5_24 = [
    ("Very high", "> 28", "> 35", "< 11", "> 30"),
    ("High", "20-31", "25-41", "7-12", "20-30"),
    ("Medium", "13-23", "15-28", "10-16", "10-30"),
    ("Low", "< 15", "< 18", "> 15", "< 10"),
]

# Table 7-17 (Army & Air Force 1994): swell potential from LL and PI.
# (potential, ll, pi)
_TABLE_7_17 = [
    ("High", "> 60", "> 35"),
    ("Marginal", "50 - 60", "25 - 35"),
    ("Low", "< 50", "< 25"),
]


def table_5_24_swell_potential_holtz_gibbs(potential: str = "") -> dict:
    """Swell (expansion) potential from Atterberg limits (Table 5-24, Holtz & Gibbs 1956).

    Estimation of swell potential (Low / Medium / High / Very high) from the
    percentage finer than 0.001 mm, plasticity index PI (%), shrinkage limit SL
    (%), and the probable expansion (% total volume change under a 1 psi / 6.9 kPa
    load). Expansive subgrade soils must be removed, stabilized, or accounted for.

    Parameters
    ----------
    potential : str, optional
        '', 'low', 'medium', 'high', or 'very high'. Empty (default) returns the
        whole table.

    Returns
    -------
    dict
        Full table or the matched potential row.

    Raises
    ------
    ValueError
        If potential is unrecognized.
    """
    rows = [{"potential_for_expansion": p, "finer_than_0p001mm_pct": f,
             "plasticity_index_pct": pi, "shrinkage_limit_pct": sl,
             "probable_expansion_pct_total_volume": exp}
            for p, f, pi, sl, exp in _TABLE_5_24]
    key = str(potential).strip().lower()
    if key in ("", "all"):
        return {
            "reference": "FHWA-NHI-05-037 Table 5-24 (Holtz & Gibbs, 1956)",
            "table": "5-24", "pdf_page": 210, "printed_page": "5-33",
            "rows": rows,
            "note": "Probable expansion is % total volume change under 6.9 kPa (1 psi).",
        }
    match = next((r for r in rows
                  if r["potential_for_expansion"].lower() == key), None)
    if match is None:
        raise ValueError(
            f"Unknown potential '{potential}'. Use 'low', 'medium', 'high', or "
            "'very high'."
        )
    out = dict(match)
    out.update({"reference": "FHWA-NHI-05-037 Table 5-24 (Holtz & Gibbs, 1956)",
                "table": "5-24", "pdf_page": 210, "printed_page": "5-33"})
    return out


def table_7_17_swell_potential_ll_pi(potential: str = "") -> dict:
    """Swell potential of soils from liquid limit and plasticity index (Table 7-17).

    A simpler swell-potential screen (Low / Marginal / High) from the liquid
    limit (LL) and plasticity index (PI), used in the Chapter 7 stabilization
    guidance (Joint Departments of the Army & Air Force, 1994). Soils that swell
    in excess of 3% are treated as expansive for pavement purposes; lime
    treatment may then be appropriate.

    Parameters
    ----------
    potential : str, optional
        '', 'low', 'marginal', or 'high'. Empty (default) returns the whole table.

    Returns
    -------
    dict
        Full table or the matched potential row (LL and PI ranges).

    Raises
    ------
    ValueError
        If potential is unrecognized.
    """
    rows = [{"potential_swell": p, "liquid_limit": ll, "plasticity_index": pi}
            for p, ll, pi in _TABLE_7_17]
    key = str(potential).strip().lower()
    if key in ("", "all"):
        return {
            "reference": "FHWA-NHI-05-037 Table 7-17 (Army & Air Force, 1994)",
            "table": "7-17", "pdf_page": 430, "printed_page": "7-79",
            "rows": rows,
            "note": ("Soils that swell > 3% are expansive for pavement purposes; "
                     "lime treatment may be appropriate."),
        }
    match = next((r for r in rows if r["potential_swell"].lower() == key), None)
    if match is None:
        raise ValueError(
            f"Unknown potential '{potential}'. Use 'low', 'marginal', or 'high'."
        )
    out = dict(match)
    out.update({"reference": "FHWA-NHI-05-037 Table 7-17 (Army & Air Force, 1994)",
                "table": "7-17", "pdf_page": 430, "printed_page": "7-79"})
    return out


# ============================================================================
# Table 5-18: Typical compacted dry unit weight and OMC by AASHTO soil class
# (after Carter & Bentley, 1991).  (Chapter 5; PDF p.201, printed 5-24)
# ============================================================================

# aashto_class -> (description, gamma_pcf_min, gamma_pcf_max,
#                  gamma_knm3_min, gamma_knm3_max, omc_min, omc_max)
_TABLE_5_18 = {
    "A-1": ("Well-graded gravel/sand mixtures", 115, 134, 18.1, 21.1, 5, 15),
    "A-2": ("Silty or clayey gravel and sand", 109, 134, 17.2, 21.1, 9, 18),
    "A-3": ("Poorly graded sands", 100, 119, 15.7, 18.6, 5, 12),
    "A-4": ("Low plasticity silty sands and gravels", 94, 125, 14.7, 19.6, 10, 20),
    "A-5": ("Diatomaceous or micaceous silts", 84, 100, 13.2, 15.7, 20, 35),
    "A-6": ("Plastic clay, sandy clay", 94, 119, 14.7, 18.6, 10, 30),
    "A-7": ("Highly plastic clay", 81, 115, 12.7, 18.1, 15, 35),
}


def table_5_18_compaction_aashto(soil_class: str = "") -> dict:
    """Typical compacted dry unit weight and optimum moisture by AASHTO class (Table 5-18).

    Typical compacted dry unit weight (pcf and kN/m3) and optimum moisture
    content (%) by AASHTO soil class A-1 .. A-7 (after Carter & Bentley, 1991).

    Parameters
    ----------
    soil_class : str, optional
        '', or an AASHTO class 'A-1' .. 'A-7'. Empty (default) returns the whole
        table.

    Returns
    -------
    dict
        For a specific class: dry unit weight range (pcf, kN/m3) and OMC range
        (%). For '': {'rows': [...]}.

    Raises
    ------
    ValueError
        If soil_class is unrecognized.
    """
    def _row(cls):
        desc, gp_lo, gp_hi, gk_lo, gk_hi, w_lo, w_hi = _TABLE_5_18[cls]
        return {"aashto_class": cls, "description": desc,
                "dry_unit_weight_pcf_min": gp_lo, "dry_unit_weight_pcf_max": gp_hi,
                "dry_unit_weight_knm3_min": gk_lo, "dry_unit_weight_knm3_max": gk_hi,
                "optimum_moisture_content_pct_min": w_lo,
                "optimum_moisture_content_pct_max": w_hi}

    sc = str(soil_class).strip().upper()
    if sc in ("", "ALL"):
        return {
            "reference": "FHWA-NHI-05-037 Table 5-18 (Carter & Bentley, 1991)",
            "table": "5-18", "pdf_page": 201, "printed_page": "5-24",
            "rows": [_row(k) for k in _TABLE_5_18],
        }
    if sc not in _TABLE_5_18:
        raise ValueError(
            f"Unknown soil_class '{soil_class}'. Use an AASHTO class 'A-1' .. 'A-7'."
        )
    out = _row(sc)
    out.update({"reference": "FHWA-NHI-05-037 Table 5-18 (Carter & Bentley, 1991)",
                "table": "5-18", "pdf_page": 201, "printed_page": "5-24"})
    return out


# ============================================================================
# Table 7-15: Appropriate subgrade conditions for stabilization using
# geosynthetics (after FHWA HI-95-038).  (Chapter 7; PDF p.425, printed 7-74)
#
# Geosynthetic separation/reinforcement of a weak subgrade is appropriate when
# the subgrade is poor / low-strength / wet / sensitive, per these criteria.
# ============================================================================

# (condition, related_measures)
_TABLE_7_15 = [
    ("Poor soils",
     "USCS of SC, CL, CH, ML, MH, OL, OH, or PT; or AASHTO of A-5, A-6, A-7, "
     "or A-7-6"),
    ("Low strength",
     "Undrained shear strength cu < 13 psi, OR CBR < 3, OR Mr < 4500 psi"),
    ("High water table",
     "Within the zone of influence of surface loads"),
    ("High sensitivity",
     "High undisturbed strength compared to remolded strength"),
]


def table_7_15_geosynthetic_stabilization_criteria() -> dict:
    """Subgrade conditions appropriate for geosynthetic stabilization (Table 7-15).

    Geosynthetic separation/reinforcement of a weak subgrade (combining the
    separation, filtration, and reinforcement functions) is appropriate when the
    subgrade meets the poor-soil, low-strength, high-water-table, or high-
    sensitivity conditions in Table 7-15 (after FHWA HI-95-038). The key numeric
    low-strength triggers are cu < 13 psi, CBR < 3, or Mr < 4500 psi.

    Returns
    -------
    dict
        {'reference', 'table', 'pdf_page', 'printed_page', 'rows': [...]}
    """
    return {
        "reference": "FHWA-NHI-05-037 Table 7-15 (FHWA HI-95-038)",
        "table": "7-15", "pdf_page": 425, "printed_page": "7-74",
        "rows": [{"condition": c, "related_measures": m} for c, m in _TABLE_7_15],
        "low_strength_triggers": {"cu_psi_max": 13, "cbr_max": 3, "mr_psi_max": 4500},
        "note": ("Geosynthetic stabilization combines separation, filtration, and "
                 "reinforcement. AASHTO M288 governs the geotextile property "
                 "requirements."),
    }
