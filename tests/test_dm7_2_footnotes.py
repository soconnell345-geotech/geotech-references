"""DM 7.2 (UFC 3-220-20, 16 January 2025) footnotes and table notes are stored in the
section bodies at their marks, as printed.

Numbered footnotes 1-45 run through the prologue (Chapter 1) and Chapters 2-7; each is
stored as "[Footnote n: text]" right after the word or sentence that carries the mark.
Lettered (and Table 6-10's numbered) notes under tables are stored as
"[Table X-Y note A: text]" after the paragraph that first cites the table.
"""

import json
import re
from pathlib import Path

import pytest

import geotech_references

TEXT = Path(geotech_references.__file__).resolve().parent / "dm7_2" / "text"
STEMS = ["prologue", "chapter02", "chapter03", "chapter04", "chapter05", "chapter06", "chapter07"]


def _sections(stem):
    return json.loads((TEXT / f"{stem}.json").read_text(encoding="utf-8"))["sections"]


def _body(stem, sid):
    return next(s["body"] for s in _sections(stem) if s["section_id"] == sid)


def test_all_45_numbered_footnotes_stored_once():
    seen = []
    for stem in STEMS:
        for s in _sections(stem):
            seen += [int(n) for n in re.findall(r"\[Footnote (\d+): ", s.get("body", ""))]
    assert sorted(seen) == list(range(1, 46))


@pytest.mark.parametrize("stem,count", [
    ("prologue", 6), ("chapter02", 6), ("chapter03", 5), ("chapter04", 10),
    ("chapter05", 2), ("chapter06", 11), ("chapter07", 5),
])
def test_footnote_count_per_chapter(stem, count):
    n = sum(len(re.findall(r"\[Footnote \d+: ", s.get("body", ""))) for s in _sections(stem))
    assert n == count


# (stem, section, text just before the mark, start of the printed footnote); page in comment
PINNED = [
    ("prologue", "P-2.2", "to calculate the shear strength.",
     "The φ = 0 envelope experimentally determined for saturated clays"),          # p. 3, fn 1
    ("prologue", "1-2.11", "at least 75% organic material.",
     "Other groups and organizations have their own definitions of peat"),        # p. 26, fn 5
    ("chapter02", "2-3.3", "authority to take corrective measures.",
     "See OSHA (2020) Paragraph 652(a)(1)(ii)"),                                  # p. 59, fn 8
    ("chapter02", "2-4.3.3", "in the soil below the excavation.",
     "This definition of FBH differs from that proposed by Terzaghi (1943)"),     # p. 73, fn 10
    ("chapter03", "3-6.4", "(Gregory 1993)",
     "Local regulations should be checked."),                                     # p. 159, fn 16
    ("chapter04", "4-7.2", "concrete, wood, vinyl, and plastic.",
     "Plastic and vinyl sheet piles have exceptional corrosion resistance"),     # p. 232, fn 24
    ("chapter04", "4-7.7", "similar to that used in slope stability analyses.",
     "If basal sliding is deemed a possible failure mechanism"),                 # p. 252, fn 27
    ("chapter06", "6-5.4.2", "FHWA 2016",
     "The Alpha Method credited to “Tomlinson (1979)” in FHWA manuals"),          # p. 415, fn 32
    ("chapter06", "6-5.7", "lowered more than 12 ft.",
     "It is important to note that negative skin friction can occur"),            # p. 437, fn 38
    ("chapter07", "7-4.2.1", "Wolff et al. 2004).",
     "This method is sometimes referred to as the Taylor Series approach."),      # p. 535, fn 44
]


@pytest.mark.parametrize("stem,sid,before,start", PINNED)
def test_footnote_at_its_mark(stem, sid, before, start):
    body = _body(stem, sid)
    m = re.search(re.escape(before) + r" \[Footnote \d+: " + re.escape(start), body)
    assert m, f"{sid}: footnote not right after {before!r}"


def test_footnote_23_keeps_the_printed_LFRD_with_a_note():
    # p. 223 prints "LFRD"; stored as printed with a note
    body = _body("chapter04", "4-5.1.2")
    assert "[Footnote 23: If LFRD techniques are used" in body
    assert 'As printed on p. 223: "LFRD"' in body


def test_table_note_count():
    n = 0
    for stem in STEMS:
        for s in _sections(stem):
            n += len(re.findall(r"\[Table [1-7]-\d+ note [A-H1-9]: ", s.get("body", "")))
    assert n == 82


@pytest.mark.parametrize("stem,sid,text", [
    # p. 432, Table 6-26 note E
    ("chapter06", "6-5.5", "[Table 6-26 note E: Minimum spacing is greater of 2.5 ft and s/b = 3.0 (AASHTO 2020)."),
    # p. 411, Table 6-12 note A
    ("chapter06", "6-5.4", "factors of safety may be decreased by factor of 0.75; for extreme loading"),
    # p. 426, Table 6-19 note A (typed from the render)
    ("chapter06", "6-5.4.4", "N1,60 = [0.77·log(40/σʹz)]·N60 where σʹz is the effective vertical stress in ksf"),
    # p. 296, Table 5-8 note B (typed from the render)
    ("chapter05", "5-3.3.3", "For Df/B ≥ 1: k = tan⁻¹(Df/B) in radians"),
    # p. 65, Table 2-4 note B (typed from the render)
    ("chapter02", "2-3.3.4", "Soil Type C: σʹh = (80×H)+72 psf"),
    # p. 526, Table 7-4 note C
    ("chapter07", "7-3.1.5", "[Table 7-4 note C: Mean COV plus one standard deviation"),
])
def test_table_notes_as_printed(stem, sid, text):
    assert text in _body(stem, sid)
