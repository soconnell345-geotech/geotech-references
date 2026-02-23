"""GEC-13: Ground Modification Methods — Reference Manual.

FHWA-NHI-16-027, April 2017 (FHWA GEC 013).

Volume I covers:
  Chapter 1 — Introduction to Ground Modification Technologies
  Chapter 2 — Vertical Drains and Accelerated Consolidation
  Chapter 3 — Lightweight Fills
  Chapter 4 — Deep Compaction
  Chapter 5 — Aggregate Columns

Provides:
  - Structured reference text (JSON) for key chapters (1-5, Vol I)
  - Table lookup functions (technology applicability, classification by
    function, comparative unit costs, PVD applications)
  - Text retrieval via geotech_references._retrieval module

Note: Core ground improvement analysis (aggregate piers, wick drains,
surcharge, vibro-compaction, feasibility) is implemented in
GeotechStaffEngineer's ground_improvement module. This GEC-13 reference
module provides complementary design guidance text, technology selection
tables, and cost estimation data.
"""
