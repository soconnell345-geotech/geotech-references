"""EN 1997-1:2004 stored chapter text against the print.

Each test pins a printed form or statement the stored text once got wrong
(review of 2026-11-10, REF-83). Pages are the printed page numbers; the PDF
page is the printed page plus 2.
"""

import json
import re

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
        # p. 34: u_dst;d <= sigma_stb;d (2.9a); S_dst;d <= G'_stb;d (2.9b).
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

    def test_heave_equations_page(self):
        # p. 34: 2.4.7.5(1)P and Eqs. 2.9a/2.9b are all on p. 34, not pp. 33-34.
        body = _section(10, "10.3")["body"]
        assert "2.4.7.5(1)P, p. 34" in body
        assert "pp. 33-34" not in body

    def test_slope_ground_structure_interaction_shall(self):
        # p. 120, 11.5.1(11)P: "ground-structure interaction shall be considered by
        # allowing for the difference in their relative stiffnesses". The key point
        # once said such an analysis "may be needed".
        s = _section(11, "11.5.1")
        kps = " ".join(s["key_points"])
        phrase = "ground-structure interaction shall be considered by allowing for the difference in their relative stiffnesses"
        assert phrase in kps
        assert phrase in s["body"]
        assert "may be needed" not in kps

    def test_no_design_approach_said_to_be_usual_for_slopes(self):
        # p. 33: 2.4.7.3.4.3 NOTE 2 and 2.4.7.3.4.4 NOTE 2 say how DA2 and DA3
        # are applied to slopes; neither says which approach is used for them.
        text = _all_text(_section(11, "11.5.1")) + _all_text(_section(13, "13-10")) + _all_text(_section(13, "13-13"))
        for claim in ("normally used for slope", "generally the design approach",
                      "generally used for slope", "usual choice", "typically used for slope"):
            assert claim not in text
        assert "are treated as geotechnical actions by using the set of load factors A2" in _section(13, "13-10")["body"]

    def test_k0_beta_limit_is_phi_prime(self):
        # p. 104, 9.5.2(4): the ground slopes upwards at beta <= phi'.
        d = _equation(_section(9, "9.5.2"), "Eq. 9.2")["description"]
        assert "beta <= phi' to the horizontal" in d

    def test_non_linear_stiffness_force_word(self):
        # p. 67, 6.6.2(16): ratio below 2 -> "the calculations should take account
        # of non-linear stiffness effects in the ground".
        summary = _section(6, "6.6.2")["summary"]
        assert "should take account of non-linear stiffness effects in the ground" in summary
        assert "requires non-linear stiffness" not in summary

    def test_earthquake_vibrations_shall(self):
        # p. 67, 6.6.4(3)P: "Vibrations caused by earthquakes shall be considered
        # using EN 1998."
        s = _section(6, "6.6.4")
        assert "shall be considered using EN 1998" in s["summary"]
        assert "shall be considered using EN 1998" in " ".join(s["key_points"])

    def test_block_uplift_shall(self):
        # p. 83, 7.6.3.1(4)P: block uplift "shall be carried out in accordance with 2.4.7.4".
        d = _equation(_section(7, "7.6.3"), "Eq. 7.12")["description"]
        assert "shall be carried out in accordance with 2.4.7.4" in d


# Tables A.6, A.7 and A.8 (printed p. 132), R1/R2/R3/R4, as the standard prints them.
_PILE_TABLES_PRINTED = {
    "A.6": {"base": (1.0, 1.1, 1.0, 1.3), "shaft_compression": (1.0, 1.1, 1.0, 1.3),
            "total_compression": (1.0, 1.1, 1.0, 1.3), "shaft_tension": (1.25, 1.15, 1.1, 1.6)},
    "A.7": {"base": (1.25, 1.1, 1.0, 1.6), "shaft_compression": (1.0, 1.1, 1.0, 1.3),
            "total_compression": (1.15, 1.1, 1.0, 1.5), "shaft_tension": (1.25, 1.15, 1.1, 1.6)},
    "A.8": {"base": (1.1, 1.1, 1.0, 1.45), "shaft_compression": (1.0, 1.1, 1.0, 1.3),
            "total_compression": (1.1, 1.1, 1.0, 1.4), "shaft_tension": (1.25, 1.15, 1.1, 1.6)},
}
_PILE_TABLE_LABELS = {"A.6": "Driven piles", "A.7": "Bored piles", "A.8": "CFA piles"}
_FOUR = r"(\d+(?:\.\d+)?/\d+(?:\.\d+)?/\d+(?:\.\d+)?/\d+(?:\.\d+)?)"


