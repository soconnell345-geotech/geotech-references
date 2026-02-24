"""UFC 3-220-05 — Dewatering and Groundwater Control.

Well flow equations (Thiem/Dupuit), radius of influence, wellpoint
spacing, superposition of drawdown, and dewatering method selection
per UFC 3-220-05 (NAVFAC).

Usage::

    from geotech_references.ufc_dewatering.equations import thiem_confined_flow_m3_per_s
    from geotech_references.ufc_dewatering.tables import table_dewatering_method_selection

    Q = thiem_confined_flow_m3_per_s(
        k_m_per_s=1e-4, aquifer_thickness_m=10.0,
        drawdown_m=5.0, radius_of_influence_m=300.0, well_radius_m=0.15
    )

    method = table_dewatering_method_selection("sand")
    # {'soil_type': 'sand', 'primary_method': 'wellpoints', ...}
"""
