"""EN 1997-1:2004 stored chapter text against the print.

Each test pins a printed form or statement the stored text once got wrong
(review of 2026-11-10, REF-83). Pages are the printed page numbers; the PDF
page is the printed page plus 2.
"""

import json

from geotech_references._retrieval import load_chapter


def _section(chapter, section_id):
    for s in load_chapter("eurocode_7_1", chapter)["sections"]:
        if s["section_id"] == section_id:
            return s
    raise KeyError(section_id)


def _equation(section, equation_id):
    for e in section["equations"]:
        if e["id"] == equation_id:
            return e
    raise KeyError(equation_id)


def _all_text(section):
    return json.dumps(section, ensure_ascii=False)


class TestPiles:
    def test_eq_7_12_is_the_tension_inequality(self):
        # p. 83: Ft;d <= Rt;d (7.12); block uplift is verified per 2.4.7.4.
        d = _equation(_section(7, "7.6.3"), "Eq. 7.12")["description"]
        assert d.startswith("Ft;d <= Rt;d")
        assert "OCR" not in d

    def test_eq_7_16_is_rt_equals_rs(self):
        # p. 85: Rt;k = Rs;k (7.16), not Rs;d = Rs;k/gamma_s.
        s = _section(7, "7.6.3")
        assert _equation(s, "Eq. 7.16")["description"].startswith("Rt;k = Rs;k")
        assert "Rs;d = Rs;k/gamma_s (Eq. 7.16)" not in _all_text(s)

    def test_eq_7_18_printed_form(self):
        # p. 85: Rt;k = sum_i As;i qs;i;k (7.18).
        assert "Rt;k = SUM_i As;i * qs;i;k" in _equation(_section(7, "7.6.3"), "Eq. 7.18")["description"]

    def test_block_effect_normally_governs(self):
        # p. 83, 7.6.3.1(7): "Normally the block effect will govern ...".
        assert "Normally the block effect will govern" in _section(7, "7.6.3")["summary"]

    def test_eq_7_6_and_7_7_printed_forms(self):
        # p. 80: Rc;d = Rb;d + Rs;d (7.6); Rb;d = Rb;k/gamma_b and Rs;d = Rs;k/gamma_s (7.7).
        s = _section(7, "7.6.2")
        assert _equation(s, "Eq. 7.6")["description"].startswith("Rc;d = Rb;d + Rs;d")
        assert _equation(s, "Eq. 7.7")["description"].startswith("Rb;d = Rb;k/gamma_b and Rs;d = Rs;k/gamma_s")

    def test_r4_conservatism_claim_removed(self):
        # The print says nothing of R4 being "more conservative" (2.4.7.3.4.2, p. 32-33).
        assert "materially more conservative" not in _section(7, "7.6.2")["body"]

    def test_anchorage_eq_8_1_printed_symbol(self):
        # p. 94: Pd <= Ra;d (8.1).
        s = _section(8, "8.5")
        assert _equation(s, "Eq. 8.1")["description"].startswith("Pd <= Ra;d")
        assert "Fa;d" not in _all_text(s)

    def test_tension_tests_force_word(self):
        # p. 75, 7.5.2(4): tension pile load tests "should be carried out to failure".
        kps = " ".join(_section(7, "7.5")["key_points"])
        assert "should be carried out to failure" in kps
        assert "must be carried out to failure" not in kps


class TestAnnexC:
    def test_eq_c3_printed_form(self):
        # p. 151: cos(2mt + phi + beta0) = -sin(beta0)/sin(phi) (C.3).
        d = _equation(_section(15, "15-2"), "Eq. C.3")["description"]
        assert "cos(2mt + phi + beta0) = -sin(beta0)/sin(phi)" in d

    def test_eqs_c5_to_c8_printed_forms(self):
        # p. 152: (C.5) to (C.8).
        s = _section(15, "15-2")
        assert "v = mt + beta - mw - theta" in _equation(s, "Eq. C.5")["description"]
        assert "exp(2v*tan(phi))" in _equation(s, "Eq. C.6")["description"]
        assert "Kq = Kn*cos^2(beta)" in _equation(s, "Eq. C.7")["description"]
        assert "Kc = (Kn - 1)*cot(phi)" in _equation(s, "Eq. C.8")["description"]

    def test_eq_c10_printed_form(self):
        # p. 152: Kgamma (phi = 0) = cos(theta) + sin(beta) cos(mw)/sin(mt) (C.10).
        d = _equation(_section(15, "15-2"), "Eq. C.10")["description"]
        assert "cos(theta) + sin(beta)*cos(mw)/sin(mt)" in d

    def test_no_legibility_claims_left(self):
        # Annex C.2 is legible in the print; the stored text once said C.3-C.8 were not.
        assert "NOT LEGIBLE" not in _all_text(_section(15, "15-2"))
        assert "not captured by the OCR" not in _section(9, "9.5.3")["body"]


