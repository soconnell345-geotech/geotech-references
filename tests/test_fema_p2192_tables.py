"""Tests for FEMA P-2192 table lookup functions."""

import pytest

from geotech_references.fema_p2192.tables import (
    table_11_6_1_sdc_short_period,
    table_11_6_2_sdc_one_second,
    determine_sdc,
    table_20_3_1_site_class_from_vs30,
    table_20_3_1_site_class_from_spt,
    table_20_3_1_site_class_from_su,
    risk_category_from_occupancy,
    site_coefficient_fa,
    site_coefficient_fv,
    design_spectral_parameters,
)


# ============================================================================
# Table 11.6-1: SDC from Short-Period SDS
# ============================================================================

class TestTable1161SdcShortPeriod:
    """Tests for table_11_6_1_sdc_short_period()."""

    def test_sds_very_low_rc_ii(self):
        """SDS < 0.167 → SDC A for Risk Cat I/II/III."""
        assert table_11_6_1_sdc_short_period(0.10, "II") == "A"

    def test_sds_very_low_rc_iv(self):
        """SDS < 0.167 → SDC A for Risk Cat IV."""
        assert table_11_6_1_sdc_short_period(0.10, "IV") == "A"

    def test_sds_low_rc_ii(self):
        """0.167 <= SDS < 0.33 → SDC B for Risk Cat II."""
        assert table_11_6_1_sdc_short_period(0.25, "II") == "B"

    def test_sds_low_rc_iv(self):
        """0.167 <= SDS < 0.33 → SDC C for Risk Cat IV."""
        assert table_11_6_1_sdc_short_period(0.25, "IV") == "C"

    def test_sds_moderate_rc_iii(self):
        """0.33 <= SDS < 0.50 → SDC C for Risk Cat III."""
        assert table_11_6_1_sdc_short_period(0.40, "III") == "C"

    def test_sds_moderate_rc_iv(self):
        """0.33 <= SDS < 0.50 → SDC D for Risk Cat IV."""
        assert table_11_6_1_sdc_short_period(0.40, "IV") == "D"

    def test_sds_high_rc_i(self):
        """SDS >= 0.50 → SDC D for all risk categories."""
        assert table_11_6_1_sdc_short_period(0.75, "I") == "D"

    def test_sds_high_rc_iv(self):
        """SDS >= 0.50 → SDC D for Risk Cat IV."""
        assert table_11_6_1_sdc_short_period(0.75, "IV") == "D"

    def test_boundary_0167(self):
        """SDS exactly at 0.167 threshold → SDC B (not A)."""
        assert table_11_6_1_sdc_short_period(0.167, "II") == "B"

    def test_boundary_033(self):
        """SDS exactly at 0.33 threshold → SDC C."""
        assert table_11_6_1_sdc_short_period(0.33, "II") == "C"

    def test_boundary_050(self):
        """SDS exactly at 0.50 → SDC D."""
        assert table_11_6_1_sdc_short_period(0.50, "II") == "D"

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            table_11_6_1_sdc_short_period(-0.1, "II")

    def test_invalid_risk_category_raises(self):
        with pytest.raises(ValueError):
            table_11_6_1_sdc_short_period(0.5, "V")


# ============================================================================
# Table 11.6-2: SDC from 1-Second SD1
# ============================================================================

