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


def _pick(rows, field, key, table, page, also=()):
    """Rows of a GEC-11 table whose ``field`` holds the filter ``key``.

    The key is looked for in ``field`` (case-insensitive); where no row
    holds it, every word of the key is looked for in ``field`` and the
    ``also`` fields. A key that matches no row raises ValueError listing
    the rows by the library's labels, which are not all worded as printed
    (review finding gec-37: it returned an empty list).
    """
    k = key.lower().strip()
    hits = [r for r in rows if k in str(r[field]).lower()]
    if not hits:
        words = k.replace(",", " ").split()

        def _text(r):
            return " ".join(str(r.get(f, "")) for f in (field,) + tuple(also)).lower()

        hits = [r for r in rows if words and all(w in _text(r) for w in words)]
    if not hits:
        names = []
        for r in rows:
            if r[field] not in names:
                names.append(r[field])
        raise ValueError(
            f"No row of GEC-11 {table} ({page}) matches '{key}'. "
            "Rows, by the library's labels (not all worded as printed; "
            f"filter with words from one): {'; '.join(names)}.")
    return hits


# ============================================================================
# Table 2-1: Minimum Reinforcement Length
# ============================================================================

_TABLE_2_1_REF = "FHWA-NHI-10-024, Table 2-1, p. 2-43"

# FHWA-NHI-10-024 Vol I, Table 2-1, p. 2-43 (PDF page 83): three cases, as
# printed. The table prints no absolute minimum length (review finding gec-21:
# two seismic rows the table does not have and 8 ft on every row).
_TABLE_2_1 = [
    {
        "condition": "Static loading with or without traffic surcharge",
        "typical_min_L_over_H": "0.7",
        "L_over_H_low": 0.7,
        "L_over_H_high": 0.7,
        "print_note": ("Table 2-1 (p. 2-43) prints this case as 'Static "
                       "loading with or with traffic surcharge'; it is read "
                       "here as 'with or without'."),
    },
    {
        "condition": "Sloping backfill surcharge",
        "typical_min_L_over_H": "0.8",
        "L_over_H_low": 0.8,
        "L_over_H_high": 0.8,
    },
    {
        "condition": "Seismic loading",
        "typical_min_L_over_H": "0.8 to 1.1",
        "L_over_H_low": 0.8,
        "L_over_H_high": 1.1,
    },
]


def table_2_1_min_reinforcement_length(condition: str = "") -> list:
    """Typical minimum reinforcement length as the ratio L/H (dimensionless, reinforcement length over wall height) for each case of GEC-11 Table 2-1 (FHWA-NHI-10-024 Vol I, p. 2-43); a list of the matching rows.

    The table prints three cases: static loading with or without traffic
    surcharge 0.7, sloping backfill surcharge 0.8, and seismic loading
    "0.8 to 1.1" (one row; the print does not divide it by seismic zone).
    ``typical_min_L_over_H`` is the printed cell; ``L_over_H_low`` and
    ``L_over_H_high`` are its ends.

    The table prints no absolute minimum length. Section 4.4.3 (p. 4-11)
    says the preliminary length "should be the greater of 0.7H or 8 ft
    (2.5 m)", the 8 ft to suit fill spreading and compaction equipment,
    and that about 6.0 ft (1.8 m) can be considered for short walls built
    with smaller compaction equipment, keeping 0.7H.

    Parameters
    ----------
    condition : str
        Optional filter, matched against the printed case (e.g. 'static',
        'sloping', 'seismic'). A filter that matches no case raises
        ValueError naming the cases.

    Returns
    -------
    list of dict
        Matching rows: condition, typical_min_L_over_H (the printed text),
        L_over_H_low, L_over_H_high, reference; the static row also
        print_note (the table prints "with or with traffic surcharge").
    """
    rows = [dict(r, reference=_TABLE_2_1_REF) for r in _TABLE_2_1]
    if not condition:
        return rows
    return _pick(rows, "condition", condition, "Table 2-1", "p. 2-43")


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


_TABLE_2_2_NOTE = (
    "All geometries: 2 ft minimum. * Minimum depth is the greater of "
    "applicable values listed, frost depth, or scour depth.")


