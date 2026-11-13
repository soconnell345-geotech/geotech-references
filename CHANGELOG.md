# Changelog

Releases before 1.6.0 are described in their release commits (`git log`).

## Unreleased

**The PDF reader is an input of a script build.** The manifest of each
reference whose text `scripts/build_printed_text.py` reads off the PDF
(`em_1905`, `fhwa_soils_foundations`) records the PyMuPDF version it was
built with (`"built_with": {"pymupdf": "1.27.2.3"}`). The two tests that
rebuild the text and compare it with the committed files run only under
that version (`tests/_build_reader.py`). Under another version they skip,
naming both versions; with `GEOTECH_REQUIRE_BUILD_READER=1` they fail
instead. On GitHub the Python 3.10 job installs the recorded reader with
that variable set, and the Python 3.12 job the newest reader, where the
rebuilds skip and every other test runs. `tests/test_build_reader.py`
checks that every script-built manifest records the same version and that
the workflow pins it. No package code or stored text changed.

**GEC-11 lookups compared with the page after the review merge (REF-80).**
Of the five a checker found differing from the print, Tables 2-1, 4-4 and
4-7 were already as printed on the integration branch; the others:
- `table_4_1_load_combinations` (p. 4-4): the printed dashes are returned
  as "–", not 0.0 (Strength I EQ and CT, Extreme Event I CT, Extreme
  Event II EQ, Service I EQ and CT), each row with a `print_note`; a test
  checks every cell against the table as typed in the chapter text.
- `table_3_7_galvanization` (p. 3-26): the wire row ("Wire*", all
  diameters) carries the printed footnote "* For bar mats fabricated from
  uncoated steel wire."; the thicker strip row says the page prints
  "> ¼ in." (the library puts an exact ¼ in. there); every row a reference.
- `table_4_6_bearing_capacity_factors` and the chapter 4 note on Table
  4-6: the two Nc cells 0.1 off are "as rounding in steps would give" (it
  said "rounding twice").

**GEC-11 (FHWA-NHI-10-024 / -025, November 2009) chapter text rebuilt from
the print (build, REF-80).** The 11 chapter files were a condensed
paraphrase, 183 sections, with content the print does not carry; the
review of 2026-11-10 found substantive errors in 16 of the 40 sections it
checked. They are now read off the printed pages by
`scripts/build_gec11_text.py` (manifest `scripts/manifests/gec_11.json`):
284 sections at every printed level, each body the print's own words with
`[p. 4-21]` markers, every numbered equation (3-1 to 7-20b in Vol I; 8-1,
8-2, 9-1 to 9-9 and 9-14 to 9-17 in Vol II, which prints no 9-10 to 9-13)
typed in from the rendered pages, the design tables, the example
specifications' tables (chapter 10) and the inspection checklists
(chapter 11) typed in row by row; no summaries or key points. A test scans
every body for a formula that came apart in the text layer (a parted
prime, a lone number above a formula, unpaired brackets, a sentence
repeated in table rows). The appendices are in the next paragraph.
Stored statements that changed in substance, the unsafe ones first:

- 9.2.6, Eq. 9-1 (p. 9-7): the required tension was stored as
  TS = (FSR - FSU) MD / (FSR D); printed TS = (FSR - FSU) MD / D. The
  stored value was two thirds of the printed one at FSR = 1.5.
- 7.1.2 and 7.1.3, Eqs. 7-16 to 7-18 (pp. 7-12, 7-13): the seismic
  pullout and connection checks were stored without the printed 0.8 on
  F* and on phi, which overstated the resistance.
- 3.4.2 (p. 3-16): "alpha default 1.0 is conservative"; printed 0.8 for
  geogrids and 0.6 for geotextiles. Eq. 3-2 has no Rc term.
- 3.5.1, Eqs. 3-10 and 3-11a/b (p. 3-22) and Figure 3-5 (p. 3-24): stored
  Tn = 0.86 b Ec Fy and Tn = Ac Fu; printed Ec = En - ER, Tal = Fy Ac / b
  and Ptal = Fy Ac (the yield stress, never Fu), phi = 0.65 for steel
  grids on a rigid facing (stored 0.75).
- 5.3.3, Eq. 5-4 (p. 5-26): stored O95 <= D85; printed AOS <= B D85, with
  B from 0.5 to 2 by soil (stricter where B is under 1).
- Values with no printed source are gone: differential settlement limits
  1/500 and 1/50 (2.7), "RF = 3.5" (4.5), a deadline and a CDR
  requirement (4.1.1).
- 10.9 (p. 10-26): tie strips to ASTM A1101 Grade 50, as printed (stored
  A1011).
- `table_4_6_bearing_capacity_factors` (Table 4-6, p. 4-29) held
  two-decimal values the manual does not print (the page prints the table
  to one decimal and gives no equations for the factors). It now returns
  the printed cells, interpolated values rounded to one decimal; at phi =
  39 it returns 67.9 for the printed Nc = 37.9, a correction the page
  does not print, and says so.
- `figure_4_10_kr_ka_ratio` (Figure 4-10, p. 4-37): every result carries
  the footnote printed under the chart, "*Does not apply to polymer strip
  reinforcement" (its asterisk marks the Geosynthetics line), and a polymer
  strip is refused with it. The footnote is in the stored text too.
- 4.4.5 (p. 4-18) held about 60 words of hidden, overprinted copies of
  Figure 4-6's lettering ("Sliding" eight times, "(Overturning)" twelve);
  they are gone, the three printed labels are kept, and Figure 4-6 is
  listed under 4.4.6, where the page prints it. No other chapter page has
  hidden text of this kind.

UNSAFE SIDE as printed, with a note: Figure 6-14 Case 2 (p. 6-25, section
6.5) has + FV where putting LW = 0.3H into the printed Case 1 gives
+ 10 FV over the same denominator, so it divides FV by 10 and understates
Tmax; Case 3 follows from Case 1. No lookup codes Figure 6-14. The notes
printed inside Figure 6-14 are typed in.

Stored as printed, each with a note: Eq. 4-26 (p. 4-36) prints its bracket
without the square that Eqs. 4-2 and 4-3 give with no wall friction and
beta = 0 (the printed form gives the larger Ka); Figure 9-4 (p. 9-8)
prints FSR = FSU + (TS + D) / MD where Eq. 9-1 gives TS D; Table 4-6
prints Nc = 37.9 at phi = 39 (`table_4_6_bearing_capacity_factors`
returns 67.9 there and says so) and Ngamma = 25.9 at phi = 31 (within
the run of its column; returned as printed); the alignment tolerances on
p. 11-26 give 6 mm per m for
1/2 inch per 10 ft (about 4) and 15 for 2 inches (about 17); Table 5 of
the example MSE wall specification (p. 10-30) gives AASHTO T 26 for
gradation where Table 6 gives T 27; Figure 8-10 (p. 8-29) labels 1 kPa =
0.145 lb/ft2 (0.145 is lb/in2); in Table S3 (p. 10-50) the Class 3
puncture cell repeats the Class 3 tear cell's 40 lb (180 N). Section ids: none removed; 101 added,
the printed subsections the condensed files left out (2.1.1, 3.2.1,
4.4.8.a, 8.7.1, 10.4.1, 10.10.1, ...) and lettered parts of sections too
long for the reference tools (1.2.a, 3.4.2.a, 4.4.6.c.a, 5.3.3.a, 7.1.1.a,
9.2.6.a, 10.9.a to 10.9.f, 11.1.2.a, 11.3.5.a; the letters are not
printed).

**GEC-11 Volume II appendices read off the print (build, REF-85).** The
library held none of them. `scripts/build_gec11_appendix.py` (the
`appendices` of the Volume II manifest entry) builds each into its own
file, `text/appendix_b.json` and so on, the print's words with `[p. B-3]`
markers and every formula line, table and figure lettering typed in from
the rendered pages:

- Appendix A (pp. A-1 to A-4; file chapter 12), LRFD load notation, the
  load combination table (AASHTO 2007 Table 3.4.1-1) and the permanent
  load factors (Table 3.4.1-2), typed in row by row; they agree with the
  chapter 4 lookups for Tables 4-1 and 4-2.
- Appendix B (pp. B-1 to B-18; file chapter 13), pullout resistance
  factors and MBW unit-geosynthetic connection strength: sections B to
  B.4.2, Eqs. B-1 to B-4 (and Eqs. 4-41 and 4-43 printed again), Table
  B-1, the connection test protocol and the worked example (data table,
  CRcr and Talc = 444 + 0.044 N, recomputed). Noted as printed: "75
  years (670,000 hrs)" (p. B-10; about 657,000), and Figure B-5's line
  through the test data, y = 0.1132x + 1068.2 (tan 6.5 degrees), where
  the text uses tan 6 degrees (pp. B-16, B-17).
- Appendix C (p. C-1; file chapter 14), steel soil reinforcements: the
  strip, welded wire and bar mat tables typed in row by row (wire sizes
  W3.5 to W20, areas and diameters in both units, Fy/Fu, spacings). Noted
  as printed: W4.5's 0.239 in. diameter is given as 6.0 mm (6.07).
- Appendix D (pp. D-1 to D-21; file chapter 15), the creep reduction
  factor RFCR and Tal (after WSDOT T 925): Eqs. D-1, D.2-1, D.2-2 (the
  extrapolation uncertainty factor (1.2)^(x-1)), D.3-1 and D.3-2 (the
  confidence limits for comparing SIM with conventional data), D.4-1,
  the unnumbered Tal = P95 / (RFID × RFD), the four figures' lettering
  and the D.6.1 example (Tl = 56.0 kN/m, RFCR = 2.0). Noted as printed:
  p. D-9's "12 to 15" does not follow from 0.05 to 0.18 decades per
  degree; the text points to Equations "B.2-3", "B.2-1", "D.2-3" and
  "D.4" for D.2-2 and D.3-1; on p. D-16 no equation follows "in
  accordance with the following". A short last line now ends a paragraph
  that the text layer runs together (Appendix B gains three breaks).

**FHWA-NHI-05-037 (Geotechnical Aspects of Pavements): four lookups
corrected from the page (app BACKLOG REF-93).** Found while the manual's
chapter text was being rebuilt from the print; each was read from a 300 dpi
render and independently checked cell by cell.

- `table_7_12_frost_susceptibility` returned six rows one frost group LOWER
  than Table 7-12 (p. 7-60) prints, the unsafe side: gravelly soils with 10
  to 20 percent fines F1 (printed F2) and with over 20 percent F2 (printed
  F3); sands, except very fine silty sands, with over 15 percent F2 (printed
  F3); all silts F3 "High" (printed F4 "Very high"); very fine silty sands
  and clays with PI under 12 F3 (printed F4). The other four rows were
  right. The percent-finer column is the page's 0.075 mm.
- `table_4_14_soil_as_pavement_material` holds all 17 printed rows (it held
  10): the GM and SM "u" rows and ML, CL, OL, MH, CH, OH and Pt (p. 4-66).
- `table_5_57_permeability_highway_materials` cites p. 5-105 (was 5-103)
  and returns the table's footnotes.
- `table_5_18_compaction_aashto`: the A-6 optimum moisture cell is printed
  "10.30"; the function returns 10 to 30 percent and says what the page
  prints.

**EM 1110-1-1905, Geotechnical Design of Shallow Foundations on Soils
(U.S. Army Corps of Engineers, 31 July 2025), as package `em_1905`.**

- Chapter text read off the print: chapters 1-12, and Appendices B
  (design examples, ultimate limit states), C (design examples,
  settlement) and D (unit conversion factors) as chapters 13-15; 779
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
  sub-heading beside a table stands once, not on every row. Seventeen more
  slips of the print are kept as printed with a note: Examples B-1, B-4
  (the clay's unit weight printed 0.133 kcf in Table B-4a, Steps 1 and 3,
  where Figure B-4 and Table B-4c give 0.113 kcf, from which the printed
  qo and qult follow), B-5, B-6, B-7 (Table B-7b, Step 4: the CPT's four
  q*t measurements printed "of 17 ksf", the pressuremeter's value, where
  the line below lists 200, 200, 320 and 200 ksf, geometric mean 225 ksf),
  C-2, C-3, C-6 and C-7 (Table C-7b, Step
  7: the 25 rows total 0.343 in, printed 0.034 in), Table 3-15, the symbol
  list of Eqs. 8-27 and 8-28, Table 3-8 (σv with a raised semicolon, the
  evident reading σ′v; a stress given in pcf) and Tables D-3 and D-6.
  Table C-7c's note says that every input it states (pne, αd = 0.5, αc =
  0.33, Step 12's exponent 0.5) matches 8.5 tsf, Example B-7's Layer 1
  value, which its Given names, and that only its printed results (9.5,
  4.9, 0.015 ft) match pne = 16.0 tsf, the geometric mean of the P*L
  values within 1.5B, which the page never prints. Table 4-10's E*0
  (the text layer holds a capital O) and "not applicable" in Example B-2
  (the text layer holds a space for the math font's b, p. 299) are typed
  in, and a test looks for any other word broken by a space; a subscript
  inside a word in the text font stays in it (CKoU, Figure 3-9); the
  symbol lists of Eqs. 3-17, 7-3b, 7-4, 7-6, 7-11, 7-12 and 8-2 give every
  symbol the formula prints; an equation printed straight after another
  is described as printed after it, not by the other's formula (Eq. 5-3);
  the Figure List keeps a word broken after its own hyphen whole
  ("per-inch", "1-D"); a split leaves room for the notes placed after it
  (C-2b and C-3b are each in two parts). A test looks through every chapter
  for formula pieces put back in the wrong places (a prime alone, a lone
  number above a formula, a number doubled from a stacked fraction, a
  subscript spaced off its symbol, brackets that do not pair).
- The rebuild gives the same chapter files under PyMuPDF 1.27 and 2.1.
  Under 2.x the rebuild had failed on GitHub at two typed passages
  (Examples C-3 and C-7), and its text differed in five sections: PyMuPDF
  2.x gives the bar set over a symbol in the equation font (N̅60, σ̅′zo,
  h̅, c̅v; 26 bars on pp. 176-178, 186, 188, 359, 386 and 387) a box of no width at
  the symbol's right edge, or its subscript's, where 1.27 gave the bar's
  ink over the symbol, so the bar went over the wrong letter (N6̅0, σz̅′o)
  or stood apart (h ̅, cv ̅). The reader now puts such a bar on its
  symbol: the character the text layer lists before it, passing over a
  subscript. Both versions list the bar in that place. The words the two
  versions read are the same. 1.27 also reads 156 doubled spaces that 2.1
  reads as single spaces, which changes no text.
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
  Examples B-1 to B-7 and Appendix C Examples C-1 to C-7. Every input
  that may be None says when to pass None: theta_deg unless the AASHTO
  method has H > 0, d_g unless alpha_g > 0 (USACE); a value given where it
  is not needed is ignored, not checked. The equations
  of Chapters 3, 4, 8 and 9 and the charts are text and catalog only.
- Section ids in the Army layout ('5-5a(2)(b)', '2-7a(2)(c)1', 'B-1b')
  are valid (`SECTION_ID`, `chapter_schema.json`) and sit under their
  parents in both retrieval layers; the existing ids give the same
  results.
- Scripts: `scripts/printed_army_layout.py` reads manuals in the Army
  layout for `build_printed_text.py` (manifest layout "army");
  `build_figure_catalog.py` and `check_section_numbers.py` read that
  layout too.

**Build of 2026-11-12: every figure-catalog row stores the page number its
page prints.** A helper quotes `printed_page` in its citations. The audit
of all 33 catalogs (4,164 rows) found, and this build corrects: DM 7.2
Figures B-1 to B-24 three pages low; the edition year stored as the page in
GEC-5 (13 rows), GEC-10 (8) and GEC-11 (5); the micropile manual's 142 rows
cut to the number after the dash (now "1-4", "D-3", "E-5"); UFC 3-220-07
Figure 6-7 on 6-8, not 6-9; GEC-12 Figure D-99 on PDF index 231, its own
page. The 1,328 rows that had no printed page now have one, read from each
page's footer or header and checked on renders (a seeded sample of 12 and
every chapter or appendix boundary per reference): GEC-10 372, GEC-5 336,
GEC-13 239, GEC-11 137, GEC-4 90, GEC-6 86, EN 1997-1 23, GEC-8 20,
UFC 3-220-04FA 14, FHWA-NHI-05-037 6, GEC-14 5. Values are integers where
the page prints only digits, otherwise the label as printed ("4-12",
"A2-37", "A1"). New `tests/test_catalog_printed_pages.py`: every row has a
printed page and none is a year, and every row's page prints it (69 rows on
scanned or turned pages pinned to the label seen on a render). The
first-page marker of every section in 13 references' chapter text was also
checked against the page that prints the heading (4,407 sections; EN
1997-1 and the Caltrans manual cite pages only inside the text); two
GEC-13 ranges started on the wrong page and now start on the heading's
page (7.1.2.1 pp. 7-1 to 7-4, 9.7.4 pp. 9-110 to 9-111).

