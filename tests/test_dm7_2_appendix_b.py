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
    "4": ["B-4", "B-4.1", "B-4.2", "B-4.3", "B-4.4", "B-4.5", "B-4.6"],
    "5": ["B-5", "B-5.1", "B-5.2", "B-5.3", "B-5.4", "B-5.5", "B-5.6", "B-5.7", "B-5.8"],
    "6": ["B-6", "B-6.1", "B-6.2", "B-6.3", "B-6.3.1", "B-6.3.2", "B-6.3.3", "B-6.3.4", "B-6.3.5",
          "B-6.3.6", "B-6.4"],
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


# ---------------------------------------------------------------------------
# Example 4 – mat foundation (pp. 627-633)
# ---------------------------------------------------------------------------

def test_example_4_modulus_and_immediate_settlement():
    # p. 628: qnet = (3)(150) + 1,000,000/25² = 2050 psf
    assert 3 * 150 + 1_000_000 / 25 ** 2 == pytest.approx(2050)
    # Table B-23 (p. 630) from Es,u ≈ 138σʹz·(1 + OCM/σʹz)^0.8 with the printed σʹz
    rows = _rows(_table("B-4.3", "B-23"))[1:]
    for r in rows:
        sz, ocm, ocr, es = (_num(c) for c in r[1:])
        assert 1 + ocm / sz == pytest.approx(ocr, abs=0.05)
        assert 138 * sz * (1 + ocm / sz) ** 0.8 == pytest.approx(es, rel=0.002)
    # p. 630: Es,u = 889 ksf; si = 0.64 in
    es = (509 * 10 + 661 * 35 + 1281 * 30) / 75
    assert es == pytest.approx(889, abs=0.5)
    si = 0.97 * 0.2 * 120 * 2.05 / 889 * 12
    assert si == pytest.approx(0.64, abs=0.005)


def test_example_4_consolidation_tables():
    b24 = {r[0]: r for r in _rows(_table("B-4.4", "B-24"))[1:]}
    b25 = {r[0]: r for r in _rows(_table("B-4.4", "B-25"))[1:]}
    b26 = [r for r in _rows(_table("B-4.4", "B-26"))[1:] if r[0].isdigit()]
    assert len(b26) == 9
    total = 0.0
    for r in b26:
        sub = r[0]
        sz0 = _num(b24[sub][9])
        ocm, sp, dze, sze, dzl, szf = (_num(c) for c in b25[sub][2:])
        assert sz0 + ocm == pytest.approx(sp)                    # σʹp = σʹz0 + OCM
        assert sz0 + dze == pytest.approx(sze, abs=1)            # σʹze
        assert sze + dzl == pytest.approx(szf, abs=1)            # σʹzf
        cc, cr, eps, h, dh = (_num(c) for c in r[2:])
        e = cr * math.log10(min(sp, szf) / sze) + cc * math.log10(max(sp, szf) / sp)
        assert e == pytest.approx(eps, abs=0.00006)              # p. 632
        assert eps * h == pytest.approx(dh, abs=0.0011)
        total += e * h
    assert total == pytest.approx(0.195, abs=0.0015)
    # "approximately 2.4 inches": 0.195 ft is 2.34 in (noted in B-4.4)
    assert 0.195 * 12 == pytest.approx(2.34)


def test_example_4_table_b24_stresses():
    for r in _rows(_table("B-4.4", "B-24"))[1:]:
        mid, gam, s, u, se = (_num(c) for c in r[5:])
        assert u == pytest.approx(max(0.0, (195 - mid) * 62.4), abs=0.5)
        assert s - u == pytest.approx(se, abs=0.5)


def test_example_4_dm7_2_lookups():
    from geotech_references.dm7_2.chapter5 import (
        modulus_of_subgrade_reaction, subgrade_modulus_from_elastic_parameters,
        subgrade_modulus_time_dependent)
    # p. 633: ks = 2.05 ksf / 0.7 in = 20.3 pci
    ks = modulus_of_subgrade_reaction(2.05 * 1000 / 144, 0.7)
    assert ks == pytest.approx(20.3, abs=0.05)
    # Eq. 5-39: ksc = s·ks/(s + sc) = 4.6 pci with s = 0.7 in, sc = 2.4 in
    assert subgrade_modulus_time_dependent(0.7, 2.4, ks) == pytest.approx(4.6, abs=0.05)
    # Es/(B·μ0·μ1) equals q/si before si is rounded to 0.7 in (0.64 in: 22.1 pci)
    k_el = subgrade_modulus_from_elastic_parameters(120.0, 889.0, 0.97, 0.2)  # ksf/ft
    si_ft = 0.97 * 0.2 * 120 * 2.05 / 889
    assert k_el == pytest.approx(2.05 / si_ft, rel=1e-9)


