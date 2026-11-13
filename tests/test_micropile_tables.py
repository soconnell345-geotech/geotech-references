"""Tests for micropile table lookup functions."""

import pytest

from geotech_references.micropile.tables import (
    table_2_1_classification,
    table_4_2_rebar_properties,
    table_4_5_pipe_properties,
    table_5_3_alpha_bond,
    table_5_4_group_efficiency,
    table_5_5_corrosion_criteria,
    table_5_7_epsilon_50,
    table_5_8_epsilon_50_stiff,
    table_5_9_soil_modulus_k_sand,
    table_5_10_soil_modulus_k_clay,
    table_5_11_fixity,
    table_5_12_elastic_modulus,
    table_5_13_elastic_modulus_spt,
)


# ============================================================================
# Table 2-1: Classification
# ============================================================================

class TestTable21:
    """Tests for table_2_1_classification()."""

    def test_type_a1(self):
        r = table_2_1_classification("A", 1)
        assert r["type"] == "A"
        assert r["subtype"] == 1
        assert "gravity" in r["grouting"].lower()

    def test_type_b2(self):
        r = table_2_1_classification("B", 2)
        assert r["type"] == "B"
        assert r["subtype"] == 2
        assert "permanent" in r["drill_casing"].lower()

    def test_type_c1(self):
        r = table_2_1_classification("C", 1)
        assert r["type"] == "C"
        assert "pressure" in r["grout_description"].lower()

    def test_type_d3(self):
        r = table_2_1_classification("D", 3)
        assert r["type"] == "D"
        assert r["subtype"] == 3
        assert "packer" in r["grout_description"].lower()

    def test_case_insensitive(self):
        r = table_2_1_classification("a", 1)
        assert r["type"] == "A"

    def test_all_types_exist(self):
        for t in "ABCD":
            for s in [1, 2, 3]:
                r = table_2_1_classification(t, s)
                assert r["type"] == t
                assert r["subtype"] == s

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            table_2_1_classification("E", 1)

    def test_invalid_subtype(self):
        with pytest.raises(ValueError):
            table_2_1_classification("A", 4)


# ============================================================================
# Table 4-2: Rebar Properties
# ============================================================================

class TestTable42:
    """Tests for table_4_2_rebar_properties()."""

    # FHWA-NHI-05-039 Table 4-2, p. 4-27 (PDF page 83), every printed row:
    # (grade, bar, size mm, area mm2, yield strength kN)
    PRINTED = [
        (420, "#6", 19, 284, 117),
        (420, "#7", 22, 387, 160),
        (420, "#8", 25, 510, 211),
        (520, "#6", 19, 284, 147),
        (520, "#7", 22, 387, 200),
        (520, "#8", 25, 510, 264),
        (520, "#9", 29, 645, 334),
        (520, "#10", 32, 819, 424),
        (520, "#11", 36, 1006, 520),
        (520, "#14", 43, 1452, 751),
        (520, "#18", 57, 2581, 1335),
        (550, "2.5in", 63, 3168, 1747),
    ]

    @pytest.mark.parametrize("grade, bar, size, area, yield_kn", PRINTED)
    def test_every_printed_row(self, grade, bar, size, area, yield_kn):
        r = table_4_2_rebar_properties(bar, grade)
        assert r["bar_size"] == bar
        assert r["grade_mpa"] == grade
        assert r["diameter_mm"] == size
        assert r["area_mm2"] == area
        assert r["yield_kn"] == yield_kn
        assert "p. 4-27" in r["reference"]

    def test_grade_520_bar_14(self):
        r = table_4_2_rebar_properties("#14", 520)
        assert r["bar_size"] == "#14"
        assert r["grade_mpa"] == 520
        assert r["area_mm2"] == 1452
        assert r["diameter_mm"] == 43
        assert r["yield_kn"] == 751      # printed; area x fy would be 755

    def test_grade_420_bar_8(self):
        r = table_4_2_rebar_properties("#8", 420)
        assert r["area_mm2"] == 510
        assert r["yield_kn"] == 211      # printed; area x fy would be 214.2

    def test_grade_520_bar_18(self):
        r = table_4_2_rebar_properties("#18", 520)
        assert r["area_mm2"] == 2581
        assert r["yield_kn"] == 1335     # printed; area x fy would be 1342.1

    def test_tensile_strength_from_the_notes(self):
        """Notes (1)-(3): fu = 620, 690, 700 MPa for Grades 420, 520, 550."""
        assert table_4_2_rebar_properties("#8", 420)["fu_mpa"] == 620
        assert table_4_2_rebar_properties("#8", 520)["fu_mpa"] == 690
        assert table_4_2_rebar_properties("2.5in", 550)["fu_mpa"] == 700

    def test_bar_size_without_hash(self):
        r = table_4_2_rebar_properties("10", 520)
        assert r["bar_size"] == "#10"
        assert r["area_mm2"] == 819

    def test_grade_550_is_the_63_mm_bar_only(self):
        """Table 4-2 prints Grade 550 for one bar, 63 mm (2.5 in): 3168 mm2,
        1747 kN. It prints no Grade 550 #14 or #18."""
        r = table_4_2_rebar_properties("63 mm", 550)
        assert r["bar_size"] == "2.5in"
        assert r["yield_kn"] == 1747
        for bar in ("#14", "#18"):
            with pytest.raises(ValueError, match="not available in Grade 550"):
                table_4_2_rebar_properties(bar, 550)
        with pytest.raises(ValueError, match="not available in Grade 520"):
            table_4_2_rebar_properties("2.5in")

    def test_invalid_bar_size(self):
        with pytest.raises(ValueError):
            table_4_2_rebar_properties("#20", 520)

    def test_invalid_grade(self):
        with pytest.raises(ValueError):
            table_4_2_rebar_properties("#10", 600)

    def test_bar_not_in_grade(self):
        with pytest.raises(ValueError, match="not available"):
            table_4_2_rebar_properties("#10", 420)

    def test_all_grade_520_bars(self):
        for size in ["#6", "#7", "#8", "#9", "#10", "#11", "#14", "#18"]:
            r = table_4_2_rebar_properties(size, 520)
            assert r["area_mm2"] > 0
            assert r["yield_kn"] > 0


