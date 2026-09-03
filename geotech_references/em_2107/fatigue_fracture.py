"""EM 1110-2-2107 Chapter 5 -- Fatigue and Fracture.

This chapter is predominantly qualitative/procedural guidance (select an
AISC 360/AASHTO detail category, follow the Fracture Control Plan process,
etc.) rather than reprinted numeric equations -- unlike EM 1110-2-2104's
Chapter 5 (which prints its own pre-ACI-318-19 shear-capacity equations),
EM 1110-2-2107 explicitly defers member-level stress-range/detail-category
values to "AISC 360 and AASHTO" (paragraph 5.1.1) rather than reprinting
them. The few genuinely numeric, printed criteria are implemented below.
Printed pages per the 1 August 2022 edition (pdf_page = printed_page + 8).
"""

# ============================================================================
# Table 4.1 footnote 5 -- fatigue load factor (printed p. 27, pdf_page 35)
# ============================================================================

def fatigue_load_factor(life="finite"):
    """Table 4.1 footnote 5: the load factor applied to loads used to
    compute fatigue stress (printed p. 27; also paragraph 5.1.1.1).

        finite life:   gamma = 1.0  (per Table 4.1's Serviceability/Fatigue
                                      column; a design is acceptable when the
                                      combined stress range and cycle count
                                      exceed the selected detail category's
                                      fatigue strength)
        infinite life: gamma = 2.0  (all loads; paragraph 5.1.1.2 discusses
                                      Detail Categories A-C as generally
                                      sufficient for infinite life)

    Parameters
    ----------
    life : str, optional
        'finite' (default) or 'infinite'.

    Returns
    -------
    dict
        {'life', 'gamma', 'printed_page': '27', 'pdf_page': 35}
    """
    if life not in ("finite", "infinite"):
        raise ValueError(f"life must be 'finite' or 'infinite', got {life!r}")
    gamma = 1.0 if life == "finite" else 2.0
    return {"life": life, "gamma": gamma, "printed_page": "27", "pdf_page": 35}


# ============================================================================
# Paragraph 5.1.3 -- fatigue-check screening rule (printed p. 34, pdf_page 42)
# ============================================================================

def fatigue_check_required(dead_load_compressive_stress, live_load_tensile_stress):
    """Paragraph 5.1.3: fatigue-life screening rule (printed p. 34).

    Details are fatigue-prone only when subjected to a net TENSION stress.
    If the live-load tensile stress does not exceed half of the
    simultaneously-occurring dead-load compressive stress (i.e. a factor of
    safety of 2.0 against the net stress ever reaching tension), a fatigue
    life check is not required.

        required = live_load_tensile_stress >= 0.5 * dead_load_compressive_stress

    Parameters
    ----------
    dead_load_compressive_stress : float
        Sustained (dead-load) compressive stress at the detail, taken
        positive.
    live_load_tensile_stress : float
        Live-load-induced tensile stress at the same detail, taken
        positive.

    Returns
    -------
    dict
        {'dead_load_compressive_stress', 'live_load_tensile_stress',
         'threshold', 'required' (bool), 'printed_page': '34', 'pdf_page': 42}
    """
    threshold = 0.5 * dead_load_compressive_stress
    return {
        "dead_load_compressive_stress": dead_load_compressive_stress,
        "live_load_tensile_stress": live_load_tensile_stress,
        "threshold": threshold, "required": live_load_tensile_stress >= threshold,
        "printed_page": "34", "pdf_page": 42,
    }


# ============================================================================
# Paragraph 5.2.1.2 -- fracture-critical-member redundancy strength check
# (printed p. 35, pdf_page 43)
# ============================================================================

def fracture_critical_redundancy_check(q_demand_unfactored_sum, rn_nominal, fy):
    """Paragraph 5.2.1.2: the refined-analysis strength check used to show a
    member need not be treated as fracture critical because the structure
    retains adequate strength/stability with that member assumed fractured
    (printed p. 35).

    For this check: a load factor of 1.0 is applied to every load in every
    applicable combination, a resistance factor of 1.0 is applied to the
    applicable strength limit, AND in no case may the resulting stress
    exceed 90 percent of yield.

        adequate = (Q_sum <= Rn) AND (stress_demand <= 0.90*Fy)

    Parameters
    ----------
    q_demand_unfactored_sum : float
        Sum of all applicable UNFACTORED load effects (gamma = 1.0 applied
        to each), consistent units with rn_nominal.
    rn_nominal : float
        Nominal strength for the applicable limit state (phi = 1.0
        applied).
    fy : float
        Material yield strength (for the 90%-of-yield stress cap; pass the
        governing stress alongside fy via the caller's own stress
        computation if q_demand_unfactored_sum is a force rather than a
        stress -- this function's stress check assumes q_demand_unfactored_sum
        is already expressed as a stress when used for the 0.90*Fy cap).

    Returns
    -------
    dict
        {'strength_adequate' (bool), 'yield_cap', 'within_yield_cap' (bool),
         'adequate' (bool, both checks), 'printed_page': '35', 'pdf_page': 43}
    """
    strength_adequate = q_demand_unfactored_sum <= rn_nominal
    yield_cap = 0.90 * fy
    within_yield_cap = q_demand_unfactored_sum <= yield_cap
    return {
        "strength_adequate": strength_adequate, "yield_cap": yield_cap,
        "within_yield_cap": within_yield_cap,
        "adequate": strength_adequate and within_yield_cap,
        "printed_page": "35", "pdf_page": 43,
    }
