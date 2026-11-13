"""What a fetched section can reach (2026-11-12 reach audit).

The owner's test for the reference helper: it has access to everything it
is told it has. A fetched section tells it things: its ``figures`` and
``tables`` lists name printed figures and tables, and its body points to
other parts of the same document ("see Chapter 9", "Eqs. 4-8 to 4-13").
Before this module nothing said which of those the library holds, so the
helper could ask ``figure_get`` for a figure the catalog does not have, or
quote a table the library holds only by its title.

So every fetched section (``_retrieval_db.reference_get`` and
``_retrieval.retrieve_section``) carries, where it has something to say:

- ``figures_held``: for the figure numbers its ``figures`` list names,
  ``"catalog"`` where a figure catalog row holds it as ``figure_get`` looks
  it up (``figure_get`` gives the page; the page is readable only where
  the PDF is on the host); ``"catalog (2 rows: give figure_get the
  pdf_page_index)"`` for a number on several rows; ``"catalog (as 5-5)"``
  for a part the catalog files with its whole figure, ``"catalog (as
  parts C14-3A, C14-3B)"`` for a figure filed by its parts; or ``"not
  catalogued"`` (no catalog row: ``figure_get`` cannot fetch it);
- ``tables_held``: for the table numbers its ``tables`` list names, where
  the table's values are, from the reference's table catalog
  (``tables_catalog.json``, rows with ``table_number``, ``values`` "text" |
  "lookup" | "page" and ``values_in``): ``"text: <section id>"`` (its
  cells are typed in that section; ``reference_get`` it), ``"lookup:
  <function>"`` (that function returns them; ``lookup_reference`` runs it
  by this name), ``"page: printed p. P (pdf_page_index N)"`` (only on the
  printed page: ``table_get`` gives it, readable only where the PDF is on
  the host), or ``"not catalogued"`` (no catalog row, or no catalog for
  the reference: ``table_get`` cannot fetch it);
- ``not_held``: the parts of the SAME document its body points to that the
  library holds no text or catalog row for (a section, chapter, appendix
  or annex, equation, table or figure), at most :data:`NOT_HELD_MAX` and
  then "and N more".

Both held maps come in a short form (:func:`collapse`): ``{"all":
answer}`` when every number has the same answer, else the numbers whose
answer differs plus ``"others": <the commonest answer>``. A section listing
60 figures would otherwise repeat "catalog" 60 times. The fetch's ``note``
says what each key and each answer it carries means (:func:`reach_note`).

A pointer is flagged only when it is certainly one into the same document
and certainly not held. Not flagged: a pointer with another document named
just before it (ASTM, AASHTO, ACI, "Falsework Manual" ...) or "of / in /
from" one after it; one after an author and year; a number whose form is
not one of the document's own (its section, equation, table or figure
numbers) or that reads as a range ("Eqs. 6.9-6.14"); a number split across
a line; a value after a list ("Eq. 10-1, 1.0 for ..."); an appendix with
its title after it (another report's contents); a chapter number of 40 or
more and a bare section number of 100 or more. Held: a section id, or a
section printed as a heading inside another's body ("11.4.5.1 Multi-Period
Design Response Spectrum: ..."); a chapter file; an appendix or annex a
chapter title names; an equation an equation object, a "[Eq. 9-5]" marker
or a formula typed with its tag holds ("Pa = ... (Eq. 4-3-17)"); a table
or figure a listing or catalog holds, part letters either way (Figure 2-6
is held by its parts 2-6a to 2-6f, Figure 7-7a by Figure 7-7).

The flags are worked out once, when the text search database is built
(:func:`fill_reach_table`, table ``section_reach``), from the chapter
files, the figure catalogs and the table catalogs, and read back on each
fetch. Search hits do not carry them.
"""

from __future__ import annotations

import copy
import functools
import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Any

from . import _packs

_PACKAGE_DIR = Path(__file__).parent
FIGURES_CATALOG = "figures_catalog.json"
TABLES_CATALOG = "tables_catalog.json"

HELD_IN_CATALOG = "catalog"
#: A listed figure or table with no catalog row (or no catalog).
NOT_CATALOGUED = "not catalogued"
NOT_HELD = "not held"
#: The sentence a fetch with a ``not_held`` list adds to its ``note``.
NOT_HELD_NOTE = ("not_held names parts of this same document that the text "
                 "points to and that the library holds no text or catalog "
                 "row for (a coded lookup may still return some of their "
                 "values): do not quote or cite them as if they had been "
                 "read.")
#: What each answer of the held maps means, for the fetch's ``note``; only
#: the answers a fetch carries are explained (:func:`reach_note`).
FIGURE_ANSWERS = {
    "catalog": "'catalog': figure_get finds it and its page",
    "rows": "'N rows': give figure_get the pdf_page_index",
    "as": "'as X': figure_get finds it as X",
    NOT_CATALOGUED: "'not catalogued': no catalog row, figure_get cannot "
                    "fetch it",
}
TABLE_ANSWERS = {
    "text": "'text: S': typed in section S (reference_get)",
    "lookup": "'lookup: F': function F returns them (lookup_reference)",
    "page": "'page': only on that printed page (table_get)",
    NOT_CATALOGUED: "'not catalogued': no catalog row, table_get cannot "
                    "fetch it",
}
#: Said once when an answer names a page to read.
PAGE_NOTE = "Pages are readable only where the PDF is on this host."
#: Said when a held map names some numbers and gives the rest as "others".
SHORT_NOTE = "'others' stands for every listed number not named."
#: Said when a table answer comes from one of several rows of its number.
ROWS_NOTE = ("'one of N rows': the catalog has N tables so numbered; the "
             "answer is the one filed under this section, else the first.")
#: A fetch that would pass this many characters with :func:`reach_note`
#: goes without it (the keys stay): the sections near or over the
#: library's 14,000-character budget from their own text would otherwise
#: pass it, or the app's 16,000-character cap (dm7_2 4-9).
NOTE_BUDGET_CHARS = 14000
#: The most entries one section's ``not_held`` lists.
NOT_HELD_MAX = 15

