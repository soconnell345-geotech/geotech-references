"""Tests for GEC-6 figure lookup functions.

The expected values are points read off the rendered pages of
FHWA-SA-02-054 (GEC 6.pdf): the curve's centre line at 300 dpi, calibrated
on the chart's own grid lines.
"""

import pytest

from geotech_references.gec_6.figures import (
    figure_4_1_relative_density_spt,
    figure_4_2_friction_angle_from_density,
    figure_5_19_hough_bearing_capacity_index,
)

KSF = 47.88       # kPa per k/ft2, printed under Figure 4-1
PCF = 0.157087    # kN/m3 per pcf


# ============================================================================
# Figure 4-1: Relative Density from SPT
# ============================================================================

class TestFigure41:
    """Tests for figure_4_1_relative_density_spt()."""

    # GEC 6.pdf page 40 (printed p. 34), Figure 4-1: N where each relative
    # density curve crosses a stress level. (k/ft2, {Dr %: N})
    PRINTED = [
        (0.5, {15: 1.7, 40: 3.4, 50: 5.7, 60: 8.1, 70: 11.7, 80: 15.2,
               85: 16.9, 90: 19.3, 100: 24.7}),
        (1.0, {15: 2.5, 40: 4.8, 50: 7.4, 60: 10.1, 70: 14.5, 80: 18.7,
               85: 20.9, 90: 24.0, 100: 30.3}),
        (2.0, {15: 3.5, 40: 6.8, 50: 10.1, 60: 13.9, 70: 19.3, 80: 25.3,
               85: 28.9, 90: 33.3, 100: 41.5}),
        (4.0, {15: 4.5, 40: 9.2, 50: 14.2, 60: 20.1, 70: 28.2, 80: 38.2,
               85: 43.9, 90: 50.7, 100: 65.6}),
        (6.0, {15: 5.0, 40: 10.8, 50: 17.0, 60: 25.6, 70: 36.2, 80: 51.6,
               85: 58.9, 90: 68.0}),
    ]

    @pytest.mark.parametrize("ksf, curves", PRINTED)
    def test_points_on_the_printed_curves(self, ksf, curves):
        for dr, n in curves.items():
            got = figure_4_1_relative_density_spt(n, ksf * KSF)
            assert got == pytest.approx(dr, abs=0.01), (ksf, dr, n)

    def test_dense_curves_as_printed(self):
        """The 80 to 100 % curves were coded far to the right of the print:
        N = 30 at 1 k/ft2 is on the printed 100 % curve (the lookup said
        87.5 %), and N = 47 at 2 k/ft2, coded as 90 %, is off the chart."""
        assert figure_4_1_relative_density_spt(30, 1.0 * KSF) == pytest.approx(
            99.5, abs=0.6)
        assert figure_4_1_relative_density_spt(33, 2.0 * KSF) == pytest.approx(
            89.7, abs=0.6)
        with pytest.raises(ValueError, match="right of the highest curve"):
            figure_4_1_relative_density_spt(47, 2.0 * KSF)

    def test_gec6_example(self):
        """GEC-6 p. B-26 (PDF page 184) reads about 95 % for N = 24 at
        0.58 k/ft2; the lookup returned 90.2."""
        dr = figure_4_1_relative_density_spt(24, 0.58 * KSF)
        assert 94 <= dr <= 98

    def test_low_n_low_stress(self):
        """Low N at low stress = low Dr."""
        dr = figure_4_1_relative_density_spt(3, 48)
        assert 15 <= dr <= 40

    def test_high_n_low_stress(self):
        """N = 25 at 1 k/ft2 is between the 90 and 100 % curves."""
        dr = figure_4_1_relative_density_spt(25, 48)
        assert 90 <= dr <= 100

    def test_medium_n_medium_stress(self):
        """N = 20 at 2 k/ft2 is just right of the 70 % curve (19.3)."""
        dr = figure_4_1_relative_density_spt(20, 96)
        assert 70 <= dr <= 73

    def test_returns_float(self):
        dr = figure_4_1_relative_density_spt(10, 48)
        assert isinstance(dr, float)

    def test_left_of_the_15_percent_curve_is_refused(self):
        """N = 0 returned 15.0 before: the chart has no curve below 15 %."""
        with pytest.raises(ValueError, match="left of the lowest curve"):
            figure_4_1_relative_density_spt(0, 48)
        with pytest.raises(ValueError, match="Dr = 15 %"):
            figure_4_1_relative_density_spt(2, 48)

    def test_right_of_the_100_percent_curve_is_refused(self):
        """N = 50 at 1 k/ft2 returned 100.0 before."""
        with pytest.raises(ValueError, match="Dr = 100 %"):
            figure_4_1_relative_density_spt(50, 48)

    def test_100_percent_curve_leaves_the_chart(self):
        """Above 5.15 k/ft2 the 100 % curve is beyond N = 80."""
        assert figure_4_1_relative_density_spt(63.5, 5.5 * KSF) == pytest.approx(
            90, abs=0.01)
        with pytest.raises(ValueError, match="edge of the chart"):
            figure_4_1_relative_density_spt(70, 5.5 * KSF)

    def test_whole_plotted_stress_range(self):
        """The chart is plotted to 6 k/ft2 (287 kPa); 4 k/ft2 was the limit."""
        # 250 kPa = 5.22 k/ft2: the 50 % curve is at N = 15.9 and the 60 %
        # curve at 23.6 (between the 5.0 and 5.5 k/ft2 readings)
        assert figure_4_1_relative_density_spt(20, 250) == pytest.approx(
            55.3, abs=0.3)
        assert figure_4_1_relative_density_spt(5, 12) == pytest.approx(
            51.4, abs=1.5)

    def test_stress_out_of_range_low(self):
        with pytest.raises(ValueError, match="12 to 287 kPa"):
            figure_4_1_relative_density_spt(10, 10)

    def test_stress_out_of_range_high(self):
        with pytest.raises(ValueError, match="12 to 287 kPa"):
            figure_4_1_relative_density_spt(10, 300)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            figure_4_1_relative_density_spt(-5, 48)


