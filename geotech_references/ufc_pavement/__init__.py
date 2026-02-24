"""UFC 3-260-02 — Pavement Design for Airfields.

CBR-based flexible and rigid pavement design, equivalent single wheel
load (ESWL), frost susceptibility classification, and aircraft loading
parameters per UFC 3-260-02 (NAVFAC).

Usage::

    from geotech_references.ufc_pavement.equations import cbr_to_subgrade_modulus_MPa_per_m
    from geotech_references.ufc_pavement.tables import table_frost_susceptibility

    k = cbr_to_subgrade_modulus_MPa_per_m(cbr=8.0)
    # ~26.8 MPa/m

    frost = table_frost_susceptibility("ML", fines_pct=65)
    # {'frost_group': 'F3', 'description': 'Gravelly soils, ...', ...}
"""
