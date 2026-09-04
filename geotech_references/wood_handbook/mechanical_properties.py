"""Wood Handbook Chapter 5 -- Mechanical Properties of Wood (clear-wood
strength/stiffness properties, moisture-content adjustment, and temperature
effects).

SPECIES SUBSET RULE: Table 5-3 (the handbook's most extensively sampled
clear-wood property table, printed p. 5-6 to 5-8) covers ~180 species. This
module digitizes a documented structural subset covering the species that
make up the commercially important NDS softwood combination groups, plus a
handful of common hardwoods, rather than the full table:
  - Douglas-fir (Coast, Interior North, Interior West -- the Douglas
    Fir-Larch group's principal species, plus western larch itself).
  - Southern Pine group constituents: loblolly, longleaf, shortleaf, slash.
  - Hem-Fir group constituents: western hemlock plus the true firs
    (California red, grand, noble, Pacific silver, white).
  - Spruce-Pine-Fir (SPF) group constituents: Engelmann spruce, lodgepole
    pine, jack pine, subalpine fir, balsam fir.
  - Six hardwoods in common structural/general use: white ash, black
    cherry, sugar maple, northern red oak, white oak, yellow-poplar.
This is the SAME 27-species subset digitized in
``moisture_relations.TABLE_4_3_SHRINKAGE`` and referenced by
``moisture_relations.TABLE_4_1_GREEN_MC``, so a species can be looked up
consistently across both chapters. NDS design values and adjustment
factors (the tabulated allowable design stresses derived from this
clear-wood data by the National Design Specification) are OUT OF SCOPE --
NDS is a separate copyrighted standard; this module implements only the
Wood Handbook's own printed clear-wood data and equations.

Provides:
  - ``table_5_3_mechanical_properties`` -- clear-wood strength/stiffness
    properties (Table 5-3a, metric units) at green and 12% moisture
    content, for the species subset above.
  - ``adjust_property_for_moisture_content`` -- Eq 5-3, adjusting a clear-
    wood property from 12% MC to any other MC below the fiber saturation
    point, using the species' intersection MC Mp (Table 5-13).
  - ``table_5_15_temperature_effect`` -- approximate percentage change in
    mechanical properties at -50 degC and +50 degC relative to 20 degC,
    by property and moisture condition (Table 5-15).
  - ``table_5_16_temperature_adjustment`` -- the quadratic printed
    equation form for percentage change in lumber bending properties (MOE,
    MOR) with temperature (Table 5-16).

All printed citations use the PRINTED page of General Technical Report
FPL-GTR-282 (2021 edition); ``pdf_page = printed_page + 115`` for Chapter 5
in this PDF (0-based PyMuPDF page index).

UNITS: Table 5-3a metric units throughout: specific gravity (dimensionless,
ovendry mass basis), MOR/comp/shear/tension in kPa, MOE in MPa, work-to-
maximum-load in kJ/m^3, impact bending in mm (drop height), side hardness
in N.
"""

# ============================================================================
# Table 5-3a -- Strength properties of some commercially important woods
# grown in the United States (metric), green and 12% MC
# (printed pp. 5-5 to 5-8, pdf_page 120-123)
# ============================================================================

