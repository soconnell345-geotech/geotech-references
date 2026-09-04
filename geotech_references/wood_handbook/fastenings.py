"""Wood Handbook Chapter 8 -- Fastenings (withdrawal and lateral resistance
of nails, wood screws, lag screws, and drift bolts).

Implements the handbook's own printed empirical/mechanics equations:
  - Pre-1991 empirical withdrawal and lateral-resistance equations (all a
    function of wood specific gravity and fastener geometry only --
    ``nail_withdrawal_common``, ``nail_withdrawal_annularly_threaded``,
    ``nail_lateral_resistance_pre1991``, ``wood_screw_withdrawal``,
    ``screw_lateral_resistance_pre1991``, ``lag_screw_withdrawal``,
    ``lag_screw_lateral_resistance_pre1991``, ``drift_bolt_withdrawal``).
  - The post-1991 European Yield Model (5% offset lateral yield strength Z,
    Table 8-5) as printed in this handbook: dowel bearing strength from
    specific gravity (Eq 8-3) and the governing-mode Z calculation
    (``yield_limit_lateral_strength``). This is general dowel-fastener
    mechanics printed in the Wood Handbook itself (bearing strength
    computed from specific gravity, not looked up from a design-value
    table) -- it is NOT an NDS design-value table, so it is in scope per
    the module's exclusion of copyrighted NDS design values/adjustment
    factors.
  - The Hankinson formula for bearing strength at an angle to the grain
    (Eq 8-16), used generally (not just for fasteners).

CITATION NOTE -- equation-number collision in the source: the printed
document uses "Equation (8-2)" for TWO different relations: the annularly
threaded nail withdrawal equation (printed as "8-2a"/"8-2b", p. 8-4) and
the pre-1991 nail lateral resistance equation (printed as unlettered
"8-2", p. 8-6). Both are implemented here under descriptive function
names; each docstring notes its own printed equation label and page so
the collision is traceable rather than silently resolved.

All printed citations use the PRINTED page of General Technical Report
FPL-GTR-282 (2021 edition); ``pdf_page = printed_page + 203`` for Chapter 8
in this PDF (0-based PyMuPDF page index).

UNITS: metric throughout -- loads in N, lengths/diameters in mm, specific
gravity dimensionless (ovendry weight and volume basis, at 12% MC unless
noted), stresses in MPa/kPa as documented per function.
"""

import math

# ============================================================================
# Table 8-1 -- Sizes of bright common wire nails (printed p. 8-2, pdf_page 205)
# ============================================================================

TABLE_8_1_COMMON_NAILS = {
    "6d": {"gauge": "11-1/2", "length_mm": 50.8, "diameter_mm": 2.87},
    "8d": {"gauge": "10-1/4", "length_mm": 63.5, "diameter_mm": 3.33},
    "10d": {"gauge": "9", "length_mm": 76.2, "diameter_mm": 3.76},
    "12d": {"gauge": "9", "length_mm": 82.6, "diameter_mm": 3.76},
    "16d": {"gauge": "8", "length_mm": 88.9, "diameter_mm": 4.11},
    "20d": {"gauge": "6", "length_mm": 101.6, "diameter_mm": 4.88},
    "30d": {"gauge": "5", "length_mm": 114.3, "diameter_mm": 5.26},
    "40d": {"gauge": "4", "length_mm": 127.0, "diameter_mm": 5.72},
    "50d": {"gauge": "3", "length_mm": 139.7, "diameter_mm": 6.20},
    "60d": {"gauge": "2", "length_mm": 152.4, "diameter_mm": 6.65},
}


def table_8_1_common_nail_size(penny_size):
    """Table 8-1: bright common wire nail length/diameter by penny size
    (printed p. 8-2).

    Parameters
    ----------
    penny_size : str
        e.g. '6d', '16d', '60d' (a key of ``TABLE_8_1_COMMON_NAILS``).

    Returns
    -------
    dict
        {'penny_size', 'gauge', 'length_mm', 'diameter_mm', 'table': '8-1', ...}
    """
    key = penny_size.lower().strip()
    if key not in TABLE_8_1_COMMON_NAILS:
        raise ValueError(f"penny_size must be one of {sorted(TABLE_8_1_COMMON_NAILS)}, got {penny_size!r}")
    row = TABLE_8_1_COMMON_NAILS[key]
    return {"penny_size": key, "gauge": row["gauge"], "length_mm": row["length_mm"],
            "diameter_mm": row["diameter_mm"], "table": "8-1",
            "printed_page": "8-2", "pdf_page": 205}


