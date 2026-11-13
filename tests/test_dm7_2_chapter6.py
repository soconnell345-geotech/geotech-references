"""Comprehensive tests for geotech.dm7_2.chapter6 -- Deep Foundations.

Tests every public function (77 total) with valid inputs, edge cases, and
ValueError checks for all validation branches.
"""

import math

import pytest

from geotech_references.dm7_2.chapter6 import *


# ==========================================================================
# 1. critical_scour_velocity  (Eq 6-1)
# ==========================================================================

def test_critical_scour_velocity_basic():
    # D50 = 2.0 mm => vc = 0.35 * 2.0^0.45
    # 2.0^0.45 = exp(0.45*ln2) = exp(0.45*0.693147) = exp(0.311916) = 1.36604
    expected = 0.35 * 2.0 ** 0.45
    assert critical_scour_velocity(2.0) == pytest.approx(expected, rel=1e-4)


def test_critical_scour_velocity_D50_equals_1():
    # D50=1 => 0.35 * 1^0.45 = 0.35
    assert critical_scour_velocity(1.0) == pytest.approx(0.35, rel=1e-4)


def test_critical_scour_velocity_refuses_below_sand_size():
    # PDF p. 409 (printed p. 371): "Equation 6-1 should not be extrapolated
    # below sand-sized particles"; Glossary, PDF p. 719 (printed p. 681):
    # "Sand-sized - Particle size between 0.075 mm and 4.75 mm."
    for d50 in (0.074, 0.05, 0.002):
        with pytest.raises(ValueError, match="below sand-sized particles"):
            critical_scour_velocity(d50)
    # D50 = 0.075 mm: 0.35 x 0.075^0.45 = 0.35 x 0.3117 = 0.1091 m/s
    assert critical_scour_velocity(0.075) == pytest.approx(0.1091, abs=0.0001)
    # D50 = 0.5 mm: 0.35 x 0.7320 = 0.2562 m/s; gravel sizes are not refused
    assert critical_scour_velocity(0.5) == pytest.approx(0.2562, abs=0.0001)
    assert critical_scour_velocity(20.0) > critical_scour_velocity(4.75)


def test_critical_scour_velocity_raises_zero():
    with pytest.raises(ValueError, match="D50 must be positive"):
        critical_scour_velocity(0.0)


def test_critical_scour_velocity_raises_negative():
    with pytest.raises(ValueError, match="D50 must be positive"):
        critical_scour_velocity(-1.0)


# ==========================================================================
# 2. pile_impedance  (Eq 6-2)
# ==========================================================================

def test_pile_impedance_basic():
    # I = E*A/c = 30000*10/5000 = 60
    assert pile_impedance(30000.0, 10.0, 5000.0) == pytest.approx(60.0, rel=1e-4)


def test_pile_impedance_raises_E_zero():
    with pytest.raises(ValueError, match="E must be positive"):
        pile_impedance(0.0, 10.0, 5000.0)


def test_pile_impedance_raises_A_negative():
    with pytest.raises(ValueError, match="A must be positive"):
        pile_impedance(30000.0, -1.0, 5000.0)


def test_pile_impedance_raises_c_zero():
    with pytest.raises(ValueError, match="c must be positive"):
        pile_impedance(30000.0, 10.0, 0.0)


# ==========================================================================
# 3. nominal_axial_resistance  (Eq 6-3)
# ==========================================================================

def test_nominal_axial_resistance_basic():
    assert nominal_axial_resistance(100.0, 50.0) == pytest.approx(150.0, rel=1e-4)


def test_nominal_axial_resistance_zero_shaft():
    assert nominal_axial_resistance(0.0, 200.0) == pytest.approx(200.0, rel=1e-4)


def test_nominal_axial_resistance_zero_base():
    assert nominal_axial_resistance(300.0, 0.0) == pytest.approx(300.0, rel=1e-4)


# ==========================================================================
# 4. nominal_shaft_resistance  (Eq 6-4)
# ==========================================================================

def test_nominal_shaft_resistance_single_segment():
    # f_s=10, A_s=5 => R_s = 50
    assert nominal_shaft_resistance([(10.0, 5.0)]) == pytest.approx(50.0, rel=1e-4)


def test_nominal_shaft_resistance_multiple_segments():
    # (10,5) + (20,3) = 50 + 60 = 110
    segs = [(10.0, 5.0), (20.0, 3.0)]
    assert nominal_shaft_resistance(segs) == pytest.approx(110.0, rel=1e-4)


def test_nominal_shaft_resistance_empty():
    assert nominal_shaft_resistance([]) == pytest.approx(0.0, rel=1e-4)


# ==========================================================================
# 5. nominal_base_resistance  (Eq 6-5)
# ==========================================================================

def test_nominal_base_resistance_basic():
    # q_b=100, A_b=2.5 => 250
    assert nominal_base_resistance(100.0, 2.5) == pytest.approx(250.0, rel=1e-4)


def test_nominal_base_resistance_zero_area():
    assert nominal_base_resistance(100.0, 0.0) == pytest.approx(0.0, rel=1e-4)


# ==========================================================================
# 6. beta_coefficient  (Eq 6-6)
# ==========================================================================

def test_beta_coefficient_basic():
    # K=1.0, delta=30 deg => 1.0 * tan(30) = 0.57735
    expected = 1.0 * math.tan(math.radians(30.0))
    assert beta_coefficient(1.0, 30.0) == pytest.approx(expected, rel=1e-4)


def test_beta_coefficient_zero_K():
    assert beta_coefficient(0.0, 45.0) == pytest.approx(0.0, rel=1e-4)


def test_beta_coefficient_raises_negative_K():
    with pytest.raises(ValueError, match="K must be non-negative"):
        beta_coefficient(-0.1, 30.0)


# ==========================================================================
# 7. beta_method_unit_shaft_resistance  (Eq 6-7)
# ==========================================================================

def test_beta_method_unit_shaft_resistance_basic():
    # beta=0.3, sigma_z_eff=100 => 30
    assert beta_method_unit_shaft_resistance(0.3, 100.0) == pytest.approx(30.0, rel=1e-4)


def test_beta_method_unit_shaft_resistance_zero_beta():
    assert beta_method_unit_shaft_resistance(0.0, 100.0) == pytest.approx(0.0, rel=1e-4)


# ==========================================================================
# 8. alpha_method_unit_shaft_resistance  (Eq 6-8)
# ==========================================================================

def test_alpha_method_unit_shaft_resistance_basic():
    # alpha=0.5, s_u=200 => 100
    assert alpha_method_unit_shaft_resistance(0.5, 200.0) == pytest.approx(100.0, rel=1e-4)


def test_alpha_method_unit_shaft_resistance_alpha_one():
    assert alpha_method_unit_shaft_resistance(1.0, 50.0) == pytest.approx(50.0, rel=1e-4)


# ==========================================================================
# 9. alpha_tomlinson_transition  (Eq 6-9)
# ==========================================================================

def test_alpha_tomlinson_transition_basic():
    # Eq 6-9 as printed (UFC 3-220-20 printed p. 416): alpha = 0.28 (s_u/P_a)^-0.44
    # s_u=100, P_a=100 => 0.28 * 1 = 0.28
    assert alpha_tomlinson_transition(100.0, 100.0) == pytest.approx(0.28, rel=1e-4)


def test_alpha_tomlinson_transition_ratio_2():
    # s_u=200, P_a=100 => 0.28*(2.0)^-0.44 = 0.28 * 0.73706 = 0.20638
    assert alpha_tomlinson_transition(200.0, 100.0) == pytest.approx(0.20638, abs=1e-4)


@pytest.mark.parametrize("ratio, expected", [
    (0.5, 0.28 * 0.5 ** -0.44),    # 0.37984
    (1.0, 0.28),
    (2.0, 0.28 * 2.0 ** -0.44),    # 0.20638
    (0.71, 0.28 * 0.71 ** -0.44),  # 0.32519
])
def test_alpha_tomlinson_transition_printed_form(ratio, expected):
    # coefficient 0.28 on the front, exponent -0.44 on the ratio (not swapped)
    assert alpha_tomlinson_transition(ratio * 100.0, 100.0) == pytest.approx(expected, rel=1e-9)
    assert expected == pytest.approx(0.28 * ratio ** (-0.44), rel=1e-12)


def test_alpha_tomlinson_transition_raises_su_zero():
    with pytest.raises(ValueError, match="s_u must be positive"):
        alpha_tomlinson_transition(0.0, 100.0)


def test_alpha_tomlinson_transition_raises_Pa_zero():
    with pytest.raises(ValueError, match="P_a must be positive"):
        alpha_tomlinson_transition(100.0, 0.0)


# ==========================================================================
# 10. alpha_chen_drilled_shaft  (Eq 6-10)
# ==========================================================================

def test_alpha_chen_drilled_shaft_basic():
    # s_u_ICU=100, P_a=100 => 0.3 + 0.17/(100/100) = 0.3 + 0.17 = 0.47
    assert alpha_chen_drilled_shaft(100.0, 100.0) == pytest.approx(0.47, rel=1e-4)


def test_alpha_chen_drilled_shaft_cap_at_1():
    # Very small s_u_ICU => large 0.17/ratio => capped at 1.0
    # s_u_ICU=1, P_a=100 => 0.3 + 0.17/(0.01) = 0.3 + 17 = 17.3 => capped at 1.0
    assert alpha_chen_drilled_shaft(1.0, 100.0) == pytest.approx(1.0, rel=1e-4)


def test_alpha_chen_drilled_shaft_raises_su_zero():
    with pytest.raises(ValueError, match="s_u_ICU must be positive"):
        alpha_chen_drilled_shaft(0.0, 100.0)


def test_alpha_chen_drilled_shaft_raises_Pa_zero():
    with pytest.raises(ValueError, match="P_a must be positive"):
        alpha_chen_drilled_shaft(100.0, 0.0)


# ==========================================================================
# 11. su_ICU_from_UC  (Eq 6-11)
# ==========================================================================

def test_su_ICU_from_UC_basic():
    # s_u_UC=50, OCR=1 => 1.74*50*1^-0.25 = 87.0
    assert su_ICU_from_UC(50.0, 1.0) == pytest.approx(87.0, rel=1e-4)


def test_su_ICU_from_UC_OCR_4():
    # OCR=4 => 4^-0.25 = 1/(4^0.25) = 1/sqrt(2) = 0.70711
    expected = 1.74 * 50.0 * 4.0 ** (-0.25)
    assert su_ICU_from_UC(50.0, 4.0) == pytest.approx(expected, rel=1e-4)


def test_su_ICU_from_UC_raises_OCR_zero():
    with pytest.raises(ValueError, match="OCR must be positive"):
        su_ICU_from_UC(50.0, 0.0)


def test_su_ICU_from_UC_raises_OCR_negative():
    with pytest.raises(ValueError, match="OCR must be positive"):
        su_ICU_from_UC(50.0, -1.0)


# ==========================================================================
# 12. su_ICU_from_UU  (Eq 6-12)
# ==========================================================================

def test_su_ICU_from_UU_basic():
    # s_u_UU=50, OCR=1 => 1.68*50*1^-0.25 = 84.0
    assert su_ICU_from_UU(50.0, 1.0) == pytest.approx(84.0, rel=1e-4)


def test_su_ICU_from_UU_OCR_16():
    # OCR=16 => 16^-0.25 = 1/2 = 0.5
    expected = 1.68 * 50.0 * 0.5
    assert su_ICU_from_UU(50.0, 16.0) == pytest.approx(expected, rel=1e-4)


def test_su_ICU_from_UU_raises_OCR_zero():
    with pytest.raises(ValueError, match="OCR must be positive"):
        su_ICU_from_UU(50.0, 0.0)


# ==========================================================================
# 13. su_ICU_from_DSS  (Eq 6-13)
# ==========================================================================

def test_su_ICU_from_DSS_basic():
    # s_u_DSS=100 => 1.43*100 = 143
    assert su_ICU_from_DSS(100.0) == pytest.approx(143.0, rel=1e-4)


def test_su_ICU_from_DSS_zero():
    assert su_ICU_from_DSS(0.0) == pytest.approx(0.0, rel=1e-4)


# ==========================================================================
# 14. alpha_salgado_drilled_shaft  (Eq 6-14)
# ==========================================================================

def test_alpha_salgado_drilled_shaft_basic():
    # s_u=100, P_a=100 => 0.4*(1 - 0.12*ln(1)) = 0.4*(1-0) = 0.4
    assert alpha_salgado_drilled_shaft(100.0, 100.0) == pytest.approx(0.4, rel=1e-4)


def test_alpha_salgado_drilled_shaft_ratio_e():
    # s_u/P_a = e => ln(e) = 1
    # alpha = 0.4*(1-0.12*1) = 0.4*0.88 = 0.352
    s_u = 100.0 * math.e
    assert alpha_salgado_drilled_shaft(s_u, 100.0) == pytest.approx(0.352, rel=1e-4)


def test_alpha_salgado_drilled_shaft_raises_su_zero():
    with pytest.raises(ValueError, match="s_u must be positive"):
        alpha_salgado_drilled_shaft(0.0, 100.0)


