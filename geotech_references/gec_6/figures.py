"""GEC-6 figure lookup functions.

Digitized figures from FHWA-SA-02-054 (GEC-6), Shallow Foundations.
Follows the DM7 pattern: private data with ``_FIG_*`` prefix, public
lookup functions with ``_linterp`` interpolation.

Every curve below was read off the rendered PDF page (300 dpi, calibrated
on the chart's own grid lines); the points read and the page are given
above each data block.
"""

from geotech_references._interpolation import _linterp


# ============================================================================
# Figure 4-1: Correlation Between Relative Density and SPT Resistance
# (NAVFAC, 1986a, after Gibbs & Holtz); the chart itself is marked "(AFTER
# USBR EARTH MANUAL, 1960)". FHWA-SA-02-054 (GEC-6), p. 34 (PDF page 40).
#
# X axis: SPT N, 0 to 80 blows/ft. Y axis: vertical effective stress, 0 to
# 6 k/ft2 downward (1 k/ft2 = 47.88 kPa, printed under the chart). Nine
# curves labelled with the relative density Dr = 15, 40, 50, 60, 70, 80, 85,
# 90 and 100 %.
#
# N at each curve, read where the curve crosses each stress level (the
# crossing of the curve's centre line, to 0.1 blow; where a label or a grid
# line hides a curve the value is the mean of the readings just above and
# below it). The 100 % curve leaves the chart (N = 80) at 5.15 k/ft2.
#
#  k/ft2   15    40    50    60    70    80    85    90   100
#  0.25   1.2   2.6   4.7   6.9  10.4  13.4  15.1  17.1  21.9
#  0.5    1.7   3.4   5.7   8.1  11.7  15.2  16.9  19.3  24.7
#  1.0    2.5   4.8   7.4  10.1  14.5  18.7  20.9  24.0  30.3
#  1.5    3.0   5.9   8.9  12.1  16.9  22.1  25.0  28.7  35.9
#  2.0    3.5   6.8  10.1  13.9  19.3  25.3  28.9  33.3  41.5
#  2.5    3.9   7.6  11.3  15.4  21.6  28.5  32.7  37.8  47.2
#  3.0    4.2   8.1  12.4  17.1  23.8  31.8  36.3  42.1  53.5
#  3.5    4.4   8.7  13.3  18.6  26.0  35.0  40.0  46.5  59.5
#  4.0    4.5   9.2  14.2  20.1  28.2  38.2  43.9  50.7  65.6
#  4.5    4.8   9.7  14.9  21.7  30.1  41.5  47.5  54.9  72.0
#  5.0    4.9  10.2  15.6  23.0  32.3  44.8  51.4  59.2  78.1
#  5.5    5.0  10.5  16.3  24.3  34.2  48.2  55.1  63.5    -
#  6.0    5.0  10.8  17.0  25.6  36.2  51.6  58.9  68.0    -
# ============================================================================

_FIG_4_1_REFERENCE = ("FHWA-SA-02-054 (GEC-6), Figure 4-1 Correlation Between "
                      "Relative Density and SPT Resistance (NAVFAC, 1986a, "
                      "after Gibbs & Holtz), p. 34")
_KSF_TO_KPA = 47.88

_FIG_4_1_DR = [15, 40, 50, 60, 70, 80, 85, 90, 100]
_FIG_4_1_STRESS_KSF = [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5,
                       5.0, 5.5, 6.0]
# one row per stress level; one column per Dr curve
_FIG_4_1_N_TABLE = [
    [1.2, 2.6, 4.7, 6.9, 10.4, 13.4, 15.1, 17.1, 21.9],
    [1.7, 3.4, 5.7, 8.1, 11.7, 15.2, 16.9, 19.3, 24.7],
    [2.5, 4.8, 7.4, 10.1, 14.5, 18.7, 20.9, 24.0, 30.3],
    [3.0, 5.9, 8.9, 12.1, 16.9, 22.1, 25.0, 28.7, 35.9],
    [3.5, 6.8, 10.1, 13.9, 19.3, 25.3, 28.9, 33.3, 41.5],
    [3.9, 7.6, 11.3, 15.4, 21.6, 28.5, 32.7, 37.8, 47.2],
    [4.2, 8.1, 12.4, 17.1, 23.8, 31.8, 36.3, 42.1, 53.5],
    [4.4, 8.7, 13.3, 18.6, 26.0, 35.0, 40.0, 46.5, 59.5],
    [4.5, 9.2, 14.2, 20.1, 28.2, 38.2, 43.9, 50.7, 65.6],
    [4.8, 9.7, 14.9, 21.7, 30.1, 41.5, 47.5, 54.9, 72.0],
    [4.9, 10.2, 15.6, 23.0, 32.3, 44.8, 51.4, 59.2, 78.1],
    [5.0, 10.5, 16.3, 24.3, 34.2, 48.2, 55.1, 63.5, None],
    [5.0, 10.8, 17.0, 25.6, 36.2, 51.6, 58.9, 68.0, None],
]
# the 100 % curve reaches the chart's right edge, N = 80, at this stress
_FIG_4_1_100_ENDS_KSF = 5.15


