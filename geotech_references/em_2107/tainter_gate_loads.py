"""EM 1110-2-2107 Chapter 10 (Spillway Tainter Gates) + Appendix F (Tainter
Gate Load Determination).

This is where the manual's closed-form, generalizable design equations
live: side-seal friction (Eq 10.1, derived in Appendix F.1), the three wire-
rope-geometry load cases (Appendix F.2), hydrostatic load on a curved skin
plate by direct integration (Appendix F.3) and by simple projection
(Eq F.16), trunnion-pin friction resolution (Appendix F.4), the full set of
spillway-Tainter-gate strength load combinations (Eq 10.2-10.14), the
trunnion-girder anchorage shear-friction check (Eq 10.15), and Chapter 10's
printed nominal loads/serviceability limits. Printed pages per the
1 August 2022 edition (pdf_page = printed_page + 8).

Two source-document sign/ordering issues were resolved by verifying against
Appendix F's own worked example (Tables F.1-F.7, printed pp. 437-445) rather
than transcribing a form that fails to reproduce the printed numbers --
doctrine: never guess, verify against the manual's own numbers:

  - Eq F.10 (Ph, horizontal hydrostatic component): the printed OCR text
    reads "Ph = R*gamma_w*[Y*(sin th1 - sin th2) - (R/2)*(sin^2 th2 -
    sin^2 th1)]". Direct integration of the stated integral
    INT(th1,th2) (Y + R sin(th)) cos(th) dth gives the opposite sign:
    "Ph = R*gamma_w*[Y*(sin th2 - sin th1) + (R/2)*(sin^2 th2 - sin^2
    th1)]" -- and THIS form reproduces the worked example's Ph = 50.0 kips
    exactly (Table F.3), while the literally-printed form gives -50.0.
    ``hydrostatic_horizontal_component`` implements the calculus-consistent,
    numerically-verified form.
  - Paragraph F.3.5 narrative ("arctangent of the horizontal component over
    the vertical component") implies theta_p = atan(Ph/Pv), but the worked
    example computes theta_p = atan(Pv/Ph) = 0.293 rad (printed p. 440).
    ``resultant_angle_from_horizontal`` implements atan(Pv/Ph), matching
    the worked number.

See ``seismic_amplification.py``'s module docstring for the Table 4.2 /
Eq 4.4-vs-4.6 discrepancies (a different chapter, same doctrine).

SKIPPED (geometry-specific derivations that do not generalize; per review
guidance, listed with page numbers rather than digitized):
  - Wire-rope Case a (rope not tangent to skin plate, printed p. 422): the
    manual gives no closed form -- "force is determined using simple
    statics" from the specific bracket/machinery geometry.
  - The "vertical/horizontal projection" hydrostatic-load method (areas and
    centroids of circular segments of the water column, printed pp. 421,
    429-433, Figures F.14-F.19): a second, more work-intensive alternative
    to the integration method already implemented, needed only when the
    water surface is below the top of the skin plate in specific ways; its
    segment-centroid geometry (Eq for A1/A2/A3, Ls, Mb, Mt) is intricate and
    site-specific, and Table F.7 shows the simplified Eq F.16 projected
    form already agrees with "actual" (integration) to within 0.1% for the
    case where it applies.
  - The "step-wise iteration" hydrostatic-load method (printed pp. 433-434,
    442-443, Tables F.4-F.6): a numerical alternative to the closed-form
    integration already implemented (Table F.7 shows all three methods
    agree to within 1%); a genuine numerical procedure, not a single
    equation, so left as a modeling choice for the caller rather than
    reproduced as a fixed-N Python loop.
  - Eq F.17-F.19 (QT, Rtx, Rty): the trunnion-reaction COMPONENT ASSEMBLY,
    which requires every applied load's own site-specific line of action
    angle (theta_H, theta_Q, theta_Fs, theta_T) and the iterative process
    described in paragraph F.4.1 (steps a-g). ``trunnion_friction_force``
    below implements the GENERALIZABLE remainder (Eq F.17's magnitude/
    direction resolution onward: Rt from components, Ft = mu*Rt, Mt = Ft*r),
    taking the net horizontal/vertical trunnion-reaction components as
    inputs -- validated against the worked example's Rtx=-1336 kips,
    Rty=-363.0 kips -> Rt=1385 kips, Ft=415.3 kips, Mt=207.7 kip-ft
    (printed p. 445).
"""

