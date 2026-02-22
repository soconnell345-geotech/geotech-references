"""Tests for GEC-12 figure lookup functions."""

import math
import pytest

from geotech_references.gec_12.figures import (
    figure_7_10_to_13_kd,
    figure_7_14_correction_factor,
    figure_7_15_limiting_toe_resistance,
    figure_7_16a_alpha_t,
    figure_7_16b_nq,
    figure_7_9_delta_phi_ratio,
    figure_7_17_adhesion,
    figure_7_18_adhesion_factor,
)


# ============================================================================
# Tables 7-6 / 7-7: Kd for omega = 0
# ============================================================================

class TestKd:
    """Tests for figure_7_10_to_13_kd() (Tables 7-6, 7-7)."""

    def test_exact_table_7_6_phi25_v010(self):
        """Exact table entry: phi=25, V=0.10 -> Kd=0.70."""
        assert figure_7_10_to_13_kd(25, 0.10) == pytest.approx(0.70, abs=0.01)

    def test_exact_table_7_6_phi30_v050(self):
        """Exact table entry: phi=30, V=0.50 -> Kd=1.06."""
        assert figure_7_10_to_13_kd(30, 0.50) == pytest.approx(1.06, abs=0.01)

    def test_exact_table_7_6_phi35_v100(self):
        """Exact table entry: phi=35, V=1.00 -> Kd=1.75."""
        assert figure_7_10_to_13_kd(35, 1.00) == pytest.approx(1.75, abs=0.01)

    def test_exact_table_7_6_phi40_v100(self):
        """Exact table entry: phi=40, V=1.00 -> Kd=3.00."""
        assert figure_7_10_to_13_kd(40, 1.00) == pytest.approx(3.00, abs=0.01)

    def test_exact_table_7_7_phi30_v50(self):
        """Exact table entry: phi=30, V=5.0 -> Kd=1.36."""
        assert figure_7_10_to_13_kd(30, 5.0) == pytest.approx(1.36, abs=0.01)

    def test_exact_table_7_7_phi40_v100(self):
        """Exact table entry: phi=40, V=10.0 -> Kd=4.30."""
        assert figure_7_10_to_13_kd(40, 10.0) == pytest.approx(4.30, abs=0.01)

    def test_interpolation_phi(self):
        """Interpolation between phi=30 and phi=31 at V=0.50."""
        kd_30 = figure_7_10_to_13_kd(30, 0.50)
        kd_31 = figure_7_10_to_13_kd(31, 0.50)
        kd_305 = figure_7_10_to_13_kd(30.5, 0.50)
        assert kd_30 < kd_305 < kd_31

    def test_interpolation_V(self):
        """Interpolation between V=0.20 and V=0.30 at phi=35."""
        kd = figure_7_10_to_13_kd(35, 0.25)
        assert 1.33 < kd < 1.44  # between V=0.20 and V=0.30 values

    def test_monotonic_with_phi(self):
        """Kd increases with phi for constant V."""
        kd_prev = 0
        for phi in range(25, 41):
            kd = figure_7_10_to_13_kd(phi, 1.0)
            assert kd > kd_prev
            kd_prev = kd

    def test_monotonic_with_V(self):
        """Kd increases with V for constant phi."""
        kd_prev = 0
        for V in [0.10, 0.50, 1.0, 5.0, 10.0]:
            kd = figure_7_10_to_13_kd(35, V)
            assert kd > kd_prev
            kd_prev = kd

    def test_phi_out_of_range_low(self):
        """phi < 25 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_10_to_13_kd(20, 0.50)

    def test_phi_out_of_range_high(self):
        """phi > 40 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_10_to_13_kd(45, 0.50)

    def test_V_out_of_range_low(self):
        """V < 0.10 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_10_to_13_kd(30, 0.05)

    def test_V_out_of_range_high(self):
        """V > 10.0 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_10_to_13_kd(30, 15.0)

    def test_omega_nonzero_raises(self):
        """omega != 0 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_10_to_13_kd(30, 0.50, omega=1.0)

    def test_continuity_at_v1(self):
        """Kd is continuous at V=1.0 boundary between tables."""
        kd_below = figure_7_10_to_13_kd(35, 0.99)
        kd_at = figure_7_10_to_13_kd(35, 1.00)
        kd_above = figure_7_10_to_13_kd(35, 1.01)
        # Both tables give V=1.0 same value, so discontinuity is small
        assert abs(kd_at - kd_below) < 0.05
        assert abs(kd_above - kd_at) < 0.05


# ============================================================================
# Figure 7-14: Correction Factor CF
# ============================================================================

class TestCF:
    """Tests for figure_7_14_correction_factor()."""

    def test_cf_delta_equals_phi(self):
        """When delta/phi = 1.0, CF = 1.0 at all phi."""
        for phi in [15, 25, 35, 45]:
            assert figure_7_14_correction_factor(phi, 1.0) == pytest.approx(1.0)

    def test_cf_increases_with_ratio(self):
        """CF increases with delta/phi ratio at fixed phi."""
        cf_prev = 0
        for ratio in [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]:
            cf = figure_7_14_correction_factor(30, ratio)
            assert cf > cf_prev
            cf_prev = cf

    def test_cf_low_ratio(self):
        """CF at low delta/phi ratio is well below 1.0."""
        cf = figure_7_14_correction_factor(30, 0.2)
        assert cf < 0.25

    def test_cf_high_ratio(self):
        """CF at delta/phi = 1.4 is above 1.0."""
        cf = figure_7_14_correction_factor(30, 1.4)
        assert cf > 1.0

    def test_cf_phi_out_of_range(self):
        """phi outside 15-50 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_14_correction_factor(10, 1.0)

    def test_cf_ratio_out_of_range(self):
        """delta/phi ratio outside 0.2-1.4 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_14_correction_factor(30, 0.1)


# ============================================================================
# Figure 7-15: Limiting Toe Resistance
# ============================================================================

class TestLimitingToeResistance:
    """Tests for figure_7_15_limiting_toe_resistance()."""

    def test_exact_phi_30(self):
        """phi=30 gives qL approx 10 tsf."""
        assert figure_7_15_limiting_toe_resistance(30) == pytest.approx(10.0, abs=1.0)

    def test_exact_phi_40(self):
        """phi=40 gives qL approx 200 tsf."""
        assert figure_7_15_limiting_toe_resistance(40) == pytest.approx(200.0, abs=10.0)

    def test_monotonic_increase(self):
        """qL increases with phi."""
        ql_prev = 0
        for phi in [26, 30, 34, 38, 42, 45]:
            ql = figure_7_15_limiting_toe_resistance(phi)
            assert ql > ql_prev
            ql_prev = ql

    def test_phi_out_of_range(self):
        """phi < 26 or > 45 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_15_limiting_toe_resistance(20)
        with pytest.raises(ValueError):
            figure_7_15_limiting_toe_resistance(50)


