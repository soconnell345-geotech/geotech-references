"""Standard lines of engineering charts, as the references print them.

A figure that redraws a standard chart takes its lines from here, never from
memory: the plasticity chart's A-line, U-line and CL-ML zone, the AASHTO
chart's LL = 40, PI = 10 and PI = LL - 30, and the sieve sizes that bound
gravel, sand and fines. Live smoke waves w9 and w12 of the app (its BACKLOG
GM-153) drew the A-line down to PI 0 at LL 20, where the chart has it
horizontal at PI 4 up to LL 25.5, and read "PI 2.9 at LL 24" where the chart
gives 4.

Each chart carries the reference's own equations and limits as printed, the
document, the figure or section, the printed page and the PDF page (1-based),
and the library's figure key where the figure is catalogued
(``figure_get(reference, figure)``). :func:`chart_lines` gives the lines as
points over the printed chart's frame or over the range asked for;
:func:`line_value` reads one line at a point.

Standard library only, and nothing imported from the package: the app's
plotting box loads this file by its path.
"""

import copy
import math

#: Where each chart's lines come from. ``reference`` and ``figure`` are the
#: library's figure-catalog keys (``geotech_references._figures_db``).
_UFS_3_220_10 = "UFS 3-220-10 Soil Mechanics (DM 7.1), 16 January 2026"
_GEC_5 = ("FHWA-NHI-16-072, GEC 5 Geotechnical Site Characterization, "
          "November 2016")
_NHI_06_088 = ("FHWA NHI-06-088, Soils and Foundations Reference Manual, "
               "Volume I, December 2006")

#: The A-line at PI = 7: the top right corner of the CL-ML zone.
_LL_A7 = 20.0 + 7.0 / 0.73


def _a(ll):
    """The A-line's sloped part, PI = 0.73(LL - 20)."""
    return 0.73 * (ll - 20.0)


def _u(ll):
    """The U-line's sloped part, PI = 0.9(LL - 8)."""
    return 0.9 * (ll - 8.0)

