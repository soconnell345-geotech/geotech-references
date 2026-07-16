"""AASHTO Guide for Design of Pavement Structures (1993) - roadbed swelling
and frost heave environmental serviceability-loss procedure.

Appendix G ("Treatment of Roadbed Swelling and/or Frost Heave in Design",
pdf_page 394-404, printed G-1 to G-11) plus the supporting Part II pieces
that consume it: Figure 2.2 (pdf_page 100, printed II-11, the conceptual
cumulative-environmental-loss-vs-time curve) and Table 3.1 (pdf_page 123,
printed II-34, the iterative performance-period worksheet in Section 3.1.3
"Roadbed Swelling and Frost Heave"). All page numbers are 0-based ``fitz``
page indices into ``docs/aashto1993.pdf`` (fully scanned, no text layer,
read visually), with the printed guide page also given.

Page map
--------
- G-1  (pdf 394): Appendix G intro + Section G.1 "Roadbed Swelling" text
  (swell rate constant, potential vertical rise VR, swell probability).
- G-2  (pdf 395): Figure G.1, US expansive-soils map -- qualitative
  background only, NOT digitized (no numeric axis).
- G-3  (pdf 396): Figure G.2, nomograph for the swell rate constant theta
  -- ``swell_rate_constant_theta``.
- G-4  (pdf 397): Figure G.3, chart for potential vertical rise VR --
  ``potential_vertical_rise``.
- G-5  (pdf 398): Table G.1, blank field worksheet form (bore hole / section
  length / PI / moisture condition / VR / soil fabric / theta) -- the
  computational content of this worksheet (weighted averaging across
  sections) is implemented as ``weighted_swell_parameters``.
- G-6  (pdf 399): text continuing G.1 (weighted-average guidance; swell
  probability 100% rule) and starting Section G.2 "Frost Heave".
- G-7  (pdf 400): Figure G.4, nomograph solving
  dPSI_sw = 0.00335*VR*Ps*(1-e^(-theta*t)) -- ``swelling_serviceability_loss``.
- G-8  (pdf 401): Figure G.5, seasonal frost/permafrost map -- qualitative
  background only, NOT digitized.
- G-9  (pdf 402): Figure G.6, chart for estimating frost heave rate from
  USCS group + percent finer than 0.02mm, plus the Frost Susceptibility
  Classification bar (Negligible..Very High vs rate, mm/day) --
  ``frost_susceptibility_classification`` and ``frost_heave_rate_group``.
- G-10 (pdf 403): Figure G.7, straight-line chart for maximum potential
  serviceability loss due to frost heave vs depth of frost penetration, by
  drainage quality -- ``max_serviceability_loss_frost``.
- G-11 (pdf 404): Figure G.8, nomograph solving
  dPSI_FH = 0.01*P_F*dPSI_MAX*(1-e^(-0.02*phi*t)) --
  ``frost_heave_serviceability_loss``.
- Figure 2.2 (pdf 100, printed II-11): conceptual cumulative
  swelling+frost-heave loss vs time -- ``total_environmental_loss``.
- Table 3.1 (pdf 123, printed II-34): the iterative performance-period
  worksheet -- ``performance_period_iteration``.

Units: US customary, as printed (VR in inches, frost heave rate phi in
mm/day as printed on Figure G.6/G.8, time in years, PI dimensionless,
depths in feet).
"""

import math

from geotech_references._interpolation import _linterp


# ============================================================================
# G.1 Roadbed Swelling -- Figure G.2: Nomograph for Estimating Swell Rate
# Constant, theta (pdf_page 396, printed G-3). CHART READ-OFF (alignment
# nomograph reconstruction).
#
# The chart is a straight-line "alignment chart": a left vertical scale
# (Moisture Supply, LOW at bottom to HIGH at top), a right vertical scale
# (Roadbed Soil Fabric, TIGHT at bottom to FRACTURED at top), and a FIXED
# diagonal "Swell Rate Constant" ruler running from the HIGH-moisture
# corner (theta=0.20) to the TIGHT-fabric corner (theta=0.04), ticked
# 0.04-0.20. The user marks a point on each side scale (A on moisture, B on
# fabric), draws a straight line A-B, and reads theta where that line
# crosses the fixed diagonal.
#
# Modeling this as a unit square (x=0 moisture axis, x=1 fabric axis; y=0
# LOW/TIGHT, y=1 HIGH/FRACTURED), the diagonal is the line from (0,1) to
# (1,0): theta(t) = 0.20 - 0.16*t for a point parametrized (t, 1-t). A
# straight line from A=(0,a) to B=(1,b) crosses that diagonal at
# t = (1-a)/(1+b-a) (derived by equating the two lines' y at a shared x=t;
# degenerates only at the single point a=1,b=0, i.e. A and B both sitting
# exactly on the diagonal's own two corners, where the limit t->0.5 is used).
#
# This reproduces the guide's own worked example (note d.4, pdf_page 396):
# points A, B illustrating the METHOD are read (visually, from the
# rendered chart) at approximately moisture_frac=0.21, fabric_frac=0.50 ->
# t=0.61 -> theta=0.10, matching the guide's printed "read 0.10" (the guide
# gives no numeric moisture_frac/fabric_frac for A/B -- "soil fabric...must
# be developed by each individual agency" -- so this is a consistency check
# of the geometric reconstruction, not an independent numeric anchor).
# The four corner values ARE exact by construction (they sit ON the fixed
# diagonal or its defining endpoints): LOW+TIGHT -> 0.04 (minimum, both
# conditions suppress swelling), HIGH+FRACTURED -> 0.20 (maximum, both
# maximize it), and the two "mixed" corners (HIGH+TIGHT, LOW+FRACTURED)
# both land on the diagonal's midpoint, 0.12 -- physically sensible, since
# a tight fabric chokes off high moisture and a fractured fabric can't help
# without moisture to admit.
# ============================================================================

_THETA_HIGH = 0.20
_THETA_TIGHT = 0.04
_THETA_MID = 0.5 * (_THETA_HIGH + _THETA_TIGHT)


