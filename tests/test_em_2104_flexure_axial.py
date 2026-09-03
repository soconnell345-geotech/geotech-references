"""Tests for geotech_references.em_2104.flexure_axial (Chapter 4 + Appendix B
investigation equations).

Worked-example validation against the manual's own printed examples
(doctrine: reproduce published numbers, never tune):
  - Appendix C-2 (singly reinforced beam analysis, phi*Mn = 137.5 k-ft).
  - Appendix C-3 / Table C-1 (doubly reinforced slab analysis).
  - Appendix D-4 (combined flexure+axial doubly reinforced wall,
    tension-controlled Appendix B path: ku = 0.357, phi*Pn = 63 kips,
    phi*Mn = 2880 k-in).
"""

import pytest

from geotech_references.em_2104.flexure_axial import (
    aci_beta1,
    eccentricity_ratio,
    balanced_strain_kb,
    bresler_biaxial_check,
    max_axial_capacity_singly,
    balanced_eccentricity_singly,
    tension_controlled_capacity_singly,
    compression_controlled_capacity_singly,
    max_axial_capacity_doubly,
    balanced_eccentricity_doubly,
    tension_controlled_capacity_doubly,
    compression_controlled_capacity_doubly,
    max_axial_tension_capacity,
    tension_flexure_eccentricity_range,
    tension_controlled_by_compression_side_ku,
    tension_between_layers_capacity,
    pure_tension_capacity,
    pure_flexure_singly,
    pure_flexure_doubly,
)


class TestAciBeta1:
    def test_le_4000_psi(self):
        assert aci_beta1(3.0) == 0.85
        assert aci_beta1(4.0) == 0.85

    def test_between_4000_and_8000_psi(self):
        assert aci_beta1(5.0) == pytest.approx(0.80)
        assert aci_beta1(6.0) == pytest.approx(0.75)

    def test_ge_8000_psi(self):
        assert aci_beta1(9.0) == 0.65

    def test_psi_unit(self):
        assert aci_beta1(4000, unit="psi") == 0.85
        assert aci_beta1(5000, unit="psi") == pytest.approx(0.80)


class TestEccentricityRatio:
    def test_matches_appendix_d4_moment_input(self):
        # Appendix D-4 computes e' from the base Mu = 209 k-ft (not the
        # offset-inclusive Mu1 = 225 k-ft) plus d - h/2 (printed p. 78):
        # e' = 209*12/55 + (16.295 - 20/2) = 51.9 in.
        r = eccentricity_ratio(mu=209.0 * 12, pu=55.0, d=16.295, h=20.0)
        assert r["e_prime"] == pytest.approx(51.9, abs=0.05)
        assert r["e_prime_over_d"] == pytest.approx(51.9 / 16.295, rel=1e-3)


class TestBalancedStrainKb:
    def test_matches_appendix_c4(self):
        # Appendix C-4 Point 3: fc'=4 ksi -> beta1=0.85, fy=60 ksi ->
        # kb = 0.5031 (printed p. 60).
        r = balanced_strain_kb(beta1=0.85, fy=60.0)
        assert r["kb"] == pytest.approx(0.5031, abs=1e-3)


class TestBreslerBiaxial:
    def test_at_capacity_equals_one(self):
        r = bresler_biaxial_check(mux=50.0, phi_m0x=100.0, muy=0.0, phi_m0y=80.0)
        assert r["lhs"] == pytest.approx(0.5 ** 1.5)
        assert r["adequate"] is True

    def test_over_capacity(self):
        r = bresler_biaxial_check(mux=100.0, phi_m0x=100.0, muy=80.0, phi_m0y=80.0)
        assert r["lhs"] > 1.0
        assert r["adequate"] is False

    def test_square_uses_k_175(self):
        r = bresler_biaxial_check(mux=50, phi_m0x=100, muy=0, phi_m0y=80,
                                   member_shape="square_or_circular")
        assert r["k"] == 1.75


class TestSinglyReinforcedInvestigation:
    def test_max_axial_capacity_matches_c4_point2(self):
        # Appendix C-4 Point 2 (printed p. 59): fc'=4, fy=60, As=2.0 sq in,
        # Ag=12*24=288 sq in -> Pn(max) = 873.9 kips (no phi applied there,
        # so pass phi=1.0 to reproduce the printed intermediate Pn(max)).
        r = max_axial_capacity_singly(phi=1.0, fc_prime=4.0, ag=288.0, as_=2.0, fy=60.0)
        assert r["phi_pn_max"] == pytest.approx(873.9, abs=0.2)

    def test_tension_and_compression_controlled_agree_at_balanced_point(self):
        # Continuity check: at e'/d = eb'/d exactly, both branches should
        # give matching ku (~kb) and phi_Pn (self-consistency, not a printed
        # value).
        beta1 = aci_beta1(4.0)
        kb = balanced_strain_kb(beta1, fy=60.0)["kb"]
        rho = 0.006423  # Appendix C-2 section
        eb = balanced_eccentricity_singly(kb, rho, fy=60.0, fc_prime=4.0)
        eb_over_d = eb["eb_prime_over_d"]
        d, b, h, phi = 20.5, 12.0, 24.0, 0.9
        tc = tension_controlled_capacity_singly(eb_over_d, rho, 60.0, 4.0, b, d, h, phi)
        cc = compression_controlled_capacity_singly(
            eb_over_d, rho, 60.0, 4.0, b, d, h, phi, beta1, kb=kb,
        )
        assert tc["ku"] == pytest.approx(cc["ku"], rel=1e-2)
        assert tc["phi_pn"] == pytest.approx(cc["phi_pn"], rel=1e-2)