import math

# ============================================================================
# Eq 10.1 / F.1 -- side-seal friction force (printed pp. 144-145 / 419-420,
# pdf_page 152-153 / 427-428). VALIDATED against Tables F.1/F.2 (printed
# pp. 437-440).
# ============================================================================

def seal_preset_force(delta, e_seal, i_seal, d1):
    """Eq F.1: force per unit length induced by presetting the side seal
    (printed p. 420).

        S = 3 * delta * E * I / d1^3

    I (the seal's moment of inertia, taken over 12 in. of seal length to be
    compatible with the per-unit-length force) is I = t^3 for a rectangular
    seal of thickness t and unit (12 in.) width, per foot of seal length
    (worked example, printed p. 437: t = 1.0 in. -> I = 1 in^4/ft).

    Verified against the Appendix F worked example (printed p. 438):
    delta=0.25 in, E=600 psi, I=1 in^4/ft, d1=4.0 in -> S = 7.03 lb per foot
    of seal length.

    Parameters
    ----------
    delta : float
        Seal preset distance, in.
    e_seal : float
        Modulus of elasticity of the seal material, psi.
    i_seal : float
        Seal moment of inertia per foot of seal length, in^4/ft (= t^3 for
        thickness t, unit foot width).
    d1 : float
        Length (width) of seal exposed to the preset deflection, in.

    Returns
    -------
    dict
        {'s_preset' (lb per ft of seal length), 'equation': 'F.1',
         'printed_page': '420', 'pdf_page': 428}
    """
    s_preset = 3 * delta * e_seal * i_seal / d1 ** 3
    return {"s_preset": s_preset, "equation": "F.1", "printed_page": "420", "pdf_page": 428}


def side_seal_friction_force(mu_s, s_preset, l_total, gamma_w, d2, l1, l2, h):
    """Eq 10.1 (= F.1-F.3 combined): total side-seal friction force on a
    Tainter gate (printed p. 144).

        Fs1 = mu_s * S * l                                (preset component)
        Fs2 = mu_s * gamma_w * (d2/2) * (l1*(h/2) + h*l2) (hydrostatic component)
        Fs  = Fs1 + Fs2

    NOTE: the printed general Eq 10.1 uses one symbol "d" for the seal
    width in BOTH terms, but the Appendix F worked example uses two
    different values -- d1 (seal width exposed to the preset, used in
    ``seal_preset_force``) and d2 (seal width exposed to the hydrostatic
    head, used here). This function takes d2 explicitly and expects
    ``s_preset`` (from ``seal_preset_force``, which used d1) as an input,
    matching the worked example exactly rather than the ambiguous single-d
    printed form.

    Verified against the Appendix F worked example (printed pp. 438-440):
    mu_s=0.5, S=7.03 lb/ft, l_total=42.20 ft -> Fs1=0.15 kips; gamma_w=
    0.0625 kcf, d2=6.0 in (0.5 ft), l1=42.20 ft, l2=0, h=40 ft -> Fs2=6.59
    kips; Fs = 6.74 kips.

    Parameters
    ----------
    mu_s : float
        Coefficient of side-seal friction (nominal value 0.5 per paragraph
        10.2.11 -- see ``nominal_friction_coefficients``).
    s_preset : float
        Preset force per unit length (``seal_preset_force``), lb/ft.
    l_total : float
        Total length of side seal, ft (= l1 + l2).
    gamma_w : float
        Unit weight of water, kcf (0.0625 typical).
    d2 : float
        Width of the J-seal exposed to upper-pool hydrostatic pressure, ft.
    l1 : float
        Length of side seal from headwater to tailwater elevation (or to
        the bottom of the seal if no tailwater), ft.
    l2 : float
        Length of side seal from tailwater elevation to the bottom of the
        seal (0 if no tailwater on the gate), ft.
    h : float
        Vertical distance from headwater surface to tailwater surface (or
        to the bottom of the seal if no tailwater), ft.

    Returns
    -------
    dict
        {'fs1', 'fs2', 'fs_total', 'equation': '10.1', 'printed_page': '144',
         'pdf_page': 152}
    """
    fs1 = mu_s * s_preset * l_total / 1000.0  # lb -> kips
    fs2 = mu_s * gamma_w * (d2 / 2.0) * (l1 * (h / 2.0) + h * l2)
    return {"fs1": fs1, "fs2": fs2, "fs_total": fs1 + fs2,
            "equation": "10.1", "printed_page": "144", "pdf_page": 152}


