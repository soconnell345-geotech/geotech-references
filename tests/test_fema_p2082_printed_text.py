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


class TestCommentaryC21:
    """Part 2, Commentary to Chapter 21, printed pp. 514-522."""

    def test_sections_as_printed(self):
        ch = _commentary(21)
        assert ch["chapter"] == 21
        assert _ids(ch) == ["C21.0", "C21.1", "C21.1.1", "C21.1.2", "C21.1.3", "C21.2", "C21.2.1",
                            "C21.2.2", "C21.2.3", "C21.3", "C21.4", "C21.5"]

    def test_maximum_direction_factors(self):
        # p. 516: average response factored to the maximum direction.
        body = retrieve_section("fema_p2082", "C21.2")["body"]
        assert ("period-dependent factors of 1.2 at periods less than or equal to 0.2 s, by 1.25 for a period of "
                "1.0 s, and by 1.3 for periods greater than or equal to 10 s") in body

    def test_scenario_earthquake_table_in_its_section(self):
        # p. 517: Table C21.2.2-1, printed after the C21.2.2 text that cites it.
        body = retrieve_section("fema_p2082", "C21.2.2")["body"]
        assert "0.20 | 7.0 | 53% | 7.2 | 16% | 7.9 | 11% | 6.9 | 3%" in body
        assert "5.0 | 7.4 | 24% | 7.4 | 13% | 8.0 | 44% | NA | <1%" in body
        assert "Table C21.2.2-1" not in retrieve_section("fema_p2082", "C21.2.1")["body"]

    def test_ten_percent_contributor_rule(self):
        # pp. 517-518.
        body = retrieve_section("fema_p2082", "C21.2.2")["body"]
        assert ("scenario earthquakes contributing less than 10% of the largest contributor at each period "
                "shall be ignored.") in body
        assert "deaggregations used [p. 518] to determine the earthquake magnitudes." in body
        assert "great (M ≥ 8) or giant (M ≥ 9) earthquakes" in body

    def test_eighty_percent_of_usgs_spectrum(self):
        # p. 518.
        body = retrieve_section("fema_p2082", "C21.2.3")["body"]
        assert ("cannot be taken as less than 80% of the MCER response spectrum obtained from the USGS web "
                "service.") in body

    def test_sd1_period_ranges(self):
        # p. 519, typed from the page.
        body = retrieve_section("fema_p2082", "C21.4")["body"]
        assert "for a period range, 1 s ≤ T ≤ 2 s, for stiffer sites vs > 1,450 ft/s (vs > 442 m/s)" in body
        assert "1 s ≤ T ≤ 5 s, for softer sites vs ≤ 1,450 ft/s (vs ≤ 442 m/s)" in body
        assert "the value of the parameter SDS should be taken as 90% of the peak value" in body


