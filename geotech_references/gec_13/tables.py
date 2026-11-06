"""GEC-13 table lookup functions.

Digitized tables from GEC-13, Ground Modification Methods Reference
Manual: FHWA-NHI-16-027 (Volume I, chapters 1-5) and FHWA-NHI-16-028
(Volume II, chapters 6-10; the Table 8-1 and 8-6 lookups), and the deep
dynamic compaction depth, Eq. 4-1 (``equation_4_1_ddc_depth``). Follows the DM7
pattern: private data with ``_TABLE_*`` prefix, public lookup functions,
case-insensitive keys.
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
    return results
