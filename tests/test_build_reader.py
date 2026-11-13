"""The PDF reader is an input of a script-built reference's build
(tests/_build_reader.py): each such manifest records its version, all
record the same one, the GitHub job that runs the rebuilds installs that
one, and a rebuild test under another reader skips, or fails where the
job requires the recorded reader."""

import json
import re
from pathlib import Path

import pytest

from tests import _build_reader

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
SCRIPT_BUILT = sorted(
    p.stem for p in (ROOT / "scripts" / "manifests").glob("*.json")
    if json.loads(p.read_text(encoding="utf-8")).get("text_build"))


def test_the_script_built_references():
    assert SCRIPT_BUILT == ["em_1905", "fhwa_pavements", "fhwa_soils_foundations", "gec_11"]


@pytest.mark.parametrize("manifest", SCRIPT_BUILT)
def test_each_records_the_reader_it_was_built_with(manifest):
    assert re.fullmatch(r"\d+(\.\d+)+", _build_reader.recorded_reader(manifest))


def test_one_reader_for_every_build_and_the_github_job_installs_it():
    readers = {_build_reader.recorded_reader(m) for m in SCRIPT_BUILT}
    assert len(readers) == 1
    pinned = re.findall(r"pymupdf==([\d.]+)", WORKFLOW.read_text(encoding="utf-8"))
    assert pinned == list(readers)


def test_a_different_reader_skips_or_fails(monkeypatch):
    want = _build_reader.recorded_reader("em_1905")
    monkeypatch.setattr(_build_reader, "installed_reader", lambda: "0.0.1")
    monkeypatch.delenv(_build_reader.REQUIRE_ENV, raising=False)
    with pytest.raises(pytest.skip.Exception, match=f"built with PyMuPDF {want}.*has "
                                                   r"PyMuPDF 0\.0\.1.*pymupdf=="):
        _build_reader.require_build_reader("em_1905")
    monkeypatch.setenv(_build_reader.REQUIRE_ENV, "1")
    with pytest.raises(pytest.fail.Exception, match="a different reader is a failure"):
        _build_reader.require_build_reader("em_1905")
    monkeypatch.setattr(_build_reader, "installed_reader", lambda: None)
    with pytest.raises(pytest.fail.Exception, match="no PyMuPDF"):
        _build_reader.require_build_reader("em_1905")
    monkeypatch.setattr(_build_reader, "installed_reader", lambda: want)
    assert _build_reader.require_build_reader("em_1905") is None