# Each species: {"green": {...}, "12": {...}}. None = "-" (not reported) in
# the printed table. Columns: sg (specific gravity), mor_kpa (modulus of
# rupture), moe_mpa (modulus of elasticity), wml_kj_m3 (work to maximum
# load), impact_mm (impact bending), comp_parallel_kpa, comp_perp_kpa
# (compression parallel/perpendicular to grain), shear_kpa (shear parallel
# to grain), tension_perp_kpa (tension perpendicular to grain),
# side_hardness_n.
TABLE_5_3_PROPERTIES = {
    # ---- Hardwoods ----
    "ash, white": {
        "green": {"sg": 0.55, "mor_kpa": 66000, "moe_mpa": 9900, "wml_kj_m3": 108,
                   "impact_mm": 970, "comp_parallel_kpa": 27500, "comp_perp_kpa": 4600,
                   "shear_kpa": 9300, "tension_perp_kpa": 4100, "side_hardness_n": 4300},
        "12": {"sg": 0.60, "mor_kpa": 106000, "moe_mpa": 12000, "wml_kj_m3": 115,
               "impact_mm": 1090, "comp_parallel_kpa": 51100, "comp_perp_kpa": 8000,
               "shear_kpa": 13200, "tension_perp_kpa": 6500, "side_hardness_n": 5900},
    },
    "cherry, black": {
        "green": {"sg": 0.47, "mor_kpa": 55000, "moe_mpa": 9000, "wml_kj_m3": 88,
                   "impact_mm": 840, "comp_parallel_kpa": 24400, "comp_perp_kpa": 2500,
                   "shear_kpa": 7800, "tension_perp_kpa": 3900, "side_hardness_n": 2900},
        "12": {"sg": 0.50, "mor_kpa": 85000, "moe_mpa": 10300, "wml_kj_m3": 79,
               "impact_mm": 740, "comp_parallel_kpa": 49000, "comp_perp_kpa": 4800,
               "shear_kpa": 11700, "tension_perp_kpa": 3900, "side_hardness_n": 4200},
    },
    "maple, sugar": {
        "green": {"sg": 0.56, "mor_kpa": 65000, "moe_mpa": 10700, "wml_kj_m3": 92,
                   "impact_mm": 1020, "comp_parallel_kpa": 27700, "comp_perp_kpa": 4400,
                   "shear_kpa": 10100, "tension_perp_kpa": None, "side_hardness_n": 4300},
        "12": {"sg": 0.63, "mor_kpa": 109000, "moe_mpa": 12600, "wml_kj_m3": 114,
               "impact_mm": 990, "comp_parallel_kpa": 54000, "comp_perp_kpa": 10100,
               "shear_kpa": 16100, "tension_perp_kpa": None, "side_hardness_n": 6400},
    },
    "oak, northern red": {
        "green": {"sg": 0.56, "mor_kpa": 57000, "moe_mpa": 9300, "wml_kj_m3": 91,
                   "impact_mm": 1120, "comp_parallel_kpa": 23700, "comp_perp_kpa": 4200,
                   "shear_kpa": 8300, "tension_perp_kpa": 5200, "side_hardness_n": 4400},
        "12": {"sg": 0.63, "mor_kpa": 99000, "moe_mpa": 12500, "wml_kj_m3": 100,
               "impact_mm": 1090, "comp_parallel_kpa": 46600, "comp_perp_kpa": 7000,
               "shear_kpa": 12300, "tension_perp_kpa": 5500, "side_hardness_n": 5700},
    },
    "oak, white": {
        "green": {"sg": 0.60, "mor_kpa": 57000, "moe_mpa": 8600, "wml_kj_m3": 80,
                   "impact_mm": 1070, "comp_parallel_kpa": 24500, "comp_perp_kpa": 4600,
                   "shear_kpa": 8600, "tension_perp_kpa": 5300, "side_hardness_n": 4700},
        "12": {"sg": 0.68, "mor_kpa": 105000, "moe_mpa": 12300, "wml_kj_m3": 102,
               "impact_mm": 940, "comp_parallel_kpa": 51300, "comp_perp_kpa": 7400,
               "shear_kpa": 13800, "tension_perp_kpa": 5500, "side_hardness_n": 6000},
    },
    "yellow-poplar": {
        "green": {"sg": 0.40, "mor_kpa": 41000, "moe_mpa": 8400, "wml_kj_m3": 52,
                   "impact_mm": 660, "comp_parallel_kpa": 18300, "comp_perp_kpa": 1900,
                   "shear_kpa": 5400, "tension_perp_kpa": 3500, "side_hardness_n": 2000},
        "12": {"sg": 0.42, "mor_kpa": 70000, "moe_mpa": 10900, "wml_kj_m3": 61,
               "impact_mm": 610, "comp_parallel_kpa": 38200, "comp_perp_kpa": 3400,
               "shear_kpa": 8200, "tension_perp_kpa": 3700, "side_hardness_n": 2400},
    },
    # ---- Softwoods: Douglas-fir (Douglas Fir-Larch group) ----
    "douglas-fir, coast": {
        "green": {"sg": 0.45, "mor_kpa": 53000, "moe_mpa": 10800, "wml_kj_m3": 52,
                   "impact_mm": 660, "comp_parallel_kpa": 26100, "comp_perp_kpa": 2600,
                   "shear_kpa": 6200, "tension_perp_kpa": 2100, "side_hardness_n": 2200},
        "12": {"sg": 0.48, "mor_kpa": 85000, "moe_mpa": 13400, "wml_kj_m3": 68,
               "impact_mm": 790, "comp_parallel_kpa": 49900, "comp_perp_kpa": 5500,
               "shear_kpa": 7800, "tension_perp_kpa": 2300, "side_hardness_n": 3200},
    },
    "douglas-fir, interior north": {
        "green": {"sg": 0.45, "mor_kpa": 51000, "moe_mpa": 9700, "wml_kj_m3": 56,
                   "impact_mm": 560, "comp_parallel_kpa": 23900, "comp_perp_kpa": 2500,
                   "shear_kpa": 6600, "tension_perp_kpa": 2300, "side_hardness_n": 1900},
        "12": {"sg": 0.48, "mor_kpa": 90000, "moe_mpa": 12300, "wml_kj_m3": 72,
               "impact_mm": 660, "comp_parallel_kpa": 47600, "comp_perp_kpa": 5300,
               "shear_kpa": 9700, "tension_perp_kpa": 2700, "side_hardness_n": 2700},
    },
    "douglas-fir, interior west": {
        "green": {"sg": 0.46, "mor_kpa": 53000, "moe_mpa": 10400, "wml_kj_m3": 50,
                   "impact_mm": 660, "comp_parallel_kpa": 26700, "comp_perp_kpa": 2900,
                   "shear_kpa": 6500, "tension_perp_kpa": 2000, "side_hardness_n": 2300},
        "12": {"sg": 0.50, "mor_kpa": 87000, "moe_mpa": 12600, "wml_kj_m3": 73,
               "impact_mm": 810, "comp_parallel_kpa": 51200, "comp_perp_kpa": 5200,
               "shear_kpa": 8900, "tension_perp_kpa": 2400, "side_hardness_n": 2900},
    },
    "larch, western": {
        "green": {"sg": 0.48, "mor_kpa": 53000, "moe_mpa": 10100, "wml_kj_m3": 71,
                   "impact_mm": 740, "comp_parallel_kpa": 25900, "comp_perp_kpa": 2800,
                   "shear_kpa": 6000, "tension_perp_kpa": 2300, "side_hardness_n": 2300},
        "12": {"sg": 0.52, "mor_kpa": 90000, "moe_mpa": 12900, "wml_kj_m3": 87,
               "impact_mm": 890, "comp_parallel_kpa": 52500, "comp_perp_kpa": 6400,
               "shear_kpa": 9400, "tension_perp_kpa": 3000, "side_hardness_n": 3700},
    },
    # ---- Softwoods: Fir (Hem-Fir group true firs, plus balsam/subalpine) ----
    "fir, balsam": {
        "green": {"sg": 0.33, "mor_kpa": 38000, "moe_mpa": 8600, "wml_kj_m3": 32,
                   "impact_mm": 410, "comp_parallel_kpa": 18100, "comp_perp_kpa": 1300,
                   "shear_kpa": 4600, "tension_perp_kpa": 1200, "side_hardness_n": 1300},
        "12": {"sg": 0.35, "mor_kpa": 63000, "moe_mpa": 10000, "wml_kj_m3": 35,
               "impact_mm": 510, "comp_parallel_kpa": 36400, "comp_perp_kpa": 2800,
               "shear_kpa": 6500, "tension_perp_kpa": 1200, "side_hardness_n": 1700},
    },
    "fir, california red": {
        "green": {"sg": 0.36, "mor_kpa": 40000, "moe_mpa": 8100, "wml_kj_m3": 44,
                   "impact_mm": 530, "comp_parallel_kpa": 19000, "comp_perp_kpa": 2300,
                   "shear_kpa": 5300, "tension_perp_kpa": 2600, "side_hardness_n": 1600},
        "12": {"sg": 0.38, "mor_kpa": 72400, "moe_mpa": 10300, "wml_kj_m3": 61,
               "impact_mm": 610, "comp_parallel_kpa": 37600, "comp_perp_kpa": 4200,
               "shear_kpa": 7200, "tension_perp_kpa": 2700, "side_hardness_n": 2200},
    },
    "fir, grand": {
        "green": {"sg": 0.35, "mor_kpa": 40000, "moe_mpa": 8600, "wml_kj_m3": 39,
                   "impact_mm": 560, "comp_parallel_kpa": 20300, "comp_perp_kpa": 1900,
                   "shear_kpa": 5100, "tension_perp_kpa": 1700, "side_hardness_n": 1600},
        "12": {"sg": 0.37, "mor_kpa": 61400, "moe_mpa": 10800, "wml_kj_m3": 52,
               "impact_mm": 710, "comp_parallel_kpa": 36500, "comp_perp_kpa": 3400,
               "shear_kpa": 6200, "tension_perp_kpa": 1700, "side_hardness_n": 2200},
    },
    "fir, noble": {
        "green": {"sg": 0.37, "mor_kpa": 43000, "moe_mpa": 9500, "wml_kj_m3": 41,
                   "impact_mm": 480, "comp_parallel_kpa": 20800, "comp_perp_kpa": 1900,
                   "shear_kpa": 5500, "tension_perp_kpa": 1600, "side_hardness_n": 1300},
        "12": {"sg": 0.39, "mor_kpa": 74000, "moe_mpa": 11900, "wml_kj_m3": 61,
               "impact_mm": 580, "comp_parallel_kpa": 42100, "comp_perp_kpa": 3600,
               "shear_kpa": 7200, "tension_perp_kpa": 1500, "side_hardness_n": 1800},
    },
    "fir, pacific silver": {
        "green": {"sg": 0.40, "mor_kpa": 44000, "moe_mpa": 9800, "wml_kj_m3": 41,
                   "impact_mm": 530, "comp_parallel_kpa": 21600, "comp_perp_kpa": 1500,
                   "shear_kpa": 5200, "tension_perp_kpa": 1700, "side_hardness_n": 1400},
        "12": {"sg": 0.43, "mor_kpa": 75800, "moe_mpa": 12100, "wml_kj_m3": 64,
               "impact_mm": 610, "comp_parallel_kpa": 44200, "comp_perp_kpa": 3100,
               "shear_kpa": 8400, "tension_perp_kpa": None, "side_hardness_n": 1900},
    },
    "fir, subalpine": {
        "green": {"sg": 0.31, "mor_kpa": 34000, "moe_mpa": 7200, "wml_kj_m3": None,
                   "impact_mm": None, "comp_parallel_kpa": 15900, "comp_perp_kpa": 1300,
                   "shear_kpa": 4800, "tension_perp_kpa": None, "side_hardness_n": 1200},
        "12": {"sg": 0.32, "mor_kpa": 59000, "moe_mpa": 8900, "wml_kj_m3": None,
               "impact_mm": None, "comp_parallel_kpa": 33500, "comp_perp_kpa": 2700,
               "shear_kpa": 7400, "tension_perp_kpa": None, "side_hardness_n": 1600},
    },
    "fir, white": {
        "green": {"sg": 0.37, "mor_kpa": 41000, "moe_mpa": 8000, "wml_kj_m3": 39,
                   "impact_mm": 560, "comp_parallel_kpa": 20000, "comp_perp_kpa": 1900,
                   "shear_kpa": 5200, "tension_perp_kpa": 2100, "side_hardness_n": 1500},
        "12": {"sg": 0.39, "mor_kpa": 68000, "moe_mpa": 10300, "wml_kj_m3": 50,
               "impact_mm": 510, "comp_parallel_kpa": 40000, "comp_perp_kpa": 3700,
               "shear_kpa": 7600, "tension_perp_kpa": 2100, "side_hardness_n": 2100},
    },
    # ---- Softwoods: Hemlock (Hem-Fir group) ----
    "hemlock, eastern": {
        "green": {"sg": 0.38, "mor_kpa": 44000, "moe_mpa": 7400, "wml_kj_m3": 46,
                   "impact_mm": 530, "comp_parallel_kpa": 21200, "comp_perp_kpa": 2500,
                   "shear_kpa": 5900, "tension_perp_kpa": 1600, "side_hardness_n": 1800},
        "12": {"sg": 0.40, "mor_kpa": 61000, "moe_mpa": 8300, "wml_kj_m3": 47,
               "impact_mm": 530, "comp_parallel_kpa": 37300, "comp_perp_kpa": 4500,
               "shear_kpa": 7300, "tension_perp_kpa": None, "side_hardness_n": 2200},
    },
    "hemlock, mountain": {
        "green": {"sg": 0.42, "mor_kpa": 43000, "moe_mpa": 7200, "wml_kj_m3": 76,
                   "impact_mm": 810, "comp_parallel_kpa": 19900, "comp_perp_kpa": 2600,
                   "shear_kpa": 6400, "tension_perp_kpa": 2300, "side_hardness_n": 2100},
        "12": {"sg": 0.45, "mor_kpa": 79000, "moe_mpa": 9200, "wml_kj_m3": 72,
               "impact_mm": 810, "comp_parallel_kpa": 44400, "comp_perp_kpa": 5900,
               "shear_kpa": 10600, "tension_perp_kpa": None, "side_hardness_n": 3000},
    },
    "hemlock, western": {
        "green": {"sg": 0.42, "mor_kpa": 46000, "moe_mpa": 9000, "wml_kj_m3": 48,
                   "impact_mm": 560, "comp_parallel_kpa": 23200, "comp_perp_kpa": 1900,
                   "shear_kpa": 5900, "tension_perp_kpa": 2000, "side_hardness_n": 1800},
        "12": {"sg": 0.45, "mor_kpa": 78000, "moe_mpa": 11300, "wml_kj_m3": 57,
               "impact_mm": 580, "comp_parallel_kpa": 49000, "comp_perp_kpa": 3800,
               "shear_kpa": 8600, "tension_perp_kpa": 2300, "side_hardness_n": 2400},
    },
    # ---- Softwoods: Pine (Southern Pine + SPF group constituents) ----
    "pine, jack": {
        "green": {"sg": 0.40, "mor_kpa": 41000, "moe_mpa": 7400, "wml_kj_m3": 50,
                   "impact_mm": 660, "comp_parallel_kpa": 20300, "comp_perp_kpa": 2100,
                   "shear_kpa": 5200, "tension_perp_kpa": 2500, "side_hardness_n": 1800},
        "12": {"sg": 0.43, "mor_kpa": 68000, "moe_mpa": 9300, "wml_kj_m3": 57,
               "impact_mm": 690, "comp_parallel_kpa": 39000, "comp_perp_kpa": 4000,
               "shear_kpa": 8100, "tension_perp_kpa": 2900, "side_hardness_n": 2500},
    },
    "pine, loblolly": {
        "green": {"sg": 0.47, "mor_kpa": 50000, "moe_mpa": 9700, "wml_kj_m3": 57,
                   "impact_mm": 760, "comp_parallel_kpa": 24200, "comp_perp_kpa": 2700,
                   "shear_kpa": 5900, "tension_perp_kpa": 1800, "side_hardness_n": 2000},
        "12": {"sg": 0.51, "mor_kpa": 88000, "moe_mpa": 12300, "wml_kj_m3": 72,
               "impact_mm": 760, "comp_parallel_kpa": 49200, "comp_perp_kpa": 5400,
               "shear_kpa": 9600, "tension_perp_kpa": 3200, "side_hardness_n": 3100},
    },
    "pine, lodgepole": {
        "green": {"sg": 0.38, "mor_kpa": 38000, "moe_mpa": 7400, "wml_kj_m3": 39,
                   "impact_mm": 510, "comp_parallel_kpa": 18000, "comp_perp_kpa": 1700,
                   "shear_kpa": 4700, "tension_perp_kpa": 1500, "side_hardness_n": 1500},
        "12": {"sg": 0.41, "mor_kpa": 65000, "moe_mpa": 9200, "wml_kj_m3": 47,
               "impact_mm": 510, "comp_parallel_kpa": 37000, "comp_perp_kpa": 4200,
               "shear_kpa": 6100, "tension_perp_kpa": 2000, "side_hardness_n": 2100},
    },
    "pine, longleaf": {
        "green": {"sg": 0.54, "mor_kpa": 59000, "moe_mpa": 11000, "wml_kj_m3": 61,
                   "impact_mm": 890, "comp_parallel_kpa": 29800, "comp_perp_kpa": 3300,
                   "shear_kpa": 7200, "tension_perp_kpa": 2300, "side_hardness_n": 2600},
        "12": {"sg": 0.59, "mor_kpa": 100000, "moe_mpa": 13700, "wml_kj_m3": 81,
               "impact_mm": 860, "comp_parallel_kpa": 58400, "comp_perp_kpa": 6600,
               "shear_kpa": 10400, "tension_perp_kpa": 3200, "side_hardness_n": 3900},
    },
    "pine, shortleaf": {
        "green": {"sg": 0.47, "mor_kpa": 51000, "moe_mpa": 9600, "wml_kj_m3": 57,
                   "impact_mm": 760, "comp_parallel_kpa": 24300, "comp_perp_kpa": 2400,
                   "shear_kpa": 6300, "tension_perp_kpa": 2200, "side_hardness_n": 2000},
        "12": {"sg": 0.51, "mor_kpa": 90000, "moe_mpa": 12100, "wml_kj_m3": 76,
               "impact_mm": 840, "comp_parallel_kpa": 50100, "comp_perp_kpa": 5700,
               "shear_kpa": 9600, "tension_perp_kpa": 3200, "side_hardness_n": 3100},
    },
    "pine, slash": {
        "green": {"sg": 0.54, "mor_kpa": 60000, "moe_mpa": 10500, "wml_kj_m3": 66,
                   "impact_mm": None, "comp_parallel_kpa": 26300, "comp_perp_kpa": 3700,
                   "shear_kpa": 6600, "tension_perp_kpa": None, "side_hardness_n": None},
        "12": {"sg": 0.59, "mor_kpa": 112000, "moe_mpa": 13700, "wml_kj_m3": 91,
               "impact_mm": None, "comp_parallel_kpa": 56100, "comp_perp_kpa": 7000,
               "shear_kpa": 11600, "tension_perp_kpa": None, "side_hardness_n": None},
    },
    # ---- Softwoods: Spruce (SPF group constituent) ----
    "spruce, engelmann": {
        "green": {"sg": 0.33, "mor_kpa": 32000, "moe_mpa": 7100, "wml_kj_m3": 35,
                   "impact_mm": 410, "comp_parallel_kpa": 15000, "comp_perp_kpa": 1400,
                   "shear_kpa": 4400, "tension_perp_kpa": 1700, "side_hardness_n": 1150},
        "12": {"sg": 0.35, "mor_kpa": 64000, "moe_mpa": 8900, "wml_kj_m3": 44,
               "impact_mm": 460, "comp_parallel_kpa": 30900, "comp_perp_kpa": 2800,
               "shear_kpa": 8300, "tension_perp_kpa": 2400, "side_hardness_n": 1750},
    },
}


