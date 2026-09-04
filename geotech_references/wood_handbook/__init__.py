"""Wood Handbook: Wood as an Engineering Material.

USDA Forest Products Laboratory, General Technical Report FPL-GTR-282
(2021 edition). All docstring citations use the PRINTED page of this
edition (e.g. "printed p. 5-6"); the 0-based PDF page index used to
resolve figures is ``pdf_page = printed_page_number + {93 (Ch. 4) | 115
(Ch. 5) | 203 (Ch. 8) | 231 (Ch. 9)}`` (each chapter starts its own
printed-page count at 1).

SOURCE FILE: this handbook's source PDF (~104 MB, ~546 pages) is
LOCAL-ONLY -- too large for the GitHub repository, so it is git-ignored.
It is expected at ``docs/USDA_Wood_Handbook_FPL-GTR-282.pdf`` (the
``pdf_path`` convention followed by every other reference in this
package, so figure_search/read_reference_figure resolve correctly once
the file is present locally); download it from
https://research.fs.usda.gov/download/treesearch/62200.pdf and place it
in ``docs/`` to enable figure catalog rendering for this module.

SCOPE -- this is a 20-chapter, ~600-page general wood-engineering
reference; this package digitizes the DESIGN-USABLE CORE of four
chapters only (not the wood-science/manufacturing/finishing/preservation
chapters):
  - Chapter 4 (Moisture Relations and Physical Properties of Wood):
    equilibrium moisture content, shrinkage, density/specific-gravity
    conversions.
  - Chapter 5 (Mechanical Properties of Wood): the clear-wood strength/
    stiffness property table for a documented structural species subset,
    moisture-content and temperature adjustment relations.
  - Chapter 8 (Fastenings): nail/screw/lag-screw/bolt withdrawal and
    lateral-resistance equations (both the pre-1991 empirical forms and
    the post-1991 yield-limit model, all printed in this handbook itself).
  - Chapter 9 (Structural Analysis Equations): the complete printed
    deformation/stress/stability equation set (axial, bending, torsion,
    combined loading, column and beam buckling, biaxial interaction).
See each submodule's own docstring for the exact equation/table inventory
and any documented gaps (e.g. the Chapter 5 duration-of-load relationship
is graphical-only in this edition and is NOT implemented -- see
mechanical_properties.py and the Chapter 5 chapter09.json text entry
"5-9" for the citation). NDS (National Design Specification) design
values and adjustment factors are explicitly OUT OF SCOPE throughout --
NDS is a separate copyrighted standard; only this handbook's own clear-
wood data and equations are implemented.

Provides:
  - ``moisture_relations.py`` -- Chapter 4: equilibrium moisture content
    (Hailwood-Horrobin Eq 4-5 and the Glass and others 2014 alternative
    Eq 4-6/4-7), maximum/sink moisture content from specific gravity
    (Eq 4-3/4-4), shrinkage-moisture content-specific gravity relations
    (Eq 4-9 to 4-13, Table 4-3 shrinkage values), density at any moisture
    content (Eq 4-14 to 4-16), and thermal conductivity (Eq 4-17).
  - ``mechanical_properties.py`` -- Chapter 5: clear-wood property table
    (Table 5-3a, metric, for the documented 27-species structural subset),
    moisture-content adjustment (Eq 5-3, Table 5-13), and temperature
    effect relations (Table 5-15/5-16).
  - ``fastenings.py`` -- Chapter 8: withdrawal (nails Eq 8-1/8-2a, drift
    bolts Eq 8-9, wood screws Eq 8-10, lag screws Eq 8-14) and lateral
    resistance (pre-1991 empirical Eq 8-2/8-13/8-15 with Table 8-4 K
    coefficients; post-1991 yield-limit model via dowel bearing strength
    Eq 8-3 and the full Table 8-5 governing-mode calculation), plus the
    general Hankinson bearing-at-an-angle formula (Eq 8-16).
  - ``structural_deformation.py`` -- Chapter 9 Deformation Equations:
    axial (Eq 9-1), straight/tapered beam deflection (Eq 9-2 to 9-5,
    Table 9-1), water ponding (Eq 9-6), combined bending+axial (Eq 9-7/
    9-8), and torsion (Eq 9-9 to 9-11).
  - ``structural_stress.py`` -- Chapter 9 Stress Equations: axial/bending/
    shear (Eq 9-12 to 9-14), tapered beam stresses (Eq 9-15/9-16), size
    effect (Eq 9-17 to 9-20), notch crack initiation (Eq 9-21, Fig 9-14),
    combined bending+axial stress (Eq 9-22), and torsion (Eq 9-23/9-24).
  - ``structural_stability.py`` -- Chapter 9 Stability Equations: column
    buckling (Euler Eq 9-25/9-26, FPL fourth-power Eq 9-27, Ylinen Eq
    9-28/9-29, built-up columns Eq 9-30, flange instability Eq 9-31),
    beam lateral-torsional buckling (Eq 9-32 to 9-35, Table 9-2), and the
    full biaxial beam-column interaction check (Eq 9-36 to 9-41).
  - Structured reference text via ``geotech_references._retrieval``
    (``text/chapterNN.json``, chapters 4, 5, 8, 9 -- covered chapters
    only, 37 sections) and a figure catalog (``figures_catalog.json``,
    86 figures spanning the same 4 chapters, all page-confirmed against
    the source PDF's own printed page markers).

UNITS: this package digitizes the handbook's own SI (metric) tables and
equations throughout (matching repo convention), even though the source
prints matching inch-pound tables side by side. Temperature-adjustment
Table 5-16 is a printed exception that keeps its native degrees-Fahrenheit
form (documented in that function's docstring) because the printed
coefficients are fit to F, not C.

Worked-example validation (module tests, doctrine: reproduce published
numbers, never tune): the white-ash Eq 5-3 moisture adjustment example
(P8 = 119,500 kPa from P12=103,000/Pg=66,000/Mp=24); the Eq 4-13/4-14
white-ash density worked example (G12=0.605, rho=678 kg/m^3 from
Gb=0.55); the Eq 9-16 tapered-beam worked example (fx=375*M, fxy=37.5*M,
fy=3.75*M for b=100 mm, h0=200 mm, tan(theta)=1/10); and the Eq 9-18
size-effect worked example (R1=7,330 lbf/in^2 from R2=10,000 lbf/in^2,
h1=10 in, L1=216 in, third-point loading, m=18).

Usage::

    from geotech_references.wood_handbook.mechanical_properties import (
        table_5_3_mechanical_properties, adjust_property_for_moisture_content,
    )
    from geotech_references.wood_handbook.moisture_relations import (
        equilibrium_moisture_content, shrinkage_at_moisture_content,
    )
    from geotech_references.wood_handbook.fastenings import (
        nail_withdrawal_common, yield_limit_lateral_strength,
    )
    from geotech_references.wood_handbook.structural_deformation import (
        straight_beam_deflection,
    )
    from geotech_references.wood_handbook.structural_stress import bending_stress
    from geotech_references.wood_handbook.structural_stability import (
        euler_critical_stress, ylinen_buckling_stress,
    )
    from geotech_references._retrieval import retrieve_section, search_sections
"""
