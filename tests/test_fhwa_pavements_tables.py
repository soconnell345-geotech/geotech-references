"""Tests for geotech_references.fhwa_pavements (FHWA-NHI-05-037, "Geotechnical
Aspects of Pavements", FHWA, May 2006).

Covers the soil/geotech-input lookups, with values cross-checked against the
source PDF tables and equations:
  - Resilient modulus Mr: default values by AASHTO/USCS class (Table 5-35),
    correlations from CBR/R-value/DCP/plasticity (Table 5-34), stress-dependent
    granular Mr (Eq. 5.9), seasonal effective Mr (Eq. 5.11), and backcalc->design.
  - Typical CBR by USCS class (Table 5-28).
  - Soil suitability as a pavement material (Table 4-14).
  - Drainage modifier mi / coefficient Cd (Tables 5-49/5-50), drainage-quality
    definitions (Table 7-4), and permeability (Tables 5-56/5-57).
  - Frost-susceptibility classification F1-F4 (Table 7-12).
  - Swell potential (Tables 5-24, 7-17) and geosynthetic stabilization (Table 7-15).
  - Compaction by AASHTO class (Table 5-18).

Units follow the source (Mr in psi, CBR/R-value in %, unit weight in pcf).
"""

import math

import pytest

from geotech_references.fhwa_pavements.tables import (
    table_5_35_default_resilient_modulus,
    table_5_34_resilient_modulus_correlations,
    table_5_28_typical_cbr,
    table_4_14_soil_as_pavement_material,
    table_7_12_frost_susceptibility,
    table_5_49_drainage_modifier_mi,
    table_5_50_drainage_coefficient_cd,
    table_7_4_drainage_quality_definitions,
    table_5_56_permeability_soils,
    table_5_57_permeability_highway_materials,
    table_5_24_swell_potential_holtz_gibbs,
    table_7_17_swell_potential_ll_pi,
    table_5_18_compaction_aashto,
    table_7_15_geosynthetic_stabilization_criteria,
)
from geotech_references.fhwa_pavements.equations import (
    resilient_modulus_from_cbr,
    resilient_modulus_from_cbr_aashto93,
    resilient_modulus_from_r_value,
    cbr_from_dcp,
    resilient_modulus_from_dcp,
    cbr_from_plasticity_gradation,
    granular_resilient_modulus_bulk_stress,
    seasonal_relative_damage,
    effective_subgrade_modulus_from_relative_damage,
    backcalculated_to_design_modulus,
    modulus_subgrade_reaction_from_cbr,
)


# ===================================================================
# RESILIENT MODULUS — DEFAULT VALUES (Table 5-35)
# ===================================================================


class TestDefaultResilientModulus:
    @pytest.mark.parametrize("cls, typ", [
        ("A-1-a", 40000), ("A-1-b", 38000), ("A-2-4", 32000),
        ("A-7-5", 12000), ("A-7-6", 8000),
    ])
    def test_aashto_typical(self, cls, typ):
        r = table_5_35_default_resilient_modulus(cls)
        assert r["mr_typical_psi"] == typ
        assert r["classification"] == "AASHTO"

    @pytest.mark.parametrize("cls, typ", [
        ("GW", 41000), ("GP", 38000), ("SW", 32000),
        ("CL", 17000), ("CH", 8000), ("ML", 20000),
    ])
    def test_uscs_typical(self, cls, typ):
        r = table_5_35_default_resilient_modulus(cls)
        assert r["mr_typical_psi"] == typ
        assert r["classification"] == "USCS"

    def test_case_insensitive(self):
        assert table_5_35_default_resilient_modulus("a-2-6")["mr_typical_psi"] == 26000
        assert table_5_35_default_resilient_modulus("gw")["mr_typical_psi"] == 41000

    def test_range_present(self):
        r = table_5_35_default_resilient_modulus("A-6")
        assert r["mr_min_psi"] == 13500
        assert r["mr_max_psi"] == 24000

    def test_full_table_both_systems(self):
        r = table_5_35_default_resilient_modulus()
        assert len(r["aashto_rows"]) == 12
        assert len(r["uscs_rows"]) == 20

    def test_full_table_uscs_only(self):
        r = table_5_35_default_resilient_modulus(classification="uscs")
        assert "uscs_rows" in r and "aashto_rows" not in r

    def test_cites_table_and_page(self):
        r = table_5_35_default_resilient_modulus("A-1-a")
        assert r["table"] == "5-35"
        assert r["pdf_page"] == 231

    def test_bad_class_raises(self):
        with pytest.raises(ValueError):
            table_5_35_default_resilient_modulus("Z-9-z")


# ===================================================================
# RESILIENT MODULUS — CORRELATIONS (Table 5-34 + equations)
# ===================================================================


