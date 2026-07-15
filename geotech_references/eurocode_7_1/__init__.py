"""Eurocode 7: Geotechnical Design - Part 1: General Rules (EN 1997-1:2004).

Provides:
  - Table lookup functions (Annex A partial/correlation factors for ULS design;
    Annex G presumed bearing resistance rock grouping; Annex H limiting
    foundation-movement values)
  - Equation functions (Annex D sample analytical bearing resistance; Annex C
    sample earth-pressure formulas, the legible subset; Annex E semi-empirical
    pressuremeter bearing resistance; Annex F.2 adjusted-elasticity settlement)
  - Text retrieval via geotech_references._retrieval module

Usage::

    from geotech_references.eurocode_7_1.tables import table_a_3_str_geo_actions
    from geotech_references.eurocode_7_1.tables import design_approach_sets
    from geotech_references.eurocode_7_1.equations import drained_bearing_resistance
    from geotech_references._retrieval import retrieve_section, search_sections
"""