def table_5_3_mechanical_properties(species, moisture_condition="12"):
    """Table 5-3a: clear-wood strength/stiffness properties (metric units),
    for the module's documented species subset (printed pp. 5-5 to 5-8).

    Parameters
    ----------
    species : str
        A key of ``TABLE_5_3_PROPERTIES`` (case-insensitive), e.g.
        'douglas-fir, coast', 'pine, loblolly', 'oak, white'.
    moisture_condition : str, optional
        'green' or '12' (12% moisture content, default).

    Returns
    -------
    dict
        The property row (sg, mor_kpa, moe_mpa, wml_kj_m3, impact_mm,
        comp_parallel_kpa, comp_perp_kpa, shear_kpa, tension_perp_kpa,
        side_hardness_n; a value is None where the printed table has no
        entry), plus {'species', 'moisture_condition', 'table': '5-3a', ...}.
    """
    key = species.lower().strip()
    if key not in TABLE_5_3_PROPERTIES:
        raise ValueError(
            f"species must be one of {sorted(TABLE_5_3_PROPERTIES)}, got {species!r}"
        )
    if moisture_condition not in ("green", "12"):
        raise ValueError(f"moisture_condition must be 'green' or '12', got {moisture_condition!r}")
    row = dict(TABLE_5_3_PROPERTIES[key][moisture_condition])
    row.update({
        "species": key, "moisture_condition": moisture_condition,
        "table": "5-3a", "printed_page": "5-5 to 5-8", "pdf_page": "119-123",
    })
    return row


