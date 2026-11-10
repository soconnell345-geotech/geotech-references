"""Tests for AASHTO 1993 Guide for Design of Pavement Structures.

Anchors: the guide's own printed worked examples (Figure 3.1 flexible design
chart, SN=5.0; Figure 3.7 rigid design chart, D=10.0 in; Figure 2.4 effective
roadbed MR example, MR=5,000 psi), plus the printed regression-equation
"worked check" values (a2=0.14 at EBS=30,000 psi; a3=0.11 at ESB=15,000 psi),
and Table 4.1 reliability values.
"""

import pytest

from geotech_references.aashto_1993 import equations as eq
from geotech_references.aashto_1993 import tables as tb


# ============================================================================
# tables.standard_normal_deviate_zr (Table 4.1)
# ============================================================================

class TestStandardNormalDeviateZr:
    def test_r50(self):
        assert tb.standard_normal_deviate_zr(50)["zr"] == pytest.approx(0.0, abs=1e-6)

    def test_r90(self):
        assert tb.standard_normal_deviate_zr(90)["zr"] == pytest.approx(-1.282, abs=1e-6)

    def test_r95(self):
        assert tb.standard_normal_deviate_zr(95)["zr"] == pytest.approx(-1.645, abs=1e-6)

    def test_r99(self):
        assert tb.standard_normal_deviate_zr(99)["zr"] == pytest.approx(-2.327, abs=1e-6)

    def test_r99_99(self):
        assert tb.standard_normal_deviate_zr(99.99)["zr"] == pytest.approx(-3.750, abs=1e-6)

    def test_interpolated_between_98_and_99(self):
        z = tb.standard_normal_deviate_zr(98.5)["zr"]
        assert -2.327 < z < -2.054

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            tb.standard_normal_deviate_zr(49.9)
        with pytest.raises(ValueError):
            tb.standard_normal_deviate_zr(100)


# ============================================================================
# tables.recommended_reliability (Table 2.2)
# ============================================================================

class TestRecommendedReliability:
    def test_interstate_urban(self):
        r = tb.recommended_reliability("interstate_freeway", "urban")
        assert r["reliability_min_pct"] == 85
        assert r["reliability_max_pct"] == 99.9

    def test_interstate_alias(self):
        r = tb.recommended_reliability("interstate", "rural")
        assert r["functional_class"] == "interstate_freeway"
        assert r["reliability_min_pct"] == 80

    def test_local_urban(self):
        r = tb.recommended_reliability("local", "urban")
        assert r["reliability_min_pct"] == 50
        assert r["reliability_max_pct"] == 80

    def test_collector_rural(self):
        r = tb.recommended_reliability("collector", "rural")
        assert r["reliability_min_pct"] == 75
        assert r["reliability_max_pct"] == 95

    def test_unknown_class_raises(self):
        with pytest.raises(ValueError):
            tb.recommended_reliability("expressway")

    def test_unknown_area_raises(self):
        with pytest.raises(ValueError):
            tb.recommended_reliability("local", "suburban")


class TestOverallStandardDeviationRange:
    def test_flexible(self):
        r = tb.overall_standard_deviation_range("flexible")
        assert r["so_min"] == 0.40
        assert r["so_max"] == 0.50

    def test_rigid(self):
        r = tb.overall_standard_deviation_range("rigid")
        assert r["so_min"] == 0.30
        assert r["so_max"] == 0.40

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            tb.overall_standard_deviation_range("semi-rigid")


class TestTerminalServiceabilityGuidance:
    def test_full_table(self):
        r = tb.terminal_serviceability_guidance()
        assert r["po_flexible"] == 4.2
        assert r["po_rigid"] == 4.5
        assert len(r["rows"]) == 3

    def test_pt_2_5(self):
        r = tb.terminal_serviceability_guidance(2.5)
        assert r["percent_unacceptable"] == 55

    def test_invalid_pt_raises(self):
        with pytest.raises(ValueError):
            tb.terminal_serviceability_guidance(1.5)


class TestLaneDistribution:
    def test_one_lane(self):
        r = tb.lane_distribution_factor(1)
        assert r["dl_min_pct"] == 100 and r["dl_max_pct"] == 100

    def test_two_lanes(self):
        r = tb.lane_distribution_factor(2)
        assert r["dl_min_pct"] == 80 and r["dl_max_pct"] == 100

    def test_four_or_more(self):
        r = tb.lane_distribution_factor(6)
        assert r["dl_min_pct"] == 50 and r["dl_max_pct"] == 75

    def test_directional_default(self):
        r = tb.directional_distribution_default()
        assert r["dd_default"] == 0.5