def table_2_2_min_embedment_depth(condition: str = "") -> list:
    """Minimum MSE wall embedment depth to the top of the leveling pad, as a fraction of wall height H with a 2 ft (0.6 m) minimum, by slope in front of the wall, from GEC-11 Table 2-2 (FHWA-NHI-10-024 Vol I, p. 2-43); a list of the matching rows.

    Parameters
    ----------
    condition : str
        Optional filter (case-insensitive), e.g. 'horizontal', 'abutment',
        '2H:1V'. A filter that matches no row raises ValueError naming
        the rows.

    Returns
    -------
    list of dict
        Matching rows with the embedment ratio, the 2 ft minimum, the
        table's footnote (frost and scour depth) and the reference.
    """
    rows = [dict(r, notes=_TABLE_2_2_NOTE,
                 reference="FHWA-NHI-10-024, Table 2-2, p. 2-43")
            for r in _TABLE_2_2]
    if not condition:
        return rows
    return _pick(rows, "condition", condition, "Table 2-2", "p. 2-43")


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

# FHWA-NHI-10-024 Vol I, Table 3-4, p. 3-10 (PDF page 102), after FHWA
# NHI-09-087: two rows as printed. The code held PP and HDPE as two rows
# with notes the table does not print, so the print's own row name
# 'polyolefin' matched nothing.
_TABLE_3_4 = [
    {
        "polymer": "Polyester (PET)",
        "property": "pH",
        "criteria": "3 < pH < 9",
        "pH_min": 3.0,
        "pH_max": 9.0,
        "test_method": "AASHTO T-289",
    },
    {
        "polymer": "Polyolefin (PP & HDPE)",
        "property": "pH",
        "criteria": "pH > 3",
        "pH_min": 3.0,
        "pH_max": None,
        "test_method": "AASHTO T-289",
    },
]


def table_3_4_electrochemical_geosynth(polymer: str = "") -> list:
    """Recommended pH limits for reinforced fill with geosynthetic reinforcement, by base polymer, from GEC-11 Table 3-4 (FHWA-NHI-10-024 Vol I, p. 3-10); a list of the matching rows.

    The table prints two rows: polyester (PET) 3 < pH < 9 and polyolefin
    (PP & HDPE) pH > 3, both by AASHTO T-289. ``criteria`` is the printed
    cell; the bounds are strict.

    Parameters
    ----------
    polymer : str
        Optional filter, e.g. 'PET', 'polyolefin', 'PP', 'HDPE'. A filter
        that matches no row raises ValueError naming the rows.

    Returns
    -------
    list of dict
        Matching rows: polymer, property, criteria, pH_min, pH_max,
        test_method, reference.
    """
    rows = [dict(r, reference="FHWA-NHI-10-024, Table 3-4, p. 3-10")
            for r in _TABLE_3_4]
    if not polymer:
        return rows
    return _pick(rows, "polymer", polymer, "Table 3-4", "p. 3-10")


# ============================================================================
# Table 3-6: Pullout Capacity Design Parameters
# ============================================================================
# Source: FHWA-NHI-10-024 (Nov 2009) Vol I, Table 3-6 (p. 3-17), with the F*
# defaults of Section 3.4.2 (p. 3-20: Eqs. 3-4 to 3-7; p. 3-21: Eq. 3-8) and
# alpha of p. 3-16. Table 3-6 itself lists, per reinforcement type, which
# parameter comes from tests ("Obtain Tan rho from tests") and the alpha
# default; the F* defaults are the equations of Section 3.4.2.
#
# Note (i) of Table 3-6 (printed p. 3-17): the empirical values may be used
# for F* in the absence of product- and backfill-specific test data, "provided
# granular reinforced fill as specified in Table 3-1 for MSE walls is used and
# Cu >= 4. For fill outside these limits, tests must be run." Every row
# carries it in "default_fill_limit". Note (ii): pullout testing to determine
# alpha is recommended if alpha is less than 1.0.
#
# Row fields: reinforcement, F_star_at_top, F_star_at_6m, alpha, notes (the
# original keys) plus equations, printed_pages, default_fill_limit and, where
# the print gives them, F_star_top_max, Cu_if_unknown, F_star_top_if_Cu_unknown.

