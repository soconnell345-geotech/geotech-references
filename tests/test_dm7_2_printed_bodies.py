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
            assert m, (sid, e["id"])
            assert m.group(1) in e["description"], (sid, e["id"], m.group(1))


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