def nominal_friction_coefficients():
    """Paragraph 10.2.11: nominal coefficients of friction, side seal and
    trunnion (values confirmed via the Appendix E worked example, printed
    p. 414, which cites paragraph 10.2.11 directly).

        side seal (Fs):   mu_s = 0.5
        trunnion (Ft):     mu_t = 0.3

    A load factor of 1.4 is applied to these friction forces (paragraph
    4.3.5).

    Returns
    -------
    dict
        {'side_seal': 0.5, 'trunnion': 0.3, 'load_factor': 1.4,
         'printed_page': '414 (cites 10.2.11)', 'pdf_page': 422}
    """
    return {"side_seal": 0.5, "trunnion": 0.3, "load_factor": 1.4,
            "printed_page": "414 (cites 10.2.11)", "pdf_page": 422}


# ============================================================================
# Appendix F.2 -- wire rope load cases b and c (printed pp. 422-425,
# pdf_page 430-433)
# ============================================================================

def wire_rope_tangent_load(theta_w, t):
    """Eq F.4/F.5b: wire-rope Case b (rope tangent to the skin plate) --
    load per unit length along the skin plate arc, and the total resultant
    force (printed pp. 422-423).

        w = T / R                                                [Eq F.4]
        QT = R * theta_w * w = theta_w * T                       [Eq F.5a/b]

    Verified against the Appendix F worked example (printed p. 444):
    theta_w=0.878 rad, T=78.44 kips -> Q=68.89 kips.

    Parameters
    ----------
    theta_w : float
        Central angle subtended by the wire rope's contact arc with the
        skin plate, rad.
    t : float
        Wire rope tension, kips.

    Returns
    -------
    dict
        {'q_total', 'equation': 'F.4/F.5b', 'printed_page': '422-423',
         'pdf_page': '430-431'}
    """
    q_total = theta_w * t
    return {"q_total": q_total, "equation": "F.4/F.5b",
            "printed_page": "422-423", "pdf_page": "430-431"}


def wire_rope_wrap_reaction(t, b_deg):
    """Eq F.6: wire-rope Case c (rope wraps over the top edge of the skin
    plate) -- the edge reaction E from the two tension-vector components
    (printed p. 425).

        E = 2 * T * sin(B/2)

    Parameters
    ----------
    t : float
        Wire rope tension on each side of the wrap, kips.
    b_deg : float
        Angle of the bend B, measured from the tangent line extended,
        degrees.

    Returns
    -------
    dict
        {'e_reaction', 'equation': 'F.6', 'printed_page': '425', 'pdf_page': 433}
    """
    e_reaction = 2 * t * math.sin(math.radians(b_deg) / 2.0)
    return {"e_reaction": e_reaction, "equation": "F.6", "printed_page": "425", "pdf_page": 433}


# ============================================================================
# Appendix F.3 -- hydrostatic load by integration (printed pp. 426-428,
# pdf_page 434-436). VALIDATED against Table F.3 (printed p. 440-441).
# ============================================================================

