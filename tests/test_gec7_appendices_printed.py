"""GEC-7 (FHWA-NHI-14-007, 2015) Appendices B and C pinned to the print.

REF-85 (app backlog): the library held GEC-7's ten chapters but not its
appendices, so the preliminary design charts' procedure and the design
example could not be searched or quoted. Appendix B (charts for preliminary
design, pp. 295 to 300) is chapter 12 and Appendix C (design example, pp.
301 to 317) chapter 13, in the print's own wording with [p. 301] markers;
every equation, calculation line and table is typed in from a rendered page
(the text layer carries the example's equations as scattered glyphs and
spoken words). Where the print disagrees with itself the stored text keeps
the print and says so "(as printed; ...)". Chapter 11 is left for Appendix A.
"""

import json
import re

import pytest

from geotech_references._retrieval import load_chapter, retrieve_section
from geotech_references.gec_7 import tables


def _section(sid):
    return retrieve_section("gec_7", sid)


def _appendix(ch):
    return load_chapter("gec_7", ch)


def _all_text(ch):
    out = []
    for s in _appendix(ch)["sections"]:
        eqs = [json.dumps(e, ensure_ascii=False) for e in s["equations"]]
        out += [s["body"]] + s["tables"] + s["figures"] + eqs
    return " ".join(out)


def _scatter_free(body):
    """The patterns a text-layer formula leaves when it scatters."""
    assert not re.search(r"(^|\s)[′']($|\s)|\(['′]\)", body)          # a detached prime
    assert not re.search(r"(?m)^\d\s*$", body)                         # a lone digit line
    for a, b in ("()", "[]"):
        assert body.count(a) == body.count(b)                          # unbalanced brackets
    paras = [p for p in body.split("\n\n") if len(p) > 40]
    assert all(x != y for x, y in zip(paras, paras[1:]))               # a repeated paragraph
    for spoken in (" sub ", "as previously described", "fraction", "squared"):
        assert spoken not in body


B_EQS = {
    "Eq. B.1": "μ = qU DDH / (FSPO γs SH SV)",
    "Eq. B.2": "L/H (corrected) = C1L × C2L × C3L × L/H (from charts)",
    "Eq. B.3": "C1L = 1.50 - 0.15 DDH + 0.0065 DDH²",
    "Eq. B.4": "C2L = -4.0 c* + 1.09 ≥ 0.85",
    "Eq. B.5": "C3L = 0.52 FSOS + 0.30 ≥ 1.0",
    "Eq. B.6": "tmax (corrected) = C1F × C2F × tmax (from charts)",
    "Eq. B.7": "C1F = -0.3 + 0.4 DDH - 0.017 DDH²",
    "Eq. B.8": "C2F = -4.0 c* + 1.09 ≥ 0.85",
}

C_IDS = ["C", "C.1", "C.2", "C.3", "C.3.a", "C.3.b", "C.4", "C.4.a", "C.4.e", "C.4.f", "C.5",
         "C.6", "C.6.a", "C.6.b", "C.6.c", "C.7", "C.7.a", "C.7.b", "C.7.c", "C.7.d", "C.7.e",
         "C.7.f", "C.7.g", "C.8", "C.8.a", "C.8.b"]


# ---------------------------------------------------------------- Appendix B

def test_appendix_b_chapter_and_section():
    data = _appendix(12)
    assert data["chapter_title"] == "Appendix B: Charts for Preliminary Design"
    assert data["reference_id"] == "FHWA-NHI-14-007"
    assert [s["section_id"] for s in data["sections"]] == ["B"]
    body = _section("B")["body"]
    # pp. 298 to 300 hold only the charts
    assert re.findall(r"\[p\. (\d+)\]", body) == ["295", "296", "297"]
    _scatter_free(body)


@pytest.mark.parametrize("printed", [
    # p. 295
    "However, the charts should not replace the use of soil nail design computer programs for "
    "more complex conditions and for other drastically different conditions.",
    "• normalized cohesion, c* = c′/γs H = 0.02",
    "• factor of safety for overall stability, FSOS = 1.35",
    "• drill hole diameter, DDH = 4 in.",
    # p. 296
    "• Factor of safety for pullout (FSPO, usually 2.0).",
    "Interpolate between φs = 27, 31, 35 or 39 degrees as needed.",
    "Note that only sufficiently high values of φs will achieve the selected FSOS for relatively "
    "large values of β.",
    "8. Calculate the soil nail maximum force (Tmax) by multiplying tmax read from the chart by "
    "γs, H, SV and SH.",
])
def test_appendix_b_printed_sentences(printed):
    assert printed in _section("B")["body"]


def test_appendix_b_equations_typed_from_the_page():
    # pp. 296 and 297 (PDF 336, 337), 200 dpi renders
    eqs = _section("B")["equations"]
    assert [e["id"] for e in eqs] == list(B_EQS)
    body = _section("B")["body"]
    for e in eqs:
        assert e["formula"] == B_EQS[e["id"]]
        assert e["implemented_in"] is None
        assert body.count(e["formula"] + " (Equation B." + e["id"][-1] + ":") == 1
    # the corrections are 1 for the charts' assumptions (DDH = 4 in., c* = 0.02,
    # FSOS = 1.35), within the print's rounding, except C1F = 1.028
    assert abs(1.50 - 0.15 * 4 + 0.0065 * 16 - 1.0) < 0.01
    assert abs(-4.0 * 0.02 + 1.09 - 1.0) < 0.02
    assert abs(0.52 * 1.35 + 0.30 - 1.0) < 0.01
    assert round(-0.3 + 0.4 * 4 - 0.017 * 16, 3) == 1.028
    assert "(\"correction correction\" as printed)" in body


def test_appendix_b_figures():
    figs = _section("B")["figures"]
    assert figs == [
        "Figure B.1: Illustration. Conditions for calculations with charts",
        "Figure B.2: Chart. Batter = 0 deg. - Backslope 0 deg",
        "Figure B.3: Chart. Batter = 0 deg. - Backslope 10 deg",
        "Figure B.4: Chart. Batter = 0 deg. - Backslope 30 deg",
    ]


def test_appendix_sections_fit_the_tools():
    for s in _appendix(12)["sections"]:
        assert len(s["body"]) <= 12000
        assert len(json.dumps(s)) <= 14000
