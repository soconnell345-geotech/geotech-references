"""GSA Alternate Path Analysis and Design Guidelines for Progressive
Collapse Resistance (October 24, 2013, Revision 1, January 28, 2016).

The GSA Guidelines are the federal-CIVILIAN sibling of UFC 4-023-03
(``geotech_references.ufc_collapse``), DoD's progressive-collapse design
criteria. Per this document's own Section 1.5 ("Document Organization"):
"With the exception of the first introductory section (Chapters 1 and 2)
the main body of this document incorporates the general organization and
content of the UFC 04-023-03 as it relates to Alternate Path only. The
adopted methodology has been incorporated in its entirety such that these
Guidelines are a stand-alone document." Concretely, that means:

  - GSA employs the ALTERNATE PATH (AP) method ONLY. Both of UFC
    4-023-03's other two methods -- Tie Forces (Section 3.1) and Enhanced
    Local Resistance (Section 3.3) -- are REMOVED IN THEIR ENTIRETY, in
    the design-procedures chapter AND in every material chapter (Sections
    4.3/4.5, 5.3/5.5, 6.3/6.5, 7.4/7.6, 8.3/8.5). Commentary C3.1 explains
    GSA considered Tie Forces superfluous (FSL V's whole-building removal
    scope already provides that robustness) and difficult to apply to
    existing buildings.
  - GSA REPLACES UFC 4-023-03's applicability trigger (mandatory for new
    construction of 3+ stories, Occupancy-Category-based method
    combination) with its own FACILITY SECURITY LEVEL (FSL) trigger, per
    the Interagency Security Committee (ISC) Risk Management Process:
    FSL I/II never apply; FSL III/IV apply at 4+ stories (Alternate Path
    AND Redundancy); FSL V applies at any story count (Alternate Path
    only).
  - GSA ADDS entirely new content NOT found anywhere in UFC 4-023-03:
    REDUNDANCY REQUIREMENTS (Section 3.4) -- a load-redistribution-system
    location/strength/stiffness check applied up the height of the
    building, independent of the column/wall removal scenarios -- and an
    existing-building disproportionate-collapse ALLOWANCE (Section
    3.2.10.2, 15%/30% of floor area) that the current UFC 4-023-03 edition
    does not carry.

Provides:
  - ``applicability.py`` -- Section 2.3 / Figure 2.1's FSL applicability
    flow chart (``fsl_applicability``), the story-count exclusion for
    mechanical penthouses and parking (``counts_as_story``), and the
    50%-addition-area threshold that triggers existing-building evaluation
    (``addition_triggers_existing_building_evaluation``, Section 2.1 /
    Commentary C2.1).
  - ``alternate_path.py`` -- Section 3.2: the general LRFD check (Equation
    3.1), force-/deformation-controlled action classification (Section
    3.2.5, Table 1/Figure 3.7 -- IDENTICAL wording to UFC 4-023-03),
    component-capacity bases (Tables 2/3), FSL-keyed removal-location
    rules (Section 3.2.9 -- REPLACES UFC's Occupancy-Category-based
    scheme), the 30%-adjacent-element simultaneous-removal trigger, the
    existing-building disproportionate-collapse allowance (Section
    3.2.10.2, NOT in current UFC 4-023-03), the LSP's 10-story cap
    (Section 3.2.11.1, NOT in UFC 4-023-03) plus its irregularity/DCR gate,
    the LSP/NSP/NDP load combinations (Equations 3.3-3.5, 3.8-3.9, 3.11),
    Table 4 (Load Increase Factors) and Table 5 (Dynamic Increase
    Factors), and the acceptance-criteria checks (Equations 3.6, 3.7,
    3.10, 3.12). VALIDATED against Appendix D's worked reinforced-concrete
    example's m-factor calculations (see ``reinforced_concrete.py``).
  - ``redundancy.py`` -- Section 3.4: THE NEW-CONTENT CROWN JEWEL, not
    present anywhere in UFC 4-023-03. The n >= N/3 minimum load-
    redistribution-system count (Equation 3.13), the +/-30%
    strength-uniformity check (Equations 3.14-3.16), and the +/-30%
    stiffness-uniformity check (Equations 3.17-3.19), all up the height of
    the building at each exterior ground-level removal location.
    VALIDATED against Appendix D's worked redundancy example (an 8-story
    building: n=3 exactly per Equation 3.13; QR3=QR5=QR7=QR_bar=1444.4
    kip-in and KR3=KR5=KR7=KR_bar=528 kip/in, both reproduced exactly,
    including the fixed-fixed flexural-stiffness formula
    KC=384*Ec*Icr/L^3 used to build KR).
  - ``reinforced_concrete.py`` -- Chapter 4: the FULL Tables 6 through 9
    (REPLACE ASCE 41 Tables 10-7, 10-13, 10-15, 10-16 respectively) for RC
    beams and two-way slabs/slab-column connections, with bilinear
    interpolation over the printed condition grids per Footnote 1, PLUS
    the Appendix D worked-example column shear-classification check
    (Vp/Vo <= 0.6). VALIDATED against Appendix D's typical-beam-component
    m-factor example (rho-rho'/rho_bal=0.037, conforming transverse
    reinforcement, at V/(bw*d*sqrt(f'c))=3 -> m=15.48, reproduced exactly)
    and column-component example (P/(Ag*f'c)=0.35, rho_v=0.003 -> m=2.0,
    reproduced exactly). The SAME beam example carries TWO further
    FLAGGED PRINTED ARITHMETIC DISCREPANCIES -- see
    ``reinforced_concrete.py``'s docstring: its companion result at
    V/(bw*d*sqrt(f'c))=6 (printed as m=8.88; correctly recomputed as
    8.778) and its final bilinearly-interpolated answer (printed as
    m=10.74 at V/(bw*d*sqrt(f'c))=3.88; correctly recomputed as m=13.54).
  - ``structural_steel.py`` -- Chapter 5: the P/PCL>0.5 force-controlled-
    column classification (Section 5.4.3), the FULL Tables 10 (linear
    m-factors) and 11 (nonlinear modeling parameters) for Fully Restrained
    (WUF variants, RBS, SidePlate(R)) and Partially Restrained (Double
    Split Tee, Double Angles, Simple Shear Tab) connections, and Appendix
    C's Table C1.1 (steel frame connection-type inventory).
  - ``masonry_wood_cfs.py`` -- Chapters 6-8 (Masonry, Wood, Cold-Formed
    Steel): civilian-code material/Phi pointers, the wood time-effect
    factor lambda=1.0, the 0.85 default-lower-bound factor for wood/CFS,
    and the (unchanged, Life-Safety-level) ASCE 41 performance-level
    pointer -- Commentary C6/C7/C8 explain these three materials do NOT
    get the Collapse-Prevention upgrade that Chapters 4-5 receive, for
    lack of supporting test data.
  - Structured reference text via ``geotech_references._retrieval``
    (``text/chapterNN.json``, chapters 1-8) and a figure catalog
    (``figures_catalog.json``, 35 figures across Chapter 2, Chapter 3,
    Appendices B, C, and D, all page-confirmed against this document's own
    front-matter List of Figures).

CROSS-DOCUMENT CONSISTENCY WITH ufc_collapse (verified in this package's
test suite -- see each module's docstring and the corresponding test file
for the exact assertions):
  - MATCH: Table 4/Table 3-4 (Load Increase Factors) -- identical.
  - MATCH: Table 5/Table 3-5 (Dynamic Increase Factors) -- identical.
  - MATCH: ``classify_action``/``classify_action`` (Section 3.2.5) --
    identical wording and thresholds.
  - MATCH: Tables 6/7 vs UFC Tables 4-1/4-2 (RC beams) -- identical.
  - MATCH: Table 11 vs UFC Table 5-2 (nonlinear steel connections) --
    identical.
  - MATCH: Table C1.1 vs UFC Table C-1 (steel connection inventory) --
    identical restraint classification for all 17 types, and identical
    description text for 13 of 17 (4 rows have confirmed minor wording
    differences -- see ``structural_steel.py`` docstring).
  - CONFIRMED DIFFERENCE (page-verified against both rendered PDFs): Table
    9 vs UFC Table 4-4 (linear slab m-factors) -- the Vg/Vo<=0.2/No-
    continuity row (GSA: 3,3; UFC: 2,2) and the "inadequate embedment"
    row's primary m-factor (GSA: not applicable/"-"; UFC: 3).
  - CONFIRMED DIFFERENCE (page-verified against both rendered PDFs): Table
    10 vs UFC Table 5-1 (linear steel connection m-factors) -- three Fully
    Restrained connection types (Improved WUF-Bolted-Web, Reduced Beam
    Section, WUF) and all four Double Split Tee limit states differ
    numerically, while SidePlate(R), Double Angles, and Simple Shear Tab
    match exactly. Flagged as worth an independent re-check of
    ufc_collapse's own Table 5-1 digitization, since the corresponding
    NONLINEAR table (11/5-2) matches perfectly for the very same
    connection types.
  - NEW CONTENT (no UFC 4-023-03 analog exists): Redundancy Requirements
    (``redundancy.py``) and the existing-building disproportionate-
    collapse allowance (``alternate_path.disproportionate_collapse_allowance``).

NOT digitized (surveyed, deliberately out of scope, mirroring
ufc_collapse's own scope conventions):
  - Appendix A, "References" (printed pp. A1-A2) -- the source document
    list; see the Guidelines directly for citations.
  - Appendix B, "Definitions" (printed pp. B1-B7) -- narrative terminology
    (largely identical to UFC 4-023-03 Appendix B, PLUS several
    lease/procurement-specific definitions unique to a GSA document: New/
    Succeeding/Superseding Leases, Full and Open Competition, Controlled
    Public Access, Design-Basis Threat). No printed design equations
    except the same steel yield-rotation formulas UFC 4-023-03 Appendix B
    prints (ASCE 41 Equation 9-1 is the citable source).
  - Appendix C, "Commentary" (printed pp. C1-C23) -- background and
    justification narrative for the Chapter 1-3 requirements (mined into
    this package's docstrings); Table C1.1 IS digitized
    (``structural_steel.py``) since it carries reusable content.
  - Appendix D, "Reinforced Concrete Example" (printed pp. D1-D54) -- a
    full worked Alternate Path + Redundancy example (SAP2000 modeling
    workflow, iteration/upgrade logs for a specific 7-story example
    building) built around software-specific member sizing. This is a
    software-modeling narrative, not general design equations of the kind
    this package digitizes elsewhere; its m-factor and redundancy
    calculation STEPS ARE used as validation anchors in
    ``reinforced_concrete.py`` and ``redundancy.py``, but the appendix
    itself is not otherwise transcribed. Only Figures D2.1-D2.5 (building
    floor/roof/elevation plans -- general geometry, not SAP2000
    screenshots) are cataloged.
  - Appendix E, "Structural Steel Example" (printed pp. E1-E42) -- a
    parallel worked example for a 4-story steel building, in the same
    software-modeling-narrative genre as Appendix D; NOT transcribed and
    NOT cataloged for figures (mirrors ufc_collapse's own decision to skip
    its analogous Appendices E/F/G in their entirety).

UNITS: this manual is US-customary native (psf, psi, ksi, ft, in, kip).
Values are kept in source units per repo convention.

Worked-example validation: Appendix D (reinforced-concrete Alternate Path
and Redundancy example, printed pp. D1-D54) is reproduced numerically --
the typical-beam-component and column-component m-factor examples
(``reinforced_concrete.py``) and the full n/QR/QR_bar and KR/KR_bar
redundancy worked example (``redundancy.py``) are all reproduced exactly.
Module tests reproduce all anchors, clearly labeled by anchor type
(printed worked-example values vs. printed table-value/self-consistency
anchors vs. cross-document consistency checks against ufc_collapse).

Usage::

    from geotech_references.gsa_collapse.applicability import fsl_applicability
    from geotech_references.gsa_collapse.alternate_path import (
        table_4_load_increase_factor, table_5_dynamic_increase_factor,
    )
    from geotech_references.gsa_collapse.redundancy import (
        minimum_load_redistribution_systems, load_redistribution_strength_ratio,
    )
    from geotech_references._retrieval import retrieve_section, search_sections
"""
