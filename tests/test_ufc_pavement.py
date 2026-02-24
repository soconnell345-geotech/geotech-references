"""Tests for geotech_references.ufc_pavement (UFC 3-260-02)."""

import math
import pytest

from geotech_references.ufc_pavement.equations import (
    cbr_to_subgrade_modulus_MPa_per_m,
    flexible_pavement_thickness_mm,
    equivalent_single_wheel_load_kN,
    rigid_pavement_thickness_mm,
)
from geotech_references.ufc_pavement.tables import (
    table_frost_susceptibility,
    table_frost_design_reduction,
    table_aircraft_classification,
    table_pavement_layer_coefficients,
    table_subgrade_class,
)


# ===================================================================
# EQUATION TESTS
# ===================================================================


class TestCBRtoSubgradeModulus:
    """cbr_to_subgrade_modulus_MPa_per_m."""

    def test_cbr_8(self):
        k = cbr_to_subgrade_modulus_MPa_per_m(8.0)
        # k_pci = 26 * 8^0.7 ≈ 26 * 4.595 ≈ 119.5
        # k_MPa_m = 119.5 * 0.2714 ≈ 32.4
        assert 25 < k < 40

    def test_cbr_3(self):
        k = cbr_to_subgrade_modulus_MPa_per_m(3.0)
        assert k > 0
        assert k < 25

    def test_cbr_50(self):
        k = cbr_to_subgrade_modulus_MPa_per_m(50.0)
        assert k > 100

    def test_increases_with_cbr(self):
        k1 = cbr_to_subgrade_modulus_MPa_per_m(5.0)
        k2 = cbr_to_subgrade_modulus_MPa_per_m(20.0)
        assert k2 > k1

    def test_below_range_raises(self):
        with pytest.raises(ValueError, match="cbr must be >= 2"):
            cbr_to_subgrade_modulus_MPa_per_m(1.0)

    def test_above_range_raises(self):
        with pytest.raises(ValueError, match="cbr must be <= 80"):
            cbr_to_subgrade_modulus_MPa_per_m(90.0)

    def test_formula(self):
        cbr = 10.0
        k = cbr_to_subgrade_modulus_MPa_per_m(cbr)
        expected = round(26.0 * cbr ** 0.7 * 0.2714, 1)
        assert k == expected


class TestFlexiblePavementThickness:
    """flexible_pavement_thickness_mm — CBR method."""

    def test_basic_calculation(self):
        r = flexible_pavement_thickness_mm(5.0, 100.0, 700.0)
        assert r["total_thickness_mm"] > 0

    def test_lower_cbr_thicker(self):
        r1 = flexible_pavement_thickness_mm(10.0, 100.0, 700.0)
        r2 = flexible_pavement_thickness_mm(3.0, 100.0, 700.0)
        assert r2["total_thickness_mm"] > r1["total_thickness_mm"]

    def test_higher_load_thicker(self):
        r1 = flexible_pavement_thickness_mm(5.0, 50.0, 700.0)
        r2 = flexible_pavement_thickness_mm(5.0, 200.0, 700.0)
        assert r2["total_thickness_mm"] > r1["total_thickness_mm"]

    def test_contact_radius_returned(self):
        r = flexible_pavement_thickness_mm(5.0, 100.0, 700.0)
        assert r["contact_radius_mm"] > 0

    def test_coverage_factor(self):
        r1 = flexible_pavement_thickness_mm(5.0, 100.0, 700.0, coverages=100)
        r2 = flexible_pavement_thickness_mm(5.0, 100.0, 700.0, coverages=50000)
        assert r2["total_thickness_mm"] >= r1["total_thickness_mm"]

    def test_cbr_below_range_raises(self):
        with pytest.raises(ValueError, match="cbr must be >= 2"):
            flexible_pavement_thickness_mm(1.0, 100.0, 700.0)

    def test_cbr_above_range_raises(self):
        with pytest.raises(ValueError, match="cbr must be <= 50"):
            flexible_pavement_thickness_mm(60.0, 100.0, 700.0)

    def test_zero_load_raises(self):
        with pytest.raises(ValueError, match="wheel_load_kN"):
            flexible_pavement_thickness_mm(5.0, 0, 700.0)

    def test_zero_pressure_raises(self):
        with pytest.raises(ValueError, match="tire_pressure"):
            flexible_pavement_thickness_mm(5.0, 100.0, 0)

    def test_strong_subgrade_minimum(self):
        """High CBR and low load should still give minimum thickness."""
        r = flexible_pavement_thickness_mm(40.0, 20.0, 200.0)
        assert r["total_thickness_mm"] >= 100


