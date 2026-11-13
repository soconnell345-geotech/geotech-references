"""Tests for the AASHTO 1993 rigid-pavement effective modulus of subgrade
reaction procedure (Table 3.2 worksheet, Figures 3.3-3.6, Table 2.7).

Anchors: the guide's own printed worked examples -- Figure 3.3's standalone
example (pdf_page 128, printed II-39: Dsb=6in, Esb=20,000psi, MR=7,000psi ->
k_inf=400 pci), Figure 3.4's standalone example (pdf_page 129, printed
II-40: MR=4,000psi, Dsg=5ft, k_inf=230pci -> k=300pci) PLUS three more
exact (MR, k_inf, k) triples recovered from the fully-worked Table 3.3
seasonal example (pdf_page 132, printed II-43: 6in granular subbase, depth
to rigid foundation 5ft, projected slab 9in, LS=1.0 -> effective k=540pci,
LS-corrected k=170pci), plus direct chart reads on Figures 3.5/3.6 (multiple
points per curve, documented in composite_k.py's section docstrings) and
Table 2.7 (pdf_page 116, printed II-27).
"""

import pytest

from geotech_references.aashto_1993 import composite_k as ck


# ============================================================================
# loss_of_support_values (Table 2.7)
# ============================================================================

class TestLossOfSupportValues:
    def test_cement_treated_granular_base(self):
        r = ck.loss_of_support_values("cement_treated_granular_base")
        assert r["e_min_psi"] == 1000000 and r["e_max_psi"] == 2000000
        assert r["ls_min"] == 0.0 and r["ls_max"] == 1.0

    def test_lime_stabilized(self):
        r = ck.loss_of_support_values("lime_stabilized")
        assert r["e_min_psi"] == 20000 and r["e_max_psi"] == 70000
        assert r["ls_min"] == 1.0 and r["ls_max"] == 3.0

    def test_fine_grained_or_natural_subgrade(self):
        r = ck.loss_of_support_values("fine_grained_or_natural_subgrade_materials")
        assert r["ls_min"] == 2.0 and r["ls_max"] == 3.0

    def test_full_table(self):
        r = ck.loss_of_support_values()
        assert len(r["rows"]) == 7
        names = {row["material"] for row in r["rows"]}
        assert "unbound_granular_materials" in names
        assert "asphalt_treated_base" in names

    def test_unknown_material_raises(self):
        with pytest.raises(ValueError):
            ck.loss_of_support_values("gravel")


# ============================================================================
# composite_k_subbase (Figure 3.3)
# ============================================================================