# ============================================================================
# Layer coefficient charts
# ============================================================================

class TestLayerCoefficientA1:
    def test_100k_psi(self):
        # Figure 2.5, PDF 108 (pdf_page 107), printed II-18: the curve starts
        # on the a1 = 0.20 line at about 106,000 psi (re-read 2026-11-10;
        # was taken as 100,000) and reads 0.252 at 150,000 (was 0.26).
        assert tb.layer_coefficient_a1_asphalt(106000)["a1"] == pytest.approx(0.20, abs=0.005)
        assert tb.layer_coefficient_a1_asphalt(150000)["a1"] == pytest.approx(0.252, abs=0.005)
        assert tb.layer_coefficient_a1_asphalt(125000)["a1"] == pytest.approx(0.224, abs=0.005)
        with pytest.raises(ValueError, match="106,000"):
            tb.layer_coefficient_a1_asphalt(100000)

    def test_200k_psi(self):
        assert tb.layer_coefficient_a1_asphalt(200000)["a1"] == pytest.approx(0.30, abs=0.01)

    def test_450k_caution_note(self):
        r = tb.layer_coefficient_a1_asphalt(500000)
        assert "note" in r

    def test_monotonic_increasing(self):
        prev = 0
        for eac in (110000, 200000, 300000, 400000, 500000):
            a1 = tb.layer_coefficient_a1_asphalt(eac)["a1"]
            assert a1 > prev
            prev = a1

    def test_below_curve_start_refused(self):
        # Figure 2.5, aashto1993.pdf PDF 108 (pdf_page 107), printed II-18:
        # the curve begins at about EAC 106,000 psi, a1 0.20. Below it the
        # chart gives nothing (was silently 0.20).
        with pytest.raises(ValueError, match="curve begins"):
            tb.layer_coefficient_a1_asphalt(80000)

    def test_past_chart_edge_held_with_note(self):
        r = tb.layer_coefficient_a1_asphalt(600000)
        assert r["a1"] == tb.layer_coefficient_a1_asphalt(500000)["a1"]
        assert "held" in r["note"]


class TestLayerCoefficientA2Cement:
    """Figure 2.8 (pdf_page 112, printed II-23): a2 read straight across
    from the UCS scale's labelled ticks. The 800 psi tick sits on the
    printed 0.22 dashed line; 200 psi reads about 0.126 (between the 0.12
    and 0.14 ticks), 1000 psi about 0.25."""

    def test_800_psi_on_the_022_line(self):
        assert tb.layer_coefficient_a2_cement_treated(800)["a2"] == pytest.approx(0.22, abs=0.003)

    def test_ticks_read_across(self):
        for ucs, a2 in ((200, 0.126), (400, 0.155), (600, 0.188), (1000, 0.25)):
            assert tb.layer_coefficient_a2_cement_treated(ucs)["a2"] == pytest.approx(a2, abs=0.005)

    def test_linear_between_ticks(self):
        assert tb.layer_coefficient_a2_cement_treated(300)["a2"] == pytest.approx(
            (0.126 + 0.155) / 2, abs=0.001)

    def test_below_lowest_tick_raises(self):
        with pytest.raises(ValueError, match="lowest labelled tick"):
            tb.layer_coefficient_a2_cement_treated(150)

    def test_above_top_tick_held_with_note(self):
        r = tb.layer_coefficient_a2_cement_treated(1200)
        assert r["a2"] == pytest.approx(0.25, abs=0.003)
        assert "top tick" in r["note"]


class TestLayerCoefficientA2Bituminous:
    """Figure 2.9 (pdf_page 113, printed II-24): the 1600 lb tick sits on
    the printed 0.30 dashed line and 1200 lb at 0.25; the 0.20 dashed line
    falls just below the 800 lb tick (800 lb reads about 0.204)."""

    def test_1600_lb_on_the_030_line(self):
        assert tb.layer_coefficient_a2_bituminous_treated(1600)["a2"] == pytest.approx(0.30, abs=0.003)

    def test_ticks_read_across(self):
        for lb, a2 in ((200, 0.126), (400, 0.161), (800, 0.204), (1200, 0.25), (1800, 0.32)):
            assert tb.layer_coefficient_a2_bituminous_treated(lb)["a2"] == pytest.approx(a2, abs=0.005)

    def test_below_lowest_tick_raises(self):
        with pytest.raises(ValueError, match="lowest labelled tick"):
            tb.layer_coefficient_a2_bituminous_treated(100)

    def test_above_top_tick_held_with_note(self):
        r = tb.layer_coefficient_a2_bituminous_treated(2000)
        assert r["a2"] == pytest.approx(0.32, abs=0.003)
        assert "top tick" in r["note"]


