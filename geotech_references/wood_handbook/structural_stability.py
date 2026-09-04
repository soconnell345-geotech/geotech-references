"""Wood Handbook Chapter 9 -- Structural Analysis Equations: Stability
Equations (axial compression columns, beam lateral-torsional buckling,
interaction of buckling modes; printed pp. 9-13 to 9-17).

Provides:
  - Axial Compression: ``euler_critical_stress`` (Eq 9-25) with
    ``radius_of_gyration`` (Eq 9-26); ``ylinen_critical_stress`` (Eq 9-27,
    the FPL fourth-power parabolic form) and ``ylinen_buckling_stress``
    (Eq 9-29, the general Ylinen nonlinear-stress-strain form, with the
    printed c=0.957/0.8/0.9 guidance); ``built_up_column_capacity``
    (Eq 9-30); ``flange_instability_stress`` (Eq 9-31).
  - Bending: ``critical_ponding_spacing`` (Eq 9-32); ``lateral_torsional_
    buckling_stress`` (Eq 9-33) with ``TABLE_9_2_EFFECTIVE_LENGTH`` and
    ``slenderness_factor`` (Eq 9-34); ``deck_shear_stiffness_parameter``
    (Eq 9-35, chart Figure 9-23 not implemented -- see its docstring).
  - Interaction of Buckling Modes: ``biaxial_beam_column_interaction``
    (Eq 9-36) with its moment-magnification (Eq 9-37/9-38) and elastic-
    buckling-stress (Eq 9-39/9-40/9-41) helpers.

All printed citations use the PRINTED page of General Technical Report
FPL-GTR-282 (2021 edition); ``pdf_page = printed_page + 231`` for Chapter 9
in this PDF (0-based PyMuPDF page index).

UNITS: consistent SI throughout unless documented otherwise.
"""

import math

# ============================================================================
# Eq 9-25, 9-26 -- Long columns: Euler buckling (printed p. 9-13, pdf_page 244)
# ============================================================================

def euler_critical_stress(modulus_of_elasticity, unbraced_length, radius_of_gyration_value):
    """Eq 9-25: critical buckling stress of a long column (buckles before
    the compressive stress P/A exceeds the proportional limit), by
    Euler's formula (printed p. 9-13).

        fcr = pi^2 * E_L / (L/r)^2

    Parameters
    ----------
    modulus_of_elasticity : float
        E_L, elastic modulus parallel to the member axis.
    unbraced_length : float
        L, unbraced length.
    radius_of_gyration_value : float
        r, least radius of gyration (Eq 9-26).

    Returns
    -------
    dict
        {'fcr', 'slenderness_ratio' (L/r), 'equation': '9-25', ...}
    """
    slenderness = unbraced_length / radius_of_gyration_value
    fcr = math.pi**2 * modulus_of_elasticity / slenderness**2
    return {
        "modulus_of_elasticity": modulus_of_elasticity, "unbraced_length": unbraced_length,
        "radius_of_gyration": radius_of_gyration_value, "slenderness_ratio": slenderness,
        "fcr": fcr, "equation": "9-25", "printed_page": "9-13", "pdf_page": 244,
    }


def radius_of_gyration(shape, moment_of_inertia=None, area=None, b=None, d=None):
    """Eq 9-26: radius of gyration r (printed p. 9-13).

        r = sqrt(I/A)                    general
        r = b/sqrt(12)                   rectangular, b = least dimension
        r = d/4                          circular, d = diameter

    Parameters
    ----------
    shape : str
        'general' (requires moment_of_inertia and area), 'rectangular'
        (requires b), or 'circular' (requires d).
    moment_of_inertia : float, optional
        I (shape='general').
    area : float, optional
        A (shape='general').
    b : float, optional
        Least cross-section dimension (shape='rectangular').
    d : float, optional
        Diameter (shape='circular').

    Returns
    -------
    dict
        {'shape', 'r', 'equation': '9-26', ...}
    """
    if shape == "general":
        if moment_of_inertia is None or area is None:
            raise ValueError("moment_of_inertia and area are required for shape='general'")
        r = math.sqrt(moment_of_inertia / area)
    elif shape == "rectangular":
        if b is None:
            raise ValueError("b is required for shape='rectangular'")
        r = b / math.sqrt(12.0)
    elif shape == "circular":
        if d is None:
            raise ValueError("d is required for shape='circular'")
        r = d / 4.0
    else:
        raise ValueError(f"shape must be 'general', 'rectangular', or 'circular', got {shape!r}")
    return {"shape": shape, "r": r, "equation": "9-26", "printed_page": "9-13", "pdf_page": 244}


