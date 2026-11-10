# Changelog

Releases before 1.6.0 are described in their release commits (`git log`).

## Unreleased

**DM 7.2 (UFC 3-220-20, 16 Jan 2025) lookups as printed (review
dm72).** Each was read again from the rendered page; values below are
before -> after at the example input.

- Figure 4-36, Rowe's moment reduction: `figure_4_36_moment_reduction`
  now takes rho itself (5 to 200 in^2/lb) and the soil the wall
  penetrates, and uses the two curves the figure prints. rho 9.5, very
  dense: 0.30 -> 0.687 (the figure's own example reads 0.68). Fine-grained
  and loose soils, for which the figure permits no reduction, are refused;
  `plot_figure_4_36` needs both rho and soil_type for a point.
- Figure 5-18, layered clay N_cm (`figure_5_18a_Ncm_strip`,
  `figure_5_18b_Ncm_circular`): rebuilt from the figure; each returns a
  dict with N_cm and the 10 % reduction where the manual calls for it.
  Strip, su2/su1 0.2, H/B 1.0: 3.80 -> 2.53. Off the chart (su2/su1 above
  2.0) is refused.
- Eq. 5-11/5-12, circular footing equivalent rectangle: r 1.5, e 0:
  3.760 x 0.940 -> 2.659 x 2.659 (the area was half the printed one).
- Eq. 5-26 `second_layer_thickness`: as printed, (2B - H1)(c1 + tan
  phi1)/(c2 + tan phi2); Figure 5-20's example gives 4.5 ft.
- Table P-6 `usr_dss`: sin phi' - 0.5 sin^2 phi'. phi' 30: 0.067 -> 0.375.
- Eq. 3-9/3-10 (`borrow_volume_from_waste_fraction`, `shrinkage_factor`):
  (1 + X_L), not 1/(1 - X_L); X_L 0.30: 9 % less borrow (1,607 -> 1,462
  in the review's example).
- `p_a` (seven prologue power functions) and `gamma_w` (two chapter 3
  functions) have no default any more (2116 psf and 62.4 pcf gave wrong SI
  answers: 92.06 where 50.13 is right).
- Chapter 6, equations: Eq. 6-48 base resistance at 4 % (fine and coarse
  were swapped: coarse 100 -> 71 % of R_b); Eq. 6-30 N*c (Ir 50: 9 ->
  6.53); Eq. 6-31 N*c (su/Pa 0.5: -10.47 -> 8.13); Eq. 6-49/6-50
  equivalent footing (B 10, z2 4: 14 -> 12); Eq. 6-47 Meyerhof I_f
  (Z/B 6: 0.917 -> 0.5); Eq. 6-22 mean stress (phi' 30: 50 -> 66.7 % of
  sigma'); Eq. 6-23 Vesic N*q (phi' 35, Irr 100: 22.7 -> 83.8); Cheng Nq
  (phi' 35, Z/b 20: 3.93 -> 55.1); Eq. 6-33 LCPC base (qc 10,000, kt
  0.4: 25,000 -> 4,000); Eq. 6-40 group uplift (n 4: 460 -> 490, the
  effective weight now counted per element); Eq. 6-41 uplift block
  (3 x 4 x 10: 240 -> 378); Eq. 6-76 depth to fixity (sqrt 2, not 2:
  20 -> 14.1).
- Chapter 6, tables rebuilt from the page: Tables 6-21/6-22/6-23 (LCPC
  ks, fp/Pa, kt) by the eight printed soil rows and Groups I-A, I-B,
  II-A, II-B; Table 6-18 F_nu by pile shape and Poisson's ratio 0.2 to
  0.5 (square, 0.3: 0.82 -> 0.48); Tables 6-36/6-37 (lateral CLM a and
  n; clay, free head, M_max: 0.55, 0.72 -> 0.855, 1.288).
- Signatures changed: `table_6_18_Fnu(poisson_ratio, pile_shape)`;
  `table_6_21_ks`, `table_6_22_fp`, `table_6_23_kt(soil_type, group)`
  (`table_6_22_fp` returns fp/Pa); `lcpc_unit_shaft_resistance`'s fourth
  argument is fp/Pa; `table_6_36_clm(soil_type, ratio, fixity)`;
  `table_6_37_clm(soil_type, fixity)`; `drag_force_check(Q_d, Q_np, P_r)`
  (the unread `Q_d_drag` removed); `figure_4_36_moment_reduction(rho,
  soil_type)`.
- Printed limits now refused: Eq. 6-15 outside su/Pa 0.24 to 1.42; Eq. 6-1
  below sand size (D50 < 0.075 mm); Cheng Nq below Z/b 5; Table 5-6
  between phi 0 and 10 degrees. Stated, not checked (the function takes
  no such input): Z/b >= 5 for the drained base resistance (Eq. 6-20,
  6-21) and the 20 ft wall limits of Eq. 4-13 and 4-17.
- Chapter text: chapter titles as printed (chapter 2 is "Excavations",
  not "Earth Pressures"); chapter 6 equation descriptions and
  `implemented_in` links corrected; Eq. 3-4 and Eq. 6-15 state their
  printed form beside the coded one.

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
