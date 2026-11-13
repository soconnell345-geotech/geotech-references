"""The shared table interpolation (``_interpolation._linterp``).

2026-11-10 review (core-04): a NaN input compares false with every
breakpoint, so it fell through to ``return fp[-1]`` and 37 chart lookups
answered a NaN with the last value of their table. The values here are made
up.
"""

import math

import pytest

from geotech_references._interpolation import _linterp

XP = [10.0, 20.0, 40.0]
FP = [1.0, 3.0, 4.0]


@pytest.mark.parametrize("x,want", [
    (10.0, 1.0), (15.0, 2.0), (20.0, 3.0), (30.0, 3.5), (40.0, 4.0),
])
def test_interpolates_between_breakpoints(x, want):
    assert _linterp(x, XP, FP) == pytest.approx(want)


def test_out_of_range_is_still_the_end_value():
    # unchanged here: what a lookup does outside its printed range is each
    # package's call (the review's core-03)
    assert _linterp(5.0, XP, FP) == 1.0
    assert _linterp(50.0, XP, FP) == 4.0


@pytest.mark.parametrize("x", [math.nan, math.inf, -math.inf])
def test_a_non_finite_input_is_refused(x):
    with pytest.raises(ValueError, match="finite"):
        _linterp(x, XP, FP)


def test_a_chart_lookup_no_longer_answers_nan():
    # GEC-12 Figure 7-16b returned its curve's last point (about 475) for NaN
    from geotech_references.gec_12 import figures
    with pytest.raises(ValueError, match="finite"):
        figures.figure_7_16b_nq(math.nan)
