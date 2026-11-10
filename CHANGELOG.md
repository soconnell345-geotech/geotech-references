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
  - `table_7_10_brown_method_factors` (Table 7-10, p. 260): for
    compression in gravelly sand to boulders and in rock the table prints
    Bb equal to Ab (0.888 and 2.89 ksf/bpf); Bb is now 0.0, as the matching
    tension rows print it, and the result carries the printed value and a
    `print_note` (lead's ruling). At N60 = 30 in gravelly sand to boulders
    Eq. 7-21 now gives fs = 0.89 ksf (was 27.5, against Table 7-8's 2.4 ksf
    limit). The vibratory rows (Fvs 0.68) are answered under tension, where
    the table prints them; a vibratory compression lookup, which returned
    them, is refused (gec-06).
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
- **GEC-7 soil nail walls (FHWA-NHI-14-007).**
  - `figure_4_3_friction_angle_spt` (Figure 4.3, p. 79): the six curves
    rebuilt from the rendered page; the points read are in the comment
    above the data. They were 3 to 8 degrees low for N60 of 12 or more and
    up to 4 degrees high at low N60 on the higher stress ratios. N60 = 22 at
    sigma'vo/Pa = 2.0 is 37.0 degrees (it returned 33.6); N60 = 31 at 1.0 is
    45.0 (was 38.2); N60 = 48 at 1.5 is 46.5 (was 40.6). A curve is read
    only where it is drawn, from phi 25 to where it leaves the top of the
    chart or ends: N60 = 50 at 0.5 (it returned 44; the curve reaches phi 50
    at N60 38.25), N60 = 5 at 2.0 (it returned 29.0; the curve starts at
    N60 6.1) and N60 = 0 are refused. Between curves the angle is linear in
    sigma'vo/Pa at the same N60 (gec-02).
  - `figure_5_11_basal_heave_nc` (Figure 5.11, p. 124): the three curves
    rebuilt from the rendered page. At H/Be = 0 they start at 5.20 (Be/Le =
    0), 5.69 (0.5) and 6.19 (1) (it returned 5.14 for all three); a long
    excavation at H/Be = 1.6 is 6.76 (was 5.74) and at H/Be = 5 is 7.45
    (was 6.2, 17 % low) (gec-11).
  - `table_4_2a_spt_soil_properties` (Table 4.2a, p. 78): the very loose
    and very dense rows print phi "< 30" and "> 45 (3)"; they returned 25
    to 30 and 45 to 50, bounds the table does not print, and now give no
    lower and no upper bound respectively, with the printed text in
    `phi_printed`. The result carries notes (1) to (3); note (3) holds
    sands to 40 degrees and gravelly soils to 45 (gec-22).
  - `table_4_3b_elastic_modulus_spt` (Table 4.3b, p. 82): "sand" returned
    the silts row, 8 (N1)60 ksf (7,661 kPa at (N1)60 = 20, where clean fine
    to medium sand is 13,406); it fits two rows and is refused. Each row
    answers to its printed name (gec-17).
  - `table_5_1_factors_of_safety` (Table 5.1, p. 108): short-term
    excavation prints 1.25-1.33 (3); `fs_static_max` 1.33 is added beside
    1.25. The Basal Heave row's seismic 2.3 carries note (5), long-term
    conditions; the short-term row returned it and now gives none. Rows
    with a note carry it ("basal heave" alone, which returned the
    short-term row, is refused) (gec-41).
  - A key names one printed row in `table_4_3a_elastic_properties`,
    `table_4_4a_bond_strength_coarse`, `table_4_4b_bond_strength_fine`,
    `table_4_5_bond_strength_rock`, `table_4_6_pullout_resistance`,
    `table_5_1_factors_of_safety`, `table_5_3_load_factors_permanent`,
    `table_5_resistance_factors` and `table_5_12_wall_displacement`. A word
    found in several rows was answered from the first: "clay" returned
    Table 4.3a's soft sensitive clay (2,394 to 14,364 kPa); rotary drilled
    "sand" Table 4.4a's Sand/gravel (103 to 179 kPa) though Silty sand is
    also printed; "shale" Weathered shale though Slate/Hard shale is
    printed; "eh" the active row; "basal heave" the short-term resistance
    factor 0.65 (long-term 0.50); "soil" the weathered rock and stiff soil
    column (C = 0.8). Each is refused with the printed rows; printed names
    and listed short names are taken. Table 4.3a's clay rows say their
    Poisson's ratio is undrained, and Table 4.4a's high-overburden rows and
    Table 4.6 carry their notes.
  - `table_4_9_site_coefficient_fpga` (Table 4.9, p. 94): GEC-7 heads its
    columns PGA <= 0.25, 0.5, 0.75, 1.0, >= 1.25, the Ss values that head
    the Fa table (GEC-12 Vol I Table 7-28); GEC-12 Table 7-27 (p. 380)
    prints the same F_PGA values under PGA < 0.1, 0.2, 0.3, 0.4, > 0.5, and
    the lookup now reads them there (lead's ruling). Site class D at PGA
    0.30 is 1.2 (it returned 1.56); E at 0.35 is 1.05 (was 2.18). The result
    is a dict with `F_pga`, a `print_note` naming both headings and the
    reference (it was a bare number); site class F is refused with the
    table's note (1), a site-specific analysis (gec-29).
- **GEC-10 drilled shafts (FHWA-NHI-18-024, 2018).**
  - `table_8_4_resistance_factor` (Table 8-4, p. 8-14): a key names one
    printed row. "side" returned cohesionless compression 0.55 and
    "uplift" 0.45, the first rows holding the word; these and "rock",
    "load test", "structural" are refused with the rows. Rock side
    resistance cites Eq. 10-21, as printed (it said Eq. 10-21 or 10-22);
    combined axial and flexure gives the printed range, 0.75 with
    `phi_max` 0.90 (gec-15). `table_8_4_by_category` refuses a category it
    does not have (it returned an empty list), and
    `table_9_1_lateral_resistance_factor` (Table 9-1, p. 9-22) no longer
    answers a name that holds a row's word ("group uplift" returned the
    group row's 0.8).
  - `aashto_reliability_index` is removed: GEC-10 prints no table of the
    reliability index against the probability of failure, and the
    function interpolated pF linearly between six points, 27 to 37 % high
    between them (gec-23, lead's ruling).
  - `table_11_2_group_efficiency_cohesionless`: values unchanged (0.65 at
    2.5 diameters, 0.80 at 3, 1.0 at 4 or more). GEC-10 prints them in the
    text of Section 11.4.1.2 (p. 11-6), not in a Table 11-2; the result
    cites that section and says when the value is interpolated. The name
    is kept (gec-24, lead's ruling).
  - `su_uu_to_ciuc` and `su_uc_to_ciuc` (Eqs. 10-17 and 10-16, p. 10-16):
    where the printed relation gives su/su(CIUC) of zero or less (su/
    sigma'vo of 0.0149 or less for UU, 0.0182 or less for UC) it is
    refused; su(UU) = 10 kPa at sigma'vo = 700 kPa returned -1,030 kPa.
    GEC-10 prints no range for the relations; above those points the
    answers are unchanged (Example 10-2: 2,000 psf at 3,697 psf gives
    2,571 psf) (gec-14).
  - `equation_10_22_caving_rock_side` (Table 10-3, p. 10-21): below RQD 20,
    where the table has no row, the RQD 20 row is still used and the
    result now says so. `equation_10_21_rock_socket_side`,
    `equation_10_22_caving_rock_side`, `figure_10_6_alpha_clay` and
    `table_10_2_nc_base_clay` docstrings quote the print: the resistance
    factor for rock side resistance is 0.50 in Table 8-4 and 0.55 in the
    text of p. 10-21 (both printed, not reconciled); qu should not exceed
    the shaft concrete's strength (p. 10-21, not checked); Figure 10-6
    draws its curve from su/pa of about 0.25 to 5; Eq. 10-20 is in D, the
    depth of embedment. No value changes (gec-43).

- **GEC-11 MSE walls (FHWA-NHI-10-024 Vol I).**
  - `table_2_1_min_reinforcement_length` (Table 2-1, p. 2-43): the three
    printed cases. Seismic loading is one row, "0.8 to 1.1"; it was two
    rows, "Seismic (low)" 0.8 and "Seismic (moderate to high)" 1.1. Each
    row gives the printed cell (`typical_min_L_over_H`) and its ends
    (`L_over_H_low`, `L_over_H_high`; the key `L_over_H` is gone). The 8 ft
    (2.5 m) minimum on every row is removed: the table does not print it;
    the docstring quotes where the text does (p. 4-11) (gec-21).
  - `table_4_4_traffic_surcharge` (Table 4-4, p. 4-17): the parameter is
    `abutment_height_ft` (was `wall_height_ft`), and every result says the
    table is for abutments perpendicular to traffic and that walls parallel
    to traffic take heq = 2.0 ft (p. 4-16). Below 5.0 ft the 5.0 ft row
    (4.0 ft) is still used, with a note. Values unchanged (gec-20).
  - `table_4_7_internal_resistance` (Table 4-7, p. 4-48): rows and keys as
    printed: `static_phi`, `combined_static_earthquake_phi`,
    `combined_static_traffic_barrier_phi`, with notes A to C. The key
    `combined_static_phi` (a copy of the static factor, 0.75 for strips,
    beside the printed combined static/earthquake 1.00) and the keys
    `earthquake_phi` and `traffic_barrier_phi` are gone; values unchanged
    (gec-34).
  - `table_3_4_electrochemical_geosynth` (Table 3-4, p. 3-10): the two
    printed rows, polyester (PET) 3 < pH < 9 and polyolefin (PP & HDPE)
    pH > 3, by AASHTO T-289; "polyolefin" returned an empty list.
  - The eleven filter lookups (Tables 2-1, 2-2, 3-4, 3-6, 3-8, 3-9, 3-11,
    4-1, 4-2, 4-5, 4-7) refuse a filter that matches no row, naming the
    printed rows; they returned an empty list. A filter is matched as one
    phrase, then word by word, so "metallic strip" and "vertical earth
    pressure" find their printed rows (gec-37).
  - Notes as printed: Table 2-2's footnote (frost and scour depth); Table
    3-9's backfill types (Type 2: max. 3/4 in. (20 mm), D50 about #30; the
    docstring said "uniform fine sand to medium sand", 19 mm) and footnote
    a; Table 4-1's gamma_EQ note (the code said "typically 0.0 to 0.50",
    not printed); Table 4-2's types of load; Table 4-5's conditions (0.65
    also where the slope contains or supports a structural element).

- **GEC-9 laterally loaded deep foundations (FHWA-HIF-18-031).**
  - `table_7_1_p_multiplier` (Table 7-1, p. 104): beyond 5B the 5B row is
    still used, and the result now says the table has no row there (note
    (3) allows interpolation between 3B and 5B only); the table's notes
    come back as `print_notes`. The refusal below 3B no longer says "use
    Pm = 1.0 beyond 5B", which the table does not print (rows 2 and 3 are
    0.85 and 0.7 at 5B) (gec-25).
  - `table_a1_k_stiff_clay`, `table_a2_epsilon50_stiff_clay` (Tables A-1,
    A-2, p. 222): outside the printed Ca columns (0.5 to 4 ton/ft2) the
    end column is still used, with a note; Ca 100 (kPa passed as ton/ft2)
    gave 2,000 pci unsaid. The docstring's "for Ca > 4 ton/ft2 use k = 2000
    or 800" is removed: GEC-9 does not print it (gec-25).

- **GEC-4 ground anchors (FHWA-IF-99-015).**
  - `table_6_soil_anchor_transfer_load` (Table 6, p. 71): "very stiff" is
    refused; the silt-clay row prints Stiff (10-20) 30 kN/m and Hard
    (21-40) 60 kN/m only, and "very stiff" returned the Hard row's 60
    (gec-30).
  - `table_7_bond_stress_rock` (Table 7, p. 73): `recommended_FS` 3.0 on
    every row is gone (the table prints no factor of safety); the result
    quotes p. 74 instead: 3.0 on Table 8's transfer load in competent
    rock, 2.0 for intermediate geomaterials (qu 0.5 to 5.0 MPa) (gec-38).
  - `table_7_bond_stress_rock`, `table_8_rock_anchor_transfer_load`:
    "limestone" and "shale" are refused (each names two printed rows;
    they returned soft limestone and soft shales) (gec-39).
  - `table_20_corrosion_protection` (Table 20, p. 131): the table's words.
    The anchorage is "Trumpet" for both classes (was "attached to bearing
    plate with watertight weld"); Class I bond length "Grout-filled
    encapsulation or" / "Fusion-bonded epoxy" (was "Corrugated HDPE or
    polypropylene encapsulation"); Class II bond length "Grout". The source
    reads "modified after PTI, 1996", as printed (gec-39).

- **GEC-8 continuous flight auger piles (FHWA-HIF-07-03).**
  - `dd_pile_side_resistance_MPa` (Eq. 5.29, pp. 83-84): every result
    carries the print's conditions, N60 not depth corrected and
    cohesionless materials only (they were dropped); above N = 50 the
    result says N = 50 is used. Values unchanged (gec-42).

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