_CHARTS = {
    "uscs_plasticity": {
        "title": "Plasticity Chart",
        "source": {
            "document": _UFS_3_220_10,
            "where": "Figure 1-2, Plasticity Chart (Section 1-3.3.1)",
            "printed_page": "14", "pdf_page": 42,
            "reference": "dm7_1", "figure": "1-2"},
        "also_printed_in": [
            {"document": _GEC_5,
             "where": ("Figure 4-11, Casagrande plasticity chart for "
                       "classification of fine-grained soils (from ASTM "
                       "D2487, 2011); Equations 4.20 (A-line) and 4.21 "
                       "(U-line)"),
             "printed_page": "4-25", "pdf_page": 135,
             "reference": "gec_5", "figure": "4-11"},
            {"document": _NHI_06_088,
             "where": ("Figure 4-3, Plasticity chart for Unified Soil "
                       "Classification System (ASTM D 2487)"),
             "printed_page": "4-22", "pdf_page": 222},
        ],
        "x": {"name": "Liquid Limit (LL)", "log": False},
        "y": {"name": "Plasticity Index (PI)", "log": False},
        "frame": {"x": [0.0, 110.0], "y": [0.0, 60.0]},
        "lines": [
            {"name": "A-line",
             "equation": ("Horizontal at PI = 4 to LL = 25.5, then "
                          "PI = 0.73(LL - 20)"),
             "path": [(4.0, 4.0), (25.5, 4.0), (25.5, 0.73 * 5.5)],
             "ray": (1.0, 0.73), "dash": "solid", "label_x": 85.0,
             "note": ("Starts on the PI = LL line, as drawn. The printed "
                      "equations meet with a step of 0.015 at LL 25.5 "
                      "(0.73 x 5.5 = 4.015); the points join them.")},
            {"name": "U-line",
             "equation": "Vertical at LL = 16 to PI = 7, then PI = 0.9(LL - 8)",
             "path": [(16.0, 0.0), (16.0, 7.0), (16.0, 0.9 * 8.0)],
             "ray": (1.0, 0.9), "dash": "dash", "label_x": 55.0,
             "note": ("Generally considered to be the upper limit for "
                      "natural soils: test results above it should be "
                      "carefully scrutinized and probably repeated (GEC 5, "
                      "p. 4-25). The printed equations meet with a step of "
                      "0.2 at LL 16 (0.9 x 8 = 7.2); the points join them.")},
            {"name": "LL = 50",
             "equation": "LL = 50",
             "path": [(50.0, 0.0), (50.0, 50.0)],
             "ray": None, "dash": "solid", "label_y": 25.0,
             "note": ("Divides L from H (CL from CH, ML from MH); drawn up to "
                      "the PI = LL line, as printed.")},
            {"name": "PI = LL",
             "equation": "PI = LL",
             "path": [(0.0, 0.0)],
             "ray": (1.0, 1.0), "dash": "solid", "label_x": 35.0,
             "note": ("Drawn on the printed chart through (10, 10) to "
                      "(60, 60); the text gives it no equation. PI = LL - PL, "
                      "so no soil plots above it.")},
        ],
        "zones": [
            {"name": "CL-ML", "hatched": True,
             "outline": [(4.0, 4.0), (25.5, 4.0), (25.5, 0.73 * 5.5),
                         (_LL_A7, 7.0), (7.0, 7.0)],
             "label_at": (21.0, 5.5),
             "note": ("The band from PI 4 to PI 7, between the PI = LL "
                      "line and the A-line: silty clay (CL-ML). UFS "
                      "3-220-10 Figure 1-2 outlines it; GEC 5 Figure 4-11 "
                      "and NHI-06-088 Figure 4-3 hatch it.")},
            {"name": "CL or OL",
             "outline": lambda R: [(16.0, 7.0), (_LL_A7, 7.0),
                                   (50.0, _a(50.0)), (50.0, _u(50.0)),
                                   (16.0, 0.9 * 8.0)],
             "label_at": (40.0, (_a(40.0) + _u(40.0)) / 2.0)},
            {"name": "CH or OH",
             "outline": lambda R: [(50.0, _a(50.0)), (R, _a(R)), (R, _u(R)),
                                   (50.0, _u(50.0))],
             "label_at": (70.0, (_a(70.0) + _u(70.0)) / 2.0)},
            {"name": "ML or OL",
             "outline": lambda R: [(0.0, 0.0), (50.0, 0.0), (50.0, _a(50.0)),
                                   (25.5, 0.73 * 5.5), (25.5, 4.0),
                                   (4.0, 4.0)],
             "label_at": (40.0, _a(40.0) / 2.0)},
            {"name": "MH or OH",
             "outline": lambda R: [(50.0, 0.0), (R, 0.0), (R, _a(R)),
                                   (50.0, _a(50.0))],
             "label_at": (75.0, _a(75.0) / 2.0)},
        ],
        "notes": [
            "For classification of fine-grained soils and fine-grained "
            "fraction of coarse-grained soils (printed on the chart).",
            "OL and OH: a soil is organic when the liquid limit after oven "
            "drying is less than 75 % of that before; it is plotted by the "
            "liquid limit and plasticity index of the material not oven "
            "dried (UFS 3-220-10 Section 1-3.3.1).",
        ],
    },
    "aashto_plasticity": {
        "title": "AASHTO soil classifications for fine-grained soils",
        "source": {
            "document": _GEC_5,
            "where": ("Figure 4-12, AASHTO soil classifications for "
                      "fine-grained soils (from ASTM D3282, 2015)"),
            "printed_page": "4-27", "pdf_page": 137,
            "reference": "gec_5", "figure": "4-12"},
        "also_printed_in": [
            {"document": _UFS_3_220_10,
             "where": ("Table 1-5, AASHTO Soil Classification System, "
                       "note b (A-7-5 / A-7-6)"),
             "printed_page": "19", "pdf_page": 47},
        ],
        "x": {"name": "Liquid Limit", "log": False},
        "y": {"name": "Plasticity Index", "log": False},
        "frame": {"x": [0.0, 100.0], "y": [0.0, 70.0]},
        "lines": [
            {"name": "LL = 40", "equation": "LL = 40",
             "path": [(40.0, 0.0)], "ray": (0.0, 1.0), "dash": "solid",
             "label_y": 40.0,
             "note": ("Table 1-5: liquid limit 40 or less, or 41 or more; "
                      "the chart draws the line at 40.")},
            {"name": "PI = 10", "equation": "PI = 10",
             "path": [(0.0, 10.0)], "ray": (1.0, 0.0), "dash": "solid",
             "label_x": 85.0,
             "note": ("Table 1-5: plasticity index 10 or less, or 11 or "
                      "more; the chart draws the line at 10.")},
            {"name": "PI = LL - 30",
             "equation": ("A-7-5 has PI <= (LL - 30) and A-7-6 has "
                          "PI > (LL - 30)"),
             "path": [(40.0, 10.0)], "ray": (1.0, 1.0), "dash": "solid",
             "label_x": 75.0,
             "note": "Divides A-7-5 from A-7-6 (Table 1-5, note b)."},
        ],
        "zones": [
            {"name": "A-6, A-2-6",
             "outline": lambda R: [(0.0, 10.0), (40.0, 10.0), (40.0, R),
                                   (0.0, R)],
             "label_at": (25.0, 22.0)},
            {"name": "A-4, A-2-4",
             "outline": lambda R: [(0.0, 0.0), (40.0, 0.0), (40.0, 10.0),
                                   (0.0, 10.0)],
             "label_at": (30.0, 5.0)},
            {"name": "A-5, A-2-5",
             "outline": lambda R: [(40.0, 0.0), (R, 0.0), (R, 10.0),
                                   (40.0, 10.0)],
             "label_at": (52.0, 5.0)},
            {"name": "A-7-6",
             "outline": lambda R: [(40.0, 10.0), (R, R - 30.0), (R, R),
                                   (40.0, R)],
             "label_at": (55.0, 32.0)},
            {"name": "A-7-5, A-2-7",
             "outline": lambda R: [(40.0, 10.0), (R, 10.0), (R, R - 30.0)],
             "label_at": (62.0, 18.0)},
        ],
        "notes": [
            "For the fraction passing the No. 40 (425 um) sieve. A-2-4 to "
            "A-2-7 when 35 % or less passes the No. 200 sieve; A-4 to A-7 "
            "when 36 % or more does (Table 4-13; UFS 3-220-10 Table 1-5).",
        ],
    },
    "uscs_particle_sizes": {
        "title": "Particle size limits of the Unified Soil Classification",
        "source": {
            "document": _UFS_3_220_10,
            "where": ("Section 1-3.1, Definitions (they agree with ASTM "
                      "D2487)"),
            "printed_page": "7", "pdf_page": 35},
        "also_printed_in": [
            {"document": _GEC_5,
             "where": ("Table 4-2, Descriptive terms for soil particle size "
                       "ranges (the millimetres of 3/4 in. and 12 in.)"),
             "printed_page": "4-3", "pdf_page": 113},
        ],
        "x": {"name": "Grain Size (mm)", "log": True},
        "y": {"name": "% Finer by Weight", "log": False},
        "frame": {"x": [0.001, 100.0], "y": [0.0, 100.0]},
        "lines": [
            {"name": "No. 200", "equation": "No. 200 sieve, 75 um",
             "path": [(0.075, 0.0)], "ray": (0.0, 1.0), "dash": "dot",
             "label_y": 95.0, "size_mm": 0.075,
             "note": "Sand is retained on it; silt and clay pass it."},
            {"name": "No. 40", "equation": "No. 40 sieve, 425 um",
             "path": [(0.425, 0.0)], "ray": (0.0, 1.0), "dash": "dot",
             "label_y": 95.0, "size_mm": 0.425,
             "note": "Divides medium sand from fine sand."},
            {"name": "No. 10", "equation": "No. 10 sieve, 2.00 mm",
             "path": [(2.0, 0.0)], "ray": (0.0, 1.0), "dash": "dot",
             "label_y": 95.0, "size_mm": 2.0,
             "note": "Divides coarse sand from medium sand."},
            {"name": "No. 4", "equation": "No. 4 sieve, 4.75 mm",
             "path": [(4.75, 0.0)], "ray": (0.0, 1.0), "dash": "dot",
             "label_y": 95.0, "size_mm": 4.75,
             "note": "Gravel is retained on it; sand passes it."},
            {"name": "3/4 in.", "equation": "3/4-inch sieve, 19 mm",
             "path": [(19.0, 0.0)], "ray": (0.0, 1.0), "dash": "dot",
             "label_y": 95.0, "size_mm": 19.0,
             "source": {"document": _GEC_5,
                        "where": "Table 4-2 (19 mm; UFS 3-220-10 Section "
                                 "1-3.1 gives 3/4 inch)",
                        "printed_page": "4-3", "pdf_page": 113},
             "note": "Divides coarse gravel from fine gravel."},
            {"name": "3 in.", "equation": "3-inch sieve, 75 mm",
             "path": [(75.0, 0.0)], "ray": (0.0, 1.0), "dash": "dot",
             "label_y": 95.0, "size_mm": 75.0,
             "note": ("Cobbles are retained on it; gravel passes it (75 mm: "
                      "UFS 3-220-10 Section 1-3.3, p. 13).")},
            {"name": "12 in.", "equation": "12-inch opening, 305 mm",
             "path": [(305.0, 0.0)], "ray": (0.0, 1.0), "dash": "dot",
             "label_y": 95.0, "size_mm": 305.0,
             "source": {"document": _GEC_5,
                        "where": "Table 4-2 (305 mm; UFS 3-220-10 Section "
                                 "1-3.1 gives 12 inches)",
                        "printed_page": "4-3", "pdf_page": 113},
             "note": "Boulders will not pass it; cobbles do."},
        ],
        "zones": [
            {"name": "Silt or clay", "x_range": (None, 0.075),
             "note": ("Fines: both pass the No. 200 sieve and are told "
                      "apart by plasticity, not size (classify them on the "
                      "plasticity chart).")},
            {"name": "Sand", "x_range": (0.075, 4.75),
             "note": ("Coarse above the No. 10 sieve, medium to the No. 40, "
                      "fine below it.")},
            {"name": "Gravel", "x_range": (4.75, 75.0),
             "note": "Coarse above 3/4 inch, fine below it."},
            {"name": "Cobbles", "x_range": (75.0, 305.0)},
            {"name": "Boulders", "x_range": (305.0, None)},
        ],
        "notes": [
            "USCS sets no particle size between silt and clay. GEC 5 Table "
            "4-2 names silt 0.075 to 0.002 mm and clay finer than 0.002 mm "
            "as descriptive terms; that is not the USCS split.",
            "GEC 5 Table 4-2 prints the No. 40 sieve as 0.0425 mm; UFS "
            "3-220-10 Section 1-3.1 gives 425 um (0.425 mm), used here.",
            "No printed figure draws these limits on a grading chart: the "
            "frame (0.001 to 100 mm) is the range a sieve and hydrometer "
            "test reports, not a reference's.",
        ],
    },
}