def test_alpha_salgado_drilled_shaft_raises_Pa_zero():
    with pytest.raises(ValueError, match="P_a must be positive"):
        alpha_salgado_drilled_shaft(100.0, 0.0)


# ==========================================================================
# 15. alpha_coleman_CFA  (Eq 6-15)
# ==========================================================================

def test_alpha_coleman_CFA_basic():
    # Curve E of Fig. 6-14 is 0.53 / (s_u/P_a): s_u=P_a => 0.53
    assert alpha_coleman_CFA(100.0, 100.0) == pytest.approx(0.53, rel=1e-4)


def test_alpha_coleman_CFA_ratio_half():
    # s_u=50, P_a=100 => 0.53 / 0.5 = 1.06 (Fig. 6-14 Curve E: 1.06 at 0.5)
    assert alpha_coleman_CFA(50.0, 100.0) == pytest.approx(1.06, rel=1e-4)


def test_alpha_coleman_CFA_curve_E_points():
    # Curve E read off the vector figure: 0.53 at 1.0, 0.41 at 1.3, 0.39 at 1.37
    assert alpha_coleman_CFA(130.0, 100.0) == pytest.approx(0.4077, abs=1e-3)
    assert alpha_coleman_CFA(142.0, 100.0) == pytest.approx(0.3732, abs=1e-3)


def test_alpha_coleman_CFA_refuses_outside_its_printed_range():
    # PDF p. 457 (printed p. 419): Eq. 6-15 "is valid for normalized
    # strengths in the range of 0.24 to 1.42"
    assert alpha_coleman_CFA(24.0, 100.0) == pytest.approx(0.53 / 0.24, rel=1e-9)   # 2.208
    assert alpha_coleman_CFA(0.24 * 101.325, 101.325) == pytest.approx(2.208, abs=0.001)
    assert alpha_coleman_CFA(1.42 * 2116.0, 2116.0) == pytest.approx(0.3732, abs=0.0001)
    for s_u in (23.0, 10.0, 143.0, 300.0):
        with pytest.raises(ValueError, match="0.24 to 1.42"):
            alpha_coleman_CFA(s_u, 100.0)


def test_alpha_coleman_CFA_raises_su_zero():
    with pytest.raises(ValueError, match="s_u must be positive"):
        alpha_coleman_CFA(0.0, 100.0)


def test_alpha_coleman_CFA_raises_Pa_zero():
    with pytest.raises(ValueError, match="P_a must be positive"):
        alpha_coleman_CFA(100.0, 0.0)


# ==========================================================================
# 16. alpha_API_P2A  (Eqs 6-16 / 6-17)
# ==========================================================================

def test_alpha_API_P2A_ratio_le_1():
    # Eq 6-16: alpha = 0.5 * ratio^-0.5. ratio=0.5 => 0.5*1.41421 = 0.70711
    assert alpha_API_P2A(50.0, 100.0) == pytest.approx(0.70711, rel=1e-4)


def test_alpha_API_P2A_capped_at_ratio_quarter():
    # printed: alpha capped at 1.0 when the ratio is below 0.25 (0.5*0.25^-0.5 = 1)
    assert alpha_API_P2A(25.0, 100.0) == pytest.approx(1.0, rel=1e-9)
    assert alpha_API_P2A(10.0, 100.0) == pytest.approx(1.0, rel=1e-9)


def test_alpha_API_P2A_ratio_equals_1():
    # ratio=1 => 0.5 (both Eq 6-16 and 6-17 give 0.5 here)
    assert alpha_API_P2A(100.0, 100.0) == pytest.approx(0.5, rel=1e-4)


def test_alpha_API_P2A_ratio_gt_1():
    # s_u=200, sigma=100 => ratio=2 > 1 => alpha = 0.5 * 2^-0.25 = 0.42045
    expected = 0.5 * 2.0 ** (-0.25)
    assert alpha_API_P2A(200.0, 100.0) == pytest.approx(expected, rel=1e-4)


def test_alpha_API_P2A_raises_sigma_zero():
    with pytest.raises(ValueError, match="sigma_z_eff must be positive"):
        alpha_API_P2A(100.0, 0.0)


# ==========================================================================
# 17. alpha_API_from_OCR  (Eqs 6-18 / 6-19)
# ==========================================================================

def test_alpha_API_from_OCR_le_4_5():
    # OCR=1 => 1.07*1^-0.4 = 1.07, but capped at 1.0
    assert alpha_API_from_OCR(1.0) == pytest.approx(1.0, rel=1e-4)


def test_alpha_API_from_OCR_boundary():
    # OCR=4.5 => 1.07*4.5^-0.4
    expected = min(1.07 * 4.5 ** (-0.4), 1.0)
    assert alpha_API_from_OCR(4.5) == pytest.approx(expected, rel=1e-4)


def test_alpha_API_from_OCR_gt_4_5():
    # OCR=10 => 0.73*10^-0.2
    expected = min(0.73 * 10.0 ** (-0.2), 1.0)
    assert alpha_API_from_OCR(10.0) == pytest.approx(expected, rel=1e-4)


def test_alpha_API_from_OCR_raises_zero():
    with pytest.raises(ValueError, match="OCR must be positive"):
        alpha_API_from_OCR(0.0)


def test_alpha_API_from_OCR_raises_negative():
    with pytest.raises(ValueError, match="OCR must be positive"):
        alpha_API_from_OCR(-2.0)


# ==========================================================================
# 18. unit_base_resistance_drained  (Eq 6-20)
# ==========================================================================

def test_unit_base_resistance_drained_basic():
    # N_q=40, sigma=100 => 4000
    assert unit_base_resistance_drained(40.0, 100.0) == pytest.approx(4000.0, rel=1e-4)


def test_unit_base_resistance_drained_zero_Nq():
    assert unit_base_resistance_drained(0.0, 100.0) == pytest.approx(0.0, rel=1e-4)


# ==========================================================================
# 19. cheng_Nq  (Table 6-17)
# ==========================================================================

def test_cheng_Nq_basic():
    # Table 6-17, PDF p. 459 (printed p. 421): the equation under the table,
    # Nq = 1.2 (Z/b)^-0.437 exp[6.34 (Z/b)^0.0486 tan phi'] <= 200.
    # phi = 30, Z/b = 20: 1.2 x 20^-0.437 x exp(6.34 x 20^0.0486 x 0.57735)
    # = 1.2 x 0.27005 x exp(4.2337) = 22.36  (the table prints 22)
    assert cheng_Nq(30.0, 20.0) == pytest.approx(22.36, abs=0.01)
    # phi = 35, Z/b = 20: 55.05
    assert cheng_Nq(35.0, 20.0) == pytest.approx(55.05, abs=0.01)


@pytest.mark.parametrize("phi, printed", [
    # Table 6-17 (PDF p. 459, printed p. 421), the ends of each soil's
    # friction angle range and the Nq the table prints at Z/b = 10, 20, 40.
    (25.0, (12, 10, 8)),     # Clay, 25 to 30 degrees: 12-26, 10-22, 8-19
    (30.0, (26, 22, 19)),
    (28.0, (19, 16, 14)),    # Silt, 28 to 34 degrees: 19-52, 16-46, 14-40
    (34.0, (52, 46, 40)),
    (32.0, (37, 32, 27)),    # Sand, 32 to 40 degrees: 37-168, 32-152, 27-139
    (40.0, (168, 152, 139)),
])
def test_cheng_Nq_reproduces_table_6_17(phi, printed):
    for z_over_b, n_q in zip((10.0, 20.0, 40.0), printed):
        # the table prints whole numbers
        assert cheng_Nq(phi, z_over_b) == pytest.approx(n_q, abs=0.5)


def test_cheng_Nq_cap_at_200():
    # Table 6-17 prints the equation with "<= 200 unless supported by
    # project-specific information".  phi = 45, Z/b = 10: the equation
    # gives 527.
    assert cheng_Nq(45.0, 10.0) == 200.0
    assert cheng_Nq(50.0, 100.0) == 200.0


def test_cheng_Nq_raises_phi_zero():
    with pytest.raises(ValueError, match="phi_deg must be between 0 and 90"):
        cheng_Nq(0.0, 10.0)


def test_cheng_Nq_raises_Z_over_b_zero():
    # Section 6-5.4.3.1 and Table 6-17 are for deep foundation elements,
    # Z/b >= 5 (PDF p. 459, printed p. 421)
    with pytest.raises(ValueError, match="Z/b >= 5"):
        cheng_Nq(30.0, 0.0)
    with pytest.raises(ValueError, match="Z/b >= 5"):
        cheng_Nq(30.0, 4.9)
    assert cheng_Nq(30.0, 5.0) > 0.0


# ==========================================================================
# 20. unit_base_resistance_vesic_drained  (Eq 6-21)
# ==========================================================================

def test_unit_base_resistance_vesic_drained_basic():
    # N_q_star=50, sigma_m=80 => 4000
    assert unit_base_resistance_vesic_drained(50.0, 80.0) == pytest.approx(4000.0, rel=1e-4)


# ==========================================================================
# 21. mean_effective_stress  (Eq 6-22)
# ==========================================================================

def test_mean_effective_stress_basic():
    # Eq. 6-22, PDF p. 460 (printed p. 422):
    # sigma'_m = (1 - (2/3) sin phi') sigma'_zD+b/2
    # sigma = 100, phi = 30: (1 - (2/3)(0.5)) x 100 = 66.667
    assert mean_effective_stress(100.0, 30.0) == pytest.approx(66.667, abs=0.001)
    # phi = 35: (1 - (2/3)(0.57358)) x 100 = 61.76
    assert mean_effective_stress(100.0, 35.0) == pytest.approx(61.76, abs=0.01)


def test_mean_effective_stress_phi_0():
    # phi = 0: (1 - 0) x 100 = 100
    assert mean_effective_stress(100.0, 0.0) == pytest.approx(100.0, rel=1e-9)


# ==========================================================================
# 22. vesic_Nq_star  (Eq 6-23)
# ==========================================================================

def test_vesic_Nq_star_basic():
    # Eq. 6-23, PDF p. 460 (printed p. 422):
    # N*q = [3 / (3 - sin phi)] e^[(pi/2 - phi) tan phi]
    #       tan^2(pi/4 + phi/2) Irr^[4 sin phi / (3 (1 + sin phi))]
    # phi = 30, Irr = 50: 3/2.5 = 1.2; e^(1.0472 x 0.57735) = 1.8305;
    # tan^2(60 deg) = 3; 50^(2/4.5) = 5.690; product 37.50
    assert vesic_Nq_star(30.0, 50.0) == pytest.approx(37.50, abs=0.01)
    # phi = 35, Irr = 100: 83.78; phi = 40, Irr = 200: 193.1
    assert vesic_Nq_star(35.0, 100.0) == pytest.approx(83.78, abs=0.01)
    assert vesic_Nq_star(40.0, 200.0) == pytest.approx(193.1, abs=0.1)


def test_vesic_Nq_star_raises_Irr_zero():
    with pytest.raises(ValueError, match="I_rr must be positive"):
        vesic_Nq_star(30.0, 0.0)


def test_vesic_Nq_star_raises_Irr_negative():
    with pytest.raises(ValueError, match="I_rr must be positive"):
        vesic_Nq_star(30.0, -5.0)


# ==========================================================================
# 23. rigidity_index  (Eq 6-24)
# ==========================================================================

def test_rigidity_index_basic():
    # E=1000, nu=0.3, sigma_m=50, phi=30
    # denom = (1+0.6)*50*tan(30) = 1.6*50*0.57735 = 46.188
    # Ir = 1000 / 46.188 = 21.651
    phi_rad = math.radians(30.0)
    denom = (1.0 + 2.0 * 0.3) * 50.0 * math.tan(phi_rad)
    expected = 1000.0 / denom
    assert rigidity_index(1000.0, 0.3, 50.0, 30.0) == pytest.approx(expected, rel=1e-4)


def test_rigidity_index_raises_denom_zero():
    # phi=0 => tan(0)=0 => denom=0
    with pytest.raises(ValueError, match="Denominator must be positive"):
        rigidity_index(1000.0, 0.3, 50.0, 0.0)


# ==========================================================================
# 24. reduced_rigidity_index  (Eq 6-25)
# ==========================================================================

def test_reduced_rigidity_index_basic():
    # I_r=100, eps_v=0.01 => 100/(1+100*0.01) = 100/2 = 50
    assert reduced_rigidity_index(100.0, 0.01) == pytest.approx(50.0, rel=1e-4)


def test_reduced_rigidity_index_zero_strain():
    # eps_v=0 => Irr = Ir
    assert reduced_rigidity_index(100.0, 0.0) == pytest.approx(100.0, rel=1e-4)


# ==========================================================================
# 25. volumetric_strain  (Eq 6-26)
# ==========================================================================

def test_volumetric_strain_basic():
    # q_b_app=200, E_s=10000, F_nu=0.5 => 200*0.5/10000 = 0.01
    assert volumetric_strain(200.0, 10000.0, 0.5) == pytest.approx(0.01, rel=1e-4)


