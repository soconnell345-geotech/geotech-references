"""Tests for geotech_references.gsa_collapse.structural_steel (Ch 5, plus
Appendix C Table C1.1).

Anchors are PRINTED TABLE values (page-verified against the rendered PDF)
or SELF-CONSISTENCY checks, PLUS cross-document CONSISTENCY checks against
geotech_references.ufc_collapse: Table 11 and Table C1.1 match UFC exactly;
Table 10 has THREE CONFIRMED printed differences from UFC Table 5-1 (both
page-verified against the rendered PDFs of both documents) -- see module
docstring.
"""

import pytest

from geotech_references.gsa_collapse.structural_steel import (
    column_axial_classification,
    table_10_fr_connection_mfactor,
    table_10_pr_stiff_connection_mfactor,
    table_10_pr_flexible_connection_mfactor,
    table_11_fr_connection_modeling,
    table_11_pr_stiff_connection_modeling,
    table_11_pr_flexible_connection_modeling,
    table_c1_1_connection_type,
    list_table_c1_1_connection_types,
    TABLE_C1_1_CONNECTION_TYPES,
)

from geotech_references.ufc_collapse.structural_steel import (
    table_5_1_fr_connection_mfactor as ufc_table_5_1_fr,
    table_5_1_pr_stiff_connection_mfactor as ufc_table_5_1_pr_stiff,
    table_5_1_pr_flexible_connection_mfactor as ufc_table_5_1_pr_flex,
    table_5_2_fr_connection_modeling as ufc_table_5_2_fr,
    table_5_2_pr_stiff_connection_modeling as ufc_table_5_2_pr_stiff,
    table_5_2_pr_flexible_connection_modeling as ufc_table_5_2_pr_flex,
    TABLE_C1_CONNECTION_TYPES as UFC_TABLE_C1_CONNECTION_TYPES,
)


class TestColumnAxialClassification:
    def test_high_axial_load_force_controlled(self):
        r = column_axial_classification(p=600.0, p_cl=1000.0)
        assert r["p_over_pcl"] == pytest.approx(0.6)
        assert r["classification"] == "force_controlled"

    def test_low_axial_load_interaction(self):
        r = column_axial_classification(p=400.0, p_cl=1000.0)
        assert r["classification"] == "interaction_p_force_m_deformation"

    def test_boundary_at_0_5_is_interaction(self):
        r = column_axial_classification(p=500.0, p_cl=1000.0)
        assert r["classification"] == "interaction_p_force_m_deformation"


