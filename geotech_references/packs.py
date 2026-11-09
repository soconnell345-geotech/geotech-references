"""Make, check and list local reference packs (BACKLOG REF-64).

    python -m geotech_references.packs new <dir> --title "..." [--id local_x]
                                             [--reference-id ...] [--pdf FILE]
    python -m geotech_references.packs check <dir>
    python -m geotech_references.packs list
    python -m geotech_references.packs index [--rebuild]

A pack is a deployment's own reference in the library's layout (see
:mod:`geotech_references._packs` and ``docs/REFERENCE_PACKS.md``). ``check``
exits 0 when the pack can be used and 1 when it cannot; it prints every
error, every warning and what it found. It never writes into the pack.

Packs are private deployment data: ``new`` and ``check`` refuse a pack
folder inside this installed package or inside a git work tree of the
public repositories.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from . import _packs
from ._schema import validate_schema

#: The public repositories a pack must never sit inside.
PUBLIC_REPOS = ("geotech-references", "geotechstaffengineer", "planlens")
#: The largest ``read_notes`` a catalog entry may carry.
READ_NOTES_MAX = 500
#: ``pack.json`` keys every pack must give, non-empty.
REQUIRED_PACK_KEYS = ("id", "reference_id", "reference_title")
#: ``pack.json`` keys a pack should give (a warning when one is missing).
RECOMMENDED_PACK_KEYS = ("pdf_files", "prepared_by", "prepared_on", "method",
                         "distribution")
METHODS = ("printed", "model", "hand")
_PAGE_MARK = re.compile(r"[\[(]p+\.\s*[A-Za-z0-9]")


# ---------------------------------------------------------------------------
# Where a pack may live
# ---------------------------------------------------------------------------

def _git_remote_urls(top: Path) -> list[str]:
    """The remote URLs of the git work tree at ``top`` (best effort)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(top), "config", "--get-regexp",
             r"^remote\..*\.url$"],
            capture_output=True, text=True, timeout=10)
        if out.returncode in (0, 1):
            return [line.split(None, 1)[1] for line in out.stdout.splitlines()
                    if " " in line]
    except (OSError, subprocess.SubprocessError):
        pass
    # no git: read the config file itself
    git = top / ".git"
    if git.is_file():  # a worktree or submodule: "gitdir: <path>"
        m = re.match(r"gitdir:\s*(.+)", git.read_text(errors="replace"))
        if not m:
            return []
        git = (top / m.group(1).strip()).resolve()
        common = git / "commondir"
        if common.is_file():
            git = (git / common.read_text().strip()).resolve()
    try:
        text = (git / "config").read_text(errors="replace")
    except OSError:
        return []
    return re.findall(r"^\s*url\s*=\s*(\S+)", text, re.MULTILINE)


def location_problem(folder: Path) -> str | None:
    """Why a pack may not live at ``folder``, or None when it may."""
    here = folder.resolve()
    package = _packs._PACKAGE_DIR.resolve()
    if here == package or package in here.parents:
        return (f"{folder} is inside the installed geotech_references "
                "package; keep a pack outside it")
    for top in (here, *here.parents):
        if not (top / ".git").exists():
            continue
        if top == package.parent:
            return (f"{folder} is inside the geotech-references source "
                    f"checkout ({top}); keep a pack outside the public repos")
        for url in _git_remote_urls(top):
            name = url.rstrip("/").rsplit("/", 1)[-1].lower()
            name = name[:-4] if name.endswith(".git") else name
            if name in PUBLIC_REPOS:
                return (f"{folder} is inside a git work tree of the public "
                        f"repository {name} ({top}); keep a pack outside the "
                        "public repos")
        return None  # the nearest work tree is not a public one
    return None


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

@contextmanager
def _packs_setting(value: str):
    old = os.environ.get(_packs.PACKS_ENV)
    os.environ[_packs.PACKS_ENV] = value
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(_packs.PACKS_ENV, None)
        else:
            os.environ[_packs.PACKS_ENV] = old


def _walk_sections(sections):
    for sec in sections or []:
        if isinstance(sec, dict):
            yield sec
            yield from _walk_sections(sec.get("subsections"))


def _norm_number(n) -> str:
    from ._figures_db import _norm_fig_number
    return _norm_fig_number(str(n))


_is_file_name = _packs.bare_file_name
#: How a PDF must be named in a pack (pack.json, the catalog).
_BARE = "a bare file name: no folder, '..' or drive"