#: Other names a caller may use for a chart.
_ALIASES = {
    "plasticity": "uscs_plasticity",
    "plasticity_chart": "uscs_plasticity",
    "uscs_plasticity_chart": "uscs_plasticity",
    "casagrande": "uscs_plasticity",
    "casagrande_plasticity_chart": "uscs_plasticity",
    "a_line": "uscs_plasticity",
    "aashto": "aashto_plasticity",
    "aashto_plasticity_chart": "aashto_plasticity",
    "particle_sizes": "uscs_particle_sizes",
    "grain_size": "uscs_particle_sizes",
    "grain_sizes": "uscs_particle_sizes",
    "uscs_grain_size": "uscs_particle_sizes",
    "uscs_grain_sizes": "uscs_particle_sizes",
    "sieve_sizes": "uscs_particle_sizes",
}


def chart_names():
    """The charts this module gives, by name."""
    return sorted(_CHARTS)


def _key(name):
    key = str(name or "").strip().lower()
    for ch in " -.":
        key = key.replace(ch, "_")
    key = _ALIASES.get(key, key)
    if key not in _CHARTS:
        raise ValueError(f"no chart named {name!r}; the charts are "
                         f"{', '.join(chart_names())}")
    return key


def _range(given, frame, axis):
    """``[low, high]`` from ``given`` (either order), else the frame."""
    if given is None:
        return [float(frame[0]), float(frame[1])]
    try:
        lo, hi = sorted(float(v) for v in given)
    except (TypeError, ValueError):
        raise ValueError(f"{axis}_range must be two numbers")
    if not (math.isfinite(lo) and math.isfinite(hi)) or hi <= lo:
        raise ValueError(f"{axis}_range must be two different finite numbers")
    return [lo, hi]


