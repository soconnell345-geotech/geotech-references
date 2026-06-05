"""FEMA P-2082 (2020 NEHRP Provisions) table lookups.

Geotech-relevant seismic-site tables from FEMA P-2082-1, Part 1 (Provisions):

- Site classification (Table 20.2-1, Sections 20.2.1-20.2.5) — REVISED in the
  2020 NEHRP relative to ASCE 7-16: eight velocity-based classes A, B, BC, C,
  CD, D, DE, E (plus F), with the intermediate classes BC, CD, DE added and the
  Vs (Vs30) ranges re-defined. The reference site condition is now Site Class BC.
- Seismic Design Category (Tables 11.6-1 and 11.6-2), keyed on SDS and SD1
  respectively and the Risk Category.

All shear-wave-velocity boundaries are quoted exactly from Table 20.2-1 in
ft/s (the table's native unit), with m/s shown for SI convenience using the
table's stated conversion 1 ft/s = 0.3048 m/s.

Source: FEMA P-2082-1 (2020), PDF pages 123-124 (printed pages 86-87) for
Chapter 20; PDF pages 55-56 (printed pages 18-19) for Chapter 11 Section 11.6.
"""

# ============================================================================
# Table 20.2-1: Site Classification  (Ch 20, Section 20.2; PDF p.123, printed 86)
#
# Site class from the average shear wave velocity v_s (Vs30) over the upper
# 100 ft (30 m). Ranges are quoted EXACTLY as printed in ft/s; m/s values are
# the table's SI conversion (x 0.3048). The order is stiffest (A) -> softest (E),
# with F assigned separately (Section 20.2.1, site response analysis required).
#
# Boundary convention (from the printed table):
#   A:  vs > 5,000 ft/s
#   B:  3,000 < vs <= 5,000 ft/s
#   BC: 2,100 < vs <= 3,000 ft/s
#   C:  1,450 < vs <= 2,100 ft/s
#   CD: 1,000 < vs <= 1,450 ft/s
#   D:    700 < vs <= 1,000 ft/s
#   DE:   500 < vs <=   700 ft/s
#   E:  vs < 500 ft/s
# ============================================================================

_FT_TO_M = 0.3048

# (site_class, lower_bound_ft_s_exclusive, upper_bound_ft_s_inclusive, description)
# Lower bound None => no lower bound (E); upper bound None => no upper bound (A).
_TABLE_20_2_1 = [
    ("A", 5000.0, None, "Hard rock"),
    ("B", 3000.0, 5000.0, "Medium hard rock"),
    ("BC", 2100.0, 3000.0, "Soft rock"),
    ("C", 1450.0, 2100.0, "Very dense sand or hard clay"),
    ("CD", 1000.0, 1450.0, "Dense sand or very stiff clay"),
    ("D", 700.0, 1000.0, "Medium dense sand or stiff clay"),
    ("DE", 500.0, 700.0, "Loose sand or medium stiff clay"),
    ("E", None, 500.0, "Very loose sand or soft clay"),
]