class TestResilientModulusCorrelations:
    def test_full_table_five_correlations(self):
        rows = table_5_34_resilient_modulus_correlations()["rows"]
        assert len(rows) == 5

    def test_cbr_is_preferred(self):
        r = table_5_34_resilient_modulus_correlations("cbr")
        assert "2555" in r["model_psi"]

    def test_alias_r_value(self):
        r = table_5_34_resilient_modulus_correlations("r-value")
        assert r["property"] == "r_value"

    def test_bad_property_raises(self):
        with pytest.raises(ValueError):
            table_5_34_resilient_modulus_correlations("nonsense")


class TestMrFromCbr:
    def test_cbr_10_psi(self):
        # Mr = 2555 * 10^0.64 = 11153 psi
        assert resilient_modulus_from_cbr(10)["mr"] == pytest.approx(11153, abs=2)

    def test_cbr_100_psi(self):
        # Mr = 2555 * 100^0.64 = 48565 psi
        assert resilient_modulus_from_cbr(100)["mr"] == pytest.approx(2555 * 100 ** 0.64, abs=2)

    def test_cbr_mpa_form(self):
        # Mr = 17.6 * 10^0.64 = 76.8 MPa
        r = resilient_modulus_from_cbr(10, units="mpa")
        assert r["mr"] == pytest.approx(17.6 * 10 ** 0.64, abs=0.1)
        assert r["units"] == "mpa"

    def test_zero_cbr_raises(self):
        with pytest.raises(ValueError):
            resilient_modulus_from_cbr(0)

    def test_bad_units_raises(self):
        with pytest.raises(ValueError):
            resilient_modulus_from_cbr(10, units="bananas")


class TestMrFromCbrAASHTO93:
    def test_legacy_form(self):
        # Mr = 1500 * CBR
        assert resilient_modulus_from_cbr_aashto93(8)["mr_psi"] == 12000

    def test_warns_above_10(self):
        assert "warning" in resilient_modulus_from_cbr_aashto93(15)


class TestMrFromRValue:
    def test_r_60(self):
        # Mr = 1155 + 555*60 = 34455 psi
        assert resilient_modulus_from_r_value(60)["mr"] == pytest.approx(34455, abs=1)

    def test_r_mpa(self):
        # Mr = 8.0 + 3.8*60 = 236 MPa
        assert resilient_modulus_from_r_value(60, units="mpa")["mr"] == pytest.approx(236.0, abs=0.1)

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            resilient_modulus_from_r_value(150)


class TestCbrFromDcp:
    def test_dcp_10(self):
        # CBR = 292 / 10^1.12 = 22.2
        assert cbr_from_dcp(10)["cbr"] == pytest.approx(292 / 10 ** 1.12, abs=0.1)

    def test_chained_mr(self):
        r = resilient_modulus_from_dcp(10)
        cbr = 292 / 10 ** 1.12
        assert r["cbr"] == pytest.approx(round(cbr, 1), abs=0.1)
        assert r["mr"] == pytest.approx(2555 * round(cbr, 1) ** 0.64, abs=5)

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            cbr_from_dcp(0)


class TestCbrFromPlasticity:
    def test_wpi_form(self):
        # P200=80%, PI=20 -> wPI = 0.8*20 = 16 -> CBR = 75/(1+0.728*16) = 5.9
        r = cbr_from_plasticity_gradation(80, 20)
        assert r["wpi"] == pytest.approx(16.0, abs=0.01)
        assert r["cbr"] == pytest.approx(75 / (1 + 0.728 * 16), abs=0.1)

    def test_clean_soil_high_cbr(self):
        # wPI = 0 -> CBR = 75
        assert cbr_from_plasticity_gradation(0, 0)["cbr"] == pytest.approx(75.0, abs=0.1)

    def test_bad_p200_raises(self):
        with pytest.raises(ValueError):
            cbr_from_plasticity_gradation(150, 20)


class TestGranularBulkStress:
    def test_k_theta_model(self):
        # Mr = k1 * theta^k2 = 6000 * 30^0.5
        r = granular_resilient_modulus_bulk_stress(30, 6000, 0.5)
        assert r["mr_psi"] == pytest.approx(6000 * 30 ** 0.5, abs=1)

    def test_zero_theta_raises(self):
        with pytest.raises(ValueError):
            granular_resilient_modulus_bulk_stress(0, 6000, 0.5)


class TestSeasonalEffectiveModulus:
    def test_relative_damage(self):
        # uf = 1.18e8 * Mr^-2.32
        r = seasonal_relative_damage(10000)
        assert r["relative_damage_uf"] == pytest.approx(1.18e8 * 10000 ** -2.32, abs=1e-4)

    def test_inverse_roundtrip(self):
        uf = seasonal_relative_damage(7500)["relative_damage_uf"]
        mr = effective_subgrade_modulus_from_relative_damage(uf)["mr_effective_psi"]
        assert mr == pytest.approx(7500, rel=0.01)

    def test_zero_mr_raises(self):
        with pytest.raises(ValueError):
            seasonal_relative_damage(0)


