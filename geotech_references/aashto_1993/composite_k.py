"""AASHTO Guide for Design of Pavement Structures (1993) - rigid pavement
effective modulus of subgrade reaction procedure.

Part II, Chapter 3, Section 3.2.1 ("Develop Effective Modulus of Subgrade
Reaction"), the Table 3.2 worksheet, Figures 3.3-3.6, and Table 2.7 (Section
2.4.3, "Loss of Support"). This is the full seasonal composite-k procedure
that ``equations.modulus_subgrade_reaction_simple`` explicitly defers to for
the general case (subbase present, and/or a shallow rigid foundation).

All page numbers below are 0-based ``fitz`` page indices into
``docs/aashto1993.pdf``, directly re-verified by rendering during this
build (the printed guide page, e.g. "II-39", is also given). NOTE for
whoever integrates this module: two pre-existing citations elsewhere in
this package appear to be off by a small number of pages -- worth a
follow-up pass (not fixed here per the build brief's "don't touch existing
files" rule):
  - ``figures_catalog.json``'s Figure 3.3 entry says ``pdf_page_index: 127``;
    rendering that index shows Table 3.2 (printed II-38), while Figure 3.3
    itself (printed II-39, confirmed here) is at index 128.
  - ``equations.modulus_subgrade_reaction_simple``'s docstring cites
    "pdf_page 129, printed II-44"; index 129 renders as Figure 3.4 (printed
    II-40), while Section 3.2.2 (printed II-44) is actually at index 133.

Docs/PDF source: fully scanned (no text layer, no vector drawings -- a
single raster image per page), read visually page-by-page. All four
nomographs here (Figures 3.3-3.6) are CHART READ-OFFS (``chart_read: True``
in every returned dict); this is by a wide margin the most complex chart
family in this package (Figure 3.3 alone is a 3-variable, 4-quadrant,
turning-line nomograph). Every function below is built from an EXPLICIT
GRID OF POINTS READ DIRECTLY OFF ITS CHART -- either the guide's own
printed worked examples (exact, called out by value in each docstring) or
direct visual chart reads (multiple points per curve, not single-point
anchors) -- with any smoothing formula required to reproduce every read
point to a stated, tested tolerance (asserted in
``tests/test_aashto_1993_composite_k.py``). Figure 3.3 is read at every
printed curve and Dsb gridline and worked by its own construction (REF-58);
Figure 3.4's rigid-foundation-depth dependence has NO printed numeric
anchor away from its one reference value and relies on lower-confidence
direct chart reads instead (flagged, with a wider stated tolerance, in its
own section docstring) rather than an unanchored fitted exponent.

Chained end-to-end, this module reproduces the guide's own Table 3.3
worked example (composite k -> rigid-foundation correction -> relative
damage per season -> average -> back-solved effective k -> loss-of-support
correction) to within about 4% (see
``tests/test_aashto_1993_composite_k.py``).
"""

import math

from geotech_references._interpolation import _linterp
from geotech_references.aashto_1993.equations import modulus_subgrade_reaction_simple


# ============================================================================
# Table 2.7: Typical Ranges of Loss of Support (LS) Factors for Various
# Types of Materials (Section 2.4.3; pdf_page 116, printed II-27).
# Straight transcription (not a chart read). "E" in the printed table is
# the general symbol for elastic/resilient modulus of the material.
# ============================================================================

_TABLE_2_7 = {
    "cement_treated_granular_base": (1000000, 2000000, 0.0, 1.0),
    "cement_aggregate_mixtures": (500000, 1000000, 0.0, 1.0),
    "asphalt_treated_base": (350000, 1000000, 0.0, 1.0),
    "bituminous_stabilized_mixtures": (40000, 300000, 0.0, 1.0),
    "lime_stabilized": (20000, 70000, 1.0, 3.0),
    "unbound_granular_materials": (15000, 45000, 1.0, 3.0),
    "fine_grained_or_natural_subgrade_materials": (3000, 40000, 2.0, 3.0),
}
_MATERIAL_ORDER = list(_TABLE_2_7)  # preserves the printed table's row order


def loss_of_support_values(material=None) -> dict:
    """Typical loss-of-support (LS) factor ranges by material type (Table 2.7).

    Parameters
    ----------
    material : str, optional
        One of: 'cement_treated_granular_base', 'cement_aggregate_mixtures',
        'asphalt_treated_base', 'bituminous_stabilized_mixtures',
        'lime_stabilized', 'unbound_granular_materials',
        'fine_grained_or_natural_subgrade_materials'. If omitted, returns
        all rows (in the printed table's order).

    Returns
    -------
    dict
        {'material', 'e_min_psi', 'e_max_psi', 'ls_min', 'ls_max',
        'reference'} for a single material, or {'rows', 'reference'} (each
        row the same shape) for the full table.

    Raises
    ------
    ValueError
        If material is given but unrecognized.
    """
    ref = "AASHTO 1993 Guide, Table 2.7 (pdf_page 116, printed II-27)"
    if material is None:
        rows = []
        for name in _MATERIAL_ORDER:
            e_min, e_max, ls_min, ls_max = _TABLE_2_7[name]
            rows.append({
                "material": name, "e_min_psi": e_min, "e_max_psi": e_max,
                "ls_min": ls_min, "ls_max": ls_max,
            })
        return {"rows": rows, "reference": ref}
    key = str(material).strip().lower().replace(" ", "_")
    if key not in _TABLE_2_7:
        raise ValueError(
            f"Unknown material '{material}'. Use one of: "
            f"{', '.join(_MATERIAL_ORDER)}"
        )
    e_min, e_max, ls_min, ls_max = _TABLE_2_7[key]
    return {
        "material": key, "e_min_psi": e_min, "e_max_psi": e_max,
        "ls_min": ls_min, "ls_max": ls_max, "reference": ref,
    }


