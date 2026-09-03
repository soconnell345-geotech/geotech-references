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
    """Table D-1's general Kd formula (printed p. 73), the ku value at a
    target reinforcement ratio (as a fraction of the balanced ratio, e.g.
    0.25 or 0.50 per paragraph 3-6/3-4b(2)).

        Kd = (rho/rho_b) * beta1 * Es*ec / (Es*ec + fy)

    Note this is identical in form to Eq 4-3/B-7's kb with rho/rho_b
    scaling it down from the balanced value.
    """
    kd = rho_over_rho_b * beta1 * es * ec / (es * ec + fy)
    return {"kd": kd, "rho_over_rho_b": rho_over_rho_b, "table": "D-1",
            "printed_page": "73", "pdf_page": 78}


def minimum_effective_depth(mn, b, fc_prime, kd):
    """Table D-1 / Eq D-5: minimum effective depth dd at a target
    reinforcement ratio (printed p. 73).

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
        {'dd', 'equation': 'D-5', 'printed_page': '73', 'pdf_page': 78}
    """
    dd = math.sqrt(mn / (0.85 * fc_prime * kd * b * (1 - kd / 2.0)))
    return {"dd": dd, "equation": "D-5", "printed_page": "73", "pdf_page": 78}


def max_moment_at_rho_limit(fc_prime, kd, b, d, h, pn=0.0):
    """Eq D-6, D-7: MDL, the maximum bending moment a member may carry and
    remain within the target reinforcement-ratio limit (printed p. 72).

        ad = Kd * d                                          [Eq D-7]
        MDL = 0.85*fc'*ad*b*(d - ad/2) - (d - h/2)*Pn         [Eq D-6]

    If the required Mn <= MDL, the trial section is adequate
    (``design_singly_reinforced`` may be used directly); otherwise the
    section must be enlarged or doubly reinforced
    (``design_doubly_reinforced``).
    """
    ad = kd * d
    mdl = 0.85 * fc_prime * ad * b * (d - ad / 2.0) - (d - h / 2.0) * pn
    return {"ad": ad, "mdl": mdl, "equation": "D-6/D-7",
            "printed_page": "72", "pdf_page": 77}


def design_singly_reinforced(mn, pn, d, h, b, fc_prime, fy):
    """Eq D-8, D-9: direct design of a singly reinforced member for a
    required nominal moment Mn and axial load Pn (printed p. 72).

        Ku = 1 - sqrt(1 - [Mn + Pn*(d - h/2)] / (0.425*fc'*b*d^2))
        As = (0.85*fc'*Ku*b*d - Pn) / fy

    Pn positive = compression, negative = tension (or 0 for pure flexure).

    Verified against Appendix D-3 (Mn = 147 k-in, d = 6 in, h ~ 9 in
    (unused, Pn = 0), b = 12 in, fc' = 4 ksi, fy = 60 ksi): Ku = 0.105,
    As = 0.43 sq in. Also Appendix D-5 Step 3 (Mn = 476 k-ft/ft, Pn = 0,
    d = 36.5 in, fc' = 5 ksi): As = 2.73 sq in/ft.

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
    """Eq D-3, D-4, D-6, D-7: direct design of a doubly reinforced member
    when the required Mn exceeds MDL (the singly reinforced limit at the
    target reinforcement ratio) (printed pp. 70-72).

    Procedure:
      1. Kd, MDL at the target rho/rho_b (``kd_table_d1``,
         ``max_moment_at_rho_limit``).
      2. Compression-steel stress fs' at ad = Kd*d, from strain
         compatibility (paragraph D-2b): fs' = (ad - beta1*d')*ec*Es/ad
         (capped at fy).
      3. As' = (Mn - MDL) / [fs'*(d - d')]                       [Eq D-4]
      4. As = (0.85*fc'*Kd*b*d - Pn + As'*fs') / fy                [Eq D-3]

    Parameters
    ----------
    mn, pn : float
        Required nominal moment and axial load (Pn positive = compression).
    d, dprime, h, b : float
        Effective depth, compression-steel depth, overall thickness,
        section width.
    fc_prime, fy : float
        Material strengths.
    rho_over_rho_b : float, optional
        Target reinforcement ratio as a fraction of balanced (0.25 default,
        per the traditional deflection-control limit; 0.50 is the mandatory
        ceiling, paragraph 3-6).
    beta1 : float, optional
        ACI 318-19 beta_1; computed from fc_prime if omitted.

    Returns
    -------
    dict
        {'kd', 'mdl', 'fs_prime', 'as_prime_required', 'as_required',
         'equation': 'D-3/D-4/D-6/D-7', ...}
    """
    from .flexure_axial import aci_beta1
    if beta1 is None:
        beta1 = aci_beta1(fc_prime)
    kd_result = kd_table_d1(rho_over_rho_b, beta1, fy, es, ec)
    kd = kd_result["kd"]
    mdl_result = max_moment_at_rho_limit(fc_prime, kd, b, d, h, pn)
    mdl, ad = mdl_result["mdl"], mdl_result["ad"]

    if mn <= mdl:
        raise ValueError(
            "Required Mn does not exceed MDL -- a singly reinforced section "
            "is adequate; use design_singly_reinforced instead."
        )

    fs_prime = min(fy, (ad - beta1 * dprime) * ec * es / ad)
    as_prime = (mn - mdl) / (fs_prime * (d - dprime))
    as_required = (0.85 * fc_prime * kd * b * d - pn + as_prime * fs_prime) / fy

    return {
        "kd": kd, "ad": ad, "mdl": mdl, "fs_prime": fs_prime,
        "as_prime_required": as_prime, "as_required": as_required,
        "equation": "D-3/D-4/D-6/D-7", "printed_page": "70-72",
        "pdf_page": "75-77",
    }
