"""GEC-12 table lookup functions.

Digitized tables from FHWA-NHI-16-009 (GEC-12), Design and Construction
of Driven Pile Foundations. Follows the DM7 pattern: private data with
``_TABLE_*`` prefix, public lookup functions, case-insensitive keys.
"""

from geotech_references._interpolation import _linterp

# ============================================================================
# Table 7-1: Resistance Factors for Static Analysis Methods
# (modified from AASHTO 2014)
# ============================================================================

_TABLE_7_1_COMPRESSION = {
    "alpha_method": 0.35,
    "beta_method_1991": None,  # differs in manual — use field verification phi_dyn
    "brown_2001": None,  # not in AASHTO — use phi_dyn
    "api_rp2a_1993": None,  # not in AASHTO — use phi_dyn
    "eslami_fellenius": None,  # not in AASHTO — use phi_dyn
    "schmertmann_1975": 0.50,
    "nordlund": 0.45,
}

_TABLE_7_1_BLOCK_FAILURE = {"cohesive": 0.60}

_TABLE_7_1_TENSION = {
    "nordlund": 0.35,
    "alpha_method": 0.25,
    "beta_method_1991": 0.20,
    "lambda_method": 0.30,
    "spt_method": 0.25,
    "cpt_method": 0.40,
}

_TABLE_7_1_GROUP_UPLIFT = {"sand_and_clay": 0.50}
_TABLE_7_1_LATERAL = {"all_soils_and_rock": 1.0}


def table_7_1_resistance_factor_static(method: str,
                                       condition: str = "compression") -> float | None:
    """Resistance factor for static analysis methods (Table 7-1).

    Parameters
    ----------
    method : str
        Analysis method name (e.g., 'nordlund', 'alpha_method',
        'schmertmann_1975', 'beta_method_1991', 'eslami_fellenius').
    condition : str
        'compression', 'tension', 'block_failure', 'group_uplift',
        or 'lateral'.

    Returns
    -------
    float or None
        Resistance factor phi_stat. None means no AASHTO-specified
        factor; use the field verification method factor phi_dyn instead.

    Raises
    ------
    ValueError
        If method or condition is not recognized.
    """
    method_key = method.lower().strip().replace("-", "_").replace(" ", "_")
    cond = condition.lower().strip()

    if cond == "compression":
        table = _TABLE_7_1_COMPRESSION
    elif cond == "tension":
        table = _TABLE_7_1_TENSION
    elif cond == "block_failure":
        table = _TABLE_7_1_BLOCK_FAILURE
    elif cond == "group_uplift":
        table = _TABLE_7_1_GROUP_UPLIFT
    elif cond == "lateral":
        table = _TABLE_7_1_LATERAL
    else:
        raise ValueError(
            f"Unknown condition '{condition}'. Use: compression, tension, "
            f"block_failure, group_uplift, or lateral."
        )

    if method_key not in table:
        available = ", ".join(table.keys())
        raise ValueError(
            f"Unknown method '{method}' for condition '{condition}'. "
            f"Available: {available}"
        )

    return table[method_key]


# ============================================================================
# Table 7-2: Resistance Factors for Field Determination Methods
# (after AASHTO 2014)
# ============================================================================

_TABLE_7_2_COMPRESSION = [
    {
        "method": "Static load test + dynamic testing (2% production)",
        "phi_dyn": 0.80,
    },
    {
        "method": "Static load test (1 per site condition, no dynamic)",
        "phi_dyn": 0.75,
    },
    {
        "method": "Dynamic testing on 100% of production piles",
        "phi_dyn": 0.75,
    },
    {
        "method": "Dynamic testing QC (2 per site condition, >=2% production)",
        "phi_dyn": 0.65,
    },
    {
        "method": "Wave equation analysis only (EOD)",
        "phi_dyn": 0.50,
    },
    {
        "method": "FHWA Modified Gates dynamic formula (EOD)",
        "phi_dyn": 0.40,
    },
    {
        "method": "Engineering News dynamic formula (EOD)",
        "phi_dyn": 0.10,
    },
]

_TABLE_7_2_TENSION = [
    {"method": "Static load test", "phi_dyn": 0.60},
    {"method": "Dynamic testing with signal matching", "phi_dyn": 0.50},
]


