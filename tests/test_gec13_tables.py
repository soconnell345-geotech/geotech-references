"""Tests for GEC-13 table lookup functions."""

import pytest

from geotech_references.gec_13.tables import (
    table_1_2_applicability,
    table_1_3_by_function,
    table_1_6_unit_cost,
    table_2_1_pvd_applications,
    table_3_1_lightweight_fill,
    table_4_1_ddc_parameters,
    figure_4_1_ddc_depth,
    table_7_2_deep_mixing_strength,
    table_8_2_jet_grouting_systems,
)


# ============================================================================
# Table 1-2: General Applicability of Technologies
# ============================================================================

class TestTable12:
    """Tests for table_1_2_applicability()."""

    def test_all_entries(self):
        results = table_1_2_applicability()
        assert len(results) == 25

    def test_filter_by_category_grouting(self):
        results = table_1_2_applicability(category="grouting")
        assert len(results) == 5
        assert all("grouting" in r["category"] for r in results)

    def test_filter_by_category_deep_compaction(self):
        results = table_1_2_applicability(category="deep_compaction")
        assert len(results) == 2

    def test_filter_by_technology_pvd(self):
        results = table_1_2_applicability(technology="PVD")
        assert len(results) == 1
        assert "vertical_drains" == results[0]["category"]

    def test_filter_by_technology_stone(self):
        results = table_1_2_applicability(technology="stone")
        assert len(results) == 1
        assert "Stone Columns" in results[0]["technology"]

    def test_combined_filter(self):
        results = table_1_2_applicability(
            category="reinforced", technology="wall"
        )
        assert len(results) >= 1
        assert any("Wall" in r["technology"] for r in results)

    def test_no_match(self):
        results = table_1_2_applicability(technology="xyzzy_nonexistent")
        assert results == []

    def test_entries_have_required_fields(self):
        results = table_1_2_applicability()
        for entry in results:
            assert "category" in entry
            assert "technology" in entry
            assert "applicability" in entry

    def test_aggregate_columns(self):
        results = table_1_2_applicability(category="aggregate")
        assert len(results) == 2
        techs = {r["technology"] for r in results}
        assert "Stone Columns" in techs
        assert "Rammed Aggregate Piers" in techs

    def test_reinforced_soil(self):
        results = table_1_2_applicability(category="reinforced_soil")
        assert len(results) == 4


# ============================================================================
# Table 1-3: Technologies Classified by Function
# ============================================================================

class TestTable13:
    """Tests for table_1_3_by_function()."""

    def test_all_functions(self):
        results = table_1_3_by_function()
        assert len(results) == 8

    def test_shear_strength(self):
        results = table_1_3_by_function("shear")
        assert len(results) == 1
        assert "Vibro-Compaction" in results[0]["technologies"]

    def test_density(self):
        results = table_1_3_by_function("density")
        assert len(results) == 1
        assert "Dynamic Compaction" in results[0]["technologies"]

    def test_permeability(self):
        results = table_1_3_by_function("permeability")
        assert len(results) == 1
        assert "Jet Grouting" in results[0]["technologies"]

    def test_liquefaction(self):
        results = table_1_3_by_function("liquefaction")
        assert len(results) == 1
        assert "Earthquake Drains" in results[0]["technologies"]

    def test_drainage(self):
        results = table_1_3_by_function("drainage")
        assert len(results) == 1

    def test_consolidation(self):
        results = table_1_3_by_function("consolidation")
        assert len(results) == 1

    def test_lateral(self):
        results = table_1_3_by_function("lateral")
        assert len(results) == 1
        assert "Soil Nail Walls" in results[0]["technologies"]

    def test_deformation(self):
        results = table_1_3_by_function("deformation")
        assert len(results) == 1

    def test_no_match(self):
        results = table_1_3_by_function("nonexistent_xyz")
        assert results == []

    def test_entries_have_fields(self):
        results = table_1_3_by_function()
        for entry in results:
            assert "function" in entry
            assert "description" in entry
            assert "technologies" in entry
            assert isinstance(entry["technologies"], list)
            assert "comment" in entry


