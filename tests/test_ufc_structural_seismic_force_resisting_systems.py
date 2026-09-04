"""Tests for geotech_references.ufc_structural.seismic_force_resisting_systems
(Table 3-1 REPLACEMENT for ASCE 7-22 Table 12.2-1, Table 7-1 healthcare
subset, Table B-1 RC IV alternate-design permitted systems)."""

import pytest

from geotech_references.ufc_structural.seismic_force_resisting_systems import (
    table_3_1_seismic_system,
    table_3_1_footnote,
    list_table_3_1_systems,
    table_7_1_healthcare_seismic_system,
    list_table_7_1_systems,
    table_b1_rc4_permitted_system,
    table_b1_footnote,
    list_table_b1_systems,
    TABLE_3_1,
    TABLE_7_1,
    TABLE_B_1,
)


class TestTable31RowCounts:
    """Self-consistency: total system counts per category, tallied directly
    from the printed table (pp. 49-57) during digitization."""

    @pytest.mark.parametrize("category,expected_count", [
        ("A", 21), ("B", 28), ("C", 12), ("D", 15), ("E", 8), ("F", 1), ("G", 6), ("H", 1),
    ])
    def test_category_row_count(self, category, expected_count):
        assert len(TABLE_3_1[category]) == expected_count

    def test_total_row_count(self):
        assert sum(len(v) for v in TABLE_3_1.values()) == 92


class TestTable31SpotValues:
    """Anchors: specific printed Table 3-1 rows (pp. 49-57)."""

    def test_bearing_wall_special_rc_shear_walls(self):
        r = table_3_1_seismic_system("A", "special_reinforced_concrete_shear_walls")
        assert r["R"] == 5
        assert r["omega0"] == 2.5
        assert r["cd"] == 5
        assert r["height_limits"] == {"B": "NL", "C": "NL", "D": 160, "E": 160, "F": 100}

    def test_reinforced_concrete_ductile_coupled_walls_r8(self):
        # highest-R bearing-wall system; R=Cd=8 is a distinctive, easily-miskeyed pair
        r = table_3_1_seismic_system("A", "reinforced_concrete_ductile_coupled_walls")
        assert r["R"] == 8 and r["cd"] == 8
        assert "q" in r["footnotes"]

    def test_building_frame_steel_special_plate_shear_walls(self):
        r = table_3_1_seismic_system("B", "steel_special_plate_shear_walls")
        assert r["R"] == 7
        assert r["omega0"] == 2
        assert r["cd"] == 6

    def test_moment_frame_steel_special_moment_frames_unlimited_height(self):
        r = table_3_1_seismic_system("C", "steel_special_moment_frames")
        assert r["R"] == 8
        assert r["height_limits"]["D"] == "NL"
        assert r["height_limits"]["F"] == "NL"

    def test_dual_special_reinforced_concrete_ductile_coupled_walls_unlimited(self):
        r = table_3_1_seismic_system("D", "reinforced_concrete_ductile_coupled_walls")
        assert r["height_limits"] == {"B": "NL", "C": "NL", "D": "NL", "E": "NL", "F": "NL"}

    def test_shear_wall_frame_interactive_single_system(self):
        r = table_3_1_seismic_system("F", "ordinary_rc_moment_frames_and_ordinary_rc_shear_walls")
        assert r["R"] == 4.5
        assert r["height_limits"]["B"] == "NL"
        assert r["height_limits"]["C"] == "NP"

    def test_cantilevered_column_special_steel_35ft_all_sdc(self):
        r = table_3_1_seismic_system("G", "steel_special_cantilever_column_systems")
        assert r["height_limits"] == {"B": 35, "C": 35, "D": 35, "E": 35, "F": 35}

    def test_steel_not_specifically_detailed(self):
        r = table_3_1_seismic_system("H", "steel_not_specifically_detailed_excl_cantilever_columns")
        assert r["R"] == 3 and r["omega0"] == 3 and r["cd"] == 3

    def test_not_permitted_by_ufc_system(self):
        r = table_3_1_seismic_system("A", "detailed_plain_masonry_shear_walls")
        assert r["permitted"] is False
        assert "SDC B" in r["note"]

    def test_unknown_category_raises(self):
        with pytest.raises(ValueError):
            table_3_1_seismic_system("Z", "anything")

    def test_unknown_system_raises(self):
        with pytest.raises(ValueError):
            table_3_1_seismic_system("A", "nonexistent_system")


class TestTable31Footnotes:
    def test_footnote_d_defines_nl_np(self):
        r = table_3_1_footnote("d")
        assert "not limited" in r["text"].lower()
        assert "not permitted" in r["text"].lower()

    def test_unknown_footnote_raises(self):
        with pytest.raises(ValueError):
            table_3_1_footnote("zz")


