"""EM 1110-2-2107 Chapter 4 -- Design (design basis, loads, load factors,
load combinations, earthquake load combinations).

The basic LRFD safety check with a HSS-specific performance factor
(Eq 4.1), the load inventory (paragraph 4.2), the full minimum-load-factor
table (Table 4.1), the general LRFD load-combination equation (Eq 4.2), and
the three earthquake load combinations (Eq 4.7/4.8/4.9). Printed pages per
the 1 August 2022 edition (pdf_page = printed_page + 8).

For the HSS-support seismic-acceleration amplification (Eq 4.3-4.6,
Table 4.2, and the full Appendix D pseudo-dynamic derivation + validated
worked example), see ``seismic_amplification.py``.

This manual's Chapter 4 is predominantly LOADS AND LOAD FACTORS -- unlike
EM 1110-2-2104 (which amends ACI 318-19's member-design equations), this
manual does NOT reprint AISC 360 member-capacity equations; Chapter 4
explicitly states "Design equations for individual HSS are provided in
Chapters 9-16" and members/connections are designed to AISC 360 directly
(paragraph 1.8, Appendix B commentary B.4.1). The closed-form,
generalizable equations this manual DOES print are almost all in Chapter
10 + Appendix F (Tainter-gate loads: side-seal friction, wire-rope loads,
hydrostatic-load integration, trunnion friction) -- see
``tainter_gate_loads.py``.
"""

# ============================================================================
# Eq 4.1 -- basic LRFD safety check (printed p. 17, pdf_page 25)
# ============================================================================

def required_strength_check(u_demand, phi, rn_nominal, alpha=1.0):
    """Eq 4.1: sum(gamma_i * Qni) <= alpha*phi*Rn, the basic LRFD safety
    check (printed p. 17).

    Parameters
    ----------
    u_demand : float
        U = sum(gamma_i * Qni), the factored-load demand (from
        ``load_combination_lrfd`` or an earthquake combination).
    phi : float
        AISC resistance factor for the limit state (paragraph 4.1: "These
        are provided in AISC, except the resistance factor for forged and
        cast materials, which is 0.7").
    rn_nominal : float
        Nominal resistance per AISC.
    alpha : float, optional
        Performance factor (``performance_factor``); default 1.0.

    Returns
    -------
    dict
        {'u_demand', 'alpha_phi_rn', 'adequate' (bool), 'equation': '4.1',
         'printed_page': '17', 'pdf_page': 25}
    """
    alpha_phi_rn = alpha * phi * rn_nominal
    return {
        "u_demand": u_demand, "alpha": alpha, "phi": phi, "rn_nominal": rn_nominal,
        "alpha_phi_rn": alpha_phi_rn, "adequate": u_demand <= alpha_phi_rn,
        "equation": "4.1", "printed_page": "17", "pdf_page": 25,
    }


def performance_factor(override=None):
    """Paragraph 4.1.1: the HSS performance factor alpha, applied to AISC
    resistance factors (printed p. 17).

        alpha = 1.0, except alpha = 0.90 "for the following structures"

    NOTE -- source-document gap: paragraph 4.1.1's sentence "The value of
    alpha is 1.0 except for the following structures where alpha must be
    0.90" is not followed by any enumerated list on the printed page (the
    paragraph ends there; paragraph 4.1.2 "Design for Corrosion" follows
    immediately). This is not a text-extraction artifact -- verified
    directly against the PDF's raw text spans. There is no printed
    criterion in this manual for auto-selecting alpha = 0.90, so this
    function does not attempt to guess one; pass ``override=0.90``
    explicitly when the engineer has determined the reduced value applies.

    Returns
    -------
    dict
        {'alpha', 'printed_page': '17', 'pdf_page': 25}
    """
    alpha = 1.0 if override is None else override
    return {"alpha": alpha, "printed_page": "17", "pdf_page": 25}


# ============================================================================
# Table 4.1 -- Minimum load factors (printed p. 27, pdf_page 35)
# ============================================================================

# Permanent loads (paragraph 4.3.3). 'add'/'subtract' = footnotes 1/2
# (applied when the load adds to / subtracts from the predominant effect);
# 'alone' = D used alone as a principal load (gamma_pr = 1.4).
TABLE_4_1_PERMANENT = {
    "D": {"serviceability_fatigue": 1.0, "add": 1.2, "subtract": 0.9, "alone": 1.4},
    "G": {"serviceability_fatigue": 1.0, "add": 1.6, "subtract": 0.0},
}

