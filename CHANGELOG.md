# Changelog

Releases before 1.6.0 are described in their release commits (`git log`).

## Unreleased

**Structural lookups checked against the print (review of 2026-11-10,
struct-01 to struct-11).** Values that change:

- UFC 4-023-03 Table 4-1, RC beams controlled by shear, development or
  embedment (`ufc_collapse.table_4_1_beam_other_modeling`): the
  acceptance-criteria plastic rotations are the printed ones, no longer
  equal to a and b. Shear, stirrups <= d/2: primary 0.003 -> 0.002 rad,
  secondary 0.02 -> 0.01; stirrups > d/2: 0.003 / 0.01 -> 0.002 / 0.005;
  inadequate embedment: 0.015 / 0.03 -> 0.01 / 0.02 (printed p. 63).
- GSA Alternate Path Tables 6 and 8 (`gsa_collapse.table_6_beam_*`,
  `table_8_slab_*`): GSA prints one acceptance column for primary and
  secondary components; both now return it (new key `acceptance`).
  Table 6 equals b in every row, so every primary value moves from a to
  b: conforming, (rho-rho')/rho_bal <= 0, V ratio <= 3, 0.063 -> 0.10 rad;
  shear, stirrups <= d/2, 0.003 -> 0.02 (printed p. 39). Table 8: with
  continuity reinforcement, Vg/Vo <= 0.2, primary 0.05 -> 0.10 and at
  >= 0.4 0.0 -> 0.08; without, Vg/Vo <= 0.2, 0.015 -> 0.020 (both);
  development 0.0 / 0.01 -> 0.02; embedment 0.01 / 0.02 -> 0.03 (printed
  p. 41).
- EM 1110-2-2107 Table 4.1 (`em_2107.loads.table_4_1_load_factor`): the
  self-straining load T has the printed principal factor 1.2 in every
  category; it raised an error before (printed p. 27).
- Steel connection m-factors and plastic rotations printed as c0 - c1 d
  (UFC Tables 5-1/5-2, GSA Tables 10/11, eight functions): d and dbg are
  inches, named in the docstrings and results (`d_units`, `dbg_units`); a
  depth at which a printed expression is zero or negative is refused
  (a 30 in WUF beam typed as 762 gave UFC m = -59.0; now ValueError). An
  m-factor between 0 and 1 is returned with a `note`.
- EM 1110-2-2107 `bolt_grade_check` refuses a grade the manual does not
  name (it answered "not permitted", even for "A325").

Labels, units and citations (no value changes):

- EM 1110-2-2107 Eq 10.2-10.14 (`em_2107.tainter_gate_loads`): each
  description is the printed load-combination heading. Eq 10.7 is Load
  Combination 3, gate operated by two hoists (it said "gate jammed");
  Eq 10.8 is one hoist; Eq 10.9 is the jammed gate, an extreme load
  (gamma_pr = 1.3) as are Eq 10.4 and 10.11 (they said "unusual").
- RC beam flexure tables (UFC 4-1/4-2, GSA 6/7): V/(bw d sqrt f'c) is in
  psi units (an SI ratio is 1/12.04 of it and read the highest-m row);
  results return `vw_ratio_units` and the printed row read.
- EM 1110-2-2104: every parameter of the flexure, design and shear
  functions has its own description with its unit (flexure and design in
  ksi and inches, shear in psi and lbs); `aci_beta1` says f'c is ksi or
  psi, not MPa.
- Page citations: EM 1110-2-2104 Table 3-2 pp. 24-25 (was 23-24),
  Eq 4-3 p. 30 (was 29) and Eq 4-1/4-2 pp. 29-30 (was 29); UFC Eq 3-6
  p. 24 (was 23); Wood Handbook Table 5-3a pp. 5-4 to 5-8 (was 5-5 to
  5-8).
- GSA chapter 4 text no longer says Tables 6/7 are identical to UFC
  Tables 4-1/4-2.

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
