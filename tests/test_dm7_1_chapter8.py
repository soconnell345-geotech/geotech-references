"""Comprehensive tests for geotech.dm7_1.chapter8 -- Correlations for Soil and Rock.

Tests cover all 45 public functions (Equations 8-1 through 8-45) with:
  - Basic valid-input tests using hand-calculated expected values
  - Edge-case tests where applicable
  - ValueError checks for every validation branch

Reference: UFS 3-220-10, Chapter 8.
"""

import math

import pytest

from geotech_references.dm7_1.chapter8 import *


# ============================================================================
# Eq 8-1: spt_n_correction_for_pore_pressure
# ============================================================================


class TestSptNCorrectionForPorePressure:
    """Tests for Equation 8-1."""

    def test_basic_below_threshold(self):
        # N60 = 10 <= 15, returned unchanged
        assert spt_n_correction_for_pore_pressure(10.0) == pytest.approx(10.0, rel=1e-4)

    def test_basic_above_threshold(self):
        # N60 = 25: N' = 15 + 0.5*(25-15) = 15 + 5 = 20
        assert spt_n_correction_for_pore_pressure(25.0) == pytest.approx(20.0, rel=1e-4)

    def test_at_threshold(self):
        # N60 = 15: exactly at boundary, returned unchanged
        assert spt_n_correction_for_pore_pressure(15.0) == pytest.approx(15.0, rel=1e-4)

    def test_zero(self):
        assert spt_n_correction_for_pore_pressure(0.0) == pytest.approx(0.0, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="n60 must be non-negative"):
            spt_n_correction_for_pore_pressure(-1.0)


# ============================================================================
# Eq 8-2: spt_friction_angle_roads
# ============================================================================


class TestSptFrictionAngleRoads:
    """Tests for Equation 8-2."""

    def test_basic(self):
        # N60 = 20: phi' = sqrt(15*20) + 15 = sqrt(300) + 15 = 17.3205 + 15 = 32.3205
        expected = math.sqrt(300.0) + 15.0
        assert spt_friction_angle_roads(20.0) == pytest.approx(expected, rel=1e-4)

    def test_zero(self):
        # N60 = 0: phi' = sqrt(0) + 15 = 15
        assert spt_friction_angle_roads(0.0) == pytest.approx(15.0, rel=1e-4)

    def test_end_of_plotted_curve(self):
        # Figure 8-2, PDF p. 425 (printed p. 397), plots Shioi and Fukui's
        # two relationships for N60 from 0 to 50, ending near 42 degrees.
        # N60 = 50: sqrt(750) + 15 = 42.39 (roads); 0.3*50 + 27 = 42.0
        assert spt_friction_angle_roads(50.0) == pytest.approx(42.39, abs=0.01)
        assert spt_friction_angle_buildings(50.0) == pytest.approx(42.0, abs=0.01)

    def test_above_plotted_curve_raises(self):
        with pytest.raises(ValueError, match="above 50"):
            spt_friction_angle_roads(60.0)
        with pytest.raises(ValueError, match="above 50"):
            spt_friction_angle_buildings(60.0)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="n60 must be non-negative"):
            spt_friction_angle_roads(-5.0)


# ============================================================================
# Eq 8-3: spt_friction_angle_buildings
# ============================================================================


class TestSptFrictionAngleBuildings:
    """Tests for Equation 8-3."""

    def test_basic(self):
        # N60 = 20: phi' = 0.3*20 + 27 = 6 + 27 = 33
        assert spt_friction_angle_buildings(20.0) == pytest.approx(33.0, rel=1e-4)

    def test_zero(self):
        # N60 = 0: phi' = 27
        assert spt_friction_angle_buildings(0.0) == pytest.approx(27.0, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="n60 must be non-negative"):
            spt_friction_angle_buildings(-1.0)


# ============================================================================
# Eq 8-4: spt_friction_angle_kulhawy_mayne
# ============================================================================


class TestSptFrictionAngleKulhawyMayne:
    """Tests for Equation 8-4."""

    def test_basic(self):
        # N60=20, sigma_v_eff=100, pa=101.325
        # ratio = 20 / (12.2 + 20.3*(100/101.325))
        # = 20 / (12.2 + 20.3*0.98692) = 20 / (12.2 + 20.03447) = 20 / 32.23447
        # tan(phi) = 0.620455 ^ 0.34
        # 0.620455^0.34 = exp(0.34 * ln(0.620455)) = exp(0.34 * (-0.47836)) = exp(-0.16264) = 0.84987
        # phi = atan(0.84987) = 40.369 deg
        ratio = 20.0 / (12.2 + 20.3 * (100.0 / 101.325))
        tan_phi = ratio ** 0.34
        expected = math.degrees(math.atan(tan_phi))
        assert spt_friction_angle_kulhawy_mayne(20.0, 100.0, 101.325) == pytest.approx(
            expected, rel=1e-4
        )

    def test_zero_n60(self):
        # N60=0 => ratio=0, tan(phi)=0^0.34=0, phi=0
        assert spt_friction_angle_kulhawy_mayne(0.0, 100.0, 101.325) == pytest.approx(
            0.0, rel=1e-4
        )

    def test_negative_n60_raises(self):
        with pytest.raises(ValueError, match="n60 must be non-negative"):
            spt_friction_angle_kulhawy_mayne(-1.0, 100.0, 101.325)

    def test_negative_sigma_v_eff_raises(self):
        with pytest.raises(ValueError, match="sigma_v_eff must be non-negative"):
            spt_friction_angle_kulhawy_mayne(20.0, -1.0, 101.325)

    def test_zero_pa_raises(self):
        with pytest.raises(ValueError, match="pa must be positive"):
            spt_friction_angle_kulhawy_mayne(20.0, 100.0, 0.0)

    def test_negative_pa_raises(self):
        with pytest.raises(ValueError, match="pa must be positive"):
            spt_friction_angle_kulhawy_mayne(20.0, 100.0, -1.0)


# ============================================================================
# Eq 8-5: spt_friction_angle_wolff
# ============================================================================


class TestSptFrictionAngleWolff:
    """Tests for Equation 8-5."""

    def test_basic(self):
        # N1,60 = 20: phi' = 27.1 + 0.3*20 - 0.00054*20^2
        # = 27.1 + 6.0 - 0.00054*400 = 27.1 + 6.0 - 0.216 = 32.884
        assert spt_friction_angle_wolff(20.0) == pytest.approx(32.884, rel=1e-4)

    def test_zero(self):
        # N1,60 = 0: phi' = 27.1
        assert spt_friction_angle_wolff(0.0) == pytest.approx(27.1, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="n1_60 must be non-negative"):
            spt_friction_angle_wolff(-1.0)


# ============================================================================
# Eq 8-6: spt_friction_angle_hatanaka_uchida
# ============================================================================


class TestSptFrictionAngleHatanakaUchida:
    """Tests for Equation 8-6."""

    def test_basic(self):
        # N1,60 = 25: phi' = sqrt(15.4*25) + 20 = sqrt(385) + 20 = 19.6214 + 20 = 39.6214
        expected = math.sqrt(15.4 * 25.0) + 20.0
        assert spt_friction_angle_hatanaka_uchida(25.0) == pytest.approx(expected, rel=1e-4)

    def test_zero(self):
        # N1,60 = 0: phi' = 0 + 20 = 20
        assert spt_friction_angle_hatanaka_uchida(0.0) == pytest.approx(20.0, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="n1_60 must be non-negative"):
            spt_friction_angle_hatanaka_uchida(-1.0)


# ============================================================================
# Eq 8-7: cpt_friction_angle_mayne
# ============================================================================


class TestCptFrictionAngleMayne:
    """Tests for Equation 8-7."""

    def test_basic(self):
        # Eq. 8-7 as printed, PDF p. 428 (printed p. 400):
        # phi' = 17.6 + 11 log[(qt/Pa) / sqrt(sigma'v/Pa)]
        # qt=10000, sigma'v=400, Pa=100: (100)/sqrt(4) = 50
        # phi' = 17.6 + 11 * 1.69897 = 36.2887
        assert cpt_friction_angle_mayne(10000.0, 400.0, 100.0) == pytest.approx(
            36.2887, abs=1e-3
        )

    def test_vertical_stress_under_square_root(self):
        # PDF p. 428 (printed p. 400). qt=20000, sigma'v=25, Pa=100:
        # (200)/sqrt(0.25) = 400; phi' = 17.6 + 11 * 2.60206 = 46.2227
        assert cpt_friction_angle_mayne(20000.0, 25.0, 100.0) == pytest.approx(
            46.2227, abs=1e-3
        )

    def test_qt_not_positive_raises(self):
        with pytest.raises(ValueError, match="qt must be positive"):
            cpt_friction_angle_mayne(0.0, 100.0, 101.325)

    def test_sigma_v_eff_not_positive_raises(self):
        with pytest.raises(ValueError, match="sigma_v_eff must be positive"):
            cpt_friction_angle_mayne(5000.0, 0.0, 101.325)

    def test_pa_not_positive_raises(self):
        with pytest.raises(ValueError, match="pa must be positive"):
            cpt_friction_angle_mayne(5000.0, 100.0, 0.0)


# ============================================================================
# Eq 8-8: cpt_friction_angle_robertson_campanella
# ============================================================================


class TestCptFrictionAngleRobertsonCampanella:
    """Tests for Equation 8-8."""

    def test_basic(self):
        # Eq. 8-8 as printed, PDF p. 430 (printed p. 402):
        # tan(phi') = (1/2.68) [log(qc/sigma'v) + 0.29]
        # qc/sigma'v = 100: tan(phi') = 2.29/2.68 = 0.85448, phi' = 40.513 deg
        assert cpt_friction_angle_robertson_campanella(10000.0, 100.0) == pytest.approx(
            40.513, abs=1e-3
        )

    def test_angle_rises_with_tip_resistance(self):
        # PDF p. 430 (printed p. 402).
        # qc/sigma'v = 50: tan(phi') = 1.98897/2.68 = 0.74215, phi' = 36.581 deg
        # qc/sigma'v = 300: tan(phi') = 2.76712/2.68 = 1.03251, phi' = 45.916 deg
        assert cpt_friction_angle_robertson_campanella(5000.0, 100.0) == pytest.approx(
            36.581, abs=1e-3
        )
        assert cpt_friction_angle_robertson_campanella(30000.0, 100.0) == pytest.approx(
            45.916, abs=1e-3
        )

    def test_qc_not_positive_raises(self):
        with pytest.raises(ValueError, match="qc must be positive"):
            cpt_friction_angle_robertson_campanella(0.0, 100.0)

    def test_sigma_v_eff_not_positive_raises(self):
        with pytest.raises(ValueError, match="sigma_v_eff must be positive"):
            cpt_friction_angle_robertson_campanella(5000.0, 0.0)

    def test_bracket_nonpositive_raises(self):
        # log10(qc/sigma_v_eff) + 0.29 <= 0 gives no positive friction angle.
        # qc=50, sigma_v_eff=100 => log10(0.5) = -0.3010; -0.3010 + 0.29 < 0
        with pytest.raises(ValueError, match="is not positive"):
            cpt_friction_angle_robertson_campanella(50.0, 100.0)


# ============================================================================
# Eq 8-9: cpt_oc_nc_resistance_ratio
# ============================================================================


class TestCptOcNcResistanceRatio:
    """Tests for Equation 8-9."""

    def test_basic(self):
        # OCR=4, beta=0.5: R = 1 + 0.75*(4^0.5 - 1) = 1 + 0.75*(2-1) = 1 + 0.75 = 1.75
        assert cpt_oc_nc_resistance_ratio(4.0, 0.5) == pytest.approx(1.75, rel=1e-4)

    def test_nc_soil(self):
        # OCR=1 (NC): R = 1 + 0.75*(1^beta - 1) = 1 + 0 = 1 for any beta
        assert cpt_oc_nc_resistance_ratio(1.0, 0.8) == pytest.approx(1.0, rel=1e-4)

    def test_ocr_less_than_one_raises(self):
        with pytest.raises(ValueError, match="ocr must be >= 1.0"):
            cpt_oc_nc_resistance_ratio(0.5, 0.5)


# ============================================================================
# Eq 8-10: dmt_horizontal_stress_index
# ============================================================================