# ============================================================================
# Table 1-6: Comparative Unit Costs
# ============================================================================

class TestTable16:
    """Tests for table_1_6_unit_cost()."""

    def test_all_entries(self):
        results = table_1_6_unit_cost()
        assert len(results) == 24

    def test_grouting_costs(self):
        results = table_1_6_unit_cost(category="grouting")
        assert len(results) == 6

    def test_pvd_cost(self):
        results = table_1_6_unit_cost(technology="PVD")
        assert len(results) == 1
        assert results[0]["cost_low"] == 0.50
        assert results[0]["cost_high"] == 4.00

    def test_stone_column_cost(self):
        results = table_1_6_unit_cost(technology="stone")
        assert len(results) == 1
        assert results[0]["cost_low"] == 15.0
        assert results[0]["cost_high"] == 60.0

    def test_mse_wall_cost(self):
        results = table_1_6_unit_cost(technology="MSE")
        assert len(results) == 1
        assert results[0]["cost_low"] == 30.0
        assert results[0]["cost_high"] == 65.0

    def test_jet_grouting_cost(self):
        results = table_1_6_unit_cost(technology="jet")
        assert len(results) == 1
        assert results[0]["cost_low"] == 250.0

    def test_no_match(self):
        results = table_1_6_unit_cost(technology="nonexistent")
        assert results == []

    def test_entries_have_cost_fields(self):
        results = table_1_6_unit_cost()
        for entry in results:
            assert "cost_low" in entry
            assert "cost_high" in entry
            assert "unit" in entry
            assert entry["cost_low"] > 0
            assert entry["cost_high"] >= entry["cost_low"]

    def test_deep_compaction_costs(self):
        results = table_1_6_unit_cost(category="deep_compaction")
        assert len(results) == 2

    def test_pavement_stabilization(self):
        results = table_1_6_unit_cost(category="pavement")
        assert len(results) == 3


# ============================================================================
# Table 2-1: Common Uses of PVDs
# ============================================================================

class TestTable21:
    """Tests for table_2_1_pvd_applications()."""

    def test_all_entries(self):
        results = table_2_1_pvd_applications()
        assert len(results) == 8

    def test_highway(self):
        results = table_2_1_pvd_applications("highway")
        assert len(results) == 2

    def test_liquefaction(self):
        results = table_2_1_pvd_applications("liquefaction")
        assert len(results) == 1
        assert results[0]["increase_stability"] is True
        assert results[0]["accelerate_settlements"] is True

    def test_pile_foundations(self):
        results = table_2_1_pvd_applications("pile")
        assert len(results) == 1
        assert results[0]["increase_stability"] is False
        assert results[0]["accelerate_settlements"] is True

    def test_no_match(self):
        results = table_2_1_pvd_applications("nonexistent")
        assert results == []

    def test_entries_have_fields(self):
        results = table_2_1_pvd_applications()
        for entry in results:
            assert "application" in entry
            assert "increase_stability" in entry
            assert "accelerate_settlements" in entry


# ============================================================================
# Table 3-1: Lightweight Fill Material Properties
# ============================================================================

class TestTable31:
    """Tests for table_3_1_lightweight_fill()."""

    def test_all_entries(self):
        results = table_3_1_lightweight_fill()
        assert len(results) == 8

    def test_geofoam(self):
        results = table_3_1_lightweight_fill("geofoam")
        assert len(results) == 1
        assert results[0]["unit_weight_pcf_low"] < 5

    def test_tire(self):
        results = table_3_1_lightweight_fill("tire")
        assert len(results) == 1
        assert results[0]["material"] == "Tire Derived Aggregate (TDA)"

    def test_wood(self):
        results = table_3_1_lightweight_fill("wood")
        assert len(results) == 1

    def test_fly_ash(self):
        results = table_3_1_lightweight_fill("fly")
        assert len(results) == 1

    def test_entries_have_unit_weights(self):
        results = table_3_1_lightweight_fill()
        for entry in results:
            assert "unit_weight_pcf_low" in entry
            assert "unit_weight_pcf_high" in entry
            assert "unit_weight_kn_m3_low" in entry
            assert "unit_weight_kn_m3_high" in entry
            assert entry["unit_weight_pcf_low"] < entry["unit_weight_pcf_high"]


