"""UFC 3-250-11, Soil Stabilization and Modification for Pavements (30 Nov 2020).

Provides:
  - Table lookups (min. UCS by pavement type, durability requirements, the
    flagship additive-selection guide, cement/lime/bituminous gradation
    envelopes, cement content by USCS class, emulsified-asphalt content,
    swell potential, and Appendix A's thickness-equivalency factors) --
    see ``tables.py``.
  - Equations (cement content for PI-reduction modification, cutback-asphalt
    content estimate, the Table 2-3 footnote-c PI limit, stabilized-layer
    equivalent thickness, and the Appendix A-3 sulfate-determination
    formulas) -- see ``equations.py``.
  - Structured reference text via ``geotech_references._retrieval``.

Usage::

    from geotech_references.ufc_stabilization.tables import (
        table_2_3_additive_selection_guide, table_a1_equivalency_factors,
    )
    from geotech_references.ufc_stabilization.equations import (
        equation_cement_content_modifying_soils,
        equation_stabilized_equivalent_thickness,
    )
    from geotech_references._retrieval import retrieve_section, search_sections
"""