class TestBackcalcToDesign:
    def test_nchrp_subgrade(self):
        # 0.40 * 20000 = 8000
        r = backcalculated_to_design_modulus(20000, "nchrp_1_37a", "subgrade")
        assert r["factor"] == 0.40
        assert r["mr_design_psi"] == 8000

    def test_nchrp_granular(self):
        # 0.67 * 30000 = 20100
        r = backcalculated_to_design_modulus(30000, "nchrp_1_37a", "granular_base")
        assert r["factor"] == 0.67

    def test_aashto_flexible(self):
        r = backcalculated_to_design_modulus(20000, "aashto_1993_flexible")
        assert r["factor"] == 0.33

    def test_aashto_has_no_granular_factor(self):
        with pytest.raises(ValueError):
            backcalculated_to_design_modulus(20000, "aashto_1993_flexible", "granular_base")

    def test_bad_basis_raises(self):
        with pytest.raises(ValueError):
            backcalculated_to_design_modulus(20000, "made_up")


class TestModulusSubgradeReaction:
    def test_k_from_cbr(self):
        # k ~ 1500*5/19.4 = 386.6 pci
        assert modulus_subgrade_reaction_from_cbr(5)["k_pci"] == pytest.approx(1500 * 5 / 19.4, abs=0.5)


# ===================================================================
# TYPICAL CBR (Table 5-28)
# ===================================================================


class TestTypicalCbr:
    @pytest.mark.parametrize("cls, lo, hi", [
        ("GW", 60, 80), ("GP", 35, 60), ("SP", 15, 25),
        ("CL", 5, 15), ("CH", 3, 5),
    ])
    def test_ranges(self, cls, lo, hi):
        r = table_5_28_typical_cbr(cls)
        assert r["cbr_min"] == lo
        assert r["cbr_max"] == hi

    def test_full_table_14_classes(self):
        assert len(table_5_28_typical_cbr()["rows"]) == 14

    def test_bad_class_raises(self):
        with pytest.raises(ValueError):
            table_5_28_typical_cbr("XYZ")


# ===================================================================
# SOIL AS PAVEMENT MATERIAL (Table 4-14)
# ===================================================================


class TestSoilAsPavementMaterial:
    def test_gw_excellent(self):
        r = table_4_14_soil_as_pavement_material("GW")
        assert r["subgrade_strength"] == "Excellent"
        assert r["drainage"] == "Excellent"

    def test_sc_poor(self):
        r = table_4_14_soil_as_pavement_material("SC")
        assert "Poor" in r["subgrade_strength"]

    def test_full_table_eight_classes(self):
        assert len(table_4_14_soil_as_pavement_material()["rows"]) == 8

    def test_fine_grained_not_in_table_raises(self):
        with pytest.raises(ValueError):
            table_4_14_soil_as_pavement_material("CH")


# ===================================================================
# FROST SUSCEPTIBILITY (Table 7-12)
# ===================================================================


class TestFrostSusceptibility:
    def test_f1_negligible_to_low(self):
        r = table_7_12_frost_susceptibility("F1")
        assert r["degree_of_frost_susceptibility"] == "Negligible to low"

    def test_f4_very_high(self):
        r = table_7_12_frost_susceptibility("F4")
        assert r["degree_of_frost_susceptibility"] == "Very high"

    def test_f3_includes_silts(self):
        r = table_7_12_frost_susceptibility("F3")
        joined = " ".join(e["type_of_soil"] for e in r["entries"])
        assert "silt" in joined.lower()

    def test_full_table(self):
        rows = table_7_12_frost_susceptibility()["rows"]
        groups = {r["frost_group"] for r in rows}
        assert groups == {"F1", "F2", "F3", "F4"}

    def test_bad_group_raises(self):
        with pytest.raises(ValueError):
            table_7_12_frost_susceptibility("F9")


# ===================================================================
# DRAINAGE COEFFICIENTS (Tables 5-49, 5-50, 7-4)
# ===================================================================


class TestDrainage:
    def test_mi_excellent_low_saturation(self):
        r = table_5_49_drainage_modifier_mi("excellent")
        assert r["mi"]["<1%"] == "1.40-1.35"

    def test_cd_very_poor_high_saturation(self):
        r = table_5_50_drainage_coefficient_cd("very poor")
        assert r["cd"][">25%"] == "0.70"

    def test_mi_full_table_five_qualities(self):
        assert len(table_5_49_drainage_modifier_mi()["rows"]) == 5

    def test_drainage_definitions(self):
        rows = table_7_4_drainage_quality_definitions()["rows"]
        exc = next(r for r in rows if r["quality_of_drainage"] == "Excellent")
        assert exc["water_removed_within"] == "2 hours"

    def test_bad_quality_raises(self):
        with pytest.raises(ValueError):
            table_5_49_drainage_modifier_mi("amazing")


