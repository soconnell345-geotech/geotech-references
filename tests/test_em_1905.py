"""EM 1110-1-1905, Geotechnical Design of Shallow Foundations on Soils
(USACE, 31 July 2025).

The chapter text is read off the printed pages by
``scripts/build_printed_text.py`` (layout "army") and the figure catalog by
``scripts/build_figure_catalog.py``. These check that the text is there and
findable at every level the app uses (search, section, figure), that the
paragraph numbers address every level, that each figure is on the page that
prints its caption, and that the equations are the ones typed in from the
page.
"""

import json
import re
import unicodedata
from pathlib import Path

import pytest

from geotech_references import _figures_db, _retrieval, _retrieval_db

REF = "em_1905"
ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "geotech_references" / REF
PDF = ROOT / "docs" / "EM_1110-1-1905_2025.pdf"


def _chapters():
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((PKG / "text").glob("chapter*.json"))]


def _catalog():
    return json.loads((PKG / "figures_catalog.json").read_text(encoding="utf-8"))


def _pdf():
    fitz = pytest.importorskip("fitz")
    if not PDF.exists():
        pytest.skip("PDF not checked out")
    return fitz.open(str(PDF))


def test_twelve_chapters_and_appendices_b_to_d():
    chapters = _chapters()
    assert [c["chapter"] for c in chapters] == list(range(1, 16))
    for c in chapters:
        assert c["reference_id"] == "EM 1110-1-1905"
        assert c["volume"] is None
    titles = {c["chapter"]: c["chapter_title"] for c in chapters}
    assert titles[5] == "Ultimate Limit State for Static Analysis"
    assert titles[7] == "Settlement"
    assert titles[13].startswith("Appendix B: Design Examples")
    assert titles[14] == "Appendix C: Design Examples: Settlement for Static Analysis"
    assert titles[15] == "Appendix D: Common Unit Conversion Factors"
    assert sum(len(c["sections"]) for c in chapters) == 778


def test_every_section_carries_its_printed_pages():
    for c in _chapters():
        for s in c["sections"]:
            # a heading followed straight by its first subparagraph has no text
            assert s["body"] == "" or s["body"].startswith("[p. "), s["section_id"]
            # a split part says which pages it continues over
            assert "printed p" in s["applicability"] or (
                s["applicability"].startswith("Part ")
                and "letter is not printed" in s["applicability"]), s["section_id"]


def test_section_bodies_fit_the_reference_tools():
    # the app sends at most 16,000 characters of a tool's result, and
    # wraps a section in about 300 more
    for c in _chapters():
        for s in c["sections"]:
            assert len(json.dumps(s)) <= 14000, s["section_id"]
    # the three printed paragraphs too long for that are split into
    # lettered parts, the letters not printed; a split leaves room for the
    # notes the manifest adds (C-2b's three)
    for sid in ("7-11c(2)", "C-2b", "C-7b"):
        part = _retrieval.retrieve_section(REF, sid + ".a")
        assert part["parent_id"] == sid
        assert "(continued, p" in part["title"]
    with pytest.raises(KeyError):
        _retrieval.retrieve_section(REF, "C-2b.b")


def test_text_spanning_a_table_is_stored_once():
    # a total under a table on the page it runs on to (Table C-6b, p. 374)
    # and a sub-heading between two inner tables (Table C-2, p. 349) stand
    # once, not on every row of the table beside them
    c6 = _retrieval.retrieve_section(REF, "C-6b")["body"]
    assert c6.count("∑ δc = 0.081 inches") == 1
    assert "| 30.5 | 0.7 | 32 | 0.030 | 0.07 | 0.018\n" in c6
    c2 = "\n".join(_retrieval.retrieve_section(REF, sid)["body"] for sid in ("C-2b", "C-2b.a"))
    assert c2.count("3. The total induced vertical stress (Δσz) below point E") == 1
    # no sentence or total stands in three or more consecutive rows anywhere
    for c in _chapters():
        for s in c["sections"]:
            run = {}
            for line in s["body"].split("\n"):
                cells = {(j, x.strip()) for j, x in enumerate(line.split(" | "))
                         if " | " in line and len(x.strip()) >= 15
                         and (x.strip().endswith(".") or "=" in x)}
                run = {k: run.get(k, 0) + 1 for k in cells}
                assert not any(v >= 3 for v in run.values()), (s["section_id"], line)


