"""Tests for the AASHTO 1993 roadbed swelling / frost heave environmental
serviceability-loss procedure (Appendix G, Figure 2.2, Table 3.1).

Anchors: the guide's own printed worked examples -- Figure G.2's nomograph
note (theta~0.10, pdf_page 396, printed G-3), Figure G.3's printed worked
example (PI=50, Optimum, 2 ft -> VR=0.83in EXACT by construction, pdf_page
397, printed G-4), Figure G.4's printed nomograph equation and example
(dPSI_sw=0.3, pdf_page 400, printed G-7), Figure G.7's printed example
(dPSI_MAX=2.0 EXACT, pdf_page 403, printed G-10), Figure G.8's printed
nomograph equation and example (dPSI_FH=0.47, pdf_page 404, printed G-11),
and Table 3.1's fully-worked 3-row iteration example (pdf_page 123, printed
II-34), reproduced here via directly-injected column-3/5/6 callables (see
``performance_period_iteration``'s docstring for why the guide's own
SN=4.4/reliability narrative could not be independently chained through).
"""

import pytest

from geotech_references.aashto_1993 import environmental as env


# ============================================================================
# swell_rate_constant_theta (Figure G.2)
# ============================================================================

class TestSwellRateConstantTheta:
    def test_low_moisture_tight_fabric_minimum(self):
        # Both conditions suppress swelling -> minimum rate, exact by
        # construction (this corner sits on the diagonal's own endpoint).
        r = env.swell_rate_constant_theta(0.0, 0.0)
        assert r["theta"] == pytest.approx(0.04)

    def test_high_moisture_fractured_fabric_maximum(self):
        r = env.swell_rate_constant_theta(1.0, 1.0)
        assert r["theta"] == pytest.approx(0.20)

    def test_mixed_corners_give_midpoint(self):
        # Tight fabric chokes off high moisture; fractured fabric can't
        # help without moisture -- both mixed corners land on the diagonal
        # midpoint (0.12), exact by construction.
        r1 = env.swell_rate_constant_theta(0.0, 1.0)
        r2 = env.swell_rate_constant_theta(1.0, 0.0)
        assert r1["theta"] == pytest.approx(0.12)
        assert r2["theta"] == pytest.approx(0.12)

    def test_worked_example_reads_about_0_10(self):
        # Guide's own note d.4 worked example: read theta=0.10. A/B are not
        # given numeric fractions in the guide (qualitative axes); this
        # checks the geometric reconstruction against visually-estimated
        # A/B positions (moisture~0.21, fabric~0.50).
        r = env.swell_rate_constant_theta(0.2137, 0.504)
        assert r["theta"] == pytest.approx(0.10, abs=0.01)
        assert r["chart_read"] is True

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            env.swell_rate_constant_theta(1.5, 0.5)
        with pytest.raises(ValueError):
            env.swell_rate_constant_theta(0.5, -0.1)


# ============================================================================
# potential_vertical_rise (Figure G.3)
# ============================================================================

class TestPotentialVerticalRise:
    def test_printed_worked_example_exact(self):
        # PI=50, Optimum Conditions, 2 ft thickness -> VR=0.83 in (printed
        # on the chart itself; exact by construction, this is the anchor
        # that calibrates the whole function).
        r = env.potential_vertical_rise(50, "optimum", 2)
        assert r["vr_in"] == pytest.approx(0.83)
        assert r["chart_read"] is True

    def test_condition_ordering_minimum_gt_average_gt_optimum(self):
        # At a fixed PI and thickness, less moisture/density control ->
        # more swell (physically sensible ordering shown in the figure).
        vmin = env.potential_vertical_rise(50, "minimum", 2)["vr_in"]
        vavg = env.potential_vertical_rise(50, "average", 2)["vr_in"]
        vopt = env.potential_vertical_rise(50, "optimum", 2)["vr_in"]
        assert vmin > vavg > vopt

    def test_below_condition_threshold_gives_zero(self):
        r = env.potential_vertical_rise(25, "optimum", 5)
        assert r["vr_in"] == 0.0

    def test_thickness_monotonic_increasing(self):
        v_thin = env.potential_vertical_rise(50, "optimum", 2)["vr_in"]
        v_thick = env.potential_vertical_rise(50, "optimum", 30)["vr_in"]
        assert v_thick > v_thin

    def test_thickness_clamped_above_30(self):
        r30 = env.potential_vertical_rise(50, "optimum", 30)
        r40 = env.potential_vertical_rise(50, "optimum", 40)
        assert r40["vr_in"] == pytest.approx(r30["vr_in"])
        assert "note" in r40

    def test_unknown_condition_raises(self):
        with pytest.raises(ValueError):
            env.potential_vertical_rise(50, "bad_condition", 5)

    def test_nonpositive_thickness_raises(self):
        with pytest.raises(ValueError):
            env.potential_vertical_rise(50, "optimum", 0)


