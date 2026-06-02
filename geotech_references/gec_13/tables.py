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


# ============================================================================
# Table 7-2: Deep Mixing — Typical Unconfined Compressive Strength (qu)
# (qu in kPa at 28 days)
# ============================================================================

_TABLE_7_2 = {
    "soft_clay_ddm": {
        "soil_type": "Soft clay",
        "method": "Dry deep mixing (DDM)",
        "binder": "Lime-cement blend",
        "qu_low_kpa": 200,
        "qu_high_kpa": 500,
        "notes": "Scandinavian practice; lower end for high water content soils",
    },
    "soft_clay_wdm": {
        "soil_type": "Soft clay",
        "method": "Wet deep mixing (WDM)",
        "binder": "Portland cement slurry",
        "qu_low_kpa": 500,
        "qu_high_kpa": 2000,
        "notes": "Higher binder content achievable with wet mixing",
    },
    "organic_peat_ddm": {
        "soil_type": "Organic clay / peat",
        "method": "Dry deep mixing (DDM)",
        "binder": "Lime-cement blend",
        "qu_low_kpa": 100,
        "qu_high_kpa": 400,
        "notes": "Organic content > 6% may inhibit hydration; treatability testing required",
    },
    "organic_peat_wdm": {
        "soil_type": "Organic clay / peat",
        "method": "Wet deep mixing (WDM)",
        "binder": "Portland cement slurry",
        "qu_low_kpa": 200,
        "qu_high_kpa": 800,
        "notes": "Lower strength than mineral clays; higher w/c ratio may be needed",
    },
    "silt_ddm": {
        "soil_type": "Silt",
        "method": "Dry deep mixing (DDM)",
        "binder": "Lime-cement blend",
        "qu_low_kpa": 300,
        "qu_high_kpa": 800,
        "notes": "Effective when water content is high",
    },
    "silt_wdm": {
        "soil_type": "Silt",
        "method": "Wet deep mixing (WDM)",
        "binder": "Portland cement slurry",
        "qu_low_kpa": 500,
        "qu_high_kpa": 2000,
        "notes": "Consistent with soft clay WDM performance",
    },
    "loose_sand_wdm": {
        "soil_type": "Loose to medium sand",
        "method": "Wet deep mixing (WDM)",
        "binder": "Portland cement slurry",
        "qu_low_kpa": 1000,
        "qu_high_kpa": 4000,
        "notes": "Granular soils respond well to cement; higher strength than cohesive soils",
    },
}


def table_7_2_deep_mixing_strength(soil_type: str = "", method: str = "") -> list:
    """Typical unconfined compressive strength (qu) for deep mixed soil (Table 7-2).

    Parameters
    ----------
    soil_type : str
        Filter by soil type (partial match, case-insensitive).
        E.g., 'clay', 'peat', 'silt', 'sand', 'organic'.
    method : str
        Filter by mixing method (partial match, case-insensitive).
        E.g., 'dry', 'wet', 'DDM', 'WDM'.

    Returns
    -------
    list of dict
        Each dict has soil_type, method, binder, qu_low_kpa,
        qu_high_kpa, and notes.
    """
    st_lower = soil_type.lower().strip()
    meth_lower = method.lower().strip()
    results = []
    for key, data in _TABLE_7_2.items():
        if st_lower and (st_lower not in key.lower() and
                         st_lower not in data["soil_type"].lower()):
            continue
        if meth_lower and (meth_lower not in key.lower() and
                           meth_lower not in data["method"].lower()):
            continue
        entry = {"key": key}
        entry.update(data)
        results.append(entry)
    return results


# ============================================================================
# Table 8-2: Jet Grouting System Comparison
# ============================================================================

