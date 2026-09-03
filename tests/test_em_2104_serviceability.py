"""Tests for geotech_references.em_2104.serviceability (Chapter 3
serviceability, paragraphs 3-4 through 3-7)."""

import pytest

from geotech_references.em_2104.serviceability import (
    table_3_3_max_service_stress,
    table_3_4_single_load_factor,
    single_load_factor_design_moment,
    max_reinforcement_ratio,
    deflection_control_reinforcement_ratio,
    min_wall_thickness,
)


class TestTable33MaxServiceStress:
    def test_usual_flexure_shear(self):
        r = table_3_3_max_service_stress("usual")
        assert r["fs_ksi"] == 25.0

    def test_usual_direct_tension(self):
        r = table_3_3_max_service_stress("usual", "direct_tension")
        assert r["fs_ksi"] == 20.0

    def test_unusual_flexure_shear(self):
        assert table_3_3_max_service_stress("unusual")["fs_ksi"] == 35.0

    def test_unusual_direct_tension(self):
        r = table_3_3_max_service_stress("unusual", "direct_tension")
        assert r["fs_ksi"] == 27.5

    def test_bad_category_raises(self):
        with pytest.raises(ValueError):
            table_3_3_max_service_stress("extreme")


class TestTable34SingleLoadFactor:
    def test_usual_flexure_shear(self):
        assert table_3_4_single_load_factor("usual")["factor"] == 2.2

    def test_usual_direct_tension(self):
        assert table_3_4_single_load_factor("usual", "direct_tension")["factor"] == 2.8

    def test_unusual_flexure_shear(self):
        assert table_3_4_single_load_factor("unusual")["factor"] == 1.6

    def test_unusual_direct_tension(self):
        r = table_3_4_single_load_factor("unusual", "direct_tension")
        assert r["factor"] == 2.0


class TestSingleLoadFactorDesignMoment:
    def test_matches_appendix_d3(self):
        # Appendix D-3 Step 1: M = 5 k-ft usual -> Mu = 2.2*5 = 11 k-ft
        # (printed p. 74).
        r = single_load_factor_design_moment(5.0, "usual")
        assert r["mu"] == pytest.approx(11.0)

    def test_matches_appendix_d4(self):
        # Appendix D-4 Step 1: M = 95 k-ft usual -> Mu = 2.2*95 = 209 k-ft
        # (printed p. 77).
        r = single_load_factor_design_moment(95.0, "usual")
        assert r["mu"] == pytest.approx(209.0)


class TestReinforcementRatioLimits:
    def test_max_ratio_is_half_balanced(self):
        r = max_reinforcement_ratio(0.02851)
        assert r["rho_max"] == pytest.approx(0.014255)

    def test_deflection_control_is_quarter_balanced(self):
        # Appendix D-3 Step 4: 0.25*rho_b = 0.25*0.02851... matches
        # printed 0.0071 (rounded), rho_b computed with fc'=4, fy=60.
        r = deflection_control_reinforcement_ratio(0.0285)
        assert r["rho_deflection_limit"] == pytest.approx(0.007125, abs=1e-4)


class TestMinWallThickness:
    def test_tall_wall_min_12in(self):
        r = min_wall_thickness(height_ft=15.0)
        assert r["governing_min_in"] == 12.0

    def test_short_wall_absolute_min_8in(self):
        r = min_wall_thickness(height_ft=5.0)
        assert r["governing_min_in"] == 8.0

    def test_both_faces_required_flag(self):
        r = min_wall_thickness(height_ft=15.0, thickness_in=12.0)
        assert r["both_faces_required"] is True
        assert r["adequate"] is True

    def test_inadequate_thickness(self):
        r = min_wall_thickness(height_ft=15.0, thickness_in=10.0)
        assert r["adequate"] is False
