"""Tests for geotech_references.gsa_collapse.reinforced_concrete (Ch 4).

Anchors are PRINTED WORKED-EXAMPLE values (Appendix D), PRINTED TABLE
values, or SELF-CONSISTENCY checks, PLUS cross-document CONSISTENCY
checks against geotech_references.ufc_collapse (Tables 6/7 match UFC
Tables 4-1/4-2 exactly; Table 9 has two CONFIRMED printed differences
from UFC Table 4-4 -- both page-verified against the rendered PDFs of
both documents -- see module docstring).
"""

import pytest

from geotech_references.gsa_collapse.reinforced_concrete import (
    table_6_beam_flexure_modeling,
    table_6_beam_other_modeling,
    table_7_beam_flexure_mfactor,
    table_7_beam_other_mfactor,
    table_8_slab_flexure_modeling,
    table_8_slab_other_modeling,
    table_9_slab_flexure_mfactor,
    table_9_slab_other_mfactor,
    column_deformation_controlled_shear_check,
)

from geotech_references.ufc_collapse.reinforced_concrete import (
    table_4_1_beam_flexure_modeling as ufc_table_4_1,
    table_4_2_beam_flexure_mfactor as ufc_table_4_2,
    table_4_3_slab_flexure_modeling as ufc_table_4_3,
    table_4_4_slab_flexure_mfactor as ufc_table_4_4,
)


class TestTable6BeamFlexureModeling:
    def test_corner_c3_row(self):
        # PRINTED TABLE VALUE: (C, <3) rho0 row -> a=0.063, b=0.10, c=0.2.
        r = table_6_beam_flexure_modeling(0.0, "C", 3.0)
        assert r["a"] == pytest.approx(0.063)
        assert r["b"] == pytest.approx(0.10)
        assert r["c"] == pytest.approx(0.2)

    def test_corner_nc6_row(self):
        # PRINTED TABLE VALUE: (NC, >6) rho5 row -> a=0.013, b=0.02.
        r = table_6_beam_flexure_modeling(0.5, "NC", 6.0)
        assert r["a"] == pytest.approx(0.013)
        assert r["b"] == pytest.approx(0.02)

    def test_shear_condition(self):
        r = table_6_beam_other_modeling("shear", stirrup_spacing_le_d2=True)
        assert r["a"] == pytest.approx(0.003)
        assert r["b"] == pytest.approx(0.02)

    def test_invalid_transverse_reinf_raises(self):
        with pytest.raises(ValueError):
            table_6_beam_flexure_modeling(0.1, "X", 4.0)

    @pytest.mark.parametrize("rho,reinf,vw", [
        (0.0, "C", 3.0), (0.5, "C", 3.0), (0.0, "C", 6.0), (0.5, "C", 6.0),
        (0.0, "NC", 3.0), (0.5, "NC", 3.0), (0.0, "NC", 6.0), (0.5, "NC", 6.0),
        (0.037, "C", 3.88), (0.25, "NC", 4.5),
    ])
    def test_cross_check_vs_ufc_collapse_table_4_1(self, rho, reinf, vw):
        # CROSS-DOCUMENT CONSISTENCY: Table 6 is printed IDENTICALLY to
        # UFC 4-023-03 Table 4-1.
        gsa = table_6_beam_flexure_modeling(rho, reinf, vw)
        ufc = ufc_table_4_1(rho, reinf, vw)
        assert gsa["a"] == pytest.approx(ufc["a"])
        assert gsa["b"] == pytest.approx(ufc["b"])
        assert gsa["c"] == pytest.approx(ufc["c"])


