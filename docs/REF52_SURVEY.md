# REF-52: printed headings with no section, across the library

Survey only (2026-10-31): no heading was added and no text file changed.
GEC-10 has since been written from the print; see "GEC-10 written from the
print" at the end. The gec_10 row in the table is the survey's count, before
that work.
`scripts/check_section_numbers.py --detail` was run over every reference whose
PDF is in `docs/`, on main 1c9a642 (gec_7 re-run on dd09a27, after
REF-46). Every missing heading was then listed with
its page, and 3 to 7 per reference (about 110 in all) were looked at in the
checker's own text lines around the heading, and on the page where that was
unclear, to class each one as a real gap or a checker misread.

## How to read the table

- **Printed**: numbered headings the checker reads off the print (PDF outline
  and page text) in chapters that have a text file. Each chapter is counted
  once, even when two files share its number (see ufc_stabilization).
- **Own section**: a section of its own carries that number.
- **In a range**: covered only by a range section such as `5.1-5.4`. The
  heading's text, if it is there at all, sits inside a section that has a
  different number.
- **Other**: covered by a misnumbered section that the checker matched by
  title.
- **Missing**: no section covers the number. This is the checker's own count,
  taken once per chapter.
- **Real / misread**: the estimate from the sample and from a scan of every
  missing title. A title that reads as a sentence, a figure or table label,
  or one of five or more headings on the same page was opened. Most of those
  turned out to be real headings (example and step headings, IBC section
  headings). The misreads found are listed under the table.
- **Chars/page**: text characters in the reference's files (body and summary)
  per PDF page. It is a guide to how full the files are. A printed page holds
  about 3,000 characters. Below about 300, the files are condensed summaries,
  so a missing heading usually means its text is missing too. Adding it means
  writing the section from the print, not relabelling text that is already
  there. GEC-5 ch 8 shows this: its file is two range summaries
  (`8.1-8.5`, `8.6-8.9`), and none of 8.10 Subgrade Reaction (8.10.1,
  8.10.2 p-y Curves) appears anywhere in it.

| Reference | PDF pp | Printed | Own section | In a range | Other | Missing | Real | Misread | Chars/page |
|---|---|---|---|---|---|---|---|---|---|
| aashto_1993 | | | | | | skipped: scanned PDF, no text layer | | | |
| california_trenching | 342 | 116 | 46 | 0 | 0 | 70 | 67 | 3 | 259 |
| dm7_1 | 574 | 465 | 457 | 0 | 0 | 8 | 8 | 0 | 1,198 |
| dm7_2 | 724 | 437 | 421 | 0 | 0 | 16 | 15 | 1 | 1,183 |
| em_2104 | 135 | 39 | 39 | 0 | 0 | 0 | | | 308 |
| em_2107 | 454 | 269 | 35 | 0 | 0 | 234 | ~185 | ~50 | 115 |
| eurocode_7_1 | 171 | 231 | 167 | 0 | 0 | 64 | 64 | 0 | 1,841 |
| eurocode_7_2 | 199 | 259 | 45 | 0 | 0 | 214 | 214 | none seen | 708 |
| fema_p2082 | 593 | 55 | 24 | 3 | 0 | 28 | 28 | 0 | 85 |
| fhwa_pavements | 598 | 132 | 18 | 0 | 5 | 109 | 109 | 0 | 99 |
| fhwa_soils_foundations | 1,056 | 488 | 487 | 0 | 0 | 1 | 0 | 1 | 1,183 |
| gec_10 | 747 | 408 | 122 | 0 | 2 | 284 | 284 | none seen | 173 |
| gec_11 | 736 | 214 | 148 | 0 | 0 | 66 | 66 | 0 | 237 |
| gec_12 | 1,435 | 471 | 293 | 80 | 0 | 98 | 98 | 0 | 300 |
| gec_13 | 944 | 1,136 | 771 | 0 | 2 | 363 | 363 | none seen | 892 |
| gec_14 | 103 | 26 | 5 | 16 | 0 | 5 | 5 | 0 | 164 |
| gec_4 | 304 | 234 | 8 | 85 | 0 | 141 | 140 | 1 | 164 |
| gec_5 | 688 | 390 | 2 | 297 | 0 | 91 | 91 | 0 | 94 |
| gec_6 | 296 | 127 | 126 | 0 | 1 | 0 | | | 742 |
| gec_7 | 425 | 235 | 160 | 9 | 0 | 66 | 66 | 0 | 687 |
| gec_8 | 293 | 184 | 19 | 17 | 0 | 148 | 148 | none seen | 185 |
| gec_9 | 293 | 187 | 62 | 0 | 0 | 125 | 125 | none seen | 423 |
| gsa_collapse | 203 | 129 | 128 | 0 | 0 | 1 | 0 | 1 | 356 |
| micropile | 456 | 203 | 203 | 0 | 0 | 0 | | | 716 |
| ufc_collapse | 244 | 168 | 120 | 0 | 0 | 48 | 48 | 0 | 373 |
| ufc_concrete_practice | 194 | 318 | 318 | 0 | 0 | 0 | | | 2,046 |
| ufc_flexible_practice | 150 | 307 | 265 | 0 | 0 | 42 | 42 | 0 | 2,019 |
| ufc_pavement | 290 | 314 | 314 | 0 | 0 | 0 | | | 1,016 |
| ufc_stabilization | 84 | 212 | 89 | 0 | 0 | 123 | 123 | 0 | 1,442 |
| ufc_structural | 228 | 154 | 71 | 0 | 0 | 83 | 83 | 0 | 316 |
| wood_handbook | | | | | | skipped: printed headings carry no numbers | | | |
| **Total** | | **7,908** | **4,963** | **507** | **10** | **2,428** | **~2,370** | **~57** | |

