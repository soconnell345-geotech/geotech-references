"""Tests for geotech_references.aashto_1993.lef (axle load equivalency
factors, full Appendix D table digitization -- see the module docstring for
why this is bilinear table interpolation rather than a closed-form equation:
the closed-form AASHO Road Test equations are printed in "Appendix MM of
Volume 2", which is NOT part of ``docs/aashto1993.pdf``).

Validation strategy:
  1. Grid-point reproduction: 72 points (18 tables x 4 loads each), spanning
     both pavement types, all three axle configs (including triples), SN
     1-6 and D 6-14, and all three pt values, low/mid/high loads -- each
     asserted to exactly equal the corresponding printed table cell.
  2. Cross-check against the four pre-existing tables.py digitized curves
     (an independent digitization of the SN=5 / D=9, pt=2.5 subset), at 10
     loads each including off-grid (interpolated) loads.
  3. Structural invariants: the 18-kip row is exactly 1.00 in every
     single-axle table (all pavement types x pt); LEF is non-decreasing
     down every column of every table (a documented tolerance covers a
     handful of near-zero, sub-0.001-magnitude rounding blips in the
     printed source at the smallest loads -- see module docstring).
  4. The one flagged scan-defect cell (Table D.12, load=74 kips, D=9in).
  5. Clamping behavior (load and sn/d_in outside the printed range).
  6. Validation-error tests (bad pavement_type/axle_config, off-grid pt,
     non-positive load/sn/d_in, wrong or missing sn/d_in for the pavement
     type).
"""

import pytest

from geotech_references.aashto_1993 import lef
from geotech_references.aashto_1993 import tables as tb
from geotech_references.aashto_1993.lef import load_equivalency_factor, _TABLES


# ============================================================================
# 1. Grid-point reproduction: 18 tables x 4 (load, column) points each.
# Each expected value is read directly off the rendered printed page (see
# lef.py table comments for pdf_page/printed_page citations).
# ============================================================================

