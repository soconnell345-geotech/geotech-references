"""GEC-8 equation functions.

Equations from FHWA-HIF-07-03 (GEC-8, April 2007), Design and Construction of
Continuous Flight Auger Piles.

ASD (not LRFD) design document.  This module implements:
- DD pile side resistance (NeSmith 2002)
- ASD axial capacity check (Eq. 6.1, ΣQi ≤ R / SF)
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
    """Ultimate unit side resistance fs in MPa of a drilled displacement (DD) pile in cohesionless soil from SPT-N60, GEC-8 Eq. 5.29 in its MPa form (FHWA-HIF-07-03, pp. 83-84; NeSmith 2002).

    From NeSmith (2002): 22 full-scale compression load tests and six
    pullout tests of DD piles at 19 U.S. sites (Section 5.4.2)::

        fs (MPa) = 0.005 × N + Ws     (N ≤ 50)

    "SPT-N60 values should be based on 60% hammer efficiency but should
    not be depth corrected. These relationships should only be applied to
    cohesionless materials in which displacement of the spoils into the
    borehole wall during construction will result in densification of the
    surrounding soil" (p. 83). Every result carries that sentence.

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
        SPT-N60 (blows per 300 mm, 60% hammer efficiency, not depth
        corrected) at the depth of interest. The equation is printed for
        N ≤ 50; above 50, N = 50 is used and the result says so.
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

    out = {
        "spt_n": spt_n,
        "soil_type": key,
        "ws_MPa": params["ws"],
        "fs_MPa": round(fs, 4),
        "limiting_fs_MPa": params["fs_limit"],
        "fs_limited_MPa": round(fs_limited, 4),
        "print_note": (
            "SPT-N60 values should be based on 60% hammer efficiency but "
            "should not be depth corrected. These relationships should only "
            "be applied to cohesionless materials in which displacement of "
            "the spoils into the borehole wall during construction will "
            "result in densification of the surrounding soil (GEC-8 p. 83)."),
        "source": "GEC-8 Section 5.4.2, Eq. 5.29, pp. 83-84 (NeSmith 2002)",
    }
    if spt_n > 50.0:
        out["note"] = ("Eq. 5.29 is printed for N <= 50; N = 50 is used.")
    return out


def cfa_allowable_capacity_kN(
    ultimate_resistance_kN: float,
    safety_factor: float = 2.5,
    sf_2_conditions_met: bool = False,
) -> dict:
    """ASD allowable axial resistance for CFA piles (GEC-8 Section 6.3.1).

    GEC-8 compares the resistance computed at the geotechnical ultimate
    limit state with the service loads (Eq. 6.1, p. 138)::

        ΣQi ≤ R / SF

    CFA piles should generally be designed with a factor of safety of at
    least 2.5 (p. 138).  A factor of safety of 2.0 may be used for axial
    loads only where all four conditions of p. 138 are met:

    1. at least one conventional static load test (ASTM D1143-81) at the
       site, to 50% over the computed ultimate or to a displacement of 5%
       of the pile diameter, whichever comes first;
    2. automated monitoring systems used on production piles;
    3. site geology, stratigraphy and soil properties not highly variable;
    4. site conditions not posing difficult construction conditions for
       CFA piles.

    These are minimum values; a higher factor of safety is warranted for
    site variability, lack of redundancy, difficult construction or an
    especially critical (lifeline) structure (pp. 138-139).

    Parameters
    ----------
    ultimate_resistance_kN : float
        Computed ultimate geotechnical axial resistance R (kN).
    safety_factor : float, optional
        Factor of safety.  Default 2.5, GEC-8's general minimum.
    sf_2_conditions_met : bool, optional
        True only when all four conditions of p. 138 are met, so that
        GEC-8 allows a factor of safety of 2.0: (1) at least one
        conventional static load test (per ASTM Standard D1143-81) is
        performed at the site, to a load exceeding the computed ultimate by
        50% or to a load producing displacement equal to 5% of the pile
        diameter, whichever comes first; (2) automated monitoring systems
        are used on production piles; (3) the site geology, stratigraphy,
        and soil properties are not highly variable; (4) the site
        conditions do not pose difficult construction conditions for CFA
        piles.  Default False.

    Returns
    -------
    dict
        {'ultimate_resistance_kN': float, 'safety_factor': float,
         'allowable_resistance_kN': float, 'minimum_safety_factor': float,
         'meets_gec8_minimum': bool, 'note': str, 'source': str}

    Raises
    ------
    ValueError
        If ultimate_resistance_kN is not positive or safety_factor < 1.0.
    """
    if ultimate_resistance_kN <= 0:
        raise ValueError(
            f"ultimate_resistance_kN must be > 0, got {ultimate_resistance_kN}"
        )
    if safety_factor < 1.0:
        raise ValueError(f"safety_factor must be >= 1.0, got {safety_factor}")

    r_allow = ultimate_resistance_kN / safety_factor
    sf_min = 2.0 if sf_2_conditions_met else 2.5
    meets = safety_factor >= sf_min

    sf = float(safety_factor)
    if meets:
        note = (f"SF {sf} meets GEC-8's minimum of {sf_min}"
                + (" (all four conditions of p. 138 stated as met)."
                   if sf_2_conditions_met else "."))
    elif sf_2_conditions_met:
        note = (f"SF {sf} is below 2.0, the lowest factor of "
                "safety GEC-8 allows (p. 138).")
    else:
        note = (f"SF {sf} is below GEC-8's minimum of 2.5; "
                "2.0 may be used only where all four conditions of p. 138 "
                "are met (static load test, automated monitoring of "
                "production piles, site not highly variable, no difficult "
                "construction conditions).")

    return {
        "ultimate_resistance_kN": ultimate_resistance_kN,
        "safety_factor": safety_factor,
        "allowable_resistance_kN": round(r_allow, 1),
        "minimum_safety_factor": sf_min,
        "meets_gec8_minimum": meets,
        "note": note + " The factors are minimum values (pp. 138-139).",
        "source": "GEC-8 Section 6.3.1, Eq. 6.1, pp. 138-139",
    }


