"""Tests for GEC-7 table lookup functions."""

import pytest

from geotech_references.gec_7.tables import (
    table_4_2a_spt_soil_properties,
    table_4_3a_elastic_properties,
    table_4_3b_elastic_modulus_spt,
    table_4_4a_bond_strength_coarse,
    table_4_4b_bond_strength_fine,
    table_4_5_bond_strength_rock,
    table_4_6_pullout_resistance,
    table_4_9_site_coefficient_fpga,
    table_4_10_site_coefficient_fv,
    table_5_1_factors_of_safety,
    table_5_3_load_factors_permanent,
    table_5_resistance_factors,
    table_5_12_wall_displacement,
)


# ============================================================================
# Table 4.2a: SPT Soil Properties (Cohesionless)
# ============================================================================

class TestTable42a:
    """Tests for table_4_2a_spt_soil_properties()."""

    def test_very_loose(self):
        assert table_4_2a_spt_soil_properties(2)["density"] == "very_loose"

    def test_loose(self):
        assert table_4_2a_spt_soil_properties(5)["density"] == "loose"

    def test_medium(self):
        assert table_4_2a_spt_soil_properties(15)["density"] == "medium"

    def test_dense(self):
        assert table_4_2a_spt_soil_properties(40)["density"] == "dense"

    def test_very_dense(self):
        assert table_4_2a_spt_soil_properties(60)["density"] == "very_dense"

    def test_boundary_at_4(self):
        """N60=4 should be 'loose' (boundary)."""
        assert table_4_2a_spt_soil_properties(4)["density"] == "loose"

    def test_boundary_at_10(self):
        assert table_4_2a_spt_soil_properties(10)["density"] == "medium"

    def test_phi_range_medium(self):
        r = table_4_2a_spt_soil_properties(20)
        assert r["phi_min_deg"] == 35
        assert r["phi_max_deg"] == 40

    def test_open_rows_as_printed(self):
        """GEC-7 Table 4.2a, p. 78 (PDF page 118): very loose prints phi
        "< 30" and very dense "> 45 (3)"; the code had invented 25 and 50
        (gec-22). Note (3) holds sands to 40 and gravelly soils to 45."""
        r = table_4_2a_spt_soil_properties(2)
        assert (r["phi_min_deg"], r["phi_max_deg"]) == (None, 30)
        assert r["phi_printed"] == "< 30"
        r = table_4_2a_spt_soil_properties(60)
        assert (r["phi_min_deg"], r["phi_max_deg"]) == (45, None)
        assert r["phi_printed"] == "> 45 (3)"
        assert "Sands should be selected to have a friction angle <= 40" in r["notes"]
        assert "Gravelly soils" in r["notes"] and "<= 45" in r["notes"]
        r = table_4_2a_spt_soil_properties(35)
        assert (r["phi_min_deg"], r["phi_max_deg"]) == (40, 45)
        assert r["relative_density_pct"] == "60-80"

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            table_4_2a_spt_soil_properties(-1)


# ============================================================================
# Table 4.3a: Elastic Properties
# ============================================================================

