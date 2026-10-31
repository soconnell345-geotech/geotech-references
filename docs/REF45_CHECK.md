# REF-45: original-build chapters checked against the print

The chapters below came from the February 2026 bulk builds (84dbf77 for
GEC-12 Vol I, 8d48ece for GEC-6 and Micropile ch 1-5, 5aa8108 for
Micropile ch 6-10) and had not been written from the page (REF04_CHECK.md,
"Chapters from the original build"). Each was read page by page against
the PDFs in `docs/` (2026-10-31), one branch per manual from main 8ed9e19.
Fixes were made from the printed page, never from memory: equations were
rendered from the PDF and read symbol by symbol; table values, figure and
table numbers, captions and page numbers were read off the page. A chapter
that was mostly right was fixed in place. A chapter whose structure was
wrong throughout (printed headings missing, objects without pages,
equations away from the section that prints them) was rebuilt REF-25
style: one section per printed heading, bodies, key points and summaries
paraphrased from the page in the print's US units, equations as captioned
strings with their variable lists, every table and figure with its printed
page.

## GEC-12 Vol I (branch `fix/ref45-gec12`)

Printed page = PDF page - 46. Chapter 7 was rebuilt in REF-04 and REF-47
and is not repeated here. Counts of errors were not tallied for the
chapters fixed in place; most of what changed there was omission (printed
headings, objects and statements the file left out) rather than wrong
statements, and the examples list the wrong ones found.

| Chapter | Pages read | Errors fixed | Examples |
|---|---|---|---|
| ch 1 Driven Pile Foundation Manual (348d235) | 1-6, all | Fixed in place | Purpose 7 of the nine (alternative contracting methods, ACM) was missing; 1.3 now as printed (first and second halves, a standalone document, the training course); 1.4 history adds Naysmith's 1839 steam hammer, vibratory hammers and the Bodine resonant driver; Abu-Hejleh 2013 added; page cites on every section. |
| ch 2 Overview of Pile Foundation Design and Construction (8fc1343) | 7-44, all | Fixed in place | 2.1 rewritten as printed; 2.2 now gives the four limit states and up to thirteen cases (five strength, two extreme event, four service, two fatigue); the Strength I equation and Table 2-3 load factors read from the page; the Figure 2-2 example numbers; 2.10 Block 16 adds the printed upper limit of 96 blows/ft (8 blows/in.) for hard driving. Objects as captioned strings with pages. |
| ch 3 Considerations in Foundation Selection (2ed2ecf) | 45-78, all | Fixed in place; 10 printed headings added | 3.2.1-3.2.3.4, 3.4.1.1, 3.6.1 and 3.6.2 had no section; 3.4.1 retitled as printed; every Figure 3-n and Table 3-n in the section that prints it; Eqs 3-1 (S_max = alpha (D + 6b)) and 3-2 and the Table 3-4 alpha values read from the page. |
| ch 4 Site Characterization (65c7afa) | 79-95, all | Fixed in place | 4.1 rewritten as printed; the 2.4 in. boring against a 12 in. pile comparison, the solid stem auger limits, split barrel sizes, Deere and Deere and the swelling clay barrel added; Tables 4-3 and 4-6 read from the page; page cites and captioned objects throughout. |
| ch 5 Geomaterial Design Parameters and Geotechnical Reports (2bb42e3) | 99-148, all | Rebuilt: 18 printed headings added, 36 sections | The file carried implementation keys the print does not have (dropped); Eqs 5-1 to 5-26, Figures 5-1 to 5-13 and Tables 5-1 to 5-16 now each sit in the section that prints them, equations read off the rendered pages. |
| ch 6 Pile Types for Further Evaluation (aeb2eb7) | 155-206, all | Rebuilt: 27 printed headings added, 41 sections | Figures 6-1 to 6-29 and Tables 6-1 to 6-17 placed with pages; ch 6 has no numbered equations, so the driving stress expressions of Tables 6-1 to 6-7 moved from `equations` into key points; pile type size and load ranges, corrosion rates and the cost tables read from the page. |
| ch 8 Structural Aspects and Limit States (b3b06ac and the follow-up) | 427-481, all | Rebuilt: 12 printed headings added, 35 sections | 8.4.2.1-8.4.2.3, 8.5.2.1-8.5.2.4, 8.6.2.1, 8.6.2.2, 8.7.1, 8.7.2 and 8.7.2.1 had no section; six titles carried unprinted suffixes ("Driving Stresses (Timber)" and the like). Equations were dict objects without pages; Eqs 8-1 to 8-99 were read off the rendered pages (the formulas matched) and are now captioned strings in the section that prints them. 8.2.3 gave the K range as 0.65 to 2.0 (Figure 8-4 design values run 0.65 to 2.1). "C_KF converts ASD to LRFD" is not printed (removed). 8.9 adds the printed rule that dv for preliminary sizing may be taken as the greater of 0.9 ds or 0.72 h. |

