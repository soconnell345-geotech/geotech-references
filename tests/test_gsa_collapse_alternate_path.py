"""Tests for geotech_references.gsa_collapse.alternate_path (Section 3.2).

Anchors are PRINTED VALUE (Tables 4/5, printed equations) or SELF-
CONSISTENCY checks, PLUS cross-document CONSISTENCY checks against
geotech_references.ufc_collapse (Tables 4/5 and classify_action are
printed identically in both documents -- see module docstring).
"""

import math

import pytest

from geotech_references.gsa_collapse.alternate_path import (
    tie_forces_removed,
    enhanced_local_resistance_removed,
    lrfd_strength_check,
    classify_action,
    component_capacity_nonlinear,
    component_capacity_linear,
    removed_element_extent,
    removal_locations_fsl_3_4,
    removal_locations_fsl_5,
    adjacent_element_removal_trigger,
    disproportionate_collapse_allowance,
    lsp_story_limit,
    irregularity_check,
    lsp_applicable,
    dcr,
    deformation_controlled_load_lsp,
    gravity_load_away_from_removal,
    force_controlled_load_lsp,
    nonlinear_static_load,
    nonlinear_dynamic_load,
    table_4_load_increase_factor,
    table_5_dynamic_increase_factor,
    deformation_controlled_capacity_check,
    force_controlled_capacity_check,
    deformation_controlled_capacity_check_nonlinear,
)

from geotech_references.ufc_collapse.alternate_path import (
    table_3_4_load_increase_factor as ufc_table_3_4,
    table_3_5_dynamic_increase_factor as ufc_table_3_5,
    classify_action as ufc_classify_action,
)


class TestRemovedMethods:
    def test_tie_forces_removed(self):
        r = tie_forces_removed()
        assert r["removed"] is True
        assert r["removed_figures"] == [f"3.{i}" for i in range(1, 7)]

    def test_elr_removed(self):
        assert enhanced_local_resistance_removed()["removed"] is True


class TestLrfdStrengthCheck:
    def test_adequate(self):
        r = lrfd_strength_check(phi=0.9, rn=100, ru=80)
        assert r["design_strength"] == pytest.approx(90.0)
        assert r["adequate"] is True

    def test_inadequate(self):
        r = lrfd_strength_check(phi=0.9, rn=100, ru=95)
        assert r["adequate"] is False


class TestClassifyAction:
    @pytest.mark.parametrize("curve_type,e_over_g,is_primary,expected", [
        (1, 2.5, True, "deformation_controlled"),
        (2, 2.0, True, "deformation_controlled"),
        (1, 1.0, True, "force_controlled"),
        (2, 1.5, True, "force_controlled"),
        (3, 5.0, True, "force_controlled"),
        (1, 0.5, False, "deformation_controlled"),
        (2, 2.0, False, "deformation_controlled"),
        (2, 1.0, False, "force_controlled"),
        (3, 5.0, False, "force_controlled"),
    ])
    def test_classification(self, curve_type, e_over_g, is_primary, expected):
        r = classify_action(curve_type, e_over_g, is_primary)
        assert r["classification"] == expected

    def test_invalid_curve_type_raises(self):
        with pytest.raises(ValueError):
            classify_action(4, 2.0, True)

    @pytest.mark.parametrize("curve_type,e_over_g,is_primary", [
        (1, 2.5, True), (2, 2.0, True), (1, 1.0, True), (2, 1.5, True),
        (3, 5.0, True), (1, 0.5, False), (2, 2.0, False), (2, 1.0, False),
        (3, 5.0, False),
    ])
    def test_cross_check_vs_ufc_collapse(self, curve_type, e_over_g, is_primary):
        # CROSS-DOCUMENT CONSISTENCY: Section 3.2.5 is printed with
        # identical wording to UFC 4-023-03 Section 3-2.5.
        gsa = classify_action(curve_type, e_over_g, is_primary)
        ufc = ufc_classify_action(curve_type, e_over_g, is_primary)
        assert gsa["classification"] == ufc["classification"]


