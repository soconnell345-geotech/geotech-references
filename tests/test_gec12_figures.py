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

    def test_log_linear_in_V_between_columns(self):
        """Step 3e (p. 243): log-linear in V. Between the printed 1.0 and
        2.0 columns at phi 40: 3.00 + 1.30 log10(1.5) = 3.228 (a straight
        line between the columns would give 3.195)."""
        assert figure_7_10_to_13_kd(40, 1.5) == pytest.approx(3.228, abs=0.001)


# ============================================================================
# Figure 7-14: Correction Factor CF
# ============================================================================

class TestCF:
    """Tests for figure_7_14_correction_factor()."""

    # Read off the printed figure (REF-49): each curve's centre line.
    @pytest.mark.parametrize("phi, ratio, cf", [
        (15, 0.2, 0.815), (30, 0.2, 0.580), (45, 0.2, 0.241),
        (30, 0.4, 0.689), (45, 0.6, 0.620), (30, 0.8, 0.945),
        (45, 0.8, 0.841), (45, 1.2, 1.120), (45, 1.4, 1.160),
    ])
    def test_measured_nodes(self, phi, ratio, cf):
        assert figure_7_14_correction_factor(phi, ratio) == pytest.approx(cf, abs=0.001)

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

    def test_cf_falls_with_phi_below_one_and_rises_above(self):
        """The delta/phi < 1 curves fall as phi rises; 1.2 and 1.4 rise."""
        for ratio, sign in ((0.2, -1), (0.6, -1), (1.4, 1)):
            cfs = [figure_7_14_correction_factor(p, ratio) for p in (15, 25, 35, 45)]
            assert all(sign * (b - a) > 0 for a, b in zip(cfs, cfs[1:]))

    def test_interpolates_between_curves(self):
        cf = figure_7_14_correction_factor(30, 0.7)
        assert cf == pytest.approx((0.817 + 0.945) / 2, abs=0.001)

    @pytest.mark.parametrize("phi", [10, 14.9, 45.1, 50])
    def test_cf_phi_out_of_range(self, phi):
        """The curves span about 15-45 deg."""
        with pytest.raises(ValueError, match="outside Figure 7-14"):
            figure_7_14_correction_factor(phi, 1.0)

    def test_cf_ratio_out_of_range(self):
        """delta/phi ratio outside 0.2-1.4 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_14_correction_factor(30, 0.1)


# ============================================================================
# Figure 7-15: Limiting Toe Resistance
# ============================================================================

class TestLimitingToeResistance:
    """Tests for figure_7_15_limiting_toe_resistance()."""

    # Pins measured off the printed figure (2026-10-08); a second pixel read
    # and both vision models agree within about 1 tsf.
    @pytest.mark.parametrize("phi, ql", [
        (30, 7.1), (32, 16.0), (34, 35.9), (36, 75.2), (38, 133.6),
        (40, 208.5), (42, 296.0), (43, 339.2), (43.75, 368.0),
    ])
    def test_measured_nodes(self, phi, ql):
        assert figure_7_15_limiting_toe_resistance(phi) == pytest.approx(ql, abs=0.05)

    def test_interpolates_between_nodes(self):
        assert figure_7_15_limiting_toe_resistance(35.5) == pytest.approx(
            (53.7 + 75.2) / 2, abs=0.05)

    def test_monotonic_increase(self):
        """qL increases with phi."""
        ql_prev = 0
        for phi in [30, 31, 33, 35, 37, 39, 41, 43, 43.75]:
            ql = figure_7_15_limiting_toe_resistance(phi)
            assert ql > ql_prev
            ql_prev = ql

    @pytest.mark.parametrize("phi", [20, 26, 28, 29.9, 43.8, 44, 45, 50])
    def test_refuses_outside_the_chart(self, phi):
        """The axis starts at 30 deg and the curve ends at 43.75 deg."""
        with pytest.raises(ValueError, match="outside Figure 7-15"):
            figure_7_15_limiting_toe_resistance(phi)


# ============================================================================
# Figure 7-16a: alpha_t Coefficient
# ============================================================================

class TestAlphaT:
    """Tests for figure_7_16a_alpha_t()."""

    # Read off the printed figure (REF-49); the curves start at 20 deg and
    # merge at about 37 deg.
    @pytest.mark.parametrize("phi, db, at", [
        (20, 20, 0.365), (20, 30, 0.257), (20, 45, 0.178),
        (30, 20, 0.580), (30, 30, 0.531), (30, 45, 0.491),
        (37, 20, 0.707), (37, 45, 0.707), (45, 30, 0.800),
    ])
    def test_measured_nodes(self, phi, db, at):
        assert figure_7_16a_alpha_t(phi, db) == pytest.approx(at, abs=0.001)

    def test_alpha_t_increases_with_phi(self):
        """alpha_t increases with friction angle."""
        at_prev = 0
        for phi in [20, 25, 30, 35, 40, 45]:
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

    @pytest.mark.parametrize("phi", [10, 15, 19.9, 45.1])
    def test_phi_out_of_range(self, phi):
        """The curves span 20-45 deg."""
        with pytest.raises(ValueError, match="outside Figure 7-16"):
            figure_7_16a_alpha_t(phi, 30)

    def test_db_out_of_range(self):
        """D/b outside 20-45 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_16a_alpha_t(30, 10)