# ============================================================================
# Table 4-1: DDC Design Parameters
# ============================================================================

class TestTable41:
    """Tests for table_4_1_ddc_parameters()."""

    def test_all_entries(self):
        results = table_4_1_ddc_parameters()
        assert len(results) == 3

    def test_pervious(self):
        results = table_4_1_ddc_parameters("pervious")
        assert len(results) >= 1
        assert results[0]["max_depth_ft"] == 36

    def test_impervious(self):
        results = table_4_1_ddc_parameters("impervious")
        assert len(results) == 1
        assert results[0]["max_depth_ft"] == 20

    def test_no_match(self):
        results = table_4_1_ddc_parameters("nonexistent")
        assert results == []


# ============================================================================
# Figure 4-1: DDC Depth of Influence
# ============================================================================

class TestFigure41:
    """Tests for figure_4_1_ddc_depth()."""

    def test_pervious_typical(self):
        """20-tonne weight dropped 20 m in clean sand."""
        result = figure_4_1_ddc_depth(20.0, 20.0, "pervious_coarse")
        assert result["depth_low_m"] == pytest.approx(10.0, abs=0.5)
        assert result["depth_high_m"] == pytest.approx(12.0, abs=0.5)

    def test_semi_pervious(self):
        result = figure_4_1_ddc_depth(15.0, 15.0, "semi_pervious")
        assert result["depth_low_m"] < result["depth_high_m"]
        assert result["depth_low_m"] > 0

    def test_impervious(self):
        result = figure_4_1_ddc_depth(10.0, 10.0, "impervious")
        assert result["depth_low_m"] < result["depth_high_m"]

    def test_zero_weight_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            figure_4_1_ddc_depth(0, 20.0)

    def test_negative_height_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            figure_4_1_ddc_depth(20.0, -5.0)

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError, match="Unknown soil_type"):
            figure_4_1_ddc_depth(20.0, 20.0, "unknown_type")

    def test_result_has_all_keys(self):
        result = figure_4_1_ddc_depth(20.0, 15.0)
        assert "depth_low_m" in result
        assert "depth_high_m" in result
        assert "n_low" in result
        assert "n_high" in result
        assert "soil_type" in result
        assert "description" in result


# ============================================================================
# Table 7-2: Deep Mixing Strength
# ============================================================================

class TestTable72:
    """Tests for table_7_2_deep_mixing_strength()."""

    def test_all_entries(self):
        results = table_7_2_deep_mixing_strength()
        assert len(results) == 7

    def test_filter_clay(self):
        results = table_7_2_deep_mixing_strength(soil_type="clay")
        assert len(results) >= 2
        assert all("clay" in r["soil_type"].lower() for r in results)

    def test_filter_ddm(self):
        results = table_7_2_deep_mixing_strength(method="DDM")
        assert len(results) >= 3
        assert all("DDM" in r["method"] or "dry" in r["method"].lower()
                   for r in results)

    def test_filter_wdm(self):
        results = table_7_2_deep_mixing_strength(method="WDM")
        assert len(results) >= 3

    def test_sand_wdm_highest_strength(self):
        """Sand WDM has the highest qu range."""
        sand = table_7_2_deep_mixing_strength(soil_type="sand", method="WDM")
        assert len(sand) == 1
        assert sand[0]["qu_high_kpa"] == 4000

    def test_organic_peat_lower_than_clay(self):
        """Organic/peat has lower strength than mineral clay for same method."""
        clay = table_7_2_deep_mixing_strength(soil_type="soft_clay", method="DDM")
        peat = table_7_2_deep_mixing_strength(soil_type="organic", method="DDM")
        assert clay[0]["qu_low_kpa"] > peat[0]["qu_low_kpa"]

    def test_entries_have_required_fields(self):
        results = table_7_2_deep_mixing_strength()
        for entry in results:
            assert "soil_type" in entry
            assert "method" in entry
            assert "qu_low_kpa" in entry
            assert "qu_high_kpa" in entry
            assert entry["qu_low_kpa"] < entry["qu_high_kpa"]

    def test_no_match(self):
        results = table_7_2_deep_mixing_strength(soil_type="nonexistent_xyz")
        assert results == []


