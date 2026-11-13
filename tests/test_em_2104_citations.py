"""em_2104 page citations (app BACKLOG REF-98, part 1).

The printed page of every corrected citation is pinned, and, where PyMuPDF
and the PDF are present, the cited label is looked up on that printed page
of EM_1110-2-2104_2025.pdf (PDF page index = printed page + 5; the folio
printed on each page was checked to be constant through the appendices).
"""
import os
import re

import pytest

from geotech_references.em_2104 import design, flexure_axial, loads

PDF = os.path.join(os.path.dirname(__file__), "..", "docs",
                   "EM_1110-2-2104_2025.pdf")
OFFSET = 5

# (what, call, expected 'printed_page', [(label as printed, printed page)])
CASES = [
    ("Eq B-22 phi*Pn(max), doubly reinforced",
     lambda: flexure_axial.max_axial_capacity_doubly(
         0.65, 4.0, 288.0, 0.02, 0.01, 60.0, 240.0),
     "45", [("(B-22)", 45)]),
    ("Eq B-42 ku, tension, e'/d < 0",
     lambda: flexure_axial.tension_controlled_by_compression_side_ku(
         -0.5, 0.01, 60.0, 4.0),
     "50", [("(B-42)", 50)]),
    ("Eq B-43 phi*Pn, pure tension",
     lambda: flexure_axial.pure_tension_capacity(0.9, 2.0, 1.0, 60.0),
     "50", [("(B-43)", 50)]),
    ("Eqs B-44 to B-48, tension between layers",
     lambda: flexure_axial.tension_between_layers_capacity(
         0.3, 0.1, 0.01, 0.005, 60.0),
     "50-51", [("(B-44)", 50), ("(B-48)", 51)]),
    ("Eq D-5 minimum effective depth",
     lambda: design.minimum_effective_depth(5000.0, 12.0, 4.0, 0.4),
     "71", [("(D-5)", 71)]),
    ("Eq 4-3 kb",
     lambda: flexure_axial.balanced_strain_kb(0.85, 60.0),
     "30", [("(4-3)", 30)]),
    ("Eqs 4-1 and 4-2 eccentricity",
     lambda: flexure_axial.eccentricity_ratio(1200.0, 50.0, 16.0, 20.0),
     "29-30", [("(4-1)", 29), ("(4-2)", 30)]),
    ("Table 3-2 load factors",
     lambda: loads.table_3_2_load_factor("Hs", "usual"),
     "24-25", [("Table 3-2", 24), ("Hawser", 25)]),
]


@pytest.mark.parametrize("what,call,expected,labels", CASES,
                         ids=[c[0] for c in CASES])
def test_cited_printed_page_is_pinned(what, call, expected, labels):
    r = call()
    assert r["printed_page"] == expected
    pdf = r["pdf_page_index"]
    first = int(expected.split("-")[0]) + OFFSET
    assert (pdf[0] if isinstance(pdf, list) else pdf) == first


def test_resistance_factor_comment_cites_p_121():
    src = flexure_axial.__file__
    with open(src, encoding="utf-8") as f:
        head = f.read(4000)
    assert "Appendix F commentary (printed p. 121)" in head


def _pages():
    fitz = pytest.importorskip("pymupdf")
    if not os.path.exists(PDF):
        pytest.skip("EM_1110-2-2104_2025.pdf not present")
    return fitz.open(PDF)


def _text(doc, printed):
    t = doc[printed + OFFSET].get_text()
    return t.replace("\u2013", "-").replace("\u2011", "-").replace("\u00a0", " ")


@pytest.mark.parametrize("what,call,expected,labels", CASES,
                         ids=[c[0] for c in CASES])
def test_label_is_on_the_cited_page(what, call, expected, labels):
    doc = _pages()
    for label, printed in labels:
        t = _text(doc, printed)
        assert label in t, f"{label} not on printed p. {printed} ({what})"
        assert re.search(r"\n%d\s*\n" % printed, t + "\n"), \
            f"folio {printed} not printed on that page"


def test_resistance_factors_without_modification_is_on_p_121():
    doc = _pages()
    assert "without modification" in _text(doc, 121)