def test_volumetric_strain_raises_Es_zero():
    with pytest.raises(ValueError, match="E_s must be positive"):
        volumetric_strain(200.0, 0.0, 0.5)


def test_volumetric_strain_raises_Es_negative():
    with pytest.raises(ValueError, match="E_s must be positive"):
        volumetric_strain(200.0, -100.0, 0.5)


# ==========================================================================
# 26. unit_base_resistance_undrained  (Eq 6-27)
# ==========================================================================

def test_unit_base_resistance_undrained_basic():
    # N_c_star=9, s_u=50 => 450
    assert unit_base_resistance_undrained(9.0, 50.0) == pytest.approx(450.0, rel=1e-4)


def test_unit_base_resistance_undrained_zero_su():
    assert unit_base_resistance_undrained(9.0, 0.0) == pytest.approx(0.0, rel=1e-4)


# ==========================================================================
# 27. vesic_Nc_star  (Eq 6-28)
# ==========================================================================

def test_vesic_Nc_star_basic():
    # I_rr=50 => (4/3)*(ln50+1) + pi/2 + 1
    # ln(50) = 3.91202
    # (4/3)*(3.91202+1) = (4/3)*4.91202 = 6.54936
    # + pi/2 + 1 = 6.54936 + 1.5708 + 1 = 9.12016
    expected = (4.0 / 3.0) * (math.log(50.0) + 1.0) + math.pi / 2.0 + 1.0
    assert vesic_Nc_star(50.0) == pytest.approx(expected, rel=1e-4)


def test_vesic_Nc_star_Irr_1():
    # I_rr=1 => (4/3)*(0+1) + pi/2 + 1 = 1.3333 + 1.5708 + 1 = 3.9041
    expected = 4.0 / 3.0 + math.pi / 2.0 + 1.0
    assert vesic_Nc_star(1.0) == pytest.approx(expected, rel=1e-4)


def test_vesic_Nc_star_raises_Irr_zero():
    with pytest.raises(ValueError, match="I_rr must be positive"):
        vesic_Nc_star(0.0)


# ==========================================================================
# 28. undrained_rigidity_index  (Eq 6-29)
# ==========================================================================

def test_undrained_rigidity_index_basic():
    # E_u=300, s_u=2 => 300/(3*2) = 50
    assert undrained_rigidity_index(300.0, 2.0) == pytest.approx(50.0, rel=1e-4)


def test_undrained_rigidity_index_raises_su_zero():
    with pytest.raises(ValueError, match="s_u must be positive"):
        undrained_rigidity_index(300.0, 0.0)


def test_undrained_rigidity_index_raises_su_negative():
    with pytest.raises(ValueError, match="s_u must be positive"):
        undrained_rigidity_index(300.0, -1.0)


# ==========================================================================
# 29. Nc_star_FHWA_from_Ir  (Eq 6-30)
# ==========================================================================

def test_Nc_star_FHWA_from_Ir_basic():
    # Eq. 6-30, PDF p. 462 (printed p. 424): N*c = 1.33 [ln(Ir) + 1] <= 9
    # Ir = 50: 1.33 x (3.9120 + 1) = 6.533
    assert Nc_star_FHWA_from_Ir(50.0) == pytest.approx(6.533, abs=0.001)
    # Ir = 100: 1.33 x 5.6052 = 7.455; Ir = 300: 1.33 x 6.7038 = 8.916
    assert Nc_star_FHWA_from_Ir(100.0) == pytest.approx(7.455, abs=0.001)
    assert Nc_star_FHWA_from_Ir(300.0) == pytest.approx(8.916, abs=0.001)


def test_Nc_star_FHWA_from_Ir_cap_at_9():
    # Ir = 1000: 1.33 x (6.9078 + 1) = 10.52, limited to 9 as printed
    assert Nc_star_FHWA_from_Ir(1000.0) == 9.0


def test_Nc_star_FHWA_from_Ir_raises_zero():
    with pytest.raises(ValueError, match="I_r must be positive"):
        Nc_star_FHWA_from_Ir(0.0)


# ==========================================================================
# 30. Nc_star_FHWA_from_su  (Eq 6-31)
# ==========================================================================

def test_Nc_star_FHWA_from_su_basic():
    # Eq. 6-31, PDF p. 462 (printed p. 424):
    # N*c = 10.2 - 12.4 [0.1 / (0.1 + su/Pa)] <= 9
    # su/Pa = 0.5: 10.2 - 12.4 x (0.1 / 0.6) = 10.2 - 2.0667 = 8.133
    assert Nc_star_FHWA_from_su(50.0, 100.0) == pytest.approx(8.133, abs=0.001)
    # su/Pa = 0.25: 10.2 - 12.4 x (0.1 / 0.35) = 10.2 - 3.5429 = 6.657
    assert Nc_star_FHWA_from_su(25.0, 100.0) == pytest.approx(6.657, abs=0.001)
    # su/Pa = 0.9: 10.2 - 12.4 x (0.1 / 1.0) = 8.96
    assert Nc_star_FHWA_from_su(90.0, 100.0) == pytest.approx(8.96, abs=0.001)


def test_Nc_star_FHWA_from_su_cap_at_9():
    # The equation is for su below 2 ksf, "otherwise N*c = 9".  It reaches
    # 9 at su/Pa = 0.933 (about 2 ksf); su/Pa = 2 gives 9.61, limited to 9.
    assert Nc_star_FHWA_from_su(200.0, 100.0) == 9.0
    assert Nc_star_FHWA_from_su(100000.0, 100.0) == 9.0
    # su = 2 ksf with Pa = 2.116 ksf
    assert Nc_star_FHWA_from_su(2.0, 2.116) == 9.0


def test_Nc_star_FHWA_from_su_raises_negative_su():
    with pytest.raises(ValueError, match="s_u must be non-negative"):
        Nc_star_FHWA_from_su(-1.0, 100.0)


def test_Nc_star_FHWA_from_su_raises_Pa_zero():
    with pytest.raises(ValueError, match="P_a must be positive"):
        Nc_star_FHWA_from_su(100.0, 0.0)


# ==========================================================================
# 31. lcpc_unit_shaft_resistance  (Eq 6-32)
# ==========================================================================

def test_lcpc_unit_shaft_resistance_basic():
    # Eq. 6-32, PDF p. 463 (printed p. 425):
    # f_s = (Pa / ks)(qc / Pa) <= Pa (fp / Pa)
    # qc = 5000, Pa = 100, ks = 200, fp/Pa = 0.8:
    # f_s = (100 / 200)(5000 / 100) = 25, under the limit 100 x 0.8 = 80
    assert lcpc_unit_shaft_resistance(5000.0, 100.0, 200.0, 0.8) == pytest.approx(25.0, rel=1e-9)
    # qc = 1000 kPa, Pa = 101.325 kPa, ks = 60, fp/Pa = 0.35:
    # 1000 / 60 = 16.67 kPa, under 0.35 x 101.325 = 35.46 kPa
    assert lcpc_unit_shaft_resistance(1000.0, 101.325, 60.0, 0.35) == pytest.approx(16.667, abs=0.001)


def test_lcpc_unit_shaft_resistance_capped():
    # qc = 5000, Pa = 100, ks = 30: (100 / 30)(50) = 166.7, limited to
    # Pa (fp/Pa) = 100 x 0.15 = 15
    assert lcpc_unit_shaft_resistance(5000.0, 100.0, 30.0, 0.15) == pytest.approx(15.0, rel=1e-9)
    # qc = 5000 kPa, Pa = 101.325 kPa, ks = 60: 83.33, limited to
    # 0.35 x 101.325 = 35.46 kPa
    assert lcpc_unit_shaft_resistance(5000.0, 101.325, 60.0, 0.35) == pytest.approx(35.46, abs=0.01)


def test_lcpc_unit_shaft_resistance_refuses_a_stress_for_fp_over_Pa():
    # Table 6-22 (PDF p. 465, printed p. 427) prints the ratio fp/Pa, 0.15
    # to 1.5; a maximum side resistance in kPa or psf is not the ratio.
    with pytest.raises(ValueError, match="ratio fp/Pa"):
        lcpc_unit_shaft_resistance(5000.0, 100.0, 200.0, 100.0)
    with pytest.raises(ValueError, match="ratio fp/Pa"):
        lcpc_unit_shaft_resistance(5000.0, 100.0, 200.0, 0.0)
    assert lcpc_unit_shaft_resistance(50000.0, 100.0, 150.0, 1.5) == pytest.approx(150.0, rel=1e-9)


def test_lcpc_unit_shaft_resistance_raises_ks_zero():
    with pytest.raises(ValueError, match="k_s must be positive"):
        lcpc_unit_shaft_resistance(5000.0, 100.0, 0.0, 0.8)


def test_lcpc_unit_shaft_resistance_raises_Pa_zero():
    with pytest.raises(ValueError, match="P_a must be positive"):
        lcpc_unit_shaft_resistance(5000.0, 0.0, 200.0, 0.8)


# ==========================================================================
# 32. lcpc_unit_base_resistance  (Eq 6-33)
# ==========================================================================

def test_lcpc_unit_base_resistance_basic():
    # Eq. 6-33, PDF p. 463 (printed p. 425): q_b = Pa kt (qc,a / Pa)
    # qc,a = 10000, Pa = 100, kt = 0.4: 100 x 0.4 x 100 = 4000
    assert lcpc_unit_base_resistance(10000.0, 100.0, 0.4) == pytest.approx(4000.0, rel=1e-9)
    # qc,a = 15000 kPa, Pa = 101.325 kPa, kt = 0.3: 0.3 x 15000 = 4500 kPa
    assert lcpc_unit_base_resistance(15000.0, 101.325, 0.3) == pytest.approx(4500.0, rel=1e-9)
    # kt = 0.55 (the largest in Table 6-23), qc,a = 2000: 1100
    assert lcpc_unit_base_resistance(2000.0, 101.325, 0.55) == pytest.approx(1100.0, rel=1e-9)


def test_lcpc_unit_base_resistance_raises_kt_zero():
    with pytest.raises(ValueError, match="k_t must be positive"):
        lcpc_unit_base_resistance(10000.0, 100.0, 0.0)


def test_lcpc_unit_base_resistance_raises_Pa_zero():
    with pytest.raises(ValueError, match="P_a must be positive"):
        lcpc_unit_base_resistance(10000.0, 0.0, 0.4)


# ==========================================================================
# 33. micropile_shaft_resistance  (Eq 6-34)
# ==========================================================================

def test_micropile_shaft_resistance_basic():
    # alpha_bond=150, b=0.3, Z_b=5
    # R_s = 150 * pi * 0.3 * 5 = 150 * 4.71239 = 706.858
    expected = 150.0 * math.pi * 0.3 * 5.0
    assert micropile_shaft_resistance(150.0, 0.3, 5.0) == pytest.approx(expected, rel=1e-4)


def test_micropile_shaft_resistance_raises_b_zero():
    with pytest.raises(ValueError, match="b must be positive"):
        micropile_shaft_resistance(150.0, 0.0, 5.0)


def test_micropile_shaft_resistance_raises_Zb_zero():
    with pytest.raises(ValueError, match="Z_b must be positive"):
        micropile_shaft_resistance(150.0, 0.3, 0.0)


# ==========================================================================
# 34. rock_socket_unit_shaft_resistance  (Eq 6-35)
# ==========================================================================

def test_rock_socket_unit_shaft_resistance_basic():
    # q_u=5000, P_a=100, C=1, n=0.5
    # f_s = 1 * 100 * (5000/100)^0.5 = 100 * 50^0.5 = 100*7.07107 = 707.107
    expected = 1.0 * 100.0 * (5000.0 / 100.0) ** 0.5
    assert rock_socket_unit_shaft_resistance(5000.0, 100.0) == pytest.approx(expected, rel=1e-4)


def test_rock_socket_unit_shaft_resistance_custom_C_n():
    # C=0.63, n=0.5
    expected = 0.63 * 100.0 * (5000.0 / 100.0) ** 0.5
    assert rock_socket_unit_shaft_resistance(5000.0, 100.0, C=0.63, n=0.5) == pytest.approx(expected, rel=1e-4)


def test_rock_socket_unit_shaft_resistance_raises_Pa_zero():
    with pytest.raises(ValueError, match="P_a must be positive"):
        rock_socket_unit_shaft_resistance(5000.0, 0.0)


# ==========================================================================
# 35. rock_socket_unit_base_resistance  (Eq 6-36)
# ==========================================================================

def test_rock_socket_unit_base_resistance_basic():
    # N_cr_star=2.5, q_u=5000 => 12500
    assert rock_socket_unit_base_resistance(2.5, 5000.0) == pytest.approx(12500.0, rel=1e-4)


def test_rock_socket_unit_base_resistance_zero_qu():
    assert rock_socket_unit_base_resistance(2.5, 0.0) == pytest.approx(0.0, rel=1e-4)


# ==========================================================================
# 36. group_axial_capacity  (Eq 6-37)
# ==========================================================================

def test_group_axial_capacity_individual_governs():
    # n=4, eta=1.0, Rr=200, Rr_gblock=1000 => min(4*1*200, 1000) = min(800,1000) = 800
    assert group_axial_capacity(4, 1.0, 200.0, 1000.0) == pytest.approx(800.0, rel=1e-4)


