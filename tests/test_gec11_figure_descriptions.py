"""GEC-11's figure descriptions come from the stored chapter text.

The catalog's ``description`` is what a figure search matches a concept
against and what a caller reads beside the caption. Until 2026-11-13 the
GEC-11 descriptions were the summaries of the earlier, paraphrased chapter
text, and four of them (Figures 9-4 to 9-7) gave Eq. 9-1 with a division by
FSR that the manual does not print (Vol II p. 9-9), which understates the
reinforcement tension. They are now rebuilt from the text read off the
print: the title and place of each section that cites the figure
(``scripts/build_figure_catalog.py``, ``_enrich_from_text``).
"""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_figure_catalog as builder  # noqa: E402

CATALOG = ROOT / "geotech_references" / "gec_11" / "figures_catalog.json"


def _figures():
    return json.loads(CATALOG.read_text(encoding="utf-8"))["figures"]


def test_descriptions_are_rebuilt_from_the_stored_text():
    committed = _figures()
    rebuilt = copy.deepcopy(committed)
    for f in rebuilt:
        f["description"] = ""
    builder._enrich_from_text("gec_11", rebuilt)
    differ = [f["figure_number"] for f, g in zip(committed, rebuilt)
              if f.get("description", "") != g["description"]]
    assert not differ, (
        "gec_11 figure descriptions that are not what the chapter text gives "
        f"(rerun the enrichment): {differ}")


def test_no_description_states_a_formula():
    """A description names where the figure is used; it never carries an
    equation, which belongs to the text and its page."""
    with_formula = [f["figure_number"] for f in _figures()
                    if "=" in f.get("description", "")
                    or re.search(r"\bEq\b", f.get("description", ""))]
    assert not with_formula, with_formula