def test_paragraph_numbers_address_every_level():
    sec = _retrieval.retrieve_section(REF, "2-7a(2)")
    assert sec["title"] == "Differential settlement"
    assert sec["parent_id"] == "2-7a"
    assert sec["under"] == ("2-7 Serviceability limit state requirements > "
                            "2-7a Allowable movements")
    kids = [k["section_id"] for k in sec["children"]]
    assert kids[:4] == ["2-7a(2)(a)", "2-7a(2)(b)", "2-7a(2)(c)", "2-7a(2)(d)"]
    assert _retrieval.retrieve_section(REF, "2-7a(2)(c)1")["parent_id"] == "2-7a(2)(c)"
    # an appendix's opening text lists its examples
    sec = _retrieval.retrieve_section(REF, "B")
    assert sec["children"][0]["section_id"] == "B-1"
    # a number not printed names the nearest paragraph above it
    with pytest.raises(KeyError, match="5-5a Shear zone for bearing capacity"):
        _retrieval_db.reference_get(REF, "5-5a(9)")


def test_section_lookup_through_the_database():
    row = _retrieval_db.reference_get(REF, "5-5b")
    assert row["title"] == "Bearing capacity equation"
    assert row["body"].startswith("[p. 104] Bearing capacity equation.")
    assert "[Eq. 5-21]" in row["body"]


def test_search_finds_the_bearing_capacity_paragraphs():
    hits = _retrieval_db.reference_search("bearing capacity", reference=REF)
    top = [h["section_id"] for h in hits[:5]]
    assert "5-5b" in top and "5-5" in top
    hits = _retrieval_db.reference_search("Menard pressuremeter settlement",
                                          reference=REF)
    assert "7-11c" in [h["section_id"] for h in hits[:5]]


def test_every_listed_equation_is_marked_in_its_section():
    for c in _chapters():
        for s in c["sections"]:
            for e in s["equations"]:
                assert f"[{e['id']}]" in s["body"], (s["section_id"], e["id"])


def test_table_cells_read_row_by_row():
    body = _retrieval.retrieve_section(REF, "2-6b(1)")["body"]
    rows = body[body.index("Table 2-1 Minimum factors of safety for ultimate limit state"):]
    assert "ULS Failure Mode | Minimum Factor of Safety, FS\nBearing capacity | 3.0[1]\n" \
        "Sliding | 2.0[2]\nOverturning moment and eccentricity | Note 3\nUplift | 1.5" in rows
    # a worked example's summary table, row by row (p. 297)
    body = _retrieval.retrieve_section(REF, "B-1c")["body"]
    rows = body[body.index("Table B-1b Summary of calculations for Example B-1"):]
    assert "Row | Symbol | USACE | FHWA\n1 | B (ft) | 7 | 7" in rows
    assert "14 | qult (ksf) | 3.51 | 3.32" in rows
    assert "18 | FS | 3.1 | 3" in rows


def test_table_typed_in_from_the_page():
    # Table 4-10 (p. 89) is printed as two tables side by side; the manifest
    # (printed_tables) gives its rows
    body = _retrieval.retrieve_section(REF, "4-10d(1)(f)")["body"]
    rows = body[body.index("[Table 4-10 is printed as two tables"):]
    assert "Clay | Soft | Medium | Stiff | Very Stiff | Hard\n" \
        "P*L (tsf) | 0 to 2 | 2 to 4 | 4 to 8 | 8 to 16 | > 16" in rows
    assert "Sand | Loose | Compact | Dense | Very Dense" in rows
    # the caption's subscript is the zero of E0 (the text layer holds a
    # capital O; manifest printed_tables 'title')
    assert "Table 4-10 Common values of net limit pressure (P*L) and pressuremeter " \
        "modulus (E*0) (Briaud 1992)" in body
    assert "E*O" not in body


