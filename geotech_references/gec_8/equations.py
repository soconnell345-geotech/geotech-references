"""GEC-8 equation functions.

Equations from FHWA-HIF-07-03 (GEC-8, April 2007), Design and Construction of
Continuous Flight Auger Piles.

ASD (not LRFD) design document.  This module implements:
- DD pile side resistance (NeSmith 2002)
- ASD axial capacity check (RT ≥ SF × Q_allow)
- Grout volume factor check

Conventional CFA pile capacity uses the FHWA 1999 method:
- Cohesive: fs = α × Su (alpha method)
- Cohesionless: fs = β × σ'v (FHWA 1999)
These equations are shared with the drilled shaft design methods (GEC-10/GEC-12)
and are not duplicated here.
"""


def dd_pile_side_resistance_MPa(
    spt_n: float,
    soil_type: str = "dirty_rounded",
) -> dict:
    """Unit side resistance for drilled displacement (DD) piles (NeSmith 2002).

    From NeSmith (2002) research on 22 full-scale compression and pullout tests
    at 19 U.S. sites (Chapter 5.4.2, GEC-8)::

        fs (MPa) = 0.005 × N + Ws     (N ≤ 50)

    where Ws is a soil correlation constant that accounts for gradation.

    Two soil categories:
    - 'dirty_rounded': uniform, rounded materials with up to 40% fines.
      Ws = 0; limit fs ≤ 0.16 MPa.
    - 'clean_angular': well-graded angular materials with ≤ 10% fines.
      Ws = 0.05 MPa; limit fs ≤ 0.21 MPa.

    For soils between these extremes, linearly interpolate Ws and the
    limiting fs value.

    Parameters
    ----------
    spt_n : float
        SPT N-value (blows per 300 mm) at the depth of interest.
        Valid for N ≤ 50; for N > 50 use N = 50.
    soil_type : str
        Soil gradation type: 'dirty_rounded' or 'clean_angular'.

    Returns
    -------
    dict
        {'spt_n': float, 'soil_type': str, 'ws_MPa': float,
         'fs_MPa': float, 'limiting_fs_MPa': float,
         'fs_limited_MPa': float, 'source': str}

    Raises
    ------
    ValueError
        If spt_n is not positive or soil_type is unrecognized.
    """
    if spt_n <= 0:
        raise ValueError(f"spt_n must be > 0, got {spt_n}")

    _soil_params = {
        "dirty_rounded": {"ws": 0.0, "fs_limit": 0.16},
        "clean_angular": {"ws": 0.05, "fs_limit": 0.21},
    }

    key = soil_type.lower().strip().replace(" ", "_").replace("-", "_")
    _aliases = {
        "dirty": "dirty_rounded",
        "rounded": "dirty_rounded",
        "uniform": "dirty_rounded",
        "clean": "clean_angular",
        "angular": "clean_angular",
        "well_graded": "clean_angular",
        "well_graded_angular": "clean_angular",
    }
    key = _aliases.get(key, key)

    if key not in _soil_params:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. "
            "Use: 'dirty_rounded' (uniform, rounded, ≤ 40% fines) or "
            "'clean_angular' (well-graded, angular, ≤ 10% fines)."
        )

    params = _soil_params[key]
    n_capped = min(spt_n, 50.0)

    fs = 0.005 * n_capped + params["ws"]
    fs_limited = min(fs, params["fs_limit"])

    return {
        "spt_n": spt_n,
        "soil_type": key,
        "ws_MPa": params["ws"],
        "fs_MPa": round(fs, 4),
        "limiting_fs_MPa": params["fs_limit"],
        "fs_limited_MPa": round(fs_limited, 4),
        "source": "GEC-8 Section 5.4.2 (NeSmith 2002)",
    }


def cfa_allowable_capacity_kN(
    ultimate_resistance_kN: float,
    safety_factor: float = 2.0,
) -> dict:
    """ASD allowable axial resistance for CFA piles (GEC-8 Chapter 6).

    GEC-8 uses Allowable Stress Design (ASD).  The allowable resistance is:

        R_allow = R_ultimate / SF

    Where the factor of safety is compared to the applied service load:

        Q_applied ≤ R_allow

    Recommended safety factors (Section 6.3.2):
    - SF = 2.0–2.5 without load tests
    - SF = 2.0 with a complete pre-production static load test program

    Parameters
    ----------
    ultimate_resistance_kN : float
        Computed ultimate geotechnical axial resistance (kN).
        RT = RS + RB (side shear + end bearing).
    safety_factor : float, optional
        Factor of safety.  Default 2.0 (with load tests).
        Use 2.0–2.5 without load tests.

    Returns
    -------
    dict
        {'ultimate_resistance_kN': float, 'safety_factor': float,
         'allowable_resistance_kN': float, 'note': str}

    Raises
    ------
    ValueError
        If inputs are not positive.
    """
    if ultimate_resistance_kN <= 0:
        raise ValueError(
            f"ultimate_resistance_kN must be > 0, got {ultimate_resistance_kN}"
        )
    if safety_factor < 1.0:
        raise ValueError(f"safety_factor must be >= 1.0, got {safety_factor}")

    r_allow = ultimate_resistance_kN / safety_factor

    return {
        "ultimate_resistance_kN": ultimate_resistance_kN,
        "safety_factor": safety_factor,
        "allowable_resistance_kN": round(r_allow, 1),
        "note": (
            "GEC-8 ASD: SF = 2.0 with pre-production static load tests; "
            "SF = 2.0–2.5 without load tests; "
            "Q_service ≤ R_allow"
        ),
    }


def cfa_grout_volume_factor(
    delivered_volume_L: float,
    nominal_pile_volume_L: float,
) -> dict:
    """Grout volume factor (GVF) for CFA pile construction QC (GEC-8 Chapter 7).

    The grout volume factor is the ratio of delivered grout volume to the
    theoretical (nominal) pile volume.  GVF must exceed 1.0 at all times
    during auger withdrawal.  A target overrun of 15–20% above theoretical
    volume is required (GVF target: 1.15–1.20).

    Per GEC-8 Chapter 8 (guide specification), the GVF must remain within
    7.5% of the target established in the Pile Installation Plan.

    Parameters
    ----------
    delivered_volume_L : float
        Volume of grout/concrete delivered (liters).
    nominal_pile_volume_L : float
        Theoretical pile volume based on nominal diameter and depth (liters).

    Returns
    -------
    dict
        {'delivered_volume_L': float, 'nominal_pile_volume_L': float,
         'grout_volume_factor': float, 'acceptable': bool,
         'target_min': float, 'note': str}

    Raises
    ------
    ValueError
        If inputs are not positive.
    """
    if delivered_volume_L <= 0:
        raise ValueError(
            f"delivered_volume_L must be > 0, got {delivered_volume_L}"
        )
    if nominal_pile_volume_L <= 0:
        raise ValueError(
            f"nominal_pile_volume_L must be > 0, got {nominal_pile_volume_L}"
        )

    gvf = delivered_volume_L / nominal_pile_volume_L

    return {
        "delivered_volume_L": delivered_volume_L,
        "nominal_pile_volume_L": nominal_pile_volume_L,
        "grout_volume_factor": round(gvf, 3),
        "acceptable": gvf >= 1.0,
        "target_min": 1.15,
        "note": (
            "GEC-8: GVF must exceed 1.0 continuously during withdrawal; "
            "target 1.15–1.20 (15–20% overrun); "
            "spec allows ±7.5% of target from Pile Installation Plan"
        ),
    }