# ============================================================================
# Table 4-5: Pipe Properties
# ============================================================================

class TestTable45:
    """Tests for table_4_5_pipe_properties()."""

    def test_api_n80_177_8_12_6(self):
        r = table_4_5_pipe_properties(177.8, 12.6, "n80")
        assert r["od_mm"] == 177.8
        assert r["wall_mm"] == 12.6
        assert r["area_mm2"] == 6560
        assert r["yield_kn"] == 3620
        assert r["fy_mpa"] == 552

    def test_api_n80_244_5(self):
        r = table_4_5_pipe_properties(244.5, 12.0, "n80")
        assert r["area_mm2"] == 8760
        assert r["yield_kn"] == 4830

    def test_a519_139_7(self):
        r = table_4_5_pipe_properties(139.7, 12.7, "a519")
        assert r["area_mm2"] == 5067
        assert r["yield_kn"] == 1270
        assert "A519" in r["steel_type"]

    def test_a519_273_1(self):
        r = table_4_5_pipe_properties(273.1, 16.0, "a519")
        assert r["area_mm2"] == 12850
        assert r["yield_kn"] == 3190

    def test_a519_fy_from_note_4_with_print_note(self):
        """FHWA-NHI-05-039 Table 4-5, p. 4-33 (PDF page 89): no Fy column;
        note (4) "Fy = 241 MPa (36 ksi)". 36 ksi = 248 MPa, which the four
        printed yield strengths imply (1,270, 1,540, 1,890, 3,190 kN on
        5,067, 6,208, 7,600, 12,850 mm2); 248 is returned with a note
        (lead's ruling on gec-47)."""
        printed = {(139.7, 12.7): (5067, 1270), (168.3, 12.7): (6208, 1540),
                   (203.2, 12.7): (7600, 1890), (273.1, 16.0): (12850, 3190)}
        for (od, wall), (area, kn) in printed.items():
            r = table_4_5_pipe_properties(od, wall, "a519")
            assert (r["area_mm2"], r["yield_kn"]) == (area, kn)
            assert r["fy_mpa"] == 248
            assert "241 MPa (36 ksi)" in r["print_note"]
            assert "implies 250.6" in r["print_note"]
            assert "36 ksi" in r["fy_basis"]
        n80 = table_4_5_pipe_properties(177.8, 12.6, "n80")
        assert n80["fy_mpa"] == 552 and "print_note" not in n80

    def test_no_wall_returns_list(self):
        r = table_4_5_pipe_properties(139.7, 0, "n80")
        assert isinstance(r, list)
        assert len(r) == 2  # Two 139.7mm pipes in N-80

    def test_invalid_od(self):
        with pytest.raises(ValueError):
            table_4_5_pipe_properties(100.0, 10.0, "n80")

    def test_invalid_steel_type(self):
        with pytest.raises(ValueError):
            table_4_5_pipe_properties(139.7, 9.17, "xyz")

    def test_steel_type_case_insensitive(self):
        r = table_4_5_pipe_properties(139.7, 9.17, "N80")
        assert r["fy_mpa"] == 552

    def test_a106_alias(self):
        r = table_4_5_pipe_properties(168.3, 12.7, "a106")
        assert r["area_mm2"] == 6208