def site_class_table() -> dict:
    """Return the full FEMA P-2082 Table 20.2-1 site classification.

    The 2020 NEHRP Provisions (P-2082) revised the ASCE 7-16 site classes by
    adding the intermediate classes BC, CD, and DE and re-defining the
    shear-wave-velocity ranges. Site Class BC is the new reference (baseline)
    site condition for the mapped SS / S1 parameters.

    Returns
    -------
    dict
        {'reference': str, 'table': '20.2-1', 'pdf_page': 123,
         'printed_page': 86, 'depth_ft': 100, 'depth_m': 30.0,
         'classes': [ {site_class, description, vs_min_ft_s, vs_max_ft_s,
                       vs_min_m_s, vs_max_m_s, boundary} ... ]}
    """
    classes = []
    for sc, lo, hi, desc in _TABLE_20_2_1:
        if hi is None:
            boundary = f"vs > {lo:,.0f} ft/s"
        elif lo is None:
            boundary = f"vs < {hi:,.0f} ft/s"
        else:
            boundary = f"{lo:,.0f} < vs <= {hi:,.0f} ft/s"
        classes.append({
            "site_class": sc,
            "description": desc,
            "vs_min_ft_s": lo,
            "vs_max_ft_s": hi,
            "vs_min_m_s": round(lo * _FT_TO_M, 1) if lo is not None else None,
            "vs_max_m_s": round(hi * _FT_TO_M, 1) if hi is not None else None,
            "boundary": boundary,
        })
    return {
        "reference": "FEMA P-2082 (2020 NEHRP) Table 20.2-1",
        "table": "20.2-1",
        "pdf_page": 123,
        "printed_page": 86,
        "depth_ft": 100,
        "depth_m": 30.0,
        "classes": classes,
        "note": (
            "Site Class F (Section 20.2.1) is assigned separately for soils "
            "requiring site response analysis (liquefiable, quick/sensitive "
            "clays, collapsible soils, thick peat/organic, very high PI clays, "
            "or thick soft/medium-stiff clays). Site Class BC is the reference "
            "(baseline) site condition for mapped SS/S1."
        ),
    }


def site_class_from_vs30(vs30, unit: str = "m/s") -> dict:
    """Determine the FEMA P-2082 Site Class from the average shear wave velocity.

    Implements Table 20.2-1 of the 2020 NEHRP Provisions (P-2082), the REVISED
    site-classification scheme that adds the intermediate classes BC, CD, DE.
    The velocity is the average over the upper 100 ft (30 m), i.e. Vs30.

    This returns the velocity-based class only. It does NOT apply the Site
    Class E soft-clay override (Section 20.2.2) or the Site Class F triggers
    (Section 20.2.1, e.g. liquefaction), which require additional soil data;
    those are reported via :func:`site_class_f_triggers` and noted in the result.

    Parameters
    ----------
    vs30 : float
        Average shear wave velocity over the upper 100 ft (30 m).
    unit : str, optional
        Unit of ``vs30``: 'm/s' (default) or 'ft/s'.

    Returns
    -------
    dict
        {'vs30': float, 'unit': str, 'vs30_ft_s': float, 'site_class': str,
         'description': str, 'boundary': str, 'reference': str, 'note': str}

    Raises
    ------
    ValueError
        If vs30 is not positive or unit is unrecognized.
    """
    if vs30 <= 0:
        raise ValueError(f"vs30 must be > 0, got {vs30}")

    u = unit.lower().strip().replace(" ", "")
    if u in ("m/s", "mps", "m"):
        vs_ft = vs30 / _FT_TO_M
    elif u in ("ft/s", "fps", "ft", "feet/s"):
        vs_ft = float(vs30)
    else:
        raise ValueError(f"Unknown unit '{unit}'. Use 'm/s' or 'ft/s'.")

    matched = None
    for sc, lo, hi, desc in _TABLE_20_2_1:
        lo_ok = (lo is None) or (vs_ft > lo)
        hi_ok = (hi is None) or (vs_ft <= hi)
        if lo_ok and hi_ok:
            matched = (sc, lo, hi, desc)
            break
    if matched is None:  # pragma: no cover — table spans all positive vs
        raise ValueError(f"Could not classify vs30={vs30} {unit}")

    sc, lo, hi, desc = matched
    if hi is None:
        boundary = f"vs > {lo:,.0f} ft/s"
    elif lo is None:
        boundary = f"vs < {hi:,.0f} ft/s"
    else:
        boundary = f"{lo:,.0f} < vs <= {hi:,.0f} ft/s"

    return {
        "vs30": vs30,
        "unit": unit,
        "vs30_ft_s": round(vs_ft, 1),
        "site_class": sc,
        "description": desc,
        "boundary": boundary,
        "reference": "FEMA P-2082 (2020 NEHRP) Table 20.2-1 (Section 20.2)",
        "note": (
            "Velocity-based class only. Check Section 20.2.1 (Site Class F) and "
            "20.2.2 (Site Class E soft clay) overrides with additional soil data. "
            "Site Classes A and B require on-site measured Vs; an estimated "
            "rock site defaults to BC (Section 20.2.4)."
        ),
    }