class TestDmtHorizontalStressIndex:
    """Tests for Equation 8-10."""

    def test_basic(self):
        # p0=300, u0=50, sigma_v_eff=100: KD = (300-50)/100 = 2.5
        assert dmt_horizontal_stress_index(300.0, 50.0, 100.0) == pytest.approx(
            2.5, rel=1e-4
        )

    def test_zero_pore_pressure(self):
        # p0=200, u0=0, sigma_v_eff=100: KD = 200/100 = 2.0
        assert dmt_horizontal_stress_index(200.0, 0.0, 100.0) == pytest.approx(
            2.0, rel=1e-4
        )

    def test_sigma_v_eff_not_positive_raises(self):
        with pytest.raises(ValueError, match="sigma_v_eff must be positive"):
            dmt_horizontal_stress_index(300.0, 50.0, 0.0)

    def test_sigma_v_eff_negative_raises(self):
        with pytest.raises(ValueError, match="sigma_v_eff must be positive"):
            dmt_horizontal_stress_index(300.0, 50.0, -10.0)


# ============================================================================
# Eq 8-11: dmt_friction_angle_upper_bound
# ============================================================================


class TestDmtFrictionAngleUpperBound:
    """Tests for Equation 8-11."""

    def test_basic(self):
        # KD=5: phi' = 31 + 5/(0.236 + 0.066*5) = 31 + 5/(0.236+0.33) = 31 + 5/0.566 = 31 + 8.8339
        expected = 31.0 + 5.0 / (0.236 + 0.066 * 5.0)
        assert dmt_friction_angle_upper_bound(5.0) == pytest.approx(expected, rel=1e-4)

    def test_small_kd(self):
        # KD=1: phi' = 31 + 1/(0.236+0.066) = 31 + 1/0.302 = 31 + 3.3113
        expected = 31.0 + 1.0 / 0.302
        assert dmt_friction_angle_upper_bound(1.0) == pytest.approx(expected, rel=1e-4)

    def test_denominator_nonpositive_raises(self):
        # 0.236 + 0.066*kd <= 0 => kd <= -0.236/0.066 = -3.5758
        with pytest.raises(ValueError, match="Denominator.*non-positive"):
            dmt_friction_angle_upper_bound(-4.0)


# ============================================================================
# Eq 8-12: dmt_friction_angle_lower_bound
# ============================================================================


class TestDmtFrictionAngleLowerBound:
    """Tests for Equation 8-12."""

    def test_basic(self):
        # KD=5: log10(5) = 0.69897
        # phi' = 28 + 14.6*0.69897 - 2.1*0.69897^2
        # = 28 + 10.2050 - 2.1*0.48856 = 28 + 10.2050 - 1.0260 = 37.179
        log_kd = math.log10(5.0)
        expected = 28.0 + 14.6 * log_kd - 2.1 * log_kd ** 2
        assert dmt_friction_angle_lower_bound(5.0) == pytest.approx(expected, rel=1e-4)

    def test_kd_equals_one(self):
        # KD=1: log10(1)=0 => phi' = 28
        assert dmt_friction_angle_lower_bound(1.0) == pytest.approx(28.0, rel=1e-4)

    def test_kd_not_positive_raises(self):
        with pytest.raises(ValueError, match="kd must be positive"):
            dmt_friction_angle_lower_bound(0.0)

    def test_kd_negative_raises(self):
        with pytest.raises(ValueError, match="kd must be positive"):
            dmt_friction_angle_lower_bound(-1.0)


# ============================================================================
# Eq 8-13: fully_softened_friction_angle
# ============================================================================


class TestFullySoftenedFrictionAngle:
    """Tests for Equation 8-13."""

    def test_basic(self):
        # Eq. 8-13 as printed, PDF p. 435 (printed p. 407):
        # phi'FS = 0.0058 PI^1.73 - 0.32 PI + 36.2
        # PI=40: 40^1.73 = 590.97; 3.4276 - 12.8 + 36.2 = 26.83
        assert fully_softened_friction_angle(40.0) == pytest.approx(26.83, abs=0.01)

    def test_angle_falls_with_plasticity(self):
        # PDF p. 435 (printed p. 407); Figure 8-13, PDF p. 436 (printed
        # p. 408), plots the angle falling from about 36 at PI 0 to about
        # 21 at PI 100.
        # PI=20: 1.0333 - 6.4 + 36.2 = 30.83; PI=100: 16.727 - 32 + 36.2 = 20.93
        assert fully_softened_friction_angle(20.0) == pytest.approx(30.83, abs=0.01)
        assert fully_softened_friction_angle(100.0) == pytest.approx(20.93, abs=0.01)

    def test_zero_pi(self):
        # PI=0: phi'FS = 0 + 0 + 36.2 = 36.2
        assert fully_softened_friction_angle(0.0) == pytest.approx(36.2, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="pi must be non-negative"):
            fully_softened_friction_angle(-1.0)


# ============================================================================
# Eq 8-14: secant_friction_angle_shear_strength
# ============================================================================


class TestSecantFrictionAngleShearStrength:
    """Tests for Equation 8-14."""

    def test_basic(self):
        # sigma_ff_eff=100, phi_sec=30 deg
        # s = 100 * tan(30 deg) = 100 * 0.57735 = 57.735
        expected = 100.0 * math.tan(math.radians(30.0))
        assert secant_friction_angle_shear_strength(100.0, 30.0) == pytest.approx(
            expected, rel=1e-4
        )

    def test_zero_stress(self):
        # sigma_ff_eff=0 => s=0
        assert secant_friction_angle_shear_strength(0.0, 30.0) == pytest.approx(
            0.0, rel=1e-4
        )

    def test_zero_angle(self):
        # phi_sec=0 => s=0
        assert secant_friction_angle_shear_strength(100.0, 0.0) == pytest.approx(
            0.0, rel=1e-4
        )

    def test_negative_stress_raises(self):
        with pytest.raises(ValueError, match="sigma_ff_eff must be non-negative"):
            secant_friction_angle_shear_strength(-1.0, 30.0)

    def test_angle_below_zero_raises(self):
        with pytest.raises(ValueError, match="phi_sec_deg must be in"):
            secant_friction_angle_shear_strength(100.0, -1.0)

    def test_angle_at_90_raises(self):
        with pytest.raises(ValueError, match="phi_sec_deg must be in"):
            secant_friction_angle_shear_strength(100.0, 90.0)

    def test_angle_above_90_raises(self):
        with pytest.raises(ValueError, match="phi_sec_deg must be in"):
            secant_friction_angle_shear_strength(100.0, 91.0)


# ============================================================================
# Eq 8-15: power_function_shear_strength
# ============================================================================


class TestPowerFunctionShearStrength:
    """Tests for Equation 8-15."""

    def test_basic(self):
        # a=0.5, sigma_ff_eff=200, pa=101.325, b=0.8
        # s = 0.5 * 101.325 * (200/101.325)^0.8
        # (200/101.325) = 1.97384; 1.97384^0.8 = exp(0.8*ln(1.97384)) = exp(0.8*0.68009) = exp(0.54407) = 1.72333
        # s = 0.5 * 101.325 * 1.72333 = 87.307
        expected = 0.5 * 101.325 * (200.0 / 101.325) ** 0.8
        assert power_function_shear_strength(0.5, 200.0, 101.325, 0.8) == pytest.approx(
            expected, rel=1e-4
        )

    def test_zero_stress(self):
        # sigma_ff_eff=0 => s=0 (since 0^b = 0 for b>0)
        assert power_function_shear_strength(0.5, 0.0, 101.325, 0.8) == pytest.approx(
            0.0, rel=1e-4
        )

    def test_negative_stress_raises(self):
        with pytest.raises(ValueError, match="sigma_ff_eff must be non-negative"):
            power_function_shear_strength(0.5, -1.0, 101.325, 0.8)

    def test_pa_not_positive_raises(self):
        with pytest.raises(ValueError, match="pa must be positive"):
            power_function_shear_strength(0.5, 200.0, 0.0, 0.8)

    def test_pa_negative_raises(self):
        with pytest.raises(ValueError, match="pa must be positive"):
            power_function_shear_strength(0.5, 200.0, -1.0, 0.8)


# ============================================================================
# Eq 8-16: residual_friction_angle_gibson
# ============================================================================


class TestResidualFrictionAngleGibson:
    """Tests for Equation 8-16."""

    def test_basic(self):
        # PI=40: phi'r = 0.084*40^1.4 - 0.75*40 + 31.9
        # 40^1.4 = exp(1.4*ln(40)) = exp(1.4*3.68888) = exp(5.16443) = 174.94
        # = 0.084*174.94 - 30.0 + 31.9 = 14.695 - 30.0 + 31.9 = 16.595
        expected = 0.084 * 40.0 ** 1.4 - 0.75 * 40.0 + 31.9
        assert residual_friction_angle_gibson(40.0) == pytest.approx(expected, rel=1e-4)

    def test_zero_pi(self):
        # PI=0: phi'r = 0 - 0 + 31.9 = 31.9
        assert residual_friction_angle_gibson(0.0) == pytest.approx(31.9, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="pi must be non-negative"):
            residual_friction_angle_gibson(-1.0)


# ============================================================================
# Eq 8-17: residual_friction_angle_stark_hussain
# ============================================================================


class TestResidualFrictionAngleStarkHussain:
    """Tests for Equation 8-17."""

    def test_basic(self):
        # LL=60, C0=46.6, C1=-0.3357, C2=-0.00171, C3=0.0000138
        # phi'r = 46.6 + (-0.3357)*60 + (-0.00171)*60^2 + 0.0000138*60^3
        # = 46.6 - 20.142 - 6.156 + 2.9808 = 23.2828
        expected = 46.6 + (-0.3357) * 60.0 + (-0.00171) * 3600.0 + 0.0000138 * 216000.0
        assert residual_friction_angle_stark_hussain(
            60.0, 46.6, -0.3357, -0.00171, 0.0000138
        ) == pytest.approx(expected, rel=1e-4)

    def test_zero_ll(self):
        # LL=0: phi'r = C0
        assert residual_friction_angle_stark_hussain(0.0, 50.0, -0.5, 0.001, -0.00001) == pytest.approx(
            50.0, rel=1e-4
        )

    def test_negative_ll_raises(self):
        with pytest.raises(ValueError, match="ll must be non-negative"):
            residual_friction_angle_stark_hussain(-1.0, 46.6, -0.3357, -0.00171, 0.0000138)


# ============================================================================
# Eq 8-18: undrained_strength_ratio_skempton
# ============================================================================


class TestUndrainedStrengthRatioSkempton:
    """Tests for Equation 8-18."""

    def test_basic(self):
        # PI=30: su/sv = 0.11 + 0.0037*30 = 0.11 + 0.111 = 0.221
        assert undrained_strength_ratio_skempton(30.0) == pytest.approx(0.221, rel=1e-4)

    def test_zero_pi(self):
        # PI=0: su/sv = 0.11
        assert undrained_strength_ratio_skempton(0.0) == pytest.approx(0.11, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="pi must be non-negative"):
            undrained_strength_ratio_skempton(-1.0)


# ============================================================================
# Eq 8-19: undrained_strength_ratio_hansbo
# ============================================================================


class TestUndrainedStrengthRatioHansbo:
    """Tests for Equation 8-19."""

    def test_basic(self):
        # LL=50: (su/sv)_NC = 0.0045*50 = 0.225
        assert undrained_strength_ratio_hansbo(50.0) == pytest.approx(0.225, rel=1e-4)

    def test_zero_ll(self):
        # LL=0: 0
        assert undrained_strength_ratio_hansbo(0.0) == pytest.approx(0.0, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="ll must be non-negative"):
            undrained_strength_ratio_hansbo(-1.0)


# ============================================================================
# Eq 8-20: undrained_strength_ratio_oc
# ============================================================================


class TestUndrainedStrengthRatioOc:
    """Tests for Equation 8-20."""

    def test_basic(self):
        # su_sigma_v_nc=0.25, OCR=4, m=0.8
        # (su/sv)_OC = 0.25 * 4^0.8 = 0.25 * 3.03143 = 0.75786
        expected = 0.25 * 4.0 ** 0.8
        assert undrained_strength_ratio_oc(0.25, 4.0, 0.8) == pytest.approx(
            expected, rel=1e-4
        )

    def test_nc_soil(self):
        # OCR=1: (su/sv)_OC = su_sigma_v_nc * 1^m = su_sigma_v_nc
        assert undrained_strength_ratio_oc(0.25, 1.0, 0.8) == pytest.approx(0.25, rel=1e-4)

    def test_negative_ratio_raises(self):
        with pytest.raises(ValueError, match="su_sigma_v_nc must be non-negative"):
            undrained_strength_ratio_oc(-0.1, 4.0, 0.8)

    def test_ocr_less_than_one_raises(self):
        with pytest.raises(ValueError, match="ocr must be >= 1.0"):
            undrained_strength_ratio_oc(0.25, 0.5, 0.8)


