"""Wood Handbook Chapter 9 -- Structural Analysis Equations: Deformation
Equations (axial, bending, torsion; printed pp. 9-2 to 9-6).

Provides:
  - ``axial_deformation`` (Eq 9-1).
  - ``straight_beam_deflection`` (Eq 9-2) with ``TABLE_9_1_KB_KS`` (Table
    9-1, kb/ks for 8 loading cases) and ``section_moment_of_inertia`` /
    ``section_modified_shear_area`` (Eq 9-3/9-4).
  - ``tapered_beam_shear_deflection`` (Eq 9-5).
  - ``ponding_deflection_amplification`` (Eq 9-6).
  - ``combined_bending_axial_deflection`` (Eq 9-7, concentric),
    ``eccentric_axial_bending_deflection`` (Eq 9-8).
  - ``angle_of_twist`` (Eq 9-9) with ``torsional_constant_circular``
    (Eq 9-10) and ``torsional_constant_rectangular`` (Eq 9-11, using the
    closed-form Saint-Venant rectangular-torsion stiffness coefficient
    that Figure 9-9 plots -- see that function's docstring).

All printed citations use the PRINTED page of General Technical Report
FPL-GTR-282 (2021 edition); ``pdf_page = printed_page + 231`` for Chapter 9
in this PDF (0-based PyMuPDF page index), e.g. printed p. 9-2 = pdf_page 233.

UNITS: consistent SI (N, m, Pa) throughout unless documented otherwise; any
consistent unit system works since these are dimensionally homogeneous
mechanics-of-materials equations.
"""

import math

# ============================================================================
# Eq 9-1 -- Axial load deformation (printed p. 9-2, pdf_page 233)
# ============================================================================

def axial_deformation(axial_force, length, area, modulus_of_elasticity):
    """Eq 9-1: change of length of an axially loaded member (printed p. 9-2).

        delta = P*L / (A*E)

    Parameters
    ----------
    axial_force : float
        P, axial force parallel to the member axis (positive = tension).
    length : float
        L, initial length.
    area : float
        A, cross-sectional area.
    modulus_of_elasticity : float
        E, modulus of elasticity (E_L when grain runs parallel to the
        member axis).

    Returns
    -------
    dict
        {'axial_force', 'length', 'area', 'modulus_of_elasticity',
         'deformation', 'equation': '9-1', ...}
    """
    delta = axial_force * length / (area * modulus_of_elasticity)
    return {
        "axial_force": axial_force, "length": length, "area": area,
        "modulus_of_elasticity": modulus_of_elasticity, "deformation": delta,
        "equation": "9-1", "printed_page": "9-2", "pdf_page": 233,
    }


# ============================================================================
# Eq 9-2, 9-3, 9-4, Table 9-1 -- Straight beam deflection
# (printed pp. 9-2 to 9-3, pdf_page 233-234)
# ============================================================================

# (loading, support) -> (kb, ks, deflection_at). Table 9-1 (printed p. 9-3).
TABLE_9_1_KB_KS = {
    ("uniformly_distributed", "simply_supported"): {"kb": 5.0 / 384, "ks": 1.0 / 8, "deflection_at": "midspan"},
    ("uniformly_distributed", "clamped"): {"kb": 1.0 / 384, "ks": 1.0 / 8, "deflection_at": "midspan"},
    ("concentrated_midspan", "simply_supported"): {"kb": 1.0 / 48, "ks": 1.0 / 4, "deflection_at": "midspan"},
    ("concentrated_midspan", "clamped"): {"kb": 1.0 / 192, "ks": 1.0 / 4, "deflection_at": "midspan"},
    ("concentrated_quarter_points", "simply_supported"): {"kb": 11.0 / 768, "ks": 1.0 / 8, "deflection_at": "midspan"},
    ("concentrated_quarter_points", "clamped"): {"kb": 1.0 / 96, "ks": 1.0 / 8, "deflection_at": "load_point"},
    ("uniformly_distributed", "cantilever"): {"kb": 1.0 / 8, "ks": 1.0 / 2, "deflection_at": "free_end"},
    ("concentrated_free_end", "cantilever"): {"kb": 1.0 / 3, "ks": 1.0, "deflection_at": "free_end"},
}