# ============================================================================
# swell_probability_guidance (Appendix G.1 text)
# ============================================================================

class TestSwellProbabilityGuidance:
    def test_pi_over_30_and_thickness_over_2ft_triggers_100(self):
        r = env.swell_probability_guidance(35, thickness_ft=3)
        assert r["is_100_pct"] is True
        assert r["ps_pct"] == 100.0

    def test_pi_over_30_and_vr_over_020_triggers_100(self):
        r = env.swell_probability_guidance(35, thickness_ft=1, vr_in=0.25)
        assert r["is_100_pct"] is True

    def test_pi_under_30_does_not_trigger(self):
        r = env.swell_probability_guidance(20, thickness_ft=10, vr_in=1.0)
        assert r["is_100_pct"] is False
        assert "note" in r

    def test_thin_layer_low_vr_does_not_trigger(self):
        r = env.swell_probability_guidance(35, thickness_ft=1, vr_in=0.1)
        assert r["is_100_pct"] is False

    def test_requires_thickness_or_vr(self):
        with pytest.raises(ValueError):
            env.swell_probability_guidance(35)


# ============================================================================
# weighted_swell_parameters (Table G.1)
# ============================================================================

class TestWeightedSwellParameters:
    def test_two_sections(self):
        sections = [
            {"length_ft": 1000, "vr_in": 0.5, "theta": 0.10},
            {"length_ft": 500, "vr_in": 0.1, "theta": 0.06},
        ]
        r = env.weighted_swell_parameters(sections)
        assert r["total_length_ft"] == pytest.approx(1500.0)
        assert r["swelling_length_ft"] == pytest.approx(1000.0)  # only the 0.5in section > 0.20in
        assert r["vr_design_in"] == pytest.approx((0.5 * 1000 + 0.1 * 500) / 1500, abs=1e-4)
        assert r["ps_design_pct"] == pytest.approx(100.0 * 1000 / 1500, abs=1e-2)
        assert r["theta_design"] == pytest.approx((0.10 * 1000 + 0.06 * 500) / 1500, abs=1e-4)

    def test_theta_omitted_when_no_section_provides_it(self):
        sections = [{"length_ft": 100, "vr_in": 0.3}]
        r = env.weighted_swell_parameters(sections)
        assert "theta_design" not in r

    def test_empty_sections_raises(self):
        with pytest.raises(ValueError):
            env.weighted_swell_parameters([])

    def test_missing_vr_raises(self):
        with pytest.raises(ValueError):
            env.weighted_swell_parameters([{"length_ft": 100}])

    def test_nonpositive_length_raises(self):
        with pytest.raises(ValueError):
            env.weighted_swell_parameters([{"length_ft": 0, "vr_in": 0.3}])


# ============================================================================
# swelling_serviceability_loss (Figure G.4)
# ============================================================================

