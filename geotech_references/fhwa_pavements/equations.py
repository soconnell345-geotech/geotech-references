"""FHWA-NHI-05-037 "Geotechnical Aspects of Pavements" design equations.

Numeric correlations and models for the geotech pavement inputs in
FHWA-NHI-05-037 (FHWA, May 2006): resilient modulus Mr from CBR, R-value,
plasticity/gradation, and the Dynamic Cone Penetrometer; the AASHTO 1993
stress-dependent (bulk-stress) granular Mr model; CBR from DCP; the seasonal
effective-Mr relative-damage relationship; and the modulus-of-subgrade-reaction
approximation. Units follow the source (Mr in psi, CBR/R in percent). Each
function cites the source equation/table and PDF page.
"""


# ============================================================================
# Resilient modulus from CBR (Table 5-34; the most preferred Mr correlation)
# (Chapter 5; PDF p.230, printed 5-53)
# ============================================================================

def resilient_modulus_from_cbr(cbr, units: str = "psi") -> dict:
    """Resilient modulus Mr from CBR (NCHRP 1-37A, Table 5-34).

        Mr (psi) = 2555 * CBR^0.64
        Mr (MPa) = 17.6 * CBR^0.64

    This is the NCHRP 1-37A recommended Mr-from-CBR correlation (the most
    preferred of the Table 5-34 correlations). NCHRP 1-37A strongly recommends
    AGAINST the older Heukelom & Klomp (1962) form Mr = 1500*CBR (Eq. 5.13) that
    appeared in the 1993 AASHTO Guide; see ``resilient_modulus_from_cbr_aashto93``.

    Parameters
    ----------
    cbr : float
        California Bearing Ratio (%), > 0.
    units : str, optional
        'psi' (default) or 'mpa' — which form/coefficient to use for the result.

    Returns
    -------
    dict
        {'cbr', 'mr', 'units', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If cbr <= 0 or units is invalid.
    """
    if cbr <= 0:
        raise ValueError(f"cbr must be > 0, got {cbr}")
    u = str(units).strip().lower()
    if u == "psi":
        mr = 2555.0 * cbr ** 0.64
    elif u in ("mpa", "si"):
        mr = 17.6 * cbr ** 0.64
        u = "mpa"
    else:
        raise ValueError(f"units must be 'psi' or 'mpa', got '{units}'.")
    return {
        "cbr": cbr, "mr": round(mr, 1), "units": u,
        "equation": "Mr(psi)=2555*CBR^0.64 (Mr(MPa)=17.6*CBR^0.64)",
        "reference": "FHWA-NHI-05-037 Table 5-34 (NCHRP 1-37A, 2004)",
        "pdf_page": 230, "printed_page": "5-53",
        "note": "Preferred Mr-CBR correlation; NOT the older Mr=1500*CBR (Eq. 5.13).",
    }


def resilient_modulus_from_cbr_aashto93(cbr) -> dict:
    """Subgrade Mr from CBR, Heukelom & Klomp 1962 (Eq. 5.13, 1993 AASHTO Guide).

        Mr (psi) = 1500 * CBR     (for CBR < 10)

    The legacy 1993 AASHTO Guide subgrade correlation. NCHRP 1-37A strongly
    recommends AGAINST this form; prefer ``resilient_modulus_from_cbr``
    (Mr = 2555*CBR^0.64). Provided for back-checking older designs only.

    Parameters
    ----------
    cbr : float
        California Bearing Ratio (%), > 0. The correlation is intended for
        CBR < 10 (fine-grained subgrade); a warning is added above 10.

    Returns
    -------
    dict
        {'cbr', 'mr_psi', 'equation', 'reference', 'warning'?, ...}

    Raises
    ------
    ValueError
        If cbr <= 0.
    """
    if cbr <= 0:
        raise ValueError(f"cbr must be > 0, got {cbr}")
    out = {
        "cbr": cbr, "mr_psi": round(1500.0 * cbr, 1),
        "equation": "Mr(psi) = 1500 * CBR  (CBR < 10)",
        "reference": "FHWA-NHI-05-037 Eq. 5.13 (Heukelom & Klomp 1962 / 1993 AASHTO)",
        "pdf_page": 226, "printed_page": "5-49",
        "note": ("Legacy 1993 AASHTO subgrade form; NCHRP 1-37A recommends "
                 "AGAINST it. Prefer Mr = 2555*CBR^0.64."),
    }
    if cbr >= 10:
        out["warning"] = "Eq. 5.13 is intended for CBR < 10; result may be unreliable."
    return out


