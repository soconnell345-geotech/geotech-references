"""UFC 3-220-20 (dm7_2) Appendix B verification examples, as printed.

The examples are stored in ``dm7_2/text/appendix_b.json`` in the print's
wording with page marks; every formula line and table cell was typed from a
rendered page (app BACKLOG REF-85). These tests:

* check the stored structure (sections, page marks, chapter title);
* scan every dm7_2 body and table for the scatter patterns the text layer
  leaves in formulas (an isolated prime or "(')", empty brackets, runs of
  single letters or digits from a stacked formula, unbalanced brackets, a row
  repeated in consecutive table rows);
* recompute the printed worked numbers from the printed equations and the
  stored table cells; and
* run the dm7_2 functions on the examples' inputs against the printed values.

Printed page = PDF page - 38.
"""
import json
import math
import re
from pathlib import Path

import pytest

TEXT = Path(__file__).resolve().parent.parent / "geotech_references" / "dm7_2" / "text"


def _load(name):
    return json.loads((TEXT / name).read_text(encoding="utf-8"))


APX = _load("appendix_b.json")
SEC = {s["section_id"]: s for s in APX["sections"]}


def _table(section_id, number):
    for t in SEC[section_id]["tables"]:
        if t.startswith(f"Table {number} "):
            return t
    raise KeyError(number)


def _rows(table):
    """Rows of a stored table string: the cells after the title, split on ';'."""
    body = table.split(" — ", 1)[1]
    body = re.sub(r"\s*\(p\. \d+\)(\s*\(As printed.*)?$", "", body)
    return [[c.strip() for c in r.split(" / ")] for r in body.split("; ")]


def _num(cell):
    return float(cell.replace("−", "-").replace(",", ""))


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

BUILT = {
    "1": ["B-1", "B-1.1", "B-1.2", "B-1.3", "B-1.4", "B-1.5", "B-1.6", "B-1.7", "B-1.8"],
    "2": ["B-2", "B-2.1", "B-2.2", "B-2.3", "B-2.4", "B-2.5", "B-2.6", "B-2.7", "B-2.8"],
    "3": ["B-3", "B-3.1", "B-3.2", "B-3.3", "B-3.4", "B-3.5", "B-3.6", "B-3.7"],
}


@pytest.mark.parametrize("example", sorted(BUILT))
def test_example_sections_present(example):
    for sid in BUILT[example]:
        assert sid in SEC, sid
        assert SEC[sid]["body"].strip()


def test_chapter_title_names_the_examples_held():
    title = APX["chapter_title"]
    assert title.startswith("Appendix B: Verification Examples")
    held = sorted(int(e) for e in BUILT)
    if held != list(range(1, 8)):
        assert re.search(rf"Examples? {held[0]}\b", title), title


def test_every_body_has_a_page_mark():
    for s in APX["sections"]:
        assert re.search(r"\(pp?\. \d+", s["body"]), s["section_id"]


def test_tables_have_page_marks():
    for s in APX["sections"]:
        for t in s["tables"]:
            assert re.search(r"\(p\. \d+\)", t), t[:60]


# ---------------------------------------------------------------------------
# Scatter patterns (rule 2a of the 2026-11-10 build brief)
# ---------------------------------------------------------------------------

_PRIME = "'ʹ′"
SCATTER = [
    ("isolated prime", re.compile(rf"(?:^|\s)[{_PRIME}](?:\s|$)")),
    ("(') ", re.compile(rf"\(\s*[{_PRIME}]\s*\)")),
    ("empty brackets", re.compile(r"\(\s*\)|\[\s*\]")),
    ("run of single letters", re.compile(r"(?:(?<=\s)|^)(?:[A-Za-zγφσδθ] ){6,}")),
    ("run of single digits", re.compile(r"(?:(?<=\s)|^)(?:\d ){5,}")),
]


_LIST_MARK = re.compile(r"(?:^|\s)(?:\d{1,2}|[a-z])$")


def _parens_balanced(text):
    """True when every ')' closes a '(' or ends a list marker such as "1)"."""
    depth = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth:
                depth -= 1
            elif not _LIST_MARK.search(text[max(0, i - 4):i]):
                return False
    return depth == 0


def _scatter(text):
    # the print's own "(ʹ)" where P-2.1 names the prime symbol is not scatter
    text = text.replace("prime symbol (ʹ)", "prime symbol")
    found = [name for name, rx in SCATTER if rx.search(text)]
    if not _parens_balanced(text):
        found.append("unbalanced ()")
    if text.count("[") != text.count("]"):
        found.append("unbalanced []")
    return found


