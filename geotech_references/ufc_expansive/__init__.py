"""UFC 3-220-07 — Foundations in Expansive Soils.

Swell potential classification, free swell and swell pressure estimation,
heave prediction, foundation selection, and pier design for expansive
soils per UFC 3-220-07 (NAVFAC).

Usage::

    from geotech_references.ufc_expansive.tables import table_swell_potential_classification
    from geotech_references.ufc_expansive.equations import free_swell_percent

    cls = table_swell_potential_classification(plasticity_index=45)
    # {'classification': 'high', 'pi_range': '35-55', ...}

    swell = free_swell_percent(plasticity_index=45)
    # ~6.1 %
"""
