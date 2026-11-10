"""GEC-13 table lookup functions.

Digitized tables from GEC-13, Ground Modification Methods Reference
Manual: FHWA-NHI-16-027 (Volume I, chapters 1-5) and FHWA-NHI-16-028
(Volume II, chapters 6-10; the Table 8-1 and 8-6 lookups), and the deep
dynamic compaction depth, Eq. 4-1 (``equation_4_1_ddc_depth``). Follows the DM7
pattern: private data with ``_TABLE_*`` prefix, public lookup functions,
case-insensitive keys.
"""

from geotech_references._interpolation import _linterp


def _no_match(table, page, given, choices):
    """ValueError for a filter that matched no printed row."""
    asked = ", ".join(f"{k}='{v}'" for k, v in given.items() if v)
    return ValueError(
        f"No row of GEC-13 {table} ({page}) matches {asked}. "
        + " ".join(f"{name}: {', '.join(vals)}." for name, vals in choices))

# ============================================================================
# Table 1-2: General Applicability of Technologies
# ============================================================================

_TABLE_1_2 = [
    {
        "category": "vertical_drains",
        "technology": "PVDs with and without fill preloading",
        "applicability": "Compressible clays, saturated low strength clays",
    },
    {
        "category": "lightweight_fills",
        "technology": "Compressive Strength Fills: Geofoam; Foamed Concrete",
        "applicability": "Broad applicability; no geologic or geometric limitations",
    },
    {
        "category": "lightweight_fills",
        "technology": "Granular Fills: Wood Fiber; Blast Furnace Slag; Fly Ash; "
                       "Boiler Slag; Expanded Shale, Clay, and Slate; Tire Shreds",
        "applicability": "Broad applicability; no geologic or geometric limitations",
    },
    {
        "category": "deep_compaction",
        "technology": "Deep Dynamic Compaction",
        "applicability": "Loose pervious and semi-pervious soils with fines contents "
                         "less than 15%, materials containing large voids, spoils and "
                         "waste areas",
    },
    {
        "category": "deep_compaction",
        "technology": "Vibro-Compaction",
        "applicability": "Cohesionless soils, clean sands with less than 15% silts "
                         "and/or less than 2% clay",
    },
    {
        "category": "aggregate_columns",
        "technology": "Stone Columns",
        "applicability": "Clays, silts, loose silty sands, and uncompacted fill",
    },
    {
        "category": "aggregate_columns",
        "technology": "Rammed Aggregate Piers",
        "applicability": "Clays, silts, loose silty sands, uncompacted fill",
    },
    {
        "category": "column_supported_embankments",
        "technology": "Column Supported Embankments",
        "applicability": "Soft compressible clay, peats, and organic soils where "
                         "settlement and global stability are concerns",
    },
    {
        "category": "column_supported_embankments",
        "technology": "Reinforced Soil Load Transfer Platform",
        "applicability": "Soft compressible clay, peats, and organic soils where "
                         "settlement and global stability are concerns",
    },
    {
        "category": "column_supported_embankments",
        "technology": "Columns: Non-compressible",
        "applicability": "All soil types, in particular weak soils that cannot "
                         "support surface loads",
    },
    {
        "category": "column_supported_embankments",
        "technology": "Columns: Compressible",
        "applicability": "All soil types except very soft soils with low undrained "
                         "shear strength",
    },
    {
        "category": "soil_mixing",
        "technology": "Deep Mixing",
        "applicability": "Suitable in large range of soils, ones that can be "
                         "stabilized with cement, lime, slag, or other binders",
    },
    {
        "category": "soil_mixing",
        "technology": "Mass Mixing",
        "applicability": "Peat, soft clay, dredged soil, soft silt, sludges, "
                         "contaminated soils",
    },
    {
        "category": "grouting",
        "technology": "Chemical (Permeation) Grouting",
        "applicability": "Wide range of soil types including weakly cemented "
                         "rock-fill materials",
    },
    {
        "category": "grouting",
        "technology": "Compaction Grouting",
        "applicability": "Cohesionless granular soils, collapsible soils, and "
                         "unsaturated fine grained soils; may be used to fill "
                         "voids in sinkholes or abandoned mine shafts; can "
                         "arrest settlement under a structure and lift "
                         "foundations that have settled",
    },
    {
        "category": "grouting",
        "technology": "Jet Grouting",
        "applicability": "Wide range of soil types and groundwater conditions",
    },
    {
        "category": "grouting",
        "technology": "Rock Fissure Grouting",
        "applicability": "Structural stability and groundwater control",
    },
    {
        "category": "grouting",
        "technology": "Bulk Void Filling and Slabjacking",
        "applicability": "All soil types were voids develop under pavements",
    },
    {
        "category": "pavement_stabilization",
        "technology": "Mechanical Stabilization",
        "applicability": "Weak subgrades, loose sands, and to stabilize thin "
                         "aggregate layers on subgrades with CBR<8",
    },
    {
        "category": "pavement_stabilization",
        "technology": "Chemical Stabilization",
        "applicability": "Portland cement and lime: high plasticity clays; "
                         "Fly ash: soils with little or no plastic fines; "
                         "Asphalt: silty, sandy and granular soils; "
                         "Cement Kiln Dust: expansive soils",
    },
    {
        "category": "pavement_stabilization",
        "technology": "Moisture Control",
        "applicability": "All soil types",
    },
    {
        "category": "reinforced_soil",
        "technology": "Reinforced Embankments Over Soft Soils",
        "applicability": "Soft soil foundations, with no limitation on depth of "
                         "soft soils",
    },
    {
        "category": "reinforced_soil",
        "technology": "Reinforced Soil Walls",
        "applicability": "Well suited in fill embankments, steep-sided terrain, "
                         "ground subject to soil instability and where foundations "
                         "soils are poor",
    },
    {
        "category": "reinforced_soil",
        "technology": "Reinforced Soil Slopes",
        "applicability": "Can be constructed over any firm foundation",
    },
    {
        "category": "reinforced_soil",
        "technology": "Soil Nail Walls",
        "applicability": "Dense to very dense granular soils with apparent "
                         "cohesion, weathered rock, stiff to hard fine-grained "
                         "soils, engineered fill, residual soils, glacial till",
    },
]


