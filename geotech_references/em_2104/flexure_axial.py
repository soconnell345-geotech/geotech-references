"""EM 1110-2-2104 Chapter 4 + Appendix B -- Flexure and Axial Loads
(INVESTIGATION equations).

Given a section's reinforcement (As, As'), find its capacity (phi*Pn,
phi*Mn) at a given load eccentricity. Covers: eccentricity ratio (Eq 4-1/
4-2), the balanced-strain factor kb (Eq 4-3), the Bresler biaxial-bending
load-contour check (Eq 4-4/4-5), and the full Appendix B derivation chain
for singly reinforced (B-1 to B-21), doubly reinforced (B-22 to B-39),
tension-plus-flexure (B-40 to B-48), and pure-flexure (B-49 to B-53)
members. Printed pages per the 1 Nov 2023 edition (pdf_page = printed_page+5).

For the complementary DESIGN direction (given a required Mn/Pn, solve
directly for As/As'), see ``design.py`` (Appendix D-2).

Some of Appendix B's fully-expanded cubic equations (B-33 in particular)
were corrupted by PDF text extraction on the printed page (a scrambled
multi-line OCR block). Rather than transcribe a guess, this module uses the
IDENTICAL cubic reproduced cleanly in Appendix D-4 Step 3(a) -- the manual's
own worked example applies "equation B-33" and prints its fully-expanded
form there -- and verifies it against that example's numbers (ku = 0.357,
phi*Pn = 63 kips, phi*Mn = 2880 k-in; see tests/test_em_2104_flexure_axial.py).
Equation B-39 (doubly reinforced, compression-controlled cubic) and B-21
(singly reinforced, compression-controlled cubic) were legible on the
printed page and are transcribed directly.

ACI 318-19 VALUES USED BUT NOT REPRINTED IN THIS MANUAL: beta_1 ("will be
taken as specified in ACI 318-19", paragraph 4-1d(4)) and the strength
reduction factors phi ("the decision was to use the resistance factors in
ACI 318-19 without modification", Appendix F commentary). ``aci_beta1`` and
the ``PHI_*`` constants below are ACI 318-19 Table 21.2.2/22.2.2.4.3 values,
provided here only so this manual's own equations can be exercised; they are
not EM 1110-2-2104 content.
"""

import math

try:
    import numpy as _np
except ImportError:  # pragma: no cover - numpy is a repo-wide dependency
    _np = None

# ACI 318-19 strength reduction factors (Table 21.2.2), adopted without
# modification per Appendix F commentary (printed p. 118).
PHI_TENSION_CONTROLLED = 0.90
PHI_COMPRESSION_CONTROLLED_TIED = 0.65
PHI_COMPRESSION_CONTROLLED_SPIRAL = 0.75
PHI_SHEAR = 0.75

# Default steel modulus (ksi) and ultimate concrete strain, used throughout
# Appendix B/Chapter 4 (paragraph 4-1d(1): epsilon_c = 0.003).
DEFAULT_ES_KSI = 29000.0
DEFAULT_EC = 0.003


def aci_beta1(fc_prime, unit="ksi"):
    """ACI 318-19 Table 22.2.2.4.3 beta_1 factor (dimensionless, 0.65 to
    0.85) from f'c given in ksi (default) or psi; not reprinted in this
    manual (EM 1110-2-2104 paragraph 4-1d(4) states "Factor beta_1 will be
    taken as specified in ACI 318-19").

    Parameters
    ----------
    fc_prime : float
        Specified concrete compressive strength f'c, in ksi (unit='ksi',
        the default) or psi (unit='psi'). Not MPa: 28 (MPa) read as 28 ksi
        gives 0.65 where 28 MPa (4.06 ksi) gives 0.847.
    unit : str, optional
        'ksi' (default) or 'psi'.

    Returns
    -------
    float
        beta_1 (0.65 to 0.85).
    """
    fc_psi = fc_prime * 1000.0 if unit == "ksi" else fc_prime
    if fc_psi <= 4000.0:
        return 0.85
    if fc_psi <= 8000.0:
        return max(0.65, 0.85 - 0.05 * (fc_psi - 4000.0) / 1000.0)
    return 0.65


def _solve_cubic_ku(coeffs, kb=None, prefer="lt_kb", lo=1e-6, hi=5.0):
    """Solve a cubic in ku (coefficients [a3, a2, a1, a0], highest degree
    first) and select the physically valid real root.

    Parameters
    ----------
    coeffs : sequence of float
        [1, a2, a1, a0] for ku^3 + a2*ku^2 + a1*ku + a0 = 0.
    kb : float, optional
        Balanced ku, used to pick the tension- vs compression-controlled
        root when more than one candidate lies in (lo, hi).
    prefer : str, optional
        'lt_kb' (tension-controlled: pick the largest real root < kb,
        default), 'gt_kb' (compression-controlled: pick the smallest real
        root > kb), or 'smallest_positive' (kb not required).
    lo, hi : float, optional
        Bounds for a physically admissible root.

    Returns
    -------
    float
        The selected root.
    """
    if _np is None:  # pragma: no cover
        raise ImportError("numpy is required to solve the Appendix B cubics")
    roots = _np.roots(coeffs)
    real_roots = sorted(
        r.real for r in roots
        if abs(r.imag) < 1e-6 and lo < r.real < hi
    )
    if not real_roots:
        raise ValueError(f"No admissible real root in ({lo}, {hi}) for {coeffs}")
    if kb is None or prefer == "smallest_positive":
        return real_roots[0]
    if prefer == "lt_kb":
        candidates = [r for r in real_roots if r < kb]
        return max(candidates) if candidates else real_roots[0]
    if prefer == "gt_kb":
        candidates = [r for r in real_roots if r > kb]
        return min(candidates) if candidates else real_roots[-1]
    raise ValueError(f"Unknown prefer={prefer!r}")


