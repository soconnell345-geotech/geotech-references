"""GEC-7 table lookup functions.

Digitized tables from FHWA-NHI-14-007 (GEC-7), Soil Nail Walls.
Follows the DM7 pattern: private data with ``_TABLE_*`` prefix, public
lookup functions with string matching and ``_linterp`` interpolation.
"""

from geotech_references._interpolation import _linterp


def _key(text: str) -> str:
    """A caller's name for a row as a lower-case, underscore-joined key."""
    for ch in ",;:()/-_.":
        text = text.replace(ch, " ")
    return "_".join(text.lower().split())


def _one_key(given, rows, aliases, table, page):
    """The one row key a name gives: the row's own key or a listed alias.
    Any other name, including a word several rows share, is refused with
    the printed rows; there is no partial matching. ``rows`` maps each key
    to the row as printed."""
    key = _key(given)
    key = aliases.get(key, key)
    if key in rows:
        return key
    raise ValueError(
        f"'{given}' does not name one row of GEC-7 {table} ({page}). "
        "Rows (key: as printed): "
        + "; ".join(f"{k}: {v}" for k, v in rows.items()))


# ============================================================================
# Table 4.2a: Correlations between SPT N-values, CPT, and Friction Angle of
# Cohesionless Soils - SPT. FHWA-NHI-14-007 (GEC-7), p. 78 (PDF page 118),
# read off the rendered page:
#
#   SPT N60 (1) (blows/ft)  Soil Density  Soil Relative  phi_s' (deg) (2)
#                            Description   Density
#   0 to 4                   Very Loose    < 20           < 30
#   4 to 10                  Loose         20 - 40        30 to 35
#   10 to 30                 Medium        40 - 60        35 to 40
#   30 to 50                 Dense         60 - 80        40 to 45
#   > 50                     Very Dense    > 80           > 45 (3)
#
#   Notes: (1) Uncorrected values are considered equivalent to N60.
#   (2) From Kulhawy and Mayne (1990) based on Meyerhof (1956).
#   (3) Sands should be selected to have a friction angle <= 40 degrees.
#   Gravelly soils should be selected to have a friction angle <= 45
#   degrees.
#
# The open bounds "< 30" and "> 45" print no second value: phi_min_deg is
# None for very loose and phi_max_deg is None for very dense.
#
# Boundaries, as printed: 50 is printed only in "30 to 50" (Dense; Very Dense
# is "> 50"), so N60 = 50 is Dense. 4, 10 and 30 are each printed in two
# rows ("0 to 4" and "4 to 10", ...); there the upper row is returned, as
# before, and the result names the lower row that also prints the value.
# ============================================================================

_TABLE_4_2A = [
    {"n_min": 0, "n_max": 4, "n_printed": "0 to 4", "density": "very_loose",
     "dr_pct": "<20", "phi_min": None, "phi_max": 30, "phi_printed": "< 30"},
    {"n_min": 4, "n_max": 10, "n_printed": "4 to 10", "density": "loose",
     "dr_pct": "20-40", "phi_min": 30, "phi_max": 35,
     "phi_printed": "30 to 35"},
    {"n_min": 10, "n_max": 30, "n_printed": "10 to 30", "density": "medium",
     "dr_pct": "40-60", "phi_min": 35, "phi_max": 40,
     "phi_printed": "35 to 40"},
    {"n_min": 30, "n_max": 50, "n_printed": "30 to 50", "density": "dense",
     "dr_pct": "60-80", "phi_min": 40, "phi_max": 45,
     "phi_printed": "40 to 45"},
    {"n_min": 50, "n_max": float("inf"), "n_printed": "> 50",
     "density": "very_dense",
     "dr_pct": ">80", "phi_min": 45, "phi_max": None,
     "phi_printed": "> 45 (3)"},
]

_TABLE_4_2A_NOTES = (
    "(1) Uncorrected values are considered equivalent to N60. "
    "(2) From Kulhawy and Mayne (1990) based on Meyerhof (1956). "
    "(3) Sands should be selected to have a friction angle <= 40 degrees. "
    "Gravelly soils should be selected to have a friction angle <= 45 "
    "degrees."
)


def table_4_2a_spt_soil_properties(n60: float) -> dict:
    """Density description, relative density (%) and friction angle range phi_s' (degrees) of a cohesionless soil from SPT N60, GEC-7 Table 4.2a (FHWA-NHI-14-007, p. 78); the open rows print "< 30" and "> 45" (phi_min_deg or phi_max_deg is None there), and note (3) holds sands to 40 and gravelly soils to 45 degrees.

    Parameters
    ----------
    n60 : float
        SPT blow count corrected for 60 % hammer efficiency (blows/ft); the
        table's note (1) takes uncorrected values as equivalent.

    N60 = 50 is Dense: the table prints 50 in "30 to 50" and Very Dense as
    "> 50". N60 = 4, 10 and 30 are printed in two rows each ("0 to 4" and
    "4 to 10", ...); the upper row is returned and the result names the
    lower one under ``also_printed_in``, with a ``note``.

    Returns
    -------
    dict
        density, relative_density_pct, phi_min_deg, phi_max_deg (None where
        the print gives an open bound), phi_printed (the cell as printed),
        n60_printed (the row's N60 cell), notes (the table's notes (1) to
        (3)), reference; at N60 = 4, 10 or 30 also also_printed_in and note.

    Raises
    ------
    ValueError
        If n60 is negative.
    """
    if n60 < 0:
        raise ValueError(f"n60 must be non-negative, got {n60}")

    def _out(row):
        return {
            "density": row["density"],
            "relative_density_pct": row["dr_pct"],
            "phi_min_deg": row["phi_min"],
            "phi_max_deg": row["phi_max"],
            "phi_printed": row["phi_printed"],
            "n60_printed": row["n_printed"],
            "notes": _TABLE_4_2A_NOTES,
            "reference": "FHWA-NHI-14-007 (GEC-7), Table 4.2a, p. 78",
        }

    if n60 == 50:          # printed in "30 to 50" only; Very Dense is "> 50"
        return _out(_TABLE_4_2A[3])
    for i, row in enumerate(_TABLE_4_2A):
        if row["n_min"] <= n60 < row["n_max"]:
            out = _out(row)
            if i > 0 and n60 == row["n_min"]:
                lower = _TABLE_4_2A[i - 1]
                out["also_printed_in"] = {
                    "n60_printed": lower["n_printed"],
                    "density": lower["density"],
                    "phi_printed": lower["phi_printed"]}
                out["note"] = (
                    f"Table 4.2a prints N60 = {n60:g} in two rows, "
                    f"'{lower['n_printed']}' ({lower['density']}) and "
                    f"'{row['n_printed']}' ({row['density']}); the upper row "
                    "is returned.")
            return out
    raise AssertionError("unreachable")  # pragma: no cover


# ============================================================================
# Table 4.3a: Elastic Properties of Various Soils
# Es in ksf (original units), Poisson's ratio dimensionless
# Conversion: 1 ksf = 47.88 kPa
# ============================================================================