class TestUnboundK1K2:
    def test_base_dry(self):
        r = tb.unbound_k1_k2("base", "dry")
        assert r["k1_min"] == 6000 and r["k1_max"] == 10000

    def test_subbase_wet(self):
        r = tb.unbound_k1_k2("subbase", "wet")
        assert r["k1_min"] == 1500 and r["k1_max"] == 4000

    def test_invalid_layer_raises(self):
        with pytest.raises(ValueError):
            tb.unbound_k1_k2("surface", "dry")

    def test_invalid_moisture_raises(self):
        with pytest.raises(ValueError):
            tb.unbound_k1_k2("base", "saturated")


# ============================================================================
# Drainage / load transfer tables
# ============================================================================

class TestDrainageMiFlexible:
    # Table 2.4, aashto1993.pdf PDF 115 (pdf_page 114), printed II-25; cells
    # printed high-low ("1.15-1.05"): mi_min is the low value.
    def test_fair_default_aashto_road_test(self):
        r = tb.drainage_mi_flexible("fair", "1-5%")
        assert r["mi_min"] == 1.05 and r["mi_max"] == 1.15
        assert r["mi_min"] <= r["mi_max"]

    def test_excellent_lt1pct(self):
        r = tb.drainage_mi_flexible("excellent", "<1%")
        assert r["mi_min"] == 1.35 and r["mi_max"] == 1.40

    def test_very_poor_gt25pct(self):
        r = tb.drainage_mi_flexible("very_poor", ">25%")
        assert r["mi_min"] == 0.40 and r["mi_max"] == 0.40

    def test_invalid_quality_raises(self):
        with pytest.raises(ValueError):
            tb.drainage_mi_flexible("mediocre", "<1%")

    def test_invalid_saturation_raises(self):
        with pytest.raises(ValueError):
            tb.drainage_mi_flexible("fair", "10%")


class TestDrainageCdRigid:
    # Table 2.5, PDF 116 (pdf_page 115), printed II-26; cells printed
    # high-low ("1.10-1.00"): cd_min is the low value.
    def test_fair_1_5pct(self):
        r = tb.drainage_cd_rigid("fair", "1-5%")
        assert r["cd_min"] == 1.00 and r["cd_max"] == 1.10

    def test_excellent_lt1pct(self):
        r = tb.drainage_cd_rigid("excellent", "<1%")
        assert r["cd_min"] == 1.20 and r["cd_max"] == 1.25

    def test_poor_5_25pct(self):
        r = tb.drainage_cd_rigid("poor", "5-25%")
        assert (r["cd_min"], r["cd_max"]) == (0.80, 0.90)


class TestQualityOfDrainageDefinitions:
    def test_full_table(self):
        r = tb.quality_of_drainage_definitions()
        assert len(r["rows"]) == 5

    def test_fair_row(self):
        r = tb.quality_of_drainage_definitions("fair")
        assert r["water_removed_within"] == "1 week"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            tb.quality_of_drainage_definitions("mediocre")


class TestLoadTransferCoefficientJ:
    def test_aashto_road_test_protected_corner(self):
        r = tb.load_transfer_coefficient_j("plain_jointed_jrcp", "asphalt", True)
        assert r["j_min"] == 3.2 and r["j_max"] == 3.2

    def test_no_devices_asphalt_shoulder(self):
        r = tb.load_transfer_coefficient_j("plain_jointed_jrcp", "asphalt", False)
        assert r["j_min"] == 3.8 and r["j_max"] == 4.4

    def test_crcp_tied_shoulder(self):
        r = tb.load_transfer_coefficient_j("crcp", "tied_pcc", True)
        assert r["j_min"] == 2.3 and r["j_max"] == 2.9

    def test_crcp_no_devices_asphalt_is_na(self):
        with pytest.raises(ValueError):
            tb.load_transfer_coefficient_j("crcp", "asphalt", False)

    def test_invalid_pavement_type_raises(self):
        with pytest.raises(ValueError):
            tb.load_transfer_coefficient_j("composite", "asphalt", True)


