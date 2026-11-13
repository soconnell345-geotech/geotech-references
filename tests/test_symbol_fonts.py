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
    ("fhwa_soils_foundations", "9.15.7.2", "immediately after, 2½ minutes after, and 5 minutes",
     "after, 22 minutes"),
    # NHI-06-089 PDF p. 277, printed p. 9-167
    ("fhwa_soils_foundations", "9.15.7.4", "an angle of about 20° from the load axis", "about 20E"),
    # NHI-06-088 PDF p. 251, printed p. 5-1
    ("fhwa_soils_foundations", "5.0", "the project’s issues", "project=s"),
    # --- signs the page completes with a drawn stroke, raised exponents and
    # degree signs (manifest "text_fixes" and "raised_o_degree"):
    # NHI-06-088 PDF p. 257, printed p. 5-7, Table 5-2 (turned): "+" with a
    # stroke drawn under it, and a degree sign the text layer gives as "o"
    ("fhwa_soils_foundations", "5.2", "Dry soil in oven at 100 ± 5 °C", "100 + 5 oC"),
    # PDF p. 259, printed p. 5-9: "<" with a stroke under it, 10 raised to -5
    ("fhwa_soils_foundations", "5.2", "(k ≤ 1x10^-5 cm/s)", "(k < 1x10-5"),
    # PDF p. 312, printed p. 5-62: ">" with a stroke under it
    ("fhwa_soils_foundations", "5.6.4", "(k ≥ 10^-3 cm/sec)", "(k > 10-3"),
    ("fhwa_soils_foundations", "5.6.4", "valid only for k ≥ 10^-3 cm/sec", "k > 10-3"),
    # PDF p. 309, printed p. 5-59
    ("fhwa_soils_foundations", "5.6.2", "k ≤ 2 x 10^-5 ft/min (1 x 10^-6 cm/s)", "2 x 10-5 ft/min"),
    # PDF p. 311, printed p. 5-61, Table 5-9
    ("fhwa_soils_foundations", "5.6.3", "1 x 10^-6 to 1 x 10^-7 20 less than 1 x 10^-7 30",
     "less than 1 x 10-7"),
    # PDF p. 313, printed p. 5-63, Table 5-10
    ("fhwa_soils_foundations", "5.6.4", "Portland cement concrete less than 10^-8", "less than 10-8"),
    # PDF p. 344, printed p. 5-94, Table 5-21
    ("fhwa_soils_foundations", "5.12", "Elastic Modulus, Ei (psi ×10^6)", "(psi ×106)"),
    # PDF p. 61, printed p. 2-5; PDF p. 367, printed p. 6-17 (raised "o")
    ("fhwa_soils_foundations", "2.1.2", "between 220 and 230°F (105 and 110°C)", "230oF"),
    ("fhwa_soils_foundations", "6.4.3", "(12,000 lbs) (cos 20°) = 11,276 lbs", "(cos 20o)"),
    # NHI-06-089 PDF p. 343, printed p. 10-53
    ("fhwa_soils_foundations", "10.6", "cos 10°", "cos 10o"),
    # --- hand-kept references: a sign the page completes with a stroke drawn
    # under it, stored as the bare sign; a raised exponent or degree sign
    # stored as plain characters:
    # FHWA-NHI-18-024 PDF pp. 287-288, printed pp. 10-7, 10-8
    ("gec_10", "10.3.4", "common socket diameter B ≤ 5 ft", "B < 5 ft"),
    ("gec_10", "10.3.4", "(e.g., qu ≥ 10,000 psi)", "qu > 10,000"),
    # FHWA-NHI-18-024 PDF p. 368, printed p. 12-6: "clear spacing (≥ 5 inches)"
    ("gec_10", "12.3.2", "with clear spacing ≥ 5 inches", "over 5 inches"),
    # FHWA-NHI-16-028 PDF pp. 430-431, printed pp. 9-122, 9-123
    ("gec_13", "9.8.3.2.1", "for Cu ≤ 3 use", "Cu < 3"),
    ("gec_13", "9.8.3.2.1", "nonwoven porosity ≥ 50%", "porosity > 50%"),
    ("gec_13", "9.8.3.2.1", "woven percent open area ≥ 4%", "area > 4%"),
    ("gec_13", "9.8.3.2.1", "(Class 1, < 50% / ≥ 50% elongation)", "/ > 50%"),
    # FHWA-IF-99-015 PDF p. 76, printed p. 55
    ("gec_4", "5.2.5", "stiff to hard fissured clays (Ns ≤ 4)", "fissured clays (Ns < 4)"),
    # FHWA-NHI-16-027 PDF pp. 182, 184, printed pp. 3-32, 3-34
    ("gec_13", "3.4.2.2", "permeability 1 x 10^-5 m/s", "1 x 10-5"),
    ("gec_13", "3.4.2.2", "k 1 x 10^-6 to 1 x 10^-9 m/s", "1 x 10-9"),
    # FHWA-NHI-16-028 PDF p. 176, printed p. 8-30; p. 201, printed p. 8-55
    ("gec_13", "8.2.3.2.1", "'0.04 ≤ k ≤ 4 × 10^-4'", "<= k <="),
    ("gec_13", "8.2.5.6.2", "Bitumen pumps easily above 400°F", "400 F"),
    # UFS 3-220-10 PDF p. 71, printed p. 43; p. 197, printed p. 169; p. 324,
    # printed p. 296 (the page prints "less 10-8", no "than")
    ("dm7_1", "1-5.3.2", "finer than 0.02 mm (8x10^-4 inches)", "8x10-4"),
    ("dm7_1", "3-2.7.1", "conductivity less than 10^-3 cm/sec", "10-3 cm"),
    ("dm7_1", "3-2.7.2", "conductivity less than 10^-4 cm/sec", "10-4 cm"),
    ("dm7_1", "6-3", "range from less 10^-8 cm/sec", "10-8 cm"),
    # FHWA-HIF-18-031 PDF p. 236, printed p. 232 (Eq. A-43's coefficients)
    ("gec_9", "A.6", "A = 3 (10^-7) (z + 1)^6.05; B = 2.80 (z + 1)^0.11; and C = 2.85 (z + 1)^-0.41",
     "(10-7) (z + 1)6.05"),
    # UFC 3-250-03 PDF p. 137, printed p. 123
    ("ufc_flexible_practice", "9-1.1", "8 microns (3.15x10^-4 inch)", "3.15x10-4"),
    # FHWA-NHI-05-037 PDF p. 78, printed p. 3-24: "+" with a stroke drawn
    # under it (manifest text_fixes)
    ("fhwa_pavements", "3.5.2.a", "cost index varying by about ±20% over", "about +20%"),
    # UFC 3-220-20 PDF p. 65, printed p. 27; PDF p. 206, printed p. 168
    ("dm7_2", "1-2.11", "Peats have a high permeability (10^-3 cm/sec)", "(10-3 cm"),
    ("dm7_2", "3-7.4", "ranges from 3×10^-6 to 5×10^-5 1/psf", "3×10-6"),
    # UFC 3-220-20 PDF p. 694, printed p. 656, Table B-39: the page prints
    # "2.4 x 10-6" with the -6 on the line; the value is 2.4 x 10^-6
    ("dm7_2", "B-7.4", "/ 2.4 x 10^-6 (the page prints the -6 on the line, not raised) / 0%",
     "2.4 x 10-6 /"),
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


