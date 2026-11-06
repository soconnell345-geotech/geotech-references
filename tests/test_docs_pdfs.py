"""Every committed docs/*.pdf is a PDF (REF-12).

docs/UFC_4-023-03_2024_c4.pdf was a 1.3 KB HTML page saved under a .pdf
name. This checks the file signature of every PDF git tracks under docs/,
and, where PyMuPDF is installed, that it opens with at least one page.
"""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _tracked_pdfs():
    try:
        out = subprocess.run(
            ["git", "ls-files", "docs"], cwd=ROOT, capture_output=True,
            text=True, check=True,
        ).stdout
        files = [ROOT / line for line in out.splitlines()
                 if line.lower().endswith(".pdf")]
    except (OSError, subprocess.CalledProcessError):
        files = sorted((ROOT / "docs").glob("*.pdf"))
    return [f for f in files if f.exists()]


PDFS = _tracked_pdfs()


def test_some_pdfs_found():
    if not (ROOT / "docs").is_dir():
        pytest.skip("no docs/ folder in this checkout")
    assert PDFS


@pytest.mark.parametrize("path", PDFS, ids=lambda p: p.name)
def test_docs_pdf_opens_as_pdf(path):
    with open(path, "rb") as fh:
        head = fh.read(1024)
    assert b"%PDF-" in head, f"{path.name} does not start as a PDF"
    fitz = pytest.importorskip("pymupdf")
    with fitz.open(path) as doc:
        assert doc.is_pdf
        assert doc.page_count >= 1
