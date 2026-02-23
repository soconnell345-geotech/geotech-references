"""GEC-11: Design and Construction of Mechanically Stabilized Earth Walls
and Reinforced Soil Slopes.

FHWA-NHI-10-024 (Volume I) and FHWA-NHI-10-025 (Volume II), November 2009.

Volume I covers:
  Chapter 1 — Introduction
  Chapter 2 — Systems and Project Evaluation
  Chapter 3 — Soil Reinforcement Principles and System Design Properties
  Chapter 4 — Design of MSE Walls (LRFD)
  Chapter 5 — Design of MSE Walls with Complex Geometrics
  Chapter 6 — Reinforced Soil Slopes (RSS)
  Chapter 7 — Field Inspection and Monitoring

Provides:
  - Structured reference text (JSON) for key chapters (1-7, Vol I)
  - Table lookup functions (LRFD factors, corrosion rates, durability,
    installation damage, backfill specs, bearing capacity factors)
  - Figure lookup functions (Kr/Ka ratio vs depth)
  - Text retrieval via geotech_references._retrieval module

Note: Core MSE wall analysis (sliding, overturning, bearing, internal
stability) is implemented in GeotechStaffEngineer's retaining_walls
module. This GEC-11 reference module provides complementary LRFD design
guidance, material property tables, and resistance factor data.
"""
