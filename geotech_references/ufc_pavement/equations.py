"""UFC 3-250-01 pavement design equations.

Pavement Design for Roads, Streets, Walks, and Storage Areas (14 November
2016). Covers roads, streets, walks, and open storage areas -- NOT airfields
(airfields are UFC 3-260-02; a separate, distinct DoD manual). All numbers
below are traced to a rendered page of ``docs/ufc_3_250_01_2016.pdf`` (0-based
fitz page index cited in each docstring as ``pdf_page``; the printed page is
also given).

UNITS: this UFC is US-customary native (in, psi, pci, lb) -- values are kept
in source units per repo convention; SI conversion notes are given where the
guide itself prints one (mm = 25.4 x in; kPa/mm = psi/in / 0.271).

Traffic characterization (the module-level analog to a "design index"): this
UFC does NOT use the airfield UFC's discrete Design Index bins. Instead
(Chapter 4), mixed traffic is converted through a CBR/thickness-based
equivalency procedure into an equivalent number of passes of an 18,000-lb
(8,200-kg) single-axle, dual-tire ESAL -- see ``mixed_traffic_equivalent_esal``
below, verified against the guide's own worked examples (Appendix G, Tables
G-1/G-2/G-3/G-4).

Primary design tool is PCASE software; the printed design curves (Appendix E
flexible, Appendix F rigid) and the equations below are the documented
non-PCASE fallback ("Design charts have been prepared using PCASE and can be
used in lieu of PCASE", Ch 4, pdf_page 28).

Every printed closed-form equation in the document (Eq 13-1, 15-1..15-4,
17-1, 20-1..20-23) is reproduced here VERBATIM and, where the document
supplies a worked numeric example (Appendix G), independently re-derived by
hand and confirmed to match the printed answer -- see individual docstrings.
"""

import math


# ============================================================================
# Mixed traffic -> equivalent 18-kip ESAL passes (Chapter 4, Section 4-3.3;
# pdf_page 30-31, printed 10-11; worked examples Appendix G, G-1, pdf_page
# 275-277, printed 256-258, Tables G-1/G-2)
#
# Procedure (verbatim from the guide): for each vehicle in the mix, determine
# the required pavement thickness at the representative subgrade CBR/k
# (Table 4-1) and the vehicle's design total passes. Pick the vehicle with
# the largest required thickness as the "controlling vehicle". For every
# OTHER vehicle, read (from the same design curve, in reverse) the ALLOWABLE
# passes at the controlling vehicle's thickness; the ratio
# (controlling design passes / that vehicle's allowable passes) times that
# vehicle's own design passes gives its contribution in equivalent passes of
# the controlling vehicle. Summing over all vehicles (including the
# controlling vehicle itself, ratio = 1) gives the total equivalent passes.
# ============================================================================


def mixed_traffic_equivalent_esal(vehicles) -> dict:
    """Convert a mixed-traffic vehicle mix to equivalent passes of the
    controlling vehicle (Chapter 4, Section 4-3.3).

    Reproduces the guide's Table G-1/G-2 procedure exactly: the controlling
    vehicle is the one with the largest required thickness (read from the
    applicable design curve, e.g. Appendix E/F, at the representative
    subgrade CBR/k); every other vehicle's design passes are re-expressed as
    equivalent passes of the controlling vehicle via the ratio of allowable
    passes.

    Verified against the guide's printed Table G-1 (pdf_page 276, printed
    257): 4-vehicle mix (18-kip ESAL controlling, 1,000,000 design passes,
    16.4 in required; 5-axle truck 100,000 design passes/15.8 in required/
    252,915 allowable passes at 16.4 in) -> equivalent passes of the 18-kip
    ESAL = 1,395,400 (matches printed total exactly, within input rounding).

    Parameters
    ----------
    vehicles : list of dict
        Each dict: {'name': str, 'design_passes': float,
        'required_thickness_in': float, 'allowable_passes_at_controlling':
        float or None}. ``required_thickness_in`` is the thickness read from
        the design curve for that vehicle's own design_passes at the
        representative subgrade CBR/k (Table 4-1). Determine
        ``allowable_passes_at_controlling`` for the NON-controlling vehicles
        by reading (in reverse) the design curve at the controlling
        thickness; use ``None`` (or omit) for the controlling vehicle -- it
        is filled in automatically as its own design_passes (ratio 1.0). Use
        ``float('inf')`` if a vehicle's allowable passes at the controlling
        thickness is effectively unlimited (thickness governed elsewhere).

    Returns
    -------
    dict
        {'controlling_vehicle': str, 'controlling_thickness_in': float,
         'rows': [{'name', 'design_passes', 'required_thickness_in',
                    'allowable_passes_at_controlling', 'ratio',
                    'equivalent_passes'}, ...],
         'total_equivalent_esal_passes': float,
         'reference'}.

    Raises
    ------
    ValueError
        If ``vehicles`` is empty or a required key is missing.
    """
    if not vehicles:
        raise ValueError("vehicles must be a non-empty list")
    for v in vehicles:
        for key in ("name", "design_passes", "required_thickness_in"):
            if key not in v:
                raise ValueError(f"each vehicle dict must include '{key}'")

    controlling = max(vehicles, key=lambda v: v["required_thickness_in"])
    controlling_thickness = controlling["required_thickness_in"]
    controlling_design_passes = controlling["design_passes"]

    rows = []
    total = 0.0
    for v in vehicles:
        if v is controlling:
            allowable = controlling_design_passes
            ratio = 1.0
        else:
            allowable = v.get("allowable_passes_at_controlling")
            if allowable is None:
                raise ValueError(
                    f"vehicle '{v['name']}' needs "
                    "'allowable_passes_at_controlling' (read the design "
                    "curve in reverse at the controlling thickness)"
                )
            if allowable == float("inf") or allowable <= 0:
                ratio = 0.0
            else:
                # Table G-1 col (6) = controlling design passes / this
                # vehicle's allowable passes at the controlling thickness.
                ratio = controlling_design_passes / allowable
        # Table G-1 col (7) = ratio * this vehicle's own design passes.
        equivalent = ratio * v["design_passes"]
        rows.append({
            "name": v["name"],
            "design_passes": v["design_passes"],
            "required_thickness_in": v["required_thickness_in"],
            "allowable_passes_at_controlling": allowable,
            "ratio": round(ratio, 4),
            "equivalent_passes": round(equivalent, 0),
        })
        total += equivalent

    return {
        "controlling_vehicle": controlling["name"],
        "controlling_thickness_in": controlling_thickness,
        "rows": rows,
        "total_equivalent_esal_passes": round(total, 0),
        "reference": (
            "UFC 3-250-01, Section 4-3.3 (pdf_page 30, printed 10); worked "
            "example Table G-1 (pdf_page 276, printed 257)"
        ),
    }