def test_table_3_8_note_reads_sigma_v_prime():
    # Table 3-8 (p. 46) sets a raised semicolon where the prime of σ′v stands
    body = _retrieval.retrieve_section(REF, "3-7a")["body"]
    assert body.count("For σ′v = 2,000 to 8,000 pcf") == 3
    assert "^(;)" not in body


def test_print_quirk_kept_as_printed():
    # Table 5-3's AASHTO cell for the inclination factor on N-gamma prints iq
    body = _retrieval.retrieve_section(REF, "5-5f")["body"]
    assert "iγ | iγ = [1 − β/φ′]^2 | iq = [1 − tanβ]^(n+1)" in body


def test_worked_example_slips_kept_with_a_note():
    # Examples C-7c and C-7d keep their printed numbers (pp. 382, 385-386);
    # a note after each (manifest print_notes) gives what the rows give
    c7 = c7a = _retrieval.retrieve_section(REF, "C-7b.a")["body"]
    assert "δ = 0.015 ft + 0.013 ft = 0.028 ft = 0.38 in\n[Note (not printed): " \
        "Table C-7c, Step 12 (p. 382)" in c7
    assert "| 0.114 | 0.008\n" in c7a and "= 0.0266" in c7a
    assert "= 0.125 ft = 1.5 in\n[Note (not printed): Table C-7d" in c7a
    assert "the sum is 0.0194, not 0.0266" in c7a and "0.092 ft (1.1 in)" in c7a
    # Step 10's ratios and Step 12's exponent (p. 382)
    assert "Table 7-6, αc = 0.33\n[Note (not printed): Table C-7c, Step 10" in c7
    assert "17.9 and 78 tsf/8.5 tsf = 9.2, not 9.5 and 4.9" in c7
    assert "4.4^(1/3) = 0.0151 ft" in c7
    # the other worked examples' slips, each kept with a note after it
    after = {
        "B-4c": ("| u (ksf) | 0499 | 0.499\n[Note (not printed): ",
                 "0499 is 0.499 ksf"),
        "B-6c": ("limit state requirements.\n[Note (not printed): ",
                 "18.82 ksf (USACE) and 16.62 ksf (FHWA), the sand layer"),
        "C-2b": ("| 12.5 | 0.06 | 0.023 | 0.18\n[Note (not printed): ",
                 "0.06 + 0.023 = 0.08 tsf, printed 0.18"),
        "C-3b": ("0.54 tcf = 0.54 tsf for depths < 25 ft per Step 2.\n[Note "
                 "(not printed): ", "is 0.54 tsf (tcf is the unit of γm)"),
        "C-4b": ("| 3 | 13.0 | 8 | 0.12 | 0.11\n[Note (not printed): ",
                 "1.43 is the same pressure in ksf"),
        "C-6b": ("| 30.5 | 0.7 | 32 | 0.030 | 0.07 | 0.018\n[Note (not "
                 "printed): ", "total 0.812 in, not 0.081 in"),
    }
    for sid, (place, words) in after.items():
        body = _retrieval.retrieve_section(REF, sid)["body"]
        assert place in body and words in body, sid
    c4 = _retrieval.retrieve_section(REF, "C-4b")["body"]
    assert "= 1.01 tsf\n[Note (not printed): Table C-4, Steps 3 and 6" in c4
    c2 = _retrieval.retrieve_section(REF, "C-2b")["body"]
    assert "|  | 0.72 | 0.045 | 0.04\n[Note (not printed): " in c2
    c3 = _retrieval.retrieve_section(REF, "C-3b")["body"]
    assert "to a depth of 25.0 ft per Step 2.\n[Note (not printed): Table C-3b" in c3
    # slips found when every appendix formula line was read against the page
    noted = {
        "B-1b": "= 7 ft = 49 ft^2 (Row 3)\n[Note (not printed): Table B-1a, Step 1 (p. 296)",
        "B-4b": "= 0.226 ksf (Row 6)\n[Note (not printed): Table B-4a, Step 3 (p. 312)",
        "B-5b": "= 9.9/3 = 3.3 ≥ 3 OK ü\n[Note (not printed): Table B-5a, Step 9 (p. 321)",
        "B-6b": "tan(1.4 · 31°)\n[Note (not printed): Table B-6a, Step 4 (p. 325)",
        "C-2b": "= 0.45 tsf\n[Note (not printed): Table C-2, Step 5 (p. 345)",
        "C-6b": "| 264 | 23.9 | 199\n[Note (not printed): Table C-6a (p. 370)",
        "3-9b(1)(b)": "2 | PI > 50 | 115 to 75\n[Note (not printed): Table 3-15 (p. 59)",
        "8-6b(3)": "My = distance ratio as shown on Figure 8-7 (dimensionless)\n"
                   "[Note (not printed): Eqs. 8-27 and 8-28 (p. 206)",
    }
    for sid, place in noted.items():
        assert place in _retrieval.retrieve_section(REF, sid)["body"], sid