_TABLE_8_2 = {
    "single_fluid": {
        "system": "Single-fluid",
        "fluids": "Grout jet only",
        "column_diameter_mm_low": 300,
        "column_diameter_mm_high": 600,
        "typical_soils": "Soft clays, silts, loose sands",
        "strength_mpa_low": 1,
        "strength_mpa_high": 5,
        "notes": "Simplest system; smallest column diameter; most economical in soft soils",
    },
    "double_fluid": {
        "system": "Double-fluid",
        "fluids": "Grout jet with air shroud",
        "column_diameter_mm_low": 600,
        "column_diameter_mm_high": 1000,
        "typical_soils": "Clays, silts, loose to medium sands",
        "strength_mpa_low": 1,
        "strength_mpa_high": 7,
        "notes": "Air shroud increases cutting energy and column diameter",
    },
    "triple_fluid": {
        "system": "Triple-fluid",
        "fluids": "Separate water jet, air shroud, and grout injection",
        "column_diameter_mm_low": 600,
        "column_diameter_mm_high": 2000,
        "typical_soils": "Wide range: silts, clays, sands, gravels",
        "strength_mpa_low": 1,
        "strength_mpa_high": 10,
        "notes": "Largest columns; highest cost; most versatile soil range",
    },
}


def table_8_2_jet_grouting_systems(system: str = "") -> list:
    """Jet grouting system comparison — diameter, soils, and strength (Table 8-2).

    Parameters
    ----------
    system : str
        Filter by system name (partial match, case-insensitive).
        E.g., 'single', 'double', 'triple'.

    Returns
    -------
    list of dict
        Each dict has system, fluids, column_diameter_mm (low/high),
        typical_soils, strength_mpa (low/high), and notes.
    """
    sys_lower = system.lower().strip()
    results = []
    for key, data in _TABLE_8_2.items():
        if sys_lower and (sys_lower not in key.lower() and
                          sys_lower not in data["system"].lower()):
            continue
        entry = {"key": key}
        entry.update(data)
        results.append(entry)
    return results


# ============================================================================
# Table 9-2: Soil Nail Bond Strength — Ultimate Unit Resistance (qu_nail)
# Values for drilled and pressure-grouted nails per GEC-7 / GEC-13 Ch 9.
# ============================================================================

_TABLE_9_2 = {
    "cohesive_soft": {
        "soil_type": "Cohesive soils — soft to medium (su = 20–50 kPa)",
        "installation": "Drilled and grouted",
        "qu_nail_low_kpa": 20,
        "qu_nail_high_kpa": 55,
        "notes": "Low bond; marginal applicability; verify with field pullout tests",
    },
    "cohesive_stiff": {
        "soil_type": "Cohesive soils — stiff to hard (su = 50–150 kPa)",
        "installation": "Drilled and grouted",
        "qu_nail_low_kpa": 40,
        "qu_nail_high_kpa": 100,
        "notes": "Most common cohesive soil nail condition",
    },
    "cohesionless_loose": {
        "soil_type": "Cohesionless soils — loose to medium (SPT N = 10–30)",
        "installation": "Drilled and grouted",
        "qu_nail_low_kpa": 55,
        "qu_nail_high_kpa": 145,
        "notes": "Apparent cohesion required for face stability during construction",
    },
    "cohesionless_dense": {
        "soil_type": "Cohesionless soils — dense to very dense (SPT N > 30)",
        "installation": "Drilled and grouted",
        "qu_nail_low_kpa": 100,
        "qu_nail_high_kpa": 190,
        "notes": "High bond in dense granular soils",
    },
    "glacial_till": {
        "soil_type": "Glacial till / mixed granular-cohesive",
        "installation": "Drilled and grouted",
        "qu_nail_low_kpa": 100,
        "qu_nail_high_kpa": 200,
        "notes": "Variable; depends on fines content and compaction state",
    },
    "weathered_rock": {
        "soil_type": "Weathered rock / residual soils",
        "installation": "Drilled and grouted",
        "qu_nail_low_kpa": 200,
        "qu_nail_high_kpa": 400,
        "notes": "Significant variability depending on rock type and weathering grade",
    },
    "soft_rock": {
        "soil_type": "Soft rock (soft sandstone, shale, soft limestone)",
        "installation": "Drilled and grouted",
        "qu_nail_low_kpa": 300,
        "qu_nail_high_kpa": 800,
        "notes": "Verify with pullout tests; rock quality strongly affects bond",
    },
    "hard_rock": {
        "soil_type": "Hard rock (granite, hard limestone, quartzite)",
        "installation": "Drilled and grouted",
        "qu_nail_low_kpa": 500,
        "qu_nail_high_kpa": 3000,
        "notes": "Bond often limited by grout/drill-hole interface rather than rock strength",
    },
}