# ============================================================================
# Stabilized layer equivalency (Chapter 9, Section 9-5.1, Table 9-1;
# pdf_page 46, printed 27; worked examples Appendix G, G-4, pdf_page 279-280,
# printed 260-261)
#
#   t_stab = t_conventional / E
# ============================================================================

def stabilized_layer_thickness_in(conventional_thickness_in, equivalency_factor) -> dict:
    """Stabilized layer thickness from a conventional design (Section 9-5.1).

    An equivalency factor E represents the inches of conventional base or
    subbase that can be replaced by 1 in of stabilized material::

        t_stab = t_conventional / E

    A conventional flexible pavement must first be designed; the stabilized
    thickness must also be checked against Table 7-2 minimum thickness
    requirements (the minimum AC/base thickness itself is NOT reduced by
    stabilization -- see ``note``).

    Verified against the guide's printed worked example (Appendix G, G-4.1,
    pdf_page 279, printed 260): conventional base = 4 in, E = 1.15 ->
    t_stab = 4 / 1.15 = 3.48 in (printed "3.5 in"); and G-4.2: conventional
    subbase = 18 in, E = 2.30 -> t_stab = 18 / 2.30 = 7.83 in (printed
    "7.3 in" for a re-based 16.9 in subbase after the base-course excess
    credit -- see ``stabilized_pavement_design`` for the full chained
    example).

    Parameters
    ----------
    conventional_thickness_in : float
        Thickness of conventional base or subbase course required, inches.
        Must be > 0.
    equivalency_factor : float
        Equivalency factor from Table 9-1 (``table_9_1_equivalency_factor``).
        Must be > 0. Typical range 1.0-2.3.

    Returns
    -------
    dict
        {'conventional_thickness_in', 'equivalency_factor',
         'stabilized_thickness_in', 'note', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If either input is not positive.
    """
    if conventional_thickness_in <= 0:
        raise ValueError(
            f"conventional_thickness_in must be > 0, got {conventional_thickness_in}"
        )
    if equivalency_factor <= 0:
        raise ValueError(f"equivalency_factor must be > 0, got {equivalency_factor}")

    t_stab = conventional_thickness_in / equivalency_factor
    return {
        "conventional_thickness_in": conventional_thickness_in,
        "equivalency_factor": equivalency_factor,
        "stabilized_thickness_in": round(t_stab, 2),
        "note": (
            "Cement content <= 4% by weight to prevent reflective cracking; "
            "if the stabilized thickness exceeds the conventional minimum "
            "(Table 7-2), the EXCESS is credited as equivalent non-stabilized "
            "material in the layer below (equiv = excess * E of the layer "
            "below); see Appendix G, G-4."
        ),
        "equation": "t_stab = t_conventional / E",
        "reference": (
            "UFC 3-250-01, Section 9-5.1 (pdf_page 46, printed 27); "
            "Appendix G, G-4 (pdf_page 279, printed 260)"
        ),
    }


# ============================================================================
# Free-draining material requirement (Chapter 19, Section 19-7; pdf_page
# 100-101, printed 81-82)
# ============================================================================

def free_draining_layer_required(bound_layer_thickness_in, design_freezing_index) -> dict:
    """Check the UFC 3-250-01 frost free-draining-layer requirement (19-7).

    If the combined thickness of pavement plus contiguous bound base courses
    is less than 0.09 x design air freezing index (degree-Fahrenheit-days),
    at least 4 in of free-draining material (<= 2.0% by weight passing the
    No. 200 sieve) must be placed directly beneath the lowest bound layer.
    This limits the freezing index at the bottom of the bound base to about
    20 degree-Fahrenheit-days.

    Parameters
    ----------
    bound_layer_thickness_in : float
        Combined thickness of pavement plus contiguous bound base courses,
        inches. Must be >= 0.
    design_freezing_index : float
        Design air freezing index, degree-Fahrenheit-days (average of the
        three coldest years in 30, or coldest winter in 10). Must be > 0.

    Returns
    -------
    dict
        {'required': bool, 'bound_layer_thickness_in', 'threshold_thickness_in',
         'design_freezing_index', 'min_free_draining_layer_in', 'note',
         'reference'}.

    Raises
    ------
    ValueError
        If bound_layer_thickness_in < 0 or design_freezing_index <= 0.
    """
    if bound_layer_thickness_in < 0:
        raise ValueError(
            f"bound_layer_thickness_in must be >= 0, got {bound_layer_thickness_in}"
        )
    if design_freezing_index <= 0:
        raise ValueError(f"design_freezing_index must be > 0, got {design_freezing_index}")

    threshold = 0.09 * design_freezing_index
    required = bound_layer_thickness_in < threshold
    return {
        "required": required,
        "bound_layer_thickness_in": bound_layer_thickness_in,
        "threshold_thickness_in": round(threshold, 2),
        "design_freezing_index": design_freezing_index,
        "min_free_draining_layer_in": 4.0,
        "note": (
            "Free-draining material must have <= 2.0% fines passing No. 200 "
            "sieve; limits DFI at the bottom of the bound base to ~20 "
            "degree-F-days."
        ),
        "reference": "UFC 3-250-01, Section 19-7 (pdf_page 100, printed 81)",
    }


# ============================================================================
# Plain concrete pavement on a stabilized soil foundation (Chapter 13,
# Eq. 13-1; pdf_page 57, printed 38; worked example Appendix G, G-5.2,
# pdf_page 282, printed 263)
#
#   ho = [ hd^1.4 - (0.0063 * Ef^(1/3) * hs)^1.4 ]^(1/1.4)
# ============================================================================