# ============================================================================
# Table 8-9 -- Screw shank diameters for various screw gauges
# (printed p. 8-12, pdf_page 215)
# ============================================================================

TABLE_8_9_SCREW_SHANK_DIAMETER_MM = {
    4: 2.84, 5: 3.18, 6: 3.51, 7: 3.84, 8: 4.17, 9: 4.50, 10: 4.83,
    11: 5.16, 12: 5.49, 14: 6.15, 16: 6.81, 18: 7.47, 20: 8.13, 24: 9.45,
}


def table_8_9_screw_shank_diameter(gauge):
    """Table 8-9: wood screw shank diameter (mm) by screw gauge number
    (printed p. 8-12).

    Parameters
    ----------
    gauge : int
        Screw number/gauge (a key of ``TABLE_8_9_SCREW_SHANK_DIAMETER_MM``).

    Returns
    -------
    dict
        {'gauge', 'diameter_mm', 'table': '8-9', ...}
    """
    if gauge not in TABLE_8_9_SCREW_SHANK_DIAMETER_MM:
        raise ValueError(
            f"gauge must be one of {sorted(TABLE_8_9_SCREW_SHANK_DIAMETER_MM)}, got {gauge!r}"
        )
    return {"gauge": gauge, "diameter_mm": TABLE_8_9_SCREW_SHANK_DIAMETER_MM[gauge],
            "table": "8-9", "printed_page": "8-12", "pdf_page": 215}


# ============================================================================
# Withdrawal resistance -- nails, drift bolts, wood screws, lag screws
# ============================================================================

def nail_withdrawal_common(specific_gravity, diameter_mm, penetration_mm):
    """Eq 8-1: maximum withdrawal load of a bright common wire (smooth
    shank) nail driven into the side grain of seasoned wood or unseasoned
    wood that remains wet (printed p. 8-2).

        p = 54.12 * G^(5/2) * D * L

    Parameters
    ----------
    specific_gravity : float
        G, wood specific gravity based on ovendry weight and volume at
        12% moisture content (Table 5-3).
    diameter_mm : float
        D, nail diameter (mm).
    penetration_mm : float
        L, depth of penetration of the nail in the member holding the
        point (mm).

    Returns
    -------
    dict
        {'specific_gravity', 'diameter_mm', 'penetration_mm',
         'withdrawal_load_n', 'equation': '8-1', ...}
    """
    p = 54.12 * specific_gravity**2.5 * diameter_mm * penetration_mm
    return {
        "specific_gravity": specific_gravity, "diameter_mm": diameter_mm,
        "penetration_mm": penetration_mm, "withdrawal_load_n": p,
        "equation": "8-1", "printed_page": "8-2", "pdf_page": 205,
    }


def nail_withdrawal_annularly_threaded(specific_gravity, diameter_mm, penetration_mm):
    """Eq 8-2a: maximum withdrawal load of a bright annularly threaded nail
    (thread-crest diameter difference > 0.2 mm, thread spacing
    1.27-1.96 mm) driven into the side grain of seasoned wood (printed
    p. 8-4). See module docstring's citation note for the "8-2" label
    collision with the (unrelated) nail lateral-resistance equation.

        p = 77.57 * G^2 * D * L

    Parameters
    ----------
    specific_gravity : float
        G, wood specific gravity based on ovendry weight and ovendry
        moisture content (Table 5-2 to 5-5).
    diameter_mm : float
        D, thread-root shank diameter (mm). Valid only for the threaded
        portion of the nail.
    penetration_mm : float
        L, depth of penetration of the nail in the member holding the
        point (mm).

    Returns
    -------
    dict
        {'specific_gravity', 'diameter_mm', 'penetration_mm',
         'withdrawal_load_n', 'equation': '8-2a', ...}
    """
    p = 77.57 * specific_gravity**2 * diameter_mm * penetration_mm
    return {
        "specific_gravity": specific_gravity, "diameter_mm": diameter_mm,
        "penetration_mm": penetration_mm, "withdrawal_load_n": p,
        "equation": "8-2a", "printed_page": "8-4", "pdf_page": 207,
    }