class TestTable43a:
    """Tests for table_4_3a_elastic_properties()."""

    def test_clay_soft(self):
        r = table_4_3a_elastic_properties("clay_soft")
        assert r["Es_min_kPa"] == pytest.approx(2394)
        assert r["nu_min"] == 0.4

    def test_sand_loose(self):
        r = table_4_3a_elastic_properties("sand_loose")
        assert r["Es_min_kPa"] == pytest.approx(9576)
        assert r["nu_min"] == 0.20

    def test_gravel_dense(self):
        r = table_4_3a_elastic_properties("gravel_dense")
        assert r["Es_max_kPa"] == pytest.approx(191520)

    def test_partial_match(self):
        """'silt' is a printed row (Silt, 40 - 400 ksf, p. 82)."""
        r = table_4_3a_elastic_properties("silt")
        assert r["description"] == "Silt"
        assert (r["Es_min_kPa"], r["Es_max_kPa"]) == (1915, 19152)

    def test_word_of_several_rows_refused(self):
        """GEC-7 Table 4.3a, p. 82 (PDF page 122): 'clay' returned the soft
        sensitive row and 'sand' the loose fine sand row, the first row
        whose key held the word; both fit several rows and are refused."""
        for word in ("clay", "sand", "fine sand", "gravel"):
            with pytest.raises(ValueError, match="does not name one row"):
                table_4_3a_elastic_properties(word)

    def test_aliases_and_undrained_clay(self):
        """Printed and condition-first names: 'Clay - very stiff' 1,000 -
        2,000 ksf, 0.4 - 0.5 (undrained); 'dense sand' 1,000 - 1,600 ksf."""
        r = table_4_3a_elastic_properties("Clay - very stiff")
        assert (r["Es_min_kPa"], r["Es_max_kPa"]) == (47880, 95760)
        assert r["nu_condition"] == "undrained"
        r = table_4_3a_elastic_properties("dense sand")
        assert (r["Es_min_kPa"], r["Es_max_kPa"]) == (47880, 76608)
        assert (r["nu_min"], r["nu_max"]) == (0.30, 0.40)
        assert "nu_condition" not in r

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_4_3a_elastic_properties("organic_peat")


# ============================================================================
# Table 4.3b: Elastic Modulus from SPT
# ============================================================================

class TestTable43b:
    """Tests for table_4_3b_elastic_modulus_spt()."""

    def test_clean_sand_n20(self):
        """Es = 14 * 20 * 47.88 = 13406.4 kPa."""
        es = table_4_3b_elastic_modulus_spt("clean_fine_to_medium_sand", 20)
        assert es == pytest.approx(14 * 20 * 47.88)

    def test_sandy_gravel_n10(self):
        """Es = 24 * 10 * 47.88 = 11491.2 kPa."""
        es = table_4_3b_elastic_modulus_spt("sandy_gravel", 10)
        assert es == pytest.approx(24 * 10 * 47.88)

    def test_silt_n5(self):
        es = table_4_3b_elastic_modulus_spt("silts_sandy_silts", 5)
        assert es == pytest.approx(8 * 5 * 47.88)

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            table_4_3b_elastic_modulus_spt("coarse_sand", -5)

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError):
            table_4_3b_elastic_modulus_spt("organic_clay", 10)

    def test_sand_alone_refused(self):
        """GEC-7 Table 4.3b, p. 82 (PDF page 122): 'sand' returned the silts
        row, 8 (N1)60 (7,661 kPa at 20, where clean fine to medium sand is
        14 (N1)60, 13,406 kPa); it fits two rows and is refused (gec-17)."""
        with pytest.raises(ValueError, match="does not name one row"):
            table_4_3b_elastic_modulus_spt("sand", 20)

    def test_printed_names(self):
        """Each printed row name: 8, 14, 20, 24 (N1)60 ksf."""
        assert table_4_3b_elastic_modulus_spt(
            "Silts, sandy silts, slightly cohesive mixtures", 1) == pytest.approx(8 * 47.88)
        assert table_4_3b_elastic_modulus_spt(
            "Clean fine to medium sands and slightly silty sands", 1) == pytest.approx(14 * 47.88)
        assert table_4_3b_elastic_modulus_spt(
            "Coarse sands and sands with little gravel", 1) == pytest.approx(20 * 47.88)
        assert table_4_3b_elastic_modulus_spt(
            "Sandy gravel and gravels", 1) == pytest.approx(24 * 47.88)


# ============================================================================
# Table 4.4a: Bond Strength — Coarse-Grained Soils
# ============================================================================

