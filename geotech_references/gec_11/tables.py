"""GEC-11 table lookup functions.

FHWA-NHI-10-024 — Mechanically Stabilized Earth Walls and Reinforced
Soil Slopes, Volume I, November 2009.

Functions
---------
table_2_1_min_reinforcement_length  Table 2-1  Minimum reinforcement lengths
table_2_2_min_embedment_depth       Table 2-2  Minimum embedment depths
table_3_1_select_fill_gradation     Table 3-1  Select fill gradation limits
table_3_3_electrochemical_steel     Table 3-3  Electrochemical limits (steel)
table_3_4_electrochemical_geosynth  Table 3-4  Electrochemical limits (geosynth)
table_3_6_pullout_parameters        Table 3-6  Pullout capacity parameters (F*, alpha)
table_3_7_galvanization             Table 3-7  Minimum galvanization thickness
table_3_8_corrosion_rates           Table 3-8  Steel corrosion rates
table_3_9_installation_damage       Table 3-9  Installation damage reduction factors
table_3_11_pet_durability           Table 3-11 PET durability reduction factors (RF_D)
table_4_1_load_combinations         Table 4-1  LRFD load combinations
table_4_2_permanent_load_factors    Table 4-2  Permanent load factors (gamma_p)
table_4_4_traffic_surcharge         Table 4-4  Equivalent height for traffic surcharge
table_4_5_external_resistance       Table 4-5  External stability resistance factors
table_4_6_bearing_capacity_factors  Table 4-6  Bearing capacity factors (Nc, Nq, Ngamma)
table_4_7_internal_resistance       Table 4-7  Internal stability resistance factors
"""

from .._interpolation import _linterp


# ============================================================================
# Table 2-1: Minimum Reinforcement Length
# ============================================================================

_TABLE_2_1 = [
    {
        "condition": "Static walls",
        "L_over_H": 0.7,
        "min_length_ft": 8.0,
        "min_length_m": 2.5,
        "notes": "Greater of 0.7H or 8 ft (2.5 m)",
    },
    {
        "condition": "Sloping surcharge",
        "L_over_H": 0.8,
        "min_length_ft": 8.0,
        "min_length_m": 2.5,
        "notes": "Greater of 0.8H or 8 ft (2.5 m)",
    },
    {
        "condition": "Seismic (low)",
        "L_over_H": 0.8,
        "min_length_ft": 8.0,
        "min_length_m": 2.5,
        "notes": "0.8H for low seismic zones",
    },
    {
        "condition": "Seismic (moderate to high)",
        "L_over_H": 1.1,
        "min_length_ft": 8.0,
        "min_length_m": 2.5,
        "notes": "Up to 1.1H for moderate-to-high seismic",
    },
]


def table_2_1_min_reinforcement_length(condition: str = "") -> list:
    """Look up minimum reinforcement length ratios from GEC-11 Table 2-1.

    Parameters
    ----------
    condition : str
        Optional filter (case-insensitive substring match).
        E.g., 'static', 'sloping', 'seismic'.

    Returns
    -------
    list of dict
        Matching entries with L/H ratio and minimum absolute length.
    """
    if not condition:
        return list(_TABLE_2_1)
    key = condition.lower().strip()
    return [r for r in _TABLE_2_1 if key in r["condition"].lower()]


# ============================================================================
# Table 2-2: Minimum Embedment Depth
# ============================================================================