def drift_bolt_withdrawal(specific_gravity, diameter_mm, penetration_mm):
    """Eq 8-9: ultimate withdrawal load of a round drift bolt or pin from
    the side grain of seasoned wood (printed p. 8-10). Average
    relationship for all species; presumes prebored holes 3.2 mm smaller
    in diameter than the bolt.

        p = 45.51 * G^2 * D * L

    Parameters
    ----------
    specific_gravity : float
        G, specific gravity based on ovendry weight/volume at 12% MC.
    diameter_mm : float
        D, drift bolt diameter (mm).
    penetration_mm : float
        L, length of penetration of the bolt (mm).

    Returns
    -------
    dict
        {'specific_gravity', 'diameter_mm', 'penetration_mm',
         'withdrawal_load_n', 'equation': '8-9', ...}
    """
    p = 45.51 * specific_gravity**2 * diameter_mm * penetration_mm
    return {
        "specific_gravity": specific_gravity, "diameter_mm": diameter_mm,
        "penetration_mm": penetration_mm, "withdrawal_load_n": p,
        "equation": "8-9", "printed_page": "8-10", "pdf_page": 213,
    }


def wood_screw_withdrawal(specific_gravity, diameter_mm, penetration_mm):
    """Eq 8-10: ultimate withdrawal load of a wood screw inserted into the
    side grain of seasoned wood (printed p. 8-10). Applicable for lead
    holes ~70% of root diameter (softwoods) / ~90% (hardwoods), and for
    the screw length/gauge combinations in Table 8-8.

        p = 108.25 * G^2 * D * L

    Parameters
    ----------
    specific_gravity : float
        G, specific gravity based on ovendry weight/volume at 12% MC.
    diameter_mm : float
        D, screw shank diameter (mm, Table 8-9).
    penetration_mm : float
        L, length of penetration of the threaded part of the screw (mm).

    Returns
    -------
    dict
        {'specific_gravity', 'diameter_mm', 'penetration_mm',
         'withdrawal_load_n', 'equation': '8-10', ...}
    """
    p = 108.25 * specific_gravity**2 * diameter_mm * penetration_mm
    return {
        "specific_gravity": specific_gravity, "diameter_mm": diameter_mm,
        "penetration_mm": penetration_mm, "withdrawal_load_n": p,
        "equation": "8-10", "printed_page": "8-10", "pdf_page": 213,
    }


def lag_screw_withdrawal(specific_gravity, diameter_mm, penetration_mm):
    """Eq 8-14: maximum direct withdrawal load of a lag screw from the
    side grain of seasoned wood (printed p. 8-12). Developed
    independently of the wood-screw equation (Eq 8-10) but gives
    approximately the same results.

        p = 125.4 * G^(3/2) * D^(3/4) * L

    Parameters
    ----------
    specific_gravity : float
        G, specific gravity based on ovendry weight/volume at 12% MC.
    diameter_mm : float
        D, lag screw shank diameter (mm).
    penetration_mm : float
        L, length of penetration of the threaded part (mm).

    Returns
    -------
    dict
        {'specific_gravity', 'diameter_mm', 'penetration_mm',
         'withdrawal_load_n', 'equation': '8-14', ...}
    """
    p = 125.4 * specific_gravity**1.5 * diameter_mm**0.75 * penetration_mm
    return {
        "specific_gravity": specific_gravity, "diameter_mm": diameter_mm,
        "penetration_mm": penetration_mm, "withdrawal_load_n": p,
        "equation": "8-14", "printed_page": "8-12", "pdf_page": 215,
    }


# ============================================================================
# Table 8-4 -- Coefficients for computing pre-1991 lateral-load test loads
# (printed p. 8-6, pdf_page 209)
# ============================================================================

