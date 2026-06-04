"""Tests for geotech_references.ufc_pavement (UFC 3-250-01).

Pavement Design for Roads and Parking Areas (14 November 2016).
NOT for airfields (airfields = UFC 3-260-02).
"""

import pytest

from geotech_references.ufc_pavement.equations import (
    cbr_to_k_psi_per_in,
    stabilized_layer_thickness_mm,
    free_draining_layer_required,
)
from geotech_references.ufc_pavement.tables import (
    table_4_1_subgrade_category,
    table_6_1_subbase_permissible_values,
    table_7_1_base_design_cbr,
    table_7_2_min_thickness,
    table_9_1_equivalency_factor,
    table_10_1_k_subgrade,
    table_19_2_frost_classification,
    table_19_3_frost_support_index,
)


# ===================================================================
# EQUATION TESTS
# ===================================================================


class TestCBRtoK:
    """cbr_to_k_psi_per_in."""

    def test_cbr_10(self):
        r = cbr_to_k_psi_per_in(10.0)
        # k_psi = 26 * 10^0.7 ≈ 26 * 5.012 ≈ 130.3
        assert 120 < r["k_psi_in"] < 140

    def test_cbr_3(self):
        r = cbr_to_k_psi_per_in(3.0)
        assert r["k_psi_in"] > 0
        assert r["k_psi_in"] < 80

    def test_cbr_50(self):
        r = cbr_to_k_psi_per_in(50.0)
        assert r["k_psi_in"] > 300

    def test_increases_with_cbr(self):
        r1 = cbr_to_k_psi_per_in(5.0)
        r2 = cbr_to_k_psi_per_in(20.0)
        assert r2["k_psi_in"] > r1["k_psi_in"]

    def test_si_conversion_consistent(self):
        r = cbr_to_k_psi_per_in(10.0)
        assert abs(r["k_kPa_mm"] - r["k_psi_in"] * 0.271) < 0.5

    def test_below_range_raises(self):
        with pytest.raises(ValueError, match="cbr must be >= 2"):
            cbr_to_k_psi_per_in(1.0)

    def test_above_range_raises(self):
        with pytest.raises(ValueError, match="cbr must be <= 100"):
            cbr_to_k_psi_per_in(110.0)

    def test_formula(self):
        cbr = 15.0
        r = cbr_to_k_psi_per_in(cbr)
        expected = round(26.0 * cbr ** 0.7, 1)
        assert r["k_psi_in"] == expected


class TestStabilizedLayerThickness:
    """stabilized_layer_thickness_mm."""

    def test_basic(self):
        r = stabilized_layer_thickness_mm(300.0, 2.0)
        assert r["stabilized_thickness_mm"] == pytest.approx(150.0, abs=0.5)

    def test_unity_factor(self):
        r = stabilized_layer_thickness_mm(200.0, 1.0)
        assert r["stabilized_thickness_mm"] == pytest.approx(200.0, abs=0.5)

    def test_higher_factor_thinner(self):
        r1 = stabilized_layer_thickness_mm(300.0, 1.5)
        r2 = stabilized_layer_thickness_mm(300.0, 2.3)
        assert r2["stabilized_thickness_mm"] < r1["stabilized_thickness_mm"]

    def test_returns_factor(self):
        r = stabilized_layer_thickness_mm(200.0, 1.15)
        assert r["equivalency_factor"] == 1.15

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError, match="conventional_thickness_mm"):
            stabilized_layer_thickness_mm(0, 2.0)

    def test_zero_factor_raises(self):
        with pytest.raises(ValueError, match="equivalency_factor"):
            stabilized_layer_thickness_mm(200.0, 0)