class TestMinimumLayerThickness:
    def test_low_traffic(self):
        r = tb.minimum_layer_thickness(30000)
        assert r["asphalt_concrete_min_in"] == 1.0
        assert r["aggregate_base_min_in"] == 4

    def test_high_traffic(self):
        r = tb.minimum_layer_thickness(8000000)
        assert r["asphalt_concrete_min_in"] == 4.0
        assert r["aggregate_base_min_in"] == 6

    def test_mid_range(self):
        r = tb.minimum_layer_thickness(1000000)
        assert r["asphalt_concrete_min_in"] == 3.0
        assert r["aggregate_base_min_in"] == 6

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            tb.minimum_layer_thickness(0)


# ============================================================================
# ESAL / load equivalency factor tables (Appendix D subset)
# ============================================================================

class TestEsalFlexibleSingleAxle:
    def test_18kip_reference_axle(self):
        # 18-kip single axle load equivalency factor is always 1.00 by definition
        r = tb.esal_flexible_single_axle(18.0)
        assert r["lef"] == pytest.approx(1.00, abs=0.01)

    def test_2kip_small(self):
        r = tb.esal_flexible_single_axle(2.0)
        assert r["lef"] == pytest.approx(0.0002, abs=1e-5)

    def test_50kip_large(self):
        r = tb.esal_flexible_single_axle(50.0)
        assert r["lef"] == pytest.approx(53, rel=0.02)

    def test_monotonic(self):
        prev = 0
        for axle in (2, 10, 20, 30, 40, 50):
            lef = tb.esal_flexible_single_axle(axle)["lef"]
            assert lef > prev
            prev = lef

    def test_other_sn_reads_appendix_d(self):
        # Table D.4 (pt = 2.5, printed D-6): SN = 3 at 24 kips prints 3.09
        r = tb.esal_flexible_single_axle(24.0, sn=3.0)
        assert r["lef"] == 3.09
        assert r["table"] == "Table D.4"

    def test_other_pt_reads_its_table(self):
        r = tb.esal_flexible_single_axle(18.0, pt=2.0)
        assert r["lef"] == 1.0
        assert r["table"] == "Table D.1"

    def test_off_grid_pt_refused_with_lef_message(self):
        with pytest.raises(ValueError, match="exactly one of 2.0, 2.5, 3.0"):
            tb.esal_flexible_single_axle(18.0, pt=2.2)


class TestEsalFlexibleTandemAxle:
    def test_36kip_digitized_value(self):
        # Table D.5 (SN=5, pt=2.5): 36-kip tandem -> LEF=1.38 (NOT 1.00 --
        # the 1.00 reference point is the 18-kip SINGLE axle, not a 36-kip
        # tandem; tandem groups are less damaging per unit total weight)
        r = tb.esal_flexible_tandem_axle(36.0)
        assert r["lef"] == pytest.approx(1.38, abs=0.02)

    def test_90kip_large(self):
        r = tb.esal_flexible_tandem_axle(90.0)
        assert r["lef"] == pytest.approx(46.8, rel=0.02)


class TestEsalRigidSingleAxle:
    def test_18kip_reference_axle(self):
        r = tb.esal_rigid_single_axle(18.0)
        assert r["lef"] == pytest.approx(1.00, abs=0.01)

    def test_50kip(self):
        r = tb.esal_rigid_single_axle(50.0)
        assert r["lef"] == pytest.approx(67.8, rel=0.02)

    def test_other_d_reads_appendix_d(self):
        r = tb.esal_rigid_single_axle(18.0, d_in=10.0)
        assert r["lef"] == 1.0
        assert r["table"] == "Table D.13"
        assert r["d_in"] == 10.0


class TestEsalRigidTandemAxle:
    def test_36kip_digitized_value(self):
        # Table D.14 (D=9in, pt=2.5): 36-kip tandem -> LEF=2.43
        r = tb.esal_rigid_tandem_axle(36.0)
        assert r["lef"] == pytest.approx(2.43, abs=0.02)

    def test_90kip(self):
        r = tb.esal_rigid_tandem_axle(90.0)
        assert r["lef"] == pytest.approx(105, rel=0.02)


# ============================================================================
# equations.py: flexible design equation (Figure 3.1)
# ============================================================================

