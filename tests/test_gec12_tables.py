"""Tests for GEC-12 table lookup functions."""

import pytest

from geotech_references.gec_12.tables import (
    table_7_1_resistance_factor_static,
    table_7_2_resistance_factor_field,
    table_7_3_static_analysis_methods,
    table_7_9_beta_nt_coefficients,
    table_7_10_brown_method_factors,
    table_7_11_eslami_fellenius_cs,
    table_7_16_soil_setup_factor,
    table_7_8_api_design_parameters,
)


# ============================================================================
# Table 7-1: Resistance Factors for Static Analysis
# ============================================================================

class TestTable71:
    """Tests for table_7_1_resistance_factor_static()."""

    def test_nordlund_compression(self):
        """Nordlund compression phi_stat = 0.45."""
        assert table_7_1_resistance_factor_static("nordlund", "compression") == 0.45

    def test_alpha_method_compression(self):
        """Alpha method compression phi_stat = 0.35."""
        assert table_7_1_resistance_factor_static("alpha_method", "compression") == 0.35

    def test_schmertmann_compression(self):
        """Schmertmann compression phi_stat = 0.50."""
        assert table_7_1_resistance_factor_static("schmertmann_1975", "compression") == 0.50

    def test_nordlund_tension(self):
        """Nordlund tension phi_stat = 0.35."""
        assert table_7_1_resistance_factor_static("nordlund", "tension") == 0.35

    def test_beta_method_tension(self):
        """Beta method 1991 tension phi_stat = 0.20."""
        assert table_7_1_resistance_factor_static("beta_method_1991", "tension") == 0.20

    def test_block_failure_cohesive(self):
        """Block failure cohesive phi_stat = 0.60."""
        assert table_7_1_resistance_factor_static("cohesive", "block_failure") == 0.60

    def test_group_uplift(self):
        """Group uplift phi_stat = 0.50."""
        assert table_7_1_resistance_factor_static("sand_and_clay", "group_uplift") == 0.50

    def test_lateral_all_soils(self):
        """Lateral all soils phi_stat = 1.0."""
        assert table_7_1_resistance_factor_static("all_soils_and_rock", "lateral") == 1.0

    def test_none_for_no_aashto_factor(self):
        """Methods without AASHTO factor return None."""
        assert table_7_1_resistance_factor_static("beta_method_1991", "compression") is None

    def test_case_insensitive(self):
        """Method names are case-insensitive."""
        phi = table_7_1_resistance_factor_static("NORDLUND", "COMPRESSION")
        assert phi == 0.45

    def test_unknown_method_raises(self):
        """Unknown method raises ValueError."""
        with pytest.raises(ValueError):
            table_7_1_resistance_factor_static("unknown_method", "compression")

    def test_unknown_condition_raises(self):
        """Unknown condition raises ValueError."""
        with pytest.raises(ValueError):
            table_7_1_resistance_factor_static("nordlund", "unknown_condition")


# ============================================================================
# Table 7-2: Resistance Factors for Field Methods
# ============================================================================