GRID_POINTS = [
    # (pavement, axle_config, pt, col_kwarg, col_value, load, expected_lef, table)
    ("flexible", "single", 2.0, "sn", 1, 2, 0.0002, "D.1"),
    ("flexible", "single", 2.0, "sn", 3, 18, 1.00, "D.1"),
    ("flexible", "single", 2.0, "sn", 4, 32, 11.5, "D.1"),
    ("flexible", "single", 2.0, "sn", 6, 50, 82.0, "D.1"),

    ("flexible", "tandem", 2.0, "sn", 2, 2, 0.0000, "D.2"),
    ("flexible", "tandem", 2.0, "sn", 1, 34, 1.06, "D.2"),
    ("flexible", "tandem", 2.0, "sn", 5, 60, 12.0, "D.2"),
    ("flexible", "tandem", 2.0, "sn", 6, 90, 71.3, "D.2"),

    ("flexible", "triple", 2.0, "sn", 4, 4, 0.0001, "D.3"),
    ("flexible", "triple", 2.0, "sn", 3, 40, 0.481, "D.3"),
    ("flexible", "triple", 2.0, "sn", 1, 70, 5.40, "D.3"),
    ("flexible", "triple", 2.0, "sn", 6, 90, 15.2, "D.3"),

    ("flexible", "single", 2.5, "sn", 2, 6, 0.017, "D.4"),
    ("flexible", "single", 2.5, "sn", 6, 18, 1.00, "D.4"),
    ("flexible", "single", 2.5, "sn", 1, 30, 10.3, "D.4"),
    ("flexible", "single", 2.5, "sn", 4, 50, 60.0, "D.4"),

    ("flexible", "tandem", 2.5, "sn", 3, 8, 0.005, "D.5"),
    ("flexible", "tandem", 2.5, "sn", 5, 36, 1.38, "D.5"),
    ("flexible", "tandem", 2.5, "sn", 2, 64, 17.6, "D.5"),
    ("flexible", "tandem", 2.5, "sn", 1, 90, 93.7, "D.5"),

    ("flexible", "triple", 2.5, "sn", 1, 10, 0.003, "D.6"),
    ("flexible", "triple", 2.5, "sn", 6, 48, 1.005, "D.6"),
    ("flexible", "triple", 2.5, "sn", 4, 66, 3.47, "D.6"),
    ("flexible", "triple", 2.5, "sn", 3, 90, 13.2, "D.6"),

    ("flexible", "single", 3.0, "sn", 2, 2, 0.0009, "D.7"),
    ("flexible", "single", 3.0, "sn", 1, 18, 1.00, "D.7"),
    ("flexible", "single", 3.0, "sn", 5, 34, 7.6, "D.7"),
    ("flexible", "single", 3.0, "sn", 6, 50, 32.0, "D.7"),

    ("flexible", "tandem", 3.0, "sn", 1, 4, 0.001, "D.8"),
    ("flexible", "tandem", 3.0, "sn", 3, 30, 0.788, "D.8"),
    ("flexible", "tandem", 3.0, "sn", 6, 58, 7.7, "D.8"),
    ("flexible", "tandem", 3.0, "sn", 2, 90, 78.8, "D.8"),

    ("flexible", "triple", 3.0, "sn", 4, 6, 0.001, "D.9"),
    ("flexible", "triple", 3.0, "sn", 1, 40, 0.447, "D.9"),
    ("flexible", "triple", 3.0, "sn", 5, 72, 4.31, "D.9"),
    ("flexible", "triple", 3.0, "sn", 6, 90, 10.4, "D.9"),

    ("rigid", "single", 2.0, "d_in", 6, 2, 0.0002, "D.10"),
    ("rigid", "single", 2.0, "d_in", 14, 18, 1.00, "D.10"),
    ("rigid", "single", 2.0, "d_in", 9, 32, 11.8, "D.10"),
    ("rigid", "single", 2.0, "d_in", 13, 50, 89.8, "D.10"),

    ("rigid", "tandem", 2.0, "d_in", 7, 6, 0.002, "D.11"),
    ("rigid", "tandem", 2.0, "d_in", 6, 40, 3.79, "D.11"),
    ("rigid", "tandem", 2.0, "d_in", 12, 64, 31.0, "D.11"),
    ("rigid", "tandem", 2.0, "d_in", 14, 90, 141.0, "D.11"),

    ("rigid", "triple", 2.0, "d_in", 8, 8, 0.002, "D.12"),
    ("rigid", "triple", 2.0, "d_in", 9, 44, 1.77, "D.12"),
    ("rigid", "triple", 2.0, "d_in", 9, 74, 15.8, "D.12"),  # flagged, see below
    ("rigid", "triple", 2.0, "d_in", 14, 90, 40.9, "D.12"),

    ("rigid", "single", 2.5, "d_in", 8, 4, 0.002, "D.13"),
    ("rigid", "single", 2.5, "d_in", 9, 18, 1.00, "D.13"),
    ("rigid", "single", 2.5, "d_in", 6, 36, 18.2, "D.13"),
    ("rigid", "single", 2.5, "d_in", 14, 50, 87.1, "D.13"),

    ("rigid", "tandem", 2.5, "d_in", 10, 10, 0.012, "D.14"),
    ("rigid", "tandem", 2.5, "d_in", 8, 42, 4.30, "D.14"),
    ("rigid", "tandem", 2.5, "d_in", 6, 68, 35.4, "D.14"),
    ("rigid", "tandem", 2.5, "d_in", 13, 90, 123.0, "D.14"),

    ("rigid", "triple", 2.5, "d_in", 11, 12, 0.009, "D.15"),
    ("rigid", "triple", 2.5, "d_in", 9, 46, 2.09, "D.15"),
    ("rigid", "triple", 2.5, "d_in", 7, 70, 10.6, "D.15"),
    ("rigid", "triple", 2.5, "d_in", 14, 90, 39.8, "D.15"),

    ("rigid", "single", 3.0, "d_in", 13, 14, 0.336, "D.16"),
    ("rigid", "single", 3.0, "d_in", 6, 24, 2.90, "D.16"),
    ("rigid", "single", 3.0, "d_in", 9, 38, 17.7, "D.16"),
    ("rigid", "single", 3.0, "d_in", 6, 50, 69.6, "D.16"),

    ("rigid", "tandem", 3.0, "d_in", 14, 16, 0.080, "D.17"),
    ("rigid", "tandem", 3.0, "d_in", 7, 52, 8.41, "D.17"),
    ("rigid", "tandem", 3.0, "d_in", 12, 78, 56.6, "D.17"),
    ("rigid", "tandem", 3.0, "d_in", 6, 90, 109.0, "D.17"),

    ("rigid", "triple", 3.0, "d_in", 6, 18, 0.061, "D.18"),
    ("rigid", "triple", 3.0, "d_in", 10, 54, 4.03, "D.18"),
    ("rigid", "triple", 3.0, "d_in", 8, 80, 14.8, "D.18"),
    ("rigid", "triple", 3.0, "d_in", 9, 90, 24.6, "D.18"),
]