# Temporary and dynamic loads (Table 4.1). 'companion' = gamma_c
# (Permanent-and-Companion column); 'usual'/'unusual'/'extreme' = gamma_pr
# (Principal Load Factor columns); None = no entry ('NA' in the printed
# table). Footnote superscripts noted in each entry's 'note'.
TABLE_4_1_TEMPORARY_DYNAMIC = {
    "Hs": {"serviceability_fatigue": 1.0, "companion": 1.0,
           "usual": 1.5, "unusual": 1.4, "extreme": 1.3,
           "note": "usual/unusual footnote 3 (used as principal when the maximum possible load); extreme footnote 7 (typical value)."},
    "IX": {"serviceability_fatigue": 1.0, "companion": 1.0,
           "usual": None, "unusual": None, "extreme": 1.3, "note": "footnote 7"},
    "Q": {"serviceability_fatigue": 1.0, "companion": 1.0,
          "usual": 1.5, "unusual": 1.4, "extreme": 1.3,
          "note": "usual/unusual footnote 3; extreme footnote 7"},
    "L": {"serviceability_fatigue": 1.0, "companion": 1.0,
          "usual": None, "unusual": 1.6, "extreme": None, "note": "footnote 4, from ASCE 7-22"},
    "T": {"serviceability_fatigue": 1.0, "companion": 1.0,
          "usual": None, "unusual": None, "extreme": None,
          "note": ("Table 4.1's compact printed cell for T is ambiguous; paragraph "
                    "4.3.4.4 states the T principal load factor directly as gamma_pr "
                    "= 1.2 (min), not banded by usual/unusual/extreme -- see "
                    "``principal_load_factor_self_straining``.")},
    "F": {"serviceability_fatigue": 1.0, "companion": 1.4,
          "usual": None, "unusual": None, "extreme": None,
          "note": "companion-only, footnote-free (paragraph 4.3.5): gamma_c = 1.4 applied to friction coefficients."},
    "Hd": {"serviceability_fatigue": 1.0, "companion": 1.0,
           "usual": None, "unusual": None, "extreme": 1.3, "note": "footnote 7"},
    "Hw": {"serviceability_fatigue": 1.0, "companion": 1.0,
           "usual": None, "unusual": None, "extreme": 1.2, "note": "footnote 7"},
    "IM": {"serviceability_fatigue": 1.0, "companion": 1.0,
           "usual": None, "unusual": None, "extreme": 1.3, "note": "footnote 7"},
    "BI": {"serviceability_fatigue": 1.0, "companion": 1.0,
           "usual": None, "unusual": None, "extreme": 1.3, "note": None},
    "W": {"serviceability_fatigue": 1.0, "companion": 0.5,
          "usual": None, "unusual": None, "extreme": 1.0, "note": "footnote 4, from ASCE 7-22"},
    "EQ": {"serviceability_fatigue": None, "companion": None,
           "usual": None, "unusual": 1.5, "extreme": "1.0 or 1.25",
           "note": ("footnote 6: for site-specific earthquake the load factor is 1.0; "
                     "otherwise the higher (1.25) load factor is used -- see Eq 4.7/4.8/4.9.")},
}


def table_4_1_permanent_load_factor(load_id, effect="add"):
    """Table 4.1 permanent load factor gamma_p (printed p. 27).

    Parameters
    ----------
    load_id : str
        'D' or 'G'.
    effect : str, optional
        'add' (loads add to the predominant effect, default), 'subtract',
        or 'alone' (D used alone as a principal load, gamma_pr = 1.4;
        'D' only).

    Returns
    -------
    dict
        {'load_id', 'effect', 'gamma', 'table': '4.1', ...}
    """
    if load_id not in TABLE_4_1_PERMANENT:
        raise ValueError(f"load_id must be 'D' or 'G', got {load_id!r}")
    row = TABLE_4_1_PERMANENT[load_id]
    if effect not in row:
        raise ValueError(f"effect {effect!r} not defined for {load_id!r}; available: {sorted(k for k in row if k != 'serviceability_fatigue')}")
    return {"load_id": load_id, "effect": effect, "gamma": row[effect],
            "table": "4.1", "printed_page": "27", "pdf_page": 35}