# ============================================================================
# Figure 7-16b: N'q Bearing Capacity Factor
# ============================================================================

class TestNq:
    """Tests for figure_7_16b_nq()."""

    # Read off the printed figure (REF-49) at every degree; the seven
    # earlier nodes read 150 at 40 deg.
    @pytest.mark.parametrize("phi, nq", [
        (15, 4.83), (20, 8.18), (25, 15.00), (30, 30.1), (32, 40.0),
        (35, 63.8), (40, 160.4), (44, 374.0), (45, 475.0),
    ])
    def test_measured_nodes(self, phi, nq):
        assert figure_7_16b_nq(phi) == pytest.approx(nq, rel=1e-6)

    def test_nq_increases_with_phi(self):
        """N'q increases with phi (monotonic on log scale)."""
        nq_prev = 0
        for phi in [15, 20, 25, 30, 35, 40, 45]:
            nq = figure_7_16b_nq(phi)
            assert nq > nq_prev
            nq_prev = nq

    def test_nq_uses_log_interpolation(self):
        """Interpolation is log-linear, not linear: the half degree is the
        geometric mean of the two nodes."""
        nq_mid = figure_7_16b_nq(39.5)
        assert nq_mid == pytest.approx(math.sqrt(130.9 * 160.4), rel=1e-6)

    def test_phi_out_of_range(self):
        """phi outside 15-45 raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_16b_nq(10)


# ============================================================================
# Figure 7-9: delta/phi Ratios
# ============================================================================

class TestDeltaPhiRatio:
    """Tests for figure_7_9_delta_phi_ratio()."""

    # Read off the printed figure (REF-49): delta/phi follows V on each
    # pile type's curve.
    @pytest.mark.parametrize("pile_type, V, ratio, curve", [
        ("pipe_pile", 0.3, 0.344, "a"), ("pipe_pile", 1.0, 0.655, "a"),
        ("timber", 1.9, 0.823, "b"), ("precast_concrete", 1.0, 0.767, "c"),
        ("raymond_step_taper", 1.0, 0.873, "d"),
        ("raymond_uniform_taper", 1.9, 1.270, "e"),
        ("h_pile", 0.15, 0.791, "f"), ("monotube_tapered", 1.0, 0.914, "g"),
    ])
    def test_measured_nodes(self, pile_type, V, ratio, curve):
        result = figure_7_9_delta_phi_ratio(pile_type, V)
        assert result["delta_phi_ratio"] == pytest.approx(ratio, abs=0.001)
        assert result["curve"] == curve

    def test_interpolates_along_the_curve(self):
        result = figure_7_9_delta_phi_ratio("pipe_pile", 1.05)
        assert result["delta_phi_ratio"] == pytest.approx((0.655 + 0.678) / 2, abs=0.001)

    def test_ratio_rises_with_V(self):
        ratios = [figure_7_9_delta_phi_ratio("timber", V)["delta_phi_ratio"]
                  for V in (0.3, 0.8, 1.3, 1.9)]
        assert ratios == sorted(ratios)

    @pytest.mark.parametrize("pile_type, V", [
        ("pipe_pile", 0.2), ("pipe_pile", 2.0), ("h_pile", 0.05), ("h_pile", 0.6),
    ])
    def test_refuses_V_outside_the_curve(self, pile_type, V):
        with pytest.raises(ValueError, match="outside Figure 7-9"):
            figure_7_9_delta_phi_ratio(pile_type, V)

    def test_has_description(self):
        """Result includes a description string."""
        result = figure_7_9_delta_phi_ratio("timber", 1.0)
        assert "description" in result
        assert len(result["description"]) > 0
        assert result["V_range"] == (0.3, 1.9)

    def test_unknown_pile_type(self):
        """Unknown pile type raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_9_delta_phi_ratio("unknown_pile", 1.0)

    def test_partial_match(self):
        """Partial name matching works."""
        result = figure_7_9_delta_phi_ratio("pipe", 1.0)
        assert result["curve"] == "a"


# ============================================================================
# Figure 7-17: Adhesion Ca
# ============================================================================

