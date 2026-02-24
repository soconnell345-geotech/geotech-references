"""FEMA P-2192 table lookup functions.

Digitized tables from FEMA P-2192 (2024), ASCE 7-22, and referenced AASHTO
provisions for Seismic Design Category determination. Follows the DM7 pattern:
private data with ``_TABLE_*`` prefix, public lookup functions.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 11.6-1: SDC Based on Short-Period Response Acceleration SDS
# ASCE 7-22 Table 11.6-1
# ============================================================================

_TABLE_11_6_1 = [
    # (sds_upper, sdc_i_ii_iii, sdc_iv)
    (0.167, "A", "A"),
    (0.33, "B", "C"),
    (0.50, "C", "D"),
]
# SDS >= 0.50 → D for all


def table_11_6_1_sdc_short_period(sds: float, risk_category: str) -> str:
    """Seismic Design Category from short-period SDS (ASCE 7-22 Table 11.6-1).

    Parameters
    ----------
    sds : float
        Design spectral acceleration at short periods (dimensionless, g).
    risk_category : str
        Risk category: 'I', 'II', 'III', or 'IV'.

    Returns
    -------
    str
        Seismic Design Category letter: 'A', 'B', 'C', or 'D'.

    Raises
    ------
    ValueError
        If sds is negative or risk_category is invalid.
    """
    if sds < 0:
        raise ValueError(f"sds must be non-negative, got {sds}")

    rc = risk_category.strip().upper()
    if rc not in ("I", "II", "III", "IV"):
        raise ValueError(
            f"Invalid risk_category '{risk_category}'. Options: I, II, III, IV"
        )

    col = 2 if rc == "IV" else 1

    for upper, sdc_low, sdc_iv in _TABLE_11_6_1:
        if sds < upper:
            return sdc_iv if col == 2 else sdc_low

    # SDS >= 0.50
    return "D"


# ============================================================================
# Table 11.6-2: SDC Based on 1-Second Response Acceleration SD1
# ASCE 7-22 Table 11.6-2
# ============================================================================

_TABLE_11_6_2 = [
    # (sd1_upper, sdc_i_ii_iii, sdc_iv)
    (0.067, "A", "A"),
    (0.133, "B", "C"),
    (0.20, "C", "D"),
]
# SD1 >= 0.20 → D for all


def table_11_6_2_sdc_one_second(sd1: float, risk_category: str) -> str:
    """Seismic Design Category from 1-second SD1 (ASCE 7-22 Table 11.6-2).

    Parameters
    ----------
    sd1 : float
        Design spectral acceleration at 1-second period (dimensionless, g).
    risk_category : str
        Risk category: 'I', 'II', 'III', or 'IV'.

    Returns
    -------
    str
        Seismic Design Category letter: 'A', 'B', 'C', or 'D'.

    Raises
    ------
    ValueError
        If sd1 is negative or risk_category is invalid.
    """
    if sd1 < 0:
        raise ValueError(f"sd1 must be non-negative, got {sd1}")

    rc = risk_category.strip().upper()
    if rc not in ("I", "II", "III", "IV"):
        raise ValueError(
            f"Invalid risk_category '{risk_category}'. Options: I, II, III, IV"
        )

    col = 2 if rc == "IV" else 1

    for upper, sdc_low, sdc_iv in _TABLE_11_6_2:
        if sd1 < upper:
            return sdc_iv if col == 2 else sdc_low

    # SD1 >= 0.20
    return "D"


# ============================================================================
# SDC Determination Algorithm (ASCE 7-22 Section 11.6)
# ============================================================================

_SDC_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5}


def determine_sdc(sds: float, sd1: float, risk_category: str,
                  s1: float = None) -> dict:
    """Full Seismic Design Category determination (ASCE 7-22 Section 11.6).

    Algorithm:
      1. Look up SDC from SDS (Table 11.6-1)
      2. Look up SDC from SD1 (Table 11.6-2)
      3. Take the more severe (higher letter)
      4. Override: if S1 >= 0.75, SDC = E (Risk Cat I/II/III) or F (Risk Cat IV)

    Parameters
    ----------
    sds : float
        Design spectral acceleration at short periods (g).
    sd1 : float
        Design spectral acceleration at 1-second period (g).
    risk_category : str
        Risk category: 'I', 'II', 'III', or 'IV'.
    s1 : float, optional
        Mapped MCER spectral acceleration at 1-second period (g).
        Required to check the S1 >= 0.75 override to SDC E or F.

    Returns
    -------
    dict
        Keys: sdc (str), sdc_from_sds (str), sdc_from_sd1 (str),
        governing_parameter (str), s1_override (bool),
        risk_category (str), sds (float), sd1 (float).

    Raises
    ------
    ValueError
        If inputs are negative or risk_category is invalid.
    """
    sdc_sds = table_11_6_1_sdc_short_period(sds, risk_category)
    sdc_sd1 = table_11_6_2_sdc_one_second(sd1, risk_category)

    # More severe governs
    if _SDC_ORDER[sdc_sds] >= _SDC_ORDER[sdc_sd1]:
        sdc = sdc_sds
        governing = "SDS"
    else:
        sdc = sdc_sd1
        governing = "SD1"

    # S1 >= 0.75 override (ASCE 7-22 Section 11.6)
    s1_override = False
    if s1 is not None:
        if s1 < 0:
            raise ValueError(f"s1 must be non-negative, got {s1}")
        if s1 >= 0.75:
            rc = risk_category.strip().upper()
            override_sdc = "F" if rc == "IV" else "E"
            if _SDC_ORDER.get(override_sdc, 0) > _SDC_ORDER[sdc]:
                sdc = override_sdc
                governing = "S1_override"
                s1_override = True

    return {
        "sdc": sdc,
        "sdc_from_sds": sdc_sds,
        "sdc_from_sd1": sdc_sd1,
        "governing_parameter": governing,
        "s1_override": s1_override,
        "risk_category": risk_category.strip().upper(),
        "sds": sds,
        "sd1": sd1,
    }


# ============================================================================
# Table 20.3-1: Site Classification (ASCE 7-22 Expanded 9-Class System)
# Vs30 boundaries in m/s
# ============================================================================

# ASCE 7-22 expanded 9-class site classification by Vs30
_TABLE_20_3_1_VS30_9CLASS = [
    # (vs30_lower, vs30_upper, site_class, description)
    (1524, None, "A", "Hard rock"),
    (762, 1524, "B", "Medium hard rock"),
    (487, 762, "BC", "Soft rock"),
    (366, 487, "C", "Very dense soil or hard rock"),
    (244, 366, "CD", "Dense soil or soft rock"),
    (183, 244, "D", "Stiff soil"),
    (122, 183, "DE", "Stiff to soft soil"),
    (0, 122, "E", "Soft soil"),
]

# ASCE 7-16 legacy 5-class site classification by Vs30
_TABLE_20_3_1_VS30_5CLASS = [
    (1524, None, "A", "Hard rock"),
    (762, 1524, "B", "Rock"),
    (366, 762, "C", "Very dense soil and soft rock"),
    (183, 366, "D", "Stiff soil"),
    (0, 183, "E", "Soft clay soil"),
]


def table_20_3_1_site_class_from_vs30(vs30_m_per_s: float,
                                      system: str = "asce7_22") -> dict:
    """Site classification from average shear wave velocity (ASCE 7-22 Table 20.3-1).

    Parameters
    ----------
    vs30_m_per_s : float
        Average shear wave velocity in the upper 30 m (m/s).
    system : str
        Classification system: 'asce7_22' for expanded 9-class (default)
        or 'asce7_16' for legacy 5-class.

    Returns
    -------
    dict
        Keys: site_class, description, vs30_m_per_s, system.

    Raises
    ------
    ValueError
        If vs30 is not positive or system is invalid.
    """
    if vs30_m_per_s <= 0:
        raise ValueError(f"vs30 must be positive, got {vs30_m_per_s}")

    sys_key = system.lower().strip().replace("-", "").replace("_", "")
    if sys_key in ("asce722", "9class", "expanded"):
        table = _TABLE_20_3_1_VS30_9CLASS
        sys_label = "asce7_22"
    elif sys_key in ("asce716", "5class", "legacy"):
        table = _TABLE_20_3_1_VS30_5CLASS
        sys_label = "asce7_16"
    else:
        raise ValueError(
            f"Unknown system '{system}'. Options: 'asce7_22', 'asce7_16'"
        )

    for lower, upper, sc, desc in table:
        if upper is None:
            if vs30_m_per_s >= lower:
                return {
                    "site_class": sc,
                    "description": desc,
                    "vs30_m_per_s": vs30_m_per_s,
                    "system": sys_label,
                }
        else:
            if lower <= vs30_m_per_s < upper:
                return {
                    "site_class": sc,
                    "description": desc,
                    "vs30_m_per_s": vs30_m_per_s,
                    "system": sys_label,
                }

    # Should not reach here given positive input
    return {  # pragma: no cover
        "site_class": "E",
        "description": "Soft soil",
        "vs30_m_per_s": vs30_m_per_s,
        "system": sys_label,
    }


# ============================================================================
# Table 20.3-1: Site Classification from SPT N-value
# N-bar = weighted average over soil layers in top 30 m
# ============================================================================

# ASCE 7-22 approximate SPT boundaries for 9-class system
# Note: ASCE 7-22 defines intermediate classes primarily by Vs30.
# These SPT boundaries are approximate for when Vs30 is unavailable.
_TABLE_20_3_1_SPT_9CLASS = [
    # (n_lower, n_upper, site_class, description)
    (100, None, "BC", "Soft rock (very high blow count)"),
    (50, 100, "C", "Very dense soil"),
    (30, 50, "CD", "Dense soil"),
    (15, 30, "D", "Stiff soil"),
    (8, 15, "DE", "Stiff to soft soil"),
    (0, 8, "E", "Soft soil"),
]

_TABLE_20_3_1_SPT_5CLASS = [
    (50, None, "C", "Very dense soil and soft rock"),
    (15, 50, "D", "Stiff soil"),
    (0, 15, "E", "Soft clay soil"),
]


def table_20_3_1_site_class_from_spt(n_avg: float,
                                     system: str = "asce7_22") -> dict:
    """Site classification from average SPT blow count (ASCE 7-22 Table 20.3-1).

    Uses the weighted average standard penetration resistance over the top
    30 m of soil. Site Classes A and B (rock) cannot be determined from
    SPT alone and require Vs30 measurement.

    Parameters
    ----------
    n_avg : float
        Average SPT N-value (blows/300mm) over the top 30 m of soil.
    system : str
        Classification system: 'asce7_22' for expanded 9-class (default)
        or 'asce7_16' for legacy 5-class.

    Returns
    -------
    dict
        Keys: site_class, description, n_avg, system, note (str).

    Raises
    ------
    ValueError
        If n_avg is negative or system is invalid.
    """
    if n_avg < 0:
        raise ValueError(f"n_avg must be non-negative, got {n_avg}")

    sys_key = system.lower().strip().replace("-", "").replace("_", "")
    if sys_key in ("asce722", "9class", "expanded"):
        table = _TABLE_20_3_1_SPT_9CLASS
        sys_label = "asce7_22"
    elif sys_key in ("asce716", "5class", "legacy"):
        table = _TABLE_20_3_1_SPT_5CLASS
        sys_label = "asce7_16"
    else:
        raise ValueError(
            f"Unknown system '{system}'. Options: 'asce7_22', 'asce7_16'"
        )

    note = "Site Classes A and B require Vs30 measurement."

    for lower, upper, sc, desc in table:
        if upper is None:
            if n_avg >= lower:
                return {
                    "site_class": sc,
                    "description": desc,
                    "n_avg": n_avg,
                    "system": sys_label,
                    "note": note,
                }
        else:
            if lower <= n_avg < upper:
                return {
                    "site_class": sc,
                    "description": desc,
                    "n_avg": n_avg,
                    "system": sys_label,
                    "note": note,
                }

    # n_avg == 0
    row = table[-1]
    return {
        "site_class": row[2],
        "description": row[3],
        "n_avg": n_avg,
        "system": sys_label,
        "note": note,
    }


# ============================================================================
# Table 20.3-1: Site Classification from Undrained Shear Strength
# Su in kPa, weighted average over soil layers in top 30 m
# ============================================================================

_TABLE_20_3_1_SU_9CLASS = [
    # (su_lower_kPa, su_upper_kPa, site_class, description)
    (192, None, "BC", "Soft rock (very high strength)"),
    (100, 192, "C", "Very dense soil"),
    (72, 100, "CD", "Dense soil"),
    (48, 72, "D", "Stiff soil"),
    (24, 48, "DE", "Stiff to soft soil"),
    (0, 24, "E", "Soft soil"),
]

_TABLE_20_3_1_SU_5CLASS = [
    (100, None, "C", "Very dense soil and soft rock"),
    (50, 100, "D", "Stiff soil"),
    (0, 50, "E", "Soft clay soil"),
]


def table_20_3_1_site_class_from_su(su_kpa: float,
                                    system: str = "asce7_22") -> dict:
    """Site classification from average undrained shear strength (ASCE 7-22 Table 20.3-1).

    Uses the weighted average undrained shear strength over the top 30 m.
    Site Classes A and B (rock) cannot be determined from Su alone.

    Parameters
    ----------
    su_kpa : float
        Average undrained shear strength (kPa) over the top 30 m.
    system : str
        Classification system: 'asce7_22' for expanded 9-class (default)
        or 'asce7_16' for legacy 5-class.

    Returns
    -------
    dict
        Keys: site_class, description, su_kPa, system, note (str).

    Raises
    ------
    ValueError
        If su_kpa is not positive or system is invalid.
    """
    if su_kpa <= 0:
        raise ValueError(f"su_kpa must be positive, got {su_kpa}")

    sys_key = system.lower().strip().replace("-", "").replace("_", "")
    if sys_key in ("asce722", "9class", "expanded"):
        table = _TABLE_20_3_1_SU_9CLASS
        sys_label = "asce7_22"
    elif sys_key in ("asce716", "5class", "legacy"):
        table = _TABLE_20_3_1_SU_5CLASS
        sys_label = "asce7_16"
    else:
        raise ValueError(
            f"Unknown system '{system}'. Options: 'asce7_22', 'asce7_16'"
        )

    note = "Site Classes A and B require Vs30 measurement."

    for lower, upper, sc, desc in table:
        if upper is None:
            if su_kpa >= lower:
                return {
                    "site_class": sc,
                    "description": desc,
                    "su_kPa": su_kpa,
                    "system": sys_label,
                    "note": note,
                }
        else:
            if lower <= su_kpa < upper:
                return {
                    "site_class": sc,
                    "description": desc,
                    "su_kPa": su_kpa,
                    "system": sys_label,
                    "note": note,
                }

    # su_kpa very small but positive
    row = table[-1]
    return {
        "site_class": row[2],
        "description": row[3],
        "su_kPa": su_kpa,
        "system": sys_label,
        "note": note,
    }


# ============================================================================
# Risk Category from Occupancy (ASCE 7-22 Table 1.5-1)
# ============================================================================

_TABLE_RISK_CATEGORY = {
    "agricultural": {
        "risk_category": "I",
        "description": "Agricultural facilities, minor storage",
    },
    "minor_storage": {
        "risk_category": "I",
        "description": "Minor storage facilities",
    },
    "standard": {
        "risk_category": "II",
        "description": "Standard occupancy (residential, commercial, industrial)",
    },
    "residential": {
        "risk_category": "II",
        "description": "Residential buildings",
    },
    "commercial": {
        "risk_category": "II",
        "description": "Commercial buildings",
    },
    "industrial": {
        "risk_category": "II",
        "description": "Industrial buildings",
    },
    "office": {
        "risk_category": "II",
        "description": "Office buildings",
    },
    "assembly": {
        "risk_category": "III",
        "description": "Assembly occupancy >300 persons",
    },
    "school": {
        "risk_category": "III",
        "description": "Schools and educational facilities",
    },
    "jail": {
        "risk_category": "III",
        "description": "Jails and detention facilities",
    },
    "power_station": {
        "risk_category": "III",
        "description": "Power generating stations",
    },
    "water_treatment": {
        "risk_category": "III",
        "description": "Water treatment facilities",
    },
    "hospital": {
        "risk_category": "IV",
        "description": "Hospitals and healthcare facilities",
    },
    "fire_station": {
        "risk_category": "IV",
        "description": "Fire stations",
    },
    "police_station": {
        "risk_category": "IV",
        "description": "Police stations",
    },
    "emergency": {
        "risk_category": "IV",
        "description": "Emergency response facilities",
    },
    "essential": {
        "risk_category": "IV",
        "description": "Essential facilities",
    },
}


def risk_category_from_occupancy(occupancy: str) -> dict:
    """Risk category from building occupancy (ASCE 7-22 Table 1.5-1).

    Parameters
    ----------
    occupancy : str
        Building occupancy type. Examples: 'residential', 'commercial',
        'school', 'hospital', 'essential', 'agricultural'.

    Returns
    -------
    dict
        Keys: risk_category (str I-IV), occupancy (str), description (str).

    Raises
    ------
    ValueError
        If occupancy is not recognized.
    """
    key = occupancy.lower().strip().replace(" ", "_")

    if key in _TABLE_RISK_CATEGORY:
        entry = _TABLE_RISK_CATEGORY[key]
        return {
            "risk_category": entry["risk_category"],
            "occupancy": key,
            "description": entry["description"],
        }

    # Partial match
    for k, v in _TABLE_RISK_CATEGORY.items():
        if key in k or k in key:
            return {
                "risk_category": v["risk_category"],
                "occupancy": k,
                "description": v["description"],
            }

    raise ValueError(
        f"Unknown occupancy '{occupancy}'. Options: "
        f"{', '.join(_TABLE_RISK_CATEGORY.keys())}"
    )


# ============================================================================
# Table 11.4-1: Short-Period Site Coefficient Fa (ASCE 7-22)
# Columns: Ss = 0.25, 0.50, 0.75, 1.00, 1.25, 1.50
# Rows: Site Classes A through E (F always requires site-specific)
# ============================================================================

_TABLE_11_4_1_SS = [0.25, 0.50, 0.75, 1.00, 1.25, 1.50]

_TABLE_11_4_1_FA = {
    "A":  [0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    "B":  [0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
    "BC": [1.3, 1.2, 1.1, 1.0, 1.0, 1.0],
    "C":  [1.4, 1.3, 1.2, 1.2, 1.2, 1.2],
    "CD": [1.6, 1.4, 1.2, 1.1, 1.0, 1.0],
    "D":  [1.8, 1.6, 1.4, 1.2, 1.1, 1.1],
    "DE": [2.4, 1.9, 1.5, 1.3, 1.2, 1.1],
    "E":  [2.5, 1.7, 1.3, 1.3, 1.3, 1.3],
}


def site_coefficient_fa(site_class: str, ss: float) -> float:
    """Short-period site coefficient Fa (ASCE 7-22 Table 11.4-1).

    Parameters
    ----------
    site_class : str
        Site class: 'A', 'B', 'BC', 'C', 'CD', 'D', 'DE', or 'E'.
        Site Class F requires site-specific analysis.
    ss : float
        Mapped MCER spectral acceleration at short periods (g).
        Clamped to range [0.25, 1.50] for interpolation.

    Returns
    -------
    float
        Short-period site coefficient Fa.

    Raises
    ------
    ValueError
        If site_class is not recognized or is 'F'.
    """
    key = site_class.upper().strip()

    if key == "F":
        raise ValueError(
            "Site Class F requires site-specific ground motion analysis. "
            "Fa cannot be determined from Table 11.4-1."
        )

    if key not in _TABLE_11_4_1_FA:
        raise ValueError(
            f"Unknown site_class '{site_class}'. "
            f"Options: {', '.join(_TABLE_11_4_1_FA.keys())}"
        )

    ss_clamped = max(0.25, min(1.50, ss))
    return _linterp(ss_clamped, _TABLE_11_4_1_SS, _TABLE_11_4_1_FA[key])


# ============================================================================
# Table 11.4-2: Long-Period Site Coefficient Fv (ASCE 7-22)
# Columns: S1 = 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60
# Site Classes DE and E require site-specific analysis per ASCE 7-22.
# ============================================================================

_TABLE_11_4_2_S1 = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60]

_TABLE_11_4_2_FV = {
    "A":  [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    "B":  [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
    "BC": [1.5, 1.5, 1.5, 1.5, 1.4, 1.3, 1.2, 1.1],
    "C":  [1.5, 1.5, 1.5, 1.5, 1.5, 1.4, 1.3, 1.2],
    "CD": [2.4, 2.2, 2.0, 1.9, 1.8, 1.6, 1.5, 1.4],
    "D":  [4.0, 3.5, 3.0, 2.8, 2.6, 2.4, 2.2, 2.0],
}


def site_coefficient_fv(site_class: str, s1: float) -> float:
    """Long-period site coefficient Fv (ASCE 7-22 Table 11.4-2).

    Note: ASCE 7-22 requires site-specific ground motion analysis for
    Site Classes DE, E, and F. These classes are not in the Fv table.

    Parameters
    ----------
    site_class : str
        Site class: 'A', 'B', 'BC', 'C', 'CD', or 'D'.
        Site Classes DE, E, and F require site-specific analysis.
    s1 : float
        Mapped MCER spectral acceleration at 1-second period (g).
        Clamped to range [0.10, 0.60] for interpolation.

    Returns
    -------
    float
        Long-period site coefficient Fv.

    Raises
    ------
    ValueError
        If site_class is not recognized or requires site-specific analysis.
    """
    key = site_class.upper().strip()

    if key in ("DE", "E", "F"):
        raise ValueError(
            f"Site Class {key} requires site-specific ground motion analysis "
            f"per ASCE 7-22 Section 11.4.8. Fv cannot be determined from "
            f"Table 11.4-2."
        )

    if key not in _TABLE_11_4_2_FV:
        raise ValueError(
            f"Unknown site_class '{site_class}'. "
            f"Options: {', '.join(_TABLE_11_4_2_FV.keys())} "
            f"(DE, E, F require site-specific analysis)"
        )

    s1_clamped = max(0.10, min(0.60, s1))
    return _linterp(s1_clamped, _TABLE_11_4_2_S1, _TABLE_11_4_2_FV[key])


# ============================================================================
# Design Spectral Parameters SDS and SD1 (ASCE 7-22 Section 11.4.5)
# ============================================================================

def design_spectral_parameters(ss: float, s1: float,
                               site_class: str) -> dict:
    """Compute design spectral acceleration parameters SDS and SD1.

    SDS = (2/3) * Fa * Ss
    SD1 = (2/3) * Fv * S1

    Parameters
    ----------
    ss : float
        Mapped MCER spectral acceleration at short periods (g).
    s1 : float
        Mapped MCER spectral acceleration at 1-second period (g).
    site_class : str
        Site class for Fa/Fv lookup.

    Returns
    -------
    dict
        Keys: sds (float), sd1 (float), fa (float), fv (float),
        ss (float), s1 (float), site_class (str).
        sd1 and fv will be None if site class requires site-specific Fv.

    Raises
    ------
    ValueError
        If ss or s1 is negative or site_class is invalid.
    """
    if ss < 0:
        raise ValueError(f"ss must be non-negative, got {ss}")
    if s1 < 0:
        raise ValueError(f"s1 must be non-negative, got {s1}")

    key = site_class.upper().strip()

    fa = site_coefficient_fa(key, ss)
    sds = (2.0 / 3.0) * fa * ss

    # Fv may not be available for DE, E, F
    try:
        fv = site_coefficient_fv(key, s1)
        sd1 = (2.0 / 3.0) * fv * s1
    except ValueError:
        fv = None
        sd1 = None

    return {
        "sds": round(sds, 4),
        "sd1": round(sd1, 4) if sd1 is not None else None,
        "fa": round(fa, 4),
        "fv": round(fv, 4) if fv is not None else None,
        "ss": ss,
        "s1": s1,
        "site_class": key,
    }