def table_1_2_applicability(category: str = "", technology: str = "") -> list:
    """Ground conditions each ground modification technology applies to, as printed in GEC-13 Table 1-2 "General Applicability of Technologies" (FHWA-NHI-16-027 Vol I, pp. 1-10 to 1-11).

    Parameters
    ----------
    category : str
        Filter by category (partial match, case-insensitive).
        E.g., 'deep_compaction', 'grouting', 'aggregate'.
    technology : str
        Filter by technology name (partial match, case-insensitive).
        E.g., 'stone columns', 'PVD', 'jet grouting'.

    Returns
    -------
    list of dict
        Matching entries with category, technology, and applicability.

    Raises
    ------
    ValueError
        If a filter is given and no row of the table matches it.
    """
    cat_lower = category.lower().strip()
    tech_lower = technology.lower().strip()
    results = []
    for entry in _TABLE_1_2:
        if cat_lower and cat_lower not in entry["category"].lower():
            continue
        if tech_lower and tech_lower not in entry["technology"].lower():
            continue
        results.append(dict(entry))
    if not results:
        cats = []
        for entry in _TABLE_1_2:
            if entry["category"] not in cats:
                cats.append(entry["category"])
        raise _no_match(
            "Table 1-2", "pp. 1-10 to 1-11",
            {"category": category, "technology": technology},
            [("Categories", cats),
             ("Technologies", [e["technology"] for e in _TABLE_1_2])])
    return results


# ============================================================================
# Table 1-3: Technologies Classified by Function
# ============================================================================

# FHWA-NHI-16-027 (GEC-13) Vol I, pp. 1-15 and 1-16 (PDF pages 29-30), read
# off the rendered pages: ten functions, each with its bulleted technologies
# and its comment, in the print's words (the fourth row prints "Columns
# Supported Embankments").
_TABLE_1_3 = {
    "increase_shear_strength": {
        "description": "Increase shear strength and bearing resistance",
        "technologies": [
            "Vibro-Compaction", "Dynamic Compaction", "Compaction Grouting",
            "Mixing Methods", "PVDs", "Stone Columns",
            "Rammed Aggregate Piers", "Chemical Stabilization",
            "Mechanical Stabilization",
        ],
        "comment": "Some technologies will work in all soil types; others "
                   "are limited to cohesive or cohesionless soils.",
    },
    "increase_density": {
        "description": "Increase density",
        "technologies": [
            "Vibro-Compaction", "Dynamic Compaction", "Blasting Compaction",
            "Compaction Grouting", "Mixing Methods", "PVDs",
        ],
        "comment": "Some technologies will work on all soil types; others "
                   "are limited to cohesive or to cohesionless soils.",
    },
    "decrease_permeability": {
        "description": "Decrease permeability",
        "technologies": [
            "Bulk-infill Grouting", "Chemical Grouting",
            "Jet Grouting", "Deep Mixing Methods",
        ],
        "comment": "Type of grouting dependent upon soils, depths, geology, "
                   "and design requirements.",
    },
    "control_deformations": {
        "description": "Control deformations (settlement, heave, distortions)",
        "technologies": [
            "Columns Supported Embankments",
            "Reinforced Load Transfer Platforms",
            "Non-compressible Columns", "Mixing Methods",
            "Vibro-Compaction", "Dynamic Compaction",
            "Stone Columns", "Rammed Aggregate Piers",
            "Chemical Stabilization", "Mechanical Stabilization",
            "Encapsulation",
        ],
        "comment": "Technologies generally used to bypass or isolate soft "
                   "ground or to modify and improve the soft ground.",
    },
    "increase_drainage": {
        "description": "Increase drainage",
        "technologies": [
            "PVDs", "Aggregate Columns", "Geotextile Encased columns",
            "Electro-osmosis", "Geosynthetics in Pavement Drainage",
        ],
        "comment": "Generally increase drainage by inserting a drainage "
                   "path within the soil to be drained.",
    },
    "accelerate_consolidation": {
        "description": "Accelerate consolidation",
        "technologies": [
            "PVDs", "Aggregate Columns", "Geotextile Encased Columns",
        ],
        "comment": "Acceleration due to decreased length of flow path to "
                   "dissipate excess pore water pressure.",
    },
    "decrease_imposed_loads": {
        "description": "Decrease imposed loads",
        "technologies": [
            "Granular Fills (Wood Fiber; Blast Furnace Slag; Fly Ash; "
            "Boiler Slag; Expanded Shale, Clay & Slate; Tire Shreds)",
            "Compressive Strength Fills: (Geofoam, Foamed Concrete)",
        ],
        "comment": "Densities vary from 1 to 90 pcf. Granular fill usage "
                   "subject to local availability.",
    },
    "provide_lateral_stability": {
        "description": "Provide lateral stability",
        "technologies": [
            "Mechanically Stabilized Earth (MSE) Walls",
            "Reinforced Soil Slopes", "Soil Nailing",
        ],
        "comment": "Techniques based on internal reinforcement of soils.",
    },
    "increase_liquefaction_resistance": {
        "description": "Increase resistance to liquefaction",
        "technologies": [
            "Aggregate Columns", "Deep Dynamic Compaction", "Deep Mixing",
            "Jet Grouting", "Vibro-Compaction",
        ],
        "comment": "Techniques generally to modify and improve soil "
                   "susceptible to liquefaction. Aggregate columns also "
                   "provide drainage path for excess pore water pressure.",
    },
    "transfer_embankment_loads": {
        "description": "Transfer embankment loads to more competent layers",
        "technologies": [
            "Column Supported Embankments",
            "Reinforced Soil Load Transfer Platforms",
            "Non-compressible Columns", "Compressible Columns",
        ],
        "comment": "A column supported embankment may be constructed on a "
                   "load transfer platform that is supported on columns.",
    },
}