class TestAdhesion:
    """Tests for figure_7_17_adhesion()."""

    # Read off the printed figure (REF-49): Ca peaks near su = 2 ksf.
    @pytest.mark.parametrize("su, db, surface, ca", [
        (1.0, 10, "concrete", 0.948), (2.0, 10, "concrete", 1.369),
        (3.45, 10, "concrete", 0.827), (2.2, 40, "concrete", 1.819),
        (3.45, 40, "concrete", 1.367), (2.0, 10, "steel", 1.170),
        (2.2, 40, "steel", 1.581), (3.05, 40, "steel", 1.279),
    ])
    def test_measured_nodes(self, su, db, surface, ca):
        assert figure_7_17_adhesion(su, db, surface) == pytest.approx(ca, abs=0.001)

    def test_concrete_d40(self):
        """Concrete pile at D/b=40 gives higher adhesion than D/b=10."""
        ca_d10 = figure_7_17_adhesion(1.5, D_over_b=10.0, pile_surface="concrete")
        ca_d40 = figure_7_17_adhesion(1.5, D_over_b=40.0, pile_surface="concrete")
        assert ca_d40 > ca_d10

    def test_one_solid_curve_below_1_ksf(self):
        """The solid D = 40b curve starts at su = 1.0 ksf."""
        assert figure_7_17_adhesion(0.8, 40.0) == pytest.approx(
            figure_7_17_adhesion(0.8, 10.0))

    def test_ca_falls_past_the_peak(self):
        assert figure_7_17_adhesion(3.0, 10.0) < figure_7_17_adhesion(2.0, 10.0)

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

    @pytest.mark.parametrize("su, surface", [
        (-1.0, "concrete"), (0.0, "concrete"), (0.2, "steel"),
        (3.5, "concrete"), (3.1, "steel"), (5.0, "concrete"),
    ])
    def test_refuses_su_outside_the_curves(self, su, surface):
        with pytest.raises(ValueError, match="outside Figure 7-17"):
            figure_7_17_adhesion(su, pile_surface=surface)

    def test_unknown_surface_raises(self):
        """Unknown pile surface raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_17_adhesion(1.0, pile_surface="fiberglass")


# ============================================================================
# Figure 7-18: Adhesion Factor alpha
# ============================================================================

class TestAdhesionFactor:
    """Tests for figure_7_18_adhesion_factor()."""

    # Read off the printed figure (REF-49).
    @pytest.mark.parametrize("su, db, case, alpha", [
        (2.0, 10, "sand_over_stiff_clay", 1.000),
        (2.0, 20, "sand_over_stiff_clay", 0.955),
        (2.0, 40, "sand_over_stiff_clay", 0.680),
        (5.0, 40, "sand_over_stiff_clay", 0.390),
        (2.0, 10, "soft_over_stiff_clay", 0.296),
        (2.0, 20, "soft_over_stiff_clay", 0.674),
        (2.0, 10, "stiff_clay_only", 0.691),
        (2.0, 40, "stiff_clay_only", 0.902),
        (5.0, 40, "stiff_clay_only", 0.300),
    ])
    def test_measured_nodes(self, su, db, case, alpha):
        assert figure_7_18_adhesion_factor(su, db, case) == pytest.approx(alpha, abs=0.001)

    def test_sand_case_starts_at_alpha_1(self):
        for db in (10, 20, 40):
            assert figure_7_18_adhesion_factor(0.0, db, "sand_over_stiff_clay") == 1.0

    def test_alpha_decreases_with_su(self):
        """Alpha decreases as su increases."""
        alpha_1 = figure_7_18_adhesion_factor(1.0, 40, "sand_over_stiff_clay")
        alpha_3 = figure_7_18_adhesion_factor(3.0, 40, "sand_over_stiff_clay")
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

    def test_linear_in_D_over_b_between_curves(self):
        alpha = figure_7_18_adhesion_factor(2.0, 15, "soft_over_stiff_clay")
        assert alpha == pytest.approx((0.296 + 0.674) / 2, abs=0.001)

    def test_alpha_range(self):
        """Alpha is between 0 and 1 for all valid inputs."""
        for su in [0.6, 1.0, 2.0, 3.0, 4.5]:
            for case in ["sand_over_stiff_clay", "soft_over_stiff_clay", "stiff_clay_only"]:
                alpha = figure_7_18_adhesion_factor(su, 20, case)
                assert 0 <= alpha <= 1.0

    @pytest.mark.parametrize("su, db, case", [
        (-1.0, 20, "sand_over_stiff_clay"), (6.0, 20, "sand_over_stiff_clay"),
        (0.3, 10, "soft_over_stiff_clay"), (4.7, 10, "soft_over_stiff_clay"),
        (5.0, 20, "soft_over_stiff_clay"), (0.0, 10, "stiff_clay_only"),
    ])
    def test_refuses_su_outside_the_curves(self, su, db, case):
        with pytest.raises(ValueError, match="outside Figure 7-18"):
            figure_7_18_adhesion_factor(su, db, case)

    def test_unknown_stratigraphy_raises(self):
        """Unknown stratigraphy raises ValueError."""
        with pytest.raises(ValueError):
            figure_7_18_adhesion_factor(1.0, 20, "unknown_case")

    def test_case_aliases(self):
        """Case aliases work (case1, case_1)."""
        alpha1 = figure_7_18_adhesion_factor(2.0, 20, "sand_over_stiff_clay")
        alpha2 = figure_7_18_adhesion_factor(2.0, 20, "case1")
        assert alpha1 == pytest.approx(alpha2)
