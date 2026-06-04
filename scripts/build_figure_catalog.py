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

# A figure marker, e.g. "Figure 4-12", "Figure P-1" (DM7/UFC dash), "Figure 2.1"
# (GEC dot), or "Figure 1 - 1" (micropile spaced dash). Matched anywhere (not
# just line start) so inline-glued LoF entries segment too. Spaces around the
# separator are tolerated and stripped from the captured id (see _fig_id).
_FIG_MARKER = re.compile(r"Figure\s+((?:[A-Z]{1,3}|\d+)\s*[-.]\s*\d+)", re.I)


def _fig_id(raw: str) -> str:
    """Normalize a captured figure id: 'Figure '-free, spaces stripped, upper."""
    return re.sub(r"\s+", "", raw).upper()


# Sequential figure numbering used by some older refs (e.g. GEC-4, 1999):
# "Figure 1", "Figure 21" with no chapter dash. Lookaheads exclude longer digit
# runs and dash/dot *ids* ("1-1", "1.5") but still allow a caption period
# ("Figure 1. Components ...").
_SEQ_MARKER = re.compile(r"Figure\s+(\d{1,3})(?!\d)(?![-.]\d)", re.I)
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


def _parse_list_of_figures(doc) -> tuple[list[dict], "int | None"]:
    """Parse the LIST OF FIGURES section into figure entries.

    Segments the section text on figure markers (robust to entries glued
    inline and to header/footer noise across page breaks). Returns
    ``(figs, lof_last_page)``: a list of ``{figure_number, caption,
    printed_page}`` dicts in document order, plus the last PDF page index the
    figure list occupies (so body resolution can start after the front matter).
    ``lof_last_page`` is ``None`` when no list is found.
    """
    lof_pages: list[int] = []
    start = None
    for i in range(min(60, doc.page_count)):
        if re.search(r"^\s*LIST OF FIGURES\s*$", doc[i].get_text(), re.I | re.M):
            start = i
            break
    kept: list[str] = []
    if start is not None:
        for i in range(start, min(start + 14, doc.page_count)):
            text = doc[i].get_text()
            lof_pages.append(i)
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
            return [], None
        run = [dense[0]]
        for i in dense[1:]:
            if i == run[-1] + 1:
                run.append(i)
            else:
                break
        lof_pages = run
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
            {"figure_number": _fig_id(m.group(1)),
             "caption": cap, "printed_page": printed}
        )
    return figs, (max(lof_pages) if lof_pages else None)


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


def _figs_from_body(doc, marker=None) -> list[dict]:
    """Extract figures by scanning the body for labeled captions — used when a
    reference has no parseable List of Figures (e.g. GEC-6, GEC-14). A figure's
    caption appears on its own page, so the page where ``Figure X-Y`` is followed
    by a substantial capitalized caption is taken as that figure's page. ``marker``
    defaults to the dash/dot id pattern; pass ``_SEQ_MARKER`` for sequential refs.
    """
    marker = marker or _FIG_MARKER
    figs: list[dict] = []
    seen: set[str] = set()
    for i in range(doc.page_count):
        text = doc[i].get_text()
        for m in marker.finditer(text):
            num = _fig_id(m.group(1))
            if num in seen:
                continue
            tail = re.sub(r"^[\s:.\-]+", "", text[m.end():m.end() + 220])
            cap = re.split(r"[\r\n]", tail, maxsplit=1)[0]
            cap = re.sub(r"\.{2,}.*$", "", cap)            # drop dotted-leader tail
            cap = re.sub(r"\s+", " ", cap).strip(" .-:")
            # Caption pages read "Figure X-Y. <Capitalized caption>"; in-text refs
            # ("...in Figure X-Y") leave little/no caption after the marker.
            if len(cap) < 8 or not cap[:1].isupper():
                continue
            seen.add(num)
            figs.append({"figure_number": num, "caption": cap[:200],
                         "printed_page": None, "pdf_page_index": i,
                         "page_estimated": False})
    return figs


def _figs_from_pdf(pdf_abs, seq=False) -> list[dict]:
    """Parse + page-resolve every figure in one PDF (figs carry page_estimated).

    ``seq=True`` forces sequential body extraction (refs numbered "Figure 1",
    "Figure 2" with no chapter dash, e.g. GEC-4).
    """
    import fitz  # PyMuPDF
    doc = fitz.open(str(pdf_abs))
    try:
        if seq:
            return _figs_from_body(doc, _SEQ_MARKER)
        figs, lof_last = _parse_list_of_figures(doc)
        if figs:
            # Resolve from just after the figure list so a caption matches on its
            # real body page, not its LoF entry.
            body_start = (lof_last + 1) if lof_last is not None else 0
            _resolve_pages(doc, figs, body_start)
            return figs
        # No List of Figures: extract labeled captions from the body directly.
        return _figs_from_body(doc)
    finally:
        doc.close()


def build_catalog(package: str) -> dict:
    """Build and write ``figures_catalog.json`` for one package.

    Single-volume manifests carry a ``pdf_path``. Multi-volume manifests carry a
    ``volumes`` list of ``{pdf_path, volume}``; each figure is tagged with its own
    volume's ``pdf_path`` so read-off resolves to the right PDF.
    """
    manifest = _load_manifest(package)
    volumes = manifest.get("volumes")

    if volumes:
        figs: list[dict] = []
        for vol in volumes:
            vrel = _repo_relative_pdf_path({"pdf_path": vol.get("pdf_path", "")})
            vabs = _REPO_ROOT / vrel
            if not vabs.exists():
                raise FileNotFoundError(f"PDF not found for '{package}': {vabs}")
            vfigs = _figs_from_pdf(vabs)
            for f in vfigs:
                f["pdf_path"] = vrel            # per-figure source PDF
                f["volume"] = vol.get("volume")
            figs.extend(vfigs)
        if not figs:
            raise ValueError(f"No figures parsed from any volume of '{package}'")
        pdf_rel = _repo_relative_pdf_path({"pdf_path": volumes[0].get("pdf_path", "")})
    else:
        pdf_rel = _repo_relative_pdf_path(manifest)
        pdf_abs = _REPO_ROOT / pdf_rel
        if not pdf_abs.exists():
            raise FileNotFoundError(f"PDF not found for '{package}': {pdf_abs}")
        figs = _figs_from_pdf(
            pdf_abs, seq=manifest.get("figure_numbering") == "sequential")
        if not figs:
            raise ValueError(f"No figures parsed from {pdf_abs}")

    enriched = _enrich_from_text(package, figs)

    out_figs = []
    for f in figs:
        rec = {
            "figure_number": f["figure_number"],
            "caption": f["caption"],
            "chapter": _chapter_of(f["figure_number"]),
            "pdf_page_index": f["pdf_page_index"],
            "printed_page": f["printed_page"],
            "page_estimated": bool(f.get("page_estimated", False)),
            "description": f.get("description", ""),
        }
        if f.get("pdf_path"):              # multi-volume per-figure override
            rec["pdf_path"] = f["pdf_path"]
        if f.get("volume") is not None:
            rec["volume"] = f["volume"]
        out_figs.append(rec)

    resolved = sum(1 for f in out_figs if not f["page_estimated"])
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
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"[{package}] {len(out_figs)} figures (caption-resolved {resolved}, "
        f"estimated {len(out_figs) - resolved}; text-enriched {enriched}) -> {out_path}"
    )
    return catalog


def _packages_with_pdf() -> list[str]:
    out = []
    for mf in sorted(_MANIFEST_DIR.glob("*.json")):
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("pdf_path") or data.get("volumes"):
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
