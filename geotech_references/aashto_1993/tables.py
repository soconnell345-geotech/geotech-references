"""AASHTO Guide for Design of Pavement Structures (1993) - table lookups.

Digitized tables and chart-based (nomograph) read-offs from Part I
(Reliability) and Part II (Design Requirements / Structural Design), plus
the single- and tandem-axle Appendix D load equivalency factor (ESAL)
lookups, which read the full printed tables through ``lef.py``. Units follow the guide (US customary): psi, pci, inches, kips.

PDF pages cited below are 0-based fitz page indices into
``docs/aashto1993.pdf``; the printed guide page (e.g. "II-20") is also given.
Chart-based functions (layer coefficient a1, cement/bituminous-treated a2)
are read off a printed nomograph rather than a closed-form equation; each
says so explicitly and lists the digitized (x, y) anchor points.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 4.1: Standard Normal Deviate (ZR) vs Reliability Level
# (Part I, Section 4.2.3; pdf_page_index 83, printed I-62)
# ============================================================================

_ZR_R = [50, 60, 70, 75, 80, 85, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
        99.9, 99.99]
_ZR_Z = [-0.000, -0.253, -0.524, -0.674, -0.841, -1.037, -1.282, -1.340,
        -1.405, -1.476, -1.555, -1.645, -1.751, -1.881, -2.054, -2.327,
        -3.090, -3.750]


def standard_normal_deviate_zr(reliability_pct) -> dict:
    """Standard normal deviate ZR for a design reliability level (Table 4.1).

    Exact at the tabulated reliability levels (50, 60, 70, 75, 80, 85,
    90-99 by 1, 99.9, 99.99); linearly interpolated between them (the
    guide's own Table 4.1 is itself already a discretized lookup from
    standard normal-curve area tables, so interpolation between adjacent
    tabulated levels is the intended use).

    Parameters
    ----------
    reliability_pct : float
        Design reliability level R, percent, in [50, 99.99].

    Returns
    -------
    dict
        {'reliability_pct', 'zr', 'reference'}.

    Raises
    ------
    ValueError
        If reliability_pct is outside [50, 99.99].
    """
    if not (50 <= reliability_pct <= 99.99):
        raise ValueError(
            f"reliability_pct must be in [50, 99.99], got {reliability_pct}"
        )
    zr = _linterp(reliability_pct, _ZR_R, _ZR_Z)
    return {
        "reliability_pct": reliability_pct, "zr": round(zr, 3),
        "reference": "AASHTO 1993 Guide, Table 4.1 (pdf_page_index 83, printed I-62)",
    }


# ============================================================================
# Table 2.2: Suggested Levels of Reliability for Various Functional
# Classifications (Part II, Section 2.1.3; pdf_page_index 98, printed II-9)
# ============================================================================

_TABLE_2_2 = {
    "interstate_freeway": {"urban": (85, 99.9), "rural": (80, 99.9)},
    "principal_arterial": {"urban": (80, 99), "rural": (75, 95)},
    "collector": {"urban": (80, 95), "rural": (75, 95)},
    "local": {"urban": (50, 80), "rural": (50, 80)},
}

_FUNCTIONAL_CLASS_ALIASES = {
    "interstate": "interstate_freeway", "freeway": "interstate_freeway",
    "interstate_freeway": "interstate_freeway", "other_freeway": "interstate_freeway",
    "principal_arterial": "principal_arterial", "arterial": "principal_arterial",
    "collector": "collector",
    "local": "local",
}


def recommended_reliability(functional_class, area="urban") -> dict:
    """Suggested reliability range by functional classification (Table 2.2).

    Based on a survey of the inherent reliability in current (1993) state
    DOT design procedures, by functional class and urban/rural condition.

    Parameters
    ----------
    functional_class : str
        'interstate_freeway' (or 'interstate'/'freeway'), 'principal_arterial'
        (or 'arterial'), 'collector', or 'local'.
    area : str, optional
        'urban' (default) or 'rural'.

    Returns
    -------
    dict
        {'functional_class', 'area', 'reliability_min_pct',
         'reliability_max_pct', 'reference'}.

    Raises
    ------
    ValueError
        If functional_class or area is unrecognized.
    """
    key = str(functional_class).strip().lower().replace(" ", "_")
    if key not in _FUNCTIONAL_CLASS_ALIASES:
        raise ValueError(
            f"Unknown functional_class '{functional_class}'. Use: "
            f"{', '.join(sorted(set(_FUNCTIONAL_CLASS_ALIASES))) }"
        )
    canonical = _FUNCTIONAL_CLASS_ALIASES[key]
    a = str(area).strip().lower()
    if a not in ("urban", "rural"):
        raise ValueError(f"area must be 'urban' or 'rural', got '{area}'")
    lo, hi = _TABLE_2_2[canonical][a]
    return {
        "functional_class": canonical, "area": a,
        "reliability_min_pct": lo, "reliability_max_pct": hi,
        "reference": "AASHTO 1993 Guide, Table 2.2 (pdf_page_index 98, printed II-9)",
    }


def overall_standard_deviation_range(pavement_type) -> dict:
    """Recommended overall standard deviation So range (Section 4.3).

    Interim criteria: rigid 0.30-0.40, flexible 0.40-0.50 (Part I, Section
    4.3). The guide also gives narrower AASHO-Road-Test-anchored figures
    for two sub-cases: WITH projected-traffic variance included (rigid
    0.39, flexible 0.49) and WITHOUT it (rigid 0.34, flexible 0.44).

    Parameters
    ----------
    pavement_type : str
        'flexible' or 'rigid'.

    Returns
    -------
    dict
        {'pavement_type', 'so_min', 'so_max', 'so_with_traffic_variance',
         'so_without_traffic_variance', 'reference'}.

    Raises
    ------
    ValueError
        If pavement_type is not 'flexible' or 'rigid'.
    """
    key = str(pavement_type).strip().lower()
    if key == "flexible":
        out = {"so_min": 0.40, "so_max": 0.50,
              "so_with_traffic_variance": 0.49,
              "so_without_traffic_variance": 0.44}
    elif key == "rigid":
        out = {"so_min": 0.30, "so_max": 0.40,
              "so_with_traffic_variance": 0.39,
              "so_without_traffic_variance": 0.34}
    else:
        raise ValueError(f"pavement_type must be 'flexible' or 'rigid', got '{pavement_type}'")
    out.update({
        "pavement_type": key,
        "reference": "AASHTO 1993 Guide, Section 4.3 (pdf_page_index 83, printed I-62)",
    })
    return out


def terminal_serviceability_guidance(pt=None) -> dict:
    """Terminal serviceability index guidance (Section 2.2.1).

    po (AASHO Road Test observed initial serviceability) = 4.2 flexible,
    4.5 rigid. pt=2.5 or higher suggested for major highways, pt=2.0 for
    lesser-volume highways. Public-acceptance survey data (from AASHO Road
    Test connected studies) for the percent of people rating a given pt
    "unacceptable": pt=3.0 -> 12%, pt=2.5 -> 55%, pt=2.0 -> 85%.

    Parameters
    ----------
    pt : float, optional
        If given (3.0, 2.5, or 2.0), returns just that row's
        percent-unacceptable. If omitted, returns the full table.

    Returns
    -------
    dict
        {'po_flexible', 'po_rigid', 'rows' or 'pt'/'percent_unacceptable',
         'reference'}.

    Raises
    ------
    ValueError
        If pt is given but not one of 3.0, 2.5, 2.0.
    """
    rows = [
        {"pt": 3.0, "percent_unacceptable": 12},
        {"pt": 2.5, "percent_unacceptable": 55},
        {"pt": 2.0, "percent_unacceptable": 85},
    ]
    base = {
        "po_flexible": 4.2, "po_rigid": 4.5,
        "reference": "AASHTO 1993 Guide, Section 2.2.1 (pdf_page_index 99, printed II-10)",
    }
    if pt is None:
        base["rows"] = rows
        return base
    match = next((r for r in rows if abs(r["pt"] - pt) < 1e-9), None)
    if match is None:
        raise ValueError(f"pt must be one of 3.0, 2.5, 2.0, got {pt}")
    base.update(match)
    return base


# ============================================================================
# Traffic distribution (Section 2.1.2; pdf_page_index 97-98, printed II-8/9)
# ============================================================================

_DL_TABLE = {1: (100, 100), 2: (80, 100), 3: (60, 80), 4: (50, 75)}


def lane_distribution_factor(num_lanes_per_direction) -> dict:
    """Percent of 18-kip ESAL traffic in the design lane, by lane count.

    Parameters
    ----------
    num_lanes_per_direction : int
        Number of lanes in each direction: 1, 2, 3, or "4" (4 or more).

    Returns
    -------
    dict
        {'num_lanes_per_direction', 'dl_min_pct', 'dl_max_pct', 'reference'}.

    Raises
    ------
    ValueError
        If num_lanes_per_direction is not 1-4 (or more, clamped to the
        4-or-more row).
    """
    n = int(num_lanes_per_direction)
    key = min(n, 4)
    if key < 1:
        raise ValueError(f"num_lanes_per_direction must be >= 1, got {n}")
    lo, hi = _DL_TABLE[key]
    return {
        "num_lanes_per_direction": n, "dl_min_pct": lo, "dl_max_pct": hi,
        "reference": "AASHTO 1993 Guide, Section 2.1.2 (pdf_page_index 98, printed II-9)",
    }


def directional_distribution_default() -> dict:
    """Default directional distribution factor DD (Section 2.1.2).

    DD is generally 0.5 (50%) for most roadways but may range 0.3 to 0.7
    depending on which direction carries more/heavier loaded trucks.

    Returns
    -------
    dict
        {'dd_default', 'dd_min', 'dd_max', 'reference'}.
    """
    return {
        "dd_default": 0.5, "dd_min": 0.3, "dd_max": 0.7,
        "reference": "AASHTO 1993 Guide, Section 2.1.2 (pdf_page_index 98, printed II-9)",
    }


# ============================================================================
# Figure 2.5: Structural layer coefficient a1 for dense-graded asphalt
# concrete surface course vs elastic (resilient) modulus EAC at 68F.
# CHART READ-OFF (no printed closed-form equation): digitized at dpi 150/240
# (pdf_page_index 107, printed II-18). Anchor points from the printed curve
# (solid to about EAC 450,000 psi; dashed beyond to the 500,000 psi edge;
# II-17: "Caution is recommended for modulus values above 450,000 psi").
# Re-read 2026-11-10 (review pave-11) from a 400-dpi render, gridline-
# calibrated: the curve begins on the a1 = 0.20 line at about 106,000 psi
# (was taken as 100,000) and reads 0.252 at 150,000 (was 0.26); the other
# anchors agree with the trace within 0.004.
# ============================================================================

_A1_EAC = [106000, 150000, 200000, 250000, 300000, 350000, 400000, 450000,
          500000]
_A1_VAL = [0.20, 0.252, 0.30, 0.335, 0.365, 0.39, 0.42, 0.44, 0.465]


def layer_coefficient_a1_asphalt(eac_psi) -> dict:
    """Structural layer coefficient a1 of a dense-graded asphalt concrete
    surface course from its elastic modulus EAC at 68 F, AASHTO 1993
    Figure 2.5 (pdf_page_index 107, printed II-18); returns a1 (per inch).

    Chart-read-off (interpolated), NOT a printed closed-form equation.
    Digitized anchor points (EAC psi -> a1): 106000->0.20, 150000->0.252,
    200000->0.30, 250000->0.335, 300000->0.365, 350000->0.39, 400000->0.42,
    450000->0.44, 500000->0.465. The printed curve is drawn from about
    106,000 psi (a1 0.20) to the chart's 500,000 psi edge, dashed past
    about 450,000 psi; II-17: "Caution is recommended for modulus values
    above 450,000 psi".

    Parameters
    ----------
    eac_psi : float
        Asphalt concrete elastic (resilient) modulus at 68 F, psi. The
        printed curve begins at about 106,000 psi (a1 0.20): below that the
        lookup refuses. Above 450,000 psi the curve is dashed (noted);
        above 500,000 psi, the chart's edge, a1 is held at its 500,000 psi
        value, with a note and an ``out_of_range`` key. Holding is on the
        safe side (a1 rises with EAC, so a stiffer mix gets no more credit)
        and follows II-17: "Caution is recommended for modulus values above
        450,000 psi".

    Returns
    -------
    dict
        {'eac_psi', 'a1', 'chart_read', 'reference', 'note'?,
        'out_of_range'?}.

    Raises
    ------
    ValueError
        If eac_psi is below about 106,000 psi, where Figure 2.5's curve
        begins.
    """
    if eac_psi is None or eac_psi < _A1_EAC[0]:
        raise ValueError(
            f"EAC {eac_psi} psi is below where Figure 2.5's curve begins: "
            "the chart draws a1 for EAC from about 106,000 psi (a1 0.20) to "
            "500,000 psi (printed II-18); it gives no a1 below that.")
    a1 = _linterp(eac_psi, _A1_EAC, _A1_VAL)
    out = {
        "eac_psi": eac_psi, "a1": round(a1, 3), "chart_read": True,
        "reference": "AASHTO 1993 Guide, Figure 2.5 (pdf_page_index 107, printed II-18)",
    }
    if eac_psi > 450000:
        out["note"] = ("EAC > 450,000 psi: the curve is dashed here, and "
                       "II-17 says 'Caution is recommended for modulus "
                       "values above 450,000 psi' (stiffer mixes are more "
                       "susceptible to thermal and fatigue cracking).")
    if eac_psi > _A1_EAC[-1]:
        out["note"] += (" EAC is past the chart's 500,000 psi edge; a1 is "
                        "held at its 500,000 psi value, on the safe side.")
        out["out_of_range"] = (
            f"eac_psi = {eac_psi:,.0f} is above 500,000 psi, the right edge "
            "of Figure 2.5 (printed II-18).")
    return out


# ============================================================================
# Figures 2.8 and 2.9: structural layer coefficient a2 for cement-treated
# and bituminous-treated bases. Each chart is a set of parallel vertical
# scales (a2; the material property; modulus): a2 is read straight across
# from the property's tick. CHART READ-OFF (REF-58, from the GM-298 read of
# 2026-10-31): the labelled ticks of each property scale were located on
# the scanned page and read across to the a2 scale, linearly between a2
# ticks; between property ticks a2 is linear. The dashed lines printed on
# each chart (Fig. 2.8: 0.10 / 0.16 / 0.22 / 0.28; Fig. 2.9: 0.10 / 0.20 /
# 0.30) mark a2 values, not ticks of the property scale.
#
# Outside the labelled ticks the scale is not read (ValueError): below the
# lowest, and (REF-76) above the top one, where a2 used to be held at the
# top tick's value with a note. The guide's text (II-22) gives no rule
# beyond the scales.
# ============================================================================

# Figure 2.8 (pdf_page_index 112, printed II-23): 7-day UCS (psi) -> a2.
_A2_CEMENT_SCALE = ((200, 0.126), (400, 0.155), (600, 0.188), (800, 0.220),
                    (1000, 0.250))
# Figure 2.9 (pdf_page_index 113, printed II-24): Marshall stability (lb) -> a2.
_A2_BITUMINOUS_SCALE = ((200, 0.126), (400, 0.161), (600, 0.180),
                        (800, 0.204), (1000, 0.230), (1200, 0.250),
                        (1400, 0.275), (1600, 0.300), (1800, 0.320))


def _a2_across(value, scale, what, unit):
    lo, hi = scale[0][0], scale[-1][0]
    if value is None or value < lo:
        raise ValueError(
            f"{what} {value} {unit} is below the lowest labelled tick of the "
            f"printed scale ({lo} {unit}); give the layer coefficient "
            "directly."
        )
    if value > hi:
        raise ValueError(
            f"{what} {value} {unit} is above the top labelled tick of the "
            f"printed scale ({hi} {unit}); the chart gives no a2 there and "
            "the guide's text no rule. Give the layer coefficient directly."
        )
    for (x0, a0), (x1, a1) in zip(scale, scale[1:]):
        if x0 <= value <= x1:
            return a0 + (a1 - a0) * (value - x0) / (x1 - x0), None
    return scale[-1][1], None  # pragma: no cover


def layer_coefficient_a2_cement_treated(ucs_7day_psi) -> dict:
    """Cement-treated base layer coefficient a2 vs 7-day UCS (Figure 2.8, chart).

    Read straight across from the UCS scale's labelled ticks (psi -> a2):
    200 -> 0.126, 400 -> 0.155, 600 -> 0.188, 800 -> 0.220, 1000 -> 0.250;
    linear between ticks. The chart's modulus scale is not read here.

    Parameters
    ----------
    ucs_7day_psi : float
        7-day unconfined compressive strength of the cement-treated base
        (ASTM D 1633), psi. The printed scale's ticks run 200-1000 psi.

    Returns
    -------
    dict
        {'ucs_7day_psi', 'a2', 'chart_read', 'reference'}.

    Raises
    ------
    ValueError
        If the UCS is outside the scale's labelled ticks, 200-1000 psi
        (printed II-23). Above 1000 psi a2 used to be held at 0.250 with
        a note (REF-76).
    """
    a2, note = _a2_across(ucs_7day_psi, _A2_CEMENT_SCALE, "7-day UCS", "psi")
    out = {
        "ucs_7day_psi": ucs_7day_psi, "a2": round(a2, 3), "chart_read": True,
        "reference": "AASHTO 1993 Guide, Figure 2.8 (pdf_page_index 112, printed II-23)",
    }
    if note:
        out["note"] = note
    return out


def layer_coefficient_a2_bituminous_treated(marshall_stability_lb) -> dict:
    """Bituminous-treated base layer coefficient a2 vs Marshall stability (Fig. 2.9, chart).

    Read straight across from the Marshall stability scale's labelled
    ticks (lb -> a2): 200 -> 0.126, 400 -> 0.161, 600 -> 0.180,
    800 -> 0.204, 1000 -> 0.230, 1200 -> 0.250, 1400 -> 0.275,
    1600 -> 0.300, 1800 -> 0.320; linear between ticks. The chart's
    modulus scale is not read here.

    Parameters
    ----------
    marshall_stability_lb : float
        Marshall stability (AASHTO T 245 / ASTM D 1559), lb. The printed
        scale's labelled ticks used run 200-1800 lb.

    Returns
    -------
    dict
        {'marshall_stability_lb', 'a2', 'chart_read', 'reference'}.

    Raises
    ------
    ValueError
        If the stability is outside the labelled ticks used, 200-1800 lb
        (printed II-24). Above 1800 lb a2 used to be held at 0.320 with a
        note (REF-76).
    """
    a2, note = _a2_across(marshall_stability_lb, _A2_BITUMINOUS_SCALE,
                          "Marshall stability", "lb")
    out = {
        "marshall_stability_lb": marshall_stability_lb, "a2": round(a2, 3),
        "chart_read": True,
        "reference": "AASHTO 1993 Guide, Figure 2.9 (pdf_page_index 113, printed II-24)",
    }
    if note:
        out["note"] = note
    return out


# ============================================================================
# Table 2.3: Typical k1, k2 for Unbound Base and Subbase Materials
# (MR = k1*theta^k2); pdf_page_index 109, printed II-20
# ============================================================================

_TABLE_2_3 = {
    "base": {"dry": (6000, 10000), "damp": (4000, 6000), "wet": (2000, 4000)},
    "subbase": {"dry": (6000, 8000), "damp": (4000, 6000), "wet": (1500, 4000)},
}
_TABLE_2_3_K2 = {"base": (0.5, 0.7), "subbase": (0.4, 0.6)}


def unbound_k1_k2(layer, moisture_condition) -> dict:
    """Typical k1/k2 ranges for unbound base/subbase MR = k1*theta^k2 (Table 2.3).

    Parameters
    ----------
    layer : str
        'base' or 'subbase'.
    moisture_condition : str
        'dry', 'damp', or 'wet'.

    Returns
    -------
    dict
        {'layer', 'moisture_condition', 'k1_min', 'k1_max', 'k2_min',
         'k2_max', 'reference'}.

    Raises
    ------
    ValueError
        If layer or moisture_condition is unrecognized.
    """
    lk = str(layer).strip().lower()
    if lk not in _TABLE_2_3:
        raise ValueError(f"layer must be 'base' or 'subbase', got '{layer}'")
    mk = str(moisture_condition).strip().lower()
    if mk not in _TABLE_2_3[lk]:
        raise ValueError(
            f"moisture_condition must be 'dry', 'damp', or 'wet', got "
            f"'{moisture_condition}'"
        )
    k1_lo, k1_hi = _TABLE_2_3[lk][mk]
    k2_lo, k2_hi = _TABLE_2_3_K2[lk]
    return {
        "layer": lk, "moisture_condition": mk,
        "k1_min": k1_lo, "k1_max": k1_hi, "k2_min": k2_lo, "k2_max": k2_hi,
        "reference": "AASHTO 1993 Guide, Table 2.3 (pdf_page_index 109, printed II-20)",
    }


# ============================================================================
# Table 2.4: Recommended mi Values for Modifying Structural Layer
# Coefficients of Untreated Base/Subbase in Flexible Pavements
# (pdf_page_index 114, printed II-25)
# ============================================================================

_SATURATION_COLS = ["<1%", "1-5%", "5-25%", ">25%"]

# Each cell as printed, "high-low" (e.g. "1.40-1.35"): (high, low).
_TABLE_2_4 = {
    "excellent": [(1.40, 1.35), (1.35, 1.30), (1.30, 1.20), (1.20, 1.20)],
    "good": [(1.35, 1.25), (1.25, 1.15), (1.15, 1.00), (1.00, 1.00)],
    "fair": [(1.25, 1.15), (1.15, 1.05), (1.00, 0.80), (0.80, 0.80)],
    "poor": [(1.15, 1.05), (1.05, 0.80), (0.80, 0.60), (0.60, 0.60)],
    "very_poor": [(1.05, 0.95), (0.95, 0.75), (0.75, 0.40), (0.40, 0.40)],
}


def drainage_mi_flexible(quality, pct_saturation_time) -> dict:
    """Recommended mi values for modifying the layer coefficients of
    untreated base and subbase in flexible pavements, AASHTO 1993 Table 2.4
    (pdf_page_index 114, printed II-25); returns the printed range as mi_min and
    mi_max (dimensionless).

    Modifies the base/subbase layer coefficients in the SN equation
    (SN = a1*D1 + a2*D2*m2 + a3*D3*m3). AASHO Road Test conditions
    correspond to mi=1.0 (quality 'fair').

    Parameters
    ----------
    quality : str
        'excellent', 'good', 'fair', 'poor', or 'very_poor' (also accepts
        'very poor' with a space).
    pct_saturation_time : str
        '<1%', '1-5%', '5-25%', or '>25%' (percent of time the pavement
        structure is exposed to moisture levels approaching saturation).

    Returns
    -------
    dict
        {'quality', 'pct_saturation_time', 'mi_min', 'mi_max', 'reference'}.

    Raises
    ------
    ValueError
        If quality or pct_saturation_time is unrecognized.
    """
    qk = str(quality).strip().lower().replace(" ", "_")
    if qk not in _TABLE_2_4:
        raise ValueError(
            f"Unknown quality '{quality}'. Use: {', '.join(_TABLE_2_4)}"
        )
    if pct_saturation_time not in _SATURATION_COLS:
        raise ValueError(
            f"pct_saturation_time must be one of {_SATURATION_COLS}, got "
            f"'{pct_saturation_time}'"
        )
    idx = _SATURATION_COLS.index(pct_saturation_time)
    hi, lo = _TABLE_2_4[qk][idx]
    return {
        "quality": qk, "pct_saturation_time": pct_saturation_time,
        "mi_min": lo, "mi_max": hi,
        "reference": "AASHTO 1993 Guide, Table 2.4 (pdf_page_index 114, printed II-25)",
    }


# ============================================================================
# Table 2.5: Recommended Values of Drainage Coefficient Cd, Rigid Pavements
# (pdf_page_index 115, printed II-26)
# ============================================================================

# Each cell as printed, "high-low" (e.g. "1.25-1.20"): (high, low).
_TABLE_2_5 = {
    "excellent": [(1.25, 1.20), (1.20, 1.15), (1.15, 1.10), (1.10, 1.10)],
    "good": [(1.20, 1.15), (1.15, 1.10), (1.10, 1.00), (1.00, 1.00)],
    "fair": [(1.15, 1.10), (1.10, 1.00), (1.00, 0.90), (0.90, 0.90)],
    "poor": [(1.10, 1.00), (1.00, 0.90), (0.90, 0.80), (0.80, 0.80)],
    "very_poor": [(1.00, 0.90), (0.90, 0.80), (0.80, 0.70), (0.70, 0.70)],
}


def drainage_cd_rigid(quality, pct_saturation_time) -> dict:
    """Recommended values of drainage coefficient Cd for rigid pavement
    design, AASHTO 1993 Table 2.5 (pdf_page_index 115, printed II-26); returns the
    printed range as cd_min and cd_max (dimensionless).

    AASHO Road Test conditions correspond to Cd=1.0 (quality 'fair').

    Parameters
    ----------
    quality : str
        'excellent', 'good', 'fair', 'poor', or 'very_poor'.
    pct_saturation_time : str
        '<1%', '1-5%', '5-25%', or '>25%'.

    Returns
    -------
    dict
        {'quality', 'pct_saturation_time', 'cd_min', 'cd_max', 'reference'}.

    Raises
    ------
    ValueError
        If quality or pct_saturation_time is unrecognized.
    """
    qk = str(quality).strip().lower().replace(" ", "_")
    if qk not in _TABLE_2_5:
        raise ValueError(
            f"Unknown quality '{quality}'. Use: {', '.join(_TABLE_2_5)}"
        )
    if pct_saturation_time not in _SATURATION_COLS:
        raise ValueError(
            f"pct_saturation_time must be one of {_SATURATION_COLS}, got "
            f"'{pct_saturation_time}'"
        )
    idx = _SATURATION_COLS.index(pct_saturation_time)
    hi, lo = _TABLE_2_5[qk][idx]
    return {
        "quality": qk, "pct_saturation_time": pct_saturation_time,
        "cd_min": lo, "cd_max": hi,
        "reference": "AASHTO 1993 Guide, Table 2.5 (pdf_page_index 115, printed II-26)",
    }


def quality_of_drainage_definitions(quality=None) -> dict:
    """Quality-of-drainage definitions by water-removal time (Section 2.4.1).

    Parameters
    ----------
    quality : str, optional
        If given, returns just that row. Otherwise returns all rows.

    Returns
    -------
    dict
        {'rows'} or {'quality', 'water_removed_within'}, plus 'reference'.

    Raises
    ------
    ValueError
        If quality is given but unrecognized.
    """
    rows = [
        {"quality": "excellent", "water_removed_within": "2 hours"},
        {"quality": "good", "water_removed_within": "1 day"},
        {"quality": "fair", "water_removed_within": "1 week"},
        {"quality": "poor", "water_removed_within": "1 month"},
        {"quality": "very_poor", "water_removed_within": "water will not drain"},
    ]
    ref = "AASHTO 1993 Guide, Section 2.4.1 (pdf_page_index 111, printed II-22)"
    if quality is None:
        return {"rows": rows, "note": "AASHO Road Test drainage = 'fair'.",
                "reference": ref}
    qk = str(quality).strip().lower().replace(" ", "_")
    match = next((r for r in rows if r["quality"] == qk), None)
    if match is None:
        raise ValueError(
            f"Unknown quality '{quality}'. Use: excellent, good, fair, "
            "poor, very_poor"
        )
    out = dict(match)
    out["reference"] = ref
    return out


# ============================================================================
# Table 2.6: Recommended Load Transfer Coefficient J for Various Pavement
# Types and Design Conditions (pdf_page_index 115, printed II-26)
# ============================================================================

_TABLE_2_6 = {
    "plain_jointed_jrcp": {
        ("asphalt", True): (3.2, 3.2),
        ("asphalt", False): (3.8, 4.4),
        ("tied_pcc", True): (2.5, 3.1),
        ("tied_pcc", False): (3.6, 4.2),
    },
    "crcp": {
        ("asphalt", True): (2.9, 3.2),
        ("asphalt", False): None,
        ("tied_pcc", True): (2.3, 2.9),
        ("tied_pcc", False): None,
    },
}


def load_transfer_coefficient_j(pavement_type, shoulder_type,
                                load_transfer_devices) -> dict:
    """Recommended load transfer coefficient J (Table 2.6).

    AASHO Road Test "protected corner" (dowelled JCP/JRCP, no tied
    shoulder) J = 3.2.

    Parameters
    ----------
    pavement_type : str
        'plain_jointed_jrcp' (plain jointed or jointed reinforced concrete)
        or 'crcp' (continuously reinforced).
    shoulder_type : str
        'asphalt' or 'tied_pcc'.
    load_transfer_devices : bool
        True if dowels/load-transfer devices are present at the joints
        (for CRCP, this represents aggregate interlock capability at
        future transverse cracks).

    Returns
    -------
    dict
        {'pavement_type', 'shoulder_type', 'load_transfer_devices',
         'j_min', 'j_max', 'reference'}.

    Raises
    ------
    ValueError
        If the combination is unrecognized or not applicable (N/A in the
        printed table, e.g. CRCP without load transfer devices).
    """
    pk = str(pavement_type).strip().lower()
    if pk not in _TABLE_2_6:
        raise ValueError(
            f"pavement_type must be 'plain_jointed_jrcp' or 'crcp', got "
            f"'{pavement_type}'"
        )
    sk = str(shoulder_type).strip().lower()
    if sk not in ("asphalt", "tied_pcc"):
        raise ValueError(
            f"shoulder_type must be 'asphalt' or 'tied_pcc', got '{shoulder_type}'"
        )
    cell = _TABLE_2_6[pk].get((sk, bool(load_transfer_devices)))
    if cell is None:
        raise ValueError(
            f"J is not applicable (N/A) for pavement_type='{pk}', "
            f"shoulder_type='{sk}', load_transfer_devices="
            f"{load_transfer_devices} per Table 2.6."
        )
    lo, hi = cell
    return {
        "pavement_type": pk, "shoulder_type": sk,
        "load_transfer_devices": bool(load_transfer_devices),
        "j_min": lo, "j_max": hi,
        "reference": "AASHTO 1993 Guide, Table 2.6 (pdf_page_index 115, printed II-26)",
    }


# ============================================================================
# Minimum practical layer thicknesses by traffic level
# (Section 3.1.4; pdf_page_index 124, printed II-35)
# ============================================================================

_MIN_THICKNESS = [
    # (esal_upper_bound or None for open-ended, ac_min_in, agg_base_min_in, ac_note)
    (50000, 1.0, 4, "or surface treatment"),
    (150000, 2.0, 4, None),
    (500000, 2.5, 4, None),
    (2000000, 3.0, 6, None),
    (7000000, 3.5, 6, None),
    (None, 4.0, 6, None),
]


def minimum_layer_thickness(esal) -> dict:
    """Minimum practical asphalt concrete and aggregate base thickness (Section 3.1.4).

    Parameters
    ----------
    esal : float
        Design traffic, 18-kip ESAL over the performance period, > 0.

    Returns
    -------
    dict
        {'esal', 'asphalt_concrete_min_in', 'aggregate_base_min_in',
         'note'?, 'reference'}.

    Raises
    ------
    ValueError
        If esal <= 0.
    """
    if esal <= 0:
        raise ValueError(f"esal must be > 0, got {esal}")
    for upper, ac_min, base_min, note in _MIN_THICKNESS:
        if upper is None or esal <= upper:
            out = {
                "esal": esal, "asphalt_concrete_min_in": ac_min,
                "aggregate_base_min_in": base_min,
                "reference": ("AASHTO 1993 Guide, Section 3.1.4 "
                             "(pdf_page_index 124, printed II-35)"),
            }
            if note:
                out["note"] = note
            return out
    raise AssertionError("unreachable")  # pragma: no cover


# ============================================================================
# Appendix D: Axle Load Equivalency Factors (ESAL), single and tandem axles.
#
# These four lookups are kept for callers that name them; since REF-12 each
# one reads the full printed Appendix D grid through
# ``lef.load_equivalency_factor`` (Tables D.1-D.18: flexible SN = 1-6, rigid
# D = 6-14 in, each at pt = 2.0, 2.5 and 3.0; table layout and transcription
# notes in lef.py's module docstring). Before REF-12 they held only the
# SN = 5 / D = 9 in, pt = 2.5 columns (Tables D.4, D.5, D.13, D.14) and
# refused anything else; those columns are the same numbers lef.py holds, so
# the SN = 5 / D = 9 in, pt = 2.5 answers are unchanged to the digit
# (tests/test_aashto_1993_esal.py pins them). Triple axles: call
# ``lef.load_equivalency_factor(..., axle_config="triple")``.
# ============================================================================


def _esal_from_lef(pavement_type, axle_config, axle_load_kips, sn, d_in, pt,
                   column_key):
    """Read Appendix D through lef.py and return this module's keys.

    lef.py's ValueError (pt not 2.0/2.5/3.0, a load or SN/D <= 0 or
    outside the printed table) passes through unchanged.
    """
    from geotech_references.aashto_1993.lef import load_equivalency_factor
    kw = {"sn": sn} if pavement_type == "flexible" else {"d_in": d_in}
    r = load_equivalency_factor(pavement_type, axle_config, axle_load_kips,
                                pt=pt, **kw)
    out = {
        "axle_load_kips": axle_load_kips,
        column_key: r[column_key],
        "pt": r["pt"],
        "lef": r["lef"],
        "table": r["table"],
        "reference": r["reference"],
    }
    if "note" in r:
        out["note"] = r["note"]
    return out


def esal_flexible_single_axle(axle_load_kips, sn=5.0, pt=2.5) -> dict:
    """Load equivalency factor, flexible pavement, single axle (Tables D.1, D.4, D.7).

    Bilinear interpolation over the printed Appendix D table for the given
    pt: Table D.1 (pt = 2.0, pdf_page_index 362, printed D-3), D.4 (pt = 2.5,
    pdf_page_index 365, printed D-6) or D.7 (pt = 3.0, pdf_page_index 368, printed D-9);
    see ``lef.load_equivalency_factor``.

    Parameters
    ----------
    axle_load_kips : float
        Single axle load, kips, > 0. Printed rows are 2-50 kips; a load
        outside them is refused (REF-76).
    sn : float, optional
        Pavement structural number, > 0. Printed columns are SN = 1-6,
        interpolated linearly between them; outside 1-6 it is refused.
        Default 5.0.
    pt : float, optional
        Terminal serviceability: exactly 2.0, 2.5 or 3.0, the values
        Appendix D prints. Default 2.5.

    Returns
    -------
    dict
        {'axle_load_kips', 'sn', 'pt', 'lef', 'table', 'reference'}.
        'table' is the printed table number (e.g. 'Table D.4').

    Raises
    ------
    ValueError
        As ``lef.load_equivalency_factor``: pt not 2.0/2.5/3.0, or a load
        or SN <= 0 or outside the printed table.
    """
    return _esal_from_lef("flexible", "single", axle_load_kips, sn, None,
                          pt, "sn")


def esal_flexible_tandem_axle(axle_load_kips, sn=5.0, pt=2.5) -> dict:
    """Load equivalency factor, flexible pavement, tandem axle (Tables D.2, D.5, D.8).

    Table D.2 (pt = 2.0, pdf_page_index 363, printed D-4), D.5 (pt = 2.5,
    pdf_page_index 366, printed D-7) or D.8 (pt = 3.0, pdf_page_index 369, printed
    D-10); see ``esal_flexible_single_axle``.

    Parameters
    ----------
    axle_load_kips : float
        Tandem axle group load, kips, > 0. Printed rows are 2-90 kips; a
        load outside them is refused (REF-76).
    sn : float, optional
        Pavement structural number; printed SN = 1-6, interpolated,
        refused outside. Default 5.0.
    pt : float, optional
        Exactly 2.0, 2.5 or 3.0. Default 2.5.

    Returns
    -------
    dict
        {'axle_load_kips', 'sn', 'pt', 'lef', 'table', 'reference',
         'note'?}.

    Raises
    ------
    ValueError
        As ``lef.load_equivalency_factor``.
    """
    return _esal_from_lef("flexible", "tandem", axle_load_kips, sn, None,
                          pt, "sn")


def esal_rigid_single_axle(axle_load_kips, d_in=9.0, pt=2.5) -> dict:
    """Load equivalency factor, rigid pavement, single axle (Tables D.10, D.13, D.16).

    Table D.10 (pt = 2.0, pdf_page_index 371, printed D-12), D.13 (pt = 2.5,
    pdf_page_index 374, printed D-15) or D.16 (pt = 3.0, pdf_page_index 377, printed
    D-18); see ``lef.load_equivalency_factor``.

    Parameters
    ----------
    axle_load_kips : float
        Single axle load, kips, > 0. Printed rows are 2-50 kips; a load
        outside them is refused (REF-76).
    d_in : float, optional
        Slab thickness, inches, > 0. Printed columns are D = 6-14 in,
        interpolated linearly between them; outside 6-14 it is refused.
        Default 9.0.
    pt : float, optional
        Exactly 2.0, 2.5 or 3.0. Default 2.5.

    Returns
    -------
    dict
        {'axle_load_kips', 'd_in', 'pt', 'lef', 'table', 'reference',
         'note'?}.

    Raises
    ------
    ValueError
        As ``lef.load_equivalency_factor``: pt not 2.0/2.5/3.0, or a load
        or D <= 0 or outside the printed table.
    """
    return _esal_from_lef("rigid", "single", axle_load_kips, None, d_in,
                          pt, "d_in")


def esal_rigid_tandem_axle(axle_load_kips, d_in=9.0, pt=2.5) -> dict:
    """Load equivalency factor, rigid pavement, tandem axle (Tables D.11, D.14, D.17).

    Table D.11 (pt = 2.0, pdf_page_index 372, printed D-13), D.14 (pt = 2.5,
    pdf_page_index 375, printed D-16) or D.17 (pt = 3.0, pdf_page_index 378, printed
    D-19); see ``esal_rigid_single_axle``.

    Parameters
    ----------
    axle_load_kips : float
        Tandem axle group load, kips, > 0. Printed rows are 2-90 kips; a
        load outside them is refused (REF-76).
    d_in : float, optional
        Slab thickness, inches; printed D = 6-14 in, interpolated,
        refused outside. Default 9.0.
    pt : float, optional
        Exactly 2.0, 2.5 or 3.0. Default 2.5.

    Returns
    -------
    dict
        {'axle_load_kips', 'd_in', 'pt', 'lef', 'table', 'reference',
         'note'?}.

    Raises
    ------
    ValueError
        As ``lef.load_equivalency_factor``.
    """
    return _esal_from_lef("rigid", "tandem", axle_load_kips, None, d_in,
                          pt, "d_in")