# ---------------------------------------------------------------------------
# Numbers
# ---------------------------------------------------------------------------

_DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"
#: A printed number as listings write it: "7-7", "4-12", "P-1", "A.1",
#: "C22-2", "11.4-1", "3.1a", "9-37(a)".
_NUM = r"(?:[A-Z]{1,3}[-.]?)?\d+(?:[-.]\d+)*[a-z]?(?:\([a-z]\))?"
_LISTING_RE = {
    "figure": re.compile(
        r"^\W*(?:(?i:figures?|figs?\.?|exhibit)\s*)?(" + _NUM + r")(?!\d)"),
    "table": re.compile(
        r"^\W*(?:(?i:tables?|tbl\.?)\s*)?(" + _NUM + r")(?!\d)"),
}
_DICT_KEYS = {"figure": ("figure_id", "figure_number", "id", "number"),
              "table": ("table_id", "table_number", "id", "number")}


_DASH_RE = re.compile(f"[{_DASHES}]")
_SHAPE_PART = re.compile(r"\([a-z]\)$|(?<=\d)[a-z]$")
_DIGITS = re.compile(r"\d+")
_CAPITALS = re.compile(r"[A-Z]+")


def _dashes(text: str) -> str:
    """Text with every printed dash and minus sign as '-'."""
    return _DASH_RE.sub("-", str(text))


def listing_number(entry, kind: str) -> str | None:
    """The printed number a ``figures`` / ``tables`` entry names
    (``kind`` "figure" or "table"), or None for an entry that names none
    ("Analysis Period guidelines by highway condition"). An entry is a
    string ("Figure 7-7 (a): ...", "4-1") or a dict with ``figure_id`` /
    ``table_id`` / ``id``."""
    if isinstance(entry, dict):
        raw = next((entry[k] for k in _DICT_KEYS[kind]
                    if entry.get(k) not in (None, "")), None)
        if raw is None:
            return None
        text = str(raw)
    else:
        text = str(entry)
    m = _LISTING_RE[kind].match(_dashes(text))
    return m.group(1) if m else None


def figure_keys(number: str) -> tuple:
    """The forms a figure number is looked up by, as ``figure_get`` reads
    it (``_figures_db._fig_number_keys``)."""
    from ._figures_db import _fig_number_keys
    return _fig_number_keys(_dashes(number))


def table_key(number: str) -> str:
    """A table number for comparing: dashes as '-', no spaces, a part letter
    printed in brackets as the plain letter, upper case, '.' and '-' alike
    (the rule the table catalogs are built by)."""
    s = re.sub(r"\s+", "", _dashes(number))
    s = re.sub(r"^(?i:tables?)\.?", "", s)
    s = re.sub(r"\(([A-Za-z])\)$", r"\1", s)
    return re.sub(r"[-.]", "-", s).upper()


def _unified(number: str) -> str:
    """A number with '-' and '.' alike and upper case, for sections,
    chapters, appendices and equations."""
    return re.sub(r"[-.]", ".", _dashes(number).strip()).upper()


def _shape(number: str) -> str:
    """A number's form: digits as 9, letters as A, separators kept, a part
    letter dropped ('4-12a' -> '9-9'; 'B.1' -> 'A.9')."""
    s = _SHAPE_PART.sub("", _dashes(number).strip())
    return _CAPITALS.sub("A", _DIGITS.sub("9", s))


def _seps(number: str) -> tuple:
    """Which separators a number uses and whether it starts with a letter:
    the numbers of one list share them ("Tables 7-1, 7-2")."""
    s = _dashes(number)
    return ("-" in s, "." in s, s[:1].isalpha())


def _is_range(number: str, shapes: set[str]) -> bool:
    """'6.9-6.14' read as one number: two halves of one known form joined
    by a dash ('Eqs. 6.9-6.14' is a range of equations)."""
    s = _dashes(number)
    for i, ch in enumerate(s):
        if ch == "-":
            left, right = s[:i], s[i + 1:]
            if left and right and _shape(left) == _shape(right) \
                    and _shape(left) in shapes:
                return True
    return False


# ---------------------------------------------------------------------------
# What a reference holds
# ---------------------------------------------------------------------------

def reference_dir(reference: str) -> Path | None:
    """The folder holding a reference's catalogs: its package folder, or a
    local pack's folder (REF-64)."""
    if str(reference).startswith(_packs.PACK_PREFIX):
        return _packs.pack_dir(reference)
    folder = _PACKAGE_DIR / reference
    return folder if folder.is_dir() else None


def catalog_paths() -> list[Path]:
    """Every figure and table catalog the flags read, there or not: one of
    each per reference with chapter text and per local pack. The text
    database's source signature takes them in, so adding, editing or
    removing a catalog rebuilds the flags."""
    folders = [d for d in sorted(_PACKAGE_DIR.iterdir())
               if d.is_dir() and (d / "text").is_dir()]
    folders += [folder for _, folder in _packs.packs()]
    return [folder / name for folder in folders
            for name in (FIGURES_CATALOG, TABLES_CATALOG)]


def _catalog_rows(path: Path, key: str) -> list[dict] | None:
    """The rows of a catalog (``{key: [...]}`` or a bare list), or None
    when there is none or it cannot be read: its figures or tables then
    answer "not catalogued", and why is kept for :func:`catalog_problems`.
    A broken or hostile file never stops the build (2026-11-12 review of
    the reach build, item 3: ``"[" * 200000`` raised RecursionError and no
    reference's text database could be built)."""
    _PROBLEMS.pop(str(path), None)
    if not path.is_file():
        return None
    why = None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except _packs.JSON_ERRORS as e:
        data, why = None, f"not readable JSON ({type(e).__name__})"
    if why is None:
        rows = data.get(key) if isinstance(data, dict) else data
        if isinstance(rows, list):
            return [r for r in rows if isinstance(r, dict)]
        why = (f"'{key}' is not a list" if isinstance(data, dict)
               else "not a JSON object or list")
    _PROBLEMS[str(path)] = why
    return None


#: Catalogs the flags could not read, by path, and why (see
#: :func:`catalog_problems`).
_PROBLEMS: dict[str, str] = {}