Notes on the totals:
- The gec_7 row is main at 1c9a642. REF-46 (merged, dd09a27) adds all 66:
  the checker now reads gec_7 as 235 printed, 235 matched, 0 missing. So
  about 2,300 real gaps remain open.
- The checker's raw total is 2,585. The difference is ufc_stabilization: the
  checker reports 280, of which 157 are double counts (see "Checker quirks").
- "None seen" means the 4 to 7 opened from that list were all real. The real
  count is the missing count less any misreads found.

## Where the gaps are, by reference

Page numbers are PDF pages.

- **gec_13 (363).** The print restarts its numbering in each chapter, and the
  checker allows for that.
  - ch 2 Vertical Drains has 9 sections for 80 printed headings (2.1.1
    Description … 2.5.3.1 Site Preparation).
  - ch 2 accounts for 71 of the missing. The rest: ch 8 Grouting 109,
    ch 9 68, ch 1 60 (among them the 8.2.x "Step 1: …" headings, p57
    on), ch 10 23, ch 4 22, ch 7 8, ch 6 2.
  - Sampled 2.1.1.2 (p234) and 2.1.1.3 (p235): real.
- **gec_10 (284).** The files are shallower than the print in most chapters:
  ch 13 Field Load Tests 67, ch 9 33, ch 7 32, ch 4 27. Sampled 4.2.1 (p74),
  7.6.1 (p198), 9.3.3.4.1 (p254), 13.2.2.3.7 (p438), 13.2.3.1.2 (p442): real.
- **em_2107 (234).**
  - About 185 are titled subparagraphs (1.6.1 Risk Assessment, 2.3.3 Tainter
    Valves, 4.2.8 EQ Earthquake, 6.1.3.4 High-Strength Bolts). They come
    from the PDF outline only, because the text layer drops the
    auto-numbers.
  - About 50 are misreads. Roughly 43 are bookmarks of numbered list items
    or untitled paragraphs, such as 3.2.1.2 "Local and global instability;"
    and 4.4.6.6 "Substituting Equation 4.5 into …". Seven are rows of the
    load-factor table on p36 (1.0, 1.04, 1.24 "Gate Operation Friction").
