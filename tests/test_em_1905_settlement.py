"""EM 1110-1-1905 (2025) Chapters 6 and 7 functions checked against the
Appendix C worked examples (pp. 338-387). The examples print their inputs
rounded, so each check uses the printed inputs and a tolerance of the
printed result's last digit; where a print slip is known it is named."""

import inspect
import math

import pytest

from geotech_references.em_1905 import figures, settlement as st

approx = pytest.approx


# ---------------------------------------------------------------------------
# Example C-1: isolated footing on clay, e-log-p method (Table C-1)
# ---------------------------------------------------------------------------

def test_c1_step1_stresses():
    # Shelby #1 at 7.0 ft: 120 pcf, water at 5 ft (2.0 ft of water), sigma'_p 1.0
    sz = st.equation_6_1_total_vertical_stress([7.0], [120 / 2000])["sigma_z"]
    ev = st.equation_6_2_effective_vertical_stress(sz, 2.0 * 62.4 / 2000)
    assert ev["sigma_v_eff"] == approx(0.36, abs=0.005)
    oc = st.equation_6_3_overconsolidation(1.0, 0.36)
    assert oc["margin"] == approx(0.64)
    assert oc["OCR"] == approx(1.0 / 0.36)


def test_c1_step5_and_6_net_pressure():
    q = (20 + 150 / 2000 * 7.0 ** 2 * 2.0) / 7.0 ** 2
    assert q == approx(0.558, abs=0.0005)
    assert st.equation_6_5_net_bearing_pressure(q, 0.12)["q_net"] == approx(
        0.438, abs=0.001)


@pytest.mark.parametrize("z, i_printed, ds_printed", [
    (0.5, 1.0, 0.44), (2.0, 0.92, 0.40), (4.0, 0.63, 0.28),
    (6.5, 0.36, 0.16), (9.5, 0.20, 0.09), (12.5, 0.12, 0.05),
])
def test_c1_step7_influence_factor(z, i_printed, ds_printed):
    i = st.equation_6_8_influence_factor("square", 7.0, z, None)
    assert i["equation"] == "6-9"
    assert i["I_sigma"] == approx(i_printed, abs=0.005)
    ds = st.equation_6_6_induced_vertical_stress(i["I_sigma"], 0.558, 0.12)
    assert ds["delta_sigma_z"] == approx(ds_printed, abs=0.005)


# Table C-1, Step 9: (H, Cc/(1+e0), Cr/(1+e0), sigma'_zo, sigma'_p,
# sigma'_zf, delta_c)
_C1 = [
    (1, 0.113, 0.012, 0.15, 0.79, 0.59, 0.0071),
    (2, 0.113, 0.012, 0.24, 0.88, 0.64, 0.0102),
    (2, 0.113, 0.012, 0.33, 0.97, 0.61, 0.0064),
    (3, 0.113, 0.012, 0.40, 1.04, 0.56, 0.0053),
    (3, 0.048, 0.006, 0.49, 5.89, 0.58, 0.0013),
    (3, 0.048, 0.006, 0.59, 5.99, 0.64, 0.0006),
]


def test_c1_step9_consolidation_settlement():
    # The table prints Cc/(1 + e0) and Cr/(1 + e0); e0 = 0 with the ratios.
    total = 0.0
    for h, cc, cr, so, sp, sf, printed in _C1:
        r = st.equation_7_7_consolidation_settlement(h, 0.0, cc, cr, so, sf,
                                                     sp)
        assert r["equation"] == "7-8"
        assert r["settlement_ft"] == approx(printed, abs=0.0001)
        total += r["settlement_ft"]
    assert total == approx(0.0309, abs=0.0001)
    assert total * 12 == approx(0.37, abs=0.005)


# ---------------------------------------------------------------------------
# Example C-3: footing and areal fill on soft clay (Tables C-3b, C-3c)
# ---------------------------------------------------------------------------

# Table C-3b, Step 9: (H, Cc/(1+e0), Cr/(1+e0), sigma'_zo, sigma'_p,
# sigma'_zf, case, delta_c)
_C3 = [
    (2, 0.113, 0.012, 0.06, 0.70, 0.91, "7-9", 0.051),
    (1, 0.113, 0.012, 0.15, 0.79, 0.92, "7-9", 0.016),
    (2, 0.113, 0.012, 0.21, 0.85, 0.94, "7-9", 0.025),
    (2, 0.113, 0.012, 0.33, 0.97, 1.00, "7-9", 0.014),
    (3, 0.113, 0.012, 0.40, 1.04, 1.03, "7-8", 0.015),
    (3, 0.048, 0.006, 0.49, 5.89, 1.09, "7-8", 0.006),
    (3, 0.048, 0.006, 0.59, 5.99, 1.18, "7-8", 0.005),
    (4, 0.048, 0.006, 0.69, 6.09, 1.26, "7-8", 0.006),
    (5, 0.048, 0.006, 0.84, 6.24, 1.40, "7-8", 0.007),
]


def test_c3_step9_consolidation_cases():
    total = 0.0
    for h, cc, cr, so, sp, sf, case, printed in _C3:
        r = st.equation_7_7_consolidation_settlement(h, 0.0, cc, cr, so, sf, sp)
        assert r["equation"] == case
        assert r["settlement_ft"] == approx(printed, abs=0.0006)
        total += r["settlement_ft"]
    assert total == approx(0.145, abs=0.001)
    assert total * 12 == approx(1.74, abs=0.01)


def test_c3_step7b_fill_stress():
    r = st.equation_6_7_embankment_stress(0.5, 0.54)
    assert r["delta_sigma_z_fill"] == approx(0.54)


def test_c3c_time_rate():
    # Step 3: U = 0.74/1.10 = 67 % (Eq. 7-41 rearranged), taken as 70 %
    assert st.equation_7_41_settlement_at_time(0.74 / 1.10 * 100,
                                               1.10)["delta_ct"] == approx(0.74)
    tv = figures.figure_7_16_time_factor(70, None)
    assert tv["T_v"] == 0.403 and tv["interpolated"] is False
    cv = (0.471 * 10 + 0.372 * 15) / 25
    assert cv == approx(0.412, abs=0.0005)
    t = st.equation_7_42_time_for_consolidation(tv["T_v"], 25 / 2, 0.412)
    assert t["t_days"] == approx(152.8, abs=0.05)