def test_appendix_formula_lines_as_printed():
    # worked-example lines the placement rules read wrongly, typed in from the
    # rendered page (manifest printed_passages); each result follows from the
    # line as stored
    c3 = _retrieval.retrieve_section(REF, "C-3b")["body"]
    # Step 4 (p. 359): the drainage path squared; without the power the line
    # gives 12.2 days, not the printed 152.8
    assert "\nt = (Tv · Hdr^2)/Cv = (0.403 ((25 ft)/2)^2)/(0.412 ft^2/day) = 152.8 days" in c3
    assert round(0.403 * (25 / 2) ** 2 / 0.412, 1) == 152.8
    c7a = _retrieval.retrieve_section(REF, "C-7b.a")["body"]
    # Step 6 (p. 384): σ′zp = 6.5′ × 125 pcf/2,000 under the root
    assert "Izp = 0.5 + 0.1√((3.31 tsf − 0.156 tsf)/(6.5′ × 125 pcf/2,000)) = 0.779" in c7a
    assert round(0.5 + 0.1 * ((3.31 - 0.156) / (6.5 * 125 / 2000)) ** 0.5, 3) == 0.779
    # Step 7 (p. 384): Eq. 7-24 as quoted there
    assert "Eq. 7-24: C1 = 1 − 0.5 (σ′zD/(q − σ′zD)) ≥ 0.5" in c7a
    assert round(1 - 0.5 * 0.156 / (3.31 - 0.156), 3) == 0.975
    assert "Step 10 | ∑ (Iz · H)/Es = 0.0266" in c7a
    # Eq. 7-10 as quoted in Examples C-6 and C-7 (pp. 373, 380)
    for sid in ("C-6b", "C-7b"):
        assert "Eq. 7-10: δ = ∑(Iσ(q − σ′zD))/M · H = ∑(Δσz)/M · H" in \
            _retrieval.retrieve_section(REF, sid)["body"], sid
    # Example B-2, Step 3 (p. 301)
    b2 = _retrieval.retrieve_section(REF, "B-2b")["body"]
    assert "\nqeq = (Q + Wf)/A′ = (1.2 kips/ft + 0.6 kips/ft)/(2 ft^2/ft) = 0.9 ksf " \
        "(Row 17)" in b2
    # the page prints bpf where the text layer holds pf (pp. 335, 386)
    b7 = _retrieval.retrieve_section(REF, "B-7b")["body"]
    assert "= 13.2 bpf\n" in b7 and "13.2 bpf · 2 ksf = 26.4 ksf" in b7
    assert "N̅60 = (12 + 15 + 14)/3 = 14 bpf" in c7a
    # "14.7 k–ips" (p. 314) is the word kips
    assert "(80 kips + 14.7 kips)/(49 ft^2)" in _retrieval.retrieve_section(REF, "B-4b")["body"]


