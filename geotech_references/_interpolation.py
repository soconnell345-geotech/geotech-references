"""Shared interpolation helpers used across DM7 chapter modules."""


def _linterp(x: float, xp: list, fp: list) -> float:
    """Pure-Python piecewise linear interpolation (like numpy.interp).

    Parameters
    ----------
    x : float
        Query point.
    xp : list of float
        Breakpoints in ascending order.
    fp : list of float
        Function values at each breakpoint (same length as *xp*).

    Returns
    -------
    float
        Interpolated value, clamped at the endpoint values for
        out-of-range queries.
    """
    if x <= xp[0]:
        return fp[0]
    if x >= xp[-1]:
        return fp[-1]
    for i in range(len(xp) - 1):
        if xp[i] <= x <= xp[i + 1]:
            t = (x - xp[i]) / (xp[i + 1] - xp[i])
            return fp[i] + t * (fp[i + 1] - fp[i])
    return fp[-1]  # pragma: no cover