def hydrostatic_radial_force(r, gamma_w, y, theta1, theta2):
    """Eq F.9: total radial hydrostatic force on the Tainter gate skin
    plate, per foot of gate length, by direct integration (printed p. 427).

        P = R*gamma_w * [R*(cos(th1) - cos(th2)) - Y*th1 + Y*th2]

    Angle convention (paragraph 10.10.2): angles are measured from a
    horizontal line at the trunnion centerline elevation, POSITIVE below
    horizontal and NEGATIVE above; theta1 is the angle to the top of the
    water surface (or top of gate) and theta2 to the bottom of the gate.

    Verified against Table F.3 (printed p. 440): R=40 ft, gamma_w=0.0625
    kcf, Y=16 ft, theta1=-0.412 rad, theta2=0.644 rad -> P = 53.85 kips/ft.

    Parameters
    ----------
    r : float
        Gate radius, ft.
    gamma_w : float
        Unit weight of water, kcf.
    y : float
        Depth from the water surface to the trunnion-pin centerline, ft.
    theta1, theta2 : float
        Angles (rad) to the top and bottom of the loaded skin plate arc,
        per the sign convention above.

    Returns
    -------
    dict
        {'p', 'equation': 'F.9', 'printed_page': '427', 'pdf_page': 435}
    """
    p = r * gamma_w * (r * (math.cos(theta1) - math.cos(theta2)) - y * theta1 + y * theta2)
    return {"p": p, "equation": "F.9", "printed_page": "427", "pdf_page": 435}


def hydrostatic_horizontal_component(r, gamma_w, y, theta1, theta2):
    """Eq F.10: horizontal component of the radial hydrostatic force
    (printed p. 427; see module docstring for the sign correction applied).

        Ph = R*gamma_w * [Y*(sin(th2) - sin(th1)) + (R/2)*(sin(th2)^2 - sin(th1)^2)]

    Verified against Table F.3 (printed p. 440): same inputs as
    ``hydrostatic_radial_force`` -> Ph = 50.0 kips/ft (also independently
    verified via the simplified projection form, Eq F.16, for this case
    where the water surface is at the top of the skin plate).

    Returns
    -------
    dict
        {'ph', 'equation': 'F.10', 'printed_page': '427', 'pdf_page': 435}
    """
    ph = r * gamma_w * (y * (math.sin(theta2) - math.sin(theta1))
                        + (r / 2.0) * (math.sin(theta2) ** 2 - math.sin(theta1) ** 2))
    return {"ph": ph, "equation": "F.10", "printed_page": "427", "pdf_page": 435}


def hydrostatic_vertical_component(r, gamma_w, y, theta1, theta2):
    """Eq F.11: vertical component of the radial hydrostatic force (printed
    p. 427).

        Pv = R*gamma_w * [Y*(cos(th1)-cos(th2)) + (R/4)*(2*th2-2*th1+sin(2*th1)-sin(2*th2))]

    Verified against Table F.3 (printed p. 440): same inputs as
    ``hydrostatic_radial_force`` -> Pv = 15.081 kips/ft.

    Returns
    -------
    dict
        {'pv', 'equation': 'F.11', 'printed_page': '427', 'pdf_page': 435}
    """
    pv = r * gamma_w * (y * (math.cos(theta1) - math.cos(theta2))
                        + (r / 4.0) * (2 * theta2 - 2 * theta1
                                       + math.sin(2 * theta1) - math.sin(2 * theta2)))
    return {"pv": pv, "equation": "F.11", "printed_page": "427", "pdf_page": 435}


def resultant_angle_from_horizontal(ph, pv):
    """The radial-force resultant angle from horizontal, theta_p (printed
    p. 427/440). See the module docstring: this implements atan(Pv/Ph), the
    form the worked example (printed p. 440) actually computes, not the
    atan(Ph/Pv) implied by the surrounding narrative text.

    Verified against Table F.3: Ph=50.0, Pv=15.081 -> theta_p = 0.293 rad.

    Returns
    -------
    dict
        {'theta_p_rad', 'printed_page': '427/440', 'pdf_page': '435/448'}
    """
    return {"theta_p_rad": math.atan(pv / ph), "printed_page": "427/440", "pdf_page": "435/448"}


