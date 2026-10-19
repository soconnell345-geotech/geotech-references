"""Results that fit a caller's size limit by their shape (REF-26).

The GeotechStaffEngineer app sends its agent at most 16,000 characters of a
reference tool's result and cuts the rest, which leaves broken JSON: every
chapter's sections for ufc_concrete_practice were 27,820 characters,
reference_search at limit 50 about 36,000, plain search_sections for "pile"
in GEC-12 317,000, a whole chapter over 200,000, one catalog caption 29,911.
With ``max_chars`` each comes back in a shape that fits and says how to get
the rest; without it every function returns what it always did.
"""

import json

import pytest

from geotech_references import _figures_db, _retrieval, _retrieval_db

#: What the app passes (its 16,000-character cap, less room for its own keys).
BUDGET = 14000


def _size(obj) -> int:
    return len(json.dumps(obj, default=str))


def _references() -> list[str]:
    pkg = _retrieval._PACKAGE_DIR
    return sorted(d.name for d in pkg.iterdir() if (d / "text").is_dir())


@pytest.fixture(scope="module", autouse=True)
def _ensure_dbs():
    _retrieval_db._ensure_db()
    _figures_db._ensure_db()
    yield


# ---------------------------------------------------------------------------
# the shared rules
# ---------------------------------------------------------------------------

def test_fit_hits_leaves_a_result_that_fits_alone():
    hits = [{"id": i, "summary": "word " * 40} for i in range(5)]
    out = _retrieval.fit_hits(hits, BUDGET, text_fields=("summary",))
    assert out == {"hits": hits, "shown": 5}


def test_fit_hits_shortens_then_leaves_out_and_says_where_the_rest_starts():
    hits = [{"id": i, "summary": "word " * 400} for i in range(60)]
    out = _retrieval.fit_hits(hits, BUDGET, text_fields=("summary",),
                              offset=20, narrow="narrow it")
    assert _size(out) <= BUDGET
    assert 1 <= out["shown"] < 60
    assert [h["id"] for h in out["hits"]] == list(range(out["shown"]))
    assert all(len(h["summary"]) <= _retrieval.HIT_TEXT_CHARS
               for h in out["hits"])
    assert out["left_out"] == 60 - out["shown"]
    assert out["next_offset"] == 20 + out["shown"]
    assert f"offset={out['next_offset']}" in out["note"]
    assert "narrow it" in out["note"] and "cut to 300" in out["note"]


def test_fit_hits_says_more_match_when_all_given_fit():
    out = _retrieval.fit_hits([{"id": 1}], BUDGET, more=True, total=7)
    assert out["shown"] == 1 and out["left_out"] == 0
    assert out["next_offset"] == 1 and out["total_hits"] == 7


def test_fit_record_cuts_the_longest_field_only():
    rec = {"caption": "x " * 20000, "title": "keep"}
    out, cut = _retrieval.fit_record(rec, 5000)
    assert _size(out) <= 5000 and out["title"] == "keep"
    assert cut == {"caption": 40000} and out["caption"].endswith("...")


# ---------------------------------------------------------------------------
# list_chapters
# ---------------------------------------------------------------------------

def test_list_chapters_default_shape_is_unchanged():
    chapters = _retrieval.list_chapters("gec_12")
    assert chapters and all("sections" in c for c in chapters)
    assert all(c["n_sections"] == len(c["sections"]) for c in chapters)


@pytest.mark.parametrize("ref", _references())
def test_every_listing_fits(ref):
    compact = _retrieval.list_chapters(ref, sections=False)
    assert _size(compact) <= BUDGET
    assert all("sections" not in c and c["n_sections"] >= 0 for c in compact)
    full = _retrieval.list_chapters(ref)
    assert [c["n_sections"] for c in compact] \
        == [len(c["sections"]) for c in full]
    for c in compact:
        one = _retrieval.list_chapters(ref, chapter=c["chapter"],
                                       max_chars=BUDGET)
        assert _size(one) <= BUDGET
        assert {o["chapter"] for o in one} == {c["chapter"]}


def test_list_chapters_names_the_chapters_a_missing_one_is_not():
    with pytest.raises(KeyError) as e:
        _retrieval.list_chapters("gec_12", chapter=99)
    assert "1, 2, 3" in str(e.value)


def test_a_chapter_too_long_to_list_lists_its_top_level_sections():
    one = _retrieval.list_chapters("gec_12", chapter=7, max_chars=3000)[0]
    assert one["n_sections"] > len(one["sections"])
    assert all("n_subsections" in s for s in one["sections"])
    assert "top-level" in one["note"]


# ---------------------------------------------------------------------------
# load_chapter
# ---------------------------------------------------------------------------

def test_load_chapter_too_long_is_its_outline():
    whole = _retrieval.load_chapter("gec_12", 7)
    assert _size(whole) > BUDGET          # the default is unchanged
    out = _retrieval.load_chapter("gec_12", 7, max_chars=BUDGET)
    assert _size(out) <= BUDGET
    assert out["chapter_chars"] == _size(whole)
    assert "retrieve_section" in out["note"]
    assert "7.2.1.3.1" in [s["section_id"] for s in out["sections"]]
    assert all("body" not in s for s in out["sections"])