class TestFreeDrainingLayer:
    """free_draining_layer_required."""

    def test_required_when_thin(self):
        # 0.09 * 1000 = 90 in threshold; bound thickness 50 in < 90
        r = free_draining_layer_required(50.0, 1000)
        assert r["required"] is True

    def test_not_required_when_thick(self):
        # 0.09 * 1000 = 90 in threshold; bound thickness 100 in > 90
        r = free_draining_layer_required(100.0, 1000)
        assert r["required"] is False

    def test_threshold_correct(self):
        r = free_draining_layer_required(10.0, 500)
        assert r["threshold_thickness_in"] == pytest.approx(45.0, abs=0.1)

    def test_min_layer_4_in(self):
        r = free_draining_layer_required(5.0, 200)
        assert r["min_free_draining_layer_in"] == 4.0

    def test_negative_bound_raises(self):
        with pytest.raises(ValueError, match="bound_layer_thickness_in"):
            free_draining_layer_required(-1.0, 500)

    def test_zero_dfi_raises(self):
        with pytest.raises(ValueError, match="design_freezing_index"):
            free_draining_layer_required(10.0, 0)


# ===================================================================
# TABLE TESTS
# ===================================================================


class TestSubgradeCategory:
    """table_4_1_subgrade_category."""

    def test_category_a_high_cbr(self):
        r = table_4_1_subgrade_category(20.0)
        assert r["category"] == "A"

    def test_category_a_boundary(self):
        r = table_4_1_subgrade_category(13.0)
        assert r["category"] == "A"

    def test_category_b(self):
        r = table_4_1_subgrade_category(10.0)
        assert r["category"] == "B"

    def test_category_c(self):
        r = table_4_1_subgrade_category(6.0)
        assert r["category"] == "C"

    def test_category_d_low_cbr(self):
        r = table_4_1_subgrade_category(2.0)
        assert r["category"] == "D"

    def test_category_d_boundary(self):
        r = table_4_1_subgrade_category(4.0)
        assert r["category"] == "D"

    def test_representative_cbr_present(self):
        r = table_4_1_subgrade_category(10.0)
        assert r["representative_cbr"] == 10

    def test_k_value_present(self):
        r = table_4_1_subgrade_category(15.0)
        assert r["representative_k_psi_in"] > 0

    def test_zero_cbr_raises(self):
        with pytest.raises(ValueError, match="cbr must be > 0"):
            table_4_1_subgrade_category(0.0)


class TestSubbasePermissibleValues:
    """table_6_1_subbase_permissible_values."""

    def test_cbr_50_subbase(self):
        r = table_6_1_subbase_permissible_values(50)
        assert r["design_cbr"] == 50
        assert r["layer_type"] == "Subbase"
        assert r["max_pct_passing_no200"] == 15
        assert r["max_plasticity_index"] == 5

    def test_cbr_30(self):
        r = table_6_1_subbase_permissible_values(30)
        assert r["max_pct_passing_no10"] == 100

    def test_cbr_20_select_material(self):
        r = table_6_1_subbase_permissible_values(20)
        assert r["layer_type"] == "Select material"
        assert r["max_liquid_limit"] == 35
        assert r["max_plasticity_index"] == 12

    def test_invalid_cbr_raises(self):
        with pytest.raises(ValueError, match="design_cbr must be one of"):
            table_6_1_subbase_permissible_values(60)


class TestBaseDesignCBR:
    """table_7_1_base_design_cbr."""

    def test_graded_crushed_aggregate_100(self):
        r = table_7_1_base_design_cbr("graded_crushed_aggregate")
        assert r["design_cbr"] == 100

    def test_limerock_80(self):
        r = table_7_1_base_design_cbr("limerock")
        assert r["design_cbr"] == 80

    def test_aggregate_80(self):
        r = table_7_1_base_design_cbr("aggregate")
        assert r["design_cbr"] == 80

    def test_bituminous_100(self):
        r = table_7_1_base_design_cbr("bituminous_binder_surface")
        assert r["design_cbr"] == 100

    def test_case_insensitive(self):
        r = table_7_1_base_design_cbr("Limerock")
        assert r["design_cbr"] == 80

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown material_type"):
            table_7_1_base_design_cbr("concrete")