# ============================================================================
# Eq 5-3, Table 5-13 -- Moisture content adjustment of clear-wood properties
# (printed p. 5-34, pdf_page 149)
# ============================================================================

# Mp (%), the intersection moisture content, for species where the
# handbook tabulates a specific value (Table 5-13). For any other species,
# the text directs using Mp = 25 (the documented default).
TABLE_5_13_MP = {
    "ash, white": 24,
    "birch, yellow": 27,
    "chestnut, american": 24,
    "douglas-fir": 24,
    "hemlock, western": 28,
    "larch, western": 28,
    "pine, loblolly": 21,
    "pine, longleaf": 21,
    "pine, red": 24,
    "redwood": 21,
    "spruce, red": 27,
    "spruce, sitka": 27,
    "tamarack": 24,
}

DEFAULT_MP = 25.0  # printed default when species not in Table 5-13


def table_5_13_intersection_mc(species):
    """Table 5-13: intersection moisture content Mp (%) for a species, the
    point at which mechanical properties begin to change as wood dries
    from the green condition (printed p. 5-34). Falls back to the
    documented default Mp = 25 for species not in the printed table.

    Parameters
    ----------
    species : str
        A key of ``TABLE_5_13_MP`` (case-insensitive), or any other
        species name (returns the default).

    Returns
    -------
    dict
        {'species', 'mp_pct', 'is_tabulated' (bool), 'table': '5-13', ...}
    """
    key = species.lower().strip()
    is_tabulated = key in TABLE_5_13_MP
    mp = TABLE_5_13_MP.get(key, DEFAULT_MP)
    return {
        "species": key, "mp_pct": mp, "is_tabulated": is_tabulated,
        "table": "5-13", "printed_page": "5-34", "pdf_page": 149,
    }


