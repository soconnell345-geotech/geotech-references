"""FEMA P-2082-1 (2020 NEHRP Provisions) stored chapter text against the print.

Each test pins a printed form the stored text once got wrong (review of
2026-11-10, findings text-08 and REF-83). Pages are printed page numbers;
the PDF page is the printed page plus 38.
"""

import json

import pytest

from geotech_references._retrieval import load_chapter


def _section(chapter, section_id):
    for s in load_chapter("fema_p2082", chapter)["sections"]:
        if s["section_id"] == section_id:
            return s
    raise KeyError(section_id)


def _equation(section, equation_id):
    for e in section["equations"]:
        if e["equation_id"] == equation_id:
            return e
    raise KeyError(equation_id)


def _all_text(section):
    return json.dumps(section, ensure_ascii=False)


# ---------------------------------------------------------------- 19.3.2


class TestEffectiveDampingRatio:
    """Section 19.3.2, Eqs. (19.3-1) to (19.3-4), pp. 79-80."""

    def test_eq_19_3_1_caps_beta0_at_0_20(self):
        # p. 79: beta_0 = beta_f + beta/(T~/T)^2_eff <= 0.20 (19.3-1).
        s = _section(19, "19.3.2")
        e = _equation(s, "19.3-1")
        assert e["latex"].endswith(r"\le 0.20")
        assert r"\tilde{T}" in e["latex"]
        assert "<= 0.20 (Eq. 19.3-1)" in s["body"]
        assert "<= 0.20" in s["summary"]
        assert "<= 0.20" in s["key_points"][0]

    def test_eq_19_3_1_cap_binds(self):
        # Made-up values: beta_f 0.15, beta 0.05, (T~/T)_eff 1.0 give
        # 0.20 before the cap; beta_f 0.18 gives 0.23, which the printed
        # cap brings back to 0.20.
        def beta0(beta_f, beta, ratio_eff):
            return min(beta_f + beta / ratio_eff ** 2, 0.20)

        assert beta0(0.18, 0.05, 1.0) == pytest.approx(0.20)
        assert beta0(0.05, 0.05, 1.2) == pytest.approx(0.05 + 0.05 / 1.44)

    def test_eq_19_3_2_uses_t_tilde_over_t(self):
        # p. 79: (T~/T)_eff = {1 + (1/mu)[(T~/T)^2 - 1]}^0.5 (19.3-2).
        s = _section(19, "19.3.2")
        e = _equation(s, "19.3-2")
        assert e["latex"].count(r"\tilde{T}") == 2
        assert "(T_tilde/T)_eff = {1 + (1/mu)*[(T_tilde/T)^2 - 1]}^0.5" in s["body"]
        # The stored text once read "(T/T)", which is 1 and makes the ratio 1.
        assert "(T/T)" not in _all_text(s)

    def test_eq_19_3_3_factor_multiplies_beta_s(self):
        # p. 80: beta_f = [((T~/T)^2 - 1)/(T~/T)^2] beta_s + beta_rd (19.3-3).
        s = _section(19, "19.3.2")
        e = _equation(s, "19.3-3")
        assert e["latex"] == (
            r"\beta_f = \left[\frac{(\tilde{T}/T)^2 - 1}{(\tilde{T}/T)^2}\right]"
            r"\beta_s + \beta_{rd}")
        form = "beta_f = [((T_tilde/T)^2 - 1)/(T_tilde/T)^2]*beta_s + beta_rd"
        assert form in s["body"]
        assert form in s["summary"]
        # The old stored form put the factor on beta_rd.
        assert "*beta_rd + beta_s" not in _all_text(s)

    def test_eq_19_3_3_worked_value(self):
        # Made-up values: T~/T = 1.5, beta_s = 0.05, beta_rd = 0.04.
        # Printed form: (2.25 - 1)/2.25 * 0.05 + 0.04 = 0.06778.
        # The old stored form gave (1 - 1/2.25)*0.04 + 0.05 = 0.07222.
        r2 = 1.5 ** 2
        printed = (r2 - 1) / r2 * 0.05 + 0.04
        assert printed == pytest.approx(0.067778, rel=1e-4)

    def test_eq_19_3_4_replacement_symbol_as_printed(self):
        # p. 80 prints "the damping values, beta_r, in Eq. (19.3-3) shall be
        # replaced by beta'_s"; the stored text keeps beta_r and notes it.
        s = _section(19, "19.3.2")
        assert "the damping values, beta_r, in Eq. (19.3-3) shall be replaced by beta_s'" in s["body"]
        assert "p. 80 writes beta_r" in s["body"]
        e = _equation(s, "19.3-4")
        assert e["latex"] == r"\beta_s' = \left(\frac{4 D_s}{v_s \tilde{T}}\right)^4 \beta_s"


