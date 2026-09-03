"""EM 1110-2-2107 paragraph 4.4 (HSS Support Acceleration) + Appendix D
(Simplified Ground Motion Amplification Estimate for Concrete Gravity Dams).

For HSS mounted on a concrete gravity dam (e.g. spillway Tainter-gate
trunnions), the acceleration at the HSS support during an earthquake is
amplified above the free-field peak ground acceleration (PGA) by the dam's
own dynamic response. This module implements the Westergaard hydrodynamic
pressure (Eq 4.3), the "pseudo-dynamic" (Chopra & Tan 1989) single-degree-
of-freedom amplification method printed in both Chapter 4 (Eq 4.4-4.6,
Table 4.2) and derived in full in Appendix D (Eq D.1-D.12), and the period
estimate (Eq D.11/D.12). Printed pages per the 1 August 2022 edition
(pdf_page = printed_page + 8).

SOURCE-DOCUMENT INCONSISTENCIES (transcribed as printed, flagged here --
doctrine: never silently "fix" the manual, verify against its own worked
example and note the discrepancy):

1. Table 4.2 (printed p. 31) cites "Equation 4.7" as the formula for ac vs
   height/width ratio. Equation 4.7 (printed p. 32) is actually one of the
   THREE EARTHQUAKE LOAD COMBINATIONS (see ``loads.earthquake_load_
   combination``), unrelated to Table 4.2's height/width-ratio subject
   matter (the scale factor Gamma-tilde). Table 4.2 also appears on printed
   p. 31, ONE PAGE BEFORE Eq 4.7 is even introduced (printed p. 32) -- a
   forward reference to an equation about an unrelated topic. Independent
   corroboration: Appendix D derives the IDENTICAL Gamma-tilde-based
   formula as its own Eq D.8 (general) and Eq D.10 (normalized amplification
   form), and Chapter 4's own Eq 4.4/4.6 use Gamma-tilde directly. This is
   almost certainly an editorial cross-reference error for "Equation 4.4"
   (or D.8) in the source document. This module implements the actual
   Gamma-tilde-based computation (``hss_support_acceleration``,
   ``amplification_factor``) and ``table_4_2_scale_factor`` returns the
   printed citation string as-is for traceability.

2. Eq 4.4 (printed p. 30) introduces a "Pseudo Static Correction Factor"
   C = 0.75 multiplying the whole bracket: ac = C*[(SA*Gamma-tilde -
   PGA)*phi(z) + PGA]. Eq 4.6 (printed p. 32), the very next closed-form
   equation in the SAME chapter, omits C entirely: ac = [SA*Gamma-tilde -
   PGA]*phi(z) + PGA. Appendix D's parallel derivation (Eq D.8, D.10) also
   never introduces a C factor. The Appendix D worked example (Steps 4-5,
   printed pp. 399-402) reproduces ac = 1.6g using the NO-C form exactly
   (verified below); applying C = 0.75 would give 1.2g, not the printed
   1.6g. This module therefore implements the validated no-C closed form
   (Eq 4.6/D.8, ``hss_support_acceleration``) as the primary function, and
   provides ``hss_support_acceleration_with_c_factor`` implementing Eq 4.4
   literally (with C exposed) for traceability -- the two will disagree by
   the factor C on any nonzero PGA/SA difference; use the no-C form for
   design unless the discrepancy is resolved by the design authority.

3. Paragraph F.3.5 (printed p. 435): the narrative states the resultant
   angle theta_p is "the arctangent of the horizontal component over the
   vertical component" (Ph/Pv), but the worked example (printed p. 440)
   computes theta_p = atan(Pv/Ph) = 0.293 rad, matching Pv/Ph, not Ph/Pv.
   This module (``resultant_angle_from_horizontal`` in
   ``tainter_gate_loads.py``) implements atan(Pv/Ph), the form the worked
   number actually confirms.
"""

import math

# ============================================================================
# Eq 4.3 -- Westergaard hydrodynamic pressure (printed p. 28, pdf_page 36)
# ============================================================================

