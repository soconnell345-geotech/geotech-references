"""Tests for geotech_references.em_2104.reinforcement (Chapter 2 detailing)."""

import pytest

from geotech_references.em_2104.reinforcement import (
    table_2_1_min_cover,
    table_2_2_splice_stagger,
    table_2_3_temp_shrinkage_ratio,
    shrinkage_temperature_reinforcement,
)


class TestTable21MinCover:
    def test_unformed_contact_foundation(self):
        r = table_2_1_min_cover("unformed_contact_foundation")
        assert r["min_cover_in"] == 4.0

    def test_cavitation_abrasion(self):
        r = table_2_1_min_cover("formed_cavitation_abrasion")
        assert r["min_cover_in"] == 6.0

    def test_ge_24in(self):
        assert table_2_1_min_cover("formed_ge_24in")["min_cover_in"] == 4.0

    def test_12_to_24in(self):
        assert table_2_1_min_cover("formed_12_to_24in")["min_cover_in"] == 3.0

    def test_aggregate_floor_governs(self):
        # 1.5x a 3-in aggregate = 4.5 in > the 3-in table value.
        r = table_2_1_min_cover("formed_12_to_24in", aggregate_size_in=3.0)
        assert r["min_cover_in"] == pytest.approx(4.5)
        assert r["governs_by"] == "1.5x_max_aggregate"

    def test_bad_section_raises(self):
        with pytest.raises(ValueError):
            table_2_1_min_cover("not_a_section")


class TestTable22SpliceStagger:
    def test_no11_or_smaller(self):
        r = table_2_2_splice_stagger(11)
        assert r["category"] == "<=No.11"
        assert r["min_stagger_ft"] is None

    def test_larger_than_no11(self):
        r = table_2_2_splice_stagger(14)
        assert r["category"] == ">No.11"
        assert r["min_stagger_ft"] == 5.0


class TestTable23TempShrinkage:
    @pytest.mark.parametrize("spacing, ratio", [
        (20, 0.003), (29.9, 0.003), (30, 0.004), (40, 0.004),
        (40.1, 0.005), (100, 0.005),
    ])
    def test_bands(self, spacing, ratio):
        assert table_2_3_temp_shrinkage_ratio(spacing)["min_ratio"] == ratio

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            table_2_3_temp_shrinkage_ratio(-1)


class TestShrinkageTemperatureReinforcement:
    def test_matches_appendix_d5_example(self):
        # Appendix D-5 Step 7: 42-in stem, monolith > 40 ft -> ratio 0.005,
        # raw A_T&S = 0.005*42*12/2 = 1.26 sq in/ft per face, which EXCEEDS
        # the No.9-at-12in ceiling (1.00 sq in/ft) -- the manual's own
        # example applies the paragraph 2-9b cap and specifies #9 @ 12 in.
        # each face rather than the raw 1.26 sq in (printed p. 87).
        r = shrinkage_temperature_reinforcement(
            joint_spacing_ft=45, gross_thickness_in=42, unit_width_in=12
        )
        assert r["ratio"] == 0.005
        assert r["as_per_face_raw_in2"] == pytest.approx(1.26, abs=1e-6)
        assert r["as_per_face_in2"] == pytest.approx(1.00, abs=1e-6)
        assert r["governs_by"] == "max_no9_at_12in_2-9b"

    def test_min_no4_floor(self):
        # A thin, short-joint-spacing section drives the ratio-based area
        # below the No.4-at-12in floor (0.20 sq in/ft).
        r = shrinkage_temperature_reinforcement(
            joint_spacing_ft=10, gross_thickness_in=8, unit_width_in=12
        )
        assert r["governs_by"] == "min_no4_at_12in_2-9a"
        assert r["as_per_face_in2"] == pytest.approx(0.20, abs=1e-6)

    def test_max_no9_ceiling(self):
        r = shrinkage_temperature_reinforcement(
            joint_spacing_ft=50, gross_thickness_in=200, unit_width_in=12
        )
        assert r["governs_by"] == "max_no9_at_12in_2-9b"
        assert r["as_per_face_in2"] == pytest.approx(1.00, abs=1e-6)