# ============================================================================
# Chapter 4 -- eccentricity, balanced strain factor, biaxial bending
# ============================================================================

def eccentricity_ratio(mu, pu, d, h):
    """Eq 4-1/4-2: eccentricity of axial load e' (in., measured from the
    centroid of tension reinforcement) and its ratio e'/d (dimensionless)
    (printed pp. 29-30: Eq 4-1 on p. 29, Eq 4-2 on p. 30), from Mu in
    kip-in., Pu in kips and d, h in inches.

    Parameters
    ----------
    mu : float
        Resultant factored moment Mu, kip-in. (or nominal Mn: e'/d is the
        same either way since phi cancels). Mu/Pu must come out in the
        length unit of d and h.
    pu : float
        Resultant factored axial load Pu, kips; positive for compression,
        negative for tension (paragraph 4-1c(1)).
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.
    h : float
        Overall thickness of the section, in.

    Returns
    -------
    dict
        {'e_prime', 'e_prime_over_d', 'equation': '4-1/4-2',
         'printed_page': '29-30', 'pdf_page': '34-35'}
    """
    e_prime = mu / pu + (d - h / 2.0)
    return {
        "e_prime": e_prime, "e_prime_over_d": e_prime / d,
        "equation": "4-1/4-2", "printed_page": "29-30", "pdf_page": "34-35",
    }


def balanced_strain_kb(beta1, fy, es=DEFAULT_ES_KSI, ec=DEFAULT_EC):
    """Eq 4-3 (= Eq B-7): kb, the ratio of stress-block depth to effective
    depth at the balanced strain condition (dimensionless), from fy in ksi
    (printed p. 30).

        kb = beta1 * Es * ec / (Es * ec + fy)

    Parameters
    ----------
    beta1 : float
        ACI 318-19 beta_1 (``aci_beta1``), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of es;
        60 ksi for Grade 60, paragraph 3-5).
    es : float, optional
        Steel modulus of elasticity Es, ksi (default 29,000 ksi).
    ec : float, optional
        Maximum usable concrete strain, 0.003 (paragraph 4-1d(1)).

    Returns
    -------
    dict
        {'kb', 'equation': '4-3', 'printed_page': '30', 'pdf_page': 35}
    """
    kb = beta1 * es * ec / (es * ec + fy)
    return {"kb": kb, "equation": "4-3", "printed_page": "30", "pdf_page": 35}


def bresler_biaxial_check(mux, phi_m0x, muy, phi_m0y, member_shape="rectangular"):
    """Eq 4-5: Bresler load-contour biaxial-bending design check; returns
    the dimensionless left-hand side and whether it is <= 1.0 (printed
    p. 33). The moments may be in any one unit (kip-in. in the manual).

        [Mux / (phi*M0x)]^K + [Muy / (phi*M0y)]^K <= 1.0

    Parameters
    ----------
    mux : float
        Factored bending moment about the x axis, kip-in. (the unit of
        phi_m0x).
    phi_m0x : float
        Design uniaxial bending strength about x at the given Pn, phi*M0x
        (Muy = 0), kip-in., from the Appendix B singly- or doubly-
        reinforced capacity functions.
    muy : float
        Factored bending moment about the y axis, kip-in. (the unit of
        phi_m0y).
    phi_m0y : float
        Design uniaxial bending strength about y at the given Pn, phi*M0y
        (Mux = 0), kip-in.
    member_shape : str, optional
        'rectangular' (K = 1.5, default) or 'square_or_circular' (K = 1.75).

    Returns
    -------
    dict
        {'lhs', 'k', 'adequate' (bool), 'equation': '4-5',
         'printed_page': '33', 'pdf_page': 38}
    """
    k = 1.5 if member_shape == "rectangular" else 1.75
    if member_shape not in ("rectangular", "square_or_circular"):
        raise ValueError(
            f"member_shape must be 'rectangular' or 'square_or_circular', "
            f"got {member_shape!r}"
        )
    lhs = (mux / phi_m0x) ** k + (muy / phi_m0y) ** k
    return {
        "lhs": lhs, "k": k, "adequate": lhs <= 1.0, "equation": "4-5",
        "printed_page": "33", "pdf_page": 38,
    }


# ============================================================================
# Appendix B-2 -- Singly reinforced, flexure + axial compression (Fig B-1)
# ============================================================================

def max_axial_capacity_singly(phi, fc_prime, ag, as_, fy):
    """Eq B-1: maximum design axial load strength phi*Pn(max), kips, for
    tied, singly reinforced members, from strengths in ksi and areas in
    sq in. (printed p. 42).

        phi*Pn(max) = 0.8*phi*[0.85*fc'*(Ag - As) + fy*As]

    Parameters
    ----------
    phi : float
        Strength reduction factor (ACI 318-19; 0.65 compression-controlled
        tied, ``PHI_COMPRESSION_CONTROLLED_TIED``).
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    ag : float
        Gross area of the section, sq in.
    as_ : float
        Area of tension reinforcement As, sq in.
    fy : float
        Specified yield strength of reinforcement, ksi.

    Returns
    -------
    dict
        {'phi_pn_max', 'equation': 'B-1', 'printed_page': '42', 'pdf_page': 47}
    """
    phi_pn_max = 0.8 * phi * (0.85 * fc_prime * (ag - as_) + fy * as_)
    return {"phi_pn_max": phi_pn_max, "equation": "B-1",
            "printed_page": "42", "pdf_page": 47}