def westergaard_pressure(gamma_w, ac, h, y):
    """Eq 4.3: Westergaard (1933) hydrodynamic pressure at depth y below the
    pool surface, for simplified seismic screening (printed p. 28).

        p = gamma_w * ac * sqrt(H * y)

    Parameters
    ----------
    gamma_w : float
        Unit weight of water.
    ac : float
        Maximum acceleration at the HSS support in the upstream/downstream
        direction, as a fraction of g (``hss_support_acceleration``).
    h : float
        Pool depth to dam foundation.
    y : float
        Distance below the pool surface.

    Returns
    -------
    dict
        {'p', 'equation': '4.3', 'printed_page': '28', 'pdf_page': 36}
    """
    p = gamma_w * ac * math.sqrt(h * y)
    return {"p": p, "equation": "4.3", "printed_page": "28", "pdf_page": 36}


# ============================================================================
# Eq 4.5/D.9 -- fundamental mode shape (printed p. 32 / p. 398, pdf 40/406)
# ============================================================================

def mode_shape_phi(z, hs):
    """Eq 4.5 (= Eq D.9): the fundamental mode shape phi(z) for a concrete
    gravity dam, found by Chopra & Tan (1989) to represent gravity dams of
    varying heights well enough that a single shape suffices (printed
    p. 32 / p. 398).

        phi(z) = 23.41 * sin^2(2*pi*z / (32.18*Hs) + 0.0122)

    Parameters
    ----------
    z : float
        Height of the HSS (e.g. trunnion) above the dam foundation.
    hs : float
        Full dam height (foundation to crest).

    Returns
    -------
    dict
        {'phi', 'equation': '4.5/D.9', 'printed_page': '32/398', 'pdf_page': '40/406'}
    """
    phi = 23.41 * math.sin(2 * math.pi * z / (32.18 * hs) + 0.0122) ** 2
    return {"phi": phi, "equation": "4.5/D.9", "printed_page": "32/398", "pdf_page": "40/406"}


# ============================================================================
# Table 4.2 -- ac vs height-to-width ratio (printed p. 31, pdf_page 39)
# ============================================================================

_TABLE_4_2 = [
    # (upper bound description, gamma_tilde or 'pga')
    ("gt_1h_1.5w", 2.8),
    ("1h_1.5w_to_1h_3w", 1.5),
    ("lt_1h_3w", "pga"),
]


def table_4_2_scale_factor(height_to_width_category):
    """Table 4.2: scale factor Gamma-tilde by dam height-to-width ratio
    (printed p. 31). See the module docstring, item 1, for the "Equation
    4.7" citation printed in this table -- it is reproduced here verbatim
    for traceability, but the actual computation is Eq 4.4/4.6 (Appendix D
    Eq D.8), implemented in ``hss_support_acceleration``.

    Parameters
    ----------
    height_to_width_category : str
        'gt_1h_1.5w' (height/width ratio greater than 1h:1.5w -- tall,
        heavily tapered dams; Gamma-tilde = 2.8), '1h_1.5w_to_1h_3w'
        (intermediate; Gamma-tilde = 1.5), or 'lt_1h_3w' (wide, low-taper
        dams; use PGA directly, i.e. no amplification -- amplification
        factor A(z) = 1.0).

    Returns
    -------
    dict
        {'height_to_width_category', 'gamma_tilde' (float or 'pga'),
         'printed_citation': 'Equation 4.7' (as printed; see module
         docstring), 'table': '4.2', 'printed_page': '31', 'pdf_page': 39}
    """
    table = dict(_TABLE_4_2)
    if height_to_width_category not in table:
        raise ValueError(
            f"height_to_width_category must be one of {sorted(table)}, "
            f"got {height_to_width_category!r}"
        )
    return {
        "height_to_width_category": height_to_width_category,
        "gamma_tilde": table[height_to_width_category],
        "printed_citation": "Equation 4.7",
        "table": "4.2", "printed_page": "31", "pdf_page": 39,
    }


# ============================================================================
# Eq 4.6/D.8 -- HSS support acceleration, no-C closed form (printed p. 32 /
# p. 400, pdf 40/408). VALIDATED against the Appendix D worked example.
# ============================================================================

