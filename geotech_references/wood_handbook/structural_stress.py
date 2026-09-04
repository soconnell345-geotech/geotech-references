"""Wood Handbook Chapter 9 -- Structural Analysis Equations: Stress
Equations (axial, bending, size effect, notches, combined loading,
torsion; printed pp. 9-6 to 9-12).

Provides:
  - ``axial_stress`` (Eq 9-12, tension positive / short-block compression).
  - ``bending_stress`` (Eq 9-13) with ``section_modulus`` helper.
  - ``beam_shear_stress`` (Eq 9-14).
  - ``tapered_beam_stresses`` (Eq 9-16) and ``tapered_beam_interaction``
    (Eq 9-15, the Hankinson-form Norris interaction criterion applied to
    the combined stress state at a tapered edge).
  - Size effect: ``size_effect_ratio_two_point_vs_concentrated`` (Eq 9-17
    general form, Eq 9-18 factored worked form), ``size_effect_ratio_
    uniform_vs_concentrated`` (Eq 9-19), ``shear_strength_size_adjusted``
    (Eq 9-20).
  - ``crack_initiation_check`` (Eq 9-21, with the Figure 9-14 A/B
    coefficient table).
  - ``combined_bending_axial_stress`` (Eq 9-22, concentric) and
    ``eccentric_bending_axial_stress`` (the printed ft_max/fc_max
    examples for eccentric axial load).
  - ``torsional_shear_stress_circular`` (Eq 9-23) and
    ``torsional_shear_stress_rectangular`` (Eq 9-24, using the closed-form
    reproduction of the Figure 9-15 beta coefficient).

All printed citations use the PRINTED page of General Technical Report
FPL-GTR-282 (2021 edition); ``pdf_page = printed_page + 231`` for Chapter 9
in this PDF (0-based PyMuPDF page index).

UNITS: consistent SI throughout unless documented otherwise.
"""

import math

# ============================================================================
# Eq 9-12 -- Axial stress (printed p. 9-6, pdf_page 237)
# ============================================================================

def axial_stress(axial_load, area):
    """Eq 9-12: uniform axial stress from a concentric axial load (printed
    p. 9-6). Tension positive (ft = +P/A); the same equation applies to
    short-block compression with a negative sign convention (fc = -P/A,
    valid while the member is short enough to fail by fiber crushing
    without buckling).

        f = P / A

    Parameters
    ----------
    axial_load : float
        P, axial load (positive = tension, negative = compression, per
        the caller's sign convention).
    area : float
        A, cross-sectional area.

    Returns
    -------
    dict
        {'axial_load', 'area', 'stress', 'equation': '9-12', ...}
    """
    f = axial_load / area
    return {"axial_load": axial_load, "area": area, "stress": f,
            "equation": "9-12", "printed_page": "9-6", "pdf_page": 237}


# ============================================================================
# Eq 9-13, 9-14 -- Straight beam stresses (printed p. 9-7, pdf_page 238)
# ============================================================================

def section_modulus(shape, b_or_d, h=None):
    """Elastic section modulus S used in Eq 9-13 (printed p. 9-7):
    S = b*h^2/6 for rectangular, S = pi*D^3/32 for circular.

    Parameters
    ----------
    shape : str
        'rectangular' or 'circular'.
    b_or_d : float
        Beam width b (rectangular) or diameter D (circular).
    h : float, optional
        Beam depth (rectangular only).

    Returns
    -------
    dict
        {'shape', 's', 'printed_page': '9-7', ...}
    """
    if shape == "rectangular":
        if h is None:
            raise ValueError("h is required for shape='rectangular'")
        s = b_or_d * h**2 / 6.0
    elif shape == "circular":
        s = math.pi * b_or_d**3 / 32.0
    else:
        raise ValueError(f"shape must be 'rectangular' or 'circular', got {shape!r}")
    return {"shape": shape, "s": s, "printed_page": "9-7", "pdf_page": 238}


def bending_stress(moment, section_modulus_value):
    """Eq 9-13: maximum bending stress at the extreme top/bottom fibers of
    a beam cross section (printed p. 9-7). Also used beyond the limits of
    Hooke's law with M as the ultimate moment at failure, giving the
    "modulus of rupture" (Table 5-3 values).

        fb = M / S

    Parameters
    ----------
    moment : float
        M, bending moment.
    section_modulus_value : float
        S (``section_modulus``).

    Returns
    -------
    dict
        {'moment', 's', 'bending_stress', 'equation': '9-13', ...}
    """
    fb = moment / section_modulus_value
    return {"moment": moment, "s": section_modulus_value, "bending_stress": fb,
            "equation": "9-13", "printed_page": "9-7", "pdf_page": 238}