def _find_pdf(folder: Path, name: str) -> Path | None:
    p = folder / name
    if p.is_file():
        return p
    docs = os.environ.get("GEOTECH_REFERENCES_DOCS")
    if docs and (Path(docs) / name).is_file():
        return Path(docs) / name
    return None


def _check_pack_json(folder: Path, report: dict) -> dict | None:
    err, warn = report["errors"].append, report["warnings"].append
    try:
        meta = _packs.read_pack_json(folder)
    except (OSError, ValueError) as e:
        err(f"pack.json: cannot be read ({e})")
        return None
    for k in REQUIRED_PACK_KEYS:
        if not isinstance(meta.get(k), str) or not meta.get(k).strip():
            err(f"pack.json: '{k}' is missing or empty")
    pid = str(meta.get("id") or "")
    if pid and not pid.startswith(_packs.PACK_PREFIX):
        err(f"pack.json: id '{pid}' must start with '{_packs.PACK_PREFIX}'")
    if pid and pid != folder.name:
        err(f"pack.json: id '{pid}' is not the folder's name "
            f"'{folder.name}'")
    if pid in _packs.builtin_ids():
        err(f"pack.json: id '{pid}' is a built-in reference's name")
    if not (meta.get("edition") or meta.get("date")):
        warn("pack.json: give the 'edition' or 'date' as printed")
    for k in RECOMMENDED_PACK_KEYS:
        if not meta.get(k):
            warn(f"pack.json: '{k}' is not given")
    if meta.get("method") and meta["method"] not in METHODS:
        warn(f"pack.json: method '{meta['method']}' is not one of "
             f"{', '.join(METHODS)}")
    pdfs = meta.get("pdf_files") or []
    if not isinstance(pdfs, list) or not all(_is_file_name(p) for p in pdfs):
        err(f"pack.json: 'pdf_files' must be a list of file names, each "
            f"{_BARE}")
    return meta


def _check_text(folder: Path, meta: dict, report: dict) -> list[dict]:
    err, warn = report["errors"].append, report["warnings"].append
    files = sorted((folder / "text").glob("*.json")) \
        if (folder / "text").is_dir() else []
    if not files:
        err("text/: no chapter files (text/chapterNN.json)")
        return []
    chapters: list[dict] = []
    seen: dict[Any, str] = {}
    for jf in files:
        name = f"text/{jf.name}"
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            err(f"{name}: not readable JSON ({e})")
            continue
        if not isinstance(data, dict):
            err(f"{name}: not a JSON object")
            continue
        for e in validate_schema(data):
            err(f"{name}: {e}")
        for k in ("reference_id", "reference_title"):
            if k in data and meta.get(k) and data[k] != meta[k]:
                err(f"{name}: {k} '{data[k]}' is not pack.json's "
                    f"'{meta[k]}'")
        ch = data.get("chapter")
        if ch in seen:
            err(f"{name}: chapter {ch} repeats {seen[ch]}")
        else:
            seen[ch] = name
        for sec in _walk_sections(data.get("sections")):
            sid = sec.get("section_id", "?")
            for eq in sec.get("equations") or []:
                if isinstance(eq, dict) and eq.get("formula") and \
                        not eq.get("source"):
                    warn(f"{name} {sid}: equation {eq.get('id', '?')} has a "
                         "formula but no 'source' (the page it was typed "
                         "from)")
            body = sec.get("body")
            if isinstance(body, str) and body.strip() and \
                    not _PAGE_MARK.search(body):
                warn(f"{name} {sid}: body has no page marker ('[p. N]')")
        chapters.append(data)
    report["found"]["chapters"] = len(chapters)
    report["found"]["sections"] = sum(
        len(list(_walk_sections(c.get("sections")))) for c in chapters)
    return chapters


def _check_bbox(bbox) -> str | None:
    if not (isinstance(bbox, list) and len(bbox) == 4 and
            all(isinstance(v, (int, float)) and not isinstance(v, bool)
                for v in bbox)):
        return "bbox must be [x0, y0, x1, y1] in PDF points"
    if not (bbox[0] < bbox[2] and bbox[1] < bbox[3]):
        return "bbox must have x0 < x1 and y0 < y1"
    return None