class TestComponentCapacityTables:
    def test_table_2_deformation_controlled(self):
        r = component_capacity_nonlinear(deformation_controlled=True)
        assert r["deformation_capacity_basis"] == "deformation_limit"
        assert r["strength_capacity_basis"] is None

    def test_table_2_force_controlled(self):
        r = component_capacity_nonlinear(deformation_controlled=False)
        assert r["strength_capacity_basis"] == "phi_qcl"

    def test_table_3_deformation_controlled(self):
        r = component_capacity_linear(deformation_controlled=True)
        assert r["material_strength_basis"] == "expected_strength_qce"
        assert r["strength_capacity_formula"] == "phi_m_qce"

    def test_table_3_force_controlled(self):
        r = component_capacity_linear(deformation_controlled=False)
        assert r["material_strength_basis"] == "lower_bound_strength_qcl"
        assert r["strength_capacity_formula"] == "phi_qcl"


class TestRemovalLocations:
    def test_removed_element_extent_passthrough(self):
        assert removed_element_extent(12.0)["removed_extent"] == 12.0

    def test_fsl_3_4_scope_mentions_first_floor_and_uncontrolled_access(self):
        r = removal_locations_fsl_3_4()
        assert "first floor above grade" in r["story_scope"]
        assert "uncontrolled public access" in r["story_scope"]
        assert len(r["controlled_public_access_criteria"]) == 2

    def test_fsl_5_scope_is_every_floor(self):
        r = removal_locations_fsl_5()
        assert "every floor level" in r["story_scope"]

    def test_adjacent_element_trigger_within_30_pct(self):
        # PRINTED VALUE: 30% of the largest bay dimension.
        r = adjacent_element_removal_trigger(distance=9.0, reference_dimension=30.0)
        assert r["threshold_distance"] == pytest.approx(9.0)
        assert r["triggers_simultaneous_removal"] is True

    def test_adjacent_element_trigger_outside_30_pct(self):
        r = adjacent_element_removal_trigger(distance=9.1, reference_dimension=30.0)
        assert r["triggers_simultaneous_removal"] is False


class TestDisproportionateCollapseAllowance:
    def test_exterior_15_pct(self):
        r = disproportionate_collapse_allowance(is_exterior_removal=True)
        assert r["allowable_extent_pct"] == 15
        assert r["applies_to"] == "existing buildings only"

    def test_interior_30_pct(self):
        r = disproportionate_collapse_allowance(is_exterior_removal=False)
        assert r["allowable_extent_pct"] == 30


class TestLspLimits:
    def test_story_limit_is_10(self):
        assert lsp_story_limit()["max_stories"] == 10

    def test_regular_structure_always_lsp_permitted(self):
        irr = irregularity_check()
        assert irr["is_irregular"] is False
        assert lsp_applicable(is_irregular=False)["lsp_permitted"] is True

    def test_irregular_structure_requires_max_dcr(self):
        with pytest.raises(ValueError):
            lsp_applicable(is_irregular=True)

    def test_irregular_structure_dcr_le_2_permits_lsp(self):
        r = lsp_applicable(is_irregular=True, max_dcr=2.0)
        assert r["lsp_permitted"] is True

    def test_irregular_structure_dcr_gt_2_blocks_lsp(self):
        r = lsp_applicable(is_irregular=True, max_dcr=2.01)
        assert r["lsp_permitted"] is False

    def test_irregularity_check_all_four_conditions(self):
        r = irregularity_check(has_discontinuity=True, has_nonorthogonal_lateral_elements=True)
        assert r["is_irregular"] is True
        assert r["triggered_conditions"] == [1, 4]

    def test_dcr_equation(self):
        r = dcr(q_udlim=150.0, q_ce=100.0)
        assert r["dcr"] == pytest.approx(1.5)