# ============================================================================
# Table 5-3: Alpha Bond
# ============================================================================

class TestTable53:
    """Tests for table_5_3_alpha_bond()."""

    def test_silt_clay_soft_type_a(self):
        r = table_5_3_alpha_bond("silt_clay_soft", "A")
        assert r["alpha_bond_min_kpa"] == 35
        assert r["alpha_bond_max_kpa"] == 70

    def test_silt_clay_soft_type_d(self):
        r = table_5_3_alpha_bond("silt_clay_soft", "D")
        assert r["alpha_bond_min_kpa"] == 50
        assert r["alpha_bond_max_kpa"] == 145

    def test_sand_coarse_dense_type_b(self):
        r = table_5_3_alpha_bond("sand_coarse_dense", "B")
        assert r["alpha_bond_min_kpa"] == 120
        assert r["alpha_bond_max_kpa"] == 360

    def test_gravel_type_c(self):
        r = table_5_3_alpha_bond("gravel", "C")
        assert r["alpha_bond_min_kpa"] == 145
        assert r["alpha_bond_max_kpa"] == 360

    def test_glacial_till_type_d(self):
        r = table_5_3_alpha_bond("glacial_till", "D")
        assert r["alpha_bond_min_kpa"] == 120
        assert r["alpha_bond_max_kpa"] == 335

    def test_limestone_type_a(self):
        r = table_5_3_alpha_bond("limestone", "A")
        assert r["alpha_bond_min_kpa"] == 1035
        assert r["alpha_bond_max_kpa"] == 2070

    def test_granite_basalt(self):
        r = table_5_3_alpha_bond("granite_basalt", "A")
        assert r["alpha_bond_min_kpa"] == 1380
        assert r["alpha_bond_max_kpa"] == 4200

    def test_rock_type_b_not_available(self):
        with pytest.raises(ValueError):
            table_5_3_alpha_bond("limestone", "B")

    def test_rock_type_c_not_available(self):
        with pytest.raises(ValueError):
            table_5_3_alpha_bond("sandstone", "C")

    def test_partial_match(self):
        r = table_5_3_alpha_bond("limestone", "A")
        assert r["soil_type"] == "limestone"

    def test_invalid_soil_type(self):
        with pytest.raises(ValueError):
            table_5_3_alpha_bond("organic_muck", "A")

    def test_all_soil_types(self):
        for soil in ["silt_clay_soft", "silt_clay_stiff", "sand_fine_loose",
                      "sand_coarse_dense", "gravel", "glacial_till",
                      "soft_shale", "hard_shale", "limestone",
                      "sandstone", "granite_basalt"]:
            r = table_5_3_alpha_bond(soil, "A")
            assert r["alpha_bond_min_kpa"] > 0
            assert r["alpha_bond_max_kpa"] > r["alpha_bond_min_kpa"]

    def test_type_d_higher_than_a(self):
        """Type D (postgrout) should give higher bond than Type A (gravity)."""
        a = table_5_3_alpha_bond("sand_coarse_dense", "A")
        d = table_5_3_alpha_bond("sand_coarse_dense", "D")
        assert d["alpha_bond_max_kpa"] >= a["alpha_bond_max_kpa"]

    def test_soft_soil_lower_than_dense(self):
        """Soft clay should have lower bond than dense sand."""
        soft = table_5_3_alpha_bond("silt_clay_soft", "B")
        dense = table_5_3_alpha_bond("sand_coarse_dense", "B")
        assert soft["alpha_bond_max_kpa"] < dense["alpha_bond_max_kpa"]

    def test_description_populated(self):
        r = table_5_3_alpha_bond("gravel", "A")
        assert "Gravel" in r["soil_description"]


# ============================================================================
# Table 5-4: Group Efficiency
# ============================================================================

