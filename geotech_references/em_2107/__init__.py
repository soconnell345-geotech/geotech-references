"""EM 1110-2-2107, Design of Hydraulic Steel Structures.

U.S. Army Corps of Engineers (USACE) Engineer Manual 1110-2-2107, "Design
of Hydraulic Steel Structures" (HSS), dated 1 August 2022 (the current
edition). All docstring citations use the PRINTED page of this edition
(e.g. "printed p. 42"); the 0-based PDF page index used to resolve figures
is ``pdf_page = printed_page + 8``.

This manual gives LRFD load and resistance criteria for HSS (miter gates,
Tainter gates, Tainter valves, vertical lift gates, levee closure gates,
bulkheads/stoplogs, sector gates, and associated trunnion girders and
anchorages) designed to AISC 360 (with an HSS-specific performance factor)
as modified/supplemented herein. UNLIKE EM 1110-2-2104 (which amends ACI
318-19's member-design equations for concrete), this manual does NOT
reprint AISC 360 member-capacity equations for tension/compression/
flexure/shear -- Chapter 4's own commentary states "Design equations for
individual HSS are provided in Chapters 9-16," and members/connections are
designed to AISC 360 directly (Appendix B commentary B.4.1). The closed-
form, generalizable content this manual DOES print is concentrated in:
loads/load-factors/load-combinations (Chapter 4), the HSS-support seismic-
acceleration amplification method (Chapter 4.4 + Appendix D, incl. a fully
worked example), and Chapter 10 + Appendix F's Tainter-gate load-
determination equations (side-seal friction, wire-rope loads, hydrostatic
load by integration, trunnion friction) -- all validated below against the
manual's own printed worked examples (Appendix D, E, F).

Provides:
  - ``design_basis.py`` -- Chapter 3: target reliability index beta by
    structure class/load path (Table 3.1), and the usual/unusual/extreme
    load-category classification by return period/AEP (paragraph 3.3.4).
  - ``loads.py`` -- Chapter 4: the basic LRFD safety check with the HSS
    performance factor (Eq 4.1), the full minimum-load-factor table
    (Table 4.1) and its lookup functions, generic principal-load-factor
    conditions (paragraph 4.3.4), the general LRFD load-combination
    equation (Eq 4.2), and the three earthquake load combinations
    (Eq 4.7/4.8/4.9).
  - ``seismic_amplification.py`` -- paragraph 4.4 + Appendix D: the
    Westergaard hydrodynamic pressure (Eq 4.3), the fundamental mode shape
    (Eq 4.5/D.9), the pseudo-dynamic (Chopra & Tan 1989) HSS-support-
    acceleration amplification method (Eq 4.4/4.6/D.8, Table 4.2, Eq D.10),
    and the dam-period estimate (Eq D.11/D.12) -- fully validated against
    Appendix D's own two-variant worked example (ac = 1.6g / 1.3g). Flags
    two source-document inconsistencies (Table 4.2's "Equation 4.7"
    citation and Eq 4.4's unused "C" correction factor) resolved by
    verifying against that worked example.
  - ``fatigue_fracture.py`` -- Chapter 5: the fatigue load factor (finite
    vs. infinite life, Table 4.1 footnote 5), the fatigue-check screening
    rule (paragraph 5.1.3), and the fracture-critical-member redundancy
    strength check (paragraph 5.2.1.2). This chapter is mostly qualitative
    guidance deferring to AISC 360/AASHTO detail categories -- these are
    its only printed numeric criteria.
  - ``connections.py`` -- Chapter 6: bolt-grade and welding-code selection
    rules, and faying-surface preparation classes. Entirely qualitative
    guidance in this manual (no numeric bolt/weld capacity equations are
    printed; AISC 360/RCSC S348 govern by reference) -- these lookups
    digitize the chapter's few enumerable selection RULES.
  - ``tainter_gate_loads.py`` -- Chapter 10 + Appendix F: side-seal
    friction (Eq 10.1/F.1), the wire-rope tangent and wrap load cases
    (Eq F.4-F.6), hydrostatic load on the skin plate by direct integration
    (Eq F.9-F.15) and by simplified projection (Eq F.16), trunnion-pin
    friction resolution (Eq F.17), the full spillway-Tainter-gate strength
    load-combination table (Eq 10.2-10.14), the trunnion-girder anchorage
    shear-friction check (Eq 10.15), and Chapter 10's nominal loads/
    serviceability limits (ice/debris/barge impact loads, girder and skin-
    plate deflection limits, skin-plate thickness bounds). Fully validated
    against Appendix F's own worked example (Tables F.1-F.7); flags and
    resolves two sign/citation issues found while verifying that example.
  - Structured reference text via ``geotech_references._retrieval``
    (``text/chapterNN.json``, chapters 1-6) and a figure catalog
    (``figures_catalog.json``, all 114 figures in the manual's own Figure
    List, 100% page-confirmed directly against body-page captions -- not
    caption-search-estimated).

UNITS: this manual is US-customary native (kips, feet, inches, psi/ksi,
pcf/kcf). Values are kept in source units per repo convention.

Worked-example validation (module tests, doctrine: reproduce published
numbers, never tune): Appendix D's seismic-amplification example (Steps
1-5, printed pp. 399-402: ac = 1.6g using peak spectral acceleration, and
ac = 1.3g / T = 0.35 sec using the period estimate); Appendix F's Tainter-
gate load example (Tables F.1-F.7, printed pp. 437-445: side-seal friction
Fs = 6.74 kips, hydrostatic-by-integration P/Ph/Pv = 53.85/50.0/15.081
kips, Mh = Mv = 533.33 kip-ft, Yp/Xp = 10.67/35.36 ft, wire-rope Q = 68.89
kips, trunnion reaction Rt = 1385 kips, Ft = 415.3 kips, Mt = 207.7 kip-ft).

Usage::

    from geotech_references.em_2107.loads import (
        required_strength_check, table_4_1_load_factor, load_combination_lrfd,
    )
    from geotech_references.em_2107.seismic_amplification import hss_support_acceleration
    from geotech_references.em_2107.tainter_gate_loads import (
        side_seal_friction_force, hydrostatic_radial_force, trunnion_friction_force,
    )
    from geotech_references._retrieval import retrieve_section, search_sections
"""