class TestTable10LinearMfactors:
    def test_improved_wuf_bolted_web_page_verified(self):
        # PAGE-VERIFIED PRINTED VALUE (rendered PDF, printed p. 45):
        # primary=3.1-0.032d, secondary=6.2-0.065d.
        r = table_10_fr_connection_mfactor("improved_wuf_bolted_web", d=30.0)
        assert r["m_primary"] == pytest.approx(3.1 - 0.032 * 30.0)
        assert r["m_secondary"] == pytest.approx(6.2 - 0.065 * 30.0)

    def test_reduced_beam_section_page_verified(self):
        r = table_10_fr_connection_mfactor("reduced_beam_section", d=24.0)
        assert r["m_primary"] == pytest.approx(6.9 - 0.032 * 24.0)
        assert r["m_secondary"] == pytest.approx(8.4 - 0.032 * 24.0)

    def test_wuf_page_verified(self):
        r = table_10_fr_connection_mfactor("wuf", d=20.0)
        assert r["m_primary"] == pytest.approx(3.9 - 0.043 * 20.0)
        assert r["m_secondary"] == pytest.approx(5.5 - 0.064 * 20.0)

    def test_sideplate_matches_ufc(self):
        r = table_10_fr_connection_mfactor("sideplate", d=30.0)
        ufc = ufc_table_5_1_fr("sideplate", d=30.0)
        assert r["m_primary"] == pytest.approx(ufc["m_primary"])
        assert r["m_secondary"] == pytest.approx(ufc["m_secondary"])

    def test_invalid_connection_raises(self):
        with pytest.raises(ValueError):
            table_10_fr_connection_mfactor("bogus", d=20.0)

    @pytest.mark.parametrize("connection_type", [
        "improved_wuf_bolted_web", "reduced_beam_section", "wuf",
    ])
    def test_cross_check_vs_ufc_collapse_table_5_1_CONFIRMED_DIFFERENCE(self, connection_type):
        # CONFIRMED PRINTED VALUE DIFFERENCE (page-verified against both
        # rendered PDFs -- see module docstring): these three Fully
        # Restrained connection types differ numerically from
        # ufc_collapse's Table 5-1 digitization. Documented, NOT
        # reconciled.
        d = 24.0
        gsa = table_10_fr_connection_mfactor(connection_type, d)
        ufc = ufc_table_5_1_fr(connection_type, d)
        assert gsa["m_primary"] != pytest.approx(ufc["m_primary"], rel=0.05)

    def test_cross_check_vs_ufc_collapse_table_5_1_sideplate_MATCHES(self):
        d = 24.0
        gsa = table_10_fr_connection_mfactor("sideplate", d)
        ufc = ufc_table_5_1_fr("sideplate", d)
        assert gsa["m_primary"] == pytest.approx(ufc["m_primary"])
        assert gsa["m_secondary"] == pytest.approx(ufc["m_secondary"])

    def test_double_split_tee_page_verified(self):
        # PAGE-VERIFIED PRINTED VALUE (rendered PDF, printed p. 45):
        # shear-in-bolt m=(6, 8), tension-in-bolt m=(2.5, 4),
        # tension-in-tee m=(2, 2), flexure-in-tee m=(7, 14).
        cases = {
            "shear_in_bolt": (6, 8), "tension_in_bolt": (2.5, 4),
            "tension_in_tee": (2, 2), "flexure_in_tee": (7, 14),
        }
        for limit_state, (mp, ms) in cases.items():
            r = table_10_pr_stiff_connection_mfactor("double_split_tee", limit_state)
            assert r["m_primary"] == pytest.approx(mp)
            assert r["m_secondary"] == pytest.approx(ms)

    def test_double_split_tee_cross_check_CONFIRMED_DIFFERENCE(self):
        # CONFIRMED PRINTED VALUE DIFFERENCE: all four Double Split Tee
        # limit states differ from ufc_collapse's Table 5-1 digitization.
        gsa = table_10_pr_stiff_connection_mfactor("double_split_tee", "shear_in_bolt")
        ufc = ufc_table_5_1_pr_stiff("double_split_tee", "shear_in_bolt")
        assert gsa["m_primary"] == pytest.approx(6)
        assert ufc["m_primary"] == pytest.approx(4)
        assert gsa["m_primary"] != ufc["m_primary"]

    def test_double_angles_and_simple_shear_tab_MATCH_ufc(self):
        # CONFIRMED MATCH: Double Angles and Simple Shear Tab agree with
        # ufc_collapse's Table 5-1 digitization exactly.
        dbg = 18.0
        for conn, ls in [("double_angles", "shear_in_bolt"),
                          ("double_angles", "tension_in_bolt"),
                          ("double_angles", "flexure_in_angles"),
                          ("simple_shear_tab", None)]:
            gsa = table_10_pr_flexible_connection_mfactor(conn, dbg, ls)
            ufc = ufc_table_5_1_pr_flex(conn, dbg, ls)
            assert gsa["m_primary"] == pytest.approx(ufc["m_primary"])
            assert gsa["m_secondary"] == pytest.approx(ufc["m_secondary"])