class TestTable72:
    """Tests for table_7_2_resistance_factor_field()."""

    def test_wave_equation(self):
        """Wave equation analysis phi_dyn = 0.50."""
        assert table_7_2_resistance_factor_field("wave equation") == 0.50

    def test_gates_formula(self):
        """FHWA Modified Gates phi_dyn = 0.40."""
        assert table_7_2_resistance_factor_field("gates") == 0.40

    def test_engineering_news(self):
        """Engineering News phi_dyn = 0.10."""
        assert table_7_2_resistance_factor_field("engineering news") == 0.10

    # GEC-12 Vol I Table 7-2, p. 226 (PDF page 272), every printed row.
    @pytest.mark.parametrize("key, phi", [
        ("static_load_test_and_dynamic_testing", 0.80),
        ("static_load_test_without_dynamic_testing", 0.75),
        ("dynamic_testing_100_percent", 0.75),
        ("dynamic_testing_2_percent", 0.65),
        ("wave_equation", 0.50),
        ("fhwa_modified_gates", 0.40),
        ("engineering_news", 0.10),
        ("tension_static_load_test", 0.60),
        ("tension_dynamic_testing_signal_matching", 0.50),
    ])
    def test_every_printed_row(self, key, phi):
        assert table_7_2_resistance_factor_field(key) == phi

    def test_static_load_test_compression(self):
        """Static load test and dynamic testing: phi_dyn = 0.80."""
        phi = table_7_2_resistance_factor_field(
            "static load test and dynamic testing")
        assert phi == 0.80

    def test_static_load_test_without_dynamic_testing(self):
        """A static load test alone is 0.75, not the combined row's 0.80."""
        phi = table_7_2_resistance_factor_field(
            "static load test without dynamic testing")
        assert phi == 0.75

    def test_dynamic_testing_100_percent(self):
        """Dynamic testing 100% phi_dyn = 0.75."""
        phi = table_7_2_resistance_factor_field("dynamic testing on 100%")
        assert phi == 0.75

    def test_tension_static(self):
        """Static load test (tension) phi_dyn = 0.60."""
        assert table_7_2_resistance_factor_field(
            "static load test (tension)") == 0.60

    @pytest.mark.parametrize("ambiguous", [
        "static load test", "dynamic testing", "dynamic", "signal matching",
        "static", "load test", "testing"])
    def test_a_key_that_fits_several_rows_is_refused(self, ambiguous):
        """'static load test' fits three rows (0.80, 0.75, 0.60) and 'dynamic
        testing' four; each returned the first row's 0.80 before."""
        with pytest.raises(ValueError, match="does not name one row"):
            table_7_2_resistance_factor_field(ambiguous)

    def test_no_match_raises(self):
        """No matching method raises ValueError."""
        with pytest.raises(ValueError):
            table_7_2_resistance_factor_field("nonexistent_method")


# ============================================================================
# Table 7-3: Summary of Static Analysis Methods
# ============================================================================

class TestTable73:
    """Tests for table_7_3_static_analysis_methods()."""

    def test_all_methods(self):
        """Returns all 10 methods when no filter."""
        methods = table_7_3_static_analysis_methods()
        assert len(methods) == 10

    def test_cohesionless_filter(self):
        """Filtering by 'cohesionless' returns correct methods."""
        methods = table_7_3_static_analysis_methods("cohesionless")
        assert len(methods) >= 2
        assert all(m["soil_type"] == "cohesionless" for m in methods)

    def test_cohesive_filter(self):
        """Filtering by 'cohesive' returns correct methods."""
        methods = table_7_3_static_analysis_methods("cohesive")
        assert len(methods) >= 3
        assert all(m["soil_type"] == "cohesive" for m in methods)

    def test_unknown_filter_is_refused(self):
        """An unknown soil type raised nothing and returned [] before."""
        for bad in ("sand", "clay", "zzz"):
            with pytest.raises(ValueError, match="cohesionless, cohesive, mixed"):
                table_7_3_static_analysis_methods(bad)

    def test_mixed_filter(self):
        methods = table_7_3_static_analysis_methods("mixed")
        assert len(methods) == 5
        assert all(m["soil_type"] == "mixed" for m in methods)

    def test_method_has_required_keys(self):
        """Each method dict has all required keys."""
        methods = table_7_3_static_analysis_methods()
        for m in methods:
            assert "method" in m
            assert "soil_type" in m
            assert "input" in m
            assert "in_gec12" in m
            assert "in_aashto" in m
            assert "phi_stat" in m

    def test_nordlund_in_gec12(self):
        """Nordlund method is in GEC-12."""
        methods = table_7_3_static_analysis_methods("cohesionless")
        nordlund = [m for m in methods if "Nordlund" in m["method"]]
        assert len(nordlund) == 1
        assert nordlund[0]["in_gec12"] is True