_TABLE_4_3A = {
    "clay_soft": {
        "description": "Clay, soft sensitive",
        "Es_min_kPa": 2394, "Es_max_kPa": 14364,
        "nu_min": 0.4, "nu_max": 0.5,
    },
    "clay_medium_stiff": {
        "description": "Clay, medium stiff to stiff",
        "Es_min_kPa": 14364, "Es_max_kPa": 47880,
        "nu_min": 0.4, "nu_max": 0.5,
    },
    "clay_very_stiff": {
        "description": "Clay, very stiff",
        "Es_min_kPa": 47880, "Es_max_kPa": 95760,
        "nu_min": 0.4, "nu_max": 0.5,
    },
    "loess": {
        "description": "Loess",
        "Es_min_kPa": 14364, "Es_max_kPa": 57456,
        "nu_min": 0.1, "nu_max": 0.3,
    },
    "silt": {
        "description": "Silt",
        "Es_min_kPa": 1915, "Es_max_kPa": 19152,
        "nu_min": 0.3, "nu_max": 0.35,
    },
    "fine_sand_loose": {
        "description": "Fine sand, loose",
        "Es_min_kPa": 7661, "Es_max_kPa": 11491,
        "nu_min": 0.25, "nu_max": 0.25,
    },
    "fine_sand_medium_dense": {
        "description": "Fine sand, medium dense",
        "Es_min_kPa": 11491, "Es_max_kPa": 19152,
        "nu_min": 0.25, "nu_max": 0.25,
    },
    "fine_sand_dense": {
        "description": "Fine sand, dense",
        "Es_min_kPa": 19152, "Es_max_kPa": 28728,
        "nu_min": 0.25, "nu_max": 0.25,
    },
    "sand_loose": {
        "description": "Sand, loose",
        "Es_min_kPa": 9576, "Es_max_kPa": 28728,
        "nu_min": 0.20, "nu_max": 0.36,
    },
    "sand_medium_dense": {
        "description": "Sand, medium dense",
        "Es_min_kPa": 28728, "Es_max_kPa": 47880,
        "nu_min": 0.20, "nu_max": 0.36,
    },
    "sand_dense": {
        "description": "Sand, dense",
        "Es_min_kPa": 47880, "Es_max_kPa": 76608,
        "nu_min": 0.30, "nu_max": 0.40,
    },
    "gravel_loose": {
        "description": "Gravel, loose",
        "Es_min_kPa": 28728, "Es_max_kPa": 76608,
        "nu_min": 0.20, "nu_max": 0.35,
    },
    "gravel_medium_dense": {
        "description": "Gravel, medium dense",
        "Es_min_kPa": 76608, "Es_max_kPa": 95760,
        "nu_min": 0.20, "nu_max": 0.35,
    },
    "gravel_dense": {
        "description": "Gravel, dense",
        "Es_min_kPa": 95760, "Es_max_kPa": 191520,
        "nu_min": 0.30, "nu_max": 0.40,
    },
}


# Other names of ONE row (FHWA-NHI-14-007 p. 82, PDF page 122): the printed
# "Soil - condition" names and the condition-first forms. 'clay', 'sand',
# 'fine sand', 'gravel', 'dense' and the like fit several rows and are
# refused.
_TABLE_4_3A_ALIASES = {
    "clay_soft_sensitive": "clay_soft",
    "soft_sensitive_clay": "clay_soft",
    "soft_clay": "clay_soft",
    "clay_medium_stiff_to_stiff": "clay_medium_stiff",
    "medium_stiff_to_stiff_clay": "clay_medium_stiff",
    "medium_stiff_clay": "clay_medium_stiff",
    "very_stiff_clay": "clay_very_stiff",
    "loose_fine_sand": "fine_sand_loose",
    "medium_dense_fine_sand": "fine_sand_medium_dense",
    "dense_fine_sand": "fine_sand_dense",
    "loose_sand": "sand_loose",
    "medium_dense_sand": "sand_medium_dense",
    "dense_sand": "sand_dense",
    "loose_gravel": "gravel_loose",
    "medium_dense_gravel": "gravel_medium_dense",
    "dense_gravel": "gravel_dense",
}


def table_4_3a_elastic_properties(soil_type: str) -> dict:
    """Range of Young's modulus Es (kPa, from the printed ksf) and Poisson's ratio of one soil type, GEC-7 Table 4.3a Elastic Properties of Soils Based on Soil Type (after AASHTO 2014; FHWA-NHI-14-007, p. 82); the soil type must name one printed row.

    Original data in ksf, converted to kPa (1 ksf = 47.88 kPa). The three
    clay rows print Poisson's ratio 0.4 - 0.5 as undrained.

    Parameters
    ----------
    soil_type : str
        One printed row: 'clay_soft' (Clay - soft sensitive),
        'clay_medium_stiff' (medium stiff to stiff), 'clay_very_stiff',
        'loess', 'silt', 'fine_sand_loose', 'fine_sand_medium_dense',
        'fine_sand_dense', 'sand_loose', 'sand_medium_dense', 'sand_dense',
        'gravel_loose', 'gravel_medium_dense', 'gravel_dense', or a listed
        alias ('soft clay', 'dense sand', ...). A word several rows share
        ('clay', 'sand') is refused.

    Returns
    -------
    dict
        Keys: description, Es_min_kPa, Es_max_kPa, nu_min, nu_max; the clay
        rows add nu_condition 'undrained'.

    Raises
    ------
    ValueError
        If soil_type does not name one printed row.
    """
    rows = {k: v["description"] for k, v in _TABLE_4_3A.items()}
    key = _one_key(soil_type, rows, _TABLE_4_3A_ALIASES, "Table 4.3a",
                   "p. 82")
    out = dict(_TABLE_4_3A[key])
    if key.startswith("clay_"):
        out["nu_condition"] = "undrained"
    return out


# ============================================================================
# Table 4.3b: Elastic Modulus from SPT
# Es = multiplier * (N1)60, in ksf (original). Convert to kPa.
# Multiplier in ksf per blow; 1 ksf = 47.88 kPa
# ============================================================================

_TABLE_4_3B = {
    "silts_sandy_silts": {
        "description": "Silts, sandy silts, slightly cohesive mixtures",
        "multiplier_ksf": 8,
    },
    "clean_fine_to_medium_sand": {
        "description": "Clean fine to medium sands and slightly silty sands",
        "multiplier_ksf": 14,
    },
    "coarse_sand": {
        "description": "Coarse sands and sands with little gravel",
        "multiplier_ksf": 20,
    },
    "sandy_gravel": {
        "description": "Sandy gravel and gravels",
        "multiplier_ksf": 24,
    },
}


# Other names of ONE row (p. 82, PDF page 122): the printed row names (the
# print spells the third "Coarse sands and sands with little grave") and
# short forms. 'sand' fits the second and third rows and is refused (it
# returned the silts row, 8 (N1)60).
_TABLE_4_3B_ALIASES = {
    "silts_sandy_silts_slightly_cohesive_mixtures": "silts_sandy_silts",
    "silt": "silts_sandy_silts",
    "silts": "silts_sandy_silts",
    "sandy_silt": "silts_sandy_silts",
    "sandy_silts": "silts_sandy_silts",
    "clean_fine_to_medium_sands_and_slightly_silty_sands":
        "clean_fine_to_medium_sand",
    "clean_fine_to_medium_sands": "clean_fine_to_medium_sand",
    "fine_to_medium_sand": "clean_fine_to_medium_sand",
    "slightly_silty_sand": "clean_fine_to_medium_sand",
    "slightly_silty_sands": "clean_fine_to_medium_sand",
    "coarse_sands_and_sands_with_little_gravel": "coarse_sand",
    "coarse_sands_and_sands_with_little_grave": "coarse_sand",
    "coarse_sands": "coarse_sand",
    "sand_with_little_gravel": "coarse_sand",
    "sandy_gravel_and_gravels": "sandy_gravel",
    "sandy_gravels": "sandy_gravel",
    "gravel": "sandy_gravel",
    "gravels": "sandy_gravel",
}