def _fig_4_1_n_at(curve: int, sigma_ksf: float):
    """N on one Dr curve at a stress; None where the curve is off the chart."""
    xs, ys = [], []
    for stress, row in zip(_FIG_4_1_STRESS_KSF, _FIG_4_1_N_TABLE):
        if row[curve] is not None:
            xs.append(stress)
            ys.append(row[curve])
    if curve == len(_FIG_4_1_DR) - 1:
        xs.append(_FIG_4_1_100_ENDS_KSF)
        ys.append(80.0)
    if sigma_ksf > xs[-1]:
        return None
    return _linterp(sigma_ksf, xs, ys)


def figure_4_1_relative_density_spt(n_value: float,
                                    sigma_v_kpa: float) -> float:
    """Relative density Dr (percent) of sand from the SPT blow count N and the vertical effective stress, read from GEC-6 Figure 4-1 (FHWA-SA-02-054, p. 34; NAVFAC 1986a, after Gibbs & Holtz): linear between the chart's curves for Dr = 15, 40, 50, 60, 70, 80, 85, 90 and 100 %, at stresses of 12 to 287 kPa (0.25 to 6 k/ft2); a point left of the 15 % curve or right of the 100 % curve is refused.

    The chart is entered with N as measured with a rope and cathead (60
    percent efficiency; correct other hammers by Eq. 4-1, p. 33) and NOT
    corrected for overburden: the chart is itself a function of the
    effective overburden stress.

    The chart draws its curves from 0 k/ft2, the top of the chart. They are
    read here from 0.25 k/ft2 (12 kPa) down, so a stress under 12 kPa is
    refused by this library, not by the chart.

    Parameters
    ----------
    n_value : float
        SPT blow count N (blows per 0.3 m / 1 ft), at 60 percent hammer
        efficiency, not corrected for overburden.
    sigma_v_kpa : float
        Vertical effective stress in kPa, 12 to 287 kPa (the chart's 0.25
        to 6 k/ft2; 1 k/ft2 = 47.88 kPa).

    Returns
    -------
    float
        Relative density [percent], 15 to 100.

    Raises
    ------
    ValueError
        If the stress is outside 0.25 to 6 k/ft2 (below 0.25 the refusal
        is the library's: the curves are drawn there), or N at that stress is
        left of the chart's 15 % curve or right of its 100 % curve (or,
        above 5.15 k/ft2 where the 100 % curve has left the chart, right
        of the 90 % curve).

    References
    ----------
    FHWA-SA-02-054 (GEC-6), Figure 4-1, printed p. 34 (pdf_page_index 39).
    """
    if n_value < 0:
        raise ValueError(f"n_value must be non-negative, got {n_value}")
    sigma_ksf = sigma_v_kpa / _KSF_TO_KPA
    lo, hi = _FIG_4_1_STRESS_KSF[0], _FIG_4_1_STRESS_KSF[-1]
    # 12 and 287 kPa are the rounded ends of the range given to the caller
    if sigma_v_kpa < 11.97 or sigma_v_kpa > 287.3:
        raise ValueError(
            f"sigma_v_kpa = {sigma_v_kpa} is outside GEC-6 Figure 4-1 as "
            f"read here: 12 to 287 kPa ({lo} to {hi:g} k/ft2). The chart "
            "is plotted from 0 to 6 k/ft2; its curves are drawn above 0.25 "
            "k/ft2 but are not read there by this library.")
    sigma_ksf = min(max(sigma_ksf, lo), hi)

    n_curves = [_fig_4_1_n_at(i, sigma_ksf) for i in range(len(_FIG_4_1_DR))]
    if n_value < n_curves[0]:
        raise ValueError(
            f"N = {n_value} at {sigma_v_kpa} kPa is left of the lowest "
            f"curve of GEC-6 Figure 4-1, Dr = 15 % (N = {n_curves[0]:.1f} "
            "at this stress). The chart gives no relative density below "
            "15 %.")
    drs = [float(d) for d, n in zip(_FIG_4_1_DR, n_curves) if n is not None]
    ns = [n for n in n_curves if n is not None]
    if n_value > ns[-1]:
        if len(ns) < len(n_curves):
            raise ValueError(
                f"N = {n_value} at {sigma_v_kpa} kPa is right of the 90 % "
                f"curve of GEC-6 Figure 4-1 (N = {ns[-1]:.1f} at this "
                "stress), and above 5.15 k/ft2 (247 kPa) the 100 % curve "
                "lies beyond N = 80, the edge of the chart. The chart "
                "cannot be read here.")
        raise ValueError(
            f"N = {n_value} at {sigma_v_kpa} kPa is right of the highest "
            f"curve of GEC-6 Figure 4-1, Dr = 100 % (N = {ns[-1]:.1f} at "
            "this stress). The chart gives no relative density above "
            "100 %.")
    return _linterp(n_value, ns, drs)