# ============================================================================
# Figure 4-2: Friction Angle from Density
# ============================================================================

class TestFigure42:
    """Tests for figure_4_2_friction_angle_from_density()."""

    # GEC 6.pdf page 41 (printed p. 35), Figure 4-2: where each dashed
    # relative density line meets the first (ML), fourth (SW) and sixth (GW)
    # solid line. (Dr %, pcf, phi' deg)
    PRINTED = [
        (0, 78.9, 26.1), (0, 102.1, 27.2), (0, 117.8, 27.9),
        (25, 83.7, 28.7), (25, 107.0, 30.3), (25, 123.3, 31.4),
        (50, 88.2, 31.0), (50, 112.9, 33.8), (50, 130.5, 35.8),
        (75, 92.8, 33.4), (75, 118.6, 37.2), (75, 138.0, 40.1),
        (100, 97.9, 36.0), (100, 124.4, 40.8), (100, 147.0, 44.9),
    ]

    @pytest.mark.parametrize("dr, pcf, phi", PRINTED)
    def test_points_on_the_printed_mesh(self, dr, pcf, phi):
        got = figure_4_2_friction_angle_from_density(pcf * PCF, dr)
        assert got == pytest.approx(phi, abs=0.02)

    def test_zero_relative_density_line_as_printed(self):
        """The printed 0 % line runs from 26.1 deg at 79 pcf to 27.9 deg at
        118 pcf; the lookup had it 2.4 deg higher at 110 pcf (30.0)."""
        phi = figure_4_2_friction_angle_from_density(17.3, 0)
        assert phi == pytest.approx(27.5, abs=0.15)
        phi = figure_4_2_friction_angle_from_density(110 * PCF, 25)
        assert phi == pytest.approx(30.5, abs=0.15)

    def test_low_density_dr0(self):
        """Low density, Dr=0 gives low phi."""
        phi = figure_4_2_friction_angle_from_density(14.1, 0)
        assert 26 <= phi <= 27

    def test_high_density_dr100(self):
        """High density, Dr=100 gives high phi."""
        phi = figure_4_2_friction_angle_from_density(22.0, 100)
        assert 43 <= phi <= 44.5

    def test_medium_density_dr50(self):
        """Medium density, Dr=50."""
        phi = figure_4_2_friction_angle_from_density(18.9, 50)
        assert 34 <= phi <= 35.5

    def test_between_the_printed_lines(self):
        """Half way from the 25 % to the 50 % line along the SW line:
        (107.0 + 112.9) / 2 pcf, (30.3 + 33.8) / 2 deg."""
        phi = figure_4_2_friction_angle_from_density(109.95 * PCF, 37.5)
        assert phi == pytest.approx(32.05, abs=0.03)

    def test_off_the_mesh_is_refused(self):
        """22.0 kN/m3 at Dr = 0 and 12.6 kN/m3 at Dr = 100 are outside the
        printed mesh; each returned 33 deg before."""
        with pytest.raises(ValueError, match="12.4 kN/m\\^3 .* to 18.5"):
            figure_4_2_friction_angle_from_density(22.0, 0)
        with pytest.raises(ValueError, match="15.4 kN/m\\^3 .* to 23.1"):
            figure_4_2_friction_angle_from_density(12.6, 100)

    def test_gamma_out_of_range_low(self):
        with pytest.raises(ValueError):
            figure_4_2_friction_angle_from_density(10.0, 50)

    def test_gamma_out_of_range_high(self):
        with pytest.raises(ValueError):
            figure_4_2_friction_angle_from_density(25.0, 50)

    def test_dr_out_of_range(self):
        with pytest.raises(ValueError):
            figure_4_2_friction_angle_from_density(18.9, -10)
        with pytest.raises(ValueError):
            figure_4_2_friction_angle_from_density(18.9, 101)

    def test_docstring_names_the_chart(self):
        first = figure_4_2_friction_angle_from_density.__doc__.split("\n\n")[0]
        assert "Figure 4-2" in first and "p. 35" in first
        assert "refused" in first