def table_4_3b_elastic_modulus_spt(soil_type: str,
                                   n1_60: float) -> float:
    """Young's modulus Es in kPa from SPT (N1)60, Es = k (N1)60 with k = 8, 14, 20 or 24 ksf by soil row, GEC-7 Table 4.3b Elastic Properties of Soils Based on SPT N-values (after AASHTO 2014; FHWA-NHI-14-007, p. 82); the soil type must name one printed row.

    The printed Es is in ksf; the result is converted at 1 ksf = 47.88 kPa.

    Parameters
    ----------
    soil_type : str
        One printed row: 'silts_sandy_silts' (Silts, sandy silts, slightly
        cohesive mixtures: 8), 'clean_fine_to_medium_sand' (Clean fine to
        medium sands and slightly silty sands: 14), 'coarse_sand' (Coarse
        sands and sands with little gravel: 20), 'sandy_gravel' (Sandy gravel
        and gravels: 24), or a listed alias. 'sand' alone fits two rows and
        is refused.
    n1_60 : float
        Overburden-corrected SPT blow count (N1)60.

    Returns
    -------
    float
        Elastic modulus Es in kPa.

    Raises
    ------
    ValueError
        If soil_type does not name one printed row, or n1_60 is negative.
    """
    if n1_60 < 0:
        raise ValueError(f"n1_60 must be non-negative, got {n1_60}")

    rows = {k: f"{v['description']}, {v['multiplier_ksf']} (N1)60 ksf"
            for k, v in _TABLE_4_3B.items()}
    key = _one_key(soil_type, rows, _TABLE_4_3B_ALIASES, "Table 4.3b",
                   "p. 82")

    # Convert from ksf to kPa
    return _TABLE_4_3B[key]["multiplier_ksf"] * n1_60 * 47.88


# ============================================================================
# Table 4.4a: Nominal Bond Strength for Soil Nails — Coarse-Grained Soils
# Original units: psi. Conversion: 1 psi = 6.895 kPa
# Construction methods: Rotary Drilled, Driven Casing, Augered
# ============================================================================

_TABLE_4_4A_DATA = [
    # Rotary Drilled
    {"method": "rotary_drilled", "soil": "sand_gravel",
     "description": "Sand/gravel",
     "min_psi": 15, "max_psi": 26},
    {"method": "rotary_drilled", "soil": "silty_sand",
     "description": "Silty sand",
     "min_psi": 15, "max_psi": 22},
    {"method": "rotary_drilled", "soil": "silt",
     "description": "Silt",
     "min_psi": 9, "max_psi": 11},
    {"method": "rotary_drilled", "soil": "piedmont_residual",
     "description": "Piedmont residual",
     "min_psi": 6, "max_psi": 17},
    {"method": "rotary_drilled", "soil": "fine_colluvium",
     "description": "Fine colluvium",
     "min_psi": 11, "max_psi": 22},
    # Driven Casing
    {"method": "driven_casing", "soil": "sand_gravel_low_overburden",
     "description": "Sand/gravel with low overburden",
     "min_psi": 28, "max_psi": 35},
    {"method": "driven_casing", "soil": "sand_gravel_high_overburden",
     "description": "Sand/gravel with high overburden",
     "min_psi": 41, "max_psi": 62},
    {"method": "driven_casing", "soil": "dense_moraine",
     "description": "Dense moraine",
     "min_psi": 55, "max_psi": 70},
    {"method": "driven_casing", "soil": "colluvium",
     "description": "Colluvium",
     "min_psi": 15, "max_psi": 26},
    # Augered
    {"method": "augered", "soil": "silty_sand_fill",
     "description": "Silty sand fill",
     "min_psi": 3, "max_psi": 6},
    {"method": "augered", "soil": "silty_fine_sand",
     "description": "Silty fine sand",
     "min_psi": 8, "max_psi": 13},
    {"method": "augered", "soil": "silty_clayey_sand",
     "description": "Silty clayey sand",
     "min_psi": 9, "max_psi": 20},
]


_BOND_METHOD_ALIASES = {
    "rotary": "rotary_drilled",
    "driven": "driven_casing",
    "auger": "augered",
}

# Other names of ONE row, by drilling method (Table 4.4a, p. 84, PDF page
# 124). For driven casing, 'sand_gravel' fits two rows (low and high
# overburden) and is refused; 'sand' or 'silty_sand' in rotary drilling
# no longer reach Sand/gravel or Silty sand by a part of the name.
_TABLE_4_4A_ALIASES = {
    "rotary_drilled": {
        "sand_and_gravel": "sand_gravel",
        "piedmont": "piedmont_residual",
    },
    "driven_casing": {
        "sand_gravel_w_low_overburden": "sand_gravel_low_overburden",
        "sand_gravel_with_low_overburden": "sand_gravel_low_overburden",
        "sand_gravel_w_high_overburden": "sand_gravel_high_overburden",
        "sand_gravel_with_high_overburden": "sand_gravel_high_overburden",
        "moraine": "dense_moraine",
    },
    "augered": {},
}

_TABLE_4_4A_NOTE_1 = (
    "Table 4.4a note (1): low and high overburden are defined as effective "
    "overburden pressure being, respectively, less than and greater than "
    "1.5 tsf."
)


def _bond_row(data, construction_method, soil_type, soil_aliases, table,
              page):
    """The one row of a bond strength table (Table 4.4a or 4.4b) that a
    drilling method and a soil name give; no partial matching."""
    methods = list(dict.fromkeys(r["method"] for r in data))
    method_key = _key(construction_method)
    method_key = _BOND_METHOD_ALIASES.get(method_key, method_key)
    if method_key not in methods:
        raise ValueError(
            f"Unknown construction_method '{construction_method}' for "
            f"GEC-7 {table} ({page}). Options: {', '.join(methods)}")
    rows = {r["soil"]: r["description"] for r in data
            if r["method"] == method_key}
    key = _one_key(soil_type, rows, soil_aliases.get(method_key, {}),
                   f"{table}, {method_key}", page)
    for r in data:
        if r["method"] == method_key and r["soil"] == key:
            return r
    raise AssertionError("unreachable")  # pragma: no cover


