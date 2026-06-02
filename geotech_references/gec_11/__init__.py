"""GEC-11: Design and Construction of Mechanically Stabilized Earth Walls
and Reinforced Soil Slopes.

FHWA-NHI-10-024 (Volume I) and FHWA-NHI-10-025 (Volume II), November 2009.

Volume I (FHWA-NHI-10-024) covers:
  Chapter 1 — Introduction
  Chapter 2 — Systems and Project Evaluation
  Chapter 3 — Soil Reinforcement Principles and System Design Properties
  Chapter 4 — Design of MSE Walls (LRFD)
  Chapter 5 — MSE Wall Design Details
  Chapter 6 — Design of MSE Walls with Complex Geometrics
  Chapter 7 — Design of MSE Walls for Extreme Events

Volume II (FHWA-NHI-10-025) covers:
  Chapter 8  — Reinforced Soil Slopes Project Evaluation
  Chapter 9  — Design of Reinforced Soil Slopes
  Chapter 10 — Contracting Methods and Specifications for MSE Walls and Slopes
  Chapter 11 — Field Inspection and Performance Monitoring

Provides:
  - Structured reference text (JSON) for all 11 chapters (Vol I + Vol II)
  - Table lookup functions (LRFD factors, corrosion rates, durability,
    installation damage, backfill specs, bearing capacity factors)
  - Figure lookup functions (Kr/Ka ratio vs depth)
  - Text retrieval via geotech_references._retrieval module

Note: Core MSE wall analysis (sliding, overturning, bearing, internal
stability) is implemented in GeotechStaffEngineer's retaining_walls
module. This GEC-11 reference module provides complementary LRFD design
guidance, material property tables, and resistance factor data.
"""
