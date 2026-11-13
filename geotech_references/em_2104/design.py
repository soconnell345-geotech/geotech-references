"""EM 1110-2-2104 Appendix D-2 -- Design Equations and Procedures (DESIGN
direction).

Given a required nominal Mn/Pn, solve directly for the reinforcement area
(As, As') -- the complement of ``flexure_axial.py``'s Appendix B
INVESTIGATION equations (given As/As', find capacity). Printed pages per the
1 Nov 2023 edition (pdf_page = printed_page + 5).

Verified against Appendix D-3 (singly reinforced retaining-wall stem design,
As = 0.43 sq in), Appendix D-5 Step 3 (coastal-floodwall stem, As = 2.73 sq
in/ft), and Appendix D-4 (combined flexure+axial doubly reinforced wall,
which checks an EXISTING design via the Appendix B investigation path in
``flexure_axial.py`` rather than this module -- see that module's docstring).
"""

import math

from .flexure_axial import DEFAULT_ES_KSI, DEFAULT_EC


# ============================================================================
# Eq D-1 to D-9, Table D-1 -- singly reinforced design (printed pp. 69-73)
# ============================================================================

def kd_table_d1(rho_over_rho_b, beta1, fy, es=DEFAULT_ES_KSI, ec=DEFAULT_EC):
    """Table D-1's general Kd formula (printed p. 73): Kd, the ku value
    (dimensionless) at a target reinforcement ratio given as a fraction of
    the balanced ratio (e.g. 0.25 or 0.50 per paragraphs 3-4b(2) and 3-6),
    from fy in ksi.

        Kd = (rho/rho_b) * beta1 * Es*ec / (Es*ec + fy)

    Note this is identical in form to Eq 4-3/B-7's kb with rho/rho_b
    scaling it down from the balanced value.

    Parameters
    ----------
    rho_over_rho_b : float
        Target tension reinforcement ratio as a fraction of the balanced
        ratio, rho/rho_b (0.25 recommended, paragraph 3-4b(2); 0.50 the
        maximum, paragraph 3-6).
    beta1 : float
        ACI 318-19 beta_1 (``flexure_axial.aci_beta1``), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of es).
    es : float, optional
        Steel modulus of elasticity Es, ksi (default 29,000 ksi).
    ec : float, optional
        Maximum usable concrete strain, 0.003 (paragraph 4-1d(1)).

    Returns
    -------
    dict
        {'kd', 'rho_over_rho_b', 'table': 'D-1', 'printed_page': '73',
         'pdf_page': 78}
    """
    kd = rho_over_rho_b * beta1 * es * ec / (es * ec + fy)
    return {"kd": kd, "rho_over_rho_b": rho_over_rho_b, "table": "D-1",
            "printed_page": "73", "pdf_page": 78}


def minimum_effective_depth(mn, b, fc_prime, kd):
    """Table D-1 / Eq D-5: minimum effective depth dd at a target
    reinforcement ratio (printed p. 71).

        dd = sqrt( Mn / (0.85*fc'*Kd*b*(1 - Kd/2)) )

    If d >= dd for a trial section, the member has adequate depth to meet
    the target steel-ratio limit and As follows directly from Eq D-8/D-9
    (``design_singly_reinforced``).

    Parameters
    ----------
    mn : float
        Required nominal moment (Mu/phi), in-kips (consistent with fc' in
        ksi and b, dd in inches).
    b : float
        Section width, in.
    fc_prime : float
        Concrete compressive strength, ksi.
    kd : float
        From ``kd_table_d1`` (or a Table D-1 tabulated value).

    Returns
    -------
    dict
        {'dd', 'equation': 'D-5', 'printed_page': '71', 'pdf_page': 76}
    """
    dd = math.sqrt(mn / (0.85 * fc_prime * kd * b * (1 - kd / 2.0)))
    return {"dd": dd, "equation": "D-5", "printed_page": "71", "pdf_page": 76}