def balanced_eccentricity_singly(kb, rho, fy, fc_prime):
    """Eq B-10: balanced eccentricity ratio eb'/d (dimensionless) for a
    singly reinforced member (printed p. 43).

        eb'/d = (2*kb - kb^2) / (2*kb - rho*fy/(0.425*fc'))

    Compare a member's e'/d (Eq 4-1/4-2) to this: e'/d > eb'/d -> controlled
    by tension (``tension_controlled_capacity_singly``); e'/d <= eb'/d ->
    controlled by compression (``compression_controlled_capacity_singly``).

    Parameters
    ----------
    kb : float
        Balanced ku (``balanced_strain_kb``), dimensionless.
    rho : float
        Tension reinforcement ratio As/(b d), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of
        fc_prime).
    fc_prime : float
        Specified concrete compressive strength f'c, ksi (the unit of fy).

    Returns
    -------
    dict
        {'eb_prime_over_d', 'equation': 'B-10', 'printed_page': '43',
         'pdf_page': 48}
    """
    eb_over_d = (2 * kb - kb ** 2) / (2 * kb - rho * fy / (0.425 * fc_prime))
    return {"eb_prime_over_d": eb_over_d, "equation": "B-10",
            "printed_page": "43", "pdf_page": 48}


def tension_controlled_capacity_singly(e_prime_over_d, rho, fy, fc_prime, b, d, h, phi):
    """Eq B-16, B-11, B-13: design capacity phi*Pn (kips) and phi*Mn
    (kip-in.) of a singly reinforced, tension-controlled member
    (e'/d > eb'/d), from strengths in ksi and dimensions in inches (printed
    pp. 43-44).

        ku = sqrt[(e'/d - 1)^2 + rho*fy*(e'/d)/(0.425*fc')] - (e'/d - 1)
        phi*Pn = phi*(0.85*fc'*ku - rho*fy)*b*d
        phi*Mn = phi*Pn*[e'/d - (1 - h/(2d))]*d

    Note this uses a different closed form from Appendix D-2's Eq D-8 (the
    DESIGN-direction quadratic in ``design.design_singly_reinforced``) --
    B-15/B-16 here and Eq D-8 solve different quadratics (this one is driven
    by e'/d and rho; D-8 is driven directly by Mn/Pn) and are not
    interchangeable.

    Parameters
    ----------
    e_prime_over_d : float
        Eccentricity ratio e'/d (``eccentricity_ratio``), dimensionless.
    rho : float
        Tension reinforcement ratio As/(b d), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi.
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    b : float
        Design width of member, in.
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.
    h : float
        Overall thickness of the section, in.
    phi : float
        Strength reduction factor (ACI 318-19; 0.90 tension-controlled,
        ``PHI_TENSION_CONTROLLED``).

    Returns
    -------
    dict
        {'ku', 'phi_pn', 'phi_mn', 'equation': 'B-11/B-13/B-16', ...}
    """
    term = e_prime_over_d - 1
    radicand = term ** 2 + rho * fy * e_prime_over_d / (0.425 * fc_prime)
    ku = math.sqrt(radicand) - term
    phi_pn = phi * (0.85 * fc_prime * ku - rho * fy) * b * d
    phi_mn = phi_pn * (e_prime_over_d - (1 - h / (2 * d))) * d
    return {
        "ku": ku, "phi_pn": phi_pn, "phi_mn": phi_mn,
        "equation": "B-11/B-13/B-16", "printed_page": "43-44",
        "pdf_page": "48-49",
    }


def compression_controlled_capacity_singly(e_prime_over_d, rho, fy, fc_prime,
                                            b, d, h, phi, beta1,
                                            es=DEFAULT_ES_KSI, ec=DEFAULT_EC,
                                            kb=None):
    """Eq B-21, B-17, B-18, B-19: design capacity phi*Pn (kips) and phi*Mn
    (kip-in.) of a singly reinforced, compression-controlled member
    (e'/d <= eb'/d), from strengths in ksi and dimensions in inches (printed
    pp. 44-45).

    ku solves the cubic (Eq B-21):
        ku^3 + 2*(e'/d - 1)*ku^2
             + [Es*ec*rho*(e'/d) / (0.425*fc')] * ku
             - beta1*Es*ec*rho*(e'/d) / (0.425*fc') = 0
    solved numerically (no closed form is given in the manual); the tension
    reinforcement stress fs (Eq B-19, capped >= -fy) then follows from
    strain compatibility, and:
        phi*Pn = phi*(0.85*fc'*ku - rho*fs)*b*d          [Eq B-17]
        phi*Mn = phi*Pn*[e'/d - (1 - h/(2d))]*d           [Eq B-18]

    Parameters
    ----------
    e_prime_over_d : float
        Eccentricity ratio e'/d (``eccentricity_ratio``), dimensionless.
    rho : float
        Tension reinforcement ratio As/(b d), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of es).
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    b : float
        Design width of member, in.
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.
    h : float
        Overall thickness of the section, in.
    phi : float
        Strength reduction factor (ACI 318-19; 0.65 compression-controlled
        tied, ``PHI_COMPRESSION_CONTROLLED_TIED``).
    beta1 : float
        ACI 318-19 beta_1 (``aci_beta1``), dimensionless.
    es : float, optional
        Steel modulus of elasticity Es, ksi (default 29,000 ksi).
    ec : float, optional
        Maximum usable concrete strain, 0.003 (paragraph 4-1d(1)).
    kb : float, optional
        Balanced ku (``balanced_strain_kb``), dimensionless; picks the root
        of the cubic above kb.

    Returns
    -------
    dict
        {'ku', 'fs', 'phi_pn', 'phi_mn', 'equation': 'B-17/B-18/B-19/B-21', ...}
    """
    esec = es * ec
    coeffs = [
        1.0,
        2 * (e_prime_over_d - 1),
        esec * rho * e_prime_over_d / (0.425 * fc_prime),
        -beta1 * esec * rho * e_prime_over_d / (0.425 * fc_prime),
    ]
    ku = _solve_cubic_ku(coeffs, kb=kb, prefer="gt_kb")
    fs = max(-fy, es * ec * (beta1 - ku) / ku)
    phi_pn = phi * (0.85 * fc_prime * ku - rho * fs) * b * d
    phi_mn = phi_pn * (e_prime_over_d - (1 - h / (2 * d))) * d
    return {
        "ku": ku, "fs": fs, "phi_pn": phi_pn, "phi_mn": phi_mn,
        "equation": "B-17/B-18/B-19/B-21", "printed_page": "44-45",
        "pdf_page": "49-50",
    }


