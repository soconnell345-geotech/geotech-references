"""GEC-10: Drilled Shafts — Construction Procedures and LRFD Design Methods.

FHWA-NHI-10-016, May 2010 (FHWA GEC 010).

Provides:
  - Structured reference text (JSON) for key chapters (1-23)
  - Table lookup functions (LRFD resistance factors, group efficiency,
    p-multipliers, lateral resistance factors, reliability index)
  - Figure lookup functions (alpha for clay, beta for sand, Nc* base,
    rock socket side resistance)
  - Text retrieval via geotech_references._retrieval module

Note: Core drilled shaft analysis (alpha, beta, rock socket, end bearing) is
implemented in GeotechStaffEngineer's drilled_shaft module. This GEC-10 reference
module provides complementary design guidance text, lookup tables, and charts.
"""
