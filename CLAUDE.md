# geotech-references

Standalone geotechnical reference library: digitized equations, figures, tables, and structured reference text from UFC 3-220-10/20 (the UFC successors to NAVFAC DM 7.01/7.02), FHWA GEC series, and other standards.

Consumed by [GeotechStaffEngineer](https://github.com/soconnell345-geotech/GeotechStaffEngineer) as a Git submodule.

## Architecture

```
geotech_references/           # Python package (pip install -e .)
  _interpolation.py            # Shared helpers (_linterp)
  _plotting.py                 # Shared matplotlib helpers (get_pyplot, setup_engineering_plot)
  _retrieval.py                # Reference text retrieval (load, search, retrieve by section)
  dm7_1/                       # UFC 3-220-10 Soil Mechanics (8 chapters)
    chapter1.py ... chapter8.py
    text/                      # Structured chapter JSON (8 chapters, 457 sections, 2026-04-07)
  dm7_2/                       # UFC 3-220-20 Foundations & Earth Structures (7 chapters)
    prologue.py, chapter2.py ... chapter7.py
    text/                      # Structured chapter JSON (prologue + 6 chapters, 438 sections, 2026-04-07)
  gec_6/                       # FHWA-SA-02-054 Shallow Foundations
    tables.py, figures.py
    text/                      # Structured chapter JSON
  gec_7/                       # FHWA-NHI-14-007 Soil Nail Walls
    tables.py                  # 13 table lookup functions (bond, pullout, resistance factors, seismic)
    figures.py                 # 2 figure lookup functions (friction angle vs SPT, basal heave Nc)
    text/                      # Structured chapter JSON (5 chapters, ~37 sections)
  gec_10/                      # FHWA-NHI-10-016 Drilled Shafts
    tables.py, figures.py
    text/                      # Structured chapter JSON (5 chapters)
  gec_11/                      # FHWA-NHI-10-024 Design of MSE Walls & Slopes
    tables.py, figures.py
  gec_12/                      # FHWA-NHI-16-009 Driven Piles
    tables.py                  # 8 table lookup functions (resistance factors, beta/Nt, setup, API)
    figures.py                 # 8 figure lookup functions (Nordlund Kd, CF, alpha_t, N'q, adhesion)
    text/                      # Structured chapter JSON (8 chapters, ~109 sections)
  gec_13/                      # FHWA-NHI-16-027 Ground Modification Methods
    tables.py, figures.py
  micropile/                   # FHWA-NHI-05-039 Micropile Design & Construction
    tables.py                  # 13 table lookup functions (bond stress, pipe/rebar, elastic modulus)
    figures.py                 # 1 figure lookup function (limiting lateral modulus)
    text/                      # Structured chapter JSON (5 chapters, ~35 sections)
  fema_p2192/                  # FEMA P-2192 Seismic Design Category (2024)
    tables.py                  # 10 functions (SDC, site class, Fa/Fv, risk category)
  noaa_frost/                  # NOAA Frost Protected Shallow Foundations
    equations.py               # 5 physics equations (Stefan, Berggren, latent heat)
    tables.py                  # 4 soil thermal property lookups
  ufc_backfill/                # UFC 3-220-04N Backfill for Subsurface Structures
    equations.py               # 3 equations (compaction pressure, filter criteria, RC check)
    tables.py                  # 5 tables (compaction, material, lift, equipment, drainage)
  ufc_dewatering/              # UFC 3-220-05 Dewatering and Groundwater Control
    equations.py               # 6 equations (Thiem, Dupuit, Sichardt, superposition)
    tables.py                  # 3 tables (permeability, method selection, screen slot)
  ufc_expansive/               # UFC 3-220-07 Foundations in Expansive Soils
    equations.py               # 5 equations (activity, free swell, swell pressure, heave, pier)
    tables.py                  # 4 tables (swell potential, active zone, foundation, void space)
  ufc_pavement/                # UFC 3-260-02 Pavement Design for Airfields
    equations.py               # 4 equations (CBR-to-k, flexible/rigid thickness, ESWL)
    tables.py                  # 5 tables (frost susceptibility, reduction, aircraft, layers, subgrade)
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
  ufc_pavement_agent.py        # UFC 3-260-02 Foundry-style 3-function wrapper
tests/                         # 3,299 tests (pytest)
references/                    # Source PDFs (git-ignored)
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
| gec_6 | FHWA-SA-02-054 Shallow Foundations | 13 | 121 | yes |
| gec_7 | FHWA-NHI-14-007 Soil Nail Walls | 15 | 101 | 5 chapters |
| gec_10 | FHWA-NHI-10-016 Drilled Shafts | 10 | 175 | 5 chapters |
| gec_11 | FHWA-NHI-10-024 MSE Walls & Slopes | 17 | 130 | - |
| gec_12 | FHWA-NHI-16-009 Driven Piles | 16 | 147 | 8 chapters |
| gec_13 | FHWA-NHI-16-027 Ground Modification | 10 | 105 | yes |
| micropile | FHWA-NHI-05-039 Micropile Design | 14 | 108 | 5 chapters |
| fema_p2192 | FEMA P-2192 SDC Determination (2024) | 10 | 132 | - |
| noaa_frost | NOAA Frost Protected Shallow Foundations | 9 | 86 | - |
| ufc_backfill | UFC 3-220-04N Backfill | 8 | 87 | - |
| ufc_dewatering | UFC 3-220-05 Dewatering | 9 | 75 | - |
| ufc_expansive | UFC 3-220-07 Expansive Soils | 9 | 55 | - |
| ufc_pavement | UFC 3-260-02 Airfield Pavement | 9 | 54 | - |

### GEC-7: Soil Nail Walls (15 functions, 101 tests)

**Table Functions** (13): Bond strength coarse/fine-grained soils & rock (Tables 4.4a/b, 4.5), pullout resistance, ASD factors of safety, LRFD resistance factors (Tables 5.4-5.11), AASHTO seismic site coefficients (F_PGA, F_v), SPT correlations, elastic properties, wall displacement parameters

**Figure Functions** (2): Friction angle vs SPT N60 (Fig 4.3), basal heave Nc (Fig 5.11)

### Micropile: FHWA-NHI-05-039 (14 functions, 108 tests)

**Table Functions** (13): Grout-to-ground bond stress alpha_bond by soil/rock type & micropile type A/B/C/D (Table 5-3), pipe casing properties API N-80 & ASTM A519/A106 (Table 4-5), reinforcing bar properties (Table 4-2), classification system (Table 2-1), group efficiency (Table 5-4), corrosion criteria (Table 5-5), epsilon_50 for clays (Tables 5-7/5-8), soil modulus k for sand/clay (Tables 5-9/5-10), fixity guidance (Table 5-11), elastic modulus by soil type & SPT (Tables 5-12/5-13)

**Figure Functions** (1): Limiting lateral modulus for buckling (Fig 5-23)

### GEC-12: Driven Piles (16 functions, 147 tests)

**Figure Functions** (8): Nordlund Kd, CF correction factor, limiting toe resistance, alpha_t coefficient, N'q bearing capacity, delta/phi ratio, adhesion Ca, adhesion factor alpha

**Table Functions** (8): Resistance factors static/field, static analysis methods, API design parameters, beta/Nt coefficients, Brown's method factors, Eslami-Fellenius Cs, soil setup factors

**Text Retrieval**: `retrieve_section(reference, section_id)`, `search_sections(reference, query)`, `list_chapters(reference)`, `load_chapter(reference, chapter)`

**Structured Text**: 8 chapters (Ch 1-8 of Vol I), ~109 sections with title, body, key_points, equations, figures, tables, and applicability fields

## Agent Pattern

All 14 agents follow the 3-function Foundry pattern:

```python
# Pattern (replace {name} with dm7, gec6, gec7, gec10, gec11, gec12, gec13, micropile, fema_p2192, noaa_frost, ufc_backfill, ufc_dewatering, ufc_expansive, ufc_pavement)
{name}_agent(method: str, params_json: str) -> str
{name}_list_methods(category: str = "") -> str
{name}_describe_method(method: str) -> str
```

DM7 agent auto-discovers 340+ functions via `inspect.getmembers()`. GEC/micropile agents wrap text retrieval + figure/table lookup functions. FEMA/NOAA/UFC agents wrap table/equation lookup functions (no text retrieval).

## Working on This Repo

1. Install: `pip install -e .`
2. Run tests: `pytest tests/ -q`
3. Each chapter file is self-contained (no cross-chapter imports)
4. When adding equations, follow existing patterns in the relevant chapter file

## Environment

- Python 3.10+ (developed on 3.14.3)
- No required dependencies (numpy/scipy/matplotlib are optional, used by some functions)
- Tests: `pytest tests/ -q` (expect 3,299 passed, 85 skipped)
