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
  _atomic_db.py                # Both search databases are built under a temporary name beside the real one and moved in with os.replace, so no process reads a half-built file; concurrent first calls each build their own copy (REF-56)
  _packs.py                    # Local reference packs (REF-64): GEOTECH_REFERENCES_PACKS folders indexed beside the built-ins; ids local_*; PDFs by bare file name only; a pack file the indexes cannot take is skipped (SAVEPOINT per file) and named in problems()
  packs.py                     # python -m geotech_references.packs new | check | list | index | schema; the format is docs/REFERENCE_PACKS.md
  _schema.py                   # validate_schema(): the chapter-file check shared by scripts/audit_chapter_text.py and packs check
  chapter_schema.json          # JSON schema for chapter files (package data since 1.6.0; `packs schema` prints it)
  _query_expansion.py          # Synonym query-expansion recall lever for reference_search/figure_search; EXPANSION_STRATEGY off/fill/rerank/auto (env GEOTECH_RETRIEVAL_EXPANSION, default auto), EXPANSION_PIN (env GEOTECH_RETRIEVAL_PIN, default 1). See "Lexical Query Expansion" below.
  dm7_1/                       # UFS 3-220-10 Soil Mechanics (DM 7.1), 16 Jan 2026 (8 chapters)
    chapter1.py ... chapter8.py
    text/                      # Structured chapter JSON (8 chapters, 465 sections = every printed section, 2026-04-07; every equation checked against the rendered page and stated as printed, the 7 missing sections added and the table formulas of ch 5, 6, 8 checked 2026-11-10, REF-79, tests/test_dm7_1_text_equations.py)
    figures_catalog.json       # 223 figures (number, caption, page, text-enriched description)
  dm7_2/                       # UFC 3-220-20 Foundations & Earth Structures (7 chapters)
    prologue.py, chapter2.py ... chapter7.py
    text/                      # Structured chapter JSON (prologue + 6 chapters, 439 sections, plus appendix B; equations point-fixed to the print 2026-11-10, REF-79, tests/test_dm7_2_text_equations.py)
    figures_catalog.json       # 252 figures (incl. P-* prologue, B-* appendix; e.g. Fig 4-12 log-spiral Ka/Kp)
  gec_6/                       # FHWA-SA-02-054 Shallow Foundations
    tables.py, figures.py
    text/                      # Structured chapter JSON (10 chapters, body-only — manifest ready for full-schema re-extraction)
  gec_7/                       # FHWA-NHI-14-007 Soil Nail Walls
    tables.py                  # 13 table lookup functions (bond, pullout, resistance factors, seismic)
    figures.py                 # 2 figure lookup functions (friction angle vs SPT, basal heave Nc)
    text/                      # Structured chapter JSON (ch 1-10, 164 sections; ch 1-5 rebuilt from the print, ch 6-10 checked against it, REF-04)
  gec_10/                      # FHWA-NHI-18-024 Drilled Shafts (2018 edition)
    tables.py, figures.py      # 2018 edition: Table 8-4/9-1/10-2/11-1, Figure 10-6, Eq 10-21/22
    text/                      # All 18 chapters complete (FHWA-NHI-18-024, ch 1-18)
  gec_11/                      # FHWA-NHI-10-024 Design of MSE Walls & Slopes
    tables.py, figures.py
    text/                      # All 11 chapters complete (FHWA-NHI-10-024, ch 1-11)
  gec_12/                      # FHWA-NHI-16-009 Driven Piles
    tables.py                  # 8 table lookup functions (resistance factors, beta/Nt, setup, API)
    figures.py                 # 8 figure lookup functions (Nordlund Kd, CF, alpha_t, N'q, adhesion)
    text/                      # Structured chapter JSON (Vol I ch 1-8 and Vol II ch 9-18, 238 sections; ch 9-18 checked against the print, REF-04)
  gec_13/                      # FHWA-NHI-16-027 / -028 Ground Modification Methods
    tables.py, figures.py
    text/                      # Structured chapter JSON (5 chapters, body-only — manifest ready for full-schema re-extraction)
  micropile/                   # FHWA-NHI-05-039 Micropile Design & Construction
    tables.py                  # 13 table lookup functions (bond stress, pipe/rebar, elastic modulus)
    figures.py                 # 1 figure lookup function (limiting lateral modulus)
    text/                      # Structured chapter JSON (10 chapters, 70 sections, complete)
  ufc_backfill/                # UFC 3-220-04FA Backfill for Subsurface Structures (16 Jan 2004, the reproduced TM 5-818-4) — rebuilt from the print 2026-11-10; no chapter text
    equations.py               # relative compaction check (CE 55 basis, para 5-1b(4))
    tables.py                  # para 5-1b(4) densities, Table 5-1, para 3-3d materials, 5-1b(3) lifts, 5-1b(2) equipment, Fig 2-5a
  ufc_expansive/               # UFC 3-220-07 Foundations in Expansive Soils (the reproduced TM 5-818-7) — rebuilt from the print 2026-11-10
    equations.py               # total swell as the area under per cent swell vs depth (Figure 5-4); Table 4-2's four swell relations; Eq 4-1 (Van Der Merwe), Eq 5-2, Eqs 5-3 to 5-5, Eqs 5-8/5-9
    tables.py                  # Table 4-1 swell potential, para 5-4c active zone, Table 6-1 foundations, para 6-4 grade-beam void, Figure 4-1 potential expansiveness
  ufc_pavement/                # UFC 3-250-01 (2016) Pavement Design for Roads & Parking — REBUILT 2026-07 from the real doc (audit gap CLOSED): CBR curve E-1, rigid Eq 13-1, overlays, frost, drainage
  ufc_stabilization/           # UFC 3-250-11 (2020) Soil Stabilization (additive selection, criteria, equivalency)
  ufc_flexible_practice/       # UFC 3-250-03 (2018) Flexible Pavement Practice (HMA/Marshall/Superpave, sprays, seals)
  ufc_concrete_practice/       # UFC 3-250-04 (2024) Concrete Pavement Practice (materials, dowels, joints, RCC)
    equations.py               # 4 equations (CBR-to-k, flexible/rigid thickness, ESWL)
    tables.py                  # 5 tables (frost susceptibility, reduction, aircraft, layers, subgrade)