def beam_shear_stress(shear_force, area, shape="rectangular"):
    """Eq 9-14: maximum shear stress acting on a beam cross section of
    uniform, solid section, at the neutral axis (printed p. 9-8).

        fv = k*V/A,  k = 3/2 (rectangular) or 4/3 (circular)

    For an I-shape, conservatively estimate shear capacity using the
    rectangular web alone.

    Parameters
    ----------
    shear_force : float
        V, vertical shear force on the cross section.
    area : float
        A, cross-sectional area.
    shape : str, optional
        'rectangular' (default, k=3/2) or 'circular' (k=4/3).

    Returns
    -------
    dict
        {'shear_force', 'area', 'k', 'shear_stress', 'equation': '9-14', ...}
    """
    if shape == "rectangular":
        k = 1.5
    elif shape == "circular":
        k = 4.0 / 3.0
    else:
        raise ValueError(f"shape must be 'rectangular' or 'circular', got {shape!r}")
    fv = k * shear_force / area
    return {"shear_force": shear_force, "area": area, "k": k, "shear_stress": fv,
            "equation": "9-14", "printed_page": "9-8", "pdf_page": 239}


# ============================================================================
# Eq 9-15, 9-16 -- Tapered beam stresses (printed p. 9-9, pdf_page 240)
# ============================================================================

def tapered_beam_stresses(moment, b, h0, theta_rad):
    """Eq 9-16: combined stress state (bending fx, shear fxy, perpendicular
    tension/compression fy) at the tapered edge of a beam of constant
    width b that tapers in depth at angle theta (printed p. 9-9, valid
    for taper slopes < 25 degrees).

        fx = 3*M / (2*b*h0^2)
        fxy = fx * tan(theta)
        fy = fx * tan(theta)^2

    Worked example (printed): b=100 mm, h0=200 mm, tan(theta)=1/10 gives
    fx=375*M, fxy=37.5*M, fy=3.75*M (M in N*m, stresses in Pa).

    Parameters
    ----------
    moment : float
        M, bending moment at the cross section of interest.
    b : float
        Beam width (constant).
    h0 : float
        Beam depth at the reaction (shallow end).
    theta_rad : float
        theta, angle of the tapered beam profile (radians).

    Returns
    -------
    dict
        {'fx', 'fxy', 'fy', 'equation': '9-16', ...}
    """
    fx = 3.0 * moment / (2.0 * b * h0**2)
    t = math.tan(theta_rad)
    fxy = fx * t
    fy = fx * t**2
    return {
        "moment": moment, "b": b, "h0": h0, "theta_rad": theta_rad,
        "fx": fx, "fxy": fxy, "fy": fy, "equation": "9-16",
        "printed_page": "9-9", "pdf_page": 240,
    }


def tapered_beam_interaction(fx, fxy, fy, fx_allow, fxy_allow, fy_allow):
    """Eq 9-15: Norris (1950) interaction criterion for the combined
    stress state at a tapered beam edge, based on the Henky-von Mises
    distortion-energy theory (printed p. 9-9).

        (fx/Fx)^2 + (fxy/Fxy)^2 + (fy/Fy)^2 = 1  (at failure)

    Parameters
    ----------
    fx, fxy, fy : float
        Applied bending, shear, and perpendicular-to-neutral-axis
        stresses at the tapered edge (Eq 9-16).
    fx_allow, fxy_allow, fy_allow : float
        Corresponding allowable/design or maximum (Fx=Fb, Fxy=Fv,
        Fy=Ft-perp or Fc-perp) stresses.

    Returns
    -------
    dict
        {'interaction_value' (<=1.0 is OK), 'equation': '9-15', ...}
    """
    value = (fx / fx_allow) ** 2 + (fxy / fxy_allow) ** 2 + (fy / fy_allow) ** 2
    return {
        "fx": fx, "fxy": fxy, "fy": fy, "interaction_value": value,
        "equation": "9-15", "printed_page": "9-9", "pdf_page": 240,
    }