# ---------------------------------------------------------------------------
# Example 5 – pile group capacity and settlement (pp. 633-643)
# ---------------------------------------------------------------------------

def test_example_5_loads_and_single_pile_resistance():
    # p. 635: Wcap+soil = 21²[(3.5)(0.15) + (8 − 3.5)(0.12)] = 470 kips
    assert 21 ** 2 * (3.5 * 0.15 + 4.5 * 0.12) == pytest.approx(470, abs=0.5)
    # p. 636: "1500 + 470 = 1976" as printed (1970); Q'g = 3520 follows from 1976
    assert "1500 kips + 470 kips = 1976 kips" in SEC["B-5.3"]["body"]
    assert 1.25 * 1976 + 1.75 * 600 == pytest.approx(3520)
    # p. 637: Rs = 199, Rb = 27, Rn = 226, n(ηg Rr,s) = 3876
    rs = 40 * 2 + 10 * 2.9 + 15 * 6
    assert rs == pytest.approx(199)
    assert 9 * 3000 * 1 / 1000 == pytest.approx(27)
    assert 49 * 1.0 * 0.35 * 226 == pytest.approx(3876, abs=0.5)
    # p. 638: block failure
    su1 = (0.5 * 40 + 3 * 20) / 60
    assert su1 == pytest.approx(1.33, abs=0.005)
    rn_block = 2 * 60 * (18 + 18) * 1.33 + 18 * 18 * 3 * 9
    assert rn_block == pytest.approx(14494, abs=1)
    assert 0.6 * 14494 == pytest.approx(8696, abs=0.5)


def test_example_5_table_b28_neutral_plane():
    rows = _rows(_table("B-5.5", "B-28"))
    data = {r[0]: [_num(c) for c in r[1:]] for r in rows[1:5]}
    # load curve: 40 kips at the bearing grade (8 ft), −Δp of 2, 2.9 and 6 k/ft below
    assert data["48"][0] == pytest.approx(40 + 2 * 40)
    assert data["58"][0] == pytest.approx(120 + 2.9 * 10)
    assert data["73"][0] == pytest.approx(149 + 6 * 15)
    for i, rb in ((1, 0.0), (2, 13.5), (3, 27.0)):
        assert data["8"][i] == pytest.approx(199 + rb, abs=0.5)
        assert data["73"][i] == pytest.approx(rb, abs=0.5)
    # neutral plane in the transition zone (48 to 58 ft): 120 + 2.9x = Rz(48) − 2.9x
    znp = [_num(c) for c in rows[5][1:]]
    pmax = [_num(c) for c in rows[6][1:]]
    for i, rb in enumerate((0.0, 13.5, 27.0)):
        x = (119 + rb - 120) / (2 * 2.9)
        assert 48 + x == pytest.approx(znp[i], abs=0.6)
        assert 120 + 2.9 * x == pytest.approx(pmax[i], abs=0.8)


def test_example_5_table_b30_consolidation():
    b29 = {r[0]: [_num(c) for c in r[1:]] for r in _rows(_table("B-5.7", "B-29"))[1:]}
    rows = [r for r in _rows(_table("B-5.7", "B-30"))[1:] if r[0].isdigit()]
    assert len(rows) == 10
    total = 0.0
    for r in rows:
        sz0 = b29[r[0]][4]
        sp, dfill, dpile, szf, eps, h0, dh = (_num(c) for c in r[1:])
        assert sz0 + 5000 == pytest.approx(sp)                       # OCM = 5000 psf (Figure B-16)
        assert dfill == pytest.approx(8 * 120)                       # 8 ft of fill at 120 pcf
        assert sz0 + dfill + dpile == pytest.approx(szf, abs=1)
        e = 0.01 * math.log10(min(sp, szf) / sz0) + 0.10 * math.log10(max(sp, szf) / sp)
        assert e == pytest.approx(eps, abs=0.00006)
        assert eps * h0 == pytest.approx(dh, abs=0.0011)
        total += e * h0
    # printed ΔH sum to 0.154 ft, unrounded strains to 0.155 ft: "0.15 ft (1.9 in)"
    printed = sum(_num(r[7]) for r in rows)
    assert printed == pytest.approx(0.154, abs=0.0005)
    assert total == pytest.approx(0.155, abs=0.001)
    assert total * 12 == pytest.approx(1.9, abs=0.05)
    # Table B-29: σʹz,0 = 40 ft of soft clay at 40 pcf + stiff clay at 55 pcf below 48 ft
    for sub, (ztop, h0, zbot, zmid, sz0) in b29.items():
        assert ztop + h0 == zbot and zmid == pytest.approx((ztop + zbot) / 2)
        assert 40 * 40 + 55 * (zmid - 48) == pytest.approx(sz0)


