"""FEMA P-2192: Seismic Design Category Determination (2024 Edition).

Provides:
  - SDC determination from SDS, SD1, and risk category (ASCE 7-22 Tables 11.6-1/11.6-2)
  - ASCE 7-22 expanded 9-class site classification (A, B, BC, C, CD, D, DE, E, F)
  - ASCE 7-16 legacy 5-class site classification (A, B, C, D, E, F)
  - Site coefficients Fa and Fv (ASCE 7-22 Table 11.4-1/11.4-2)
  - Design spectral parameters SDS and SD1
  - Risk category from building occupancy

Usage::

    from geotech_references.fema_p2192.tables import determine_sdc
    from geotech_references.fema_p2192.tables import table_20_3_1_site_class_from_vs30
"""
