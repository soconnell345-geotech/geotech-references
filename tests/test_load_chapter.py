"""``load_chapter`` loads every chapter ``list_chapters`` lists.

2026-11-10 review (core-15): the file was built from the number
(``chapterNN.json``), so the 17 chapter files named otherwise could not be
loaded although ``list_chapters`` listed them: the UFC 3-220-20 prologue and
Appendix B, the Eurocode 7 Part 2 section and annex files, and the
appendices of GEC-9, GEC-10, GEC-12 and UFC 3-250-11.
"""

from pathlib import Path

import pytest

from geotech_references import _retrieval

PKG = Path(_retrieval.__file__).parent
REFERENCES = sorted(d.name for d in PKG.iterdir() if (d / "text").is_dir()
                    and any((d / "text").glob("*.json")))


@pytest.mark.parametrize("reference", REFERENCES)
def test_every_listed_chapter_loads(reference):
    listed = _retrieval.list_chapters(reference, sections=False)
    assert listed
    for item in listed:
        data = _retrieval.load_chapter(reference, item["chapter"])
        assert data["chapter"] == item["chapter"]
        assert data.get("chapter_title", "") == item["chapter_title"]


@pytest.mark.parametrize("reference,chapter,file_name", [
    ("dm7_2", 0, "prologue.json"),
    ("gec_12", 22, "appendix_d.json"),
    ("eurocode_7_2", 7, "annex_field_tests.json"),
    ("ufc_stabilization", 6, "appendix_a.json"),
])
def test_a_file_not_named_for_its_number_is_found(reference, chapter,
                                                  file_name):
    import json
    want = json.loads((PKG / reference / "text" / file_name).read_text(
        encoding="utf-8"))
    assert _retrieval.load_chapter(reference, chapter) == want
    # the size-limited form works for it too
    out = _retrieval.load_chapter(reference, chapter, max_chars=3000)
    assert out["chapter"] == chapter


def test_a_missing_chapter_names_the_chapters_there_are():
    with pytest.raises(FileNotFoundError) as e:
        _retrieval.load_chapter("ufc_stabilization", 99)
    assert "its chapters: 6, 7, 8, 1, 2, 3, 4, 5" in str(e.value)
