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
    """Tests for figure_4_3_friction_angle_spt(). Expected values are the
    points read off GEC-7 Figure 4.3, p. 79 (PDF page 119), rendered at
    300 dpi (see the comment above the data in gec_7/figures.py)."""

    def test_low_n_low_stress(self):
        """N60 = 5 on the 0.5 curve: between the crossings at phi 29 (N60
        4.23) and phi 31 (N60 5.05): 30.9 degrees."""
        phi = figure_4_3_friction_angle_spt(5, 0.5)
        assert phi == pytest.approx(30.9, abs=0.05)

    def test_high_n_low_stress(self):
        """The 0.5 curve leaves the top of the chart (phi 50) at N60 38.25;
        N60 = 50 is off it (it returned 44)."""
        with pytest.raises(ValueError, match="38.25"):
            figure_4_3_friction_angle_spt(50, 0.5)

    def test_medium_n_medium_stress(self):
        """N60 = 31 on the 1.0 curve: read 44.99, 45.0 degrees (at N60 = 30
        it returned 38.0)."""
        phi = figure_4_3_friction_angle_spt(31, 1.0)
        assert phi == pytest.approx(45.0, abs=0.05)

    def test_review_point(self):
        """The review's point, N60 = 22 at sigma'vo/Pa = 2.0: the 2.0 curve
        reads 36.99 there, 37.0 degrees (it returned 33.6)."""
        assert figure_4_3_friction_angle_spt(22, 2.0) == pytest.approx(37.0, abs=0.05)

    def test_points_on_each_curve(self):
        """One read point on each of the six curves, top to bottom."""
        assert figure_4_3_friction_angle_spt(16, 0.5) == pytest.approx(41.6, abs=0.05)
        assert figure_4_3_friction_angle_spt(40, 1.0) == pytest.approx(47.5, abs=0.05)
        assert figure_4_3_friction_angle_spt(48, 1.5) == pytest.approx(46.5, abs=0.05)
        assert figure_4_3_friction_angle_spt(12, 2.0) == pytest.approx(31.2, abs=0.05)
        assert figure_4_3_friction_angle_spt(55, 2.5) == pytest.approx(44.2, abs=0.05)
        assert figure_4_3_friction_angle_spt(40, 3.0) == pytest.approx(39.4, abs=0.05)

    def test_low_n_high_stress_below_chart(self):
        """At sigma'vo/Pa = 2.0 the curve meets phi 25 at N60 6.1; N60 = 5 is
        below the chart (it returned 29.6, above the print)."""
        with pytest.raises(ValueError):
            figure_4_3_friction_angle_spt(5, 2.0)

    def test_curve_ends(self):
        """Each curve ends where it is drawn: 1.0 at N60 44.75, 2.5 at 57.5."""
        assert figure_4_3_friction_angle_spt(44.75, 1.0) == pytest.approx(48.6, abs=0.05)
        with pytest.raises(ValueError):
            figure_4_3_friction_angle_spt(45, 1.0)
        assert figure_4_3_friction_angle_spt(57.5, 2.5) == pytest.approx(44.6, abs=0.05)
        with pytest.raises(ValueError):
            figure_4_3_friction_angle_spt(58, 2.5)

    def test_high_stress_lowers_phi(self):
        """Higher confining stress should give lower phi for same N."""
        phi_low = figure_4_3_friction_angle_spt(30, 0.5)
        phi_high = figure_4_3_friction_angle_spt(30, 3.0)
        assert phi_low > phi_high

    def test_zero_n(self):
        """N60 = 0 is below every curve (the chart starts at phi 25); it
        returned 28."""
        with pytest.raises(ValueError):
            figure_4_3_friction_angle_spt(0, 1.0)

    def test_interpolation(self):
        """N60 = 25 on the 1.5 curve: 40.3; between curves the angle is
        linear in sigma'vo/Pa at the same N60: at 1.25 and N60 = 21, halfway
        between 41.21 (1.0) and 38.73 (1.5)."""
        assert figure_4_3_friction_angle_spt(25, 1.5) == pytest.approx(40.3, abs=0.05)
        assert figure_4_3_friction_angle_spt(21, 1.25) == pytest.approx(40.0, abs=0.05)

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
    """Tests for figure_5_11_basal_heave_nc(). Expected values are the
    points read off GEC-7 Figure 5.11, p. 124 (PDF page 164), rendered at
    300 dpi (see the comment above the data in gec_7/figures.py)."""

    def test_zero_h_be(self):
        """At H/Be = 0 the three curves start apart: 5.20 (Be/Le 0), 5.69
        (0.5), 6.19 (1); it returned 5.14 for all three."""
        assert figure_5_11_basal_heave_nc(0, 0.0) == pytest.approx(5.20)
        assert figure_5_11_basal_heave_nc(0, 0.5) == pytest.approx(5.69)
        assert figure_5_11_basal_heave_nc(0, 1.0) == pytest.approx(6.19)

    def test_points_read(self):
        """Read at H/Be 0.25, 1.6 and 3.6 (Be/Le 0, 0.5, 1)."""
        assert [figure_5_11_basal_heave_nc(0.25, r) for r in (0.0, 0.5, 1.0)] == \
            pytest.approx([5.50, 6.05, 6.58])
        assert [figure_5_11_basal_heave_nc(1.6, r) for r in (0.0, 0.5, 1.0)] == \
            pytest.approx([6.76, 7.42, 8.08])
        assert [figure_5_11_basal_heave_nc(3.6, r) for r in (0.0, 0.5, 1.0)] == \
            pytest.approx([7.43, 8.12, 8.90])

    def test_long_excavation_high_h_be(self):
        """Long excavation (Be/Le = 0) at H/Be = 5: 7.45 (it returned 6.2,
        17 % low)."""
        nc = figure_5_11_basal_heave_nc(5.0, 0.0)
        assert nc == pytest.approx(7.45)

    def test_square_excavation_high_h_be(self):
        """Square excavation (Be/Le = 1) at H/Be = 5: 8.96."""
        nc = figure_5_11_basal_heave_nc(5.0, 1.0)
        assert nc == pytest.approx(8.96)

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