# ============================================================================
# Eq 8-21: undrained_strength_from_preconsolidation
# ============================================================================


class TestUndrainedStrengthFromPreconsolidation:
    """Tests for Equation 8-21."""

    def test_basic(self):
        # sigma_p_eff=200: su = 0.21*200 = 42
        assert undrained_strength_from_preconsolidation(200.0) == pytest.approx(42.0, rel=1e-4)

    def test_zero(self):
        assert undrained_strength_from_preconsolidation(0.0) == pytest.approx(0.0, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="sigma_p_eff must be non-negative"):
            undrained_strength_from_preconsolidation(-1.0)


# ============================================================================
# Eq 8-22: undrained_strength_ratio_acu_from_icu
# ============================================================================


class TestUndrainedStrengthRatioAcuFromIcu:
    """Tests for Equation 8-22."""

    def test_basic(self):
        # su_sigma_v_icu=0.5: (su/sv)_ACU = 0.15 + 0.49*0.5 = 0.15 + 0.245 = 0.395
        assert undrained_strength_ratio_acu_from_icu(0.5) == pytest.approx(0.395, rel=1e-4)

    def test_zero(self):
        # su_sigma_v_icu=0: 0.15 + 0 = 0.15
        assert undrained_strength_ratio_acu_from_icu(0.0) == pytest.approx(0.15, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="su_sigma_v_icu must be non-negative"):
            undrained_strength_ratio_acu_from_icu(-0.1)


# ============================================================================
# Eq 8-23: cpt_undrained_strength_nc
# ============================================================================


class TestCptUndrainedStrengthNc:
    """Tests for Equation 8-23."""

    def test_basic(self):
        # qc=2000, Nc=20: su = 2000/20 = 100
        assert cpt_undrained_strength_nc(2000.0, 20.0) == pytest.approx(100.0, rel=1e-4)

    def test_zero_qc(self):
        assert cpt_undrained_strength_nc(0.0, 20.0) == pytest.approx(0.0, rel=1e-4)

    def test_qc_negative_raises(self):
        with pytest.raises(ValueError, match="qc must be non-negative"):
            cpt_undrained_strength_nc(-1.0, 20.0)

    def test_nc_not_positive_raises(self):
        with pytest.raises(ValueError, match="nc must be positive"):
            cpt_undrained_strength_nc(2000.0, 0.0)

    def test_nc_negative_raises(self):
        with pytest.raises(ValueError, match="nc must be positive"):
            cpt_undrained_strength_nc(2000.0, -5.0)


# ============================================================================
# Eq 8-24: cpt_undrained_strength_nk
# ============================================================================


class TestCptUndrainedStrengthNk:
    """Tests for Equation 8-24."""

    def test_basic(self):
        # qc=2000, sigma_v=100, Nk=15: su = (2000-100)/15 = 1900/15 = 126.667
        expected = 1900.0 / 15.0
        assert cpt_undrained_strength_nk(2000.0, 100.0, 15.0) == pytest.approx(
            expected, rel=1e-4
        )

    def test_nk_not_positive_raises(self):
        with pytest.raises(ValueError, match="nk must be positive"):
            cpt_undrained_strength_nk(2000.0, 100.0, 0.0)

    def test_nk_negative_raises(self):
        with pytest.raises(ValueError, match="nk must be positive"):
            cpt_undrained_strength_nk(2000.0, 100.0, -1.0)


# ============================================================================
# Eq 8-25: cpt_undrained_strength_nkt
# ============================================================================


class TestCptUndrainedStrengthNkt:
    """Tests for Equation 8-25."""

    def test_basic(self):
        # qt=2500, sigma_v=120, Nkt=15: su = (2500-120)/15 = 2380/15 = 158.667
        expected = 2380.0 / 15.0
        assert cpt_undrained_strength_nkt(2500.0, 120.0, 15.0) == pytest.approx(
            expected, rel=1e-4
        )

    def test_nkt_not_positive_raises(self):
        with pytest.raises(ValueError, match="nkt must be positive"):
            cpt_undrained_strength_nkt(2500.0, 120.0, 0.0)

    def test_nkt_negative_raises(self):
        with pytest.raises(ValueError, match="nkt must be positive"):
            cpt_undrained_strength_nkt(2500.0, 120.0, -1.0)


# ============================================================================
# Eq 8-26: spt_undrained_strength_stroud_butler
# ============================================================================


class TestSptUndrainedStrengthStroudButler:
    """Tests for Equation 8-26."""

    def test_basic(self):
        # Eq. 8-26 as printed, PDF p. 456 (printed p. 428):
        # su/N = 8910/PI^3 + 4.36, su in kPa
        # N=20, PI=30: su = 20 * (8910/27000 + 4.36) = 20 * 4.69 = 93.8 kPa
        assert spt_undrained_strength_stroud_butler(20.0, 30.0) == pytest.approx(
            93.8, abs=0.01
        )

    def test_low_plasticity(self):
        # PDF p. 456 (printed p. 428).
        # N=10, PI=15: su = 10 * (8910/3375 + 4.36) = 10 * 7.00 = 70.0 kPa
        assert spt_undrained_strength_stroud_butler(10.0, 15.0) == pytest.approx(
            70.0, abs=0.01
        )

    def test_zero_n(self):
        assert spt_undrained_strength_stroud_butler(0.0, 30.0) == pytest.approx(
            0.0, rel=1e-4
        )

    def test_negative_n_raises(self):
        with pytest.raises(ValueError, match="n must be non-negative"):
            spt_undrained_strength_stroud_butler(-1.0, 30.0)

    def test_pi_not_positive_raises(self):
        with pytest.raises(ValueError, match="pi must be positive"):
            spt_undrained_strength_stroud_butler(20.0, 0.0)

    def test_pi_negative_raises(self):
        with pytest.raises(ValueError, match="pi must be positive"):
            spt_undrained_strength_stroud_butler(20.0, -5.0)

    def test_range_of_figure_8_31(self):
        # Figure 8-31, PDF p. 456 (printed p. 428), draws the trendline from
        # PI 15 (su/N 7.0) to about PI 62 (su/N 4.40); outside it the
        # function refuses.
        # N=20, PI=15:   20 * (8910/3375 + 4.36) = 20 * 7.00 = 140.00 kPa
        # N=20, PI=15.1: 20 * (8910/3442.951 + 4.36) = 20 * 6.94790 = 138.96
        # N=20, PI=61.9: 20 * (8910/237176.659 + 4.36) = 20 * 4.39757 = 87.95
        # N=20, PI=62:   20 * (8910/238328 + 4.36) = 20 * 4.39739 = 87.95
        assert spt_undrained_strength_stroud_butler(20.0, 15.0) == pytest.approx(
            140.00, abs=0.01)
        assert spt_undrained_strength_stroud_butler(20.0, 15.1) == pytest.approx(
            138.96, abs=0.01)
        assert spt_undrained_strength_stroud_butler(20.0, 61.9) == pytest.approx(
            87.95, abs=0.01)
        assert spt_undrained_strength_stroud_butler(20.0, 62.0) == pytest.approx(
            87.95, abs=0.01)
        for pi in (14.9, 62.1, 5.0):
            # PI 5 used to return 1,513 kPa at N 20
            with pytest.raises(ValueError, match="outside 15 to 62"):
                spt_undrained_strength_stroud_butler(20.0, pi)


# ============================================================================
# Eq 8-27: intrinsic_compression_index
# ============================================================================


class TestIntrinsicCompressionIndex:
    """Tests for Equation 8-27."""

    def test_basic(self):
        # e*100=1.2, e*1000=0.8: C*c = 1.2 - 0.8 = 0.4
        assert intrinsic_compression_index(1.2, 0.8) == pytest.approx(0.4, rel=1e-4)

    def test_equal_raises(self):
        with pytest.raises(ValueError, match="e_star_100 must be greater than e_star_1000"):
            intrinsic_compression_index(1.0, 1.0)

    def test_inverted_raises(self):
        with pytest.raises(ValueError, match="e_star_100 must be greater than e_star_1000"):
            intrinsic_compression_index(0.5, 1.0)


# ============================================================================
# Eq 8-28: void_index
# ============================================================================


class TestVoidIndex:
    """Tests for Equation 8-28."""

    def test_basic(self):
        # e=1.5, e*100=1.2, C*c=0.4: Iv = (1.5-1.2)/0.4 = 0.3/0.4 = 0.75
        assert void_index(1.5, 1.2, 0.4) == pytest.approx(0.75, rel=1e-4)

    def test_negative_result(self):
        # e=0.8, e*100=1.2, C*c=0.4: Iv = (0.8-1.2)/0.4 = -1.0
        assert void_index(0.8, 1.2, 0.4) == pytest.approx(-1.0, rel=1e-4)

    def test_c_star_c_not_positive_raises(self):
        with pytest.raises(ValueError, match="c_star_c must be positive"):
            void_index(1.5, 1.2, 0.0)

    def test_c_star_c_negative_raises(self):
        with pytest.raises(ValueError, match="c_star_c must be positive"):
            void_index(1.5, 1.2, -0.1)


# ============================================================================
# Eq 8-29: intrinsic_void_ratio_at_100kpa
# ============================================================================


class TestIntrinsicVoidRatioAt100kpa:
    """Tests for Equation 8-29."""

    def test_basic(self):
        # eL=1.5: e*100 = 0.109 + 0.679*1.5 - 0.089*1.5^2 + 0.016*1.5^3
        # = 0.109 + 1.0185 - 0.089*2.25 + 0.016*3.375
        # = 0.109 + 1.0185 - 0.20025 + 0.054 = 0.98125
        expected = 0.109 + 0.679 * 1.5 - 0.089 * 1.5 ** 2 + 0.016 * 1.5 ** 3
        assert intrinsic_void_ratio_at_100kpa(1.5) == pytest.approx(expected, rel=1e-4)

    def test_zero(self):
        # eL=0: e*100 = 0.109
        assert intrinsic_void_ratio_at_100kpa(0.0) == pytest.approx(0.109, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="e_l must be non-negative"):
            intrinsic_void_ratio_at_100kpa(-0.1)


# ============================================================================
# Eq 8-30: intrinsic_compression_index_from_el
# ============================================================================


class TestIntrinsicCompressionIndexFromEl:
    """Tests for Equation 8-30."""

    def test_basic(self):
        # eL=1.5: C*c = 0.256*1.5 - 0.04 = 0.384 - 0.04 = 0.344
        assert intrinsic_compression_index_from_el(1.5) == pytest.approx(0.344, rel=1e-4)

    def test_zero(self):
        # eL=0: C*c = -0.04
        assert intrinsic_compression_index_from_el(0.0) == pytest.approx(-0.04, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="e_l must be non-negative"):
            intrinsic_compression_index_from_el(-0.1)


# ============================================================================
# Eq 8-31: constrained_modulus_linear
# ============================================================================


class TestConstrainedModulusLinear:
    """Tests for Equation 8-31."""

    def test_basic(self):
        # m=10, sigma_v_eff=50: Mds = 10*50 = 500
        assert constrained_modulus_linear(10.0, 50.0) == pytest.approx(500.0, rel=1e-4)

    def test_zero_stress(self):
        assert constrained_modulus_linear(10.0, 0.0) == pytest.approx(0.0, rel=1e-4)

    def test_zero_modulus_number(self):
        assert constrained_modulus_linear(0.0, 50.0) == pytest.approx(0.0, rel=1e-4)

    def test_m_negative_raises(self):
        with pytest.raises(ValueError, match="m must be non-negative"):
            constrained_modulus_linear(-1.0, 50.0)

    def test_sigma_v_eff_negative_raises(self):
        with pytest.raises(ValueError, match="sigma_v_eff must be non-negative"):
            constrained_modulus_linear(10.0, -1.0)