def test_group_axial_capacity_block_governs():
    # n=10, eta=1.0, Rr=200, Rr_gblock=500 => min(2000, 500) = 500
    assert group_axial_capacity(10, 1.0, 200.0, 500.0) == pytest.approx(500.0, rel=1e-4)


# ==========================================================================
# 37. block_failure_resistance  (Eq 6-38)
# ==========================================================================

def test_block_failure_resistance_basic():
    # Z=20, B=6, L=9, f_s1=1.0, s_u2=2.0, N_c=7.5
    # 2*20*(6+9)*1.0 + 6*9*2.0*7.5 = 40*15 + 810 = 600 + 810 = 1410  (wait, let me redo)
    # Wait: 6*9*2.0*7.5 = 54*15 = 810. Yes.
    # 2*20*(15)*1.0 = 600
    # Total = 1410
    # Hmm, let me recompute: 6*9=54, 54*2.0=108, 108*7.5=810. And 2*20*15*1 = 600.
    # Total = 600+810 = 1410
    assert block_failure_resistance(20.0, 6.0, 9.0, 1.0, 2.0, 7.5) == pytest.approx(1410.0, rel=1e-4)


# ==========================================================================
# 38. block_failure_Nc  (Eq 6-39)
# ==========================================================================

def test_block_failure_Nc_basic():
    # B=6, L=9, Z=20
    # 5*(1 + 0.2*6/9)*(1 + 0.2*20/6) = 5*(1+0.13333)*(1+0.66667)
    # = 5*1.13333*1.66667 = 5*1.88889 = 9.44444 => capped at 9
    assert block_failure_Nc(6.0, 9.0, 20.0) == pytest.approx(9.0, rel=1e-4)


def test_block_failure_Nc_appendix_b_example_5():
    # Appendix B Example 5 (PDF p. 676, printed p. 638): a group B = L =
    # 18 ft, Z = 60 ft: 5 (1 + 0.2)(1 + 0.2 x 60 / 18) = 10, "Use maximum
    # value of Nc = 9", the limit of Eq. 6-39 (PDF p. 471, printed p. 433)
    assert block_failure_Nc(18.0, 18.0, 60.0) == 9.0


def test_block_failure_Nc_no_cap():
    # B=3, L=10, Z=2
    # 5*(1+0.2*3/10)*(1+0.2*2/3) = 5*(1+0.06)*(1+0.13333) = 5*1.06*1.13333 = 6.0067
    expected = 5.0 * (1.0 + 0.2 * 3.0 / 10.0) * (1.0 + 0.2 * 2.0 / 3.0)
    assert block_failure_Nc(3.0, 10.0, 2.0) == pytest.approx(expected, rel=1e-4)


def test_block_failure_Nc_raises_L_zero():
    with pytest.raises(ValueError, match="L must be positive"):
        block_failure_Nc(3.0, 0.0, 2.0)


def test_block_failure_Nc_raises_B_zero():
    with pytest.raises(ValueError, match="B must be positive"):
        block_failure_Nc(0.0, 10.0, 2.0)


# ==========================================================================
# 39. group_uplift_capacity  (Eq 6-40)
# ==========================================================================

def test_group_uplift_capacity_individual_governs():
    # Eq. 6-40, PDF p. 473 (printed p. 435):
    # R_r,gu = min{ n (R_r,s + W_r,e) + W_r,e,cap ; R_r,ublock }
    # n = 4, R_r,s = 50, W_r,e = 10, W_r,e,cap = 20, R_r,ublock = 500:
    # 4 x (50 + 10) + 20 = 260 < 500
    assert group_uplift_capacity(4, 50.0, 10.0, 20.0, 500.0) == pytest.approx(260.0, rel=1e-9)
    # n = 9, R_r,s = 120, W_r,e = 15, W_r,e,cap = 60: 9 x 135 + 60 = 1275
    assert group_uplift_capacity(9, 120.0, 15.0, 60.0, 5000.0) == pytest.approx(1275.0, rel=1e-9)


def test_group_uplift_capacity_block_governs():
    # n=4, R_r_s=50, W_r_e=10, W_r_e_cap=20, R_r_ublock=100
    # individual = 260 > 100 => 100
    assert group_uplift_capacity(4, 50.0, 10.0, 20.0, 100.0) == pytest.approx(100.0, rel=1e-4)


# ==========================================================================
# 40. uplift_block_volume  (Eq 6-41)
# ==========================================================================

def test_uplift_block_volume_basic():
    # Eq. 6-41, PDF p. 474 (printed p. 436):
    # V_block = B L Z + (Z^2 / 4)(B + L) + Z^3 / 12
    # B = 6, L = 9, Z = 10: 540 + 25 x 15 + 1000 / 12 = 998.33
    assert uplift_block_volume(6.0, 9.0, 10.0) == pytest.approx(998.33, abs=0.01)
    # B = L = 10, Z = 20: 2000 + 100 x 20 + 8000 / 12 = 4666.67
    assert uplift_block_volume(10.0, 10.0, 20.0) == pytest.approx(4666.67, abs=0.01)


def test_uplift_block_volume_is_the_4v_1h_prism():
    # Figure 6-16(a): the block's sides slope at 4V:1H, so at a height z
    # above the base its plan is (B + z/2) by (L + z/2).  The volume summed
    # in thin slices is the equation's.
    B, L, Z, n = 6.0, 9.0, 10.0, 20000
    dz = Z / n
    summed = sum((B + (i + 0.5) * dz / 2.0) * (L + (i + 0.5) * dz / 2.0)
                 for i in range(n)) * dz
    assert uplift_block_volume(B, L, Z) == pytest.approx(summed, rel=1e-6)


def test_uplift_block_volume_zero_depth():
    assert uplift_block_volume(6.0, 9.0, 0.0) == pytest.approx(0.0, rel=1e-4)


# ==========================================================================
# 41. uplift_block_weight_undrained  (Eq 6-42)
# ==========================================================================

def test_uplift_block_weight_undrained_basic():
    # B=6, L=9, Z1=5, Z2=5, gamma_m=120, gamma_b=60, W_cap=50
    # 6*9*(5*120 + 5*60) + 50 = 54*(600+300) + 50 = 54*900 + 50 = 48600+50 = 48650
    assert uplift_block_weight_undrained(6.0, 9.0, 5.0, 5.0, 120.0, 60.0, 50.0) == pytest.approx(48650.0, rel=1e-4)


def test_uplift_block_weight_undrained_no_submergence():
    # Z2=0 => B*L*Z1*gamma_m + W_cap = 6*9*(10*120 + 0) + 0 = 54*1200 = 64800
    assert uplift_block_weight_undrained(6.0, 9.0, 10.0, 0.0, 120.0, 60.0, 0.0) == pytest.approx(64800.0, rel=1e-4)


# ==========================================================================
# 42. uplift_block_capacity_undrained  (Eq 6-43)
# ==========================================================================

def test_uplift_block_capacity_undrained_basic():
    # Z=10, B=6, L=9, s_u_avg=2.0, W_e_g=1000
    # 2*10*(6+9)*2.0 + 1000 = 2*10*15*2 + 1000 = 600 + 1000 = 1600
    assert uplift_block_capacity_undrained(10.0, 6.0, 9.0, 2.0, 1000.0) == pytest.approx(1600.0, rel=1e-4)


# ==========================================================================
# 43. elastic_compression_pile  (Eq 6-45)
# ==========================================================================

def test_elastic_compression_pile_basic():
    # delta_Q=100, Z=30, A_p=1.0, E_p=29000
    # delta_e = 100*30/(1*29000) = 3000/29000 = 0.10345
    expected = 100.0 * 30.0 / (1.0 * 29000.0)
    assert elastic_compression_pile(100.0, 30.0, 1.0, 29000.0) == pytest.approx(expected, rel=1e-4)


def test_elastic_compression_pile_raises_Ap_zero():
    with pytest.raises(ValueError, match="A_p must be positive"):
        elastic_compression_pile(100.0, 30.0, 0.0, 29000.0)


def test_elastic_compression_pile_raises_Ep_zero():
    with pytest.raises(ValueError, match="E_p must be positive"):
        elastic_compression_pile(100.0, 30.0, 1.0, 0.0)


# ==========================================================================
# 44. meyerhof_group_settlement  (Eq 6-46)
# ==========================================================================

def test_meyerhof_group_settlement_basic():
    # Q_d=500, B=10, L=15, N1_60=25, I_f=0.8
    # delta_s = 500*sqrt(10)/(10*15*25) * 0.8
    # = 500*3.16228/3750 * 0.8 = 1581.139/3750 * 0.8 = 0.42164*0.8 = 0.33731
    expected = 500.0 * math.sqrt(10.0) / (10.0 * 15.0 * 25.0) * 0.8
    assert meyerhof_group_settlement(500.0, 10.0, 15.0, 25.0, 0.8) == pytest.approx(expected, rel=1e-4)


def test_meyerhof_group_settlement_raises_N_zero():
    with pytest.raises(ValueError, match="N1_60 must be positive"):
        meyerhof_group_settlement(500.0, 10.0, 15.0, 0.0, 0.8)


def test_meyerhof_group_settlement_raises_B_zero():
    with pytest.raises(ValueError, match="B and L must be positive"):
        meyerhof_group_settlement(500.0, 0.0, 15.0, 25.0, 0.8)


def test_meyerhof_group_settlement_raises_L_zero():
    with pytest.raises(ValueError, match="B and L must be positive"):
        meyerhof_group_settlement(500.0, 10.0, 0.0, 25.0, 0.8)


# ==========================================================================
# 45. meyerhof_influence_factor  (Eq 6-47)
# ==========================================================================

def test_meyerhof_influence_factor_basic():
    # Eq. 6-47, PDF p. 480 (printed p. 442): I_f = max{ 1 - Z/(12 B) ; 0.5 }
    # Z = 20, B = 10: 1 - 20/120 = 0.8333
    assert meyerhof_influence_factor(20.0, 10.0) == pytest.approx(0.8333, abs=0.0001)
    # Z = 30, B = 10: 1 - 30/120 = 0.75
    assert meyerhof_influence_factor(30.0, 10.0) == pytest.approx(0.75, rel=1e-9)
    # a short group, Z = 5, B = 10: 1 - 5/120 = 0.9583
    assert meyerhof_influence_factor(5.0, 10.0) == pytest.approx(0.9583, abs=0.0001)


def test_meyerhof_influence_factor_min_0_5():
    # Z = 6 B: 1 - 60/120 = 0.5; longer groups stay at 0.5
    assert meyerhof_influence_factor(60.0, 10.0) == pytest.approx(0.5, rel=1e-9)
    assert meyerhof_influence_factor(90.0, 10.0) == 0.5
    assert meyerhof_influence_factor(200.0, 10.0) == 0.5


def test_meyerhof_influence_factor_raises_B_zero():
    with pytest.raises(ValueError, match="B must be positive"):
        meyerhof_influence_factor(20.0, 0.0)


def test_meyerhof_influence_factor_raises_Z_zero():
    with pytest.raises(ValueError, match="Z must be positive"):
        meyerhof_influence_factor(0.0, 10.0)


# ==========================================================================
# 46. drilled_shaft_base_resistance_at_4pct  (Eq 6-48)
# ==========================================================================

def test_drilled_shaft_base_resistance_at_4pct_fine():
    # Eq. 6-48, PDF p. 481 (printed p. 443): R'_b = R_b for fine-grained
    # (cohesive) soils
    assert drilled_shaft_base_resistance_at_4pct(1000.0, "fine") == pytest.approx(1000.0, rel=1e-9)
    assert drilled_shaft_base_resistance_at_4pct(350.0, "fine") == pytest.approx(350.0, rel=1e-9)


def test_drilled_shaft_base_resistance_at_4pct_coarse():
    # Eq. 6-48: R'_b = 0.71 R_b for coarse-grained (cohesionless) soils
    assert drilled_shaft_base_resistance_at_4pct(1000.0, "coarse") == pytest.approx(710.0, rel=1e-9)
    assert drilled_shaft_base_resistance_at_4pct(350.0, "coarse") == pytest.approx(248.5, rel=1e-9)


def test_drilled_shaft_base_resistance_at_4pct_raises_invalid():
    with pytest.raises(ValueError, match="soil_type must be 'fine' or 'coarse'"):
        drilled_shaft_base_resistance_at_4pct(1000.0, "silt")


# ==========================================================================
# 47. equivalent_footing_width  (Eq 6-49)
# ==========================================================================

def test_equivalent_footing_width_basic():
    # Eq. 6-49, PDF p. 483 (printed p. 445): B' = B + z2/2
    # B = 6, z2 = 4: 6 + 2 = 8;  B = 18, z2 = 20: 28
    assert equivalent_footing_width(6.0, 4.0) == pytest.approx(8.0, rel=1e-9)
    assert equivalent_footing_width(18.0, 20.0) == pytest.approx(28.0, rel=1e-9)


def test_equivalent_footing_width_zero_z2():
    assert equivalent_footing_width(6.0, 0.0) == pytest.approx(6.0, rel=1e-4)


