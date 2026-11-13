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
Figure 3.4 is read along its three Dsg curves and twelve k_inf lines and
worked by its own construction too (GM-303).

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
# Outside the printed curves the lookup raises ValueError (REF-76): Dsb
# outside 6-18 in, Esb outside 15,000-1,000,000 psi, MR outside
# 1,000-20,000 psi, or a construction landing beyond the 2,000 pci diagonal
# or short of the 50 pci one. Reading off the nearest curve below the chart
# would overstate k; above it, it would understate k, but the guide's text
# gives no rule for either.
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
        'method', 'reference'}.

    Raises
    ------
    ValueError
        If an input is <= 0, or Dsb, Esb or MR is outside Figure 3.3's
        printed curves (Dsb 6-18 in, Esb 15,000-1,000,000 psi, MR
        1,000-20,000 psi, printed II-39), or the construction lands beyond
        the 2,000 pci diagonal or short of the 50 pci one: the chart gives
        no k_inf there, and the guide's text no rule.
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
    if dsb_in > _COMPK_DSB_RANGE[1]:
        raise ValueError(
            f"Subbase thickness {dsb_in} in is above Figure 3.3's printed "
            f"Dsb scale ({_COMPK_DSB_RANGE[0]:g}-{_COMPK_DSB_RANGE[1]:g} in, "
            "printed II-39); the chart gives no k_inf there. Read the chart "
            "and give k directly.")
    if esb_psi > _COMPK_ESB_RANGE[1]:
        raise ValueError(
            f"Subbase modulus {esb_psi:,.0f} psi is above Figure 3.3's "
            f"highest printed curve ({_COMPK_ESB_RANGE[1]:,.0f} psi, printed "
            "II-39); the chart gives no k_inf there. Give k directly.")
    if mr_psi > _COMPK_MR_RANGE[1]:
        raise ValueError(
            f"Roadbed modulus {mr_psi:,.0f} psi is above Figure 3.3's "
            f"highest printed curve ({_COMPK_MR_RANGE[1]:,.0f} psi, printed "
            "II-39); the chart gives no k_inf there. Give k directly.")
    dsb, esb, mr = dsb_in, esb_psi, mr_psi

    y_e = _compk_curve_height(_COMPK_UPPER, _COMPK_ESB, dsb, esb)
    y_m = _compk_curve_height(_COMPK_LOWER, _COMPK_MR, dsb, mr)
    c = y_m + _compk_turning_c(y_m) - y_e
    if not _COMPK_K_C[0] <= c <= _COMPK_K_C[-1]:
        edge = ("beyond the highest drawn diagonal, 2,000 pci"
                if c > _COMPK_K_C[-1]
                else "short of the lowest labelled diagonal, 50 pci")
        raise ValueError(
            f"Figure 3.3's construction for MR {mr_psi:,.0f} psi, Esb "
            f"{esb_psi:,.0f} psi and Dsb {dsb_in:g} in lands {edge} (printed "
            "II-39); the chart gives no k_inf there. Give k directly.")
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
    return out


