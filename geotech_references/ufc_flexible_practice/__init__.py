"""UFC 3-250-03, Standard Practice Manual for Flexible Pavements (30 May 2018).

A construction-practice / QC manual for hot-mix asphalt (equipment,
materials, dense-graded HMA and Marshall mix design, porous friction
course, stone matrix asphalt, warm-mix asphalt), spray applications (prime
coat, tack coat, fog seals, rejuvenation), seal coats (surface treatments,
slurry seal, fuel-resistant sealer, micro-surfacing), asphalt
stabilization, miscellaneous mixtures (recycled/sand/sheet/rock/cold-mix
asphalt), and resin modified pavement (RMP). Unlike a design-code
reference, most of this document is narrative/procedural rather than
equation-driven -- the full chapter text (``text/``) is the primary
deliverable of this module.

Provides:
  - Structured reference text for all 7 chapters plus Appendices A
    (References), B (Best Practices), and C (Glossary) -- via
    ``geotech_references._retrieval``.
  - A figure catalog (``figures_catalog.json``, 17 figures) for
    text-search + vision figure read-off.
  - Table lookups (``tables.py``, 24 functions) for the genuinely
    lookup-worthy tables only: PG-grade/asphalt-cement selection by
    climate (Tables 2-3, 2-5, 6-2), Marshall/Superpave mix design and
    acceptance criteria (Tables 2-7, 2-8, 2-17), aggregate gradation
    bands (Tables 2-1, 2-12, 2-15, 4-4, 4-5, 6-1, 7-2, 7-3, and the
    combined SBST/DBST surface treatment gradations), spray application
    rates (prime/tack/fog/rejuvenator), spray/mixing temperatures
    (Tables 3-2, 6-4), RMP grout mixture proportions and viscosity
    (Tables 7-4, 7-5), and the slurry-seal surface-area design method's
    factor table (Table B-1). Purely descriptive tables (ASTM spec
    citation lists, worked-example instance data, thin single-row
    property sheets) were intentionally left undigitized -- see the
    ``tables`` module docstring.
  - Equation functions (``equations.py``, 12 functions) for the handful of
    genuinely closed-form formulas in an otherwise narrative document:
    Marshall/Superpave volumetric mixture properties (Gmb, Vv/VTM, VMA,
    VFA), the Fuller-Thompson 0.45-power maximum-density gradation curve,
    the RMP open-graded mixture's French optimum-asphalt-content method,
    and the Appendix B slurry-seal surface-area asphalt-content design
    procedure (with a documented, worked-example-verified fix to a
    decimal-point typo in the source's printed metric coefficient).

Usage::

    from geotech_references.ufc_flexible_practice.tables import (
        table_2_8_marshall_design_criteria, table_2_3_asphalt_grade_by_pti,
    )
    from geotech_references.ufc_flexible_practice.equations import (
        voids_in_mineral_aggregate_vma, slurry_seal_total_asphalt_required,
    )
    from geotech_references._retrieval import retrieve_section, search_sections
"""
