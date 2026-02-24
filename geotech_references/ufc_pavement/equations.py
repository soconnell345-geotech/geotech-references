"""UFC 3-260-02 pavement design equations.

CBR-to-subgrade modulus conversion, flexible pavement thickness (CBR
method), equivalent single wheel load (ESWL), and rigid pavement
thickness (Westergaard-based).  All units SI.
"""

import math


def cbr_to_subgrade_modulus_MPa_per_m(cbr):
    """Convert California Bearing Ratio to modulus of subgrade reaction.

    Empirical correlation (AASHTO/PCA/UFC)::

        k (pci) ≈ 26 * CBR^0.7   (for CBR 2-80)
        k (MPa/m) = k (pci) * 0.2714

    Parameters
    ----------
    cbr : float
        California Bearing Ratio (%).  Valid range 2-80.

    Returns
    -------
    float
        Modulus of subgrade reaction k (MPa/m).

    Raises
    ------
    ValueError
        If cbr is outside 2-80 range.
    """
    if cbr < 2:
        raise ValueError(f"cbr must be >= 2, got {cbr}")
    if cbr > 80:
        raise ValueError(f"cbr must be <= 80, got {cbr}")

    k_pci = 26.0 * cbr ** 0.7
    k_MPa_per_m = k_pci * 0.2714
    return round(k_MPa_per_m, 1)


def flexible_pavement_thickness_mm(
    cbr,
    wheel_load_kN,
    tire_pressure_kPa,
    coverages=10000,
):
    """Flexible pavement thickness by the CBR method (UFC 3-260-02).

    Simplified thickness equation for flexible pavements::

        t (in) = sqrt(P / (8.1 * CBR * pi)) * alpha

    where *P* = wheel load (lb), *CBR* = subgrade CBR (%),
    and *alpha* is a coverage factor.  Converted to SI.

    For traffic coverages: alpha ~ 1.0 for 1,000 coverages,
    increases with traffic.

    Parameters
    ----------
    cbr : float
        Subgrade CBR (%).  Valid range 2-50.
    wheel_load_kN : float
        Single wheel load (kN).
    tire_pressure_kPa : float
        Tire inflation pressure (kPa).
    coverages : int, optional
        Design number of coverages (default 10,000).

    Returns
    -------
    dict
        Keys: total_thickness_mm, contact_radius_mm, notes.

    Raises
    ------
    ValueError
        If inputs are non-positive or CBR out of range.
    """
    if cbr < 2:
        raise ValueError(f"cbr must be >= 2, got {cbr}")
    if cbr > 50:
        raise ValueError(f"cbr must be <= 50, got {cbr}")
    if wheel_load_kN <= 0:
        raise ValueError(f"wheel_load_kN must be > 0, got {wheel_load_kN}")
    if tire_pressure_kPa <= 0:
        raise ValueError(
            f"tire_pressure_kPa must be > 0, got {tire_pressure_kPa}"
        )
    if coverages <= 0:
        raise ValueError(f"coverages must be > 0, got {coverages}")

    # Contact area and radius
    A_mm2 = (wheel_load_kN * 1000.0) / tire_pressure_kPa  # N / (N/mm²*1e-3) ...
    # tire_pressure in kPa = kN/m²; load in kN
    # Contact area = load / pressure = kN / (kN/m²) = m²
    A_m2 = wheel_load_kN / tire_pressure_kPa
    r_m = math.sqrt(A_m2 / math.pi)
    r_mm = r_m * 1000.0

    # Coverage factor (logarithmic relationship)
    if coverages <= 1000:
        alpha = 1.0
    elif coverages <= 10000:
        alpha = 1.0 + 0.12 * math.log10(coverages / 1000.0)
    else:
        alpha = 1.12 + 0.15 * math.log10(coverages / 10000.0)

    # CBR thickness equation
    # t = sqrt(P / (pi * CBR_decimal * S)) where S is allowable subgrade
    # stress ~ 8.1 * CBR (psi).  In SI:
    # Allowable subgrade stress (kPa) ~ 68.9 * CBR (conversion from psi)
    # Simplification: t = r * sqrt(tire_pressure / (68.9 * CBR) - 1) * alpha
    # If the ratio < 1, the subgrade can support the load directly
    ratio = tire_pressure_kPa / (68.9 * cbr)
    if ratio <= 1.0:
        # Subgrade strong enough; only base/surface minimum
        t_mm = max(100.0, r_mm * 0.5)
    else:
        t_mm = r_mm * math.sqrt(ratio - 1.0) * alpha

    return {
        "total_thickness_mm": round(t_mm, 0),
        "contact_radius_mm": round(r_mm, 1),
        "coverage_factor": round(alpha, 3),
        "notes": "Minimum total pavement thickness above subgrade",
    }