class TestFlexibleDesignEquation:
    """Verified against the guide's own printed worked example (Figure 3.1,
    pdf_page 121, printed II-32): W18=5e6, R=95% (ZR=-1.645), So=0.35,
    MR=5000 psi, dPSI=1.9 -> printed solution SN=5.0."""

    ZR_95 = -1.645

    def test_forward_reproduces_guide_w18_order_of_magnitude(self):
        r = eq.flexible_w18_from_sn(sn=5.0, zr=self.ZR_95, so=0.35,
                                    delta_psi=1.9, mr_psi=5000)
        # guide's printed W18 = 5e6; nomograph SN=5.0 is itself a rounded
        # read-off, so allow ~5% tolerance
        assert r["w18"] == pytest.approx(5e6, rel=0.05)

    def test_inverse_reproduces_guide_sn(self):
        r = eq.flexible_sn_from_w18(w18=5e6, zr=self.ZR_95, so=0.35,
                                    delta_psi=1.9, mr_psi=5000)
        assert r["sn"] == pytest.approx(5.0, abs=0.1)

    def test_forward_inverse_roundtrip(self):
        fwd = eq.flexible_w18_from_sn(sn=4.0, zr=-1.037, so=0.45,
                                      delta_psi=2.0, mr_psi=8000)
        inv = eq.flexible_sn_from_w18(w18=fwd["w18"], zr=-1.037, so=0.45,
                                      delta_psi=2.0, mr_psi=8000)
        assert inv["sn"] == pytest.approx(4.0, abs=0.02)

    def test_higher_sn_carries_more_traffic(self):
        w1 = eq.flexible_w18_from_sn(sn=3, zr=-1.282, so=0.45, delta_psi=1.9,
                                     mr_psi=5000)["w18"]
        w2 = eq.flexible_w18_from_sn(sn=6, zr=-1.282, so=0.45, delta_psi=1.9,
                                     mr_psi=5000)["w18"]
        assert w2 > w1

    def test_invalid_sn_raises(self):
        with pytest.raises(ValueError):
            eq.flexible_w18_from_sn(sn=0, zr=-1.0, so=0.4, delta_psi=1.9,
                                    mr_psi=5000)

    def test_invalid_delta_psi_raises(self):
        with pytest.raises(ValueError):
            eq.flexible_w18_from_sn(sn=5, zr=-1.0, so=0.4, delta_psi=3.0,
                                    mr_psi=5000)

    def test_invalid_mr_raises(self):
        with pytest.raises(ValueError):
            eq.flexible_w18_from_sn(sn=5, zr=-1.0, so=0.4, delta_psi=1.9,
                                    mr_psi=0)

    def test_sn_bounds_not_bracketed_raises(self):
        with pytest.raises(ValueError):
            eq.flexible_sn_from_w18(w18=1e12, zr=-1.0, so=0.4, delta_psi=1.9,
                                    mr_psi=5000, sn_bounds=(0.5, 3.0))


# ============================================================================
# equations.py: rigid design equation (Figure 3.7)
# ============================================================================

class TestRigidDesignEquation:
    """Verified against the guide's own printed worked example (Figure 3.7,
    pdf_page 134-135, printed II-45/46): k=72pci, Ec=5e6psi, Sc'=650psi,
    J=3.2, Cd=1.0, So=0.29, R=95% (ZR=-1.645), dPSI=1.7, W18=5.1e6 ->
    printed solution D=10.0 in (nearest half-inch)."""

    ZR_95 = -1.645
    COMMON = dict(zr=ZR_95, so=0.29, delta_psi=1.7, sc_psi=650, cd=1.0,
                 j=3.2, ec_psi=5e6, k_pci=72, pt=2.5)

    def test_forward_reproduces_guide_w18_order_of_magnitude(self):
        r = eq.rigid_w18_from_d(d=10.0, **self.COMMON)
        # guide's printed W18=5.1e6; D=10.0 itself is a nomograph read-off
        # rounded to the nearest half-inch, so allow generous tolerance
        assert r["w18"] == pytest.approx(5.1e6, rel=0.25)

    def test_inverse_reproduces_guide_d(self):
        r = eq.rigid_d_from_w18(w18=5.1e6, **self.COMMON)
        assert r["d"] == pytest.approx(10.0, abs=0.5)

    def test_forward_inverse_roundtrip(self):
        fwd = eq.rigid_w18_from_d(d=9.0, **self.COMMON)
        inv = eq.rigid_d_from_w18(w18=fwd["w18"], **self.COMMON)
        assert inv["d"] == pytest.approx(9.0, abs=0.02)

    def test_thicker_slab_carries_more_traffic(self):
        w1 = eq.rigid_w18_from_d(d=8.0, **self.COMMON)["w18"]
        w2 = eq.rigid_w18_from_d(d=12.0, **self.COMMON)["w18"]
        assert w2 > w1

    def test_invalid_d_raises(self):
        with pytest.raises(ValueError):
            eq.rigid_w18_from_d(d=0, **self.COMMON)

    def test_invalid_delta_psi_raises(self):
        bad = dict(self.COMMON)
        bad["delta_psi"] = 3.5
        with pytest.raises(ValueError):
            eq.rigid_w18_from_d(d=10.0, **bad)

    def test_too_thin_slab_raises(self):
        # a very thin slab makes D^0.75 - 18.42/(Ec/k)^0.25 <= 0
        with pytest.raises(ValueError):
            eq.rigid_w18_from_d(d=0.5, **self.COMMON)

    def test_d_bounds_not_bracketed_raises(self):
        with pytest.raises(ValueError):
            eq.rigid_d_from_w18(w18=1e12, d_bounds=(4.0, 8.0), **self.COMMON)


