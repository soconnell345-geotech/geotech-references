"""Eurocode 7 (EN 1997-1:2004) equation functions.

Digitized closed-form equations from:
  - Annex D (informative), "A sample analytical method for bearing resistance
    calculation" [pdf_page_index 158-160] -- undrained (D.3) and drained
    (D.4) bearing resistance, fully implemented.
  - Annex E (informative), "A sample semi-empirical method for bearing
    resistance estimation" [pdf_page_index 161] -- pressuremeter method,
    fully implemented.
  - Annex F.2 (informative), "Adjusted elasticity method" for settlement
    [pdf_page_index 162] -- fully implemented.
  - Annex C (informative), "Sample procedures to determine earth pressures"
    [pdf_page_index 142-158] -- PARTIALLY implemented; see the module-level
    note below.

Annex C completeness note
--------------------------
Annex C.1 (basic active/passive pressure formulas, Eq. C.1/C.2, plus the
Kac cohesion-coefficient formula) and Eq. C.4 (the wall boundary condition
for the angle mw) and Eq. C.9 (the approximate weight-density coefficient
Kgamma, given Kn) are clearly legible in the source PDF and are implemented
below.

Eq. C.3 (soil-surface boundary condition for angle mt), Eq. C.5 (tangent
rotation v), Eq. C.7 (surcharge coefficient Kq), and Eq. C.8 (cohesion
coefficient Kc) render as BLANK content in the source PDF's extracted text
layer between their descriptive sentence and their equation label -- i.e.
they were embedded as images in the original scan and were not captured by
OCR at all (not merely garbled). Per the "flag, don't guess" rule these are
NOT implemented here; a caller needing the full log-spiral analytical
procedure (or Kn itself, Eq. C.6, whose surviving OCR fragments were
ambiguous enough that reconstructing it here would also amount to guessing)
should consult EN 1997-1:2004 Annex C.2 directly or use the design charts
(Figures C.1.1-C.1.4 for Ka, C.2.1-C.2.4 for Kp; see figures_catalog.json).
"""

import math


# ============================================================================
# Annex C.1 (pdf idx 142-143): Limit values of earth pressure on a vertical
# wall (Eq. C.1, C.2), and the cohesion earth-pressure coefficient formula
# given for Kac (Eq. C.1's note).
# ============================================================================

def active_earth_pressure(K_a: float, gamma: float, depth: float,
                          q: float = 0.0, u: float = 0.0, c: float = 0.0,
                          K_ac: float = 0.0) -> float:
    """Total active earth pressure normal to a wall at depth z (Eq. C.1).

    sigma_a(z) = Ka * [integral(gamma dz) + q] + u - c * Kac

    For a homogeneous layer the integral of weight density from the ground
    surface to depth reduces to ``gamma * depth``.

    Parameters
    ----------
    K_a : float
        Coefficient of effective horizontal active earth pressure (from
        Figures C.1.1-C.1.4, or an external analytical/numerical method).
    gamma : float
        Total weight density of the retained ground [kN/m3].
    depth : float
        Depth z down the face of the wall from the ground surface [m].
    q : float
        Uniform vertical surface load [kPa].  Default 0.
    u : float
        Pore water pressure at depth z [kPa].  Default 0.
    c : float
        Cohesion (c' for drained soil, cu for undrained soil) [kPa].
        Default 0.
    K_ac : float
        Cohesion earth-pressure coefficient (see
        ``cohesion_earth_pressure_coefficient``).  Default 0 (no cohesion
        relief).

    Returns
    -------
    float
        Total stress normal to the wall at depth z, sigma_a(z) [kPa].
    """
    return K_a * (gamma * depth + q) + u - c * K_ac