def table_9_1_kb_ks(loading, support):
    """Table 9-1: kb/ks deflection constants by loading and support
    condition, for use in ``straight_beam_deflection`` (Eq 9-2) (printed
    p. 9-3).

    Parameters
    ----------
    loading : str
        'uniformly_distributed', 'concentrated_midspan',
        'concentrated_quarter_points' (two loads at the outer quarter-span
        points), or 'concentrated_free_end' (cantilever only).
    support : str
        'simply_supported', 'clamped' (both ends), or 'cantilever' (one
        free, one clamped).

    Returns
    -------
    dict
        {'loading', 'support', 'kb', 'ks', 'deflection_at', 'table': '9-1', ...}
    """
    key = (loading, support)
    if key not in TABLE_9_1_KB_KS:
        raise ValueError(f"(loading, support) must be one of {sorted(TABLE_9_1_KB_KS)}, got {key!r}")
    row = TABLE_9_1_KB_KS[key]
    return {
        "loading": loading, "support": support, "kb": row["kb"], "ks": row["ks"],
        "deflection_at": row["deflection_at"], "table": "9-1",
        "printed_page": "9-3", "pdf_page": 234,
    }


def section_moment_of_inertia(shape, b_or_d, h=None):
    """Eq 9-3: moment of inertia I about the centroidal axis (printed p. 9-3).

        I = b*h^3/12   for a beam of rectangular cross section
        I = pi*d^4/64  for a beam of circular cross section

    Parameters
    ----------
    shape : str
        'rectangular' or 'circular'.
    b_or_d : float
        Beam width b (rectangular) or diameter d (circular).
    h : float, optional
        Beam depth (rectangular only; required if shape='rectangular').

    Returns
    -------
    dict
        {'shape', 'i', 'equation': '9-3', ...}
    """
    if shape == "rectangular":
        if h is None:
            raise ValueError("h is required for shape='rectangular'")
        i = b_or_d * h**3 / 12.0
    elif shape == "circular":
        i = math.pi * b_or_d**4 / 64.0
    else:
        raise ValueError(f"shape must be 'rectangular' or 'circular', got {shape!r}")
    return {"shape": shape, "i": i, "equation": "9-3", "printed_page": "9-3", "pdf_page": 234}


def section_modified_shear_area(shape, b_or_d, h=None):
    """Eq 9-4: modified area A' for shear deflection (printed p. 9-3).

        A' = (5/6)*b*h    for a beam of rectangular cross section
        A' = (9/40)*pi*d^2  for a beam of circular cross section

    Parameters
    ----------
    shape : str
        'rectangular' or 'circular'.
    b_or_d : float
        Beam width b (rectangular) or diameter d (circular).
    h : float, optional
        Beam depth (rectangular only; required if shape='rectangular').

    Returns
    -------
    dict
        {'shape', 'a_prime', 'equation': '9-4', ...}
    """
    if shape == "rectangular":
        if h is None:
            raise ValueError("h is required for shape='rectangular'")
        a_prime = (5.0 / 6.0) * b_or_d * h
    elif shape == "circular":
        a_prime = (9.0 / 40.0) * math.pi * b_or_d**2
    else:
        raise ValueError(f"shape must be 'rectangular' or 'circular', got {shape!r}")
    return {"shape": shape, "a_prime": a_prime, "equation": "9-4", "printed_page": "9-3", "pdf_page": 234}


def straight_beam_deflection(kb, ks, w_total, length, moment_of_inertia,
                              modified_area, modulus_of_elasticity, shear_modulus):
    """Eq 9-2: deflection of a straight, elastically stressed beam of
    constant cross section (printed p. 9-2), as the sum of bending and
    shear deflection.

        delta = kb*W*L^3/(E*I) + ks*W*L/(G*A')

    Parameters
    ----------
    kb, ks : float
        Constants for the loading/support condition and deflection point
        (Table 9-1, ``table_9_1_kb_ks``).
    w_total : float
        W, total beam load acting perpendicular to the beam neutral axis.
    length : float
        L, beam span.
    moment_of_inertia : float
        I, beam moment of inertia (Eq 9-3).
    modified_area : float
        A', modified beam area for shear (Eq 9-4).
    modulus_of_elasticity : float
        E, beam modulus of elasticity (E_L for grain parallel to axis).
    shear_modulus : float
        G, beam shear modulus (G_LT for flat-grained vertical faces, G_LR
        for edge-grained vertical faces).

    Returns
    -------
    dict
        {'deflection_bending', 'deflection_shear', 'deflection_total',
         'equation': '9-2', ...}
    """
    delta_b = kb * w_total * length**3 / (modulus_of_elasticity * moment_of_inertia)
    delta_s = ks * w_total * length / (shear_modulus * modified_area)
    return {
        "kb": kb, "ks": ks, "w_total": w_total, "length": length,
        "deflection_bending": delta_b, "deflection_shear": delta_s,
        "deflection_total": delta_b + delta_s, "equation": "9-2",
        "printed_page": "9-2", "pdf_page": 233,
    }


