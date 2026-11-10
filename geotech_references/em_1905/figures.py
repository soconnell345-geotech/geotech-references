"""EM 1110-1-1905 (2025) figures that print their values as a table.

Only Figure 7-16 does: beside its curve of average degree of consolidation
against the time factor it prints the pairs it is drawn from. The other
charts (bearing capacity factors, the influence charts of Chapter 6, the
shape factors of Figure 7-11) are not digitized here; read them off the
rendered page through the figure catalog.
"""

from __future__ import annotations

_REF = "EM 1110-1-1905 (2025)"

# (U percent, Tv) as printed in the table on Figure 7-16, p. 185; U = 100
# percent is printed with Tv = infinity and is not interpolated to.
_FIG_7_16 = (
    (0.0, 0.0), (10.0, 0.008), (20.0, 0.031), (30.0, 0.071),
    (40.0, 0.126), (50.0, 0.197), (60.0, 0.287), (70.0, 0.403),
    (80.0, 0.567), (90.0, 0.848), (93.1, 1.000), (95.0, 1.163),
    (98.0, 1.500), (99.4, 2.000),
)


def figure_7_16_time_factor(U_percent: float | None,
                            T_v: float | None) -> dict:
    """Time factor for vertical drainage against the average degree of
    consolidation, from the table printed on Figure 7-16 (initial excess
    pore pressure constant or linear with depth). Give one of U_percent or
    T_v and get the other. A printed pair comes back exactly; between
    printed pairs the value is interpolated linearly and marked
    ``interpolated`` True (the curve is not linear, so the interpolated
    value is approximate: read the chart for more).

    Print check (Figure 7-16, p. 185, read off the rendered page):

        U%   0     10     20     30     40     50     60
        Tv   0     0.008  0.031  0.071  0.126  0.197  0.287
        U%   70    80     90     93.1   95.0   98.0   99.4   100.0
        Tv   0.403 0.567  0.848  1.000  1.163  1.500  2.000  ∞
        here the same pairs; U = 100 percent is not returned

    Parameters
    ----------
    U_percent : float or None
        Average degree of consolidation, percent (0 to 99.4); None when
        T_v is given.
    T_v : float or None
        Time factor (0 to 2.000); None when U_percent is given.

    Returns
    -------
    dict
        U_percent, T_v, interpolated, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If both or neither are given, or the value is outside the printed
        table (U 0 to 99.4 percent, Tv 0 to 2.000).
    """
    if (U_percent is None) == (T_v is None):
        raise ValueError("give one of U_percent or T_v")
    if U_percent is not None:
        x, xi, yi = float(U_percent), 0, 1
        name, hi = "U_percent", _FIG_7_16[-1][0]
    else:
        x, xi, yi = float(T_v), 1, 0
        name, hi = "T_v", _FIG_7_16[-1][1]
    if not 0 <= x <= hi:
        raise ValueError(f"{name} = {x}: the table on Figure 7-16 runs 0 to "
                         f"{hi} (U = 100 percent at Tv = infinity)")
    y, interp = None, False
    for a, b in zip(_FIG_7_16, _FIG_7_16[1:]):
        if x == a[xi]:
            y = a[yi]
            break
        if x == b[xi]:
            y = b[yi]
            break
        if a[xi] < x < b[xi]:
            y = a[yi] + (b[yi] - a[yi]) * (x - a[xi]) / (b[xi] - a[xi])
            interp = True
            break
    u, t = (x, y) if xi == 0 else (y, x)
    return {"U_percent": u, "T_v": t, "interpolated": interp,
            "units": {"U_percent": "percent", "T_v": "dimensionless"},
            "source": f"{_REF} Figure 7-16, p. 185",
            "valid_for": ("One-dimensional consolidation, vertical drainage, "
                          "initial excess pore pressure constant or linear "
                          "with depth."),
            "notes": ("Printed pairs exact; between them linear "
                      "interpolation of a curved relation (approximate).")}