def passive_earth_pressure(K_p: float, gamma: float, depth: float,
                           q: float = 0.0, u: float = 0.0, c: float = 0.0,
                           K_pc: float = 0.0) -> float:
    """Total passive earth pressure normal to a wall at depth z (Eq. C.2).

    sigma_p(z) = Kp * [integral(gamma dz) + q] + u + c * Kpc

    Parameters
    ----------
    K_p : float
        Coefficient of effective horizontal passive earth pressure (from
        Figures C.2.1-C.2.4, or an external analytical/numerical method).
    gamma, depth, q, u, c : float
        As in ``active_earth_pressure``.
    K_pc : float
        Cohesion earth-pressure coefficient (see
        ``cohesion_earth_pressure_coefficient``).  Default 0.

    Returns
    -------
    float
        Total stress normal to the wall at depth z, sigma_p(z) [kPa].
    """
    return K_p * (gamma * depth + q) + u + c * K_pc


def cohesion_earth_pressure_coefficient(K: float, adhesion: float,
                                        cohesion: float) -> float:
    """Cohesion earth-pressure coefficient Kac (Eq. C.1 note, pdf idx 142).

    Kac = 2 * sqrt(K * (1 + a/c)), limited to 2.56 * sqrt(K)

    The source explicitly gives this form for the active coefficient Kac
    (used with Ka in Eq. C.1).  EN 1997-1 does not restate a separate
    formula for the passive Kpc (used with Kp in Eq. C.2) in the visible
    text; by analogy with the standard Coulomb/Caquot-Kerisel treatment of
    cohesion this same functional form is commonly applied for Kpc as well
    (with K = Kp), but that extension is NOT explicitly stated in the
    source PDF -- treat a Kpc result from this function as inferred by
    analogy, not as a directly cited EN 1997-1 value.

    Parameters
    ----------
    K : float
        The corresponding earth-pressure coefficient (Ka for Kac, or Kp by
        analogy for Kpc).
    adhesion : float
        Adhesion between ground and wall, a [kPa].
    cohesion : float
        Cohesion, c (c' or cu) [kPa].  Must be > 0.

    Returns
    -------
    float
        Kac (or, by analogy, Kpc).

    Raises
    ------
    ValueError
        If cohesion <= 0 or K < 0.
    """
    if cohesion <= 0:
        raise ValueError(f"cohesion must be > 0, got {cohesion}")
    if K < 0:
        raise ValueError(f"K must be >= 0, got {K}")
    value = 2.0 * math.sqrt(K * (1.0 + adhesion / cohesion))
    cap = 2.56 * math.sqrt(K)
    return min(value, cap)


# ============================================================================
# Annex C.2 (pdf idx 151-153): Analytical procedure, legible portion only.
# Eq. C.4 (angle mw) and Eq. C.9 (Kgamma, given Kn) -- see module docstring
# for what is NOT implemented (Eq. C.3, C.5, C.6, C.7, C.8).
# ============================================================================

def mobilised_wall_angle_mw(phi_deg: float, delta_deg: float) -> float:
    """Angle mw from the wall boundary condition (Eq. C.4, pdf idx 152).

    cos(2*mw + phi + delta) = sin(delta) / sin(phi)

    mw is negative for passive pressures (phi > 0) if sin(delta)/sin(phi) is
    sufficiently large (per the source note).  For active pressure
    calculations, per Annex C.2(3), phi and delta should be passed in as
    NEGATIVE values (the sign convention used throughout Annex C.2).

    Parameters
    ----------
    phi_deg : float
        Angle of shearing resistance [degrees]; negative for active-pressure
        calculations per Annex C.2(3).
    delta_deg : float
        Angle of wall friction [degrees]; negative for active-pressure
        calculations per Annex C.2(3).

    Returns
    -------
    float
        mw [degrees].

    Raises
    ------
    ValueError
        If phi_deg is 0 (undefined) or |sin(delta)/sin(phi)| > 1 (no real
        solution).
    """
    if phi_deg == 0:
        raise ValueError("phi_deg must be nonzero (Eq. C.4 is undefined at phi=0; "
                         "see the phi=0 special-case relations, Eq. C.10, "
                         "which this module does not implement -- see docstring).")
    phi = math.radians(phi_deg)
    delta = math.radians(delta_deg)
    ratio = math.sin(delta) / math.sin(phi)
    if abs(ratio) > 1.0:
        raise ValueError(
            f"No real solution: sin(delta)/sin(phi) = {ratio:.4f} exceeds 1 in "
            f"magnitude for phi={phi_deg} deg, delta={delta_deg} deg."
        )
    mw = (math.acos(ratio) - phi - delta) / 2.0
    return math.degrees(mw)


