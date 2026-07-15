"""Eurocode 7-2 derived-value equations.

Digitized equations from EN 1997-2:2007, Eurocode 7: Geotechnical design -
Part 2: Ground investigation and testing -- the main-body Section 4
equations (4.1)-(4.5) defining derived-value formulas, plus the annex
example correlations (Annexes D-K, N) that are closed-form expressions
rather than tabulations.  Page citations are the *printed* page number of
the standard.
"""

import math


# ============================================================================
# Eq. 4.1 / 4.2: undrained shear strength from CPT / CPTU cone resistance
# (printed p.43)
# ============================================================================

def equation_4_1_cu_from_cpt(qc_kpa: float, sigma_v0_kpa: float, nk: float) -> float:
    """Undrained shear strength from CPT cone resistance (Eq. 4.1).

    cu = (qc - sigma_v0) / Nk

    Parameters
    ----------
    qc_kpa : float
        Cone penetration resistance, in kPa.
    sigma_v0_kpa : float
        Initial total vertical overburden stress at the depth considered, in kPa.
    nk : float
        Cone factor, estimated from local experience or reliable
        correlations.  Must be > 0.

    Returns
    -------
    float
        Undrained shear strength cu, in kPa.

    Raises
    ------
    ValueError
        If nk <= 0.
    """
    if nk <= 0:
        raise ValueError(f"nk must be > 0, got {nk}")
    return (qc_kpa - sigma_v0_kpa) / nk


def equation_4_2_cu_from_cptu(qt_kpa: float, sigma_v0_kpa: float, nkt: float) -> float:
    """Undrained shear strength from CPTU corrected cone resistance (Eq. 4.2).

    cu = (qt - sigma_v0) / Nkt

    Parameters
    ----------
    qt_kpa : float
        Cone penetration resistance corrected for pore water pressure
        effects, in kPa.
    sigma_v0_kpa : float
        Initial total vertical overburden stress at the depth considered, in kPa.
    nkt : float
        Cone factor for CPTU, estimated from local experience or reliable
        correlations.  Must be > 0.

    Returns
    -------
    float
        Undrained shear strength cu, in kPa.

    Raises
    ------
    ValueError
        If nkt <= 0.
    """
    if nkt <= 0:
        raise ValueError(f"nkt must be > 0, got {nkt}")
    return (qt_kpa - sigma_v0_kpa) / nkt


# ============================================================================
# Eq. 4.3: oedometer modulus from CPT cone resistance (printed p.44)
# ============================================================================

def equation_4_3_oedometer_modulus_from_qc(alpha: float, qc_mpa: float) -> float:
    """Oedometer modulus from CPT cone resistance (Eq. 4.3).

    Eoed = alpha * qc

    Parameters
    ----------
    alpha : float
        Correlation factor depending on local experience (see
        tables.table_d2_alpha_oedometer for example values by soil type,
        Annex D.4).
    qc_mpa : float
        Cone penetration resistance, in MPa.

    Returns
    -------
    float
        Oedometer modulus Eoed, in MPa.
    """
    return alpha * qc_mpa


# ============================================================================
# Eq. 4.4: undrained shear strength from field vane test (printed p.56)
# ============================================================================

def equation_4_4_cu_from_fvt(mu: float, cfv_kpa: float) -> float:
    """Undrained shear strength from field vane test (Eq. 4.4).

    cu = mu * cfv

    Parameters
    ----------
    mu : float
        Correction factor, determined based on local experience (see
        equation_i5_fvt_correction_factor for example formulas, Annex I.5).
    cfv_kpa : float
        Undrained shear strength measured in the field vane test, in kPa.

    Returns
    -------
    float
        Corrected undrained shear strength cu, in kPa.
    """
    return mu * cfv_kpa


# ============================================================================
# Eq. 4.5: undrained shear strength from flat dilatometer test (printed p.57)
# ============================================================================