# K coefficient (metric) for p = K*D^n (n=1.5 for nails, n=2 for
# screws/lag screws), by wood type and specific-gravity range at 15% MC.
TABLE_8_4_K_COEFFICIENTS = {
    "hardwoods": [
        {"sg_min": 0.33, "sg_max": 0.47, "nails": 50.04, "screws": 23.17, "lag_screws": 26.34},
        {"sg_min": 0.48, "sg_max": 0.56, "nails": 69.50, "screws": 31.99, "lag_screws": 29.51},
        {"sg_min": 0.57, "sg_max": 0.74, "nails": 94.52, "screws": 44.13, "lag_screws": 34.13},
    ],
    "softwoods": [
        {"sg_min": 0.29, "sg_max": 0.42, "nails": 50.04, "screws": 23.17, "lag_screws": 23.30},
        {"sg_min": 0.43, "sg_max": 0.47, "nails": 62.55, "screws": 29.79, "lag_screws": 26.34},
        {"sg_min": 0.48, "sg_max": 0.52, "nails": 76.45, "screws": 36.40, "lag_screws": 29.51},
    ],
}


def table_8_4_lateral_load_coefficient(wood_type, specific_gravity, fastener="nails"):
    """Table 8-4: pre-1991 lateral-load coefficient K (metric), by wood
    type, specific-gravity range (ovendry weight/volume at 12% MC, tested
    at 15% MC), and fastener type (printed p. 8-6).

    Parameters
    ----------
    wood_type : str
        'hardwoods' or 'softwoods'.
    specific_gravity : float
        G, used to select the matching printed specific-gravity range.
    fastener : str, optional
        'nails' (default, use with Eq 8-2 lateral, p=K*D^1.5), 'screws',
        or 'lag_screws' (use with Eq 8-13/8-15, p=K*D^2).

    Returns
    -------
    dict
        {'wood_type', 'specific_gravity', 'fastener', 'sg_range', 'k',
         'table': '8-4', ...}
    """
    wt = wood_type.lower().strip()
    if wt not in TABLE_8_4_K_COEFFICIENTS:
        raise ValueError(f"wood_type must be 'hardwoods' or 'softwoods', got {wood_type!r}")
    if fastener not in ("nails", "screws", "lag_screws"):
        raise ValueError(f"fastener must be 'nails', 'screws', or 'lag_screws', got {fastener!r}")
    for row in TABLE_8_4_K_COEFFICIENTS[wt]:
        if row["sg_min"] <= specific_gravity <= row["sg_max"]:
            return {
                "wood_type": wt, "specific_gravity": specific_gravity, "fastener": fastener,
                "sg_range": (row["sg_min"], row["sg_max"]), "k": row[fastener],
                "table": "8-4", "printed_page": "8-6", "pdf_page": 209,
            }
    raise ValueError(
        f"specific_gravity={specific_gravity} is outside the printed Table 8-4 "
        f"ranges for wood_type={wt!r}"
    )


# ============================================================================
# Lateral resistance, pre-1991 empirical equations (nails/screws/lag screws)
# ============================================================================

def nail_lateral_resistance_pre1991(k_coefficient, diameter_mm):
    """Eq 8-2 (lateral resistance form -- see module docstring's citation
    note): pre-1991 proportional-limit lateral load for a bright common
    wire nail driven into the side grain of seasoned wood, at a joint slip
    of 0.38 mm (printed p. 8-6). Requires penetration >= 10x (dense,
    G > 0.61) to 14x (G < 0.42) the nail diameter into the member holding
    the point, and side member thickness about half that penetration.

        p = K * D^(3/2)

    Ultimate loads may approach 3.5x (softwoods) or 7x (hardwoods) this
    proportional-limit value, at much larger joint slip.

    Parameters
    ----------
    k_coefficient : float
        K, from Table 8-4 (``table_8_4_lateral_load_coefficient``,
        fastener='nails').
    diameter_mm : float
        D, nail diameter (mm).

    Returns
    -------
    dict
        {'k_coefficient', 'diameter_mm', 'lateral_load_n', 'equation': '8-2', ...}
    """
    p = k_coefficient * diameter_mm**1.5
    return {
        "k_coefficient": k_coefficient, "diameter_mm": diameter_mm,
        "lateral_load_n": p, "equation": "8-2", "printed_page": "8-6", "pdf_page": 209,
    }