class TestCommentaryC19:
    """Part 2, Commentary to Chapter 19, printed pp. 495-504."""

    def test_sections_as_printed(self):
        ch = _commentary(19)
        assert ch["chapter"] == 19
        assert _ids(ch) == ["C19.1", "C19.2", "C19.3", "C19.4", "C19.4.1", "C19.4.2"]

    def test_reduction_limit_for_low_r(self):
        # p. 497, typed from the page.
        body = retrieve_section("fema_p2082", "C19.2")["body"]
        assert "That is why reductions of 30% are permitted for R = 3 or less." in body
        assert "and then divided by (R/Ie), is input into the mathematical model." in body
        assert "Reductions for kinematic SSI effects are not permitted for the equivalent lateral force and modal response spectrum procedures." in body

    def test_shear_modulus_from_velocity(self):
        # p. 500: G from the small-strain shear wave velocity over half the lesser foundation dimension.
        body = retrieve_section("fema_p2082", "C19.3")["body"]
        assert "G = (G/Go)Go = (G/Go)γvso²/g (all terms defined in the standard)." in body
        assert "The effective depth should be taken as half the lesser dimension of the foundation, which in the provisions is defined as B." in body

    def test_period_lengthening_ratio(self):
        # p. 499.
        body = retrieve_section("fema_p2082", "C19.3")["body"]
        assert "the effective period lengthening ratio, (T̃/T)eff given by Eq. (19.3-2)." in body
        assert "The period lengthening ratio, (T̃/T) appearing in Eq. (19.3-2) is derived in the same manner assuming that μ = 1." in body

    def test_kinematic_limits(self):
        # p. 503: 260 ft effective base size, 0.75 factor, about 20 ft embedment.
        b1 = retrieve_section("fema_p2082", "C19.4.1")["body"]
        assert "effective base size of 260 ft (79.2 m), which is why that limitation has been placed on Eq. (19.4-4)." in b1
        b2 = retrieve_section("fema_p2082", "C19.4.2")["body"]
        assert "effective embedment depth of approximately 20 ft (6.096 m)" in b2
        assert "the provisions are not applicable to embedded individual spread footings." in b2

    def test_print_slips_kept_with_notes(self):
        assert "two [as printed; three are listed] following SSI effects" in retrieve_section("fema_p2082", "C19.1")["body"]
        assert "Eq. (19.2-4) [as printed" in retrieve_section("fema_p2082", "C19.4.2")["body"]


class TestCommentaryC22:
    """Part 2, Commentary to Chapter 22, printed pp. 524-544. Its headings are not numbered;
    the file holds them as C22 and C22.a to C22.g (letters not printed)."""

    def test_sections_and_printed_headings(self):
        ch = _commentary(22)
        assert ch["chapter"] == 22
        assert _ids(ch) == ["C22", "C22.a", "C22.b", "C22.c", "C22.d", "C22.e", "C22.f", "C22.g"]
        titles = [s["title"] for s in ch["sections"]]
        assert titles[4] == "Risk-Targeted Maximum Considered Earthquake (MCER) Spectral Response Accelerations"
        assert titles[6] == "Long-Period Transition Maps"

    def test_table_c22_1_cells(self):
        # p. 525.
        body = retrieve_section("fema_p2082", "C22.a")["body"]
        assert "3b. 84th-percentile calculation | X | X | X |  |  | " in body
        assert "4. Max-direction factors | X |  | X | X |  | X" in body
        assert "the MCER and MCEG ground motions of ASCE/SEI 7-16 (and back to ASCE/SEI 7-98)" in body

    def test_epsilon_and_table_c22_7(self):
        # pp. 539-540: the 84th-percentile ground motion from epsilon; sigma 0.6.
        body = retrieve_section("fema_p2082", "C22.d")["body"]
        assert "dividing the probabilistic ground motion by exp(ε∙σ) ÷ exp(1∙σ)." in body
        assert "0.20 | 2.36 | 1.87 | 1.40 | 1.88 | 1.39 | 2.07 | 1.24" in body
        assert "5.0 | 0.20 | 1.36 | 0.16 | 1.41 | 0.16 | 0.97 | 0.20" in body
        assert "maximum-response ground [p. 541] motions are multiplied by 1.8." in body

    def test_long_period_transition(self):
        # p. 541.
        body = retrieve_section("fema_p2082", "C22.f")["body"]
        assert "is used in Eq. (11.4-7) to determine values of Sa for periods greater than TL." in body
        assert "Thus, for Tc ≤ 10 s, the fundamental convective period range for nearly all storage tanks" in body

    def test_comparison_tables_named_not_typed(self):
        # pp. 529-538: the 34-location comparison tables are named, their cells left to the page.
        body = retrieve_section("fema_p2082", "C22.c")["body"]
        for n in range(2, 7):
            assert f"Table C22-{n} " in body
        assert body.count("[The cells of this table are not typed here:") == 5
        assert "The increase at the Sacramento location (from 0.76g to 0.97g)" in body