def catalog_problems() -> dict[str, list[str]]:
    """``{reference: [problem, ...]}``: each figure or table catalog the
    reach flags cannot read, and why (its figures or tables answer "not
    catalogued"). Read afresh, so every process names the same files. A
    local pack's are named in ``_packs.problems()`` too."""
    pack_of = {folder: pid for pid, folder in _packs.packs()}
    out: dict[str, list[str]] = {}
    for path in catalog_paths():
        key = "figures" if path.name == FIGURES_CATALOG else "tables"
        _catalog_rows(path, key)
        if str(path) in _PROBLEMS:
            ref = pack_of.get(path.parent, path.parent.name)
            out.setdefault(ref, []).append(
                f"{path}: {_PROBLEMS[str(path)]}; its {key} answer "
                f"'{NOT_CATALOGUED}'")
    return out


_EQ_ENTRY_RE = re.compile(
    r"^\W*(?:(?i:equations?|eqs?)\.?\s*)?(" + _NUM + r")(?!\d)")
_EQ_TAG_RES = (
    # [Eq. 9-5], the printed-text builder's marker (REF-29)
    re.compile(r"\[(?i:eq(?:uation)?)\.?\s*(" + _NUM + r")\]"),
    # a line that opens with its equation number: "Eq. 4-8: ..."
    re.compile(r"(?m)^\s*(?i:eq(?:uation)?)\.?\s*(" + _NUM + r")\s*[:=]"),
    # a formula line that ends with its number in brackets: "... (4-8)"
    re.compile(r"(?m)=[^\n]{0,400}\((" + _NUM + r")\)\s*$"),
)


#: An equation tag in running text: "(Eq. 4-3-17)", "Eqs. 4-4-6 and 4-4-9".
_EQ_TAG_INLINE = re.compile(
    r"(?<![A-Za-z])(?:Equations?|Eqs?)\.?[ \t\u00a0]*\(?(?P<num>"
    + r"(?:[A-Z]{1,2}[-.]?)?\d+(?:[-.]\d+)*[a-z]?)\)?(?![\dA-Za-z])"
    + r"(?P<more>(?:[ \t\u00a0]*(?:,|and|/|to|\.\.)[ \t\u00a0]*\(?"
    + r"(?:[A-Z]{1,2}[-.]?)?\d+(?:[-.]\d+)*[a-z]?\)?(?![\dA-Za-z]))*)")
#: A formula's relation sign: =, ~, <, >, and their typeset forms.
_FORMULA_SIGN = re.compile(r"[=~<>\u2248\u2264\u2265\u2245]")
#: A colon after an equation tag and a formula on the same line.
_FORMULA_AFTER = re.compile(r"\)?[ \t]*:[^\n.]{0,150}?=")
#: A section number printed as a heading inside a body, at a line or
#: sentence start and followed by its title and a colon or line end.
_INLINE_HEADING = re.compile(
    r"(?:^|\n|(?<=[.:;] ))[ \t]*(?P<num>\d+(?:[-.]\d+)+)[ \t]+"
    r"(?=[A-Z][a-z])[A-Z][^\n:]{2,80}?(?::|\n|$)")
_PART_LETTER = re.compile(r"(?:\(([A-Za-z])\)|(?<=\d)([A-Za-z]))$")


def _base(key: str) -> str:
    """A key without its part letter ('4-6A' -> '4-6', '5-5(A)' -> '5-5');
    the key itself when it has none."""
    return _PART_LETTER.sub("", key)


class _Pool:
    """Numbers held, compared with their part letters either way: a pointer
    to Figure 7-7a is held by a row for Figure 7-7, and a pointer to Figure
    2-6 by the rows for its parts 2-6a to 2-6f."""

    def __init__(self):
        self.keys: set[str] = set()
        self.bases: set[str] = set()

    def add(self, key: str) -> None:
        self.keys.add(key)
        base = _base(key)
        if base != key:
            self.bases.add(base)

    def holds(self, key: str) -> bool:
        return (key in self.keys or key in self.bases
                or _base(key) in self.keys)