class TestTable54:
    """Tests for table_5_4_group_efficiency()."""

    def test_all_conditions(self):
        r = table_5_4_group_efficiency()
        assert len(r) == 5
        assert "cap_firm_contact" in r

    def test_firm_contact(self):
        r = table_5_4_group_efficiency("cap_firm_contact")
        assert r["efficiency"] == 1.0

    def test_soft_soil_2_5d(self):
        r = table_5_4_group_efficiency("cap_no_contact_soft_2.5d")
        assert r["efficiency"] == 0.65

    def test_soft_soil_3d(self):
        r = table_5_4_group_efficiency("cap_no_contact_soft_3d")
        assert r["efficiency"] == 0.70

    def test_invalid_condition(self):
        with pytest.raises(ValueError):
            table_5_4_group_efficiency("invalid")


# ============================================================================
# Table 5-5: Corrosion Criteria
# ============================================================================

class TestTable55:
    """Tests for table_5_5_corrosion_criteria()."""

    def test_returns_all_criteria(self):
        r = table_5_5_corrosion_criteria()
        assert "ph" in r
        assert "resistivity" in r
        assert "sulfates" in r
        assert "chlorides" in r

    def test_sulfate_threshold(self):
        r = table_5_5_corrosion_criteria()
        assert r["sulfates"]["threshold"] == 200

    def test_chloride_threshold(self):
        r = table_5_5_corrosion_criteria()
        assert r["chlorides"]["threshold"] == 100

    def test_resistivity_threshold(self):
        r = table_5_5_corrosion_criteria()
        assert r["resistivity"]["threshold"] == 3000


# ============================================================================
# Table 5-7: Epsilon_50
# ============================================================================

class TestTable57:
    """Tests for table_5_7_epsilon_50()."""

    def test_soft(self):
        assert table_5_7_epsilon_50("soft") == 0.020

    def test_medium(self):
        assert table_5_7_epsilon_50("medium") == 0.010

    def test_stiff(self):
        assert table_5_7_epsilon_50("stiff") == 0.005

    def test_soft_higher_than_stiff(self):
        assert table_5_7_epsilon_50("soft") > table_5_7_epsilon_50("stiff")

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_5_7_epsilon_50("very_stiff")


# ============================================================================
# Table 5-8: Epsilon_50 for Stiff Clays
# ============================================================================

class TestTable58:
    """Tests for table_5_8_epsilon_50_stiff()."""

    def test_su_50(self):
        assert table_5_8_epsilon_50_stiff(50) == pytest.approx(0.007)

    def test_su_100(self):
        assert table_5_8_epsilon_50_stiff(100) == pytest.approx(0.005)

    def test_su_400(self):
        assert table_5_8_epsilon_50_stiff(400) == pytest.approx(0.004)

    # FHWA-NHI-05-039 Table 5-8, p. 5-56 (PDF page 148): three ranges of
    # su, one value each: 50-100 kPa 0.007; 100-200 kPa 0.005; 300-400 kPa
    # 0.004. No row for 200-300 kPa.
    @pytest.mark.parametrize("su, eps", [
        (50, 0.007), (60, 0.007), (75, 0.007), (99, 0.007),
        (100, 0.005), (150, 0.005), (200, 0.005),
        (300, 0.004), (350, 0.004), (400, 0.004),
    ])
    def test_printed_range_value(self, su, eps):
        """The value of the printed range, not an interpolation between
        ranges (75 kPa gave 0.006 and 150 kPa 0.0045 before)."""
        assert table_5_8_epsilon_50_stiff(su) == eps

    @pytest.mark.parametrize("su", [201, 250, 299])
    def test_no_row_between_200_and_300(self, su):
        with pytest.raises(ValueError, match="no row between 200 and 300"):
            table_5_8_epsilon_50_stiff(su)

    def test_decreasing_with_su(self):
        e1 = table_5_8_epsilon_50_stiff(60)
        e2 = table_5_8_epsilon_50_stiff(150)
        assert e1 > e2

    def test_low_out_of_range(self):
        with pytest.raises(ValueError):
            table_5_8_epsilon_50_stiff(40)

    def test_high_out_of_range(self):
        with pytest.raises(ValueError):
            table_5_8_epsilon_50_stiff(500)


# ============================================================================
# Table 5-9: Soil Modulus k for Sand
# ============================================================================

