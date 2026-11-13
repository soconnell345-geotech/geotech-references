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
    # p. 153: "should always be interpreted with a φ = 0 failure envelope"
    (3, "3-2.4.2.2", "should always be interpreted with a φ = 0 failure envelope", ("must always",)),
    # p. 413: Eq. 8-16 is Carter and Bentley's (2016) fit to Gibson's trend line; the 5% is theirs
    (8, "8-2.2.2", "Carter and Bentley (2016) approximate its trend line by Eq. 8-16",
     ("Gibson (1953) Eq. 8-16",)),
    # p. 271: the Figure 5-27 method "can also be used"; the print names no equations
    (5, "5-7.4.3", "The method presented in Figure 5-27 can also be used with vertical drains.",
     ("applies directly", "Eq. 5-20")),
    # p. 373: Td "should be divided by a factor of safety for geosynthetic strength (FR) of at least 1.3"
    (7, "7-9.5", "should be divided by a factor of safety for geosynthetic strength (FR) of at least 1.3",
     ("requires FR",)),
    # Force-word sweep: the print's own modality
    # p. 179: including ponded water "is imperative"; as a layer it "can be considered"
    (4, "4-2.1.1", "it can be considered by adding a layer", ("must be included as a layer",)),
    # p. 180: "the water does not sustain shear stress"
    (4, "4-2.1.2", "the water does not sustain shear stress", ("cannot sustain",)),
    # p. 304: "the lack of a "roof" prevents the progression of a pipe"
    (6, "6-4.2", "the lack of a roof prevents the progression of a pipe", ("a pipe cannot form",)),
    # p. 364: "It is often necessary to increase the factor of safety of existing slopes"
    (7, "7-7", "It is often necessary to increase the factor of safety", ("Slope stabilization is required",)),
]


@pytest.mark.parametrize("ch,sid,phrase,absent", KEY_POINTS,
                         ids=[c[1] for c in KEY_POINTS])
def test_key_point_reads_as_printed(ch, sid, phrase, absent):
    kps = _kps(ch, sid)
    assert phrase in kps, (sid, kps)
    for term in absent:
        assert term not in kps, (sid, term)


# p. 236: immediate settlement may be significant for unsaturated or heavily
# overconsolidated clay (the old text said "saturated").
def test_immediate_settlement_applicability_names_both_cases():
    assert "unsaturated or heavily overconsolidated clay" in _sec(5, "5-5.1")["applicability"]


# p. 406: 8-2.2 prints no slope-failure scope.
def test_fine_grained_strength_applicability_has_no_unprinted_scope():
    assert "first-time" not in _sec(8, "8-2.2")["applicability"]


def _variables(ch, sid, eq_id):
    hits = [e for e in _sec(ch, sid)["equations"] if e["id"] == eq_id]
    assert len(hits) == 1, (sid, eq_id, len(hits))
    return hits[0].get("variables", {})


# (chapter, section, equation, symbol, printed definition in its where-list)
WHERE_LISTS = [
    (2, "2-9.1.2", "Eq. 2-1", "D", "diameter of the vane"),  # p. 101
    (5, "5-5.2.2", "Eq. 5-12", "σ'z0", "initial vertical stress at the midpoint of the soil layer or sublayer"),  # p. 241
    (5, "5-5.2.2", "Eq. 5-12", "Δσz", "change in vertical stress at layer midpoint"),  # p. 241
    (8, "8-2.1.3", "Eq. 8-7", "Pa", "atmospheric pressure in same units as vertical stress and qc"),  # p. 400
    (8, "8-2.1.3", "Eq. 8-8", "σ′v", "effective vertical stress in same units as qc"),  # p. 402
    (8, "8-2.1.4", "Eq. 8-10", "p0", "corrected pressure required to initiate movement of the membrane against the soil"),  # p. 406
    (8, "8-2.2.1", "Eq. 8-15", "Pa", "atmospheric pressure in same units as stress"),  # p. 411
    (8, "8-4.1.2", "Eq. 8-30", "eL", "void ratio at water content equal to the liquid limit"),  # p. 439
    (8, "8-4.3", "Eq. 8-32", "Pa", "atmospheric pressure (same units as Mds and σ′v)"),  # p. 442
    (5, "5-5.2.2", "Eq. 5-14", "σ'p", "preconsolidation stress"),  # p. 241
]


# pp. 98, 105, 106: the figure pointers as printed, at their places in the bodies
FIGURE_POINTERS = [
    (2, "2-9.1.1", "usually behind a piezocone. A schematic of the PMT equipment and test is shown in Figure 2-14."),
    (2, "2-9.3.1.1", "from a volume-calibrated container as shown in Figure 2-19. The water balloon"),
    (2, "2-9.3.1.2", "is the volume of the sample. A conventional drive cylinder is shown in Figure 2-20. This method"),
]


@pytest.mark.parametrize("ch,sid,text", FIGURE_POINTERS, ids=[c[1] for c in FIGURE_POINTERS])
def test_figure_pointer_in_body(ch, sid, text):
    assert text in _sec(ch, sid)["body"]


# p. 446: the Eq. 8-35 where-list gives wn no unit
def test_eq_8_35_states_no_printed_unit():
    eq = [e for e in _sec(8, "8-4.4")["equations"] if e["id"] == "Eq. 8-35"][0]
    assert "(in %)" not in eq["description"]
    assert "prints no unit" in eq["description"]


@pytest.mark.parametrize("ch,sid,eq_id,sym,definition", WHERE_LISTS,
                         ids=[f"{c[2]}-{c[3]}" for c in WHERE_LISTS])
def test_equation_where_list_as_printed(ch, sid, eq_id, sym, definition):
    assert _variables(ch, sid, eq_id).get(sym) == definition


# p. 162: the cyclic DSS failure definition closes 3-2.5.1.1.
def test_cyclic_dss_failure_definition_in_body():
    assert ("Failure is defined as a pore pressure ratio of 100% or a limiting cyclic shear strain."
            in _sec(3, "3-2.5.1.1")["body"])


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


# Table notes the bodies lacked until the review of 2026-11-12.
TABLE_NOTES = [
    (5, "5-4.1.1", "[Note to Table 5-2: Correlations provide values of Es in ksf units.]"),  # p. 231
    (1, "1-5.4.2", '[Notes to Table 1-22: "A" means preferred method and "B" alternate method'
                   ' based on the 2020 version of the standard.]'),  # p. 49
]


@pytest.mark.parametrize("ch,sid,note", TABLE_NOTES, ids=[c[1] for c in TABLE_NOTES])
def test_table_note_in_body(ch, sid, note):
    assert note in _sec(ch, sid)["body"]


# p. 260: Table 5-8 prints (1−νs)² in both Km formulas and (1−νm)² under the rectangular one.
def test_table_5_8_km_formulas_as_printed():
    eqs = {e["id"]: e for e in _sec(5, "5-6.3")["equations"]}
    assert eqs["Table 5-8 (Circular)"]["formula"] == "Km = 8 · [Em·(1−νs)² / Es] · (tm³ / B³)"
    assert eqs["Table 5-8 (Rectangular)"]["formula"] == (
        "Km = (4/3) · [Em·(1−νs)² / (Es·(1−νm)²)] · (tm³ / B³)")