def _full_path(line, reach):
    """The line's vertices, its ray carried out to ``reach``."""
    pts = [tuple(map(float, p)) for p in line["path"]]
    ray = line.get("ray")
    if ray:
        x, y = pts[-1]
        pts.append((x + ray[0] * reach, y + ray[1] * reach))
    return pts


def _clip_segment(p, q, box):
    """Liang-Barsky: the part of segment p-q inside ``box``, or None."""
    (x0, y0), (x1, y1) = p, q
    (xl, xh), (yl, yh) = box
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, x0 - xl), (dx, xh - x0), (-dy, y0 - yl),
                   (dy, yh - y0)):
        if pk == 0:
            if qk < 0:
                return None
            continue
        t = qk / pk
        if pk < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return None
    return ((x0 + t0 * dx, y0 + t0 * dy), (x0 + t1 * dx, y0 + t1 * dy))


def _same(a, b, tol=1e-9):
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def _clip_path(pts, box):
    """The longest connected run of the polyline inside ``box``."""
    runs, run = [], []
    for p, q in zip(pts, pts[1:]):
        seg = _clip_segment(p, q, box)
        if seg is None or _same(seg[0], seg[1]):
            if run:
                runs.append(run)
                run = []
            continue
        if run and _same(run[-1], seg[0]):
            run.append(seg[1])
        else:
            if run:
                runs.append(run)
            run = [seg[0], seg[1]]
    if run:
        runs.append(run)
    if not runs:
        return []
    return max(runs, key=len)