# ---------------------------------------------------------------- 19.3.3 to 19.3.5


class TestRadiationAndSoilDamping:
    def test_psi_cap_printed_as_inequality(self):
        # pp. 81, 83: psi = sqrt(2(1 - nu)/(1 - 2 nu)) <= 2.5 (19.3-13, 19.3-23).
        for sid, eq in (("19.3.3", "19.3-13"), ("19.3.4", "19.3-23")):
            body = _section(19, sid)["body"]
            assert f"psi = sqrt(2(1-nu)/(1-2nu)) <= 2.5 (Eq. {eq})" in body

    def test_rectangular_where_list_b_symbol_note(self):
        # p. 82 prints "v_so = half the smaller dimension of the base"; stored as
        # printed, the evident symbol B in a note.
        body = _section(19, "19.3.3")["body"]
        assert "v_so = half the smaller dimension of the base of the structure (as printed on p. 82" in body
        assert "the symbol is evidently B" in body
        assert "B = half the smaller dimension of the base of the structure" not in body

    def test_alpha_rr(self):
        # p. 84: alpha_rr = 1.0 - [0.35 a0^2/(1.0 + a0^2)] (19.3-24).
        assert "alpha_rr = 1.0 - [0.35*a_0^2/(1.0 + a_0^2)] (Eq. 19.3-24)" in _section(19, "19.3.4")["body"]

    def test_table_19_3_3_summary_values(self):
        # p. 84, Table 19.3-3: DE = 0.20 at SDS/2.5 >= 0.8; E = 0.20 at 0.4, 'b' at >= 0.8.
        s = _section(19, "19.3.5")
        assert "Site Class DE reaches 0.20 at SDS/2.5 >= 0.8" in s["summary"]
        assert "E: 0.01, 0.05, 0.20, (b)" in s["body"]
        assert "DE: 0.01, 0.03, 0.12, 0.20" in s["body"]

    def test_g0_entry_is_unnumbered(self):
        # p. 82: G0 = gamma v_so^2 / g is a where-list definition, no number.
        s = _section(19, "19.3.3.1")
        ids = [e["equation_id"] for e in s["equations"]]
        assert ids == ["G0 (unnumbered, 19.3.3 where-list)"]


# ---------------------------------------------------------------- chapters 11, 20, 21


class TestOtherChapters:
    def test_importance_factor_values_not_stated(self):
        # p. 18, 11.5.1 names Table 1.5-2 and prints no values.
        s = _section(11, "11.5")
        text = _all_text(s)
        for invented in ("1.25", "Ie=1.5", "Table 1.5-1"):
            assert invented not in text

    def test_site_class_bc_not_called_reference_condition(self):
        # pp. 86-87: 20.1 and 20.2 do not call BC a reference or baseline condition.
        for sid in ("20.1", "20.2"):
            text = _all_text(_section(20, sid)).lower()
            assert "baseline" not in text
            assert "reference (baseline)" not in text

    def test_table_20_2_1_boundaries(self):
        # p. 86, Table 20.2-1.
        kps = _section(20, "20.2")["key_points"]
        assert "C: > 1,450 to 2,100 ft/s - Very dense sand or hard clay" in kps
        assert "E: < 500 ft/s - Very loose sand or soft clay" in kps

    def test_deterministic_lower_limit_filed_under_21_2_2(self):
        # p. 92: the lower limit of Table 21.2-1 and its exception are in 21.2.2.
        body = _section(21, "21.2")["body"]
        assert ("the deterministic response spectral acceleration at each period shall be taken as "
                "not less than the deterministic lower limit response spectrum of Table 21.2-1") in body
        assert "The deterministic ground motion response spectrum need not be calculated" in body

    def test_lower_limit_applies_to_deterministic_values_not_sam(self):
        # p. 92-93: SaM is the lesser of the two; the floor is on the deterministic values.
        kps = " ".join(_section(21, "21.2.3")["key_points"])
        assert "SaM >= the Table 21.2-1" not in kps

    def test_section_21_4_entries_unnumbered(self):
        # p. 93: Section 21.4 is prose; no equation number is printed.
        ids = [e["equation_id"] for e in _section(21, "21.4")["equations"]]
        assert ids == ["SDS (unnumbered, Section 21.4)", "SD1 (unnumbered, Section 21.4)"]