# ============================================================================
# equations.py: structural number & layered thickness
# ============================================================================

class TestStructuralNumber:
    def test_surface_only(self):
        r = eq.structural_number(a1=0.42, d1=4.0)
        assert r["sn"] == pytest.approx(1.68, abs=1e-6)

    def test_three_layers(self):
        r = eq.structural_number(a1=0.42, d1=4.0, a2=0.14, d2=6.0, m2=1.0,
                                 a3=0.11, d3=8.0, m3=0.8)
        expected = 0.42 * 4.0 + 0.14 * 6.0 * 1.0 + 0.11 * 8.0 * 0.8
        assert r["sn"] == pytest.approx(expected, abs=1e-6)

    def test_negative_input_raises(self):
        with pytest.raises(ValueError):
            eq.structural_number(a1=0.42, d1=-1.0)


class TestMinimumLayerThicknesses:
    def test_three_layer_cascade(self):
        r = eq.minimum_layer_thicknesses(
            sn_over_base=2.0, sn_over_subbase=3.5, sn_over_roadbed=5.0,
            a1=0.42, a2=0.14, m2=1.0, a3=0.11, m3=1.0,
        )
        assert r["d1_min"] == pytest.approx(2.0 / 0.42, abs=1e-3)
        sn1_star = 0.42 * r["d1_min"]
        assert r["sn1_actual"] == pytest.approx(sn1_star, abs=1e-3)
        d2_expected = (3.5 - sn1_star) / (0.14 * 1.0)
        assert r["d2_min"] == pytest.approx(d2_expected, abs=1e-3)

    def test_base_alone_sufficient_clamps_deeper_layers(self):
        r = eq.minimum_layer_thicknesses(
            sn_over_base=2.0, sn_over_subbase=2.0, sn_over_roadbed=2.0,
            a1=0.42, a2=0.14, m2=1.0, a3=0.11, m3=1.0,
        )
        assert r["d2_min"] == 0.0
        assert r["d3_min"] == 0.0
        assert "notes" in r

    def test_non_monotonic_sn_raises(self):
        with pytest.raises(ValueError):
            eq.minimum_layer_thicknesses(
                sn_over_base=5.0, sn_over_subbase=3.0, sn_over_roadbed=4.0,
                a1=0.42, a2=0.14, m2=1.0, a3=0.11, m3=1.0,
            )


# ============================================================================
# equations.py: layer coefficient regressions (a2/a3 granular)
# ============================================================================

class TestLayerCoefficientA2Granular:
    def test_printed_worked_check(self):
        # guide's own printed check: EBS=30,000 psi -> a2=0.14
        r = eq.layer_coefficient_a2_granular_base(30000)
        assert r["a2"] == pytest.approx(0.14, abs=0.01)

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            eq.layer_coefficient_a2_granular_base(0)


class TestLayerCoefficientA3Granular:
    def test_printed_worked_check(self):
        # guide's own printed check: ESB=15,000 psi -> a3=0.11
        r = eq.layer_coefficient_a3_granular_subbase(15000)
        assert r["a3"] == pytest.approx(0.11, abs=0.01)

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            eq.layer_coefficient_a3_granular_subbase(-100)


# ============================================================================
# equations.py: effective roadbed resilient modulus
# ============================================================================

class TestRelativeDamageUf:
    def test_5000_psi_matches_guide_figure_2_4(self):
        # guide's Figure 2.4 example: avg uf=0.31 corresponds to MR=5000 psi
        r = eq.relative_damage_uf(5000)
        assert r["uf"] == pytest.approx(0.31, abs=0.02)

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            eq.relative_damage_uf(0)