def test_c3c_time_rate_from_an_oedometer_cv():
    # Eq. 7-43 gives Cv in in^2/day (Hdr in inches, p. 186); Eq. 7-42 (p. 184)
    # takes ft^2/day, as its list of symbols at the top of p. 185 gives Cv.
    # A made-up oedometer increment: a 1.0 in specimen
    # (Hdr = 0.5 in, two-way drainage) whose t50 gives Example C-3c's
    # 0.412 ft^2/day, chained into Step 4
    t50 = 0.197 * 0.5 ** 2 / (0.412 * 144)
    cv = st.equation_7_43_coefficient_of_consolidation("log time", 0.5, t50)
    assert cv["cv_in2_per_day"] == approx(0.412 * 144)
    assert cv["cv_ft2_per_day"] == approx(0.412)
    assert cv["units"] == {"cv_in2_per_day": "in^2/day",
                           "cv_ft2_per_day": "ft^2/day"}
    assert "Eq. 7-42 (p. 184) takes Cv in ft^2/day (p. 185)" in cv["notes"]
    assert "Cv is in ft^2/day (p. 185)" in st.equation_7_42_time_for_consolidation(
        0.403, 12.5, 0.412)["notes"]
    t = st.equation_7_42_time_for_consolidation(
        0.403, 25 / 2, cv_ft2_per_day=cv["cv_ft2_per_day"])
    assert t["t_days"] == approx(152.8, abs=0.05)
    # the in^2/day value in its place would give a time 144 times shorter
    wrong = st.equation_7_42_time_for_consolidation(0.403, 25 / 2,
                                                    cv["cv_in2_per_day"])
    assert wrong["t_days"] == approx(t["t_days"] / 144)


# ---------------------------------------------------------------------------
# Example C-2: superposition at points B and E (Table C-2, pp. 345-351)
# ---------------------------------------------------------------------------

# The I_sigma are read off Figure 6-8 (a chart, not coded) and printed; fed
# to Eq. 6-6 and Eq. 7-7 they give Steps 7 and 9. Per layer: (z, H,
# Cr/(1+e0), sigma'_zo, sigma'_p, I at B from the spread footing (x4),
# strip I1, I2 at B (x2), I at E from the strip (x4), spread I1, I2 at E
# (x2), printed delta_c at B, printed delta_c at E)
_C2 = [
    (0.5, 1, 0.012, 0.15, 0.79, 0.249, 0.250, 0.250, 0.240, 0.250, 0.248,
     0.0071, 0.0060),
    (2.0, 2, 0.012, 0.24, 0.88, 0.226, 0.247, 0.243, 0.137, 0.236, 0.198,
     0.0102, 0.0066),
    (4.0, 2, 0.012, 0.33, 0.97, 0.158, 0.233, 0.213, 0.076, 0.190, 0.115,
     0.0066, 0.0043),
    (6.5, 3, 0.012, 0.40, 1.04, 0.093, 0.205, 0.171, 0.048, 0.137, 0.060,
     0.0058, 0.0044),
    (9.5, 3, 0.006, 0.49, 5.89, 0.053, 0.170, 0.132, 0.033, 0.093, 0.032,
     0.0017, 0.0013),
    (12.5, 3, 0.006, 0.59, 5.99, 0.033, 0.141, 0.106, 0.025, 0.065, 0.020,
     0.0010, 0.0009),
]


def test_c2_superposition_through_eqs_6_6_and_7_7():
    q_spread = (20 + 150 / 2000 * 7.0 ** 2 * 2.0) / 7.0 ** 2   # 0.558
    q_strip = (0.6 + 150 * 2.0 * 2.0 / 2000) / 2.0              # 0.45
    assert q_spread == approx(0.558, abs=0.0005)
    assert q_strip == approx(0.45)
    sum_b = sum_e = 0.0
    dsig_b = []
    for (z, h, cr, szo, sp, ib, i1, i2, ie, j1, j2, pb, pe) in _C2:
        b = (st.equation_6_6_induced_vertical_stress(4 * ib, q_spread, 0.12)
             ["delta_sigma_z"]
             + st.equation_6_6_induced_vertical_stress(2 * (i1 - i2), q_strip,
                                                      0.12)["delta_sigma_z"])
        e = (st.equation_6_6_induced_vertical_stress(4 * ie, q_strip, 0.12)
             ["delta_sigma_z"]
             + st.equation_6_6_induced_vertical_stress(2 * (j1 - j2),
                                                      q_spread, 0.12)
             ["delta_sigma_z"])
        dsig_b.append(b)
        cc = 0.113 if cr == 0.012 else 0.048  # Cc/(1 + e0), Step 9
        rb = st.equation_7_7_consolidation_settlement(h, 0.0, cc, cr, szo,
                                                      szo + b, sp)
        re_ = st.equation_7_7_consolidation_settlement(h, 0.0, cc, cr, szo,
                                                       szo + e, sp)
        assert rb["equation"] == re_["equation"] == "7-8"
        # Delta-sigma_z is printed to 0.01 and carried rounded
        assert rb["settlement_ft"] == approx(pb, abs=0.0003), z
        assert re_["settlement_ft"] == approx(pe, abs=0.0003), z
        sum_b += rb["settlement_ft"]
        sum_e += re_["settlement_ft"]
    assert sum_b == approx(0.0324, abs=0.0002) and sum_b * 12 == approx(0.39, abs=0.005)
    assert sum_e == approx(0.0235, abs=0.0002) and sum_e * 12 == approx(0.28, abs=0.005)
    # Step 7a prints the sum at z = 12.5 ft as 0.18; it is 0.06 + 0.023 =
    # 0.08, the value Step 9 uses for layer 6
    assert dsig_b[-1] == approx(0.08, abs=0.002)


# ---------------------------------------------------------------------------
# Example C-4: excavation rebound and recompression (Table C-4)
# ---------------------------------------------------------------------------