class TestEquivalentSingleWheelLoad:
    """equivalent_single_wheel_load_kN — ESWL."""

    def test_single_wheel(self):
        eswl = equivalent_single_wheel_load_kN(100.0, 1, 500.0, 300.0)
        assert eswl == 100.0

    def test_dual_full_overlap(self):
        eswl = equivalent_single_wheel_load_kN(100.0, 2, 500.0, 1000.0)
        # At depth >= S, full overlap: ESWL = n*P
        assert eswl == pytest.approx(200.0, abs=0.1)

    def test_dual_no_overlap(self):
        eswl = equivalent_single_wheel_load_kN(100.0, 2, 500.0, 0.0)
        # At z=0: ESWL = P
        assert eswl == pytest.approx(100.0, abs=0.1)

    def test_partial_overlap(self):
        eswl = equivalent_single_wheel_load_kN(100.0, 2, 500.0, 250.0)
        assert 100.0 < eswl < 200.0

    def test_four_wheels(self):
        eswl = equivalent_single_wheel_load_kN(50.0, 4, 500.0, 1000.0)
        assert eswl == pytest.approx(200.0, abs=0.1)

    def test_zero_load_raises(self):
        with pytest.raises(ValueError, match="wheel_load_kN"):
            equivalent_single_wheel_load_kN(0, 2, 500.0, 300.0)

    def test_zero_spacing_raises(self):
        with pytest.raises(ValueError, match="wheel_spacing_mm"):
            equivalent_single_wheel_load_kN(100.0, 2, 0, 300.0)

    def test_negative_depth_raises(self):
        with pytest.raises(ValueError, match="depth_mm"):
            equivalent_single_wheel_load_kN(100.0, 2, 500.0, -1)


class TestRigidPavementThickness:
    """rigid_pavement_thickness_mm — Westergaard."""

    def test_basic(self):
        r = rigid_pavement_thickness_mm(30.0, 100.0, 4.0)
        assert r["thickness_mm"] > 0

    def test_higher_load_thicker(self):
        r1 = rigid_pavement_thickness_mm(30.0, 50.0, 4.0)
        r2 = rigid_pavement_thickness_mm(30.0, 200.0, 4.0)
        assert r2["thickness_mm"] > r1["thickness_mm"]

    def test_stronger_concrete_thinner(self):
        r1 = rigid_pavement_thickness_mm(30.0, 100.0, 3.5)
        r2 = rigid_pavement_thickness_mm(30.0, 100.0, 5.0)
        assert r2["thickness_mm"] < r1["thickness_mm"]

    def test_radius_of_stiffness(self):
        r = rigid_pavement_thickness_mm(30.0, 100.0, 4.0)
        assert r["radius_of_relative_stiffness_mm"] > 0

    def test_zero_k_raises(self):
        with pytest.raises(ValueError, match="k_subgrade"):
            rigid_pavement_thickness_mm(0, 100.0, 4.0)

    def test_zero_load_raises(self):
        with pytest.raises(ValueError, match="wheel_load_kN"):
            rigid_pavement_thickness_mm(30.0, 0, 4.0)

    def test_zero_strength_raises(self):
        with pytest.raises(ValueError, match="concrete_flexural"):
            rigid_pavement_thickness_mm(30.0, 100.0, 0)

    def test_safety_factor_lt_1_raises(self):
        with pytest.raises(ValueError, match="safety_factor"):
            rigid_pavement_thickness_mm(30.0, 100.0, 4.0, safety_factor=0.5)


# ===================================================================
# TABLE TESTS
# ===================================================================


class TestFrostSusceptibility:
    """table_frost_susceptibility."""

    def test_gw_nfs(self):
        r = table_frost_susceptibility("GW")
        assert r["frost_group"] == "NFS"

    def test_sw_s1(self):
        r = table_frost_susceptibility("SW")
        assert r["frost_group"] == "S1"

    def test_gm_f1(self):
        r = table_frost_susceptibility("GM")
        assert r["frost_group"] == "F1"

    def test_sm_f2(self):
        r = table_frost_susceptibility("SM")
        assert r["frost_group"] == "F2"

    def test_ml_f3(self):
        r = table_frost_susceptibility("ML")
        assert r["frost_group"] == "F3"

    def test_ch_f4(self):
        r = table_frost_susceptibility("CH")
        assert r["frost_group"] == "F4"

    def test_pt_f4(self):
        r = table_frost_susceptibility("PT")
        assert r["frost_group"] == "F4"

    def test_dual_symbol(self):
        r = table_frost_susceptibility("GW-GM")
        assert r["frost_group"] == "F1"

    def test_case_insensitive(self):
        r = table_frost_susceptibility("ml")
        assert r["frost_group"] == "F3"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown USCS"):
            table_frost_susceptibility("XX")


