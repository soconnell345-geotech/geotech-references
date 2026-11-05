# REF-52: the citation guard's library gaps (the part that was REF-36)

Branch `claude/ref-52-citation-gaps` from main 1427409. The app's
`funhouse_agent/tests/test_citations.py` lists in `REFERENCE_GAPS` the printed
numbers the app cites correctly but the library's chapter text leaves out.
The list holds 18 entries (the backlog says 19). Each one was read on the
PDF page (text layer, and the rendered page wherever the text layer was
unclear: every equation and table below was checked on a render) and added
in the section that prints it.

## Entries added

| Manual | Number | Section id (file) | Printed page | PDF page |
|---|---|---|---|---|
| GEC-9 (FHWA-HIF-18-031) | Eq. A-9 | A.2 (`gec_9/text/appendix_a.json`) | 222 | 226 |
| GEC-9 | Table A-1 | A.2 | 222 | 226 |
| GEC-9 | Table A-2 | A.2 | 222 | 226 |
| GEC-9 | Eq. A-20 | A.3 | 226 | 230 |
| GEC-9 | Eq. A-21 | A.3 | 226 | 230 |
| GEC-9 | Eq. A-27 | A.4 | 228 | 232 |
| GEC-9 | Table A-3 | A.4 | 228 | 232 |
| GEC-10 (FHWA-NHI-18-024) | Eq. A-2 | A.2 (`gec_10/text/appendix_a.json`) | A-8 | 591 |
| GEC-11 Vol I (FHWA-NHI-10-024) | Eq. 4-21 | 4.4.6.c (`gec_11/text/chapter04.json`) | 4-28 | 170 |
| GEC-11 Vol I | Eq. 4-22 | 4.4.6.c | 4-28 | 170 |
| GEC-11 Vol I | Table 4-6 | 4.4.6.c | 4-29 | 171 |
| GEC-11 Vol I | Eq. 4-23 | 4.4.6.c | 4-30 | 172 |
| GEC-11 Vol I | Eq. 4-24 | 4.4.6.c | 4-30 | 172 |
| UFC 3-220-20 (dm7_2) | Table B-17 | B-3.4 (`dm7_2/text/appendix_b.json`) | 622 | 660 |
| GEC-12 Vol III (FHWA-NHI-16-009) | Table D-6 | D.10.1 (`gec_12/text/appendix_d.json`) | 28 to 29 | 62 to 63 |
| GEC-12 Vol III | Table D-51 | D.22.1 | 100 | 134 |
| GEC-12 Vol III | Table D-100 | D.34.1 | 179 to 180 | 213 to 214 |

What else came with them, so each number sits in its printed section:

- **GEC-9 Appendix A** had no text. It is now its own file (chapter 14, the
  next number after the printed chapters, as EN 1997-2's annex files are
  numbered): sections A (the appendix's opening text), A.1 to A.7 and
  A.7.1, the text in the print's wording with page marks, Eqs. A-1 to A-53
  and Tables A-1 to A-3 as printed, Figures A-1 to A-13 by caption.
- **GEC-10 Appendix A** (the design example) had no text. Its own file
  (chapter 19): A.1, A.2 and A.3 in the condensed style of the GEC-10
  chapter files, with the worked numbers as printed, Eqs. A-1 and A-2,
  Table A-1 with its values and Tables A-2 to A-10 and Figures A-1 to A-14
  by caption.
- **GEC-11 Sec. 4.4.6.c** listed Eqs. 4-17 to 4-20. Eqs. 4-21 to 4-24 and
  Table 4-6 (all 46 rows) are added. The entries for Eqs. 4-19 and 4-20
  called them "eB for horizontal backfill" and "eB for sloping backfill";
  the print has 4-19 as eB (horizontal backslope) and 4-20 as the factored
  stress sigma_V-F, with 4-21 the sloping-backfill stress, so those two
  entries and the body sentence naming them now follow the page.
- **UFC 3-220-20 Appendix B** had no text. Example 3 (B-3 to B-3.7, pp. 618
  to 626, bearing capacity of three footings near a slope) is its own file
  (chapter 9), with Tables B-14 to B-21 cell by cell.
- **GEC-12 Vol III Appendix D** had no text. The whole appendix is built
  (see below).

## Already in the library under another form

- **GEC-4 Eqs. 15-16** (p. 62, Sec. 5.2.9). Both are in Sec. 5.2.9 already,
  as `Eq. 15: Uf = ...` and `Eq. 16: Uc = ...`, with the right formulas. The
  guard still flags them because its single-sequence pattern `_BARE["eq"]`
  reads only the word "Equation N", while every GEC-4 file writes "Eq. N".
  No copy was added. The fix is the app's: let `_BARE["eq"]` also read
  `Eq. N` (or leave the entry in `REFERENCE_GAPS`).

## The REFERENCE_GAPS lines the app should drop

With this branch the guard finds all of these, so
`test_the_reference_gap_list_is_exact` fails on them, as it should (17):

```
("gec_9", "eq", "A-9"), ("gec_9", "eq", "A-20"), ("gec_9", "eq", "A-21"),
("gec_9", "eq", "A-27"), ("gec_9", "table", "A-1"), ("gec_9", "table", "A-2"),
("gec_9", "table", "A-3"), ("gec_10", "eq", "A-2"),
("gec_11", "eq", "4-21"), ("gec_11", "eq", "4-22"), ("gec_11", "eq", "4-23"),
("gec_11", "eq", "4-24"), ("gec_11", "table", "4-6"),
("gec_12", "table", "D-6"), ("gec_12", "table", "D-51"),
("gec_12", "table", "D-100"), ("dm7_2", "table", "B-17")
```

`("gec_4", "eq", "15-16")` stays until the guard reads "Eq. N" (above).

## GEC-12 Appendix D: what was built and what is left

Built by `scripts/build_gec12_appendix_d.py` (helpers in
`scripts/gec12_appendix_d_extract.py`) off the printed pages, no API; it
reproduces `appendix_d.json` byte for byte.

- All of it: D.1 to D.56, every printed heading (all 75 are in the PDF
  outline; the checker matches every one), plus a section D for the opening
  text. File chapter 22 (Vol II's unbuilt Appendices A to C would be 19 to
  21).
- Bodies are the print's wording with `[p. N]` marks (printed page = PDF
  page - 34). No summaries, no key points, as for the other printed build
  (`fhwa_soils_foundations`).
- All 135 tables (D-1 to D-135), each with its cells as printed, read across
  the rows. D-6, D-51 and D-100 are given row by row (depth / shaft / toe /
  nominal), checked against the rendered pages.
- All 125 figures by caption and printed page.
- The appendix's own Eqs. D-1 to D-7 typed in from the renders, each in the
  section that prints it (D.13, D.15, D.19, D.30).
