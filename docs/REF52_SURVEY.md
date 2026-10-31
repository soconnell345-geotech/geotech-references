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
- **Numbered outline lines read as headings.** A guide specification
  printed as a numbered outline ("6.1. Drilling equipment", "4.1.
  Mobilization - lump sum") is read off the page as headings, because each
  line starts with a number and ends in a period. GEC-13 ch 7 (8, pp. 7-37
  to 7-38) and ch 8 (31, pp. 8-128/129) show these as missing; they are
  not headings.

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
| eurocode_7_2 | Annexes L-X | 111 (all matched now that the annex files are keyed to annex letters; see "EN 1997-2 written from the print") |
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

A review then found objects these passes had not stored, added on
fix/ref52-gec10 from the page that prints each: Figs 1-4, 1-5, 1-6, 1-8
and 1-9 in 1.3; Figs 6-2 to 6-28 and Table 6-3 in the ch 6 sections that
print them; Table 8-4, every row, in 8.1; the label Eq. 10-32 on the
10.4 uplift equation; and 3.2's full printed title. Ch 2's four captions
and table contents were paraphrases and now follow the print.

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

## GEC-12 Vol II written from the print

GEC-12 (FHWA-NHI-16-009, 2016) Vol II ch 9 to 18 was rewritten on
fix/ref52, one commit per chapter. The range sections (such as
"10.1-10.3" or "18.6-18.7") were split so that every printed heading has
its own section, with its body read off its printed pages; the
unnumbered chapter openings went into the first section. Each equation,
figure and table sits in the section whose pages print it. REF-04's
equation entries were kept. Those re-read off rendered pages, symbol by
symbol, did not change: 9-2, 9-5 to 9-8, 10-1 to 10-7, 11-1 to 11-10,
13-1 to 13-8, 14-1 to 14-6, 15-1 to 15-3 and 18-1 (ch 12, 16 and 17
print none). Ch 14 was the one Vol II file that nested sections under
`subsections`; it is now flat, like the others (`section_entries` reads
both).

`check_section_numbers.py gec_12` now reads 471 printed, 471 matched
(it was 293), with 0 range and 0 missing. The 1 extra (3.0 Introduction)
and the 2 ambiguous (7.2.3.2.2 and 7.2.3.2.3, which the contents number
one lower than the page) are in Vol I and were not changed.

### Print inconsistencies, kept as printed

No reading was chosen; the sections give what the page prints. Page
numbers are Vol II's printed page numbers.
- ch 9: no 9.2.1 is printed (9.2 is followed by 9.2.2), and p. 18 cites
  "Section 9.2.1" for the primary and back-up load systems (they are in
  9.2.2). p. 42 says the telltale load distribution "calculated from Eq.
  9-5 to 9-7" excludes residual load (the telltale equations are 9-4 to
  9-6; 9-7 is the strain gage force). p. 28 says unloading is "in four
  load decrements equal to 50% of the maximum load", while Table 9-2
  steps 200-150-100-50-0 percent of design load (25 % of the maximum
  each). "Measureand 2015" (p. 25) against "Measurand" (Figure 9-16);
  "Sellers (2015)" (p. 47) against "Sellers 1995" (p. 37).
- ch 10: three cross-references are one section off: p. 77 "Section
  10.3" for Eqs. 10-1 and 10-2 (10.4) and "Section 10.7" for EMX
  (10.8.2); p. 81 "Section 10.4" for wave mechanics (10.5). The fixed-end
  sentence on pp. 65-66 is garbled ("... the particle velocity must be
  zero material wave speed, C"). p. 97 says the compression stresses
  exceed the 50 ksi yield of the A572 Grade 50 H-pile, but the printed
  CSX 44.9, CSI 45.3 and CSB 49.5 ksi are below it (only the iCAP CSC,
  52.3 ksi, exceeds it); "As noted earlier" points at no earlier
  statement. "Hererra et al. (2009)" (p. 54) against the reference list's
  "Herrera".
- ch 11: p. 138 says the MUP single mass acceleration is "defined from
  the average of the pile head and toe displacement", then runs the UPM
  with "the average accelerations and velocities". p. 136 writes
  Fu(tmax) where Eq. 11-5 writes Fu(tumax). "Municiapl" (p. 150).
- ch 12: p. 159 says a bearing graph gives "two types of information"
  and lists three. Example 3 (p. 172) gives 45 blows/ft through the
  extremely dense layer, then says the resistance "increases to only 44
  blows/foot" deeper. Example 4 gives the compression stress limit as
  4.1 ksi (p. 175) and as 4.15 ksi (p. 177). p. 206 says "Section 12.8"
  discusses the diesel stroke options (12.7.1). p. 248 gives the time
  after impact "in m/s" (milliseconds elsewhere). Table 12-8 prints
  "4.o" (p. 229).
- ch 13: Table 13-6 (p. 278) does not close: the Gates underrun prints
  29,408 lf against 246,052 - 216,664 = 29,388; the paid-length total
  1,154,517 against 216,664 + 937,873 = 1,154,537; the underrun total
  86,638 against 29,408 + 57,227 = 86,635.
- ch 14: p. 301 (X.04 B 5) cites "Section X.06 C) 4" for the location and
  alignment tolerances, which are X.06 C) 5. p. 314 cites "the commentary
  of Section 14.2.5.1 A" (no such number; the commentary is under X.05
  A) 1). The contents list (pp. 284-285) and the body title three
  sub-items differently: X.06 B "Preparation of Piling" / "Preparation
  of Piles for Driving", B 2 "Collars for Timber Piles" / "Collars and
  Bands", X.06 C "Driving" / "Pile Driving". "Pile Marking for Prior to
  Driving" (pp. 285, 318).
- ch 15: p. 345 cites "Section 15.3" for templates (15.4). p. 391 cites
  "Section 14.2.1 and 14.2.3" for the Pile Installation Plan and the
  driving equipment (printed in 14.2.2 and 14.2.4). Table 15-2 (p. 380)
  bands "416 to 540" and "540 to 600" share 540 kips, and its bands (301
  to 415, 416 to 540) differ from Table 14-3's (301 to 420, 421 to 540).
  p. 385 cites "Reinwall et al. (2014)" and a "Reinwall pile"; the
  reference list (p. 394) prints "Reinhall". The 15.21 heading prints
  "NOISE SUPPRESION"; Figure 15-45's caption prints "drving".
- ch 16: p. 397 cites "Collin 2012"; the reference list (p. 431) prints
  Collin (2002). 16.5.2 (p. 426) preheats to a minimum 70 F and keeps a
  minimum 50 F until welding is done; the 16.5.4.1 checklist (p. 429)
  says the area is preheated "and maintained at 70 degrees". The p. 395
  sentence on attaching the toe protection device is garbled. p. 413
  cites "Section 7.10 7". p. 419 spells the same splice "Herkules" and
  "Hercules".
- ch 17: p. 434 says a switch from the Gates formula (phi 0.40) to a
  static load test (0.75) or 100 % dynamic testing "will result in an
  87% reduction in the required nominal resistance"; the required
  resistance scales by 0.40/0.75 = 0.53. The 63 % increase for 0.65 to
  0.40 agrees with 0.65/0.40. p. 435 cites waiting periods "noted in
  Section 14.5.2.1" (no such section; the restrike delays are Table 14-4
  in 14.2.5). Example 2 (p. 444) prints 230/(1.2 x 0.9) = 212 kips
  (212.96).
- ch 18: Figure 18-2, the inspector's tools checklist (p. 452), is
  captioned "Key components of the pile installation process", close to
  Figure 18-1's. The Eq. 18-1 symbol list prints "blow per minute"; 18.7.4
  item m opens with "...."; p. 494 prints "Double hydraulic hammers" for
  double acting hydraulic hammers.