_TABLE_3_6_NOTE_I = (
    "Note (i), p. 3-17: the defaults may be used only with granular reinforced "
    "fill as specified in Table 3-1 for MSE walls and Cu >= 4; for fill outside "
    "these limits, pullout tests must be run."
)

_TABLE_3_6 = [
    {
        "reinforcement": "Ribbed steel strips (inextensible strips)",
        "F_star_at_top": "1.2 + log10(Cu), 2.0 maximum",
        "F_star_at_6m": "tan(phi)",
        "alpha": 1.0,
        "F_star_top_max": 2.0,
        "Cu_if_unknown": 4,
        "F_star_top_if_Cu_unknown": 1.8,
        "equations": ["3-4", "3-5"],
        "printed_pages": ["3-17", "3-20"],
        "default_fill_limit": _TABLE_3_6_NOTE_I,
        "notes": (
            "F* = tan(rho) = 1.2 + log Cu at the top of the structure, 2.0 "
            "maximum (Eq. 3-4); F* = tan(phi) at a depth of 20 ft (6 m) and "
            "below (Eq. 3-5); Cu = D60/D10 of the backfill. If the specific "
            "Cu is unknown at design time, assume Cu = 4 (F* = 1.8 at the top "
            "of the wall) for reinforced fill meeting Section 3.1 (printed in "
            "bold, p. 3-20). Table 3-6: inextensible strips, alpha = 1.0. "
            "The print gives the top and the 6 m values only; it does not "
            "state how F* varies between them."
        ),
    },
    {
        "reinforcement": "Smooth steel strips (inextensible strips)",
        "F_star_at_top": "tan(rho) from tests; no default printed",
        "F_star_at_6m": "tan(rho) from tests; no default printed",
        "alpha": 1.0,
        "equations": [],
        "printed_pages": ["3-17"],
        "default_fill_limit": _TABLE_3_6_NOTE_I,
        "notes": (
            "Table 3-6 has one row for inextensible strips: Tan rho from "
            "tests, or use default values; alpha = 1.0. The only default F* "
            "the section prints for strips is the ribbed-strip pair of Eqs. "
            "3-4 and 3-5 (p. 3-20); no separate F* for smooth strips is "
            "printed (the 0.4 this row carried before is not in the 2009 "
            "print)."
        ),
    },
    {
        "reinforcement": "Steel grids (bar mats and welded wire; inextensible grids)",
        "F_star_at_top": "20 * (t/St)",
        "F_star_at_6m": "10 * (t/St)",
        "alpha": 1.0,
        "equations": ["3-6", "3-7"],
        "printed_pages": ["3-17", "3-20", "3-21"],
        "default_fill_limit": _TABLE_3_6_NOTE_I,
        "notes": (
            "For transverse spacing St > 6 in. (150 mm): F* = Fq * alpha_beta "
            "= 40 alpha_beta = 40 (t/2St) = 20 (t/St) at the top of the "
            "structure (Eq. 3-6) and = 20 alpha_beta = 20 (t/2St) = 10 (t/St) "
            "at a depth of 20 ft (6 m) and below (Eq. 3-7); t is the "
            "thickness of the transverse bar; St must be uniform along the "
            "reinforcement; the maximum St is 24 in. (610 mm). Table 3-6: for "
            "St <= Sopt, Tan rho from tests (Sopt = t Fq / (2 tan phi)); for "
            "St > Sopt, Fq from tests or default values, alpha_beta = t/2St; "
            "alpha = 1.0 (*for longitudinal bars/wires spaced more than 6 in., "
            "alpha may be less than 1.0 and pullout tests are required)."
        ),
    },
    {
        "reinforcement": "Geogrids (extensible grids)",
        "F_star_at_top": "(2/3) * tan(phi)",
        "F_star_at_6m": "(2/3) * tan(phi)",
        "alpha": 0.8,
        "equations": ["3-8"],
        "printed_pages": ["3-16", "3-17", "3-21"],
        "default_fill_limit": _TABLE_3_6_NOTE_I,
        "notes": (
            "For geosynthetic (geogrid and geotextile) sheet reinforcement, "
            "in the absence of test data F* is conservatively taken as "
            "(2/3) tan(phi) (Eq. 3-8, i.e. 0.67 tan phi), phi the peak "
            "friction angle (MSE walls with select granular backfill: 34 deg "
            "maximum unless tests support more; RSS: by test, 28 deg lower "
            "bound often used). Table 3-6: extensible grids, alpha = 0.8 "
            "(also p. 3-16: alpha = 0.8 for geogrids absent test data); when "
            "the minimum grid opening / D50 is greater than 1, Tan rho from "
            "tests for St <= Sopt and Fq from tests (alpha_beta = fb t/2St) "
            "for St > Sopt, and when it is less than 1, Tan rho from tests. "
            "Pullout testing for alpha is recommended where alpha < 1.0 "
            "(note ii)."
        ),
    },
    {
        "reinforcement": "Geotextiles (extensible sheets)",
        "F_star_at_top": "(2/3) * tan(phi)",
        "F_star_at_6m": "(2/3) * tan(phi)",
        "alpha": 0.6,
        "equations": ["3-8"],
        "printed_pages": ["3-16", "3-17", "3-21"],
        "default_fill_limit": _TABLE_3_6_NOTE_I,
        "notes": (
            "Extensible sheets: Tan rho from tests; alpha = 0.6 (also p. "
            "3-16: alpha = 0.6 for geotextiles absent test data). In the "
            "absence of test data F* = (2/3) tan(phi) (Eq. 3-8). Pullout "
            "testing for alpha is recommended where alpha < 1.0 (note ii)."
        ),
    },
]


