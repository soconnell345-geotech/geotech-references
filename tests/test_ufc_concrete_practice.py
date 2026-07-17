"""Tests for UFC 3-250-04 (Standard Practice for Concrete Pavements) table,
equation, and structured reference text functions.
"""

import pytest

from geotech_references.ufc_concrete_practice.tables import (
    table_3_1_weather_severity,
    table_3_2_deleterious_material_limit,
    table_3_3_aggregate_test_time,
    table_3_4_portland_cement_type,
    table_3_5_blended_cement_type,
    table_3_6_hydraulic_cement_type,
    table_3_7_ggbf_slag_grade,
    table_3_8_admixture_type,
    table_8_1_dowel_misalignment_impact,
    dowel_bar_alignment_tolerance,
    dowel_bar_corner_clearance,
    dowel_bar_drilled_hole_oversize,
    table_9_1_maximum_joint_spacing,
    edge_slump_tolerance,
    table_d1_cracking_causes,
    table_e1_rcc_gradation,
)
from geotech_references.ufc_concrete_practice.equations import (
    coarseness_factor,
    workability_factor,
)
from geotech_references._retrieval import (
    load_chapter,
    retrieve_section,
    search_sections,
    list_chapters,
)


# ============================================================================
# Table 3-1: Weather severity
# ============================================================================

class TestTable31WeatherSeverity:
    def test_moderate_low_freezing_index(self):
        r = table_3_1_weather_severity(400, 5.0)
        assert r["severity"] == "moderate"

    def test_moderate_low_precip(self):
        r = table_3_1_weather_severity(600, 0.5)
        assert r["severity"] == "moderate"

    def test_severe_high_precip(self):
        r = table_3_1_weather_severity(600, 1.5)
        assert r["severity"] == "severe"

    def test_boundary_freezing_index_500_is_moderate(self):
        r = table_3_1_weather_severity(500, 3.0)
        assert r["severity"] == "moderate"

    def test_reference_present(self):
        r = table_3_1_weather_severity(400, 0.0)
        assert "Table 3-1" in r["reference"]


# ============================================================================
# Table 3-2: Deleterious material limits
# ============================================================================

class TestTable32DeleteriousMaterialLimit:
    def test_clay_lumps_coarse_severe(self):
        r = table_3_2_deleterious_material_limit(
            "clay_lumps_and_friable_particles", "coarse_severe"
        )
        assert r["limit_pct_mass"] == 0.2

    def test_clay_lumps_fine(self):
        r = table_3_2_deleterious_material_limit(
            "clay_lumps_and_friable_particles", "fine"
        )
        assert r["limit_pct_mass"] == 1.0

    def test_alias_minus_200(self):
        r = table_3_2_deleterious_material_limit("minus_200", "coarse_moderate")
        assert r["limit_pct_mass"] == 0.5

    def test_not_applicable_cell_returns_none(self):
        r = table_3_2_deleterious_material_limit("shale", "fine")
        assert r["limit_pct_mass"] is None

    def test_total_fine_incl_minus_200(self):
        r = table_3_2_deleterious_material_limit(
            "total_fine_incl_minus_200", "fine"
        )
        assert r["limit_pct_mass"] == 3.0

    def test_invalid_material(self):
        with pytest.raises(ValueError):
            table_3_2_deleterious_material_limit("nonexistent", "fine")

    def test_invalid_category(self):
        with pytest.raises(ValueError):
            table_3_2_deleterious_material_limit("shale", "nonexistent")


# ============================================================================
# Table 3-3: Aggregate test time
# ============================================================================

class TestTable33AggregateTestTime:
    def test_c1260(self):
        r = table_3_3_aggregate_test_time("astm_c1260")
        assert r["time_for_result"] == "16 days"

    def test_alias_bare_c666(self):
        r = table_3_3_aggregate_test_time("c666")
        assert "2 to 3 months" in r["time_for_result"]

    def test_c1293_two_years(self):
        r = table_3_3_aggregate_test_time("c1293")
        assert "2 years" in r["time_for_result"]

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_3_3_aggregate_test_time("nonexistent")


# ============================================================================
# Table 3-4: Portland cement types
# ============================================================================

class TestTable34PortlandCement:
    def test_type_i(self):
        r = table_3_4_portland_cement_type("type_i")
        assert "Most widely available" in r["application"]

    def test_roman_numeral_input(self):
        r = table_3_4_portland_cement_type("V")
        assert r["cement_type"] == "type_v"
        assert "sulfate resistance" in r["application"]

    def test_bare_number_input(self):
        r = table_3_4_portland_cement_type("3")
        assert r["cement_type"] == "type_iii"
        assert "high early strength" in r["application"]

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_3_4_portland_cement_type("type_ix")


