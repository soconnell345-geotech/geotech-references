"""Tests for chart_lines: standard chart lines as the references print them.

The plasticity chart's A-line is horizontal at PI = 4 up to LL = 25.5 and
PI = 0.73(LL - 20) beyond; the U-line is vertical at LL = 16 up to PI = 7
and PI = 0.9(LL - 8) beyond (UFS 3-220-10 Figure 1-2, p. 14; GEC 5
Equations 4.20 and 4.21, p. 4-25). Live runs drew the A-line down to PI 0
at LL 20 and read PI 2.9 at LL 24: these tests pin the printed form.
"""

import importlib.util
import json
import math
from pathlib import Path

import pytest

from geotech_references import _figures_db
from geotech_references import chart_lines as cl


def _on(points, x):
    """y of the first sloped or level segment of ``points`` spanning x."""
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 != x1 and min(x0, x1) <= x <= max(x0, x1):
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None


def _line(chart, name):
    return next(l for l in chart["lines"] if l["name"] == name)


def _zone(chart, name):
    return next(z for z in chart["zones"] if z["name"] == name)


# ---------------------------------------------------------------- A-line


@pytest.mark.parametrize("ll, pi", [
    (4.0, 4.0), (10.0, 4.0), (20.0, 4.0), (24.0, 4.0), (25.5, 4.0),
])
def test_a_line_is_level_at_pi_4_up_to_ll_25_5(ll, pi):
    assert cl.line_value("uscs_plasticity", "A-line", ll) == pytest.approx(pi)
    pts = _line(cl.chart_lines("uscs_plasticity"), "A-line")["points"]
    assert _on(pts, ll) == pytest.approx(pi)


@pytest.mark.parametrize("ll", [26.0, 30.0, 40.0, 50.0, 75.0, 100.0])
def test_a_line_slope_is_0_73_ll_minus_20(ll):
    want = 0.73 * (ll - 20.0)
    assert cl.line_value("uscs_plasticity", "A-line", ll) == pytest.approx(want)
    pts = _line(cl.chart_lines("uscs_plasticity"), "A-line")["points"]
    assert _on(pts, ll) == pytest.approx(want)


def test_a_line_at_ll_24_is_pi_4_not_2_9():
    # The w12 read-off said 2.9: 0.73(24 - 20) on the sloped equation,
    # which the chart does not draw below LL 25.5.
    assert cl.line_value("plasticity_chart", "A-line", 24) == 4.0
    assert cl.line_value("uscs_plasticity", "a-line", 24) != pytest.approx(
        0.73 * 4.0)


def test_a_line_never_runs_to_pi_0_at_ll_20():
    pts = _line(cl.chart_lines("uscs_plasticity"), "A-line")["points"]
    assert min(y for _, y in pts) == pytest.approx(4.0)
    assert pts[0] == [4.0, 4.0]          # starts on the PI = LL line
    assert cl.line_value("uscs_plasticity", "A-line", 3.0) is None


def test_a_line_points_join_the_two_printed_equations_at_ll_25_5():
    pts = _line(cl.chart_lines("uscs_plasticity"), "A-line")["points"]
    assert [25.5, 4.0] in pts and [25.5, 4.015] in pts


# ---------------------------------------------------------------- U-line


def test_u_line_is_vertical_at_ll_16_up_to_pi_7():
    pts = _line(cl.chart_lines("uscs_plasticity"), "U-line")["points"]
    assert pts[0] == [16.0, 0.0] and pts[1] == [16.0, 7.0]
    assert pts[2] == [16.0, 7.2]         # 0.9(16 - 8): the printed step
    assert cl.line_value("uscs_plasticity", "U-line", 15.9) is None


@pytest.mark.parametrize("ll", [20.0, 30.0, 50.0, 60.0])
def test_u_line_slope_is_0_9_ll_minus_8(ll):
    want = 0.9 * (ll - 8.0)
    assert cl.line_value("uscs_plasticity", "U-line", ll) == pytest.approx(want)
    pts = _line(cl.chart_lines("uscs_plasticity"), "U-line")["points"]
    assert _on(pts, ll) == pytest.approx(want)