class TestSwellingServiceabilityLoss:
    def test_printed_worked_example(self):
        # t=15yr, theta=0.10, Ps=60%, VR=2in -> printed solution dPSI_sw=0.3
        r = env.swelling_serviceability_loss(vr_in=2, ps_pct=60, theta=0.10, t_yr=15)
        assert r["delta_psi_sw"] == pytest.approx(0.3123, rel=1e-3)
        assert round(r["delta_psi_sw"], 1) == 0.3

    def test_zero_time_gives_zero_loss(self):
        r = env.swelling_serviceability_loss(vr_in=2, ps_pct=60, theta=0.10, t_yr=0)
        assert r["delta_psi_sw"] == 0.0

    def test_monotonic_increasing_with_time(self):
        r1 = env.swelling_serviceability_loss(vr_in=2, ps_pct=60, theta=0.10, t_yr=5)
        r2 = env.swelling_serviceability_loss(vr_in=2, ps_pct=60, theta=0.10, t_yr=20)
        assert r2["delta_psi_sw"] > r1["delta_psi_sw"]

    def test_invalid_ps_raises(self):
        with pytest.raises(ValueError):
            env.swelling_serviceability_loss(vr_in=2, ps_pct=150, theta=0.10, t_yr=15)

    def test_nonpositive_theta_raises(self):
        with pytest.raises(ValueError):
            env.swelling_serviceability_loss(vr_in=2, ps_pct=60, theta=0, t_yr=15)


# ============================================================================
# max_serviceability_loss_frost (Figure G.7)
# ============================================================================

class TestMaxServiceabilityLossFrost:
    def test_printed_worked_example_exact(self):
        r = env.max_serviceability_loss_frost("poor", 5)
        assert r["delta_psi_max"] == pytest.approx(2.0)

    def test_slope_ordering_across_drainage_quality(self):
        vals = [
            env.max_serviceability_loss_frost(q, 10)["delta_psi_max"]
            for q in ("excellent", "good", "fair", "poor", "very_poor")
        ]
        assert vals == sorted(vals)
        assert vals == pytest.approx([1.0, 2.0, 3.0, 4.0, 5.0])

    def test_unknown_drainage_quality_raises(self):
        with pytest.raises(ValueError):
            env.max_serviceability_loss_frost("terrible", 5)

    def test_negative_depth_raises(self):
        with pytest.raises(ValueError):
            env.max_serviceability_loss_frost("good", -1)


# ============================================================================
# frost_susceptibility_classification (Figure G.6 bar)
# ============================================================================

class TestFrostSusceptibilityClassification:
    @pytest.mark.parametrize("rate,expected", [
        (0.3, "negligible"), (0.5, "very_low"), (0.9, "very_low"),
        (1.0, "low"), (1.9, "low"), (2.0, "medium"), (3.9, "medium"),
        (4.0, "high"), (7.9, "high"), (8.0, "very_high"), (20.0, "very_high"),
    ])
    def test_boundaries(self, rate, expected):
        r = env.frost_susceptibility_classification(rate)
        assert r["classification"] == expected

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError):
            env.frost_susceptibility_classification(-1)


# ============================================================================
# frost_heave_rate_group (Figure G.6 body)
# ============================================================================

class TestFrostHeaveRateGroup:
    def test_clean_sand_gravel_low_rate(self):
        r = env.frost_heave_rate_group("gw")
        assert r["rate_range_mm_day"][0] < r["rate_range_mm_day"][1]
        assert r["chart_read"] is True

    def test_fat_clay_negligible(self):
        r = env.frost_heave_rate_group("ch")
        assert r["classification"] in ("negligible", "very_low")

    def test_silty_gravel_higher_than_clean_gravel(self):
        r_gw = env.frost_heave_rate_group("gw")["rate_mm_day"]
        r_gm = env.frost_heave_rate_group("gm")["rate_mm_day"]
        assert r_gm > r_gw

    def test_unknown_group_raises(self):
        with pytest.raises(ValueError):
            env.frost_heave_rate_group("xx")


# ============================================================================
# frost_heave_serviceability_loss (Figure G.8)
# ============================================================================