- **eurocode_7_2 (214).** Real clauses in sections 2 to 5 (2.4.2.6,
  4.4.4, 5.12.3.1). The text layer is OCR-damaged ("Salnpling" for Sampling
  at 2.4.1.4), so titles need reading off the page.
- **gec_8 (148).** Real (5.3.1.3 p94, 5.8 p148, 6.6.1 p168, 8.3.2.2 p232).
  The 6.6 and 5.8 example-problem headings are real headings. 17 more
  headings sit inside 6 range sections.
- **gec_4 (141).** Real (2.2.2.3 p29, 3.3.3 p43, 5.3.6 p90). 85 more sit
  inside 12 range sections. 1 misread (9.9 is the caption "Figure A-4",
  p218).
- **gec_9 (125).** Real (3.3.1 p37, 6.3.3 p78, 11.4.5 p170). 99 of the 125
  have their parent section in the file.
- **ufc_stabilization (123).** Real: ch 4 50, ch 3 28, ch 5 13, ch 2 6
  (3-5.3 p37, 4-2.2.2.8 p53, 4-4.2.2 p59).
- **fhwa_pavements (109).** Real: ch 7 43, ch 4 20, ch 8 16, ch 3 8,
  ch 5 6. The checker places 15 ch 5 headings on p180, where the chapter
  opens with a list of its own sections. The headings are printed later,
  for example 5.2 on p181.
- **gec_12 (98).** All in Vol II (PDF volume 2, p33-521), outline and page
  both:
  - ch 9 21 (9.1.1-9.5.3);
  - ch 16 17 (pile toe attachments, splices, welding checklist);
  - ch 10 13 (10.6.x, 10.8.x);
  - ch 18 13 (18.5.x, 18.7.1-18.7.9 hammer types);
  - ch 12 9 (12.5.1-12.5.9 Examples 1-9, real headings);
  - ch 11 7, ch 13 7, ch 17 2.

  A further 80 headings sit inside 24 range sections (10.1-10.3,
  15.1-15.7, 15.8-15.16 and others).
- **gec_5 (91).** Real. Its files are 28 range summaries, which cover 297
  of 390 headings, and only 2 headings have a section of their own. The 91
  are the subheadings after each range's last number plus anything outside
  the ranges. They include 8.10, 8.10.1 and 8.10.2 p-y Curves (p356), and
  10.6.1-10.6.3 piezometers (p427).
- **california_trenching (70).** Real, top level included (2-1 to 2-5, 3-1,
  3-3, 3-5, 3-8, 4-1, 6-1, 6-3, 7-1, 7-4, 10-1), as are the Example 7-1A …
  subheadings. 3 misreads: 2-2.01, 2-2.02 and 2-2.05 are numbered
  definitions (p27).
- **gec_11 (66).** Real (2.5.2 p64, 3.3.1 p102, 10.4.6 Vol II p96); 61 of
  65 have their parent in the file.
- **eurocode_7_1 (64).** Real clauses (1.1 p11, 2.4.7.3.4 p34, 6.6 p67,
  7.5.2 p77, 7.6.2.7 p84); 28 are in section 7 Piles.
- **ufc_collapse (48).** Real, 36 of them in ch 3 (3-2.11.2.3 p59, 8-4.1
  p91).
- **ufc_flexible_practice (42).** Real, 22 of them in ch 2 (2-2.1.1.5 Hot
  Bins p22, 2-4.2.7.1 Flow p44).
- **ufc_structural (83).** Real: IBC and ASCE modification subsections such
  as 2-1.1 "Section 101 - GENERAL" (p29) and 6-3.1 "Section 1807 …" (p109).
- **fema_p2082 (28).** Real (11.4.7 p56, 21.1.3 p128); 17 in ch 11.
- **dm7_2 (16).**
  - 15 are real. Of these, 12 come from the outline only, because the text
    layer drops the numbers: 6-1.1-6-1.4 (p402 prints "INTRODUCTION. Scope."
    with no numbers), 3-1.3, 4-9.1-4-9.3, 5-4.10, 6-9.1, 6-10.5. 7-6
    Suggested Reading is real but of little value.
  - 1 misread: 2-22 is "Figure 2-22" (p137).
