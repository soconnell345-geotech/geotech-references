"""EM 1110-2-2104 Chapter 3 -- Serviceability design (paragraphs 3-4 through
3-7).

Maximum service stresses (Table 3-3), the alternate single-load-factor
serviceability method (Table 3-4), reinforcement limits (paragraph 3-6), and
minimum wall thickness (paragraph 3-7). Printed pages per the 1 Nov 2023
edition (pdf_page = printed_page + 5).
"""

# ============================================================================
# Table 3-3 -- Maximum service stresses (printed p. 26, pdf_page 31)
# ============================================================================

_TABLE_3_3 = {
    "usual": {"flexure_shear_ksi": 25.0, "flexure_shear_mpa": 170.0,
              "direct_tension_ksi": 20.0, "direct_tension_mpa": 140.0},
    "unusual": {"flexure_shear_ksi": 35.0, "flexure_shear_mpa": 240.0,
                "direct_tension_ksi": 27.5, "direct_tension_mpa": 190.0},
}


def table_3_3_max_service_stress(category, action="flexure_shear"):
    """Table 3-3: maximum service (unfactored) reinforcement stress,
    all steel grades (printed p. 26).

    There are no serviceability stress requirements for extreme load
    combinations (paragraph 3-4a(1)).

    Parameters
    ----------
    category : str
        'usual' or 'unusual'.
    action : str, optional
        'flexure_shear' (reinforcement flexure and shear stress, default) or
        'direct_tension'.

    Returns
    -------
    dict
        {'category', 'action', 'fs_ksi', 'fs_mpa', 'table': '3-3', ...}
    """
    if category not in _TABLE_3_3:
        raise ValueError(f"category must be 'usual' or 'unusual', got {category!r}")
    row = _TABLE_3_3[category]
    if action == "flexure_shear":
        fs_ksi, fs_mpa = row["flexure_shear_ksi"], row["flexure_shear_mpa"]
    elif action == "direct_tension":
        fs_ksi, fs_mpa = row["direct_tension_ksi"], row["direct_tension_mpa"]
    else:
        raise ValueError(
            f"action must be 'flexure_shear' or 'direct_tension', got {action!r}"
        )
    return {
        "category": category, "action": action, "fs_ksi": fs_ksi,
        "fs_mpa": fs_mpa, "table": "3-3", "printed_page": "26", "pdf_page": 31,
    }


# ============================================================================
# Table 3-4 -- Single-load factors, fy = 60,000 psi (printed p. 26)
# ============================================================================

_TABLE_3_4 = {
    "usual": {"flexure_shear": 2.2, "direct_tension": 2.8},
    "unusual": {"flexure_shear": 1.6, "direct_tension": 2.0},
}


def table_3_4_single_load_factor(category, action="flexure_shear"):
    """Table 3-4: single-load factor for the alternate serviceability
    design method, fy = 60,000 psi (414 MPa) only (printed p. 26).

    Beams and one-way slabs designed to meet Table 3-3 service stresses may
    instead be designed with the strength design method by multiplying
    service loads by this single load factor (paragraph 3-4a(2)).

    Parameters
    ----------
    category : str
        'usual' or 'unusual'.
    action : str, optional
        'flexure_shear' (reinforcement, default) or 'direct_tension'.

    Returns
    -------
    dict
        {'category', 'action', 'factor', 'table': '3-4', ...}
    """
    if category not in _TABLE_3_4:
        raise ValueError(f"category must be 'usual' or 'unusual', got {category!r}")
    row = _TABLE_3_4[category]
    if action not in row:
        raise ValueError(
            f"action must be 'flexure_shear' or 'direct_tension', got {action!r}"
        )
    return {
        "category": category, "action": action, "factor": row[action],
        "table": "3-4", "printed_page": "26", "pdf_page": 31,
        "note": "Applies only for fy = 60,000 psi (414 MPa).",
    }