# ============================================================================
# Section 20.2.1 / 20.2.2: Site Class F and Site Class E overrides
# (Ch 20; PDF p.124, printed 87)
# ============================================================================

_SITE_CLASS_F_TRIGGERS = [
    {
        "trigger": "vulnerable_soils",
        "description": (
            "Soils vulnerable to potential failure or collapse under seismic "
            "loading: liquefiable soils, quick and highly sensitive clays, "
            "collapsible weakly cemented soils."
        ),
        "exception": (
            "For structures with fundamental period T <= 0.5 s, site response "
            "analysis is not required to determine spectral accelerations for "
            "liquefiable soils; a site class per Section 20.2 is permitted."
        ),
    },
    {
        "trigger": "peat_organic",
        "description": (
            "Peats and/or highly organic clays with thickness H > 10 ft (3 m)."
        ),
        "exception": None,
    },
    {
        "trigger": "very_high_plasticity_clay",
        "description": (
            "Very high plasticity clays with H > 25 ft (7.6 m) and PI > 75, in "
            "a profile that would otherwise be Site Class CD, D, DE or E."
        ),
        "exception": (
            "Not required for SDC A or B (where SDC is based on SDS and SD1)."
        ),
    },
    {
        "trigger": "thick_soft_medium_clay",
        "description": (
            "Soft/medium stiff clays with H > 120 ft (37 m) and "
            "su < 1,000 psf (50 kPa)."
        ),
        "exception": "Not required for SDC A or B.",
    },
]


def site_class_f_triggers() -> dict:
    """Return the Site Class F triggering conditions (Section 20.2.1).

    A site meeting ANY of these conditions is Site Class F and requires a site
    response analysis per Section 21.1 (subject to the listed exceptions).

    Returns
    -------
    dict
        {'reference': str, 'pdf_page': 124, 'printed_page': 87,
         'triggers': [ {trigger, description, exception} ... ],
         'site_class_e_soft_clay': {...}}
    """
    return {
        "reference": "FEMA P-2082 (2020 NEHRP) Section 20.2.1 (Site Class F)",
        "pdf_page": 124,
        "printed_page": 87,
        "triggers": [dict(t) for t in _SITE_CLASS_F_TRIGGERS],
        "site_class_e_soft_clay": {
            "rule": (
                "Section 20.2.2: A site not qualifying as F with total soft-clay "
                "thickness > 10 ft (3 m) — soft clay defined by su < 500 psf "
                "(25 kPa), w >= 40%, and PI > 20 — is classified Site Class E "
                "regardless of the computed vs."
            ),
        },
    }


# ============================================================================
# Table 11.6-1: Seismic Design Category from SDS  (Ch 11; PDF p.56, printed 19)
# Table 11.6-2: Seismic Design Category from SD1   (Ch 11; PDF p.56, printed 19)
#
# SDC is the MORE SEVERE of the two table results. Separately, Risk Category
# I/II/III with S1 >= 0.75 -> SDC E; Risk Category IV with S1 >= 0.75 -> SDC F.
# Risk Categories I, II, III share one column; Risk Category IV is the other.
# ============================================================================

# Table 11.6-1: (upper_bound_SDS_exclusive, SDC for I/II/III, SDC for IV)
_TABLE_11_6_1 = [
    (0.167, "A", "A"),   # SDS < 0.167
    (0.33, "B", "C"),    # 0.167 <= SDS < 0.33
    (0.50, "C", "D"),    # 0.33  <= SDS < 0.50
    (None, "D", "D"),    # SDS >= 0.50
]

