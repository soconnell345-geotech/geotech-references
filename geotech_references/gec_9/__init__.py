"""GEC-9: Design, Analysis, and Testing of Laterally Loaded Deep Foundations.

FHWA-HIF-18-031, April 2018.

Provides:
  - Structured reference text (JSON) for all 13 chapters
  - Table lookup functions (tables.py): LRFD resistance factors (Table 4-1),
    p-multipliers for group analysis (Table 7-1), p-y parameters for stiff
    clay (Tables A-1 and A-2), and p-y initial modulus for sand (Table A-3)
  - Text retrieval via geotech_references._retrieval module

Note: Core lateral pile computation (p-y method, COM624P) is implemented in
GeotechStaffEngineer's lateral_pile module.  This GEC-9 reference module
provides LRFD design guidance text, group p-multipliers, and p-y curve
parameter tables.
"""