# ============================================================================
# Eq 9-27, 9-28, 9-29 -- Short columns (printed pp. 9-13 to 9-14, pdf_page 244-245)
# ============================================================================

def ylinen_critical_stress_fourth_power(fc, unbraced_length, radius_of_gyration_value,
                                         modulus_of_elasticity):
    """Eq 9-27: short-column critical buckling stress, the FPL fourth-
    power parabolic function of Newlin and Gahagan (1930) (printed p. 9-13).

        fcr = Fc * [1 - (4/(27*pi^4)) * (L/r * sqrt(Fc/E_L))^4]

    Nonconservative for intermediate L/r columns compared with the Ylinen
    form (Eq 9-29); see ``ylinen_buckling_stress``.

    Parameters
    ----------
    fc : float
        Fc, compressive strength (parallel to grain).
    unbraced_length : float
        L, unbraced length.
    radius_of_gyration_value : float
        r, least radius of gyration.
    modulus_of_elasticity : float
        E_L, elastic modulus parallel to the member axis.

    Returns
    -------
    dict
        {'fcr', 'equation': '9-27', ...}
    """
    ratio = unbraced_length / radius_of_gyration_value * math.sqrt(fc / modulus_of_elasticity)
    fcr = fc * (1.0 - (4.0 / (27.0 * math.pi**4)) * ratio**4)
    return {"fc": fc, "unbraced_length": unbraced_length,
            "radius_of_gyration": radius_of_gyration_value,
            "modulus_of_elasticity": modulus_of_elasticity, "fcr": fcr,
            "equation": "9-27", "printed_page": "9-13", "pdf_page": 244}


def ylinen_strain(fc, stress, modulus_of_elasticity, c):
    """Eq 9-28: Ylinen (1956) nonlinear compressive stress-strain
    relationship used in place of Hooke's law for short-column analysis
    (printed p. 9-14).

        epsilon = (Fc/E_L) * [c*(f/Fc) - (1-c)*ln(1 - f/Fc)]

    Parameters
    ----------
    fc : float
        Fc, compressive strength.
    stress : float
        f, compressive stress (0 <= f < Fc).
    modulus_of_elasticity : float
        E_L.
    c : float
        Empirical constant, 0 < c < 1 (see ``ylinen_buckling_stress`` for
        the printed guidance on c).

    Returns
    -------
    dict
        {'strain', 'equation': '9-28', ...}
    """
    ratio = stress / fc
    strain = (fc / modulus_of_elasticity) * (c * ratio - (1.0 - c) * math.log(1.0 - ratio))
    return {"fc": fc, "stress": stress, "c": c, "strain": strain,
            "equation": "9-28", "printed_page": "9-14", "pdf_page": 245}


def ylinen_buckling_stress(fc, fe, c=0.957):
    """Eq 9-29: Ylinen's short-column buckling equation, using the slope
    of Eq 9-28 in place of E_L in Euler's formula (printed p. 9-14).

        fcr = (Fc+fe)/(2c) - sqrt( ((Fc+fe)/(2c))^2 - Fc*fe/c )

    Printed guidance on c: c=0.957 matches the FPL fourth-power formula
    (Eq 9-27, Fig. 9-18) closely; c=0.8 better fits solid-sawn and glued-
    laminated timber data (nonconservative range of the fourth-power
    form); c=0.9 better fits structural composite lumber.

    Parameters
    ----------
    fc : float
        Fc, compressive strength.
    fe : float
        fe, Euler buckling stress (Eq 9-25).
    c : float, optional
        Empirical constant (default 0.957; see printed guidance above).

    Returns
    -------
    dict
        {'fcr', 'c', 'equation': '9-29', ...}
    """
    term = (fc + fe) / (2.0 * c)
    fcr = term - math.sqrt(term**2 - fc * fe / c)
    return {"fc": fc, "fe": fe, "c": c, "fcr": fcr, "equation": "9-29",
            "printed_page": "9-14", "pdf_page": 245}


