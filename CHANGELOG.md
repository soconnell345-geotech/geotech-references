# Changelog

Releases before 1.6.0 are described in their release commits (`git log`).

## Unreleased

**EM 1110-1-1905, Geotechnical Design of Shallow Foundations on Soils
(U.S. Army Corps of Engineers, 31 July 2025), as package `em_1905`.**

- Chapter text read off the print: chapters 1-12, and Appendices B
  (design examples, ultimate limit states), C (design examples,
  settlement) and D (unit conversion factors) as chapters 13-15; 778
  sections, each body in the print's own wording with page markers, and
  all 213 numbered equations typed in from the rendered page with their
  symbols and units. Figure catalog: all 136 figures, each on the page
  that prints its caption.
- Build: each of the 475 formula lines of Appendices B and C was read
  against the rendered page. The 40 the placement rules had read wrongly
  (a power left off, a denominator stacked on a line of its own,
  subscripts spaced off their symbols, two lines run into one, "pf" where
  the page prints "bpf") are typed in from the page in the manifest
  (`printed_passages`), each checked by its letters and digits, and each
  result recomputed from the line as stored. Among them: Example C-3,
  Step 4 (p. 359), whose time line had lost the square on the drainage
  path (as read it gave 12.2 days, not the printed 152.8); Example C-7,
  Steps 6 and 7 (p. 384); Eq. 7-10 as quoted in Examples C-6 and C-7; the
  equivalent bearing pressure of Example B-2 (p. 301). A total or
  sub-heading beside a table stands once, not on every row. Eight more
  slips of the print are kept as printed with a note (Examples B-1, B-4,
  B-5, B-6, C-2 and C-6, Table 3-15, the symbol list of Eqs. 8-27 and
  8-28). Table 3-8's σ′v (the page sets a raised semicolon for the prime)
  and Table 4-10's E*0 (the text layer holds a capital O) are typed in; the
  symbol lists of Eqs. 3-17, 7-3b, 7-4, 7-6, 7-11, 7-12 and 8-2 give every
  symbol the formula prints; an equation printed straight after another
  is described as printed after it, not by the other's formula (Eq. 5-3);
  the Figure List keeps a word broken after its own hyphen whole
  ("per-inch", "1-D"); a split leaves room for the notes placed after it
  (C-2b is in two parts). A test looks through every chapter
  for formula pieces put back in the wrong places (a prime alone, a lone
  number above a formula, a number doubled from a stacked fraction, a
  subscript spaced off its symbol, brackets that do not pair).
- Lookups in the manual's US units, 66 functions: `tables` (Tables 2-1,
  5-2 to 5-5 and 7-6), `equations` (Chapter 5, Eqs. 5-1 to 5-36),
  `settlement` (Chapters 6 and 7, Eqs. 6-1 to 6-13 and 7-1 to 7-47) and
  `figures` (the table printed on Figure 7-16). Each returns a dict with
  `units`, `source` (the printed page), `valid_for` and `notes`, and
  raises ValueError outside what the print covers. A limit printed as part
  of a relation is applied as printed (USACE dc <= 1.5, AASHTO dq <= 1.4,
  Pa,d >= 0, C1 >= 0.5): the limited value comes back with the formula's
  value beside it and `limit_governs`. sigma'p < sigma'zo, outside the
  conditions printed beside Eqs. 7-7 to 7-9 (pp. 159-160), is refused, the
  message naming them and the page. Some refusals rest on no printed
  condition, and their messages and docstrings say they are the library's
  reading: beta > phi' (Table 5-3, USACE), tan(beta) > 1 (Table 5-3,
  AASHTO), t < 3 years (Eq. 7-34; p. 178 says only that R3 covers the
  first 3 years), a void ratio that rises (Eqs. 7-5, 7-6, 7-46) and q <
  sigma'zD in the settlement equations. A correction factor of Tables 5-3
  and 5-4 that computes negative is refused with its value, one of exactly
  zero returned with a note; Eqs. 6-5 and 6-6 return a negative net
  pressure flagged `net_negative`. Eq. 7-43 returns Cv in in^2/day and
  ft^2/day; Eq. 7-42 takes ft^2/day (`cv_ft2_per_day`). Eqs. 5-34/5-35
  keep the printed 2c'd without the square root of K (noted); Eqs. 7-7 to
  7-10 return feet and inches, as the examples convert. The worked
  examples' slips (in Examples B-1, B-4 to B-6 and C-2 to C-7) are
  kept as printed in the text, each with a note giving what the inputs
  give, and the tests pin what the inputs give. The tests run Appendix B
  Examples B-1 to B-7 and Appendix C Examples C-1 to C-7. The equations
  of Chapters 3, 4, 8 and 9 and the charts are text and catalog only.
- Section ids in the Army layout ('5-5a(2)(b)', '2-7a(2)(c)1', 'B-1b')
  are valid (`SECTION_ID`, `chapter_schema.json`) and sit under their
  parents in both retrieval layers; the existing ids give the same
  results.
- Scripts: `scripts/printed_army_layout.py` reads manuals in the Army
  layout for `build_printed_text.py` (manifest layout "army");
  `build_figure_catalog.py` and `check_section_numbers.py` read that
  layout too.

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
