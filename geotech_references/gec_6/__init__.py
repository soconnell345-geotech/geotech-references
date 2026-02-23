"""GEC-6: Shallow Foundations (FHWA-SA-02-054).

Provides:
  - Structured reference text (JSON) for all 10 chapters
  - Table lookup functions (bearing capacity factors, rock properties, friction)
  - Figure lookup functions (Hough bearing capacity index)
  - Text retrieval via geotech_references._retrieval module

Usage::

    from geotech_references.gec_6.tables import table_5_1_bearing_capacity_factors
    from geotech_references.gec_6.figures import figure_5_19_hough_bearing_capacity_index
    from geotech_references._retrieval import retrieve_section, search_sections
"""
