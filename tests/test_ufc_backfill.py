"""Tests for geotech_references.ufc_backfill (UFC 3-220-04FA, 16 January 2004,
the reproduced TM 5-818-4/AFM 88-5, Chap. 5; docs/ufc_3_220_04fa_2004.pdf).

Values are the printed ones; each test names the pdf_page_index (0-based) and the
printed page. Rebuilt 2026-11-10 (review pave-06, pave-14): the earlier
ASTM D698 compaction table, millimetre lift table, drain table, Broms
pressure equation and filter ratios are not in this manual and were removed.
"""

import pytest

from geotech_references.ufc_backfill.tables import (
    table_compaction_requirements,
    table_5_1_compaction_criteria,
    table_backfill_material_classification,
    table_maximum_lift_thickness,
    table_compaction_equipment_selection,
    figure_2_5_compaction_induced_lateral_pressure,
)
from geotech_references.ufc_backfill.equations import (
    relative_compaction_check,
)


# ===================================================================
# TABLE TESTS
# ===================================================================


class TestCompactionRequirements:
    """table_compaction_requirements: para 5-1b(4), pdf_page_index 28, printed p. 5-2."""

    def test_open_area_90(self):
        r = table_compaction_requirements("open_area")
        assert r["min_compaction_pct"] == 90
        assert r["max_compaction_pct"] is None
        assert "CE 55" in r["basis"]

    def test_beneath_structures_cohesionless_95_to_100(self):
        r = table_compaction_requirements("beneath_structures_cohesionless")
        assert (r["min_compaction_pct"], r["max_compaction_pct"]) == (95, 100)

    def test_beneath_structures_cohesive_at_least_95(self):
        r = table_compaction_requirements("beneath_structures_cohesive")
        assert (r["min_compaction_pct"], r["max_compaction_pct"]) == (95, None)

    def test_drainage_blankets_and_filters_95_to_100(self):
        r = table_compaction_requirements("drainage_blankets_and_filters")
        assert (r["min_compaction_pct"], r["max_compaction_pct"]) == (95, 100)

    def test_case_insensitive(self):
        r = table_compaction_requirements("OPEN_AREA")
        assert r["min_compaction_pct"] == 90

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown application"):
            table_compaction_requirements("nonexistent")

    def test_unprinted_old_rows_refused(self):
        # The old ASTM D698 rows (e.g. 85 % above pipe) are not printed.
        with pytest.raises(ValueError, match="Unknown application"):
            table_compaction_requirements("above_pipe")

    def test_page_in_reference(self):
        r = table_compaction_requirements("open_area")
        assert "UFC 3-220-04FA" in r["reference"]
        assert "p. 5-2" in r["reference"]


class TestTable51CompactionCriteria:
    """table_5_1_compaction_criteria: Table 5-1, pdf_page_index 29, printed p. 5-3."""

    def test_pervious_compacted(self):
        r = table_5_1_compaction_criteria("pervious", "compacted")
        assert r["degree_of_compaction"] == [
            "90 to 95% of CE 55 maximum density",
            "75 to 85% of relative density"]
        rows = {e["equipment"]: e for e in r["equipment"]}
        assert rows["Rubber-tired roller"]["compacted_lift_thickness_in"] == "12"
        assert rows["Rubber-tired roller"]["passes_or_coverages"] == "2-5 coverages"
        assert rows["Crawler-type tractor"]["compacted_lift_thickness_in"] == "8"
        assert rows["Power hand tamper"]["compacted_lift_thickness_in"] == "6"
        assert r["placement_water_content"] == "Saturate by flooding"

    def test_pervious_semicompacted(self):
        r = table_5_1_compaction_criteria("SP", "semicompacted")
        assert r["soil_group"] == "pervious"
        rows = {e["equipment"]: e for e in r["equipment"]}
        assert rows["Rubber-tired roller"]["compacted_lift_thickness_in"] == "14"
        assert rows["Crawler-type tractor"]["passes_or_coverages"] == "1-2 coverages"
        assert rows["Controlled routing of construction equipment"][
            "compacted_lift_thickness_in"] == "8-10"

    def test_semipervious_impervious_compacted(self):
        r = table_5_1_compaction_criteria("CL")
        assert r["soil_group"] == "semipervious_impervious"
        assert r["degree_of_compaction"] == ["90 to 95% of CE 55 maximum density"]
        rows = {e["equipment"]: e for e in r["equipment"]}
        assert rows["Rubber-tired roller"]["compacted_lift_thickness_in"] == "8"
        assert rows["Sheepsfoot roller"]["passes_or_coverages"] == "4-8 passes"
        assert rows["Sheepsfoot roller"]["compacted_lift_thickness_in"] == "6"
        assert rows["Power hand tamper"]["compacted_lift_thickness_in"] == "4"
        assert r["placement_water_content"] == "Optimum water content"

    def test_semipervious_impervious_semicompacted(self):
        r = table_5_1_compaction_criteria("semipervious_impervious", "semicompacted")
        rows = {e["equipment"]: e for e in r["equipment"]}
        assert rows["Rubber-tired roller"]["passes_or_coverages"] == "2-4 coverages"
        assert rows["Rubber-tired roller"]["compacted_lift_thickness_in"] == "10"
        assert rows["Crawler-type tractor"]["passes_or_coverages"] == "3 coverages"
        assert rows["Controlled routing of construction equipment"][
            "compacted_lift_thickness_in"] == "6-8"

    def test_footnotes(self):
        r = table_5_1_compaction_criteria("pervious", "compacted")
        assert "18,000 and 25,000 lb" in r["footnotes"]["b"]
        assert "20,000 lb" in r["footnotes"]["c"]
        assert "100 lb" in r["footnotes"]["d"]
        r = table_5_1_compaction_criteria("semipervious_impervious")
        assert "250 and 500 psi" in r["footnotes"]["e"]
        assert "95 to 100% of compaction effort" in r["note"]

    def test_invalid_group_and_compaction(self):
        with pytest.raises(ValueError, match="Unknown soil group"):
            table_5_1_compaction_criteria("PT")
        with pytest.raises(ValueError, match="compaction must be"):
            table_5_1_compaction_criteria("pervious", "loose")