# ============================================================================
# Eq 9-17 to 9-20 -- Size effect (printed pp. 9-10 to 9-11, pdf_page 241-242)
# ============================================================================

def size_effect_ratio_two_point_vs_concentrated(h1, l1, a1, h2, l2, a2, m=18.0):
    """Eq 9-17: ratio of modulus of rupture of beam 1 to beam 2, for two
    beams under two equal concentrated loads placed symmetrically about
    midspan (weakest-link statistical strength theory) (printed p. 9-10).

        R1/R2 = [h2*L2*(1+m*a2/L2) / (h1*L1*(1+m*a1/L1))] ^ (1/m)

    Parameters
    ----------
    h1, l1, a1 : float
        Depth, span, and load spacing (loads placed a/2 each side of
        midspan) of beam 1.
    h2, l2, a2 : float
        Same for beam 2.
    m : float, optional
        Empirically determined material constant (default 18, per
        Bohannan 1966 for clear, straight-grained Douglas-fir).

    Returns
    -------
    dict
        {'ratio_r1_r2', 'equation': '9-17', ...}
    """
    ratio = (h2 * l2 * (1.0 + m * a2 / l2) / (h1 * l1 * (1.0 + m * a1 / l1))) ** (1.0 / m)
    return {
        "h1": h1, "l1": l1, "a1": a1, "h2": h2, "l2": l2, "a2": a2, "m": m,
        "ratio_r1_r2": ratio, "equation": "9-17", "printed_page": "9-10", "pdf_page": 241,
    }


def size_effect_midspan_reference(r2, h1, l1, a1, m=18.0, units="metric"):
    """Eq 9-18: modulus of rupture R1 of a beam under two-point (or
    third-point, etc.) bending, referenced to R2 measured on a beam of
    depth 50.8 mm (2 in.) and span 711.12 mm (28 in.) loaded at midspan
    (printed p. 9-10, factored from Eq 9-17 with h2/L2 fixed and a2=0).

        R1 = R2 * [36125 / (h1*L1*(1+m*a1/L1))] ^ (1/m)   (MPa, metric)
        R1 = R2 * [56 / (h1*L1*(1+m*a1/L1))] ^ (1/m)       (lbf/in^2, inch-pound)

    Worked example (printed): h1=10 in, L1=18 ft=216 in, third-point
    loading (a1/L1=1/3), R2=10,000 lbf/in^2, m=18 -> R1 = 7,330 lbf/in^2.

    Parameters
    ----------
    r2 : float
        Modulus of rupture of the h2=50.8 mm / L2=711.12 mm midspan-
        loaded reference beam.
    h1, l1, a1 : float
        Depth, span, and load spacing of beam 1 (consistent units: mm for
        'metric', inches for 'inch-pound').
    m : float, optional
        Material constant (default 18).
    units : str, optional
        'metric' (Eq 9-18a, constant 36125, R in MPa) or 'inch-pound'
        (Eq 9-18b, constant 56, R in lbf/in^2).

    Returns
    -------
    dict
        {'r1', 'equation': '9-18a' or '9-18b', ...}
    """
    if units == "metric":
        constant, eq = 36125.0, "9-18a"
    elif units == "inch-pound":
        constant, eq = 56.0, "9-18b"
    else:
        raise ValueError(f"units must be 'metric' or 'inch-pound', got {units!r}")
    r1 = r2 * (constant / (h1 * l1 * (1.0 + m * a1 / l1))) ** (1.0 / m)
    return {
        "r2": r2, "h1": h1, "l1": l1, "a1": a1, "m": m, "units": units,
        "r1": r1, "equation": eq, "printed_page": "9-10", "pdf_page": 241,
    }


def size_effect_ratio_uniform_vs_concentrated(hu, lu, hc, lc, ac, m=18.0):
    """Eq 9-19: ratio of modulus of rupture of a beam under uniformly
    distributed load (subscript u) to a beam under two-point concentrated
    load (subscript c) (printed p. 9-11, Liu 1982).

        Ru/Rc = [(1+18*ac/Lc)*hc*Lc / (3.876*hu*Lu)] ^ (1/18)

    Parameters
    ----------
    hu, lu : float
        Depth and span of the uniformly loaded beam.
    hc, lc, ac : float
        Depth, span, and load spacing of the two-point-loaded beam.
    m : float, optional
        Material constant (default 18, fixed by fitting Douglas-fir data
        as printed; the exponent 1/18 in the printed equation is not
        parameterized independently of m in the source, so m is exposed
        here only for consistency with Eq 9-17/9-18 -- leave at 18 unless
        a source-documented alternative is available).

    Returns
    -------
    dict
        {'ratio_ru_rc', 'equation': '9-19', ...}
    """
    ratio = ((1.0 + 18.0 * ac / lc) * hc * lc / (3.876 * hu * lu)) ** (1.0 / m)
    return {
        "hu": hu, "lu": lu, "hc": hc, "lc": lc, "ac": ac, "m": m,
        "ratio_ru_rc": ratio, "equation": "9-19", "printed_page": "9-11", "pdf_page": 242,
    }