_TABLE_2_2 = [
    {
        "condition": "Horizontal ground (walls)",
        "embedment_ratio": "H/20",
        "ratio_value": 1 / 20,
        "min_depth_ft": 2.0,
        "min_depth_m": 0.6,
    },
    {
        "condition": "Horizontal ground (abutments)",
        "embedment_ratio": "H/10",
        "ratio_value": 1 / 10,
        "min_depth_ft": 2.0,
        "min_depth_m": 0.6,
    },
    {
        "condition": "Slopes 3H:1V",
        "embedment_ratio": "H/10",
        "ratio_value": 1 / 10,
        "min_depth_ft": 2.0,
        "min_depth_m": 0.6,
    },
    {
        "condition": "Slopes 2H:1V",
        "embedment_ratio": "H/7",
        "ratio_value": 1 / 7,
        "min_depth_ft": 2.0,
        "min_depth_m": 0.6,
    },
    {
        "condition": "Slopes 1.5H:1V",
        "embedment_ratio": "H/5",
        "ratio_value": 1 / 5,
        "min_depth_ft": 2.0,
        "min_depth_m": 0.6,
    },
]


def table_2_2_min_embedment_depth(condition: str = "") -> list:
    """Look up minimum embedment depth ratios from GEC-11 Table 2-2.

    Parameters
    ----------
    condition : str
        Optional filter (case-insensitive substring match).
        E.g., 'horizontal', 'abutment', '2H:1V'.

    Returns
    -------
    list of dict
        Matching entries with embedment ratio and minimum depth.
    """
    if not condition:
        return list(_TABLE_2_2)
    key = condition.lower().strip()
    return [r for r in _TABLE_2_2 if key in r["condition"].lower()]


# ============================================================================
# Table 3-1: Select Fill Gradation Requirements
# ============================================================================

_TABLE_3_1 = [
    {"sieve": "4 in (102 mm)", "percent_passing_min": 100, "percent_passing_max": 100},
    {"sieve": "No. 40 (0.425 mm)", "percent_passing_min": 0, "percent_passing_max": 60},
    {"sieve": "No. 200 (0.075 mm)", "percent_passing_min": 0, "percent_passing_max": 15},
]

_TABLE_3_1_PI = {"PI_max": 6, "notes": "Plasticity index of fines fraction shall not exceed 6"}


def table_3_1_select_fill_gradation() -> dict:
    """Return select backfill gradation requirements from GEC-11 Table 3-1.

    Returns
    -------
    dict
        Gradation limits and plasticity index requirement.
    """
    return {
        "gradation": list(_TABLE_3_1),
        "PI_max": _TABLE_3_1_PI["PI_max"],
        "notes": _TABLE_3_1_PI["notes"],
        "reference": "FHWA-NHI-10-024, Table 3-1",
    }


# ============================================================================
# Table 3-3: Electrochemical Limits for Steel Reinforcement
# ============================================================================

_TABLE_3_3 = {
    "resistivity_min_ohm_cm": 3000,
    "pH_min": 5.0,
    "pH_max": 10.0,
    "chlorides_max_ppm": 100,
    "sulfates_max_ppm": 200,
    "organic_content_max_pct": 1.0,
    "notes": "Backfill must meet ALL criteria for steel reinforcement",
    "reference": "FHWA-NHI-10-024, Table 3-3",
}


def table_3_3_electrochemical_steel() -> dict:
    """Return electrochemical property limits for steel reinforcement fill.

    From GEC-11 Table 3-3. Backfill must meet all criteria simultaneously.

    Returns
    -------
    dict
        Electrochemical limits for steel-reinforced MSE walls.
    """
    return dict(_TABLE_3_3)


# ============================================================================
# Table 3-4: Electrochemical Limits for Geosynthetic Reinforcement
# ============================================================================

_TABLE_3_4 = [
    {
        "polymer": "Polyester (PET)",
        "pH_min": 3.0,
        "pH_max": 9.0,
        "notes": "PET is susceptible to hydrolysis at extreme pH",
    },
    {
        "polymer": "Polypropylene (PP)",
        "pH_min": 3.0,
        "pH_max": None,
        "notes": "PP resistant to wide pH range; pH > 3 required",
    },
    {
        "polymer": "Polyethylene (HDPE)",
        "pH_min": 3.0,
        "pH_max": None,
        "notes": "HDPE resistant to wide pH range; pH > 3 required",
    },
]