def adjust_property_for_moisture_content(p12, pg, moisture_content_pct, mp_pct):
    """Eq 5-3: adjust a clear-wood mechanical property from 12% MC to any
    other moisture content M below the fiber saturation point, at about
    21 degC (70 degF) (printed p. 5-34).

        P = P12 * (P12/Pg) ^ ((12-M)/(Mp-12))

    NOT recommended for work to maximum load, impact bending, or tension
    perpendicular to grain (erratic response to moisture content change,
    per the handbook text).

    Worked example (printed): white ash MOR at 8% MC, P12=103,000 kPa,
    Pg=66,000 kPa, Mp=24 -> P8 = 103000*(103000/66000)**(4/12) = 119,500 kPa.

    Parameters
    ----------
    p12 : float
        The property value at 12% moisture content (Table 5-3).
    pg : float
        The property value at green moisture content (Table 5-3).
    moisture_content_pct : float
        M, the target moisture content (%), below Mp.
    mp_pct : float
        Mp, the species' intersection moisture content (Table 5-13, or
        ``table_5_13_intersection_mc``).

    Returns
    -------
    dict
        {'p12', 'pg', 'moisture_content_pct', 'mp_pct', 'property_value',
         'equation': '5-3', ...}
    """
    exponent = (12.0 - moisture_content_pct) / (mp_pct - 12.0)
    p = p12 * (p12 / pg) ** exponent
    return {
        "p12": p12, "pg": pg, "moisture_content_pct": moisture_content_pct,
        "mp_pct": mp_pct, "property_value": p, "equation": "5-3",
        "printed_page": "5-34", "pdf_page": 149,
    }