class TestTable7BeamFlexureMfactor:
    def test_intermediate_result_at_vw_3(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D12, "m_a,3"): at
        # rho_diff_over_rho_bal=0.037, transverse_reinf='C', vw_ratio=3
        # (the single-axis rho-interpolation-only result) -> m=15.48.
        r = table_7_beam_flexure_mfactor(0.037, "C", 3.0)
        assert r["m_primary"] == pytest.approx(15.48, abs=0.01)

    def test_intermediate_result_at_vw_6(self):
        # FLAGGED PRINTED ARITHMETIC DISCREPANCY (p. D12, "m_a,6"): the
        # document states this same-rho, vw_ratio=6 result is m=8.88, but
        # applying its own printed interpolation formula to its own
        # Table 7 corner values (9 at rho=0, 6 at rho=0.5) at rho=0.037
        # gives m=8.778 (which would round to 8.78, not 8.88) -- a second
        # flagged discrepancy in this same worked example, alongside the
        # final-answer mismatch documented in the module docstring. This
        # function reproduces the mathematically correct 8.778.
        r = table_7_beam_flexure_mfactor(0.037, "C", 6.0)
        assert r["m_primary"] == pytest.approx(8.778, abs=0.001)

    def test_full_bilinear_result_does_not_match_printed_final_answer(self):
        # FLAGGED PRINTED ARITHMETIC DISCREPANCY (see module docstring):
        # the Appendix D worked example states the final bilinearly-
        # interpolated m-factor at vw_ratio=3.88 is 10.74 (printed
        # p. D13). Independently recomputing the document's OWN printed
        # formula -- m = [(3.88-3)/3]*(m_a,6-m_a,3)+m_a,3, using the
        # document's OWN printed m_a,3=15.48/m_a,6=8.88 -- gives 13.54,
        # NOT 10.74. This function reproduces the correct (13.54-ish)
        # recomputation, confirming the source document's own final
        # answer does not follow from its own displayed work.
        r = table_7_beam_flexure_mfactor(0.037, "C", 3.88)
        recomputed = (3.88 - 3.0) / 3.0 * (8.88 - 15.48) + 15.48
        assert r["m_primary"] == pytest.approx(recomputed, abs=0.05)
        assert r["m_primary"] != pytest.approx(10.74, abs=0.5)

    def test_corner_values_match_table(self):
        # PRINTED TABLE VALUE: (C, <3) rho0 -> m_primary=16, m_secondary=19.
        r = table_7_beam_flexure_mfactor(0.0, "C", 3.0)
        assert r["m_primary"] == pytest.approx(16)
        assert r["m_secondary"] == pytest.approx(19)

    def test_shear_condition_mfactor(self):
        r = table_7_beam_other_mfactor("shear", stirrup_spacing_le_d2=True)
        assert r["m_primary"] == pytest.approx(1.75)
        assert r["m_secondary"] == pytest.approx(4)

    @pytest.mark.parametrize("rho,reinf,vw", [
        (0.0, "C", 3.0), (0.5, "C", 3.0), (0.0, "C", 6.0), (0.5, "C", 6.0),
        (0.0, "NC", 3.0), (0.5, "NC", 3.0), (0.0, "NC", 6.0), (0.5, "NC", 6.0),
        (0.037, "C", 3.88),
    ])
    def test_cross_check_vs_ufc_collapse_table_4_2(self, rho, reinf, vw):
        # CROSS-DOCUMENT CONSISTENCY: Table 7 is printed IDENTICALLY to
        # UFC 4-023-03 Table 4-2.
        gsa = table_7_beam_flexure_mfactor(rho, reinf, vw)
        ufc = ufc_table_4_2(rho, reinf, vw)
        assert gsa["m_primary"] == pytest.approx(ufc["m_primary"])
        assert gsa["m_secondary"] == pytest.approx(ufc["m_secondary"])


class TestTable8SlabFlexureModeling:
    def test_yes_continuity_vg02(self):
        # PRINTED TABLE VALUE: (<=0.2, Yes) -> a=0.05, b=0.10, c=0.2.
        r = table_8_slab_flexure_modeling(0.2, True)
        assert r["a"] == pytest.approx(0.05)
        assert r["b"] == pytest.approx(0.10)
        assert r["c"] == pytest.approx(0.2)

    def test_no_continuity_residual_ratio_undefined(self):
        r = table_8_slab_flexure_modeling(0.3, False)
        assert r["c"] is None

    def test_development_condition(self):
        r = table_8_slab_other_modeling("development")
        assert r["a"] == pytest.approx(0.0)
        assert r["b"] == pytest.approx(0.02)

    @pytest.mark.parametrize("vg,continuity", [
        (0.2, True), (0.4, True), (0.3, True), (0.2, False), (0.4, False),
    ])
    def test_cross_check_vs_ufc_collapse_table_4_3(self, vg, continuity):
        # CROSS-DOCUMENT CONSISTENCY: Table 8's modeling parameters (a, b,
        # c) match UFC 4-023-03 Table 4-3 exactly (no confirmed
        # differences found for Table 8, unlike Table 9 below).
        gsa = table_8_slab_flexure_modeling(vg, continuity)
        ufc = ufc_table_4_3(vg, continuity)
        assert gsa["a"] == pytest.approx(ufc["a"])
        assert gsa["b"] == pytest.approx(ufc["b"])
        if gsa["c"] is None or ufc["c"] is None:
            assert gsa["c"] is None and ufc["c"] is None
        else:
            assert gsa["c"] == pytest.approx(ufc["c"])


