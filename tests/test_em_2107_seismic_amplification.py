"""Tests for geotech_references.em_2107.seismic_amplification (paragraph
4.4 + Appendix D).

Worked-example validation (doctrine: reproduce published numbers, never
tune) against the Appendix D example (printed pp. 399-402): a gated
spillway on a concrete gravity dam, Hs=350 ft, z=311.5 ft, Gamma~=2.8:
  - Variant 1 (peak spectral acceleration): SA=0.684g, PGA=0.325g -> ac=1.6g,
    amplification 4.9.
  - Variant 2 (period-based): Es=4e6 psi -> beta=2.0, T=0.35 sec, SA=0.55g
    -> ac=1.3g, amplification 4.0.
"""

import math

import pytest

from geotech_references.em_2107.seismic_amplification import (
    westergaard_pressure,
    mode_shape_phi,
    table_4_2_scale_factor,
    hss_support_acceleration,
    hss_support_acceleration_with_c_factor,
    amplification_factor,
    dam_period_estimate,
    table_d1_measured_amplification,
)


class TestWestergaardPressure:
    def test_matches_eq_4_3_form(self):
        gamma_w, ac, h, y = 62.4, 0.2, 100.0, 50.0
        r = westergaard_pressure(gamma_w, ac, h, y)
        assert r["p"] == pytest.approx(gamma_w * ac * math.sqrt(h * y))


class TestModeShapePhi_AppendixDExample:
    def test_matches_worked_example(self):
        # Step 2 (printed p. 400): Hs=350, z=311.5 -> z/Hs=0.89, phi=0.8.
        r = mode_shape_phi(z=311.5, hs=350.0)
        assert r["phi"] == pytest.approx(0.8, abs=0.01)


class TestTable42ScaleFactor:
    def test_tall_dam(self):
        assert table_4_2_scale_factor("gt_1h_1.5w")["gamma_tilde"] == 2.8

    def test_intermediate(self):
        assert table_4_2_scale_factor("1h_1.5w_to_1h_3w")["gamma_tilde"] == 1.5

    def test_wide_dam_uses_pga(self):
        assert table_4_2_scale_factor("lt_1h_3w")["gamma_tilde"] == "pga"

    def test_invalid_category(self):
        with pytest.raises(ValueError):
            table_4_2_scale_factor("bogus")


class TestHssSupportAcceleration_AppendixDWorkedExample:
    """Appendix D Steps 1-5 (printed pp. 399-401), variant 1: peak spectral
    acceleration."""

    def test_variant_1_peak_sa(self):
        r = hss_support_acceleration(sa=0.684, gamma_tilde=2.8, pga=0.325, z=311.5, hs=350.0)
        assert r["ac"] == pytest.approx(1.6, abs=0.02)

    def test_variant_1_amplification(self):
        r = amplification_factor(sa=0.684, gamma_tilde=2.8, pga=0.325, z=311.5, hs=350.0)
        assert r["a_z"] == pytest.approx(4.9, abs=0.1)

    def test_variant_2_period_based(self):
        # Step 4-5 (printed pp. 401-402): T=0.35 sec, SA=0.55g -> ac=1.3g.
        r = hss_support_acceleration(sa=0.55, gamma_tilde=2.8, pga=0.325, z=311.5, hs=350.0)
        assert r["ac"] == pytest.approx(1.3, abs=0.02)

    def test_variant_2_amplification(self):
        r = amplification_factor(sa=0.55, gamma_tilde=2.8, pga=0.325, z=311.5, hs=350.0)
        assert r["a_z"] == pytest.approx(4.0, abs=0.1)

    def test_c_factor_form_disagrees_with_worked_example(self):
        # Documents the source-document discrepancy: applying the printed
        # Eq 4.4 "C=0.75" factor gives a DIFFERENT (wrong, per the worked
        # example) result than the validated no-C Eq 4.6/D.8 form.
        no_c = hss_support_acceleration(sa=0.684, gamma_tilde=2.8, pga=0.325, z=311.5, hs=350.0)["ac"]
        with_c = hss_support_acceleration_with_c_factor(
            sa=0.684, gamma_tilde=2.8, pga=0.325, z=311.5, hs=350.0
        )["ac"]
        assert with_c == pytest.approx(0.75 * no_c)
        assert with_c != pytest.approx(no_c)
        # The worked example's printed answer (1.6g) matches the no-C form.
        assert no_c == pytest.approx(1.6, abs=0.02)


class TestDamPeriodEstimate_AppendixDWorkedExample:
    def test_matches_worked_example(self):
        # Printed p. 402: Hs=350 ft, Es=4e6 psi -> beta=2.0, T=0.35 sec.
        r = dam_period_estimate(hs=350.0, es=4e6)
        assert r["beta"] == pytest.approx(2.0, abs=0.01)
        assert r["t_sec"] == pytest.approx(0.35, abs=0.005)


class TestTableD1MeasuredAmplification:
    def test_full_table(self):
        r = table_d1_measured_amplification()
        assert len(r["dams"]) == 9

    def test_single_dam(self):
        r = table_d1_measured_amplification("Dworshak")
        assert r["amplification_factor"] == 9.06
        assert r["height_ft"] == 717

    def test_unknown_dam(self):
        with pytest.raises(ValueError):
            table_d1_measured_amplification("Not A Dam")