# ============================================================================
# Table 7-8: API Design Parameters
# ============================================================================

class TestTable78:
    """Tests for table_7_8_api_design_parameters()."""

    def test_delta_15(self):
        """delta=15 returns correct values."""
        result = table_7_8_api_design_parameters(15)
        assert result["fs_limit_ksf"] == 1.0
        assert result["Nq"] == 8
        assert result["qp_limit_ksf"] == 40

    def test_delta_30(self):
        """delta=30 returns correct values."""
        result = table_7_8_api_design_parameters(30)
        assert result["fs_limit_ksf"] == 2.0
        assert result["Nq"] == 40
        assert result["qp_limit_ksf"] == 200

    def test_delta_35(self):
        """delta=35 returns correct values."""
        result = table_7_8_api_design_parameters(35)
        assert result["Nq"] == 50

    def test_interpolation(self):
        """Intermediate delta interpolates between table entries."""
        result = table_7_8_api_design_parameters(22.5)
        assert 1.4 < result["fs_limit_ksf"] < 1.7

    def test_out_of_range_raises(self):
        """delta outside 15-35 raises ValueError."""
        with pytest.raises(ValueError):
            table_7_8_api_design_parameters(10)
        with pytest.raises(ValueError):
            table_7_8_api_design_parameters(40)


# ============================================================================
# Table 7-9: Beta and Nt Coefficients
# ============================================================================

class TestTable79:
    """Tests for table_7_9_beta_nt_coefficients()."""

    def test_clay(self):
        """Clay returns correct beta range."""
        result = table_7_9_beta_nt_coefficients("clay")
        assert result["beta_min"] == 0.15
        assert result["beta_max"] == 0.35

    def test_sand(self):
        """Sand returns correct Nt range."""
        result = table_7_9_beta_nt_coefficients("sand")
        assert result["nt_min"] == 30
        assert result["nt_max"] == 150

    def test_gravel(self):
        """Gravel returns correct phi range."""
        result = table_7_9_beta_nt_coefficients("gravel")
        assert result["phi_min"] == 35
        assert result["phi_max"] == 45

    def test_case_insensitive(self):
        """Soil type is case-insensitive."""
        result = table_7_9_beta_nt_coefficients("SAND")
        assert result["beta_min"] == 0.30

    def test_unknown_soil_raises(self):
        """Unknown soil type raises ValueError."""
        with pytest.raises(ValueError):
            table_7_9_beta_nt_coefficients("peat")


# ============================================================================
# Table 7-10: Brown's Method Factors
# ============================================================================