class TestTable44a:
    """Tests for table_4_4a_bond_strength_coarse()."""

    def test_rotary_sand_gravel(self):
        r = table_4_4a_bond_strength_coarse("rotary_drilled", "sand_gravel")
        assert r["min_kPa"] == pytest.approx(15 * 6.895, rel=0.01)
        assert r["max_kPa"] == pytest.approx(26 * 6.895, rel=0.01)

    def test_rotary_silt(self):
        r = table_4_4a_bond_strength_coarse("rotary_drilled", "silt")
        assert r["min_kPa"] == pytest.approx(9 * 6.895, rel=0.01)
        assert r["max_kPa"] == pytest.approx(11 * 6.895, rel=0.01)

    def test_driven_casing_dense_moraine(self):
        r = table_4_4a_bond_strength_coarse("driven_casing", "dense_moraine")
        assert r["min_kPa"] == pytest.approx(55 * 6.895, rel=0.01)

    def test_augered_silty_sand_fill(self):
        r = table_4_4a_bond_strength_coarse("augered", "silty_sand_fill")
        assert r["min_kPa"] == pytest.approx(3 * 6.895, rel=0.01)

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError):
            table_4_4a_bond_strength_coarse("jet_grouted", "sand")

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError):
            table_4_4a_bond_strength_coarse("rotary_drilled", "organic_clay")

    def test_partial_soil_refused(self):
        """GEC-7 Table 4.4a, p. 84 (PDF page 124): rotary drilled 'sand'
        returned Sand/gravel (15 - 26 psi) by a part of the name; it fits
        Sand/gravel and Silty sand and is refused. Driven casing
        'sand/gravel' fits the low and the high overburden rows."""
        with pytest.raises(ValueError, match="does not name one row"):
            table_4_4a_bond_strength_coarse("rotary_drilled", "sand")
        with pytest.raises(ValueError, match="does not name one row"):
            table_4_4a_bond_strength_coarse("driven_casing", "sand/gravel")

    def test_overburden_rows_carry_note(self):
        """Sand/gravel w/high overburden (1): 41 - 62 psi; note (1): high
        overburden is effective overburden pressure greater than 1.5 tsf."""
        r = table_4_4a_bond_strength_coarse("Driven Casing",
                                            "Sand/gravel w/high overburden")
        assert r["min_kPa"] == pytest.approx(41 * 6.895, rel=0.01)
        assert r["max_kPa"] == pytest.approx(62 * 6.895, rel=0.01)
        assert "1.5 tsf" in r["note"]


# ============================================================================
# Table 4.4b: Bond Strength — Fine-Grained Soils
# ============================================================================

class TestTable44b:
    """Tests for table_4_4b_bond_strength_fine()."""

    def test_rotary_silty_clay(self):
        r = table_4_4b_bond_strength_fine("rotary_drilled", "silty_clay")
        assert r["min_kPa"] == pytest.approx(5 * 6.895, rel=0.01)
        assert r["max_kPa"] == pytest.approx(7 * 6.895, rel=0.01)

    def test_augered_loess(self):
        r = table_4_4b_bond_strength_fine("augered", "loess")
        assert r["min_kPa"] == pytest.approx(4 * 6.895, rel=0.01)

    def test_augered_stiff_clay(self):
        r = table_4_4b_bond_strength_fine("augered", "stiff_clay")
        assert r["min_kPa"] == pytest.approx(6 * 6.895, rel=0.01)
        assert r["max_kPa"] == pytest.approx(9 * 6.895, rel=0.01)

    def test_driven_casing_clayey_silt(self):
        r = table_4_4b_bond_strength_fine("driven_casing", "clayey_silt")
        assert r["min_kPa"] == pytest.approx(13 * 6.895, rel=0.01)

    def test_unknown_soil_raises(self):
        with pytest.raises(ValueError):
            table_4_4b_bond_strength_fine("augered", "peat")

    def test_partial_soil_refused(self):
        """GEC-7 Table 4.4b, p. 85 (PDF page 125): augered 'clay' returned
        Soft clay (3 - 4 psi); it fits soft, stiff and calcareous sandy clay
        and is refused."""
        with pytest.raises(ValueError, match="does not name one row"):
            table_4_4b_bond_strength_fine("augered", "clay")
        r = table_4_4b_bond_strength_fine("augered", "Calcareous sandy clay")
        assert r["max_kPa"] == pytest.approx(20 * 6.895, rel=0.01)