def screw_lateral_resistance_pre1991(k_coefficient, diameter_mm):
    """Eq 8-13: pre-1991 proportional-limit lateral load for a wood screw
    in the side grain of seasoned wood (printed p. 8-11). Applies when
    penetration of the threaded part is >= 7x the shank diameter and side
    member/main member are of similar density.

        p = K * D^2

    Parameters
    ----------
    k_coefficient : float
        K, from Table 8-4 (fastener='screws').
    diameter_mm : float
        D, screw shank diameter (mm).

    Returns
    -------
    dict
        {'k_coefficient', 'diameter_mm', 'lateral_load_n', 'equation': '8-13', ...}
    """
    p = k_coefficient * diameter_mm**2
    return {
        "k_coefficient": k_coefficient, "diameter_mm": diameter_mm,
        "lateral_load_n": p, "equation": "8-13", "printed_page": "8-11", "pdf_page": 214,
    }


TABLE_8_10_THICKNESS_FACTOR = {
    2.0: 0.62, 2.5: 0.77, 3.0: 0.93, 3.5: 1.00, 4.0: 1.07,
    4.5: 1.13, 5.0: 1.18, 5.5: 1.21, 6.0: 1.22, 6.5: 1.22,
}

TABLE_8_11_PERPENDICULAR_FACTOR = {
    4.8: 1.00, 6.4: 0.97, 7.9: 0.85, 9.5: 0.76, 11.1: 0.70, 12.7: 0.65,
    15.9: 0.60, 19.0: 0.55, 22.2: 0.52, 25.4: 0.50,
}


def lag_screw_lateral_resistance_pre1991(k_coefficient, diameter_mm):
    """Eq 8-15: pre-1991 proportional-limit lateral load for a lag screw
    in the side grain, parallel to the grain, of seasoned wood (printed
    p. 8-13). Base value assumes side-member thickness 3.5x the shank
    diameter and main-member penetration 7x (harder woods) to 11x
    (softer woods) the diameter -- see ``TABLE_8_10_THICKNESS_FACTOR`` for
    other side-member thicknesses and ``TABLE_8_11_PERPENDICULAR_FACTOR``
    for perpendicular-to-grain loading.

        p = K * D^2

    Parameters
    ----------
    k_coefficient : float
        K, from Table 8-4 (fastener='lag_screws').
    diameter_mm : float
        D, lag screw shank diameter (mm).

    Returns
    -------
    dict
        {'k_coefficient', 'diameter_mm', 'lateral_load_n', 'equation': '8-15', ...}
    """
    p = k_coefficient * diameter_mm**2
    return {
        "k_coefficient": k_coefficient, "diameter_mm": diameter_mm,
        "lateral_load_n": p, "equation": "8-15", "printed_page": "8-13", "pdf_page": 216,
    }


def table_8_10_thickness_factor(side_member_ratio):
    """Table 8-10: multiplication factor for Eq 8-15 lag-screw lateral
    loads at side-member-thickness/shank-diameter ratios other than 3.5
    (printed p. 8-13). Exact printed ratios only (no interpolation).

    Parameters
    ----------
    side_member_ratio : float
        Ratio of side-member thickness to lag-screw shank diameter (a key
        of ``TABLE_8_10_THICKNESS_FACTOR``: 2.0 to 6.5 in 0.5 steps).

    Returns
    -------
    dict
        {'side_member_ratio', 'factor', 'table': '8-10', ...}
    """
    if side_member_ratio not in TABLE_8_10_THICKNESS_FACTOR:
        raise ValueError(
            f"side_member_ratio must be one of {sorted(TABLE_8_10_THICKNESS_FACTOR)}, "
            f"got {side_member_ratio!r}"
        )
    return {"side_member_ratio": side_member_ratio,
            "factor": TABLE_8_10_THICKNESS_FACTOR[side_member_ratio],
            "table": "8-10", "printed_page": "8-13", "pdf_page": 216}


def table_8_11_perpendicular_factor(shank_diameter_mm):
    """Table 8-11: multiplication factor for Eq 8-15 lag-screw lateral
    loads applied perpendicular to grain, with the lag screw in the side
    grain of wood (printed p. 8-13). Exact printed diameters only (no
    interpolation).

    Parameters
    ----------
    shank_diameter_mm : float
        Lag screw shank diameter (mm; a key of
        ``TABLE_8_11_PERPENDICULAR_FACTOR``: 4.8 to 25.4 mm).

    Returns
    -------
    dict
        {'shank_diameter_mm', 'factor', 'table': '8-11', ...}
    """
    if shank_diameter_mm not in TABLE_8_11_PERPENDICULAR_FACTOR:
        raise ValueError(
            f"shank_diameter_mm must be one of {sorted(TABLE_8_11_PERPENDICULAR_FACTOR)}, "
            f"got {shank_diameter_mm!r}"
        )
    return {"shank_diameter_mm": shank_diameter_mm,
            "factor": TABLE_8_11_PERPENDICULAR_FACTOR[shank_diameter_mm],
            "table": "8-11", "printed_page": "8-13", "pdf_page": 216}


