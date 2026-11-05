"""agents/references_agent.py: its catalog is the package's (DOC-09).

The catalog was a hand-kept dict of 12 references that had drifted from the
package (GEC-10 cited by the 2010 edition, GEC-11 and UFC 3-250-01 marked
as having no text, UFC 3-250-01 under a title its cover does not print). It
is now read from the installed package; these tests hold it there.
"""

import importlib
import json
import pkgutil
from pathlib import Path

import pytest

import geotech_references
from agents import references_agent as agent

PKG = Path(geotech_references.__file__).parent


def _references():
    return sorted(m.name for m in pkgutil.iter_modules(geotech_references.__path__)
                  if m.ispkg and not m.name.startswith("_"))


def test_catalog_lists_every_reference_in_the_package():
    assert sorted(agent._REFERENCE_CATALOG) == _references()


@pytest.mark.parametrize("ref", _references())
def test_entry_matches_the_package(ref):
    cfg = agent._REFERENCE_CATALOG[ref]
    pkg = importlib.import_module(f"geotech_references.{ref}")
    modules = sorted(m.name for m in pkgutil.iter_modules(pkg.__path__)
                     if not m.ispkg and not m.name.startswith("_"))
    assert cfg["submodules"] == modules
    assert cfg["has_text"] == any((PKG / ref / "text").glob("*.json"))
    assert cfg["citation"]
    registry, _ = agent._load_reference(ref)
    assert registry, f"{ref}: nothing registered"
    if cfg["has_text"]:
        out = json.loads(agent.lookup_reference(ref, "list_chapters", "{}"))
        assert not (isinstance(out, dict) and "error" in out), out


def test_citations_follow_the_chapter_files():
    cat = agent._REFERENCE_CATALOG
    assert cat["ufc_pavement"]["citation"] == (
        "UFC 3-250-01 — Pavement Design for Roads and Parking Areas")
    assert cat["gec_10"]["citation"].startswith("FHWA-NHI-18-024 — ")
    assert cat["dm7_1"]["citation"].startswith("UFS 3-220-10 — ")
    # no text: the package docstring's first line
    assert cat["ufc_backfill"]["citation"].startswith("UFC 3-220-04N")


def test_empty_reference_lists_the_catalog():
    out = json.loads(agent.list_reference_methods(""))
    assert sorted(out) == _references()