def hydrostatic_moment(r, gamma_w, y, theta1, theta2):
    """Eq F.12/F.13: moment of the radial hydrostatic force about the
    trunnion-pin centerline (printed p. 427-428). Both the horizontal- and
    vertical-component moments (Mh, Mv) reduce to the SAME closed form
    (the manual notes, printed p. 441, that they must be identical because
    the moment of the hydrostatic head about the trunnion pin is zero).

        Mh = Mv = R^2*gamma_w * [(Y/2)*(sin(th2)^2-sin(th1)^2) + (R/3)*(sin(th2)^3-sin(th1)^3)]

    Verified against Table F.3 (printed p. 441): same inputs as
    ``hydrostatic_radial_force`` -> Mh = Mv = 533.33 kip-ft/ft.

    Returns
    -------
    dict
        {'mh', 'mv' (equal), 'equation': 'F.12/F.13', 'printed_page': '427-428',
         'pdf_page': '435-436'}
    """
    m = r ** 2 * gamma_w * ((y / 2.0) * (math.sin(theta2) ** 2 - math.sin(theta1) ** 2)
                            + (r / 3.0) * (math.sin(theta2) ** 3 - math.sin(theta1) ** 3))
    return {"mh": m, "mv": m, "equation": "F.12/F.13", "printed_page": "427-428", "pdf_page": "435-436"}


def hydrostatic_resultant_location(mh, ph, mv, pv):
    """Eq F.14/F.15: location of the resultant radial force below the
    trunnion (horizontal component) and from the trunnion centerline
    (vertical component) (printed p. 427).

        Yp = Mh / Ph
        Xp = Mv / Pv

    Verified against Table F.3 (printed p. 441): Mh=Mv=533.33, Ph=50.0,
    Pv=15.081 -> Yp=10.67 ft, Xp=35.36 ft.

    Returns
    -------
    dict
        {'yp', 'xp', 'equation': 'F.14/F.15', 'printed_page': '427',
         'pdf_page': 435}
    """
    return {"yp": mh / ph, "xp": mv / pv, "equation": "F.14/F.15",
            "printed_page": "427", "pdf_page": 435}


# ============================================================================
# Eq F.16 -- simplified hydrostatic projection (printed p. 429, pdf_page 437)
# ============================================================================

def hydrostatic_simplified_projection(gamma_w, h, el_trunnion=None, el_sill=None):
    """Eq F.16: simplified horizontal hydrostatic force by projecting the
    load onto a vertical plane, applicable when the water surface is at or
    below the top of the skin plate (printed p. 429).

        Ph = 0.5 * gamma_w * H^2

    The centroid of this triangular pressure distribution is H/3 above the
    sill; if trunnion and sill elevations are given, the moment arm Y from
    the trunnion centerline follows directly.

        Y = (EL_trunnion - EL_sill) - H/3

    Verified against the worked example (printed p. 440-441): gamma_w=
    0.0625 kcf, H=40 ft -> Ph=50.0 kips/ft (matches the integration method's
    Ph exactly, since the water surface is at the top of the gate in that
    example); EL_trunnion=910, EL_sill=886, H=40 (i.e. EL_trunnion -
    H = EL_bottom_of_gate = 886... using EL_trunnion-EL_sill=24 ft here,
    the worked value) -> Y=10.67 ft.

    Parameters
    ----------
    gamma_w : float
        Unit weight of water, kcf.
    h : float
        Height of the hydrostatic pressure triangle (headwater to sill or
        bottom of gate), ft.
    el_trunnion, el_sill : float, optional
        Trunnion and sill elevations, for the moment-arm Y.

    Returns
    -------
    dict
        {'ph', 'y' (if elevations given), 'equation': 'F.16',
         'printed_page': '429', 'pdf_page': 437}
    """
    ph = 0.5 * gamma_w * h ** 2
    out = {"ph": ph, "equation": "F.16", "printed_page": "429", "pdf_page": 437}
    if el_trunnion is not None and el_sill is not None:
        out["y"] = (el_trunnion - el_sill) - h / 3.0
    return out


