# Changelog

Releases before 1.6.0 are described in their release commits (`git log`).

## Unreleased

**FHWA lookups corrected against the print (review of 2026-11-10, findings
gec-NN).** Each lookup below now returns what its cited page prints. A key
that names no printed row, or more than one, is refused with the printed
rows instead of being answered from the first row that contains the words.

- **Micropile manual (FHWA-NHI-05-039).**
  - `figure_5_23_limiting_lateral_modulus` (Figure 5-23, p. 5-70): three
    bars were wrong. The 9.625"x0.47" 80 ksi casing is 71 psi (490 kPa; it
    returned 1096 kPa, the 7"x0.73" casing's value); hollow bar 73/53 is
    165 psi (1138 kPa; was 2414) and 103/51 is 350 psi (2413 kPa; was
    1138). The 7"x0.73" casing and the #20 bar are added. The result now
    carries the printed psi, the page and the rule of p. 5-68 (no further
    buckling check when Es LIMIT is less than the soil's Es); the docstring
    had the rule reversed. '5.5', '8', '10' and other partial keys are
    refused (gec-03).
  - `table_4_2_rebar_properties` (Table 4-2, p. 4-27): the yield strength
    is the printed column (#18 Grade 520: 1335 kN, was 1342.1; #8 Grade
    420: 211 kN, was 214.2) and the size is the printed 19 to 63 mm. Grade
    550 is the one printed bar, 63 mm (2.5 in), 1747 kN; Grade 550 #14 and
    #18, which the table does not print, are refused (gec-28).
  - `table_5_8_epsilon_50_stiff` (Table 5-8, p. 5-56): the value of the
    printed range, not an interpolation between ranges (su 75 kPa: 0.007,
    was 0.006; 150 kPa: 0.005, was 0.0045; 200 kPa: 0.005, was 0.004). The
    table has no row for 200 to 300 kPa; a strength there is refused
    (gec-18).
  - `table_5_10_soil_modulus_k_clay` (Table 5-10, p. 5-56): the cyclic k
    of soft and medium clay, which the table leaves blank, is refused (it
    returned the static 8140 and 27150 kPa/m) (gec-19).
  - `table_5_11_fixity` (Table 5-11, p. 5-58): the three columns in the
    print's words, with "300 mm or less" and "600 mm or more" and the
    footnote; `table_5_12_elastic_modulus` says where its two sand rows
    differ from the table's kPa column (gec-47).
- **GEC-12 driven piles (FHWA-NHI-16-009 Vol I).**
  - `table_7_2_resistance_factor_field` (Table 7-2, p. 226): a key names
    one row. "static load test" and "dynamic testing" alone, which each
    returned the combined row's 0.80, are refused; a static load test
    without dynamic testing is 0.75 and dynamic testing of two piles per
    site condition 0.65, as printed (gec-04).
  - `table_7_16_soil_setup_factor` (Table 7-16, p. 299): mixed soils reach
    their own row. "silty clay" is Silt - Clay, recommended 1.0 (it
    returned Clay's 2.0); "sandy clay" is Sand - Clay, 1.5 (was 2.0);
    "silty sand" is Sand - Silt, 1.2 (was Silt's 1.5). The result names the
    row and carries the table's footnote and site counts (gec-05).
  - `table_7_11_eslami_fellenius_cs` and `figure_7_9_delta_phi_ratio`: a
    name that fits two rows or curves ("silt", "pile", "taper") is refused;
    `table_7_3_static_analysis_methods` refuses an unknown soil type
    instead of returning an empty list (gec-45, gec-37).
  - `table_7_10_brown_method_factors` (Table 7-10, p. 260): values
    unchanged. The docstring now says that the page prints Bb equal to Ab
    for compression in gravelly sand to boulders and in rock, and prints
    the vibratory rows under "Tension"; both await a ruling (gec-06).

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