_TABLE_1_3_REFERENCE = ("FHWA-NHI-16-027 (GEC-13) Vol I, Table 1-3 "
                        "Technologies Classified by Function, pp. 1-15 to 1-16")


def table_1_3_by_function(function: str = "") -> list:
    """Ground modification technologies listed under each function (increase shear strength, increase density, decrease permeability, control deformations, increase drainage, accelerate consolidation, decrease imposed loads, provide lateral stability, increase resistance to liquefaction, transfer embankment loads), as printed in GEC-13 Table 1-3 (FHWA-NHI-16-027 Vol I, pp. 1-15 to 1-16).

    Parameters
    ----------
    function : str
        Filter by function name (partial match, case-insensitive).
        E.g., 'shear', 'density', 'drainage', 'liquefaction', 'loads'.
        Empty string returns all ten functions.

    Returns
    -------
    list of dict
        Each dict has function, description (the function as printed),
        technologies (the printed bullets), comment (as printed) and
        reference.

    Raises
    ------
    ValueError
        If a filter is given and no function of the table matches it.
    """
    func_lower = function.lower().strip()
    results = []
    for key, data in _TABLE_1_3.items():
        if func_lower and (func_lower not in key.lower() and
                           func_lower not in data["description"].lower()):
            continue
        results.append({
            "function": key,
            "description": data["description"],
            "technologies": list(data["technologies"]),
            "comment": data["comment"],
            "reference": _TABLE_1_3_REFERENCE,
        })
    if not results:
        raise _no_match(
            "Table 1-3", "pp. 1-15 to 1-16", {"function": function},
            [("Functions", [d["description"] for d in _TABLE_1_3.values()])])
    return results


# ============================================================================
# Table 1-6: Comparative Unit Costs by Ground Modification Technology
# (November 2016 dollars)
# ============================================================================

_TABLE_1_6 = [
    {
        "category": "vertical_drains",
        "technology": "PVDs with and without fill preloading",
        "unit_cost": "$0.50-$4/lft",
        "cost_low": 0.50,
        "cost_high": 4.00,
        "unit": "$/lft",
    },
    {
        "category": "lightweight_fills",
        "technology": "Compressive Strength Fills (Geofoam, Foamed Concrete)",
        "unit_cost": "$75-$150/yd3",
        "cost_low": 75.0,
        "cost_high": 150.0,
        "unit": "$/yd3",
    },
    {
        "category": "lightweight_fills",
        "technology": "Granular Fills (Wood Fiber, Slag, Fly Ash, Tire Shreds)",
        "unit_cost": "$3-$15/yd3",
        "cost_low": 3.0,
        "cost_high": 15.0,
        "unit": "$/yd3",
    },
    {
        "category": "deep_compaction",
        "technology": "Deep Dynamic Compaction",
        "unit_cost": "$10-$30/yd2",
        "cost_low": 10.0,
        "cost_high": 30.0,
        "unit": "$/yd2",
    },
    {
        "category": "deep_compaction",
        "technology": "Vibro-Compaction",
        "unit_cost": "$5-$9/lft",
        "cost_low": 5.0,
        "cost_high": 9.0,
        "unit": "$/lft",
    },
    {
        "category": "aggregate_columns",
        "technology": "Stone Columns and Rammed Aggregate Piers",
        "unit_cost": "$15-$60/lft",
        "cost_low": 15.0,
        "cost_high": 60.0,
        "unit": "$/lft",
    },
    {
        "category": "column_supported_embankments",
        "technology": "Column Supported Embankments",
        "unit_cost": "$9/ft2 + cost of the column",
        "cost_low": 9.0,
        "cost_high": 9.0,
        "unit": "$/ft2 + column",
    },
    {
        "category": "column_supported_embankments",
        "technology": "Columns: Non-compressible",
        "unit_cost": "$30-$80/lft",
        "cost_low": 30.0,
        "cost_high": 80.0,
        "unit": "$/lft",
    },
    {
        "category": "column_supported_embankments",
        "technology": "Columns: Compressible",
        "unit_cost": "$20-$100/lft",
        "cost_low": 20.0,
        "cost_high": 100.0,
        "unit": "$/lft",
    },
    {
        "category": "soil_mixing",
        "technology": "Deep Mixing (dry)",
        "unit_cost": "$60-$125/lft",
        "cost_low": 60.0,
        "cost_high": 125.0,
        "unit": "$/lft",
    },
    {
        "category": "soil_mixing",
        "technology": "Mass Mixing",
        "unit_cost": "$15-$75/yd3",
        "cost_low": 15.0,
        "cost_high": 75.0,
        "unit": "$/yd3",
    },
    {
        "category": "grouting",
        "technology": "Chemical Grouting",
        "unit_cost": "$20/ft + $0.65/qt",
        "cost_low": 20.0,
        "cost_high": 20.0,
        "unit": "$/ft + $/qt",
    },
    {
        "category": "grouting",
        "technology": "Compaction Grouting",
        "unit_cost": "$75-$750/yd3",
        "cost_low": 75.0,
        "cost_high": 750.0,
        "unit": "$/yd3",
    },
    {
        "category": "grouting",
        "technology": "Bulk Void Filling",
        "unit_cost": "$50-$150/yd3",
        "cost_low": 50.0,
        "cost_high": 150.0,
        "unit": "$/yd3",
    },
    {
        "category": "grouting",
        "technology": "Slabjacking",
        "unit_cost": "$6.50-$9.30/ft2",
        "cost_low": 6.50,
        "cost_high": 9.30,
        "unit": "$/ft2",
    },
    {
        "category": "grouting",
        "technology": "Jet Grouting",
        "unit_cost": "$250-$750/yd3",
        "cost_low": 250.0,
        "cost_high": 750.0,
        "unit": "$/yd3",
    },
    {
        "category": "grouting",
        "technology": "Rock Fissure Grouting",
        "unit_cost": "$25-$80/ft2",
        "cost_low": 25.0,
        "cost_high": 80.0,
        "unit": "$/ft2",
    },
    {
        "category": "pavement_stabilization",
        "technology": "Mechanical Stabilization",
        "unit_cost": "$1-$5/yd2",
        "cost_low": 1.0,
        "cost_high": 5.0,
        "unit": "$/yd2",
    },
    {
        "category": "pavement_stabilization",
        "technology": "Chemical Stabilization",
        "unit_cost": "$2-$5/yd2",
        "cost_low": 2.0,
        "cost_high": 5.0,
        "unit": "$/yd2",
    },
    {
        "category": "pavement_stabilization",
        "technology": "Moisture Control",
        "unit_cost": "$3-$12/lft",
        "cost_low": 3.0,
        "cost_high": 12.0,
        "unit": "$/lft",
    },
    {
        "category": "reinforced_soil",
        "technology": "Reinforced Embankments",
        "unit_cost": "$2-$12/yd2",
        "cost_low": 2.0,
        "cost_high": 12.0,
        "unit": "$/yd2",
    },
    {
        "category": "reinforced_soil",
        "technology": "MSE Walls",
        "unit_cost": "$30-$65/ft2",
        "cost_low": 30.0,
        "cost_high": 65.0,
        "unit": "$/ft2",
    },
    {
        "category": "reinforced_soil",
        "technology": "Reinforced Soil Slopes",
        "unit_cost": "$3-$25/ft2",
        "cost_low": 3.0,
        "cost_high": 25.0,
        "unit": "$/ft2",
    },
    {
        "category": "reinforced_soil",
        "technology": "Soil Nailing",
        "unit_cost": "$20-$50/lft",
        "cost_low": 20.0,
        "cost_high": 50.0,
        "unit": "$/lft",
    },
]