class Holdings:
    """What one reference holds, for the flags: its section numbers, its
    chapters and their titles, the equation numbers it types in, the
    tables and figures its sections list, and its catalogs."""

    def __init__(self, reference: str, rows: list[sqlite3.Row]):
        self.reference = reference
        self.section_keys: set[str] = set()
        self.section_shapes: set[str] = set()
        self.section_letters: set[str] = set()
        self.chapters: set[str] = set()
        self.titles: list[str] = []
        self.equations = _Pool()
        self.equation_shapes: set[str] = set()
        self.tables = _Pool()
        self.table_shapes: set[str] = set()
        self.figure_shapes: set[str] = set()
        seen_chapters = set()
        for row in rows:
            sid = str(row["section_id"] or "")
            if sid:
                parts = _unified(sid).split(".")
                for k in range(1, len(parts) + 1):
                    self.section_keys.add(".".join(parts[:k]))
                if len(parts) > 1:
                    # chapter-prefixed (GEC-13 '1.8.2.7' prints 8.2.7) or
                    # part-lettered ('II-2.3.5') ids answer for the rest
                    self.section_keys.add(".".join(parts[1:]))
                self.section_shapes.add(_shape(sid))
                lead = re.match(r"[A-Z]+", sid)
                if lead:
                    self.section_letters.add(lead.group(0))
            if row["chapter"] not in seen_chapters:
                seen_chapters.add(row["chapter"])
                self.chapters.add(str(row["chapter"]))
                self.titles.append(str(row["chapter_title"] or ""))
            for eq in json.loads(row["equations_json"] or "[]"):
                raw = (next((eq[k] for k in ("id", "eq_id", "equation_id",
                                             "number") if eq.get(k)), "")
                       if isinstance(eq, dict) else eq)
                m = _EQ_ENTRY_RE.match(_dashes(str(raw)))
                if m:
                    self._add_equation(m.group(1))
            body = _dashes(row["body"] or "")
            for rx in _EQ_TAG_RES:
                for m in rx.finditer(body):
                    self._add_equation(m.group(1))
            self._add_typed_tags(body)
            for m in _INLINE_HEADING.finditer(body):
                # a section printed inside another's body ("11.4.5.1
                # Multi-Period Design Response Spectrum: ...")
                self.section_keys.add(_unified(m.group("num")))
            for entry in json.loads(row["tables_json"] or "[]"):
                num = listing_number(entry, "table")
                if num:
                    self.tables.add(table_key(num))
                    self.table_shapes.add(_shape(num))
            for entry in json.loads(row["figures_json"] or "[]"):
                num = listing_number(entry, "figure")
                if num:
                    self.figure_shapes.add(_shape(num))
        folder = reference_dir(reference)
        figs = (_catalog_rows(folder / FIGURES_CATALOG, "figures")
                if folder else None) or []
        # keyed as figure_get matches a row: UPPER(figure_number)
        self.figure_rows: dict[str, int] = {}
        self.figures = _Pool()
        for f in figs:
            num = f.get("figure_number")
            # a number of another kind (a list, an object) names nothing
            num = (_dashes(str(num)).strip().upper()
                   if isinstance(num, (str, int)) else "")
            if num:
                self.figure_rows[num] = self.figure_rows.get(num, 0) + 1
                self.figures.add(num)
                self.figure_shapes.add(_shape(num))
        tabs = (_catalog_rows(folder / TABLES_CATALOG, "tables")
                if folder else None)
        self.has_tables_catalog = tabs is not None
        # every row of a number, in catalog order ('.' and '-' alike)
        self.table_rows: dict[str, list[dict]] = {}
        for t in tabs or []:
            num = t.get("table_number")
            if isinstance(num, (str, int)) and str(num).strip():
                self.table_rows.setdefault(table_key(str(num)), []).append(t)
                self.tables.add(table_key(str(num)))
                self.table_shapes.add(_shape(str(num)))

    def _add_equation(self, number: str) -> None:
        self.equations.add(_unified(number))
        self.equation_shapes.add(_shape(number))

    def _add_typed_tags(self, body: str) -> None:
        """Equation numbers the body gives with their formula: "Pa =
        (1/2)(gamma)(h^2)(Ka) (Eq. 4-3-17)" (an '=', '~', '<=' ... between
        the tag and the tag before it, on the same line, within 300
        characters) or "Equations B-2 and B-3: AR = SAA + KA" (a colon and
        a formula right after)."""
        prev_end = 0
        for m in _EQ_TAG_INLINE.finditer(body):
            line_start = body.rfind("\n", 0, m.start()) + 1
            window = body[max(prev_end, line_start, m.start() - 300):m.start()]
            prev_end = m.end()
            if (_FORMULA_SIGN.search(window)
                    or _FORMULA_AFTER.match(body, m.end())):
                for num in [m.group("num")] + _MORE_NUM_RE.findall(
                        m.group("more")):
                    if not (len(num) == 1 and num.isalpha()):
                        self._add_equation(num)

    # -- listings ----------------------------------------------------------

    def figure_flag(self, number: str) -> str:
        """``"catalog"`` when a catalog row holds the figure as
        ``figure_get`` looks it up; ``"catalog (as 5-5)"`` when the catalog
        files the whole figure a part belongs to; else ``"not
        catalogued"``."""
        keys = figure_keys(number)
        n = max((self.figure_rows.get(k, 0) for k in keys), default=0)
        if n > 1:
            return (f"{HELD_IN_CATALOG} ({n} rows: give figure_get the "
                    "pdf_page_index)")
        if n == 1:
            return HELD_IN_CATALOG
        base = _base(keys[0])
        if base != keys[0] and self.figure_rows.get(base):
            return f"{HELD_IN_CATALOG} (as {base})"
        if keys[0] in self.figures.bases:
            parts = sorted(k for k in self.figure_rows if _base(k) == keys[0])
            return f"{HELD_IN_CATALOG} (as parts {', '.join(parts)})"
        return NOT_CATALOGUED

    def table_flag(self, number: str, section_id: str | None = None) -> str:
        """Where a table's values are, from the table catalog; ``"not
        catalogued"`` when the reference has no catalog or no row for it.

        A number on several rows (GEC-11 prints a Table 1-1 in Volume I and
        a Table 1.1 in Volume II, read alike) answers from the rows numbered
        exactly as the section lists it; of those, the row filed under the
        listing section ``section_id``, else the first in the catalog. When
        more than one row was left the answer says so: "(one of 2 rows
        numbered 1-1: table_get needs pdf_page_index 32)"."""
        rows = self.table_rows.get(table_key(number), [])
        if not rows:
            return NOT_CATALOGUED
        exact = [r for r in rows
                 if _exact_table(str(r.get("table_number"))) ==
                 _exact_table(number)]
        rows = exact or rows
        here = [r for r in rows if r.get("section_id") == section_id]
        row = (here or rows)[0]
        answer = table_values(row)
        if len(rows) > 1 and answer != NOT_CATALOGUED:
            page = row.get("pdf_page_index")
            answer += (f" (one of {len(rows)} rows numbered {number}: "
                       f"table_get needs pdf_page_index {page})")
        return answer

    # -- pointers ----------------------------------------------------------

    @staticmethod
    def _known_shape(shape: str, shapes: set[str],
                     prefix: bool = False) -> bool:
        if prefix:
            return any(s == shape or (s.startswith(shape)
                                      and s[len(shape)] in "-.")
                       for s in shapes)
        return shape in shapes

    def pointer_held(self, kind: str, number: str) -> bool | None:
        """Whether the part a same-document pointer names is held: True,
        False, or None when the number cannot be read for certain as one
        of this document's (its form is not the document's own)."""
        key = _unified(number)
        shape = _shape(number)
        if kind == "chapter":
            if not re.fullmatch(r"\d+", number) or int(number) >= 40:
                return None  # 'Chapters 4-8' is a range, not a number
            return number in self.chapters or key in self.section_keys
        if kind == "section":
            if re.fullmatch(r"\d+", number):
                if int(number) >= 100:
                    return None
                return number in self.chapters or key in self.section_keys
            lead = re.match(r"[A-Z]+", number)
            if lead and lead.group(0) not in self.section_letters:
                return None  # 'Section X.01' of a sample specification
            if not self._known_shape(shape, self.section_shapes, prefix=True):
                return None
            return key in self.section_keys or _base(key) in self.section_keys
        if kind in ("appendix", "annex"):
            letter = re.match(r"[A-Z]+", number)
            if not letter:
                return None
            letter = letter.group(0)
            for title in self.titles:
                if re.search(r"\b(?:Appendix|Appendices|Annex|Annexes)\s+"
                             + letter + r"\b", title):
                    return True
                for a, b in re.findall(
                        r"\b(?:Appendices|Annexes)\s+([A-Z])\s+to\s+([A-Z])\b",
                        title):
                    if len(letter) == 1 and a <= letter <= b:
                        return True
            return letter in self.section_keys or key in self.section_keys
        if kind == "equation":
            if (not self._known_shape(shape, self.equation_shapes)
                    or _is_range(number, self.equation_shapes)):
                return None
            return self.equations.holds(key)
        if kind == "table":
            if (not self._known_shape(shape, self.table_shapes)
                    or _is_range(number, self.table_shapes)):
                return None
            return self.tables.holds(table_key(number))
        if kind == "figure":
            if (not self._known_shape(shape, self.figure_shapes)
                    or _is_range(number, self.figure_shapes)):
                return None
            return any(self.figures.holds(k) for k in figure_keys(number))
        return None


