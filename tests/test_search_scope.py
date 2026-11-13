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


# ---------------------------------------------------------------------------
# 2026-11-10 review follow-up, second round
# ---------------------------------------------------------------------------

from agents import references_agent  # noqa: E402
from geotech_references import _retrieval  # noqa: E402


def _stored_ids():
    """(layer, reference, stored report number) of every stored id."""
    conn = _retrieval_db._ro_connect()
    try:
        text = _retrieval_db._held(conn)
    finally:
        conn.close()
    conn = _figures_db._ro_connect()
    try:
        figs = _figures_db._catalog_refs(conn)
    finally:
        conn.close()
    return ([("text", rid, n) for rid, _, nums in text for n in nums]
            + [("figures", rid, n) for rid, _, nums in figs for n in nums])


# 2a. The plain list shows the volume: every text hit carries reference_id,
# and the agent's search tool returns the form with the scope note.

def test_every_text_hit_carries_its_report_number():
    hits = _retrieval_db.reference_search("pile", limit=50)
    assert hits and all(h.get("reference_id") for h in hits)
    plain = _retrieval_db.reference_search(
        "consolidation", reference="FHWA-NHI-06-089", limit=10)
    assert plain and {h["reference_id"] for h in plain} == {"FHWA-NHI-06-089"}


def test_the_agent_search_tool_carries_the_scope_note():
    out = json.loads(references_agent.reference_search(
        "consolidation", reference="FHWA-NHI-06-089", limit=5))
    assert out["resolved_reference"] == "fhwa_soils_foundations"
    assert out["report_number"] == "FHWA-NHI-06-089"
    assert "is one volume of fhwa_soils_foundations" in out["note"]
    assert out["hits"] and all(h["reference_id"] == "FHWA-NHI-06-089"
                               for h in out["hits"])
    # paging is offered and taken
    nxt = json.loads(references_agent.reference_search(
        "consolidation", reference="FHWA-NHI-06-089", limit=5, offset=5))
    assert nxt["hits"] and nxt["hits"][0] != out["hits"][0]
    err = json.loads(references_agent.reference_search("pile",
                                                       reference="dm7"))
    assert set(err) == {"error"} and "dm7_1" in err["error"]


# 2b. A stored id's designation alone resolves, in both searches.

@pytest.mark.parametrize("layer,ref,stored", _stored_ids())
def test_a_stored_id_s_designation_resolves(layer, ref, stored):
    search = (_retrieval_db.reference_search if layer == "text"
              else _figures_db.figure_search)
    designation = _retrieval_db.designation(stored)
    forms = {stored, designation,
             _retrieval_db._STANDARD_YEAR.sub("", designation)}
    for form in forms:
        out = search("the", reference=form, limit=3, max_chars=14000)
        assert "error" not in out, (form, out)
        assert out.get("resolved_reference", ref) == ref, (form, out)
        assert all(h["reference"] == ref for h in out["hits"])


@pytest.mark.parametrize("name,ref", [
    ("FHWA-NHI-05-037", "fhwa_pavements"),   # stored with its title after
    ("EN 1997-1", "eurocode_7_1"),           # stored as EN 1997-1:2004
    ("EN 1997-2", "eurocode_7_2"),
])
def test_the_lead_s_examples_resolve_in_both_searches(name, ref):
    for search in (_retrieval_db.reference_search, _figures_db.figure_search):
        out = search("design", reference=name, limit=3, max_chars=14000)
        assert out["resolved_reference"] == ref and out["hits"]


def test_a_number_that_could_be_several_is_refused_naming_them():
    """'2-2007' ends both EN 1997-2:2007 and UFC 3-220-07: it searched both
    catalogs without a word."""
    out = _figures_db.figure_search("design", reference="2-2007",
                                    max_chars=14000)
    assert set(out) == {"error"}
    assert "could be more than one report number here" in out["error"]
    assert "EN 1997-2:2007 (eurocode_7_2)" in out["error"]
    assert "UFC 3-220-07 (ufc_expansive)" in out["error"]
    with pytest.raises(KeyError, match="could be more than one"):
        _figures_db.figure_get("2-2007", "1")
    # a standard's number without its part is no designation: refused,
    # naming the ids (a name that only begins one is loose, core-09)
    out = _figures_db.figure_search("design", reference="EN 1997",
                                    max_chars=14000)
    assert "no figure catalog 'EN 1997'" in out["error"]


# 7a. Every function that takes a reference reads it the same way.

TEXT_CALLS = {
    "reference_get": lambda n: _retrieval_db.reference_get(n, "7.2")["title"],
    "retrieve_section": lambda n: _retrieval.retrieve_section(n, "7.2")[
        "title"],
    "load_chapter": lambda n: _retrieval.load_chapter(n, 7)["chapter"],
    "list_chapters": lambda n: len(_retrieval.list_chapters(n)),
    "search_sections": lambda n: len(_retrieval.search_sections(
        n, "Nordlund")),
    "reference_search": lambda n: len(_retrieval_db.reference_search(
        "Nordlund", reference=n)),
}
FIGURE_CALLS = {
    "figure_get": lambda n: _figures_db.figure_get(n, "7-1")["caption"],
    "resolve_pdf": lambda n: _figures_db.resolve_pdf(n, "7-1")[1],
    "figure_search": lambda n: len(_figures_db.figure_search(
        "pile", reference=n)),
}


@pytest.mark.parametrize("call", sorted(TEXT_CALLS) + sorted(FIGURE_CALLS))
def test_every_function_reads_a_reference_the_same_way(call):
    fn = {**TEXT_CALLS, **FIGURE_CALLS}[call]
    want = fn("gec_12")
    for name in ("gec12", "GEC-12", "FHWA-NHI-16-009"):
        assert fn(name) == want, name


@pytest.mark.parametrize("call", sorted(TEXT_CALLS))
def test_an_unknown_or_shared_name_is_refused_the_same_way(call):
    fn = TEXT_CALLS[call]
    for name, says in (("nope", "no reference 'nope' in the text index"),
                       ("dm7", "'dm7' names 2 references here")):
        if call == "reference_search":  # a search answers, not raises
            out = _retrieval_db.reference_search("Nordlund", reference=name)
            assert says in out[0]["error"]
            continue
        with pytest.raises((KeyError, FileNotFoundError)) as e:
            fn(name)
        assert says in str(e.value)


def test_the_agent_dispatcher_reads_a_reference_the_same_way():
    want = json.loads(references_agent.lookup_reference(
        "gec_12", "retrieve_section", '{"section_id": "7.2"}'))
    for name in ("gec12", "FHWA-NHI-16-009"):
        assert json.loads(references_agent.lookup_reference(
            name, "retrieve_section", '{"section_id": "7.2"}')) == want
    out = json.loads(references_agent.lookup_reference(
        "dm7", "retrieve_section", '{"section_id": "7.2"}'))
    assert "'dm7' names 2 references here" in out["error"]