class TestCompositeKSubbase:
    """Figure 3.3 read off the printed chart (REF-58). Anchors: Figure
    3.3's own example and the four Table 3.3 rows (pdf_page 132, printed
    II-43), all at Dsb=6in; the guide's own two reads of one point (400 and
    410 pci) differ by 2.5%, which sets the tolerance."""

    def test_figure_3_3_standalone_example(self):
        # Dsb=6in, Esb=20,000psi, MR=7,000psi -> printed k_inf=400 pci
        r = ck.composite_k_subbase(mr_psi=7000, esb_psi=20000, dsb_in=6.0)
        assert r["k_inf_pci"] == pytest.approx(400, rel=0.05)
        assert r["chart_read"] is True
        assert "Figure 3.3" in r["reference"]

    def test_table_3_3_jan_row(self):
        r = ck.composite_k_subbase(mr_psi=20000, esb_psi=50000, dsb_in=6.0)
        assert r["k_inf_pci"] == pytest.approx(1100, rel=0.05)

    def test_table_3_3_mar_row(self):
        r = ck.composite_k_subbase(mr_psi=2500, esb_psi=15000, dsb_in=6.0)
        assert r["k_inf_pci"] == pytest.approx(160, rel=0.05)

    def test_table_3_3_apr_row(self):
        r = ck.composite_k_subbase(mr_psi=4000, esb_psi=15000, dsb_in=6.0)
        assert r["k_inf_pci"] == pytest.approx(230, rel=0.05)

    def test_table_3_3_june_row(self):
        r = ck.composite_k_subbase(mr_psi=7000, esb_psi=20000, dsb_in=6.0)
        assert r["k_inf_pci"] == pytest.approx(410, rel=0.05)

    def test_stiff_subbase_lands_between_drawn_diagonals(self):
        # Esb 400,000 psi over MR 5,000 psi at Dsb 6in: the construction
        # lands between the chart's 400 and 600 pci diagonals (the old
        # power-law fit gave about 3,000 pci, beyond the chart's 2,000).
        r = ck.composite_k_subbase(mr_psi=5000, esb_psi=400000, dsb_in=6.0)
        assert 400 < r["k_inf_pci"] < 600
        assert "note" not in r

    def test_monotonic_increasing_in_esb(self):
        prev = 0
        for esb in (15000, 30000, 50000, 100000, 300000):
            k = ck.composite_k_subbase(mr_psi=7000, esb_psi=esb, dsb_in=6.0)["k_inf_pci"]
            assert k > prev
            prev = k

    def test_monotonic_increasing_in_mr(self):
        prev = 0
        for mr in (1000, 3000, 7000, 12000, 20000):
            k = ck.composite_k_subbase(mr_psi=mr, esb_psi=30000, dsb_in=10.0)["k_inf_pci"]
            assert k > prev
            prev = k

    def test_monotonic_increasing_in_dsb(self):
        prev = 0
        for dsb in (6, 8, 10, 12, 14, 18):
            k = ck.composite_k_subbase(mr_psi=7000, esb_psi=20000, dsb_in=dsb)["k_inf_pci"]
            assert k > prev
            prev = k

    def test_below_printed_dsb_raises(self):
        # Below the 6in gridline the chart is not read (reading the 6in
        # curves would overstate k).
        with pytest.raises(ValueError, match="Dsb scale"):
            ck.composite_k_subbase(mr_psi=7000, esb_psi=20000, dsb_in=4.0)

    def test_below_printed_esb_raises(self):
        with pytest.raises(ValueError, match="lowest"):
            ck.composite_k_subbase(mr_psi=7000, esb_psi=10000, dsb_in=6.0)

    def test_below_printed_mr_raises(self):
        with pytest.raises(ValueError, match="lowest"):
            ck.composite_k_subbase(mr_psi=800, esb_psi=20000, dsb_in=6.0)

    # REF-76: Figure 3.3 (printed II-39) draws Dsb 6-18 in, Esb curves
    # 15,000-1,000,000 psi, MR curves 1,000-20,000 psi and k_inf diagonals
    # 50-2,000 pci; above them the nearest curve used to be read with a
    # note. The guide gives no rule there, so they are refused.
    def test_esb_above_printed_curves_refused(self):
        assert "note" not in ck.composite_k_subbase(
            mr_psi=7000, esb_psi=1000000, dsb_in=6.0)
        with pytest.raises(ValueError, match="1,000,000 psi, printed II-39"):
            ck.composite_k_subbase(mr_psi=7000, esb_psi=2000000, dsb_in=6.0)

    def test_dsb_above_printed_scale_refused(self):
        ck.composite_k_subbase(mr_psi=7000, esb_psi=20000, dsb_in=18.0)
        with pytest.raises(ValueError, match="6-18 in, printed II-39"):
            ck.composite_k_subbase(mr_psi=7000, esb_psi=20000, dsb_in=25.0)

    def test_mr_above_printed_curves_refused(self):
        ck.composite_k_subbase(mr_psi=20000, esb_psi=20000, dsb_in=6.0)
        with pytest.raises(ValueError, match="20,000 psi, printed II-39"):
            ck.composite_k_subbase(mr_psi=25000, esb_psi=20000, dsb_in=6.0)

    def test_beyond_highest_diagonal_refused(self):
        with pytest.raises(ValueError, match="beyond the highest drawn "
                           "diagonal, 2,000 pci"):
            ck.composite_k_subbase(mr_psi=20000, esb_psi=1000000, dsb_in=18.0)

    def test_invalid_mr_raises(self):
        with pytest.raises(ValueError):
            ck.composite_k_subbase(mr_psi=0, esb_psi=20000, dsb_in=6.0)

    def test_invalid_esb_raises(self):
        with pytest.raises(ValueError):
            ck.composite_k_subbase(mr_psi=7000, esb_psi=-1, dsb_in=6.0)

    def test_invalid_dsb_raises(self):
        with pytest.raises(ValueError):
            ck.composite_k_subbase(mr_psi=7000, esb_psi=20000, dsb_in=0)