def _exact_table(number: str) -> str:
    """A table number as table_get first looks it up: no "Table", no
    spaces, dashes as '-', a bracketed part letter plain, upper case; '.'
    and '-' kept apart (GEC-11's Table 1-1 and Table 1.1 are two
    tables)."""
    s = re.sub(r"\s+", "", _dashes(number))
    s = re.sub(r"^(?i:tables?)\.?", "", s)
    return re.sub(r"\(([A-Za-z])\)$", r"\1", s).upper()


def table_values(row: dict) -> str:
    """Where one table catalog row says the table's values are: ``"text:
    <section id>"``, ``"lookup: <function>"`` (the name
    ``lookup_reference`` takes: ``values_in`` without its module), or the
    printed page, ``"page: printed p. P (pdf_page_index N)"``. A "text" or
    "lookup" row that names nothing answers with its page; a row with no
    page either answers ``"not catalogued"``."""
    values = row.get("values")
    where = row.get("values_in")
    if isinstance(where, (list, tuple)):
        where = ", ".join(w.strip() for w in where
                          if isinstance(w, str) and w.strip())
    where = where.strip() if isinstance(where, str) else ""
    if values == "text" and where:
        return f"text: {where}"
    if values == "lookup" and where:
        return "lookup: " + ", ".join(
            w.strip().rpartition(".")[2] for w in where.split(","))
    printed, index = row.get("printed_page"), row.get("pdf_page_index")
    if not isinstance(index, int) or isinstance(index, bool) or index < 0:
        return NOT_CATALOGUED  # no page a reader could be sent to
    if (isinstance(printed, (str, int)) and not isinstance(printed, bool)
            and str(printed).strip()):
        return f"page: printed p. {printed} (pdf_page_index {index})"
    return f"page: pdf_page_index {index}"


# ---------------------------------------------------------------------------
# Pointers in a body
# ---------------------------------------------------------------------------

_KINDS = {
    "Section": "section", "Sections": "section", "Sec.": "section",
    "Secs.": "section", "\u00a7": "section", "\u00a7\u00a7": "section",
    "Chapter": "chapter", "Chapters": "chapter", "Ch.": "chapter",
    "Appendix": "appendix", "Appendices": "appendix", "App.": "appendix",
    "Annex": "annex", "Annexes": "annex",
    "Table": "table", "Tables": "table",
    "Figure": "figure", "Figures": "figure", "Fig.": "figure",
    "Figs.": "figure",
    "Equation": "equation", "Equations": "equation", "Eq.": "equation",
    "Eqs.": "equation", "Eq": "equation", "Eqs": "equation",
}
_KIND_WORD = {"section": "Section", "chapter": "Chapter",
              "appendix": "Appendix", "annex": "Annex", "table": "Table",
              "figure": "Figure", "equation": "Eq."}
_PTR_NUM = r"(?:[A-Z]{1,2}[-.]?)?\d+(?:[-.]\d+)*[a-z]?|[A-Z](?![A-Za-z0-9])"
_SEP = (r"[ \t\u00a0]*(?:,[ \t\u00a0]*(?:and|or)?|and|or|to|through|&|/|"
        r"\.\.)[ \t\u00a0]*")
_POINTER_RE = re.compile(
    r"(?<![A-Za-z])(?P<kind>"
    + "|".join(re.escape(k) for k in sorted(_KINDS, key=len, reverse=True))
    + r")[ \t\u00a0]*\(?(?P<num>" + _PTR_NUM + r")\)?(?![\dA-Za-z])"
    + r"(?P<more>(?:" + _SEP + r"\(?(?:" + _PTR_NUM
    + r")\)?(?![\dA-Za-z]))*)")
_MORE_NUM_RE = re.compile(_PTR_NUM)
#: Another document named just before a pointer.
_OTHER_DOCUMENT = re.compile(
    r"\b(?:ACI|ASCE|IBC|IEBC|IRC|AISC|ASTM|NDS|TMS|AWS|ANSI|AASHTO|NCHRP|"
    r"AREMA|PCI|PTI|API|ISO|BS|DIN|CFR|OSHA|NEHRP|FEMA|USACE|USBR|NAVFAC|"
    r"UFC|UFGS|UFS|DM ?7|TM|EM|ER|ETL|EN|HEC|GEC|FHWA|NHI|Caltrans|"
    r"MIL|CRD|SHRP|Eurocode|Article|Articles|Subpart|Part \d|"
    r"Code|Specifications?|Standard|Manual of|Guide Specifications?)\b")
