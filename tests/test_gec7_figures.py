"""Tests for GEC-7 figure lookup functions."""

import pytest

from geotech_references.gec_7.figures import (
    figure_4_3_friction_angle_spt,
    figure_5_11_basal_heave_nc,
)


# ============================================================================
# Figure 4.3: Friction Angle vs SPT N60 (Schmertmann 1975)
# ============================================================================

class TestFigure43:
    """Tests for figure_4_3_friction_angle_spt()."""

    def test_low_n_low_stress(self):
        """N60=5, sigma_v/Pa=0.5 should give ~30 degrees."""
        phi = figure_4_3_friction_angle_spt(5, 0.5)
        assert 28 <= phi <= 32

    def test_high_n_low_stress(self):
        """N60=50, sigma_v/Pa=0.5 should give ~44 degrees."""
        phi = figure_4_3_friction_angle_spt(50, 0.5)
        assert 42 <= phi <= 46

    def test_medium_n_medium_stress(self):
        """N60=30, sigma_v/Pa=1.0 should give ~38 degrees."""
        phi = figure_4_3_friction_angle_spt(30, 1.0)
        assert 36 <= phi <= 40

    def test_high_stress_lowers_phi(self):
        """Higher confining stress should give lower phi for same N."""
        phi_low = figure_4_3_friction_angle_spt(30, 0.5)
        phi_high = figure_4_3_friction_angle_spt(30, 3.0)
        assert phi_low > phi_high

    def test_zero_n(self):
        """N60=0 should give ~28 degrees for all stress levels."""
        phi = figure_4_3_friction_angle_spt(0, 1.0)
        assert phi == pytest.approx(28, abs=1)

    def test_interpolation(self):
        """Intermediate values should interpolate smoothly."""
        phi = figure_4_3_friction_angle_spt(25, 1.5)
        assert 30 <= phi <= 38

    def test_returns_float(self):
        phi = figure_4_3_friction_angle_spt(20, 1.0)
        assert isinstance(phi, float)

    def test_n_out_of_range_low(self):
        with pytest.raises(ValueError):
            figure_4_3_friction_angle_spt(-5, 1.0)

    def test_n_out_of_range_high(self):
        with pytest.raises(ValueError):
            figure_4_3_friction_angle_spt(80, 1.0)

    def test_stress_out_of_range_low(self):
        with pytest.raises(ValueError):
            figure_4_3_friction_angle_spt(20, 0.1)

    def test_stress_out_of_range_high(self):
        with pytest.raises(ValueError):
            figure_4_3_friction_angle_spt(20, 4.0)


# ============================================================================
# Figure 5.11: Basal Heave Nc
# ============================================================================

class TestFigure511:
    """Tests for figure_5_11_basal_heave_nc()."""

    def test_zero_h_be(self):
        """H/Be=0 should give Nc=5.14 for all Be/Le ratios."""
        assert figure_5_11_basal_heave_nc(0, 0.0) == pytest.approx(5.14)
        assert figure_5_11_basal_heave_nc(0, 1.0) == pytest.approx(5.14)

    def test_long_excavation_high_h_be(self):
        """Long excavation (Be/Le=0) at large H/Be should give ~6.2."""
        nc = figure_5_11_basal_heave_nc(5.0, 0.0)
        assert nc == pytest.approx(6.2, abs=0.1)

    def test_square_excavation_high_h_be(self):
        """Square excavation (Be/Le=1) at large H/Be should give ~9.0."""
        nc = figure_5_11_basal_heave_nc(5.0, 1.0)
        assert nc == pytest.approx(9.0, abs=0.2)

    def test_square_higher_than_long(self):
        """Square excavation should have higher Nc than long excavation."""
        nc_long = figure_5_11_basal_heave_nc(2.0, 0.0)
        nc_square = figure_5_11_basal_heave_nc(2.0, 1.0)
        assert nc_square > nc_long

    def test_interpolation_be_le(self):
        """Be/Le=0.5 should interpolate between 0 and 1."""
        nc_0 = figure_5_11_basal_heave_nc(2.0, 0.0)
        nc_05 = figure_5_11_basal_heave_nc(2.0, 0.5)
        nc_1 = figure_5_11_basal_heave_nc(2.0, 1.0)
        assert nc_0 < nc_05 < nc_1

    def test_h_be_out_of_range(self):
        with pytest.raises(ValueError):
            figure_5_11_basal_heave_nc(-1, 0.0)
        with pytest.raises(ValueError):
            figure_5_11_basal_heave_nc(6.0, 0.0)

    def test_be_le_out_of_range(self):
        with pytest.raises(ValueError):
            figure_5_11_basal_heave_nc(2.0, -0.1)
        with pytest.raises(ValueError):
            figure_5_11_basal_heave_nc(2.0, 1.5)
