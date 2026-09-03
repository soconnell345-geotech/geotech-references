"""EM 1110-2-2104 Chapter 3 -- Loads and Strength Design.

Load inventory (Table 3-1), the full load-factor table (Table 3-2), the
general LRFD strength-design equations (Eq 3-1/3-2), the three earthquake
load combinations (Eq 3-3/3-4/3-5), and the Appendix F commentary target-
reliability table (Table F-2). Printed pages per the 1 Nov 2023 edition
(pdf_page = printed_page + 5).

This manual's load factors are NOT identical to ACI 318-19 / ASCE 7 --
paragraph 1-7d: "The load factors resemble those shown in ACI 318-19 but are
modified to account for unique loads on hydraulic structures, serviceability
needs of hydraulic structures, and the higher reliability needed for
critical structures." Implement THIS manual's Table 3-2, not the ACI/ASCE
default.
"""

import math

# ============================================================================
# Table 3-1 -- Loads on hydraulic structures (printed p. 17, pdf_page 22)
# ============================================================================

TABLE_3_1_LOADS = {
    # Permanent loads, Lp
    "D": {"name": "Dead", "duration": "permanent"},
    "EV": {"name": "Vertical Earth", "duration": "permanent"},
    "EH": {"name": "Lateral Earth", "duration": "permanent"},
    "G": {"name": "Gravity (mud/ice)", "duration": "permanent"},
    # Temporary (intermittent static) loads, Lt
    "Hs": {"name": "Hydrostatic", "duration": "temporary"},
    "IX": {"name": "Ice, Thermal Expansion", "duration": "temporary"},
    "ES": {"name": "Soil Surcharge", "duration": "temporary"},
    "Q": {"name": "Operating Equipment", "duration": "temporary"},
    "L": {"name": "Live Load", "duration": "temporary"},
    "T": {"name": "Self-Straining", "duration": "temporary"},
    "V": {"name": "Vehicle Live Loads", "duration": "temporary"},
    # Dynamic (impulse) loads, Ld
    "Hd": {"name": "Hydrodynamic (except earthquake)", "duration": "dynamic"},
    "Hw": {"name": "Wave", "duration": "dynamic"},
    "IM": {"name": "Debris/Floating Ice Impact", "duration": "dynamic"},
    "BI": {"name": "Barge/Boat Impact", "duration": "dynamic"},
    "W": {"name": "Wind", "duration": "dynamic"},
    "EQ": {"name": "Earthquake", "duration": "dynamic"},
    "HA": {"name": "Hawser", "duration": "dynamic"},
}


def table_3_1_load_inventory(load_id=None):
    """Table 3-1: loads on hydraulic structures, and their duration category
    (permanent Lp / temporary Lt / dynamic Ld) (printed p. 17).

    Parameters
    ----------
    load_id : str, optional
        A key of ``TABLE_3_1_LOADS`` (e.g. 'Hs', 'EQ'). If omitted, the full
        table is returned.

    Returns
    -------
    dict
    """
    if load_id is None:
        return {"loads": dict(TABLE_3_1_LOADS), "table": "3-1",
                "printed_page": "17", "pdf_page": 22}
    if load_id not in TABLE_3_1_LOADS:
        raise ValueError(f"Unknown load_id {load_id!r}; see TABLE_3_1_LOADS")
    row = dict(TABLE_3_1_LOADS[load_id])
    row.update({"load_id": load_id, "table": "3-1",
                "printed_page": "17", "pdf_page": 22})
    return row


# ============================================================================
# Table 3-2 -- Minimum load factors for strength design
# (printed pp. 23-24, pdf_page 28-29)
# ============================================================================

# Permanent load factors, gamma_p (paragraph 3-3d, printed p. 22, pdf 27).
# 'add' = applied when the load adds to the predominant load effect (footnote
# 1); 'subtract' = applied when it subtracts (footnote 2).
TABLE_3_2_PERMANENT = {
    "D": {"add": 1.2, "subtract": 0.9, "alone": 1.4},
    "EV": {"add": 1.35, "subtract": 1.0},
    "EH_at_rest_driving": {"add": 1.35},
    "EH_at_rest_resisting": {"add": 0.9},
    "EH_active": {"add": 1.5},
    "EH_passive": {"add": 0.5},
    "G": {"add": 1.6, "subtract": 0.0},
}

