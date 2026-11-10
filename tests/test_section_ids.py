"""A section number names one section of a reference, in both fetch layers.

2026-11-10 review (core-01, core-08). Twenty-two numbers were held by two
sections each: GEC-13 chapter 1 kept the print's local numbers bare
('8.2.7'), the form chapters 2-10 use for chapter 8's section 2.7; the
AASHTO 1993 Guide restarts its chapters in each Part; the UFC 3-250-11
appendices were numbered 1, 2, 3 each. ``reference_get`` returned the first
one indexed, ``retrieve_section`` the one in the file the number's first
part named, so the two disagreed and 23 sections could not be fetched at
all. And a number sent as a JSON number (7.10) arrived as 7.1, another
section.
"""

from pathlib import Path

import pytest

from geotech_references import _retrieval, _retrieval_db

PKG = Path(_retrieval.__file__).parent
REFERENCES = sorted(d.name for d in PKG.iterdir() if (d / "text").is_dir()
                    and any((d / "text").glob("*.json")))


@pytest.mark.parametrize("reference", REFERENCES)
def test_no_number_is_held_by_two_sections(reference):
    held = _retrieval.duplicate_section_ids(PKG / reference / "text")
    assert not held, (
        f"{reference}: a section number must be the only one in the "
        f"reference: {dict(list(held.items())[:5])}")


def test_the_index_holds_no_number_twice():
    rows = _retrieval_db.reference_query(
        "SELECT reference, section_id, COUNT(*) AS n FROM sections "
        "WHERE reference NOT LIKE 'local_%' "
        "GROUP BY reference, section_id HAVING n > 1")
    assert rows == []


# (reference, number, title, where the print shows it)
PRINTED = [
    # GEC-13 Vol I, PDF page 60 (printed 1-46): chapter 1, "8.2.7 Step 7:
    # Consider Project Risks"; the id carries the chapter, as chapters 2-10
    ("gec_13", "1.8.2.7", "Step 7: Consider Project Risks", 1),
    # GEC-13 Vol II, PDF page 213: chapter 8, "2.7 Jet Grouting"
    ("gec_13", "8.2.7", "Jet Grouting", 8),
    # AASHTO 1993 Guide, PDF page 23 (printed I-3): Part I, Chapter 1,
    # "1.1 SCOPE OF THE GUIDE"
    ("aashto_1993", "I-1.1", "Scope of the Guide", 1),
    # PDF page 93 (printed II-3): Part II, Chapter 1, "1.1 BACKGROUND"
    ("aashto_1993", "II-1.1", "Background", 6),
    # UFC 3-250-11, PDF page 71 (printed 63): "A-1 THICKNESS
    # CRITERIA-STABILIZED SOIL LAYERS"; "A-1.1 Equivalency Factors."
    ("ufc_stabilization", "A-1",
     "Thickness Criteria - Stabilized Soil Layers", 6),
    ("ufc_stabilization", "A-1.1", "Equivalency Factors", 6),
    # PDF page 79 (printed 71): "B-1 ACRONYMS"
    ("ufc_stabilization", "B-1", "Acronyms", 7),
    # PDF page 83 (printed 75): "APPENDIX C REFERENCES", which numbers no
    # paragraph, so the appendix letter is its number
    ("ufc_stabilization", "C", "References", 8),
]


@pytest.mark.parametrize("reference,number,title,chapter", PRINTED)
def test_both_layers_fetch_the_printed_section(reference, number, title,
                                               chapter):
    from_index = _retrieval_db.reference_get(reference, number)
    from_files = _retrieval.retrieve_section(reference, number)
    assert from_index["title"] == from_files["title"] == title
    assert from_index["chapter"] == chapter
    assert from_index["body"] == from_files["body"]


@pytest.mark.parametrize("reference", ["gec_13", "aashto_1993",
                                       "ufc_stabilization"])
def test_both_layers_agree_on_every_section(reference):
    rows = _retrieval_db.reference_query(
        "SELECT section_id, title FROM sections WHERE reference = "
        f"'{reference}' AND (chapter = 1 OR reference != 'gec_13') LIMIT 50")
    assert rows
    for row in rows:
        got = _retrieval.retrieve_section(reference, row["section_id"])
        assert got["title"] == row["title"], row["section_id"]


@pytest.mark.parametrize("reference,number,names", [
    # the bare number is printed in two Parts: neither is returned
    ("aashto_1993", "1.1", ["I-1.1 Scope of the Guide", "II-1.1 Background"]),
    ("aashto_1993", "2.3.5", ["II-2.3.5"]),
    ("ufc_stabilization", "1", ["A-1 Thickness Criteria", "B-1 Acronyms"]),
])
def test_a_bare_number_names_the_lettered_sections(reference, number, names):
    for fetch in (_retrieval_db.reference_get, _retrieval.retrieve_section):
        with pytest.raises(KeyError) as e:
            fetch(reference, number)
        for name in names:
            assert name in str(e.value)


@pytest.mark.parametrize("number", [7.10, 7, None, ["7.10"]])
def test_a_number_that_is_not_text_is_refused(number):
    """GEC-12 7.10 sent as a JSON number is 7.1, another section."""
    for fetch in (_retrieval_db.reference_get, _retrieval.retrieve_section):
        with pytest.raises(TypeError, match="in quotes"):
            fetch("gec_12", number)
    assert _retrieval_db.reference_get("gec_12", "7.10")["title"] != \
        _retrieval_db.reference_get("gec_12", "7.1")["title"]
