"""A search scoped to a reference or chapter that does not exist says so.

2026-11-10 review (core-06): an unknown ``reference`` or a ``chapter`` with
nothing in it came back as an empty list, the same answer as "nothing in
the library says this", so a helper reported that a manual was silent when
it had never been searched.
"""

import pytest

from geotech_references import _figures_db, _retrieval_db


def _error(out):
    """The error text of a search result in either shape."""
    if isinstance(out, dict):
        assert set(out) == {"error"}
        return out["error"]
    assert len(out) == 1 and set(out[0]) == {"error"}
    return out[0]["error"]


SHAPES = [{}, {"max_chars": 14000}]


@pytest.mark.parametrize("kwargs", SHAPES)
@pytest.mark.parametrize("reference", ["GEC-3", "nope", "gec_1", "FHWA"])
def test_text_search_of_an_unknown_reference_names_the_ids(reference, kwargs):
    err = _error(_retrieval_db.reference_search(
        "bearing capacity", reference=reference, **kwargs))
    assert f"no reference '{reference}'" in err
    for known in ("dm7_1", "gec_12", "ufc_pavement"):
        assert known in err


@pytest.mark.parametrize("kwargs", SHAPES)
def test_text_search_of_a_missing_chapter_names_the_chapters(kwargs):
    err = _error(_retrieval_db.reference_search(
        "pile", reference="gec_12", chapter=40, **kwargs))
    assert "no chapter 40 in gec_12" in err
    assert "chapters there: 1, 2, 3" in err and "22" in err
    # a chapter the reference has still searches
    hits = _retrieval_db.reference_search("pile", reference="gec_12",
                                          chapter=7, **kwargs)
    hits = hits["hits"] if isinstance(hits, dict) else hits
    assert hits and all(h["chapter"] == 7 for h in hits)


def test_fetch_from_an_unknown_reference_names_the_ids():
    with pytest.raises(KeyError) as e:
        _retrieval_db.reference_get("gec_1", "7.2")
    assert "no reference 'gec_1'" in str(e.value) and "gec_12" in str(e.value)
    # another spelling of an id is that reference, as in the searches
    # (2026-11-10 review follow-up; it was refused here)
    assert _retrieval_db.reference_get("gec12", "7.2")["reference"] == "gec_12"
    # a known reference still reports the missing section, with its neighbours
    with pytest.raises(KeyError, match="not found in reference 'gec_12'"):
        _retrieval_db.reference_get("gec_12", "7.99")


@pytest.mark.parametrize("kwargs", SHAPES)
def test_figure_search_of_a_missing_chapter_names_the_chapters(kwargs):
    err = _error(_figures_db.figure_search(
        "pile", reference="gec_12", chapter=40, **kwargs))
    assert "no figures filed under chapter 40 in gec_12" in err
    assert "chapters with figures there:" in err and "7" in err
    hits = _figures_db.figure_search("pile", reference="gec_12", chapter=7,
                                     **kwargs)
    hits = hits["hits"] if isinstance(hits, dict) else hits
    assert hits and all(h["chapter"] == 7 for h in hits)


def test_figure_search_takes_a_chapter_as_the_catalog_files_it():
    # the AASHTO 1993 Guide's figures are filed by Part and chapter
    hits = _figures_db.figure_search("layer coefficient",
                                     reference="aashto_1993", chapter="II-2")
    assert hits and all(h["chapter"] == "II-2" for h in hits)
    err = _error(_figures_db.figure_search(
        "layer coefficient", reference="aashto_1993", chapter=2))
    assert "II-2" in err


def test_a_loosely_spelled_reference_says_what_it_was_read_as():
    out = _figures_db.figure_search("alpha adhesion", reference="GEC-10",
                                    max_chars=14000)
    assert out["resolved_reference"] == "gec_10"
    assert out["hits"] and all(h["reference"] == "gec_10" for h in out["hits"])
    exact = _figures_db.figure_search("alpha adhesion", reference="gec_10",
                                      max_chars=14000)
    assert "resolved_reference" not in exact
    # the text search reads the name the same way (2026-11-10 follow-up)
    text = _retrieval_db.reference_search("alpha adhesion", reference="GEC-10",
                                          max_chars=14000)
    assert text["resolved_reference"] == "gec_10"
    assert text["hits"] == _retrieval_db.reference_search(
        "alpha adhesion", reference="gec_10", max_chars=14000)["hits"]
