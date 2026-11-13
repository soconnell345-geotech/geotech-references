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

Equation B-33 (doubly reinforced, tension-controlled cubic) is typeset
cleanly on the rendered page (printed p. 47, pdf 53); only the PDF's text
layer scrambles it. The code's cubic is identical, term for term, to the
rendered B-33 and to the form the manual's worked example prints in
Appendix D-4 Step 3(a), and it is verified against that example's numbers
(ku = 0.357, phi*Pn = 63 kips, phi*Mn = 2880 k-in; see
tests/test_em_2104_flexure_axial.py).
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


def _yield_bounded(value, fy, name, printed):
    """Hold a steel stress within -fy..fy (ruling 42 on REF-76).

    ``printed`` names the bound the page prints beside the equation; the
    other side is the library's reading (steel carries no more than yield).
    Returns (bounded value, note or None)."""
    if -fy <= value <= fy:
        return value, None
    bound = fy if value > fy else -fy
    return bound, (
        f"{name} = {value:.4g} ksi from the equation; {printed}. The library "
        f"applies both bounds, -fy and fy, so {name} = {bound:g} ksi is used "
        "(steel carries no more than yield; the library's reading where the "
        "page prints only one side).")


# A stress within this fraction of fy counts as at yield, not past it (the
# cubic's root at the balanced point lands on kb only to rounding).
_YIELD_TOL = 1e-9

# The largest ku the cubic solver admits (``_solve_cubic_ku``'s ``hi``); the
# upper end of the equilibrium brackets below.
_KU_MAX = 5.0


def _equilibrium_residual(ku, e, dpr, rho, rho_prime, fc_prime, fs, fs_prime):
    """Eq B-23 (sum of forces) times e'/d, less Eq B-24 (moments about the
    tension steel), each divided by b d^2, ksi (printed p. 45): zero at the
    ku where a section whose steel stresses are fs and fs' balances a load
    at e'. With rho' = 0 these are Eqs B-2 and B-5 (printed p. 42)."""
    axial = 0.85 * fc_prime * ku + rho_prime * fs_prime - rho * fs
    moment = (0.425 * fc_prime * (2 * ku - ku ** 2)
              + rho_prime * fs_prime * (1 - dpr))
    return axial * e - moment


