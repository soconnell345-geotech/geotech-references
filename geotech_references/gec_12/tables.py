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

# FHWA-NHI-16-009 (GEC-12) Vol I, Table 7-2 "Resistance Factors for Field
# Determination Methods (after AASHTO 2014)", p. 226 (PDF page 272), read
# off the rendered page. (key, condition, method as printed, phi_dyn)
_TABLE_7_2 = [
    ("static_load_test_and_dynamic_testing", "compression",
     "Driving criteria established by successful static load test of at "
     "least one pile per site condition and dynamic testing* of at least "
     "two piles per site condition, but no less than 2% of the production "
     "piles.", 0.80),
    ("static_load_test_without_dynamic_testing", "compression",
     "Driving criteria established by successful static load test of at "
     "least one pile per site condition without dynamic testing.", 0.75),
    ("dynamic_testing_100_percent", "compression",
     "Driving criteria established by dynamic testing* conducted on 100% "
     "of production piles.", 0.75),
    ("dynamic_testing_2_percent", "compression",
     "Driving criteria established by dynamic testing,* quality control by "
     "dynamic testing* of at least two piles per site condition, but no "
     "less than 2% of the production piles.", 0.65),
    ("wave_equation", "compression",
     "Wave equation analysis, without pile dynamic measurements or load "
     "test, at End of Drive conditions only.", 0.50),
    ("fhwa_modified_gates", "compression",
     "FHWA Modified Gates dynamic pile formula (End of Drive condition "
     "only).", 0.40),
    ("engineering_news", "compression",
     "Engineering News (as defined in AASHTO) dynamic pile formula (End of "
     "Drive condition only).", 0.10),
    ("tension_static_load_test", "tension",
     "Static load test.", 0.60),
    ("tension_dynamic_testing_signal_matching", "tension",
     "Dynamic testing* with signal matching.", 0.50),
]

_TABLE_7_2_FOOTNOTE = (
    "* - Dynamic testing requires signal matching, and best estimates of "
    "nominal resistance are made from a restrike test. Dynamic tests are "
    "calibrated to the static load test, when available."
)

# Other spellings of ONE printed row. "static load test" and "dynamic
# testing" alone each fit several rows and are refused.
_TABLE_7_2_ALIASES = {
    "static load test + dynamic testing (2% production)":
        "static_load_test_and_dynamic_testing",
    "static load test and dynamic testing":
        "static_load_test_and_dynamic_testing",
    "static load test with dynamic testing":
        "static_load_test_and_dynamic_testing",
    "static load test (1 per site condition, no dynamic)":
        "static_load_test_without_dynamic_testing",
    "static load test without dynamic testing":
        "static_load_test_without_dynamic_testing",
    "static load test only":
        "static_load_test_without_dynamic_testing",
    "dynamic testing on 100% of production piles":
        "dynamic_testing_100_percent",
    "dynamic testing 100%": "dynamic_testing_100_percent",
    "dynamic testing on 100%": "dynamic_testing_100_percent",
    "dynamic testing qc (2 per site condition, >=2% production)":
        "dynamic_testing_2_percent",
    "dynamic testing 2%": "dynamic_testing_2_percent",
    "dynamic testing quality control": "dynamic_testing_2_percent",
    "wave equation analysis only (eod)": "wave_equation",
    "wave equation analysis": "wave_equation",
    "wave equation": "wave_equation",
    "fhwa modified gates dynamic formula (eod)": "fhwa_modified_gates",
    "fhwa modified gates": "fhwa_modified_gates",
    "modified gates": "fhwa_modified_gates",
    "gates": "fhwa_modified_gates",
    "engineering news dynamic formula (eod)": "engineering_news",
    "engineering news formula": "engineering_news",
    "engineering news": "engineering_news",
    "enr": "engineering_news",
    "static load test (tension)": "tension_static_load_test",
    "tension static load test": "tension_static_load_test",
    "dynamic testing with signal matching (tension)":
        "tension_dynamic_testing_signal_matching",
    "tension dynamic testing": "tension_dynamic_testing_signal_matching",
}


