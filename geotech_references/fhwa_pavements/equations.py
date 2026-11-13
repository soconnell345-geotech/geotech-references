"""FHWA-NHI-05-037 "Geotechnical Aspects of Pavements" design equations.

Numeric correlations and models for the geotech pavement inputs in
FHWA-NHI-05-037 (FHWA, May 2006): resilient modulus Mr from CBR, R-value,
plasticity/gradation, and the Dynamic Cone Penetrometer; the AASHTO 1993
stress-dependent (bulk-stress) granular Mr model; CBR from DCP; the seasonal
effective-Mr relative-damage relationship. Units follow the source (Mr in psi,
CBR/R in percent). Each function cites the source equation/table and page.

``pdf_page_index`` values are 0-based fitz page indices into
``docs/FHWA-NHI-05-037 - Geotech Pavements.pdf`` (add 1 for a PDF viewer);
``printed_page`` is the manual's own page number (e.g. "5-53").

The modulus of subgrade reaction from CBR (k = 1500 CBR / 19.4) was removed:
FHWA-NHI-05-037 does not print it (review finding gec-27). The AASHTO 1993
Guide prints k = MR/19.4 (p. II-44) for a slab directly on the roadbed;
``aashto_1993.equations.modulus_subgrade_reaction_simple`` holds it.
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
        "pdf_page_index": 230, "printed_page": "5-53",
        "note": "Preferred Mr-CBR correlation; NOT the older Mr=1500*CBR (Eq. 5.13).",
    }


def resilient_modulus_from_cbr_aashto93(cbr) -> dict:
    """Subgrade Mr from CBR, Heukelom & Klomp 1962 (Eq. 5.13, 1993 AASHTO Guide).

        Mr (psi) = 1500 * CBR     (for CBR <= 10, as printed on p. 5-49)

    The legacy 1993 AASHTO Guide subgrade correlation. NCHRP 1-37A strongly
    recommends AGAINST this form; prefer ``resilient_modulus_from_cbr``
    (Mr = 2555*CBR^0.64). Provided for back-checking older designs only.

    Parameters
    ----------
    cbr : float
        California Bearing Ratio (%), > 0. Eq. 5.13 is printed for CBR <= 10;
        a warning is added above 10.

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
        "equation": "Mr(psi) = 1500 * CBR  (CBR <= 10)",
        "reference": "FHWA-NHI-05-037 Eq. 5.13 (Heukelom & Klomp 1962 / 1993 AASHTO)",
        "pdf_page_index": 226, "printed_page": "5-49",
        "note": ("Legacy 1993 AASHTO subgrade form; NCHRP 1-37A recommends "
                 "AGAINST it. Prefer Mr = 2555*CBR^0.64."),
    }
    if cbr > 10:
        out["warning"] = "Eq. 5.13 is printed for CBR <= 10; result may be unreliable."
    return out


# ============================================================================
# Resilient modulus from R-value (Table 5-34 / Eq. 5.15)
# (Chapter 5; PDF p.230/226, printed 5-53/5-49)
# ============================================================================