# ============================================================================
# Table 4.5: Bond Strength — Rock
# ============================================================================

class TestTable45:
    """Tests for table_4_5_bond_strength_rock()."""

    def test_basalt(self):
        r = table_4_5_bond_strength_rock("basalt")
        assert r["min_kPa"] == pytest.approx(73 * 6.895, rel=0.01)
        assert r["max_kPa"] == pytest.approx(87 * 6.895, rel=0.01)

    def test_chalk(self):
        r = table_4_5_bond_strength_rock("chalk")
        assert r["min_kPa"] == pytest.approx(73 * 6.895, rel=0.01)

    def test_fissured_dolomite(self):
        r = table_4_5_bond_strength_rock("fissured_dolomite")
        assert r["max_kPa"] == pytest.approx(145 * 6.895, rel=0.01)

    def test_weathered_shale(self):
        r = table_4_5_bond_strength_rock("weathered_shale")
        assert r["min_kPa"] == pytest.approx(15 * 6.895, rel=0.01)

    def test_partial_match_sandstone(self):
        """GEC-7 Table 4.5, p. 85 (PDF page 125) prints Weathered sandstone
        (29 - 44 psi) only; 'sandstone', which returned it, is refused, as
        are 'shale' (weathered shale or slate/hard shale) and 'dolomite'."""
        for word in ("sandstone", "shale", "dolomite"):
            with pytest.raises(ValueError, match="does not name one row"):
                table_4_5_bond_strength_rock(word)
        r = table_4_5_bond_strength_rock("Slate/Hard shale")
        assert (r["rock_type"], r["min_kPa"]) == ("slate_hard_shale", round(44 * 6.895, 1))
        assert table_4_5_bond_strength_rock("limestone")["rock_type"] == "marl_limestone"

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_4_5_bond_strength_rock("concrete")


# ============================================================================
# Table 4.6: Pullout Resistance
# ============================================================================

class TestTable46:
    """Tests for table_4_6_pullout_resistance()."""

    def test_sand_gravel_medium_dense(self):
        r = table_4_6_pullout_resistance("sand_and_gravel", "medium_dense")
        assert r["qu_kN_per_m"] == pytest.approx(15 * 14.594, rel=0.01)

    def test_sand_loose(self):
        r = table_4_6_pullout_resistance("sand", "loose")
        assert r["qu_kN_per_m"] == pytest.approx(7 * 14.594, rel=0.01)

    def test_silt_clay_stiff(self):
        r = table_4_6_pullout_resistance("silt_clay_low_pi", "stiff")
        assert r["qu_kN_per_m"] == pytest.approx(2 * 14.594, rel=0.01)

    def test_n60_range(self):
        r = table_4_6_pullout_resistance("sand_and_gravel", "dense")
        assert r["n60_min"] == 31
        assert r["n60_max"] == 50

    def test_unknown_combination_raises(self):
        with pytest.raises(ValueError):
            table_4_6_pullout_resistance("sand", "very_soft")

    def test_partial_soil_refused(self):
        """GEC-7 Table 4.6, p. 86 (PDF page 126): 'silt' with 'loose'
        returned Sand and Silt by a part of the name; refused. The result
        says the SPT range is (N1)60 and gives note (1)."""
        with pytest.raises(ValueError, match="does not name one row"):
            table_4_6_pullout_resistance("silt", "loose")
        r = table_4_6_pullout_resistance("Sand and Silt", "Medium dense")
        assert r["qu_kN_per_m"] == pytest.approx(7 * 14.594, rel=0.01)
        assert "(N1)60" in r["note"] and "gravity-grouted" in r["note"]


# ============================================================================
# Table 4.9: Site Coefficient F_PGA
# ============================================================================

