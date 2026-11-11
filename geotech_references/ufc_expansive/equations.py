"""UFC 3-220-07 expansive soil equations.

From UFC 3-220-07, Foundations in Expansive Soils (the reproduced
TM 5-818-7), docs/ufc_3_220_07.pdf: total swell as the area under the
per cent swell versus depth curve, Figure 5-4 (printed p. 5-7, PDF 42),
the four relations of Table 4-2, "Other Empirical Methods for
Prediction of Potential Heave" (printed p. 4-3, PDF 33), Van Der Merwe's
total heave, Eq. 4-1 with Figure 4-1 (printed p. 4-1 to 4-2), the
potential vertical heave from void ratios, Eq. 5-2 (p. 5-2), the
equilibrium pore water pressure profiles, Eqs. 5-3 to 5-5 (p. 5-3 to
5-4), and the heave from a consolidometer test, Eqs. 5-8 and 5-9 (p. 5-5).

Rebuilt from the print 2026-11-10 (review pave-13): activity_index
(Skempton), free_swell_percent (Seed et al. 1962), swell_pressure_kPa
(Komornik and David, with LL taken as PI + 20) and
pier_minimum_embedment_m (1.5 times the active zone) were removed; none
is printed in this manual.
"""

import math

_REF = "UFC 3-220-07 (TM 5-818-7)"
_M_TO_FT = 1.0 / 0.3048
_T42 = f"{_REF}, Table 4-2, printed p. 4-3 (PDF 33)"
_T42_NOTE = ("Table 4-2 footnote a: Sp = percent swell; LL = liquid limit in "
             "percent; PI = plasticity index in percent; wo = initial water "
             "content in percent; H = depth of soil in feet.")


def _nonneg(name, v):
    if v is None or v < 0:
        raise ValueError(f"{name} must be >= 0, got {v}")


def table_4_2_swell_vijayvergiya_ghazzaly(liquid_limit, initial_water_content):
    """Potential swell Sp (percent) by Vijayvergiya and Ghazzaly, UFC 3-220-07
    Table 4-2 (printed p. 4-3, PDF 33), from initial water content to
    saturation for 0.1-tsf surcharge pressure.

    As printed::

        Log Sp = 1/12(0.44LL - wo + 5.5)

    Parameters
    ----------
    liquid_limit : float
        Liquid limit LL, percent.
    initial_water_content : float
        Initial water content wo, percent.

    Returns
    -------
    dict
        Keys: potential_swell_pct, log_sp, condition, equation, note,
        reference, and the inputs.

    Raises
    ------
    ValueError
        If an input is negative.
    """
    _nonneg("liquid_limit", liquid_limit)
    _nonneg("initial_water_content", initial_water_content)
    log_sp = (0.44 * liquid_limit - initial_water_content + 5.5) / 12.0
    return {
        "liquid_limit": liquid_limit,
        "initial_water_content": initial_water_content,
        "log_sp": round(log_sp, 4),
        "potential_swell_pct": round(10.0 ** log_sp, 3),
        "condition": ("from initial water content to saturation for 0.1-tsf "
                      "surcharge pressure"),
        "equation": "Log Sp = 1/12(0.44LL - wo + 5.5)",
        "note": _T42_NOTE,
        "reference": _T42,
    }


def table_4_2_swell_schneider_poor(plasticity_index, initial_water_content):
    """Potential swell Sp (percent) by Schneider and Poor, UFC 3-220-07
    Table 4-2 (printed p. 4-3, PDF 33), for no fill or weight on the
    swelling soil to saturation.

    As printed::

        Log Sp = 0.9(PI/wo) - 1.19

    Parameters
    ----------
    plasticity_index : float
        Plasticity index PI, percent.
    initial_water_content : float
        Initial water content wo, percent, > 0.

    Returns
    -------
    dict
        Keys: potential_swell_pct, log_sp, condition, equation, note,
        reference, and the inputs.

    Raises
    ------
    ValueError
        If PI is negative or wo is not positive.
    """
    _nonneg("plasticity_index", plasticity_index)
    if initial_water_content is None or initial_water_content <= 0:
        raise ValueError(
            f"initial_water_content must be > 0, got {initial_water_content}")
    log_sp = 0.9 * (plasticity_index / initial_water_content) - 1.19
    return {
        "plasticity_index": plasticity_index,
        "initial_water_content": initial_water_content,
        "log_sp": round(log_sp, 4),
        "potential_swell_pct": round(10.0 ** log_sp, 3),
        "condition": "for no fill or weight on the swelling soil to saturation",
        "equation": "Log Sp = 0.9(PI/wo) - 1.19",
        "note": _T42_NOTE,
        "reference": _T42,
    }