def table_7_2_resistance_factor_field(method: str) -> float:
    """Resistance factor for field determination methods (Table 7-2).

    Parameters
    ----------
    method : str
        Partial match on the method description (case-insensitive).
        Examples: 'static load test', 'wave equation', 'gates',
        'engineering news', 'dynamic testing 100%'.

    Returns
    -------
    float
        Resistance factor phi_dyn.

    Raises
    ------
    ValueError
        If no matching method is found.
    """
    query = method.lower().strip()
    all_entries = _TABLE_7_2_COMPRESSION + _TABLE_7_2_TENSION

    for entry in all_entries:
        if query in entry["method"].lower():
            return entry["phi_dyn"]

    # Try partial word matching
    for entry in all_entries:
        words = query.split()
        if all(w in entry["method"].lower() for w in words):
            return entry["phi_dyn"]

    methods = [e["method"] for e in all_entries]
    raise ValueError(
        f"No matching method for '{method}'. Available:\n"
        + "\n".join(f"  - {m}" for m in methods)
    )


# ============================================================================
# Table 7-9: Approximate Range of beta and Nt Coefficients
# (after Fellenius 2014)
# ============================================================================

_TABLE_7_9 = {
    "clay":    {"phi_min": 25, "phi_max": 30, "beta_min": 0.15, "beta_max": 0.35, "nt_min": 3,  "nt_max": 30},
    "silt":    {"phi_min": 28, "phi_max": 34, "beta_min": 0.25, "beta_max": 0.50, "nt_min": 20, "nt_max": 40},
    "sand":    {"phi_min": 32, "phi_max": 40, "beta_min": 0.30, "beta_max": 0.90, "nt_min": 30, "nt_max": 150},
    "gravel":  {"phi_min": 35, "phi_max": 45, "beta_min": 0.35, "beta_max": 0.80, "nt_min": 60, "nt_max": 300},
}


def table_7_9_beta_nt_coefficients(soil_type: str) -> dict:
    """Approximate range of beta and Nt coefficients (Table 7-9).

    Parameters
    ----------
    soil_type : str
        Soil type: 'clay', 'silt', 'sand', or 'gravel'.

    Returns
    -------
    dict
        Keys: phi_min, phi_max, beta_min, beta_max, nt_min, nt_max.
    """
    key = soil_type.lower().strip()
    if key not in _TABLE_7_9:
        raise ValueError(
            f"Unknown soil type '{soil_type}'. "
            f"Use: {', '.join(_TABLE_7_9.keys())}"
        )
    return dict(_TABLE_7_9[key])


# ============================================================================
# Table 7-10: Input Factors for Brown's Method
# ============================================================================

_TABLE_7_10 = [
    # (loading, installation, soil_type, Fvs, Ab_ksf, Bb_ksf_per_bpf)
    ("compression", "impact", "clay_to_sand",           1.0,  0.555, 0.040),
    ("compression", "impact", "gravelly_sand_to_boulders", 1.0, 0.888, 0.888),
    ("compression", "impact", "rock",                   1.0,  2.89,  2.89),
    ("tension",     "impact", "clay_to_sand",           1.0,  0.522, 0.0376),
    ("tension",     "impact", "gravelly_sand_to_boulders", 1.0, 0.835, 0.0),
    ("tension",     "impact", "rock",                   1.0,  2.71,  0.0),
    ("compression", "vibratory", "clay_to_sand",        0.68, 0.522, 0.0376),
    ("compression", "vibratory", "gravelly_sand_to_boulders", 0.68, 0.835, 0.0),
    ("compression", "vibratory", "rock",                0.68, 2.71,  0.0),
]


def table_7_10_brown_method_factors(loading: str = "compression",
                                    installation: str = "impact",
                                    soil_type: str = "clay_to_sand") -> dict:
    """Input factors for Brown's SPT-based method (Table 7-10).

    Parameters
    ----------
    loading : str
        'compression' or 'tension'.
    installation : str
        'impact' or 'vibratory'.
    soil_type : str
        'clay_to_sand', 'gravelly_sand_to_boulders', or 'rock'.

    Returns
    -------
    dict
        Keys: Fvs, Ab_ksf, Bb_ksf_per_bpf.
    """
    load_key = loading.lower().strip()
    inst_key = installation.lower().strip()
    soil_key = soil_type.lower().strip().replace(" ", "_")

    for row in _TABLE_7_10:
        if row[0] == load_key and row[1] == inst_key and row[2] == soil_key:
            return {"Fvs": row[3], "Ab_ksf": row[4], "Bb_ksf_per_bpf": row[5]}

    raise ValueError(
        f"No match for loading='{loading}', installation='{installation}', "
        f"soil_type='{soil_type}'."
    )