#: A named work just before a pointer ("Falsework Manual Section 5-2").
_NAMED_WORK_BEFORE = re.compile(
    r"\b(?:Manual|Guide|Handbook|Provisions|Report|Specification|Standard|"
    r"Circular|Bulletin|Memorandum)s?\s*,?\s*$")
#: A title right after an appendix letter: a contents list, not a pointer.
_TITLE_AFTER = re.compile(
    r"[ \t]+(?:-[ \t]+[A-Z]|[A-Z][a-z]+[ \t]+[A-Z][a-z]+)")
#: An author and year just before a pointer ("Wilson et al. (2006) Figure").
_YEAR_BEFORE = re.compile(r"(?:19|20)\d\d[a-z]?\)?[,;]?\s*$")
#: A pointer followed by "of / in / from" another named document or work.
_OF_OTHER = re.compile(
    r"^\s*,?\s*(?:of|in|from)\s+(?!this\b|these\b|the\s+(?:present\s+)?"
    r"(?:manual|guide|report|document|circular|chapter|section|appendix|"
    r"annex|text|volume)\b)(?:the\s+)?(?:[A-Z]|\d{4})")


def iter_pointers(body: str, holdings: Holdings):
    """``(kind, number, start, end, held)`` for each pointer in ``body``
    read as one into the same document (``held`` True, False, or None
    when the number is not certainly one of the document's own)."""
    text = _dashes(body or "")
    for m in _POINTER_RE.finditer(text):
        kind = _KINDS[m.group("kind")]
        line_start = text.rfind("\n", 0, m.start()) + 1
        before = text[max(line_start, m.start() - 60):m.start()]
        if (_OTHER_DOCUMENT.search(before) or _YEAR_BEFORE.search(before)
                or _NAMED_WORK_BEFORE.search(before)):
            continue
        after = text[m.end():m.end() + 60]
        if _OF_OTHER.match(after):
            continue
        # a number split across a line ("Table 4-\n12", "Equation 2- 20")
        if re.match(r"-[ \t]+\d|[-.][ \t]*\n",
                    text[m.end("num"):m.end("num") + 4]):
            continue
        first = m.group("num")
        # the numbers after the first are its list ("Tables 7-1, 7-2"), not
        # a value that follows ("in Eq. 10-1, 1.0 for compression")
        numbers = [first] + [n for n in _MORE_NUM_RE.findall(m.group("more"))
                             if _seps(n) == _seps(first)]
        if kind in ("appendix", "annex") and _TITLE_AFTER.match(
                text, m.end("num")):
            # another document's contents ("Appendix A - Boring Location
            # Plan", "Appendices A Field Investigation Plan, B ...")
            continue
        for num in numbers:
            if (len(num) == 1 and num.isalpha()
                    and kind not in ("appendix", "annex")):
                continue
            if num.startswith("0."):
                continue  # a value ("or 0.56/S_u"), not a number of a part
            yield (kind, num, m.start(), m.end(),
                   holdings.pointer_held(kind, num))


def pointers_not_held(body: str, holdings: Holdings) -> list[str]:
    """The same-document pointers in ``body`` whose target ``holdings``
    does not hold, each as "<Kind> <number>", in order, once each."""
    out: list[str] = []
    for kind, num, _, _, held in iter_pointers(body, holdings):
        if held is False:
            label = f"{_KIND_WORD[kind]} {num}"
            if label not in out:
                out.append(label)
    return out


# ---------------------------------------------------------------------------
# The flags, built with the database and read back on a fetch
# ---------------------------------------------------------------------------

def collapse(held: dict[str, str]) -> dict[str, str]:
    """A ``figures_held`` / ``tables_held`` map in the short form fetches
    carry: ``{"all": v}`` when every number has the same answer, else the
    numbers whose answer differs from the commonest one plus ``"others":
    <the commonest answer>`` (when two or more share it). A section listing
    60 figures in the catalog would otherwise repeat "catalog" 60 times
    and push the largest fetches past the 14,000-character budget."""
    if not held:
        return held
    values = list(held.values())
    # a tie goes to the first answer in sorted order, not to hash order
    common = max(sorted(set(values)), key=values.count)
    n = values.count(common)
    if n == len(values):
        return {"all": common}
    if n < 2:
        return dict(held)
    out = {k: v for k, v in held.items() if v != common}
    out["others"] = common
    return out


def expand(short: dict[str, str], numbers: list[str]) -> dict[str, str]:
    """The ``{number: answer}`` map a :func:`collapse` short form stands for,
    given the numbers the section lists (in its order)."""
    if "all" in short:
        return {n: short["all"] for n in numbers}
    return {n: short.get(n, short.get("others", NOT_CATALOGUED))
            for n in numbers}


def listed_numbers(entries: list, kind: str) -> list[str]:
    """The numbers a ``figures`` / ``tables`` list names, once each."""
    out: list[str] = []
    for entry in entries or []:
        num = listing_number(entry, kind)
        if num and num not in out:
            out.append(num)
    return out


def section_flags(row: sqlite3.Row, holdings: Holdings,
                  short: bool = True) -> dict[str, Any]:
    """The flags of one section row: ``figures_held``, ``tables_held``,
    ``not_held``, each only when there is something in it; the held maps in
    the :func:`collapse` form unless ``short`` is False."""
    out: dict[str, Any] = {}
    figs = {num: holdings.figure_flag(num) for num in listed_numbers(
        json.loads(row["figures_json"] or "[]"), "figure")}
    if figs:
        out["figures_held"] = collapse(figs) if short else figs
    tabs = {num: holdings.table_flag(num, row["section_id"])
            for num in listed_numbers(json.loads(row["tables_json"] or "[]"),
                                      "table")}
    if tabs:
        out["tables_held"] = collapse(tabs) if short else tabs
    # the whole list is stored; a fetch shows NOT_HELD_MAX (add_flags)
    missing = pointers_not_held(row["body"] or "", holdings)
    if missing:
        out["not_held"] = missing
    return out


def _shown(flags: dict) -> dict:
    """``flags`` as a fetch shows them: ``not_held`` cut to
    :data:`NOT_HELD_MAX` entries and "and N more"."""
    missing = flags.get("not_held")
    if not missing or len(missing) <= NOT_HELD_MAX:
        return flags
    return dict(flags, not_held=missing[:NOT_HELD_MAX] + [
        f"and {len(missing) - NOT_HELD_MAX} more"])


