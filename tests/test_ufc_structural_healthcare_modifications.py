"""Tests for geotech_references.ufc_structural.healthcare_modifications
(Chapters 6/7 critical healthcare facility modifications)."""

import pytest

from geotech_references.ufc_structural.healthcare_modifications import (
    table_6_1_masonry_wall_thickness,
    healthcare_retaining_wall_lateral_load_minimum,
    healthcare_structural_configuration_limits,
    healthcare_elevator_seismic_force_asd,
)


class TestTable61MasonryWallThickness:
    """Anchors: printed Table 6-1 (p. 93)."""

    def test_stone_masonry(self):
        r = table_6_1_masonry_wall_thickness("stone_masonry_bearing_or_shear")
        assert r["max_height_or_length_to_thickness_ratio"] == 14
        assert r["nominal_min_thickness_in"] == 16

    def test_reinforced_hollow_unit_masonry(self):
        r = table_6_1_masonry_wall_thickness("reinforced_hollow_unit_masonry_bearing_or_shear")
        assert r["max_height_or_length_to_thickness_ratio"] == 25
        assert r["nominal_min_thickness_in"] == 6

    def test_interior_reinforced_nonbearing_partitions_thinnest(self):
        r = table_6_1_masonry_wall_thickness("interior_reinforced_nonbearing_partitions")
        assert r["nominal_min_thickness_in"] == 4
        assert r["max_height_or_length_to_thickness_ratio"] == 36

    def test_nonbearing_walls_have_higher_ratio_than_bearing(self):
        # self-consistency: nonbearing walls are permitted a more slender
        # ratio than bearing/shear walls of the same reinforcement class
        bearing = table_6_1_masonry_wall_thickness("reinforced_hollow_unit_masonry_bearing_or_shear")
        nonbearing = table_6_1_masonry_wall_thickness("exterior_reinforced_nonbearing_walls")
        assert nonbearing["max_height_or_length_to_thickness_ratio"] > bearing["max_height_or_length_to_thickness_ratio"]

    def test_unknown_wall_type_raises(self):
        with pytest.raises(ValueError):
            table_6_1_masonry_wall_thickness("adobe_wall")


class TestRetainingWallLateralLoad:
    """Anchors: paragraph 1807.2.2 (printed p. 88)."""

    def test_minimum_fraction_and_seismic_threshold(self):
        r = healthcare_retaining_wall_lateral_load_minimum()
        assert r["minimum_fraction_of_section_1610_load"] == 0.80
        assert r["seismic_increment_backfill_height_threshold_ft"] == 6


class TestStructuralConfigurationLimits:
    """Anchors: paragraph 12.1.7 (printed pp. 95-96)."""

    def test_seismic_joint_factor(self):
        assert healthcare_structural_configuration_limits()["seismic_joint_separation_factor"] == 1.25

    def test_adjacent_structure_separation(self):
        r = healthcare_structural_configuration_limits()
        assert r["adjacent_structure_separation_in_per_story"] == 2


class TestElevatorSeismicForce:
    """Anchors: paragraph 13.6.11.1.1 (printed pp. 100-101)."""

    def test_minimum_asd_force_and_load_fraction(self):
        r = healthcare_elevator_seismic_force_asd()
        assert r["minimum_asd_seismic_force_g"] == 0.5
        assert r["counterweight_load_fraction"] == 0.40

    def test_guide_member_fractions_sum_to_one(self):
        r = healthcare_elevator_seismic_force_asd()
        total = r["top_guide_member_fraction"] + r["bottom_guide_member_fraction"]
        assert total == pytest.approx(1.0)
        assert r["bottom_guide_member_fraction"] == pytest.approx(2.0 / 3.0)
