"""EM 1110-1-1905, Geotechnical Design of Shallow Foundations on Soils
(U.S. Army Corps of Engineers, 31 July 2025; approved for public release,
distribution unlimited). It supersedes EM 1110-1-1904 (1990) and
EM 1110-1-1905 (1992).

The chapter text in ``text/`` and the figure catalog are read off the
printed pages (``scripts/build_printed_text.py``, layout "army", and
``scripts/build_figure_catalog.py``). Each section's body is the print's own
wording with ``[p. 93]`` markers for the printed pages; every numbered
equation (213) is typed in from the rendered page with its symbols and
units (manifest ``printed_equations``).

  Chapters 1 Overview, 2 Design and Performance Requirements, 3 Soil
  Properties, 4 Site Exploration, 5 Ultimate Limit State for Static
  Analysis, 6 Stress Distribution, 7 Settlement, 8 Mat Foundations,
  9 Seismic Design, 10 Problematic Ground Conditions, 11 Ground Improvement,
  12 Earthwork Observation, Testing, and Documentation; Appendix B (design
  examples, ultimate limit states) as chapter 13, Appendix C (design
  examples, settlement) as chapter 14, Appendix D (unit conversion factors)
  as chapter 15. Not built: the front matter, Appendix A (references) and
  the glossary.

Section ids are the printed paragraph numbers: '5-5' for a paragraph, its
subparagraphs a., (1), (a) and 1 as '5-5a', '5-5a(2)', '5-5a(2)(b)' and
'2-7a(2)(c)1'; 'B-1b' in an appendix; 'B' for an appendix's opening text.

Lookups, in the manual's US units: ``tables`` (Tables 2-1, 5-2 to 5-5 and
7-6), ``equations`` (Chapter 5, the ultimate limit state, Eqs. 5-1 to
5-36), ``settlement`` (Chapter 6 stress distribution and Chapter 7
settlement, Eqs. 6-1 to 6-13 and 7-1 to 7-47) and ``figures`` (the table
printed on Figure 7-16). Each function returns a dict with its values,
``units``, ``source`` (the printed page), ``valid_for`` and ``notes``, and
raises ValueError outside what the print covers. A limit printed as part
of a relation (dc <= 1.5, Pa,d >= 0) is applied as printed: the limited
value is returned with the formula's value beside it and
``limit_governs``; an input the page's own conditions exclude is refused,
the message naming the condition and the page. Each docstring
holds a print check: the formula as printed beside what the code does. The
tests run the Appendix B and C worked examples. The other charts are not
digitized: read them off the rendered page through the figure catalog.
"""