def table_3_6_pullout_parameters(reinforcement: str = "") -> list:
    """Look up pullout capacity design parameters from GEC-11 Table 3-6.

    Parameters
    ----------
    reinforcement : str
        Optional filter (e.g., 'ribbed', 'grid', 'geogrid', 'geotextile').
        A filter that matches no row raises ValueError naming the rows.

    Returns
    -------
    list of dict
        Matching entries with F* and alpha values.
    """
    if not reinforcement:
        return list(_TABLE_3_6)
    return _pick(_TABLE_3_6, "reinforcement", reinforcement,
                 "Table 3-6", "p. 3-17")


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
        Optional filter (e.g., 'zinc', 'carbon', 'steel'). A filter that
        matches no row raises ValueError naming the rows.

    Returns
    -------
    list of dict
        Corrosion rates in micrometers per year.
    """
    if not material:
        return list(_TABLE_3_8)
    return _pick(_TABLE_3_8, "material", material, "Table 3-8", "p. 3-26")


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


_TABLE_3_9_BACKFILL = {
    "type1_backfill": "Max. size 4 in. (100 mm), D50 about 1-1/4 in. (30 mm)",
    "type2_backfill": "Max. size 3/4 in. (20 mm), D50 about #30 (0.7 mm)",
}
_TABLE_3_9_NOTE_A = "a. Minimum weight 8.0 oz/yd2 (270 g/m2)."


def table_3_9_installation_damage(geosynthetic: str = "") -> list:
    """Installation damage reduction factor RF_ID ranges (dimensionless) by geosynthetic, for Type 1 and Type 2 backfill, from GEC-11 Table 3-9 (FHWA-NHI-10-024 Vol I, p. 3-32); a list of the matching rows.

    The print defines the backfills in the column heads: Type 1, max. size
    4 in. (100 mm), D50 about 1-1/4 in. (30 mm); Type 2, max. size 3/4 in.
    (20 mm), D50 about #30 (0.7 mm). Each row carries both definitions;
    the three geotextile rows carry footnote a (minimum weight 8.0 oz/yd2).

    Parameters
    ----------
    geosynthetic : str
        Optional filter (e.g., 'HDPE', 'PP biaxial', 'PVC', 'woven'). A
        filter that matches no row raises ValueError naming the rows.

    Returns
    -------
    list of dict
        RF_ID ranges for Type 1 and Type 2 backfill.
    """
    rows = []
    for r in _TABLE_3_9:
        row = dict(r, **_TABLE_3_9_BACKFILL)
        if "geotextile" in r["geosynthetic"].lower():
            row["notes"] = _TABLE_3_9_NOTE_A
        row["reference"] = "FHWA-NHI-10-024, Table 3-9, p. 3-32"
        rows.append(row)
    if not geosynthetic:
        return rows
    return _pick(rows, "geosynthetic", geosynthetic, "Table 3-9", "p. 3-32")


# ============================================================================
# Table 3-11: PET Durability Reduction Factors (RF_D)
# ============================================================================

_TABLE_3_11 = [
    {
        "product": "Geotextiles (Mn < 20,000, 40 < CEG < 50)",
        "pH_5_to_8": 1.6,
        "pH_3_to_5_or_8_to_9": 2.0,
        "notes": "Lower molecular weight PET; more susceptible to hydrolysis",
    },
    {
        "product": "Coated geogrids, Geotextiles (Mn > 25,000, CEG < 30)",
        "pH_5_to_8": 1.15,
        "pH_3_to_5_or_8_to_9": 1.3,
        "notes": "Higher molecular weight PET; better durability",
    },
]


def table_3_11_pet_durability(product: str = "") -> list:
    """Look up PET durability reduction factors from GEC-11 Table 3-11.

    GEC-11 Vol I Table 3-11 (p. 3-36) lists geotextiles in both rows; the
    row depends on Mn and CEG. So 'geotextile' returns both rows, and
    'geogrid' or 'coated' returns only the Mn > 25,000, CEG < 30 row.

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
    return _pick(_TABLE_3_11, "product", product, "Table 3-11", "p. 3-36")


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
        "notes": ("gamma_EQ = load factor for live load applied "
                  "simultaneously with seismic loads (Table 4-1 note)"),
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
    return _pick(_TABLE_4_1, "limit_state", limit_state, "Table 4-1", "p. 4-4")