def test_example_5_elastic_shortening():
    rows = _rows(_table("B-5.7", "B-31"))[1:]
    ea = 4000 * 144  # kips: E = 4,000 ksi, A = 144 in²
    total = 0.0
    for r in rows:
        L0, pavg, dl = _num(r[2]), _num(r[7]), _num(r[8])
        assert pavg * L0 / ea == pytest.approx(dl, abs=0.00006)
        total += dl
    assert total == pytest.approx(0.006, abs=0.0005)


def test_example_5_dm7_2_lookups():
    from geotech_references.dm7_2.chapter6 import (
        alpha_method_unit_shaft_resistance, alpha_tomlinson_transition, block_failure_Nc,
        block_failure_resistance, drag_force_check)
    # p. 636: fs = α·su
    assert alpha_method_unit_shaft_resistance(1.0, 500.0) == pytest.approx(500.0)
    assert alpha_method_unit_shaft_resistance(0.5, 3000.0) == pytest.approx(1500.0)
    # Equation 6-9: α = 0.28(su/Pa)^−0.44 -> fs,transition = ±720 psf
    alpha = alpha_tomlinson_transition(3000.0, 2116.0)
    assert alpha * 3000.0 == pytest.approx(720.0, abs=1.0)
    # p. 638: Nc = 10 -> 9; block resistance 14494 kips with depth 60 ft, plan 18 ft x 18 ft
    assert block_failure_Nc(18.0, 18.0, 60.0) == 9.0
    assert block_failure_resistance(60.0, 18.0, 18.0, 1.33, 3.0, 9.0) == pytest.approx(14494, abs=1)
    # p. 640: Equation 6-80, 1.25(40) + 1.1(133 − 40) = 152 ≤ 200 kips
    assert drag_force_check(40.0, 133.0, 200.0) is True


# ---------------------------------------------------------------------------
# Example 6 – lateral load analysis (pp. 644-651)
# ---------------------------------------------------------------------------

_PC, _MC, _N = 265.0, 45457.0, 49


def _p_cap_piles(y, a, n):
    # p. 648: Pcap+piles = 49(265)[(1/a)(yt/12 in)]^(1/n) + [max{15; 204·yt/(0.85yt + 0.252)}] − 15
    piles = _N * _PC * (y / (a * 12.0)) ** (1.0 / n)
    cap = max(15.0, 204.0 * y / (0.85 * y + 0.252)) - 15.0
    return piles, cap


def test_example_6_p_multiplier_and_characteristic_values():
    rows = _rows(_table("B-6.3.1", "B-32"))
    pms = [float(re.search(r"= (0\.\d+)$", r[1]).group(1)) for r in rows[1:5]]
    for (m, c), pm in zip(((0.06, 0.64), (0.11, 0.34), (0.14, 0.16), (0.16, 0.04)), pms):
        assert m * 3 + c == pytest.approx(pm, abs=0.005)
    assert (pms[0] + pms[1] + pms[2] + 4 * pms[3]) / 7 == pytest.approx(0.593, abs=0.0005)
    # p. 646: RI = 64/(12π) = 1.70; Pc = 265 kips; Mc = 45457 in-kips
    ri = 64 / (12 * math.pi)
    assert ri == pytest.approx(1.70, abs=0.005)
    ratio = 500 * 0.593 / (4000 * 1.70 * 144000)
    assert 7.34 * 12 ** 2 * 4000 * 1.70 * ratio ** 0.68 == pytest.approx(265, abs=0.5)
    assert 3.86 * 12 ** 3 * 4000 * 1.70 * ratio ** 0.46 == pytest.approx(45457, rel=0.001)


def test_example_6_cap_pressures():
    assert 0.27 * 4.5 * 120 == pytest.approx(146, abs=0.5)
    assert 0.27 * 8 * 120 == pytest.approx(259, abs=0.5)
    assert 3.7 * 4.5 * 120 == pytest.approx(1998)
    assert 3.7 * 8 * 120 == pytest.approx(3552)
    assert 0.5 * (146 + 259) * 3.5 * 21 / 1000 == pytest.approx(15, abs=0.2)
    assert 0.5 * (1998 + 3552) * 3.5 * 21 / 1000 == pytest.approx(204, abs=0.1)
    assert 0.006 * 3.5 * 12 == pytest.approx(0.252)


