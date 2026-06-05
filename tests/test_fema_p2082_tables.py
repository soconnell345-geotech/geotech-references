"""Tests for geotech_references.fema_p2082 (FEMA P-2082, 2020 NEHRP Provisions).

Covers the geotech-relevant seismic-site lookups:
  - Chapter 20 site classification (the REVISED 2020 scheme with intermediate
    classes BC, CD, DE) — Table 20.2-1.
  - Chapter 11 design spectral parameters (SDS/SD1, two-period spectrum) and
    Seismic Design Category (Tables 11.6-1 and 11.6-2).

Boundary values are quoted exactly from FEMA P-2082-1 Table 20.2-1 (PDF p.123)
and Section 11.6 / Tables 11.6-1 and 11.6-2 (PDF p.56).
"""

import pytest

from geotech_references.fema_p2082.tables import (
    site_class_table,
    site_class_from_vs30,
    site_class_f_triggers,
    sdc_from_sds,
    sdc_from_sd1,
    seismic_design_category,
    importance_factor,
)
from geotech_references.fema_p2082.equations import (
    design_spectral_acceleration_short,
    design_spectral_acceleration_1s,
    mcer_from_design_spectrum,
    two_period_spectrum_parameters,
    design_response_spectrum_sa,
)


# ===================================================================
# SITE CLASSIFICATION — Table 20.2-1 (the revised 2020 NEHRP scheme)
# ===================================================================


class TestSiteClassTable:
    def test_eight_velocity_classes(self):
        t = site_class_table()
        classes = [c["site_class"] for c in t["classes"]]
        # The 2020 NEHRP revision: BC, CD, DE added between B/C, C/D, D/E.
        assert classes == ["A", "B", "BC", "C", "CD", "D", "DE", "E"]

    def test_intermediate_classes_present(self):
        classes = {c["site_class"] for c in site_class_table()["classes"]}
        assert {"BC", "CD", "DE"}.issubset(classes)

    def test_bc_is_soft_rock(self):
        bc = next(c for c in site_class_table()["classes"]
                  if c["site_class"] == "BC")
        assert "rock" in bc["description"].lower()
        assert bc["vs_min_ft_s"] == 2100.0
        assert bc["vs_max_ft_s"] == 3000.0

    def test_cites_pdf_page(self):
        assert site_class_table()["pdf_page"] == 123


class TestSiteClassFromVs30:
    @pytest.mark.parametrize("vs_ft, expected", [
        (6000, "A"),    # A: vs > 5,000
        (5001, "A"),
        (5000, "B"),    # B upper bound inclusive
        (4000, "B"),
        (3001, "B"),
        (3000, "BC"),   # BC upper bound inclusive
        (2500, "BC"),
        (2101, "BC"),
        (2100, "C"),    # C upper bound inclusive
        (1800, "C"),
        (1451, "C"),
        (1450, "CD"),   # CD upper bound inclusive
        (1200, "CD"),
        (1001, "CD"),
        (1000, "D"),    # D upper bound inclusive
        (850, "D"),
        (701, "D"),
        (700, "DE"),    # DE upper bound inclusive
        (600, "DE"),
        (501, "DE"),
        (501, "DE"),
        (499, "E"),
        (300, "E"),
    ])
    def test_ft_per_s_boundaries(self, vs_ft, expected):
        # Table 20.2-1 boundary convention: each band is ">lower to upper" with
        # the upper bound inclusive (so a boundary value joins the band whose
        # UPPER bound equals it, i.e. the softer/lower-velocity class).
        r = site_class_from_vs30(vs_ft, "ft/s")
        assert r["site_class"] == expected

    def test_exactly_500_ft_s_edge(self):
        # The printed table leaves a hairline gap at 500 ft/s (DE is ">500 to
        # 700", E is "<500"). We resolve the boundary to the more critical
        # (softer) class E, consistent with the inclusive-upper convention used
        # for the other bands. 499.9 ft/s is unambiguously E.
        assert site_class_from_vs30(500, "ft/s")["site_class"] == "E"
        assert site_class_from_vs30(499.9, "ft/s")["site_class"] == "E"
        assert site_class_from_vs30(500.1, "ft/s")["site_class"] == "DE"

    def test_metric_default_unit(self):
        # 760 m/s ~ 2,493 ft/s -> BC (2,100-3,000 ft/s)
        assert site_class_from_vs30(760)["site_class"] == "BC"
        # 270 m/s ~ 886 ft/s -> D (700-1,000 ft/s)
        assert site_class_from_vs30(270, "m/s")["site_class"] == "D"
        # 150 m/s ~ 492 ft/s -> E (<500 ft/s)
        assert site_class_from_vs30(150, "m/s")["site_class"] == "E"

    def test_metric_matches_ftps(self):
        r_m = site_class_from_vs30(305.0, "m/s")    # 305 m/s = 1,000.66 ft/s
        assert r_m["site_class"] == "CD"
        assert r_m["vs30_ft_s"] == pytest.approx(1000.66, abs=0.5)

    def test_invalid_unit(self):
        with pytest.raises(ValueError):
            site_class_from_vs30(300, "km/h")

    def test_nonpositive(self):
        with pytest.raises(ValueError):
            site_class_from_vs30(0)


