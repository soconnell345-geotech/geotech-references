"""UFC 4-023-03 (14 July 2009, Change 4, 10 June 2024) stored chapter text against the print.

Each test pins a printed equation, table value or statement the stored text once got
wrong, paraphrased away or left out (review of 2026-11-10; app backlog REF-83).
Pages are the printed page numbers; the PDF page is the printed page plus 16.
"""

import json

from geotech_references._retrieval import load_chapter


def _section(chapter, section_id):
    for s in load_chapter("ufc_collapse", chapter)["sections"]:
        if s["section_id"] == section_id:
            return s
    raise KeyError(section_id)


def _all_text(section):
    return json.dumps(section, ensure_ascii=False)


class TestChapter1:
    def test_1_2_1_summary_is_the_printed_rule(self):
        # p. 1: "Special attention shall be given to potential deleterious effects
        # associated with the attachment of the short building section".
        s = _section(1, "1-2.1")
        assert "Special attention shall be given to potential deleterious effects" in s["body"]
        assert "special attention shall be given" in s["summary"]
        assert "trigger peripheral-tie" not in _all_text(s)

    def test_1_2_existing_buildings_as_printed(self):
        # p. 1: "For existing buildings, these requirements may be applied as
        # required by the project proponents or AHJ."
        s = _section(1, "1-2")
        assert "may be applied as required by the project proponents or AHJ" in s["body"]
        assert "Change 4 removed" not in _all_text(s)

    def test_1_6_points_to_appendix_h_without_module_notes(self):
        s = _section(1, "1-6")
        assert "Appendix H" in s["body"]
        assert ".py" not in _all_text(s)


class TestChapter2:
    def test_table_2_1_rows_typed_in(self):
        # p. 7 Table 2-1: RC II includes inhabited buildings with less than 50
        # personnel; RC IV includes UFC 3-301-01 RC IV and RC V.
        s = _section(2, "2-1")
        assert "inhabited buildings with less than 50 personnel" in s["body"]
        assert "Risk Category IV: buildings in Risk Category IV and Risk Category V" in s["body"]

    def test_2_2_4_3_multiplies_the_flexural_demand(self):
        # p. 11: "The flexural demand of the columns and walls for a design with
        # only gravity loads meeting the AP requirements shall be increased
        # respectively by a factor of 2 and a factor of 1.5".
        s = _section(2, "2-2.4.3")
        assert "shall be increased respectively by a factor of 2 and a factor of 1.5" in s["body"]
        assert "flexural demand of the columns and walls for a design with only gravity loads" in s["summary"]
        assert "gravity-only-design flexural strength" not in _all_text(s)
        assert "two elements failing" not in _all_text(s)


class TestChapter3Equations:
    def test_tie_force_equations(self):
        # p. 15, 24: Eq. 3-2, 3-6, 3-7 as printed (checked on the rendered page).
        assert "wF = 1.2D + 0.5L Equation (3-2)" in _section(3, "3-1.3.1")["body"]
        b = _section(3, "3-1.4.2")["body"]
        assert "Fp = 6 wF L1 Lp + 3 WC Equation (3-6)" in b
        assert "Fp = 6 wF L1 Lp + 3 WC + 3 WW Equation (3-7)" in b

    def test_alternate_path_equations(self):
        # p. 42, 44, 49: Eq. 3-9, 3-10, 3-13.
        assert "DCR = QUDLim/QCE Equation (3-9)" in _section(3, "3-2.11.1.2")["body"]
        assert "GLD = ΩLD [1.2 D + (0.5 L or 0.2 S)] Equation (3-10)" in _section(3, "3-2.11.4.1")["body"]
        assert "Φ m QCE ≥ QUD Equation (3-13)" in _section(3, "3-2.11.7")["body"]

    def test_table_3_4_load_increase_factors(self):
        # p. 46 Table 3-4: steel 0.9 mLIF + 1.1, RC framed 1.2 mLIF + 0.80,
        # walls 2.0 mLIF, OmegaLF 2.0; footnote A on RC joints.
        s = _section(3, "3-2.11.5")
        assert "ΩLD = 0.9 mLIF + 1.1, ΩLF = 2.0" in s["body"]
        assert "ΩLD = 1.2 mLIF + 0.80, ΩLF = 2.0" in s["body"]
        assert "beam-column joints are treated as force-controlled" in s["body"]
        assert "Appendix E" not in _all_text(s)

    def test_table_3_5_dynamic_increase_factors(self):
        # p. 52 Table 3-5.
        s = _section(3, "3-2.12.5")
        assert "1.08 + 0.76/(θpra/θy + 0.83)" in s["body"]
        assert "1.04 + 0.45/(θpra/θy + 0.48)" in s["body"]
        assert "SAP2000" not in _all_text(s)


class TestChapter3Statements:
    def test_3_1_frp_and_anchorage(self):
        # p. 13: FRP not acceptable unless the 0.20-rad rotation is proven.
        s = _section(3, "3-1")
        assert "fiber reinforced polymer (FRP) to provide the tie forces is not acceptable" in s["body"]
        assert "tie_forces.py" not in _all_text(s)

    def test_3_1_6_seismic_hooks_paragraph_kept(self):
        # p. 27, printed beside Figure 3-6.
        s = _section(3, "3-1.6")
        assert "engage the furthest peripheral tie rebar" in s["body"]
        assert "noncontact splices are not allowed" in s["body"]

    def test_3_2_5_classification_rules(self):
        # p. 31: "classification as a force or deformation controlled action is
        # not up to the discretion of the user".
        s = _section(3, "3-2.5")
        assert "not up to the discretion of the user" in s["body"]
        assert "OPERATIVE" not in _all_text(s)

    def test_3_2_11_1_print_slip_noted(self):
        # p. 41: DCRs "determined in the Section 3-2.11.1.1"; they are defined in 3-2.11.1.2.
        s = _section(3, "3-2.11.1")
        assert "determined in the Section 3-2.11.1.1" in s["body"]
        assert "Print note" in s["body"]


class TestChapters4To8:
    def test_4_4_3_captions_kept_as_printed_with_note(self):
        # p. 62, 65, 66: the text replaces Tables 10-14 and 10-15; the captions
        # say "Replacement for Table 6-14 / 6-15 in ASCE 41".
        s = _section(4, "4-4.3")
        assert "Replace Table 10-14 of ASCE 41 with Table 4-3" in s["body"]
        assert any("Replacement for Table 6-14 in ASCE 41" in t for t in s["tables"])
        assert "Print note" in s["body"]
        assert "Table 3-4 Footnote A" not in _all_text(s)

    def test_5_1_printed_table_number_with_note(self):
        # p. 67 prints ASCE 41 Table 5-3; p. 14 and 30 give Table 9-3 for steel.
        s = _section(5, "5-1")
        assert "Table 5-3 Factors to Translate Lower-Bound Steel Properties" in s["body"]
        assert "Print note" in s["body"]

    def test_7_3_time_effect_factor_and_commentary(self):
        # p. 73: lambda = 1.0; p. 117 Appendix C-10.1.
        s = _section(7, "7-3")
        assert "The time effect factor λ for wood is 1.0." in s["body"]
        assert "a time effect factor of 1.0, consistent with the time effect factors used for gravity-lateral load combinations, is specified." in s["body"]

    def test_no_module_or_worked_example_notes(self):
        for ch in range(1, 9):
            text = json.dumps(load_chapter("ufc_collapse", ch), ensure_ascii=False)
            for phrase in (".py", "Validated in", "validated by", "Reproduced", "No worked example"):
                assert phrase not in text, (ch, phrase)