def table_4_4a_bond_strength_coarse(construction_method: str,
                                    soil_type: str) -> dict:
    """Range of estimated bond strength qu (kPa, from the printed psi) of soil nails in coarse-grained soils by drilling method and soil, GEC-7 Table 4.4a Estimated Bond Strength for Soil Nails in Coarse-Grained Soils (modified after Elias and Juran 1991; FHWA-NHI-14-007, p. 84); the soil must name one printed row.

    The bond strength qu is between the grout and the surrounding soil; the
    ultimate pullout resistance per unit length of nail is the bond
    strength times the perimeter of the bond zone (p. 85).

    Parameters
    ----------
    construction_method : str
        Installation method: 'rotary_drilled', 'driven_casing', or 'augered'.
    soil_type : str
        Soil type within the chosen method. Examples:
        - rotary_drilled: 'sand_gravel', 'silty_sand', 'silt',
          'piedmont_residual', 'fine_colluvium'
        - driven_casing: 'sand_gravel_low_overburden',
          'sand_gravel_high_overburden', 'dense_moraine', 'colluvium'
        - augered: 'silty_sand_fill', 'silty_fine_sand', 'silty_clayey_sand'

    Returns
    -------
    dict
        Keys: method, soil, description, min_kPa, max_kPa; the two driven
        casing sand/gravel rows add note (the table's note (1)).

    Raises
    ------
    ValueError
        If the method is unknown or the soil does not name one row printed
        for that method.
    """
    row = _bond_row(_TABLE_4_4A_DATA, construction_method, soil_type,
                    _TABLE_4_4A_ALIASES, "Table 4.4a", "p. 84")
    out = {
        "method": row["method"],
        "soil": row["soil"],
        "description": row["description"],
        "min_kPa": round(row["min_psi"] * 6.895, 1),
        "max_kPa": round(row["max_psi"] * 6.895, 1),
    }
    if row["soil"].endswith("_overburden"):
        out["note"] = _TABLE_4_4A_NOTE_1
    return out


# ============================================================================
# Table 4.4b: Nominal Bond Strength for Soil Nails — Fine-Grained Soils
# Original units: psi. Conversion: 1 psi = 6.895 kPa
# ============================================================================

_TABLE_4_4B_DATA = [
    # Rotary Drilled
    {"method": "rotary_drilled", "soil": "silty_clay",
     "description": "Silty clay",
     "min_psi": 5, "max_psi": 7},
    # Driven Casing
    {"method": "driven_casing", "soil": "clayey_silt",
     "description": "Clayey silt",
     "min_psi": 13, "max_psi": 20},
    # Augered
    {"method": "augered", "soil": "loess",
     "description": "Loess",
     "min_psi": 4, "max_psi": 11},
    {"method": "augered", "soil": "soft_clay",
     "description": "Soft clay",
     "min_psi": 3, "max_psi": 4},
    {"method": "augered", "soil": "stiff_clay",
     "description": "Stiff clay",
     "min_psi": 6, "max_psi": 9},
    {"method": "augered", "soil": "stiff_clayey_silt",
     "description": "Stiff clayey silt",
     "min_psi": 6, "max_psi": 15},
    {"method": "augered", "soil": "calcareous_sandy_clay",
     "description": "Calcareous sandy clay",
     "min_psi": 13, "max_psi": 20},
]


def table_4_4b_bond_strength_fine(construction_method: str,
                                  soil_type: str) -> dict:
    """Range of estimated bond strength qu (kPa, from the printed psi) of soil nails in fine-grained soils by drilling method and soil, GEC-7 Table 4.4b Estimated Bond Strength for Soil Nails in Fine-Grained Soils (modified after Elias and Juran 1991; FHWA-NHI-14-007, p. 85); the soil must name one printed row.

    The bond strength qu is between the grout and the surrounding soil.
    'clay' for augered nails fits soft, stiff and calcareous sandy clay and
    is refused (it returned soft clay).

    Parameters
    ----------
    construction_method : str
        Installation method: 'rotary_drilled', 'driven_casing', or 'augered'.
    soil_type : str
        Soil type within the chosen method. Examples:
        - rotary_drilled: 'silty_clay'
        - driven_casing: 'clayey_silt'
        - augered: 'loess', 'soft_clay', 'stiff_clay',
          'stiff_clayey_silt', 'calcareous_sandy_clay'

    Returns
    -------
    dict
        Keys: method, soil, description, min_kPa, max_kPa.

    Raises
    ------
    ValueError
        If the method is unknown or the soil does not name one row printed
        for that method.
    """
    row = _bond_row(_TABLE_4_4B_DATA, construction_method, soil_type, {},
                    "Table 4.4b", "p. 85")
    return {
        "method": row["method"],
        "soil": row["soil"],
        "description": row["description"],
        "min_kPa": round(row["min_psi"] * 6.895, 1),
        "max_kPa": round(row["max_psi"] * 6.895, 1),
    }


# ============================================================================
# Table 4.5: Nominal Bond Strength for Soil Nails — Rock
# All entries are Rotary Drilled.
# Original units: psi. Conversion: 1 psi = 6.895 kPa
# ============================================================================

_TABLE_4_5 = {
    "marl_limestone": {
        "description": "Marl/limestone",
        "min_psi": 44, "max_psi": 58,
    },
    "phyllite": {
        "description": "Phyllite",
        "min_psi": 15, "max_psi": 44,
    },
    "chalk": {
        "description": "Chalk",
        "min_psi": 73, "max_psi": 87,
    },
    "soft_dolomite": {
        "description": "Soft dolomite",
        "min_psi": 58, "max_psi": 87,
    },
    "fissured_dolomite": {
        "description": "Fissured dolomite",
        "min_psi": 87, "max_psi": 145,
    },
    "weathered_sandstone": {
        "description": "Weathered sandstone",
        "min_psi": 29, "max_psi": 44,
    },
    "weathered_shale": {
        "description": "Weathered shale",
        "min_psi": 15, "max_psi": 22,
    },
    "weathered_schist": {
        "description": "Weathered schist",
        "min_psi": 15, "max_psi": 25,
    },
    "basalt": {
        "description": "Basalt",
        "min_psi": 73, "max_psi": 87,
    },
    "slate_hard_shale": {
        "description": "Slate/hard shale",
        "min_psi": 44, "max_psi": 58,
    },
}


# Other names of ONE row (Table 4.5, p. 85, PDF page 125). 'shale' (weathered
# shale or slate/hard shale), 'dolomite' (soft or fissured) and 'sandstone',
# 'schist' (the table prints only their weathered rows) are refused.
_TABLE_4_5_ALIASES = {
    "marl": "marl_limestone",
    "limestone": "marl_limestone",
    "slate": "slate_hard_shale",
    "hard_shale": "slate_hard_shale",
}


def table_4_5_bond_strength_rock(rock_type: str) -> dict:
    """Range of estimated bond strength qu (kPa, from the printed psi) of soil nails in rock, rotary drilled, GEC-7 Table 4.5 Estimated Bond Strength for Soil Nails in Rock (modified after Elias and Juran 1991; FHWA-NHI-14-007, p. 85); the rock type must name one printed row.

    Parameters
    ----------
    rock_type : str
        One printed row: 'marl_limestone', 'phyllite', 'chalk',
        'soft_dolomite', 'fissured_dolomite', 'weathered_sandstone',
        'weathered_shale', 'weathered_schist', 'basalt', 'slate_hard_shale',
        or 'marl', 'limestone', 'slate', 'hard_shale'. 'shale', 'dolomite',
        'sandstone' and 'schist' alone are refused (they returned weathered
        shale, soft dolomite, weathered sandstone and weathered schist).

    Returns
    -------
    dict
        Keys: rock_type, description, min_kPa, max_kPa.

    Raises
    ------
    ValueError
        If rock_type does not name one printed row.
    """
    rows = {k: v["description"] for k, v in _TABLE_4_5.items()}
    key = _one_key(rock_type, rows, _TABLE_4_5_ALIASES, "Table 4.5", "p. 85")
    entry = _TABLE_4_5[key]
    return {
        "rock_type": key,
        "description": entry["description"],
        "min_kPa": round(entry["min_psi"] * 6.895, 1),
        "max_kPa": round(entry["max_psi"] * 6.895, 1),
    }


