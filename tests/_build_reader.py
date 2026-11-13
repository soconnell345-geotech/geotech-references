"""The PDF reader a script-built reference was built with.

A reference whose chapter text is read off its PDF by a script
(``scripts/build_printed_text.py``) depends on exactly what the PDF reader,
PyMuPDF, returns for each page, and two versions of the reader do not
return the same thing everywhere. So the reader's version is an input of
the build: each script-built reference's manifest records it
(``"built_with": {"pymupdf": "1.27.2.3"}``), and the test that rebuilds the
text and compares it with the committed files runs only under that version.

Under another version that test skips, with a reason naming both versions
and how to run it. With ``GEOTECH_REQUIRE_BUILD_READER=1`` (the GitHub job
that installs the recorded version) a different or missing reader is a
failure, so that job cannot pass by skipping. Every other test that reads
a PDF runs under any reader.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "scripts" / "manifests"
REQUIRE_ENV = "GEOTECH_REQUIRE_BUILD_READER"


def recorded_reader(manifest: str) -> str:
    """The PyMuPDF version a reference's manifest says it was built with."""
    data = json.loads((MANIFESTS / f"{manifest}.json").read_text(encoding="utf-8"))
    try:
        return data["built_with"]["pymupdf"]
    except (KeyError, TypeError):
        raise AssertionError(
            f"scripts/manifests/{manifest}.json records no reader: add "
            '"built_with": {"pymupdf": "<the version it was built with>"}') from None


def installed_reader() -> str | None:
    """The installed PyMuPDF's version, or None if there is none."""
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            return None
    return pymupdf.__version__


def require_build_reader(manifest: str) -> None:
    """Call first in a test that rebuilds a reference's text from its PDF
    and compares it with the committed files: it returns only when the
    installed PyMuPDF is the version the manifest records."""
    want, have = recorded_reader(manifest), installed_reader()
    if have == want:
        return
    reason = (f"{manifest} was built with PyMuPDF {want}, and this environment has "
              + (f"PyMuPDF {have}" if have else "no PyMuPDF")
              + f"; to run the rebuild, install that version (pip install pymupdf=={want})")
    if os.environ.get(REQUIRE_ENV) == "1":
        pytest.fail(f"{reason}. {REQUIRE_ENV}=1, so a different reader is a failure "
                    "here, not a skip")
    pytest.skip(reason)
