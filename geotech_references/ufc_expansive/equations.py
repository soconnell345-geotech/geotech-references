"""UFC 3-220-07 expansive soil equations.

From UFC 3-220-07, Foundations in Expansive Soils (the reproduced
TM 5-818-7), docs/ufc_3_220_07.pdf: total swell as the area under the
per cent swell versus depth curve, Figure 5-4 (printed p. 5-7, PDF 42),
and the four relations of Table 4-2, "Other Empirical Methods for
Prediction of Potential Heave" (printed p. 4-3, PDF 33).

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
