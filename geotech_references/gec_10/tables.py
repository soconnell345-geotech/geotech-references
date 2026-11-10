"""GEC-10 table lookup functions.

Tables from FHWA-NHI-18-024 (GEC-10, 2018 edition), Drilled Shafts:
Construction Procedures and Design Methods.  Resistance factors are
consistent with AASHTO LRFD Bridge Design Specifications (2017a) except for
lateral resistance, where this manual recommends 0.67/0.80 rather than the
AASHTO default of 1.0 (see Section 8.1 and Table 9-1).
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Table 8-4: Resistance Factors for LRFD Design of Drilled Shafts
# (FHWA-NHI-18-024 Table 8-4, consistent with AASHTO 2017a except lateral)
#
# Format for axial side resistance entries: compression / uplift (no load test)
# ============================================================================

_TABLE_8_4 = {
    # --- Lateral geotechnical resistance (from Table 9-1) ---
    "lateral_individual": {
        "phi": 0.67,
        "condition": "Individual elastic shaft or single-row wall, head free; p-y pushover",
        "category": "lateral",
    },
    "lateral_group": {
        "phi": 0.80,
        "condition": "Elastic shaft in multiple-row group with moment connection to cap; p-y pushover",
        "category": "lateral",
    },
    # --- Side resistance: compression / uplift (without load test) ---
    "side_cohesionless_compression": {
        "phi": 0.55,
        "condition": "Cohesionless soil, Beta method, compression (without load test)",
        "category": "compression_side",
    },
    "side_cohesionless_uplift": {
        "phi": 0.45,
        "condition": "Cohesionless soil, Beta method, uplift (without load test)",
        "category": "uplift_side",
    },
    "side_cohesive_compression": {
        "phi": 0.45,
        "condition": "Cohesive soil, Alpha method, compression (without load test)",
        "category": "compression_side",
    },
    "side_cohesive_uplift": {
        "phi": 0.35,
        "condition": "Cohesive soil, Alpha method, uplift (without load test)",
        "category": "uplift_side",
    },
    "side_rock_compression": {
        "phi": 0.50,
        "condition": "Rock, Eq. 10-21, compression (without load test)",
        "category": "compression_side",
    },
    "side_rock_uplift": {
        "phi": 0.40,
        "condition": "Rock, Eq. 10-21, uplift (without load test)",
        "category": "uplift_side",
    },
    "side_igm_compression": {
        "phi": 0.60,
        "condition": "Cohesive IGM, modified alpha method, compression (without load test)",
        "category": "compression_side",
    },
    "side_igm_uplift": {
        "phi": 0.50,
        "condition": "Cohesive IGM, modified alpha method, uplift (without load test)",
        "category": "uplift_side",
    },
    # --- Base resistance: compression only (without load test) ---
    "base_cohesionless": {
        "phi": 0.50,
        "condition": "Cohesionless soil, N-value method (Eq. 10-14), compression",
        "category": "compression_base",
    },
    "base_cohesive": {
        "phi": 0.40,
        "condition": "Cohesive soil, bearing capacity eq., compression",
        "category": "compression_base",
    },
    "base_rock": {
        "phi": 0.50,
        "condition": "Rock, Eq. 10-23 or Eq. 10-29, compression",
        "category": "compression_base",
    },
    # --- Load test ---
    "load_test_compression": {
        "phi": 0.70,
        "condition": "Static compressive resistance from load test, all geomaterials",
        "category": "load_test",
    },
    "load_test_uplift": {
        "phi": 0.60,
        "condition": "Static uplift resistance from load test, all geomaterials",
        "category": "load_test",
    },
    # --- Group effects ---
    "group_block_failure": {
        "phi": 0.55,
        "condition": "Group block failure mode, cohesive soil",
        "category": "group",
    },
    "group_uplift": {
        "phi": 0.45,
        "condition": "Group uplift resistance, cohesive and cohesionless soil",
        "category": "group",
    },
    # --- Structural resistance (reinforced concrete) ---
    "structural_compression": {
        "phi": 0.75,
        "condition": "Axial compression, reinforced concrete",
        "category": "structural",
    },
    "structural_flexure": {
        "phi": 0.75,
        "phi_max": 0.90,
        "condition": ("Combined axial and flexure, reinforced concrete; "
                      "printed 0.75 to 0.90 (phi is the lower value, "
                      "phi_max the upper)"),
        "category": "structural",
    },
    "structural_shear": {
        "phi": 0.90,
        "condition": "Shear, reinforced concrete",
        "category": "structural",
    },
    # --- Service I ---
    "service": {
        "phi": 1.00,
        "condition": "Service I, all cases, all geomaterials",
        "category": "service",
    },
    # --- Extreme Event I and II ---
    "extreme_uplift": {
        "phi": 0.80,
        "condition": "Axial geotechnical uplift, Extreme Event I and II",
        "category": "extreme",
    },
    "extreme_lateral": {
        "phi": 0.80,
        "condition": "Geotechnical lateral resistance, Extreme Event I and II; p-y pushover",
        "category": "extreme",
    },
    "extreme_other": {
        "phi": 1.00,
        "condition": "All other resistance components, Extreme Event I and II",
        "category": "extreme",
    },
}


# Other names of ONE row of Table 8-4 (p. 8-14). A word that fits several
# rows ('side', 'uplift', 'rock', 'load_test', 'structural') is refused.
_TABLE_8_4_ALIASES = {
    "lateral_single_row": "lateral_individual",
    "lateral_single": "lateral_individual",
    "lateral_multiple_row_group": "lateral_group",
    "group_block": "group_block_failure",
    "group_uplift_resistance": "group_uplift",
    "static_compressive_resistance_from_load_tests": "load_test_compression",
    "static_uplift_resistance_from_load_tests": "load_test_uplift",
    "structural_axial_compression": "structural_compression",
    "structural_combined_axial_and_flexure": "structural_flexure",
    "structural_axial_flexure": "structural_flexure",
    "service_i": "service",
    "extreme_axial_uplift": "extreme_uplift",
    "extreme_all_other": "extreme_other",
}


def table_8_4_resistance_factor(method: str) -> dict:
    """Resistance factor phi for one row of GEC-10 Table 8-4 Resistance Factors for LRFD Design of Drilled Shafts (FHWA-NHI-18-024, p. 8-14); the key must name one printed row.

    Covers lateral, axial (side and base), load test, group, structural,
    service, and extreme event limit states. Side resistance prints
    compression / uplift (e.g. 0.55 / 0.45), one key each:
    'side_<geomaterial>_compression' or 'side_<geomaterial>_uplift'.
    Use 'load_test_compression' (phi = 0.70) or 'load_test_uplift'
    (phi = 0.60) when static load tests are performed.

    Parameters
    ----------
    method : str
        One printed row: 'lateral_individual', 'lateral_group',
        'side_cohesionless_compression', 'side_cohesionless_uplift',
        'side_cohesive_compression', 'side_cohesive_uplift',
        'side_rock_compression', 'side_rock_uplift', 'side_igm_compression',
        'side_igm_uplift', 'base_cohesionless', 'base_cohesive',
        'base_rock', 'load_test_compression', 'load_test_uplift',
        'group_block_failure', 'group_uplift', 'structural_compression',
        'structural_flexure', 'structural_shear', 'service',
        'extreme_uplift', 'extreme_lateral', 'extreme_other', or a listed
        alias ('group_block', 'service_i', ...).

    Returns
    -------
    dict
        {'method': str, 'phi': float, 'condition': str, 'category': str};
        'structural_flexure' adds 'phi_max' (printed 0.75 to 0.90).

    Raises
    ------
    ValueError
        If method does not name one printed row (a word found in several
        rows, such as 'side' or 'uplift', was answered from the first).
    """
    key = method.lower().strip().replace(" ", "_").replace("-", "_")
    key = _TABLE_8_4_ALIASES.get(key, key)

    if key in _TABLE_8_4:
        result = dict(_TABLE_8_4[key])
        result["method"] = key
        return result

    available = ", ".join(sorted(_TABLE_8_4.keys()))
    raise ValueError(
        f"No matching method for '{method}': Table 8-4 (p. 8-14) keys name "
        f"one printed row.\nAvailable: {available}"
    )


_TABLE_8_4_CATEGORIES = ("lateral", "compression_side", "uplift_side",
                         "compression_base", "load_test", "group",
                         "structural", "service", "extreme")


def table_8_4_by_category(category: str) -> list:
    """All rows of GEC-10 Table 8-4 (FHWA-NHI-18-024, p. 8-14) in one of the library's categories, each with its resistance factor phi.

    Parameters
    ----------
    category : str
        'lateral', 'compression_side', 'uplift_side', 'compression_base',
        'load_test', 'group', 'structural', 'service', 'extreme', or ''
        for all rows.

    Returns
    -------
    list of dict
        All entries in the category, each with 'method', 'phi',
        'condition', and 'category' keys.

    Raises
    ------
    ValueError
        If category is not one of the listed names (an unknown word
        returned an empty list; a part of a name, such as 'side', every
        category holding it).
    """
    cat = category.lower().strip().replace(" ", "_").replace("-", "_")
    if cat and cat not in _TABLE_8_4_CATEGORIES:
        raise ValueError(
            f"Unknown category '{category}'. Options: "
            f"{', '.join(_TABLE_8_4_CATEGORIES)}, or '' for all rows."
        )
    results = []
    for k, v in _TABLE_8_4.items():
        if not cat or v["category"] == cat:
            entry = dict(v)
            entry["method"] = k
            results.append(entry)
    return results


# ============================================================================
# Table 9-1: Recommended Resistance Factors for Lateral Loading
# (FHWA-NHI-18-024 Table 9-1; p-y pushover analysis method)
# ============================================================================

_TABLE_9_1 = {
    "individual": {
        "phi": 0.67,
        "description": "Individual elastic shaft or single-row wall, free to rotate at head",
    },
    "group": {
        "phi": 0.80,
        "description": "Elastic shaft in multiple-row group, moment connection to cap",
    },
    "extreme": {
        "phi": 0.80,
        "description": "Extreme event strength cases (seismic, vessel impact, etc.)",
    },
}


def table_9_1_lateral_resistance_factor(method: str) -> dict:
    """Resistance factor phi for geotechnical strength of laterally loaded drilled shafts by the p-y method, GEC-10 Table 9-1 (FHWA-NHI-18-024, p. 9-22); the key must name one of its three rows.

    Based on p-y method static pushover analysis.  AASHTO (2017a) specifies
    φ = 1.0 for lateral resistance; this manual recommends lower values
    (0.67 or 0.80) to ensure ductile response and adequate reserve capacity.

    Parameters
    ----------
    method : str
        Loading condition: 'individual' (or 'single'), 'group', or 'extreme'.

    Returns
    -------
    dict
        {'method': str, 'phi': float, 'description': str}

    Raises
    ------
    ValueError
        If method is not recognized.
    """
    _aliases = {
        "individual": "individual",
        "single": "individual",
        "single_row": "individual",
        "retaining_wall": "individual",
        "abutment": "individual",
        "free_head": "individual",
        "group": "group",
        "multi_row": "group",
        "moment_connection": "group",
        "extreme": "extreme",
        "extreme_event": "extreme",
        "seismic": "extreme",
    }

    key = method.lower().strip().replace(" ", "_").replace("-", "_")
    resolved = _aliases.get(key)

    if resolved is None or resolved not in _TABLE_9_1:
        raise ValueError(
            f"Unknown method '{method}'. "
            f"Use: 'individual', 'group', or 'extreme'."
        )

    result = dict(_TABLE_9_1[resolved])
    result["method"] = resolved
    return result


# ============================================================================
# Table 10-2: Bearing Capacity Factor N*c for Base Resistance in Cohesive Soil
# (FHWA-NHI-18-024 Table 10-2)
#
# For L/B ≥ 3: qBN = N*c × su
# For L/B < 3: qBN = (2/3)(1 + L/(6B)) × N*c × su  (Equation 10-20)
# su = mean undrained shear strength over depth 2B below base
# ============================================================================

_TABLE_10_2_SU_PSF = [0.0, 500.0, 1000.0, 2000.0]
_TABLE_10_2_NC     = [6.50,  6.50,   8.00,   9.00]


def table_10_2_nc_base_clay(su_psf: float) -> dict:
    """Bearing capacity factor N*c for drilled shaft base resistance in cohesive soil (Table 10-2).

    N*c is the dimensionless bearing capacity factor used in:

        qBN = N*c × su  (for L/B ≥ 3)

    where su is the mean CIUC-equivalent undrained shear strength over a
    depth of 2B below the shaft base.  For shallow embedment (L/B < 3), apply
    the reduction from Equation 10-20:

        qBN = (2/3)(1 + L/(6B)) × N*c × su

    Resistance factor (Table 8-4): φ = 0.40 (compression).

    Parameters
    ----------
    su_psf : float
        Mean undrained shear strength at the base in lb/ft² (psf).  Must be
        positive.  Values above 2,000 psf return N*c = 9.0.

    Returns
    -------
    dict
        {'su_psf': float, 'nc_star': float,
         'note': str}

    Raises
    ------
    ValueError
        If su_psf is not positive.
    """
    if su_psf <= 0:
        raise ValueError(f"su_psf must be positive, got {su_psf}")

    if su_psf >= _TABLE_10_2_SU_PSF[-1]:
        nc = _TABLE_10_2_NC[-1]
        note = "su >= 2000 psf; N*c = 9.0 (maximum value per Table 10-2)"
    elif su_psf <= _TABLE_10_2_SU_PSF[1]:
        nc = _TABLE_10_2_NC[1]
        note = "su <= 500 psf; N*c = 6.5 (minimum tabulated value)"
    else:
        nc = _linterp(su_psf, _TABLE_10_2_SU_PSF, _TABLE_10_2_NC)
        note = "interpolated from Table 10-2"

    return {
        "su_psf": su_psf,
        "nc_star": round(nc, 3),
        "note": note,
    }


# ============================================================================
# Table 11-1: Recommended P-Multiplier Pm Values for Lateral Group Analysis
# (FHWA-NHI-18-024 Table 11-1; Brown et al. 1987, 2001)
# ============================================================================

_TABLE_11_1_SPACING = [3.0, 4.0, 5.0, 6.0]

_TABLE_11_1 = {
    "lead_row": {
        "pm": [0.70, 0.85, 1.00, 1.00],
        "notes": "Lead (front) row — least affected by group shadowing",
    },
    "2nd_row": {
        "pm": [0.50, 0.65, 0.85, 1.00],
        "notes": "Second row",
    },
    "3rd_or_more_row": {
        "pm": [0.35, 0.50, 0.70, 1.00],
        "notes": "Third and all subsequent (trailing) rows",
    },
}


def table_11_1_p_multiplier(row_position: str,
                              spacing_over_d: float) -> dict:
    """P-multiplier Pm for lateral group analysis (Table 11-1).

    Scales the p-y resistance of each shaft in a group:

        p_group = Pm × p_single

    Values recommended by Brown et al. (1987, 2001) and tabulated in Table
    11-1.  Input the center-to-center shaft spacing divided by shaft diameter.
    Pm = 1.0 for all rows at spacing ≥ 6D.

    Parameters
    ----------
    row_position : str
        Row position: 'lead' (or '1st', 'front'), '2nd' (or 'second'),
        '3rd' (or 'trail', 'trailing', '3rd_or_more').
    spacing_over_d : float
        Center-to-center shaft spacing ÷ shaft diameter.  Must be ≥ 3.0.

    Returns
    -------
    dict
        {'row_position': str, 'spacing_over_d': float,
         'pm': float, 'notes': str}

    Raises
    ------
    ValueError
        If row_position is unrecognized or spacing < 3.0.
    """
    if spacing_over_d < 3.0:
        raise ValueError(
            f"spacing_over_d={spacing_over_d} is below the minimum of 3.0D."
        )

    _aliases = {
        "lead": "lead_row",
        "lead_row": "lead_row",
        "front": "lead_row",
        "1st": "lead_row",
        "1st_row": "lead_row",
        "first": "lead_row",
        "2nd": "2nd_row",
        "2nd_row": "2nd_row",
        "second": "2nd_row",
        "3rd": "3rd_or_more_row",
        "3rd_row": "3rd_or_more_row",
        "3rd_or_more": "3rd_or_more_row",
        "3rd_or_more_row": "3rd_or_more_row",
        "trail": "3rd_or_more_row",
        "trailing": "3rd_or_more_row",
        "4th": "3rd_or_more_row",
        "5th": "3rd_or_more_row",
    }

    key = row_position.lower().strip().replace(" ", "_").replace("-", "_")
    row_key = _aliases.get(key)
    if row_key is None:
        raise ValueError(
            f"Unknown row_position '{row_position}'. "
            "Use: 'lead', '2nd', '3rd' (or 'trail')."
        )

    data = _TABLE_11_1[row_key]

    if spacing_over_d >= _TABLE_11_1_SPACING[-1]:
        pm = 1.0
    else:
        pm = _linterp(spacing_over_d, _TABLE_11_1_SPACING, data["pm"])

    return {
        "row_position": row_key,
        "spacing_over_d": spacing_over_d,
        "pm": round(pm, 3),
        "notes": data["notes"],
    }


# ============================================================================
# Group efficiency for drilled shafts in cohesionless soils
# FHWA-NHI-18-024 Section 11.4.1.2 Cohesionless Soils, p. 11-6 (PDF page 340),
# citing AASHTO (2017a) 10.8.3.6.3. GEC-10 prints the three values in the
# text; it has no Table 11-2 (the function keeps its old name):
#
#   "for cases in which the cap is not in contact with the ground:
#    eta = 0.65 for a center-to-center spacing of 2.5 diameters
#    eta = 0.80 for a center-to-center spacing of 3 diameters
#    eta = 1.0 for a center-to-center spacing of 4 diameters or more
#    The value of eta may be determined by linear interpolation for
#    intermediate spacings. If the cap will be maintained in contact with
#    the ground (which is not typically applicable to bridge foundations),
#    then no reduction is applied."
# ============================================================================

_GROUP_EFF_SPACING = [2.5, 3.0, 4.0]
_GROUP_EFF_ETA     = [0.65, 0.80, 1.00]

_GROUP_EFF_REFERENCE = (
    "FHWA-NHI-18-024 (GEC-10) Section 11.4.1.2 Cohesionless Soils, p. 11-6, "
    "citing AASHTO (2017a) 10.8.3.6.3 (no Table 11-2 is printed)")


def table_11_2_group_efficiency_cohesionless(spacing_over_d: float) -> dict:
    """Group efficiency eta for the axial resistance of drilled shafts in cohesionless soil with the cap not in contact with the ground, from GEC-10 Section 11.4.1.2 (FHWA-NHI-18-024, p. 11-6, citing AASHTO 10.8.3.6.3); GEC-10 has no Table 11-2, the name is kept.

    As printed: eta = 0.65 at a center-to-center spacing of 2.5 diameters,
    0.80 at 3 diameters and 1.0 at 4 diameters or more, by linear
    interpolation for intermediate spacings. With the cap kept in contact
    with the ground no reduction is applied; the AASHTO commentary cited
    there says the reduction need not be made if casing is advanced in
    front of the excavation (p. 11-6 discusses both).

    Parameters
    ----------
    spacing_over_d : float
        Center-to-center shaft spacing / shaft diameter. Must be >= 2.5
        (the smallest spacing printed).

    Returns
    -------
    dict
        {'spacing_over_d': float, 'eta': float, 'note': str,
         'reference': str}

    Raises
    ------
    ValueError
        If spacing_over_d < 2.5.
    """
    if spacing_over_d < _GROUP_EFF_SPACING[0]:
        raise ValueError(
            f"spacing_over_d={spacing_over_d} is below the minimum of 2.5D, "
            "the smallest spacing printed (GEC-10 Section 11.4.1.2, p. 11-6)."
        )

    if spacing_over_d >= _GROUP_EFF_SPACING[-1]:
        eta = 1.0
        note = "spacing >= 4 diameters: eta = 1.0 (as printed)"
    elif spacing_over_d in _GROUP_EFF_SPACING:
        eta = _GROUP_EFF_ETA[_GROUP_EFF_SPACING.index(spacing_over_d)]
        note = "printed value"
    else:
        eta = _linterp(spacing_over_d, _GROUP_EFF_SPACING, _GROUP_EFF_ETA)
        note = ("linear interpolation for intermediate spacings, as "
                "Section 11.4.1.2 allows")

    return {
        "spacing_over_d": spacing_over_d,
        "eta": round(eta, 3),
        "note": note,
        "reference": _GROUP_EFF_REFERENCE,
    }