def test_u_line_lies_above_the_a_line():
    for ll in (16.0, 25.5, 40.0, 50.0, 80.0, 100.0):
        u = cl.line_value("uscs_plasticity", "U-line", ll)
        a = cl.line_value("uscs_plasticity", "A-line", ll)
        assert u > a


# ---------------------------------------------------------------- other lines


def test_ll_50_and_pi_equals_ll():
    c = cl.chart_lines("uscs_plasticity")
    ll50 = _line(c, "LL = 50")["points"]
    assert {x for x, _ in ll50} == {50.0}
    assert ll50[0] == [50.0, 0.0] and ll50[-1] == [50.0, 50.0]
    for x, y in _line(c, "PI = LL")["points"]:
        assert x == pytest.approx(y)
    assert cl.line_value("uscs_plasticity", "LL = 50", 50) is None


def test_cl_ml_zone_is_pi_4_to_7_between_pi_ll_and_a_line():
    z = _zone(cl.chart_lines("uscs_plasticity"), "CL-ML")
    assert z["hatched"] is True
    ys = [y for _, y in z["outline"]]
    assert min(ys) == pytest.approx(4.0) and max(ys) == pytest.approx(7.0)
    assert [4.0, 4.0] in z["outline"] and [7.0, 7.0] in z["outline"]
    corner = [p for p in z["outline"] if p[1] == 7.0 and p[0] > 7.0][0]
    assert corner[0] == pytest.approx(20.0 + 7.0 / 0.73, abs=1e-6)
    others = [x for x in cl.chart_lines("uscs_plasticity")["zones"]
              if x["name"] != "CL-ML"]
    assert not any(x["hatched"] for x in others)


@pytest.mark.parametrize("zone, ll, pi", [
    ("CL or OL", 30.0, 12.0), ("CL or OL", 45.0, 25.0),
    ("CH or OH", 70.0, 40.0), ("ML or OL", 30.0, 3.0),
    ("ML or OL", 45.0, 15.0), ("MH or OH", 80.0, 30.0),
])
def test_zone_names_sit_between_their_lines(zone, ll, pi):
    z = _zone(cl.chart_lines("uscs_plasticity"), zone)
    assert cl._inside((ll, pi), [tuple(p) for p in z["outline"]])
    x, y = z["label_at"]
    a = cl.line_value("uscs_plasticity", "A-line", x)
    u = cl.line_value("uscs_plasticity", "U-line", x)
    if zone.startswith("C"):
        assert a < y < u                  # above the A-line, below the U-line
    else:
        assert y < a
    assert (x < 50.0) == zone.endswith("L or OL") or zone == "CL-ML"


def test_cl_label_is_not_above_the_u_line_in_any_extent():
    for xr, yr in [(None, None), ((0, 40), (0, 20)), ((15, 35), (0, 12)),
                   ((0, 60), (0, 30))]:
        z = _zone(cl.chart_lines("uscs_plasticity", xr, yr), "CL or OL")
        x, y = z["label_at"]
        assert y < cl.line_value("uscs_plasticity", "U-line", x)
        assert y > cl.line_value("uscs_plasticity", "A-line", x)


# ---------------------------------------------------------------- extents


def test_extent_clips_and_widens():
    c = cl.chart_lines("uscs_plasticity", x_range=[40, 0], y_range=[0, 20])
    assert c["extent"] == {"x": [0.0, 40.0], "y": [0.0, 20.0]}
    for line in c["lines"]:
        for x, y in line["points"]:
            assert 0.0 <= x <= 40.0 + 1e-9 and 0.0 <= y <= 20.0 + 1e-9
    assert _line(c, "LL = 50")["points"] == []
    assert _line(c, "LL = 50")["label_at"] is None
    assert _zone(c, "CH or OH")["label_at"] is None
    wide = cl.chart_lines("uscs_plasticity", x_range=[0, 150],
                          y_range=[0, 100])
    a = _line(wide, "A-line")["points"]
    assert a[-1][0] == pytest.approx(150.0)
    assert a[-1][1] == pytest.approx(0.73 * 130.0)


def test_label_points_are_on_the_drawn_lines():
    for name in cl.chart_names():
        for line in cl.chart_lines(name)["lines"]:
            if not line["points"]:
                continue
            assert line["label_at"] in line["points"]


