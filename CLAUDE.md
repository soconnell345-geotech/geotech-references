# geotech-references

Standalone geotechnical reference library: digitized equations, figures, tables, and structured reference text from UFC 3-220-10/20 (the UFC successors to NAVFAC DM 7.01/7.02), FHWA GEC series, and other standards.

**Two complementary components per reference:**
1. **Python lookup scripts** (`tables.py`, `figures.py`, sometimes `equations.py`) — Digitized design charts, tables, and equations as callable functions. Written manually by Claude Code from the source PDFs.
2. **Structured reference text** (`text/chapterNN.json`) — Each chapter as a JSON file with sections containing `body`, `key_points`, `equations`, `figures`, `tables`, and `applicability` fields. Also written manually by Claude Code across sessions (not auto-generated — the `build_chapter_text.py` pipeline was retired after the $20/reference cost incurred on DM7).

Consumed by [GeotechStaffEngineer](https://github.com/soconnell345-geotech/GeotechStaffEngineer) as a Git submodule.

## Architecture

```
geotech_references/           # Python package (pip install -e .)
  _interpolation.py            # Shared helpers (_linterp)
  _plotting.py                 # Shared matplotlib helpers (get_pyplot, setup_engineering_plot)
  _retrieval.py                # Reference text retrieval (load, search, retrieve by section)
  _retrieval_db.py             # SQLite FTS5 retrieval layer — reference_search / reference_get / reference_query (v1.2.0)
  _figures_db.py               # SQLite FTS5 figure-catalog retrieval — figure_search / figure_get / resolve_pdf
  dm7_1/                       # UFC 3-220-10 Soil Mechanics (8 chapters)
    chapter1.py ... chapter8.py
    text/                      # Structured chapter JSON (8 chapters, 457 sections, 2026-04-07)
    figures_catalog.json       # 223 figures (number, caption, page, text-enriched description)
  dm7_2/                       # UFC 3-220-20 Foundations & Earth Structures (7 chapters)
    prologue.py, chapter2.py ... chapter7.py
    text/                      # Structured chapter JSON (prologue + 6 chapters, 438 sections, 2026-04-07)
    figures_catalog.json       # 252 figures (incl. P-* prologue, B-* appendix; e.g. Fig 4-12 log-spiral Ka/Kp)
  gec_4/                       # FHWA-IF-99-015 Ground Anchors and Anchored Systems (1999)
    tables.py                  # 6 functions: table_6 soil anchor transfer load, table_7 bond stress (rock/cohesive/cohesionless), table_8 rock anchor transfer load, table_20 corrosion protection
    text/                      # All 9 chapters complete (ch 1-9)
  gec_5/                       # FHWA NHI-16-072 Geotechnical Site Characterization (2017)
    text/                      # All 13 chapters complete (ch 1-13)
  gec_6/                       # FHWA-SA-02-054 Shallow Foundations
    tables.py, figures.py
    text/                      # Structured chapter JSON (10 chapters, body-only — manifest ready for full-schema re-extraction)
  gec_7/                       # FHWA-NHI-14-007 Soil Nail Walls
    tables.py                  # 13 table lookup functions (bond, pullout, resistance factors, seismic)
    figures.py                 # 2 figure lookup functions (friction angle vs SPT, basal heave Nc)
    text/                      # Structured chapter JSON (ch 1-5, ~37 sections, body-only; ch 6-10 not yet extracted — manifest ready)
  gec_8/                       # FHWA-HIF-07-03 Design and Construction of CFA Piles (2007)
    equations.py               # 3 functions: dd_pile_side_resistance (NeSmith 2002), cfa_allowable_capacity, cfa_grout_volume_factor
    tables.py                  # 2 functions: table_5_4 p-multiplier, table_group_efficiency_cohesionless
    text/                      # All 8 chapters complete (ch 1-8)
  gec_9/                       # FHWA-HIF-18-031 Laterally Loaded Deep Foundations (2018)
    tables.py                  # 5 functions: table_4_1 lateral resistance factor, table_7_1 p-multiplier, table_a1 k stiff clay, table_a2 epsilon50, table_a3 k sand
    figures.py                 # (catalog only; figures handled by figure_db vision tools)
    text/                      # All 13 chapters complete (ch 1-13)
  gec_10/                      # FHWA-NHI-18-024 Drilled Shafts (2018 edition)
    tables.py, figures.py      # 2018 edition: Table 8-4/9-1/10-2/11-1, Figure 10-6, Eq 10-21/22
    text/                      # All 18 chapters complete (FHWA-NHI-18-024, ch 1-18)
  gec_11/                      # FHWA-NHI-10-024 Design of MSE Walls & Slopes
    tables.py, figures.py
    text/                      # All 11 chapters complete (FHWA-NHI-10-024, ch 1-11)
  gec_12/                      # FHWA-NHI-16-009 Driven Piles
    tables.py                  # 8 table lookup functions (resistance factors, beta/Nt, setup, API)
    figures.py                 # 8 figure lookup functions (Nordlund Kd, CF, alpha_t, N'q, adhesion)
    text/                      # Structured chapter JSON (all 18 chapters complete — Vol I ch 1-8 body-only; Vol II ch 9-18 full schema with summary/key_points/equations/tables)
  gec_13/                      # FHWA-NHI-16-027 Ground Modification Methods
    tables.py, figures.py
    text/                      # Structured chapter JSON (all 11 chapters complete)
  gec_14/                      # FHWA-HIF-17-016 Assuring Quality in Geotechnical Reporting Documents (2016)
    text/                      # All 4 chapters complete (ch 1-4)
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
  ufc_pavement/                # UFC 3-250-01 Pavement Design for Roads, Streets, Walks & Storage
    equations.py               # 3 equations (cbr_to_k, stabilized_layer_thickness, free_draining_layer_required)
    tables.py                  # 8 tables (subgrade category, subbase permissible values, base design CBR, min thickness, equivalency factors, k-subgrade, frost classification, frost support index)
scripts/                       # Content generation tools (NOT installed with the package)
  build_figure_catalog.py      # PDF "List of Figures" → <pkg>/figures_catalog.json (no API; PyMuPDF text parse). Resolves each figure to its PDF page via caption-search; enriches descriptions from chapter text. Run: python scripts/build_figure_catalog.py dm7_1 dm7_2
  build_chapter_text.py        # DEPRECATED: PDF → chapter JSON pipeline (Anthropic API); discontinued — too costly ($20/reference on DM7). Chapter JSON files are now authored manually by Claude Code across sessions.
  audit_chapter_text.py        # Validate generated JSON (schema, eq coverage, implemented_in links)
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
  ufc_pavement_agent.py        # UFC 3-250-01 Foundry-style 3-function wrapper
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
| gec_4 | FHWA-IF-99-015 Ground Anchors (1999) | 6 | 50 | All 9 chapters complete |
| gec_5 | FHWA NHI-16-072 Site Characterization (2017) | 0 | 0 | All 13 chapters complete (text only) |
| gec_6 | FHWA-SA-02-054 Shallow Foundations | 13 | 121 | 10 chapters body-only; manifest ready |
| gec_7 | FHWA-NHI-14-007 Soil Nail Walls | 15 | 101 | ch 1-5 body-only; ch 6-10 pending |
| gec_8 | FHWA-HIF-07-03 CFA Piles (2007) | 5 | 37 | All 8 chapters complete |
| gec_9 | FHWA-HIF-18-031 Laterally Loaded Piles (2018) | 5 | 0 | All 13 chapters complete (no text retrieval tests yet) |
| gec_10 | FHWA-NHI-18-024 Drilled Shafts (2018) | 12 | 195 | All 18 chapters complete (ch 1-18) |
| gec_11 | FHWA-NHI-10-024 MSE Walls & Slopes | 17 | 130 | All 11 chapters complete (ch 1-11) |
| gec_12 | FHWA-NHI-16-009 Driven Piles | 16 | 147 | All 18 chapters complete (Vol I ch 1-8 body-only; Vol II ch 9-18 full schema) |
| gec_13 | FHWA-NHI-16-027 Ground Modification | 18 | 168 | All 11 chapters complete (Vol I ch 1-6, Vol II ch 7-11) |
| gec_14 | FHWA-HIF-17-016 QA Geotechnical Reports (2016) | 0 | 0 | All 4 chapters complete (text only) |
| micropile | FHWA-NHI-05-039 Micropile Design | 14 | 108 | 10 chapters (complete) |
| fema_p2192 | FEMA P-2192 SDC Determination (2024) | 10 | 132 | - |
| noaa_frost | NOAA Frost Protected Shallow Foundations | 9 | 86 | - |
| ufc_backfill | UFC 3-220-04N Backfill | 8 | 87 | - |
| ufc_dewatering | UFC 3-220-05 Dewatering | 9 | 75 | - |
| ufc_expansive | UFC 3-220-07 Expansive Soils | 9 | 55 | - |
| ufc_pavement | UFC 3-250-01 Roads/Streets/Walks/Storage | 11 | 86 | - |

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

**Text Retrieval**: `retrieve_section(reference, section_id)`, `search_sections(reference, query)`, `list_chapters(reference)`, `load_chapter(reference, chapter)`

**Structured Text**: 8 chapters (Ch 1-8 of Vol I), ~109 sections with title, body, key_points, equations, figures, tables, and applicability fields

### GEC-11: MSE Walls & Reinforced Soil Slopes — FHWA-NHI-10-024 (17 functions, 130 tests)

**Table Functions** (16): Minimum reinforcement length and embedment depth (Tables 2-1/2-2); select fill gradation (Table 3-1); electrochemical limits for steel and geosynthetics (Tables 3-3/3-4); pullout parameters Ci and F* (Table 3-6); galvanization thickness and corrosion rates (Tables 3-7/3-8); installation damage reduction factors (Table 3-9); PET durability (Table 3-11); LRFD load combinations and permanent load factors (Tables 4-1/4-2); traffic surcharge (Table 4-4); external resistance factors (Table 4-5); bearing capacity factors (Table 4-6); internal resistance factors (Table 4-7)

**Figure Functions** (1): Kr/Ka lateral stress ratio vs depth (Fig 4-10)

**Text**: All 11 chapters (Vol I ch 1-6: overview through design of MSE walls; Vol II ch 1-5: RSS design, construction, and inspection)

### GEC-13: Ground Modification Methods — FHWA-NHI-16-027 (18 functions, 168 tests)

**Table Functions** (12): Technology applicability by category/soil (Table 1-2); technologies by function (Table 1-3); comparative unit costs (Table 1-6, 2016 $); PVD transportation applications (Table 2-1); lightweight fill material properties (Table 3-1); DDC design parameters (Table 4-1); deep mixing typical qu by soil/method (Table 7-2); jet grouting system comparison (Table 8-2); soil nail bond strength by soil type (Table 9-2); micropile bond zone unit resistance Types A/B/C-D (Table 10-1); geosynthetic reduction factors RF_ID/RF_CR/RF_CBD by polymer (Table 11-1)

**Figure/Equation Functions** (6): Vibro-compaction soil suitability number (Fig 4-3, Brown 1977 SN formula); aggregate column area replacement ratio (Fig 5-2, triangular/square pattern); stone column settlement improvement factor (Fig 5-5, Priebe 1995 SRF formula); deep mixed zone composite modulus (Eq 7-4, parallel model); groutability ratio for permeation grouting (Eq 8-1, N = D15_soil/D85_grout); long-term design strength for geosynthetics (Eq 11-1, LTDS = T_ult/RF_product)

**Text**: All 11 chapters — Vol I ch 1-6 (Introduction, Vertical Drains, Lightweight Fills, Deep Compaction, Aggregate Columns, Column-Supported Embankments); Vol II ch 7-11 (Deep Mixing, Grouting, Soil Nailing, Micropiles, Geosynthetic Reinforcement)

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
  `figure_search(query, reference, chapter, limit)` (BM25, with an OR-of-terms
  recall fallback), `figure_get(reference, figure_number)`, `resolve_pdf(...)`
  → `(pdf_abs_path, page_index)`, `list_indexed_figures()`.
- **Read off** (in GeotechStaffEngineer): the `read_reference_figure` vision tool
  renders the resolved page at 220 DPI and asks the engine to read the value(s).
  Results are **read-off estimates** to be verified, not exact digitized values.

Built for DM7 (`dm7_1`: 223 figures, `dm7_2`: 252). Run the same script per
reference to extend. Source PDFs live in `docs/`.

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

**Per-chapter QC status** — `references.<key>.text` and `references.<key>.python` blocks; each file entry has `status` (`pending` / `done` / `pdf_unreadable`), `qc_date`, `issues_fixed`, and `notes`. Edition metadata (`pdf_edition`, `extraction_edition`) is per-reference; when they differ, the agent flags edition changes in `notes` rather than overwriting content (relevant for dm7_1: JSON from the 2022 edition, PDF is 2026).

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