def built_up_column_capacity(fc, fe, c, k_f):
    """Eq 9-30: buckling stress capacity of a built-up column of
    mechanically connected members (printed p. 9-14), the Ylinen form
    reduced by a built-up stability factor Kf that accounts for connection
    efficiency.

        fcr = Kf * [(Fc+fe)/(2c) - sqrt(((Fc+fe)/(2c))^2 - Fc*fe/c)]

    Printed Kf values: 0.75 for bolted connections, 0.6 for nailed
    connections (provided fastener spacing meets design-specification
    requirements).

    Parameters
    ----------
    fc : float
        Fc, compressive strength.
    fe : float
        fe, Euler buckling stress (Eq 9-25) of the built-up section.
    c : float
        Ylinen constant (see ``ylinen_buckling_stress``).
    k_f : float
        Built-up stability factor (0.75 bolts, 0.6 nails, per the printed
        guidance).

    Returns
    -------
    dict
        {'fcr', 'k_f', 'equation': '9-30', ...}
    """
    term = (fc + fe) / (2.0 * c)
    fcr = k_f * (term - math.sqrt(term**2 - fc * fe / c))
    return {"fc": fc, "fe": fe, "c": c, "k_f": k_f, "fcr": fcr,
            "equation": "9-30", "printed_page": "9-14", "pdf_page": 245}


def flange_instability_stress(modulus_of_elasticity, flange_thickness, flange_width):
    """Eq 9-31: elastic instability stress of a thin outstanding flange
    (I, H, +, or L cross sections) (printed p. 9-14, Trayer and March
    1931). If joints between column members are glued and reinforced with
    glued fillets, the instability stress increases to as much as 1.6x
    this value.

        fcr = 0.044 * E * t^2 / b^2

    Parameters
    ----------
    modulus_of_elasticity : float
        E, column modulus of elasticity.
    flange_thickness : float
        t, thickness of the outstanding flange.
    flange_width : float
        b, width of the outstanding flange.

    Returns
    -------
    dict
        {'fcr', 'equation': '9-31', ...}
    """
    fcr = 0.044 * modulus_of_elasticity * flange_thickness**2 / flange_width**2
    return {"modulus_of_elasticity": modulus_of_elasticity,
            "flange_thickness": flange_thickness, "flange_width": flange_width,
            "fcr": fcr, "equation": "9-31", "printed_page": "9-14", "pdf_page": 245}


# ============================================================================
# Eq 9-32 -- Water ponding critical spacing (printed p. 9-15, pdf_page 246)
# ============================================================================

RHO_WATER_KG_M3 = 1000.0


def critical_ponding_spacing(modulus_of_elasticity, moment_of_inertia, length,
                              end_condition="simple", rho_water=RHO_WATER_KG_M3):
    """Eq 9-32: critical beam spacing to prevent progressive deflection
    (ponding failure) under roof water accumulation (printed p. 9-15,
    Zahn 1988). To prevent ponding, actual beam spacing must be less than
    s_cr.

        s_cr = m * pi^4 * E * I / (rho * L^4)

    Parameters
    ----------
    modulus_of_elasticity : float
        E, beam modulus of elasticity.
    moment_of_inertia : float
        I, beam moment of inertia.
    length : float
        L, beam length.
    end_condition : str, optional
        'simple' (default, m=1) or 'fixed' (m=16/3).
    rho_water : float, optional
        Density of water (kg/m^3, default 1000; printed alternative 0.0361
        lb/in^3 for inch-pound units -- pass explicitly if using those).

    Returns
    -------
    dict
        {'s_cr', 'm', 'equation': '9-32', ...}
    """
    if end_condition == "simple":
        m = 1.0
    elif end_condition == "fixed":
        m = 16.0 / 3.0
    else:
        raise ValueError(f"end_condition must be 'simple' or 'fixed', got {end_condition!r}")
    s_cr = m * math.pi**4 * modulus_of_elasticity * moment_of_inertia / (rho_water * length**4)
    return {"modulus_of_elasticity": modulus_of_elasticity, "moment_of_inertia": moment_of_inertia,
            "length": length, "end_condition": end_condition, "m": m, "s_cr": s_cr,
            "equation": "9-32", "printed_page": "9-15", "pdf_page": 246}


# ============================================================================
# Eq 9-33, 9-34, Table 9-2 -- Lateral-torsional buckling, long beams
# (printed pp. 9-15 to 9-16, pdf_page 246-247)
# ============================================================================