class TestFrostHeaveServiceabilityLoss:
    def test_printed_worked_example(self):
        # t=15yr, phi=5mm/day, P_F=30%, dPSI_MAX=2.0 -> printed solution 0.47
        r = env.frost_heave_serviceability_loss(
            phi_mm_day=5, pf_pct=30, delta_psi_max=2.0, t_yr=15
        )
        assert r["delta_psi_fh"] == pytest.approx(0.4661, rel=1e-3)
        assert round(r["delta_psi_fh"], 2) == 0.47

    def test_constant_used_is_0_02_not_0_2(self):
        # Sanity check documented in the module docstring: using 0.2 as the
        # exponent constant would give ~0.6, not the printed 0.47.
        import math
        wrong = 0.01 * 30 * 2.0 * (1 - math.exp(-(0.2 * 5 * 15)))
        assert wrong == pytest.approx(0.6, abs=0.01)
        r = env.frost_heave_serviceability_loss(
            phi_mm_day=5, pf_pct=30, delta_psi_max=2.0, t_yr=15
        )
        assert r["delta_psi_fh"] != pytest.approx(0.6, abs=0.05)

    def test_zero_time_gives_zero(self):
        r = env.frost_heave_serviceability_loss(
            phi_mm_day=5, pf_pct=30, delta_psi_max=2.0, t_yr=0
        )
        assert r["delta_psi_fh"] == 0.0

    def test_invalid_pf_raises(self):
        with pytest.raises(ValueError):
            env.frost_heave_serviceability_loss(
                phi_mm_day=5, pf_pct=-5, delta_psi_max=2.0, t_yr=15
            )


# ============================================================================
# total_environmental_loss (Figure 2.2)
# ============================================================================

class TestTotalEnvironmentalLoss:
    def test_sum_of_components(self):
        r = env.total_environmental_loss(
            15,
            swelling={"vr_in": 2, "ps_pct": 60, "theta": 0.10},
            frost={"phi_mm_day": 5, "pf_pct": 30, "delta_psi_max": 2.0},
        )
        assert r["delta_psi_total"] == pytest.approx(
            r["delta_psi_sw"] + r["delta_psi_fh"], rel=1e-6
        )
        assert r["delta_psi_total"] == pytest.approx(0.3123 + 0.4661, rel=1e-3)

    def test_swelling_only(self):
        r = env.total_environmental_loss(15, swelling={"vr_in": 2, "ps_pct": 60, "theta": 0.10})
        assert "delta_psi_fh" not in r
        assert r["delta_psi_total"] == pytest.approx(0.3123, rel=1e-3)

    def test_frost_only(self):
        r = env.total_environmental_loss(
            15, frost={"phi_mm_day": 5, "pf_pct": 30, "delta_psi_max": 2.0}
        )
        assert "delta_psi_sw" not in r
        assert r["delta_psi_total"] == pytest.approx(0.4661, rel=1e-3)

    def test_requires_swelling_or_frost(self):
        with pytest.raises(ValueError):
            env.total_environmental_loss(15)


# ============================================================================
# performance_period_iteration (Table 3.1)
# ============================================================================