def table_7_2_resistance_factor_field(method: str) -> float:
    """Resistance factor phi_dyn (dimensionless) for one field determination method of GEC-12 Table 7-2 (FHWA-NHI-16-009 Vol I, p. 226, after AASHTO 2014).

    Compression: static load test of at least one pile per site condition
    AND dynamic testing of at least two piles per site condition (no less
    than 2% of production piles) 0.80; static load test without dynamic
    testing 0.75; dynamic testing on 100% of production piles 0.75;
    dynamic testing of at least two piles per site condition (no less than
    2%) 0.65; wave equation analysis at End of Drive 0.50; FHWA Modified
    Gates formula 0.40; Engineering News formula 0.10. Tension: static load
    test 0.60; dynamic testing with signal matching 0.50. Table footnote:
    dynamic testing requires signal matching, and best estimates of nominal
    resistance are made from a restrike test.

    Parameters
    ----------
    method : str
        One row of the table, by its key:
        'static_load_test_and_dynamic_testing' (0.80),
        'static_load_test_without_dynamic_testing' (0.75),
        'dynamic_testing_100_percent' (0.75),
        'dynamic_testing_2_percent' (0.65), 'wave_equation' (0.50),
        'fhwa_modified_gates' (0.40), 'engineering_news' (0.10),
        'tension_static_load_test' (0.60),
        'tension_dynamic_testing_signal_matching' (0.50).
        'static load test' or 'dynamic testing' alone fits several rows
        and is refused.

    Returns
    -------
    float
        Resistance factor phi_dyn of that row.

    Raises
    ------
    ValueError
        If method does not name one row of the table.
    """
    query = " ".join(method.lower().strip().rstrip(".").split())
    key = _TABLE_7_2_ALIASES.get(query, query.replace(" ", "_").replace("-", "_"))

    for row_key, _condition, _text, phi in _TABLE_7_2:
        if row_key == key:
            return phi

    raise ValueError(
        f"'{method}' does not name one row of GEC-12 Table 7-2 (p. 226). "
        "Rows (key: phi_dyn, condition, method as printed):\n"
        + "\n".join(f"  - {k}: {phi:.2f}, {cond}: {text}"
                    for k, cond, text, phi in _TABLE_7_2)
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
# FHWA-NHI-16-009 (GEC-12) Vol I, p. 260 (PDF page 306); Eq. 7-21, p. 258:
# fs = Fvs (Ab + Bb N60), fs in ksf, N60 held between 3 and 50 (p. 259).
#
# Read off the rendered page (PDF page 306). The rows are as printed except
# one cell pair, by the lead's ruling (RULINGS row 7, review finding gec-06):
# Bb for the two compression rows "Gravelly Sand to Boulders" and "Rock" is
# PRINTED equal to Ab (0.888 and 2.89); it is CODED 0.0, as the matching
# tension rows print it. In the printed table each tension Ab is about 0.94
# times its compression Ab (0.522/0.555, 0.835/0.888, 2.71/2.89) and the
# clay-to-sand tension Bb is 0.94 times its compression Bb (0.0376/0.040);
# the tension Bb of gravelly sand to boulders and of rock prints 0.0. With
# Bb = 0.888, Eq. 7-21 gives 27.5 ksf at N60 = 30, against Table 7-8's 2.4
# ksf limit. Those two rows carry a print_note.
# The three Vibratory rows are typeset under a ditto mark below "Tension"
# and are filed under tension, as printed; the table prints no vibratory
# compression row.
# ============================================================================

_TABLE_7_10 = [
    # (loading, installation, soil_type, Fvs, Ab_ksf, Bb_ksf_per_bpf)
    ("compression", "impact", "clay_to_sand",           1.0,  0.555, 0.040),
    ("compression", "impact", "gravelly_sand_to_boulders", 1.0, 0.888, 0.0),
    ("compression", "impact", "rock",                   1.0,  2.89,  0.0),
    ("tension",     "impact", "clay_to_sand",           1.0,  0.522, 0.0376),
    ("tension",     "impact", "gravelly_sand_to_boulders", 1.0, 0.835, 0.0),
    ("tension",     "impact", "rock",                   1.0,  2.71,  0.0),
    ("tension",     "vibratory", "clay_to_sand",        0.68, 0.522, 0.0376),
    ("tension",     "vibratory", "gravelly_sand_to_boulders", 0.68, 0.835, 0.0),
    ("tension",     "vibratory", "rock",                0.68, 2.71,  0.0),
]

# The printed Bb of the two rows coded 0.0 (RULINGS row 7).
_TABLE_7_10_PRINTED_BB = {
    ("compression", "impact", "gravelly_sand_to_boulders"): 0.888,
    ("compression", "impact", "rock"): 2.89,
}


def table_7_10_brown_method_factors(loading: str = "compression",
                                    installation: str = "impact",
                                    soil_type: str = "clay_to_sand") -> dict:
    """Input factors Fvs, Ab (ksf) and Bb (ksf per blow/ft) of Brown's SPT method, fs = Fvs (Ab + Bb N60), from GEC-12 Table 7-10 (FHWA-NHI-16-009 Vol I, p. 260, PDF page 306). For compression in gravelly sand to boulders and in rock the table prints Bb equal to Ab (0.888 and 2.89); Bb = 0.0 is returned there, as the matching tension rows print it, with a print_note saying so (lead's ruling). The vibratory rows are printed under "Tension" and are answered for loading 'tension' only.

    Eq. 7-21 (p. 258): fs = Fvs (Ab + Bb N60) in ksf, with N60 taken no
    higher than 50 and no lower than 3 (p. 259). The manual recommends the
    method for preliminary length estimates only (p. 259). With the printed
    Bb = 0.888, Eq. 7-21 gives 27.5 ksf at N60 = 30 for gravelly sand to
    boulders, against Table 7-8's limit of 2.4 ksf on unit shaft resistance
    (p. 253). In the printed table each tension Ab is about 0.94 times its
    compression Ab (0.522/0.555, 0.835/0.888, 2.71/2.89) and the
    clay-to-sand tension Bb is 0.94 times its compression Bb
    (0.0376/0.040); the tension Bb of gravelly sand to boulders and of rock
    prints 0.0.

    Parameters
    ----------
    loading : str
        'compression' or 'tension'.
    installation : str
        'impact' or 'vibratory' (vibratory rows are printed under tension
        only).
    soil_type : str
        'clay_to_sand', 'gravelly_sand_to_boulders', or 'rock'.

    Returns
    -------
    dict
        Keys: Fvs, Ab_ksf, Bb_ksf_per_bpf; for the two compression rows
        whose printed Bb is replaced by 0.0, also Bb_printed_ksf_per_bpf
        and print_note.
    """
    load_key = loading.lower().strip()
    inst_key = installation.lower().strip()
    soil_key = soil_type.lower().strip().replace(" ", "_")

    for row in _TABLE_7_10:
        if row[0] == load_key and row[1] == inst_key and row[2] == soil_key:
            out = {"Fvs": row[3], "Ab_ksf": row[4], "Bb_ksf_per_bpf": row[5]}
            printed = _TABLE_7_10_PRINTED_BB.get(row[:3])
            if printed is not None:
                out["Bb_printed_ksf_per_bpf"] = printed
                out["print_note"] = (
                    f"GEC-12 Table 7-10 (p. 260) prints Bb = {printed} for "
                    f"this row, equal to its Ab; Bb = 0.0 is used, as the "
                    f"matching tension row prints it. With the printed "
                    f"value, Eq. 7-21 gives far more than Table 7-8's 2.4 "
                    f"ksf limit on unit shaft resistance (p. 253)."
                )
            return out

    rows = ", ".join(f"({r[0]}, {r[1]}, {r[2]})" for r in _TABLE_7_10)
    raise ValueError(
        f"No match for loading='{loading}', installation='{installation}', "
        f"soil_type='{soil_type}' in GEC-12 Table 7-10 (p. 260), which "
        f"prints the vibratory rows under tension only. Printed rows: {rows}."
    )


# ============================================================================
# Table 7-11: Cs Values for Eslami and Fellenius Method
# (after Fellenius 2014)
# ============================================================================

# FHWA-NHI-16-009 (GEC-12) Vol I, p. 261 (PDF page 307), read off the
# rendered page: Soil Type | Cs (%)
#   Soft sensitive soil 8.0 | Clay 5.0 | Silty clay, stiff clay and silt 2.5
#   Sandy silt and silt 1.5 | Fine sand or silty sand 1.0 | Sand 0.4
_TABLE_7_11 = {
    "soft_sensitive_soil":     8.0,
    "clay":                    5.0,
    "silty_clay_stiff_clay_silt": 2.5,
    "sandy_silt_silt":         1.5,
    "fine_sand_silty_sand":    1.0,
    "sand":                    0.4,
}

_TABLE_7_11_ROWS = {
    "soft_sensitive_soil": "Soft sensitive soil",
    "clay": "Clay",
    "silty_clay_stiff_clay_silt": "Silty clay, stiff clay and silt",
    "sandy_silt_silt": "Sandy silt and silt",
    "fine_sand_silty_sand": "Fine sand or silty sand",
    "sand": "Sand",
}

# One soil named in one printed row. "silt" is printed in two rows (2.5 and
# 1.5) and is refused.
_TABLE_7_11_ALIASES = {
    "soft_sensitive": "soft_sensitive_soil",
    "silty_clay": "silty_clay_stiff_clay_silt",
    "stiff_clay": "silty_clay_stiff_clay_silt",
    "silty_clay,_stiff_clay_and_silt": "silty_clay_stiff_clay_silt",
    "sandy_silt": "sandy_silt_silt",
    "sandy_silt_and_silt": "sandy_silt_silt",
    "fine_sand": "fine_sand_silty_sand",
    "silty_sand": "fine_sand_silty_sand",
    "fine_sand_or_silty_sand": "fine_sand_silty_sand",
}


def table_7_11_eslami_fellenius_cs(soil_type: str) -> float:
    """Shaft correlation coefficient Cs, in PERCENT, of the Eslami and Fellenius CPT method for one soil type of GEC-12 Table 7-11 (FHWA-NHI-16-009 Vol I, p. 261, after Fellenius 2014).

    As printed: soft sensitive soil 8.0; clay 5.0; silty clay, stiff clay
    and silt 2.5; sandy silt and silt 1.5; fine sand or silty sand 1.0;
    sand 0.4. The value is a percentage (8.0 means 8 %).

    Parameters
    ----------
    soil_type : str
        One row: 'soft_sensitive_soil', 'clay',
        'silty_clay_stiff_clay_silt' (or 'silty_clay', 'stiff_clay'),
        'sandy_silt_silt' (or 'sandy_silt'), 'fine_sand_silty_sand' (or
        'fine_sand', 'silty_sand'), 'sand'. 'silt' alone is printed in two
        rows (2.5 and 1.5) and is refused.

    Returns
    -------
    float
        Cs value in percent.

    Raises
    ------
    ValueError
        If soil_type does not name one row of the table.
    """
    key = soil_type.lower().strip().replace(" ", "_").replace("-", "_")
    key = _TABLE_7_11_ALIASES.get(key, key)

    if key in _TABLE_7_11:
        return _TABLE_7_11[key]

    raise ValueError(
        f"'{soil_type}' does not name one row of GEC-12 Table 7-11 "
        "(p. 261). Rows (key: Cs %, soil type as printed): "
        + "; ".join(f"{k}: {v}, {_TABLE_7_11_ROWS[k]}"
                    for k, v in _TABLE_7_11.items())
    )


# ============================================================================
# Table 7-16: Soil Setup Factors (after Rausche et al. 1996)
# ============================================================================

# FHWA-NHI-16-009 (GEC-12) Vol I, p. 299 (PDF page 345), read off the
# rendered page:
#
#   Predominant Soil Type   Range in Soil   Recommended Soil   Number of Sites and
#   Along Pile Shaft        Setup Factor    Setup Factors*     (Percentage of Database)
#   Clay                    1.2-5.5         2.0                7 (15%)
#   Silt - Clay             1.0-2.0         1.0                10 (22%)
#   Silt                    1.5-5.0         1.5                2 (4%)
#   Sand - Clay             1.0-6.0         1.5                13 (28%)
#   Sand - Silt             1.2-2.0         1.2                8 (18%)
#   Fine Sand               1.2-2.0         1.2                2 (4%)
#   Sand                    0.8-2.0         1.0                3 (7%)
#   Sand - Gravel           1.2-2.0         1.0                1 (2%)
#   * Confirmation with Local Experience Recommended.
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

# key: (row name as printed, number of sites, percentage of database)
_TABLE_7_16_ROWS = {
    "clay": ("Clay", 7, 15),
    "silt_clay": ("Silt - Clay", 10, 22),
    "silt": ("Silt", 2, 4),
    "sand_clay": ("Sand - Clay", 13, 28),
    "sand_silt": ("Sand - Silt", 8, 18),
    "fine_sand": ("Fine Sand", 2, 4),
    "sand": ("Sand", 3, 7),
    "sand_gravel": ("Sand - Gravel", 1, 2),
}

# Two-soil names in either order, for the print's "Silt - Clay" and the like.
_TABLE_7_16_ALIASES = {
    "silty_clay": "silt_clay", "clayey_silt": "silt_clay",
    "clay_silt": "silt_clay",
    "sandy_clay": "sand_clay", "clayey_sand": "sand_clay",
    "clay_sand": "sand_clay",
    "silty_sand": "sand_silt", "sandy_silt": "sand_silt",
    "silt_sand": "sand_silt",
    "sandy_gravel": "sand_gravel", "gravelly_sand": "sand_gravel",
    "gravel_sand": "sand_gravel",
}

_TABLE_7_16_NOTE = "* Confirmation with Local Experience Recommended."
_TABLE_7_16_REFERENCE = ("FHWA-NHI-16-009 (GEC-12) Vol I, Table 7-16 Soil "
                         "Setup Factors (after Rausche et al. 1996), p. 299")


def table_7_16_soil_setup_factor(soil_type: str) -> dict:
    """Soil setup factor (dimensionless: range and recommended value) for the predominant soil type along the pile shaft, one row of GEC-12 Table 7-16 (FHWA-NHI-16-009 Vol I, p. 299, after Rausche et al. 1996).

    As printed (range, recommended): Clay 1.2-5.5, 2.0; Silt - Clay
    1.0-2.0, 1.0; Silt 1.5-5.0, 1.5; Sand - Clay 1.0-6.0, 1.5; Sand - Silt
    1.2-2.0, 1.2; Fine Sand 1.2-2.0, 1.2; Sand 0.8-2.0, 1.0; Sand - Gravel
    1.2-2.0, 1.0. Table footnote on the recommended values: "Confirmation
    with Local Experience Recommended."

    Parameters
    ----------
    soil_type : str
        One row: 'clay', 'silt_clay' (or 'silty clay', 'clayey silt'),
        'silt', 'sand_clay' (or 'sandy clay', 'clayey sand'), 'sand_silt'
        (or 'silty sand', 'sandy silt'), 'fine_sand', 'sand', 'sand_gravel'
        (or 'sandy gravel', 'gravelly sand'). Any other name is refused.

    Returns
    -------
    dict
        Keys: soil_type (the row as printed), range_min, range_max,
        recommended, sites, percent_of_database, note (the footnote),
        reference.

    Raises
    ------
    ValueError
        If soil_type does not name one row of the table.
    """
    key = soil_type.lower().strip().replace(" ", "_").replace("-", "_")
    while "__" in key:
        key = key.replace("__", "_")
    key = _TABLE_7_16_ALIASES.get(key, key)

    if key not in _TABLE_7_16:
        raise ValueError(
            f"'{soil_type}' does not name one row of GEC-12 Table 7-16 "
            "(p. 299). Rows (key: soil type as printed): "
            + "; ".join(f"{k}: {v[0]}" for k, v in _TABLE_7_16_ROWS.items())
        )
    name, sites, pct = _TABLE_7_16_ROWS[key]
    out = {"soil_type": name}
    out.update(_TABLE_7_16[key])
    out.update({"sites": sites, "percent_of_database": pct,
                "note": _TABLE_7_16_NOTE,
                "reference": _TABLE_7_16_REFERENCE})
    return out


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
        Optional filter, the table's own soil types: 'cohesionless',
        'cohesive', or 'mixed'. Empty returns every method.

    Returns
    -------
    list of dict
        Matching methods with keys: method, soil_type, input, in_gec12,
        in_aashto, phi_stat.

    Raises
    ------
    ValueError
        If soil_type is not one of the table's three soil types.
    """
    if not soil_type:
        return [dict(row) for row in _TABLE_7_3]

    key = soil_type.lower().strip()
    valid = ("cohesionless", "cohesive", "mixed")
    if key not in valid:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. GEC-12 Table 7-3 (p. 228) "
            f"lists its methods under: {', '.join(valid)}")
    return [dict(row) for row in _TABLE_7_3 if row["soil_type"] == key]


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
        Soil-pile friction angle (degrees): 15, 20, 25, 30, or 35, the
        printed rows (p. 253, PDF page 299), each given for density classes
        and soils. A value between rows is interpolated linearly, which the
        table does not print; the result then carries a "note".

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
        "note": ("Interpolated between Table 7-8's rows (p. 253), which it "
                 "prints only at delta 15, 20, 25, 30 and 35 deg, each for "
                 "density classes and soils; the interpolation is not "
                 "printed."),
    }
