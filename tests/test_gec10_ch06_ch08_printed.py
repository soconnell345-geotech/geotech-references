"""GEC-10 (FHWA-NHI-18-024, 2018) chapters 6 and 8 text pinned to the print.

REF-81 (app backlog): 9 of the 12 sections of chapter 6 (Rebar Cages) and 2 of
the 3 of chapter 8 (Drilled Shaft Design Process) were written from memory
(review of 2026-11-10, finding text-05). Both chapters were rewritten from the
printed pages: bodies in the print's own wording with [p. 6-5] markers, Tables
6-1 to 6-3 and 8-1 to 8-4 and Eq. 8-1 typed in from rendered pages. Printed
8.1 (pp. 8-1 to 8-17) is stored as 8.1 and parts 8.1.a to 8.1.d (letters not
printed) to fit the reference tools' size limit.
"""

import json
import math

import pytest

from geotech_references._retrieval import load_chapter, retrieve_section
from geotech_references.gec_10.tables import table_8_4_resistance_factor


def _section(sid):
    return retrieve_section("gec_10", sid)


def _eq_text(eq):
    return eq if isinstance(eq, str) else json.dumps(eq, ensure_ascii=False)


def _text(sid):
    s = _section(sid)
    return " ".join([s["body"]] + s["key_points"] + s["tables"] + s["figures"]
                    + [_eq_text(e) for e in s["equations"]])


def _chapter_text(ch):
    return " ".join(_text(s["section_id"]) for s in load_chapter("gec_10", ch)["sections"])


CH6_TITLES = {
    "6.1": "Introduction",
    "6.2": "Properties of Reinforcing Steel",
    "6.3": "Longitudinal Reinforcing",
    "6.4": "Transverse Reinforcement",
    "6.5": "Splices",
    "6.6": "Connection Between Drilled Shaft and Column",
    "6.7": "Fabrication and Storage",
    "6.8": "Sizing Hoops",
    "6.9": "Centering Devices",
    "6.10": "Bracing of Rebar Cages",
    "6.11": "Rebar Cage Lifting and Placement",
    "6.12": "Summary",
}


class TestStructure:
    def test_chapter_6_sections_and_titles_as_printed(self):
        data = load_chapter("gec_10", 6)
        assert data["chapter_title"] == "Rebar Cages"
        got = {s["section_id"]: s["title"] for s in data["sections"]}
        assert got == CH6_TITLES

    def test_chapter_8_sections(self):
        data = load_chapter("gec_10", 8)
        assert data["chapter_title"] == "Drilled Shaft Design Process"
        ids = [s["section_id"] for s in data["sections"]]
        assert ids == ["8.1", "8.1.a", "8.1.b", "8.1.c", "8.1.d", "8.2", "8.3"]
        assert _section("8.1")["title"] == (
            "Outline of the Overall Design and Construction Process")
        assert _section("8.2")["title"] == (
            "Calibration of Resistance Factors to Regional Conditions or Agency Practice")
        assert _section("8.3")["title"] == "Summary"
        for sid in ("8.1.a", "8.1.b", "8.1.c", "8.1.d"):
            s = _section(sid)
            assert s["title"].startswith(
                "Outline of the Overall Design and Construction Process (continued, Block")
            assert "letter is not printed" in s["applicability"]

    @pytest.mark.parametrize("ch", [6, 8])
    def test_every_body_starts_with_a_printed_page_marker(self, ch):
        for s in load_chapter("gec_10", ch)["sections"]:
            assert s["body"].startswith(f"[p. {ch}-"), s["section_id"]

    @pytest.mark.parametrize("ch", [6, 8])
    def test_sections_fit_the_reference_tools(self, ch):
        for s in load_chapter("gec_10", ch)["sections"]:
            assert len(s["body"]) <= 12000, s["section_id"]
            assert len(json.dumps(s)) <= 14000, s["section_id"]

    @pytest.mark.parametrize("ch", [6, 8])
    def test_key_points_cite_their_page(self, ch):
        for s in load_chapter("gec_10", ch)["sections"]:
            for kp in s["key_points"]:
                assert "(p. " in kp or "(pp. " in kp or ", p. " in kp, kp

    def test_all_22_printed_blocks_in_8_1(self):
        t = " ".join(_section(s)["body"]
                     for s in ("8.1", "8.1.a", "8.1.b", "8.1.c", "8.1.d"))
        for n in range(1, 23):
            assert f"Block {n}:" in t, n
        # p. 8-15: Block 16 is plans and specifications (the old text made it
        # the construction phase)
        assert "Block 16: Prepare Plans and Specifications" in t
        assert "Block 22: Post-Construction Evaluation and Report" in t