scripts/                       # Content generation tools (NOT installed with the package)
  build_figure_catalog.py      # PDF "List of Figures" → <pkg>/figures_catalog.json (no API; PyMuPDF text parse). Resolves each figure to its PDF page via caption-search; enriches descriptions from chapter text. Run: python scripts/build_figure_catalog.py dm7_1 dm7_2; `--add-missing <pkg>` adds the printed figures a catalog lacks without changing its rows (REF-84)
  build_chapter_text.py        # DEPRECATED: PDF → chapter JSON pipeline (Anthropic API); discontinued — too costly ($20/reference on DM7). Chapter JSON files are now authored manually by Claude Code across sessions.
  audit_chapter_text.py        # Validate generated JSON (schema, eq coverage, implemented_in links)
  build_printed_text.py        # Chapter text + figure catalog read off the printed pages (no API): sections from the printed contents, bodies in the print's wording with [p. 6-28] markers, equation objects as [Eq. 9-5], figures/tables from the Lists of Figures/Tables. Manifest "text_build": "printed". Used for fhwa_soils_foundations (REF-29)
  check_section_numbers.py     # Chapter JSON section numbers vs the printed PDF (outline + page headings; no API). --detail lists what needs a reader, --apply writes only definite renumberings (section_id values only). Test: tests/test_section_numbers.py (skips without the PDFs). REF-23
  eval_retrieval_gold.py       # recall@3/5/10 per expansion strategy on the hand-curated gold set retrieval_gold.json (54 cases, 17 references). REF-07
  eval_subsection_retrieval.py # 14 questions answered in a subsection (8 references): replays search -> fetch, reports recall@5 and characters read; --titles --save/--compare = the ranking guard (top-level sections found by their own title). Test: tests/test_subsection_retrieval.py. REF-24
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
  ufc_backfill_agent.py        # UFC 3-220-04FA Foundry-style 3-function wrapper
  ufc_expansive_agent.py       # UFC 3-220-07 Foundry-style 3-function wrapper
  ufc_pavement_agent.py        # UFC 3-250-01 Foundry-style 3-function wrapper
tests/                         # 6,755 tests collected (`pytest --collect-only -q`, 2026-11-09)
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

## DM7 Inventory (393 functions, 2,014 tests; counted 2026-10-21 with `inspect` and `pytest --collect-only -q`)

| Module | Chapter | Topic | Functions | Tests |
|--------|---------|-------|-----------|-------|
| dm7_1 | 1 | Identification & Classification | 7 | 47 |
| dm7_1 | 2 | Field Exploration & Testing | 3 | 29 |
| dm7_1 | 3 | Laboratory Testing | 6 | 47 |
| dm7_1 | 4 | Distribution of Stresses | 23 | 134 |
| dm7_1 | 5 | Consolidation & Settlement | 37 | 227 |
| dm7_1 | 6 | Seepage & Drainage | 15 | 119 |
| dm7_1 | 7 | Slope Stability | 6 | 61 |
| dm7_1 | 8 | Correlations for Soil Properties | 50 | 228 |
| dm7_2 | Pro | Prologue — Index Properties | 13 | 95 |
| dm7_2 | 2 | Earth Pressures | 10 | 75 |
| dm7_2 | 3 | Shallow Foundations | 11 | 105 |
| dm7_2 | 4 | Deep Foundations | 35 | 212 |
| dm7_2 | 5 | Bearing Capacity (Deep) | 69 | 245 |
| dm7_2 | 6 | Retaining Structures | 83 | 247 |
| dm7_2 | 7 | Slope Stability (Earth Structures) | 25 | 143 |