# ============================================================================
# Table 4-2: Permanent Load Factors (gamma_p)
# ============================================================================

_TABLE_4_2 = [
    {
        "load_type": "DC",
        "description": "DC: Component and Attachments",
        "gamma_max": 1.25,
        "gamma_min": 0.90,
    },
    {
        "load_type": "EH Active",
        "description": "EH: Horizontal Earth Pressure, Active",
        "gamma_max": 1.50,
        "gamma_min": 0.90,
    },
    {
        "load_type": "EV Overall Stability",
        "description": "EV: Vertical Earth Pressure, Overall Stability",
        "gamma_max": 1.00,
        "gamma_min": None,
    },
    {
        "load_type": "EV Retaining Walls",
        "description": ("EV: Vertical Earth Pressure, Retaining Walls "
                        "and Abutments"),
        "gamma_max": 1.35,
        "gamma_min": 1.00,
    },
    {
        "load_type": "ES",
        "description": "ES: Earth Surcharge",
        "gamma_max": 1.50,
        "gamma_min": 0.75,
    },
]


def table_4_2_permanent_load_factors(load_type: str = "") -> list:
    """Look up permanent load factors from GEC-11 Table 4-2.

    Parameters
    ----------
    load_type : str
        Optional filter (e.g., 'DC', 'EH', 'EV', 'ES'), matched against
        the load code, then word by word against the printed type of load
        ('vertical earth pressure'). A filter that matches no row raises
        ValueError naming the rows.

    Returns
    -------
    list of dict
        Max and min load factors by load type.
    """
    if not load_type:
        return list(_TABLE_4_2)
    return _pick(_TABLE_4_2, "load_type", load_type, "Table 4-2", "p. 4-4",
                 also=("description",))


# ============================================================================
# Table 4-4: Equivalent Height for Traffic Surcharge on Abutments
# ============================================================================

_TABLE_4_4_DEPTHS_FT = [5.0, 10.0, 20.0]
_TABLE_4_4_HEQ_FT = [4.0, 3.0, 2.0]


