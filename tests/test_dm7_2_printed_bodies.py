"""UFC 3-220-20 (DM 7.2, 16 January 2025): section bodies in the print's own
words (app BACKLOG REF-94).

The bodies were condensed accounts written by hand; ``scripts/build_dm72_bodies.py``
rebuilds each one from the printed pages (heading to next heading) with
``[p. 508]`` markers (printed page = PDF page - 38), each numbered equation
as ``[Eq. 7-5]`` and the formula its checked ``equations`` entry states, every
unnumbered formula line typed in from the rendered page, footnotes and table
notes at their marks, figure and table captions where printed, and a table
whose cells no body held marked "not typed in". Every other field of a
section (title, summary, key points, applicability, equations, figures,
tables) is kept as it was checked: a digest of those fields is pinned here.
"""

import hashlib
import json
import re
from pathlib import Path

import pytest

from geotech_references import _retrieval, _retrieval_db

REF = "dm7_2"
ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "geotech_references" / REF / "text"
PDF = ROOT / "docs" / "ufc_3_220_20_2025.pdf"
#: Chapters whose bodies are rebuilt from the print so far, with their PDF pages.
BUILT = {
    "prologue": (39, 92),
    "chapter02": (93, 144),
    "chapter03": (145, 212),
    "chapter07": (546, 595),
}
#: sha256 of every section's fields other than ``body`` (json, sorted keys),
#: as merged at b38ffcd: the build keeps them byte for byte.
KEPT_DIGEST = {
    "prologue": "c8d4a9a0d2de418767d587366031f1a29eca295b83c5e3370eab51d34b37efa9",
    "chapter02": "3a8784c9e8b0a3054d039820cd42e80e2e8b301b832e1fe19b43ba53da5e72f6",
    "chapter03": "9d60231d48e64fb8131a5becedf843a2febde9043f5b022fd0fcec1057f77dc1",
    "chapter04": "0f9eb3dfe8078ed95352892242b7f20ee9e7bb47400014e203271386d0c4123d",
    "chapter05": "d6ee0d9787a133fcde12b1857ae19094a4d378cd2dfacc0ab2b4d909bfd411d5",
    "chapter06": "41844efe5750c0da0b6d802076797e42a22f55a771b1f33db1929950a57beb55",
    "chapter07": "7b8774175d719f20f10d649b8cfcf3cca07c28048f7286d6c52bcad7d4b56b75",
}
_PART = re.compile(r"\.[a-z]$")


def _chapter(stem):
    return json.loads((TEXT / f"{stem}.json").read_text(encoding="utf-8"))


def _sections(stem):
    return {s["section_id"]: s for s in _chapter(stem)["sections"]}


def _body_with_parts(secs, sid):
    """A section's body and those of its lettered parts, in order."""
    return "\n\n".join(s["body"] for k, s in secs.items()
                       if k == sid or (_PART.search(k) and k[:-2] == sid))


# --- what is kept -----------------------------------------------------------

@pytest.mark.parametrize("stem", sorted(KEPT_DIGEST))
def test_checked_fields_kept_byte_for_byte(stem):
    rows = [{k: v for k, v in s.items() if k != "body"}
            for s in _chapter(stem)["sections"] if not _PART.search(s["section_id"])]
    digest = hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True)
                            .encode("utf-8")).hexdigest()
    assert digest == KEPT_DIGEST[stem]


# --- the bodies -------------------------------------------------------------

@pytest.mark.parametrize("stem", sorted(BUILT))
def test_every_body_carries_its_printed_pages(stem):
    lo, hi = BUILT[stem]
    for sid, s in _sections(stem).items():
        body = s["body"]
        assert body == "" or body.startswith("[p. "), sid
        for m in re.finditer(r"\[p\. (\d+)\]", body):
            assert lo - 38 <= int(m.group(1)) <= hi - 38, (sid, m.group(0))


@pytest.mark.parametrize("stem", sorted(BUILT))
def test_sections_fit_the_reference_tools(stem):
    for sid, s in _sections(stem).items():
        assert len(s["body"]) <= 12000, sid
        assert len(json.dumps(s)) <= 14000, sid


