"""UFC 3-301-01 (11 April 2023, Change 4, 3 June 2025) stored chapter text against the print.

Each test pins a printed equation, table value or statement the stored text once got
wrong, paraphrased away or left out (review of 2026-11-10; app backlog REF-83).
Pages are the printed page numbers; the PDF page is the printed page plus 22.
"""

import json
import re

from geotech_references._retrieval import load_chapter


def _section(chapter, section_id):
    for s in load_chapter("ufc_structural", chapter)["sections"]:
        if s["section_id"] == section_id:
            return s
    raise KeyError(section_id)


def _all_text(section):
    return json.dumps(section, ensure_ascii=False)


class TestChapter1:
    def test_section_count_and_bodies_in_print_words(self):
        secs = load_chapter("ufc_structural", 1)["sections"]
        assert len(secs) == 13
        # p. 1: the legend of the four modification actions, as printed.
        b = _section(1, "1-1")["body"]
        assert b.startswith("[p. 1] UFC 1-200-01 implements and supplements 2024 IBC")
        assert "[Replacement] – Delete referenced 2024 IBC or ASCE 7-22 section or noted portion and replace it with the narrative shown." in b

    def test_commentary_is_not_called_non_mandatory(self):
        # p. 4 says only that [C] designations mark the shaded commentary.
        s = _section(1, "1-7")
        assert "Section designations for such commentary are preceded by a “[C]”" in s["body"]
        assert "non-mandatory" not in _all_text(s)

    def test_appendix_b_only_with_ahj_approval(self):
        # p. 3: "Apply the optional nonlinear procedures outlined in Appendix B only
        # with the approval of the Authority Having Jurisdiction."
        s = _section(1, "1-6")
        assert "only with the approval of the Authority Having Jurisdiction" in s["body"]
        assert "wholly new" not in _all_text(s)

    def test_rc_v_wording(self):
        # p. 5: "national strategic military assets"; designed to remain elastic during the MCER.
        s = _section(1, "1-8.3")
        assert "designed to remain elastic during the MCER" in s["body"]
        assert "defensive" not in s["applicability"]


class TestChapter2:
    def test_sections_and_the_split_of_2_7(self):
        # 2-7 printed is over 14,000 characters: Section 1903 (pp. 29-34) is stored as 2-7.2.
        ids = [s["section_id"] for s in load_chapter("ufc_structural", 2)["sections"]]
        assert len(ids) == 21 and ids.index("2-7.2") == ids.index("2-7") + 1
        s = _section(2, "2-7.2")
        assert "limited to one-story, Risk Category I or II structures in Seismic Design Categories A and B only" in s["body"]
        assert s["figures"] == ["Figure 2-1 (Webbing in Shell Elements)"]
        assert _section(2, "2-4")["figures"] == [] and _section(2, "2-7")["figures"] == []

    def test_table_2_1_deflection_limits(self):
        # p. 10 Table 2-1, read off the rendered page.
        b = _section(2, "2-4.2")["body"]
        assert "Brick veneer: L/600. Exterior Insulation Finish Systems: L/240. Cement board: L/360." in b
        assert "Metal or vinyl siding and insulated metal panel: L/120." in b
        assert "0.42 times the “component and cladding” wind loads" in b

    def test_table_2_2_factors_per_risk_category(self):
        # pp. 11-13 Table 2-2: Ie and ITSU per row, RC V printed "1.0".
        b = _section(2, "2-4.2")["body"]
        assert "Ie = 1.00; ITSU: N/A, Tsunami design not required; SLR scenario: N/A." in b
        assert "Ie = 1.25; ITSU = 1.25; SLR scenario: Medium (2065)." in b
        assert "Ie = 1.50; ITSU = 1.25; SLR scenario: High (2065) (note g)." in b
        assert "Ie = 1.0; ITSU = 1.25; SLR scenario: Highest (2065) (note g)." in b
        assert "Sce-nario" not in b and "• •" not in b

    def test_wind_speed_conversion_equations(self):
        # p. 19: the radical covers 0.6 only (rendered page).
        s = _section(2, "2-4.6")
        assert "Vasd = √(0.6) V (Equation 16-18a)" in s["body"]
        assert "Vfm = (√(0.6) V - 10.5)/1.05 (Equation 16-18b)" in s["body"]
        assert [e["formula"] for e in s["equations"]] == ["Vasd = √(0.6) V", "Vfm = (√(0.6) V - 10.5)/1.05"]

    def test_vlfd_700_year_rule_is_for_maintenance_hangars(self):
        # p. 18: the 700-year-MRI prohibition is "for use in aircraft maintenance hangars".
        s = _section(2, "2-4.6")
        assert "VLFD’s are prohibited for use in aircraft maintenance hangars where 700-year-MRI wind speeds" in s["body"]
        assert any("aircraft maintenance hangars where 700-year-MRI" in k for k in s["key_points"])

    def test_vertical_ground_motion_derivation_as_typeset(self):
        # p. 15 commentary: avg = 0.62x(2/3SDS) = 0.41SDS; 0.65/1.05 = 0.62.
        b = _section(2, "2-4.3")["body"]
        assert "avg = 0.62×(2/3SDS) = 0.41SDS" in b
        assert "0.65/1.05 = 0.62" in b

    def test_delegated_design_examples_are_ten(self):
        # p. 9 lists a. to j.
        s = _section(2, "2-4.1")
        assert "j. Cross-laminated timber connections" in s["body"]
        assert "Nine" not in _all_text(s)

    def test_coupling_beam_shear(self):
        # p. 37, rendered: phi Vn >= 1.25(Mn1 + Mn2)/Lc + 1.4Vg (unnumbered).
        s = _section(2, "2-8")
        assert "ϕVn ≥ 1.25(Mn1 + Mn2)/Lc + 1.4Vg" in s["body"]
        assert s["equations"][0]["formula"] == "ϕVn ≥ 1.25(Mn1 + Mn2)/Lc + 1.4Vg"
        assert "is multiplied by Ωo." in s["body"]

    def test_frost_depth_wording(self):
        # p. 28: frost line depth "must be specified by the project geotechnical engineer".
        s = _section(2, "2-6")
        assert "must be specified by the project geotechnical engineer" in s["body"]
        assert "no frost-depth table" not in _all_text(s) and "no table printed" not in _all_text(s)

    def test_commentary_number_print_note(self):
        # p. 22: provision 1613.1.1.3, its commentary headed 1613.2.1.4.
        b = _section(2, "2-4.7")["body"]
        assert "[C] 1613.2.1.4" in b and "Print note" in b


