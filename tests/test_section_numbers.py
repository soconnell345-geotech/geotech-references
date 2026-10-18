"""Chapter JSON section numbers agree with the printed manuals (REF-23).

``scripts/check_section_numbers.py`` compares every chapter file's section
numbers and titles with the numbered headings of the source PDF in ``docs/``.
The per-reference tests need those PDFs. They are committed with the
repository, so the tests run wherever it is checked out with its docs
(including CI); a reference whose PDF is absent is skipped. The unit tests
at the bottom run everywhere.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "check_section_numbers", ROOT / "scripts" / "check_section_numbers.py")
csn = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = csn
_spec.loader.exec_module(csn)


def _refs_with_pdfs():
    return [r for r in csn.all_refs() if r not in csn.SKIP and csn.ref_pdfs(r)]


# ---------------------------------------------------------------------------
# against the printed manuals (local only)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ref", _refs_with_pdfs() or ["(no PDFs in docs/)"])
def test_no_definite_renumbering_left(ref):
    """Every section the checker can place with certainty carries the printed
    number. Sections it cannot place are listed by ``--detail``, not failed."""
    if ref not in csn.all_refs():
        pytest.skip("no source PDFs in docs/")
    pytest.importorskip("fitz")
    result = csn.compare_reference(ref)
    fixes = [f"{ch['file']}: {r['sid']} -> {r['new']} ({r['title']})"
             for ch in result["chapters"] for r in ch["rows"] if r.get("fix")]
    assert not fixes, "renumber from the print (check_section_numbers.py --apply):\n" + \
        "\n".join(fixes)


def test_gec12_chapter7_static_methods_follow_the_print():
    """The filed defect: GEC-12 7.2.1.3 holds the static methods for soil."""
    data = json.loads((csn.PKG / "gec_12" / "text" / "chapter07.json").read_text(
        encoding="utf-8"))
    ids = {}

    def walk(secs):
        for s in secs or []:
            ids[s["section_id"]] = s["title"]
            walk(s.get("subsections"))

    walk(data["sections"])
    assert ids["7.2.1.3.1"].startswith("Nordlund")
    assert ids["7.2.1.3.2"].startswith("Alpha")
    assert ids["7.2.1.3.4"].startswith("Beta")
    assert "Rock" in ids["7.2.1.4"]
    assert "7.2.1.1" not in ids and "7.2.1.6" not in ids


# ---------------------------------------------------------------------------
# unit tests (no PDFs needed)
# ---------------------------------------------------------------------------

def test_title_grades():
    m = csn.TitleMatcher([
        "Nordlund Method - Cohesionless Soils", "α-Method - Cohesive Soils",
        "Effective Stress β-Method - Mixed Soil Profiles", "Summary",
        "Pile Groups in Cohesionless Soils", "Pile Groups in Cohesive Soils",
    ])
    assert m.score("Nordlund Method (Cohesionless Soils)",
                   "Nordlund Method - Cohesionless Soils")[1] == "strong"
    assert m.score("Beta Method (Effective Stress)",
                   "Effective Stress β-Method - Mixed Soil Profiles")[1] == "strong"
    # one word apart, opposite meaning: never strong
    assert m.score("Pile Groups in Cohesive Soils",
                   "Pile Groups in Cohesionless Soils")[1] != "strong"


def test_numbers_and_levels():
    assert csn.num_key("7.2.1.3.1") < csn.num_key("7.2.1.4")
    assert csn.num_key("4-2.1") < csn.num_key("4-10")
    assert csn.level("3.0") == csn.level("3") == 1
    assert csn.level("3.1") == 2
    assert csn.is_range("7.2.1.3.4-7.2.1.3.7", "dotted") == ("7.2.1.3.4", "7.2.1.3.7")
    assert csn.is_range("4-2.1", "ufc") is None


def _row(sid, status, target=None, parent=None, title=""):
    return {"sid": sid, "title": title or sid, "status": status, "target": target,
            "target_title": None, "evidence": "", "parent": parent}


def test_decide_fixes_moves_a_dropped_level_and_names_the_group():
    rows = [
        _row("7.2.1", "matched"),
        _row("7.2.1.1", "missing_level", "7.2.1.3.1", "7.2.1"),
        _row("7.2.1.4", "title_differs", None, "7.2.1", "Effective Stress Methods"),
        _row("7.2.1.4.1", "misnumbered", "7.2.1.3.4", "7.2.1.4"),
        _row("7.2.1.4.2", "misnumbered", "7.2.1.3.5", "7.2.1.4"),
        _row("7.2.1.5", "misnumbered", "7.2.1.4", "7.2.1"),
    ]
    csn._decide_fixes(rows, set(), {})
    new = {r["sid"]: r.get("new") for r in rows if r["fix"]}
    assert new == {"7.2.1.1": "7.2.1.3.1", "7.2.1.4": "7.2.1.3.4-7.2.1.3.5",
                   "7.2.1.4.1": "7.2.1.3.4", "7.2.1.4.2": "7.2.1.3.5",
                   "7.2.1.5": "7.2.1.4"}


def test_decide_fixes_holds_what_needs_a_guess():
    rows = [
        _row("3.4", "title_differs"),                 # keeps 3.4
        _row("3.5", "misnumbered", "3.4"),            # 3.4 is taken
        _row("5.1", "misnumbered", "5.3"),            # two claim 5.3
        _row("5.2", "misnumbered", "5.3"),
        _row("6.1", "misnumbered", "6.4"),            # the print is ambiguous
        _row("7.1", "matched"),
        _row("7.1.2", "misnumbered", "7.2.1.2", "7.1"),  # would leave its parent
    ]
    csn._decide_fixes(rows, {"6.4"}, {})
    assert not any(r["fix"] for r in rows)
    holds = {r["sid"]: r["hold"] for r in rows if r.get("hold")}
    assert "held by" in holds["3.5"]
    assert "claims the same" in holds["5.1"]
    assert "two ways" in holds["6.1"]
    assert "under section 7.1" in holds["7.1.2"]


def test_rewrite_ids_changes_only_the_ids(tmp_path):
    src = ('{\r\n  "sections": [\r\n    {\r\n      "section_id": "7.2.1.1",\r\n'
           '      "title": "Nordlund",\r\n      "body": "see 7.2.1.1"\r\n    }\r\n  ]\r\n}\r\n')
    p = tmp_path / "chapter07.json"
    p.write_bytes(src.encode("utf-8"))
    csn.rewrite_ids(p, {"7.2.1.1": "7.2.1.3.1"})
    out = p.read_bytes().decode("utf-8")
    assert out == src.replace('"section_id": "7.2.1.1"', '"section_id": "7.2.1.3.1"')
    assert "see 7.2.1.1" in out and out.count("\r\n") == src.count("\r\n")
    with pytest.raises(SystemExit):
        csn.rewrite_ids(p, {"9.9": "9.10"})