class TestLoadCombinations:
    def test_deformation_controlled_load_lsp(self):
        # Equation 3.3: GLD = Omega_LD*[1.2D + 0.5L]
        r = deformation_controlled_load_lsp(omega_ld=2.0, d=100.0, l=50.0)
        assert r["gld"] == pytest.approx(2.0 * (1.2 * 100 + 0.5 * 50))

    def test_gravity_load_away_from_removal(self):
        r = gravity_load_away_from_removal(d=100.0, l=50.0)
        assert r["g"] == pytest.approx(1.2 * 100 + 0.5 * 50)

    def test_force_controlled_load_lsp(self):
        r = force_controlled_load_lsp(omega_lf=2.0, d=100.0, l=50.0)
        assert r["glf"] == pytest.approx(2.0 * (1.2 * 100 + 0.5 * 50))

    def test_nonlinear_static_load(self):
        r = nonlinear_static_load(omega_n=1.5, d=100.0, s=20.0)
        assert r["gn"] == pytest.approx(1.5 * (1.2 * 100 + 0.2 * 20))

    def test_nonlinear_dynamic_load_no_increase_factor(self):
        # PRINTED VALUE: Equation 3.11 has NO Omega multiplier.
        r = nonlinear_dynamic_load(d=100.0, l=50.0)
        assert r["gnd"] == pytest.approx(1.2 * 100 + 0.5 * 50)


class TestTable4LoadIncreaseFactor:
    def test_steel_framed_matches_printed_formula(self):
        r = table_4_load_increase_factor("steel", "framed", m_lif=1.8)
        assert r["omega_ld"] == pytest.approx(0.9 * 1.8 + 1.1)
        assert r["omega_lf"] == 2.0

    def test_rc_framed(self):
        r = table_4_load_increase_factor("reinforced_concrete", "framed", m_lif=10.0)
        assert r["omega_ld"] == pytest.approx(1.2 * 10.0 + 0.80)

    def test_load_bearing_wall_materials(self):
        for material in ("reinforced_concrete", "masonry", "wood", "cold_formed_steel"):
            r = table_4_load_increase_factor(material, "load_bearing_wall", m_lif=3.0)
            assert r["omega_ld"] == pytest.approx(6.0)
            assert r["omega_lf"] == 2.0

    def test_invalid_combination_raises(self):
        with pytest.raises(ValueError):
            table_4_load_increase_factor("wood", "framed", m_lif=2.0)

    @pytest.mark.parametrize("material,structure_type,m_lif", [
        ("steel", "framed", 1.8), ("steel", "framed", 1.79),
        ("reinforced_concrete", "framed", 10.74),
        ("reinforced_concrete", "load_bearing_wall", 4.0),
        ("masonry", "load_bearing_wall", 4.0),
        ("wood", "load_bearing_wall", 4.0),
        ("cold_formed_steel", "load_bearing_wall", 4.0),
    ])
    def test_cross_check_vs_ufc_collapse_table_3_4(self, material, structure_type, m_lif):
        # CROSS-DOCUMENT CONSISTENCY: Table 4 is printed IDENTICALLY to
        # UFC 4-023-03 Table 3-4.
        gsa = table_4_load_increase_factor(material, structure_type, m_lif)
        ufc = ufc_table_3_4(material, structure_type, m_lif)
        assert gsa["omega_ld"] == pytest.approx(ufc["omega_ld"])
        assert gsa["omega_lf"] == pytest.approx(ufc["omega_lf"])