# ============================================================================
# Figure 3.3: Chart for Estimating Composite Modulus of Subgrade Reaction,
# k(infinity), Assuming a Semi-Infinite Subgrade Depth
# (pdf_page 128, printed II-39). CHART READ-OFF.
#
# A 3-variable (Dsb, Esb, MR), 4-quadrant nomograph with a turning line:
# up from Dsb to the Esb curve and across; up from the same Dsb to the MR
# curve in the lower quadrant, across to the turning line, then vertically
# to meet the Esb height on a k_inf diagonal. The chart is read here and
# its own construction followed, not fitted with a formula.
#
# How it was read (REF-58, from the GM-298 read of 2026-10-31): the scanned
# page rendered at its scan resolution (about 305 dpi). Every printed
# curve's height (scan pixels, downward) was measured at each even Dsb
# gridline (6-18 in) by fitting the curve's ink locally; the eleven k_inf
# diagonals (50-2000 pci) and the turning line by where they cross the
# gridline rows. Then
#
#   y_E = height of the Esb curve at Dsb    (upper quadrant)
#   y_M = height of the MR curve at Dsb     (lower quadrant)
#   x_t = y_M + c_t(y_M)                    (turning line, x - y = c_t)
#   c   = x_t - y_E                         (the diagonal through (x_t, y_E))
#   k_inf from c, log-interpolated between the drawn diagonals.
#
# Esb and MR are interpolated between curves in log(Esb), log(MR); Dsb
# linearly between gridlines. Checked against the five printed anchors,
# all at Dsb = 6 in: the figure's own example (Esb 20,000, MR 7,000 -> 400;
# read 391) and the four Table 3.3 rows (pdf_page 132, printed II-43:
# 1,100 -> 1,085; 160 -> 154; 230 -> 230; 410 -> 391), within 5 %, the
# spread of the guide's own two reads of one point (400 and 410).
#
# Outside the printed curves: Dsb below 6 in, Esb below 15,000 psi or MR
# below 1,000 psi raise ValueError (reading off the lowest curve would
# overstate k); Dsb above 18 in, Esb above 1,000,000 psi or MR above
# 20,000 psi use the nearest printed curve with a note (understates k); a
# construction landing beyond the 2,000 pci diagonal is held at 2,000 pci
# with a note.
# ============================================================================

# Upper quadrant: heights of the nine Esb curves at each even Dsb gridline,
# in _COMPK_ESB order.
_COMPK_ESB = (1_000_000, 600_000, 400_000, 200_000, 100_000, 75_000, 50_000,
              30_000, 15_000)
_COMPK_UPPER = {
    18: (945.5, 974.2, 999.2, 1034.7, 1074.7, 1090.8, 1112.1, 1141.7, 1180.3),
    16: (990.7, 1018.2, 1040.3, 1072.9, 1112.6, 1127.1, 1146.9, 1176.5, 1212.3),
    14: (1037.1, 1062.4, 1083.1, 1114.5, 1153.7, 1166.1, 1185.5, 1211.9, 1246.0),
    12: (1092.4, 1115.3, 1134.5, 1164.3, 1200.4, 1212.1, 1230.5, 1254.0, 1286.4),
    10: (1155.9, 1177.8, 1194.6, 1222.9, 1254.7, 1265.1, 1281.4, 1304.6, 1333.1),
    8: (1233.2, 1251.9, 1266.8, 1293.1, 1319.0, 1330.3, 1344.5, 1364.5, 1390.3),
    6: (1328.5, 1342.8, 1355.8, 1377.1, 1397.1, 1407.6, 1420.4, 1434.5, 1459.5),
}
# Lower quadrant: heights of the nine MR curves, in _COMPK_MR order. (Dsb
# 8 in, MR 10,000: the curve is not resolved at that gridline; 2203.5 is
# set from its neighbours' steps between Dsb 10, 8 and 6.)
_COMPK_MR = (1000, 2000, 3000, 5000, 7000, 10_000, 12_000, 16_000, 20_000)
_COMPK_LOWER = {
    18: (1747.7, 1832.0, 1882.5, 1942.3, 1986.8, 2030.3, 2052.6, 2087.3, 2114.2),
    16: (1765.5, 1855.1, 1906.1, 1968.8, 2012.2, 2055.2, 2079.2, 2114.0, 2141.8),
    14: (1785.8, 1878.9, 1931.1, 1993.3, 2039.8, 2081.2, 2108.6, 2141.8, 2173.0),
    12: (1811.5, 1907.2, 1959.3, 2025.2, 2071.8, 2115.3, 2141.5, 2178.6, 2207.7),
    10: (1843.0, 1939.3, 1992.9, 2062.7, 2107.5, 2156.6, 2183.0, 2218.0, 2251.0),
    8: (1879.6, 1981.2, 2034.1, 2110.0, 2152.0, 2203.5, 2232.0, 2270.9, 2302.6),
    6: (1926.8, 2032.5, 2087.1, 2167.4, 2214.7, 2269.3, 2296.6, 2335.9, 2370.7),
}
# The k_inf diagonals x - y = c, as drawn, and the turning line
# x - y = -339.5 at y = 1770 rising to -334.5 at y = 2480.
_COMPK_K_LINES = (50, 100, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000)
_COMPK_K_C = (69.5, 190.5, 312.0, 380.5, 433.5, 480.5, 515.5, 557.0, 600.5,
              673.0, 724.5)