def _repeated_rows(table):
    parts = [p.strip() for p in table.split(";")]
    return [a for a, b in zip(parts, parts[1:]) if a == b and len(a) > 25]


@pytest.mark.parametrize("text_layer", [
    # the PDF text layer's form of formula lines on pp. 599 and 606
    "( )( )( ) 1 250 0.25 18 1,125 h s A P q K H psf ft lb ft",
    ", , 2 0 0 2 48 985 1270 2540 4560 0 48 985 1270 toe M B B x x B = − ⋅ + ⋅ ⋅ − ⋅ = = ⋅ ∑",
    "0 1 1 v OT W x a W P F    = −    +    (xx)",
    "the effective friction angle φ ' is",
    "σ (') v0 is",
    "Ws2 = ((1.5 ft − 1 ft)(16 ft)/2(150 pcf)",
])
def test_scatter_scan_catches_text_layer_formulas(text_layer):
    assert _scatter(text_layer)


@pytest.mark.parametrize("name", sorted(p.name for p in TEXT.glob("*.json")))
def test_no_scatter_patterns(name):
    bad = []
    for s in _load(name)["sections"]:
        for field in ("body", "summary"):
            hits = _scatter(s[field])
            if hits:
                bad.append((s["section_id"], field, hits))
        for t in s["tables"] + s["key_points"]:
            hits = _scatter(t)
            if hits:
                bad.append((s["section_id"], t[:50], hits))
        for t in s["tables"]:
            if _repeated_rows(t):
                bad.append((s["section_id"], t[:50], "repeated row"))
    assert not bad, bad


def test_appendix_b_bodies_do_not_repeat_a_sentence_in_a_row():
    for s in APX["sections"]:
        sentences = [x.strip() for x in re.split(r"(?<=[.;])\s+", s["body"]) if len(x.strip()) > 40]
        for a, b in zip(sentences, sentences[1:]):
            assert a != b, (s["section_id"], a)


# ---------------------------------------------------------------------------
# Example 1 – cantilever cut wall (pp. 596-606)
# ---------------------------------------------------------------------------

def _x0_heel_surcharge(B):
    # p. 602: x0 = (1395·B² − 50,516)/(2790·B − 5435)
    return (1395.0 * B * B - 50516.0) / (2790.0 * B - 5435.0)


def _theta(B):
    # p. 602: θ = tan⁻¹[6795/(2790·B − 5435)]
    return math.degrees(math.atan(6795.0 / (2790.0 * B - 5435.0)))


def _b_calc(x0, theta, phi=37.0):
    # p. 603: B = 1.782x0²(1 − θ/φʹ)² + 4.308x0(1 − θ/90)² + 1.948
    return 1.782 * x0 * x0 * (1 - theta / phi) ** 2 + 4.308 * x0 * (1 - theta / 90.0) ** 2 + 1.948


def test_example_1_table_b2_rows_follow_the_printed_equations():
    rows = _rows(_table("B-1.6", "B-2"))
    data = [r for r in rows[1:] if len(r) == 5]
    assert len(data) == 12
    for r in data:
        if r[0].startswith("Using Solver: "):
            r[0] = r[0].split(": ")[1]
        b, x0, th, bc, diff = (_num(c) for c in r)
        if b == 7.68:  # the Solver row is printed from B = 7.677
            b = 7.677
        assert _x0_heel_surcharge(b) == pytest.approx(x0, abs=0.0015)
        assert _theta(b) == pytest.approx(th, abs=0.0015)
        assert _b_calc(x0, th) == pytest.approx(bc, abs=0.005)
        assert bc - b == pytest.approx(diff, abs=0.0015)


def test_example_1_widths_of_table_b3():
    # p. 601: 0 = 48985 − 1520·B − 423.33·B² -> 9.11 ft
    a, b, c = -423.33, -1520.0, 48985.0
    B_ot = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
    assert B_ot == pytest.approx(9.11, abs=0.005)
    # p. 601: FSL = 0.2056·B − 0.3691 = 1.5 -> 9.09
    assert (1.5 + 0.3691) / 0.2056 == pytest.approx(9.09, abs=0.005)
    rows = _rows(_table("B-1.7", "B-3"))
    assert [r[1] for r in rows[1:]] == ["9.11", "9.09", "7.68"]


