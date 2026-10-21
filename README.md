# geotech-references

Digitized geotechnical reference library: callable Python functions for NAVFAC DM7 and FHWA GEC series equations, figures, and tables.

## Installation

```bash
pip install geotech-references
```

## Overview

This package provides 1,233 digitized functions from 33 reference packages, turning published figures, tables, and equations into callable Python code. 31 of the 33 packages also carry structured chapter text (see Text Retrieval below).

```python
from geotech_references.dm7_1.chapter1 import table_1_4_uscs_classification

result = table_1_4_uscs_classification(
    gravel_pct=25, sand_pct=55, fines_pct=20,
    liquid_limit=35, plasticity_index=12
)
print(result)  # {'symbol': 'SC', 'description': 'Clayey sand'}
```

## Contents

Function counts are the public functions defined in each package's modules (counted with `inspect`). A dash means the package is text only: it has chapter text and a figure catalog but no callable functions.

### Soil mechanics and foundations: DM 7 (393 functions)

| Module | Reference | Functions |
|--------|-----------|-----------|
| `dm7_1` | UFS 3-220-10 Soil Mechanics (DM 7.1), 16 January 2026 | 147 |
| `dm7_2` | UFC 3-220-20 Foundations and Earth Structures (DM 7.2) | 246 |

### FHWA geotechnical manuals and micropiles (146 functions)

| Module | Reference | Functions |
|--------|-----------|-----------|
| `gec_4` | Ground Anchors and Anchored Systems (FHWA-IF-99-015) | 6 |
| `gec_5` | Geotechnical Site Characterization (FHWA NHI-16-072) | - |
| `gec_6` | Shallow Foundations (FHWA-SA-02-054) | 13 |
| `gec_7` | Soil Nail Walls (FHWA-NHI-14-007) | 15 |
| `gec_8` | Design and Construction of Continuous Flight Auger Piles (FHWA-HIF-07-03) | 5 |
| `gec_9` | Laterally Loaded Deep Foundations (FHWA-HIF-18-031) | 5 |
| `gec_10` | Drilled Shafts: Construction Procedures and LRFD Design Methods (FHWA-NHI-18-024, 2018) | 12 |
| `gec_11` | MSE Walls and Reinforced Soil Slopes (FHWA-NHI-10-024, -025) | 17 |
| `gec_12` | Design and Construction of Driven Pile Foundations (FHWA-NHI-16-009) | 16 |
| `gec_13` | Ground Modification Methods (FHWA-NHI-16-027) | 18 |
| `gec_14` | Assuring Quality in Geotechnical Reporting Documents (FHWA-HIF-17-016) | - |
| `micropile` | Micropile Design and Construction (FHWA-NHI-05-039) | 14 |
| `fhwa_soils_foundations` | Soils and Foundations Reference Manual, Volumes I and II (FHWA-NHI-06-088, -089) | - |
| `fhwa_pavements` | Geotechnical Aspects of Pavements (FHWA-NHI-05-037) | 25 |

### Other geotechnical and seismic references (118 functions)

| Module | Reference | Functions |
|--------|-----------|-----------|
| `california_trenching` | California Trenching and Shoring Manual (Caltrans) | 32 |
| `fema_p2082` | 2020 NEHRP Recommended Seismic Provisions (FEMA P-2082-1) | 12 |
| `eurocode_7_1` | EN 1997-1:2004 Eurocode 7, Part 1: General Rules | 31 |
| `eurocode_7_2` | EN 1997-2:2007 Eurocode 7, Part 2: Ground Investigation and Testing | 43 |

### UFC pavement, soils and structural criteria (576 functions)

| Module | Reference | Functions |
|--------|-----------|-----------|
| `ufc_backfill` | UFC 3-220-04N Backfill for Subsurface Structures | 8 |
| `ufc_expansive` | UFC 3-220-07 Foundations in Expansive Soils | 9 |
| `ufc_pavement` | UFC 3-250-01 Pavement Design for Roads, Streets, Walks, and Storage Areas | 53 |
| `ufc_stabilization` | UFC 3-250-11 Soil Stabilization and Modification for Pavements | 17 |
| `ufc_flexible_practice` | UFC 3-250-03 Standard Practice Manual for Flexible Pavements | 36 |
| `ufc_concrete_practice` | UFC 3-250-04 Standard Practice for Concrete Pavements | 18 |
| `aashto_1993` | AASHTO Guide for Design of Pavement Structures, 1993 | 52 |
| `ufc_structural` | UFC 3-301-01 Structural Engineering | 66 |
| `ufc_collapse` | UFC 4-023-03 Design of Buildings to Resist Progressive Collapse | 77 |
| `gsa_collapse` | GSA Alternate Path Analysis and Design Guidelines for Progressive Collapse Resistance | 63 |
| `em_2104` | EM 1110-2-2104 Strength Design for Reinforced Concrete Hydraulic Structures | 47 |
| `em_2107` | EM 1110-2-2107 Design of Hydraulic Steel Structures | 49 |
| `wood_handbook` | Wood Handbook: Wood as an Engineering Material (FPL-GTR-282) | 81 |

### Text Retrieval

Structured chapter text is available for 31 of the 33 packages (all but `ufc_backfill` and `ufc_expansive`). List them with `geotech_references._retrieval_db.list_indexed_references()`:

```python
from geotech_references._retrieval import search_sections

results = search_sections("gec_12", "pile setup")
for section in results:
    print(section["title"], "-", section["body"][:100])
```

## Agents

Pre-built Foundry-style agent wrappers are included in the `agents/` directory: 19 per-reference wrappers (`dm7_agent` covers both DM 7 volumes) and a generic `references_agent`. The remaining packages have no wrapper. These are standalone files for Palantir Foundry AIP Agent Studio — they are **not** part of the pip-installable `geotech-references` package. Copy them into your Foundry function repository as needed.

```python
from agents.dm7_agent import dm7_agent, dm7_list_methods

# List available methods
print(dm7_list_methods("chapter1"))

# Call a specific function
result = dm7_agent("table_1_4_uscs_classification", '{"gravel_pct": 25, "sand_pct": 55, "fines_pct": 20, "liquid_limit": 35, "plasticity_index": 12}')
```

## Source documents

`docs/` holds the PDFs the modules were built from. Most are U.S. government publications: FHWA, USACE, UFC, FEMA, USDA, GSA and Caltrans.

Three are standards from other publishers. They are kept here because copies are openly available online:
- `docs/aashto1993.pdf`: AASHTO Guide for Design of Pavement Structures, 1993 Edition. Where this copy came from was not recorded.
- `docs/en.1997.2.2007-1.pdf`: EN 1997-2:2007, Eurocode 7 Part 2, a Public.Resource.Org copy.
- `docs/eurocode_7_-_geotechnical_designen.1997.1.2004.pdf`: EN 1997-1:2004, Eurocode 7 Part 1, a Public.Resource.Org scan of BS EN 1997-1:2004.

Copyright in these three stays with their publishers. The MIT licence below covers this package's code, not the source documents.

## License

MIT