_COMPK_ESB_RANGE = (15000.0, 1000000.0)
_COMPK_MR_RANGE = (1000.0, 20000.0)
_COMPK_DSB_RANGE = (6.0, 18.0)
_FIG33_REF = "AASHTO 1993 Guide, Figure 3.3 (pdf_page 128, printed II-39)"


def _compk_turning_c(y):
    return -339.5 + (y - 1770.0) * (5.0 / 710.0)


def _compk_curve_height(table, labels, dsb, value):
    pairs = sorted(zip((math.log10(v) for v in labels), range(len(labels))))
    logs = [p[0] for p in pairs]
    order = [p[1] for p in pairs]
    ds = sorted(table)
    heights = [_linterp(math.log10(value), logs, [table[d][i] for i in order])
               for d in ds]
    return _linterp(dsb, [float(d) for d in ds], heights)


def composite_k_subbase(mr_psi, esb_psi, dsb_in) -> dict:
    """Composite modulus of subgrade reaction k_inf, semi-infinite subgrade
    depth, read off Figure 3.3 (pdf_page 128, printed II-39) by the chart's
    own construction (see the section note above for how it was read).

    Checked against the guide's five printed reads, all at Dsb = 6 in
    (the figure's example Esb 20,000 / MR 7,000 -> 400 pci, read 391; the
    Table 3.3 rows 1,100 / 160 / 230 / 410 pci, read 1,085 / 154 / 230 /
    391), within 5 %.

    Parameters
    ----------
    mr_psi : float
        Roadbed soil resilient modulus for the season, psi. Printed curves
        1,000-20,000 psi.
    esb_psi : float
        Subbase elastic (resilient) modulus for the season, psi. Printed
        curves 15,000-1,000,000 psi.
    dsb_in : float
        Subbase thickness, inches. Printed scale 6-18 in.

    Returns
    -------
    dict
        {'mr_psi', 'esb_psi', 'dsb_in', 'k_inf_pci', 'chart_read',
        'method', 'reference', 'note'?}.

    Raises
    ------
    ValueError
        If an input is <= 0, or Dsb is below 6 in, Esb below 15,000 psi
        or MR below 1,000 psi (below the printed curves; reading off the
        lowest curve would overstate k). Above the printed curves the
        nearest curve is used with a note (understates k).
    """
    for name, val in (("mr_psi", mr_psi), ("esb_psi", esb_psi),
                      ("dsb_in", dsb_in)):
        if val is None or val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    if dsb_in < _COMPK_DSB_RANGE[0]:
        raise ValueError(
            f"Subbase thickness {dsb_in} in is below Figure 3.3's printed "
            f"Dsb scale ({_COMPK_DSB_RANGE[0]:g}-{_COMPK_DSB_RANGE[1]:g} in); "
            "read the chart and give k directly, or use the roadbed alone "
            "(equations.modulus_subgrade_reaction_simple)."
        )
    if esb_psi < _COMPK_ESB_RANGE[0]:
        raise ValueError(
            f"Subbase modulus {esb_psi} psi is below Figure 3.3's lowest "
            f"printed curve ({_COMPK_ESB_RANGE[0]:,.0f} psi); give k directly "
            "or use the roadbed alone."
        )
    if mr_psi < _COMPK_MR_RANGE[0]:
        raise ValueError(
            f"Roadbed modulus {mr_psi} psi is below Figure 3.3's lowest "
            f"printed curve ({_COMPK_MR_RANGE[0]:,.0f} psi); give k directly."
        )
    notes = []
    dsb = dsb_in
    if dsb > _COMPK_DSB_RANGE[1]:
        dsb = _COMPK_DSB_RANGE[1]
        notes.append(f"Dsb {dsb_in} in is above the printed scale; the "
                     f"{_COMPK_DSB_RANGE[1]:g}-in gridline was used "
                     "(understates k).")
    esb = esb_psi
    if esb > _COMPK_ESB_RANGE[1]:
        esb = _COMPK_ESB_RANGE[1]
        notes.append(f"Esb {esb_psi:,.0f} psi is above the highest printed "
                     "curve; the 1,000,000-psi curve was used (understates k).")
    mr = mr_psi
    if mr > _COMPK_MR_RANGE[1]:
        mr = _COMPK_MR_RANGE[1]
        notes.append(f"MR {mr_psi:,.0f} psi is above the highest printed "
                     "curve; the 20,000-psi curve was used (understates k).")

    y_e = _compk_curve_height(_COMPK_UPPER, _COMPK_ESB, dsb, esb)
    y_m = _compk_curve_height(_COMPK_LOWER, _COMPK_MR, dsb, mr)
    c = y_m + _compk_turning_c(y_m) - y_e
    if c > _COMPK_K_C[-1]:
        k_inf = float(_COMPK_K_LINES[-1])
        notes.append("The construction lands beyond the highest drawn "
                     "diagonal; k_inf held at 2,000 pci.")
    else:
        log_k = _linterp(c, list(_COMPK_K_C),
                         [math.log10(k) for k in _COMPK_K_LINES])
        k_inf = 10 ** log_k

    out = {
        "mr_psi": mr_psi, "esb_psi": esb_psi, "dsb_in": dsb_in,
        "k_inf_pci": round(k_inf, 1), "chart_read": True,
        "method": ("Figure 3.3 read off the printed chart (curve heights at "
                   "the Dsb gridlines, the turning line and the k diagonals; "
                   "the chart's own construction)"),
        "reference": _FIG33_REF,
    }
    if notes:
        out["note"] = " ".join(notes)
    return out


