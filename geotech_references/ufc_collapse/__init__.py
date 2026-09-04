"""UFC 4-023-03, Design of Buildings to Resist Progressive Collapse.

Unified Facilities Criteria (UFC) 4-023-03, dated 14 July 2009, as amended
through Change 4 (10 June 2024). All docstring citations use the PRINTED
page of this edition (e.g. "printed p. 33"); the 0-based PDF page index
used to resolve figures is ``pdf_page = printed_page + 15``.

This UFC provides DIRECT design requirements for resisting progressive
collapse -- unlike UFC 3-301-01 (which mostly modifies civilian codes by
reference), this document prints its own tie-force equations, load/
dynamic increase factor tables, removal-location criteria, and (for
reinforced concrete and structural steel) its own REPLACEMENT ASCE 41
modeling-parameter/m-factor tables. Three design approaches are defined
in Chapter 3 and required in combination per the building's progressive-
collapse Risk Category (Chapter 2): Tie Forces (TF), Alternate Path (AP),
and Enhanced Local Resistance (ELR).

Provides:
  - ``applicability.py`` -- Chapter 1's 3-story applicability threshold
    and story/partial-occupancy definitions; Chapter 2's Table 2-1 (Risk
    Category assignment, cross-referencing UFC 3-301-01) and Table 2-2
    (the TF/AP/ELR combination required per Risk Category, including
    Footnote A's Tie-Force-minimum exemption for RC IV vs. RC V).
  - ``tie_forces.py`` -- Section 3-1, THE crown-jewel prescriptive method:
    Equation 3-2 (floor load wF), the non-uniform-floor-load averaging
    rule (Section 3-1.3.2.2), Equations 3-3/3-4/3-5 (internal longitudinal/
    transverse tie force for framed, two-way wall, and one-way wall
    construction), the column/wall-strip force cap and tie-spacing limits,
    Equations 3-6/3-7 (peripheral tie force, two-way and one-way),
    vertical tie force, Equation 3-1 (LRFD tie-strength check) and its
    rearranged required-rebar-area form, and the Section 3-1.6 splice-
    exclusion-zone rule. VALIDATED against Appendix D's worked reinforced-
    concrete example: Fp=250.1-kip and As=4.45-in2 both reproduced exactly
    from wF=214.5-psf (carried forward as a given, per Table D-2); the
    averaging CRITERIA (25%/25% thresholds) for wF itself are also
    reproduced exactly, though the source's own printed wF answer
    (214.5-psf) has a flagged ~1% arithmetic inconsistency against its own
    inputs -- see the tie_forces.py module docstring.
  - ``alternate_path.py`` -- Section 3-2: the general LRFD check (Equation
    3-8), removal-location/extent rules (Section 3-2.9, incl. the 30%
    simultaneous-removal trigger and the 4-story removal-analysis list),
    the LSP irregularity/DCR gate (Section 3-2.11.1, Equation 3-9), the
    LSP/NSP/NDP load combinations (Equations 3-10 through 3-12, 3-15,
    3-16, 3-18), Table 3-4 (Linear Static load increase factors, by
    material and structure type) and Table 3-5 (Nonlinear Static dynamic
    increase factors, incl. the printed steel and RC rotation-ratio
    equations -- the steel equation reproduces Figure C-7's fit exactly),
    the acceptance-criteria checks (Equations 3-13, 3-14, 3-17, 3-19), and
    the Section 3-2.5 force-/deformation-controlled classification rule
    (the UFC's operative rule; Table 3-1 is an ASCE-41-illustrative table
    that does not extract unambiguously -- see the module's table-
    structure note). VALIDATED against Appendix E Table E-3 (steel LIF:
    mLIF=1.8 -> 2.72, mLIF=1.79 -> 2.71).
  - ``enhanced_local_resistance.py`` -- Section 3-3: the ELR LRFD check
    (Equation 3-20, Phi always 1.0), Appendix D's Equation D-1 (pinned-
    fixed column shear demand from flexural strength, derived from PDC
    TR-06-01), the RC IV flexural-demand multipliers (2.0 columns / 1.5
    walls, Section 3-3.5.1), the 50% rebound reaction force (Section
    3-3.6), and ELR location requirements by Risk Category (Section
    3-3.2). VALIDATED against Appendix D's worked ELR check (Mn=783-ft-kip,
    L=16-ft -> Vu=367-kip via Equation D-1, matching the printed example).
  - ``reinforced_concrete.py`` -- Chapter 4: the tie-force rebar Phi=0.75
    (Section 4-3), and the FULL Tables 4-1 through 4-4 (REPLACE ASCE 41
    Tables 10-7, 10-11, 6-14, 6-15 respectively) for RC beams and two-way
    slabs/slab-column connections, with bilinear interpolation over the
    printed condition grids per Footnote 1. See the module docstring for
    a flagged ambiguity in how Tables 4-1/4-3 print their "Acceptance
    Criteria" columns (extracted identical to modeling parameters a, b).
  - ``structural_steel.py`` -- Chapter 5: the P/PCL>0.5 force-controlled-
    column classification (Section 5-4.3), and the FULL Tables 5-1
    (linear m-factors) and 5-2 (nonlinear modeling parameters) for Fully
    Restrained (WUF variants, RBS, SidePlate(R)) and Partially Restrained
    (Double Split Tee, Double Angles, Simple Shear Tab) connections, all
    as printed depth-dependent linear formulas in beam depth d or bolt-
    group depth dbg. Also Appendix C's Table C-1 (steel frame beam-to-
    column connection-type inventory: description, FR/PR classification,
    illustrating figure).
  - ``masonry_wood_cfs.py`` -- Chapters 6-8 (Masonry, Wood, Cold-Formed
    Steel), combined given how little material-specific content each
    prints: civilian-code pointers for over-strength/Phi, ASCE 41
    Chapter 11/12 Life-Safety modeling-source pointers, and the two
    numeric wood/CFS factors this UFC DOES print (wood time-effect factor
    lambda=1.0, Section 7-3; the 0.85 default-lower-bound factor for wood
    and cold-formed steel, Sections 7-1/8-1).
  - ``ibc_modifications.py`` -- Appendix H's enumerable IBC 2015 Chapter
    16/17 modifications: construction-document notes (Section 1603.1.9),
    the quality-assurance-plan trigger by Risk Category (Section 1710.1.1)
    and its detailed content list (1710.1.2), material-keyed special
    inspection requirements (Section 1711.2-1711.5), and the structural-
    observation trigger (Section 1712.1). The narrative contractor-
    responsibility procedural text (Sections 1710.2-1710.3) is NOT
    reprinted -- administrative process text, no design criteria.
  - Structured reference text via ``geotech_references._retrieval``
    (``text/chapterNN.json``, chapters 1-8) and a figure catalog
    (``figures_catalog.json``, 39 figures across Chapter 3, Appendices
    B, C, and D, all page-confirmed against this document's own List of
    Figures).

NOT digitized (surveyed, deliberately out of scope):
  - Appendix A, "References" (printed pp. 77-80) -- the source document
    list; see the UFC directly for citations.
  - Appendix B, "Definitions" (printed pp. 81-88) -- narrative
    terminology and structural-analysis-procedure definitions (joint/
    connection rotation, yield/plastic rotation, panel zone, story drift).
    No printed design equations except an unlabeled steel yield-rotation
    formula (printed p. 85) that did not survive text extraction (image-
    rendered equation) -- flagged for lead visual check if needed; ASCE
    41 Equation 9-1 is the citable source per the UFC's own text.
  - Appendix C, "Commentary" (printed pp. 89-118) -- background and
    justification narrative for the Chapter 1-3 requirements (largely
    mined into this package's docstrings); Table C-1 and the printed
    Figure C-7 fit ARE digitized (structural_steel.py, alternate_path.py)
    since they carry reusable content beyond pure rationale.
  - Appendices E, F, G -- full worked Alternate Path examples (steel,
    wood, cold-formed steel) built around specific SAP2000/software
    modeling workflows for particular example buildings (member sizes,
    hinge property tables, iteration logs). These are software-modeling
    narratives, not general design equations of the kind this package
    digitizes elsewhere; Appendix E's Table E-3 (m-factor -> load-increase-
    factor worked numbers) IS used as a validation anchor for Table 3-4
    in ``alternate_path.py``, but the appendices themselves are not
    otherwise transcribed.
  - Table 3-1, "Examples of Deformation Controlled and Force-Controlled
    Actions, from ASCE 41" (printed p. 33) -- an illustrative table
    reproduced from ASCE 41 with a bulleted/merged-cell layout that does
    NOT extract into an unambiguous component/action/classification
    mapping; this UFC's own OPERATIVE classification rule (Section 3-2.5)
    is fully digitized instead (``alternate_path.classify_action``).
  - Table 4-2 in ASCE 41 terms is REPLACED (not this UFC's own numbering);
    all four RC replacement tables (4-1 through 4-4) are fully digitized.

Tables 4-1 and 4-3 (reinforced_concrete.py) carry a flagged extraction
ambiguity in their "Acceptance Criteria" columns -- see that module's
docstring.

UNITS: this manual is US-customary native (psf, psi, ksi, ft, in, kip).
Values are kept in source units per repo convention.

Worked-example validation: Appendix D (reinforced-concrete tie-force and
ELR example, printed pp. 119-131) is reproduced numerically -- Table D-1's
25%/25% averaging-criteria decision is reproduced exactly (the resulting
wF=214.5-psf carries a flagged ~1% source-arithmetic discrepancy, see
tie_forces.py); Fp=250.1-kip and As=4.45-in2 (Table D-2) and Vu=367-kip
via Equation D-1 (ELR shear demand) are all reproduced exactly from that
carried-forward wF. Appendix E's Table E-3 (steel structural-steel
example, printed p. 138) validates the Table 3-4 load-increase-factor
formula (mLIF=1.8/1.79 -> Omega_LD=2.72/2.71).
Module tests reproduce both, clearly labeled by anchor type (printed
worked-example values vs. printed table-value/self-consistency anchors).

Usage::

    from geotech_references.ufc_collapse.tie_forces import (
        floor_load_wf, peripheral_tie_force_two_way, required_tie_area,
    )
    from geotech_references.ufc_collapse.alternate_path import (
        table_3_4_load_increase_factor, table_3_5_dynamic_increase_factor,
    )
    from geotech_references.ufc_collapse.enhanced_local_resistance import (
        shear_demand_pinned_fixed_column,
    )
    from geotech_references._retrieval import retrieve_section, search_sections
"""
