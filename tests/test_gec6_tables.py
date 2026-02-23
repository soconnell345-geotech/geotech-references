"""Tests for GEC-6 table lookup functions."""

import pytest

from geotech_references.gec_6.tables import (
    table_4_1_spt_soil_properties,
    table_5_1_bearing_capacity_factors,
    table_5_4_depth_correction_factor,
    table_5_7_presumptive_bearing_rock,
    table_5_9_rqd_bearing_capacity,
    table_5_10_fill_bearing_capacity,
    table_5_12_shape_rigidity_factor,
    table_5_13_poissons_ratio_rock,
    table_5_14_youngs_modulus_rock,
    table_5_15_friction_factor,
)


# ============================================================================
# Table 4-1: SPT Soil Properties
# ============================================================================

class TestTable41:
    """Tests for table_4_1_spt_soil_properties()."""

    def test_sand_very_loose(self):
        assert table_4_1_spt_soil_properties(2, "sand")["relative_density"] == "very_loose"

    def test_sand_loose(self):
        assert table_4_1_spt_soil_properties(5, "sand")["relative_density"] == "loose"

    def test_sand_medium(self):
        assert table_4_1_spt_soil_properties(15, "sand")["relative_density"] == "medium"

    def test_sand_dense(self):
        assert table_4_1_spt_soil_properties(40, "sand")["relative_density"] == "dense"

    def test_sand_very_dense(self):
        assert table_4_1_spt_soil_properties(60, "sand")["relative_density"] == "very_dense"

    def test_clay_very_soft(self):
        assert table_4_1_spt_soil_properties(1, "clay")["consistency"] == "very_soft"

    def test_clay_soft(self):
        assert table_4_1_spt_soil_properties(3, "clay")["consistency"] == "soft"

    def test_clay_medium(self):
        assert table_4_1_spt_soil_properties(6, "clay")["consistency"] == "medium"

    def test_clay_stiff(self):
        assert table_4_1_spt_soil_properties(10, "clay")["consistency"] == "stiff"

    def test_clay_very_stiff(self):
        assert table_4_1_spt_soil_properties(20, "clay")["consistency"] == "very_stiff"

    def test_clay_hard(self):
        assert table_4_1_spt_soil_properties(35, "clay")["consistency"] == "hard"

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            table_4_1_spt_soil_properties(-1, "sand")

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError):
            table_4_1_spt_soil_properties(10, "peat")


# ============================================================================
# Table 5-1: Bearing Capacity Factors
# ============================================================================

class TestTable51:
    """Tests for table_5_1_bearing_capacity_factors()."""

    def test_phi_0(self):
        """phi=0: Nc=5.14, Nq=1.0, Ngamma=0.0."""
        result = table_5_1_bearing_capacity_factors(0)
        assert result["Nc"] == 5.14
        assert result["Nq"] == 1.0
        assert result["Ngamma"] == 0.0

    def test_phi_30(self):
        """phi=30: Nc=30.1, Nq=18.4, Ngamma=22.4."""
        result = table_5_1_bearing_capacity_factors(30)
        assert result["Nc"] == pytest.approx(30.1)
        assert result["Nq"] == pytest.approx(18.4)
        assert result["Ngamma"] == pytest.approx(22.4)

    def test_phi_45(self):
        """phi=45: Nc=133.9, Nq=134.9, Ngamma=271.8."""
        result = table_5_1_bearing_capacity_factors(45)
        assert result["Nc"] == pytest.approx(133.9)
        assert result["Nq"] == pytest.approx(134.9)
        assert result["Ngamma"] == pytest.approx(271.8)

    def test_phi_interpolation(self):
        """Intermediate phi interpolates."""
        result = table_5_1_bearing_capacity_factors(15.5)
        assert 11.0 < result["Nc"] < 11.6

    def test_phi_out_of_range_low(self):
        with pytest.raises(ValueError):
            table_5_1_bearing_capacity_factors(-1)

    def test_phi_out_of_range_high(self):
        with pytest.raises(ValueError):
            table_5_1_bearing_capacity_factors(50)


# ============================================================================
# Table 5-4: Depth Correction Factor
# ============================================================================

class TestTable54:
    """Tests for table_5_4_depth_correction_factor()."""

    def test_phi32_dfbf1(self):
        assert table_5_4_depth_correction_factor(32, 1) == pytest.approx(1.20)

    def test_phi37_dfbf4(self):
        assert table_5_4_depth_correction_factor(37, 4) == pytest.approx(1.30)

    def test_phi42_dfbf8(self):
        assert table_5_4_depth_correction_factor(42, 8) == pytest.approx(1.30)

    def test_interpolation(self):
        """Intermediate values interpolate correctly."""
        dq = table_5_4_depth_correction_factor(35, 2)
        assert 1.20 < dq < 1.30

    def test_phi_out_of_range(self):
        with pytest.raises(ValueError):
            table_5_4_depth_correction_factor(25, 2)

    def test_dfbf_out_of_range(self):
        with pytest.raises(ValueError):
            table_5_4_depth_correction_factor(35, 0.5)


# ============================================================================
# Table 5-7: Presumptive Rock Bearing
# ============================================================================

