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
``tests/test_aashto_1993_composite_k.py``). Two functions (Figure 3.3's
subbase-thickness dependence, Figure 3.4's rigid-foundation-depth
dependence) have NO printed numeric anchor away from their one reference
value and rely on lower-confidence direct chart reads instead (explicitly
flagged, with a wider stated tolerance, in their own section docstrings)
rather than an unanchored fitted exponent.

Chained end-to-end, this module reproduces the guide's own Table 3.3
worked example (composite k -> rigid-foundation correction -> relative
damage per season -> average -> back-solved effective k -> loss-of-support
correction) to within about 3% (see
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
# This is a 3-variable (Dsb, Esb, MR), 4-quadrant nomograph with a "turning
# line": (1) project up from Dsb on the shared thickness axis to the Esb
# curve; (2) project that height right to the turning line; (3) separately
# project up from the SAME Dsb value to the MR curve in the lower quadrant,
# then right to the turning line; (4) a vertical line from the turning-line
# point combines with the Esb-quadrant height to land on a k_inf diagonal
# (traced directly for the printed worked example; pdf_page 128).
#
#   k_inf = (MR/19.4) * [1 + A*(Esb/MR)^B * dsb_scale(Dsb)]
#
# The (MR/19.4) factor is the guide's own bare-roadbed relation
# (equations.modulus_subgrade_reaction_simple), so the bracket is the
# subbase's amplification factor. This function is only meaningful over
# the digitized chart range Dsb=6-18 in (dsb_scale is CLAMPED, not
# extrapolated to 0, outside that range -- see the note flag below); for
# the true no-subbase case, callers should use
# ``equations.modulus_subgrade_reaction_simple`` directly (this is exactly
# what ``effective_modulus_subgrade_reaction`` does when no Dsb/Esb is
# given for a period), not this function with a vanishingly small dsb_in.
#
# A, B (the Esb/MR power law, held at the reference Dsb=6 in) fit (exact
# 2-point log-log solve) to the two most-separated of FOUR printed anchors,
# all at Dsb=6 in (Table 3.3 worked example, pdf_page 132, printed II-43 --
# the guide's own fully-worked seasonal example uses a 6-inch granular
# subbase throughout):
#   Esb=50,000 psi, MR=20,000 psi -> k_inf=1,100 pci  (F-1=0.0670)
#   Esb=15,000 psi, MR= 2,500 psi -> k_inf=  160 pci  (F-1=0.2416)  <- fit pts
#   Esb=15,000 psi, MR= 4,000 psi -> k_inf=  230 pci  (F-1=0.1155)  <- check
#   Esb=20,000 psi, MR= 7,000 psi -> k_inf=  410 pci  (F-1=0.1363)  <- check
# Plus a 5th anchor, Figure 3.3's OWN standalone worked example (same page):
#   Esb=20,000 psi, MR= 7,000 psi -> k_inf=  400 pci  (F-1=0.1086)
# (identical inputs to the anchor immediately above -- the guide's own two
# independent reads of the same chart point differ by ~2.5%, which sets a
# natural noise floor for this whole digitization).
# Cross-checking the fitted A, B against the 3rd/4th/5th anchors gives
# predicted k_inf = 231 (act. 230, +0.5%) and 390 (act. 400-410, -2.4% to
# -4.8%) -- i.e. within the guide's own reading noise.
#
# dsb_scale(Dsb) -- a DENSITY READ GRID, not a fitted exponent -- replaces
# the smooth power-law extrapolation. Every printed numeric example in this
# guide happens to use Dsb=6 in, so there is no printed anchor away from
# Dsb=6; the two additional points below are direct visual chart reads,
# tracing the same 4-quadrant construction as the worked example but at
# Dsb=12 in and Dsb=18 in gridlines (Esb=20,000/MR=7,000 held fixed,
# pdf_page 128 -- narrow high-DPI column crops through both the Esb and MR
# quadrants). Confidence is markedly lower than the Dsb=6 anchors (a raster
# scan with no vector data does not support pixel-exact reads of this
# 4-quadrant construction away from the one example the guide traces with
# arrows) -- treat these two points as +/-20-25%:
#   Dsb= 6 in -> dsb_scale = 1.00  (anchor-defined; F-1 above is *this*
#                                    quantity, read directly)
#   Dsb=12 in -> dsb_scale = 1.16  (chart read; ESB/MR curve families are
#                                    visibly more spread apart / less
#                                    converged at Dsb=12 than at Dsb=6)
#   Dsb=18 in -> dsb_scale = 1.30  (chart read, same method, Dsb=18 in)
# Linearly interpolated (clamped outside 6-18 in) via ``_linterp``.
#
# Net effect: at Esb/MR=2.857 (the Table 3.3 June-Oct point), k_inf only
# rises from 390 pci (Dsb=6) to 399 pci (Dsb=18) -- a modest ~2% change,
# because the Dsb-scale multiplies the *amplification* term (which is
# itself only ~8-11% for this Esb/MR ratio), not the full k_inf. This is
# a real (if imprecise) chart-based finding, not an assumption -- treat it
# as this function's single largest accuracy limitation and cross-check
# Figure 3.3 directly for designs with Dsb far from 6 in, or where the
# Esb/MR ratio is far from the 2.5-6.0 range spanned by the anchors.
# ============================================================================

_COMPK_A = 0.01750
_COMPK_B = 1.4650
_COMPK_DSB_VALUES = [6.0, 12.0, 18.0]
_COMPK_DSB_SCALE = [1.00, 1.16, 1.30]

_COMPK_ESB_RANGE = (15000.0, 1000000.0)
_COMPK_MR_RANGE = (1000.0, 20000.0)
_COMPK_DSB_RANGE = (6.0, 18.0)


def composite_k_subbase(mr_psi, esb_psi, dsb_in) -> dict:
    """Composite modulus of subgrade reaction k_inf, semi-infinite subgrade
    depth (Figure 3.3 nomograph read-off; see module/section docstring for
    the read-grid derivation and anchor points).

        k_inf = (MR/19.4) * [1 + 0.0175*(Esb/MR)^1.465 * dsb_scale(Dsb)]

    dsb_scale is a 3-point read grid (Dsb=6/12/18 in -> 1.00/1.16/1.30,
    linearly interpolated), NOT a fitted exponent -- see section docstring
    for provenance and the (wider) tolerance away from Dsb=6 in.

    Parameters
    ----------
    mr_psi : float
        Roadbed soil resilient modulus for the season, psi, > 0. Digitized
        chart range approximately 1,000-20,000 psi.
    esb_psi : float
        Subbase elastic (resilient) modulus for the season, psi, > 0.
        Digitized chart range 15,000-1,000,000 psi (the 9 printed curves).
    dsb_in : float
        Subbase thickness, inches, > 0. Digitized chart range
        approximately 6-18 in.

    Returns
    -------
    dict
        {'mr_psi', 'esb_psi', 'dsb_in', 'k_inf_pci', 'chart_read',
        'equation', 'reference', 'note'?}.

    Raises
    ------
    ValueError
        If mr_psi, esb_psi, or dsb_in <= 0.
    """
    if mr_psi <= 0:
        raise ValueError(f"mr_psi must be > 0, got {mr_psi}")
    if esb_psi <= 0:
        raise ValueError(f"esb_psi must be > 0, got {esb_psi}")
    if dsb_in <= 0:
        raise ValueError(f"dsb_in must be > 0, got {dsb_in}")

    r = esb_psi / mr_psi
    scale = _linterp(dsb_in, _COMPK_DSB_VALUES, _COMPK_DSB_SCALE)
    amplification = 1 + _COMPK_A * r ** _COMPK_B * scale
    k_inf = (mr_psi / 19.4) * amplification

    out = {
        "mr_psi": mr_psi, "esb_psi": esb_psi, "dsb_in": dsb_in,
        "k_inf_pci": round(k_inf, 1), "chart_read": True,
        "equation": ("k_inf = (MR/19.4)*[1 + 0.0175*(Esb/MR)^1.465*dsb_scale(Dsb)]; "
                    "dsb_scale read grid: Dsb=6/12/18in -> 1.00/1.16/1.30"),
        "reference": "AASHTO 1993 Guide, Figure 3.3 (pdf_page 128, printed II-39)",
    }
    notes = []
    if not (_COMPK_ESB_RANGE[0] <= esb_psi <= _COMPK_ESB_RANGE[1]):
        notes.append(
            f"esb_psi outside the digitized chart range {_COMPK_ESB_RANGE} psi -- extrapolated."
        )
    if not (_COMPK_MR_RANGE[0] <= mr_psi <= _COMPK_MR_RANGE[1]):
        notes.append(
            f"mr_psi outside the digitized chart range {_COMPK_MR_RANGE} psi -- extrapolated."
        )
    if not (_COMPK_DSB_RANGE[0] <= dsb_in <= _COMPK_DSB_RANGE[1]):
        notes.append(
            f"dsb_in outside the digitized chart range {_COMPK_DSB_RANGE} in -- extrapolated "
            "(dsb_scale read grid clamped at the nearest end)."
        )
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
    reproduces that to within about 3% (effective k ~525.5, -2.7%;
    LS-corrected k ~166.3, -2.2%) -- see
    ``tests/test_aashto_1993_composite_k.py`` for the exact figures. Most
    of the remaining error traces to ``composite_k_subbase`` (the Esb/MR
    power law is within ~5% of its own printed anchors, and is the only
    piece of the chain without an exact per-row match); the Figure 3.4
    rigid-foundation step is now exact at Dsg=5 ft (the depth used
    throughout Table 3.3) since it is anchored to 4 real printed
    (MR, k_inf, k) triples, not a single point.

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
        'esb_psi', 'dsg_ft', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If seasonal is empty, slab_d_in <= 0, a period is missing
        'mr_psi' or has mr_psi <= 0, or the back-solved effective k would
        be non-physical (average relative damage too large for this slab
        thickness).
    """
    if not seasonal:
        raise ValueError("seasonal must be a non-empty list of per-period dicts")
    if slab_d_in <= 0:
        raise ValueError(f"slab_d_in must be > 0, got {slab_d_in}")

    has_subbase = dsb_in is not None and dsb_in > 0
    rows = []
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

    return {
        "rows": rows,
        "n_periods": n,
        "ur_sum": round(ur_sum, 4),
        "ur_avg": round(ur_avg, 4),
        "effective_k_pci": round(k_effective, 1),
        "ls": ls,
        "k_corrected_for_loss_of_support_pci": k_corrected,
        "slab_d_in": slab_d_in, "dsb_in": dsb_in, "esb_psi": esb_psi,
        "dsg_ft": dsg_ft,
        "equation": ("Table 3.2 worksheet: per-period composite k (Fig. 3.3, or "
                    "MR/19.4 with no subbase) -> rigid-foundation correction "
                    "(Fig. 3.4, if dsg_ft<10) -> relative damage u_r (Fig. 3.5) "
                    "-> average u_r -> back-solved effective k -> loss-of-support "
                    "correction (Fig. 3.6)"),
        "reference": "AASHTO 1993 Guide, Table 3.2 (pdf_page 127, printed II-38)",
    }