def fill_reach_table(cur: sqlite3.Cursor) -> None:
    """Work out every section's flags from the ``sections`` table just
    filled and the reference's catalogs, into ``section_reach``."""
    cur.execute("CREATE TABLE section_reach (sec_rowid INTEGER PRIMARY KEY,"
                " reach_json TEXT NOT NULL)")
    refs = [r[0] for r in cur.execute(
        "SELECT DISTINCT reference FROM sections ORDER BY reference")]
    old_factory = cur.connection.row_factory
    cur.connection.row_factory = sqlite3.Row
    try:
        for ref in refs:
            rows = cur.connection.execute(
                "SELECT rowid, reference, chapter, chapter_title, section_id,"
                " body, equations_json, figures_json, tables_json "
                "FROM sections WHERE reference = ? ORDER BY rowid",
                (ref,)).fetchall()
            try:
                holdings = Holdings(ref, rows)
                batch = []
                for row in rows:
                    flags = section_flags(row, holdings)
                    if flags:
                        batch.append((row["rowid"],
                                      json.dumps(flags, ensure_ascii=False)))
            except Exception:  # noqa: BLE001
                if not str(ref).startswith(_packs.PACK_PREFIX):
                    raise
                # a local pack the flags cannot read keeps its search and
                # fetches, without flags
                continue
            cur.executemany("INSERT INTO section_reach VALUES (?, ?)", batch)
    finally:
        cur.connection.row_factory = old_factory


def chapter_flags(conn: sqlite3.Connection, reference: str,
                  chapter) -> dict[str, dict]:
    """``{section_id: flags}`` for one chapter file of a reference (the
    first section of a number, as the fetches resolve it). Empty for a
    database built before the flags existed."""
    try:
        rows = conn.execute(
            "SELECT s.section_id, r.reach_json FROM sections s "
            "JOIN section_reach r ON r.sec_rowid = s.rowid "
            "WHERE s.reference = ? AND s.chapter = ? ORDER BY s.rowid",
            (reference, chapter)).fetchall()
    except sqlite3.OperationalError:
        return {}
    out: dict[str, dict] = {}
    for sid, flags in rows:
        out.setdefault(sid, json.loads(flags))
    return out


def add_flags(section: dict, table: dict[str, dict]) -> dict:
    """``section`` with the flags ``table`` (:func:`chapter_flags`) holds
    for its number; the section itself when there are none."""
    flags = table.get(section.get("section_id"))
    if not flags:
        return section
    out = dict(section)
    out.update(copy.deepcopy(_shown(flags)))  # the table may be cached
    return out


def tree_with_flags(sections: list[dict], table: dict[str, dict]
                    ) -> list[dict]:
    """Subsections to be inlined, each with its flags, at every level (the
    note of the fetch explains them once, :func:`with_notes`)."""
    out = []
    for sec in sections:
        sec = add_flags(sec, table)
        if sec.get("subsections"):
            sec = dict(sec, subsections=tree_with_flags(sec["subsections"],
                                                        table))
        out.append(sec)
    return out


def _figure_kind(answer: str) -> str:
    if answer.startswith(f"{HELD_IN_CATALOG} (") and "rows" in answer:
        return "rows"
    if answer.startswith(f"{HELD_IN_CATALOG} (as"):
        return "as"
    return answer if answer in FIGURE_ANSWERS else ""


def _table_kind(answer: str) -> str:
    kind = answer.split(":", 1)[0]
    return kind if kind in TABLE_ANSWERS else ""


def reach_note(section: dict) -> str:
    """The sentences a fetch's ``note`` gets for the keys it carries (at
    its top or in an inlined subsection): what ``figures_held`` and
    ``tables_held`` answer, each answer the fetch carries explained, and
    :data:`NOT_HELD_NOTE` for ``not_held``. Empty when it carries none."""
    figures: list[str] = []
    tables: list[str] = []
    short = has_not_held = rows = False
    for sec in [section] + list(_inlined(section.get("subsections"))):
        for key, kinds, kind_of in (("figures_held", figures, _figure_kind),
                                    ("tables_held", tables, _table_kind)):
            held = sec.get(key) or {}
            short = short or "others" in held
            rows = rows or any(" (one of " in str(v) for v in held.values())
            for answer in held.values():
                kind = kind_of(str(answer))
                if kind and kind not in kinds:
                    kinds.append(kind)
        has_not_held = has_not_held or "not_held" in sec
    out = []
    if figures:
        out.append("figures_held, for each listed figure: "
                   + "; ".join(FIGURE_ANSWERS[k] for k in FIGURE_ANSWERS
                               if k in figures) + ".")
    if tables:
        out.append("tables_held, where each listed table's values are: "
                   + "; ".join(TABLE_ANSWERS[k] for k in TABLE_ANSWERS
                               if k in tables) + ".")
    if short:
        out.append(SHORT_NOTE)
    if rows:
        out.append(ROWS_NOTE)
    if any(k in figures for k in ("catalog", "rows", "as")) \
            or "page" in tables:
        out.append(PAGE_NOTE)
    if has_not_held:
        out.append(NOT_HELD_NOTE)
    return " ".join(out)


def _inlined(sections):
    for sec in sections or []:
        yield sec
        yield from _inlined(sec.get("subsections"))


def with_notes(section: dict) -> dict:
    """``section`` with :func:`reach_note` added to its ``note``, unless
    the whole would pass :data:`NOTE_BUDGET_CHARS` (the keys then speak
    for themselves)."""
    note = reach_note(section)
    if not note:
        return section
    out = dict(section)
    out["note"] = (str(out.get("note") or "") + " " + note).strip()
    if len(json.dumps(out, default=str)) > NOTE_BUDGET_CHARS:
        return section
    return out