def hss_support_acceleration(sa, gamma_tilde, pga, z, hs):
    """Eq 4.6 (= Eq D.8): HSS support acceleration ac via the pseudo-dynamic
    (Chopra & Tan 1989) amplification method (printed p. 32 / p. 400). This
    is the validated closed form -- see module docstring item 2 for why the
    "C = 0.75" factor in Eq 4.4 is NOT applied here.

        ac = [SA(T1,zeta)*Gamma~ - PGA] * phi(z) + PGA
           = [SA(T1,zeta)*Gamma~ - PGA] * 23.41*sin^2(2*pi*z/(32.18*Hs)+0.0122) + PGA

    Verified against the Appendix D worked example (printed pp. 399-401,
    Steps 1-5): Hs=350 ft, z=311.5 ft (z/Hs=0.89), phi(z)=0.8,
    Gamma~=2.8, SA=0.684g, PGA=0.325g -> ac = 1.6g (amplification 4.9); and
    with a period estimate (Eq D.11/D.12) giving SA=0.55g -> ac = 1.3g
    (amplification 4.0).

    Parameters
    ----------
    sa : float
        Spectral acceleration SA(T1, zeta) at the structure's period and
        damping ratio, g (from a site response spectrum; damping typically
        assumed 5%, paragraph D.2.5).
    gamma_tilde : float
        Scale factor (``table_4_2_scale_factor``, or 2.8 for gravity dams
        per Appendix D's general recommendation, printed p. 398).
    pga : float
        Peak ground acceleration, g.
    z : float
        Height of the HSS above the dam foundation.
    hs : float
        Full dam height.

    Returns
    -------
    dict
        {'ac', 'phi_z', 'equation': '4.6/D.8', 'printed_page': '32/400',
         'pdf_page': '40/408'}
    """
    phi_z = mode_shape_phi(z, hs)["phi"]
    ac = (sa * gamma_tilde - pga) * phi_z + pga
    return {"ac": ac, "phi_z": phi_z, "equation": "4.6/D.8",
            "printed_page": "32/400", "pdf_page": "40/408"}


def hss_support_acceleration_with_c_factor(sa, gamma_tilde, pga, z, hs, c=0.75):
    """Eq 4.4: HSS support acceleration ac WITH the printed "Pseudo Static
    Correction Factor" C (printed p. 30). See module docstring item 2 --
    this literal form of Eq 4.4 is NOT what the Appendix D worked example
    (nor Eq 4.6) actually computes; provided for traceability to the
    as-printed equation only.

        ac = C * {[SA(T1,zeta)*Gamma~ - PGA] * phi(z) + PGA}

    Parameters
    ----------
    c : float, optional
        Pseudo Static Correction Factor; printed value 0.75 (default).
    (other parameters as ``hss_support_acceleration``)

    Returns
    -------
    dict
        {'ac', 'c', 'phi_z', 'equation': '4.4', 'printed_page': '30',
         'pdf_page': 38}
    """
    phi_z = mode_shape_phi(z, hs)["phi"]
    ac = c * ((sa * gamma_tilde - pga) * phi_z + pga)
    return {"ac": ac, "c": c, "phi_z": phi_z, "equation": "4.4",
            "printed_page": "30", "pdf_page": 38}


def amplification_factor(sa, gamma_tilde, pga, z, hs):
    """Eq D.10: the amplification factor A(z) = ac / PGA, normalized form
    (printed p. 399).

        A(z) = {[Gamma~*SA(T,zeta) - PGA] + PGA} / PGA   (at the top of a
                                                            structure, z=Hs
                                                            i.e. phi(z)=1;
                                                            general form
                                                            below)
        A(z) = ac(z) / PGA

    Verified against the Appendix D worked example: A(z) = 1.6/0.325 = 4.9
    (peak-SA variant) and 1.3/0.325 = 4.0 (period-based variant).

    Returns
    -------
    dict
        {'a_z', 'ac', 'equation': 'D.10', 'printed_page': '399', 'pdf_page': 407}
    """
    ac = hss_support_acceleration(sa, gamma_tilde, pga, z, hs)["ac"]
    return {"a_z": ac / pga, "ac": ac, "equation": "D.10",
            "printed_page": "399", "pdf_page": 407}


