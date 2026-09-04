"""UFC 3-301-01, Structural Engineering.

Unified Facilities Criteria (UFC) 3-301-01, "Structural Engineering", dated
11 April 2023, as amended through Change 4 (3 June 2025). All docstring
citations use the PRINTED page of this edition (e.g. "printed p. 49"); the
0-based PDF page index used to resolve figures is
``pdf_page = printed_page + 21``.

This UFC ADOPTS the 2024 International Building Code (IBC) and ASCE/SEI
7-22 as the DoD structural design basis, then prints DoD-specific
MODIFICATIONS to both -- additions, deletions, replacements, and
supplements (the four action types defined in paragraph 1-6, digitized in
``general_provisions.py``). THIS package implements only the provisions
this UFC itself prints (the DoD-modified/added content); base IBC/ASCE 7-22
content that is merely adopted by reference (e.g. member-capacity design
equations, most load determination procedures) is NOT reprinted here --
apply the civilian code directly for anything this UFC does not modify.
Where a provision replaces a civilian-code table or equation, the relevant
docstring says so explicitly (e.g. "Table 3-1 REPLACES ASCE 7-22 Table
12.2-1 in its entirety").

Provides:
  - ``general_provisions.py`` -- Chapter 1: the four modification-action
    definitions (paragraph 1-6), the Risk Category V pointer (1-8.3, see
    Table 2-2 for the actual RC V occupancy list), the progressive-collapse
    applicability pointer to UFC 4-023-03 (1-8.2, no printed trigger table --
    "when required, apply UFC 4-023-03"), and the cybersecurity pointer
    (1-8.4).
  - ``risk_category_and_loads.py`` -- Chapter 2 Section 1604 wind-induced
    deflection limits (Table 2-1) and the full Risk Category table
    including the DoD-added Risk Category V and DoD Sea Level Rise scenario
    column (Table 2-2, REPLACES IBC Table 1604.5 / ASCE 7-22 Tables 1.5-1
    and 1.5-2); Appendix E's full minimum live-load table (Table E-1,
    REPLACES IBC Table 1607.1, 64 occupancy categories including
    DoD/military-specific additions); Section 1609.3.1 wind-speed
    conversion equations (Eq 16-18a/16-18b) and the non-permanent-structure
    wind-speed reduction factor (0.78, paragraph 1609.3.3); the
    SDS > 0.6g vertical-ground-motion-sensitive-member threshold check
    (paragraph 1605.1.2) that triggers the additional seismic load
    combinations in ``seismic_load_combinations.py``.
  - ``seismic_load_combinations.py`` -- the additional LRFD (Section 2.3.6)
    and ASD (Section 2.4.5) load combinations for vertical-ground-motion-
    sensitive members, with the vertical seismic effect Ev0 = 0.67*SDS*D;
    the Appendix B alternate Risk Category IV seismic load combinations
    (Eq B-1, B-2); the Chapter 2 coupling-beam capacity-design shear check
    (paragraph 2106.2.3); and the Chapter 7 healthcare structural-separation
    equation (Eq 12.12-1, delta_M = Cd*delta_max).
  - ``seismic_force_resisting_systems.py`` -- the full Table 3-1 (REPLACES
    ASCE 7-22 Table 12.2-1 in its entirety: R, Omega0, Cd, and structural
    height limits by Seismic Design Category for ~85 systems across
    categories A-H); Table 7-1 (the smaller permitted-systems subset for
    Chapter 6/7 critical healthcare facilities, REPLACES ASCE 7-16 Table
    12.2-1 for those facilities); and Table B-1 (the Appendix B alternate
    Risk Category IV nonlinear-design permitted-systems table, which
    REPLACES both ASCE 7-22 Table 12.2-1 and this UFC's own Table 3-1 when
    the Appendix B alternate procedure is used -- R/Cd/Omega0 do not apply
    to that procedure, only height/SDC limitations).
  - ``evaluation_retrofit.py`` -- Chapter 4's Table 4-1(a)/4-1(b)
    structural/nonstructural performance-objective lookup (trigger x risk
    category -> evaluation/retrofit performance level and hazard level,
    REPLACES RP 10 Tables 2-1/2-2/2-3), the RP 10 evaluation-trigger cost
    thresholds (paragraph 4-2.1: 50% of replacement cost for SDC C, 30%
    for SDC D-F), and the IEBC high-wind roof-diaphragm retrofit trigger
    (paragraph 503.12: 130 mph threshold, 50% cost/re-roofing triggers).
    Table 4-2 (the ASCE 41-17 benchmark-building code-vintage cross-
    reference, printed pp. 78-81) is NOT digitized -- it is an 18-building-
    type x 11-code-vintage administrative lookup with no design equations;
    consult the printed table directly.
  - ``healthcare_modifications.py`` -- Chapter 6/7's Table 6-1 (minimum
    masonry wall thickness by height/length-to-thickness ratio) and the
    Chapter 7 healthcare-specific structural configuration limits (uniform
    bay spacing, transfer-beam restriction, 125%-of-ASCE-7 seismic joint
    sizing, 2 in./story adjacent-structure separation).
  - ``nonbuilding_structures.py`` -- Chapter 5's governing-standard lookup
    for ten nonbuilding structure types (highway/railroad/pedestrian
    bridges, tanks, towers, water treatment facilities) -- pointers only,
    no printed equations in this UFC.
  - ``nonstructural_seismic.py`` -- Appendix C's rigid-pipe maximum-span
    tables (Tables C-1/C-2/C-3, pinned-pinned/fixed-pinned/fixed-fixed
    support conditions) with the underlying period equation (Eq C-1) and
    period constants; elevator, counterweight, and partition-wall seismic
    design criteria with their printed numeric limits.
  - ``gfrp.py`` -- Appendix G's Table G-1 (GFRP vs. steel reinforcement
    material-property comparison) and the printed GFRP design factors
    (0.85 environmental reduction factor, 0.3x sustained-stress service
    limit, 60% bend-strength reduction, seismic force-resisting-system
    prohibition by Seismic Design Category).
  - ``best_practices.py`` -- Appendix A's topic-indexed best-practice
    guidance (drift limits, expansive-soil footings, corrosion protection,
    etc.) with the handful of printed numeric criteria embedded in that
    narrative appendix (shelf-angle deflection limit, masonry veneer ledge
    offset, gable-bent tie-rod force range).
  - Structured reference text via ``geotech_references._retrieval``
    (``text/chapterNN.json``, chapters 1-7) and a figure catalog
    (``figures_catalog.json``, 13 figures, all page-confirmed).

NOT digitized (surveyed, deliberately out of scope -- no printed design
tables/equations, or narrow case-study content):
  - Appendix F, "Composites for Bridging Applications" [ADDITION]
    (printed pp. 161-180) -- FRP/thermoplastic bridge-component guidance
    and case studies; no DoD-modified structural design tables/equations of
    the kind this package digitizes elsewhere.
  - Appendix H, "Glossary" (printed pp. 191-196) -- abbreviation
    definitions only.
  - Appendix I, "References" (printed pp. 197-206) -- the source document
    list; see the UFC directly for citations.
  - Table 4-2 (see above).
  - Figure C-9's multi-mode period-coefficient chart for uniform cantilever/
    pinned-base beams (printed p. 143) -- the underlying text extraction
    interleaves the per-mode-shape coefficients ambiguously; the single-
    mode fundamental-period formula and its C constants (Eq C-1) ARE
    digitized in ``nonstructural_seismic.py``. Flagged for lead visual
    check if higher-mode stack coefficients are needed.

UNITS: this manual is US-customary native (psi/ksi, feet/inches, psf, kips).
Values are kept in source units per repo convention.

Worked-example validation: this is a criteria/administrative document
(load factors, risk categories, seismic design tables) with NO printed
numerical worked examples of the kind found in design manuals like EM
1110-2-2104. Module tests therefore anchor on printed TABLE/EQUATION
values directly (e.g. reproducing specific Table 3-1 rows, Table E-1
occupancy loads, the Eq C-1 pipe-span calculation) and on self-consistency
checks (e.g. Table 7-1 rows are a strict subset of Table 3-1 for the same
system), clearly labeled as such in the test docstrings.

Usage::

    from geotech_references.ufc_structural.risk_category_and_loads import (
        table_2_2_risk_category, table_e1_live_load,
    )
    from geotech_references.ufc_structural.seismic_force_resisting_systems import (
        table_3_1_seismic_system,
    )
    from geotech_references.ufc_structural.seismic_load_combinations import (
        alternate_rc4_seismic_combination,
    )
    from geotech_references._retrieval import retrieve_section, search_sections
"""