# ============================================================================
# Resilient modulus from R-value (Table 5-34 / Eq. 5.15)
# (Chapter 5; PDF p.230/226, printed 5-53/5-49)
# ============================================================================

def resilient_modulus_from_r_value(r_value, units: str = "psi") -> dict:
    """Resilient modulus Mr from Stabilometer R-value (Table 5-34 / Eq. 5.15).

        Mr (psi) = 1155 + 555 * R   (Table 5-34)
        Mr (MPa) = 8.0  + 3.8  * R

    Equivalent to the recommended subgrade form Eq. 5.15, Mr(psi)=1000+555*R
    (the 1993 AASHTO general form Mr = A + B*R has A = 772-1155, B = 369-555,
    Asphalt Institute 1982). The Table 5-34 coefficients (1155, 555) are used
    here.

    Parameters
    ----------
    r_value : float
        Stabilometer R-value (AASHTO T190), 0-100.
    units : str, optional
        'psi' (default) or 'mpa'.

    Returns
    -------
    dict
        {'r_value', 'mr', 'units', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If r_value is out of 0-100 or units is invalid.
    """
    if not (0 <= r_value <= 100):
        raise ValueError(f"r_value must be in 0-100, got {r_value}")
    u = str(units).strip().lower()
    if u == "psi":
        mr = 1155.0 + 555.0 * r_value
    elif u in ("mpa", "si"):
        mr = 8.0 + 3.8 * r_value
        u = "mpa"
    else:
        raise ValueError(f"units must be 'psi' or 'mpa', got '{units}'.")
    return {
        "r_value": r_value, "mr": round(mr, 1), "units": u,
        "equation": "Mr(psi)=1155+555*R (Mr(MPa)=8.0+3.8*R)",
        "reference": "FHWA-NHI-05-037 Table 5-34 / Eq. 5.15 (Asphalt Institute 1982)",
        "pdf_page": 230, "printed_page": "5-53",
        "note": ("Recommended subgrade form Eq. 5.15 is Mr(psi)=1000+555*R; the "
                 "general 1993 AASHTO form is Mr=A+B*R, A=772-1155, B=369-555."),
    }


# ============================================================================
# CBR from the Dynamic Cone Penetrometer, and Mr from DCP (Table 5-34)
# ============================================================================

def cbr_from_dcp(dcp_index) -> dict:
    """CBR from the Dynamic Cone Penetrometer index (Table 5-34, ASTM D6951).

        CBR = 292 / DCP^1.12

    where DCP is the penetration index (in./blow). The CBR estimate is then used
    to estimate Mr (e.g. via ``resilient_modulus_from_cbr``).

    Parameters
    ----------
    dcp_index : float
        DCP penetration index (inches per blow), > 0.

    Returns
    -------
    dict
        {'dcp_index_in_per_blow', 'cbr', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If dcp_index <= 0.
    """
    if dcp_index <= 0:
        raise ValueError(f"dcp_index must be > 0, got {dcp_index}")
    cbr = 292.0 / dcp_index ** 1.12
    return {
        "dcp_index_in_per_blow": dcp_index, "cbr": round(cbr, 1),
        "equation": "CBR = 292 / DCP^1.12",
        "reference": "FHWA-NHI-05-037 Table 5-34 (ASTM D6951)",
        "pdf_page": 230, "printed_page": "5-53",
        "note": "Feed the CBR into resilient_modulus_from_cbr to estimate Mr.",
    }