**Lookups outside their printed range (app BACKLOG REF-76).** A lookup
given an input past the end of its printed table or chart no longer
returns the edge value with nothing said. Where the print gives an
open-ended row or curve ("D > 40b", ">= 6") the edge value stays and the
docstring says so; where the manual's text says what to do beyond the
range, the lookup does that and says so; otherwise it raises `ValueError`
naming the printed range, the page and the value given. In-range values
are unchanged. Functions whose out-of-range behaviour changed (printed
pages):

- `gec_12.figures.figure_7_17_adhesion`: D/b outside 10 to 40 is refused
  (curves D = 10b and D = 40b only, p. 248); it was held at 10 or 40.
- `gec_12.figures.figure_7_18_adhesion_factor`: D/b below 10 in Cases 2
  and 3 is refused (their shallowest curve is printed "D = 10b", p. 249);
  it took the D = 10b curve. Case 1's "D < 10b" and every case's "D > 20b"
  / "D > 40b" curve are open-ended as printed and still read past their
  label. D/b <= 0 is refused.
- `gec_10.figures.equation_10_22_caving_rock_side`: RQD below 20 is
  refused (Table 10-3 prints RQD 20 to 100, p. 10-21); it held the RQD 20
  row (alpha_E 0.45) with a note, which overstates alpha_E there.
- `gec_10.tables.table_10_2_nc_base_clay`: su below 500 psf is refused
  (Table 10-2 prints 500, 1,000 and ">= 2,000" psf, p. 10-19); it held
  N*c = 6.5. Above 2,000 psf the open-ended row still gives 9.0.
- `gec_11.tables.table_4_4_traffic_surcharge`: an abutment height above 0
  and below 5.0 ft is refused (Table 4-4 prints 5.0, 10.0 and ">= 20.0"
  ft, p. 4-17); it held heq = 4.0 ft with a note. 0 still returns the
  whole table; taller than 20 ft still takes the open-ended 2.0 ft.