# ============================================================================
# Figure 5-19: Bearing Capacity Index versus Corrected SPT (Cheney &
# Chassie, 2000, modified from Hough, 1959). FHWA-SA-02-054 (GEC-6), p. 91
# (PDF page 97).
#
# X axis: corrected SPT value N', 0 to 100 ("N' - SPT (N) Value Corrected
# for Overburden Pressure"). Y axis: bearing capacity index C', 0 to 300.
# Six curves, named on the chart, from the highest C' to the lowest:
#   Clean uniform medium SAND
#   Well graded silty SAND & GRAVEL
#   Clean well graded fine to coarse SAND
#   Well graded fine to medium silty SAND
#   Sandy CLAY
#   Inorganic SILT
# Every curve starts at N' = 4. The three upper curves leave the top of the
# chart (C' = 300) at N' = 56.0, 75.2 and 89.4; the three lower ones reach
# N' = 100.
#
# C' read at N' = 4, every 5 from 5, and the end of each curve (the curve's
# centre line; whole numbers, the chart's grid is 5 C' by 2 N'):
#
#   N'   unif.  silty sand  fine to   silty  sandy  inorg.
#        sand   & gravel    coarse    sand   clay   silt
#    4     48      42         38       34     29     22
#    5     50      44         39       35     30     24
#   10     60      54         49       42     36     30
#   15     73      65         59       50     43     36
#   20     88      77         69       59     51     42
#   25    106      89         80       68     58     48
#   30    127     103         90       77     65     55
#   35    151     117        102       87     73     62
#   40    176     132        114       97     80     69
#   45    208     150        127      108     87     76
#   50    245     169        141      118     95     84
#   55    290     190        156      130    103     91
#   60    (300    212        171      141    111     99
#   65     at     238        188      153    119    106
#   70    56.0)   266        207      165    128    114
#   75            299        228      178    138    122
#   80        (300 at 75.2)  250      191    148    129
#   85                       275      205    158    136
#   90                  (300 at 89.4) 220    168    144
#   95                                236    179    152
#  100                                253    191    161
#
# GEC-6's own example (p. B-28, PDF page 186) enters the chart "with N' = 32
# for well-graded silty sand and gravel" and reads C' = 110; the points
# above give 109.
# ============================================================================

_FIG_5_19_REFERENCE = ("FHWA-SA-02-054 (GEC-6), Figure 5-19 Bearing Capacity "
                       "Index versus Corrected SPT (Cheney & Chassie, 2000, "
                       "modified from Hough, 1959), p. 91")

_FIG_5_19_N5 = list(range(5, 101, 5))