# ============================================================================
# Table 5-15 -- Approximate middle-trend effects of temperature on
# mechanical properties of clear wood (printed p. 5-36, pdf_page 151)
# ============================================================================

# Keyed by (property, moisture_condition_label) -> {'minus50_pct', 'plus50_pct'}
# (relative change (%) from 20 degC, at -50 degC and +50 degC). None = no
# printed entry ('--' in the table) for that combination.
TABLE_5_15_TEMPERATURE_EFFECT = {
    ("moe_parallel", "0"): {"minus50_pct": 11, "plus50_pct": -6},
    ("moe_parallel", "12"): {"minus50_pct": 17, "plus50_pct": -7},
    ("moe_parallel", ">fsp"): {"minus50_pct": 50, "plus50_pct": None},
    ("moe_perpendicular", "6"): {"minus50_pct": None, "plus50_pct": -20},
    ("moe_perpendicular", "12"): {"minus50_pct": None, "plus50_pct": -35},
    ("moe_perpendicular", ">=20"): {"minus50_pct": None, "plus50_pct": -38},
    ("shear_modulus", ">fsp"): {"minus50_pct": None, "plus50_pct": -25},
    ("bending_strength", "<=4"): {"minus50_pct": 18, "plus50_pct": -10},
    ("bending_strength", "11-15"): {"minus50_pct": 35, "plus50_pct": -20},
    ("bending_strength", "18-20"): {"minus50_pct": 60, "plus50_pct": -25},
    ("bending_strength", ">fsp"): {"minus50_pct": 110, "plus50_pct": -25},
    ("tensile_strength_parallel", "0-12"): {"minus50_pct": None, "plus50_pct": -4},
    ("compressive_strength_parallel", "0"): {"minus50_pct": 20, "plus50_pct": -10},
    ("compressive_strength_parallel", "12-45"): {"minus50_pct": 50, "plus50_pct": -25},
    ("shear_strength_parallel", ">fsp"): {"minus50_pct": None, "plus50_pct": -25},
    ("tensile_strength_perpendicular", "4-6"): {"minus50_pct": None, "plus50_pct": -10},
    ("tensile_strength_perpendicular", "11-16"): {"minus50_pct": None, "plus50_pct": -20},
    ("tensile_strength_perpendicular", ">=18"): {"minus50_pct": None, "plus50_pct": -30},
    ("compressive_strength_perpendicular_proportional_limit", "0-6"): {"minus50_pct": None, "plus50_pct": -20},
    ("compressive_strength_perpendicular_proportional_limit", ">=10"): {"minus50_pct": None, "plus50_pct": -35},
}