def test_example_6_load_deflection_values_of_figures_b21_b22():
    # P'' = (1/0.8)[(1.25)(100) + (1.75)(200)] = 594 kips
    assert (1.25 * 100 + 1.75 * 200) / 0.8 == pytest.approx(594, abs=0.5)
    for y, a, n, printed in ((1.2, 50, 1.822, 606), (1.2, 14, 1.846, 1070),
                             (0.5, 50, 1.822, 401), (0.5, 14, 1.846, 691)):
        piles, cap = _p_cap_piles(y, a, n)
        assert piles + cap == pytest.approx(printed, abs=1.5)
    # B-6.3.6: "at the service limit state of 0.5 inch ... the pile group ... 265 kips" (free head)
    assert _p_cap_piles(0.5, 50, 1.822)[0] == pytest.approx(265, abs=0.5)


def test_example_6_table_b34():
    rows = {r[0]: r[1:] for r in _rows(_table("B-6.3.6", "B-34"))[1:]}
    for i, (a, n, am, nm) in enumerate(((50, 1.822, 0.855, 1.288), (14, 1.846, 0.782, 1.249))):
        y = _num(rows["yt"][i].replace(" in.", ""))
        p_group = _num(rows["Pt,group"][i].replace(" kips", ""))
        m = _num(rows["Mmax,corner"][i].replace(" ft-kips", ""))
        lo, hi = 0.01, 1.2                                          # solve Pcap+piles = 300 kips
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if sum(_p_cap_piles(mid, a, n)) < 300 else (lo, mid)
        assert lo == pytest.approx(y, abs=0.005)
        assert _p_cap_piles(lo, a, n)[0] == pytest.approx(p_group, abs=1.0)
        assert 1.2 / 12 * am * _MC * (p_group / (_N * _PC)) ** nm == pytest.approx(m, abs=0.5)
    # 0.5 in: 26 ft-kip (free, from 265 kips; the printed line's 259 kips gives 25) and 69 (fixed)
    assert 0.1 * 0.855 * _MC * (265 / (_N * _PC)) ** 1.288 == pytest.approx(26, abs=0.5)
    assert 0.1 * 0.855 * _MC * (259 / (_N * _PC)) ** 1.288 == pytest.approx(25.1, abs=0.1)
    fixed_pile = _p_cap_piles(0.5, 14, 1.846)[0]
    assert 0.1 * 0.782 * _MC * (fixed_pile / (_N * _PC)) ** 1.249 == pytest.approx(69, abs=0.5)


def test_example_6_dm7_2_lookups():
    from geotech_references.dm7_2.chapter4 import (
        rankine_active_pressure_coefficient, rankine_passive_pressure_coefficient)
    from geotech_references.dm7_2.chapter6 import (
        clm_load_from_deflection, clm_max_moment, table_6_36_clm, table_6_37_clm)
    # p. 647: Rankine 0.27 and 3.7 for 35 degrees
    assert rankine_active_pressure_coefficient(35.0) == pytest.approx(0.27, abs=0.005)
    assert rankine_passive_pressure_coefficient(35.0) == pytest.approx(3.7, abs=0.05)
    # p. 648: Table 6-31 constants as printed in the example (the library's Table 6-36 key)
    free = table_6_36_clm("clay", "Pt/Pc", "free")
    fixed = table_6_36_clm("clay", "Pt/Pc", "fixed")
    assert (free["a"], free["n"]) == (50.0, 1.822) or (free["a"], free["n"]) == (50, 1.822)
    assert (fixed["a"], fixed["n"]) == (14.0, 1.846) or (fixed["a"], fixed["n"]) == (14, 1.846)
    # Table B-34 free head: Pt,group = 197 kips at yt = 0.29 in.
    p = _N * clm_load_from_deflection(0.29, 12.0, _PC, free["a"], free["n"])
    assert p == pytest.approx(197, abs=0.5)
    # p. 650: Equation 6-71 constants and the 18 ft-kips of Table B-34
    m_free = table_6_37_clm("clay", "free")
    assert (m_free["a"], m_free["n"]) == (0.855, 1.288)
    assert 1.2 / 12 * clm_max_moment(197 / _N, _PC, _MC, m_free["a"], m_free["n"]) == \
        pytest.approx(18, abs=0.5)