## GEC Module Inventory

Tests: the tests in each package's own test files (`tests/test_gec6_*.py`, `tests/test_ufc_backfill.py`, `tests/test_aashto_1993*.py` and so on), counted by running them (`pytest -q`, 2026-11-05, all passing; the fhwa_soils_foundations count includes 3 tests that skip without PyMuPDF and the PDFs). Functions are not re-counted here.

| Module | Reference | Functions | Tests | Text Chapters |
|--------|-----------|-----------|-------|---------------|
| gec_6 | FHWA-SA-02-054 Shallow Foundations | 13 | 121 | 10 chapters body-only; manifest ready. Figure catalog 86 rows, Appendices B and C's 29 figures added 2026-11-10 (REF-84) |
| gec_7 | FHWA-NHI-14-007 Soil Nail Walls | 15 | 101 | All 10 chapters with equations, figures and tables; ch 1-5 rebuilt from the print, ch 6-10 checked against the print page by page (REF-04, 2026-10-30). Figure catalog 89 rows, 3.22 and Appendices A, B, C and G added 2026-11-10 (REF-84) |
| gec_10 | FHWA-NHI-18-024 Drilled Shafts (2018) | 12 | 311 | All 18 chapters complete (ch 1-18); ch 6 and 8 rewritten from the print 2026-11-10 (REF-81): bodies in the print's wording with page markers, Tables 6-1 to 6-3 and 8-1 to 8-4 and Eq. 8-1 typed in from the page; printed 8.1 (Blocks 1 to 22) stored as 8.1 and parts 8.1.a to 8.1.d, the letters not printed |
| gec_11 | FHWA-NHI-10-024 MSE Walls & Slopes | 17 | 136 | All 11 chapters complete (ch 1-11) |
| gec_12 | FHWA-NHI-16-009 Driven Piles | 16 | 231 | All 18 chapters; Vol I (ch 1-8) body-only, its ch 7 top-level sections 7.1-7.10 rebuilt from the print (REF-04); Vol II (ch 9-18) with equations, figures and tables, checked against the print page by page (REF-04, 2026-10-30); Vol II appendices A-C not built |
| gec_13 | FHWA-NHI-16-027 / -028 (Vols I / II) Ground Modification | 16 | 222 | All 10 printed chapters (Vol I ch 1-5, Vol II ch 6-10); ch 3-10 rebuilt from the print 2026-10-19 (REF-25); the DDC depth is Eq. 4-1 as printed (REF-63). Figure catalog 239 rows: chapters 2-5 and 7-10 (206 figures) added 2026-11-10, the catalog had held ch 1 and 6 only (REF-84) |
| micropile | FHWA-NHI-05-039 Micropile Design | 14 | 108 | 10 chapters (complete). Figure catalog 142 rows, the sample problems' S1-1 to S2-3 added 2026-11-10 (REF-84) |
| fhwa_soils_foundations | FHWA NHI-06-088 / NHI-06-089 Soils and Foundations Reference Manual, Vols I-II (Dec 2006) | 0 | 15 | All 12 chapters (Vol I ch 1-7, Vol II ch 8-12; appendices A-E not built), 511 sections, 295 figures, 200 tagged equation numbers (formulas not typed in: app BACKLOG REF-38); read off the print by `scripts/build_printed_text.py` (REF-29): bodies are the print's own wording with page markers, no summaries or key points; 4 sections over 14,000 characters split into lettered parts (`9.2.a`), the letters not printed; Tables 4-8 and 10-1, printed as pictures, typed in from the page (manifest key `printed_tables`). Figure catalog 391 rows, Appendix A's 59 figures and D-10 added 2026-11-10 (REF-84) |
| ufc_backfill | UFC 3-220-04FA Backfill (rebuilt from the print 2026-11-10) | 7 | 49 | - |
| ufc_expansive | UFC 3-220-07 Expansive Soils (rebuilt from the print 2026-11-10; the printed heave methods of ch 4-5 built 2026-11-10, REF-91) | 14 | 79 | - |
| ufc_pavement | UFC 3-250-01 Pavement Design for Roads and Parking Areas (rebuilt 2026-07 from the real document; no longer the UFC 3-260-02 airfield coding, audit done; Figure 10-1 traced from the chart 2026-11-10) | 53 | 397 | 21 chapters |
| eurocode_7_1 | EN 1997-1:2004 Eurocode 7 Part 1 General Rules (Annex A partial factors, DA1-DA3, Annex C/D/E/F/G/H methods) | 31 | 134 | All 21 chapters (Sections 1-12 + Annexes A-J) |
| eurocode_7_2 | EN 1997-2:2007 Eurocode 7 Part 2 Ground Investigation (CPT/PMT/SPT/DP/FVT/DMT/PLT correlations) | 43 | 143 | 9 chapters (body + all annexes). Figure catalog 21 rows, B.4 and B.5 added 2026-11-10 (REF-84) |
| aashto_1993 | AASHTO 1993 Pavement Design Guide (flexible SN / rigid D equations, layer coefficients, reliability; FULL Appendix D LEF tables D.1-D.18 in lef.py — closed-form equations are in Volume 2 Appendix MM, NOT in this scan; Section 3.2 composite-k worksheet in composite_k.py, chart-read; Appendix G swell/frost-heave loss + Table 3.1 performance-period iteration in environmental.py; scanned source read visually; US units) | ~45 | 425 | 11 chapters (Part I-II full, III/IV stubs) |
| em_2104 | EM 1110-2-2104 Strength Design for Reinforced Concrete Hydraulic Structures (1 Nov 2023 ed., published 8 Jan 2025) — load inventory + full Table 3-2 load-factor table + LRFD/earthquake load combinations (loads.py); serviceability service-stress/single-load-factor/reinforcement-limit provisions (serviceability.py); Chapter 2 detailing incl. temp/shrinkage steel (reinforcement.py); the complete Appendix B flexure+axial INVESTIGATION equations for singly/doubly reinforced, tension+flexure, and pure-flexure members incl. numerically-solved cubics (flexure_axial.py); the complementary Appendix D-2 DESIGN equations (design.py); Chapter 5 shear incl. the pre-ACI-318-19 equation deliberately retained for RCHS per Appendix G commentary (shear.py); US units | ~50 | 111 | 5 chapters (1-5) full; Appendix B-G implemented as Python lookups, not re-narrated text |
| em_2107 | EM 1110-2-2107 Design of Hydraulic Steel Structures (1 Aug 2022 ed.) — does NOT reprint AISC 360 member-capacity equations (member design is by direct AISC 360 reference); LRFD loads/full Table 4.1 load-factor table/load combinations + earthquake combinations (loads.py); HSS-support seismic-acceleration amplification incl. the full Appendix D pseudo-dynamic (Chopra & Tan 1989) derivation, validated against its own 2-variant worked example (seismic_amplification.py); Table 3.1 target reliability + usual/unusual/extreme load categories (design_basis.py); fatigue screening + fracture-critical redundancy check (fatigue_fracture.py); bolt/weld/faying-surface selection rules (connections.py); Chapter 10 + Appendix F Tainter-gate load equations — side-seal friction, wire-rope loads, hydrostatic load by integration + simplified projection, trunnion friction, full Eq 10.2-10.14 load-combination table, anchorage shear-friction (tainter_gate_loads.py), fully validated against Appendix F's own worked example (2 source-document sign/citation errors found and resolved by cross-verification); US units | 49 | 103 | 6 chapters (1-6) full; Chapters 9-16/Appendices B/C gate-geometry content intentionally thin per scope (closed-form Appendix D/E/F content fully covered instead) |
| ufc_structural | UFC 3-301-01 Structural Engineering (DoD, 11 Apr 2023, thru Change 4 3 Jun 2025) — DoD modifications ONLY (adopts 2024 IBC/ASCE 7-22 baseline, does not reprint civilian-code content this UFC doesn't itself modify); risk category Table 2-2 (adds DoD Risk Category V + Sea Level Rise column, REPLACES IBC Table 1604.5/ASCE 7-22 Tables 1.5-1/1.5-2) + wind deflection Table 2-1 + wind-speed conversion Eq 16-18a/b (risk_category_and_loads.py); the FULL Table 3-1 seismic-system replacement for ASCE 7-22 Table 12.2-1 (92 systems, categories A-H) + Table 7-1 critical-healthcare permitted-systems subset + Table B-1 Risk-Category-IV alternate-design permitted-systems table (seismic_force_resisting_systems.py); additional vertical-ground-motion seismic load combinations (Eq under 2.3.6/2.4.5), Appendix B RC IV combinations (Eq B-1/B-2), coupling-beam capacity-design shear check, healthcare structural-separation Eq 12.12-1 (seismic_load_combinations.py); Chapter 4 Table 4-1(a)/(b) performance-objective lookups (Table 4-1(a)'s RC I/II and III cells preserved as literal printed text — genuine cell-merge/footnote ambiguity in the source, documented) + trigger cost thresholds + IEBC high-wind roof-diaphragm trigger (evaluation_retrofit.py); Chapters 6/7 healthcare Table 6-1 masonry thickness + structural-configuration/elevator criteria (healthcare_modifications.py); Chapter 5 nonbuilding-structure standard pointers (nonbuilding_structures.py); Appendix C rigid-pipe span Tables C-1/C-2/C-3 + Eq C-1 + elevator/partition/certification criteria (nonstructural_seismic.py); Appendix G GFRP Table G-1 + DoD-specific seismic/fire/durability limits (gfrp.py); Appendix A best-practice guidance + embedded numeric criteria (best_practices.py); Chapter 1 legend/progressive-collapse/RC-V pointers (general_provisions.py). Table 4-2 (benchmark-building code-vintage cross-reference) and Appendices F/H/I NOT digitized (administrative/narrow-scope, no design equations — see package docstring); US units | 66 | 200 | 7 chapters (1-7) full; Appendices A-D/G implemented as Python lookups, not re-narrated text |