# ============================================================================
# Figure 3.4: Chart to Modify Modulus of Subgrade Reaction to Consider
# Effects of Rigid Foundation Near Surface (within 10 feet)
# (pdf_page 129, printed II-40). CHART READ-OFF.
#
#   k = k_inf * [1 + (mult_at_dsg5(MR) - 1) * dsg_ratio(Dsg)],  Dsg < 10 ft
#   k = k_inf,                                                  Dsg >= 10 ft
#
# The guide's own text (Section 3.2.1 step 5, pdf_page 126, printed II-37)
# instructs disregarding this correction entirely when the depth to a
# rigid foundation Dsg >= 10 ft; implemented here as a hard cutoff (see
# Notes -- this is a deliberate, explicit modeling choice, not an artifact).
#
# mult_at_dsg5(MR) is a DENSITY READ GRID of 4 EXACT printed anchors, not a
# fitted exponent. The guide's Table 3.3 worked example (pdf_page 132,
# printed II-43) holds Dsg=5 ft fixed for all 12 seasonal rows while MR
# varies across 4 distinct values, and prints BOTH the composite k (Figure
# 3.3 column) and the rigid-foundation-corrected k (Figure 3.4 column) for
# each -- giving 4 EXACT (MR, mult=k_rigid/k_inf) pairs at Dsg=5 ft, far
# stronger than a single-point anchor:
#   MR= 2,500 psi -> k_inf=  160, k=  230 pci -> mult=1.4375  (Mar row)
#   MR= 4,000 psi -> k_inf=  230, k=  300 pci -> mult=1.3043  (Apr/May/Nov)
#   MR= 7,000 psi -> k_inf=  410, k=  540 pci -> mult=1.3170  (June-Oct)
#   MR=20,000 psi -> k_inf=1,100, k=1,350 pci -> mult=1.2270  (Jan/Feb/Dec)
# Interpolated log-log (via ``_linterp`` in log-MR/log-mult space) between
# these 4 exact points -- reproduces all four exactly at Dsg=5 ft by
# construction. Note the trend is NOT perfectly monotonic (MR=4,000 dips
# slightly below MR=7,000); this is accepted as-is since both are exact
# printed values, not smoothed away.
#
# dsg_ratio(Dsg) scales that Dsg=5 ft relationship to other Dsg values; NO
# printed anchor exists at Dsg != 5 ft (Table 3.3 only varies MR). This
# is a direct visual chart read (pdf_page 129), not a formula: at a fixed
# MR=4,000 psi reference column, the Dsg=2/5/10 ft curve heights were read
# and ratioed to the Dsg=5 ft height:
#   Dsg= 2 ft -> ratio = 1.406  (chart read, relative to Dsg=5)
#   Dsg= 5 ft -> ratio = 1.000  (reference)
#   Dsg=10 ft -> ratio = 0.691  (chart read; not applied -- see hard cutoff)
# Linearly interpolated between Dsg=2/5/10 (clamped outside). Confidence
# here is lower than the MR read grid (~+/-15-20%, single reference column,
# no independent printed check) -- this is the main accuracy limitation of
# this function.
# ============================================================================

_RIGIDCORR_MR_ANCHORS = [2500.0, 4000.0, 7000.0, 20000.0]
_RIGIDCORR_MULT_AT_DSG5 = [1.4375, 1.3043, 1.3170, 1.2270]

_RIGIDCORR_DSG_VALUES = [2.0, 5.0, 10.0]
_RIGIDCORR_ROW_AT_MR4000 = [2.32, 1.65, 1.14]  # chart read, MR=4,000 psi column
_RIGIDCORR_ROW_REF = 1.65  # = row at (Dsg=5, MR=4,000): dsg_ratio(5) = 1 exactly

_RIGIDCORR_DSG_LIMIT = 10.0


def _loglog_interp(x, xp, fp):
    """Piecewise-linear interpolation in log10-log10 space (clamped)."""
    log_x = math.log10(x)
    log_xp = [math.log10(v) for v in xp]
    log_fp = [math.log10(v) for v in fp]
    return 10 ** _linterp(log_x, log_xp, log_fp)


