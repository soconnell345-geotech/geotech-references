"""EM 1110-1-1905 (2025) bearing capacity lookups against the manual's worked
examples of Appendix B (Examples B-1 to B-7, summary Tables B-1b to B-7c,
pp. 294-337).

The examples round each factor to two decimals and carry the rounded
values on, so a factor is compared to its printed two decimals within
0.01 (0.02 where the example rounded N or Nq first), and a capacity within
1 percent; feeding the examples' own rounded factors into equation 5-22
reproduces the printed capacity to 0.01 ksf.
"""

import math

import pytest

from geotech_references.em_1905 import equations as eq
from geotech_references.em_1905 import tables as tb


def near(value, printed, tol=0.01):
    return abs(value - printed) <= tol + 1e-9


# --- Table 2-1 and Table 5-5 ---------------------------------------------

def test_table_2_1_minimum_factors_of_safety():
    assert tb.table_2_1_minimum_factor_of_safety("Bearing capacity")["fs_min"] == 3.0
    assert tb.table_2_1_minimum_factor_of_safety("sliding")["fs_min"] == 2.0
    assert tb.table_2_1_minimum_factor_of_safety("uplift")["fs_min"] == 1.5
    over = tb.table_2_1_minimum_factor_of_safety("overturning")
    assert over["fs_min"] is None and "middle-third" in over["note"]
    assert "1.1" in tb.table_2_1_minimum_factor_of_safety("sliding")["note"]
    assert tb.table_2_1_minimum_factor_of_safety("uplift")["source"] == \
        "EM 1110-1-1905 (2025) Table 2-1, p. 10"
    with pytest.raises(ValueError):
        tb.table_2_1_minimum_factor_of_safety("settlement")


def test_table_5_5_k_values():
    # Table B-7c: PMT 0.9, CPT 0.1, SPT 0.6 drained; Table B-5e: PMT 0.7
    assert tb.table_5_5_in_situ_bearing_factor("PMT", "drained")["k"] == 0.9
    assert tb.table_5_5_in_situ_bearing_factor("CPT", "drained")["k"] == 0.1
    assert tb.table_5_5_in_situ_bearing_factor("SPT", "drained")["k"] == 0.6
    assert tb.table_5_5_in_situ_bearing_factor("PMT", "undrained")["k"] == 0.7
    assert tb.table_5_5_in_situ_bearing_factor("SPT", "undrained")["k"] == 0.35
    with pytest.raises(ValueError):
        tb.table_5_5_in_situ_bearing_factor("DMT", "drained")
    with pytest.raises(ValueError):
        tb.table_5_5_in_situ_bearing_factor("CPT", "partly drained")


# --- undrained: Examples B-1, B-2, B-4, B-5 ---------------------------------

@pytest.mark.parametrize("method, dc, q_ult, fs", [
    ("usace", 1.06, 3.51, 3.1), ("fhwa", 1.0, 3.32, 3.0)])
def test_example_b1_isolated_footing_on_clay(method, dc, q_ult, fs):
    # Table B-1b: 7 ft x 7 ft, Df 2 ft, su 0.5 ksf, q0 0.24 ksf, Q 40 kips
    r = eq.ultimate_bearing_capacity_undrained(
        method, su=0.5, q0=0.120 * 2, B_eff=7, L_eff=7, Df=2, H=0, V=54.7,
        theta_deg=None, alpha_b_deg=0, alpha_g_deg=0, d_g=None)
    assert near(r["Nc"], 5.14) and near(r["sc"], 1.2) and near(r["dc"], dc)
    assert r["ic"] == r["bc"] == r["gc"] == 1.0
    assert r["q_ult"] == pytest.approx(q_ult, rel=0.01)
    wf = 7 * 7 * 2 * 0.150                      # Step 5: 14.7 kips
    assert near(wf, 14.7)
    qe = eq.equation_5_2_equivalent_bearing_pressure(40, wf, 7, 7, 0)
    assert near(qe["q_eq"], 1.12)
    f = eq.equation_5_23_factor_of_safety(q_ult, qe["q_eq"])
    # Step 6b prints FS = 3.32/1.12 = 3.0 >= 3 OK; unrounded it is 2.97,
    # under the minimum, which the function says
    assert round(f["FS"], 1) == fs
    assert f["meets_minimum"] is (method == "usace")