# ============================================================================
# Figure 7-16a: alpha_t Coefficient
# ============================================================================

class TestAlphaT:
    """Tests for figure_7_16a_alpha_t()."""

    def test_alpha_t_increases_with_phi(self):
        """alpha_t increases with friction angle."""
        at_prev = 0
        for phi in [15, 20, 25, 30, 35, 40, 45]:
            at = figure_7_16a_alpha_t(phi, 30)
            assert at > at_prev
            at_prev = at

    def test_alpha_t_decreases_with_db(self):
        """alpha_t decreases as D/b increases (deeper piles)."""
        at_20 = figure_7_16a_alpha_t(30, 20)
        at_30 = figure_7_16a_alpha_t(30, 30)
        at_45 = figure_7_16a_alpha_t(30, 45)
        assert at_20 > at_30 > at_45

    def test_alpha_t_range(self):
        """alpha_t is between 0 and 1."""
        for phi in [20, 30, 40]:
            for db in [20, 30, 45]:
                at = figure_7_16a_alpha_t(phi, db)
                assert 0 < at < 1

    def test_phi_out_of_range(self):
        """phi outside 15-45 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_16a_alpha_t(10, 30)

    def test_db_out_of_range(self):
        """D/b outside 20-45 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_16a_alpha_t(30, 10)