# ===================================================================
# PERMEABILITY (Tables 5-56, 5-57)
# ===================================================================


class TestPermeability:
    def test_clean_gravel_high_k(self):
        r = table_5_56_permeability_soils("clean gravel")
        assert r["k_cm_s"] == "1 - 100"

    def test_clay_low_k(self):
        r = table_5_56_permeability_soils("clay")
        assert "1e-10" in r["k_cm_s"]

    def test_highway_materials_pcc(self):
        r = table_5_57_permeability_highway_materials("portland cement concrete")
        assert "1e-10" in r["k_m_s"]

    def test_soils_full_table(self):
        assert len(table_5_56_permeability_soils()["rows"]) == 8

    def test_bad_soil_raises(self):
        with pytest.raises(ValueError):
            table_5_56_permeability_soils("moon rock")


# ===================================================================
# SWELL POTENTIAL (Tables 5-24, 7-17)
# ===================================================================


class TestSwellPotential:
    def test_holtz_gibbs_very_high(self):
        r = table_5_24_swell_potential_holtz_gibbs("very high")
        assert r["plasticity_index_pct"] == "> 35"
        assert r["probable_expansion_pct_total_volume"] == "> 30"

    def test_ll_pi_high(self):
        r = table_7_17_swell_potential_ll_pi("high")
        assert r["liquid_limit"] == "> 60"
        assert r["plasticity_index"] == "> 35"

    def test_ll_pi_full_table(self):
        rows = table_7_17_swell_potential_ll_pi()["rows"]
        assert {r["potential_swell"] for r in rows} == {"High", "Marginal", "Low"}

    def test_bad_potential_raises(self):
        with pytest.raises(ValueError):
            table_7_17_swell_potential_ll_pi("extreme")


# ===================================================================
# COMPACTION (Table 5-18) AND GEOSYNTHETIC STABILIZATION (Table 7-15)
# ===================================================================


class TestCompaction:
    def test_a1_unit_weight(self):
        r = table_5_18_compaction_aashto("A-1")
        assert r["dry_unit_weight_pcf_min"] == 115
        assert r["dry_unit_weight_pcf_max"] == 134

    def test_a7_high_moisture(self):
        r = table_5_18_compaction_aashto("A-7")
        assert r["optimum_moisture_content_pct_max"] == 35

    def test_full_table_seven_classes(self):
        assert len(table_5_18_compaction_aashto()["rows"]) == 7

    def test_bad_class_raises(self):
        with pytest.raises(ValueError):
            table_5_18_compaction_aashto("A-9")


class TestGeosyntheticStabilization:
    def test_low_strength_triggers(self):
        r = table_7_15_geosynthetic_stabilization_criteria()
        assert r["low_strength_triggers"]["cbr_max"] == 3
        assert r["low_strength_triggers"]["cu_psi_max"] == 13
        assert r["low_strength_triggers"]["mr_psi_max"] == 4500

    def test_four_conditions(self):
        rows = table_7_15_geosynthetic_stabilization_criteria()["rows"]
        assert len(rows) == 4
        conds = {r["condition"] for r in rows}
        assert "Poor soils" in conds


# ===================================================================
# TEXT RETRIEVAL — chapter JSON (4, 5, 7)
# ===================================================================


class TestTextRetrieval:
    def test_chapter_5_loads(self):
        from geotech_references import _retrieval
        ch = _retrieval.load_chapter("fhwa_pavements", 5)
        assert ch["chapter"] == 5
        assert any(s["section_id"] == "5.4.3" for s in ch["sections"])

    def test_chapter_7_frost_section(self):
        from geotech_references import _retrieval
        ch = _retrieval.load_chapter("fhwa_pavements", 7)
        assert any("frost" in s["title"].lower() for s in ch["sections"])

    def test_search_resilient_modulus(self):
        from geotech_references import _retrieval
        hits = _retrieval.search_sections("fhwa_pavements", "resilient modulus CBR")
        assert len(hits) > 0

    def test_list_chapters(self):
        from geotech_references import _retrieval
        chs = {c["chapter"] for c in _retrieval.list_chapters("fhwa_pavements")}
        assert {4, 5, 7}.issubset(chs)

    def test_retrieve_section_4_7_2_classification(self):
        from geotech_references import _retrieval
        s = _retrieval.retrieve_section("fhwa_pavements", "4.7.2")
        assert "classification" in s["title"].lower()