# ============================================================================
# k_rigid_foundation_correction (Figure 3.4)
# ============================================================================

class TestKRigidFoundationCorrection:
    """Figure 3.4 read off the chart (GM-303): the three Dsg curves traced,
    the twelve k_inf lines fitted, worked by the chart's construction."""

    def test_printed_worked_example(self):
        # MR=4,000psi, Dsg=5ft, k_inf=230pci -> printed k=300 pci
        r = ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=5.0, k_inf_pci=230)
        assert r["k_pci"] == pytest.approx(300, rel=0.02)
        assert "note" not in r

    @pytest.mark.parametrize("mr,k_inf,k", [(20000, 1100, 1350),
                                            (2500, 160, 230),
                                            (4000, 230, 300),
                                            (7000, 410, 540)])
    def test_table_3_3_rows(self, mr, k_inf, k):
        # Table 3.3 (printed II-43), all at Dsg 5 ft: the guide's own reads
        # of Figure 3.4, within 4 % of the chart read.
        r = ck.k_rigid_foundation_correction(mr_psi=mr, dsg_ft=5.0, k_inf_pci=k_inf)
        assert r["k_pci"] == pytest.approx(k, rel=0.04)

    def test_k_inf_lines_fan_out(self):
        # Made-up inputs: the correction grows with k_inf (the lines fan
        # out), which a multiplier per MR cannot show.
        # (k_inf 800 at Dsg 3 ft lands past the k scale's 2,000 pci end and
        # is refused since REF-76; 500 lands at about 1,090.)
        lo = ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=3.0, k_inf_pci=100)["k_pci"]
        hi = ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=3.0, k_inf_pci=500)["k_pci"]
        assert hi / 500 > lo / 100 > 1

    def test_outside_the_drawn_curves_refused(self):
        # REF-76: Figure 3.4 (printed II-40) draws Dsg 2, 5 and 10 ft, MR to
        # 20,000 psi (the 2-ft curve from 1,169 psi), k_inf lines 50-1,400
        # pci and a k scale to 2,000 pci. Each case used to be read at the
        # nearest curve, or uncorrected, with a note; now refused.
        ok = ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=2.0, k_inf_pci=230)
        assert "note" not in ok
        with pytest.raises(ValueError, match="2-ft curve"):
            ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=1.0, k_inf_pci=230)
        with pytest.raises(ValueError, match="50-1,400 pci, printed II-40"):
            ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=5.0, k_inf_pci=1500)
        with pytest.raises(ValueError, match="50-1,400 pci"):
            ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=5.0, k_inf_pci=40)
        with pytest.raises(ValueError, match="1,073-20,000 psi"):
            ck.k_rigid_foundation_correction(mr_psi=25000, dsg_ft=5.0, k_inf_pci=1000)
        with pytest.raises(ValueError, match="1,169-20,000 psi"):
            ck.k_rigid_foundation_correction(mr_psi=1100, dsg_ft=3.0, k_inf_pci=100)
        with pytest.raises(ValueError, match="2,000 pci end"):
            ck.k_rigid_foundation_correction(mr_psi=20000, dsg_ft=2.0, k_inf_pci=1400)
        # the edges themselves are read
        ck.k_rigid_foundation_correction(mr_psi=1169, dsg_ft=9.0, k_inf_pci=50)
        ck.k_rigid_foundation_correction(mr_psi=20000, dsg_ft=9.0, k_inf_pci=50)

    def test_lower_mr_limit_follows_the_curves_used(self):
        # Checker finding on REF-76: Figure 3.4 (printed II-40) draws the
        # 5-ft and 10-ft curves down to 1,073 and 1,083 psi; only the 2-ft
        # curve leaves the top at 1,169. A Dsg of 5-10 ft was refused below
        # 1,169 psi for the 2-ft curve's sake.
        r = ck.k_rigid_foundation_correction(mr_psi=1100, dsg_ft=7.0, k_inf_pci=230)
        assert r["k_pci"] > 230
        ck.k_rigid_foundation_correction(mr_psi=1083, dsg_ft=7.0, k_inf_pci=230)
        ck.k_rigid_foundation_correction(mr_psi=1073, dsg_ft=5.0, k_inf_pci=230)
        with pytest.raises(ValueError, match="1,083-20,000 psi.*5-ft and 10-ft"):
            ck.k_rigid_foundation_correction(mr_psi=1080, dsg_ft=7.0, k_inf_pci=230)
        with pytest.raises(ValueError, match="1,073-20,000 psi.*5-ft curve is"):
            ck.k_rigid_foundation_correction(mr_psi=1070, dsg_ft=5.0, k_inf_pci=230)
        with pytest.raises(ValueError, match="2-ft curve leaves the top at 1,169"):
            ck.k_rigid_foundation_correction(mr_psi=1150, dsg_ft=4.0, k_inf_pci=230)
        # a Dsg on a curve reads that curve alone; between, the pair
        on5 = ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=5.0, k_inf_pci=230)
        near = ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=4.999, k_inf_pci=230)
        assert near["k_pci"] == pytest.approx(on5["k_pci"], abs=0.2)

    def test_dsg_at_or_beyond_10ft_disregards_correction(self):
        r = ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=10.0, k_inf_pci=230)
        assert r["k_pci"] == pytest.approx(230, abs=1e-6)
        assert "note" in r

        r2 = ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=15.0, k_inf_pci=230)
        assert r2["k_pci"] == pytest.approx(230, abs=1e-6)

    def test_shallower_rock_gives_larger_correction(self):
        k_shallow = ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=2.0, k_inf_pci=230)["k_pci"]
        k_deep = ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=8.0, k_inf_pci=230)["k_pci"]
        assert k_shallow > k_deep > 230

    def test_correction_always_increases_k(self):
        for dsg in (2, 3, 5, 7, 9):  # Dsg 1 ft is refused since REF-76
            r = ck.k_rigid_foundation_correction(mr_psi=6000, dsg_ft=dsg, k_inf_pci=300)
            assert r["k_pci"] >= 300

    def test_invalid_mr_raises(self):
        with pytest.raises(ValueError):
            ck.k_rigid_foundation_correction(mr_psi=0, dsg_ft=5, k_inf_pci=230)

    def test_invalid_dsg_raises(self):
        with pytest.raises(ValueError):
            ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=0, k_inf_pci=230)

    def test_invalid_kinf_raises(self):
        with pytest.raises(ValueError):
            ck.k_rigid_foundation_correction(mr_psi=4000, dsg_ft=5, k_inf_pci=-1)