def test_c4_steps4_to_6_unloading():
    # 8 ft at 100 pcf and 4 ft at 113 pcf removed: q'exc = 0.626, printed
    # 0.63 tsf (gamma_t the mean total unit weight of the soil removed);
    # Steps 5 and 6 carry the printed 0.63.
    g = (8 * 100 + 4 * 113) / 12 / 2000
    assert st.equation_7_35_excavation_unloading(g, 12.0, 1.0, 1.0)[
        "q_exc"] == approx(0.63, abs=0.005)
    g = 0.63 / 12
    lay2 = st.equation_7_35_excavation_unloading(g, 12.0, 4 * 0.248, 0.73)
    assert lay2["q_exc"] == approx(0.63)
    assert lay2["delta_sigma_z_exc"] == approx(0.63, abs=0.006)  # 0.625
    assert lay2["sigma_z_exc"] == approx(0.10, abs=0.006)
    lay3 = st.equation_7_35_excavation_unloading(g, 12.0, 4 * 0.188, 1.05)
    assert lay3["delta_sigma_z_exc"] == approx(0.47, abs=0.005)
    assert lay3["sigma_z_exc"] == approx(0.58, abs=0.005)


@pytest.mark.parametrize("kind, h, de, e, printed", [
    ("rebound", 8.0, 0.017, 0.947, 0.07),
    ("rebound", 14.0, 0.008, 0.991, 0.06),
    ("recompression", 6.0, 0.159, 0.964, 0.49),
    ("recompression", 8.0, 0.016, 0.999, 0.06),
])
def test_c4_steps7_and_12(kind, h, de, e, printed):
    r = st.equation_7_38_void_ratio_change_settlement(h, de, e, kind)
    assert r["equation"] == ("7-38" if kind == "rebound" else "7-40")
    assert r["movement_ft"] == approx(printed, abs=0.005)


def test_c4_step3_from_its_inputs():
    # Step 3 (p. 362) prints Layer 2's sigma'zgw as 7.3 tsf: it is 0.727
    # (Step 6 uses 0.73); Layer 3's is 1.01 as printed, while Step 6 uses
    # 1.05, so sigma'zexc there is 1.01 - 0.47 = 0.54, not 0.58
    w = 62.4 / 2000
    lay2 = st.equation_6_1_total_vertical_stress([8, 8.0], [0.05, 0.0565])
    s2 = st.equation_6_2_effective_vertical_stress(lay2["sigma_z"], 4 * w)
    assert s2["sigma_v_eff"] == approx(0.727, abs=0.0005)
    lay3 = st.equation_6_1_total_vertical_stress([8, 19.0], [0.05, 0.0565])
    s3 = st.equation_6_2_effective_vertical_stress(lay3["sigma_z"], 15 * w)
    assert s3["sigma_v_eff"] == approx(1.01, abs=0.005)
    assert s3["sigma_v_eff"] - 0.47 == approx(0.54, abs=0.005)


def test_c4_steps10_and_11_from_the_step8_pressure():
    # Step 8 (p. 363): q = (40 T + 7.35 T)/49 ft^2 - 0.25 tsf = 0.72 tsf;
    # Step 10 uses 1.43, Example B-4's qeq in ksf (p. 314), the same
    # pressure (1.43 ksf / 2 = 0.72 tsf)
    from geotech_references.em_1905 import equations as eq
    q = eq.equation_5_2_equivalent_bearing_pressure(
        40, 150 / 2000 * 7.0 ** 2 * 2.0, 7.0, 7.0, 8.0 * 62.4 / 2000)["q_eq"]
    assert q == approx(0.72, abs=0.005)
    assert 1.43 / 2 == approx(q, abs=0.005)
    szd = 0.49  # Step 9
    rows = [(2.0, 0.92, 0.87, 0.54, 1.41), (13.0, 0.12, 0.11, None, 0.83)]
    # the printed Delta-sigma_z follow from 1.43; from 0.72 they are 0.21
    # and 0.028 tsf, and Step 11's sigma'zf 0.75 and 0.745 tsf
    lay3 = st.equation_6_2_effective_vertical_stress(
        (8 * 100 + 15 * 113) / 2000, 17 * 62.4 / 2000)["sigma_v_eff"]
    assert lay3 == approx(0.717, abs=0.0005)
    expect = [(0.21, 0.75), (0.028, 0.745)]
    for (z, i_pr, ds_pr, szo, szf_pr), (ds_in, szf_in) in zip(rows, expect):
        i = st.equation_6_8_influence_factor("square", 7.0, z, None)["I_sigma"]
        assert i == approx(i_pr, abs=0.005)
        printed = st.equation_6_6_induced_vertical_stress(i_pr, 1.43, szd)
        assert printed["delta_sigma_z"] == approx(ds_pr, abs=0.006)
        ds = st.equation_6_6_induced_vertical_stress(i, q, szd)["delta_sigma_z"]
        assert ds == approx(ds_in, abs=0.005)
        base = 0.54 if szo else lay3
        assert base + printed["delta_sigma_z"] == approx(szf_pr, abs=0.01)
        assert base + ds == approx(szf_in, abs=0.005)


# ---------------------------------------------------------------------------
# Example C-5: footing on clay, Menard and Rousseau PMT method (Table C-5)
# ---------------------------------------------------------------------------

def test_c5_step7_harmonic_means():
    hm = st.equation_7_13_harmonic_mean
    assert hm([225, 292])["E"] == approx(254, abs=0.5)
    assert hm([292, 394, 25, 33, 52, 349, 287])["E"] == approx(69, abs=0.5)
    assert hm([287, 678, 1071])["E"] == approx(509, abs=0.5)
    assert hm([1220, 1724])["E"] == approx(1429, abs=0.5)
    assert hm([25, 33, 52])["E"] == approx(33.5, abs=0.05)  # Step 13, EL


def test_c5_step9_distortion_modulus():
    r = st.equation_7_14_equivalent_distortion_modulus(225, 254, 69, 509, 1429)
    assert r["E_d"] == approx(162, abs=0.5)


