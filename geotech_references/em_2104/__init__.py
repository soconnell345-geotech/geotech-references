"""EM 1110-2-2104, Strength Design for Reinforced Concrete Hydraulic Structures.

U.S. Army Corps of Engineers (USACE) Engineer Manual 1110-2-2104, "Strength
Design for Reinforced Concrete Hydraulic Structures" (RCHS), dated 1 November
2023, published 8 January 2025 (the current edition; supersedes the
30 November 2016 edition). All docstring citations use the PRINTED page of
this edition (e.g. "printed p. 42"); the 0-based PDF page index used to
resolve figures is ``pdf_page = printed_page + 5``.

This manual amends/supplements ACI 318-19 for reinforced concrete hydraulic
structures (RCHS) -- stilling basins, floodwalls, intake towers, lock walls
and monoliths, spillway chute/basin walls, culverts and conduits, and similar
Corps civil-works concrete. Where the manual modifies an ACI 318-19
provision (load factors, load combinations, reinforcement limits, shear
capacity for members without shear reinforcement), THIS package implements
the manual's version, not the current ACI 318-19 default, and the deviation
is noted in the relevant docstring. Base ACI 318-19 values needed to exercise
the manual's own equations but not reprinted in it (beta_1, phi) are provided
as clearly-cited helpers in ``flexure_axial.py``.

Provides:
  - ``reinforcement.py`` -- Chapter 2 detailing: minimum clear cover
    (Table 2-1), tension butt-splice stagger (Table 2-2), and temperature/
    shrinkage reinforcement (Table 2-3 + the min/max per-face bar limits of
    paragraph 2-9).
  - ``loads.py`` -- Chapter 3 loads and strength design: the load
    inventory (Table 3-1), the full load-factor table (Table 3-2, permanent/
    principal/companion), the general LRFD load-combination equation
    (Eq 3-1/3-2), the three earthquake load combinations (Eq 3-3/3-4/3-5),
    and the target-reliability commentary table (Table F-2).
  - ``serviceability.py`` -- Chapter 3 serviceability: maximum service
    stresses (Table 3-3), the single-load-factor alternate serviceability
    method (Table 3-4), the mandatory (0.50 rho_b) and deflection-control
    (0.25 rho_b) tension-reinforcement-ratio limits (paragraph 3-6/3-4b),
    and minimum wall thickness (paragraph 3-7).
  - ``flexure_axial.py`` -- Chapter 4 + Appendix B: eccentricity ratio
    (Eq 4-1/4-2), the Bresler biaxial-bending load-contour check
    (Eq 4-4/4-5), and the full Appendix B INVESTIGATION equations (given a
    section's As/As', find its capacity) for singly reinforced
    tension-and-compression-controlled members (B-1 through B-21), doubly
    reinforced members (B-22 through B-39), members in tension plus uniaxial
    flexure (B-40 through B-48), and pure flexure (B-49 through B-53).
  - ``design.py`` -- Appendix D-2 DESIGN equations (given a required Mn/Pn,
    solve directly for As/As') for singly reinforced (Eq D-1 through D-9,
    Table D-1 minimum effective depth) and doubly reinforced members.
  - ``shear.py`` -- Chapter 5: one-way slab/wall shear capacity without
    shear reinforcement (Eq 5-1, the manual's pre-ACI-318-19 form, adopted
    deliberately -- see Appendix G commentary and Table G-1), special
    straight members (box culverts, gate wells; Eq 5-2/5-3), and curved
    members (Eq 5-4).
  - Structured reference text via ``geotech_references._retrieval``
    (``text/chapterNN.json``, chapters 1-5) and a figure catalog
    (``figures_catalog.json``, 32 figures, all page-confirmed).

UNITS: this manual is US-customary native (psi/ksi, inches, kips, pcf).
Values are kept in source units per repo convention; stress-unit functions
accept any consistent unit system (psi or ksi) unless documented otherwise.

Worked-example validation (module tests, doctrine: reproduce published
numbers, never tune): Appendix C-2 (singly reinforced beam analysis,
phi*Mn = 137.5 k-ft), C-3 (doubly reinforced slab analysis, Table C-1: both
tension-only and compression-steel moment capacities), D-3 (singly
reinforced retaining-wall design, As = 0.43 sq in), D-4 (combined
flexure+axial doubly reinforced wall, cubic ku = 0.357, phi*Pn = 63 kips,
phi*Mn = 2880 k-in), D-6 (special-straight-member shear, Vc = 134.9 kips),
and D-7 (curved-member shear, Vc = 192.1 kips).

Usage::

    from geotech_references.em_2104.loads import table_3_2_load_factor
    from geotech_references.em_2104.flexure_axial import (
        eccentricity_ratio, tension_controlled_capacity_singly,
    )
    from geotech_references.em_2104.design import design_singly_reinforced
    from geotech_references.em_2104.shear import shear_capacity_special_straight_member
    from geotech_references._retrieval import retrieve_section, search_sections
"""