# ============================================================================
# Appendix B-3 -- Doubly reinforced, flexure + axial compression (Fig B-2)
# ============================================================================

def max_axial_capacity_doubly(phi, fc_prime, ag, rho, rho_prime, fy, bd):
    """Eq B-22: maximum design axial load strength phi*Pn(max), kips, for
    tied, doubly reinforced members, from strengths in ksi and areas in
    sq in. (printed p. 44).

        phi*Pn(max) = 0.8*phi*[0.85*fc'*(Ag-(rho+rho')*bd) + fy*(rho+rho')*bd]

    Parameters
    ----------
    phi : float
        Strength reduction factor (ACI 318-19; 0.65 compression-controlled
        tied, ``PHI_COMPRESSION_CONTROLLED_TIED``).
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    ag : float
        Gross area of the section, sq in.
    rho : float
        Tension reinforcement ratio As/(b d), dimensionless.
    rho_prime : float
        Compression reinforcement ratio As'/(b d), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi.
    bd : float
        Product of width b and effective depth d, sq in.

    Returns
    -------
    dict
        {'phi_pn_max', 'equation': 'B-22', 'printed_page': '44',
         'pdf_page': 49}
    """
    steel_area = (rho + rho_prime) * bd
    phi_pn_max = 0.8 * phi * (0.85 * fc_prime * (ag - steel_area) + fy * steel_area)
    return {"phi_pn_max": phi_pn_max, "equation": "B-22",
            "printed_page": "44", "pdf_page": 49}


def compression_steel_stress_at_ku(ku, dprime_over_d, beta1, fy,
                                    es=DEFAULT_ES_KSI, ec=DEFAULT_EC,
                                    regime="tension_controlled"):
    """Eq B-31 (tension-controlled regime) or B-37 (compression-controlled
    regime): compression-steel stress fs', ksi, at a given ku (printed
    pp. 46-47).

        fs' = [(ku - beta1*d'/d) / (beta1 - ku)] * Es*epsilon_y   (B-31, capped <= fy)
        fs' = Es*ec*[ku - beta1*(d'/d)] / ku                       (B-37, capped >= -fy)

    Parameters
    ----------
    ku : float
        Ratio of stress-block depth a to effective depth d, dimensionless.
    dprime_over_d : float
        d'/d, compression-steel depth over effective depth, dimensionless.
    beta1 : float
        ACI 318-19 beta_1 (``aci_beta1``), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of es).
    es : float, optional
        Steel modulus of elasticity Es, ksi (default 29,000 ksi).
    ec : float, optional
        Maximum usable concrete strain, 0.003 (paragraph 4-1d(1)).
    regime : str, optional
        'tension_controlled' (Eq B-31, uses Es*epsilon_y; default) or
        'compression_controlled' (Eq B-37, uses Es*ec).
    """
    if regime == "tension_controlled":
        ey = fy / es
        fs_prime = (ku - beta1 * dprime_over_d) / (beta1 - ku) * es * ey
        fs_prime = min(fs_prime, fy)
        eq = "B-31"
    elif regime == "compression_controlled":
        fs_prime = es * ec * (ku - beta1 * dprime_over_d) / ku
        fs_prime = max(fs_prime, -fy)
        eq = "B-37"
    else:
        raise ValueError(
            f"regime must be 'tension_controlled' or 'compression_controlled', "
            f"got {regime!r}"
        )
    return {"fs_prime": fs_prime, "equation": eq,
            "printed_page": "46-47", "pdf_page": "51-52"}