class TestTable1162SdcOneSecond:
    """Tests for table_11_6_2_sdc_one_second()."""

    def test_sd1_very_low_rc_ii(self):
        """SD1 < 0.067 → SDC A."""
        assert table_11_6_2_sdc_one_second(0.05, "II") == "A"

    def test_sd1_very_low_rc_iv(self):
        """SD1 < 0.067 → SDC A for Risk Cat IV too."""
        assert table_11_6_2_sdc_one_second(0.05, "IV") == "A"

    def test_sd1_low_rc_ii(self):
        """0.067 <= SD1 < 0.133 → SDC B for Risk Cat II."""
        assert table_11_6_2_sdc_one_second(0.10, "II") == "B"

    def test_sd1_low_rc_iv(self):
        """0.067 <= SD1 < 0.133 → SDC C for Risk Cat IV."""
        assert table_11_6_2_sdc_one_second(0.10, "IV") == "C"

    def test_sd1_moderate_rc_iii(self):
        """0.133 <= SD1 < 0.20 → SDC C for Risk Cat III."""
        assert table_11_6_2_sdc_one_second(0.15, "III") == "C"

    def test_sd1_moderate_rc_iv(self):
        """0.133 <= SD1 < 0.20 → SDC D for Risk Cat IV."""
        assert table_11_6_2_sdc_one_second(0.15, "IV") == "D"

    def test_sd1_high_rc_ii(self):
        """SD1 >= 0.20 → SDC D."""
        assert table_11_6_2_sdc_one_second(0.30, "II") == "D"

    def test_boundary_0067(self):
        """SD1 exactly at 0.067 → SDC B."""
        assert table_11_6_2_sdc_one_second(0.067, "II") == "B"

    def test_boundary_0133(self):
        """SD1 exactly at 0.133 → SDC C."""
        assert table_11_6_2_sdc_one_second(0.133, "II") == "C"

    def test_boundary_020(self):
        """SD1 exactly at 0.20 → SDC D."""
        assert table_11_6_2_sdc_one_second(0.20, "II") == "D"

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            table_11_6_2_sdc_one_second(-0.01, "II")

    def test_invalid_risk_category_raises(self):
        with pytest.raises(ValueError):
            table_11_6_2_sdc_one_second(0.1, "X")


# ============================================================================
# determine_sdc: Full SDC Algorithm
# ============================================================================

class TestDetermineSdc:
    """Tests for determine_sdc()."""

    def test_both_low_gives_a(self):
        """SDS and SD1 both very low → SDC A."""
        r = determine_sdc(0.10, 0.05, "II")
        assert r["sdc"] == "A"
        assert r["s1_override"] is False

    def test_sds_governs(self):
        """SDS yields higher SDC than SD1."""
        r = determine_sdc(0.60, 0.05, "II")
        assert r["sdc"] == "D"
        assert r["governing_parameter"] == "SDS"

    def test_sd1_governs(self):
        """SD1 yields higher SDC than SDS."""
        r = determine_sdc(0.10, 0.25, "II")
        assert r["sdc"] == "D"
        assert r["governing_parameter"] == "SD1"

    def test_both_equal_sds_governs(self):
        """When both yield same SDC, SDS governs (checked first)."""
        r = determine_sdc(0.60, 0.25, "II")
        assert r["sdc"] == "D"
        assert r["sdc_from_sds"] == "D"
        assert r["sdc_from_sd1"] == "D"

    def test_s1_override_to_e(self):
        """S1 >= 0.75 → SDC E for Risk Cat I/II/III."""
        r = determine_sdc(0.60, 0.25, "II", s1=0.80)
        assert r["sdc"] == "E"
        assert r["s1_override"] is True
        assert r["governing_parameter"] == "S1_override"

    def test_s1_override_to_f(self):
        """S1 >= 0.75 → SDC F for Risk Cat IV."""
        r = determine_sdc(0.60, 0.25, "IV", s1=0.80)
        assert r["sdc"] == "F"
        assert r["s1_override"] is True

    def test_s1_below_threshold_no_override(self):
        """S1 < 0.75 → no override."""
        r = determine_sdc(0.60, 0.25, "II", s1=0.50)
        assert r["sdc"] == "D"
        assert r["s1_override"] is False

    def test_s1_none_no_override(self):
        """s1=None → override not checked."""
        r = determine_sdc(0.60, 0.25, "II", s1=None)
        assert r["sdc"] == "D"
        assert r["s1_override"] is False

    def test_return_keys(self):
        """Check all expected keys are present."""
        r = determine_sdc(0.40, 0.15, "III")
        expected = {"sdc", "sdc_from_sds", "sdc_from_sd1",
                    "governing_parameter", "s1_override",
                    "risk_category", "sds", "sd1"}
        assert set(r.keys()) == expected

    def test_negative_s1_raises(self):
        with pytest.raises(ValueError):
            determine_sdc(0.5, 0.2, "II", s1=-0.1)

    def test_risk_category_normalized(self):
        """Risk category returned in uppercase."""
        r = determine_sdc(0.5, 0.2, " ii ")
        assert r["risk_category"] == "II"