# key: (soil type as printed on the chart, N' points, C' at those points)
_FIG_5_19_CURVES = {
    "clean_uniform_medium_sand": (
        "Clean uniform medium SAND",
        [4] + _FIG_5_19_N5[:11] + [56.0],
        [48, 50, 60, 73, 88, 106, 127, 151, 176, 208, 245, 290, 300],
    ),
    "well_graded_silty_sand_and_gravel": (
        "Well graded silty SAND & GRAVEL",
        [4] + _FIG_5_19_N5[:15] + [75.2],
        [42, 44, 54, 65, 77, 89, 103, 117, 132, 150, 169, 190, 212, 238, 266,
         299, 300],
    ),
    "clean_well_graded_fine_to_coarse_sand": (
        "Clean well graded fine to coarse SAND",
        [4] + _FIG_5_19_N5[:17] + [89.4],
        [38, 39, 49, 59, 69, 80, 90, 102, 114, 127, 141, 156, 171, 188, 207,
         228, 250, 275, 300],
    ),
    "well_graded_fine_to_medium_silty_sand": (
        "Well graded fine to medium silty SAND",
        [4] + _FIG_5_19_N5,
        [34, 35, 42, 50, 59, 68, 77, 87, 97, 108, 118, 130, 141, 153, 165,
         178, 191, 205, 220, 236, 253],
    ),
    "sandy_clay": (
        "Sandy CLAY",
        [4] + _FIG_5_19_N5,
        [29, 30, 36, 43, 51, 58, 65, 73, 80, 87, 95, 103, 111, 119, 128, 138,
         148, 158, 168, 179, 191],
    ),
    "inorganic_silt": (
        "Inorganic SILT",
        [4] + _FIG_5_19_N5,
        [22, 24, 30, 36, 42, 48, 55, 62, 69, 76, 84, 91, 99, 106, 114, 122,
         129, 136, 144, 152, 161],
    ),
}

# Other names of ONE curve. 'sand', 'silty sand', 'well graded sand',
# 'coarse sand' and 'fine to medium sand' fit no single curve and are
# refused.
_FIG_5_19_ALIASES = {
    "silt": "inorganic_silt",
    "uniform_medium_sand": "clean_uniform_medium_sand",
    "clean_uniform_sand": "clean_uniform_medium_sand",
    "uniform_sand": "clean_uniform_medium_sand",
    "well_graded_silty_sand_gravel": "well_graded_silty_sand_and_gravel",
    "well_graded_sand_and_gravel": "well_graded_silty_sand_and_gravel",
    "well_graded_sand_gravel": "well_graded_silty_sand_and_gravel",
    "silty_sand_and_gravel": "well_graded_silty_sand_and_gravel",
    "silty_sand_gravel": "well_graded_silty_sand_and_gravel",
    "sand_and_gravel": "well_graded_silty_sand_and_gravel",
    "clean_well_graded_sand": "clean_well_graded_fine_to_coarse_sand",
    "well_graded_fine_to_coarse_sand": "clean_well_graded_fine_to_coarse_sand",
    "clean_fine_to_coarse_sand": "clean_well_graded_fine_to_coarse_sand",
    "fine_to_coarse_sand": "clean_well_graded_fine_to_coarse_sand",
    "fine_to_medium_silty_sand": "well_graded_fine_to_medium_silty_sand",
    "well_graded_silty_sand_fine_to_medium":
        "well_graded_fine_to_medium_silty_sand",
}


def figure_5_19_hough_bearing_capacity_index(n_prime: float,
                                             soil_type: str
                                             ) -> float:
    """Bearing capacity index C' (dimensionless) of the Hough settlement method at the corrected SPT value N', read from the curve of one soil type in GEC-6 Figure 5-19 (FHWA-SA-02-054, p. 91; Cheney & Chassie 2000, modified from Hough 1959): clean uniform medium sand, well graded silty sand and gravel, clean well graded fine to coarse sand, well graded fine to medium silty sand, sandy clay, or inorganic silt.

    C' goes into Eq. 5-24 (p. 90): delta_H = H0 (1/C') log10((sigma'vo +
    delta_sigma_v) / sigma'vo), the settlement of one layer. N' is the SPT
    N-value corrected for overburden pressure (Figure 5-18). Every curve
    starts at N' = 4; the clean uniform medium sand curve leaves the chart
    (C' = 300) at N' = 56, the silty sand and gravel curve at N' = 75 and
    the fine to coarse sand curve at N' = 89. Outside its curve no value
    is returned. Read to about 1 C'.

    Parameters
    ----------
    n_prime : float
        SPT N-value corrected for overburden pressure, N', from 4 to the
        end of the soil type's curve (56, 75, 89 or 100).
    soil_type : str
        One curve of the chart: 'clean_uniform_medium_sand',
        'well_graded_silty_sand_and_gravel',
        'clean_well_graded_fine_to_coarse_sand',
        'well_graded_fine_to_medium_silty_sand', 'sandy_clay',
        'inorganic_silt'. 'sand', 'silty sand' or 'coarse sand' alone fits
        no single curve and is refused.

    Returns
    -------
    float
        Bearing capacity index C' [no unit printed].

    Raises
    ------
    ValueError
        If soil_type does not name one curve, or n_prime is outside that
        curve.

    References
    ----------
    FHWA-SA-02-054 (GEC-6), Figure 5-19, printed p. 91 (pdf_page_index 96).
    """
    key = soil_type.lower().strip().replace("&", "and")
    key = "_".join(key.replace("-", " ").replace("_", " ").split())
    key = _FIG_5_19_ALIASES.get(key, key)

    if key not in _FIG_5_19_CURVES:
        raise ValueError(
            f"'{soil_type}' does not name one curve of GEC-6 Figure 5-19 "
            "(p. 91). Curves (key: soil type as printed): "
            + "; ".join(f"{k}: {v[0]}" for k, v in _FIG_5_19_CURVES.items())
        )
    name, ns, cs = _FIG_5_19_CURVES[key]
    if n_prime < ns[0] or n_prime > ns[-1]:
        end = ("where it leaves the chart at C' = 300" if cs[-1] == 300
               else "the edge of the chart")
        raise ValueError(
            f"n_prime = {n_prime} is outside the '{name}' curve of GEC-6 "
            f"Figure 5-19, which runs from N' = {ns[0]} to N' = {ns[-1]:g} "
            f"({end}). The chart gives no C' here.")
    return _linterp(n_prime, ns, [float(c) for c in cs])