def table_9_2_nail_bond_strength(soil_type: str = "") -> list:
    """Soil nail ultimate unit bond resistance by soil type (Table 9-2).

    Values for drilled and pressure-grouted nails. Field pullout tests
    required per GEC-7 (FHWA-NHI-14-007).

    Parameters
    ----------
    soil_type : str
        Filter by soil type (partial match, case-insensitive).
        E.g., 'cohesive', 'cohesionless', 'rock', 'glacial', 'sand'.

    Returns
    -------
    list of dict
        Each dict has soil_type, installation, qu_nail_low_kpa,
        qu_nail_high_kpa, and notes.
    """
    st_lower = soil_type.lower().strip()
    results = []
    for key, data in _TABLE_9_2.items():
        if st_lower and (st_lower not in key.lower() and
                         st_lower not in data["soil_type"].lower()):
            continue
        entry = {"key": key}
        entry.update(data)
        results.append(entry)
    return results


# ============================================================================
# Table 10-1: Micropile Bond Zone Unit Resistance (alpha_bond) by Soil/Rock Type
# Grout types A–D per FHWA-NHI-05-039 classification.
# ============================================================================

_TABLE_10_1 = {
    "soft_clay": {
        "soil_type": "Soft clay (su < 50 kPa)",
        "type_a": (35, 70),
        "type_b": (35, 95),
        "type_cd": (50, 120),
    },
    "medium_clay": {
        "soil_type": "Medium stiff clay (su = 50–100 kPa)",
        "type_a": (40, 75),
        "type_b": (50, 120),
        "type_cd": (65, 160),
    },
    "loose_sand": {
        "soil_type": "Loose to medium sand (SPT N = 10–30)",
        "type_a": (55, 90),
        "type_b": (75, 145),
        "type_cd": (95, 190),
    },
    "dense_sand": {
        "soil_type": "Dense to very dense sand (SPT N > 30)",
        "type_a": (75, 110),
        "type_b": (95, 180),
        "type_cd": (120, 240),
    },
    "gravel": {
        "soil_type": "Gravel and cobbles",
        "type_a": (90, 140),
        "type_b": (110, 200),
        "type_cd": (145, 265),
    },
    "soft_rock": {
        "soil_type": "Soft rock (soft sandstone, shale, soft limestone)",
        "type_a": (None, None),
        "type_b": (200, 600),
        "type_cd": (250, 750),
    },
    "hard_rock": {
        "soil_type": "Hard rock (granite, hard limestone, quartzite)",
        "type_a": (None, None),
        "type_b": (500, 2500),
        "type_cd": (600, 3000),
    },
}


def table_10_1_micropile_bond_stress(soil_type: str = "",
                                     grout_type: str = "") -> list:
    """Micropile bond zone unit resistance by soil/rock type and grout type (Table 10-1).

    Grout types:
      Type A: Gravity-placed neat cement grout
      Type B: Pressure-injected through drill pipe
      Type C/D: Post-grouted through sleeve pipes

    Based on GEC-13 Chapter 10 and FHWA-NHI-05-039 Table 5-3.
    Verify with field load tests.

    Parameters
    ----------
    soil_type : str
        Filter by soil or rock type (partial match, case-insensitive).
        E.g., 'clay', 'sand', 'rock', 'gravel'.
    grout_type : str
        Filter by grout type: 'A', 'B', 'C', 'D', or 'CD'.
        Empty string returns all types.

    Returns
    -------
    list of dict
        Each dict has soil_type plus alpha_bond_low_kpa and
        alpha_bond_high_kpa for each applicable grout type.
    """
    st_lower = soil_type.lower().strip()
    gt_lower = grout_type.lower().strip()
    results = []
    for key, data in _TABLE_10_1.items():
        if st_lower and (st_lower not in key.lower() and
                         st_lower not in data["soil_type"].lower()):
            continue
        entry = {"key": key, "soil_type": data["soil_type"]}
        include_a = not gt_lower or gt_lower == "a"
        include_b = not gt_lower or gt_lower == "b"
        include_cd = not gt_lower or gt_lower in ("c", "d", "cd")
        if include_a and data["type_a"][0] is not None:
            entry["type_a_alpha_bond_low_kpa"] = data["type_a"][0]
            entry["type_a_alpha_bond_high_kpa"] = data["type_a"][1]
        if include_b:
            entry["type_b_alpha_bond_low_kpa"] = data["type_b"][0]
            entry["type_b_alpha_bond_high_kpa"] = data["type_b"][1]
        if include_cd:
            entry["type_cd_alpha_bond_low_kpa"] = data["type_cd"][0]
            entry["type_cd_alpha_bond_high_kpa"] = data["type_cd"][1]
        results.append(entry)
    return results


