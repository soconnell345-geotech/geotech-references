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

    def test_no_module_notes(self):
        for ch in (1,):
            text = json.dumps(load_chapter("ufc_structural", ch), ensure_ascii=False)
            assert ".py" not in text, ch
            assert not re.search(r"see [a-z_]+\.[a-z_]+", text), ch