def _y_at(pts, x):
    """y of the first non-vertical segment of ``pts`` that spans ``x``."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 == x1:
            continue
        lo, hi = min(x0, x1), max(x0, x1)
        if lo - 1e-12 <= x <= hi + 1e-12:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None


def _label_point(line, pts):
    """A point on the drawn line for its name: at ``label_x`` (or
    ``label_y`` for an upright line) when the drawn part reaches it, else
    the middle of its longest piece."""
    if "label_x" in line:
        y = _y_at(pts, line["label_x"])
        if y is not None:
            return (float(line["label_x"]), y)
    if "label_y" in line:
        ly = float(line["label_y"])
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 == x1 and min(y0, y1) <= ly <= max(y0, y1):
                return (x0, ly)
    (x0, y0), (x1, y1) = max(zip(pts, pts[1:]),
                             key=lambda s: math.hypot(s[1][0] - s[0][0],
                                                      s[1][1] - s[0][1]))
    return ((x0 + x1) / 2.0, (y0 + y1) / 2.0)


def _with_vertex(pts, at):
    """``pts`` with ``at`` (a point on the line) put in as a vertex."""
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        if _same(p, at) or _same(q, at):
            return pts
        if (min(p[0], q[0]) - 1e-12 <= at[0] <= max(p[0], q[0]) + 1e-12
                and min(p[1], q[1]) - 1e-12 <= at[1]
                <= max(p[1], q[1]) + 1e-12):
            return pts[:i + 1] + [at] + pts[i + 1:]
    return pts


def _clip_polygon(outline, box):
    """Sutherland-Hodgman: the part of a polygon inside ``box``."""
    (xl, xh), (yl, yh) = box
    edges = ((lambda p: p[0] >= xl, lambda p, q: _cross_x(p, q, xl)),
             (lambda p: p[0] <= xh, lambda p, q: _cross_x(p, q, xh)),
             (lambda p: p[1] >= yl, lambda p, q: _cross_y(p, q, yl)),
             (lambda p: p[1] <= yh, lambda p, q: _cross_y(p, q, yh)))
    out = list(outline)
    for inside, cross in edges:
        if not out:
            break
        src, out = out, []
        for i, p in enumerate(src):
            prev = src[i - 1]
            if inside(p):
                if not inside(prev):
                    out.append(cross(prev, p))
                out.append(p)
            elif inside(prev):
                out.append(cross(prev, p))
    return out


def _cross_x(p, q, x):
    t = (x - p[0]) / (q[0] - p[0])
    return (x, p[1] + t * (q[1] - p[1]))


def _cross_y(p, q, y):
    t = (y - p[1]) / (q[1] - p[1])
    return (p[0] + t * (q[0] - p[0]), y)


def _inside(pt, poly):
    """Whether ``pt`` is inside the polygon ``poly`` (ray casting)."""
    x, y = pt
    hit = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y):
            if x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                hit = not hit
    return hit


def _edge_distance(pt, poly, sx, sy):
    """The distance from ``pt`` to the nearest edge of ``poly``, with x and
    y scaled by ``sx`` and ``sy`` (the extent's width and height)."""
    px, py = pt[0] / sx, pt[1] / sy
    best = math.inf
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        ax, ay, bx, by = x0 / sx, y0 / sy, x1 / sx, y1 / sy
        dx, dy = bx - ax, by - ay
        den = dx * dx + dy * dy
        t = 0.0 if den == 0 else max(0.0, min(1.0, ((px - ax) * dx
                                                    + (py - ay) * dy) / den))
        best = min(best, math.hypot(px - ax - t * dx, py - ay - t * dy))
    return best


def _zone_label(at, shape, xr, yr):
    """Where a zone's name goes: its printed place when that is drawn, else
    the point of the drawn part farthest from its edges; ``None`` when no
    part is drawn."""
    if len(shape) < 3:
        return None
    if at is not None and _inside(tuple(at), shape):
        return [_r(at[0]), _r(at[1])]
    sx, sy = xr[1] - xr[0], yr[1] - yr[0]
    xs = [p[0] for p in shape]
    ys = [p[1] for p in shape]
    best, where = 0.0, None
    n = 40
    for i in range(1, n):
        for j in range(1, n):
            pt = (min(xs) + (max(xs) - min(xs)) * i / n,
                  min(ys) + (max(ys) - min(ys)) * j / n)
            if _inside(pt, shape):
                d = _edge_distance(pt, shape, sx, sy)
                if d > best:
                    best, where = d, pt
    return None if where is None else [_r(where[0]), _r(where[1])]


def _band_label(x_range, xr, yr, log, inner):
    """Where the name of a band between upright lines goes: low on the
    chart, in the middle of the widest gap between the lines drawn across
    the band (``inner``: their x), by the log of x on a log axis; ``None``
    when the part drawn is under a twelfth of the chart's width."""
    lo = xr[0] if x_range[0] is None else max(xr[0], x_range[0])
    hi = xr[1] if x_range[1] is None else min(xr[1], x_range[1])
    log = bool(log) and lo > 0

    def width(a, b):
        return math.log(b / a) if log else b - a

    if hi <= lo or width(lo, hi) < width(xr[0], xr[1]) / 12.0:
        return None
    cuts = [lo] + sorted(x for x in inner if lo < x < hi) + [hi]
    a, b = max(zip(cuts, cuts[1:]), key=lambda g: width(*g))
    x = math.sqrt(a * b) if log else (a + b) / 2.0
    return [_r(x), _r(yr[0] + 0.05 * (yr[1] - yr[0]))]


def _r(v):
    return round(float(v), 6)


def _pts(seq):
    return [[_r(x), _r(y)] for x, y in seq]


def chart_lines(name, x_range=None, y_range=None):
    """The standard lines of a chart a reference prints, as points.

    Parameters
    ----------
    name : str
        ``"uscs_plasticity"`` (UFS 3-220-10 Figure 1-2: the A-line, the
        U-line, LL = 50, the PI = LL line and the CL-ML zone, with the
        zone names), ``"aashto_plasticity"`` (GEC 5 Figure 4-12: LL =
        40, PI = 10 and PI = LL - 30, with the group names) or
        ``"uscs_particle_sizes"`` (UFS 3-220-10 Section 1-3.1: the sieve
        sizes that bound fines, sand, gravel, cobbles and boulders; upright
        lines on a grain-size chart). A few other spellings are taken
        ("plasticity_chart", "aashto", "grain_size").
    x_range, y_range : pair of numbers, optional
        The extent to draw over, in either order (an axis drawn from high to
        low is the same extent). Default: the printed chart's frame
        (``frame`` in the result).

    Returns
    -------
    dict
        ``name``, ``title``, ``source`` (``document``, ``where``,
        ``printed_page``, ``pdf_page``, and the library's ``reference`` /
        ``figure`` keys where the figure is catalogued), ``also_printed_in``,
        ``x`` / ``y`` (axis ``name`` as printed and ``log``), ``frame``,
        ``extent`` (what was drawn over), ``lines`` and ``zones``, and
        ``notes``. Each line: ``name``, ``equation`` (as printed),
        ``points`` (``[[x, y], ...]`` inside the extent, empty when the line
        is outside it), ``label_at`` (a point of ``points`` for the line's
        name), ``dash`` (as printed: solid, dash, or dot), ``note`` and a
        ``source`` where it differs from the chart's. Each zone: ``name``
        (as printed); ``label_at`` (a point inside the drawn part of the
        zone for its name: the printed place when that is drawn, ``None``
        when no part is); on the plasticity charts ``outline`` (the zone's
        part inside the extent, ``[[x, y], ...]``) and ``hatched`` (true
        for the CL-ML zone alone: UFS 3-220-10 Figure 1-2 outlines it, GEC 5
        Figure 4-11 and NHI-06-088 Figure 4-3 hatch it); on the
        particle-size chart
        ``x_range`` (a band between upright lines, ``None`` at an open end);
        and a ``note`` where there is one.
    """
    key = _key(name)
    chart = _CHARTS[key]
    xr = _range(x_range, chart["frame"]["x"], "x")
    yr = _range(y_range, chart["frame"]["y"], "y")
    box = (tuple(xr), tuple(yr))
    reach = 10.0 * (abs(xr[0]) + abs(xr[1]) + abs(yr[0]) + abs(yr[1]) + 1.0)
    lines = []
    for line in chart["lines"]:
        pts = _clip_path(_full_path(line, reach), box)
        label = None
        if pts:
            label = _label_point(line, pts)
            pts = _with_vertex(pts, label)
        row = {"name": line["name"], "equation": line["equation"],
               "points": _pts(pts),
               "label_at": [_r(label[0]), _r(label[1])] if label else None,
               "dash": line["dash"]}
        for extra in ("size_mm", "note"):
            if extra in line:
                row[extra] = line[extra]
        if "source" in line:
            row["source"] = dict(line["source"])
        lines.append(row)
    zones = []
    for zone in chart["zones"]:
        row = {"name": zone["name"]}
        if "outline" in zone:
            outline = zone["outline"]
            if callable(outline):
                outline = outline(reach)
            shape = _clip_polygon([tuple(map(float, p)) for p in outline],
                                  box)
            row["outline"] = _pts(shape)
            row["hatched"] = bool(zone.get("hatched"))
            row["label_at"] = _zone_label(zone.get("label_at"), shape,
                                           xr, yr)
        if "x_range" in zone:
            row["x_range"] = list(zone["x_range"])
            row["label_at"] = _band_label(
                zone["x_range"], xr, yr, chart["x"]["log"],
                [l["path"][0][0] for l in chart["lines"]])
        if "note" in zone:
            row["note"] = zone["note"]
        zones.append(row)
    return {
        "name": key, "title": chart["title"],
        "source": dict(chart["source"]),
        "also_printed_in": copy.deepcopy(chart["also_printed_in"]),
        "x": dict(chart["x"]), "y": dict(chart["y"]),
        "frame": copy.deepcopy(chart["frame"]),
        "extent": {"x": [_r(v) for v in xr], "y": [_r(v) for v in yr]},
        "lines": lines, "zones": zones,
        "notes": list(chart["notes"]),
    }


def line_value(name, line, x):
    """The value of one of a chart's lines at ``x``, from its printed
    equation: ``line_value("uscs_plasticity", "A-line", 24)`` is 4.0 (the
    A-line is horizontal at PI = 4 to LL = 25.5) and at LL 46 it is 18.98.

    ``None`` where the line is not drawn (the A-line left of LL 4, where it
    starts on the PI = LL line; the U-line left of LL 16) and for an upright
    line (LL = 50, a sieve size), which has no single value.
    """
    key = _key(name)
    want = str(line or "").strip().lower()
    for spec in _CHARTS[key]["lines"]:
        if spec["name"].lower() == want:
            break
    else:
        names = ", ".join(s["name"] for s in _CHARTS[key]["lines"])
        raise ValueError(f"{key} has no line named {line!r}; its lines are "
                         f"{names}")
    x = float(x)
    pts = _full_path(spec, 10.0 * (abs(x) + 1000.0))
    y = _y_at(pts, x)
    return None if y is None else _r(y)


__all__ = ["chart_lines", "chart_names", "line_value"]
