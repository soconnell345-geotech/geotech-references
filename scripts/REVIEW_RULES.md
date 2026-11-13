# Rules for building and checking this library's content

For any session (local or cloud) that builds stored text or lookups from a
printed manual, or checks someone else's build. Open work is tracked in the
GeotechStaffEngineer repository's `BACKLOG.md`, not here.

This library holds digitised engineering manuals: coded lookups and stored
chapter text that an LLM helper searches and quotes to practising engineers.
A wrong stored number reaches an engineer's answer, and nothing downstream
will catch it. The printed page is the only authority.

## Setup

- Work from the branch you are given, never from `main` unless told so.
- `pip install -e . pytest pymupdf==1.27.2.3` (that PyMuPDF version exactly:
  script-built text was built with it; see "The PDF reader is part of a
  script build" in `CLAUDE.md`).
- Source PDFs are in `docs/`. `scripts/manifests/<package>.json` names each
  package's PDF and its page ranges. Work out the offset between PDF page
  index and printed page yourself and state it.

## Reading the print

1. Render the page with PyMuPDF at 300 dpi to a PNG (crop to the table,
   equation or passage) and LOOK at the image. The image governs.
2. The PDF's text layer may be used to find things, to compare long prose,
   and as a cross-check. It loses things the image shows: a greater-or-equal
   sign can come out as `$`, less-or-equal as `#`, a degree sign as a raised
   `o`, a Greek letter as a Latin one, a power of ten as plain digits
   (`x 106` for x 10^6), and it scrambles stacked fractions and subscripts.
   Every formula line, numbered or not, every table cell, every symbol,
   exponent, subscript and unit is read from the image.
3. Nothing from memory and nothing from another source or edition.

## What is stored

4. What is printed, as printed: units, footnotes and notes in the print's
   words; the real symbols; exponents written with `^`; a printed dash as a
   dash; an empty cell as empty; "should" where the print says should and
   "must" where it says must.
5. Where the print itself is wrong (arithmetic that does not follow, a
   pointer to the wrong table, a unit that cannot be right), it is kept as
   printed with a note beside it, `[as printed; <what the page shows and
   what follows from the print's own numbers>]`. Never corrected silently.
6. A lookup returns what its page prints. Outside the printed range it
   refuses, naming the range and page, unless the print gives an open-ended
   row or says what to do beyond the range. Anything the library adds (a
   limit, a reading of an ambiguous page) is labelled in the result as the
   library's reading, never presented as the manual's.
7. Stored text is never shortened or dropped to fit a size limit: a long
   section is split into lettered parts (`8.1.a`; the part's applicability
   says the letter is the library's, not printed).
8. A table typed into a section's `tables` entry uses the form the library
   already has (see `geotech_references/gec_10/text/chapter08.json`,
   Tables 8-1 to 8-4): `Table N: caption (p. <printed page>) - columns: ...`
   then the rows and the printed notes.

## Builders

9. Do not change a coded lookup's values unless that is the task. If a
   lookup disagrees with a page you read, report it (function, input,
   returned, printed, page).
10. A reference built by script from a manifest (`"text_build"` in its
    manifest) is changed through the manifest, so that a rebuild reproduces
    the committed files.
11. Tests assert printed values (these are public manuals); any other test
    data is made up. Run only the test files your change touches, one file
    at a time, and `python scripts/audit_chapter_text.py <package>`.
12. Commit in small steps, staging exact paths, with plain-words messages.
    Push only the branch you were given to push. No tags, no release, no
    change under `.github/` unless that is the task.
13. If you run short of context or time, stop at a clean commit, push, and
    report exactly what is done and what is left.

## Checkers

14. A checker is independent: it reads the pages itself and does not rely on
    the builder's notes, renders or test results. It changes nothing unless
    told to; it reports.
15. Check, in this order: values an engineer copies (table cells, factors,
    limits, formulas, worked-example lines with their arithmetic recomputed)
    completely; every "as printed" note (is the page as the note says, is
    the corrected value right); then a seeded sample of prose per chapter
    (state the seed), taking in every sentence that carries a number, a
    limit or shall / must / should / may.
16. Look for what a builder cannot see in its own work: a slip of the print
    with no note, a silent correction, a sentence the print does not have,
    text cut to fit a limit, a section id added, renamed or removed, a
    figure or table listed under the wrong section, a page marker on the
    wrong page.
17. Where the text reads a value from a table or chart that the package
    codes as a lookup, call the lookup with the same inputs and compare. A
    disagreement is a finding against the lookup or the print: say which,
    from the page.
18. Report: a verdict per part (merge as is / after named fixes / not);
    every item not as printed, most serious first, unsafe ones marked, each
    with section, printed page, what is stored and what is printed; counts
    of what was checked; tests run with counts and exit codes; and what you
    could not check.
