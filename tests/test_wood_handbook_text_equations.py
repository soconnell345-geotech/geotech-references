"""Wood Handbook FPL-GTR-282 (2021) stored chapter text against the print.

Each test pins a printed equation, limit or statement the stored text once got
wrong or left out (review of 2026-11-10; app backlog REF-83). Pages are the
printed page numbers; the PDF page is the printed page plus 94 in chapter 4,
116 in chapter 5, 204 in chapter 8 and 232 in chapter 9.
"""

import json

from geotech_references._retrieval import load_chapter


def _section(chapter, section_id):
    for s in load_chapter("wood_handbook", chapter)["sections"]:
        if s["section_id"] == section_id:
            return s
    raise KeyError(section_id)


def _all_text(section):
    return json.dumps(section, ensure_ascii=False)


def _chapter_text(chapter):
    return json.dumps(load_chapter("wood_handbook", chapter), ensure_ascii=False)


class TestChapter8DowelBearing:
    def test_nail_equation_is_not_given_for_all_dowel_fasteners(self):
        # p. 8-7: "The yield model theory is applicable to all types of dowel
        # fasteners"; Eq. 8-3 Fe = 114.5 G^1.84 is the nail equation. The old
        # key point said Eq 8-3 fed the model "for ALL dowel-type fasteners".
        s = _section(8, "8-1")
        assert "Fe = 114.5 G^1.84 (metric) (Eq. 8-3a)" in s["body"]
        assert "Fe = 16,600 G^1.84 (inch-pound) (Eq. 8-3b)" in s["body"]
        assert "applicable to all types of dowel fasteners" in s["body"]
        assert "for ALL dowel-type fasteners" not in _all_text(s)

    def test_screws_use_the_nail_equation(self):
        # p. 8-12: "based on the same specific gravity equation used to
        # establish values for nails (Eq. (8-3))".
        s = _section(8, "8-3")
        assert "same specific gravity equation used to establish values for nails (Eq. (8-3))" in s["body"]

    def test_bolts_have_their_own_dowel_bearing_equations(self):
        # p. 8-19: parallel Fe = 77.2 G (8-17a), 11,200 G (8-17b); perpendicular
        # Fe = 212.0 G^1.45 D^-0.5 (8-18a), 6,100 G^1.45 D^-0.5 (8-18b).
        s = _section(8, "8-5")
        assert "Fe = 77.2 G (metric) (Eq. 8-17a)" in s["body"]
        assert "Fe = 11,200 G (inch-pound) (Eq. 8-17b)" in s["body"]
        assert "Fe = 212.0 G^1.45 D^-0.5 (metric) (Eq. 8-18a)" in s["body"]
        assert "Fe = 6,100 G^1.45 D^-0.5 (inch-pound) (Eq. 8-18b)" in s["body"]
        assert set(s["equations"]) >= {"8-17a", "8-17b", "8-18a", "8-18b"}

    def test_lag_screws_use_the_bolt_equations(self):
        # p. 8-14: "the same parallel- and perpendicular-to-grain specific
        # gravity equations used to establish values for bolts".
        s = _section(8, "8-4")
        assert "same parallel- and perpendicular-to-grain specific gravity equations used to establish values for bolts" in s["body"]

    def test_table_8_5_mode_iv_coefficients(self):
        # p. 8-7 Table 8-5: mode IV is D^2 sqrt(2 Fem Fyb/(3(1+Re))) for nails
        # and 1.75 for screws; the print gives no reason for the difference.
        s = _section(8, "8-3")
        assert "the handbook gives no reason for the difference" in s["body"]
        assert "reflecting" not in _all_text(s)