def table_1_6_unit_cost(category: str = "", technology: str = "") -> list:
    """Comparative unit costs by ground modification technology (Table 1-6).

    Costs are in November 2016 US dollars. Does not include mobilization
    or site investigation costs.

    Parameters
    ----------
    category : str
        Filter by category (partial match, case-insensitive).
        E.g., 'grouting', 'deep_compaction', 'reinforced'.
    technology : str
        Filter by technology name (partial match, case-insensitive).
        E.g., 'PVD', 'stone columns', 'jet grouting'.

    Returns
    -------
    list of dict
        Matching entries with category, technology, unit_cost,
        cost_low, cost_high, and unit fields.

    Raises
    ------
    ValueError
        If a filter is given and no row of the table matches it.
    """
    cat_lower = category.lower().strip()
    tech_lower = technology.lower().strip()
    results = []
    for entry in _TABLE_1_6:
        if cat_lower and cat_lower not in entry["category"].lower():
            continue
        if tech_lower and tech_lower not in entry["technology"].lower():
            continue
        results.append(dict(entry))
    if not results:
        cats = []
        for entry in _TABLE_1_6:
            if entry["category"] not in cats:
                cats.append(entry["category"])
        raise _no_match(
            "Table 1-6", "p. 1-36",
            {"category": category, "technology": technology},
            [("Categories", cats),
             ("Technologies", [e["technology"] for e in _TABLE_1_6])])
    return results


# ============================================================================
# Table 2-1: Common Uses of PVDs for Transportation Applications
# ============================================================================

_TABLE_2_1 = [
    {
        "application": "Highways Roadway Embankments",
        "increase_stability": True,
        "accelerate_settlements": True,
    },
    {
        "application": "Highway Structure Approach Fills",
        "increase_stability": True,
        "accelerate_settlements": True,
    },
    {
        "application": "Airfield Runways and Taxiways",
        "increase_stability": True,
        "accelerate_settlements": True,
    },
    {
        "application": "Earth Embankment Dams",
        "increase_stability": True,
        "accelerate_settlements": True,
    },
    {
        "application": "Storage Tanks",
        "increase_stability": True,
        "accelerate_settlements": True,
    },
    {
        "application": "Pile Foundations to Reduce Negative Skin Friction",
        "increase_stability": False,
        "accelerate_settlements": True,
    },
    {
        "application": "Liquefaction Mitigation",
        "increase_stability": True,
        "accelerate_settlements": True,
    },
    {
        "application": "Land Reclamation",
        "increase_stability": True,
        "accelerate_settlements": True,
    },
]


def table_2_1_pvd_applications(application: str = "") -> list:
    """Common uses of PVDs for transportation applications (Table 2-1).

    Parameters
    ----------
    application : str
        Filter by application name (partial match, case-insensitive).
        E.g., 'highway', 'liquefaction', 'embankment'.

    Returns
    -------
    list of dict
        Matching entries with application, increase_stability, and
        accelerate_settlements fields.

    Raises
    ------
    ValueError
        If a filter is given and no row of the table matches it.
    """
    app_lower = application.lower().strip()
    results = []
    for entry in _TABLE_2_1:
        if app_lower and app_lower not in entry["application"].lower():
            continue
        results.append(dict(entry))
    if not results:
        raise _no_match(
            "Table 2-1", "p. 2-9", {"application": application},
            [("Fields of application",
              [e["application"] for e in _TABLE_2_1])])
    return results


# ============================================================================
# Table 3-1: Densities and Specific Gravity for Various Lightweight Fill
# Materials. FHWA-NHI-16-027 (GEC-13) Vol I, p. 3-1 (PDF page 151), read off
# the rendered page:
#
#   Fill Type                                Range in Density pcf   Range in Specific Gravity
#   Geofoam (RCPS)                           0.70 to 3.00           0.01 to 0.05
#   Cellular Concrete                        20 to 80               0.4 to 1.3
#   Wood Fiber                               35 to 55               0.6 to 0.9
#   Tire Shreds                              37 to 73               0.6 to 1.2
#   Expanded Shale, Clay, and Slate (ESCS)   37 to 65               0.6 to 1.0
#   Fly Ash                                  70 to 90               1.1 to 1.4
#   Boiler Slag                              60 to 90               1.0 to 1.4
#   Expanded Air-Cooled Slag                 69 to 94               1.1 to 1.5
# ============================================================================