def single_load_factor_design_moment(m_service, category, action="flexure_shear"):
    """Nominal design moment/force via the alternate serviceability (single
    load factor) method (paragraph 3-4a(2), Table 3-4; printed p. 26).

        Mu = factor * M_service ;  Mn = Mu / phi

    Reproduces Appendix D-3/D-4's ``Mu = 2.2*(Lp+Lt+Ld) = 2.2*M`` step for
    usual loads with fy = 60,000 psi.

    Parameters
    ----------
    m_service : float
        Unfactored (service) moment or force.
    category : str
        'usual' or 'unusual'.
    action : str, optional
        'flexure_shear' (default) or 'direct_tension'.

    Returns
    -------
    dict
        {'m_service', 'factor', 'mu', 'printed_page': '26', 'pdf_page': 31}
    """
    tbl = table_3_4_single_load_factor(category, action)
    mu = tbl["factor"] * m_service
    return {
        "m_service": m_service, "factor": tbl["factor"], "mu": mu,
        "printed_page": "26", "pdf_page": 31,
    }


# ============================================================================
# Paragraph 3-6 -- Reinforcement limits (printed p. 27, pdf_page 32)
# ============================================================================

def max_reinforcement_ratio(rho_b):
    """Mandatory maximum tension reinforcement ratio, 0.50*rho_b, for all
    load cases, to ensure a ductile failure mode (paragraph 3-6, printed
    p. 27).

    Parameters
    ----------
    rho_b : float
        Balanced reinforcement ratio (e.g. from
        ``flexure_axial.balanced_reinforcement_ratio``).

    Returns
    -------
    dict
        {'rho_b', 'rho_max', 'printed_page': '27', 'pdf_page': 32}
    """
    return {
        "rho_b": rho_b, "rho_max": 0.50 * rho_b,
        "reference": "EM 1110-2-2104 paragraph 3-6 (mandatory)",
        "printed_page": "27", "pdf_page": 32,
    }


def deflection_control_reinforcement_ratio(rho_b):
    """Recommended (not mandatory) deflection-control tension reinforcement
    ratio limit, 0.25*rho_b (paragraph 3-4b(2), printed p. 27).

    Limiting rho to 0.25*rho_b was mandatory in past editions and is
    "recommended to generally design within" in the current edition, used
    in lieu of a detailed deflection check (as in Appendix D-3/D-4/D-5).

    Parameters
    ----------
    rho_b : float
        Balanced reinforcement ratio.

    Returns
    -------
    dict
        {'rho_b', 'rho_deflection_limit', 'printed_page': '27', 'pdf_page': 32}
    """
    return {
        "rho_b": rho_b, "rho_deflection_limit": 0.25 * rho_b,
        "reference": "EM 1110-2-2104 paragraph 3-4b(2) (recommended)",
        "printed_page": "27", "pdf_page": 32,
    }


# ============================================================================
# Paragraph 3-7 -- Minimum thickness of walls (printed p. 27, pdf_page 32)
# ============================================================================

def min_wall_thickness(height_ft, thickness_in=None):
    """Minimum wall thickness and both-faces-reinforcement requirement
    (paragraph 3-7, printed p. 27).

    Rules: walls with height > 10 ft must be >= 12 in. thick; walls
    >= 10 in. thick must have reinforcement in both faces; walls must not be
    less than 8 in. thick (any height).

    Parameters
    ----------
    height_ft : float
        Wall height, ft.
    thickness_in : float, optional
        A candidate/trial thickness to check against the rules. If omitted,
        only the governing minimum is returned.

    Returns
    -------
    dict
        {'height_ft', 'absolute_min_in' (8.0), 'height_governed_min_in'
         (12.0 if height_ft > 10 else None), 'governing_min_in',
         'both_faces_required_at_in' (10.0), and, if thickness_in given,
         'thickness_in', 'adequate' (bool), 'both_faces_required' (bool)}
    """
    absolute_min = 8.0
    height_min = 12.0 if height_ft > 10.0 else None
    governing_min = max(absolute_min, height_min or 0.0)
    out = {
        "height_ft": height_ft, "absolute_min_in": absolute_min,
        "height_governed_min_in": height_min, "governing_min_in": governing_min,
        "both_faces_required_at_in": 10.0,
        "reference": "EM 1110-2-2104 paragraph 3-7",
        "printed_page": "27", "pdf_page": 32,
    }
    if thickness_in is not None:
        out["thickness_in"] = thickness_in
        out["adequate"] = thickness_in >= governing_min
        out["both_faces_required"] = thickness_in >= 10.0
    return out