# ============================================================================
# Table 4.6: Estimated Pullout Resistance per Unit Length (Qu/L)
# For preliminary design. Original units: kip/ft.
# Conversion: 1 kip/ft = 14.594 kN/m
# ============================================================================

_TABLE_4_6_DATA = [
    {"soil": "sand_and_gravel", "density": "loose",
     "n60_min": 4, "n60_max": 10, "qu_kip_ft": 10},
    {"soil": "sand_and_gravel", "density": "medium_dense",
     "n60_min": 11, "n60_max": 30, "qu_kip_ft": 15},
    {"soil": "sand_and_gravel", "density": "dense",
     "n60_min": 31, "n60_max": 50, "qu_kip_ft": 20},
    {"soil": "sand", "density": "loose",
     "n60_min": 4, "n60_max": 10, "qu_kip_ft": 7},
    {"soil": "sand", "density": "medium_dense",
     "n60_min": 11, "n60_max": 30, "qu_kip_ft": 10},
    {"soil": "sand", "density": "dense",
     "n60_min": 31, "n60_max": 50, "qu_kip_ft": 13},
    {"soil": "sand_and_silt", "density": "loose",
     "n60_min": 4, "n60_max": 10, "qu_kip_ft": 5},
    {"soil": "sand_and_silt", "density": "medium_dense",
     "n60_min": 11, "n60_max": 30, "qu_kip_ft": 7},
    {"soil": "sand_and_silt", "density": "dense",
     "n60_min": 31, "n60_max": 50, "qu_kip_ft": 9},
    {"soil": "silt_clay_low_pi", "density": "stiff",
     "n60_min": 10, "n60_max": 20, "qu_kip_ft": 2},
    {"soil": "silt_clay_low_pi", "density": "hard",
     "n60_min": 21, "n60_max": 40, "qu_kip_ft": 4},
]


_TABLE_4_6_SOILS = {
    "sand_and_gravel": "Sand and Gravel",
    "sand": "Sand",
    "sand_and_silt": "Sand and Silt",
    "silt_clay_low_pi": "Silt-clay mixture of low plasticity or fine "
                        "micaceous sand or silt mixtures",
}

# Other names of ONE soil row (p. 86, PDF page 126). 'silt' fits the sand
# and silt row and the silt-clay row and is refused.
_TABLE_4_6_ALIASES = {
    "sand_gravel": "sand_and_gravel",
    "sand_silt": "sand_and_silt",
    "silt_clay": "silt_clay_low_pi",
    "silt_clay_mixture": "silt_clay_low_pi",
    "silt_clay_mixture_of_low_plasticity_or_fine_micaceous_sand_or_silt_"
    "mixtures": "silt_clay_low_pi",
}

_TABLE_4_6_NOTE = (
    "Table 4.6 gives the SPT range as (N1)60 (the keys n60_min and n60_max "
    "hold that printed (N1)60 range). Note (1): values are for "
    "small-diameter (4 and 6 in.), straight-shaft, gravity-grouted ground "
    "anchors installed in soil."
)


def table_4_6_pullout_resistance(soil_type: str,
                                 density: str) -> dict:
    """Presumptive ultimate pullout resistance per unit length rPO (kN/m, from the printed kip/ft) by soil and relative density or consistency, GEC-7 Table 4.6 Presumptive Ultimate Values of Soil Nail Pullout Resistance per Unit Length (modified after Sabatini et al. 1999; FHWA-NHI-14-007, p. 86); for small-diameter gravity-grouted ground anchors (note (1)).

    The bond strength can be estimated by dividing these values by the
    perimeter of the drill hole (p. 86). The SPT ranges are printed as
    (N1)60.

    Parameters
    ----------
    soil_type : str
        One printed soil row: 'sand_and_gravel', 'sand', 'sand_and_silt',
        'silt_clay_low_pi' (Silt-clay mixture of low plasticity or fine
        micaceous sand or silt mixtures), or a listed alias. 'silt' alone
        is refused.
    density : str
        'loose', 'medium_dense', 'dense' (sands and gravels) or 'stiff',
        'hard' (silt-clay).

    Returns
    -------
    dict
        Keys: soil_type, density, n60_min, n60_max (the printed (N1)60
        range), qu_kN_per_m, note.

    Raises
    ------
    ValueError
        If the soil does not name one printed row or the combination is not
        printed.
    """
    soil_key = _one_key(soil_type, _TABLE_4_6_SOILS, _TABLE_4_6_ALIASES,
                        "Table 4.6", "p. 86")
    density_key = _key(density)

    for row in _TABLE_4_6_DATA:
        if row["soil"] == soil_key and row["density"] == density_key:
            return {
                "soil_type": row["soil"],
                "density": row["density"],
                "n60_min": row["n60_min"],
                "n60_max": row["n60_max"],
                "qu_kN_per_m": round(row["qu_kip_ft"] * 14.594, 1),
                "note": _TABLE_4_6_NOTE,
            }

    densities = [r["density"] for r in _TABLE_4_6_DATA
                 if r["soil"] == soil_key]
    raise ValueError(
        f"Table 4.6 (GEC-7 p. 86) prints no '{density}' row for "
        f"{_TABLE_4_6_SOILS[soil_key]}. Options: {', '.join(densities)}."
    )


# ============================================================================
# Table 4.9: Site Coefficient F_PGA (Kavazanjian et al. 2011).
# FHWA-NHI-14-007 (GEC-7), p. 94 (PDF page 134), read off the rendered page:
#
#   Site Class  PGA <= 0.25  PGA = 0.5  PGA = 0.75  PGA = 1.0  PGA >= 1.25
#   A           0.8          0.8        0.8         0.8        0.8
#   B           1.0          1.0        1.0         1.0        1.0
#   C           1.2          1.2        1.1         1.0        1.0
#   D           1.6          1.4        1.2         1.1        1.0
#   E           2.5          1.7        1.2         0.9        0.9
#   F           (1) A site-specific dynamic site response analysis must be
#               performed in these cases.
#
# By the lead's ruling (RULINGS row 10, review finding gec-29) the values
# are used under PGA 0.1, 0.2, 0.3, 0.4, 0.5: GEC-7's headings are the Ss
# values of the Fa table, and GEC-12 Vol I Table 7-27 (p. 380, PDF page
# 426) prints the same values under PGA < 0.1, 0.2, 0.3, 0.4, > 0.5, with
# "Straight line interpolation ... for intermediate values" (p. 379).
# ============================================================================

_TABLE_4_9_PGA = [0.1, 0.2, 0.3, 0.4, 0.5]

_TABLE_4_9_FPGA = {
    "A": [0.8, 0.8, 0.8, 0.8, 0.8],
    "B": [1.0, 1.0, 1.0, 1.0, 1.0],
    "C": [1.2, 1.2, 1.1, 1.0, 1.0],
    "D": [1.6, 1.4, 1.2, 1.1, 1.0],
    "E": [2.5, 1.7, 1.2, 0.9, 0.9],
}

_TABLE_4_9_NOTE = (
    "GEC-7 Table 4.9 (p. 94) heads its columns PGA <= 0.25, 0.5, 0.75, 1.0, "
    ">= 1.25; GEC-12 Vol I Table 7-27 (p. 380) prints the same values under "
    "PGA < 0.1, 0.2, 0.3, 0.4, > 0.5, and those are used here (lead's "
    "ruling). With GEC-7's headings, site class D at PGA 0.30 would read "
    "1.56 instead of 1.2."
)