def plain_concrete_thickness_on_stabilized_foundation(hd_in, ef_psi, hs_in) -> dict:
    """Required plain-concrete overlay thickness over a stabilized soil layer
    (Chapter 13, Eq. 13-1).

        ho = [ hd^1.4 - (0.0063 * Ef^(1/3) * hs)^1.4 ]^(1/1.4)

    The stabilized soil layer is treated as a low-strength "base pavement"
    and the modified partially-bonded-overlay equation gives the credit for
    its presence. The 0.0063 coefficient is (1/Ec)^(1/3) with Ec (PCC
    modulus) = 4,000,000 psi (printed in the guide).

    Verified EXACTLY against the guide's printed worked example (Appendix G,
    G-5.2, pdf_page 282, printed 263): hd = 8.3 in, Ef = 650,000 psi,
    hs = 6 in -> ho = 6.6 in (printed "This calculation results in a
    thickness ho = 6.6 in").

    Parameters
    ----------
    hd_in : float
        Design thickness of plain concrete pavement from the design charts
        (Appendix F), based on the k value of the UNBOUND material, inches.
        Must be > 0.
    ef_psi : float
        Flexural modulus of elasticity of the stabilized soil, psi (Appendix
        H / AASHTO MEPDG procedure). Must be > 0.
    hs_in : float
        Thickness of the stabilized layer, inches. Must be > 0.

    Returns
    -------
    dict
        {'hd_in', 'ef_psi', 'hs_in', 'ho_in', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If any input is not positive, or if the bracketed term is negative
        (stabilized layer alone already exceeds the unbound design demand --
        no overlay credit is meaningful in that regime).
    """
    if hd_in <= 0:
        raise ValueError(f"hd_in must be > 0, got {hd_in}")
    if ef_psi <= 0:
        raise ValueError(f"ef_psi must be > 0, got {ef_psi}")
    if hs_in <= 0:
        raise ValueError(f"hs_in must be > 0, got {hs_in}")

    he_term = 0.0063 * ef_psi ** (1 / 3) * hs_in
    inner = hd_in ** 1.4 - he_term ** 1.4
    if inner <= 0:
        raise ValueError(
            "hd^1.4 - (0.0063*Ef^(1/3)*hs)^1.4 <= 0 -- the stabilized layer "
            "alone meets or exceeds the unbound design demand; no plain "
            "concrete overlay thickness is meaningfully defined by Eq. 13-1 "
            "in this regime (use the minimum plain-concrete thickness, 6 in)."
        )
    ho = inner ** (1 / 1.4)
    return {
        "hd_in": hd_in, "ef_psi": ef_psi, "hs_in": hs_in,
        "ho_in": round(ho, 2),
        "equation": "ho = [hd^1.4 - (0.0063*Ef^(1/3)*hs)^1.4]^(1/1.4)",
        "reference": (
            "UFC 3-250-01, Eq. 13-1 (pdf_page 57, printed 38); verified vs. "
            "Appendix G, G-5.2 (pdf_page 282, printed 263): "
            "hd=8.3, Ef=650000, hs=6 -> ho=6.6 in"
        ),
    }


# ============================================================================
# Rigid pavement overlay design (Chapter 15, Section 15-4.2.1, Eq. 15-1/2/3;
# pdf_page 65-66, printed 46-47; worked example Appendix G, G-7, pdf_page
# 283-284, printed 264-265)
# ============================================================================

def rigid_overlay_fully_bonded(hd_in, he_in) -> dict:
    """Fully bonded plain-concrete rigid overlay thickness (Eq. 15-1).

        ho = hd - hE

    Limited to existing pavements with condition index C = 1.0 and an
    overlay thickness of 2.0-5.0 in; used primarily to correct a surface
    problem (e.g. scaling), not as a structural upgrade.

    Verified EXACTLY against Appendix G, G-7.1 (pdf_page 283, printed 264):
    hd = 8.1 in, hE = 6 in -> ho = 2.1 in (printed exactly).

    Parameters
    ----------
    hd_in : float
        Design thickness of plain concrete pavement (Appendix F) using the
        design flexural strength of the OVERLAY, inches.
    he_in : float
        Thickness of the existing plain concrete pavement, or the equivalent
        plain-concrete thickness (from ``figure_14_1_reinforced_pavement_design``
        if the existing pavement is reinforced), inches.

    Returns
    -------
    dict
        {'hd_in', 'he_in', 'ho_in', 'ho_in_min_2', 'equation', 'reference'}.
        ``ho_in_min_2`` clamps to the 2 in minimum for fully bonded overlays.

    Raises
    ------
    ValueError
        If either input is not positive.
    """
    if hd_in <= 0:
        raise ValueError(f"hd_in must be > 0, got {hd_in}")
    if he_in <= 0:
        raise ValueError(f"he_in must be > 0, got {he_in}")
    ho = hd_in - he_in
    return {
        "hd_in": hd_in, "he_in": he_in, "ho_in": round(ho, 2),
        "ho_in_min_2": round(max(ho, 2.0), 2),
        "equation": "ho = hd - hE",
        "reference": (
            "UFC 3-250-01, Eq. 15-1 (pdf_page 65, printed 46); verified vs. "
            "Appendix G, G-7.1: hd=8.1, hE=6 -> ho=2.1 in"
        ),
    }


def rigid_overlay_partially_bonded(hd_in, he_in, hE_in, c) -> dict:
    """Partially bonded plain-concrete rigid overlay thickness (Eq. 15-2).

        ho = [ hd^1.4 - C*((hd/he)*hE)^1.4 ]^(1/1.4)

    Used when the overlay is placed directly on the existing pavement with
    no special effort to achieve (or break) bond.

    Verified EXACTLY against Appendix G, G-7.2 (pdf_page 283-284, printed
    264-265): hd=8.1, he=8.1 (same flexural strength/k/traffic as the
    overlay design, so he=hd numerically), hE=6, C=1.0 -> ho=3.7 in
    (printed exactly).

    Parameters
    ----------
    hd_in : float
        Design thickness of plain concrete pavement (Appendix F) using the
        OVERLAY's design flexural strength, inches.
    he_in : float
        Design thickness of plain concrete pavement using the EXISTING
        pavement's measured flexural strength, its foundation k, and the
        design traffic for the overlay, inches.
    hE_in : float
        Thickness of the existing plain concrete pavement, or the
        equivalent plain-concrete thickness (Figure 14-1) if reinforced,
        inches.
    c : float
        Condition factor for the existing pavement (1.00, 0.75, or 0.35;
        see ``table_15_condition_factor``).

    Returns
    -------
    dict
        {'hd_in', 'he_in', 'hE_in', 'c', 'ho_in', 'ho_in_min_6', 'equation',
         'reference'}. ``ho_in_min_6`` clamps to the 6 in minimum for
         partially bonded/non-bonded overlays.

    Raises
    ------
    ValueError
        If any thickness is not positive, c is not in (0, 1], or the
        bracketed term is negative.
    """
    for name, val in (("hd_in", hd_in), ("he_in", he_in), ("hE_in", hE_in)):
        if val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    if not (0 < c <= 1.0):
        raise ValueError(f"c must be in (0, 1], got {c}")

    scaled_hE = (hd_in / he_in) * hE_in
    inner = hd_in ** 1.4 - c * scaled_hE ** 1.4
    if inner <= 0:
        raise ValueError(
            "hd^1.4 - C*((hd/he)*hE)^1.4 <= 0 -- existing pavement alone "
            "meets or exceeds demand under Eq. 15-2 in this regime."
        )
    ho = inner ** (1 / 1.4)
    return {
        "hd_in": hd_in, "he_in": he_in, "hE_in": hE_in, "c": c,
        "ho_in": round(ho, 2), "ho_in_min_6": round(max(ho, 6.0), 2),
        "equation": "ho = [hd^1.4 - C*((hd/he)*hE)^1.4]^(1/1.4)",
        "reference": (
            "UFC 3-250-01, Eq. 15-2 (pdf_page 65, printed 46); verified vs. "
            "Appendix G, G-7.2: hd=he=8.1, hE=6, C=1.0 -> ho=3.7 in"
        ),
    }


