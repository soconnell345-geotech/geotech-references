"""Every level of a chapter file is addressable (REF-24).

GEC-12 nests 76 sections inside others (every chapter 7 static method,
group efficiency, uplift, setup, settlement, p-y); until REF-24 none could
be searched for or fetched by its own number. The other references list
every level flat and gained the chain above a section and the list below
it. The questions in ``scripts/eval_subsection_retrieval.py`` keep the
librarian's route to a subsection's answer short.
"""

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

import geotech_references._query_expansion as _qe
from geotech_references import _retrieval, _retrieval_db

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "eval_subsection_retrieval",
    ROOT / "scripts" / "eval_subsection_retrieval.py")
evs = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = evs
_spec.loader.exec_module(evs)

CAP = evs.APP_REFERENCE_CAP


@pytest.fixture(scope="module", autouse=True)
def _ensure_db():
    _retrieval_db._ensure_db()
    yield


@pytest.fixture
def auto_expansion(monkeypatch):
    monkeypatch.setattr(_qe, "EXPANSION_STRATEGY", "auto")


def _size(obj) -> int:
    return len(json.dumps(obj, default=str))


# ---------------------------------------------------------------------------
# the questions: the answer's own section is found and fetched cheaply
# ---------------------------------------------------------------------------

def test_questions_span_references_beyond_gec_12():
    refs = {q["ref"] for q in evs.QUESTIONS}
    assert len(evs.QUESTIONS) >= 12
    assert len(refs - {"gec_12"}) >= 4


@pytest.mark.parametrize("q", evs.QUESTIONS,
                         ids=[f"{q['ref']}:{q['target']}" for q in evs.QUESTIONS])
def test_question_reaches_its_section(q, auto_expansion):
    tree = evs.section_tree(q["ref"])
    assert q["target"] in tree, "the answer's section is no longer in the file"
    r = evs.replay(q, tree)
    assert r["rank"] is not None and r["rank"] <= evs.K, r
    assert r["reached"], r
    # one search and one fetch of the section itself
    assert r["route"] == f"search -> get {q['target']}"
    assert r["fetch_chars"] < CAP


# ---------------------------------------------------------------------------
# every section resolves by its own number, at every level
# ---------------------------------------------------------------------------

def _all_ids():
    conn = sqlite3.connect(str(_retrieval_db._ensure_db()))
    try:
        return conn.execute(
            "SELECT reference, section_id, MIN(rowid), parent_rowid IS NOT NULL "
            "FROM sections GROUP BY reference, section_id").fetchall()
    finally:
        conn.close()


def test_every_section_resolves_in_the_db_within_the_app_cap():
    assert _retrieval.SUBSECTIONS_INLINE_MAX_CHARS < CAP
    ids = _all_ids()
    assert len(ids) > 3800
    for ref, sid, _rowid, _has_parent in ids:
        got = _retrieval_db.reference_get(ref, sid)
        assert got["section_id"] == sid
        assert "children" in got and "under" in got and "parent_id" in got
        assert _size(got) < CAP, (ref, sid)
        if got["children"]:
            inlined = _retrieval_db.reference_get(ref, sid,
                                                  include_subsections=True)
            assert _size(inlined) < CAP, (ref, sid)


def test_every_gec_12_section_resolves_in_both_layers():
    entries = []
    for jf in sorted((ROOT / "geotech_references" / "gec_12" / "text")
                     .glob("*.json")):
        entries += _retrieval.section_entries(
            json.loads(jf.read_text(encoding="utf-8")))
    nested = [e for e in entries if e["nested"]]
    assert len(nested) >= 76
    for e in entries:
        sid = e["section"]["section_id"]
        legacy = _retrieval.retrieve_section("gec_12", sid)
        db = _retrieval_db.reference_get("gec_12", sid)
        assert legacy["section_id"] == db["section_id"] == sid
        assert legacy["body"] == db["body"] == e["section"].get("body", "")
        assert legacy["under"] == db["under"]
        assert legacy["children"] == db["children"]
        if e["nested"]:
            assert db["under"], sid