@pytest.mark.parametrize("stem", sorted(BUILT))
def test_parts_say_what_they_continue(stem):
    secs = _sections(stem)
    for sid, s in secs.items():
        if _PART.search(sid):
            assert sid[:-2] in secs, sid
            assert s["title"].startswith(secs[sid[:-2]]["title"] + " (continued, p"), sid
            assert "the letter is not printed" in s["applicability"], sid


@pytest.mark.parametrize("stem", sorted(BUILT))
def test_numbered_equations_marked_with_their_checked_formula(stem):
    secs = _sections(stem)
    for sid, s in secs.items():
        if _PART.search(sid):
            continue
        body = _body_with_parts(secs, sid)
        for e in s["equations"]:
            if not e["id"].startswith("Eq. "):
                continue
            m = re.search(re.escape(f"[{e['id']}] ") + r"([^\n]*)", body)
            if m is None:
                # printed in another section and cited here (Eqs. 3-3 to 3-5 in 3-5.1)
                assert any(f"[{e['id']}] " in x["body"] for k, x in secs.items() if k != sid), \
                    (sid, e["id"])
                continue
            formula = m.group(1)
            if formula not in e["description"]:
                # the formula, then a note in brackets ("[left side printed εb]")
                formula = re.sub(r" \[[a-z][^\]]*\]$", "", formula)
            assert formula in e["description"], (sid, e["id"], m.group(1))


@pytest.mark.parametrize("stem", sorted(BUILT))
def test_tables_not_typed_in_say_so(stem):
    for sid, s in _sections(stem).items():
        for m in re.finditer(r"\[(Table [P1-7]-\d+): values on printed (pp?\. [\d ,to-]+); not typed in\]",
                             s["body"]):
            # the placeholder follows the table's caption
            before = s["body"][:m.start()]
            assert re.search(re.escape(m.group(1)) + r" \S[^\n]*\n\n$", before), (sid, m.group(1))