# ============================================================================
# Figure 7-16b: N'q Bearing Capacity Factor
# ============================================================================

class TestNq:
    """Tests for figure_7_16b_nq()."""

    def test_nq_at_phi_30(self):
        """N'q at phi=30 is approximately 28."""
        assert figure_7_16b_nq(30) == pytest.approx(28, rel=0.1)

    def test_nq_at_phi_15(self):
        """N'q at phi=15 is approximately 5."""
        assert figure_7_16b_nq(15) == pytest.approx(5, rel=0.1)

    def test_nq_increases_with_phi(self):
        """N'q increases with phi (monotonic on log scale)."""
        nq_prev = 0
        for phi in [15, 20, 25, 30, 35, 40, 45]:
            nq = figure_7_16b_nq(phi)
            assert nq > nq_prev
            nq_prev = nq

    def test_nq_uses_log_interpolation(self):
        """Interpolation is log-linear, not linear."""
        nq_30 = figure_7_16b_nq(30)
        nq_35 = figure_7_16b_nq(35)
        nq_mid = figure_7_16b_nq(32.5)
        # Log-linear midpoint should be geometric mean
        geometric_mean = math.sqrt(nq_30 * nq_35)
        assert abs(nq_mid - geometric_mean) / geometric_mean < 0.05

    def test_phi_out_of_range(self):
        """phi outside 15-45 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_16b_nq(10)


# ============================================================================
# Figure 7-9: delta/phi Ratios
# ============================================================================

class TestDeltaPhiRatio:
    """Tests for figure_7_9_delta_phi_ratio()."""

    def test_pipe_pile(self):
        """Pipe pile has delta/phi around 0.70."""
        result = figure_7_9_delta_phi_ratio("pipe_pile")
        assert result["delta_phi_ratio"] == pytest.approx(0.70)

    def test_h_pile(self):
        """H-pile has lowest delta/phi ratio."""
        result = figure_7_9_delta_phi_ratio("h_pile")
        assert result["delta_phi_ratio"] < 0.70

    def test_precast_concrete(self):
        """Precast concrete has delta/phi around 0.85."""
        result = figure_7_9_delta_phi_ratio("precast_concrete")
        assert result["delta_phi_ratio"] == pytest.approx(0.85)

    def test_has_description(self):
        """Result includes a description string."""
        result = figure_7_9_delta_phi_ratio("timber")
        assert "description" in result
        assert len(result["description"]) > 0

    def test_unknown_pile_type(self):
        """Unknown pile type raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_9_delta_phi_ratio("unknown_pile")

    def test_partial_match(self):
        """Partial name matching works."""
        result = figure_7_9_delta_phi_ratio("pipe")
        assert "delta_phi_ratio" in result


# ============================================================================
# Figure 7-17: Adhesion Ca
# ============================================================================