def _four(s):
    return tuple(float(x) for x in s.split("/"))


class TestAnnexA:
    def test_pile_tables_body_every_cell(self):
        # p. 132: every cell of Tables A.6-A.8 in the 13-6 body. The stored text
        # once gave R4 = 1.3 for the bored-pile base and total and the CFA base.
        body = _section(13, "13-6")["body"]
        for table, label in _PILE_TABLE_LABELS.items():
            m = re.search(
                re.escape(f"{label} (Table {table}): ") + "base = " + _FOUR
                + r"; shaft \(compression\) = " + _FOUR
                + r"; total/combined \(compression\) = " + _FOUR
                + "; shaft in tension = " + _FOUR, body)
            assert m, table
            stored = dict(zip(("base", "shaft_compression", "total_compression", "shaft_tension"),
                              (_four(g) for g in m.groups())))
            assert stored == _PILE_TABLES_PRINTED[table], table

    def test_pile_tables_key_points_every_cell(self):
        kps = _section(13, "13-6")["key_points"]
        driven = next(k for k in kps if k.startswith("Driven piles (Table A.6)"))
        assert "base, shaft (compression) and total/combined (compression) each 1.0/1.1/1.0/1.3" in driven
        assert "shaft in tension 1.25/1.15/1.1/1.6" in driven
        for table in ("A.7", "A.8"):
            label = _PILE_TABLE_LABELS[table]
            kp = next(k for k in kps if k.startswith(f"{label} (Table {table})"))
            m = re.search("base " + _FOUR + r"; shaft \(compression\) " + _FOUR
                          + r"; total/combined \(compression\) " + _FOUR
                          + "; shaft in tension " + _FOUR, kp)
            assert m, table
            stored = dict(zip(("base", "shaft_compression", "total_compression", "shaft_tension"),
                              (_four(g) for g in m.groups())))
            assert stored == _PILE_TABLES_PRINTED[table], table

    def test_r4_column_key_point(self):
        # p. 132: the R4 column is not the same in the three tables.
        kps = " ".join(_section(13, "13-6")["key_points"])
        assert "base 1.3 (driven), 1.6 (bored), 1.45 (CFA)" in kps
        assert "total/combined 1.3 (driven), 1.5 (bored), 1.4 (CFA)" in kps
        assert "R4 column identical to Table A.6" not in kps
        assert "A.6/A.7's 1.3" not in kps

    def test_coded_pile_tables_match_the_print(self):
        from geotech_references.eurocode_7_1 import tables
        funcs = {"A.6": tables.table_a_6_driven_pile_resistance,
                 "A.7": tables.table_a_7_bored_pile_resistance,
                 "A.8": tables.table_a_8_cfa_pile_resistance}
        for table, rows in _PILE_TABLES_PRINTED.items():
            for resistance, values in rows.items():
                coded = tuple(funcs[table](resistance, r) for r in ("R1", "R2", "R3", "R4"))
                assert coded == values, (table, resistance)

    def test_dynamic_test_model_factor_force_words(self):
        # p. 134, Table A.11 footnotes b-d: 0.85 "may", 1.10 "should", 1.20 "shall".
        s = _section(13, "13-7")
        for text in (s["body"], " ".join(s["key_points"])):
            assert "may be multiplied" in text and "0.85" in text
            assert "should be multiplied" in text and "1.10" in text
            assert "shall be multiplied" in text and "1.20" in text
        assert "may be multiplied with a model factor of 0.85" in s["body"]
        assert "should be multiplied with a model factor of 1.10" in s["body"]
        assert "shall be multiplied with a model factor of 1.20" in s["body"]

    def test_design_approach_1_combination_notes(self):
        # p. 32-33, 2.4.7.3.4.2: the NOTEs' own words; M1 is 1.0 throughout (Table A.4, p. 130).
        body = _section(13, "13-13")["body"]
        assert "in Combinations 1 and 2, partial factors are applied to actions and to ground strength parameters" in body
        assert ("in Combination 2, partial factors are applied to actions, to ground resistances "
                "and sometimes to ground strength parameters") in body
        assert "In set M1 every factor is 1.0 (Table A.4, p. 130)" in body
        assert "factor actions and ground strength, not resistance" not in body
        assert "not ground strength" not in body
