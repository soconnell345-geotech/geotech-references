"""DM 7.1 chapter text: key points, applicability and footnotes read as UFS 3-220-10
(16 Jan 2026) prints them.

The key-point cases pin corrections made when every summary, key point and
applicability field was checked against the print (build of 2026-11-12): each
holds a phrase of the printed sentence and, where the old text said something the
print does not, a term that must stay out. The footnote cases pin the printed page
footnotes that now sit in the bodies at their marks as "[Footnote n: ...]".
Pages in the comments are printed pages (the PDF page is 28 higher).
"""
from functools import lru_cache

import pytest

from geotech_references._retrieval import load_chapter


@lru_cache(maxsize=None)
def _chapter(ch):
    return load_chapter("dm7_1", ch)


def _sec(ch, sid):
    hits = [s for s in _chapter(ch)["sections"] if s["section_id"] == sid]
    assert len(hits) == 1, (sid, len(hits))
    return hits[0]


def _kps(ch, sid):
    return " ".join(_sec(ch, sid)["key_points"])


# (chapter, section, printed phrase a key point must hold, terms that must stay out)
KEY_POINTS = [
    # p. 51: Decker et al. (2008), corrosion above the water table in the fluctuation zone
    (1, "1-5.7.2", "higher corrosion rate on steel piles in the section above the water table", ()),
    # p. 61: aerial images "currently be considered a minimal requirement" (as printed)
    (2, "2-3", "currently be considered a minimal requirement", ()),
    # p. 95: the other dominant subsurface gas
    (2, "2-8.4", "The other dominant subsurface gas is carbon dioxide (CO2)", ()),
    # p. 114: the lugeon was introduced in the 1930s (Houlsby 1976)
    (2, "2-9.4.3", "In the 1930s, the lugeon was introduced to quantify water flow in jointed rock (Houlsby 1976)", ()),
    # p. 177: notation, strain rate is epsilon with a dot
    (3, "3-6", "ε̇ = strain rate", ()),
    # p. 143: ASTM D4253 apparatus
    (3, "3-2.3.2", "many commercial laboratories are not able to perform this test", ()),
    # p. 140: index tests priced within more elaborate tests
    (3, "3-2.2", "may include the cost of certain index tests within more elaborate tests", ()),
    # p. 178: one-third of the ultimate shear strength (Davis and Selvadurai 1996)
    (4, "4-1.2", "less than about one-third of the ultimate shear strength", ()),
    # p. 221: chapter 5 settlement methods
    (5, "5-1.4", "where shear stresses are well below the shear strength", ()),
    # p. 267: smear (FHWA 2017)
    (5, "5-7.4", "Smear tends to be important mostly for drains in high plasticity clays or sensitive soils", ()),
    # p. 268: Eq. 5-27 with average degrees of consolidation
    (5, "5-7.4.1", "Ūc = 100 − (100 − Ūr)(100 − Ūz)/100", ()),
    # p. 279: hydrocompression damage
    (5, "5-9", "worst where the fill depth changes rapidly", ()),
    # p. 306: print slip kept as printed with a note
    (6, "6-4.3", "either suffusion or suffusion (as printed", ()),
    # p. 335: relief trench gradient limit
    (6, "6-5.3", "limiting upward hydraulic gradients in the trench to 0.4", ()),
    # p. 380: plane failure condition 3 as printed, with the evident reading
    (7, "7-10.3.2", "the print writes this as φʹ < ΨF", ()),
    # p. 388: the videography need was stated for the time FHWA (1998) appeared
    (7, "7-10.8.7", "When FHWA (1998) was published", ()),
    # p. 393: one standard deviation below the mean
    (8, "8-1", "the probability is only 16% that the actual value is lower", ("underestimation",)),
    # p. 468: suggested reading, no ranking printed
    (8, "8-9", "Topic Soil Properties: Kulhawy", ("primary reference",)),
    # p. 429: Table 8-11 note
    (8, "8-3.5", "KD = horizontal stress index from dilatometer", ("must be derived",)),
    # p. 450: Figure 8-51 plots Eu/su falling with OCR; the text says "undrained shear modulus"
    (8, "8-5.2.2", "the text prints 'undrained shear modulus'", ("higher Eu/su",)),
]


@pytest.mark.parametrize("ch,sid,phrase,absent", KEY_POINTS,
                         ids=[c[1] for c in KEY_POINTS])
def test_key_point_reads_as_printed(ch, sid, phrase, absent):
    kps = _kps(ch, sid)
    assert phrase in kps, (sid, kps)
    for term in absent:
        assert term not in kps, (sid, term)


# p. 236: immediate settlement may be significant for unsaturated or heavily
# overconsolidated clay (the old text named only one of the two).
def test_immediate_settlement_applicability_names_both_cases():
    assert "unsaturated or heavily overconsolidated clay" in _sec(5, "5-5.1")["applicability"]


# p. 406: 8-2.2 prints no slope-failure scope.
def test_fine_grained_strength_applicability_has_no_unprinted_scope():
    assert "first-time" not in _sec(8, "8-2.2")["applicability"]


# (chapter, section, footnote number, start of the printed footnote)
FOOTNOTES = [
    (1, "1-2.1", 1, "In this context, unconsolidated means that the particles have not lithified into rock"),  # p. 3
    (2, "2-7.4.1", 2, "DCP is often used to represent the DCP Index in equations"),  # p. 89
    (3, "3-2.3.2", 3, "Some engineers use the dry density obtained from ASTM D4253"),  # p. 142
    (3, "3-2.4.1.2", 4, "Although ASTM D7181 allows directly extruded samples to be tested"),  # p. 146
    (3, "3-2.4.1.3", 5, "It is not clear why the letter R is used for this test"),  # p. 148
    (3, "3-2.4.1.4", 6, "Although some older testing manuals provide instructions for conducting staged CU and CD"),  # p. 149
    (3, "3-2.4.2", 7, "A saturated soil is often called a"),  # p. 151
    (3, "3-2.4.2.2", 8, "ASTM D2850 suggests using a strain rate of 0.3% for brittle soils"),  # p. 153
    (3, "3-2.4.2.2", 9, "There are test apparatuses available for conducting triaxial tests on partially saturated"),  # p. 154
    (3, "3-2.6.1", 10, "The compression curve is often called the"),  # p. 165
    (5, "5-4.1.4", 11, "In this context, reliability was defined as the percentage of cases where the measured set"),  # p. 234
    (5, "5-5.2.1", 12, "In old soil mechanics references, the water content was often used in lieu of void ratio"),  # p. 237
    (7, "7-8", 13, "This example is intentionally left uncited to maintain anonymity of the source."),  # p. 366
    (8, "8-3.2", 14, "For this to be true, ideal or remolded soils must be assumed to follow the tenets of critical state soil mechanics"),  # p. 424
]


@pytest.mark.parametrize("ch,sid,n,start", FOOTNOTES, ids=[f"fn{c[2]}" for c in FOOTNOTES])
def test_footnote_in_body_at_its_section(ch, sid, n, start):
    assert f"[Footnote {n}: {start}" in _sec(ch, sid)["body"]


def test_each_footnote_stored_once():
    seen = {}
    for ch in range(1, 9):
        for s in _chapter(ch)["sections"]:
            for n in range(1, 15):
                k = s["body"].count(f"[Footnote {n}: ")
                if k:
                    seen[n] = seen.get(n, 0) + k
    assert seen == {n: 1 for n in range(1, 15)}, seen
