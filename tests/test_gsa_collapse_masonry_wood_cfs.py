"""Tests for geotech_references.gsa_collapse.masonry_wood_cfs (Ch 6-8).

All anchors are PRINTED VALUE or SELF-CONSISTENCY checks.
"""

import pytest

from geotech_references.gsa_collapse.masonry_wood_cfs import (
    masonry_material_basis,
    masonry_phi_basis,
    wood_material_basis,
    wood_phi_basis,
    wood_time_effect_factor,
    cfs_material_basis,
    cfs_phi_basis,
    default_lower_bound_factor,
    masonry_wood_cfs_performance_level,
)


class TestMaterialAndPhiBasis:
    def test_masonry_material_basis(self):
        assert masonry_material_basis()["basis"] == "ASCE 41 Table 11-1"

    def test_masonry_phi_basis(self):
        assert masonry_phi_basis()["basis"] == "ACI 530"

    def test_wood_material_basis(self):
        assert "AF&PA/ASCE 16" in wood_material_basis()["basis"]

    def test_wood_phi_basis(self):
        assert wood_phi_basis()["basis"] == "AF&PA/AWC NDS"

    def test_cfs_material_basis(self):
        assert "light-metal-framing" in cfs_material_basis()["basis"]

    def test_cfs_phi_basis(self):
        assert cfs_phi_basis()["basis"] == "AISI/COS/NASPEC"


class TestWoodTimeEffectFactor:
    def test_lambda_is_one(self):
        # PRINTED VALUE: Section 7.3.
        assert wood_time_effect_factor()["lambda"] == 1.0


class TestDefaultLowerBoundFactor:
    def test_factor_is_0_85(self):
        r = default_lower_bound_factor()
        assert r["factor"] == pytest.approx(0.85)
        assert set(r["applies_to"]) == {"wood", "cold_formed_steel"}


class TestPerformanceLevel:
    @pytest.mark.parametrize("material", ["masonry", "wood", "cold_formed_steel"])
    def test_all_three_materials_stay_at_life_safety(self, material):
        # PRINTED VALUE: Commentary C6/C7/C8 -- unlike RC/steel (Chapters
        # 4-5), these three materials do NOT get upgraded to Collapse
        # Prevention.
        r = masonry_wood_cfs_performance_level(material)
        assert r["performance_level"] == "life_safety"

    def test_masonry_uses_asce_41_chapter_11(self):
        assert masonry_wood_cfs_performance_level("masonry")["asce_41_chapter"] == 11

    def test_wood_and_cfs_use_asce_41_chapter_12(self):
        assert masonry_wood_cfs_performance_level("wood")["asce_41_chapter"] == 12
        assert masonry_wood_cfs_performance_level("cold_formed_steel")["asce_41_chapter"] == 12

    def test_invalid_material_raises(self):
        with pytest.raises(ValueError):
            masonry_wood_cfs_performance_level("reinforced_concrete")
