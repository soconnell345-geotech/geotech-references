"""Micropile figure lookup functions.

Digitized figures from FHWA-NHI-05-039, Micropile Design & Construction.
Follows the DM7 pattern: private data with ``_FIG_*`` prefix, public
lookup functions.

Currently contains Figure 5-23, the limiting lateral reaction modulus for
buckling of common micropile casings, bars and hollow bars.
"""

from geotech_references import _units as _u


# ============================================================================
# Figure 5-23: Limiting Lateral Modulus Values for Various Micropile
# Materials (after Cadden and Gomez, 2002)
# FHWA-NHI-05-039, p. 5-70 (PDF page 162). A bar chart; every bar carries its
# value in psi, printed above it. The values below are those printed numbers,
# read off the rendered page, left to right:
#
#   5.5"x0.36" 80 ksi casing   97     #10 Bar  610     30/16   295
#   7"x0.5" 80 ksi casing     105     #11 Bar  610     32/20   253
#   7"x0.73" 80 ksi casing    159     #14 Bar  610     40/20   310
#   9.625"x0.47" 80 ksi casing 71     #18 Bar  610     52/26   343
#   5 1/2-inch casing          27     #20 Bar  610     73/53   165
#   6 5/8-inch casing          23     #28 Bar  610     103/51  350
#   8-inch casing              19
#   10 3/4-inch casing         17
#
# The figure prints no steel grade for the four plain casings or the bars,
# and no word "hollow" for the last six; the `_a519` in four keys is this
# library's name for those casings, kept because callers use it.
# ============================================================================

_PSI_TO_KPA = 6.894757

# key: (label as printed under the bar, limiting Es in psi as printed)
_FIG_5_23_CASING = {
    "5.5x0.36_n80": ('5.5"x0.36" 80 ksi casing', 97),
    "7x0.5_n80": ('7"x0.5" 80 ksi casing', 105),
    "7x0.73_n80": ('7"x0.73" 80 ksi casing', 159),
    "9.625x0.47_n80": ('9.625"x0.47" 80 ksi casing', 71),
    "5.5_a519": ("5 1/2-inch casing", 27),
    "6.625_a519": ("6 5/8-inch casing", 23),
    "8_a519": ("8-inch casing", 19),
    "10.75_a519": ("10 3/4-inch casing", 17),
}

_FIG_5_23_BAR = {
    "#10": ("#10 Bar", 610),
    "#11": ("#11 Bar", 610),
    "#14": ("#14 Bar", 610),
    "#18": ("#18 Bar", 610),
    "#20": ("#20 Bar", 610),
    "#28": ("#28 Bar", 610),
}

_FIG_5_23_HOLLOW_BAR = {
    "30/16": ("30/16", 295),
    "32/20": ("32/20", 253),
    "40/20": ("40/20", 310),
    "52/26": ("52/26", 343),
    "73/53": ("73/53", 165),
    "103/51": ("103/51", 350),
}

# Other spellings of one printed bar. Anything not a key above or listed
# here is refused: '5.5' or '10' alone could be a casing or a bar.
_FIG_5_23_ALIASES = {
    "5.5x0.36": "5.5x0.36_n80",
    "7x0.5": "7x0.5_n80",
    "7x0.73": "7x0.73_n80",
    "9.625x0.47": "9.625x0.47_n80",
    "6.625": "6.625_a519",
    "10.75": "10.75_a519",
    "#10bar": "#10",
    "#11bar": "#11",
    "#14bar": "#14",
    "#18bar": "#18",
    "#20bar": "#20",
    "#28bar": "#28",
}

_FIG_5_23_REFERENCE = ("FHWA-NHI-05-039, Figure 5-23 Limiting Lateral Modulus "
                       "Values for Various Micropile Materials (after Cadden "
                       "and Gomez, 2002), p. 5-70")

