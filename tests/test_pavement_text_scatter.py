"""Signs of text-layer scatter in the pavement references' chapter text.

An earlier build took formulas from the PDF text layer and stored them
scrambled: a prime cut loose from its symbol, a superscript left on a line of
its own above the formula, a bracket that never closes, a sentence repeated
row after row of a table. The 2026-11-12 build (app BACKLOG REF-83) read every
formula line of these three references from the rendered page; this test
looks for those signs in every body and stored formula. Each case that the
print itself shows is listed below with where it is printed, so a new hit is
either a fresh scatter or a printed case to check on the page and add.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "geotech_references"
REFS = ("aashto_1993", "ufc_pavement", "ufc_stabilization")

# a prime alone between spaces, or "(')": a symbol's prime that lost its symbol
LOOSE_PRIME = re.compile(r"\(\s*['′]\s*\)|(?:^|\s)['′](?:\s|$)", re.M)
# a line holding only a short number (a superscript or subscript left behind)
LONE_NUMBER = re.compile(r"^\s*[-−]?[\d.]{1,4}\s*$")
# a list marker "1)" or "a)" opening a paragraph or following ": " or ". "
# closes nothing
LIST_MARKER_BEFORE = re.compile(r"(?:^|[:.;] )(?:\d{1,2}|[A-Za-z])$")
OPENER = {")": "(", "]": "[", "}": "{"}


def unbalanced(para: str) -> list[str]:
    """Brackets in a paragraph that do not pair, by position."""
    stack, bad = [], []
    for i, ch in enumerate(para):
        if ch in "([{":
            stack.append((ch, i))
        elif ch in OPENER:
            if stack and stack[-1][0] == OPENER[ch]:
                stack.pop()
            elif not (ch == ")" and LIST_MARKER_BEFORE.search(para[:i])):
                bad.append(f"{ch} at {i}")
    return bad + [f"{ch} at {i} not closed" for ch, i in stack]

# Unbalanced brackets the print shows; the body names the slip in a note.
PRINTED_UNBALANCED = {
    ("aashto_1993", "II-2.4.2"): 'The print closes no parenthesis after "1 1/4 inch".',
}

# Sentences of 60 characters or more that a body holds more than once, each
# checked on the page (2026-11-12).
PRINTED_REPEATS = {
    # Figures 2.3 (blank form, p. II-14) and 2.4 (worked example, p. II-15) print one title
    ("aashto_1993", "II-2.3.1", "Chart for Estimating Effective Roadbed Soil Resilient Modulus"),
    # Table 3.2's blank worksheet (p. II-38) and the worked example (p. II-43) print the same columns
    ("aashto_1993", "II-3.2.1", "Columns: (1) Month | (2) Roadbed Modulus"),
    # Figures 3.10, 3.11 and 3.12 each print "Nomograph solves:" above their equation
    ("aashto_1993", "II-3.4.2.a", 'Printed on the chart: "Nomograph solves:"'),
    # Figures 3.13 (p. II-63) and 3.14 (p. II-64) each print the 48-inch spacing note across the top
    ("aashto_1993", "II-3.4.3", 'printed across the top: "Spacings greater than 48'),
    # Tables 4.8(a), 4.9(a) and 4.9(b) print one title (pp. II-82, II-84, II-85)
    ("aashto_1993", "II-4.2.2", "Rigid Design Catalog for Low-Volume Roads: Recommended Minimum PCC Slab"),
    # Tables 4.8(a) (p. II-82) and 4.9(b) (p. II-85) print the same medium-traffic row
    ("aashto_1993", "II-4.2.2", "Medium Traffic: Very good & good | 6.25 | 5.75 | 5.75 | 5.25 | 6 | 5.5 | 5.5 | 5"),
    # the build's own column line for Tables 4.8(b), 4.9(a) and 4.9(b)
    ("aashto_1993", "II-4.2.2", "Columns as in Table 4.8(a)"),
    # printed under both 2-1.1.1 (p. 3) and 2-1.1.2 (p. 4)
    ("ufc_stabilization", "2-1.1", "Use layered elastic pavement design procedures described in UFC 3-260-02"),
    # printed under both 2-1.1.4 and 2-1.1.5 (p. 4)
    ("ufc_stabilization", "2-1.1", "Bitumen and polymers are not effective against freeze-thaw action"),
}


def _texts():
    for ref in REFS:
        for f in sorted((ROOT / ref / "text").glob("*.json")):
            for s in json.loads(f.read_text(encoding="utf-8"))["sections"]:
                yield ref, s["section_id"], "body", s.get("body") or ""
                for e in s.get("equations") or []:
                    if e.get("formula"):
                        yield ref, s["section_id"], "formula", e["formula"]


TEXTS = list(_texts())


def test_texts_found():
    refs = {r for r, *_ in TEXTS}
    assert refs == set(REFS)
    assert len(TEXTS) > 400


def test_no_loose_primes():
    hits = [(r, sid, kind, t[max(0, m.start() - 30):m.end() + 30])
            for r, sid, kind, t in TEXTS for m in LOOSE_PRIME.finditer(t)]
    assert not hits, hits


def test_no_lone_number_line_above_a_formula():
    hits = []
    for r, sid, kind, t in TEXTS:
        lines = t.split("\n")
        for a, b in zip(lines, lines[1:]):
            if LONE_NUMBER.match(a) and "=" in b:
                hits.append((r, sid, kind, a, b[:60]))
    assert not hits, hits


def test_brackets_balance_in_each_paragraph():
    hits = []
    for r, sid, kind, t in TEXTS:
        for para in t.split("\n\n"):
            bad = unbalanced(para)
            if not bad:
                continue
            note = PRINTED_UNBALANCED.get((r, sid))
            if note and note in para:
                continue
            hits.append((r, sid, kind, bad, para[:100]))
    assert not hits, hits


def _repeats(t: str):
    sents = [x.strip() for x in re.split(r"(?<=[.;])\s+", t) if len(x.strip()) >= 60]
    return [x for x, n in Counter(sents).items() if n > 1]


def test_no_unchecked_repeated_sentence():
    hits = []
    for r, sid, kind, t in TEXTS:
        for x in _repeats(t):
            if not any(r == pr and sid == ps and x.startswith(pp) for pr, ps, pp in PRINTED_REPEATS):
                hits.append((r, sid, kind, x[:100]))
    assert not hits, hits


@pytest.mark.parametrize("ref, sid, prefix", sorted(PRINTED_REPEATS))
def test_listed_repeats_are_still_there(ref, sid, prefix):
    # a stale entry would excuse a later scatter
    found = [x for r, s, _, t in TEXTS if (r, s) == (ref, sid) for x in _repeats(t)]
    assert any(x.startswith(prefix) for x in found), (ref, sid, prefix)


def test_no_sentence_repeated_in_consecutive_table_rows():
    # rows of a typed table are "label | cell | cell" separated by "; "; a
    # cell that is a sentence (four words or more) should not run down rows
    hits = []
    for r, sid, kind, t in TEXTS:
        for para in t.split("\n\n"):
            if para.count("|") < 4:
                continue
            rows = [row.split("|") for row in re.split(r";\s+", para)]
            for prev, row in zip(rows, rows[1:]):
                prev_cells = {c.strip() for c in prev[1:]}
                for c in row[1:]:
                    c = c.strip()
                    if len(re.findall(r"[A-Za-z]{2,}", c)) >= 4 and c in prev_cells:
                        hits.append((r, sid, c[:80]))
    assert not hits, hits
