"""GEC-13 figure lookup functions.

Digitized figures from FHWA-NHI-16-027 (GEC-13), Ground Modification
Methods Reference Manual. GEC-13 is primarily a guidance/reference manual;
most computation-oriented charts are in the ground_improvement module.
The figures here capture empirical relationships from the manual.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Eq. 4-3: Vibro-compaction backfill suitability number (Brown 1977), p. 4-73
# SN = 1.7 * sqrt(3/D50^2 + 1/D20^2 + 1/D10^2), D in mm
# The function keeps its old name (figure_4_3_...) because callers use it;
# GEC-13 Figure 4-3 is "SPT liquefaction chart", not this relation.
# ============================================================================

def figure_4_3_suitability_number(d50_mm: float, d20_mm: float,
                                   d10_mm: float) -> dict:
    """Backfill suitability number for vibro-compaction (GEC-13 Eq. 4-3, p. 4-73).

    GEC-13 (FHWA-NHI-16-027) Vol I, Ch. 4, Section 3.2.2 "Materials",
    Eq. 4-3 (Brown 1977), printed p. 4-73:

        Suitability No. = 1.7 * sqrt(3/(D50)^2 + 1/(D20)^2 + 1/(D10)^2)

    where D50, D20 and D10 are the grain sizes, in millimeters, at 50, 20
    and 10 percent passing. It rates the BACKFILL fed to the vibrator, not
    the in situ soil. This is not GEC-13 Figure 4-3 (the SPT liquefaction
    chart); the function keeps its name because callers use it.

    Rating, as printed in GEC-13 Table 4-7 "Backfill Evaluation Criteria",
    p. 4-73 (Brown 1977):
        SN 0-10:  Excellent
        SN 10-20: Good
        SN 20-30: Fair
        SN 30-40: Poor
        SN > 50:  Unsuitable
    Table 4-7 prints no row for 40 to 50, so for 40 < SN <= 50 the rating
    is None and the result carries a ``note`` saying the table gives none.

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
        suitability_number, rating (None for 40 < SN <= 50), d50_mm,
        d20_mm, d10_mm, description; ``note`` when the rating is None.

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

    # Table 4-7 (p. 4-73) bands, in its own words; it has no 40 to 50 row.
    note = None
    if sn <= 10:
        rating = "Excellent"
    elif sn <= 20:
        rating = "Good"
    elif sn <= 30:
        rating = "Fair"
    elif sn <= 40:
        rating = "Poor"
    elif sn <= 50:
        rating = None
        note = ("No rating: GEC-13 Table 4-7 (p. 4-73) prints no band for a "
                "suitability number between 40 and 50 (its rows end at "
                "'30 to 40 Poor' and resume at '>50 Unsuitable').")
    else:
        rating = "Unsuitable"

    result = {
        "suitability_number": round(sn, 1),
        "rating": rating,
        "d50_mm": d50_mm,
        "d20_mm": d20_mm,
        "d10_mm": d10_mm,
        "description": "Backfill suitability number for vibro-compaction, GEC-13 Eq. 4-3 (Brown 1977), p. 4-73, rated by Table 4-7",
    }
    if note:
        result["note"] = note
    return result


# ============================================================================
# Eq. 5-1: Area Replacement Ratio for Aggregate Columns (p. 5-31)
# alpha_sc = A_sc / A;  A = tributary (unit cell) area, by pattern
# The function keeps its old name (figure_5_2_...) because callers use it;
# GEC-13 Figure 5-2 is "Top feed vibro-replacement", not this relation.
# ============================================================================