class TestTable5DynamicIncreaseFactor:
    def test_steel_framed_requires_rotations(self):
        with pytest.raises(ValueError):
            table_5_dynamic_increase_factor("steel", "framed")

    def test_steel_framed_formula(self):
        r = table_5_dynamic_increase_factor("steel", "framed", theta_pra=0.04, theta_y=0.02)
        ratio = 0.04 / 0.02
        assert r["omega_n"] == pytest.approx(1.08 + 0.76 / (ratio + 0.83))

    def test_rc_framed_formula(self):
        r = table_5_dynamic_increase_factor("reinforced_concrete", "framed", theta_pra=0.03, theta_y=0.01)
        ratio = 0.03 / 0.01
        assert r["omega_n"] == pytest.approx(1.04 + 0.45 / (ratio + 0.48))

    def test_load_bearing_wall_fixed_at_2(self):
        for material in ("reinforced_concrete", "masonry", "wood", "cold_formed_steel"):
            r = table_5_dynamic_increase_factor(material, "load_bearing_wall")
            assert r["omega_n"] == pytest.approx(2.0)
            assert r["rotation_ratio"] is None

    @pytest.mark.parametrize("material,structure_type,theta_pra,theta_y", [
        ("steel", "framed", 0.04, 0.02), ("steel", "framed", 0.09, 0.03),
        ("reinforced_concrete", "framed", 0.03, 0.01),
    ])
    def test_cross_check_vs_ufc_collapse_table_3_5_framed(self, material, structure_type, theta_pra, theta_y):
        # CROSS-DOCUMENT CONSISTENCY: Table 5 is printed IDENTICALLY to
        # UFC 4-023-03 Table 3-5.
        gsa = table_5_dynamic_increase_factor(material, structure_type, theta_pra, theta_y)
        ufc = ufc_table_3_5(material, structure_type, theta_pra, theta_y)
        assert gsa["omega_n"] == pytest.approx(ufc["omega_n"])

    @pytest.mark.parametrize("material", ["reinforced_concrete", "masonry", "wood", "cold_formed_steel"])
    def test_cross_check_vs_ufc_collapse_table_3_5_wall(self, material):
        gsa = table_5_dynamic_increase_factor(material, "load_bearing_wall")
        ufc = ufc_table_3_5(material, "load_bearing_wall")
        assert gsa["omega_n"] == pytest.approx(ufc["omega_n"])


class TestAcceptanceCriteria:
    def test_deformation_controlled_capacity_check_adequate(self):
        r = deformation_controlled_capacity_check(phi=0.9, m=10.74, q_ce=100.0, q_ud=900.0)
        assert r["capacity"] == pytest.approx(0.9 * 10.74 * 100.0)
        assert r["adequate"] is True

    def test_force_controlled_capacity_check(self):
        r = force_controlled_capacity_check(phi=0.75, q_cl=200.0, q_uf=140.0)
        assert r["capacity"] == pytest.approx(150.0)
        assert r["adequate"] is True

    def test_force_controlled_capacity_check_inadequate(self):
        # PRINTED WORKED-EXAMPLE VALUE (with a flagged source-document
        # arithmetic error): Appendix D's pan-joist shear check (printed
        # p. D47) computes VCL=Av*fy*d/s=42 kips two lines above, then
        # states "Phi*QCL >= QUF: 0.75(80 kips) = 42 kips <= 57.6 kips,
        # NG" -- the printed "80 kips" does not appear anywhere else in
        # the derivation and 0.75*80=60, NOT 42, so the printed
        # intermediate equation is internally inconsistent (page-verified
        # against the rendered PDF; NOT silently corrected here). The
        # CORRECT arithmetic using the document's own VCL=42 kips value
        # reproduces the document's stated "NG" conclusion exactly:
        # Phi*QCL = 0.75*42 = 31.5 kips < QUF = 57.6 kips.
        r = force_controlled_capacity_check(phi=0.75, q_cl=42.0, q_uf=57.6)
        assert r["capacity"] == pytest.approx(31.5)
        assert r["adequate"] is False

    def test_deformation_controlled_capacity_check_nonlinear(self):
        r = deformation_controlled_capacity_check_nonlinear(
            expected_deformation_capacity=0.05, demand=0.03)
        assert r["adequate"] is True
        r2 = deformation_controlled_capacity_check_nonlinear(
            expected_deformation_capacity=0.02, demand=0.03)
        assert r2["adequate"] is False