def resilient_modulus_from_dcp(dcp_index, units: str = "psi") -> dict:
    """Resilient modulus Mr from the DCP index, via CBR (Table 5-34).

    Chains CBR = 292/DCP^1.12 (ASTM D6951) into the preferred Mr-CBR correlation
    Mr = 2555*CBR^0.64 (psi) / 17.6*CBR^0.64 (MPa).

    Parameters
    ----------
    dcp_index : float
        DCP penetration index (inches per blow), > 0.
    units : str, optional
        'psi' (default) or 'mpa'.

    Returns
    -------
    dict
        {'dcp_index_in_per_blow', 'cbr', 'mr', 'units', 'reference', ...}

    Raises
    ------
    ValueError
        If dcp_index <= 0 or units is invalid.
    """
    cbr = cbr_from_dcp(dcp_index)["cbr"]
    mr = resilient_modulus_from_cbr(cbr, units=units)
    return {
        "dcp_index_in_per_blow": dcp_index, "cbr": cbr,
        "mr": mr["mr"], "units": mr["units"],
        "equation": "CBR=292/DCP^1.12 -> Mr=2555*CBR^0.64 (psi)",
        "reference": "FHWA-NHI-05-037 Table 5-34 (ASTM D6951; NCHRP 1-37A)",
        "pdf_page": 230, "printed_page": "5-53",
    }


# ============================================================================
# CBR from plasticity index + gradation (Table 5-34)
# ============================================================================

def cbr_from_plasticity_gradation(p200, pi) -> dict:
    """CBR from plasticity index and gradation, wPI form (Table 5-34).

        CBR = 75 / (1 + 0.728 * wPI),   wPI = P200 * PI

    where P200 is the percent passing the No. 200 sieve (as a percentage value,
    e.g. 35 for 35%) expressed as a decimal fraction in wPI, and PI is the
    plasticity index (%). The resulting CBR is then used to estimate Mr.

    Parameters
    ----------
    p200 : float
        Percent passing the No. 200 sieve (%), 0-100.
    pi : float
        Plasticity index (%), >= 0.

    Returns
    -------
    dict
        {'p200_pct', 'pi_pct', 'wpi', 'cbr', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If p200 is out of 0-100 or pi < 0.
    """
    if not (0 <= p200 <= 100):
        raise ValueError(f"p200 must be in 0-100, got {p200}")
    if pi < 0:
        raise ValueError(f"pi must be >= 0, got {pi}")
    wpi = (p200 / 100.0) * pi
    cbr = 75.0 / (1.0 + 0.728 * wpi)
    return {
        "p200_pct": p200, "pi_pct": pi, "wpi": round(wpi, 3),
        "cbr": round(cbr, 1),
        "equation": "CBR = 75 / (1 + 0.728*wPI), wPI = (P200/100)*PI",
        "reference": "FHWA-NHI-05-037 Table 5-34 (NCHRP 1-37A, 2004)",
        "pdf_page": 230, "printed_page": "5-53",
        "note": "Feed the CBR into resilient_modulus_from_cbr to estimate Mr.",
    }


# ============================================================================
# AASHTO 1993 stress-dependent granular base/subbase Mr (Eq. 5.9)
# (Chapter 5; PDF p.221, printed 5-44)
# ============================================================================

def granular_resilient_modulus_bulk_stress(theta_psi, k1, k2) -> dict:
    """Stress-dependent (bulk-stress) resilient modulus for granular layers (Eq. 5.9).

        Mr = k1 * theta^k2

    The AASHTO 1993 (and NCHRP 1-37A) K-theta model for unbound granular base and
    subbase materials, where theta = bulk stress = sigma1 + sigma2 + sigma3 (psi)
    and k1, k2 are material properties (Table 5-39 gives typical k1, k2 for base
    and subbase; Table 5-41/5-43 give suggested theta values).

    Parameters
    ----------
    theta_psi : float
        Bulk stress theta = sigma1 + sigma2 + sigma3 (psi), > 0.
    k1 : float
        Material coefficient k1 (Mr units, psi). Typical ranges in Table 5-39.
    k2 : float
        Material exponent k2 (dimensionless). Typical ranges in Table 5-39.

    Returns
    -------
    dict
        {'theta_psi', 'k1', 'k2', 'mr_psi', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If theta_psi <= 0.
    """
    if theta_psi <= 0:
        raise ValueError(f"theta_psi must be > 0, got {theta_psi}")
    mr = k1 * theta_psi ** k2
    return {
        "theta_psi": theta_psi, "k1": k1, "k2": k2,
        "mr_psi": round(mr, 1),
        "equation": "Mr = k1 * theta^k2  (theta = sigma1+sigma2+sigma3, psi)",
        "reference": "FHWA-NHI-05-037 Eq. 5.9 (AASHTO 1993 / NCHRP 1-37A)",
        "pdf_page": 221, "printed_page": "5-44",
        "note": ("Typical k1/k2 for base & subbase: Table 5-39. Suggested theta: "
                 "base ~Table 5-41, subbase ~Table 5-43."),
    }