# ============================================================================
# Eq 8-16 -- Hankinson formula (bearing/loading at an angle to the grain)
# (printed p. 8-13, pdf_page 216)
# ============================================================================

def hankinson_bearing_strength(p_parallel, q_perpendicular, theta_deg):
    """Eq 8-16: the Hankinson formula for bearing strength (or load) of
    wood at an angle theta to the grain, given the parallel- and
    perpendicular-to-grain values (printed p. 8-13). Used for bolt/lag-
    screw bearing at an angle to grain, and generally wherever an
    angle-to-grain interaction is needed.

        N = P*Q / (P*sin^2(theta) + Q*cos^2(theta))

    Parameters
    ----------
    p_parallel : float
        P, load or stress parallel to the grain.
    q_perpendicular : float
        Q, load or stress perpendicular to the grain.
    theta_deg : float
        theta, inclination angle from the grain direction (degrees).

    Returns
    -------
    dict
        {'p_parallel', 'q_perpendicular', 'theta_deg', 'n_value',
         'equation': '8-16', ...}
    """
    theta = math.radians(theta_deg)
    n = (p_parallel * q_perpendicular) / (
        p_parallel * math.sin(theta) ** 2 + q_perpendicular * math.cos(theta) ** 2
    )
    return {
        "p_parallel": p_parallel, "q_perpendicular": q_perpendicular,
        "theta_deg": theta_deg, "n_value": n, "equation": "8-16",
        "printed_page": "8-13", "pdf_page": 216,
    }


# ============================================================================
# Post-1991 yield (European Yield Model) lateral resistance -- Eq 8-3,
# Table 8-5 (printed pp. 8-7, pdf_page 210)
# ============================================================================

def dowel_bearing_strength(specific_gravity):
    """Eq 8-3: dowel bearing strength Fe (MPa), empirically related to
    specific gravity (printed p. 8-7). Used for both main-member (Fem)
    and side-member (Fes) dowel bearing stress in the yield model.

        Fe = 114.5 * G^1.84

    Parameters
    ----------
    specific_gravity : float
        G, ovendry weight and volume basis.

    Returns
    -------
    dict
        {'specific_gravity', 'fe_mpa', 'equation': '8-3', ...}
    """
    fe = 114.5 * specific_gravity**1.84
    return {
        "specific_gravity": specific_gravity, "fe_mpa": fe, "equation": "8-3",
        "printed_page": "8-7", "pdf_page": 210,
    }