def table_3_4_electrochemical_geosynth(polymer: str = "") -> list:
    """Look up electrochemical limits for geosynthetic reinforcement.

    From GEC-11 Table 3-4.

    Parameters
    ----------
    polymer : str
        Optional filter (e.g., 'PET', 'PP', 'HDPE').

    Returns
    -------
    list of dict
        Matching entries with pH limits.
    """
    if not polymer:
        return list(_TABLE_3_4)
    key = polymer.lower().strip()
    return [r for r in _TABLE_3_4 if key in r["polymer"].lower()]


# ============================================================================
# Table 3-6: Pullout Capacity Design Parameters
# ============================================================================

_TABLE_3_6 = [
    {
        "reinforcement": "Ribbed steel strips",
        "F_star_at_top": "tan(phi)",
        "F_star_at_6m": "tan(phi)",
        "alpha": 1.0,
        "notes": "F* = tan(phi) at all depths; alpha = 1.0",
    },
    {
        "reinforcement": "Smooth steel strips",
        "F_star_at_top": "0.4",
        "F_star_at_6m": "0.4",
        "alpha": 1.0,
        "notes": "F* = 0.4 constant; alpha = 1.0",
    },
    {
        "reinforcement": "Steel grids (w-transverse bars)",
        "F_star_at_top": "20 * (t/St)",
        "F_star_at_6m": "10 * (t/St)",
        "alpha": 1.0,
        "notes": "t = transverse bar diameter, St = transverse spacing",
    },
    {
        "reinforcement": "Geogrids",
        "F_star_at_top": "0.8 * tan(phi)",
        "F_star_at_6m": "0.8 * tan(phi)",
        "alpha": 0.8,
        "notes": "Default; project-specific pullout tests may increase",
    },
    {
        "reinforcement": "Geotextiles",
        "F_star_at_top": "0.67 * tan(phi)",
        "F_star_at_6m": "0.67 * tan(phi)",
        "alpha": 0.6,
        "notes": "Default; limited use in permanent MSE walls",
    },
]


def table_3_6_pullout_parameters(reinforcement: str = "") -> list:
    """Look up pullout capacity design parameters from GEC-11 Table 3-6.

    Parameters
    ----------
    reinforcement : str
        Optional filter (e.g., 'ribbed', 'grid', 'geogrid', 'geotextile').

    Returns
    -------
    list of dict
        Matching entries with F* and alpha values.
    """
    if not reinforcement:
        return list(_TABLE_3_6)
    key = reinforcement.lower().strip()
    return [r for r in _TABLE_3_6 if key in r["reinforcement"].lower()]


# ============================================================================
# Table 3-7: Minimum Galvanization Thickness
# ============================================================================

_TABLE_3_7 = [
    {
        "component": "Strip reinforcement (thickness < 1/4 in)",
        "thickness_mils": 3.4,
        "thickness_um": 85,
    },
    {
        "component": "Strip reinforcement (thickness >= 1/4 in)",
        "thickness_mils": 3.9,
        "thickness_um": 100,
    },
    {
        "component": "Wire reinforcement (all sizes)",
        "thickness_mils": 3.4,
        "thickness_um": 85,
    },
]


def table_3_7_galvanization() -> list:
    """Return minimum galvanization thickness from GEC-11 Table 3-7.

    Returns
    -------
    list of dict
        Galvanization thickness by component type.
    """
    return list(_TABLE_3_7)


# ============================================================================
# Table 3-8: Steel Corrosion Rates
# ============================================================================

_TABLE_3_8 = [
    {
        "material": "Zinc (galvanization)",
        "rate_um_per_yr": 15.0,
        "period": "First 2 years",
        "notes": "Initial corrosion rate for zinc coating",
    },
    {
        "material": "Zinc (galvanization)",
        "rate_um_per_yr": 4.0,
        "period": "After first 2 years",
        "notes": "Long-term zinc corrosion rate",
    },
    {
        "material": "Carbon steel",
        "rate_um_per_yr": 12.0,
        "period": "After zinc depleted",
        "notes": "Rate applies after galvanization is consumed",
    },
]


