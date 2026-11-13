"""GEC-7 figure lookup functions.

Digitized figures from FHWA-NHI-14-007 (GEC-7), Soil Nail Walls.
Follows the DM7 pattern: private data with ``_FIG_*`` prefix, public
lookup functions with ``_linterp`` interpolation.
"""

from geotech_references._interpolation import _linterp


def _on_curve(x, pts, what):
    """Linear interpolation along one printed curve given as (x, y) points;
    a point outside the curve's printed span is refused."""
    xs = [p[0] for p in pts]
    if x < xs[0] or x > xs[-1]:
        raise ValueError(
            f"{what} is drawn only from {xs[0]:g} to {xs[-1]:g}; "
            f"{x:g} is off the curve.")
    return _linterp(x, xs, [p[1] for p in pts])


# ============================================================================
# Figure 4.3: Friction angle of cohesionless soils as a function of
# normalized overburden (Modified after Schmertmann 1975).
# FHWA-NHI-14-007 (GEC-7), p. 79 (PDF page 119).
#
# X axis: SPT N60-value (blows/300 mm or bl/ft), 0 to 60. Y axis: friction
# angle phi_s (degrees), 25 to 50. Six curves, labelled sigma'vo/Pa = 0.5,
# 1.0, 1.5, 2.0, 2.5, 3.0 (top to bottom). Each curve rises from the
# chart's bottom edge (phi 25) and ends where it is drawn: 0.5 leaves the
# top (phi 50) at N60 38.25; the others stop at N60 44.75 (1.0), 50.0
# (1.5), 55.0 (2.0 and 3.0) and 57.5 (2.5). Outside a curve the chart
# gives nothing and the lookup refuses.
#
# Read off the page rendered at 300 dpi (scripts gb02_fig43.py in the
# review's evidence folder). Scale from the chart's own lines: N60 0 and 60
# at the frame's left and right edges (the grey vertical grid lines at 10
# to 50 fall on the printed numbers); phi 25 and 50 at the bottom and top
# edges, with the right-edge ticks and the grey grid lines at 30, 35, 40,
# 45 evenly between them. The printed phi numbers on the left axis are set
# a little off their grid lines (by up to 1.7 degrees at "25"); the grid
# lines were used. Below each curve's turn the points are where the curve
# crosses a row of constant phi (the curve is near vertical there); above
# it, where it crosses a column of constant N60 (centre of the line). Where
# a curve label hides the curve the lookup runs straight across the gap:
# 0.5 between N60 22.5 and 28; 1.0 between 33 and 37; 1.5 between 40 and
# 44.75; 2.0 between 43 and 49; 2.5 between 45.5 and 50.25. phi 25 is the
# chart's bottom edge (N60 read 3 px above it).
# ============================================================================

_FIG_4_3_REFERENCE = ("FHWA-NHI-14-007 (GEC-7), Figure 4.3 Friction angle of "
                      "cohesionless soils as a function of normalized "
                      "overburden (Modified after Schmertmann 1975), p. 79")

