"""geotech_references — digitized geotechnical reference library.

Sub-packages
------------
dm7_1 : UFC 3-220-10N (formerly NAVFAC DM 7.1) — Soil Mechanics
dm7_2 : UFC 3-220-10N (formerly NAVFAC DM 7.2) — Foundations & Earth Structures
gec_6 : FHWA-SA-02-054 — Shallow Foundations
gec_7 : FHWA-NHI-14-007 — Soil Nail Walls
gec_10 : FHWA-NHI-10-016 — Drilled Shafts
gec_11 : FHWA-NHI-10-024 — MSE Walls & Slopes
gec_12 : FHWA-NHI-16-009 — Driven Pile Foundations
gec_13 : FHWA-NHI-16-027 — Ground Modification Methods
micropile : FHWA-NHI-05-039 — Micropile Design & Construction
ufc_backfill : UFC 3-220-04N — Backfill for Subsurface Structures
ufc_expansive : UFC 3-220-07 — Foundations in Expansive Soils
ufc_pavement : UFC 3-250-01 (2016) — Pavement Design for Roads and Parking
             Areas (REBUILT 2026-07 from the actual document: mixed-traffic
             equivalent ESALs, CBR flexible design curve E-1, rigid Eq 13-1
             + reinforced design, overlays Ch 15, joints/dowels, frost Ch 19,
             subsurface drainage Ch 20; US customary)
ufc_stabilization : UFC 3-250-11 (2020) — Soil Stabilization and Modification
             (additive selection, strength/durability criteria, mix design,
             equivalency factors)
ufc_flexible_practice : UFC 3-250-03 (2018) — Standard Practice Manual for
             Flexible Pavements (HMA gradations, Marshall/Superpave criteria,
             spray applications, seal coats, RMP; Marshall volumetrics)
ufc_concrete_practice : UFC 3-250-04 (2024) — Standard Practice for Concrete
             Pavements (materials tables, dowel tolerances, joint spacing,
             RCC, cracking causes)
fema_p2082 : FEMA P-2082 — 2020 NEHRP Recommended Seismic Provisions
             (Ch 20 site classification, Ch 11 seismic design criteria)
california_trenching : California (Caltrans) Trenching and Shoring Manual —
             temporary excavation support (Cal/OSHA soil types & slopes, earth
             pressure, apparent earth pressure for braced/anchored walls, heave)
fhwa_pavements : FHWA-NHI-05-037 — Geotechnical Aspects of Pavements (resilient
             modulus Mr, CBR, soil-as-pavement-material suitability, drainage,
             frost susceptibility, swell, stabilization, compaction; DISTINCT
             from the UFC 3-250-01 roads/parking design module ``ufc_pavement``)
eurocode_7_1 : EN 1997-1:2004 — Eurocode 7 Geotechnical Design Part 1, General
             Rules (Annex A partial-factor sets A/M/R + Design Approaches,
             sample earth pressures, bearing resistance, settlement)
eurocode_7_2 : EN 1997-2:2007 — Eurocode 7 Part 2, Ground Investigation and
             Testing (CPT/PMT/SPT/DP/FVT/DMT/PLT derived-value correlations,
             lab-test minima)
aashto_1993 : AASHTO Guide for Design of Pavement Structures (1993) — flexible
             SN + rigid D design equations, layer coefficients, reliability,
             drainage, full Appendix D ESAL load-equivalency tables D.1-D.18
             (lef.py), Section 3.2 composite/effective subgrade-reaction
             worksheet (composite_k.py), Appendix G swelling/frost-heave
             serviceability loss (environmental.py) (US customary units)
"""