def shear_strength_size_adjusted(cf, tau_astm, area, units="metric"):
    """Eq 9-20: beam shear strength adjusted for size and the shear-block
    re-entrant-corner stress concentration, from ASTM D143 shear block
    strength (printed p. 9-11, Rammer and Soltis 1994; Rammer and others
    1996).

        tau = 1.9*Cf*tau_ASTM / A^(1/5)   (MPa, cm^2; metric)
        tau = 1.3*Cf*tau_ASTM / A^(1/5)   (lbf/in^2, in^2; inch-pound)

    Parameters
    ----------
    cf : float
        Stress concentration factor for the shear block re-entrant
        corner (approximately 2).
    tau_astm : float
        ASTM D143 shear block strength.
    area : float
        A, shear area (beam width x length of beam subjected to shear
        force; cm^2 for metric, in^2 for inch-pound).
    units : str, optional
        'metric' (Eq 9-20a) or 'inch-pound' (Eq 9-20b).

    Returns
    -------
    dict
        {'tau', 'equation': '9-20a' or '9-20b', ...}
    """
    if units == "metric":
        constant, eq = 1.9, "9-20a"
    elif units == "inch-pound":
        constant, eq = 1.3, "9-20b"
    else:
        raise ValueError(f"units must be 'metric' or 'inch-pound', got {units!r}")
    tau = constant * cf * tau_astm / area ** (1.0 / 5.0)
    return {
        "cf": cf, "tau_astm": tau_astm, "area": area, "units": units,
        "tau": tau, "equation": eq, "printed_page": "9-11", "pdf_page": 242,
    }


# ============================================================================
# Eq 9-21 -- Crack initiation at notches/slits (printed p. 9-12, pdf_page 243)
# ============================================================================

# Figure 9-14: coefficients A (tension-edge At, compression-edge Ac) and B
# for the crack-initiation criterion, as a function of slit-depth ratio
# a/h. Units: A, B in (kPa*sqrt(mm))^-1 x 1e-4 as plotted. Values below are
# a visual digitization of the printed curves at a/h = 0, 0.1, ..., 0.5,
# 0.55 (nearest ~0.05 gridline on the plotted 1e-4 scale); piecewise-linear
# interpolation between them approximates the printed curves. The
# handbook's own text notes these curve values are already conservative
# estimates for most softwood species -- treat this digitization as an
# approximate figure read, not an exact table value.
FIGURE_9_14_AB = [
    # (a/h, A_tension, A_compression, B)  -- units 1e-4 (kPa*sqrt(mm))^-1
    (0.0, 0.00, 0.00, 0.00),
    (0.1, 0.05, 0.03, 0.35),
    (0.2, 0.15, 0.07, 0.65),
    (0.3, 0.25, 0.10, 1.00),
    (0.4, 0.45, 0.15, 1.35),
    (0.5, 0.60, 0.20, 1.75),
    (0.55, 0.70, 0.25, 2.00),
]