# sigma'vo/Pa: [(N60, phi deg), ...] along the printed curve
_FIG_4_3_CURVES = {
    0.5: [(2.86, 25.0), (3.27, 26.0), (3.41, 27.0), (3.82, 28.0),
          (4.23, 29.0), (5.05, 31.0), (5.73, 32.0), (6.55, 33.0),
          (7.23, 34.0), (8.86, 36.0), (9.82, 37.0), (11, 38.12),
          (12, 38.80), (14, 40.36), (16, 41.60), (18, 42.73), (19, 43.27),
          (21, 44.29), (22, 44.65), (22.5, 44.76), (28, 46.93), (29, 47.29),
          (31, 47.92), (33, 48.58), (35, 49.10), (37, 49.66), (38, 49.85),
          (38.25, 49.90)],
    1.0: [(3.82, 25.0), (4.36, 26.0), (4.91, 27.0), (5.32, 28.0),
          (6.00, 29.0), (7.36, 31.0), (8.05, 32.0), (9.14, 33.0),
          (10.09, 34.0), (11, 34.91), (12, 35.68), (14, 37.20), (16, 38.55),
          (18, 39.75), (19, 40.27), (21, 41.21), (22, 41.64), (23, 42.05),
          (24, 42.46), (25, 42.84), (26, 43.20), (27, 43.61), (28, 43.99),
          (29, 44.31), (31, 44.99), (33, 45.62), (37, 46.75), (38, 46.97),
          (39, 47.24), (40, 47.47), (41, 47.67), (42, 47.92), (43, 48.15),
          (44, 48.42), (44.75, 48.60)],
    1.5: [(4.91, 25.0), (5.52, 26.0), (6.14, 27.0), (6.82, 28.0),
          (7.64, 29.0), (9.27, 31.0), (10.30, 32.0), (11, 32.59),
          (12, 33.30), (14, 34.78), (16, 36.09), (18, 37.22), (19, 37.73),
          (21, 38.73), (22, 39.07), (23, 39.52), (24, 39.97), (25, 40.29),
          (26, 40.70), (27, 41.08), (28, 41.42), (29, 41.73), (31, 42.37),
          (33, 42.95), (34, 43.22), (35, 43.50), (36, 43.81), (37, 44.04),
          (38, 44.29), (39, 44.58), (40, 44.81), (44.75, 45.89),
          (45.5, 45.98), (46, 46.14), (47, 46.34), (48, 46.52), (49, 46.73),
          (50, 46.91)],
    2.0: [(6.14, 25.0), (6.95, 26.0), (7.64, 27.0), (8.59, 28.0),
          (9.55, 29.0), (11, 30.42), (12, 31.17), (14, 32.70), (16, 34.01),
          (18, 35.07), (19, 35.61), (21, 36.63), (22, 36.99), (23, 37.47),
          (24, 37.92), (25, 38.26), (26, 38.66), (27, 39.02), (28, 39.36),
          (29, 39.63), (31, 40.33), (33, 40.94), (34, 41.19), (35, 41.44),
          (36, 41.78), (37, 42.01), (38, 42.28), (39, 42.55), (40, 42.77),
          (41, 43.00), (42, 43.27), (43, 43.45), (49, 44.74), (50, 44.90),
          (51, 45.14), (52, 45.30), (53, 45.46), (54, 45.66), (55, 45.84)],
    2.5: [(7.84, 25.0), (8.45, 26.0), (9.41, 27.0), (10.50, 28.0),
          (11, 28.57), (12, 29.30), (14, 30.85), (16, 32.05), (18, 33.31),
          (19, 33.81), (21, 34.80), (22, 35.25), (23, 35.70), (24, 36.09),
          (25, 36.47), (26, 36.83), (27, 37.17), (28, 37.60), (29, 37.90),
          (31, 38.57), (33, 39.21), (34, 39.50), (35, 39.75), (36, 40.02),
          (37, 40.24), (38, 40.54), (39, 40.83), (40, 41.08), (41, 41.28),
          (42, 41.53), (43, 41.78), (44, 41.96), (45, 42.23), (45.5, 42.30),
          (50.25, 43.29), (51, 43.43), (52, 43.61), (53, 43.83), (54, 44.02),
          (55, 44.17), (56, 44.33), (57.25, 44.56), (57.5, 44.60)],
    3.0: [(9.07, 25.0), (9.95, 26.0), (11, 26.87), (12, 27.70),
          (14, 29.22), (16, 30.44), (18, 31.62), (19, 32.09), (21, 33.08),
          (22, 33.51), (23, 33.99), (24, 34.39), (25, 34.82), (26, 35.12),
          (27, 35.52), (28, 35.84), (29, 36.20), (31, 36.83), (33, 37.47),
          (34, 37.77), (35, 38.03), (36, 38.32), (37, 38.55), (38, 38.84),
          (39, 39.07), (40, 39.36), (41, 39.52), (42, 39.81), (43, 40.04),
          (44, 40.27), (45, 40.47), (46, 40.67), (47, 40.85), (48, 41.10),
          (49, 41.31), (50, 41.49), (51, 41.69), (52, 41.87), (53, 42.07),
          (54, 42.25), (55, 42.37)],
}