def test_c5_step12_and_17_settlement():
    args = dict(q=2.53, sigma_zD=0.156, B=8.0, E_d=162, E_c=225, alpha_d=1,
                alpha_c=1, lambda_d=1.1, lambda_c=1.1)
    r = st.equation_7_11_menard_settlement(soft_layers=[], **args)
    assert r["equation"] == "7-11"
    assert r["deviatoric_ft"] == approx(0.029, abs=0.0005)
    assert r["spherical_ft"] == approx(0.010, abs=0.0005)
    assert r["settlement_ft"] == approx(0.039, abs=0.0005)
    assert r["settlement_in"] == approx(0.47, abs=0.005)
    i14 = st.equation_6_8_influence_factor("square", 8.0, 14.0, None)
    assert i14["I_sigma"] == approx(0.129, abs=0.0005)
    r = st.equation_7_11_menard_settlement(
        soft_layers=[(2 / 3, 33.5, 0.129, 4.0)], **args)
    assert r["equation"] == "7-12"
    assert r["settlement_ft"] == approx(0.058, abs=0.0005)
    assert r["settlement_in"] == approx(0.70, abs=0.005)


# ---------------------------------------------------------------------------
# Example C-6: footing on mixed soils, DMT method (Table C-6b)
# ---------------------------------------------------------------------------

# Step 7, all 46 rows (pp. 373-374): (z, H, M, I_sigma, delta_sigma_z,
# delta in inches), as printed
_C6 = [
    (0.7, 0.7, 769, 0.998, 2.34, 0.026), (1.6, 0.9, 770, 0.969, 2.27, 0.032),
    (2.3, 0.7, 920, 0.914, 2.14, 0.020), (3.0, 0.7, 158, 0.834, 1.95, 0.104),
    (3.6, 0.6, 717, 0.757, 1.77, 0.018), (4.3, 0.7, 917, 0.666, 1.56, 0.014),
    (4.9, 0.6, 898, 0.593, 1.39, 0.011), (5.6, 0.7, 985, 0.516, 1.21, 0.010),
    (6.2, 0.6, 2264, 0.458, 1.07, 0.003), (6.9, 0.7, 2132, 0.399, 0.93, 0.004),
    (7.5, 0.6, 1559, 0.356, 0.83, 0.004), (8.2, 0.7, 1457, 0.313, 0.73, 0.004),
    (8.9, 0.7, 1115, 0.277, 0.65, 0.005), (9.5, 0.6, 789, 0.250, 0.58, 0.005),
    (10.2, 0.7, 858, 0.223, 0.52, 0.005), (10.8, 0.6, 858, 0.202, 0.47, 0.004),
    (11.5, 0.7, 459, 0.182, 0.43, 0.008), (12.1, 0.6, 412, 0.167, 0.39, 0.007),
    (12.8, 0.7, 1059, 0.151, 0.35, 0.003), (13.4, 0.6, 517, 0.139, 0.33, 0.005),
    (14.1, 0.7, 72, 0.127, 0.30, 0.035), (14.8, 0.7, 58, 0.117, 0.27, 0.040),
    (15.4, 0.6, 29, 0.109, 0.25, 0.063), (16.1, 0.7, 39, 0.100, 0.23, 0.050),
    (16.7, 0.6, 61, 0.094, 0.22, 0.026), (17.4, 0.7, 48, 0.087, 0.20, 0.035),
    (18.0, 0.6, 45, 0.081, 0.19, 0.030), (18.7, 0.7, 70, 0.076, 0.18, 0.021),
    (19.4, 0.7, 88, 0.071, 0.17, 0.016), (20.0, 0.6, 115, 0.067, 0.16, 0.010),
    (20.7, 0.7, 167, 0.062, 0.15, 0.007), (21.3, 0.6, 138, 0.059, 0.14, 0.007),
    (22.0, 0.7, 78, 0.056, 0.13, 0.014), (22.6, 0.6, 190, 0.053, 0.12, 0.005),
    (23.3, 0.7, 135, 0.050, 0.12, 0.007), (23.9, 0.6, 199, 0.047, 0.11, 0.004),
    (24.6, 0.7, 179, 0.045, 0.11, 0.005), (25.3, 0.7, 40, 0.043, 0.10, 0.021),
    (25.9, 0.6, 35, 0.041, 0.10, 0.020), (26.6, 0.7, 122, 0.039, 0.09, 0.006),
    (27.2, 0.6, 55, 0.037, 0.09, 0.011), (27.9, 0.7, 39, 0.035, 0.08, 0.018),
    (28.5, 0.6, 38, 0.034, 0.08, 0.015), (29.2, 0.7, 31, 0.032, 0.08, 0.020),
    (29.8, 0.6, 33, 0.031, 0.07, 0.016), (30.5, 0.7, 32, 0.030, 0.07, 0.018),
]


@pytest.mark.parametrize("z, h, m, i_pr, ds, d_in", _C6)
def test_c6_step7_rows(z, h, m, i_pr, ds, d_in):
    i = st.equation_6_8_influence_factor("square", 8.0, z, None)
    assert i["I_sigma"] == approx(i_pr, abs=0.0005)
    r = st.equation_7_10_constrained_modulus_settlement([(h, ds, m)])
    # delta_sigma_z is printed to 0.01: allow its half digit, and the
    # printed result's
    assert r["settlement_in"] == approx(d_in, abs=0.005 / m * h * 12 + 0.0005)


def test_c6_printed_stress_column_is_I_times_Q_over_A():
    # Every printed delta_sigma_z is I_sigma Q/A = I_sigma 150 T/64 ft^2
    # (2.34 I_sigma), within the rounding of I_sigma (0.0005) and of
    # delta_sigma_z (0.005); Step 6 and Eq. 6-6 give I_sigma (q - sigma'zD)
    # = I_sigma (2.53 - 0.15) = 2.38 I_sigma, which the first rows miss
    for z, h, m, i_pr, ds, d_in in _C6:
        assert ds == approx(i_pr * 150 / 64, abs=0.0065), z
    for z, h, m, i_pr, ds, d_in in _C6[:4]:
        eq66 = st.equation_6_6_induced_vertical_stress(i_pr, 2.53, 0.15)
        assert abs(eq66["delta_sigma_z"] - ds) > 0.02, z