- **dm7_1 (8).** Real; printed as "N-N.N" then the title on its own line
  (1-3.2.3 p41, 4-2.2 p211, 8-4.5 p476).
- **gec_14 (5).** Real (1.3 p16, 3.4.1-3.4.4 p34). 16 more sit inside 2
  range sections.
- **fhwa_soils_foundations (1)** and **gsa_collapse (1)** are misreads:
  11.8 "Step 3" is a step list (Vol 2 p468); 3.19 is "Figure 3.19." just
  before Equation 3.18 (p48).

## Misread classes found

These are few, about 57 of 2,428 (2 %):
- bookmarks of numbered list items and untitled paragraphs (em_2107, about
  43);
- table rows (em_2107 p36, 7);
- numbered definitions (california_trenching, 3);
- figure labels and cross-references (dm7_2 2-22, gec_4 9.9, gsa_collapse
  3.19);
- a step list (fhwa_soils_foundations 11.8).

None of the samples was a running head. One real-heading case has the
wrong page: a chapter's own list of its sections (fhwa_pavements p180).

## Checker quirks

These were noted, not fixed.

- **ufc_stabilization appendix files.** Its `appendix_a/b/c.json` number
  their sections 1, 1.1, 2 …, so the checker files them under chapters 1-3.
  It then counts every heading of those chapters as missing again: 157
  double counts in the raw 280.
- **Range sections.** A range covers the headings from its first number to
  its last number in print order, but not the last number's own
  subheadings. That is why 8.5.1-8.5.4 and 8.9.1-8.9.4 show as missing in
  GEC-5 ch 8 (`8.1-8.5`, `8.6-8.9`). Where the files are summaries, as in
  GEC-5, that text is not in the file either.

## Chapters with no text file (not counted above)

The checker counts only chapters that have a file. The printed numbered
headings in chapters without one are below. Whether each one was left out
on purpose was not checked. em_2107 is the largest case: its functions use
ch 10 and Appendices D-F (its module docstring says so), but its text files
stop at ch 6, so there is no retrievable text behind those functions.

| Reference | Chapters | Printed headings |
|---|---|---|
| em_2107 | ch 7-16, App A-F | ~1,320 (numbered paragraphs included) |
| ufc_structural | App A-I | 193 |
| fema_p2082 | ch 1, 2, 12-15, 18 | 157 |
| ufc_collapse | App B-G | 126 |
| eurocode_7_2 | Annexes L-X | 111 (the annex files exist but are not keyed to annex letters) |
| ufc_concrete_practice | App A-F | 105 |
| gec_12 | App D | 75 |
| ufc_pavement | App B-H | 75 |
| fhwa_pavements | ch 1, 2, 6, App B-D | 68 |
| gec_10 | keyed "X" by the checker | 64 (not examined) |
| dm7_2 | App B | 59 |
| em_2104 | App B-G | 35 |
| california_trenching | ch 1, 9, App A, C, D | 33 |
| gec_8 | App A, B | 29 |
| ufc_stabilization | App A, B | 28 |

Smaller ones (under 25 each) are in eurocode_7_1, fhwa_soils_foundations,
gec_10 (App A-C), gec_11, gec_6, gec_9 and ufc_flexible_practice. Single headings keyed to
chapters such as "68" or "47" are checker misreads of page or figure numbers.

## Reproduce

From the repo root, with a temp folder of its own:

```
python scripts/check_section_numbers.py --detail --json <out>.json
```

The counting above takes each chapter once and intersects the missing sets of
files that share a chapter number. The tools used (survey, classifier, peek)
are scratch scripts outside the repo.

## GEC-10 written from the print

