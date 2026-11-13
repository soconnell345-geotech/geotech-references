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
    compression_steel_stress_at_ku,
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
        # Eq B-31's fs' is below fy here, so Eq B-33's ku is used as printed
        assert r["limit_governs"] is False and "ku_cubic" not in r

    def test_max_axial_capacity_not_governing(self):
        # Printed p. 79: phi*Pn(max) = 802 kips >> phi*Pn = 63 kips, so the
        # Eq B-22 cap does not govern.
        r = max_axial_capacity_doubly(
            phi=0.9, fc_prime=4.0, ag=12 * 20, rho=self.rho,
            rho_prime=self.rho_prime, fy=60.0, bd=12 * self.d,
        )
        assert r["phi_pn_max"] == pytest.approx(802.0, rel=0.02)


class TestDoublyReinforcedCompressionControlled:
    """Eqs B-34 to B-39 on a made-up section (f'c 4 ksi, fy 60 ksi, 12 x
    20 in, d 16.5, d' 3.5, e'/d 0.8, below the balanced eb'/d)."""

    def _call(self, **kw):
        beta1 = aci_beta1(4.0)
        args = dict(e_prime_over_d=0.8, dprime_over_d=3.5 / 16.5,
                    rho=0.01, rho_prime=0.006, fy=60.0, fc_prime=4.0,
                    beta1=beta1, b=12.0, d=16.5, h=20.0, phi=0.65,
                    kb=balanced_strain_kb(beta1, fy=60.0)["kb"])
        args.update(kw)
        return compression_controlled_capacity_doubly(**args)

    def test_steel_stress_within_yield(self):
        r = self._call()
        assert r["ku"] > balanced_strain_kb(aci_beta1(4.0), fy=60.0)["kb"]
        assert -60.0 <= r["fs"] <= 60.0
        assert r["phi_pn"] > 0

    def test_non_physical_bound_refused(self):
        # REF-76: fy, es and ec set the bound on fs; not positive is
        # refused (fy <= 0 used to turn the bound inside out).
        for kw in ({"fy": 0.0}, {"fy": -60.0}, {"es": 0.0}, {"ec": -0.003}):
            with pytest.raises(ValueError, match="must be > 0"):
                self._call(**kw)


def _b23_b24(ku, e, dpr, rho, rhop, fc, fs, fsp):
    """Eq B-23 (Pu/phi over b d) and Eq B-24 (Pu e'/phi over b d^2), ksi, as
    printed on p. 45 (EM_1110-2-2104_2025.pdf page 51); with rho' = 0 they
    are Eqs B-2 and B-5 (printed p. 42). In equilibrium B-23 * e'/d = B-24."""
    force = 0.85 * fc * ku + fsp * rhop - fs * rho
    moment = 0.425 * fc * (2 * ku - ku ** 2) + fsp * rhop * (1 - dpr)
    return force * e, moment