_PCF_TO_KN_M3 = 0.157087

# key: (fill type as printed, (density pcf low, high), (specific gravity low, high))
_TABLE_3_1 = {
    "geofoam": ("Geofoam (RCPS)", (0.70, 3.00), (0.01, 0.05)),
    "cellular_concrete": ("Cellular Concrete", (20, 80), (0.4, 1.3)),
    "wood_fiber": ("Wood Fiber", (35, 55), (0.6, 0.9)),
    "tire_shreds": ("Tire Shreds", (37, 73), (0.6, 1.2)),
    "expanded_shale_clay_slate": (
        "Expanded Shale, Clay, and Slate (ESCS)", (37, 65), (0.6, 1.0)),
    "fly_ash": ("Fly Ash", (70, 90), (1.1, 1.4)),
    "boiler_slag": ("Boiler Slag", (60, 90), (1.0, 1.4)),
    "expanded_air_cooled_slag": (
        "Expanded Air-Cooled Slag", (69, 94), (1.1, 1.5)),
}

_TABLE_3_1_REFERENCE = ("FHWA-NHI-16-027 (GEC-13) Vol I, Table 3-1 Densities "
                        "and Specific Gravity for Various Lightweight Fill "
                        "Materials, p. 3-1")


def table_3_1_lightweight_fill(material: str = "") -> list:
    """Range of density (pcf as printed, and kN/m3 converted) and of specific gravity for eight lightweight fill materials, as printed in GEC-13 Table 3-1 (FHWA-NHI-16-027 Vol I, p. 3-1).

    As printed, density in pcf: Geofoam (RCPS) 0.70 to 3.00; Cellular
    Concrete 20 to 80; Wood Fiber 35 to 55; Tire Shreds 37 to 73; Expanded
    Shale, Clay, and Slate (ESCS) 37 to 65; Fly Ash 70 to 90; Boiler Slag
    60 to 90; Expanded Air-Cooled Slag 69 to 94.

    Parameters
    ----------
    material : str
        Filter by material name (partial match, case-insensitive).
        E.g., 'geofoam', 'tire', 'wood', 'fly ash', 'slag', 'cellular'.
        Empty returns all eight.

    Returns
    -------
    list of dict
        Each dict has key, material (as printed), unit_weight_pcf_low and
        _high (as printed), unit_weight_kn_m3_low and _high (the printed
        pcf at 0.157087 kN/m3 per pcf), specific_gravity_low and _high (as
        printed), reference.

    Raises
    ------
    ValueError
        If a filter is given and no row of the table matches it.
    """
    mat_lower = material.lower().strip()
    results = []
    for key, (name, pcf, sg) in _TABLE_3_1.items():
        if mat_lower and (mat_lower not in key.lower() and
                          mat_lower not in key.replace("_", " ") and
                          mat_lower not in name.lower()):
            continue
        results.append({
            "key": key,
            "material": name,
            "unit_weight_pcf_low": pcf[0],
            "unit_weight_pcf_high": pcf[1],
            "unit_weight_kn_m3_low": round(pcf[0] * _PCF_TO_KN_M3, 2),
            "unit_weight_kn_m3_high": round(pcf[1] * _PCF_TO_KN_M3, 2),
            "specific_gravity_low": sg[0],
            "specific_gravity_high": sg[1],
            "reference": _TABLE_3_1_REFERENCE,
        })
    if not results:
        raise _no_match(
            "Table 3-1", "p. 3-1", {"material": material},
            [("Fill types", [v[0] for v in _TABLE_3_1.values()])])
    return results


# ============================================================================
# Table 4-3: Applied Energy Guidelines (deep dynamic compaction)
# FHWA-NHI-16-027 (GEC-13) Vol I, Ch. 4, Sec. 2.3.3.2, p. 4-46.
# (REF-62: this replaces table_4_1_ddc_parameters, whose energies, passes,
# waiting times and depths no held manual prints; GEC-13 Table 4-1, p. 4-34,
# is the crane and cable sizes for tampers.)
# ============================================================================

_TABLE_4_3 = {
    "pervious_coarse": {
        "type_of_deposit": "Pervious coarse-grained soil (Zone 1 of Figure 4-5)",
        "unit_applied_energy_ft_lbf_per_ft3": (4100, 5200),
        "unit_applied_energy_kj_per_m3": (200, 250),
        "percent_standard_proctor_energy": (33, 41),
    },
    "semi_pervious": {
        "type_of_deposit": "Semipervious fine-grained soils (Zone 2 and clay "
                           "fills above the water table and Zone 3 of Figure 4-5)",
        "unit_applied_energy_ft_lbf_per_ft3": (5200, 7200),
        "unit_applied_energy_kj_per_m3": (250, 350),
        "percent_standard_proctor_energy": (41, 60),
    },
    "landfills": {
        "type_of_deposit": "Landfills",
        "unit_applied_energy_ft_lbf_per_ft3": (12400, 22700),
        "unit_applied_energy_kj_per_m3": (600, 1100),
        "percent_standard_proctor_energy": (100, 180),
    },
}

_TABLE_4_3_REFERENCE = ("FHWA-NHI-16-027 (GEC-13) Vol I, Ch. 4, Table 4-3 "
                        "Applied Energy Guidelines, p. 4-46")
_TABLE_4_3_NOTE = (
    "Standard Proctor energy equals 12,400 ft-lbf/ft3 (table note). The "
    "energy is per unit volume of the deposit: the average energy applied "
    "at the surface is the unit applied energy times the deposit thickness. "
    "Loose deposits take the higher value of the range, denser deposits the "
    "lower (p. 4-46). Zones are those of Figure 4-5; saturated Zone 3 clays "
    "are not recommended for deep dynamic compaction (p. 4-21)."
)


