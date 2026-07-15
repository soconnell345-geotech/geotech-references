"""Eurocode 7 (EN 1997-1:2004) table lookup functions.

Digitized tables from Annex A (normative) "Partial and correlation factors
for ultimate limit states and recommended values" [source PDF pages 130-139,
0-based pdf_page_index 129-138], plus Annex G Table G.1 (rock grouping for
presumed bearing resistance, pdf_page_index 164) and Annex H limiting relative
rotation guidance (pdf_page_index 166).  Follows the DM7/micropile pattern:
private data with ``_TABLE_*`` prefix, public lookup functions with
string-matched keys.

All values are the RECOMMENDED values given in EN 1997-1:2004.  A National
Annex may set different values for use in a specific country; these functions
return the base-standard recommended values only.

OCR note on the source PDF
---------------------------
The source PDF (a public.resource.org scan of BS EN 1997-1:2004) has a text
layer produced by OCR that systematically drops the leading digit/comma of
factor values in several places (e.g. "1,35" -> "1" ) and loses some column
headers in the four-column Annex A resistance tables.  Every value below was
cross-checked against (a) the surviving OCR fragments -- which for every table
agree at least partially -- and (b) internal consistency (monotonic trends
across correlation-factor columns, exact repetition of the R1/R2/R3/R4
structure across Tables A.6/A.7/A.8).  No value here required an outright
guess; where the OCR was ambiguous this is noted in the specific function's
docstring.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table A.1 (pdf p.130, idx 129): Partial factors on actions (gamma_F) for
# equilibrium limit state (EQU) verification.
# ============================================================================

_TABLE_A_1 = {
    ("permanent", "unfavourable"): 1.1,   # gamma_G;dst
    ("permanent", "favourable"): 0.9,     # gamma_G;stb
    ("variable", "unfavourable"): 1.5,    # gamma_Q;dst
    ("variable", "favourable"): 0.0,      # gamma_Q;stb
}


def table_a_1_equ_actions(action: str = "permanent",
                          condition: str = "unfavourable") -> float:
    """Partial factors on actions (gamma_F) for EQU verification (Table A.1).

    Parameters
    ----------
    action : str
        'permanent' or 'variable'.
    condition : str
        'unfavourable' (destabilising) or 'favourable' (stabilising).

    Returns
    -------
    float
        Partial factor gamma_F.

    Raises
    ------
    ValueError
        If action or condition is not recognized.
    """
    a = action.strip().lower()
    c = condition.strip().lower()
    key = (a, c)
    if key not in _TABLE_A_1:
        raise ValueError(
            f"Unknown (action, condition) = ({action}, {condition}). "
            f"Valid actions: permanent, variable. "
            f"Valid conditions: unfavourable, favourable."
        )
    return _TABLE_A_1[key]


# ============================================================================
# Table A.2 (pdf p.131, idx 130): Partial factors for soil parameters
# (gamma_M) for EQU verification.
# ============================================================================

_TABLE_A_2 = {
    "phi": 1.25,       # gamma_phi', applied to tan(phi')
    "c": 1.25,         # gamma_c' (effective cohesion)
    "cu": 1.4,         # gamma_cu (undrained shear strength)
    "qu": 1.4,         # gamma_qu (unconfined strength)
    "gamma": 1.0,      # gamma_gamma (weight density)
}

_TABLE_A_2_ALIASES = {
    "phi'": "phi", "tan_phi": "phi", "friction_angle": "phi",
    "c'": "c", "cohesion": "c", "effective_cohesion": "c",
    "undrained_shear_strength": "cu", "su": "cu",
    "unconfined_strength": "qu",
    "unit_weight": "gamma", "weight_density": "gamma",
}


def table_a_2_equ_soil_parameters(parameter: str = "phi") -> float:
    """Partial factors for soil parameters (gamma_M) for EQU verification (Table A.2).

    Parameters
    ----------
    parameter : str
        One of 'phi' (tan of shearing resistance angle), 'c' (effective
        cohesion), 'cu' (undrained shear strength), 'qu' (unconfined
        strength), 'gamma' (weight density).  Common aliases accepted.

    Returns
    -------
    float
        Partial factor gamma_M.
    """
    key = _TABLE_A_2_ALIASES.get(parameter.strip().lower(), parameter.strip().lower())
    if key not in _TABLE_A_2:
        raise ValueError(
            f"Unknown parameter '{parameter}'. "
            f"Valid: {', '.join(sorted(_TABLE_A_2.keys()))}"
        )
    return _TABLE_A_2[key]


# ============================================================================
# Table A.3 (pdf p.132, idx 131): Partial factors on actions (gamma_F) or
# effects of actions (gamma_E) for STR/GEO verification, sets A1 and A2.
# ============================================================================

_TABLE_A_3 = {
    ("permanent", "unfavourable", "a1"): 1.35,
    ("permanent", "favourable", "a1"): 1.0,
    ("variable", "unfavourable", "a1"): 1.5,
    ("variable", "favourable", "a1"): 0.0,
    ("permanent", "unfavourable", "a2"): 1.0,
    ("permanent", "favourable", "a2"): 1.0,
    ("variable", "unfavourable", "a2"): 1.3,
    ("variable", "favourable", "a2"): 0.0,
}


def table_a_3_str_geo_actions(action: str = "permanent",
                              condition: str = "unfavourable",
                              factor_set: str = "A1") -> float:
    """Partial factors on actions (gamma_F) for STR/GEO verification (Table A.3).

    Parameters
    ----------
    action : str
        'permanent' or 'variable'.
    condition : str
        'unfavourable' or 'favourable'.
    factor_set : str
        'A1' or 'A2'.  Design Approach 1 Combination 1 uses A1; Design
        Approach 1 Combination 2 and Design Approach 2 use A1 for actions in
        DA2, A2 for DA1-C2; Design Approach 3 uses A1 on structural actions
        or A2 on geotechnical actions (see design_approach_sets()).

    Returns
    -------
    float
        Partial factor gamma_F / gamma_E.
    """
    key = (action.strip().lower(), condition.strip().lower(),
           factor_set.strip().lower())
    if key not in _TABLE_A_3:
        raise ValueError(
            f"Unknown combination action={action}, condition={condition}, "
            f"factor_set={factor_set}. Valid factor_set: A1, A2."
        )
    return _TABLE_A_3[key]


# ============================================================================
# Table A.4 (pdf p.132, idx 131): Partial factors for soil parameters
# (gamma_M), sets M1 and M2.
# ============================================================================

_TABLE_A_4 = {
    ("phi", "m1"): 1.0, ("phi", "m2"): 1.25,
    ("c", "m1"): 1.0, ("c", "m2"): 1.25,
    ("cu", "m1"): 1.0, ("cu", "m2"): 1.4,
    ("qu", "m1"): 1.0, ("qu", "m2"): 1.4,
    ("gamma", "m1"): 1.0, ("gamma", "m2"): 1.0,
}


def table_a_4_str_geo_soil_parameters(parameter: str = "phi",
                                      factor_set: str = "M1") -> float:
    """Partial factors for soil parameters (gamma_M) for STR/GEO verification (Table A.4).

    Parameters
    ----------
    parameter : str
        'phi', 'c', 'cu', 'qu', or 'gamma' (aliases per Table A.2 accepted).
    factor_set : str
        'M1' or 'M2'.

    Returns
    -------
    float
        Partial factor gamma_M.
    """
    p = _TABLE_A_2_ALIASES.get(parameter.strip().lower(), parameter.strip().lower())
    fs = factor_set.strip().lower()
    key = (p, fs)
    if key not in _TABLE_A_4:
        raise ValueError(
            f"Unknown parameter='{parameter}' or factor_set='{factor_set}'. "
            f"Valid parameters: phi, c, cu, qu, gamma. Valid sets: M1, M2."
        )
    return _TABLE_A_4[key]


# ============================================================================
# Table A.5 (pdf p.133, idx 132): Partial resistance factors (gamma_R) for
# spread foundations, sets R1, R2, R3.
# ============================================================================

_TABLE_A_5 = {
    ("bearing", "r1"): 1.0, ("bearing", "r2"): 1.4, ("bearing", "r3"): 1.0,
    ("sliding", "r1"): 1.0, ("sliding", "r2"): 1.1, ("sliding", "r3"): 1.0,
}


def table_a_5_spread_foundation_resistance(resistance: str = "bearing",
                                           factor_set: str = "R1") -> float:
    """Partial resistance factors (gamma_R) for spread foundations (Table A.5).

    Parameters
    ----------
    resistance : str
        'bearing' (gamma_R;v) or 'sliding' (gamma_R;h).
    factor_set : str
        'R1', 'R2', or 'R3'.

    Returns
    -------
    float
        Partial resistance factor.
    """
    key = (resistance.strip().lower(), factor_set.strip().lower())
    if key not in _TABLE_A_5:
        raise ValueError(
            f"Unknown resistance='{resistance}' or factor_set='{factor_set}'. "
            f"Valid resistance: bearing, sliding. Valid sets: R1, R2, R3."
        )
    return _TABLE_A_5[key]


# ============================================================================
# Tables A.6/A.7/A.8 (pdf p.134, idx 133): Partial resistance factors
# (gamma_R) for driven, bored, and CFA piles, sets R1-R4.
#
# OCR note: the R4 column of each table was extracted by PyMuPDF as a
# trailing run of 4 numbers below the main R1/R2/R3 rows (a column-order
# artifact of the source PDF's narrow 4-column table layout), rather than
# alongside its row.  Values below reassemble the intended row/column
# structure and match the well-published EN 1997-1:2004 Annex A values.
# ============================================================================

_TABLE_A_6_DRIVEN = {
    ("base", "r1"): 1.0, ("base", "r2"): 1.1, ("base", "r3"): 1.0, ("base", "r4"): 1.3,
    ("shaft_compression", "r1"): 1.0, ("shaft_compression", "r2"): 1.1,
    ("shaft_compression", "r3"): 1.0, ("shaft_compression", "r4"): 1.3,
    ("total_compression", "r1"): 1.0, ("total_compression", "r2"): 1.1,
    ("total_compression", "r3"): 1.0, ("total_compression", "r4"): 1.3,
    ("shaft_tension", "r1"): 1.25, ("shaft_tension", "r2"): 1.15,
    ("shaft_tension", "r3"): 1.1, ("shaft_tension", "r4"): 1.6,
}

_TABLE_A_7_BORED = {
    # R4 base/total verified against the rendered page image (pdf idx 133;
    # printed p.132) during lead QC 2026-07-15 — the OCR-scrambled column had
    # been mis-reconstructed as 1.3/1.3.
    ("base", "r1"): 1.25, ("base", "r2"): 1.1, ("base", "r3"): 1.0, ("base", "r4"): 1.6,
    ("shaft_compression", "r1"): 1.0, ("shaft_compression", "r2"): 1.1,
    ("shaft_compression", "r3"): 1.0, ("shaft_compression", "r4"): 1.3,
    ("total_compression", "r1"): 1.15, ("total_compression", "r2"): 1.1,
    ("total_compression", "r3"): 1.0, ("total_compression", "r4"): 1.5,
    ("shaft_tension", "r1"): 1.25, ("shaft_tension", "r2"): 1.15,
    ("shaft_tension", "r3"): 1.1, ("shaft_tension", "r4"): 1.6,
}

_TABLE_A_8_CFA = {
    # R4 base verified against the rendered page image (pdf idx 133) during
    # lead QC 2026-07-15 — was mis-reconstructed as 1.3.
    ("base", "r1"): 1.1, ("base", "r2"): 1.1, ("base", "r3"): 1.0, ("base", "r4"): 1.45,
    ("shaft_compression", "r1"): 1.0, ("shaft_compression", "r2"): 1.1,
    ("shaft_compression", "r3"): 1.0, ("shaft_compression", "r4"): 1.3,
    ("total_compression", "r1"): 1.1, ("total_compression", "r2"): 1.1,
    ("total_compression", "r3"): 1.0, ("total_compression", "r4"): 1.4,
    ("shaft_tension", "r1"): 1.25, ("shaft_tension", "r2"): 1.15,
    ("shaft_tension", "r3"): 1.1, ("shaft_tension", "r4"): 1.6,
}

_PILE_RESISTANCE_KEYS = ("base", "shaft_compression", "total_compression",
                          "shaft_tension")
_PILE_RESISTANCE_ALIASES = {
    "shaft": "shaft_compression", "shaft_comp": "shaft_compression",
    "total": "total_compression", "combined": "total_compression",
    "tension": "shaft_tension", "shaft_uplift": "shaft_tension",
    "uplift": "shaft_tension",
}


def _pile_resistance_lookup(table: dict, table_name: str,
                            resistance: str, factor_set: str) -> float:
    r = _PILE_RESISTANCE_ALIASES.get(resistance.strip().lower(),
                                      resistance.strip().lower())
    fs = factor_set.strip().lower()
    key = (r, fs)
    if key not in table:
        raise ValueError(
            f"Unknown resistance='{resistance}' or factor_set='{factor_set}' "
            f"for {table_name}. Valid resistance: {', '.join(_PILE_RESISTANCE_KEYS)}. "
            f"Valid sets: R1, R2, R3, R4."
        )
    return table[key]


def table_a_6_driven_pile_resistance(resistance: str = "base",
                                     factor_set: str = "R1") -> float:
    """Partial resistance factors (gamma_R) for driven piles (Table A.6).

    Parameters
    ----------
    resistance : str
        'base' (gamma_b), 'shaft_compression' (gamma_s), 'total_compression'
        (gamma_t), or 'shaft_tension' (gamma_s;t).
    factor_set : str
        'R1', 'R2', 'R3', or 'R4'.

    Returns
    -------
    float
        Partial resistance factor.
    """
    return _pile_resistance_lookup(_TABLE_A_6_DRIVEN, "Table A.6 (driven piles)",
                                   resistance, factor_set)


def table_a_7_bored_pile_resistance(resistance: str = "base",
                                    factor_set: str = "R1") -> float:
    """Partial resistance factors (gamma_R) for bored piles (Table A.7).

    Parameters
    ----------
    resistance : str
        'base', 'shaft_compression', 'total_compression', or 'shaft_tension'.
    factor_set : str
        'R1', 'R2', 'R3', or 'R4'.

    Returns
    -------
    float
        Partial resistance factor.
    """
    return _pile_resistance_lookup(_TABLE_A_7_BORED, "Table A.7 (bored piles)",
                                   resistance, factor_set)


def table_a_8_cfa_pile_resistance(resistance: str = "base",
                                  factor_set: str = "R1") -> float:
    """Partial resistance factors (gamma_R) for CFA piles (Table A.8).

    Continuous flight auger piles.

    Parameters
    ----------
    resistance : str
        'base', 'shaft_compression', 'total_compression', or 'shaft_tension'.
    factor_set : str
        'R1', 'R2', 'R3', or 'R4'.

    Returns
    -------
    float
        Partial resistance factor.
    """
    return _pile_resistance_lookup(_TABLE_A_8_CFA, "Table A.8 (CFA piles)",
                                   resistance, factor_set)


# ============================================================================
# Table A.9 (pdf p.135, idx 134): Correlation factors (xi) to derive
# characteristic pile resistance from STATIC load tests, by number of piles
# tested n.
# ============================================================================

_TABLE_A_9_N = [1, 2, 3, 4, 5]
_TABLE_A_9_MEAN = [1.40, 1.30, 1.20, 1.10, 1.00]   # xi_1
_TABLE_A_9_MIN = [1.40, 1.20, 1.05, 1.00, 1.00]    # xi_2


def table_a_9_correlation_static_load_test(factor: str = "mean",
                                           n: int = 1) -> float:
    """Correlation factors (xi) for static pile load tests (Table A.9).

    Parameters
    ----------
    factor : str
        'mean' (xi_1, applied to the mean of measured resistances) or 'min'
        (xi_2, applied to the minimum of measured resistances).
    n : int
        Number of piles tested, 1 to 5 (n >= 5 uses the n=5 value, per the
        source table's ">= 5" column).

    Returns
    -------
    float
        Correlation factor xi.
    """
    f = factor.strip().lower()
    if f not in ("mean", "min"):
        raise ValueError(f"Unknown factor '{factor}'. Valid: mean, min.")
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    n_eff = min(n, 5)
    series = _TABLE_A_9_MEAN if f == "mean" else _TABLE_A_9_MIN
    return series[_TABLE_A_9_N.index(n_eff)]


# ============================================================================
# Table A.10 (pdf p.135, idx 134): Correlation factors (xi) to derive
# characteristic pile resistance from GROUND TEST profiles, by number of
# profiles n.
# ============================================================================

_TABLE_A_10_N = [1, 2, 3, 4, 5, 7, 10]
_TABLE_A_10_MEAN = [1.40, 1.35, 1.33, 1.31, 1.29, 1.27, 1.25]   # xi_3
_TABLE_A_10_MIN = [1.40, 1.27, 1.23, 1.20, 1.15, 1.12, 1.08]    # xi_4


def table_a_10_correlation_ground_test(factor: str = "mean",
                                       n: int = 1) -> float:
    """Correlation factors (xi) for characteristic resistance from ground test
    profiles (Table A.10).

    Parameters
    ----------
    factor : str
        'mean' (xi_3) or 'min' (xi_4).
    n : int
        Number of ground test profiles, 1 to 10.  Intermediate n values
        (e.g. 6, 8, 9) are linearly interpolated between the table's
        tabulated points (1,2,3,4,5,7,10); n > 10 uses the n=10 value.

    Returns
    -------
    float
        Correlation factor xi.
    """
    f = factor.strip().lower()
    if f not in ("mean", "min"):
        raise ValueError(f"Unknown factor '{factor}'. Valid: mean, min.")
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    n_eff = min(n, 10)
    series = _TABLE_A_10_MEAN if f == "mean" else _TABLE_A_10_MIN
    if n_eff in _TABLE_A_10_N:
        return series[_TABLE_A_10_N.index(n_eff)]
    return _linterp(n_eff, _TABLE_A_10_N, series)


# ============================================================================
# Table A.11 (pdf p.136, idx 135): Correlation factors (xi) to derive
# characteristic pile resistance from DYNAMIC IMPACT tests, by number of
# piles tested n, with optional model factors per footnotes b-d.
# ============================================================================

_TABLE_A_11_N = [2, 5, 10, 15, 20]
_TABLE_A_11_MEAN = [1.60, 1.50, 1.45, 1.42, 1.40]   # xi_5
_TABLE_A_11_MIN = [1.50, 1.35, 1.30, 1.25, 1.25]    # xi_6

_TABLE_A_11_MODEL_FACTORS = {
    "signal_matching": 0.85,
    "formula_with_measurement": 1.10,
    "formula_without_measurement": 1.20,
}


def table_a_11_correlation_dynamic_impact_test(factor: str = "mean",
                                               n: int = 2,
                                               model_factor: str = None) -> float:
    """Correlation factors (xi) for dynamic impact pile tests (Table A.11).

    Parameters
    ----------
    factor : str
        'mean' (xi_5) or 'min' (xi_6).
    n : int
        Number of piles tested, 2 to 20 (n < 2 raises; n > 20 uses n=20;
        intermediate values are linearly interpolated between 2,5,10,15,20).
    model_factor : str, optional
        Additional model factor per the table footnotes: 'signal_matching'
        (x0.85, for dynamic impact tests with signal matching),
        'formula_with_measurement' (x1.10, pile driving formula with
        measured quasi-elastic pile head displacement), or
        'formula_without_measurement' (x1.20, pile driving formula without
        that measurement).  If None (default), no model factor is applied.

    Returns
    -------
    float
        Correlation factor xi, times the model factor if given.

    Raises
    ------
    ValueError
        If factor, n, or model_factor is invalid.
    """
    f = factor.strip().lower()
    if f not in ("mean", "min"):
        raise ValueError(f"Unknown factor '{factor}'. Valid: mean, min.")
    if n < 2:
        raise ValueError(f"n must be >= 2, got {n}")
    n_eff = min(n, 20)
    series = _TABLE_A_11_MEAN if f == "mean" else _TABLE_A_11_MIN
    if n_eff in _TABLE_A_11_N:
        xi = series[_TABLE_A_11_N.index(n_eff)]
    else:
        xi = _linterp(n_eff, _TABLE_A_11_N, series)

    if model_factor is not None:
        mf_key = model_factor.strip().lower()
        if mf_key not in _TABLE_A_11_MODEL_FACTORS:
            raise ValueError(
                f"Unknown model_factor '{model_factor}'. Valid: "
                f"{', '.join(_TABLE_A_11_MODEL_FACTORS.keys())}"
            )
        xi *= _TABLE_A_11_MODEL_FACTORS[mf_key]
    return xi


# ============================================================================
# Table A.12 (pdf p.136, idx 135): Partial resistance factors (gamma_R) for
# pre-stressed anchorages, sets R1-R4.
# ============================================================================

_TABLE_A_12 = {
    ("temporary", "r1"): 1.1, ("temporary", "r2"): 1.1,
    ("temporary", "r3"): 1.0, ("temporary", "r4"): 1.1,
    ("permanent", "r1"): 1.1, ("permanent", "r2"): 1.1,
    ("permanent", "r3"): 1.0, ("permanent", "r4"): 1.1,
}


def table_a_12_anchorage_resistance(anchorage_type: str = "temporary",
                                    factor_set: str = "R1") -> float:
    """Partial resistance factors (gamma_R) for pre-stressed anchorages (Table A.12).

    Parameters
    ----------
    anchorage_type : str
        'temporary' (gamma_a;t) or 'permanent' (gamma_a;p).
    factor_set : str
        'R1', 'R2', 'R3', or 'R4'.

    Returns
    -------
    float
        Partial resistance factor.
    """
    key = (anchorage_type.strip().lower(), factor_set.strip().lower())
    if key not in _TABLE_A_12:
        raise ValueError(
            f"Unknown anchorage_type='{anchorage_type}' or factor_set="
            f"'{factor_set}'. Valid types: temporary, permanent. "
            f"Valid sets: R1, R2, R3, R4."
        )
    return _TABLE_A_12[key]


# ============================================================================
# Table A.13 (pdf p.137, idx 136): Partial resistance factors (gamma_R) for
# retaining structures, sets R1-R3.
# ============================================================================

_TABLE_A_13 = {
    ("bearing", "r1"): 1.0, ("bearing", "r2"): 1.4, ("bearing", "r3"): 1.0,
    ("sliding", "r1"): 1.0, ("sliding", "r2"): 1.1, ("sliding", "r3"): 1.0,
    ("earth_resistance", "r1"): 1.0, ("earth_resistance", "r2"): 1.4,
    ("earth_resistance", "r3"): 1.0,
}


def table_a_13_retaining_structure_resistance(resistance: str = "bearing",
                                              factor_set: str = "R1") -> float:
    """Partial resistance factors (gamma_R) for retaining structures (Table A.13).

    Parameters
    ----------
    resistance : str
        'bearing' (gamma_R;v), 'sliding' (gamma_R;h), or 'earth_resistance'
        (gamma_R;e).
    factor_set : str
        'R1', 'R2', or 'R3'.

    Returns
    -------
    float
        Partial resistance factor.
    """
    key = (resistance.strip().lower(), factor_set.strip().lower())
    if key not in _TABLE_A_13:
        raise ValueError(
            f"Unknown resistance='{resistance}' or factor_set='{factor_set}'. "
            f"Valid resistance: bearing, sliding, earth_resistance. "
            f"Valid sets: R1, R2, R3."
        )
    return _TABLE_A_13[key]


# ============================================================================
# Table A.14 (pdf p.137, idx 136): Partial resistance factor (gamma_R;e) for
# slopes and overall stability, sets R1-R3.
# ============================================================================

_TABLE_A_14 = {"r1": 1.0, "r2": 1.1, "r3": 1.0}


def table_a_14_slope_stability_resistance(factor_set: str = "R1") -> float:
    """Partial resistance factor (gamma_R;e) for slopes and overall stability (Table A.14).

    Parameters
    ----------
    factor_set : str
        'R1', 'R2', or 'R3'.

    Returns
    -------
    float
        Partial resistance factor on earth resistance.
    """
    key = factor_set.strip().lower()
    if key not in _TABLE_A_14:
        raise ValueError(
            f"Unknown factor_set '{factor_set}'. Valid: R1, R2, R3."
        )
    return _TABLE_A_14[key]


# ============================================================================
# Table A.15 (pdf p.138, idx 137): Partial factors on actions (gamma_F) for
# uplift limit state (UPL) verification.
# ============================================================================

_TABLE_A_15 = {
    ("permanent", "unfavourable"): 1.0,   # gamma_G;dst
    ("permanent", "favourable"): 0.9,     # gamma_G;stb
    ("variable", "unfavourable"): 1.5,    # gamma_Q;dst
}


def table_a_15_upl_actions(action: str = "permanent",
                           condition: str = "unfavourable") -> float:
    """Partial factors on actions (gamma_F) for UPL verification (Table A.15).

    Parameters
    ----------
    action : str
        'permanent' or 'variable'.  (No favourable variable action factor is
        given in the standard for UPL -- destabilising variable actions only.)
    condition : str
        'unfavourable' or 'favourable'.

    Returns
    -------
    float
        Partial factor gamma_F.
    """
    key = (action.strip().lower(), condition.strip().lower())
    if key not in _TABLE_A_15:
        raise ValueError(
            f"Unknown (action, condition) = ({action}, {condition}) for "
            f"Table A.15. Valid: (permanent, unfavourable), "
            f"(permanent, favourable), (variable, unfavourable)."
        )
    return _TABLE_A_15[key]


# ============================================================================
# Table A.16 (pdf p.139, idx 138): Partial factors for soil parameters and
# resistances for uplift limit state (UPL) verification.
# ============================================================================

_TABLE_A_16 = {
    "phi": 1.25,             # gamma_phi' (applied to tan phi')
    "c": 1.25,               # gamma_c'
    "cu": 1.40,               # gamma_cu
    "shaft_tension": 1.40,    # gamma_s;t (tensile pile resistance)
    "anchorage": 1.40,        # gamma_a (anchorage resistance)
}

_TABLE_A_16_ALIASES = dict(_TABLE_A_2_ALIASES)
_TABLE_A_16_ALIASES.update({
    "tensile_pile_resistance": "shaft_tension",
    "pile_tension": "shaft_tension",
    "anchorage_resistance": "anchorage",
})


def table_a_16_upl_soil_resistance(parameter: str = "phi") -> float:
    """Partial factors for soil parameters/resistances for UPL verification (Table A.16).

    Parameters
    ----------
    parameter : str
        'phi', 'c', 'cu', 'shaft_tension' (tensile pile resistance), or
        'anchorage' (anchorage resistance).

    Returns
    -------
    float
        Partial factor.
    """
    key = _TABLE_A_16_ALIASES.get(parameter.strip().lower(), parameter.strip().lower())
    if key not in _TABLE_A_16:
        raise ValueError(
            f"Unknown parameter '{parameter}'. "
            f"Valid: {', '.join(sorted(_TABLE_A_16.keys()))}"
        )
    return _TABLE_A_16[key]


# ============================================================================
# Table A.17 (pdf p.139, idx 138): Partial factors on actions (gamma_F) for
# hydraulic heave limit state (HYD) verification.
# ============================================================================

_TABLE_A_17 = {
    ("permanent", "unfavourable"): 1.35,   # gamma_G;dst
    ("permanent", "favourable"): 0.90,     # gamma_G;stb
    ("variable", "unfavourable"): 1.50,    # gamma_Q;dst
}


def table_a_17_hyd_actions(action: str = "permanent",
                           condition: str = "unfavourable") -> float:
    """Partial factors on actions (gamma_F) for HYD verification (Table A.17).

    Parameters
    ----------
    action : str
        'permanent' or 'variable'.
    condition : str
        'unfavourable' or 'favourable'.

    Returns
    -------
    float
        Partial factor gamma_F.
    """
    key = (action.strip().lower(), condition.strip().lower())
    if key not in _TABLE_A_17:
        raise ValueError(
            f"Unknown (action, condition) = ({action}, {condition}) for "
            f"Table A.17. Valid: (permanent, unfavourable), "
            f"(permanent, favourable), (variable, unfavourable)."
        )
    return _TABLE_A_17[key]


# ============================================================================
# Design Approach combinations (2.4.7.3.4, pdf idx 33-34): which Annex A
# action/material/resistance sets apply to each Design Approach.
# ============================================================================

_DESIGN_APPROACHES = {
    "da1-c1": {
        "description": "Design Approach 1, Combination 1: A1 + M1 + R1",
        "action_set": "A1", "material_set": "M1", "resistance_set": "R1",
    },
    "da1-c2": {
        "description": (
            "Design Approach 1, Combination 2: A2 + M2 + R1 "
            "(except axially loaded piles/anchors: A2 + (M1 or M2) + R4)"
        ),
        "action_set": "A2", "material_set": "M2", "resistance_set": "R1",
        "pile_anchor_material_set": "M1 or M2",
        "pile_anchor_resistance_set": "R4",
    },
    "da2": {
        "description": "Design Approach 2: A1 + M1 + R2",
        "action_set": "A1", "material_set": "M1", "resistance_set": "R2",
    },
    "da3": {
        "description": (
            "Design Approach 3: (A1 on structural actions, or A2 on "
            "geotechnical actions) + M2 + R3"
        ),
        "structural_action_set": "A1", "geotechnical_action_set": "A2",
        "material_set": "M2", "resistance_set": "R3",
    },
}

_DESIGN_APPROACH_ALIASES = {
    "da1": "da1-c1", "da1c1": "da1-c1", "da1_c1": "da1-c1",
    "combination1": "da1-c1", "combination_1": "da1-c1",
    "da1c2": "da1-c2", "da1_c2": "da1-c2",
    "combination2": "da1-c2", "combination_2": "da1-c2",
    "da_2": "da2", "designapproach2": "da2",
    "da_3": "da3", "designapproach3": "da3",
}


def design_approach_sets(approach: str = "DA1-C1") -> dict:
    """Annex A action/material/resistance sets used by each Design Approach (2.4.7.3.4).

    Parameters
    ----------
    approach : str
        One of 'DA1-C1', 'DA1-C2', 'DA2', 'DA3' (case-insensitive; 'DA1' is
        accepted as an alias for 'DA1-C1').

    Returns
    -------
    dict
        Keys vary by approach: 'description' plus 'action_set'/
        'material_set'/'resistance_set' for DA1-C1 and DA2; for DA1-C2 also
        'pile_anchor_material_set'/'pile_anchor_resistance_set'; for DA3
        'structural_action_set'/'geotechnical_action_set' instead of a
        single 'action_set'.

    Raises
    ------
    ValueError
        If approach is not recognized.
    """
    key = approach.strip().lower().replace(" ", "")
    key = _DESIGN_APPROACH_ALIASES.get(key, key)
    if key not in _DESIGN_APPROACHES:
        raise ValueError(
            f"Unknown design approach '{approach}'. "
            f"Valid: DA1-C1, DA1-C2, DA2, DA3."
        )
    return dict(_DESIGN_APPROACHES[key])


# ============================================================================
# Table G.1 (pdf p.164-165, idx 164): Grouping of weak and broken rocks for
# presumed bearing resistance (Annex G, informative).  Figure G.1 itself is
# a nomograph (qu vs. discontinuity spacing) and is not digitized here -- see
# figures_catalog.json for the read-off entry.
# ============================================================================

_TABLE_G_1 = {
    1: [
        "Pure limestones and dolomites",
        "Carbonate sandstones of low porosity",
    ],
    2: [
        "Igneous",
        "Oolitic and marly limestones",
        "Well cemented sandstones",
        "Indurated carbonate mudstones",
        "Metamorphic rocks, including slates and schist (flat cleavage/foliation)",
    ],
    3: [
        "Very marly limestones",
        "Poorly cemented sandstones",
        "Slates and schists (steep cleavage/foliation)",
    ],
    4: [
        "Uncemented mudstones and shales",
    ],
}


def table_g_1_rock_group(rock_type: str) -> dict:
    """Weak/broken rock grouping for presumed bearing resistance (Table G.1).

    Used with Figure G.1 (a nomograph of qu vs. discontinuity spacing, not
    digitized -- see figures_catalog.json) to derive presumed bearing
    resistance for spread foundations on weak/broken rock with tight joints
    (incl. chalk with porosity < 35%), for settlements up to 0.5% of
    foundation width.

    Parameters
    ----------
    rock_type : str
        A rock description; matched case-insensitively as a substring
        against the Table G.1 entries (e.g. 'limestone', 'sandstone',
        'shale', 'schist', 'igneous').

    Returns
    -------
    dict
        Keys: rock_type (the matched description), group (1-4, 1 = strongest
        grouping).

    Raises
    ------
    ValueError
        If rock_type does not match any Table G.1 entry.
    """
    q = rock_type.strip().lower()
    matches = []
    for group, entries in _TABLE_G_1.items():
        for entry in entries:
            if q in entry.lower():
                matches.append((entry, group))
    if not matches:
        all_entries = [e for entries in _TABLE_G_1.values() for e in entries]
        raise ValueError(
            f"Unknown rock_type '{rock_type}'. Valid Table G.1 entries: "
            f"{', '.join(all_entries)}"
        )
    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous rock_type '{rock_type}'. Matches: "
            f"{', '.join(f'{e} (Group {g})' for e, g in matches)}"
        )
    entry, group = matches[0]
    return {"rock_type": entry, "group": group}


# ============================================================================
# Annex H (pdf p.166-167, idx 166): Limiting values of structural deformation
# and foundation movement (informative guidance, not a numbered table in the
# source -- values are hand-tabulated from Annex H(2)-(4) narrative text).
# ============================================================================

_TABLE_H_1_RELATIVE_ROTATION_SAGGING = {
    "range_min": 1.0 / 2000,
    "range_max": 1.0 / 300,
    "acceptable_many_structures": 1.0 / 500,
    "ultimate_limit_state": 1.0 / 150,
}


def table_h_1_limiting_relative_rotation(limit_type: str = "acceptable_many_structures",
                                         mode: str = "sagging") -> float:
    """Limiting relative rotation (angular distortion) for foundation movement (Annex H(2)-(3)).

    Parameters
    ----------
    limit_type : str
        'range_min' (1/2000, most restrictive end of the general range),
        'range_max' (1/300, least restrictive end of the general range),
        'acceptable_many_structures' (1/500, stated as acceptable for many
        structures), or 'ultimate_limit_state' (1/150, likely to cause a
        structural ULS).
    mode : str
        'sagging' (values as given, per Annex H Figure H.1) or 'hogging'
        (Annex H(3): halve the sagging-mode value when the edge settles
        more than the middle).

    Returns
    -------
    float
        Limiting relative rotation, dimensionless (e.g. 0.002 for 1/500).

    Raises
    ------
    ValueError
        If limit_type or mode is not recognized.
    """
    key = limit_type.strip().lower()
    if key not in _TABLE_H_1_RELATIVE_ROTATION_SAGGING:
        raise ValueError(
            f"Unknown limit_type '{limit_type}'. Valid: "
            f"{', '.join(_TABLE_H_1_RELATIVE_ROTATION_SAGGING.keys())}"
        )
    m = mode.strip().lower()
    if m not in ("sagging", "hogging"):
        raise ValueError(f"Unknown mode '{mode}'. Valid: sagging, hogging.")
    value = _TABLE_H_1_RELATIVE_ROTATION_SAGGING[key]
    return value / 2 if m == "hogging" else value


def table_h_2_limiting_total_settlement() -> float:
    """Typical acceptable total settlement for isolated foundations (Annex H(4)).

    Returns
    -------
    float
        0.050 (50 mm), the total settlement often acceptable for normal
        structures with isolated foundations, per Annex H(4) -- provided
        relative rotations remain within acceptable limits and services are
        not affected.  Larger settlements may still be acceptable if those
        conditions hold.
    """
    return 0.050
