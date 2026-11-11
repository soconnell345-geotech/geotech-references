"""FEMA P-2082-1 chapters added from the print (app BACKLOG REF-85).

Chapter 22 of Part 1 and the Part 2 commentary to Chapters 11, 19, 20, 21
and 22, read off the printed pages: bodies in the print's own wording with
[p. N] markers, equations typed from renders. Pages are printed page
numbers; the PDF page is the printed page plus 38.
"""

import json
from pathlib import Path

import geotech_references
from geotech_references._retrieval import load_chapter, retrieve_section

TEXT = Path(geotech_references.__file__).parent / "fema_p2082" / "text"


def _ids(chapter_json):
    return [s["section_id"] for s in chapter_json["sections"]]


def _commentary(n):
    return json.loads((TEXT / f"commentary_c{n}.json").read_text(encoding="utf-8"))


def _eq(section_id, equation_id):
    for e in retrieve_section("fema_p2082", section_id)["equations"]:
        if e["equation_id"] == equation_id:
            return e
    raise KeyError(equation_id)


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


class TestCommentaryC20:
    """Part 2, Commentary to Chapter 20, printed pp. 506-513."""

    def test_sections_as_printed(self):
        ch = _commentary(20)
        assert ch["chapter"] == 20
        assert _ids(ch) == ["C20.1", "C20.2", "C20.2.1", "C20.2.2-20.2.5", "C20.3", "C20.4"]
        assert [s["title"] for s in ch["sections"]][4] == "Estimation of Shear Wave Velocity Profiles"

    def test_estimated_velocity_range(self):
        # p. 507: a 68% chance that the actual vs is between vs/1.3 and 1.3vs.
        body = retrieve_section("fema_p2082", "C20.3")["body"]
        assert "approximately a 68% chance that the actual value of vs is between vs/1.3 and 1.3vs." in body
        assert body.startswith("[p. 507] When measured shear wave velocities are not available for a site")

    def test_penetration_resistance_equations(self):
        # p. 509 (C20.3-1) and p. 510 (C20.3-2).
        assert _eq("C20.3", "C20.3-1")["latex"] == r"\ln V_S = c_0 + c_1 \ln(PR) + c_2 \ln f_z + \varepsilon\,\sigma_{\ln Vs}"
        assert r"c_3 \ln f_m" in _eq("C20.3", "C20.3-2")["latex"]
        assert r"\ln(q_t/p_a)" in _eq("C20.3", "C20.3-2")["latex"]

    def test_table_c20_3_1_cells(self):
        # p. 510, Table C20.3-1 (after Brandenberg et al., 2010).
        body = retrieve_section("fema_p2082", "C20.3")["body"]
        assert "Sand | 4.045 | 0.096 | 0.236 | 0.217 | 0.57- 0.07ln σ'v | 0.20" in body
        assert "Clay | 3.996 | 0.230 | 0.164 | 0.227 | 0.21- 0.01ln σ'v | 0.16" in body

    def test_table_c20_3_2_cells(self):
        # p. 511, Table C20.3-2 and its note (b).
        body = retrieve_section("fema_p2082", "C20.3")["body"]
        assert "McGann et al. 2015; Christchurch, NZ | 3.959 | 0.144 | 0.278 | 0.0832 | Note b" in body
        assert "Hegazy & Mayne 2006; cohesive soils (Ic > 2.6) | -2.488 | 1.0 | 0.5 | 1.0 | Note a" in body
        assert "σlnVs = 0.216 − 0.0108z (z = 5-10 m)" in body

    def test_site_class_f_short_period_exception(self):
        # p. 506: liquefiable soils, periods equal to or less than 0.5 seconds.
        body = retrieve_section("fema_p2082", "C20.2.1")["body"]
        assert "fundamental periods of vibration equal to or less than 0.5 seconds" in body

    def test_print_slips_kept_with_notes(self):
        # p. 510 prints "Eq. (C.20.3-1)"; p. 512 cites Section 20.3 for the site class definitions.
        assert "Eq. (C.20.3-1) [as printed" in retrieve_section("fema_p2082", "C20.3")["body"]
        assert "Section 20.3 [as printed; the site class definitions are in Section 20.2" in retrieve_section("fema_p2082", "C20.4")["body"]