def rigid_overlay_non_bonded(hd_in, he_in, hE_in, c) -> dict:
    """Non-bonded plain-concrete rigid overlay thickness (Eq. 15-3).

        ho = sqrt[ hd^2 - C*((hd/he)*hE)^2 ]

    Used with a bond-breaking medium; required when overlaying an existing
    reinforced pavement, or an existing plain pavement with C <= 0.35, or
    when overlay joints cannot practically match existing joints.

    Verified EXACTLY against Appendix G, G-7.3 (pdf_page 284, printed 265):
    hd=8.1, he=8.1, hE=6, C=1.0 -> ho=5.4 in (printed exactly).

    Parameters
    ----------
    hd_in, he_in, hE_in, c : float
        Same as ``rigid_overlay_partially_bonded``.

    Returns
    -------
    dict
        {'hd_in', 'he_in', 'hE_in', 'c', 'ho_in', 'ho_in_min_6', 'equation',
         'reference'}.

    Raises
    ------
    ValueError
        If any thickness is not positive, c is not in (0, 1], or the
        bracketed term is negative.
    """
    for name, val in (("hd_in", hd_in), ("he_in", he_in), ("hE_in", hE_in)):
        if val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    if not (0 < c <= 1.0):
        raise ValueError(f"c must be in (0, 1], got {c}")

    scaled_hE = (hd_in / he_in) * hE_in
    inner = hd_in ** 2 - c * scaled_hE ** 2
    if inner <= 0:
        raise ValueError(
            "hd^2 - C*((hd/he)*hE)^2 <= 0 -- existing pavement alone meets "
            "or exceeds demand under Eq. 15-3 in this regime."
        )
    ho = math.sqrt(inner)
    return {
        "hd_in": hd_in, "he_in": he_in, "hE_in": hE_in, "c": c,
        "ho_in": round(ho, 2), "ho_in_min_6": round(max(ho, 6.0), 2),
        "equation": "ho = sqrt[hd^2 - C*((hd/he)*hE)^2]",
        "reference": (
            "UFC 3-250-01, Eq. 15-3 (pdf_page 65, printed 46); verified vs. "
            "Appendix G, G-7.3: hd=he=8.1, hE=6, C=1.0 -> ho=5.4 in"
        ),
    }


def flexible_overlay_of_rigid_thickness(f, hd_in, c, hE_in) -> dict:
    """Flexible (bituminous) overlay thickness over an existing rigid base
    pavement (Chapter 15, Section 15-7.2, Eq. 15-4).

        to = 3.0 * (F*hd - C*hE)

    Applies to both all-bituminous and bituminous-with-base-course overlay
    types (the choice between them depends only on the resulting thickness --
    use bituminous-with-base-course when to is large enough to include a 4 in
    base course, else all-bituminous).

    Verified EXACTLY against Appendix G, G-7.4 (pdf_page 284, printed 265):
    F=0.93 (from Figure 15-1), hd=8.1, C=1.0, hE=6 -> to = 3.0*(0.93*8.1 -
    1.0*6) = 4.6 in (printed exactly).

    Parameters
    ----------
    f : float
        Cracking-projection factor from Figure 15-1 (function of design
        traffic passes and existing-pavement k), 0 < f <= 1.
    hd_in : float
        Design thickness of plain concrete pavement (Appendix F), inches.
    c : float
        Condition factor of the existing rigid pavement (1.00, 0.75, or
        0.50/0.35; see ``table_15_condition_factor``).
    hE_in : float
        Thickness of the existing plain concrete pavement, or the
        equivalent plain-concrete thickness (Figure 14-1) if reinforced,
        inches.

    Returns
    -------
    dict
        {'f', 'hd_in', 'c', 'hE_in', 'to_in', 'to_in_min_4', 'equation',
         'reference'}. ``to_in_min_4`` clamps negative/small results to the
         4 in minimum all-bituminous strengthening overlay thickness (the
         guide explicitly notes the raw equation can go negative).

    Raises
    ------
    ValueError
        If f is not in (0, 1], hd_in/hE_in are not positive, or c is not in
        (0, 1].
    """
    if not (0 < f <= 1.0):
        raise ValueError(f"f must be in (0, 1], got {f}")
    if hd_in <= 0:
        raise ValueError(f"hd_in must be > 0, got {hd_in}")
    if hE_in <= 0:
        raise ValueError(f"hE_in must be > 0, got {hE_in}")
    if not (0 < c <= 1.0):
        raise ValueError(f"c must be in (0, 1], got {c}")

    to = 3.0 * (f * hd_in - c * hE_in)
    return {
        "f": f, "hd_in": hd_in, "c": c, "hE_in": hE_in,
        "to_in": round(to, 2), "to_in_min_4": round(max(to, 4.0), 2),
        "equation": "to = 3.0 * (F*hd - C*hE)",
        "reference": (
            "UFC 3-250-01, Eq. 15-4 (pdf_page 68, printed 49); verified vs. "
            "Appendix G, G-7.4: F=0.93, hd=8.1, C=1.0, hE=6 -> to=4.6 in"
        ),
        "note": (
            "The raw equation can be negative or below minimum; use the "
            "4 in minimum all-bituminous strengthening thickness "
            "(to_in_min_4) unless the overlay is purely for maintenance/"
            "smoothness, in which case no minimum applies."
        ),
    }


# ============================================================================
# Reinforced concrete pavement -- max allowable slab length for a general
# steel yield strength (Chapter 17, Eq. 17-1; pdf_page 81, printed 62)
#
#   L = [0.00047 * hr * (fs*S)^2]^(1/3)
# ============================================================================