### GEC-7: Soil Nail Walls (15 functions, 101 tests)

**Table Functions** (13): Bond strength coarse/fine-grained soils & rock (Tables 4.4a/b, 4.5), pullout resistance, ASD factors of safety, LRFD resistance factors (Tables 5.4-5.11), AASHTO seismic site coefficients (F_PGA, F_v), SPT correlations, elastic properties, wall displacement parameters

**Figure Functions** (2): Friction angle vs SPT N60 (Fig 4.3), basal heave Nc (Fig 5.11)

### GEC-10: Drilled Shafts — FHWA-NHI-18-024 (11 functions)

**Figure/Equation Functions** (5): Alpha adhesion factor for cohesive side resistance (Fig 10-6, Chen 2011 formula α=0.30+0.17/(su/pa)); UU→CIUC and UC→CIUC strength conversion (Eq 10-16/17, Chen & Kulhawy 1993); rock socket side resistance for normal sockets (Eq 10-21, C=1.0 normalized); rock socket side resistance for caving/fractured rock (Eq 10-22 + Table 10-3 αE reduction factors by RQD and joint condition)

**Table Functions** (6): LRFD resistance factors by limit state and geomaterial (Table 8-4, compression vs. uplift keys); lateral resistance factors for p-y pushover (Table 9-1); N*c bearing capacity factor for base resistance in cohesive soil (Table 10-2, su-keyed); p-multipliers for lateral group analysis (Table 11-1, 0.70/0.50/0.35 at 3D); group axial efficiency for cohesionless soils (Section 11.4.1.2, p. 11-6, after AASHTO 10.8.3.6.3, 0.65/0.80/1.0 at 2.5D/3D/4D+; GEC-10 has no Table 11-2, the name is kept). `aashto_reliability_index` was removed (GEC-10 prints no such table; review finding gec-23)