def k_rigid_foundation_correction(mr_psi, dsg_ft, k_inf_pci) -> dict:
    """Corrected k for a rigid foundation (bedrock) within 10 ft (Figure 3.4).

        k = k_inf * [1 + (mult_at_dsg5(MR) - 1) * dsg_ratio(Dsg)],  Dsg<10 ft
        k = k_inf,                                                  Dsg>=10 ft

    mult_at_dsg5(MR) is a 4-point EXACT read grid (log-log interpolated)
    from the guide's own Table 3.3 worked example, all at Dsg=5 ft; see
    section docstring above. dsg_ratio(Dsg) is a lower-confidence 3-point
    chart read (Dsg=2/5/10 ft) scaling that relationship to other depths.

    Verified against the guide's Table 3.3 rows (all Dsg=5 ft, exact by
    construction): MR=2,500/4,000/7,000/20,000 psi reproduce k=230/300/
    540/1,350 pci exactly from their printed k_inf values.

    Parameters
    ----------
    mr_psi : float
        Roadbed soil resilient modulus, psi, > 0.
    dsg_ft : float
        Depth from the subgrade surface to the rigid foundation (bedrock),
        feet, > 0.
    k_inf_pci : float
        Composite (or simple) modulus of subgrade reaction assuming a
        semi-infinite subgrade depth, pci, > 0 (see
        ``composite_k_subbase`` /
        ``equations.modulus_subgrade_reaction_simple``).

    Returns
    -------
    dict
        {'mr_psi', 'dsg_ft', 'k_inf_pci', 'k_pci', 'chart_read', 'equation',
        'reference', 'note'?}.

    Raises
    ------
    ValueError
        If mr_psi, dsg_ft, or k_inf_pci <= 0.
    """
    if mr_psi <= 0:
        raise ValueError(f"mr_psi must be > 0, got {mr_psi}")
    if dsg_ft <= 0:
        raise ValueError(f"dsg_ft must be > 0, got {dsg_ft}")
    if k_inf_pci <= 0:
        raise ValueError(f"k_inf_pci must be > 0, got {k_inf_pci}")

    out = {
        "mr_psi": mr_psi, "dsg_ft": dsg_ft, "k_inf_pci": k_inf_pci,
        "chart_read": True,
        "reference": "AASHTO 1993 Guide, Figure 3.4 (pdf_page 129, printed II-40)",
    }
    if dsg_ft >= _RIGIDCORR_DSG_LIMIT:
        out["k_pci"] = round(k_inf_pci, 1)
        out["equation"] = "k = k_inf  (Dsg >= 10 ft: guide instructs disregarding this correction)"
        out["note"] = "Depth to rigid foundation >= 10 ft; no correction applied, per the guide."
        return out

    mult_dsg5 = _loglog_interp(mr_psi, _RIGIDCORR_MR_ANCHORS, _RIGIDCORR_MULT_AT_DSG5)
    dsg_ratio = (_linterp(dsg_ft, _RIGIDCORR_DSG_VALUES, _RIGIDCORR_ROW_AT_MR4000)
                / _RIGIDCORR_ROW_REF)
    mult = 1 + (mult_dsg5 - 1) * dsg_ratio
    out["k_pci"] = round(k_inf_pci * mult, 1)
    out["equation"] = ("k = k_inf*[1 + (mult_at_dsg5(MR)-1)*dsg_ratio(Dsg)]; "
                       "mult_at_dsg5: 4 exact Table 3.3 anchors; "
                       "dsg_ratio: chart read, Dsg=2/5/10ft -> 1.406/1.000/0.691")
    return out


# ============================================================================
# Figure 3.5: Chart for Estimating Relative Damage to Rigid Pavements Based
# on Slab Thickness and Underlying Support (pdf_page 130, printed II-41).
# CHART READ-OFF -- NO printed closed-form equation appears on or near this
# page in this guide (only the nomograph itself, with curves for D=6-14 in
# vs composite/corrected k-value, 10-2000 pci).
#
#   u_r = [D^0.75 - 0.39*k^0.25]^3.42 / 100
#
# This is a widely-used closed-form reconstruction of the same chart
# (appearing in later pavement-engineering references reverse-engineering
# this exact AASHTO figure) -- NOT printed anywhere in this scan; it is
# adopted here, in place of digitizing gridline anchor points directly off
# the chart image, because it independently reproduces TWO separate sets
# of chart-based evidence to good tolerance:
#
# (1) ALL FOUR rows of the guide's OWN printed Table 3.3 worked example
#     (pdf_page 132, printed II-43; D=9 in throughout), to within 0.6%:
#   D=9, k=1,350 pci -> u_r=0.35 (printed);  computed 0.3518 (+0.5%)
#   D=9, k=  230 pci -> u_r=0.86 (printed);  computed 0.8593 (-0.1%)
#   D=9, k=  300 pci -> u_r=0.78 (printed);  computed 0.7787 (-0.2%)
#   D=9, k=  540 pci -> u_r=0.60 (printed);  computed 0.6033 (+0.6%)
#   (all four rows are at the SAME D=9 in, so on their own they only
#   validate the k-dependence, not the D-dependence.)
#
# (2) Direct chart reads at D values FAR from the D=9 anchors above
#     (D=6, 7, 8, 10, 12, 14 in), read off Figure 3.5 itself (pdf_page
#     130, printed II-41) at a shared reference k-column (back-solved
#     from the D=9 relationship to k~25 pci, using the guide's own
#     "Projected Slab Thickness" hash-mark labels that identify exactly
#     where each D-curve crosses that column):
#   D= 6 in -> u_r=0.4083 (chart read);  computed 0.4089 (+0.2%)
#   D= 7 in -> u_r=0.7280 (chart read);  computed 0.6768 (-7.0%)
#   D= 8 in -> u_r=0.9502 (chart read);  computed 1.0348 (+8.9%)
#   D=10 in -> u_r=2.3550 (chart read);  computed 2.0610 (-12.5%)
#   D=12 in -> u_r=3.7070 (chart read);  computed 3.5621 (-3.9%)
#   D=14 in -> u_r=5.8250 (chart read);  computed 5.6059 (-3.8%)
#   (u_r values > 1 at this low k are off the guide's practical design
#   range but are valid reads of the printed curves, used here purely to
#   test the formula's D-exponent across the chart's full D=6-14 span.)
# Typical agreement is <8%, worst case 12.5% (D=10) -- this is a
# materially tighter, more broadly-validated fit than digitizing a
# handful of gridline points directly would likely achieve, and it now
# covers the D-dependence (not just the k-dependence) with real chart
# evidence. See ``tests/test_aashto_1993_composite_k.py`` for the
# asserted tolerances on both anchor sets.
# ============================================================================

