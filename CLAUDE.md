# geotech-references

Standalone geotechnical reference library: digitized equations, figures, tables, and (future) structured reference text from NAVFAC DM7, FHWA GEC series, and other standards.

Consumed by [GeotechStaffEngineer](https://github.com/soconnell345-geotech/GeotechStaffEngineer) as a Git submodule.

## Architecture

```
geotech_references/           # Python package (pip install -e .)
  _interpolation.py            # Shared helpers (_linterp)
  _plotting.py                 # Shared matplotlib helpers (get_pyplot, setup_engineering_plot)
  dm7_1/                       # UFC 3-220-10 Soil Mechanics (8 chapters)
    chapter1.py ... chapter8.py
  dm7_2/                       # UFC 3-220-20 Foundations & Earth Structures (7 chapters)
    prologue.py, chapter2.py ... chapter7.py
  gec_12/                      # FHWA-NHI-16-009 Driven Piles (Phase 2 placeholder)
agents/
  dm7_agent.py                 # Foundry-style 3-function wrapper
tests/                         # 2,008 tests (pytest)
references/                    # Source PDFs (git-ignored)
```

## Key Conventions

- **All units SI**: meters, kPa, kN, degrees
- **No external dependencies** beyond Python stdlib + numpy/scipy (optional matplotlib for plots)
- **Function naming**: `figure_X_Y_*()` for figures, `table_X_Y_*()` for tables — matches UFC numbering
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

## Agent Pattern

The DM7 agent (`agents/dm7_agent.py`) follows the 3-function Foundry pattern:

```python
dm7_agent(method: str, params_json: str) -> str      # Run an equation
dm7_list_methods(category: str = "") -> str           # Browse methods
dm7_describe_method(method: str) -> str               # Get parameter docs
```

Auto-discovers all public functions via `inspect.getmembers()`. Handles name collisions with chapter prefixing.

## Working on This Repo

1. Install: `pip install -e .`
2. Run tests: `pytest tests/ -q`
3. Each chapter file is self-contained (no cross-chapter imports)
4. When adding equations, follow existing patterns in the relevant chapter file

## Environment

- Python 3.10+ (developed on 3.14.3)
- No required dependencies (numpy/scipy/matplotlib are optional, used by some functions)
- Tests: `pytest tests/ -q` (expect 2,008 passed)