class TestTable710:
    """Tests for table_7_10_brown_method_factors()."""

    def test_compression_impact_clay_to_sand(self):
        """Compression, impact, clay_to_sand."""
        result = table_7_10_brown_method_factors("compression", "impact", "clay_to_sand")
        assert result["Fvs"] == 1.0
        assert result["Ab_ksf"] == 0.555
        assert result["Bb_ksf_per_bpf"] == 0.040

    def test_tension_impact_rock(self):
        """Tension, impact, rock."""
        result = table_7_10_brown_method_factors("tension", "impact", "rock")
        assert result["Bb_ksf_per_bpf"] == 0.0

    def test_vibratory_fvs(self):
        """Vibratory installation has Fvs = 0.68; GEC-12 Vol I Table 7-10,
        p. 260 (PDF page 306) types the vibratory rows under "Tension"."""
        result = table_7_10_brown_method_factors("tension", "vibratory", "clay_to_sand")
        assert result["Fvs"] == 0.68
        assert (result["Ab_ksf"], result["Bb_ksf_per_bpf"]) == (0.522, 0.0376)
        result = table_7_10_brown_method_factors("tension", "vibratory", "rock")
        assert (result["Fvs"], result["Ab_ksf"], result["Bb_ksf_per_bpf"]) == (0.68, 2.71, 0.0)

    def test_no_match_raises(self):
        """The table prints no vibratory compression row (p. 260)."""
        with pytest.raises(ValueError, match="vibratory rows under tension"):
            table_7_10_brown_method_factors("compression", "vibratory", "clay_to_sand")

    def test_printed_bb_replaced_by_zero_with_note(self):
        """GEC-12 Vol I Table 7-10, p. 260 (PDF page 306): Bb is printed
        equal to Ab for compression in gravelly sand to boulders (0.888) and
        rock (2.89); the tension rows print 0.0. By the lead's ruling
        (RULINGS row 7, finding gec-06) 0.0 is returned with a print_note
        naming the printed value; Ab is as printed."""
        r = table_7_10_brown_method_factors(soil_type="gravelly_sand_to_boulders")
        assert (r["Ab_ksf"], r["Bb_ksf_per_bpf"]) == (0.888, 0.0)
        assert r["Bb_printed_ksf_per_bpf"] == 0.888
        assert "0.888" in r["print_note"] and "p. 260" in r["print_note"]
        r = table_7_10_brown_method_factors(soil_type="rock")
        assert (r["Ab_ksf"], r["Bb_ksf_per_bpf"]) == (2.89, 0.0)
        assert r["Bb_printed_ksf_per_bpf"] == 2.89
        assert "2.89" in r["print_note"]
        r = table_7_10_brown_method_factors("tension", "impact",
                                            "gravelly_sand_to_boulders")
        assert (r["Ab_ksf"], r["Bb_ksf_per_bpf"]) == (0.835, 0.0)
        assert "print_note" not in r
        r = table_7_10_brown_method_factors("compression", "impact", "clay_to_sand")
        assert "print_note" not in r
        first = table_7_10_brown_method_factors.__doc__.split("\n\n")[0]
        assert "prints Bb equal to Ab" in first
        assert 'printed under "Tension"' in first


# ============================================================================
# Table 7-11: Eslami-Fellenius Cs
# ============================================================================

class TestTable711:
    """Tests for table_7_11_eslami_fellenius_cs()."""

    def test_clay(self):
        """Clay Cs = 5.0."""
        assert table_7_11_eslami_fellenius_cs("clay") == 5.0

    def test_sand(self):
        """Sand Cs = 0.4."""
        assert table_7_11_eslami_fellenius_cs("sand") == 0.4

    # GEC-12 Vol I Table 7-11, p. 261 (PDF page 307): Cs in percent.
    @pytest.mark.parametrize("soil, cs", [
        ("soft_sensitive_soil", 8.0), ("clay", 5.0),
        ("silty_clay_stiff_clay_silt", 2.5), ("sandy_silt_silt", 1.5),
        ("fine_sand_silty_sand", 1.0), ("sand", 0.4),
        ("silty clay", 2.5), ("stiff clay", 2.5), ("sandy silt", 1.5),
        ("fine sand", 1.0), ("silty sand", 1.0),
    ])
    def test_printed_rows_and_listed_names(self, soil, cs):
        assert table_7_11_eslami_fellenius_cs(soil) == cs

    def test_partial_match(self):
        """A soil named in one printed row is that row."""
        cs = table_7_11_eslami_fellenius_cs("fine_sand")
        assert cs == 1.0  # fine_sand_silty_sand

    def test_silt_alone_is_refused(self):
        """'silt' is printed in two rows (2.5 and 1.5); it returned 2.5."""
        with pytest.raises(ValueError, match="does not name one row"):
            table_7_11_eslami_fellenius_cs("silt")

    def test_unprinted_soil_is_refused(self):
        """'sandy gravel' returned the Sand row's 0.4 before."""
        with pytest.raises(ValueError):
            table_7_11_eslami_fellenius_cs("sandy gravel")

    def test_unknown_soil_raises(self):
        """Unknown soil type raises ValueError."""
        with pytest.raises(ValueError):
            table_7_11_eslami_fellenius_cs("peat")


