"""Eurocode 7-2 table lookup functions.

Digitized tables from EN 1997-2:2007, Eurocode 7: Geotechnical design -
Part 2: Ground investigation and testing.  Follows the DM7/GEC pattern:
private data with ``_TABLE_*`` prefix, public lookup functions with
string-matched keys.  Page citations are the *printed* page number of the
standard (bottom-of-page numeral); the source PDF is
``docs/en.1997.2.2007-1.pdf`` (public.resource.org copy, printed page =
PDF page index - 1).
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 2.1: Simplified overview of the applicability of field investigation
# methods covered by Sections 3 and 4 (printed p.25)
# Values are composite ratings: R1/R2/R3 = high/medium/low for rock,
# C1/C2/C3 = high/medium/low for coarse soil, F1/F2/F3 = high/medium/low
# for fine soil.  A cell may combine several ratings (e.g. "C2F2").
# "-" = not applicable / not obtainable.
# ============================================================================

_TABLE_2_1_METHODS = [
    "sampling_soil_a", "sampling_soil_b", "sampling_soil_c",
    "sampling_rock_a", "sampling_rock_b", "sampling_rock_c",
    "cpt_cptu", "pressuremeter", "rdt", "flexible_dilatometer",
    "spt", "dpl_dpm", "dph_dpsh", "wst", "fvt", "dmt", "plt",
    "groundwater_open", "groundwater_closed",
]

_TABLE_2_1_ROWS = {
    "type_of_soil": [
        "C1F1", "C1F1", "C2F2", "-", "-", "-", "C2F2", "C3F3", "-", "C3F3",
        "C2F1", "C3F3", "C3F3", "-", "-", "C2F2", "-", "-", "-",
    ],
    "type_of_rock": [
        "-", "-", "-", "R1", "R1", "R2", "R3c", "R3", "R2", "-",
        "-", "-", "-", "-", "-", "-", "-", "-", "-",
    ],
    "extension_of_layers": [
        "C1F1", "C1F1", "C3F3", "R1", "R1", "R2", "C1F1", "R3C3F3", "R3", "C3F3",
        "C2F2", "C1F2", "C1F2", "F2", "-", "C2F1", "-", "-", "-",
    ],
    "groundwater_level": [
        "-", "-", "-", "-", "-", "-", "C2", "-", "-", "-",
        "-", "-", "-", "-", "-", "-", "-", "R2C1F2", "R1C1F1",
    ],
    "pore_water_pressure": [
        "-", "-", "-", "-", "-", "-", "C2F2", "F3", "-", "-",
        "-", "-", "-", "-", "-", "-", "-", "R2C1F2", "R1C1F1",
    ],
    "particle_size": [
        "C1F1", "C1F1", "-", "R1", "R1", "R2", "-", "-", "-", "-",
        "C2F1", "-", "-", "-", "-", "-", "-", "-", "-",
    ],
    "water_content": [
        "C1F1", "C2F1", "C3F3", "R1", "R1", "-", "-", "-", "-", "-",
        "C2F2", "-", "-", "-", "-", "-", "-", "-", "-",
    ],
    "atterberg_limits": [
        "F1", "F1", "-", "-", "-", "-", "-", "-", "-", "-",
        "F2", "-", "-", "-", "-", "-", "-", "-", "-",
    ],
    "density": [
        "C2F1", "C3F3", "-", "R1", "R1", "-", "C2F2", "-", "-", "-",
        "C2F2", "C2", "C2", "-", "-", "C2F2", "-", "-", "-",
    ],
    "shear_strength": [
        "C2F1", "-", "-", "R1", "-", "-", "C2F1", "C1F1", "-", "-",
        "C2F3", "C2F3", "C2F3", "C2", "F1", "C2F1", "R2C1F1", "-", "-",
    ],
    "compressibility": [
        "C2F1", "-", "-", "R1", "-", "-", "C1F2", "C1F1", "R1", "F1",
        "C2F2", "C2F2", "C2F2", "C2", "-", "C2F1", "C1F1", "-", "-",
    ],
    "permeability": [
        "C2F1", "-", "-", "R1", "-", "-", "C3F2", "F3", "-", "-",
        "-", "-", "-", "-", "-", "-", "-", "C2F3", "C2F2",
    ],
    "chemical_tests": [
        "C1F1", "C1F1", "-", "R1", "R1", "-", "-", "-", "-", "-",
        "C2F2", "-", "-", "-", "-", "-", "-", "-", "-",
    ],
}

_TABLE_2_1 = {
    prop: dict(zip(_TABLE_2_1_METHODS, ratings))
    for prop, ratings in _TABLE_2_1_ROWS.items()
}


def table_2_1_test_applicability(soil_property: str, method: str = "") -> dict:
    """Applicability of field investigation methods to a soil property (Table 2.1).

    Simplified overview of which sampling categories, field tests, and
    groundwater measurement systems can obtain each type of geotechnical
    information, and with what reliability.

    Parameters
    ----------
    soil_property : str
        Property key: 'type_of_soil', 'type_of_rock', 'extension_of_layers',
        'groundwater_level', 'pore_water_pressure', 'particle_size',
        'water_content', 'atterberg_limits', 'density', 'shear_strength',
        'compressibility', 'permeability', 'chemical_tests'.
    method : str
        Investigation method key (optional).  If given, returns the rating
        for that single method.  Valid keys: 'sampling_soil_a/b/c',
        'sampling_rock_a/b/c', 'cpt_cptu', 'pressuremeter', 'rdt',
        'flexible_dilatometer', 'spt', 'dpl_dpm', 'dph_dpsh', 'wst', 'fvt',
        'dmt', 'plt', 'groundwater_open', 'groundwater_closed'.
        If empty, returns ratings for all methods.

    Returns
    -------
    dict
        If method given: {"soil_property", "method", "rating"}.
        Rating combines R1-R3 (rock: high/medium/low), C1-C3 (coarse soil:
        high/medium/low), F1-F3 (fine soil: high/medium/low); "-" means not
        applicable/not obtainable.
        If method omitted: {"soil_property", "ratings": {method: rating, ...}}.

    Raises
    ------
    ValueError
        If soil_property or method is not recognized.
    """
    prop = soil_property.strip().lower().replace(" ", "_")
    if prop not in _TABLE_2_1:
        raise ValueError(
            f"Unknown soil_property '{soil_property}'. "
            f"Valid: {', '.join(sorted(_TABLE_2_1.keys()))}"
        )
    row = _TABLE_2_1[prop]
    if not method:
        return {"soil_property": prop, "ratings": dict(row)}

    key = method.strip().lower().replace(" ", "_").replace("-", "_")
    if key not in row:
        raise ValueError(
            f"Unknown method '{method}'. "
            f"Valid: {', '.join(_TABLE_2_1_METHODS)}"
        )
    return {"soil_property": prop, "method": key, "rating": row[key]}


# ============================================================================
# Table 3.1: Quality classes of soil samples for laboratory testing and
# sampling categories to be used (printed p.34)
# ============================================================================

_TABLE_3_1 = {
    1: {
        "unchanged_properties": [
            "particle_size", "water_content",
            "density_density_index_permeability",
            "compressibility_shear_strength",
        ],
        "determinable_properties": [
            "sequence_of_layers", "boundaries_broad", "boundaries_fine",
            "atterberg_limits_particle_density_organic_content",
            "water_content", "density_density_index_porosity_permeability",
            "compressibility_shear_strength",
        ],
        "sampling_categories": ["A"],
    },
    2: {
        "unchanged_properties": [
            "particle_size", "water_content",
            "density_density_index_permeability",
        ],
        "determinable_properties": [
            "sequence_of_layers", "boundaries_broad", "boundaries_fine",
            "atterberg_limits_particle_density_organic_content",
            "water_content", "density_density_index_porosity_permeability",
        ],
        "sampling_categories": ["A"],
    },
    3: {
        "unchanged_properties": ["particle_size", "water_content"],
        "determinable_properties": [
            "sequence_of_layers", "boundaries_broad",
            "atterberg_limits_particle_density_organic_content",
            "water_content",
        ],
        "sampling_categories": ["A", "B"],
    },
    4: {
        "unchanged_properties": ["particle_size"],
        "determinable_properties": [
            "sequence_of_layers", "boundaries_broad",
            "atterberg_limits_particle_density_organic_content",
        ],
        "sampling_categories": ["A", "B"],
    },
    5: {
        "unchanged_properties": [],
        "determinable_properties": ["sequence_of_layers"],
        "sampling_categories": ["A", "B", "C"],
    },
}


def table_3_1_quality_class(quality_class: int) -> dict:
    """Soil sample quality class properties and sampling category (Table 3.1).

    Parameters
    ----------
    quality_class : int
        Quality class 1 (least disturbed) to 5 (most disturbed).

    Returns
    -------
    dict
        Keys: quality_class, unchanged_properties (list of soil properties
        assumed to remain unchanged during sampling/handling),
        determinable_properties (list of properties that can be determined
        from the sample), sampling_categories (list of EN ISO 22475-1
        sampling method categories capable of achieving this class).

    Raises
    ------
    ValueError
        If quality_class is not 1-5.
    """
    if quality_class not in _TABLE_3_1:
        raise ValueError(f"quality_class must be 1-5, got {quality_class}")
    result = {"quality_class": quality_class}
    result.update({k: list(v) if isinstance(v, list) else v
                    for k, v in _TABLE_3_1[quality_class].items()})
    return result


# ============================================================================
# Annex D.1 / Table D.1: Effective angle of shearing resistance (phi') and
# drained Young's modulus (E') for quartz and feldspar sands from CPT cone
# resistance (qc) (printed p.111; Bergdahl et al. 1993)
# ============================================================================

_TABLE_D1 = [
    # (density_index, qc_min_MPa, qc_max_MPa, phi_min_deg, phi_max_deg, e_min_MPa, e_max_MPa)
    ("very_loose", 0.0, 2.5, 29, 32, 0, 10),
    ("loose", 2.5, 5.0, 32, 35, 10, 20),
    ("medium_dense", 5.0, 10.0, 35, 37, 20, 30),
    ("dense", 10.0, 20.0, 37, 40, 30, 60),
    ("very_dense", 20.0, None, 40, 42, 60, 90),
]


def table_d1_phi_e_from_qc(qc_mpa: float, soil_type: str = "sand") -> dict:
    """Effective angle of shearing resistance and drained modulus from CPT (Table D.1).

    Example correlation (quartz and feldspar sands) for deriving phi' and
    the drained (long-term) Young's modulus E' from cone resistance qc, for
    bearing resistance and settlement calculations of spread foundations.

    Parameters
    ----------
    qc_mpa : float
        Mean cone penetration resistance in the layer, in MPa.  Must be >= 0.
    soil_type : str
        'sand' (values as tabulated), 'silty' (phi' reduced by 3 degrees
        per note a), or 'gravelly' (phi' increased by 2 degrees per note a).

    Returns
    -------
    dict
        Keys: density_index, qc_mpa, phi_min_deg, phi_max_deg, e_min_mpa,
        e_max_mpa, soil_type.

    Raises
    ------
    ValueError
        If qc_mpa < 0 or soil_type is not recognized.
    """
    if qc_mpa < 0:
        raise ValueError(f"qc_mpa must be >= 0, got {qc_mpa}")
    st = soil_type.strip().lower()
    if st not in ("sand", "silty", "gravelly"):
        raise ValueError(f"Unknown soil_type '{soil_type}'. Use sand, silty, or gravelly")

    for density_index, qc_min, qc_max, phi_min, phi_max, e_min, e_max in _TABLE_D1:
        hi_ok = qc_max is None or qc_mpa <= qc_max
        if qc_mpa >= qc_min and hi_ok:
            if st == "silty":
                phi_min, phi_max = phi_min - 3, phi_max - 3
            elif st == "gravelly":
                phi_min, phi_max = phi_min + 2, phi_max + 2
            return {
                "density_index": density_index,
                "qc_mpa": qc_mpa,
                "phi_min_deg": phi_min,
                "phi_max_deg": phi_max,
                "e_min_mpa": e_min,
                "e_max_mpa": e_max,
                "soil_type": st,
            }
    # qc_mpa exceeds all ranges (shouldn't happen since very_dense has no upper bound)
    raise ValueError(f"No density category found for qc_mpa={qc_mpa}")  # pragma: no cover


# ============================================================================
# Annex D.2: correlation between qc and phi' for poorly-graded sands
# (printed p.112; Stenzel et al. 1978 / DIN 4094-1)
# See equations.py: equation_d2_phi_from_qc()
# ============================================================================


# ============================================================================
# Annex D.4 / Table D.2: values of correlation factor 'a' between oedometer
# modulus Eoed and CPT cone resistance qc, by soil type (printed p.114;
# Sanglerat 1972).  Eoed = a * qc  (see equations.equation_4_3_oedometer_modulus_from_qc)
# ============================================================================

_TABLE_D2 = {
    "low_plasticity_clay": [
        (None, 0.7, 3, 8),
        (0.7, 2.0, 2, 5),
        (2.0, None, 1, 2.5),
    ],
    "low_plasticity_silt": [
        (None, 2.0, 3, 6),
        (2.0, None, 1, 2),
    ],
    "very_plastic_clay": [
        (None, 2.0, 2, 6),
    ],
    "very_plastic_silt": [
        (2.0, None, 1, 2),
    ],
    "very_organic_silt": [
        (None, 1.2, 2, 8),
    ],
    "chalk": [
        (2.0, 3.0, 2, 4),
        (3.0, None, 1.5, 3),
    ],
    "sand": [
        (None, 5.0, 2.0, 2.0),
        (10.0, None, 1.5, 1.5),
    ],
}


def table_d2_alpha_oedometer(soil_type: str, qc_mpa: float) -> dict:
    """Correlation factor alpha for Eoed = alpha * qc, by soil type (Table D.2).

    Parameters
    ----------
    soil_type : str
        'low_plasticity_clay', 'low_plasticity_silt', 'very_plastic_clay',
        'very_plastic_silt', 'very_organic_silt', 'chalk', or 'sand'.
    qc_mpa : float
        Cone penetration resistance, in MPa.

    Returns
    -------
    dict
        Keys: soil_type, qc_mpa, alpha_min, alpha_max.

    Raises
    ------
    ValueError
        If soil_type is unknown or qc_mpa falls outside the tabulated
        ranges for that soil type (sand is only tabulated for qc<5 or
        qc>=10 MPa; for 'peat_very_organic_clay' see qc<0.7 with water
        content dependence, not covered by this simplified lookup).
    """
    key = soil_type.strip().lower().replace(" ", "_")
    if key not in _TABLE_D2:
        raise ValueError(
            f"Unknown soil_type '{soil_type}'. "
            f"Valid: {', '.join(sorted(_TABLE_D2.keys()))}"
        )
    for qc_min, qc_max, a_min, a_max in _TABLE_D2[key]:
        lo_ok = qc_min is None or qc_mpa >= qc_min
        hi_ok = qc_max is None or qc_mpa <= qc_max
        if lo_ok and hi_ok:
            return {
                "soil_type": key,
                "qc_mpa": qc_mpa,
                "alpha_min": a_min,
                "alpha_max": a_max,
            }
    raise ValueError(
        f"qc_mpa={qc_mpa} is outside the tabulated ranges for soil_type '{key}'"
    )


# ============================================================================
# Annex D.6 / Table D.3, D.4: unit base and shaft resistance of cast in-situ
# piles in coarse soil with little or no fines, from CPT (printed p.115-116;
# Dutch method, NEN 6743-1)
# ============================================================================

_TABLE_D3_QC = [10, 15, 20, 25]  # MPa (qc >= 25 column labelled ">=25")
_TABLE_D3 = {
    0.02: [0.70, 1.05, 1.40, 1.75],
    0.03: [0.90, 1.35, 1.80, 2.25],
    0.10: [2.00, 3.00, 3.50, 4.00],
}


def table_d3_pile_base_resistance(settlement_ratio: float, qc_mpa: float,
                                   enlarged_base: bool = False) -> dict:
    """Unit base resistance of cast in-situ piles in coarse soil (Table D.3).

    Interpolates pb (MPa) at the given normalised pile-head settlement
    ratio (s/Db) and average cone resistance qc.

    Parameters
    ----------
    settlement_ratio : float
        Normalised settlement s/Db.  Tabulated at 0.02, 0.03, and 0.10
        (0.10 corresponds to ultimate settlement sg).
    qc_mpa : float
        Average cone penetration resistance, in MPa (tabulated 10-25 MPa;
        clamped at endpoints).
    enlarged_base : bool
        If True, multiply the result by 0.75 per the table note (piles
        with pile-base enlargement).

    Returns
    -------
    dict
        Keys: settlement_ratio, qc_mpa, pb_mpa.

    Raises
    ------
    ValueError
        If settlement_ratio is not one of 0.02, 0.03, 0.10.
    """
    ratios = sorted(_TABLE_D3.keys())
    if settlement_ratio not in _TABLE_D3:
        raise ValueError(
            f"settlement_ratio must be one of {ratios} (tabulated values), "
            f"got {settlement_ratio}"
        )
    pb = _linterp(qc_mpa, _TABLE_D3_QC, _TABLE_D3[settlement_ratio])
    if enlarged_base:
        pb *= 0.75
    return {
        "settlement_ratio": settlement_ratio,
        "qc_mpa": qc_mpa,
        "pb_mpa": round(pb, 4),
    }


_TABLE_D4_QC = [0, 5, 10, 15]  # MPa (>15 clamped to 15's value)
_TABLE_D4_PS = [0.0, 0.040, 0.080, 0.120]


def table_d4_pile_shaft_resistance(qc_mpa: float) -> dict:
    """Unit shaft resistance of cast in-situ piles in coarse soil (Table D.4).

    Parameters
    ----------
    qc_mpa : float
        Average cone penetration resistance, in MPa.

    Returns
    -------
    dict
        Keys: qc_mpa, ps_mpa (unit shaft resistance).
    """
    ps = _linterp(qc_mpa, _TABLE_D4_QC, _TABLE_D4_PS)
    return {"qc_mpa": qc_mpa, "ps_mpa": round(ps, 4)}


# ============================================================================
# Annex D.7 / Table D.5: maximum values of alpha_p and alpha_s for sands and
# gravelly sands (Dutch CPT pile method, printed p.118)
# ============================================================================

_TABLE_D5 = {
    "driven_prefab": {"description": "Driven prefabricated piles",
                       "alpha_p": 1.0, "alpha_s": 0.010},
    "driven_cast_in_place_closed_tube": {
        "description": "Cast in place piles, driven closed-end steel tube reclaimed during concreting",
        "alpha_p": 1.0, "alpha_s": 0.012},
    "flight_auger": {"description": "Flight auger piles",
                      "alpha_p": 0.8, "alpha_s": 0.006},
    "bored_with_mud": {"description": "Bored piles (with drilling mud)",
                        "alpha_p": 0.6, "alpha_s": 0.005},
}


def table_d5_alpha_p_alpha_s_sand(pile_type: str) -> dict:
    """Maximum alpha_p, alpha_s for sands and gravelly sands (Table D.5).

    Used in the Dutch CPT pile method (Annex D.7) for maximum base
    resistance pmax;base = 0.5*alpha_p*beta*s*{...} and maximum shaft
    resistance pmax;shaft;z = alpha_s * qc;z;a.

    Parameters
    ----------
    pile_type : str
        'driven_prefab', 'driven_cast_in_place_closed_tube', 'flight_auger',
        or 'bored_with_mud'.

    Returns
    -------
    dict
        Keys: pile_type, description, alpha_p, alpha_s.  Note: values are
        valid for fine to coarse sands; apply a reduction factor of 0.75
        for very coarse sands, 0.5 for gravel.  alpha_s for flight_auger
        may be raised to 0.01 if CPTs were carried out in the vicinity of
        the flight auger piles (rather than before pile installation).

    Raises
    ------
    ValueError
        If pile_type is not recognized.
    """
    key = pile_type.strip().lower().replace(" ", "_").replace("-", "_")
    if key not in _TABLE_D5:
        raise ValueError(
            f"Unknown pile_type '{pile_type}'. "
            f"Valid: {', '.join(sorted(_TABLE_D5.keys()))}"
        )
    return {"pile_type": key, **_TABLE_D5[key]}


# ============================================================================
# Annex D.7 / Table D.6: maximum alpha_s values for clay, silt and peat
# (Dutch CPT pile method, printed p.119)
# ============================================================================

# Verified against the rendered page image (pdf idx 120, printed p.119) during
# lead QC 2026-07-15 — the OCR text layer had shifted the four rows by one
# (clay/silt/peat mis-assigned and peat's alpha_s = 0 lost). The printed table:
#   clay, qc > 3 MPa -> alpha_s < 0.030
#   clay, qc < 3 MPa -> alpha_s < 0.020
#   silt             -> alpha_s < 0.025
#   peat             -> alpha_s = 0   (no shaft resistance credited in peat)
_TABLE_D6 = {
    "clay": {"qc_threshold_mpa": 3.0, "alpha_s_above": 0.030,
             "alpha_s_below": 0.020},
    "silt": {"qc_threshold_mpa": None, "alpha_s_above": 0.025,
             "alpha_s_below": 0.025},
    "peat": {"qc_threshold_mpa": None, "alpha_s_above": 0.0,
             "alpha_s_below": 0.0},
}


def table_d6_alpha_s_clay_silt_peat(soil_type: str, qc_mpa: float = None) -> dict:
    """Maximum alpha_s for clay, silt and peat (Table D.6, Dutch CPT pile method).

    Parameters
    ----------
    soil_type : str
        'clay', 'silt', or 'peat'.
    qc_mpa : float, optional
        Cone resistance (MPa). Only clay is qc-banded (> 3 MPa -> 0.030,
        < 3 MPa -> 0.020); when omitted for clay, BOTH band values are
        returned and alpha_s_max conservatively reports the lower band.

    Returns
    -------
    dict
        Keys: soil_type, alpha_s_max (upper-bound design value of the
        shaft-resistance factor alpha_s in pmax;shaft;z = alpha_s * qc;z;a),
        plus alpha_s_qc_above_3 / alpha_s_qc_below_3 for clay. Peat returns
        0 — the table credits NO shaft resistance in peat.

    Raises
    ------
    ValueError
        If soil_type is not recognized.
    """
    key = soil_type.strip().lower()
    if key not in _TABLE_D6:
        raise ValueError(f"Unknown soil_type '{soil_type}'. Valid: clay, silt, peat")
    rec = _TABLE_D6[key]
    out = {"soil_type": key}
    if key == "clay":
        out["alpha_s_qc_above_3"] = rec["alpha_s_above"]
        out["alpha_s_qc_below_3"] = rec["alpha_s_below"]
        if qc_mpa is None:
            out["alpha_s_max"] = rec["alpha_s_below"]   # conservative
        else:
            out["alpha_s_max"] = (rec["alpha_s_above"] if qc_mpa > 3.0
                                  else rec["alpha_s_below"])
    else:
        out["alpha_s_max"] = rec["alpha_s_above"]
    return out


# ============================================================================
# Annex E.1 / Table E.1: bearing resistance factor k for spread foundations
# from Menard pressuremeter results (printed p.121; French Ministere de
# l'Equipement 1993)
# ============================================================================

_TABLE_E1 = {
    ("clay_and_silt", "a"): {"plm_range": "< 0.7 MPa", "base": 0.8, "coeff": 0.25},
    ("clay_and_silt", "b"): {"plm_range": "1.2-2.0 MPa", "base": 0.8, "coeff": 0.35},
    ("clay_and_silt", "c"): {"plm_range": "> ~2.5 MPa", "base": 0.8, "coeff": 0.50},
    ("sand_and_gravel", "a"): {"plm_range": "< 0.5 MPa", "base": 1.0, "coeff": 0.35},
    ("sand_and_gravel", "b"): {"plm_range": "1.0-2.0 MPa", "base": 1.0, "coeff": 0.50},
    ("sand_and_gravel", "c"): {"plm_range": "> 2.5 MPa", "base": 1.0, "coeff": 0.80},
    ("chalk", "a"): {"plm_range": "n/a", "base": 1.3, "coeff": 0.27},
    ("marl_and_weathered_rock", "a"): {"plm_range": "n/a", "base": 1.0, "coeff": 0.27},
}


def table_e1_pmt_bearing_factor_k(soil_category: str, plm_category: str,
                                   b_m: float, l_m: float, de_m: float) -> dict:
    """Bearing resistance factor k for spread foundations from PMT (Table E.1).

    k = base * [1 + coeff * (0.6 + 0.4*B/L) * De/B]

    Used in R = (A' * k * (PLM - p0)) + A' * sigma_v0 for the Menard
    pressuremeter semi-empirical bearing resistance method (Annex E.1).

    Parameters
    ----------
    soil_category : str
        'clay_and_silt', 'sand_and_gravel', 'chalk', or 'marl_and_weathered_rock'.
    plm_category : str
        'a', 'b', or 'c' (increasing Menard limit pressure PLM category;
        'chalk' and 'marl_and_weathered_rock' only have category 'a').
    b_m : float
        Foundation width B, in m.
    l_m : float
        Foundation length L, in m (L >= B).
    de_m : float
        Equivalent depth of foundation De, in m.

    Returns
    -------
    dict
        Keys: soil_category, plm_category, plm_range, k.

    Raises
    ------
    ValueError
        If soil_category/plm_category combination is not tabulated.
    """
    sc = soil_category.strip().lower().replace(" ", "_")
    pc = plm_category.strip().lower()
    key = (sc, pc)
    if key not in _TABLE_E1:
        raise ValueError(
            f"Unknown (soil_category, plm_category) combination '{key}'. "
            f"Valid soil_category: clay_and_silt, sand_and_gravel, chalk, "
            f"marl_and_weathered_rock"
        )
    row = _TABLE_E1[key]
    k = row["base"] * (1 + row["coeff"] * (0.6 + 0.4 * b_m / l_m) * de_m / b_m)
    return {
        "soil_category": sc,
        "plm_category": pc,
        "plm_range": row["plm_range"],
        "k": round(k, 4),
    }


# ============================================================================
# Annex E.2 / Table E.2: shape coefficients lambda_c, lambda_l for
# settlement of spread foundations from PMT (printed p.122)
# ============================================================================

# Verified against the rendered page image (pdf idx 123, printed p.122) during
# lead QC 2026-07-15. The printed columns are Circle | Square | L/B=2 | 3 | 5 | 20:
#   lambda_d: 1 | 1.12 | 1.53 | 1.78 | 2.14 | 2.65
#   lambda_c: 1 | 1.1  | 1.2  | 1.3  | 1.4  | 1.5
# (The prior encoding had dropped the 1.53 entry — shifting the lambda_d row —
# and resolved the L/B=20 lambda_c digit to 1.4; the page reads 1.5.)
_TABLE_E2_LB = [1, 2, 3, 5, 20]                     # square at L/B=1, then L/B
_TABLE_E2_LAMBDA_L = {"circle": [1.0, 1.0, 1.0, 1.0, 1.0],
                      "square": [1.12, 1.53, 1.78, 2.14, 2.65]}
_TABLE_E2_LAMBDA_C = {"circle": [1.0, 1.0, 1.0, 1.0, 1.0],
                      "square": [1.1, 1.2, 1.3, 1.4, 1.5]}


def table_e2_pmt_shape_coefficients(lb_ratio: float, shape: str = "square") -> dict:
    """Shape coefficients for settlement of spread foundations from PMT (Table E.2).

    Parameters
    ----------
    lb_ratio : float
        Foundation length-to-width ratio L/B (1 = circle/square).
    shape : str
        'circle' or 'square' (rectangular foundations use the square
        column per the standard's simplified table).  Ignored for
        lambda_c, which is shape-independent.

    Returns
    -------
    dict
        Keys: lb_ratio, lambda_c, lambda_l (interpolated).

    Raises
    ------
    ValueError
        If shape is not 'circle' or 'square', or lb_ratio < 1.
    """
    sh = shape.strip().lower()
    if sh not in _TABLE_E2_LAMBDA_L:
        raise ValueError(f"Unknown shape '{shape}'. Use circle or square")
    if lb_ratio < 1:
        raise ValueError(f"lb_ratio must be >= 1, got {lb_ratio}")
    lambda_l = _linterp(lb_ratio, _TABLE_E2_LB, _TABLE_E2_LAMBDA_L[sh])
    lambda_c = _linterp(lb_ratio, _TABLE_E2_LB, _TABLE_E2_LAMBDA_C[sh])
    return {
        "lb_ratio": lb_ratio,
        "shape": sh,
        "lambda_c": round(lambda_c, 4),
        "lambda_l": round(lambda_l, 4),
    }


# ============================================================================
# Annex E.2 / Table E.3: rheological factor alpha for settlement of spread
# foundations from PMT (printed p.122)
# ============================================================================

_TABLE_E3 = {
    "peat": {"description": "Peat", "em_plm_range": "-", "alpha": 1.0},
    "clay_over_consolidated": {"description": "Clay, over-consolidated", "em_plm_range": ">16", "alpha": 1.0},
    "clay_normally_consolidated": {"description": "Clay, normally consolidated", "em_plm_range": "9-16", "alpha": 0.67},
    "clay_remoulded": {"description": "Clay, remoulded", "em_plm_range": "7-9", "alpha": 0.5},
    "silt_over_consolidated": {"description": "Silt, over-consolidated", "em_plm_range": ">14", "alpha": 0.67},
    "silt_normally_consolidated": {"description": "Silt, normally consolidated", "em_plm_range": "5-14", "alpha": 0.5},
    "sand_dense": {"description": "Sand", "em_plm_range": ">12", "alpha": 0.5},
    "sand_loose": {"description": "Sand", "em_plm_range": "5-12", "alpha": 0.33},
    "sand_and_gravel_dense": {"description": "Sand and gravel", "em_plm_range": ">10", "alpha": 0.33},
    "sand_and_gravel_loose": {"description": "Sand and gravel", "em_plm_range": "6-10", "alpha": 0.25},
    "rock_extensively_fractured": {"description": "Rock, extensively fractured", "em_plm_range": "-", "alpha": 0.33},
    "rock_unaltered": {"description": "Rock, unaltered", "em_plm_range": "-", "alpha": 0.5},
    "rock_weathered": {"description": "Rock, weathered", "em_plm_range": "-", "alpha": 0.67},
}


def table_e3_pmt_rheological_factor(ground_type: str) -> dict:
    """Rheological factor alpha for settlement of spread foundations from PMT (Table E.3).

    Parameters
    ----------
    ground_type : str
        Ground type key, e.g. 'clay_normally_consolidated', 'sand_dense',
        'rock_weathered'.  See _TABLE_E3 keys for the full list.

    Returns
    -------
    dict
        Keys: ground_type, description, em_plm_range (typical EM/PLM
        ratio range used to select the row), alpha.

    Raises
    ------
    ValueError
        If ground_type is not recognized.
    """
    key = ground_type.strip().lower().replace(" ", "_")
    if key not in _TABLE_E3:
        raise ValueError(
            f"Unknown ground_type '{ground_type}'. "
            f"Valid: {', '.join(sorted(_TABLE_E3.keys()))}"
        )
    return {"ground_type": key, **_TABLE_E3[key]}


# ============================================================================
# Annex E.3 / Table E.4: compression resistance factor k for axially loaded
# piles from PMT (printed p.123)
# ============================================================================

_TABLE_E4 = {
    ("clay_and_silt", "a"): {"plm_range": "< 0.7 MPa", "k_bored": 1.1, "k_displacement": 1.4},
    ("clay_and_silt", "b"): {"plm_range": "1.2-2.0 MPa", "k_bored": 1.2, "k_displacement": 1.5},
    ("clay_and_silt", "c"): {"plm_range": "> 2.5 MPa", "k_bored": 1.3, "k_displacement": 1.6},
    ("sand_and_gravel", "a"): {"plm_range": "< 0.5 MPa", "k_bored": 1.0, "k_displacement": 4.2},
    ("sand_and_gravel", "b"): {"plm_range": "1.0-2.0 MPa", "k_bored": 1.1, "k_displacement": 3.7},
    ("sand_and_gravel", "c"): {"plm_range": "> 2.5 MPa", "k_bored": 1.2, "k_displacement": 3.2},
    ("chalk", "a"): {"plm_range": "< 0.7 MPa", "k_bored": 1.1, "k_displacement": 1.6},
    ("chalk", "b"): {"plm_range": "1.0-2.5 MPa", "k_bored": 1.4, "k_displacement": 2.2},
    ("chalk", "c"): {"plm_range": "> 3.0 MPa", "k_bored": 1.8, "k_displacement": 2.6},
}


def table_e4_pmt_pile_compression_factor(soil_category: str, plm_category: str,
                                          pile_type: str = "bored") -> dict:
    """Compression resistance factor k for axially loaded piles from PMT (Table E.4).

    Used in Q = k * A * (PLM - p0) + Cp * shaft resistance (Annex E.3).

    Parameters
    ----------
    soil_category : str
        'clay_and_silt', 'sand_and_gravel', or 'chalk'.
    plm_category : str
        'a', 'b', or 'c'.
    pile_type : str
        'bored' (bored piles and small displacement piles) or
        'displacement' (full displacement piles).

    Returns
    -------
    dict
        Keys: soil_category, plm_category, plm_range, pile_type, k.

    Raises
    ------
    ValueError
        If the combination is not tabulated or pile_type is invalid.
    """
    sc = soil_category.strip().lower().replace(" ", "_")
    pc = plm_category.strip().lower()
    pt = pile_type.strip().lower()
    if pt not in ("bored", "displacement"):
        raise ValueError(f"Unknown pile_type '{pile_type}'. Use bored or displacement")
    key = (sc, pc)
    if key not in _TABLE_E4:
        raise ValueError(
            f"Unknown (soil_category, plm_category) combination '{key}'. "
            f"Valid soil_category: clay_and_silt, sand_and_gravel, chalk"
        )
    row = _TABLE_E4[key]
    k = row["k_bored"] if pt == "bored" else row["k_displacement"]
    return {
        "soil_category": sc,
        "plm_category": pc,
        "plm_range": row["plm_range"],
        "pile_type": pt,
        "k": k,
    }


# ============================================================================
# Annex F.1 / Table F.1: correlation between normalised blow count (N1)60
# and density index ID for normally-consolidated natural sand deposits
# (printed p.125; Skempton 1986)
# ============================================================================

_TABLE_F1 = [
    # (density_category, n1_60_min, n1_60_max, id_min_pct, id_max_pct)
    ("very_loose", 0, 3, 0, 15),
    ("loose", 3, 8, 15, 35),
    ("medium", 8, 25, 35, 65),
    ("dense", 25, 42, 65, 85),
    ("very_dense", 42, 58, 85, 100),
]


def table_f1_density_index_from_n160(n1_60: float) -> dict:
    """Density index from normalised SPT blow count (N1)60 (Table F.1).

    Parameters
    ----------
    n1_60 : float
        Normalised SPT blow count (N1)60.  Valid range 0-58.

    Returns
    -------
    dict
        Keys: n1_60, density_category, id_min_pct, id_max_pct.

    Raises
    ------
    ValueError
        If n1_60 is outside the tabulated range 0-58.
    """
    if n1_60 < 0 or n1_60 > 58:
        raise ValueError(f"n1_60 must be 0-58, got {n1_60}")
    for category, n_min, n_max, id_min, id_max in _TABLE_F1:
        if n_min <= n1_60 <= n_max:
            return {
                "n1_60": n1_60,
                "density_category": category,
                "id_min_pct": id_min,
                "id_max_pct": id_max,
            }
    raise ValueError(f"No density category found for n1_60={n1_60}")  # pragma: no cover


# ============================================================================
# Annex F.1 / Table F.2: effect of ageing in normally consolidated fine
# sands, on the parameter a = (N1)60 / ID^2 (printed p.125)
# ============================================================================

_TABLE_F2 = {
    "laboratory_tests": {"age_years": 0.01, "n1_60_over_id2": 35},
    "recent_fills": {"age_years": 10, "n1_60_over_id2": 40},
    "natural_deposits": {"age_years": 100, "n1_60_over_id2": 55},
}


def table_f2_ageing_factor(deposit_type: str) -> dict:
    """Effect of ageing on normalised SPT blow count for fine sands (Table F.2).

    Parameters
    ----------
    deposit_type : str
        'laboratory_tests' (age ~10^-2 years), 'recent_fills' (~10 years),
        or 'natural_deposits' (>10^2 years).

    Returns
    -------
    dict
        Keys: deposit_type, age_years (representative value), n1_60_over_id2
        (the parameter a = (N1)60/ID^2, dimensionless).

    Raises
    ------
    ValueError
        If deposit_type is not recognized.
    """
    key = deposit_type.strip().lower().replace(" ", "_")
    if key not in _TABLE_F2:
        raise ValueError(
            f"Unknown deposit_type '{deposit_type}'. "
            f"Valid: laboratory_tests, recent_fills, natural_deposits"
        )
    return {"deposit_type": key, **_TABLE_F2[key]}


# ============================================================================
# Annex F.2 / Table F.3: correlation between density index ID and effective
# angle of shearing resistance phi' of silica sands (printed p.126;
# US Army Corps of Engineers 1993)
# ============================================================================

_TABLE_F3_ID = [40, 60, 80, 100]
_TABLE_F3 = {
    ("fine", "uniform"): [34, 36, 39, 42],
    ("fine", "well_graded"): [36, 38, 41, 43],
    ("medium", "uniform"): [36, 38, 41, 43],
    ("medium", "well_graded"): [38, 41, 43, 44],
    ("coarse", "uniform"): [41, 41, 43, 44],
    ("coarse", "well_graded"): [43, 43, 44, 46],
}


def table_f3_phi_from_density_index(density_index_pct: float, grain_size: str,
                                     grading: str) -> dict:
    """Effective angle of shearing resistance of silica sands from ID (Table F.3).

    Parameters
    ----------
    density_index_pct : float
        Density index ID, in percent (0-100; clamped at endpoints 40-100).
    grain_size : str
        'fine', 'medium', or 'coarse'.
    grading : str
        'uniform' or 'well_graded'.

    Returns
    -------
    dict
        Keys: density_index_pct, grain_size, grading, phi_deg (interpolated).

    Raises
    ------
    ValueError
        If grain_size/grading is not recognized.
    """
    gs = grain_size.strip().lower()
    gr = grading.strip().lower().replace(" ", "_").replace("-", "_")
    key = (gs, gr)
    if key not in _TABLE_F3:
        raise ValueError(
            f"Unknown (grain_size, grading) combination '{key}'. "
            f"grain_size: fine, medium, coarse; grading: uniform, well_graded"
        )
    phi = _linterp(density_index_pct, _TABLE_F3_ID, _TABLE_F3[key])
    return {
        "density_index_pct": density_index_pct,
        "grain_size": gs,
        "grading": gr,
        "phi_deg": round(phi, 2),
    }


# ============================================================================
# Annex G.2 / Table G.1: effective angle of shearing resistance of coarse
# soil from density index (DP test), by grading and Cu (printed p.129;
# DIN 1054-100)
# ============================================================================

_TABLE_G1 = {
    ("poorly_graded", "loose"): {"id_range": "15-35%", "phi_deg": 30},
    ("poorly_graded", "medium_dense"): {"id_range": "35-65%", "phi_deg": 32.5},
    ("poorly_graded", "dense"): {"id_range": ">65%", "phi_deg": 35},
    ("well_graded", "loose"): {"id_range": "15-35%", "phi_deg": 30},
    ("well_graded", "medium_dense"): {"id_range": "35-65%(assumed)", "phi_deg": 34},
    ("well_graded", "dense"): {"id_range": ">65%(assumed)", "phi_deg": 38},
}


def table_g1_phi_from_density_index_dp(grading: str, density_state: str) -> dict:
    """Effective angle of shearing resistance of coarse soil from DP (Table G.1).

    Parameters
    ----------
    grading : str
        'poorly_graded' (Cu < 6, e.g. sand/sand-gravel) or 'well_graded'
        (6 <= Cu <= 15, e.g. sand/sand-gravel/gravel).
    density_state : str
        'loose', 'medium_dense', or 'dense'.

    Returns
    -------
    dict
        Keys: grading, density_state, id_range, phi_deg.

    Raises
    ------
    ValueError
        If grading/density_state is not recognized.
    """
    gr = grading.strip().lower().replace(" ", "_").replace("-", "_")
    ds = density_state.strip().lower().replace(" ", "_")
    key = (gr, ds)
    if key not in _TABLE_G1:
        raise ValueError(
            f"Unknown (grading, density_state) combination '{key}'. "
            f"grading: poorly_graded, well_graded; "
            f"density_state: loose, medium_dense, dense"
        )
    return {"grading": gr, "density_state": ds, **_TABLE_G1[key]}


# ============================================================================
# Annex H / Table H.1: effective angle of shearing resistance and drained
# Young's modulus from weight sounding test (WST) resistance, Swedish
# experience (printed p.132; Bergdahl et al. 1993)
# ============================================================================

_TABLE_H1 = [
    # (density_index, wst_min_halfturns, wst_max_halfturns, phi_min, phi_max, e_min_mpa, e_max_mpa)
    ("very_loose", 0, 10, 29, 32, None, 10),
    ("loose", 10, 30, 32, 35, 10, 20),
    ("medium_dense", 20, 50, 35, 37, 20, 30),
    ("dense", 40, 90, 37, 40, 30, 60),
    ("very_dense", 80, None, 40, 42, 60, 90),
]


def table_h1_phi_e_from_wst(density_category: str, soil_type: str = "sand") -> dict:
    """Effective angle of shearing resistance and drained modulus from WST (Table H.1).

    Example correlation for naturally deposited quartz and feldspar sands
    (Swedish experience), keyed by qualitative density category since the
    WST resistance ranges overlap between categories in the source table.

    Parameters
    ----------
    density_category : str
        'very_loose', 'loose', 'medium_dense', 'dense', or 'very_dense'.
    soil_type : str
        'sand' (as tabulated), 'silty' (phi' reduced 3 deg per note),
        or 'gravelly' (phi' increased 2 deg per note).

    Returns
    -------
    dict
        Keys: density_category, wst_halfturns_range (per 0.2 m penetration),
        phi_min_deg, phi_max_deg, e_min_mpa, e_max_mpa, soil_type.
        Per the standard: if only WST results are available, use the lower
        value of each interval (conservative).

    Raises
    ------
    ValueError
        If density_category or soil_type is not recognized.
    """
    st = soil_type.strip().lower()
    if st not in ("sand", "silty", "gravelly"):
        raise ValueError(f"Unknown soil_type '{soil_type}'. Use sand, silty, or gravelly")
    key = density_category.strip().lower().replace(" ", "_")
    for category, wst_min, wst_max, phi_min, phi_max, e_min, e_max in _TABLE_H1:
        if category == key:
            if st == "silty":
                phi_min, phi_max = phi_min - 3, phi_max - 3
            elif st == "gravelly":
                phi_min, phi_max = phi_min + 2, phi_max + 2
            return {
                "density_category": category,
                "wst_halfturns_min": wst_min,
                "wst_halfturns_max": wst_max,
                "phi_min_deg": phi_min,
                "phi_max_deg": phi_max,
                "e_min_mpa": e_min,
                "e_max_mpa": e_max,
                "soil_type": st,
            }
    raise ValueError(
        f"Unknown density_category '{density_category}'. "
        f"Valid: very_loose, loose, medium_dense, dense, very_dense"
    )


# ============================================================================
# Annex L / Table L.1 (partial): minimum mass of soil required for tests on
# disturbed samples (printed p.143; selected rows -- water content, particle
# density, consistency limits, density index)
# ============================================================================

_TABLE_L1 = {
    "water_content": {"initial_mass": "at least twice specimen mass",
                       "clay_silt_g": 30, "sand_g": 100,
                       "gravelly_soil": "0.3 x MMS, min 500 g"},
    "particle_density": {"initial_mass": "100 g",
                          "clay_silt_g": 10, "sand_g": None,
                          "gravelly_soil": None,
                          "note": "particle size < 4 mm"},
    "consistency_limits": {"initial_mass": "500 g",
                            "clay_silt_g": 300, "sand_g": None,
                            "gravelly_soil": None,
                            "note": "particle size < 0.4 mm"},
    "density_index": {"initial_mass": "8 kg",
                       "clay_silt_g": None, "sand_g": None,
                       "gravelly_soil": None},
}


def table_l1_sample_mass(test: str) -> dict:
    """Minimum mass of disturbed soil required for testing (Table L.1, partial).

    Parameters
    ----------
    test : str
        'water_content', 'particle_density', 'consistency_limits', or
        'density_index'.

    Returns
    -------
    dict
        Keys: test, initial_mass, clay_silt_g, sand_g, gravelly_soil
        (minimum prepared test specimen masses by soil type).

    Raises
    ------
    ValueError
        If test is not recognized.
    """
    key = test.strip().lower().replace(" ", "_")
    if key not in _TABLE_L1:
        raise ValueError(
            f"Unknown test '{test}'. "
            f"Valid: {', '.join(sorted(_TABLE_L1.keys()))}"
        )
    return {"test": key, **_TABLE_L1[key]}


# ============================================================================
# Annex L / Table L.2: minimum mass for sieving (MMS), by largest particle
# diameter (printed p.145)
# ============================================================================

_TABLE_L2_D_MM = [2, 4, 10, 16, 20, 31.5, 37.5, 45, 63, 75]
_TABLE_L2_MMS_KG = [0.1, 0.2, 0.5, 0.6, 2, 15, 25, 25, 70, 120]
# NOTE: below 2 mm the standard tabulates grams (100 g at D<=2mm, 150 g at
# 2.8mm, 200 g at 4mm, 250 g at 5.6mm, 400 g at 8mm, 500 g at 10mm,
# 600 g at 11.2mm) as a separate fine sub-table; this lookup covers the
# coarser (kg) sub-table from D=2mm upward for the primary particle sizes.


def table_l2_min_mass_sieving(largest_particle_mm: float) -> dict:
    """Minimum mass for sieving (MMS) by largest particle diameter (Table L.2).

    Parameters
    ----------
    largest_particle_mm : float
        Largest particle diameter present in significant proportion
        (10% or more by dry mass), in mm.  Valid range 2-75 mm (the kg
        sub-table; see note for the finer gram-scale sub-table).

    Returns
    -------
    dict
        Keys: largest_particle_mm, mms_kg (interpolated minimum mass for
        sieving).

    Raises
    ------
    ValueError
        If largest_particle_mm is outside 2-75 mm.
    """
    if largest_particle_mm < 2 or largest_particle_mm > 75:
        raise ValueError(
            f"largest_particle_mm must be 2-75 (kg sub-table), got {largest_particle_mm}"
        )
    mms = _linterp(largest_particle_mm, _TABLE_L2_D_MM, _TABLE_L2_MMS_KG)
    return {"largest_particle_mm": largest_particle_mm, "mms_kg": round(mms, 3)}


# ============================================================================
# Minimum recommended test counts (Annexes M, P, Q, S, W).  These share the
# "variability x comparable experience" 3x3 structure of EN 1997-2's
# guidance tables; each test family is tabulated separately since the
# variability criterion differs by test type.
# ============================================================================

_TABLE_M1_CLASSIFICATION = {
    # test: (count_no_experience, count_with_experience)
    "particle_size_distribution": (6, 4),  # "4-6" / "2-4": using max of each range
    "consistency_limits": (5, 3),
    "loss_on_ignition": (3, 1),
}


def table_m1_classification_test_count(test: str, comparable_experience: bool) -> dict:
    """Minimum number of classification tests per soil stratum (Table M.1).

    Parameters
    ----------
    test : str
        'particle_size_distribution', 'consistency_limits', or
        'loss_on_ignition'.
    comparable_experience : bool
        True if comparable local experience exists, False otherwise.

    Returns
    -------
    dict
        Keys: test, comparable_experience, min_count_range (printed as
        "lo-hi" upper/lower recommended count from the standard's range).

    Raises
    ------
    ValueError
        If test is not recognized.
    """
    key = test.strip().lower().replace(" ", "_")
    if key not in _TABLE_M1_CLASSIFICATION:
        raise ValueError(
            f"Unknown test '{test}'. "
            f"Valid: {', '.join(sorted(_TABLE_M1_CLASSIFICATION.keys()))}"
        )
    hi, lo = _TABLE_M1_CLASSIFICATION[key]
    count = lo if comparable_experience else hi
    return {
        "test": key,
        "comparable_experience": comparable_experience,
        "min_count": count,
    }


_VARIABILITY_TEST_COUNTS = {
    # test_family: {variability_tier: {experience_tier: count}}
    "triaxial_phi": {  # Table P.1, printed p.163 (correlation coefficient r)
        "low": {"none": 2, "medium": 1, "extensive": 1},   # r >= 0.98
        "medium": {"none": 3, "medium": 2, "extensive": 1},  # 0.95 < r <= 0.98
        "high": {"none": 4, "medium": 3, "extensive": 2},  # r <= 0.95
    },
    "triaxial_su": {  # Table P.1, printed p.163 (max/min ratio)
        "low": {"none": 3, "medium": 2, "extensive": 1},  # ratio <= 1.25
        "medium": {"none": 4, "medium": 3, "extensive": 2},  # 1.25 < ratio <= 2
        "high": {"none": 6, "medium": 4, "extensive": 3},  # ratio > 2
    },
    "direct_shear": {  # Table P.2, printed p.164
        "low": {"none": 2, "medium": 2, "extensive": 1},  # r >= 0.98
        "medium": {"none": 3, "medium": 2, "extensive": 2},  # 0.95 <= r < 0.98
        "high": {"none": 4, "medium": 3, "extensive": 2},  # r < 0.95
    },
    "oedometer": {  # Table Q.1, printed p.166
        "low": {"none": 2, "medium": 2, "extensive": 1},  # range < ~20%
        "medium": {"none": 3, "medium": 2, "extensive": 2},  # ~20-50%
        "high": {"none": 4, "medium": 3, "extensive": 2},  # range > ~50%
    },
    "permeability": {  # Table S.1, printed p.169
        "low": {"none": 3, "medium": 2, "extensive": 1},  # kmax/kmin <= 10
        "medium": {"none": 5, "medium": 3, "extensive": 2},  # 10 < ratio <= 100
        "high": {"none": 5, "medium": 4, "extensive": 3},  # ratio > 100
    },
    "rock_uniaxial_compression": {  # Table W.1, printed p.177 (also used
        # for Brazil and triaxial tests on rock per Annex W)
        "low": {"none": 2, "medium": 1, "extensive": 0},  # s < 20
        "medium": {"none": 3, "medium": 2, "extensive": 1},  # 20 < s < 50
        "high": {"none": 6, "medium": 4, "extensive": 2},  # s > 50
    },
}


def table_min_test_count(test_family: str, variability: str,
                          comparable_experience: str) -> dict:
    """Recommended minimum number of tests for one stratum/formation.

    Consolidates the "variability x comparable experience" minimum test
    count tables from Annexes P (triaxial, direct shear), Q (oedometer),
    S (permeability), and W (rock uniaxial compression/Brazil/triaxial).

    Parameters
    ----------
    test_family : str
        'triaxial_phi' (Table P.1, by regression coefficient r),
        'triaxial_su' (Table P.1, by max/min undrained strength ratio),
        'direct_shear' (Table P.2), 'oedometer' (Table Q.1, by Eoed
        range), 'permeability' (Table S.1, by kmax/kmin ratio), or
        'rock_uniaxial_compression' (Table W.1, by standard deviation of
        strength as % of mean; also governs Brazil and triaxial rock
        tests per the standard).
    variability : str
        'low', 'medium', or 'high' (see each family's docstring criterion
        above for the exact numeric boundary).
    comparable_experience : str
        'none', 'medium', or 'extensive'.

    Returns
    -------
    dict
        Keys: test_family, variability, comparable_experience, min_count.
        Note: one recommended triaxial/direct-shear "test" = a set of
        three individual specimens at different confining/normal stresses.

    Raises
    ------
    ValueError
        If any parameter is not recognized.
    """
    fam = test_family.strip().lower().replace(" ", "_")
    if fam not in _VARIABILITY_TEST_COUNTS:
        raise ValueError(
            f"Unknown test_family '{fam}'. "
            f"Valid: {', '.join(sorted(_VARIABILITY_TEST_COUNTS.keys()))}"
        )
    var = variability.strip().lower()
    exp = comparable_experience.strip().lower()
    table = _VARIABILITY_TEST_COUNTS[fam]
    if var not in table:
        raise ValueError(f"Unknown variability '{variability}'. Use low, medium, or high")
    if exp not in table[var]:
        raise ValueError(
            f"Unknown comparable_experience '{comparable_experience}'. "
            f"Use none, medium, or extensive"
        )
    return {
        "test_family": fam,
        "variability": var,
        "comparable_experience": exp,
        "min_count": table[var][exp],
    }


# ============================================================================
# Annex N.3/N.4: chemical-test unit-conversion factors (printed p.159)
# See equations.py: equation_n_caco3_from_co2(), equation_n_so4_from_so3()
# ============================================================================


# ============================================================================
# Annex V / Table V.1: minimum number of rock swelling test specimens
# (printed p.173)
# ============================================================================

_TABLE_V1 = {
    "swelling_pressure_zero_volume_change": {
        "min_thickness_mm": 15, "min_diameter_ratio": "2.5x thickness",
        "min_specimens": 3,
    },
    "swelling_strain_radially_confined_axial_surcharge": {
        "min_thickness_mm": 15, "min_diameter_ratio": "4x thickness",
        "min_specimens": "3 + duplicates for water content",
    },
    "swelling_strain_unconfined": {
        "min_thickness_mm": 15, "min_diameter_ratio": "10x max particle size",
        "min_specimens": "3 + duplicates for water content",
    },
}


def table_v1_swelling_test_specimens(test_type: str) -> dict:
    """Minimum rock swelling test specimen requirements (Table V.1).

    Values apply to sites with limited risk of swelling rock; double the
    specimen count at sites more likely to be subject to swelling.

    Parameters
    ----------
    test_type : str
        'swelling_pressure_zero_volume_change',
        'swelling_strain_radially_confined_axial_surcharge', or
        'swelling_strain_unconfined'.

    Returns
    -------
    dict
        Keys: test_type, min_thickness_mm, min_diameter_ratio, min_specimens.

    Raises
    ------
    ValueError
        If test_type is not recognized.
    """
    key = test_type.strip().lower().replace(" ", "_")
    if key not in _TABLE_V1:
        raise ValueError(
            f"Unknown test_type '{test_type}'. "
            f"Valid: {', '.join(sorted(_TABLE_V1.keys()))}"
        )
    return {"test_type": key, **_TABLE_V1[key]}