@pytest.mark.parametrize("method, dc, q_ult", [
    ("usace", 1.2, 3.32), ("fhwa", 1.0, 2.81)])
def test_example_b2_continuous_footing_on_clay(method, dc, q_ult):
    # Table B-2b: B 2 ft continuous, Df 2 ft, su 0.5 ksf, q0 0.24 ksf
    r = eq.ultimate_bearing_capacity_undrained(
        method, su=0.5, q0=0.24, B_eff=2, L_eff=None, Df=2, H=0, V=1.8,
        theta_deg=None, alpha_b_deg=0, alpha_g_deg=0, d_g=None)
    assert r["sc"] == 1.0 and near(r["dc"], dc)
    assert near(r["q_ult"], q_ult)
    qe = eq.equation_5_2_equivalent_bearing_pressure(1.2, 0.6, 2, None, 0)
    assert near(qe["q_eq"], 0.9)


@pytest.mark.parametrize("method, q_ult", [("usace", 5.78), ("fhwa", 5.47)])
def test_example_b4_water_table_uplift(method, q_ult):
    # Table B-4c: su 0.85 ksf, gamma 0.113 kcf, q0 0.226 ksf, Q 80 kips;
    # u at the base 0.125 ksf (end of construction) and 0.499 ksf (long term)
    r = eq.ultimate_bearing_capacity_undrained(
        method, su=0.85, q0=0.226, B_eff=7, L_eff=7, Df=2, H=0, V=94.7,
        theta_deg=None, alpha_b_deg=0, alpha_g_deg=0, d_g=None)
    assert r["q_ult"] == pytest.approx(q_ult, rel=0.01)
    for u, q_eq in ((0.125, 1.81), (0.499, 1.43)):
        qe = eq.equation_5_2_equivalent_bearing_pressure(80, 14.7, 7, 7, u)
        assert near(qe["q_eq"], q_eq)


def test_example_b5_undrained_three_ways():
    # Table B-5e: 8 ft x 8 ft, Df 2.5 ft, q0 0.31 ksf
    for method, q_ult in (("usace", 21.23), ("fhwa", 20.05)):
        r = eq.ultimate_bearing_capacity_undrained(
            method, su=3.2, q0=0.125 * 2.5, B_eff=8, L_eff=8, Df=2.5, H=0,
            V=324, theta_deg=None, alpha_b_deg=0, alpha_g_deg=0, d_g=None)
        assert r["q_ult"] == pytest.approx(q_ult, rel=0.01), method
    # PMT: s = p*le 15.8 ksf, k 0.7, sc 1.2, dc 1.06 -> 14.38 ksf
    k = tb.table_5_5_in_situ_bearing_factor("PMT", "undrained")["k"]
    r = eq.equation_5_25_in_situ_bearing_capacity(
        "undrained", k, 15.8, 0.31, 1.2, 1.06, 1, 1, 1)
    assert near(r["q_ult"], 14.38)
    # punch-through into the weak layer: su 0.6 ksf, Hs 8.5 ft
    for method, q2, q_ult in (("usace", 4.23, 17.98), ("fhwa", 4.01, 17.04)):
        r2 = eq.ultimate_bearing_capacity_undrained(
            method, su=0.6, q0=0.31, B_eff=8, L_eff=8, Df=2.5, H=0, V=324,
            theta_deg=None, alpha_b_deg=0, alpha_g_deg=0, d_g=None)
        assert r2["q_ult"] == pytest.approx(q2, rel=0.01), method
        p = eq.equation_5_17_punching_capacity(21.23, q2, 8.5, 8, 8, 8, 8)
        assert near(p["spreading_factor"], 4.25)
        assert near(p["q_ult"], q_ult, 0.02) and p["governs"] == "punching"
    # Table B-5d averages the three: it prints (3.6 + 3.4 + 2.8)/3 = 9.9/3
    # = 3.3; the sum is 9.8, and 9.8/3 also rounds to 3.3
    assert round((3.6 + 3.4 + 2.8) / 3, 1) == 3.3


# --- drained: Examples B-3, B-6, B-7 ------------------------------------

