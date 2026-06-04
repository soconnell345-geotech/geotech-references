"""Build a figure catalog (figures_catalog.json) for a reference package.

For a reference whose manifest carries a ``pdf_path`` and chapter page ranges,
this script:

1. Parses the PDF's "LIST OF FIGURES" section into ``{figure_number, caption,
   printed_page}`` entries (the authoritative figure list with full captions).
2. Resolves each figure to its 0-based PDF page index by searching the document
   *body* for the page where ``Figure <num>`` is immediately followed by the
   figure's caption text (the caption only appears verbatim on the figure's own
   page; in-text references read "Figure X-Y shows ..."). Front matter is skipped
   using the first chapter's ``page_start`` from the manifest.
3. Backfills any figure the caption search misses, first via the median
   printed-to-PDF page offset, then by monotonic interpolation between resolved
   neighbours, so every figure gets a best-estimate page.
4. Writes ``geotech_references/<package>/figures_catalog.json``.

The catalog is the indexable artifact consumed by
``geotech_references._figures_db`` (FTS5 retrieval) and by the
``read_reference_figure`` vision tool, which renders the resolved page for
on-demand chart read-off. The ``description`` field starts empty and is filled
lazily the first time a figure is read off.

This is a one-time, no-API build step (pure PyMuPDF text parsing).

Usage
-----
    python scripts/build_figure_catalog.py dm7_2
    python scripts/build_figure_catalog.py dm7_1 dm7_2
    python scripts/build_figure_catalog.py all

Requires: PyMuPDF (``pip install PyMuPDF``).
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
_MANIFEST_DIR = _SCRIPTS_DIR / "manifests"
_PACKAGE_DIR = _REPO_ROOT / "geotech_references"

# A figure marker, e.g. "Figure 4-12", "Figure P-1", "Figure B-1" (DM7/UFC dash
# notation) or "Figure 2.1", "Figure 3.10" (GEC dot notation). Matched anywhere
# (not just line start) so inline-glued LoF entries segment too.
_FIG_MARKER = re.compile(r"Figure\s+((?:[A-Z]{1,3}|\d+)[-.]\d+)", re.I)
# A dotted leader terminated by the printed page number.
_LEADER_PG = re.compile(r"\.{2,}\s*(\d+)\s*$")
# Trailing bare page number (no dotted leader); guard against caption-internal
# numbers by requiring it to be the very last token.
_TRAIL_PG = re.compile(r"(?<![\d-])(\d{1,4})\s*$")
# Smart quotes / dashes / replacement char -> ASCII (PyMuPDF emits these; the
# Windows console renders them as the replacement glyph).
_SMART = {0x201C: '"', 0x201D: '"', 0x2018: "'", 0x2019: "'",
          0x2013: "-", 0x2014: "-", 0xFFFD: " "}


def _norm(s: str) -> str:
    """Lowercase and strip everything but alphanumerics (subscript/garble safe)."""
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _is_lof_noise(line: str) -> bool:
    """True for running headers/footers that bleed into the List of Figures."""
    s = line.strip()
    if not s:
        return True
    if re.match(r"(?i)^UF[SC]\s+3-", s):              # "UFC 3-220-20" header (OCR: UFS)
        return True
    if re.match(r"(?i)^\d{1,2}\s+[A-Za-z]+\s+\d{4}$", s):   # "16 January 2025"
        return True
    if re.match(r"(?i)^[ivxlcdm]{1,6}$", s):          # roman front-matter page no.
        return True
    if re.match(r"(?i)^list of (figures|tables)$", s):
        return True
    return False


def _clean_caption(seg: str) -> tuple[str, int | None]:
    """Split a between-markers segment into (caption, printed_page)."""
    seg = re.sub(r"\s+", " ", seg).strip()
    printed = None
    lm = _LEADER_PG.search(seg)
    if lm:
        printed = int(lm.group(1))
        seg = _LEADER_PG.sub("", seg)
    else:
        tm = _TRAIL_PG.search(seg)
        if tm:
            printed = int(tm.group(1))
            seg = seg[:tm.start()]
    cap = re.sub(r"\.{2,}", "", seg).translate(_SMART)
    # Strip leading colon too: GEC entries read "Figure 2.1: <caption>".
    cap = re.sub(r"\s+", " ", cap).strip(" .-:")
    return cap, printed


def _parse_list_of_figures(doc) -> list[dict]:
    """Parse the LIST OF FIGURES section into figure entries.

    Segments the section text on figure markers (robust to entries glued
    inline and to header/footer noise across page breaks). Returns a list of
    ``{figure_number, caption, printed_page}`` dicts in document order;
    ``printed_page`` may be ``None`` when no page number parsed.
    """
    start = None
    for i in range(min(60, doc.page_count)):
        if re.search(r"^\s*LIST OF FIGURES\s*$", doc[i].get_text(), re.I | re.M):
            start = i
            break
    kept: list[str] = []
    if start is not None:
        for i in range(start, min(start + 14, doc.page_count)):
            text = doc[i].get_text()
            if i > start and re.search(r"^\s*LIST OF TABLES\s*$", text, re.I | re.M):
                for ln in text.splitlines():
                    if re.search(r"(?i)^\s*list of tables\s*$", ln):
                        break
                    if not _is_lof_noise(ln):
                        kept.append(ln.strip())
                break
            kept.extend(ln.strip() for ln in text.splitlines() if not _is_lof_noise(ln))
    else:
        # No "LIST OF FIGURES" heading: fall back to the contiguous run of
        # front-matter pages dense with dotted-leader figure entries (some
        # references, e.g. GEC-9, carry the figure list with no heading). Require
        # both several figure markers AND dotted page leaders so the main TOC
        # (chapters, no figure markers) and body pages (no leaders) are skipped.
        dense = [
            i for i in range(min(60, doc.page_count))
            if len(_FIG_MARKER.findall(doc[i].get_text())) >= 3
            and len(re.findall(r"\.{3,}\s*\d{1,4}", doc[i].get_text())) >= 3
        ]
        if not dense:
            return []
        run = [dense[0]]
        for i in dense[1:]:
            if i == run[-1] + 1:
                run.append(i)
            else:
                break
        for i in run:
            kept.extend(ln.strip() for ln in doc[i].get_text().splitlines()
                        if not _is_lof_noise(ln))

    blob = "\n".join(kept)
    markers = list(_FIG_MARKER.finditer(blob))
    figs: list[dict] = []
    for k, m in enumerate(markers):
        end = markers[k + 1].start() if k + 1 < len(markers) else len(blob)
        cap, printed = _clean_caption(blob[m.end():end])
        figs.append(
            {"figure_number": m.group(1).upper(),
             "caption": cap, "printed_page": printed}
        )
    return figs


def _norm_fig_ref(s) -> str:
    """Normalize a text-cited figure ref to a catalog key ('Figure 4-12'->'4-12').

    Tolerates strings ("Figure 2.1: caption") and dicts ({"number": "2.1", ...}) —
    reference text JSON is not uniform across packages — and trims any trailing
    ": caption" so GEC-style citations match the bare figure id.
    """
    if isinstance(s, dict):
        s = (s.get("number") or s.get("figure_number") or s.get("id")
             or s.get("label") or s.get("ref") or "")
    s = (str(s) if s is not None else "").strip()
    if s.lower().startswith("figure"):
        s = s[len("figure"):].strip()
    if s:  # keep only the figure-id token; drop any trailing ": caption"
        s = re.split(r"[:\s]", s, maxsplit=1)[0]
    return s.upper()


def _enrich_from_text(package: str, figs: list[dict], max_chars: int = 800) -> int:
    """Fold concept vocabulary from the chapter text into figure descriptions.

    Figure captions use notation (``KA``/``KP``) while engineers query by
    concept ("passive earth pressure"). The structured chapter text in
    ``<package>/text/*.json`` cites each figure and carries the concept
    vocabulary in section titles / applicability / key points. We aggregate the
    context of every section that cites a figure into that figure's searchable
    ``description``. No API cost — pure cross-link of curated text.

    Returns the number of figures enriched.
    """
    text_dir = _PACKAGE_DIR / package / "text"
    if not text_dir.is_dir():
        return 0

    ctx: dict[str, list[str]] = {}
    for jf in sorted(text_dir.glob("*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for sec in data.get("sections", []):
            if not isinstance(sec, dict):
                continue
            cited = sec.get("figures", []) or []
            if not cited:
                continue
            parts: list[str] = []
            if sec.get("title"):
                parts.append(str(sec["title"]))
            if sec.get("applicability"):
                parts.append(str(sec["applicability"]))
            kps = sec.get("key_points", [])
            if isinstance(kps, list) and kps:
                parts.append(" ".join(str(k) for k in kps))
            snippet = re.sub(r"\s+", " ", " ".join(parts)).strip()
            if not snippet:
                continue
            for c in cited:
                key = _norm_fig_ref(c)
                if key:
                    bucket = ctx.setdefault(key, [])
                    if snippet not in bucket:
                        bucket.append(snippet)

    enriched = 0
    for f in figs:
        snips = ctx.get(f["figure_number"].upper())
        if not snips:
            continue
        desc = re.sub(r"\s+", " ", " ".join(snips)).strip()
        if len(desc) > max_chars:
            desc = desc[:max_chars].rsplit(" ", 1)[0]
        f["description"] = desc
        enriched += 1
    return enriched


def _chapter_of(figure_number: str):
    """Infer an integer chapter from a figure number prefix.

    ``"4-12"`` -> 4, ``"P-1"`` (prologue) -> 0, anything else -> ``None``.
    """
    prefix = figure_number.split("-", 1)[0]
    if prefix.upper() == "P":
        return 0
    if prefix.isdigit():
        return int(prefix)
    return None


def _resolve_pages(doc, figs: list[dict], body_start: int) -> dict:
    """Resolve a ``pdf_page_index`` for every figure. Mutates ``figs`` in place.

    Returns a small stats dict.
    """
    norm_pages = [
        _norm(re.sub(r"\s+", " ", doc[i].get_text()))
        for i in range(doc.page_count)
    ]

    for f in figs:
        key = _norm(f"Figure {f['figure_number']}")
        tgt = _norm(f["caption"])[:15]
        idx = None
        if tgt:
            needle = key + tgt
            for i in range(body_start, doc.page_count):
                if needle in norm_pages[i]:
                    idx = i
                    break
        f["pdf_page_index"] = idx

    # Fallback 1: median printed->index offset for figures still unresolved.
    offsets = [
        f["pdf_page_index"] - f["printed_page"]
        for f in figs
        if f["pdf_page_index"] is not None and f["printed_page"]
    ]
    offset = int(statistics.median(offsets)) if offsets else 0
    filled_offset = 0
    for f in figs:
        if f["pdf_page_index"] is None and f["printed_page"]:
            f["pdf_page_index"] = max(0, min(doc.page_count - 1,
                                             f["printed_page"] + offset))
            f["page_estimated"] = True
            filled_offset += 1

    # Fallback 2: monotonic interpolation between resolved neighbours.
    filled_interp = 0
    for i, f in enumerate(figs):
        if f["pdf_page_index"] is not None:
            continue
        prev_idx = next((figs[j]["pdf_page_index"] for j in range(i - 1, -1, -1)
                         if figs[j]["pdf_page_index"] is not None), None)
        nxt_idx = next((figs[j]["pdf_page_index"] for j in range(i + 1, len(figs))
                        if figs[j]["pdf_page_index"] is not None), None)
        if prev_idx is not None and nxt_idx is not None:
            f["pdf_page_index"] = (prev_idx + nxt_idx) // 2
        elif prev_idx is not None:
            f["pdf_page_index"] = prev_idx
        elif nxt_idx is not None:
            f["pdf_page_index"] = nxt_idx
        else:
            f["pdf_page_index"] = body_start
        f["page_estimated"] = True
        filled_interp += 1

    resolved = sum(1 for f in figs if not f.get("page_estimated"))
    return {
        "total": len(figs),
        "caption_resolved": resolved,
        "offset_filled": filled_offset,
        "interp_filled": filled_interp,
        "median_offset": offset,
    }


def _load_manifest(package: str) -> dict:
    mf = _MANIFEST_DIR / f"{package}.json"
    if not mf.exists():
        raise FileNotFoundError(f"No manifest for package '{package}': {mf}")
    return json.loads(mf.read_text(encoding="utf-8"))


def _repo_relative_pdf_path(manifest: dict) -> str:
    """Resolve the manifest pdf_path to a path relative to the repo root.

    Manifests store ``pdf_path`` relative to ``scripts/manifests/`` (e.g.
    ``../../docs/ufc_3_220_20_2025.pdf``). We re-express it relative to the
    repo root (e.g. ``docs/ufc_3_220_20_2025.pdf``) so the catalog is portable
    and resolvable from the installed package.
    """
    raw = manifest.get("pdf_path", "")
    abs_pdf = (_MANIFEST_DIR / raw).resolve()
    try:
        return abs_pdf.relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return abs_pdf.as_posix()


def build_catalog(package: str) -> dict:
    """Build and write ``figures_catalog.json`` for one package."""
    import fitz  # PyMuPDF

    manifest = _load_manifest(package)
    pdf_rel = _repo_relative_pdf_path(manifest)
    pdf_abs = _REPO_ROOT / pdf_rel
    if not pdf_abs.exists():
        raise FileNotFoundError(f"PDF not found for '{package}': {pdf_abs}")

    chapters = manifest.get("chapters", [])
    starts = [c["page_start"] for c in chapters if isinstance(c.get("page_start"), int)]
    # page_start is the 1-based PDF page of the first chapter; body index is -1.
    body_start = (min(starts) - 1) if starts else 0

    doc = fitz.open(str(pdf_abs))
    try:
        figs = _parse_list_of_figures(doc)
        if not figs:
            raise ValueError(f"No LIST OF FIGURES parsed from {pdf_abs}")
        stats = _resolve_pages(doc, figs, body_start)
    finally:
        doc.close()

    stats["enriched"] = _enrich_from_text(package, figs)

    out_figs = [
        {
            "figure_number": f["figure_number"],
            "caption": f["caption"],
            "chapter": _chapter_of(f["figure_number"]),
            "pdf_page_index": f["pdf_page_index"],
            "printed_page": f["printed_page"],
            "page_estimated": bool(f.get("page_estimated", False)),
            "description": f.get("description", ""),
        }
        for f in figs
    ]

    catalog = {
        "reference_id": manifest.get("reference_id", ""),
        "reference_title": manifest.get("reference_title", ""),
        "package": package,
        "volume": manifest.get("volume"),
        "pdf_path": pdf_rel,
        "figure_count": len(out_figs),
        "figures": out_figs,
    }

    out_path = _PACKAGE_DIR / package / "figures_catalog.json"
    out_path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(
        f"[{package}] {stats['total']} figures "
        f"(caption-resolved {stats['caption_resolved']}, "
        f"offset {stats['offset_filled']}, interp {stats['interp_filled']}; "
        f"median offset {stats['median_offset']}; "
        f"text-enriched {stats['enriched']}) -> {out_path}"
    )
    return catalog


def _packages_with_pdf() -> list[str]:
    out = []
    for mf in sorted(_MANIFEST_DIR.glob("*.json")):
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("pdf_path"):
            out.append(mf.stem)
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        print("Packages with a manifest pdf_path:", ", ".join(_packages_with_pdf()))
        return 1
    targets = _packages_with_pdf() if argv == ["all"] else argv
    rc = 0
    for pkg in targets:
        try:
            build_catalog(pkg)
        except Exception as e:  # noqa: BLE001 — surface per-package failures, keep going
            print(f"[{pkg}] FAILED: {type(e).__name__}: {e}")
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