def figure_5_2_area_replacement_ratio(column_diameter_m: float,
                                       spacing_m: float,
                                       pattern: str = "triangular") -> dict:
    """Area replacement ratio for aggregate columns (GEC-13 Eq. 5-1, p. 5-31).

    GEC-13 (FHWA-NHI-16-027) Vol I, Ch. 5, Section 4.1.2.2, Eq. 5-1:
    alpha_sc = A_sc / A, where A_sc is the area of the stone column after
    compaction and A the total area within the unit cell; typical ratios
    0.10 to 0.30 (p. 5-31). The unit cell is the tributary area about one
    column (p. 5-30, Figure 5-17: a regular hexagon for a triangular
    pattern). This function takes A_sc = pi/4 * d^2 and:
      - Triangular: A = 0.866 * s^2 (the hexagon's area, sqrt(3)/2 * s^2)
      - Square: A = s^2
    This is not GEC-13 Figure 5-2 (top feed vibro-replacement); the
    function keeps its name because callers use it.

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
        "description": "Area replacement ratio alpha_sc = A_sc / A for aggregate columns, GEC-13 Eq. 5-1 (p. 5-31)",
    }


# ============================================================================
# Eq. 5-4: Stress on the unimproved soil, stone column unit cell (p. 5-32)
# sigma_soil = q / [1 + (n - 1) a_sc];  n = stress ratio (typically 2-5)
# SRF = sigma_soil / q = 1 / (1 + a_sc*(n-1))
# The function keeps its old name (figure_5_5_...) because callers use it;
# GEC-13 Figure 5-5 is "Typical vibrator cross-section" (p. 5-14), not this
# relation, and the relation is the stress reduction method (GEC-13 4.1.2.6), not
# Priebe's (the Priebe curve is read from Figures 5-21 and 5-27).
# ============================================================================

def figure_5_5_settlement_improvement(area_replacement_ratio: float,
                                       stress_concentration_ratio: float = 3.0) -> dict:
    """Settlement improvement factor for stone columns (GEC-13 Eq. 5-4, p. 5-32).

    From the stress reduction method (GEC-13 4.1.2.6, after Han 2015), GEC-13 printed
    Section 4.1.2.4 "Stress Ratio", Eq. 5-4:
    sigma_soil = q / [1 + (n - 1) as], so

    Settlement Reduction Factor (SRF) = sigma_soil / q = 1 / (1 + as*(n-1))
    Settlement Improvement Factor = 1 / SRF = 1 + as*(n-1)

    This is not GEC-13 Figure 5-5 (a vibrator cross-section) and not the
    Priebe curve; the name is kept for existing callers.

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
        "description": "Stone column settlement improvement from the stress ratio, GEC-13 Eq. 5-4 (p. 5-32)",
    }


# ============================================================================
# Deep mixing composite modulus (parallel, area-weighted model)
# E_comp = a_s * E_col + (1 - a_s) * E_soil
# NOT printed in GEC-13: chapter 7 numbers no equations and has no Eq. 7-4.
# The function keeps its old name (equation_7_4_...) because callers use it.
# ============================================================================