# (stem, section, printed page, a printed sentence): the sentence is in the
# section's body and the last page marker before it names its page
PRINTED = [
    ("chapter03", "3-2.2.1", 110,
     "The compactive effort for standard Proctor is 12,400 lbf-ft/ft³."),
    ("chapter03", "3-3.1", 119,
     "For mass earthwork, initial exploration should be on a 200-foot grid."),
    ("chapter03", "3-3.2", 123,
     "For normal embankment construction, the maximum particle sizes should not exceed 3 inches "
     "(i.e., gravel-sized or smaller) or 50 percent of the compacted layer thickness."),
    ("chapter03", "3-4.3.2", 135,
     "If more detailed unit weight information is not available, a shrinkage factor of 10% to 15% "
     "of VF can be used for estimating purposes."),
    ("chapter03", "3-4.3.2", 136,
     "In this case, the shrinkage factor may be as low as -10%."),
    ("chapter03", "3-5.1", 145,
     "In some cases, special equipment can be specified based on experience with local conditions "
     "and available fill materials."),
    ("prologue", "P-2.1", 2,
     "The prime symbol is often omitted even though the shear strength parameters refer to "
     "effective stress or drained parameters, and the reader should be aware of this issue."),
    ("prologue", "P-3.3", 11,
     "This is not ideal, but as long as the value of su is interpreted using a conservative "
     "method, it should suffice."),
    ("prologue", "P-3.3.3", 15,
     "Low plasticity silts typically have effective stress friction angles in the range of 35 "
     "to 40 degrees with little to no cohesion intercept (Duncan et al. 2014)."),
    ("prologue", "P-3.4", 17,
     "End-of-Construction - At least three UU triaxial compression tests should be performed "
     "for each combination of water content and compacted dry unit weight."),
    ("prologue", "1-2.8", 24,
     "Loose sands can be defined as sand-sized soils having a relative density less than 40% "
     "and an SPT blow count less than 10 blows/ft (Duncan et al. 2014)."),
    ("prologue", "1-2.12", 27,
     "Soils are deemed not expansive if the plasticity index is less than 15, less than 10% "
     "passes the No. 200 mesh sieve, or less than 5% of the soil is finer than 0.005 mm."),
    ("prologue", "1-2.18", 32,
     "Bray et al. (2009) suggested using an effective stress cohesion intercept of 300 psf and "
     "a drained friction angle of 36 degrees at a normal stress of 2000 psf with the friction "
     "angle decreasing by 5 degrees for each tenfold increase in normal stress."),
    ("chapter02", "2-3.3", 59,
     "Protective measures are also required for some excavations at any point less than "
     "5 feet deep where there is evidence of a potential cave-in as determined by a "
     "competent person."),
    ("chapter02", "2-3.3.2", 61,
     "Excavations up to 2 feet below the shield are permitted when the shield is designed "
     "to resist the forces for the full depth of the trench."),
    ("chapter02", "2-3.3.4", 64,
     "A maximum of two feet of soil surcharge adjacent to the trench and a maximum "
     "equipment surcharge of 20,000 lb are assumed in the design."),
    ("chapter02", "2-4.3.3", 73,
     "A factor of safety of at least 1.5 should be used against basal heave failure as "
     "discussed by Mana and Clough (1981)."),
    ("chapter02", "2-4.3.3", 76,
     "Stiffer concrete diaphragm walls often have normalized wall stiffness greater than 100."),
    ("chapter02", "2-4.4.2", 82,
     "When excavation support walls are flexible and the factor of safety against basal "
     "heave is less than 1.5, δVm = 2%·H is a reasonable assumption."),
    ("chapter02", "2-5.3.1", 94,
     "The scaled distance is not correct dimensionally and requires use of the indicated units."),
    ("chapter02", "2-6.2", 99,
     "Tests on vinyl sheet piling indicate ρ ranging from 10⁻⁵ cm/sec for unsealed joints "
     "in tension to about 10⁻¹⁰ cm/sec for sealed joints."),
    ("chapter07", "7-1.1", 508,
     "A primary purpose of this chapter is to familiarize the engineer with common "
     "applications of probability in geotechnical engineering."),
    ("chapter07", "7-2.3.3", 518,
     "The CDF cannot be expressed in a closed form equation and must be read from tables "
     "or determined numerically."),
    ("chapter07", "7-2.3.3", 519,
     "When RV with any type of distribution are added together, the resulting distribution "
     "will tend to be normal as the number of RV increases."),
    ("chapter07", "7-3.1.5", 525,
     "The values can be assumed to contain the combined effects of inherent, measurement, "
     "and transformation uncertainty."),
    ("chapter07", "7-4.2.2", 536,
     "The limit state function is evaluated for 2ⁿ cases with each RV either one standard "
     "deviation above or below the mean."),
    ("chapter07", "7-4.2.4", 541,
     "If the acceptable error in the estimates of the mean and standard deviation is 10%, "
     "the required number of trials is in the range of 100 to 1000."),
    ("chapter07", "7-4.4", 549,
     "For example, events with a probability of exceedance of 10% in 50 years have λ(y*) "
     "of 2.1×10⁻³ yr⁻¹, which corresponds to R of 475 years."),
    ("chapter07", "7-4.5.2", 553,
     "For this reason, resistance factors are methodology specific, and careful attention "
     "must be given to selecting the appropriate φ for the design method used."),
]


@pytest.mark.parametrize("stem,sid,page,sentence", PRINTED,
                         ids=[f"{p[1]}-p{p[2]}" for p in PRINTED])
def test_printed_sentences_with_their_pages(stem, sid, page, sentence):
    body = _body_with_parts(_sections(stem), sid)
    i = body.find(sentence)
    assert i >= 0, sid
    marks = re.findall(r"\[p\. (\d+)\]", body[:i])
    assert marks and int(marks[-1]) == page, (sid, marks[-1:])