# ============================================================================
# Eq 8-32: constrained_modulus_nonlinear
# ============================================================================


class TestConstrainedModulusNonlinear:
    """Tests for Equation 8-32."""

    def test_basic(self):
        # m=10, sigma_v_eff=100, pa=101.325
        # Mds = 10 * 101.325 * (100/101.325)^0.5
        # = 1013.25 * (0.98692)^0.5 = 1013.25 * 0.99345 = 1006.61
        expected = 10.0 * 101.325 * (100.0 / 101.325) ** 0.5
        assert constrained_modulus_nonlinear(10.0, 100.0, 101.325) == pytest.approx(
            expected, rel=1e-4
        )

    def test_zero_stress(self):
        # sigma_v_eff=0: (0/pa)^0.5 = 0 => Mds = 0
        assert constrained_modulus_nonlinear(10.0, 0.0, 101.325) == pytest.approx(
            0.0, rel=1e-4
        )

    def test_m_negative_raises(self):
        with pytest.raises(ValueError, match="m must be non-negative"):
            constrained_modulus_nonlinear(-1.0, 100.0, 101.325)

    def test_sigma_v_eff_negative_raises(self):
        with pytest.raises(ValueError, match="sigma_v_eff must be non-negative"):
            constrained_modulus_nonlinear(10.0, -1.0, 101.325)

    def test_pa_not_positive_raises(self):
        with pytest.raises(ValueError, match="pa must be positive"):
            constrained_modulus_nonlinear(10.0, 100.0, 0.0)

    def test_pa_negative_raises(self):
        with pytest.raises(ValueError, match="pa must be positive"):
            constrained_modulus_nonlinear(10.0, 100.0, -1.0)


# ============================================================================
# Eq 8-33: constrained_modulus_spt
# ============================================================================


class TestConstrainedModulusSpt:
    """Tests for Equation 8-33."""

    def test_basic(self):
        # f=5, N=20, pa=101.325: Mds = 5*20*101.325 = 10132.5
        assert constrained_modulus_spt(5.0, 20.0, 101.325) == pytest.approx(
            10132.5, rel=1e-4
        )

    def test_zero_n(self):
        assert constrained_modulus_spt(5.0, 0.0, 101.325) == pytest.approx(0.0, rel=1e-4)

    def test_f_negative_raises(self):
        with pytest.raises(ValueError, match="f must be non-negative"):
            constrained_modulus_spt(-1.0, 20.0, 101.325)

    def test_n_negative_raises(self):
        with pytest.raises(ValueError, match="n must be non-negative"):
            constrained_modulus_spt(5.0, -1.0, 101.325)

    def test_pa_not_positive_raises(self):
        with pytest.raises(ValueError, match="pa must be positive"):
            constrained_modulus_spt(5.0, 20.0, 0.0)

    def test_pa_negative_raises(self):
        with pytest.raises(ValueError, match="pa must be positive"):
            constrained_modulus_spt(5.0, 20.0, -1.0)


# ============================================================================
# Eq 8-34: constrained_modulus_cpt
# ============================================================================


class TestConstrainedModulusCpt:
    """Tests for Equation 8-34."""

    def test_basic(self):
        # alpha=2.5, qc=4000: Mds = 2.5*4000 = 10000
        assert constrained_modulus_cpt(2.5, 4000.0) == pytest.approx(10000.0, rel=1e-4)

    def test_zero_qc(self):
        assert constrained_modulus_cpt(2.5, 0.0) == pytest.approx(0.0, rel=1e-4)

    def test_zero_alpha(self):
        assert constrained_modulus_cpt(0.0, 4000.0) == pytest.approx(0.0, rel=1e-4)

    def test_alpha_negative_raises(self):
        with pytest.raises(ValueError, match="alpha must be non-negative"):
            constrained_modulus_cpt(-1.0, 4000.0)

    def test_qc_negative_raises(self):
        with pytest.raises(ValueError, match="qc must be non-negative"):
            constrained_modulus_cpt(2.5, -1.0)


# ============================================================================
# Eq 8-35: secondary_compression_ratio
# ============================================================================


class TestSecondaryCompressionRatio:
    """Tests for Equation 8-35."""

    def test_basic(self):
        # wn=40: C_ea = 0.0001*40 = 0.004
        assert secondary_compression_ratio(40.0) == pytest.approx(0.004, rel=1e-4)

    def test_zero(self):
        assert secondary_compression_ratio(0.0) == pytest.approx(0.0, rel=1e-4)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="wn must be non-negative"):
            secondary_compression_ratio(-1.0)


# ============================================================================
# Eq 8-36: drained_youngs_modulus_from_undrained
# ============================================================================


class TestDrainedYoungsModulusFromUndrained:
    """Tests for Equation 8-36."""

    def test_basic(self):
        # Eu=3000, nu=0.3: E = 2*(1+0.3)/3 * 3000 = 2*1.3/3 * 3000 = 0.86667*3000 = 2600
        expected = 2.0 * (1.0 + 0.3) / 3.0 * 3000.0
        assert drained_youngs_modulus_from_undrained(3000.0, 0.3) == pytest.approx(
            expected, rel=1e-4
        )

    def test_zero_eu(self):
        assert drained_youngs_modulus_from_undrained(0.0, 0.3) == pytest.approx(
            0.0, rel=1e-4
        )

    def test_nu_zero(self):
        # nu=0: E = 2*(1+0)/3 * 1000 = 2/3*1000 = 666.667
        expected = 2.0 / 3.0 * 1000.0
        assert drained_youngs_modulus_from_undrained(1000.0, 0.0) == pytest.approx(
            expected, rel=1e-4
        )

    def test_eu_negative_raises(self):
        with pytest.raises(ValueError, match="eu must be non-negative"):
            drained_youngs_modulus_from_undrained(-1.0, 0.3)

    def test_nu_at_minus_one_raises(self):
        with pytest.raises(ValueError, match="nu must be in the range"):
            drained_youngs_modulus_from_undrained(1000.0, -1.0)

    def test_nu_at_half_raises(self):
        with pytest.raises(ValueError, match="nu must be in the range"):
            drained_youngs_modulus_from_undrained(1000.0, 0.5)

    def test_nu_above_half_raises(self):
        with pytest.raises(ValueError, match="nu must be in the range"):
            drained_youngs_modulus_from_undrained(1000.0, 0.6)

    def test_nu_below_minus_one_raises(self):
        with pytest.raises(ValueError, match="nu must be in the range"):
            drained_youngs_modulus_from_undrained(1000.0, -1.5)


# ============================================================================
# Eq 8-37: cbr_from_dcp_power
# ============================================================================


class TestCbrFromDcpPower:
    """Tests for Equation 8-37."""

    def test_basic(self):
        # A=292, DCP=10, x=-1.12: CBR = 292 * 10^(-1.12)
        # 10^(-1.12) = 1/10^1.12 = 1/13.1826 = 0.07586
        # CBR = 292 * 0.07586 = 22.15
        expected = 292.0 * 10.0 ** (-1.12)
        assert cbr_from_dcp_power(292.0, 10.0, -1.12) == pytest.approx(expected, rel=1e-4)

    def test_positive_exponent(self):
        # A=10, DCP=2, x=1.5: CBR = 10 * 2^1.5 = 10 * 2.8284 = 28.284
        expected = 10.0 * 2.0 ** 1.5
        assert cbr_from_dcp_power(10.0, 2.0, 1.5) == pytest.approx(expected, rel=1e-4)

    def test_a_negative_raises(self):
        with pytest.raises(ValueError, match="a_coeff must be non-negative"):
            cbr_from_dcp_power(-1.0, 10.0, -1.12)

    def test_dcp_not_positive_raises(self):
        with pytest.raises(ValueError, match="dcp must be positive"):
            cbr_from_dcp_power(292.0, 0.0, -1.12)

    def test_dcp_negative_raises(self):
        with pytest.raises(ValueError, match="dcp must be positive"):
            cbr_from_dcp_power(292.0, -1.0, -1.12)


# ============================================================================
# Eq 8-38: cbr_from_dcp_nazzal
# ============================================================================


class TestCbrFromDcpNazzal:
    """Tests for Equation 8-38."""

    def test_basic(self):
        # Eq. 8-38 as printed, PDF p. 484 (printed p. 456):
        # CBR = 2559 / (DCP^1.84 - 7.35) + 1
        # DCP=20: 20^1.84 = 247.67; 2559/240.32 + 1 = 11.648
        assert cbr_from_dcp_nazzal(20.0) == pytest.approx(11.648, abs=1e-3)

    def test_ends_of_stated_range(self):
        # PDF p. 484 (printed p. 456): "DCP values between 6.3 and 67 mm/blow"
        # DCP=6.3: 6.3^1.84 = 29.566; 2559/22.216 + 1 = 116.19
        # DCP=67: 67^1.84 = 2290.7; 2559/2283.4 + 1 = 2.1207
        assert cbr_from_dcp_nazzal(6.3) == pytest.approx(116.19, abs=0.01)
        assert cbr_from_dcp_nazzal(67.0) == pytest.approx(2.1207, abs=1e-3)

    def test_dcp_10(self):
        # DCP=10: 10^1.84 = 69.183; 2559/61.833 + 1 = 42.386
        assert cbr_from_dcp_nazzal(10.0) == pytest.approx(42.386, abs=1e-3)

    def test_outside_stated_range_raises(self):
        # The denominator passes through zero at DCP = 7.35^(1/1.84) = 2.96
        with pytest.raises(ValueError, match="outside 6.3 to 67 mm/blow"):
            cbr_from_dcp_nazzal(3.0)
        with pytest.raises(ValueError, match="outside 6.3 to 67 mm/blow"):
            cbr_from_dcp_nazzal(80.0)

    def test_dcp_not_positive_raises(self):
        with pytest.raises(ValueError, match="dcp must be positive"):
            cbr_from_dcp_nazzal(0.0)

    def test_dcp_negative_raises(self):
        with pytest.raises(ValueError, match="dcp must be positive"):
            cbr_from_dcp_nazzal(-5.0)


# ============================================================================
# Eq 8-39: cbr_from_spt
# ============================================================================


class TestCbrFromSpt:
    """Tests for Equation 8-39."""

    def test_basic(self):
        # Eq. 8-39 as printed, PDF p. 485 (printed p. 457):
        # log CBR = -5.13 + 6.55 [log(300/N)]^-0.26
        # N=10: log(30) = 1.47712; 1.47712^-0.26 = 0.90355
        # log CBR = -5.13 + 5.9183 = 0.7883; CBR = 6.141
        assert cbr_from_spt(10.0) == pytest.approx(6.141, abs=1e-3)

    def test_against_figure_8_57(self):
        # Figure 8-57, PDF p. 486 (printed p. 458), plots the same curve:
        # about 26 at N = 30 and about 160 at N = 68.
        # N=30: log(10) = 1; log CBR = -5.13 + 6.55 = 1.42; CBR = 26.30
        assert cbr_from_spt(30.0) == pytest.approx(26.30, abs=0.01)
        assert cbr_from_spt(68.0) == pytest.approx(160.0, abs=5.0)

    def test_n_not_positive_raises(self):
        with pytest.raises(ValueError, match="n must be positive"):
            cbr_from_spt(0.0)

    def test_n_negative_raises(self):
        with pytest.raises(ValueError, match="n must be positive"):
            cbr_from_spt(-5.0)

    def test_n_300_or_more_raises(self):
        # Outside the curve of Figure 8-57, and log(300/N) is not positive.
        with pytest.raises(ValueError, match="outside 5 to 68.*300 or more"):
            cbr_from_spt(300.0)

    def test_range_of_figure_8_57(self):
        # Figure 8-57, PDF p. 486 (printed p. 458), draws the curve from
        # N 5 to N 68 (read off a 400 dpi render); outside it the function
        # refuses.
        # N=5:    log(60) = 1.778151;   ^-0.26 = 0.861010; log CBR = 0.509615
        #         CBR = 3.233
        # N=5.1:  log(58.824) = 1.769551; ^-0.26 = 0.862096; CBR = 3.287
        # N=67.9: log(4.4183) = 0.645251; ^-0.26 = 1.120651; CBR = 162.28
        # N=68:   log(4.4118) = 0.644612; ^-0.26 = 1.120940; CBR = 162.99
        assert cbr_from_spt(5.0) == pytest.approx(3.233, abs=1e-3)
        assert cbr_from_spt(5.1) == pytest.approx(3.287, abs=1e-3)
        assert cbr_from_spt(67.9) == pytest.approx(162.28, abs=0.01)
        assert cbr_from_spt(68.0) == pytest.approx(162.99, abs=0.01)
        for n in (4.9, 68.1, 200.0):
            # N 200 used to return 144,025
            with pytest.raises(ValueError, match="outside 5 to 68"):
                cbr_from_spt(n)