#: (example, method): inputs and the summary rows, Tables B-3c, B-6c, B-7c
DRAINED = {
    ("B-3", "usace"): dict(phi=34, B=7, Df=2, Dw=13, gamma=0.135,
                           rows=dict(N=3.54, Nq=29.46, sq=1.35, dq=1.05,
                                     N_gamma=31.17, s_gamma=1.35, d_gamma=1.05),
                           ratio=1.0, q_ult=32.15),
    ("B-3", "fhwa"): dict(phi=34, B=7, Df=2, Dw=13, gamma=0.135,
                          rows=dict(N=3.54, Nq=29.46, sq=1.67, dq=1.07,
                                    N_gamma=41.09, s_gamma=0.6, d_gamma=1.0),
                          ratio=1.0, q_ult=25.86),
    ("B-6", "usace"): dict(phi=31, B=8, Df=2.5, Dw=8, gamma=0.12,
                           rows=dict(N=3.12, Nq=20.6, sq=1.31, dq=1.06,
                                     N_gamma=18.5, s_gamma=1.31, d_gamma=1.06),
                           ratio=0.83, q_ult=18.82),
    ("B-6", "fhwa"): dict(phi=31, B=8, Df=2.5, Dw=8, gamma=0.12,
                          rows=dict(N=3.12, Nq=20.6, sq=1.60, dq=1.09,
                                    N_gamma=26.0, s_gamma=0.6, d_gamma=1.0),
                          ratio=0.78, q_ult=16.62),
    ("B-7", "usace"): dict(phi=32, B=8, Df=2.5, Dw=20, gamma=0.125, q0=0.31,
                           rows=dict(N=3.25, Nq=23.1, sq=1.33, dq=1.06,
                                     N_gamma=21.9, s_gamma=1.33, d_gamma=1.06),
                           ratio=1.0, q_ult=25.5),
    ("B-7", "fhwa"): dict(phi=32, B=8, Df=2.5, Dw=20, gamma=0.125, q0=0.31,
                          rows=dict(N=3.25, Nq=23.1, sq=1.62, dq=1.08,
                                    N_gamma=30.1, s_gamma=0.60, d_gamma=1.0),
                          ratio=1.0, q_ult=21.6),
}


@pytest.mark.parametrize("key", sorted(DRAINED))
def test_drained_examples(key):
    ex, method = key
    d = DRAINED[key]
    g = eq.equation_5_19_effective_unit_weight(d["gamma"], d["Dw"], d["Df"],
                                               d["B"], method)
    assert near(g["ratio"], d["ratio"])
    q0 = d.get("q0", d["gamma"] * d["Df"])      # Row 8 as printed
    r = eq.ultimate_bearing_capacity_drained(
        method, phi_deg=d["phi"], c=0, q0=q0, gamma_eff=g["gamma_eff"],
        B_eff=d["B"], L_eff=d["B"], Df=d["Df"], H=0, V=1, theta_deg=None,
        alpha_b_deg=0, alpha_g_deg=0, d_g=None)
    for name, printed in d["rows"].items():
        # Nq and N-gamma are printed to 3 or 4 figures from a rounded N
        tol = max(0.02, 0.01 * printed) if name in ("Nq", "N_gamma") else 0.01
        assert near(r[name], printed, tol), (key, name, r[name])
    for name in ("iq", "bq", "gq", "i_gamma", "b_gamma", "g_gamma"):
        assert r[name] == 1.0
    assert r["q_ult"] == pytest.approx(d["q_ult"], rel=0.01), key
    # the example's own rounded factors give its capacity (Eq. 5-22)
    w = d["rows"]
    gamma_eff = d["gamma"] * d["ratio"]
    q = eq.equation_5_22_ultimate_bearing_capacity(
        0, q0, gamma_eff, d["B"], 0, w["Nq"], w["N_gamma"],
        1, 1, 1, 1, 1, w["sq"], w["dq"], 1, 1, 1,
        w["s_gamma"], w["d_gamma"], 1, 1, 1)
    assert near(q["q_ult"], d["q_ult"], 0.1), (key, q["q_ult"])


def test_example_b3_punch_through():
    # Table B-3c: weak clay su 0.5 ksf below a 6 ft strong layer
    for method, q2, q_ult in (("usace", 3.54, 12.21), ("fhwa", 3.35, 11.56)):
        r = eq.ultimate_bearing_capacity_undrained(
            method, su=0.5, q0=0.27, B_eff=7, L_eff=7, Df=2, H=0, V=104.7,
            theta_deg=None, alpha_b_deg=0, alpha_g_deg=0, d_g=None)
        assert r["q_ult"] == pytest.approx(q2, rel=0.01)
        p = eq.equation_5_17_punching_capacity(32.15, q2, 6, 7, 7, 7, 7)
        assert near(p["spreading_factor"], 3.45)
        assert near(p["q_ult"], q_ult)


