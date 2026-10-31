# REF-04: rescue branch checked against the print

Branch `rescue/reference-wip-2026-06-02` (7fb6fe8, base 829b897) merged onto
main (ceeef53) on `wip/ref04`, then every new chapter checked page by page
against the PDFs in `docs/` (2026-10-30). Fixes were made from the printed
page, never from memory: equations were rendered from the PDF and read symbol
by symbol; table values, figure and table numbers, captions and page numbers
were read off the page. Counts below are wrong or unprinted statements found
and fixed (approximate where one sentence held several errors). After that
check (9948a59), GEC-7 ch 1-5 and the GEC-12 ch 7 top-level sections were
rebuilt from the print (see "Rebuilt from the print").

## What the merge kept and dropped

- **Kept:** GEC-7 ch 6-10 and GEC-12 Vol II ch 9-18 (new chapter files), after
  the check below; merged section summaries in GEC-6, GEC-7 ch 5 and GEC-12
  Vol I ch 1-8, after their own check.
- **Dropped:** the branch's GEC-13 ch 3-10 files and summaries (main rebuilt
  those chapters from the print on 2026-10-19, REF-25) and
  `scripts/add_gec13_summaries.py`; its edits to GEC-13 ch 11 (main
  removed that file in REF-25; it stays removed); its GEC-12 2.10.1-2.10.3
  summaries (main's chapter 2 has no such sections); its GEC-7 ch 1-4
  summaries (see below); its CLAUDE.md (main's kept).

## New chapters

Printed page numbers; GEC-7 printed = PDF - 40, GEC-12 Vol II printed = PDF - 32.

| Chapter | Pages read | Errors fixed | Examples |
|---|---|---|---|
| GEC-7 ch 6 Design of Soil Nail Walls | 143-204, all | ~80 | Eq 6.35 (seismic displacement) was a different formula; print: log(de) = -1.51 - 0.74 log(ky/kmax) + 3.27 log(1 - ky/kmax) - 0.80 kmax + 1.59 PGV. Eqs 6.31/6.33 wrong symbols. Facing CDRs (Eqs 6.18, 6.19, 6.27) used Tmax; print uses To. Table 6.3 phi_FH 0.75 vs printed 0.70/0.80 static, 0.65/0.75 seismic. Strut nails "3-5 degrees"; print 15-20 to 45 degrees from vertical. Six figure captions or pages wrong. |
| GEC-7 ch 7 Corrosion Protection | 205-223, all | ~35 | Protection decision tree inverted. Eq 7.1 given as "X = f(tf)"; print X (um) = 80 tf^0.8. Grout cover 25 mm vs 1 in.; grout pH 12.5 vs >13; stray current 30-60 m vs 100-200 ft. |
| GEC-7 ch 8 Contracting Approaches and Specifications | 225-230, all | ~12 | Contractor experience "5 projects in 5 years" and other list items not in the print. |
| GEC-7 ch 9 Construction Inspection and Performance Monitoring | 231-263, all | ~30 | Eqs 9.5-9.7 missing the printed x 0.75; verification-test unbonded length "1 ft beyond the failure surface" vs printed 3 ft; Figs 9.1-9.8 and Tables 9.1-9.2 added with pages. |
| GEC-7 ch 10 Hollow Bar Soil Nails | 265-271, all | ~10 | 200 ft spacing presented as a soil nail figure (print: MSE figure after Elias); Table 10.1 rows missing. |
| GEC-12 ch 9 Static Load Testing | 1-49, all | ~20 | Quick test "2.5-min holds to 200% design load" vs printed 5% increments, 4-15 min holds; Table 9-2 is the ASTM D3966 lateral schedule, not axial; Eqs 9-7 to 9-12 added. |
| GEC-12 ch 10 Dynamic Testing and Signal Matching Analysis | 53-121, all | ~25 | Driving stress limits (not in this chapter) removed; "<10 bpf underpredicts" vs printed <24 bpf overpredict, >120 bpf underpredict; Eq 10-4 in printed form; Section 10.9 case history added. |
| GEC-12 ch 11 Rapid Load Testing | 123-151, all | ~20 | Eq 11-1 inverted (file L/(c tL); print c tL/L); Statnamic "to 30,000 kips" vs printed under 9,000 kips; Eqs 11-2, 11-3, 11-8 to 11-10 and Sections 11.5-11.6 added. |
| GEC-12 ch 12 Wave Equation Analysis | 153-257, all | ~12 | Hard rock seating "5 blows/0.5 in." vs printed 5 blows per 1/4 in.; plug limitation reversed; generic unprinted text in 12.7-12.9 replaced. |
| GEC-12 ch 13 Dynamic Formulas | 261-278, all | ~14 | Eqs 13-2 to 13-6 each wrong (e.g. 13-6 Feff Ed / ln(10 Nb) vs printed 6.6 Feff Ed ln(10 Nb); 13-5 missing the 12); Eqs 13-7, 13-8 added; Engineering News actual FS range corrected to the printed database 0.6-13.1. |
| GEC-12 ch 14 Contract Documents | 281-330, all | ~16 | Prestressed pile driving stress limits wrong (0.85 f'c vs printed 0.85 f'c - fpe; severe-environment tension phi_da fpe, not 0.0 ksi); hammer approval criteria not printed; test pile heave 0.5 in. vs printed 1/4 in.; Eqs 14-3 to 14-6 and Tables 14-2 to 14-5 added. |
| GEC-12 ch 15 Pile Driving Equipment | 333-393, all | ~12 | Chapter 14 specification limits attributed to ch 15; pile cushion "replace after ~1,500 blows" vs printed 1000-2000 blows total; Eqs 15-1 to 15-3 added. |
| GEC-12 ch 16 Pile Accessories | 395-431, all | ~8 | "All prestressed concrete piles are prestressed" (print: virtually all concrete piles are prestressed); 70 F preheat stated unconditionally (print: below 32 F ambient only). |
| GEC-12 ch 17 Driving Criteria | 433-445, all | ~6 | Driving-formula reduction "~47%" (see print inconsistencies); hard rock "20 blows/inch equivalent" not printed. |
| GEC-12 ch 18 Construction Monitoring of Pile Installation | 447-507, all | ~10 | Eq 18-1 had no formula (print h = 4.01 (60/bpm)^2 - 0.3) and a non-schema key; checklist items 9-13 were a placeholder; Table 18-5 added. |

Chapter titles in `scripts/manifests/gec_12_v2.json` now follow the printed
headings (ch 10, 14, 16, 18).

Figure records (found by the independent spot-check of 9948a59): 11 GEC-12
figure records carried the description of the table with the same number,
Figures 12-3 to 12-7, 13-1, 18-1 and 18-3 to 18-6 (e.g. Figure 18-3, a
photograph of Blue Nylon hammer cushion disks, held Table 18-3's diesel
hammer problems). The check scripts' helper applied a description keyed by
number to the figure and the table alike. Each now has a description read
off its page; captions and pages were already as printed. Sweep of every
figure record in the chapters this work touched (GEC-12 ch 7 and 9-18,
GEC-7 ch 1-10): no other figure shares a table's description; the four
with more than half their words in some table's description (GEC-7 Figures
5.7, 6.5, 7.2, 9.6) describe their own figures.

## Merged summaries (main's sections that had none)

- **GEC-6 ch 1-10 (127 summaries):** every number and capitalised name
  matched by script against the chapter's printed pages; the numbers were
  checked in context. No errors found; unchanged.
- **GEC-12 Vol I ch 1-8 (106 summaries):** read against the print; 38
  corrected (commit cbec1f9). The ch 7 top-level summaries restated main's
  overview bodies and were wrong: equation numbers, a phi range of
  "0.65-0.80" for dynamic methods (Table 7-2 runs 0.10 to 0.80), angular
  distortion "0.004-0.008" (Table 7-18: 0.004 multi-span, 0.005 simple-span),
  a hammer ram-weight rule and batter-pile claims the print does not make.
  6.11 had converted Fundex/Tubex tons as kips. 8.2.3 gave K up to 2.0
  (Figure 8-4: 0.65 to 2.1). 22 metric summaries now quote the printed US
  values.
- **GEC-7 ch 5 (9 summaries):** read against the print; 4 corrected (Eq 5.17
  missing the gamma_ES ES term, Rankine Ka is Eq 5.22, load factor wording).
- **GEC-7 ch 1-4 (28 summaries): dropped.** They restated main's ch 1-4
  bodies, and those bodies were not built from the print: 1.4 says 1986,
  Cumberland Gap, Tennessee (print: the 1984 FHWA demonstration in Kentucky);
  4.3 boring spacing and depth, 4.6 creep criteria and 4.7 aggressive-ground
  limits differ from the print; lift heights are metric memory values (print
  2.5-7 ft, typically 3-5 ft); several figure titles are not the printed
  ones. A summary cannot be right where its body is wrong, so the files went
  back to main's. The rebuild below then rewrote ch 1-5 from the print,
  summaries included.

## Rebuilt from the print (after 9948a59)

Main's GEC-7 ch 1-5 came from the original build (8d48ece) and its GEC-12
ch 7 top-level sections from the same kind of build (84dbf77); neither was
written from the page. Rebuilt REF-25 style: one section per printed heading
to x.y.z (lettered sub-headings folded into their parent), bodies, key points
and summaries paraphrased from the page in the print's US units, equations
rendered from the PDF, tables and figures with printed pages.

| Part | Pages | Commit | Sections | What main had wrong (examples) |
|---|---|---|---|---|
| GEC-7 ch 1 Introduction | 1-7 | 12607dd | 9 | Temporary walls in scope (print: permanent only); first use "1986 Cumberland Gap, Tennessee" (print: 1976 Portland, Oregon; the 1984 FHWA demonstration near Cumberland Gap, Kentucky). |
| GEC-7 ch 2 Applications and Feasibility Evaluations | 9-32 | ea06a4c | 27 | Metric memory values (1-2 m lifts; print 2.5-7 ft, typically 3-5 ft); unprinted section titles. |
| GEC-7 ch 3 Construction Materials and Methods | 33-62 | 1b39f70 | 20 | "100-200 mm holes", "150-200 mm facing", tendon grades in MPa; Figure 3.8 called "drainage details" (print: a centralizer photo); a stray 3.2.7. |
| GEC-7 ch 4 Information Required for Design | 63-95 | 96df21a | 31 | Boring spacing and depth (4.3), creep criteria (4.6) and aggressive-ground limits (4.7) differ from the print. |
| GEC-7 ch 5 Resisting Mechanisms and Limit States | 97-142 | 7de8a5d | 36 | Bodies not from the page; Eqs 5.1-5.31 now read off the rendered pages. |
| GEC-12 ch 7 top-level 7.1-7.10 | 211-398 | f71bb95 | 10 | Setup "2-5x", group settlement "1.5-3x", angular distortion "0.004-0.008", "minimum 10 ft into the bearing stratum", phi "0.25-0.50" and "0.65-0.80", Rndr "< Rn with setup", "flange width" for H-pile impedance; none printed in ch 7. Wrong objects: 7.1 held misnumbered Eq 7-1 to 7-5, Figures 7-1 to 7-3, Tables 7-1/7-2; 7.5, 7.6 and 7.7 cited Figures 7-66 to 7-71, which are p-y and wedge figures in 7.3.7. 7.6 now holds Eqs 7-85/7-86 and Table 7-32 as printed (Rn = 200/0.65 = 308 kips; Rndr = 308 + 50 + 100/0.65 = 512 kips). Eq 7-87 and Figure 7-81 moved to 7.10.3, Eqs 7-88 to 7-90 to 7.10.7. |

Figure catalogs: the text-enriched figure descriptions (titles, applicability
and key points of the sections citing a figure) were refreshed for gec_7 and
gec_12 from the rebuilt text, so the old claims no longer reach figure
search. `_norm_fig_ref` in `scripts/build_figure_catalog.py` now reads the
`figure_id` key the GEC-7 and GEC-12 Vol II chapters use; before, those
citations were skipped (78 gec_7 and 328 gec_12 figures are enriched now,
against 19 and 78).

## Found but not fixed

GEC-12 ch 7 subsections (from `check_section_numbers.py gec_12`, unchecked):

- 13 printed headings with no section: 7.2.1.3, 7.2.1.4.1, 7.2.1.4.2,
  7.2.4.2.1, 7.3.1.1, 7.3.5.2.1, 7.3.5.2.2, 7.3.7.6.1, 7.4.2.1, 7.4.2.2,
  7.4.3.1, 7.4.3.2, 7.4.3.3.
- 7.2.1.3.4-7.2.1.3.7 held as one range; 7.3.7.3 is extra.
- Titles: 7.2.2.1 (printed "Pile Groups in Cohesionless Soils"), 7.3.6.2
  (printed "Methods for Reducing Downdrag and Drag Force"), 7.3.1 (printed
  "Tolerable Vertical Deformations and Angular Distortion"), 7.4.1 (printed
  "Extreme Event Scour During Check Flood").
- 7.3.1 lists Table 7-18 as "Tolerable movement criteria for highway bridges
  and structures"; printed "Tolerable Movement Criteria for Bridges".

## Chapters from the original build (8d48ece) or the same kind of build (unchecked)

From the file history (the commit that added each chapter file). Not checked
against the print here; "print pass" means a later REF-23/REF-25 commit
reworked part of the chapter from the print, not that it was rebuilt whole.

- **8d48ece (2026-02-23, the original build), still as built:** GEC-6
  ch 1-10 (never touched since; its 127 merged summaries were checked, the
  bodies were not); Micropile ch 1-5 (summaries added by ec96e39 "manual
  annotation, no API"; ch 3-5 print pass). GEC-7 ch 1-5 rebuilt above.
- **8d48ece, later rewritten by another bulk drop (method not checked):**
  GEC-10 ch 9, 10, 11, 17, 18 (c855ee5, 2026-06-02; ch 9-11 and 18 print
  pass since, ch 17 none); GEC-13 ch 1-2 (4220d5e, 2026-06-02; ch 2 print
  pass). GEC-13 ch 3-5 were rebuilt from the print in REF-25.
- **84dbf77 (2026-02-22, same kind):** GEC-12 Vol I ch 1, 3, 4, 5, 6 (no
  print pass), ch 2, 7, 8 (print pass; ch 7 top level rebuilt above).
- **5aa8108 (2026-04-15, "manual annotation, no API"):** Micropile ch 6-10.
- Later bulk drops whose method this check did not look at: cf7c17f (DM7.1
  ch 1-8, DM7.2), c855ee5 (GEC-10 ch 1-8, 12-16; GEC-11 ch 1-11), b0838af
  (GEC-4, 5, 8, 9, 14), 1612e6a and 1176620
  (FEMA P-2082, Caltrans trenching, FHWA pavements), c0552e7, c1fb7ce,
  4c64e25 (Eurocode 7-1, 7-2, AASHTO 1993), 6869631 and 47be106 (UFC
  pavement series), 0e65f9e, 1485139, 1d71743, 3ee90d1, 9e18826, ead7573
  (GSA, UFC structural, EM 2107, EM 2104, UFC collapse, Wood Handbook).
  1c3a9cc (FHWA Soils and Foundations, REF-29) says it was read off the
  print.

## Could not be verified

- GEC-7 ch 6 Eqs 6.6-6.17, 6.20-6.25, 6.28-6.30 and 6.40-6.43 are cited by
  number only; the file holds no formula for them to check.
- GEC-12 Vol II appendices A-C (PDF 541-573: resource lists, standards list,
  hammer table) are not in the library and were not checked.

## Print inconsistencies (kept as printed, noted in the body)

- GEC-7 Table 7.3 gives Class B for "intermediate or high" risk tolerance and
  Class C for high, against Figure 7.2.
- GEC-7 Table 9.2 says hold "until movement stabilizes"; the text says 10
  minutes.
- GEC-7 6.5.1 prints a minimum FS_OS of "120" (written 1.20); 6.11 asks for a
  monitoring plan when deformations are "non-significant".
- GEC-12 ch 17: the text calls the Gates-to-static change an "87% reduction";
  the printed factors (0.40/0.75) give 53%, i.e. 47% lower. Both stated.
- GEC-12 ch 16: Collin 2012 in the text, 2002 in the references; Figure 16-43
  caption "full groove" vs text "partial penetration"; checklist "70 degrees"
  vs 16.5.2 "50 F minimum".
- GEC-12 Table 15-2 last band printed "540 to 600" (overlaps the band above).
- GEC-12 Table 12-8 very dense maximum shaft value printed "4.o" (read 4.0).
- GEC-12 Figure 18-2 caption (process) vs text (inspector's tools).
- GEC-12 8.5.3: lambda_pf printed once as 9.25, elsewhere 9.15; the text
  cites "Eq 8-48" where Eq 8-51 is applied.
- GEC-12 3.5.5 and 5.2.5 point to Sections 6.13 and 6.14; the material is in
  6.12.
- GEC-12 6.8: Figure 6-20 prints the square solid prestressed pile as 8-24
  in. (the 6.8 summary's "square 8-24 in."); Figure 6-5 prints 10-30 in.
- GEC-12 12.5.2: "any stroke greater than 8.2 feet at a penetration
  resistance of 90 blows/foot is acceptable"; the Figure 12-5 curve is above
  9 ft at 90 blows/ft. Figure 12-6 gives the pile penetrations as 65 and 70
  ft "below excavation" (piles 50 and 52 ft long); the text has 49 ft below
  excavation (65.5 ft below river bed) and bedrock 70 ft below river bed.
  12.5.3 says Figure 12-7 includes transferred energy; that plot is in
  Figure 12-8.
- GEC-7 2.7.2: the heading wording is kept as printed.
- GEC-7 3.3.7: CIP contraction joints at 90-100 ft are called "similar to"
  shotcrete facings, given as 45-90 ft; a reference to "Section 3.5" for
  sculpted faces (the material is 3.4.1). 3.2.6 prints "ASTM 1064M".
- GEC-7 4.4.2 prints "D21974"; Table 4.8 ends with a truncated "Very dense
  soil and soft".
- GEC-7 ch 5: Eq 5.14 has a minus before Q/B'e where Eq 5.12 adds Q; Eq 5.27
  already divides by S and Eq 5.28 divides by S again; 5.8.3 prints
  "hi = di/2" (the definition makes di half of hi); 5.9.2 cites "Figure 5.20"
  (the figure is 5.16); 5.6.2 cites "Section 6.6.3 Resistance Factors for
  Overall Stability" (that heading is 5.6.5); 5.7.2 calls the pullout
  factors "overall stability"; 5.7.3 takes gamma_EH "from Table 5.3 for
  Strength I" (twice); 5.2.1 prints "RT < RP" for RPO, and gives To ranges of
  0.6-1.0 overall and 0.40-0.70 in the upper two thirds; the body headings of
  5.2 and 5.3 differ from the table of contents (TOC titles kept).
- GEC-12 7.6 cites "Equation 7-85" for the Rndr example (it is Eq 7-86) and
  a stray "Table" opens the sentence after Eq 7-86; 7.9's heading is printed
  "DETERIORATON" and its text "marine bores".

## Gates

- `python scripts/audit_chapter_text.py <ref>`: gec_6, gec_7, gec_12, gec_13
  all exit 0 (0 errors).
- `python scripts/check_section_numbers.py gec_7 gec_12 gec_6`: exit 0; the
  flags left are the earlier REF-30 ones (gec_12 3.0, 7.2.2.1, 7.3.6.2,
  7.3.7.3; gec_6 chapter "x.0" introductions and 4.3.3).
- Targeted tests (GEC-6/7/12/13 text, figures and tables, retrieval,
  section numbers, subsections, result size, cover citations, figure
  captions and ids, query expansion; 19 files): exit 0, 838 passed, 2
  xfailed, on the final tree.
- After the rebuild (f71bb95 and the catalog and notes commits): audits for
  gec_7 (10 chapters) and gec_12 (18 chapters) exit 0;
  `check_section_numbers.py gec_7 gec_12` exit 0, with gec_7 ch 1-5
  matching every printed heading and 66 printed headings in gec_7 ch 6, 7,
  9 and 10 still without a section of their own, plus four ch 9 ranges
  (9.3.4-9.3.5, 9.3.6-9.3.7, 9.4.2-9.4.3, 9.4.4-9.4.6), the rescue branch's
  structure; the same 19 test files exit 0, 838 passed, 2 xfailed.
- Test count: these 19 files collect 840 tests (838 passed + 2 xfailed) on
  this branch and at 9948a59 alike, counted per file with `pytest --co`. The
  independent spot-check reported 936 passed and 2 xfailed for its run;
  that is not what these 19 files collect at either commit here, so the two
  runs' file lists are worth comparing before quoting either number.