def equation_7_4_composite_modulus(e_col_kpa: float,
                                    e_soil_kpa: float,
                                    area_replacement_ratio: float) -> dict:
    """Composite modulus of a deep mixed treatment zone (parallel model; not printed in GEC-13).

    E_comp = a_s * E_col + (1 - a_s) * E_soil

    GEC-13 does not print this equation. Its chapter 7 (Deep Mixing, Vol II)
    numbers no equations, so there is no "Eq. 7-4". Step 5 of the design
    procedure (Section 2.3.2.5, p. 7-16) says only that the treated zone
    "is treated as a composite of the soil-cement elements and the
    untreated zone", and the chapter defers to the FHWA (2013) deep mixing
    manual, which is not in this library. The area-weighted (parallel,
    equal-strain) form here is this library's own; it is not a printed
    GEC-13 method. The function keeps its name because callers use it.

    Column modulus: GEC-13's worked example takes E50 = 150 * qu from the
    FHWA (2013) deep mixing manual (Section 3.3.3.2, p. 7-32).

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
        "description": "Composite modulus of a deep mixed zone, parallel area-weighted model (not printed in GEC-13; ch. 7 p. 7-16 names a composite without an equation)",
    }


# ============================================================================
# Eq. 8-2: Groutability Ratio for Permeation Grouting (p. 8-29)
# N = (D15)SOIL / (D85)GROUT
# The function keeps its old name (equation_8_1_...) because callers use it;
# GEC-13 Eq. 8-1 is Darcy's law.
# ============================================================================

def equation_8_1_groutability_ratio(d15_soil_mm: float,
                                     d85_grout_mm: float) -> dict:
    """Groutability ratio for particulate permeation grouting (GEC-13 Eq. 8-2, p. 8-29).

    GEC-13 (FHWA-NHI-16-027) Vol II, Ch. 8, Section 2.3.2.1, Eq. 8-2
    (King and Bush 1963), printed p. 8-29:

        N = (D15)SOIL / (D85)GROUT

    Interpretation (p. 8-29): "Grouting is consistently possible in soils
    if N > 24 or NC > 11, and is not possible when N < 11 or NC < 6."
      N > 24:   Grouting feasible
      11-24:    Grouting uncertain (between the printed limits)
      N < 11:   Grouting not feasible
    NC (Eq. 8-3, (D10)SOIL / (D95)GROUT) is not computed here. This is not
    GEC-13 Eq. 8-1 (Darcy's law); the function keeps its name because
    callers use it.

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

    if n > 24:
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
        "description": "Groutability ratio N = D15_soil / D85_grout for particulate permeation grouting, GEC-13 Eq. 8-2 (p. 8-29)",
    }


# ============================================================================
# Long-Term Design Strength for Geosynthetics: GEC-11 Eq. 3-12 (p. 3-28)
# T_al = T_ult / (RF_ID * RF_CR * RF_D)   (FS is this function's extra divisor)
# GEC-13 has 10 chapters and no Eq. 11-1; it states the relation in words
# (Vol II p. 6-37) and refers to GEC-11 Chapter 3. The function keeps its
# old name (equation_11_1_...) because callers use it.
# ============================================================================

def equation_11_1_ltds(t_ult_kn_m: float,
                        rf_id: float,
                        rf_cr: float,
                        rf_cbd: float,
                        fs: float = 1.0) -> dict:
    """Long-term design strength of geosynthetic reinforcement (GEC-11 Eq. 3-12, p. 3-28).

    LTDS = T_ult / (RF_ID * RF_CR * RF_CBD * FS)

    GEC-13 prints no equation for this: the manual has ten chapters, so
    there is no "Eq. 11-1". GEC-13 Vol II Ch. 6, Section 4.6 (p. 6-37)
    states it in words ("the quotient of the quick (or short-term) tensile
    testing ... and the product of creep, installation damage, and
    durability reduction factors") and refers to Chapter 3 of GEC 11. The
    printed equation is GEC-11 (FHWA-NHI-10-024) Vol I Eq. 3-12, p. 3-28:

        T_al = T_ult / RF = T_ult / (RF_ID * RF_CR * RF_D)

    rf_cbd here is GEC-11's RF_D. ``fs`` is not in Eq. 3-12: it is this
    function's extra divisor, and its default 1.0 gives the printed
    equation. The function keeps its name because callers use it.

    GEC-11 prints the reduction factors themselves: RF_ID in Vol I
    Table 3-9 (p. 3-32; ``gec_11.tables.table_3_9_installation_damage``),
    typical RF_CR ranges by polymer in an unnumbered list on p. 3-33, and
    RF_D for PET in Table 3-11 (p. 3-36; ``gec_11.tables.table_3_11_pet_durability``).
    GEC-13 prints no reduction-factor table.

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
        "description": "Long-term design strength of geosynthetic reinforcement, GEC-11 Eq. 3-12 (p. 3-28); GEC-13 p. 6-37 refers to it",
    }