class TestChapter3:
    def test_vertical_seismic_load_combinations(self):
        # pp. 44-46, rendered: combinations 8, 9 and 11 to 13.
        s = _section(3, "3-2")
        for combo in ("8. 1.2D + 1.0Ev0 + 0.3Eh + L + 0.2S", "9. 0.9D – 1.0Ev0 + 0.3Eh",
                      "11. 1.0D + 0.7Ev0 + 0.21Eh", "12. 1.0D + 0.525Ev0 + 0.1575Eh + 0.75L + 0.75S",
                      "13. 0.6D – 0.7Ev0 + 0.21Eh", "13. 0.6D – 0.7Ev0 + 0.21Emh"):
            assert combo in s["body"], combo
        assert "Ev0 = 0.67SDSD" in s["body"]
        assert "(0.3×0.67SDS = 0.2SDS)" in s["body"]
        assert "0.525Ev0" in s["equations"][1]["formula"]

    def test_collector_item_c_is_not_a_general_rule(self):
        # p. 58: only Item (c) of 12.10.2.1 and its exception are replaced.
        s = _section(3, "3-6")
        assert "Item (c) [Replacement]. Forces calculated using the load combinations of Section 2.3.6 without overstrength factor" in s["body"]
        assert not any(k.startswith("Collector elements at SDC C-F: use load combinations WITHOUT") for k in s["key_points"])

    def test_table_3_1_notes_symbols_from_the_page(self):
        # pp. 56-57 notes b and q: Omega-o and hn, read off the rendered page.
        b = _section(3, "3-6")["body"]
        assert "Where the tabulated value of the overstrength factor, Ωo, is greater than or equal to 2½, Ωo is permitted to be reduced by subtracting the value of ½" in b
        assert "Structural height, hn, shall not be less than 60 ft (18.3 m)" in b
        assert "its rows are not typed into this text" in b

    def test_nonstructural_anchor_factor_is_omega_op(self):
        # p. 61: "multiplied by Omega_op as given in ASCE 7-22 Tables 13.5-1 and 13.6-1";
        # the text layer gives only "Omega o o o o". p. 65 (nonbuilding structures) prints Omega_o.
        assert "QE, is multiplied by Ωop as given in ASCE 7-22 Tables 13.5-1 and 13.6-1" in _section(3, "3-7")["body"]
        assert "QE, is multiplied by Ωo as given in ASCE 7-22 Tables 13.5-1 and 13.6-1" in _section(3, "3-8")["body"]

    def test_crane_ratios(self):
        # p. 64: CAR/Rpo = 1, crane rail connections 1.15; commentary 1.5/1.3 = 1.15.
        b = _section(3, "3-7")["body"]
        assert "Seismic forces, Fp, must be calculated using CAR/Rpo = 1, except that crane rail connections must be designed for the forces resulting from CAR/Rpo = 1.15 in all directions" in b
        assert "raised by a factor of 1.5/1.3 = 1.15" in b

    def test_training_towers_need_ahj_approval(self):
        # p. 47: "are not to be classified as non-building structures unless specifically approved by the AHJ".
        s = _section(3, "3-5")
        assert "unless specifically approved by the AHJ" in s["body"]
        assert "automatically" not in _all_text(s)

    def test_printed_chapter_titles(self):
        # pp. 65, 67 print "ASCE 7 CHAPTER 15" and "ASCE 7 CHAPTER 26".
        assert _section(3, "3-8")["title"].startswith("ASCE 7 Chapter 15")
        assert _section(3, "3-9")["title"].startswith("ASCE 7 Chapter 26")


class TestAllChapters:
    def test_no_module_notes(self):
        for ch in (1, 2, 3):
            text = json.dumps(load_chapter("ufc_structural", ch), ensure_ascii=False)
            assert ".py" not in text, ch
            assert not re.search(r"see [a-z_]+\.[a-z_]+", text), ch