# ==========================================================================
# 48. equivalent_footing_length  (Eq 6-50)
# ==========================================================================

def test_equivalent_footing_length_basic():
    # Eq. 6-50, PDF p. 483 (printed p. 445): L' = L + z2/2
    # L = 9, z2 = 4: 9 + 2 = 11;  L = 24, z2 = 20: 34
    assert equivalent_footing_length(9.0, 4.0) == pytest.approx(11.0, rel=1e-9)
    assert equivalent_footing_length(24.0, 20.0) == pytest.approx(34.0, rel=1e-9)


def test_equivalent_footing_length_zero_z2():
    assert equivalent_footing_length(9.0, 0.0) == pytest.approx(9.0, rel=1e-4)


def test_equivalent_footing_appendix_b_example_5():
    # Appendix B Example 5 (PDF p. 680, printed p. 642): the equivalent
    # footing is at the neutral plane (z2 = 0), so B' = L' = 18 ft; with
    # Q = 1976 kips, Table B-30 prints the stress change by Eq. 6-51 as
    # 5774, 4940 and 4083 psf at z' = 0.5, 2 and 4 ft.
    B_prime = equivalent_footing_width(18.0, 0.0)
    L_prime = equivalent_footing_length(18.0, 0.0)
    assert (B_prime, L_prime) == (18.0, 18.0)
    for z_prime, printed in ((0.5, 5774.0), (2.0, 4940.0), (4.0, 4083.0)):
        got = stress_change_2V1H(1976000.0, B_prime, L_prime, z_prime)
        assert got == pytest.approx(printed, abs=0.5)


# ==========================================================================
# 49. stress_change_2V1H  (Eq 6-51)
# ==========================================================================

def test_stress_change_2V1H_basic():
    # Q=1000, B'=10, L'=13, z'=5
    # delta_sigma = 1000/((10+5)*(13+5)) = 1000/(15*18) = 1000/270 = 3.7037
    expected = 1000.0 / (15.0 * 18.0)
    assert stress_change_2V1H(1000.0, 10.0, 13.0, 5.0) == pytest.approx(expected, rel=1e-4)


def test_stress_change_2V1H_zero_depth():
    # z'=0 => 1000/(10*13) = 1000/130 = 7.6923
    expected = 1000.0 / (10.0 * 13.0)
    assert stress_change_2V1H(1000.0, 10.0, 13.0, 0.0) == pytest.approx(expected, rel=1e-4)


def test_stress_change_2V1H_raises_denom_zero():
    # B'=0, z'=0 => denom = 0*L' = 0
    with pytest.raises(ValueError, match="Denominator must be positive"):
        stress_change_2V1H(1000.0, 0.0, 13.0, 0.0)


# ==========================================================================
# 50. stress_change_neutral_plane  (Eq 6-52)
# ==========================================================================

def test_stress_change_neutral_plane_basic():
    # Q=1000, B'=10, L'=13, z'=5, delta_sigma_other=2.0
    # stress_change_2V1H = 1000/270 = 3.7037 + 2.0 = 5.7037
    expected = 1000.0 / ((10.0 + 5.0) * (13.0 + 5.0)) + 2.0
    assert stress_change_neutral_plane(1000.0, 10.0, 13.0, 5.0, 2.0) == pytest.approx(expected, rel=1e-4)


def test_stress_change_neutral_plane_no_other():
    # delta_sigma_other defaults to 0
    expected = 1000.0 / ((10.0 + 5.0) * (13.0 + 5.0))
    assert stress_change_neutral_plane(1000.0, 10.0, 13.0, 5.0) == pytest.approx(expected, rel=1e-4)


# ==========================================================================
# 51. settlement_clay  (Eq 6-53)
# ==========================================================================

def test_settlement_clay_recompression_only():
    # sigma_z0=100, sigma_p=200, delta=50 => final=150 < 200 => recompression only
    # delta_s = C_er * H0 * log10(150/100) = 0.01*10*log10(1.5)
    expected = 0.01 * 10.0 * math.log10(1.5)
    assert settlement_clay(10.0, 0.01, 0.1, 100.0, 200.0, 50.0) == pytest.approx(expected, rel=1e-4)


def test_settlement_clay_virgin_only():
    # sigma_z0=200 >= sigma_p=150 => virgin compression only
    # delta_s = C_ec * H0 * log10((200+50)/200) = 0.1*10*log10(1.25)
    expected = 0.1 * 10.0 * math.log10(1.25)
    assert settlement_clay(10.0, 0.01, 0.1, 200.0, 150.0, 50.0) == pytest.approx(expected, rel=1e-4)


def test_settlement_clay_spans_both():
    # sigma_z0=100, sigma_p=120, delta=50 => final=150 > 120 and sigma_z0 < sigma_p
    # delta_s = 0.01*10*log10(120/100) + 0.1*10*log10(150/120)
    expected = (0.01 * 10.0 * math.log10(1.2)
                + 0.1 * 10.0 * math.log10(150.0 / 120.0))
    assert settlement_clay(10.0, 0.01, 0.1, 100.0, 120.0, 50.0) == pytest.approx(expected, rel=1e-4)


def test_settlement_clay_raises_sigma_z0_zero():
    with pytest.raises(ValueError, match="sigma_z0_eff must be positive"):
        settlement_clay(10.0, 0.01, 0.1, 0.0, 200.0, 50.0)


def test_settlement_clay_raises_sigma_p_zero():
    with pytest.raises(ValueError, match="sigma_p must be positive"):
        settlement_clay(10.0, 0.01, 0.1, 100.0, 0.0, 50.0)


def test_settlement_clay_raises_final_stress_negative():
    # sigma_z0=10, delta=-20 => final=-10 < 0
    with pytest.raises(ValueError, match="Final effective stress must be positive"):
        settlement_clay(10.0, 0.01, 0.1, 10.0, 200.0, -20.0)


# ==========================================================================
# 52. settlement_sand_elastic  (Eq 6-54)
# ==========================================================================

def test_settlement_sand_elastic_basic():
    # H0=10, nu_s=0.3, E_s=5000, delta_sigma_z=100
    # (10*(1+0.3)*(1-0.6))/((1-0.3)*5000)*100
    # = (10*1.3*0.4)/(0.7*5000)*100 = 5.2/3500*100 = 0.14857
    expected = 10.0 * 1.3 * 0.4 / (0.7 * 5000.0) * 100.0
    assert settlement_sand_elastic(10.0, 0.3, 5000.0, 100.0) == pytest.approx(expected, rel=1e-4)


def test_settlement_sand_elastic_raises_Es_zero():
    with pytest.raises(ValueError, match="E_s must be positive"):
        settlement_sand_elastic(10.0, 0.3, 0.0, 100.0)


def test_settlement_sand_elastic_raises_Es_negative():
    with pytest.raises(ValueError, match="E_s must be positive"):
        settlement_sand_elastic(10.0, 0.3, -100.0, 100.0)


# ==========================================================================
# 53. broms_factored_load  (Eq 6-55)
# ==========================================================================

def test_broms_factored_load_basic():
    # P_dead=10, P_live=20 => 1.5*10 + 2.0*20 = 15+40 = 55
    assert broms_factored_load(10.0, 20.0) == pytest.approx(55.0, rel=1e-4)


def test_broms_factored_load_no_live():
    assert broms_factored_load(10.0, 0.0) == pytest.approx(15.0, rel=1e-4)


# ==========================================================================
# 54. broms_factored_moment  (Eq 6-56)
# ==========================================================================

def test_broms_factored_moment_basic():
    # M_dead=100, M_live=200 => 1.5*100 + 2.0*200 = 150+400 = 550
    assert broms_factored_moment(100.0, 200.0) == pytest.approx(550.0, rel=1e-4)


def test_broms_factored_moment_no_live():
    assert broms_factored_moment(100.0, 0.0) == pytest.approx(150.0, rel=1e-4)


# ==========================================================================
# 55. broms_factored_su  (Eq 6-57)
# ==========================================================================

def test_broms_factored_su_basic():
    # s_u=2.0 => 0.75*2 = 1.5
    assert broms_factored_su(2.0) == pytest.approx(1.5, rel=1e-4)


def test_broms_factored_su_zero():
    assert broms_factored_su(0.0) == pytest.approx(0.0, rel=1e-4)


# ==========================================================================
# 56. broms_factored_phi  (Eq 6-58)
# ==========================================================================

def test_broms_factored_phi_basic():
    # phi=30 => atan(0.75*tan(30)) = atan(0.75*0.57735) = atan(0.43301)
    expected = math.degrees(math.atan(0.75 * math.tan(math.radians(30.0))))
    assert broms_factored_phi(30.0) == pytest.approx(expected, rel=1e-4)


def test_broms_factored_phi_zero():
    # phi=0 => atan(0) = 0
    assert broms_factored_phi(0.0) == pytest.approx(0.0, rel=1e-4)


def test_broms_factored_phi_45():
    # phi=45 => atan(0.75*1) = atan(0.75)
    expected = math.degrees(math.atan(0.75))
    assert broms_factored_phi(45.0) == pytest.approx(expected, rel=1e-4)


# ==========================================================================
# 57. broms_undrained_f  (Eq 6-59)
# ==========================================================================

def test_broms_undrained_f_basic():
    # P_t_ult=54, s_u_star=1.5, b=1.0
    # f = 54/(9*1.5*1.0) = 54/13.5 = 4.0
    assert broms_undrained_f(54.0, 1.5, 1.0) == pytest.approx(4.0, rel=1e-4)


def test_broms_undrained_f_raises_su_zero():
    with pytest.raises(ValueError, match="s_u_star must be positive"):
        broms_undrained_f(54.0, 0.0, 1.0)


def test_broms_undrained_f_raises_b_zero():
    with pytest.raises(ValueError, match="b must be positive"):
        broms_undrained_f(54.0, 1.5, 0.0)


# ==========================================================================
# 58. broms_undrained_g  (Eq 6-60)
# ==========================================================================

def test_broms_undrained_g_basic():
    # M_t_ult=100, P_t_ult=54, b=1.0, f=4.0, s_u_star=1.5
    # num = 100 + 54*(1.5*1 + 0.5*4) = 100 + 54*(1.5+2) = 100 + 54*3.5 = 100+189 = 289
    # denom = 2.25*1.0*1.5 = 3.375
    # g = sqrt(289/3.375) = sqrt(85.6296) = 9.2537
    expected = math.sqrt((100.0 + 54.0 * (1.5 + 2.0)) / (2.25 * 1.0 * 1.5))
    assert broms_undrained_g(100.0, 54.0, 1.0, 4.0, 1.5) == pytest.approx(expected, rel=1e-4)


def test_broms_undrained_g_raises_denom_zero():
    with pytest.raises(ValueError, match="Denominator must be positive"):
        broms_undrained_g(100.0, 54.0, 0.0, 4.0, 1.5)


# ==========================================================================
# 59. broms_undrained_Zmin  (Eq 6-61)
# ==========================================================================

def test_broms_undrained_Zmin_basic():
    # b=1.0, f=4.0, g=9.25 => 1.5*1 + 4 + 9.25 = 14.75
    assert broms_undrained_Zmin(1.0, 4.0, 9.25) == pytest.approx(14.75, rel=1e-4)


def test_broms_undrained_Zmin_zero_fg():
    # b=2, f=0, g=0 => 1.5*2 = 3
    assert broms_undrained_Zmin(2.0, 0.0, 0.0) == pytest.approx(3.0, rel=1e-4)


# ==========================================================================
# 60. broms_drained_passive  (Eq 6-62)
# ==========================================================================

def test_broms_drained_passive_basic():
    # gamma_eff=0.06, b=1.0, K_P=3.0, Z_min=10.0
    # P_P = 1.5*0.06*1.0*3.0*100 = 27.0
    expected = 1.5 * 0.06 * 1.0 * 3.0 * 10.0 ** 2
    assert broms_drained_passive(0.06, 1.0, 3.0, 10.0) == pytest.approx(expected, rel=1e-4)


# ==========================================================================
# 61. broms_drained_Zmin  (Eq 6-63)
# ==========================================================================

def test_broms_drained_Zmin_basic():
    # P_t_ult=10, M_t_ult=50, gamma_eff=0.06, b=1.0, K_P=3.0
    # iterative solve: Z = (2*(10*Z+50)/(0.06*1*3))^(1/3) = (2*(10Z+50)/0.18)^(1/3)
    # Let me solve numerically: start with Z=10
    # Z_new = (2*(100+50)/0.18)^(1/3) = (2*150/0.18)^(1/3) = (1666.67)^(1/3) = 11.856
    # Continue iterations... just verify convergence
    result = broms_drained_Zmin(10.0, 50.0, 0.06, 1.0, 3.0)
    # Verify by plugging back: Z = (2*(10*Z+50)/0.18)^(1/3)
    check = (2.0 * (10.0 * result + 50.0) / (0.06 * 1.0 * 3.0)) ** (1.0 / 3.0)
    assert result == pytest.approx(check, rel=1e-4)