# Note (1) of Tables 4.9 (p. 94) and 4.10 (p. 95), on the site class F row.
_SITE_CLASS_F_NOTE = (
    "A site-specific dynamic site response analysis must be performed in "
    "these cases.")


def table_4_9_site_coefficient_fpga(site_class: str,
                                    pga: float) -> dict:
    """Site coefficient F_PGA for site classes A to E, GEC-7 Table 4.9 (FHWA-NHI-14-007, p. 94), read under the PGA columns 0.1 to 0.5 of GEC-12 Vol I Table 7-27 (p. 380), which prints the same values; GEC-7 heads them PGA <= 0.25 to >= 1.25 (lead's ruling; print_note in the result).

    Between columns F_PGA is interpolated on a straight line (GEC-12 p.
    379); at PGA 0.1 or less the first column applies and at 0.5 or more
    the last (Table 7-27 heads them "PGA < 0.1" and "PGA > 0.5"). Site
    class F needs a site-specific dynamic site response analysis (note (1))
    and is refused.

    Parameters
    ----------
    site_class : str
        AASHTO site class: 'A', 'B', 'C', 'D', or 'E'.
    pga : float
        Peak ground acceleration coefficient (Site Class B, in g), 0 or
        more. The first and last columns are printed open-ended (GEC-7
        "<= 0.25" / ">= 1.25"; GEC-12 Table 7-27 "< 0.1" / "> 0.5"), so a
        PGA below the first or above the last takes that column.

    Returns
    -------
    dict
        site_class, pga, F_pga, print_note, reference.

    Raises
    ------
    ValueError
        If site_class is F or not a site class, or pga is negative.
    """
    key = site_class.upper().strip()
    if key == "F":
        raise ValueError(
            "Site class F: GEC-7 Table 4.9 (p. 94) gives no F_PGA; its note "
            f"(1): \"{_SITE_CLASS_F_NOTE}\"")
    if key not in _TABLE_4_9_FPGA:
        raise ValueError(
            f"Unknown site_class '{site_class}'. Options: A, B, C, D, E"
        )

    if pga < 0:
        raise ValueError(f"pga must be 0 or more (in g), got {pga}")
    # the first and last columns are printed open-ended (see the docstring)
    pga_held = max(0.1, min(0.5, pga))
    f_pga = _linterp(pga_held, _TABLE_4_9_PGA, _TABLE_4_9_FPGA[key])
    return {
        "site_class": key,
        "pga": pga,
        "F_pga": round(f_pga, 3),
        "print_note": _TABLE_4_9_NOTE,
        "reference": ("FHWA-NHI-14-007 (GEC-7), Table 4.9 Site Coefficient "
                      "F_PGA, p. 94; columns of FHWA-NHI-16-009 (GEC-12) "
                      "Vol I Table 7-27, p. 380"),
    }


# ============================================================================
# Table 4.10: Site Coefficient F_v (Kavazanjian 2011), FHWA-NHI-14-007
# (GEC-7), p. 95 (PDF page 135)
# ============================================================================

_TABLE_4_10_S1 = [0.1, 0.2, 0.3, 0.4, 0.5]

_TABLE_4_10_FV = {
    "A": [0.8, 0.8, 0.8, 0.8, 0.8],
    "B": [1.0, 1.0, 1.0, 1.0, 1.0],
    "C": [1.7, 1.6, 1.5, 1.4, 1.3],
    "D": [2.4, 2.0, 1.8, 1.6, 1.5],
    "E": [3.5, 3.2, 2.8, 2.4, 2.4],
}


def table_4_10_site_coefficient_fv(site_class: str,
                                   s1: float) -> float:
    """Site coefficient F_v for site classes A to E from the 1-second spectral acceleration S1, GEC-7 Table 4.10 Site Coefficient F_v (Kavazanjian 2011) (FHWA-NHI-14-007, p. 95); site class F is refused with the table's note (1).

    Parameters
    ----------
    site_class : str
        AASHTO site class: 'A', 'B', 'C', 'D', or 'E'.
    s1 : float
        Spectral acceleration at 1-second period (dimensionless, g units),
        0 or more. The table heads its first and last columns "S1 <= 0.1"
        and "S1 >= 0.5" (p. 95, PDF page 135), printed open-ended: values
        <= 0.1 use the first column; >= 0.5 use the last.

    Returns
    -------
    float
        Site coefficient F_v.

    Raises
    ------
    ValueError
        If site_class is F (the table's note (1): a site-specific dynamic
        site response analysis) or not a site class, or s1 is negative.
    """
    key = site_class.upper().strip()
    if key == "F":
        raise ValueError(
            "Site class F: GEC-7 Table 4.10 (p. 95) gives no F_v; its note "
            f"(1): \"{_SITE_CLASS_F_NOTE}\"")
    if key not in _TABLE_4_10_FV:
        raise ValueError(
            f"Unknown site_class '{site_class}'. Options: A, B, C, D, E"
        )

    if s1 < 0:
        raise ValueError(f"s1 must be 0 or more (in g), got {s1}")
    # the first and last columns are printed open-ended (see the docstring)
    s1_clamped = max(0.1, min(0.5, s1))
    return _linterp(s1_clamped, _TABLE_4_10_S1, _TABLE_4_10_FV[key])


# ============================================================================
# Table 5.1: Minimum Recommended Factors of Safety (ASD)
# ============================================================================

_TABLE_5_1 = {
    "overall_stability": {
        "description": "Overall stability",
        "symbol": "FS_OS",
        "fs_static": 1.5,
        "fs_seismic": 1.1,
    },
    "short_term_excavation": {
        "description": "Short-term condition, excavation",
        "symbol": "FS_OS",
        "fs_static": 1.25,
        "fs_static_max": 1.33,
        "fs_seismic": None,
    },
    "basal_heave_short_term": {
        "description": "Basal heave, permanent wall short-term",
        "symbol": "FS_BH",
        "fs_static": 2.0,
        "fs_seismic": None,
    },
    "basal_heave_long_term": {
        "description": "Basal heave, permanent wall long-term",
        "symbol": "FS_BH",
        "fs_static": 2.5,
        "fs_seismic": 2.3,
    },
    "pullout_resistance": {
        "description": "Pullout resistance",
        "symbol": "FS_PO",
        "fs_static": 2.0,
        "fs_seismic": 1.5,
    },
    "lateral_sliding": {
        "description": "Lateral sliding",
        "symbol": "FS_LS",
        "fs_static": 1.5,
        "fs_seismic": 1.1,
    },
    "tendon_tensile_grade_60_75": {
        "description": "Tendon tensile strength (Grades 60 and 75)",
        "symbol": "FS_T",
        "fs_static": 1.8,
        "fs_seismic": 1.35,
    },
    "tendon_tensile_grade_95_150": {
        "description": "Tendon tensile strength (Grades 95 and 150)",
        "symbol": "FS_T",
        "fs_static": 2.0,
        "fs_seismic": 1.50,
    },
    "facing_flexure": {
        "description": "Facing flexural",
        "symbol": "FS_FF",
        "fs_static": 1.5,
        "fs_seismic": 1.1,
    },
    "facing_punching_shear": {
        "description": "Facing punching shear",
        "symbol": "FS_FP",
        "fs_static": 1.5,
        "fs_seismic": 1.1,
    },
    "headed_stud_a307": {
        "description": "Headed stud tensile (A307 bolt)",
        "symbol": "FS_FH",
        "fs_static": 2.0,
        "fs_seismic": 1.5,
    },
    "headed_stud_a325": {
        "description": "Headed stud tensile (A325 bolt)",
        "symbol": "FS_FH",
        "fs_static": 1.7,
        "fs_seismic": 1.3,
    },
}