GEC-10 (FHWA-NHI-18-024, 2018) was rewritten chapter by chapter on
fix/ref52, one commit per chapter (ch 1, 3, 4, 5, 7, 9 to 18). Every
printed heading now has its own section, with its body read off its
printed page. Each equation, figure and table sits in the section that
prints it. Equations were read off rendered pages, symbol by symbol.
Chapters 2, 6 and 8 already had a section for every printed heading and
were not changed. The REF-40 sections of
ch 10 (10.1, 10.2, 10.3.5 to 10.4), which match the 2018 print, were
left as they were.

`check_section_numbers.py gec_10` now reads 408 printed, 391 matched,
17 missing and 1 extra (it was 122 with a section of their own and 284
missing):
- The 17 missing are ch 13 numbers that only the PDF outline carries
  (13.2.3.1.2, 13.2.3.2 with 13.2.3.2.1-8, 13.2.3.3, 13.3.1.1-2,
  13.3.2.1-2, 13.3.3.1-2). The page headings number the same headings
  differently, and the sections follow the page (see ch 13 below).
- The 1 extra is 17.6 Summary. The page prints it as "7.6 SUMMARY" and
  the outline leaves it out.

### Values the old files gave that the chapter does not print

These were replaced with the printed text. Where the print gives a
value, it is in brackets.
- ch 3: old 3.6 held sleeve-port and permeation grouting (that text is
  4.4.2's) and cited Appendix H [Appendix F, p. 3-16].
- ch 5: old 5.3 said permanent casing "eliminates side resistance in the
  cased zone" [p. 5-22/23: casing in an oversized hole cannot be relied
  on; impact-driven casing is like a driven pipe pile]. Old 5.4 gave
  slurry limits that the 2018 manual prints nowhere (bentonite 8.5-9.0
  lb/gal, Marsh 28-40 s, 1.15 g/cm3 or less, pH 7.5-11; polymer 34-80 s,
  1.01 g/cm3 or less, pH 7-12) and an unprinted table [ch 5 text: Marsh
  28-50 s, polymer 32-135 s, sand 4 % and 1 %; App. D X.3.4: 64.3-72 pcf,
  28-50 s, pH 8-11, sand 4.0 % max].
- ch 7: old 7.4 to 7.7 gave 500-1000 psi before drilling within about 5
  diameters, cement 600-800 lb/cy, slump 6-8 and 8-10 in., slump flow
  20-28 in., bleed 0.4 cm3/cm2 or less, f'c 4000 psi, 50-90 F, 2 cylinders
  per 100 cy and a 5-10 % volume overage [initial set and 3 diameters
  clear spacing; dry slump 6 to 9 in., tremie slump about 9 in., slump
  flow 16 to 22 in.]. Table 7-2's admixture ranges (0-5, 0-15, 3-5, 5-15
  oz/cwt), which the text layer drops, were read off the rendered page.
- ch 9: old 9.3.2 described Broms' method [9.3.2 is the equivalent-fixity
  planning estimate, Mn about 27 D^3 or 40 D^3; Broms is only an
  alternative in 9.3.4]. Old 9.3.3 gave three Matlock (1970) soft-clay
  p-y equations that the 2018 manual does not print; they were dropped.
- ch 10: old 10.5 gave "gamma_EQ = 0.5 for Extreme Event II". Old 10.6
  gave "gamma_DD = 1.25 for Strength I and IV", resistance below the
  neutral plane equal to factored loads plus factored downdrag,
  bituminous coating, isolation collars and residual-strength
  post-liquefaction downdrag [drag is not present at the geotechnical
  strength limit, only structural strength and service;
  post-liquefaction drag is 50 % of the pre-earthquake beta side
  resistance].
- ch 11: AASHTO minimum spacing 2.5B and 3.0B, eta = 0.65 at 3B in cohesive
  soils, an equivalent footing "at 2/3 of embedded depth" with a
  Terzaghi-Meyerhof-DeBeer correction, and two unnumbered group equations
  [typical minimum 3 diameters, sometimes 2.5; group effects below 4
  diameters axially and 5 laterally; cohesive eta from the block, Eq.
  11-2; cohesionless eta 0.65, 0.80 and 1.0 at 2.5, 3 and 4 or more
  diameters; equivalent footing at D/3 above the toe, spread 1H:2V].
  11.5 keeps Table 11-1's values in its body, because test_gec10_text
  pins them there. The table object sits in 11.5.1, where it is printed.