class TestDoublyReinforcedTensionControlled_AppendixD4:
    """Full reproduction of Appendix D-4 (printed pp. 77-79)."""

    def setup_method(self):
        self.beta1 = aci_beta1(4.0)
        self.d = 16.295
        self.dprime = 3.705
        self.rho = 3.40 / (12 * self.d)
        self.rho_prime = 1.87 / (12 * self.d)
        self.kb = balanced_strain_kb(self.beta1, fy=60.0)["kb"]
        e = eccentricity_ratio(mu=209.0 * 12, pu=55.0, d=self.d, h=20.0)
        self.e_over_d = e["e_prime_over_d"]

    def test_kb(self):
        assert self.kb == pytest.approx(0.503, abs=1e-3)

    def test_balanced_eccentricity_confirms_tension_controlled(self):
        eb = balanced_eccentricity_doubly(
            self.kb, self.beta1, self.dprime / self.d, self.rho, self.rho_prime,
            fy=60.0, fc_prime=4.0,
        )
        # Printed: eb' = 23.2 in -> eb'/d = 23.2/16.295 = 1.424; manual finds
        # e' (51.9) > eb' (23.2), section controlled by tension.
        assert eb["eb_prime_over_d"] == pytest.approx(23.2 / self.d, abs=0.03)
        assert self.e_over_d > eb["eb_prime_over_d"]

    def test_capacity_matches_printed_numbers(self):
        r = tension_controlled_capacity_doubly(
            e_prime_over_d=self.e_over_d, dprime_over_d=self.dprime / self.d,
            rho=self.rho, rho_prime=self.rho_prime, fy=60.0, fc_prime=4.0,
            beta1=self.beta1, b=12.0, d=self.d, h=20.0, phi=0.9, kb=self.kb,
        )
        assert r["ku"] == pytest.approx(0.357, abs=0.01)
        assert r["phi_pn"] == pytest.approx(63.0, rel=0.01)
        assert r["phi_mn"] == pytest.approx(2880.0, rel=0.01)

    def test_max_axial_capacity_not_governing(self):
        # Printed p. 79: phi*Pn(max) = 802 kips >> phi*Pn = 63 kips, so the
        # Eq B-22 cap does not govern.
        r = max_axial_capacity_doubly(
            phi=0.9, fc_prime=4.0, ag=12 * 20, rho=self.rho,
            rho_prime=self.rho_prime, fy=60.0, bd=12 * self.d,
        )
        assert r["phi_pn_max"] == pytest.approx(802.0, rel=0.02)


class TestPureFlexureSingly_AppendixC2:
    def test_matches_c2_moment_capacity(self):
        r = pure_flexure_singly(as_=1.58, fy=60.0, fc_prime=4.0, b=12.0, d=20.5, phi=0.90)
        assert r["a"] == pytest.approx(2.324, abs=1e-3)
        assert r["phi_mn"] == pytest.approx(1649.9, abs=1.0)  # in-kips
        assert r["phi_mn"] / 12.0 == pytest.approx(137.5, abs=0.1)  # ft-kips


class TestPureFlexureDoubly_AppendixC3:
    def test_tension_steel_only_matches_table_c1(self):
        # Table C-1 "Tension Steel Only" column: a=11.76 in, M=25,976.5 in-k.
        r = pure_flexure_singly(as_=8.0, fy=60.0, fc_prime=4.0, b=12.0, d=60.0)
        assert r["a"] == pytest.approx(11.76, abs=0.01)
        assert r["mn"] == pytest.approx(25976.5, rel=1e-4)

    def test_compression_steel_matches_table_c1(self):
        # Table C-1 "Compression Steel" column: a=8.62 in, c=10.14 in,
        # M=26,515.2 in-k. Reproduces the general equilibrium (non-yielding
        # compression steel) path.
        r = pure_flexure_doubly(as_=8.0, as_prime=4.0, fc_prime=4.0, fy=60.0,
                                 b=12.0, d=60.0, dprime=6.0)
        assert r["a"] == pytest.approx(8.62, abs=0.01)
        assert r["c"] == pytest.approx(10.14, abs=0.01)
        assert r["mn"] == pytest.approx(26515.2, rel=5e-4)
        assert r["compression_steel_yields"] is False


class TestTensionPlusFlexure:
    def test_max_tension_capacity(self):
        r = max_axial_tension_capacity(phi=0.9, rho=0.01, rho_prime=0.005, fy=60.0, bd=720.0)
        assert r["phi_pn_max"] == pytest.approx(0.8 * 0.9 * 0.015 * 60.0 * 720.0)

    def test_eccentricity_range(self):
        r = tension_flexure_eccentricity_range(h=24.0, d=20.0)
        assert r["lower_bound"] == 0.0
        assert r["upper_bound"] == pytest.approx(1 - 24 / 40.0)

    def test_ku_compression_side_negative_ecc(self):
        r = tension_controlled_by_compression_side_ku(
            e_prime_over_d=-0.5, rho=0.01, fy=60.0, fc_prime=4.0,
        )
        assert isinstance(r["ku"], float)

    def test_between_layers_capacity_runs(self):
        r = tension_between_layers_capacity(
            e_prime_over_d=0.3, dprime_over_d=0.15, rho=0.01, rho_prime=0.008,
            fy=60.0,
        )
        assert "ku" in r and "fs_prime" in r

    def test_pure_tension(self):
        r = pure_tension_capacity(phi=0.9, as_=3.0, as_prime=2.0, fy=60.0)
        assert r["phi_pn"] == pytest.approx(0.9 * 5.0 * 60.0)