def equivalent_single_wheel_load_kN(
    wheel_load_kN,
    num_wheels,
    wheel_spacing_mm,
    depth_mm,
):
    """Equivalent single wheel load (ESWL) at a given depth.

    For a multi-wheel gear, the ESWL at depth *z* is interpolated
    between::

        ESWL = P            (at z = 0, stress overlap = 0)
        ESWL = n * P        (at z >> S, full overlap)

    Using the log-based interpolation (UFC 3-260-02)::

        If z <= S/2: ESWL = P * (1 + (n-1) * 2z/S * log(n)/log(n))
        Simplified: ESWL = P at z=0, n*P at z=S/2, interpolate log

    A common approximation::

        ESWL = P * (1 + (n-1) * min(2*z/S, 1))

    Parameters
    ----------
    wheel_load_kN : float
        Load per wheel (kN).
    num_wheels : int
        Number of wheels in the gear assembly.
    wheel_spacing_mm : float
        Centre-to-centre wheel spacing (mm).
    depth_mm : float
        Depth below surface at which ESWL is evaluated (mm).

    Returns
    -------
    float
        Equivalent single wheel load (kN).

    Raises
    ------
    ValueError
        If inputs are non-positive.
    """
    P = wheel_load_kN
    n = num_wheels
    S = wheel_spacing_mm
    z = depth_mm

    if P <= 0:
        raise ValueError(f"wheel_load_kN must be > 0, got {P}")
    if n < 1:
        raise ValueError(f"num_wheels must be >= 1, got {n}")
    if S <= 0:
        raise ValueError(f"wheel_spacing_mm must be > 0, got {S}")
    if z < 0:
        raise ValueError(f"depth_mm must be >= 0, got {z}")

    if n == 1:
        return P

    # Linear interpolation factor from 1 at z=0 to n at z=2*S_d
    # where S_d is the critical overlap depth
    S_d = S / 2.0  # half-spacing
    if z >= 2.0 * S_d:
        factor = float(n)
    else:
        # Log interpolation (Boyd & Foster approach)
        ratio = z / (2.0 * S_d)
        factor = 1.0 + (n - 1.0) * ratio

    return round(P * factor, 1)


def rigid_pavement_thickness_mm(
    k_subgrade_MPa_per_m,
    wheel_load_kN,
    concrete_flexural_strength_MPa,
    safety_factor=1.3,
):
    """Rigid (PCC) pavement thickness for airfields (simplified).

    Based on Westergaard edge loading analysis (UFC 3-260-02)::

        h = sqrt(3 * P * FS / (pi * f_r))

    where *P* = wheel load, *f_r* = concrete flexural (rupture)
    strength, *FS* = safety factor.  The subgrade modulus *k* affects
    the radius of relative stiffness but for a simplified single-load
    check, this approach gives a conservative first estimate.

    Parameters
    ----------
    k_subgrade_MPa_per_m : float
        Modulus of subgrade reaction (MPa/m).
    wheel_load_kN : float
        Single wheel load (kN).
    concrete_flexural_strength_MPa : float
        Flexural (rupture) strength of PCC, f_r (MPa).
        Typical values: 3.5-5.0 MPa.
    safety_factor : float, optional
        Factor of safety applied to stress (default 1.3).

    Returns
    -------
    dict
        Keys: thickness_mm, radius_of_relative_stiffness_mm, notes.

    Raises
    ------
    ValueError
        If inputs are non-positive.
    """
    k = k_subgrade_MPa_per_m
    P = wheel_load_kN
    fr = concrete_flexural_strength_MPa
    FS = safety_factor

    if k <= 0:
        raise ValueError(f"k_subgrade_MPa_per_m must be > 0, got {k}")
    if P <= 0:
        raise ValueError(f"wheel_load_kN must be > 0, got {P}")
    if fr <= 0:
        raise ValueError(
            f"concrete_flexural_strength_MPa must be > 0, got {fr}"
        )
    if FS < 1.0:
        raise ValueError(f"safety_factor must be >= 1.0, got {FS}")

    # Concrete properties (typical)
    E_concrete = 27600.0  # MPa (typical for PCC)
    nu = 0.15  # Poisson's ratio for concrete

    # Westergaard: required thickness from edge stress
    # sigma_edge = (3*P) / (pi * h^2) * [1 + ...] ≈ simplified
    # Rearranging: h = sqrt(3 * P * FS / (pi * fr))
    # P in kN = kN; fr in MPa = kN/m²/1000; so convert:
    # P_kN * 1000 (to N) / (pi * fr * 1e6 (N/m²)) -> h in m
    # Simplified: h_m = sqrt(3 * P * FS / (pi * fr * 1e3))
    h_m = math.sqrt(3.0 * P * FS / (math.pi * fr * 1e3))
    h_mm = h_m * 1000.0

    # Radius of relative stiffness
    # l = (E*h^3 / (12*(1-nu^2)*k))^0.25
    k_Pa_per_m = k * 1e6  # MPa/m -> Pa/m
    l_m = (E_concrete * 1e6 * h_m**3 / (12.0 * (1.0 - nu**2) * k_Pa_per_m)) ** 0.25

    return {
        "thickness_mm": round(h_mm, 0),
        "radius_of_relative_stiffness_mm": round(l_m * 1000.0, 0),
        "notes": "Simplified Westergaard edge loading; verify with full design charts",
    }