def test_c6_step7_sum_and_what_the_inputs_give():
    # Step 7 prints sum delta_c = 0.081 in; its 46 rows total 0.812 in
    assert len(_C6) == 46
    assert sum(r[5] for r in _C6) == approx(0.812, abs=1e-9)
    printed_column = st.equation_7_10_constrained_modulus_settlement(
        [(h, ds, m) for z, h, m, i_pr, ds, d_in in _C6])
    assert printed_column["settlement_in"] == approx(0.813, abs=0.0005)
    # from the inputs: q = 2.53 tsf (Step 4), sigma'zD = 0.15 tsf (Step 5),
    # I_sigma by Eq. 6-9 and delta_sigma_z by Eq. 6-6 (Step 6)
    q = (150 + 150 / 2000 * 8.0 ** 2 * 2.5) / 8.0 ** 2
    assert q == approx(2.53, abs=0.005)
    layers = []
    for z, h, m, i_pr, ds, d_in in _C6:
        i = st.equation_6_8_influence_factor("square", 8.0, z, None)["I_sigma"]
        layers.append((h, st.equation_6_6_induced_vertical_stress(
            i, 2.53, 0.15)["delta_sigma_z"], m))
    inputs = st.equation_7_10_constrained_modulus_settlement(layers)
    assert inputs["settlement_in"] == approx(0.825, abs=0.0005)  # 0.83 in


# ---------------------------------------------------------------------------
# Example C-7: footing on sand (Tables C-7d, C-7e)
# ---------------------------------------------------------------------------

def test_c7d_factors():
    # sigma'_zp at D + B/2 = 6.5 ft, 125 pcf
    izp = st.equation_7_18_peak_strain_influence(3.31, 0.156, 6.5 * 125 / 2000)
    assert izp["I_zp"] == approx(0.779, abs=0.0005)
    c1 = st.equation_7_24_embedment_factor(3.31, 0.156)
    assert c1["C1"] == approx(0.975, abs=0.0005)
    assert c1["limit_governs"] is False and c1["C1_unlimited"] == c1["C1"]
    assert st.equation_7_25_creep_factor(50)["C2"] == approx(1.539, abs=0.001)
    assert st.equation_7_16_cpt_modulus(100, "axisymmetric")["E_s"] == 250
    assert st.equation_7_16_cpt_modulus(300, "axisymmetric")["E_s"] == 750


# Step 10: (z, H, Es, Iz printed, (Iz H)/Es printed)
_C7D = [
    (0.75, 1.5, 250, 0.227, 0.0014), (2.0, 1.0, 250, 0.439, 0.0018),
    (3.25, 1.5, 400, 0.651, 0.0024), (5.75, 3.5, 250, 0.665, 0.0093),
    (8.5, 2.0, 750, 0.489, 0.0013), (11.0, 3.0, 400, 0.324, 0.0024),
    (14.25, 3.5, 500, 0.114, 0.0008),  # printed 0.008: a slip, see below
]


def test_c7d_strain_influence_and_settlement():
    izp = 0.779
    layers = []
    for z, h, es, iz_pr, ratio in _C7D:
        r = st.equation_7_19_strain_influence_factor("axisymmetric", z, 8.0,
                                                     izp, None)
        # layer 5 computes 0.487 against 0.489 printed
        assert r["I_z"] == approx(iz_pr, abs=0.0025)
        assert iz_pr * h / es == approx(ratio, abs=0.00006)
        layers.append((iz_pr, h, es))
    r = st.equation_7_26_schmertmann_settlement(0.975, 1.539, 3.31, 0.156,
                                                layers)
    # The print sums to 0.0266 with layer 7 as 0.008 (0.114 x 3.5/500 is
    # 0.0008) and gets 0.125 ft (1.5 in); the layers sum to 0.0194.
    assert r["sum_Iz_H_over_Es"] == approx(0.0194, abs=0.0001)
    assert r["settlement_ft"] == approx(0.092, abs=0.001)
    assert 0.975 * 1.539 * (3.31 - 0.156) * 0.0266 == approx(0.125, abs=0.001)


def test_c7e_burland_burbidge():
    zi = st.equation_7_27_depth_of_influence(8.0)["Z_I"]
    assert zi == approx(6.13, abs=0.005)
    # (12 + 15 + 14)/3 = 13.7, printed and carried as 14
    ic = st.equation_7_28_compressibility_index(14)["I_c"]
    assert ic == approx(0.0087, abs=0.00005)
    c1 = st.equation_7_32_shape_factor("rectangular", 8.0, 8.0)["C1"]
    assert c1 == approx(1.0)
    c2 = st.equation_7_33_thickness_factor(zi, zi)
    assert c2["C2"] == 1.0 and c2["applies"] is False
    c3 = st.equation_7_34_time_factor(0.3, 0.2, 50)["C3"]
    assert c3 == approx(1.54, abs=0.005)
    # Step 9: sigma'_zo 0.35, sigma'_p 3.88; q + sigma'_zo <= sigma'_p
    r = st.equation_7_29_burland_burbidge_settlement(
        "overconsolidated", 3.31, 0.35, 3.88, 6.13, 0.0087, 1.0, 1.0, 1.54)
    assert r["equation"] == "7-30"
    assert r["settlement_ft"] == approx(0.10, abs=0.002)
    assert r["settlement_in"] == approx(1.2, abs=0.03)


# ---------------------------------------------------------------------------
# Made-up values (no worked example)
# ---------------------------------------------------------------------------

def test_influence_shapes_and_two_to_one():
    f = st.equation_6_8_influence_factor
    # z = B/2: square 1 - 0.5^1.76, circle 1 - 0.5^1.5, strip 1 - 0.5^2.60
    assert f("square", 4, 2, None)["I_sigma"] == approx(1 - 0.5 ** 1.76)
    assert f("circle", 4, 2, None)["I_sigma"] == approx(1 - 0.5 ** 1.5)
    assert f("strip", 4, 2, None)["I_sigma"] == approx(1 - 0.5 ** 2.60)
    # a rectangle with L = B is Eq. 6-10 at B/L = 1: exponents 2.00 and 1.76
    assert f("rectangle", 4, 2, 4)["I_sigma"] == approx(1 - 0.5 ** 1.76)
    t = st.equation_6_12_two_to_one_influence_factor
    assert t("rectangle", 2, 2, 2)["I_sigma"] == approx(0.25)
    assert t("circle", 4, 4, None)["I_sigma"] == approx(0.25)