def _check_catalog(folder: Path, meta: dict, report: dict) -> list[dict]:
    err, warn = report["errors"].append, report["warnings"].append
    cat_path = folder / _packs.CATALOG_NAME
    if not cat_path.is_file():
        report["found"]["figures"] = 0
        return []
    try:
        cat = json.loads(cat_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        err(f"figures_catalog.json: not readable JSON ({e})")
        return []
    figs = cat.get("figures") if isinstance(cat, dict) else None
    if not isinstance(figs, list):
        err("figures_catalog.json: needs a 'figures' list")
        return []
    if cat.get("pdf_path") and not _is_file_name(cat["pdf_path"]):
        err(f"figures_catalog.json: pdf_path must be a file name only "
            f"({_BARE}), not '{cat['pdf_path']}'")
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf  # older PyMuPDF
        except ImportError:
            pymupdf = None
    if pymupdf is None:
        report["info"].append("PyMuPDF not installed: pages and boxes not "
                              "checked against the PDF")
    docs: dict[str, Any] = {}
    numbers: dict[str, int] = {}
    good: list[dict] = []
    for i, fig in enumerate(figs):
        where = f"figures_catalog.json figures[{i}]"
        if not isinstance(fig, dict):
            err(f"{where}: not an object")
            continue
        num = fig.get("figure_number")
        if not num or not isinstance(num, str):
            err(f"{where}: figure_number is missing")
            continue
        where = f"figures_catalog.json figure {num}"
        key = _norm_number(num)
        if key in numbers:
            err(f"{where}: number repeats figures[{numbers[key]}]")
        numbers.setdefault(key, i)
        if not isinstance(fig.get("caption"), str) or not fig["caption"]:
            err(f"{where}: caption is missing")
        page = fig.get("pdf_page_index")
        if not isinstance(page, int) or isinstance(page, bool) or page < 0:
            err(f"{where}: pdf_page_index must be an integer 0 or more")
            page = None
        notes = fig.get("read_notes")
        if notes is not None and (not isinstance(notes, str) or
                                  len(notes) > READ_NOTES_MAX):
            err(f"{where}: read_notes must be text of at most "
                f"{READ_NOTES_MAX} characters")
        bbox = fig.get("bbox")
        if bbox is not None and _check_bbox(bbox):
            err(f"{where}: {_check_bbox(bbox)}")
            bbox = None
        pdf_name = fig.get("pdf_path") or cat.get("pdf_path")
        if fig.get("pdf_path") and not _is_file_name(fig["pdf_path"]):
            err(f"{where}: pdf_path must be a file name only ({_BARE}), "
                f"not '{fig['pdf_path']}'")
            pdf_name = None
        good.append(fig)
        if pymupdf is None or page is None or not _is_file_name(pdf_name):
            continue
        if pdf_name not in docs:
            path = _find_pdf(folder, pdf_name)
            docs[pdf_name] = pymupdf.open(str(path)) if path else None
            if path is None:
                report["info"].append(
                    f"{pdf_name}: not in the pack folder or "
                    "GEOTECH_REFERENCES_DOCS; pages not checked")
        doc = docs[pdf_name]
        if doc is None:
            continue
        if page >= doc.page_count:
            err(f"{where}: pdf_page_index {page} is past the PDF's "
                f"{doc.page_count} pages")
            continue
        pg = doc[page]
        text = re.sub(r"\s+", " ", pg.get_text())
        if not re.search(r"(?<![\w.-])" + re.escape(num) + r"(?![\w-])",
                         text):
            if fig.get("page_estimated"):
                report["info"].append(
                    f"{where}: number not printed on page index {page} "
                    "(page_estimated is set)")
            else:
                warn(f"{where}: number '{num}' is not printed on page index "
                     f"{page}; fix the page or set page_estimated: true")
        if bbox is not None:
            r = pg.rect
            if not (0 <= bbox[0] and 0 <= bbox[1] and bbox[2] <= r.width + 0.5
                    and bbox[3] <= r.height + 0.5):
                err(f"{where}: bbox {bbox} is not inside the page "
                    f"({r.width:.0f} x {r.height:.0f} pt)")
    for doc in docs.values():
        if doc is not None:
            doc.close()
    report["found"]["figures"] = len(good)
    return good


def _smoke(folder: Path, pid: str, chapters: list[dict], figures: list[dict],
           report: dict) -> None:
    """Index the built-ins plus this pack and look things up through the
    same calls the librarian makes."""
    from . import _figures_db, _retrieval_db
    err, info = report["errors"].append, report["info"].append
    with _packs_setting(str(folder)):
        if _packs.pack_dir(pid) is None:
            err("smoke test: the pack is not picked up: "
                + "; ".join(_packs.problems()))
            return
        listed = {r["reference"]: r for r in
                  _retrieval_db.list_indexed_references()}
        if pid not in listed:
            err("smoke test: the pack is not in list_indexed_references")
            return
        info(f"indexed: {listed[pid]['n_chapters']} chapters, "
             f"{listed[pid]['n_sections']} sections")
        for ch in chapters:
            title = str(ch.get("chapter_title") or "").strip()
            if not title:
                continue
            hits = _retrieval_db.reference_search(title, reference=pid,
                                                  limit=5)
            if not any(isinstance(h, dict) and h.get("reference") == pid
                       for h in hits):
                err(f"smoke test: a search for chapter {ch.get('chapter')}'s "
                    f"title '{title}' finds nothing in the pack")
                continue
            wide = _retrieval_db.reference_search(title, limit=50)
            ranks = [i + 1 for i, h in enumerate(wide)
                     if isinstance(h, dict) and h.get("reference") == pid]
            info(f"chapter {ch.get('chapter')} '{title}': found; across the "
                 "whole library its first hit ranks "
                 + (str(ranks[0]) if ranks else "below 50"))
        if figures:
            num = figures[0]["figure_number"]
            try:
                rec = _figures_db.figure_get(pid, num)
                info(f"figure_get {num}: page index {rec['pdf_page_index']}")
            except KeyError as e:
                err(f"smoke test: figure_get {num} failed ({e})")
                return
            try:
                path, _ = _figures_db.resolve_pdf(pid, num)
                info(f"resolve_pdf {num}: {path.name}")
            except FileNotFoundError:
                info(f"resolve_pdf {num}: PDF not found here (the app asks "
                     "its fetcher by file name)")


def check_pack(folder: str | Path, smoke: bool = True) -> dict:
    """Check one pack; ``{"errors", "warnings", "info", "found"}``."""
    folder = Path(folder)
    report: dict = {"errors": [], "warnings": [], "info": [], "found": {}}
    if not folder.is_dir():
        report["errors"].append(f"{folder}: not a folder")
        return report
    where = location_problem(folder)
    if where:
        report["errors"].append(where)
    meta = _check_pack_json(folder, report)
    if meta is None:
        return report
    chapters = _check_text(folder, meta, report)
    figures = _check_catalog(folder, meta, report)
    pid = str(meta.get("id") or "")
    if smoke and chapters and not report["errors"]:
        _smoke(folder, pid, chapters, figures, report)
    elif smoke:
        report["info"].append("smoke test not run: fix the errors first")
    return report


# ---------------------------------------------------------------------------
# new / list / index
# ---------------------------------------------------------------------------

def new_pack(folder: str | Path, title: str, pack_id: str | None = None,
             reference_id: str | None = None, pdf: str | None = None,
             edition: str = "") -> Path:
    """Write a pack skeleton (``pack.json`` and an empty ``text/``)."""
    folder = Path(folder)
    pid = pack_id or folder.name
    if not pid.startswith(_packs.PACK_PREFIX):
        raise ValueError(f"the id '{pid}' must start with "
                         f"'{_packs.PACK_PREFIX}'")
    if pid != folder.name:
        raise ValueError(f"the folder's name '{folder.name}' must be the "
                         f"id '{pid}'")
    if pid in _packs.builtin_ids():
        raise ValueError(f"'{pid}' is a built-in reference's name")
    if (folder / _packs.PACK_FILE).exists():
        raise FileExistsError(f"{folder / _packs.PACK_FILE} already exists")
    where = location_problem(folder.parent if not folder.exists() else folder)
    if where:
        raise ValueError(where)
    meta = {
        "id": pid,
        "reference_id": reference_id or title,
        "reference_title": title,
        "edition": edition,
        "date": "",
        "pdf_files": [Path(pdf).name] if pdf else [],
        "prepared_by": "",
        "prepared_on": datetime.date.today().isoformat(),
        "method": "printed",
        "distribution": "this deployment's own; not for the public repos",
    }
    (folder / "text").mkdir(parents=True, exist_ok=True)
    (folder / _packs.PACK_FILE).write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    return folder


def list_packs() -> dict:
    """What ``GEOTECH_REFERENCES_PACKS`` resolves to, with counts."""
    rows = []
    for pid, folder in _packs.packs():
        try:
            meta = _packs.read_pack_json(folder)
        except (OSError, ValueError):
            meta = {}
        n_sections = 0
        chapters = 0
        for _, jf in [(p, f) for p, f in _packs.text_jsons() if p == pid]:
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            chapters += 1
            n_sections += len(list(_walk_sections(data.get("sections"))))
        n_figures = 0
        cat = folder / _packs.CATALOG_NAME
        if cat.is_file():
            try:
                n_figures = len(json.loads(cat.read_text(
                    encoding="utf-8")).get("figures", []))
            except (OSError, ValueError, AttributeError):
                pass
        rows.append({"id": pid, "title": meta.get("reference_title", ""),
                     "folder": str(folder), "chapters": chapters,
                     "sections": n_sections, "figures": n_figures})
    return {"setting": os.environ.get(_packs.PACKS_ENV, ""), "packs": rows,
            "problems": _packs.problems()}


def _print_report(report: dict) -> None:
    for e in report["errors"]:
        print(f"ERROR    {e}")
    for w in report["warnings"]:
        print(f"WARNING  {w}")
    for i in report["info"]:
        print(f"ok       {i}")
    found = ", ".join(f"{v} {k}" for k, v in report["found"].items())
    verdict = "FAILED" if report["errors"] else "PASSED"
    print(f"{verdict}: {len(report['errors'])} errors, "
          f"{len(report['warnings'])} warnings" + (f"; {found}" if found
                                                    else ""))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m geotech_references.packs",
        description="Make, check and list local reference packs.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_new = sub.add_parser("new", help="write a pack skeleton")
    p_new.add_argument("dir")
    p_new.add_argument("--title", required=True,
                       help="the reference's title as printed")
    p_new.add_argument("--id", help="pack id (local_...); the folder name "
                                    "by default")
    p_new.add_argument("--reference-id",
                       help="the designation as printed (the title if left "
                            "out)")
    p_new.add_argument("--pdf", help="the reference's PDF (its file name is "
                                     "recorded; copy it into the pack or "
                                     "where the PDFs go)")
    p_new.add_argument("--edition", default="")
    p_check = sub.add_parser("check", help="check a pack; exit 0 or 1")
    p_check.add_argument("dir")
    p_check.add_argument("--no-smoke", action="store_true",
                         help="skip building the index")
    sub.add_parser("list", help="what GEOTECH_REFERENCES_PACKS resolves to")
    p_index = sub.add_parser("index", help="build the search indexes")
    p_index.add_argument("--rebuild", action="store_true",
                         help="rebuild even when they are current")
    args = parser.parse_args(argv)

    if args.command == "new":
        try:
            folder = new_pack(args.dir, args.title, args.id,
                              args.reference_id, args.pdf, args.edition)
        except (ValueError, FileExistsError) as e:
            print(f"ERROR    {e}")
            return 1
        print(f"wrote {folder / _packs.PACK_FILE} and {folder / 'text'}; "
              "fill in pack.json, write text/chapterNN.json, then run "
              f"'python -m geotech_references.packs check {folder}'")
        return 0
    if args.command == "check":
        report = check_pack(args.dir, smoke=not args.no_smoke)
        _print_report(report)
        return 1 if report["errors"] else 0
    if args.command == "list":
        out = list_packs()
        print(f"{_packs.PACKS_ENV} = {out['setting'] or '(not set)'}")
        for row in out["packs"]:
            print(f"  {row['id']}: {row['title']} -- {row['chapters']} "
                  f"chapters, {row['sections']} sections, {row['figures']} "
                  f"figures ({row['folder']})")
        if not out["packs"]:
            print("  no packs")
        for prob in out["problems"]:
            print(f"  skipped: {prob}")
        return 0
    if args.command == "index":
        from . import _figures_db, _retrieval_db
        if args.rebuild:
            text = _retrieval_db.rebuild_db()
            figs = _figures_db.rebuild_db()
            text_refs, fig_refs = text["indexed"], figs["indexed"]
        else:
            text_refs = _retrieval_db.list_indexed_references()
            fig_refs = _figures_db.list_indexed_figures()
        print(f"text index: {len(text_refs)} references "
              f"({_retrieval_db._db_path()})")
        print(f"figure index: {len(fig_refs)} catalogs "
              f"({_figures_db._db_path()})")
        local = [r for r in text_refs
                 if str(r["reference"]).startswith(_packs.PACK_PREFIX)]
        for r in local:
            print(f"  {r['reference']}: {r['n_chapters']} chapters, "
                  f"{r['n_sections']} sections")
        for prob in _packs.problems():
            print(f"  skipped: {prob}")
        return 0
    return 2  # pragma: no cover


if __name__ == "__main__":
    sys.exit(main())