def test_example_1_checks_at_design_width():
    B = 9.5
    # Table B-4 (p. 605): FSL = 1.58, x0/B = 0.35 (printed in each other's row), FBC = 6.35
    fsl = (1397 * B - 2508) / 6795
    assert fsl == pytest.approx(1.58, abs=0.005)
    x0 = (1270 * B * B - 48985) / (2540 * B - 4560)
    assert x0 / B == pytest.approx(0.353, abs=0.001)
    x0q = _x0_heel_surcharge(B)
    th = _theta(B)
    R = 2790 * B - 5435
    q_ult = 3 * 140 * 42.92 * (1 - th / 90) ** 2 + x0q * 140 * 53.27 * (1 - th / 37) ** 2
    assert q_ult / (R / (2 * x0q)) == pytest.approx(6.35, abs=0.01)
    # p. 605: FOT = (1270·B² − 4840)/44145 = 2.49
    assert (1270 * B * B - 4840) / 44145 == pytest.approx(2.49, abs=0.005)
    # p. 606: 48,985 = 1270·B² -> 6.21 ft; x0 = 5.61(1 − 1/2.49) = 3.36
    assert math.sqrt(48985 / 1270) == pytest.approx(6.21, abs=0.005)
    assert 5.61 * (1 - 1 / 2.49) == pytest.approx(3.36, abs=0.005)


def test_example_1_print_slip_kept_with_note():
    body = SEC["B-1.3"]["body"]
    assert "2,240·(B − 3.5 ft) = 2,240B − 4560 (lb/ft)" in body
    assert "2,240B − 7,840" in body
    # R as printed follows from −7,840
    assert 300 + 2240 == 2540 and 2400 + 600 - 7840 + 280 == -4560


def test_example_1_dm7_2_lookups():
    from geotech_references.dm7_2.chapter4 import (
        active_earth_pressure_resultant, rankine_active_pressure_coefficient)
    from geotech_references.dm7_2.chapter5 import (
        check_eccentricity_one_direction, meyerhof_Ngamma, meyerhof_hansen_Nq,
        meyerhof_inclination_factors)
    # p. 599: Rankine KA "equal to 0.25" for φʹ = 37 deg (Figure B-2)
    assert rankine_active_pressure_coefficient(37.0) == pytest.approx(0.25, abs=0.002)
    # p. 599: Ph2 = 0.5(0.25)(140)(18)² = 5,670 lb/ft
    assert active_earth_pressure_resultant(0.25, 140.0, 18.0) == pytest.approx(5670.0)
    # p. 603: Meyerhof Nq = 42.92, Nγ = 53.27 for 37 degrees
    assert meyerhof_hansen_Nq(37.0) == pytest.approx(42.92, abs=0.005)
    assert meyerhof_Ngamma(37.0) == pytest.approx(53.27, abs=0.005)
    # p. 603: iq = (1 − θ/90)², iγ = (1 − θ/φʹ)² at the Solver row θ = 23.032
    _, iq, ig = meyerhof_inclination_factors(23.032, 37.0)
    assert iq == pytest.approx((1 - 23.032 / 90) ** 2, rel=1e-6)
    assert ig == pytest.approx((1 - 23.032 / 37) ** 2, rel=1e-6)
    # B-1.2/B-1.8: resultant in the middle third at B = 9.5 ft (x0/B = 0.353)
    e = 9.5 / 2 - 0.353 * 9.5
    assert check_eccentricity_one_direction(e, 9.5)


# ---------------------------------------------------------------------------
# Example 2 – anchored cut wall (pp. 606-617)
# ---------------------------------------------------------------------------

def test_example_2_table_b6_forces():
    rows = {r[0]: r for r in _rows(_table("B-2.3", "B-6"))[1:] if r[0].isdigit()}
    assert len(rows) == 11
    # rows with numeric heights: ΔP = [(Δσʹh,top + Δσʹh,bot)/2]·hshape (p. 610)
    for fid in ("1", "2", "3", "4", "10"):
        top, bot, h, dp = (_num(rows[fid][i]) for i in (4, 5, 6, 7))
        assert (top + bot) / 2 * h == pytest.approx(dp, rel=0.003), fid
    # Δσʹh = K·Δσʹv for the active rows
    for fid in ("1", "2", "3", "4", "5", "6", "7"):
        k, vbot, hbot = _num(rows[fid][3]), _num(rows[fid][2]), _num(rows[fid][5])
        assert k * vbot == pytest.approx(hbot, abs=1.0), fid


def _sum_moments(D):
    # Table B-7 (p. 610), moments about the tierod elevation
    return (26040 - 642 + 38500 + 34346 + 291
            + (125 + 172 + 237) * D * (19 + D / 2)
            + (7.2 - 69.1) * D * D * (19 + 2 * D / 3)
            + 125 * (D + 16) * (19 + D - (16 + D) / 2))