Smaller typos are not listed.

## GEC-13 written from the print

GEC-13 (FHWA-NHI-16-027 and -028, 2017) was reworked on fix/ref52, one commit per
chapter. Ch 1 (17 -> 77 sections) and ch 2 (9 -> 80) were rewritten from
the print: the June 2026 files were not the chapters' text (see below).
In ch 4, 6, 8, 9 and 10 the headings REF-25 had folded into their parents
became their own sections, written from their printed pages: ch 4 22,
ch 6 2, ch 8 78 (105 -> 183), ch 9 71 (168 -> 239), ch 10 29 (103 ->
132). Ch 3 and 5 had no gaps. Each equation, figure and table sits in the
section whose pages print it. Equations re-read off rendered pages, symbol
by symbol: Eqs. 2-1 to 2-3 (new), 8-2 to 8-6 (unchanged). Figure 8-22
takes its printed caption ("used in Swedish grouting practice"; it read
"national").

`check_section_numbers.py gec_13` now reads 1,136 printed, 1,097 matched
(it was 771), 0 range and 39 missing. The 39 are outline lines (Checker
quirks). The 5 misnumbered and 5 extra rows are print numbering slips,
held:
- ch 4: two headings printed 2.6.1.4 (Predicted and Actual Densification
  Procedure, pp. 4-55/56); the first is 4.2.6.1.4.a.
- ch 9: two printed 5.1.3.1 (Geotechnical and Environmental
  Considerations, p. 9-74); Geotechnical is 9.5.1.3.1.a. 'Potential
  Disadvantages' printed 8.2.1.2 under 8.1.2 (p. 9-114) is 9.8.1.2.2;
  'Advantages' printed 9.2.1.1 under 9.1.2 (p. 9-130) is 9.9.1.2.1.
- ch 10: 'Advantages' and 'Potential Disadvantages' printed 2.1.2.1 and
  2.1.2.2 under 2.2.1 (p. 10-8) are 10.2.2.1.1 and 10.2.2.1.2;
  'Geotechnical', 'Environmental Considerations' and 'Site Conditions'
  printed 2.1.3.1 to 2.1.3.3 under 2.2.2 (p. 10-9) are 10.2.2.2.1 to
  10.2.2.2.3 (split out on fix/ref52-gec13; they were folded into their
  parents). 'Potential Disadvantages' printed 2.1.2.2 under 4.1.2 (p.
  10-45) is 10.4.1.2.2.

tests/test_query_expansion.py: the "wick drain smear zone" case pinned
2.4.3, the old file's "Smear Zone Effects"; printed 4.3 is Preliminary
Spacing Design. It now expects 2.3.2.1 (printed 3.2.1, where the print
discusses the smear zone), returned by the same, unchanged query.
scripts/retrieval_gold.json follows: pvd-smear names 2.3.2.1 and pvd-spacing
names 2.4.2 Design Procedure and 2.4.3 Preliminary Spacing Design.

### Values the old files gave that the chapter does not print

- ch 1: unit costs per cubic or linear meter (preloading $2-8/m3, PVDs
  $3-6/m, deep mixing $60-150/m3 and others) and "savings of 25-50%
  against deep foundations" (Table 1-6 gives November 2016 costs in $/lft,
  $/yd2, $/yd3 and $/ft2); a 12-step list in another order (Table 1-7);
  DDC limited to about 10 m, vibro-compaction fines below 12-15 %, stone
  columns to 15-20 m (Table 1-2 gives DDC fines < 15 %, vibro < 15 % silt
  and/or < 2 % clay, no depths); references the chapter does not list.
- ch 2: SI values throughout (cv, spacings 1.0-2.5 m, mandrel 60 x 120
  mm, blanket 0.5-1.0 m) where the print gives U.S. units (spacings 3-5 ft
  in clays, blanket at least 1 ft, typically 1.5-3 ft); sand drains
  patented by Moran in 1925 and first used in California in 1934 (print:
  patent 1926, California tests from 1933); eight equations (combined
  U = 1-(1-Uv)(1-Ur), Hansbo smear and well resistance, smear ratio 2-5,
  kh/ks 2-10) where the print has three; de = 1.128S / 1.050S (print
  1.13 / 1.05); case histories the chapter does not hold.

### Print inconsistencies, kept as printed

No reading was chosen. Page numbers are printed page numbers.
- ch 1: Table 1-9's constructability row gives weighted rating 3 for
  WF 3 x RR 2; Geotech B's weighted ratings sum to 68 against the printed
  total 69. Step 12 (p. 1-48) takes WF "from Table 1-7" (the weight
  factors are Table 1-8). Table 1-4 cites "Gransberg and Loukakis 2012"
  against "Loulakis" in the text and references. Table 1-9 gives relative
  ratings of 0 although Step 11 rates 1 to 4.
- ch 2: "Considerations for Using Equation 2.1" (p. 2-35) calls Fs a
  "sample disturbance factor" where Eq. 2-1 names it the soil disturbance
  (smear) factor. Council Bluffs (p. 2-53): 438,077 lf installed against
  690,750 estimated is "slightly less", and results are "well within the
  design time of 6 months" where the design gave 3 to 5 months.
  "Fellenious and Altace 1999" against "Altaee" in the list. Section 1.1
  cites "Section 2.4 Limitations" (printed 2.4 is id 2.2.4).
- ch 4: the mine spoil case cites Figure 4-25 for the SPT comparison,
  4-26 for induced settlement and "Figure 24" for crater depths; the
  captions are 4-24, 4-25 and 4-26. Table 4-3 Zone 2 gives "250 to 350
  kJ/m3 (5,200 to 7,200 ft-lbf/ft2)". Landfill case: "(20%)(3 m) = 0.6 m
  (1 feet)" (p. 4-62); "7 drops per phase" (p. 4-63) against "seven drops
  at each drop point location" (p. 4-62).
- ch 8: Landry et al. ranges printed "0.04 <= k <= 4 x 10-4" (falling
  bounds). "Case History 3: Apache Trail" is set under 2.4.5.2 with no
  number. Table 8-4 gives SVIF in m/s; Eq. 8-5 gives a percent. The bulk
  void filling intro (p. 8-53) says the third and fourth case histories
  describe "bituminous grout and cemented paste for mine backfill"
  (bitumen is the second; neither uses cemented paste). Slabjacking grout
  strength "in excess of 480 Pa" (p. 8-61); Case History 1 cites "Figure
  8-36" for the injection system (p. 8-63). Rock fissure grouting: NR
  "nearer 3 than 5" while the list gives NR > 5 consistently possible and
  NR < 2 not possible (p. 8-78); the Lugeon "is defined as the
  permeability of grout in the rock mass and is equal to 0.11 inch2/psi"
  (p. 8-78); grout curtains "$25 and $80 per sq. feet" (p. 8-79) against
  "$25 to $80 per square yard" (p. 8-85). Figures 8-14/8-15 credit "Bruce
  and Chauqui 2012" against the heading's "Chuaqui".
- ch 9: geotextile durability life "should be well in excess of 1000 yrs"
  (p. 9-48). Fly ash "must meet ... ASTM C593 for Class C fly ash" (p.
  9-92). A lime slurry of "1 ton of lime mixed with 500 gallons of water to
  produce 600 tons of slurry" (p. 9-88).
- ch 10: soil nailing lists "Weathered rock with adverse weakness planes"
  as well suited and "with unfavorable weakness planes" as unfavorable,
  and "Glacial till" in both lists (pp. 10-62/63).

## GEC-9 written from the print