def test_prologue_as_printed():
    secs = _sections("prologue")
    # the where-lists of Eqs. P-1 and P-2, one symbol to a line (p. 4)
    assert ("where:\na and b = power function strength parameters and\n"
            "Pa = atmospheric pressure.") in secs["P-2.2.1"]["body"]
    assert ("where:\nsu = undrained shear strength,\nau and bu = power function strength "
            "parameters.") in secs["P-2.2.1"]["body"]
    # the three-parameter function numbered (A-3) as printed (p. 4)
    assert "[Eq. A-3] s = a·Pa·(σʹ/Pa + t)^b" in secs["P-2.2.2"]["body"]
    # Tables P-2 to P-8 typed in from the page, row by row, after the caption
    assert ("[p. 9] Table P-2 Shear Strength Methods for In situ Coarse-Grained Soil\n\n"
            "Method | Guidance\nLaboratory tests on disturbed, reconstituted, or compacted test "
            "specimens | Rarely Appropriate.") in secs["P-3.1"]["body"]
    assert "• DSS: USR = sin φʹ – 0.5 sin² φʹ" in secs["P-3.3.3"]["body"]
    assert "(see Table ). [As printed on p. 10: no table number]" in secs["P-3.2"]["body"]
    # the worked example inside Figure P-4 kept after the caption (p. 6)
    assert ("Parameters from Power Function Parameters\n\nWorked example (Figure P-4):"
            in secs["P-2.2.3"]["body"])
    # the bars of φ̄ and c̄ drawn on p. 2 put back
    assert "(e.g., φ̄ and c̄)" in secs["P-2.1"]["body"]
    # numbered lists one item to a line; the two-column list of p. 37 read
    # down the left column, then the right
    assert "1) Clays at low initial degrees" in secs["1-2.12"]["body"]
    assert "\n\n2) The swell potential increases" in secs["1-2.12"]["body"]
    b = secs["1-3.1"]["body"]
    assert b.index("• Geotextile encased columns") < b.index("• Jet grouting")
    assert "• Combined soil stabilization with vertical columns" in b
    # the notation tables kept; no blank page or chapter title in P-4
    assert secs["P-4"]["body"].startswith("[p. 18] Variable | Definition\na | Power function")
    assert "[p. 19] φʹp | Peak drained" in secs["P-4"]["body"]
    assert "Intentionally" not in secs["P-4"]["body"]
    assert "GEOTECHNICAL DESIGN IN PROBLEM SOILS" not in secs["P-4"]["body"]
    assert secs["1-4"]["body"].startswith("[p. 54] Variable | Definition")


def test_chapter_3_as_printed():
    secs = _sections("chapter03")
    # Eq. 3-4 as printed, its where-list one symbol (p. 112)
    assert "[p. 112] [Eq. 3-4] Δw = wopt − wfield\n\nwhere:\nwfield = water content of the compacted fill." \
        in secs["3-2.2.1"]["body"]
    assert "[Eq. 3-5] Dr = [(emax − e)/(emax − emin)] × 100% = " in secs["3-2.2.2"]["body"]
    # Tables 3-10 and 3-11 typed in from the page, with Table 3-11's slip noted (p. 144)
    b = secs["3-5.1"]["body"]
    assert ("Soil moisture (soil with appreciable fines) | Appropriate moisture: Rollers track in 3 "
            "to 4 inches on first pass") in b
    assert ("Structural Support | 100% (D698) 95% (D1557) | -2% to +2% | Up to 12 inches | Fill "
            "should be uniform.") in b
    assert "Drainage blanket or filter | 95% (D698) 90% (D1557) | Wet | Up 8 inches |" in b
    assert '[As printed on p. 144: "See Table 2-12". Table 2-12 is Problem Soil Considerations' in b
    assert b.index("Table 3-11 Typical Compaction") < b.index("[Table 3-11 note A:")
    # a section number broken over two lines joined (p. 145)
    assert "(see Section 3-5.2)" in b
    # the notation with its last two rows (p. 173) and the slip of p. 172
    n = secs["3-9"]["body"]
    assert n.startswith("[p. 171] Variable | Definition")
    assert "[p. 173] σ | Standard deviation\nσʹz | Effective vertical stress" in n
    assert 'with confinings [As printed on p. 172: "confinings"]' in n
    assert secs["3-10"]["body"].startswith("[p. 173] Topic: General Earthwork")
    assert "Intentionally" not in secs["3-10"]["body"]


