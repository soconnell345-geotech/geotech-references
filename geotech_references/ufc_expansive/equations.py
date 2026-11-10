"""UFC 3-220-07 expansive soil equations.

From UFC 3-220-07, Foundations in Expansive Soils (the reproduced
TM 5-818-7), docs/ufc_3_220_07.pdf: total swell as the area under the
per cent swell versus depth curve, Figure 5-4 (printed p. 5-7, PDF 42).

Rebuilt from the print 2026-11-10 (review pave-13): activity_index
(Skempton), free_swell_percent (Seed et al. 1962), swell_pressure_kPa
(Komornik and David, with LL taken as PI + 20) and
pier_minimum_embedment_m (1.5 times the active zone) were removed; none
is printed in this manual.
"""

_REF = "UFC 3-220-07 (TM 5-818-7)"
_M_TO_FT = 1.0 / 0.3048


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
