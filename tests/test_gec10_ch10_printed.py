"""GEC-10 (FHWA-NHI-18-024, 2018) chapter 10 text pinned to the printed pages.

REF-40: the chapter text used to be a summary of the 2010 edition (no
Eq. 10-21, resistance factors 0.45/0.65, no delta = phi'). These tests pin the
equations, factors and tables as printed in the 2018 edition (page numbers in
the section bodies are the printed ones, 10-9 to 10-40).
"""

import math

import pytest

from geotech_references._retrieval import load_chapter, retrieve_section
from geotech_references.gec_10.figures import (
    equation_10_21_rock_socket_side,
    equation_10_22_caving_rock_side,
)
from geotech_references.gec_10.tables import (
    table_10_2_nc_base_clay,
    table_8_4_resistance_factor,
)


def _section(sid):
    return retrieve_section("gec_10", sid)


def _text(sid):
    s = _section(sid)
    return " ".join([s["body"]] + s["key_points"] + s["equations"])


class TestChapter10Structure:
    def test_edition_in_title(self):
        assert "(2018)" in load_chapter("gec_10", 10)["reference_title"]

    def test_section_keys_follow_the_print(self):
        ids = [s["section_id"] for s in load_chapter("gec_10", 10)["sections"]]
        for sid in ("10.3.5", "10.3.5.1", "10.3.5.2", "10.3.5.3", "10.3.6", "10.4"):
            assert sid in ids
        assert _section("10.3.5.1")["title"] == "Cohesionless Soils"
        assert _section("10.3.5.2")["title"] == "Cohesive Soils"
        assert _section("10.3.5.3")["title"] == "Rock"

    @pytest.mark.parametrize("n", list(range(1, 30)))
    def test_every_equation_10_1_to_10_29_present_or_numbered(self, n):
        text = " ".join(
            _text(s) for s in
            ("10.3", "10.3.5", "10.3.5.1", "10.3.5.2", "10.3.5.3"))
        assert f"Eq. 10-{n}" in text or f"Eqs. 10-{n}" in text or f"10-{n}" in text


class TestCohesionlessPrinted:
    def test_eq_10_5_to_10_13(self):
        t = _text("10.3.5.1")
        assert "Eq. 10-5" in t and "sigma'_v K tan delta" in t
        assert "beta = K tan delta" in t and "f_SN = sigma'_v beta" in t
        assert "(1 - sin phi') OCR^(sin phi') <= K_p" in t
        assert "tan^2(45 deg + phi'/2)" in t
        assert "0.47 (N60)^m" in t and "0.15 N60" in t
        assert "m = 0.6" in t and "m = 0.8" in t
        assert "K_p tan phi'" in t
        assert "7.5 ft" in t and "900 psf" in t

    def test_delta_equals_phi_prime_in_example_10_1(self):
        t = _text("10.3.5.1")
        assert "phi' = delta = 27.5 + 9.2 log[(N1)60]" in t
        assert "delta = phi'" in t

    def test_side_factor_055_and_base_correlation(self):
        t = _text("10.3.5.1")
        assert "phi_S = 0.55" in t
        assert "q_BN (tsf) = 0.60 N60 <= 30 tsf" in t
        assert "phi = 0.50" in t and "FS = 2.75" in t

    def test_stale_2010_factors_gone(self):
        for sid in ("10.3.5", "10.3.5.1", "10.3.5.2", "10.3.5.3", "10.3.6", "10.4"):
            t = _text(sid)
            assert "0.65 (with load test)" not in t
            assert "0.45 (without)" not in t
            assert "Rollins" not in t
            assert "q_b = 3q_u" not in t and "qb = 3qu" not in t


class TestCohesivePrinted:
    def test_alpha_and_conversions(self):
        t = _text("10.3.5.2")
        assert "0.30 + 0.17 / (s_u(CIUC)/p_a)" in t
        assert "0.893 + 0.513" in t and "0.911 + 0.499" in t
        assert "top 5 ft" in t

    def test_base_resistance(self):
        t = _text("10.3.5.2")
        assert "q_BN = N*_c s_u" in t
        assert "(2/3) [1 + D/(6B)]" in t
        assert "phi = 0.40" in t
        assert "OCR > 8" in t

    def test_table_10_2_text_matches_python(self):
        t = _text("10.3.5.2")
        assert "500 psf: 6.5" in t and "1,000 psf: 8.0" in t
        assert table_10_2_nc_base_clay(500)["nc_star"] == 6.5
        assert table_10_2_nc_base_clay(1000)["nc_star"] == 8.0
        assert table_10_2_nc_base_clay(2000)["nc_star"] == 9.0


