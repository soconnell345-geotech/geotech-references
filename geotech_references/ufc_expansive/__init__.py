"""UFC 3-220-07 — Foundations in Expansive Soils.

Table 4-1's WES classification of potential swell, paragraph 5-4c's depth
of the active zone, Table 6-1's foundation systems, the grade-beam void
space of paragraph 6-4, Figure 5-4's total swell, Table 4-2's four
empirical swell relations (Vijayvergiya and Ghazzaly, Schneider and Poor,
McKeen-Lytton, Johnson), and the manual's other heave methods: Van Der
Merwe's Eq. 4-1 with Figure 4-1's potential expansiveness, the potential
vertical heave from void ratios (Eq. 5-2), the equilibrium pore water
pressure profiles (Eqs. 5-3 to 5-5) and the heave from consolidometer
tests (Eqs. 5-8 and 5-9). Each is read off UFC 3-220-07 (the reproduced
TM 5-818-7) with its printed page in every result.

Usage::

    from geotech_references.ufc_expansive.tables import (
        table_swell_potential_classification, table_grade_beam_void_space)

    cls = table_swell_potential_classification(plasticity_index=30)
    # {'classification': 'marginal', 'potential_swell_pct': '0.5-1.5', ...,
    #  'reference': '... Table 4-1, printed p. 4-1 (pdf_page_index 30)'}

    void = table_grade_beam_void_space(predicted_total_heave_in=4)
    # {'void_space_low_in': 8.0, 'void_space_high_in': 12.0, ...}
"""
