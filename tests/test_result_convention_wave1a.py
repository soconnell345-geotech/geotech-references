"""REF-78 wave 1a: every lookup of the pavement family and EM 1110-2-2104
keeps the result convention (geotech_references._units).

A dict result carries a unit for every number, ``printed_page`` and
``pdf_page_index`` (consistent with its reference string); the one lookup
that returns a bare number (``aci_beta1``) labels it in its docstring. Each
lookup is called once below with made-up inputs; a new lookup in these
packages fails ``test_every_lookup_has_one_call`` until it is added here.
"""

import inspect
import re

import pytest

from tests import _result_convention as rc

PACKAGES = ("aashto_1993", "ufc_pavement", "fhwa_pavements",
            "ufc_flexible_practice", "ufc_concrete_practice", "ufc_backfill",
            "ufc_expansive", "ufc_stabilization", "em_2104")
LOOKUPS = rc.lookups(PACKAGES)

# Takes Python callables, so it is called by hand below.
BY_HAND = {"aashto_1993.environmental.performance_period_iteration"}

CALLS = {
    "aashto_1993.composite_k.composite_k_subbase": {
        "dsb_in": 6.0, "esb_psi": 20000, "mr_psi": 7000},
    "aashto_1993.composite_k.effective_modulus_subgrade_reaction": {
        "dsb_in": 6.0, "dsg_ft": 15.0, "esb_psi": None, "ls": 0.0,
        "seasonal": [{"esb_psi": 20000, "mr_psi": 7000}], "slab_d_in": 9.0},
    "aashto_1993.composite_k.k_loss_of_support": {"k_pci": 540, "ls": 2.0},
    "aashto_1993.composite_k.k_rigid_foundation_correction": {
        "dsg_ft": 5.0, "k_inf_pci": 230, "mr_psi": 4000},
    "aashto_1993.composite_k.loss_of_support_values": {"material": None},
    "aashto_1993.composite_k.relative_damage_rigid": {
        "d_in": 9.0, "k_pci": 1350},
    "aashto_1993.environmental.frost_heave_rate_group": {"uscs_group": "gw"},
    "aashto_1993.environmental.frost_heave_serviceability_loss": {
        "delta_psi_max": 2.0, "pf_pct": 30, "phi_mm_day": 5, "t_yr": 15},
    "aashto_1993.environmental.frost_susceptibility_classification": {
        "rate_mm_day": 0.3},
    "aashto_1993.environmental.max_serviceability_loss_frost": {
        "depth_ft": 5, "drainage_quality": "poor"},
    "aashto_1993.environmental.potential_vertical_rise": {
        "condition": "average", "pi": 50, "thickness_ft": 5},
    "aashto_1993.environmental.swell_probability_guidance": {
        "pi": 35, "thickness_ft": 3, "vr_in": None},
    "aashto_1993.environmental.swell_rate_constant_theta": {
        "moisture_supply_frac": 0.0, "soil_fabric_frac": 0.0},
    "aashto_1993.environmental.swelling_serviceability_loss": {
        "ps_pct": 60, "t_yr": 15, "theta": 0.1, "vr_in": 2},
    "aashto_1993.environmental.total_environmental_loss": {
        "frost": None, "swelling": {"ps_pct": 60, "theta": 0.1, "vr_in": 2},
        "t_yr": 15},
    "aashto_1993.environmental.weighted_swell_parameters": {
        "sections": [{"length_ft": 100, "vr_in": 0.3}]},
    "aashto_1993.equations.aggregate_loss_brazil": {
        "bladings": 6, "grade_pct": 3, "ladt": 200, "radius_ft": 1000},
    "aashto_1993.equations.aggregate_loss_truck_traffic": {
        "loaded_trucks_thousands": 0},
    "aashto_1993.equations.annual_aggregate_loss_kenya": {
        "grade_pct": 5, "gravel_type": "lateritic", "rainfall_in": 30,
        "traffic_thousands": 2},
    "aashto_1993.equations.design_serviceability_loss": {"po": 4.2, "pt": 2.5},
    "aashto_1993.equations.effective_roadbed_resilient_modulus": {
        "monthly_mr_psi": [20000, 20000, 2500, 4000, 4000, 7000, 7000, 7000, 7000, 7000, 4000, 20000]},
    "aashto_1993.equations.flexible_sn_from_w18": {
        "delta_psi": 1.9, "max_iter": 200, "mr_psi": 5000,
        "sn_bounds": [0.5, 25.0], "so": 0.35, "tol": 1e-07, "w18": 5000000.0,
        "zr": -1.645},
    "aashto_1993.equations.flexible_w18_from_sn": {
        "delta_psi": 1.9, "mr_psi": 5000, "sn": 5.0, "so": 0.35, "zr": -1.645},
    "aashto_1993.equations.layer_coefficient_a2_granular_base": {
        "ebs_psi": 30000},
    "aashto_1993.equations.layer_coefficient_a3_granular_subbase": {
        "esb_psi": 15000},
    "aashto_1993.equations.minimum_layer_thicknesses": {
        "a1": 0.42, "a2": 0.14, "a3": 0.11, "m2": 1.0, "m3": 1.0,
        "sn_over_base": 2.0, "sn_over_roadbed": 5.0, "sn_over_subbase": 3.5},
    "aashto_1993.equations.modulus_subgrade_reaction_simple": {"mr_psi": 7000},
    "aashto_1993.equations.relative_damage_uf": {"mr_psi": 5000},
    "aashto_1993.equations.rigid_d_from_w18": {
        "cd": 1.0, "d_bounds": [4.0, 20.0], "delta_psi": 1.7,
        "ec_psi": 5000000.0, "j": 3.2, "k_pci": 72, "max_iter": 200, "pt": 2.5,
        "sc_psi": 650, "so": 0.29, "tol": 1e-07, "w18": 5100000.0, "zr": -1.645},
    "aashto_1993.equations.rigid_w18_from_d": {
        "cd": 1.0, "d": 10.0, "delta_psi": 1.7, "ec_psi": 5000000.0, "j": 3.2,
        "k_pci": 72, "pt": 2.5, "sc_psi": 650, "so": 0.29, "zr": -1.645},
    "aashto_1993.equations.stage_reliability": {
        "n_stages": 2, "overall_reliability_pct": 95},
    "aashto_1993.equations.structural_number": {
        "a1": 0.42, "a2": 0.0, "a3": 0.0, "d1": 4.0, "d2": 0.0, "d3": 0.0,
        "m2": 1.0, "m3": 1.0},
    "aashto_1993.lef.load_equivalency_factor": {
        "axle_config": "single", "axle_load_kips": 18.0, "d_in": 9.0,
        "pavement_type": "rigid", "pt": 2.5, "sn": None},
    "aashto_1993.tables.directional_distribution_default": {},
    "aashto_1993.tables.drainage_cd_rigid": {
        "pct_saturation_time": "1-5%", "quality": "fair"},
    "aashto_1993.tables.drainage_mi_flexible": {
        "pct_saturation_time": "1-5%", "quality": "fair"},
    "aashto_1993.tables.esal_flexible_single_axle": {
        "axle_load_kips": 18.0, "pt": 2.5, "sn": 5.0},
    "aashto_1993.tables.esal_flexible_tandem_axle": {
        "axle_load_kips": 36.0, "pt": 2.5, "sn": 5.0},
    "aashto_1993.tables.esal_rigid_single_axle": {
        "axle_load_kips": 18.0, "d_in": 9.0, "pt": 2.5},
    "aashto_1993.tables.esal_rigid_tandem_axle": {
        "axle_load_kips": 36.0, "d_in": 9.0, "pt": 2.5},
    "aashto_1993.tables.lane_distribution_factor": {
        "num_lanes_per_direction": 1},
    "aashto_1993.tables.layer_coefficient_a1_asphalt": {"eac_psi": 106000},
    "aashto_1993.tables.layer_coefficient_a2_bituminous_treated": {
        "marshall_stability_lb": 1600},
    "aashto_1993.tables.layer_coefficient_a2_cement_treated": {
        "ucs_7day_psi": 800},
    "aashto_1993.tables.load_transfer_coefficient_j": {
        "load_transfer_devices": True, "pavement_type": "plain_jointed_jrcp",
        "shoulder_type": "asphalt"},
    "aashto_1993.tables.minimum_layer_thickness": {"esal": 30000},
    "aashto_1993.tables.overall_standard_deviation_range": {
        "pavement_type": "flexible"},
    "aashto_1993.tables.quality_of_drainage_definitions": {"quality": None},
    "aashto_1993.tables.recommended_reliability": {
        "area": "urban", "functional_class": "interstate_freeway"},
    "aashto_1993.tables.standard_normal_deviate_zr": {"reliability_pct": 50},
    "aashto_1993.tables.terminal_serviceability_guidance": {"pt": 2.5},
    "aashto_1993.tables.unbound_k1_k2": {
        "layer": "base", "moisture_condition": "dry"},
    "em_2104.design.design_doubly_reinforced": {
        "b": 12.0, "beta1": None, "d": 30.0, "dprime": 3.0, "ec": 0.003,
        "es": 29000.0, "fc_prime": 4.0, "fy": 60.0, "h": 34.0, "mn": 8000.0,
        "pn": 0.0, "rho_over_rho_b": 0.25},
    "em_2104.design.design_singly_reinforced": {
        "b": 12.0, "d": 6.0, "fc_prime": 4.0, "fy": 60.0, "h": 9.0,
        "mn": 147.0, "pn": 0.0},
    "em_2104.design.kd_table_d1": {
        "beta1": 0.85, "ec": 0.003, "es": 29000.0, "fy": 60.0,
        "rho_over_rho_b": 0.25},
    "em_2104.design.max_moment_at_rho_limit": {
        "b": 12.0, "d": 20.0, "fc_prime": 4.0, "h": 24.0,
        "kd": 0.125765306122449, "pn": 0.0},
    "em_2104.design.minimum_effective_depth": {
        "b": 12.0, "fc_prime": 4.0, "kd": 0.125765306122449, "mn": 147.0},
    "em_2104.flexure_axial.aci_beta1": {"fc_prime": 4.0, "unit": "ksi"},
    "em_2104.flexure_axial.balanced_eccentricity_doubly": {
        "beta1": 0.85, "dprime_over_d": 0.1, "ec": 0.003, "es": 29000.0,
        "fc_prime": 4.0, "fy": 60.0, "kb": 0.503061224489796, "rho": 0.01,
        "rho_prime": 0.01},
    "em_2104.flexure_axial.balanced_eccentricity_singly": {
        "fc_prime": 4.0, "fy": 60.0, "kb": 0.503061224489796, "rho": 0.006423},
    "em_2104.flexure_axial.balanced_strain_kb": {
        "beta1": 0.85, "ec": 0.003, "es": 29000.0, "fy": 60.0},
    "em_2104.flexure_axial.bresler_biaxial_check": {
        "member_shape": "rectangular", "mux": 50.0, "muy": 0.0,
        "phi_m0x": 100.0, "phi_m0y": 80.0},
    "em_2104.flexure_axial.compression_controlled_capacity_doubly": {
        "b": 12.0, "beta1": 0.85, "d": 16.5, "dprime_over_d": 0.35,
        "e_prime_over_d": 0.8, "ec": 0.003, "es": 29000.0, "fc_prime": 4.0,
        "fy": 60.0, "h": 20.0, "kb": None, "phi": 0.65, "rho": 0.01,
        "rho_prime": 0.006},
    "em_2104.flexure_axial.compression_controlled_capacity_singly": {
        "b": 12.0, "beta1": 0.85, "d": 12.0, "e_prime_over_d": 0.05,
        "ec": 0.003, "es": 29000.0, "fc_prime": 4.0, "fy": 40.0, "h": 24.0,
        "kb": None, "phi": 0.65, "rho": 0.01},
    "em_2104.flexure_axial.compression_steel_stress_at_ku": {
        "beta1": 0.85, "dprime_over_d": 0.22737035900583, "ec": 0.003,
        "es": 29000.0, "fy": 60.0, "ku": 0.503061224489796,
        "regime": "tension_controlled"},
    "em_2104.flexure_axial.eccentricity_ratio": {
        "d": 16.295, "h": 20.0, "mu": 2508.0, "pu": 55.0},
    "em_2104.flexure_axial.max_axial_capacity_doubly": {
        "ag": 240, "bd": 195.54000000000002, "fc_prime": 4.0, "fy": 60.0,
        "phi": 0.9, "rho": 0.01738774675258259,
        "rho_prime": 0.009563260713920425},
    "em_2104.flexure_axial.max_axial_capacity_singly": {
        "ag": 288.0, "as_": 2.0, "fc_prime": 4.0, "fy": 60.0, "phi": 1.0},
    "em_2104.flexure_axial.max_axial_tension_capacity": {
        "bd": 720.0, "fy": 60.0, "phi": 0.9, "rho": 0.01, "rho_prime": 0.005},
    "em_2104.flexure_axial.pure_flexure_doubly": {
        "as_": 8.0, "as_prime": 4.0, "b": 12.0, "beta1": None, "d": 60.0,
        "dprime": 6.0, "ec": 0.003, "es": 29000.0, "fc_prime": 4.0, "fy": 60.0,
        "phi": None},
    "em_2104.flexure_axial.pure_flexure_singly": {
        "as_": 1.58, "b": 12.0, "d": 20.5, "fc_prime": 4.0, "fy": 60.0,
        "phi": 0.9},
    "em_2104.flexure_axial.pure_tension_capacity": {
        "as_": 3.0, "as_prime": 2.0, "fy": 60.0, "phi": 0.9},
    "em_2104.flexure_axial.tension_between_layers_capacity": {
        "dprime_over_d": 0.15, "e_prime_over_d": 0.3, "fy": 60.0, "rho": 0.01,
        "rho_prime": 0.008},
    "em_2104.flexure_axial.tension_controlled_by_compression_side_ku": {
        "e_prime_over_d": -0.5, "fc_prime": 4.0, "fy": 60.0, "rho": 0.01},
    "em_2104.flexure_axial.tension_controlled_capacity_doubly": {
        "b": 12.0, "beta1": 0.85, "d": 20.0, "dprime_over_d": 0.1,
        "e_prime_over_d": 1.0641835030158107, "ec": 0.003, "es": 29000.0,
        "fc_prime": 4.0, "fy": 60.0, "h": 24.0, "kb": 0.503061224489796,
        "phi": 0.9, "rho": 0.01, "rho_prime": 0.01},
    "em_2104.flexure_axial.tension_controlled_capacity_singly": {
        "b": 12.0, "d": 20.5, "e_prime_over_d": 0.966159200432168,
        "fc_prime": 4.0, "fy": 60.0, "h": 24.0, "phi": 0.9, "rho": 0.006423},
    "em_2104.flexure_axial.tension_flexure_eccentricity_range": {
        "d": 20.0, "h": 24.0},
    "em_2104.loads.earthquake_load_combination": {
        "companion_terms": None, "eq_load": 40.0, "method": "standard_obe",
        "permanent_sum": 100.0},
    "em_2104.loads.load_combination_lrfd": {
        "companion_terms": [[10.0, 1.0]], "permanent_terms": [[100.0, 1.2]],
        "principal_term": [50.0, 1.5]},
    "em_2104.loads.probability_of_failure_from_beta": {"beta": 0.0},
    "em_2104.loads.required_strength_check": {
        "phi": 0.9, "rn_nominal": 150.0, "u_demand": 100.0},
    "em_2104.loads.table_3_1_load_inventory": {"load_id": "Hs"},
    "em_2104.loads.table_3_2_load_factor": {
        "category": None, "load_id": "Hs", "role": "companion"},
    "em_2104.loads.table_3_2_permanent_load_factor": {
        "effect": "add", "load_id": "D"},
    "em_2104.loads.table_f2_target_reliability": {
        "load_path": "single", "structure_class": "normal"},
    "em_2104.reinforcement.shrinkage_temperature_reinforcement": {
        "gross_thickness_in": 42, "joint_spacing_ft": 45, "unit_width_in": 12},
    "em_2104.reinforcement.table_2_1_min_cover": {
        "aggregate_size_in": None, "bar_diameter_in": None,
        "concrete_section": "unformed_contact_foundation"},
    "em_2104.reinforcement.table_2_2_splice_stagger": {"bar_size": 11},
    "em_2104.reinforcement.table_2_3_temp_shrinkage_ratio": {
        "joint_spacing_ft": 20},
    "em_2104.serviceability.deflection_control_reinforcement_ratio": {
        "rho_b": 0.0285},
    "em_2104.serviceability.max_reinforcement_ratio": {"rho_b": 0.02851},
    "em_2104.serviceability.min_wall_thickness": {
        "height_ft": 5.0, "thickness_in": None},
    "em_2104.serviceability.single_load_factor_design_moment": {
        "action": "flexure_shear", "category": "usual", "m_service": 5.0},
    "em_2104.serviceability.table_3_3_max_service_stress": {
        "action": "flexure_shear", "category": "usual"},
    "em_2104.serviceability.table_3_4_single_load_factor": {
        "action": "flexure_shear", "category": "usual"},
    "em_2104.shear.shear_capacity_curved_member": {
        "ag": 576, "b": 12, "d": 43.5, "fc_prime": 4000, "nu": 162500,
        "radius": None},
    "em_2104.shear.shear_capacity_one_way_slab": {
        "ag": 336, "b": 12, "d": 24, "fc_prime": 4000, "nu": 0.0, "unit": "us"},
    "em_2104.shear.shear_capacity_special_straight_member": {
        "ag": 336, "b": 12, "d": 24, "fc_prime": 4000, "ln": 120, "nu": 31700},
    "em_2104.shear.table_g1_shear_coefficient": {"thickness_in": 12},
    "fhwa_pavements.equations.backcalculated_to_design_modulus": {
        "basis": "nchrp_1_37a", "layer": "subgrade",
        "mr_backcalculated_psi": 20000},
    "fhwa_pavements.equations.cbr_from_dcp": {"dcp_mm_per_blow": 10},
    "fhwa_pavements.equations.cbr_from_plasticity_gradation": {
        "p200": 0.8, "pi": 20},
    "fhwa_pavements.equations.effective_subgrade_modulus_from_relative_damage": {
        "uf_avg": 0.1207},
    "fhwa_pavements.equations.granular_resilient_modulus_bulk_stress": {
        "k1": 6000, "k2": 0.5, "theta_psi": 30},
    "fhwa_pavements.equations.resilient_modulus_from_cbr": {
        "cbr": 10, "units": "psi"},
    "fhwa_pavements.equations.resilient_modulus_from_cbr_aashto93": {"cbr": 8},
    "fhwa_pavements.equations.resilient_modulus_from_dcp": {
        "dcp_mm_per_blow": 10, "units": "psi"},
    "fhwa_pavements.equations.resilient_modulus_from_r_value": {
        "r_value": 60, "units": "psi"},
    "fhwa_pavements.equations.seasonal_relative_damage": {"mr_psi": 10000},
    "fhwa_pavements.tables.table_4_14_soil_as_pavement_material": {
        "soil_class": ""},
    "fhwa_pavements.tables.table_5_18_compaction_aashto": {"soil_class": ""},
    "fhwa_pavements.tables.table_5_24_swell_potential_holtz_gibbs": {
        "potential": "very high"},
    "fhwa_pavements.tables.table_5_28_typical_cbr": {"soil_class": ""},
    "fhwa_pavements.tables.table_5_34_resilient_modulus_correlations": {
        "property": ""},
    "fhwa_pavements.tables.table_5_35_default_resilient_modulus": {
        "classification": "", "soil_class": ""},
    "fhwa_pavements.tables.table_5_49_drainage_modifier_mi": {"quality": ""},
    "fhwa_pavements.tables.table_5_50_drainage_coefficient_cd": {
        "quality": "very poor"},
    "fhwa_pavements.tables.table_5_56_permeability_soils": {
        "soil_description": ""},
    "fhwa_pavements.tables.table_5_57_permeability_highway_materials": {
        "material": ""},
    "fhwa_pavements.tables.table_7_12_frost_susceptibility": {
        "frost_group": ""},
    "fhwa_pavements.tables.table_7_15_geosynthetic_stabilization_criteria": {},
    "fhwa_pavements.tables.table_7_17_swell_potential_ll_pi": {
        "potential": ""},
    "fhwa_pavements.tables.table_7_4_drainage_quality_definitions": {},
    "ufc_backfill.equations.relative_compaction_check": {
        "dry_density_kN_per_m3": 18.0, "max_dry_density_kN_per_m3": 19.0,
        "required_pct": 95.0},
    "ufc_backfill.tables.figure_2_5_compaction_induced_lateral_pressure": {
        "equipment": "10-ton smooth wheel roller"},
    "ufc_backfill.tables.table_5_1_compaction_criteria": {
        "compaction": "compacted", "soil_group": "CL"},
    "ufc_backfill.tables.table_backfill_material_classification": {
        "uscs_class": "GW"},
    "ufc_backfill.tables.table_compaction_equipment_selection": {
        "soil_type": "gravels", "zone": "open"},
    "ufc_backfill.tables.table_compaction_requirements": {
        "application": "open_area"},
    "ufc_backfill.tables.table_maximum_lift_thickness": {
        "case": "cohesionless_heavy_vibratory"},
    "ufc_concrete_practice.equations.coarseness_factor": {
        "pct_retained_2_36mm": 60, "pct_retained_9_5mm": 40},
    "ufc_concrete_practice.equations.workability_factor": {
        "cementitious_content_kg_m3": 335, "pct_passing_2_36mm": 35},
    "ufc_concrete_practice.tables.dowel_bar_alignment_tolerance": {},
    "ufc_concrete_practice.tables.dowel_bar_corner_clearance": {},
    "ufc_concrete_practice.tables.dowel_bar_drilled_hole_oversize": {},
    "ufc_concrete_practice.tables.edge_slump_tolerance": {},
    "ufc_concrete_practice.tables.table_3_1_weather_severity": {
        "air_freezing_index": 400, "avg_monthly_precip_in": 5.0},
    "ufc_concrete_practice.tables.table_3_2_deleterious_material_limit": {
        "aggregate_category": "fine", "material": "shale"},
    "ufc_concrete_practice.tables.table_3_3_aggregate_test_time": {
        "test_method": "astm_c1260"},
    "ufc_concrete_practice.tables.table_3_4_portland_cement_type": {
        "cement_type": "type_i"},
    "ufc_concrete_practice.tables.table_3_5_blended_cement_type": {
        "cement_type": "type_is"},
    "ufc_concrete_practice.tables.table_3_6_hydraulic_cement_type": {
        "cement_type": "type_hs"},
    "ufc_concrete_practice.tables.table_3_7_ggbf_slag_grade": {
        "grade": "grade_120"},
    "ufc_concrete_practice.tables.table_3_8_admixture_type": {
        "admixture_type": "type_g"},
    "ufc_concrete_practice.tables.table_8_1_dowel_misalignment_impact": {
        "misalignment_type": "horizontal_translation"},
    "ufc_concrete_practice.tables.table_9_1_maximum_joint_spacing": {
        "facility_type": "airfield", "slab_thickness_in": 8},
    "ufc_concrete_practice.tables.table_d1_cracking_causes": {
        "crack_type": "plastic_shrinkage"},
    "ufc_concrete_practice.tables.table_e1_rcc_gradation": {"sieve_mm": 4.75},
    "ufc_expansive.equations.eq_4_1_van_der_merwe_heave": {
        "layers": [{"clay_fraction_pct": 30, "plasticity_index": 40, "thickness_ft": 10}]},
    "ufc_expansive.equations.eq_5_2_potential_vertical_heave": {
        "depth_increment_ft": 1.0,
        "elements": [{"final_void_ratio": 0.9, "initial_void_ratio": 0.8}],
        "vertical_swell_fraction": 1.0},
    "ufc_expansive.equations.eq_5_3_to_5_5_equilibrium_pore_water_pressure": {
        "active_zone_depth_ft": 8, "depth_ft": 8,
        "pore_water_pressure_at_xa_tsf": -7.5, "profile": "method_3"},
    "ufc_expansive.equations.eq_5_8_consolidometer_heave": {
        "layers": [{"initial_void_ratio": 1.0, "swell_index": 0.1, "swell_pressure_tsf": 4, "thickness_ft": 1, "total_vertical_pressure_tsf": 0.4}]},
    "ufc_expansive.equations.heave_prediction_mm": {
        "layers": [{"swell_strain_pct": 1.4, "thickness_m": 2.19456}]},
    "ufc_expansive.equations.table_4_2_swell_johnson": {
        "depth_ft": 5, "initial_water_content": 25, "plasticity_index": 50},
    "ufc_expansive.equations.table_4_2_swell_mckeen_lytton": {
        "final_suction": 1.0, "initial_suction": 10.0,
        "suction_compression_index": 0.1},
    "ufc_expansive.equations.table_4_2_swell_schneider_poor": {
        "initial_water_content": 20, "plasticity_index": 30},
    "ufc_expansive.equations.table_4_2_swell_vijayvergiya_ghazzaly": {
        "initial_water_content": 20, "liquid_limit": 60},
    "ufc_expansive.tables.figure_4_1_potential_expansiveness": {
        "clay_fraction_pct": 10, "plasticity_index": 50},
    "ufc_expansive.tables.table_active_zone_depth": {
        "depth_to_groundwater_ft": None, "natural_soil_suction_tsf": None,
        "profile": "moist", "shaft_base_diameter_ft": None},
    "ufc_expansive.tables.table_foundation_selection": {
        "effective_plasticity_index": None,
        "predicted_differential_movement_in": 0.5},
    "ufc_expansive.tables.table_grade_beam_void_space": {
        "predicted_total_heave_in": 2.0},
    "ufc_expansive.tables.table_swell_potential_classification": {
        "liquid_limit": None, "natural_soil_suction_tsf": None,
        "plasticity_index": 5},
    "ufc_flexible_practice.equations.air_voids_vtm": {
        "gmb": 2.421, "gmm": 2.519},
    "ufc_flexible_practice.equations.bulk_specific_gravity_gmb": {
        "wt_dry_air": 1237.9, "wt_ssd": 1240.2, "wt_submerged": 510.9},
    "ufc_flexible_practice.equations.bulk_specific_gravity_gmb_geometric": {
        "diameter": 15.24, "height": 6.35, "wt_dry_air": 2500},
    "ufc_flexible_practice.equations.fuller_thompson_max_density_passing": {
        "max_particle_size_mm": 19.0, "n": 0.45, "sieve_size_mm": 19.0},
    "ufc_flexible_practice.equations.rmp_optimum_asphalt_content": {
        "apparent_sg_combined_aggregate": 2.65, "sigma": 1716.3},
    "ufc_flexible_practice.equations.rmp_specific_surface_area": {
        "pct_passing_no200": 10, "pct_passing_no30_retained_no200": 20,
        "pct_passing_no4_retained_no30": 40, "pct_retained_no4": 30},
    "ufc_flexible_practice.equations.slurry_seal_asphalt_for_film_thickness": {
        "csa_m2_per_kg": 8.31, "film_thickness_um": 8, "sg_asphalt": 1.028},
    "ufc_flexible_practice.equations.slurry_seal_corrected_surface_area": {
        "apparent_sg_aggregate": 2.96, "surface_area_m2_per_kg": 9.215},
    "ufc_flexible_practice.equations.slurry_seal_surface_area": {
        "pct_passing_by_sieve_mm": {"0.075": 6.4, "0.15": 10.7, "0.3": 24.5, "0.6": 52.0, "1.18": 77.8, "2.36": 95.6, "4.75": 99.5, "9.5": 100}},
    "ufc_flexible_practice.equations.slurry_seal_total_asphalt_required": {
        "ka_pct": 5.7, "saa_pct": 6.83},
    "ufc_flexible_practice.equations.voids_filled_with_asphalt_vfa": {
        "vma_percent": 14.8, "vv_percent": 3.9},
    "ufc_flexible_practice.equations.voids_in_mineral_aggregate_vma": {
        "gmb": 2.421, "gsb": 2.7, "pb": 0.05},
    "ufc_flexible_practice.tables.spray_application_rate": {
        "application_type": "prime_coat"},
    "ufc_flexible_practice.tables.table_2_12_pfc_gradation": {
        "gradation": "gradation_a", "sieve_mm": 4.75},
    "ufc_flexible_practice.tables.table_2_15_sma_gradation": {"sieve_mm": 9.5},
    "ufc_flexible_practice.tables.table_2_17_sma_mix_design_requirements": {
        "parameter": None},
    "ufc_flexible_practice.tables.table_2_1_gradation_hma": {
        "gradation": "gradation_1", "sieve_mm": 4.75},
    "ufc_flexible_practice.tables.table_2_3_asphalt_grade_by_pti": {
        "pti_c": 10.0},
    "ufc_flexible_practice.tables.table_2_5_asphalt_grade_by_freezing_index": {
        "dfi_c": 1000},
    "ufc_flexible_practice.tables.table_2_7_minimum_vma": {
        "gradation": "gradation_1"},
    "ufc_flexible_practice.tables.table_2_8_marshall_design_criteria": {
        "compaction": "50_blows", "mix_type": "hma", "property": None},
    "ufc_flexible_practice.tables.table_3_2_tack_coat_temperature": {
        "grade": "rc_70", "material_type": "cutback"},
    "ufc_flexible_practice.tables.table_4_2_gradation_sbst": {
        "designation": "no_1", "sieve_mm": 19.0},
    "ufc_flexible_practice.tables.table_4_3_gradation_dbst": {
        "designation": "no_1", "sieve_mm": 4.75},
    "ufc_flexible_practice.tables.table_4_4_slurry_seal_gradation": {
        "sieve_mm": 9.5, "type_": "type_2"},
    "ufc_flexible_practice.tables.table_4_5_frs_application_rate": {
        "gradation": "medium", "sieve_mm": 0.6},
    "ufc_flexible_practice.tables.table_4_7_micro_surfacing_gradation": {
        "sieve_mm": 4.75, "type_": "type_2"},
    "ufc_flexible_practice.tables.table_6_1_cold_mix_gradation": {
        "column": 1, "mix_type": "dense_graded", "sieve_mm": 9.5},
    "ufc_flexible_practice.tables.table_6_2_cold_mix_asphalt_selection": {
        "climate": "hot"},
    "ufc_flexible_practice.tables.table_6_3_cold_mix_optimum_ac_selection": {
        "property_": None},
    "ufc_flexible_practice.tables.table_6_4_mixing_temperature": {
        "grade": "ms_2", "material_type": "emulsified"},
    "ufc_flexible_practice.tables.table_7_2_ogam_gradation": {
        "sieve_mm": 19.0},
    "ufc_flexible_practice.tables.table_7_3_slurry_grout_gradation": {
        "sieve_mm": 1.18},
    "ufc_flexible_practice.tables.table_7_4_grout_mix_proportions": {
        "material": None},
    "ufc_flexible_practice.tables.table_7_5_grout_viscosity": {
        "time_elapsed": "0_30_min"},
    "ufc_flexible_practice.tables.table_b1_surface_area_factor": {
        "sieve_mm": 4.75},
    "ufc_pavement.equations.collector_drain_flow": {
        "h": 0.33, "i": 0.02, "k": 1000, "units": "ft_day"},
    "ufc_pavement.equations.darcy_flow_rate": {
        "area": 10, "i": 0.02, "k": 0.5},
    "ufc_pavement.equations.drainage_layer_drainable_flow": {
        "h": 4, "i": 0.02, "k": 1000, "length": 50, "t": 2},
    "ufc_pavement.equations.drainage_layer_storage_capacity": {
        "h": 4, "ne": 0.25},
    "ufc_pavement.equations.drainage_layer_thickness_required": {
        "f": 0.5, "i": 0.02, "k": 1000, "length": 50, "ne": 0.25, "r": 0.2,
        "t": 1},
    "ufc_pavement.equations.drainage_layer_thickness_simplified": {
        "f": 0.5, "ne": 0.25, "r": 0.2, "t": 1},
    "ufc_pavement.equations.drainage_path_length": {
        "ie": 0.01, "it": 0.02, "lt": 24},
    "ufc_pavement.equations.drainage_path_slope": {"ie": 0.01, "it": 0.02},
    "ufc_pavement.equations.effective_horizontal_permeability": {
        "layers": [[100, 4], [10, 8]]},
    "ufc_pavement.equations.effective_porosity": {
        "dry_density": 110, "gs": 2.68, "water_unit_weight": 62.4, "we": 0.05},
    "ufc_pavement.equations.flexible_overlay_of_rigid_thickness": {
        "c": 1.0, "f": 0.93, "hE_in": 6, "hd_in": 8.1},
    "ufc_pavement.equations.free_draining_layer_required": {
        "bound_layer_thickness_in": 50.0, "design_freezing_index": 1000},
    "ufc_pavement.equations.granular_permeability_estimate": {
        "d10_mm": 0.5, "n": 0.35, "p200_pct": 5, "units": "mm_per_sec"},
    "ufc_pavement.equations.insulation_initial_temperature_differential": {
        "mean_annual_soil_temp_f": 40},
    "ufc_pavement.equations.insulation_mean_soil_temperature_estimate": {
        "mean_annual_air_temp_f": 33},
    "ufc_pavement.equations.mixed_traffic_equivalent_esal": {
        "vehicles": [
            {"name": "18kip_esal", "design_passes": 1000000,
             "required_thickness_in": 16.4},
            {"name": "5axle_truck", "design_passes": 100000,
             "required_thickness_in": 15.8,
             "allowable_passes_at_controlling": 252915}]},
    "ufc_pavement.equations.pipe_capacity_manning": {
        "d_ft": 0.5, "n": 0.013, "s": 0.0015, "units": "us"},
    "ufc_pavement.equations.plain_concrete_thickness_on_stabilized_foundation": {
        "ef_psi": 650000, "hd_in": 8.3, "hs_in": 6},
    "ufc_pavement.equations.reinforced_pavement_max_slab_length": {
        "fs_psi": 60000, "hr_in": 7, "s_pct": 0.1},
    "ufc_pavement.equations.rigid_overlay_fully_bonded": {
        "hd_in": 8.1, "he_in": 6},
    "ufc_pavement.equations.rigid_overlay_non_bonded": {
        "c": 1.0, "hE_in": 6, "hd_in": 8.1, "he_in": 8.1},
    "ufc_pavement.equations.rigid_overlay_partially_bonded": {
        "c": 1.0, "hE_in": 6, "hd_in": 8.1, "he_in": 8.1},
    "ufc_pavement.equations.stabilized_layer_thickness_in": {
        "conventional_thickness_in": 4.0, "equivalency_factor": 1.15},
    "ufc_pavement.equations.taylor_permeability": {
        "c": 25, "ds_mm": 0.5, "e": 0.6, "gamma": 62.4, "mu": 1.0},
    "ufc_pavement.equations.time_for_50pct_drainage": {
        "d": 50, "i": 0.02, "k": 1000, "ne": 0.25},
    "ufc_pavement.equations.time_for_85pct_drainage": {
        "d": 50, "i": 0.02, "k": 1000, "ne": 0.25},
    "ufc_pavement.tables.figure_10_1_k_on_base": {
        "base_thickness_in": 2.7, "k_subgrade_psi_in": 25},
    "ufc_pavement.tables.figure_14_1_reinforced_pavement_design": {
        "fs_psi": 60000, "hd_in": 7.9, "s_pct": 0.1},
    "ufc_pavement.tables.figure_15_1_cracking_projection_factor": {
        "k_existing_psi_in": 25, "passes": 100},
    "ufc_pavement.tables.figure_19_5_design_base_thickness": {
        "c_in": 32, "r": 2.0},
    "ufc_pavement.tables.figure_19_6_frost_area_index_of_reaction": {
        "base_thickness_in": 8, "frost_group": "F3_F4"},
    "ufc_pavement.tables.figure_e1_flexible_thickness": {
        "cbr": 3, "passes": 1000000},
    "ufc_pavement.tables.figure_e_vehicle_allowable_passes": {
        "cbr": 3, "max_iter": 60, "thickness_in": 16.4, "tol": 1e-06,
        "vehicle": "truck_5_axle"},
    "ufc_pavement.tables.figure_e_vehicle_thickness": {
        "cbr": 3, "passes": 100000, "vehicle": "truck_5_axle"},
    "ufc_pavement.tables.figure_f1_rigid_thickness": {
        "flexural_psi": 650, "k_psi_in": 800, "passes": 5000000},
    "ufc_pavement.tables.table_10_1_k_subgrade": {
        "moisture_pct": 10, "uscs_group": "CL"},
    "ufc_pavement.tables.table_15_condition_factor": {
        "c": 1.0, "existing_pavement_type": "plain", "overlay_type": "rigid"},
    "ufc_pavement.tables.table_16_1_joint_spacing": {"thickness_in": 6},
    "ufc_pavement.tables.table_16_2_dowel_size": {"thickness_in": 6},
    "ufc_pavement.tables.table_19_1_distress_modes": {
        "distress_mode": "cracking"},
    "ufc_pavement.tables.table_19_2_frost_classification": {
        "finer_than_0_02mm_pct": 1.0, "frost_group": None, "uscs_class": "GW"},
    "ufc_pavement.tables.table_19_3_frost_support_index": {
        "frost_group": "F1"},
    "ufc_pavement.tables.table_20_1_permeability_estimate": {
        "pct_passing_no200": 10},
    "ufc_pavement.tables.table_20_2_frost_susceptible_soils": {
        "frost_group": "F1"},
    "ufc_pavement.tables.table_20_8_pipe_roughness": {
        "pipe_type": "clay_concrete_smooth_plastic_asbestos_cement"},
    "ufc_pavement.tables.table_21_1_aggregate_gradation": {"gradation_no": 1},
    "ufc_pavement.tables.table_21_2_aggregate_compaction_depth": {
        "density_pct": 95, "passes": 1000000, "soil_type": "cohesionless"},
    "ufc_pavement.tables.table_4_1_subgrade_category": {"cbr": 20.0},
    "ufc_pavement.tables.table_5_1_compaction_depth": {
        "density_pct": 95, "passes": 1000000, "pavement_type": "flexible",
        "soil_type": "cohesive"},
    "ufc_pavement.tables.table_6_1_subbase_permissible_values": {
        "design_cbr": 50},
    "ufc_pavement.tables.table_7_1_base_design_cbr": {
        "material_type": "graded_crushed_aggregate"},
    "ufc_pavement.tables.table_7_2_min_thickness": {
        "base_cbr": 100, "esal": 10000},
    "ufc_pavement.tables.table_9_1_equivalency_factor": {
        "layer_type": "base", "stabilizer_type": "asphalt", "uscs_class": "gm"},
    "ufc_stabilization.equations.equation_cement_content_modifying_soils": {
        "percent_cement_for_pi": 0.08, "percent_passing_no40": 0.6},
    "ufc_stabilization.equations.equation_cement_pi_limit_table_2_3": {
        "percent_passing_no200": 25},
    "ufc_stabilization.equations.equation_cutback_asphalt_content_estimate": {
        "percent_no100_to_no200": 30, "percent_no50_to_no100": 20,
        "percent_passing_no200": 40, "percent_retained_no50": 10,
        "percent_solvent": 0},
    "ufc_stabilization.equations.equation_gravimetric_percent_so4": {
        "oven_dry_weight_g": 10, "weight_of_residue_g": 0.1},
    "ufc_stabilization.equations.equation_oven_dry_weight_from_air_dry": {
        "air_dry_moisture_content_pct": 9.36, "air_dry_weight_g": 10.12},
    "ufc_stabilization.equations.equation_stabilized_equivalent_thickness": {
        "conventional_thickness_in": 4, "equivalency_factor": 1.15},
    "ufc_stabilization.equations.equation_turbidimetric_percent_so4": {
        "concentration_ppm": 80.0, "dry_weight_g": 9.27,
        "total_volume_ml": 39.1},
    "ufc_stabilization.tables.table_2_1_min_ucs_requirements": {
        "layer": "base", "pavement_type": "flexible"},
    "ufc_stabilization.tables.table_2_2_durability_requirements": {
        "soil_type": "granular_pi_lt_10"},
    "ufc_stabilization.tables.table_2_3_additive_selection_guide": {
        "area": "1c"},
    "ufc_stabilization.tables.table_3_1_cement_gradation": {
        "course_type": "base", "sieve": ""},
    "ufc_stabilization.tables.table_3_2_cement_content_by_soil": {
        "uscs_class": "GW"},
    "ufc_stabilization.tables.table_3_3_bituminous_subgrade_gradation": {
        "sieve": ""},
    "ufc_stabilization.tables.table_3_4_bituminous_base_subbase_gradation": {
        "max_size": "0.75in", "sieve": ""},
    "ufc_stabilization.tables.table_3_5_emulsified_asphalt_requirements": {
        "percent_passing_200": 0, "percent_passing_no10": 100},
    "ufc_stabilization.tables.table_3_6_swell_potential": {
        "liquid_limit": 65, "plasticity_index": 40},
    "ufc_stabilization.tables.table_a1_equivalency_factors": {
        "soil_class": "gp", "stabilizer_type": "cement"},
}