# ============================================================================
# Eq D.11, D.12 -- dam fundamental period estimate (printed p. 401, pdf 409)
# ============================================================================

def dam_period_estimate(hs, es):
    """Eq D.11/D.12 (Chopra & Tan 1989, as simplified in Appendix D): an
    estimate of the dam's fundamental period, for use with a period-based
    (rather than peak-spectral-acceleration) evaluation of Eq D.8 (printed
    p. 401).

        beta = 2.49*(Hs/sqrt(Es)) + 1.56                          [Eq D.12]
        T = beta * Hs/sqrt(Es)                                    [Eq D.11]

    Applicability (printed p. 401): valid when the pool is near the top of
    the dam (>80% of structure height) and the foundation modulus is near
    that of the dam concrete (i.e. a relatively hard rock foundation); Es
    and Hs must be in consistent units matching the worked example (psi,
    ft) for beta's calibrated coefficients to apply as printed.

    Verified against the Appendix D worked example (printed p. 402):
    Hs=350 ft, Es=4e6 psi -> beta=2.0, T=0.35 sec.

    Parameters
    ----------
    hs : float
        Dam height, ft.
    es : float
        Modulus of elasticity of the dam concrete, psi.

    Returns
    -------
    dict
        {'beta', 't_sec', 'equation': 'D.11/D.12', 'printed_page': '401',
         'pdf_page': 409}
    """
    beta = 2.49 * (hs / math.sqrt(es)) + 1.56
    t_sec = beta * hs / math.sqrt(es)
    return {"beta": beta, "t_sec": t_sec, "equation": "D.11/D.12",
            "printed_page": "401", "pdf_page": 409}


# ============================================================================
# Table D.1 -- measured amplification factors (context data, printed p. 389)
# ============================================================================

TABLE_D_1_MEASURED_AMPLIFICATION = {
    "Dworshak": {"height_ft": 717, "event": "Lincoln, MT (2017)", "amplification_factor": 9.06},
    "Chief Joseph": {"height_ft": 236, "event": "Nisqually (2001)", "amplification_factor": 4.69},
    "Wynoochee_Nisqually": {"height_ft": 175, "event": "Nisqually, WA (2001)", "amplification_factor": 3.58},
    "Wynoochee_Satsop": {"height_ft": 175, "event": "Satsop, WA (1999)", "amplification_factor": 2.97},
    "Detroit": {"height_ft": 463, "event": "Scotts Mills (1993)", "amplification_factor": 7.72},
    "Hakkagawa": {"height_ft": 171, "event": "Honshu (2007)", "amplification_factor": 5.12},
    "Gin-Mian": {"height_ft": 115, "event": "Meinong (2016)", "amplification_factor": 1.24},
    "Takou": {"height_ft": 252, "event": "Tohoku Aftershock (2011)", "amplification_factor": 4.71},
    "Kasho": {"height_ft": 152, "event": "Western Tattori (2000)", "amplification_factor": 3.87},
}


def table_d1_measured_amplification(dam=None):
    """Table D.1: measured base-to-crest acceleration amplification factors
    at nine instrumented concrete gravity dams (printed p. 389). Background
    context motivating the simplified method -- not a design formula.

    Parameters
    ----------
    dam : str, optional
        A key of ``TABLE_D_1_MEASURED_AMPLIFICATION``. If omitted, the full
        table is returned.

    Returns
    -------
    dict
    """
    if dam is None:
        return {"dams": dict(TABLE_D_1_MEASURED_AMPLIFICATION), "table": "D.1",
                "printed_page": "389", "pdf_page": 397}
    if dam not in TABLE_D_1_MEASURED_AMPLIFICATION:
        raise ValueError(f"Unknown dam {dam!r}; see TABLE_D_1_MEASURED_AMPLIFICATION")
    row = dict(TABLE_D_1_MEASURED_AMPLIFICATION[dam])
    row.update({"dam": dam, "table": "D.1", "printed_page": "389", "pdf_page": 397})
    return row