def test_example_2_embedment_and_tierod_force():
    lo, hi = 10.0, 20.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _sum_moments(mid) > 0:
            lo = mid
        else:
            hi = mid
    D = (lo + hi) / 2
    assert D == pytest.approx(14.45, abs=0.01)                  # p. 611
    assert math.ceil(1.2 * 14.45) == 18                         # design embedment
    # horizontal equilibrium with Table B-6 forces at D = 14.45 ft: −9,568 lb/ft printed
    sum_p = 3720 + 642 + 3850 + 2642 + 125 + (125 + 172 + 237) * 14.45 \
        + (7.2 - 69.1) * 14.45 ** 2 + 125 * (14.45 + 16)
    assert -sum_p == pytest.approx(-9568, rel=0.002)
    # p. 611: tierod 9,600 lb/ft x 6 ft = 58 kips; connections 69 kips (1.2 x 9,568 rounds up to 11,500)
    assert round(9600 * 6 / 1000) == 58
    assert math.ceil(1.2 * 9568 / 100) * 100 == 11500 and 11500 * 6 / 1000 == 69.0
    assert "11,400 lb/ft" in SEC["B-2.4"]["body"] and "11,500" in SEC["B-2.4"]["body"]


def test_example_2_table_b8_sum_and_section():
    rows = _rows(_table("B-2.6", "B-8"))
    moments = [_num(r[4]) for r in rows[1:] if len(r) == 5]
    assert len(moments) == 7
    assert sum(moments) == pytest.approx(63370, abs=2)
    # p. 614: Sreq = 39.3 ft-k (12 in/ft)/38.5 ksi = 12.25 in³ per foot
    assert 39.3 * 12 / 38.5 == pytest.approx(12.25, abs=0.005)


def test_example_2_anchor():
    # p. 615: min h1 = 9600/((150)(2))·tan 8.7° = 4.9 ft
    assert 9600 / 300 * math.tan(math.radians(8.7)) == pytest.approx(4.9, abs=0.05)
    # p. 616: 9600 = 3705 + 1235(h − 6) + 47.1(h − 6)² -> h = 10.1 ft
    x = (-1235 + math.sqrt(1235 ** 2 + 4 * 47.1 * (9600 - 3705))) / (2 * 47.1)
    assert 6 + x == pytest.approx(10.1, abs=0.05)
    # Table B-12 (p. 617): yresultant = 3.93 ft; tierod at 5.1 ft is about 14 inches higher
    y = (26306 + 10128 + 1109) / (3705 + 5064 + 792)
    assert y == pytest.approx(3.93, abs=0.005)
    assert (5.1 - y) * 12 == pytest.approx(14, abs=0.5)


def test_example_2_dm7_2_lookups():
    from geotech_references.dm7_2.chapter4 import (
        figure_4_36_moment_reduction, log_spiral_passive_coefficient,
        rankine_active_pressure_coefficient, relative_flexibility_anchored_bulkhead)
    # Table B-5 (p. 608): Rankine KA 0.31 and 0.25
    assert rankine_active_pressure_coefficient(32.0) == pytest.approx(0.31, abs=0.005)
    assert rankine_active_pressure_coefficient(37.0) == pytest.approx(0.25, abs=0.005)
    # factored angles φʹ* = tan⁻¹(tan φʹ/2): 17.4 and 20.6 printed
    phi1 = math.degrees(math.atan(math.tan(math.radians(32.0)) / 2))
    phi2 = math.degrees(math.atan(math.tan(math.radians(37.0)) / 2))
    assert phi1 == pytest.approx(17.4, abs=0.05)
    assert phi2 == pytest.approx(20.6, abs=0.06)
    # KP,h = KP·cos δ* with KP from Equation 4-12
    kph1 = log_spiral_passive_coefficient(17.4, 8.7) * math.cos(math.radians(8.7))
    assert kph1 == pytest.approx(2.1, abs=0.01)
    kph2 = log_spiral_passive_coefficient(20.6, 10.3) * math.cos(math.radians(10.3))
    # DIFFERENCE: the print carries 2.4 for layer 2; Equation 4-12 gives 2.47
    # (noted in B-2.3).
    assert kph2 == pytest.approx(2.47, abs=0.01)
    # p. 614: ρ = 18.52, Rowe medium dense sand 0.62, Mdesign = 39.3 ft-k
    rho = relative_flexibility_anchored_bulkhead(24.0 * 12.0, 14.45 * 12.0, 29.0e6, 84.4)
    assert rho == pytest.approx(18.52, abs=0.01)
    ratio = figure_4_36_moment_reduction(rho, "medium_dense_and_dense_coarse_grained")
    assert ratio == pytest.approx(0.62, abs=0.005)