# ============================================================================
# Figure 5-19: Hough Bearing Capacity Index
# ============================================================================

class TestFigure519:
    """Tests for figure_5_19_hough_bearing_capacity_index()."""

    # GEC 6.pdf page 97 (printed p. 91), Figure 5-19: C' read off each
    # curve. (curve, {N': C'})
    PRINTED = [
        ("clean_uniform_medium_sand", {4: 48, 10: 60, 20: 88, 30: 127,
                                       40: 176, 50: 245, 55: 290}),
        ("well_graded_silty_sand_and_gravel", {4: 42, 10: 54, 20: 77,
                                               30: 103, 40: 132, 50: 169,
                                               60: 212, 70: 266, 75: 299}),
        ("clean_well_graded_fine_to_coarse_sand", {4: 38, 10: 49, 20: 69,
                                                   30: 90, 40: 114, 50: 141,
                                                   60: 171, 70: 207, 80: 250,
                                                   85: 275}),
        ("well_graded_fine_to_medium_silty_sand", {4: 34, 10: 42, 20: 59,
                                                   30: 77, 40: 97, 50: 118,
                                                   60: 141, 70: 165, 80: 191,
                                                   90: 220, 100: 253}),
        ("sandy_clay", {4: 29, 10: 36, 20: 51, 30: 65, 40: 80, 50: 95,
                        60: 111, 70: 128, 80: 148, 90: 168, 100: 191}),
        ("inorganic_silt", {4: 22, 10: 30, 20: 42, 30: 55, 40: 69, 50: 84,
                            60: 99, 70: 114, 80: 129, 90: 144, 100: 161}),
    ]

    @pytest.mark.parametrize("curve, points", PRINTED)
    def test_points_on_the_printed_curves(self, curve, points):
        for n, c in points.items():
            got = figure_5_19_hough_bearing_capacity_index(n, curve)
            assert got == pytest.approx(c, abs=0.01), (curve, n)

    def test_gec6_example(self):
        """GEC-6 p. B-28 (PDF page 186): "Entering Figure 5-19 with N' = 32
        for well-graded silty sand and gravel, a C' of 110 is read". The
        lookup returned 96.6 under the nearest of its names."""
        c = figure_5_19_hough_bearing_capacity_index(
            32, "well-graded silty sand and gravel")
        assert c == pytest.approx(110, abs=2.5)

    def test_curves_do_not_start_at_zero(self):
        """N' = 0 returned C' = 0 (no settlement resistance at all, and a
        division by zero in Eq. 5-24); the printed curves start at N' = 4."""
        with pytest.raises(ValueError, match="from N' = 4"):
            figure_5_19_hough_bearing_capacity_index(0, "sandy_clay")
        with pytest.raises(ValueError, match="from N' = 4"):
            figure_5_19_hough_bearing_capacity_index(3.9, "inorganic_silt")

    def test_inorganic_silt_n50(self):
        """Inorganic silt at N'=50: 84 (the lookup held 78)."""
        c_prime = figure_5_19_hough_bearing_capacity_index(50, "inorganic_silt")
        assert c_prime == pytest.approx(84, abs=0.01)

    def test_well_graded_sand_n30(self):
        """Well graded silty sand and gravel at N'=30: 103 (the lookup held
        92 under 'well_graded_sand_gravel')."""
        c_prime = figure_5_19_hough_bearing_capacity_index(30, "well_graded_sand_gravel")
        assert c_prime == pytest.approx(103, abs=0.01)

    def test_coarse_sand_alone_is_refused(self):
        """'coarse_sand' is no curve of the chart (the nearest is 'Clean
        well graded fine to coarse SAND', 141 at N' = 50); the lookup
        answered it with 182."""
        with pytest.raises(ValueError, match="does not name one curve"):
            figure_5_19_hough_bearing_capacity_index(50, "coarse_sand")
        with pytest.raises(ValueError, match="does not name one curve"):
            figure_5_19_hough_bearing_capacity_index(50, "clean_fine_to_medium_sand")
        assert figure_5_19_hough_bearing_capacity_index(
            50, "clean well graded fine to coarse sand") == pytest.approx(141)

    def test_clean_uniform_medium_sand(self):
        """Clean uniform medium sand at N'=40: 176, the highest curve (the
        lookup held 138, below its 'coarse_sand')."""
        c_prime = figure_5_19_hough_bearing_capacity_index(40, "clean_uniform_medium_sand")
        assert c_prime == pytest.approx(176, abs=0.01)

    def test_interpolation(self):
        """N'=25 on the sandy clay curve."""
        c_prime = figure_5_19_hough_bearing_capacity_index(25, "sandy_clay")
        assert c_prime == pytest.approx(58, abs=0.01)
        c_prime = figure_5_19_hough_bearing_capacity_index(22, "sandy_clay")
        assert 51 < c_prime < 58

    def test_curve_that_leaves_the_chart(self):
        """The clean uniform medium sand curve reaches C' = 300 at N' = 56;
        the lookup returned 183 at N' = 60."""
        with pytest.raises(ValueError, match="N' = 56"):
            figure_5_19_hough_bearing_capacity_index(60, "clean_uniform_medium_sand")
        with pytest.raises(ValueError, match="N' = 75.2"):
            figure_5_19_hough_bearing_capacity_index(80, "well_graded_silty_sand_and_gravel")
        with pytest.raises(ValueError, match="N' = 89.4"):
            figure_5_19_hough_bearing_capacity_index(95, "clean_well_graded_fine_to_coarse_sand")

    def test_n_out_of_range(self):
        with pytest.raises(ValueError):
            figure_5_19_hough_bearing_capacity_index(-5, "sandy_clay")
        with pytest.raises(ValueError):
            figure_5_19_hough_bearing_capacity_index(110, "sandy_clay")

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError):
            figure_5_19_hough_bearing_capacity_index(20, "organic_peat")

    @pytest.mark.parametrize("ambiguous", ["sand", "silty sand", "gravel",
                                           "clay", "well graded sand",
                                           "medium sand"])
    def test_a_name_that_fits_no_single_curve_is_refused(self, ambiguous):
        """'sand' returned the Sandy CLAY curve and 'gravel' a sand curve:
        the first key that held the word."""
        with pytest.raises(ValueError, match="does not name one curve"):
            figure_5_19_hough_bearing_capacity_index(30, ambiguous)

    def test_partial_match(self):
        """'silt' is the chart's Inorganic SILT curve (a listed name)."""
        c_prime = figure_5_19_hough_bearing_capacity_index(20, "silt")
        assert c_prime == pytest.approx(42, abs=0.01)
