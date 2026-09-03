"""Tests for geotech_references.em_2107.tainter_gate_loads (Chapter 10 +
Appendix F).

Worked-example validation (doctrine: reproduce published numbers, never
tune) against Appendix F's Tainter-gate load example (Tables F.1-F.7,
printed pp. 437-445): side-seal friction (Fs=6.74 kips), hydrostatic load
by integration (P=53.85, Ph=50.0, Pv=15.081 kips; Mh=Mv=533.33 kip-ft;
Yp=10.67, Xp=35.36 ft), the simplified projection (Ph=50.0 kips), wire-rope
Case b (Q=68.89 kips), and trunnion friction (Rt=1385 kips, Ft=415.3 kips,
Mt=207.7 kip-ft).
"""

import math

import pytest

from geotech_references.em_2107.tainter_gate_loads import (
    seal_preset_force,
    side_seal_friction_force,
    nominal_friction_coefficients,
    wire_rope_tangent_load,
    wire_rope_wrap_reaction,
    hydrostatic_radial_force,
    hydrostatic_horizontal_component,
    hydrostatic_vertical_component,
    resultant_angle_from_horizontal,
    hydrostatic_moment,
    hydrostatic_resultant_location,
    hydrostatic_simplified_projection,
    trunnion_reaction_force,
    trunnion_friction_force,
    trunnion_friction_moment,
    table_10_load_combination,
    TABLE_10_LOAD_COMBINATIONS,
    anchorage_shear_friction_check,
    ice_debris_load,
    minimum_barge_impact_load,
    girder_deflection_limit,
    skin_plate_deflection_limit,
    skin_plate_thickness_bounds,
    minimum_rib_depth,
)


# Shared worked-example geometry (Appendix F Tables F.1-F.3, printed
# pp. 437-441).
R = 40.0
GAMMA_W = 0.0625
Y = 16.0
THETA1 = -0.412
THETA2 = 0.644


class TestSideSealFriction_AppendixFWorkedExample:
    def test_seal_preset_force(self):
        # Printed p. 438: delta=0.25 in, E=600 psi, I=1 in^4/ft, d1=4.0 in
        # -> S = 7.03 lb/ft.
        r = seal_preset_force(delta=0.25, e_seal=600.0, i_seal=1.0, d1=4.0)
        assert r["s_preset"] == pytest.approx(7.03, abs=0.01)

    def test_fs1_fs2_and_total(self):
        s_preset = seal_preset_force(0.25, 600.0, 1.0, 4.0)["s_preset"]
        r = side_seal_friction_force(
            mu_s=0.5, s_preset=s_preset, l_total=42.20,
            gamma_w=0.0625, d2=0.5, l1=42.20, l2=0.0, h=40.0,
        )
        assert r["fs1"] == pytest.approx(0.15, abs=0.01)
        assert r["fs2"] == pytest.approx(6.59, abs=0.01)
        assert r["fs_total"] == pytest.approx(6.74, abs=0.02)

    def test_nominal_friction_coefficients(self):
        r = nominal_friction_coefficients()
        assert r["side_seal"] == 0.5
        assert r["trunnion"] == 0.3
        assert r["load_factor"] == 1.4


class TestWireRopeLoads:
    def test_case_b_tangent_load_appendix_f_example(self):
        # Printed p. 444: theta_w=0.878 rad, T=78.44 kips -> Q=68.89 kips.
        r = wire_rope_tangent_load(theta_w=0.878, t=78.44)
        assert r["q_total"] == pytest.approx(68.89, abs=0.1)

    def test_case_c_wrap_reaction_formula(self):
        # E = 2*T*sin(B/2); at B=90 deg, sin(45deg)=0.7071.
        r = wire_rope_wrap_reaction(t=10.0, b_deg=90.0)
        assert r["e_reaction"] == pytest.approx(2 * 10.0 * math.sin(math.radians(45.0)))


class TestHydrostaticByIntegration_TableF3:
    """Verified against Table F.3 (printed p. 440): R=40 ft, gamma_w=0.0625
    kcf, Y=16 ft, theta1=-0.412 rad, theta2=0.644 rad."""

    def test_radial_force(self):
        r = hydrostatic_radial_force(R, GAMMA_W, Y, THETA1, THETA2)
        assert r["p"] == pytest.approx(53.85, abs=0.2)

    def test_horizontal_component(self):
        r = hydrostatic_horizontal_component(R, GAMMA_W, Y, THETA1, THETA2)
        assert r["ph"] == pytest.approx(50.0, abs=0.2)

    def test_vertical_component(self):
        r = hydrostatic_vertical_component(R, GAMMA_W, Y, THETA1, THETA2)
        assert r["pv"] == pytest.approx(15.081, abs=0.2)

    def test_resultant_angle(self):
        # Uses the printed Ph/Pv values directly (0.293 rad, printed p. 440).
        r = resultant_angle_from_horizontal(ph=50.0, pv=15.081)
        assert r["theta_p_rad"] == pytest.approx(0.293, abs=0.005)

    def test_moment(self):
        r = hydrostatic_moment(R, GAMMA_W, Y, THETA1, THETA2)
        assert r["mh"] == pytest.approx(533.33, abs=4.0)
        assert r["mv"] == r["mh"]

    def test_resultant_location(self):
        # Using the printed Mh/Mv/Ph/Pv values (printed p. 441).
        r = hydrostatic_resultant_location(mh=533.33, ph=50.0, mv=533.33, pv=15.081)
        assert r["yp"] == pytest.approx(10.67, abs=0.01)
        assert r["xp"] == pytest.approx(35.36, abs=0.01)