def table_3_8_corrosion_rates(material: str = "") -> list:
    """Look up steel corrosion rates from GEC-11 Table 3-8.

    Parameters
    ----------
    material : str
        Optional filter (e.g., 'zinc', 'carbon', 'steel').

    Returns
    -------
    list of dict
        Corrosion rates in micrometers per year.
    """
    if not material:
        return list(_TABLE_3_8)
    key = material.lower().strip()
    return [r for r in _TABLE_3_8 if key in r["material"].lower()]


# ============================================================================
# Table 3-9: Installation Damage Reduction Factors (RF_ID)
# ============================================================================

_TABLE_3_9 = [
    {
        "geosynthetic": "HDPE uniaxial geogrid",
        "backfill_type1_low": 1.20,
        "backfill_type1_high": 1.45,
        "backfill_type2_low": 1.10,
        "backfill_type2_high": 1.20,
    },
    {
        "geosynthetic": "PP biaxial geogrid",
        "backfill_type1_low": 1.20,
        "backfill_type1_high": 1.45,
        "backfill_type2_low": 1.10,
        "backfill_type2_high": 1.20,
    },
    {
        "geosynthetic": "PVC coated PET geogrid",
        "backfill_type1_low": 1.30,
        "backfill_type1_high": 1.85,
        "backfill_type2_low": 1.10,
        "backfill_type2_high": 1.30,
    },
    {
        "geosynthetic": "Acrylic coated PET geogrid",
        "backfill_type1_low": 1.30,
        "backfill_type1_high": 2.05,
        "backfill_type2_low": 1.20,
        "backfill_type2_high": 1.40,
    },
    {
        "geosynthetic": "Woven geotextile (PP and PET)",
        "backfill_type1_low": 1.40,
        "backfill_type1_high": 2.20,
        "backfill_type2_low": 1.10,
        "backfill_type2_high": 1.40,
    },
    {
        "geosynthetic": "Non-woven geotextile (PP and PET)",
        "backfill_type1_low": 1.40,
        "backfill_type1_high": 2.50,
        "backfill_type2_low": 1.10,
        "backfill_type2_high": 1.40,
    },
    {
        "geosynthetic": "Slit film woven PP geotextile",
        "backfill_type1_low": 1.60,
        "backfill_type1_high": 3.00,
        "backfill_type2_low": 1.10,
        "backfill_type2_high": 2.00,
    },
]


def table_3_9_installation_damage(geosynthetic: str = "") -> list:
    """Look up installation damage reduction factors from GEC-11 Table 3-9.

    Type 1 backfill: well-graded, max particle size up to 4 in (102 mm).
    Type 2 backfill: uniform fine sand to medium sand, max 3/4 in (19 mm).

    Parameters
    ----------
    geosynthetic : str
        Optional filter (e.g., 'HDPE', 'PP biaxial', 'PVC', 'woven').

    Returns
    -------
    list of dict
        RF_ID ranges for Type 1 and Type 2 backfill.
    """
    if not geosynthetic:
        return list(_TABLE_3_9)
    key = geosynthetic.lower().strip()
    return [r for r in _TABLE_3_9 if key in r["geosynthetic"].lower()]


# ============================================================================
# Table 3-11: PET Durability Reduction Factors (RF_D)
# ============================================================================

_TABLE_3_11 = [
    {
        "product": "Geotextiles (Mn < 20,000, CEG 40-50)",
        "pH_5_to_8": 1.6,
        "pH_3_to_5_or_8_to_9": 2.0,
        "notes": "Lower molecular weight PET; more susceptible to hydrolysis",
    },
    {
        "product": "Coated geogrids (Mn > 25,000, CEG < 30)",
        "pH_5_to_8": 1.15,
        "pH_3_to_5_or_8_to_9": 1.3,
        "notes": "Higher molecular weight PET; better durability",
    },
]