class TestBackfillMaterialClassification:
    """table_backfill_material_classification: para 3-3d, pdf_page_index 21-22,
    printed p. 3-5 and 3-6."""

    def test_gw_coarse_grained(self):
        r = table_backfill_material_classification("GW")
        assert r["category"] == "coarse_grained"
        assert "good backfill and foundation support" in r["printed"]
        assert "p. 3-5" in r["reference"]

    def test_sw_coarse_grained(self):
        r = table_backfill_material_classification("SW")
        assert r["category"] == "coarse_grained"

    def test_sp_coarse_grained(self):
        r = table_backfill_material_classification("SP")
        assert r["category"] == "coarse_grained"
        assert "poorly graded sands and gravels" in r["printed"]

    def test_sm_coarse_grained(self):
        r = table_backfill_material_classification("SM")
        assert r["category"] == "coarse_grained"

    def test_cl_low_to_medium_plasticity(self):
        r = table_backfill_material_classification("CL")
        assert r["category"] == "fine_grained_low_to_medium_plasticity"
        assert "good stable backfill" in r["printed"]

    def test_ch_marginal(self):
        r = table_backfill_material_classification("CH")
        assert r["category"] == "marginal_fine_grained_high_plasticity"
        assert "inorganic clay (CH)" in r["printed"]
        assert "p. 3-6" in r["reference"]

    def test_pt_not_placed_by_the_print(self):
        with pytest.raises(ValueError, match="places only"):
            table_backfill_material_classification("PT")

    def test_dual_symbol_gw_gm(self):
        r = table_backfill_material_classification("GW-GM")
        assert r["category"] == "coarse_grained"

    def test_dual_symbol_sp_sc(self):
        r = table_backfill_material_classification("SP-SC")
        assert r["category"] == "coarse_grained"

    def test_dual_symbol_across_categories_refused(self):
        with pytest.raises(ValueError, match="spans two"):
            table_backfill_material_classification("SC-CL")

    def test_case_insensitive(self):
        r = table_backfill_material_classification("gw")
        assert r["category"] == "coarse_grained"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="places only"):
            table_backfill_material_classification("XX")


class TestMaximumLiftThickness:
    """table_maximum_lift_thickness: para 5-1b(3), pdf_page_index 27-28, printed
    p. 5-1 and 5-2."""

    def test_cohesive_sheepsfoot_or_pneumatic(self):
        r = table_maximum_lift_thickness("cohesive_sheepsfoot_or_pneumatic")
        assert r["loose_lift_in"] == "approximately 10"
        assert r["compacted_lift_in"] == "approximately 6"

    def test_cohesionless_sheepsfoot_or_pneumatic(self):
        r = table_maximum_lift_thickness("cohesionless_sheepsfoot_or_pneumatic")
        assert r["loose_lift_in"] == "approximately 8"
        assert r["compacted_lift_in"] == "6"

    def test_heavy_vibratory(self):
        r = table_maximum_lift_thickness("cohesionless_heavy_vibratory")
        assert r["loose_lift_in"] == "about 12 to 15"

    def test_confined_clean_cohesionless(self):
        r = table_maximum_lift_thickness("confined_clean_cohesionless")
        assert r["loose_lift_in"] == "4 to 6"
        assert "walk-behind, dual-drum" in r["printed"]

    def test_confined_cohesive(self):
        r = table_maximum_lift_thickness("confined_cohesive")
        assert r["loose_lift_in"] == "not more than 4"
        assert "rammer compactors" in r["printed"]
        assert "p. 5-2" in r["reference"]

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown case"):
            table_maximum_lift_thickness("hand_tamper")