GEC-9 (FHWA-HIF-18-031, April 2018) was rewritten from the print on
fix/ref52, one commit per chapter (ch 1 to 13). The June 2026 files held
59 condensed sections. Every printed heading now has its own section,
with its body read off its printed pages, 187 in all (ch 6 34, ch 11 30,
ch 12 23, ch 7 18, ch 13 16, ch 10 14). Each equation, figure and table
sits in the section whose pages print it. A figure printed after a
section's text, before the next heading, stays with that section.
Equations were read off rendered pages, symbol by symbol: ch 6 now holds
Eqs. 6-1 to 6-22 (the old file had 9 unnumbered ones) and ch 11 holds
Eqs. 11-1 to 11-61 (the old file had 13). Captions come from the List of
Figures and List of Tables (pp. vii-xi), which match the body captions.

`check_section_numbers.py gec_9` now reads 187 printed and 187 matched,
with 0 missing (it was 62 with a section of their own and 125 missing).
Old 3.4 was dropped because the print has no 3.4; its text is printed as
3.3.4 and 3.3.5. No retrieval eval case moved: test_query_expansion
passed after every chapter, and so did the gec_9 cases elsewhere in the
suite.

### What the old files held that the print does not

- Figure captions that are not the print's. Ch 12 held six captions;
  12-1 to 12-5 were wrong and 12-6 was right. For example, old "Figure
  12-2: Strain gauge pair placement" is printed as "Example of a one-way
  lateral load test set up on a deep foundation".
- Duplicated figures. Ch 6 listed Figure 6-6 twice, once captioned "Pile
  group interaction in SWM model". Old 10.4 listed Figure 2-11 again; it
  is now in ch 2 only.