def test_constrained_modulus_cases():
    m = st.equation_7_3_constrained_modulus
    # normally consolidated: sigma_z = sigma_p
    r = m(1.0, 1.0, 2.0, 1.0, 0.3, 0.03)
    assert r["equation"] == "7-3a"
    assert r["M"] == approx(2 * 1.0 / (math.log10(2) * 0.3))
    r = m(1.0, 1.0, 2.0, 3.0, 0.3, 0.03)
    assert r["equation"] == "7-3b"
    assert r["M"] == approx(2 * 1.0 / (math.log10(2) * 0.03))
    r = m(1.0, 1.0, 4.0, 2.0, 0.3, 0.03)
    assert r["equation"] == "7-4"
    assert r["M"] == approx(2 * 3.0 / (math.log10(2) * 0.03
                                       + math.log10(2) * 0.3))
    assert r["m_v"] == approx(1 / r["M"])


def test_indices_and_lab_equations():
    r = st.equation_7_5_compression_indices(0.80, 0.77, 1.0, 10.0, "Cr")
    assert r["Cr"] == approx(0.03) and r["equation"] == "7-5"
    r = st.equation_7_5_compression_indices(0.75, 0.45, 2.0, 20.0, "Cc")
    assert r["Cc"] == approx(0.30) and r["equation"] == "7-6"
    r = st.equation_7_43_coefficient_of_consolidation("log time", 0.5, 0.01)
    assert r["cv_in2_per_day"] == approx(0.197 * 0.25 / 0.01) and r["equation"] == "7-43"
    r = st.equation_7_43_coefficient_of_consolidation("root time", 0.5, 0.05)
    assert r["cv_in2_per_day"] == approx(0.848 * 0.25 / 0.05) and r["equation"] == "7-44"
    assert r["cv_ft2_per_day"] == approx(r["cv_in2_per_day"] / 144)
    r = st.equation_7_45_void_ratio_from_dial(1.0, 1.0, 0.0, -0.1)
    # Hs = 0.5 in; e = ((1.0 - 0.5) - 0.1)/0.5 = 0.8
    assert r["H_s"] == approx(0.5) and r["e"] == approx(0.8)
    assert st.equation_7_46_secondary_compression_index(
        0.80, 0.79, 100, 1000)["C_alpha"] == approx(0.01)
    r = st.equation_7_47_secondary_settlement(0.01, 1.0, 10.0, 1e3, 1e5)
    assert r["settlement_ft"] == approx(0.1)
    assert r["settlement_in"] == approx(1.2)
    assert st.equation_7_1_total_settlement(0.2, 1.0, 0.3)["delta_T"] == approx(1.5)


def test_burland_burbidge_other_cases():
    f = st.equation_7_29_burland_burbidge_settlement
    r = f("normally consolidated", 2.0, 0.5, None, 5.0, 0.01, 1.0, 1.0, 1.5)
    assert r["equation"] == "7-29"
    assert r["settlement_ft"] == approx(1.5 * 2.5 * 5.0 * 0.01)
    r = f("overconsolidated", 2.0, 0.5, 1.5, 5.0, 0.01, 1.0, 1.0, 1.5)
    assert r["equation"] == "7-31"
    assert r["settlement_ft"] == approx(1.5 * (2.5 - 1.0) * 5.0 * 0.01)
    assert st.equation_7_32_shape_factor("strip", None, None)["C1"] == 1.56
    assert st.equation_7_32_shape_factor("axisymmetric", None, None)["C1"] == 1.0
    c2 = st.equation_7_33_thickness_factor(3.0, 6.0)
    assert c2["C2"] == approx(0.75) and c2["applies"] is True
    assert st.equation_7_16_cpt_modulus(100, "plane strain")["E_s"] == 350


def test_strain_influence_plane_strain_and_rectangle():
    f = st.equation_7_19_strain_influence_factor
    assert f("plane strain", 4.0, 4.0, 0.7, None)["I_z"] == approx(0.7)
    assert f("plane strain", 8.0, 4.0, 0.7, None)["I_z"] == approx(
        0.331 * 0.7 * 2)
    a = f("axisymmetric", 2.0, 4.0, 0.7, None)["I_z"]
    c = f("plane strain", 2.0, 4.0, 0.7, None)["I_z"]
    r = f("rectangular", 2.0, 4.0, 0.7, 8.0)
    assert r["equation"] == "7-23"
    assert r["I_z"] == approx(a + 0.111 * (c - a) * 1)


def test_figure_7_16_interpolation_and_inverse():
    r = figures.figure_7_16_time_factor(None, 0.848)
    assert r["U_percent"] == 90.0 and r["interpolated"] is False
    r = figures.figure_7_16_time_factor(67, None)
    assert r["interpolated"] is True
    assert r["T_v"] == approx(0.287 + 0.7 * (0.403 - 0.287))
    assert figures.figure_7_16_time_factor(0, None)["T_v"] == 0.0
    assert figures.figure_7_16_time_factor(99.4, None)["T_v"] == 2.0


# ---------------------------------------------------------------------------
# Refusals
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("call", [
    lambda: st.equation_6_8_influence_factor("hexagon", 4, 2, None),
    lambda: st.equation_6_8_influence_factor("rectangle", 4, 2, None),
    lambda: st.equation_6_8_influence_factor("rectangle", 4, 2, 3),
    lambda: st.equation_6_8_influence_factor("square", 4, 2, 4),
    lambda: st.equation_6_6_induced_vertical_stress(1.2, 1.0, 0.1),
    lambda: st.equation_6_7_embankment_stress(0.6, 1.0),
    lambda: st.equation_7_7_consolidation_settlement(1, 1, 0.3, 0.03, 1.0,
                                                     2.0, 0.8),
    lambda: st.equation_7_7_consolidation_settlement(1, 1, 0.3, 0.03, 1.0,
                                                     0.9, 2.0),
    lambda: st.equation_7_3_constrained_modulus(1, 1.0, 0.9, 1.0, 0.3, 0.03),
    lambda: st.equation_7_19_strain_influence_factor("axisymmetric", 9.0,
                                                     4.0, 0.7, None),
    lambda: st.equation_7_19_strain_influence_factor("plane strain", 17.0,
                                                     4.0, 0.7, None),
    lambda: st.equation_7_19_strain_influence_factor("rectangular", 1.0,
                                                     4.0, 0.7, 48.0),
    lambda: st.equation_7_34_time_factor(0.3, 0.2, 2.0),
    lambda: st.equation_7_29_burland_burbidge_settlement(
        "dense", 2.0, 0.5, None, 5.0, 0.01, 1.0, 1.0, 1.5),
    lambda: st.equation_7_29_burland_burbidge_settlement(
        "overconsolidated", 2.0, 0.5, None, 5.0, 0.01, 1.0, 1.0, 1.5),
    lambda: st.equation_7_11_menard_settlement(2.53, 0.156, 8, 162, 225, 1.5,
                                               1, 1.1, 1.1, []),
    lambda: st.equation_7_43_coefficient_of_consolidation("fast", 0.5, 0.01),
    lambda: figures.figure_7_16_time_factor(100, None),
    lambda: figures.figure_7_16_time_factor(None, None),
    lambda: figures.figure_7_16_time_factor(50, 0.197),
])
def test_refusals(call):
    with pytest.raises(ValueError):
        call()