# ============================================================================
# Seasonal effective subgrade Mr — relative damage (Eq. 5.10 / 5.11)
# (Chapter 5; PDF p.223, printed 5-46)
# ============================================================================

def seasonal_relative_damage(mr_psi) -> dict:
    """Seasonal relative damage uf for an effective subgrade Mr (Eq. 5.11).

        uf = 1.18e8 * Mr^(-2.32)

    The 1993 AASHTO Guide accounts for seasonal subgrade-moisture variation by
    computing a relative damage uf for each seasonal Mr, averaging uf over the
    year, and back-solving this relationship for the single effective (design)
    resilient modulus. This returns uf for one seasonal Mr value.

    Parameters
    ----------
    mr_psi : float
        Seasonal subgrade resilient modulus (psi), > 0.

    Returns
    -------
    dict
        {'mr_psi', 'relative_damage_uf', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If mr_psi <= 0.
    """
    if mr_psi <= 0:
        raise ValueError(f"mr_psi must be > 0, got {mr_psi}")
    uf = 1.18e8 * mr_psi ** (-2.32)
    return {
        "mr_psi": mr_psi, "relative_damage_uf": round(uf, 4),
        "equation": "uf = 1.18e8 * Mr^(-2.32)",
        "reference": "FHWA-NHI-05-037 Eq. 5.11 (1993 AASHTO seasonal effective Mr)",
        "pdf_page": 223, "printed_page": "5-46",
        "note": ("Average uf over the seasons, then invert to the effective "
                 "design Mr: Mr_eff = (1.18e8 / uf_avg)^(1/2.32)."),
    }


def effective_subgrade_modulus_from_relative_damage(uf_avg) -> dict:
    """Effective design subgrade Mr from average relative damage (inverse of Eq. 5.11).

        Mr_eff (psi) = (1.18e8 / uf_avg)^(1/2.32)

    Inverts the seasonal relative-damage relationship: given the average relative
    damage uf over the analysis seasons, recover the single effective (design)
    subgrade resilient modulus (1993 AASHTO Guide).

    Parameters
    ----------
    uf_avg : float
        Average seasonal relative damage uf, > 0.

    Returns
    -------
    dict
        {'uf_avg', 'mr_effective_psi', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If uf_avg <= 0.
    """
    if uf_avg <= 0:
        raise ValueError(f"uf_avg must be > 0, got {uf_avg}")
    mr = (1.18e8 / uf_avg) ** (1.0 / 2.32)
    return {
        "uf_avg": uf_avg, "mr_effective_psi": round(mr, 1),
        "equation": "Mr_eff = (1.18e8 / uf_avg)^(1/2.32)",
        "reference": "FHWA-NHI-05-037 Eq. 5.11 (1993 AASHTO seasonal effective Mr)",
        "pdf_page": 223, "printed_page": "5-46",
    }


# ============================================================================
# Backcalculated -> design Mr adjustment (Table 5-32 / NCHRP 1-37A guidance)
# (Chapter 5; PDF p.226, printed 5-49)
# ============================================================================

# (basis, subgrade_factor, granular_base_factor, note)
_BACKCALC_FACTORS = {
    "aashto_1993_flexible": (
        0.33, None,
        "1993 AASHTO: multiply field/backcalculated subgrade Mr by UP TO 0.33 "
        "for flexible pavements to get design Mr."),
    "aashto_1993_rigid": (
        0.25, None,
        "1993 AASHTO: multiply field/backcalculated subgrade Mr by UP TO 0.25 "
        "for rigid pavements to get design Mr."),
    "nchrp_1_37a": (
        0.40, 0.67,
        "NCHRP 1-37A: subgrade factor 0.40; granular base/subbase factor 0.67 "
        "under flexible pavements."),
}