- Titles with added words: 7.2 (": Group Efficiency and P-Multipliers"),
  8.3 ("Seismic Design"; printed "Seismic") and 10.3 ("Using the Liang
  and Zeng Method"; printed "Drilled Shaft Analysis").
- Eq. 11-34 was written as Pn = P0 0.658^(P0/Pe). The print sets P0/Pe on
  the line after 0.658, not raised (see below).
- The old ch 6 depth-to-zero-shear formula for cohesionless soil used
  gamma. Eq. 6-16 prints gamma'.

### Print inconsistencies, kept as printed

No reading was chosen. Page numbers are printed page numbers (PDF page
minus 4).
- ch 3: pp. 33 and 34 cite "Table 3-2" for the recommendations that
  Table 3-3 gives.
- ch 4: p. 40 says "substituted into Equation 4-1", but no Equation 4-1
  is printed.
- ch 5: p. 61 ("Section 5.3.1") and p. 62 ("Sections 5.3.1, 5.3.2, and
  5.3.3") point to the roles printed as 5.2.1 to 5.2.3.
- ch 6:
  - p. 64 prints "see Error! Reference source not found."
  - The same paper is "Davisson and Robinson 1985" on p. 93 and 1965
    elsewhere.
  - Eq. 6-13 prints gamma z, while the text calls the term the vertical
    effective stress (gamma'z).
  - Eq. 6-15 is printed as Pt = gamma' Bb Lmin^2 Kp/(2 Lmin) - Mt/Lmin.
    Its first term is a force per length; Mt/Lmin is a force.
- ch 7:
  - The same paper is "Mokwa and Duncan (2001)" on p. 106 and "Duncan
    and Mokwa (2001)" on p. 112.
  - The batter wording disagrees. P. 114 says a modifying constant of 0
    to 1 (head toward the load) "reduces the p value, which reduces the
    deflection". P. 115 has "outwardly battered piles (pile head inclined
    toward the load)", while pp. 113 and 114 call outward batter "away
    from the load".
  - The list in 7.4.2 is printed numbered 7 to 9 (p. 110).
- ch 8:
  - The Extreme Event lateral resistance factor is 0.80 on p. 116 and
    1.0 on pp. 117 and 122.
  - P. 118 reads "For periods less than or equal to, the elastic"; T0 is
    missing.
  - Abutments and piers are "located 30 feet from the edge of roadway"
    (p. 123).
- ch 9: the last value of Table 9-1 is printed ".25" (p. 129).
- ch 10:
  - On p. 132, an unnumbered heading "Initial Geotechnical Resistance
    Assessment" runs into the next sentence.
  - P. 133 says "As the program is based upon a 2-dimensional finite
    element method (FEM) model" without naming a program.
  - The Eq. 10-1 legend has "Ci'Ii" and "PiIi = Interslice force", and
    the equation prints C'_I (p. 135).
  - P. 141 cites "Chapter 6 of this report" for micropile slope design.
- ch 11:
  - No Equation 11-58 is printed; 11-57 is followed by 11-59.
  - Eq. 11-34 prints "Pn = P0 0.658 P0/Pe" with the fraction on the line.
  - Eq. 11-48 has no condition printed; only Eq. 11-47 carries "If
    Pu/Pr < 0.2".
  - P. 145 cites "Table 11-2" for nh, but Table 11-2 gives casing yield
    strengths.
  - The depth-to-fixity paragraph is printed twice (pp. 145 and 146).
  - The toe is "fixed for both translation and rotation (pinned)" (p. 144).
  - The concrete failure strain is "approximately up to approximately
    0.0038" (p. 144).
  - The compression-controlled strain limit is printed as 0.003 (p. 154).
  - The units of Est, Ep and ecu are printed as "(in2)" (pp. 155 to 157).
  - The legends cite "AASHTO (2014) Section 8.5.2.3" and "Table 8-6"
    (p. 156).
  - P. 166 names Equations 11-37 and 11-39 for the compact and
    noncompact Mn cases, which Eqs. 11-40 and 11-42 print.
  - The text gives 235 MPa for Figure 11-10, and the figure's note says
    234 MPa (pp. 171 and 172).
  - The Eq. 11-61 legend gives "Et" for the modulus of steel (p. 174).
- ch 12:
  - The cross-references point to the wrong sections. P. 181 has
    "external instrumentation (see Section 12.6)"; instrumentation is
    12.3. P. 187 has bending moments "see Section 12.7"; data analysis
    is 12.4.
  - Eqs. 12-1, 12-2 and 12-4 print the curvature as the glyph "Ø"; the
    text uses phi.
  - Procedure A "consists of 1) load increments ..." has no 2) (p. 184).
  - The shape arrays are "Shape accelerator arrays (SAAs)" on p. 187 and
    "Shape Array Accelerometers (SAA)" on p. 189.
  - Piecewise fitting gives p "at the group center point" (p. 192).
- ch 13: the pre-bored hole is limited to "not more than 6 inches than
  the largest dimension of the pile" (p. 201).

Smaller typos are not listed.

## GEC-4 written from the print

GEC-4 (FHWA-IF-99-015, June 1999) was rewritten from the print on
fix/ref52, one commit per chapter (ch 1 to 9). The June 2026 files held
21 sections, 12 of them ranges such as 5.9-5.11 and 9.1-9.5. Every
printed heading now has its own section, with its body read off its
printed pages, 241 in all (ch 5 83, ch 7 32, ch 9 30, ch 2 27, ch 6 22,
ch 4 17, ch 8 14, ch 3 13, ch 1 3). Each equation, figure and table sits
in the section whose pages print it. A figure printed after a section's
text, before the next heading, stays with that section; one printed
inside a later section's text goes there (Figure 40 in 5.5.2.1, Figure
63 in 6.4.3). GEC-4 numbers figures, tables and equations straight
through the document, not by chapter: Figures 1 to 73, Tables 1 to 23
and Equations 1 to 49 (Equation 10 is printed as 10a and 10b). Equations
were read off rendered pages, symbol by symbol: ch 4 holds Eqs. 1 to 8,
ch 5 Eqs. 9 to 48 and ch 7 Eq. 49. Captions come from the List of
Figures and List of Tables (pp. xiii-xix); the body caption of Figure 4
is longer (it adds the Littlejohn paper title and the ASCE permission).

`check_section_numbers.py gec_4` now reads 234 printed, 233 matched, 0
ranges and 1 missing (it was 8 matched and 141 missing). The one
missing, "9.9", is a misread of the caption "Figure A-4" (p. A-12) in
appendix A, which has no text file. The 8 extras are printed headings
the checker does not list: 3.5 (p. 24), and seven ch 5 headings printed
with no space after the number ("5.2.10.1Uniform"): 5.2.10.1, 5.2.10.2,
5.10.2.1 to 5.10.2.3, 5.10.3.1 and 5.10.3.2. No retrieval eval case
moved: test_query_expansion and the gec_4 cases passed after every
chapter, and test_every_section_resolves_in_the_db_within_the_app_cap
passed at the end.

### What the old files held that the print does not

- Equation ids that are not the print's. Ch 4's were "4-1" to "4-8" and
  Eqs. 4 and 5 were missing; ch 5 held seven equations with ids "5-9" to
  "5-38". The print numbers them 1 to 49 through the document.
- Grouped or misfiled objects: "Figures 18-22" and "Figures 38-39" as
  single entries, and Table 3 listed among the figures in ch 4.
- Captions not the print's: Tables 6 and 8 in ch 5, and six figures in
  ch 7. For example, old "Extended creep test data plot" for Figure 72
  is printed "Plotting of extended creep test data (after PTI, 1996)".
- Missing sections: 6.5, 7.5 (lock-off load), 7.6 (lift-off testing),
  8.5 and 9.6 (short-term and long-term monitoring) were not in the old
  files at all.

### Print inconsistencies, kept as printed

No reading was chosen. Page numbers are printed page numbers (PDF page
minus 21).
- ch 2: p. 16 says the advantages of anchored walls "have been described
  in section 1.2"; they are listed in 1.3.
- ch 3: the Table 1 bands leave gaps: dense 25-50 then very dense
  "> 51", and hard 31-60 then very hard ">61" (p. 24).
- ch 4:
  - P. 36 ties both the maximum (passive) and the minimum (active)
    horizontal stress to "outward movement of the wall".
  - The heading is printed "4.2.4." with a trailing period (p. 32).
- ch 5:
  - P. 106 says "B' cannot exceed B sqrt(2)", while Eq. 35 prints
    Su sqrt(2)/B in the denominator.
  - Table 9 (p. 77): the 2-1/2 in. Grade 150 row prints 0.8, 0.7 and
    0.6 fpu Aps as 622.4, 435.7 and 466.8 kips.
  - Eq. 45 (p. 114) prints the D' bracket as "1 +", the same sign as
    Eq. 43.
  - Eq. 47 (p. 117) prints the numerator as "tan(tan a + cot b)".
  - Eq. 13 (p. 58) prints the term "(2 - x) sqrt(2) d", with x in m.
  - Table 12 (p. 82) prints the soil symbols "GS" and "SM-SL".
- ch 7:
  - P. 152 says anchors passing the enhanced creep test "may be locked
    off at the design test load"; Figure 73 says "lock-off at design
    lock-off load".
  - The reduced lock-off is "50 percent of the load that the anchor
    holds without detectable movement" and "no greater than 50 percent
    of the maximum load attained during testing" in the text (p. 152),
    and "50% of the maximum acceptable test load" in Figure 73 (p. 153).
  - Table 21 step 9 prints "delta_tn - delta_r6 = delta_e6" (p. 144).

Smaller typos are not listed.

## GEC-5 written from the print

GEC-5 (FHWA-NHI-16-072, November 2016) was rewritten from the print on
fix/ref52, one commit per chapter (ch 1 to 13). The June 2026 files held
30 sections, 28 of them ranges such as 9.1-9.4 and 10.9-10.15. Every
printed heading now has its own section, with its body read off its
printed pages, 390 in all (ch 10 58, ch 5 56, ch 4 47, ch 7 40, ch 6 32,
ch 11 32, ch 9 28, ch 3 24, ch 8 24, ch 12 19, ch 2 15, ch 13 11, ch 1
4). Each equation, figure and table sits in the section whose pages
print it. A figure printed after a section's text, before the next
heading, stays with that section; Figures 13-5 to 13-8, cited in 13.5.3,
print in 13.5.4. GEC-5 numbers equations with a point (Eq. 4.26) and
figures and tables with a hyphen (Figure 4-17), and the files keep that.
Equations were read off rendered pages, symbol by symbol, 227 in all:
Eq. 3.1, Eqs. 4.1 to 4.32, 5.1 to 5.14, 6.1 to 6.24 (with 6.9a to 6.9c),
7.1 to 7.28, 8.1 to 8.23, 9.1 to 9.34, 10.1 to 10.38 and 11.1 to 11.31.
Chapters 1, 2, 12 and 13 print none. Table values were read off the
pages, rendered where the text layer loses symbols (Table 12-5 is an
image). The Lists of Figures and Tables (pp. xv-xl) print captions in
capitals and often differ from the body captions; the files use the body
captions. Eight body captions the automatic match missed were read by
hand: Tables 5-15, 8-13 and 10-11 and Figures 9-17, 9-22, 11-2, 11-12
and 11-26. The List of Tables' text layer also loses the Table 10-11
entry.

`check_section_numbers.py gec_5` now reads 390 printed and 390 matched,
with 0 ranges and 0 missing (it was 2 matched, 28 ranges and 91
missing). 35 printed headings were in no old range at all: 3.10 to 3.13,
4.11 to 4.14, 6.13 and 6.14 with their subsections, 8.10 to 8.10.2,
10.4 to 10.8.2 (groundwater observation in borings, wells, piezometers,
CPTU and geophysics), 11.6 (outliers) and 11.7 (observational method).

Four retrieval gold entries named old ranges and now name the printed
sections (as in df580ff): cu-def 4.1-4.10 to 4.4.1, plasticity-chart
4.16-4.17 to 4.16.1, liq-screen 5.5-5.7 to 5.6.1 and 5.6.2, and
hoek-brown 9.5-9.8 to 9.8 (Eq. 9.29, p. 9-50). No query was reworded.
py-method also accepts gec_5 8.10.2 "p-y Curves" (p. 8-30), new here:
it defines p-y curves for laterally loaded deep foundations, and Table
8-13 (p. 8-31) lists the p-y models by soil. Ranks moved as follows
(rerank, unless a mode is named):
- cu-def 2 to 1 and plasticity-chart 3 to 2, in all modes; hoek-brown
  stays 1.
- liq-screen 1 to not in the top 10, in all modes. The top hits are
  gec_10 9.4.2.1 and gec_5 12.4.2 (seismic liquefaction screening, with
  Table 12-5); neither prints a fines limit. 5.6.1, which prints "less
  than about 20 percent fines" (p. 5-31), is not in the top 50, and
  5.6.2 ranks 16: the print says "liquefiable" and "liquefy", where the
  old range summary held the query's words (REF-54).
- py-method 9 to 1, in all modes (gec_5 8.10.2 first; gec_9 6.3 went
  from 9 to 11).
- rqd-def 1 to 2 (fill and rerank); dmt-def 4 to 7 (auto 5 to 7; gec_5
  10.14.3 and 10.14 rank above); stone-col-capacity 7 to 5; spt-def 3 to
  4 (off and fill); phi-cpt 6 to 7 (auto and rerank).

Rerank R@10 went from 41 to 40 of 54 and MRR@10 from 0.510 to 0.509
(off 34 to 33, fill 39 to 38, auto 44 to 43); the case lost is
liq-screen. test_query_expansion and the gec_5 cases passed after every
chapter.

### What the old files held that the print does not

- Equation ids that are not the print's. The old files held 25
  equations for the 227 printed. Their ids were descriptive ("4-Cu",
  "4-RQD", "6-cv", "7-MC", "7-SHANSEP", "7-Su-CPT", "8-Gmax",
  "9-Brazilian", "9-Hoek-Diederichs", "9-HB", "10-head", "10-Darcy",
  "10-Hazen", "11-sigma-total", "11-sigvo") or hyphenated numbers ("3-1",
  "4-12", "5-2", "8-7") where the print uses a point.
- 9-Hoek-Diederichs held the constant 0.02 where Eq. 9.28 prints 0.2
  (see below).
- Captions not the print's. Old Figure 7-15 carried Figure 7-12's
  caption ("Total stress strength envelopes for saturated soils"); the
  print's 7-15 is "Stress-induced anisotropy for undrained shear strength
  of normally consolidated clays (Ladd, 1991)". Old Table 9-6 "RMR
  system: class descriptions and engineering properties" is printed "RMR
  System parameter R6 (from ASTM D5878, 2008)". Old Figure 12-13
  "Borehole tomography" is printed "Changes in surface wave motions due
  to subsurface voids"; tomography is Figure 12-14.
- A merged entry, "Table 8-7 and 8-8".
- Tables 10-3 and 10-4 sat in 10.1-10.3; they print in 10.9 and 10.10.7.

### Print inconsistencies, kept as printed

No reading was chosen. Page numbers are printed page numbers
(chapter-page; PDF page 49 is p. 1-1).
- ch 3: the deep foundations row of Table 3-2 asks for "at least one
  exploration point per embankment" (p. 3-36).
- ch 4:
  - Table 4-2 gives the No. 40 sieve as 0.0425 mm (medium sand 0.0425
    to 2.00 mm, fine sand 0.075 to 0.0425 mm). P. 4-3 gives the No. 200
    opening as 0.074 mm, while Table 4-2 and 4.4.2 use 0.075 mm.
  - The inch and mm columns of Table 4-23 disagree: 0.02-0.8 in.
    (0.425-2 mm), 0.8-2 in. (2-4.75 mm), 2 in. (> 4.75 mm).
  - The Begemann (1965) bands overlap: Rf < 2.5 % sand, > 3.5 % clay, 2
    to 4 % mixed (p. 4-30).
  - Eqs. 4.31 (ID = 10^(1.67 - 0.67 Ic-RW)) and 4.32 (Ic-RW = 2.5 - 1.5
    log ID) are called equivalent (p. 4-36); inverting 4.31 gives 2.49
    and 1.49.
  - In Table 4-13 the A-7 "11 min" for PI carries a footnote mark with
    no footnote.
  - The 4.8.1 to 4.8.3 headings read "Liquid Limit", "Plastic Limit" and
    "Shrinkage Limit" in the body and "Determining the ..." in the Table
    of Contents (the files use the Table of Contents).
- ch 5:
  - Table 5-15 scores pH 2 to 4.5 as 6, 5 to 6 as 0, 7 to 9 as 6 and
    10.5 to 12 as 2, which leaves gaps (4.5-5, 6-7, 9-10.5). Its maximum
    total is 21, while Table 5-16 stops at 20 (p. 5-43).
  - Table 5-12 gives IJ "= 6", "3 to 5" and "< 2", which leaves IJ = 2
    unassigned.
  - Figure 5-7 credits "Van der Mere, 1964" (p. 5-15); the text has "Van
    der Merwe (1964)" (p. 5-14).
- ch 6:
  - Figure 6-4 credits "Bozozuk, 1971"; the text says Bozozuk (1970).
  - The first row of Table 6-1 prints "1" for the volumetric strain; the
    next row is 1-2.
  - 6.6.2 sends the stress-history terms to Table 6-2; they are in Table
    6-3 (p. 6-16).
  - Eq. 6.23 prints (25)(7.5 mm)^2/t50 = 14.06 mm^2/t50 (p. 6-42); 25 x
    56.25 mm^2 is 1406 mm^2.
  - Table 6-6 prints the Larsson and Eskilson relation as OCR = 10(0.16KD
    - 2.5).
  - 6.14.3 gives Calpha/Cc for peats as 0.06 +/- 0.01 (p. 6-47); 5.4.5
    gives 0.075 +/- 0.01 (p. 5-27).
  - Figure 6-36 labels its lines Cc = PI/74 and Cur = PI/370; its
    regression header gives PI/73 and PI/385, and Table 6-15 has PI/73.
  - 6.8 prints pa = 100 kPa = 14.7 psi (p. 6-19).
- ch 7:
  - Eq. 7.1 prints s = c' + tan phi' (p. 7-2) and Eq. 7.4 sT = c + tan
    phi (p. 7-13), with no normal stress.
  - 7.2.1 says d and tan psi are "as shown in Table 7-4"; they are in
    Table 7-1 (p. 7-4).
  - Table 7-1 has two rows named "p-q diagram". Its (sigma1 - sigma3)
    vs. sigma'3 and sigma'1 vs. sigma'3 rows list the abscissa as (sigma1
    - sigma3) or sigma'1 and the ordinate as sigma'3, while Figure 7-4
    plots sigma'3 on the abscissa (p. 7-5).
  - Table 7-4 repeats Table 7-3's caption ("Estimates for normalized
    undrained strength parameters, S and m"); it lists levels of
    investigation.
  - 7.6.9 computes sigma'N "as (cos^2 phi')/(1 - sin phi')", with no
    stress (p. 7-57).
- ch 8:
  - 8.3 has no title in the Table of Contents; the body prints "Boring
    and Sampling Requirements for Measurement of Stress-Strain and
    Stiffness Properties".
  - The Sections column of Table 8-1 cites 6.8, 6.9, 8.8.1 to 8.8.4,
    8.9, 8.10 and 8.6 to 8.7; the printed headings put those subjects at
    6.7, 6.8, 8.9.1 to 8.9.4, 8.10.1, 8.10.2 and 8.7 to 8.8 (pp. 8-1 to
    8-2).
  - Eq. 8.11 prints F(e) = e^1.3 (Bellotti et al., 1996), which rises
    with e, while Eqs. 8.8 to 8.10 fall with e (p. 8-16).
  - 8.9.2 gives nu of about 0.1 to 0.2 for drained coarse soils (p.
    8-26); Table 8-10 gives 0.25 for fine sand and 0.2-0.36 and 0.3-0.4
    for sand and gravel.
- ch 9:
  - Eq. 9.28 prints EM = ER (0.2 + ...) (p. 9-48). The curves of Figure
    9-34 start near 0.02 at low GSI and reach about 1.0 at GSI 100.
  - 9.5.5 sends the JRC shear strength to "Equation 9.20" (p. 9-31);
    Barton's relation is Eq. 9.17, and 9.20 is the dilatometer Gd.
  - 9.7.1 cites "Equation 9.26" twice for the borehole jack modulus (pp.
    9-42 to 9-43); the jack relation is Eq. 9.23.
  - 9.7.4 gives the isotropy condition "for use of Equations 9.30 and
    9.31" (p. 9-50); the GSI modulus relations are Eqs. 9.27 and 9.28.
  - 9.8 says "Equation 9.32 can be used directly for design" (p. 9-53);
    Eq. 9.32 defines a, and the criterion is Eq. 9.29.
  - 9.6.1 calls the Q-system "a.k.a. the CSIR system" (p. 9-33).
- ch 10:
  - Eq. 10.8 prints k = cv Delta_w mv with "Delta_w is the density of
    water" (p. 10-30); Eq. 10.28 uses gamma_w, the unit weight.
  - Eq. 10.27 prints k = q Wf/(A H Wf (0.5 Pa)), with Wf above and below
    the line, and "Pa ... equal to Pg x G x Wf" with Pg not defined (pp.
    10-51 to 10-52).
  - The slot 20 and slot 30 rows of Table 10-1 are the same except for
    the screen size (p. 10-10).
  - Eq. 10.10 calls Q the "volume of water added" (p. 10-37); k = Q/(5.5
    r H) needs a flow rate.
  - Figure 10-40 credits Leroueil et al. 1983 in the List of Figures and
    1990 in the body.
  - "Lafluer et al., 1987" and "Lafleur et al., 1987" are both printed
    on p. 10-45.
- ch 11:
  - Eq. 11.25 prints sigma_y = sigma_d^2 sigma_s^2/(sigma_d^2 +
    sigma_s^2) (p. 11-30). The combined values of Table 11-4 equal the
    square root of that expression (94 and 223 give 87; 366 and 382 give
    265).
  - 11.9.2 has S = 0.25 and m = 0.77 "determined from CUIC tests" (p.
    11-44); Figure 11-21's caption says CIUC.
  - The List of Figures gives pages one later than the captions for
    Figures 11-16 to 11-26 (Figure 11-16 is listed on 11-36 and printed
    on 11-35).
- ch 12:
  - Figure 12-6 is captioned "Stress distribution beneath a square
    foundation"; the text describes "a circular loaded area" (p. 12-7).
  - The seismic refraction paragraph is headed "Surface Refraction:" (p.
    12-10).
  - Figure 12-24 is "Landslide event affecting highway (Courtesy of
    USGS/Photo by D. Krammer)" in the body (p. 12-28), "LANDSLIDE EVENT
    AFFECTING HIGHWAY 3 IN TAIWAN (PETLEY, 2010)" in the List of
    Figures, and "The massive slope failure in Idaho along a highway" in
    the text (p. 12-27).

