# REF-52, GEC-12 and GEC-5 8.10.2: check (2026-11-05)

Branch `claude/ref-52-gec12-headings`, from main 1427409.

## Result: nothing left to add

The gaps this task names were closed on main before this run:

- GEC-12 Vol II ch 9-18 (the survey's 98 missing headings plus the 80
  inside range sections): refs 95aabd6, one commit per chapter (for
  example c382d2d for ch 9). See "GEC-12 Vol II written from the print"
  in `docs/REF52_SURVEY.md`.
- GEC-5, 8.10.2 "p-y Curves" and its other 90 missing headings: refs
  39f779f, review fixes 6fbaa4e. `gec_5/text/chapter08.json` now has
  8.10, 8.10.1 and 8.10.2.

So no heading was added, no text was moved, no section id changed and
no search index or catalog needed a rebuild. This branch carries only
this file.

## Section checker, run afresh

`python scripts/check_section_numbers.py gec_12 gec_5` (same before and
after, since nothing changed):

| reference | printed | matched | range | misnumber | missing | extra | ambiguous |
|---|---|---|---|---|---|---|---|
| gec_12 | 471 | 471 | 0 | 0 | 0 | 1 | 2 |
| gec_5 | 390 | 390 | 0 | 0 | 0 | 0 | 0 |

The three GEC-12 rows to read are the ones the survey already lists as
flagged by the checker, not real gaps:

- `chapter03.json` 3.0 "Introduction": extra (an unprinted number for
  the chapter opening; was REF-30).
- `chapter07.json` 7.2.3.2.2 and 7.2.3.2.3: ambiguous, because the
  contents number them one lower than the page headings. The sections
  follow the page.

## Tests

- Refs suite, serial (`pytest tests -q`): **6,487 passed, 2 xfailed, 0
  failed**, exit 0.
- Refs suite with `-n 4` (as the brief asks): exit 1, **1 failed and 88
  errors**, every one `sqlite3.OperationalError: disk I/O error` in
  `_retrieval_db._build_db` (test_query_expansion 87, four DM7 chapter
  files, test_fhwa_soils_foundations 1). Two workers rebuilding the one
  temp search database at once: the race BACKLOG REF-56 describes. The
  same tree passes serially, and this branch changes no code.
- App, with this refs checkout installed editable:
  `test_reference_example_ids.py`, `test_reference_adapters.py`,
  `test_reference_result_sizes.py`: **399 passed, 0 failed**, exit 0.

## Noted, not fixed

- **GEC-12 Vol III, Appendix D** (the design example, Vol III pp. 35-299
  in the PDF) has no text file, so the checker does not count it. The
  survey lists 75 printed headings there (D.1 to D.14 and their
  subheadings), and the app's citation guard lists Tables D-6, D-51 and
  D-100 as library gaps (`funhouse_agent/tests/test_citations.py`,
  REFERENCE_GAPS; `adapters/axial_pile.py` cites Table D-100). Building
  it means a new appendix file read off about 265 pages, mostly tables
  and figures. That is outside the "headings with no section" gap this
  task names; it is the lead's call whether it becomes its own item.
- REF-56 bit this run: `pytest -n 4` on a fresh temp folder fails on the
  shared database rebuild. Until it is fixed, run the refs suite serially
  or let one test build the database first.
