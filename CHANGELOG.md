# Changelog

Releases before 1.6.0 are described in their release commits (`git log`).

## Unreleased

**Pavement and UFC soils values checked against the printed pages (review
of 2026-11-10, pave-01 to pave-32).** Every changed value was read off the
rendered page; results and docstrings name the page.

- UFC 3-250-01 Chapter 20 drainage: Eq. 20-17 lacked its factor 2 (layer
  thickness H was half the print), Eq. 20-18 had 0.85 in the numerator
  (H was 0.72 of the print), Eq. 20-4 effective porosity computed the water
  retained (0.088 against the printed form's 0.247 at 110 pcf, Gs 2.65,
  We 0.05), and Eq. 20-11 lacked its 2 (T50 twice the print). Eq. 20-3 is
  kept with (1+e) where the page prints (1-e), and the result and the
  first docstring paragraph say so.
- UFC 3-250-01 Table 5-1 gained its rigid-pavement traffic column
  (`pavement_type='rigid'`; 1 million passes, cohesive 95 %: 11 -> 12 in);
  `pavement_type` is required, since the table prints both columns and no
  default (leaving it out raises TypeError), and both Table 5-1 and 21-2 read each "< n" bound strictly; Table 21-2
  gained its cohesive 80 % column. Table 9-1's asphalt-stabilized rows are
  split as printed (GM base 1.15 -> 1.00; SM subbase 2.30 -> 1.50; SP base
  refused, "not used for base course").
- UFC 3-250-01 Figure 15-1 retraced along every curve (k 450 at 100,000
  passes: F 0.42 -> 0.694); past 10 million passes the value is held with a
  note. Figure 10-1 refuses a subgrade k below 25 pci and notes a hold above
  300 pci or past 60 in.
- AASHTO 1993: Tables 2.4/2.5 `mi_min`/`mi_max` and `cd_min`/`cd_max` the
  right way round (1.35/1.40, was 1.40/1.35; midpoints unchanged);
  Figure 2.5 re-read at 400 dpi: the curve begins on the a1 0.20 line at
  about EAC 106,000 psi and reads 0.252 at 150,000 psi (was 0.26); below
  106,000 psi a1 raises, naming the chart's range (was 0.20 unsaid; the
  app's flexible design raises there too), and past 500,000 psi it holds
  with a note quoting II-17's caution above 450,000 psi. Aggregate loss
  (II-12): the scan drops decimal points, so the Kenya equation's " 092T"
  is .092T and its gravel factors f are .037/.043/.028/.059, not
  0.37/0.43/0.28/0.59 (lateritic, T 2, R 30 in, VC 5: 22.352 -> 2.231
  in/yr); `aggregate_loss_army_corps` is renamed `aggregate_loss_brazil`
  (the print credits a Brazil study; no alias) and the page's first
  equation is added as `aggregate_loss_truck_traffic`, GL = 0.12 +
  0.1223(LT). Figures 3.5 and 3.6 (II-41, II-42) are charts that print no
  equation; `relative_damage_rigid` and `k_loss_of_support` say in their
  first paragraph and a `print_note` that their closed forms are fits
  (values unchanged).
- UFC 3-250-03 Table 6-2 adds the stockpile kerosene amounts (cold 18.8 L
  per metric ton, 4.5 gal per ton, where only 8.3/2.0 was returned and
  called the stockpile amount) and lists the emulsion grades by climate as
  printed; Table 2-8 gives Section 1's VTM for the optimum asphalt content
  (4 for HMA, 6 for sand asphalt).
- UFC 3-250-04 Table 9-1: the range is of the maximum joint spacing
  (`max_joint_spacing_low_ft`/`_high_ft`, renamed) and a 12 in slab is in
  the 9-12 in row (20 ft -> 15-20 ft); Table 3-2 carries footnotes 2
  (1.5 % for crusher dust) and 3 (blast-furnace slag).
- UFC 3-250-11: Table 3-6 rates LL 60 and PI 35 Marginal as printed (were
  High); Table 3-5 holds percent passing No. 200 above 25 at the 25 row
  with a note; Table A-1 carries Sec A-1.1's 4 % cement limit; the
  Table 2-3 footnote (c) PI limit is 20 + (50 - percent passing No. 200)/4,
  the form printed in the 2004 edition's Table 2-1 footnote b (printed
  2-3), where the held 2020 page prints 20 + 50 - P200 with no divisor and
  the code took it literally (25 % passing: 45 -> 26.25); the result's
  `print_note` gives both editions' forms.
- `ufc_backfill` rebuilt from the held UFC 3-220-04FA (16 January 2004) and
  cited to it, which overturns REF-31 (2026-11-06), where the package was
  kept cited to "UFC 3-220-04N", an edition that is not held: open areas 90 %, beneath structures 95-100 % (cohesionless)
  or >= 95 % (cohesive) of CE 55 maximum density, where the old table gave
  ASTM D698 rows (95/90/85 %) the print does not have; new Table 5-1
  compaction criteria and Figure 2-5 compaction-induced lateral pressures.
  Removed (not in the print): `table_drainage_requirements`,
  `compaction_induced_pressure_kPa`, `filter_criteria_check`.
- `ufc_expansive` rebuilt from UFC 3-220-07: Table 4-1's three classes
  (PI 30 -> Marginal, Sp 0.5-1.5 %; was "medium", 4-8 %), para 5-4c's
  active zone (10 ft moist / 20 ft dry, or the water table under 20 ft),
  Table 6-1's foundation systems, and the grade-beam void "6 to 12 inches
  or 2 times the predicted total heave, whichever is larger" (a 4 in heave
  gives 8-12 in; was 100 mm for a "high" class). Removed (not in the
  print): `activity_index`, `free_swell_percent`, `swell_pressure_kPa`,
  `pier_minimum_embedment_m`. Added: Table 4-2's four empirical swell
  relations as printed (Vijayvergiya and Ghazzaly, Schneider and Poor,
  McKeen-Lytton, Johnson; printed 4-3).

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