#: a formula line the scatter check passes because the page prints it so
AS_PRINTED = {
    # Table C-4, Step 9 (p. 363): no bracket opens before 6.0 ft · 113 pcf
    "σ′zD = ((8.0 ft · 100 pcf) + 6.0 ft · 113 pcf) − (8.0 ft · 62.4 pcf))/2,000 = 0.49 tsf",
    # paragraph 7-19b (p. 190): no bracket opens before 10^(−4)
    "d0 = initial dial reading 10^(−4) inches)",
}
_PRIME_ALONE = re.compile(r"\(\s*[′']\s*\)|\(\s*′\s|(?<![\w)\]′])′(?=[\s)])")
_LONE_NUMBER = re.compile(r"^\d{1,3}(?:\.\d+)?$")
_DOUBLED = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?) \1 (?:ft|in|kips|ksf|tsf|psf|pcf|kcf|m)\b")
_SPACED = re.compile(r"\([A-ZΔσα∝] [a-z0-9]{1,4}(?: [a-z0-9]{1,4})?\)")


def _scattered(lines: list[str], k: int) -> list[str]:
    """What marks line k as pieces of a formula put back in the wrong
    places: a prime standing alone, a lone number on the line above a
    formula (a stacked power), a number doubled from a stacked fraction
    ('2 2 ft'), a subscript spaced off its symbol ('(E 1)'), brackets that
    do not pair in a cell holding '='."""
    ln = lines[k]
    marks = []
    if _PRIME_ALONE.search(ln):
        marks.append("prime alone")
    if _LONE_NUMBER.match(ln.strip()) and k + 1 < len(lines) and "=" in lines[k + 1]:
        marks.append("lone number above a formula")
    if _DOUBLED.search(ln):
        marks.append("number doubled")
    if _SPACED.search(ln):
        marks.append("subscript spaced off")
    if "=" in ln and any(c.count(a) != c.count(b) for c in ln.split(" | ")
                         for a, b in ("()", "[]")):
        marks.append("unbalanced brackets")
    return marks


def test_no_formula_pieces_scattered():
    # the lines as they were read before they were typed in from the page
    # are each caught
    for bad in (["Izp = 0.5 + 0.1√((3.31 tsf − 0.156 tsf)/(′) = 0.779)"],
                ["2", "t = (Tv · Hdr^2)/Cv = (0.403 ((25 ft)/2))/(0.412 ft^2/day) = 152.8 days"],
                ["qeq = (Q+W f)/(′ A) = (1.2 kips/ft+0.6 kips/ft)/(2 2 ft /ft) = 0.9 ksf"],
                ["Eq. 7-13: Ek = n/(1/(E 1)+ 1/(E 2)+⋯+ 1/(E n))"],
                ["Eq. 7-24: C1 = 1 − 0.5 ((′ σ zD)/(′ q − σ z D)) ≥ 0.5"]):
        assert _scattered(bad, 0), bad
    found = []
    for c in _chapters():
        for s in c["sections"]:
            lines = s["body"].split("\n")
            for k, ln in enumerate(lines):
                if ln.startswith("[Note (not printed)") or ln in AS_PRINTED:
                    continue
                if _scattered(lines, k):
                    found.append((s["section_id"], _scattered(lines, k), ln[:120]))
    assert found == []


# --- figures ----------------------------------------------------------------

