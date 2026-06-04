"""GEC-8 table lookup functions.

Tables from FHWA-HIF-07-03 (GEC-8, April 2007), Design and Construction of
Continuous Flight Auger Piles.

ASD (not LRFD) design document.  Primary design tool is PCASE-style analysis
using load tests; these tables provide preliminary capacity estimates.
"""


# ============================================================================
# Table 5.4: P-Multipliers (Pm) for Design of Laterally Loaded Pile Groups
# (Chapter 5, p. 112)
#
# Same conceptual values as AASHTO Table 10.7.2.4-1.  For CFA piles,
# the recommended approach is the Pm method.
# Applies to vertical piles only; center-to-center spacing in direction of loading.
# Linear interpolation between 3B and 5B.
# ============================================================================

_TABLE_5_4_SPACING = [3.0, 5.0]

_TABLE_5_4 = {
    # p-multipliers at [3B, 5B] spacing — row 1, 2, 3+ per Pando et al.
    "lead_row": {"pm": [0.8, 1.0], "notes": "Lead (front) row"},
    "2nd_row": {"pm": [0.4, 0.85], "notes": "Second row"},
    "3rd_or_more_row": {"pm": [0.3, 0.7], "notes": "Third and subsequent rows"},
}


def table_5_4_p_multiplier(row_position: str, spacing_over_b: float) -> dict:
    """P-multiplier Pm for CFA/DD pile group lateral analysis (Table 5.4).

    Scales p-y resistance for each pile in a laterally loaded group:
        p_group = Pm × p_single

    Values consistent with AASHTO (2002) and Hannigan et al. (2006).
    Linear interpolation between 3B and 5B spacing.  Use Pm = 1.0 for
    spacing ≥ 5B.

    Parameters
    ----------
    row_position : str
        Row position: 'lead' (or '1st', 'front'), '2nd', '3rd' (or 'trail').
    spacing_over_b : float
        Center-to-center spacing ÷ pile diameter.  Must be ≥ 3.0.

    Returns
    -------
    dict
        {'row_position': str, 'spacing_over_b': float,
         'pm': float, 'notes': str}

    Raises
    ------
    ValueError
        If row_position is unrecognized or spacing_over_b < 3.0.
    """
    from geotech_references._interpolation import _linterp

    if spacing_over_b < 3.0:
        raise ValueError(
            f"spacing_over_b={spacing_over_b} is below the minimum of 3.0 "
            "(Table 5.4 applies for 3B ≤ spacing ≤ 5B; use Pm=1.0 beyond 5B)."
        )

    _aliases = {
        "lead": "lead_row", "lead_row": "lead_row", "front": "lead_row",
        "1st": "lead_row", "first": "lead_row", "row1": "lead_row",
        "2nd": "2nd_row", "second": "2nd_row", "row2": "2nd_row",
        "3rd": "3rd_or_more_row", "third": "3rd_or_more_row",
        "trail": "3rd_or_more_row", "trailing": "3rd_or_more_row",
        "3rd_or_more": "3rd_or_more_row", "row3": "3rd_or_more_row",
        "row3+": "3rd_or_more_row", "4th": "3rd_or_more_row",
    }

    key = row_position.lower().strip().replace(" ", "_").replace("-", "_")
    row_key = _aliases.get(key)
    if row_key is None:
        raise ValueError(
            f"Unknown row_position '{row_position}'. "
            "Use: 'lead', '2nd', or '3rd' (or 'trail')."
        )

    data = _TABLE_5_4[row_key]
    pm = _linterp(spacing_over_b, _TABLE_5_4_SPACING, data["pm"])

    return {
        "row_position": row_key,
        "spacing_over_b": spacing_over_b,
        "pm": round(pm, 3),
        "notes": data["notes"],
    }


# ============================================================================
# Table 5.3: Group Efficiency (η) for Model Drilled Shafts in CFA Pile Groups
# in Cohesive Soils (Chapter 5, p. 92)
#
# Per AASHTO (2002) Section 10.8.3.9.3 (drilled shaft provisions applied
# to CFA piles in cohesionless soils):
#   η = 0.65 at 2.5D spacing
#   η = 1.0 at 6.0D spacing
#   Linear interpolation between 2.5D and 6.0D.
#   No cap contact adjustment needed — values already conservative.
# ============================================================================

_GROUP_EFF_SPACING = [2.5, 6.0]
_GROUP_EFF_COHESIONLESS = [0.65, 1.00]


def table_group_efficiency_cohesionless(spacing_over_d: float) -> dict:
    """Axial group efficiency for CFA piles in cohesionless soils.

    Per AASHTO (2002) Section 10.8.3.9.3 (drilled shaft provisions
    applied to conventional CFA piles).  Regardless of cap contact
    with the ground:

        η = 0.65 at 2.5D center-to-center spacing
        η = 1.0 at 6.0D center-to-center spacing
        Linear interpolation between 2.5D and 6.0D.

    For DD pile groups in cohesionless soils, η ≈ 1.0 (similar to
    driven pile groups in dense/medium-dense conditions).

    Parameters
    ----------
    spacing_over_d : float
        Center-to-center spacing ÷ pile diameter.  Must be ≥ 2.5.
        Use η = 1.0 for spacing ≥ 6.0D.

    Returns
    -------
    dict
        {'spacing_over_d': float, 'group_efficiency': float,
         'source': str}

    Raises
    ------
    ValueError
        If spacing_over_d < 2.5.
    """
    from geotech_references._interpolation import _linterp

    if spacing_over_d < 2.5:
        raise ValueError(
            f"spacing_over_d={spacing_over_d} is below the minimum of 2.5D."
        )

    eta = _linterp(spacing_over_d, _GROUP_EFF_SPACING, _GROUP_EFF_COHESIONLESS)
    eta = min(eta, 1.0)

    return {
        "spacing_over_d": spacing_over_d,
        "group_efficiency": round(eta, 3),
        "source": (
            "GEC-8 Ch 5 (AASHTO 2002 Section 10.8.3.9.3, drilled shaft "
            "provisions applied to CFA piles in cohesionless soils)"
        ),
    }