def table_3_11_pet_durability(product: str = "") -> list:
    """Look up PET durability reduction factors from GEC-11 Table 3-11.

    Parameters
    ----------
    product : str
        Optional filter (e.g., 'geotextile', 'geogrid', 'coated').

    Returns
    -------
    list of dict
        RF_D values for neutral and aggressive pH ranges.
    """
    if not product:
        return list(_TABLE_3_11)
    key = product.lower().strip()
    return [r for r in _TABLE_3_11 if key in r["product"].lower()]


# ============================================================================
# Table 4-1: LRFD Load Combinations
# ============================================================================

_TABLE_4_1 = [
    {
        "limit_state": "Strength I",
        "EH_ES_EV": "gamma_p",
        "LL_LS": 1.75,
        "EQ": 0.0,
        "CT": 0.0,
        "notes": "Normal gravity loading",
    },
    {
        "limit_state": "Extreme Event I",
        "EH_ES_EV": "gamma_p",
        "LL_LS": "gamma_EQ",
        "EQ": 1.00,
        "CT": 0.0,
        "notes": "Seismic loading; gamma_EQ typically 0.0 to 0.50",
    },
    {
        "limit_state": "Extreme Event II",
        "EH_ES_EV": "gamma_p",
        "LL_LS": 0.50,
        "EQ": 0.0,
        "CT": 1.00,
        "notes": "Vehicle collision on traffic barrier",
    },
    {
        "limit_state": "Service I",
        "EH_ES_EV": 1.00,
        "LL_LS": 1.00,
        "EQ": 0.0,
        "CT": 0.0,
        "notes": "Settlement and lateral deformation check",
    },
]


def table_4_1_load_combinations(limit_state: str = "") -> list:
    """Look up LRFD load combinations from GEC-11 Table 4-1.

    Parameters
    ----------
    limit_state : str
        Optional filter (e.g., 'strength', 'extreme', 'service').

    Returns
    -------
    list of dict
        Load factor combinations by limit state.
    """
    if not limit_state:
        return list(_TABLE_4_1)
    key = limit_state.lower().strip()
    return [r for r in _TABLE_4_1 if key in r["limit_state"].lower()]


# ============================================================================
# Table 4-2: Permanent Load Factors (gamma_p)
# ============================================================================

_TABLE_4_2 = [
    {
        "load_type": "DC",
        "description": "Dead load of structural components",
        "gamma_max": 1.25,
        "gamma_min": 0.90,
    },
    {
        "load_type": "EH Active",
        "description": "Horizontal earth pressure (active)",
        "gamma_max": 1.50,
        "gamma_min": 0.90,
    },
    {
        "load_type": "EV Overall Stability",
        "description": "Vertical earth pressure (overall stability)",
        "gamma_max": 1.00,
        "gamma_min": None,
    },
    {
        "load_type": "EV Retaining Walls",
        "description": "Vertical earth pressure (retaining walls)",
        "gamma_max": 1.35,
        "gamma_min": 1.00,
    },
    {
        "load_type": "ES",
        "description": "Earth surcharge",
        "gamma_max": 1.50,
        "gamma_min": 0.75,
    },
]


def table_4_2_permanent_load_factors(load_type: str = "") -> list:
    """Look up permanent load factors from GEC-11 Table 4-2.

    Parameters
    ----------
    load_type : str
        Optional filter (e.g., 'DC', 'EH', 'EV', 'ES').

    Returns
    -------
    list of dict
        Max and min load factors by load type.
    """
    if not load_type:
        return list(_TABLE_4_2)
    key = load_type.lower().strip()
    return [r for r in _TABLE_4_2 if key in r["load_type"].lower()]


# ============================================================================
# Table 4-4: Equivalent Height for Traffic Surcharge on Abutments
# ============================================================================

_TABLE_4_4_DEPTHS_FT = [5.0, 10.0, 20.0]
_TABLE_4_4_HEQ_FT = [4.0, 3.0, 2.0]


