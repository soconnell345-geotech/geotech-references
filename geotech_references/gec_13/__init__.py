"""GEC-13: Ground Modification Methods — Reference Manual.

FHWA-NHI-16-027 (Volume I) and FHWA-NHI-16-028 (Volume II), April 2017
(FHWA GEC 013).

Volume I covers:
  Chapter 1 — Introduction to Ground Modification Technologies
  Chapter 2 — Vertical Drains and Accelerated Consolidation
  Chapter 3 — Lightweight Fills
  Chapter 4 — Deep Compaction
  Chapter 5 — Aggregate Columns

Volume II (FHWA-NHI-16-028) covers:
  Chapter 6 — Column-Supported Embankments
  Chapter 7 — Deep Mixing and Mass Mixing
  Chapter 8 — Grouting
  Chapter 9 — Pavement Support Stabilization Technologies
  Chapter 10 — Reinforced Soil Structures

Provides:
  - Structured reference text (JSON) for all 10 chapters (Vols I and II)
  - Table lookup functions (technology applicability, classification by
    function, comparative unit costs, PVD applications)
  - Text retrieval via geotech_references._retrieval module

Note: Core ground improvement analysis (aggregate piers, wick drains,
surcharge, vibro-compaction, feasibility) is implemented in
GeotechStaffEngineer's ground_improvement module. This GEC-13 reference
module provides complementary design guidance text, technology selection
tables, and cost estimation data.
"""