def test_c1_limit_applied_as_printed():
    # Eq. 7-24 (p. 174): C1 = 1 - 0.5 (sigma'zD/(q - sigma'zD)) >= 0.5;
    # q 0.3, sigma'zD 0.2 gives 1 - 0.5 x 2 = 0, so C1 = 0.5
    c1 = st.equation_7_24_embedment_factor(0.3, 0.2)
    assert c1["C1"] == 0.5 and c1["limit_governs"] is True
    assert c1["C1_unlimited"] == approx(0.0)
    assert "p. 174" in c1["notes"] and ">= 0.5" in c1["notes"]


def test_net_pressure_below_zero_is_flagged_not_refused():
    # Eqs. 6-5 and 6-6 (pp. 127, 131) print no sign condition on q - sigma'zD
    n = st.equation_6_5_net_bearing_pressure(0.3, 0.5)
    assert n["q_net"] == approx(-0.2) and n["net_negative"] is True
    assert "p. 127" in n["notes"] and "net unloading" in n["notes"]
    d = st.equation_6_6_induced_vertical_stress(0.5, 0.3, 0.5)
    assert d["delta_sigma_z"] == approx(-0.1) and d["net_negative"] is True
    assert "p. 131" in d["notes"]
    ok = st.equation_6_6_induced_vertical_stress(0.5, 0.5, 0.3)
    assert ok["net_negative"] is False and ok["notes"] == ""
    assert st.equation_6_5_net_bearing_pressure(0.5, 0.5)["net_negative"] is False
    # the settlement equations refuse it, saying it is the library's reading
    for call in (
            lambda: st.equation_7_11_menard_settlement(0.1, 0.156, 8, 162, 225,
                                                       1, 1, 1.1, 1.1, []),
            lambda: st.equation_7_18_peak_strain_influence(0.1, 0.2, 0.5),
            lambda: st.equation_7_24_embedment_factor(0.2, 0.2),
            lambda: st.equation_7_26_schmertmann_settlement(
                1.0, 1.0, 0.1, 0.2, [(0.5, 1.0, 100.0)])):
        with pytest.raises(ValueError, match="library refuses it"):
            call()


def test_menard_factor_range_and_a_stiff_layer():
    # Table 7-6 (p. 170) prints rheological factors from 1/4 to 1
    args = dict(q=2.53, sigma_zD=0.156, B=8.0, E_d=162, E_c=225,
                lambda_d=1.1, lambda_c=1.1)
    for a in (0.2, 1.5, 0.0):
        with pytest.raises(ValueError, match="Table 7-6"):
            st.equation_7_11_menard_settlement(alpha_d=a, alpha_c=1,
                                               soft_layers=[], **args)
        with pytest.raises(ValueError, match="Table 7-6"):
            st.equation_7_11_menard_settlement(alpha_d=1, alpha_c=1,
                                               soft_layers=[(a, 30, 0.5, 2)],
                                               **args)
    assert st.equation_7_11_menard_settlement(
        alpha_d=0.25, alpha_c=0.25, soft_layers=[], **args)["equation"] == "7-11"
    # EL above Ed: p. 167 prints no condition on it; computed, with a note
    r = st.equation_7_11_menard_settlement(alpha_d=1, alpha_c=1,
                                           soft_layers=[(2 / 3, 200, 0.3, 4)],
                                           **args)
    assert r["soft_layers_ft"] < 0
    assert "E_L above E_d" in r["notes"] and "no condition EL <= Ed" in r["notes"]
    plain = st.equation_7_11_menard_settlement(alpha_d=1, alpha_c=1,
                                               soft_layers=[(2 / 3, 30, 0.3, 4)],
                                               **args)
    assert plain["soft_layers_ft"] > 0 and "E_L above" not in plain["notes"]


def test_rising_void_ratio_refused_with_the_page():
    with pytest.raises(ValueError, match=r"Eq\. 7-46 \(p\. 191\)"):
        st.equation_7_46_secondary_compression_index(0.80, 0.81, 10, 100)
    # each index named as the list under its equation names it
    with pytest.raises(ValueError, match=r"Eq\. 7-5 \(p\. 157\) gives Cr, the slope "
                                         r"of the recompression curve"):
        st.equation_7_5_compression_indices(0.80, 0.81, 1.0, 2.0, "Cr")
    with pytest.raises(ValueError, match=r"Eq\. 7-6 \(p\. 158\) gives Cc, the slope "
                                         r"of the reconstructed field virgin compression"):
        st.equation_7_5_compression_indices(0.80, 0.81, 1.0, 2.0, "Cc")
    assert st.equation_7_46_secondary_compression_index(
        0.81, 0.80, 10, 100)["C_alpha"] == approx(0.01)
    assert st.equation_7_46_secondary_compression_index(
        0.80, 0.80, 10, 100)["C_alpha"] == 0


def test_time_factor_below_3_years_is_the_librarys_reading():
    with pytest.raises(ValueError, match="library's reading, not a condition"):
        st.equation_7_34_time_factor(0.3, 0.2, 2.0)
    assert st.equation_7_34_time_factor(0.3, 0.2, 30)["C3"] == approx(1.5)