#: A power of ten whose exponent the page prints raised, stored as plain
#: digits ("1 x 10-8 cm/sec" for 1 x 10^-8, "psi ×106" for psi ×10^6): the
#: text layer gives a raised exponent as ordinary characters, and the stored
#: number reads a thousand or a million times off. These forms are not a
#: range or a figure number; the library writes an exponent with "^".
_PLAIN_POWER = [
    re.compile(r"(?<![\w^.,])\d+(?:[.,]\d+)?\s?[x×]\s?10[-−–]\d{1,2}(?![\d^.,])"),
    re.compile(r"(?:than|≈|<|>|≤|≥)\s?10[-−–]\d{1,2}\s?(?:cm|mm|m|in|ft)(?!\w)"),
    re.compile(r"(?<![\w.^\-–−])10[-−–]\d{1,2}\s?(?:cm|mm|m|in|ft)/(?:s|sec)\b"),
    re.compile(r"\(10[-−–]\d\)"),
    re.compile(r"×10\d(?![\d^])"),
]

#: Plain powers of ten left in stored text on purpose: none (UFC 3-220-20's
#: three were corrected 2026-11-12).
KNOWN_PLAIN_POWERS = {}


def test_no_power_of_ten_stored_as_plain_digits():
    found = {}
    for pkg_dir in sorted(p for p in PKGS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        for fname, path, s in _strings(pkg_dir):
            n = sum(len(rx.findall(s)) for rx in _PLAIN_POWER)
            if n:
                found[(pkg_dir.name, fname, path)] = n
    assert found == KNOWN_PLAIN_POWERS


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


#: Font-name prefixes of the text faces in FHWA NHI-06-088/089; every other
#: font is a symbol font (LucidaConsole, LucidaSansUnicode, Courier and Tahoma
#: set only spaces there).
_SOILS_TEXT_FONTS = ("TimesNewRoman", "Arial", "CourierNew", "BookAntiqua", "Verdana", "ComicSansMS",
                     "LucidaConsole", "LucidaSansUnicode", "Courier", "Tahoma")


def test_every_soils_symbol_font_glyph_is_read_off_the_page():
    # each character a symbol font sets in either soils volume is in the
    # manifest's "symbol_fonts" (mapped in the build) or "symbol_fonts_checked"
    # (the text layer already gives the printed glyph: SymbolMT's Greek, signs
    # and the pieces of tall brackets in equation objects), every pair looked at
    # on a 300 dpi crop; a glyph in neither, or a private-use character in any
    # font, fails here
    fitz = pytest.importorskip("fitz")
    m = json.loads((MANIFESTS / "fhwa_soils_foundations.json").read_text(encoding="utf-8"))
    n = 0
    for vol in m["volumes"]:
        pdf = (MANIFESTS / vol["pdf_path"]).resolve()
        if not pdf.exists():
            pytest.skip("PDF not checked out")
        known = {}
        for key in ("symbol_fonts", "symbol_fonts_checked"):
            for f, cm in vol.get(key, {}).items():
                known.setdefault(f, set()).update(cm)
        unread = set()
        with fitz.open(str(pdf)) as doc:
            for page in doc:
                for b in page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]:
                    for ln in b["lines"]:
                        for s in ln["spans"]:
                            symbol = not s["font"].startswith(_SOILS_TEXT_FONTS)
                            for c in s["text"]:
                                if c != " " and (symbol or 0xE000 <= ord(c) <= 0xF8FF):
                                    n += 1
                                    if c not in known.get(s["font"], ()):
                                        unread.add((s["font"], c))
        assert not unread, (pdf.name, sorted(unread))
    assert n > 1000


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