class TestEffectiveRoadbedResilientModulus:
    """Guide's fully worked 12-month example (Figure 2.4, pdf_page 104,
    printed II-15): monthly MR = [20000,20000,2500,4000,4000,7000,7000,
    7000,7000,7000,4000,20000] psi -> sum(uf)=3.72, avg uf=0.31, effective
    MR=5,000 psi, with each uf read off the Figure 2.3 scale (0.01 / 1.51 /
    0.51 / 0.13). The printed equation uf = 1.18e8 * MR^-2.32 gives 3.846,
    0.3205 and 4,923 psi, 1.5 % below the example."""

    MONTHLY_MR = [20000, 20000, 2500, 4000, 4000, 7000, 7000, 7000, 7000,
                 7000, 4000, 20000]

    def test_effective_mr_matches_guide_example(self):
        r = eq.effective_roadbed_resilient_modulus(self.MONTHLY_MR)
        assert r["effective_mr_psi"] == pytest.approx(5000, rel=0.10)
        assert r["n_seasons"] == 12

    def test_uf_sum_matches_guide_example(self):
        r = eq.effective_roadbed_resilient_modulus(self.MONTHLY_MR)
        assert r["uf_sum"] == pytest.approx(3.72, rel=0.10)

    def test_printed_equation_values(self):
        r = eq.effective_roadbed_resilient_modulus(self.MONTHLY_MR)
        assert r["uf_sum"] == pytest.approx(3.846, abs=0.002)
        assert r["uf_avg"] == pytest.approx(0.3205, abs=0.0002)
        assert r["effective_mr_psi"] == pytest.approx(4923, abs=2)

    def test_uf_avg_matches_guide_example(self):
        r = eq.effective_roadbed_resilient_modulus(self.MONTHLY_MR)
        assert r["uf_avg"] == pytest.approx(0.31, rel=0.10)

    def test_constant_mr_returns_same_mr(self):
        r = eq.effective_roadbed_resilient_modulus([6000] * 12)
        assert r["effective_mr_psi"] == pytest.approx(6000, rel=0.01)

    def test_empty_list_raises(self):
        with pytest.raises(ValueError):
            eq.effective_roadbed_resilient_modulus([])

    def test_nonpositive_value_raises(self):
        with pytest.raises(ValueError):
            eq.effective_roadbed_resilient_modulus([5000, 0, 6000])


class TestModulusSubgradeReactionSimple:
    def test_basic(self):
        r = eq.modulus_subgrade_reaction_simple(mr_psi=7000)
        assert r["k_pci"] == pytest.approx(7000 / 19.4, abs=0.1)

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            eq.modulus_subgrade_reaction_simple(0)


# ============================================================================
# equations.py: serviceability & stage reliability
# ============================================================================

class TestDesignServiceabilityLoss:
    def test_flexible_typical(self):
        r = eq.design_serviceability_loss(po=4.2, pt=2.5)
        assert r["delta_psi"] == pytest.approx(1.7, abs=1e-6)

    def test_pt_ge_po_raises(self):
        with pytest.raises(ValueError):
            eq.design_serviceability_loss(po=4.2, pt=4.2)


class TestStageReliability:
    def test_two_stage_95_percent(self):
        # guide's own example: 95% overall over 2 stages -> 97.5% per stage
        r = eq.stage_reliability(overall_reliability_pct=95, n_stages=2)
        assert r["stage_reliability_pct"] == pytest.approx(97.47, abs=0.05)

    def test_three_stage_90_percent_compounds_to_72_9(self):
        # inverse check of the guide's example: three 90% stages -> 72.9% overall
        r = eq.stage_reliability(overall_reliability_pct=72.9, n_stages=3)
        assert r["stage_reliability_pct"] == pytest.approx(90.0, abs=0.1)

    def test_single_stage_is_identity(self):
        r = eq.stage_reliability(overall_reliability_pct=88, n_stages=1)
        assert r["stage_reliability_pct"] == pytest.approx(88.0, abs=1e-6)

    def test_invalid_reliability_raises(self):
        with pytest.raises(ValueError):
            eq.stage_reliability(overall_reliability_pct=0, n_stages=2)

    def test_invalid_n_stages_raises(self):
        with pytest.raises(ValueError):
            eq.stage_reliability(overall_reliability_pct=90, n_stages=0)


# ============================================================================
# equations.py: aggregate-surfaced road models
# ============================================================================

