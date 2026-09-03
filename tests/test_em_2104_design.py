"""Tests for geotech_references.em_2104.design (Appendix D-2 design
equations).

Worked-example validation: Appendix D-3 (singly reinforced retaining-wall
stem design, As = 0.43 sq in) and Appendix D-5 Step 3 (coastal-floodwall
stem, As = 2.73 sq in/ft).
"""

import pytest

from geotech_references.em_2104.design import (
    kd_table_d1,
    minimum_effective_depth,
    max_moment_at_rho_limit,
    design_singly_reinforced,
    design_doubly_reinforced,
)
from geotech_references.em_2104.flexure_axial import aci_beta1, balanced_strain_kb


class TestKdTableD1:
    def test_matches_table_d1_row(self):
        # Table D-1: fc'=4000 psi (4 ksi), fy=60000 psi (60 ksi),
        # rho/rho_b=0.25 -> Kd=0.125765 (printed p. 73).
        beta1 = aci_beta1(4.0)
        r = kd_table_d1(0.25, beta1, fy=60.0)
        assert r["kd"] == pytest.approx(0.125765, abs=1e-5)

    def test_matches_table_d1_row_half(self):
        beta1 = aci_beta1(4.0)
        r = kd_table_d1(0.5, beta1, fy=60.0)
        assert r["kd"] == pytest.approx(0.251531, abs=1e-5)


class TestMinimumEffectiveDepth:
    def test_matches_appendix_d3(self):
        # Appendix D-3 Step 2: Mn=147 k-in, b=12 in -> dd=5.53 in
        # (printed p. 74), using the fc'=4ksi/rho=0.25rho_b row (2.4956
        # coefficient = 1/(0.85*4*0.125765*(1-0.125765/2))).
        beta1 = aci_beta1(4.0)
        kd = kd_table_d1(0.25, beta1, fy=60.0)["kd"]
        r = minimum_effective_depth(mn=147.0, b=12.0, fc_prime=4.0, kd=kd)
        assert r["dd"] == pytest.approx(5.53, abs=0.01)


class TestMaxMomentAtRhoLimit:
    def test_matches_table_d1_own_5ksi_coefficient(self):
        # Table D-1's OWN fc'=5,000 psi / rho=0.25*rho_b row gives
        # dd = sqrt(2.1129*Mn/b) (printed p. 73); with Mn=476 k-ft (5712
        # k-in) and b=12 in this gives dd = sqrt(2.1129*476) = 31.71 in.
        #
        # NOTE: Appendix D-5 Step 3(g) itself prints dd = 34.47 in for this
        # exact problem, but does so using the 2.4956 coefficient -- which
        # is Table D-1's fc'=4,000 psi row, not the fc'=5,000 psi given in
        # D-5's own design data (printed p. 91). This looks like the source
        # document citing the wrong Table D-1 row; per doctrine we do not
        # tune our formula to match a probable errata. It is immaterial to
        # the example's final answer either way (actual d=36.5 in exceeds
        # both 31.71 and 34.47, so the section is adequate regardless).
        beta1 = aci_beta1(5.0)
        kd = kd_table_d1(0.25, beta1, fy=60.0)["kd"]
        r = minimum_effective_depth(mn=476.0 * 12, b=12.0, fc_prime=5.0, kd=kd)
        assert r["dd"] == pytest.approx(31.71, abs=0.02)


class TestDesignSinglyReinforced:
    def test_matches_appendix_d3(self):
        # Appendix D-3 Step 3: Mn=147 k-in, Pn=0, d=6 in, b=12 in, fc'=4 ksi,
        # fy=60 ksi -> Ku=0.105 (printed 0.105, our precise calc gives
        # 0.1057 -- the source's own rounding is one part in a thousand
        # off; see docstring), As=0.43 sq in (printed p. 75).
        r = design_singly_reinforced(mn=147.0, pn=0.0, d=6.0, h=9.0, b=12.0,
                                      fc_prime=4.0, fy=60.0)
        assert r["ku"] == pytest.approx(0.106, abs=0.001)
        assert r["as_required"] == pytest.approx(0.43, abs=0.01)

    def test_matches_appendix_d5_step3(self):
        # Appendix D-5 Step 3(i): Mn=476 k-ft, d=36.5 in, b=12 in, fc'=5 ksi
        # -> Ku=0.088, As=2.73 sq in/ft (printed p. 91).
        r = design_singly_reinforced(mn=476.0 * 12, pn=0.0, d=36.5, h=42.0,
                                      b=12.0, fc_prime=5.0, fy=60.0)
        assert r["ku"] == pytest.approx(0.088, abs=0.001)
        assert r["as_required"] == pytest.approx(2.73, abs=0.02)

    def test_oversized_moment_raises(self):
        with pytest.raises(ValueError):
            design_singly_reinforced(mn=1e6, pn=0.0, d=6.0, h=9.0, b=12.0,
                                      fc_prime=4.0, fy=60.0)


class TestDesignDoublyReinforced:
    def test_requires_mn_above_mdl(self):
        with pytest.raises(ValueError):
            # A tiny Mn is well below MDL -- should raise, directing the
            # caller to design_singly_reinforced instead.
            design_doubly_reinforced(mn=1.0, pn=0.0, d=20.0, dprime=3.0,
                                      h=24.0, b=12.0, fc_prime=4.0, fy=60.0)

    def test_runs_for_large_moment(self):
        # d, d' chosen so the stress-block depth at the target ratio
        # (ad = Kd*d) exceeds beta1*d' -- i.e. the compression steel is
        # actually within the compression stress block (a physically
        # sensible doubly reinforced case).
        r = design_doubly_reinforced(mn=8000.0, pn=0.0, d=30.0, dprime=3.0,
                                      h=34.0, b=12.0, fc_prime=4.0, fy=60.0)
        assert r["as_required"] > 0
        assert r["as_prime_required"] > 0