def max_moment_at_rho_limit(fc_prime, kd, b, d, h, pn=0.0):
    """Eq D-6, D-7: M_DS, kip-in. (returned as 'mdl'), the maximum bending
    moment a member may
    carry and remain within the target reinforcement-ratio limit, with the
    stress-block depth ad, in., from fc' in ksi, dimensions in inches and
    Pn in kips (printed p. 72).

        ad = Kd * d                                          [Eq D-7]
        M_DS = 0.85*fc'*ad*b*(d - ad/2) - (d - h/2)*Pn        [Eq D-6]

    If the required Mn <= M_DS, the trial section is adequate
    (``design_singly_reinforced`` may be used directly); otherwise the
    section must be enlarged or doubly reinforced
    (``design_doubly_reinforced``).

    Parameters
    ----------
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    kd : float
        Kd at the target reinforcement ratio (``kd_table_d1``),
        dimensionless.
    b : float
        Design width of member, in.
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.
    h : float
        Overall thickness of the section, in.
    pn : float, optional
        Nominal axial load Pn, kips; positive for compression, negative for
        tension (default 0, pure flexure).

    Returns
    -------
    dict
        {'ad', 'mdl' (the print's M_DS), 'equation': 'D-6/D-7', 'printed_page': '72',
         'pdf_page': 77}
    """
    ad = kd * d
    mdl = 0.85 * fc_prime * ad * b * (d - ad / 2.0) - (d - h / 2.0) * pn
    return {"ad": ad, "mdl": mdl, "equation": "D-6/D-7",
            "printed_page": "72", "pdf_page": 77}


def design_singly_reinforced(mn, pn, d, h, b, fc_prime, fy):
    """Eq D-8, D-9: direct design of a singly reinforced member: the
    required tension reinforcement area As, sq in., and Ku
    (dimensionless), for a required nominal moment Mn (kip-in.) and axial
    load Pn (kips), with strengths in ksi and dimensions in inches (printed
    p. 72).

        Ku = 1 - sqrt(1 - [Mn + Pn*(d - h/2)] / (0.425*fc'*b*d^2))
        As = (0.85*fc'*Ku*b*d - Pn) / fy

    Pn positive = compression, negative = tension (or 0 for pure flexure).

    Verified against Appendix D-3 (Mn = 147 k-in, d = 6 in, h ~ 9 in
    (unused, Pn = 0), b = 12 in, fc' = 4 ksi, fy = 60 ksi): Ku = 0.105,
    As = 0.43 sq in. Also Appendix D-5 Step 3 (Mn = 476 k-ft/ft, Pn = 0,
    d = 36.5 in, fc' = 5 ksi): As = 2.73 sq in/ft.

    Parameters
    ----------
    mn : float
        Required nominal moment Mn = Mu/phi, kip-in.
    pn : float
        Required nominal axial load Pn, kips; positive for compression,
        negative for tension, 0 for pure flexure.
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.
    h : float
        Overall thickness of the section, in.
    b : float
        Design width of member, in.
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    fy : float
        Specified yield strength of reinforcement, ksi.

    Returns
    -------
    dict
        {'ku', 'as_required', 'equation': 'D-8/D-9', 'printed_page': '72',
         'pdf_page': 77}
    """
    radicand = 1 - (mn + pn * (d - h / 2.0)) / (0.425 * fc_prime * b * d ** 2)
    if radicand < 0:
        raise ValueError(
            "Negative radicand in Eq D-8 -- section is too small for the "
            "required Mn/Pn (over-reinforced or inadequate depth)."
        )
    ku = 1 - math.sqrt(radicand)
    as_required = (0.85 * fc_prime * ku * b * d - pn) / fy
    return {
        "ku": ku, "as_required": as_required, "equation": "D-8/D-9",
        "printed_page": "72", "pdf_page": 77,
    }


# ============================================================================
# Eq D-3, D-4 -- doubly reinforced design (printed pp. 70-71)
# ============================================================================