class TestSiteClassF:
    def test_four_triggers(self):
        f = site_class_f_triggers()
        triggers = {t["trigger"] for t in f["triggers"]}
        assert triggers == {
            "vulnerable_soils", "peat_organic",
            "very_high_plasticity_clay", "thick_soft_medium_clay",
        }

    def test_liquefaction_is_a_trigger(self):
        f = site_class_f_triggers()
        vuln = next(t for t in f["triggers"] if t["trigger"] == "vulnerable_soils")
        assert "liquefiable" in vuln["description"].lower()

    def test_soft_clay_E_override(self):
        f = site_class_f_triggers()
        assert "25 kPa" in f["site_class_e_soft_clay"]["rule"]


# ===================================================================
# SEISMIC DESIGN CATEGORY — Tables 11.6-1 and 11.6-2
# ===================================================================


class TestSDCFromSDS:
    @pytest.mark.parametrize("sds, rc, expected", [
        (0.10, "II", "A"),
        (0.166, "II", "A"),
        (0.167, "II", "B"),
        (0.30, "II", "B"),
        (0.33, "II", "C"),
        (0.45, "II", "C"),
        (0.50, "II", "D"),
        (0.80, "II", "D"),
        # Risk Category IV column
        (0.10, "IV", "A"),
        (0.20, "IV", "C"),
        (0.40, "IV", "D"),
        (0.60, "IV", "D"),
    ])
    def test_table_11_6_1(self, sds, rc, expected):
        assert sdc_from_sds(sds, rc)["sdc"] == expected

    def test_risk_categories_I_II_III_share_column(self):
        for rc in ("I", "II", "III"):
            assert sdc_from_sds(0.20, rc)["sdc"] == "B"

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            sdc_from_sds(-0.1)


class TestSDCFromSD1:
    @pytest.mark.parametrize("sd1, rc, expected", [
        (0.05, "II", "A"),
        (0.066, "II", "A"),
        (0.067, "II", "B"),
        (0.10, "II", "B"),
        (0.133, "II", "C"),
        (0.18, "II", "C"),
        (0.20, "II", "D"),
        (0.40, "II", "D"),
        (0.05, "IV", "A"),
        (0.10, "IV", "C"),
        (0.15, "IV", "D"),
    ])
    def test_table_11_6_2(self, sd1, rc, expected):
        assert sdc_from_sd1(sd1, rc)["sdc"] == expected


class TestCombinedSDC:
    def test_more_severe_governs(self):
        # SDS->C, SD1->D : SD1 governs
        r = seismic_design_category(sds=0.40, sd1=0.25, risk_category="II")
        assert r["sdc_from_sds"] == "C"
        assert r["sdc_from_sd1"] == "D"
        assert r["sdc"] == "D"
        assert "SD1" in r["governed_by"]

    def test_sds_governs(self):
        # SDS->D, SD1->C : SDS governs
        r = seismic_design_category(sds=0.55, sd1=0.15, risk_category="II")
        assert r["sdc"] == "D"
        assert "SDS" in r["governed_by"]

    def test_s1_override_rc_iii_gives_E(self):
        r = seismic_design_category(sds=0.1, sd1=0.05, risk_category="III", s1=0.80)
        assert r["sdc"] == "E"
        assert "S1" in r["governed_by"]

    def test_s1_override_rc_iv_gives_F(self):
        r = seismic_design_category(sds=0.1, sd1=0.05, risk_category="IV", s1=0.80)
        assert r["sdc"] == "F"

    def test_s1_just_below_threshold_no_override(self):
        r = seismic_design_category(sds=0.1, sd1=0.05, risk_category="II", s1=0.74)
        assert r["s1_override_sdc"] is None
        assert r["sdc"] == "A"

    def test_s1_exactly_075_triggers(self):
        r = seismic_design_category(sds=0.1, sd1=0.05, risk_category="II", s1=0.75)
        assert r["sdc"] == "E"