class TestPerformancePeriodIteration:
    """Reproduces the guide's own printed 3-row example (pdf_page 123,
    printed II-34) exactly via directly-injected column-3/5/6 callables
    (env_loss_fn / w18_fn / time_from_w18_fn), since the guide's own prose
    around Table 3.1 could not be independently chained through the
    package's flexible-design equation (see the function's docstring)."""

    ENV_LOSS = {13.0: 0.73, 9.65: 0.63, 8.425: 0.56}
    W18 = {1.17: 2.0e6, 1.27: 2.3e6, 1.34: 2.6e6}
    TIME = {2.0e6: 6.3, 2.3e6: 7.2, 2.6e6: 8.2}

    @staticmethod
    def _nearest(table, key):
        return table[min(table, key=lambda k: abs(k - key))]

    def _env_loss_fn(self, t):
        return self._nearest(self.ENV_LOSS, t)

    def _w18_fn(self, dpsi):
        return self._nearest(self.W18, dpsi)

    def _time_fn(self, w18):
        return self._nearest(self.TIME, w18)

    def test_reproduces_printed_rows(self):
        result = env.performance_period_iteration(
            delta_psi_design=1.9,
            w18_fn=self._w18_fn,
            time_from_w18_fn=self._time_fn,
            initial_trial_yr=13.0,
            env_loss_fn=self._env_loss_fn,
            max_iter=3, tol=1e-6,
        )
        rows = result["rows"]
        assert len(rows) == 3

        # Row 1 (printed): trial=13.0, env=0.73, traffic=1.17, w18=2.0e6, corr=6.3
        assert rows[0]["trial_period_yr"] == pytest.approx(13.0)
        assert rows[0]["delta_psi_env"] == pytest.approx(0.73)
        assert rows[0]["delta_psi_traffic"] == pytest.approx(1.17, abs=1e-6)
        assert rows[0]["w18_cumulative"] == pytest.approx(2.0e6)
        assert rows[0]["corresponding_period_yr"] == pytest.approx(6.3)

        # Row 2 (printed): trial=9.7 (here 9.65, guide rounds), env=0.63,
        # traffic=1.27, w18=2.3e6, corr=7.2
        assert rows[1]["trial_period_yr"] == pytest.approx(9.65, abs=0.06)
        assert rows[1]["delta_psi_traffic"] == pytest.approx(1.27, abs=1e-6)
        assert rows[1]["corresponding_period_yr"] == pytest.approx(7.2)

        # Row 3 (printed): trial=8.5 (here 8.425), env=0.56, traffic=1.34,
        # w18=2.6e6, corr=8.2
        assert rows[2]["trial_period_yr"] == pytest.approx(8.425, abs=0.08)
        assert rows[2]["delta_psi_traffic"] == pytest.approx(1.34, abs=1e-6)
        assert rows[2]["corresponding_period_yr"] == pytest.approx(8.2)

        assert result["performance_period_yr"] == pytest.approx(8.2)

    def test_converges_when_trial_meets_corresponding(self):
        env_loss = {10.0: 0.5, 8.0: 0.4}
        w18 = {1.4: 3.0e6, 1.5: 3.2e6}
        time_ = {3.0e6: 8.0, 3.2e6: 8.0}

        result = env.performance_period_iteration(
            delta_psi_design=1.9,
            w18_fn=lambda dpsi: self._nearest(w18, dpsi),
            time_from_w18_fn=lambda w: self._nearest(time_, w),
            initial_trial_yr=10.0,
            env_loss_fn=lambda t: self._nearest(env_loss, t),
            max_iter=5, tol=0.5,
        )
        assert result["converged"] is True

    def test_default_initial_trial_from_max_performance_period(self):
        result = env.performance_period_iteration(
            delta_psi_design=1.9,
            w18_fn=self._w18_fn,
            time_from_w18_fn=self._time_fn,
            max_performance_period_yr=(13.0 / 0.9),
            env_loss_fn=self._env_loss_fn,
            max_iter=1, tol=1e-6,
        )
        assert result["rows"][0]["trial_period_yr"] == pytest.approx(13.0, abs=1e-6)

    def test_requires_env_loss_source(self):
        with pytest.raises(ValueError):
            env.performance_period_iteration(
                delta_psi_design=1.9, w18_fn=self._w18_fn,
                time_from_w18_fn=self._time_fn, initial_trial_yr=10,
            )

    def test_requires_trial_or_max_period(self):
        with pytest.raises(ValueError):
            env.performance_period_iteration(
                delta_psi_design=1.9, w18_fn=self._w18_fn,
                time_from_w18_fn=self._time_fn, env_loss_fn=self._env_loss_fn,
            )

    def test_nonpositive_design_loss_raises(self):
        with pytest.raises(ValueError):
            env.performance_period_iteration(
                delta_psi_design=0, w18_fn=self._w18_fn,
                time_from_w18_fn=self._time_fn, initial_trial_yr=10,
                env_loss_fn=self._env_loss_fn,
            )

    def test_env_loss_exceeding_budget_raises(self):
        with pytest.raises(ValueError):
            env.performance_period_iteration(
                delta_psi_design=0.5,
                w18_fn=self._w18_fn, time_from_w18_fn=self._time_fn,
                initial_trial_yr=13.0, env_loss_fn=self._env_loss_fn,
            )

    def test_swelling_frost_specs_path(self):
        # Exercise the normal (non-injected) path through
        # total_environmental_loss for coverage of that branch.
        result = env.performance_period_iteration(
            delta_psi_design=1.9,
            w18_fn=lambda dpsi: 2.0e6,
            time_from_w18_fn=lambda w: 10.0,
            initial_trial_yr=5.0,
            swelling={"vr_in": 1.0, "ps_pct": 50, "theta": 0.08},
            max_iter=1, tol=1e-6,
        )
        assert result["rows"][0]["delta_psi_env"] > 0
