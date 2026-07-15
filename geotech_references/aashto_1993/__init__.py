"""AASHTO Guide for Design of Pavement Structures, 1993 Edition.

Provides:
  - Design equations (flexible/rigid AASHO-Road-Test-derived performance
    equations, structural number composition, effective roadbed resilient
    modulus, layer coefficient regressions, reliability/stage-construction
    helpers) -- see ``equations.py``.
  - Table lookups (reliability ZR, recommended reliability by functional
    class, drainage mi/Cd, load transfer J, layer coefficient charts a1/a2,
    a representative ESAL load-equivalency-factor subset) -- see
    ``tables.py``.
  - Structured reference text via ``geotech_references._retrieval``.

Usage::

    from geotech_references.aashto_1993.equations import (
        flexible_sn_from_w18, rigid_d_from_w18, structural_number,
    )
    from geotech_references.aashto_1993.tables import (
        standard_normal_deviate_zr, layer_coefficient_a1_asphalt,
    )
    from geotech_references._retrieval import retrieve_section, search_sections
"""
