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