def swell_rate_constant_theta(moisture_supply_frac, soil_fabric_frac) -> dict:
    """Swell rate constant theta from moisture supply and soil fabric (Fig. G.2).

    Reconstructs the printed alignment nomograph geometrically (see section
    docstring above): a straight line from a point on the Moisture Supply
    scale to a point on the Soil Fabric scale is read off a fixed diagonal
    ruler ticked 0.04 (TIGHT/LOW corner) to 0.20 (HIGH/FRACTURED corner).

        t = (1 - moisture_supply_frac) / (1 + soil_fabric_frac - moisture_supply_frac)
        theta = 0.20 - 0.16*t

    Consistency-checked against the guide's own worked example (Figure G.2
    note d.4): moisture_supply_frac~0.21, soil_fabric_frac~0.50 -> theta~0.10
    (printed "read 0.10"); the four corners are exact by construction (see
    section docstring). Away from the corners, moisture_supply_frac and
    soil_fabric_frac are inherently qualitative/agency-calibrated judgment
    calls per the guide's own text ("This scale must be developed by each
    individual agency") -- treat intermediate reads as +/-10%.

    Parameters
    ----------
    moisture_supply_frac : float
        Position on the Moisture Supply scale, 0 (LOW: low rainfall, good
        drainage) to 1 (HIGH: high rainfall, poor drainage, vicinity of
        culverts/bridge abutments/inlets).
    soil_fabric_frac : float
        Position on the Roadbed Soil Fabric scale, 0 (TIGHT) to 1
        (FRACTURED).

    Returns
    -------
    dict
        {'moisture_supply_frac', 'soil_fabric_frac', 'theta', 'chart_read',
         'equation', 'reference'}.

    Raises
    ------
    ValueError
        If either fraction is outside [0, 1].
    """
    if not (0.0 <= moisture_supply_frac <= 1.0):
        raise ValueError(
            f"moisture_supply_frac must be in [0, 1], got {moisture_supply_frac}"
        )
    if not (0.0 <= soil_fabric_frac <= 1.0):
        raise ValueError(
            f"soil_fabric_frac must be in [0, 1], got {soil_fabric_frac}"
        )
    denom = 1.0 + soil_fabric_frac - moisture_supply_frac
    if abs(denom) < 1e-9:
        # Degenerate case: A and B both sit on the diagonal's own corners
        # (moisture_supply_frac=1, soil_fabric_frac=0) -- limiting value.
        t = _THETA_MID  # placeholder, overwritten below via direct theta calc
        theta = _THETA_MID
    else:
        t = (1.0 - moisture_supply_frac) / denom
        theta = _THETA_HIGH - 0.16 * t
    return {
        "moisture_supply_frac": moisture_supply_frac,
        "soil_fabric_frac": soil_fabric_frac,
        "theta": round(theta, 4),
        "chart_read": True,
        "equation": ("t=(1-moisture_frac)/(1+fabric_frac-moisture_frac); "
                     "theta = 0.20 - 0.16*t"),
        "reference": "AASHTO 1993 Guide, Figure G.2 (pdf_page 396, printed G-3)",
    }


# ============================================================================
# G.1 Roadbed Swelling -- Figure G.3: Chart for Estimating the Approximate
# Potential Vertical Rise VR of Natural Soils (pdf_page 397, printed G-4).
# CHART READ-OFF -- a two-panel graphical-multiplication chart: a LEFT panel
# (Plasticity Index PI, 0-80, vs an unlabeled shared "height" axis, one
# curve per moisture condition) feeds a RIGHT panel (height vs VR, 0-10 in,
# one straight line per roadbed thickness, all through the origin).
#
# EXACT anchor (printed on the chart itself, guide's own worked example):
# PI=50, "Optimum Conditions" curve, 2 ft thickness of layer -> VR=0.83 in.
# This fixes the shared height scale: H_optimum(PI=50) := 1.0.
#
# LEFT PANEL (condition curves vs PI). No further printed numeric anchor
# exists on this chart, so the PI-dependence is modeled as a power law
# through a threshold PI0 (each condition needs less PI to reach a given
# height than a better-controlled one):
#   H(PI; PI0) = ((PI - PI0) / 20)^1.71,  PI >= PI0,  else 0
# PI0 = 30 for "optimum" reuses the guide's OWN printed swell-probability
# threshold (Appendix G.1 text: "probability...100 percent if PI...greater
# than 30"), which sets H_optimum(50) = 1.0 exactly (anchor). PI0 = 25
# ("average") and PI0 = 20 ("minimum") are read directly from the rendered
# chart (the three condition curves are visibly offset in PI by roughly
# this spacing, "Minimum Natural Dry" reaching a given height at the
# lowest PI, "Optimum" at the highest); the shared exponent 1.71 is a
# visual convexity read of the "optimum" curve's shape between PI~35 and
# PI~68. This gives H_average(50)=1.46, H_minimum(50)=2.00 relative to the
# H=1.0 anchor -- TREAT THESE AS COARSE (+/-30-40%) -- there is no
# independent printed check for the condition-to-condition spacing.
#
# RIGHT PANEL (thickness lines through the origin: VR = height * slope).
# slope(2 ft) = 0.83 EXACT (= VR anchor / H_optimum(50)=1.0). The other six
# thickness slopes are direct visual chart reads (where each labeled line
# crosses the same reference height as the anchor), COARSE (+/-20-25%):
#   thickness (ft):  2     5     10    15    20    25    30
#   slope (VR/H):   0.83  1.05  1.55  1.95  2.15  2.30  2.45
# Per the guide's own Table G.1 note, thicknesses greater than 30 ft use
# 30 ft (clamped here, not extrapolated).
# ============================================================================

_VR_CONDITION_PI0 = {"minimum": 20.0, "average": 25.0, "optimum": 30.0}
_VR_HEIGHT_EXPONENT = 1.71
_VR_HEIGHT_SCALE = 20.0