class TestFrostDesignReduction:
    """table_frost_design_reduction."""

    def test_nfs(self):
        r = table_frost_design_reduction("NFS")
        assert r["reduction_factor"] == 1.00

    def test_f1(self):
        r = table_frost_design_reduction("F1")
        assert r["reduction_factor"] == 0.65

    def test_f3(self):
        r = table_frost_design_reduction("F3")
        assert r["reduction_factor"] == 0.35

    def test_f4(self):
        r = table_frost_design_reduction("F4")
        assert r["reduction_factor"] == 0.25

    def test_s1(self):
        r = table_frost_design_reduction("S1")
        assert r["reduction_factor"] == 0.90

    def test_case_insensitive(self):
        r = table_frost_design_reduction("f2")
        assert r["frost_group"] == "F2"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown frost group"):
            table_frost_design_reduction("F5")


class TestAircraftClassification:
    """table_aircraft_classification."""

    def test_c130(self):
        r = table_aircraft_classification("C-130")
        assert r["gross_weight_kN"] == 700.0
        assert r["gear_type"] == "tandem"

    def test_c17(self):
        r = table_aircraft_classification("C-17")
        assert r["gross_weight_kN"] == 2650.0

    def test_f15(self):
        r = table_aircraft_classification("F-15")
        assert r["tire_pressure_kPa"] == 2070.0

    def test_b747(self):
        r = table_aircraft_classification("B-747")
        assert r["gear_type"] == "dual_tandem"

    def test_uh60(self):
        r = table_aircraft_classification("UH-60")
        assert r["gear_type"] == "tailwheel"

    def test_case_insensitive(self):
        r = table_aircraft_classification("c-130")
        assert r["aircraft_type"] == "c-130"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown aircraft"):
            table_aircraft_classification("F-22")


class TestPavementLayerCoefficients:
    """table_pavement_layer_coefficients."""

    def test_asphalt(self):
        r = table_pavement_layer_coefficients("asphalt_concrete")
        assert r["coefficient"] == 0.44

    def test_crushed_stone(self):
        r = table_pavement_layer_coefficients("crushed_stone_base")
        assert r["coefficient"] == 0.14

    def test_cement_treated(self):
        r = table_pavement_layer_coefficients("cement_treated_base")
        assert r["coefficient"] == 0.23

    def test_granular_subbase(self):
        r = table_pavement_layer_coefficients("granular_subbase")
        assert r["coefficient"] == 0.11

    def test_sand_subbase(self):
        r = table_pavement_layer_coefficients("sand_subbase")
        assert r["coefficient"] == 0.08

    def test_has_thickness_range(self):
        r = table_pavement_layer_coefficients("asphalt_concrete")
        assert r["typical_thickness_mm"] == (75, 200)

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown material"):
            table_pavement_layer_coefficients("steel_plate")


class TestSubgradeClass:
    """table_subgrade_class."""

    def test_very_poor(self):
        r = table_subgrade_class(2.0)
        assert r["quality"] == "very_poor"

    def test_poor(self):
        r = table_subgrade_class(5.0)
        assert r["quality"] == "poor"

    def test_fair(self):
        r = table_subgrade_class(10.0)
        assert r["quality"] == "fair"

    def test_good(self):
        r = table_subgrade_class(30.0)
        assert r["quality"] == "good"

    def test_excellent(self):
        r = table_subgrade_class(60.0)
        assert r["quality"] == "excellent"

    def test_boundary_0(self):
        r = table_subgrade_class(0.0)
        assert r["quality"] == "very_poor"

    def test_boundary_100(self):
        r = table_subgrade_class(100.0)
        assert r["quality"] == "excellent"

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="cbr must be >= 0"):
            table_subgrade_class(-1.0)

    def test_over_100_raises(self):
        with pytest.raises(ValueError, match="cbr must be <= 100"):
            table_subgrade_class(101.0)