def figure_9_14_coefficients(a_over_h, edge="tension"):
    """Figure 9-14: coefficients A (tension- or compression-edge slit) and
    B for the crack-initiation criterion (Eq 9-21), by slit-depth ratio
    a/h (printed p. 9-12). Linearly interpolated between the printed
    curve's plotted stations; conservative for most softwood species per
    the handbook text.

    Parameters
    ----------
    a_over_h : float
        a/h, slit depth over beam depth (0 to ~0.55, the plotted range).
    edge : str, optional
        'tension' (default, uses At) or 'compression' (uses Ac).

    Returns
    -------
    dict
        {'a_over_h', 'edge', 'a_coefficient', 'b_coefficient',
         'figure': '9-14', ...}
    """
    if edge not in ("tension", "compression"):
        raise ValueError(f"edge must be 'tension' or 'compression', got {edge!r}")
    pts = FIGURE_9_14_AB
    if not (pts[0][0] <= a_over_h <= pts[-1][0]):
        raise ValueError(f"a_over_h={a_over_h} outside the digitized Figure 9-14 range [0, 0.55]")
    a_idx = 1 if edge == "tension" else 2
    for i in range(len(pts) - 1):
        x0, x1 = pts[i][0], pts[i + 1][0]
        if x0 <= a_over_h <= x1:
            frac = 0.0 if x1 == x0 else (a_over_h - x0) / (x1 - x0)
            a_val = pts[i][a_idx] + frac * (pts[i + 1][a_idx] - pts[i][a_idx])
            b_val = pts[i][3] + frac * (pts[i + 1][3] - pts[i][3])
            break
    return {
        "a_over_h": a_over_h, "edge": edge,
        "a_coefficient": a_val * 1e-4, "b_coefficient": b_val * 1e-4,
        "figure": "9-14", "printed_page": "9-12", "pdf_page": 243,
    }


def crack_initiation_check(h, b, moment, shear_force, a_coefficient, b_coefficient):
    """Eq 9-21: conservative fracture-mechanics criterion for crack
    initiation at a beam slit/notch (printed p. 9-12, after Murphy 1979).

        sqrt(h) * [A*(6M/(b*h^2)) + B*(3V/(2*b*h))] = 1   (at crack initiation)

    A value of the left side < 1 indicates the beam is below the crack-
    initiation load; >= 1 indicates crack initiation is predicted.

    Parameters
    ----------
    h : float
        Beam depth.
    b : float
        Beam width.
    moment : float
        M, bending moment.
    shear_force : float
        V, vertical shear force.
    a_coefficient, b_coefficient : float
        A, B from Figure 9-14 (``figure_9_14_coefficients``), matched to
        units of h (sqrt(length)) and stress.

    Returns
    -------
    dict
        {'criterion_value', 'crack_predicted' (bool), 'equation': '9-21', ...}
    """
    value = math.sqrt(h) * (
        a_coefficient * (6.0 * moment / (b * h**2))
        + b_coefficient * (3.0 * shear_force / (2.0 * b * h))
    )
    return {
        "h": h, "b": b, "moment": moment, "shear_force": shear_force,
        "criterion_value": value, "crack_predicted": value >= 1.0,
        "equation": "9-21", "printed_page": "9-12", "pdf_page": 243,
    }


# ============================================================================
# Eq 9-22 -- Combined bending and axial stress (printed p. 9-12, pdf_page 243)
# ============================================================================

def combined_bending_axial_stress(fb0, axial_load, area, p_critical, is_tension):
    """Eq 9-22: net bending stress from combined bending and concentric
    axial load, on a simply supported, pin-ended beam (printed p. 9-12).
    Total stress is by superposition of this with Eq 9-12 (fb + P/A).

        fb = fb0 / (1 +/- P/Pcr)   (+ tension, - compression)

    Worked example forms (printed): with fb0 tensile on the convex edge
    and compressive on the concave edge, and an added tensile axial force P:
        ft_max = fb0/(1+P/Pcr) + P/A   (convex edge)
        fc_max = fb0/(1+P/Pcr) - P/A   (concave edge; negative result means
                                         the stress is actually tensile)

    Parameters
    ----------
    fb0 : float
        Bending stress without axial load.
    axial_load : float
        P, axial load (magnitude).
    area : float
        A, cross-sectional area.
    p_critical : float
        Pcr, buckling load of the beam under axial compression alone.
    is_tension : bool
        True for tension ('+'), False for compression ('-'; check P < Pcr
        and possible buckling under combined loading, Eq 9-36).

    Returns
    -------
    dict
        {'fb', 'ft_max', 'fc_max', 'equation': '9-22', ...}
    """
    sign = 1.0 if is_tension else -1.0
    fb = fb0 / (1.0 + sign * axial_load / p_critical)
    axial_stress_value = axial_load / area
    return {
        "fb0": fb0, "axial_load": axial_load, "area": area,
        "p_critical": p_critical, "is_tension": is_tension, "fb": fb,
        "ft_max": fb + axial_stress_value, "fc_max": fb - axial_stress_value,
        "equation": "9-22", "printed_page": "9-12", "pdf_page": 243,
    }