def yield_limit_lateral_strength(fastener_type, diameter_mm, fem_mpa, fes_mpa,
                                  fyb_mpa, side_member_thickness_mm=None,
                                  main_member_penetration_mm=None):
    """Table 8-5: 5% offset lateral yield strength Z for a two-member
    dowel-type fastener joint (nail, spike, or screw), by governing yield
    mode (printed p. 8-7). The yield model theory applies generally to
    dowel fasteners (nails, screws, bolts, lag screws); the main- and
    side-member dowel bearing strengths (Fem, Fes) are found from specific
    gravity via ``dowel_bearing_strength`` (Eq 8-3).

    Computes all applicable modes and returns the governing (minimum) Z,
    per standard yield-model design practice:
      - Mode Is: wood-bearing failure in the side member.
          Z = D * ts * Fes                                (nails AND screws)
      - Mode IIIm: wood bearing + one plastic hinge, main member (nails
        only -- not applicable to screws in this table).
          Z = k1*D*p*Fem / (1 + 2*Re)
      - Mode IIIs: wood bearing + one plastic hinge, side member.
          Z = k2*D*ts*Fem / (2 + Re)                        (nails)
          Z = k3*D*ts*Fem / (2 + Re)                        (screws)
      - Mode IV: wood bearing + two plastic hinges.
          Z = D^2 * sqrt(2*Fem*Fyb / (3*(1+Re)))             (nails)
          Z = D^2 * sqrt(1.75*Fem*Fyb / (3*(1+Re)))          (screws)

    with Re = Fem/Fes and (nails):
        k1 = -1 + sqrt(2*(1+Re) + 2*Fyb*(1+2*Re)*D^2 / (3*Fem*p^2))
        k2 = -1 + sqrt(2*(1+Re)/Re + 2*Fyb*(2+Re)*D^2 / (3*Fem*ts^2))
    and (screws):
        k3 = -1 + sqrt(2*(1+Re)/Re + Fyb*(2+Re)*D^2 / (2*Fem*ts^2))

    Parameters
    ----------
    fastener_type : str
        'nail' (includes Mode IIIm) or 'screw' (Mode IIIm not applicable).
    diameter_mm : float
        D. For annularly threaded nails, thread-root diameter; for screws,
        shank diameter (or root diameter if the threaded portion is in the
        shear plane).
    fem_mpa : float
        Dowel bearing stress of the main member (member holding the
        point), MPa (``dowel_bearing_strength``).
    fes_mpa : float
        Dowel bearing stress of the side member, MPa.
    fyb_mpa : float
        Bending yield stress of the fastener, MPa (ASTM F1575; typically
        551-689 MPa for common nails).
    side_member_thickness_mm : float, optional
        ts. Required for modes Is and IIIs/IV.
    main_member_penetration_mm : float, optional
        p, penetration of the nail/spike point in the main member.
        Required for mode IIIm (nails only).

    Returns
    -------
    dict
        {'re', 'z_is', 'z_iiim' (None for screws), 'z_iiis', 'z_iv',
         'z_governing', 'governing_mode', 'table': '8-5', ...}
    """
    if fastener_type not in ("nail", "screw"):
        raise ValueError(f"fastener_type must be 'nail' or 'screw', got {fastener_type!r}")
    re = fem_mpa / fes_mpa
    d = diameter_mm
    modes = {}

    if side_member_thickness_mm is not None:
        ts = side_member_thickness_mm
        modes["is"] = d * ts * fes_mpa

    if fastener_type == "nail" and main_member_penetration_mm is not None:
        p = main_member_penetration_mm
        k1 = -1.0 + math.sqrt(2.0 * (1.0 + re) + 2.0 * fyb_mpa * (1.0 + 2.0 * re) * d**2 / (3.0 * fem_mpa * p**2))
        modes["iiim"] = k1 * d * p * fem_mpa / (1.0 + 2.0 * re)

    if side_member_thickness_mm is not None:
        ts = side_member_thickness_mm
        if fastener_type == "nail":
            k2 = -1.0 + math.sqrt(2.0 * (1.0 + re) / re + 2.0 * fyb_mpa * (2.0 + re) * d**2 / (3.0 * fem_mpa * ts**2))
            modes["iiis"] = k2 * d * ts * fem_mpa / (2.0 + re)
        else:
            k3 = -1.0 + math.sqrt(2.0 * (1.0 + re) / re + fyb_mpa * (2.0 + re) * d**2 / (2.0 * fem_mpa * ts**2))
            modes["iiis"] = k3 * d * ts * fem_mpa / (2.0 + re)

    if fastener_type == "nail":
        modes["iv"] = d**2 * math.sqrt(2.0 * fem_mpa * fyb_mpa / (3.0 * (1.0 + re)))
    else:
        modes["iv"] = d**2 * math.sqrt(1.75 * fem_mpa * fyb_mpa / (3.0 * (1.0 + re)))

    if not modes:
        raise ValueError(
            "provide at least side_member_thickness_mm (modes Is/IIIs) or "
            "main_member_penetration_mm (mode IIIm, nails)"
        )
    governing_mode, z_governing = min(modes.items(), key=lambda kv: kv[1])
    return {
        "fastener_type": fastener_type, "re": re,
        "z_is": modes.get("is"), "z_iiim": modes.get("iiim"),
        "z_iiis": modes.get("iiis"), "z_iv": modes.get("iv"),
        "z_governing": z_governing, "governing_mode": governing_mode,
        "table": "8-5", "printed_page": "8-7", "pdf_page": 210,
    }
