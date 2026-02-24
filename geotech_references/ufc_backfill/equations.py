"""UFC 3-220-04N backfill equations.

Compaction-induced lateral earth pressures (Broms 1971 / Ingold 1979),
Terzaghi filter criteria, and relative compaction checks.
All units SI.
"""

import math


def compaction_induced_pressure_kPa(
    roller_line_load_kN_per_m,
    depth_m,
    unit_weight_kN_per_m3,
    K0=0.5,
):
    """Lateral earth pressure from backfill compaction (Broms 1971).

    A vibratory roller modelled as a line load *q* produces a residual
    lateral pressure that is constant from the surface to a critical
    depth *z_cr*, then follows *K0 * gamma * z* below.

    Parameters
    ----------
    roller_line_load_kN_per_m : float
        Static line load of roller = weight / drum width (kN/m).
        Typical values: 10-50 kN/m.
    depth_m : float
        Depth below ground surface (m), must be > 0.
    unit_weight_kN_per_m3 : float
        Total unit weight of compacted backfill (kN/m³).
    K0 : float, optional
        At-rest earth pressure coefficient (default 0.5).

    Returns
    -------
    dict
        Keys: sigma_h_kPa (lateral pressure), z_cr_m (critical depth),
        sigma_h_max_kPa (maximum residual pressure), regime
        ('compaction_controlled' or 'overburden_controlled').

    Raises
    ------
    ValueError
        If any input is non-positive, or K0 not in (0, 1].
    """
    q = roller_line_load_kN_per_m
    z = depth_m
    gamma = unit_weight_kN_per_m3

    if q <= 0:
        raise ValueError(f"roller_line_load_kN_per_m must be > 0, got {q}")
    if z <= 0:
        raise ValueError(f"depth_m must be > 0, got {z}")
    if gamma <= 0:
        raise ValueError(f"unit_weight_kN_per_m3 must be > 0, got {gamma}")
    if not (0 < K0 <= 1):
        raise ValueError(f"K0 must be in (0, 1], got {K0}")

    # Maximum residual horizontal stress (Broms 1971)
    sigma_h_max = math.sqrt(2.0 * q * gamma * K0 / math.pi)

    # Critical depth where K0*gamma*z equals sigma_h_max
    z_cr = sigma_h_max / (K0 * gamma)

    if z <= z_cr:
        sigma_h = sigma_h_max
        regime = "compaction_controlled"
    else:
        sigma_h = K0 * gamma * z
        regime = "overburden_controlled"

    return {
        "sigma_h_kPa": round(sigma_h, 2),
        "z_cr_m": round(z_cr, 3),
        "sigma_h_max_kPa": round(sigma_h_max, 2),
        "regime": regime,
    }


