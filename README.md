# geotech-references

Digitized geotechnical reference library: callable Python functions for NAVFAC DM7 and FHWA GEC series equations, figures, and tables.

## Installation

```bash
pip install geotech-references
```

## Overview

This package provides 477 digitized functions from major geotechnical engineering references, turning published figures, tables, and equations into callable Python code.

```python
from geotech_references.dm7_1.chapter1 import table_1_4_uscs_classification

result = table_1_4_uscs_classification(
    gravel_pct=25, sand_pct=55, fines_pct=20,
    liquid_limit=35, plasticity_index=12
)
print(result)  # {'symbol': 'SC', 'description': 'Clayey sand'}
```

## Contents

### NAVFAC DM7 (382 functions, 2,008 tests)

| Module | Topic | Functions |
|--------|-------|-----------|
| `dm7_1.chapter1` | Identification & Classification | 24 |
| `dm7_1.chapter2` | Field Exploration & Testing | 20 |
| `dm7_1.chapter3` | Laboratory Testing | 18 |
| `dm7_1.chapter4` | Distribution of Stresses | 17 |
| `dm7_1.chapter5` | Consolidation & Settlement | 42 |
| `dm7_1.chapter6` | Seepage & Drainage | 19 |
| `dm7_1.chapter7` | Slope Stability | 10 |
| `dm7_1.chapter8` | Correlations for Soil Properties | 35 |
| `dm7_2.prologue` | Index Properties | 12 |
| `dm7_2.chapter2` | Earth Pressures | 26 |
| `dm7_2.chapter3` | Shallow Foundations | 22 |
| `dm7_2.chapter4` | Deep Foundations | 42 |
| `dm7_2.chapter5` | Bearing Capacity (Deep) | 62 |
| `dm7_2.chapter6` | Retaining Structures | 37 |
| `dm7_2.chapter7` | Slope Stability (Earth Structures) | 16 |

### FHWA GEC Series (95 functions, 802 tests)

| Module | Reference | Functions |
|--------|-----------|-----------|
| `gec_6` | Shallow Foundations (FHWA-SA-02-054) | 13 |
| `gec_7` | Soil Nail Walls (FHWA-NHI-14-007) | 15 |
| `gec_10` | Drilled Shafts (FHWA-NHI-10-016) | 10 |
| `gec_11` | MSE Walls & Slopes (FHWA-NHI-10-024) | 17 |
| `gec_12` | Driven Piles (FHWA-NHI-16-009) | 16 |
| `gec_13` | Ground Modification (FHWA-NHI-16-027) | 10 |
| `micropile` | Micropile Design (FHWA-NHI-05-039) | 14 |

### Text Retrieval

Structured chapter text is available for GEC-6, GEC-7, GEC-10, GEC-12, GEC-13, and Micropile references:

```python
from geotech_references._retrieval import search_sections

results = search_sections("gec_12", "pile setup")
for section in results:
    print(section["title"], "-", section["body"][:100])
```

## Agents

Pre-built Foundry-style agent wrappers are included for all 8 references:

```python
from agents.dm7_agent import dm7_agent, dm7_list_methods

# List available methods
print(dm7_list_methods("chapter1"))

# Call a specific function
result = dm7_agent("table_1_4_uscs_classification", '{"gravel_pct": 25, "sand_pct": 55, "fines_pct": 20, "liquid_limit": 35, "plasticity_index": 12}')
```

## License

MIT