Smaller typos are not listed.

## GEC-8 written from the print

GEC-8 (FHWA-HIF-07-03, April 2007) was rewritten from the print on
fix/ref52, one commit per chapter (ch 1 to 8). The June 2026 files held
25 sections, 6 of them ranges such as 5.2-5.3 and 7.5-7.6. Every printed
heading now has its own section, with its body read off its printed
pages, 186 in all (ch 5 44, ch 8 42, ch 7 32, ch 4 22, ch 6 18, ch 3 14,
ch 2 10, ch 1 4). Each equation, figure and table sits in the section
whose pages print it. GEC-8 numbers equations, figures and tables with a
point (Eq. 5.5, Figure 5.1, Table 5.1), and the files keep that.

The accessible PDF lays alt text over every equation and figure, so a
plain text read returns sentences such as "f sub s equals alpha times S
sub U" and loses the equation tags and many captions. The text was read
with the alt text ignored. Equations were read off rendered pages,
symbol by symbol, 72 in all: Eqs. 5.1 to 5.64 (71 tags with the a and b
variants) and Eq. 6.1. The other chapters print none. Tables 5.1 to 5.4,
6.1, 6.2 and 7.1 carry their contents. The 115 figures carry the body
captions; twelve that the automatic match missed or cut short were set
by hand: Figures 2.5, 2.11, 2.12, 3.3, 3.6, 4.6, 4.9, 5.2, 5.4, 6.5, 6.6
and 7.13.