def table_4_4_traffic_surcharge(wall_height_ft: float = 0.0) -> dict:
    """Look up equivalent height of soil for traffic surcharge.

    From GEC-11 Table 4-4. Interpolates for intermediate wall heights.

    Parameters
    ----------
    wall_height_ft : float
        Wall height in feet. If 0, returns the full table.

    Returns
    -------
    dict
        Equivalent height (h_eq) in feet and the full table data.
    """
    table = [
        {"wall_height_ft": d, "h_eq_ft": h}
        for d, h in zip(_TABLE_4_4_DEPTHS_FT, _TABLE_4_4_HEQ_FT)
    ]

    if wall_height_ft <= 0:
        return {"table": table, "reference": "FHWA-NHI-10-024, Table 4-4"}

    if wall_height_ft <= 5.0:
        h_eq = 4.0
    elif wall_height_ft >= 20.0:
        h_eq = 2.0
    else:
        h_eq = _linterp(wall_height_ft, _TABLE_4_4_DEPTHS_FT, _TABLE_4_4_HEQ_FT)

    return {
        "wall_height_ft": wall_height_ft,
        "h_eq_ft": round(h_eq, 2),
        "table": table,
        "reference": "FHWA-NHI-10-024, Table 4-4",
    }


# ============================================================================
# Table 4-5: External Stability Resistance Factors
# ============================================================================

_TABLE_4_5 = [
    {
        "failure_mode": "Bearing resistance",
        "phi_factor": 0.65,
        "notes": "Bearing capacity of foundation soil",
    },
    {
        "failure_mode": "Sliding",
        "phi_factor": 1.0,
        "notes": "Sliding at base of reinforced zone",
    },
    {
        "failure_mode": "Overall (global) stability — well-defined conditions",
        "phi_factor": 0.75,
        "notes": "Slope stability with adequate subsurface data",
    },
    {
        "failure_mode": "Overall (global) stability — limited information",
        "phi_factor": 0.65,
        "notes": "Slope stability with limited subsurface data",
    },
]


def table_4_5_external_resistance(failure_mode: str = "") -> list:
    """Look up external stability resistance factors from GEC-11 Table 4-5.

    Parameters
    ----------
    failure_mode : str
        Optional filter (e.g., 'bearing', 'sliding', 'global', 'overall').

    Returns
    -------
    list of dict
        Resistance factors by failure mode.
    """
    if not failure_mode:
        return list(_TABLE_4_5)
    key = failure_mode.lower().strip()
    return [r for r in _TABLE_4_5 if key in r["failure_mode"].lower()]


# ============================================================================
# Table 4-6: Bearing Capacity Factors (Nc, Nq, Ngamma)
# ============================================================================

_TABLE_4_6_PHI = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
    41, 42, 43, 44, 45,
]

_TABLE_4_6_NC = [
    5.14, 5.38, 5.63, 5.90, 6.19, 6.49, 6.81, 7.16, 7.53, 7.92, 8.35,
    8.80, 9.28, 9.81, 10.37, 10.98, 11.63, 12.34, 13.10, 13.93, 14.83,
    15.82, 16.88, 18.05, 19.32, 20.72, 22.25, 23.94, 25.80, 27.86, 30.14,
    32.67, 35.49, 38.64, 42.16, 46.12, 50.59, 55.63, 61.35, 67.87, 75.31,
    83.86, 93.71, 105.11, 118.37, 133.88,
]

_TABLE_4_6_NQ = [
    1.00, 1.09, 1.20, 1.31, 1.43, 1.57, 1.72, 1.88, 2.06, 2.25, 2.47,
    2.71, 2.97, 3.26, 3.59, 3.94, 4.34, 4.77, 5.26, 5.80, 6.40,
    7.07, 7.82, 8.66, 9.60, 10.66, 11.85, 13.20, 14.72, 16.44, 18.40,
    20.63, 23.18, 26.09, 29.44, 33.30, 37.75, 42.92, 48.93, 55.96, 64.20,
    73.90, 85.38, 99.02, 115.31, 134.88,
]

