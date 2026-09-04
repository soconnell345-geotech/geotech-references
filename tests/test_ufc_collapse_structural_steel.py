"""Tests for geotech_references.ufc_collapse.structural_steel (Chapter 5)
and Appendix C Table C-1.

Numeric anchors are PRINTED TABLE values (Tables 5-1/5-2, printed pp. 69-70,
and Table C-1, printed p. 111), plus SELF-CONSISTENCY checks.
"""

import pytest

from geotech_references.ufc_collapse.structural_steel import (
    column_axial_classification,
    table_5_1_fr_connection_mfactor,
    table_5_1_pr_stiff_connection_mfactor,
    table_5_1_pr_flexible_connection_mfactor,
    table_5_2_fr_connection_modeling,
    table_5_2_pr_stiff_connection_modeling,
    table_5_2_pr_flexible_connection_modeling,
    table_c1_connection_type,
    list_table_c1_connection_types,
    TABLE_C1_CONNECTION_TYPES,
)


class TestColumnAxialClassification:
    def test_high_axial_force_controlled(self):
        r = column_axial_classification(p=60, p_cl=100)
        assert r["p_over_pcl"] == pytest.approx(0.6)
        assert r["classification"] == "force_controlled"

    def test_low_axial_interaction(self):
        r = column_axial_classification(p=40, p_cl=100)
        assert r["classification"] == "interaction_p_force_m_deformation"

    def test_boundary_at_0_5_is_interaction(self):
        # SELF-CONSISTENCY: P/PCL exactly 0.5 is NOT > 0.5, so interaction applies
        r = column_axial_classification(p=50, p_cl=100)
        assert r["classification"] == "interaction_p_force_m_deformation"


class TestTable51FrConnections:
    def test_improved_wuf_bolted_web(self):
        # PRINTED TABLE (p. 69): m = 2.3-0.021d (primary), 4.9-0.048d (secondary)
        r = table_5_1_fr_connection_mfactor("improved_wuf_bolted_web", d=30)
        assert r["m_primary"] == pytest.approx(2.3 - 0.021 * 30)
        assert r["m_secondary"] == pytest.approx(4.9 - 0.048 * 30)

    def test_reduced_beam_section(self):
        r = table_5_1_fr_connection_mfactor("reduced_beam_section", d=24)
        assert r["m_primary"] == pytest.approx(4.9 - 0.025 * 24)
        assert r["m_secondary"] == pytest.approx(6.5 - 0.025 * 24)

    def test_sideplate(self):
        r = table_5_1_fr_connection_mfactor("sideplate", d=20)
        assert r["m_primary"] == pytest.approx(6.7 - 0.039 * 20)
        assert r["m_secondary"] == pytest.approx(11.1 - 0.062 * 20)

    def test_unknown_connection_raises(self):
        with pytest.raises(ValueError):
            table_5_1_fr_connection_mfactor("unknown", d=24)


class TestTable51PrStiff:
    def test_double_split_tee_shear_in_bolt(self):
        # PRINTED TABLE: shear in bolt -> m_primary=4, m_secondary=6
        r = table_5_1_pr_stiff_connection_mfactor("double_split_tee", "shear_in_bolt")
        assert r["m_primary"] == 4
        assert r["m_secondary"] == 6

    def test_double_split_tee_flexure_in_tee(self):
        r = table_5_1_pr_stiff_connection_mfactor("double_split_tee", "flexure_in_tee")
        assert r["m_primary"] == 5
        assert r["m_secondary"] == 7


class TestTable51PrFlexible:
    def test_double_angles_shear_in_bolt(self):
        # PRINTED TABLE: m = 5.8-0.107*dbg (primary), 8.7-0.161*dbg (secondary)
        r = table_5_1_pr_flexible_connection_mfactor("double_angles", dbg=10, limit_state="shear_in_bolt")
        assert r["m_primary"] == pytest.approx(5.8 - 0.107 * 10)
        assert r["m_secondary"] == pytest.approx(8.7 - 0.161 * 10)

    def test_simple_shear_tab(self):
        r = table_5_1_pr_flexible_connection_mfactor("simple_shear_tab", dbg=9)
        assert r["m_primary"] == pytest.approx(5.8 - 0.107 * 9)
        assert r["m_secondary"] == pytest.approx(8.7 - 0.161 * 9)


class TestTable52FrConnections:
    def test_wuf(self):
        # PRINTED TABLE (p. 70): a=0.0284-0.0004d, b=0.043-0.0006d, c=0.2
        r = table_5_2_fr_connection_modeling("wuf", d=30)
        assert r["a"] == pytest.approx(0.0284 - 0.0004 * 30)
        assert r["b"] == pytest.approx(0.043 - 0.0006 * 30)
        assert r["c"] == 0.2

    def test_sideplate_c_is_0_6(self):
        # PRINTED TABLE: SidePlate(R) has a distinct residual-strength
        # ratio c=0.6 (unlike the other FR connections' c=0.2)
        r = table_5_2_fr_connection_modeling("sideplate", d=20)
        assert r["c"] == 0.6

    def test_acceptance_equals_a_b(self):
        r = table_5_2_fr_connection_modeling("reduced_beam_section", d=24)
        assert r["primary_acceptance"] == r["a"]
        assert r["secondary_acceptance"] == r["b"]


class TestTable52PrStiff:
    def test_double_split_tee_tension_in_bolt(self):
        # PRINTED TABLE: tension in bolt -> a=0.016, b=0.024, c=0.8, primary=0.013, secondary=0.020
        r = table_5_2_pr_stiff_connection_modeling("double_split_tee", "tension_in_bolt")
        assert r["a"] == pytest.approx(0.016)
        assert r["c"] == pytest.approx(0.8)
        assert r["primary_acceptance"] == pytest.approx(0.013)
        assert r["secondary_acceptance"] == pytest.approx(0.020)


class TestTable52PrFlexible:
    def test_double_angles_flexure_in_angles(self):
        # PRINTED TABLE: a=0.1125-0.0027*dbg, c=0.4
        r = table_5_2_pr_flexible_connection_modeling("double_angles", dbg=9, limit_state="flexure_in_angles")
        assert r["a"] == pytest.approx(0.1125 - 0.0027 * 9)
        assert r["c"] == pytest.approx(0.4)


class TestTableC1ConnectionTypes:
    def test_reduced_beam_section_is_fr(self):
        r = table_c1_connection_type("reduced_beam_section")
        assert r["restraint"] == "FR"
        assert r["table"] == "C-1"

    def test_shear_tab_is_pr(self):
        r = table_c1_connection_type("shear_tab_connection")
        assert r["restraint"] == "PR"

    def test_all_entries_have_required_fields(self):
        for key in TABLE_C1_CONNECTION_TYPES:
            r = table_c1_connection_type(key)
            assert r["description"]
            assert r["restraint"] in ("FR", "PR", "FR or PR")
            assert r["figure"]

    def test_list_filter_by_restraint(self):
        fr_list = list_table_c1_connection_types("FR")
        pr_list = list_table_c1_connection_types("PR")
        assert "sideplate" in fr_list
        assert "double_split_tee" in pr_list
        assert set(fr_list) & set(pr_list) == set()

    def test_unknown_connection_raises(self):
        with pytest.raises(ValueError):
            table_c1_connection_type("nonexistent")
