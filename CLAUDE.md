# geotech-references

> **Open work for this repo is tracked in ONE list: `BACKLOG.md` in the
> GeotechStaffEngineer repo** (§8, REF-nn; this repo is its submodule at
> `geotech-references/`). Add new to-dos there with the next free ID, never as
> a list in this file. Backlog, TODO and "follow-up" notes further down are
> history (owner's rule, 2026-10-12).

Standalone geotechnical reference library: digitized equations, figures, tables, and structured reference text from UFS 3-220-10 (DM 7.1, 16 January 2026) and UFC 3-220-20 (DM 7.2, 16 January 2025), the successors to NAVFAC DM 7.01/7.02, FHWA GEC series, and other standards.

**Two complementary components per reference:**
1. **Python lookup scripts** (`tables.py`, `figures.py`, sometimes `equations.py`) — Digitized design charts, tables, and equations as callable functions. Written manually by Claude Code from the source PDFs.
2. **Structured reference text** (`text/chapterNN.json`) — Each chapter as a JSON file with sections containing `body`, `key_points`, `equations`, `figures`, `tables`, and `applicability` fields. Also written manually by Claude Code across sessions (not auto-generated — the `build_chapter_text.py` pipeline was retired after the $20/reference cost incurred on DM7).

Consumed by [GeotechStaffEngineer](https://github.com/soconnell345-geotech/GeotechStaffEngineer) as a Git submodule.

## Architecture

```
geotech_references/           # Python package (pip install -e .)
  _interpolation.py            # Shared helpers (_linterp)
  _plotting.py                 # Shared matplotlib helpers (get_pyplot, setup_engineering_plot)
  _retrieval.py                # Reference text retrieval (load, search, retrieve by section) at every section level; section_entries() = the one section tree both layers use; fit_hits() / fit_record() shape a result to a caller's max_chars. See "Section levels" and "Results that fit a size limit" below.
  _retrieval_db.py             # SQLite FTS5 retrieval layer — reference_search / reference_get / reference_query (v1.2.0); one row per section at every level (REF-24)
  _figures_db.py               # SQLite FTS5 figure-catalog retrieval — figure_search / figure_get / resolve_pdf
  _query_expansion.py          # Synonym query-expansion recall lever for reference_search/figure_search; EXPANSION_STRATEGY off/fill/rerank/auto (env GEOTECH_RETRIEVAL_EXPANSION, default auto). See "Lexical Query Expansion" below.
  dm7_1/                       # UFS 3-220-10 Soil Mechanics (DM 7.1), 16 Jan 2026 (8 chapters)
    chapter1.py ... chapter8.py
    text/                      # Structured chapter JSON (8 chapters, 457 sections, 2026-04-07)
    figures_catalog.json       # 223 figures (number, caption, page, text-enriched description)
  dm7_2/                       # UFC 3-220-20 Foundations & Earth Structures (7 chapters)
    prologue.py, chapter2.py ... chapter7.py
    text/                      # Structured chapter JSON (prologue + 6 chapters, 438 sections, 2026-04-07)
    figures_catalog.json       # 252 figures (incl. P-* prologue, B-* appendix; e.g. Fig 4-12 log-spiral Ka/Kp)
  gec_6/                       # FHWA-SA-02-054 Shallow Foundations
    tables.py, figures.py
    text/                      # Structured chapter JSON (10 chapters, body-only — manifest ready for full-schema re-extraction)
  gec_7/                       # FHWA-NHI-14-007 Soil Nail Walls
    tables.py                  # 13 table lookup functions (bond, pullout, resistance factors, seismic)
    figures.py                 # 2 figure lookup functions (friction angle vs SPT, basal heave Nc)
    text/                      # Structured chapter JSON (ch 1-5, ~37 sections, body-only; ch 6-10 not yet extracted — manifest ready)
  gec_10/                      # FHWA-NHI-18-024 Drilled Shafts (2018 edition)
    tables.py, figures.py      # 2018 edition: Table 8-4/9-1/10-2/11-1, Figure 10-6, Eq 10-21/22
    text/                      # All 18 chapters complete (FHWA-NHI-18-024, ch 1-18)
  gec_11/                      # FHWA-NHI-10-024 Design of MSE Walls & Slopes
    tables.py, figures.py
    text/                      # All 11 chapters complete (FHWA-NHI-10-024, ch 1-11)
  gec_12/                      # FHWA-NHI-16-009 Driven Piles
    tables.py                  # 8 table lookup functions (resistance factors, beta/Nt, setup, API)
    figures.py                 # 8 figure lookup functions (Nordlund Kd, CF, alpha_t, N'q, adhesion)
    text/                      # Structured chapter JSON (Vol I ch 1-8 only, ~109 sections, body-only; Vol II ch 9-18 not yet extracted — manifests ready)
  gec_13/                      # FHWA-NHI-16-027 Ground Modification Methods
    tables.py, figures.py
    text/                      # Structured chapter JSON (5 chapters, body-only — manifest ready for full-schema re-extraction)
  micropile/                   # FHWA-NHI-05-039 Micropile Design & Construction
    tables.py                  # 13 table lookup functions (bond stress, pipe/rebar, elastic modulus)
    figures.py                 # 1 figure lookup function (limiting lateral modulus)
    text/                      # Structured chapter JSON (10 chapters, 70 sections, complete)
  fema_p2192/                  # FEMA P-2192 Seismic Design Category (2024) — text extraction skipped (separate ASCE 7 effort)
    tables.py                  # 10 functions (SDC, site class, Fa/Fv, risk category)
  noaa_frost/                  # NOAA Frost Protected Shallow Foundations — being superseded by USACE TM 5-852-4 (pending)
    equations.py               # 5 physics equations (Stefan, Berggren, latent heat)
    tables.py                  # 4 soil thermal property lookups
  ufc_backfill/                # UFC 3-220-04N Backfill for Subsurface Structures — text extraction skipped (content covered by DM7)
    equations.py               # 3 equations (compaction pressure, filter criteria, RC check)
    tables.py                  # 5 tables (compaction, material, lift, equipment, drainage)
  ufc_dewatering/              # UFC 3-220-05 Dewatering and Groundwater Control
    equations.py               # 6 equations (Thiem, Dupuit, Sichardt, superposition)
    tables.py                  # 3 tables (permeability, method selection, screen slot)
  ufc_expansive/               # UFC 3-220-07 Foundations in Expansive Soils
    equations.py               # 5 equations (activity, free swell, swell pressure, heave, pier)
    tables.py                  # 4 tables (swell potential, active zone, foundation, void space)
  ufc_pavement/                # UFC 3-250-01 (2016) Pavement Design for Roads & Parking — REBUILT 2026-07 from the real doc (audit gap CLOSED): CBR curve E-1, rigid Eq 13-1, overlays, frost, drainage
  ufc_stabilization/           # UFC 3-250-11 (2020) Soil Stabilization (additive selection, criteria, equivalency)
  ufc_flexible_practice/       # UFC 3-250-03 (2018) Flexible Pavement Practice (HMA/Marshall/Superpave, sprays, seals)
  ufc_concrete_practice/       # UFC 3-250-04 (2024) Concrete Pavement Practice (materials, dowels, joints, RCC)
    equations.py               # 4 equations (CBR-to-k, flexible/rigid thickness, ESWL)
    tables.py                  # 5 tables (frost susceptibility, reduction, aircraft, layers, subgrade)
scripts/                       # Content generation tools (NOT installed with the package)
  build_figure_catalog.py      # PDF "List of Figures" → <pkg>/figures_catalog.json (no API; PyMuPDF text parse). Resolves each figure to its PDF page via caption-search; enriches descriptions from chapter text. Run: python scripts/build_figure_catalog.py dm7_1 dm7_2
  build_chapter_text.py        # DEPRECATED: PDF → chapter JSON pipeline (Anthropic API); discontinued — too costly ($20/reference on DM7). Chapter JSON files are now authored manually by Claude Code across sessions.
  audit_chapter_text.py        # Validate generated JSON (schema, eq coverage, implemented_in links)
  check_section_numbers.py     # Chapter JSON section numbers vs the printed PDF (outline + page headings; no API). --detail lists what needs a reader, --apply writes only definite renumberings (section_id values only). Test: tests/test_section_numbers.py (skips without the PDFs). REF-23
  eval_subsection_retrieval.py # 14 questions answered in a subsection (8 references): replays search -> fetch, reports recall@5 and characters read; --titles --save/--compare = the ranking guard (top-level sections found by their own title). Test: tests/test_subsection_retrieval.py. REF-24
  chapter_schema.json          # JSON schema for chapter files
  manifests/                   # Per-reference manifest files (chapter page ranges + PDF paths)
    dm7_1.json, dm7_2.json     # DM7 — page ranges pre-filled
    gec_6.json, gec_7.json, gec_10.json, gec_11.json  # GECs — page ranges pre-filled
    gec_12_v1.json, gec_12_v2.json, gec_13.json       # GECs — page ranges pre-filled
  README.md                    # Pipeline usage guide (describes deprecated build_chapter_text.py approach)
agents/
  dm7_agent.py                 # DM7 Foundry-style 3-function wrapper
  gec6_agent.py                # GEC-6 Foundry-style 3-function wrapper
  gec7_agent.py                # GEC-7 Foundry-style 3-function wrapper
  gec10_agent.py               # GEC-10 Foundry-style 3-function wrapper
  gec11_agent.py               # GEC-11 Foundry-style 3-function wrapper
  gec12_agent.py               # GEC-12 Foundry-style 3-function wrapper
  gec13_agent.py               # GEC-13 Foundry-style 3-function wrapper
  micropile_agent.py           # Micropile Foundry-style 3-function wrapper
  fema_p2192_agent.py          # FEMA P-2192 Foundry-style 3-function wrapper
  noaa_frost_agent.py          # NOAA Frost Foundry-style 3-function wrapper
  ufc_backfill_agent.py        # UFC 3-220-04N Foundry-style 3-function wrapper
  ufc_dewatering_agent.py      # UFC 3-220-05 Foundry-style 3-function wrapper
  ufc_expansive_agent.py       # UFC 3-220-07 Foundry-style 3-function wrapper
  ufc_pavement_agent.py        # UFC 3-250-01 Foundry-style 3-function wrapper (agent references UFC 3-260-02 — update when equations.py/tables.py are audited)
tests/                         # 3,529 tests (pytest)
docs/                          # Source PDFs (UFC/GEC/micropile/pavement) — used by build_figure_catalog.py and figure read-off
references/                    # (legacy) source PDFs (git-ignored)
```

## Key Conventions

- **All units SI**: meters, kPa, kN, degrees (GEC-12 figures use original units: ksf, tsf, ft)
- **No external dependencies** beyond Python stdlib + numpy/scipy (optional matplotlib for plots)
- **Function naming**: `figure_X_Y_*()` for figures, `table_X_Y_*()` for tables — matches reference numbering
- **Private data**: `_TABLE_*`, `_FIG_*` prefixed dicts/lists
- **Dict keys**: snake_case, lowercase (`.lower().strip()` applied on input)
- **Shared helpers**: `_linterp` in `_interpolation.py` (was duplicated in 5 chapters)
- **Plot functions**: `plot_figure_*()` with `(ax=None, show=True, **kwargs)` signature

## DM7 Inventory (382 functions, 2,008 tests)

| Module | Chapter | Topic | Functions | Tests |
|--------|---------|-------|-----------|-------|
| dm7_1 | 1 | Identification & Classification | 24 | 174 |
| dm7_1 | 2 | Field Exploration & Testing | 20 | 97 |
| dm7_1 | 3 | Laboratory Testing | 18 | 109 |
| dm7_1 | 4 | Distribution of Stresses | 17 | 90 |
| dm7_1 | 5 | Consolidation & Settlement | 42 | 232 |
| dm7_1 | 6 | Seepage & Drainage | 19 | 82 |
| dm7_1 | 7 | Slope Stability | 10 | 44 |
| dm7_1 | 8 | Correlations for Soil Properties | 35 | 143 |
| dm7_2 | Pro | Prologue — Index Properties | 12 | 111 |
| dm7_2 | 2 | Earth Pressures | 26 | 147 |
| dm7_2 | 3 | Shallow Foundations | 22 | 120 |
| dm7_2 | 4 | Deep Foundations | 42 | 195 |
| dm7_2 | 5 | Bearing Capacity (Deep) | 62 | 271 |
| dm7_2 | 6 | Retaining Structures | 37 | 122 |
| dm7_2 | 7 | Slope Stability (Earth Structures) | 16 | 71 |

## GEC Module Inventory

| Module | Reference | Functions | Tests | Text Chapters |
|--------|-----------|-----------|-------|---------------|
| gec_6 | FHWA-SA-02-054 Shallow Foundations | 13 | 121 | 10 chapters body-only; manifest ready |
| gec_7 | FHWA-NHI-14-007 Soil Nail Walls | 15 | 101 | ch 1-5 body-only; ch 6-10 pending |
| gec_10 | FHWA-NHI-18-024 Drilled Shafts (2018) | 12 | 195 | All 18 chapters complete (ch 1-18) |
| gec_11 | FHWA-NHI-10-024 MSE Walls & Slopes | 17 | 130 | All 11 chapters complete (ch 1-11) |
| gec_12 | FHWA-NHI-16-009 Driven Piles | 16 | 147 | Vol I (ch 1-8) body-only; Vol II (ch 9-18) pending |
| gec_13 | FHWA-NHI-16-027 Ground Modification | 18 | 168 | All 10 printed chapters (Vol I ch 1-5, Vol II ch 6-10); ch 3-10 rebuilt from the print 2026-10-19 (REF-25) |
| micropile | FHWA-NHI-05-039 Micropile Design | 14 | 108 | 10 chapters (complete) |
| fema_p2192 | FEMA P-2192 SDC Determination (2024) | 10 | 132 | - |
| noaa_frost | NOAA Frost Protected Shallow Foundations | 9 | 86 | - |
| ufc_backfill | UFC 3-220-04N Backfill | 8 | 87 | - |
| ufc_dewatering | UFC 3-220-05 Dewatering | 9 | 75 | - |
| ufc_expansive | UFC 3-220-07 Expansive Soils | 9 | 55 | - |
| ufc_pavement | UFC 3-250-01 Roads/Streets/Walks/Storage (**NOTE: equations.py/tables.py still from UFC 3-260-02 airfield — pending audit**) | 9 | 54 | - |
| eurocode_7_1 | EN 1997-1:2004 Eurocode 7 Part 1 General Rules (Annex A partial factors, DA1-DA3, Annex C/D/E/F/G/H methods) | 31 | 134 | All 21 chapters (Sections 1-12 + Annexes A-J) |
| eurocode_7_2 | EN 1997-2:2007 Eurocode 7 Part 2 Ground Investigation (CPT/PMT/SPT/DP/FVT/DMT/PLT correlations) | 43 | 133 | 9 chapters (body + all annexes) |
| aashto_1993 | AASHTO 1993 Pavement Design Guide (flexible SN / rigid D equations, layer coefficients, reliability; FULL Appendix D LEF tables D.1-D.18 in lef.py — closed-form equations are in Volume 2 Appendix MM, NOT in this scan; Section 3.2 composite-k worksheet in composite_k.py, chart-read; Appendix G swell/frost-heave loss + Table 3.1 performance-period iteration in environmental.py; scanned source read visually; US units) | ~45 | 308+ | 11 chapters (Part I-II full, III/IV stubs) |
| em_2104 | EM 1110-2-2104 Strength Design for Reinforced Concrete Hydraulic Structures (1 Nov 2023 ed., published 8 Jan 2025) — load inventory + full Table 3-2 load-factor table + LRFD/earthquake load combinations (loads.py); serviceability service-stress/single-load-factor/reinforcement-limit provisions (serviceability.py); Chapter 2 detailing incl. temp/shrinkage steel (reinforcement.py); the complete Appendix B flexure+axial INVESTIGATION equations for singly/doubly reinforced, tension+flexure, and pure-flexure members incl. numerically-solved cubics (flexure_axial.py); the complementary Appendix D-2 DESIGN equations (design.py); Chapter 5 shear incl. the pre-ACI-318-19 equation deliberately retained for RCHS per Appendix G commentary (shear.py); US units | ~50 | 190+ | 5 chapters (1-5) full; Appendix B-G implemented as Python lookups, not re-narrated text |
| em_2107 | EM 1110-2-2107 Design of Hydraulic Steel Structures (1 Aug 2022 ed.) — does NOT reprint AISC 360 member-capacity equations (member design is by direct AISC 360 reference); LRFD loads/full Table 4.1 load-factor table/load combinations + earthquake combinations (loads.py); HSS-support seismic-acceleration amplification incl. the full Appendix D pseudo-dynamic (Chopra & Tan 1989) derivation, validated against its own 2-variant worked example (seismic_amplification.py); Table 3.1 target reliability + usual/unusual/extreme load categories (design_basis.py); fatigue screening + fracture-critical redundancy check (fatigue_fracture.py); bolt/weld/faying-surface selection rules (connections.py); Chapter 10 + Appendix F Tainter-gate load equations — side-seal friction, wire-rope loads, hydrostatic load by integration + simplified projection, trunnion friction, full Eq 10.2-10.14 load-combination table, anchorage shear-friction (tainter_gate_loads.py), fully validated against Appendix F's own worked example (2 source-document sign/citation errors found and resolved by cross-verification); US units | 49 | 103 | 6 chapters (1-6) full; Chapters 9-16/Appendices B/C gate-geometry content intentionally thin per scope (closed-form Appendix D/E/F content fully covered instead) |
| ufc_structural | UFC 3-301-01 Structural Engineering (DoD, 11 Apr 2023, thru Change 4 3 Jun 2025) — DoD modifications ONLY (adopts 2024 IBC/ASCE 7-22 baseline, does not reprint civilian-code content this UFC doesn't itself modify); risk category Table 2-2 (adds DoD Risk Category V + Sea Level Rise column, REPLACES IBC Table 1604.5/ASCE 7-22 Tables 1.5-1/1.5-2) + wind deflection Table 2-1 + wind-speed conversion Eq 16-18a/b (risk_category_and_loads.py); the FULL Table 3-1 seismic-system replacement for ASCE 7-22 Table 12.2-1 (92 systems, categories A-H) + Table 7-1 critical-healthcare permitted-systems subset + Table B-1 Risk-Category-IV alternate-design permitted-systems table (seismic_force_resisting_systems.py); additional vertical-ground-motion seismic load combinations (Eq under 2.3.6/2.4.5), Appendix B RC IV combinations (Eq B-1/B-2), coupling-beam capacity-design shear check, healthcare structural-separation Eq 12.12-1 (seismic_load_combinations.py); Chapter 4 Table 4-1(a)/(b) performance-objective lookups (Table 4-1(a)'s RC I/II and III cells preserved as literal printed text — genuine cell-merge/footnote ambiguity in the source, documented) + trigger cost thresholds + IEBC high-wind roof-diaphragm trigger (evaluation_retrofit.py); Chapters 6/7 healthcare Table 6-1 masonry thickness + structural-configuration/elevator criteria (healthcare_modifications.py); Chapter 5 nonbuilding-structure standard pointers (nonbuilding_structures.py); Appendix C rigid-pipe span Tables C-1/C-2/C-3 + Eq C-1 + elevator/partition/certification criteria (nonstructural_seismic.py); Appendix G GFRP Table G-1 + DoD-specific seismic/fire/durability limits (gfrp.py); Appendix A best-practice guidance + embedded numeric criteria (best_practices.py); Chapter 1 legend/progressive-collapse/RC-V pointers (general_provisions.py). Table 4-2 (benchmark-building code-vintage cross-reference) and Appendices F/H/I NOT digitized (administrative/narrow-scope, no design equations — see package docstring); US units | 66 | 200 | 7 chapters (1-7) full; Appendices A-D/G implemented as Python lookups, not re-narrated text |

### GEC-7: Soil Nail Walls (15 functions, 101 tests)

**Table Functions** (13): Bond strength coarse/fine-grained soils & rock (Tables 4.4a/b, 4.5), pullout resistance, ASD factors of safety, LRFD resistance factors (Tables 5.4-5.11), AASHTO seismic site coefficients (F_PGA, F_v), SPT correlations, elastic properties, wall displacement parameters

**Figure Functions** (2): Friction angle vs SPT N60 (Fig 4.3), basal heave Nc (Fig 5.11)

### GEC-10: Drilled Shafts — FHWA-NHI-18-024 (12 functions, 195 tests)

**Figure/Equation Functions** (5): Alpha adhesion factor for cohesive side resistance (Fig 10-6, Chen 2011 formula α=0.30+0.17/(su/pa)); UU→CIUC and UC→CIUC strength conversion (Eq 10-16/17, Chen & Kulhawy 1993); rock socket side resistance for normal sockets (Eq 10-21, C=1.0 normalized); rock socket side resistance for caving/fractured rock (Eq 10-22 + Table 10-3 αE reduction factors by RQD and joint condition)

**Table Functions** (7): LRFD resistance factors by limit state and geomaterial (Table 8-4, compression vs. uplift keys); lateral resistance factors for p-y pushover (Table 9-1); N*c bearing capacity factor for base resistance in cohesive soil (Table 10-2, su-keyed); p-multipliers for lateral group analysis (Table 11-1, 0.70/0.50/0.35 at 3D); group axial efficiency for cohesionless soils (AASHTO 10.8.3.6.3, 0.65/0.80/1.0 at 2.5D/3D/4D+); LRFD reliability index β ↔ pF

**Text**: All 18 chapters (FHWA-NHI-18-024, 2018 edition) — construction methods (ch 1-7), design process (ch 8), lateral and axial design (ch 9-10), group design (ch 11), structural design (ch 12), load tests (ch 13), specifications/inspection/integrity/acceptance/cost (ch 14-18)

### Micropile: FHWA-NHI-05-039 (14 functions, 108 tests)

**Table Functions** (13): Grout-to-ground bond stress alpha_bond by soil/rock type & micropile type A/B/C/D (Table 5-3), pipe casing properties API N-80 & ASTM A519/A106 (Table 4-5), reinforcing bar properties (Table 4-2), classification system (Table 2-1), group efficiency (Table 5-4), corrosion criteria (Table 5-5), epsilon_50 for clays (Tables 5-7/5-8), soil modulus k for sand/clay (Tables 5-9/5-10), fixity guidance (Table 5-11), elastic modulus by soil type & SPT (Tables 5-12/5-13)

**Figure Functions** (1): Limiting lateral modulus for buckling (Fig 5-23)

### GEC-12: Driven Piles (16 functions, 147 tests)

**Figure Functions** (8): Nordlund Kd, CF correction factor, limiting toe resistance, alpha_t coefficient, N'q bearing capacity, delta/phi ratio, adhesion Ca, adhesion factor alpha

**Table Functions** (8): Resistance factors static/field, static analysis methods, API design parameters, beta/Nt coefficients, Brown's method factors, Eslami-Fellenius Cs, soil setup factors

**Text Retrieval**: `retrieve_section(reference, section_id, include_subsections=False)`, `search_sections(reference, query, limit=None, offset=0, max_chars=None)`, `list_chapters(reference, chapter=None, sections=True, max_chars=None)`, `load_chapter(reference, chapter, max_chars=None)` — every level, e.g. `retrieve_section("gec_12", "7.2.1.3.1")` (see "Section levels"; `max_chars` in "Results that fit a size limit")

**Structured Text**: 8 chapters (Ch 1-8 of Vol I), 109 top-level sections plus 76 nested in `subsections` (chapter 7: the static methods, group efficiency, uplift, setup, settlement, p-y), with title, body, key_points, equations, figures, tables, and applicability fields

### GEC-11: MSE Walls & Reinforced Soil Slopes — FHWA-NHI-10-024 (17 functions, 130 tests)

**Table Functions** (16): Minimum reinforcement length and embedment depth (Tables 2-1/2-2); select fill gradation (Table 3-1); electrochemical limits for steel and geosynthetics (Tables 3-3/3-4); pullout parameters Ci and F* (Table 3-6); galvanization thickness and corrosion rates (Tables 3-7/3-8); installation damage reduction factors (Table 3-9); PET durability (Table 3-11); LRFD load combinations and permanent load factors (Tables 4-1/4-2); traffic surcharge (Table 4-4); external resistance factors (Table 4-5); bearing capacity factors (Table 4-6); internal resistance factors (Table 4-7)

**Figure Functions** (1): Kr/Ka lateral stress ratio vs depth (Fig 4-10)

**Text**: All 11 chapters (Vol I ch 1-6: overview through design of MSE walls; Vol II ch 1-5: RSS design, construction, and inspection)

### GEC-13: Ground Modification Methods — FHWA-NHI-16-027 (18 functions, 168 tests)

**Table Functions** (12): Technology applicability by category/soil (Table 1-2); technologies by function (Table 1-3); comparative unit costs (Table 1-6, 2016 $); PVD transportation applications (Table 2-1); lightweight fill material properties (Table 3-1); DDC design parameters (Table 4-1); deep mixing typical qu by soil/method (Table 7-2); jet grouting system comparison (Table 8-2); soil nail bond strength by soil type (Table 9-2); micropile bond zone unit resistance Types A/B/C-D (Table 10-1); geosynthetic reduction factors RF_ID/RF_CR/RF_CBD by polymer (Table 11-1)

**Figure/Equation Functions** (6): Vibro-compaction soil suitability number (Fig 4-3, Brown 1977 SN formula); aggregate column area replacement ratio (Fig 5-2, triangular/square pattern); stone column settlement improvement factor (Fig 5-5, Priebe 1995 SRF formula); deep mixed zone composite modulus (Eq 7-4, parallel model); groutability ratio for permeation grouting (Eq 8-1, N = D15_soil/D85_grout); long-term design strength for geosynthetics (Eq 11-1, LTDS = T_ult/RF_product)

**Text**: The 10 printed chapters — Vol I ch 1-5 (Introduction, PVDs and Fill Preloading, Lightweight Fills, Deep Compaction, Aggregate Columns); Vol II ch 6-10 (Column-Supported Embankments, Deep Mixing and Mass Mixing, Grouting, Pavement Support Stabilization Technologies, Reinforced Soil Structures). Section ids are '<chapter>.<printed local number>' ('5.4.1.2.2'), since the print restarts its numbers in each chapter. Ch 3-10 were rebuilt from the print on 2026-10-19 (REF-25): the earlier files were written from memory, and their chapters 9-11 (Soil Nailing, Micropiles, Geosynthetic Reinforcement) were not the manual's.

## Figure Retrieval & Vision Read-Off

A third access modality alongside Python lookups and chapter text: **find an
engineering chart by meaning, then read a value off it with a vision model** —
giving coverage of figures that have not been hand-digitized into `figures.py`.

- **Catalog** (`<pkg>/figures_catalog.json`, committed): built by
  `scripts/build_figure_catalog.py` from the PDF's "List of Figures". Each entry
  has `figure_number`, `caption`, `chapter`, 0-based `pdf_page_index` (resolved
  by searching the body for the caption's own page), `printed_page`, and a
  `description` cross-linked from the chapter text (so concept queries like
  "passive earth pressure" hit Fig 4-12 even though its caption only says
  "K_A and K_P for the Log Spiral Method"). No API cost.
- **Retrieve** (`_figures_db.py`, FTS5 lazy temp DB, mirrors `_retrieval_db.py`):
  `figure_search(query, reference, chapter, limit)` (BM25, with synonym
  query-expansion + an OR-of-terms recall fallback — see "Lexical Query Expansion"),
  `figure_get(reference, figure_number)`, `resolve_pdf(...)`
  → `(pdf_abs_path, page_index)`, `list_indexed_figures()`.
- **Read off** (in GeotechStaffEngineer): the `read_reference_figure` vision tool
  renders the resolved page at 220 DPI and asks the engine to read the value(s).
  Results are **read-off estimates** to be verified, not exact digitized values.

Built for DM7 (`dm7_1`: 223 figures, `dm7_2`: 252). Run the same script per
reference to extend. Source PDFs live in `docs/`.

## Section levels (REF-24): every section is addressable

A chapter file holds its levels two ways: GEC-12 nests subsections inside
their section (`subsections`, 76 of them), every other reference lists each
level as its own entry (`5-5`, `5-5.2`, `5-5.2.1`). `_retrieval.section_entries`
reads both into one tree — a nested section sits under its container, a flat
one under the nearest section of the same file whose number is a prefix of
its own (`7.3.2.1` under `7.3` where there is no `7.3.2`) — and both layers use it.

- **Indexed at every level, own text only.** `_retrieval_db` has one row per
  section (3,884 rows), each with its own body, never its subsections', so a
  search hit is the section that holds the words: "Nordlund" finds GEC-12
  7.2.1.3.1, not only 7.2. Rows carry `parent_rowid`, `depth`, `parents_json`;
  `PRAGMA user_version` = `_SCHEMA_VERSION` (2), and a database built by an
  older version is rebuilt on first use whatever its mtime.
- **Results say where a section sits.** Search hits (both layers) carry
  `parent_id` and `under` (`"7.2 Strength Limit States > 7.2.1 Nominal Axial
  ..."`). `reference_get` / `retrieve_section` work on any number and add
  `children` (number + title of each section directly under it).
- **A parent is NOT inlined by default.** Before REF-24 `retrieve_section`
  returned a section with its whole subtree: GEC-12 7.2 was 28,490 characters,
  so the app's 16,000-character reference cap cut it mid-JSON and 7.2.2-7.2.10
  were never seen; reaching a 2 k subsection cost ~18 k characters. Now the
  parent comes back with its own text and `children`, and the librarian
  fetches the child it needs. `include_subsections=True` (both layers) still
  inlines the subtree, only when the whole result fits
  `SUBSECTIONS_INLINE_MAX_CHARS` (12,000, under the app cap); past that it
  returns `children` and a `note`. Largest single fetch in the library: 13,734
  characters (dm7_1 1-3.6, its own body).
- **A missing number** in `reference_get` or plain `retrieve_section`
  raises `KeyError` naming the nearest section above it and up to eight
  sections numbered under it (`7.2.1.3` -> 7.2.1 and 7.2.1.3.1 Nordlund
  ...); both word it the same way (`_retrieval.nearby_note`; REF-26).
- **`list_chapters`** lists nested sections too, each with `parent_id`; a
  reference that lists its levels flat keeps the shape it had.
- **Ranking is unchanged** (BM25, equal column weights). Measured
  (`scripts/eval_subsection_retrieval.py`, 2026-10-18): the 14 subsection
  questions went from recall@5 7/14 (GEC-12 0/7) and 10/14 reached (GEC-12
  three, each through a 16 k-cut fetch, ~18 k characters) to 14/14 and 14/14,
  each one search plus one fetch of 1.1-6.9 k characters. Of 2,260 top-level
  sections their own title found first, 3 no longer are (two lose to a nested
  GEC-12 subsection, one a near-tie that moved with the new rows' term
  statistics). A title weight in BM25 was tried and rejected: at 2x it changed
  462 first hits library-wide and still lost those two. The cross-reference
  eval (`eval_retrieval_recall.py`) went from 4/9 to 3/8 trusted cases under
  `auto`: GEC-12 7.2.10 "Downdrag" now outranks the dm7_2 target for "downdrag
  drag load on pile", and the canonical "liquefaction triggering" now has
  GEC-12 7.4.2 first, whose title fails the eval's gate; top-1 disturbance
  stays 0/10 (`auto`).
- **Tests:** `tests/test_subsection_retrieval.py`.

## Results that fit a size limit (REF-26)

The app sends its agent at most 16,000 characters of a reference tool's
result and cuts the rest, which leaves broken JSON. Before REF-26 the
largest results were: `list_chapters` 27,820 (ufc_concrete_practice; three
references over), `search_sections` 708,876 ("a"; "pile" in GEC-12 317,437),
`load_chapter` 206,140, `reference_search` at 50 hits 36,424,
`reference_query` 258,786, `figure_search` at 50 hits 68,859, `figure_get`
30,444 (a catalog caption that ran on into the page text). Every function
that can return that much now takes an optional **`max_chars`** and, given
it, returns a shape that fits and says how to get the rest. Without it each
returns exactly what it always did; the app passes 14,000.

- **`list_chapters(reference, chapter=None, sections=True, max_chars=None)`**:
  every chapter carries `n_sections`; `sections=False` leaves the sections
  out (largest listing 3,122); `chapter=N` lists one chapter (a missing one
  raises `KeyError` naming the chapters there are); with `max_chars` a
  chapter whose section list does not fit lists its top-level sections with
  `n_subsections` and a `note`. The app's `list_chapters` without a chapter
  returns the full listing when it fits its 14,000 characters (22 of 27
  references) and the chapters alone with a note otherwise.
- **`load_chapter(reference, chapter, max_chars=None)`**: a chapter over the
  limit (147 of 291 are over 14,000) comes back as its outline
  (`chapter_outline`: the chapter's fields, `n_sections`, each section's
  number, title and place) with `chapter_chars` and a note to fetch sections
  with `retrieve_section`.
- **`search_sections(reference, query, limit=None, offset=0, max_chars=None)`**:
  the plain call still returns whole sections (unchanged); with `max_chars`
  each hit is the section's number, title, chapter, `parent_id`, `under` and
  a 300-character `snippet` from where the words first appear, and the
  result is `{"hits", "shown", "total_hits"}`.
- **`reference_search` / `figure_search` gain `offset` and `max_chars`**;
  with `max_chars` the result is the `fit_hits` dict. A plain call runs the
  same SQL as before; a paged or fitted one asks for `offset + limit + 1`
  rows and slices, and its first page lists the same hits in the same order
  as the plain call (checked over 144 queries). `offset` goes no higher than
  500 (`_MAX_OFFSET`): past it the result is an error saying to narrow the
  query, and a page whose next hits would start past it says so instead of
  offering `next_offset` (`fit_hits(max_offset=)`).
- **`reference_query(sql, limit=50, max_chars=None)`** keeps whole rows that
  fit (`{"rows", "shown", "left_out", "note"}`); a first row that alone does
  not fit comes back with its longest values cut and named, and one that
  still does not fit (very many columns) is an error saying to select fewer
  columns; the note says to raise the SQL's OFFSET by the rows shown.
  **`figure_get(...,
  max_chars=None)`** cuts a caption / description that ran on, with a note.
- **The shared rules** are in `_retrieval`: `fit_hits` (cut the hits' text
  fields to `HIT_TEXT_CHARS` 300 first, then leave out the lowest-ranked
  hits; `left_out`, `next_offset` and a `note` saying how to get the rest)
  and `fit_record` (cut a record's longest text fields, never below 200).
- **Section fetches are not shaped**: the largest (`reference_get` dm7_1
  1-3.6, 13,783; `retrieve_section` gec_12 8.5.2, 13,074) fit by their data.
  The app's guard test walks every reference method and fails if that
  changes (`funhouse_agent/tests/test_reference_result_sizes.py`).
- **Tests:** `tests/test_result_size.py`.

## Lexical Query Expansion (recall lever)

> Status: built + tested on branch `ref-retrieval-expansion` (2026-06-08),
> **uncommitted** — a master-level agent owns the merge. Default is ON (`auto`).

Both FTS5 retrieval layers (`reference_search` for text, `figure_search` for
figures) are lexical (BM25 + porter stemming), which closes *morphological* gaps
("pressures"→"pressure") but **not** *synonym* gaps ("interface friction" vs
"wall friction"/δ; "bored pile" vs "drilled shaft"). `_query_expansion.py` adds a
curated, dependency-free table of geotechnical term-equivalence groups and applies
it as a recall lever. This is the **cheaper alternative to text embeddings** (see
the GeotechStaffEngineer HANDOFF P6); image embeddings remain rejected.

- **`expand_query(q)`** → an FTS5 `OR` clause of synonym surface forms not already
  in `q` (or `""` if no group matches). **`combined_query(q)`** → `"(q) OR <syns>"`.
- **`EXPANSION_STRATEGY`** (module global; env `GEOTECH_RETRIEVAL_EXPANSION`;
  default `auto`):
  - `off` — pure literal.
  - `fill` — append synonym hits only to empty result slots (precision-safe, but
    the eval shows ~0 recall lift — the win comes from re-ranking, not filling).
  - `rerank` — BM25 over `(literal) OR synonyms` (best recall, but disturbs the
    top-1 of already-good queries).
  - `auto` (**default**) — rerank the union BUT pin the literal top-1 (best of both).
- **Eval** (`scripts/eval_retrieval_recall.py`, self-labeling gated ground truth):
  recall@5 — off/fill 11%, rerank/**auto 44%**; top-1 disturbance — off/fill/auto 0,
  rerank 5/10. So `auto` = rerank's recall at fill's precision.
- **Reaches the Funhouse consultant for free** — the reviewer/consult sub-agent
  calls these same `reference_db`/`figure_db` functions via adapters, so it picks up
  `auto` with no funhouse_agent change.
- **Tests:** `tests/test_query_expansion.py` (27); full suite **3702 passed**.

### Remaining items (this feature)
- [ ] **Live Funhouse reviewer-agent eval** (owner-gated, costs API) — validate the
      lift end-to-end with the consultant on a synonym-phrased question set.
- [ ] **Curate `SYNONYM_GROUPS`** from observed recall misses (the eval's
      "no trusted GT" rows hint at vocabulary gaps); keep entries defensible.
- [ ] **Grow the eval's labeled set** (currently 9 trusted cases — small) toward a
      hand-curated gold set for a firmer recall@k estimate.
- [ ] **Owner decision at merge:** keep `auto` as the default, or ship opt-in
      (env-flip to `off`/`fill`).
- [ ] **Optional precision tuning:** `rerank`/`auto` reorder ranks 2–5 of good
      queries; if that matters, pin top-N instead of top-1.

## Agent Pattern

All 14 agents follow the 3-function Foundry pattern:

```python
# Pattern (replace {name} with dm7, gec6, gec7, gec10, gec11, gec12, gec13, micropile, fema_p2192, noaa_frost, ufc_backfill, ufc_dewatering, ufc_expansive, ufc_pavement)
{name}_agent(method: str, params_json: str) -> str
{name}_list_methods(category: str = "") -> str
{name}_describe_method(method: str) -> str
```

DM7 agent auto-discovers 340+ functions via `inspect.getmembers()`. GEC/micropile agents wrap text retrieval + figure/table lookup functions. FEMA/NOAA/UFC agents wrap table/equation lookup functions (no text retrieval).

## Weekend QC Agent (scheduled remote routine)

A **scheduled remote agent** ("routine") runs automated quality control on this repo every weekend, comparing the digitized JSON/Python against the source PDFs and pushing fixes. It runs in Anthropic's cloud (CCR) on the claude.ai Pro subscription — NOT on the API console, and NOT a Claude Code subagent. It is intentionally split into small chunks so weekday interactive sessions can author content without colliding with it.

**Where it lives / how to manage it:** https://claude.ai/code/routines (routine id `trig_015ika6HHrYfcrf7uupLGGTC`). Edit/run/disable via the `/schedule` skill in any Claude Code session, or the web UI. Deletion is web-UI only.

**Schedule:** `0 */5 * * 6,0` — every 5 hours on Sat/Sun UTC (~10 runs/weekend). Weekdays are left free for interactive authoring. Model: `claude-sonnet-4-6`.

**What it does each run (one file per run):**
1. Scans `scripts/manifests/*.json`; a reference is eligible when its manifest `pdf_path` resolves to an existing PDF in `docs/`.
2. Auto-registers any new eligible reference into `qc_progress.json`.
3. Picks the first `pending` file (text chapter, then Python file) and extracts the matching PDF pages via PyMuPDF.
4. Verifies content against the PDF, fixes extraction errors, flags edition differences and implementation gaps.
5. Validates (`audit_chapter_text.py` + `pytest`), then pushes a `qc/<ref>-<file>-<date>` branch and updates `qc_progress.json`. **It opens branches, never merges** — review and merge the `qc/*` branches yourself.

**Onboarding a new reference** (so the weekend agent picks it up automatically):
1. Add the source PDF to `docs/` and commit it (note: `docs/` is committed; `references/*.pdf` is git-ignored).
2. Set that reference's manifest `pdf_path` to `../../docs/<filename>` (resolved relative to `scripts/manifests/`).
3. Commit + push. No prompt edit needed — discovery is automatic.

### qc_progress.json (repo root)

The agent's state file, tracking two things:

**Per-chapter QC status** — `references.<key>.text` and `references.<key>.python` blocks; each file entry has `status` (`pending` / `done` / `pdf_unreadable`), `qc_date`, `issues_fixed`, and `notes`. Edition metadata (`pdf_edition`, `extraction_edition`) is per-reference; when they differ, the agent flags edition changes in `notes` rather than overwriting content (dm7_1 was once recorded as extracted from the 2022 UFC; REF-28 (2026-10-19) found its text, sections, figures and equations match the 2026 UFS print and moved its docstring pages to the 2026 printed pages).

**Implementation gaps** — `references.<key>.implementation_gaps`: figures/tables referenced in the JSON text that have NO corresponding Python lookup function. These are **TODOs for weekday authoring sessions** (e.g., a parameter-lookup chart that should become a `figure_X_Y_*()` function). The agent only flags them; it never writes the function.

When starting work on a reference, check the gaps first:
```bash
python -c "import json; d=json.load(open('qc_progress.json')); print(json.dumps(d['references'].get('dm7_1',{}).get('implementation_gaps',[]), indent=2))"
```
Each gap entry has `type` (figure/table), `id` (e.g., "Figure 2-4"), `section`, and `notes`.

## Working on This Repo

1. Install: `pip install -e .`
2. Run tests: `pytest tests/ -q`
3. Each chapter file is self-contained (no cross-chapter imports)
4. When adding equations, follow existing patterns in the relevant chapter file
5. Check `qc_progress.json` for `implementation_gaps` before authoring new functions — the QC agent flags figures/tables that need Python implementations but don't have them yet

## Environment

- Python 3.10+ (developed on 3.14.3)
- No required dependencies (numpy/scipy/matplotlib are optional, used by some functions)
- Tests: `pytest tests/ -q` (expect 3,529 passed)