def equation_4_5_cu_from_dmt(sigma_v0_eff_kpa: float, k_dmt: float,
                              i_dmt: float = None) -> float:
    """Undrained shear strength of non-cemented clays from DMT (Eq. 4.5).

    cu = 0.22 * sigma'v0 * (0.5 * KDMT)^1.25

    Valid only when the DMT material index IDMT < 0.8 (non-cemented clay).

    Parameters
    ----------
    sigma_v0_eff_kpa : float
        Initial effective vertical stress at the test depth, in kPa.
    k_dmt : float
        Horizontal stress index from the flat dilatometer test.
    i_dmt : float, optional
        Material index from the flat dilatometer test.  If given and
        >= 0.8, raises ValueError (outside the equation's stated validity).

    Returns
    -------
    float
        Undrained shear strength cu, in kPa.

    Raises
    ------
    ValueError
        If i_dmt is given and >= 0.8.
    """
    if i_dmt is not None and i_dmt >= 0.8:
        raise ValueError(
            f"Eq. 4.5 is only valid for IDMT < 0.8 (non-cemented clay), got {i_dmt}"
        )
    return 0.22 * sigma_v0_eff_kpa * (0.5 * k_dmt) ** 1.25


# ============================================================================
# Annex D.2: effective angle of shearing resistance from CPT cone resistance,
# poorly-graded sands (printed p.112; Stenzel et al. 1978 / DIN 4094-1)
# ============================================================================

def equation_d2_phi_from_qc(qc_mpa: float) -> float:
    """Effective angle of shearing resistance from CPT, poorly-graded sands (D.2).

    phi' = 13.5 * log10(qc) + 23

    Valid for poorly-graded sands (Cu < 3) above groundwater, for cone
    penetration resistances 5 MPa <= qc <= 28 MPa.  Considered a
    conservative estimate.

    Parameters
    ----------
    qc_mpa : float
        Cone penetration resistance, in MPa.  Must be in [5, 28].

    Returns
    -------
    float
        Effective angle of shearing resistance phi', in degrees.

    Raises
    ------
    ValueError
        If qc_mpa is outside the valid range 5-28 MPa.
    """
    if not (5.0 <= qc_mpa <= 28.0):
        raise ValueError(f"qc_mpa must be 5-28 MPa (D.2 validity range), got {qc_mpa}")
    return 13.5 * math.log10(qc_mpa) + 23


# ============================================================================
# Annex D.3: Young's modulus from CPT cone resistance for settlement of
# spread foundations in coarse soil (printed p.112; Schmertmann method)
# ============================================================================

def equation_d3_youngs_modulus_from_qc(qc_mpa: float, foundation_shape: str) -> float:
    """Drained Young's modulus from CPT for Schmertmann settlement method (D.3).

    E' = 2.5 * qc  (axisymmetric: circular and square foundations)
    E' = 3.5 * qc  (plane strain: strip foundations)

    Parameters
    ----------
    qc_mpa : float
        Cone penetration resistance, in MPa.
    foundation_shape : str
        'axisymmetric' (circular/square) or 'plane_strain' (strip).

    Returns
    -------
    float
        Drained Young's modulus E', in MPa.

    Raises
    ------
    ValueError
        If foundation_shape is not recognized.
    """
    shape = foundation_shape.strip().lower().replace(" ", "_").replace("-", "_")
    if shape in ("axisymmetric", "circular", "square"):
        return 2.5 * qc_mpa
    if shape in ("plane_strain", "strip"):
        return 3.5 * qc_mpa
    raise ValueError(
        f"Unknown foundation_shape '{foundation_shape}'. "
        f"Use axisymmetric or plane_strain"
    )


def equation_d3_settlement_coefficients(sigma_v0_eff_kpa: float, q_kpa: float,
                                         t_years: float, foundation_shape: str,
                                         l_over_b: float = 1.0) -> dict:
    """C1, C2, C3 coefficients for the Schmertmann settlement method (D.3).

    s = C1 * C2 * (q - sigma'v0) * integral[0,zi]( Iz / (C3 * E') ) dz

    This function returns the three scalar coefficients; the strain
    influence factor Iz distribution (Figure D.1) and the resulting
    integral are chart-dependent and are not digitized here.

    Parameters
    ----------
    sigma_v0_eff_kpa : float
        Initial effective vertical stress at the foundation level, in kPa.
    q_kpa : float
        Design normal pressure applied on the foundation, in kPa.  Must
        be > sigma_v0_eff_kpa.
    t_years : float
        Time since load application, in years.  Must be > 0.
    foundation_shape : str
        'square' (C3 = 1.25) or 'strip' (C3 = 1.75, valid for L > 10B).
    l_over_b : float
        Foundation length-to-width ratio (informational; strip requires
        L > 10B per the standard).

    Returns
    -------
    dict
        Keys: c1, c2, c3.

    Raises
    ------
    ValueError
        If q_kpa <= sigma_v0_eff_kpa, t_years <= 0, or foundation_shape
        is not recognized.
    """
    if q_kpa <= sigma_v0_eff_kpa:
        raise ValueError("q_kpa must be > sigma_v0_eff_kpa")
    if t_years <= 0:
        raise ValueError(f"t_years must be > 0, got {t_years}")
    shape = foundation_shape.strip().lower()
    if shape == "square":
        c3 = 1.25
    elif shape == "strip":
        if l_over_b <= 10:
            raise ValueError("strip foundations require L > 10B (D.3 validity)")
        c3 = 1.75
    else:
        raise ValueError(f"Unknown foundation_shape '{foundation_shape}'. Use square or strip")

    c1 = 1 - 0.5 * (sigma_v0_eff_kpa / (q_kpa - sigma_v0_eff_kpa))
    c2 = 1.2 + 0.2 * math.log10(t_years)
    return {"c1": round(c1, 4), "c2": round(c2, 4), "c3": c3}