# ============================================================================
# Figure 4-2: Correlation Between Relative Density, Material Classification
# and Angle of Internal Friction for Coarse-Grained Soils (NAVFAC, 1986a).
# FHWA-SA-02-054 (GEC-6), p. 35 (PDF page 41).
#
# X axis: dry unit weight, 80 to 150 pcf below the chart and 12.6 to 23.6
# kN/m3 above it. Y axis: angle of internal friction phi', 20 to 45
# degrees. The chart is a mesh: six solid lines rising to the right (the
# material types; the circled labels ML, SW, GP and GW sit on the first,
# fourth, fifth and sixth, and "SM and SP in this range" is written between
# ML and SW) crossed by five dashed lines for relative density 0, 25, 50,
# 75 and 100 %. Outside the mesh the chart gives nothing. On the chart:
# "phi' obtained from effective stress failure envelopes; approximate
# correlation is for cohesionless materials without plastic fines". Note
# under the chart: "Use caution in the shaded portion of the chart due to
# the potential for unreliable SPT N-values in gravels" (the shaded portion
# is between the GP and GW lines above about 50 % relative density, and
# beyond).
#
# The 30 points where a solid line meets a dashed line (dry unit weight in
# pcf, phi' in degrees), from straight lines fitted to each dashed line and
# to each solid line near the crossing:
#
#   Dr     line 1 (ML)   line 2        line 3        line 4 (SW)   line 5 (GP)   line 6 (GW)
#     0    78.9, 26.1    87.0, 26.5    95.0, 26.8    102.1, 27.2   109.0, 27.5   117.8, 27.9
#    25    83.7, 28.7    92.1, 29.2    100.1, 29.8   107.0, 30.3   114.3, 30.8   123.3, 31.4
#    50    88.2, 31.0    97.3, 32.1    105.2, 32.9   112.9, 33.8   120.6, 34.7   130.5, 35.8
#    75    92.8, 33.4    102.5, 34.9   110.5, 36.0   118.6, 37.2   126.6, 38.4   138.0, 40.1
#   100    97.9, 36.0    108.2, 37.8   115.7, 39.2   124.4, 40.8   132.9, 42.4   147.0, 44.9
# ============================================================================

_FIG_4_2_REFERENCE = ("FHWA-SA-02-054 (GEC-6), Figure 4-2 Correlation Between "
                      "Relative Density, Material Classification and Angle "
                      "of Internal Friction for Coarse-Grained Soils "
                      "(NAVFAC, 1986a), p. 35")
_PCF_TO_KNM3 = 0.157087

_FIG_4_2_DR = [0, 25, 50, 75, 100]
# one row per relative density; (dry unit weight pcf, phi' deg) at each of
# the six solid lines, left to right
_FIG_4_2_MESH = [
    [(78.9, 26.1), (87.0, 26.5), (95.0, 26.8), (102.1, 27.2), (109.0, 27.5),
     (117.8, 27.9)],
    [(83.7, 28.7), (92.1, 29.2), (100.1, 29.8), (107.0, 30.3), (114.3, 30.8),
     (123.3, 31.4)],
    [(88.2, 31.0), (97.3, 32.1), (105.2, 32.9), (112.9, 33.8), (120.6, 34.7),
     (130.5, 35.8)],
    [(92.8, 33.4), (102.5, 34.9), (110.5, 36.0), (118.6, 37.2), (126.6, 38.4),
     (138.0, 40.1)],
    [(97.9, 36.0), (108.2, 37.8), (115.7, 39.2), (124.4, 40.8), (132.9, 42.4),
     (147.0, 44.9)],
]