class TestTable11NonlinearModeling:
    @pytest.mark.parametrize("connection_type", [
        "improved_wuf_bolted_web", "reduced_beam_section", "wuf", "sideplate",
    ])
    def test_fr_connections_match_ufc_table_5_2(self, connection_type):
        # CROSS-DOCUMENT CONSISTENCY: Table 11 is printed IDENTICALLY to
        # UFC 4-023-03 Table 5-2 for EVERY Fully Restrained connection
        # type (unlike Table 10, which differs for three of these four).
        d = 24.0
        gsa = table_11_fr_connection_modeling(connection_type, d)
        ufc = ufc_table_5_2_fr(connection_type, d)
        assert gsa["a"] == pytest.approx(ufc["a"])
        assert gsa["b"] == pytest.approx(ufc["b"])
        assert gsa["c"] == pytest.approx(ufc["c"])

    def test_pr_stiff_double_split_tee_matches_ufc(self):
        for limit_state in ("shear_in_bolt", "tension_in_bolt", "tension_in_tee", "flexure_in_tee"):
            gsa = table_11_pr_stiff_connection_modeling("double_split_tee", limit_state)
            ufc = ufc_table_5_2_pr_stiff("double_split_tee", limit_state)
            assert gsa["a"] == pytest.approx(ufc["a"])
            assert gsa["primary_acceptance"] == pytest.approx(ufc["primary_acceptance"])

    def test_pr_flexible_matches_ufc(self):
        dbg = 18.0
        for conn, ls in [("double_angles", "shear_in_bolt"),
                          ("double_angles", "flexure_in_angles"),
                          ("simple_shear_tab", None)]:
            gsa = table_11_pr_flexible_connection_modeling(conn, dbg, ls)
            ufc = ufc_table_5_2_pr_flex(conn, dbg, ls)
            assert gsa["a"] == pytest.approx(ufc["a"])
            assert gsa["b"] == pytest.approx(ufc["b"])

    def test_improved_wuf_bolted_web_page_verified_values(self):
        # PAGE-VERIFIED PRINTED VALUE: a=0.021-0.0003d, b=0.050-0.0006d, c=0.2.
        r = table_11_fr_connection_modeling("improved_wuf_bolted_web", d=20.0)
        assert r["a"] == pytest.approx(0.021 - 0.0003 * 20.0)
        assert r["b"] == pytest.approx(0.050 - 0.0006 * 20.0)
        assert r["c"] == pytest.approx(0.2)


class TestTableC11ConnectionTypes:
    def test_all_seventeen_types_present(self):
        assert len(TABLE_C1_1_CONNECTION_TYPES) == 17

    def test_reduced_beam_section_lookup(self):
        r = table_c1_1_connection_type("reduced_beam_section")
        assert r["restraint"] == "FR"
        assert r["table"] == "C1.1"

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            table_c1_1_connection_type("bogus")

    def test_list_by_restraint(self):
        fr = list_table_c1_1_connection_types("FR")
        pr = list_table_c1_1_connection_types("PR")
        assert "sideplate" in fr
        assert "double_split_tee" in pr
        assert "bolted_flange_plates" not in fr  # 'FR or PR', excluded from both filters
        assert "bolted_flange_plates" not in pr

    def test_cross_check_vs_ufc_collapse_restraint_classification_identical(self):
        # CROSS-DOCUMENT CONSISTENCY: Table C1.1's restraint (FR/PR)
        # classification matches UFC 4-023-03's Table C-1 for all 17
        # connection types.
        assert set(TABLE_C1_1_CONNECTION_TYPES) == set(UFC_TABLE_C1_CONNECTION_TYPES)
        for key, row in TABLE_C1_1_CONNECTION_TYPES.items():
            ufc_row = UFC_TABLE_C1_CONNECTION_TYPES[key]
            assert row["restraint"] == ufc_row["restraint"]

    def test_cross_check_vs_ufc_collapse_description_matches_13_of_17(self):
        # CROSS-DOCUMENT CONSISTENCY: 13 of 17 descriptions match
        # verbatim. Four rows are CONFIRMED printed wording differences
        # (page-verified against both rendered PDFs -- see module
        # docstring), transcribed here exactly as GSA prints them (incl.
        # GSA's own slightly awkward phrasing, e.g. "weld access holes to
        # separating" for slottedweb) rather than silently adopting UFC's
        # more polished wording for the same connections.
        mismatches = {
            key for key, row in TABLE_C1_1_CONNECTION_TYPES.items()
            if row["description"] != UFC_TABLE_C1_CONNECTION_TYPES[key]["description"]
        }
        assert mismatches == {
            "free_flange", "reduced_beam_section", "kaiser_bolted_bracket", "slottedweb",
        }