def _weighted_suction(name, v):
    """A number, or (top, middle, bottom) thirds of the active zone."""
    if isinstance(v, (list, tuple)):
        if len(v) != 3:
            raise ValueError(
                f"{name} as a list must hold 3 suctions (top, middle, bottom "
                f"third of the active zone), got {len(v)}")
        t1, t2, t3 = (float(x) for x in v)
        w = 0.5 * t1 + 0.3 * t2 + 0.2 * t3
    else:
        w = float(v)
    if w <= 0:
        raise ValueError(f"{name} must be > 0, got {v}")
    return w


def table_4_2_swell_mckeen_lytton(suction_compression_index,
                                  final_suction, initial_suction):
    """Potential swell Sp (percent) by the McKeen-Lytton method (by McKeen),
    UFC 3-220-07 Table 4-2 (printed p. 4-3, PDF 33), from the suction
    compression index and the final and initial weighted in situ suctions.

    As printed::

        Sp = -100 gamma_h log10(tau_f / tau_o)

    gamma_h = suction compression index, "found from a chart using the CEC,
    PI, and percent clay" (the chart is not in this manual, so gamma_h is an
    input); tau_f = final weighted in situ suction; tau_o = initial in situ
    weighted suction. "The weighted suction is given by tau = 0.5 tau_1 +
    0.3 tau_2 + 0.2 tau_3 where tau_1, tau_2, and tau_3 are in situ suctions
    measured in the top, middle, and bottom third of the active zone."

    Parameters
    ----------
    suction_compression_index : float
        gamma_h (dimensionless), >= 0.
    final_suction : float or sequence of 3
        tau_f, the final weighted suction, or the three thirds' suctions
        (weighted 0.5/0.3/0.2). Any unit, the same as initial_suction.
    initial_suction : float or sequence of 3
        tau_o, the initial weighted suction, or the three thirds' suctions.

    Returns
    -------
    dict
        Keys: potential_swell_pct, final_weighted_suction,
        initial_weighted_suction, equation, reference, and gamma_h.

    Raises
    ------
    ValueError
        If gamma_h is negative or a suction is not positive.
    """
    _nonneg("suction_compression_index", suction_compression_index)
    tf = _weighted_suction("final_suction", final_suction)
    to = _weighted_suction("initial_suction", initial_suction)
    sp = -100.0 * suction_compression_index * math.log10(tf / to)
    return {
        "suction_compression_index": suction_compression_index,
        "final_weighted_suction": round(tf, 4),
        "initial_weighted_suction": round(to, 4),
        "potential_swell_pct": round(sp, 3),
        "equation": "Sp = -100 gamma_h log10(tau_f / tau_o)",
        "reference": _T42,
    }