def table_5_15_temperature_effect(property_name, moisture_condition):
    """Table 5-15: approximate middle-trend relative change (%) in a clear
    wood mechanical property at -50 degC (-58 degF) and +50 degC (+122
    degF), relative to the value at 20 degC (68 degF), for a given
    moisture condition band (printed p. 5-36).

    Parameters
    ----------
    property_name : str
        A property key of ``TABLE_5_15_TEMPERATURE_EFFECT``, e.g.
        'moe_parallel', 'bending_strength', 'compressive_strength_parallel'.
    moisture_condition : str
        The moisture-condition band as printed, e.g. '0', '12', '>fsp',
        '11-15' (see ``TABLE_5_15_TEMPERATURE_EFFECT`` keys).

    Returns
    -------
    dict
        {'property', 'moisture_condition', 'change_at_minus50c_pct',
         'change_at_plus50c_pct', 'table': '5-15', ...}
    """
    key = (property_name.lower().strip(), moisture_condition.lower().strip())
    if key not in TABLE_5_15_TEMPERATURE_EFFECT:
        raise ValueError(
            f"(property_name, moisture_condition) must be one of "
            f"{sorted(TABLE_5_15_TEMPERATURE_EFFECT)}, got {key!r}"
        )
    row = TABLE_5_15_TEMPERATURE_EFFECT[key]
    return {
        "property": key[0], "moisture_condition": key[1],
        "change_at_minus50c_pct": row["minus50_pct"],
        "change_at_plus50c_pct": row["plus50_pct"], "table": "5-15",
        "printed_page": "5-36", "pdf_page": 151,
    }