class TestListTable31Systems:
    def test_list_by_category(self):
        systems = list_table_3_1_systems("A")
        assert "special_reinforced_concrete_shear_walls" in systems
        assert systems == sorted(systems)

    def test_list_all_categories(self):
        all_systems = list_table_3_1_systems()
        assert set(all_systems) == set(TABLE_3_1)


class TestTable71HealthcareSubset:
    """Anchors: printed Table 7-1 (pp. 98-99); self-consistency: Table 7-1
    is a curated subset of Table 3-1's system names."""

    def test_row_counts(self):
        assert len(TABLE_7_1["B"]) == 8
        assert len(TABLE_7_1["C"]) == 2
        assert len(TABLE_7_1["D"]) == 5

    def test_steel_eccentrically_braced_frames_matches_table_3_1(self):
        # this system's R/Omega0/Cd happen to be identical between Table 3-1
        # and Table 7-1 category B -- a genuine cross-table consistency check
        t31 = table_3_1_seismic_system("B", "steel_eccentrically_braced_frames")
        t71 = table_7_1_healthcare_seismic_system("B", "steel_eccentrically_braced_frames")
        assert t71["R"] == t31["R"] == 8
        assert t71["cd"] == t31["cd"] == 4

    def test_healthcare_wood_light_frame_limited_two_stories(self):
        r = table_7_1_healthcare_seismic_system("B", "light_frame_wood_walls_wood_structural_panels")
        assert "v" in r["footnotes"]

    def test_dual_special_rc_shear_walls_healthcare(self):
        # printed Table 7-1 category D value (p. 99); happens to equal the
        # same-named Table 3-1 category D row for this particular system
        r = table_7_1_healthcare_seismic_system("D", "special_reinforced_concrete_shear_walls")
        assert r["R"] == 7 and r["cd"] == 5.5

    def test_table_7_1_is_subset_of_table_3_1_system_names(self):
        for category, systems in TABLE_7_1.items():
            for system_name in systems:
                # every Table 7-1 system name must also exist in Table 3-1's
                # same category (Table 7-1 only curates a subset, never adds
                # a system Table 3-1 doesn't have)
                assert system_name in TABLE_3_1[category], (category, system_name)

    def test_list_table_7_1_systems(self):
        assert list_table_7_1_systems("C") == sorted(TABLE_7_1["C"])

    def test_unknown_category_raises(self):
        with pytest.raises(ValueError):
            table_7_1_healthcare_seismic_system("A", "anything")


class TestTableB1RC4AlternateDesign:
    """Anchors: printed Table B-1 (pp. 124-126); no R/Cd/Omega0 fields
    (not required for the Appendix B nonlinear procedure)."""

    def test_row_counts(self):
        assert len(TABLE_B_1["Bearing Wall Systems"]) == 8
        assert len(TABLE_B_1["Building Frame Systems"]) == 15
        assert len(TABLE_B_1["Moment-Resisting Frame Systems"]) == 9
        assert len(TABLE_B_1["Dual Systems with Special Moment Frames (>=25%)"]) == 12
        assert len(TABLE_B_1["Dual Systems with Intermediate Moment Frames (>=25%)"]) == 6
        assert len(TABLE_B_1["Cantilevered Column Systems"]) == 2

    def test_special_steel_moment_frames_unlimited(self):
        r = table_b1_rc4_permitted_system("Moment-Resisting Frame Systems", "special_steel_moment_frames")
        assert r["height_limits"] == {"B": "NL", "C": "NL", "D": "NL", "E": "NL", "F": "NL"}
        assert "R" not in r  # R/Cd/Omega0 not applicable to this table

    def test_cantilevered_column_systems_35ft(self):
        r = table_b1_rc4_permitted_system("Cantilevered Column Systems", "special_steel_cantilever_column_systems")
        assert r["height_limits"] == {"B": 35, "C": 35, "D": 35, "E": 35, "F": 35}

    def test_case_insensitive_category(self):
        r = table_b1_rc4_permitted_system("cantilevered column systems", "special_steel_cantilever_column_systems")
        assert r["category"] == "Cantilevered Column Systems"

    def test_footnote_1_design_review_panel(self):
        r = table_b1_footnote("1")
        assert "design review panel" in r["text"].lower()

    def test_unknown_category_raises(self):
        with pytest.raises(ValueError):
            table_b1_rc4_permitted_system("Nonexistent Category", "anything")

    def test_list_table_b1_systems(self):
        assert set(list_table_b1_systems()) == set(TABLE_B_1)
