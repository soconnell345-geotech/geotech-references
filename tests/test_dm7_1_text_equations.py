"""DM 7.1 chapter text: the stored equations read as UFS 3-220-10 (16 Jan 2026) prints them.

Each test pins the term that tells the printed form from the form the text held
before (app BACKLOG REF-79). Pages are PDF pages; the printed page is 28 lower.
"""
from functools import lru_cache

import pytest

from geotech_references._retrieval import load_chapter


@lru_cache(maxsize=None)
def _chapter(ch):
    return load_chapter("dm7_1", ch)


def _sec(ch, sid):
    hits = [s for s in _chapter(ch)["sections"] if s["section_id"] == sid]
    assert len(hits) == 1, (sid, len(hits))
    return hits[0]


def _eq(ch, sid, eq_id):
    hits = [e for e in _sec(ch, sid)["equations"] if e["id"] == eq_id]
    assert len(hits) == 1, (sid, eq_id, len(hits))
    return hits[0]["description"]


def _kps(ch, sid):
    return " ".join(_sec(ch, sid)["key_points"])


def _sections_with(ch, eq_id):
    return [s["section_id"] for s in _chapter(ch)["sections"]
            if any(e["id"] == eq_id for e in s["equations"])]


# Chapter 1, PDF p. 60: Is(50) = F P / d^2 and F = sqrt(De / 50).
def test_point_load_index_eq_1_4_and_1_5():
    s = _sec(1, "1-4.3.2")
    assert "Is(50) = F · P / d²" in s["body"]
    assert "F = √(De / 50)" in s["body"]
    assert "P / (F · d²)" not in s["body"] + _kps(1, "1-4.3.2")
    assert "F · P / d²" in _eq(1, "1-4.3.2", "Eq. 1-4")
    assert "√(De / 50)" in _eq(1, "1-4.3.2", "Eq. 1-5")


# Chapter 2, PDF p. 116 prints KD = (p1 - p0)/sigma'v0; Eq. 8-10 (p. 434) prints (p0 - u0)/sigma'v.
def test_dmt_kd_kept_as_printed_with_note():
    s = _sec(2, "2-7.3.1")
    assert "KD = (p1 - p0) / σʹv0" in s["body"]
    assert "Equation 8-10" in s["body"]
    assert "KD = (p1 − p0)/σ′v0" in _kps(2, "2-7.3.1")


# Chapter 3, PDF p. 198: Eq. 3-5 k = cv mv gamma_w is printed in 3-2.7.3, not 3-3.1.
def test_eq_3_5_filed_where_printed():
    assert _sections_with(3, "Eq. 3-5") == ["3-2.7.3"]
    assert "k = cv · mv · γw" in _sec(3, "3-2.7.3")["body"]


# Chapter 3, PDF p. 180: the UCT section prints no su = qu/2.
def test_uct_key_points_hold_only_the_print():
    assert "qu/2" not in _kps(3, "3-2.4.2.1")


# Chapter 4, PDF pp. 213-214: Table 4-2.
@pytest.mark.parametrize("row, term", [
    ("Table 4-2 (Uniform Line Load)", "(2·P / π) · (z³ / R⁴)"),
    ("Table 4-2 (Rectangular Area)", "tan⁻¹(y·x / (z·R3)) + (x·y·z / R3)"),
    ("Table 4-2 (Triangular Load)", "(q0 / π) · [x·α / a + ((a + b − x) / b) · β]"),
    ("Table 4-2 (Slope Load)", "(q0 / (π·a)) · (x·β + z)"),
    ("Table 4-2 (Terrace Load)", "(q0 / (π·a)) · (a·β + x·α)"),
    ("Table 4-2 (Point Load)", "R = √(x² + y² + z²)"),
])
def test_table_4_2_rows(row, term):
    assert term in _eq(4, "4-3.2.2", row)


def test_table_4_2_line_load_has_no_4p():
    assert "4P" not in _eq(4, "4-3.2.2", "Table 4-2 (Uniform Line Load)")


# Chapter 4, PDF p. 239: Eq. 4-12 sigma_h = gamma' z - su is printed in 4-5.5.2.
def test_eq_4_12_filed_where_printed():
    assert _sections_with(4, "Eq. 4-12") == ["4-5.5.2"]
    assert "σh = γʹ · z − su   (4-12)" in _sec(4, "4-5.5.2")["body"]