# ============================================================================
# Table 5-16 -- Percentage change in bending properties of lumber with
# change in temperature (printed p. 5-37, pdf_page 152)
# ============================================================================

# ((P - P70)/P70)*100 = A + B*T + C*T^2, with T in DEGREES FAHRENHEIT (as
# printed) and P70 the property at 21 degC (70 degF). Keyed by
# (property, lumber_grade, moisture_condition).
TABLE_5_16_COEFFICIENTS = {
    ("moe", "all", "green_low"): {"a": 22.0350, "b": -0.4578, "c": 0.0, "t_min": 0, "t_max": 32},
    ("moe", "all", "green_high"): {"a": 13.1215, "b": -0.1793, "c": 0.0, "t_min": 32, "t_max": 150},
    ("moe", "all", "12"): {"a": 7.8553, "b": -0.1108, "c": 0.0, "t_min": -15, "t_max": 150},
    ("mor", "select structural", "green_low"): {"a": 34.13, "b": -0.937, "c": 0.0043, "t_min": -20, "t_max": 46},
    ("mor", "select structural", "green_high"): {"a": 0.0, "b": 0.0, "c": 0.0, "t_min": 46, "t_max": 100},
    ("mor", "select structural", "12"): {"a": 0.0, "b": 0.0, "c": 0.0, "t_min": -20, "t_max": 100},
    ("mor", "no. 2 or less", "green_low"): {"a": 56.89, "b": -1.562, "c": 0.0072, "t_min": -20, "t_max": 46},
    ("mor", "no. 2 or less", "green_high"): {"a": 0.0, "b": 0.0, "c": 0.0, "t_min": 46, "t_max": 100},
    ("mor", "no. 2 or less", "dry"): {"a": 0.0, "b": 0.0, "c": 0.0, "t_min": -20, "t_max": 100},
}


def table_5_16_temperature_adjustment(property_name, lumber_grade, moisture_condition, temp_f):
    """Table 5-16: percentage change in lumber bending properties (MOE,
    MOR) with change in temperature, via the printed quadratic equation
    (printed p. 5-37).

        ((P - P70)/P70)*100 = A + B*T + C*T^2   (T in degrees F)

    Parameters
    ----------
    property_name : str
        'moe' or 'mor'.
    lumber_grade : str
        'all' (MOE) or 'select structural'/'no. 2 or less' (MOR).
    moisture_condition : str
        'green_low' (green, lower T range), 'green_high' (green, upper T
        range, coefficients are 0 -- no significant change), '12', or 'dry'
        (see ``TABLE_5_16_COEFFICIENTS`` keys for the valid combination).
    temp_f : float
        T, temperature (degrees F). A ValueError is raised if outside the
        printed [t_min, t_max] range for the selected row.

    Returns
    -------
    dict
        {'property', 'lumber_grade', 'moisture_condition', 'temp_f',
         'percent_change', 'table': '5-16', ...}
    """
    key = (property_name.lower().strip(), lumber_grade.lower().strip(),
           moisture_condition.lower().strip())
    if key not in TABLE_5_16_COEFFICIENTS:
        raise ValueError(
            f"(property_name, lumber_grade, moisture_condition) must be one of "
            f"{sorted(TABLE_5_16_COEFFICIENTS)}, got {key!r}"
        )
    row = TABLE_5_16_COEFFICIENTS[key]
    if not (row["t_min"] <= temp_f <= row["t_max"]):
        raise ValueError(
            f"temp_f={temp_f} outside the printed range "
            f"[{row['t_min']}, {row['t_max']}] degF for {key!r}"
        )
    pct_change = row["a"] + row["b"] * temp_f + row["c"] * temp_f**2
    return {
        "property": key[0], "lumber_grade": key[1], "moisture_condition": key[2],
        "temp_f": temp_f, "percent_change": pct_change, "table": "5-16",
        "printed_page": "5-37", "pdf_page": 152,
    }
