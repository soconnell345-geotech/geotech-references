"""Tests for geotech_references.gec_4.tables (FHWA-IF-99-015 GEC-4)."""

import pytest

from geotech_references.gec_4.tables import (
    table_6_soil_anchor_transfer_load,
    table_7_bond_stress_rock,
    table_7_bond_stress_cohesive,
    table_7_bond_stress_cohesionless,
    table_8_rock_anchor_transfer_load,
    table_20_corrosion_protection,
)


class TestTable6SoilAnchorTransferLoad:
    """table_6_soil_anchor_transfer_load — Table 6."""

    def test_sand_gravel_medium_dense(self):
        r = table_6_soil_anchor_transfer_load("sand_and_gravel", "medium_dense")
        assert r["ultimate_transfer_load_kN_per_m"] == 220

    def test_sand_gravel_dense(self):
        r = table_6_soil_anchor_transfer_load("sand_and_gravel", "dense")
        assert r["ultimate_transfer_load_kN_per_m"] == 290

    def test_sand_loose(self):
        r = table_6_soil_anchor_transfer_load("sand", "loose")
        assert r["ultimate_transfer_load_kN_per_m"] == 100

    def test_sand_dense(self):
        r = table_6_soil_anchor_transfer_load("sand", "dense")
        assert r["ultimate_transfer_load_kN_per_m"] == 190

    def test_sand_silt_medium_dense(self):
        r = table_6_soil_anchor_transfer_load("sand_and_silt", "medium_dense")
        assert r["ultimate_transfer_load_kN_per_m"] == 100

    def test_silt_clay_stiff(self):
        r = table_6_soil_anchor_transfer_load("silt_clay_mixture", "stiff")
        assert r["ultimate_transfer_load_kN_per_m"] == 30

    def test_silt_clay_hard(self):
        r = table_6_soil_anchor_transfer_load("silt_clay_mixture", "hard")
        assert r["ultimate_transfer_load_kN_per_m"] == 60

    def test_allowable_load_fs2(self):
        r = table_6_soil_anchor_transfer_load("sand", "medium_dense")
        assert r["factor_of_safety"] == 2.0
        assert r["allowable_load_per_m_kN"] == pytest.approx(72.5, abs=0.1)

    def test_gravel_alias(self):
        r = table_6_soil_anchor_transfer_load("gravel", "dense")
        assert r["ultimate_transfer_load_kN_per_m"] == 290

    def test_invalid_soil_raises(self):
        with pytest.raises(ValueError, match="Unknown soil_type"):
            table_6_soil_anchor_transfer_load("clay", "stiff")

    def test_invalid_density_raises(self):
        with pytest.raises(ValueError, match="Unknown density"):
            table_6_soil_anchor_transfer_load("sand", "very_dense")

    def test_very_stiff_refused(self):
        """FHWA-IF-99-015 Table 6, p. 71 (PDF page 92): the silt-clay row
        prints Stiff (10-20) 30 kN/m and Hard (21-40) 60 kN/m only. 'very
        stiff' was answered from the Hard row (review finding gec-30)."""
        for word in ("very stiff", "very_stiff"):
            with pytest.raises(ValueError, match="hard.*stiff|stiff.*hard"):
                table_6_soil_anchor_transfer_load("silt_clay_mixture", word)

    def test_spt_range_returned(self):
        r = table_6_soil_anchor_transfer_load("sand_and_gravel", "loose")
        assert r["spt_range"] == "4-10"

    def test_denser_higher_capacity(self):
        r1 = table_6_soil_anchor_transfer_load("sand", "loose")
        r2 = table_6_soil_anchor_transfer_load("sand", "dense")
        assert r2["ultimate_transfer_load_kN_per_m"] > r1["ultimate_transfer_load_kN_per_m"]