class TestChapter6Printed:
    def test_6_3_clear_spacing_is_a_minimum(self):
        t = _text("6.3")
        # p. 6-5, AASHTO (2017a) Article 5.12.9.5.2
        assert "[p. 6-5]" in t
        assert ("clear distance between parallel longitudinal, and parallel "
                "transverse reinforcing bars in cast-in-place concrete piling shall "
                "not be less than the greater of the following") in t
        assert "Five times the maximum aggregate size" in t and "5.0 in." in t
        assert "should be considered minimum values" in t
        assert "eight times the size of the largest coarse aggregate" in t
        assert "5 inches in both the vertical and horizontal direction" in t
        assert "at least ten times the size of the largest coarse aggregate" in t

    def test_6_3_stale_maximum_spacing_gone(self):
        t = _chapter_text(6)
        assert "should not exceed 6 inches" not in t
        assert "≤6 inches" not in t

    def test_6_3_minimum_steel_and_full_length(self):
        t = _text("6.3")
        assert "minimum percentage of longitudinal steel of 0.5% provides a lower bound" in t
        assert "Seismic Zones 3 and 4 to be reinforced over the full length" in t
        assert "at least six" in t

    def test_6_4_pitch_and_development_length(self):
        t = _text("6.4")
        # p. 6-8
        assert "less than 5 inch pitch" in t
        assert "clear space between hoops to at least 5 inches" in t
        # p. 6-7, typed in from the 300 dpi render
        assert "0.04 A_b f_y/[(f'_c)^0.5]" in t
        assert "lapped for one full turn" in t

    def test_6_4_stale_pitch_limits_gone(self):
        t = _chapter_text(6)
        assert "minimum 3 inches (governed by concrete placement)" not in t
        assert "maximum 6 inches for seismic zones" not in t
        assert "maximum aggregate size + 1.5 in." not in t

    def test_6_5_splices(self):
        t = _text("6.5")
        assert "60 ft or less" in t
        assert "Not more than 50 per cent of the splices should be at any one level" in t
        assert "subject to approval by the engineer of record" in t

    def test_6_5_stale_values_gone(self):
        t = _chapter_text(6)
        assert "125%" not in t
        assert "≥2 ft" not in t

    def test_6_6_cover_and_alignment(self):
        t = _text("6.6")
        assert "drilled shaft is specified to be 6 inches larger in diameter than the column" in t
        assert "adjusted by 3 inches in any direction" in t

    def test_6_7_tie_wire_and_transverse_bar_size(self):
        t = _text("6.7")
        assert "No. 15 gauge (dia = 0.072 in) should be considered the minimum" in t
        assert "No. 14 gauge (dia = 0.083 inches) is recommended" in t
        # p. 6-17
        assert "[p. 6-17]" in t
        assert "Once the cage diameter reaches 4 ft, a minimum bar size of No. 5" in t

    def test_6_8_sizing_hoops_are_fabrication_guides(self):
        t = _text("6.8")
        assert "spaced at 8 to 10 ft longitudinally" in t
        assert "not considered in the structural design" in t
        assert "typically 3 inches minimum" not in t

    def test_6_9_cover_by_diameter(self):
        t = _text("6.9")
        # p. 6-18
        assert ("minimum concrete cover should be 3 inches for drilled shafts with "
                "diameters up to 3 ft; 4 inches for diameters greater than 3 ft and "
                "less than 5 ft; and 6 inches for drilled shaft diameters of 5 ft and "
                "larger") in t
        assert "not less than five times the largest size of coarse aggregate" in t
        assert "Figure 6-20 shows examples of sled centralizers" in t

    def test_6_10_bracing(self):
        t = _text("6.10")
        assert "length to diameter ratio of 8 or greater" in t
        assert "minimum bar size of No. 8 is recommended" in t

    def test_6_11_lifting(self):
        t = _text("6.11")
        assert "factor of safety of 2 or greater" in t
        assert "Figure 6-25 shows a well-executed lifting sequence" in t
        assert "< 20 ft: 1 block, 1 point rigging" in t
        assert "40 to 140 ft: 2 blocks or 2 cranes, multi-point rigging" in t
        assert "> 140 ft: Lift Table is most appropriate" in t

    def test_table_6_1_typed_in(self):
        t = _text("6.2")
        assert "A615, M 31, deformed and plain billet-steel bars: 40, 60, 75, 80, 100 ksi; not weldable; No. 18" in t
        assert "A706, no AASHTO No." in t and "60, 80 ksi; weldable; No. 18" in t

    # Table 6-2 (p. 6-3) as typed in: bar No.: weight, diameter, area, perimeter
    TABLE_6_2 = {
        3: (0.376, 0.375, 0.11, 1.178), 4: (0.668, 0.500, 0.20, 1.571),
        5: (1.043, 0.625, 0.31, 1.963), 6: (1.502, 0.750, 0.44, 2.356),
        7: (2.044, 0.875, 0.60, 2.749), 8: (2.670, 1.000, 0.79, 3.142),
        9: (3.400, 1.128, 1.00, 3.544), 10: (4.303, 1.270, 1.27, 3.990),
        11: (5.313, 1.410, 1.56, 4.430), 14: (7.650, 1.693, 2.25, 5.320),
        18: (13.600, 2.257, 4.00, 7.090),
    }

    @pytest.mark.parametrize("bar", sorted(TABLE_6_2))
    def test_table_6_2_row_stored_and_consistent(self, bar):
        w, d, a, p = self.TABLE_6_2[bar]
        t = _text("6.2")
        assert f"No. {bar}: {w:.3f}, {d:.3f}, {a:.2f}, {p:.3f}" in t
        # the printed perimeter and area are those of a round bar of the
        # printed diameter
        assert p == pytest.approx(math.pi * d, abs=0.002)
        assert a == pytest.approx(math.pi * d * d / 4, abs=0.006)