def test_the_old_top_level_ids_still_resolve():
    for ref, sid in [("gec_12", "1.1"), ("gec_12", "7.2"),
                     ("dm7_1", "5-5.2"), ("dm7_2", "4-5"), ("gec_10", "11.5")]:
        assert _retrieval.retrieve_section(ref, sid)["section_id"] == sid
        assert _retrieval_db.reference_get(ref, sid)["section_id"] == sid


# ---------------------------------------------------------------------------
# a parent lists its children; inlining is opt-in and bounded
# ---------------------------------------------------------------------------

GEC12_72_CHILDREN = ["7.2.1", "7.2.2", "7.2.3", "7.2.4", "7.2.5", "7.2.6",
                     "7.2.7", "7.2.8", "7.2.9", "7.2.10"]


@pytest.mark.parametrize("get", [
    lambda sid, **kw: _retrieval.retrieve_section("gec_12", sid, **kw),
    lambda sid, **kw: _retrieval_db.reference_get("gec_12", sid, **kw),
], ids=["retrieve_section", "reference_get"])
def test_a_parent_lists_its_children_not_their_text(get):
    sec = get("7.2")
    assert [c["section_id"] for c in sec["children"]] == GEC12_72_CHILDREN
    assert "subsections" not in sec
    assert sec["under"] == "" and sec["parent_id"] is None
    # its own text only: ~2 k characters, not the ~28 k of the whole tree
    assert _size(sec) < 4000

    big = get("7.2", include_subsections=True)
    assert "subsections" not in big
    assert "not inlined" in big["note"]
    assert _size(big) <= _retrieval.SUBSECTIONS_INLINE_MAX_CHARS

    small = get("7.2.3", include_subsections=True)
    assert [s["section_id"] for s in small["subsections"]] == [
        "7.2.3.1", "7.2.3.2"]
    assert [s["section_id"] for s in small["subsections"][1]["subsections"]] \
        == ["7.2.3.2.2", "7.2.3.2.3"]   # the printed headings (pp. 291-292)
    assert _size(small) <= _retrieval.SUBSECTIONS_INLINE_MAX_CHARS


def test_a_nested_section_says_where_it_sits():
    sec = _retrieval_db.reference_get("gec_12", "7.2.1.3.1")
    assert sec["title"].startswith("Nordlund")
    assert sec["parent_id"] == "7.2.1"
    assert sec["under"].startswith("7.2 Strength Limit States > 7.2.1 ")
    # a nested section sits under the section the file nests it in
    assert _retrieval_db.reference_get("gec_12", "7.2.8.1")["parent_id"] \
        == "7.2.8"


def test_a_flat_listed_section_sits_under_its_number():
    sec = _retrieval_db.reference_get("dm7_1", "5-5.2")
    assert sec["parent_id"] == "5-5"
    assert "5-5.2.1" in [c["section_id"] for c in sec["children"]]
    # letters as the last part (GEC-11 '3.5.2.c')
    assert _retrieval_db.reference_get("gec_11", "3.5.2.c")["parent_id"] \
        == "3.5.2"


def test_a_missing_number_names_what_is_near_it():
    with pytest.raises(KeyError) as e:
        _retrieval_db.reference_get("gec_12", "7.2.1.3")
    assert "7.2.1 " in str(e.value) and "7.2.1.3.1 Nordlund" in str(e.value)
    with pytest.raises(KeyError):
        _retrieval.retrieve_section("gec_12", "7.2.1.3")


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

def test_search_finds_the_subsection_and_says_where_it_sits(auto_expansion):
    hits = _retrieval_db.reference_search("Nordlund", reference="gec_12")
    ids = [h["section_id"] for h in hits]
    assert "7.2.1.3.1" in ids
    hit = hits[ids.index("7.2.1.3.1")]
    assert hit["under"].startswith("7.2 Strength Limit States > 7.2.1 ")
    assert hit["parent_id"] == "7.2.1"
    assert "body" not in hit

    legacy = _retrieval.search_sections("gec_12", "Nordlund")
    assert legacy[0]["section_id"] == "7.2.1.3.1"
    assert legacy[0]["under"] == hit["under"]
    assert "subsections" not in legacy[0]