def table_4_2_swell_johnson(plasticity_index, depth_ft, initial_water_content):
    """Potential swell Sp (percent) by Johnson, UFC 3-220-07 Table 4-2
    (printed p. 4-3, PDF 33), for 1 psi surcharge pressure to saturation;
    H is the depth of soil in feet. In the PI <= 40 form the scan renders
    the two operators before 0.0432PIwo and 0.01215PIH as "="; they are
    read as minus signs (a judgment call, review pave-13), and the two
    forms then nearly meet at PI 40 (H 10 ft, wo 20: 16.21 against 16.43).
    The result's print_note says so.

    As printed::

        PI >= 40  Sp = 23.82 + 0.7346PI - 0.1458H - 1.7wo
                       + 0.0025PIwo - 0.00884PIH
        PI <= 40  Sp = -9.18 + 1.5546PI + 0.08424H + 0.1wo
                       - 0.0432PIwo - 0.01215PIH

    An "=" cannot stand in either place; read as plus signs, the PI <= 40
    form would give about 95.3 at PI 40 (H 10 ft, wo 20). Both forms are
    printed for PI = 40; at exactly 40 the PI >= 40 form is returned and the other
    value is given in the note (the code's choice).

    Parameters
    ----------
    plasticity_index : float
        PI, percent.
    depth_ft : float
        H, depth of soil, feet.
    initial_water_content : float
        wo, percent.

    Returns
    -------
    dict
        Keys: potential_swell_pct, form ('PI >= 40' or 'PI <= 40'),
        condition, equation, note, print_note, reference, and the inputs.
        A negative value is returned as computed, and the note says it is
        not a predicted shrinkage.

    Raises
    ------
    ValueError
        If an input is negative.
    """
    _nonneg("plasticity_index", plasticity_index)
    _nonneg("depth_ft", depth_ft)
    _nonneg("initial_water_content", initial_water_content)
    pi, h, w = plasticity_index, depth_ft, initial_water_content
    hi = (23.82 + 0.7346 * pi - 0.1458 * h - 1.7 * w
          + 0.0025 * pi * w - 0.00884 * pi * h)
    lo = (-9.18 + 1.5546 * pi + 0.08424 * h + 0.1 * w
          - 0.0432 * pi * w - 0.01215 * pi * h)
    note = _T42_NOTE
    if pi >= 40:
        sp, form = hi, "PI >= 40"
        eq = ("Sp = 23.82 + 0.7346PI - 0.1458H - 1.7wo + 0.0025PIwo "
              "- 0.00884PIH")
        if pi == 40:
            note += (f" PI = 40 is printed under both forms; the PI <= 40 "
                     f"form gives {lo:.3f}.")
    else:
        sp, form = lo, "PI <= 40"
        eq = ("Sp = -9.18 + 1.5546PI + 0.08424H + 0.1wo - 0.0432PIwo "
              "- 0.01215PIH")
    if sp < 0:
        note += (" The relation gives a negative number for these inputs; "
                 "it is not a predicted shrinkage.")
    return {
        "plasticity_index": pi, "depth_ft": h, "initial_water_content": w,
        "potential_swell_pct": round(sp, 3),
        "form": form,
        "condition": "for 1 psi surcharge pressure to saturation",
        "equation": eq,
        "note": note,
        "print_note": ("In the PI <= 40 form the scan renders the two "
                       "operators before 0.0432PIwo and 0.01215PIH as '='; "
                       "they are read as minus signs, and the two forms then "
                       "nearly meet at PI 40 (H 10 ft, wo 20: 16.21 against "
                       "16.43)."),
        "reference": _T42,
    }


def heave_prediction_mm(layers):
    """Total swell (heave) of a soil profile, mm, as the sum of each
    layer's per cent swell times its thickness: the stepwise form of
    UFC 3-220-07 Figure 5-4, "Approximate method for computing foundation
    swell" (printed p. 5-7, PDF 42).

    Figure 5-4 (A), procedure for estimating total swell, as printed:
    "3. Compute swell in terms of per cent of original specimen height and
    plot vs depth. 4. Compute total swell which is equal to area
    encompassed by per cent swell vs depth curve. For example, using
    curves shown above: Total swell = 1/2 x (8.2 - 1.0) x 2.8/100 =
    0.10 ft". The specimens are loaded in the consolidometer to the
    overburden pressure plus the weight of the structure (step 2). This
    function takes the area as a sum of rectangles::

        delta_H = sum(swell_strain_pct_i / 100 * H_i)

    with H_i in metres; delta_H is returned in mm (and in feet, the
    print's unit, as a conversion). One layer of 7.2 ft (2.195 m) at the
    printed triangle's mean 1.4 % gives the printed 0.10 ft.

    Parameters
    ----------
    layers : list of dict
        Each dict must have:
        - thickness_m (float): layer thickness (m)
        - swell_strain_pct (float): swell, per cent of original specimen
          height, under overburden plus structure load (%)

    Returns
    -------
    dict
        Keys: total_heave_mm, total_heave_ft (conversion),
        layer_heaves_mm (list of float), number_of_layers, reference.

    Raises
    ------
    ValueError
        If layers is empty or any value is out of range.
    """
    if not layers:
        raise ValueError("layers list must not be empty")

    layer_heaves = []
    for i, layer in enumerate(layers):
        t = layer["thickness_m"]
        s = layer["swell_strain_pct"]
        if t <= 0:
            raise ValueError(f"Layer {i}: thickness_m must be > 0, got {t}")
        if s < 0:
            raise ValueError(
                f"Layer {i}: swell_strain_pct must be >= 0, got {s}"
            )
        heave_mm = (s / 100.0) * t * 1000.0  # convert m to mm
        layer_heaves.append(round(heave_mm, 1))

    total_mm = round(sum(layer_heaves), 1)
    return {
        "total_heave_mm": total_mm,
        "total_heave_ft": round(total_mm / 1000.0 * _M_TO_FT, 3),
        "layer_heaves_mm": layer_heaves,
        "number_of_layers": len(layers),
        "reference": (f"{_REF}, Figure 5-4 (A) step 4, printed p. 5-7 "
                      "(PDF 42)"),
    }