class TestHydrostaticSimplifiedProjection:
    def test_matches_integration_ph(self):
        # Printed pp. 429/440-441: H=40 ft, gamma_w=0.0625 kcf -> Ph=50.0
        # kips (matches the integration method exactly for this geometry).
        r = hydrostatic_simplified_projection(gamma_w=0.0625, h=40.0)
        assert r["ph"] == pytest.approx(50.0)

    def test_moment_arm(self):
        r = hydrostatic_simplified_projection(gamma_w=0.0625, h=40.0, el_trunnion=910.0, el_sill=886.0)
        assert r["y"] == pytest.approx(10.667, abs=0.01)


class TestTrunnionFriction_WorkedExample:
    """Verified against the worked example (printed p. 445): Rtx=-1336,
    Rty=-363.0 -> Rt=1385, theta_Rt=0.2653, Ft=415.3, Mt=207.7."""

    def test_reaction_force(self):
        r = trunnion_reaction_force(rtx=-1336.0, rty=-363.0)
        assert r["rt"] == pytest.approx(1385.0, abs=1.0)
        assert r["theta_rt_rad"] == pytest.approx(0.2653, abs=0.001)

    def test_friction_force(self):
        r = trunnion_friction_force(mu=0.3, rt=1385.0)
        assert r["ft"] == pytest.approx(415.3, abs=0.3)

    def test_friction_moment(self):
        r = trunnion_friction_moment(ft=415.3, r=0.5)
        assert r["mt"] == pytest.approx(207.7, abs=0.05)

    def test_full_chain(self):
        reaction = trunnion_reaction_force(rtx=-1336.0, rty=-363.0)
        friction = trunnion_friction_force(mu=0.3, rt=reaction["rt"])
        moment = trunnion_friction_moment(ft=friction["ft"], r=0.5)
        assert moment["mt"] == pytest.approx(207.7, abs=0.5)


class TestTable10LoadCombinations:
    def test_all_equations_present(self):
        for eq in ["10.2", "10.3", "10.4", "10.5", "10.6", "10.7", "10.8",
                   "10.9", "10.10", "10.11", "10.12", "10.13", "10.14"]:
            assert eq in TABLE_10_LOAD_COMBINATIONS

    def test_lookup_gate_jammed_combination(self):
        r = table_10_load_combination("10.7")
        assert "Fs" in r["formula"] and "Ft" in r["formula"]
        assert r["pdf_page"] == 8 + 147

    def test_unknown_equation(self):
        with pytest.raises(ValueError):
            table_10_load_combination("99.9")


class TestAnchorageShearFriction:
    def test_adequate(self):
        r = anchorage_shear_friction_check(vu=50.0, mu=0.6, r=100.0)
        assert r["capacity"] == pytest.approx(0.85 * 0.6 * 100.0)
        assert r["adequate"] is True

    def test_inadequate(self):
        r = anchorage_shear_friction_check(vu=90.0, mu=0.6, r=100.0)
        assert r["adequate"] is False


class TestNominalLoadsAndServiceability:
    def test_ice_debris_load(self):
        assert ice_debris_load()["load_kip_per_ft"] == 5.0

    def test_minimum_barge_impact(self):
        r = minimum_barge_impact_load(gate_width_ft=35.0)
        assert r["bi_min_kips"] == pytest.approx(175.0)

    def test_girder_deflection_between_end_frames(self):
        r = girder_deflection_limit(length=800.0, cantilever=False)
        assert r["limit"] == pytest.approx(1.0)

    def test_girder_deflection_cantilever(self):
        r = girder_deflection_limit(length=300.0, cantilever=True)
        assert r["limit"] == pytest.approx(1.0)

    def test_skin_plate_deflection_limit(self):
        r = skin_plate_deflection_limit(thickness=0.5)
        assert r["limit"] == pytest.approx(0.2)

    def test_skin_plate_thickness_bounds(self):
        r = skin_plate_thickness_bounds()
        assert r["min_in"] == 0.375
        assert r["max_recommended_in"] == 0.75

    def test_minimum_rib_depth(self):
        assert minimum_rib_depth()["min_depth_in"] == 8.0