class TestImportanceFactor:
    @pytest.mark.parametrize("rc, ie", [
        ("I", 1.0), ("II", 1.0), ("III", 1.25), ("IV", 1.5),
    ])
    def test_ie(self, rc, ie):
        assert importance_factor(rc)["importance_factor_ie"] == ie

    def test_bad_rc(self):
        with pytest.raises(ValueError):
            importance_factor("V")


# ===================================================================
# DESIGN SPECTRAL PARAMETERS — Chapter 11 equations
# ===================================================================


class TestDesignSpectralParameters:
    def test_sds_two_thirds_sms(self):
        assert design_spectral_acceleration_short(1.5)["sds"] == pytest.approx(1.0)

    def test_sd1_two_thirds_sm1(self):
        assert design_spectral_acceleration_1s(0.9)["sd1"] == pytest.approx(0.6)

    def test_mcer_is_1_5_design(self):
        assert mcer_from_design_spectrum(0.4)["sa_mcer"] == pytest.approx(0.6)

    def test_negative_sms_raises(self):
        with pytest.raises(ValueError):
            design_spectral_acceleration_short(-0.1)


class TestTwoPeriodSpectrum:
    def test_corner_periods(self):
        r = two_period_spectrum_parameters(sds=1.0, sd1=0.6)
        assert r["ts_s"] == pytest.approx(0.6)
        assert r["t0_s"] == pytest.approx(0.12)

    def test_zero_sds_raises(self):
        with pytest.raises(ValueError):
            two_period_spectrum_parameters(sds=0.0, sd1=0.6)

    def test_ascending_branch_at_zero(self):
        # T=0 -> Sa = 0.4*SDS
        r = design_response_spectrum_sa(0.0, sds=1.0, sd1=0.6, tl=8.0)
        assert r["sa"] == pytest.approx(0.4)
        assert "ascending" in r["branch"]

    def test_plateau_branch(self):
        # T0=0.12, Ts=0.6 ; T=0.3 -> Sa=SDS=1.0
        r = design_response_spectrum_sa(0.3, sds=1.0, sd1=0.6, tl=8.0)
        assert r["sa"] == pytest.approx(1.0)
        assert r["branch"] == "plateau (SDS)"

    def test_constant_velocity_branch(self):
        # Ts=0.6 < T=2 <= TL=8 -> Sa = SD1/T = 0.6/2 = 0.3
        r = design_response_spectrum_sa(2.0, sds=1.0, sd1=0.6, tl=8.0)
        assert r["sa"] == pytest.approx(0.3)
        assert "constant-velocity" in r["branch"]

    def test_constant_displacement_branch(self):
        # T=10 > TL=8 -> Sa = SD1*TL/T^2 = 0.6*8/100 = 0.048
        r = design_response_spectrum_sa(10.0, sds=1.0, sd1=0.6, tl=8.0)
        assert r["sa"] == pytest.approx(0.048)
        assert "constant-displacement" in r["branch"]

    def test_continuity_at_ts(self):
        # At T just above Ts, Sa should be ~SDS (continuity SD1/Ts = SDS).
        r = design_response_spectrum_sa(0.6001, sds=1.0, sd1=0.6, tl=8.0)
        assert r["sa"] == pytest.approx(1.0, abs=1e-3)


# ===================================================================
# TEXT RETRIEVAL — chapter JSON
# ===================================================================


class TestTextRetrieval:
    def test_chapter_20_loads(self):
        from geotech_references import _retrieval
        ch = _retrieval.load_chapter("fema_p2082", 20)
        assert ch["chapter"] == 20
        assert any(s["section_id"] == "20.2" for s in ch["sections"])

    def test_chapter_11_loads(self):
        from geotech_references import _retrieval
        ch = _retrieval.load_chapter("fema_p2082", 11)
        assert ch["chapter"] == 11
        assert any(s["section_id"] == "11.6" for s in ch["sections"])

    def test_search_finds_site_class(self):
        from geotech_references import _retrieval
        hits = _retrieval.search_sections("fema_p2082", "site class shear wave velocity")
        assert len(hits) > 0

    def test_list_chapters(self):
        from geotech_references import _retrieval
        chs = {c["chapter"] for c in _retrieval.list_chapters("fema_p2082")}
        assert {11, 20}.issubset(chs)