# Principal/companion load factors, gamma_pu / gamma_c, by load category
# (Table 3-2, printed pp. 23-24). None = no entry ('-' or 'N/A' in the
# printed table); 'AASHTO' = per AASHTO LRFD (footnote 8, paragraph 3-1g).
TABLE_3_2_TEMPORARY_DYNAMIC = {
    "Hs": {"companion": 1.0, "usual": 1.5, "unusual": 1.4, "extreme": 1.3},
    "IX": {"companion": 1.0, "usual": None, "unusual": None, "extreme": 1.3},
    "ES": {"companion": 1.0, "usual": None, "unusual": 1.6, "extreme": 1.3},
    "Q": {"companion": 1.0, "usual": 1.5, "unusual": 1.4, "extreme": 1.3},
    "L": {"companion": 1.0, "usual": None, "unusual": 1.6, "extreme": None},
    "T": {"companion": 0.75, "usual": None, "unusual": 1.0, "extreme": 1.0},
    "V": {"companion": 1.0, "usual": None, "unusual": "AASHTO", "extreme": "AASHTO"},
    "Hd": {"companion": 1.0, "usual": None, "unusual": None, "extreme": 1.3},
    "Hw": {"companion": 1.0, "usual": None, "unusual": None, "extreme": 1.2},
    "IM": {"companion": 1.0, "usual": None, "unusual": None, "extreme": 1.3},
    "BI": {"companion": 1.0, "usual": 2.2, "unusual": 1.6, "extreme": 1.3},
    "W": {"companion": 0.5, "usual": None, "unusual": None, "extreme": 1.0},
    "EQ": {"companion": None, "usual": None, "unusual": 1.5, "extreme": "1.0 or 1.25"},
    "HA": {"companion": 1.0, "usual": None, "unusual": 1.6, "extreme": None},
}

# Generic principal-load-factor conditions (paragraph 3-3e, printed pp. 22-23):
# used when a load is not one of the tabulated Table 3-2 rows above.
PRINCIPAL_LOAD_CONDITIONS = {
    "condition_1": 1.2,   # unlimited by geometry; return period estimable
    "condition_2_extreme": 1.3,
    "condition_2_unusual": 1.4,
    "condition_2_usual": 1.5,
    "condition_3": 1.3,   # upper-bound/unknown-return-period loads
}


def table_3_2_permanent_load_factor(load_id, effect="add"):
    """Table 3-2 permanent load factor gamma_p (printed pp. 23-24).

    Parameters
    ----------
    load_id : str
        One of 'D', 'EV', 'EH_at_rest_driving', 'EH_at_rest_resisting',
        'EH_active', 'EH_passive', 'G'.
    effect : str, optional
        'add' (loads add to the predominant effect, footnote 1, default),
        'subtract' (footnote 2), or 'alone' (D applied alone, gamma_p = 1.4).

    Returns
    -------
    dict
        {'load_id', 'effect', 'gamma_p', 'table': '3-2', ...}
    """
    if load_id not in TABLE_3_2_PERMANENT:
        raise ValueError(
            f"load_id must be one of {sorted(TABLE_3_2_PERMANENT)}, got {load_id!r}"
        )
    row = TABLE_3_2_PERMANENT[load_id]
    if effect not in row:
        raise ValueError(
            f"effect {effect!r} not defined for {load_id!r}; available: {sorted(row)}"
        )
    return {
        "load_id": load_id, "effect": effect, "gamma_p": row[effect],
        "table": "3-2", "printed_page": "23-24", "pdf_page": "28-29",
    }