def relative_damage_rigid(d_in, k_pci) -> dict:
    """Seasonal relative damage u_r for a rigid slab (Figure 3.5).

        u_r = [D^0.75 - 0.39*k^0.25]^3.42 / 100

    Not printed as an equation in this guide (chart read-off only); this
    closed form reproduces all four rows of the guide's own Table 3.3
    worked example (D=9 in, k-dependence) to within 0.6%, AND six direct
    chart reads at D=6-14 in (D-dependence, a shared low-k reference
    column) to within 8% typical / 12.5% worst case -- see section
    docstring above for both anchor sets.

    Parameters
    ----------
    d_in : float
        Projected/trial slab thickness, inches, > 0.
    k_pci : float
        Composite (or rigid-foundation-corrected) modulus of subgrade
        reaction for the season, pci, > 0.

    Returns
    -------
    dict
        {'d_in', 'k_pci', 'u_r', 'chart_read', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If d_in or k_pci <= 0, or if D^0.75 <= 0.39*k^0.25 (the slab is too
        thin / k too high -- off the digitized chart, undefined fractional
        power of a non-positive base).
    """
    if d_in <= 0:
        raise ValueError(f"d_in must be > 0, got {d_in}")
    if k_pci <= 0:
        raise ValueError(f"k_pci must be > 0, got {k_pci}")
    base = d_in ** 0.75 - 0.39 * k_pci ** 0.25
    if base <= 0:
        raise ValueError(
            f"d_in^0.75 - 0.39*k_pci^0.25 <= 0 (D={d_in}, k={k_pci}) -- slab "
            "too thin / k too high for this relation (off the digitized "
            "chart range)."
        )
    u_r = (base ** 3.42) / 100.0
    return {
        "d_in": d_in, "k_pci": k_pci, "u_r": round(u_r, 4), "chart_read": True,
        "equation": "u_r = [D^0.75 - 0.39*k^0.25]^3.42 / 100",
        "reference": "AASHTO 1993 Guide, Figure 3.5 (pdf_page 130, printed II-41)",
    }


# ============================================================================
# Figure 3.6: Correction of Effective Modulus of Subgrade Reaction for
# Potential Loss of Subbase Support (pdf_page 131, printed II-42).
# CHART READ-OFF.
#
# All 4 printed LS curves (LS=0, 1.0, 2.0, 3.0) are straight lines through
# the (1,1) origin in log-log space, i.e. pure power laws
# k_corrected = k^slope(LS). Rather than anchoring each slope to a single
# point, MULTIPLE (k, k_corrected) pairs were read directly along each
# curve (pdf_page 131), and the slope below is the one that reproduces
# ALL of them to a stated tolerance (asserted in
# ``tests/test_aashto_1993_composite_k.py``):
#   LS=0   -- slope=1.0 exact, by definition (no loss of support -> no
#             correction; also the chart's own visible 1:1 identity line).
#   LS=1.0 -- read pairs: (k=10,kc=7), (50,24), (100,43),
#             (540,170)<-EXACT anchor from the guide's Table 3.3 worked
#             example (pdf_page 132, printed II-43), (2000,495)<-chart
#             edge read. slope=0.8163 (solved from the exact 540->170
#             anchor) reproduces all 5 points within 7%.
#   LS=2.0 -- read pairs: (10,4), (50,10), (100,16), (2000,105), all
#             direct chart reads (no printed anchor for this curve).
#             slope=0.605 (average of the 4 points' own log-log slopes)
#             reproduces all 4 within 7%.
#   LS=3.0 -- read pairs: (10,2.5), (50,5.5), (100,8.5), (2000,42), all
#             direct chart reads. slope=0.464 reproduces the k=50-2000
#             points within 12%; the k=10 point (hardest to read
#             precisely, near the chart's bottom-left corner) is off by
#             16% -- flagged as this curve's main accuracy limitation.
# Intermediate LS values are linearly interpolated between these 4 slopes
# (clamped at LS=0/LS=3 for out-of-range inputs, via ``_linterp``).
# ============================================================================

