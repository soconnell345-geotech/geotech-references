"""What a search's ``reference`` names, the same in both search layers.

2026-11-10 review follow-up (the independent check of the core fixes):

* a report number given as the scope of ``figure_search`` resolved to the
  whole manual, so FHWA-NHI-06-089 (Soils and Foundations Vol II) returned
  Vol I figures first, and ``reference_search`` refused the same number. A
  volume's own number now searches that volume in both, and says so;
* ``reference="dm7"`` (the app's module name for UFS 3-220-10 and UFC
  3-220-20) was accepted by ``figure_search`` and refused by
  ``reference_search``. Both refuse it, naming ``dm7_1`` and ``dm7_2``.

Every figure hit carries its ``reference_id``.
"""

import json
from pathlib import Path

import pytest

from geotech_references import _figures_db, _retrieval_db

PKG = Path(__file__).resolve().parents[1] / "geotech_references"

#: (report number, the catalog it is a volume of, a query) -- the three
#: examples of the check (v-core/report_number_scope.py).
VOLUMES = [
    ("FHWA-NHI-10-025", "gec_11", "wall facing"),
    ("FHWA-NHI-16-064", "gec_12", "pile"),
    ("FHWA-NHI-06-089", "fhwa_soils_foundations", "consolidation"),
]


def _chapters_of(ref, number):
    """The chapters whose files carry report ``number``."""
    out = set()
    for p in (PKG / ref / "text").glob("*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("reference_id") == number:
            out.add(data.get("chapter"))
    return out


@pytest.mark.parametrize("number,ref,query", VOLUMES)
def test_a_volume_number_searches_that_volume_s_figures(number, ref, query):
    out = _figures_db.figure_search(query, reference=number, limit=10,
                                    max_chars=14000)
    assert out["hits"], out
    assert all(h["reference"] == ref and h["reference_id"] == number
               for h in out["hits"])
    assert out["resolved_reference"] == ref
    assert out["report_number"] == number
    assert f"{number} is one volume of {ref}" in out["note"]
    # the plain call keeps to the volume too
    plain = _figures_db.figure_search(query, reference=number, limit=10)
    assert plain and all(h["reference_id"] == number for h in plain)
    # the reference id still searches every volume
    whole = _figures_db.figure_search(query, reference=ref, limit=50)
    assert len({h["reference_id"] for h in whole}) > 1


@pytest.mark.parametrize("number,ref,query", VOLUMES)
def test_a_volume_number_searches_that_volume_s_text(number, ref, query):
    chapters = _chapters_of(ref, number)
    assert chapters
    out = _retrieval_db.reference_search(query, reference=number, limit=10,
                                         max_chars=14000)
    assert out["hits"], out
    assert all(h["reference"] == ref and h["chapter"] in chapters
               for h in out["hits"])
    assert out["resolved_reference"] == ref
    assert out["report_number"] == number
    assert f"{number} is one volume of {ref}" in out["note"]
    plain = _retrieval_db.reference_search(query, reference=number, limit=10)
    assert plain and all(h["chapter"] in chapters for h in plain)


def test_a_manual_s_only_number_searches_all_of_it():
    """A report number a whole catalog carries scopes to the catalog and
    adds no volume note."""
    out = _figures_db.figure_search("bond strength", reference="NHI-14-007",
                                    max_chars=14000)
    assert out["hits"] and out["resolved_reference"] == "gec_7"
    assert "report_number" not in out
    assert out["hits"] == _figures_db.figure_search(
        "bond strength", reference="gec_7", max_chars=14000)["hits"]


def test_every_figure_hit_carries_its_report_number():
    hits = _figures_db.figure_search("pile", limit=50)
    assert hits and all(h.get("reference_id") for h in hits)
    vol2 = _figures_db.figure_search("static load test", reference="gec_12",
                                     limit=50)
    assert {h["reference_id"] for h in vol2 if h["chapter"] == 9} == {
        "FHWA-NHI-16-010"}


@pytest.mark.parametrize("kwargs", [{}, {"max_chars": 14000}])
def test_dm7_is_refused_the_same_way_by_both_searches(kwargs):
    errors = []
    for search in (_figures_db.figure_search, _retrieval_db.reference_search):
        out = search("earth pressure", reference="dm7", **kwargs)
        if isinstance(out, list):
            assert len(out) == 1 and set(out[0]) == {"error"}
            out = out[0]
        assert set(out) == {"error"}
        errors.append(out["error"])
    assert errors[0] == errors[1]
    assert "'dm7' names 2 references here: dm7_1" in errors[0]
    assert "dm7_2" in errors[0]
    # a figure lookup still reads dm7 by the figure asked for
    assert _figures_db.resolve_reference("dm7", "P-6") == "dm7_2"