def table_3_2_load_factor(load_id, category, role="principal"):
    """Table 3-2 principal/companion load factor for a temporary or dynamic
    load (printed pp. 23-24).

    Parameters
    ----------
    load_id : str
        A key of ``TABLE_3_2_TEMPORARY_DYNAMIC`` (e.g. 'Hs', 'Hw', 'EQ').
    category : str
        'usual', 'unusual', or 'extreme' (ignored if role='companion').
    role : str, optional
        'principal' (default, uses the usual/unusual/extreme column) or
        'companion' (uses the Permanent-and-Companion column, gamma_c).

    Returns
    -------
    dict
        {'load_id', 'category', 'role', 'factor' (float, str, or None),
         'table': '3-2', ...}

    Raises
    ------
    ValueError
        If load_id/category is invalid, or the table has no entry
        ('-'/'N/A' in the printed table) for that combination.
    """
    if load_id not in TABLE_3_2_TEMPORARY_DYNAMIC:
        raise ValueError(
            f"load_id must be one of {sorted(TABLE_3_2_TEMPORARY_DYNAMIC)}, "
            f"got {load_id!r}"
        )
    row = TABLE_3_2_TEMPORARY_DYNAMIC[load_id]
    if role == "companion":
        factor = row["companion"]
    elif role == "principal":
        if category not in ("usual", "unusual", "extreme"):
            raise ValueError(
                f"category must be 'usual'/'unusual'/'extreme', got {category!r}"
            )
        factor = row[category]
    else:
        raise ValueError(f"role must be 'principal' or 'companion', got {role!r}")
    if factor is None:
        raise ValueError(
            f"Table 3-2 has no entry for load_id={load_id!r}, role={role!r}, "
            f"category={category!r} ('-'/N/A in the printed table)."
        )
    return {
        "load_id": load_id, "category": category, "role": role,
        "factor": factor, "table": "3-2", "printed_page": "23-24",
        "pdf_page": "28-29",
    }


# ============================================================================
# Eq 3-1, 3-2 -- Required strength / general LRFD load combination
# (printed pp. 21-22, pdf_page 26-27)
# ============================================================================

def required_strength_check(u_demand, phi, rn_nominal):
    """Eq 3-1: required strength check, sum(gamma_i * Lni) <= phi*Rn
    (printed p. 21).

    Parameters
    ----------
    u_demand : float
        U = sum(gamma_i * L_ni), the factored-load demand (from
        ``load_combination_lrfd`` or an earthquake combination).
    phi : float
        ACI 318-19 resistance (strength-reduction) factor.
    rn_nominal : float
        Nominal resistance (from Chapter 4/5 or Appendix B/D).

    Returns
    -------
    dict
        {'u_demand', 'phi_rn', 'adequate' (bool), 'equation': '3-1', ...}
    """
    phi_rn = phi * rn_nominal
    return {
        "u_demand": u_demand, "phi": phi, "rn_nominal": rn_nominal,
        "phi_rn": phi_rn, "adequate": u_demand <= phi_rn,
        "equation": "3-1", "printed_page": "21", "pdf_page": 26,
    }


def load_combination_lrfd(permanent_terms, principal_term, companion_terms=None):
    """Eq 3-2: general LRFD load-combination equation (printed p. 22).

        U = sum(gamma_p * Lp) + gamma_pu * Lpu + sum(gamma_c * Lc)

    Parameters
    ----------
    permanent_terms : list of (load_value, gamma_p)
        Permanent-load contributions Lp with their Table 3-2 gamma_p
        (``table_3_2_permanent_load_factor``).
    principal_term : (load_value, gamma_pu)
        The single principal load Lpu with its Table 3-2 or paragraph-3-3e
        principal load factor.
    companion_terms : list of (load_value, gamma_c), optional
        Temporary and/or dynamic companion-load contributions. Per paragraph
        3-2c(1), a dynamic companion load (Ld) is not included when the
        principal load itself is dynamic -- the caller is responsible for
        that exclusion (this function performs no load-type introspection).

    Returns
    -------
    dict
        {'u', 'permanent_sum', 'principal_contribution', 'companion_sum',
         'equation': '3-2', 'printed_page': '22', 'pdf_page': 27}
    """
    permanent_sum = sum(v * g for v, g in permanent_terms)
    lpu, gpu = principal_term
    principal_contribution = lpu * gpu
    companion_sum = sum(v * g for v, g in (companion_terms or []))
    u = permanent_sum + principal_contribution + companion_sum
    return {
        "u": u, "permanent_sum": permanent_sum,
        "principal_contribution": principal_contribution,
        "companion_sum": companion_sum,
        "equation": "3-2", "printed_page": "22", "pdf_page": 27,
    }


# ============================================================================
# Eq 3-3, 3-4, 3-5 -- Earthquake load combinations (printed p. 26, pdf_page 31)
# ============================================================================