- ch 13: resistance factors "up to 0.65-0.75 with a load test against
  0.50-0.55 without", lateral tests to "more than 1/2 in." causing damage,
  Statnamic "for medium-high capacity" and the Davisson criterion [rapid
  test: 0.05 below the AASHTO static-test value, max 0.65; high-strain
  dynamic: 0.10 below, max 0.60; the 1/2 inch is for uplift and
  bi-directional upward movement].
- ch 14: old 14.5 gave the same unprinted slurry limits as old 5.4. Old
  14.7 gave location (+/-3 in.) and alignment (1/4 in. per 10 ft)
  tolerances that the chapter does not print.
- ch 15: sediment limits (dry hole 2 in.; wet hole 1.5 in. where side
  shear is critical, 2.5 in. where end bearing is) and an eight-item list
  [Table 15-2].
- ch 16: TIP "typically 12-72 hours after placement" and sonic echo "PIT,
  ASTM D5882" [TIP results within 2 to 3 days, with a window of several
  days; no ASTM standard is cited for sonic echo].
- ch 17: an ASTM D6760 "flaw" definition (that wording is ch 16's; ch 17
  prints "Defect (noun) - a fault or flaw"), a four-step evaluation
  sequence, epoxy injection and jacketing, and sleeve-port side grouting.
- ch 18: markup "typically 5-15 %" [the print says reasonable markups
  cannot be quoted without knowing where costs are carried], inflation
  adjustment by the ENR index, unit conversion, and "mobilization
  negligible for large projects". The old Table 18-2 string named the
  FDOT cost template, which is Figure 18-1. Printed Table 18-2 is the
  Galveston bid tabulation.

### Print inconsistencies, kept as printed

No reading was chosen; the sections give what the page prints.
- ch 7: 7.6.4 says 3,500-4,000 psi is adequate, and 7.5 says 4,000-5,000
  psi is the typical requirement.
- ch 9: Figure 9-17's caption cites Equations 9-6 and 9-7, but the terms
  it defines are those of Eqs. 9-3 and 9-4. The text says 9.3.3.5 covers
  selecting p-y models; that is in 9.3.3.4, and 9.3.3.5 covers scour.
  9.3.5 cites a Section 9.2.5 that does not exist. 9.4.2.5 cites Figure
  9-5 (a sign structure). p. 9-18 gives concrete ultimate strain about
  0.003 and steel 0.0020, while Figure 9-19 plots concrete to 0.0038.
- ch 10: the failure-threshold equation is numbered 10-31 (p. 10-32), but
  the text and Example 10-6 call it Equation 10-30. Other slips: p. 10-32
  "Step 11-6"; Example 10-6 cites "Figure 13-10" twice for Figure 10-10;
  p. 10-33 cites Section 13.3.3 for 10.3.5. 10.3.7 places the
  closed-form equations in Appendix C and the solutions in Appendix D,
  and the p. 10-36 list of cases ends "..., and" after two items. Figure
  10-20 prints "Goudrealt".
- ch 11: 11.4.1.3 cites Section 11.6 for group settlement (11.4.2). Eqs.
  11-11 and 11-12 use C_cr, but the symbol list defines C_r. In Example
  11.6.2 (2 x 3 group), K_Psi = 7,672,800 k-ft/(in/in) uses x_i in feet,
  but Delta_z multiplies Psi_G by x_i in inches. The printed R_z = 173,
  496 and 819 kips do not satisfy moment equilibrium (2 x 24 ft x
  (819 - 173) = 31,008 kip-ft against 2,700 kip-ft applied); consistent
  units give about 468, 497 and 525 kips. Figure 11-11's caption prints
  "25.4 min = 1 inch".