def test_example_b6_punch_through():
    for method, q2, q_ult in (("usace", 2.92, 20.12), ("fhwa", 2.77, 19.09)):
        r = eq.ultimate_bearing_capacity_undrained(
            method, su=0.4, q0=0.3, B_eff=8, L_eff=8, Df=2.5, H=0, V=324,
            theta_deg=None, alpha_b_deg=0, alpha_g_deg=0, d_g=None)
        assert r["q_ult"] == pytest.approx(q2, rel=0.01)
        p = eq.equation_5_17_punching_capacity(18.82, q2, 13, 8, 8, 8, 8)
        assert near(p["spreading_factor"], 6.89)
        # the summary prints the punching capacity; the strong layer's
        # 18.82 ksf (USACE) is the lesser, so Eq. 5-17's min is 18.82
        assert near(p["q_ult_punching"], q_ult, 0.02)
        assert p["governs"] == "strong layer" and p["q_ult"] == 18.82
    qe = eq.equation_5_2_equivalent_bearing_pressure(300, 24, 8, 8, 0)
    assert near(qe["q_eq"], 5.06)


def test_example_b7_in_situ_methods():
    # Table B-7c: N = 3 for the in situ methods, sq 1.3, dq 1.05
    sd = tb.table_5_2_usace_shape_depth_factors(3, 8, 8, 2.5)
    assert near(sd["sq"], 1.3) and near(sd["dq"], 1.05)
    for test, s, q_ult in (("PMT", 17, 21.2), ("CPT", 225, 31), ("SPT", 26.4, 21.9)):
        k = tb.table_5_5_in_situ_bearing_factor(test, "drained")["k"]
        r = eq.equation_5_25_in_situ_bearing_capacity(
            "drained", k, s, 0.31, 1.3, 1.05, 1, 1, 1)
        assert near(r["q_ult"], q_ult, 0.05), test
        exact = eq.equation_5_25_in_situ_bearing_capacity(
            "drained", k, s, 0.3125, sd["sq"], sd["dq"], 1, 1, 1)
        assert exact["q_ult"] == pytest.approx(q_ult, rel=0.01), test


# --- the other equations and the refusals ---------------------------------

def test_eccentricity_and_circular_footing():
    r = eq.equation_5_4_effective_dimensions(B=8, L=10, V=200, M_B=100, M_L=0)
    assert r["e_B"] == 0.5 and r["B_eff"] == 7 and r["L_eff"] == 10
    assert r["A_eff"] == 70 and r["within_middle_third"] is True
    assert eq.equation_5_4_effective_dimensions(6, None, 10, 12, 0)[
        "within_middle_third"] is False
    c = eq.equation_5_9_circular_effective_footing(A=math.pi * 25, e=0)
    assert c["R_eq"] == pytest.approx(5) and c["A_eff"] == pytest.approx(math.pi * 25)
    assert c["B_eq"] == pytest.approx(10) and c["L_eq"] == pytest.approx(10)
    with pytest.raises(ValueError):
        eq.equation_5_9_circular_effective_footing(A=10, e=5)


def test_sliding_and_uplift():
    d = eq.equation_5_31_developed_strength(2.0, 30, 0.4)
    assert d["phi_d_deg"] == pytest.approx(math.degrees(math.atan(math.tan(math.radians(30)) / 2)))
    assert d["c_d"] == 0.2
    f = eq.equation_5_34_developed_earth_forces(0.12, 3, 2.0, 0.5, 0.0, 1)
    assert f["P_pd"] == pytest.approx(0.5 * 0.12 * 3 * 2.0 * 3)
    with pytest.raises(ValueError, match="must be >= 0"):
        eq.equation_5_34_developed_earth_forces(0.12, 3, 2.0, 0.5, 0.2, 1)
    s = eq.equation_5_29_sliding_factor_of_safety_drained(
        N=100, U=10, delta_deg=25, ca_over_c=0, c_eff=0, A=50, H=20,
        P_ad=0, P_pd=0)
    assert s["FS"] == pytest.approx(90 * math.tan(math.radians(25)) / 20)
    u = eq.equation_5_30_sliding_factor_of_safety_undrained(0.5, 1.0, 40, 5, 0, 0)
    assert u["FS"] == 4.0
    up = eq.equation_5_36_uplift_factor_of_safety(30, 20, 0, 40)
    assert up["FS"] == 1.25 and up["meets_minimum"] is False