# ============================================================================
# Annex D.5: stiffness coefficient w1 from CPT cone resistance, for the
# stress-dependent oedometer modulus Eoed = w1 * (sigma'v/pa)^w2
# (printed p.114-115; Stenzel et al. 1978, Biedermann 1984, DIN 4094-1)
# ============================================================================

def equation_d5_stiffness_coefficient_from_qc(soil_type: str, qc_mpa: float) -> float:
    """Stiffness coefficient w1 from CPT cone resistance (Annex D.5).

    w1 = 167*lg(qc) + 113   poorly-graded sands (Cu <= 3) above GW, 5<=qc<=30 MPa
    w1 = 463*lg(qc) - 13    well-graded sands (Cu > 6) above GW, 5<=qc<=30 MPa
    w1 = 15.2*qc + 50       low-plasticity clays (0.75<=Ic<=1.30) above GW,
                            0.6<=qc<=3.5 MPa

    Used in Eoed = w1 * (sigma'v / pa)^w2 (w2 = 0.5 for Cu<=3 sands, 0.6 for
    low-plasticity clays).

    Parameters
    ----------
    soil_type : str
        'poorly_graded_sand', 'well_graded_sand', or 'low_plasticity_clay'.
    qc_mpa : float
        Cone penetration resistance, in MPa (validity range depends on
        soil_type; see above).

    Returns
    -------
    float
        Stiffness coefficient w1 (dimensionless).

    Raises
    ------
    ValueError
        If soil_type is not recognized or qc_mpa is outside that soil
        type's validity range.
    """
    st = soil_type.strip().lower().replace(" ", "_").replace("-", "_")
    if st == "poorly_graded_sand":
        if not (5.0 <= qc_mpa <= 30.0):
            raise ValueError(f"qc_mpa must be 5-30 MPa for poorly_graded_sand, got {qc_mpa}")
        return 167 * math.log10(qc_mpa) + 113
    if st == "well_graded_sand":
        if not (5.0 <= qc_mpa <= 30.0):
            raise ValueError(f"qc_mpa must be 5-30 MPa for well_graded_sand, got {qc_mpa}")
        return 463 * math.log10(qc_mpa) - 13
    if st == "low_plasticity_clay":
        if not (0.6 <= qc_mpa <= 3.5):
            raise ValueError(f"qc_mpa must be 0.6-3.5 MPa for low_plasticity_clay, got {qc_mpa}")
        return 15.2 * qc_mpa + 50
    raise ValueError(
        f"Unknown soil_type '{soil_type}'. "
        f"Valid: poorly_graded_sand, well_graded_sand, low_plasticity_clay"
    )


# ============================================================================
# Annex F.3: Burland & Burbridge (1985) settlement of spread foundations in
# sand from SPT results (printed p.126-128)
# ============================================================================

def equation_burland_burbridge_icc(n_avg: float) -> float:
    """Foundation subgrade compressibility index Icc from average SPT N (F.3(3)).

    Icc = 1.71 / N_avg^1.4

    Parameters
    ----------
    n_avg : float
        Arithmetic mean of measured (uncorrected) SPT N-values over the
        depth of influence z1 = B^0.75.  Must be > 0.

    Returns
    -------
    float
        Icc = af / B^0.7, in mm/kPa per unit B^0.7.

    Raises
    ------
    ValueError
        If n_avg <= 0.
    """
    if n_avg <= 0:
        raise ValueError(f"n_avg must be > 0, got {n_avg}")
    return 1.71 / n_avg ** 1.4