**Text**: All 18 chapters (FHWA-NHI-18-024, 2018 edition) — construction methods (ch 1-7), design process (ch 8), lateral and axial design (ch 9-10), group design (ch 11), structural design (ch 12), load tests (ch 13), specifications/inspection/integrity/acceptance/cost (ch 14-18)

### Micropile: FHWA-NHI-05-039 (14 functions, 108 tests)

**Table Functions** (13): Grout-to-ground bond stress alpha_bond by soil/rock type & micropile type A/B/C/D (Table 5-3), pipe casing properties API N-80 & ASTM A519/A106 (Table 4-5), reinforcing bar properties (Table 4-2), classification system (Table 2-1), group efficiency (Table 5-4), corrosion criteria (Table 5-5), epsilon_50 for clays (Tables 5-7/5-8), soil modulus k for sand/clay (Tables 5-9/5-10), fixity guidance (Table 5-11), elastic modulus by soil type & SPT (Tables 5-12/5-13)

**Figure Functions** (1): Limiting lateral modulus for buckling (Fig 5-23)

### GEC-12: Driven Piles (16 functions, 231 tests)

**Figure Functions** (8): Nordlund Kd, CF correction factor, limiting toe resistance, alpha_t coefficient, N'q bearing capacity, delta/phi ratio, adhesion Ca, adhesion factor alpha

**Table Functions** (8): Resistance factors static/field, static analysis methods, API design parameters, beta/Nt coefficients, Brown's method factors, Eslami-Fellenius Cs, soil setup factors

**Text Retrieval**: `retrieve_section(reference, section_id, include_subsections=False)`, `search_sections(reference, query, limit=None, offset=0, max_chars=None)`, `list_chapters(reference, chapter=None, sections=True, max_chars=None)`, `load_chapter(reference, chapter, max_chars=None)` — every level, e.g. `retrieve_section("gec_12", "7.2.1.3.1")` (see "Section levels"; `max_chars` in "Results that fit a size limit")

**Structured Text**: 8 chapters (Ch 1-8 of Vol I), 109 top-level sections plus 76 nested in `subsections` (chapter 7: the static methods, group efficiency, uplift, setup, settlement, p-y), with title, body, key_points, equations, figures, tables, and applicability fields