# ============================================================================
# Eq 8-40: hydraulic_conductivity_hazen
# ============================================================================


class TestHydraulicConductivityHazen:
    """Tests for Equation 8-40."""

    def test_basic(self):
        # D10=0.5, C=1.0: k = 1.0 * 0.5^2 = 0.25 cm/s
        assert hydraulic_conductivity_hazen(0.5) == pytest.approx(0.25, rel=1e-4)

    def test_with_custom_c(self):
        # D10=0.3, C=2.0: k = 2.0 * 0.3^2 = 2.0 * 0.09 = 0.18
        assert hydraulic_conductivity_hazen(0.3, c=2.0) == pytest.approx(0.18, rel=1e-4)

    def test_d10_not_positive_raises(self):
        with pytest.raises(ValueError, match="d10 must be positive"):
            hydraulic_conductivity_hazen(0.0)

    def test_d10_negative_raises(self):
        with pytest.raises(ValueError, match="d10 must be positive"):
            hydraulic_conductivity_hazen(-0.1)

    def test_c_not_positive_raises(self):
        with pytest.raises(ValueError, match="c must be positive"):
            hydraulic_conductivity_hazen(0.5, c=0.0)

    def test_c_negative_raises(self):
        with pytest.raises(ValueError, match="c must be positive"):
            hydraulic_conductivity_hazen(0.5, c=-1.0)


# ============================================================================
# Eq 8-41: hydraulic_conductivity_kozeny_carman
# ============================================================================


class TestHydraulicConductivityKozenyCarman:
    """Tests for Equation 8-41."""

    # Eq. 8-41 as printed, PDF p. 490 (printed p. 462), D in mm, k in cm/s:
    # k = 1.99e2 * [100% / sum(fi / (D_li^0.404 * D_si^0.596))]^2
    #     * (1/S^2) * (e^3/(1+e))

    def test_basic(self):
        # One fraction between the 0.425 mm and 0.25 mm sieves, e=0.6, S=6
        # D_eff = 0.425^0.404 * 0.25^0.596 = 0.70773 * 0.43770 = 0.30977 mm
        # 100% / sum = 0.30977; squared = 0.095958
        # k = 199 * 0.095958 * (1/36) * (0.216/1.6) = 0.07161 cm/s
        fractions = [(1.0, 0.425, 0.25)]
        assert hydraulic_conductivity_kozeny_carman(fractions, 0.6, 6.0) == pytest.approx(
            0.07161, abs=1e-5
        )

    def test_two_fractions(self):
        # 60% between 2.0 and 0.85 mm, 40% between 0.85 and 0.425 mm,
        # e=0.5, S=7
        # D_eff_1 = 2.0^0.404 * 0.85^0.596 = 1.20103
        # D_eff_2 = 0.85^0.404 * 0.425^0.596 = 0.56235
        # sum = 0.6/1.20103 + 0.4/0.56235 = 1.21087
        # k = 199 * (1/1.21087)^2 * (1/49) * (0.125/1.5) = 0.23082 cm/s
        fractions = [(0.6, 2.0, 0.85), (0.4, 0.85, 0.425)]
        assert hydraulic_conductivity_kozeny_carman(fractions, 0.5, 7.0) == pytest.approx(
            0.23082, abs=1e-5
        )

    def test_fractions_in_percent(self):
        # The print writes the numerator as 100%: the same grading given
        # in percent returns the same k.
        fractions = [(60.0, 2.0, 0.85), (40.0, 0.85, 0.425)]
        assert hydraulic_conductivity_kozeny_carman(fractions, 0.5, 7.0) == pytest.approx(
            0.23082, abs=1e-5
        )

    def test_same_as_equation_6_13(self):
        # Eq. 6-13 (PDF p. 328, printed p. 300) and Eq. 8-41 are printed
        # identically.
        from geotech_references.dm7_1.chapter6 import (
            kozeny_carman_hydraulic_conductivity,
        )
        fractions = [(0.6, 2.0, 0.85), (0.4, 0.85, 0.425)]
        assert hydraulic_conductivity_kozeny_carman(fractions, 0.5, 7.0) == pytest.approx(
            kozeny_carman_hydraulic_conductivity(fractions, 7.0, 0.5), rel=1e-12
        )

    def test_fractions_not_whole_grading_raises(self):
        with pytest.raises(ValueError, match="must add up to 1.0"):
            hydraulic_conductivity_kozeny_carman(
                [(0.5, 2.0, 0.85), (0.3, 0.85, 0.425)], 0.5, 6.0)

    def test_total_within_two_percent_used_as_given(self):
        # The library accepts a total within 2 % of 1.0 or 100 (its own
        # tolerance, not printed) and does not normalise it. Same sieves
        # as test_two_fractions, e=0.5, S=7, by the printed formula:
        # 0.6 + 0.38 = 0.98: sum = 0.6/1.20102 + 0.38/0.56235 = 1.17531
        #   k = 199 * (1/1.17531)^2 * (1/49) * (0.125/1.5) = 0.24500
        # 60 + 39 = 99 (percent): sum = 119.30968; k = 0.23775
        # 0.6 + 0.42 = 1.02: sum = 1.24644; k = 0.21784
        # 60 + 42 = 102: the same k as 1.02
        cases = [
            ([(0.6, 2.0, 0.85), (0.38, 0.85, 0.425)], 0.24500),
            ([(60.0, 2.0, 0.85), (39.0, 0.85, 0.425)], 0.23775),
            ([(0.6, 2.0, 0.85), (0.42, 0.85, 0.425)], 0.21784),
            ([(60.0, 2.0, 0.85), (42.0, 0.85, 0.425)], 0.21784),
        ]
        for fractions, k in cases:
            result = hydraulic_conductivity_kozeny_carman(fractions, 0.5, 7.0)
            assert result == pytest.approx(k, abs=1e-5)

    def test_total_more_than_two_percent_off_raises(self):
        # 0.97, 1.03, 97, 103 and a percent/decimal mix-up (60 + 0.4)
        for fractions in (
            [(0.6, 2.0, 0.85), (0.37, 0.85, 0.425)],
            [(0.6, 2.0, 0.85), (0.43, 0.85, 0.425)],
            [(60.0, 2.0, 0.85), (37.0, 0.85, 0.425)],
            [(60.0, 2.0, 0.85), (43.0, 0.85, 0.425)],
            [(60.0, 2.0, 0.85), (0.4, 0.85, 0.425)],
        ):
            with pytest.raises(ValueError, match="within 2 %"):
                hydraulic_conductivity_kozeny_carman(fractions, 0.5, 7.0)

    def test_e_negative_raises(self):
        with pytest.raises(ValueError, match="e must be non-negative"):
            hydraulic_conductivity_kozeny_carman([(1.0, 0.5, 0.25)], -0.1, 6.0)

    def test_s_not_positive_raises(self):
        with pytest.raises(ValueError, match="s must be positive"):
            hydraulic_conductivity_kozeny_carman([(1.0, 0.5, 0.25)], 0.65, 0.0)

    def test_sieve_not_positive_raises(self):
        with pytest.raises(ValueError, match="All sieve sizes.*must be positive"):
            hydraulic_conductivity_kozeny_carman([(1.0, 0.5, 0.0)], 0.65, 6.0)

    def test_sieve_negative_raises(self):
        with pytest.raises(ValueError, match="All sieve sizes.*must be positive"):
            hydraulic_conductivity_kozeny_carman([(1.0, -0.1, 0.25)], 0.65, 6.0)

    def test_empty_fractions_zero_sum_raises(self):
        # All fractions with fi=0 result in summation=0
        with pytest.raises(ValueError, match="Sum of fi/.* is zero"):
            hydraulic_conductivity_kozeny_carman([(0.0, 0.5, 0.25)], 0.65, 6.0)


# ============================================================================
# Eq 8-42: hydraulic_conductivity_carrier_beckman
# ============================================================================


class TestHydraulicConductivityCarrierBeckman:
    """Tests for Equation 8-42."""

    # Eq. 8-42 as printed, PDF p. 490 (printed p. 462), k in m/s:
    # k = 0.0174 {[e - 0.027 (PL - 0.242 PI)] / PI}^4.29 * 1/(1+e)

    def test_basic(self):
        # e=1.5, PL=25, PI=30
        # e - 0.027*(25 - 7.26) = 1.5 - 0.47898 = 1.02102
        # (1.02102/30)^4.29 = 0.034034^4.29 = 5.0339e-07
        # k = 0.0174 * 5.0339e-07 / 2.5 = 3.5036e-09 m/s
        assert hydraulic_conductivity_carrier_beckman(1.5, 25.0, 30.0) == pytest.approx(
            3.5036e-09, rel=1e-4, abs=0.0
        )

    def test_second_point(self):
        # e=2.0, PL=20, PI=20
        # e - 0.027*(20 - 4.84) = 2.0 - 0.40932 = 1.59068
        # (1.59068/20)^4.29 = 0.079534^4.29 = 1.9203e-05
        # k = 0.0174 * 1.9203e-05 / 3.0 = 1.1138e-07 m/s
        assert hydraulic_conductivity_carrier_beckman(2.0, 20.0, 20.0) == pytest.approx(
            1.1138e-07, rel=1e-4, abs=0.0
        )

    def test_void_ratio_too_low_raises(self):
        # e=0.3, PL=30, PI=10: 0.3 - 0.027*(30 - 2.42) = -0.4447
        with pytest.raises(ValueError, match="is not positive"):
            hydraulic_conductivity_carrier_beckman(0.3, 30.0, 10.0)

    def test_e_negative_raises(self):
        with pytest.raises(ValueError, match="e must be non-negative"):
            hydraulic_conductivity_carrier_beckman(-0.1, 25.0, 20.0)

    def test_pi_not_positive_raises(self):
        with pytest.raises(ValueError, match="pi must be positive"):
            hydraulic_conductivity_carrier_beckman(0.8, 25.0, 0.0)

    def test_pi_negative_raises(self):
        with pytest.raises(ValueError, match="pi must be positive"):
            hydraulic_conductivity_carrier_beckman(0.8, 25.0, -5.0)


# ============================================================================
# Eq 8-43: hydraulic_conductivity_benson_landfill
# ============================================================================