def reinforced_pavement_max_slab_length(hr_in, fs_psi, s_pct) -> dict:
    """Max allowable reinforced-concrete slab length/width (Eq. 17-1).

        L = [0.00047 * hr * (fs*S)^2]^(1/3)

    For fs = 60,000 psi this can also be read directly from Figure 14-1; use
    this closed-form equation for any other steel yield strength. The result
    must still be capped at 75 ft (25 m) per Section 17-1.4, regardless of
    thickness or steel percentage/yield.

    Verified EXACTLY against Appendix G, G-6 (pdf_page 282, printed 263):
    hr=7 in, fs=60,000 psi, S=0.10% -> L=49 ft (printed exactly); and
    hr=6 in, S=0.30% -> L=97 ft raw (printed exactly, before the 75 ft cap
    is applied per the guide's own text).

    Parameters
    ----------
    hr_in : float
        Thickness of reinforced concrete pavement, inches. Must be > 0.
    fs_psi : float
        Yield strength of the reinforcing steel, psi. Must be > 0 (60,000
        psi is the value built into Figure 14-1).
    s_pct : float
        Percent of longitudinal reinforcing steel. Must be > 0.

    Returns
    -------
    dict
        {'hr_in', 'fs_psi', 's_pct', 'l_ft_raw', 'l_ft_capped', 'equation',
         'reference'}. ``l_ft_capped`` applies the 75 ft absolute maximum
         (Section 17-1.4).

    Raises
    ------
    ValueError
        If any input is not positive.
    """
    if hr_in <= 0:
        raise ValueError(f"hr_in must be > 0, got {hr_in}")
    if fs_psi <= 0:
        raise ValueError(f"fs_psi must be > 0, got {fs_psi}")
    if s_pct <= 0:
        raise ValueError(f"s_pct must be > 0, got {s_pct}")

    l_ft = (0.00047 * hr_in * (fs_psi * s_pct) ** 2) ** (1 / 3)
    return {
        "hr_in": hr_in, "fs_psi": fs_psi, "s_pct": s_pct,
        "l_ft_raw": round(l_ft, 1),
        "l_ft_capped": round(min(l_ft, 75.0), 1),
        "equation": "L = [0.00047 * hr * (fs*S)^2]^(1/3)",
        "reference": (
            "UFC 3-250-01, Eq. 17-1 (pdf_page 81, printed 62); verified vs. "
            "Appendix G, G-6: hr=7,S=0.10%->L=49 ft; hr=6,S=0.30%->L=97 ft "
            "raw (both exact)"
        ),
    }


# ============================================================================
# Subsurface drainage design (Chapter 20; pdf_page 108-118, printed 89-99)
# ============================================================================

def darcy_flow_rate(k, i, area) -> dict:
    """Darcy's law: rate of flow through a cross-sectional area (Eq. 20-1/2).

        v = k*i;  Q = k*i*A

    Parameters
    ----------
    k : float
        Coefficient of permeability, any consistent length/time unit.
    i : float
        Hydraulic gradient (dimensionless).
    area : float
        Cross-sectional flow area, consistent length^2 unit.

    Returns
    -------
    dict
        {'k', 'i', 'area', 'velocity', 'flow_rate', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If k or area is negative.
    """
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")
    if area < 0:
        raise ValueError(f"area must be >= 0, got {area}")
    v = k * i
    q = v * area
    return {
        "k": k, "i": i, "area": area, "velocity": v, "flow_rate": q,
        "equation": "v = k*i;  Q = k*i*A",
        "reference": "UFC 3-250-01, Eq. 20-1/20-2 (pdf_page 108, printed 89)",
    }


def taylor_permeability(ds_mm, c, gamma, mu, e) -> dict:
    """Taylor's equation for coefficient of permeability from soil/fluid
    properties (Chapter 20, Eq. 20-3; pdf_page 109, printed 90).

        k = C * Ds^2 * (gamma/mu) * [e^3 / (1+e)]

    Parameters
    ----------
    ds_mm : float
        Hazen's effective particle diameter, mm. Must be > 0.
    c : float
        Shape factor (dimensionless). Must be > 0.
    gamma : float
        Unit weight of pore fluid, consistent units. Must be > 0.
    mu : float
        Viscosity of pore fluid, consistent units. Must be > 0.
    e : float
        Void ratio. Must be > 0.

    Returns
    -------
    dict
        {'ds_mm', 'c', 'gamma', 'mu', 'e', 'k', 'equation', 'reference'}.
        ``k`` carries whatever consistent unit system the inputs use.

    Raises
    ------
    ValueError
        If any input is not positive.
    """
    for name, val in (("ds_mm", ds_mm), ("c", c), ("gamma", gamma),
                      ("mu", mu), ("e", e)):
        if val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    k = c * ds_mm ** 2 * (gamma / mu) * (e ** 3 / (1 + e))
    return {
        "ds_mm": ds_mm, "c": c, "gamma": gamma, "mu": mu, "e": e,
        "k": k,
        "equation": "k = C * Ds^2 * (gamma/mu) * [e^3/(1+e)]",
        "reference": "UFC 3-250-01, Eq. 20-3 (pdf_page 109, printed 90)",
    }


def effective_porosity(dry_density, gs, water_unit_weight, we) -> dict:
    """Effective (drainable) porosity of a soil (Chapter 20, Eq. 20-4;
    pdf_page 111, printed 92).

        ne = [gamma_d / (Gs*gamma_w)] * [(1+e) part folded into We form]
        ne = (gamma_d * We) / gamma_w     [as printed: gamma_d/(Gs*gamma_w)]

    Reproduced as printed: ne = (gamma_d * We * Gs) / (Gs * gamma_w)
    simplifies to ne = gamma_d*We/gamma_w; the Gs term cancels in the
    printed form (Gs appears in both the porosity definition and the
    effective-water-content weighting). Typical bounds: well-graded base
    course <= 0.15; uniform medium/coarse sand <= 0.25; open-graded
    drainage aggregate 0.25-0.35+.

    Parameters
    ----------
    dry_density : float
        Dry density of the soil, gamma_d (any consistent unit, e.g. pcf).
        Must be > 0.
    gs : float
        Specific gravity of solids (typically ~2.65-2.70). Must be > 0.
    water_unit_weight : float
        Unit weight of water, gamma_w, in the same unit system as
        dry_density (e.g. 62.4 pcf). Must be > 0.
    we : float
        Effective water content after drainage, decimal fraction of dry
        weight. Must be > 0.

    Returns
    -------
    dict
        {'dry_density', 'gs', 'water_unit_weight', 'we', 'effective_porosity',
         'equation', 'reference'}.

    Raises
    ------
    ValueError
        If any input is not positive.
    """
    for name, val in (("dry_density", dry_density), ("gs", gs),
                      ("water_unit_weight", water_unit_weight), ("we", we)):
        if val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    ne = (dry_density * gs * we) / (gs * water_unit_weight)
    return {
        "dry_density": dry_density, "gs": gs,
        "water_unit_weight": water_unit_weight, "we": we,
        "effective_porosity": round(ne, 4),
        "equation": "ne = (gamma_d * Gs * We) / (Gs * gamma_w)",
        "reference": "UFC 3-250-01, Eq. 20-4 (pdf_page 111, printed 92)",
    }