# Table 5.1's notes (p. 108, PDF page 148) on the rows they mark.
_TABLE_5_1_NOTES = {
    "overall_stability": (
        "(2) For non-critical, permanent structures, some Owners may accept "
        "a design for static loads and long-term conditions with FS_OS = "
        "1.35 when uncertainty is considered to be limited due to the "
        "availability of sufficient geotechnical information and successful "
        "local experience on soil nailing. (6) The minimum FS_OS for seismic "
        "overall stability should be 1.0, when horizontal seismic "
        "coefficients are used and these were derived from estimated, "
        "allowable seismic deformations."),
    "short_term_excavation": (
        "(3) This range of safety factors for global stability corresponds "
        "to the case of temporary excavation lifts that are unsupported for "
        "up to 2 days before nails are installed. The larger value may be "
        "applied to critical structures or when more uncertainty exists "
        "regarding soil conditions."),
    "basal_heave_short_term": (
        "(4) This factor of safety for basal heave is applicable to "
        "permanent walls for short-term conditions."),
    "basal_heave_long_term": (
        "(5) This factor of safety for basal heave is applicable to "
        "permanent walls for long-term conditions."),
}

# The Basal Heave row prints "2.0 (4), 2.5 (5)" static and "2.3 (5)" seismic.
_TABLE_5_1_BH_NOTE = (
    "Table 5.1 prints one Basal Heave row: static 2.0 (note 4, short-term) "
    "and 2.5 (note 5, long-term), seismic 2.3 (note 5, long-term). No "
    "seismic value is printed for short-term conditions.")

# Other names of ONE row. 'basal_heave' (short- or long-term), 'tendon'
# (two grade rows), 'headed_stud' (A307 or A325) and 'facing' are refused.
_TABLE_5_1_ALIASES = {
    "overall": "overall_stability",
    "short_term": "short_term_excavation",
    "short_term_condition_excavation": "short_term_excavation",
    "pullout": "pullout_resistance",
    "sliding": "lateral_sliding",
    "tendon_tensile_strength_grades_60_and_75": "tendon_tensile_grade_60_75",
    "tendon_tensile_strength_grades_95_and_150":
        "tendon_tensile_grade_95_150",
    "tendon_grade_60_75": "tendon_tensile_grade_60_75",
    "tendon_grade_95_150": "tendon_tensile_grade_95_150",
    "facing_flexural": "facing_flexure",
    "headed_stud_tensile_a307_bolt": "headed_stud_a307",
    "headed_stud_tensile_a325_bolt": "headed_stud_a325",
}


def table_5_1_factors_of_safety(limit_state: str) -> dict:
    """Minimum recommended factors of safety (static and seismic) for soil nail walls designed by ASD, GEC-7 Table 5.1 (FHWA-NHI-14-007, p. 108), with the table's notes; the limit state must name one printed row.

    Short-term excavation prints a range, 1.25-1.33 (note (3)): fs_static
    is 1.25 and fs_static_max 1.33. Basal heave prints 2.0 (short-term,
    note (4)) and 2.5 (long-term, note (5)) static and 2.3 seismic with
    note (5), so the seismic value is given for long-term only.

    Parameters
    ----------
    limit_state : str
        One printed row: 'overall_stability', 'short_term_excavation',
        'basal_heave_short_term', 'basal_heave_long_term',
        'pullout_resistance', 'lateral_sliding',
        'tendon_tensile_grade_60_75', 'tendon_tensile_grade_95_150',
        'facing_flexure', 'facing_punching_shear', 'headed_stud_a307',
        'headed_stud_a325', or a listed alias. 'basal heave', 'tendon',
        'headed stud' and 'facing' alone fit two rows and are refused.

    Returns
    -------
    dict
        Keys: description, symbol, fs_static, fs_seismic (None where the
        table prints NA or nothing); short_term_excavation adds
        fs_static_max; rows with a note add notes.

    Raises
    ------
    ValueError
        If limit_state does not name one printed row.
    """
    rows = {k: v["description"] for k, v in _TABLE_5_1.items()}
    key = _one_key(limit_state, rows, _TABLE_5_1_ALIASES, "Table 5.1",
                   "p. 108")
    out = dict(_TABLE_5_1[key])
    if key in _TABLE_5_1_NOTES:
        out["notes"] = _TABLE_5_1_NOTES[key]
    if key.startswith("basal_heave"):
        out["print_note"] = _TABLE_5_1_BH_NOTE
    return out


# ============================================================================
# Table 5.3: Load Factors for Permanent Loads (AASHTO 2014)
# ============================================================================

_TABLE_5_3 = {
    "dc_dead_loads": {
        "description": "DC: Dead loads",
        "max_factor": 1.25, "min_factor": 0.90,
    },
    "dw_wearing_surfaces": {
        "description": "DW: Loads from wearing surfaces and utilities",
        "max_factor": 1.50, "min_factor": 0.65,
    },
    "eh_active": {
        "description": "EH: Horizontal earth pressure (active condition)",
        "max_factor": 1.50, "min_factor": 0.90,
    },
    "eh_at_rest": {
        "description": "EH: Horizontal earth pressure (at-rest condition)",
        "max_factor": 1.35, "min_factor": 0.90,
    },
    "ev_overall_stability": {
        "description": "EV: Vertical earth pressure (overall stability)",
        "max_factor": 1.00, "min_factor": None,
    },
    "ev_retaining_walls": {
        "description": "EV: Vertical earth pressure (retaining walls and abutments)",
        "max_factor": 1.35, "min_factor": 1.00,
    },
    "es_earth_surcharge": {
        "description": "ES: Earth surcharge",
        "max_factor": 1.50, "min_factor": 0.75,
    },
}


# Other names of ONE row (p. 113, PDF page 153). 'eh' and 'ev' fit two rows
# each and are refused.
_TABLE_5_3_ALIASES = {
    "dc": "dc_dead_loads",
    "dead_loads": "dc_dead_loads",
    "dw": "dw_wearing_surfaces",
    "eh_active_condition": "eh_active",
    "eh_at_rest_condition": "eh_at_rest",
    "ev_overall": "ev_overall_stability",
    "ev_retaining": "ev_retaining_walls",
    "ev_ret_walls_and_abutments": "ev_retaining_walls",
    "es": "es_earth_surcharge",
    "earth_surcharge": "es_earth_surcharge",
}


def table_5_3_load_factors_permanent(load_type: str) -> dict:
    """Maximum and minimum load factors gamma_p for permanent loads, GEC-7 Table 5.3 Load Factors for Permanent Loads (FHWA-NHI-14-007, p. 113, after AASHTO 2014); the load type must name one printed row.

    The maximum applies when the permanent load has a destabilizing effect
    and the minimum when it has a stabilizing effect (notes (1), (2)).

    Parameters
    ----------
    load_type : str
        One printed row: 'dc_dead_loads', 'dw_wearing_surfaces',
        'eh_active', 'eh_at_rest', 'ev_overall_stability',
        'ev_retaining_walls', 'es_earth_surcharge', or a listed alias. 'eh'
        and 'ev' alone fit two rows and are refused.

    Returns
    -------
    dict
        Keys: description, max_factor, min_factor.

    Raises
    ------
    ValueError
        If load_type does not name one printed row.
    """
    rows = {k: v["description"] for k, v in _TABLE_5_3.items()}
    key = _one_key(load_type, rows, _TABLE_5_3_ALIASES, "Table 5.3",
                   "p. 113")
    return dict(_TABLE_5_3[key])