# ============================================================================
# Table 7-11: Cs Values for Eslami and Fellenius Method
# (after Fellenius 2014)
# ============================================================================

_TABLE_7_11 = {
    "soft_sensitive_soil":     8.0,
    "clay":                    5.0,
    "silty_clay_stiff_clay_silt": 2.5,
    "sandy_silt_silt":         1.5,
    "fine_sand_silty_sand":    1.0,
    "sand":                    0.4,
}


def table_7_11_eslami_fellenius_cs(soil_type: str) -> float:
    """Shaft correlation coefficient Cs for Eslami-Fellenius method (Table 7-11).

    Parameters
    ----------
    soil_type : str
        Soil type description. Partial match supported.

    Returns
    -------
    float
        Cs value in percent.
    """
    key = soil_type.lower().strip().replace(" ", "_").replace("-", "_")

    if key in _TABLE_7_11:
        return _TABLE_7_11[key]

    # Partial match
    for k, v in _TABLE_7_11.items():
        if key in k or k in key:
            return v

    raise ValueError(
        f"Unknown soil type '{soil_type}'. "
        f"Available: {', '.join(_TABLE_7_11.keys())}"
    )


# ============================================================================
# Table 7-16: Soil Setup Factors (after Rausche et al. 1996)
# ============================================================================

_TABLE_7_16 = {
    "clay":        {"range_min": 1.2, "range_max": 5.5, "recommended": 2.0},
    "silt_clay":   {"range_min": 1.0, "range_max": 2.0, "recommended": 1.0},
    "silt":        {"range_min": 1.5, "range_max": 5.0, "recommended": 1.5},
    "sand_clay":   {"range_min": 1.0, "range_max": 6.0, "recommended": 1.5},
    "sand_silt":   {"range_min": 1.2, "range_max": 2.0, "recommended": 1.2},
    "fine_sand":   {"range_min": 1.2, "range_max": 2.0, "recommended": 1.2},
    "sand":        {"range_min": 0.8, "range_max": 2.0, "recommended": 1.0},
    "sand_gravel": {"range_min": 1.2, "range_max": 2.0, "recommended": 1.0},
}


def table_7_16_soil_setup_factor(soil_type: str) -> dict:
    """Soil setup factors by predominant soil type (Table 7-16).

    Parameters
    ----------
    soil_type : str
        Predominant soil type along pile shaft (e.g., 'clay', 'sand',
        'silt_clay', 'sand_silt', 'fine_sand', 'sand_gravel').

    Returns
    -------
    dict
        Keys: range_min, range_max, recommended.
    """
    key = soil_type.lower().strip().replace(" ", "_").replace("-", "_")

    if key not in _TABLE_7_16:
        # Try partial match
        for k in _TABLE_7_16:
            if key in k or k in key:
                return dict(_TABLE_7_16[k])
        raise ValueError(
            f"Unknown soil type '{soil_type}'. "
            f"Available: {', '.join(_TABLE_7_16.keys())}"
        )
    return dict(_TABLE_7_16[key])


# ============================================================================
# Table 7-3: Summary of Static Analysis Methods
# ============================================================================