## Found but not fixed

- The retrieval eval's CPT question (REF-48, "CPT pile capacity effective
  cone resistance", strict xfail) now passes, so its strict xfail fails the
  test file. After the ch 5 rebuild the search reaches 7.2.1.3.6 at rank 4
  of 5 (5.1.2, 7.3.5.2.2, 7.2.1.3.7, 7.2.1.3.6); it stays at rank 4 after
  ch 6 and ch 8. The short 7.3.5.2.2 still outranks the capacity methods,
  so REF-48 is not fixed; the move comes from changed corpus statistics.
  The query and the test are left as they are for the lead to decide.

## Print inconsistencies (kept as printed, noted in the body)

GEC-12 Vol I (the 3.5.5/5.2.5, 6.8 and 8.5.3 items are also in
REF04_CHECK.md):

- 2.3: the example labels 1982 and 4307 kips as Service II.
- 3.2.3.2: a sentence ends "AASHTO (2014) design specifications Section"
  with no number.
- 3.4.1.1 prints 1700 kips, then 1722 kips at 118 ft. 3.5.5 prints "Gu at
  al."; 3.6.1 prints "summer of 2104".
- 3.5.5 cites Section 6.13 and 5.2.5 cites 6.14 for material printed in
  6.12; 6.3 cites "Section 6.14.1" for corrosion losses printed in 6.12.1.
- 4.2.3.5 prints "Deere and Deer (1989)". 5.1.1 prints "Lio and Whitman"
  (the references list Liao).
- 5.2.3.2: the Table 5-8 caption refers to "Figure 5-12" where the text
  uses Figure 5-10. 5.5.1 cites Sections 5.2.3.3 and 5.2.3.4 for SPT
  correlations printed in 5.2.3.2 and 5.2.3.4.
- 6.4.1 gives closed end pipe walls of 0.188-1 in. where Figure 6-4 prints 5/16-1
  in.; 6.6 gives Tapertube walls of 0.1875-0.625 in. where Figure 6-7
  prints 0.312-0.5 in.
- 6.8: Figure 6-20 prints the square solid prestressed pile as 8-24 in.;
  Figure 6-5 prints 10-30 in.
- 6.3 prints "low allow steels". 6.12.1.1 cites Beavers and Dunn (1998);
  the references list Beavers and Durr. Table 6-12 lists "STEEL PILING, 24"
  DIA. PIPE" twice ($224.28 and $121.27). Table 6-17 prints HP 14x117 at
  $20.00/ft.
- 8.3.3: the text gives phi_c = 0.60 for an H-pile with good driving and a
  pile tip; Table 8-6 gives 0.60 where a pile tip is not necessary and 0.50
  where it is.
- 8.4.2.1: Eq 8-25 prints E = Eo Ct; Ct is not defined (the variable list
  gives CM and Ci) and Eq 8-32 prints E = Eo CM Ci.
- 8.5.2.2: "if Equation 8-2 is not satisfied" for Eq 8-52.
- 8.5.3: lambda_pf printed as 9.25 when computed and 9.15 in the
  comparison and in Eq 8-51; the text says "Equation 8-48 will be used"
  where Eq 8-51 is applied.