def backcalculated_to_design_modulus(mr_backcalculated_psi, basis: str,
                                     layer: str = "subgrade") -> dict:
    """Adjust a backcalculated/field Mr to a design Mr (Table 5-32 guidance).

    Backcalculated (or field-measured) resilient moduli must be reduced to design
    values. This applies the recommended adjustment factor (C) for the chosen
    basis and layer:

        Mr_design = C * Mr_backcalculated

    Parameters
    ----------
    mr_backcalculated_psi : float
        Backcalculated or field resilient modulus (psi), > 0.
    basis : str
        'aashto_1993_flexible', 'aashto_1993_rigid', or 'nchrp_1_37a'.
    layer : str, optional
        'subgrade' (default) or 'granular_base'/'granular' (NCHRP 1-37A only;
        factor 0.67).

    Returns
    -------
    dict
        {'mr_backcalculated_psi', 'factor', 'mr_design_psi', 'basis', 'layer',
         'reference', ...}

    Raises
    ------
    ValueError
        If inputs are invalid or the layer/basis combination has no factor.
    """
    if mr_backcalculated_psi <= 0:
        raise ValueError(
            f"mr_backcalculated_psi must be > 0, got {mr_backcalculated_psi}")
    b = str(basis).strip().lower()
    if b not in _BACKCALC_FACTORS:
        raise ValueError(
            f"Unknown basis '{basis}'. Use 'aashto_1993_flexible', "
            "'aashto_1993_rigid', or 'nchrp_1_37a'."
        )
    sub_f, gran_f, note = _BACKCALC_FACTORS[b]
    lk = str(layer).strip().lower()
    if lk in ("subgrade", "sub", ""):
        factor = sub_f
        layer_out = "subgrade"
    elif lk in ("granular_base", "granular", "base", "subbase"):
        if gran_f is None:
            raise ValueError(
                f"basis '{basis}' has no granular-layer factor; use "
                "'nchrp_1_37a' for granular base/subbase (0.67)."
            )
        factor = gran_f
        layer_out = "granular_base"
    else:
        raise ValueError(
            f"Unknown layer '{layer}'. Use 'subgrade' or 'granular_base'."
        )
    return {
        "mr_backcalculated_psi": mr_backcalculated_psi,
        "factor": factor,
        "mr_design_psi": round(factor * mr_backcalculated_psi, 1),
        "basis": b, "layer": layer_out,
        "equation": "Mr_design = C * Mr_backcalculated",
        "reference": "FHWA-NHI-05-037 Table 5-32 / NCHRP 1-37A (Ch 5)",
        "pdf_page": 226, "printed_page": "5-49",
        "note": note,
    }


# ============================================================================
# Modulus of subgrade reaction k from CBR (carried in the broader FHWA context)
# ============================================================================

def modulus_subgrade_reaction_from_cbr(cbr) -> dict:
    """Approximate modulus of subgrade reaction k from CBR.

        k (psi/in, pci) ~ 1500 * CBR / 19.4   (i.e. k ~ 77.3 * CBR)

    A commonly used approximation relating the modulus of subgrade reaction k
    (pci) to CBR via the elastic modulus (Mr ~ 1500*CBR for fine-grained
    subgrade, then k ~ Mr/19.4). It is approximate; for design, k is normally
    obtained from a plate-load test or the AASHTO/NCHRP k-from-Mr procedure.

    Parameters
    ----------
    cbr : float
        California Bearing Ratio (%), > 0.

    Returns
    -------
    dict
        {'cbr', 'k_pci', 'equation', 'reference', ...}

    Raises
    ------
    ValueError
        If cbr <= 0.
    """
    if cbr <= 0:
        raise ValueError(f"cbr must be > 0, got {cbr}")
    k = 1500.0 * cbr / 19.4
    return {
        "cbr": cbr, "k_pci": round(k, 1),
        "equation": "k (pci) ~ 1500*CBR / 19.4  (via Mr ~ 1500*CBR)",
        "reference": "FHWA-NHI-05-037 Ch 5 (approximate; k from Mr/19.4)",
        "pdf_page": 226, "printed_page": "5-49",
        "note": ("Approximate screening value only; obtain k from a plate-load "
                 "test or the AASHTO/NCHRP k-from-Mr procedure for design."),
    }