def equation_burland_burbridge_shape_factor(l_over_b: float) -> float:
    """Length-to-width correction factor fs for Burland & Burbridge settlement (F.3(6)).

    fs = [1.25 * (L/B) / (L/B + 0.25)]^2

    fs tends to 1.56 as L/B tends to infinity; no depth correction is
    needed for D/B < 3.

    Parameters
    ----------
    l_over_b : float
        Foundation length-to-width ratio L/B.  Must be >= 1.

    Returns
    -------
    float
        Shape correction factor fs.

    Raises
    ------
    ValueError
        If l_over_b < 1.
    """
    if l_over_b < 1:
        raise ValueError(f"l_over_b must be >= 1, got {l_over_b}")
    return (1.25 * l_over_b / (l_over_b + 0.25)) ** 2


def equation_burland_burbridge_settlement(b_m: float, icc: float, q_kpa: float,
                                           sigma_p_kpa: float) -> float:
    """Immediate settlement of a square footing on sand (Burland & Burbridge, F.3).

    For q' >= sigma'p (over-consolidated sand, effective foundation
    pressure at/above the maximum previous overburden pressure):
        si = sigma'p * B^0.7 * Icc / 3          if q' <= sigma'p
        si = (q' - sigma'p) * B^0.7 * Icc       for normally consolidated sand

    This function selects the applicable branch from q_kpa vs sigma_p_kpa.

    Parameters
    ----------
    b_m : float
        Footing width B, in m.  Must be > 0.
    icc : float
        Foundation subgrade compressibility index (see
        equation_burland_burbridge_icc).
    q_kpa : float
        Average effective foundation pressure q', in kPa.
    sigma_p_kpa : float
        Maximum previous overburden pressure sigma'p, in kPa.

    Returns
    -------
    float
        Immediate settlement si, in mm.

    Raises
    ------
    ValueError
        If b_m <= 0.
    """
    if b_m <= 0:
        raise ValueError(f"b_m must be > 0, got {b_m}")
    b07 = b_m ** 0.7
    if q_kpa <= sigma_p_kpa:
        return sigma_p_kpa * b07 * icc / 3
    return (q_kpa - sigma_p_kpa) * b07 * icc


# ============================================================================
# Annex G.1: density index from dynamic probing (DP) blow counts
# (printed p.129; Stenzel et al. 1978 / DIN 4094-3)
# ============================================================================

_DP_ID_FORMULAS = {
    ("poorly_graded", "above", "dpl"): (0.15, 0.260),
    ("poorly_graded", "above", "dph"): (0.10, 0.435),
    ("poorly_graded", "below", "dpl"): (0.21, 0.230),
    ("poorly_graded", "below", "dph"): (0.23, 0.380),
    ("well_graded", "above", "dph"): (0.14, 0.550),
}


def equation_g1_density_index_from_dp(n10: float, grading: str, groundwater: str,
                                       probe_type: str) -> float:
    """Density index from dynamic probing (DP) blow count N10 (Annex G.1).

    ID = a + b * log10(N10), coefficients (a, b) depend on grading,
    groundwater position, and probe type.  Range of validity: 3 <= N10 <= 50.

    Parameters
    ----------
    n10 : float
        Number of blows per 10 cm penetration (N10L for DPL, N10H for DPH).
    grading : str
        'poorly_graded' (Cu <= 3) or 'well_graded' (Cu >= 6, sand-gravel).
    groundwater : str
        'above' or 'below' groundwater level.
    probe_type : str
        'dpl' (dynamic probing light) or 'dph' (dynamic probing heavy).

    Returns
    -------
    float
        Density index ID (fraction, 0-1).

    Raises
    ------
    ValueError
        If the (grading, groundwater, probe_type) combination is not
        tabulated (only 'well_graded'+'above'+'dph' is given in the
        standard; no well-graded-below-groundwater or DPL formula exists).
    """
    key = (
        grading.strip().lower().replace(" ", "_").replace("-", "_"),
        groundwater.strip().lower(),
        probe_type.strip().lower(),
    )
    if key not in _DP_ID_FORMULAS:
        raise ValueError(
            f"No G.1 correlation tabulated for (grading, groundwater, probe_type) "
            f"= {key}. Valid combinations: {sorted(_DP_ID_FORMULAS.keys())}"
        )
    a, b = _DP_ID_FORMULAS[key]
    return a + b * math.log10(n10)


