# REF-04: rescue branch checked against the print

Branch `rescue/reference-wip-2026-06-02` (7fb6fe8, base 829b897) merged onto
main (ceeef53) on `wip/ref04`, then every new chapter checked page by page
against the PDFs in `docs/` (2026-10-30). Fixes were made from the printed
page, never from memory: equations were rendered from the PDF and read symbol
by symbol; table values, figure and table numbers, captions and page numbers
were read off the page. Counts below are wrong or unprinted statements found
and fixed (approximate where one sentence held several errors).

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
  back to main's.

## Found but not fixed (main's own files, outside the rescue branch)

- **GEC-7 ch 1-5 bodies and key points** are not from the print (examples
  above). The ch 5 values its summaries quote (Eq 5.1, Tables 5.3-5.12)
  match the print. These chapters need a rebuild from the
  print like GEC-13's (REF-25).
- **GEC-12 ch 7 top-level bodies (7.1-7.10)** are generated overviews with
  unprinted claims, e.g. setup "2-5 times", group settlement "1.5-3 times",
  "minimum 10 ft into the bearing layer", predrilling "reduces shaft
  resistance 50-85%". The numbered subsections are print-based.

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