def filter_criteria_check(
    d15_filter_mm,
    d85_soil_mm,
    d15_soil_mm=None,
    d50_filter_mm=None,
    d50_soil_mm=None,
    cu_filter=None,
):
    """Check Terzaghi/USACE filter design criteria (UFC 3-220-04N).

    Evaluates up to four filter compatibility criteria:

    1. **Retention (piping)**: D15_filter / d85_soil <= 5
    2. **Permeability**: D15_filter / d15_soil >= 5
    3. **Uniformity**: D50_filter / d50_soil <= 25
    4. **Segregation**: Cu_filter <= 20

    Parameters
    ----------
    d15_filter_mm : float
        D15 of filter material (mm).
    d85_soil_mm : float
        d85 of base (protected) soil (mm).
    d15_soil_mm : float, optional
        d15 of base soil (mm). Required for permeability check.
    d50_filter_mm : float, optional
        D50 of filter material (mm). Required for uniformity check.
    d50_soil_mm : float, optional
        d50 of base soil (mm). Required for uniformity check.
    cu_filter : float, optional
        Coefficient of uniformity (D60/D10) of filter. Required for
        segregation check.

    Returns
    -------
    dict
        Keys: retention_ratio, retention_pass (bool),
        permeability_ratio, permeability_pass (bool),
        uniformity_ratio, uniformity_pass (bool),
        segregation_cu, segregation_pass (bool),
        all_pass (bool), criteria_checked (list of str).

    Raises
    ------
    ValueError
        If required inputs are non-positive.
    """
    if d15_filter_mm <= 0:
        raise ValueError(f"d15_filter_mm must be > 0, got {d15_filter_mm}")
    if d85_soil_mm <= 0:
        raise ValueError(f"d85_soil_mm must be > 0, got {d85_soil_mm}")

    result = {"criteria_checked": []}
    all_pass = True

    # 1. Retention (piping prevention)
    ratio_ret = d15_filter_mm / d85_soil_mm
    pass_ret = ratio_ret <= 5.0
    result["retention_ratio"] = round(ratio_ret, 2)
    result["retention_pass"] = pass_ret
    result["criteria_checked"].append("retention")
    if not pass_ret:
        all_pass = False

    # 2. Permeability
    if d15_soil_mm is not None:
        if d15_soil_mm <= 0:
            raise ValueError(f"d15_soil_mm must be > 0, got {d15_soil_mm}")
        ratio_perm = d15_filter_mm / d15_soil_mm
        pass_perm = ratio_perm >= 5.0
        result["permeability_ratio"] = round(ratio_perm, 2)
        result["permeability_pass"] = pass_perm
        result["criteria_checked"].append("permeability")
        if not pass_perm:
            all_pass = False

    # 3. Uniformity
    if d50_filter_mm is not None and d50_soil_mm is not None:
        if d50_filter_mm <= 0:
            raise ValueError(f"d50_filter_mm must be > 0, got {d50_filter_mm}")
        if d50_soil_mm <= 0:
            raise ValueError(f"d50_soil_mm must be > 0, got {d50_soil_mm}")
        ratio_unif = d50_filter_mm / d50_soil_mm
        pass_unif = ratio_unif <= 25.0
        result["uniformity_ratio"] = round(ratio_unif, 2)
        result["uniformity_pass"] = pass_unif
        result["criteria_checked"].append("uniformity")
        if not pass_unif:
            all_pass = False

    # 4. Segregation
    if cu_filter is not None:
        if cu_filter <= 0:
            raise ValueError(f"cu_filter must be > 0, got {cu_filter}")
        pass_seg = cu_filter <= 20.0
        result["segregation_cu"] = round(cu_filter, 2)
        result["segregation_pass"] = pass_seg
        result["criteria_checked"].append("segregation")
        if not pass_seg:
            all_pass = False

    result["all_pass"] = all_pass
    return result


def relative_compaction_check(
    dry_density_kN_per_m3,
    max_dry_density_kN_per_m3,
    required_pct=95.0,
):
    """Check whether field compaction meets the specification.

    Parameters
    ----------
    dry_density_kN_per_m3 : float
        Field dry unit weight (kN/m³).
    max_dry_density_kN_per_m3 : float
        Maximum dry unit weight from Standard Proctor (ASTM D698)
        or Modified Proctor (ASTM D1557) (kN/m³).
    required_pct : float, optional
        Minimum required relative compaction (%, default 95).

    Returns
    -------
    dict
        Keys: relative_compaction_pct, required_pct, passes (bool),
        deficit_pct (0 if passes, else shortfall).

    Raises
    ------
    ValueError
        If any input is non-positive or required_pct not in (0, 100].
    """
    if dry_density_kN_per_m3 <= 0:
        raise ValueError(
            f"dry_density_kN_per_m3 must be > 0, got {dry_density_kN_per_m3}"
        )
    if max_dry_density_kN_per_m3 <= 0:
        raise ValueError(
            f"max_dry_density_kN_per_m3 must be > 0, got {max_dry_density_kN_per_m3}"
        )
    if not (0 < required_pct <= 100):
        raise ValueError(f"required_pct must be in (0, 100], got {required_pct}")

    rc = (dry_density_kN_per_m3 / max_dry_density_kN_per_m3) * 100.0
    passes = rc >= required_pct
    deficit = 0.0 if passes else required_pct - rc

    return {
        "relative_compaction_pct": round(rc, 1),
        "required_pct": required_pct,
        "passes": passes,
        "deficit_pct": round(deficit, 1),
    }
