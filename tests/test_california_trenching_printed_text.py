"""Caltrans Trenching and Shoring Manual (July 2025) chapters added from the print (app BACKLOG REF-85).

Chapter 1, Chapter 9 and Appendix D, read off the printed pages: bodies in
the print's own wording with [p. 9-4] markers, values typed from renders.
Pages are the printed page numbers.
"""

import json
from pathlib import Path

import geotech_references
from geotech_references._retrieval import load_chapter, retrieve_section

TEXT = Path(geotech_references.__file__).parent / "california_trenching" / "text"


def _file(name):
    return json.loads((TEXT / name).read_text(encoding="utf-8"))


def _ids(chapter_json):
    return [s["section_id"] for s in chapter_json["sections"]]


class TestChapter1:
    """Chapter 1, Legal Requirements, printed pp. 1-1 to 1-9."""

    def test_sections_as_printed(self):
        ch = _file("chapter01.json")
        assert ch["chapter"] == 1 and ch["chapter_title"] == "Legal Requirements"
        assert _ids(ch) == ["1-1", "1-2", "1-3", "1-4", "1-5", "1-6", "1-7", "1-8"]
        assert load_chapter("california_trenching", 1)["chapter_title"] == "Legal Requirements"

    def test_shop_drawings_for_five_feet(self):
        # p. 1-2 and p. 1-7.
        assert "For any excavation 5 feet or more in depth, the Contractor must submit shop drawings for a protective system." in retrieve_section("california_trenching", "1-1")["body"]
        assert "The Engineer must authorize the excavation shop drawings before work begins." in retrieve_section("california_trenching", "1-7")["body"]

    def test_permit_and_trench_definition(self):
        # p. 1-5.
        body = retrieve_section("california_trenching", "1-3")["body"]
        assert "requires a permit prior to the start of any excavation work 5 feet or deeper into which a person is required to descend." in body
        assert "the width of a trench (measured at the bottom) is not greater than 15 feet." in body

    def test_surcharge_beyond_two_feet_of_spoils(self):
        # p. 1-8.
        body = retrieve_section("california_trenching", "1-7")["body"]
        assert "when a surcharge load exceeds the two feet of spoils (lateral pressure of approximately 72 psf) that the Cal/OSHA CSO reference, an engineered system is required." in body
        assert "\n3. A geotechnical engineer or a civil engineer specializing in soils must prepare soils reports and supplemental data.\n" in body

    def test_railroad_review_time(self):
        # pp. 1-6 to 1-7.
        body = retrieve_section("california_trenching", "1-6")["body"]
        assert "the Structure Construction (SC) [p. 1-7] Falsework Engineer, not with the Engineer on the job site." in body
        assert "allows 65 days for the review of shop drawings for excavations on or affecting railroad properties." in body

    def test_print_slips_kept_with_notes(self):
        assert "The Contact [as printed; evidently Contract] Specifications (CS)" in retrieve_section("california_trenching", "1-1")["body"]
        assert "(Labor Code Section [as printed; no section number is given])" in retrieve_section("california_trenching", "1-2")["body"]
