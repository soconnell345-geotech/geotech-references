"""UFC 3-250-04, Standard Practice for Concrete Pavements (29 Jan 2024).

A DoD construction-practice manual for rigid (portland cement concrete)
pavements -- procedural and QC narrative covering pre-construction
activities, subgrade/base/subbase preparation, concrete mixture design,
placement/finishing/texturing/curing, joint sawing and sealing, CQC
implementation, early distress repair, and appendices (preconstruction and
inspection/testing checklists, joint sawing checklist, early-age-cracking
decision tree, roller-compacted concrete pavements, glossary, references).
This is the CONSTRUCTION companion to the design UFCs (UFC 3-250-01 for
roads/parking, UFC 3-260-02 for airfields) -- it does not contain pavement
thickness design procedures or a dowel-bar diameter/spacing sizing table
(that content lives in the design UFCs).

Provides:
  - Table lookup functions (weather severity, aggregate deleterious
    material limits, aggregate/ASR test lead times, portland/blended/
    hydraulic cement types, GGBF slag grades, chemical admixture types,
    dowel bar misalignment impact and installation tolerances, maximum
    joint spacing, edge slump tolerance, early-age cracking causes, RCC
    combined aggregate gradation) -- see ``tables.py``.
  - The one genuine printed formula in the document (combined-aggregate
    coarseness factor / workability factor, Equation 7-1) -- see
    ``equations.py``.
  - A figure catalog (9 figures) for vision read-off via
    ``geotech_references._figures_db``.
  - Structured reference text (all 11 chapters + 7 appendices, A-G) via
    ``geotech_references._retrieval``.

Usage::

    from geotech_references.ufc_concrete_practice.tables import (
        table_8_1_dowel_misalignment_impact,
        dowel_bar_alignment_tolerance,
        table_9_1_maximum_joint_spacing,
    )
    from geotech_references.ufc_concrete_practice.equations import (
        coarseness_factor, workability_factor,
    )
    from geotech_references._retrieval import retrieve_section, search_sections
"""