def balanced_eccentricity_doubly(kb, beta1, dprime_over_d, rho, rho_prime, fy,
                                  fc_prime, es=DEFAULT_ES_KSI, ec=DEFAULT_EC):
    """Eq B-28: balanced eccentricity ratio eb'/d (dimensionless) for a
    doubly reinforced member, with fs' at kb in ksi (printed p. 45).

        eb'/d = [2kb - kb^2 + fs'*rho'*(1 - d'/d)/(0.425*fc')]
                / [2kb - fy*rho/(0.425*fc') + fs'*rho'/(0.425*fc')]

    where fs' is the compression-steel stress at ku = kb (Eq B-31).

    Parameters
    ----------
    kb : float
        Balanced ku (``balanced_strain_kb``).
    beta1 : float
        ACI 318-19 beta_1 (``aci_beta1``).
    dprime_over_d : float
        d'/d, compression-steel depth over effective depth, dimensionless.
    rho : float
        Tension reinforcement ratio As/(b d), dimensionless.
    rho_prime : float
        Compression reinforcement ratio As'/(b d), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of es).
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    es : float, optional
        Steel modulus of elasticity Es, ksi (default 29,000 ksi).
    ec : float, optional
        Maximum usable concrete strain, 0.003 (paragraph 4-1d(1)).

    Returns
    -------
    dict
        {'eb_prime_over_d', 'fs_prime_at_kb', 'equation': 'B-28', ...}
    """
    fs_prime = compression_steel_stress_at_ku(
        kb, dprime_over_d, beta1, fy, es, ec, regime="tension_controlled",
    )["fs_prime"]
    numerator = (2 * kb - kb ** 2
                 + fs_prime * rho_prime * (1 - dprime_over_d) / (0.425 * fc_prime))
    denominator = (2 * kb - fy * rho / (0.425 * fc_prime)
                   + fs_prime * rho_prime / (0.425 * fc_prime))
    eb_over_d = numerator / denominator
    return {
        "eb_prime_over_d": eb_over_d, "fs_prime_at_kb": fs_prime,
        "equation": "B-28", "printed_page": "45", "pdf_page": 50,
    }


def tension_controlled_capacity_doubly(e_prime_over_d, dprime_over_d, rho,
                                        rho_prime, fy, fc_prime, beta1,
                                        b, d, h, phi, es=DEFAULT_ES_KSI,
                                        ec=DEFAULT_EC, kb=None):
    """Eq B-33, B-29, B-30: design capacity phi*Pn (kips) and phi*Mn
    (kip-in.) of a doubly reinforced, tension-controlled member
    (e'/d > eb'/d), from strengths in ksi and dimensions in inches (printed
    pp. 46-47).

    The printed page's fully-expanded form of Eq B-33 was corrupted by PDF
    text extraction; this is the identical cubic as re-derived and printed
    cleanly in Appendix D-4 Step 3(a) (verified against that worked example,
    ku = 0.357 -- see the module tests):

        ku^3 + [2*(e'/d - 1) - beta1]*ku^2
             - {(fy/(0.425fc')) * [rho'*(e'/d + d'/d - 1) + rho*(e'/d)]
                + 2*beta1*(e'/d - 1)} * ku
             + (fy*beta1/(0.425fc')) * [rho'*(d'/d)*(e'/d + d'/d - 1)
                                          + rho*(e'/d)] = 0

    Then (Eq B-31, B-29, B-30):
        fs' = compression_steel_stress_at_ku(ku, ..., 'tension_controlled')
        phi*Pn = phi*(0.85*fc'*ku + rho'*fs' - rho*fy)*b*d
        phi*Mn = phi*Pn*[e'/d - (1 - h/(2d))]*d

    Parameters
    ----------
    e_prime_over_d : float
        Eccentricity ratio e'/d (``eccentricity_ratio``), dimensionless.
    dprime_over_d : float
        d'/d, compression-steel depth over effective depth, dimensionless.
    rho : float
        Tension reinforcement ratio As/(b d), dimensionless.
    rho_prime : float
        Compression reinforcement ratio As'/(b d), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of es).
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    beta1 : float
        ACI 318-19 beta_1 (``aci_beta1``), dimensionless.
    b : float
        Design width of member, in.
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.
    h : float
        Overall thickness of the section, in.
    phi : float
        Strength reduction factor (ACI 318-19; 0.90 tension-controlled,
        ``PHI_TENSION_CONTROLLED``).
    es : float, optional
        Steel modulus of elasticity Es, ksi (default 29,000 ksi).
    ec : float, optional
        Maximum usable concrete strain, 0.003 (paragraph 4-1d(1)).
    kb : float, optional
        Balanced ku (``balanced_strain_kb``), dimensionless; picks the root
        of the cubic below kb.

    Returns
    -------
    dict
        {'ku', 'fs_prime', 'phi_pn', 'phi_mn', 'equation': 'B-29/B-30/B-33', ...}
    """
    e = e_prime_over_d
    dpr = dprime_over_d
    k = fy / (0.425 * fc_prime)
    a2 = 2 * (e - 1) - beta1
    a1 = -(k * (rho_prime * (e + dpr - 1) + rho * e) + 2 * beta1 * (e - 1))
    a0 = k * beta1 * (rho_prime * dpr * (e + dpr - 1) + rho * e)
    coeffs = [1.0, a2, a1, a0]
    ku = _solve_cubic_ku(coeffs, kb=kb, prefer="lt_kb")
    fs_prime = compression_steel_stress_at_ku(
        ku, dprime_over_d, beta1, fy, es, ec, regime="tension_controlled",
    )["fs_prime"]
    phi_pn = phi * (0.85 * fc_prime * ku + rho_prime * fs_prime - rho * fy) * b * d
    phi_mn = phi_pn * (e_prime_over_d - (1 - h / (2 * d))) * d
    return {
        "ku": ku, "fs_prime": fs_prime, "phi_pn": phi_pn, "phi_mn": phi_mn,
        "equation": "B-29/B-30/B-33", "printed_page": "46-47",
        "pdf_page": "51-52",
    }