def test_figure_7_16_valid_for_quotes_the_caption():
    r = figures.figure_7_16_time_factor(50, None)
    assert "linear distribution of excess pore water pressure with depth" in (
        r["valid_for"])


def test_preconsolidation_below_initial_stress_names_the_conditions():
    # sigma'p < sigma'zo is outside the conditions printed beside Eqs. 7-7
    # to 7-9 (pp. 159-160)
    with pytest.raises(ValueError, match="pp. 159-160"):
        st.equation_7_7_consolidation_settlement(1, 1, 0.3, 0.03, 1.0, 2.0, 0.8)


def test_settlements_in_feet_and_inches():
    # the lists of symbols give inches; the formulas with H in ft give ft
    # (Table C-1 Step 9, p. 342; Table C-6b Step 7, p. 373)
    s = st.equation_7_7_consolidation_settlement(2.0, 1.0, 0.3, 0.03, 1.0,
                                                 2.0, 1.0)
    assert s["settlement_in"] == approx(12 * s["settlement_ft"])
    assert "p. 342" in s["notes"]
    m = st.equation_7_10_constrained_modulus_settlement([(1.0, 1.0, 100.0)])
    assert m["settlement_ft"] == approx(0.01)
    assert m["settlement_in"] == approx(0.12)
    assert "p. 373" in m["notes"]


# ---------------------------------------------------------------------------
# Docstrings: the engineer's paragraph, then the print check, then Parameters
# ---------------------------------------------------------------------------

def _public(mod):
    return [f for n, f in inspect.getmembers(mod, inspect.isfunction)
            if not n.startswith("_") and f.__module__ == mod.__name__]


@pytest.mark.parametrize("fn", _public(st) + _public(figures),
                         ids=lambda f: f.__name__)
def test_docstring_layout(fn):
    doc = inspect.getdoc(fn)
    assert "Print check" in doc and "Parameters" in doc and "Raises" in doc
    assert doc.index("Print check") < doc.index("Parameters")


# Table 6-2 (p. 139), Boussinesq column: (B/z, I_sigma) beneath the center
# of a square uniformly loaded area
_T6_2 = [
    (20, 0.9992), (16, 0.9984), (12, 0.9968), (10, 0.9944), (8, 0.9892),
    (6, 0.9756), (5, 0.9604), (4, 0.9300), (3.6, 0.9096), (3.2, 0.8812),
    (2.8, 0.8408), (2.4, 0.7832), (2.0, 0.7008), (1.8, 0.6476),
    (1.6, 0.5844), (1.4, 0.5108), (1.2, 0.4276), (1.0, 0.3360),
    (0.8, 0.2410), (0.6, 0.1494), (0.4, 0.0716), (0.2, 0.0188),
]


@pytest.mark.parametrize("ratio, boussinesq", _T6_2)
def test_eq_6_9_against_table_6_2(ratio, boussinesq):
    # p. 144 says Eqs. 6-8 to 6-11 are within 5 percent of the Boussinesq
    # solution: Eq. 6-9 is within 0.012 of every row of Table 6-2 (the
    # difference is up to 7.7 percent of the value where I_sigma < 0.02).
    i = st.equation_6_8_influence_factor("square", ratio, 1.0, None)
    assert i["I_sigma"] == approx(boussinesq, abs=0.0125)


def test_c7c_menard_on_sand():
    # Table C-7c (pp. 381-382): harmonic means and Ed as printed
    hm = st.equation_7_13_harmonic_mean
    assert hm([78, 238])["E"] == approx(118, abs=0.6)  # 117.49
    assert hm([238, 320, 826])["E"] == approx(351, abs=0.5)
    assert hm([1419, 1065])["E"] == approx(1217, abs=0.5)
    assert hm([2508, 1059, 1128])["E"] == approx(1346, abs=0.5)
    ed = st.equation_7_14_equivalent_distortion_modulus(78, 118, 351, 1217,
                                                        1346)
    assert ed["E_d"] == approx(152, abs=0.5)
    r = st.equation_7_11_menard_settlement(3.31, 0.156, 8.0, 152, 78, 0.5,
                                           0.33, 1.1, 1.1, [])
    assert r["spherical_ft"] == approx(0.013, abs=0.0005)
    # Step 12 prints the deviatoric term as 0.015 ft and the sum as
    # 0.028 ft = 0.38 in; the typed-in numbers give 0.0193 ft, and
    # 0.019 + 0.013 = 0.032 ft is the printed 0.38 in (0.028 ft is 0.34 in).
    assert r["deviatoric_ft"] == approx(0.0193, abs=0.0001)
    assert r["settlement_in"] == approx(0.38, abs=0.01)


def test_c7c_step10_ratios_and_the_printed_first_term():
    # Step 10 (p. 382) prints Ed/pne = 152/8.5 = 9.5 and Ec/pne = 78/8.5 =
    # 4.9; with pne = 17 ksf = 8.5 tsf (Example B-7, p. 335) they are 17.9
    # and 9.2
    assert 152 / 8.5 == approx(17.9, abs=0.05)
    assert 78 / 8.5 == approx(9.2, abs=0.05)
    # Table 7-6, sand: over-consolidated above 12 gives 1/2, normally
    # consolidated 7 to 12 gives 1/3; so 17.9 gives the printed alpha_d 0.5
    # and 9.2 the printed alpha_c 0.33, while the printed 9.5 gives 1/3
    from geotech_references.em_1905 import tables as tb
    oc = tb.table_7_6_menard_rheological_factor("sand", "overconsolidated")
    nc = tb.table_7_6_menard_rheological_factor("sand", "normally consolidated")
    assert oc["alpha"] == approx(1 / 2) and nc["alpha"] == approx(1 / 3)
    # Step 12's printed 0.015 ft is the first term with exponent 1/3:
    # 2/(9 x 152) x (3.31 - 0.156) x 2.0 x 4.4^(1/3) = 0.0151 ft
    r = st.equation_7_11_menard_settlement(3.31, 0.156, 8.0, 152, 78, 1 / 3,
                                           0.33, 1.1, 1.1, [])
    assert r["deviatoric_ft"] == approx(0.0151, abs=0.00005)
