"""UFC 3-220-07 — Foundations in Expansive Soils.

Table 4-1's WES classification of potential swell, paragraph 5-4c's depth
of the active zone, Table 6-1's foundation systems, the grade-beam void
space of paragraph 6-4, Figure 5-4's total swell and Table 4-2's four
empirical swell relations (Vijayvergiya and Ghazzaly, Schneider and Poor,
McKeen-Lytton, Johnson), each read off UFC 3-220-07 (the reproduced
TM 5-818-7) with its printed page in every result.

Usage::

    from geotech_references.ufc_expansive.tables import (
        table_swell_potential_classification, table_grade_beam_void_space)

    cls = table_swell_potential_classification(plasticity_index=30)
    # {'classification': 'marginal', 'potential_swell_pct': '0.5-1.5', ...,
    #  'reference': '... Table 4-1, printed p. 4-1 (PDF 31)'}

    void = table_grade_beam_void_space(predicted_total_heave_in=4)
    # {'void_space_low_in': 8.0, 'void_space_high_in': 12.0, ...}
"""
