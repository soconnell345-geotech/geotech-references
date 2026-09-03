"""EM 1110-2-2104 Chapter 5 -- Shear.

Shear strength for one-way slabs/walls without shear reinforcement
(Eq 5-1), special straight members such as box culverts and gate wells
(Eq 5-2/5-3), and curved members (Eq 5-4). Printed pages per the 1 Nov 2023
edition (pdf_page = printed_page + 5).

DEVIATION FROM CURRENT ACI 318-19: Chapter 5 deliberately keeps the
PRE-ACI-318-19 shear-capacity equations for members without shear
reinforcement rather than adopting ACI 318-19's revised (lower, size- and
reinforcement-ratio-dependent) capacity. Appendix G explains why: RCHS are
thick, lightly reinforced, one-way cantilever members very unlike the simple-
span, concentrated-load test specimens behind ACI 318-19's new provision;
USACE has not observed shear failures under the prior equations across a
large inventory of RCHS designed by them. ``table_g1_shear_coefficient``
reproduces the manual's own side-by-side coefficient comparison (Table G-1).
Equations here implement THIS manual's Chapter 5, not ACI 318-19 Chapter 22.

Units: these equations are printed IN U.S. (standard) units only (paragraphs
5-4a, 5-5) -- psi for fc', lbs for Vc/Nu, in. for b/d/ln/R. Eq 5-1 is also
given in SI form and is implemented with an optional ``unit`` switch.
"""

import math


# ============================================================================
# Eq 5-1 -- one-way slabs/walls without shear reinforcement (printed p. 35)
# ============================================================================

def shear_capacity_one_way_slab(fc_prime, nu, ag, b, d, unit="us"):
    """Eq 5-1: nominal shear capacity of a one-way slab/wall section without
    shear reinforcement (printed p. 35). ACI 318-19's shear-capacity
    requirements for members without shear reinforcement are WAIVED for
    these member types in favor of this equation.

        US:  Vc = [2*sqrt(fc') + Nu/(6*Ag)] * b * d          (fc' psi, Vc lbs)
        SI:  Vc = [0.17*sqrt(fc') + Nu/(6*Ag)] * b * d        (fc' MPa, Vc N)

    Parameters
    ----------
    fc_prime : float
        Concrete compressive strength (psi if unit='us', MPa if unit='si').
    nu : float
        Factored axial load (lbs if unit='us', N if unit='si'); compression
        positive.
    ag : float
        Gross area of the design section (in^2 or mm^2, matching unit).
    b, d : float
        Section width and effective depth (in. or mm, matching unit).
    unit : str, optional
        'us' (default) or 'si'.

    Returns
    -------
    dict
        {'vc', 'equation': '5-1', 'printed_page': '35', 'pdf_page': 40}
    """
    if unit == "us":
        coeff = 2.0 * math.sqrt(fc_prime)
    elif unit == "si":
        coeff = 0.17 * math.sqrt(fc_prime)
    else:
        raise ValueError(f"unit must be 'us' or 'si', got {unit!r}")
    vc = (coeff + nu / (6.0 * ag)) * b * d
    return {"vc": vc, "equation": "5-1", "printed_page": "35", "pdf_page": 40}


# ============================================================================
# Eq 5-2, 5-3 -- special straight members (printed pp. 37-38)
# ============================================================================

def shear_capacity_special_straight_member(fc_prime, ln, nu, ag, b, d):
    """Eq 5-2 with the Eq 5-3 upper limits: shear capacity of special
    straight members (box-culvert sections, gate wells, similar structures
    meeting paragraph 5-4c) at the critical section 0.15*ln from the face of
    support (printed pp. 37-38). U.S. (standard) units only: fc' in psi, Nu
    in lbs, Vc in lbs.

        Vc = (11.5 - ln/d) * sqrt(fc') * sqrt(1 + Nu/(5*Ag*sqrt(fc'))) * b * d   [Eq 5-2]
        Vc <= 2*[12 - (ln/d)]*sqrt(fc')*b*d                                       [Eq 5-3, first limit]
        Vc <= 10*sqrt(fc')*b*d                                                     [Eq 5-3, absolute cap]

    Applicability (paragraph 5-4b/c): uniformly (or approximately uniformly)
    distributed load producing shear, flexure, and axial COMPRESSION (not
    tension); rectangular section; ln/d between 1.25 and 9; fc' <= 6,000 psi;
    rigid continuous joints/corners; straight full-length flexural
    reinforcement extended around corners and through supports.

    Verified against Appendix D-6 (fc'=4,000 psi, ln=120 in, d=24 in,
    Nu=31,700 lbs, Ag=336 sq in, b=12 in): Vc = 134,906 lbs (134.9 kips);
    the Eq 5-3 absolute cap for that section is 182,147 lbs (not governing).

    Returns
    -------
    dict
        {'vc', 'vc_limit_1' (Eq 5-3 first form), 'vc_limit_abs' (10*sqrt(fc')*b*d),
         'vc_governing', 'ln_over_d', 'applicable' (bool, ln/d in [1.25, 9]),
         'equation': '5-2/5-3', 'printed_page': '37-38', 'pdf_page': '42-43'}
    """
    ln_over_d = ln / d
    sqrt_fc = math.sqrt(fc_prime)
    vc = (11.5 - ln_over_d) * sqrt_fc * math.sqrt(1 + nu / (5 * ag * sqrt_fc)) * b * d
    vc_limit_1 = 2 * (12 - ln_over_d) * sqrt_fc * b * d
    vc_limit_abs = 10 * sqrt_fc * b * d
    vc_governing = min(vc, vc_limit_1, vc_limit_abs)
    return {
        "vc": vc, "vc_limit_1": vc_limit_1, "vc_limit_abs": vc_limit_abs,
        "vc_governing": vc_governing, "ln_over_d": ln_over_d,
        "applicable": 1.25 <= ln_over_d <= 9 and fc_prime <= 6000,
        "equation": "5-2/5-3", "printed_page": "37-38", "pdf_page": "42-43",
    }