class TestYieldedSteelSolvedFromEquilibrium:
    """Ruling 42 on REF-76, second part. The cubics (Eqs B-21, B-33, B-39)
    are derived with the steel elastic; where a steel stress is past yield
    at the cubic's root, ku is solved again from the manual's equilibrium
    equations with that stress at yield (Eqs B-23 and B-24, printed p. 45;
    B-32, p. 47; B-2 and B-5, p. 42), or the call is refused where the
    tension steel has yielded. Sections are made up: rho 0.01, rho' 0.01,
    fy 60 ksi, f'c 4 ksi, beta1 0.85, b 12 in, d 20 in, h 24 in."""

    SEC = dict(dprime_over_d=0.1, rho=0.01, rho_prime=0.01, fy=60.0,
               fc_prime=4.0, beta1=0.85, b=12.0, d=20.0, h=24.0)

    @pytest.mark.parametrize("e, phi_pn, phi_pn_cubic", [
        (0.8, 396.0, 424.8), (0.65, 524.6, 566.6), (0.5, 695.5, 749.1)])
    def test_compression_steel_yielded(self, e, phi_pn, phi_pn_cubic):
        # The independent check's force-and-moment solution with fs' = fy:
        # phi Pn 396.0, 524.6, 695.5 kips; holding fs' at fy with the
        # cubic's ku gave 400.3, 538.2, 717.3.
        r = compression_controlled_capacity_doubly(
            e_prime_over_d=e, phi=0.65, **self.SEC)
        assert r["phi_pn"] == pytest.approx(phi_pn, rel=1e-3)
        assert r["phi_pn_cubic"] == pytest.approx(phi_pn_cubic, rel=1e-3)
        assert r["fs_prime"] == 60.0 and r["limit_governs"] is True
        assert r["fs_prime_unlimited"] > 60.0 and r["ku"] < r["ku_cubic"]
        # the returned ku, fs and fs' satisfy Eqs B-23 and B-24 ...
        lhs, rhs = _b23_b24(r["ku"], e, 0.1, 0.01, 0.01, 4.0, r["fs"], 60.0)
        assert lhs == pytest.approx(rhs, rel=1e-9)
        assert r["fs"] == pytest.approx(87.0 * (0.85 - r["ku"]) / r["ku"])
        assert r["phi_pn"] == pytest.approx(0.65 * lhs / e * 12 * 20)
        # ... and the cubic's ku with fs' at fy does not
        kc = r["ku_cubic"]
        lhs, rhs = _b23_b24(kc, e, 0.1, 0.01, 0.01, 4.0,
                            87.0 * (0.85 - kc) / kc, 60.0)
        assert lhs != pytest.approx(rhs, rel=1e-3)

    def test_note_says_what_was_done(self):
        r = compression_controlled_capacity_doubly(
            e_prime_over_d=0.8, phi=0.65, **self.SEC)
        assert r["ku"] == pytest.approx(0.6493, abs=1e-4)
        assert r["ku_cubic"] == pytest.approx(0.6546, abs=1e-4)
        assert r["fs_prime_unlimited"] == pytest.approx(75.70, abs=0.01)
        for words in ("the compression steel has yielded",
                      "derived with the compression steel not yielded",
                      "Eqs B-23 and B-24 (printed p. 45)", "with fs' = fy",
                      "phi Pn = 396.0 kips",
                      "a lower capacity than the cubic's 424.8 kips",
                      "library's reading"):
            assert words in r["note"]

    def test_no_limit_unchanged(self):
        # d'/d 0.35: B-37 stays below fy, so Eqs B-34 to B-39 as printed;
        # the numbers are those of the release before (ku is B-39's root).
        r = compression_controlled_capacity_doubly(
            0.8, 0.35, 0.01, 0.006, 60.0, 4.0, 0.85, 12.0, 16.5, 20.0, 0.65)
        assert r["limit_governs"] is False
        assert "note" not in r and "ku_cubic" not in r
        ku = r["ku"]
        assert ku == pytest.approx(0.6152455, abs=1e-7)
        assert r["fs_prime"] == pytest.approx(87.0 * (ku - 0.85 * 0.35) / ku)
        assert r["fs_prime"] == pytest.approx(44.9314, abs=1e-4)
        assert r["phi_pn"] == pytest.approx(261.19204, abs=1e-5)
        ck = 87.0 / (0.425 * 4.0)      # Eq B-39, printed p. 48
        assert (ku ** 3 + 2 * (0.8 - 1) * ku ** 2
                + ck * (0.016 * 0.8 - 0.006 * 0.65) * ku
                - 0.85 * ck * (0.006 * 0.35 * 0.15 + 0.01 * 0.8)
                ) == pytest.approx(0.0, abs=1e-10)

    def test_tension_steel_yielded_refused(self):
        # e'/d 2.0 is above the balanced ratio: B-36's fs is above fy at
        # the cubic's root, so paragraph B-3f does not cover the section.
        with pytest.raises(ValueError, match="controlled by tension") as ex:
            compression_controlled_capacity_doubly(
                2.0, 0.3, 0.01, 0.006, 60.0, 4.0, 0.85, 12.0, 16.5, 20.0, 0.65)
        assert "Eq B-36 gives fs = 95.45 ksi" in str(ex.value)
        assert "tension_controlled_capacity_doubly" in str(ex.value)
        assert "kb was not given" in str(ex.value)
        # the same with fs' past yield too (d'/d 0.1)
        with pytest.raises(ValueError, match="controlled by tension"):
            compression_controlled_capacity_doubly(
                e_prime_over_d=2.0, phi=0.65, kb=0.5031, **self.SEC)

    def test_both_regimes_meet_at_the_balanced_point(self):
        # At e'/d = eb'/d (Eq B-28, fs' at fy there) both functions now
        # return ku = kb and the same capacity; the cubics gave 0.4951
        # (B-33) and 0.4991 (B-39).
        kb = balanced_strain_kb(0.85, 60.0)["kb"]
        eb = balanced_eccentricity_doubly(
            kb, 0.85, 0.1, 0.01, 0.01, 60.0, 4.0)["eb_prime_over_d"]
        tc = tension_controlled_capacity_doubly(
            e_prime_over_d=eb, phi=0.9, kb=kb, **self.SEC)
        cc = compression_controlled_capacity_doubly(
            e_prime_over_d=eb, phi=0.9, kb=kb, **self.SEC)
        assert tc["ku"] == pytest.approx(kb, abs=1e-9)
        assert cc["ku"] == pytest.approx(kb, abs=1e-9)
        assert tc["phi_pn"] == pytest.approx(cc["phi_pn"], rel=1e-9)
        assert tc["ku_cubic"] == pytest.approx(0.4951, abs=1e-4)
        assert cc["ku_cubic"] == pytest.approx(0.4991, abs=1e-4)

    def test_tension_controlled_compression_steel_yielded(self):
        # Just above the balanced ratio B-31 is above fy at B-33's root;
        # the page prints fs' (<= fy) (printed p. 47), and ku is solved
        # again from Eq B-32 with fs' = fy (a quadratic in ku).
        kb = balanced_strain_kb(0.85, 60.0)["kb"]
        eb = balanced_eccentricity_doubly(
            kb, 0.85, 0.1, 0.01, 0.01, 60.0, 4.0)["eb_prime_over_d"]
        e = 1.02 * eb
        r = tension_controlled_capacity_doubly(
            e_prime_over_d=e, phi=0.9, kb=kb, **self.SEC)
        assert r["limit_governs"] is True and r["fs_prime"] == 60.0
        assert r["fs_prime_unlimited"] == pytest.approx(64.23, abs=0.01)
        k = 60.0 / (0.425 * 4.0)
        ku = (1 - e) + ((e - 1) ** 2 + k * 0.01 * 0.9) ** 0.5   # rho = rho'
        assert r["ku"] == pytest.approx(ku, abs=1e-9)
        lhs, rhs = _b23_b24(r["ku"], e, 0.1, 0.01, 0.01, 4.0, 60.0, 60.0)
        assert lhs == pytest.approx(rhs, rel=1e-9)
        assert r["phi_pn"] == pytest.approx(355.9, abs=0.1)
        assert r["phi_pn_cubic"] == pytest.approx(352.9, abs=0.1)
        assert 0.85 * 1.1 / 2 < r["ku"] < kb          # the bracket
        for words in ("the page prints fs' (<= fy) beside Eq B-31",
                      "Eq B-32 (printed p. 47", "with fs' = fy",
                      "library's reading"):
            assert words in r["note"]
        # further from the balanced point B-31 is below fy: Eq B-33 as printed
        r = tension_controlled_capacity_doubly(
            e_prime_over_d=1.5 * eb, phi=0.9, kb=kb, **self.SEC)
        assert r["limit_governs"] is False and "ku_cubic" not in r
        assert r["ku"] == pytest.approx(0.3080, abs=1e-4)
        assert r["phi_pn"] == pytest.approx(149.97, abs=0.01)

    def test_tension_controlled_refuses_a_compression_controlled_section(self):
        kb = balanced_strain_kb(0.85, 60.0)["kb"]
        with pytest.raises(ValueError, match="not controlled by tension"):
            tension_controlled_capacity_doubly(
                e_prime_over_d=0.9, phi=0.9, kb=kb, **self.SEC)

    def test_singly_tension_steel_yielded_refused(self):
        # Eq B-19 (printed p. 44) above fy at B-21's root: controlled by
        # tension, paragraph B-2d (Eq B-16) applies.
        with pytest.raises(ValueError, match="controlled by tension") as ex:
            compression_controlled_capacity_singly(
                2.0, 0.01, 60.0, 4.0, 12.0, 20.0, 24.0, 0.65, 0.85)
        assert "Eq B-19 gives fs = 87.38 ksi" in str(ex.value)
        assert "tension_controlled_capacity_singly" in str(ex.value)

    def test_singly_below_yield_unchanged(self):
        r = compression_controlled_capacity_singly(
            0.6, 0.01, 60.0, 4.0, 12.0, 20.0, 24.0, 0.65, 0.85)
        assert r["limit_governs"] is False and "note" not in r
        assert r["ku"] == pytest.approx(0.8157860, abs=1e-7)
        assert r["fs"] == pytest.approx(87.0 * (0.85 - r["ku"]) / r["ku"])
        assert r["phi_pn"] == pytest.approx(427.00082, abs=1e-5)

    def test_singly_steel_yielded_in_compression(self):
        # One layer at mid-depth (d = h/2 = 12 in), fy 40 ksi, the load
        # almost on it (e'/d 0.05): B-19 is below -fy, the bound the page
        # prints (printed p. 44); ku from Eqs B-2 and B-5 with fs = -fy.
        e, rho = 0.05, 0.01
        r = compression_controlled_capacity_singly(
            e, rho, 40.0, 4.0, 12.0, 12.0, 24.0, 0.65, 0.85)
        assert r["limit_governs"] is True and r["fs"] == -40.0
        assert r["fs_unlimited"] == pytest.approx(-47.93, abs=0.01)
        ku = (1 - e) + ((1 - e) ** 2 - rho * 40.0 * e / (0.425 * 4.0)) ** 0.5
        assert r["ku"] == pytest.approx(ku, abs=1e-9)
        lhs, rhs = _b23_b24(r["ku"], e, 0.0, rho, 0.0, 4.0, -40.0, 0.0)
        assert lhs == pytest.approx(rhs, rel=1e-9)
        assert r["phi_pn"] == pytest.approx(640.1, abs=0.1)
        assert r["phi_pn_cubic"] == pytest.approx(639.7, abs=0.1)
        assert r["ku_cubic"] == pytest.approx(1.8926, abs=1e-4)
        for words in ("the page prints fs (>= -fy) beside Eq B-19",
                      "Eqs B-2 and B-5 (printed p. 42)", "with fs = -fy",
                      "library's reading"):
            assert words in r["note"]