class TestTable59:
    """Tests for table_5_9_soil_modulus_k_sand()."""

    def test_loose_submerged(self):
        assert table_5_9_soil_modulus_k_sand("loose", True) == 5430

    def test_dense_above_wt(self):
        assert table_5_9_soil_modulus_k_sand("dense", False) == 61000

    def test_medium_submerged(self):
        assert table_5_9_soil_modulus_k_sand("medium", True) == 16300

    def test_above_wt_higher(self):
        """Above water table should give higher k than submerged."""
        sub = table_5_9_soil_modulus_k_sand("loose", True)
        dry = table_5_9_soil_modulus_k_sand("loose", False)
        assert dry > sub

    def test_dense_higher_than_loose(self):
        k_loose = table_5_9_soil_modulus_k_sand("loose", True)
        k_dense = table_5_9_soil_modulus_k_sand("dense", True)
        assert k_dense > k_loose

    def test_invalid_density(self):
        with pytest.raises(ValueError):
            table_5_9_soil_modulus_k_sand("very_loose")

    def test_default_not_submerged(self):
        k = table_5_9_soil_modulus_k_sand("medium")
        assert k == 24430  # Above WT value


# ============================================================================
# Table 5-10: Soil Modulus k for Clay
# ============================================================================

class TestTable510:
    """Tests for table_5_10_soil_modulus_k_clay()."""

    def test_soft_static(self):
        assert table_5_10_soil_modulus_k_clay("soft", "static") == 8140

    def test_stiff_cyclic(self):
        assert table_5_10_soil_modulus_k_clay("stiff", "cyclic") == 54300

    def test_hard_static(self):
        assert table_5_10_soil_modulus_k_clay("hard", "static") == 543000

    def test_very_stiff(self):
        k = table_5_10_soil_modulus_k_clay("very_stiff", "static")
        assert k == 271000

    # FHWA-NHI-05-039 Table 5-10, p. 5-56 (PDF page 148), kPa/m.
    @pytest.mark.parametrize("consistency, loading, k", [
        ("soft", "static", 8140), ("medium", "static", 27150),
        ("stiff", "static", 136000), ("very_stiff", "static", 271000),
        ("hard", "static", 543000),
        ("stiff", "cyclic", 54300), ("very_stiff", "cyclic", 108500),
        ("hard", "cyclic", 217000),
    ])
    def test_every_printed_value(self, consistency, loading, k):
        assert table_5_10_soil_modulus_k_clay(consistency, loading) == k

    @pytest.mark.parametrize("consistency", ["soft", "medium"])
    def test_no_cyclic_k_for_soft_and_medium(self, consistency):
        """The Cyclic columns print '-' for Soft and Medium clay; the static
        value was returned for them before."""
        with pytest.raises(ValueError, match="prints no cyclic k"):
            table_5_10_soil_modulus_k_clay(consistency, "cyclic")

    def test_stiff_cyclic_less_than_static(self):
        """For stiff+ clay, cyclic loading gives lower k."""
        s = table_5_10_soil_modulus_k_clay("stiff", "static")
        c = table_5_10_soil_modulus_k_clay("stiff", "cyclic")
        assert c < s

    def test_invalid_consistency(self):
        with pytest.raises(ValueError):
            table_5_10_soil_modulus_k_clay("firm")

    def test_invalid_loading(self):
        with pytest.raises(ValueError):
            table_5_10_soil_modulus_k_clay("soft", "dynamic")


# ============================================================================
# Table 5-11: Fixity
# ============================================================================

class TestTable511:
    """Tests for table_5_11_fixity()."""

    def test_pinned(self):
        r = table_5_11_fixity(0)
        assert r["embedment_mm"] == 300
        assert "pinned" in r["description"].lower()

    def test_partial(self):
        r = table_5_11_fixity(50)
        assert r["embedment_mm"] == 450

    def test_fixed(self):
        r = table_5_11_fixity(100)
        assert r["embedment_mm"] == 600

    def test_columns_as_printed(self):
        """FHWA-NHI-05-039 Table 5-11, p. 5-58 (PDF page 150)."""
        r0 = table_5_11_fixity(0)
        assert r0["embedment_limit"] == "300 mm (12 in.) or less"
        assert "Reinforcing bar embedment with or without bearing plate" \
            in r0["description"]
        r50 = table_5_11_fixity(50)
        assert r50["embedment_limit"] == "450 mm (18 in.)"
        assert "Shear connection between casing and existing footing" \
            in r50["description"]
        r100 = table_5_11_fixity(100)
        assert r100["embedment_limit"] == "600 mm (24 in.) or more"
        assert "additional detailing" not in r100["description"]
        assert "only one row of piles in direction of loading" in r100["note"]

    def test_invalid_pct(self):
        with pytest.raises(ValueError):
            table_5_11_fixity(75)


# ============================================================================
# Table 5-12: Elastic Modulus by Soil Type
# ============================================================================