# ============================================================================
# Table 7-16: Soil Setup Factors
# ============================================================================

class TestTable716:
    """Tests for table_7_16_soil_setup_factor()."""

    def test_clay(self):
        """Clay setup factor recommended = 2.0."""
        result = table_7_16_soil_setup_factor("clay")
        assert result["recommended"] == 2.0
        assert result["range_min"] == 1.2
        assert result["range_max"] == 5.5

    def test_sand(self):
        """Sand setup factor recommended = 1.0."""
        result = table_7_16_soil_setup_factor("sand")
        assert result["recommended"] == 1.0

    def test_silt(self):
        """Silt setup factor recommended = 1.5."""
        result = table_7_16_soil_setup_factor("silt")
        assert result["recommended"] == 1.5

    def test_case_insensitive(self):
        """Soil type is case-insensitive."""
        result = table_7_16_soil_setup_factor("CLAY")
        assert result["recommended"] == 2.0

    # GEC-12 Vol I Table 7-16, p. 299 (PDF page 345), every printed row:
    # (key, row name, range min, range max, recommended, sites, percent)
    @pytest.mark.parametrize("key, name, lo, hi, rec, sites, pct", [
        ("clay", "Clay", 1.2, 5.5, 2.0, 7, 15),
        ("silt_clay", "Silt - Clay", 1.0, 2.0, 1.0, 10, 22),
        ("silt", "Silt", 1.5, 5.0, 1.5, 2, 4),
        ("sand_clay", "Sand - Clay", 1.0, 6.0, 1.5, 13, 28),
        ("sand_silt", "Sand - Silt", 1.2, 2.0, 1.2, 8, 18),
        ("fine_sand", "Fine Sand", 1.2, 2.0, 1.2, 2, 4),
        ("sand", "Sand", 0.8, 2.0, 1.0, 3, 7),
        ("sand_gravel", "Sand - Gravel", 1.2, 2.0, 1.0, 1, 2),
    ])
    def test_every_printed_row(self, key, name, lo, hi, rec, sites, pct):
        r = table_7_16_soil_setup_factor(key)
        assert r["soil_type"] == name
        assert (r["range_min"], r["range_max"], r["recommended"]) == (lo, hi, rec)
        assert (r["sites"], r["percent_of_database"]) == (sites, pct)
        assert "Confirmation with Local Experience" in r["note"]
        assert "p. 299" in r["reference"]

    @pytest.mark.parametrize("name, row, rec", [
        ("silty clay", "Silt - Clay", 1.0),     # returned Clay's 2.0 before
        ("sandy clay", "Sand - Clay", 1.5),     # returned Clay's 2.0 before
        ("silty sand", "Sand - Silt", 1.2),     # returned Silt's 1.5 before
        ("Silt - Clay", "Silt - Clay", 1.0),
        ("sandy gravel", "Sand - Gravel", 1.0),
    ])
    def test_mixed_soils_reach_their_own_row(self, name, row, rec):
        r = table_7_16_soil_setup_factor(name)
        assert r["soil_type"] == row
        assert r["recommended"] == rec

    def test_partial_match(self):
        """A printed row by its key."""
        result = table_7_16_soil_setup_factor("fine_sand")
        assert result["recommended"] == 1.2

    @pytest.mark.parametrize("bad", ["gravel", "stiff clay", "cla", "san"])
    def test_partial_or_unprinted_name_is_refused(self, bad):
        with pytest.raises(ValueError, match="does not name one row"):
            table_7_16_soil_setup_factor(bad)

    def test_unknown_soil_raises(self):
        """Unknown soil type raises ValueError."""
        with pytest.raises(ValueError):
            table_7_16_soil_setup_factor("organic")