def table_4_3_applied_energy(soil_type: str = "") -> list:
    """Deep dynamic compaction applied energy guidelines (GEC-13 Table 4-3).

    The unit applied energy, per unit volume of the deposit, by type of
    deposit, as printed in FHWA-NHI-16-027 (GEC-13) Vol I, Table 4-3,
    p. 4-46: pervious coarse-grained soil (Zone 1 of Figure 4-5) 4,100 to
    5,200 ft-lbf/ft3 (200 to 250 kJ/m3), 33 to 41 % of standard Proctor
    energy; semipervious fine-grained soils (Zone 2, and clay fills above
    the water table and Zone 3) 5,200 to 7,200 (250 to 350), 41 to 60 %;
    landfills 12,400 to 22,700 (600 to 1100), 100 to 180 %. Multiply by the
    deposit thickness for the average energy at the surface (p. 4-46).

    The worked example on p. 4-46 multiplies 5,200 by a 26 ft deposit and
    prints 41,000 ft-lbf/ft2; 5,200 x 26 is 135,200 ft-lbf/ft2 (41,000 is
    that divided by 3.28). The table's two unit columns agree with each
    other (250 kJ/m3 = 5,221 ft-lbf/ft3), so the table is used as printed.

    Parameters
    ----------
    soil_type : str
        Filter by type of deposit (partial match, case-insensitive).
        E.g., 'pervious', 'semi', 'landfill', 'zone 1', 'clay'.

    Returns
    -------
    list of dict
        Each dict has key, type_of_deposit, the unit applied energy in
        ft-lbf/ft3 and kJ/m3 (low, high), percent of standard Proctor
        energy (low, high), reference and note.

    Raises
    ------
    ValueError
        If a filter is given and no row of the table matches it.
    """
    st_lower = soil_type.lower().strip()
    results = []
    for key, data in _TABLE_4_3.items():
        if st_lower and (st_lower not in key.lower() and
                         st_lower not in data["type_of_deposit"].lower()):
            continue
        results.append({
            "key": key,
            "type_of_deposit": data["type_of_deposit"],
            "unit_applied_energy_ft_lbf_per_ft3_low":
                data["unit_applied_energy_ft_lbf_per_ft3"][0],
            "unit_applied_energy_ft_lbf_per_ft3_high":
                data["unit_applied_energy_ft_lbf_per_ft3"][1],
            "unit_applied_energy_kj_per_m3_low":
                data["unit_applied_energy_kj_per_m3"][0],
            "unit_applied_energy_kj_per_m3_high":
                data["unit_applied_energy_kj_per_m3"][1],
            "percent_standard_proctor_energy_low":
                data["percent_standard_proctor_energy"][0],
            "percent_standard_proctor_energy_high":
                data["percent_standard_proctor_energy"][1],
            "reference": _TABLE_4_3_REFERENCE,
            "note": _TABLE_4_3_NOTE,
        })
    if not results:
        raise _no_match(
            "Table 4-3", "p. 4-46", {"soil_type": soil_type},
            [("Types of deposit",
              [d["type_of_deposit"] for d in _TABLE_4_3.values()])])
    return results


# ============================================================================
# Deep Dynamic Compaction — Depth of Improvement, Eq. 4-1
# FHWA-NHI-16-027 (GEC-13) Vol I, Ch. 4, Sec. 2.3.3.1, Eq. 4-1, p. 4-40;
# the range of n from Figure 4-21 (Mayne et al. 1984), p. 4-41.
# (REF-63: this replaces figure_4_1_ddc_depth's four soil types, n 0.35 to
# 0.6 after Lukas 1995, which GEC-13 does not print; GEC-13 Figure 4-1,
# p. 4-2, is a schematic illustration of deep dynamic compaction.)
# ============================================================================

_EQ_4_1_REFERENCE = (
    "FHWA-NHI-16-027 (GEC-13) Vol I, Ch. 4, Eq. 4-1, p. 4-40; "
    "range of n from Figure 4-21 (Mayne et al. 1984), p. 4-41"
)

# n as p. 4-40 prints it: "approximately 0.5 for most soils ... A value of
# 0.4 is typically used for landfills."
_EQ_4_1_N = {
    "most_soils": (0.5, "approximately 0.5 for most soils "
                        "(GEC-13 Eq. 4-1, p. 4-40)"),
    "landfill": (0.4, "0.4, typically used for landfills "
                      "(GEC-13 Eq. 4-1, p. 4-40)"),
}

# "As shown in Figure 4-21, n varies between 0.3 and 0.8." (p. 4-40)
_EQ_4_1_N_RANGE = (0.3, 0.8)

_OLD_SOIL_TYPES = ("pervious_coarse", "semi_pervious", "impervious",
                   "waste_fills")