# ============================================================================
# Annex G.3: stiffness coefficient w1 from dynamic probing (DP)
# (printed p.130; Stenzel et al. 1978 / Biedermann 1984 / DIN 4094-3)
# ============================================================================

_DP_W1_FORMULAS = {
    # (soil_type, probe_type): (coefficient, intercept)
    ("sand", "dpl"): (214, 71),
    ("sand", "dph"): (249, 161),
    ("clay", "dpl"): (4, 30),
    ("clay", "dph"): (6, 50),
}


def equation_g3_stiffness_coefficient_from_dp(n10: float, soil_type: str,
                                               probe_type: str) -> float:
    """Stiffness coefficient w1 from dynamic probing (DP) blow count (Annex G.3).

    Used in Eoed = w1 * (sigma'v/pa)^w2 (w2=0.5 for Cu<=3 sands, w2=0.6 for
    low-plasticity clays).

    Poorly-graded sands (Cu<=3) above groundwater:
        w1 = 214*lg(N10L) + 71  (DPL; 4<=N10L<=50)
        w1 = 249*lg(N10H) + 161 (DPH; 3<=N10H<=30)
    Low-plasticity clays (0.75<=Ic<=1.30) above groundwater:
        w1 = 4*N10L + 30  (DPL; 6<=N10L<=19)
        w1 = 6*N10H + 50  (DPH; 3<=N10H<=13)

    Parameters
    ----------
    n10 : float
        Number of blows per 10 cm penetration.
    soil_type : str
        'sand' (poorly-graded, Cu<=3) or 'clay' (low-plasticity, stiff).
    probe_type : str
        'dpl' or 'dph'.

    Returns
    -------
    float
        Stiffness coefficient w1 (dimensionless).

    Raises
    ------
    ValueError
        If soil_type/probe_type is not recognized.
    """
    key = (soil_type.strip().lower(), probe_type.strip().lower())
    if key not in _DP_W1_FORMULAS:
        raise ValueError(
            f"Unknown (soil_type, probe_type) '{key}'. "
            f"Valid: {sorted(_DP_W1_FORMULAS.keys())}"
        )
    coeff, const = _DP_W1_FORMULAS[key]
    if soil_type.strip().lower() == "sand":
        return coeff * math.log10(n10) + const
    return coeff * n10 + const


# ============================================================================
# Annex I.5: field vane test correction factor mu, based on Atterberg
# limits and state of consolidation (printed p.136-137; Larsson & Ahnberg
# 2003, Hansbo 1957)
# ============================================================================

def equation_i5_fvt_correction_factor(w_l_pct: float, roc: float = None,
                                       cfv_kpa: float = None,
                                       sigma_v0_eff_kpa: float = None) -> float:
    """Field vane correction factor mu from Atterberg limits and OCR (Annex I.5).

    Normally-consolidated / slightly over-consolidated clays:
        mu = (0.43 / wL)^0.45, floored at 0.5

    Clays with a known over-consolidation ratio Roc > 1.3:
        mu = (0.43 / wL)^0.45 * (Roc / 1.3)^-0.15

    If Roc is not known, it may be estimated from cfv = 0.45 * wL * sigma'p
    (Hansbo 1957), giving:
        mu = (0.43 / wL)^0.45 * (cfv / (0.585 * wL * sigma'v0))^-0.15

    In all three formulas wL is used as a *fraction* (e.g. 0.60 for a 60%
    liquid limit), not a percentage: the standard's Figure I.1 plots the
    companion chart method over wL = 0-200%, and the mu>=0.5 floor of the
    base formula becomes active almost exactly at wL=200% (fraction 2.0),
    confirming the fraction convention -- with wL taken as a raw percentage
    (e.g. 60), the base formula would be pinned at the 0.5 floor for every
    realistic clay, which cannot be the intended behaviour.

    Parameters
    ----------
    w_l_pct : float
        Liquid limit wL, in percent (e.g. 60 for 60%).  Must be > 0.
    roc : float, optional
        Over-consolidation ratio, if known.  If given and > 1.3, uses the
        Roc-based formula.
    cfv_kpa : float, optional
        Undrained shear strength measured in the field vane test, in kPa
        (used with sigma_v0_eff_kpa when roc is not known, to estimate
        the OCR-adjusted correction).
    sigma_v0_eff_kpa : float, optional
        Initial effective vertical stress, in kPa (paired with cfv_kpa).

    Returns
    -------
    float
        Correction factor mu (dimensionless), such that cu = mu * cfv.

    Raises
    ------
    ValueError
        If w_l_pct <= 0, or if roc is given but <= 1.3 (use the base
        formula instead), or if only one of cfv_kpa/sigma_v0_eff_kpa is
        given.
    """
    if w_l_pct <= 0:
        raise ValueError(f"w_l_pct must be > 0, got {w_l_pct}")
    wl_frac = w_l_pct / 100
    base = (0.43 / wl_frac) ** 0.45

    if roc is not None:
        if roc <= 1.3:
            raise ValueError(
                "roc is given but <= 1.3; use the base (NC/slightly OC) "
                "formula (omit roc) instead"
            )
        return base * (roc / 1.3) ** -0.15

    if (cfv_kpa is None) != (sigma_v0_eff_kpa is None):
        raise ValueError("cfv_kpa and sigma_v0_eff_kpa must be given together")

    if cfv_kpa is not None:
        return base * (cfv_kpa / (0.585 * wl_frac * sigma_v0_eff_kpa)) ** -0.15

    return max(base, 0.5)


