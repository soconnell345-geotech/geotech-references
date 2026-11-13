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

    # GEC 6.pdf page 74 (printed p. 68), Table 5-7, every printed row:
    # (key, consistency in place, range MPa, recommended value MPa)
    @pytest.mark.parametrize("key, consistency, lo, hi, rec", [
        ("massive_crystalline_igneous_metamorphic", "Hard, sound rock", 5.8, 9.6, 7.7),
        ("foliated_metamorphic", "Medium-hard, sound rock", 2.9, 3.8, 3.4),
        ("sedimentary_hard_cemented", "Medium-hard, sound rock", 1.4, 2.4, 1.9),
        ("weathered_broken_bedrock", "Soft rock", 0.8, 1.2, 1.0),
        ("compaction_shale_argillaceous", "Soft rock", 0.8, 1.2, 1.0),
    ])
    def test_every_printed_row(self, key, consistency, lo, hi, rec):
        r = table_5_7_presumptive_bearing_rock(key)
        assert r["consistency_printed"] == consistency
        assert (r["range_min_mpa"], r["range_max_mpa"], r["recommended_mpa"]) == (lo, hi, rec)
        assert "p. 68" in r["reference"]

    @pytest.mark.parametrize("rock, rec", [
        ("granite", 7.7), ("gneiss", 7.7), ("schist", 3.4), ("slate", 3.4),
        ("sandstone", 1.9), ("limestone", 1.9), ("hard cemented shale", 1.9),
        ("compaction shale", 1.0), ("broken bedrock", 1.0),
    ])
    def test_rocks_the_rows_name(self, rock, rec):
        assert table_5_7_presumptive_bearing_rock(rock)["recommended_mpa"] == rec

    @pytest.mark.parametrize("ambiguous", ["rock", "hard", "medium hard",
                                           "metamorphic", "soft rock",
                                           "shale", "sound rock"])
    def test_a_name_that_fits_several_rows_is_refused(self, ambiguous):
        """'rock' and 'hard' returned the first row, 7.7 MPa; 'medium hard'
        the foliated row's 3.4 where the sedimentary row (1.9) has the same
        consistency; 'shale' is in three rows (1.9, 1, 1)."""
        with pytest.raises(ValueError, match="does not name one row"):
            table_5_7_presumptive_bearing_rock(ambiguous)

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

    # GEC 6.pdf page 76 (printed p. 70), Table 5-9, every printed row.
    @pytest.mark.parametrize("rqd, quality, mpa", [
        (100, "excellent", 29), (90, "good", 19), (75, "fair", 12),
        (50, "poor", 6), (25, "very_poor", 3), (0, "soil_like", 1),
    ])
    def test_every_printed_row(self, rqd, quality, mpa):
        r = table_5_9_rqd_bearing_capacity(rqd)
        assert r["rock_mass_quality"] == quality
        assert r["allowable_pressure_mpa"] == mpa
        assert r["interpolated"] is False
        assert r["printed_rows"] == [(rqd, quality, mpa)]

    def test_between_rows_the_quality_is_not_the_lower_rows(self):
        """RQD 80 returned 'fair' and RQD 95 'good', the row below; the
        table prints a quality only at its six RQD values."""
        r = table_5_9_rqd_bearing_capacity(80)
        assert r["rock_mass_quality"] == "between fair (RQD 75) and good (RQD 90)"
        assert r["interpolated"] is True
        assert r["printed_rows"] == [(75, "fair", 12), (90, "good", 19)]
        assert r["allowable_pressure_mpa"] == pytest.approx(14.3, abs=0.05)
        r = table_5_9_rqd_bearing_capacity(95)
        assert r["rock_mass_quality"] == "between good (RQD 90) and excellent (RQD 100)"
        assert r["allowable_pressure_mpa"] == 24.0
        r = table_5_9_rqd_bearing_capacity(10)
        assert r["rock_mass_quality"] == "between soil like (RQD 0) and very poor (RQD 25)"

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

    # GEC 6.pdf page 103 (printed p. 97), Table 5-12, rectangle rows:
    # (length/width, center, corner, middle of short side, middle of long
    # side, average)
    @pytest.mark.parametrize("lw, center, corner, short, long_, avg", [
        (1.5, 1.36, 0.67, 0.89, 0.97, 1.15),
        (2, 1.52, 0.76, 0.98, 1.12, 1.30),
        (3, 1.78, 0.88, 1.11, 1.35, 1.52),
        (5, 2.10, 1.05, 1.27, 1.68, 1.83),
        (10, 2.53, 1.26, 1.49, 2.12, 2.25),
        (100, 4.00, 2.00, 2.20, 3.60, 3.70),
        (1000, 5.47, 2.75, 2.94, 5.03, 5.15),
        (10000, 6.90, 3.50, 3.70, 6.50, 6.60),
    ])
    def test_rectangle_rows_as_printed(self, lw, center, corner, short, long_, avg):
        f = table_5_12_shape_rigidity_factor
        assert f("rectangle", "center", lw) == pytest.approx(center)
        assert f("rectangle", "corner", lw) == pytest.approx(corner)
        assert f("rectangle", "mid_short", lw) == pytest.approx(short)
        assert f("rectangle", "mid_long", lw) == pytest.approx(long_)
        assert f("rectangle", "average", lw) == pytest.approx(avg)

    def test_docstring_says_the_interpolation_is_not_printed(self):
        first = table_5_12_shape_rigidity_factor.__doc__.split("\n\n")[0]
        assert "which the table does not state" in first
        assert "p. 97" in first

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

    @pytest.mark.parametrize("partial", ["s", "a", "stone", "weathered granite",
                                         "granite gneiss"])
    def test_part_of_a_name_is_refused(self, partial):
        """'s' returned diabase and 'weathered granite' the intact granite
        row: the first name that held, or was held by, the text."""
        with pytest.raises(ValueError, match="is not a rock type"):
            table_5_13_poissons_ratio_rock(partial)

    # GEC 6.pdf page 103 (printed p. 97), Table 5-13: (rock, max, min, mean, std)
    @pytest.mark.parametrize("rock, mx, mn, mean, std", [
        ("gabbro", 0.20, 0.16, 0.18, 0.02), ("schist", 0.31, 0.02, 0.12, 0.08),
        ("shale", 0.18, 0.03, 0.09, 0.06), ("dolostone", 0.35, 0.14, 0.29, 0.08),
    ])
    def test_rows_as_printed(self, rock, mx, mn, mean, std):
        r = table_5_13_poissons_ratio_rock(rock)
        assert (r["max"], r["min"], r["mean"], r["std"]) == (mx, mn, mean, std)


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

    @pytest.mark.parametrize("partial", ["s", "a", "stone", "weathered granite"])
    def test_part_of_a_name_is_refused(self, partial):
        with pytest.raises(ValueError, match="is not a rock type"):
            table_5_14_youngs_modulus_rock(partial)

    # GEC 6.pdf page 104 (printed p. 98), Table 5-14, kPa x 10^6:
    # (rock, max, min, mean, std)
    @pytest.mark.parametrize("rock, mx, mn, mean, std", [
        ("diorite", 111.69, 17.10, 51.36, 42.68),
        ("slate", 26.13, 2.41, 9.58, 6.62),
        ("shale", 38.61, 0.01, 9.79, 10.00),
        ("dolostone", 78.60, 5.72, 29.10, 23.72),
    ])
    def test_rows_as_printed(self, rock, mx, mn, mean, std):
        r = table_5_14_youngs_modulus_rock(rock)
        assert (r["max_GPa"], r["min_GPa"], r["mean_GPa"], r["std_GPa"]) == (mx, mn, mean, std)


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
        """Clean gravel is 0.55 to 0.60; 'gravel' alone is also the 'silty
        or clayey gravel' of the next row (0.45 to 0.55) and is refused."""
        result = table_5_15_friction_factor("clean gravel")
        assert result["tan_delta_min"] == 0.55
        with pytest.raises(ValueError, match="does not name one row"):
            table_5_15_friction_factor("gravel")
        assert table_5_15_friction_factor("silty gravel")["tan_delta_min"] == 0.45

    # GEC 6.pdf page 105 (printed p. 99), Table 5-15, every printed row:
    # (key, tan delta low, high, delta low, high)
    @pytest.mark.parametrize("key, t0, t1, d0, d1", [
        ("clean_sound_rock", 0.70, 0.70, 35, 35),
        ("clean_gravel_coarse_sand", 0.55, 0.60, 29, 31),
        ("clean_fine_to_medium_sand_silty_medium_to_coarse_sand", 0.45, 0.55, 24, 29),
        ("clean_fine_sand_silty_or_clayey_fine_to_medium_sand", 0.35, 0.45, 19, 24),
        ("fine_sandy_silt_nonplastic_silt", 0.30, 0.35, 17, 19),
        ("very_stiff_hard_residual_preconsolidated_clay", 0.40, 0.50, 22, 26),
        ("medium_stiff_clay_silty_clay", 0.30, 0.35, 17, 19),
    ])
    def test_every_printed_row(self, key, t0, t1, d0, d1):
        r = table_5_15_friction_factor(key)
        assert (r["tan_delta_min"], r["tan_delta_max"]) == (t0, t1)
        assert (r["delta_min_deg"], r["delta_max_deg"]) == (d0, d1)
        assert "p. 99" in r["reference"]

    def test_sands_reach_their_own_row(self):
        """'fine sand' returned 0.45 to 0.55 (the fine to medium sand row);
        the print's 'Clean fine sand' row is 0.35 to 0.45."""
        r = table_5_15_friction_factor("fine sand")
        assert (r["tan_delta_min"], r["tan_delta_max"]) == (0.35, 0.45)
        r = table_5_15_friction_factor("clean fine to medium sand")
        assert (r["tan_delta_min"], r["tan_delta_max"]) == (0.45, 0.55)
        r = table_5_15_friction_factor("coarse sand")
        assert (r["tan_delta_min"], r["tan_delta_max"]) == (0.55, 0.60)

    @pytest.mark.parametrize("ambiguous", ["sand", "silty sand", "clay",
                                           "medium sand", "stiff", "clean"])
    def test_a_name_that_fits_several_rows_is_refused(self, ambiguous):
        """'sand' returned the clean gravel / coarse sand row, 0.55 to
        0.60, the highest of the four rows that name a sand."""
        with pytest.raises(ValueError, match="does not name one row"):
            table_5_15_friction_factor(ambiguous)

    def test_silt(self):
        result = table_5_15_friction_factor("silt")
        assert result["tan_delta_min"] == 0.30
        assert result["delta_min_deg"] == 17

    def test_clay(self):
        """Medium stiff and stiff clay 0.30 to 0.35; very stiff and hard
        clay 0.40 to 0.50."""
        result = table_5_15_friction_factor("stiff clay")
        assert result["tan_delta_min"] == 0.30
        result = table_5_15_friction_factor("very stiff clay")
        assert (result["tan_delta_min"], result["tan_delta_max"]) == (0.40, 0.50)

    def test_no_match_raises(self):
        with pytest.raises(ValueError):
            table_5_15_friction_factor("nonexistent_material")