_LS_VALUES = [0.0, 1.0, 2.0, 3.0]
_LS_SLOPES = [1.0, 0.8163, 0.605, 0.464]

# Read grid used ONLY for documentation/test verification (see section
# docstring above) -- the slopes in _LS_SLOPES already reproduce these.
_LS_READ_POINTS = {
    1.0: [(10, 7), (50, 24), (100, 43), (540, 170), (2000, 495)],
    2.0: [(10, 4), (50, 10), (100, 16), (2000, 105)],
    3.0: [(10, 2.5), (50, 5.5), (100, 8.5), (2000, 42)],
}


def k_loss_of_support(k_pci, ls) -> dict:
    """Effective k corrected for potential loss of subbase support (Figure 3.6).

        k_corrected = k_pci ^ slope(LS)

    slope(LS) is linearly interpolated between 4 anchors (LS=0, 1.0, 2.0,
    3.0 -> slope=1.0, 0.8163, 0.605, 0.464). Each slope (other than LS=0,
    exact by definition) is fit to MULTIPLE (k, k_corrected) points read
    directly off the chart along that LS curve (not a single anchor) --
    LS=1.0's read set includes an exact guide-printed value at k=540; see
    section docstring above for every read pair and the achieved
    per-curve tolerance (~7% for LS=1/2, ~12-16% for LS=3).

    Parameters
    ----------
    k_pci : float
        Effective modulus of subgrade reaction before loss-of-support
        correction, pci, > 0.
    ls : float
        Loss of support factor (see ``loss_of_support_values``, Table 2.7),
        nominally 0-3. Values outside [0, 3] are clamped to the nearest
        end slope.

    Returns
    -------
    dict
        {'k_pci', 'ls', 'k_corrected_pci', 'chart_read', 'equation',
        'reference', 'note'?}.

    Raises
    ------
    ValueError
        If k_pci <= 0.
    """
    if k_pci <= 0:
        raise ValueError(f"k_pci must be > 0, got {k_pci}")
    slope = _linterp(ls, _LS_VALUES, _LS_SLOPES)
    k_corrected = k_pci ** slope
    out = {
        "k_pci": k_pci, "ls": ls, "k_corrected_pci": round(k_corrected, 1),
        "chart_read": True,
        "equation": "k_corrected = k_pci^slope(LS)  (slope=1.0,0.8163,0.605,0.464 at LS=0,1,2,3; each fit to multiple chart-read points)",
        "reference": "AASHTO 1993 Guide, Figure 3.6 (pdf_page 131, printed II-42)",
    }
    if not (0.0 <= ls <= 3.0):
        out["note"] = "ls outside the guide's plotted range [0, 3]; slope clamped to the nearest end."
    return out


# ============================================================================
# Table 3.2: Table for Estimating Effective Modulus of Subgrade Reaction
# (pdf_page 127, printed II-38) -- the 8-step worksheet orchestrator.
# Fully worked example: Table 3.3 (pdf_page 132, printed II-43).
# ============================================================================