class TestMinThickness:
    """table_7_2_min_thickness."""

    def test_low_esal_cbr100(self):
        r = table_7_2_min_thickness(10_000, 100)
        # ESAL ≤ 20,000, CBR100: ST surface, 4 in base, 4.5 in total
        assert r["base_in"] == 4
        assert r["total_in"] == 4.5

    def test_medium_esal_cbr80(self):
        r = table_7_2_min_thickness(100_000, 80)
        # 20,001-150,000 ESALs, CBR80: 2 in surface, 4 base, 6 total
        assert r["surface_in"] == 2
        assert r["total_in"] == 6

    def test_high_esal_cbr100(self):
        r = table_7_2_min_thickness(5_000_000, 100)
        # 2M-7M, CBR100: 3.5 in surface, 4 base, 7.5 total
        assert r["surface_in"] == 3.5
        assert r["total_in"] == 7.5

    def test_mm_conversion(self):
        r = table_7_2_min_thickness(200_000, 100)
        # surface_mm = surface_in * 25.4
        if isinstance(r["surface_in"], (int, float)):
            expected_mm = round(r["surface_in"] * 25.4, 0)
            assert r["surface_mm"] == expected_mm

    def test_cbr50_low_esal(self):
        r = table_7_2_min_thickness(100_000, 50)
        assert r["total_in"] > 0

    def test_cbr50_high_esal_raises(self):
        with pytest.raises(ValueError, match="restricted to ESAL"):
            table_7_2_min_thickness(1_000_000, 50)

    def test_invalid_cbr_raises(self):
        with pytest.raises(ValueError, match="base_cbr must be 50, 80, or 100"):
            table_7_2_min_thickness(100_000, 70)


class TestEquivalencyFactor:
    """table_9_1_equivalency_factor."""

    def test_asphalt_base(self):
        r = table_9_1_equivalency_factor("asphalt", "gm", "base")
        assert r["equivalency_factor"] == 1.15

    def test_asphalt_subbase(self):
        r = table_9_1_equivalency_factor("asphalt", "gm", "subbase")
        assert r["equivalency_factor"] == 2.30

    def test_cement_gw_base(self):
        r = table_9_1_equivalency_factor("cement", "GW", "base")
        assert r["equivalency_factor"] == 1.15

    def test_cement_gm_base(self):
        r = table_9_1_equivalency_factor("cement", "GM", "base")
        assert r["equivalency_factor"] == 1.00

    def test_cement_cl_subbase(self):
        r = table_9_1_equivalency_factor("cement", "CL", "subbase")
        assert r["equivalency_factor"] == 1.70

    def test_lime_cl_subbase(self):
        r = table_9_1_equivalency_factor("lime", "CL", "subbase")
        assert r["equivalency_factor"] == 1.00

    def test_lime_gm_subbase(self):
        r = table_9_1_equivalency_factor("lime", "GM", "subbase")
        assert r["equivalency_factor"] == 1.10

    def test_lime_cl_base_raises(self):
        with pytest.raises(ValueError, match="not used as a base"):
            table_9_1_equivalency_factor("lime", "CL", "base")

    def test_unbound_crushed_stone_base(self):
        r = table_9_1_equivalency_factor("unbound_crushed_stone", "all", "base")
        assert r["equivalency_factor"] == 1.00

    def test_unbound_aggregate_subbase(self):
        r = table_9_1_equivalency_factor("unbound_aggregate", "all", "subbase")
        assert r["equivalency_factor"] == 1.00

    def test_lcfa_ch_subbase(self):
        r = table_9_1_equivalency_factor("lime_cement_flyash", "CH", "subbase")
        assert r["equivalency_factor"] == 1.30

    def test_invalid_stabilizer_raises(self):
        with pytest.raises(ValueError, match="Unknown stabilizer_type"):
            table_9_1_equivalency_factor("epoxy", "CL", "base")