# ============================================================================
# Appendix F.4 -- trunnion friction (printed pp. 435-436, pdf_page 443-444).
# VALIDATED against the worked example (printed p. 445).
# ============================================================================

def trunnion_reaction_force(rtx, rty):
    """Eq F.17 (magnitude/direction portion): resultant trunnion-pin
    reaction force from its net horizontal and vertical components (printed
    p. 436). See the module docstring for why the full component ASSEMBLY
    (Eq F.17-F.19) is left to the caller -- it requires site-specific load
    line-of-action angles.

        Rt = sqrt(Rtx^2 + Rty^2)
        theta_Rt = atan(|Rty| / |Rtx|)

    Verified against the worked example (printed p. 445): Rtx=-1336 kips,
    Rty=-363.0 kips -> Rt=1385 kips, theta_Rt=0.2653 rad.

    Parameters
    ----------
    rtx, rty : float
        Net horizontal and vertical components of the trunnion-pin
        reaction (sum of all applied-load components per the caller's own
        statics), kips.

    Returns
    -------
    dict
        {'rt', 'theta_rt_rad', 'equation': 'F.17', 'printed_page': '436',
         'pdf_page': 444}
    """
    rt = math.sqrt(rtx ** 2 + rty ** 2)
    theta_rt = math.atan(abs(rty) / abs(rtx))
    return {"rt": rt, "theta_rt_rad": theta_rt, "equation": "F.17",
            "printed_page": "436", "pdf_page": 444}


def trunnion_friction_force(mu, rt):
    """Eq F.17 (friction-force portion): trunnion-pin friction force
    (printed p. 436).

        Ft = mu * Rt

    Verified against the worked example (printed p. 445): mu=0.3, Rt=1385
    kips -> Ft=415.3 kips.

    Parameters
    ----------
    mu : float
        Trunnion coefficient of friction (nominal value 0.3 per paragraph
        10.2.11 -- see ``nominal_friction_coefficients``).
    rt : float
        Trunnion-pin reaction force (``trunnion_reaction_force``), kips.

    Returns
    -------
    dict
        {'ft', 'equation': 'F.17', 'printed_page': '436', 'pdf_page': 444}
    """
    return {"ft": mu * rt, "equation": "F.17", "printed_page": "436", "pdf_page": 444}


def trunnion_friction_moment(ft, r):
    """Trunnion-pin friction moment, Mt = Ft * r (printed p. 436).

    Verified against the worked example (printed p. 445): Ft=415.3 kips,
    r=0.5 ft (pin radius) -> Mt=207.7 kip-ft.

    Parameters
    ----------
    ft : float
        Trunnion friction force (``trunnion_friction_force``), kips.
    r : float
        Trunnion pin radius, ft.

    Returns
    -------
    dict
        {'mt', 'equation': 'F.17', 'printed_page': '436', 'pdf_page': 444}
    """
    return {"mt": ft * r, "equation": "F.17", "printed_page": "436", "pdf_page": 444}


# ============================================================================
# Eq 10.2-10.14 -- spillway Tainter gate strength load combinations
# (printed pp. 146-148, pdf_page 154-156). Formulas + citations only --
# assemble via ``loads.load_combination_lrfd``/``loads.earthquake_load_
# combination``, which implement the shared Eq 4.2/4.7-4.9 machinery these
# all specialize.
# ============================================================================