`check_section_numbers.py gec_8` now reads 184 printed and 184 matched,
with 0 ranges and 0 missing (it was 19 matched, 6 ranges and 148
missing). Two more printed headings have their own sections and show as
extra: 7.3.4 Pile Installation Plan (p. 165) and 8.1.8 Construction
Submittals (p. 201). On those two pages the text layer stores the first
letters of each line apart from the rest, so the checker loses the
numbers; the Table of Contents lists 186. 30 printed headings were in no
old section at all: 2.3 (summary), 3.1, 4.1 and 7.1 (introductions), 5.4
to 5.4.3 (static axial capacity of drilled displacement piles), 5.8 to
5.8.2 (single-pile examples), 6.6 to 6.6.6 (the design example), 7.7 to
7.7.6 (QC/QA checklists), 8.2 (materials), 8.4 (measurement) and 8.5
(payment).

One retrieval gold entry named an old range and now names the printed
sections (as in df580ff): cfa-piles 5.2-5.3 to 5.2 and 5.3, beside dm7_2
6-4.3. auger-cast's gold, gec_8 3.2, is now a heading with no text of
its own, so the gold also accepts the sections that print its advantages
and limitations: 3.2.1 (p. 15), 3.2.2.1 (p. 16), 3.2.2.2 (p. 17) and
3.2.3 (p. 20). No query was reworded. Ranks moved as follows from refs
main before GEC-8 (39f779f, with the GEC-5 review fixes) to after ch 8
(rerank, unless a mode is named):
- cfa-piles 3 to 2 (off and fill 3 to 1, auto 4 to 1).
- neutral-plane 2 to 1; nsf-def 2 to 1.
- auger-cast 3 to 4, scored by dm7_2 6-4.3. GEC-8's own text left the
  top 10: the best of 3.2.1 to 3.2.3 is 3.2.2.1 at 14. Their text says
  "favorable" and "unfavorable", where the old 3.2 text also said
  "advantages" and "limitations" (REF-54).
- stone-col-capacity 5 to 7. The gold is gec_13 5.4.1.2.5; the top 8 are
  all gec_13 and dm7_2 sections, in a new order.
- py-method stays 1 (gec_5 8.10.2).

Rerank R@10 stays 40 of 54 and MRR@10 went from 0.509 to 0.528; R@3 went
from 33 to 32 and R@5 from 36 to 35 (off, fill and auto R@10 unchanged
at 33, 38 and 43). test_query_expansion and the gec_8 tests passed after
every chapter.

### What the old files held that the print does not

- Equation ids that are not the print's. The old files held 12
  equations for the 72 printed, with hyphenated ids ("5-1", "5-2",
  "5-20a") or descriptive ones ("5-DD-1", "5-group-eff",
  "5-elastic-comp", "6-ASD").
- Captions not the print's. Old Figure 2.3 "CFA piles in group with pile
  cap form" is printed "Schematic of Typical Drilled Shaft vs. CFA
  Foundation". Old Figure 3.11 "Subsurface profile at Krenek Road Bridge
  site" is printed as a photograph, "CFA Piles at the Krenek Road Bridge
  Site". Old Figures 5.17, 5.21 and 5.22 carried the captions of 5.14,
  5.19 and 5.20. Several others were paraphrased.
- Old Figure 2.6 sat in 2.1; it prints in 2.2.1.

### Print inconsistencies, kept as printed

No reading was chosen. Page numbers are printed page numbers (PDF page
24 is p. 1).
- ch 2: 2.2.2.1 lifts the auger "typically 150 to 300 mm (6 to 12 in.)"
  to release the plug; 2.2.2.2 says the lift "must be limited to 150 mm
  (6 in.)" (p. 9).
- ch 3:
  - 3.5 prints "$40 to $60 per linear meter ($12 to $20 per linear
    foot)" (p. 31); $20 per foot is about $66 per meter.
  - 3.2.3 gives secant walls up to 10 m (33 ft) high with piles under
    1.2 m (4 ft) (p. 21); 3.4.3 gives diameters of about 1 m (40 in.)
    and heights of about 12 m (40 ft) or less (p. 29).
- ch 4:
  - 4.3.1 sends fluidifiers to "Section 4.3.6" (p. 54); there is no
    4.3.6 (they are in 4.3.1.5).
  - 4.3.1.2 says fly ash, silica fume or slag "will probably severely
    retard" early strength, to about 10 to 14 days (p. 55; 8.3.2 repeats
    it, p. 207); 2.2.2.4 says they "tend to slightly retard" it (p. 12).
