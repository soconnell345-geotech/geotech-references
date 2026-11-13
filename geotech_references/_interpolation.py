"""Shared interpolation helpers used across DM7 chapter modules."""

import math


def _linterp(x: float, xp: list, fp: list) -> float:
    """Pure-Python piecewise linear interpolation (like numpy.interp).

    Parameters
    ----------
    x : float
        Query point. Must be a finite number.
    xp : list of float
        Breakpoints in ascending order.
    fp : list of float
        Function values at each breakpoint (same length as *xp*).

    Returns
    -------
    float
        Interpolated value, clamped at the endpoint values for
        out-of-range queries.

    Raises
    ------
    ValueError
        If ``x`` is NaN or infinite. A NaN compares false with every
        breakpoint, so it used to fall through to the table's last value
        and come back as a finite answer (GEC-12 Figure 7-16b at
        phi = NaN returned the curve's last point).
    """
    if not math.isfinite(x):
        raise ValueError(
            f"cannot interpolate at {x!r}: the input must be a finite "
            f"number (the table runs from {xp[0]} to {xp[-1]})")
    if x <= xp[0]:
        return fp[0]
    if x >= xp[-1]:
        return fp[-1]
    for i in range(len(xp) - 1):
        if xp[i] <= x <= xp[i + 1]:
            t = (x - xp[i]) / (xp[i + 1] - xp[i])
            return fp[i] + t * (fp[i + 1] - fp[i])
    return fp[-1]  # pragma: no cover