# ---------------------------------------------------------------------------
# Chapter 4 and 5 heave methods (built 2026-11-10, app backlog REF-91)
# ---------------------------------------------------------------------------

_GAMMA_W_TCF = 0.0312  # unit weight of water, ton per cubic foot (p. 5-3)


def _whole_feet(name, v):
    if v is None or v <= 0 or abs(v - round(v)) > 1e-9:
        raise ValueError(
            f"{name} must be a positive whole number of feet (Eq. 4-1 sums "
            f"1-foot increments), got {v}")
    return int(round(v))


def eq_4_1_van_der_merwe_heave(layers):
    """Total heave at the ground surface, inches, by Van Der Merwe's
    method, UFC 3-220-07 Eq. 4-1 with Figure 4-1 (printed p. 4-1 to 4-2,
    PDF 31-32): the sum over 1-foot depth increments of the surcharge
    reduction factor F = 10^(-D/20) times the potential expansiveness PE
    (inch/foot) read off Figure 4-1 from each soil's PI and clay fraction.

    As printed (para 4-1c)::

        delta_H = sum from D = 1 to D_bar = n of F * PE        (4-1)

    delta_H = total heave, inches; D = depth of soil layer in increments of
    1 foot; D_bar = increment at the deepest level; F = reduction factor
    for surcharge pressure, F = 10^(-D/20); PE = potential expansiveness in
    inch/foot of depth (fig. 4-1). The layers are numbered from the ground
    surface, the first foot being D = 1. Para 4-1e (p. 4-2): the method
    does not need the active zone depth "since computations extend down to
    depths where the computed heaves become negligible", and it tends to
    "give maximum values or may overestimate heave". Para 4-1f(1): "More
    than one identification test should be used"; "estimates of potential
    heave at the ground surface of more than 1/2 inch may require further
    laboratory tests".

    Parameters
    ----------
    layers : list of dict
        From the ground surface down. Each dict: thickness_ft (a whole
        number of feet), plasticity_index (percent, whole sample) and
        clay_fraction_pct (percent finer than 2 microns, whole sample);
        both 0 to 70, Figure 4-1's range.

    Returns
    -------
    dict
        Keys: total_heave_in, depth_ft (n), increments (list of dicts: D,
        level, pe_in_per_ft, F, heave_in), equation, notes, source.

    Raises
    ------
    ValueError
        If layers is empty, a thickness is not a whole number of feet, or
        a PI or clay fraction is outside Figure 4-1's range.

    Example: 10 ft of soil with PI 40 and clay fraction 30 % (very high,
    PE 1 inch/foot) gives the sum of 10^(-D/20) for D = 1 to 10 =
    5.604 in.
    """
    from geotech_references.ufc_expansive.tables import (
        figure_4_1_potential_expansiveness)
    if not layers:
        raise ValueError("layers must not be empty")
    increments = []
    d = 0
    for i, layer in enumerate(layers):
        n_ft = _whole_feet(f"layers[{i}].thickness_ft", layer.get("thickness_ft"))
        fig = figure_4_1_potential_expansiveness(
            layer.get("plasticity_index"), layer.get("clay_fraction_pct"))
        for _ in range(n_ft):
            d += 1
            f = 10.0 ** (-d / 20.0)
            increments.append({
                "D": d, "level": fig["level"],
                "pe_in_per_ft": fig["pe_in_per_ft"],
                "F": round(f, 4), "heave_in": round(f * fig["pe_in_per_ft"], 4),
            })
    total = sum(10.0 ** (-r["D"] / 20.0) * r["pe_in_per_ft"] for r in increments)
    return {
        "total_heave_in": round(total, 3),
        "depth_ft": d,
        "increments": increments,
        "equation": "delta_H (in) = sum_{D=1}^{n} F * PE, F = 10^(-D/20)",
        "notes": [
            "Para 4-1c: the PE values are based on consolidometer swell test "
            "results and field observations; this method does not consider "
            "variations in initial moisture conditions.",
            "Para 4-1e: computations extend down to depths where the "
            "computed heaves become negligible; the Van Der Merwe method "
            "tends to give maximum values or may overestimate heave.",
            "Para 4-1f(1): more than one identification test should be "
            "used; estimates of potential heave at the ground surface of "
            "more than 1/2 inch may require further laboratory tests.",
            _figure_4_1_trace_note(),
        ],
        "source": (f"{_REF}, Eq. 4-1 and Figure 4-1, para 4-1c, printed "
                   "p. 4-1 to 4-2 (PDF 31-32)"),
    }