- ch 5:
  - Eq. 5.31 prints qp (MPa or tsf) = 0.19 N60 + WT (p. 84); the p. 84
    comparison and the 5.8.2 example use 1.9 N60 tsf.
  - Eq. 5.34 prints R_Block = 2 fs [D Z + B] + qp (Z B) (p. 92), adding
    an area to a length inside the bracket.
  - Eqs. 5.42 and 5.43 print p and e with a subscript sigma (p. 100);
    the where-list defines eo and po.
  - 5.6.2 gives the steel modulus as "200,000 MPa (2,900 ksi)" (p. 109);
    200,000 MPa is about 29,000 ksi.
  - 5.6.2 calls the axial stress "(Px x Area)" (p. 110).
  - With no axial load Eq. 5.61a (psi) reduces to Vc = sqrt(f'c) and Eq.
    5.61b (MPa) to 0.166 sqrt(f'c) (p. 118); they differ by a factor of
    about 2.
  - 5.3.3.2 limits the Florida limestone data to "approximately 9 and 8
    MPa (94 to 84 tsf)" (p. 76); Figure 5.7's curves end near 9 and 8
    tons/ft2.
  - Figure 5.4's legend reads "Silts" and "Clays" (p. 74); the text
    gives Eqs. 5.22 and 5.23 for silty and sandy soils.
  - 5.1 puts the recommended methods in "Section 5.2" and the DD method
    in "Section 5.3" (p. 64); they are 5.3 and 5.4.
  - 5.5.2.1 cites "Section 5.5.2.1.2" (p. 93; 6.6.4 too, p. 154); there
    is no such heading. 5.5.2.2 sends R_Block to "Section 5.5.3" (pp. 94
    to 95); it is Eq. 5.34 in 5.5.2.1.
  - 5.8 cites "section 6.7.4, part A" and "Part D" (p. 125); the example
    is 6.6, with Step 3 at 6.6.4.
  - The 5.8.2 DD example takes side shear "from Equation 5.31" (p. 131)
    and end bearing "from Equation 5.33" (p. 132); the SPT relations are
    Eqs. 5.29 and 5.31.
- ch 6:
  - 6.6.4 prints the cap weight as "10 ft x 10 ft x 2.5 ft x 0.15
    kip/ft3 / 4 piles = 8 kips/pile" for a five-pile group (p. 149);
    37.5/4 is 9.4 and 37.5/5 is 7.5.
  - 6.6.4 prints "2/3 x (69 - 29 ft) = 0.67 x 40 = 56 ft, or 27 ft into
    the stiff clay" (p. 155); 0.67 x 40 is 27 ft, and 56 ft is the depth
    below the ground.
  - 6.6.5 (c) asks about soil mining in loose water-bearing sands and
    answers "Yes, if soils are cohesive." (p. 159).
- ch 7:
  - 7.3.5.2 sends the integrity test frequency to "Section 7.3.3" (p.
    169); 7.3.3 is Design Submittals, and the frequency is in 7.5.1.
  - 7.3.4 and 8.1.8.1 ask for a monitoring plan "as required in Section
    3.1" (pp. 166, 202); 3.1 is the chapter 3 introduction.
  - 7.4.4 gives "24 to 31 MPa (3,000 to 4,500 psi)" (p. 180); 24 MPa is
    about 3,500 psi.
  - 7.6.2 gives "around 5 MN, (450 tons)" (p. 189); 5 MN is about 560
    short tons.
  - 7.4.2 gives re-drilling 1.5 m (5 ft) below a pressure drop as common
    practice (p. 173); 7.7.4 calls re-drilling less than the full length
    "generally considered unacceptable" (p. 193).
- ch 8:
  - 8.1.7 sets geotechnical design by "Service Load Design (SLD)" per
    chapters 5 and 6, and structural design not covered there by SLD per
    the AASHTO Standard Specification, 17th Edition (p. 199); 6.3.1 uses
    ASD for geotechnical and LRFD for structural design (p. 136).
  - 8.1.4 and 8.3.11 name the circular "Augered Cast-in-Place and
    Continuous Flight Auger Piles" (pp. 196, 219).
  - 8.3.3 cites "Section 3.5" for soil drawn into the bore (p. 212); 3.5
    is Construction Cost Evaluation.
  - 8.2 bars "Type B fly ash" with Type II cement (p. 205); the fly ash
    line above it lists ASTM C 618 Class C or F.
  - 8.3.1.1 gives compaction "as specified by ASTM D 698 (AASHTO T 180)"
    (p. 206); D 698 is the standard effort (T 99), T 180 the modified.
  - 8.3.8 bars steel spacers, then allows steel centering guides such as
    a wire "basket" or "football" (p. 217).
  - 8.3.12 spaces access tubes at about one per 1 ft (0.3 m) of cage
    diameter (p. 221); 7.5.3 spaces them about 0.3 m (1 ft) apart around
    the cage (p. 186). 8.3.12 sets integrity tests on at least 20 % of
    production piles (p. 221); 7.5.1 calls 10 % to 20 % typical (p. 183).
  - 8.3.2.4 asks for six samples per "50 yd3 (38 m3)" (p. 211); 7.4.4
    has "40 m3 (about 50 yd3)" (p. 180).

Smaller typos are not listed.

## EN 1997-2 written from the print

EN 1997-2:2007 (the BS EN copy, with the AC1 corrigendum marked) was
rewritten from the print on fix/ref52: one commit per section (1 to 6,
with Tables 2.1 to 2.3 in a commit of their own), reviewed and merged to
refs main as 158e408 with the review fixes 74cf1b2, then one for
Annexes A to X (f153df5, with a page fix in 4fe7bc4). The text layer
is OCR ("requirenlents", "Salnpling"), so every heading, symbol,
number, equation and table value was read off rendered pages. The standard's
text is CEN copyright: bodies are paraphrased, and numbers, equations,
symbols and table values are as printed. Page numbers below are printed
page numbers (PDF page 3 is p. 1).

The June 2026 files held 88 sections. Every printed heading now has its
own section, 479 in all:
- Sections 1 to 6: 47 to 273 (s1 13, s2 22, s3 17, s4 62, s5 155, s6 4).
- Annexes: 41 to 206 (A to K 41, L to S 77, T to X 88). The three annex
  files keep their names and chapter numbers (annex_field_tests 7,
  annex_lab_tests 8, annex_rock_tests 9), so the figure catalog's
  chapter 7 still holds. Their old sections were keyed 7.1 to 7.11.4,
  8.1 to 8.8 and 9.1 to 9.5. They are now keyed as printed: the letter
  alone for an annex heading, or for a whole annex with no numbered
  clauses (A, C, H, J, O, T), and D.1, N.4.2, X.4.11.2 for the clauses.
  The audit's section-id pattern now accepts that form.

Each table and figure sits in the section whose page prints it. The
section 4 and 5 files held copies of the Annex D to W tables and figures
and the Annex N equations; those now live only in the annexes. Section 4
keeps Eqs. 4.1 to 4.5 with their links, and Table 4.1 sits in 4.4.3.
Section 5 prints no equation, table or figure. Tables 2.1 to 2.3 and 3.1
carry every cell as printed. The annexes hold 53 tables and figures (A
to K 38, L to S 13, T to X 2) and 30 equations. The annexes print their
equations without numbers, so the old ids (Annex D.2, F.3, G.1 ...) keep
their implemented_in links. Links were added for the D.3 settlement
coefficients and the F.3 Icc and fs functions. Annex X (pp. 180 to 196)
lists its documents clause by clause.

`check_section_numbers.py eurocode_7_2` now reads 370 printed and 370
matched, with 0 ranges and 0 missing. It was 259 printed, 45 matched and
214 missing. The 111 Annex L to X headings it reads now count, because
the annex files carry their letters.
- 106 sections show as extra. All are printed headings, read off their
  pages:
  - 1.7 (p. 15), 3.4.1 (p. 33), 4.10.4 (p. 57, OCR'd "4. t 0.4") and ten
    section 5 headings (5.5, 5.5.4.1, 5.5.5.1, 5.5.8, 5.5.8.2, 5.6.1.2,
    5.6.2.2, 5.6.5, 5.7.3, 5.13.5), whose OCR'd lines are damaged or
    missed;
  - the 24 annex letters A to X;
  - the 30 numbered clauses of Annexes A to K, where the checker finds
    no printed headings at all;
  - 39 numbered clauses of Annexes L to X whose OCR'd heading lines it
    misses (X.4.1.5 and X.4.8, for example).
- 3 misnumber flags are held, none applied, and all are false:
  - 5.2.1 General requirements to 5.2: p. 60 and the Table of Contents
    print 5.2.1.
  - N.5.2 to N.4.2: N.4 (p. 159) and N.5 (p. 160) each print an
    "Evaluation of test results" clause.
  - X.4.1.4 Particle density determination to X.4.1.3: both print on
    p. 186, each with its own list.
- 19 rows are ambiguous: repeated titles in sections 4 and 5
  ("Requirements", "Specific requirements"). Each says matched by page
  heading.

One retrieval gold entry named an old annex key and now names the
printed clause: dr-n160 7.6.1 to F.1. No query was reworded. No old
annex id appears in the app. The review of sections 1 to 6 (74cf1b2)
moved pmt-def's gold from 4.9, the field vane test, to 4.4 and 4.4.1,
and let cpt-def's gold accept 4.3.1. spt-def (4.6) and dmt-def (4.10)
still name section 4 headings that carry no text of their own; their
Objectives clauses are 4.6.1 and 4.10.1. They were left as they are.

Ranks moved as follows from refs main 158e408 (sections 1 to 6 merged,
with the review fixes) to after the annexes (rerank, unless a mode is
named):
- dr-n160 1 to 3 (fill 1 to 3; auto stays 1). The old key 7.6.1 was the
  whole of Annex F.1. F.1 now ranks under dm7_1 2-7.1.1 and eurocode_7_2
  4.6.4.2 (bearing resistance of spread foundations in sands).
- n160-phi 3 to 2 (fill and auto 4 to 3).
- cpt-def stays 1; off and fill 7 to 8.
- stone-col-capacity 7 to 5 and ec7-compaction 10 to 9. Neither gold is
  in EC7-2.

Rerank R@5 went from 35 to 36 of 54 and MRR@10 from 0.523 to 0.515; R@3
(32) and R@10 (40) are unchanged. test_query_expansion and the
eurocode_7_2 tests passed after every commit, and the audit ends at 0
errors.

### What the old files held that the print does not

- Annex keys that are not the print's: 7.1 to 7.11.4, 8.1 to 8.8 and 9.1
  to 9.5. "Annex G.4-G.5" (7.7.4) and "Annex I.1-I.4" (7.9.1) were
  ranges. Annexes L to X had one summary each, so their 152 numbered
  clauses had no section.
- Copies of annex objects in sections 4 and 5, among them "Table
  D.3/D.4" and "Table D.5/D.6" as single entries, and a placeholder
  "Figure F..." in 4.6.
- Figure 1.2 twice, in 1.6 and 1.7; it prints in 1.7.
- Table 2.1's key without R3 (low applicability in rock).
- Captions not the print's. Old Figure B.7 "piles" is printed "Pile
  groups" (p. 108). Old Table E.2 named λc and λl; the print has λc and
  λd (p. 122).
- Figures B.4 Tunnels and caverns (p. 106), B.5 Excavations (p. 107) and
  C.1 Measured and predicted groundwater levels (p. 110) were missing.

### Print inconsistencies, kept as printed

No reading was chosen. Page numbers are printed page numbers.
- 2.4.1.1 (4) has the NOTE "See also 13.2." (p. 24); EN 1997-2 has no
  13.2. The file leaves the note out.
- Table A.1 lists "chlorite content (CCl)" among the laboratory results
  (p. 99).
- D.3 gives C2 = 1,2 + 0,2 lg t and does not define t (p. 112).
- Table D.2 prints "1.0" with a point (p. 114), and Table E.2 prints
  "2.65" and "1.4" (p. 122); their other values use commas.
- The E.2 settlement equation, marked AC1, prints (λd B/B0) with no
  exponent (p. 122).
- F.2's NOTE sends the reader to "X.3.3. 3", and Table F.3's caption
  writes the density index as "(Id)" (p. 126).
- F.3 (2) says settlement below the over-consolidation pressure is one
  third of the normally consolidated value, and gives si = σ'p × B^0,7 ×
  Icc/3 + (q' - σ'p) × B^0,7 × Icc for over-consolidated sand with q' ≥
  σ'p (p. 126). For q' ≤ σ'p it gives si = σ'p × B^0,7 × Icc/3, which
  does not change with q'. For normally consolidated sands it gives si =
  (q' - σ'p) × B^0,7 × Icc (p. 127).
- Table H.1 gives dense as 40 to 90 and very dense as > 80 (p. 132).
- M.5 (3) calibrates other methods "against the methods in (2)"
  (p. 153); sieving and sedimentation are in (1).
- Table P.1 prints its middle row as "0,95 << r ≤ 0,98" (p. 163).
- R.3's NOTE sends compaction procedures to X.4.2 (p. 167), the
  chemical testing list; X.4.6 lists the compaction documents.
- V.3 is the radially confined swelling test, but its NOTE names a test
  on an unconfined specimen and points to X.4.10.2 (p. 174), the
  radially confined method. V.4 repeats the unconfined wording.
- X.3.2 lists EN ISO 22476-7, the borehole jack test, among the
  pressuremeter documents (p. 182).
- X.4.1.4 repeats SN 670 335:1960, a sand replacement method for bulk
  density, among the particle density documents (p. 186).
- X.4.2.6 lists BS 812-118:1988, with its sulfate title, under chloride
  content (p. 189).

Smaller typos are not listed.

### Code that differs from the print

The app reads `eurocode_7_2.equations` through its EC7-2 adapter, so
these two change what a live run returns:
- `equation_g1_density_index_from_dp`, for well-graded sand-gravel above
  groundwater with the DPH, uses ID = 0,14 + 0,550 lg N10H. G.1 prints
  -0,14 (p. 129). tests/test_eurocode_7_2.py pins the + sign.
- `equation_burland_burbridge_settlement` returns (q' - σ'p) × B^0,7 ×
  Icc for q' > σ'p, the normally consolidated form. F.3 (2) gives σ'p ×
  B^0,7 × Icc/3 + (q' - σ'p) × B^0,7 × Icc for over-consolidated sand
  with q' ≥ σ'p (p. 126). The result drops by σ'p × B^0,7 × Icc/3 as q'
  passes σ'p. Its q' ≤ σ'p branch follows the print (p. 127).

Noted, not fixed, because no live result changes:
- The `equation_g3_stiffness_coefficient_from_dp` docstring gives the
  DPH range for sands as 3 ≤ N10H ≤ 30; G.3 prints ≤ 10 (p. 130). The
  code checks no range.
- `equation_i5_fvt_correction_factor` takes wL in percent and divides by
  100. I.5 prints no unit (pp. 136 to 137); the docstring gives the
  reason.
- figures_catalog.json has no Figures B.4, B.5 or C.1. Their captions
  and contents are in B.3 and C.