@pytest.mark.parametrize(
    "pavement,axle_config,pt,col_kwarg,col_value,load,expected,table",
    GRID_POINTS,
    ids=[f"{gp[7]}-{gp[1]}-pt{gp[2]}-{gp[3]}{gp[4]}-load{gp[5]}" for gp in GRID_POINTS],
)
def test_grid_point_reproduces_printed_value(pavement, axle_config, pt,
                                             col_kwarg, col_value, load,
                                             expected, table):
    kwargs = {col_kwarg: col_value}
    result = load_equivalency_factor(pavement, axle_config, load, pt=pt, **kwargs)
    assert result["lef"] == pytest.approx(expected, abs=5e-4)
    assert result["table"] == f"Table {table}"
    assert "note" not in result  # every grid point is inside the printed range


def test_flagged_scan_defect_cell_documented():
    """Table D.12 (rigid, triple, pt=2.0), load=74 kips, D=9in is a scan
    defect in the source PDF (unreadable even at 600 dpi). Its stored value
    is a linear interpolation between the printed D=8in (15.4) and D=10in
    (16.2) neighbors at the same load -- NOT a transcribed printed value.
    This test documents that provenance explicitly rather than silently
    treating it as ordinary printed data."""
    d8 = load_equivalency_factor("rigid", "triple", 74, d_in=8, pt=2.0)["lef"]
    d10 = load_equivalency_factor("rigid", "triple", 74, d_in=10, pt=2.0)["lef"]
    d9 = load_equivalency_factor("rigid", "triple", 74, d_in=9, pt=2.0)["lef"]
    assert d8 == pytest.approx(15.4, abs=5e-4)
    assert d10 == pytest.approx(16.2, abs=5e-4)
    assert d9 == pytest.approx((d8 + d10) / 2, abs=5e-4)


# ============================================================================
# 2. Cross-check against the pre-existing tables.py digitized subset
# (SN=5, pt=2.5 flexible; D=9in, pt=2.5 rigid) at 10 loads each, including
# off-grid (interpolated) loads.
# ============================================================================

FLEX_SINGLE_LOADS = [3, 7, 9, 15, 21, 25, 33, 41, 47, 49]
FLEX_TANDEM_LOADS = [3, 9, 17, 25, 33, 45, 57, 67, 79, 89]
RIGID_LOADS_SINGLE = [3, 7, 9, 15, 21, 25, 33, 41, 47, 49]
RIGID_LOADS_TANDEM = [3, 9, 17, 25, 33, 45, 57, 67, 79, 89]


@pytest.mark.parametrize("load", FLEX_SINGLE_LOADS)
def test_cross_check_flexible_single_sn5(load):
    expected = tb.esal_flexible_single_axle(load, sn=5.0, pt=2.5)["lef"]
    got = load_equivalency_factor("flexible", "single", load, sn=5.0, pt=2.5)["lef"]
    assert got == pytest.approx(expected, abs=5e-3)


@pytest.mark.parametrize("load", FLEX_TANDEM_LOADS)
def test_cross_check_flexible_tandem_sn5(load):
    expected = tb.esal_flexible_tandem_axle(load, sn=5.0, pt=2.5)["lef"]
    got = load_equivalency_factor("flexible", "tandem", load, sn=5.0, pt=2.5)["lef"]
    assert got == pytest.approx(expected, abs=5e-3)


@pytest.mark.parametrize("load", RIGID_LOADS_SINGLE)
def test_cross_check_rigid_single_d9(load):
    expected = tb.esal_rigid_single_axle(load, d_in=9.0, pt=2.5)["lef"]
    got = load_equivalency_factor("rigid", "single", load, d_in=9.0, pt=2.5)["lef"]
    assert got == pytest.approx(expected, abs=5e-3)


@pytest.mark.parametrize("load", RIGID_LOADS_TANDEM)
def test_cross_check_rigid_tandem_d9(load):
    expected = tb.esal_rigid_tandem_axle(load, d_in=9.0, pt=2.5)["lef"]
    got = load_equivalency_factor("rigid", "tandem", load, d_in=9.0, pt=2.5)["lef"]
    assert got == pytest.approx(expected, abs=5e-3)


# ============================================================================
# 3. Structural invariants
# ============================================================================