class TestChapter8Printed:
    def test_eq_8_1_as_printed(self):
        s = _section("8.1.b")
        eq = s["equations"][0]
        assert eq["id"] == "Eq. 8-1"
        assert eq["formula"] == "∑ ηi γi Qi ≤ ∑ φi Ri"
        assert set(eq["variables"]) == {"ηi", "γi", "Qi", "φi", "Ri"}
        assert "γI" in eq["notes"]
        assert "∑ ηi γi Qi ≤ ∑ φi Ri (8-1)" in s["body"]

    def test_most_common_limit_states(self):
        t = _text("8.1.b")
        assert ("Strength I, Strength IV, Extreme Event I (earthquake), and Service I") in t
        assert "are not relevant to foundation design" in t

    def test_table_8_2_rows(self):
        t = _text("8.1.b")
        assert "Strength I (unless noted): γp | 1.75 | 1.00 | - | - | 1.00 | 0.50/1.20 | γTG | γSE" in t
        assert "Strength IV: γp | - | 1.00 | - | - | 1.00 | 0.50/1.20 | - | -" in t
        assert "Extreme Event I: 1.00 | γEQ | 1.00 | - | - | 1.00 | - | - | - | EQ 1.00" in t
        assert "Service I: 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00/1.20 | γTG | γSE" in t

    def test_table_8_3_drilled_shaft_downdrag(self):
        t = _text("8.1.b")
        assert "Drilled shafts, O'Neill and Reese (2010) Method 1.25 / 0.35" in t
        assert "DC: Strength IV only 1.50 / 0.90" in t

    def test_table_8_4_text(self):
        t = _text("8.1.c")
        assert "cohesionless soil, Beta method: 0.55 / 0.45" in t
        assert "rock, Eq. 10-21: 0.50 / 0.40" in t
        assert "combined axial and flexure 0.75 to 0.90" in t
        assert "AASHTO specifies 1.0" in t and "0.67 or 0.80" in t

    @pytest.mark.parametrize("key, phi", [
        ("lateral_individual", 0.67), ("lateral_group", 0.80),
        ("side_cohesionless_compression", 0.55), ("side_cohesionless_uplift", 0.45),
        ("side_cohesive_compression", 0.45), ("side_cohesive_uplift", 0.35),
        ("side_rock_compression", 0.50), ("side_rock_uplift", 0.40),
        ("side_igm_compression", 0.60), ("side_igm_uplift", 0.50),
        ("base_cohesionless", 0.50), ("base_cohesive", 0.40), ("base_rock", 0.50),
        ("load_test_compression", 0.70), ("load_test_uplift", 0.60),
        ("group_block_failure", 0.55), ("group_uplift", 0.45),
        ("structural_compression", 0.75), ("structural_shear", 0.90),
        ("service", 1.00), ("extreme_uplift", 0.80), ("extreme_lateral", 0.80),
        ("extreme_other", 1.00)])
    def test_python_table_8_4_matches_the_printed_table(self, key, phi):
        # Table 8-4, p. 8-14
        assert table_8_4_resistance_factor(key)["phi"] == phi

    def test_8_2_no_number_of_load_tests(self):
        t = _text("8.2")
        # p. 8-17 gives no number of load tests (the old text said 5-10)
        assert "5-10" not in t and "load tests required" not in t
        assert "Allen et al. (2005)" in t
        assert "Fitting should therefore be considered an interim approach" in t
        assert "Establish a target level of reliability" in t

    def test_8_1_opening_sentence(self):
        t = _text("8.1")
        assert ("The sequence of steps is not as important as verifying that "
                "important issues are not overlooked") in t
        assert "[p. 8-5] Block 1:" in t