def effective_modulus_subgrade_reaction(seasonal, slab_d_in, dsb_in=None,
                                        esb_psi=None, dsg_ft=None, ls=0.0) -> dict:
    """Table 3.2 worksheet: seasonal composite k -> effective design k (pci).

    For each period in ``seasonal``: computes composite k (Figure 3.3, if a
    subbase is given -- ``dsb_in`` and an Esb for that period -- else the
    simple k=MR/19.4 relation), applies the rigid-foundation correction
    (Figure 3.4) if ``dsg_ft`` < 10 ft, computes relative damage u_r
    (Figure 3.5), then averages u_r over all periods, back-solves the
    effective k from the average u_r (closed-form inverse of the Figure
    3.5 relation), and applies the loss-of-support correction (Figure 3.6).

    Verified against the guide's fully-worked Table 3.3 example (pdf_page
    132, printed II-43): 12 monthly periods (6 in granular subbase, depth
    to rigid foundation 5 ft, projected slab thickness 9 in, LS=1.0) ->
    printed effective k=540 pci, LS-corrected k=170 pci. This module
    reproduces that to within about 4% (see
    ``tests/test_aashto_1993_composite_k.py`` for the exact figures). Most
    of the remaining error traces to ``composite_k_subbase`` (Figure 3.3
    read off the chart, within 5% of the guide's own printed reads, which
    themselves differ by 2.5% for one point); the Figure 3.4
    rigid-foundation step is exact at Dsg=5 ft (the depth used
    throughout Table 3.3) since it is anchored to 4 real printed
    (MR, k_inf, k) triples, not a single point. A Figure 3.3 note (an
    input above the printed curves) is carried on the period's row and in
    ``notes``; an input below them raises ValueError.

    Parameters
    ----------
    seasonal : list of dict
        One dict per seasonal increment (typically 12 monthly, or 24
        half-monthly), each with:
          'mr_psi' : float, required -- roadbed soil resilient modulus for
              that period.
          'esb_psi' : float, optional -- subbase modulus for that period;
              if omitted, falls back to the top-level ``esb_psi``.
    slab_d_in : float
        Projected (trial) slab thickness, inches, > 0 (used for every
        period's relative-damage calculation, Figure 3.5).
    dsb_in : float, optional
        Subbase thickness, inches. If omitted (or no Esb is available for
        a given period), that period's composite k falls back to the
        simple k=MR/19.4 relation (no subbase).
    esb_psi : float, optional
        Default subbase modulus, psi, used for any period that does not
        specify its own 'esb_psi'.
    dsg_ft : float, optional
        Depth to a rigid foundation (bedrock), feet. If given and < 10 ft,
        the Figure 3.4 correction is applied to every period before the
        relative-damage step (per the guide, this step is disregarded --
        and so is omitted here -- when dsg_ft is None or >= 10 ft).
    ls : float, optional
        Loss of support factor (Table 2.7), default 0.0 (no correction).

    Returns
    -------
    dict
        {'rows' (per-period worksheet: 'mr_psi', 'esb_psi'?,
        'composite_k_pci', 'k_rigid_foundation_pci'?, 'u_r'), 'n_periods',
        'ur_sum', 'ur_avg', 'effective_k_pci',
        'k_corrected_for_loss_of_support_pci', 'ls', 'slab_d_in', 'dsb_in',
        'esb_psi', 'dsg_ft', 'equation', 'reference', 'notes'?}.

    Raises
    ------
    ValueError
        If seasonal is empty, slab_d_in <= 0, a period is missing
        'mr_psi' or has mr_psi <= 0, a subbase input is below Figure 3.3's
        printed curves, or the back-solved effective k would be
        non-physical (average relative damage too large for this slab
        thickness).
    """
    if not seasonal:
        raise ValueError("seasonal must be a non-empty list of per-period dicts")
    if slab_d_in <= 0:
        raise ValueError(f"slab_d_in must be > 0, got {slab_d_in}")

    has_subbase = dsb_in is not None and dsb_in > 0
    rows = []
    notes = []
    for i, period in enumerate(seasonal):
        if "mr_psi" not in period:
            raise ValueError(f"seasonal[{i}] is missing the required key 'mr_psi'")
        mr = period["mr_psi"]
        if mr <= 0:
            raise ValueError(f"seasonal[{i}]['mr_psi'] must be > 0, got {mr}")
        period_esb = period.get("esb_psi", esb_psi)

        row = {"period": i, "mr_psi": mr}
        if has_subbase and period_esb is not None and period_esb > 0:
            comp = composite_k_subbase(mr, period_esb, dsb_in)
            k_composite = comp["k_inf_pci"]
            row["esb_psi"] = period_esb
            row["composite_k_pci"] = k_composite
            if "note" in comp:
                row["note"] = comp["note"]
                if comp["note"] not in notes:
                    notes.append(comp["note"])
        else:
            simple = modulus_subgrade_reaction_simple(mr)
            k_composite = simple["k_pci"]
            row["composite_k_pci"] = k_composite
            row["note"] = "no subbase (or esb_psi not given): k = MR/19.4"

        if dsg_ft is not None and dsg_ft < 10:
            rf = k_rigid_foundation_correction(mr, dsg_ft, k_composite)
            k_for_ur = rf["k_pci"]
            row["k_rigid_foundation_pci"] = k_for_ur
        else:
            k_for_ur = k_composite

        row["u_r"] = relative_damage_rigid(slab_d_in, k_for_ur)["u_r"]
        rows.append(row)

    n = len(rows)
    ur_sum = sum(r["u_r"] for r in rows)
    ur_avg = ur_sum / n

    # Closed-form inverse of relative_damage_rigid: solve k from ur_avg.
    #   u_r = [D^0.75 - 0.39*k^0.25]^3.42 / 100
    #   =>  k = { [D^0.75 - (100*u_r)^(1/3.42)] / 0.39 }^4
    base = slab_d_in ** 0.75 - (100 * ur_avg) ** (1 / 3.42)
    if base <= 0:
        raise ValueError(
            f"Average relative damage (u_r={ur_avg:.4f}) is too large for "
            f"slab_d_in={slab_d_in} -- the back-solved effective k would be "
            "non-physical. Increase slab_d_in or check the seasonal inputs."
        )
    k_effective = (base / 0.39) ** 4

    ls_result = k_loss_of_support(k_effective, ls)
    k_corrected = ls_result["k_corrected_pci"]

    out = {
        "rows": rows,
        "n_periods": n,
        "ur_sum": round(ur_sum, 4),
        "ur_avg": round(ur_avg, 4),
        "effective_k_pci": round(k_effective, 1),
        "ls": ls,
        "k_corrected_for_loss_of_support_pci": k_corrected,
        "slab_d_in": slab_d_in, "dsb_in": dsb_in, "esb_psi": esb_psi,
        "dsg_ft": dsg_ft,
        "equation": ("Table 3.2 worksheet: per-period composite k (Fig. 3.3 "
                    "read off the printed chart, or MR/19.4 with no subbase) "
                    "-> rigid-foundation correction (Fig. 3.4, if dsg_ft<10) "
                    "-> relative damage u_r (Fig. 3.5) -> average u_r -> "
                    "back-solved effective k -> loss-of-support correction "
                    "(Fig. 3.6)"),
        "reference": "AASHTO 1993 Guide, Table 3.2 (pdf_page 127, printed II-38)",
    }
    if notes:
        out["notes"] = notes
    return out
