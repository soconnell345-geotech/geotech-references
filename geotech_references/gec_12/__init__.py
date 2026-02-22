"""GEC-12: Design and Construction of Driven Pile Foundations (FHWA-NHI-16-009).

Provides:
  - Structured reference text (JSON) for all 8 chapters
  - Figure lookup functions (Nordlund Kd, CF, alpha_t, N'q, adhesion)
  - Table lookup functions (resistance factors, beta/Nt, setup factors, API params)
  - Text retrieval via geotech_references._retrieval module

Usage::

    from geotech_references.gec_12.figures import figure_7_10_to_13_kd
    from geotech_references.gec_12.tables import table_7_1_resistance_factor_static
    from geotech_references._retrieval import retrieve_section, search_sections
"""