_FIG_5_23_RULE = (
    "If Es LIMIT is less than the measured or assumed soil modulus Es, "
    "buckling does not need to be considered further; if Es LIMIT is greater "
    "than Es, buckling should be evaluated further (FHWA-NHI-05-039, p. 5-68)."
)


def _fig_5_23_entry(key, label, psi):
    return {
        "section": key,
        "description": label,
        "es_limit_kpa": int(round(psi * _PSI_TO_KPA)),
        "es_limit_psi": psi,
    }


@_u.labelled(
    {"es_limit_kpa": "kPa", "es_limit_psi": "psi"},
    printed_page="5-70", pdf_page_index=161)
def figure_5_23_limiting_lateral_modulus(section: str) -> dict:
    """Limiting lateral reaction modulus Es LIMIT for micropile buckling, in kPa and in psi as printed (FHWA-NHI-05-039 Figure 5-23, p. 5-70); buckling needs no further check when Es LIMIT is LESS than the soil's Es.

    Figure 5-23 (after Cadden and Gomez, 2002) is a bar chart of the limiting
    lateral reaction modulus of Eq. 5-29 for eight casings, six bars and six
    hollow bars; each bar carries its value in psi. Page 5-68: "if the
    Es LIMIT value is less than the measured or assumed soil modulus, Es,
    then the geotechnical and structural strength of the micropile will
    control the micropile capacity and buckling does not need to be
    considered further. If the Es LIMIT value is greater than Es, buckling
    should be evaluated further." Tables 5-12 and 5-13 give ranges of Es.

    Parameters
    ----------
    section : str
        One printed bar of the figure. Casings: '5.5x0.36_n80', '7x0.5_n80',
        '7x0.73_n80', '9.625x0.47_n80' (the 80 ksi casings), '5.5_a519',
        '6.625_a519', '8_a519', '10.75_a519' (the plain 5 1/2, 6 5/8, 8 and
        10 3/4 inch casings). Bars: '#10', '#11', '#14', '#18', '#20', '#28'.
        Hollow bars: '30/16', '32/20', '40/20', '52/26', '73/53', '103/51'.
        A key must name one bar; a partial key such as '5.5' is refused.
        Use '' or 'all' to get every bar.

    Returns
    -------
    dict
        section, description (the label printed under the bar),
        es_limit_kpa (the printed psi converted at 6.894757 kPa/psi),
        es_limit_psi (as printed), rule, reference. If section is '' or
        'all', a dict of all sections grouped as casings, bars, hollow_bars,
        with rule and reference.

    Raises
    ------
    ValueError
        If section does not name one printed bar.
    """
    key = section.strip().lower().replace(" ", "")

    if not key or key == "all":
        result = {"casings": {}, "bars": {}, "hollow_bars": {}}
        for group, table in (("casings", _FIG_5_23_CASING),
                             ("bars", _FIG_5_23_BAR),
                             ("hollow_bars", _FIG_5_23_HOLLOW_BAR)):
            for k, (label, psi) in table.items():
                entry = _fig_5_23_entry(k, label, psi)
                del entry["section"]
                result[group][k] = entry
        result["rule"] = _FIG_5_23_RULE
        result["reference"] = _FIG_5_23_REFERENCE
        return result

    key = _FIG_5_23_ALIASES.get(key, key)
    for table in (_FIG_5_23_CASING, _FIG_5_23_BAR, _FIG_5_23_HOLLOW_BAR):
        if key in table:
            label, psi = table[key]
            entry = _fig_5_23_entry(key, label, psi)
            entry["rule"] = _FIG_5_23_RULE
            entry["reference"] = _FIG_5_23_REFERENCE
            return entry

    all_keys = (
        list(_FIG_5_23_CASING.keys()) +
        list(_FIG_5_23_BAR.keys()) +
        list(_FIG_5_23_HOLLOW_BAR.keys())
    )
    raise ValueError(
        f"Unknown section '{section}'. Figure 5-23 (p. 5-70) has one bar for "
        f"each of: {', '.join(all_keys)}"
    )