def fetch_result(view: dict, subtree: list[dict] | None,
                 table: dict[str, dict]) -> dict:
    """A fetched section as both fetches return it: ``view`` (the section
    with ``parent_id``, ``under`` and ``children``) with its flags from
    ``table`` (:func:`chapter_flags`); ``subtree`` (its subsections, None
    when they were not asked for) inlined with theirs; and the ``note``
    saying what the keys and answers mean (:func:`reach_note`).

    Whether the subsections are inlined is decided on the content without
    the flags, by the 12,000-character rule as before them
    (``_retrieval.inline_subsections``), provided the whole result with
    the flags and the note still fits :data:`INLINE_WITH_FLAGS_MAX_CHARS`
    (2026-11-12 review, item 5: counting the flags in the 12,000 had
    stopped twelve fetches that fitted from inlining)."""
    from ._retrieval import inline_subsections
    out = add_flags(view, table)
    if subtree is None:
        return with_notes(out)
    bare = inline_subsections(view, subtree)
    if "subsections" in bare:
        trial = with_notes(dict(out, subsections=tree_with_flags(subtree,
                                                                 table)))
        size = len(json.dumps(trial, default=str))
        if size <= INLINE_WITH_FLAGS_MAX_CHARS:
            return trial
        out = dict(out, note=(
            f"Subsections not inlined: with them and what they reach this "
            f"section is {size:,} characters, over the "
            f"{INLINE_WITH_FLAGS_MAX_CHARS:,}-character limit. Fetch the "
            "one you need by its section_id from 'children'."))
    elif bare.get("note") != view.get("note"):
        out = dict(out, note=bare["note"])  # over the 12,000 without flags
    return with_notes(out)


#: The most a fetch with its subsections inlined may come to with the
#: flags and their note (the library's budget; the app's cap is 16,000).
INLINE_WITH_FLAGS_MAX_CHARS = 14000


@functools.lru_cache(maxsize=256)
def _cached_chapter_flags(db: str, stamp: int, reference: str,
                          chapter) -> dict[str, dict]:
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return chapter_flags(conn, reference, chapter)
    finally:
        conn.close()


def flags_for(reference: str, chapter) -> dict[str, dict]:
    """:func:`chapter_flags` from the text search database, built first if
    it must be; the chapter-file fetch (``_retrieval.retrieve_section``)
    reads its flags this way. Empty when the database cannot be built or
    opened: the fetch then works as it did before the flags.

    Whether the database is current (a stat of every source file, ~35 ms)
    is checked at most once every :data:`CHECK_SECONDS` per database, so a
    loop over many sections does not pay it on every fetch."""
    from . import _retrieval_db
    try:
        key = str(_retrieval_db._db_path())
        now = time.monotonic()
        seen = _CHECKED.get(key)
        if seen and now - seen[0] < CHECK_SECONDS and seen[1].exists():
            db = seen[1]
        else:
            db = _retrieval_db._ensure_db()
            _CHECKED[key] = (now, db)
        stamp = db.stat().st_mtime_ns
        return _cached_chapter_flags(str(db), stamp, reference, chapter)
    except Exception:  # noqa: BLE001 -- the fetch must not fail on flags
        return {}


#: How long (seconds) :func:`flags_for` trusts its last check that the
#: database is current.
CHECK_SECONDS = 2.0
_CHECKED: dict[str, tuple[float, Path]] = {}


def reach_items() -> dict[str, dict[str, list[str]]]:
    """Per reference, what a fetch tells the helper of that it cannot
    reach, item by item: ``{reference: {"figures_not_catalogued": [...],
    "tables_not_catalogued": [...], "pointers_not_held": [...]}}``, each
    item "<section_id>: <number or pointer>", sorted, from the text search
    database. The standing test (``tests/test_reach.py``) holds them to
    ``tests/reach_baseline.json`` item by item, so one fixed and one
    broken cannot cancel out (2026-11-12 review, item 6)."""
    from . import _retrieval_db
    conn = _retrieval_db._ro_connect()
    try:
        rows = conn.execute(
            "SELECT s.reference, s.section_id, s.figures_json, s.tables_json,"
            " r.reach_json FROM sections s JOIN section_reach r "
            "ON r.sec_rowid = s.rowid ORDER BY s.rowid").fetchall()
        refs = [r[0] for r in conn.execute(
            "SELECT DISTINCT reference FROM sections ORDER BY reference")]
    finally:
        conn.close()
    out = {ref: {"figures_not_catalogued": [], "tables_not_catalogued": [],
                 "pointers_not_held": []} for ref in refs}
    for ref, sid, figs, tabs, flags in rows:
        flags = json.loads(flags)
        items = out[ref]
        for key, listing, kind in (("figures_held", figs, "figure"),
                                   ("tables_held", tabs, "table")):
            if key in flags:
                held = expand(flags[key], listed_numbers(
                    json.loads(listing or "[]"), kind))
                items[f"{kind}s_not_catalogued"] += [
                    f"{sid}: {num}" for num, v in held.items()
                    if v == NOT_CATALOGUED]
        items["pointers_not_held"] += [f"{sid}: {label}"
                                       for label in flags.get("not_held", [])]
    for items in out.values():
        for key in items:
            items[key] = sorted(set(items[key]))
    return out


def reach_counts() -> dict[str, dict[str, int]]:
    """Per reference, how many listed figures and tables are not
    catalogued and how many same-document pointers the library does not
    hold (the lengths of :func:`reach_items`)."""
    return {ref: {key: len(v) for key, v in items.items()}
            for ref, items in reach_items().items()}


def all_flags() -> dict[tuple, dict]:
    """``{(reference, chapter, section_id): flags}`` for every section with
    flags, from the text search database (the standing test reads this)."""
    from . import _retrieval_db
    conn = _retrieval_db._ro_connect()
    try:
        rows = conn.execute(
            "SELECT s.reference, s.chapter, s.section_id, r.reach_json "
            "FROM sections s JOIN section_reach r ON r.sec_rowid = s.rowid "
            "ORDER BY s.rowid").fetchall()
    finally:
        conn.close()
    out: dict[tuple, dict] = {}
    for ref, chapter, sid, flags in rows:
        out.setdefault((ref, chapter, sid), json.loads(flags))
    return out