# ============================================================================
# Table 3-5: Blended cement types
# ============================================================================

class TestTable35BlendedCement:
    def test_type_is_slag(self):
        r = table_3_5_blended_cement_type("type_is")
        assert "blast furnace slag" in r["composition"]

    def test_alias_ip(self):
        r = table_3_5_blended_cement_type("ip")
        assert "pozzolan" in r["composition"]

    def test_type_s(self):
        r = table_3_5_blended_cement_type("type_s")
        assert "at least 70 percent slag" in r["composition"]

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_3_5_blended_cement_type("type_zz")


# ============================================================================
# Table 3-6: Hydraulic cement types
# ============================================================================

class TestTable36HydraulicCement:
    def test_type_hs(self):
        r = table_3_6_hydraulic_cement_type("type_hs")
        assert "high sulfate resistance" in r["use"]

    def test_alias_bare_letters(self):
        r = table_3_6_hydraulic_cement_type("lh")
        assert "low heat of hydration" in r["use"]

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_3_6_hydraulic_cement_type("type_zz")


# ============================================================================
# Table 3-7: GGBF slag grades
# ============================================================================

class TestTable37GgbfSlagGrade:
    def test_grade_120_most_reactive(self):
        r = table_3_7_ggbf_slag_grade("grade_120")
        assert "Most reactive" in r["properties"]

    def test_numeric_alias(self):
        r = table_3_7_ggbf_slag_grade(80)
        assert r["grade"] == "grade_80"
        assert "not normally used for airfield" in r["properties"]

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_3_7_ggbf_slag_grade("grade_999")


# ============================================================================
# Table 3-8: Admixture types
# ============================================================================

class TestTable38AdmixtureType:
    def test_type_g(self):
        r = table_3_8_admixture_type("type_g")
        assert "high range" in r["use"] and "retarding" in r["use"]

    def test_alias_bare_letter(self):
        r = table_3_8_admixture_type("c")
        assert "Accelerating" in r["use"]

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_3_8_admixture_type("type_z")


# ============================================================================
# Table 8-1: Dowel bar misalignment impact
# ============================================================================

class TestTable81DowelMisalignment:
    def test_horizontal_translation_load_transfer_only(self):
        r = table_8_1_dowel_misalignment_impact("horizontal_translation")
        assert r["affects_load_transfer"] is True
        assert r["affects_spalling"] is False
        assert r["affects_cracking"] is False

    def test_vertical_translation_spalling_and_load_transfer(self):
        r = table_8_1_dowel_misalignment_impact("vertical_translation")
        assert r["affects_spalling"] is True
        assert r["affects_cracking"] is False
        assert r["affects_load_transfer"] is True

    def test_horizontal_skew_affects_all_three(self):
        r = table_8_1_dowel_misalignment_impact("horizontal_skew")
        assert r["affects_spalling"] is True
        assert r["affects_cracking"] is True
        assert r["affects_load_transfer"] is True

    def test_vertical_skew_affects_all_three(self):
        r = table_8_1_dowel_misalignment_impact("vertical_skew")
        assert all(
            r[k] is True
            for k in ("affects_spalling", "affects_cracking", "affects_load_transfer")
        )

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_8_1_dowel_misalignment_impact("diagonal_translation")


# ============================================================================
# Dowel bar installation tolerances (inline lookups)
# ============================================================================

class TestDowelBarTolerances:
    def test_alignment_tolerance_values(self):
        r = dowel_bar_alignment_tolerance()
        assert r["skew_mm_per_m"] == 10
        assert r["horizontal_longitudinal_translation_mm"] == 15
        assert r["vertical_translation_mm"] == 13

    def test_corner_clearance_values(self):
        r = dowel_bar_corner_clearance()
        assert r["minimum_mm"] == 150
        assert r["preferred_mm"] == 300

    def test_drilled_hole_oversize_values(self):
        r = dowel_bar_drilled_hole_oversize()
        assert r["oversize_min_mm"] == 3
        assert r["oversize_max_mm"] == 6


# ============================================================================
# Table 9-1: Maximum joint spacing
# ============================================================================