# ============================================================================
# relative_damage_rigid (Figure 3.5)
# ============================================================================

class TestRelativeDamageRigid:
    """Two independent anchor sets: (1) all four rows of the guide's Table
    3.3 worked example, D=9in throughout (pdf_page 132, printed II-43),
    validating the k-dependence; (2) six direct chart reads at D=6-14in
    (pdf_page 130), all at a shared low-k reference column, validating the
    D-dependence away from the D=9in anchors."""

    def test_jan_feb_dec_row(self):
        r = ck.relative_damage_rigid(d_in=9.0, k_pci=1350)
        assert r["u_r"] == pytest.approx(0.35, abs=0.01)

    def test_mar_row(self):
        r = ck.relative_damage_rigid(d_in=9.0, k_pci=230)
        assert r["u_r"] == pytest.approx(0.86, abs=0.01)

    def test_apr_may_nov_row(self):
        r = ck.relative_damage_rigid(d_in=9.0, k_pci=300)
        assert r["u_r"] == pytest.approx(0.78, abs=0.01)

    def test_june_oct_row(self):
        r = ck.relative_damage_rigid(d_in=9.0, k_pci=540)
        assert r["u_r"] == pytest.approx(0.60, abs=0.01)

    def test_result_says_chart_not_equation(self):
        # Figure 3.5, aashto1993.pdf PDF 131 (pdf_page 130), printed II-41,
        # is a chart and prints no equation (review pave-28).
        r = ck.relative_damage_rigid(d_in=9.0, k_pci=540)
        assert "prints no equation" in r["print_note"]

    # Chart reads at D=6,7,8,10,12,14in, all at the same reference k-column
    # (k~25.234 pci, back-solved from the D=9 read at that same column --
    # see composite_k.py's Figure 3.5 section docstring for the read
    # values and provenance). Typical agreement <8%, worst case ~12.5%.
    @pytest.mark.parametrize("d_in, u_r_read, tol", [
        (6.0, 0.4083, 0.03),
        (7.0, 0.7280, 0.10),
        (8.0, 0.9502, 0.10),
        (10.0, 2.3550, 0.15),
        (12.0, 3.7070, 0.06),
        (14.0, 5.8250, 0.06),
    ])
    def test_chart_read_verification_points(self, d_in, u_r_read, tol):
        k_ref = 25.234
        r = ck.relative_damage_rigid(d_in=d_in, k_pci=k_ref)
        assert r["u_r"] == pytest.approx(u_r_read, rel=tol)

    def test_monotonic_decreasing_in_k(self):
        prev = 10.0
        for k in (100, 300, 600, 1000, 1500):
            u = ck.relative_damage_rigid(d_in=9.0, k_pci=k)["u_r"]
            assert u < prev
            prev = u

    def test_monotonic_increasing_in_d(self):
        prev = 0.0
        for d in (7, 8, 9, 10, 11):
            u = ck.relative_damage_rigid(d_in=d, k_pci=400)["u_r"]
            assert u > prev
            prev = u

    def test_invalid_d_raises(self):
        with pytest.raises(ValueError):
            ck.relative_damage_rigid(d_in=0, k_pci=400)

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            ck.relative_damage_rigid(d_in=9, k_pci=0)

    def test_off_chart_raises(self):
        # a very thin slab with a very high k drives the base non-positive
        with pytest.raises(ValueError):
            ck.relative_damage_rigid(d_in=1.0, k_pci=5000)