_VR_THICKNESS_VALUES = [2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
_VR_THICKNESS_SLOPES = [0.83, 1.05, 1.55, 1.95, 2.15, 2.30, 2.45]


def _vr_height(pi, condition):
    key = str(condition).strip().lower()
    if key not in _VR_CONDITION_PI0:
        raise ValueError(
            f"Unknown condition '{condition}'. Use one of: "
            f"{', '.join(_VR_CONDITION_PI0)}"
        )
    pi0 = _VR_CONDITION_PI0[key]
    if pi <= pi0:
        return 0.0
    return ((pi - pi0) / _VR_HEIGHT_SCALE) ** _VR_HEIGHT_EXPONENT


def _vr_thickness_slope(thickness_ft):
    return _linterp(thickness_ft, _VR_THICKNESS_VALUES, _VR_THICKNESS_SLOPES)


def potential_vertical_rise(pi, condition, thickness_ft) -> dict:
    """Potential vertical rise VR of natural soils (Figure G.3 chart read-off).

        VR = H(PI; condition) * slope(thickness_ft)

    where H is the left-panel condition curve (power law through a
    condition-specific PI threshold) and slope is the right-panel
    thickness line's slope (VR per unit H, both lines through the origin).
    See section docstring above for the full derivation and stated
    tolerances (EXACT at the printed anchor; COARSE, +/-20-40%, elsewhere).

    Verified against the guide's own printed worked example (Figure G.3,
    pdf_page 397, printed G-4): PI=50, condition='optimum',
    thickness_ft=2 -> VR=0.83 in EXACTLY (by construction).

    Parameters
    ----------
    pi : float
        Plasticity index of the swelling layer (ASTM D 424 / AASHTO T 90),
        >= the condition's threshold (20/25/30 for minimum/average/optimum)
        for a nonzero result.
    condition : str
        One of 'minimum' (Minimum Natural Dry Conditions, no moisture
        control), 'average' (Normal Field Control Moisture & Density), or
        'optimum' (Closely Controlled Moisture & Density Throughout Life
        of Facility).
    thickness_ft : float
        Thickness of the swelling roadbed layer, feet, > 0. Clamped to
        [2, 30] per the guide's own "greater than 30 feet, use 30 feet"
        note; values below 2 ft are also clamped (chart does not extend
        below the 2 ft curve) with a note.

    Returns
    -------
    dict
        {'pi', 'condition', 'thickness_ft', 'vr_in', 'chart_read',
         'equation', 'reference', 'note'?}.

    Raises
    ------
    ValueError
        If condition is unrecognized or thickness_ft <= 0.
    """
    if thickness_ft <= 0:
        raise ValueError(f"thickness_ft must be > 0, got {thickness_ft}")
    notes = []
    t_clamped = thickness_ft
    if thickness_ft > 30.0:
        t_clamped = 30.0
        notes.append("thickness_ft > 30 ft; clamped to 30 ft per the guide's own note.")
    elif thickness_ft < 2.0:
        t_clamped = 2.0
        notes.append("thickness_ft < 2 ft; clamped to the chart's minimum digitized curve (2 ft).")

    h = _vr_height(pi, condition)
    slope = _vr_thickness_slope(t_clamped)
    vr = h * slope
    out = {
        "pi": pi, "condition": str(condition).strip().lower(),
        "thickness_ft": thickness_ft, "vr_in": round(vr, 3),
        "chart_read": True,
        "equation": "VR = H(PI;condition) * slope(thickness_ft); H=((PI-PI0)/20)^1.71",
        "reference": "AASHTO 1993 Guide, Figure G.3 (pdf_page 397, printed G-4)",
    }
    if notes:
        out["note"] = " ".join(notes)
    return out


# ============================================================================
# G.1 Roadbed Swelling -- swell probability guidance (text, pdf_page 394-395,
# printed G-1/G-2; not a chart). Printed rule: probability of swelling at a
# given location = 100% if PI (AASHTO T 90) > 30 AND (layer thickness > 2 ft
# OR VR > 0.20 in).
# ============================================================================

def swell_probability_guidance(pi, thickness_ft=None, vr_in=None) -> dict:
    """Swell probability screening rule (Appendix G.1 text, pdf_page 394-395).

    The guide's printed rule: swell probability at a given location is
    considered 100 percent if the roadbed soil plasticity index (AASHTO
    T 90) is greater than 30 AND EITHER the swelling layer thickness is
    greater than 2 feet OR the potential vertical rise VR is greater than
    0.20 inches. Otherwise the guide directs the designer to estimate
    swell probability from the boring/lab program directly (no printed
    formula) -- this function returns ``is_100_pct=False`` with a note in
    that case rather than guessing a value.

    Parameters
    ----------
    pi : float
        Roadbed soil plasticity index (AASHTO T 90).
    thickness_ft : float, optional
        Thickness of the swelling layer, feet.
    vr_in : float, optional
        Potential vertical rise (see ``potential_vertical_rise``), inches.

    Returns
    -------
    dict
        {'pi', 'thickness_ft', 'vr_in', 'is_100_pct', 'ps_pct'?, 'reference',
         'note'?}. 'ps_pct' is only populated (100.0) when the rule fires.

    Raises
    ------
    ValueError
        If neither thickness_ft nor vr_in is given.
    """
    if thickness_ft is None and vr_in is None:
        raise ValueError("Provide at least one of thickness_ft or vr_in.")
    thick_trigger = thickness_ft is not None and thickness_ft > 2.0
    vr_trigger = vr_in is not None and vr_in > 0.20
    is_100 = pi > 30.0 and (thick_trigger or vr_trigger)
    out = {
        "pi": pi, "thickness_ft": thickness_ft, "vr_in": vr_in,
        "is_100_pct": is_100,
        "reference": "AASHTO 1993 Guide, Appendix G.1 (pdf_page 394-395, printed G-1/G-2)",
    }
    if is_100:
        out["ps_pct"] = 100.0
    else:
        out["note"] = (
            "Rule not triggered (PI<=30, or both thickness<=2ft and "
            "VR<=0.20in); the guide directs estimating swell probability "
            "directly from the boring/lab program -- no printed formula "
            "for the sub-100% case."
        )
    return out


# ============================================================================
# Table G.1: worksheet for section-length-weighted swell design parameters
# (pdf_page 398, printed G-5). Not a chart -- a blank field-data form; the
# computational content is the weighted-average procedure described in the
# surrounding text (pdf_page 399, printed G-6): VR and theta are
# length-weighted averages across ALL sections, while swell probability Ps
# is the length-weighted percent of TOTAL project length having VR greater
# than 0.20 inches (i.e. classified as "swelling" sections).
# ============================================================================

def weighted_swell_parameters(sections) -> dict:
    """Section-length-weighted swell design parameters (Table G.1 worksheet).

        VR_design = sum(VR_i * L_i) / sum(L_i)        (all sections)
        theta_design = sum(theta_i * L_i) / sum(L_i)  (all sections)
        Ps_design = 100 * sum(L_i : VR_i > 0.20in) / sum(L_i)   (all sections)

    Parameters
    ----------
    sections : list of dict
        One dict per bore-hole/section, each with:
          'length_ft' : float, required, > 0 -- length of roadway
              represented by this section.
          'vr_in' : float, required -- potential vertical rise for this
              section (see ``potential_vertical_rise``).
          'theta' : float, optional -- swell rate constant for this section
              (see ``swell_rate_constant_theta``); sections without a
              theta are excluded from the theta weighted-average only.

    Returns
    -------
    dict
        {'n_sections', 'total_length_ft', 'swelling_length_ft',
         'vr_design_in', 'theta_design'?, 'ps_design_pct', 'reference'}.
        'theta_design' is omitted if no section provides 'theta'.

    Raises
    ------
    ValueError
        If sections is empty, or any 'length_ft' <= 0, or any section is
        missing 'vr_in'.
    """
    if not sections:
        raise ValueError("sections must be a non-empty list of per-section dicts")
    total_length = 0.0
    vr_weighted_sum = 0.0
    theta_weighted_sum = 0.0
    theta_length_sum = 0.0
    swelling_length = 0.0
    for i, sec in enumerate(sections):
        length = sec.get("length_ft")
        if length is None or length <= 0:
            raise ValueError(f"sections[{i}]['length_ft'] must be > 0, got {length}")
        if "vr_in" not in sec:
            raise ValueError(f"sections[{i}] is missing the required key 'vr_in'")
        vr = sec["vr_in"]
        total_length += length
        vr_weighted_sum += vr * length
        if vr > 0.20:
            swelling_length += length
        if "theta" in sec and sec["theta"] is not None:
            theta_weighted_sum += sec["theta"] * length
            theta_length_sum += length

    out = {
        "n_sections": len(sections),
        "total_length_ft": round(total_length, 2),
        "swelling_length_ft": round(swelling_length, 2),
        "vr_design_in": round(vr_weighted_sum / total_length, 4),
        "ps_design_pct": round(100.0 * swelling_length / total_length, 2),
        "reference": "AASHTO 1993 Guide, Table G.1 (pdf_page 398, printed G-5)",
    }
    if theta_length_sum > 0:
        out["theta_design"] = round(theta_weighted_sum / theta_length_sum, 4)
    return out


# ============================================================================
# G.1 Roadbed Swelling -- Figure G.4: Chart for Estimating Serviceability
# Loss Due to Roadbed Swelling (pdf_page 400, printed G-7). PRINTED EQUATION
# (not a chart read-off -- the nomograph solves this closed form, given
# directly on the page):
#
#   dPSI_sw = 0.00335 * VR * Ps * (1 - e^(-theta*t))
#
# Ps enters as a PERCENT (0-100), not a fraction -- confirmed by the
# printed worked example: t=15 yr, theta=0.10, Ps=60%, VR=2 in ->
# 0.00335*2*60*(1-e^-1.5) = 0.402*0.7769 = 0.3123, matching the printed
# solution dPSI_sw=0.3 (rounded to 1 decimal on the chart).
# ============================================================================

def swelling_serviceability_loss(vr_in, ps_pct, theta, t_yr) -> dict:
    """Serviceability loss due to roadbed swelling (Figure G.4, printed equation).

        dPSI_sw = 0.00335 * VR * Ps * (1 - e^(-theta*t))

    Verified EXACTLY against the guide's own printed worked example (Figure
    G.4, pdf_page 400, printed G-7): t=15 yr, theta=0.10, Ps=60%, VR=2 in ->
    dPSI_sw=0.3123, printed solution 0.3 (chart rounds to 1 decimal).

    Parameters
    ----------
    vr_in : float
        Potential vertical rise (see ``potential_vertical_rise``), inches,
        >= 0.
    ps_pct : float
        Swell probability, PERCENT of total area subject to swell (0-100;
        see ``swell_probability_guidance`` / ``weighted_swell_parameters``).
    theta : float
        Swell rate constant (see ``swell_rate_constant_theta``), > 0
        (typically 0.04-0.20).
    t_yr : float
        Time since construction, years, >= 0.

    Returns
    -------
    dict
        {'vr_in', 'ps_pct', 'theta', 't_yr', 'delta_psi_sw', 'equation',
         'reference'}.

    Raises
    ------
    ValueError
        If vr_in < 0, ps_pct not in [0, 100], theta <= 0, or t_yr < 0.
    """
    if vr_in < 0:
        raise ValueError(f"vr_in must be >= 0, got {vr_in}")
    if not (0.0 <= ps_pct <= 100.0):
        raise ValueError(f"ps_pct must be in [0, 100], got {ps_pct}")
    if theta <= 0:
        raise ValueError(f"theta must be > 0, got {theta}")
    if t_yr < 0:
        raise ValueError(f"t_yr must be >= 0, got {t_yr}")
    delta_psi = 0.00335 * vr_in * ps_pct * (1.0 - math.exp(-theta * t_yr))
    return {
        "vr_in": vr_in, "ps_pct": ps_pct, "theta": theta, "t_yr": t_yr,
        "delta_psi_sw": round(delta_psi, 4),
        "equation": "dPSI_sw = 0.00335 * VR * Ps * (1 - e^(-theta*t))  (Ps in percent)",
        "reference": "AASHTO 1993 Guide, Figure G.4 (pdf_page 400, printed G-7)",
    }


# ============================================================================
# G.2 Frost Heave -- Figure G.7: Graph for Estimating Maximum Serviceability
# Loss Due to Frost Heave (pdf_page 403, printed G-10). Straight lines
# through the origin, one per drainage quality (Table 2.7-style categories:
# Excellent/Good/Fair/Poor/Very Poor). Slopes read directly off the chart's
# right edge (depth=10 ft): 1.0/2.0/3.0/4.0/5.0 -> slopes 0.10/0.20/0.30/
# 0.40/0.50 (clean round numbers, consistent with the printed worked
# example: depth=5 ft, "Poor" drainage -> dPSI_MAX=2.0 EXACTLY = 0.40*5).
# ============================================================================

_FROST_MAX_LOSS_SLOPE = {
    "excellent": 0.10, "good": 0.20, "fair": 0.30, "poor": 0.40, "very_poor": 0.50,
}
_FROST_MAX_LOSS_ORDER = list(_FROST_MAX_LOSS_SLOPE)


def max_serviceability_loss_frost(drainage_quality, depth_ft) -> dict:
    """Maximum potential serviceability loss due to frost heave (Figure G.7).

        dPSI_MAX = slope(drainage_quality) * depth_ft
        slope: excellent=0.10, good=0.20, fair=0.30, poor=0.40, very_poor=0.50

    Verified EXACTLY against the guide's own printed worked example (Figure
    G.7, pdf_page 403, printed G-10): drainage_quality='poor', depth_ft=5 ->
    dPSI_MAX=2.0 (printed "(2.0)"/"(5 feet)" dashed-line annotation).

    Parameters
    ----------
    drainage_quality : str
        One of 'excellent', 'good', 'fair', 'poor', 'very_poor'.
    depth_ft : float
        Depth of frost penetration, feet, >= 0 (chart digitized over 0-10 ft;
        the relation is a straight line through the origin so extrapolation
        beyond 10 ft is a modeling choice, flagged with a note).

    Returns
    -------
    dict
        {'drainage_quality', 'depth_ft', 'delta_psi_max', 'equation',
         'reference', 'note'?}.

    Raises
    ------
    ValueError
        If drainage_quality is unrecognized or depth_ft < 0.
    """
    key = str(drainage_quality).strip().lower().replace(" ", "_")
    if key not in _FROST_MAX_LOSS_SLOPE:
        raise ValueError(
            f"Unknown drainage_quality '{drainage_quality}'. Use one of: "
            f"{', '.join(_FROST_MAX_LOSS_ORDER)}"
        )
    if depth_ft < 0:
        raise ValueError(f"depth_ft must be >= 0, got {depth_ft}")
    slope = _FROST_MAX_LOSS_SLOPE[key]
    out = {
        "drainage_quality": key, "depth_ft": depth_ft,
        "delta_psi_max": round(slope * depth_ft, 3),
        "equation": "dPSI_MAX = slope(drainage_quality) * depth_ft",
        "reference": "AASHTO 1993 Guide, Figure G.7 (pdf_page 403, printed G-10)",
    }
    if depth_ft > 10.0:
        out["note"] = "depth_ft > 10 ft, beyond the digitized chart range -- linear extrapolation."
    return out


# ============================================================================
# G.2 Frost Heave -- Figure G.6: Chart for Estimating Frost Heave Rate for a
# Roadbed Soil, Part II (pdf_page 402, printed G-9). Two pieces:
#
# (1) The printed "Frost Susceptibility Classifications" bar (Negligible /
#     Very Low / Low / Medium / High / Very High) vs Average Rate of Heave,
#     mm/day (log scale). Boundary positions read directly off the chart
#     (log-scale pixel measurement): a clean geometric doubling sequence
#     0.5, 1, 2, 4, 8 mm/day -- ``frost_susceptibility_classification``.
#
# (2) The main body of the chart: irregular hatched/stippled polygons, one
#     per USCS group family, plotted on (percent finer than 0.02mm) vs
#     (rate of heave, mm/day), both log scale, PLUS four labeled sample
#     points A/B/C/D. The polygon boundaries are too irregular to trace
#     reliably from this raster scan; digitized here as a COARSE
#     representative rate RANGE per USCS group (the approximate horizontal
#     extent of each named region), NOT a continuous function of percent
#     fines -- ``frost_heave_rate_group``. Wide tolerance (+/-50%) is
#     explicitly stated; this is a rough screening aid only.
# ============================================================================

_FROST_SUSCEPT_BOUNDARIES = [0.5, 1.0, 2.0, 4.0, 8.0]
_FROST_SUSCEPT_LABELS = ["negligible", "very_low", "low", "medium", "high", "very_high"]


def frost_susceptibility_classification(rate_mm_day) -> dict:
    """Frost susceptibility classification from average heave rate (Fig. G.6 bar).

    Boundaries (mm/day), read off the chart's log-scale classification bar:
    Negligible <0.5, Very Low 0.5-1, Low 1-2, Medium 2-4, High 4-8,
    Very High >8. Chart-read from log-axis pixel positions; treat boundary
    precision as +/-15%.

    Parameters
    ----------
    rate_mm_day : float
        Average rate of frost heave, mm/day, >= 0.

    Returns
    -------
    dict
        {'rate_mm_day', 'classification', 'chart_read', 'reference'}.

    Raises
    ------
    ValueError
        If rate_mm_day < 0.
    """
    if rate_mm_day < 0:
        raise ValueError(f"rate_mm_day must be >= 0, got {rate_mm_day}")
    idx = 0
    for boundary in _FROST_SUSCEPT_BOUNDARIES:
        if rate_mm_day < boundary:
            break
        idx += 1
    else:
        idx = len(_FROST_SUSCEPT_BOUNDARIES)
    return {
        "rate_mm_day": rate_mm_day, "classification": _FROST_SUSCEPT_LABELS[idx],
        "chart_read": True,
        "reference": ("AASHTO 1993 Guide, Figure G.6 classification bar "
                     "(pdf_page 402, printed G-9)"),
    }


_FROST_RATE_GROUP_RANGES = {
    "gw": (0.3, 1.0), "gp": (0.3, 1.0),
    "sw": (0.5, 1.3), "sp": (0.5, 1.3),
    "gm": (1.0, 3.0), "gw-gm": (1.0, 3.0), "gp-gm": (1.0, 3.0),
    "sm": (0.7, 2.5), "sw-sm": (0.7, 2.5), "sp-sm": (0.7, 2.5),
    "gc": (1.5, 3.5), "gw-gc": (1.5, 3.5), "gm-gc": (1.5, 3.5),
    "sc": (1.0, 3.0), "sm-sc": (1.0, 3.0),
    "cl_high_pi": (0.5, 2.0), "cl_low_pi": (0.3, 1.5), "cl-ol": (0.3, 1.5),
    "ml": (1.0, 3.0), "ml-ol": (1.0, 3.0),
    "ch": (0.2, 0.6),
}


def frost_heave_rate_group(uscs_group) -> dict:
    """Coarse frost heave rate estimate by USCS group (Figure G.6 chart read-off).

    Digitized as an approximate rate RANGE per labeled USCS-group region on
    the chart (see section docstring above) -- NOT a function of percent
    fines (the polygon boundaries resist reliable tracing from this scan).
    Wide tolerance: treat as a rough screening range, +/-50%.

    Parameters
    ----------
    uscs_group : str
        USCS group symbol. One of: 'gw', 'gp', 'sw', 'sp', 'gm', 'gw-gm',
        'gp-gm', 'sm', 'sw-sm', 'sp-sm', 'gc', 'gw-gc', 'gm-gc', 'sc',
        'sm-sc', 'cl_high_pi' (lean/gravelly/sandy clays, PI>12),
        'cl_low_pi' or 'cl-ol' (PI<12), 'ml', 'ml-ol', 'ch' (fat clay).

    Returns
    -------
    dict
        {'uscs_group', 'rate_range_mm_day', 'rate_mm_day' (midpoint),
         'classification', 'chart_read', 'reference', 'note'}.

    Raises
    ------
    ValueError
        If uscs_group is unrecognized.
    """
    key = str(uscs_group).strip().lower()
    if key not in _FROST_RATE_GROUP_RANGES:
        raise ValueError(
            f"Unknown uscs_group '{uscs_group}'. Use one of: "
            f"{', '.join(_FROST_RATE_GROUP_RANGES)}"
        )
    lo, hi = _FROST_RATE_GROUP_RANGES[key]
    mid = 0.5 * (lo + hi)
    return {
        "uscs_group": key, "rate_range_mm_day": (lo, hi),
        "rate_mm_day": round(mid, 2),
        "classification": frost_susceptibility_classification(mid)["classification"],
        "chart_read": True,
        "reference": "AASHTO 1993 Guide, Figure G.6 (pdf_page 402, printed G-9)",
        "note": ("Coarse per-group range read from the chart's irregular "
                "polygon regions, not a function of percent fines -- "
                "treat as a rough screening estimate, +/-50%."),
    }


# ============================================================================
# G.2 Frost Heave -- Figure G.8: Chart for Estimating Serviceability Loss
# Due to Frost Heave (pdf_page 404, printed G-11). PRINTED EQUATION:
#
#   dPSI_FH = 0.01 * P_F * dPSI_MAX * [1 - e^(-0.02*phi*t)]
#
# The printed exponent constant renders as "0 2" (guide's no-decimal-point
# typographic convention, e.g. Figure G.2's "0 10"); reproducing the
# printed worked example (t=15 yr, phi=5 mm/day, P_F=30%, dPSI_MAX=2.0 ->
# solution dPSI_FH=0.47) requires the constant to be 0.02, NOT 0.2 (0.02
# gives 0.01*30*2.0*(1-e^-1.5)=0.6*0.7769=0.4661~0.47 EXACT; 0.2 would give
# 1-e^-15~1.0 -> 0.6, not matching) -- resolved here as 0.02.
# ============================================================================

def frost_heave_serviceability_loss(phi_mm_day, pf_pct, delta_psi_max, t_yr) -> dict:
    """Serviceability loss due to frost heave (Figure G.8, printed equation).

        dPSI_FH = 0.01 * P_F * dPSI_MAX * [1 - e^(-0.02*phi*t)]

    Verified EXACTLY against the guide's own printed worked example (Figure
    G.8, pdf_page 404, printed G-11): t=15 yr, phi=5 mm/day, P_F=30%,
    dPSI_MAX=2.0 -> dPSI_FH=0.4661, printed solution 0.47.

    Parameters
    ----------
    phi_mm_day : float
        Frost heave rate, mm/day (see ``frost_susceptibility_classification``
        / ``frost_heave_rate_group``), >= 0.
    pf_pct : float
        Frost heave probability, PERCENT of total area subject to frost
        heave (0-100).
    delta_psi_max : float
        Maximum potential serviceability loss (see
        ``max_serviceability_loss_frost``), >= 0.
    t_yr : float
        Time since construction, years, >= 0.

    Returns
    -------
    dict
        {'phi_mm_day', 'pf_pct', 'delta_psi_max', 't_yr', 'delta_psi_fh',
         'equation', 'reference'}.

    Raises
    ------
    ValueError
        If phi_mm_day < 0, pf_pct not in [0, 100], delta_psi_max < 0, or
        t_yr < 0.
    """
    if phi_mm_day < 0:
        raise ValueError(f"phi_mm_day must be >= 0, got {phi_mm_day}")
    if not (0.0 <= pf_pct <= 100.0):
        raise ValueError(f"pf_pct must be in [0, 100], got {pf_pct}")
    if delta_psi_max < 0:
        raise ValueError(f"delta_psi_max must be >= 0, got {delta_psi_max}")
    if t_yr < 0:
        raise ValueError(f"t_yr must be >= 0, got {t_yr}")
    delta_psi = 0.01 * pf_pct * delta_psi_max * (1.0 - math.exp(-0.02 * phi_mm_day * t_yr))
    return {
        "phi_mm_day": phi_mm_day, "pf_pct": pf_pct,
        "delta_psi_max": delta_psi_max, "t_yr": t_yr,
        "delta_psi_fh": round(delta_psi, 4),
        "equation": "dPSI_FH = 0.01 * P_F * dPSI_MAX * [1 - e^(-0.02*phi*t)]  (P_F in percent)",
        "reference": "AASHTO 1993 Guide, Figure G.8 (pdf_page 404, printed G-11)",
    }


# ============================================================================
# Figure 2.2: A Conceptual Example of the Environmental Serviceability Loss
# Versus Time Graph (pdf_page 100, printed II-11). Purely additive: total
# environmental loss at time t is the sum of the swelling and frost-heave
# components (each independently evaluated via the Figure G.4/G.8 equations
# above). Figure 2.2 itself is explicitly labeled "conceptual" -- its curve
# is illustrative artwork, not tied to specific printed VR/Ps/theta/phi/P_F/
# dPSI_MAX values, so this function is verified structurally (the printed
# total-loss curve equals swelling-loss-curve plus frost-heave-loss-curve
# at every t, which the figure itself shows), not against a numeric anchor.
# ============================================================================

def total_environmental_loss(t_yr, swelling=None, frost=None) -> dict:
    """Total (swelling + frost heave) serviceability loss at time t (Figure 2.2).

        dPSI_SW,FH(t) = dPSI_sw(t) + dPSI_FH(t)

    Parameters
    ----------
    t_yr : float
        Time since construction, years, >= 0.
    swelling : dict, optional
        Spec dict with keys 'vr_in', 'ps_pct', 'theta' (see
        ``swelling_serviceability_loss``). Omit if swelling is not
        applicable at this location.
    frost : dict, optional
        Spec dict with keys 'phi_mm_day', 'pf_pct', 'delta_psi_max' (see
        ``frost_heave_serviceability_loss``). Omit if frost heave is not
        applicable at this location.

    Returns
    -------
    dict
        {'t_yr', 'delta_psi_sw'?, 'delta_psi_fh'?, 'delta_psi_total',
         'reference'}. Component keys are included only when that spec was
         given.

    Raises
    ------
    ValueError
        If neither swelling nor frost is given, or t_yr < 0.
    """
    if swelling is None and frost is None:
        raise ValueError("Provide at least one of swelling or frost.")
    if t_yr < 0:
        raise ValueError(f"t_yr must be >= 0, got {t_yr}")
    out = {"t_yr": t_yr}
    total = 0.0
    if swelling is not None:
        sw = swelling_serviceability_loss(
            vr_in=swelling["vr_in"], ps_pct=swelling["ps_pct"],
            theta=swelling["theta"], t_yr=t_yr,
        )
        out["delta_psi_sw"] = sw["delta_psi_sw"]
        total += sw["delta_psi_sw"]
    if frost is not None:
        fh = frost_heave_serviceability_loss(
            phi_mm_day=frost["phi_mm_day"], pf_pct=frost["pf_pct"],
            delta_psi_max=frost["delta_psi_max"], t_yr=t_yr,
        )
        out["delta_psi_fh"] = fh["delta_psi_fh"]
        total += fh["delta_psi_fh"]
    out["delta_psi_total"] = round(total, 4)
    out["reference"] = "AASHTO 1993 Guide, Figure 2.2 (pdf_page 100, printed II-11)"
    return out


# ============================================================================
# Table 3.1: Example of Process Used to Predict the Performance Period of an
# Initial Pavement Structure Considering Swelling and/or Frost Heave
# (pdf_page 123, printed II-34; Section 3.1.3 "Roadbed Swelling and Frost
# Heave"). The printed 6-column worksheet, per iteration:
#   (1) iteration number
#   (2) trial performance period, t (years) -- designer's estimate
#   (3) total environmental loss dPSI_SW,FH(t) -- from Figure 2.2 (here,
#       ``total_environmental_loss``)
#   (4) corresponding traffic-serviceability-loss budget,
#       dPSI_TR = dPSI_design - dPSI_SW,FH(t)
#   (5) allowable cumulative 18-kip ESAL traffic -- from Figure 3.1 IN
#       REVERSE, holding SN/reliability/MR constant except for using
#       dPSI_TR from column 4 (here, a caller-supplied ``w18_fn(dPSI_TR)``,
#       so the caller pre-binds SN/ZR/So/MR -- e.g. via
#       ``equations.flexible_w18_from_sn`` -- or D/etc. for a rigid design)
#   (6) the calendar year at which that cumulative traffic is reached, from
#       the project's cumulative-traffic-vs-time relationship (Figure 2.1;
#       project/traffic-growth-rate specific, no printed universal formula
#       -- caller-supplied ``time_from_w18_fn(w18)``)
#
# CONVERGENCE RULE (reverse-engineered from the guide's own printed 3-row
# example, reproduced exactly below): the next trial period is the average
# of the current trial and the current column-6 result, iterated until
# they coincide within tolerance:
#   trial_1=13.0 -> col6=6.3;  trial_2=(13.0+6.3)/2=9.65~9.7 -> col6=7.2;
#   trial_3=(9.7+7.2)/2=8.45~8.5 -> col6=8.2 (converging toward ~8.3 yr).
#
# NOTE (transparency): the guide's OWN prose around Table 3.1 (pdf_page
# 123-124, printed II-33/34) describes a companion worked example (R=95%,
# MR=5,000 psi, po=4.4, pt=2.5 -> dPSI=1.9, 15-yr/5x10^6-ESAL initial
# pavement -> "maximum SN...is 4.4") that this module could NOT reconcile
# end-to-end against ``equations.flexible_w18_from_sn`` using the So=0.35
# used elsewhere in this package (an So around 0.12 would be needed to tie
# SN=4.4 to W18=5x10^6 at that dPSI; the guide's text does not print an So
# for this specific example). The three ROW-TO-ROW arithmetic
# relationships in Table 3.1 itself (columns 3->4, and the trial-period
# averaging 2->6->2) ARE fully and exactly reproducible from the printed
# table alone and are what this function implements and what its tests
# verify (via directly injected column-3/5/6 callables reproducing the
# printed numbers) -- the SN=4.4 reliability-chain figure is flagged, not
# silently assumed.
# ============================================================================

def performance_period_iteration(
    delta_psi_design, w18_fn, time_from_w18_fn,
    initial_trial_yr=None, max_performance_period_yr=None,
    swelling=None, frost=None, env_loss_fn=None,
    max_iter=10, tol=0.1,
) -> dict:
    """Iterative performance-period worksheet with swelling/frost heave (Table 3.1).

    At each iteration, the environmental serviceability loss expected over
    the trial performance period eats into the total design serviceability
    loss budget; the REMAINING budget is allocated to traffic and converted
    (via the caller's design-equation-in-reverse) to an allowable cumulative
    18-kip ESAL traffic, which is in turn converted (via the caller's
    traffic-growth relationship) to the calendar year that traffic level is
    reached. The next trial period is the average of the current trial and
    that result; iteration stops when they agree within ``tol`` (or
    ``max_iter`` is reached). See section docstring above for the exact
    convergence rule (reverse-engineered from, and verified against, the
    guide's own printed 3-row example) and an important transparency note
    on what could and could not be independently reconciled from the guide.

    Parameters
    ----------
    delta_psi_design : float
        Total design serviceability loss budget, po - pt (traffic +
        environmental combined), > 0.
    w18_fn : callable
        ``w18_fn(delta_psi_traffic) -> w18_cumulative``. Caller-supplied;
        pre-bind SN (or D), ZR, So, MR (or the rigid-design equivalents)
        and pass e.g. ``lambda dpsi: equations.flexible_w18_from_sn(sn=4.4,
        zr=-1.645, so=0.35, delta_psi=dpsi, mr_psi=5000)['w18']``.
    time_from_w18_fn : callable
        ``time_from_w18_fn(w18_cumulative) -> years``. Caller-supplied
        project traffic-growth relationship (Figure 2.1 is a plot, not a
        printed universal formula).
    initial_trial_yr : float, optional
        Starting trial performance period, years. Default
        ``0.9 * max_performance_period_yr`` (per the guide's own Step 2
        guidance: "should be less than the maximum possible performance
        period").
    max_performance_period_yr : float, optional
        Maximum possible performance period (years) for the selected
        initial structural number (Section 2.1.1). Required if
        ``initial_trial_yr`` is not given.
    swelling : dict, optional
        Spec dict for ``total_environmental_loss`` (see that function).
    frost : dict, optional
        Spec dict for ``total_environmental_loss``.
    env_loss_fn : callable, optional
        ``env_loss_fn(t_yr) -> delta_psi_env``, overriding ``swelling``/
        ``frost`` entirely (e.g. to inject a directly-read Figure 2.2
        curve, or for testing against the printed table). If given,
        ``swelling``/``frost`` are ignored.
    max_iter : int, optional
        Maximum iterations, default 10.
    tol : float, optional
        Convergence tolerance on |trial_period - corresponding_period|,
        years, default 0.1.

    Returns
    -------
    dict
        {'rows': [{'iteration', 'trial_period_yr', 'delta_psi_env',
         'delta_psi_traffic', 'w18_cumulative', 'corresponding_period_yr'},
         ...], 'converged', 'n_iterations', 'performance_period_yr'
         (the final corresponding_period_yr), 'delta_psi_design',
         'reference'}.

    Raises
    ------
    ValueError
        If delta_psi_design <= 0, no environmental-loss source is given
        (env_loss_fn or swelling/frost), no initial_trial_yr and no
        max_performance_period_yr is given, or a trial period ever yields
        a non-positive traffic serviceability-loss budget (environmental
        loss has consumed the entire design budget).
    """
    if delta_psi_design <= 0:
        raise ValueError(f"delta_psi_design must be > 0, got {delta_psi_design}")
    if env_loss_fn is None and swelling is None and frost is None:
        raise ValueError("Provide env_loss_fn, or at least one of swelling/frost.")
    if initial_trial_yr is None:
        if max_performance_period_yr is None:
            raise ValueError(
                "Provide initial_trial_yr, or max_performance_period_yr to "
                "derive a default (0.9 * max_performance_period_yr)."
            )
        initial_trial_yr = 0.9 * max_performance_period_yr

    def _env_loss(t):
        if env_loss_fn is not None:
            return env_loss_fn(t)
        return total_environmental_loss(t, swelling=swelling, frost=frost)["delta_psi_total"]

    rows = []
    trial = initial_trial_yr
    converged = False
    n = 0
    corresponding = trial
    for n in range(1, max_iter + 1):
        env_loss = _env_loss(trial)
        traffic_loss = delta_psi_design - env_loss
        if traffic_loss <= 0:
            raise ValueError(
                f"At trial_period={trial:.2f} yr, environmental loss "
                f"({env_loss:.4f}) consumes the entire design budget "
                f"({delta_psi_design}) -- no traffic capacity remains."
            )
        w18 = w18_fn(traffic_loss)
        corresponding = time_from_w18_fn(w18)
        rows.append({
            "iteration": n, "trial_period_yr": round(trial, 2),
            "delta_psi_env": round(env_loss, 4),
            "delta_psi_traffic": round(traffic_loss, 4),
            "w18_cumulative": w18,
            "corresponding_period_yr": round(corresponding, 2),
        })
        if abs(trial - corresponding) <= tol:
            converged = True
            break
        trial = 0.5 * (trial + corresponding)

    return {
        "rows": rows, "converged": converged, "n_iterations": n,
        "performance_period_yr": round(corresponding, 2),
        "delta_psi_design": delta_psi_design,
        "reference": "AASHTO 1993 Guide, Table 3.1 (pdf_page 123, printed II-34)",
    }