class TestChapter8Withdrawal:
    def test_nail_withdrawal_equations(self):
        # p. 8-2: p = 54.12 G^(5/2) D L (8-1a), 7,850 (8-1b); side grain of
        # seasoned wood or unseasoned wood that remains wet.
        s = _section(8, "8-1")
        assert "p = 54.12 G^(5/2) D L (metric) (Eq. 8-1a)" in s["body"]
        assert "p = 7,850 G^(5/2) D L (inch-pound) (Eq. 8-1b)" in s["body"]
        assert "seasoned wood or unseasoned wood that remains wet" in s["body"]

    def test_threaded_nail_conditions(self):
        # p. 8-4: crest difference > 0.2 mm, thread spacing 1.27 to 1.96 mm;
        # p = 77.57 G^2 D L (8-2a); valid only for the threaded portion.
        s = _section(8, "8-1")
        assert "greater than 0.2 mm (0.008 in.)" in s["body"]
        assert "between 1.27 mm (0.05 in.) and 1.96 mm (0.077 in.)" in s["body"]
        assert "p = 77.57 G^2 D L (metric) (Eq. 8-2a)" in s["body"]
        assert "valid only for the threaded portion" in s["body"]

    def test_pre_1991_nail_lateral_keeps_the_printed_number(self):
        # p. 8-6: p = K D^(3/2), printed as "(8-2)", the same number as the
        # threaded-nail withdrawal equation.
        s = _section(8, "8-1")
        assert "p = K D^(3/2) (printed as Eq. 8-2" in s["body"]
        assert "fastenings.py" not in _all_text(s)

    def test_moisture_change_withdrawal_warning(self):
        # p. 8-3: may be as low as 25% of the values soon after driving;
        # regained resistance "should not be relied on in the design".
        s = _section(8, "8-1")
        assert "may be as low as 25% of the values for nails tested soon after driving" in s["body"]
        assert "should not be relied on in the design of a nailed joint" in s["body"]

    def test_screw_withdrawal_limits(self):
        # p. 8-10 to 8-11: p = 108.25 G^2 D L (8-10a); lead holes about 70% of
        # root diameter (softwoods), 90% (hardwoods); Table 8-8 sizes.
        s = _section(8, "8-3")
        assert "p = 108.25 G^2 D L (metric) (Eq. 8-10a)" in s["body"]
        assert "about 70% of the root diameter of the threads in softwoods, and about 90% in hardwoods" in s["body"]
        assert "actual values are likely to be less than the equation values" in s["body"]
        assert "never be started or driven with a hammer" in s["body"]

    def test_spikes_staples_drift_bolts(self):
        # p. 8-9 to 8-10: spike penetration less two-thirds of the point;
        # staples without verification tests; p = 45.51 G^2 D L (8-9a).
        s = _section(8, "8-2")
        assert "minus two-thirds the length of the point" in s["body"]
        assert "no verification tests have been done" in s["body"]
        assert "p = 45.51 G^2 D L (metric) (Eq. 8-9a)" in s["body"]
        assert "not separately digitized" not in _all_text(s)

    def test_lag_screw_withdrawal(self):
        # p. 8-12: p = 125.4 G^(3/2) D^(3/4) L (8-14a), 8,100 (8-14b).
        s = _section(8, "8-4")
        assert "p = 125.4 G^(3/2) D^(3/4) L (metric) (Eq. 8-14a)" in s["body"]
        assert "p = 8,100 G^(3/2) D^(3/4) L (inch-pound) (Eq. 8-14b)" in s["body"]


class TestChapter8TestedHardware:
    def test_metal_plate_design_load(self):
        # p. 8-25: at least five specimens; 0.38 mm or 0.76 mm slip / 1.6;
        # average ultimate / 3.0.
        s = _section(8, "8-7")
        assert "at least five specimens at 0.38-mm (0.015-in.) slip" in s["body"]
        assert "is divided by 1.6" in s["body"]
        assert "average ultimate load of at least five specimens is divided by 3.0" in s["body"]
        assert "ICC-ES" not in _all_text(s)

    def test_joist_hanger_design_load(self):
        # p. 8-26: ASTM D7147; 3.2 mm deformation, at least six specimens;
        # ultimate / 3.0, or least ultimate / 3.0 for fewer than six.
        s = _section(8, "8-7")
        assert "ASTM D7147" in s["body"]
        assert "3.2-mm (0.125-in.) deformation" in s["body"]
        assert "least ultimate load for lower than six replicates divided by 3.0" in s["body"]

    def test_head_embedment_should_be_considered(self):
        # p. 8-26: annularly threaded nails in withdrawal: head embedment or
        # pull-through "should be considered in design".
        s = _section(8, "8-8")
        assert "pull-through can be a limiting condition and should be considered in design" in s["body"]