- ch 12: the shear equation labels print 12-11, 12-12a, 12-13b, 12-14 to
  12-18, with no 12-12b or 12-13a, and the text cites them one lower. p.
  12-19 prints "0.5 phi V_u = 0.5 (0.90) 306" where phi V_c is meant. The
  upper-bound check compares 2,424 kips with "> 482.9 kips", the nominal
  V_c + V_s. p. 12-3 calls w_c = 0.145 a water-to-cement ratio (it is the
  unit weight in kcf). Table 12-2 prints "00030" for the 80 ksi
  compression-control limit. Other slips: Figure 12-11 "Docketed"; p.
  12-22 "l_ab" for l_db; "Section 12-6" for 12.6; "permissable".
- ch 13: the page headings and the PDF outline number 13.2.3.x, 13.3.1.x,
  13.3.2.x and 13.3.3.x differently, and the sections follow the page:
  - page 13.2.3.1.1 Hydraulie Jack, 13.2.3.3.2 Load Cell, 13.2.3.4 with
    13.2.3.4.1-8, 13.2.3.5; outline 13.2.3.1.2, 13.2.3.2 with
    13.2.3.2.1-8, 13.2.3.3;
  - page 13.3.1.3-9, outline 13.3.1.1-7;
  - 13.3.2 and 13.3.3: page .3-.5, outline .1-.3.

  The text's cross-references fit neither scheme ("Section 13.2.3.5" for
  strain gauges, "Section 13.2.3.3" for gauges) or only the outline
  ("Section 13.3.2.1"). Headings 13.2.2.3.4-8 (high-strain dynamic,
  uplift) sit under 13.2.2.3 Rapid Load Test in both. The List of
  Figures gives Figure 13-6 the caption of Figure 13-5. Other slips:
  p. 13-17 "6.6-ft (2000 mm)" and p. 13-18 "6.28-ft (2,000-mm)"; figure
  citations that point to the wrong figure on pp. 13-51 (13-19 for
  13-18), 13-52 (13-30 for 13-27), 13-53 (13-9) and 13-59 (13-56 for
  13-54); "Uplifting Test"; "Robinsons et al. (2002)".
- ch 15: "paymemt" and "preformed" for payment and performed.
- ch 16: the List of Figures and List of Tables carry a DFI (2018) CSL
  rating figure (16-2) and table (16-3) that are not printed on the pages.
  So their numbers run one ahead of the page captions from Figure 16-2
  and Table 16-3; the sections use the page captions. p. 16-5 still
  cites "Class C of Table 16-3", the unprinted DFI table; the printed
  Table 16-3 is the TIP table. p. 16-15 gives 1.35 percent as the
  probability of a reading three standard deviations below the mean (a
  normal distribution gives 0.135 percent). The Eq. 16-3 symbol list
  prints "G" for g. p. 16-23 core sizes overlap: NX for 1/2-inch
  aggregate, and 4-inch for 1/4 to 1 inch. The 16.4 heading prints
  "INTEGITY"; the text has "decibals", "gamma-gammma" and "impedence".
- ch 17: p. 17-5 cites deficiencies as Sections 17.3 and 17.4, evaluation
  as 17.5 and remediation as 17.6, one ahead of the headings (17.3, 17.4
  and 17.5). Table 17-1 gives CSL Class A as "FAT Increase < 15%" and
  "Energy Reduction <= 9 dB", with Classes B and C "see Table 16-2".
  Table 16-2 rates by velocity reduction and puts 6.1 to 9 dB in
  Questionable. p. 17-4 refers to the "CSL Rating Criteria of Chapter
  16", the DFI criteria that are not printed. Typos: "Decibals",
  "paramters"; the summary heading prints "7.6".
- ch 18: Table 18-1 prints a 12-month quantity of "1,.250" (SIGN MTS
  54 IN). Table 18-2 prints the 72-in. Engineer's estimate as "$475.001".
  The 18.4 heading prints "PUBLICALLY".