class TestTable512:
    """Tests for table_5_12_elastic_modulus()."""

    def test_clay_soft(self):
        r = table_5_12_elastic_modulus("clay_soft")
        assert r["es_min_kpa"] == 2400
        assert r["es_max_kpa"] == 14400

    def test_sand_dense(self):
        r = table_5_12_elastic_modulus("sand_dense")
        assert r["es_min_kpa"] == 48000
        assert r["es_max_kpa"] == 76000

    def test_sand_rows_note_says_what_the_page_shows(self):
        """Table 5-12, p. 5-69 (PDF page 161): sand medium dense prints
        '29,000 - 96,000 (600 - 1,000)' and dense '96,000 - 76,000 (1,000 -
        1,600)'. The held kPa are the table's own kPa for 600, 1,000 and
        1,600 ksf in other rows (29,000; 48,000; 76,000), not 48 x ksf
        (600 x 48 = 28,800; 1,600 x 48 = 76,800); the note said '48 kPa
        per ksf' (independent check)."""
        md = table_5_12_elastic_modulus("sand_medium_dense")
        d = table_5_12_elastic_modulus("sand_dense")
        assert (md["es_min_kpa"], md["es_max_kpa"]) == (29000, 48000)
        for r in (md, d):
            assert "48 kPa per ksf" not in r["note"]
            assert "in its other rows" in r["note"]
        assert "28,728 and 47,880" in md["note"]
        assert "47,880 and 76,608" in d["note"]

    def test_gravel_dense(self):
        r = table_5_12_elastic_modulus("gravel_dense")
        assert r["es_min_kpa"] == 96000
        assert r["es_max_kpa"] == 192000

    def test_silt(self):
        r = table_5_12_elastic_modulus("silt")
        assert r["es_min_kpa"] == 1900
        assert r["es_max_kpa"] == 19000

    def test_loess(self):
        r = table_5_12_elastic_modulus("loess")
        assert r["es_min_kpa"] == 14400
        assert r["es_max_kpa"] == 57500

    def test_description_populated(self):
        r = table_5_12_elastic_modulus("fine_sand_loose")
        assert "Fine Sand" in r["description"]

    def test_invalid_soil(self):
        with pytest.raises(ValueError):
            table_5_12_elastic_modulus("peat")

    def test_all_entries(self):
        for key in ["clay_soft", "clay_medium_stiff", "clay_very_stiff",
                     "loess", "silt", "fine_sand_loose",
                     "fine_sand_medium_dense", "fine_sand_dense",
                     "sand_loose", "sand_medium_dense", "sand_dense",
                     "gravel_loose", "gravel_medium_dense", "gravel_dense"]:
            r = table_5_12_elastic_modulus(key)
            assert r["es_max_kpa"] > r["es_min_kpa"]


# ============================================================================
# Table 5-13: Elastic Modulus from SPT
# ============================================================================

class TestTable513:
    """Tests for table_5_13_elastic_modulus_spt()."""

    def test_silts_n20(self):
        r = table_5_13_elastic_modulus_spt("silts_sandy_silts", 20)
        assert r["es_kpa"] == 8000  # 400 * 20

    def test_clean_sand_n15(self):
        r = table_5_13_elastic_modulus_spt("clean_fine_medium_sand", 15)
        assert r["es_kpa"] == 10500  # 700 * 15

    def test_coarse_sand_n30(self):
        r = table_5_13_elastic_modulus_spt("coarse_sand_gravel", 30)
        assert r["es_kpa"] == 30000  # 1000 * 30

    def test_sandy_gravels_n25(self):
        r = table_5_13_elastic_modulus_spt("sandy_gravels", 25)
        assert r["es_kpa"] == 30000  # 1200 * 25

    def test_factor_increases_with_grain_size(self):
        """Coarser soils should have higher factor."""
        r1 = table_5_13_elastic_modulus_spt("silts_sandy_silts", 10)
        r2 = table_5_13_elastic_modulus_spt("sandy_gravels", 10)
        assert r2["es_kpa"] > r1["es_kpa"]

    def test_invalid_soil(self):
        with pytest.raises(ValueError):
            table_5_13_elastic_modulus_spt("clay", 10)

    def test_zero_n(self):
        with pytest.raises(ValueError):
            table_5_13_elastic_modulus_spt("sandy_gravels", 0)

    def test_negative_n(self):
        with pytest.raises(ValueError):
            table_5_13_elastic_modulus_spt("sandy_gravels", -5)