_TABLE_4_6_NGAMMA = [
    0.00, 0.07, 0.15, 0.24, 0.34, 0.45, 0.57, 0.71, 0.86, 1.03, 1.22,
    1.44, 1.69, 1.97, 2.29, 2.65, 3.06, 3.53, 4.07, 4.68, 5.39,
    6.20, 7.13, 8.20, 9.44, 10.88, 12.54, 14.47, 16.72, 19.34, 22.40,
    25.99, 30.22, 35.19, 41.06, 48.03, 56.31, 66.19, 78.03, 92.25, 109.41,
    130.22, 155.55, 186.54, 224.64, 271.76,
]


def table_4_6_bearing_capacity_factors(phi_deg: float = None) -> dict:
    """Look up bearing capacity factors from GEC-11 Table 4-6.

    Interpolates for non-integer friction angles.

    Parameters
    ----------
    phi_deg : float
        Friction angle in degrees (0-45). If None, returns the full table.

    Returns
    -------
    dict
        Nc, Nq, and Ngamma values.
    """
    if phi_deg is None:
        return {
            "table": [
                {"phi_deg": p, "Nc": nc, "Nq": nq, "Ngamma": ng}
                for p, nc, nq, ng in zip(
                    _TABLE_4_6_PHI, _TABLE_4_6_NC, _TABLE_4_6_NQ, _TABLE_4_6_NGAMMA
                )
            ],
            "reference": "FHWA-NHI-10-024, Table 4-6",
        }

    if phi_deg < 0 or phi_deg > 45:
        raise ValueError("phi_deg must be between 0 and 45 degrees")

    nc = _linterp(phi_deg, _TABLE_4_6_PHI, _TABLE_4_6_NC)
    nq = _linterp(phi_deg, _TABLE_4_6_PHI, _TABLE_4_6_NQ)
    ng = _linterp(phi_deg, _TABLE_4_6_PHI, _TABLE_4_6_NGAMMA)

    return {
        "phi_deg": phi_deg,
        "Nc": round(nc, 2),
        "Nq": round(nq, 2),
        "Ngamma": round(ng, 2),
        "reference": "FHWA-NHI-10-024, Table 4-6",
    }


# ============================================================================
# Table 4-7: Internal Stability Resistance Factors
# ============================================================================

_TABLE_4_7 = [
    {
        "reinforcement_type": "Metallic strip reinforcement",
        "static_phi": 0.75,
        "combined_static_phi": 0.75,
        "earthquake_phi": 1.00,
        "traffic_barrier_phi": 1.00,
    },
    {
        "reinforcement_type": "Metallic grid reinforcement (rigid face)",
        "static_phi": 0.65,
        "combined_static_phi": 0.65,
        "earthquake_phi": 0.85,
        "traffic_barrier_phi": 0.85,
    },
    {
        "reinforcement_type": "Geosynthetic reinforcement",
        "static_phi": 0.90,
        "combined_static_phi": 0.90,
        "earthquake_phi": 1.20,
        "traffic_barrier_phi": 1.20,
    },
    {
        "reinforcement_type": "Pullout resistance (all types)",
        "static_phi": 0.90,
        "combined_static_phi": 0.90,
        "earthquake_phi": 1.20,
        "traffic_barrier_phi": 1.00,
    },
]


def table_4_7_internal_resistance(reinforcement_type: str = "") -> list:
    """Look up internal stability resistance factors from GEC-11 Table 4-7.

    Parameters
    ----------
    reinforcement_type : str
        Optional filter (e.g., 'metallic strip', 'geosynthetic', 'pullout').

    Returns
    -------
    list of dict
        Resistance factors by reinforcement type and loading condition.
    """
    if not reinforcement_type:
        return list(_TABLE_4_7)
    key = reinforcement_type.lower().strip()
    return [r for r in _TABLE_4_7 if key in r["reinforcement_type"].lower()]