_TABLE_4_4_REF = "FHWA-NHI-10-024, Table 4-4, p. 4-17 (AASHTO 2007 Table 3.11.6.4-1)"
_TABLE_4_4_APPLIES = ("Traffic loading on abutments perpendicular to traffic "
                      "(Table 4-4 title)")
_TABLE_4_4_NOTE = (
    "Walls parallel to traffic: heq = 2.0 ft for external stability, and for "
    "internal stability unless traffic is allowed within 1.0 ft of the back "
    "of the wall facing (p. 4-16). Where a structural approach slab is "
    "supported on the abutment backwall, heq = 0 unless otherwise mandated "
    "by an owner (p. 4-17).")


def table_4_4_traffic_surcharge(abutment_height_ft: float = 0.0) -> dict:
    """Equivalent height of soil heq in feet for traffic loading on abutments perpendicular to traffic, from the abutment height in feet, GEC-11 Table 4-4 (FHWA-NHI-10-024 Vol I, p. 4-17).

    The table prints abutment heights 5.0, 10.0 and >= 20.0 ft (heq 4.0,
    3.0 and 2.0 ft) and is interpolated linearly between them, as p. 4-17
    says. It is for abutments with traffic running perpendicular to the
    wall; walls parallel to traffic take heq = 2.0 ft (p. 4-16), and every
    result says so. Below 5.0 ft, where the table has no row, the 5.0 ft
    row is used with a note.

    Parameters
    ----------
    abutment_height_ft : float
        Abutment height in feet. If 0, returns the full table.

    Returns
    -------
    dict
        abutment_height_ft, h_eq_ft, applies_to, print_note, the table and
        the reference (and a note below 5.0 ft).
    """
    table = [
        {"abutment_height_ft": d, "h_eq_ft": h}
        for d, h in zip(_TABLE_4_4_DEPTHS_FT, _TABLE_4_4_HEQ_FT)
    ]
    out = {"applies_to": _TABLE_4_4_APPLIES, "print_note": _TABLE_4_4_NOTE}

    if abutment_height_ft <= 0:
        return dict(out, table=table, reference=_TABLE_4_4_REF)

    note = None
    if abutment_height_ft < 5.0:
        h_eq = 4.0
        note = ("Table 4-4 prints no row below an abutment height of 5.0 ft; "
                "the 5.0 ft row is used.")
    elif abutment_height_ft >= 20.0:
        h_eq = 2.0
    else:
        h_eq = _linterp(abutment_height_ft, _TABLE_4_4_DEPTHS_FT, _TABLE_4_4_HEQ_FT)

    out = dict({"abutment_height_ft": abutment_height_ft,
                "h_eq_ft": round(h_eq, 2)}, **out)
    if note:
        out["note"] = note
    out["table"] = table
    out["reference"] = _TABLE_4_4_REF
    return out


# ============================================================================
# Table 4-5: External Stability Resistance Factors
# ============================================================================

_TABLE_4_5 = [
    {
        "failure_mode": "Bearing resistance",
        "phi_factor": 0.65,
        "condition": None,
    },
    {
        "failure_mode": "Sliding",
        "phi_factor": 1.0,
        "condition": None,
    },
    {
        "failure_mode": "Overall (global) stability — well-defined conditions",
        "phi_factor": 0.75,
        "condition": ("Where geotechnical parameters are well defined, "
                      "and the slope does not support or contain a "
                      "structural element"),
    },
    {
        "failure_mode": "Overall (global) stability — limited information",
        "phi_factor": 0.65,
        "condition": ("Where geotechnical parameters are based on "
                      "limited information, or the slope contains or "
                      "supports a structural element"),
    },
]


def table_4_5_external_resistance(failure_mode: str = "") -> list:
    """Look up external stability resistance factors from GEC-11 Table 4-5.

    Parameters
    ----------
    failure_mode : str
        Optional filter (e.g., 'bearing', 'sliding', 'global', 'overall').
        A filter that matches no row raises ValueError naming the rows.

    Returns
    -------
    list of dict
        Resistance factors by failure mode, with the printed condition.
    """
    if not failure_mode:
        return list(_TABLE_4_5)
    return _pick(_TABLE_4_5, "failure_mode", failure_mode, "Table 4-5",
                 "p. 4-19", also=("condition",))


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