class TestRockPrinted:
    def test_eq_10_21_and_10_22_with_coefficients(self):
        t = _text("10.3.5.3")
        assert "f_SN / p_a = C sqrt(q_u / p_a)" in t
        assert "f_SN / p_a = 0.65 alpha_E sqrt(q_u / p_a)" in t
        assert "C = 1.0" in t and "C = 1.9" in t
        assert "roughened" in t

    def test_resistance_factors_as_printed_on_each_page(self):
        t = _text("10.3.5.3")
        # p. 10-21 text: 0.55 (FS = 2.5, "as presented in Table 8-4")
        assert "phi = 0.55" in t and "FS = 2.5" in t
        # Table 8-4 (p. 8-14) prints 0.50; both are kept, not reconciled (OWN-81)
        assert "prints 0.50" in t
        # Eq. 10-23 and Eq. 10-29 base resistance: 0.50; structural bearing 0.70
        assert "phi = 0.50" in t and "phi = 0.70" in t

    def test_eq_10_23_to_10_29(self):
        t = _text("10.3.5.3")
        assert "q_BN = N*_cr q_u" in t and "N*_cr = 2.5" in t
        assert "exp[(GSI - 100)/28]" in t and "exp[(GSI - 100)/9]" in t
        assert "1/2 + (1/6)[exp(-GSI/15) - exp(-20/3)]" in t
        assert "q_BN = A + q_u [m_b (A/q_u) + s]^a" in t

    def test_table_10_3_text(self):
        t = _text("10.3.5.3")
        assert ("RQD 100 percent: 1.00 (closed joints), 0.85 (open or "
                "gouge-filled joints); RQD 70: 0.85, 0.55; RQD 50: 0.60, "
                "0.55; RQD 30: 0.50, 0.50; RQD 20: 0.45, 0.45") in t

    @pytest.mark.parametrize("rqd, closed, open_", [
        (100, 1.00, 0.85), (70, 0.85, 0.55), (50, 0.60, 0.55),
        (30, 0.50, 0.50), (20, 0.45, 0.45)])
    def test_table_10_3_python_rows(self, rqd, closed, open_):
        assert equation_10_22_caving_rock_side(
            5000.0, rqd, "closed")["alpha_E"] == closed
        assert equation_10_22_caving_rock_side(
            5000.0, rqd, "open")["alpha_E"] == open_

    def test_example_10_4_side_resistance(self):
        # The print gives f_SN = 2.116 x 1.0 x sqrt(300/2.116) = 27.6 ksf, and
        # R_SN = 5,202 kips from that. The expression itself evaluates to
        # 25.2 ksf; the library function evaluates the expression.
        t = _text("10.3.5.3")
        assert "= 27.6 ksf as printed" in t and "evaluates to 25.2 ksf" in t
        assert "5,202 kips" in t
        ksf = 47.8803
        r = equation_10_21_rock_socket_side(300 * ksf)
        assert r["f_sn_kpa"] / ksf == pytest.approx(
            2.116 * math.sqrt(300 / 2.116), rel=0.005)
        assert r["f_sn_kpa"] / ksf == pytest.approx(25.2, abs=0.05)

    def test_python_table_8_4_rock_side_is_050(self):
        assert table_8_4_resistance_factor(
            "side_rock_compression")["phi"] == 0.50


class TestStrengthStepAndUplift:
    def test_example_10_5_factors(self):
        t = _text("10.3.6")
        assert "cohesionless soil 0.55" in t and "cohesive soil 0.45" in t
        assert "0.40" in t and "855.4 kips" in t and "0.70" in t

    def test_uplift_factors(self):
        t = _text("10.4")
        assert "less by 0.10" in t and "phi = 0.60" in t and "0.80" in t
        assert "base resistance" in t.lower()