def eccentric_bending_axial_stress(fb0, eccentricity, section_modulus_value,
                                    axial_load, area, p_critical, is_tension):
    """Printed p. 9-12: maximum tensile/compressive stresses under an
    eccentrically applied axial load added to transverse bending (fb0
    tensile on the convex edge, compressive on the concave edge). The
    bending stress fb0 is augmented by +/- P*e0/S before applying the
    Eq 9-22 amplification.

        ft_max = (fb0 - P*e0/S)/(1+P/Pcr) + P/A
        fc_max = (fb0 - P*e0/S)/(1+P/Pcr) - P/A

    Parameters
    ----------
    fb0 : float
        Bending stress without axial load (tensile on convex edge).
    eccentricity : float
        e0, eccentricity of the axial load from the centroidal axis
        (negative if applied to create convex curvature opposite Fig 9-7).
    section_modulus_value : float
        S (``section_modulus``).
    axial_load : float
        P, axial load (magnitude).
    area : float
        A, cross-sectional area.
    p_critical : float
        Pcr, buckling load under axial compression alone.
    is_tension : bool
        True for tension, False for compression.

    Returns
    -------
    dict
        {'ft_max', 'fc_max', 'printed_page': '9-12', ...}
    """
    sign = 1.0 if is_tension else -1.0
    augmented = fb0 - axial_load * eccentricity / section_modulus_value
    amplified = augmented / (1.0 + sign * axial_load / p_critical)
    axial_stress_value = axial_load / area
    return {
        "fb0": fb0, "eccentricity": eccentricity, "axial_load": axial_load,
        "ft_max": amplified + axial_stress_value,
        "fc_max": amplified - axial_stress_value,
        "printed_page": "9-12", "pdf_page": 243,
    }


# ============================================================================
# Eq 9-23, 9-24 -- Torsional shear stress (printed p. 9-12, pdf_page 243)
# ============================================================================

def torsional_shear_stress_circular(torque, diameter):
    """Eq 9-23: shear stress induced by torsion on a circular cross
    section (printed p. 9-12).

        fs = 16*T / (pi*d^3)

    Parameters
    ----------
    torque : float
        T, applied torsional moment.
    diameter : float
        d, member diameter.

    Returns
    -------
    dict
        {'torque', 'diameter', 'shear_stress', 'equation': '9-23', ...}
    """
    fs = 16.0 * torque / (math.pi * diameter**3)
    return {"torque": torque, "diameter": diameter, "shear_stress": fs,
            "equation": "9-23", "printed_page": "9-12", "pdf_page": 243}


def _beta_rectangular_torsion(b_over_h):
    """Closed-form reproduction of Figure 9-15 (coefficient beta for
    maximum torsional shear stress in a rectangular member): the classical
    Saint-Venant/Roark polynomial for the maximum-shear-stress coefficient
    of a rectangular section, matching the printed curve's endpoints
    (beta=3.0 at b/h=0, beta~4.8 at b/h=1, both read off Fig. 9-15).
    """
    x = b_over_h
    return 3.0 * (1.0 + 0.6095 * x + 0.8865 * x**2 - 1.8023 * x**3 + 0.9100 * x**4)


def torsional_shear_stress_rectangular(torque, h, b):
    """Eq 9-24: maximum shear stress induced by torsion on a rectangular
    cross section (printed p. 9-12, Trayer and March 1930).

        fs = T / (beta*h*b^2)

    where h is the larger cross-section dimension, b the smaller, and beta
    is read from Figure 9-15 as a function of b/h (reproduced here in
    closed form -- see ``_beta_rectangular_torsion``).

    Parameters
    ----------
    torque : float
        T, applied torsional moment.
    h : float
        Larger cross-section dimension.
    b : float
        Smaller cross-section dimension (b <= h).

    Returns
    -------
    dict
        {'torque', 'h', 'b', 'b_over_h', 'beta', 'shear_stress',
         'equation': '9-24', ...}
    """
    if b > h:
        raise ValueError("b must be <= h (b is the smaller cross-section dimension)")
    b_over_h = b / h
    beta = _beta_rectangular_torsion(b_over_h)
    fs = torque / (beta * h * b**2)
    return {
        "torque": torque, "h": h, "b": b, "b_over_h": b_over_h, "beta": beta,
        "shear_stress": fs, "equation": "9-24", "printed_page": "9-12", "pdf_page": 243,
    }
