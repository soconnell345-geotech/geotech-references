"""Tests for geotech_references.ufc_collapse.tie_forces (Section 3-1).

Anchors are labeled by type:
  - WORKED EXAMPLE: reproduces a numeric result from Appendix D's printed
    7-story reinforced-concrete worked example.
  - PRINTED VALUE: reproduces a value stated directly in the printed text
    (e.g. an illustrative in-text example).
  - SELF-CONSISTENCY: checks internal logic (e.g. equation symmetry,
    threshold boundaries) rather than an external anchor.
"""

import pytest

from geotech_references.ufc_collapse.tie_forces import (
    minimum_bays_for_tie_force,
    floor_load_wf,
    effective_wf_for_nonuniform_load,
    internal_tie_force_framed,
    internal_tie_force_two_way_wall,
    one_way_wall_transverse_length,
    internal_tie_force_one_way_wall,
    max_tie_spacing,
    max_force_in_column_or_wall_strip,
    peripheral_tie_force_two_way,
    peripheral_tie_force_one_way,
    vertical_tie_force,
    perimeter_column_effective_wf,
    tie_strength_check,
    required_tie_area,
    splice_exclusion_zone,
)


class TestMinimumBays:
    def test_framed_four_bays_each_direction_ok(self):
        r = minimum_bays_for_tie_force(4, 4)
        assert r["meets_minimum_requirements"] is True

    def test_framed_three_bays_fails(self):
        r = minimum_bays_for_tie_force(3, 4)
        assert r["meets_minimum_requirements"] is False

    def test_one_way_wall_length_check(self):
        # SELF-CONSISTENCY: wall_length must be >= 4*hw
        r = minimum_bays_for_tie_force(4, one_way_wall=True, wall_length=48, clear_story_height=12)
        assert r["meets_minimum_requirements"] is True
        r2 = minimum_bays_for_tie_force(4, one_way_wall=True, wall_length=40, clear_story_height=12)
        assert r2["meets_minimum_requirements"] is False


class TestFloorLoadWf:
    def test_equation_3_2(self):
        # PRINTED VALUE: wF = 1.2D + 0.5L (Equation 3-2)
        r = floor_load_wf(dead_load=100, live_load=50)
        assert r["wf"] == pytest.approx(1.2 * 100 + 0.5 * 50)
        assert r["equation"] == "3-2"


class TestEffectiveWfNonuniform:
    def test_appendix_d_worked_example_averaging_criteria(self):
        # WORKED EXAMPLE (averaging-criteria half): Appendix D Table D-1
        # (printed p. 125). Office 207.8 psf over 16875 sf, storage/mech
        # 235.3 psf over 3375 sf, corridor 212.8 psf over 1125 sf. The
        # printed difference/area criteria (both satisfied) are reproduced
        # exactly.
        r = effective_wf_for_nonuniform_load([
            (207.8, 16875), (235.3, 3375), (212.8, 1125),
        ])
        assert r["averaging_permitted"] is True
        assert r["wf_difference"] == pytest.approx(27.5, abs=0.01)
        assert r["total_area"] == pytest.approx(21375)

    def test_appendix_d_area_weighted_average_arithmetic(self):
        # SELF-CONSISTENCY (not a worked-example anchor): applying the
        # printed formula to Appendix D's own printed inputs gives
        # 212.4 psf. The source document states 214.5 psf as its final
        # answer for this same calculation -- a ~1% arithmetic
        # inconsistency in the source's own worked example (independently
        # re-verified against the printed page; see this function's
        # docstring). Table D-2's downstream calculations carry wF=214.5
        # forward as a given value rather than re-deriving it, so this
        # discrepancy does not propagate into the Fp/As anchors below.
        r = effective_wf_for_nonuniform_load([
            (207.8, 16875), (235.3, 3375), (212.8, 1125),
        ])
        assert r["effective_wf"] == pytest.approx(212.4, abs=0.1)

    def test_area_threshold_forces_no_averaging(self):
        # SELF-CONSISTENCY: max-load area > 25% of total blocks averaging
        r = effective_wf_for_nonuniform_load([(100, 50), (200, 60)])
        assert r["averaging_permitted"] is False
        assert r["effective_wf"] is None


class TestInternalTieForce:
    def test_equation_3_3_framed(self):
        r = internal_tie_force_framed(wf=10, l1=20)
        assert r["fi"] == pytest.approx(3 * 10 * 20)
        assert r["equation"] == "3-3"

    def test_equation_3_4_two_way_wall_same_form(self):
        # SELF-CONSISTENCY: Equations 3-3 and 3-4 are numerically identical
        r3 = internal_tie_force_framed(wf=10, l1=20)
        r4 = internal_tie_force_two_way_wall(wf=10, l1=20)
        assert r3["fi"] == r4["fi"]
        assert r4["equation"] == "3-4"

    def test_one_way_wall_transverse_length_min_rule(self):
        # PRINTED VALUE: LT = min(5*hw, building_width)
        r = one_way_wall_transverse_length(clear_story_height=12, building_width=100)
        assert r["lt"] == pytest.approx(60)
        r2 = one_way_wall_transverse_length(clear_story_height=12, building_width=50)
        assert r2["lt"] == pytest.approx(50)

    def test_equation_3_5_one_way_wall(self):
        r = internal_tie_force_one_way_wall(wf=10, l1=52)
        assert r["fi"] == pytest.approx(3 * 10 * 52)
        assert r["equation"] == "3-5"