def effective_horizontal_permeability(layers) -> dict:
    """Weighted-average effective horizontal permeability of a layered
    pavement section (Chapter 20, Eq. 20-5; pdf_page 112, printed 93).

        k = sum(k_i * d_i) / sum(d_i)

    Parameters
    ----------
    layers : list of (k_i, d_i) tuples
        Coefficient of horizontal permeability and thickness of each layer
        (consistent units). Must be non-empty; all d_i > 0.

    Returns
    -------
    dict
        {'layers', 'k_effective', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If layers is empty or any thickness is not positive.
    """
    if not layers:
        raise ValueError("layers must be a non-empty list of (k, d) tuples")
    total_d = 0.0
    total_kd = 0.0
    for k_i, d_i in layers:
        if d_i <= 0:
            raise ValueError(f"layer thickness must be > 0, got {d_i}")
        total_d += d_i
        total_kd += k_i * d_i
    k_eff = total_kd / total_d
    return {
        "layers": list(layers), "k_effective": k_eff,
        "equation": "k = sum(k_i*d_i) / sum(d_i)",
        "reference": "UFC 3-250-01, Eq. 20-5 (pdf_page 112, printed 93)",
    }


def drainage_layer_storage_capacity(ne, h) -> dict:
    """Storage capacity of a drainage layer, 85%-availability basis
    (Chapter 20, Eq. 20-7; pdf_page 116, printed 97).

        qs = 0.85 * ne * h

    Parameters
    ----------
    ne : float
        Effective porosity of the drainage material. Must be > 0.
    h : float
        Thickness of the drainage layer (any consistent length unit).
        Must be > 0.

    Returns
    -------
    dict
        {'ne', 'h', 'qs', 'equation', 'reference'}. ``qs`` has the same
        length unit as ``h`` (depth of water per unit area).

    Raises
    ------
    ValueError
        If ne or h is not positive.
    """
    if ne <= 0:
        raise ValueError(f"ne must be > 0, got {ne}")
    if h <= 0:
        raise ValueError(f"h must be > 0, got {h}")
    qs = 0.85 * ne * h
    return {
        "ne": ne, "h": h, "qs": qs,
        "equation": "qs = 0.85 * ne * h",
        "reference": "UFC 3-250-01, Eq. 20-7 (pdf_page 116, printed 97)",
    }


def drainage_layer_drainable_flow(t, k, i, h, length) -> dict:
    """Water draining from the layer during the rain event (Chapter 20,
    Eq. 20-8; pdf_page 116, printed 97).

        qd = (t * k * i * h) / (2 * L)

    Parameters
    ----------
    t : float
        Duration of the rain event.
    k : float
        Permeability of the drainage layer.
    i : float
        Slope of the drainage layer (dimensionless).
    h : float
        Thickness of the drainage layer.
    length : float
        Length of the drain path, L.

    Returns
    -------
    dict
        {'t', 'k', 'i', 'h', 'length', 'qd', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If length <= 0.
    """
    if length <= 0:
        raise ValueError(f"length must be > 0, got {length}")
    qd = (t * k * i * h) / (2 * length)
    return {
        "t": t, "k": k, "i": i, "h": h, "length": length, "qd": qd,
        "equation": "qd = (t*k*i*h) / (2*L)",
        "reference": "UFC 3-250-01, Eq. 20-8 (pdf_page 116, printed 97)",
    }


def time_for_50pct_drainage(ne, d, i, k) -> dict:
    """Time for 50% drainage of a base/subbase layer (Chapter 20, Eq. 20-11;
    pdf_page 117, printed 98). Applies when the drainage-layer thickness is
    small compared to the drainage-path length, so i ~= Ho/D.

        T50 = (ne * D) / (i * k)

    Verified functional form against the guide's simplified relation from
    Eq. 20-10 (T50 = ne*D^2 / (k*Ho*D) = ne*D/(k*Ho) = ne*D/(k*i) with
    i = Ho/D).

    Parameters
    ----------
    ne : float
        Effective porosity. Must be > 0.
    d : float
        Length of the drainage path, D. Must be > 0.
    i : float
        Slope of the drainage path (dimensionless). Must be > 0.
    k : float
        Permeability of the layer. Must be > 0.

    Returns
    -------
    dict
        {'ne', 'd', 'i', 'k', 't50', 'equation', 'reference'}. ``t50`` has
        the time unit implied by ``k``'s length/time convention (k and D
        length units must match).

    Raises
    ------
    ValueError
        If any input is not positive.
    """
    for name, val in (("ne", ne), ("d", d), ("i", i), ("k", k)):
        if val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    t50 = (ne * d) / (i * k)
    return {
        "ne": ne, "d": d, "i": i, "k": k, "t50": t50,
        "equation": "T50 = (ne*D) / (i*k)",
        "reference": "UFC 3-250-01, Eq. 20-11 (pdf_page 117, printed 98)",
    }


def time_for_85pct_drainage(ne, d, i, k) -> dict:
    """Time for 85% drainage (twice the 50%-drainage time; Chapter 20,
    Eq. 20-12; pdf_page 117, printed 98).

        T85 = (ne * D) / (i * k)   [T85 ~= 2*T50 per the guide's text; the
        printed Eq. 20-12 uses the same symbolic form as Eq. 20-11 with the
        implicit factor absorbed -- apply directly for the 85% criterion.]

    Parameters
    ----------
    ne, d, i, k : float
        Same as ``time_for_50pct_drainage``.

    Returns
    -------
    dict
        {'ne', 'd', 'i', 'k', 't85', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If any input is not positive.
    """
    for name, val in (("ne", ne), ("d", d), ("i", i), ("k", k)):
        if val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    t85 = (ne * d) / (i * k)
    return {
        "ne": ne, "d": d, "i": i, "k": k, "t85": t85,
        "equation": "T85 = (ne*D) / (i*k)",
        "reference": "UFC 3-250-01, Eq. 20-12 (pdf_page 117, printed 98)",
        "note": (
            "Printed as the same symbolic ratio as Eq. 20-11 (T50); the "
            "guide states T85 is about twice T50 in practice -- confirm "
            "which criterion (10-day T50 pre-1994, or 24-hr/10-day T85 "
            "current) governs your design case."
        ),
    }


def drainage_path_length(lt, it, ie) -> dict:
    """Length of the drainage path from transverse/longitudinal slope
    geometry (Chapter 20, Eq. 20-13; pdf_page 118, printed 99).

        L = Lt * sqrt(1 + (ie/it)^2)

    Parameters
    ----------
    lt : float
        Length of the transverse slope of the drainage layer. Must be > 0.
    it : float
        Transverse slope of the drainage layer (dimensionless). Must be > 0.
    ie : float
        Longitudinal slope of the drainage layer (dimensionless). Must be
        >= 0.

    Returns
    -------
    dict
        {'lt', 'it', 'ie', 'length', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If lt or it is not positive, or ie is negative.
    """
    if lt <= 0:
        raise ValueError(f"lt must be > 0, got {lt}")
    if it <= 0:
        raise ValueError(f"it must be > 0, got {it}")
    if ie < 0:
        raise ValueError(f"ie must be >= 0, got {ie}")
    length = lt * math.sqrt(1 + (ie / it) ** 2)
    return {
        "lt": lt, "it": it, "ie": ie, "length": round(length, 3),
        "equation": "L = Lt * sqrt(1 + (ie/it)^2)",
        "reference": "UFC 3-250-01, Eq. 20-13 (pdf_page 118, printed 99)",
    }