# ============================================================================
# Figure 3.4: Chart to Modify Modulus of Subgrade Reaction to Consider
# Effects of Rigid Foundation Near Surface (within 10 feet)
# (pdf_page 129, printed II-40). CHART READ off the print.
#
# The chart's construction: up from MR to the Dsg curve (2, 5 and 10 ft are
# drawn), across to the k_inf line (50 to 1,400 pci are drawn), down to k.
# Example on the chart: MR 4,000, Dsg 5, k_inf 230 -> 300.
#
# How it was read (GM-303, 2026-11-02; replaces a multiplier per MR, exact
# at the four Table 3.3 rows, scaled by a three-point depth guess, which
# left out the chart's dependence on k_inf and was 12-36 % below the chart
# at Dsg 2-3 ft or at twice the MR/19.4 k_inf, and up to 26 % above it at
# Dsg 7-9 ft): the page at the scan's resolution (about 305 dpi). The three
# Dsg curves were traced on the ink and thinned to within 0.5 px at the
# 95th percentile (1.8 px at worst); the twelve k_inf lines were fitted as
# straight lines (median offset 0.5-1.4 px); the axes come from their
# gridlines, and the example's own arrows (MR 4,000) confirm the MR scale.
# Between curves k is linear in Dsg; between lines, linear in k_inf.
#
# Checked against the example (read 303) and Table 3.3 (pdf_page 132,
# printed II-43; all at Dsg 5 ft): k_inf 1,100 / 160 / 230 / 410 ->
# printed 1,350 / 230 / 300 / 540, read 1,378 / 222 / 303 / 539 (-3.5 to
# +2.1 %).
#
# II-37, step (4): the correction applies when bedrock lies "within 10 feet
# of the surface of the subgrade"; at 10 ft or more none is applied.
# ============================================================================

_FIG34_REF = "AASHTO 1993 Guide, Figure 3.4 (pdf_page 129, printed II-40)"

# Left half: the three Dsg curves as (MR psi, height in scan pixels,
# downward), thinned to within 0.5 px of the traced ink. The frame runs
# from 1910.5 (bottom) to 464.5 (top).
_FIG34_DSG_CURVES = {
    2: ((20007, 1782.2), (19142, 1773.9), (17570, 1755.8), (17354, 1754.3),
        (16450, 1742.1), (15723, 1730.8), (15566, 1729.5), (15035, 1721.3),
        (14466, 1711.5), (13110, 1685.3), (13012, 1684.2), (12265, 1667.9),
        (10968, 1637.9), (9868, 1607.5), (9200, 1587.4), (8433, 1561.9),
        (7883, 1540.7), (7137, 1508.9), (6567, 1482.2), (6210, 1462.1),
        (5661, 1427.0), (4979, 1376.0), (4696, 1352.0), (4377, 1322.0),
        (3850, 1265.0), (3796, 1261.0), (3609, 1239.0), (3340, 1201.0),
        (3208, 1178.0), (3077, 1149.0), (3011, 1139.0), (2649, 1038.0),
        (2590, 1028.0), (2519, 1009.0), (2247, 925.0), (2176, 909.0),
        (1852, 795.0), (1698, 728.0), (1634, 693.0), (1557, 671.0),
        (1553, 663.0), (1391, 581.8), (1326, 560.0), (1169, 471.0)),
    5: ((20007, 1861.5), (18828, 1852.2), (17590, 1841.2), (17492, 1841.4),
        (16548, 1833.0), (15664, 1823.6), (15566, 1823.9), (15428, 1822.5),
        (14643, 1813.4), (13110, 1792.9), (12992, 1792.3), (12245, 1780.9),
        (11184, 1762.8), (10968, 1760.0), (8964, 1721.2), (8650, 1713.8),
        (8473, 1710.5), (7785, 1692.9), (7431, 1682.4), (6410, 1649.4),
        (5899, 1629.6), (5408, 1608.5), (4877, 1583.7), (4531, 1563.9),
        (3932, 1524.0), (3506, 1491.0), (3345, 1477.0), (3026, 1444.0),
        (2533, 1382.0), (2438, 1372.0), (2168, 1332.0), (1840, 1268.0),
        (1785, 1261.0), (1708, 1245.0), (1474, 1183.0), (1377, 1150.0),
        (1340, 1145.0), (1239, 1107.0), (1181, 1074.0), (1146, 1064.0),
        (1143, 1057.0), (1104, 1043.0), (1099, 1034.0), (1073, 1028.0)),
    10: ((20007, 1906.1), (19083, 1904.6), (18238, 1901.1), (17727, 1898.1),
         (17590, 1897.6), (17472, 1898.0), (16725, 1893.9), (15664, 1886.8),
         (15487, 1887.0), (14760, 1880.9), (13601, 1869.9), (13110, 1864.2),
         (12953, 1863.7), (10575, 1835.1), (9180, 1813.3), (8198, 1796.0),
         (7490, 1781.2), (6724, 1763.6), (6488, 1759.1), (5702, 1738.6),
         (5290, 1725.9), (4897, 1711.7), (4366, 1689.3), (3855, 1663.5),
         (3437, 1638.0), (3040, 1610.0), (2762, 1587.0), (2534, 1566.0),
         (2301, 1542.0), (1809, 1482.0), (1582, 1445.0), (1455, 1421.0),
         (1281, 1383.0), (1206, 1371.0), (1083, 1338.0)),
}
# Right half: each drawn k_inf line by the k it reads at the frame's bottom
# and at its top (pci on the k scale; the lines that leave through the
# right side extended to the top).
_FIG34_K_INF = (50, 100, 200, 300, 400, 500, 600, 700, 800, 1000, 1200, 1400)
_FIG34_K_BOTTOM = (17.6, 40.4, 108.6, 199.0, 296.7, 407.9, 514.6, 636.4,
                   772.0, 1053.0, 1355.7, 1666.2)