def test_broms_drained_Zmin_raises_denom_zero():
    with pytest.raises(ValueError, match="gamma_eff, b, and K_P must all be positive"):
        broms_drained_Zmin(10.0, 50.0, 0.0, 1.0, 3.0)


# ==========================================================================
# 62. broms_drained_zero_shear_depth  (Eq 6-64)
# ==========================================================================

def test_broms_drained_zero_shear_depth_basic():
    # P_t_ult=27, gamma_eff=0.06, b=1.0, K_P=3.0
    # f = sqrt(27/(1.5*0.06*1*3)) = sqrt(27/0.27) = sqrt(100) = 10
    assert broms_drained_zero_shear_depth(27.0, 0.06, 1.0, 3.0) == pytest.approx(10.0, rel=1e-4)


def test_broms_drained_zero_shear_depth_raises_denom_zero():
    with pytest.raises(ValueError, match="gamma_eff, b, and K_P must all be positive"):
        broms_drained_zero_shear_depth(27.0, 0.0, 1.0, 3.0)


# ==========================================================================
# 63. broms_drained_max_moment  (Eq 6-65)
# ==========================================================================

def test_broms_drained_max_moment_basic():
    # M_t_ult=50, P_t_ult=10, f=5, gamma_eff=0.06, b=1.0, K_P=3.0
    # M_max = 50 + 10*5 - 0.06*1*3*125/2 = 50+50-11.25 = 88.75
    expected = 50.0 + 10.0 * 5.0 - 0.06 * 1.0 * 3.0 * 5.0 ** 3 / 2.0
    assert broms_drained_max_moment(50.0, 10.0, 5.0, 0.06, 1.0, 3.0) == pytest.approx(expected, rel=1e-4)


# ==========================================================================
# 64. clm_deflection_from_load  (Eq 6-66)
# ==========================================================================

def test_clm_deflection_from_load_basic():
    # P_t=10, P_c=100, b=1.0, a=0.15, n=0.73
    # y_t = 1.0 * 0.15 * (10/100)^0.73 = 0.15 * 0.1^0.73
    expected = 1.0 * 0.15 * (10.0 / 100.0) ** 0.73
    assert clm_deflection_from_load(10.0, 100.0, 1.0, 0.15, 0.73) == pytest.approx(expected, rel=1e-4)


def test_clm_deflection_from_load_raises_Pc_zero():
    with pytest.raises(ValueError, match="P_c must be positive"):
        clm_deflection_from_load(10.0, 0.0, 1.0, 0.15, 0.73)


# ==========================================================================
# 65. clm_load_from_deflection  (Eq 6-67)
# ==========================================================================

def test_clm_load_from_deflection_basic():
    # y_t=0.5, b=1.0, P_c=100, a=0.15, n=0.73
    # P_t = 100 * (0.5/(0.15*1))^(1/0.73) = 100*(3.3333)^1.36986
    expected = 100.0 * (0.5 / (0.15 * 1.0)) ** (1.0 / 0.73)
    assert clm_load_from_deflection(0.5, 1.0, 100.0, 0.15, 0.73) == pytest.approx(expected, rel=1e-4)


def test_clm_load_from_deflection_raises_a_zero():
    with pytest.raises(ValueError, match="a and b must be positive"):
        clm_load_from_deflection(0.5, 1.0, 100.0, 0.0, 0.73)


def test_clm_load_from_deflection_raises_b_zero():
    with pytest.raises(ValueError, match="a and b must be positive"):
        clm_load_from_deflection(0.5, 0.0, 100.0, 0.15, 0.73)


# ==========================================================================
# 66. clm_deflection_from_moment  (Eq 6-68)
# ==========================================================================

def test_clm_deflection_from_moment_basic():
    # M_t=50, M_c=500, b=1.0, a=0.15, n=0.73
    # y_t = 1.0 * 0.15 * (50/500)^0.73 = 0.15 * 0.1^0.73
    expected = 1.0 * 0.15 * (50.0 / 500.0) ** 0.73
    assert clm_deflection_from_moment(50.0, 500.0, 1.0, 0.15, 0.73) == pytest.approx(expected, rel=1e-4)


def test_clm_deflection_from_moment_raises_Mc_zero():
    with pytest.raises(ValueError, match="M_c must be positive"):
        clm_deflection_from_moment(50.0, 0.0, 1.0, 0.15, 0.73)


# ==========================================================================
# 67. clm_moment_from_deflection  (Eq 6-69)
# ==========================================================================

def test_clm_moment_from_deflection_basic():
    # y_t=0.5, b=1.0, M_c=500, a=0.15, n=0.73
    # M_t = 500 * (0.5/(0.15*1))^(1/0.73)
    expected = 500.0 * (0.5 / (0.15 * 1.0)) ** (1.0 / 0.73)
    assert clm_moment_from_deflection(0.5, 1.0, 500.0, 0.15, 0.73) == pytest.approx(expected, rel=1e-4)


def test_clm_moment_from_deflection_raises_a_zero():
    with pytest.raises(ValueError, match="a and b must be positive"):
        clm_moment_from_deflection(0.5, 1.0, 500.0, 0.0, 0.73)


def test_clm_moment_from_deflection_raises_b_zero():
    with pytest.raises(ValueError, match="a and b must be positive"):
        clm_moment_from_deflection(0.5, 0.0, 500.0, 0.15, 0.73)


# ==========================================================================
# 68. clm_max_moment  (Eq 6-70)
# ==========================================================================

def test_clm_max_moment_basic():
    # P_t=10, P_c=100, M_c=500, a=0.10, n=0.68
    # M_max = 500 * 0.10 * (10/100)^0.68 = 50 * 0.1^0.68
    expected = 500.0 * 0.10 * (10.0 / 100.0) ** 0.68
    assert clm_max_moment(10.0, 100.0, 500.0, 0.10, 0.68) == pytest.approx(expected, rel=1e-4)


def test_clm_max_moment_raises_Pc_zero():
    with pytest.raises(ValueError, match="P_c must be positive"):
        clm_max_moment(10.0, 0.0, 500.0, 0.10, 0.68)


# ==========================================================================
# 69. mobilized_passive_resistance  (Eq 6-71)
# ==========================================================================

def test_mobilized_passive_resistance_basic():
    # P_P_ult=100, y=0.5, H_cap=3.0
    # P_mob = 100*0.5/(0.006*3 + 0.85*0.5) = 50/(0.018+0.425) = 50/0.443 = 112.87
    # capped at 100
    assert mobilized_passive_resistance(100.0, 0.5, 3.0) == pytest.approx(100.0, rel=1e-4)


def test_mobilized_passive_resistance_small_y():
    # Eq. 6-71, PDF p. 505 (printed p. 467):
    # P_P,mob / P_P,ult = y / (0.85 y + 0.006 H_cap) <= 1
    # P_P,ult = 100, y = 0.01, H_cap = 3.0:
    # 0.01 / (0.0085 + 0.018) = 0.37736 -> 37.736
    assert mobilized_passive_resistance(100.0, 0.01, 3.0) == pytest.approx(37.736, abs=0.001)


def test_mobilized_passive_resistance_full_at_4_percent_of_cap_height():
    # "full passive resistance is mobilized at a lateral displacement equal
    # to 4% of the height of the pile cap": y = 0.04 x 3.0 = 0.12 gives
    # 0.12 / (0.102 + 0.018) = 1
    assert mobilized_passive_resistance(100.0, 0.12, 3.0) == pytest.approx(100.0, rel=1e-9)
    # Appendix B Example 6 (PDF p. 686, printed p. 648) writes the cap's
    # term as 204 kips x y_t / (0.85 y_t + 0.252): P_P,ult = 204 kips and
    # 0.006 H_cap = 0.252 in (H_cap = 42 in).  At y_t = 0.5 in:
    # 204 x 0.5 / (0.425 + 0.252) = 150.7 kips
    assert mobilized_passive_resistance(204.0, 0.5, 42.0) == pytest.approx(150.7, abs=0.1)


def test_mobilized_passive_resistance_zero_y():
    # y<=0 => returns 0
    assert mobilized_passive_resistance(100.0, 0.0, 3.0) == pytest.approx(0.0, rel=1e-4)


def test_mobilized_passive_resistance_negative_y():
    assert mobilized_passive_resistance(100.0, -0.5, 3.0) == pytest.approx(0.0, rel=1e-4)


def test_mobilized_passive_resistance_raises_Pp_zero():
    with pytest.raises(ValueError, match="P_P_ult must be positive"):
        mobilized_passive_resistance(0.0, 0.5, 3.0)


def test_mobilized_passive_resistance_raises_Hcap_zero():
    with pytest.raises(ValueError, match="H_cap must be positive"):
        mobilized_passive_resistance(100.0, 0.5, 0.0)


# ==========================================================================
# 70. driving_stress_limit_steel  (Eq 6-72)
# ==========================================================================

def test_driving_stress_limit_steel_basic():
    # phi_da=1.0, f_y=50 => 1.0*0.9*50 = 45
    assert driving_stress_limit_steel(1.0, 50.0) == pytest.approx(45.0, rel=1e-4)


def test_driving_stress_limit_steel_phi_less_than_1():
    # phi_da=0.9, f_y=36 => 0.9*0.9*36 = 29.16
    assert driving_stress_limit_steel(0.9, 36.0) == pytest.approx(29.16, rel=1e-4)


# ==========================================================================
# 71. driving_stress_limit_concrete_compression  (Eq 6-73)
# ==========================================================================

def test_driving_stress_limit_concrete_compression_basic():
    # phi_da=1.0, f_c'=5.0, f_pe=0.7
    # 1.0*(0.85*5 - 0.7) = 1.0*(4.25-0.7) = 3.55
    assert driving_stress_limit_concrete_compression(1.0, 5.0, 0.7) == pytest.approx(3.55, rel=1e-4)


def test_driving_stress_limit_concrete_compression_no_prestress():
    # f_pe=0 => phi_da*0.85*f_c' = 1.0*0.85*5 = 4.25
    assert driving_stress_limit_concrete_compression(1.0, 5.0, 0.0) == pytest.approx(4.25, rel=1e-4)


# ==========================================================================
# 72. driving_stress_limit_concrete_tension  (Eq 6-74)
# ==========================================================================

def test_driving_stress_limit_concrete_tension_basic():
    # phi_da=1.0, f_c'=5.0, f_pe=0.7
    # 1.0*(0.095*sqrt(5) + 0.7) = 1.0*(0.095*2.2361+0.7) = 1.0*(0.21243+0.7) = 0.91243
    expected = 1.0 * (0.095 * math.sqrt(5.0) + 0.7)
    assert driving_stress_limit_concrete_tension(1.0, 5.0, 0.7) == pytest.approx(expected, rel=1e-4)


def test_driving_stress_limit_concrete_tension_no_prestress():
    # f_pe=0 => 0.095*sqrt(5) = 0.21243
    expected = 0.095 * math.sqrt(5.0)
    assert driving_stress_limit_concrete_tension(1.0, 5.0, 0.0) == pytest.approx(expected, rel=1e-4)


# ==========================================================================
# 73. driving_stress_limit_timber  (Eq 6-75)
# ==========================================================================

def test_driving_stress_limit_timber_basic():
    # phi_da=1.15, f_cto=1.2 => 1.15*2.6*1.2 = 3.588
    assert driving_stress_limit_timber(1.15, 1.2) == pytest.approx(3.588, rel=1e-4)


def test_driving_stress_limit_timber_phi_1():
    # phi_da=1.0, f_cto=1.0 => 2.6
    assert driving_stress_limit_timber(1.0, 1.0) == pytest.approx(2.6, rel=1e-4)


# ==========================================================================
# 74. depth_to_fixity_undrained  (Eq 6-76)
# ==========================================================================

def test_depth_to_fixity_undrained_basic():
    # Eq. 6-76, PDF p. 512 (printed p. 474):
    # Z_f = sqrt(2) (Ep Ip / (b kh))^0.25
    # Ep = 29000, Ip = 100, b = 1.0, kh = 10: 290000^0.25 = 23.206;
    # Z_f = 1.4142 x 23.206 = 32.82
    assert depth_to_fixity_undrained(29000.0, 100.0, 1.0, 10.0) == pytest.approx(32.82, abs=0.01)
    # Ep Ip / (b kh) = 16: Z_f = 1.4142 x 2 = 2.828
    assert depth_to_fixity_undrained(16.0, 1.0, 1.0, 1.0) == pytest.approx(2.828, abs=0.001)
    # Ep Ip / (b kh) = 10000: Z_f = 1.4142 x 10 = 14.142
    assert depth_to_fixity_undrained(200.0, 100.0, 0.5, 4.0) == pytest.approx(14.142, abs=0.001)


def test_depth_to_fixity_undrained_raises_b_zero():
    with pytest.raises(ValueError, match="b and k_h must be positive"):
        depth_to_fixity_undrained(29000.0, 100.0, 0.0, 10.0)


def test_depth_to_fixity_undrained_raises_kh_zero():
    with pytest.raises(ValueError, match="b and k_h must be positive"):
        depth_to_fixity_undrained(29000.0, 100.0, 1.0, 0.0)


# ==========================================================================
# 75. undrained_subgrade_modulus  (Eq 6-77)
# ==========================================================================