# Table 11.6-2: (upper_bound_SD1_exclusive, SDC for I/II/III, SDC for IV)
_TABLE_11_6_2 = [
    (0.067, "A", "A"),   # SD1 < 0.067
    (0.133, "B", "C"),   # 0.067 <= SD1 < 0.133
    (0.20, "C", "D"),    # 0.133 <= SD1 < 0.20
    (None, "D", "D"),    # SD1 >= 0.20
]

_SDC_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5}


def _risk_col(risk_category) -> int:
    """Return 0 for Risk Category I/II/III, 1 for Risk Category IV."""
    rc = str(risk_category).upper().strip().replace("RISK CATEGORY", "").strip()
    _map = {"I": 0, "II": 0, "III": 0, "IV": 1,
            "1": 0, "2": 0, "3": 0, "4": 1}
    if rc not in _map:
        raise ValueError(
            f"Unknown risk_category '{risk_category}'. "
            "Use 'I', 'II', 'III', or 'IV'."
        )
    return _map[rc]


def sdc_from_sds(sds, risk_category: str = "II") -> dict:
    """Seismic Design Category from SDS (Table 11.6-1).

    Parameters
    ----------
    sds : float
        Design spectral response acceleration at short periods, SDS.
    risk_category : str, optional
        Risk Category 'I', 'II', 'III', or 'IV'. Default 'II'.
        (I, II, and III share one column.)

    Returns
    -------
    dict
        {'sds': float, 'risk_category': str, 'sdc': str, 'reference': str}

    Raises
    ------
    ValueError
        If sds is negative or risk_category is unrecognized.
    """
    if sds < 0:
        raise ValueError(f"sds must be >= 0, got {sds}")
    col = _risk_col(risk_category)
    sdc = None
    for hi, sdc_a, sdc_iv in _TABLE_11_6_1:
        if hi is None or sds < hi:
            sdc = sdc_a if col == 0 else sdc_iv
            break
    return {
        "sds": sds,
        "risk_category": str(risk_category).upper().strip(),
        "sdc": sdc,
        "reference": "FEMA P-2082 (2020 NEHRP) Table 11.6-1",
        "note": (
            "Final SDC is the MORE SEVERE of Table 11.6-1 (this) and 11.6-2; "
            "use seismic_design_category() to combine, including the S1 >= 0.75 "
            "rule (SDC E for RC I/II/III; SDC F for RC IV)."
        ),
    }


def sdc_from_sd1(sd1, risk_category: str = "II") -> dict:
    """Seismic Design Category from SD1 (Table 11.6-2).

    Parameters
    ----------
    sd1 : float
        Design spectral response acceleration at a 1-s period, SD1.
    risk_category : str, optional
        Risk Category 'I', 'II', 'III', or 'IV'. Default 'II'.

    Returns
    -------
    dict
        {'sd1': float, 'risk_category': str, 'sdc': str, 'reference': str}

    Raises
    ------
    ValueError
        If sd1 is negative or risk_category is unrecognized.
    """
    if sd1 < 0:
        raise ValueError(f"sd1 must be >= 0, got {sd1}")
    col = _risk_col(risk_category)
    sdc = None
    for hi, sdc_a, sdc_iv in _TABLE_11_6_2:
        if hi is None or sd1 < hi:
            sdc = sdc_a if col == 0 else sdc_iv
            break
    return {
        "sd1": sd1,
        "risk_category": str(risk_category).upper().strip(),
        "sdc": sdc,
        "reference": "FEMA P-2082 (2020 NEHRP) Table 11.6-2",
        "note": (
            "Final SDC is the MORE SEVERE of Table 11.6-1 and 11.6-2 (this); "
            "use seismic_design_category() to combine, including the S1 >= 0.75 "
            "rule (SDC E for RC I/II/III; SDC F for RC IV)."
        ),
    }


