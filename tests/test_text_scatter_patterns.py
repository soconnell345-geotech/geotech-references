"""Stored bodies carry none of the text layer's scatter patterns (app backlog REF-83).

A PDF text layer scatters a typeset formula: a prime comes loose from its symbol, an
exponent or a stacked denominator lands on its own line, brackets lose their partner,
and a sentence after a table is copied into each continuation row. The structural
references rebuilt from the print are scanned for each pattern. A bracket the print
itself leaves unpaired is listed with its page.
"""

import json
import re

import pytest

from geotech_references._retrieval import list_chapters, load_chapter

REFERENCES = ["ufc_structural", "em_2104", "em_2107", "wood_handbook", "ufc_collapse"]

# (reference, section, the text around it): printed so.
PRINTED_UNPAIRED = {
    ("ufc_collapse", "1-8"): "Design Approach (Tie Forces (TF) or Alternate Path (AP), and",  # PDF p. 22
    ("ufc_collapse", "3-1.4.1"): "((lb/ft2 or kN/m2)",  # PDF p. 38
    ("ufc_structural", "2-5"): "in MIL STD 3007).",  # PDF p. 46
}


def _sections(reference):
    for ch in list_chapters(reference, sections=False):
        number = ch["chapter"] if isinstance(ch, dict) else ch
        for s in load_chapter(reference, number)["sections"]:
            yield s


def _unpaired(body):
    """Positions of brackets without a partner; '1)' and 'a)' list markers are not brackets."""
    found, stack = [], []
    pairs = {")": "(", "]": "[", "}": "{"}
    for i, ch in enumerate(body):
        if ch in "([{":
            stack.append((ch, i))
        elif ch in pairs:
            if stack and stack[-1][0] == pairs[ch]:
                stack.pop()
            elif ch == ")" and re.search(r"(?:^|[\s;:,])(\d{1,2}|[a-z])$", body[max(0, i - 4):i]):
                continue
            else:
                found.append(i)
                stack = []
    return found + [i for _, i in stack]


@pytest.mark.parametrize("reference", REFERENCES)
def test_no_loose_primes(reference):
    for s in _sections(reference):
        m = re.search(r"(?<![\w′'\"“”])['′](?![\w])|\(\s*['′]\s*\)", s["body"])
        assert not m, (reference, s["section_id"], s["body"][max(0, m.start() - 40):m.end() + 40])


@pytest.mark.parametrize("reference", REFERENCES)
def test_no_lone_digit_before_a_formula(reference):
    # an exponent or index pulled out of a typeset formula: "... 2 fx = 3M/ ..."
    pat = re.compile(r"(?:^|[.;:]\s)\d\s+[A-Za-zα-ωΣ]\w{0,6}\s*=\s*[^=;.]{0,30}[+\-−×*/√^]")
    for s in _sections(reference):
        m = pat.search(s["body"])
        assert not m, (reference, s["section_id"], m.group(0))


@pytest.mark.parametrize("reference", REFERENCES)
def test_brackets_pair_up(reference):
    for s in _sections(reference):
        body = s["body"]
        allowed = PRINTED_UNPAIRED.get((reference, s["section_id"]))
        for i in _unpaired(body):
            around = body[max(0, i - 80):i + 80]
            assert allowed and allowed in around, (reference, s["section_id"], around)


@pytest.mark.parametrize("reference", REFERENCES)
def test_no_sentence_repeated_in_consecutive_rows(reference):
    for s in _sections(reference):
        sents = [x.strip() for x in re.split(r"(?<=[.])\s+", s["body"]) if len(x.strip()) > 40]
        for a, b in zip(sents, sents[1:]):
            assert a != b, (reference, s["section_id"], a[:120])


def test_printed_exceptions_are_still_there():
    for (reference, sid), text in PRINTED_UNPAIRED.items():
        body = next(s["body"] for s in _sections(reference) if s["section_id"] == sid)
        assert text in body, (reference, sid)


def test_worked_example_formula_lines_as_printed():
    # Wood Handbook pp. 9-10 and 9-12, read from the rendered pages.
    body = {s["section_id"]: s["body"] for s in _sections("wood_handbook")}
    assert "fx = 375M, fxy = 37.5M, fy = 3.75M" in body["9-4"]
    assert "M = 1/(3.75 [10^4/Fx^2 + 10^2/Fxy^2 + 1/Fy^2]^(1/2))" in body["9-4"]
    assert "ft max = (fb0 - P e0/S)/(1 + P/Pcr) + P/A" in body["9-7"]
    assert "R1 = 10,000 [56/(2,160(1 + 6))]^(1/18) = 7,330 lbf in^-2" in body["9-5"]
    em = json.dumps(load_chapter("em_2104", 4), ensure_ascii=False)
    assert "0.85f′c" in em and "fc ′" not in em
