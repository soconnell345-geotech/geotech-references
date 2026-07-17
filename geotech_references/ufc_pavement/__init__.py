"""UFC 3-250-01 -- Pavement Design for Roads, Streets, Walks, and Storage Areas.

Pavement design for roads and parking areas (14 November 2016) -- NOT
airfields (airfields are UFC 3-260-02, a separate DoD manual). Covers
flexible (CBR/Beta Criteria) and rigid (Westergaard-derived) pavement
thickness design, mixed-traffic equivalency, stabilized-layer and overlay
design, reinforced concrete pavement design, seasonal frost design, and
subsurface pavement drainage design.

Usage::

    from geotech_references.ufc_pavement.equations import (
        mixed_traffic_equivalent_esal,
        rigid_overlay_partially_bonded,
        reinforced_pavement_max_slab_length,
    )
    from geotech_references.ufc_pavement.tables import (
        table_4_1_subgrade_category,
        figure_e1_flexible_thickness,
        table_10_1_k_subgrade,
    )

    cat = table_4_1_subgrade_category(cbr=4.0)
    # {'category': 'D', 'representative_cbr': 3, ...}

    thickness = figure_e1_flexible_thickness(cbr=3, passes=1_000_000)
    # {'thickness_in': 16.4, ...}  -- matches the guide's Appendix G, G-1 example

    length = reinforced_pavement_max_slab_length(hr_in=7, fs_psi=60_000, s_pct=0.10)
    # {'l_ft_raw': 49.1, ...}  -- matches the guide's Appendix G, G-6 example
"""