class TestTable7BondStressRock:
    """table_7_bond_stress_rock — Table 7, rock."""

    def test_granite_basalt(self):
        r = table_7_bond_stress_rock("granite_basalt")
        assert r["bond_stress_min_MPa"] == 1.7
        assert r["bond_stress_max_MPa"] == 3.1

    def test_soft_limestone(self):
        r = table_7_bond_stress_rock("soft_limestone")
        assert r["bond_stress_min_MPa"] == 1.0
        assert r["bond_stress_max_MPa"] == 1.4

    def test_soft_shales(self):
        r = table_7_bond_stress_rock("soft_shales")
        assert r["bond_stress_max_MPa"] == pytest.approx(0.8)

    def test_sandstones(self):
        r = table_7_bond_stress_rock("sandstones")
        assert r["bond_stress_min_MPa"] == 0.8

    def test_granite_alias(self):
        r = table_7_bond_stress_rock("granite")
        assert r["rock_type"] == "granite_basalt"

    def test_limestone_and_shale_refused(self):
        """Table 7, p. 73 (PDF page 94) prints dolomitic and soft limestone,
        slates and hard shales and soft shales: 'limestone' and 'shale'
        name two rows each and were answered from the weaker one (review
        finding gec-39)."""
        for word in ("limestone", "shale"):
            with pytest.raises(ValueError, match="Unknown rock_type"):
                table_7_bond_stress_rock(word)
        assert table_7_bond_stress_rock("slates and hard shales")[
            "bond_stress_max_MPa"] == 1.4

    def test_no_factor_of_safety_in_table(self):
        """Table 7 prints no factor of safety; recommended_FS 3.0 on every
        row (soft shales, chalk, marl too) is gone, and the result quotes
        p. 74 (PDF page 95): 3.0 on Table 8 in competent rock, 2.0 for
        intermediate geomaterials (review finding gec-38)."""
        r = table_7_bond_stress_rock("soft_shales")
        assert "recommended_FS" not in r
        assert "factor of safety of 2.0" in r["print_note"]
        assert "0.5 to 5.0 MPa" in r["print_note"]

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown rock_type"):
            table_7_bond_stress_rock("quartzite")


class TestTable7BondStressCohesive:
    """table_7_bond_stress_cohesive — Table 7, cohesive soil."""

    def test_gravity_grouted(self):
        r = table_7_bond_stress_cohesive("gravity_grouted_all")
        assert r["bond_stress_min_MPa"] == 0.03
        assert r["bond_stress_max_MPa"] == 0.07

    def test_stiff_clay_med_plasticity(self):
        r = table_7_bond_stress_cohesive("pressure_stiff_clay_med_plasticity")
        assert r["bond_stress_min_MPa"] == 0.10
        assert r["bond_stress_max_MPa"] == 0.25

    def test_very_stiff_sandy_silt(self):
        r = table_7_bond_stress_cohesive("pressure_very_stiff_sandy_silt_med_plasticity")
        assert r["bond_stress_min_MPa"] == 0.28

    def test_description_returned(self):
        r = table_7_bond_stress_cohesive("gravity_grouted_all")
        assert "gravity" in r["description"].lower()

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown cohesive sub_type"):
            table_7_bond_stress_cohesive("stiff_clay")


class TestTable7BondStressCohesionless:
    """table_7_bond_stress_cohesionless — Table 7, cohesionless soil."""

    def test_gravity_grouted(self):
        r = table_7_bond_stress_cohesionless("gravity_grouted_all")
        assert r["bond_stress_min_MPa"] == 0.07
        assert r["bond_stress_max_MPa"] == 0.14

    def test_pressure_med_coarse_sand_dense(self):
        r = table_7_bond_stress_cohesionless("pressure_med_coarse_sand_gravel_dense")
        assert r["bond_stress_min_MPa"] == 0.25
        assert r["bond_stress_max_MPa"] == 0.97

    def test_pressure_sandy_gravel_dense(self):
        r = table_7_bond_stress_cohesionless("pressure_sandy_gravel_dense")
        assert r["bond_stress_max_MPa"] == 1.38

    def test_pressure_higher_than_gravity(self):
        rg = table_7_bond_stress_cohesionless("gravity_grouted_all")
        rp = table_7_bond_stress_cohesionless("pressure_med_coarse_sand_gravel_dense")
        assert rp["bond_stress_max_MPa"] > rg["bond_stress_max_MPa"]

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown cohesionless sub_type"):
            table_7_bond_stress_cohesionless("gravel")


