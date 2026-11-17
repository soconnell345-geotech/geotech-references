# Maintaining geotech-references

For whoever maintains the library. How to release: `RELEASING.md`. The detailed
rules for building and checking content: `scripts/REVIEW_RULES.md`; read them
before you build or check anything.

## What the library holds

`geotech_references` is a Python package of 34 digitised geotechnical manuals.
It serves engineers directly, and an LLM helper that searches and quotes it. A
wrong stored number reaches an engineer's answer and nothing downstream catches
it, so the printed page is the only authority.

Each reference's folder, `geotech_references/<id>/`, holds four kinds:

- **Lookups** (`tables.py`, `figures.py`, `equations.py` or `chapterN.py`):
  functions named after the printed item (`table_5_4_...`, `figure_7_10_...`).
  A lookup returns what its page prints and refuses outside the printed range.
  A dict result carries `units`, `printed_page` and `pdf_page_index` (0-based);
  a bare number gives its unit and page in its docstring.
- **Chapter text** (`text/chapterNN.json`, one file per chapter): each section
  has `body`, `key_points`, `equations`, `figures`, `tables` and
  `applicability`. The schema is `geotech_references/chapter_schema.json`.
- **Table catalog** (`tables_catalog.json`): one row per printed table, saying
  where its values are: `text` (typed into a section), `lookup` (a function
  returns them) or `page` (only on the printed page). In November 2026 the
  catalogs held 2,099 rows: 770 text, 254 lookup, 1,075 page.
- **Figure catalog** (`figures_catalog.json`): each printed figure's page.

Shared code sits at the package root: `_retrieval.py` and `_query_expansion.py`
(search), `_tables_db.py` and `_figures_db.py` (the catalogs), `_reach.py`
(what a fetched section can reach), `_units.py` (units and conversions) and
`_packs.py` (local reference packs). `scripts/` holds the builders, the checks
and one manifest per reference (`scripts/manifests/<id>.json`: the PDF and its
page ranges). `agents/` (agent wrappers) and `docs/` (the source PDFs) are not
in the wheel. GeotechStaffEngineer uses the library as a git submodule
(`geotech-references/`) and as a PyPI requirement.

## How content is added and checked

Every item is built by one person or session and then checked by another who
did not build it. The checker reads the rendered page, not the builder's notes.

### A reference

1. **The PDF** goes in `docs/`: a public document (owner's rules below). One
   over 100 MB (GitHub's limit) stays local, in `.gitignore`.
2. **The manifest** `scripts/manifests/<id>.json` gives `pdf_path`, `package`,
   and the chapters with their page ranges. State the offset between the PDF
   page index and the printed page.
3. **The package** `geotech_references/<id>/`: chapter text read off each page
   (`scripts/build_chapter_text.py`; see `scripts/README.md`), or built by
   script from the PDF (`scripts/build_printed_text.py`; the manifest then has
   `"text_build"`, and a test rebuilds the text under the PyMuPDF version the
   manifest records).
4. **Audit, then catalogs** (all in `scripts/`): `audit_chapter_text.py <id>`,
   then `build_table_catalog.py <id>` and `build_figure_catalog.py <id>`.
5. **The independent check** (REVIEW_RULES 14 to 18): every value an engineer
   copies and every "[as printed ...]" note, plus a seeded sample of prose.

### A typed table

1. **Type it in** as `Table N: caption (p. <printed page>) - columns: A; B.`,
   then the rows (`row1 A; row1 B | row2 A; row2 B`), then the printed notes.
   " | " separates rows and "; " separates cells, so a semicolon inside a cell
   (printed, or in a note) is written ", ", and a typist's note reads
   "[as printed, ...]". An empty cell stays empty, and every row holds as many
   cells as its table has columns.
2. **Pin the cells in a test** (`tests/test_<id>_typed_tables*.py`), asserting
   printed values.
3. **Rebuild the catalog:** `python scripts/build_table_catalog.py <id>`, then
   the same command with `--verify <id>`. The builder marks a table `text`
   when the section's cells match the page's text layer.
   A table that is right on the render but that the cell check cannot count (a
   picture, subscripts, no numbers) goes under `text_by_render` in that
   reference's `CONFIG` entry, with a comment on what the render showed; a table
   printed on more than one page lists its pages under `pages_from_render`.
4. **The check:** a script compares every typed cell with the page's words in
   order (numbers, signs, ranges); the checker reads on a 200 dpi render
   whatever the script cannot settle, and counts each row's cells.

### A worked example

Typed into its section as printed, line by line, with its arithmetic. A test
calls the lookups with the printed inputs and asserts the printed results to
the print's rounding. The checker recomputes every line; a printed slip is kept
with an "[as printed, ...]" note.

### A lookup

It is named after its printed item and returns what is printed; outside the
printed range it refuses, naming the range and the page. Anything the library
adds itself (a limit, a reading of an ambiguous page) is labelled as the
library's reading. Its References line has "printed p. X (pdf_page_index N)"
within its first 160 characters. A US-unit lookup that would silently accept an
SI number takes `unit_system="SI"` (inputs converted, printed units returned).
Its tests assert printed values; any other test data is made up.

## Tests

```
pip install -e ".[plot]" pytest pymupdf==1.27.2.3
python -m pytest -q -p no:cacheprovider
```

- **Skips:** a test that reads a PDF skips when `docs/` lacks it; a
  text-rebuild test skips under another PyMuPDF
  (`GEOTECH_REQUIRE_BUILD_READER=1` fails instead).
- **On GitHub:** `.github/workflows/tests.yml` runs on every push to `main` and
  `ci/**`, in two jobs (Python 3.10 with the recorded PyMuPDF, 3.12 with the
  newest), in about 12 minutes. A push that changes only `.md` files starts no
  run. Locally, run only the test files your change touches.
- **Worth knowing:** `test_reach.py`, `test_tables_db.py`,
  `test_table_catalog_rows.py`, `test_table_printed_pages.py`,
  `test_cover_citations.py`, `test_build_reader.py`,
  `test_result_convention_wave1*.py`.

## The owner's rules

1. **The print is the only authority:** every value, equation, default and
   curve traces to a printed page, never to memory, another source or another
   edition.
2. **As printed, in the references' own terms:** units, symbols, notes,
   "should" and "must" as printed, and no coined terms. A printed error is
   kept, with an "[as printed, ...]" note. Nothing is shortened to fit a size
   limit; a long section is split into lettered parts.
3. **The repository is public:** only public source documents (government
   publications, and the three openly available standards named in the README),
   never a private, client or project document, nor a name or value from one.
   Test data that is not printed is made up.
4. **A release needs the owner's word** (`RELEASING.md`).

## Open work

All open work is in one list, `BACKLOG.md` in the GeotechStaffEngineer
repository (section 8, `REF-nn`); add new items there, never here. The main
ones in November 2026:

- **REF-112:** three branches held for a later release, each rebuilding chapter
  text from the print and needing an independent check before it merges:
  `build/dm72-bodies` (REF-94, DM 7.2 section bodies; resolve its conflicts
  with `main` first), `build/gec11text` (GEC-11 Appendix E examples),
  `build/pavetext` (REF-83, pavement manuals and AASHTO 1993).
- **REF-97:** 1,075 tables whose values are only on the printed page. Type them
  in, most used first.
- **REF-78:** result units and pages, waves 2 and 3: about 576 lookups in the
  structural and remaining references.
- **REF-83 to REF-87:** chapter text never checked; figures, chapters and
  appendices with no entry; equations outside the search; the helper's call
  budgets measured again on a host without the PDFs.