- 8.6.2.2: Eq 8-68 uses phi Po while Eq 8-69 defines Pn; Est is given
  units of in^2 and epsilon_cu of in^2; the second variable list names Ep
  where Est is used; Mrx and Mry point to Section 8.5.2.3.
- 8.7.2.1 Step 2 says "Equation 8-73 or Equation 8-74" for Eqs 8-76 and
  8-77.
- 8.9: Eq 8-84 prints bo = co + dv for circular columns; the step heading
  repeats "Layout of Pile Groups"; the two-way shear text cites "Equation
  8-84" and "8-85" for Eqs 8-87 and 8-88, and the one-way text "the lesser
  of Equation 8-91 or 8-92" for Eqs 8-94 and 8-95.
- 8.9.1 cites Brown and Thompson (2014); the references list 2015.

## Gates

GEC-12, on the final tree of `fix/ref45-gec12` (and before each chapter
commit):

- `python scripts/audit_chapter_text.py gec_12`: exit 0.
- `python scripts/check_section_numbers.py gec_12`: exit 0. Chapters 1-6
  and 8 match every printed heading (3.0 Introduction is the accepted
  chapter introduction); the headings still missing are in the Vol II
  chapters (REF-04 notes).
- The app's `test_citations.py` (app master 3539090, this library on
  PYTHONPATH): exit 0, 5 passed.
- The 19 targeted test files (GEC-6/7/12/13 text, figures and tables,
  retrieval, section numbers, subsections, result size, cover citations,
  figure captions and ids, query expansion): 838 passed, 2 xfailed, 1
  failed. The one failure is the strict XPASS of the REF-48 question above;
  nothing else changed.

## GEC-6 (branch `fix/ref45-gec6`)

Printed page = PDF page - 6. Chapters 1-4 and 6-10 were fixed in place;
chapter 5 was rebuilt in printed order. As for GEC-12, most of what changed
in the chapters fixed in place was omission; the examples list the wrong
statements found. This branch also carries the GEC-12 section above
(cherry-picked from 286686d), so the GEC-6 section can be merged after
`fix/ref45-gec12`: the two files differ only by this appended section.