class TestTable49:
    """Tests for table_4_9_site_coefficient_fpga(). Values: GEC-7 Table 4.9,
    p. 94 (PDF page 134), under the PGA columns 0.1 to 0.5 of GEC-12 Vol I
    Table 7-27, p. 380 (PDF page 426), which prints the same values (lead's
    ruling, RULINGS row 10, finding gec-29)."""

    def test_site_a(self):
        assert table_4_9_site_coefficient_fpga("A", 0.5)["F_pga"] == 0.8

    def test_site_b(self):
        assert table_4_9_site_coefficient_fpga("B", 0.5)["F_pga"] == 1.0

    def test_site_d_low_pga(self):
        """PGA < 0.1 column: 1.6; at 0.25 the value is between the 0.2 and
        0.3 columns, 1.3 (it returned 1.6, GEC-7's first column)."""
        assert table_4_9_site_coefficient_fpga("D", 0.1)["F_pga"] == 1.6
        assert table_4_9_site_coefficient_fpga("D", 0.05)["F_pga"] == 1.6
        assert table_4_9_site_coefficient_fpga("D", 0.25)["F_pga"] == pytest.approx(1.3)

    def test_site_d_high_pga(self):
        """PGA > 0.5 column: 1.0."""
        assert table_4_9_site_coefficient_fpga("D", 0.5)["F_pga"] == 1.0
        assert table_4_9_site_coefficient_fpga("D", 1.25)["F_pga"] == 1.0

    def test_review_point(self):
        """Site class D at PGA 0.30: 1.2 (was 1.56)."""
        r = table_4_9_site_coefficient_fpga("D", 0.30)
        assert r["F_pga"] == pytest.approx(1.2)
        assert "PGA <= 0.25" in r["print_note"] and "Table 7-27" in r["print_note"]

    def test_interpolation(self):
        """Straight line between columns (GEC-12 p. 379): D at PGA 0.15
        is halfway between 1.6 and 1.4; E at 0.35 between 1.2 and 0.9."""
        assert table_4_9_site_coefficient_fpga("D", 0.15)["F_pga"] == pytest.approx(1.5)
        assert table_4_9_site_coefficient_fpga("E", 0.35)["F_pga"] == pytest.approx(1.05)

    def test_site_e(self):
        assert table_4_9_site_coefficient_fpga("E", 0.1)["F_pga"] == 2.5
        assert table_4_9_site_coefficient_fpga("C", 0.3)["F_pga"] == 1.1

    def test_unknown_class_raises(self):
        """Site class F: note (1), a site-specific analysis."""
        with pytest.raises(ValueError, match="site-specific"):
            table_4_9_site_coefficient_fpga("F", 0.5)
        with pytest.raises(ValueError):
            table_4_9_site_coefficient_fpga("G", 0.5)


# ============================================================================
# Table 4.10: Site Coefficient F_v
# ============================================================================

class TestTable410:
    """Tests for table_4_10_site_coefficient_fv()."""

    def test_site_c_low_s1(self):
        assert table_4_10_site_coefficient_fv("C", 0.1) == 1.7

    def test_site_d_high_s1(self):
        assert table_4_10_site_coefficient_fv("D", 0.5) == 1.5

    def test_site_e_low_s1(self):
        assert table_4_10_site_coefficient_fv("E", 0.1) == 3.5

    def test_interpolation(self):
        fv = table_4_10_site_coefficient_fv("C", 0.25)
        assert 1.5 < fv < 1.7

    def test_unknown_class_raises(self):
        with pytest.raises(ValueError):
            table_4_10_site_coefficient_fv("F", 0.3)


# ============================================================================
# Table 5.1: Factors of Safety (ASD)
# ============================================================================

