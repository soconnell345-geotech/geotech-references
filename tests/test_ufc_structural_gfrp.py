"""Tests for geotech_references.ufc_structural.gfrp (Appendix G [ADDITION])."""

import pytest

from geotech_references.ufc_structural.gfrp import (
    table_g1_material_property,
    gfrp_seismic_applicability,
    gfrp_fire_rating_limitation,
    gfrp_bend_strength_reduction_factor,
    gfrp_sustained_stress_limit,
    gfrp_environmental_reduction_factor,
    gfrp_temperature_limits,
    gfrp_uv_exposure_storage_limit,
)


class TestTableG1MaterialProperties:
    """Anchors: printed Table G-1 (p. 185)."""

    def test_modulus_of_elasticity(self):
        r = table_g1_material_property("modulus_of_elasticity")
        assert r["gfrp_ksi"] == 6500
        assert r["steel_astm_a615_ksi"] == 29000

    def test_gfrp_is_roughly_quarter_stiffness_of_steel(self):
        r = table_g1_material_property("modulus_of_elasticity")
        ratio = r["gfrp_ksi"] / r["steel_astm_a615_ksi"]
        assert ratio == pytest.approx(0.224, abs=0.01)

    def test_transverse_shear_strength(self):
        r = table_g1_material_property("transverse_shear_strength")
        assert r["gfrp_ksi"] == 19

    def test_gfrp_has_no_yield_point(self):
        r = table_g1_material_property("minimum_yield_strength")
        assert "none" in r["gfrp"].lower()

    def test_density(self):
        r = table_g1_material_property("density")
        assert r["steel_astm_a615_lb_per_ft3"] == 493

    def test_unknown_property_raises(self):
        with pytest.raises(ValueError):
            table_g1_material_property("poisson_ratio")


class TestSeismicApplicability:
    """Anchors: paragraph G-1.3 / G-4.4 (printed pp. 181-182, 208)."""

    @pytest.mark.parametrize("sdc", ["B", "C", "D", "E", "F"])
    def test_prohibited_in_sfrs_for_sdc_b_through_f(self, sdc):
        r = gfrp_seismic_applicability(sdc, is_part_of_lateral_force_resisting_system=True)
        assert r["permitted"] is False

    def test_permitted_in_sfrs_for_sdc_a(self):
        r = gfrp_seismic_applicability("A", is_part_of_lateral_force_resisting_system=True)
        assert r["permitted"] is True

    @pytest.mark.parametrize("sdc", ["A", "B", "C"])
    def test_permitted_in_non_sfrs_for_sdc_a_through_c(self, sdc):
        r = gfrp_seismic_applicability(sdc, is_part_of_lateral_force_resisting_system=False)
        assert r["permitted"] is True

    @pytest.mark.parametrize("sdc", ["D", "E", "F"])
    def test_not_permitted_in_non_sfrs_for_sdc_d_through_f(self, sdc):
        r = gfrp_seismic_applicability(sdc, is_part_of_lateral_force_resisting_system=False)
        assert r["permitted"] is False

    def test_invalid_sdc_raises(self):
        with pytest.raises(ValueError):
            gfrp_seismic_applicability("G", True)


class TestFireRatingLimitation:
    def test_max_fire_rating_is_zero(self):
        assert gfrp_fire_rating_limitation()["max_fire_rating"] == 0


class TestDesignFactors:
    """Anchors: paragraphs G-3.2, G-4.2, G-5.1, G-5.3 (printed pp. 184-188)."""

    def test_bend_strength_reduction(self):
        assert gfrp_bend_strength_reduction_factor()["bend_strength_fraction"] == 0.60

    def test_sustained_stress_limit(self):
        assert gfrp_sustained_stress_limit()["sustained_stress_fraction"] == 0.30

    def test_environmental_reduction_factor(self):
        assert gfrp_environmental_reduction_factor()["ce"] == 0.85

    def test_temperature_limits_consistent(self):
        r = gfrp_temperature_limits()
        assert r["min_glass_transition_temp_f"] - r["in_service_margin_below_tg_f"] == r["in_service_limit_f"]
        assert r["in_service_limit_f"] == 185

    def test_uv_exposure_storage_limit_stricter_than_aci(self):
        r = gfrp_uv_exposure_storage_limit()
        assert r["ufgs_03_30_00_limit_months"] < r["aci_440_5_limit_months"]