def test_undrained_subgrade_modulus_basic():
    # C=67, s_u=2.0 => 134
    assert undrained_subgrade_modulus(67.0, 2.0) == pytest.approx(134.0, rel=1e-4)


def test_undrained_subgrade_modulus_zero_su():
    assert undrained_subgrade_modulus(67.0, 0.0) == pytest.approx(0.0, rel=1e-4)


# ==========================================================================
# 76. depth_to_fixity_drained  (Eq 6-78)
# ==========================================================================

def test_depth_to_fixity_drained_basic():
    # E_p=29000, I_p=100, n_h=5
    # Z_f = 1.8*(29000*100/5)^0.2 = 1.8*(580000)^0.2
    # 580000^0.2: ln(580000)=13.2706, *0.2=2.65412, exp=14.214
    # Z_f = 1.8*14.214 = 25.585
    expected = 1.8 * (29000.0 * 100.0 / 5.0) ** 0.2
    assert depth_to_fixity_drained(29000.0, 100.0, 5.0) == pytest.approx(expected, rel=1e-4)


def test_depth_to_fixity_drained_raises_nh_zero():
    with pytest.raises(ValueError, match="n_h must be positive"):
        depth_to_fixity_drained(29000.0, 100.0, 0.0)


def test_depth_to_fixity_drained_raises_nh_negative():
    with pytest.raises(ValueError, match="n_h must be positive"):
        depth_to_fixity_drained(29000.0, 100.0, -1.0)


# ==========================================================================
# 77. drag_force_check  (Eq 6-80)
# ==========================================================================

def test_drag_force_check_passes():
    # Eq. 6-80, PDF p. 516 (printed p. 478):
    # 1.25 Q_d + 1.10 (Q_np - Q_d) <= P_r
    # Q_d = 100, Q_np = 150, P_r = 200:
    # 1.25 x 100 + 1.10 x (150 - 100) = 125 + 55 = 180 <= 200
    assert drag_force_check(100.0, 150.0, 200.0) is True


def test_drag_force_check_appendix_b_example_5():
    # Appendix B Example 5 (PDF p. 678, printed p. 640): Q_d = 40 kips,
    # Q_np = 133 kips: 1.25 (40) + 1.1 (133 - 40) = 152 kips <= 200 kips
    assert drag_force_check(40.0, 133.0, 200.0) is True
    # the same demand of 152.3 kips against 152 and 153 kips
    assert drag_force_check(40.0, 133.0, 152.0) is False
    assert drag_force_check(40.0, 133.0, 153.0) is True


def test_drag_force_check_fails():
    # Q_d = 100, Q_np = 200, P_r = 200
    # 1.25 x 100 + 1.10 x (200 - 100) = 125 + 110 = 235 > 200
    assert drag_force_check(100.0, 200.0, 200.0) is False


def test_drag_force_check_exact_boundary():
    # demand = P_r exactly => True (<=)
    # Q_d = 100, Q_np - Q_d = 50: 125 + 55 = 180
    assert drag_force_check(100.0, 150.0, 180.0) is True


def test_drag_force_check_takes_three_loads():
    # The drag force is Q_np - Q_d; the old fourth argument (Q_d_drag) was
    # never read and is gone.
    with pytest.raises(TypeError):
        drag_force_check(100.0, 150.0, 50.0, 200.0)


# ==========================================================================
# 78. table_6_18_Fnu  (Table 6-18)
# ==========================================================================

class TestTable618Fnu:
    """Table 6-18, Factors for Approximating Volumetric Strain, PDF p. 461
    (printed p. 423): F_nu by pile shape at nu = 0.2 to 0.5."""

    @pytest.mark.parametrize("nu, square, circular", [
        (0.2, 0.59, 0.63),
        (0.25, 0.54, 0.58),
        (0.3, 0.48, 0.52),
        (0.35, 0.41, 0.44),
        (0.4, 0.30, 0.33),
        (0.45, 0.17, 0.18),
        (0.5, 0.0, 0.0),
    ])
    def test_printed_columns(self, nu, square, circular):
        assert table_6_18_Fnu(nu, "square") == pytest.approx(square, abs=1e-9)
        assert table_6_18_Fnu(nu, "circular") == pytest.approx(circular, abs=1e-9)

    def test_nu_05(self):
        # nu = 0.5 (no volume change): the table prints 0 for both shapes
        assert table_6_18_Fnu(0.5, "square") == 0.0
        assert table_6_18_Fnu(0.5, "circular") == 0.0

    def test_nu_03(self):
        assert table_6_18_Fnu(0.3, "square") == pytest.approx(0.48, abs=1e-9)
        assert table_6_18_Fnu(0.3, "Circular") == pytest.approx(0.52, abs=1e-9)

    def test_interpolated(self):
        # midway between the printed columns 0.25 and 0.3, circular:
        # (0.58 + 0.52) / 2 = 0.55; between 0.4 and 0.45, square:
        # (0.30 + 0.17) / 2 = 0.235
        assert table_6_18_Fnu(0.275, "circular") == pytest.approx(0.55, abs=1e-6)
        assert table_6_18_Fnu(0.425, "square") == pytest.approx(0.235, abs=1e-6)

    def test_below_the_first_column_raises(self):
        # the table's first column is nu = 0.2
        for nu in (-0.1, 0.0, 0.1, 0.19):
            with pytest.raises(ValueError, match="0.2 to 0.5"):
                table_6_18_Fnu(nu, "square")

    def test_above_05_raises(self):
        with pytest.raises(ValueError, match="0.2 to 0.5"):
            table_6_18_Fnu(0.6, "circular")

    def test_unknown_shape_raises(self):
        with pytest.raises(ValueError, match="no row for pile_shape"):
            table_6_18_Fnu(0.3, "h_pile")

    def test_shape_is_required(self):
        with pytest.raises(TypeError):
            table_6_18_Fnu(0.3)


# ==========================================================================
# 79. table_6_21_ks  (Table 6-21)
# ==========================================================================

# Tables 6-21, 6-22 and 6-23, PDF p. 465 (printed p. 427), row by row as
# printed.  Columns: Group I-A, I-B, II-A, II-B (groups defined on PDF
# p. 463, printed p. 425).  Each soil row is for the qc/Pa range in the
# comment.
_LCPC_PRINTED = [
    # soil row, ks (I-A, I-B, II-A, II-B),
    #   fp/Pa (I-A, I-B, II-A, II-B) as (value, value in parentheses),
    #   kt (Group I-A&B, Group II-A&B)
    ("soft_clay_and_mud",                          # qc/Pa < 10
     (30, 30, 30, 30),
     ((0.15, None), (0.15, None), (0.15, None), (0.15, None)),
     (0.4, 0.5)),
    ("moderately_compact_clay",                    # 10 to 50
     (40, 80, 40, 80),
     ((0.35, 0.8), (0.35, 0.8), (0.35, 0.8), (0.35, None)),
     (0.35, 0.45)),
    ("silt_and_loose_sand",                        # <= 50
     (60, 150, 60, 120),
     ((0.35, None), (0.35, None), (0.35, None), (0.35, None)),
     (0.4, 0.5)),
    ("compact_to_stiff_clay_and_compact_silt",     # > 50
     (60, 120, 60, 120),
     ((0.35, 0.8), (0.35, 0.8), (0.35, 0.8), (0.35, None)),
     (0.45, 0.55)),
    ("soft_chalk",                                 # <= 50
     (100, 120, 100, 120),
     ((0.35, None), (0.35, None), (0.35, None), (0.35, None)),
     (0.2, 0.3)),
    ("moderately_compact_sand_and_gravel",         # 50 to 120
     (100, 200, 100, 200),
     ((0.8, 1.2), (0.35, 0.8), (0.8, 1.2), (0.8, None)),
     (0.4, 0.5)),
    ("weathered_to_fragmented_chalk",              # > 50
     (60, 80, 60, 80),
     ((1.2, 1.5), (0.8, 1.2), (1.2, 1.5), (1.2, None)),
     (0.2, 0.4)),
    ("compact_to_very_compact_sand_and_gravel",    # > 120
     (150, 300, 150, 200),
     ((1.2, 1.5), (0.8, 1.2), (1.2, 1.5), (1.2, None)),
     (0.3, 0.4)),
]
_LCPC_GROUP_NAMES = ("I-A", "I-B", "II-A", "II-B")


class TestTable621Ks:
    @pytest.mark.parametrize("row", _LCPC_PRINTED, ids=[r[0] for r in _LCPC_PRINTED])
    def test_every_printed_cell(self, row):
        soil, ks, _fp, _kt = row
        for group, printed in zip(_LCPC_GROUP_NAMES, ks):
            assert table_6_21_ks(soil, group) == printed

    def test_soft_clay_driven(self):
        # Soft clay and mud: 30 in every group
        assert table_6_21_ks("soft_clay_and_mud", "II-A") == pytest.approx(30.0, rel=1e-9)

    def test_dense_sand_bored(self):
        # Compact to very compact sand and gravel, Group I-B (drilled shaft
        # with permanent casing): 300, the largest ks in the table
        assert table_6_21_ks("compact_to_very_compact_sand_and_gravel", "I-B") == pytest.approx(300.0, rel=1e-9)

    def test_medium_sand_driven_steel_open(self):
        # Moderately compact sand and gravel, Group II-B (driven and jacked
        # steel piles): 200
        assert table_6_21_ks("moderately_compact_sand_and_gravel", "II-B") == pytest.approx(200.0, rel=1e-9)

    def test_row_and_group_spellings(self):
        assert table_6_21_ks("Silt and loose sand", "Group II-B") == 120.0
        assert table_6_21_ks("silt_and_loose_sand", "ib") == 150.0

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_6_21_ks("unknown", "driven")

    def test_old_soil_and_pile_names_are_refused(self):
        # the rows and pile types of the old table were not the print's
        with pytest.raises(ValueError, match="no row for soil_type"):
            table_6_21_ks("soft_clay", "I-A")
        with pytest.raises(ValueError, match="no column for group"):
            table_6_21_ks("soft_clay_and_mud", "driven_concrete")
        # Table 6-21 has four columns: 'II' alone does not pick one
        with pytest.raises(ValueError, match="no column for group"):
            table_6_21_ks("soft_clay_and_mud", "II")


# ==========================================================================
# 80. table_6_22_fp  (Table 6-22)
# ==========================================================================

class TestTable622Fp:
    @pytest.mark.parametrize("row", _LCPC_PRINTED, ids=[r[0] for r in _LCPC_PRINTED])
    def test_every_printed_cell(self, row):
        soil, _ks, fp, _kt = row
        for group, (value, careful) in zip(_LCPC_GROUP_NAMES, fp):
            assert table_6_22_fp(soil, group) == value
            # "Values in parentheses reflect careful construction."  A cell
            # with no value in parentheses keeps its one value.
            assert table_6_22_fp(soil, group, careful_construction=True) == (
                careful if careful is not None else value)

    def test_soft_clay(self):
        # fp/Pa = 0.15, a ratio (15 kPa at Pa = 101.325 kPa), not 15
        assert table_6_22_fp("soft_clay_and_mud", "II-A") == pytest.approx(0.15, rel=1e-9)

    def test_dense_sand(self):
        # Compact to very compact sand and gravel, Group I-A: 1.2 (1.5)
        assert table_6_22_fp("compact_to_very_compact_sand_and_gravel", "I-A") == pytest.approx(1.2, rel=1e-9)
        assert table_6_22_fp("compact_to_very_compact_sand_and_gravel", "I-A", True) == pytest.approx(1.5, rel=1e-9)

    def test_values_are_ratios(self):
        for soil, _ks, _fp, _kt in _LCPC_PRINTED:
            for group in _LCPC_GROUP_NAMES:
                assert 0.15 <= table_6_22_fp(soil, group, True) <= 1.5

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_6_22_fp("unknown", "driven")


# ==========================================================================
# 81. table_6_23_kt  (Table 6-23)
# ==========================================================================

class TestTable623Kt:
    @pytest.mark.parametrize("row", _LCPC_PRINTED, ids=[r[0] for r in _LCPC_PRINTED])
    def test_every_printed_cell(self, row):
        soil, _ks, _fp, kt = row
        assert table_6_23_kt(soil, "I") == kt[0]
        assert table_6_23_kt(soil, "II") == kt[1]
        # the table's two columns are Group I-A&B and Group II-A&B
        assert table_6_23_kt(soil, "I-A") == kt[0]
        assert table_6_23_kt(soil, "I-B") == kt[0]
        assert table_6_23_kt(soil, "II-A") == kt[1]
        assert table_6_23_kt(soil, "II-B") == kt[1]

    def test_medium_sand_driven(self):
        # Moderately compact sand and gravel, Group II: 0.5
        assert table_6_23_kt("moderately_compact_sand_and_gravel", "II") == pytest.approx(0.5, rel=1e-9)

    def test_loose_sand_bored(self):
        # Silt and loose sand, Group I: 0.4
        assert table_6_23_kt("silt_and_loose_sand", "I") == pytest.approx(0.4, rel=1e-9)

    def test_kt_is_a_fraction_of_qc(self):
        # the table's kt runs from 0.2 to 0.55
        values = [table_6_23_kt(soil, g) for soil, *_ in _LCPC_PRINTED for g in ("I", "II")]
        assert min(values) == 0.2
        assert max(values) == 0.55

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_6_23_kt("unknown", "driven")