def _bisect_ku(g, lo, hi):
    """Root of g(ku) between lo and hi by bisection; the caller has checked
    that g(lo) and g(hi) are of opposite sign."""
    g_lo = g(lo)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            break
        g_mid = g(mid)
        if g_mid == 0.0:
            return mid
        if (g_mid < 0.0) == (g_lo < 0.0):
            lo, g_lo = mid, g_mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


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
    p. 44).

    ku solves the cubic (Eq B-21):
        ku^3 + 2*(e'/d - 1)*ku^2
             + [Es*ec*rho*(e'/d) / (0.425*fc')] * ku
             - beta1*Es*ec*rho*(e'/d) / (0.425*fc') = 0
    solved numerically (no closed form is given in the manual); the tension
    reinforcement stress fs = Es*ec*(beta1 - ku)/ku (Eq B-19, printed with
    fs >= -fy) then follows from strain compatibility, and:
        phi*Pn = phi*(0.85*fc'*ku - rho*fs)*b*d          [Eq B-17]
        phi*Mn = phi*Pn*[e'/d - (1 - h/(2d))]*d           [Eq B-18]

    Eq B-21 comes from putting Eq B-19, with no bound, into the equilibrium
    equations B-2 and B-5 (printed p. 42), so its ku balances the section
    only while B-19's fs lies within -fy..fy. Past yield (the library's
    reading, ruling 42 on REF-76; holding fs at yield with B-21's ku left
    phi*Pn out of equilibrium):

    - fs above fy: the tension steel has yielded, the section is controlled
      by tension and paragraph B-2e does not cover it. Refused; use
      ``tension_controlled_capacity_singly`` (paragraph B-2d).
    - fs below -fy (the bound the page prints): fs = -fy, and ku is solved
      again from Eqs B-2 and B-5 with fs = -fy, by bisection between the ku
      at which B-19 reaches -fy and 5 (the cubic solver's limit), where the
      residual rises steadily so the root is the only one. The result gives
      ``limit_governs`` True, B-21's root as ``ku_cubic``, B-19 there as
      ``fs_unlimited``, B-21's ku with fs = -fy as ``phi_pn_cubic``, and a
      note.

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
        {'ku', 'fs', 'phi_pn', 'phi_mn', 'limit_governs',
         'equation': 'B-17/B-18/B-19/B-21', ...}; where fs is held at -fy
        also 'ku_cubic', 'fs_unlimited', 'phi_pn_cubic' and 'note', and
        'equation' names B-2 and B-5 in place of B-21.

    Raises
    ------
    ValueError
        If fy, es or ec is not positive (they set the bound on fs); if Eq
        B-19's fs is above fy at Eq B-21's root (the section is controlled
        by tension); or if Eqs B-2 and B-5 with fs = -fy have no root in
        the bracket.
    """
    for name, val in (("fy", fy), ("es", es), ("ec", ec)):
        if val is None or val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    esec = es * ec
    coeffs = [
        1.0,
        2 * (e_prime_over_d - 1),
        esec * rho * e_prime_over_d / (0.425 * fc_prime),
        -beta1 * esec * rho * e_prime_over_d / (0.425 * fc_prime),
    ]
    ku = _solve_cubic_ku(coeffs, kb=kb, prefer="gt_kb")
    fs_raw = es * ec * (beta1 - ku) / ku
    if fs_raw > fy * (1 + _YIELD_TOL):
        raise ValueError(
            f"Eq B-19 gives fs = {fs_raw:.4g} ksi at the root of Eq B-21 "
            f"(ku = {ku:.4g}), above fy = {fy:g} ksi: the tension steel has "
            "yielded, so the section is controlled by tension and "
            "paragraph B-2e's Eqs B-17 to B-21, which take the steel below "
            "yield, do not cover it (printed p. 44). Use "
            "tension_controlled_capacity_singly (paragraph B-2d, for e'/d "
            "above the balanced eb'/d of Eq B-10: Eqs B-11, B-13, B-16).")
    fs = max(-fy, fs_raw)
    phi_pn = phi * (0.85 * fc_prime * ku - rho * fs) * b * d
    phi_mn = phi_pn * (e_prime_over_d - (1 - h / (2 * d))) * d
    out = {
        "ku": ku, "fs": fs, "phi_pn": phi_pn, "phi_mn": phi_mn,
        "equation": "B-17/B-18/B-19/B-21", "printed_page": "44",
        "pdf_page": "49", "limit_governs": False,
    }
    if fs_raw >= -fy:
        return out

    # B-19 below -fy: Eq B-21's ku was found with the steel elastic. Solve
    # Eqs B-2 and B-5 again with fs = -fy. Bracket: from the ku at which
    # B-19 = -fy (below it the steel has not yielded in compression) to
    # _KU_MAX; the residual there is ku^2 + 2(e'/d - 1)ku + a constant,
    # rising for ku > 1 - e'/d, so the root is the only one.
    def resid(k):
        return _equilibrium_residual(k, e_prime_over_d, 0.0, rho, 0.0,
                                     fc_prime, -fy, 0.0)

    k_lo = beta1 * esec / (esec - fy)
    tol = 1e-9 * 0.85 * fc_prime
    r_lo = resid(k_lo)
    if r_lo > tol or resid(_KU_MAX) <= 0.0:
        raise ValueError(
            f"Eq B-19 gives fs = {fs_raw:.4g} ksi at the root of Eq B-21 "
            f"(ku = {ku:.4g}), below -fy = {-fy:g} ksi, and Eqs B-2 and B-5 "
            f"(printed p. 42) with fs = -fy have no root between ku = "
            f"{k_lo:.4g} (where Eq B-19 reaches -fy) and {_KU_MAX:g} for "
            f"e'/d = {e_prime_over_d:g}: the section is outside what "
            "paragraph B-2e's equations cover.")
    ku_eq = k_lo if r_lo >= -tol else _bisect_ku(resid, k_lo, _KU_MAX)
    phi_pn_eq = phi * (0.85 * fc_prime * ku_eq + rho * fy) * b * d
    out.update({
        "ku": ku_eq, "fs": -fy, "phi_pn": phi_pn_eq,
        "phi_mn": phi_pn_eq * (e_prime_over_d - (1 - h / (2 * d))) * d,
        "equation": "B-2/B-5/B-17/B-18/B-19", "printed_page": "42-44",
        "pdf_page": "47-49", "limit_governs": True,
        "ku_cubic": ku, "fs_unlimited": fs_raw, "phi_pn_cubic": phi_pn,
        "note": (
            f"Eq B-19 gives fs = {fs_raw:.4g} ksi at the root of Eq B-21 "
            f"(ku = {ku:.4g}), below -fy = {-fy:g} ksi: the steel has "
            "yielded in compression, and the page prints fs (>= -fy) beside "
            "Eq B-19 (printed p. 44). Eq B-21 is derived with the steel "
            "not yielded, so its ku does not balance the section with fs "
            "held at -fy. The library solves the manual's own equilibrium "
            "equations, Eqs B-2 and B-5 (printed p. 42), with fs = -fy: ku "
            f"= {ku_eq:.4g} and phi Pn = {phi_pn_eq:.1f} kips, against "
            f"{phi_pn:.1f} kips with Eq B-21's ku (phi_pn_cubic). Solving "
            "again with fs at -fy is the library's reading. Eq B-1's phi "
            "Pn(max) (printed p. 42) still limits phi Pn."),
    })
    return out


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

        fs' = [(ku - beta1*d'/d) / (beta1 - ku)] * Es*epsilon_y   (B-31, <= fy)
        fs' = Es*ec*[ku - beta1*(d'/d)] / ku                       (B-37, >= -fy)

    fs' is held within -fy..fy in both regimes (ruling 42 on REF-76): each
    equation prints one bound (B-31 <= fy, printed p. 47; B-37 >= -fy,
    printed p. 48) and the library applies both, since steel carries no
    more than yield. Where a bound governs, the result gives
    ``limit_governs`` True, the equation's value as ``fs_prime_unlimited``
    and a note (B-37 above fy used to be returned as it came).

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

    Raises
    ------
    ValueError
        REF-76: fs' is bounded at fy (B-31, printed p. 47) or -fy (B-37,
        printed p. 48), so an input no section can have is refused rather
        than bounded: fy, es, ec, ku or beta1 not positive; beta1 above 1;
        d'/d outside 0 to 1 (the compression steel lies between the
        compression face and the tension steel); and for B-31, ku not below
        beta1 (its denominator; the neutral axis would be at or below the
        tension steel).
    """
    for name, val in (("fy", fy), ("es", es), ("ec", ec), ("ku", ku),
                      ("beta1", beta1)):
        if val is None or val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    if beta1 > 1.0:
        raise ValueError(f"beta1 must be at most 1 (ACI 318-19 beta_1 is "
                         f"0.65 to 0.85), got {beta1}")
    if not 0.0 < dprime_over_d < 1.0:
        raise ValueError(
            f"dprime_over_d must be between 0 and 1 (d' is the depth of the "
            f"compression steel, d that of the tension steel), got "
            f"{dprime_over_d}")
    if regime == "tension_controlled" and ku >= beta1:
        raise ValueError(
            f"Eq B-31 needs ku below beta1 (its denominator beta1 - ku; the "
            f"neutral axis above the tension steel), got ku={ku}, "
            f"beta1={beta1}")
    if regime == "tension_controlled":
        ey = fy / es
        raw = (ku - beta1 * dprime_over_d) / (beta1 - ku) * es * ey
        eq = "B-31"
        printed = "Eq B-31 prints fs' (<= fy) (printed p. 47)"
    elif regime == "compression_controlled":
        raw = es * ec * (ku - beta1 * dprime_over_d) / ku
        eq = "B-37"
        printed = ("Eq B-37 prints only the lower bound, fs' (>= -fy) "
                   "(printed p. 48); Eq B-31 prints the upper, fs' (<= fy) "
                   "(printed p. 47)")
    else:
        raise ValueError(
            f"regime must be 'tension_controlled' or 'compression_controlled', "
            f"got {regime!r}"
        )
    fs_prime, note = _yield_bounded(raw, fy, "fs'", printed)
    out = {"fs_prime": fs_prime, "equation": eq,
           "printed_page": "46-48", "pdf_page": "51-53",
           "limit_governs": note is not None}
    if note:
        out["fs_prime_unlimited"] = raw
        out["note"] = note
    return out


def balanced_eccentricity_doubly(kb, beta1, dprime_over_d, rho, rho_prime, fy,
                                  fc_prime, es=DEFAULT_ES_KSI, ec=DEFAULT_EC):
    """Eq B-28: balanced eccentricity ratio eb'/d (dimensionless) for a
    doubly reinforced member, with fs' at kb in ksi (printed p. 45).

        eb'/d = [2kb - kb^2 + fs'*rho'*(1 - d'/d)/(0.425*fc')]
                / [2kb - fy*rho/(0.425*fc') + fs'*rho'/(0.425*fc')]

    where fs' is the compression-steel stress at ku = kb (Eq B-31, held at
    fy as the page prints; ku = kb is set by Eq B-25, not solved for, so
    Eq B-28 stays the ratio of Eq B-24 to Eq B-23 with fs' at fy).

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
    fsr = compression_steel_stress_at_ku(
        kb, dprime_over_d, beta1, fy, es, ec, regime="tension_controlled",
    )
    fs_prime = fsr["fs_prime"]
    numerator = (2 * kb - kb ** 2
                 + fs_prime * rho_prime * (1 - dprime_over_d) / (0.425 * fc_prime))
    denominator = (2 * kb - fy * rho / (0.425 * fc_prime)
                   + fs_prime * rho_prime / (0.425 * fc_prime))
    eb_over_d = numerator / denominator
    out = {
        "eb_prime_over_d": eb_over_d, "fs_prime_at_kb": fs_prime,
        "equation": "B-28", "printed_page": "45", "pdf_page": 50,
        "limit_governs": fsr["limit_governs"],
    }
    if fsr["limit_governs"]:
        out["fs_prime_unlimited"] = fsr["fs_prime_unlimited"]
        out["note"] = fsr["note"]
    return out


def tension_controlled_capacity_doubly(e_prime_over_d, dprime_over_d, rho,
                                        rho_prime, fy, fc_prime, beta1,
                                        b, d, h, phi, es=DEFAULT_ES_KSI,
                                        ec=DEFAULT_EC, kb=None):
    """Eq B-33, B-29, B-30: design capacity phi*Pn (kips) and phi*Mn
    (kip-in.) of a doubly reinforced, tension-controlled member
    (e'/d > eb'/d), from strengths in ksi and dimensions in inches (printed
    pp. 46-47).

    Eq B-33 as typeset on the rendered page (printed p. 47, pdf 53; the
    PDF's text layer scrambles it, the page itself is clean), the same
    cubic the worked example prints in Appendix D-4 Step 3(a) (verified
    against that example, ku = 0.357 -- see the module tests):

        ku^3 + [2*(e'/d - 1) - beta1]*ku^2
             - {(fy/(0.425fc')) * [rho'*(e'/d + d'/d - 1) + rho*(e'/d)]
                + 2*beta1*(e'/d - 1)} * ku
             + (fy*beta1/(0.425fc')) * [rho'*(d'/d)*(e'/d + d'/d - 1)
                                          + rho*(e'/d)] = 0

    Then (Eq B-31, B-29, B-30):
        fs' = compression_steel_stress_at_ku(ku, ..., 'tension_controlled')
        phi*Pn = phi*(0.85*fc'*ku + rho'*fs' - rho*fy)*b*d
        phi*Mn = phi*Pn*[e'/d - (1 - h/(2d))]*d

    Eq B-33 comes from putting Eq B-31, with no bound, into Eq B-32 (the
    equilibrium equations B-23 and B-24 with fs = fy), so its ku balances
    the section only while B-31's fs' is below fy. Where B-31 is above fy
    at B-33's root (near the balanced point, and only where d'/d is below
    (Es*ec - fy)/(Es*ec + fy), 0.18 for Grade 60 steel) the page's fs'
    (<= fy) holds fs' at fy, and the library solves Eq B-32 again with
    fs' = fy for ku (the library's reading, ruling 42 on REF-76; B-33's ku
    with fs' held at fy left phi*Pn out of equilibrium). It is solved by
    bisection between ku = beta1*(1 + d'/d)/2, where B-31 reaches fy (below
    it the compression steel has not yielded), and the balanced kb of Eq
    B-25 (above it the tension steel has not yielded and the section is not
    controlled by tension). The result then gives ``limit_governs`` True,
    B-33's root as ``ku_cubic``, B-31 there as ``fs_prime_unlimited``,
    B-33's ku with fs' = fy as ``phi_pn_cubic``, and a note.

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
        {'ku', 'fs_prime', 'phi_pn', 'phi_mn', 'limit_governs',
         'equation': 'B-29/B-30/B-33', ...}; where fs' is held at fy also
        'ku_cubic', 'fs_prime_unlimited', 'phi_pn_cubic' and 'note', and
        'equation' names B-32 in place of B-33.

    Raises
    ------
    ValueError
        Where Eq B-31's fs' is above fy at Eq B-33's root and Eq B-32 with
        fs' = fy has no root in the bracket (the section is not controlled
        by tension, or the compression steel has not yielded there).
    """
    e = e_prime_over_d
    dpr = dprime_over_d
    k = fy / (0.425 * fc_prime)
    a2 = 2 * (e - 1) - beta1
    a1 = -(k * (rho_prime * (e + dpr - 1) + rho * e) + 2 * beta1 * (e - 1))
    a0 = k * beta1 * (rho_prime * dpr * (e + dpr - 1) + rho * e)
    coeffs = [1.0, a2, a1, a0]
    ku = _solve_cubic_ku(coeffs, kb=kb, prefer="lt_kb")
    fsr = compression_steel_stress_at_ku(
        ku, dprime_over_d, beta1, fy, es, ec, regime="tension_controlled",
    )
    fs_prime = fsr["fs_prime"]
    phi_pn = phi * (0.85 * fc_prime * ku + rho_prime * fs_prime - rho * fy) * b * d
    phi_mn = phi_pn * (e_prime_over_d - (1 - h / (2 * d))) * d
    out = {
        "ku": ku, "fs_prime": fs_prime, "phi_pn": phi_pn, "phi_mn": phi_mn,
        "equation": "B-29/B-30/B-33", "printed_page": "46-47",
        "pdf_page": "51-52", "limit_governs": False,
    }
    if not fsr["limit_governs"]:
        return out

    # B-31 above fy (its lower side cannot pass -fy for d'/d below 1): Eq
    # B-33's ku was found with the compression steel elastic. Solve Eq B-32
    # again with fs' = fy.
    fsp_raw = fsr["fs_prime_unlimited"]

    def resid(k_):
        return _equilibrium_residual(k_, e, dpr, rho, rho_prime, fc_prime,
                                     fy, fy)

    k_lo = beta1 * (1 + dpr) / 2
    k_hi = beta1 * es * ec / (es * ec + fy)
    tol = 1e-9 * 0.85 * fc_prime
    head = (f"Eq B-31 gives fs' = {fsp_raw:.4g} ksi at the root of Eq B-33 "
            f"(ku = {ku:.4g}), above fy = {fy:g} ksi")
    r_lo, r_hi = resid(k_lo), resid(k_hi)
    if k_lo >= k_hi or r_hi < -tol:
        why = (f"Eq B-31 reaches fy only at ku = {k_lo:.4g}, above the "
               f"balanced kb = {k_hi:.4g} (Eq B-25), so that root is"
               if k_lo >= k_hi else
               "Eq B-32 (printed p. 47) with fs' = fy balances only above "
               f"the balanced kb = {k_hi:.4g} (Eq B-25),")
        raise ValueError(
            f"{head}, and {why} where the tension steel has not yielded: "
            "the section is not controlled by tension and paragraph B-3e "
            "does not cover it. Use compression_controlled_capacity_doubly "
            "(paragraph B-3f, for e'/d at or below the balanced eb'/d of "
            "Eq B-28).")
    if r_lo > tol:
        raise ValueError(
            f"{head}, and Eq B-32 (printed p. 47) with fs' = fy has no root "
            f"between ku = {k_lo:.4g} (where Eq B-31 reaches fy) and the "
            f"balanced kb = {k_hi:.4g} for e'/d = {e:g}: the section is "
            "outside what paragraph B-3e's equations cover.")
    if r_hi <= tol:
        ku_eq = k_hi
    elif r_lo >= -tol:
        ku_eq = k_lo
    else:
        ku_eq = _bisect_ku(resid, k_lo, k_hi)
    phi_pn_eq = phi * (0.85 * fc_prime * ku_eq + rho_prime * fy - rho * fy) * b * d
    out.update({
        "ku": ku_eq, "fs_prime": fy, "phi_pn": phi_pn_eq,
        "phi_mn": phi_pn_eq * (e_prime_over_d - (1 - h / (2 * d))) * d,
        "equation": "B-29/B-30/B-31/B-32", "limit_governs": True,
        "ku_cubic": ku, "fs_prime_unlimited": fsp_raw,
        "phi_pn_cubic": phi_pn,
        "note": (
            f"{head}: the compression steel has yielded, and the page "
            "prints fs' (<= fy) beside Eq B-31 (printed p. 47). Eq B-33 is "
            "derived with the compression steel not yielded, so its ku "
            "does not balance the section with fs' held at fy. The library "
            "solves the manual's own equilibrium equation, Eq B-32 (printed "
            "p. 47; Eqs B-23 and B-24 with fs = fy), with fs' = fy: ku = "
            f"{ku_eq:.4g} and phi Pn = {phi_pn_eq:.1f} kips, against "
            f"{phi_pn:.1f} kips with Eq B-33's ku (phi_pn_cubic). Solving "
            "again with fs' at fy is the library's reading."),
    })
    return out


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

    The cubic (Eq B-39) comes from putting Eqs B-36 and B-37, with no upper
    bound, into Eq B-38 (the equilibrium equations B-23 and B-24, printed
    p. 45; B-38 is typeset with "=" where B-23 has its first "+", printed
    p. 48, a misprint), so its ku balances the section only while neither
    steel has yielded. B-37 prints only fs' (>= -fy) (printed p. 48), yet
    it passes
    fy at every ku from the balanced kb up where d'/d is below
    (Es*ec - fy)/(Es*ec + fy), 0.18 for Grade 60 steel: there the
    compression steel of every compression-controlled section has yielded.
    Past yield (the library's reading, ruling 42 on REF-76; the cubic's ku
    with a stress held at fy left phi*Pn out of equilibrium):

    - fs' (B-37) above fy at the cubic's root: fs' = fy, and ku is solved
      again from Eqs B-23 and B-24 with fs' = fy and fs from Eq B-36 (held
      at -fy if below it), by bisection. The bracket runs from the larger
      of the ku at which B-37 reaches fy (below it the compression steel
      has not yielded) and the balanced kb of Eq B-25 (below it the tension
      steel has yielded and compression does not control) up to 5, the
      cubic solver's limit. The result gives ``limit_governs`` True, the
      cubic's root as ``ku_cubic``, B-37 there as ``fs_prime_unlimited``,
      phi*Pn by Eqs B-39, B-36, B-37 and B-34 as printed as
      ``phi_pn_cubic``, and a note.
    - fs (B-36) above fy: the tension steel has yielded, the section is
      controlled by tension and paragraph B-3f does not cover it. Refused;
      use ``tension_controlled_capacity_doubly`` (paragraph B-3e). An fs'
      below -fy only occurs here.

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
        {'ku', 'fs', 'fs_prime', 'phi_pn', 'phi_mn', 'limit_governs',
         'equation': 'B-34/B-35/B-36/B-37/B-39', ...}; where fs' is held at
        fy also 'ku_cubic', 'fs_prime_unlimited', 'phi_pn_cubic' and 'note'
        ('fs_unlimited' too if fs is held at -fy), and 'equation' names
        B-23 and B-24 in place of B-37 and B-39.

    Raises
    ------
    ValueError
        If fy, es or ec is not positive (they set the bounds on fs and
        fs'); if the tension steel has yielded (Eq B-36's fs above fy: the
        section is controlled by tension); or if Eqs B-23 and B-24 with
        fs' = fy have no root in the bracket.
    """
    for name, val in (("fy", fy), ("es", es), ("ec", ec)):
        if val is None or val <= 0:
            raise ValueError(f"{name} must be > 0, got {val}")
    e = e_prime_over_d
    dpr = dprime_over_d
    esec = es * ec
    coeff_k = esec / (0.425 * fc_prime)
    a2 = 2 * (e - 1)
    a1 = coeff_k * ((rho + rho_prime) * e - rho_prime * (1 - dpr))
    a0 = -beta1 * coeff_k * (rho_prime * dpr * (e + dpr - 1) + rho * e)
    coeffs = [1.0, a2, a1, a0]
    ku = _solve_cubic_ku(coeffs, kb=kb, prefer="gt_kb")
    fs_raw = esec * (beta1 - ku) / ku
    fsr = compression_steel_stress_at_ku(
        ku, dprime_over_d, beta1, fy, es, ec, regime="compression_controlled",
    )
    fsp_raw = fsr.get("fs_prime_unlimited", fsr["fs_prime"])
    tension_controls = (
        "the tension steel has yielded, so the section is controlled by "
        "tension and paragraph B-3f's Eqs B-34 to B-39, which take the "
        "tension steel below yield, do not cover it (printed pp. 47-48). "
        "Use tension_controlled_capacity_doubly (paragraph B-3e, for e'/d "
        "above the balanced eb'/d of Eq B-28).")

    if fsp_raw <= fy:
        if fs_raw > fy * (1 + _YIELD_TOL):
            raise ValueError(
                f"Eq B-36 gives fs = {fs_raw:.4g} ksi at the root of Eq "
                f"B-39 (ku = {ku:.4g}), above fy = {fy:g} ksi: "
                + tension_controls
                + ("" if kb is not None else
                   " kb was not given, so the cubic's smallest root was "
                   "taken: if e'/d is not above eb'/d, give kb "
                   "(balanced_strain_kb) so that the root above kb is "
                   "taken."))
        # Neither steel past yield: Eqs B-34 to B-39 as printed.
        fs = max(-fy, min(fy, fs_raw))
        fs_prime = fsr["fs_prime"]
        phi_pn = phi * (0.85 * fc_prime * ku + rho_prime * fs_prime - rho * fs) * b * d
        phi_mn = phi_pn * (e_prime_over_d - (1 - h / (2 * d))) * d
        return {
            "ku": ku, "fs": fs, "fs_prime": fs_prime, "phi_pn": phi_pn,
            "phi_mn": phi_mn, "equation": "B-34/B-35/B-36/B-37/B-39",
            "printed_page": "47-48", "pdf_page": "52-53",
            "limit_governs": False,
        }

    # B-37 above fy: the cubic's ku was found with the compression steel
    # elastic. Solve Eqs B-23 and B-24 again with fs' = fy; fs is Eq B-36,
    # held at -fy (it cannot pass fy from kb up).
    def fs_at(k_):
        return max(-fy, min(fy, esec * (beta1 - k_) / k_))

    def resid(k_):
        return _equilibrium_residual(k_, e, dpr, rho, rho_prime, fc_prime,
                                     fs_at(k_), fy)

    k_yield = beta1 * dpr * esec / (esec - fy)
    k_bal = beta1 * esec / (esec + fy)
    k_lo = max(k_yield, k_bal)
    tol = 1e-9 * 0.85 * fc_prime
    head = (f"Eq B-37 gives fs' = {fsp_raw:.4g} ksi at the root of Eq B-39 "
            f"(ku = {ku:.4g}), above fy = {fy:g} ksi")
    r_lo = resid(k_lo)
    if r_lo > tol and k_lo == k_bal:
        raise ValueError(
            f"{head}, and with fs' = fy Eqs B-23 and B-24 (printed p. 45) "
            f"balance only below the balanced kb = {k_bal:.4g} (Eq B-25): "
            + tension_controls)
    if r_lo > tol or resid(_KU_MAX) <= 0.0:
        raise ValueError(
            f"{head}, and Eqs B-23 and B-24 (printed p. 45) with fs' = fy "
            f"have no root between ku = {k_lo:.4g} (where Eq B-37 reaches "
            f"fy) and {_KU_MAX:g} for e'/d = {e:g}: the section is outside "
            "what paragraph B-3f's equations cover.")
    ku_eq = k_lo if r_lo >= -tol else _bisect_ku(resid, k_lo, _KU_MAX)
    fs_eq_raw = esec * (beta1 - ku_eq) / ku_eq
    fs = fs_at(ku_eq)
    phi_pn = phi * (0.85 * fc_prime * ku_eq + rho_prime * fy - rho * fs) * b * d
    phi_pn_cubic = phi * (0.85 * fc_prime * ku + rho_prime * fsp_raw
                          - rho * fs_raw) * b * d
    note = (
        f"{head}: the compression steel has yielded. Eq B-39 is derived "
        "with the compression steel not yielded (Eq B-37 prints only fs' "
        "(>= -fy), printed p. 48), so its ku does not balance the section "
        "with fs' held at fy. The library solves the manual's own "
        "equilibrium equations, Eqs B-23 and B-24 (printed p. 45), with "
        f"fs' = fy and fs from Eq B-36: ku = {ku_eq:.4g} and phi Pn = "
        f"{phi_pn:.1f} kips, "
        + ("a lower capacity than the cubic's" if phi_pn < phi_pn_cubic
           else "against the cubic's")
        + f" {phi_pn_cubic:.1f} kips (Eqs B-39, B-37 and B-34 as printed; "
        "phi_pn_cubic). Holding fs' at fy and solving again is the "
        "library's reading.")
    out = {
        "ku": ku_eq, "fs": fs, "fs_prime": fy, "phi_pn": phi_pn,
        "phi_mn": phi_pn * (e_prime_over_d - (1 - h / (2 * d))) * d,
        "equation": "B-23/B-24/B-34/B-35/B-36", "printed_page": "45-48",
        "pdf_page": "50-53", "limit_governs": True,
        "ku_cubic": ku, "fs_prime_unlimited": fsp_raw,
        "phi_pn_cubic": phi_pn_cubic,
    }
    if fs_eq_raw < -fy:
        out["fs_unlimited"] = fs_eq_raw
        note += (f" Eq B-36 gives fs = {fs_eq_raw:.4g} ksi at this ku, held "
                 f"at -fy = {-fy:g} ksi the same way (B-36 prints no bound).")
    out["note"] = note
    return out


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
    b=12 in, d=20.5 in, phi=0.9): this function returns phi*Mn = 1649.9
    kip-in., printed as "1649.9 in.-k = 137.5 ft-k" (printed p. 54,
    EM_1110-2-2104_2025.pdf pdf 60).

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
        Cs = As'*(fs' - 0.85*fc')                 [Eq B-53, as C-3 uses it]
        Mn = Cc*(d - a/2) + Cs*(d - d')            [Eq B-51]

    Eq B-53 is typeset "Cs = 0.85 fs' - 0.85 fc' A's" (printed p. 51, pdf
    57), a misprint (not a force); the code uses As'*(fs' - 0.85*fc'),
    which Appendix C-3 prints and uses (printed p. 56, pdf 62).

    Verified against Appendix C-3 / Table C-1 (As=8 sq in, As'=4 sq in,
    fc'=4 ksi, fy=60 ksi, b=12 in, d=60 in, d'=6 in): a = 8.62 in,
    c = 10.14 in, Mn = 26,515.2 in-k. The compression steel does NOT yield
    in this case (es' = 0.003*(10.14 - 6)/10.14 = 0.0012 < ey, so fs' =
    87 - 443.7/a = 35.5 ksi, from the quadratic a^2 - 3.57a - 43.5 = 0);
    the print's check "es' = 0.0148 > 0.0021" is worked from d - c and is
    the TENSION-steel strain, labelled es' in the print.

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