def compression_controlled_capacity_doubly(e_prime_over_d, dprime_over_d, rho,
                                            rho_prime, fy, fc_prime, beta1,
                                            b, d, h, phi, es=DEFAULT_ES_KSI,
                                            ec=DEFAULT_EC, kb=None):
    """Eq B-39, B-34, B-35, B-36, B-37: design capacity phi*Pn (kips) and
    phi*Mn (kip-in.) of a doubly reinforced, compression-controlled member
    (e'/d <= eb'/d), from strengths in ksi and dimensions in inches (printed
    pp. 47-48).

        ku^3 + 2*(e'/d - 1)*ku^2
             + [Es*ec/(0.425fc')] * [(rho+rho')*(e'/d) - rho'*(1 - d'/d)] * ku
             - [beta1*Es*ec/(0.425fc')] * [rho'*(d'/d)*(e'/d + d'/d - 1)
                                             + rho*(e'/d)] = 0

    Then (Eq B-36, B-37, B-34, B-35):
        fs  = Es*ec*(beta1 - ku)/ku              [tension steel, non-yielding]
        fs' = Es*ec*[ku - beta1*(d'/d)]/ku        [compression steel]
        phi*Pn = phi*(0.85*fc'*ku + rho'*fs' - rho*fs)*b*d
        phi*Mn = phi*Pn*[e'/d - (1 - h/(2d))]*d

    Parameters
    ----------
    e_prime_over_d : float
        Eccentricity ratio e'/d (``eccentricity_ratio``), dimensionless.
    dprime_over_d : float
        d'/d, compression-steel depth over effective depth, dimensionless.
    rho : float
        Tension reinforcement ratio As/(b d), dimensionless.
    rho_prime : float
        Compression reinforcement ratio As'/(b d), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of es).
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    beta1 : float
        ACI 318-19 beta_1 (``aci_beta1``), dimensionless.
    b : float
        Design width of member, in.
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.
    h : float
        Overall thickness of the section, in.
    phi : float
        Strength reduction factor (ACI 318-19; 0.65 compression-controlled
        tied, ``PHI_COMPRESSION_CONTROLLED_TIED``).
    es : float, optional
        Steel modulus of elasticity Es, ksi (default 29,000 ksi).
    ec : float, optional
        Maximum usable concrete strain, 0.003 (paragraph 4-1d(1)).
    kb : float, optional
        Balanced ku (``balanced_strain_kb``), dimensionless; picks the root
        of the cubic above kb.

    Returns
    -------
    dict
        {'ku', 'fs', 'fs_prime', 'phi_pn', 'phi_mn',
         'equation': 'B-34/B-35/B-36/B-37/B-39', ...}
    """
    e = e_prime_over_d
    dpr = dprime_over_d
    esec = es * ec
    coeff_k = esec / (0.425 * fc_prime)
    a2 = 2 * (e - 1)
    a1 = coeff_k * ((rho + rho_prime) * e - rho_prime * (1 - dpr))
    a0 = -beta1 * coeff_k * (rho_prime * dpr * (e + dpr - 1) + rho * e)
    coeffs = [1.0, a2, a1, a0]
    ku = _solve_cubic_ku(coeffs, kb=kb, prefer="gt_kb")
    fs = max(-fy, min(fy, esec * (beta1 - ku) / ku))
    fs_prime = compression_steel_stress_at_ku(
        ku, dprime_over_d, beta1, fy, es, ec, regime="compression_controlled",
    )["fs_prime"]
    phi_pn = phi * (0.85 * fc_prime * ku + rho_prime * fs_prime - rho * fs) * b * d
    phi_mn = phi_pn * (e_prime_over_d - (1 - h / (2 * d))) * d
    return {
        "ku": ku, "fs": fs, "fs_prime": fs_prime, "phi_pn": phi_pn,
        "phi_mn": phi_mn, "equation": "B-34/B-35/B-36/B-37/B-39",
        "printed_page": "47-48", "pdf_page": "52-53",
    }


# ============================================================================
# Appendix B-4 -- Flexural and tensile capacity (Fig B-3)
# ============================================================================

def max_axial_tension_capacity(phi, rho, rho_prime, fy, bd):
    """Eq B-40 (= Eq B-43, converted to a design limit): maximum design
    axial tension strength phi*Pn(max), kips, 80 percent of the strength at
    zero eccentricity, from fy in ksi and b*d in sq in. (printed p. 48).

        phi*Pn(max) = 0.8*phi*(rho + rho')*fy*b*d

    Parameters
    ----------
    phi : float
        Strength reduction factor (ACI 318-19; 0.90 tension-controlled,
        ``PHI_TENSION_CONTROLLED``).
    rho : float
        Tension reinforcement ratio As/(b d), dimensionless.
    rho_prime : float
        Compression reinforcement ratio As'/(b d), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi.
    bd : float
        Product of width b and effective depth d, sq in.

    Returns
    -------
    dict
        {'phi_pn_max', 'equation': 'B-40', 'printed_page': '48',
         'pdf_page': 53}
    """
    phi_pn_max = 0.8 * phi * (rho + rho_prime) * fy * bd
    return {"phi_pn_max": phi_pn_max, "equation": "B-40",
            "printed_page": "48", "pdf_page": 53}


