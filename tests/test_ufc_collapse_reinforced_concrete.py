"""Tests for geotech_references.ufc_collapse.reinforced_concrete (Chapter 4).

All numeric anchors are PRINTED TABLE values (Tables 4-1 through 4-4,
printed pp. 63-66), reproduced exactly at the printed grid points (no
interpolation needed at those exact points), plus SELF-CONSISTENCY checks
on the interpolation behavior between grid points.
"""

import pytest

from geotech_references.ufc_collapse.reinforced_concrete import (
    tie_rebar_phi,
    table_4_1_beam_flexure_modeling,
    table_4_1_beam_other_modeling,
    table_4_2_beam_flexure_mfactor,
    table_4_2_beam_other_mfactor,
    table_4_3_slab_flexure_modeling,
    table_4_3_slab_other_modeling,
    table_4_4_slab_flexure_mfactor,
    table_4_4_slab_other_mfactor,
)


class TestTieRebarPhi:
    def test_phi_0_75(self):
        assert tie_rebar_phi()["phi"] == 0.75


class TestTable41BeamFlexure:
    def test_conforming_low_rho_low_v(self):
        # PRINTED TABLE (p. 63): rho<=0.0, C, V<=3 -> a=0.063, b=0.10, c=0.2
        r = table_4_1_beam_flexure_modeling(0.0, "C", 3)
        assert r["a"] == pytest.approx(0.063)
        assert r["b"] == pytest.approx(0.10)
        assert r["c"] == pytest.approx(0.2)

    def test_nonconforming_high_rho_high_v(self):
        # PRINTED TABLE: rho>=0.5, NC, V>=6 -> a=0.013, b=0.02, c=0.2
        r = table_4_1_beam_flexure_modeling(0.5, "NC", 6)
        assert r["a"] == pytest.approx(0.013)
        assert r["b"] == pytest.approx(0.02)

    def test_conforming_high_rho_low_v(self):
        # PRINTED TABLE: rho>=0.5, C, V<=3 -> a=0.05, b=0.06
        r = table_4_1_beam_flexure_modeling(0.5, "C", 3)
        assert r["a"] == pytest.approx(0.05)
        assert r["b"] == pytest.approx(0.06)

    def test_acceptance_equals_a_b_as_extracted(self):
        # SELF-CONSISTENCY (flagged in module docstring): the printed
        # acceptance-criteria columns equal a (primary) and b (secondary)
        # exactly, as extracted.
        r = table_4_1_beam_flexure_modeling(0.0, "C", 3)
        assert r["primary_acceptance"] == r["a"]
        assert r["secondary_acceptance"] == r["b"]

    def test_interpolation_midpoint(self):
        # SELF-CONSISTENCY: at rho=0.25 (midpoint of 0.0/0.5), a should be
        # the average of the two grid endpoints for C, V<=3.
        r = table_4_1_beam_flexure_modeling(0.25, "C", 3)
        assert r["a"] == pytest.approx((0.063 + 0.05) / 2)

    def test_invalid_transverse_reinf_raises(self):
        with pytest.raises(ValueError):
            table_4_1_beam_flexure_modeling(0.0, "X", 3)


class TestTable41BeamOther:
    def test_shear_stirrup_le_d2(self):
        # PRINTED TABLE: shear-controlled, stirrup<=d/2 -> a=0.0030, b=0.02, c=0.2
        r = table_4_1_beam_other_modeling("shear", stirrup_spacing_le_d2=True)
        assert r["a"] == pytest.approx(0.0030)
        assert r["b"] == pytest.approx(0.02)

    def test_inadequate_embedment(self):
        # PRINTED TABLE: inadequate embedment -> a=0.015, b=0.03, c=0.2
        r = table_4_1_beam_other_modeling("inadequate_embedment")
        assert r["a"] == pytest.approx(0.015)
        assert r["b"] == pytest.approx(0.03)

    def test_development_c_is_zero(self):
        # PRINTED TABLE: development/splicing conditions have c=0.0
        # (unlike shear/flexure/embedment which have c=0.2)
        r = table_4_1_beam_other_modeling("development", stirrup_spacing_le_d2=True)
        assert r["c"] == pytest.approx(0.0)


