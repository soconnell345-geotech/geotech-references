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
- **GEC-13 ground modification (FHWA-NHI-16-027 Vol I).**
  - `table_3_1_lightweight_fill` (Table 3-1, p. 3-1): rebuilt from the
    print, with the specific gravity column. Four of eight rows change:
    Tire Shreds 37 to 73 pcf (was 37 to 55); Cellular Concrete 20 to 80
    (was "Foamed Concrete" 24 to 55); Expanded Shale, Clay, and Slate 37 to
    65 (was 40 to 65); Expanded Air-Cooled Slag 69 to 94 (was "Blast
    Furnace Slag" 60 to 75). The `notes` field, whose statements the table
    does not print, is gone (gec-07).
  - `table_1_3_by_function` (Table 1-3, pp. 1-15 to 1-16): the ten printed
    functions with their printed technologies and comments. Increase
    drainage, accelerate consolidation, provide lateral stability and
    increase resistance to liquefaction listed technologies the table does
    not (earthquake drains, vacuum consolidation, compaction grouting) and
    left out ones it does (jet grouting for liquefaction); "decrease
    imposed loads" and "transfer embankment loads" were missing (gec-09).
  - `table_1_2_applicability`: two rows completed (gec-46). The eight
    filter lookups (`table_1_2`, `1_3`, `1_6`, `2_1`, `3_1`, `4_3`, `8_1`,
    `8_6`) refuse a filter that matches no row, naming the printed rows,
    instead of returning an empty list (gec-37).
- **GEC-6 shallow foundations (FHWA-SA-02-054).** The three chart lookups
  are rebuilt from the rendered pages; the points read are in the comment
  above each data block.
  - `figure_5_19_hough_bearing_capacity_index` (Figure 5-19, p. 91): the six
    curves under the chart's own names, clean uniform medium sand highest
    and inorganic silt lowest. The old names of the four upper curves were
    not the chart's and their values were other curves' or no curve's:
    well graded silty sand and gravel at N' = 32 is 109 (the manual's own
    example reads 110; it returned 97), clean uniform medium sand at N' =
    40 is 176 (was 138), inorganic silt at N' = 50 is 84 (was 78). The
    curves start at N' = 4 (N' = 0 returned C' = 0) and the three upper
    ones leave the chart at N' = 56, 75 and 89; outside its curve a value
    is refused. 'coarse_sand' and 'clean_fine_to_medium_sand', which are
    not curves of the chart, and 'sand', 'gravel', 'silty sand' are
    refused (gec-01).
  - `figure_4_1_relative_density_spt` (Figure 4-1, p. 34): the 80 to 100 %
    curves were far right of the print. N = 30 at 1 k/ft2 is on the 100 %
    curve (it returned 87.5 %); N = 24 at 0.58 k/ft2 is 97 % (was 90). The
    chart's whole stress range, 0.25 to 6 k/ft2 (12 to 287 kPa), is read. A
    point left of the 15 % curve or right of the 100 % curve is refused; it
    returned 15 or 100 (gec-10).
  - `figure_4_2_friction_angle_from_density` (Figure 4-2, p. 35): the
    printed mesh of relative density lines between the ML and GW lines. The
    0 % line is 27.5 degrees at 17.3 kN/m3 (it returned 30.0). A dry unit
    weight the chart does not plot at the given relative density (22.0
    kN/m3 at 0 %, which returned 33 degrees) is refused (gec-13).
  - `table_5_15_friction_factor` (Table 5-15, p. 99): a key names one row
    by a soil the row prints. "fine sand" is the Clean fine sand row, 0.35
    to 0.45 (it returned 0.45 to 0.55); "sand", which returned the clean
    gravel and coarse sand row's 0.55 to 0.60, and "gravel", "clay",
    "silty sand" are refused (gec-16).
  - `table_5_7_presumptive_bearing_rock` (Table 5-7, p. 68): "rock" and
    "hard", which returned the first row's 7.7 MPa, and "medium hard",
    "shale", "soft rock" are refused; each row answers to its own words and
    the rocks it lists (gec-31).
  - `table_5_9_rqd_bearing_capacity` (Table 5-9, p. 70): between two
    printed rows the quality is "between fair (RQD 75) and good (RQD 90)",
    not the lower row's word, and the result says the pressure was
    interpolated (gec-32).
  - `table_5_13_poissons_ratio_rock` and `table_5_14_youngs_modulus_rock`:
    a rock type by its printed name only ("s" returned diabase, "weathered
    granite" the intact granite row) (gec-40).
  - `table_5_12_shape_rigidity_factor`: values unchanged; the docstring
    says the linear interpolation between the printed length/width rows is
    not the table's (gec-33).

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