class TestTable57:
    """Tests for table_5_7_presumptive_bearing_rock()."""

    def test_massive_crystalline(self):
        result = table_5_7_presumptive_bearing_rock("massive")
        assert result["recommended_mpa"] == 7.7

    def test_foliated(self):
        result = table_5_7_presumptive_bearing_rock("foliated")
        assert result["recommended_mpa"] == 3.4

    def test_sedimentary(self):
        result = table_5_7_presumptive_bearing_rock("sedimentary")
        assert result["recommended_mpa"] == 1.9

    def test_weathered(self):
        result = table_5_7_presumptive_bearing_rock("weathered")
        assert result["recommended_mpa"] == 1.0

    def test_no_match_raises(self):
        with pytest.raises(ValueError):
            table_5_7_presumptive_bearing_rock("nonexistent")


# ============================================================================
# Table 5-9: RQD Bearing Capacity
# ============================================================================

class TestTable59:
    """Tests for table_5_9_rqd_bearing_capacity()."""

    def test_rqd_100(self):
        result = table_5_9_rqd_bearing_capacity(100)
        assert result["allowable_pressure_mpa"] == 29.0
        assert result["rock_mass_quality"] == "excellent"

    def test_rqd_75(self):
        result = table_5_9_rqd_bearing_capacity(75)
        assert result["allowable_pressure_mpa"] == 12.0

    def test_rqd_0(self):
        result = table_5_9_rqd_bearing_capacity(0)
        assert result["allowable_pressure_mpa"] == 1.0
        assert result["rock_mass_quality"] == "soil_like"

    def test_rqd_interpolation(self):
        result = table_5_9_rqd_bearing_capacity(50)
        assert result["allowable_pressure_mpa"] == 6.0

    def test_rqd_out_of_range(self):
        with pytest.raises(ValueError):
            table_5_9_rqd_bearing_capacity(-5)
        with pytest.raises(ValueError):
            table_5_9_rqd_bearing_capacity(101)


# ============================================================================
# Table 5-10: Fill Bearing Capacity
# ============================================================================

class TestTable510:
    """Tests for table_5_10_fill_bearing_capacity()."""

    def test_all_agencies(self):
        results = table_5_10_fill_bearing_capacity()
        assert len(results) == 3

    def test_washington(self):
        results = table_5_10_fill_bearing_capacity("washington")
        assert len(results) == 1
        assert results[0]["bearing_capacity_kpa"] == 290

    def test_no_match_raises(self):
        with pytest.raises(ValueError):
            table_5_10_fill_bearing_capacity("nonexistent")


# ============================================================================
# Table 5-12: Shape and Rigidity Factors
# ============================================================================

class TestTable512:
    """Tests for table_5_12_shape_rigidity_factor()."""

    def test_circle_center(self):
        assert table_5_12_shape_rigidity_factor("circle", "center") == 1.00

    def test_square_corner(self):
        assert table_5_12_shape_rigidity_factor("square", "corner") == 0.56

    def test_rectangle_center(self):
        cd = table_5_12_shape_rigidity_factor("rectangle", "center", 2.0)
        assert cd == pytest.approx(1.52)

    def test_rectangle_requires_lw(self):
        with pytest.raises(ValueError):
            table_5_12_shape_rigidity_factor("rectangle", "center")

    def test_unknown_shape_raises(self):
        with pytest.raises(ValueError):
            table_5_12_shape_rigidity_factor("hexagon", "center")


# ============================================================================
# Table 5-13: Poisson's Ratio for Rock
# ============================================================================

class TestTable513:
    """Tests for table_5_13_poissons_ratio_rock()."""

    def test_granite(self):
        result = table_5_13_poissons_ratio_rock("granite")
        assert result["mean"] == 0.20

    def test_sandstone(self):
        result = table_5_13_poissons_ratio_rock("sandstone")
        assert result["mean"] == 0.20

    def test_limestone(self):
        result = table_5_13_poissons_ratio_rock("limestone")
        assert result["mean"] == 0.23

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_5_13_poissons_ratio_rock("concrete")


# ============================================================================
# Table 5-14: Young's Modulus for Rock
# ============================================================================

class TestTable514:
    """Tests for table_5_14_youngs_modulus_rock()."""

    def test_granite(self):
        result = table_5_14_youngs_modulus_rock("granite")
        assert result["mean_GPa"] == pytest.approx(52.67)

    def test_sandstone(self):
        result = table_5_14_youngs_modulus_rock("sandstone")
        assert result["mean_GPa"] == pytest.approx(14.69)

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_5_14_youngs_modulus_rock("concrete")


# ============================================================================
# Table 5-15: Friction Factors
# ============================================================================

class TestTable515:
    """Tests for table_5_15_friction_factor()."""

    def test_rock(self):
        result = table_5_15_friction_factor("rock")
        assert result["tan_delta_min"] == 0.70
        assert result["delta_min_deg"] == 35

    def test_gravel(self):
        result = table_5_15_friction_factor("gravel")
        assert result["tan_delta_min"] == 0.55

    def test_silt(self):
        result = table_5_15_friction_factor("silt")
        assert result["tan_delta_min"] == 0.30
        assert result["delta_min_deg"] == 17

    def test_clay(self):
        result = table_5_15_friction_factor("clay")
        assert result["tan_delta_min"] == 0.30

    def test_no_match_raises(self):
        with pytest.raises(ValueError):
            table_5_15_friction_factor("nonexistent_material")
