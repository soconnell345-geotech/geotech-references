# FHWA NHI-06-088 / NHI-06-089, "Soils and Foundations Reference Manual",
# Volumes I and II (NHI Course No. 132012), Federal Highway Administration,
# December 2006. Samtani & Nowatzki (2006).
#
# Text only (no Python lookups yet): the chapter text in ``text/`` and the
# figure catalog are read off the printed pages by
# ``scripts/build_printed_text.py`` (BACKLOG REF-29). Each section's body is
# the print's own wording with ``[p. 6-28]`` markers for the printed pages.
#
#   Volume I (FHWA NHI-06-088): 1 Introduction, 2 Stress and Strain in Soils,
#     3 Subsurface Explorations, 4 Engineering Description, Classification and
#     Characteristics of Soils and Rocks, 5 Laboratory Testing for Geotechnical
#     Design and Construction, 6 Slope Stability, 7 Approach Roadway
#     Deformations.
#   Volume II (FHWA NHI-06-089): 8 Shallow Foundations, 9 Deep Foundations,
#     10 Earth Retaining Structures, 11 Geotechnical Reports, 12 References.
#
# Chapters are numbered through both volumes as the manual numbers them, so
# one package holds both (as gec_11 holds GEC-11's two volumes); each chapter
# file carries its own volume's designation in ``reference_id``.