# ============================================================================
# Table 8-2: Jet Grouting Systems
# ============================================================================

class TestTable82:
    """Tests for table_8_2_jet_grouting_systems()."""

    def test_all_systems(self):
        results = table_8_2_jet_grouting_systems()
        assert len(results) == 3

    def test_single_fluid(self):
        results = table_8_2_jet_grouting_systems("single")
        assert len(results) == 1
        assert results[0]["column_diameter_mm_high"] <= 600

    def test_triple_fluid_largest(self):
        results = table_8_2_jet_grouting_systems("triple")
        assert len(results) == 1
        assert results[0]["column_diameter_mm_high"] == 2000

    def test_diameter_increases_with_system(self):
        single = table_8_2_jet_grouting_systems("single")[0]
        double = table_8_2_jet_grouting_systems("double")[0]
        triple = table_8_2_jet_grouting_systems("triple")[0]
        assert single["column_diameter_mm_high"] <= double["column_diameter_mm_high"]
        assert double["column_diameter_mm_high"] <= triple["column_diameter_mm_high"]

    def test_entries_have_required_fields(self):
        results = table_8_2_jet_grouting_systems()
        for entry in results:
            assert "system" in entry
            assert "column_diameter_mm_low" in entry
            assert "column_diameter_mm_high" in entry
            assert "strength_mpa_low" in entry
            assert "strength_mpa_high" in entry

    def test_no_match(self):
        results = table_8_2_jet_grouting_systems("quadruple")
        assert results == []


# ============================================================================
# REF-61: lookups GEC-13 does not print are gone
# ============================================================================

class TestRemovedTables:
    """GEC-13 Vol II prints Table 9-2 on subgrade stabilization (p. 9-3) and
    Table 10-1 on geosynthetic properties (p. 10-12), and has no Table 11-1.
    The soil-nail bond, micropile bond and geosynthetic reduction-factor
    lookups that carried those numbers matched no held manual, and were
    removed (REF-61). The printed tables live in their own manuals."""

    @pytest.mark.parametrize("name", [
        "table_9_2_nail_bond_strength",
        "table_10_1_micropile_bond_stress",
        "table_11_1_geosynthetic_reduction_factors",
    ])
    def test_not_in_gec13(self, name):
        import geotech_references.gec_13.tables as t
        assert not hasattr(t, name)

    def test_micropile_table_5_3_as_printed(self):
        """FHWA-NHI-05-039 Table 5-3, p. 5-21, kPa as printed."""
        from geotech_references.micropile.tables import table_5_3_alpha_bond
        r = table_5_3_alpha_bond("silt_clay_soft", "A")
        assert (r["alpha_bond_min_kpa"], r["alpha_bond_max_kpa"]) == (35, 70)
        r = table_5_3_alpha_bond("sand_coarse_dense", "D")
        assert (r["alpha_bond_min_kpa"], r["alpha_bond_max_kpa"]) == (145, 385)
        r = table_5_3_alpha_bond("granite_basalt", "A")
        assert (r["alpha_bond_min_kpa"], r["alpha_bond_max_kpa"]) == (1380, 4200)

    def test_gec11_table_3_9_as_printed(self):
        """FHWA-NHI-10-024 Vol I Table 3-9, p. 3-32."""
        from geotech_references.gec_11.tables import table_3_9_installation_damage
        (r,) = table_3_9_installation_damage("slit film")
        assert (r["backfill_type1_low"], r["backfill_type1_high"]) == (1.60, 3.00)
        assert (r["backfill_type2_low"], r["backfill_type2_high"]) == (1.10, 2.00)
        (r,) = table_3_9_installation_damage("HDPE")
        assert (r["backfill_type1_low"], r["backfill_type1_high"]) == (1.20, 1.45)