def tension_flexure_eccentricity_range(h, d):
    """Eq B-41: the eccentricity-ratio range (dimensionless bounds on e'/d)
    within which BOTH reinforcement layers are in tension (the tensile
    resultant lies between them), from h and d in one length unit (printed
    p. 48).

        0 <= e'/d <= (1 - h/(2d))

    Outside this range (e'/d < 0), the section behaves like a compression
    member controlled by tension (paragraph B-4g/h: use
    ``compression_controlled_capacity_singly``/``tension_controlled_capacity_doubly``
    as appropriate); above the upper bound, the assumed tension face is
    actually in compression and the eccentricity should be recomputed from
    the opposite face.

    Parameters
    ----------
    h : float
        Overall thickness of the section, in. (the unit of d).
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.

    Returns
    -------
    dict
        {'lower_bound', 'upper_bound', 'equation': 'B-41',
         'printed_page': '48', 'pdf_page': 53}
    """
    upper = 1 - h / (2 * d)
    return {"lower_bound": 0.0, "upper_bound": upper, "equation": "B-41",
            "printed_page": "48", "pdf_page": 53}


def tension_controlled_by_compression_side_ku(e_prime_over_d, rho, fy, fc_prime):
    """Eq B-42: ku (dimensionless) for a tensile load with e'/d < 0, no
    compression reinforcement (or c <= d'), designed per paragraph B-2e
    (printed p. 49).

        ku = -(e'/d - 1) - sqrt[(e'/d - 1)^2 + (rho*fy/(0.425fc'))*(e'/d)]

    Parameters
    ----------
    e_prime_over_d : float
        Eccentricity ratio e'/d (negative here), dimensionless.
    rho : float
        Tension reinforcement ratio As/(b d), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of
        fc_prime).
    fc_prime : float
        Specified concrete compressive strength f'c, ksi (the unit of fy).

    Returns
    -------
    dict
        {'ku', 'equation': 'B-42', 'printed_page': '49', 'pdf_page': 54}
    """
    term = e_prime_over_d - 1
    radicand = term ** 2 + (rho * fy / (0.425 * fc_prime)) * e_prime_over_d
    ku = -term - math.sqrt(radicand)
    return {"ku": ku, "equation": "B-42", "printed_page": "49", "pdf_page": 54}


def tension_between_layers_capacity(e_prime_over_d, dprime_over_d, rho,
                                     rho_prime, fy):
    """Eq B-48, B-46, B-44, B-45: ku (dimensionless) and the second-layer
    steel stress fs' (ksi, the unit of fy) for a tensile load between the
    two reinforcement layers, 0 <= e'/d <= (1 - h/(2d)) (printed pp. 49-50);
    phi*Pn and phi*Mn follow from them (see 'note').

        ku = [rho'*(d'/d)*(1 - d'/d - e'/d) - rho*(e'/d)]
             / [rho*(e'/d) - rho'*(1 - d'/d - e'/d)]
        fs' = fy*(ku + d'/d) / (ku + 1)
        phi*Pn = phi*(rho*fy + rho'*fs')*b*d
        phi*Mn = phi*Pn*[(1 - h/(2d)) - e'/d]*d

    Parameters
    ----------
    e_prime_over_d : float
        Eccentricity ratio e'/d, dimensionless.
    dprime_over_d : float
        d'/d, second-layer steel depth over effective depth, dimensionless.
    rho : float
        Tension reinforcement ratio As/(b d), dimensionless.
    rho_prime : float
        Second-layer reinforcement ratio As'/(b d), dimensionless.
    fy : float
        Specified yield strength of reinforcement, ksi.

    Returns
    -------
    dict
        {'ku', 'fs_prime', 'equation': 'B-44/B-45/B-46/B-48',
         'printed_page': '49-50', 'pdf_page': '54-55', 'note'}
    """
    e = e_prime_over_d
    dpr = dprime_over_d
    term = 1 - dpr - e
    ku = (rho_prime * dpr * term - rho * e) / (rho * e - rho_prime * term)
    fs_prime = fy * (ku + dpr) / (ku + 1)
    return {
        "ku": ku, "fs_prime": fs_prime,
        "equation": "B-44/B-45/B-46/B-48", "printed_page": "49-50",
        "pdf_page": "54-55",
        "note": ("phi*Pn = phi*(rho*fy + rho'*fs')*b*d and "
                 "phi*Mn = phi*Pn*[(1-h/(2d)) - e'/d]*d -- multiply by the "
                 "section's b*d directly; ku and fs' above are dimensionless/"
                 "stress results independent of b."),
    }


def pure_tension_capacity(phi, as_, as_prime, fy):
    """Eq B-43: design axial tension strength phi*Pn, kips, at zero
    eccentricity (printed p. 49), before the Eq B-40 0.8 design cap is
    applied, from areas in sq in. and fy in ksi.

        phi*Pn = phi*(As + As')*fy

    Parameters
    ----------
    phi : float
        Strength reduction factor (ACI 318-19; 0.90 tension-controlled,
        ``PHI_TENSION_CONTROLLED``; 1.0 gives the nominal Pn).
    as_ : float
        Area of tension reinforcement As, sq in.
    as_prime : float
        Area of the second (compression-face) reinforcement As', sq in.
    fy : float
        Specified yield strength of reinforcement, ksi.

    Returns
    -------
    dict
        {'phi_pn', 'equation': 'B-43', 'printed_page': '49', 'pdf_page': 54}
    """
    phi_pn = phi * (as_ + as_prime) * fy
    return {"phi_pn": phi_pn, "equation": "B-43", "printed_page": "49",
            "pdf_page": 54}


# ============================================================================
# Appendix B-5, B-6 -- Pure flexure
# ============================================================================