# ============================================================================
# Table 11-1: Geosynthetic Reduction Factors
# RF_ID = installation damage, RF_CR = creep, RF_CBD = chemical/biological
# Per AASHTO M288 and GEC-11 Table 3-3.
# ============================================================================

_TABLE_11_1 = {
    "pp_woven_geotextile": {
        "product": "PP woven geotextile",
        "polymer": "Polypropylene (PP)",
        "rf_id_low": 1.10,
        "rf_id_high": 3.00,
        "rf_cr_low": 1.50,
        "rf_cr_high": 4.50,
        "rf_cbd_low": 1.05,
        "rf_cbd_high": 1.50,
        "notes": "RF_ID depends on fill gradation and compaction energy",
    },
    "hdpe_geogrid": {
        "product": "HDPE geogrid",
        "polymer": "High-density polyethylene (HDPE)",
        "rf_id_low": 1.05,
        "rf_id_high": 2.50,
        "rf_cr_low": 2.00,
        "rf_cr_high": 5.00,
        "rf_cbd_low": 1.05,
        "rf_cbd_high": 1.50,
        "notes": "High creep susceptibility of HDPE; use long-term creep test data",
    },
    "pet_geogrid": {
        "product": "PET geogrid",
        "polymer": "Polyester (PET)",
        "rf_id_low": 1.05,
        "rf_id_high": 2.00,
        "rf_cr_low": 1.60,
        "rf_cr_high": 2.50,
        "rf_cbd_low": 1.20,
        "rf_cbd_high": 1.60,
        "notes": "RF_CBD increases for acidic (pH < 4.5) or alkaline (pH > 9) conditions",
    },
    "pet_woven_geotextile": {
        "product": "PET woven geotextile",
        "polymer": "Polyester (PET)",
        "rf_id_low": 1.10,
        "rf_id_high": 2.50,
        "rf_cr_low": 1.60,
        "rf_cr_high": 2.50,
        "rf_cbd_low": 1.20,
        "rf_cbd_high": 1.60,
        "notes": "Same polymer as PET geogrid; typically higher RF_ID due to thinner cross-section",
    },
}


def table_11_1_geosynthetic_reduction_factors(product: str = "",
                                               polymer: str = "") -> list:
    """Geosynthetic reduction factors for LTDS calculation (Table 11-1).

    RF_ID: installation damage (fill gradation and compaction energy)
    RF_CR: creep (time-dependent elongation under sustained load)
    RF_CBD: chemical and biological degradation (pH, oxidation)

    Used in LTDS = T_ult / (RF_ID * RF_CR * RF_CBD * FS).
    Per AASHTO M288 and GEC-11 Table 3-3.

    Parameters
    ----------
    product : str
        Filter by product type (partial match, case-insensitive).
        E.g., 'geogrid', 'geotextile', 'woven'.
    polymer : str
        Filter by polymer type (partial match, case-insensitive).
        E.g., 'PP', 'HDPE', 'PET', 'polyester'.

    Returns
    -------
    list of dict
        Each dict has product, polymer, rf_id (low/high),
        rf_cr (low/high), rf_cbd (low/high), and notes.
    """
    prod_lower = product.lower().strip()
    poly_lower = polymer.lower().strip()
    results = []
    for key, data in _TABLE_11_1.items():
        if prod_lower and (prod_lower not in key.lower() and
                           prod_lower not in data["product"].lower()):
            continue
        if poly_lower and (poly_lower not in key.lower() and
                           poly_lower not in data["polymer"].lower()):
            continue
        entry = {"key": key}
        entry.update(data)
        results.append(entry)
    return results