class TestHydraulicConductivityBensonLandfill:
    """Tests for Equation 8-43."""

    # Eq. 8-43 as printed, PDF p. 491 (printed p. 463), k in m/s:
    # ln k = -18.35 + 894/W - 0.08 PI - 2.87 [w/(gamma_w/gamma_d - 1/Gs)]
    #        + 0.32 sqrt(GC) + 0.02 CF

    def test_basic(self):
        # CF=30, GC=4, W=200 kN, PI=25, w=0.18, gamma_w=9.81, gamma_d=17.0,
        # Gs=2.70
        # bracket = 0.18 / (9.81/17.0 - 1/2.70) = 0.18 / 0.206688 = 0.870876
        # ln k = -18.35 + 4.47 - 2.0 - 2.87*0.870876 + 0.32*2 + 0.6
        #      = -17.13941;  k = 3.6012e-08 m/s
        result = hydraulic_conductivity_benson_landfill(
            cf=30.0, gc=4.0, w_compactor=200.0, pi=25.0, w=0.18,
            gamma_w=9.81, gamma_d=17.0, gs=2.70
        )
        assert result == pytest.approx(3.6012e-08, rel=1e-4, abs=0.0)

    def test_heavier_compactor_lower_k(self):
        # Same clay, W=400 kN: 894/W falls from 4.47 to 2.235
        # ln k = -17.13941 - 2.235 = -19.37441;  k = 3.8530e-09 m/s
        result = hydraulic_conductivity_benson_landfill(
            cf=30.0, gc=4.0, w_compactor=400.0, pi=25.0, w=0.18,
            gamma_w=9.81, gamma_d=17.0, gs=2.70
        )
        assert result == pytest.approx(3.8530e-09, rel=1e-4, abs=0.0)

    def test_no_gravel(self):
        # GC=0: the square-root term is zero
        # ln k = -17.13941 - 0.64 = -17.77941;  k = 1.8989e-08 m/s
        result = hydraulic_conductivity_benson_landfill(
            cf=30.0, gc=0.0, w_compactor=200.0, pi=25.0, w=0.18,
            gamma_w=9.81, gamma_d=17.0, gs=2.70
        )
        assert result == pytest.approx(1.8989e-08, rel=1e-4, abs=0.0)

    def test_gamma_d_not_positive_raises(self):
        with pytest.raises(ValueError, match="gamma_d must be positive"):
            hydraulic_conductivity_benson_landfill(
                cf=30.0, gc=0.05, w_compactor=300.0, pi=20.0, w=0.20,
                gamma_w=9.81, gamma_d=0.0, gs=2.70
            )

    def test_gamma_w_not_positive_raises(self):
        with pytest.raises(ValueError, match="gamma_w must be positive"):
            hydraulic_conductivity_benson_landfill(
                cf=30.0, gc=0.05, w_compactor=300.0, pi=20.0, w=0.20,
                gamma_w=0.0, gamma_d=17.0, gs=2.70
            )

    def test_gs_not_positive_raises(self):
        with pytest.raises(ValueError, match="gs must be positive"):
            hydraulic_conductivity_benson_landfill(
                cf=30.0, gc=0.05, w_compactor=300.0, pi=20.0, w=0.20,
                gamma_w=9.81, gamma_d=17.0, gs=0.0
            )

    def test_w_compactor_not_positive_raises(self):
        with pytest.raises(ValueError, match="w_compactor must be positive"):
            hydraulic_conductivity_benson_landfill(
                cf=30.0, gc=0.05, w_compactor=0.0, pi=20.0, w=0.20,
                gamma_w=9.81, gamma_d=17.0, gs=2.70
            )

    def test_void_ratio_nonpositive_raises(self):
        # gamma_w/gamma_d - 1/Gs <= 0 when gamma_d >= Gs*gamma_w
        # Gs=2.7, gamma_w=9.81 => Gs*gamma_w=26.487; gamma_d=27
        with pytest.raises(ValueError, match="void ratio is non-positive"):
            hydraulic_conductivity_benson_landfill(
                cf=30.0, gc=0.05, w_compactor=300.0, pi=20.0, w=0.20,
                gamma_w=9.81, gamma_d=27.0, gs=2.70
            )

    def test_w_given_in_percent_raises(self):
        # The page gives w no unit; the function takes a decimal. w=18.0
        # would make the bracket (the degree of saturation) 87.09 and k
        # below 1e-100 m/s.
        with pytest.raises(ValueError, match="not above 1.10"):
            hydraulic_conductivity_benson_landfill(
                cf=30.0, gc=4.0, w_compactor=200.0, pi=25.0, w=18.0,
                gamma_w=9.81, gamma_d=17.0, gs=2.70
            )

    def test_saturation_limit_is_1_10(self):
        # The guard refuses a saturation above 1.10 (the library's limit,
        # not printed): a little over 1.0 comes from scatter in measured
        # w, gamma_d and Gs. Same clay as test_basic, by the printed
        # equation, ln k = -14.64 - 2.87 * bracket (bracket = w/0.206688):
        # w=0.21:  bracket 1.01602; ln k = -17.55598; k = 2.3743e-08 m/s
        # w=0.227: bracket 1.09827; ln k = -17.79204; k = 1.8751e-08 m/s
        # w=0.228: bracket 1.10311, refused
        for w, k in ((0.21, 2.3743e-08), (0.227, 1.8751e-08)):
            result = hydraulic_conductivity_benson_landfill(
                cf=30.0, gc=4.0, w_compactor=200.0, pi=25.0, w=w,
                gamma_w=9.81, gamma_d=17.0, gs=2.70
            )
            assert result == pytest.approx(k, rel=1e-4, abs=0.0)
        with pytest.raises(ValueError, match="1.103.*not above 1.10"):
            hydraulic_conductivity_benson_landfill(
                cf=30.0, gc=4.0, w_compactor=200.0, pi=25.0, w=0.228,
                gamma_w=9.81, gamma_d=17.0, gs=2.70
            )

    def test_docstring_first_line_gives_the_unit_taken(self):
        first = hydraulic_conductivity_benson_landfill.__doc__.strip().splitlines()[0]
        assert "molding water content taken as a decimal" in first
        assert "the page prints no unit for it" in first


# ============================================================================
# Eq 8-44: hydraulic_conductivity_benson_trast
# ============================================================================


class TestHydraulicConductivityBensonTrast:
    """Tests for Equation 8-44."""

    # Eq. 8-44 as printed, PDF p. 491 (printed p. 463), k in m/s:
    # ln k = -15 - 0.087 [w/(gamma_w/gamma_d - 1/Gs)] - 0.054 PI
    #        + 0.022 CF + 0.91 E
    # The page gives "w = molding water content" with no unit. The function
    # takes w as a decimal, as in Eq. 8-43, and enters the bracket (the
    # initial degree of saturation) in percent. That is the reading of the
    # review of 2026-11-10, not a printed statement (the docstring's Notes
    # give the reasons). These tests pin that reading and record the other.

    def test_basic_saturation_in_percent(self):
        # PI=25, CF=30, E=0 (standard Proctor), w=0.18, gamma_w=9.81,
        # gamma_d=17.0, Gs=2.70
        # bracket = 0.18 / (9.81/17.0 - 1/2.70) = 0.870876, or 87.0876 %
        # ln k = -15 - 0.087*87.0876 - 0.054*25 + 0.022*30 + 0.91*0
        #      = -15 - 7.57662 - 1.35 + 0.66 = -23.26662;  k = 7.8602e-11 m/s
        result = hydraulic_conductivity_benson_trast(
            pi=25.0, cf=30.0, e_effort=0.0, w=0.18,
            gamma_w=9.81, gamma_d=17.0, gs=2.70
        )
        assert result == pytest.approx(7.8602e-11, rel=1e-4, abs=0.0)

    def test_decimal_reading_is_not_what_is_returned(self):
        # With the bracket as a decimal: ln k = -15 - 0.087*0.870876 - 1.35
        # + 0.66 = -15.76577;  k = 1.4224e-07 m/s, about 1,800 times the
        # value returned (e^(0.087*(87.0876 - 0.870876)) = e^7.50085 = 1810).
        result = hydraulic_conductivity_benson_trast(
            pi=25.0, cf=30.0, e_effort=0.0, w=0.18,
            gamma_w=9.81, gamma_d=17.0, gs=2.70
        )
        assert result != pytest.approx(1.4224e-07, rel=1e-2, abs=0.0)
        assert 1.4224e-07 / result == pytest.approx(1810.0, rel=1e-2)

    def test_compactive_effort_index(self):
        # E = -1 modified, 0 standard, +1 reduced Proctor: each step in E
        # multiplies k by e^0.91 = 2.4843
        # modified: 7.8602e-11 / 2.4843 = 3.1639e-11
        # reduced:  7.8602e-11 * 2.4843 = 1.9527e-10
        modified = hydraulic_conductivity_benson_trast(
            pi=25.0, cf=30.0, e_effort=-1.0, w=0.18,
            gamma_w=9.81, gamma_d=17.0, gs=2.70
        )
        reduced = hydraulic_conductivity_benson_trast(
            pi=25.0, cf=30.0, e_effort=1.0, w=0.18,
            gamma_w=9.81, gamma_d=17.0, gs=2.70
        )
        assert modified == pytest.approx(3.1639e-11, rel=1e-4, abs=0.0)
        assert reduced == pytest.approx(1.9527e-10, rel=1e-4, abs=0.0)

    def test_w_given_in_percent_raises(self):
        # w=18.0 would be a saturation of 8,709 %
        with pytest.raises(ValueError, match="not above 110 %"):
            hydraulic_conductivity_benson_trast(
                pi=25.0, cf=30.0, e_effort=0.0, w=18.0,
                gamma_w=9.81, gamma_d=17.0, gs=2.70
            )

    def test_saturation_above_110_percent_raises(self):
        # w=0.30 at gamma_d=17.0: 0.30/0.206688 = 145.1 %
        with pytest.raises(ValueError, match="145.1 %"):
            hydraulic_conductivity_benson_trast(
                pi=25.0, cf=30.0, e_effort=0.0, w=0.30,
                gamma_w=9.81, gamma_d=17.0, gs=2.70
            )

    def test_saturation_limit_is_110_percent(self):
        # The guard refuses a saturation above 110 % (the library's limit,
        # not printed): a little over 100 % comes from scatter in measured
        # w, gamma_d and Gs. Same clay as test_basic, by the printed
        # equation with the bracket in percent, ln k = -15.69 - 0.087 * S%:
        # w=0.21:  S 101.602 %; ln k = -24.52939; k = 2.2234e-11 m/s
        # w=0.227: S 109.827 %; ln k = -25.24496; k = 1.0871e-11 m/s
        # w=0.228: S 110.311 %, refused
        for w, k in ((0.21, 2.2234e-11), (0.227, 1.0871e-11)):
            result = hydraulic_conductivity_benson_trast(
                pi=25.0, cf=30.0, e_effort=0.0, w=w,
                gamma_w=9.81, gamma_d=17.0, gs=2.70
            )
            assert result == pytest.approx(k, rel=1e-4, abs=0.0)
        with pytest.raises(ValueError, match="110.3 %.*not above 110 %"):
            hydraulic_conductivity_benson_trast(
                pi=25.0, cf=30.0, e_effort=0.0, w=0.228,
                gamma_w=9.81, gamma_d=17.0, gs=2.70
            )

    def test_zero_water_content_raises(self):
        with pytest.raises(ValueError, match="must be above 0"):
            hydraulic_conductivity_benson_trast(
                pi=25.0, cf=30.0, e_effort=0.0, w=0.0,
                gamma_w=9.81, gamma_d=17.0, gs=2.70
            )

    def test_void_ratio_nonpositive_raises(self):
        # gamma_d = 27 is above Gs*gamma_w = 26.487
        with pytest.raises(ValueError, match="void ratio is non-positive"):
            hydraulic_conductivity_benson_trast(
                pi=25.0, cf=30.0, e_effort=0.0, w=0.18,
                gamma_w=9.81, gamma_d=27.0, gs=2.70
            )

    def test_docstring_gives_the_printed_equation(self):
        doc = hydraulic_conductivity_benson_trast.__doc__
        assert "ln k = -15 - 0.087 * [ w / (gamma_w / gamma_d - 1 / Gs) ]" in doc
        assert "- 0.054 PI + 0.022 CF + 0.91 E" in doc

    def test_docstring_says_the_unit_is_a_reading_not_printed(self):
        doc = hydraulic_conductivity_benson_trast.__doc__
        first = doc.strip().splitlines()[0]
        assert "saturation term taken in percent" in first
        assert "not a printed statement" in first
        # both readings at the example above
        assert "k = 7.86e-11 m/s" in doc
        assert "k = 1.42e-07 m/s" in doc


# ============================================================================
# Eq 8-45: shear_wave_velocity_spt
# ============================================================================


class TestShearWaveVelocitySpt:
    """Tests for Equation 8-45."""

    def test_basic(self):
        # B=80, N=20, x=0.33: Vs = 80 * 20^0.33 * 1^0 = 80 * 2.6390 = 211.12
        expected = 80.0 * 20.0 ** 0.33
        assert shear_wave_velocity_spt(80.0, 20.0, 0.33) == pytest.approx(
            expected, rel=1e-4
        )

    def test_with_depth(self):
        # B=80, N=20, x=0.33, z=10, y=0.5: Vs = 80 * 20^0.33 * 10^0.5
        # = 80 * 2.6390 * 3.1623 = 667.55
        expected = 80.0 * 20.0 ** 0.33 * 10.0 ** 0.5
        assert shear_wave_velocity_spt(80.0, 20.0, 0.33, z=10.0, y=0.5) == pytest.approx(
            expected, rel=1e-4
        )

    def test_zero_n(self):
        # N=0: 0^x = 0 (for positive x) => Vs = 0
        assert shear_wave_velocity_spt(80.0, 0.0, 0.33) == pytest.approx(0.0, rel=1e-4)

    def test_default_depth(self):
        # z=1.0 (default), y=0.0 (default) => z^y = 1^0 = 1
        expected = 80.0 * 20.0 ** 0.33
        assert shear_wave_velocity_spt(80.0, 20.0, 0.33) == pytest.approx(
            expected, rel=1e-4
        )

    def test_b_negative_raises(self):
        with pytest.raises(ValueError, match="b must be non-negative"):
            shear_wave_velocity_spt(-1.0, 20.0, 0.33)

    def test_n_negative_raises(self):
        with pytest.raises(ValueError, match="n must be non-negative"):
            shear_wave_velocity_spt(80.0, -1.0, 0.33)

    def test_z_not_positive_raises(self):
        with pytest.raises(ValueError, match="z must be positive"):
            shear_wave_velocity_spt(80.0, 20.0, 0.33, z=0.0)

    def test_z_negative_raises(self):
        with pytest.raises(ValueError, match="z must be positive"):
            shear_wave_velocity_spt(80.0, 20.0, 0.33, z=-1.0)