#: GEC-12 sections with subsections, found by their own title in the top
#: five with those subsections indexed beside them: short subsections do
#: not crowd out their parent.
GEC12_PARENTS = ["7.2.1", "7.2.2", "7.2.3", "7.2.3.2", "7.2.4", "7.2.8",
                 "7.3.5", "7.3.6", "7.3.7", "7.4", "7.7", "7.10", "7.10.1"]


@pytest.mark.parametrize("sid", GEC12_PARENTS)
def test_a_parent_is_still_found_by_its_title(sid, auto_expansion):
    sec = _retrieval_db.reference_get("gec_12", sid)
    assert sec["children"]
    hits = _retrieval_db.reference_search(sec["title"], reference="gec_12",
                                          limit=5)
    assert sid in [h["section_id"] for h in hits]


# ---------------------------------------------------------------------------
# the tree and the database layout
# ---------------------------------------------------------------------------

def test_id_prefixes():
    assert _retrieval.id_prefixes("4-2.1.3") == ["4-2.1", "4-2", "4"]
    assert _retrieval.id_prefixes("7.2.1.3.1") == [
        "7.2.1.3", "7.2.1", "7.2", "7"]
    assert _retrieval.id_prefixes("3.5.2.f") == ["3.5.2", "3.5", "3"]
    assert _retrieval.id_prefixes("P-1") == ["P"]
    assert _retrieval.id_prefixes("7") == []


def test_section_entries_nested_flat_and_out_of_order():
    chapter = {"sections": [
        {"section_id": "4-1.1", "title": "child listed first"},
        {"section_id": "4-1", "title": "parent", "subsections": [
            {"section_id": "4-1.9", "title": "nested"}]},
        {"section_id": "4-1.2.1", "title": "grandchild, no 4-1.2"},
        {"section_id": "4-1", "title": "duplicate"},
        {"section_id": "5-1", "title": "unrelated"},
    ]}
    entries = _retrieval.section_entries(chapter)
    ids = [e["section"]["section_id"] for e in entries]
    assert ids == ["4-1.1", "4-1", "4-1.9", "4-1.2.1", "4-1", "5-1"]
    parent = {i: entries[i]["parent"] for i in range(len(entries))}
    assert parent[0] == 1          # flat child before its parent
    assert parent[2] == 1          # nested
    assert entries[2]["nested"] and not entries[0]["nested"]
    assert parent[3] == 1          # nearest existing number above
    assert parent[4] is None       # a duplicate is not its own child
    assert parent[5] is None
    assert all("subsections" not in e["section"] for e in entries)


def test_a_database_from_the_old_layout_is_rebuilt(tmp_path, monkeypatch):
    old = tmp_path / "old.sqlite"
    conn = sqlite3.connect(str(old))
    conn.execute("CREATE TABLE sections (x INTEGER)")
    conn.commit()
    conn.close()
    # newer than every source file, but an older layout
    monkeypatch.setattr(_retrieval_db, "_newest_source_mtime", lambda: 0.0)
    assert _retrieval_db._schema_version(old) == 0
    assert _retrieval_db._needs_rebuild(old)
    assert not _retrieval_db._needs_rebuild(_retrieval_db._ensure_db())


def test_list_chapters_includes_nested_sections():
    sections = [s for c in _retrieval.list_chapters("gec_12")
                for s in c["sections"]]
    by_id = {s["section_id"]: s for s in sections}
    assert by_id["7.2.1.3.1"]["parent_id"] == "7.2.1"
    assert "parent_id" not in by_id["7.2"]
    # a flat reference keeps the shape it had
    for c in _retrieval.list_chapters("dm7_1"):
        assert all(set(s) == {"section_id", "title"} for s in c["sections"])