# FHWA-NHI-10-024 Vol I, Table 4-7, p. 4-48 (PDF page 190), after AASHTO
# (2007) Table 11.5.6-1: the printed loading conditions are "Static loading",
# "Combined static/earthquake loading" and "Combined static/traffic barrier
# impact". The key combined_static_phi (a copy of the static factor, no
# printed column) was removed (review finding gec-34).
_TABLE_4_7_NOTE_A = (
    "A. Apply to gross cross-section less sacrificial area. For sections "
    "with holes, reduce gross area in accordance with AASHTO (2007) Article "
    "6.8.3 and apply to net section less sacrificial area.")
_TABLE_4_7_NOTE_B = (
    "B. Combined static/traffic barrier impact resistance factors are not "
    "presented in AASHTO.")
_TABLE_4_7_NOTE_C = (
    "C. Applies to grid reinforcements connected to rigid facing element, "
    "e.g., a concrete panel or block. For grid reinforcements connected to a "
    "flexible facing mat or which are continuous with the facing mat, use "
    "the resistance factor for strip reinforcements.")

_TABLE_4_7 = [
    {
        "reinforcement_type": ("Metallic reinforcement and connectors: "
                               "strip reinforcements"),
        "static_phi": 0.75,
        "combined_static_earthquake_phi": 1.00,
        "combined_static_traffic_barrier_phi": 1.00,
        "notes": [_TABLE_4_7_NOTE_A, _TABLE_4_7_NOTE_B],
    },
    {
        "reinforcement_type": ("Metallic reinforcement and connectors: "
                               "grid reinforcements"),
        "static_phi": 0.65,
        "combined_static_earthquake_phi": 0.85,
        "combined_static_traffic_barrier_phi": 0.85,
        "notes": [_TABLE_4_7_NOTE_A, _TABLE_4_7_NOTE_B, _TABLE_4_7_NOTE_C],
    },
    {
        "reinforcement_type": "Geosynthetic reinforcement and connectors",
        "static_phi": 0.90,
        "combined_static_earthquake_phi": 1.20,
        "combined_static_traffic_barrier_phi": 1.20,
        "notes": [_TABLE_4_7_NOTE_B],
    },
    {
        "reinforcement_type": ("Pullout resistance of tensile reinforcement "
                               "(metallic and geosynthetic)"),
        "static_phi": 0.90,
        "combined_static_earthquake_phi": 1.20,
        "combined_static_traffic_barrier_phi": 1.00,
        "notes": [_TABLE_4_7_NOTE_B],
    },
]


def table_4_7_internal_resistance(reinforcement_type: str = "") -> list:
    """Resistance factors phi (dimensionless) for tensile and pullout resistance of MSE wall reinforcement, by reinforcement type and loading condition, from GEC-11 Table 4-7 (FHWA-NHI-10-024 Vol I, p. 4-48); a list of the matching rows.

    Each row gives the three printed loading conditions: ``static_phi``
    (static loading), ``combined_static_earthquake_phi`` (combined
    static/earthquake loading) and ``combined_static_traffic_barrier_phi``
    (combined static/traffic barrier impact, note B), with the table's
    notes A to C as they apply.

    Parameters
    ----------
    reinforcement_type : str
        Optional filter, matched against the printed type and then word by
        word (e.g. 'metallic strip', 'grid', 'geosynthetic', 'pullout').
        A filter that matches no row raises ValueError naming the rows.

    Returns
    -------
    list of dict
        Matching rows: reinforcement_type, the three resistance factors,
        notes, reference.
    """
    rows = [dict(r, reference="FHWA-NHI-10-024, Table 4-7, p. 4-48")
            for r in _TABLE_4_7]
    if not reinforcement_type:
        return rows
    return _pick(rows, "reinforcement_type", reinforcement_type,
                 "Table 4-7", "p. 4-48")