TABLE_10_LOAD_COMBINATIONS = {
    "10.2": {"description": "Maximum hydrostatic (hydraulic-cylinder-supported gate)",
             "formula": "(1.2 or 0.9)D + (1.6 or 0)G + gamma_pr*Hspr + (1.0 or 0)QDc + 1.0*(Hwc or IMc)",
             "printed_page": "146"},
    "10.3": {"description": "Maximum ice, impact, or wave (hydraulic-cylinder-supported gate)",
             "formula": "(1.2 or 0.9)D + (1.6 or 0)G + gamma_pr*(IXX or IMX or BIX or HwX) + 1.0*Hsc + (1.0 or 0)QDc",
             "printed_page": "146"},
    "10.4": {"description": "Maximum hydraulic cylinder load (where applicable)",
             "formula": "(1.2 or 0.9)D + (1.6 or 0)G + gamma_pr*QDpr + 1.0*Hsc",
             "printed_page": "147"},
    "10.5": {"description": "Maximum hydrostatic (wire-rope-supported gate; operating machinery forces are a reaction)",
             "formula": "(1.2 or 0.9)D + (1.6 or 0)G + gamma_pr*Hspr + 1.0*(Hwc or IMc)",
             "printed_page": "147"},
    "10.6": {"description": "Maximum impact (wire-rope-supported gate; operating machinery forces are a reaction)",
             "formula": "(1.2 or 0.9)D + (1.6 or 0)G + gamma_pr*(IXX or IMX or BIx or HwX) + 1.0*Hsc",
             "printed_page": "147"},
    "10.7": {"description": "Gate jammed / operating on obstruction: maximum hydrostatic + side-seal and trunnion friction (operating machinery forces are a reaction)",
             "formula": "(1.2 or 0.9)D + (1.6 or 0)G + gamma_pr*Hspr + 1.4*Fs + 1.4*Ft",
             "printed_page": "147"},
    "10.8": {"description": "Gate jammed: unusual hydrostatic (principal) + side-seal, side-sway, and trunnion friction",
             "formula": "(1.2 or 0.9)D + (1.6 or 0)G + 1.4*HsN + 1.4*Fs + 1.4*Fb + 1.4*Ft",
             "printed_page": "147"},
    "10.9": {"description": "Maximum operating equipment force (unusual)",
             "formula": "(1.2 or 0.9)D + (1.6 or 0)G + gamma_pr*QUpr + 1.0*Hsc",
             "printed_page": "147"},
    "10.10": {"description": "Dead + gravity + wind as the principal load",
              "formula": "(1.2 or 0.9)D + (1.6 or 0)G + 1.0*W",
              "printed_page": "148"},
    "10.11": {"description": "Supported or operating on two hoists: maximum operating equipment force (unusual)",
              "formula": "(1.2 or 0.9)D + (1.6 or 0)G + gamma_pr*QUpr",
              "printed_page": "148"},
    "10.12": {"description": "Earthquake, standard OBE ground motion (see loads.earthquake_load_combination method='standard_obe')",
              "formula": "(1.2 or 0.9)D + (1.6 or 0.0)G + 1.5*EQ + 1.0*Hsc",
              "printed_page": "148"},
    "10.13": {"description": "Earthquake, standard MDE ground motion (see loads.earthquake_load_combination method='standard_mde')",
              "formula": "(1.2 or 0.9)D + (1.6 or 0.0)G + 1.25*EQ + 1.0*Hsc",
              "printed_page": "148"},
    "10.14": {"description": "Earthquake, site-specific MDE/MCE ground motion (see loads.earthquake_load_combination method='site_specific')",
              "formula": "(1.2 or 0.9)D + (1.6 or 0.0)G + 1.0*EQ + 1.0*Hsc",
              "printed_page": "148"},
}


def table_10_load_combination(eq_number):
    """Eq 10.2-10.14: lookup of one of the spillway-Tainter-gate strength
    load-combination formulas (printed pp. 146-148).

    All are specializations of the general LRFD combination, Eq 4.2 (or the
    earthquake combinations, Eq 4.7-4.9) with gate-specific load labels;
    once each term's factored value is known, assemble the total demand U
    with ``loads.load_combination_lrfd``/``loads.earthquake_load_
    combination``.

    Parameters
    ----------
    eq_number : str
        A key of ``TABLE_10_LOAD_COMBINATIONS`` (e.g. '10.7').

    Returns
    -------
    dict
        {'equation', 'description', 'formula', 'printed_page', 'pdf_page'}
    """
    if eq_number not in TABLE_10_LOAD_COMBINATIONS:
        raise ValueError(f"eq_number must be one of {sorted(TABLE_10_LOAD_COMBINATIONS)}, got {eq_number!r}")
    row = dict(TABLE_10_LOAD_COMBINATIONS[eq_number])
    row["equation"] = eq_number
    row["pdf_page"] = int(row["printed_page"]) + 8
    return row