# ============================================================================
# Eq 9-5 -- Tapered beam shear deflection (printed p. 9-4, pdf_page 235)
# ============================================================================

def tapered_beam_shear_deflection(load, length, shear_modulus, b, h0, loading="uniform"):
    """Eq 9-5: shear deflection of a single- or double-tapered beam
    (printed p. 9-4, Maki and Kuenzi 1965). Total deflection = this shear
    term plus the bending deflection (read from Figs. 9-4/9-5 for tapered
    beams).

        Delta_s = 3*W*L / (20*G*b*h0)   for a uniformly distributed load
        Delta_s = 3*P*L / (10*G*b*h0)   for a midspan-concentrated load

    Parameters
    ----------
    load : float
        W (total, uniformly distributed) or P (concentrated at midspan).
    length : float
        L, beam span.
    shear_modulus : float
        G, beam shear modulus.
    b : float
        Beam width.
    h0 : float
        Depth of the beam at the shallow end (minimum depth).
    loading : str, optional
        'uniform' (default) or 'concentrated_midspan'.

    Returns
    -------
    dict
        {'load', 'length', 'shear_modulus', 'b', 'h0', 'loading',
         'shear_deflection', 'equation': '9-5', ...}
    """
    if loading == "uniform":
        delta_s = 3.0 * load * length / (20.0 * shear_modulus * b * h0)
    elif loading == "concentrated_midspan":
        delta_s = 3.0 * load * length / (10.0 * shear_modulus * b * h0)
    else:
        raise ValueError(f"loading must be 'uniform' or 'concentrated_midspan', got {loading!r}")
    return {
        "load": load, "length": length, "shear_modulus": shear_modulus, "b": b,
        "h0": h0, "loading": loading, "shear_deflection": delta_s,
        "equation": "9-5", "printed_page": "9-4", "pdf_page": 235,
    }


# ============================================================================
# Eq 9-6 -- Water ponding deflection amplification (printed p. 9-5, pdf_page 236)
# ============================================================================

def ponding_deflection_amplification(delta_0, beam_spacing, critical_spacing):
    """Eq 9-6: total elastic deflection due to design load plus ponded
    water (printed p. 9-5, Zahn).

        Delta = Delta_0 / (1 - s/s_cr)

    Parameters
    ----------
    delta_0 : float
        Deflection due to design load alone.
    beam_spacing : float
        s, beam spacing.
    critical_spacing : float
        s_cr, critical beam spacing (Eq 9-32,
        ``structural_stability.critical_ponding_spacing``).

    Returns
    -------
    dict
        {'delta_0', 'beam_spacing', 'critical_spacing', 'delta_total',
         'equation': '9-6', ...}
    """
    delta = delta_0 / (1.0 - beam_spacing / critical_spacing)
    return {
        "delta_0": delta_0, "beam_spacing": beam_spacing,
        "critical_spacing": critical_spacing, "delta_total": delta,
        "equation": "9-6", "printed_page": "9-5", "pdf_page": 236,
    }


# ============================================================================
# Eq 9-7, 9-8 -- Combined bending and axial load deflection
# (printed p. 9-5, pdf_page 236)
# ============================================================================

def combined_bending_axial_deflection(delta_0, axial_load, p_critical, is_tension):
    """Eq 9-7: midspan deflection of a pin-ended (simply supported) member
    under combined transverse bending load and concentric axial load
    (printed p. 9-5).

        Delta = Delta_0 / (1 +/- P/Pcr)   (+ for tension, - for compression)

    Parameters
    ----------
    delta_0 : float
        Beam midspan deflection without axial load.
    axial_load : float
        P, axial load (magnitude).
    p_critical : float
        Pcr, buckling load of the beam under axial compressive load only
        (``structural_stability.euler_critical_stress`` x area, or the
        governing column buckling load).
    is_tension : bool
        True if the axial load is tension (uses '+'), False if
        compression (uses '-'; P must be < Pcr to avoid collapse).

    Returns
    -------
    dict
        {'delta_0', 'axial_load', 'p_critical', 'is_tension', 'delta',
         'equation': '9-7', ...}
    """
    sign = 1.0 if is_tension else -1.0
    delta = delta_0 / (1.0 + sign * axial_load / p_critical)
    return {
        "delta_0": delta_0, "axial_load": axial_load, "p_critical": p_critical,
        "is_tension": is_tension, "delta": delta, "equation": "9-7",
        "printed_page": "9-5", "pdf_page": 236,
    }