def _figure_4_1_trace_note():
    from geotech_references.ufc_expansive.tables import _FIG_4_1_TRACE
    return "Figure 4-1: " + _FIG_4_1_TRACE


def eq_5_2_potential_vertical_heave(elements, depth_increment_ft,
                                    vertical_swell_fraction):
    """Potential vertical heave at the bottom of the foundation, feet,
    UFC 3-220-07 Eq. 5-2 (printed p. 5-2, PDF 37): N times the depth
    increment DX times the sum, over the elements from the bottom of the
    foundation to the bottom of the profile, of each element's volumetric
    swell (e_f - e_o)/(1 + e_o).

    As printed (para 5-4a)::

        delta_H = N * DX * sum_{i=NBX}^{NEL} DELTA(i)
                = N * DX * sum_{i=NBX}^{NEL} (e_f(i) - e_o(i)) / (1 + e_o(i))   (5-2)

    delta_H = potential vertical heave at the bottom of the foundation,
    feet; N = fraction of volumetric swell that occurs as heave in the
    vertical direction; DX = increment of depth, feet; NEL = total number
    of elements; NBX = number of nodal point at bottom of the foundation;
    DELTA(i) = potential volumetric swell of soil element i, fraction;
    e_f(i), e_o(i) = final and initial void ratio of element i. "The
    delta_H is the potential vertical heave beneath a flexible,
    unrestrained foundation. The bottom nodal point NNP = NEL + 1, and it
    is often set at the active depth of heave Xa." N (para 5-3a and 5-4):
    1 for intact soil with few fissures, as low as 1/3 for heavily
    fissured soil; "N should be 1 for consolidometer swell test results
    and a minimum of 1/3 for soil suction test results".

    For one element with N = 1 and DX = H this is Figure 4-2's relation
    (p. 4-4), Sp/100 = delta_H/H = (e1 - eo)/(1 + eo); each element's
    percent_swell is that Sp.

    Parameters
    ----------
    elements : list of dict
        The elements from the bottom of the foundation down, each with
        initial_void_ratio (e_o) and final_void_ratio (e_f), both > 0.
    depth_increment_ft : float
        DX, feet, > 0.
    vertical_swell_fraction : float
        N, from 1/3 to 1 (para 5-3a).

    Returns
    -------
    dict
        Keys: heave_ft, elements (list: DELTA, percent_swell),
        sum_delta, depth_increment_ft, vertical_swell_fraction, equation,
        notes, source.

    Raises
    ------
    ValueError
        If elements is empty, a void ratio is not positive, DX is not
        positive, or N is outside 1/3 to 1.

    Example: one element, e_o 0.8, e_f 0.9, DX 1 ft, N 1: 0.1/1.8 =
    0.0556 ft.
    """
    if not elements:
        raise ValueError("elements must not be empty")
    if depth_increment_ft is None or depth_increment_ft <= 0:
        raise ValueError(f"depth_increment_ft must be > 0, got {depth_increment_ft}")
    n = vertical_swell_fraction
    if n is None or not (1.0 / 3.0 - 1e-9 <= n <= 1.0):
        raise ValueError(
            "vertical_swell_fraction N must be from 1/3 to 1 (para 5-3a, "
            f"p. 5-2: N = 1 for intact soil, as low as 1/3); got {n}")
    rows = []
    for i, el in enumerate(elements):
        eo, ef = el.get("initial_void_ratio"), el.get("final_void_ratio")
        for name, v in (("initial_void_ratio", eo), ("final_void_ratio", ef)):
            if v is None or v <= 0:
                raise ValueError(f"elements[{i}].{name} must be > 0, got {v}")
        delta = (ef - eo) / (1.0 + eo)
        rows.append({"initial_void_ratio": eo, "final_void_ratio": ef,
                     "DELTA": round(delta, 5),
                     "percent_swell": round(100.0 * delta, 3)})
    sum_delta = sum((r["final_void_ratio"] - r["initial_void_ratio"])
                    / (1.0 + r["initial_void_ratio"]) for r in rows)
    heave = n * depth_increment_ft * sum_delta
    notes = [
        "Para 5-4a: the potential vertical heave beneath a flexible, "
        "unrestrained foundation; the bottom nodal point is often set at "
        "the active depth of heave Xa.",
        "Para 5-4: N should be 1 for consolidometer swell test results and "
        "a minimum of 1/3 for soil suction test results.",
    ]
    if heave < 0:
        notes.append("The final void ratios are smaller than the initial "
                     "ones overall: the result is a settlement, not heave.")
    return {
        "heave_ft": round(heave, 4),
        "sum_delta": round(sum_delta, 5),
        "elements": rows,
        "depth_increment_ft": depth_increment_ft,
        "vertical_swell_fraction": n,
        "equation": "delta_H = N * DX * sum (e_f(i) - e_o(i)) / (1 + e_o(i))",
        "notes": notes,
        "source": f"{_REF}, Eq. 5-2, para 5-4a, printed p. 5-2 (PDF 37)",
    }


