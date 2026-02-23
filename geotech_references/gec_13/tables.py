"""GEC-13 table lookup functions.

Digitized tables from FHWA-NHI-16-027 (GEC-13), Ground Modification
Methods Reference Manual, Volume I. Follows the DM7 pattern: private
data with ``_TABLE_*`` prefix, public lookup functions, case-insensitive keys.
"""

from geotech_references._interpolation import _linterp

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
                         "voids in sinkholes or abandoned mine shafts",
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
                         "Asphalt: silty, sandy and granular soils",
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
    """Technology applicability lookup from GEC-13 Table 1-2.

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
    return results


# ============================================================================
# Table 1-3: Technologies Classified by Function
# ============================================================================

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
            "Column Supported Embankments",
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
            "PVDs", "Stone Columns", "Aggregate Drains",
            "Earthquake Drains",
        ],
        "comment": "Vertical drains to accelerate consolidation or mitigate "
                   "liquefaction potential.",
    },
    "accelerate_consolidation": {
        "description": "Accelerate consolidation",
        "technologies": [
            "PVDs with Preloading", "PVDs with Surcharge",
            "Surcharge Only", "Vacuum Consolidation",
        ],
        "comment": "Used with soft compressible soils; surcharge alone may "
                   "be sufficient for thin compressible layers.",
    },
    "provide_lateral_stability": {
        "description": "Provide lateral stability",
        "technologies": [
            "Reinforced Embankments", "Reinforced Soil Walls",
            "Reinforced Soil Slopes", "Soil Nail Walls",
            "Deep Mixing for Shear Walls",
        ],
        "comment": "Both active and passive earth retention and slope "
                   "reinforcement methods.",
    },
    "increase_liquefaction_resistance": {
        "description": "Increase resistance to liquefaction",
        "technologies": [
            "Vibro-Compaction", "Dynamic Compaction",
            "Stone Columns", "Earthquake Drains",
            "Compaction Grouting", "Deep Mixing",
        ],
        "comment": "Densification methods for loose saturated sands; "
                   "drainage methods for pore pressure relief.",
    },
}


def table_1_3_by_function(function: str = "") -> list:
    """Technologies classified by function from GEC-13 Table 1-3.

    Parameters
    ----------
    function : str
        Filter by function name (partial match, case-insensitive).
        E.g., 'shear', 'density', 'drainage', 'liquefaction'.
        Empty string returns all functions.

    Returns
    -------
    list of dict
        Each dict has function, description, technologies, and comment.
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
        })
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
    """
    app_lower = application.lower().strip()
    results = []
    for entry in _TABLE_2_1:
        if app_lower and app_lower not in entry["application"].lower():
            continue
        results.append(dict(entry))
    return results


# ============================================================================
# Table 3-1: Lightweight Fill Material Properties (selected values)
# ============================================================================

_TABLE_3_1 = {
    "geofoam_eps": {
        "material": "Geofoam (EPS)",
        "unit_weight_pcf": (0.7, 3.0),
        "unit_weight_kn_m3": (0.11, 0.47),
        "notes": "Expanded polystyrene blocks; compressive strength 2-18 psi",
    },
    "foamed_concrete": {
        "material": "Foamed Concrete",
        "unit_weight_pcf": (24, 55),
        "unit_weight_kn_m3": (3.8, 8.6),
        "notes": "Cellular concrete; strength varies with density",
    },
    "wood_fiber": {
        "material": "Wood Fiber",
        "unit_weight_pcf": (35, 55),
        "unit_weight_kn_m3": (5.5, 8.6),
        "notes": "Compacted wood chips/fibers; susceptible to decomposition below GWT",
    },
    "blast_furnace_slag": {
        "material": "Blast Furnace Slag",
        "unit_weight_pcf": (60, 75),
        "unit_weight_kn_m3": (9.4, 11.8),
        "notes": "Air-cooled or expanded; granular lightweight fill",
    },
    "fly_ash": {
        "material": "Fly Ash",
        "unit_weight_pcf": (70, 90),
        "unit_weight_kn_m3": (11.0, 14.1),
        "notes": "Coal combustion byproduct; needs moisture control",
    },
    "expanded_shale": {
        "material": "Expanded Shale, Clay, and Slate",
        "unit_weight_pcf": (40, 65),
        "unit_weight_kn_m3": (6.3, 10.2),
        "notes": "Rotary kiln produced; durable and chemically inert",
    },
    "tire_shreds": {
        "material": "Tire Derived Aggregate (TDA)",
        "unit_weight_pcf": (37, 55),
        "unit_weight_kn_m3": (5.8, 8.6),
        "notes": "Shredded tires; max fill height ~10 ft per FHWA guidelines",
    },
    "boiler_slag": {
        "material": "Boiler Slag",
        "unit_weight_pcf": (60, 90),
        "unit_weight_kn_m3": (9.4, 14.1),
        "notes": "Wet-bottom furnace byproduct; hard and angular",
    },
}


def table_3_1_lightweight_fill(material: str = "") -> list:
    """Lightweight fill material properties from GEC-13 Chapter 3.

    Parameters
    ----------
    material : str
        Filter by material name (partial match, case-insensitive).
        E.g., 'geofoam', 'tire', 'wood', 'fly ash'.

    Returns
    -------
    list of dict
        Each dict has material, unit_weight_pcf (low, high),
        unit_weight_kn_m3 (low, high), and notes.
    """
    mat_lower = material.lower().strip()
    results = []
    for key, data in _TABLE_3_1.items():
        if mat_lower and (mat_lower not in key.lower() and
                          mat_lower not in data["material"].lower()):
            continue
        results.append({
            "key": key,
            "material": data["material"],
            "unit_weight_pcf_low": data["unit_weight_pcf"][0],
            "unit_weight_pcf_high": data["unit_weight_pcf"][1],
            "unit_weight_kn_m3_low": data["unit_weight_kn_m3"][0],
            "unit_weight_kn_m3_high": data["unit_weight_kn_m3"][1],
            "notes": data["notes"],
        })
    return results


# ============================================================================
# Table 4-1: Deep Dynamic Compaction — Typical Design Parameters
# ============================================================================

_TABLE_4_1 = {
    "pervious_coarse": {
        "soil_type": "Pervious coarse-grained soils (Zone 1)",
        "energy_per_pass_ft_lbs_per_ft2": (5000, 8000),
        "number_of_passes": (5, 10),
        "time_between_passes_weeks": 1,
        "max_depth_ft": 36,
        "notes": "Clean sands and gravels; most effective for DDC",
    },
    "semi_pervious": {
        "soil_type": "Semi-pervious soils (Zone 2)",
        "energy_per_pass_ft_lbs_per_ft2": (5000, 10000),
        "number_of_passes": (7, 14),
        "time_between_passes_weeks": (1, 4),
        "max_depth_ft": 30,
        "notes": "Silty sands, sandy silts; requires pore pressure dissipation",
    },
    "impervious": {
        "soil_type": "Impervious fine-grained soils (Zone 3)",
        "energy_per_pass_ft_lbs_per_ft2": (8000, 12000),
        "number_of_passes": (10, 15),
        "time_between_passes_weeks": (2, 6),
        "max_depth_ft": 20,
        "notes": "Clays and silts; limited effectiveness; not recommended for "
                 "saturated clays",
    },
}


def table_4_1_ddc_parameters(soil_type: str = "") -> list:
    """Deep Dynamic Compaction design parameters from GEC-13 Chapter 4.

    Parameters
    ----------
    soil_type : str
        Filter by soil type (partial match, case-insensitive).
        E.g., 'pervious', 'semi', 'impervious', 'sand', 'clay'.

    Returns
    -------
    list of dict
        Each dict has soil_type, energy range, number_of_passes range,
        time_between_passes, max_depth_ft, and notes.
    """
    st_lower = soil_type.lower().strip()
    results = []
    for key, data in _TABLE_4_1.items():
        if st_lower and (st_lower not in key.lower() and
                         st_lower not in data["soil_type"].lower()):
            continue
        entry = {"key": key}
        for k, v in data.items():
            entry[k] = v
        results.append(entry)
    return results


# ============================================================================
# Deep Dynamic Compaction — Depth of Influence
# D_max = n * sqrt(W * H) (Lukas 1995)
# n = empirical coefficient depending on soil type
# ============================================================================

_DDC_N_COEFFICIENTS = {
    "pervious_coarse": {"n_low": 0.5, "n_high": 0.6,
                        "description": "Clean sands and gravels"},
    "semi_pervious": {"n_low": 0.35, "n_high": 0.5,
                      "description": "Silty sands, sandy silts"},
    "impervious": {"n_low": 0.35, "n_high": 0.40,
                   "description": "Clays and silts (limited effectiveness)"},
    "waste_fills": {"n_low": 0.35, "n_high": 0.5,
                    "description": "Landfills, demolition debris, mine spoils"},
}


def figure_4_1_ddc_depth(weight_tonnes: float, drop_height_m: float,
                         soil_type: str = "pervious_coarse") -> dict:
    """Estimate depth of influence for deep dynamic compaction.

    Uses the Lukas (1995) empirical relationship:
        D_max = n * sqrt(W * H)
    where W = weight in tonnes, H = drop height in meters.

    Parameters
    ----------
    weight_tonnes : float
        Drop weight in metric tonnes (typically 5-30 tonnes).
    drop_height_m : float
        Drop height in meters (typically 10-25 m).
    soil_type : str
        Soil classification: 'pervious_coarse', 'semi_pervious',
        'impervious', or 'waste_fills'.

    Returns
    -------
    dict
        depth_low_m, depth_high_m, n_low, n_high, soil_type, description.

    Raises
    ------
    ValueError
        If weight or height is non-positive, or soil_type is unknown.
    """
    if weight_tonnes <= 0:
        raise ValueError("weight_tonnes must be > 0")
    if drop_height_m <= 0:
        raise ValueError("drop_height_m must be > 0")

    key = soil_type.lower().strip()
    if key not in _DDC_N_COEFFICIENTS:
        valid = ", ".join(_DDC_N_COEFFICIENTS.keys())
        raise ValueError(f"Unknown soil_type '{soil_type}'. Valid: {valid}")

    data = _DDC_N_COEFFICIENTS[key]
    sqrt_wh = (weight_tonnes * drop_height_m) ** 0.5
    d_low = data["n_low"] * sqrt_wh
    d_high = data["n_high"] * sqrt_wh

    return {
        "depth_low_m": round(d_low, 2),
        "depth_high_m": round(d_high, 2),
        "n_low": data["n_low"],
        "n_high": data["n_high"],
        "weight_tonnes": weight_tonnes,
        "drop_height_m": drop_height_m,
        "soil_type": key,
        "description": data["description"],
    }