def eccentric_axial_bending_deflection(eccentricity, axial_load, p_critical, is_tension):
    """Eq 9-8: bending deflection at midspan induced by an eccentrically
    applied axial load on a simply supported, pin-ended member (printed
    p. 9-5).

        delta_b + e0 = e0 / (1 +/- P/Pcr)

    Parameters
    ----------
    eccentricity : float
        e0, eccentricity of P from the centroidal neutral axis.
    axial_load : float
        P, axial load (magnitude).
    p_critical : float
        Pcr, buckling load of the beam under axial compressive load only.
    is_tension : bool
        True for tension ('+'), False for compression ('-').

    Returns
    -------
    dict
        {'eccentricity', 'axial_load', 'p_critical', 'is_tension',
         'induced_bending_deflection', 'equation': '9-8', ...}
    """
    sign = 1.0 if is_tension else -1.0
    total = eccentricity / (1.0 + sign * axial_load / p_critical)
    delta_b = total - eccentricity
    return {
        "eccentricity": eccentricity, "axial_load": axial_load,
        "p_critical": p_critical, "is_tension": is_tension,
        "induced_bending_deflection": delta_b, "equation": "9-8",
        "printed_page": "9-5", "pdf_page": 236,
    }


# ============================================================================
# Eq 9-9, 9-10, 9-11 -- Torsion (printed pp. 9-5 to 9-6, pdf_page 236-237)
# ============================================================================

def angle_of_twist(torque, length, shear_modulus, torsional_constant):
    """Eq 9-9: angle of twist of a wood member about its longitudinal axis
    (printed p. 9-5).

        theta = T*L / (G*K)

    Parameters
    ----------
    torque : float
        T, applied torque.
    length : float
        L, member length.
    shear_modulus : float
        G, shear modulus (use sqrt(G_LR*G_LT), or approximate G by E_L/16
        if measured G is not available).
    torsional_constant : float
        K, torsional constant dependent on cross-sectional shape (Eq 9-10
        circular, Eq 9-11 rectangular).

    Returns
    -------
    dict
        {'torque', 'length', 'shear_modulus', 'torsional_constant',
         'theta_rad', 'equation': '9-9', ...}
    """
    theta = torque * length / (shear_modulus * torsional_constant)
    return {
        "torque": torque, "length": length, "shear_modulus": shear_modulus,
        "torsional_constant": torsional_constant, "theta_rad": theta,
        "equation": "9-9", "printed_page": "9-5", "pdf_page": 236,
    }


def torsional_constant_circular(diameter):
    """Eq 9-10: torsional constant K for a circular cross section, equal
    to the polar moment of inertia J (printed p. 9-6).

        K = J = pi*D^4/32

    Parameters
    ----------
    diameter : float
        D, member diameter.

    Returns
    -------
    dict
        {'diameter', 'k', 'equation': '9-10', ...}
    """
    k = math.pi * diameter**4 / 32.0
    return {"diameter": diameter, "k": k, "equation": "9-10", "printed_page": "9-6", "pdf_page": 237}


def _phi_rectangular_torsion(b_over_h):
    """Closed-form reproduction of Figure 9-9 (coefficient phi for
    rectangular-member torsional rigidity): phi = 1/k2, where k2 is the
    classical Saint-Venant torsional-stiffness coefficient for a
    rectangular section (Timoshenko). The polynomial below (Roark's
    Formulas for Stress and Strain) reproduces the printed curve to
    within a few percent and matches its two labeled endpoints exactly:
    phi=3.00 at b/h=0 (thin-rectangle limit) and phi=1/0.141=7.09 at
    b/h=1 (square, printed as ~7).
    """
    x = b_over_h
    k2 = (1.0 / 3.0) - 0.21 * x * (1.0 - x**4 / 12.0)
    return 1.0 / k2


def torsional_constant_rectangular(h, b):
    """Eq 9-11: approximate torsional constant K (second polar moment of
    inertia J) for a rectangular cross section (printed p. 9-6, Trayer
    and March 1930).

        K = J ~= h*b^3 / phi

    where h is the larger cross-section dimension, b the smaller, and phi
    is read from Figure 9-9 as a function of b/h (reproduced here in
    closed form -- see ``_phi_rectangular_torsion``).

    Parameters
    ----------
    h : float
        Larger cross-section dimension.
    b : float
        Smaller cross-section dimension (b <= h).

    Returns
    -------
    dict
        {'h', 'b', 'b_over_h', 'phi', 'k', 'equation': '9-11', ...}
    """
    if b > h:
        raise ValueError("b must be <= h (b is the smaller cross-section dimension)")
    b_over_h = b / h
    phi = _phi_rectangular_torsion(b_over_h)
    k = h * b**3 / phi
    return {
        "h": h, "b": b, "b_over_h": b_over_h, "phi": phi, "k": k,
        "equation": "9-11", "printed_page": "9-6", "pdf_page": 237,
    }