class TestTable8RockAnchorTransferLoad:
    """table_8_rock_anchor_transfer_load — Table 8."""

    def test_granite_basalt(self):
        r = table_8_rock_anchor_transfer_load("granite_basalt")
        assert r["ultimate_transfer_load_kN_per_m"] == 730

    def test_dolomitic_limestone(self):
        r = table_8_rock_anchor_transfer_load("dolomitic_limestone")
        assert r["ultimate_transfer_load_kN_per_m"] == 580

    def test_soft_limestone(self):
        r = table_8_rock_anchor_transfer_load("soft_limestone")
        assert r["ultimate_transfer_load_kN_per_m"] == 440

    def test_sandstone(self):
        r = table_8_rock_anchor_transfer_load("sandstone")
        assert r["ultimate_transfer_load_kN_per_m"] == 440

    def test_slates_hard_shales(self):
        r = table_8_rock_anchor_transfer_load("slates_hard_shales")
        assert r["ultimate_transfer_load_kN_per_m"] == 360

    def test_soft_shales(self):
        r = table_8_rock_anchor_transfer_load("soft_shales")
        assert r["ultimate_transfer_load_kN_per_m"] == 150

    def test_fs_3(self):
        r = table_8_rock_anchor_transfer_load("granite_basalt")
        assert r["factor_of_safety"] == 3.0

    def test_allowable_correct(self):
        r = table_8_rock_anchor_transfer_load("granite_basalt")
        assert r["allowable_load_per_m_kN"] == pytest.approx(730 / 3.0, abs=0.5)

    def test_granite_alias(self):
        r = table_8_rock_anchor_transfer_load("granite")
        assert r["ultimate_transfer_load_kN_per_m"] == 730

    def test_limestone_and_shale_refused(self):
        """Table 8, p. 74: 'limestone' and 'shale' name two rows each (gec-39)."""
        for word in ("limestone", "shale"):
            with pytest.raises(ValueError, match="Unknown rock_type"):
                table_8_rock_anchor_transfer_load(word)

    def test_harder_rock_higher_capacity(self):
        r1 = table_8_rock_anchor_transfer_load("soft_shales")
        r2 = table_8_rock_anchor_transfer_load("granite_basalt")
        assert r2["ultimate_transfer_load_kN_per_m"] > r1["ultimate_transfer_load_kN_per_m"]

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown rock_type"):
            table_8_rock_anchor_transfer_load("quartzite")


class TestTable20CorrosionProtection:
    """table_20_corrosion_protection — Table 20."""

    def test_class_i_name(self):
        r = table_20_corrosion_protection("class_i")
        assert r["name"] == "Encapsulated Tendon"

    def test_class_ii_name(self):
        r = table_20_corrosion_protection("class_ii")
        assert r["name"] == "Grout Protected Tendon"

    def test_class_i_has_bond_length(self):
        r = table_20_corrosion_protection("class_i")
        assert len(r["bond_length"]) > 0

    def test_class_ii_bond_length_grout(self):
        r = table_20_corrosion_protection("class_ii")
        assert any("grout" in item.lower() for item in r["bond_length"])

    def test_alias_i(self):
        r = table_20_corrosion_protection("i")
        assert r["class"] == "class_i"

    def test_alias_ii(self):
        r = table_20_corrosion_protection("2")
        assert r["class"] == "class_ii"

    def test_encapsulated_alias(self):
        r = table_20_corrosion_protection("encapsulated")
        assert r["class"] == "class_i"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown protection_class"):
            table_20_corrosion_protection("class_iii")

    def test_words_as_printed(self):
        """Table 20, p. 131 (PDF page 152), 'modified after PTI, 1996': the
        anchorage is '1. Trumpet' for both classes and the Class I bond
        length 'Grout-filled encapsulation or / Fusion-bonded epoxy'. The
        code said 'with watertight weld' and 'Corrugated HDPE or
        polypropylene', which the table does not print (gec-39)."""
        one = table_20_corrosion_protection("class_i")
        two = table_20_corrosion_protection("class_ii")
        assert one["anchorage"] == ["Trumpet", "Cover if exposed"]
        assert two["anchorage"] == ["Trumpet", "Cover if exposed"]
        assert one["bond_length"] == ["Grout-filled encapsulation or",
                                      "Fusion-bonded epoxy"]
        assert two["bond_length"] == ["Grout"]
        assert "modified after PTI, 1996" in one["source"]