### GEC-11: MSE Walls & Reinforced Soil Slopes — FHWA-NHI-10-024 (17 functions, 135 tests)

**Table Functions** (16): Minimum reinforcement length and embedment depth (Tables 2-1/2-2); select fill gradation (Table 3-1); electrochemical limits for steel and geosynthetics (Tables 3-3/3-4); pullout parameters Ci and F* (Table 3-6); galvanization thickness and corrosion rates (Tables 3-7/3-8); installation damage reduction factors (Table 3-9); PET durability (Table 3-11); LRFD load combinations and permanent load factors (Tables 4-1/4-2); traffic surcharge (Table 4-4); external resistance factors (Table 4-5); bearing capacity factors (Table 4-6); internal resistance factors (Table 4-7)

**Figure Functions** (1): Kr/Ka lateral stress ratio vs depth (Fig 4-10)

**Text**: All 11 chapters (Vol I ch 1-6: overview through design of MSE walls; Vol II ch 1-5: RSS design, construction, and inspection)

### GEC-13: Ground Modification Methods — FHWA-NHI-16-027 (Vol I) / -028 (Vol II) (16 functions, 222 tests)

**Table Functions** (10): Technology applicability by category/soil (Table 1-2); technologies by function (Table 1-3); comparative unit costs (Table 1-6, 2016 $); PVD transportation applications (Table 2-1); lightweight fill material properties (Table 3-1); DDC applied energy by deposit type (`table_4_3_applied_energy`, Table 4-3, p. 4-46); jet grouting systems' advantages and disadvantages (`table_8_1_jet_grouting_systems`, Table 8-1, p. 8-26); single-fluid soilcrete strengths by soil (`table_8_6_soilcrete_strength`, Table 8-6, p. 8-71); and the DDC depth of improvement `equation_4_1_ddc_depth` (in tables.py; Eq. 4-1, p. 4-40, D = n (W H)^0.5 with W in Mg and H in m: n = 0.5 for most soils by default, 0.4 for landfills, any n from 0.3 to 0.8 per Figure 4-21, the depths at 0.3 and 0.8 always given; the old name `figure_4_1_ddc_depth` is kept as an alias returning the same; its four soil types after Lukas 1995, n 0.35 to 0.6, which GEC-13 does not print, are refused, REF-63, 2026-11-06). The DDC parameters, deep mixing qu and jet grouting diameter/strength lookups that cited Tables 4-1, 7-2 and 8-2 were removed or re-cited (REF-62, 2026-11-06): Table 4-1 is tamper equipment, Table 8-2 permeation grout components, chapter 7 numbers no tables, and their values matched no held manual. Deep mixing strength is text only (p. 7-23, 100 to 500 psi specified on recent projects; `search_sections`). Soil nail bond, micropile bond and geosynthetic reduction-factor lookups that cited GEC-13 Tables 9-2, 10-1 and 11-1 were removed (REF-61, 2026-11-06): GEC-13 prints Table 9-2 on subgrade stabilization and Table 10-1 on geosynthetic properties, has no Table 11-1, and their values matched no held manual. The printed tables are `gec_7` Tables 4.4a/4.4b/4.5, `micropile` Table 5-3 and `gec_11` Tables 3-9/3-11

**Figure/Equation Functions** (6): Vibro-compaction backfill suitability number (`figure_4_3_suitability_number`, but the relation is Eq. 4-3, p. 4-73, Brown 1977; Fig 4-3 is the SPT liquefaction chart, REF-60); aggregate column area replacement ratio (`figure_5_2_area_replacement_ratio`, Eq. 5-1, p. 5-31, triangular/square pattern; Fig 5-2 is top-feed vibro-replacement); stone column settlement improvement factor (`figure_5_5_settlement_improvement`, but the relation is Eq. 5-4, p. 5-32, the stress-ratio SRF = 1/[1 + (n-1)a_s]; Fig 5-5 is a vibrator cross-section and the relation is not Priebe's, REF-44); deep mixed zone composite modulus (`equation_7_4_composite_modulus`, parallel model, NOT printed in GEC-13: chapter 7 numbers no equations); groutability ratio for permeation grouting (`equation_8_1_groutability_ratio`, but the relation is Eq. 8-2, p. 8-29, N = D15_soil/D85_grout, feasible above 24 as printed; Eq. 8-1 is Darcy's law); long-term design strength for geosynthetics (`equation_11_1_ltds`: GEC-13 has no Eq. 11-1; the printed equation is GEC-11 Vol I Eq. 3-12, p. 3-28, which GEC-13 p. 6-37 refers to)

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
  query-expansion + an OR-of-terms recall fallback — see "Lexical Query Expansion";
  a figure printed over several pages is one hit listing its `pages`, and
  each hit carries its volume's `reference_id`),
  `figure_get(reference, figure_number)`, `resolve_pdf(...)`
  → `(pdf_abs_path, page_index)`, `list_indexed_figures()`.