# ==========================================================================
# 82. table_6_36_clm  (Table 6-36)
# ==========================================================================

class TestTable636Clm:
    """Table 6-36, Constants for Load and Moment Deflection Equations, PDF
    p. 500 (printed p. 462)."""

    @pytest.mark.parametrize("soil, ratio, fixity, a, n", [
        ("clay", "Pt/Pc", "free", 50.0, 1.822),
        ("clay", "Pt/Pc", "fixed", 14.0, 1.846),
        ("clay", "Mt/Mc", "n/a", 21.0, 1.412),
        ("sand", "Pt/Pc", "free", 119.0, 1.523),
        ("sand", "Pt/Pc", "fixed", 28.8, 1.500),
        ("sand", "Mt/Mc", "n/a", 36.0, 1.308),
    ])
    def test_every_printed_row(self, soil, ratio, fixity, a, n):
        result = table_6_36_clm(soil, ratio, fixity)
        assert result["a"] == a
        assert result["n"] == n

    def test_clay_free_load(self):
        result = table_6_36_clm("clay", "Pt/Pc", "free")
        assert result["a"] == pytest.approx(50.0, rel=1e-9)
        assert result["n"] == pytest.approx(1.822, rel=1e-9)
        assert "Eq. 6-66" in result["equations"]

    def test_sand_fixed_moment(self):
        # the Mt/Mc rows print fixity "N/A": a fixed-head moment row is
        # not in the table
        with pytest.raises(ValueError, match="no row"):
            table_6_36_clm("sand", "Mt/Mc", "fixed")
        result = table_6_36_clm("sand", "Mt/Mc", "N/A")
        assert result["a"] == pytest.approx(36.0, rel=1e-9)
        assert result["n"] == pytest.approx(1.308, rel=1e-9)
        assert "Eq. 6-68" in result["equations"]

    def test_returns_copy(self):
        result1 = table_6_36_clm("clay", "Pt/Pc", "free")
        result1["a"] = 999.0
        result2 = table_6_36_clm("clay", "Pt/Pc", "free")
        assert result2["a"] == pytest.approx(50.0, rel=1e-9)

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_6_36_clm("unknown", "Pt/Pc", "free")
        # the old argument order (fixity second, an equation name third)
        with pytest.raises(ValueError):
            table_6_36_clm("clay", "free", "deflection_from_load")


# ==========================================================================
# 83. table_6_37_clm  (Table 6-37)
# ==========================================================================

class TestTable637Clm:
    """Table 6-37, Coefficients for Estimating the Maximum Moment, PDF
    p. 502 (printed p. 464)."""

    def test_clay_free(self):
        result = table_6_37_clm("clay", "free")
        assert result["a"] == pytest.approx(0.855, rel=1e-9)
        assert result["n"] == pytest.approx(1.288, rel=1e-9)

    def test_clay_fixed(self):
        result = table_6_37_clm("clay", "fixed")
        assert result["a"] == pytest.approx(0.782, rel=1e-9)
        assert result["n"] == pytest.approx(1.249, rel=1e-9)

    def test_sand_free(self):
        result = table_6_37_clm("sand", "free")
        assert result["a"] == pytest.approx(4.28, rel=1e-9)
        assert result["n"] == pytest.approx(1.384, rel=1e-9)

    def test_sand_fixed(self):
        result = table_6_37_clm("sand", "fixed")
        assert result["a"] == pytest.approx(2.64, rel=1e-9)
        assert result["n"] == pytest.approx(1.300, rel=1e-9)
        assert "Eq. 6-70" in result["equations"]

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            table_6_37_clm("unknown", "free")


# ===========================================================================
# INTEGRATION & PUBLISHED REFERENCE VALUES
# ===========================================================================

class TestTable618Integration:
    """Chain table_6_18_Fnu → volumetric_strain."""

    def test_incompressible_soil(self):
        # nu = 0.5 (incompressible): Table 6-18 prints F_nu = 0, so the
        # volumetric strain of Eq. 6-26 is zero
        F_nu = table_6_18_Fnu(0.5, "circular")
        eps_v = volumetric_strain(500.0, 20000.0, F_nu)
        assert eps_v == pytest.approx(0.0, abs=1e-12)

    def test_higher_nu_less_strain(self):
        # Higher Poisson's ratio → lower Fnu → less volumetric strain
        # nu = 0.2: 500 x 0.63 / 20000 = 0.01575; nu = 0.4: 500 x 0.33 /
        # 20000 = 0.00825
        eps_low_nu = volumetric_strain(500.0, 20000.0, table_6_18_Fnu(0.2, "circular"))
        eps_high_nu = volumetric_strain(500.0, 20000.0, table_6_18_Fnu(0.4, "circular"))
        assert eps_low_nu == pytest.approx(0.01575, abs=1e-7)
        assert eps_high_nu == pytest.approx(0.00825, abs=1e-7)
        assert eps_high_nu < eps_low_nu


class TestLCPCIntegration:
    """Chain table_6_21/22/23 → lcpc_unit_shaft/base_resistance."""

    def test_shaft_soft_clay_driven(self):
        # qc = 1000 kPa (qc/Pa = 9.9, under 10), Pa = 101.3 kPa, soft clay
        # and mud, driven concrete pile (Group II-A): ks = 30, fp/Pa = 0.15
        k_s = table_6_21_ks("soft_clay_and_mud", "II-A")
        fp_over_Pa = table_6_22_fp("soft_clay_and_mud", "II-A")
        f_s = lcpc_unit_shaft_resistance(1000.0, 101.3, k_s, fp_over_Pa)
        # f_s = 1000 / 30 = 33.3 kPa, limited to 0.15 x 101.3 = 15.2 kPa
        assert f_s == pytest.approx(15.195, abs=0.001)

    def test_shaft_moderately_compact_clay_careful_construction(self):
        # qc = 3000 kPa (qc/Pa = 29.6), moderately compact clay, drilled
        # shaft without casing (Group I-A): ks = 40, fp/Pa = 0.35 (0.8)
        k_s = table_6_21_ks("moderately_compact_clay", "I-A")
        # f_s = 3000 / 40 = 75 kPa, limited to 0.35 x 101.325 = 35.46 kPa
        usual = lcpc_unit_shaft_resistance(
            3000.0, 101.325, k_s, table_6_22_fp("moderately_compact_clay", "I-A"))
        assert usual == pytest.approx(35.46, abs=0.01)
        # with careful construction the limit is 0.8 x 101.325 = 81.06 kPa,
        # so the 75 kPa stands
        careful = lcpc_unit_shaft_resistance(
            3000.0, 101.325, k_s, table_6_22_fp("moderately_compact_clay", "I-A", True))
        assert careful == pytest.approx(75.0, rel=1e-9)

    def test_base_dense_sand_driven(self):
        # qc,a = 15000 kPa (qc/Pa = 148, over 120), compact to very compact
        # sand and gravel, driven pile (Group II): kt = 0.4
        k_t = table_6_23_kt("compact_to_very_compact_sand_and_gravel", "II")
        q_b = lcpc_unit_base_resistance(15000.0, 101.3, k_t)
        # q_b = 0.4 x 15000 = 6000 kPa
        assert q_b == pytest.approx(6000.0, rel=1e-9)

    def test_bored_lower_than_driven_base(self):
        # Table 6-23: every Group I (drilled) kt is below its Group II
        # (driven and jacked) kt, so q_b = kt qc,a is lower for Group I.
        # Moderately compact sand and gravel: 0.4 against 0.5.
        k_t_driven = table_6_23_kt("moderately_compact_sand_and_gravel", "II")
        k_t_bored = table_6_23_kt("moderately_compact_sand_and_gravel", "I")
        assert (k_t_bored, k_t_driven) == (0.4, 0.5)
        q_b_driven = lcpc_unit_base_resistance(10000.0, 101.3, k_t_driven)
        q_b_bored = lcpc_unit_base_resistance(10000.0, 101.3, k_t_bored)
        assert q_b_bored == pytest.approx(4000.0, rel=1e-9)
        assert q_b_driven == pytest.approx(5000.0, rel=1e-9)
        for soil, *_ in _LCPC_PRINTED:
            assert table_6_23_kt(soil, "I") < table_6_23_kt(soil, "II")


class TestCLMIntegration:
    """Chain table_6_36/37 → clm_deflection_from_load / clm_max_moment,
    against Appendix B Example 6 (PDF pp. 686 and 688, printed pp. 648 and
    650): 49 piles, b = 12 in, Pc = 265 kips per pile, Mc = 45457 in-kips,
    piles in clay."""

    N_PILES, B_IN, P_C, M_C = 49, 12.0, 265.0, 45457.0

    def test_deflection_clay_free(self):
        # Table 6-36: clay, Pt/Pc, free → a = 50, n = 1.822
        consts = table_6_36_clm("clay", "Pt/Pc", "free")
        # Pt = 100, Pc = 500, b = 0.5: y = b a (Pt/Pc)^n
        # = 0.5 x 50 x 0.2^1.822 = 25 x 0.05327 = 1.332
        y = clm_deflection_from_load(100.0, 500.0, 0.5, consts["a"], consts["n"])
        assert y == pytest.approx(1.332, abs=0.001)

    def test_appendix_b_example_6_group_load(self):
        # Table B-34: at y_t = 0.29 in (free head) P_t,group = 197 kips; at
        # y_t = 0.11 in (fixed head) 249 kips, by
        # P_t,group = (49)(265 kips)[(1/a)(y_t / 12 in)]^(1/n)  (Eq. 6-67).
        # The printed y_t are rounded to 0.01 in: 0.29 in gives 196.6 kips;
        # 0.11 in gives 244.7 kips, and 249 kips is y_t = 0.1136 in.
        free = table_6_36_clm("clay", "Pt/Pc", "free")
        fixed = table_6_36_clm("clay", "Pt/Pc", "fixed")
        p_free = self.N_PILES * clm_load_from_deflection(
            0.29, self.B_IN, self.P_C, free["a"], free["n"])
        assert p_free == pytest.approx(197.0, abs=0.5)
        y_free = clm_deflection_from_load(
            197.0 / self.N_PILES, self.P_C, self.B_IN, free["a"], free["n"])
        assert y_free == pytest.approx(0.29, abs=0.005)
        y_fixed = clm_deflection_from_load(
            249.0 / self.N_PILES, self.P_C, self.B_IN, fixed["a"], fixed["n"])
        assert y_fixed == pytest.approx(0.11, abs=0.005)

    def test_appendix_b_example_6_maximum_moment(self):
        # Table B-34: M_max,corner = 18 ft-kips (free head, P_t,group = 197
        # kips) and 25 ft-kips (fixed head, 249 kips), by
        # M_max,corner = (1.2 / 12 in/ft) a Mc (Pt / Pc)^n with the Table
        # 6-37 constants (clay: 0.855, 1.288 free; 0.782, 1.249 fixed).
        for fixity, p_group, printed in (("free", 197.0, 18.0), ("fixed", 249.0, 25.0)):
            consts = table_6_37_clm("clay", fixity)
            m_max = clm_max_moment(p_group / self.N_PILES, self.P_C, self.M_C,
                                   consts["a"], consts["n"])
            assert 1.2 / 12.0 * m_max == pytest.approx(printed, abs=0.5)
        # the same page, free head at the 0.5 in service deflection: "the
        # resistance provided by the pile group is equal to 265 kips" and
        # the worked line ends "= 26 ft-kip".  The worked line writes
        # 259 kips in its fraction, which gives 25.1; the printed 26 is
        # what 265 kips gives (25.9).
        consts = table_6_37_clm("clay", "free")
        m_max = clm_max_moment(265.0 / self.N_PILES, self.P_C, self.M_C,
                               consts["a"], consts["n"])
        assert 1.2 / 12.0 * m_max == pytest.approx(26.0, abs=0.5)

    def test_max_moment_sand_free(self):
        # Table 6-37: sand, free → a = 4.28, n = 1.384
        consts = table_6_37_clm("sand", "free")
        # Pt = 200, Pc = 800, Mc = 1000: M_max = Mc a (Pt/Pc)^n
        # = 1000 x 4.28 x 0.25^1.384 = 4280 x 0.14682 = 628.4
        M_max = clm_max_moment(200.0, 800.0, 1000.0, consts["a"], consts["n"])
        assert M_max == pytest.approx(628.4, abs=0.1)

    def test_fixed_less_deflection_than_free(self):
        # Fixed head should give less deflection than free head
        free = table_6_36_clm("clay", "Pt/Pc", "free")
        fixed = table_6_36_clm("clay", "Pt/Pc", "fixed")
        y_free = clm_deflection_from_load(100.0, 500.0, 0.5,
                                           free["a"], free["n"])
        y_fixed = clm_deflection_from_load(100.0, 500.0, 0.5,
                                            fixed["a"], fixed["n"])
        assert y_fixed < y_free