def design_doubly_reinforced(mn, pn, d, dprime, h, b, fc_prime, fy,
                              rho_over_rho_b=0.25, beta1=None,
                              es=DEFAULT_ES_KSI, ec=DEFAULT_EC):
    """Eq D-3, D-4, D-6, D-7: direct design of a doubly reinforced member:
    the required tension and compression reinforcement areas As and As',
    sq in., when the required Mn (kip-in.) exceeds M_DS (the singly
    reinforced limit at the target reinforcement ratio), with strengths in
    ksi, dimensions in inches and Pn in kips (printed pp. 70-72).

    Procedure:
      1. Kd, M_DS at the target rho/rho_b (``kd_table_d1``,
         ``max_moment_at_rho_limit``).
      2. Compression-steel stress fs' at ad = Kd*d, from strain
         compatibility (paragraph D-2b, printed p. 71): fs' =
         (ad - beta1*d')*ec*Es/ad, which the page prints with no bound;
         held at fy by the library (``limit_governs``, ``fs_prime_unlimited``
         and a note when it governs), and refused where it is not positive
         (the compression steel not in compression: D-4 gives no As'). ad
         is set by the target ratio, not solved for, so with fs' at fy
         Eqs D-3 and D-4 still balance the section's forces and moments.
      3. As' = (Mn - M_DS) / [fs'*(d - d')]                      [Eq D-4]
      4. As = (0.85*fc'*Kd*b*d - Pn + As'*fs') / fy                [Eq D-3]

    Parameters
    ----------
    mn : float
        Required nominal moment Mn = Mu/phi, kip-in.
    pn : float
        Required nominal axial load Pn, kips; positive for compression,
        negative for tension, 0 for pure flexure.
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.
    dprime : float
        Depth d' from the extreme compression fiber to the centroid of the
        compression reinforcement, in.
    h : float
        Overall thickness of the section, in.
    b : float
        Design width of member, in.
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of es).
    rho_over_rho_b : float, optional
        Target reinforcement ratio as a fraction of balanced (0.25 default,
        per the traditional deflection-control limit; 0.50 is the mandatory
        ceiling, paragraph 3-6).
    beta1 : float, optional
        ACI 318-19 beta_1; computed from fc_prime (ksi) if omitted.
    es : float, optional
        Steel modulus of elasticity Es, ksi (default 29,000 ksi).
    ec : float, optional
        Maximum usable concrete strain, 0.003 (paragraph 4-1d(1)).

    Returns
    -------
    dict
        {'kd', 'mdl' (M_DS), 'fs_prime', 'as_prime_required', 'as_required',
         'equation': 'D-3/D-4/D-6/D-7', ...}
    """
    from .flexure_axial import aci_beta1
    # REF-76: fs' is held at fy below; an fy, Es or ec no steel or
    # concrete has is refused rather than used as that bound.
    for name, val in (("fy", fy), ("es", es), ("ec", ec)):
        if val is None or val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    if beta1 is None:
        beta1 = aci_beta1(fc_prime)
    kd_result = kd_table_d1(rho_over_rho_b, beta1, fy, es, ec)
    kd = kd_result["kd"]
    mdl_result = max_moment_at_rho_limit(fc_prime, kd, b, d, h, pn)
    mdl, ad = mdl_result["mdl"], mdl_result["ad"]

    if mn <= mdl:
        raise ValueError(
            "Required Mn does not exceed M_DS (Eq D-6) -- a singly reinforced section "
            "is adequate; use design_singly_reinforced instead."
        )

    fs_raw = (ad - beta1 * dprime) * ec * es / ad
    if fs_raw <= 0:
        raise ValueError(
            f"fs' = (ad - beta1*d') ec Es / ad = {fs_raw:.4g} ksi at ad = "
            f"{ad:.4g} in. (printed p. 71): the compression steel is not in "
            "compression, so Eq D-4 gives no As' (the library's reading: D-4 "
            "asks the compression steel to carry Mn - M_DS). Use a deeper "
            "section or a smaller d'.")
    fs_prime = min(fy, fs_raw)
    as_prime = (mn - mdl) / (fs_prime * (d - dprime))
    as_required = (0.85 * fc_prime * kd * b * d - pn + as_prime * fs_prime) / fy

    out = {
        "kd": kd, "ad": ad, "mdl": mdl, "fs_prime": fs_prime,
        "as_prime_required": as_prime, "as_required": as_required,
        "equation": "D-3/D-4/D-6/D-7", "printed_page": "70-72",
        "pdf_page": "75-77", "limit_governs": fs_raw > fy,
    }
    if fs_raw > fy:
        out["fs_prime_unlimited"] = fs_raw
        out["note"] = (
            f"fs' = {fs_raw:.4g} ksi from (ad - beta1*d') ec Es / ad (printed "
            f"p. 71), which prints no bound; the library holds it at fy = "
            f"{fy:g} ksi (steel carries no more than yield; the library's "
            "reading).")
    return out