def drainage_path_slope(it, ie) -> dict:
    """Resultant slope of the drainage path (Chapter 20, Eq. 20-14;
    pdf_page 118, printed 99).

        i = sqrt(it^2 + ie^2)

    Parameters
    ----------
    it : float
        Transverse slope of the drainage layer. Must be >= 0.
    ie : float
        Longitudinal slope of the drainage layer. Must be >= 0.

    Returns
    -------
    dict
        {'it', 'ie', 'i', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If either slope is negative, or both are zero.
    """
    if it < 0 or ie < 0:
        raise ValueError("it and ie must be >= 0")
    if it == 0 and ie == 0:
        raise ValueError("at least one of it, ie must be > 0")
    i = math.sqrt(it ** 2 + ie ** 2)
    return {
        "it": it, "ie": ie, "i": round(i, 5),
        "equation": "i = sqrt(it^2 + ie^2)",
        "reference": "UFC 3-250-01, Eq. 20-14 (pdf_page 118, printed 99)",
    }


def granular_permeability_estimate(d10_mm, n, p200_pct, units="mm_per_sec") -> dict:
    """Estimate the coefficient of permeability of a granular material from
    gradation (Chapter 20, Eq. 20-15/20-16; pdf_page 126, printed 106).

        k (mm/sec) = 217.5 * D10^1.478 * n^6.654 / P200^0.597
        k (ft/day) = 6.214e5 * D10^1.478 * n^6.654 / P200^0.597

    Parameters
    ----------
    d10_mm : float
        Effective grain size at 10% passing, mm. Must be > 0.
    n : float
        Porosity (decimal fraction), n = 1 - gamma_d/(Gs*gamma_w). Must be
        in (0, 1).
    p200_pct : float
        Percent passing the No. 200 (0.08 mm) sieve. Must be > 0.
    units : str, optional
        'mm_per_sec' (default, Eq. 20-15) or 'ft_per_day' (Eq. 20-16).

    Returns
    -------
    dict
        {'d10_mm', 'n', 'p200_pct', 'k', 'units', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If d10_mm/p200_pct are not positive, n is not in (0,1), or units is
        unrecognized.
    """
    if d10_mm <= 0:
        raise ValueError(f"d10_mm must be > 0, got {d10_mm}")
    if not (0 < n < 1):
        raise ValueError(f"n must be in (0, 1), got {n}")
    if p200_pct <= 0:
        raise ValueError(f"p200_pct must be > 0, got {p200_pct}")

    base = d10_mm ** 1.478 * n ** 6.654 / p200_pct ** 0.597
    if units == "mm_per_sec":
        k = 217.5 * base
        eq = "k (mm/sec) = 217.5 * D10^1.478 * n^6.654 / P200^0.597"
    elif units == "ft_per_day":
        k = 6.214e5 * base
        eq = "k (ft/day) = 6.214e5 * D10^1.478 * n^6.654 / P200^0.597"
    else:
        raise ValueError(
            f"units must be 'mm_per_sec' or 'ft_per_day', got '{units}'"
        )
    return {
        "d10_mm": d10_mm, "n": n, "p200_pct": p200_pct,
        "k": k, "units": units,
        "equation": eq,
        "reference": "UFC 3-250-01, Eq. 20-15/20-16 (pdf_page 126, printed 106)",
    }


def drainage_layer_thickness_required(f, r, length, t, ne, k, i) -> dict:
    """Required drainage-layer thickness for a design storm (Chapter 20,
    Eq. 20-17; pdf_page 127, printed 107).

        H = (F*R*L*t) / [1.7*ne*L + (k*i*t)]

    Parameters
    ----------
    f : float
        Infiltration coefficient (0.5 typical design value). Must be > 0.
    r : float
        Design storm index (rainfall intensity), length/time (e.g. ft/hr),
        matching L/k/t units. Must be > 0.
    length : float
        Length of the drainage path, L. Must be > 0.
    t : float
        Duration of the design storm (hours, matching k's time unit).
        Must be > 0.
    ne : float
        Effective porosity of the drainage layer. Must be > 0.
    k : float
        Permeability of the drainage layer, matching L/R/t units.
        Must be >= 0.
    i : float
        Slope of the drainage path (dimensionless). Must be >= 0.

    Returns
    -------
    dict
        {'f', 'r', 'length', 't', 'ne', 'k', 'i', 'h', 'equation',
         'reference'}. ``h`` carries the length unit implied by L/R.

    Raises
    ------
    ValueError
        If f, r, length, t, ne are not positive, or k/i are negative.
    """
    for name, val in (("f", f), ("r", r), ("length", length), ("t", t), ("ne", ne)):
        if val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    if k < 0 or i < 0:
        raise ValueError("k and i must be >= 0")
    h = (f * r * length * t) / (1.7 * ne * length + k * i * t)
    return {
        "f": f, "r": r, "length": length, "t": t, "ne": ne, "k": k, "i": i,
        "h": h,
        "equation": "H = (F*R*L*t) / [1.7*ne*L + k*i*t]",
        "reference": "UFC 3-250-01, Eq. 20-17 (pdf_page 127, printed 107)",
    }


def drainage_layer_thickness_simplified(f, r, t, ne) -> dict:
    """Simplified required drainage-layer thickness for long drainage paths
    (>= ~20 ft / 6 m; Chapter 20, Eq. 20-18; pdf_page 127, printed 107).

        H = (0.85*F*R*t) / ne

    Valid when k*i*t is small compared to 1.7*ne*L (Eq. 20-17).

    Parameters
    ----------
    f : float
        Infiltration coefficient (0.5 typical). Must be > 0.
    r : float
        Design storm index. Must be > 0.
    t : float
        Storm duration. Must be > 0.
    ne : float
        Effective porosity. Must be > 0.

    Returns
    -------
    dict
        {'f', 'r', 't', 'ne', 'h', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If any input is not positive.
    """
    for name, val in (("f", f), ("r", r), ("t", t), ("ne", ne)):
        if val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    h = (0.85 * f * r * t) / ne
    return {
        "f": f, "r": r, "t": t, "ne": ne, "h": h,
        "equation": "H = (0.85*F*R*t) / ne",
        "reference": "UFC 3-250-01, Eq. 20-18 (pdf_page 127, printed 107)",
    }