# ============================================================================
# k_loss_of_support (Figure 3.6)
# ============================================================================

class TestKLossOfSupport:
    """Each LS curve's slope is fit to MULTIPLE (k, k_corrected) points
    read directly off the chart (not a single anchor); LS=1.0's read set
    includes the guide's exact printed Table 3.3 value at k=540."""

    def test_result_says_slopes_are_a_fit(self):
        # Figure 3.6, aashto1993.pdf PDF 132 (pdf_page 131), printed II-42,
        # is a chart; the slopes are fitted to chart reads (review pave-28).
        r = ck.k_loss_of_support(k_pci=540, ls=2.0)
        assert "prints no equation" in r["print_note"]
        assert "fit" in r["print_note"]

    def test_ls_zero_is_identity(self):
        r = ck.k_loss_of_support(k_pci=540, ls=0.0)
        assert r["k_corrected_pci"] == pytest.approx(540, rel=1e-6)

    def test_printed_worked_example(self):
        # k=540pci, LS=1.0 -> printed k_corrected=170 pci
        r = ck.k_loss_of_support(k_pci=540, ls=1.0)
        assert r["k_corrected_pci"] == pytest.approx(170, rel=1e-3)

    @pytest.mark.parametrize("k_pci, ls, kc_read, tol", [
        (10, 1.0, 7, 0.07), (50, 1.0, 24, 0.02), (100, 1.0, 43, 0.01),
        (2000, 1.0, 495, 0.01),
        (10, 2.0, 4, 0.02), (50, 2.0, 10, 0.07), (100, 2.0, 16, 0.02),
        (2000, 2.0, 105, 0.06),
        (50, 3.0, 5.5, 0.12), (100, 3.0, 8.5, 0.01),
        (2000, 3.0, 42, 0.20),
    ])
    def test_chart_read_grid_points(self, k_pci, ls, kc_read, tol):
        r = ck.k_loss_of_support(k_pci=k_pci, ls=ls)
        assert r["k_corrected_pci"] == pytest.approx(kc_read, rel=tol)

    def test_higher_ls_gives_lower_corrected_k(self):
        prev = 10000.0
        for ls in (0.0, 1.0, 2.0, 3.0):
            k = ck.k_loss_of_support(k_pci=540, ls=ls)["k_corrected_pci"]
            assert k < prev
            prev = k

    def test_interpolated_ls(self):
        k_at_1 = ck.k_loss_of_support(k_pci=540, ls=1.0)["k_corrected_pci"]
        k_at_2 = ck.k_loss_of_support(k_pci=540, ls=2.0)["k_corrected_pci"]
        k_at_1_5 = ck.k_loss_of_support(k_pci=540, ls=1.5)["k_corrected_pci"]
        assert k_at_2 < k_at_1_5 < k_at_1

    def test_out_of_range_ls_refused(self):
        # REF-76: Figure 3.6 (printed II-42) draws LS = 0, 1.0, 2.0 and 3.0.
        # LS = 4 used to take the LS = 3.0 line (a larger k than the trend)
        # with a note; a negative LS took LS = 0.
        assert "note" not in ck.k_loss_of_support(k_pci=540, ls=3.0)
        assert "note" not in ck.k_loss_of_support(k_pci=540, ls=0.0)
        for ls in (4.0, 3.01, -0.5):
            with pytest.raises(ValueError, match="LS = 0, 1.0, 2.0 and 3.0 "
                               r"\(printed II-42\)"):
                ck.k_loss_of_support(k_pci=540, ls=ls)

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            ck.k_loss_of_support(k_pci=0, ls=1.0)


