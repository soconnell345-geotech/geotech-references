"""EM 1110-2-2104 (1 November 2023) stored chapter text against the print.

Each test pins a printed equation, table value or statement the stored text once
paraphrased, mislabelled or left out (review of 2026-11-10; app backlog REF-83).
Pages are the printed page numbers; the PDF page is the printed page plus 6.
"""

import json
import re

from geotech_references._retrieval import load_chapter


def _section(chapter, section_id):
    for s in load_chapter("em_2104", chapter)["sections"]:
        if s["section_id"] == section_id:
            return s
    raise KeyError(section_id)


def _formulas(chapter, section_id):
    return {e["id"]: e.get("formula") for e in _section(chapter, section_id)["equations"]}


def test_bodies_are_the_print_with_page_markers():
    assert _section(1, "1-1")["body"] == (
        "[p. 1] This engineer manual provides guidance for designing reinforced concrete hydraulic structures "
        "by the strength design method. Plain concrete and prestressed concrete are not covered in this manual.")
    for ch in range(1, 6):
        for s in load_chapter("em_2104", ch)["sections"]:
            assert s["body"].startswith("[p. "), s["section_id"]


def test_load_definitions_split_out_of_3_2():
    # 3-2 printed is over 14,000 characters: paragraph 3-2f (pp. 16-21) is stored as 3-2.f.
    ids = [s["section_id"] for s in load_chapter("em_2104", 3)["sections"]]
    assert ids.index("3-2.f") == ids.index("3-2") + 1
    s = _section(3, "3-2.f")
    assert s["body"].startswith("[p. 16] f. Load definitions.")
    assert "Dynamic Loads, Ld: Hydrodynamic (except earthquake) Hd; Wave Hw;" in s["body"]
    assert "f. Load definitions" not in _section(3, "3-2")["body"]


def test_lrfd_combination_symbols_from_the_page():
    # p. 22, rendered: the principal load factor is gamma_pr (the stored text said gamma_pu).
    f = _formulas(3, "3-3")
    assert f["3-1"] == "Σγi Lni ≤ φRn"
    assert f["3-2"] == "U = Σγp Lp + γpr Lpr + Σ γc Ltc + γc Ldc"
    assert f["3-3"] == "U = Σ γp Lp + 1.5 EQ + γc Ltc"
    assert f["3-4"] == "U = Σ γp Lp + 1.25 EQ + γc Ltc"
    assert f["3-5"] == "U = 1.0 Σ Lp + 1.0 EQ + 1.0 Ltc"
    assert "γpu" not in json.dumps(_section(3, "3-3"), ensure_ascii=False)


def test_table_3_2_rows():
    # pp. 24-25, rendered.
    b = _section(3, "3-3")["body"]
    assert "Dead D: 1.2 (note 1), 0.9 (note 2), 1.4 (note 1); –; –; –." in b
    assert "Hydrostatic Hs: 1.0; 1.5 (note 3); 1.4 (note 3); 1.3 (note 6)." in b
    assert "Barge/Vessel Impact BI: 1.0; 2.2 (note 9); 1.6 (note 9); 1.3 (note 9)." in b
    assert "Earthquake EQ: N/A; –; 1.5; 1.0 or 1.25 (note 5)." in b


def test_permanent_load_factors():
    # p. 22, rendered.
    b = _section(3, "3-3")["body"]
    assert "EH, at-rest pressure, driving γp = 1.35, resisting γp = 0.9; EH, active pressure, γp = 1.5, passive pressure: γp = 0.5; G, γp = 1.6 or 0." in b


def test_service_stresses_and_single_load_factors():
    # p. 26, rendered Tables 3-3 and 3-4.
    b = _section(3, "3-4")["body"]
    assert "Usual: 25 (170); 20 (140). Unusual: 35 (240); 27.5 (190)." in b
    assert "Usual: 2.2; 2.8. Unusual: 1.6; 2.0." in b


def test_table_3_1_slip_noted():
    # p. 13 says the extreme-load factors are "in Table 3-1"; they are in Table 3-2.
    assert "(Print note: the load factors are in Table 3-2; Table 3-1 lists the loads, p. 13.)" in _section(3, "3-1")["body"]


def test_detailing_tables():
    # pp. 5-7, rendered Tables 2-1 to 2-3.
    assert "greater than 12 in. (30 cm) and less than 24 in. (61 cm) thick: 3 in. (7.5 cm)" in _section(2, "2-7")["body"]
    assert "> No. 11: No less than 5 ft (1.5 m)*." in _section(2, "2-8")["body"]
    assert "30-40 ft (9-12 m): 0.004. Greater than 40 ft (12 m): 0.005." in _section(2, "2-9")["body"]


def test_no4_bars_are_generally_not_a_rule():
    # pp. 6-7: "Generally, for ease of placement, ... no less than No. 4 bars at 12 in."
    s = _section(2, "2-9")
    assert "Generally, for ease of [p. 7] placement, temperature and shrinkage reinforcement will be no less than No. 4 bars" in s["body"]
    assert any(k.startswith("Generally, for ease of placement") for k in s["key_points"])


def test_reinforcement_grade_paragraph_as_printed():
    # p. 4 cites paragraph 3-4 (the stored text said 3-5).
    s = _section(2, "2-2")
    assert "comply with the requirements of ACI 318-19 and paragraph 3-4 may be used as needed" in s["body"]
    assert "3-5" not in s["summary"]


def test_flexure_axial_equations():
    # pp. 29-33, rendered.
    assert _formulas(4, "4-1") == {"4-1": "e′ = Mu/Pu + d − h/2", "4-2": "e′/d", "4-3": "kb = β1 Es εc/(Es εc + fy)"}
    f = _formulas(4, "4-3")
    assert f["4-4"] == "[Mnx/M0x]^K + [Mny/M0y]^K = 1.0"
    assert f["4-5"] == "[Mux/(φM0x)]^K + [Muy/(φM0y)]^K ≤ 1.0"
    assert "M0x = capacity at Pn when Muy is zero; M0y = capacity at Pn when Mux is zero" in _section(4, "4-3")["body"]


def test_shear_equations():
    # pp. 35-38, rendered.
    assert _formulas(5, "5-2")["5-1"].startswith("Vc = [2√(f′c) + Nu/(6 Ag)] bd lbs")
    f = _formulas(5, "5-4")
    assert f["5-2"] == "Vc = [(11.5 − ℓn/d) √(f′c) √(1 + (Nu/Ag)/(5√(f′c)))] bd lbs"
    assert f["5-3"].startswith("Vc = 2[12 − (ℓn/d)] √(f′c) bd lbs")
    assert _formulas(5, "5-5")["5-4"].startswith("Vc = [4√(f′c) √(1 + (Nu/Ag)/(4√(f′c)))] bd lbs")
    assert "Appendix A" not in _section(5, "5-6")["body"]


def test_no_module_notes_or_extraction_debris():
    for ch in range(1, 6):
        text = json.dumps(load_chapter("em_2104", ch), ensure_ascii=False)
        assert ".py" not in text and "implemented in" not in text, ch
        assert not re.search(r"see [a-z_]+\.[a-z_]+", text), ch
        assert not re.search("[\U0001D400-\U0001D7FF]|[ቀቁቂቃ൤൦ඥඩ]", text), ch