#: figure -> (printed page, 0-based PDF page, chapter file). Lettered appendix
#: figures (C-2a) and figures captioned inside a table cell (8-4, C-2c, C-4b)
#: included; Figure 7-10 prints a caption with no picture.
FIGURES = {
    "2-1": (6, 20, 2), "4-7": (85, 99, 4), "6-7": (135, 149, 6),
    "7-6": (159, 173, 7), "7-10": (166, 180, 7), "8-4": (201, 215, 8),
    "8-11": (211, 225, 8), "9-6": (230, 244, 9), "B-1": (295, 309, 13),
    "C-1": (339, 353, 14), "C-2a": (343, 357, 14), "C-2c": (346, 360, 14),
    "C-4b": (361, 375, 14),
}


def test_catalog_covers_every_figure():
    cat = _catalog()
    assert cat["figure_count"] == len(cat["figures"]) == 136
    assert not any(f["page_estimated"] for f in cat["figures"])
    assert all(f["description"] for f in cat["figures"])
    assert cat["pdf_path"] == "docs/EM_1110-1-1905_2025.pdf"
    nums = [f["figure_number"] for f in cat["figures"]]
    assert nums[0] == "2-1" and nums[-1] == "C-7b"
    # every figure the chapter text lists is in the catalog
    listed = {x.split(":")[0].removeprefix("Figure ")
              for c in _chapters() for s in c["sections"] for x in s["figures"]}
    assert listed == set(nums)


def test_catalog_captions_keep_a_broken_word_whole():
    # a Figure List entry broken over two lines after a word's own hyphen
    caps = {f["figure_number"]: f["caption"] for f in _catalog()["figures"]}
    assert "blow counts on a per-inch basis" in caps["4-3"]
    assert caps["C-6c"].endswith("from Laboratory 1-D Oedometer Test")
    assert not [n for n, c in caps.items() if re.search(r"\w- \w", c)]


def test_figure_lookup():
    for num, (page, idx, chapter) in FIGURES.items():
        fig = _figures_db.figure_get(REF, num)
        assert (fig["printed_page"], fig["pdf_page_index"], fig["chapter"]) == \
            (page, idx, chapter), num
        pdf, i = _figures_db.resolve_pdf(REF, num)
        assert pdf.name == PDF.name and i == idx, num
    # printed page = PDF page - 15 throughout
    for f in _catalog()["figures"]:
        assert f["pdf_page_index"] == f["printed_page"] + 14, f["figure_number"]


def test_figure_search_finds_the_influence_charts():
    hits = _figures_db.figure_search("influence factor vertical stress", reference=REF)
    assert {"6-7", "6-8", "6-10"} <= {h["figure_number"] for h in hits[:5]}


def _squash(text):
    # a caption on its page sets symbols in mathematical bold italic letters
    # and numbers with en dashes, and may print a dash the Figure List prints
    # as a hyphen (Figure 7-19, "void ratio—logarithm time"); letters and
    # digits are compared
    text = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in text.lower() if ch.isalnum())


def test_catalog_pages_are_the_caption_pages():
    with _pdf() as doc:
        for f in _catalog()["figures"]:
            page = _squash(doc[f["pdf_page_index"]].get_text())
            want = _squash(f"Figure {f['figure_number']}. {f['caption']}")[:40]
            assert want in page, f["figure_number"]


def test_cover_designation():
    with _pdf() as doc:
        cover = doc[0].get_text()
    assert "EM 1110-1-1905 ● 31 July 2025" in cover
    assert "Geotechnical Design of Shallow Foundations on Soils" in cover
    for c in _chapters():
        assert c["reference_id"] == "EM 1110-1-1905"


# --- the equations as printed ---------------------------------------------


def _equations():
    out = {}
    for c in _chapters():
        for s in c["sections"]:
            for e in s["equations"]:
                out.setdefault(e["id"][4:], (s["section_id"], e))
    return out


def test_every_equation_has_its_printed_formula():
    eqs = _equations()
    assert len(eqs) == 213
    per_chapter = {}
    for num, (sid, e) in eqs.items():
        per_chapter[int(num.split("-")[0])] = per_chapter.get(int(num.split("-")[0]), 0) + 1
        assert e.get("formula"), num
        assert e["source"].startswith("Typed in from p. "), num
        assert "variables" in e, num
    assert per_chapter == {2: 8, 3: 51, 4: 21, 5: 36, 6: 13, 7: 48, 8: 31, 9: 5}