# Chapter 4, PDF pp. 229-231: Tables 4-7 and 4-8 are tunnelling tables, not the reading list or notation.
def test_reading_and_notation_list_no_tables():
    assert _sec(4, "4-7")["tables"] == []
    assert _sec(4, "4-8")["tables"] == []


# Chapter 5, PDF p. 255: s = Delta H = sum of eps_z,i H_i.
def test_eq_5_4():
    assert "s = ΔH = Σ(i=1..n) εz,i · Hi" in _sec(5, "5-3.1")["body"]
    assert "ΣHi =" not in _sec(5, "5-3.1")["body"]


# Chapter 5, PDF p. 260: Eq. 5-7 sums (Iz,i/Es,i) zi; the where-list prints C1 for the time factor.
def test_eq_5_7():
    body = _sec(5, "5-4.1.2")["body"]
    assert "Σ(i=1..n) [(Iz,i / Es,i)·zi]  (Eq. 5-7)" in body
    assert "Δzi" not in body
    assert "Equation 5-9 gives this time correction as C2" in body


# Chapter 5, PDFs p. 282-296: formulas the text left out.
@pytest.mark.parametrize("sid, eq_id, term", [
    ("5-5.4", "Eq. 5-19", "Cεα ≈ 10⁻⁴ · wn"),
    ("5-7.3", "Eq. 5-20", "log[1 + qf/σ′z0] / log[1 + (qf/σ′z0)·(1 + qs/qf)]"),
    ("5-7.3", "Eq. 5-21", "(Cα/Cc)·log(t/tp)"),
    ("5-7.4", "Eq. 5-22", "Tr = (1/8)·(Fn + Fs + Fr)·ln[1 / (1 − Ūr)]"),
    ("5-7.4", "Eq. 5-25", "Fs ≈ (kh / ks)·ln(s)"),
    ("5-7.4.1", "Eq. 5-27", "Ūc = 100 − (100 − Ūr)(100 − Ūz) / 100"),
])
def test_chapter_5_formulas(sid, eq_id, term):
    assert term in _eq(5, sid, eq_id)


def test_chapter_5_body_formulas():
    assert "dw = 2(a + b) / π  (Eq. 5-24)" in _sec(5, "5-7.4")["body"]
    assert "dc = √(ch · t / Tr)  (Eq. 5-28)" in _sec(5, "5-7.4.2")["body"]


# Chapters 5 and 6: equations filed under sections that only cite them.
@pytest.mark.parametrize("ch, eq_id, where", [
    (5, "Eq. 5-9", ["5-4.1.2"]),
    (5, "Eq. 5-15", ["5-5.3"]),
    (5, "Eq. 5-22", ["5-7.4"]),
    (6, "Eq. 6-3", ["6-2.2"]),
    (6, "Eq. 6-5", ["6-2.2"]),
    (6, "Eq. 6-11", ["6-2.4.2"]),
    (7, "Eq. 7-1", ["7-3"]),
])
def test_equations_only_where_printed(ch, eq_id, where):
    assert _sections_with(ch, eq_id) == where


# Chapter 6, PDF p. 353: FSg = kg/ks = psi_g tg / ks.
def test_eq_6_16():
    assert "FSg = kg / ks = ψg · tg / ks   (6-16)" in _sec(6, "6-5.3.2")["body"]
    assert "FSg = kg / ks = ψg · tg / ks" in _eq(6, "6-5.3.2", "Eq. 6-16")
    assert "≥ FSg" not in _kps(6, "6-5.3.2")


# Chapter 6 PDF p. 328 and chapter 8 PDF p. 490: the constant's unit is cm/(s·mm²).
def test_kozeny_carman_unit():
    assert "1.99×10^2 cm/(s·mm^2)" in _sec(6, "6-3.3")["body"]
    assert "1.99×10² cm/(s·mm²)" in _sec(8, "8-7.2")["body"]


# Chapter 7, PDF p. 385: Eq. 7-2 S = i gamma_w is printed in 7-5.2 Seepage Forces.
def test_eq_7_2_in_section_7_5_2():
    assert _sections_with(7, "Eq. 7-2") == ["7-5.2"]
    s = _sec(7, "7-5.2")
    assert s["title"] == "Seepage Forces"
    assert "S = i · γw   (7-2)" in s["body"]


# Chapter 8, PDF p. 434: phi' = 31 + KD / (0.236 + 0.066 KD).
def test_eq_8_11():
    assert "φ′ = 31 + KD / (0.236 + 0.066·KD)" in _eq(8, "8-2.1.4", "Eq. 8-11")
    assert "0.236·KD +" not in _eq(8, "8-2.1.4", "Eq. 8-11") + _kps(8, "8-2.1.4")