def seismic_design_category(sds, sd1, risk_category: str = "II",
                            s1: float = 0.0) -> dict:
    """Combined Seismic Design Category per Section 11.6 (P-2082).

    Applies BOTH Table 11.6-1 (from SDS) and Table 11.6-2 (from SD1), taking the
    more severe category, AND the S1 >= 0.75 override:
      - Risk Category I, II, or III with S1 >= 0.75  -> SDC E
      - Risk Category IV with S1 >= 0.75             -> SDC F

    Parameters
    ----------
    sds : float
        Design spectral acceleration at short periods, SDS.
    sd1 : float
        Design spectral acceleration at a 1-s period, SD1.
    risk_category : str, optional
        Risk Category 'I', 'II', 'III', or 'IV'. Default 'II'.
    s1 : float, optional
        Mapped MCER spectral response acceleration at 1 s (Site Class BC).
        Default 0.0. If >= 0.75 the override applies.

    Returns
    -------
    dict
        {'sds': float, 'sd1': float, 's1': float, 'risk_category': str,
         'sdc_from_sds': str, 'sdc_from_sd1': str, 'sdc': str,
         'governed_by': str, 'reference': str}

    Raises
    ------
    ValueError
        If inputs are invalid.
    """
    a = sdc_from_sds(sds, risk_category)["sdc"]
    b = sdc_from_sd1(sd1, risk_category)["sdc"]
    # More severe of the two tables.
    if _SDC_ORDER[a] >= _SDC_ORDER[b]:
        sdc, governed = a, "Table 11.6-1 (SDS)"
    else:
        sdc, governed = b, "Table 11.6-2 (SD1)"

    col = _risk_col(risk_category)
    override = None
    if s1 >= 0.75:
        override = "F" if col == 1 else "E"
        if _SDC_ORDER[override] >= _SDC_ORDER[sdc]:
            sdc = override
            governed = "Section 11.6 S1 >= 0.75 rule"

    return {
        "sds": sds,
        "sd1": sd1,
        "s1": s1,
        "risk_category": str(risk_category).upper().strip(),
        "sdc_from_sds": a,
        "sdc_from_sd1": b,
        "s1_override_sdc": override,
        "sdc": sdc,
        "governed_by": governed,
        "reference": "FEMA P-2082 (2020 NEHRP) Section 11.6, Tables 11.6-1 and 11.6-2",
    }


# ============================================================================
# Risk Category / Importance Factor (Section 11.5; ASCE 7 Tables 1.5-1/1.5-2)
# Importance Factors Ie referenced via Table 1.5-2 (unchanged by P-2082).
# ============================================================================

_IMPORTANCE_FACTOR = {
    "I": 1.0,
    "II": 1.0,
    "III": 1.25,
    "IV": 1.5,
}


def importance_factor(risk_category: str) -> dict:
    """Seismic Importance Factor Ie from the Risk Category (Section 11.5.1).

    P-2082 assigns Ie via Table 1.5-2 (Risk Category I=1.0, II=1.0, III=1.25,
    IV=1.5 — unchanged from ASCE 7). Returned for convenience alongside the SDC
    lookups.

    Parameters
    ----------
    risk_category : str
        Risk Category 'I', 'II', 'III', or 'IV'.

    Returns
    -------
    dict
        {'risk_category': str, 'importance_factor_ie': float, 'reference': str}

    Raises
    ------
    ValueError
        If risk_category is unrecognized.
    """
    rc = str(risk_category).upper().strip().replace("RISK CATEGORY", "").strip()
    if rc not in _IMPORTANCE_FACTOR:
        raise ValueError(
            f"Unknown risk_category '{risk_category}'. Use 'I', 'II', 'III', 'IV'."
        )
    return {
        "risk_category": rc,
        "importance_factor_ie": _IMPORTANCE_FACTOR[rc],
        "reference": "FEMA P-2082 (2020 NEHRP) Section 11.5.1 / ASCE 7 Table 1.5-2",
    }
