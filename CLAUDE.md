# geotech-references

Standalone geotechnical reference library: digitized equations, figures, tables, and structured reference text from NAVFAC DM7, FHWA GEC series, and other standards.

Consumed by [GeotechStaffEngineer](https://github.com/soconnell345-geotech/GeotechStaffEngineer) as a Git submodule.

## Architecture

```
geotech_references/           # Python package (pip install -e .)
  _interpolation.py            # Shared helpers (_linterp)
  _plotting.py                 # Shared matplotlib helpers (get_pyplot, setup_engineering_plot)
  _retrieval.py                # Reference text retrieval (load, search, retrieve by section)
  dm7_1/                       # UFC 3-220-10 Soil Mechanics (8 chapters)
    chapter1.py ... chapter8.py
  dm7_2/                       # UFC 3-220-20 Foundations & Earth Structures (7 chapters)
    prologue.py, chapter2.py ... chapter7.py
  gec_12/                      # FHWA-NHI-16-009 Driven Piles
    __init__.py
    figures.py                 # 8 figure lookup functions (Nordlund Kd, CF, alpha_t, N'q, adhesion)
    tables.py                  # 8 table lookup functions (resistance factors, beta/Nt, setup, API)
    text/                      # Structured chapter JSON (8 chapters, ~109 sections)
      chapter01.json ... chapter08.json
agents/
  dm7_agent.py                 # DM7 Foundry-style 3-function wrapper
  gec12_agent.py               # GEC-12 Foundry-style 3-function wrapper
tests/                         # 2,155 tests (pytest)
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

## GEC-12 Inventory (16 functions + 4 text retrieval, 147 tests)

| Module | Type | Functions | Tests |
|--------|------|-----------|-------|
| figures.py | Figure lookups | 8 | 65 |
| tables.py | Table lookups | 8 | 48 |
| _retrieval.py | Text retrieval | 4 | 34 |

**Figure Functions**: Nordlund Kd (Tables 7-6/7-7), CF correction factor (Fig 7-14), limiting toe resistance (Fig 7-15), alpha_t coefficient (Fig 7-16a), N'q bearing capacity (Fig 7-16b), delta/phi ratio (Fig 7-9), adhesion Ca (Fig 7-17), adhesion factor alpha (Fig 7-18)

**Table Functions**: Resistance factors static (Table 7-1), resistance factors field (Table 7-2), static analysis methods (Table 7-3), API design parameters (Table 7-8), beta/Nt coefficients (Table 7-9), Brown's method factors (Table 7-10), Eslami-Fellenius Cs (Table 7-11), soil setup factors (Table 7-16)

**Text Retrieval**: `retrieve_section(reference, section_id)`, `search_sections(reference, query)`, `list_chapters(reference)`, `load_chapter(reference, chapter)`

**Structured Text**: 8 chapters (Ch 1-8 of Vol I), ~109 sections with title, body, key_points, equations, figures, tables, and applicability fields

## Agent Pattern

Both agents follow the 3-function Foundry pattern:

```python
# DM7 Agent
dm7_agent(method: str, params_json: str) -> str
dm7_list_methods(category: str = "") -> str
dm7_describe_method(method: str) -> str

# GEC-12 Agent
gec12_agent(method: str, params_json: str) -> str
gec12_list_methods(category: str = "") -> str
gec12_describe_method(method: str) -> str
```

DM7 agent auto-discovers 340+ functions via `inspect.getmembers()`. GEC-12 agent wraps text retrieval + figure/table lookup functions (20 methods in 3 categories: Text Retrieval, GEC-12 Figures, GEC-12 Tables).

## Working on This Repo

1. Install: `pip install -e .`
2. Run tests: `pytest tests/ -q`
3. Each chapter file is self-contained (no cross-chapter imports)
4. When adding equations, follow existing patterns in the relevant chapter file

## Environment

- Python 3.10+ (developed on 3.14.3)
- No required dependencies (numpy/scipy/matplotlib are optional, used by some functions)
- Tests: `pytest tests/ -q` (expect 2,155 passed)