class TestTable9SlabFlexureMfactor:
    def test_yes_continuity_vg02(self):
        # PRINTED TABLE VALUE: (<=0.2, Yes) -> m=(6, 7).
        r = table_9_slab_flexure_mfactor(0.2, True)
        assert r["m_primary"] == pytest.approx(6)
        assert r["m_secondary"] == pytest.approx(7)

    def test_no_continuity_vg02_page_verified_value(self):
        # PAGE-VERIFIED PRINTED VALUE (rendered PDF, printed p. 42):
        # (<=0.2, No) -> m=(3, 3) in THIS document.
        r = table_9_slab_flexure_mfactor(0.2, False)
        assert r["m_primary"] == pytest.approx(3)
        assert r["m_secondary"] == pytest.approx(3)

    def test_development_and_embedment_both_print_dash_primary(self):
        # PAGE-VERIFIED PRINTED VALUE (rendered PDF, printed p. 42): BOTH
        # "development" and "inadequate embedment" rows print primary='-'
        # (not applicable), secondary=4.
        dev = table_9_slab_other_mfactor("development")
        emb = table_9_slab_other_mfactor("inadequate_embedment")
        assert dev["m_primary"] is None
        assert dev["m_secondary"] == pytest.approx(4)
        assert emb["m_primary"] is None
        assert emb["m_secondary"] == pytest.approx(4)

    def test_invalid_condition_raises(self):
        with pytest.raises(ValueError):
            table_9_slab_other_mfactor("bogus")

    def test_cross_check_vs_ufc_collapse_table_4_4_yes_rows_match(self):
        # CROSS-DOCUMENT CONSISTENCY: the "Yes" continuity rows of Table 9
        # match UFC 4-023-03 Table 4-4 exactly.
        for vg in (0.2, 0.4):
            gsa = table_9_slab_flexure_mfactor(vg, True)
            ufc = ufc_table_4_4(vg, True)
            assert gsa["m_primary"] == pytest.approx(ufc["m_primary"])
            assert gsa["m_secondary"] == pytest.approx(ufc["m_secondary"])

    def test_cross_check_vs_ufc_collapse_table_4_4_no_row_02_CONFIRMED_DIFFERENCE(self):
        # CONFIRMED PRINTED VALUE DIFFERENCE (page-verified against both
        # rendered PDFs -- see module docstring): GSA prints (3, 3) for
        # Vg/Vo<=0.2/No-continuity; ufc_collapse's Table 4-4 digitization
        # has (2, 2) for the identical cell. NOT reconciled -- both
        # values are asserted here as the documented disagreement.
        gsa = table_9_slab_flexure_mfactor(0.2, False)
        ufc = ufc_table_4_4(0.2, False)
        assert gsa["m_primary"] == pytest.approx(3)
        assert gsa["m_secondary"] == pytest.approx(3)
        assert ufc["m_primary"] == pytest.approx(2)
        assert ufc["m_secondary"] == pytest.approx(2)
        assert gsa["m_primary"] != ufc["m_primary"]

    def test_cross_check_vs_ufc_collapse_table_4_4_inadequate_embedment_CONFIRMED_DIFFERENCE(self):
        # CONFIRMED PRINTED VALUE DIFFERENCE (page-verified -- see module
        # docstring): GSA prints primary='-' (not applicable) for
        # "inadequate embedment"; ufc_collapse's Table 4-4 digitization
        # has primary=3 for the identical row.
        from geotech_references.ufc_collapse.reinforced_concrete import (
            table_4_4_slab_other_mfactor as ufc_table_4_4_other,
        )
        gsa = table_9_slab_other_mfactor("inadequate_embedment")
        ufc = ufc_table_4_4_other("inadequate_embedment")
        assert gsa["m_primary"] is None
        assert ufc["m_primary"] == pytest.approx(3)
        assert gsa["m_secondary"] == pytest.approx(ufc["m_secondary"])  # secondary=4 agrees


class TestColumnShearClassification:
    def test_deformation_controlled_assumption_holds(self):
        # PRINTED WORKED-EXAMPLE VALUE (p. D13): the preliminary
        # assumption Vp/Vo <= 0.6.
        r = column_deformation_controlled_shear_check(vp=45.0, vo=100.0)
        assert r["vp_over_vo"] == pytest.approx(0.45)
        assert r["assumed_deformation_controlled"] is True

    def test_reclassified_as_force_controlled(self):
        r = column_deformation_controlled_shear_check(vp=70.0, vo=100.0)
        assert r["assumed_deformation_controlled"] is False
