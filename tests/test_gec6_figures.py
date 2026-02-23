"""Tests for GEC-6 figure lookup functions."""

import pytest

from geotech_references.gec_6.figures import (
    figure_4_1_relative_density_spt,
    figure_4_2_friction_angle_from_density,
    figure_5_19_hough_bearing_capacity_index,
)


# ============================================================================
# Figure 4-1: Relative Density from SPT
# ============================================================================

class TestFigure41:
    """Tests for figure_4_1_relative_density_spt()."""

    def test_low_n_low_stress(self):
        """Low N at low stress = low Dr."""
        dr = figure_4_1_relative_density_spt(2, 48)
        assert 15 <= dr <= 50

    def test_high_n_low_stress(self):
        """High N at low stress = high Dr."""
        dr = figure_4_1_relative_density_spt(40, 48)
        assert 80 <= dr <= 100

    def test_medium_n_medium_stress(self):
        """Medium N at medium stress."""
        dr = figure_4_1_relative_density_spt(20, 96)
        assert 50 <= dr <= 80

    def test_returns_float(self):
        dr = figure_4_1_relative_density_spt(10, 48)
        assert isinstance(dr, float)

    def test_stress_out_of_range_low(self):
        with pytest.raises(ValueError):
            figure_4_1_relative_density_spt(10, 10)

    def test_stress_out_of_range_high(self):
        with pytest.raises(ValueError):
            figure_4_1_relative_density_spt(10, 250)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            figure_4_1_relative_density_spt(-5, 48)


# ============================================================================
# Figure 4-2: Friction Angle from Density
# ============================================================================

class TestFigure42:
    """Tests for figure_4_2_friction_angle_from_density()."""

    def test_low_density_dr0(self):
        """Low density, Dr=0 gives low phi."""
        phi = figure_4_2_friction_angle_from_density(14.1, 0)
        assert 25 <= phi <= 30

    def test_high_density_dr100(self):
        """High density, Dr=100 gives high phi."""
        phi = figure_4_2_friction_angle_from_density(22.0, 100)
        assert 40 <= phi <= 45

    def test_medium_density_dr50(self):
        """Medium density, Dr=50."""
        phi = figure_4_2_friction_angle_from_density(18.9, 50)
        assert 33 <= phi <= 37

    def test_gamma_out_of_range_low(self):
        with pytest.raises(ValueError):
            figure_4_2_friction_angle_from_density(10.0, 50)

    def test_gamma_out_of_range_high(self):
        with pytest.raises(ValueError):
            figure_4_2_friction_angle_from_density(25.0, 50)

    def test_dr_out_of_range(self):
        with pytest.raises(ValueError):
            figure_4_2_friction_angle_from_density(18.9, -10)


# ============================================================================
# Figure 5-19: Hough Bearing Capacity Index
# ============================================================================

class TestFigure519:
    """Tests for figure_5_19_hough_bearing_capacity_index()."""

    def test_zero_n(self):
        """N'=0 gives C'=0 for all soil types."""
        assert figure_5_19_hough_bearing_capacity_index(0, "sandy_clay") == 0

    def test_inorganic_silt_n50(self):
        """Inorganic silt at N'=50."""
        c_prime = figure_5_19_hough_bearing_capacity_index(50, "inorganic_silt")
        assert 75 <= c_prime <= 85

    def test_well_graded_sand_n30(self):
        """Well-graded sand at N'=30."""
        c_prime = figure_5_19_hough_bearing_capacity_index(30, "well_graded_sand_gravel")
        assert 88 <= c_prime <= 96

    def test_coarse_sand_n50(self):
        """Coarse sand at N'=50."""
        c_prime = figure_5_19_hough_bearing_capacity_index(50, "coarse_sand")
        assert 175 <= c_prime <= 190

    def test_clean_uniform_medium_sand(self):
        """Clean uniform medium sand at N'=40."""
        c_prime = figure_5_19_hough_bearing_capacity_index(40, "clean_uniform_medium_sand")
        assert 130 <= c_prime <= 145

    def test_interpolation(self):
        """N'=25 interpolates between data points."""
        c_prime = figure_5_19_hough_bearing_capacity_index(25, "sandy_clay")
        assert 50 < c_prime < 65

    def test_n_out_of_range(self):
        with pytest.raises(ValueError):
            figure_5_19_hough_bearing_capacity_index(-5, "sandy_clay")
        with pytest.raises(ValueError):
            figure_5_19_hough_bearing_capacity_index(110, "sandy_clay")

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError):
            figure_5_19_hough_bearing_capacity_index(20, "organic_peat")

    def test_partial_match(self):
        """Partial soil type matching works."""
        c_prime = figure_5_19_hough_bearing_capacity_index(20, "silt")
        assert c_prime > 0