def lateral_torsional_buckling_stress(modulus_of_elasticity, alpha):
    """Eq 9-33: critical bending stress at which a long, slender beam
    (restrained against torsional/axial rotation at supports, otherwise
    free to twist and deflect laterally) buckles (printed p. 9-15). Valid
    for bending stresses below the proportional limit.

        fb_cr = pi^2 * E_L / alpha^2

    For short beams, use the column-buckling criterion (``ylinen_
    buckling_stress`` / Fig. 9-18 relations) with alpha in place of L/r
    and fb_cr/Fb in place of fcr/Fc (per the printed guidance).

    Parameters
    ----------
    modulus_of_elasticity : float
        E_L, elastic modulus parallel to the member axis.
    alpha : float
        Slenderness factor (Eq 9-34, ``slenderness_factor``).

    Returns
    -------
    dict
        {'fb_cr', 'equation': '9-33', ...}
    """
    fb_cr = math.pi**2 * modulus_of_elasticity / alpha**2
    return {"modulus_of_elasticity": modulus_of_elasticity, "alpha": alpha,
            "fb_cr": fb_cr, "equation": "9-33", "printed_page": "9-15", "pdf_page": 246}


# Table 9-2: effective length Le for checking lateral-torsional stability
# of beams (printed p. 9-16). Conservative for width-to-depth ratios < 0.4;
# load assumed to act at the top edge of the beam.
TABLE_9_2_EFFECTIVE_LENGTH = {
    ("simple_support", "equal_end_moments"): lambda L, h: L,
    ("simple_support", "concentrated_center"): lambda L, h: 0.742 * L / (1.0 - 2.0 * h / L),
    ("simple_support", "uniformly_distributed"): lambda L, h: 0.887 * L / (1.0 - 2.0 * h / L),
    ("cantilever", "concentrated_end"): lambda L, h: 0.783 * L / (1.0 - 2.0 * h / L),
    ("cantilever", "uniformly_distributed"): lambda L, h: 0.489 * L / (1.0 - 2.0 * h / L),
}


def table_9_2_effective_length(support, load, length, depth):
    """Table 9-2: effective length Le for checking lateral-torsional
    stability of beams, by support condition and load case (printed
    p. 9-16). Conservative for beam width/depth ratio < 0.4.

    Parameters
    ----------
    support : str
        'simple_support' or 'cantilever'.
    load : str
        'equal_end_moments' (simple support only), 'concentrated_center'
        (simple support) / 'concentrated_end' (cantilever), or
        'uniformly_distributed' (either support).
    length : float
        L, beam span (simple support) or cantilever length.
    depth : float
        h, beam depth.

    Returns
    -------
    dict
        {'support', 'load', 'le', 'table': '9-2', ...}
    """
    key = (support, load)
    if key not in TABLE_9_2_EFFECTIVE_LENGTH:
        raise ValueError(f"(support, load) must be one of {sorted(TABLE_9_2_EFFECTIVE_LENGTH)}, got {key!r}")
    le = TABLE_9_2_EFFECTIVE_LENGTH[key](length, depth)
    return {"support": support, "load": load, "length": length, "depth": depth,
            "le": le, "table": "9-2", "printed_page": "9-16", "pdf_page": 247}


def slenderness_factor(ei_y, gj, le, h, b):
    """Eq 9-34: slenderness factor alpha for lateral-torsional buckling of
    a rectangular beam (printed p. 9-16).

        alpha = sqrt(2*pi) * (EIy/GJ)^(1/4) * sqrt(Le*h) / b

    with EIy = E_L*h*b^3/12 (lateral flexural rigidity) and GJ the
    torsional rigidity (Eq 9-9/9-11).

    Parameters
    ----------
    ei_y : float
        Lateral flexural rigidity E_L*h*b^3/12.
    gj : float
        Torsional rigidity (G times the torsional constant K, Eq 9-9/9-11).
    le : float
        Le, effective length (Table 9-2).
    h : float
        Beam depth.
    b : float
        Beam width.

    Returns
    -------
    dict
        {'alpha', 'equation': '9-34', ...}
    """
    alpha = math.sqrt(2.0 * math.pi) * (ei_y / gj) ** 0.25 * math.sqrt(le * h) / b
    return {"ei_y": ei_y, "gj": gj, "le": le, "h": h, "b": b, "alpha": alpha,
            "equation": "9-34", "printed_page": "9-16", "pdf_page": 247}