def weight_density_coefficient(K_n: float, beta_deg: float,
                               theta_deg: float = 0.0) -> float:
    """Approximate weight-density earth-pressure coefficient Kgamma (Eq. C.9, pdf idx 153).

    Kgamma = Kn * cos(beta) * cos(beta - theta)

    Per the source: "This expression is on the safe side. While the error
    is unimportant for active pressures it may be considerable for passive
    pressures with positive values of beta."

    Parameters
    ----------
    K_n : float
        Coefficient for normal loading on the surface (Eq. C.6 -- must be
        supplied by the caller; not computed by this module, see the
        module docstring).
    beta_deg : float
        Slope angle of the ground behind the wall, positive rising away
        from the wall [degrees].
    theta_deg : float
        Angle between the vertical and the wall direction, positive when
        the soil overhangs the wall [degrees].  Default 0 (vertical wall).

    Returns
    -------
    float
        Kgamma.
    """
    beta = math.radians(beta_deg)
    theta = math.radians(theta_deg)
    return K_n * math.cos(beta) * math.cos(beta - theta)


# ============================================================================
# Annex D.3 (pdf idx 159): Undrained bearing resistance.
# ============================================================================

def undrained_bearing_resistance(cu: float, q: float, B: float,
                                 L: float = None, shape: str = "rectangular",
                                 alpha_deg: float = 0.0, H: float = 0.0,
                                 A_prime: float = None) -> dict:
    """Design bearing resistance in undrained conditions (Eq. D.1, Annex D.3).

    R/A' = (pi + 2) * cu * bc * sc * ic + q

    Parameters
    ----------
    cu : float
        Design undrained shear strength [kPa].
    q : float
        Design effective overburden pressure at the foundation base level
        [kPa].
    B : float
        Effective foundation width B' [m].
    L : float, optional
        Effective foundation length L' [m].  Omit (or set equal to B) for a
        square or circular base (uses the sc=1.2 special case).
    shape : str
        'rectangular' or 'square_circular'.  If L is omitted, defaults to
        'square_circular'.
    alpha_deg : float
        Inclination of the foundation base to the horizontal, alpha
        [degrees].  Default 0 (horizontal base).
    H : float
        Design horizontal load [kN].  Must satisfy H <= A'*cu.  Default 0.
    A_prime : float, optional
        Design effective foundation area A' = B'*L' [m2].  If omitted,
        computed as B*L (or B*B for square/circular).

    Returns
    -------
    dict
        Keys: bearing_pressure_kpa (R/A'), bc, sc, ic, Nc (= pi + 2).

    Raises
    ------
    ValueError
        If H > A'*cu (inclination factor undefined).
    """
    shp = shape.strip().lower()
    if L is None:
        L = B
        shp = "square_circular"
    A = A_prime if A_prime is not None else B * L

    alpha = math.radians(alpha_deg)
    b_c = 1.0 - 2.0 * alpha / (math.pi + 2.0)

    if shp in ("square_circular", "square", "circular", "circle"):
        s_c = 1.2
    else:
        s_c = 1.0 + 0.2 * (B / L)

    max_H = A * cu
    if H > max_H + 1e-9:
        raise ValueError(
            f"H={H} exceeds A'*cu={max_H:.3f}; inclination factor ic is undefined."
        )
    i_c = 0.5 * (1.0 + math.sqrt(max(1.0 - H / max_H, 0.0))) if max_H > 0 else 1.0

    Nc = math.pi + 2.0
    bearing_pressure = Nc * cu * b_c * s_c * i_c + q

    return {
        "bearing_pressure_kpa": bearing_pressure,
        "bc": b_c,
        "sc": s_c,
        "ic": i_c,
        "Nc": Nc,
    }


# ============================================================================
# Annex D.4 (pdf idx 159-160): Drained bearing resistance.
# ============================================================================