# ============================================================================
# effective_modulus_subgrade_reaction (Table 3.2 worksheet orchestrator)
# ============================================================================

class TestEffectiveModulusSubgradeReaction:
    """Reproduces the guide's fully-worked Table 3.3 example (pdf_page 132,
    printed II-43): 6in granular subbase, depth to rigid foundation 5ft,
    projected slab thickness 9in, LS=1.0 -> printed effective k=540 pci,
    LS-corrected k=170 pci. With Figure 3.4 anchored to 4 exact Table 3.3
    triples and Figure 3.3 read off the chart, the remaining error (about
    4%) traces to the Figure 3.3 reads (within 5% of the printed rows)."""

    # Table 3.3's 12 monthly (MR psi, Esb psi) pairs, in order.
    SEASONAL = [
        {"mr_psi": 20000, "esb_psi": 50000},  # Jan
        {"mr_psi": 20000, "esb_psi": 50000},  # Feb
        {"mr_psi": 2500, "esb_psi": 15000},   # Mar
        {"mr_psi": 4000, "esb_psi": 15000},   # Apr
        {"mr_psi": 4000, "esb_psi": 15000},   # May
        {"mr_psi": 7000, "esb_psi": 20000},   # June
        {"mr_psi": 7000, "esb_psi": 20000},   # July
        {"mr_psi": 7000, "esb_psi": 20000},   # Aug
        {"mr_psi": 7000, "esb_psi": 20000},   # Sept
        {"mr_psi": 7000, "esb_psi": 20000},   # Oct
        {"mr_psi": 4000, "esb_psi": 15000},   # Nov
        {"mr_psi": 20000, "esb_psi": 50000},  # Dec
    ]

    def test_full_worksheet_reproduces_table_3_3(self):
        r = ck.effective_modulus_subgrade_reaction(
            seasonal=self.SEASONAL, slab_d_in=9.0, dsb_in=6.0,
            dsg_ft=5.0, ls=1.0,
        )
        assert r["n_periods"] == 12
        # printed: sum(u_r)=7.25, avg=0.60 (0.6042); allow chart-reading tolerance
        assert r["ur_avg"] == pytest.approx(0.60, rel=0.05)
        # printed effective k=540 pci, LS-corrected k=170 pci; achieved
        # tolerance is ~4% (see class docstring) -- assert with margin.
        assert r["effective_k_pci"] == pytest.approx(540, rel=0.05)
        assert r["k_corrected_for_loss_of_support_pci"] == pytest.approx(170, rel=0.05)

    def test_rigid_foundation_rows_match_table_3_3(self):
        # Each row stacks two chart reads: Figure 3.3 (composite k, within
        # 5 % of the guide's reads) then Figure 3.4 (within 4 %), so the
        # rows land within 10 % of the printed Table 3.3 column (March 210
        # for 230 from composite k 154 for 160; June 504 for 540 from 391
        # for 410).
        r = ck.effective_modulus_subgrade_reaction(
            seasonal=self.SEASONAL, slab_d_in=9.0, dsb_in=6.0,
            dsg_ft=5.0, ls=1.0,
        )
        expected_rigid = [1350, 1350, 230, 300, 300, 540, 540, 540, 540, 540, 300, 1350]
        for row, exp in zip(r["rows"], expected_rigid):
            assert row["k_rigid_foundation_pci"] == pytest.approx(exp, rel=0.10)

    def test_rows_are_returned_for_auditability(self):
        r = ck.effective_modulus_subgrade_reaction(
            seasonal=self.SEASONAL, slab_d_in=9.0, dsb_in=6.0,
            dsg_ft=5.0, ls=1.0,
        )
        assert len(r["rows"]) == 12
        for row in r["rows"]:
            assert "composite_k_pci" in row
            assert "k_rigid_foundation_pci" in row
            assert "u_r" in row

    def test_no_subbase_falls_back_to_simple_relation(self):
        seasonal = [{"mr_psi": 7000}, {"mr_psi": 5000}, {"mr_psi": 10000}]
        r = ck.effective_modulus_subgrade_reaction(seasonal=seasonal, slab_d_in=9.0)
        for row in r["rows"]:
            assert row["composite_k_pci"] == pytest.approx(row["mr_psi"] / 19.4, abs=0.1)
            assert "esb_psi" not in row

    def test_dsg_ge_10_skips_rigid_foundation_step(self):
        seasonal = [{"mr_psi": 7000, "esb_psi": 20000}]
        r = ck.effective_modulus_subgrade_reaction(
            seasonal=seasonal, slab_d_in=9.0, dsb_in=6.0, dsg_ft=15.0,
        )
        assert "k_rigid_foundation_pci" not in r["rows"][0]

    def test_per_period_esb_override(self):
        seasonal = [{"mr_psi": 7000, "esb_psi": 50000}, {"mr_psi": 7000, "esb_psi": 15000}]
        r = ck.effective_modulus_subgrade_reaction(
            seasonal=seasonal, slab_d_in=9.0, dsb_in=6.0, esb_psi=20000,
        )
        # different esb per period -> different composite k despite same MR
        assert r["rows"][0]["composite_k_pci"] != r["rows"][1]["composite_k_pci"]

    def test_figure_3_3_above_curves_refused_in_worksheet(self):
        # REF-76: a season above Figure 3.3's curves used to carry a note;
        # composite_k_subbase now refuses it, and the worksheet passes the
        # refusal on. So does an LS outside Figure 3.6's 0-3.
        seasonal = [{"mr_psi": 7000, "esb_psi": 2000000},
                    {"mr_psi": 7000, "esb_psi": 20000}]
        with pytest.raises(ValueError, match="highest printed curve"):
            ck.effective_modulus_subgrade_reaction(
                seasonal=seasonal, slab_d_in=9.0, dsb_in=6.0,
            )
        with pytest.raises(ValueError, match="Figure 3.6"):
            ck.effective_modulus_subgrade_reaction(
                seasonal=[{"mr_psi": 7000, "esb_psi": 20000}],
                slab_d_in=9.0, dsb_in=6.0, ls=3.5,
            )

    def test_subbase_below_printed_curves_raises(self):
        with pytest.raises(ValueError, match="Dsb scale"):
            ck.effective_modulus_subgrade_reaction(
                seasonal=[{"mr_psi": 7000, "esb_psi": 20000}],
                slab_d_in=9.0, dsb_in=4.0,
            )

    def test_empty_seasonal_raises(self):
        with pytest.raises(ValueError):
            ck.effective_modulus_subgrade_reaction(seasonal=[], slab_d_in=9.0)

    def test_invalid_slab_thickness_raises(self):
        with pytest.raises(ValueError):
            ck.effective_modulus_subgrade_reaction(
                seasonal=[{"mr_psi": 7000}], slab_d_in=0,
            )

    def test_missing_mr_key_raises(self):
        with pytest.raises(ValueError):
            ck.effective_modulus_subgrade_reaction(
                seasonal=[{"esb_psi": 20000}], slab_d_in=9.0,
            )

    def test_nonpositive_mr_raises(self):
        with pytest.raises(ValueError):
            ck.effective_modulus_subgrade_reaction(
                seasonal=[{"mr_psi": -100}], slab_d_in=9.0,
            )