class TestStructuralInvariants:
    @pytest.mark.parametrize("pavement", ["flexible", "rigid"])
    @pytest.mark.parametrize("pt", [2.0, 2.5, 3.0])
    def test_18_kip_single_axle_is_exactly_one(self, pavement, pt):
        """The 18-kip single axle load is the definitional reference (LEF=1.00
        by definition of the ESAL) -- true in every single-axle table."""
        kwargs = {"sn": 5.0} if pavement == "flexible" else {"d_in": 9.0}
        result = load_equivalency_factor(pavement, "single", 18, pt=pt, **kwargs)
        assert result["lef"] == pytest.approx(1.00, abs=1e-9)

    def test_lef_nondecreasing_with_load_every_column_every_table(self):
        """LEF must not decrease as axle load increases, within each printed
        column of each of the 18 tables. A small tolerance (5e-4, i.e. under
        the smallest printed significant digit) accounts for a documented
        handful of near-zero rounding blips in the printed source at the
        very smallest loads (magnitude ~0.0001) -- see the module
        docstring; nothing above that tiny magnitude is affected."""
        offenders = []
        for key, table in _TABLES.items():
            loads = table["loads"]
            columns = table["columns"]
            rows = table["rows"]
            for c in range(len(columns)):
                prev = None
                for i, load in enumerate(loads):
                    v = rows[i][c]
                    if prev is not None and v < prev - 5e-4:
                        offenders.append((key, columns[c], load, prev, v))
                    prev = v
        assert not offenders, offenders

    def test_lef_varies_smoothly_across_adjacent_columns(self):
        """No adjacent-column jump should be wildly out of step with its
        neighbors (guards against a column-transposition transcription
        error): for every row, the value at column i should lie within 50%
        of the average of its two neighbors.

        Restricted to cells where all three values are >= 0.5: below that
        floor, the printed AASHO Road Test curves genuinely are NOT smooth
        across SN/D at a fixed (small) load -- e.g. Table D.7 (flexible,
        single, pt=3.0), load=6 kips reads "014 030 028 018 012 010" across
        SN=1..6, a real non-monotonic bump at SN=2/3 confirmed against the
        rendered page twice, not a transcription error. That low-magnitude
        scatter is real AASHO Road Test data, not noise to be smoothed
        away."""
        offenders = []
        for key, table in _TABLES.items():
            rows = table["rows"]
            for row in rows:
                for i in range(1, len(row) - 1):
                    lo, mid, hi = row[i - 1], row[i], row[i + 1]
                    if min(abs(lo), abs(mid), abs(hi)) < 0.5:
                        continue
                    avg = (lo + hi) / 2
                    tol = 0.5 * max(abs(lo), abs(hi))
                    if abs(mid - avg) > tol:
                        offenders.append((key, row, i, mid, avg, tol))
        assert not offenders, offenders


# ============================================================================
# 4. Clamping behavior
# ============================================================================