def _fig_4_2_dr_line(relative_density_pct: float):
    """The chart's line of one relative density: six (pcf, phi') points,
    each taken along its solid line between the printed dashed lines."""
    dr = relative_density_pct
    for i in range(len(_FIG_4_2_DR) - 1):
        d0, d1 = _FIG_4_2_DR[i], _FIG_4_2_DR[i + 1]
        if d0 <= dr <= d1:
            t = (dr - d0) / (d1 - d0)
            return [(g0 + t * (g1 - g0), p0 + t * (p1 - p0))
                    for (g0, p0), (g1, p1) in zip(_FIG_4_2_MESH[i],
                                                  _FIG_4_2_MESH[i + 1])]
    raise ValueError(
        f"relative_density must be 0-100%, got {relative_density_pct}")


def figure_4_2_friction_angle_from_density(gamma_d_kNm3: float,
                                           relative_density_pct: float = 50
                                           ) -> float:
    """Angle of internal friction phi' (degrees) of a coarse-grained soil without plastic fines at a dry unit weight and a relative density, read from the mesh of GEC-6 Figure 4-2 (FHWA-SA-02-054, p. 35; NAVFAC 1986a): linear along and between the chart's relative density lines (0, 25, 50, 75, 100 %), which run from the ML line to the GW line; a dry unit weight the chart does not plot at that relative density is refused.

    The chart ties the two inputs to the material type: at one relative
    density the dry unit weight rises from the ML line through "SM and SP
    in this range" and SW to GP and GW, so each relative density has its
    own range of dry unit weight (0 %: 12.4 to 18.5 kN/m3; 50 %: 13.9 to
    20.5; 100 %: 15.4 to 23.1). The chart says phi' was obtained from
    effective stress failure envelopes and that the correlation is
    approximate, for cohesionless materials without plastic fines; its note
    says to use caution in the shaded portion of the chart because of the
    potential for unreliable SPT N-values in gravels. As drawn, the shaded
    portion lies between the SW line and the GW line, up to the 100 %
    relative density line, above a thin line drawn from the SW line at 75 %
    through the GP label to the GW line at 50 %.

    Parameters
    ----------
    gamma_d_kNm3 : float
        Dry unit weight in kN/m^3, inside the chart's mesh at the given
        relative density (overall 12.4 to 23.1 kN/m^3, 78.9 to 147 pcf).
    relative_density_pct : float
        Relative density in percent, 0 to 100. Default 50, which is not a
        value the chart recommends: give the soil's own.

    Returns
    -------
    float
        Angle of internal friction phi' [degrees], 26.1 to 44.9.

    Raises
    ------
    ValueError
        If the relative density is outside 0 to 100 %, or the dry unit
        weight is outside the chart's mesh at that relative density.

    References
    ----------
    FHWA-SA-02-054 (GEC-6), Figure 4-2, printed p. 35 (pdf_page_index 40).
    """
    if relative_density_pct < 0 or relative_density_pct > 100:
        raise ValueError(
            f"relative_density must be 0-100%, got {relative_density_pct}"
        )
    line = _fig_4_2_dr_line(relative_density_pct)
    gs = [g for g, _ in line]
    ps = [p for _, p in line]
    gamma_pcf = gamma_d_kNm3 / _PCF_TO_KNM3
    # 0.05 kN/m3 of grace: the ends are given to the caller to 0.1 kN/m3
    if (gamma_d_kNm3 < gs[0] * _PCF_TO_KNM3 - 0.05
            or gamma_d_kNm3 > gs[-1] * _PCF_TO_KNM3 + 0.05):
        raise ValueError(
            f"gamma_d = {gamma_d_kNm3} kN/m^3 is outside GEC-6 Figure 4-2 "
            f"at a relative density of {relative_density_pct:g} %: the "
            f"chart's mesh runs there from {gs[0] * _PCF_TO_KNM3:.1f} kN/m^3 "
            f"({gs[0]:.0f} pcf, the ML line) to "
            f"{gs[-1] * _PCF_TO_KNM3:.1f} kN/m^3 ({gs[-1]:.0f} pcf, the GW "
            "line). The chart gives no friction angle here.")
    gamma_pcf = min(max(gamma_pcf, gs[0]), gs[-1])
    return _linterp(gamma_pcf, gs, ps)