class TestKSubgrade:
    """table_10_1_k_subgrade."""

    def test_cl_10pct(self):
        r = table_10_1_k_subgrade("CL", 10)
        assert r["k_psi_in"] == 175

    def test_sm_5pct(self):
        r = table_10_1_k_subgrade("SM", 5)
        assert r["k_psi_in"] == 250

    def test_gw_2pct(self):
        r = table_10_1_k_subgrade("GW", 2)
        assert r["k_psi_in"] == 500

    def test_gw_6pct(self):
        r = table_10_1_k_subgrade("GW", 6)
        assert r["k_psi_in"] == 450

    def test_si_conversion(self):
        r = table_10_1_k_subgrade("CL", 15)
        assert abs(r["k_kPa_mm"] - r["k_psi_in"] * 0.271) < 0.5

    def test_case_insensitive(self):
        r = table_10_1_k_subgrade("cl", 10)
        assert r["k_psi_in"] == 175

    def test_high_moisture_unavailable_raises(self):
        with pytest.raises(ValueError, match="no data"):
            table_10_1_k_subgrade("GW", 25)

    def test_invalid_uscs_raises(self):
        with pytest.raises(ValueError, match="Unknown USCS group"):
            table_10_1_k_subgrade("XX", 10)


class TestFrostClassification:
    """table_19_2_frost_classification."""

    def test_ml_is_f4(self):
        r = table_19_2_frost_classification("ML", 50)
        assert r["frost_group"] == "F4"
        assert r["subgroup"] == "a"

    def test_cl_is_f3(self):
        r = table_19_2_frost_classification("CL", 80)
        assert r["frost_group"] == "F3"

    def test_sm_low_fines_s2(self):
        r = table_19_2_frost_classification("SM", 4.0)
        assert r["frost_group"] == "S2"

    def test_sm_mid_fines_f2(self):
        r = table_19_2_frost_classification("SM", 10.0)
        assert r["frost_group"] == "F2"

    def test_sm_high_fines_f4(self):
        r = table_19_2_frost_classification("SM", 25.0)
        assert r["frost_group"] == "F4"

    def test_gm_low_fines_f1(self):
        r = table_19_2_frost_classification("GM", 8.0)
        assert r["frost_group"] == "F1"

    def test_gm_med_fines_f2(self):
        r = table_19_2_frost_classification("GM", 15.0)
        assert r["frost_group"] == "F2"

    def test_gm_high_fines_f3(self):
        r = table_19_2_frost_classification("GM", 25.0)
        assert r["frost_group"] == "F3"

    def test_gw_nfs(self):
        r = table_19_2_frost_classification("GW", 1.0)
        assert r["frost_group"] == "NFS"

    def test_gw_s1(self):
        r = table_19_2_frost_classification("GW", 4.5)
        assert r["frost_group"] == "S1"

    def test_case_insensitive(self):
        r = table_19_2_frost_classification("ml", 50)
        assert r["frost_group"] == "F4"


class TestFrostSupportIndex:
    """table_19_3_frost_support_index."""

    def test_f1_returns_9(self):
        r = table_19_3_frost_support_index("F1")
        assert r["soil_support_index"] == 9.0

    def test_s1_returns_9(self):
        r = table_19_3_frost_support_index("S1")
        assert r["soil_support_index"] == 9.0

    def test_f2_returns_6_5(self):
        r = table_19_3_frost_support_index("F2")
        assert r["soil_support_index"] == 6.5

    def test_s2_returns_6_5(self):
        r = table_19_3_frost_support_index("S2")
        assert r["soil_support_index"] == 6.5

    def test_f3_returns_3_5(self):
        r = table_19_3_frost_support_index("F3")
        assert r["soil_support_index"] == 3.5

    def test_f4_returns_3_5(self):
        r = table_19_3_frost_support_index("F4")
        assert r["soil_support_index"] == 3.5

    def test_case_insensitive(self):
        r = table_19_3_frost_support_index("f1")
        assert r["soil_support_index"] == 9.0

    def test_nfs_raises(self):
        with pytest.raises(ValueError, match="NFS"):
            table_19_3_frost_support_index("NFS")

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown frost_group"):
            table_19_3_frost_support_index("F5")