- **Read off** (in GeotechStaffEngineer): the `read_reference_figure` vision tool
  renders the resolved page at 220 DPI and asks the engine to read the value(s).
  Results are **read-off estimates** to be verified, not exact digitized values.

Built for DM7 (`dm7_1`: 223 figures, `dm7_2`: 252). Run the same script per
reference to extend. Source PDFs live in `docs/`.

Printed figures a catalog lacks (a List of Figures that leaves out the
appendices, or one list per chapter read as one) are added with
`python scripts/build_figure_catalog.py --add-missing <package>`, which
changes no existing row: each new row's page prints the label and caption
and holds a picture or drawing, and `--overrides FILE.json` places a figure
the scan cannot (a garbled label, typed text in a box) or adds `read_notes`
for one printed turned. 428 rows were added this way on 2026-11-10 (REF-08,
REF-84): `gec_5` 349 rows, `gec_13` 239, `fhwa_soils_foundations` 391,
`gec_6` 86, `gec_4` 90, `gec_7` 89, `micropile` 142, `eurocode_7_2` 21.
Tests: `tests/test_catalog_added_rows.py`.

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
  7.2.1.3.1, not only 7.2. Rows carry `parent_rowid`, `depth`, `parents_json`
  and `reference_id` (the chapter file's report number, so a search scoped
  by a volume's number keeps to that volume, `_retrieval_db.search_scope`);
  `PRAGMA user_version` = `_SCHEMA_VERSION` (4), and a database built by an
  older version is rebuilt on first use whatever its mtime. Both databases
  keep a `build_meta` table with the signature of their source files (path,
  size, mtime of each), so a chapter file or catalog deleted, added or
  restored with an older date also rebuilds (2026-11-10 review, core-11).
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
  result is `{"hits", "shown", "total_hits"}`. When no section holds every
  word it returns the ranked search of that reference instead, each hit
  marked `match` (2026-11-10 review, core-07; see "How a hit matched").
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
- **How a hit matched** (2026-11-10 review, core-05): `reference_search`
  and `figure_search` hits that do not hold every word carry `match`
  (`"synonyms"`; `"all words"` with `not_as_phrase` for a hit with every
  word but not a phrase the query ran, a hyphenated term being the phrase
  of its parts; or `"any word"` with `lacks`, the words they do not
  hold), worked out after the ranking, so no hit moves; a hit that holds
  every word has no mark. With `max_chars` the dict adds `matched`,
  `words_not_found` and a sentence on the note, and an empty result names
  the scope searched, what was tried and the words nothing there holds.
- **Section fetches are not shaped**: the largest (`reference_get` dm7_1
  1-3.6, 13,783; `retrieve_section` gec_12 8.5.2, 13,074) fit by their data.
  The app's guard test walks every reference method and fails if that
  changes (`funhouse_agent/tests/test_reference_result_sizes.py`).
- **Tests:** `tests/test_result_size.py`.

## Lexical Query Expansion (recall lever)

> Status: on master since 2026-06 and released in refs 1.3.0 (2026-07-05); curated and measured on a gold set
> 2026-10-20 (REF-03/REF-07, below). Default is ON (`auto`).

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
  - `auto` (**default**) — fuse the literal hits with the union by reciprocal
    rank (`fuse_hits`, `FUSION_K` 3, env `GEOTECH_RETRIEVAL_FUSION_K`; the
    literal top 3 vote, `FUSION_VOTES`), pin the literal top-1, and keep the
    literal hit at rank r <= 5 no lower than 2r (REF-54, 2026-11-05: before,
    only the top-1 was kept and the union filled the other nine places, so
    "PVD spacing design" lost its literal ranks 3 and 5; gold set `auto` R@5
    38 -> 41, R@10 43 -> 44; `eval_retrieval_recall.py` unchanged at 4/9).
- **Eval** (`scripts/eval_retrieval_recall.py`, self-labeling gated ground truth):
  recall@5 — off/fill 11%, rerank/**auto 44%**; top-1 disturbance — off/fill/auto 0,
  rerank 5/10. So `auto` = rerank's recall at fill's precision.
- **Reaches the Funhouse consultant for free** — the reviewer/consult sub-agent
  calls these same `reference_db`/`figure_db` functions via adapters, so it picks up
  `auto` with no funhouse_agent change.
- **Tests:** `tests/test_query_expansion.py` (65).

### Curation and the gold set (REF-03, REF-07; 2026-10-20)
- **Removed:** bare `cu` (also the coefficient of uniformity, UFS 3-220-10
  Sec. 1-3.3.2, and the CU triaxial test); bare `compaction` (fired on deep
  dynamic compaction and vibro-compaction); the dead `liquefaction
  triggering` form (no section in the library says it) and bare
  `liquefaction` from the CRR group. CSR (demand) and CRR (capacity) are
  separate groups (FHWA-NHI-16-027 Sec. 4.1.6).
- **Fixed:** longest match wins, so "negative skin friction" no longer fires
  the side-resistance group; terms match whole words with an optional plural
  ("PVDs"); a term with punctuation goes to FTS5 as the phrase of its tokens
  (`(N1)60`, `N1(60)` -> `"n1 60"`, the way the index tokenizes the print).
- **Added:** PVD/wick drain/vertical drain, CSR, (N1)60/N160/normalized
  blow count (not "corrected blow count": UFS 3-220-10 uses it for N60),
  p-y, t-z/load-transfer curve, CPT/CPTu/piezocone (not "cone
  penetrometer": the DCP is another test), SPT, DMT, PMT, UCS/uniaxial
  compressive strength (no bare `qu`: FHWA-NHI-14-007 uses it for the nail
  bond strength), RQD, geofoam/EPS, stone column/aggregate column/aggregate
  pier, vibro-compaction/vibroflotation, deep mixing/DSM/DMM, CFA/auger
  cast/ACIP, bare `mse`.
- **Zero-hit queries under `auto`:** a query whose literal AND form matches
  nothing is run with its named terms swapped for their groups
  (`substituted_query`), so "wick drain smear zone" still has to say
  "smear"; the slots left are filled by the query's words OR-ed with the
  synonyms (`zero_literal_hits`), so a group that fires does not crowd out
  the OR-of-words fallback ("DSM column layout for embankment support").
- **`EXPANSION_PIN`** (env `GEOTECH_RETRIEVAL_PIN`, default 1): how many
  literal hits `auto` keeps in place. Pin 2 and 3 measured lower; 1 stays.
- **REF-37 pruning (in REF-54, 2026-11-05):** removed `cohesion` from the su
  group (drained c' is another quantity), `ultimate bearing` (allowable
  bearing fired it), the settlement group (immediate settlement fired
  consolidation settlement; GEC-6/GEC-8 print "compression settlement" for
  sand), `load-transfer curve` from t-z (UFC 3-220-20 Sec. 6-5.8.4.2 uses it
  for t-z and q-z) and `active resistance` (printed nowhere, not a term).
  `tip resistance` stays in end bearing (FHWA-NHI-06-089 Sec. 9.1.2 and
  GEC-10 Sec. 10.1 print it for the shaft or pile base); "cone tip
  resistance" and "CPT tip resistance" are their own group, so the longest
  match keeps the CPT qc from firing end bearing.
  Unprinted forms an engineer types (`dsm`, `underseepage`, `pile freeze`,
  `interface adhesion`) stay as triggers.
- **Gold set** `scripts/retrieval_gold.json` (54 cases over 17 references;
  kinds method / table value / figure / definition / limit; each with the
  sections a good search returns, 69 of 85 located on their printed page) and
  `scripts/eval_retrieval_gold.py` (recall@3/5/10 per strategy, MRR, top-1
  changes, `--pins`, `--per-case`). Before -> after, `auto`: R@3 38 -> 41,
  R@5 42 -> 46, R@10 45 -> 48 of 54; `off` (no synonyms and no OR fallback)
  31/35/37 unchanged. The script's "top-1 changed" (10) counts queries the
  literal answers with nothing; of the 44 it answers, `auto` changes the
  top-1 of none. **The set is in sample:** it was written with the
  curation, and most cases use a group's vocabulary, so it shows the
  groups work, not how much they lift questions nobody tuned on.
- **Still open** (BACKLOG): a held-out question set; the live librarian
  eval; ranking misses no synonym fixes (p-multipliers, EC7 design approach
  1, bearing-capacity FOS, trench earth pressures).

## Agent Pattern

The per-reference agents follow the 3-function Foundry pattern:

```python
# Pattern (replace {name} with dm7, gec6, gec7, gec10, gec11, gec12, gec13, micropile, ufc_backfill, ufc_expansive, ufc_pavement, and so on for the other files in agents/)
{name}_agent(method: str, params_json: str) -> str
{name}_list_methods(category: str = "") -> str
{name}_describe_method(method: str) -> str
```

`agents/references_agent.py` is the one dispatcher for every reference: its catalog (`_REFERENCE_CATALOG`) is built at import from the installed package (each subpackage, its public modules, whether it ships `text/*.json`, and the citation from its chapter files or docstring), so a new package needs no edit there (DOC-09; `tests/test_references_agent.py`). DM7 agent auto-discovers 340+ functions via `inspect.getmembers()`. GEC/micropile agents wrap text retrieval + figure/table lookup functions. UFC agents wrap table/equation lookup functions (no text retrieval).

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
- Tests: `pytest tests/ -q` (6,755 tests collected on 2026-11-09 by `pytest --collect-only -q`)
