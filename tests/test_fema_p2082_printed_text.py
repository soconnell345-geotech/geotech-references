"""FEMA P-2082-1 chapters added from the print (app BACKLOG REF-85).

Chapter 22 of Part 1 and the Part 2 commentary to Chapters 11, 19, 20, 21
and 22, read off the printed pages: bodies in the print's own wording with
[p. N] markers, equations typed from renders. Pages are printed page
numbers; the PDF page is the printed page plus 38.
"""

from geotech_references._retrieval import load_chapter, retrieve_section


def _ids(chapter_json):
    return [s["section_id"] for s in chapter_json["sections"]]


class TestChapter22:
    """Part 1, Chapter 22, printed pp. 96-111."""

    def test_one_section_with_the_seventeen_maps(self):
        ch = load_chapter("fema_p2082", 22)
        assert ch["chapter"] == 22
        assert _ids(ch) == ["22"]
        figs = ch["sections"][0]["figures"]
        assert len(figs) == 17
        assert figs[0].startswith("Figure 22-1: SMS for the Default Site Class")
        assert figs[16].startswith("Figure 22-17: TL for Puerto Rico")

    def test_tl_for_the_islands_without_maps(self):
        # p. 96: "the value of TL shall be 12 s for those islands".
        body = retrieve_section("fema_p2082", "22")["body"]
        assert body.startswith("[p. 96] Revise Chapter 22 as follows")
        assert "Therefore, as in previous editions of these Provisions, the value of TL shall be 12 s for those islands." in body

    def test_tl_maps_unchanged_from_asce_7_16(self):
        # p. 111: each TL caption is followed by this sentence, no map.
        body = retrieve_section("fema_p2082", "22")["body"]
        assert "[p. 111] Figure 22-14 TL for the Conterminous United States\nThis map has not changed with respect to ASCE/SEI 7-16" in body
        assert body.count("This map has not changed with respect to ASCE/SEI 7-16") == 4