# ============================================================================
# Eq 5-4 -- curved members (printed p. 38)
# ============================================================================

def shear_capacity_curved_member(fc_prime, nu, ag, b, d, radius=None):
    """Eq 5-4: shear capacity at points of maximum shear for uniformly
    loaded, curved, cast-in-place members with R/d > 2.25 (R = radius of
    curvature to the member centerline) (printed p. 38). U.S. (standard)
    units only: fc' in psi, Nu in lbs, Vc in lbs.

        Vc = 4*sqrt(fc') * sqrt(1 + Nu/(4*Ag*sqrt(fc'))) * b * d
        Vc <= 10*sqrt(fc') * b * d

    Verified against Appendix D-7 (fc'=4,000 psi, Nu=162,500 lbs,
    Ag=576 sq in, b=12 in, d=43.5 in): Vc = 192,058 lbs (192.1 kips); the
    absolute cap for that section is 330,142 lbs (not governing).

    Parameters
    ----------
    radius : float, optional
        Radius of curvature to the member centerline, in. If given, the
        R/d > 2.25 applicability check is included in the result.

    Returns
    -------
    dict
        {'vc', 'vc_limit_abs', 'vc_governing', 'applicable' (bool or None
         if radius not given), 'equation': '5-4', 'printed_page': '38',
         'pdf_page': 43}
    """
    sqrt_fc = math.sqrt(fc_prime)
    vc = 4 * sqrt_fc * math.sqrt(1 + nu / (4 * ag * sqrt_fc)) * b * d
    vc_limit_abs = 10 * sqrt_fc * b * d
    vc_governing = min(vc, vc_limit_abs)
    applicable = (radius / d > 2.25) if radius is not None else None
    return {
        "vc": vc, "vc_limit_abs": vc_limit_abs, "vc_governing": vc_governing,
        "applicable": applicable, "equation": "5-4", "printed_page": "38",
        "pdf_page": 43,
    }


# ============================================================================
# Table G-1 -- ACI 318-19 vs. pre-ACI-318-19 shear coefficient comparison
# (Appendix G commentary, printed p. 125)
# ============================================================================

_TABLE_G_1 = {
    12: 1.54, 24: 1.25, 36: 1.06, 48: 0.93, 60: 0.84,
    72: 0.78, 84: 0.72, 96: 0.68, 108: 0.64, 120: 0.61,
}


def table_g1_shear_coefficient(thickness_in):
    """Table G-1: ACI 318-19's shear coefficient 8*lambda_s*rho_w^(1/3) at
    rho_w = 0.25*rho_b, fc' = 4,000 psi, fy = 60,000 psi, cover = 3 in, for
    the tabulated member thicknesses (Appendix G commentary, printed p. 125).

    Illustrates why this manual retained the pre-ACI-318-19 Eq 5-1 (fixed
    coefficient of 2.0) instead of adopting ACI 318-19's size- and
    reinforcement-ratio-dependent coefficient, which the table shows falling
    below 2.0 at every tabulated thickness and dropping toward 0.6 at large
    (RCHS-typical) thickness.

    Parameters
    ----------
    thickness_in : float
        Member thickness, in. Must be one of the 10 tabulated values
        (12, 24, ..., 120); this is a printed lookup table, not an
        interpolation formula.

    Returns
    -------
    dict
        {'thickness_in', 'coefficient', 'table': 'G-1', 'printed_page': '125',
         'pdf_page': 130}
    """
    if thickness_in not in _TABLE_G_1:
        raise ValueError(
            f"Table G-1 is tabulated only at {sorted(_TABLE_G_1)} in.; "
            f"got {thickness_in}. This is a printed lookup table, not an "
            "interpolation formula."
        )
    return {
        "thickness_in": thickness_in, "coefficient": _TABLE_G_1[thickness_in],
        "table": "G-1", "printed_page": "125", "pdf_page": 130,
    }