def test_formulas_as_printed():
    # spot checks against the rendered pages
    eqs = _equations()
    assert eqs["5-21"][1]["formula"] == \
        "qult = c · Nc + q0 · Nq + (1/2) B · γ′ · Nγ   (Continuous Footing)"
    assert "ksf" in eqs["5-21"][1]["variables"]["qult"]
    assert eqs["3-21"][1]["formula"] == "Hydraulic Conductivity, k = Cv · mv · γw"
    assert eqs["8-19"][1]["formula"] == "D = (EC · t^3)/(12(1 − μC^2))"
    assert eqs["6-9"][1]["formula"] == \
        "Iσ = 1 − (1/(1 + (B/(2z))^2))^1.76   (Square Loaded Area)"
    # a formula that differs from its neighbours is typed as printed and said
    assert eqs["7-15"][1]["formula"] == "EL = n/(1/E1 + 1/E2 + ⋯1/En)"
    assert eqs["7-15"][1]["notes"].startswith("As printed")
    assert "As printed" in eqs["5-17"][1]["notes"]
    assert "As printed" in eqs["9-5"][1]["notes"]
    assert "As printed" in eqs["8-28"][1]["notes"]


def test_equation_symbols_as_listed():
    # symbols the formula prints, from the list printed under it (pp. 42, 151,
    # 158, 167, 197), with the list's spelling said where it differs
    eqs = _equations()
    want = {"3-17": {"φ′"}, "7-3b": {"CR"}, "7-4": {"CR", "CC"},
            "7-6": {"eG′", "σ′zG′", "σ′zF"}, "7-11": {"αd"}, "7-12": {"αd", "αL"},
            "8-2": {"E", "I"}}
    for num, symbols in want.items():
        assert symbols <= set(eqs[num][1]["variables"]), num
    assert "prints Cr" in eqs["7-3b"][1]["variables"]["CR"]


def test_equation_description_is_not_another_formula():
    # Eq. 5-3 is printed after Eq. 5-2 (p. 94); its description says so and
    # does not quote Eq. 5-2's formula as the words introducing it
    eqs = _equations()
    assert eqs["5-3"][1]["description"] == "Equation 5-3, printed after Eq. 5-2 (p. 94)."
    formulas = {num: e["formula"] for num, (_, e) in eqs.items()}
    for num, (_, e) in eqs.items():
        quoted = [m for m, f in formulas.items()
                  if m != num and len(f) > 30 and f[:30] in e["description"]]
        assert quoted == [], num


def test_manifest_formulas_match_the_text():
    manifest = json.loads((ROOT / "scripts" / "manifests" / f"{REF}.json")
                          .read_text(encoding="utf-8"))
    eqs = _equations()
    n = 0
    for vol in manifest["volumes"]:
        for p in vol.get("printed_equations", []):
            assert eqs[p["number"]][1]["formula"] == p["formula"], p["number"]
            n += 1
    assert n == 213


def test_rebuild_reproduces_the_committed_text():
    # the formulas, passages and Table 4-10 live in the manifest, so a
    # rebuild keeps them
    pytest.importorskip("fitz")
    if not PDF.exists():
        pytest.skip("PDF not checked out")
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import build_printed_text as builder
    finally:
        sys.path.remove(str(ROOT / "scripts"))
    chapters, _ = builder.build_chapters(REF)
    assert sorted(chapters) == list(range(1, 16))
    for n, data in chapters.items():
        assert data.pop("_missing") == [], f"chapter {n}"
        committed = (PKG / "text" / f"chapter{n:02d}.json").read_text(encoding="utf-8")
        assert builder.chapter_json(data) == committed, f"chapter {n}"
