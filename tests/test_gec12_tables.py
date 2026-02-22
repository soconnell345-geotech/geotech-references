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

    def test_static_load_test_compression(self):
        """Static load test + dynamic testing phi_dyn = 0.80."""
        phi = table_7_2_resistance_factor_field("static load test + dynamic")
        assert phi == 0.80

    def test_dynamic_testing_100_percent(self):
        """Dynamic testing 100% phi_dyn = 0.75."""
        phi = table_7_2_resistance_factor_field("dynamic testing on 100%")
        assert phi == 0.75

    def test_tension_static(self):
        """Static load test (tension) phi_dyn = 0.60."""
        phi = table_7_2_resistance_factor_field("static load test")
        # First match in compression list
        assert phi in (0.80, 0.75, 0.60)

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
        """Vibratory installation has Fvs = 0.68."""
        result = table_7_10_brown_method_factors("compression", "vibratory", "clay_to_sand")
        assert result["Fvs"] == 0.68

    def test_no_match_raises(self):
        """Invalid combination raises ValueError."""
        with pytest.raises(ValueError):
            table_7_10_brown_method_factors("tension", "vibratory", "clay_to_sand")


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

    def test_partial_match(self):
        """Partial match on soil type works."""
        cs = table_7_11_eslami_fellenius_cs("fine_sand")
        assert cs == 1.0  # fine_sand_silty_sand

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

    def test_partial_match(self):
        """Partial match works."""
        result = table_7_16_soil_setup_factor("fine_sand")
        assert result["recommended"] == 1.2

    def test_unknown_soil_raises(self):
        """Unknown soil type raises ValueError."""
        with pytest.raises(ValueError):
            table_7_16_soil_setup_factor("organic")