class TestTable91MaximumJointSpacing:
    def test_thin_slab_airfield(self):
        r = table_9_1_maximum_joint_spacing(8, "airfield")
        assert r["joint_spacing_min_ft"] == 12.5
        assert r["joint_spacing_max_ft"] == 15

    def test_thin_slab_road_narrower_min(self):
        r = table_9_1_maximum_joint_spacing(8, "road")
        assert r["joint_spacing_min_ft"] == 10
        assert r["joint_spacing_max_ft"] == 15

    def test_mid_thickness_slab(self):
        r = table_9_1_maximum_joint_spacing(10, "airfield")
        assert r["joint_spacing_min_ft"] == 15
        assert r["joint_spacing_max_ft"] == 20

    def test_thick_slab(self):
        r = table_9_1_maximum_joint_spacing(14, "airfield")
        assert r["joint_spacing_min_ft"] == 20
        assert r["joint_spacing_max_ft"] == 20

    def test_metric_conversion_present(self):
        r = table_9_1_maximum_joint_spacing(10)
        assert r["joint_spacing_min_m"] == pytest.approx(4.57, abs=0.05)

    def test_invalid_thickness(self):
        with pytest.raises(ValueError):
            table_9_1_maximum_joint_spacing(0)

    def test_invalid_facility_type(self):
        with pytest.raises(ValueError):
            table_9_1_maximum_joint_spacing(10, "parking_garage")


# ============================================================================
# Edge slump tolerance
# ============================================================================

class TestEdgeSlumpTolerance:
    def test_values(self):
        r = edge_slump_tolerance()
        assert r["local_limit_mm"] == 6
        assert r["absolute_max_mm"] == 10
        assert r["max_pct_of_joint_length_at_local_limit"] == 15


# ============================================================================
# Table D-1: Early-age cracking causes
# ============================================================================

class TestTableD1CrackingCauses:
    def test_plastic_shrinkage(self):
        r = table_d1_cracking_causes("plastic_shrinkage")
        assert any("evaporation" in c.lower() for c in r["possible_causes"])

    def test_alias_random(self):
        r = table_d1_cracking_causes("random")
        assert r["crack_type"] == "random_no_orientation"
        assert len(r["possible_causes"]) > 0

    def test_corner_cracking(self):
        r = table_d1_cracking_causes("corner_cracking")
        assert any("dowel" in c.lower() for c in r["possible_causes"])

    def test_settlement_over_dowel_bars(self):
        r = table_d1_cracking_causes("settlement_cracks")
        assert any("dowel" in c.lower() or "tie" in c.lower() for c in r["possible_causes"])

    def test_re_entrant(self):
        r = table_d1_cracking_causes("reentrant")
        assert r["crack_type"] == "re_entrant"

    def test_invalid(self):
        with pytest.raises(ValueError):
            table_d1_cracking_causes("diagonal_cracking")


# ============================================================================
# Table E-1: RCC combined aggregate gradation
# ============================================================================

class TestTableE1RccGradation:
    def test_single_sieve(self):
        r = table_e1_rcc_gradation(4.75)
        assert r["pct_passing_min"] == 40
        assert r["pct_passing_max"] == 65

    def test_full_table(self):
        r = table_e1_rcc_gradation()
        assert len(r["rows"]) == 11
        assert r["rows"][0]["sieve_mm"] == 25
        assert r["rows"][0]["pct_passing_min"] == 100

    def test_finest_sieve(self):
        r = table_e1_rcc_gradation(0.075)
        assert r["pct_passing_min"] == 2
        assert r["pct_passing_max"] == 10

    def test_invalid_sieve(self):
        with pytest.raises(ValueError):
            table_e1_rcc_gradation(1.0)


# ============================================================================
# Equations: coarseness factor / workability factor (Equation 7-1)
# ============================================================================

class TestCoarsenessWorkabilityFactor:
    def test_coarseness_factor_basic(self):
        r = coarseness_factor(pct_retained_9_5mm=40, pct_retained_2_36mm=60)
        assert r["coarseness_factor"] == pytest.approx(66.7, abs=0.1)
        assert r["in_recommended_range"] is True

    def test_coarseness_factor_gap_graded_flag(self):
        r = coarseness_factor(pct_retained_9_5mm=80, pct_retained_2_36mm=100)
        assert r["coarseness_factor"] == 80.0
        assert "note" not in r or r["coarseness_factor"] <= 80

    def test_coarseness_factor_above_75_flags_gap_graded(self):
        r = coarseness_factor(pct_retained_9_5mm=78, pct_retained_2_36mm=100)
        assert r["coarseness_factor"] == 78.0
        assert "note" in r
        assert "gap-graded" in r["note"].lower()

    def test_coarseness_factor_zero_denominator_raises(self):
        with pytest.raises(ValueError):
            coarseness_factor(pct_retained_9_5mm=40, pct_retained_2_36mm=0)

    def test_workability_factor_at_baseline_no_adjustment(self):
        r = workability_factor(
            pct_passing_2_36mm=35, cementitious_content_kg_m3=335
        )
        assert r["workability_factor"] == 35.0

    def test_workability_factor_below_baseline_no_adjustment(self):
        r = workability_factor(
            pct_passing_2_36mm=35, cementitious_content_kg_m3=300
        )
        assert r["workability_factor"] == 35.0

    def test_workability_factor_above_baseline_adjusts_upward(self):
        # 391 kg/m3 is 56 kg/m3 above the 335 baseline -> +2.5%
        r = workability_factor(
            pct_passing_2_36mm=35, cementitious_content_kg_m3=391
        )
        assert r["workability_factor"] == pytest.approx(37.5, abs=0.01)

    def test_workability_factor_negative_inputs_raise(self):
        with pytest.raises(ValueError):
            workability_factor(pct_passing_2_36mm=-1, cementitious_content_kg_m3=335)
        with pytest.raises(ValueError):
            workability_factor(pct_passing_2_36mm=35, cementitious_content_kg_m3=-1)