def table_4_1_load_factor(load_id, category, role="principal"):
    """Table 4.1 principal/companion load factor for a temporary or dynamic
    load (printed p. 27).

    Parameters
    ----------
    load_id : str
        A key of ``TABLE_4_1_TEMPORARY_DYNAMIC`` (e.g. 'Hs', 'Hw', 'EQ').
    category : str
        'usual', 'unusual', or 'extreme' (ignored if role='companion').
    role : str, optional
        'principal' (default; the usual/unusual/extreme column) or
        'companion' (the Permanent-and-Companion column, gamma_c).

    Returns
    -------
    dict
        {'load_id', 'category', 'role', 'factor', 'table': '4.1', ...}

    Raises
    ------
    ValueError
        If load_id/category is invalid, or the table has no entry ('NA' in
        the printed table) for that combination.
    """
    if load_id not in TABLE_4_1_TEMPORARY_DYNAMIC:
        raise ValueError(
            f"load_id must be one of {sorted(TABLE_4_1_TEMPORARY_DYNAMIC)}, got {load_id!r}"
        )
    row = TABLE_4_1_TEMPORARY_DYNAMIC[load_id]
    if role == "companion":
        factor = row["companion"]
    elif role == "principal":
        if category not in ("usual", "unusual", "extreme"):
            raise ValueError(f"category must be 'usual'/'unusual'/'extreme', got {category!r}")
        factor = row[category]
    else:
        raise ValueError(f"role must be 'principal' or 'companion', got {role!r}")
    if factor is None:
        raise ValueError(
            f"Table 4.1 has no entry for load_id={load_id!r}, role={role!r}, "
            f"category={category!r} ('NA' in the printed table)."
        )
    return {"load_id": load_id, "category": category, "role": role, "factor": factor,
            "table": "4.1", "printed_page": "27", "pdf_page": 35}


def fatigue_serviceability_load_factor(load_id):
    """Table 4.1's Serviceability-and-Fatigue column: 1.0 for every load
    (footnote 5: this is the FINITE fatigue life value; infinite-life
    fatigue design uses 2.0 for all loads -- see
    ``fatigue_fracture.fatigue_load_factor``). Printed p. 27.
    """
    all_loads = dict(TABLE_4_1_PERMANENT)
    all_loads.update(TABLE_4_1_TEMPORARY_DYNAMIC)
    if load_id not in all_loads:
        raise ValueError(f"Unknown load_id {load_id!r}")
    val = all_loads[load_id]["serviceability_fatigue"]
    if val is None:
        raise ValueError(f"Table 4.1 has no Serviceability/Fatigue entry for {load_id!r} (EQ: 'NA').")
    return {"load_id": load_id, "factor": val, "life": "finite",
            "table": "4.1", "printed_page": "27", "pdf_page": 35}


# ============================================================================
# Paragraph 4.3.4 -- generic principal load factor conditions
# (printed pp. 24-25, pdf_page 32-33)
# ============================================================================

PRINCIPAL_LOAD_CONDITIONS = {
    "condition_1": 1.2,          # unlimited by geometry; return period estimable (e.g. wind, most wave loads)
    "condition_2_usual": 1.5,    # limited to a usual-range maximum
    "condition_2_unusual": 1.4,  # limited to an unusual-range maximum
    "condition_2_extreme": 1.3,  # limited to an extreme-range maximum
    "condition_3": 1.3,          # return period unknown; treated as extreme
}


def principal_load_condition_factor(condition):
    """Paragraph 4.3.4: generic principal load factor gamma_pr for a load
    not covered by a specific Table 4.1 row (printed pp. 24-25).

    Parameters
    ----------
    condition : str
        A key of ``PRINCIPAL_LOAD_CONDITIONS``:
        'condition_1' (maximum loading not limited by geometry/physical
        factors, e.g. wind/wave, return period estimable -- 1.2),
        'condition_2_usual'/'condition_2_unusual'/'condition_2_extreme'
        (loading limited to a maximum value with a return period in the
        stated range -- 1.5/1.4/1.3), or
        'condition_3' (return period unknown; treated as very-low-
        probability-of-exceedance extreme -- 1.3).

    Returns
    -------
    dict
        {'condition', 'gamma_pr', 'printed_page': '24-25', 'pdf_page': '32-33'}
    """
    if condition not in PRINCIPAL_LOAD_CONDITIONS:
        raise ValueError(f"condition must be one of {sorted(PRINCIPAL_LOAD_CONDITIONS)}, got {condition!r}")
    return {"condition": condition, "gamma_pr": PRINCIPAL_LOAD_CONDITIONS[condition],
            "printed_page": "24-25", "pdf_page": "32-33"}


def principal_load_factor_self_straining(minimum=True):
    """Paragraph 4.3.4.4: self-straining (T) principal load factor,
    gamma_pr = 1.2 (min) (printed p. 25).
    """
    return {"load_id": "T", "gamma_pr": 1.2, "is_minimum": minimum,
            "printed_page": "25", "pdf_page": 33}