def cfa_grout_volume_factor(
    delivered_volume_L: float,
    nominal_pile_volume_L: float,
    target_factor: float = 0.0,
) -> dict:
    """Grout volume factor for CFA pile construction QC (GEC-8 Ch. 7 and 8).

    The grout factor is the ratio of the volume of grout/concrete used to
    the theoretical volume for the specified pile size (p. 167).

    Guide specification (Chapter 8): the minimum oversupply (grout volume
    factor) for the site is established during the pre-production test
    pile program and maintained in production (p. 215), and the factor of
    each pile shall be within 7.5% of the target volume factor established
    in the Pile Installation Plan as modified by that program; piles
    outside this range are unacceptable (p. 216).  Commentary (p. 215):
    typical factors range from 1.15 to 1.2 (15% to 20% oversupply); 1.15
    is in general considered a minimum; factors greater than 1.5 suggest
    soil mining or other undesirable installation effects, though they may
    be acceptable where integrity and proof tests show the pile meets the
    performance requirements and pre-production piles showed similar
    results.

    With a target factor, ``acceptable`` is the specification's 7.5% band;
    without one, it is the commentary's minimum of 1.15.

    Parameters
    ----------
    delivered_volume_L : float
        Volume of grout/concrete delivered (liters).
    nominal_pile_volume_L : float
        Theoretical pile volume based on nominal diameter and depth (liters).
    target_factor : float, optional
        Target volume factor from the Pile Installation Plan as modified by
        the pre-production test piles.  0 (default) when none is set.

    Returns
    -------
    dict
        {'delivered_volume_L': float, 'nominal_pile_volume_L': float,
         'grout_volume_factor': float, 'acceptable': bool, 'basis': str,
         'target_min': float, 'typical_range': list,
         'above_1_5': bool, 'target_factor': float,
         'target_band': list or None, 'note': str, 'source': str}

    Raises
    ------
    ValueError
        If the volumes are not positive or target_factor is negative.
    """
    if delivered_volume_L <= 0:
        raise ValueError(
            f"delivered_volume_L must be > 0, got {delivered_volume_L}"
        )
    if nominal_pile_volume_L <= 0:
        raise ValueError(
            f"nominal_pile_volume_L must be > 0, got {nominal_pile_volume_L}"
        )

    if target_factor < 0:
        raise ValueError(f"target_factor must be >= 0, got {target_factor}")

    gvf = delivered_volume_L / nominal_pile_volume_L
    above_1_5 = gvf > 1.5

    if target_factor > 0:
        band = [round(target_factor * 0.925, 3), round(target_factor * 1.075, 3)]
        acceptable = abs(gvf - target_factor) <= 0.075 * target_factor
        basis = (f"within 7.5% of the target factor {target_factor:g} "
                 f"({band[0]:g} to {band[1]:g}; p. 216)")
    else:
        band = None
        acceptable = gvf >= 1.15
        basis = ("no target factor given: the commentary's minimum of 1.15 "
                 "(p. 215); the specification's test is 7.5% of the target "
                 "set by the pre-production test piles (p. 216)")

    note = ("Inadequate volume pumped over a depth interval of 5 ft (1.5 m) "
            "is a basis for rejection of the pile (p. 215); the lowermost "
            "0.9 to 1.8 m (3 to 6 ft) should be over-supplied by about twice "
            "the theoretical volume (p. 173).")
    if above_1_5:
        note = ("A factor greater than 1.5 suggests soil mining or other "
                "undesirable installation effects; it may be acceptable if "
                "integrity and proof tests show the pile meets the "
                "performance requirements and pre-production piles showed "
                "similar results (p. 215). " + note)

    return {
        "delivered_volume_L": delivered_volume_L,
        "nominal_pile_volume_L": nominal_pile_volume_L,
        "grout_volume_factor": round(gvf, 3),
        "acceptable": acceptable,
        "basis": basis,
        "target_min": 1.15,
        "typical_range": [1.15, 1.2],
        "above_1_5": above_1_5,
        "target_factor": target_factor,
        "target_band": band,
        "note": note,
        "source": ("GEC-8 Sections 7.3.5.1 (p. 167), 7.4.2 (p. 173) and "
                   "8.3.6 (pp. 215-216)"),
    }