@pytest.mark.parametrize("bad", [[1, 1], ["a", 2], [0, math.inf]])
def test_bad_range_is_refused(bad):
    with pytest.raises(ValueError):
        cl.chart_lines("uscs_plasticity", x_range=bad)


def test_unknown_names_are_refused_with_the_names_there_are():
    with pytest.raises(ValueError, match="uscs_plasticity"):
        cl.chart_lines("unified_chart")
    with pytest.raises(ValueError, match="A-line"):
        cl.line_value("uscs_plasticity", "B-line", 30)


# ---------------------------------------------------------------- AASHTO


def test_aashto_lines():
    c = cl.chart_lines("aashto_plasticity")
    assert {x for x, _ in _line(c, "LL = 40")["points"]} == {40.0}
    assert {y for _, y in _line(c, "PI = 10")["points"]} == {10.0}
    pts = _line(c, "PI = LL - 30")["points"]
    assert pts[0] == [40.0, 10.0]
    for ll in (50.0, 70.0, 90.0):
        assert _on(pts, ll) == pytest.approx(ll - 30.0)
        assert cl.line_value("aashto", "PI = LL - 30", ll) == pytest.approx(
            ll - 30.0)
    names = {z["name"] for z in c["zones"]}
    assert names == {"A-6, A-2-6", "A-4, A-2-4", "A-5, A-2-5", "A-7-6",
                     "A-7-5, A-2-7"}
    z = _zone(c, "A-7-6")
    x, y = z["label_at"]
    assert y > x - 30.0 and x > 40.0


# ---------------------------------------------------------------- sieves


def test_particle_sizes_as_printed():
    c = cl.chart_lines("uscs_particle_sizes", x_range=[0.001, 1000])
    sizes = {l["name"]: l["size_mm"] for l in c["lines"]}
    assert sizes == {"No. 200": 0.075, "No. 40": 0.425, "No. 10": 2.0,
                     "No. 4": 4.75, "3/4 in.": 19.0, "3 in.": 75.0,
                     "12 in.": 305.0}
    for l in c["lines"]:
        assert {x for x, _ in l["points"]} == {l["size_mm"]}
    assert c["x"]["log"] is True
    bands = {z["name"]: z["x_range"] for z in c["zones"]}
    assert bands["Sand"] == [0.075, 4.75]
    assert bands["Gravel"] == [4.75, 75.0]
    assert bands["Silt or clay"] == [None, 0.075]
    # a band's name stands between the lines drawn across it, never on one
    sizes_drawn = [l["size_mm"] for l in c["lines"]]
    for z in c["zones"]:
        x = z["label_at"][0]
        assert all(abs(math.log(x / s)) > 0.3 for s in sizes_drawn), z
    sand = _zone(c, "Sand")["label_at"][0]
    assert sand == pytest.approx(math.sqrt(0.075 * 0.425), abs=1e-6)


def test_particle_sizes_default_frame_leaves_out_the_12_in_line():
    c = cl.chart_lines("grain_size")
    assert _line(c, "12 in.")["points"] == []
    assert _zone(c, "Boulders")["label_at"] is None


# ---------------------------------------------------------------- sources


def test_every_chart_names_its_source_and_page():
    for name in cl.chart_names():
        c = cl.chart_lines(name)
        for src in [c["source"]] + c["also_printed_in"]:
            assert src["document"] and src["where"]
            assert src["printed_page"] and isinstance(src["pdf_page"], int)
        json.dumps(c)                      # plain data


@pytest.mark.parametrize("name", ["uscs_plasticity", "aashto_plasticity"])
def test_catalogued_figures_match_the_figure_catalog(name):
    c = cl.chart_lines(name)
    for src in [c["source"]] + c["also_printed_in"]:
        if "figure" not in src:
            continue
        row = _figures_db.figure_get(src["reference"], src["figure"])
        assert row["pdf_page_index"] == src["pdf_page"] - 1


def test_loads_by_path_without_the_package():
    # The app's plotting box loads this file by its path, outside the
    # package: it must import nothing from the package.
    path = Path(cl.__file__)
    spec = importlib.util.spec_from_file_location("_chart_lines_alone", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.line_value("uscs_plasticity", "A-line", 24) == 4.0
