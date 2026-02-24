"""UFC 3-220-04N — Backfill for Subsurface Structures.

Compaction criteria, material classification, lift thickness limits,
filter design criteria, and compaction-induced lateral pressures per
UFC 3-220-04N (NAVFAC).

Usage::

    from geotech_references.ufc_backfill.tables import table_compaction_requirements
    from geotech_references.ufc_backfill.equations import compaction_induced_pressure_kPa

    req = table_compaction_requirements("under_foundations")
    # {'application': 'under_foundations', 'min_compaction_pct': 95, ...}

    sigma_h = compaction_induced_pressure_kPa(
        roller_line_load_kN_per_m=30.0, depth_m=1.5,
        unit_weight_kN_per_m3=18.0, K0=0.5
    )
"""