def earthquake_load_combination(permanent_sum, eq_load, companion_terms=None,
                                 method="standard_obe"):
    """Eq 3-3/3-4/3-5: earthquake load combinations (printed p. 26).

    Only one temporary load is included at a time (if applicable) with an
    earthquake load (paragraph 3-3h(3)). For dynamic analysis, load factors
    are applied to the computed member force effects, not the applied loads.

    Parameters
    ----------
    permanent_sum : float
        sum(gamma_p * Lp), the factored permanent-load sum (see
        ``load_combination_lrfd``'s permanent_sum, or compute directly).
    eq_load : float
        EQ, the earthquake load effect (unfactored).
    companion_terms : list of (load_value, gamma_c), optional
        At most one companion load per paragraph 3-3h(3).
    method : str, optional
        'standard_obe' (Eq 3-3, U = sum(gamma_p*Lp) + 1.5*EQ + gamma_c*Lc,
        for standard/site-specific OBE ground motion, default),
        'standard_mde' (Eq 3-4, U = sum(gamma_p*Lp) + 1.25*EQ + gamma_c*Lc,
        for standard MDE ground motion), or 'site_specific_mde_mce' (Eq 3-5,
        U = 1.0*sum(Lp) + 1.0*EQ + 1.0*Lc, for site-specific MDE/MCE ground
        motion -- unfactored, since site-specific analysis already reflects
        the target reliability).

    Returns
    -------
    dict
        {'u', 'eq_factor', 'equation', 'printed_page': '26', 'pdf_page': 31}
    """
    companion_terms = companion_terms or []
    if method == "standard_obe":
        eq_factor = 1.5
        companion_sum = sum(v * g for v, g in companion_terms)
        u = permanent_sum + eq_factor * eq_load + companion_sum
        equation = "3-3"
    elif method == "standard_mde":
        eq_factor = 1.25
        companion_sum = sum(v * g for v, g in companion_terms)
        u = permanent_sum + eq_factor * eq_load + companion_sum
        equation = "3-4"
    elif method == "site_specific_mde_mce":
        eq_factor = 1.0
        companion_sum = sum(v for v, _g in companion_terms)  # all factors = 1.0
        u = permanent_sum + eq_factor * eq_load + companion_sum
        equation = "3-5"
    else:
        raise ValueError(
            "method must be 'standard_obe', 'standard_mde', or "
            f"'site_specific_mde_mce', got {method!r}"
        )
    return {
        "u": u, "eq_factor": eq_factor, "equation": equation,
        "printed_page": "26", "pdf_page": 31,
    }


# ============================================================================
# Table F-2 -- Target reliability, beta (Appendix F commentary, printed p. 119)
# ============================================================================

_TABLE_F_2 = {
    ("normal", "redundant"): 3.0,
    ("normal", "single"): 3.5,
    ("critical", "redundant"): 3.5,
    ("critical", "single"): 4.0,
}


def table_f2_target_reliability(structure_class, load_path):
    """Table F-2: target reliability index beta for a 100-year service life
    (Appendix F commentary, printed p. 119).

    Most RCHS are cantilever structures with a single load path (Appendix F
    commentary), so ``load_path='single'`` is the typical case.

    Parameters
    ----------
    structure_class : str
        'normal' or 'critical' (paragraph 3-1d).
    load_path : str
        'redundant' or 'single'.

    Returns
    -------
    dict
        {'structure_class', 'load_path', 'beta', 'table': 'F-2', ...}
    """
    key = (structure_class.lower(), load_path.lower())
    if key not in _TABLE_F_2:
        raise ValueError(
            "structure_class must be 'normal'/'critical' and load_path "
            f"'redundant'/'single'; got {structure_class!r}, {load_path!r}"
        )
    return {
        "structure_class": structure_class, "load_path": load_path,
        "beta": _TABLE_F_2[key], "table": "F-2",
        "printed_page": "119", "pdf_page": 124,
    }


def probability_of_failure_from_beta(beta):
    """Pf ~= Phi(-beta), the standard-normal-deviate approximation of
    probability of failure from reliability index beta (Appendix F
    commentary, printed p. 120).

    Parameters
    ----------
    beta : float
        Reliability index (e.g. from ``table_f2_target_reliability``).

    Returns
    -------
    dict
        {'beta', 'pf', 'printed_page': '120', 'pdf_page': 125}
    """
    pf = 0.5 * math.erfc(beta / math.sqrt(2.0))
    return {"beta": beta, "pf": pf, "printed_page": "120", "pdf_page": 125}