def bearing_capacity_factors(phi_deg: float) -> dict:
    """Drained bearing capacity factors Nq, Nc, Ngamma (Eq. D.2, Annex D.4).

    Nq = e^(pi*tan(phi')) * tan^2(45 + phi'/2)
    Nc = (Nq - 1) * cot(phi')
    Ngamma = 2 * (Nq - 1) * tan(phi')   [rough base, delta >= phi'/2]

    Parameters
    ----------
    phi_deg : float
        Design effective angle of shearing resistance, phi' [degrees].
        Must be > 0.

    Returns
    -------
    dict
        Keys: Nq, Nc, Ngamma.

    Raises
    ------
    ValueError
        If phi_deg <= 0.
    """
    if phi_deg <= 0:
        raise ValueError(f"phi_deg must be > 0, got {phi_deg}")
    phi = math.radians(phi_deg)
    Nq = math.exp(math.pi * math.tan(phi)) * math.tan(math.radians(45) + phi / 2) ** 2
    Nc = (Nq - 1.0) / math.tan(phi)
    Ngamma = 2.0 * (Nq - 1.0) * math.tan(phi)
    return {"Nq": Nq, "Nc": Nc, "Ngamma": Ngamma}


def drained_bearing_resistance(phi_deg: float, c: float, q: float,
                               gamma: float, B: float, L: float = None,
                               shape: str = "rectangular",
                               alpha_deg: float = 0.0, H: float = 0.0,
                               V: float = None, load_direction: str = "B",
                               A_prime: float = None) -> dict:
    """Design bearing resistance in drained conditions (Eq. D.2, Annex D.4).

    R/A' = c'*Nc*bc*sc*ic + q'*Nq*bq*sq*iq + 0.5*gamma'*B'*Ngamma*bgamma*sgamma*igamma

    Parameters
    ----------
    phi_deg : float
        Design effective angle of shearing resistance, phi' [degrees].
    c : float
        Design effective cohesion, c' [kPa].
    q : float
        Design effective overburden pressure at the foundation base level
        [kPa].
    gamma : float
        Design effective weight density of the soil below the foundation
        [kN/m3].
    B : float
        Effective foundation width B' [m].
    L : float, optional
        Effective foundation length L' [m].  Omit for a square/circular
        base.
    shape : str
        'rectangular' or 'square_circular'.  If L is omitted, defaults to
        'square_circular'.
    alpha_deg : float
        Inclination of the foundation base to the horizontal [degrees].
        Default 0.
    H : float
        Design horizontal load [kN], acting in the direction given by
        ``load_direction``.  Default 0 (no inclination factors reduction,
        i=1).
    V : float, optional
        Design vertical load [kN].  Required if H != 0.
    load_direction : str
        'B' (H acts in the direction of B') or 'L' (H acts in the direction
        of L').  Selects m = mB or m = mL.  Default 'B'.
    A_prime : float, optional
        Design effective foundation area A' = B'*L' [m2].  If omitted,
        computed as B*L (or B*B for square/circular).

    Returns
    -------
    dict
        Keys: bearing_pressure_kpa (R/A'), Nq, Nc, Ngamma, bq, bc, bgamma,
        sq, sc, sgamma, iq, ic, igamma, m.

    Raises
    ------
    ValueError
        If phi_deg <= 0, or H != 0 without V, or inclination factor base
        (V + A'*c'*cot(phi')) <= 0.
    """
    shp = shape.strip().lower()
    if L is None:
        L = B
        shp = "square_circular"
    is_rect = shp not in ("square_circular", "square", "circular", "circle")
    A = A_prime if A_prime is not None else B * L

    factors = bearing_capacity_factors(phi_deg)
    Nq, Nc, Ngamma = factors["Nq"], factors["Nc"], factors["Ngamma"]
    phi = math.radians(phi_deg)
    alpha = math.radians(alpha_deg)

    # Base inclination factors
    b_q = b_gamma = (1.0 - alpha * math.tan(phi)) ** 2
    b_c = b_q - (1.0 - b_q) / (Nc * math.tan(phi))

    # Shape factors
    if is_rect:
        s_q = 1.0 + (B / L) * math.sin(phi)
        s_gamma = 1.0 - 0.3 * (B / L)
    else:
        s_q = 1.0 + math.sin(phi)
        s_gamma = 0.7
    s_c = (s_q * Nq - 1.0) / (Nq - 1.0)

    # Load inclination factors
    if H == 0.0:
        i_q = i_c = i_gamma = 1.0
        m = None
    else:
        if V is None:
            raise ValueError("V (design vertical load) is required when H != 0.")
        base = V + A * c / math.tan(phi) if phi != 0 else None
        if base is None or base <= 0:
            raise ValueError(
                "V + A'*c'*cot(phi') must be > 0 to evaluate load inclination factors."
            )
        ld = load_direction.strip().upper()
        if ld == "B":
            m = (2.0 + B / L) / (1.0 + B / L)
        elif ld == "L":
            m = (2.0 + L / B) / (1.0 + L / B)
        else:
            raise ValueError(f"Unknown load_direction '{load_direction}'. Use 'B' or 'L'.")
        ratio = max(1.0 - H / base, 0.0)
        i_q = ratio ** m
        i_gamma = ratio ** (m + 1.0)
        i_c = i_q - (1.0 - i_q) / (Nc * math.tan(phi))

    bearing_pressure = (
        c * Nc * b_c * s_c * i_c
        + q * Nq * b_q * s_q * i_q
        + 0.5 * gamma * B * Ngamma * b_gamma * s_gamma * i_gamma
    )

    return {
        "bearing_pressure_kpa": bearing_pressure,
        "Nq": Nq, "Nc": Nc, "Ngamma": Ngamma,
        "bq": b_q, "bc": b_c, "bgamma": b_gamma,
        "sq": s_q, "sc": s_c, "sgamma": s_gamma,
        "iq": i_q, "ic": i_c, "igamma": i_gamma,
        "m": m,
    }