def test_chapter_2_as_printed():
    secs = _sections("chapter02")
    # the where-list of Eq. 2-1 with its subscripts in place (p. 56)
    assert ("[Eq. 2-1] Hcrit = 4su / γt\n\nwhere:\nsu = undrained shear strength and\n"
            "γt = total or moist unit weight of the clay.") in secs["2-2.2.1"]["body"]
    # Eq. 2-6 in both its pieces (p. 85)
    assert ("[Eq. 2-6] δi = δm for 0 ≤ di ≤ 0.75H; δi = δm · ((1.5H − di) / 0.75H) "
            "for 0.75H ≤ di ≤ 1.5H") in secs["2-4.4.3"]["body"]
    # the second-level list of 2-1 as printed, one item to a line
    assert "include:\n\no Open cut excavations,\n\no Trenching," in secs["2-1"]["body"]
    # the print's slips noted where they are (pp. 84)
    assert "[Eq. 2-4] εh = (δHi − δHj) / db [left side printed εb]" in secs["2-4.4.3"]["body"]
    assert "estimated settlements [As printed on p. 84" in secs["2-4.4.3"]["body"]
    # 2-3.3.5 Steel Shoring has no section here: its text stays in 2-3.3.4
    assert "[p. 66] 2-3.3.5 Steel Shoring.\n\nSteel sheeting and bracing" in secs["2-3.3.4"]["body"]
    # the notation table whole (pp. 104-106) and the reading list in 2-9
    assert secs["2-8"]["body"].startswith("[p. 104] Variable | Definition\nB | Excavation")
    assert "[p. 106] ∆p | Differential water pressure" in secs["2-8"]["body"]
    assert secs["2-9"]["body"].startswith("[p. 106] Excavation Safety and Shoring:\n")
    assert "Variable definitions" not in secs["2-9"]["body"]


def test_chapter_7_as_printed():
    secs = _sections("chapter07")
    # the where-list of Eq. 7-5, one symbol to a line (p. 524)
    assert ("where:\nθ = generic geotechnical parameter\nCOVw = coefficient of variation "
            "of inherent variability,") in secs["7-3.1.5"]["body"]
    # Table 7-4's notes after its caption and the "not typed in" line (p. 526)
    assert ("[Table 7-4: values on printed p. 526; not typed in]\n\n"
            "[Table 7-4 note A: Mean COV minus one standard deviation") in secs["7-3.1.5"]["body"]
    # the notation table kept as typed, with the row p. 557 adds
    assert secs["7-5"]["body"].startswith("[p. 555] Variable | Definition\na, b | Limits")
    assert "[p. 557] σci | Unconfined compressive strength of rock" in secs["7-5"]["body"]
    # "Table 7 1" on p. 509 (the hyphen missing on the page) put back
    assert "summarized in Table 7-1." in secs["7-2.1"]["body"]
    # the print's own slips stay noted where they were
    assert "(i.e., N(1,0)). [As printed on p. 538." in secs["7-4.2.3"]["body"]
    assert "at least 10⁶ trials. [Note, not printed (build check" in secs["7-4.2.4"]["body"]
    # 7-6 SUGGESTED READING has no section here and is not stored
    assert "Benjamin, J. R." not in secs["7-5"]["body"]


def test_search_and_fetch_through_the_database():
    hits = _retrieval_db.reference_search("importance sampling controlled variates",
                                          reference=REF, limit=5)
    assert any(h["section_id"] == "7-4.2.4" for h in hits)
    sec = _retrieval.retrieve_section(REF, "7-4.2.4")
    assert "[p. 541]" in sec["body"]


# --- the build ------------------------------------------------------------

def _builder():
    pytest.importorskip("fitz")
    if not PDF.exists():
        pytest.skip("PDF not checked out")
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import build_dm72_bodies as builder
    finally:
        sys.path.remove(str(ROOT / "scripts"))
    return builder