# Chapter 8, PDF p. 455: qt as printed; the note cites the (1 - a) form only where a held manual prints it
# (FHWA-NHI-16-072, GEC 5, Eq. 4.23, p. 4-29).
def test_eq_8_25_qt_note():
    body = _sec(8, "8-3.3")["body"]
    assert "qc + u·(1+a) [As printed" in body
    assert "FHWA-NHI-16-072 (GEC 5, November 2016), Eq. 4.23, p. 4-29, prints qt = qc + u2(1 − a)" in body
    eq = _eq(8, "8-3.3", "Eq. 8-25")
    assert "Eq. 4.23, p. 4-29, prints qt = qc + u2(1 − a)" in eq
    assert "usually written" not in body + eq


# Chapter 8, PDF p. 457: Table 8-11.
def test_table_8_11_key_points():
    kps = _kps(8, "8-3.5")
    assert "0.35·(0.47·KD)^1.14" in kps
    assert "(su/σ′v)NC·(0.5·KD)^1.25 ≈ 0.22·(0.5·KD)^1.25" in kps


# Chapter 8: Eq. 8-30 points at its own function.
def test_eq_8_30_function():
    e = [x for x in _sec(8, "8-4.1.2")["equations"] if x["id"] == "Eq. 8-30"][0]
    assert e["implemented_in"].endswith("intrinsic_compression_index_from_el")


# Chapter 8, PDF p. 477: E = (2/3)(1 + nu) Eu.
def test_eq_8_36():
    d = _eq(8, "8-5.1", "Eq. 8-36")
    assert "E = (2/3)·(1 + ν)·Eu" in d
    assert "Eu / (2(1+ν)/3)" not in d


# Chapter 8, PDF p. 481: Tables 8-20 and 8-21.
def test_table_8_20_key_points():
    kps = _kps(8, "8-5.3")
    assert "driven piles 275–550, 550–700, 700–1100" in kps
    assert "USACE (1990) 100–250 (loose), 250–1000 (medium), 1000–2000 (dense)" in kps
    assert "2000 Pa" not in kps


def test_table_8_21_begemann():
    kps = _kps(8, "8-5.3.1")
    assert "E/Pa ≈ 39.5 + C(N − 6) for N ≥ 15" in kps
    assert "C(N+6)−39.5" not in kps


# Chapter 8, PDF p. 487: Table 8-25.
def test_table_8_25_key_points():
    kps = _kps(8, "8-7.1")
    assert "Sandy gravel, clean sand, and fine sand: k = 10⁻³ to 10⁻⁵ m/s" in kps
    assert "Sand, dirty sand, and silty sand: k = 10⁻⁵ to 10⁻⁷ m/s" in kps


# Chapter 8, PDF p. 483: Table 8-22's first row as printed, with what FHWA-NHI-05-037 Table 5-34 (p. 5-53) prints.
def test_table_8_22_cbr_note():
    kps = _kps(8, "8-6.1")
    assert "CBR = 75/[1 + 0.728·(FC × PI)], printed with the condition FC×PI = 0" in kps
    assert "CBR = 28.09·(D60)^0.358, has the same condition" in kps
    assert "FHWA-NHI-05-037 Table 5-34, p. 5-53, prints CBR = 75/[1 + 0.728(wPI)], wPI = P200·PI" in kps


# Chapter 3, PDF p. 180: the heading prints "(ASTM D2116)"; the text and Table 3-4 (PDF p. 172) print D2166.
def test_uct_heading_note():
    s = _sec(3, "3-2.4.2.1")
    assert s["title"] == "Unconfined Compression Test (ASTM D2166)"
    assert "[The section heading prints “(ASTM D2116)” (PDF p. 180, printed p. 152)" in s["body"]