class TestTable51:
    """Tests for table_5_1_factors_of_safety()."""

    def test_overall_stability(self):
        r = table_5_1_factors_of_safety("overall_stability")
        assert r["fs_static"] == 1.5
        assert r["fs_seismic"] == 1.1

    def test_pullout_resistance(self):
        r = table_5_1_factors_of_safety("pullout_resistance")
        assert r["fs_static"] == 2.0
        assert r["fs_seismic"] == 1.5

    def test_lateral_sliding(self):
        r = table_5_1_factors_of_safety("lateral_sliding")
        assert r["fs_static"] == 1.5
        assert r["fs_seismic"] == 1.1

    def test_tendon_grade_60_75(self):
        r = table_5_1_factors_of_safety("tendon_tensile_grade_60_75")
        assert r["fs_static"] == 1.8
        assert r["fs_seismic"] == 1.35

    def test_tendon_grade_95_150(self):
        r = table_5_1_factors_of_safety("tendon_tensile_grade_95_150")
        assert r["fs_static"] == 2.0

    def test_facing_punching_shear(self):
        r = table_5_1_factors_of_safety("facing_punching_shear")
        assert r["fs_static"] == 1.5

    def test_headed_stud_a307(self):
        r = table_5_1_factors_of_safety("headed_stud_a307")
        assert r["fs_static"] == 2.0
        assert r["fs_seismic"] == 1.5

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_5_1_factors_of_safety("nonexistent")

    def test_short_term_range_and_basal_heave_notes(self):
        """GEC-7 Table 5.1, p. 108 (PDF page 148): short-term excavation
        prints 1.25-1.33 (3); basal heave 2.0 (4), 2.5 (5) static and 2.3 (5)
        seismic, note (5) being long-term. The short-term row had seismic
        2.3 (gec-41)."""
        r = table_5_1_factors_of_safety("short_term_excavation")
        assert (r["fs_static"], r["fs_static_max"], r["fs_seismic"]) == (1.25, 1.33, None)
        assert "2 days" in r["notes"]
        r = table_5_1_factors_of_safety("basal_heave_short_term")
        assert (r["fs_static"], r["fs_seismic"]) == (2.0, None)
        assert "No seismic value is printed for short-term" in r["print_note"]
        r = table_5_1_factors_of_safety("basal_heave_long_term")
        assert (r["fs_static"], r["fs_seismic"]) == (2.5, 2.3)
        assert "1.35" in table_5_1_factors_of_safety("overall")["notes"]

    def test_partial_names_refused(self):
        """'basal heave' returned the short-term row (2.0) and 'tendon' the
        Grades 60 and 75 row; each fits two rows and is refused."""
        for word in ("basal heave", "tendon", "headed stud", "facing"):
            with pytest.raises(ValueError, match="does not name one row"):
                table_5_1_factors_of_safety(word)


# ============================================================================
# Table 5.3: Load Factors for Permanent Loads
# ============================================================================

class TestTable53:
    """Tests for table_5_3_load_factors_permanent()."""

    def test_dc_dead_loads(self):
        r = table_5_3_load_factors_permanent("dc_dead_loads")
        assert r["max_factor"] == 1.25
        assert r["min_factor"] == 0.90

    def test_eh_active(self):
        r = table_5_3_load_factors_permanent("eh_active")
        assert r["max_factor"] == 1.50

    def test_ev_retaining_walls(self):
        r = table_5_3_load_factors_permanent("ev_retaining_walls")
        assert r["max_factor"] == 1.35

    def test_es_earth_surcharge(self):
        r = table_5_3_load_factors_permanent("es_earth_surcharge")
        assert r["max_factor"] == 1.50
        assert r["min_factor"] == 0.75

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_5_3_load_factors_permanent("nonexistent")

    def test_partial_names_refused(self):
        """GEC-7 Table 5.3, p. 113 (PDF page 153): 'eh' and 'ev' each fit two
        rows and are refused; 'EV: Vertical earth pressure (overall
        stability)' prints 1.00 and N/A."""
        for word in ("eh", "ev"):
            with pytest.raises(ValueError, match="does not name one row"):
                table_5_3_load_factors_permanent(word)
        r = table_5_3_load_factors_permanent("ev overall")
        assert (r["max_factor"], r["min_factor"]) == (1.00, None)