# ============================================================================
# Table 20.3-1: Site Classification from Vs30
# ============================================================================

class TestSiteClassFromVs30:
    """Tests for table_20_3_1_site_class_from_vs30()."""

    def test_class_a(self):
        r = table_20_3_1_site_class_from_vs30(2000)
        assert r["site_class"] == "A"

    def test_class_b(self):
        r = table_20_3_1_site_class_from_vs30(1000)
        assert r["site_class"] == "B"

    def test_class_bc(self):
        r = table_20_3_1_site_class_from_vs30(600)
        assert r["site_class"] == "BC"

    def test_class_c(self):
        r = table_20_3_1_site_class_from_vs30(400)
        assert r["site_class"] == "C"

    def test_class_cd(self):
        r = table_20_3_1_site_class_from_vs30(300)
        assert r["site_class"] == "CD"

    def test_class_d(self):
        r = table_20_3_1_site_class_from_vs30(200)
        assert r["site_class"] == "D"

    def test_class_de(self):
        r = table_20_3_1_site_class_from_vs30(150)
        assert r["site_class"] == "DE"

    def test_class_e(self):
        r = table_20_3_1_site_class_from_vs30(100)
        assert r["site_class"] == "E"

    def test_boundary_1524(self):
        """Vs30 exactly 1524 → A (>= 1524)."""
        r = table_20_3_1_site_class_from_vs30(1524)
        assert r["site_class"] == "A"

    def test_boundary_762(self):
        """Vs30 exactly 762 → B (762 <= vs30 < 1524)."""
        r = table_20_3_1_site_class_from_vs30(762)
        assert r["site_class"] == "B"

    def test_boundary_244(self):
        """Vs30 exactly 244 → CD."""
        r = table_20_3_1_site_class_from_vs30(244)
        assert r["site_class"] == "CD"

    def test_legacy_5class_c(self):
        """Legacy system: 366-762 → C."""
        r = table_20_3_1_site_class_from_vs30(500, system="asce7_16")
        assert r["site_class"] == "C"
        assert r["system"] == "asce7_16"

    def test_legacy_5class_d(self):
        """Legacy system: 183-366 → D."""
        r = table_20_3_1_site_class_from_vs30(300, system="asce7_16")
        assert r["site_class"] == "D"

    def test_legacy_5class_e(self):
        """Legacy system: <183 → E."""
        r = table_20_3_1_site_class_from_vs30(150, system="asce7_16")
        assert r["site_class"] == "E"

    def test_zero_vs30_raises(self):
        with pytest.raises(ValueError):
            table_20_3_1_site_class_from_vs30(0)

    def test_negative_vs30_raises(self):
        with pytest.raises(ValueError):
            table_20_3_1_site_class_from_vs30(-100)

    def test_invalid_system_raises(self):
        with pytest.raises(ValueError):
            table_20_3_1_site_class_from_vs30(300, system="eurocode")


# ============================================================================
# Table 20.3-1: Site Classification from SPT
# ============================================================================

class TestSiteClassFromSpt:
    """Tests for table_20_3_1_site_class_from_spt()."""

    def test_bc_high_n(self):
        r = table_20_3_1_site_class_from_spt(120)
        assert r["site_class"] == "BC"

    def test_c(self):
        r = table_20_3_1_site_class_from_spt(60)
        assert r["site_class"] == "C"

    def test_cd(self):
        r = table_20_3_1_site_class_from_spt(40)
        assert r["site_class"] == "CD"

    def test_d(self):
        r = table_20_3_1_site_class_from_spt(20)
        assert r["site_class"] == "D"

    def test_de(self):
        r = table_20_3_1_site_class_from_spt(10)
        assert r["site_class"] == "DE"

    def test_e(self):
        r = table_20_3_1_site_class_from_spt(5)
        assert r["site_class"] == "E"

    def test_boundary_100(self):
        """N=100 → BC."""
        r = table_20_3_1_site_class_from_spt(100)
        assert r["site_class"] == "BC"

    def test_boundary_50(self):
        """N=50 → C."""
        r = table_20_3_1_site_class_from_spt(50)
        assert r["site_class"] == "C"

    def test_legacy_5class_c(self):
        r = table_20_3_1_site_class_from_spt(60, system="asce7_16")
        assert r["site_class"] == "C"

    def test_legacy_5class_d(self):
        r = table_20_3_1_site_class_from_spt(30, system="asce7_16")
        assert r["site_class"] == "D"

    def test_legacy_5class_e(self):
        r = table_20_3_1_site_class_from_spt(10, system="asce7_16")
        assert r["site_class"] == "E"

    def test_note_present(self):
        """Return dict should include a note about A/B."""
        r = table_20_3_1_site_class_from_spt(20)
        assert "note" in r
        assert "Vs30" in r["note"]

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            table_20_3_1_site_class_from_spt(-5)