# The seven printed sections the text did not hold, each with one printed sentence.
@pytest.mark.parametrize("ch, sid, title, sentence", [
    # PDF p. 41
    (1, "1-3.2.3", "Examples",
     "Below are a few examples of visual descriptions and identifications (ASTM D2488):"),
    # PDF p. 87
    (2, "2-2.2", "Published Geologic and Hydrogeologic Maps",
     "An example of documents and sources of available information is provided in Table 2-2."),
    # PDF p. 190
    (3, "3-2.5.1.2", "Resonant Column Test (ASTM D4015)",
     "is a dynamic test that provides values of shear modulus for low shear strain amplitudes."),
    (3, "3-2.5.1.3", "Cyclic Triaxial Test for Modulus and Damping (ASTM D3999)",
     "The main purpose of this test is to determine the dynamic properties for strains ranging from about 0.01% to 0.5%."),
    # PDF p. 211
    (4, "4-2.2", "Mohr Circle of Stress",
     "by rotating an angle 2α about the center of the circle, where α is the angle between the major principal plane and the plane of interest."),
    # PDF pp. 283-284
    (5, "5-5.5", "Organic Soils and Peat",
     "Primary consolidation tends to occur more rapidly in these soils due to their relatively high hydraulic conductivity."),
    # PDF p. 476
    (8, "8-4.5", "Coefficient of Consolidation",
     "A first-order approximation for the coefficient of consolidation can be obtained using Figure 8-50."),
])
def test_missing_sections_added(ch, sid, title, sentence):
    s = _sec(ch, sid)
    assert s["title"] == title
    assert sentence in s["body"]


def test_all_465_printed_sections_held():
    assert sum(len(_chapter(ch)["sections"]) for ch in range(1, 9)) == 465


# The new sections list the figure and table they cite, which no section listed before.
def test_new_sections_list_their_figure_and_table():
    assert _sec(2, "2-2.2")["tables"] == ["Table 2-2"]
    assert _sec(4, "4-2.2")["figures"] == ["Figure 4-3: Mohr Circle Relationships"]
    assert _sec(8, "8-4.5")["figures"] == ["Figure 8-50"]


# Chapter 1, PDF p. 41 prints "Poorly-Graded Gravel with Sand (GW)"; Section 1-3.3.2 (PDF p. 44) uses GP for it.
def test_example_1_symbol_as_printed_with_note():
    body = _sec(1, "1-3.2.3")["body"]
    assert "1) Poorly-Graded Gravel with Sand (GW): About 80%" in body
    assert "classifies poorly-graded gravel as GP and well-graded gravel as GW" in body


# Bodies the text had cut off, completed from the print.
@pytest.mark.parametrize("ch, sid, sentence", [
    # PDF p. 41
    (1, "1-3.2.2.2", "“with cobbles,” “with boulders,” or “with cobbles and boulders” should be added to the group name."),
    # PDF p. 92
    (2, "2-4.2", "Spot checks of “interpreted” versus “actual” conditions are strongly recommended for each site using boring methods."),
    # PDF pp. 170-171
    (3, "3-2.3.2", "Using a Vibratory Table) is used to determine emin and γd-max."),
    # PDF p. 329
    (6, "6-3.4", "Table 6-6 and Table 6-7 present typical values for anisotropy in natural soil deposits and compacted fill."),
])
def test_cut_off_bodies_completed(ch, sid, sentence):
    assert sentence in _sec(ch, sid)["body"]


def test_no_body_cut_off():
    for ch in range(1, 9):
        for s in _chapter(ch)["sections"]:
            body = s["body"]
            assert "[section continues]" not in body and "continues beyond" not in body, s["section_id"]
            assert not body.rstrip().endswith("..."), s["section_id"]


# Chapter 6, PDF p. 330: Tables 6-6 and 6-7 are listed under 6-3.4, which cites them.
def test_anisotropy_tables_listed():
    tables = _sec(6, "6-3.4")["tables"]
    assert [t.split(" — ")[0] for t in tables] == ["Table 6-6", "Table 6-7"]
    assert "hydraulic fill 64 to 225 (Table 6-7)" in _kps(6, "6-3.4")


# Table sweep: key points that said more than the print.
def test_table_sweep_key_points():
    # PDF p. 452-453: m is about 0.8 from direct simple shear tests (Ladd et al. 1977); the print never says SHANSEP.
    s = _sec(8, "8-3.2")
    assert "for most clays" not in _kps(8, "8-3.2")
    assert "SHANSEP" not in s["summary"] + _kps(8, "8-3.2")
    assert "m is approximately 0.8 based on direct simple shear tests" in _kps(8, "8-3.2")
    # PDF p. 475, Table 8-17.
    assert "organic clays and silts: 0.035–0.075" in _kps(8, "8-4.4")
    # PDF p. 495, Table 8-28's notes attribute n to no source.
    assert "per Robertson (2009)" not in _kps(8, "8-8.2")
    # PDF p. 352.
    assert "provided the soil is non-dispersive" in _kps(6, "6-5.3.2")
    # PDF p. 327.
    assert "some of which also account for the effect of void ratio on k" in _kps(6, "6-3.3")