_PROFILES = {
    "saturated": "saturated", "method_1": "saturated", "method 1": "saturated",
    "hydrostatic_i": "hydrostatic_i", "hydrostatic i": "hydrostatic_i",
    "method_2": "hydrostatic_i", "method 2": "hydrostatic_i",
    "hydrostatic_ii": "hydrostatic_ii", "hydrostatic ii": "hydrostatic_ii",
    "method_3": "hydrostatic_ii", "method 3": "hydrostatic_ii",
}


def eq_5_3_to_5_5_equilibrium_pore_water_pressure(
        profile, depth_ft, active_zone_depth_ft=None,
        pore_water_pressure_at_xa_tsf=None):
    """Equilibrium (final) pore water pressure u_w, tons per square foot,
    at depth X in the active zone, UFC 3-220-07 Eqs. 5-3 to 5-5 (printed
    p. 5-3 to 5-4, PDF 38-39), for the saturated (Method 1), hydrostatic I
    (Method 2) or hydrostatic II (Method 3) profile of Figure 5-1; u_w is
    the pore water pressure Eq. 5-9 subtracts to give the final effective
    pressure for Eq. 5-8.

    As printed (para 5-4b(2))::

        saturated, Method 1:       u_w = 0                         (5-3)
        hydrostatic I, Method 2:   u_w = gamma_w (X - Xa)          (5-4)
        hydrostatic II, Method 3:  u_w = u_wa + gamma_w (X - Xa)   (5-5)

    u_w = pore water pressure in tons per square foot at any depth X in
    feet within the active zone; gamma_w = unit weight of water (0.0312 ton
    per cubic foot); u_wa = the negative pore water pressure in tons per
    square foot at depth Xa in feet. Figure 5-1 draws X down from the
    foundation slab. Method 1 "should be used if other information on the
    equilibrium pore water pressure profile is not available"; Method 2 is
    believed more realistic beneath highways and pavements where drainage
    is good, and leads to smaller predictions of heave than Method 1;
    Method 3 is Method 2 without a shallow water table. Para 5-4c(1)
    (p. 5-4): for groundwater levels less than 20 feet in clay soil Xa may
    be assumed equal to the depth of the water table, and the u_wa term
    becomes zero for the hydrostatic I profile.

    Parameters
    ----------
    profile : str
        'saturated' (or 'method_1'), 'hydrostatic_i' ('method_2') or
        'hydrostatic_ii' ('method_3').
    depth_ft : float
        X, feet, from 0 to Xa.
    active_zone_depth_ft : float, optional
        Xa, feet (> 0); required for Methods 2 and 3 (for Method 2 the
        depth of the water table, para 5-4c(1)).
    pore_water_pressure_at_xa_tsf : float, optional
        u_wa, tons per square foot, <= 0; required for Method 3.

    Returns
    -------
    dict
        Keys: pore_water_pressure_tsf, profile, method, depth_ft,
        active_zone_depth_ft, gamma_w_tcf, equation, note, source.

    Raises
    ------
    ValueError
        For an unknown profile, a missing Xa or u_wa, X outside 0 to Xa, or
        a positive u_wa.

    Example: Method 3 at X = 2 ft with Xa = 8 ft and u_wa = -7.5 tsf (the
    values Figure 5-2 prints for the Hayes, Kansas site): -7.5 + 0.0312 x
    (2 - 8) = -7.687 tsf.
    """
    key = _PROFILES.get(str(profile).strip().lower())
    if key is None:
        raise ValueError(
            f"Unknown profile '{profile}'. Use 'saturated' (Method 1, Eq. "
            "5-3), 'hydrostatic_i' (Method 2, Eq. 5-4) or 'hydrostatic_ii' "
            "(Method 3, Eq. 5-5).")
    x, xa, uwa = depth_ft, active_zone_depth_ft, pore_water_pressure_at_xa_tsf
    if x is None or x < 0:
        raise ValueError(f"depth_ft must be >= 0, got {x}")
    if key != "saturated" and xa is None:
        raise ValueError(f"active_zone_depth_ft (Xa) is required for the {key} profile")
    if xa is not None:
        if xa <= 0:
            raise ValueError(f"active_zone_depth_ft must be > 0, got {xa}")
        if x > xa:
            raise ValueError(
                f"depth_ft {x} is below the active zone (Xa = {xa} ft); Eqs. "
                "5-3 to 5-5 give u_w within the active zone")
    if key == "saturated":
        uw, method, eq = 0.0, "Method 1", "u_w = 0 (5-3)"
    elif key == "hydrostatic_i":
        uw = _GAMMA_W_TCF * (x - xa)
        method, eq = "Method 2", "u_w = gamma_w (X - Xa) (5-4)"
    else:
        if uwa is None:
            raise ValueError(
                "pore_water_pressure_at_xa_tsf (u_wa) is required for the "
                "hydrostatic II profile")
        if uwa > 0:
            raise ValueError(
                "pore_water_pressure_at_xa_tsf is the negative pore water "
                f"pressure at Xa (<= 0), got {uwa}")
        uw = uwa + _GAMMA_W_TCF * (x - xa)
        method, eq = "Method 3", "u_w = u_wa + gamma_w (X - Xa) (5-5)"
    return {
        "pore_water_pressure_tsf": round(uw, 4),
        "profile": key,
        "method": method,
        "depth_ft": x,
        "active_zone_depth_ft": xa,
        "pore_water_pressure_at_xa_tsf": uwa,
        "gamma_w_tcf": _GAMMA_W_TCF,
        "equation": eq,
        "note": ("Para 5-4b(2)(a): the saturated profile should be used if "
                 "other information on the equilibrium pore water pressure "
                 "profile is not available. The hydrostatic profiles lead to "
                 "smaller predictions of heave than the saturated profile."),
        "source": (f"{_REF}, Eqs. 5-3 to 5-5 and Figure 5-1, para 5-4b(2), "
                   "printed p. 5-3 to 5-4 (PDF 38-39)"),
    }


