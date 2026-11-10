# Changelog

Releases before 1.6.0 are described in their release commits (`git log`).

## Unreleased

**Fixes from the 2026-11-10 review of the core layer.** Every page, number
and caption below was read off the rendered print.

- **A section number names one section** (core-01, core-08). Twenty-two
  numbers were held by two sections of one reference, and the two fetch
  layers returned different ones. GEC-13 chapter 1 is now numbered
  `1.<printed number>`, the AASHTO 1993 Guide's numbers carry their Part
  (`II-2.3.5`), and UFC 3-250-11's appendices are `A-1`, `B-1` and `C` as
  printed. Both fetches refuse a number two sections hold, and a
  `section_id` that is not text (7.10 sent as a number arrived as 7.1).
- **A figure number the catalog holds twice is never the first row**
  (core-02). `figure_get` and `resolve_pdf` take `pdf_page_index`, and a
  repeated number is refused without it, naming each row's page. GEC-11
  Figure 5-11 had been catalogued as a second 5-14, and GEC-12's Appendix D
  continuation sheets each had the first sheet's page.
- **`_linterp` refuses a NaN or infinite input** (core-04).
- **Search results say how they matched** (core-05). `reference_search` and
  `figure_search` hits that do not hold every word carry `match`
  (`"synonyms"`, or `"any word"` with `lacks`). This is worked out after the
  ranking, so no hit moves. With `max_chars` the result adds `matched`,
  `words_not_found` and a sentence on the note. An empty result names the
  scope, what was tried and the words nothing there holds.
- **An unknown reference or chapter is an error, and a reference name means
  one thing** (core-06, core-09). A search scoped to either returned `[]`.
  A figure lookup no longer reads a loose name ("FHWA", "pile") as every
  catalog it touches.
- **`search_sections` with no section holding every word** (core-07) returns
  the ranked search of that reference, each hit marked `match` ("all
  words", "synonyms", "any word" with `lacks`), 10 by default. The fitted
  result has no `total_hits`. A search that finds hits is unchanged.
- **A skipped local pack is named** (core-10). `list_indexed_references`
  gives a partly skipped pack its `problems`. It lists a pack skipped whole
  with no sections and its problems, and a search naming that pack quotes
  them. A manual whose volumes' files carry titles of their own is listed
  once, with `reference_titles`.
- **A database knows what it was built from** (core-11). Both search
  databases store a signature of their source files and are rebuilt when it
  differs. Before, a chapter file or catalog that was deleted, added or
  restored with an older date kept the old text. The text layout version
  is 3; the figures database has `user_version` 1.
- **An unreadable built-in source fails the build** (core-12), naming the
  file and keeping the database already there. A local pack's file is still
  skipped and named.
- **Each volume is cited by its own cover's number** (core-13). GEC-11 Vol
  II rows are FHWA-NHI-10-025, GEC-12 Vol III rows and Appendix D are
  FHWA-NHI-16-064, and Soils and Foundations Vol II rows are
  FHWA-NHI-06-089. GEC-13 chapter 6's title says Volume II. GEC-12 Vol II is
  unchanged: its cover prints 16-009 and its documentation page 16-010.
- **`load_chapter` finds a chapter file by its `chapter` field** (core-15),
  so the 17 files named otherwise (prologues, appendices, Eurocode 7 Part 2
  sections) load.
- **Catalog rows lead to their figure.**
  - Pages corrected: UFS 3-220-10 Figures 1-13, 3-1, 5-4, 6-9 (the figure
    is on the page before its caption), GEC-10 4-5, GEC-14 A-1 to A-3 and
    GEC-9 6-17.
  - Numbers as printed: UFC 3-250-01 C14-5B, and D-3 as four sheets.
    `figure_get` reads a bracketed part letter, so "Figure 9-37(a)" finds
    `9-37a`.
  - Chapters filled in: GEC-7 and GEC-8 rows had none, and GEC-4 rows had
    their own figure number as the chapter.

## 1.6.0

**Local reference packs (REF-64).** A deployment can add its own references
in the library's structured format without putting them in the public
repository or the wheel.

- Set `GEOTECH_REFERENCES_PACKS` to a pack folder or a folder of packs
  (several separated by `os.pathsep`). Each pack holds `pack.json`,
  `text/chapterNN.json` (the chapter schema the built-ins use) and
  optionally `figures_catalog.json` and its PDF. Pack ids start with
  `local_`. Packs hold no code.
- `reference_search`, `reference_get`, `reference_query`,
  `list_indexed_references`, `figure_search`, `figure_get`, `resolve_pdf`
  and the file-based `retrieve_section` family cover packs beside the
  built-in references, with the same ranking and synonym expansion.
- A pack names its PDFs by bare file name only (`pdf_files`, a catalog's
  `pdf_path`). For a pack figure, `resolve_pdf` looks in the pack folder,
  then `GEOTECH_REFERENCES_DOCS`, then raises `FileNotFoundError`; no path
  read from a pack leads outside those folders, and `figure_get` never
  returns a host path for a pack figure.
- A bad pack file cannot break search. A chapter file or catalog the
  indexes cannot take (unreadable JSON, a list or an object where text
  belongs, a PDF named by a path) is skipped and named in
  `_packs.problems()`. Each pack file is indexed under its own SQLite
  savepoint, so one that fails anyway is rolled back while the built-ins
  and the other packs still index.
- The search databases are keyed by the pack set as well as the package
  copy. With the setting unset, every key, every database and every result
  is unchanged.
- A figure catalog may give any figure two optional fields: `bbox` (the
  chart's box on the page, PDF points, top-left origin) and `read_notes` (at
  most 500 characters on how to read it). `figure_get` returns them where
  given; built-in figures carry neither.
- New: `python -m geotech_references.packs new|check|list|index|schema`.
  `check` exits 0 or 1. It checks the schema and the type of every field
  (reported as errors, never tracebacks), the catalog, pages and boxes
  against the PDF with PyMuPDF, print-fidelity warnings and a search smoke
  test. It refuses a pack inside the package or a public repository's work
  tree. `schema` prints the chapter-file schema.
- `chapter_schema.json` moved from `scripts/` into the package and ships in
  the wheel.
- Also new: `scripts/build_figure_catalog.py --pack`,
  `_packs.pack_records()` for build records, and `docs/REFERENCE_PACKS.md`
  (the format, the print-fidelity rules, a minimal chapter file, where packs
  live on each host).
- The chapter schema check moved from `scripts/audit_chapter_text.py` into
  `geotech_references/_schema.py`. The script imports it, and its results
  are unchanged.