class TestAggregateLossTruckTraffic:
    # Section 2.2.3, aashto1993.pdf PDF 102 (pdf_page 101), printed II-12:
    # the first equation, GL = 0.12 + 0.1223(LT), > 50 % truck traffic.
    def test_printed_equation(self):
        assert eq.aggregate_loss_truck_traffic(0)["gl_in"] == pytest.approx(0.12)
        assert eq.aggregate_loss_truck_traffic(10)["gl_in"] == pytest.approx(1.343)
        r = eq.aggregate_loss_truck_traffic(50)
        assert r["gl_in"] == pytest.approx(6.235)
        assert "printed II-12" in r["reference"]

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            eq.aggregate_loss_truck_traffic(-1)


class TestAggregateLossArmyCorps:
    # Section 2.2.3, aashto1993.pdf PDF 102 (pdf_page 101), printed II-12:
    # the Brazil-study equation GL = (B/25.4)/(.0045LADT + 3380.6/R + .467G).
    # The function is aggregate_loss_brazil (was aggregate_loss_army_corps).
    def test_basic(self):
        r = eq.aggregate_loss_brazil(bladings=6, ladt=200, radius_ft=1000,
                                     grade_pct=3)
        assert r["gl_in"] == pytest.approx(
            (6 / 25.4) / (0.0045 * 200 + 3380.6 / 1000 + 0.467 * 3), abs=1e-3)
        assert "Brazil" in r["source"]
        assert "printed II-12" in r["reference"]

    def test_invalid_radius_raises(self):
        with pytest.raises(ValueError):
            eq.aggregate_loss_brazil(bladings=6, ladt=200, radius_ft=0,
                                     grade_pct=3)

    def test_old_name_gone(self):
        assert not hasattr(eq, "aggregate_loss_army_corps")


class TestAnnualAggregateLossKenya:
    # Same page: AGL = [T^2/(T^2+50)] x f(4.2 + .092T + 0.889R^2 + 1.88VC);
    # the scan drops decimal points, a space where each was (" 092T" =
    # .092T; f " 037" = .037, was read as 0.37).
    def test_lateritic_default(self):
        r = eq.annual_aggregate_loss_kenya(traffic_thousands=2, rainfall_in=30,
                                           grade_pct=5)
        assert r["f"] == 0.037
        expected = (4 / 54) * 0.037 * (4.2 + 0.092 * 2 + 0.889 * 900 + 1.88 * 5)
        assert r["agl_in_per_year"] == pytest.approx(expected, abs=1e-3)
        assert r["agl_in_per_year"] == pytest.approx(2.231, abs=1e-3)
        r = eq.annual_aggregate_loss_kenya(traffic_thousands=20, rainfall_in=2,
                                           grade_pct=1)
        expected = (400 / 450) * 0.037 * (4.2 + 0.092 * 20 + 0.889 * 4 + 1.88)
        assert r["agl_in_per_year"] == pytest.approx(expected, abs=1e-3)

    def test_coral(self):
        r = eq.annual_aggregate_loss_kenya(traffic_thousands=2, rainfall_in=30,
                                           grade_pct=5, gravel_type="coral")
        assert r["f"] == 0.059

    def test_invalid_gravel_type_raises(self):
        with pytest.raises(ValueError):
            eq.annual_aggregate_loss_kenya(traffic_thousands=2, rainfall_in=30,
                                           grade_pct=5, gravel_type="granite")


# ============================================================================
# Reference text retrieval smoke test
# ============================================================================

class TestReferenceTextRetrieval:
    def test_load_all_chapters(self):
        import json
        from pathlib import Path

        text_dir = Path(__file__).resolve().parent.parent / "geotech_references" / "aashto_1993" / "text"
        chapter_files = sorted(text_dir.glob("chapter*.json"))
        assert len(chapter_files) == 11
        for f in chapter_files:
            data = json.loads(f.read_text(encoding="utf-8"))
            assert data["reference_id"] == "AASHTO Guide for Design of Pavement Structures"
            assert len(data["sections"]) >= 1
            for sec in data["sections"]:
                assert sec["summary"]
                assert sec["key_points"]

    def test_figures_catalog_loads(self):
        import json
        from pathlib import Path

        fc_path = (Path(__file__).resolve().parent.parent / "geotech_references"
                  / "aashto_1993" / "figures_catalog.json")
        data = json.loads(fc_path.read_text(encoding="utf-8"))
        assert data["package"] == "aashto_1993"
        assert len(data["figures"]) == data["figure_count"]
        for fig in data["figures"]:
            assert fig["page_estimated"] is False
            assert isinstance(fig["pdf_page_index"], int)
