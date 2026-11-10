# Changelog

Releases before 1.6.0 are described in their release commits (`git log`).

## Unreleased

**Review of 2026-11-10: Eurocode 7 Parts 1 and 2, the Caltrans Trenching and
Shoring Manual and FEMA P-2082 checked against the printed pages.** Lookups
that returned a value the print does not support now return the printed
value or refuse and say why.

Values that change:

- **EN 1997-1 Eqs. C.1 and C.2** (`active_earth_pressure`,
  `passive_earth_pressure`): the pore water pressure is now inside the
  bracket as printed, `K [gamma z + q - u] + u`. Nothing changes where
  u = 0. Below the water table (Kp 3.0, gamma 20 kN/m3, z 5 m, u 49.05 kPa)
  the passive pressure was 349.05 kPa and is 201.90 kPa; the active
  pressure at Ka 0.333 was 82.35 kPa and is 66.02 kPa.
- **EN 1997-1 Table A.11** (`table_a_11_correlation_dynamic_impact_test`):
  the columns are printed ">= 2, >= 5, >= 10, >= 15, >= 20", so n between
  two columns takes the lower column and is no longer interpolated. For
  4 piles tested the factor on the minimum was 1.40 and is 1.50; on the
  mean 1.533 and is 1.60.
- **Caltrans anchor blocks** (`factor_of_safety_requirements`): the factor
  of safety was 1.5 and is 2.0, as Section 10-2 prints.
- **Caltrans Table 3-1, Very Loose sand** (`table_3_1_granular_properties`):
  the unit weights were moist "none", submerged 60 to 100 pcf, and are moist
  below 100 pcf, submerged below 60 pcf.
- **Caltrans Rankine and tension-crack results**: the printed page cited for
  Eq. 4-3-16 is 4-10, for Eq. 4-3-19 4-11, for Eq. 4-4-13 4-19, and for
  Eq. 8-3-3 8-6.

Lookups that now refuse where they used to answer:

- **EN 1997-1 Table A.10** (`table_a_10_correlation_ground_test`): n = 6, 8,
  9 and n above 10 are not printed and were interpolated or capped (n = 6
  gave 1.135 on the minimum). They now raise, and the message gives the
  printed neighbours (n = 5: 1.15, n = 7: 1.12).
- **EN 1997-1 Annex D bearing resistance** (`undrained_bearing_resistance`,
  `drained_bearing_resistance`): `shape="strip"` with no length was computed
  as a square footing (undrained, cu 50 kPa, q 20 kPa, B 2 m: 328.5 kPa
  where a long rectangle gives 277.1 kPa). Annex D prints a rectangular and a square or
  circular case only. Any other shape raises, a rectangular shape needs L,
  and the result names the shape case used. For a strip give
  `shape="rectangular"` and its length.
- **EN 1997-1 Annex A partial and correlation factors** (the 17
  `table_a_*` lookups and `design_approach_sets`): the row and the set must
  be given. A call that left the set out used to get the set of ones
  (`table_a_4_str_geo_soil_parameters()` returned 1.0, where set M2 gives
  1.25). The value returned is still a bare number.
- **EN 1997-1 selectors**: `parameter="cohesion"` (Tables A.2, A.4, A.16)
  and `resistance="shaft"` (Tables A.6 to A.8) picked one of two printed
  rows (effective cohesion 1.25 not undrained shear strength 1.4; shaft in
  compression 1.3 not shaft in tension 1.6). They now raise and name the
  choices.
- **EN 1997-2 Table D.3** (`table_d3_pile_base_resistance`): below the first
  printed column, qc = 10 MPa (qc = 4 MPa gave 2.0 MPa at s/Db = 0.10).
- **EN 1997-2 Table F.3** (`table_f3_phi_from_density_index`): below the
  first printed row, ID = 40 % (ID = 10 % gave 34 degrees; a density index
  passed as the fraction 0.5 gave 41 degrees).
