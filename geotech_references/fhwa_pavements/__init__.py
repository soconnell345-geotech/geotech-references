# FHWA-NHI-05-037, "Geotechnical Aspects of Pavements" (Reference Manual /
# Participant Workbook, NHI Course No. 132040), Federal Highway Administration,
# May 2006. Authors: Christopher, Schwartz & Boudreau.
#
# This is the broad GEOTECHNICAL-aspects pavement reference (DISTINCT from the
# narrower UFC 3-250-01 roads/parking design module, ``ufc_pavement``). The
# digitized lookups focus on the soil/geotech inputs an engineer needs for
# pavement design:
#
#   - Resilient modulus Mr (Chapter 5): correlations from CBR, R-value, layer
#     coefficient, and plasticity/gradation (Table 5-34); default Mr ranges and
#     typical values by AASHTO and USCS soil class (Table 5-35); the AASHTO 1993
#     bulk-stress-dependent base/subbase Mr-CBR/R correlations and the subgrade
#     Mr-CBR (Heukelom & Klomp) and Mr-R-value (Asphalt Institute) forms; the
#     seasonal / backcalculated-to-design adjustment factors (Table 5-32 / NCHRP).
#   - CBR (Chapter 5): typical field CBR by USCS soil class (Table 5-28) and the
#     DCP-CBR correlation (Table 5-34).
#   - Soil suitability as a pavement material by USCS class — subgrade strength,
#     potential frost action, compressibility/expansion, drainage (Table 4-14).
#   - Drainage (Chapters 5, 7): AASHTO 1993 drainage modifier mi (flexible,
#     Table 5-49) and drainage coefficient Cd (rigid, Table 5-50); AASHTO quality-
#     of-drainage time-to-drain definitions (Table 7-4); typical saturated
#     hydraulic conductivity for soils (Table 5-56) and highway materials
#     (Table 5-57).
#   - Frost (Chapter 7): frost-susceptibility classification F1-F4 (Table 7-12).
#   - Stabilization & expansive soils (Chapter 7): swell potential from
#     Atterberg limits (Tables 5-23/5-24, 7-17) and the lime/cement/asphalt
#     stabilization applicability guidance.
#   - Compaction (Chapter 5): typical compacted dry unit weight and optimum
#     moisture content by AASHTO soil class (Table 5-18).
#
# UNITS: this reference is largely US customary (psi for Mr, % for CBR/R-value,
# pcf for unit weight) with SI given in parentheses in the source. The digitized
# values are kept in the source's PRIMARY units (psi, %, pcf, ft) to match the
# manual; conversions (1 psi = 6.9 kPa; pcf->kN/m3) are noted, not applied.
#
# Source PDF text layer is intact (no OCR was required). Image-only design
# charts / matrix tables (e.g. Fig 5-17 Mr-vs-property nomograph, Table 7-16
# admixture-selection matrix, Table 7-13 stabilization-method matrix) are exposed
# through the figure catalog rather than digitized as numbers.