def test_every_lookup_has_one_call():
    assert set(LOOKUPS) == set(CALLS) | BY_HAND


def test_every_lookup_is_labelled():
    assert [n for n, f in LOOKUPS.items()
            if not hasattr(f, "__result_units__")] == []


@pytest.mark.parametrize("name", sorted(CALLS))
def test_result_follows_the_convention(name):
    func = LOOKUPS[name]
    result = func(**CALLS[name])
    if isinstance(result, dict):
        assert rc.dict_result_problems(result) == []
    else:
        assert rc.bare_docstring_problems(func) == []


def test_performance_period_iteration_follows_the_convention():
    func = LOOKUPS["aashto_1993.environmental.performance_period_iteration"]
    result = func(1.9, lambda dpsi: 1.0e6 * dpsi, lambda w18: w18 / 2.0e5,
                  initial_trial_yr=10.0, max_performance_period_yr=20.0,
                  swelling={"vr_in": 2.0, "ps_pct": 60, "theta": 0.1})
    assert rc.dict_result_problems(result) == []
    assert func.needs_python_callables is True


@pytest.mark.parametrize("name", sorted(
    n for n, f in LOOKUPS.items() if "unit_system" in rc.signature_names(f)))
def test_unit_system_is_documented(name):
    doc = inspect.getdoc(LOOKUPS[name])
    assert re.search(r"^unit_system : str, optional$", doc, re.M)
    assert "With unit_system='SI' the" in " ".join(doc.split())