# ============================================================================
# Table 20.3-1: Site Classification from Undrained Shear Strength
# ============================================================================

class TestSiteClassFromSu:
    """Tests for table_20_3_1_site_class_from_su()."""

    def test_bc_high_su(self):
        r = table_20_3_1_site_class_from_su(250)
        assert r["site_class"] == "BC"

    def test_c(self):
        r = table_20_3_1_site_class_from_su(150)
        assert r["site_class"] == "C"

    def test_cd(self):
        r = table_20_3_1_site_class_from_su(85)
        assert r["site_class"] == "CD"

    def test_d(self):
        r = table_20_3_1_site_class_from_su(60)
        assert r["site_class"] == "D"

    def test_de(self):
        r = table_20_3_1_site_class_from_su(35)
        assert r["site_class"] == "DE"

    def test_e(self):
        r = table_20_3_1_site_class_from_su(15)
        assert r["site_class"] == "E"

    def test_boundary_192(self):
        """Su=192 → BC."""
        r = table_20_3_1_site_class_from_su(192)
        assert r["site_class"] == "BC"

    def test_boundary_100(self):
        """Su=100 → C."""
        r = table_20_3_1_site_class_from_su(100)
        assert r["site_class"] == "C"

    def test_legacy_5class_c(self):
        r = table_20_3_1_site_class_from_su(150, system="asce7_16")
        assert r["site_class"] == "C"

    def test_legacy_5class_d(self):
        r = table_20_3_1_site_class_from_su(75, system="asce7_16")
        assert r["site_class"] == "D"

    def test_legacy_5class_e(self):
        r = table_20_3_1_site_class_from_su(30, system="asce7_16")
        assert r["site_class"] == "E"

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            table_20_3_1_site_class_from_su(0)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            table_20_3_1_site_class_from_su(-10)


# ============================================================================
# Risk Category from Occupancy
# ============================================================================

class TestRiskCategory:
    """Tests for risk_category_from_occupancy()."""

    def test_agricultural(self):
        r = risk_category_from_occupancy("agricultural")
        assert r["risk_category"] == "I"

    def test_residential(self):
        r = risk_category_from_occupancy("residential")
        assert r["risk_category"] == "II"

    def test_commercial(self):
        r = risk_category_from_occupancy("commercial")
        assert r["risk_category"] == "II"

    def test_standard(self):
        r = risk_category_from_occupancy("standard")
        assert r["risk_category"] == "II"

    def test_school(self):
        r = risk_category_from_occupancy("school")
        assert r["risk_category"] == "III"

    def test_assembly(self):
        r = risk_category_from_occupancy("assembly")
        assert r["risk_category"] == "III"

    def test_hospital(self):
        r = risk_category_from_occupancy("hospital")
        assert r["risk_category"] == "IV"

    def test_fire_station(self):
        r = risk_category_from_occupancy("fire_station")
        assert r["risk_category"] == "IV"

    def test_essential(self):
        r = risk_category_from_occupancy("essential")
        assert r["risk_category"] == "IV"

    def test_case_insensitive(self):
        r = risk_category_from_occupancy("HOSPITAL")
        assert r["risk_category"] == "IV"

    def test_partial_match(self):
        """'police' should partial-match 'police_station'."""
        r = risk_category_from_occupancy("police")
        assert r["risk_category"] == "IV"

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            risk_category_from_occupancy("spaceship")


# ============================================================================
# Site Coefficient Fa (ASCE 7-22 Table 11.4-1)
# ============================================================================

