"""GEC-13 figure lookup functions.

Digitized figures from FHWA-NHI-16-027 (GEC-13), Ground Modification
Methods Reference Manual. GEC-13 is primarily a guidance/reference manual;
most computation-oriented charts are in the ground_improvement module.
The figures here capture empirical relationships from the manual.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Figure 4-3: Vibro-Compaction — Suitability by Grain Size
# Soil suitability number SN (Brown 1977)
# SN = 1.7 * sqrt(3/D50^2 + 1/D20^2 + 1/D10^2)
# ============================================================================

def figure_4_3_suitability_number(d50_mm: float, d20_mm: float,
                                   d10_mm: float) -> dict:
    """Soil suitability number for vibro-compaction (Brown 1977).

    SN = 1.7 * sqrt(3/D50^2 + 1/D20^2 + 1/D10^2)

    Rating:
        SN 0-10:  Excellent
        SN 10-20: Good
        SN 20-30: Fair
        SN 30-50: Poor (may not be suitable)
        SN > 50:  Not suitable

    Parameters
    ----------
    d50_mm : float
        Median grain size D50 in mm.
    d20_mm : float
        Grain size D20 in mm (20% finer).
    d10_mm : float
        Effective grain size D10 in mm (10% finer).

    Returns
    -------
    dict
        suitability_number, rating, d50_mm, d20_mm, d10_mm.

    Raises
    ------
    ValueError
        If any grain size is <= 0 or sizes are not in order.
    """
    if d10_mm <= 0 or d20_mm <= 0 or d50_mm <= 0:
        raise ValueError("All grain sizes must be > 0")
    if not (d10_mm <= d20_mm <= d50_mm):
        raise ValueError("Grain sizes must satisfy D10 <= D20 <= D50")

    sn = 1.7 * (3.0 / d50_mm**2 + 1.0 / d20_mm**2 + 1.0 / d10_mm**2) ** 0.5

    if sn <= 10:
        rating = "Excellent"
    elif sn <= 20:
        rating = "Good"
    elif sn <= 30:
        rating = "Fair"
    elif sn <= 50:
        rating = "Poor"
    else:
        rating = "Not suitable"

    return {
        "suitability_number": round(sn, 1),
        "rating": rating,
        "d50_mm": d50_mm,
        "d20_mm": d20_mm,
        "d10_mm": d10_mm,
        "description": "Brown (1977) soil suitability number for vibro-compaction",
    }


# ============================================================================
# Figure 5-2: Area Replacement Ratio for Aggregate Columns
# as = (pi/4 * d^2) / A_tributary
# A_tributary depends on pattern: triangular or square
# ============================================================================

def figure_5_2_area_replacement_ratio(column_diameter_m: float,
                                       spacing_m: float,
                                       pattern: str = "triangular") -> dict:
    """Area replacement ratio for aggregate columns (GEC-13 Figure 5-2).

    as = Ac / At where Ac = pi/4 * d^2, and At depends on pattern:
      - Triangular: At = 0.866 * s^2
      - Square: At = s^2

    Parameters
    ----------
    column_diameter_m : float
        Column diameter in meters.
    spacing_m : float
        Center-to-center column spacing in meters.
    pattern : str
        'triangular' or 'square'.

    Returns
    -------
    dict
        area_replacement_ratio, column_area_m2, tributary_area_m2,
        column_diameter_m, spacing_m, pattern.

    Raises
    ------
    ValueError
        If diameter or spacing invalid, or pattern unknown.
    """
    import math

    if column_diameter_m <= 0:
        raise ValueError("column_diameter_m must be > 0")
    if spacing_m <= 0:
        raise ValueError("spacing_m must be > 0")
    if spacing_m <= column_diameter_m:
        raise ValueError("spacing_m must exceed column_diameter_m")

    pat = pattern.lower().strip()
    ac = math.pi / 4.0 * column_diameter_m**2

    if pat == "triangular":
        at = 0.866 * spacing_m**2
    elif pat == "square":
        at = spacing_m**2
    else:
        raise ValueError(f"Unknown pattern '{pattern}'. Use 'triangular' or 'square'")

    a_s = ac / at

    return {
        "area_replacement_ratio": round(a_s, 4),
        "column_area_m2": round(ac, 4),
        "tributary_area_m2": round(at, 4),
        "column_diameter_m": column_diameter_m,
        "spacing_m": spacing_m,
        "pattern": pat,
        "description": "Area replacement ratio for aggregate column design",
    }


# ============================================================================
# Figure 5-5: Settlement Improvement Factor for Stone Columns
# n = stress concentration ratio (typically 2-5)
# SRF = 1 / (1 + as*(n-1))
# ============================================================================

def figure_5_5_settlement_improvement(area_replacement_ratio: float,
                                       stress_concentration_ratio: float = 3.0) -> dict:
    """Settlement improvement factor for stone columns (GEC-13 Figure 5-5).

    Settlement Reduction Factor (SRF) = 1 / (1 + as*(n-1))
    Settlement Improvement Factor = 1 / SRF = 1 + as*(n-1)

    Parameters
    ----------
    area_replacement_ratio : float
        Area replacement ratio as (typically 0.10 to 0.35).
    stress_concentration_ratio : float
        Stress concentration ratio n (typically 2 to 5, default 3.0).

    Returns
    -------
    dict
        settlement_reduction_factor, settlement_improvement_factor,
        area_replacement_ratio, stress_concentration_ratio.

    Raises
    ------
    ValueError
        If inputs are out of valid range.
    """
    if area_replacement_ratio <= 0 or area_replacement_ratio >= 1:
        raise ValueError("area_replacement_ratio must be between 0 and 1")
    if stress_concentration_ratio < 1:
        raise ValueError("stress_concentration_ratio must be >= 1")

    srf = 1.0 / (1.0 + area_replacement_ratio * (stress_concentration_ratio - 1.0))
    sif = 1.0 / srf

    return {
        "settlement_reduction_factor": round(srf, 4),
        "settlement_improvement_factor": round(sif, 2),
        "area_replacement_ratio": area_replacement_ratio,
        "stress_concentration_ratio": stress_concentration_ratio,
        "description": "Priebe (1995) settlement improvement for stone columns",
    }


# ============================================================================
# Equation 7-4: Deep Mixing Composite Modulus
# E_comp = a_s * E_col + (1 - a_s) * E_soil
# ============================================================================

def equation_7_4_composite_modulus(e_col_kpa: float,
                                    e_soil_kpa: float,
                                    area_replacement_ratio: float) -> dict:
    """Composite modulus of a deep mixed treatment zone (GEC-13 Eq 7-4).

    E_comp = a_s * E_col + (1 - a_s) * E_soil

    Typical column modulus: E_col = 50–200 * qu (E in kPa, qu in kPa).

    Parameters
    ----------
    e_col_kpa : float
        Elastic modulus of the DM column in kPa.
    e_soil_kpa : float
        Elastic modulus of the untreated soil in kPa.
    area_replacement_ratio : float
        Area replacement ratio a_s = column area / tributary area (0–1).

    Returns
    -------
    dict
        e_comp_kpa, e_col_kpa, e_soil_kpa, area_replacement_ratio,
        stress_concentration_ratio.

    Raises
    ------
    ValueError
        If moduli are non-positive or area ratio is out of range.
    """
    if e_col_kpa <= 0:
        raise ValueError("e_col_kpa must be > 0")
    if e_soil_kpa <= 0:
        raise ValueError("e_soil_kpa must be > 0")
    if not (0 < area_replacement_ratio < 1):
        raise ValueError("area_replacement_ratio must be between 0 and 1")

    a_s = area_replacement_ratio
    e_comp = a_s * e_col_kpa + (1.0 - a_s) * e_soil_kpa
    n = e_col_kpa / e_soil_kpa

    return {
        "e_comp_kpa": round(e_comp, 1),
        "e_col_kpa": e_col_kpa,
        "e_soil_kpa": e_soil_kpa,
        "area_replacement_ratio": a_s,
        "stress_concentration_ratio": round(n, 2),
        "description": "Composite modulus of deep mixed treatment zone (parallel model)",
    }


# ============================================================================
# Equation 8-1: Groutability Ratio for Permeation Grouting
# N = D15_soil / D85_grout
# ============================================================================

def equation_8_1_groutability_ratio(d15_soil_mm: float,
                                     d85_grout_mm: float) -> dict:
    """Groutability ratio for particulate permeation grouting (GEC-13 Eq 8-1).

    N = D15_soil / D85_grout

    Interpretation:
      N > 25:   Grouting feasible
      11–25:    Grouting uncertain
      N < 11:   Grouting not feasible

    Parameters
    ----------
    d15_soil_mm : float
        D15 grain size of the soil to be grouted in mm.
    d85_grout_mm : float
        D85 particle size of the particulate grout in mm.

    Returns
    -------
    dict
        groutability_ratio, feasibility, d15_soil_mm, d85_grout_mm.

    Raises
    ------
    ValueError
        If either input is non-positive.
    """
    if d15_soil_mm <= 0:
        raise ValueError("d15_soil_mm must be > 0")
    if d85_grout_mm <= 0:
        raise ValueError("d85_grout_mm must be > 0")

    n = d15_soil_mm / d85_grout_mm

    if n > 25:
        feasibility = "Feasible"
    elif n >= 11:
        feasibility = "Uncertain"
    else:
        feasibility = "Not feasible"

    return {
        "groutability_ratio": round(n, 2),
        "feasibility": feasibility,
        "d15_soil_mm": d15_soil_mm,
        "d85_grout_mm": d85_grout_mm,
        "description": "Groutability ratio N = D15_soil / D85_grout for particulate permeation grouting",
    }


# ============================================================================
# Equation 11-1: Long-Term Design Strength (LTDS) for Geosynthetics
# LTDS = T_ult / (RF_ID * RF_CR * RF_CBD * FS)
# ============================================================================

def equation_11_1_ltds(t_ult_kn_m: float,
                        rf_id: float,
                        rf_cr: float,
                        rf_cbd: float,
                        fs: float = 1.0) -> dict:
    """Long-term design strength for geosynthetic reinforcement (GEC-13 Eq 11-1).

    LTDS = T_ult / (RF_ID * RF_CR * RF_CBD * FS)

    Use table_11_1_geosynthetic_reduction_factors() for RF values by polymer.

    Parameters
    ----------
    t_ult_kn_m : float
        Ultimate tensile strength from index test (kN/m).
    rf_id : float
        Installation damage reduction factor (typically 1.05–3.0).
    rf_cr : float
        Creep reduction factor (typically 1.5–5.0 by polymer type).
    rf_cbd : float
        Chemical and biological degradation factor (typically 1.05–1.6).
    fs : float
        Overall factor of safety (default 1.0; AASHTO LRFD typically uses
        FS=1.0 with RF terms covering all uncertainty).

    Returns
    -------
    dict
        ltds_kn_m, combined_reduction_factor, t_ult_kn_m,
        rf_id, rf_cr, rf_cbd, fs.

    Raises
    ------
    ValueError
        If any input is non-positive.
    """
    for name, val in [("t_ult_kn_m", t_ult_kn_m), ("rf_id", rf_id),
                      ("rf_cr", rf_cr), ("rf_cbd", rf_cbd), ("fs", fs)]:
        if val <= 0:
            raise ValueError(f"{name} must be > 0")

    combined_rf = rf_id * rf_cr * rf_cbd * fs
    ltds = t_ult_kn_m / combined_rf

    return {
        "ltds_kn_m": round(ltds, 2),
        "combined_reduction_factor": round(combined_rf, 3),
        "t_ult_kn_m": t_ult_kn_m,
        "rf_id": rf_id,
        "rf_cr": rf_cr,
        "rf_cbd": rf_cbd,
        "fs": fs,
        "description": "Long-term design strength (LTDS) for geosynthetic reinforcement",
    }