# ============================================================================
# Annex J: oedometer modulus from flat dilatometer test (DMT) results
# (printed p.138; Marchetti 2001)
# ============================================================================

def equation_j_dmt_oedometer_modulus(i_dmt: float, k_dmt: float,
                                      e_dmt_mpa: float) -> dict:
    """One-dimensional tangent modulus Eoed from DMT results (Annex J).

    Eoed = RM * EDMT

    RM is estimated from IDMT and KDMT:
        IDMT <= 0.6:            RM = 0.14 + 2.36*lg(KDMT)
        0.6 < IDMT < 3.0:       RM = RM0 + (2.5 - RM0)*lg(KDMT),
                                 RM0 = 0.14 + 0.15*(IDMT - 0.6)
        IDMT >= 3:               RM = 0.5 + 2*lg(KDMT)
        KDMT > 10 (overrides):   RM = 0.32 + 2.18*lg(KDMT)
        RM is floored at 0.85.

    Parameters
    ----------
    i_dmt : float
        Material index from the flat dilatometer test.
    k_dmt : float
        Horizontal stress index from the flat dilatometer test.  Must be > 0.
    e_dmt_mpa : float
        Dilatometer modulus EDMT, in MPa.

    Returns
    -------
    dict
        Keys: rm, eoed_mpa.

    Raises
    ------
    ValueError
        If k_dmt <= 0.
    """
    if k_dmt <= 0:
        raise ValueError(f"k_dmt must be > 0, got {k_dmt}")

    if k_dmt > 10:
        rm = 0.32 + 2.18 * math.log10(k_dmt)
    elif i_dmt <= 0.6:
        rm = 0.14 + 2.36 * math.log10(k_dmt)
    elif i_dmt < 3.0:
        rm0 = 0.14 + 0.15 * (i_dmt - 0.6)
        rm = rm0 + (2.5 - rm0) * math.log10(k_dmt)
    else:
        rm = 0.5 + 2 * math.log10(k_dmt)

    rm = max(rm, 0.85)
    return {"rm": round(rm, 4), "eoed_mpa": round(rm * e_dmt_mpa, 4)}


# ============================================================================
# Annex K: plate loading test (PLT) derived values (printed p.139-140;
# Marsland 1972, Burland 1969, Bergdahl 1993)
# ============================================================================

def equation_k1_plt_undrained_shear_strength(pu_kpa: float, gamma_z_kpa: float,
                                              plate_condition: str = "surface") -> float:
    """Undrained shear strength from a plate loading test (Annex K.1).

    cu = (pu - gamma*z) / Nc

    Nc = 6 for a PLT on the subsoil surface; Nc = 9 for a PLT in a
    borehole at depth greater than 4 times the plate diameter/width.

    Parameters
    ----------
    pu_kpa : float
        Ultimate contact pressure from the PLT results, in kPa.
    gamma_z_kpa : float
        Total stress (unit weight times depth) at the test level, in kPa
        (only relevant/nonzero for boreholes with diameter smaller than
        3 times the plate diameter).
    plate_condition : str
        'surface' (Nc=6) or 'borehole_deep' (Nc=9, depth > 4x plate
        diameter/width).

    Returns
    -------
    float
        Undrained shear strength cu, in kPa.

    Raises
    ------
    ValueError
        If plate_condition is not recognized.
    """
    cond = plate_condition.strip().lower()
    if cond == "surface":
        nc = 6
    elif cond == "borehole_deep":
        nc = 9
    else:
        raise ValueError(
            f"Unknown plate_condition '{plate_condition}'. "
            f"Use surface or borehole_deep"
        )
    return (pu_kpa - gamma_z_kpa) / nc


