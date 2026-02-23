"""GEC-7: Soil Nail Walls (FHWA-NHI-14-007).

Provides:
  - Structured reference text (JSON) for all 10 chapters
  - Table lookup functions (bond strength, pullout, resistance factors, seismic)
  - Figure lookup functions (friction angle vs SPT, basal heave Nc)
  - Text retrieval via geotech_references._retrieval module

Usage::

    from geotech_references.gec_7.tables import table_4_4a_bond_strength_coarse
    from geotech_references.gec_7.figures import figure_4_3_friction_angle_spt
    from geotech_references._retrieval import retrieve_section, search_sections
"""