_FIG_4_3_SIGMA_RATIOS = sorted(_FIG_4_3_CURVES)


def figure_4_3_friction_angle_spt(n60: float,
                                  sigma_v_ratio: float) -> float:
    """Friction angle phi_s (degrees) of a cohesionless soil from SPT N60 and sigma'vo/Pa, read off GEC-7 Figure 4.3 (FHWA-NHI-14-007, p. 79; modified after Schmertmann 1975); a point the six printed curves do not cover is refused.

    Figure 4.3 draws six curves, sigma'vo/Pa = 0.5, 1.0, 1.5, 2.0, 2.5 and
    3.0, on axes N60 0 to 60 and phi 25 to 50 degrees. Each curve starts at
    phi 25 (N60 2.9 for 0.5 up to 9.1 for 3.0) and ends where it is drawn:
    0.5 leaves the top of the chart at N60 38.25; 1.0 ends at 44.75, 1.5 at
    50, 2.0 and 3.0 at 55, 2.5 at 57.5. At a stress ratio between two
    curves the angle is interpolated linearly between them at the same
    N60 (not printed); both curves must be drawn at that N60.

    Parameters
    ----------
    n60 : float
        SPT blow count corrected for 60 % hammer efficiency (blows/ft).
    sigma_v_ratio : float
        Vertical effective overburden stress over atmospheric pressure,
        sigma'vo/Pa, 0.5 to 3.0.

    Returns
    -------
    float
        Friction angle phi_s in degrees, to 0.1 degree.

    Raises
    ------
    ValueError
        If sigma_v_ratio is outside 0.5 to 3.0, or n60 is off the curve(s)
        used (below phi 25 or past a curve's end).
    """
    if sigma_v_ratio < 0.5 or sigma_v_ratio > 3.0:
        raise ValueError(
            f"Figure 4.3 (GEC-7 p. 79) draws sigma'vo/Pa = 0.5 to 3.0; "
            f"got {sigma_v_ratio}.")
    ratios = _FIG_4_3_SIGMA_RATIOS
    lo = max(r for r in ratios if r <= sigma_v_ratio)
    hi = min(r for r in ratios if r >= sigma_v_ratio)
    phi_lo = _on_curve(n60, _FIG_4_3_CURVES[lo],
                       f"Figure 4.3 (GEC-7 p. 79) curve sigma'vo/Pa = {lo} "
                       f"(N60)")
    if hi == lo:
        return round(phi_lo, 1)
    phi_hi = _on_curve(n60, _FIG_4_3_CURVES[hi],
                       f"Figure 4.3 (GEC-7 p. 79) curve sigma'vo/Pa = {hi} "
                       f"(N60)")
    t = (sigma_v_ratio - lo) / (hi - lo)
    return round(phi_lo + t * (phi_hi - phi_lo), 1)


# ============================================================================
# Figure 5.11: Bearing capacity factor (Nc) for determining basal heave.
# Modified after Terzaghi et al. (1996) and Sabatini et al. (1999).
# FHWA-NHI-14-007 (GEC-7), p. 124 (PDF page 164).
#
# X axis: H/Be, 0 to 5 (H = excavation depth, Be = excavation width; on
# the chart: "H/Be ~ 0 (wide excavations)"). Y axis: Nc, 4 to 10. Three
# curves: Be/Le = 1 (Square excav. on plan view), Be/Le = 0.5, Be/Le = 0
# (Long, rectang. excav.), Le = excavation length.
#
# Read off the page rendered at 300 dpi (gb03_fig511.py in the review's
# evidence folder): H/Be 0 and 5 at the frame's left and right edges (ticks
# every 0.5), Nc 4 and 10 at the bottom and top edges (ticks every 1).
# Points are the centre of each curve in a column of constant H/Be; the
# value at H/Be 0 is the one read 5 px inside the left edge (H/Be 0.02),
# and at 5 the one read at 4.97. The Be/Le = 0.5 curve is hidden by a label
# leader at H/Be 2.9 (no point there).
# ============================================================================

_FIG_5_11_REFERENCE = ("FHWA-NHI-14-007 (GEC-7), Figure 5.11 Bearing capacity "
                       "factor (Nc) for determining basal heave, p. 124")