class TestCompactionEquipmentSelection:
    """table_compaction_equipment_selection: para 5-1b(2), pdf_page_index 27, printed
    p. 5-1."""

    def test_gravels(self):
        r = table_compaction_equipment_selection("gravels")
        assert "crawler tractor or rubber-tired and steel-wheeled rollers" in r["printed"]

    def test_sands_little_or_no_fines(self):
        r = table_compaction_equipment_selection("sands_little_or_no_fines")
        assert "tractor compaction" in r["printed"]

    def test_low_to_medium_plasticity(self):
        r = table_compaction_equipment_selection("fine_grained_low_to_medium_plasticity")
        assert "15,000-pound and above wheel-load class" in r["printed"]

    def test_confined_cohesionless(self):
        r = table_compaction_equipment_selection("cohesionless", "confined")
        assert "at least 100 pounds" in r["printed"]
        assert "p. 5-1" in r["reference"]

    def test_highly_plastic_confined(self):
        r = table_compaction_equipment_selection("fine_grained_highly_plastic", "confined")
        assert "rammer or impact compactors" in r["printed"]

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="No printed case"):
            table_compaction_equipment_selection("organic_muck")
        with pytest.raises(ValueError, match="No printed case"):
            table_compaction_equipment_selection("gravels", "confined")


class TestFigure25CompactionInducedPressure:
    """figure_2_5_compaction_induced_lateral_pressure: Figure 2-5a, pdf_page_index 13,
    printed p. 2-7."""

    def test_ten_ton_smooth_wheel_roller(self):
        r = figure_2_5_compaction_induced_lateral_pressure("10-ton smooth wheel roller")
        assert r["critical_depth_ft"] == 1.9
        assert r["critical_lateral_pressure_psf"] == 420
        assert r["critical_lateral_pressure_kPa"] == pytest.approx(20.11, abs=0.01)

    def test_vibratory_rollers_and_plates(self):
        expect = {"3.2-ton vibratory roller": (1.7, 400),
                  "1.4-ton vibratory roller": (1.2, 260),
                  "400-kg vibratory plate": (1.5, 340),
                  "120-kg vibratory plate": (1.0, 240)}
        for eq, (dc, sig) in expect.items():
            r = figure_2_5_compaction_induced_lateral_pressure(eq)
            assert (r["critical_depth_ft"], r["critical_lateral_pressure_psf"]) == (dc, sig)
        r = figure_2_5_compaction_induced_lateral_pressure("120-kg vibratory plate")
        assert r["critical_depth_m"] == pytest.approx(0.305, abs=0.001)
        assert "6 inches of the wall" in r["printed_basis"]

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown equipment"):
            figure_2_5_compaction_induced_lateral_pressure("bulldozer")


# ===================================================================
# EQUATION TESTS
# ===================================================================


class TestRelativeCompactionCheck:
    """relative_compaction_check: degree of compaction as a percent of
    maximum dry density (para 5-1b(4), pdf_page_index 28, printed p. 5-2)."""

    def test_passes(self):
        r = relative_compaction_check(18.0, 19.0, 95.0)
        # RC = 18/19 * 100 = 94.7% < 95% -> fails
        assert r["passes"] is False

    def test_passes_above_required(self):
        r = relative_compaction_check(18.5, 19.0, 95.0)
        # RC = 18.5/19 * 100 = 97.4%
        assert r["passes"] is True

    def test_exact_boundary(self):
        r = relative_compaction_check(19.0, 20.0, 95.0)
        # RC = 95.0% exactly
        assert r["passes"] is True
        assert r["deficit_pct"] == 0.0

    def test_deficit_calculated(self):
        r = relative_compaction_check(17.0, 19.0, 95.0)
        # RC = 89.5%, deficit = 95 - 89.5 = 5.5
        assert r["deficit_pct"] == pytest.approx(5.5, abs=0.1)

    def test_custom_required_pct(self):
        # 90 percent: open areas, para 5-1b(4), printed p. 5-2.
        r = relative_compaction_check(18.0, 20.0, 90.0)
        assert r["passes"] is True
        assert "CE 55" in r["basis"]
        assert "p. 5-2" in r["reference"]

    def test_zero_density_raises(self):
        with pytest.raises(ValueError, match="dry_density"):
            relative_compaction_check(0, 19.0, 95.0)

    def test_zero_max_density_raises(self):
        with pytest.raises(ValueError, match="max_dry_density"):
            relative_compaction_check(18.0, 0, 95.0)

    def test_invalid_required_pct(self):
        with pytest.raises(ValueError, match="required_pct"):
            relative_compaction_check(18.0, 19.0, 0)