# ============================================================================
# Eq 4.2 -- general LRFD load-combination equation (printed p. 23, pdf_page 31)
# ============================================================================

def load_combination_lrfd(permanent_terms, principal_term, companion_terms=None):
    """Eq 4.2: general LRFD load-combination equation (printed p. 23).

        U = sum(gamma_p * Lp) + gamma_pr * Lpr + sum(gamma_c * Ltc) + gamma_c * Ldc

    Parameters
    ----------
    permanent_terms : list of (load_value, gamma_p)
        Permanent-load contributions Lp with their Table 4.1 gamma_p
        (``table_4_1_permanent_load_factor``).
    principal_term : (load_value, gamma_pr)
        The single principal load Lpr with its Table 4.1 or paragraph-4.3.4
        principal load factor.
    companion_terms : list of (load_value, gamma_c), optional
        Temporary and/or dynamic companion-load contributions (Ltc, Ldc).

    Returns
    -------
    dict
        {'u', 'permanent_sum', 'principal_contribution', 'companion_sum',
         'equation': '4.2', 'printed_page': '23', 'pdf_page': 31}
    """
    permanent_sum = sum(v * g for v, g in permanent_terms)
    lpr, gpr = principal_term
    principal_contribution = lpr * gpr
    companion_sum = sum(v * g for v, g in (companion_terms or []))
    u = permanent_sum + principal_contribution + companion_sum
    return {
        "u": u, "permanent_sum": permanent_sum,
        "principal_contribution": principal_contribution, "companion_sum": companion_sum,
        "equation": "4.2", "printed_page": "23", "pdf_page": 31,
    }


# ============================================================================
# Eq 4.7, 4.8, 4.9 -- earthquake load combinations (printed p. 32, pdf_page 40)
# ============================================================================

def earthquake_load_combination(permanent_sum, eq_load, companion_terms=None, method="standard_obe"):
    """Eq 4.7/4.8/4.9: earthquake load combinations (printed p. 32).

    Two earthquakes are considered (paragraph 4.4.1, per ER 1110-2-1806):
    the Operating Basis Earthquake (OBE, unusual load) and the Maximum
    Design Earthquake (MDE, extreme load; equals the Maximum Credible
    Earthquake (MCE) for critical features).

    Parameters
    ----------
    permanent_sum : float
        sum(gamma_p * Lp), the factored permanent-load sum (see
        ``load_combination_lrfd``'s permanent_sum, or compute directly).
    eq_load : float
        EQ, the earthquake load effect (unfactored).
    companion_terms : list of (load_value, gamma_c), optional
        Companion loads (typically hydrostatic, Hsc).
    method : str, optional
        'standard_obe' (Eq 4.7, U = sum(gamma_p*Lp) + 1.5*EQ + gamma_c*Ltc,
        for the OBE/unusual-return-period standard ground motion, default),
        'standard_mde' (Eq 4.8, U = sum(gamma_p*Lp) + 1.25*EQ + gamma_c*Ltc,
        for standard MDE ground motion -- Table 4.1 footnote 6's "1.25"),
        or 'site_specific' (Eq 4.9, U = sum(gamma_p*Lp) + 1.0*EQ + 1.0*Lt,
        for site-specific MDE/MCE ground motion -- Table 4.1 footnote 6's
        "1.0"; unfactored because a site-specific analysis already reflects
        the target reliability).

    Returns
    -------
    dict
        {'u', 'eq_factor', 'equation', 'printed_page': '32', 'pdf_page': 40}
    """
    companion_terms = companion_terms or []
    if method == "standard_obe":
        eq_factor = 1.5
        companion_sum = sum(v * g for v, g in companion_terms)
        u = permanent_sum + eq_factor * eq_load + companion_sum
        equation = "4.7"
    elif method == "standard_mde":
        eq_factor = 1.25
        companion_sum = sum(v * g for v, g in companion_terms)
        u = permanent_sum + eq_factor * eq_load + companion_sum
        equation = "4.8"
    elif method == "site_specific":
        eq_factor = 1.0
        companion_sum = sum(v for v, _g in companion_terms)  # all factors = 1.0
        u = permanent_sum + eq_factor * eq_load + companion_sum
        equation = "4.9"
    else:
        raise ValueError(
            f"method must be 'standard_obe', 'standard_mde', or 'site_specific', got {method!r}"
        )
    return {"u": u, "eq_factor": eq_factor, "equation": equation,
            "printed_page": "32", "pdf_page": 40}