# ============================================================================
# Structured reference text retrieval smoke tests
# ============================================================================

_ALL_CHAPTERS = list(range(1, 19))  # chapters 1-11 + appendices A-G as 12-18


class TestLoadChapter:
    @pytest.mark.parametrize("chapter", _ALL_CHAPTERS)
    def test_all_chapters_load(self, chapter):
        data = load_chapter("ufc_concrete_practice", chapter)
        assert isinstance(data, dict)
        assert data["chapter"] == chapter

    @pytest.mark.parametrize("chapter", _ALL_CHAPTERS)
    def test_chapter_has_required_fields(self, chapter):
        data = load_chapter("ufc_concrete_practice", chapter)
        assert data["reference_id"] == "UFC 3-250-04"
        assert "chapter_title" in data
        assert isinstance(data["sections"], list)
        assert len(data["sections"]) > 0

    @pytest.mark.parametrize("chapter", _ALL_CHAPTERS)
    def test_sections_have_required_fields(self, chapter):
        data = load_chapter("ufc_concrete_practice", chapter)
        for section in data["sections"]:
            assert "section_id" in section
            assert "title" in section
            assert "body" in section
            assert "key_points" in section
            assert "applicability" in section

    def test_chapter_9_is_joint_sawing_and_sealing(self):
        data = load_chapter("ufc_concrete_practice", 9)
        assert "joint" in data["chapter_title"].lower()

    def test_chapter_13_is_appendix_b_inspection_checklist(self):
        data = load_chapter("ufc_concrete_practice", 13)
        assert "inspection" in data["chapter_title"].lower()

    def test_nonexistent_chapter(self):
        with pytest.raises(FileNotFoundError):
            load_chapter("ufc_concrete_practice", 99)


class TestRetrieveSection:
    def test_retrieve_dowel_installation_section(self):
        section = retrieve_section("ufc_concrete_practice", "8-5.2")
        assert "dowel" in section["title"].lower()

    def test_retrieve_joint_spacing_section(self):
        section = retrieve_section("ufc_concrete_practice", "9-3.2.1")
        assert "tables" in section
        assert any("9-1" in t for t in section["tables"])

    def test_retrieve_appendix_section(self):
        # Appendix D (chapter 15) uses sequential section ids 15-1..15-7
        section = retrieve_section("ufc_concrete_practice", "15-1")
        assert "title" in section and "body" in section

    def test_nonexistent_section(self):
        with pytest.raises(KeyError):
            retrieve_section("ufc_concrete_practice", "99-99")


class TestSearchSections:
    def test_search_dowel_bar(self):
        results = search_sections("ufc_concrete_practice", "dowel bar")
        assert len(results) > 0
        assert "chapter" in results[0]
        assert "chapter_title" in results[0]

    def test_search_joint_sawing(self):
        results = search_sections("ufc_concrete_practice", "joint sawing")
        assert len(results) > 0

    def test_search_curing_compound(self):
        results = search_sections("ufc_concrete_practice", "curing compound")
        assert len(results) > 0

    def test_search_no_results(self):
        results = search_sections("ufc_concrete_practice", "xyzzy_nonexistent_term_abc")
        assert results == []


class TestListChapters:
    def test_list_chapters_returns_all_18(self):
        chapters = list_chapters("ufc_concrete_practice")
        assert len(chapters) == 18
        numbers = sorted(c["chapter"] for c in chapters)
        assert numbers == _ALL_CHAPTERS

    def test_each_chapter_has_sections(self):
        chapters = list_chapters("ufc_concrete_practice")
        for c in chapters:
            assert len(c["sections"]) > 0