class TestAnnexesBDEH:
    def test_eq_b1_printed_form(self):
        # p. 138: gamma_F = gamma_S;d * gamma_f (B.1).
        assert "gamma_F = gamma_S;d * gamma_f" in _equation(_section(14, "14-2"), "Eq. B.1")["description"]

    def test_tank_exception_uses_gamma_e(self):
        # p. 139: tank with fixed fluid level -> gamma_F = 1 and gamma_E != 1.
        body = _section(14, "14-2")["body"]
        assert "then gamma_F = 1 and gamma_E != 1 are used" in body
        assert "gamma_Sd != 1" not in body

    def test_b622_is_gamma_f_equal_one(self):
        # p. 140: "When gamma_F = 1 is also used" (B.6.2.2).
        d = _equation(_section(14, "14-3"), "Eq. B.6.2.2")["description"]
        assert "gamma_F = 1" in d and "Rd = (1/gamma_R)*R{Frep; Xk; ad}" in d

    def test_b611_added(self):
        # p. 140: Rd = R{gamma_F Frep; Xk/gamma_M; ad} (B.6.1.1).
        assert "Rd = R{gamma_F*Frep; Xk/gamma_M; ad}" in _equation(_section(14, "14-3"), "Eq. B.6.1.1")["description"]

    def test_annex_d_undrained_q_and_no_prandtl(self):
        # p. 158: D.1 uses q (overburden or surcharge pressure); Nc = 5.14 / Prandtl not printed.
        s = _section(16, "16-2")
        assert "Prandtl" not in _all_text(s)
        assert "overburden or surcharge pressure" in s["summary"]

    def test_annex_d_m_theta(self):
        # p. 159: m = m_theta = mL cos^2(theta) + mB sin^2(theta).
        assert "mL*cos^2(theta) + mB*sin^2(theta)" in _section(16, "16-3")["body"]

    def test_annex_e_equation_number(self):
        # p. 160: Rd/A' = sigma_v;0 + k p*le (E.1).
        e = _equation(_section(17, "17-1"), "Eq. E.1")
        assert "sigma_v;0 + k*p*le" in e["description"]

    def test_annex_g_no_strength_ranking(self):
        # p. 163: Table G.1 lists groups 1-4 without ranking them.
        assert "strongest" not in _all_text(_section(19, "19-1"))

    def test_annex_h_prints_no_tables(self):
        # p. 165: Annex H gives its limits as text.
        assert "prints no tables" in " ".join(_section(20, "20-2")["key_points"])


class TestGeneralRules:
    def test_heave_equations_printed(self):
        # p. 33-34: u_dst;d <= sigma_stb;d (2.9a); S_dst;d <= G'_stb;d (2.9b).
        s = _section(10, "10.3")
        assert _equation(s, "Eq. 2.9a")["description"].startswith("u_dst;d <= sigma_stb;d")
        assert _equation(s, "Eq. 2.9b")["description"].startswith("S_dst;d <= G'_stb;d")
        assert "pdf_page_index" not in _all_text(s)

    def test_embankment_compaction_force_word(self):
        # p. 123, 12.1(2): "the provisions in Section 5 should be applied".
        assert "should be applied" in _section(12, "12.1")["summary"]

    def test_bearing_layer_order(self):
        # p. 63, 6.5.2.2(5): strong under weak -> weak parameters; reverse -> punching.
        assert "(weak over strong), punching" not in _section(6, "6.5.2.2")["body"]