def test_load_chapter_that_fits_is_whole():
    small = _retrieval.load_chapter("gec_14", 1)
    assert _retrieval.load_chapter("gec_14", 1, max_chars=10**7) == small


@pytest.mark.parametrize("ref", _references())
def test_every_chapter_load_fits(ref):
    for c in _retrieval.list_chapters(ref, sections=False):
        try:
            out = _retrieval.load_chapter(ref, c["chapter"], max_chars=BUDGET)
        except FileNotFoundError:     # a prologue or appendix file
            continue
        assert _size(out) <= BUDGET, (ref, c["chapter"])


# ---------------------------------------------------------------------------
# search_sections
# ---------------------------------------------------------------------------

def test_search_sections_default_shape_is_unchanged():
    hits = _retrieval.search_sections("gec_12", "Nordlund")
    assert isinstance(hits, list) and "body" in hits[0]
    assert _retrieval.search_sections("gec_12", "Nordlund", limit=2) \
        == hits[:2]


def test_search_sections_with_a_limit_is_hits_with_snippets():
    out = _retrieval.search_sections("gec_12", "pile", max_chars=BUDGET)
    assert _size(out) <= BUDGET
    assert out["total_hits"] > out["shown"] > 0
    hit = out["hits"][0]
    assert set(hit) == {"section_id", "title", "chapter", "chapter_title",
                        "parent_id", "under", "snippet"}
    assert len(hit["snippet"]) <= _retrieval.HIT_TEXT_CHARS
    assert "offset=" in out["note"]


def test_search_sections_pages_follow_the_ranking():
    ranked = [h["section_id"]
              for h in _retrieval.search_sections("gec_12", "pile")]
    first = _retrieval.search_sections("gec_12", "pile", limit=5,
                                       max_chars=BUDGET)
    second = _retrieval.search_sections("gec_12", "pile", limit=5,
                                        offset=first["next_offset"],
                                        max_chars=BUDGET)
    assert [h["section_id"] for h in first["hits"] + second["hits"]] \
        == ranked[:10]


def test_a_snippet_starts_near_the_words():
    out = _retrieval.search_sections("gec_12", "Nordlund", limit=1,
                                     max_chars=BUDGET)
    assert "nordlund" in out["hits"][0]["snippet"].lower()


@pytest.mark.parametrize("ref", _references())
def test_the_broadest_search_fits(ref):
    for q in ("a", "the"):
        out = _retrieval.search_sections(ref, q, max_chars=BUDGET)
        assert _size(out) <= BUDGET
        out = _retrieval.search_sections(ref, q, limit=50, offset=10,
                                         max_chars=BUDGET)
        assert _size(out) <= BUDGET


# ---------------------------------------------------------------------------
# retrieve_section: a missing number
# ---------------------------------------------------------------------------

def test_a_missing_number_names_what_is_near_it_in_plain_retrieval():
    with pytest.raises(KeyError) as e:
        _retrieval.retrieve_section("gec_12", "7.2.1.3")
    msg = str(e.value)
    assert "nearest section above it: 7.2.1 " in msg
    assert "7.2.1.3.1 Nordlund" in msg
    with pytest.raises(KeyError) as e:
        _retrieval_db.reference_get("gec_12", "7.2.1.3")
    assert msg.split("not found in reference 'gec_12'")[1] \
        == str(e.value).split("not found in reference 'gec_12'")[1]


def test_a_missing_number_with_nothing_near_it_says_so_plainly():
    with pytest.raises(KeyError) as e:
        _retrieval.retrieve_section("gec_12", "99.9")
    assert "nearest" not in str(e.value)


# ---------------------------------------------------------------------------
# reference_search, reference_query
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("q", ["the", "shall", "pile capacity", "of"])
def test_reference_search_at_fifty_fits(q):
    plain = _retrieval_db.reference_search(q, limit=50)
    assert _size(plain) > BUDGET          # what the app cut before REF-26
    out = _retrieval_db.reference_search(q, limit=50, max_chars=BUDGET)
    assert _size(out) <= BUDGET
    assert [h["section_id"] for h in out["hits"]] \
        == [h["section_id"] for h in plain[:out["shown"]]]
    assert out["next_offset"] == out["shown"]


def test_reference_search_pages_follow_the_ranking():
    plain = _retrieval_db.reference_search("settlement", limit=10)
    a = _retrieval_db.reference_search("settlement", limit=5, max_chars=BUDGET)
    b = _retrieval_db.reference_search("settlement", limit=5, offset=5,
                                       max_chars=BUDGET)
    key = lambda h: (h["reference"], h["section_id"])      # noqa: E731
    assert [key(h) for h in a["hits"] + b["hits"]] == [key(h) for h in plain]