class TestSteelStressHeldAtYield:
    """Ruling 42 on REF-76: Eq B-37 prints fs' (>= -fy) (printed p. 48) and
    Eq B-31 fs' (<= fy) (printed p. 47); ``compression_steel_stress_at_ku``
    holds fs' within -fy..fy, gives the equation's value beside it and says
    so."""

    def test_below_yield_unchanged_and_unflagged(self):
        r = compression_steel_stress_at_ku(0.6, 0.15, 0.85, 60.0,
                                           regime="compression_controlled")
        assert r["fs_prime"] == 60.0 and r["limit_governs"] is True
        r = compression_steel_stress_at_ku(0.4, 0.15, 0.85, 60.0,
                                           regime="compression_controlled")
        assert r["fs_prime"] == pytest.approx(87.0 * (0.4 - 0.1275) / 0.4)
        assert r["limit_governs"] is False and "note" not in r

    def test_tension_controlled_bound_flagged(self):
        r = compression_steel_stress_at_ku(0.6, 0.05, 0.85, 60.0)
        assert r["fs_prime"] == 60.0 and r["limit_governs"] is True
        assert r["fs_prime_unlimited"] > 60.0


class TestCompressionSteelStressInputs:
    """REF-76: fs' is bounded at fy (B-31, printed p. 47) and -fy (B-37,
    printed p. 48); inputs no section has are refused, not bounded."""

    def test_physical_inputs_unchanged(self):
        r = compression_steel_stress_at_ku(0.3, 0.15, 0.85, 60.0)
        assert r["fs_prime"] == pytest.approx(
            (0.3 - 0.85 * 0.15) / (0.85 - 0.3) * 60.0)
        r = compression_steel_stress_at_ku(0.4, 0.15, 0.85, 60.0,
                                           regime="compression_controlled")
        assert r["fs_prime"] == pytest.approx(
            29000.0 * 0.003 * (0.4 - 0.85 * 0.15) / 0.4)

    @pytest.mark.parametrize("kw, words", [
        ({"dprime_over_d": 30.0}, "between 0 and 1"),
        ({"dprime_over_d": 0.0}, "between 0 and 1"),
        ({"fy": -60.0}, "fy must be > 0"),
        ({"ku": 0.0}, "ku must be > 0"),
        ({"beta1": 1.2}, "at most 1"),
        ({"ku": 0.9}, "ku below beta1"),
    ])
    def test_non_physical_refused(self, kw, words):
        args = dict(ku=0.3, dprime_over_d=0.15, beta1=0.85, fy=60.0)
        args.update(kw)
        with pytest.raises(ValueError, match=words):
            compression_steel_stress_at_ku(**args)

    def test_singly_compression_controlled_refuses_bad_bound(self):
        with pytest.raises(ValueError, match="fy must be > 0"):
            compression_controlled_capacity_singly(
                e_prime_over_d=0.5, rho=0.01, fy=-60.0, fc_prime=4.0, b=12.0,
                d=20.0, h=24.0, phi=0.65, beta1=0.85)


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
        # Appendix C-3 (EM_1110-2-2104_2025.pdf pdf 62 / printed 56):
        # fs' = 87 - 443.7/a = 35.5 ksi at a = 8.62; the print's "es' =
        # 0.0148 > 0.0021" is worked from d - c, the tension-steel strain.
        assert r["fs_prime"] == pytest.approx(87.0 - 443.7 / 8.62, abs=0.1)
        assert 0.003 * (60.0 - r["c"]) / r["c"] == pytest.approx(0.0148, abs=0.0001)


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