def test_limits_printed_beside_a_formula_are_refused_not_cut():
    # USACE dc = 1 + 0.2 Df/B' <= 1.5 (Table 5-4): Df/B' = 3 gives 1.6
    with pytest.raises(ValueError, match="1.5"):
        tb.table_5_4_undrained_factors("usace", 2, 2, 6, 0, 10, 1, None, 0, 0, None)
    # AASHTO dq <= 1.4 (Table 5-2, note a)
    with pytest.raises(ValueError, match="1.4"):
        tb.table_5_2_aashto_shape_depth_factors(30, 2, 2, 40)
    # the AASHTO ground factors are in AASHTO (2020), not printed here
    with pytest.raises(ValueError, match="AASHTO"):
        tb.table_5_4_undrained_factors("aashto", 6, 6, 2, 0, 10, 1, None, 0, 10, 3)
    with pytest.raises(ValueError):
        tb.table_5_2_bearing_capacity_factors(0, "usace")
    with pytest.raises(ValueError):
        tb.table_5_2_bearing_capacity_factors(30, "meyerhof")


def test_inclination_and_slope_factors():
    # USACE, Table 5-3: beta = atan(H/V)
    i = tb.table_5_3_usace_load_inclination_factors(10, 100, 30)
    beta = math.degrees(math.atan(0.1))
    assert i["iq"] == pytest.approx((1 - beta / 90) ** 2) and i["ic"] == i["iq"]
    assert i["i_gamma"] == pytest.approx((1 - beta / 30) ** 2)
    with pytest.raises(ValueError):
        tb.table_5_3_usace_load_inclination_factors(100, 100, 30)
    a = tb.table_5_3_aashto_load_inclination_factors(10, 100, 5, 10, 0, 30, 0)
    nL = (2 + 0.5) / (1 + 0.5)
    assert a["n"] == pytest.approx(nL)
    assert a["iq"] == pytest.approx((1 - 0.1) ** nL)
    assert a["i_gamma"] == pytest.approx((1 - 0.1) ** (nL + 1))
    b = tb.table_5_3_base_inclination_factors(10, 30)
    assert b["bq"] == pytest.approx((1 - 10 / 57 * math.tan(math.radians(30))) ** 2)
    g = tb.table_5_3_usace_ground_inclination_factors(20, 0, 5, 30)
    assert g["gq0"] == pytest.approx((1 - math.tan(math.radians(20))) ** 2)
    assert g["gq"] == g["gq0"]
    far = tb.table_5_3_usace_ground_inclination_factors(20, 25, 5, 30)
    assert far["gq"] == 1.0 and far["gc"] == 1.0
    u = tb.table_5_4_undrained_factors("usace", 6, 6, 2, 10, 100, 1, None, 0, 20, 6)
    assert u["ic"] == pytest.approx(1 - 1.3 * 0.1)
    assert u["gc0"] == pytest.approx(1 - 20 / 147.3)
    assert u["gc"] == pytest.approx(u["gc0"] + (1 - u["gc0"]) * 6 / 12)


def test_effective_unit_weight_and_geometric_mean():
    assert eq.equation_5_19_effective_unit_weight(0.12, 2.5, 2.5, 8, "usace")["ratio"] == 0.45
    assert eq.equation_5_19_effective_unit_weight(0.12, 0, 2.5, 8, "fhwa")["ratio"] == 0.5
    # Table C-5, Step 15: pne = (2.2 x 3.1 x 4.0)^(1/3) = 3.01 tsf
    assert near(eq.equation_5_24_geometric_mean([2.2, 3.1, 4.0])["s"], 3.01)


def test_every_function_says_where_it_is_printed():
    import inspect
    for mod in (eq, tb):
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("_") or fn.__module__ != mod.__name__:
                continue
            doc = inspect.getdoc(fn)
            assert "Print check" in doc or "print check" in doc.lower(), name
            assert "Parameters" in doc and "Raises" in doc, name