class TestSiteCoefficientFa:
    """Tests for site_coefficient_fa()."""

    def test_class_a(self):
        """Site A: Fa = 0.8 for all Ss."""
        assert site_coefficient_fa("A", 0.50) == 0.8

    def test_class_b(self):
        """Site B: Fa = 0.9 for all Ss."""
        assert site_coefficient_fa("B", 1.00) == 0.9

    def test_class_bc_low_ss(self):
        """BC at Ss=0.25 → 1.3."""
        assert site_coefficient_fa("BC", 0.25) == 1.3

    def test_class_bc_high_ss(self):
        """BC at Ss=1.50 → 1.0."""
        assert site_coefficient_fa("BC", 1.50) == 1.0

    def test_class_c_at_075(self):
        """C at Ss=0.75 → 1.2."""
        assert site_coefficient_fa("C", 0.75) == 1.2

    def test_class_d_low_ss(self):
        """D at Ss=0.25 → 1.8."""
        assert site_coefficient_fa("D", 0.25) == 1.8

    def test_class_d_at_100(self):
        """D at Ss=1.00 → 1.2."""
        assert site_coefficient_fa("D", 1.00) == 1.2

    def test_class_de_low_ss(self):
        """DE at Ss=0.25 → 2.4."""
        assert site_coefficient_fa("DE", 0.25) == 2.4

    def test_class_e_low_ss(self):
        """E at Ss=0.25 → 2.5."""
        assert site_coefficient_fa("E", 0.25) == 2.5

    def test_interpolation_cd(self):
        """CD at Ss=0.375 (midpoint 0.25-0.50) interpolates between 1.6 and 1.4."""
        fa = site_coefficient_fa("CD", 0.375)
        assert fa == pytest.approx(1.5)

    def test_interpolation_d(self):
        """D at Ss=0.625 (midpoint 0.50-0.75) interpolates between 1.6 and 1.4."""
        fa = site_coefficient_fa("D", 0.625)
        assert fa == pytest.approx(1.5)

    def test_clamped_below(self):
        """Ss below 0.25 clamps to Ss=0.25 value."""
        assert site_coefficient_fa("D", 0.10) == site_coefficient_fa("D", 0.25)

    def test_clamped_above(self):
        """Ss above 1.50 clamps to Ss=1.50 value."""
        assert site_coefficient_fa("D", 2.00) == site_coefficient_fa("D", 1.50)

    def test_class_f_raises(self):
        with pytest.raises(ValueError, match="site-specific"):
            site_coefficient_fa("F", 0.5)

    def test_unknown_class_raises(self):
        with pytest.raises(ValueError):
            site_coefficient_fa("X", 0.5)


# ============================================================================
# Site Coefficient Fv (ASCE 7-22 Table 11.4-2)
# ============================================================================

class TestSiteCoefficientFv:
    """Tests for site_coefficient_fv()."""

    def test_class_a(self):
        """Site A: Fv = 0.8 for all S1."""
        assert site_coefficient_fv("A", 0.30) == 0.8

    def test_class_b(self):
        """Site B: Fv = 0.8 for all S1."""
        assert site_coefficient_fv("B", 0.50) == 0.8

    def test_class_bc_low_s1(self):
        """BC at S1=0.10 → 1.5."""
        assert site_coefficient_fv("BC", 0.10) == 1.5

    def test_class_bc_high_s1(self):
        """BC at S1=0.60 → 1.1."""
        assert site_coefficient_fv("BC", 0.60) == 1.1

    def test_class_c_at_040(self):
        """C at S1=0.40 → 1.4."""
        assert site_coefficient_fv("C", 0.40) == 1.4

    def test_class_cd_low_s1(self):
        """CD at S1=0.10 → 2.4."""
        assert site_coefficient_fv("CD", 0.10) == 2.4

    def test_class_d_low_s1(self):
        """D at S1=0.10 → 4.0."""
        assert site_coefficient_fv("D", 0.10) == 4.0

    def test_class_d_high_s1(self):
        """D at S1=0.60 → 2.0."""
        assert site_coefficient_fv("D", 0.60) == 2.0

    def test_interpolation_cd(self):
        """CD at S1=0.35 (midpoint 0.30-0.40) interpolates between 1.8 and 1.6."""
        fv = site_coefficient_fv("CD", 0.35)
        assert fv == pytest.approx(1.7)

    def test_interpolation_d(self):
        """D at S1=0.55 (midpoint 0.50-0.60) interpolates between 2.2 and 2.0."""
        fv = site_coefficient_fv("D", 0.55)
        assert fv == pytest.approx(2.1)

    def test_clamped_below(self):
        """S1 below 0.10 clamps to S1=0.10 value."""
        assert site_coefficient_fv("D", 0.05) == site_coefficient_fv("D", 0.10)

    def test_clamped_above(self):
        """S1 above 0.60 clamps to S1=0.60 value."""
        assert site_coefficient_fv("D", 0.80) == site_coefficient_fv("D", 0.60)

    def test_class_de_raises(self):
        """DE requires site-specific analysis."""
        with pytest.raises(ValueError, match="site-specific"):
            site_coefficient_fv("DE", 0.3)

    def test_class_e_raises(self):
        """E requires site-specific analysis."""
        with pytest.raises(ValueError, match="site-specific"):
            site_coefficient_fv("E", 0.3)

    def test_class_f_raises(self):
        """F requires site-specific analysis."""
        with pytest.raises(ValueError, match="site-specific"):
            site_coefficient_fv("F", 0.3)

    def test_unknown_class_raises(self):
        with pytest.raises(ValueError):
            site_coefficient_fv("X", 0.3)