def equation_k2_plt_modulus(delta_p_kpa: float, delta_s_mm: float, b_m: float,
                             poisson: float = 0.5, cz: float = 1.0) -> float:
    """Plate settlement modulus EpLT from a plate loading test (Annex K.2).

    Surface/excavation test (bottom width/diameter >= 5x plate diameter):
        EpLT = (delta_p / delta_s) * pi * b * (1 - v^2) / 4
    Borehole-base test:
        EpLT = (delta_p / delta_s) * pi * b * (1 - v^2) / 4 * Cz
        (Cz is a depth correction factor, Figure K.1; pass cz explicitly)

    Parameters
    ----------
    delta_p_kpa : float
        Selected range of applied contact pressure considered, in kPa.
    delta_s_mm : float
        Change in total settlement (including creep) for delta_p_kpa, in mm.
        Must be > 0.
    b_m : float
        Diameter of the plate, in m.
    poisson : float
        Poisson's ratio: 0.5 for undrained conditions in fine soil (default),
        0.3 for coarse soil, if not otherwise determined.
    cz : float
        Depth correction factor for borehole-base tests (Figure K.1);
        use 1.0 (default) for surface/excavation tests.

    Returns
    -------
    float
        Plate settlement modulus EpLT, in kPa*m/mm (i.e. delta_p units per
        delta_s-normalized geometry -- consistent units in, consistent
        units out; typically reported in MPa when delta_p is in kPa and
        delta_s/b share length units).

    Raises
    ------
    ValueError
        If delta_s_mm <= 0.
    """
    if delta_s_mm <= 0:
        raise ValueError(f"delta_s_mm must be > 0, got {delta_s_mm}")
    return (delta_p_kpa / delta_s_mm) * math.pi * b_m * (1 - poisson ** 2) / 4 * cz


def equation_k3_plt_subgrade_reaction(delta_p_kpa: float, delta_s_mm: float) -> float:
    """Coefficient of sub-grade reaction ks from a plate loading test (Annex K.3).

    ks = delta_p / delta_s

    Parameters
    ----------
    delta_p_kpa : float
        Selected range of applied contact pressure considered, in kPa.
    delta_s_mm : float
        Change in settlement (including creep) for delta_p_kpa, in mm.
        Must be > 0.

    Returns
    -------
    float
        Coefficient of sub-grade reaction ks, in kPa/mm.

    Raises
    ------
    ValueError
        If delta_s_mm <= 0.
    """
    if delta_s_mm <= 0:
        raise ValueError(f"delta_s_mm must be > 0, got {delta_s_mm}")
    return delta_p_kpa / delta_s_mm


# ============================================================================
# Annex N.3 / N.4: chemical-test unit-conversion equations (printed p.159)
# ============================================================================

def equation_n_caco3_from_co2(co2_pct: float) -> float:
    """Equivalent calcium carbonate content from CO2 content (Annex N.3.2).

    CaCO3 = 2.273 * CO2

    Parameters
    ----------
    co2_pct : float
        CO2 content, as a percentage of dry weight.  Must be >= 0.

    Returns
    -------
    float
        Equivalent CaCO3 content, as a percentage of dry weight.

    Raises
    ------
    ValueError
        If co2_pct < 0.
    """
    if co2_pct < 0:
        raise ValueError(f"co2_pct must be >= 0, got {co2_pct}")
    return 2.273 * co2_pct


def equation_n_so4_from_so3(so3_pct: float) -> float:
    """Sulfate (SO4) content from sulfur trioxide (SO3) content (Annex N.4.1).

    SO4(2-) = 1.2 * SO3

    Parameters
    ----------
    so3_pct : float
        SO3 content, as a percentage.  Must be >= 0.

    Returns
    -------
    float
        SO4(2-) content, as a percentage.

    Raises
    ------
    ValueError
        If so3_pct < 0.
    """
    if so3_pct < 0:
        raise ValueError(f"so3_pct must be >= 0, got {so3_pct}")
    return 1.2 * so3_pct