- **EN 1997-2 G.1 and G.3** (`equation_g1_density_index_from_dp`,
  `equation_g3_stiffness_coefficient_from_dp`): outside the printed ranges
  of validity (N10 = 200 gave a density index of 1.10).
- **EN 1997-2 Eq. 4.5** (`equation_4_5_cu_from_dmt`): the material index
  IDMT is now required, since the equation is printed for IDMT < 0.8.
- **Caltrans Table 4-2** (`table_4_2_wall_friction`):
  `interface_material="concrete"` picked mass concrete on foundation
  materials (29 to 31 degrees on clean gravel) over formed or precast
  concrete against soil (22 to 26 degrees). It now raises.
- **Caltrans at-rest coefficient** (`at_rest_k0`): a backfill slope together
  with OCR > 1, which Eq. 4-3-15 does not cover (the slope was ignored).
- **Caltrans cohesive apparent earth pressure**
  (`aep_cohesive_max_ordinate`): the 0.2 to 0.4 factor of Eq. 8-3-2 has no
  default (it was 0.3, which the manual does not print), and for 4 < Ns < 6
  Ka is required so the larger of the two envelopes can be taken.
- **FEMA P-2082 Seismic Design Category** (`seismic_design_category`): S1 is
  required, because Section 11.6 assigns E or F where S1 >= 0.75 (SDS 1.2,
  SD1 0.9 with no S1 gave D).

A result whose shape changed:

- `design_approach_sets("DA1")` returns both combinations of Design
  Approach 1 as `{"description", "combinations": [Combination 1,
  Combination 2], "note"}`. It used to return Combination 1 alone with its
  sets at the top level, so `result["action_set"]` no longer exists for
  "DA1": read `result["combinations"][0]["action_set"]`. "DA1-C1" and
  "DA1-C2" keep their keys and each names the other combination.

Results that now say more, with the same numbers:

- EN 1997-2 `table_d1_phi_e_from_qc`, `table_h1_phi_e_from_wst` and
  `table_d5_alpha_p_alpha_s_sand` return the tables' printed notes; for
  silty or gravelly soil the result says E' is the sand value, not adjusted.
- `table_min_test_count` returns the printed criterion behind low, medium
  and high variability, the table and page, and the footnote on a cell
  (the 0 of Table W.1 is "only valid for very homogeneous rock types with
  extensive experience from nearby locations").
- `site_class_from_vs30` also returns the site classes at vs/1.3 and
  1.3 vs, which Section 20.3 requires when the velocity is estimated from
  correlations.
- `max_allowable_slope_angle` (Caltrans Eqs. 4-5-1 to 4-5-4) computes what
  it did. Its note and its description now open with the caution that
  Eq. 4-5-2 is not dimensionally consistent as the manual prints it and
  that the slope needs a slope stability analysis.
- `heave_factor_of_safety` returns `fs: null` with a note where the driving
  force is zero or negative (it returned infinity, which is not valid JSON).
  Adequacy is judged, as before, on the unrounded ratio QU/Q against 1.5: a
  ratio of 1.4996 is reported as `fs` 1.5 and is not adequate.
- `table_d3_pile_base_resistance` says in a note when qc is above the last
  printed column (25 MPa) and that column was used, and
  `table_f3_phi_from_density_index` says when it interpolated between
  printed rows (the table prints no interpolation rule) or used the
  ID = 100 % row for a higher ID.
- `site_class_from_vs30` gives an estimated velocity no class in the Site
  Class B or A range (Sections 20.2.4 and 20.2.5 require a measured
  velocity for those classes) and says why.
- Three error messages name what is wrong: Table A.3 for a misspelt
  condition, Table A.9 for a fractional n, and the EN 1997-2 quality class
  given as text.
- The chapter text of EN 1997-1 (Eqs. C.1, C.2, Kpc, Tables A.10 and A.11)
  and of Caltrans Section 10-2 is corrected to the print.

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
