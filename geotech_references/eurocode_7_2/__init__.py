"""Eurocode 7 - Geotechnical Design - Part 2: Ground Investigation and Testing
(EN 1997-2:2007).

Provides:
  - Table lookup functions (test applicability, sample quality classes,
    field-test correlations digitized from the informative Annexes D-X:
    CPT, PMT, SPT, DP, WST, FVT, DMT, PLT, plus laboratory-test sample-mass
    and minimum-test-count tables)
  - Equation functions (derived-value formulas from Section 4 main body and
    the annexes: cu from CPT/CPTU/FVT/DMT, oedometer modulus from qc/DMT,
    SPT density index/settlement, DP density index, PLT modulus/subgrade
    reaction, chemical-test unit conversions)
  - Text retrieval via geotech_references._retrieval module

Usage::

    from geotech_references.eurocode_7_2.tables import table_d1_phi_e_from_qc
    from geotech_references.eurocode_7_2.equations import equation_4_1_cu_from_cpt
    from geotech_references._retrieval import retrieve_section, search_sections
"""