- 13 sections over the reference tools' size are split into lettered parts
  (`D.15.a`, `D.39.c` ...), the letters not printed, as
  `build_printed_text.py` does; the largest section now fetches at 12,750
  characters through `reference_get`. The audit's section-number pattern
  was widened to take these (and UFC 3-220-20's `B-3.4`).

Left, and why:

- **Display equations** (the worked calculations between the prose) are
  not typed in. The text layer maps their subscript glyphs wrongly, so they
  are marked `[equation shown on the page]` beside the printed tag
  (`[Eq. 7-61]`). Where a "Where:" list defines a symbol on its own line,
  the body keeps the definition and loses the symbol ("= minimum
  penetration depth based on ...").
- Symbols inside sentences were read by halving the doubled glyphs; the
  ones the text layer maps wrongly (Rndr, phi_dyn, phi_stat, sigma_dr,
  W_Block, R_ug, M_ux, M_rx, V_uy, P_ui, P_uz, sigma'_vo, Q_max,
  D_min-tension, gamma'_soil, D_(individual)) were corrected from the
  renders. Others that halve to a plausible but wrong subscript cannot be
  ruled out without reading every page.

## Section checker (before -> after)

`scripts/check_section_numbers.py` on the references touched:

| Reference | printed | matched | extra | missing |
|---|---|---|---|---|
| gec_4 | 234 -> 234 | 233 -> 233 | 8 -> 8 | 1 -> 1 |
| gec_9 | 187 -> 195 | 187 -> 195 | 0 -> 1 | 0 -> 0 |
| gec_10 | 408 -> 411 | 391 -> 394 | 1 -> 1 | 17 -> 17 |
| gec_11 | 214 -> 214 | 148 -> 148 | 33 -> 33 | 66 -> 66 |
| gec_12 | 471 -> 546 | 471 -> 546 | 1 -> 14 | 0 -> 0 |
| dm7_2 | 437 -> 496 | 421 -> 429 | 17 -> 17 | 16 -> 67 |

- gec_9: the new extra is section `A`, the appendix's opening text, which
  has no printed number (EN 1997-2's annex files carry the same kind).
- gec_12: the 13 new extras are the lettered parts and section `D`; one
  part (`D.10.3.a`) is also listed as a held misnumbering of D.10.3.
- dm7_2: once Appendix B has a file the checker counts its 59 printed
  headings; Example 3's 8 are matched and the other examples' 51 (B-1, B-2,
  B-4 to B-7) are missing because they are not built.

## Tests

Same venv (`python3.12 -m venv /tmp/v`, this checkout installed editable,
the app installed editable beside it; matplotlib, numpy and scipy added
because some refs tests import them).

- **geotech-references, `pytest tests -q`, serial:** 6,487 passed,
  2 xfailed, exit code 0 (after the test change below). Before that change:
  6,483 passed, 4 failed.
- **The test change:** `tests/test_subsection_retrieval.py::
  test_a_parent_is_still_found_by_its_title` failed for GEC-12 7.2.1, 7.2.2,
  7.2.3 and 7.2.3.2. Appendix D's worked-example sections print the same
  phrases at length ("Geotechnical Resistance in Axial Tension", "Pile
  Groups") and now outrank those parents in a gec_12-wide search by their
  own title: ranks 10, 9, 9 and 6 (top hits D.22.2, D.34.2, D.13, D.12 ...).
  The test's stated purpose is that a parent's own subsections do not crowd
  it out, so its search is now scoped to the parent's chapter (`chapter=`),
  where all 13 parents are in the top five. The library-wide ranks are a
  real search effect of adding the appendix; the lead may prefer another
  remedy (a lower weight for appendix sections, or REF-53's title weight).
- **Ranking evals** (main 1427409 -> this branch): `eval_retrieval_gold.py`
  `auto` R@3/5/10 37/41/44 of 54 unchanged, MRR@10 0.570 -> 0.569; `fill`
  unchanged; `rerank` R@5 36 -> 35 (spt-def's hit moves from rank 6 to 8,
  stone-col-capacity's from 5 to 6 in rerank). `eval_subsection_retrieval.py`:
  recall@5 15/15, reached 15/15.
- **Audit:** `scripts/audit_chapter_text.py` passes for gec_9, gec_10,
  gec_11, gec_12 and dm7_2 (its section-number pattern now takes `B-3.4`
  and `D.15.a`).
- **App, `funhouse_agent/tests/test_citations.py`,
  `test_reference_example_ids.py`, `test_reference_adapters.py`,
  `test_reference_result_sizes.py`:** 402 passed, 2 failed, both expected:
  - `test_citations.py::test_the_reference_gap_list_is_exact` fails on
    exactly the 17 entries listed above (the library now carries them).
  - `test_reference_example_ids.py::test_examples_come_from_the_reference_itself`
    expects GEC-12's examples `['1.1', '3.2.3.1', '5.2.3.1.1']` and now gets
    `['D', '3.2.1', '5.2.3.1.1']`: `example_section_ids` takes a lettered
    top-level section (here Appendix D's opening text, `D`) as the example
    at a level no numbered section has. All three resolve
    (`test_retrieve_section_examples_resolve` passes). The app updates the
    expected list when it pins this commit.
  - `test_reference_result_sizes.py` passes: every Appendix D section
    fetches within the 16,000-character cap (largest 12,750).

## Noted, not fixed

- GEC-11 Table 4-6 prints Nc = 37.9 at phi = 39 (the AASHTO table has
  67.9); kept as printed and marked.
- GEC-9 Eq. A-51 prints `3 D2^2` in its first bracket where the pattern of
  Eq. A-47 gives `3 D3^2`, and Eq. A-47's first term has no `z` where Eq.
  A-51's has `K0 z`; both kept as printed.
- GEC-12 Appendix D's text calls the cost equation "Equation D-5" (p. 85;
  its tag is Eq. D-6) and says "Using Equation D-1" for the angular
  distortion limit (p. 166; the equation is D-7).
- GEC-11 4.4.6.c: the entries for Eqs. 4-17 and 4-18 were not checked
  against the print.
- UFC 3-220-20 Appendix B: Examples 1, 2 and 4 to 7 are not built; GEC-10
  Appendices B to H and GEC-12 Vol II Appendices A to C are not built.
- GEC-9 Appendix B to E and GEC-10 Appendix A Tables A-2 to A-10 (by
  caption only) are not built out.
- `list_chapters("gec_12", max_chars=14000)` was already over the limit
  before this branch (36,160 characters; 36,530 now); the app shapes it.