class TestTable42BeamFlexureMfactor:
    def test_conforming_low_rho_low_v(self):
        # PRINTED TABLE (p. 64): rho<=0.0, C, V<=3 -> m_primary=16, m_secondary=19
        r = table_4_2_beam_flexure_mfactor(0.0, "C", 3)
        assert r["m_primary"] == pytest.approx(16)
        assert r["m_secondary"] == pytest.approx(19)

    def test_nonconforming_high_rho_high_v(self):
        # PRINTED TABLE: rho>=0.5, NC, V>=6 -> m_primary=4, m_secondary=5
        r = table_4_2_beam_flexure_mfactor(0.5, "NC", 6)
        assert r["m_primary"] == pytest.approx(4)
        assert r["m_secondary"] == pytest.approx(5)


class TestTable42BeamOther:
    def test_shear_stirrup_gt_d2(self):
        # PRINTED TABLE: shear, stirrup>d/2 -> m_primary=1.5, m_secondary=2
        r = table_4_2_beam_other_mfactor("shear", stirrup_spacing_le_d2=False)
        assert r["m_primary"] == pytest.approx(1.5)
        assert r["m_secondary"] == pytest.approx(2)

    def test_inadequate_embedment(self):
        r = table_4_2_beam_other_mfactor("inadequate_embedment")
        assert r["m_primary"] == pytest.approx(2)
        assert r["m_secondary"] == pytest.approx(3)


class TestTable43SlabFlexure:
    def test_continuity_low_vg(self):
        # PRINTED TABLE (p. 65): Vg/Vo<=0.2, continuity=Yes -> a=0.05, b=0.10, c=0.2
        r = table_4_3_slab_flexure_modeling(0.2, True)
        assert r["a"] == pytest.approx(0.05)
        assert r["b"] == pytest.approx(0.10)
        assert r["c"] == pytest.approx(0.2)

    def test_no_continuity_high_vg_zero(self):
        # PRINTED TABLE: Vg/Vo>=0.4, continuity=No -> a=0.0, b=0.0
        r = table_4_3_slab_flexure_modeling(0.4, False)
        assert r["a"] == pytest.approx(0.0)
        assert r["b"] == pytest.approx(0.0)

    def test_no_continuity_c_is_none(self):
        # SELF-CONSISTENCY: no residual capacity ('-' in the printed
        # table) is represented as None
        r = table_4_3_slab_flexure_modeling(0.2, False)
        assert r["c"] is None


class TestTable43SlabOther:
    def test_inadequate_embedment(self):
        r = table_4_3_slab_other_modeling("inadequate_embedment")
        assert r["a"] == pytest.approx(0.015)
        assert r["b"] == pytest.approx(0.03)

    def test_invalid_condition_raises(self):
        with pytest.raises(ValueError):
            table_4_3_slab_other_modeling("shear")


class TestTable44SlabFlexureMfactor:
    def test_continuity_low_vg(self):
        # PRINTED TABLE (p. 66): Vg/Vo<=0.2, continuity=Yes -> m_primary=6, m_secondary=7
        r = table_4_4_slab_flexure_mfactor(0.2, True)
        assert r["m_primary"] == pytest.approx(6)
        assert r["m_secondary"] == pytest.approx(7)

    def test_no_continuity_high_vg(self):
        # PRINTED TABLE: Vg/Vo>=0.4, continuity=No -> m_primary=1, m_secondary=1
        r = table_4_4_slab_flexure_mfactor(0.4, False)
        assert r["m_primary"] == pytest.approx(1)
        assert r["m_secondary"] == pytest.approx(1)


class TestTable44SlabOther:
    def test_development_primary_not_applicable(self):
        r = table_4_4_slab_other_mfactor("development")
        assert r["m_primary"] is None
        assert r["m_secondary"] == pytest.approx(4)

    def test_inadequate_embedment(self):
        r = table_4_4_slab_other_mfactor("inadequate_embedment")
        assert r["m_primary"] == pytest.approx(3)
        assert r["m_secondary"] == pytest.approx(4)