# ============================================================================
# Eq 9-35 -- Effect of deck support (printed p. 9-16, pdf_page 247)
# ============================================================================

def deck_shear_stiffness_parameter(beam_spacing, deck_shear_rigidity, length, ei_y):
    """Eq 9-35: deck shear stiffness parameter tau (Zahn 1973), the
    abscissa of Figure 9-23 (increase in lateral-torsional buckling
    stress from an attached deck, simply supported beams only) (printed
    p. 9-16).

        tau = s * G_D * L^2 / EIy

    Figure 9-23 (theta vs tau, three loading cases: end moments, uniform
    load, concentrated load) is NOT digitized here -- it is a chart
    without a printed closed form; per the text, apply it by dividing the
    effective length (Table 9-2) by theta before use in Eq 9-33/9-34.

    Parameters
    ----------
    beam_spacing : float
        s, beam spacing.
    deck_shear_rigidity : float
        G_D, in-plane shear rigidity of the deck (shear force per unit
        length of edge / shear strain).
    length : float
        L, actual beam length.
    ei_y : float
        Lateral flexural rigidity (as in Eq 9-34).

    Returns
    -------
    dict
        {'tau', 'equation': '9-35', ...}
    """
    tau = beam_spacing * deck_shear_rigidity * length**2 / ei_y
    return {"beam_spacing": beam_spacing, "deck_shear_rigidity": deck_shear_rigidity,
            "length": length, "ei_y": ei_y, "tau": tau, "equation": "9-35",
            "printed_page": "9-16", "pdf_page": 247}


# ============================================================================
# Eq 9-36 to 9-41 -- Interaction of buckling modes (printed p. 9-17, pdf_page 248)
# ============================================================================

def elastic_buckling_stress_edgewise_flatwise(modulus_of_elasticity, le, d):
    """Eq 9-39/9-40: elastic (Euler-form) buckling stress for edgewise
    (subscript 1) or flatwise (subscript 2) bending/compression, used in
    the biaxial beam-column interaction check (printed p. 9-17).

        F1_or_2'' = 0.822*E / (le/d)^2

    Parameters
    ----------
    modulus_of_elasticity : float
        E.
    le : float
        le1 or le2, effective length for the axis of interest.
    d : float
        d1 or d2, member depth for that axis.

    Returns
    -------
    dict
        {'f_double_prime', 'equation': '9-39 or 9-40', ...}
    """
    f_dprime = 0.822 * modulus_of_elasticity / (le / d) ** 2
    return {"modulus_of_elasticity": modulus_of_elasticity, "le": le, "d": d,
            "f_double_prime": f_dprime, "equation": "9-39/9-40",
            "printed_page": "9-17", "pdf_page": 248}


def elastic_buckling_stress_edgewise_bending(modulus_of_elasticity, le, d1, d2):
    """Eq 9-41: elastic lateral (edgewise) bending buckling stress used in
    the flatwise moment-magnification factor theta_c2 (printed p. 9-17).

        Fb1'' = 1.44*E/le * d2/d1

    Parameters
    ----------
    modulus_of_elasticity : float
        E.
    le : float
        Effective length of the member.
    d1 : float
        Member depth for edgewise bending.
    d2 : float
        Member depth for flatwise bending.

    Returns
    -------
    dict
        {'fb1_double_prime', 'equation': '9-41', ...}
    """
    fb1_dprime = 1.44 * modulus_of_elasticity / le * d2 / d1
    return {"modulus_of_elasticity": modulus_of_elasticity, "le": le, "d1": d1, "d2": d2,
            "fb1_double_prime": fb1_dprime, "equation": "9-41",
            "printed_page": "9-17", "pdf_page": 248}


