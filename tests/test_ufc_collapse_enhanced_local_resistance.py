"""Tests for geotech_references.ufc_collapse.enhanced_local_resistance
(Section 3-3).

Anchors are labeled by type:
  - WORKED EXAMPLE: reproduces a numeric result from Appendix D's printed
    ELR worked example (D-3.3, printed pp. 129-131).
  - PRINTED VALUE: reproduces a value stated directly in the printed text.
  - SELF-CONSISTENCY: checks internal logic rather than an external anchor.
"""

import pytest

from geotech_references.ufc_collapse.enhanced_local_resistance import (
    elr_lrfd_check,
    shear_demand_pinned_fixed_column,
    rc4_column_flexural_demand,
    rc4_wall_flexural_demand,
    rebound_reaction_force,
    elr_location_requirement,
)


class TestElrLrfdCheck:
    def test_equation_3_20_phi_is_one(self):
        r = elr_lrfd_check(rn=100, ru=90)
        assert r["design_strength"] == 100
        assert r["adequate"] is True

    def test_inadequate(self):
        r = elr_lrfd_check(rn=50, ru=90)
        assert r["adequate"] is False


class TestShearDemandPinnedFixedColumn:
    def test_appendix_d_worked_example(self):
        # WORKED EXAMPLE: Appendix D (printed p. 130). Mn=783 ft-kip,
        # L=16 ft -> Vu = 7.5*783/16 = 367.03 kip (printed as 367 kip).
        r = shear_demand_pinned_fixed_column(mn=783, l=16)
        assert r["vu"] == pytest.approx(367, abs=0.1)
        assert r["equation"] == "D-1"

    def test_formula_form(self):
        r = shear_demand_pinned_fixed_column(mn=100, l=10)
        assert r["vu"] == pytest.approx(75.0)


class TestRc4FlexuralDemand:
    def test_column_baseline_governs(self):
        # baseline*2.0 = 200 > current design 150 -> condition 1 governs
        r = rc4_column_flexural_demand(baseline_gravity_only_mn=100, current_design_mn=150)
        assert r["flexural_demand"] == pytest.approx(200)
        assert r["governing_condition"] == 1

    def test_column_current_design_governs(self):
        r = rc4_column_flexural_demand(baseline_gravity_only_mn=50, current_design_mn=150)
        assert r["flexural_demand"] == pytest.approx(150)
        assert r["governing_condition"] == 2

    def test_wall_multiplier_is_1_5(self):
        # PRINTED VALUE: wall multiplier is 1.5 (vs. 2.0 for columns)
        r = rc4_wall_flexural_demand(baseline_gravity_only_mn=100, current_design_mn=120)
        assert r["baseline_x1_5"] == pytest.approx(150)
        assert r["flexural_demand"] == pytest.approx(150)
        assert r["governing_condition"] == 1


class TestReboundReactionForce:
    def test_fifty_percent_rule(self):
        r = rebound_reaction_force(inbound_reaction_force=200)
        assert r["rebound_force"] == pytest.approx(100)
        assert r["factor"] == 0.5


class TestElrLocationRequirement:
    def test_rc_ii_corner_and_penultimate_only(self):
        r = elr_location_requirement("II")
        assert "corner" in r["location"].lower()
        assert "penultimate" in r["location"].lower()
        assert "all perimeter" not in r["location"].lower()

    def test_rc_iii_and_iv_all_perimeter(self):
        # SELF-CONSISTENCY: RC III and RC IV both require ALL perimeter
        # first-story elements (unlike RC II Option 1's corner-only scope)
        r3 = elr_location_requirement("III")
        r4 = elr_location_requirement("IV")
        assert "all perimeter" in r3["location"].lower()
        assert "all perimeter" in r4["location"].lower()

    def test_one_way_wall_full_length(self):
        r = elr_location_requirement("II", one_way_wall=True)
        assert "entire length" in r["location"].lower()

    def test_invalid_risk_category_raises(self):
        with pytest.raises(ValueError):
            elr_location_requirement("I")