def test_rebuild_reproduces_the_committed_bodies():
    # the typed formula lines, notes and kept tables live in the manifest,
    # so a rebuild from the PDF gives the committed files back
    builder = _builder()
    chapters, report = builder.build_chapters(sorted(BUILT))
    assert report == [], report
    for stem, data in chapters.items():
        committed = (TEXT / f"{stem}.json").read_text(encoding="utf-8")
        assert builder.chapter_json(data) == committed, stem


# --- scatter patterns (build rule 2a) ---------------------------------------
# What a formula taken from the text layer looks like when it has come apart:
# a prime parted from its symbol, a number left on a line of its own above
# the formula, brackets that do not pair, a sentence that follows a table
# copied into each row, and the glyphs of an equation object left in a line.

_PRIMES = (re.compile(r"(?<=\s)['′’ʹ](?=\s)"), re.compile(r"\(['′’ʹ]\)"))
_OPS = re.compile(r"[+\-−×·*/÷^√Σ²³½]")
_ENUM = re.compile(r"(?:^|(?<=[.:;•\]] )|(?<=\s)(?=\d{1,2}\)\s[A-Z]))"
                   r"(?:\d{1,2}|[a-zA-Z]|[ivx]{1,4})\)(?=\s)")
#: brackets the page itself leaves unpaired (checked on the render)
_PRINTED_UNPAIRED: set = set()
#: a prime the page itself sets alone: "the prime symbol (ʹ)" (p. 2)
_PRINTED_PRIMES = {("P-2.1", "the prime symbol (ʹ)")}


def _formula_lines(body):
    for line in body.split("\n"):
        for m in re.finditer("=", line):
            if _OPS.search(line[max(0, m.start() - 30): m.end() + 30]):
                yield line
                break


@pytest.mark.parametrize("stem", sorted(BUILT))
def test_no_scatter_patterns_in_the_bodies(stem):
    bad = []
    for sid, s in _sections(stem).items():
        body = s["body"]
        for i, snip in _PRINTED_PRIMES:
            if i == sid:
                body = body.replace(snip, "")
        for r in _PRIMES:
            bad += [f"{sid}: prime parted {body[max(0, m.start() - 20):m.end() + 8]!r}"
                    for m in r.finditer(body)]
        lines = body.split("\n")
        for i, ln in enumerate(lines):
            if re.fullmatch(r"\s*\d{1,2}\s*", ln):
                nxt = next((x for x in lines[i + 1:] if x.strip()), "")
                if "=" in nxt:
                    bad.append(f"{sid}: lone number {ln!r} above {nxt[:50]!r}")
        for ln in _formula_lines(body):
            if any(i == sid and snip in ln for i, snip in _PRINTED_UNPAIRED):
                continue
            t = re.sub(r"\[p\. [^\]]+\]|\[Eq\. [^\]]+\]", "", _ENUM.sub("", ln))
            for a, b in ("()", "[]", "{}"):
                if t.count(a) != t.count(b):
                    bad.append(f"{sid}: {a}{b} unpaired in {ln[:80]!r}")
        # the glyphs of an equation object run into a line ("( ) 2 2 2 w e t")
        bad += [f"{sid}: equation glyphs {m.group(0)!r}"
                for m in re.finditer(r"(?:(?<=\s)|^)(?:\( \)|[=∑∫−+] ){2,}", body)]
        bad += [f"{sid}: unread formula {m.group(0)[:60]!r}" for m in re.finditer(r"\[\[FORMULA[^\]]*", body)]
        bad += [f"{sid}: word repeated {m.group(0)[:60]!r}"
                for m in re.finditer(r"\b(\w[\w()'’.-]*)(?:\s+\1\b){2,}", body)
                if m.group(1).strip("_") and not m.group(1).isdigit()]
        prev = None
        for ln in lines:
            cells = [c.strip() for c in ln.split(" | ")] if " | " in ln else None
            if cells and prev:
                bad += [f"{sid}: sentence repeated in rows {c[:60]!r}"
                        for c in set(cells) & set(prev)
                        if len(c) >= 60 and re.search(r"[.?!]\)?$", c)]
            prev = cells
    assert bad == []
