"""Signs set in symbol fonts are stored as the page prints them.

Several source PDFs set their signs in symbol fonts (WordPerfect's WP MathA,
WP Greek Century and WP Typographic Symbols, Wingdings, Symbol, and the
one-page TrueType subsets of FHWA-IF-99-015 named TT...o00), and a PDF's
text layer can give such a glyph as an ordinary character: FHWA NHI-06-088
prints "with ≤ 12 percent fines" and its text layer gives "with # 12 percent
fines"; "40 ± 20" comes out "40"20"; NHI-06-089's "ω = 0°" comes out
"T = 0E"; FHWA-IF-99-015's "(OCR ≤ 4)" comes out "(OCR@4)". Chapter text
read off a text layer kept those characters.

Each reference's manifest (``scripts/manifests/<package>.json``, per volume
where it has volumes) carries ``symbol_fonts``: {font name: {text-layer
character: printed glyph}}, every pair read off a 300 dpi render of the page
(2026-11-12 symbol-font review). A reference built by
``scripts/build_printed_text.py`` applies it in the build, so a rebuild keeps
the printed signs; a hand-kept reference's text was corrected where it held
the text-layer character.

1. The printed sign is stored at a sample of the corrected places (every
   comparison sign and ten others, and three figure captions), with the PDF
   and printed page.
2. Scans that need no PDF: no stored text holds a private-use character
   (U+E000 to U+F8FF), the replacement character, a control character, or a
   Malayalam, Sinhala or Ethiopic letter (a Cambria Math bracket piece the
   text layer names wrongly), and none holds three of the same mathematical
   letter in a row (FHWA-NHI-16-009 Vol III's list of figures gave "ϕdyn" as
   eight copies of U+1D719).
3. With the PDFs present: on every page that uses a font of a reference's
   ``symbol_fonts``, no span's passage (the words either side of it on the
   page) is stored with the text-layer character where the page prints
   another glyph.
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKGS = ROOT / "geotech_references"
MANIFESTS = ROOT / "scripts" / "manifests"

#: (package, section id, printed text now stored, text-layer form it replaced);
#: the comment gives the PDF page (1-based) and the printed page.
PRINTED = [
    # FHWA NHI-06-088 PDF p. 207, printed p. 4-7 (comparison signs)
    ("fhwa_soils_foundations", "4.1.4.1", "with ≤12 percent fines", "with #12 percent"),
    ("fhwa_soils_foundations", "4.1.4.1", "with ≤ 12 percent fines", "with # 12 percent"),
    # NHI-06-088 PDF p. 283, printed p. 5-33: Cc ≈ 0.5 Gs (PI/100)
    ("fhwa_soils_foundations", "5.4.6.1", "Cc≈0.5Gs(PI/100)", "Cc.0.5Gs"),
    # NHI-06-088 PDF p. 286, printed p. 5-36 (table: Boston Blue Clay)
    ("fhwa_soils_foundations", "5.4.6.3", "40±20 12±6 135±70", '40"20'),
    # NHI-06-088 PDF p. 332, printed p. 5-82 (table of test results)
    ("fhwa_soils_foundations", "5.8.4", "SW 119±5 (18.7±0.8) 13.3±2.5", 'SW 119"5'),
    ("fhwa_soils_foundations", "5.8.4", "0.50±0.03", '0.50"0.03'),
    # NHI-06-088 PDF p. 180, printed p. 3-76
    ("fhwa_soils_foundations", "3.11", "Volume Change ΔV", "Volume Change )V"),
    # NHI-06-089 PDF p. 89, printed p. 8-55
    ("fhwa_soils_foundations", "8.5.3", "change in pressure (Δp)", "pressure ()p)"),
    # NHI-06-089 PDF pp. 152-153, printed pp. 9-42, 9-43: Tables 9-6(a), 9-6(b)
    ("fhwa_soils_foundations", "9.5.1.1", "Kδ for piles when ω = 0° and V = 0.10 to 1.00",
     "when T = 0E"),
    ("fhwa_soils_foundations", "9.5.1.1", "Kδ for piles when ω = 0° and V = 1.0 to 10.0",
     "when T = 0E"),
    # NHI-06-089 PDF p. 275, printed p. 9-165
    ("fhwa_soils_foundations", "9.15.7.2", "time interval of 2½ minutes", "of 22 minutes"),
    # NHI-06-089 PDF p. 277, printed p. 9-167
    ("fhwa_soils_foundations", "9.15.7.4", "an angle of about 20° from the load axis", "about 20E"),
    # NHI-06-088 PDF p. 251, printed p. 5-1
    ("fhwa_soils_foundations", "5.0", "the project’s issues", "project=s"),
]

#: (package, figure number, printed caption text now stored, text-layer form
#: it replaced) for figure-catalog captions; the comment gives the PDF page.
CATALOG_PRINTED = [
    # FHWA-IF-99-015 PDF p. 112, printed p. 91 (font TT284o00 gives "A")
    ("gec_4", "44", "Chart for estimating β coefficient", "estimating A coefficient"),
    # FHWA-NHI-16-009 Vol III PDF p. 66 and p. 67: Cambria Math's phi with a
    # subscript came out as eight or ten copies of U+1D719
    ("gec_12", "D-11", "2% of the piles, φdyn=0.80", "\U0001d719\U0001d719"),
    ("gec_12", "D-14", "Nordlund Method static analysis, φstat=0.45", "\U0001d719\U0001d719"),
]

#: Characters stored before this review in a reference another branch is
#: rebuilding: (package, file, JSON path) -> count. GEC-11's catalog caption
#: of Figure 4-5 holds U+F071 and U+F0B0 (the Symbol font's θ and degree
#: sign, "wall batters, θ, greater than 100°"); GEC-11 was left to its
#: rebuild (2026-11-12), and the entry goes when that lands.
KNOWN_ODD = {
    ("gec_11", "figures_catalog.json", "figures/38/caption"): 2,
}


def _strings(pkg_dir: Path):
    """(file name, JSON path, string) for every string a reference stores."""
    files = sorted((pkg_dir / "text").glob("*.json"))
    files += [pkg_dir / n for n in ("figures_catalog.json", "tables_catalog.json")
              if (pkg_dir / n).exists()]

    def walk(obj, path):
        if isinstance(obj, str):
            yield path, obj
        elif isinstance(obj, dict):
            for k, v in obj.items():
                yield from walk(v, path + [str(k)])
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from walk(v, path + [str(i)])

    for f in files:
        for path, s in walk(json.loads(f.read_text(encoding="utf-8")), []):
            yield f.name, "/".join(path), s


def _sections(pkg: str) -> dict:
    out = {}
    for f in sorted((PKGS / pkg / "text").glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        stack = list(data["sections"])
        while stack:
            s = stack.pop()
            out.setdefault(s["section_id"], []).append(s)
            stack.extend(s.get("subsections") or [])
    return out


@pytest.mark.parametrize("pkg, sid, printed, raw", PRINTED,
                         ids=[f"{p}-{s}-{i}" for i, (p, s, _, _) in enumerate(PRINTED)])
def test_printed_sign_is_stored(pkg, sid, printed, raw):
    secs = _sections(pkg)[sid]
    text = json.dumps(secs, ensure_ascii=False)
    assert printed in text, (pkg, sid, printed)
    assert raw not in text, (pkg, sid, raw)


@pytest.mark.parametrize("pkg, fig, printed, raw", CATALOG_PRINTED,
                         ids=[f"{p}-{f}" for p, f, _, _ in CATALOG_PRINTED])
def test_printed_caption_is_stored(pkg, fig, printed, raw):
    data = json.loads((PKGS / pkg / "figures_catalog.json").read_text(encoding="utf-8"))
    caps = [f["caption"] for f in data["figures"] if f.get("figure_number") == fig]
    assert caps, (pkg, fig)
    assert any(printed in c for c in caps), (pkg, fig, printed)
    assert not any(raw in c for c in caps), (pkg, fig, raw)


#: three or more of the same mathematical letter in a row: a text layer that
#: gave one Cambria Math character for every glyph of a symbol and subscript
_MATH_RUN = re.compile("([\U0001d400-\U0001d7ff])\\1\\1")


def test_no_repeated_math_letter_stored():
    found = []
    for pkg_dir in sorted(p for p in PKGS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        for fname, path, s in _strings(pkg_dir):
            if _MATH_RUN.search(s):
                found.append((pkg_dir.name, fname, path))
    assert not found, found[:20]


_ODD = re.compile("[-�\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f"
                  "ഀ-෿ሀ-፿]")


def _odd(c: str) -> bool:
    return bool(_ODD.match(c))


def test_no_private_use_or_control_characters_stored():
    found = {}
    for pkg_dir in sorted(p for p in PKGS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        for fname, path, s in _strings(pkg_dir):
            n = len(_ODD.findall(s))
            if n:
                found[(pkg_dir.name, fname, path)] = n
    assert found == KNOWN_ODD


# ---------------------------------------------------------------------------
# 3. position check against the PDF
# ---------------------------------------------------------------------------

#: References whose stored text was checked span by span against the page.
CHECKED = ["fhwa_soils_foundations", "gec_4"]

_DASH = "-‐‑‒–—―−"
_SQ = "'‘’"
_DQ = '"“”'
_CTX = 10


def _char_pat(c: str) -> str:
    for group in (_DASH, _SQ, _DQ):
        if c in group:
            return "[" + re.escape(group) + "]"
    return re.escape(c)


def _symbol_volumes(pkg: str):
    """(PDF path, {font: {raw: glyph}}) for each volume, the pairs whose
    printed glyph differs from the text-layer character (a private-use or
    control character is left to the scan above, which needs no PDF)."""
    m = json.loads((MANIFESTS / f"{pkg}.json").read_text(encoding="utf-8"))
    for v in m.get("volumes") or [m]:
        fonts = {f: {c: g for c, g in cm.items() if c != g and not _odd(c)}
                 for f, cm in (v.get("symbol_fonts") or {}).items()}
        fonts = {f: cm for f, cm in fonts.items() if cm}
        if fonts:
            yield (MANIFESTS / v["pdf_path"]).resolve(), fonts


def _raw_passages(pdf: Path, fonts: dict):
    """(PDF page, line, regex) for each symbol-font character: the regex
    finds the passage stored with the text-layer character."""
    fitz = pytest.importorskip("fitz")
    names = {f.lower() for f in fonts}
    with fitz.open(str(pdf)) as doc:
        for pno in range(doc.page_count):
            page = doc[pno]
            used = {f[3].split("+", 1)[-1].lower() for f in page.get_fonts()}
            if not any(n in u or u in n for n in names for u in used if u):
                continue
            lines = []
            for b in page.get_text("dict")["blocks"]:
                for ln in b.get("lines", []):
                    items = []
                    for s in ln["spans"]:
                        cm = fonts.get(s["font"], {})
                        items.extend((c, (c, cm[c]) if c in cm else None) for c in s["text"])
                    lines.append(items)
            for li, items in enumerate(lines):
                for k, (c, sym) in enumerate(items):
                    if not sym:
                        continue
                    left = (lines[li - 1] if li else []) + [(" ", None)] + items[:k]
                    right = items[k + 1:] + [(" ", None)] + (lines[li + 1] if li + 1 < len(lines) else [])
                    left = [x for x in left if not x[0].isspace()][-_CTX:]
                    right = [x for x in right if not x[0].isspace()][:_CTX]
                    if len(left) + len(right) < 8:
                        continue

                    def pat(seq):
                        return "".join("(?:" + re.escape(y[0]) + "|" + re.escape(y[1]) + ")"
                                       if y else _char_pat(x) for x, y in seq)

                    yield (pno + 1, "".join(x for x, _ in items),
                           re.compile(pat(left) + re.escape(c) + pat(right)))
            page = None


@pytest.mark.parametrize("pkg", CHECKED)
def test_no_symbol_font_passage_stored_raw(pkg):
    vols = list(_symbol_volumes(pkg))
    assert vols, f"{pkg}: no symbol_fonts in its manifest"
    if not all(pdf.exists() for pdf, _ in vols):
        pytest.skip("PDF not checked out")
    stored = "\x00".join(re.sub(r"\s+", "", s) for _, _, s in _strings(PKGS / pkg))
    bad = []
    n = 0
    for pdf, fonts in vols:
        for page, line, rx in _raw_passages(pdf, fonts):
            n += 1
            if rx.search(stored):
                bad.append((pdf.name, page, line))
    assert n, f"{pkg}: no symbol-font characters found in the PDF"
    assert not bad, bad[:20]