# ============================================================================
# Tables 5.4 - 5.11: LRFD Resistance Factors
# Combined into a single comprehensive lookup.
# ============================================================================

_TABLE_5_RESISTANCE_FACTORS = {
    "overall_stability": {
        "table": "5.4",
        "description": "Overall stability",
        "symbol": "phi_OS",
        "static": 0.65,
        "seismic": 0.90,
    },
    "basal_heave_short_term": {
        "table": "5.5",
        "description": "Basal heave, permanent wall short-term",
        "symbol": "phi_BH",
        "static": 0.65,
        "seismic": None,
    },
    "basal_heave_long_term": {
        "table": "5.5",
        "description": "Basal heave, permanent wall long-term",
        "symbol": "phi_BH",
        "static": 0.50,
        "seismic": None,
    },
    "pullout": {
        "table": "5.6",
        "description": "Pullout resistance",
        "symbol": "phi_PO",
        "static": 0.65,
        "seismic": 0.65,
    },
    "lateral_sliding": {
        "table": "5.7",
        "description": "Lateral sliding",
        "symbol": "phi_LS",
        "static": 1.00,
        "seismic": 0.90,
    },
    "tendon_grade_60_75": {
        "table": "5.8",
        "description": "Tendon in tension, Grades 60/75 (ASTM A615)",
        "symbol": "phi_T",
        "static": 0.75,
        "seismic": 0.75,
    },
    "tendon_grade_95_150": {
        "table": "5.8",
        "description": "Tendon in tension, Grade 95/150 (ASTM A722)",
        "symbol": "phi_T",
        "static": 0.65,
        "seismic": 0.65,
    },
    "facing_flexure": {
        "table": "5.9",
        "description": "Flexure resistance at facing",
        "symbol": "phi_FF",
        "static": 0.90,
        "seismic": 0.90,
    },
    "facing_punching_shear": {
        "table": "5.10",
        "description": "Punching shear at facing",
        "symbol": "phi_FP",
        "static": 0.90,
        "seismic": 0.90,
    },
    "headed_stud_a307": {
        "table": "5.11",
        "description": "Headed stud in tension, A307 steel bolt",
        "symbol": "phi_FH",
        "static": 0.70,
        "seismic": 0.65,
    },
    "headed_stud_a325": {
        "table": "5.11",
        "description": "Headed stud in tension, A325 steel bolt",
        "symbol": "phi_FH",
        "static": 0.80,
        "seismic": 0.75,
    },
}


# Other names of ONE row (Tables 5.4 to 5.11, pp. 121-140). 'basal_heave',
# 'tendon', 'headed_stud' and 'facing' fit two rows each and are refused.
_TABLE_5_RF_ALIASES = {
    "pullout_resistance": "pullout",
    "sliding": "lateral_sliding",
    "tendon_grades_60_75": "tendon_grade_60_75",
    "tendon_grade_95": "tendon_grade_95_150",
    "flexure": "facing_flexure",
    "flexure_resistance_at_facing": "facing_flexure",
    "punching_shear": "facing_punching_shear",
    "punching_shear_at_facing": "facing_punching_shear",
    "a307": "headed_stud_a307",
    "a325": "headed_stud_a325",
}


def table_5_resistance_factors(limit_state: str) -> dict:
    """LRFD resistance factors phi (static and seismic) for soil nail wall limit states, GEC-7 Tables 5.4 to 5.11 (FHWA-NHI-14-007, pp. 121-140); the limit state must name one printed row.

    Returns the resistance factor (phi) for the specified limit state,
    for both static and seismic loading conditions.

    Parameters
    ----------
    limit_state : str
        Limit state. Options: 'overall_stability', 'basal_heave_short_term',
        'basal_heave_long_term', 'pullout', 'lateral_sliding',
        'tendon_grade_60_75', 'tendon_grade_95_150', 'facing_flexure',
        'facing_punching_shear', 'headed_stud_a307', 'headed_stud_a325'.

    Returns
    -------
    dict
        Keys: table, description, symbol, static, seismic.

    Raises
    ------
    ValueError
        If limit_state does not name one printed row ('basal heave',
        'tendon', 'headed stud' and 'facing' alone fit two rows each).
    """
    rows = {k: f"Table {v['table']} {v['description']}"
            for k, v in _TABLE_5_RESISTANCE_FACTORS.items()}
    key = _one_key(limit_state, rows, _TABLE_5_RF_ALIASES,
                   "Tables 5.4 to 5.11", "pp. 121-140")
    return dict(_TABLE_5_RESISTANCE_FACTORS[key])


# ============================================================================
# Table 5.12: Wall Displacement Parameters
# (delta_h / H)_i and C as functions of soil conditions
# From Clouterre (1993) and Byrne et al. (1998)
# ============================================================================

_TABLE_5_12 = {
    "weathered_rock_stiff_soil": {
        "description": "Weathered rock and stiff soil",
        "delta_h_over_H": 1.0 / 1000,
        "C": 0.8,
    },
    "sandy_soil": {
        "description": "Sandy soil",
        "delta_h_over_H": 1.0 / 500,
        "C": 1.25,
    },
    "fine_grained_soil": {
        "description": "Fine-grained soil",
        "delta_h_over_H": 1.0 / 333,
        "C": 1.5,
    },
}


# Other names of ONE column (Table 5.12, p. 141, PDF page 181). 'soil' fits
# all three and is refused (it returned weathered rock and stiff soil).
_TABLE_5_12_ALIASES = {
    "weathered_rock_and_stiff_soil": "weathered_rock_stiff_soil",
    "weathered_rock": "weathered_rock_stiff_soil",
    "stiff_soil": "weathered_rock_stiff_soil",
    "sand": "sandy_soil",
    "sandy": "sandy_soil",
    "fine_grained": "fine_grained_soil",
}


def table_5_12_wall_displacement(soil_condition: str) -> dict:
    """Ratio (delta_h/H)_i and coefficient C for soil nail wall displacement by soil condition, GEC-7 Table 5.12 Values of (delta_h/H)_i and C as Functions of Soil Conditions (FHWA-NHI-14-007, p. 141; modified from Clouterre 1993 and Byrne et al. 1998); the soil condition must name one printed column.

    Used to estimate maximum horizontal and vertical displacements
    at the top of a soil nail wall:
      delta_h = delta_v = (delta_h/H)_i * H
      D_DEF = C * (1 - tan(alpha)) * H
    where H = wall height, alpha = wall batter angle.

    Parameters
    ----------
    soil_condition : str
        Soil condition: 'weathered_rock_stiff_soil', 'sandy_soil',
        or 'fine_grained_soil'.

    Returns
    -------
    dict
        Keys: description, delta_h_over_H, C.

    Raises
    ------
    ValueError
        If soil_condition does not name one printed column.
    """
    rows = {k: v["description"] for k, v in _TABLE_5_12.items()}
    key = _one_key(soil_condition, rows, _TABLE_5_12_ALIASES, "Table 5.12",
                   "p. 141")
    return dict(_TABLE_5_12[key])