# ============================================================================
# Tables 5.4-5.11: Resistance Factors
# ============================================================================

class TestResistanceFactors:
    """Tests for table_5_resistance_factors()."""

    def test_overall_stability(self):
        r = table_5_resistance_factors("overall_stability")
        assert r["static"] == 0.65
        assert r["seismic"] == 0.90

    def test_pullout(self):
        r = table_5_resistance_factors("pullout")
        assert r["static"] == 0.65
        assert r["seismic"] == 0.65

    def test_lateral_sliding(self):
        r = table_5_resistance_factors("lateral_sliding")
        assert r["static"] == 1.00
        assert r["seismic"] == 0.90

    def test_tendon_grade_60_75(self):
        r = table_5_resistance_factors("tendon_grade_60_75")
        assert r["static"] == 0.75

    def test_tendon_grade_95_150(self):
        r = table_5_resistance_factors("tendon_grade_95_150")
        assert r["static"] == 0.65

    def test_facing_flexure(self):
        r = table_5_resistance_factors("facing_flexure")
        assert r["static"] == 0.90

    def test_facing_punching_shear(self):
        r = table_5_resistance_factors("facing_punching_shear")
        assert r["static"] == 0.90

    def test_headed_stud_a307(self):
        r = table_5_resistance_factors("headed_stud_a307")
        assert r["static"] == 0.70
        assert r["seismic"] == 0.65

    def test_headed_stud_a325(self):
        r = table_5_resistance_factors("headed_stud_a325")
        assert r["static"] == 0.80
        assert r["seismic"] == 0.75

    def test_basal_heave_short_term(self):
        r = table_5_resistance_factors("basal_heave_short_term")
        assert r["static"] == 0.65

    def test_basal_heave_long_term(self):
        r = table_5_resistance_factors("basal_heave_long_term")
        assert r["static"] == 0.50

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_5_resistance_factors("nonexistent")

    def test_partial_names_refused(self):
        """'basal heave' returned the short-term 0.65 (long-term 0.50,
        Table 5.5, p. 125); 'tendon', 'headed stud', 'facing' fit two rows."""
        for word in ("basal heave", "tendon", "headed stud", "facing"):
            with pytest.raises(ValueError, match="does not name one row"):
                table_5_resistance_factors(word)
        assert table_5_resistance_factors("A325")["static"] == 0.80


# ============================================================================
# Table 5.12: Wall Displacement Parameters
# ============================================================================

class TestTable512:
    """Tests for table_5_12_wall_displacement()."""

    def test_weathered_rock(self):
        r = table_5_12_wall_displacement("weathered_rock_stiff_soil")
        assert r["delta_h_over_H"] == pytest.approx(1.0 / 1000)
        assert r["C"] == 0.8

    def test_sandy_soil(self):
        r = table_5_12_wall_displacement("sandy_soil")
        assert r["delta_h_over_H"] == pytest.approx(1.0 / 500)
        assert r["C"] == 1.25

    def test_fine_grained(self):
        r = table_5_12_wall_displacement("fine_grained_soil")
        assert r["delta_h_over_H"] == pytest.approx(1.0 / 333)
        assert r["C"] == 1.5

    def test_partial_match(self):
        """'sandy' is a listed name of the Sandy Soil column (p. 141)."""
        r = table_5_12_wall_displacement("sandy")
        assert r["C"] == 1.25

    def test_soil_alone_refused(self):
        """GEC-7 Table 5.12, p. 141 (PDF page 181): 'soil' returned the
        weathered rock and stiff soil column (1/1000, 0.8); refused."""
        with pytest.raises(ValueError, match="does not name one row"):
            table_5_12_wall_displacement("soil")
        r = table_5_12_wall_displacement("Weathered Rock and Stiff Soil")
        assert r["C"] == 0.8

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_5_12_wall_displacement("nonexistent")