def resilient_modulus_from_r_value(r_value, units: str = "psi") -> dict:
    """Resilient modulus Mr (psi, or MPa) from the Stabilometer R-value, NCHRP 1-37A correlation of FHWA-NHI-05-037 Table 5-34 (p. 5-53).

        Mr (psi) = 1155 + 555 * R   (Table 5-34)
        Mr (MPa) = 8.0  + 3.8  * R

    The Table 5-34 coefficients (1155, 555) are used. The 1993 AASHTO forms
    on p. 5-49 differ: Eq. 5.14, Mr (psi) = A + B (R-value) with A = 772 to
    1,155 and B = 369 to 555 (Asphalt Institute, 1982), and Eq. 5.15, Mr
    (psi) = 1000 + 555 (R-value), "recommended values" (155 psi lower than
    Table 5-34 at every R).

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
        "reference": "FHWA-NHI-05-037 Table 5-34 (NCHRP 1-37A, 2004)",
        "pdf_page_index": 230, "printed_page": "5-53",
        "note": ("Recommended subgrade form Eq. 5.15 is Mr(psi)=1000+555*R; the "
                 "general 1993 AASHTO form is Mr=A+B*R, A=772-1155, B=369-555."),
    }


# ============================================================================
# CBR from the Dynamic Cone Penetrometer, and Mr from DCP (Table 5-34)
# ============================================================================

_DCP_PRINT_NOTE = (
    "FHWA-NHI-05-037 Table 5-34 (p. 5-53) prints 'DCP = Penetration index, "
    "in./blow'; read in inches the relation gives CBR 635 % at 0.5 in./blow, "
    "against field CBRs of 3 to 80 in Table 5-28. The library takes DCP in mm "
    "per blow: TM 3-34.48-2 (29 February 2016) Figure G-11 (p. G-11) plots "
    "CBR = 292/PR^1.12 against 'DCP INDEX (mm/blow)', and its Table G-1 "
    "(p. G-12) gives CBR 22 at 10 mm/blow ('All other soils'); WES "
    "Instruction Report GL-92-3 (1992), p. 17: 'DCP is the penetration ratio "
    "in millimetres per blow'. Table 4-9 (p. 4-39) gives the relation after "
    "Webster et al. (1994) for gravel, sand, and silt, with no unit. A CBR "
    "over 100 % (DCP under 2.6 mm/blow) is refused. (Lead's ruling, "
    "2026-11-10.)")
_DCP_MIN_MM = (292.0 / 100.0) ** (1.0 / 1.12)   # CBR = 100 % here


def cbr_from_dcp(dcp_mm_per_blow) -> dict:
    """California Bearing Ratio CBR (%) from the Dynamic Cone Penetrometer index in mm per blow, FHWA-NHI-05-037 Table 5-34 (p. 5-53; ASTM D6951).

        CBR = 292 / DCP^1.12

    Table 5-34 prints DCP as the penetration index in in./blow; the library
    takes it in mm/blow (see ``print_note`` in the result: in inches the
    relation gives CBRs of hundreds of percent; TM 3-34.48-2 Figure G-11 and
    WES GL-92-3 give the relation in mm/blow). Table 4-9 (p. 4-39) gives it
    for gravel, sand, and silt. The CBR estimate is then used to estimate Mr
    (e.g. via ``resilient_modulus_from_cbr``).

    Parameters
    ----------
    dcp_mm_per_blow : float
        DCP penetration index (millimetres per blow), > 0. Below about
        2.6 mm/blow the relation passes CBR 100 % and the call is refused.

    Returns
    -------
    dict
        {'dcp_mm_per_blow', 'cbr', 'equation', 'print_note', 'reference', ...}

    Raises
    ------
    ValueError
        If dcp_mm_per_blow <= 0 or the CBR would exceed 100 %.
    """
    if dcp_mm_per_blow <= 0:
        raise ValueError(f"dcp_mm_per_blow must be > 0, got {dcp_mm_per_blow}")
    cbr = 292.0 / dcp_mm_per_blow ** 1.12
    if cbr > 100.0:
        raise ValueError(
            f"dcp_mm_per_blow = {dcp_mm_per_blow} gives CBR {cbr:.0f} %, over "
            f"100 % (DCP under {_DCP_MIN_MM:.2f} mm/blow). The DCP index is in "
            "mm per blow (TM 3-34.48-2 Figure G-11; WES GL-92-3 p. 17); a value "
            "in inches per blow is 25.4 times too small.")
    return {
        "dcp_mm_per_blow": dcp_mm_per_blow, "cbr": round(cbr, 1),
        "equation": "CBR = 292 / DCP^1.12  (DCP in mm/blow)",
        "print_note": _DCP_PRINT_NOTE,
        "reference": "FHWA-NHI-05-037 Table 5-34 (ASTM D6951)",
        "pdf_page_index": 230, "printed_page": "5-53",
        "note": "Feed the CBR into resilient_modulus_from_cbr to estimate Mr.",
    }


def resilient_modulus_from_dcp(dcp_mm_per_blow, units: str = "psi") -> dict:
    """Resilient modulus Mr (psi, or MPa) from the Dynamic Cone Penetrometer index in mm per blow, via CBR, FHWA-NHI-05-037 Table 5-34 (p. 5-53).

    Chains CBR = 292/DCP^1.12 (ASTM D6951; DCP in mm/blow, see
    ``cbr_from_dcp``) into the preferred Mr-CBR correlation
    Mr = 2555*CBR^0.64 (psi) / 17.6*CBR^0.64 (MPa).

    Parameters
    ----------
    dcp_mm_per_blow : float
        DCP penetration index (millimetres per blow), > 0; refused below
        about 2.6 mm/blow (CBR over 100 %).
    units : str, optional
        'psi' (default) or 'mpa'.

    Returns
    -------
    dict
        {'dcp_mm_per_blow', 'cbr', 'mr', 'units', 'print_note', 'reference', ...}

    Raises
    ------
    ValueError
        If dcp_mm_per_blow <= 0, the CBR would exceed 100 %, or units is
        invalid.
    """
    cbr_from_dcp(dcp_mm_per_blow)            # refuses DCP <= 0 and CBR > 100 %
    cbr = 292.0 / dcp_mm_per_blow ** 1.12    # unrounded; only the result is rounded
    mr = resilient_modulus_from_cbr(cbr, units=units)
    return {
        "dcp_mm_per_blow": dcp_mm_per_blow, "cbr": round(cbr, 1),
        "mr": mr["mr"], "units": mr["units"],
        "equation": "CBR=292/DCP^1.12 (DCP in mm/blow) -> Mr=2555*CBR^0.64 (psi)",
        "print_note": _DCP_PRINT_NOTE,
        "reference": "FHWA-NHI-05-037 Table 5-34 (ASTM D6951; NCHRP 1-37A)",
        "pdf_page_index": 230, "printed_page": "5-53",
    }


# ============================================================================
# CBR from plasticity index + gradation (Table 5-34)
# ============================================================================

_P200_PRINT_NOTE = (
    "FHWA-NHI-05-037 Table 5-34 (p. 5-53) prints wPI = P200*PI with 'P200 = "
    "% passing No. 200 sieve size'. The library takes the weighted "
    "plasticity index wPI as P200 times PI with P200 as a decimal fraction "
    "(lead's ruling, 2026-11-10). Read as a decimal, 35 % passing (0.35) at "
    "PI 10 gives wPI 3.5 and CBR 21.1; read as the percent (35), wPI 350 and "
    "CBR 0.29.")


def cbr_from_plasticity_gradation(p200, pi) -> dict:
    """California Bearing Ratio CBR (%) from the fraction passing the No. 200 sieve (a decimal) and the plasticity index (%), FHWA-NHI-05-037 Table 5-34 (p. 5-53).

        CBR = 75 / (1 + 0.728 * wPI),   wPI = P200 * PI

    Table 5-34 defines P200 as the "% passing No. 200 sieve size"; the
    library takes the weighted plasticity index wPI as P200 times PI with
    P200 as a decimal fraction (0.35 for 35 %), by the lead's ruling;
    ``print_note`` in the result gives one example of each reading. A value
    above 1 is refused. The resulting CBR is then used to estimate Mr.

    Parameters
    ----------
    p200 : float
        Fraction passing the No. 200 sieve, as a decimal, 0 to 1.
    pi : float
        Plasticity index (%), >= 0.

    Returns
    -------
    dict
        {'p200_decimal', 'pi_pct', 'wpi', 'cbr', 'equation', 'print_note',
         'reference', ...}

    Raises
    ------
    ValueError
        If p200 is outside 0 to 1 or pi < 0.
    """
    if not (0 <= p200 <= 1):
        hint = (f" For {p200} % passing, give {p200 / 100:g}."
                if 1 < p200 <= 100 else "")
        raise ValueError(
            f"p200 is the fraction passing the No. 200 sieve as a decimal, "
            f"0 to 1; got {p200}.{hint}")
    if pi < 0:
        raise ValueError(f"pi must be >= 0, got {pi}")
    wpi = p200 * pi
    cbr = 75.0 / (1.0 + 0.728 * wpi)
    return {
        "p200_decimal": p200, "pi_pct": pi, "wpi": round(wpi, 3),
        "cbr": round(cbr, 1),
        "equation": "CBR = 75 / (1 + 0.728*wPI), wPI = P200*PI (P200 a decimal)",
        "print_note": _P200_PRINT_NOTE,
        "reference": "FHWA-NHI-05-037 Table 5-34 (NCHRP 1-37A, 2004)",
        "pdf_page_index": 230, "printed_page": "5-53",
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
    and k1, k2 are material properties (Table 5-30, p. 5-46, gives typical
    ranges of k1 and k2 for Eq. 5.9; Table 5-39, p. 5-60, typical values for
    Eq. 5.17; Tables 5-41/5-43 give suggested theta values).

    Parameters
    ----------
    theta_psi : float
        Bulk stress theta = sigma1 + sigma2 + sigma3 (psi), > 0.
    k1 : float
        Material coefficient k1 (Mr units, psi). Typical ranges in Table 5-30
        (granular base 3000-8000, subbase 2500-7000).
    k2 : float
        Material exponent k2 (dimensionless). Typical ranges in Table 5-30
        (granular base 0.5-0.7, subbase 0.4-0.6).

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
        "pdf_page_index": 221, "printed_page": "5-44",
        "note": ("Typical k1/k2 ranges for Eq. 5.9: Table 5-30 (p. 5-46); "
                 "Table 5-39 (p. 5-60) for Eq. 5.17. Suggested theta: base "
                 "Table 5-41, subbase Table 5-43."),
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
        "pdf_page_index": 223, "printed_page": "5-46",
        "note": ("Average uf over the seasons, then Eq. 5.12 gives the "
                 "effective design Mr: Mr = 3015 * uf_avg^(-0.431) "
                 "(effective_subgrade_modulus_from_relative_damage)."),
    }


def effective_subgrade_modulus_from_relative_damage(uf_avg) -> dict:
    """Effective design subgrade resilient modulus Mr in psi from the average seasonal relative damage, FHWA-NHI-05-037 Eq. 5.12 (p. 5-46; 1993 AASHTO Guide).

        Mr (psi) = 3015 * uf^(-0.431)      (Eq. 5.12, as printed)

    Eq. 5.12 is printed as "the inverse of Eq. (5.11)", uf = 1.18e8 Mr^-2.32;
    its rounded coefficients differ from the exact inverse,
    (1.18e8 / uf)^(1/2.32), by under 0.1 %. The printed form is used.

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
    mr = 3015.0 * uf_avg ** (-0.431)
    return {
        "uf_avg": uf_avg, "mr_effective_psi": round(mr, 1),
        "equation": "Mr = 3015 * uf_avg^(-0.431)  (Eq. 5.12)",
        "reference": "FHWA-NHI-05-037 Eq. 5.12 (1993 AASHTO seasonal effective Mr)",
        "pdf_page_index": 223, "printed_page": "5-46",
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
    """Design resilient modulus Mr in psi from a backcalculated or field Mr, by the adjustment factor of the chosen basis, FHWA-NHI-05-037 Table 5-31 commentary (pp. 5-48 to 5-49).

    Backcalculated (or field-measured) resilient moduli must be reduced to design
    values. Table 5-31's commentary gives the factors: field subgrade Mr
    "multiplied by a factor of up to 0.33 for flexible pavements and up to
    0.25 for rigid pavements" (1993 AASHTO Guide); NCHRP 1-37A 0.40 for
    subgrade soils and 0.67 for granular bases and subbases under flexible
    pavements; more detailed guidance in Table 5-32. This applies the
    factor (C) for the chosen basis and layer:

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
        "reference": "FHWA-NHI-05-037 Table 5-31 commentary (see also Table 5-32)",
        "pdf_page_index": 225, "printed_page": "5-48 to 5-49",
        "note": note,
    }
