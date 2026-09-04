"""Tests for geotech_references.ufc_collapse.masonry_wood_cfs (Chapters 6-8).

All anchors are PRINTED VALUE (the handful of numeric factors these
pointer-heavy chapters actually print) or pointer-source checks.
"""

from geotech_references.ufc_collapse.masonry_wood_cfs import (
    masonry_material_code_references,
    masonry_alternate_path_modeling_source,
    wood_time_effect_factor,
    wood_default_lower_bound_factor,
    wood_material_code_references,
    wood_alternate_path_modeling_source,
    cold_formed_steel_default_lower_bound_factor,
    cold_formed_steel_material_code_references,
    cold_formed_steel_alternate_path_modeling_source,
)


class TestMasonry:
    def test_material_code_pointers(self):
        r = masonry_material_code_references()
        assert r["overstrength_factor_source"] == "ASCE 41 Table 11-1"
        assert r["phi_source"] == "ACI 530"

    def test_ap_modeling_source(self):
        r = masonry_alternate_path_modeling_source()
        assert "Chapter 11" in r["source"]


class TestWood:
    def test_time_effect_factor_is_1(self):
        # PRINTED VALUE: Section 7-3 -- lambda = 1.0 for progressive collapse
        r = wood_time_effect_factor()
        assert r["lambda"] == 1.0

    def test_default_lower_bound_factor_0_85(self):
        r = wood_default_lower_bound_factor()
        assert r["lower_bound_factor"] == 0.85

    def test_phi_source_is_nds(self):
        r = wood_material_code_references()
        assert "NDS" in r["phi_source"]

    def test_ap_modeling_source(self):
        r = wood_alternate_path_modeling_source()
        assert "Chapter 12" in r["source"]


class TestColdFormedSteel:
    def test_default_lower_bound_factor_matches_wood(self):
        # SELF-CONSISTENCY: wood and CFS share the same 0.85 factor
        r = cold_formed_steel_default_lower_bound_factor()
        assert r["lower_bound_factor"] == 0.85

    def test_phi_source_is_aisi(self):
        r = cold_formed_steel_material_code_references()
        assert "AISI" in r["phi_source"]

    def test_ap_modeling_source_same_chapter_as_wood(self):
        # SELF-CONSISTENCY: wood and CFS both cite ASCE 41 Chapter 12
        r = cold_formed_steel_alternate_path_modeling_source()
        assert "Chapter 12" in r["source"]