class TestTieSpacingAndStripCap:
    def test_max_tie_spacing(self):
        r = max_tie_spacing(20)
        assert r["max_spacing"] == pytest.approx(4.0)

    def test_printed_worked_example_in_text(self):
        # PRINTED VALUE: Section 3-1.4.1.1 in-text example -- Fi=10 k/ft,
        # LT=20 ft -> column strip width=4 ft, max total force=80 kip.
        r = max_force_in_column_or_wall_strip(fi_per_length=10, l_transverse_or_longitudinal=20)
        assert r["strip_width"] == pytest.approx(4.0)
        assert r["max_total_force"] == pytest.approx(80.0)


class TestPeripheralTieForce:
    def test_appendix_d_worked_example(self):
        # WORKED EXAMPLE: Appendix D (printed p. 126). wF=214.5 psf,
        # L1=37.5 ft, Lp=3 ft, WC=35,100 lb (printed as "35.1-kip", but
        # per the function's documented unit convention WC must be
        # supplied in lb, matching the lb that wF*L1*Lp naturally
        # computes in) -> Fp=250,088 lb, i.e. 250.1 kip when divided by
        # 1000, matching the printed answer.
        r = peripheral_tie_force_two_way(wf=214.5, l1=37.5, wc=35100, lp=3.0)
        assert r["fp"] / 1000 == pytest.approx(250.1, abs=0.2)
        assert r["equation"] == "3-6"

    def test_equation_3_7_one_way_wall(self):
        r = peripheral_tie_force_one_way(wf=100, l1=20, wc=10, ww=5, lp=3.3)
        expected = 6 * 100 * 20 * 3.3 + 3 * 10 + 3 * 5
        assert r["fp"] == pytest.approx(expected)
        assert r["equation"] == "3-7"

    def test_end_wall_wc_zero_note(self):
        # SELF-CONSISTENCY: end walls have WC=0 per the printed note
        r = peripheral_tie_force_one_way(wf=100, l1=20, wc=0, ww=5, lp=3.3)
        expected = 6 * 100 * 20 * 3.3 + 3 * 5
        assert r["fp"] == pytest.approx(expected)


class TestVerticalTieForce:
    def test_pv_equals_wf_times_area(self):
        r = vertical_tie_force(tributary_area=351.6, wf=314.3)
        assert r["pv"] == pytest.approx(351.6 * 314.3)

    def test_appendix_d_column_a1(self):
        # WORKED EXAMPLE: Appendix D Table D-2, column A1: area=351.6 sf,
        # wF=314.3 psf -> Pv=110.5 kip.
        r = vertical_tie_force(tributary_area=351.6, wf=314.3)
        assert r["pv"] / 1000 == pytest.approx(110.5, abs=0.2)


class TestPerimeterColumnEffectiveWf:
    def test_appendix_d_column_a1(self):
        # WORKED EXAMPLE: Appendix D (printed p. 125), column A1:
        # wF=214.5 psf + 1.2*(18.75+18.75 ft)(13 ft)(60 psf)/(18.75 ft)^2
        # = 314.3 psf.
        r = perimeter_column_effective_wf(
            wf_floor=214.5, cladding_dead_load_psf=60, clear_story_height=13,
            cladding_tributary_width=18.75 + 18.75, column_tributary_area=18.75 ** 2,
        )
        assert r["wf_effective"] == pytest.approx(314.3, abs=0.2)


class TestTieStrengthCheck:
    def test_equation_3_1_adequate(self):
        r = tie_strength_check(phi=0.75, rn=100, ru=50)
        assert r["adequate"] is True
        assert r["design_strength"] == pytest.approx(75)

    def test_equation_3_1_inadequate(self):
        r = tie_strength_check(phi=0.75, rn=10, ru=50)
        assert r["adequate"] is False


class TestRequiredTieArea:
    def test_appendix_d_worked_example(self):
        # WORKED EXAMPLE: Appendix D (printed p. 126). Ru=250.1 kip,
        # fy=60 ksi, Phi=0.75, overstrength=1.25 -> As=4.45 in2.
        r = required_tie_area(ru=250.1, fy=60, phi=0.75, overstrength_factor=1.25)
        assert r["as_required"] == pytest.approx(4.45, abs=0.02)

    def test_default_factors_match_appendix_d_basis(self):
        r = required_tie_area(ru=100, fy=60)
        assert r["phi"] == 0.75
        assert r["overstrength_factor"] == 1.25


class TestSpliceExclusionZone:
    def test_twenty_percent_rule(self):
        # PRINTED VALUE: splices excluded from the outer 20% of the bay
        # near each support (middle 60% permitted).
        r = splice_exclusion_zone(100)
        assert r["exclusion_distance"] == pytest.approx(20)
        assert r["permitted_zone_width"] == pytest.approx(60)