class TestAdhesion:
    """Tests for figure_7_17_adhesion()."""

    def test_zero_su(self):
        """Zero su gives zero adhesion."""
        assert figure_7_17_adhesion(0.0) == pytest.approx(0.0, abs=0.01)

    def test_concrete_d10(self):
        """Concrete pile at D/b=10, su=1.0 ksf."""
        ca = figure_7_17_adhesion(1.0, D_over_b=10.0, pile_surface="concrete")
        assert 0.6 < ca < 0.8

    def test_concrete_d40(self):
        """Concrete pile at D/b=40 gives higher adhesion than D/b=10."""
        ca_d10 = figure_7_17_adhesion(1.5, D_over_b=10.0, pile_surface="concrete")
        ca_d40 = figure_7_17_adhesion(1.5, D_over_b=40.0, pile_surface="concrete")
        assert ca_d40 > ca_d10

    def test_steel_lower_than_concrete(self):
        """Steel piles give lower adhesion than concrete piles."""
        ca_concrete = figure_7_17_adhesion(1.0, D_over_b=20.0, pile_surface="concrete")
        ca_steel = figure_7_17_adhesion(1.0, D_over_b=20.0, pile_surface="steel")
        assert ca_steel < ca_concrete

    def test_db_clamped(self):
        """D/b values outside 10-40 are clamped, not error."""
        ca_5 = figure_7_17_adhesion(1.0, D_over_b=5.0)
        ca_10 = figure_7_17_adhesion(1.0, D_over_b=10.0)
        assert ca_5 == pytest.approx(ca_10)

    def test_negative_su_raises(self):
        """Negative su raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_17_adhesion(-1.0)

    def test_su_exceeds_range_raises(self):
        """su > 4.0 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_17_adhesion(5.0)

    def test_unknown_surface_raises(self):
        """Unknown pile surface raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_17_adhesion(1.0, pile_surface="fiberglass")


# ============================================================================
# Figure 7-18: Adhesion Factor alpha
# ============================================================================

class TestAdhesionFactor:
    """Tests for figure_7_18_adhesion_factor()."""

    def test_zero_su_gives_alpha_1(self):
        """At su=0, alpha should be 1.0 for all cases."""
        for case in ["sand_over_stiff_clay", "soft_over_stiff_clay", "stiff_clay_only"]:
            alpha = figure_7_18_adhesion_factor(0.0, 20, case)
            assert alpha == pytest.approx(1.0, abs=0.05)

    def test_alpha_decreases_with_su(self):
        """Alpha decreases as su increases."""
        alpha_1 = figure_7_18_adhesion_factor(1.0, 20, "sand_over_stiff_clay")
        alpha_3 = figure_7_18_adhesion_factor(3.0, 20, "sand_over_stiff_clay")
        assert alpha_3 < alpha_1

    def test_case1_d10_highest(self):
        """Case 1: D<10b gives highest alpha (more granular drag-in)."""
        alpha_d10 = figure_7_18_adhesion_factor(2.0, 10, "sand_over_stiff_clay")
        alpha_d40 = figure_7_18_adhesion_factor(2.0, 40, "sand_over_stiff_clay")
        assert alpha_d10 > alpha_d40

    def test_case3_d40_highest(self):
        """Case 3: D>40b gives highest alpha (gap effect diminishes)."""
        alpha_d10 = figure_7_18_adhesion_factor(2.0, 10, "stiff_clay_only")
        alpha_d40 = figure_7_18_adhesion_factor(2.0, 40, "stiff_clay_only")
        assert alpha_d40 > alpha_d10

    def test_alpha_range(self):
        """Alpha is between 0 and 1 for all valid inputs."""
        for su in [0.5, 1.0, 2.0, 3.0, 5.0]:
            for case in ["sand_over_stiff_clay", "soft_over_stiff_clay", "stiff_clay_only"]:
                alpha = figure_7_18_adhesion_factor(su, 20, case)
                assert 0 <= alpha <= 1.0

    def test_negative_su_raises(self):
        """Negative su raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_18_adhesion_factor(-1.0, 20, "sand_over_stiff_clay")

    def test_su_exceeds_range_raises(self):
        """su > 5.0 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_18_adhesion_factor(6.0, 20, "sand_over_stiff_clay")

    def test_unknown_stratigraphy_raises(self):
        """Unknown stratigraphy raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_18_adhesion_factor(1.0, 20, "unknown_case")

    def test_case_aliases(self):
        """Case aliases work (case1, case_1)."""
        alpha1 = figure_7_18_adhesion_factor(2.0, 20, "sand_over_stiff_clay")
        alpha2 = figure_7_18_adhesion_factor(2.0, 20, "case1")
        assert alpha1 == pytest.approx(alpha2)