# ============================================================================
# Eq 10.15 -- trunnion girder anchorage shear-friction (printed p. 166,
# pdf_page 174)
# ============================================================================

def anchorage_shear_friction_check(vu, mu, r):
    """Eq 10.15: shear-friction check for a post-tensioned trunnion-girder
    anchorage interface (printed p. 166).

        Vu <= 0.85 * mu * R

    Parameters
    ----------
    vu : float
        Factored shear force at the girder/pier interface.
    mu : float
        Coefficient of friction for the interface.
    r : float
        Residual compressive (post-tensioning) force between the girder
        and pier.

    Returns
    -------
    dict
        {'vu', 'capacity', 'adequate' (bool), 'equation': '10.15',
         'printed_page': '166', 'pdf_page': 174}
    """
    capacity = 0.85 * mu * r
    return {"vu": vu, "capacity": capacity, "adequate": vu <= capacity,
            "equation": "10.15", "printed_page": "166", "pdf_page": 174}


# ============================================================================
# Nominal loads and serviceability limits (Chapter 10, various paragraphs)
# ============================================================================

def ice_debris_load():
    """Paragraphs 10.2.4.2 (IM) / 4.2.7 (IX): nominal uniform distributed
    load for floating ice/debris impact or thermally expanding ice on a
    Tainter gate (printed p. 144).

        5,000 lb/ft = 5 kip/ft, applied along the gate width

    Returns
    -------
    dict
        {'load_kip_per_ft': 5.0, 'printed_page': '144', 'pdf_page': 152}
    """
    return {"load_kip_per_ft": 5.0, "printed_page": "144", "pdf_page": 152}


def minimum_barge_impact_load(gate_width_ft):
    """Paragraph 10.2.5: minimum design barge-impact load for Tainter gates
    on navigable waterways (printed p. 144).

        BI_min = 5 kips/ft * gate opening width

    Parameters
    ----------
    gate_width_ft : float
        Width of the gate opening, ft.

    Returns
    -------
    dict
        {'bi_min_kips', 'printed_page': '144', 'pdf_page': 152}
    """
    return {"bi_min_kips": 5.0 * gate_width_ft, "printed_page": "144", "pdf_page": 152}


def girder_deflection_limit(length, cantilever=False):
    """Paragraph 10.8.1: maximum girder deflection (printed p. 152).

        between end frames:  L/800
        cantilever portion:  L/300 (end frame to pier face)

    Parameters
    ----------
    length : float
        Girder span (between end frames) or cantilever length.
    cantilever : bool, optional
        True for the cantilever-portion limit (L/300); False (default) for
        the between-end-frames limit (L/800).

    Returns
    -------
    dict
        {'length', 'cantilever', 'limit', 'printed_page': '152', 'pdf_page': 160}
    """
    divisor = 300.0 if cantilever else 800.0
    return {"length": length, "cantilever": cantilever, "limit": length / divisor,
            "printed_page": "152", "pdf_page": 160}


def skin_plate_deflection_limit(thickness):
    """Paragraph 10.8.1: maximum skin-plate deflection, 0.4 times the plate
    thickness (printed p. 152).
    """
    return {"thickness": thickness, "limit": 0.4 * thickness,
            "printed_page": "152", "pdf_page": 160}


def skin_plate_thickness_bounds():
    """Paragraph 10.12.1: recommended skin-plate thickness bounds (printed
    p. 154): minimum 3/8 in.; a thickness greater than 3/4 in. should be
    avoided.
    """
    return {"min_in": 0.375, "max_recommended_in": 0.75, "printed_page": "154", "pdf_page": 162}


def minimum_rib_depth():
    """Paragraph 10.12.3: minimum rib depth, typically 8 in. (shorter
    clearances usable if adequate weld quality can be demonstrated),
    printed p. 157.
    """
    return {"min_depth_in": 8.0, "printed_page": "157", "pdf_page": 165}