def equation_4_1_ddc_depth(weight_tonnes: float, drop_height_m: float,
                           deposit: str = "most_soils",
                           n: float = None) -> dict:
    """Depth of improvement by deep dynamic compaction, GEC-13 Eq. 4-1.

    FHWA-NHI-16-027 (GEC-13) Vol I, Ch. 4, Sec. 2.3.3.1, Eq. 4-1, p. 4-40:

        D = n (W H)^(1/2)

    D = depth of improvement in meters; W = mass of tamper in megagrams
    (metric tonnes = 1.10 US ton); H = drop height in meters (1 meter =
    3.28 feet). n is "an empirical coefficient that is approximately 0.5
    for most soils. As shown in Figure 4-21, n varies between 0.3 and 0.8.
    A value of 0.4 is typically used for landfills." GEC-13 prints no
    table of n by soil type.

    Parameters
    ----------
    weight_tonnes : float
        Tamper mass W in megagrams (metric tonnes).
    drop_height_m : float
        Drop height H in meters.
    deposit : str
        'most_soils' (n = 0.5, the default) or 'landfill' (n = 0.4), as
        p. 4-40 prints them.
    n : float, optional
        A chosen n within Figure 4-21's range, 0.3 to 0.8 (p. 4-40); it
        replaces the deposit's n. A value outside the range is refused.

    Returns
    -------
    dict
        depth_m (at the n used), n, n_basis, deposit, depth_low_m and
        depth_high_m (at n = 0.3 and 0.8, Figure 4-21's range), n_low,
        n_high, range_basis, weight_tonnes, drop_height_m, reference,
        choices.

    Raises
    ------
    ValueError
        If W or H is not positive, the deposit is not one p. 4-40 names,
        or n is outside 0.3 to 0.8.
    """
    if weight_tonnes <= 0:
        raise ValueError("weight_tonnes must be > 0")
    if drop_height_m <= 0:
        raise ValueError("drop_height_m must be > 0")

    key = str(deposit).lower().strip()
    if key not in _EQ_4_1_N:
        valid = ", ".join(_EQ_4_1_N)
        hint = ""
        if key in _OLD_SOIL_TYPES:
            hint = (" GEC-13 prints no table of n by soil type (Eq. 4-1, "
                    "p. 4-40): n is about 0.5 for most soils and 0.4 for "
                    "landfills, and varies between 0.3 and 0.8 (Figure "
                    "4-21); give n to choose a value in that range.")
        raise ValueError(f"Unknown deposit '{deposit}'. Valid: {valid}.{hint}")

    n_low, n_high = _EQ_4_1_N_RANGE
    if n is None:
        n_used, n_basis = _EQ_4_1_N[key]
        n_given = False
    else:
        n_used = float(n)
        if not n_low <= n_used <= n_high:
            raise ValueError(
                f"n = {n} is outside 0.3 to 0.8, the range GEC-13 p. 4-40 "
                f"gives from Figure 4-21")
        n_basis = ("given; within 0.3 to 0.8, the range of Figure 4-21 "
                   "(GEC-13 p. 4-40)")
        n_given = True

    sqrt_wh = (weight_tonnes * drop_height_m) ** 0.5

    return {
        "depth_m": round(n_used * sqrt_wh, 2),
        "n": n_used,
        "n_basis": n_basis,
        "deposit": key,
        "depth_low_m": round(n_low * sqrt_wh, 2),
        "depth_high_m": round(n_high * sqrt_wh, 2),
        "n_low": n_low,
        "n_high": n_high,
        "range_basis": ("n varies between 0.3 and 0.8, as shown in "
                        "Figure 4-21 (GEC-13 p. 4-40)"),
        "weight_tonnes": weight_tonnes,
        "drop_height_m": drop_height_m,
        "reference": _EQ_4_1_REFERENCE,
        "choices": {
            "n": {
                "value": n_used,
                "given": n_given,
                "basis": n_basis,
                "alternatives": ("0.5 most soils; 0.4 landfills; any value "
                                 "0.3 to 0.8 (Figure 4-21)"),
            },
        },
    }


def figure_4_1_ddc_depth(weight_tonnes: float, drop_height_m: float,
                         deposit: str = "most_soils",
                         n: float = None) -> dict:
    """Alias of equation_4_1_ddc_depth (GEC-13 Eq. 4-1, p. 4-40).

    Kept under its old name, which cited a figure (REF-63); it returns
    exactly what equation_4_1_ddc_depth returns. The old soil types are
    refused: GEC-13 prints no table of n by soil type.
    """
    return equation_4_1_ddc_depth(weight_tonnes, drop_height_m,
                                  deposit=deposit, n=n)


# ============================================================================
# Table 8-1: Advantages and Disadvantages of Jet Grouting Systems
# FHWA-NHI-16-028 (GEC-13) Vol II, Ch. 8, Sec. 2.2.2, p. 8-26.
# (REF-62: this replaces table_8_2_jet_grouting_systems, whose column
# diameters and strengths by system no held manual prints; GEC-13 Table 8-2,
# p. 8-38, is the permeation grouts of a case history.)
# ============================================================================

_TABLE_8_1 = {
    "single_fluid": {
        "system": "Single Fluid",
        "advantages": [
            "Simple system for equipment and tooling",
            "Good for sealing vertical joints",
            "Good in cohesionless soils",
        ],
        "disadvantages": [
            "Smallest geometry created",
            "Hardest to control heave",
            "Difficult to control quality in cohesive soils",
        ],
    },
    "double_fluid": {
        "system": "Double Fluid",
        "advantages": [
            "Most utilized system",
            "Availability of equipment and tools",
            "High energy, good geometry achieved",
            "Most experience",
            "Often most economical",
        ],
        "disadvantages": [
            "Very difficult to control heave in cohesive soils",
            "Spoil handling can be difficult depending on fluid flows",
            "Not usually considered for underpinning",
        ],
    },
    "triple_fluid": {
        "system": "Triple Fluid",
        "advantages": [
            "Most controllable system",
            "Highest final quality in difficult soils (peat, soft clay)",
            "Best underpinning system",
            "Easiest to control spoil and heave",
        ],
        "disadvantages": [
            "Most complex system due to equipment and tooling",
            "Requires significant experience",
        ],
    },
    "superjet": {
        "system": "SuperJet/MegaJet/UltraJet/STRAJet",
        "advantages": [
            "Lowest cost per volume treated",
            "Best mixing achieved",
            "Largest column diameters",
        ],
        "disadvantages": [
            "Requires special equipment and tooling",
            "Difficult to control heave in cohesive soils",
            "Spoil handling may be difficult due to high flows used",
            "Cannot work near surface without support",
            "Highest logistical problems",
        ],
    },
    "x_jet": {
        "system": "X-Jet",
        "advantages": [
            "Confidence of geometry",
            "Controllable material costs",
            "Best for soft, cohesive soils",
        ],
        "disadvantages": [
            "Very specialized equipment that requires daily calibration",
            "Limited experience available",
        ],
    },
}

