"""Tests for GEC-13 table lookup functions."""

import pytest

from geotech_references.gec_13.tables import (
    table_1_2_applicability,
    table_1_3_by_function,
    table_1_6_unit_cost,
    table_2_1_pvd_applications,
    table_3_1_lightweight_fill,
    table_4_3_applied_energy,
    equation_4_1_ddc_depth,
    figure_4_1_ddc_depth,
    table_8_1_jet_grouting_systems,
    table_8_6_soilcrete_strength,
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
# Table 4-3: DDC Applied Energy Guidelines (REF-62)
# ============================================================================

class TestTable43:
    """table_4_3_applied_energy() against GEC-13 Vol I Table 4-3, p. 4-46."""

    def test_all_rows(self):
        assert [r["key"] for r in table_4_3_applied_energy()] == [
            "pervious_coarse", "semi_pervious", "landfills"]

    @pytest.mark.parametrize("key,ft,kj,pct", [
        ("pervious_coarse", (4100, 5200), (200, 250), (33, 41)),
        ("semi_pervious", (5200, 7200), (250, 350), (41, 60)),
        ("landfills", (12400, 22700), (600, 1100), (100, 180)),
    ])
    def test_as_printed(self, key, ft, kj, pct):
        (r,) = [x for x in table_4_3_applied_energy() if x["key"] == key]
        assert (r["unit_applied_energy_ft_lbf_per_ft3_low"],
                r["unit_applied_energy_ft_lbf_per_ft3_high"]) == ft
        assert (r["unit_applied_energy_kj_per_m3_low"],
                r["unit_applied_energy_kj_per_m3_high"]) == kj
        assert (r["percent_standard_proctor_energy_low"],
                r["percent_standard_proctor_energy_high"]) == pct
        assert "Table 4-3" in r["reference"] and "p. 4-46" in r["reference"]

    def test_zone_filter(self):
        (r,) = table_4_3_applied_energy("zone 1")
        assert r["key"] == "pervious_coarse"

    def test_units_agree_as_printed(self):
        """The two printed unit columns agree: 1 kJ/m3 = 20.885 ft-lbf/ft3
        (within the print's rounding), and the note's standard Proctor
        12,400 ft-lbf/ft3 is 100 % on the landfill row."""
        for r in table_4_3_applied_energy():
            for end in ("low", "high"):
                ft = r[f"unit_applied_energy_ft_lbf_per_ft3_{end}"]
                kj = r[f"unit_applied_energy_kj_per_m3_{end}"]
                assert ft == pytest.approx(kj * 20.885, rel=0.06)
        (land,) = table_4_3_applied_energy("landfill")
        assert land["unit_applied_energy_ft_lbf_per_ft3_low"] == 12400
        assert land["percent_standard_proctor_energy_low"] == 100

    def test_no_match(self):
        assert table_4_3_applied_energy("nonexistent") == []


# ============================================================================
# Eq. 4-1: DDC Depth of Improvement (REF-63)
# ============================================================================

class TestEquation41DdcDepth:
    """equation_4_1_ddc_depth(): D = n (W H)^0.5, GEC-13 Eq. 4-1, p. 4-40.

    W and H below are made-up values, not from any project.
    """

    W, H = 12.0, 18.0          # made-up tamper mass (Mg) and drop (m)

    def _hand(self, n):
        return n * (self.W * self.H) ** 0.5

    def test_default_is_most_soils_n_05(self):
        r = equation_4_1_ddc_depth(self.W, self.H)
        assert r["n"] == 0.5
        assert r["deposit"] == "most_soils"
        assert r["depth_m"] == pytest.approx(self._hand(0.5), abs=0.005)
        assert r["choices"]["n"]["given"] is False

    def test_landfill_n_04(self):
        r = equation_4_1_ddc_depth(self.W, self.H, "landfill")
        assert r["n"] == 0.4
        assert r["depth_m"] == pytest.approx(self._hand(0.4), abs=0.005)
        assert "landfills" in r["n_basis"]

    @pytest.mark.parametrize("n", [0.3, 0.4, 0.5, 0.65, 0.8])
    def test_given_n_in_range(self, n):
        r = equation_4_1_ddc_depth(self.W, self.H, n=n)
        assert r["n"] == n
        assert r["depth_m"] == pytest.approx(self._hand(n), abs=0.005)
        assert r["choices"]["n"]["given"] is True
        assert "Figure 4-21" in r["n_basis"]

    def test_range_bounds_at_03_and_08(self):
        r = equation_4_1_ddc_depth(self.W, self.H)
        assert (r["n_low"], r["n_high"]) == (0.3, 0.8)
        assert r["depth_low_m"] == pytest.approx(self._hand(0.3), abs=0.005)
        assert r["depth_high_m"] == pytest.approx(self._hand(0.8), abs=0.005)
        assert "Figure 4-21" in r["range_basis"]

    def test_round_numbers(self):
        # made-up: W H = 100 Mg-m, so (W H)^0.5 = 10 m
        r = equation_4_1_ddc_depth(10.0, 10.0)
        assert r["depth_m"] == 5.0
        assert r["depth_low_m"] == 3.0
        assert r["depth_high_m"] == 8.0
        assert equation_4_1_ddc_depth(10.0, 10.0, "landfill")["depth_m"] == 4.0

    @pytest.mark.parametrize("n", [0.29, 0.81, 1.0, 0.0])
    def test_n_outside_range_refused(self, n):
        with pytest.raises(ValueError, match="0.3 to 0.8"):
            equation_4_1_ddc_depth(self.W, self.H, n=n)

    @pytest.mark.parametrize("old", ["pervious_coarse", "semi_pervious",
                                     "impervious", "waste_fills"])
    def test_old_soil_types_refused(self, old):
        with pytest.raises(ValueError, match="prints no table of n"):
            equation_4_1_ddc_depth(self.W, self.H, old)

    def test_unknown_deposit_refused(self):
        with pytest.raises(ValueError, match="Unknown deposit"):
            equation_4_1_ddc_depth(self.W, self.H, "peat")

    def test_zero_weight_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            equation_4_1_ddc_depth(0, 20.0)

    def test_negative_height_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            equation_4_1_ddc_depth(20.0, -5.0)

    def test_citation(self):
        ref = equation_4_1_ddc_depth(self.W, self.H)["reference"]
        assert "Eq. 4-1, p. 4-40" in ref
        assert "Figure 4-21" in ref
        assert "FHWA-NHI-16-027" in ref
        assert "Lukas" not in ref
        doc = equation_4_1_ddc_depth.__doc__
        assert "Eq. 4-1, p. 4-40" in doc

    def test_old_name_is_alias(self):
        for args, kw in [((self.W, self.H), {}),
                         ((self.W, self.H, "landfill"), {}),
                         ((self.W, self.H), {"n": 0.7})]:
            assert figure_4_1_ddc_depth(*args, **kw) == \
                equation_4_1_ddc_depth(*args, **kw)
        assert "Alias of equation_4_1_ddc_depth" in figure_4_1_ddc_depth.__doc__
        with pytest.raises(ValueError, match="prints no table of n"):
            figure_4_1_ddc_depth(self.W, self.H, "pervious_coarse")

    def test_agent_source_labels(self):
        from agents.gec13_agent import gec13_describe_method
        import json
        for name in ("equation_4_1_ddc_depth", "figure_4_1_ddc_depth"):
            info = json.loads(gec13_describe_method(name))
            assert "Eq. 4-1, p. 4-40" in info["reference"], info


# ============================================================================
# Table 8-1: Jet Grouting Systems (REF-62)
# ============================================================================

class TestTable81:
    """table_8_1_jet_grouting_systems() against GEC-13 Vol II Table 8-1,
    p. 8-26."""

    def test_all_systems(self):
        assert [r["system"] for r in table_8_1_jet_grouting_systems()] == [
            "Single Fluid", "Double Fluid", "Triple Fluid",
            "SuperJet/MegaJet/UltraJet/STRAJet", "X-Jet"]

    def test_single_fluid_as_printed(self):
        (r,) = table_8_1_jet_grouting_systems("single")
        assert r["advantages"] == [
            "Simple system for equipment and tooling",
            "Good for sealing vertical joints",
            "Good in cohesionless soils"]
        assert r["disadvantages"] == [
            "Smallest geometry created", "Hardest to control heave",
            "Difficult to control quality in cohesive soils"]
        assert "Table 8-1" in r["reference"] and "p. 8-26" in r["reference"]

    def test_triple_fluid_as_printed(self):
        (r,) = table_8_1_jet_grouting_systems("triple")
        assert "Best underpinning system" in r["advantages"]
        assert r["disadvantages"] == [
            "Most complex system due to equipment and tooling",
            "Requires significant experience"]

    def test_no_invented_numbers(self):
        """GEC-13 prints no diameter or strength per system."""
        for r in table_8_1_jet_grouting_systems():
            assert not any(k.startswith(("column_diameter", "strength"))
                           for k in r)
        assert "2.5 to 15 ft" in r["note"]

    def test_no_match(self):
        assert table_8_1_jet_grouting_systems("quadruple") == []


# ============================================================================
# Table 8-6: Single-Fluid Soilcrete Strengths (REF-62)
# ============================================================================

class TestTable86:
    """table_8_6_soilcrete_strength() against GEC-13 Vol II Table 8-6,
    p. 8-71."""

    @pytest.mark.parametrize("soil,low,high", [
        ("sands and gravel", 750, 1250),
        ("silty sands", 500, 750),
        ("clays", 250, 500),
        ("peat", None, 250),
    ])
    def test_as_printed(self, soil, low, high):
        (r,) = table_8_6_soilcrete_strength(soil)
        assert (r["ucs_psi_low"], r["ucs_psi_high"]) == (low, high)
        assert "Table 8-6" in r["reference"] and "p. 8-71" in r["reference"]

    def test_kpa_conversion(self):
        (r,) = table_8_6_soilcrete_strength("clays")
        assert (r["ucs_kpa_low"], r["ucs_kpa_high"]) == (1724, 3447)

    def test_all_rows(self):
        assert len(table_8_6_soilcrete_strength()) == 4

    def test_no_match(self):
        assert table_8_6_soilcrete_strength("nonexistent") == []


# ============================================================================
# REF-62: lookups whose values GEC-13 does not print are gone
# ============================================================================

class TestRef62Removed:
    """GEC-13 Table 4-1 (p. 4-34) is tamper equipment, Table 8-2 (p. 8-38)
    permeation grout components, and chapter 7 numbers no tables; the DDC,
    deep mixing and jet grouting values that cited them match no held
    manual."""

    @pytest.mark.parametrize("name", [
        "table_4_1_ddc_parameters",
        "table_7_2_deep_mixing_strength",
        "table_8_2_jet_grouting_systems",
    ])
    def test_not_in_gec13(self, name):
        import geotech_references.gec_13.tables as t
        assert not hasattr(t, name)


class TestRef62Vol2Citations:
    """GEC-13 Vol II's cover prints FHWA-NHI-16-028 (Vol I's prints -027):
    the chapter 8 tables and the agent's Vol II labels cite -028 (REF-62
    review)."""

    @pytest.mark.parametrize("func", [
        table_8_1_jet_grouting_systems,
        table_8_6_soilcrete_strength,
    ])
    def test_vol2_tables_cite_16_028(self, func):
        for r in func():
            assert "FHWA-NHI-16-028" in r["reference"], r["key"]
            assert "Vol II" in r["reference"], r["key"]
            assert "16-027" not in r["reference"], r["key"]
        assert "FHWA-NHI-16-028" in func.__doc__
        assert "16-027" not in func.__doc__

    def test_table_4_3_stays_vol1(self):
        for r in table_4_3_applied_energy():
            assert "FHWA-NHI-16-027" in r["reference"]
            assert "Vol I," in r["reference"]

    def test_agent_labels_vol2_as_16_028(self):
        from agents import gec13_agent
        _, info = gec13_agent._load_registry()
        for name in ("table_8_1_jet_grouting_systems",
                     "table_8_6_soilcrete_strength",
                     "equation_7_4_composite_modulus",
                     "equation_8_1_groutability_ratio"):
            ref = info[name]["reference"]
            assert "FHWA-NHI-16-028" in ref and "Vol II" in ref, name
            assert "16-027" not in ref and "Chapters 1-5" not in ref, name
        assert "Table 8-1, p. 8-26" in (
            info["table_8_1_jet_grouting_systems"]["reference"])
        assert "Table 8-6, p. 8-71" in (
            info["table_8_6_soilcrete_strength"]["reference"])
        for name, entry in info.items():
            ref = entry.get("reference", "")
            assert not ("16-027" in ref and "Vol II" in ref), name


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