def eq_5_8_consolidometer_heave(layers):
    """Heave from consolidometer swell tests, feet, UFC 3-220-07 Eq. 5-8
    with the final effective pressure of Eq. 5-9 (printed p. 5-5, PDF 40):
    for each expansive layer, its thickness times the swell index over
    (1 + e_o) times log(swell pressure / final vertical effective
    pressure), summed over the layers.

    As printed (para 5-4e(1))::

        delta_H / H = c_s / (1 + e_o) * log(sigma_s / sigma'_v)    (5-8)
        sigma'_v = sigma_v - u_w                                   (5-9)

    H = thickness of expansive soil layer, feet; c_s = swell index, slope
    of the curve between points 3 and 4, figure 4-2; sigma_s = swell
    pressure, tons per square foot; sigma'_v = final vertical effective
    pressure, tons per square foot; sigma_v = total vertical overburden
    pressure and u_w = equilibrium pore water pressure, tons per square
    foot (Eqs. 5-3 to 5-5). "log" is taken as log10, the scale of Figure
    4-2's "LOG PRESSURE" axis on which c_s is the slope. e_o is the initial
    void ratio (point 1 of Figure 4-2). The total vertical heave at the
    ground surface is the sum of the delta_H for each thickness H in the
    soil profile (para 4-2a(1), p. 4-4). Net settlements occur for final
    effective pressures exceeding the swell pressure (p. 4-4); such a layer
    gives a negative delta_H here.

    How it relates to Figure 5-4 (heave_prediction_mm): "If u_w is zero
    for a saturated profile, equation (5-3), then sigma'_v is equal to
    sigma_v and heave will be the same as that given by the equation for
    Sp in figure 4-2" (p. 5-5), that is delta_H/H = Sp/100. Figure 5-4
    adds up those per cent swells over depth as the area under the per
    cent swell versus depth curve; heave_prediction_mm takes that area as
    rectangles, so the layers' percent_swell from this function, fed to
    it with the same thicknesses, gives the same total. The print gives
    no worked example of Eq. 5-8.

    Parameters
    ----------
    layers : list of dict
        Each dict: thickness_ft (H, > 0), swell_index (c_s, >= 0),
        initial_void_ratio (e_o, > 0), swell_pressure_tsf (sigma_s, > 0),
        total_vertical_pressure_tsf (sigma_v, >= 0) and, optionally,
        pore_water_pressure_tsf (u_w; default 0, the saturated profile of
        Eq. 5-3, which para 5-4b(2)(a) says should be used if other
        information is not available).

    Returns
    -------
    dict
        Keys: total_heave_ft, total_heave_in (conversion), layers (list:
        final_effective_pressure_tsf, percent_swell, heave_ft), equation,
        notes, source.

    Raises
    ------
    ValueError
        If layers is empty, an input is out of range, or a final
        effective pressure is not positive.

    Example: H 1 ft, c_s 0.1, e_o 1.0, sigma_s 4 tsf, sigma_v 0.4 tsf,
    u_w 0: 1 x 0.1/2 x log10(10) = 0.05 ft.
    """
    if not layers:
        raise ValueError("layers must not be empty")
    rows = []
    notes = [
        "Para 4-2a(1): the total vertical heave at the ground surface is the "
        "sum of the delta_H for each thickness H in the soil profile.",
        "'log' in Eq. 5-8 is taken as log10, the scale of Figure 4-2's log "
        "pressure axis on which the swell index c_s is the slope.",
    ]
    for i, layer in enumerate(layers):
        h = layer.get("thickness_ft")
        cs = layer.get("swell_index")
        eo = layer.get("initial_void_ratio")
        ss = layer.get("swell_pressure_tsf")
        sv = layer.get("total_vertical_pressure_tsf")
        uw = layer.get("pore_water_pressure_tsf", 0.0)
        checks = (("thickness_ft", h, h is not None and h > 0),
                  ("swell_index", cs, cs is not None and cs >= 0),
                  ("initial_void_ratio", eo, eo is not None and eo > 0),
                  ("swell_pressure_tsf", ss, ss is not None and ss > 0),
                  ("total_vertical_pressure_tsf", sv, sv is not None and sv >= 0),
                  ("pore_water_pressure_tsf", uw, uw is not None))
        for name, v, ok in checks:
            if not ok:
                raise ValueError(f"layers[{i}].{name} is out of range: {v}")
        sev = sv - uw
        if sev <= 0:
            raise ValueError(
                f"layers[{i}]: final vertical effective pressure "
                f"sigma_v - u_w = {sev:g} tsf is not positive (Eq. 5-9); "
                "Eq. 5-8 needs it > 0")
        ratio = cs / (1.0 + eo) * math.log10(ss / sev)
        rows.append({
            "thickness_ft": h, "final_effective_pressure_tsf": round(sev, 4),
            "percent_swell": round(100.0 * ratio, 3),
            "heave_ft": round(h * ratio, 4),
        })
        if sev > ss:
            notes.append(
                f"Layer {i}: the final effective pressure exceeds the swell "
                "pressure, so it settles (negative delta_H): 'Net settlements "
                "will occur for final effective pressures exceeding the swell "
                "pressure' (para 4-2a(1)(b), p. 4-4).")
    total = 0.0
    for layer, r in zip(layers, rows):
        sev = layer["total_vertical_pressure_tsf"] - layer.get("pore_water_pressure_tsf", 0.0)
        total += (layer["thickness_ft"] * layer["swell_index"]
                  / (1.0 + layer["initial_void_ratio"])
                  * math.log10(layer["swell_pressure_tsf"] / sev))
    return {
        "total_heave_ft": round(total, 4),
        "total_heave_in": round(total * 12.0, 3),
        "layers": rows,
        "equation": ("delta_H/H = c_s/(1 + e_o) * log10(sigma_s/sigma'_v); "
                     "sigma'_v = sigma_v - u_w"),
        "notes": notes,
        "source": (f"{_REF}, Eqs. 5-8 and 5-9, para 5-4e(1), printed p. 5-5 "
                   "(PDF 40); symbols of Figure 4-2, printed p. 4-4 (PDF 34)"),
    }