_TABLE_8_1_REFERENCE = ("FHWA-NHI-16-028 (GEC-13) Vol II, Ch. 8, Table 8-1 "
                        "Advantages and Disadvantages of Jet Grouting "
                        "Systems, p. 8-26")
_TABLE_8_1_NOTE = (
    "GEC-13 prints no column diameter or strength for each system. Jet "
    "grouted columns range from 2.5 to 15 ft in diameter depending on the "
    "method, and 3 to 5 ft columns are typical for underpinning and "
    "excavation support (p. 8-71). Soilcrete strength is a function of the "
    "cement content whatever the system; single-fluid strengths by soil are "
    "Table 8-6 (table_8_6_soilcrete_strength, p. 8-71). All systems have "
    "problems in very loose soils where the cement travels long distances, "
    "especially below the water table (p. 8-25)."
)


def table_8_1_jet_grouting_systems(system: str = "") -> list:
    """Jet grouting systems compared (GEC-13 Table 8-1, p. 8-26).

    The advantages and disadvantages of the single, double and triple fluid
    systems, SuperJet/MegaJet/UltraJet/STRAJet and X-Jet, as printed in
    FHWA-NHI-16-028 (GEC-13) Vol II, Table 8-1, p. 8-26. GEC-13 gives no
    column diameter or strength for each system: columns range from 2.5 to
    15 ft in diameter depending on the method (p. 8-71), and single-fluid
    soilcrete strengths by soil type are Table 8-6
    (``table_8_6_soilcrete_strength``).

    Parameters
    ----------
    system : str
        Filter by system name (partial match, case-insensitive).
        E.g., 'single', 'double', 'triple', 'superjet', 'x-jet'.

    Returns
    -------
    list of dict
        Each dict has key, system, advantages (list), disadvantages (list),
        reference and note.

    Raises
    ------
    ValueError
        If a filter is given and no system of the table matches it.
    """
    sys_lower = system.lower().strip()
    results = []
    for key, data in _TABLE_8_1.items():
        if sys_lower and (sys_lower not in key.lower() and
                          sys_lower not in data["system"].lower()):
            continue
        results.append({
            "key": key,
            "system": data["system"],
            "advantages": list(data["advantages"]),
            "disadvantages": list(data["disadvantages"]),
            "reference": _TABLE_8_1_REFERENCE,
            "note": _TABLE_8_1_NOTE,
        })
    if not results:
        raise _no_match(
            "Table 8-1", "p. 8-26", {"system": system},
            [("Systems", [d["system"] for d in _TABLE_8_1.values()])])
    return results


# ============================================================================
# Table 8-6: Range of Typical Soilcrete Strengths - Single-Fluid System
# FHWA-NHI-16-028 (GEC-13) Vol II, Ch. 8, Sec. 2.7.3, p. 8-71 (Burke 2004).
# ============================================================================

_PSI_TO_KPA = 6.894757

# (low psi, high psi); None = not printed ("less than 250").
_TABLE_8_6 = {
    "clean_sands_and_gravel": ("Clean sands and gravel", 750, 1250),
    "silts_and_silty_sands": ("Silts and Silty sands", 500, 750),
    "clays": ("Clays", 250, 500),
    "organic_silts_and_peats": ("Organic silts and peats", None, 250),
}

_TABLE_8_6_REFERENCE = ("FHWA-NHI-16-028 (GEC-13) Vol II, Ch. 8, Table 8-6 "
                        "Range of Typical Soilcrete Strengths - Single-Fluid "
                        "System, p. 8-71 (Burke 2004)")
_TABLE_8_6_NOTE = (
    "Soilcrete unconfined compressive strength for the single-fluid system, "
    "printed in psi (kPa converted at 1 psi = 6.894757 kPa). Whatever the "
    "system, strength is a function of the cement content: the triple fluid "
    "system typically has more replacement and higher strength, and "
    "double-fluid strengths may occasionally be lower from air entrainment. "
    "Design values should be restricted to 50 % or less of the ultimate "
    "strength, and a production field test is essential (p. 8-71)."
)


def table_8_6_soilcrete_strength(soil_type: str = "") -> list:
    """Typical single-fluid jet grout soilcrete strengths (GEC-13 Table 8-6).

    Soilcrete unconfined compressive strength by soil type, as printed in
    FHWA-NHI-16-028 (GEC-13) Vol II, Table 8-6, p. 8-71 (Burke 2004): clean
    sands and gravel 750 to 1,250 psi; silts and silty sands 500 to 750;
    clays 250 to 500; organic silts and peats less than 250. The single-fluid
    system only; design values at most 50 % of the ultimate strength
    (p. 8-71).

    Parameters
    ----------
    soil_type : str
        Filter by soil type (partial match, case-insensitive).
        E.g., 'sand', 'silt', 'clay', 'peat', 'organic'.

    Returns
    -------
    list of dict
        Each dict has key, soil_type, ucs_psi_low (None where the print
        says "less than"), ucs_psi_high, ucs_kpa_low, ucs_kpa_high,
        system, reference and note.

    Raises
    ------
    ValueError
        If a filter is given and no row of the table matches it.
    """
    st_lower = soil_type.lower().strip()
    results = []
    for key, (label, low, high) in _TABLE_8_6.items():
        if st_lower and (st_lower not in key.lower() and
                         st_lower not in label.lower()):
            continue
        results.append({
            "key": key,
            "soil_type": label,
            "ucs_psi_low": low,
            "ucs_psi_high": high,
            "ucs_kpa_low": None if low is None else round(low * _PSI_TO_KPA),
            "ucs_kpa_high": round(high * _PSI_TO_KPA),
            "system": "Single fluid",
            "reference": _TABLE_8_6_REFERENCE,
            "note": _TABLE_8_6_NOTE,
        })
    if not results:
        raise _no_match(
            "Table 8-6", "p. 8-71", {"soil_type": soil_type},
            [("Soil types", [v[0] for v in _TABLE_8_6.values()])])
    return results