- `gec_7.tables.table_4_9_site_coefficient_fpga` and
  `table_4_10_site_coefficient_fv`: a negative PGA or S1 is refused. Their
  end columns are printed open-ended ("S1 <= 0.1" / "S1 >= 0.5", p. 95;
  Table 4.9 under GEC-12 Table 7-27's "< 0.1" / "> 0.5") and still take
  the end column.
- `gec_8.equations.dd_pile_side_resistance_MPa`: N above 50 (Eq. 5.29 is
  printed for N <= 50, p. 84) is still held at 50, now with `note` and
  `out_of_range`; the printed limit fs <= 0.16 / 0.21 MPa, reached at
  N = 32, governs the limited fs, so the value does not change.
- `gec_8.tables.table_5_4_p_multiplier`: a spacing wider than a soil's
  printed rows (3B for every soil, 5B also for M. Dense Sand and Loose M.
  Sand, p. 112) still holds the widest printed row, now with `note` and
  `out_of_range`; holding is on the low side (p. 111).
- `gec_9.tables.table_7_1_p_multiplier`: beyond 5B (Table 7-1 prints 3B
  and 5B, p. 104) the 5B row is still held, now with `out_of_range` beside
  its `note`; holding is on the low side (p. 102).
- `gec_9.tables.table_a1_k_stiff_clay` and `table_a2_epsilon50_stiff_clay`:
  Ca outside 0.5-4 ton/ft2 (the columns Tables A-1 and A-2 print, p. 222)
  is refused; the end column was returned, with a note. The message gives
  the ton/ft2 conversion (a Ca of 100 given in kPa read 2,000 pci) and
  points to Appendix A.1 for soft clay.
- `eurocode_7_2.tables.table_d3_pile_base_resistance`: qc above 25 MPa is
  refused (Table D.3 prints qc = 10, 15, 20 and 25 MPa, p. 115; it
  returned the 25 column with a note).
- `eurocode_7_2.tables.table_d4_pile_shaft_resistance`: a negative qc is
  refused; the last row is printed ">= 15" MPa (p. 116) and kept.
- `eurocode_7_2.tables.table_e2_pmt_shape_coefficients`: L/B above 20 is
  refused (Table E.2 prints Circle, Square, L/B = 2, 3, 5 and 20, p. 122;
  it returned the L/B = 20 column, whose coefficients are the lowest of a
  rising trend).
- `eurocode_7_2.tables.table_f3_phi_from_density_index`: a density index
  above 100 % is refused (Table F.3 rows ID = 40 to 100 %, p. 126; it
  returned the 100 % row with a note).
- `eurocode_7_2.tables.table_l2_min_mass_sieving`: unchanged; the docstring
  states the open-ended last row "<= 2" mm, 100 g (p. 145).
- `aashto_1993.lef.load_equivalency_factor` (and the four `tables.esal_*`
  lookups that read it): a load outside the printed rows (2-50 kips single,
  2-90 kips tandem and triple), an SN outside 1-6 or a D outside 6-14 in
  (Tables D.1-D.18, printed D-3 to D-20) is refused; the end row or column
  was read, with a note.
- `aashto_1993.composite_k.composite_k_subbase`: Dsb above 18 in, Esb above
  1,000,000 psi, MR above 20,000 psi, or a construction past the 2,000 pci
  diagonal (Figure 3.3, printed II-39) is refused; the nearest curve was
  read, with a note.
- `aashto_1993.composite_k.k_rigid_foundation_correction`: Dsg below 2 ft,
  MR above 20,000 psi or below where the curves used are drawn, k_inf
  outside 50-1,400 pci, or a k past the 2,000 pci scale end (Figure 3.4,
  printed II-40) is refused; the nearest curve was read, or no correction
  applied, with a note. The lower MR limit follows the curves the Dsg
  needs: the 2-ft curve leaves the top at 1,169 psi, the 5-ft and 10-ft
  curves end at 1,073 and 1,083 psi, so Dsg 2-5 ft needs 1,169, 5-10 ft
  1,083 and exactly 5 ft 1,073 (a first version refused below 1,169 for
  every Dsg).
- `wood_handbook.structural_deformation.torsional_constant_rectangular`
  and `structural_stress.torsional_shear_stress_rectangular` (Figures 9-9
  and 9-15 coded as polynomials in b/h): a non-positive h or b is refused;
  a negative b, or two negatives passing the b <= h check, put b/h off the
  curves' 0-1 axis and gave a number.
- `wood_handbook.structural_stability.ylinen_strain`,
  `ylinen_buckling_stress` and `built_up_column_capacity`: c outside 0 < c
  < 1 is refused (Eq 9-28 defines c as "a constant between 0 and 1",
  printed p. 9-14, and Eqs 9-29 and 9-30 take the same c; the page gives
  0.957, 0.8 and 0.9). Also refused: a stress outside 0 <= f < Fc in Eq
  9-28, Kf outside 0 < Kf <= 1 in Eq 9-30 (the page says Eq 9-29 "is
  reduced" by it), and a non-positive Fc, fe or E.
- `gec_11.tables.table_4_4_traffic_surcharge`: a negative abutment height
  is refused (it returned the whole table, the answer for 0). Refusal
  messages that named a range without its page now name it
  (`aashto_1993.composite_k.composite_k_subbase` below Figure 3.3's scales,
  `ufc_pavement.tables.figure_10_1_k_on_base` below the 25 pci curve,
  `figure_e_vehicle_allowable_passes`). Wording that said more than the
  page: the UFC 3-250-11 Table 3-5 docstring no longer says the 25 row
  would understate content past it (the table's columns do not all rise
  with fines), and the Caltrans timber-shoring note no longer gives a
  20 ft limit the page does not print beside PA = mH + 72.
- `aashto_1993.environmental.max_serviceability_loss_frost` (Figure G.7,
  printed G-10, five straight lines read off the chart): a depth of frost
  penetration beyond the chart's 10 ft axis is refused; the line used to be
  extended with a note (very poor at 12 ft: 6.0, past the chart's 5).
- `ufc_pavement.tables.figure_14_1_reinforced_pavement_design` (Figure
  14-1, printed 41): re-traced from the page. The figure is a nomograph (a
  straight line through the plain concrete thickness hd and the steel
  percentage S meets the reinforced thickness scale at hr); it had been
  coded as hd less a reduction taken from Appendix G's example at hd 7.9
  in, which read too thick away from that thickness. At S 0.10 %, hd 12 /
  17 / 24 / 30 in now give hr 10.65 / 15.1 / 21.4 / 26.9 in (were 11.1 /
  16.1 / 23.1 / 29.1; the figure's own dashed example is hd 16.9 in, hr
  15.0 in); at S 0.30 % and hd 30 in, 22.85 in (was 28.1). hd 7.9 in at
  S 0.10 % still reads 7.0 in (Appendix G-6). As and L follow the new hr.
  The whole S scale, 0.05-0.50 %, is now read (0.05-0.10 and 0.30-0.50
  were refused, the reduction not being known there). Still refused: hd
  outside the plain-concrete scale (6-30 in) and S outside 0.05-0.50 %;
  hd 3 in used to give hr 2.1. Where the line meets the reinforced scale
  below its 6 in end, hr is the 6 in minimum of paragraph 14-3 (printed
  42), with `minimum_thickness_governs` and a note (the manual's own
  example, hd 7.9 in at S 0.30 % for 6 in, lands 0.09 in below the end).
- `aashto_1993.composite_k.relative_damage_rigid` (Figure 3.5, printed
  II-41, coded as a closed form fitted to the chart): D outside the curves
  drawn (6-14 in) or k outside the k axis (10-2,000 pci) is refused; the
  formula gave numbers there with nothing to say so (D 3 in: 0.0117).
- `aashto_1993.composite_k.k_loss_of_support` (Figure 3.6, printed II-42, a
  power law fitted to the chart), for LS above 0: k above the axis end,
  2,000 pci (k 5,000 at LS 1 gave 1,045.8), a corrected k above the chart's
  top, 1,000 pci, and k below 10 pci are refused. The last is the library's
  reading: the slopes were checked against the chart only from 10 pci up,
  and below it the drawn LS = 3.0 line bends away from the power law (at k
  about 2.4 the chart gives 1 pci, the power law 1.5). LS = 0 returns k
  unchanged at any k. `effective_modulus_subgrade_reaction` holds its
  back-solved k within the periods' k (rounding of u_r could carry it just
  past them, and so past an axis end).
- `aashto_1993.composite_k.k_loss_of_support` (and
  `effective_modulus_subgrade_reaction`, which calls these three): LS
  outside 0-3 (Figure 3.6's lines, printed II-42) is refused; LS = 3 or 0
  was used, with a note.
- `aashto_1993.environmental.potential_vertical_rise`: a layer thinner than
  2 ft (Figure G.3's thinnest curve, printed G-4) is refused (the 2 ft curve
  was read, with a note); a negative PI is refused. Below the condition
  curve's start VR stays 0.00, as Table H.1 (printed H-3) prints it for PI
  15 and 19; the note now cites it.
- `aashto_1993.tables.layer_coefficient_a1_asphalt`: above 500,000 psi
  (Figure 2.5's edge, printed II-18) a1 is still held at the 500,000 psi
  value, now with `out_of_range`: on the safe side, and II-17 cautions
  against moduli above 450,000 psi.
- `aashto_1993.tables.layer_coefficient_a2_cement_treated` and
  `layer_coefficient_a2_bituminous_treated`: a UCS above 1000 psi or a
  Marshall stability above 1800 lb (the top labelled ticks of Figures 2.8
  and 2.9, printed II-23 and II-24) is refused; a2 was held at the top
  tick's value, with a note. II-22 gives no rule past the scales.
- `ufc_pavement.tables.figure_10_1_k_on_base`: k on subgrade above 300 pci
  or a base thicker than 60 in (Figure 10-1's top curve and axis, printed
  p. 32) is refused; the edge was read, with a note. The message points to
  the plate-bearing test on the base (para 10-4) and Table 10-1 note 2's
  500 psi/in maximum (printed 31).
- `ufc_pavement.tables.figure_e_vehicle_thickness`: passes below a chart's
  lowest curve (1,000 on most of Figures E-2 to E-31, 10,000 on E-2, 100 on
  E-31) still give that curve's thickness, now with `out_of_range` and a
  note naming the curve and saying the manual prints none below it: on
  every chart the thickness rises with the passes (checked on the rendered
  charts and, by a test, on the traced curves), so the hold is not less
  than fewer passes need. Where that curve is above the chart at the CBR
  it is refused. Above the highest curve the extrapolation stays, as
  Table G-1 (printed 257) reads the passenger car at 20,000,000 passes; the
  note now gives the page.
- `ufc_pavement.tables.figure_e_vehicle_allowable_passes`: a thickness more
  than 0.05 in under the lowest curve, or where every curve is above the
  chart, is refused; the lowest curve's passes were returned
  (`clamped='below_min_passes_curve'`), which overstates them. Above the
  highest curve `clamped='above_max_passes_curve'` stays (Table G-1's
  "Unlimited").
- `ufc_pavement.tables.figure_15_1_cracking_projection_factor` (F held at
  the 10,000,000-pass value past the chart's edge) and
  `figure_e1_flexible_thickness` (0.0 past the CBR where a curve meets the
  axis) are unchanged; the note and docstrings now give the basis (G-7,
  printed 264, reads 0.93 at 20 million passes; cover cannot be less than
  none).
- `ufc_stabilization.tables.table_3_5_emulsified_asphalt_requirements`:
  percent passing No. 200 above 25 (Table 3-5's last row, UFC 3-250-11
  printed p. 27) is refused; the 25 row was returned, with a note, though
  Sec 3-4.4 says the bitumen required increases with the finer sizes.
- `ufc_stabilization.equations.equation_cutback_asphalt_content_estimate`:
  a, b, c and d that do not add to 100 within 1 are refused; printed p. 26
  defines them as the four sieve fractions of the whole mineral aggregate,
  and cumulative percents passing or decimals returned a content with
  nothing said.
- `em_2104.flexure_axial.compression_controlled_capacity_doubly`: fy, Es
  or the concrete strain not positive is refused (they set the -fy..fy
  bound on the tension steel stress, the yield limit Eqs B-31 and B-37
  print for fs', printed pp. 47-48). The same for
  `compression_controlled_capacity_singly` (fs held at -fy) and
  `design.design_doubly_reinforced` (fs' held at fy).
  `compression_steel_stress_at_ku`, which bounds fs' for the doubly
  reinforced functions, also refuses ku or beta1 not positive, beta1 above
  1, d'/d outside 0 to 1, and for Eq B-31 ku not below beta1 (its
  denominator).
- `em_2104.flexure_axial.compression_controlled_capacity_doubly`, the
  lead's ruling 42: fs' from Eq B-37 came back above yield (75.7 ksi with
  fy 60 for e'/d 0.8). B-37 prints only fs' (>= -fy) (printed p. 48), and
  the cubic that gives ku (Eq B-39) is derived with the compression steel
  not yielded. Where B-37 is above fy at the cubic's root the function now
  holds fs' at fy and solves the manual's own equilibrium equations, Eqs
  B-23 and B-24 (printed p. 45), again for ku. For rho 0.01, rho' 0.01,
  d'/d 0.1, fy 60 ksi, f'c 4 ksi, b 12 in, d 20 in, h 24 in, phi 0.65:
  phi Pn 396.0 kips at e'/d 0.8 (was 424.8), 524.6 at 0.65 (was 566.6),
  695.5 at 0.5 (was 749.1). With Grade 60 steel and d'/d below 0.18 this
  is every compression-controlled section. The result gives
  `limit_governs` True, the cubic's root as `ku_cubic`, B-37 there as
  `fs_prime_unlimited`, the capacity by the printed equations as
  `phi_pn_cubic`, and a note saying this is the library's reading. Where
  the tension steel has yielded (Eq B-36 above fy at the root) the section
  is controlled by tension and the call is refused, naming
  `tension_controlled_capacity_doubly`; fs was held at fy with nothing
  said.
- `em_2104.flexure_axial.tension_controlled_capacity_doubly`: the same gap
  on the other side of the balanced point. Where Eq B-31's fs' is above fy
  at the root of Eq B-33 (near the balanced eccentricity, and only for
  d'/d below 0.18 with Grade 60 steel) fs' is still held at fy as the page
  prints (p. 47), and ku is now solved again from Eq B-32 (p. 47) with
  fs' = fy: the section above at 1.02 times its balanced e'/d, phi 0.9,
  gives 355.9 kips (was 352.9). At the balanced e'/d the two doubly
  reinforced functions now return the same ku (kb) and capacity. A
  section that is not controlled by tension is refused there.
- `em_2104.flexure_axial.compression_controlled_capacity_singly`: Eq B-19
  above fy at the root of Eq B-21 (the tension steel has yielded, the
  section is controlled by tension) is refused, naming
  `tension_controlled_capacity_singly`; B-21's ku came back with fs above
  yield. Below -fy, the bound the page prints (p. 44), fs = -fy and ku is
  solved again from Eqs B-2 and B-5 (p. 42): one layer at mid-depth, fy
  40 ksi, e'/d 0.05 gives 640.1 kips (was 639.7). Its page is cited as 44
  (was 44-45: Eqs B-17 to B-21 are all on p. 44).
- `em_2104` functions whose ku or stress-block depth is given, not solved
  with the steel taken elastic, still hold fs' at fy with `limit_governs`,
  `fs_prime_unlimited` and a note, and stay in balance:
  `compression_steel_stress_at_ku`, `balanced_eccentricity_doubly` (ku =
  kb) and `design.design_doubly_reinforced` (ad = Kd d).
  `design.design_doubly_reinforced` also refuses an fs' that is not
  positive (ad <= beta1 d': the compression steel is in tension and Eq D-4
  gave a negative As').
- `ufc_collapse.reinforced_concrete` Tables 4-1 to 4-4 flexure lookups:
  unchanged past the end rows, which are printed open-ended ("<= 0.0" /
  ">= 0.5", "<= 3" / ">= 6", "<= 0.2" / ">= 0.4", printed pp. 63-66), as
  the docstrings now say; a negative shear ratio (vw_ratio, vg_over_vo) is
  refused.
- `gsa_collapse.reinforced_concrete` Tables 6 to 9 flexure lookups: the
  same (open-ended rows printed pp. 39-42; negative shear ratios refused).

**Build of 2026-11-10: the UFS 3-220-10 (dm7_1) chapter text states its
equations as printed (app BACKLOG REF-79).** Every equation in chapters 1-8
was read off the rendered page and compared with the stored `equations`,
`body` and `key_points`. No function changes; the text an agent quotes does.
Pages are printed page numbers.

- Formulas that were wrong: Is(50) = F·P/d² and F = √(De/50) (Eqs. 1-4,
  1-5, p. 32); five rows of Table 4-2 (line, rectangular, triangular, slope
  and terrace loads, pp. 185-186); s = ΔH = Σ εz,i·Hi (Eq. 5-4, p. 227);
  the zi of Eq. 5-7 (p. 232); FSg = kg/ks = ψg·tg/ks (Eq. 6-16, p. 325);
  φ′ = 31 + KD/(0.236 + 0.066·KD) (Eq. 8-11, p. 406); E = (2/3)(1 + ν)Eu
  (Eq. 8-36, p. 449).
- Formulas the text left out are typed in: Eqs. 5-19 to 5-22, 5-24, 5-25,
  5-27 and 5-28 (pp. 254-268).
- Equations filed where they are printed: Eq. 3-5 in 3-2.7.3 (was 3-3.1),
  Eq. 4-12 in 4-5.5.2 (was 4-6.3), Eq. 7-2 in the new section 7-5.2
  Seepage Forces (p. 357; was 7-6.7). Copies under sections that only cite
  an equation are removed (Eqs. 5-9, 5-15, 5-22, 6-3, 6-5, 6-11, 7-1).
- Key points that misread a table: Tables 8-11, 8-20, 8-21 and 8-25
  (pp. 429-459); the UCT key point no longer states su = qu/2, which the
  section does not print (p. 152). Sections 4-7 and 4-8 no longer list
  Tables 4-7 and 4-8, which are tunnelling tables.
- Kept as printed, with a note: KD = (p1 − p0)/σ′v0 on p. 88 (Eq. 8-10
  prints (p0 − u0)/σ′v); the time factor C1 in the where-list of Eq. 5-7
  (Eq. 5-9 calls it C2); qt = qc + u·(1 + a) for Eq. 8-25 (the note cites
  qt = qc + u2(1 − a) from FHWA-NHI-16-072, GEC 5, Eq. 4.23, p. 4-29); the
  condition FC×PI = 0 on the first row of Table 8-22 (p. 455; the note adds
  that FHWA-NHI-05-037 Table 5-34, p. 5-53, prints the relation with no
  condition); "Example 1, Poorly-Graded Gravel with Sand (GW)" in 1-3.2.3
  (p. 13; Section 1-3.3.2 uses GP for poorly-graded gravel). The heading of
  3-2.4.2.1 prints "(ASTM D2116)"; its text and Table 3-4 print D2166, and
  the body says so (p. 152).
- The constant of Eqs. 6-13 and 8-41 is in cm/(s·mm²). Eq. 8-30 points to
  `intrinsic_compression_index_from_el` (it named the Figure 8-46 lookup).
- The seven printed sections the text did not hold are added in the print's
  wording: 1-3.2.3 Examples, 2-2.2 Published Geologic and Hydrogeologic Maps
  (lists Table 2-2), 3-2.5.1.2 Resonant Column Test, 3-2.5.1.3 Cyclic
  Triaxial Test for Modulus and Damping, 4-2.2 Mohr Circle of Stress (lists
  Figure 4-3), 5-5.5 Organic Soils and Peat, 8-4.5 Coefficient of
  Consolidation (lists Figure 8-50). The text now holds all 465 printed
  sections (`scripts/check_section_numbers.py dm7_1`: 0 missing).
- Four bodies cut off mid-sentence are completed from the print: 1-3.2.2.2,
  2-4.2, 3-2.3.2 and 6-3.4; 6-3.4 now lists Tables 6-6 and 6-7 (p. 302),
  which no section listed.
- The formulas and values of the tables in chapters 5, 6 and 8 were read
  off the rendered pages and compared with the key points and summaries
  that restate them. Key points that said more than the print now say what
  it says: m is about 0.8 from direct simple shear tests (Ladd et al. 1977),
  not "for most clays", and the print never says SHANSEP (8-3.2, Tables 8-7
  and 8-9); Table 8-17's groups (8-4.4); Table 8-28's exponent n is not
  attributed to a source (8-8.2); O95 < 0.21 mm holds for non-dispersive
  soils (6-5.3.2); filter Cu, D100F and fines (6-5.3.1); void ratio in
  Table 6-5 (6-3.3); Table 8-12 rows (8-4.1.1).
  Test: `tests/test_dm7_1_text_equations.py`.

**Build of 2026-11-12: every dm7_1 summary, key point and applicability
field checked against the print (app BACKLOG REF-79).** 3,168 fields in
chapters 1-8 were read against the printed pages and 784 changed: claims
the print does not make removed, "must" and "only" brought back to the
print's "should", "may" and "typically", limits and attributions the old
text dropped restored, and a few statements that said the opposite of the
print corrected (8-1 called the 16% one-standard-deviation probability one
of "underestimation"; 8-5.2.2 said Eu/su rises with OCR, which Figure 8-51
shows falling; 5-5.1 said "saturated" where the print, on significant
immediate settlement, says "unsaturated" (p. 236); 7-10.8.7 stated as a present requirement what FHWA (1998)
needed when it appeared). Key points restate printed sentences only; ids
are unchanged. Pages are printed page numbers.

- The 14 page footnotes now sit in the bodies at their marks as
  "[Footnote n: ...]" (pp. 3, 89, 142-165, 234, 237, 366, 424), and 35
  table notes and table footnotes as "[Note to Table x: ...]" or
  "[Footnote A to Table x: ...]" (chapters 1-8).
- Printed text the bodies left out is restored: the 6-5.3 subsections
  printed under repeated numbers (Retaining Wall Drainage to Relief Wells,
  pp. 330-338, with Figures 6-22 and 6-24 to 6-30), the 7-8 passage on
  well- and poorly-defined conditions (p. 366), 5-6.3 on Km, 5-9 on
  hydrocompression, 8-2.1.3's correction factor R and Figure 8-11, and
  shorter passages in chapters 5-8.
- Print slips kept as printed with a note: plane failure condition 3,
  "φʹ < ΨF" (p. 380), and the wedge condition "ΨFi > ΨFi > φʹ" (p. 381;
  the body had corrected it silently); "either suffusion or suffusion"
  (p. 306); Eq. 5-28 labelled "(5-5-28)" (p. 268); Table 5-8 Km's
  "(1−νs)²" (p. 260); Table 8-7 "LI = liquid index" (p. 423); 8-5.2.2's
  "undrained shear modulus" for the Eu/su of Figure 8-51 (p. 450).
- 7-5.2 no longer lists Figure 7-1 (printed in 7-2); Table 5-8 is listed
  under 5-6.3, where it is printed.
- Equation where-lists: every printed "where:" list was compared with its
  equation entry and section body. 21 entries that lacked a printed
  definition now carry the whole printed list in `variables`, in the
  print's words with its unit conditions (Eq. 2-1; Eqs. 5-12 and 5-13;
  Eqs. 8-1 to 8-5, 8-7, 8-8, 8-10 to 8-15, 8-17, 8-29, 8-30, 8-32 and
  8-35), e.g. Eq. 8-7 "Pa = atmospheric pressure in same units as vertical
  stress and qc" (p. 400) and Eq. 8-32 "Pa = atmospheric pressure (same
  units as Mds and σʹv)" (p. 442). Eq. 8-7 carries the same note on
  qt = qc + u·(1+a) as Eq. 8-25. The 8-7.3 body gives the where-lists of
  Eqs. 8-42 and 8-43 in the print's words ("k = hydraulic conductivity in
  m/s", pp. 462-463).
- Also restored: the cyclic DSS failure definition and the sentence after
  it in 3-2.5.1.1 (p. 162); six figure pointers, each at its printed
  place: 2-9.1.1 (Figure 2-14, p. 98), 2-9.1.2 (2-17), 2-9.3.1.1 (2-18,
  and 2-19 on p. 105), 2-9.3.1.2 (2-20, p. 106) and 2-10.2 (2-25a); the
  printed lead-in to Eq. 2-2.
- Table notes the bodies still lacked: Table 5-2, "Correlations provide
  values of Es in ksf units." (5-4.1.1, p. 231), the only unit printed for
  its Es correlations; Table 1-22, "A" preferred and "B" alternate method
  (1-5.4.2, p. 49). Table 5-8's two Km formulas are now in 5-6.3's
  `equations` as printed (p. 260), with (1−νs)² and, for rectangular mats,
  (1−νm)², and a note saying so; until now no Km formula was stored.
  The table, "after Brown 1969, Frazer and Wardle 1976", prints these
  two forms only, so it is complete; those papers are not held here.
- Key points brought back to the print: UU results "should always" be
  interpreted with φ = 0 (3-2.4.2.2, p. 153; was "must"); Eq. 8-16 is
  Carter and Bentley's (2016) fit to Gibson's (1953) trend line, and the
  "within 5%" is theirs (8-2.2.2, p. 413; was credited to Gibson); the
  Figure 5-27 method "can also be used" with vertical drains, no equations
  named (5-7.4.3, p. 271); under Method A, Td "should be divided by" FR of
  at least 1.3 (7-9.5, p. 373; was "requires"). Print slips kept with a
  note: "Buchiagnani" (Table 5-4, p. 234; 5-10, p. 279; Buchignani
  elsewhere) and "pore pressured" (3-2.4.1.3, p. 148, stored silently
  corrected until now). 1-3.2.2.1's note gives p. 12 (was 11).
- Where-lists: Eq. 5-14 carries its printed "σʹp = preconsolidation
  stress" (p. 241); Eq. 8-35's description no longer gives wn "(in %)",
  a unit the page does not print (p. 446), and says the library function
  takes percent; the 8-7.3 list for Eq. 8-44 reads "unit weight of the
  water" and "specific gravity of the solids" as printed (p. 463). 2-9.1.1
  keeps "As shown in Figure 2-14" and the print's "includes of an" with a
  note (p. 98).
- Force words: the 287 summary, key point and applicability sentences
  holding must, required, requires, only, cannot, always or never were
  matched to the printed sentences they restate (190 found; 125 with the
  same words printed) and the other 162 read against the body or page.
  35 now carry the print's own modality, e.g. ponded water "can be
  considered" as a layer, while including it "is imperative" (4-2.1.1,
  p. 179); water "does not sustain" shear stress (4-2.1.2, p. 180); the
  lack of a roof "prevents the progression of a pipe" (6-4.2, p. 304);
  "It is often necessary" to stabilize slopes (7-7, p. 364); Table 6-8
  assesses "if further investigation is required" (6-5.1, p. 307).
  Applicability lines that say where a section applies are unchanged.
  Eq. 8-7's note gives p. 427 for Eq. 8-25 (was 426).
  Test: `tests/test_dm7_1_build_keypoints.py`.

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
  ID = 100 % row for a higher ID. (Both cases past the last column or row
  are now refused: see "Lookups outside their printed range" above.)
- `site_class_from_vs30` gives an estimated velocity no class in the Site
  Class B or A range (Sections 20.2.4 and 20.2.5 require a measured
  velocity for those classes) and says why.
- Three error messages name what is wrong: Table A.3 for a misspelt
  condition, Table A.9 for a fractional n, and the EN 1997-2 quality class
  given as text.
- The chapter text of EN 1997-1 (Eqs. C.1, C.2, Kpc, Tables A.10 and A.11)
  and of Caltrans Section 10-2 is corrected to the print.

**Build of 2026-11-10 (app BACKLOG REF-83): the chapter text of EN 1997-1,
the Caltrans Trenching and Shoring Manual and FEMA P-2082 read again
against the printed pages.** About one section in four had a substantive
error. No lookup changes; what the text tools return does:

- **EN 1997-1**: Eq. 7.16 is Rt;k = Rs;k (stored as Rs;d = Rs;k/gamma_s)
  and Eq. 7.12 is Ft;d <= Rt;d; Eqs. 7.6 and 7.7 were swapped; Eq. 8.1 is
  Pd <= Ra;d. Annex C.2 (Eqs. C.3 to C.10), stored as not legible, is typed
  in from the page. Annex B: B.1 is gamma_F = gamma_S;d gamma_f, the tank
  exception is gamma_F = 1 with gamma_E != 1 (stored as gamma_Sd), and
  B.6.2.2 is the gamma_F = 1 case (stored as gamma_F != 1). Annex D's q is
  the overburden or surcharge pressure and the unprinted Nc = 5.14 is gone.
  "Must" is back to the print's "should" or "may" in 2.4.3, 2.4.8, 5.3.3,
  6.6.2, 6.6.4, 7.5, 7.6.1, 11.5.1, 12.1, 12.4 and Annex F.3.
- **Caltrans**: the maximum slope angle is Eq. 4-5-1 as printed (stored as
  sin(beta) <= sin(phi) + c/(gamma h), which the manual does not print);
  D = 1.2 D0 is the Simplified Method's, not the Rigorous Method's; the
  heave factor of safety 1.5 and the anchor-block factor of safety 2 are
  printed as recommendations; Appendix A's Eqs. A-2-12 to A-2-16 and A-3-1
  to A-3-4 and Tables C-1 and C-2 as printed.
- **FEMA P-2082**: the effective damping ratio of Eq. 19.3-1 is capped at
  0.20 (the cap was missing) and the period factor of Eq. 19.3-3 is on
  beta_s, not beta_rd.
- Equation ids: EN 1997-1 "Annex E Eq." is "Eq. E.1", "Annex E" (6.5.2.3)
  is "Eq. E.1 (Annex E)", "Eq. B.6.1.1" is added; FEMA "19.3-G0",
  "21.4-SDS" and "21.4-SD1" say they are unnumbered. No section ids change.
- New tests pin the printed forms: `tests/test_eurocode_7_1_text_equations.py`,
  `tests/test_california_trenching_text_equations.py`,
  `tests/test_fema_p2082_text_equations.py`.

**EN 1997-1 Annex A text: wrong pile factors corrected (build of
2026-11-12, app BACKLOG REF-83 review).** The stored text of Annex A.3.3.2
gave R4 = 1.3 for the base and total resistance of bored piles (Table A.7)
and the base of CFA piles (Table A.8). The standard prints 1,6 and 1,5
(bored) and 1,45 (CFA), printed p. 132. Its key points also said the R4
column was the same as Table A.6's. The coded tables
(`table_a_7_bored_pile_resistance`, `table_a_8_cfa_pile_resistance`) were
right. This text was in release 1.6.0, so a text answer about R4 for
bored or CFA piles from 1.6.0 should be checked again. Every cell of
Tables A.1 to A.17 in the Annex A text was compared with the print and
the coded tables; no other value was wrong. Also corrected to the print:
- The Table A.11 model factors keep their printed force words: 0.85
  "may", 1.10 "should", 1.20 "shall".
- The Design Approach summary quotes 2.4.7.3.4's NOTEs. It had said
  Combination 1 factors "actions and ground strength, not resistance".
  Set M1 is 1.0 throughout, and set R1 is not 1.0 for piles or anchorages.
- No section now says Design Approach 3 is the usual one for slopes,
  which the print does not say (Annex A.3.3.6, Section 11.5.1).
- Three force words the 2026-11-10 build weakened are back to the print:
  11.5.1(11)P "shall be considered" (ground-structure interaction),
  6.6.4(3)P "shall be considered using EN 1998", and 6.6.2(16) "should
  take account of non-linear stiffness effects".
- Also: 9.5.2 Eq. 9.2 is beta <= phi' (the prime was missing); Eqs.
  2.9a/2.9b are on p. 34, not pp. 33-34; 7.6.3.1(4)P block uplift "shall
  be carried out" per 2.4.7.4.

No lookup and no section id changes. The new tests are in
`tests/test_eurocode_7_1_text_equations.py`.

**UFS 3-220-10 (dm7_1) lookups corrected to the printed manual (review of
2026-11-10).** A review of the `dm7_1` functions against the rendered pages
found equations, tables and charts that did not match the print. Results
from the functions below change; anything computed with them before should
be re-run. Pages are printed page numbers.

Equations re-coded as typeset:

- `cpt_friction_angle_robertson_campanella` (Eq. 8-8, p. 402) returned the
  reciprocal: 9.3 degrees where the manual gives 40.5 at qc/sigma'v = 100.
- `cpt_friction_angle_mayne` (Eq. 8-7, p. 400): the vertical stress is
  under a square root; 33.0 degrees became 36.3 at qt 10,000, sigma'v 400,
  Pa 100.
- `fully_softened_friction_angle` (Eq. 8-13, p. 407) had both signs
  reversed: 45.6 degrees where the manual gives 26.8 at PI 40.
- `spt_undrained_strength_stroud_butler` (Eq. 8-26, p. 428) divided where
  the manual multiplies: 4.3 kPa where it gives 93.8 kPa at N 20, PI 30.
- `cbr_from_dcp_nazzal` (Eq. 8-38, p. 456): 9.0 became 11.6 at 20 mm/blow;
  a DCP outside the stated 6.3 to 67 mm/blow is refused.
- `cbr_from_spt` (Eq. 8-39, p. 457) returned about 1e9; the manual gives
  CBR 6.1 at N 10 and 26 at N 30.
- `kozeny_carman_hydraulic_conductivity` (Eq. 6-13, p. 300) and
  `hydraulic_conductivity_kozeny_carman` (Eq. 8-41, p. 462), printed
  identically, returned 7e-8 cm/s and 7.7 cm/s for a sand the equation
  gives 0.072 cm/s; both now return 0.072. Fractions may be decimals
  adding up to 1 or percentages adding up to 100, within 2 % (0.98 to
  1.02, or 98 to 102; the library's tolerance, not printed, there to catch
  percent and decimals mixed up); the total is used as given, not
  normalised, and any other total is refused. A grading summing to 99 %
  is accepted (0.238 cm/s for the two-fraction sand in the tests).
- `hydraulic_conductivity_carrier_beckman` (Eq. 8-42, p. 462): 2.5e-4 m/s
  became 3.5e-9 m/s at e 1.5, PL 25, PI 30.
- `hydraulic_conductivity_benson_landfill` (Eq. 8-43, p. 463) raised an
  overflow error at ordinary inputs; it now gives 3.6e-8 m/s for the
  example in its tests. The page prints no unit for the molding water
  content: the function takes a decimal (a percentage gives k below
  1e-100 m/s) and refuses a degree of saturation above 1.10. The limit is
  the library's, not printed: a little over 1.0 comes from scatter in the
  measured w, dry unit weight and Gs, and the guard is there to catch w
  entered in percent.
- `hydraulic_conductivity_benson_trast` (Eq. 8-44, p. 463) had its four
  coefficients on the wrong terms: 1.5e-8 m/s became 7.9e-11 m/s at PI 25,
  CF 30, standard Proctor, w 0.18, dry unit weight 17 kN/m3, Gs 2.70. The
  page prints no unit for the molding water content. The function takes it
  as a decimal and enters the saturation term in percent; that is this
  review's reading, not a printed statement (as a decimal the same input
  gives 1.4e-7 m/s), and the docstring gives the reasons. A degree of
  saturation above 110% is refused, for the same reason as in Eq. 8-43.
- `well_resistance_factor` (Eq. 5-26, p. 268) was zero at the far end of a
  drain, where the manual's equation is largest: 0 became 1.26 at
  z = Lm = 20, kh/qw = 0.001.
- `drain_spacing_factor(approximate=False)` (Eq. 5-23, p. 267): 0.906
  became 0.936 at n = 5. The default approximation is unchanged.

Tables and charts rebuilt from the print:

- `figure_8_46_f` (Figure 8-46, p. 444) returned 500 to 175; the figure's f
  runs from 6.85 at PI 14.8 (6.78 at PI 15) to 4.24 at PI 64.5, so the
  constrained modulus Mds = f N Pa was 46 to 73 times too stiff, by PI
  (66 at PI 15, 73 at PI 20, 47 at PI 60, 46 at PI 64.5). PI outside 14.8
  to 64.5 is refused.
- `figure_5_6_mu0` and `figure_5_6_mu1` (Figure 5-6, p. 230): mu0 is now
  0.877 at D/B = 5 (was 0.78) and 0.859 at D/B = 20 (was 0.62); mu1 for a
  square load is 0.645 at H/B = 5 (was 0.82, or 0.96 at the old default
  Poisson's ratio of 0.3). The figure is for Poisson's ratio 0.5 only: any
  other value is refused, and the default is now 0.5. `L_over_B` is 1 to
  10 or "infinite".
- `table_8_6_stark_hussain` (Table 8-6, p. 417) now holds the sixteen
  printed rows; the residual friction angle for a clay fraction over 50%
  at 400 kPa and LL 80 is 10.3 degrees (was 26.5). Keys: `lt_20`,
  `25_to_45`, `gt_50_ll_lt_120`, `gt_50_ll_120_to_300`; `700_kPa` added.
- `table_8_9_shansep_m` (Table 8-9, p. 425) lists m by source and soil, as
  the table does, not by test type; it takes `soil` and returns the printed
  row as a dict.
- `table_8_24_cbr_dcp` (Table 8-24, p. 456) now holds the thirteen printed
  rows. Of the six keys it held, only the removed `webster_1992` carried
  printed coefficients: its (292, -1.12) are those of the printed White et
  al. (2018) row for all soils except CL with CBR < 10, now
  `white_2018_all_except_cl_cbr_lt_10`. The other five are not in the
  table.
- `table_4_3_trench_fill` (Table 4-3, pp. 195-196) returns the six printed
  rows (unit weight in pcf, K, mu', K x mu'); for saturated clay K x mu' is
  0.11 (was 0.029).
- `table_4_9_tunnel_behavior` (Table 4-9, p. 205) returns the printed
  ground behavior for the seven printed rows and takes the soil type as a
  second argument.
- `table_5_6_Calpha_Cc` (Table 5-6, p. 254) gains the shale and mudstone
  row (0.03); the table's +/- 0.01 and its source are in the docstring.

Inputs outside the range the manual states or plots are now refused, with
the range and page in the message (values inside the range are unchanged):

- `hydraulic_conductivity_hazen` (Eq. 8-40, p. 458): D10 outside 0.1 to
  3 mm, the range the manual states.
- `fully_softened_friction_angle` (Eq. 8-13) and
  `residual_friction_angle_gibson` (Eq. 8-16): PI above 100, the end of
  Figure 8-13 (p. 408).
- `spt_friction_angle_roads` (Eq. 8-2) and `spt_friction_angle_buildings`
  (Eq. 8-3): N60 above 50, the end of the curves in Figure 8-2 (p. 397).
- `spt_friction_angle_kulhawy_mayne` (Eq. 8-4): N60 above 60, the end of
  the N60 axis of Figure 8-3 (p. 398), or sigma'v/Pa above 3.0. The stress
  axis ends at 3.0 kgf/cm2 (2.90 atmospheres); the limit is taken as
  3 atmospheres, so 291 kPa with Pa given as 100 kPa is answered
  (33.0 degrees at N60 20).
- `spt_undrained_strength_stroud_butler` (Eq. 8-26): PI outside 15 to 62,
  the trendline of Figure 8-31 (p. 428). At PI 5 it returned 1,513 kPa
  for N 20.
- `cbr_from_spt` (Eq. 8-39): N outside 5 to 68, the curve of Figure 8-57
  (p. 458). At N 200 it returned CBR 144,025.
- `spt_friction_angle_wolff` (Eq. 8-5) and
  `spt_friction_angle_hatanaka_uchida` (Eq. 8-6): N1,60 above 60, the end
  of Figure 8-4 (p. 399).
- `schmertmann_time_correction` (Eq. 5-9, p. 232): a time below the
  equation's reference time of 0.1 year.

Coded differently from the print, values unchanged (the docstrings now give
both forms, the pages and the reasons):

- `trench_load_coefficient` (Eq. 4-7, p. 195) has a 2 in the exponent,
  e^(-2 K mu' H/Bd), where the manual prints e^(-K mu' H/Bd).
  `flexible_pipe_trench_load` (Eq. 4-8, p. 197) multiplies by the trench
  width Bd where the manual prints Bc, the diameter of the pipe. Each coded
  form gives the higher pipe load. The review kept the coded forms; the
  library's owner is to revisit them.
- `relative_density_from_dry_density` (Eq. 3-2, p. 141) has
  gamma_d - gamma_d-min in the numerator where the manual prints
  gamma_d - gamma_d-max. The printed form is negative for any soil looser
  than its densest state and so cannot equal the void-ratio form it is set
  equal to; the coded form makes the two sides equal.

Descriptions corrected, values unchanged: the angles of the Table 4-2
strip-load functions (`boussinesq_semi_infinite_load`,
`boussinesq_terrace_load`, `boussinesq_triangular_load`,
`boussinesq_slope_load`) are now described as the table's diagrams draw
them; `corrected_spt_silty_sand` no longer claims a limit of N' = 15 the
manual does not print.

Chapter text (`dm7_1/text/` chapters 3, 4, 5, 6 and 8) now states
Eq. 3-2, 4-7, 4-8, 5-23, 5-26, 6-13, 8-8, 8-13, 8-16, 8-26, 8-38, 8-39 and 8-41
to 8-44 as printed.

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
  2.0) is refused. Top layer stiff, 0.65 < su2/su1 < 1: N_cm stays the
  printed equation's value; `print_note` says the figure's one drawn
  curve there (H/B 0.5; H/2R 0.25) runs up to about 7.5 % below it, and
  `N_cm_drawn_curve` gives that curve's value (strip, 0.85, H/B 0.5: 5.12
  by the equation, 4.74 drawn).
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

**Pavement and UFC soils values checked against the printed pages (review
of 2026-11-10, pave-01 to pave-32).** Every changed value was read off the
rendered page; results and docstrings name the page.

- UFC 3-250-01 Chapter 20 drainage: Eq. 20-17 lacked its factor 2 (layer
  thickness H was half the print), Eq. 20-18 had 0.85 in the numerator
  (H was 0.72 of the print), Eq. 20-4 effective porosity computed the water
  retained (0.088 against the printed form's 0.247 at 110 pcf, Gs 2.65,
  We 0.05), and Eq. 20-11 lacked its 2 (T50 twice the print). Eq. 20-3 is
  kept with (1+e) where the page prints (1-e), as it was coded before
  the review; the result and the first docstring paragraph say so and that
  the owner is to revisit the choice. Eq. 20-4 now raises ValueError when
  the inputs give no drainable pore space (We at or above saturation for
  the dry density), where it returned a negative porosity (125 pcf, Gs
  2.65, We 0.2 gave -0.157).
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
  McKeen-Lytton, Johnson; printed 4-3). Johnson's relation can give a
  negative number (PI 20, H 0, wo 40: -8.648); it is returned with a note
  that it is not a predicted shrinkage.

**Structural lookups checked against the print (review of 2026-11-10,
struct-01 to struct-34).** Values that change:

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
  inches, named in the docstrings and results (`d_units`, `dbg_units`).
  An entry whose printed expression is zero or negative at that depth is
  None, with a `note` naming the entry, its expression and the depths at
  which it is positive; the row's other entries are returned, and the
  call is refused only when every entry is zero or negative (a 30 in WUF
  beam typed as 762 gave UFC m = -58.9; now ValueError). A UFC WUF beam
  51.8 to 89.6 in deep returns its printed secondary m-factor with
  `m_primary` None. An m-factor between 0 and 1 is returned with a
  `note`.
- EM 1110-2-2107 `bolt_grade_check` refuses a grade the manual does not
  name (it answered "not permitted", even for "A325"). The print's own
  spelling, "ASTM 3148" (printed p. 38), gets a message naming the grade
  to pass, 'ASTM F3148'.
- UFC 3-301-01 Eq 16-18a/b (`ufc_structural.wind_speed_conversion_asd`,
  `wind_speed_conversion_fastest_mile`): Vasd = sqrt(0.6) V and Vfm =
  (sqrt(0.6) V - 10.5)/1.05, the radical over 0.6 only as typeset. The
  code took the root of 0.6 V: at V = 150 mph it returned 9.49 and
  -0.96 mph; now 116.2 and 100.7 mph (printed p. 19). The chapter 2 text
  stated the same wrong form and is corrected.
- UFC 3-301-01 Tables 3-1, 7-1 and B-1 (`ufc_structural.table_3_1_*`,
  `table_7_1_*`, `table_b1_*`): height limits are returned as
  `height_limits_ft` (was `height_limits`, no unit), with
  `height_limits_m`: footnote d's 30 m for 100 ft and 50 m for 160 ft in
  Tables 3-1 and 7-1, None for a height the print gives no metric value
  for (35, 40, 65 ft, and every Table B-1 height). `metric_footnotes`
  gives the row's cited footnotes that print a metric height (Table 3-1
  i "45 ft (14 m)", j "60 ft (18 m)", q "60 ft (18.3 m)"; Table 7-1 w
  and Table B-1 footnote 7 "60 ft (18.3m)"); the notes cite "FOR SI: 1
  foot (ft) = 304.8 mm" under Tables 3-1 and 7-1 and footnotes e and f
  (240 ft, 75 m; 160 ft, 50 m) (printed pp. 56-57, 99, 124-126).
- EM 1110-2-2107 Eq 4.3 (`em_2107.seismic_amplification.westergaard_pressure`): the
  printed 7/8 is applied, p = (7/8) wc ac sqrt(H y); 62.4 pcf, ac 0.5,
  H 100 ft, y 50 ft gives 1930.4 psf (was 2206.2; printed p. 28). The
  chapter 4 text is corrected.
- EM 1110-2-2104 Eq 3-5 (`em_2104.loads.earthquake_load_combination`):
  the docstring said every combination takes the factored permanent sum;
  Eq 3-5 is U = 1.0 Sum Lp + 1.0 EQ + 1.0 Ltc (printed p. 26). The result
  adds `permanent_sum_basis`. Following the old docstring, D = 100 with
  EQ = 50 gave 170 instead of 150.
- UFC 3-301-01 Eq C-1 (`ufc_structural.rigid_pipe_fundamental_period`):
  the print gives L = sqrt(C pi Ta sqrt(E I_g / w)) and defines neither g
  nor I_g; read as E x I x g (I the pipe's moment of inertia, g gravity,
  confirmed by Table C-1), Ta = L^2/(C pi) sqrt(w/(E I g)). The code had
  C L sqrt(w/(E I g)) and called spans to
  about 757 ft rigid. New keyword `g` (386.4 in/s^2 default). A 1 in.
  40S steel pipe at Table C-1's 7 ft 0 in gives Ta 0.059 s, rigid, and
  8 ft is not (printed pp. 137-138).
- Wood Handbook combined bending and axial load, compression
  (`wood_handbook.combined_bending_axial_stress`,
  `eccentric_bending_axial_stress`): a compressive P adds P/A on the
  concave edge and P e0/S to fb0. Example: concentric 14.5 / 10.5 ->
  10.5 / 14.5 (edges were swapped); eccentric 13.25 / 9.25 -> 11.75 /
  15.75 (printed p. 9-12).
- Wood Handbook Figure 9-14 (`wood_handbook.figure_9_14_coefficients`):
  traced off the rendered figure (printed p. 9-12). At a/h 0.1, At / Ac
  / B = 0.177 / 0.074 / 0.277 e-4 (was 0.05 / 0.03 / 0.35 e-4); A was
  too low below a/h 0.3 and 20-55 % too high above 0.4. a/h below 0.02
  is refused (the curves meet at the origin). Example: Eq 9-21 criterion
  0.90 (no crack) -> 2.17 (crack).
- UFC 4-023-03 and GSA Alternate Path gravity loads (`*_collapse.
  alternate_path`): live and snow load together are refused; both
  documents print 1.2 D + (0.5 L or 0.2 S), and the code added both.

Judgment calls where the printed equation cannot be right as typeset
(ruled by the lead, 2026-11-10; each function's first docstring
paragraph and its result give the printed form, the form used, the page
and the reason):

- Wood Handbook Eq 9-24 (`torsional_shear_stress_rectangular`): printed
  fs = T/(beta h b^2); used fs = beta T/(h b^2), because Figure 9-15's
  beta (3 to 4.8) is the classical multiplier. 100 x 100 mm, T = 1 kN m:
  0.208 -> 4.81 MPa (printed p. 9-13).
- Wood Handbook Eq 9-32 (`critical_ponding_spacing`): the print defines
  rho as "density of water (1,000 kg m-3, 0.0361 lb in-3)"; the SI
  default is now the unit weight 9,810 N/m^3 (1,000 gave s_cr 9.81 times
  too large). The parameter is renamed `unit_weight_water` (was
  `rho_water`, no alias; the result key follows), and a value from 900
  to 1,100 is refused as a mass density (printed p. 9-15).
- Wood Handbook Eq 9-41 (`elastic_buckling_stress_edgewise_bending`):
  printed (1.44 E/le)(d2/d1) is not a stress; used 1.44 E d2^2/(le d1)
  (printed p. 9-17).
- EM 1110-2-2107 Appendix F (`hydrostatic_horizontal_component`,
  `resultant_angle_from_horizontal`, `trunnion_reaction_force`): values
  unchanged; the docstrings now state that Eq F.10's typeset sign,
  theta_p = tan^-1(Ph/Pv) and theta_Rt = tan^-1(Rtx/Rty) contradict the
  worked example and its tables, which the code follows (printed pp.
  427, 436, 440, 445). For Eq F.10 only the integral's form gives Table
  F.3's Ph = 50.0; the typeset form gives -50.0 and the worked example's
  own displayed equation 30.0. `trunnion_reaction_force` returns the
  magnitude of theta_Rt: the example computes +0.2653 from Rtx = -1,336
  and Rty = -363.0, and Table F.8 lists the components unsigned beside
  -0.2653 without saying what the sign means.

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
- More page and equation citations: EM 1110-2-2107 para 5.2.1.1 (was
  5.2.1.2), Eq D.8 p. 392 (was 400), `amplification_factor` is Eq D.8
  (was D.10, its top-of-structure case), the trunnion Rt / Ft / Mt
  functions cite paragraph F.4.2.4's unnumbered equations (were "F.17",
  the QT equation); Wood Handbook Eq 9-3/9-4 p. 9-2, Eq 9-10/9-11 p. 9-5,
  Eq 9-16 p. 9-10, Eq 4-6 p. 4-3, Eq 4-15/4-16 p. 4-12.
- `ufc_collapse.effective_wf_for_nonuniform_load` adds `case` and
  `action`: when the bay loads differ by 25 % or less but the max-load
  area is over 25 %, the print allows only the maximum floor load
  (sub-areas are for a difference over 25 %).
- Docstrings that misstated the print: EM 1110-2-2104 Eq B-33 is clean on
  the page (not "corrupted"); in Appendix C-3 the compression steel does
  not yield (the printed 0.0148 is the tension-steel strain); Eq B-53's
  typeset form is a misprint the code does not follow; GSA Icr 19160
  gives 325.46 kip/in, 16423 gives 279; GSA Eq 3.18's Phi is left out by
  default, as Figure 3.19 and Appendix D do; UFC 3-301-01's tie-rod
  "118 kN" for 40 kips is a misprint (178 kN), noted in the result; Wood
  Handbook Eq 4-3's printed anchors (267 % / 44 %) fit a cell-wall
  specific gravity of 1.5, not the printed 1.54.
- More wording from the print: GSA Tables 6 and 8 footnote 2 applies the
  one acceptance column to primary and secondary components "where the
  full backbone curve is explicitly modeled"; UFC 3-301-01 commentary
  [C] 503.12 is on printed p. 84, the page after the normative text; Eq
  16-18b prints 10.5 with no unit; EM 1110-2-2104 Eq D-6's moment is
  M_DS as printed (was "MDL"; the result key stays `mdl`).

**Build: the heave methods UFC 3-220-07 prints (app backlog REF-91).**
`ufc_expansive` now holds the manual's printed ways to predict heave, in
place of the removed correlations, each read off the rendered page:

- `figure_4_1_potential_expansiveness`: Van Der Merwe's potential
  expansiveness PE (0, 1/4, 1/2, 1 inch/foot) from the PI and clay
  fraction of the whole sample, Figure 4-1 (printed 4-2), its regions
  taken at the labelled axis ticks; outside the frame (70) refused. The
  drawn lines sit up to about 0.8 % clay and 0.6 PI off the ticks and the
  chart's PI marks agree only to about 0.5 PI, so the result says a point
  within about 1 % clay or 1 PI of a boundary may lie in the next region.
- `eq_4_1_van_der_merwe_heave`: total heave at the ground surface,
  delta_H = sum of 10^(-D/20) x PE over 1-ft increments, Eq. 4-1 (printed
  4-1); 10 ft of very high soil gives 5.604 in.
- `eq_5_2_potential_vertical_heave`: N x DX x sum (ef - eo)/(1 + eo),
  Eq. 5-2 (printed 5-2), N from 1/3 to 1 (0.33 or 0.333 is taken as 1/3,
  and the result says so); one element is Figure 4-2's
  Sp/100 = (e1 - eo)/(1 + eo).
- `eq_5_3_to_5_5_equilibrium_pore_water_pressure`: the saturated,
  hydrostatic I and hydrostatic II profiles, gamma_w 0.0312 ton per cubic
  foot (printed 5-3 to 5-4).
- `eq_5_8_consolidometer_heave`: delta_H/H = cs/(1 + eo) log(sigma_s /
  sigma'_v) with sigma'_v = sigma_v - u_w, Eqs. 5-8 and 5-9 (printed 5-5),
  "log" taken as log10 (Figure 4-2's log pressure axis). A u_w left out is
  taken as 0, the saturated profile the print says to use when nothing
  else is known, and the result names those layers with p. 5-3's
  sentence. A layer past its swell pressure gets no magnitude (heave
  None, flagged, listed in `layers_left_out`): p. 4-4 says only that net
  settlements will occur, and c_s, the slope from the seating to the
  swell pressure, does not give them; the total is over the swelling
  layers.

No stored statement changed; the package keeps no chapter text.

**Build: figure catalog rows for printed figures that had none (app backlog
REF-08, REF-84).** A figure without a catalog row can be neither found by
`figure_search` nor read by the app's vision tool. 428 rows were added and
no existing row changed:

| Catalog | Rows before | Added | After | Figures added |
|---------|-------------|-------|-------|---------------|
| `gec_5` | 256 | 93 | 349 | 11-10 to 11-26, chapters 12 and 13, Appendix 2 (A2-1 to A2-40) |
| `gec_13` | 33 | 206 | 239 | chapters 2-5 (Vol I) and 7-10 (Vol II) |
| `fhwa_soils_foundations` | 331 | 60 | 391 | Appendix A (A.1-1 to A.9-1), D-10 |
| `gec_6` | 57 | 29 | 86 | Appendices B and C (B1-1 to B5-2, C1-1 to C2-4) |
| `gec_4` | 73 | 17 | 90 | Appendices A, B and D (A-1 to A-10, B-1 to B-5, D-1, D-2) |
| `gec_7` | 78 | 11 | 89 | 3.22 and Appendices A, B, C and G |
| `micropile` | 132 | 10 | 142 | the sample problems' S1-1 to S1-7, S2-1 to S2-3 |
| `eurocode_7_2` | 19 | 2 | 21 | Annex B's B.4 and B.5 |

- Each row points at the page that prints the figure's label and caption
  and holds a picture or drawing; one row in five, by a seeded draw, was
  looked at on the rendered page. The caption is the one printed under the
  figure, where a List of Figures words it otherwise (GEC-5 12-24, GEC-13
  4-17). Captions whose symbols the text layer garbles were typed from the
  page (GEC-5 "su/σ′vc").
- Figures printed turned on the page carry `read_notes` saying which way to
  turn it: GEC-5 A2-6 and A2-9; FHWA NHI-06-089 A.2-9 to A.2-12 and A.4-3;
  micropile S1-2, S1-6 and S1-7.
- Placed by hand (`--overrides`) where the scan cannot: FHWA A.2-3 and
  GEC-6 B3-4, typed text in a box with no picture; FHWA A.7-2, filed under
  the number its text cites though its caption prints "A7-2"; EN 1997-2
  B.5, whose text layer reads "Figure B.S".
- Descriptions come from the chapter text that cites the figure; appendix
  figures, which have no chapter text, have none, as the appendix rows
  before them.
- `scripts/build_figure_catalog.py --add-missing <package>` finds the rows
  and adds them without touching the others (`find_missing`, `add_rows`);
  the full build is unchanged. Tests: `tests/test_catalog_added_rows.py`.

**Fixes from the 2026-11-10 review of the core layer.** Every page, number
and caption below was read off the rendered print.

- **A section number names one section** (core-01, core-08). Twenty-two
  numbers were held by two sections of one reference, and the two fetch
  layers returned different ones. GEC-13 chapter 1 is now numbered
  `1.<printed number>`, the AASHTO 1993 Guide's numbers carry their Part
  (`II-2.3.5`), and UFC 3-250-11's appendices are `A-1`, `B-1` and `C` as
  printed. Both fetches refuse a number two sections hold, and a
  `section_id` that is not text (7.10 sent as a number arrived as 7.1).
  - A GEC-13 number that chapter 1 prints names chapter 1's section, in
    both fetches. "8.2.7" still returns chapter 8's Jet Grouting, with a
    note that chapter 1 prints 8.2.7 too, as `1.8.2.7` Step 7: Consider
    Project Risks (p. 1-46). The error for "1.3" names `1.1.3` Focus and
    Scope (p. 1-4) first.
- **A figure number the catalog holds twice is never the first row**
  (core-02). `figure_get` and `resolve_pdf` take `pdf_page_index`, and a
  repeated number is refused without it, naming each row's page. GEC-11
  Figure 5-11 had been catalogued as a second 5-14, and GEC-12's Appendix D
  continuation sheets each had the first sheet's page.
  - `figure_search` gives a figure printed over several pages one hit: its
    best-ranked sheet, with `pages` listing each sheet's `pdf_page_index`
    and `printed_page` (GEC-12 D-1 to D-4, UFC 3-250-01 D-3). Rows of one
    number with different captions stay apart (UFC 3-250-01 F-21, GEC-13
    6-14). Before, the sheets took the places of other figures, so
    "driven pile design process flow chart" lost GEC-12 Figure 7-32 from
    its top ten. A list no figure repeats is unchanged.
- **`_linterp` refuses a NaN or infinite input** (core-04).
- **Search results say how they matched** (core-05). `reference_search` and
  `figure_search` hits that do not hold every word carry `match`
  (`"synonyms"`, or `"any word"` with `lacks`). A hit with every word but
  not a phrase of the query (a hyphenated term runs as the phrase of its
  parts: "5-2" as "5 2") is `"all words"` with `not_as_phrase`; it had been
  "any word" lacking nothing. This is worked out after the ranking, so no
  hit moves. With `max_chars` the result adds `matched` (the loosest mark:
  any word, synonyms, all words), `words_not_found` and a sentence on the
  note. An empty result names the scope, what was tried and the words
  nothing there holds.
- **An unknown reference or chapter is an error, and a reference name means
  one thing** (core-06, core-09). A search scoped to either returned `[]`.
  A figure lookup no longer reads a loose name ("FHWA", "pile") as every
  catalog it touches.
  - Both searches read a `reference` by one rule
    (`_retrieval_db.search_scope`): the id, another spelling of it
    (`GEC-10`), or a report number its files carry. A volume's own number
    searches that volume alone: `FHWA-NHI-06-089` is Soils and Foundations
    Vol II, and the result adds `report_number` and a note naming the id
    that searches every volume. Before, `figure_search` read the number as
    the whole manual and `reference_search` refused it. A name that is not
    an id adds `resolved_reference` in both.
  - `"dm7"` (the app's name for UFS 3-220-10 and UFC 3-220-20) is refused by
    both searches with the same error naming `dm7_1` and `dm7_2`;
    `figure_search` had searched both. `figure_get` still reads it by the
    figure asked for.
  - Every `figure_search` and `reference_search` hit carries
    `reference_id`, its volume's report number, so the plain list shows the
    volume a report-number scope kept to (only the `max_chars` form carries
    the note). `references_agent.reference_search` returns the `max_chars`
    form (14,000 characters, the app's size) and takes `offset`. It was a
    plain list of hits, which could not carry the scope note.
  - A report number matches by its designation as well as by the whole
    stored text. That is the text up to the first space after the number,
    and a standard's number with or without its year. So "FHWA-NHI-05-037"
    names fhwa_pavements (stored with its title after the number) and "EN
    1997-1" names eurocode_7_1 (stored as EN 1997-1:2004); both had been
    refused. Every stored id's designation resolves in both searches. A
    number that ends more than one designation is refused, naming them:
    "2-2007" (EN 1997-2:2007 and UFC 3-220-07) had searched both catalogs.
  - Every function that takes a reference reads it the same way:
    `reference_get`, `retrieve_section`, `search_sections`,
    `list_chapters`, `load_chapter`, `figure_get`, `resolve_pdf` and the
    agent's `lookup_reference`, as the searches do. `reference_get("gec12",
    "7.2")` had been refused. An unknown name, or `dm7` in a text fetch,
    gets the search's refusal, with each function's own error type (`KeyError`,
    or `FileNotFoundError` in `_retrieval`).
- **`search_sections` with no section holding every word** (core-07) returns
  the ranked search of that reference, each hit marked `match` ("all
  words", "synonyms", "any word" with `lacks`), 10 by default. The fitted
  result has no `total_hits`. A search that finds hits lists the same
  sections, except that hits of equal score are ordered by section id, so
  they reorder where core-01 renamed ids: `search_sections("aashto_1993",
  "layer coefficient")` ranks 5-7 and `search_sections("ufc_stabilization",
  "sulfate")` ranks 7-10.
- **A skipped local pack is named** (core-10). `list_indexed_references`
  gives a partly skipped pack its `problems`. It lists a pack skipped whole
  with no sections and its problems, and a search naming that pack quotes
  them. A manual whose volumes' files carry titles of their own is listed
  once, with `reference_titles`.
  - A pack folder named as a built-in reference (`gec_12`) has its problems
    filed under its path, not on the built-in's listing.
- **A database knows what it was built from** (core-11). Both search
  databases store a signature of their source files and are rebuilt when it
  differs. Before, a chapter file or catalog that was deleted, added or
  restored with an older date kept the old text. The text layout version
  is 4 (each section row stores its chapter file's `reference_id`); the
  figures database has `user_version` 1.
- **An unreadable built-in source fails the build** (core-12), naming the
  file and keeping the database already there. A local pack's file is still
  skipped and named.
- **Each volume is cited by its own cover's number** (core-13). GEC-11 Vol
  II rows are FHWA-NHI-10-025, GEC-12 Vol III rows and Appendix D are
  FHWA-NHI-16-064, and Soils and Foundations Vol II rows are
  FHWA-NHI-06-089. GEC-13 chapter 6's title says Volume II. GEC-12 Vol II's
  rows and chapters 9-18 are FHWA-NHI-16-010, the number on its Technical
  Report Documentation Page; its cover prints Vol I's 16-009, taken as a
  misprint, and a figure lookup by either number still finds them.
- **`load_chapter` finds a chapter file by its `chapter` field** (core-15),
  so the 17 files named otherwise (prologues, appendices, Eurocode 7 Part 2
  sections) load. A missing chapter's error lists the chapters in numeric
  order (it gave UFC 3-250-11's as "6, 7, 8, 1, 2, 3, 4, 5").
- **Catalog rows lead to their figure.**
  - Pages corrected: UFS 3-220-10 Figures 1-13, 3-1, 5-4, 6-9 (the figure
    is on the page before its caption), GEC-10 4-5, GEC-14 A-1 to A-3 and
    GEC-9 6-17.
  - Numbers as printed: UFC 3-250-01 C14-5B, and D-3 as four sheets.
    `figure_get` reads a bracketed part letter, so "Figure 9-37(a)" finds
    `9-37a`.
  - Chapters filled in: GEC-7 and GEC-8 rows had none, and GEC-4 rows had
    their own figure number as the chapter.

**Build of 2026-11-10: FHWA-NHI-05-037 Geotechnical Aspects of Pavements,
chapter text read off the print (app backlog REF-82).** The stored text was
23 hand-written sections in chapters 3, 4, 5, 7 and 8, ten of them wrong in
substance, several under section numbers that are other subjects in the
print. `scripts/build_printed_text.py` now reads this manual
(manifest `fhwa_pavements.json`, `"text_build": "printed"`): every numbered
heading of the printed contents is a section with its printed number and
title, the body in the print's own wording with a `[p. 5-53]` marker where
each printed page starts, and each figure and table listed under the section
that prints it. Chapters rebuilt so far: 1 (Introduction, 15 sections) and 2
(State Agencies, 2 sections; the host agency's questionnaire), neither
stored before; 3 (Geotechnical Issues in Pavement Design and Performance,
13 printed sections, was 5 paraphrased ones), with Eqs. 3.1 to 3.10 typed in
from the page and written where the page prints them. Two are typed as
printed with a note: Eq. 3.5 prints 7.3 log(D + 1) where Eqs. 3.3 and 3.9
print 7.35, and Eq. 3.9 prints 1.64x10^7 where Eqs. 3.3 and 3.5 print
1.624×10^7. Chapter 4 (Geotechnical Exploration and Testing, 23 printed
sections, was 3): the stored 4.5.5 gave the DCP relation CBR = 292/DCP^1.12
and ASTM D6951 and D4429, which that section does not print; the relation is
printed in Table 4-9 (p. 4-39, after the 4.5.6 heading) with two more for
clays and no unit, and the text now says so and points to `cbr_from_dcp`'s
note (mm per blow). The stored 4.7.3 discussed Table 4-14; the printed 4.7.3
is Subsurface Profile and Table 4-14 is in 4.7.2, now typed in from pp. 4-65
and 4-66 with the silts, clays and peat rows. The lookup
`table_4_14_soil_as_pavement_material` held only the gravel and sand rows,
one row each for GM and SM, and said the printed table covered gravels and
sands only; it now holds all 17 printed rows, every cell as printed (GM and
SM each as a "d" and a "u" row, ML to OH and Pt from p. 4-66), with each
row's major division and page; "GM" or "SM" alone returns both of its rows,
and the page's footnote on the d/u split comes with them. The
SPT correction in Table 4-8 keeps the number the page gives it, (5-1).
Chapters 5 to 8 followed (2026-11-11 and 12), so all eight printed chapters
are built, 200 sections in all: 5 (Geotechnical Inputs for Pavement Design,
39 sections, was 5) with Eqs. 5.1 to 5.69 typed in from the page; 6
(Pavement Structural Design and Performance, 25 sections), not stored
before, with the 1993 AASHTO example calculations typed in (pp. 6-5, 6-22,
6-32, 6-42); 7 (Design Details and Construction Conditions Requiring Special
Design Attention, the title on the chapter's first page, where the contents
print "Subgrade" for "Construction"; 49 sections, was 3) with Eqs. 7.1 to
7.6 and the second "Eq. 7-5" of p. 7-42; 8 (Construction and Design
Verification for Unbound Pavement Materials, 24 sections, was 5). Sections
over 14,000 characters are stored in lettered parts (5.2.2.a, 6.2.2.a,
7.6.5.a, 8.4.4.a and others), the letters not printed. Tables the text layer
scrambles are typed in from the rendered page: 4-14, 5-3 to 5-6, 5-8, 5-18,
5-24, 5-28, 5-30, 5-34, 5-35, 5-41, 5-49 to 5-54, 5-56, 5-57, 6-5, 6-8, 6-10,
7-1 to 7-3, 7-11 to 7-13, 7-16, 7-19 to 7-21, 8-1, 8-3 (printed "Table 8.3")
and 8-4. Table 7-18 is printed as a picture and is not typed; Tables 7-5 to
7-10, 7-14, 7-15, 7-17, 7-22, 7-23a/b, 8-2, 8-5 and 8-6 keep the text
layer's row order. Every formula line of chapters 1 to 8 was read against
the rendered page, and a new test fails on the patterns the text layer
leaves where it scatters a formula (an isolated prime, lone digits beside an
equals sign, "= = =", a formula line whose brackets do not pair, a sentence
repeated back to back). Appendices A to F (Terminology, the Main Highway
example project, the 1993 AASHTO and NCHRP 1-37A design methods, the boring
log key, admixture content for subgrade stabilization) are not built.
Statements that changed in substance:

- Eq. 3.5's last term is typed with the page's brackets,
  (4.22 – 0.32pt)[log(Sc/215.63J)(...)]; the stored form took the log of the
  whole product, which is Eq. 3.9's form.
- 4.5.4: the two FWD back-calculation relations (d0 from Ep and MR, p. 4-21;
  MR = 0.24P/(dr r) with r ≥ 0.7ae, and ae, p. 4-22), which the text layer
  dropped, leaving only their symbol lists, are typed in.
- The stored 5.3.3 was Compaction Characteristics: the printed 5.3.3 is
  Problem Soil Identification (Tables 5-23 to 5-25, swell and collapse), and
  compaction (Tables 5-15, 5-16, 5-18) is in 5.3.2. The stored 5.4.7 was
  Swell and Collapse Potential: the printed 5.4.7 is Interface Friction. The
  stored 5.5 was Drainage Inputs: the printed 5.5 is Thermo-Hydraulic
  Properties, with the drainage coefficients (Tables 5-49, 5-50) in 5.5.1.
- The stored 7.4 was Stabilization (Lime, Cement, Asphalt) and
  Geosynthetics: the printed 7.4 is Compaction; stabilization is printed in
  7.6 (7.6.3 to 7.6.5) and treated bases in 7.3. 7.2 keeps its subject under
  its printed title, Subsurface Water and Drainage Requirements, and 7.5.6
  under Frost-Susceptible Soils.
- 7.5.6, Table 7-12: all silts, very fine silty sands and clays with PI
  under 12 are frost group F4. The stored text put clays and all silts in F3
  and only varved sediments in F4. The lookup `table_7_12_frost_susceptibility`
  had six rows one group lower than the page (gravelly soils 10-20 % fines in
  F1; gravelly soils over 20 % and sands over 15 % in F2; all silts, very
  fine silty sands and clays with PI under 12 in F3), so it returned silts
  as "High" where the page prints "Very high". It now returns every cell as
  printed, in the page's order, with the page's dash where no percentage is
  given and its "Varied clays" noted (the varved clays of p. 7-52 are
  probably meant).
- The stored 8.4.5 was Chemical Stabilization and Base/Subbase Construction:
  the printed 8.4.5 is Stabilization, and base and subbase construction is
  8.4.6. Table 8.3 (the five example soils of 8.3.2) is typed in with their
  limits, gradation, density, classes and resilient modulus constants.
- Typed as printed, each with a note naming the page: Eq. 5.15 (1000 + 555R)
  beside Table 5-34 (1155 + 555R); Eq. 5.17 (ES and EBS); the bound of Eq.
  5.34; Eq. 5.39's (3/4)(OCR/OCRmax); Eq. 5.65 (9.7e^–4); Eq. 5.66 (haev and
  have); Table 5-18's A-6 "10.30"; Table 5-57's 1 m/s = 3.25 ft/s; p. 6-42's
  SN1 = 5.67 – 0.91 = 4.76 where SN is 5.76; Eq. 7.2's S1 (the text prints
  Sl); Eq. 7.5's unclosed bracket; p. 7-26's "0.13 ft3/day (6 ft3/day)";
  slips in Table 7-20; Table 8.3's K1 "10 387"; p. 4-59's boring log key "in
  Appendix D" (it is Appendix E) and p. 8-9's lime pH test "in Appendix E"
  (it is Appendix F).

The script gains options a manifest opts into
(`contents_format` and `list_format` "lines", `header_end`, `page_label`,
`front_matter_header`, `equation_numbers` "parenthesized_dot",
`title_lines`, `headings_on_listed_page`, `heading_overrides`,
`typed_tables`, `text_fixes`, `formulas_in_body`, `table_functions`, and
`implemented_in` and `description` on a `printed_equations` entry); without
them it builds as before (the Soils and
Foundations rebuild test is unchanged).

**FHWA-NHI-05-037 chapter text and figure catalog: fixes from the build's
independent check (2026-11-12).** Each was read from the rendered page.
- Signs: the manual sets ≥, ≤, ✓, the Table 7-11 symbols, list bullets and
  table dashes in symbol fonts whose text layer gives other characters ("$"
  for ≥, "#" for ≤, "3" for ✓). The build now reads them through a table
  checked against the page (manifest `symbol_fonts`, with `symbol_fonts_checked`
  for the characters that need no mapping) and reads a raised "o" as a degree
  sign (`raised_o_degree`); a test fails on any symbol-font character the
  table does not cover. Exponents and degree signs the text layer flattened
  are as printed.
- Tables typed in again from the page: 1-1 to 1-3 (each X under its own
  column), 4-13 (every row and note, note e's formulas), 7-23a and 7-23b
  (each cost on its own method's line).
- Captions: the build had cut the sources and unit conversions after a
  caption; they are back (`captions_as_printed`), with notes where the
  printed conversion is wrong (1 pci = 0.271 MN/m³, not 284; a 2,000-lb ton
  is 8.9 kN, not kPa; Figure 5-5's sieve openings). Nine captions printed in
  a section but missing from its list are listed (`captions_listed`). Each
  section's list gives the caption the page prints where the List of Figures
  or Tables words it otherwise, 37 of them (`list_captions_as_printed`):
  Figures 6-5 and 6-6 are flexible pavement sections, not rigid; Figure 5-11
  is granular base stiffness, not subgrade; Figure 5-22 is a3, not a2; Table
  6-21 has bedrock at 4 ft, not 3 ft.
- Figure catalog: its captions were already the page's; 22 rows where the
  List of Figures differs quote it in `read_notes`, Figure 8-11's caption is
  complete, and the printed slips above are noted there too.
- Rows under their printed labels: Table 5-44 (layer coefficients for
  existing pavements) prints each material once, beside the first row of its
  group, and the text layer had put the stabilized base coefficients under
  AC Surface and the granular 0.10-0.14 under Stabilized Base. It and Tables
  5-32, 5-58, 7-9 and 7-10, mis-assigned the same way, are typed in from the
  page with the label on every row; the other 92 tables not typed in were
  each checked on a render.
- Ruled signs: the manual also sets ≥ and ≤ as ">" or "<" with a short rule
  drawn beneath. The build reads them (`ruled_comparison_signs`): Table
  5-16's eight "≥ 95" cells, Table 7-5's "≥ 50%" heads and note, and Table
  5-8's first hierarchy sign (was [?]).
- "ψ ≥ 0.1 sec^-1" (pp. 7-30, 7-76) keeps its raised -1, the only negative
  exponent printed after a unit.
- Table 4-13's SANDS head is kept as printed, with a note that it overlaps
  the GRAVELS head.
- The new manifest keys are off unless a manifest sets them; only
  fhwa_pavements does.

**Build of 2026-11-10: GEC-10 chapters 6 (Rebar Cages) and 8 (Drilled
Shaft Design Process) rewritten from the print (app backlog REF-81).** The
review found 9 of the 12 sections of chapter 6 and 2 of the 3 of chapter 8
written from memory. Both chapters now hold the printed sections in the
print's own wording, with a `[p. 6-5]` marker where each printed page
starts; Tables 6-1, 6-2, 6-3 and 8-1 to 8-4 and Eq. 8-1 are typed in from
the rendered pages, and each figure and table is listed under the section
that prints it. Printed Section 8.1 (pp. 8-1 to 8-17, Blocks 1 to 22 of
Figure 8-1) is over the tools' size limit and is stored as 8.1 and parts
8.1.a to 8.1.d (the letters are not printed). Statements that changed:

- 6.3: "maximum bar spacing should not exceed 6 inches" is gone. The print
  (p. 6-5) gives a minimum: clear distance not less than the greater of
  five times the maximum aggregate size and 5.0 in. (AASHTO Art.
  5.12.9.5.2); eight times the aggregate for tremie concrete (Dees and
  Mullins, 2005); where tremie placement is anticipated, many agencies
  require 5 in. and at least ten times the aggregate.
- 6.4: the unprinted spiral limits (3 in. minimum and 6 in. maximum pitch,
  No. 3 at 12 in., bar size by shaft diameter) are gone. Printed: a pitch
  under 5 in. causes flow problems (p. 6-8), Caltrans' bundled hoops give at
  least 5 in. clear, and the ACI development length is 0.04 A_b f_y/[(f'_c)^0.5]
  (p. 6-7). Transverse bar sizes for handling are in 6.7 (p. 6-17): No. 5
  from a 4 ft cage, No. 7 and No. 8 at 8 ft.
- 6.5: the unprinted 2 ft minimum lap and 125 % couplers are gone; printed:
  not more than 50 per cent of the splices at any one level (p. 6-9).
- 6.8 and 6.9: sizing hoops are fabrication guides spaced 8 to 10 ft
  (p. 6-17), not cover spacers; the cover is 3, 4 and 6 in. for shafts up to
  3 ft, between 3 and 5 ft, and 5 ft and larger, and the annular space at
  least five times the largest coarse aggregate (p. 6-18), where the old
  text said "typically 3 inches".
- 6.6, 6.7, 6.10, 6.11: statements the pages do not make are gone (precast
  column pockets, anchor bolts, storage on blocks, a required lifting
  analysis); the printed limits are stored: shaft cover around 6 in. and a
  shaft 6 in. larger than the column, No. 15 gauge tie wire as the minimum,
  internal bracing at a length to diameter ratio of 8 or more with No. 8
  bars, rigging connections at a factor of safety of 2 or more, Table 6-3.
- 8.1: the blocks are the printed Blocks 1 to 22 (Block 16 is plans and
  specifications; construction is Blocks 17 to 22); Tables 8-1 to 8-3 are
  typed in beside Table 8-4.
- 8.2: "minimum 5-10 load tests required" is gone: p. 8-17 gives no number.
  It says fitting to the ASD factor of safety is an interim approach and
  points to Allen et al. (2005) for the calibration steps.

Tests: `tests/test_gec10_ch06_ch08_printed.py` (64).

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
    differ from the table's kPa column; the values held there, 29,000 -
    48,000 and 48,000 - 76,000 kPa, are the kPa the table prints for 600,
    1,000 and 1,600 ksf in its other rows (the note said "48 kPa per ksf",
    which gives 28,800 and 76,800) (gec-47).
  - `table_4_5_pipe_properties` (Table 4-5, p. 4-33): values unchanged.
    The table prints no Fy column; note (4) reads "Fy = 241 MPa (36 ksi)",
    and 36 ksi is the 248 MPa the lookup returns for ASTM A519/A106 and
    the table's printed yield strengths imply (the 139.7 x 12.7 row's
    1,270 kN implies 250.6 MPa). A519/A106 results now carry a
    `print_note` saying so and every result a `fy_basis` naming the note
    (gec-47, lead's ruling).
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
    `table_7_8_api_design_parameters` (Table 7-8, p. 253): a friction angle
    between the printed rows (15 to 35 degrees, by density class and soil)
    is still interpolated, and the result now says the interpolation is
    not printed (gec-45).
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
    `8_6`) refuse a filter that matches no row, naming the rows,
    instead of returning an empty list (gec-37). Table 1-2's and Table
    1-6's names as printed: "PVDs, with and without fill preloading"; Table
    1-6's two lightweight fill rows in full (Granular Fills was shortened to
    four materials); Table 1-2's compressible columns "All soil types except
    very soft soils low undrained shear strength" (the code added "with").
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
    curves are read from 0.25 to 6 k/ft2 (12 to 287 kPa); the chart draws
    them from 0, and the refusal below 0.25 k/ft2 is the library's, as the
    docstring and the message say. A point left of the 15 % curve or right
    of the 100 % curve is refused; it returned 15 or 100 (gec-10).
  - `figure_4_2_friction_angle_from_density` (Figure 4-2, p. 35): the
    printed mesh of relative density lines between the ML and GW lines. The
    0 % line is 27.5 degrees at 17.3 kN/m3 (it returned 30.0). A dry unit
    weight the chart does not plot at the given relative density (22.0
    kN/m3 at 0 %, which returned 33 degrees) is refused (gec-13). The
    docstring describes the shaded caution area as drawn: between the SW
    and GW lines up to the 100 % line, above a thin line from the SW line
    at 75 % through the GP label to the GW line at 50 % (it said "about the
    GP to GW range above 50 %").
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
    not the table's and reads up to about 13.5 % below a logarithmic
    interpolation between the rows 10 and 100 (gec-33).
- **GEC-7 soil nail walls (FHWA-NHI-14-007).**
  - `figure_4_3_friction_angle_spt` (Figure 4.3, p. 79): the six curves
    rebuilt from the rendered page; the points read are in the comment
    above the data. On the curves sigma'vo/Pa = 0.5, 1.0, 1.5, 2.0, 2.5 and
    3.0 they were at most 8.3, 7.6, 5.9, 5.3, 4.9 and 3.9 degrees low
    (toward the high-N60 end of each curve) and at most 3.9, 3.5, 3.9, 3.9,
    3.3 and 3.4 degrees high (at the low-N60 start of each curve, up to
    N60 = 4.5, 6, 8, 10.5, 13 and 15.5 respectively). N60 = 22 at
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
    sands to 40 degrees and gravelly soils to 45 (gec-22). N60 = 50 is
    Dense, the row that prints it ("30 to 50"; Very Dense is "> 50"); it
    returned very dense. At N60 = 4, 10 and 30, each printed in two rows,
    the upper row is returned as before and the result names the lower
    one (`also_printed_in`, `note`).
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
  - `table_4_10_site_coefficient_fv` (Table 4.10, p. 95): values and
    headings unchanged (they match GEC-12 Table 7-29). Site class F is
    refused with the table's note (1), "A site-specific dynamic site
    response analysis must be performed in these cases." (it said
    "Unknown site_class"); Table 4.9's refusal quotes the same note. The
    docstring cites the table as headed, "(Kavazanjian 2011)" (it said
    AASHTO 2014).
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
    text of p. 10-21 (the lookup returns the table's 0.50, ruling G1
    below); qu should not exceed
    the shaft concrete's strength (p. 10-21, not checked); Eq. 10-20 is in
    D, the depth of embedment (gec-43).
  - Lead's rulings G1-G3 on the review's three GEC-10 questions:
    `table_8_4_resistance_factor('side_rock_compression')` returns the
    table's 0.50 with a `print_note` quoting p. 10-21's 0.55 "as
    presented in Table 8-4" (G1). `equation_10_21_rock_socket_side`
    quotes pp. 10-21 to 10-22, "Kulhawy and Prakoso (2007) suggests a
    mean value of C = 1.9 with use of Equation 10-22 for roughened
    sockets", and says C appears only in Eq. 10-21; with C above 1.0 the
    result carries the page's recommendation to verify C by load tests or
    local experience (G2; values unchanged). `figure_10_6_alpha_clay`
    (Eq. 10-18, Figure 10-6, p. 10-17) refuses su(CIUC)/pa outside the
    drawn curve, 0.25 to 5.0 (25.3 to 506.6 kPa), read at 300 dpi; su/pa
    0.1 returned alpha 2.0 and su 10,000 kPa 0.302 (G3). The refusal
    prints the ratio to enough digits that a value just outside the curve
    does not show as one of its ends.

- **GEC-11 MSE walls (FHWA-NHI-10-024 Vol I).**
  - `table_2_1_min_reinforcement_length` (Table 2-1, p. 2-43): the three
    printed cases. Seismic loading is one row, "0.8 to 1.1"; it was two
    rows, "Seismic (low)" 0.8 and "Seismic (moderate to high)" 1.1. Each
    row gives the printed cell (`typical_min_L_over_H`) and its ends
    (`L_over_H_low`, `L_over_H_high`; the key `L_over_H` is gone). The 8 ft
    (2.5 m) minimum on every row is removed: the table does not print it;
    the docstring quotes where the text does (p. 4-11) (gec-21). The
    static row carries a `print_note`: the table prints "Static loading
    with or with traffic surcharge".
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
    4-1, 4-2, 4-5, 4-7) refuse a filter that matches no row, listing the
    rows by the library's labels, which the message says are not all
    worded as printed; they returned an empty list. A filter is matched as one
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
  - `table_8_rock_anchor_transfer_load` (Table 8, p. 74): transfer loads
    unchanged. It returned a factor of safety of 3.0 on every row, soft
    shales included; p. 74 gives 3.0 "in competent rock" and 2.0 for weak
    rocks such as clay shales, "intermediate geomaterials" of unconfined
    compressive strength 0.5 to 5.0 MPa, and the table assigns neither to
    a row. Each row now returns both in `factor_of_safety_options`, each
    with its condition and allowable load per metre, the page's sentences
    in `print_note` and the printed row name (`factor_of_safety`,
    `allowable_load_per_m_kN` and `notes` are gone). Soft shales: 50 kN/m
    at 3.0 or 75 kN/m at 2.0 (lead).
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

- **FHWA-NHI-05-037 Geotechnical Aspects of Pavements (`fhwa_pavements`).**
  - `cbr_from_dcp`, `resilient_modulus_from_dcp` (Table 5-34, p. 5-53): the
    parameter is `dcp_mm_per_blow` (was `dcp_index`, in./blow as Table 5-34
    prints). Read in inches, 0.5 in./blow gave CBR 634.7 and Mr 158,867
    psi; TM 3-34.48-2 (2016) Figure G-11 and WES GL-92-3 (1992) p. 17 give
    the relation in mm per blow, and TM 3-34.48-2 Table G-1 prints CBR 22
    at 10 mm/blow. `resilient_modulus_from_dcp` works Mr from the
    unrounded CBR (10 mm/blow: 18,553.9 psi; it used CBR 22.2, 18,580.5).
    A CBR over 100 % (DCP under 2.6 mm/blow) is refused;
    every result carries a `print_note` naming the sources (gec-08, lead's
    ruling 8).
  - `cbr_from_plasticity_gradation` (Table 5-34): `p200` is the fraction
    passing the No. 200 sieve as a decimal (0 to 1), wPI = P200 x PI being
    taken with P200 as a decimal fraction; a value above 1 is refused with
    the decimal to give. It took the percent: 0.35 was read as 0.35 % (CBR
    73.1 at PI 10; now 21.1)
    (lead's ruling 9). Table 5-34's lookup keeps the printed comments and
    adds a `library_note` for the DCP and P200 rows.
  - `modulus_subgrade_reaction_from_cbr` is removed: FHWA-NHI-05-037 does
    not print k = 1500 CBR / 19.4. AASHTO 1993 prints k = MR/19.4 (p.
    II-44); `aashto_1993.equations.modulus_subgrade_reaction_simple` holds
    it (gec-27, lead's ruling).
  - `table_5_49_drainage_modifier_mi` (p. 5-87): values as FHWA prints; the
    result notes that AASHTO 1993 Table 2.4, which it cites, prints Poor
    and Very Poor < 1 % as 1.15-1.05 and 1.05-0.95 (FHWA: 1.05-0.80 and
    0.95-0.75) (gec-26).
  - `effective_subgrade_modulus_from_relative_damage` is Eq. 5.12 as
    printed, Mr = 3015 uf^-0.431 (it computed the exact inverse of Eq. 5.11
    and cited Eq. 5.11; 3014.8 at uf 1.0, now 3015.0).
    `resilient_modulus_from_cbr_aashto93` warns above CBR 10, not at it
    (Eq. 5.13 is printed for CBR <= 10). `backcalculated_to_design_modulus`
    cites Table 5-31's commentary (pp. 5-48 to 5-49), where the factors are
    printed. The module docstrings say `pdf_page` is a 0-based page index
    (gec-48).
  - `resilient_modulus_from_r_value` cites Table 5-34 only (Mr = 1155 +
    555R, unchanged): its docstring called Eq. 5.15, Mr = 1000 + 555R (p.
    5-49), equivalent, and the chapter text said the function implements
    Eq. 5.15. `granular_resilient_modulus_bulk_stress` names Table 5-30
    (p. 5-46) for typical k1, k2 (it named Table 5-39, which is for Eq.
    5.17).

**DM 7.2 chapter text: equations as printed (build of 2026-11-10, app
BACKLOG REF-79).** The equations the review found stored in a form the
print does not have were read again from the rendered pages and point-fixed
in `dm7_2/text/` (body, key points and equation entries); no lookup
changes. Those that change a computed value: Eq. 2-10 (rho = q gamma_w /
delta p, it was divided by gamma_w), 3-2, 4-25 (qmax = 2R/(3 x0); the text
gave 2.25 times it), the six Table 4-7 cofferdam checks (sliding lost +PP,
rotation had the signs swapped, the interlock pressure and the sheeting
slippage were other formulas), 5-21 (- ic), 5-34 (lambda = fourth root of
ks B/(4 Ec I)), 5-39, 6-53, 6-60, 6-64 and 6-79 (tcap = Pui/12 + 30, it was
Pui/30 + 12). Eq. 5-5 to 5-7 keep the printed absolute values; P-2, 2-5,
2-6, 3-1, 3-7, 4-5, 4-12, 4-16 and 6-63 are in their printed forms. Filed
where printed: Eq. 4-20 to 4-22 (new section 4-4.4.3.2 Low Hydraulic
Conductivity Soils; three empty "force-injected" entries under 4-5.1.1
removed), 5-34 and its paragraphs (5-4.2.1), 6-38/6-39 with the
block-failure text (6-5.5), 7-6 (7-4.1.1) and 7-16 (7-4.4, the empty
7-4.5.2 entry removed); 7-4.1.1, 7-4.4 and 5-3.3.3 bodies completed from
the page. The Table 4-7 entries are named by the printed rows ("Table 4-7,
Sliding at Base" and so on), replacing ten unprinted ids. Key points:
Table 5-22 has eleven soil rows (not seven), Figure 4-54 note 3 (moments
80 % of simple span, not a pressure reduction), 2^n point-estimate cases.
Seven `implemented_in` links now name the equation's own function. Tests:
`tests/test_dm7_2_text_equations.py`.

Also in this build:
- Eq. 5-7 `corner_bearing_pressure` uses |eB| and |eL| as printed, so q1
  is the maximum corner pressure whatever signs are passed. It now returns
  a dict (`q1` to `q4` and a `note` that the magnitudes were used) instead
  of a 4-tuple. q_gross 10, eB -0.5, eL -1.0, B 6, L 12: q1 0 -> 20 (it
  was the minimum), q4 20 -> 0.
- `dry_unit_weight_from_saturation`: the docstring's first formula is the
  printed Eq. 3-2, gamma_w S / (w/100 + S/Gs); the computation is unchanged.
- Chapter text: the 5-3.6.2 applicability gives the printed H/B limits
  (strong layer below 0.7B, weak layer below 3B, no effect); the 5-6.2.2
  floor-slab key point keeps its printed condition (where heave of the slab
  is not a critical concern); 7-4.2.4 keeps the printed "beta = 4.26 (Pu =
  0.0001)" and adds a note, marked as not printed, that a standard normal
  distribution gives beta 3.72 at 1e-4 and 4.26 at about 1e-5. Eq. 6-79
  stays uncoded (`implemented_in` null).

**Build: UFC 3-250-01 Figure 10-1 retraced from the chart (pave-22).**
`ufc_pavement.figure_10_1_k_on_base` read the effective k on top of the
base up to 29 % low at mid thicknesses and, for the 25 to 75 pci curves
under bases thinner than about 10 in., up to 39 % high (the unsafe side):
its curves were read by eye at 10 in. steps and joined by straight lines
across their S-shaped start. Each curve is now traced from the chart
image (PDF 52, printed 32) column by column, calibrated on the chart's own
gridlines, which fit one thickness scale within 0.07 in. and one log k
scale within 0.7 %, and stored every 0.5 to 2 in.; stated tolerance 1 % of
k on a curve (2 % for the 200 curve past 55 in. and the 300 curve past
57 in., where they run together with the 150 curve and the 500 pci
frame). Between curves, log k on base is interpolated in log k on
subgrade (the library's rule; it was linear). Before and after, psi/in:
k 25 under 4 in. 41.0 -> 29.5; 100 under 10 in. 160.0 -> 194.4; 200
under 10 in. 255.0 -> 299.7 (the curve passes through the 300 gridline
there); 100 under 28 in. 246.0 -> 346.3; 300 under 10 in. 350.0 -> 357.7
(the review's note had misread this one as 385).
The limits are unchanged and were re-read from the trace: below the
25 pci curve refused, above 300 pci and past 60 in. held with a note.
Results also carry the chart's note and how the value was interpolated.
Nothing in the library or the app calls the function.

**Build of 2026-11-10: design and worked-example appendices built from
the print (app backlog REF-85).** The helper could not search or quote
these appendices: they were held as a condensed paraphrase or not at all.
Each is now stored in the print's own wording with a `[p. A-5]` marker
where each printed page starts; every equation, calculation line and table
is typed in from a rendered page, and figures are listed by printed
number. Where the print disagrees with itself the text keeps the print and
says so "(as printed; ...)". A printed section over the tools' size limit
is stored as the section and lettered parts (`A.2.a`; the letters are not
printed).

- **GEC-10 (FHWA-NHI-18-024)**: Appendix A, the design example (chapter
  19, pp. A-1 to A-29), replaces the three-section paraphrase: sections A,
  A.1, A.2 with parts A.2.a to A.2.g, A.3; Eqs. A-1 and A-2, Tables A-1 to
  A-10 and the calculation lines of Steps 10 to 13. New: Appendix B,
  challenging geomaterials (chapter 20, Tables B-1 and B-2); Appendix C,
  axial load-deformation response (chapter 21: Vesic 1977, the t-z method,
  Kulhawy and Carter 1992, Mayne and Harris 1993; Eqs. C-1 to C-42, Table
  C-1); Appendix G, alternative lateral models (chapter 25: Carter and
  Kulhawy, Zhang et al.; Eqs. G-1 to G-20); Appendix H, post-grouted
  shafts (chapter 26). Appendices D to F (guide specification, inspection
  checklist, forms) are not built; chapters 22 to 24 are left for them and
  the manifest says so. Print conflicts kept and noted include the example's
  RSN lines of pp. A-10 and A-11 (932 and 967 lb/ft² against fSN 936 and
  976 psf),
  Table A-7's axial 1,836,420 against 2,673.42 kips in the text, and p. C-10's
  example (a 2-ft socket, 870 psi, 1,751 kips) against Figure C-6 (a 6-ft
  socket, 2,500 psi).
- **GEC-10, more slips noted (values unchanged)**: Table A-5's cohesionless
  total (p. A-13) leaves out Layer 1, so the Extreme Event I summation of
  9,932 kips is about 525 kips under its rows; 0.41 x 2,266 = 929 (p.
  A-10, printed 936) and 0.47 x 2,057 = 967 (p. A-11, printed 976); 26 ft
  below the scoured ground where 60 - 38 = 22 (p. A-16); 30 percent of the
  transverse demands in the text and one third in the resultants (pp. A-17
  and A-18); 365.76 printed 365.7 (p. A-23). Figure C-4(b) (p. C-5) is a
  copy of Figure C-3(b), the side curves for cohesionless soil: the
  appendix note, the figure line and the catalog row's `read_notes` say so.
  Eq. C-2's variables gain A and E (p. C-1); Eq. C-17's lose L.
- **GEC-7 (FHWA-NHI-14-007)**, new: Appendix B, charts for preliminary
  design (chapter 12, section B, pp. 295 to 300: the charts' assumptions,
  the ten steps and Equations B.1 to B.8, the corrections for drill hole
  diameter, cohesion and factor of safety); Appendix C, the design example
  (chapter 13, sections C and C.1 to C.8.b as the print numbers its steps,
  "4.a/b/c/d" stored as C.4.a; Tables C.1 to C.5 and every calculation line
  of the LRFD checks). Appendices D to G (example plans, two
  specifications, similar technologies) are not built. Kept as printed and noted: φOS = 1/1.51 ~
  0.60 (p. 308; 0.66, Table C.2 gives 0.65); the initial-facing punching
  CDR 1.58 (p. 315; 1.60); the headed-stud CDR 1.42 (p. 317; 1.41) and its
  RFS for RFH (p. 316); and DDEF = 0.8 H = 20 ft for sandy soil (p. 317),
  where Table 5.12 (p. 141) gives C = 1.25 for sandy soil and 0.8 for
  weathered rock and stiff soil; Table C.3's head thickness tSH = 0.31 in.
  for the ½ x 4⅛ stud, where Table A.7 gives 0.28 (hc = 4.8 in. either way).
- **GEC-7**, new: Appendix A, Reinforcement Characteristics (chapter 11,
  pp. 285 to 293): the manufacturer's-availability note and the property
  tables of solid-threaded bars (Tables A.1a to A.1c, Grades 60, 75 and
  150), CTS/Titan, MAI and GEO-Drill hollow bars (Tables A.2 to A.4),
  welded-wire mesh (A.5), reinforcing bars (A.6) and headed studs (A.7,
  with Figure A.1), every cell typed in from 300 dpi renders with the units,
  sources and notes as printed. The appendix prints no section numbers:
  sections A.1 to A.7 are named for the tables they hold. Kept as printed
  and noted: Table A.1c's ultimate loads 57 and 400 kips where the area
  times 150 ksi gives 55.5 and 387 (p. 287); Table A.2's yield loads, which
  divided by the areas run from 76.6 to 91.4 ksi against its note's 87 ksi
  (p. 288); Table A.3's R51L outer diameter 1.50 in., where the other rows
  give the designation's number in mm (51 mm, 2.0 in.; p. 289); Table A.7's
  three ⅞ in. rows, whose ratio columns (2.5, 0.73) agree with a shaft
  diameter of 0.88 in., not the printed 0.86 (p. 293). No gec_7 lookup
  holds any of these values.
- **Micropile manual (FHWA-NHI-05-039)**, new: Appendix D, Sample Problem
  No. 1, bridge abutment support (chapter 14, sections D and D.1 to D.10
  as the print numbers its steps: abutment loads with Table S1-1, pile
  loads, structural capacity of the cased and uncased lengths, bond length,
  settlement, the pile top connection, test loads); Appendix E, Sample
  Problem No. 2, a laterally loaded micropile (chapter 15, section E:
  combined stress checks and the moment limit at a casing joint). The
  legend of Figure S1-3, which carries the given loads, is stored with the
  figure. Not built: Appendices A to C (Case 2 networks for slope
  stabilization, LPILE output, guide specification; chapters 11 to 13 left
  for them), the LPILE output of pp. E-7 to E-30 and the drawings of pp.
  D-23 and D-24. Kept as printed and noted: Table 5-4 cited for the loads
  of Table S1-1, Fx = 15.0 + 65.3 and M with 39.3 where Table S1-1 gives
  14.91 kN and 39.13 kN-m (p. D-9); the moment of PEQ, 52.54, where Table
  S1-1 lists 50.12 for PEQ-H (p. D-8); EA 1,252,000 and 1,133,000 kN for
  1,252,640 and 1,133,600 (pp. D-15, D-16); 286 mm for 286.6 (p. D-18);
  603 kN for 602 (p. D-21); the cone's nominal strength line carrying φ
  (p. D-18); Acasing, Icasing, Pc-allowable and Mmax(joint) of pp. E-1 and
  E-4 (0.00863 for 0.008624 m², 2,479 for 2,479.6 kN, 19.2 for 19.1 kN-m).
- **GEC-6 (FHWA-SA-02-054)**, new: Appendix B, the five design examples
  (chapter 12, pp. B-1 to B-90: an interior pier and a stub abutment on
  natural soil, a stub abutment on structural fill, a full-height abutment
  and an interior pier on rock), stored as B (introduction), B.n for each
  example and B.n.5 to B.n.12 for its printed Steps 5 to 12 (Step 11a as
  B.n.11.a; Example 4's footing-sizing Steps 10 and 11 for its three load
  cases as B.4.10.a to B.4.11.c); Tables B1-1 to B5-1 and every
  calculation line typed in from 200 dpi renders; the EMBANK output of
  Figure B3-4 typed into its figure line. Chapter 11 is left for Appendix A
  (structural fill specifications), not built. Kept as printed and noted: MY with (L + I) but L
  alone in its numbers (p. B-6); Eqns. 5-10 and 5-11 cited for the ground
  water factors, printed as Eqns. 5-9 and 5-10 (p. B-9), and Section 5.2
  cited for settlement (5.3; p. B-7); 8070 k and 4729 k for kN (pp. B-14, B-15,
  B-88); results a little off their own terms (164.1, 280.7, 0.0160 m, 338 kN,
  1787 and 2645 kN-m, 1013 kN, 293.54 and 179.4 kN/m); (425.52)(2.28) for
  a division (p. B-33); Figure B3-4 cited five times for the allowable
  pressures of B3-5; ey = 0.53 m < 0.45 m "(No Good)" (p. B-55); 288 Pa
  for kPa (p. B-80); Table B3-2 for B4-1 (p. B-81); (1/4)(4.3) = 1.01 for
  1.075 (p. B-88); the rock settlement with Bf = 1 m for a 1.8-m footing
  (p. B-89); shale ν = 0.14 where Table 5-13 gives a mean of 0.09 (p.
  B-70) and granite 52 x 10⁶ kPa where Table 5-14 gives 52.67 (p. B-89).
  The coded Table 5-1, 5-7, 5-12, 5-13, 5-14 and 5-15 lookups give the
  values the examples read; Figure 5-19 within 2 and Figure 4-1 within 3.5
  of the examples' readings.
- **GEC-6**, new: Appendix C, Load and Resistance Factor Design (chapter
  13, pp. C-1 to C-48): Sections C.1 to C.6 (LRFD against Service Load
  Design, limit states, load combinations and factors, live load
  surcharge, bearing, resistance factors, eccentricity, sliding, the design
  steps), Eqns. C-1 to C-5 and Tables C-1 to C-6; Examples B-1 and B-3
  re-worked by LRFD as LRFD Example C1 (C-1, the appendix's own name for
  it, Steps C-1.5 to C-1.14) and LRFD Example 2 (C-2, Steps C-2.5 to
  C-2.14, Step 12a as C-2.12.a), with Tables
  C1-1, C1-2, C2-1, C2-2 and every calculation line typed in from 200 dpi
  renders. The first of the two printed C.4.1 (active lateral earth
  pressures, printed under C.3 before C.4) is stored as C.3.2 and says so;
  the print has no C.4.4. Kept as printed and noted: Table C-6 citing
  Section 5.4 for global stability (5.5) and Sections 6.4.3 and 6.4.4 for
  bearing, eccentricity and sliding (no 6.4.4); Table C1-1's first row
  labelled DW where the equations use DC (p. C-15); Dw defined as "(Df)"
  and CWq taking 6.8 m where CWγ takes 9.1 m, both over 1.0 (p. C-21,
  C-22); ez with "k" for kN (pp. C-26 to C-30); ey = 980 ÷ 10923 = 0.089
  for 0.0897 (p. C-27); Vmin = 224 kN where Step 5 gives 150 kN (p. C-29);
  γP for DW minimum 0 where Table C-3 gives 0.65 (p. C-35); Pv in kN·m/m
  for kN/m (pp. C-40 to C-44); 518.3 ÷ 2.12 = 246.8 for 244.5 kPa (p.
  C-41); γPmin labels on the maximum factors 1.25 and 1.35 (pp. C-43,
  C-46). No lookup is coded for Appendix C's tables.
- **GEC-6, more slips noted (values unchanged)**, found by the
  independent check of the build: Examples 4 and 5 read Table 5-12 (p. 97)
  in different columns, Cd = 1.83 being the Average value for L/B = 5 (p.
  B-70) and 1.78 the Center value for L/B = 3, whose Average is 1.52 (p.
  B-89); "Habut = (0.5)(5.24 m) = 2.62 m" for the footing width (pp. B-31,
  B-53); 6.57 m, the B with which p. B-28 enters Figure 5-20, in a line
  written with Bf (p. B-29); Table B1-3, nine of whose twelve settlements
  are 1 mm above what Table B1-2's ratios give (p. B-12); Figure 5-7f, the
  chart entered with the distance from the slope, cited for the readings
  Example 2 takes from Figure 5-7c (p. B-43); 240 kPa for a 3.5-m footing,
  about the 3-m value, where Figure B3-5 and Table B3-4 give about 219 (p.
  B-52); "less than 35 mm" where the tolerable settlement is 38 mm (p.
  B-61); Step 11c's sliding force without PLS = 24.0 kN, with which FS is
  3.3, not 3.7 (p. B-81); in Appendix C, heq = 0.7 m for 5.24 m where
  Table C-4 interpolates to 0.68 (p. C-34), and Step 12b's eccentricity
  check without the live load surcharge, with which ey = 0.87 m, more than
  Bf/4 = 0.8 m (p. C-45; its sliding check, p. C-48, leaves LS out too).
  Figures B4-6 and B4-7 are listed under Steps 11a and 11b, whose pages
  (B-76, B-79) print them.
- **Micropile manual, Appendix D**: the pile-group sketch that p. D-9
  draws beside the centroid table without a figure number is described in
  Step 2's text (D.2), as p. D-17's cone sketch already was.
- **GEC-7, Appendix C, one more slip noted**: p. 317 cites Figure 5.15
  (p. 138, the bending mechanism in the initial facing) for DDEF, which
  Figure 5.16 (p. 142) draws and p. 141 names.

Tests: `tests/test_gec10_appendices_printed.py` (119),
`tests/test_gec7_appendices_printed.py` (63),
`tests/test_gec7_appendix_a_printed.py` (89),
`tests/test_micropile_appendices_printed.py` (74),
`tests/test_gec6_appendices_printed.py` (131).

**DM 7.2 chapter text: key points, footnotes and table notes as printed
(build of 2026-11-11/12, app BACKLOG REF-79).** Every summary,
applicability and key point of the prologue (Chapter 1) and Chapters 2 to 7
was read against the printed sentences of its section; those that said
"must" or "required" where the print says "should" or "may", dropped a
printed condition, widened a limit, or stated something the print does not
were brought to the print (chapter 6: 139 of 770 fields; chapter 7: 42 of
283; earlier chapters in their own commits). Statements that changed a design
reading include: consolidation settlement under permanent loads "only" (the
print adds a reasonable fraction of transient live load, 6-5.8); the Table
6-26 group efficiency reductions (stored as applying mainly to CFAs and
micropiles; the print reduces drilled shafts in coarse-grained soil, CFAs,
and driven piles, DDPs and micropiles in soft clay, 6-5.5); the 0.1 to 0.9
resistance factors are the generic values of the Figure 7-23 example, not a
range for pile design (7-4.5.3); the COV of very small samples "must" be
taken from Table 7-4 (7-4.1.1). Section bodies that stopped at a page foot
now carry the printed rest: 2-4.2.2 (p. 72, water levels should be
monitored; the wall type must suit the groundwater), 3-4.5.4 (p. 142,
flooding trench backfill is not recommended), 3-5.6 (p. 155), 4-7.7 (p. 252,
soil nail wall design), 6-4.5 (p. 399), 6-5.3.1 (p. 409, the API unit
resistance limits); 6-5.4.2 (pp. 416-417) has the printed Tomlinson
paragraphs it had condensed, and 6-7.2 two printed sentences on Davisson's C
and depth to fixity. Notes beside two print slips: p. 476 cites "Equation
5-81" for Eq. 6-79; p. 538 prints "N(1,0)" for the standard normal. The 45
numbered footnotes are in the bodies at their marks as "[Footnote n: ...]"
(prologue 6, chapters 2-7: 6, 5, 10, 2, 11, 5; seven had been stored as a
loose "Note:" paragraph or run into the text), and 82 table notes the
library did not hold are stored after the paragraph that cites their table
as "[Table 6-26 note A: ...]" (chapter 2: 10, 3: 7, 5: 4, 6: 58, 7: 3);
the notes that carry formulas (Tables 2-4, 3-11, 3-12, 5-8, 6-10, 6-19,
6-20, 6-31, 6-46) were typed from the rendered page. Footnote 23 keeps the
printed "LFRD" with a note. No section ids changed. Tests:
`tests/test_dm7_2_footnotes.py`.

**DM 7.2 Appendix B: all seven verification examples from the print (app
BACKLOG REF-85).** `dm7_2/text/appendix_b.json` held Example 3 alone; it
now holds the appendix introduction (new section `B`, p. 596) and Examples
1, 2, 4, 5, 6 and 7 (pp. 596-659: cantilever and anchored cut walls, mat
settlement, pile group capacity and settlement, pile group lateral load,
retaining wall reliability), 60 sections in the print's wording with page
marks and the labels of each figure. Every formula line (112) and every cell
of Tables B-1 to B-42 was typed from the rendered page, not the PDF text
layer, whose formula lines read as valid but wrong formulas. Print slips are
kept as printed with a note beside them, among them: p. 599 "2,240B - 4560"
for -7,840; Table B-4 with the overturning and sliding outcomes swapped;
p. 611 "11,400 lb/ft" (1.2 x 9,568 is 11,500); p. 636 "1500 + 470 = 1976";
the Example 5 block expression lettering L and Z the other way round from
Eq. 6-38; p. 650 "259 kips" in a line whose 26 ft-kip needs 265; Example 7's
derivative of the sliding limit state with respect to the backfill unit
weight, which leaves out the unit weight in the active force (the full
derivative gives beta about 1.76 against the printed 1.64); Table B-39's
"0.390" for 0.039; Table B-41's Point Estimate beta 1.45 where the text
gives 1.48. The chapter title is "Appendix B: Verification Examples". Tests:
`tests/test_dm7_2_appendix_b.py` recomputes the printed numbers from the
printed equations and stored cells, runs the dm7_2 functions on the
examples' inputs (all agree except Table B-5 layer 2, where Eq. 4-12 gives
KP,h 2.47 against the printed 2.4), and scans every dm7_2 chapter file for
the scatter the text layer leaves in formulas (isolated primes, empty or
unbalanced brackets, runs of single letters or digits, repeated table rows).

**Structural references' chapter text rewritten from the print (REF-83,
2026-11-10 to 2026-11-12).** The stored text of UFC 3-301-01, EM
1110-2-2104, EM 1110-2-2107, UFC 4-023-03 and the Wood Handbook
(chapters 8 and 9; chapters 4 and 5 named items only) was partly
paraphrase. UFC 3-301-01, EM 1110-2-2104 and UFC 4-023-03 bodies are now
the print's own wording with [p. N] markers; every equation, formula
line and typed table was read from the rendered page; key points restate
printed sentences; code-module notes are out of the text. No Python
changed.

Statements that could have led to a less safe design:

- UFC 3-301-01 3-6: collector elements in SDC C-F were said to use load
  combinations without the overstrength factor; the print replaces only
  Item (c) of ASCE 7 12.10.2.1 and its exception (p. 58).
- UFC 3-301-01 3-7: the masonry-anchor option multiplies QE by Omega-op,
  not Omega-o (p. 61).
- UFC 3-301-01 7-2: four irregularities are prohibited (horizontal 1b,
  vertical 1b, 5a and 5b), not "two of four" (p. 100); walls retaining
  earth keep "plus the difference in earth pressures"; 7-3's elevator
  rail load is the car plus 40 percent of its rated load.
- EM 1110-2-2107 4.1: the alpha = 0.90 list is printed (normally
  submerged HSS that are hard to inspect; brackish water or seawater);
  the text said no list was printed.
- Wood Handbook 8: the nail dowel bearing equation (Eq. 8-3) was said
  to serve all dowel fasteners; bolts and lag screws use Eq. 8-17/8-18
  (p. 8-19), which perpendicular to grain give lower bearing strengths
  for bolts of 1/2 in. and larger.

Other corrections: UFC 3-301-01 2-4.6 vertical lift fabric doors (the
700-year ban is for aircraft maintenance hangars), the healthcare
chapters' scope ("having emergency surgery or emergency treatment
facilities"), 4-4's high-wind trigger conditions, an unprinted wind
turbine and Section 2109 item removed; EM 1110-2-2104 Eq 3-2's
principal load factor is gamma_pr (the text said gamma_pu), 2-2 cites
paragraph 3-4 (not 3-5), the No. 4 bars at 12 in. are "generally, for
ease of placement", Eq 3-1's L_ni; Wood Handbook Eq. 9-41 and 9-24 as
printed with notes, and the worked examples of pp. 9-10 and 9-12 in the
print's words; UFC 4-023-03 2-2.4.3 and 3-2.5 as printed.

Typed in from the rendered pages: UFC 3-301-01 Tables 2-1, 2-2, 4-1(a),
4-1(b), 6-1, 7-1 (Tables 3-1 and 4-2 are not, and the bodies say so);
EM 1110-2-2104 Eqs 3-1 to 5-4 and Tables 2-1 to 3-4; EM 1110-2-2107
Table 4.1; UFC 4-023-03 Tables 2-1, 2-2, 3-2 to 3-5. Print slips are
stored as printed with a "Print note". Section ids added: ufc_structural
2-7.2, em_2104 3-2.f (3-2's load definitions; 3-2 printed is over
14,000 characters), em_2107 4.2.3 and 6.1.3. New tests:
`test_ufc_structural_text_equations.py`, `test_em_2104_text_equations.py`,
`test_em_2107_text_equations.py`, `test_ufc_collapse_text_equations.py`,
`test_wood_handbook_text_equations.py`, and
`test_text_scatter_patterns.py` (loose primes, a lone digit before a
formula, unpaired brackets, a sentence repeated in consecutive rows).

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