# ============================================================================
# Annex E (pdf idx 161): Semi-empirical pressuremeter bearing resistance.
# ============================================================================

def pressuremeter_bearing_resistance(sigma_v0: float, k: float,
                                     p_le_star: float) -> float:
    """Design bearing resistance from pressuremeter test results (Annex E).

    Rd/A' = sigma_v0 + k * p*le

    Parameters
    ----------
    sigma_v0 : float
        Initial total vertical stress at the foundation base level [kPa].
    k : float
        Bearing resistance factor, typically in the range 0.8 to 3.0
        depending on soil type, embedment depth, and foundation shape
        (Annex E(3)).
    p_le_star : float
        Design net equivalent limit pressure from the pressuremeter test
        [kPa].

    Returns
    -------
    float
        Design bearing resistance pressure, Rd/A' [kPa].
    """
    return sigma_v0 + k * p_le_star


# ============================================================================
# Annex F.2 (pdf idx 162): Adjusted elasticity settlement method.
# ============================================================================

def adjusted_elasticity_settlement(p: float, B: float, f: float,
                                   E_m: float) -> float:
    """Foundation settlement by the adjusted elasticity method (Eq. F.1, Annex F.2).

    s = p * B * f / Em

    Only valid where stresses in the ground are such that no significant
    yielding occurs and the stress-strain behaviour may be considered
    linear (Annex F.2(4)).

    Parameters
    ----------
    p : float
        Bearing pressure, linearly distributed on the foundation base
        [kPa].
    B : float
        Foundation width [m].
    f : float
        Settlement coefficient, depending on foundation shape/dimensions,
        stiffness variation with depth, compressible-layer thickness,
        Poisson's ratio, bearing pressure distribution, and the point at
        which settlement is calculated (Annex F.2(2)).
    E_m : float
        Design value of the modulus of elasticity (drained or undrained, as
        applicable) [kPa].  Must be > 0.

    Returns
    -------
    float
        Settlement s [m] (consistent with the input length unit for B).

    Raises
    ------
    ValueError
        If E_m <= 0.
    """
    if E_m <= 0:
        raise ValueError(f"E_m must be > 0, got {E_m}")
    return p * B * f / E_m