| Chapter | Pages read | Errors fixed | Examples |
|---|---|---|---|
| ch 1 Introduction (99ed0ee) | 1-4, all | Fixed in place | 1.2 as printed: pile support is "wise, if not essential" for scour, poor ground, vessel impact, seismicity and congested urban sites, not "only" there; substructure about 50 percent of replacement cost; 6 mm (1/4 in.); 1.3 adds the interim revisions. |
| ch 2 Case Histories of Shallow Foundations (5c6a212) | 5-22, all | Fixed in place | 2.7.2's center pier layer is a 1.5-3.0 m thick hard clayey sand to clayey gravel under the sand, not a gravel layer at 1.5-3.0 m; 2.7.3 removed loose soil only under the piers (the abutment fill went on the existing ground); the 2.5 "overlap" is not printed; objects as captioned strings with pages in the section that prints them. |
| ch 3 Shallow Foundation Feasibility (483d9dd) | 23-28, all | Fixed in place | 3.1.2: the bearing capacity and the short- and long-term settlement must be evaluated (the file had "bearing capacity for short- and long-term settlement" and a drained bearing capacity the print does not name); cohesionless soils "no long-term consolidation", IGM design "slope stability governs" and potholing "to avoid claims" are not printed. |
| ch 4 Subsurface Exploration and Testing (6045ffb) | 29-46, all | Fixed in place | Eqs 4-4 and 4-5 were missing; Eqs 4-1 to 4-21 read from the page; Figure 4-5 moved to 4.4.2, where it is printed; the PMT settlement method "has potential" (the file said it applies); consolidation tests "usually essential" and shear tests "considered" (the file said required). |
| ch 5 Geotechnical Design (25c6271) | 47-102, all | Rebuilt: 5 printed headings added (5.2.1.1-5.2.1.3, 5.2.7.1, 5.2.7.2), 41 sections | Eqs 5-1 to 5-41, the 23 figures and 15 tables with pages and values; Table 5-13 lists 13 rock types and Table 5-14 16 (the file said 14 and 17); preconsolidated soils are "up to" an order of magnitude less compressible (the file said about 10 times); the ground water rise is "to the ground surface" and halves the unit weight terms; 5.2.11 names only seismic loads (the file added wind and ice); 5.2.8 asks for an "adequate" FS, not FS = 3.0; Figure 5-19 has six curves; 5.3.5's foundation soil check is not printed; Eq 5-38 P_v and Eq 5-41 a_1b defined as printed. Restored: the net-pressure reporting rule, the interim 1.5-2 multiplier to avoid, Load Groups VII-XI, the local-shear exceptions (tan 38 example), the Gifford and Briaud studies and the D'Appolonia drawbacks. |
| ch 6 Shallow Foundation Design for Bridges (9a9078e) | 103-122, all | Fixed in place | Figure 6-2 was missing; Eqs 6-1 to 6-13 read from the page; Table 6-2 with its load group descriptions. Restored: the Appendix C rework of examples 1 and 3, the aggradation, contraction and pier scour detail, channel migration (design floodplain footings for the worst scour; footings migration could expose as in the main channel), keys into softer rock with pneumatic tools, the weathered rock excavation rules and the 1991 FHWA scourability memorandum, TM 5-852-6, permafrost, the 1-2 percent self-weight rule, Munfakh et al. (2000) for expansion testing and ground improvement, the concrete-and-steel margin of 6.5. Not printed: "most" frost-susceptible (the print says "common"), at-rest design "as a conservative approach", "OCR significantly affects", fill in front "often" poorly compacted. |
| ch 7 Minor Structure Support on Shallow Foundations (96cec58) | 123-124, all | Fixed in place | The overturning factors are "greater than about" 2.0 and 1.5; 7.4's "all applicable load cases" is not printed. |
| ch 8 Shallow Foundation Design for Buildings (5381047) | 125-132, all | Fixed in place | 8.3 has no printed text: the file's body was invented and its "settlement governs for wide footings and granular soils" is not printed (now a pointer); not printed: code minimums "may be exceeded", "good engineering practice", "compensated foundations", the computed 12.5 mm; deepening a narrow footing "may be" more practical than a key, and bearing capacity "generally" does not govern mats. |
| ch 9 Construction Documents (fd37041) | 133-136, all | Fixed in place | 9.1 has no printed text (the file's body was invented; now a pointer); Figure 9-1 was a raw id/title/description record whose "15 m of embankment before abutment construction" and "3H:1V end slope" paraphrased a printed 15 m (50 ft) minimum dimension and a "3 min : 1" slope; 9.1.1 restores the backfill reference, drainage detail, specification items, soft or liquefiable soils, special shoring and payment. |
| ch 10 Inspection and Construction Monitoring (9e2c70b) | 137-140, all | Fixed in place | The print says dewatering in a clay profile can induce consolidation and that wells improve the stability of sloped excavations; the file had wells inducing consolidation. The fill testing list belongs to 10.3 (the file put it in 10.2.3). 10.2 has no printed text (now a pointer). |

### GEC-6: found but not fixed

- The section checker flags 4.3.3 In Situ Testing as misnumbered (target
  4.3). 4.3.3 is a printed heading; its title matches the 4.3 title
  "Subsurface Explorations and In Situ Testing". This is a false flag.
  The 5.0 title difference and the 6.0, 7.0, 8.0 and 10.0 introductions
  flagged as extra are the accepted chapter introductions.
- Retrieval eval (`scripts/eval_retrieval_gold.py --per-case`, against
  main 8ed9e19): auto recall@5 stays 41/54; only the rerank arm moves
  (R@10 43 -> 42, MRR@10 0.571 -> 0.559). The queries were left as they
  are.
  - presumptive ("presumptive bearing pressure on rock from RQD",
    relevant gec_6 5.2.7 only): rerank rank 1 -> 2; off, fill and auto
    stay at 1. The new 5.2.7.2 Rock, which now holds Table 5-9 and the
    RQD text, ranks first. The gold could list 5.2.7.2 as well.
  - ec7-compaction (eurocode_7_1 3.3.5): rerank rank 10 -> not in the top
    10; rel-compaction (dm7_2 3-5.1): rerank rank 4 -> 5. GEC-6 5.3.5
    Footings on Structural Fills, now with its printed compaction text,
    ranks first for both queries in the rerank arm. The other arms are
    unchanged.

### GEC-6: print inconsistencies (kept as printed)

- 2.7.2 names Nevada DOT "Type 1 Class B" aggregate base; Table 5-10
  names "Type 1A Aggregate Base".
- 4.3.2: the extremity rule prints "over 9 m (100 ft)"; the sentence before
  prints 9 m (30 ft). 4.3.3 prints "Riaund & Miran, 1992" and "ASTM 3441".
- Table 4-3 gives gamma_w = 9.8 kN/m3; 4.4.3 gives 9.81.
- At D_W = D_f, Table 5-3 gives C_W-gamma = 0.5, but Eq 5-9 gives
  0.5 + 0.5 D_f/(1.5B_f + D_f).
- Figure 5-8 prints B_f* = B_f L_f / 2(B_f + L_f) for a rectangle, which
  gives B_f/4 at L_f = B_f; the line above prints B_f* = B_f for a square.
- The RQD example of 0.5 m (18 in) of a 1.5 m (60 in) run gives 0.33 in
  metric and 0.30 in inches.
- 5.2.3.4 prints "Munfahk et al., 2000"; 5.3.4.2 and 5.3.6 print Munfakh.
- 5.3.4 names six Gifford methods but says "each of the five"; Figure 5-17
  shows five (no Oweis).
- 5.2.8 refers to AASHTO SLD Load Groups VII through XI; Table 6-2 lists
  Groups I to X.
- Kept as printed: Table 5-7 note 4's "40 mm" minimum depth below grade,
  Table 5-6 note 5's "joint spacing greater than 2 mm", Table 5-11's "0.04
  to 0.006" for uniform silts, the Eq 5-24 stress subscript "v f", and
  Eq 5-22's C_r where the text says C_R.
- 6.2.1 cites "Table 6-1" for general guidelines on design against scour;
  Table 6-1 is the design-step list. Table 6-1 cites bearing capacity
  "(Section 5.1)" and settlement "(Section 5.2)", printed in 5.2 and 5.3,
  and structural design "(Section 6.5)", printed in 6.6. Table 6-2 prints
  "Groups I though III".
- Figure 9-1 Note 1: highway embankment and select material "shall be
  placed simultaneously of the vertical payment line".

### GEC-6: gates

On the final tree of `fix/ref45-gec6`:

- `python scripts/audit_chapter_text.py gec_6`: exit 0 (10 chapters).
- `python scripts/check_section_numbers.py gec_6`: exit 0; printed 127,
  matched 126 (the flags above).
- The app's `test_citations.py` (this library on PYTHONPATH): exit 0, 5
  passed.
- The 19 targeted test files: 838 passed, 3 xfailed. The REF-48 question
  stays an expected failure on this branch (it starts from main, without
  the GEC-12 rebuild).

## Micropile Design and Construction, FHWA NHI-05-039 (branch `fix/ref45-micropile`)

Branch from main 63fb31f (after the GEC-12 and GEC-6 merges). Printed
pages are chapter-page labels (5-10 is chapter 5, page 10). All ten
chapters were wrong throughout: the files had 69 sections for 203 printed
headings (the section checker matched 62 and found 132 missing), merged
neighbouring headings into ids such as 5.9.1-5.9.2, gave objects no
pages, and carried many statements, and most of the ch 5 equations, that
are not printed. Every chapter was rebuilt from the print, one section per
printed heading; a heading with no printed text under it is a short
pointer to its subsections. The section checker now matches all 203. The
figure catalog was not changed (132 figures; ch 1-8 have 3, 5, 14, 18,
27, 44, 13 and 8).

| Chapter | Pages read | Result | Examples |
|---|---|---|---|
| ch 1 Introduction (463af89) | 1-1 to 1-8, all | Rebuilt: 4 sections (the file had five) | The file's 1.4 "FHWA Classification System Overview" and 1.5 "Report Organization" are not printed in ch 1 (1.4 is the references). Not printed: FOREVER as a French FHWA project, 3000 kN design loads, first U.S. use in the mid-1970s, w/c 0.45-0.50. |
| ch 2 Micropile Classification (4981ec2) | 2-1 to 2-9, all | Rebuilt: 4 sections (the file had four) | The file's 2.4 "Classification Summary" (eight combinations, designer and contractor roles) is not printed; 2.4 is the references. Figures 2-1 to 2-5 carry their printed captions; Table 2-1 read from the page with its sub-types. Not printed: Type B "most common in the US", CASE 2 "settlement reduction". |
| ch 3 Applications (c2e201b) | 3-1 to 3-21, all | Rebuilt: 16 sections (the file had five; 3.2.1-3.2.7, 3.3, 3.3.1 and 3.5 were missing) | The file's nine figure captions were not the printed ones; the twelve case histories as printed. Not printed: design loads of 300 to 3000 kN, FOREVER and Trinh in 3.3.4, "Approach 1 more common in the U.S.". |
| ch 4 Construction Techniques and Materials (ea4778e) | 4-1 to 4-35, all | Rebuilt: 21 sections (the file had five) | The file's fifteen figure captions were not the printed ones ("Rotary Duplex Drilling" as Figure 4-1, a "Symmetrix" figure); Tables 4-1 to 4-5 read from the page. Not printed: bentonite limited to 2 percent, "Type B the most common U.S. method", bond strength rising from Type A to D, hollow bars 517-862 MPa and threadbars 517-1035 MPa. |
| ch 5 Design of Micropiles for Structural Support (f77e6cb) | 5-1 to 5-82, all | Rebuilt: 52 sections (the file had 15, with merged ids 5.9.1-5.9.2, 5.9.3-5.9.4 and 5.15-5.16) | Eqs 5-1 to 5-32 read off the rendered pages, including 5-4a to 5-4c; the file's Eqs 5-11 to 5-32 were mostly not the printed equations ("Meyerhof 0.92 q sqrt(B)/N", "verification load = 2.0 P", "Fa/(0.47 Fy)"). Figures 5-1 to 5-27 and Tables 5-1 to 5-13 with pages. The two subsections the print numbers 5.21.1 and 5.21.2 under 5.20 are folded into the 5.20 body with their printed numbers; 5.21.1 and 5.21.2 are the seismic subsections. |
| ch 6 Design of Micropiles for Soil Slope Stabilization (1d1ca74) | 6-1 to 6-68, all | Rebuilt: 35 sections (the file had ten) | Eqs 6-1 to 6-15 read off the rendered pages; the file numbered the P = 0 and P = Pult capacity rules 6-7 and 6-8 (printed 6-6 and 6-7) and attributed Eq 6-12 to "Broms (1964)" (the print gives Ito and Matsui (1975) as stated by Hassiotis et al. (1997)). The file's Blue Trail key point carried the SUM-271 counts (154 micropiles, 41 anchors); Blue Trail used 478 micropiles and 40 ground anchors. Table 6-3 values (365, 523 and 558 kN) read from the page. |
| ch 7 Micropile Load Testing (b30d5ea) | 7-1 to 7-28, all | Rebuilt: 29 sections (the file had eight) | Tables 7-1 and 7-2 load schedules read row by row; Table 7-3 proof test frequencies. The file called the creep test "the key acceptance criterion"; the print says the creep criteria very rarely govern. Not printed: "report creep measurements at each load hold", "document any deviations". |
| ch 8 Construction Monitoring and Inspection (2b16647) | 8-1 to 8-18, all | Rebuilt: 16 sections (the file had seven) | The work plan has 19 printed elements (the file said 15); Tables 8-1 and 8-2 read from the page. Not printed: "owner agency performs both QA and QC" under the method approach. |
| ch 9 Contracting Methods (bdfa058) | 9-1 to 9-9, all | Rebuilt: 12 sections (the file had six; 9.3.1-9.3.3 and 9.5.1-9.5.3 were missing) | Contractor minimums as printed (five successful projects in five years; a supervising engineer with three years and three projects; three load test reports; superintendents and drill operators with three projects in five years). Not printed: "years in business, footage installed", value engineering savings "split with owner". |
| ch 10 Cost Estimating (6d71120) | 10-1 to 10-10, all | Rebuilt: 14 sections (the file had four) | Tables 10-1 to 10-7 read from the page, each in the section that prints it (the file put Table 10-1 in 10.1 and Table 10-5 under 10.3); the sample problems as printed ($300 x (1 + 85/100) = $555 per meter, $6,660 per 12-m micropile; $300 x (1 + 10/100) = $330 per meter, $6,600 per 20-m micropile). |

### Micropile: found but not fixed

- Retrieval eval (`scripts/eval_retrieval_gold.py --per-case`, against
  main 63fb31f): recall@3, @5 and @10 unchanged in the off, fill and auto
  arms (auto 35, 41 and 44 of 54); rerank recall@5 38 -> 37; MRR@10 off
  0.466 -> 0.463, fill 0.531 -> 0.528, auto 0.565 -> 0.559, rerank 0.515
  -> 0.502. No query was reworded.
  - micropile-bond ("grout to ground bond strength micropile"): its gold
    id 5.9.1-5.9.2 was the file's merged section and no longer exists, so
    `test_gold_set_is_well_formed` failed. The gold now names 5.9.2, the
    section that prints Table 5-3 (p. 5-21, PDF page 113); the query is
    unchanged. Ranks off 4, fill 4, auto 2 -> 3, rerank 1 -> 2: the
    rebuilt 1.2 and 2.1 (the micropile definition and classification)
    rank above it.
  - plasticity-chart (dm7_1 1-3.3.1): rank 2 -> 3 in every arm; DM 7.1
    and FHWA Pavements 4.7.2 swap places. No micropile section is in the
    top five; the move comes from the changed corpus statistics.
  - stone-col-capacity (gec_13 5.4.1.2.5): rerank rank 5 -> 6; the other
    arms are unchanged.
- The search index lives in the temp folder and is rebuilt only when a
  chapter file is newer than it, so two checkouts sharing one temp folder
  can search each other's index. The evals above ran with a temp folder
  per checkout. This affects only side-by-side checkouts, not an
  installed library (noted, not fixed).
- The section checker reports 9.3.2 and 9.5.2 as ambiguous: the contents
  print 9.5.2 Postbid Design as a second "9.3.2". The body prints 9.5.2.

### Micropile: print inconsistencies (kept as printed)

- Contents: 6.6.4 "Bending Momemt"; 9.5.2 printed as "9.3.2"; the 5.2 and
  6.7 titles differ between the contents and the body (6.7 "Design
  Examples" in the contents, "Design Example" in the body).
- 2.1 prints "micopiles"; Figure 3-7 prints "Underpining"; Figure 6-9
  prints "Uplsope"; 9.3.2 prints "Microple".
- 2.3 says the sub-classes (A1 to A3) indicate drill casing and
  reinforcement, then calls the 1, 2, 3 of the combined designation the
  "grouting method".
- Table 4-2 gives the #18 bar yield as "1335 (3000)" kip-units where
  Table 4-3 gives 1335 (300); the Table 4-2 caption says "Yield and
  Ultimate Strengths" but only yield is tabulated; the Table 4-2 notes
  give fu = 690 MPa (102 ksi) for Grade 520 and 700 MPa (104 ksi) for
  Grade 550, while the Table 4-3 notes print "Grade 500" with fy = 520
  MPa and fu = 690 MPa (100 ksi), and Grade 550 with fu = 700 MPa (102
  ksi).
- 5.6 refers to coupled sections "previously discussed in Chapter 3"
  (printed in ch 4). Eq 5-5 uses l where its variable list says L.
  5.9.3 Steps 1 and 2 both cite Eq 5-14. Eq 5-12 uses D/Bg <= 2.5 while
  Eq 5-13 uses D/Lg > 2.5. CCTG "5 mm (0.196 mm)". 5.17 prints "fill has
  recently been placed on the earlier". Brown et al. is cited as both
  1988 and 1998. 5.18.2 calls the combined stress check "Eqs. 5-4 and
  5-6" where its Step 6 uses Eq 5-3 or 5-6 (Eq 5-4 gives the casing
  section properties), and cites Sections 5.5.3 and 5.18.3 for threaded
  connection weakness (5.5.3 is Selection of Micropile Cross Section).
- Table 5-12 prints dense sand as "96,000 - 76,000" kPa, and medium dense
  sand as 29,000-96,000 kPa against 600-1,000 ksf. Table 5-8 skips 200 to
  300 kPa. The ch 5 reference list prints "Meyerhoff".
- PDF pages 171-174 and 175-178 both print pages 5-79 to 5-82 (the
  ch 5 references appear twice). The two subsections under 5.20 are
  printed as 5.21.1 and 5.21.2.
- 6.7.2 says the micropile was modeled with Approach 2 of 6.6.2.2 (a
  restraining force input directly) but describes varying the shear
  strength assigned to the micropile until the target factor of safety
  was reached, which is Approach 1.
- 6.7.4: "Labove is approximately 10 m (3.28 ft)".
- 6.7.6: the step list says to change M "in Step 1" and Q "in Step 5" and
  to repeat "steps 1 through 4" comparing Mult "in step 3"; trial M and Q
  are input in Step 2 and Mult is compared in Step 4.
- 6.7.7 labels the interpolated downslope value "Hult (psi_us) ... 450 kN"
  (psi_ds = 21 degrees). Figure 6-35 heads its Hult-soil/pile column in
  kN/m; the text gives the value at the 10-m slip surface as 753 kN.
- The 6.7 summary prints the proof test load as "760 kN (171 kN)".
- 7.4.1.2 says the first cycle raises the load to 15 percent of the design
  load and returns to the alignment load; Table 7-1's cycle 1 goes to
  0.45 DL. 7.4.3.2 calls 1.3 DL "the maximum test load" of a proof test;
  7.4.2.1 and Table 7-2 take it to 1.60 DL. Table 7-3 gives slope
  stabilization proof tests "to a test load of 2.0 times Pult"; the 6.7
  summary gives 1.6 times. The text cites "Bermingham and Jane (1989)";
  the references list Bermingham and James.
- 8.2 says the contractor under the method approach provides "quality
  assurance". 8.6.3 prints the 28-day strength as "25 and 40 MPa (3,600
  and 5,800 ksi)".
- 9.4 (Performance Specifications) lists the owner and contractor items
  under "In the design/build method".
- 10.2.2 gives the common casings as 140, 175 and 241 mm (9-5/8 in.);
  Table 10-2 lists 139.7, 177.8 and 244.5 mm. 10.3.3.2 prints "10 to 12
  meters (330 to 40 ft)".

### Micropile: gates

On the final tree of `fix/ref45-micropile`:

- `python scripts/audit_chapter_text.py micropile`: exit 0 (10 chapters).
- `python scripts/check_section_numbers.py micropile`: exit 0; printed
  203, matched 203 (the 9.3.2/9.5.2 contents misprint shows as 2
  ambiguous).
- The 19 targeted test files plus `test_micropile_figures.py` and
  `test_micropile_tables.py`: 1017 passed, 2 xfailed;
  `test_dm7_2_chapter6.py` and `test_gec13_tables.py` (which also name
  micropile): 335 passed.
- The app's `test_citations.py` (this library on PYTHONPATH): exit 0, 5
  passed.