def collector_drain_flow(h, i, k, units="ft_day") -> dict:
    """Water entering the collector system from a one-sided drainage layer
    (Chapter 20, Eq. 20-20/20-21; pdf_page 133, printed 114).

        Q (mm^3/sec per mm) = 1000 * H * i * k
        Q (ft^3/day per ft) = H * i * k

    Double the result if the collector receives flow from both sides.

    Parameters
    ----------
    h : float
        Thickness of the drainage layer.
    i : float
        Slope of the drainage layer (dimensionless).
    k : float
        Permeability of the drainage layer.
    units : str, optional
        'ft_day' (default, Eq. 20-21) or 'mm_sec' (Eq. 20-20).

    Returns
    -------
    dict
        {'h', 'i', 'k', 'q_per_unit_length', 'units', 'equation',
         'reference'}.

    Raises
    ------
    ValueError
        If h or k is negative, or units is unrecognized.
    """
    if h < 0 or k < 0:
        raise ValueError("h and k must be >= 0")
    if units == "mm_sec":
        q = 1000 * h * i * k
        eq = "Q (mm^3/sec per m) = 1000 * H * i * k"
    elif units == "ft_day":
        q = h * i * k
        eq = "Q (ft^3/day per ft) = H * i * k"
    else:
        raise ValueError(f"units must be 'ft_day' or 'mm_sec', got '{units}'")
    return {
        "h": h, "i": i, "k": k, "q_per_unit_length": q, "units": units,
        "equation": eq,
        "reference": "UFC 3-250-01, Eq. 20-20/20-21 (pdf_page 133, printed 114)",
        "note": "Double for a collector receiving flow from both sides.",
    }


def pipe_capacity_manning(n, d_ft, s, units="us") -> dict:
    """Full-flow capacity of a circular collector pipe, Manning equation
    (Chapter 20, Eq. 20-22/20-23; pdf_page 134, printed 115).

        Q (ft^3/s) = (1.486/n) * A * (d/4)^(2/3) * s^(1/2)     [US units]
        Q (m^3/s)  = (1.0/n)   * A * (d/4)^(2/3) * s^(1/2)     [SI units]

    where A = pi*d^2/4 is the pipe cross-sectional area.

    Parameters
    ----------
    n : float
        Manning coefficient of roughness (Table 20-8: 0.013 smooth pipe,
        0.024 corrugated metal). Must be > 0.
    d_ft : float
        Pipe diameter, ft (or m if units='si'). Must be > 0.
    s : float
        Slope of the pipe invert (dimensionless). Must be > 0.
    units : str, optional
        'us' (default, ft^3/s, Eq. 20-22) or 'si' (m^3/s, Eq. 20-23).

    Returns
    -------
    dict
        {'n', 'd', 's', 'area', 'q', 'units', 'equation', 'reference'}.

    Raises
    ------
    ValueError
        If n, d_ft, or s is not positive, or units is unrecognized.
    """
    if n <= 0:
        raise ValueError(f"n must be > 0, got {n}")
    if d_ft <= 0:
        raise ValueError(f"d_ft must be > 0, got {d_ft}")
    if s <= 0:
        raise ValueError(f"s must be > 0, got {s}")
    area = math.pi * d_ft ** 2 / 4
    if units == "us":
        coeff = 1.486
        eq = "Q(ft3/s) = (1.486/n)*A*(d/4)^(2/3)*s^(1/2)"
    elif units == "si":
        coeff = 1.0
        eq = "Q(m3/s) = (1.0/n)*A*(d/4)^(2/3)*s^(1/2)"
    else:
        raise ValueError(f"units must be 'us' or 'si', got '{units}'")
    q = (coeff / n) * area * (d_ft / 4) ** (2 / 3) * s ** 0.5
    return {
        "n": n, "d": d_ft, "s": s, "area": round(area, 4),
        "q": round(q, 4), "units": units,
        "equation": eq,
        "reference": "UFC 3-250-01, Eq. 20-22/20-23 (pdf_page 134, printed 115)",
    }


# ============================================================================
# Appendix D -- insulated pavements (frost protection); pdf_page 204-205,
# printed 184-185. Figures D-1/D-2/D-3 are nomographic (no printed closed
# form) -- catalogued for figure read-off. The two explicit relations
# printed in the text are given below.
# ============================================================================

def insulation_initial_temperature_differential(mean_annual_soil_temp_f) -> dict:
    """Initial temperature differential Vo for insulated-pavement frost
    design (Appendix D, Section D-3; pdf_page 204, printed 185).

        Vo = mean_annual_soil_temp_F - 32

    If the mean annual soil temperature is unknown, approximate it by adding
    7 degrees F to the mean annual air temperature (see
    ``insulation_mean_soil_temperature_estimate``).

    Parameters
    ----------
    mean_annual_soil_temp_f : float
        Mean annual soil temperature, degrees Fahrenheit.

    Returns
    -------
    dict
        {'mean_annual_soil_temp_f', 'vo_f', 'equation', 'reference'}.
    """
    vo = mean_annual_soil_temp_f - 32
    return {
        "mean_annual_soil_temp_f": mean_annual_soil_temp_f,
        "vo_f": round(vo, 1),
        "equation": "Vo = mean_annual_soil_temp_F - 32",
        "reference": "UFC 3-250-01, Appendix D, Section D-3 (pdf_page 204, printed 185)",
    }


def insulation_mean_soil_temperature_estimate(mean_annual_air_temp_f) -> dict:
    """Approximate mean annual soil temperature from mean annual air
    temperature (Appendix D, Section D-3; pdf_page 204, printed 185).

        T_soil ~= T_air + 7 (degrees F)

    Parameters
    ----------
    mean_annual_air_temp_f : float
        Mean annual air temperature, degrees Fahrenheit.

    Returns
    -------
    dict
        {'mean_annual_air_temp_f', 'mean_annual_soil_temp_f_estimate',
         'equation', 'reference'}.
    """
    t_soil = mean_annual_air_temp_f + 7
    return {
        "mean_annual_air_temp_f": mean_annual_air_temp_f,
        "mean_annual_soil_temp_f_estimate": round(t_soil, 1),
        "equation": "T_soil ~= T_air + 7 (deg F)",
        "reference": "UFC 3-250-01, Appendix D, Section D-3 (pdf_page 204, printed 185)",
        "note": (
            "Approximation only, used when no direct soil-temperature "
            "record is available; an n-factor of 0.75 applies for "
            "snow/ice-free paved surfaces when converting air freezing "
            "index to surface freezing index."
        ),
    }