def pure_flexure_singly(as_, fy, fc_prime, b, d, phi=None):
    """Eq B-49, B-50: nominal flexural capacity Mn, kip-in. (and phi*Mn
    when phi is given), with the stress-block depth a, in., for tension
    reinforcement only, from As in sq in., strengths in ksi and b, d in
    inches (printed p. 51).

        a = As*fy / (0.85*fc'*b)
        Mn = As*fy*(d - a/2)                    [phi*Mn if phi is given]

    Verified against Appendix C-2 (As=1.58 sq in, fc'=4 ksi, fy=60 ksi,
    b=12 in, d=20.5 in, phi=0.9): phi*Mn = 137.5 k-ft.

    Parameters
    ----------
    as_ : float
        Area of tension reinforcement As, sq in.
    fy : float
        Specified yield strength of reinforcement, ksi.
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    b : float
        Design width of member, in.
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.
    phi : float, optional
        Strength reduction factor (ACI 318-19; 0.90 tension-controlled);
        if given, 'phi_mn' is returned too.

    Returns
    -------
    dict
        {'a', 'mn', 'phi_mn' (if phi given), 'equation': 'B-49/B-50',
         'printed_page': '51', 'pdf_page': 56}
    """
    a = as_ * fy / (0.85 * fc_prime * b)
    mn = as_ * fy * (d - a / 2.0)
    out = {"a": a, "mn": mn, "equation": "B-49/B-50",
           "printed_page": "51", "pdf_page": 56}
    if phi is not None:
        out["phi_mn"] = phi * mn
    return out


def pure_flexure_doubly(as_, as_prime, fc_prime, fy, b, d, dprime, beta1=None,
                         es=DEFAULT_ES_KSI, ec=DEFAULT_EC, phi=None):
    """Eq B-51, B-52, B-53: nominal flexural capacity Mn, kip-in. (and
    phi*Mn when phi is given), with a and c in inches and fs' in ksi, for
    tension and compression reinforcement, from areas in sq in., strengths
    in ksi and dimensions in inches (printed p. 51).

    First assumes the compression steel yields (fs' = fy) and solves
    equilibrium (T = Cc + Cs) directly for the stress-block depth a; checks
    the resulting compression-steel strain against yield strain, and if it
    is not actually at yield, re-solves the equilibrium quadratic in a with
    fs' from strain compatibility (Eq B-53's Cs with fs' = Es*ec*(c-d')/c)
    -- reproducing the two-case procedure demonstrated in Appendix C-3.

        Cc = 0.85*fc'*b*a                         [Eq B-52]
        Cs = As'*(fs' - 0.85*fc')                 [Eq B-53]
        Mn = Cc*(d - a/2) + Cs*(d - d')            [Eq B-51]

    Verified against Appendix C-3 / Table C-1 (As=8 sq in, As'=4 sq in,
    fc'=4 ksi, fy=60 ksi, b=12 in, d=60 in, d'=6 in): a = 8.62 in,
    c = 10.14 in, Mn = 26,515.2 in-k (compression steel found to yield in
    this case, es' = 0.0148 > ey).

    Parameters
    ----------
    as_ : float
        Area of tension reinforcement As, sq in.
    as_prime : float
        Area of compression reinforcement As', sq in.
    fc_prime : float
        Specified concrete compressive strength f'c, ksi.
    fy : float
        Specified yield strength of reinforcement, ksi (the unit of es).
    b : float
        Design width of member, in.
    d : float
        Effective depth, extreme compression fiber to the centroid of the
        tension reinforcement, in.
    dprime : float
        Depth d' from the extreme compression fiber to the centroid of the
        compression reinforcement, in.
    beta1 : float, optional
        ACI 318-19 beta_1; from ``aci_beta1(fc_prime)`` (ksi) if omitted.
    es : float, optional
        Steel modulus of elasticity Es, ksi (default 29,000 ksi).
    ec : float, optional
        Maximum usable concrete strain, 0.003 (paragraph 4-1d(1)).
    phi : float, optional
        Strength reduction factor (ACI 318-19; 0.90 tension-controlled);
        if given, 'phi_mn' is returned too.

    Returns
    -------
    dict
        {'a', 'c', 'fs_prime', 'compression_steel_yields' (bool), 'mn',
         'phi_mn' (if phi given), 'equation': 'B-51/B-52/B-53', ...}
    """
    if beta1 is None:
        beta1 = aci_beta1(fc_prime)
    ey = fy / es
    esec = es * ec

    # Case 1: assume compression steel yields.
    a = ((as_ - as_prime) * fy + as_prime * 0.85 * fc_prime) / (0.85 * fc_prime * b)
    c = a / beta1
    es_prime = ec * (c - dprime) / c if c > 0 else 0.0
    yields = es_prime >= ey

    if not yields:
        # Case 2: general equilibrium, compression steel below yield
        # (quadratic in a; reproduces Appendix C-3's a^2 - 3.57a - 43.5 = 0).
        aa = 0.85 * fc_prime * b
        bb = as_prime * (esec - 0.85 * fc_prime) - as_ * fy
        cc = -as_prime * esec * dprime * beta1
        disc = bb ** 2 - 4 * aa * cc
        a = (-bb + math.sqrt(disc)) / (2 * aa)
        c = a / beta1
        es_prime = ec * (c - dprime) / c
        fs_prime = es * es_prime
    else:
        fs_prime = fy

    conc_c = 0.85 * fc_prime * b * a
    steel_c = as_prime * (fs_prime - 0.85 * fc_prime)
    mn = conc_c * (d - a / 2.0) + steel_c * (d - dprime)

    out = {
        "a": a, "c": c, "fs_prime": fs_prime,
        "compression_steel_yields": yields, "mn": mn,
        "equation": "B-51/B-52/B-53", "printed_page": "51", "pdf_page": 56,
    }
    if phi is not None:
        out["phi_mn"] = phi * mn
    return out