_TABLE_7_3 = [
    {"method": "Meyerhof (1976)",        "soil_type": "cohesionless", "input": "SPT N",  "in_gec12": False, "in_aashto": True,  "phi_stat": 0.30},
    {"method": "Nordlund (1963)",        "soil_type": "cohesionless", "input": "phi'",   "in_gec12": True,  "in_aashto": True,  "phi_stat": 0.45},
    {"method": "alpha-method (1980)",    "soil_type": "cohesive",     "input": "su",     "in_gec12": True,  "in_aashto": True,  "phi_stat": 0.35},
    {"method": "beta-method (1951/1979)","soil_type": "cohesive",     "input": "su",     "in_gec12": False, "in_aashto": True,  "phi_stat": 0.25},
    {"method": "lambda-method (1972)",   "soil_type": "cohesive",     "input": "su",     "in_gec12": False, "in_aashto": True,  "phi_stat": 0.40},
    {"method": "API RP2A (1993)",        "soil_type": "mixed",        "input": "su, phi'","in_gec12": True, "in_aashto": False, "phi_stat": None},
    {"method": "beta-method (1991)",     "soil_type": "mixed",        "input": "phi'",   "in_gec12": True,  "in_aashto": False, "phi_stat": None},
    {"method": "Brown (2001)",           "soil_type": "mixed",        "input": "SPT N",  "in_gec12": True,  "in_aashto": False, "phi_stat": None},
    {"method": "Eslami & Fellenius (1997)","soil_type": "mixed",      "input": "CPTu",   "in_gec12": True,  "in_aashto": False, "phi_stat": None},
    {"method": "Schmertmann (1975)",     "soil_type": "mixed",        "input": "CPT",    "in_gec12": True,  "in_aashto": True,  "phi_stat": 0.50},
]


def table_7_3_static_analysis_methods(soil_type: str = "") -> list[dict]:
    """Summary of static analysis methods for nominal resistance (Table 7-3).

    Parameters
    ----------
    soil_type : str
        Optional filter: 'cohesionless', 'cohesive', or 'mixed'.

    Returns
    -------
    list of dict
        Matching methods with keys: method, soil_type, input, in_gec12,
        in_aashto, phi_stat.
    """
    if not soil_type:
        return [dict(row) for row in _TABLE_7_3]

    key = soil_type.lower().strip()
    return [dict(row) for row in _TABLE_7_3 if key in row["soil_type"]]


# ============================================================================
# Table 7-8: Design Parameter Guidelines for Cohesionless Siliceous Soil
# (after API 1993)
# ============================================================================

_TABLE_7_8 = [
    {"delta_deg": 15, "fs_limit_ksf": 1.0, "Nq": 8,  "qp_limit_ksf": 40},
    {"delta_deg": 20, "fs_limit_ksf": 1.4, "Nq": 12, "qp_limit_ksf": 60},
    {"delta_deg": 25, "fs_limit_ksf": 1.7, "Nq": 20, "qp_limit_ksf": 100},
    {"delta_deg": 30, "fs_limit_ksf": 2.0, "Nq": 40, "qp_limit_ksf": 200},
    {"delta_deg": 35, "fs_limit_ksf": 2.4, "Nq": 50, "qp_limit_ksf": 250},
]

_TABLE_7_8_DENSITY_MAP = {
    15: [("very_loose", "sand"), ("loose", "sand_silt"), ("medium", "silt")],
    20: [("loose", "sand"), ("medium", "sand_silt"), ("dense", "silt")],
    25: [("medium", "sand"), ("dense", "sand_silt")],
    30: [("dense", "sand"), ("very_dense", "sand_silt")],
    35: [("dense", "gravel"), ("very_dense", "sand")],
}


def table_7_8_api_design_parameters(delta_deg: float) -> dict:
    """API design parameters for cohesionless siliceous soil (Table 7-8).

    Parameters
    ----------
    delta_deg : float
        Soil-pile friction angle (degrees): 15, 20, 25, 30, or 35.
        Interpolation between values is supported.

    Returns
    -------
    dict
        Keys: delta_deg, fs_limit_ksf, Nq, qp_limit_ksf.
    """
    deltas = [row["delta_deg"] for row in _TABLE_7_8]
    if delta_deg < deltas[0] or delta_deg > deltas[-1]:
        raise ValueError(
            f"delta={delta_deg} deg is outside the range "
            f"{deltas[0]}-{deltas[-1]} deg."
        )

    # Exact match
    for row in _TABLE_7_8:
        if row["delta_deg"] == delta_deg:
            return dict(row)

    # Interpolate
    from geotech_references._interpolation import _linterp
    fs_vals = [row["fs_limit_ksf"] for row in _TABLE_7_8]
    nq_vals = [row["Nq"] for row in _TABLE_7_8]
    qp_vals = [row["qp_limit_ksf"] for row in _TABLE_7_8]

    return {
        "delta_deg": delta_deg,
        "fs_limit_ksf": _linterp(delta_deg, deltas, fs_vals),
        "Nq": _linterp(delta_deg, deltas, nq_vals),
        "qp_limit_ksf": _linterp(delta_deg, deltas, qp_vals),
    }