# ============================================================================
# TABLE 8-6: table_8_6_stark_hussain
# ============================================================================


class TestTable86StarkHussain:
    """Tests for Table 8-6: Coefficients for Stark and Hussain (2013)
    Residual Friction Angle Correlation."""

    # Table 8-6 as printed, PDF p. 445 (printed p. 417): all 16 rows
    # (CF and LL range, effective normal stress, C0, C1, C2, C3).
    PRINTED = [
        ("lt_20", "50_kPa", 39.7, -0.29, 6.63e-04, 0.0),
        ("lt_20", "100_kPa", 39.4, -0.298, 6.81e-04, 0.0),
        ("lt_20", "400_kPa", 40.2, -0.375, 1.36e-03, 0.0),
        ("lt_20", "700_kPa", 40.3, -0.412, 1.68e-03, 0.0),
        ("25_to_45", "50_kPa", 31.4, -6.79e-03, -3.62e-03, 1.86e-05),
        ("25_to_45", "100_kPa", 29.8, -3.63e-04, -3.58e-03, 1.85e-05),
        ("25_to_45", "400_kPa", 28.4, -5.62e-02, -2.95e-03, 1.72e-05),
        ("25_to_45", "700_kPa", 28.1, -0.2083, -8.18e-04, 9.37e-06),
        ("gt_50_ll_lt_120", "50_kPa", 33.5, -0.31, 3.90e-04, 4.40e-06),
        ("gt_50_ll_lt_120", "100_kPa", 30.7, -0.2504, -4.21e-04, 8.05e-06),
        ("gt_50_ll_lt_120", "400_kPa", 29.4, -0.2621, -4.01e-04, 8.72e-06),
        ("gt_50_ll_lt_120", "700_kPa", 27.7, -0.3233, 2.90e-04, 7.11e-06),
        ("gt_50_ll_120_to_300", "50_kPa", 12.0, -0.0215, 0.0, 0.0),
        ("gt_50_ll_120_to_300", "100_kPa", 10.9, -0.0183, 0.0, 0.0),
        ("gt_50_ll_120_to_300", "400_kPa", 8.3, -0.0114, 0.0, 0.0),
        ("gt_50_ll_120_to_300", "700_kPa", 5.8, -0.0049, 0.0, 0.0),
    ]

    @pytest.mark.parametrize("cf_range, sigma, c0, c1, c2, c3", PRINTED)
    def test_printed_row(self, cf_range, sigma, c0, c1, c2, c3):
        result = table_8_6_stark_hussain(cf_range, sigma)
        assert result == {"c0": c0, "c1": c1, "c2": c2, "c3": c3}

    def test_sixteen_rows(self):
        from geotech_references.dm7_1 import chapter8
        assert len(chapter8._TABLE_8_6_STARK_HUSSAIN) == 16

    def test_returns_copy(self):
        # Modifying returned dict doesn't affect source
        result1 = table_8_6_stark_hussain("lt_20", "50_kPa")
        result1["c0"] = 999.0
        assert table_8_6_stark_hussain("lt_20", "50_kPa")["c0"] == 39.7

    def test_unknown_cf_raises(self):
        with pytest.raises(ValueError, match="Unknown combination"):
            table_8_6_stark_hussain("lt_10", "50_kPa")

    def test_unknown_sigma_raises(self):
        with pytest.raises(ValueError, match="Unknown combination"):
            table_8_6_stark_hussain("lt_20", "200_kPa")

    def test_ranges_the_manual_does_not_print_raise(self):
        # Keys of the earlier table: the print has no 20-50% group and
        # splits CF > 50% by liquid limit.
        for cf_range in ["20_to_50", "gt_50"]:
            with pytest.raises(ValueError, match="Unknown combination"):
                table_8_6_stark_hussain(cf_range, "100_kPa")


# ============================================================================
# TABLE 8-9: table_8_9_shansep_m
# ============================================================================


class TestTable89ShansepM:
    """Tests for Table 8-9: Typical Values of m."""

    # Table 8-9 as printed, PDF p. 453 (printed p. 425): rows that print
    # one number for m.
    @pytest.mark.parametrize("soil, m, source", [
        ("saturated_clay", 0.8, "Sabatini et al. (2002)"),
        ("sensitive_cemented_marine_clay", 1.00, "Ladd and DeGroot (2004)"),
        ("homogeneous_cl_ch_sedimentary_clay", 0.8, "Ladd and DeGroot (2004)"),
        ("varved_clay_dss", 0.75, "Ladd and DeGroot (2004)"),
        ("silt_organic_below_a_line", 0.8, "Ladd and DeGroot (2004)"),
    ])
    def test_printed_number(self, soil, m, source):
        row = table_8_9_shansep_m(soil)
        assert row["m"] == m
        assert row["source"] == source

    def test_nominal_rows_carry_the_printed_expression(self):
        # PDF p. 453 (printed p. 425): 0.88 (1 - Cr/Cc) +/- 0.06, Nominally 0.8
        for soil in ["homogeneous_cl_ch_sedimentary_clay",
                     "silt_organic_below_a_line"]:
            row = table_8_9_shansep_m(soil)
            assert row["m_as_printed"] == "0.88 (1 - Cr/Cc) +/- 0.06; Nominally 0.8"

    def test_theoretical_row_has_no_number(self):
        # Roscoe et al. (1958), Mitachi and Kitago (1976): m ~ 1 - Cr/Cc
        row = table_8_9_shansep_m("theoretical")
        assert row["m"] is None
        assert "1 - Cr/Cc" in row["m_as_printed"]
        assert row["soil_description"] == "Saturated clay (theoretical)"

    def test_field_vane_row_is_a_range(self):
        # Jamiolkowski et al. (1985), Chandler (1988): Range 0.8 to 1.35,
        # High value 1.51, Mean (all) 1.03, Mean (discarding extreme
        # values) 0.97
        row = table_8_9_shansep_m("field_vane")
        assert row["m"] is None
        for text in ["0.8 to 1.35", "1.51", "1.03", "0.97"]:
            assert text in row["m_as_printed"]
        assert row["soil_description"] == "Field vane shear tests on clay"

    def test_seven_rows(self):
        from geotech_references.dm7_1 import chapter8
        assert len(chapter8._TABLE_8_9_SHANSEP_M) == 7

    def test_case_insensitive(self):
        assert table_8_9_shansep_m(" Varved_Clay_DSS ")["m"] == 0.75

    def test_returns_copy(self):
        row = table_8_9_shansep_m("varved_clay_dss")
        row["m"] = 9.0
        assert table_8_9_shansep_m("varved_clay_dss")["m"] == 0.75

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown soil"):
            table_8_9_shansep_m("unknown_test")

    def test_test_types_the_manual_does_not_print_raise(self):
        # Keys of the earlier table: Table 8-9 does not list m by test type.
        for test_type in ["ciuc", "ck0uc", "dss", "ck0ue"]:
            with pytest.raises(ValueError, match="not by test type"):
                table_8_9_shansep_m(test_type)


# ============================================================================
# TABLE 8-24: table_8_24_cbr_dcp
# ============================================================================


class TestTable824CbrDcp:
    """Tests for Table 8-24: CBR Correlations with DCP."""

    # Table 8-24 as printed, PDF p. 484 (printed p. 456): all 13 rows.
    PRINTED = [
        ("gabr_2000", 25.0, -0.55),
        ("feleke_araya_2016_fine_a47", 47.0, -0.90),
        ("george_2009", 47.0, -0.79),
        ("white_2018_cl_cbr_lt_10", 59.0, -2.00),
        ("feleke_araya_2016_coarse_a90", 90.0, -1.17),
        ("feleke_araya_2016_fine_a104", 104.0, -0.91),
        ("feleke_araya_2016_coarse_a157", 157.0, -0.85),
        ("george_kumar_2018", 246.0, -1.35),
        ("white_2018_all_except_cl_cbr_lt_10", 292.0, -1.12),
        ("smith_pratt_1983", 363.0, -1.15),
        ("harrison_1986_clay_dcp_lt_10", 501.0, -1.12),
        ("harrison_1986_clay_dcp_gt_10", 363.0, -1.16),
        ("kleyn_van_heerden_1983", 425.0, -1.27),
    ]

    @pytest.mark.parametrize("source, a, x", PRINTED)
    def test_printed_row(self, source, a, x):
        result = table_8_24_cbr_dcp(source)
        assert result["a"] == a
        assert result["x"] == x

    def test_thirteen_rows(self):
        from geotech_references.dm7_1 import chapter8
        assert len(chapter8._TABLE_8_24_CBR_DCP) == 13
        assert set(chapter8._TABLE_8_24_CBR_DCP) == {r[0] for r in self.PRINTED}

    def test_reference_as_printed(self):
        result = table_8_24_cbr_dcp("harrison_1986_clay_dcp_lt_10")
        assert result["reference"] == (
            "Harrison (1986), clay-like soils with DCP < 10 mm/blow")

    def test_case_insensitive(self):
        assert table_8_24_cbr_dcp(" Gabr_2000 ")["a"] == 25.0

    def test_returns_copy(self):
        # Modifying returned dict doesn't affect source
        result1 = table_8_24_cbr_dcp("gabr_2000")
        result1["a"] = 999.0
        assert table_8_24_cbr_dcp("gabr_2000")["a"] == 25.0

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown source"):
            table_8_24_cbr_dcp("unknown_source")

    def test_rows_the_manual_does_not_print_raise(self):
        # Keys of the earlier table, none of which is a row of Table 8-24.
        for source in ["webster_1992", "ese_2006", "livneh_2000",
                       "harrison_1987", "chua_1988", "pen_2002"]:
            with pytest.raises(ValueError, match="Unknown source"):
                table_8_24_cbr_dcp(source)


# ============================================================================
# FIGURE 8-46: figure_8_46_f
# ============================================================================


class TestFigure846F:
    """Tests for Figure 8-46: Variation of Empirical Coefficient f used
    for Calculating Constrained Modulus with PI (after Stroud 1974)."""

    # Read off the curve of Figure 8-46, PDF p. 472 (printed p. 444);
    # axes PI 10 to 70 and f 3 to 8. Tolerance 0.05 = a tenth of a
    # division of the f axis.
    @pytest.mark.parametrize("pi, f", [
        (15.0, 6.75),   # start of the curve
        (17.0, 6.10),
        (20.0, 5.51),
        (25.0, 4.98),   # the curve crosses f = 5 just below PI 25
        (30.0, 4.70),
        (40.0, 4.48),
        (50.0, 4.39),
        (60.0, 4.29),
        (64.5, 4.24),   # end of the curve
    ])
    def test_read_off_points(self, pi, f):
        assert figure_8_46_f(pi) == pytest.approx(f, abs=0.05)

    def test_between_points(self):
        # PI=35 lies between the read-off points at 34 (4.56) and 36 (4.54)
        assert figure_8_46_f(35.0) == pytest.approx(4.55, abs=0.05)

    def test_f_is_of_order_five_not_hundreds(self):
        # The f axis of Figure 8-46 runs from 3 to 8.
        for pi in [15.0, 20.0, 30.0, 45.0, 64.5]:
            assert 3.0 < figure_8_46_f(pi) < 8.0

    def test_falls_with_plasticity(self):
        values = [figure_8_46_f(p) for p in [15.0, 20.0, 30.0, 40.0, 50.0, 64.0]]
        assert values == sorted(values, reverse=True)

    def test_below_curve_raises(self):
        # The curve starts at PI 15
        with pytest.raises(ValueError, match="outside 15 to 64.5"):
            figure_8_46_f(10.0)

    def test_above_curve_raises(self):
        # The curve ends at PI 64.5
        with pytest.raises(ValueError, match="outside 15 to 64.5"):
            figure_8_46_f(80.0)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="pi must be non-negative"):
            figure_8_46_f(-1.0)