class TestClamping:
    def test_load_below_range_clamps_and_notes(self):
        exact = load_equivalency_factor("flexible", "single", 2, sn=5.0, pt=2.5)
        below = load_equivalency_factor("flexible", "single", 0.5, sn=5.0, pt=2.5)
        assert below["lef"] == pytest.approx(exact["lef"], abs=1e-9)
        assert "note" in below
        assert "clamped" in below["note"]

    def test_load_above_range_clamps_and_notes(self):
        exact = load_equivalency_factor("rigid", "tandem", 90, d_in=9.0, pt=2.5)
        above = load_equivalency_factor("rigid", "tandem", 150, d_in=9.0, pt=2.5)
        assert above["lef"] == pytest.approx(exact["lef"], abs=1e-9)
        assert "note" in above
        assert "clamped" in above["note"]

    def test_sn_below_range_clamps_and_notes(self):
        exact = load_equivalency_factor("flexible", "single", 18, sn=1.0, pt=2.5)
        below = load_equivalency_factor("flexible", "single", 18, sn=0.2, pt=2.5)
        assert below["lef"] == pytest.approx(exact["lef"], abs=1e-9)
        assert "note" in below

    def test_sn_above_range_clamps_and_notes(self):
        exact = load_equivalency_factor("flexible", "single", 18, sn=6.0, pt=2.5)
        above = load_equivalency_factor("flexible", "single", 18, sn=9.0, pt=2.5)
        assert above["lef"] == pytest.approx(exact["lef"], abs=1e-9)
        assert "note" in above

    def test_d_in_below_range_clamps_and_notes(self):
        exact = load_equivalency_factor("rigid", "single", 18, d_in=6.0, pt=2.5)
        below = load_equivalency_factor("rigid", "single", 18, d_in=4.0, pt=2.5)
        assert below["lef"] == pytest.approx(exact["lef"], abs=1e-9)
        assert "note" in below

    def test_d_in_above_range_clamps_and_notes(self):
        exact = load_equivalency_factor("rigid", "single", 18, d_in=14.0, pt=2.5)
        above = load_equivalency_factor("rigid", "single", 18, d_in=20.0, pt=2.5)
        assert above["lef"] == pytest.approx(exact["lef"], abs=1e-9)
        assert "note" in above

    def test_interpolation_between_printed_sn_columns(self):
        """SN=4.5 should fall strictly between the SN=4 and SN=5 curves."""
        sn4 = load_equivalency_factor("flexible", "single", 30, sn=4.0, pt=2.5)["lef"]
        sn5 = load_equivalency_factor("flexible", "single", 30, sn=5.0, pt=2.5)["lef"]
        sn45 = load_equivalency_factor("flexible", "single", 30, sn=4.5, pt=2.5)["lef"]
        lo, hi = sorted((sn4, sn5))
        assert lo <= sn45 <= hi

    def test_interpolation_between_printed_loads(self):
        """A load of 19 kips should fall strictly between the 18- and 20-kip
        rows."""
        v18 = load_equivalency_factor("flexible", "single", 18, sn=5.0, pt=2.5)["lef"]
        v20 = load_equivalency_factor("flexible", "single", 20, sn=5.0, pt=2.5)["lef"]
        v19 = load_equivalency_factor("flexible", "single", 19, sn=5.0, pt=2.5)["lef"]
        assert v18 <= v19 <= v20


# ============================================================================
# 5. Validation errors
# ============================================================================

class TestValidationErrors:
    def test_unknown_pavement_type(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("semi-rigid", "single", 18, sn=5.0)

    def test_unknown_axle_config(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("flexible", "quad", 18, sn=5.0)

    def test_pt_off_grid_raises(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("flexible", "single", 18, sn=5.0, pt=2.2)

    def test_pt_2_25_raises(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("flexible", "single", 18, sn=5.0, pt=2.25)

    def test_nonpositive_axle_load_raises(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("flexible", "single", 0, sn=5.0)
        with pytest.raises(ValueError):
            load_equivalency_factor("flexible", "single", -5, sn=5.0)

    def test_flexible_requires_sn(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("flexible", "single", 18)

    def test_flexible_rejects_d_in(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("flexible", "single", 18, d_in=9.0)

    def test_rigid_requires_d_in(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("rigid", "single", 18)

    def test_rigid_rejects_sn(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("rigid", "single", 18, sn=5.0)

    def test_nonpositive_sn_raises(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("flexible", "single", 18, sn=0)
        with pytest.raises(ValueError):
            load_equivalency_factor("flexible", "single", 18, sn=-1)

    def test_nonpositive_d_in_raises(self):
        with pytest.raises(ValueError):
            load_equivalency_factor("rigid", "single", 18, d_in=0)
        with pytest.raises(ValueError):
            load_equivalency_factor("rigid", "single", 18, d_in=-1)


# ============================================================================
# 6. Output shape / echoed inputs
# ============================================================================

class TestOutputShape:
    def test_flexible_echoes_sn_not_d_in(self):
        out = load_equivalency_factor("flexible", "tandem", 18, sn=3.0, pt=2.0)
        assert out["sn"] == 3.0
        assert "d_in" not in out
        assert out["pavement_type"] == "flexible"
        assert out["axle_config"] == "tandem"
        assert out["pt"] == 2.0
        assert "reference" in out and "Table D.2" in out["reference"]

    def test_rigid_echoes_d_in_not_sn(self):
        out = load_equivalency_factor("rigid", "triple", 18, d_in=10.0, pt=3.0)
        assert out["d_in"] == 10.0
        assert "sn" not in out
        assert out["pavement_type"] == "rigid"
        assert out["axle_config"] == "triple"
        assert out["pt"] == 3.0
        assert "reference" in out and "Table D.18" in out["reference"]

    def test_case_and_whitespace_insensitive(self):
        out = load_equivalency_factor("  Flexible ", " SINGLE", 18, sn=5.0, pt=2.5)
        assert out["pavement_type"] == "flexible"
        assert out["axle_config"] == "single"