# ============================================================================
# Design Spectral Parameters
# ============================================================================

class TestDesignSpectralParameters:
    """Tests for design_spectral_parameters()."""

    def test_basic_computation(self):
        """SDS = (2/3)*Fa*Ss, SD1 = (2/3)*Fv*S1."""
        r = design_spectral_parameters(1.0, 0.4, "C")
        fa = site_coefficient_fa("C", 1.0)
        fv = site_coefficient_fv("C", 0.4)
        assert r["sds"] == pytest.approx((2.0 / 3.0) * fa * 1.0, abs=0.001)
        assert r["sd1"] == pytest.approx((2.0 / 3.0) * fv * 0.4, abs=0.001)

    def test_fa_fv_returned(self):
        """Fa and Fv values included in result."""
        r = design_spectral_parameters(0.5, 0.2, "D")
        assert r["fa"] == pytest.approx(site_coefficient_fa("D", 0.5))
        assert r["fv"] == pytest.approx(site_coefficient_fv("D", 0.2))

    def test_site_class_a(self):
        """Site A: Fa=0.8, Fv=0.8."""
        r = design_spectral_parameters(1.0, 0.4, "A")
        assert r["fa"] == pytest.approx(0.8)
        assert r["fv"] == pytest.approx(0.8)
        assert r["sds"] == pytest.approx((2.0 / 3.0) * 0.8 * 1.0, abs=0.001)
        assert r["sd1"] == pytest.approx((2.0 / 3.0) * 0.8 * 0.4, abs=0.001)

    def test_de_class_sd1_none(self):
        """DE: Fv requires site-specific, sd1 and fv returned as None."""
        r = design_spectral_parameters(0.5, 0.3, "DE")
        assert r["fa"] is not None
        assert r["sds"] is not None
        assert r["fv"] is None
        assert r["sd1"] is None

    def test_e_class_sd1_none(self):
        """E: same as DE, fv/sd1 = None."""
        r = design_spectral_parameters(0.5, 0.3, "E")
        assert r["fv"] is None
        assert r["sd1"] is None

    def test_return_keys(self):
        """Check all expected keys are present."""
        r = design_spectral_parameters(1.0, 0.4, "C")
        expected = {"sds", "sd1", "fa", "fv", "ss", "s1", "site_class"}
        assert set(r.keys()) == expected

    def test_site_class_normalized(self):
        """Site class returned uppercase."""
        r = design_spectral_parameters(1.0, 0.4, "c")
        assert r["site_class"] == "C"

    def test_negative_ss_raises(self):
        with pytest.raises(ValueError):
            design_spectral_parameters(-0.1, 0.4, "C")

    def test_negative_s1_raises(self):
        with pytest.raises(ValueError):
            design_spectral_parameters(1.0, -0.1, "C")

    def test_class_f_raises(self):
        """F requires site-specific Fa, so it raises."""
        with pytest.raises(ValueError):
            design_spectral_parameters(1.0, 0.4, "F")
