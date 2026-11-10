"""UFC 3-220-04N — Backfill for Subsurface Structures.

Density requirements, Table 5-1 compaction criteria, backfill material
categories, lift thicknesses, compaction equipment and Figure 2-5's
compaction-induced lateral pressures, each read off the held UFC
3-220-04FA (16 January 2004; the reproduced TM 5-818-4/AFM 88-5,
Chap. 5), with its printed page in every result.

Usage::

    from geotech_references.ufc_backfill.tables import (
        table_compaction_requirements, table_5_1_compaction_criteria)

    req = table_compaction_requirements("open_area")
    # {'application': 'open_area', 'min_compaction_pct': 90, ...,
    #  'reference': '... para 5-1b(4), printed p. 5-2 (PDF 29)'}

    crit = table_5_1_compaction_criteria("CL", "compacted")
    # equipment, coverages and compacted lift thickness (in.) as printed
"""
