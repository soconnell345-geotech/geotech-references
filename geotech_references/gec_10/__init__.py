"""GEC-10: Drilled Shafts — Construction Procedures and LRFD Design Methods.

FHWA-NHI-18-024, September 2018 (2nd edition; supersedes FHWA-NHI-10-016).

Provides:
  - Structured reference text (JSON) for all 18 chapters
  - Figure/equation functions (figures.py): alpha method (Fig 10-6), su conversion
    (Eq 10-16/17), rock socket side resistance (Eq 10-21/22), Table 10-3 αE factors
  - Table lookup functions (tables.py): resistance factors (Table 8-4), lateral
    resistance factors (Table 9-1), N*c for base in clay (Table 10-2),
    p-multipliers (Table 11-1), group efficiency for cohesionless soils (AASHTO
    10.8.3.6.3), and LRFD reliability index
  - Text retrieval via geotech_references._retrieval module

Note: Core drilled shaft analysis (alpha, beta, rock socket, end bearing) is
implemented in GeotechStaffEngineer's drilled_shaft module.  This GEC-10 reference
module provides complementary design guidance text, lookup tables, and charts.
"""