def test_reference_search_never_offers_a_page_past_its_deepest():
    deepest = _retrieval_db._MAX_OFFSET
    out = _retrieval_db.reference_search("the", limit=5, offset=deepest - 10,
                                         max_chars=BUDGET)
    assert out["next_offset"] == deepest - 5
    out = _retrieval_db.reference_search("the", limit=10, offset=deepest - 5,
                                         max_chars=BUDGET)
    assert out["shown"] == 10 and "next_offset" not in out
    assert f"no deeper than offset={deepest}" in out["note"]
    # past it: an error saying so, never the same page again
    out = _retrieval_db.reference_search("the", limit=5, offset=deepest + 24,
                                         max_chars=BUDGET)
    assert set(out) == {"error"} and "past the deepest page" in out["error"]
    plain = _retrieval_db.reference_search("the", offset=deepest + 24)
    assert "past the deepest page" in plain[0]["error"]


def test_figure_search_never_offers_a_page_past_its_deepest():
    deepest = _figures_db._MAX_OFFSET
    out = _figures_db.figure_search("the", limit=10, offset=deepest - 5,
                                    max_chars=BUDGET)
    assert out["shown"] == 10 and "next_offset" not in out
    assert f"no deeper than offset={deepest}" in out["note"]
    out = _figures_db.figure_search("pile", offset=deepest + 1,
                                    max_chars=BUDGET)
    assert set(out) == {"error"} and "past the deepest page" in out["error"]


def test_reference_search_error_is_a_dict_with_a_limit():
    out = _retrieval_db.reference_search('"unterminated', max_chars=BUDGET)
    assert isinstance(out, dict)


@pytest.mark.parametrize("sql", [
    "SELECT * FROM sections",
    "SELECT body FROM sections ORDER BY length(body) DESC",
])
def test_reference_query_keeps_whole_rows_that_fit(sql):
    out = _retrieval_db.reference_query(sql, max_chars=BUDGET)
    assert _size(out) <= BUDGET
    assert 1 <= out["shown"] < 50 and out["left_out"] == 50 - out["shown"]
    assert "OFFSET" in out["note"]
    assert _retrieval_db.reference_query(sql)[:out["shown"]] == out["rows"]


def test_reference_query_cuts_a_row_that_alone_does_not_fit():
    out = _retrieval_db.reference_query(
        "SELECT section_id, body FROM sections ORDER BY length(body) DESC",
        max_chars=3000)
    assert _size(out) <= 3000 and out["shown"] == 1
    assert "body (from" in out["note"]


def test_reference_query_row_too_wide_to_cut_is_an_error():
    # 80 columns of 250 characters: cut to 200 each it is still too long
    sql = ("SELECT " + ", ".join(f"substr(body, 1, 250) AS c{i}"
                                 for i in range(80))
           + " FROM sections WHERE length(body) > 300")
    out = _retrieval_db.reference_query(sql, max_chars=BUDGET)
    assert set(out) == {"error"} and "fewer columns" in out["error"]


def test_reference_query_next_rows_raise_the_offset():
    out = _retrieval_db.reference_query(
        "SELECT * FROM sections LIMIT 50 OFFSET 100", max_chars=BUDGET)
    assert f"raise its OFFSET by {out['shown']}" in out["note"]


def test_reference_query_refusal_is_a_dict_with_a_limit():
    assert _retrieval_db.reference_query("DELETE FROM sections",
                                         max_chars=BUDGET) \
        == {"error": "only SELECT (or WITH ... SELECT) statements allowed"}


# ---------------------------------------------------------------------------
# figure_search, figure_get
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("q", ["pile capacity", "pressure", "chart"])
def test_figure_search_at_fifty_fits(q):
    out = _figures_db.figure_search(q, limit=50, max_chars=BUDGET)
    assert _size(out) <= BUDGET
    plain = _figures_db.figure_search(q, limit=50)
    assert [h["figure_number"] for h in out["hits"]] \
        == [h["figure_number"] for h in plain[:out["shown"]]]


def test_figure_get_cuts_a_caption_that_ran_on(monkeypatch):
    # The catalog's run-on captions are fixed (REF-27), so the row is made
    # long here: the shaping must still cut a caption that runs on.
    real = _figures_db._row_to_full

    def long_row(row):
        out = real(row)
        if out["figure_number"] == "1-3" and out["reference"] == "gec_13":
            out["caption"] += " page text that ran on" * 1500
        return out

    monkeypatch.setattr(_figures_db, "_row_to_full", long_row)
    whole = _figures_db.figure_get("gec_13", "1-3")
    assert _size(whole) > BUDGET          # a catalog caption that ran on
    out = _figures_db.figure_get("gec_13", "1-3", max_chars=BUDGET)
    assert _size(out) <= BUDGET
    assert "caption (from" in out["note"]
    assert out["pdf_page_index"] == whole["pdf_page_index"]
    small = _figures_db.figure_get("dm7_2", "4-12")
    assert _figures_db.figure_get("dm7_2", "4-12", max_chars=BUDGET) == small