def moment_magnification_edgewise(fc, fc1_double_prime, beam_spacing, s_cr):
    """Eq 9-37: moment magnification factor theta_c1 for edgewise bending
    (printed p. 9-17).

        theta_c1 = 1 - (fc/Fc1'' + s/s_cr)

    Parameters
    ----------
    fc : float
        Member compressive stress.
    fc1_double_prime : float
        Fc1'', elastic buckling stress for edgewise compression (Eq 9-39).
    beam_spacing : float
        s, beam spacing.
    s_cr : float
        s_cr, critical ponding spacing (Eq 9-32).

    Returns
    -------
    dict
        {'theta_c1', 'equation': '9-37', ...}
    """
    theta = 1.0 - (fc / fc1_double_prime + beam_spacing / s_cr)
    return {"fc": fc, "fc1_double_prime": fc1_double_prime, "beam_spacing": beam_spacing,
            "s_cr": s_cr, "theta_c1": theta, "equation": "9-37",
            "printed_page": "9-17", "pdf_page": 248}


def moment_magnification_flatwise(fc, fc2_double_prime, fb1, e1_over_d1, fb1_double_prime):
    """Eq 9-38: moment magnification factor theta_c2 for flatwise bending
    (printed p. 9-17).

        theta_c2 = 1 - [fc/Fc2'' + (fb1 + 6*(e1/d1)*fc)/Fb1'']

    Parameters
    ----------
    fc : float
        Member compressive stress.
    fc2_double_prime : float
        Fc2'', elastic buckling stress for flatwise compression (Eq 9-40).
    fb1 : float
        Edgewise bending stress.
    e1_over_d1 : float
        e1/d1, ratio of eccentricity of axial compression to member depth
        for edgewise bending.
    fb1_double_prime : float
        Fb1'', elastic lateral (edgewise) bending buckling stress (Eq 9-41).

    Returns
    -------
    dict
        {'theta_c2', 'equation': '9-38', ...}
    """
    theta = 1.0 - (fc / fc2_double_prime + (fb1 + 6.0 * e1_over_d1 * fc) / fb1_double_prime)
    return {"fc": fc, "fc2_double_prime": fc2_double_prime, "fb1": fb1,
            "e1_over_d1": e1_over_d1, "fb1_double_prime": fb1_double_prime,
            "theta_c2": theta, "equation": "9-38", "printed_page": "9-17", "pdf_page": 248}


def biaxial_beam_column_interaction(fc, fc_prime, fb1, e1_over_d1, theta_c1, fb1_prime,
                                     fb2, e2_over_d2, theta_c2, fb2_allow):
    """Eq 9-36: interaction check for a member under combined axial
    compression, primary (edgewise) bending moment, and lateral (flatwise)
    bending moment (printed p. 9-17, Zahn 1986).

        (fc/Fc')^2
        + [fb1 + 6*(e1/d1)*fc*(1.234-0.234*theta_c1)] / (theta_c1*Fb1')
        + [fb2 + 6*(e2/d2)*fc*(1.234-0.234*theta_c2)] / (theta_c2*Fb2)
        <= 1.0

    Parameters
    ----------
    fc : float
        Member stress in axial compression.
    fc_prime : float
        Fc', compressive strength reduced for member slenderness (Ylinen,
        ``ylinen_buckling_stress`` applied to the governing axis).
    fb1 : float
        Edgewise bending stress.
    e1_over_d1 : float
        e1/d1, eccentricity ratio for edgewise bending.
    theta_c1 : float
        Moment magnification factor, edgewise (Eq 9-37).
    fb1_prime : float
        Fb1', edgewise bending strength reduced for slenderness.
    fb2 : float
        Flatwise bending stress.
    e2_over_d2 : float
        e2/d2, eccentricity ratio for flatwise bending.
    theta_c2 : float
        Moment magnification factor, flatwise (Eq 9-38).
    fb2_allow : float
        Fb2, flatwise bending strength (design/allowable value).

    Returns
    -------
    dict
        {'interaction_value' (<=1.0 is OK), 'equation': '9-36', ...}
    """
    term_c = (fc / fc_prime) ** 2
    term_1 = (fb1 + 6.0 * e1_over_d1 * fc * (1.234 - 0.234 * theta_c1)) / (theta_c1 * fb1_prime)
    term_2 = (fb2 + 6.0 * e2_over_d2 * fc * (1.234 - 0.234 * theta_c2)) / (theta_c2 * fb2_allow)
    value = term_c + term_1 + term_2
    return {
        "fc": fc, "fb1": fb1, "fb2": fb2, "term_axial": term_c,
        "term_edgewise": term_1, "term_flatwise": term_2,
        "interaction_value": value, "adequate": value <= 1.0,
        "equation": "9-36", "printed_page": "9-17", "pdf_page": 248,
    }