# ===========================================================================
# Ranges the manual states or plots (dm71-25)
# ============================================================================


class TestPrintedRanges:
    """A value outside the range the manual states or plots is refused."""

    def test_kulhawy_mayne_axes_of_figure_8_3(self):
        # Figure 8-3 (bottom), PDF p. 426 (printed p. 398): N60 0 to 60,
        # sigma'v 0 to 3.0 kgf/cm2; Kulhawy and Mayne (1990) approximated
        # its trends as Eq. 8-4. 3.0 kgf/cm2 = 294.2 kPa.
        # N60=60, sigma'v=294 kPa, Pa=101.325: 60/(12.2 + 20.3*2.9015) =
        # 0.84391; ^0.34 = 0.94394; atan = 43.35 deg (between the figure's
        # 40 and 45 degree curves at that point)
        assert spt_friction_angle_kulhawy_mayne(60.0, 294.0, 101.325) == pytest.approx(
            43.35, abs=0.01)
        with pytest.raises(ValueError, match="above 60"):
            spt_friction_angle_kulhawy_mayne(61.0, 100.0, 101.325)

    def test_kulhawy_mayne_stress_limit_is_three_atmospheres(self):
        # The stress axis of Figure 8-3 (bottom), PDF p. 426 (printed
        # p. 398), ends at 3.0 kgf/cm2 (294.2 kPa, 2.90 atm); the function
        # refuses sigma'v/Pa above 3.0, a few percent over it, so a caller
        # who gives Pa as 100 kPa is not refused at 291 kPa.
        # N60=20, Pa=100: 291 kPa -> 20/(12.2 + 20.3*2.91) = 0.280611;
        # ^0.34 = 0.649166; atan = 32.99 deg
        # 300 kPa (ratio 3.0, the limit) -> 20/73.1 = 0.273598; ^0.34 =
        # 0.643603; atan = 32.77 deg
        # 300 kPa with Pa=101.325 (ratio 2.961) -> 32.86 deg
        assert spt_friction_angle_kulhawy_mayne(20.0, 291.0, 100.0) == pytest.approx(
            32.99, abs=0.01)
        assert spt_friction_angle_kulhawy_mayne(20.0, 300.0, 100.0) == pytest.approx(
            32.77, abs=0.01)
        assert spt_friction_angle_kulhawy_mayne(20.0, 300.0, 101.325) == pytest.approx(
            32.86, abs=0.01)
        with pytest.raises(ValueError, match="above 3.0"):
            spt_friction_angle_kulhawy_mayne(20.0, 301.0, 100.0)
        with pytest.raises(ValueError, match="3.0 kgf/cm2"):
            spt_friction_angle_kulhawy_mayne(20.0, 305.0, 101.325)

    def test_wolff_and_hatanaka_uchida_axis_of_figure_8_4(self):
        # Figure 8-4, PDF p. 427 (printed p. 399), plots both for N1,60
        # from 0 to 60, ending near 43 and 50 degrees.
        # Wolff: 27.1 + 0.3*60 - 0.00054*3600 = 43.16
        # Hatanaka and Uchida: sqrt(15.4*60) + 20 = 50.40
        assert spt_friction_angle_wolff(60.0) == pytest.approx(43.16, abs=0.01)
        assert spt_friction_angle_hatanaka_uchida(60.0) == pytest.approx(50.40, abs=0.01)
        with pytest.raises(ValueError, match="above 60"):
            spt_friction_angle_wolff(61.0)
        with pytest.raises(ValueError, match="above 60"):
            spt_friction_angle_hatanaka_uchida(61.0)

    def test_gibson_axis_of_figure_8_13(self):
        # Figure 8-13, PDF p. 436 (printed p. 408), plots both Gibson
        # equations for PI from 0 to 100; the residual curve ends just
        # under 10 degrees.
        # PI=100: 0.084*100^1.4 - 75 + 31.9 = 53.0 - 75 + 31.9 = 9.90
        assert residual_friction_angle_gibson(100.0) == pytest.approx(9.90, abs=0.01)
        with pytest.raises(ValueError, match="above 100"):
            residual_friction_angle_gibson(101.0)
        with pytest.raises(ValueError, match="above 100"):
            fully_softened_friction_angle(101.0)

    def test_hazen_stated_range(self):
        # PDF p. 486 (printed p. 458): "developed for saturated clean sands
        # with a fines content less than 5% and D10 values ranging from
        # 0.1 mm to 3 mm". k = C D10^2: 0.01 cm/s at 0.1 mm, 9 cm/s at 3 mm
        assert hydraulic_conductivity_hazen(0.1) == pytest.approx(0.01, abs=1e-9)
        assert hydraulic_conductivity_hazen(3.0) == pytest.approx(9.0, abs=1e-9)
        with pytest.raises(ValueError, match="outside 0.1 to 3 mm"):
            hydraulic_conductivity_hazen(0.05)
        with pytest.raises(ValueError, match="outside 0.1 to 3 mm"):
            hydraulic_conductivity_hazen(5.0)


# ===========================================================================
# INTEGRATION & PUBLISHED REFERENCE VALUES
# ===========================================================================

class TestTable86Integration:
    """Chain table_8_6 → residual_friction_angle_stark_hussain."""

    # Table 8-6 and Eq. 8-17, PDF p. 445 (printed p. 417); the curves are
    # drawn in Figure 8-22, PDF p. 444 (printed p. 416).

    def _phi_r(self, cf_range, sigma, ll):
        coeffs = table_8_6_stark_hussain(cf_range, sigma)
        return residual_friction_angle_stark_hussain(
            ll, coeffs["c0"], coeffs["c1"], coeffs["c2"], coeffs["c3"]
        )

    def test_lt20_50kpa_ll75(self):
        # CF < 20%, 50 kPa, LL = 75:
        # 39.7 - 0.29*75 + 6.63e-4*5625 = 39.7 - 21.75 + 3.729 = 21.68
        # (Figure 8-22 shows about 21 at the end of that curve)
        assert self._phi_r("lt_20", "50_kPa", 75.0) == pytest.approx(21.68, abs=0.01)

    def test_25_to_45_100kpa_ll60(self):
        # 25% < CF < 45%, 100 kPa, LL = 60:
        # 29.8 - 3.63e-4*60 - 3.58e-3*3600 + 1.85e-5*216000
        # = 29.8 - 0.022 - 12.888 + 3.996 = 20.89
        assert self._phi_r("25_to_45", "100_kPa", 60.0) == pytest.approx(20.89, abs=0.01)

    def test_gt50_400kpa_ll80(self):
        # CF > 50% and LL < 120, 400 kPa, LL = 80:
        # 29.4 - 0.2621*80 - 4.01e-4*6400 + 8.72e-6*512000
        # = 29.4 - 20.968 - 2.566 + 4.465 = 10.33
        assert self._phi_r("gt_50_ll_lt_120", "400_kPa", 80.0) == pytest.approx(10.33, abs=0.01)

    def test_gt50_high_ll_against_figure_8_22(self):
        # CF > 50% and 120 < LL < 300, LL = 280: Figure 8-22 shows about
        # 6 degrees at 50 kPa and about 4.5 degrees at 700 kPa.
        # 12.0 - 0.0215*280 = 5.98;  5.8 - 0.0049*280 = 4.43
        assert self._phi_r("gt_50_ll_120_to_300", "50_kPa", 280.0) == pytest.approx(5.98, abs=0.01)
        assert self._phi_r("gt_50_ll_120_to_300", "700_kPa", 280.0) == pytest.approx(4.43, abs=0.01)

    def test_increasing_ll_decreases_phi_r(self):
        # For same clay fraction/stress, increasing LL decreases phi_r
        assert self._phi_r("25_to_45", "100_kPa", 80.0) < self._phi_r("25_to_45", "100_kPa", 40.0)


class TestTable89Integration:
    """Chain table_8_9 → undrained_strength_ratio_oc."""

    def test_nominal_m_ocr4(self):
        # Table 8-9, PDF p. 453 (printed p. 425): nominally 0.8.
        # (su/sv)NC = 0.22, OCR = 4: 0.22 * 4^0.8 = 0.22 * 3.0314 = 0.6669
        m = table_8_9_shansep_m("homogeneous_cl_ch_sedimentary_clay")["m"]
        su_ratio = undrained_strength_ratio_oc(0.22, 4.0, m)
        assert su_ratio == pytest.approx(0.6669, abs=1e-4)

    def test_varved_clay_ocr4(self):
        # Northeastern U.S. varved clays, DSS: m = 0.75
        # 0.22 * 4^0.75 = 0.22 * 2.8284 = 0.6223
        m = table_8_9_shansep_m("varved_clay_dss")["m"]
        su_ratio = undrained_strength_ratio_oc(0.22, 4.0, m)
        assert su_ratio == pytest.approx(0.6223, abs=1e-4)


class TestTable824Integration:
    """Chain table_8_24 → cbr_from_dcp_power."""

    def test_harrison_dcp8(self):
        # Table 8-24, PDF p. 484 (printed p. 456): Harrison (1986), clay-like
        # soils with DCP < 10 mm/blow: CBR = 501 * DCP^(-1.12)
        # DCP=8: 8^1.12 = 10.267; 501/10.267 = 48.80
        coeffs = table_8_24_cbr_dcp("harrison_1986_clay_dcp_lt_10")
        cbr = cbr_from_dcp_power(coeffs["a"], 8.0, coeffs["x"])
        assert cbr == pytest.approx(48.80, abs=0.01)

    def test_gabr_dcp25(self):
        # Gabr et al. (2000): CBR = 25 * DCP^(-0.55)
        # DCP=25: 25^0.55 = 5.8731; 25/5.8731 = 4.257
        coeffs = table_8_24_cbr_dcp("gabr_2000")
        cbr = cbr_from_dcp_power(coeffs["a"], 25.0, coeffs["x"])
        assert cbr == pytest.approx(4.257, abs=1e-3)

    def test_all_rows_give_positive_cbr(self):
        # For DCP=15 mm/blow, every row gives a positive CBR
        from geotech_references.dm7_1 import chapter8
        for source in chapter8._TABLE_8_24_CBR_DCP:
            coeffs = table_8_24_cbr_dcp(source)
            cbr = cbr_from_dcp_power(coeffs["a"], 15.0, coeffs["x"])
            assert cbr > 0.0, f"Negative CBR for {source}: {cbr}"


class TestFigure846Integration:
    """Chain figure_8_46_f → constrained_modulus_spt."""

    def test_pi20_n15(self):
        # Figure 8-46, PDF p. 472 (printed p. 444): f = 5.51 at PI 20.
        # Eq. 8-33, PDF p. 470 (printed p. 442): Mds = f N Pa
        # N=15, Pa=100 kPa: Mds = 5.51 * 15 * 100 = 8265 kPa
        f = figure_8_46_f(20.0)
        M_ds = constrained_modulus_spt(f, 15.0, 100.0)
        assert M_ds == pytest.approx(8265.0, rel=0.01)

    def test_higher_pi_lower_modulus(self):
        # Higher PI → lower f → lower constrained modulus
        f_low_pi = figure_8_46_f(15.0)
        f_high_pi = figure_8_46_f(60.0)
        M_low = constrained_modulus_spt(f_low_pi, 20.0, 101.3)
        M_high = constrained_modulus_spt(f_high_pi, 20.0, 101.3)
        assert M_high < M_low


# ===========================================================================
# Plot function smoke tests
# ===========================================================================

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as _plt


class TestPlotFigure846:
    """Smoke tests for plot_figure_8_46 (f vs PI curve)."""

    def test_no_query(self):
        ax = plot_figure_8_46(show=False)
        assert isinstance(ax, matplotlib.axes.Axes)
        _plt.close("all")

    def test_query_point(self):
        ax = plot_figure_8_46(PI=30.0, show=False)
        assert isinstance(ax, matplotlib.axes.Axes)
        _plt.close("all")