_FIG_5_11_H_BE = [0.0, 0.1, 0.25, 0.4, 0.6, 0.75, 0.9, 1.1, 1.25, 1.4, 1.6,
                  1.75, 1.9, 2.1, 2.25, 2.4, 2.6, 2.75, 3.1, 3.25, 3.4, 3.6,
                  3.75, 3.9, 4.1, 4.25, 4.4, 4.6, 4.75, 4.9, 5.0]

# Nc at each H/Be above, for each printed Be/Le curve
_FIG_5_11_NC = {
    0.0: [5.20, 5.31, 5.50, 5.70, 5.92, 6.09, 6.23, 6.40, 6.52, 6.63, 6.76,
          6.84, 6.93, 7.03, 7.09, 7.14, 7.21, 7.26, 7.35, 7.37, 7.40, 7.43,
          7.45, 7.46, 7.47, 7.48, 7.48, 7.47, 7.47, 7.46, 7.45],
    0.5: [5.69, 5.82, 6.05, 6.27, 6.53, 6.70, 6.86, 7.04, 7.17, 7.29, 7.42,
          7.51, 7.60, 7.71, 7.77, 7.84, 7.90, 7.95, 8.04, 8.07, 8.09, 8.12,
          8.13, 8.15, 8.16, 8.16, 8.16, 8.16, 8.15, 8.14, 8.14],
    1.0: [6.19, 6.33, 6.58, 6.82, 7.11, 7.29, 7.46, 7.66, 7.80, 7.92, 8.08,
          8.19, 8.28, 8.40, 8.47, 8.54, 8.63, 8.69, 8.79, 8.83, 8.87, 8.90,
          8.92, 8.94, 8.95, 8.96, 8.96, 8.96, 8.95, 8.96, 8.96],
}

_FIG_5_11_BE_LE = [0.0, 0.5, 1.0]


def figure_5_11_basal_heave_nc(h_be: float,
                               be_le: float = 0.0) -> float:
    """Bearing capacity factor Nc for basal heave, read off GEC-7 Figure 5.11 (FHWA-NHI-14-007, p. 124; modified after Terzaghi et al. 1996 and Sabatini et al. 1999) for H/Be 0 to 5 and Be/Le 0 to 1.

    The figure draws three curves of Nc against H/Be (excavation depth over
    excavation width): Be/Le = 0 (long, rectangular excavation), 0.5 and 1
    (square on plan), Le being the excavation length. At H/Be = 0 they
    start at 5.2, 5.7 and 6.2; at H/Be = 5 they reach 7.5, 8.1 and 9.0.
    Between the printed Be/Le curves Nc is interpolated linearly in Be/Le
    (not printed). Nc is the factor for cohesion of Eqs. 5.10 and 5.11,
    Rs = Su Nc B'e or Su Nc DB (p. 122); for very long walls and very wide
    excavations (Be/Le ~ 0, H/Be ~ 0) p. 122 says Nc = 5.14 can
    conservatively be assumed.

    Parameters
    ----------
    h_be : float
        H/Be, 0 to 5.
    be_le : float
        Be/Le, 0 (long excavation, the default and the lowest Nc) to 1
        (square).

    Returns
    -------
    float
        Bearing capacity factor Nc (dimensionless), to 0.01.

    Raises
    ------
    ValueError
        If h_be or be_le is outside the chart.
    """
    if h_be < 0 or h_be > 5.0:
        raise ValueError(
            f"Figure 5.11 (GEC-7 p. 124) is drawn for H/Be 0 to 5; got {h_be}")
    if be_le < 0 or be_le > 1.0:
        raise ValueError(
            f"Figure 5.11 (GEC-7 p. 124) draws Be/Le = 0, 0.5 and 1; got "
            f"{be_le}")

    nc_at_ratios = [_linterp(h_be, _FIG_5_11_H_BE, _FIG_5_11_NC[ratio])
                    for ratio in _FIG_5_11_BE_LE]
    return round(_linterp(be_le, _FIG_5_11_BE_LE, nc_at_ratios), 2)
