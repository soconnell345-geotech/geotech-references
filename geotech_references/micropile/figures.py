"""Micropile figure lookup functions.

Digitized figures from FHWA-NHI-05-039, Micropile Design & Construction.
Follows the DM7 pattern: private data with ``_FIG_*`` prefix, public
lookup functions with ``_linterp`` interpolation.

Currently contains Figure 5-23 limiting lateral modulus values, which are
derived from Eq. 5-29 for common micropile casing and bar sections.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Figure 5-23: Limiting Lateral Modulus Values for Various Micropile
# Materials (after Cadden and Gomez, 2002)
#
# Bar chart of limiting Es (psi → converted to kPa) for buckling
# evaluation.  Computed from Eq. 5-29: Es_limit = 1 / [(4I/A^2)(E/Fy^2)]
#
# Two categories: casings and reinforcing bars.
# Values digitized from bar chart in Figure 5-23.
# ============================================================================

# Limiting Es in kPa (converted from psi × 6.895)
_FIG_5_23_CASING = {
    # label: (description, es_limit_kpa)
    "5.5x0.36_n80": ("5.5in × 0.36in wall, API N-80 (80 ksi)",
                      669),    # 97 psi
    "7x0.5_n80": ("7in × 0.5in wall, API N-80 (80 ksi)",
                   724),       # 105 psi
    "9.625x0.47_n80": ("9.625in × 0.47in wall, API N-80 (80 ksi)",
                        1096),  # 159 psi
    "5.5_a519": ("5.5in casing, ASTM A519 (36 ksi)", 186),   # 27 psi
    "6.625_a519": ("6-5/8in casing, ASTM A519 (36 ksi)", 159),  # 23 psi
    "8_a519": ("8in casing, ASTM A519 (36 ksi)", 131),       # 19 psi
    "10.75_a519": ("10-3/4in casing, ASTM A519 (36 ksi)", 117),  # 17 psi
}

_FIG_5_23_BAR = {
    # label: (description, es_limit_kpa)
    "#10": ("#10 Reinforcing Bar (Grade 520)", 4207),   # 610 psi
    "#11": ("#11 Reinforcing Bar (Grade 520)", 4207),
    "#14": ("#14 Reinforcing Bar (Grade 520)", 4207),
    "#18": ("#18 Reinforcing Bar (Grade 520)", 4207),
    "#28": ("#28 Reinforcing Bar (Grade 520)", 4207),
}

_FIG_5_23_HOLLOW_BAR = {
    # label: (description, es_limit_kpa)
    "30/16": ("Hollow Bar 30/16", 2034),   # 295 psi
    "32/20": ("Hollow Bar 32/20", 1745),   # 253 psi
    "40/20": ("Hollow Bar 40/20", 2138),   # 310 psi
    "52/26": ("Hollow Bar 52/26", 2365),   # 343 psi
    "73/53": ("Hollow Bar 73/53", 2414),   # 350 psi
    "103/51": ("Hollow Bar 103/51", 1138),  # 165 psi
}


def figure_5_23_limiting_lateral_modulus(section: str) -> dict:
    """Limiting lateral modulus Es for micropile buckling (Figure 5-23).

    If the actual soil modulus Es is less than this limiting value,
    buckling does not control and need not be evaluated further.
    Values are from Cadden and Gomez (2002), based on Eq. 5-29.

    Parameters
    ----------
    section : str
        Micropile section identifier.  Examples:
        Casings: '5.5x0.36_n80', '7x0.5_n80', '5.5_a519', '8_a519'
        Bars: '#10', '#14', '#18'
        Hollow bars: '30/16', '73/53', '103/51'
        Use '' or 'all' to get all values.

    Returns
    -------
    dict
        Keys: section, description, es_limit_kpa.
        If section='all', returns dict of all sections grouped by category.

    Raises
    ------
    ValueError
        If section is not recognized.
    """
    key = section.strip().lower().replace(" ", "")

    if not key or key == "all":
        result = {"casings": {}, "bars": {}, "hollow_bars": {}}
        for k, (desc, es) in _FIG_5_23_CASING.items():
            result["casings"][k] = {"description": desc, "es_limit_kpa": es}
        for k, (desc, es) in _FIG_5_23_BAR.items():
            result["bars"][k] = {"description": desc, "es_limit_kpa": es}
        for k, (desc, es) in _FIG_5_23_HOLLOW_BAR.items():
            result["hollow_bars"][k] = {"description": desc, "es_limit_kpa": es}
        return result

    # Search all categories
    for table in (_FIG_5_23_CASING, _FIG_5_23_BAR, _FIG_5_23_HOLLOW_BAR):
        for k, (desc, es) in table.items():
            if k.lower() == key or key in k.lower():
                return {
                    "section": k,
                    "description": desc,
                    "es_limit_kpa": es,
                }

    all_keys = (
        list(_FIG_5_23_CASING.keys()) +
        list(_FIG_5_23_BAR.keys()) +
        list(_FIG_5_23_HOLLOW_BAR.keys())
    )
    raise ValueError(
        f"Unknown section '{section}'. "
        f"Valid sections: {', '.join(all_keys)}"
    )