class TestChapter9:
    def test_9_41_edgewise_bending_is_not_the_compression_form(self):
        # p. 9-17: F''b1 = (1.44 E/le)(d2/d1) (Eq. 9-41); the old key point
        # said Eq 9-39 to 9-41 all used 0.822 E/(le/d)^2.
        s = _section(9, "9-10")
        assert "F''b1 = (1.44 E/le)(d2/d1) (Eq. 9-41)" in s["body"]
        assert "F''c1 = 0.822 E/(le1/d1)^2 (Eq. 9-39)" in s["body"]
        assert "same Euler-form" not in _all_text(s)

    def test_9_37_and_9_38_as_printed(self):
        # p. 9-17: theta_c1 = 1 - (fc/F''c1 + s/scr); theta_c2 = 1 -
        # [fc/F''c2 + (fb1 + 6(e1/d1) fc)/F''b1].
        s = _section(9, "9-10")
        assert "theta_c1 = 1 - (fc/F''c1 + s/scr) (Eq. 9-37)" in s["body"]
        assert "theta_c2 = 1 - [fc/F''c2 + (fb1 + 6(e1/d1) fc)/F''b1] (Eq. 9-38)" in s["body"]

    def test_9_24_printed_form_with_note(self):
        # p. 9-13: fs = T/(beta h b^2) as printed; Figure 9-15 beta 3 to 4.8.
        s = _section(9, "9-7")
        assert "fs = T/(beta h b^2) (Eq. 9-24)" in s["body"]
        assert "Print note" in s["body"]
        assert "judgment call" not in _all_text(s).lower()

    def test_9_32_ponding_spacing_with_note(self):
        # p. 9-15: scr = m pi^4 E I/(rho L^4); m = 1 simple, 16/3 fixed; the
        # beam spacing must be less than scr.
        s = _section(9, "9-9")
        assert "scr = m pi^4 E I/(rho L^4) (Eq. 9-32)" in s["body"]
        assert "the beam spacing must be less than scr" in s["body"]
        assert "documented skip" not in _all_text(s)

    def test_9_5_tapered_shear_deflection(self):
        # p. 9-4: Delta_s = 3WL/(20 G b h0) uniform, 3PL/(10 G b h0) midspan.
        s = _section(9, "9-1")
        assert "Delta_s = 3 W L/(20 G b h0)" in s["body"]
        assert "3 P L/(10 G b h0)" in s["body"]

    def test_9_18_example_without_module_notes(self):
        # p. 9-10: R1 = 10,000 [56/(2,160(1 + 6))]^(1/18) = 7,330 lbf in^-2.
        s = _section(9, "9-5")
        assert "= 7,330 lbf in^-2" in s["body"]
        assert "validation anchor" not in _all_text(s)

    def test_9_7_compression_must_be_less_than_pcr(self):
        # p. 9-5: "If P is compression, it must be less than Pcr to avoid collapse."
        s = _section(9, "9-2")
        assert "If P is compression, it must be less than Pcr to avoid collapse." in s["body"]
        assert "share the same" not in _all_text(s)


class TestChapters4And5:
    def test_4_4_table_sources(self):
        # p. 4-7: Table 4-3, numerous domestic species, ASTM D143; p. 4-9 to
        # 4-10: Table 4-4 from world literature, may not be a true average.
        s = _section(4, "4-4")
        assert "numerous domestic species by methods described in ASTM D143" in s["body"]
        assert "collected from the world literature for selected imported species" in s["body"]
        assert "may not represent a true species average" in s["body"]

    def test_4_8_friction_varies_little_with_species(self):
        # p. 4-19: "They vary little with species except for woods that
        # contain abundant oily or waxy extractives".
        s = _section(4, "4-8")
        assert "vary little with species except for woods that contain abundant oily or waxy extractives" in s["body"]

    def test_5_10_decay_and_insects(self):
        # p. 5-44: 5% to 10% weight loss, properties reduced 20% to 80%;
        # discard pieces with decay; eliminate pieces with insect holes.
        s = _section(5, "5-10")
        assert "When weight loss reaches 5% to 10%, mechanical properties are reduced from 20% to 80%." in s["body"]
        assert "discard every piece that contains even a small amount of decay" in s["body"]
        assert "eliminate pieces containing insect holes" in s["body"]

    def test_5_2_table_5_6_is_variation_not_shear_moduli(self):
        # p. 5-2 to 5-3: shear moduli are ratios in Table 5-1; Table 5-6 holds
        # coefficients of variation.
        s = _section(5, "5-2")
        assert "expressed as ratios with EL, are given in Table 5-1" in s["body"]
        assert "Table 5-6 (shear moduli)" not in _all_text(s)

    def test_no_module_notes_left(self):
        for ch in (4, 5, 8, 9):
            text = _chapter_text(ch)
            for phrase in ("this module", "not digitized", "Madison curve", "Hailwood"):
                assert phrase not in text, (ch, phrase)