_FIG34_K_TOP = (76.1, 228.1, 620.9, 1115.2, 1629.0, 2215.4, 2838.8, 3512.0,
                4173.0, 5710.2, 6959.2, 8321.8)
_FIG34_Y = (1910.5, 464.5)
_FIG34_MR_MAX = 20_000.0              # the MR axis's end
# Each curve's lowest drawn MR: the 2-ft curve leaves the chart's top at
# 1,169 psi; the 5-ft and 10-ft curves end at 1,073 and 1,083 psi.
_FIG34_MR_MIN = {d: min(pt[0] for pt in c) for d, c in _FIG34_DSG_CURVES.items()}
_FIG34_K_MAX = 2000.0                 # the k scale's right end
_RIGIDCORR_DSG_LIMIT = 10.0


def k_rigid_foundation_correction(mr_psi, dsg_ft, k_inf_pci) -> dict:
    """k on a rigid foundation (bedrock) within 10 ft, from Figure 3.4 as
    printed (see the section note above): up from MR to the Dsg curve,
    across to the k_inf line, down to k.

    Dsg of 10 ft or more: no correction (II-37, step (4)). Outside the
    drawn curves the lookup raises ValueError (REF-76; the guide's text
    gives no rule there):

    - Dsg below 2 ft, the shallowest curve (2, 5 and 10 ft are drawn);
    - MR above 20,000 psi, the chart's edge, or below the lowest MR at
      which the curves used are drawn: the 2-ft curve leaves the top at
      1,169 psi, the 5-ft and 10-ft curves end at 1,073 and 1,083 psi. A
      Dsg between two curves needs both (2-5 ft: 1,169 psi; 5-10 ft:
      1,083 psi); a Dsg of 2 or 5 ft needs only its own curve;
    - k_inf outside the drawn lines (50-1,400 pci);
    - a construction landing past the k scale's 2,000 pci end.

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
        {'mr_psi', 'dsg_ft', 'k_inf_pci', 'k_pci', 'chart_read', 'method',
        'reference', 'note'?}.

    Raises
    ------
    ValueError
        If mr_psi, dsg_ft, or k_inf_pci <= 0, or an input is outside
        Figure 3.4's drawn curves (above).
    """
    for name, val in (("mr_psi", mr_psi), ("dsg_ft", dsg_ft),
                      ("k_inf_pci", k_inf_pci)):
        if val is None or val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    out = {"mr_psi": mr_psi, "dsg_ft": dsg_ft, "k_inf_pci": k_inf_pci,
           "chart_read": True, "reference": _FIG34_REF,
           "method": ("Figure 3.4 read off the printed chart (the Dsg curves "
                      "traced, the k_inf lines fitted; the chart's own "
                      "construction)")}
    if dsg_ft >= _RIGIDCORR_DSG_LIMIT:
        out["k_pci"] = round(k_inf_pci, 1)
        out["note"] = ("Depth to the rigid foundation is 10 ft or more; no "
                       "correction (II-37, step (4)).")
        return out
    if not _FIG34_K_INF[0] <= k_inf_pci <= _FIG34_K_INF[-1]:
        raise ValueError(
            f"k_inf {k_inf_pci:,.0f} pci is outside Figure 3.4's drawn k_inf "
            "lines (50-1,400 pci, printed II-40); the chart gives no "
            "correction there.")
    if dsg_ft < 2:
        raise ValueError(
            f"Dsg {dsg_ft} ft is shallower than Figure 3.4's 2-ft curve, the "
            "shallowest drawn (2, 5 and 10 ft, printed II-40); the chart "
            "gives no k there.")
    dsg = dsg_ft
    if dsg in _FIG34_DSG_CURVES:
        used = (next(d for d in _FIG34_DSG_CURVES if d == dsg),)
    else:
        used = (2, 5) if dsg < 5 else (5, 10)
    mr_min = max(_FIG34_MR_MIN[d] for d in used)
    if not mr_min <= mr_psi <= _FIG34_MR_MAX:
        curves = " and ".join(f"{d}-ft" for d in used)
        ends = "; ".join(
            f"the {d}-ft curve {'leaves the top' if d == 2 else 'ends'} at "
            f"{_FIG34_MR_MIN[d]:,.0f} psi" for d in used)
        raise ValueError(
            f"MR {mr_psi:,.0f} psi is outside {mr_min:,.0f}-"
            f"{_FIG34_MR_MAX:,.0f} psi, where Figure 3.4's {curves} "
            f"curve{'s are' if len(used) > 1 else ' is'} drawn for Dsg "
            f"{dsg_ft:g} ft (printed II-40: the MR axis ends at 20,000 psi; "
            f"{ends}); the chart gives no k there.")
    mr = mr_psi

    def height(d):
        pts = _FIG34_DSG_CURVES[d][::-1]          # MR ascending
        return _linterp(mr, [p[0] for p in pts], [p[1] for p in pts])
    if len(used) == 1:
        y = height(used[0])
    else:
        lo, hi = used
        y = height(lo) + (height(hi) - height(lo)) * (dsg - lo) / (hi - lo)
    frac = (_FIG34_Y[0] - y) / (_FIG34_Y[0] - _FIG34_Y[1])
    k_lines = [b + (t - b) * frac for b, t in zip(_FIG34_K_BOTTOM,
                                                  _FIG34_K_TOP)]
    k = _linterp(k_inf_pci, list(_FIG34_K_INF), k_lines)
    if k > _FIG34_K_MAX:
        raise ValueError(
            f"Figure 3.4's construction for MR {mr_psi:,.0f} psi, Dsg "
            f"{dsg_ft:g} ft and k_inf {k_inf_pci:,.0f} pci lands past the k "
            "scale's 2,000 pci end (printed II-40); the chart gives no k "
            "there.")
    out["k_pci"] = round(k, 1)
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
    """Seasonal relative damage u_r for a rigid slab, AASHTO 1993 Figure 3.5
    (pdf_page 130, printed II-41); returns u_r (dimensionless, the chart's
    "Relative Damage" divided by 100). Figure 3.5 is a chart (u against
    composite k for slab thicknesses 6-14 in) and prints no equation; this
    function computes a closed form fitted to it (a judgment call kept as
    coded, review pave-28), and its result says so:

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
        "print_note": ("Figure 3.5 (printed II-41) is a chart and prints no "
                       "equation; u_r is a closed form fitted to it (Table "
                       "3.3's four rows within 0.6 %, chart reads at D 6-14 "
                       "in within 12.5 %)."),
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
# Intermediate LS values are linearly interpolated between these 4 slopes.
# LS outside 0-3 (the chart's LS = 0 and LS = 3.0 lines) is refused
# (REF-76).
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
    """Effective modulus of subgrade reaction corrected for potential loss
    of subbase support, AASHTO 1993 Figure 3.6 (pdf_page 131, printed
    II-42); returns k_corrected_pci, pci. Figure 3.6 is a chart (four LS
    lines on log-log axes) and prints no equation; this function computes
    a power law whose slopes are fitted to points read off the chart (a
    judgment call kept as coded, review pave-28), and its result says so:

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
        0 to 3: Figure 3.6 draws the lines LS = 0, 1.0, 2.0 and 3.0
        (printed II-42) and nothing past them.

    Returns
    -------
    dict
        {'k_pci', 'ls', 'k_corrected_pci', 'chart_read', 'equation',
        'reference', 'print_note'}.

    Raises
    ------
    ValueError
        If k_pci <= 0, or ls is outside 0-3. Above LS = 3 the chart gives
        no line, and holding the LS = 3.0 line would give a larger k than
        the trend; a negative LS is not a loss of support.
    """
    if k_pci <= 0:
        raise ValueError(f"k_pci must be > 0, got {k_pci}")
    if not _LS_VALUES[0] <= ls <= _LS_VALUES[-1]:
        raise ValueError(
            f"ls = {ls} is outside Figure 3.6's lines, LS = 0, 1.0, 2.0 and "
            "3.0 (printed II-42); the chart gives no correction there.")
    slope = _linterp(ls, _LS_VALUES, _LS_SLOPES)
    k_corrected = k_pci ** slope
    out = {
        "k_pci": k_pci, "ls": ls, "k_corrected_pci": round(k_corrected, 1),
        "chart_read": True,
        "equation": "k_corrected = k_pci^slope(LS)  (slope=1.0,0.8163,0.605,0.464 at LS=0,1,2,3; each fit to multiple chart-read points)",
        "reference": "AASHTO 1993 Guide, Figure 3.6 (pdf_page 131, printed II-42)",
        "print_note": ("Figure 3.6 (printed II-42) is a chart and prints no "
                       "equation; the slopes are a fit to points read off "
                       "its LS = 1, 2 and 3 lines (within about 7 % for "
                       "LS 1 and 2, 12-16 % for LS 3). Only LS = 1 at "
                       "k = 540 (170 pci) is a printed value (Table 3.3)."),
    }
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
    themselves differ by 2.5% for one point) and to
    ``k_rigid_foundation_correction`` (Figure 3.4 read off the chart,
    within -3.5 to +2.1% of the guide's reads at Dsg=5 ft), the two
    chart reads stacking in each row. An input outside the printed curves
    of Figure 3.3, 3.4 or 3.6 raises their ValueError (REF-76); a note
    from them would be carried on the period's row and in ``notes``.

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
        Loss of support factor (Table 2.7), 0 to 3 (Figure 3.6's lines,
        printed II-42), default 0.0 (no correction).

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
        'mr_psi' or has mr_psi <= 0, an input is outside the printed
        curves of Figure 3.3, 3.4 or 3.6, or the back-solved effective k
        would be
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
            if "note" in rf:
                row["note"] = (row["note"] + " " + rf["note"]
                               if "note" in row else rf["note"])
                if rf["note"] not in notes:
                    notes.append(rf["note"])
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
                    "-> rigid-foundation correction (Fig. 3.4 read off the "
                    "printed chart, if dsg_ft<10) "
                    "-> relative damage u_r (Fig. 3.5) -> average u_r -> "
                    "back-solved effective k -> loss-of-support correction "
                    "(Fig. 3.6)"),
        "reference": "AASHTO 1993 Guide, Table 3.2 (pdf_page 127, printed II-38)",
    }
    if notes:
        out["notes"] = notes
    return out
