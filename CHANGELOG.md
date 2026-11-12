# Changelog

Releases before 1.6.0 are described in their release commits (`git log`).

## Unreleased

**Build of 2026-11-10: the UFS 3-220-10 (dm7_1) chapter text states its
equations as printed (app BACKLOG REF-79).** Every equation in chapters 1-8
was read off the rendered page and compared with the stored `equations`,
`body` and `key_points`. No function changes; the text an agent quotes does.
Pages are printed page numbers.

- Formulas that were wrong: Is(50) = F·P/d² and F = √(De/50) (Eqs. 1-4,
  1-5, p. 32); five rows of Table 4-2 (line, rectangular, triangular, slope
  and terrace loads, pp. 185-186); s = ΔH = Σ εz,i·Hi (Eq. 5-4, p. 227);
  the zi of Eq. 5-7 (p. 232); FSg = kg/ks = ψg·tg/ks (Eq. 6-16, p. 325);
  φ′ = 31 + KD/(0.236 + 0.066·KD) (Eq. 8-11, p. 406); E = (2/3)(1 + ν)Eu
  (Eq. 8-36, p. 449).
- Formulas the text left out are typed in: Eqs. 5-19 to 5-22, 5-24, 5-25,
  5-27 and 5-28 (pp. 254-268).
- Equations filed where they are printed: Eq. 3-5 in 3-2.7.3 (was 3-3.1),
  Eq. 4-12 in 4-5.5.2 (was 4-6.3), Eq. 7-2 in the new section 7-5.2
  Seepage Forces (p. 357; was 7-6.7). Copies under sections that only cite
  an equation are removed (Eqs. 5-9, 5-15, 5-22, 6-3, 6-5, 6-11, 7-1).
- Key points that misread a table: Tables 8-11, 8-20, 8-21 and 8-25
  (pp. 429-459); the UCT key point no longer states su = qu/2, which the
  section does not print (p. 152). Sections 4-7 and 4-8 no longer list
  Tables 4-7 and 4-8, which are tunnelling tables.
- Kept as printed, with a note: KD = (p1 − p0)/σ′v0 on p. 88 (Eq. 8-10
  prints (p0 − u0)/σ′v); the time factor C1 in the where-list of Eq. 5-7
  (Eq. 5-9 calls it C2); qt = qc + u·(1 + a) for Eq. 8-25 (the note cites
  qt = qc + u2(1 − a) from FHWA-NHI-16-072, GEC 5, Eq. 4.23, p. 4-29); the
  condition FC×PI = 0 on the first row of Table 8-22 (p. 455; the note adds
  that FHWA-NHI-05-037 Table 5-34, p. 5-53, prints the relation with no
  condition); "Example 1, Poorly-Graded Gravel with Sand (GW)" in 1-3.2.3
  (p. 13; Section 1-3.3.2 uses GP for poorly-graded gravel). The heading of
  3-2.4.2.1 prints "(ASTM D2116)"; its text and Table 3-4 print D2166, and
  the body says so (p. 152).
- The constant of Eqs. 6-13 and 8-41 is in cm/(s·mm²). Eq. 8-30 points to
  `intrinsic_compression_index_from_el` (it named the Figure 8-46 lookup).
- The seven printed sections the text did not hold are added in the print's
  wording: 1-3.2.3 Examples, 2-2.2 Published Geologic and Hydrogeologic Maps
  (lists Table 2-2), 3-2.5.1.2 Resonant Column Test, 3-2.5.1.3 Cyclic
  Triaxial Test for Modulus and Damping, 4-2.2 Mohr Circle of Stress (lists
  Figure 4-3), 5-5.5 Organic Soils and Peat, 8-4.5 Coefficient of
  Consolidation (lists Figure 8-50). The text now holds all 465 printed
  sections (`scripts/check_section_numbers.py dm7_1`: 0 missing).
- Four bodies cut off mid-sentence are completed from the print: 1-3.2.2.2,
  2-4.2, 3-2.3.2 and 6-3.4; 6-3.4 now lists Tables 6-6 and 6-7 (p. 302),
  which no section listed.
- The formulas and values of the tables in chapters 5, 6 and 8 were read
  off the rendered pages and compared with the key points and summaries
  that restate them. Key points that said more than the print now say what
  it says: m is about 0.8 from direct simple shear tests (Ladd et al. 1977),
  not "for most clays", and the print never says SHANSEP (8-3.2, Tables 8-7
  and 8-9); Table 8-17's groups (8-4.4); Table 8-28's exponent n is not
  attributed to a source (8-8.2); O95 < 0.21 mm holds for non-dispersive
  soils (6-5.3.2); filter Cu, D100F and fines (6-5.3.1); void ratio in
  Table 6-5 (6-3.3); Table 8-12 rows (8-4.1.1).
  Test: `tests/test_dm7_1_text_equations.py`.

**Review of 2026-11-10: Eurocode 7 Parts 1 and 2, the Caltrans Trenching and
Shoring Manual and FEMA P-2082 checked against the printed pages.** Lookups
that returned a value the print does not support now return the printed
value or refuse and say why.

Values that change:

- **EN 1997-1 Eqs. C.1 and C.2** (`active_earth_pressure`,
  `passive_earth_pressure`): the pore water pressure is now inside the
  bracket as printed, `K [gamma z + q - u] + u`. Nothing changes where
  u = 0. Below the water table (Kp 3.0, gamma 20 kN/m3, z 5 m, u 49.05 kPa)
  the passive pressure was 349.05 kPa and is 201.90 kPa; the active
  pressure at Ka 0.333 was 82.35 kPa and is 66.02 kPa.
- **EN 1997-1 Table A.11** (`table_a_11_correlation_dynamic_impact_test`):
  the columns are printed ">= 2, >= 5, >= 10, >= 15, >= 20", so n between
  two columns takes the lower column and is no longer interpolated. For
  4 piles tested the factor on the minimum was 1.40 and is 1.50; on the
  mean 1.533 and is 1.60.
- **Caltrans anchor blocks** (`factor_of_safety_requirements`): the factor
  of safety was 1.5 and is 2.0, as Section 10-2 prints.
- **Caltrans Table 3-1, Very Loose sand** (`table_3_1_granular_properties`):
  the unit weights were moist "none", submerged 60 to 100 pcf, and are moist
  below 100 pcf, submerged below 60 pcf.
- **Caltrans Rankine and tension-crack results**: the printed page cited for
  Eq. 4-3-16 is 4-10, for Eq. 4-3-19 4-11, for Eq. 4-4-13 4-19, and for
  Eq. 8-3-3 8-6.

Lookups that now refuse where they used to answer:

- **EN 1997-1 Table A.10** (`table_a_10_correlation_ground_test`): n = 6, 8,
  9 and n above 10 are not printed and were interpolated or capped (n = 6
  gave 1.135 on the minimum). They now raise, and the message gives the
  printed neighbours (n = 5: 1.15, n = 7: 1.12).
- **EN 1997-1 Annex D bearing resistance** (`undrained_bearing_resistance`,
  `drained_bearing_resistance`): `shape="strip"` with no length was computed
  as a square footing (undrained, cu 50 kPa, q 20 kPa, B 2 m: 328.5 kPa
  where a long rectangle gives 277.1 kPa). Annex D prints a rectangular and a square or
  circular case only. Any other shape raises, a rectangular shape needs L,
  and the result names the shape case used. For a strip give
  `shape="rectangular"` and its length.
- **EN 1997-1 Annex A partial and correlation factors** (the 17
  `table_a_*` lookups and `design_approach_sets`): the row and the set must
  be given. A call that left the set out used to get the set of ones
  (`table_a_4_str_geo_soil_parameters()` returned 1.0, where set M2 gives
  1.25). The value returned is still a bare number.
- **EN 1997-1 selectors**: `parameter="cohesion"` (Tables A.2, A.4, A.16)
  and `resistance="shaft"` (Tables A.6 to A.8) picked one of two printed
  rows (effective cohesion 1.25 not undrained shear strength 1.4; shaft in
  compression 1.3 not shaft in tension 1.6). They now raise and name the
  choices.
- **EN 1997-2 Table D.3** (`table_d3_pile_base_resistance`): below the first
  printed column, qc = 10 MPa (qc = 4 MPa gave 2.0 MPa at s/Db = 0.10).
- **EN 1997-2 Table F.3** (`table_f3_phi_from_density_index`): below the
  first printed row, ID = 40 % (ID = 10 % gave 34 degrees; a density index
  passed as the fraction 0.5 gave 41 degrees).
- **EN 1997-2 G.1 and G.3** (`equation_g1_density_index_from_dp`,
  `equation_g3_stiffness_coefficient_from_dp`): outside the printed ranges
  of validity (N10 = 200 gave a density index of 1.10).
- **EN 1997-2 Eq. 4.5** (`equation_4_5_cu_from_dmt`): the material index
  IDMT is now required, since the equation is printed for IDMT < 0.8.
- **Caltrans Table 4-2** (`table_4_2_wall_friction`):
  `interface_material="concrete"` picked mass concrete on foundation
  materials (29 to 31 degrees on clean gravel) over formed or precast
  concrete against soil (22 to 26 degrees). It now raises.
- **Caltrans at-rest coefficient** (`at_rest_k0`): a backfill slope together
  with OCR > 1, which Eq. 4-3-15 does not cover (the slope was ignored).
- **Caltrans cohesive apparent earth pressure**
  (`aep_cohesive_max_ordinate`): the 0.2 to 0.4 factor of Eq. 8-3-2 has no
  default (it was 0.3, which the manual does not print), and for 4 < Ns < 6
  Ka is required so the larger of the two envelopes can be taken.
- **FEMA P-2082 Seismic Design Category** (`seismic_design_category`): S1 is
  required, because Section 11.6 assigns E or F where S1 >= 0.75 (SDS 1.2,
  SD1 0.9 with no S1 gave D).

A result whose shape changed:

- `design_approach_sets("DA1")` returns both combinations of Design
  Approach 1 as `{"description", "combinations": [Combination 1,
  Combination 2], "note"}`. It used to return Combination 1 alone with its
  sets at the top level, so `result["action_set"]` no longer exists for
  "DA1": read `result["combinations"][0]["action_set"]`. "DA1-C1" and
  "DA1-C2" keep their keys and each names the other combination.

Results that now say more, with the same numbers:

- EN 1997-2 `table_d1_phi_e_from_qc`, `table_h1_phi_e_from_wst` and
  `table_d5_alpha_p_alpha_s_sand` return the tables' printed notes; for
  silty or gravelly soil the result says E' is the sand value, not adjusted.
- `table_min_test_count` returns the printed criterion behind low, medium
  and high variability, the table and page, and the footnote on a cell
  (the 0 of Table W.1 is "only valid for very homogeneous rock types with
  extensive experience from nearby locations").
- `site_class_from_vs30` also returns the site classes at vs/1.3 and
  1.3 vs, which Section 20.3 requires when the velocity is estimated from
  correlations.
- `max_allowable_slope_angle` (Caltrans Eqs. 4-5-1 to 4-5-4) computes what
  it did. Its note and its description now open with the caution that
  Eq. 4-5-2 is not dimensionally consistent as the manual prints it and
  that the slope needs a slope stability analysis.
- `heave_factor_of_safety` returns `fs: null` with a note where the driving
  force is zero or negative (it returned infinity, which is not valid JSON).
  Adequacy is judged, as before, on the unrounded ratio QU/Q against 1.5: a
  ratio of 1.4996 is reported as `fs` 1.5 and is not adequate.
- `table_d3_pile_base_resistance` says in a note when qc is above the last
  printed column (25 MPa) and that column was used, and
  `table_f3_phi_from_density_index` says when it interpolated between
  printed rows (the table prints no interpolation rule) or used the
  ID = 100 % row for a higher ID.
- `site_class_from_vs30` gives an estimated velocity no class in the Site
  Class B or A range (Sections 20.2.4 and 20.2.5 require a measured
  velocity for those classes) and says why.
- Three error messages name what is wrong: Table A.3 for a misspelt
  condition, Table A.9 for a fractional n, and the EN 1997-2 quality class
  given as text.
- The chapter text of EN 1997-1 (Eqs. C.1, C.2, Kpc, Tables A.10 and A.11)
  and of Caltrans Section 10-2 is corrected to the print.

**Build of 2026-11-10 (app BACKLOG REF-83): the chapter text of EN 1997-1,
the Caltrans Trenching and Shoring Manual and FEMA P-2082 read again
against the printed pages.** About one section in four had a substantive
error. No lookup changes; what the text tools return does:

- **EN 1997-1**: Eq. 7.16 is Rt;k = Rs;k (stored as Rs;d = Rs;k/gamma_s)
  and Eq. 7.12 is Ft;d <= Rt;d; Eqs. 7.6 and 7.7 were swapped; Eq. 8.1 is
  Pd <= Ra;d. Annex C.2 (Eqs. C.3 to C.10), stored as not legible, is typed
  in from the page. Annex B: B.1 is gamma_F = gamma_S;d gamma_f, the tank
  exception is gamma_F = 1 with gamma_E != 1 (stored as gamma_Sd), and
  B.6.2.2 is the gamma_F = 1 case (stored as gamma_F != 1). Annex D's q is
  the overburden or surcharge pressure and the unprinted Nc = 5.14 is gone.
  "Must" is back to the print's "should" or "may" in 2.4.3, 2.4.8, 5.3.3,
  6.6.2, 6.6.4, 7.5, 7.6.1, 11.5.1, 12.1, 12.4 and Annex F.3.
- **Caltrans**: the maximum slope angle is Eq. 4-5-1 as printed (stored as
  sin(beta) <= sin(phi) + c/(gamma h), which the manual does not print);
  D = 1.2 D0 is the Simplified Method's, not the Rigorous Method's; the
  heave factor of safety 1.5 and the anchor-block factor of safety 2 are
  printed as recommendations; Appendix A's Eqs. A-2-12 to A-2-16 and A-3-1
  to A-3-4 and Tables C-1 and C-2 as printed.
- **FEMA P-2082**: the effective damping ratio of Eq. 19.3-1 is capped at
  0.20 (the cap was missing) and the period factor of Eq. 19.3-3 is on
  beta_s, not beta_rd.
- Equation ids: EN 1997-1 "Annex E Eq." is "Eq. E.1", "Annex E" (6.5.2.3)
  is "Eq. E.1 (Annex E)", "Eq. B.6.1.1" is added; FEMA "19.3-G0",
  "21.4-SDS" and "21.4-SD1" say they are unnumbered. No section ids change.
- New tests pin the printed forms: `tests/test_eurocode_7_1_text_equations.py`,
  `tests/test_california_trenching_text_equations.py`,
  `tests/test_fema_p2082_text_equations.py`.

**EN 1997-1 Annex A text: wrong pile factors corrected (build of
2026-11-12, app BACKLOG REF-83 review).** The stored text of Annex A.3.3.2
gave R4 = 1.3 for the base and total resistance of bored piles (Table A.7)
and the base of CFA piles (Table A.8). The standard prints 1,6 and 1,5
(bored) and 1,45 (CFA), printed p. 132. Its key points also said the R4
column was the same as Table A.6's. The coded tables
(`table_a_7_bored_pile_resistance`, `table_a_8_cfa_pile_resistance`) were
right. This text was in release 1.6.0, so a text answer about R4 for
bored or CFA piles from 1.6.0 should be checked again. Every cell of
Tables A.1 to A.17 in the Annex A text was compared with the print and
the coded tables; no other value was wrong. Also corrected to the print:
- The Table A.11 model factors keep their printed force words: 0.85
  "may", 1.10 "should", 1.20 "shall".
- The Design Approach summary quotes 2.4.7.3.4's NOTEs. It had said
  Combination 1 factors "actions and ground strength, not resistance".
  Set M1 is 1.0 throughout, and set R1 is not 1.0 for piles or anchorages.
- No section now says Design Approach 3 is the usual one for slopes,
  which the print does not say (Annex A.3.3.6, Section 11.5.1).
- Three force words the 2026-11-10 build weakened are back to the print:
  11.5.1(11)P "shall be considered" (ground-structure interaction),
  6.6.4(3)P "shall be considered using EN 1998", and 6.6.2(16) "should
  take account of non-linear stiffness effects".
- Also: 9.5.2 Eq. 9.2 is beta <= phi' (the prime was missing); Eqs.
  2.9a/2.9b are on p. 34, not pp. 33-34; 7.6.3.1(4)P block uplift "shall
  be carried out" per 2.4.7.4.

No lookup and no section id changes. The new tests are in
`tests/test_eurocode_7_1_text_equations.py`.

**UFS 3-220-10 (dm7_1) lookups corrected to the printed manual (review of
2026-11-10).** A review of the `dm7_1` functions against the rendered pages
found equations, tables and charts that did not match the print. Results
from the functions below change; anything computed with them before should
be re-run. Pages are printed page numbers.

Equations re-coded as typeset:

- `cpt_friction_angle_robertson_campanella` (Eq. 8-8, p. 402) returned the
  reciprocal: 9.3 degrees where the manual gives 40.5 at qc/sigma'v = 100.
- `cpt_friction_angle_mayne` (Eq. 8-7, p. 400): the vertical stress is
  under a square root; 33.0 degrees became 36.3 at qt 10,000, sigma'v 400,
  Pa 100.
- `fully_softened_friction_angle` (Eq. 8-13, p. 407) had both signs
  reversed: 45.6 degrees where the manual gives 26.8 at PI 40.
- `spt_undrained_strength_stroud_butler` (Eq. 8-26, p. 428) divided where
  the manual multiplies: 4.3 kPa where it gives 93.8 kPa at N 20, PI 30.
- `cbr_from_dcp_nazzal` (Eq. 8-38, p. 456): 9.0 became 11.6 at 20 mm/blow;
  a DCP outside the stated 6.3 to 67 mm/blow is refused.
- `cbr_from_spt` (Eq. 8-39, p. 457) returned about 1e9; the manual gives
  CBR 6.1 at N 10 and 26 at N 30.
- `kozeny_carman_hydraulic_conductivity` (Eq. 6-13, p. 300) and
  `hydraulic_conductivity_kozeny_carman` (Eq. 8-41, p. 462), printed
  identically, returned 7e-8 cm/s and 7.7 cm/s for a sand the equation
  gives 0.072 cm/s; both now return 0.072. Fractions may be decimals
  adding up to 1 or percentages adding up to 100, within 2 % (0.98 to
  1.02, or 98 to 102; the library's tolerance, not printed, there to catch
  percent and decimals mixed up); the total is used as given, not
  normalised, and any other total is refused. A grading summing to 99 %
  is accepted (0.238 cm/s for the two-fraction sand in the tests).
- `hydraulic_conductivity_carrier_beckman` (Eq. 8-42, p. 462): 2.5e-4 m/s
  became 3.5e-9 m/s at e 1.5, PL 25, PI 30.
- `hydraulic_conductivity_benson_landfill` (Eq. 8-43, p. 463) raised an
  overflow error at ordinary inputs; it now gives 3.6e-8 m/s for the
  example in its tests. The page prints no unit for the molding water
  content: the function takes a decimal (a percentage gives k below
  1e-100 m/s) and refuses a degree of saturation above 1.10. The limit is
  the library's, not printed: a little over 1.0 comes from scatter in the
  measured w, dry unit weight and Gs, and the guard is there to catch w
  entered in percent.
- `hydraulic_conductivity_benson_trast` (Eq. 8-44, p. 463) had its four
  coefficients on the wrong terms: 1.5e-8 m/s became 7.9e-11 m/s at PI 25,
  CF 30, standard Proctor, w 0.18, dry unit weight 17 kN/m3, Gs 2.70. The
  page prints no unit for the molding water content. The function takes it
  as a decimal and enters the saturation term in percent; that is this
  review's reading, not a printed statement (as a decimal the same input
  gives 1.4e-7 m/s), and the docstring gives the reasons. A degree of
  saturation above 110% is refused, for the same reason as in Eq. 8-43.
- `well_resistance_factor` (Eq. 5-26, p. 268) was zero at the far end of a
  drain, where the manual's equation is largest: 0 became 1.26 at
  z = Lm = 20, kh/qw = 0.001.
- `drain_spacing_factor(approximate=False)` (Eq. 5-23, p. 267): 0.906
  became 0.936 at n = 5. The default approximation is unchanged.

Tables and charts rebuilt from the print:

- `figure_8_46_f` (Figure 8-46, p. 444) returned 500 to 175; the figure's f
  runs from 6.85 at PI 14.8 (6.78 at PI 15) to 4.24 at PI 64.5, so the
  constrained modulus Mds = f N Pa was 46 to 73 times too stiff, by PI
  (66 at PI 15, 73 at PI 20, 47 at PI 60, 46 at PI 64.5). PI outside 14.8
  to 64.5 is refused.
- `figure_5_6_mu0` and `figure_5_6_mu1` (Figure 5-6, p. 230): mu0 is now
  0.877 at D/B = 5 (was 0.78) and 0.859 at D/B = 20 (was 0.62); mu1 for a
  square load is 0.645 at H/B = 5 (was 0.82, or 0.96 at the old default
  Poisson's ratio of 0.3). The figure is for Poisson's ratio 0.5 only: any
  other value is refused, and the default is now 0.5. `L_over_B` is 1 to
  10 or "infinite".
- `table_8_6_stark_hussain` (Table 8-6, p. 417) now holds the sixteen
  printed rows; the residual friction angle for a clay fraction over 50%
  at 400 kPa and LL 80 is 10.3 degrees (was 26.5). Keys: `lt_20`,
  `25_to_45`, `gt_50_ll_lt_120`, `gt_50_ll_120_to_300`; `700_kPa` added.
- `table_8_9_shansep_m` (Table 8-9, p. 425) lists m by source and soil, as
  the table does, not by test type; it takes `soil` and returns the printed
  row as a dict.
- `table_8_24_cbr_dcp` (Table 8-24, p. 456) now holds the thirteen printed
  rows. Of the six keys it held, only the removed `webster_1992` carried
  printed coefficients: its (292, -1.12) are those of the printed White et
  al. (2018) row for all soils except CL with CBR < 10, now
  `white_2018_all_except_cl_cbr_lt_10`. The other five are not in the
  table.
- `table_4_3_trench_fill` (Table 4-3, pp. 195-196) returns the six printed
  rows (unit weight in pcf, K, mu', K x mu'); for saturated clay K x mu' is
  0.11 (was 0.029).
- `table_4_9_tunnel_behavior` (Table 4-9, p. 205) returns the printed
  ground behavior for the seven printed rows and takes the soil type as a
  second argument.
- `table_5_6_Calpha_Cc` (Table 5-6, p. 254) gains the shale and mudstone
  row (0.03); the table's +/- 0.01 and its source are in the docstring.

Inputs outside the range the manual states or plots are now refused, with
the range and page in the message (values inside the range are unchanged):

- `hydraulic_conductivity_hazen` (Eq. 8-40, p. 458): D10 outside 0.1 to
  3 mm, the range the manual states.
- `fully_softened_friction_angle` (Eq. 8-13) and
  `residual_friction_angle_gibson` (Eq. 8-16): PI above 100, the end of
  Figure 8-13 (p. 408).
- `spt_friction_angle_roads` (Eq. 8-2) and `spt_friction_angle_buildings`
  (Eq. 8-3): N60 above 50, the end of the curves in Figure 8-2 (p. 397).
- `spt_friction_angle_kulhawy_mayne` (Eq. 8-4): N60 above 60, the end of
  the N60 axis of Figure 8-3 (p. 398), or sigma'v/Pa above 3.0. The stress
  axis ends at 3.0 kgf/cm2 (2.90 atmospheres); the limit is taken as
  3 atmospheres, so 291 kPa with Pa given as 100 kPa is answered
  (33.0 degrees at N60 20).
- `spt_undrained_strength_stroud_butler` (Eq. 8-26): PI outside 15 to 62,
  the trendline of Figure 8-31 (p. 428). At PI 5 it returned 1,513 kPa
  for N 20.
- `cbr_from_spt` (Eq. 8-39): N outside 5 to 68, the curve of Figure 8-57
  (p. 458). At N 200 it returned CBR 144,025.
- `spt_friction_angle_wolff` (Eq. 8-5) and
  `spt_friction_angle_hatanaka_uchida` (Eq. 8-6): N1,60 above 60, the end
  of Figure 8-4 (p. 399).
- `schmertmann_time_correction` (Eq. 5-9, p. 232): a time below the
  equation's reference time of 0.1 year.

Coded differently from the print, values unchanged (the docstrings now give
both forms, the pages and the reasons):

- `trench_load_coefficient` (Eq. 4-7, p. 195) has a 2 in the exponent,
  e^(-2 K mu' H/Bd), where the manual prints e^(-K mu' H/Bd).
  `flexible_pipe_trench_load` (Eq. 4-8, p. 197) multiplies by the trench
  width Bd where the manual prints Bc, the diameter of the pipe. Each coded
  form gives the higher pipe load. The review kept the coded forms; the
  library's owner is to revisit them.
- `relative_density_from_dry_density` (Eq. 3-2, p. 141) has
  gamma_d - gamma_d-min in the numerator where the manual prints
  gamma_d - gamma_d-max. The printed form is negative for any soil looser
  than its densest state and so cannot equal the void-ratio form it is set
  equal to; the coded form makes the two sides equal.

Descriptions corrected, values unchanged: the angles of the Table 4-2
strip-load functions (`boussinesq_semi_infinite_load`,
`boussinesq_terrace_load`, `boussinesq_triangular_load`,
`boussinesq_slope_load`) are now described as the table's diagrams draw
them; `corrected_spt_silty_sand` no longer claims a limit of N' = 15 the
manual does not print.

Chapter text (`dm7_1/text/` chapters 3, 4, 5, 6 and 8) now states
Eq. 3-2, 4-7, 4-8, 5-23, 5-26, 6-13, 8-8, 8-13, 8-16, 8-26, 8-38, 8-39 and 8-41
to 8-44 as printed.

**DM 7.2 (UFC 3-220-20, 16 Jan 2025) lookups as printed (review
dm72).** Each was read again from the rendered page; values below are
before -> after at the example input.

- Figure 4-36, Rowe's moment reduction: `figure_4_36_moment_reduction`
  now takes rho itself (5 to 200 in^2/lb) and the soil the wall
  penetrates, and uses the two curves the figure prints. rho 9.5, very
  dense: 0.30 -> 0.687 (the figure's own example reads 0.68). Fine-grained
  and loose soils, for which the figure permits no reduction, are refused;
  `plot_figure_4_36` needs both rho and soil_type for a point.
- Figure 5-18, layered clay N_cm (`figure_5_18a_Ncm_strip`,
  `figure_5_18b_Ncm_circular`): rebuilt from the figure; each returns a
  dict with N_cm and the 10 % reduction where the manual calls for it.
  Strip, su2/su1 0.2, H/B 1.0: 3.80 -> 2.53. Off the chart (su2/su1 above
  2.0) is refused. Top layer stiff, 0.65 < su2/su1 < 1: N_cm stays the
  printed equation's value; `print_note` says the figure's one drawn
  curve there (H/B 0.5; H/2R 0.25) runs up to about 7.5 % below it, and
  `N_cm_drawn_curve` gives that curve's value (strip, 0.85, H/B 0.5: 5.12
  by the equation, 4.74 drawn).
- Eq. 5-11/5-12, circular footing equivalent rectangle: r 1.5, e 0:
  3.760 x 0.940 -> 2.659 x 2.659 (the area was half the printed one).
- Eq. 5-26 `second_layer_thickness`: as printed, (2B - H1)(c1 + tan
  phi1)/(c2 + tan phi2); Figure 5-20's example gives 4.5 ft.
- Table P-6 `usr_dss`: sin phi' - 0.5 sin^2 phi'. phi' 30: 0.067 -> 0.375.
- Eq. 3-9/3-10 (`borrow_volume_from_waste_fraction`, `shrinkage_factor`):
  (1 + X_L), not 1/(1 - X_L); X_L 0.30: 9 % less borrow (1,607 -> 1,462
  in the review's example).
- `p_a` (seven prologue power functions) and `gamma_w` (two chapter 3
  functions) have no default any more (2116 psf and 62.4 pcf gave wrong SI
  answers: 92.06 where 50.13 is right).
- Chapter 6, equations: Eq. 6-48 base resistance at 4 % (fine and coarse
  were swapped: coarse 100 -> 71 % of R_b); Eq. 6-30 N*c (Ir 50: 9 ->
  6.53); Eq. 6-31 N*c (su/Pa 0.5: -10.47 -> 8.13); Eq. 6-49/6-50
  equivalent footing (B 10, z2 4: 14 -> 12); Eq. 6-47 Meyerhof I_f
  (Z/B 6: 0.917 -> 0.5); Eq. 6-22 mean stress (phi' 30: 50 -> 66.7 % of
  sigma'); Eq. 6-23 Vesic N*q (phi' 35, Irr 100: 22.7 -> 83.8); Cheng Nq
  (phi' 35, Z/b 20: 3.93 -> 55.1); Eq. 6-33 LCPC base (qc 10,000, kt
  0.4: 25,000 -> 4,000); Eq. 6-40 group uplift (n 4: 460 -> 490, the
  effective weight now counted per element); Eq. 6-41 uplift block
  (3 x 4 x 10: 240 -> 378); Eq. 6-76 depth to fixity (sqrt 2, not 2:
  20 -> 14.1).
- Chapter 6, tables rebuilt from the page: Tables 6-21/6-22/6-23 (LCPC
  ks, fp/Pa, kt) by the eight printed soil rows and Groups I-A, I-B,
  II-A, II-B; Table 6-18 F_nu by pile shape and Poisson's ratio 0.2 to
  0.5 (square, 0.3: 0.82 -> 0.48); Tables 6-36/6-37 (lateral CLM a and
  n; clay, free head, M_max: 0.55, 0.72 -> 0.855, 1.288).
- Signatures changed: `table_6_18_Fnu(poisson_ratio, pile_shape)`;
  `table_6_21_ks`, `table_6_22_fp`, `table_6_23_kt(soil_type, group)`
  (`table_6_22_fp` returns fp/Pa); `lcpc_unit_shaft_resistance`'s fourth
  argument is fp/Pa; `table_6_36_clm(soil_type, ratio, fixity)`;
  `table_6_37_clm(soil_type, fixity)`; `drag_force_check(Q_d, Q_np, P_r)`
  (the unread `Q_d_drag` removed); `figure_4_36_moment_reduction(rho,
  soil_type)`.
- Printed limits now refused: Eq. 6-15 outside su/Pa 0.24 to 1.42; Eq. 6-1
  below sand size (D50 < 0.075 mm); Cheng Nq below Z/b 5; Table 5-6
  between phi 0 and 10 degrees. Stated, not checked (the function takes
  no such input): Z/b >= 5 for the drained base resistance (Eq. 6-20,
  6-21) and the 20 ft wall limits of Eq. 4-13 and 4-17.
- Chapter text: chapter titles as printed (chapter 2 is "Excavations",
  not "Earth Pressures"); chapter 6 equation descriptions and
  `implemented_in` links corrected; Eq. 3-4 and Eq. 6-15 state their
  printed form beside the coded one.

**Pavement and UFC soils values checked against the printed pages (review
of 2026-11-10, pave-01 to pave-32).** Every changed value was read off the
rendered page; results and docstrings name the page.

- UFC 3-250-01 Chapter 20 drainage: Eq. 20-17 lacked its factor 2 (layer
  thickness H was half the print), Eq. 20-18 had 0.85 in the numerator
  (H was 0.72 of the print), Eq. 20-4 effective porosity computed the water
  retained (0.088 against the printed form's 0.247 at 110 pcf, Gs 2.65,
  We 0.05), and Eq. 20-11 lacked its 2 (T50 twice the print). Eq. 20-3 is
  kept with (1+e) where the page prints (1-e), as it was coded before
  the review; the result and the first docstring paragraph say so and that
  the owner is to revisit the choice. Eq. 20-4 now raises ValueError when
  the inputs give no drainable pore space (We at or above saturation for
  the dry density), where it returned a negative porosity (125 pcf, Gs
  2.65, We 0.2 gave -0.157).
- UFC 3-250-01 Table 5-1 gained its rigid-pavement traffic column
  (`pavement_type='rigid'`; 1 million passes, cohesive 95 %: 11 -> 12 in);
  `pavement_type` is required, since the table prints both columns and no
  default (leaving it out raises TypeError), and both Table 5-1 and 21-2 read each "< n" bound strictly; Table 21-2
  gained its cohesive 80 % column. Table 9-1's asphalt-stabilized rows are
  split as printed (GM base 1.15 -> 1.00; SM subbase 2.30 -> 1.50; SP base
  refused, "not used for base course").
- UFC 3-250-01 Figure 15-1 retraced along every curve (k 450 at 100,000
  passes: F 0.42 -> 0.694); past 10 million passes the value is held with a
  note. Figure 10-1 refuses a subgrade k below 25 pci and notes a hold above
  300 pci or past 60 in.
- AASHTO 1993: Tables 2.4/2.5 `mi_min`/`mi_max` and `cd_min`/`cd_max` the
  right way round (1.35/1.40, was 1.40/1.35; midpoints unchanged);
  Figure 2.5 re-read at 400 dpi: the curve begins on the a1 0.20 line at
  about EAC 106,000 psi and reads 0.252 at 150,000 psi (was 0.26); below
  106,000 psi a1 raises, naming the chart's range (was 0.20 unsaid; the
  app's flexible design raises there too), and past 500,000 psi it holds
  with a note quoting II-17's caution above 450,000 psi. Aggregate loss
  (II-12): the scan drops decimal points, so the Kenya equation's " 092T"
  is .092T and its gravel factors f are .037/.043/.028/.059, not
  0.37/0.43/0.28/0.59 (lateritic, T 2, R 30 in, VC 5: 22.352 -> 2.231
  in/yr); `aggregate_loss_army_corps` is renamed `aggregate_loss_brazil`
  (the print credits a Brazil study; no alias) and the page's first
  equation is added as `aggregate_loss_truck_traffic`, GL = 0.12 +
  0.1223(LT). Figures 3.5 and 3.6 (II-41, II-42) are charts that print no
  equation; `relative_damage_rigid` and `k_loss_of_support` say in their
  first paragraph and a `print_note` that their closed forms are fits
  (values unchanged).
- UFC 3-250-03 Table 6-2 adds the stockpile kerosene amounts (cold 18.8 L
  per metric ton, 4.5 gal per ton, where only 8.3/2.0 was returned and
  called the stockpile amount) and lists the emulsion grades by climate as
  printed; Table 2-8 gives Section 1's VTM for the optimum asphalt content
  (4 for HMA, 6 for sand asphalt).
- UFC 3-250-04 Table 9-1: the range is of the maximum joint spacing
  (`max_joint_spacing_low_ft`/`_high_ft`, renamed) and a 12 in slab is in
  the 9-12 in row (20 ft -> 15-20 ft); Table 3-2 carries footnotes 2
  (1.5 % for crusher dust) and 3 (blast-furnace slag).
- UFC 3-250-11: Table 3-6 rates LL 60 and PI 35 Marginal as printed (were
  High); Table 3-5 holds percent passing No. 200 above 25 at the 25 row
  with a note; Table A-1 carries Sec A-1.1's 4 % cement limit; the
  Table 2-3 footnote (c) PI limit is 20 + (50 - percent passing No. 200)/4,
  the form printed in the 2004 edition's Table 2-1 footnote b (printed
  2-3), where the held 2020 page prints 20 + 50 - P200 with no divisor and
  the code took it literally (25 % passing: 45 -> 26.25); the result's
  `print_note` gives both editions' forms.
- `ufc_backfill` rebuilt from the held UFC 3-220-04FA (16 January 2004) and
  cited to it, which overturns REF-31 (2026-11-06), where the package was
  kept cited to "UFC 3-220-04N", an edition that is not held: open areas 90 %, beneath structures 95-100 % (cohesionless)
  or >= 95 % (cohesive) of CE 55 maximum density, where the old table gave
  ASTM D698 rows (95/90/85 %) the print does not have; new Table 5-1
  compaction criteria and Figure 2-5 compaction-induced lateral pressures.
  Removed (not in the print): `table_drainage_requirements`,
  `compaction_induced_pressure_kPa`, `filter_criteria_check`.
- `ufc_expansive` rebuilt from UFC 3-220-07: Table 4-1's three classes
  (PI 30 -> Marginal, Sp 0.5-1.5 %; was "medium", 4-8 %), para 5-4c's
  active zone (10 ft moist / 20 ft dry, or the water table under 20 ft),
  Table 6-1's foundation systems, and the grade-beam void "6 to 12 inches
  or 2 times the predicted total heave, whichever is larger" (a 4 in heave
  gives 8-12 in; was 100 mm for a "high" class). Removed (not in the
  print): `activity_index`, `free_swell_percent`, `swell_pressure_kPa`,
  `pier_minimum_embedment_m`. Added: Table 4-2's four empirical swell
  relations as printed (Vijayvergiya and Ghazzaly, Schneider and Poor,
  McKeen-Lytton, Johnson; printed 4-3). Johnson's relation can give a
  negative number (PI 20, H 0, wo 40: -8.648); it is returned with a note
  that it is not a predicted shrinkage.

**Structural lookups checked against the print (review of 2026-11-10,
struct-01 to struct-34).** Values that change:

- UFC 4-023-03 Table 4-1, RC beams controlled by shear, development or
  embedment (`ufc_collapse.table_4_1_beam_other_modeling`): the
  acceptance-criteria plastic rotations are the printed ones, no longer
  equal to a and b. Shear, stirrups <= d/2: primary 0.003 -> 0.002 rad,
  secondary 0.02 -> 0.01; stirrups > d/2: 0.003 / 0.01 -> 0.002 / 0.005;
  inadequate embedment: 0.015 / 0.03 -> 0.01 / 0.02 (printed p. 63).
- GSA Alternate Path Tables 6 and 8 (`gsa_collapse.table_6_beam_*`,
  `table_8_slab_*`): GSA prints one acceptance column for primary and
  secondary components; both now return it (new key `acceptance`).
  Table 6 equals b in every row, so every primary value moves from a to
  b: conforming, (rho-rho')/rho_bal <= 0, V ratio <= 3, 0.063 -> 0.10 rad;
  shear, stirrups <= d/2, 0.003 -> 0.02 (printed p. 39). Table 8: with
  continuity reinforcement, Vg/Vo <= 0.2, primary 0.05 -> 0.10 and at
  >= 0.4 0.0 -> 0.08; without, Vg/Vo <= 0.2, 0.015 -> 0.020 (both);
  development 0.0 / 0.01 -> 0.02; embedment 0.01 / 0.02 -> 0.03 (printed
  p. 41).
- EM 1110-2-2107 Table 4.1 (`em_2107.loads.table_4_1_load_factor`): the
  self-straining load T has the printed principal factor 1.2 in every
  category; it raised an error before (printed p. 27).
- Steel connection m-factors and plastic rotations printed as c0 - c1 d
  (UFC Tables 5-1/5-2, GSA Tables 10/11, eight functions): d and dbg are
  inches, named in the docstrings and results (`d_units`, `dbg_units`).
  An entry whose printed expression is zero or negative at that depth is
  None, with a `note` naming the entry, its expression and the depths at
  which it is positive; the row's other entries are returned, and the
  call is refused only when every entry is zero or negative (a 30 in WUF
  beam typed as 762 gave UFC m = -58.9; now ValueError). A UFC WUF beam
  51.8 to 89.6 in deep returns its printed secondary m-factor with
  `m_primary` None. An m-factor between 0 and 1 is returned with a
  `note`.
- EM 1110-2-2107 `bolt_grade_check` refuses a grade the manual does not
  name (it answered "not permitted", even for "A325"). The print's own
  spelling, "ASTM 3148" (printed p. 38), gets a message naming the grade
  to pass, 'ASTM F3148'.
- UFC 3-301-01 Eq 16-18a/b (`ufc_structural.wind_speed_conversion_asd`,
  `wind_speed_conversion_fastest_mile`): Vasd = sqrt(0.6) V and Vfm =
  (sqrt(0.6) V - 10.5)/1.05, the radical over 0.6 only as typeset. The
  code took the root of 0.6 V: at V = 150 mph it returned 9.49 and
  -0.96 mph; now 116.2 and 100.7 mph (printed p. 19). The chapter 2 text
  stated the same wrong form and is corrected.
- UFC 3-301-01 Tables 3-1, 7-1 and B-1 (`ufc_structural.table_3_1_*`,
  `table_7_1_*`, `table_b1_*`): height limits are returned as
  `height_limits_ft` (was `height_limits`, no unit), with
  `height_limits_m`: footnote d's 30 m for 100 ft and 50 m for 160 ft in
  Tables 3-1 and 7-1, None for a height the print gives no metric value
  for (35, 40, 65 ft, and every Table B-1 height). `metric_footnotes`
  gives the row's cited footnotes that print a metric height (Table 3-1
  i "45 ft (14 m)", j "60 ft (18 m)", q "60 ft (18.3 m)"; Table 7-1 w
  and Table B-1 footnote 7 "60 ft (18.3m)"); the notes cite "FOR SI: 1
  foot (ft) = 304.8 mm" under Tables 3-1 and 7-1 and footnotes e and f
  (240 ft, 75 m; 160 ft, 50 m) (printed pp. 56-57, 99, 124-126).
- EM 1110-2-2107 Eq 4.3 (`em_2107.seismic_amplification.westergaard_pressure`): the
  printed 7/8 is applied, p = (7/8) wc ac sqrt(H y); 62.4 pcf, ac 0.5,
  H 100 ft, y 50 ft gives 1930.4 psf (was 2206.2; printed p. 28). The
  chapter 4 text is corrected.
- EM 1110-2-2104 Eq 3-5 (`em_2104.loads.earthquake_load_combination`):
  the docstring said every combination takes the factored permanent sum;
  Eq 3-5 is U = 1.0 Sum Lp + 1.0 EQ + 1.0 Ltc (printed p. 26). The result
  adds `permanent_sum_basis`. Following the old docstring, D = 100 with
  EQ = 50 gave 170 instead of 150.
- UFC 3-301-01 Eq C-1 (`ufc_structural.rigid_pipe_fundamental_period`):
  the print gives L = sqrt(C pi Ta sqrt(E I_g / w)) and defines neither g
  nor I_g; read as E x I x g (I the pipe's moment of inertia, g gravity,
  confirmed by Table C-1), Ta = L^2/(C pi) sqrt(w/(E I g)). The code had
  C L sqrt(w/(E I g)) and called spans to
  about 757 ft rigid. New keyword `g` (386.4 in/s^2 default). A 1 in.
  40S steel pipe at Table C-1's 7 ft 0 in gives Ta 0.059 s, rigid, and
  8 ft is not (printed pp. 137-138).
- Wood Handbook combined bending and axial load, compression
  (`wood_handbook.combined_bending_axial_stress`,
  `eccentric_bending_axial_stress`): a compressive P adds P/A on the
  concave edge and P e0/S to fb0. Example: concentric 14.5 / 10.5 ->
  10.5 / 14.5 (edges were swapped); eccentric 13.25 / 9.25 -> 11.75 /
  15.75 (printed p. 9-12).
- Wood Handbook Figure 9-14 (`wood_handbook.figure_9_14_coefficients`):
  traced off the rendered figure (printed p. 9-12). At a/h 0.1, At / Ac
  / B = 0.177 / 0.074 / 0.277 e-4 (was 0.05 / 0.03 / 0.35 e-4); A was
  too low below a/h 0.3 and 20-55 % too high above 0.4. a/h below 0.02
  is refused (the curves meet at the origin). Example: Eq 9-21 criterion
  0.90 (no crack) -> 2.17 (crack).
- UFC 4-023-03 and GSA Alternate Path gravity loads (`*_collapse.
  alternate_path`): live and snow load together are refused; both
  documents print 1.2 D + (0.5 L or 0.2 S), and the code added both.

Judgment calls where the printed equation cannot be right as typeset
(ruled by the lead, 2026-11-10; each function's first docstring
paragraph and its result give the printed form, the form used, the page
and the reason):

- Wood Handbook Eq 9-24 (`torsional_shear_stress_rectangular`): printed
  fs = T/(beta h b^2); used fs = beta T/(h b^2), because Figure 9-15's
  beta (3 to 4.8) is the classical multiplier. 100 x 100 mm, T = 1 kN m:
  0.208 -> 4.81 MPa (printed p. 9-13).
- Wood Handbook Eq 9-32 (`critical_ponding_spacing`): the print defines
  rho as "density of water (1,000 kg m-3, 0.0361 lb in-3)"; the SI
  default is now the unit weight 9,810 N/m^3 (1,000 gave s_cr 9.81 times
  too large). The parameter is renamed `unit_weight_water` (was
  `rho_water`, no alias; the result key follows), and a value from 900
  to 1,100 is refused as a mass density (printed p. 9-15).
- Wood Handbook Eq 9-41 (`elastic_buckling_stress_edgewise_bending`):
  printed (1.44 E/le)(d2/d1) is not a stress; used 1.44 E d2^2/(le d1)
  (printed p. 9-17).
- EM 1110-2-2107 Appendix F (`hydrostatic_horizontal_component`,
  `resultant_angle_from_horizontal`, `trunnion_reaction_force`): values
  unchanged; the docstrings now state that Eq F.10's typeset sign,
  theta_p = tan^-1(Ph/Pv) and theta_Rt = tan^-1(Rtx/Rty) contradict the
  worked example and its tables, which the code follows (printed pp.
  427, 436, 440, 445). For Eq F.10 only the integral's form gives Table
  F.3's Ph = 50.0; the typeset form gives -50.0 and the worked example's
  own displayed equation 30.0. `trunnion_reaction_force` returns the
  magnitude of theta_Rt: the example computes +0.2653 from Rtx = -1,336
  and Rty = -363.0, and Table F.8 lists the components unsigned beside
  -0.2653 without saying what the sign means.

Labels, units and citations (no value changes):

- EM 1110-2-2107 Eq 10.2-10.14 (`em_2107.tainter_gate_loads`): each
  description is the printed load-combination heading. Eq 10.7 is Load
  Combination 3, gate operated by two hoists (it said "gate jammed");
  Eq 10.8 is one hoist; Eq 10.9 is the jammed gate, an extreme load
  (gamma_pr = 1.3) as are Eq 10.4 and 10.11 (they said "unusual").
- RC beam flexure tables (UFC 4-1/4-2, GSA 6/7): V/(bw d sqrt f'c) is in
  psi units (an SI ratio is 1/12.04 of it and read the highest-m row);
  results return `vw_ratio_units` and the printed row read.
- EM 1110-2-2104: every parameter of the flexure, design and shear
  functions has its own description with its unit (flexure and design in
  ksi and inches, shear in psi and lbs); `aci_beta1` says f'c is ksi or
  psi, not MPa.
- Page citations: EM 1110-2-2104 Table 3-2 pp. 24-25 (was 23-24),
  Eq 4-3 p. 30 (was 29) and Eq 4-1/4-2 pp. 29-30 (was 29); UFC Eq 3-6
  p. 24 (was 23); Wood Handbook Table 5-3a pp. 5-4 to 5-8 (was 5-5 to
  5-8).
- GSA chapter 4 text no longer says Tables 6/7 are identical to UFC
  Tables 4-1/4-2.
- More page and equation citations: EM 1110-2-2107 para 5.2.1.1 (was
  5.2.1.2), Eq D.8 p. 392 (was 400), `amplification_factor` is Eq D.8
  (was D.10, its top-of-structure case), the trunnion Rt / Ft / Mt
  functions cite paragraph F.4.2.4's unnumbered equations (were "F.17",
  the QT equation); Wood Handbook Eq 9-3/9-4 p. 9-2, Eq 9-10/9-11 p. 9-5,
  Eq 9-16 p. 9-10, Eq 4-6 p. 4-3, Eq 4-15/4-16 p. 4-12.
- `ufc_collapse.effective_wf_for_nonuniform_load` adds `case` and
  `action`: when the bay loads differ by 25 % or less but the max-load
  area is over 25 %, the print allows only the maximum floor load
  (sub-areas are for a difference over 25 %).
- Docstrings that misstated the print: EM 1110-2-2104 Eq B-33 is clean on
  the page (not "corrupted"); in Appendix C-3 the compression steel does
  not yield (the printed 0.0148 is the tension-steel strain); Eq B-53's
  typeset form is a misprint the code does not follow; GSA Icr 19160
  gives 325.46 kip/in, 16423 gives 279; GSA Eq 3.18's Phi is left out by
  default, as Figure 3.19 and Appendix D do; UFC 3-301-01's tie-rod
  "118 kN" for 40 kips is a misprint (178 kN), noted in the result; Wood
  Handbook Eq 4-3's printed anchors (267 % / 44 %) fit a cell-wall
  specific gravity of 1.5, not the printed 1.54.
- More wording from the print: GSA Tables 6 and 8 footnote 2 applies the
  one acceptance column to primary and secondary components "where the
  full backbone curve is explicitly modeled"; UFC 3-301-01 commentary
  [C] 503.12 is on printed p. 84, the page after the normative text; Eq
  16-18b prints 10.5 with no unit; EM 1110-2-2104 Eq D-6's moment is
  M_DS as printed (was "MDL"; the result key stays `mdl`).

**Build: the heave methods UFC 3-220-07 prints (app backlog REF-91).**
`ufc_expansive` now holds the manual's printed ways to predict heave, in
place of the removed correlations, each read off the rendered page:

- `figure_4_1_potential_expansiveness`: Van Der Merwe's potential
  expansiveness PE (0, 1/4, 1/2, 1 inch/foot) from the PI and clay
  fraction of the whole sample, Figure 4-1 (printed 4-2), its regions
  taken at the labelled axis ticks; outside the frame (70) refused. The
  drawn lines sit up to about 0.8 % clay and 0.6 PI off the ticks and the
  chart's PI marks agree only to about 0.5 PI, so the result says a point
  within about 1 % clay or 1 PI of a boundary may lie in the next region.
- `eq_4_1_van_der_merwe_heave`: total heave at the ground surface,
  delta_H = sum of 10^(-D/20) x PE over 1-ft increments, Eq. 4-1 (printed
  4-1); 10 ft of very high soil gives 5.604 in.
- `eq_5_2_potential_vertical_heave`: N x DX x sum (ef - eo)/(1 + eo),
  Eq. 5-2 (printed 5-2), N from 1/3 to 1 (0.33 or 0.333 is taken as 1/3,
  and the result says so); one element is Figure 4-2's
  Sp/100 = (e1 - eo)/(1 + eo).
- `eq_5_3_to_5_5_equilibrium_pore_water_pressure`: the saturated,
  hydrostatic I and hydrostatic II profiles, gamma_w 0.0312 ton per cubic
  foot (printed 5-3 to 5-4).
- `eq_5_8_consolidometer_heave`: delta_H/H = cs/(1 + eo) log(sigma_s /
  sigma'_v) with sigma'_v = sigma_v - u_w, Eqs. 5-8 and 5-9 (printed 5-5),
  "log" taken as log10 (Figure 4-2's log pressure axis). A u_w left out is
  taken as 0, the saturated profile the print says to use when nothing
  else is known, and the result names those layers with p. 5-3's
  sentence. A layer past its swell pressure gets no magnitude (heave
  None, flagged, listed in `layers_left_out`): p. 4-4 says only that net
  settlements will occur, and c_s, the slope from the seating to the
  swell pressure, does not give them; the total is over the swelling
  layers.

No stored statement changed; the package keeps no chapter text.

**Build: figure catalog rows for printed figures that had none (app backlog
REF-08, REF-84).** A figure without a catalog row can be neither found by
`figure_search` nor read by the app's vision tool. 428 rows were added and
no existing row changed:

| Catalog | Rows before | Added | After | Figures added |
|---------|-------------|-------|-------|---------------|
| `gec_5` | 256 | 93 | 349 | 11-10 to 11-26, chapters 12 and 13, Appendix 2 (A2-1 to A2-40) |
| `gec_13` | 33 | 206 | 239 | chapters 2-5 (Vol I) and 7-10 (Vol II) |
| `fhwa_soils_foundations` | 331 | 60 | 391 | Appendix A (A.1-1 to A.9-1), D-10 |
| `gec_6` | 57 | 29 | 86 | Appendices B and C (B1-1 to B5-2, C1-1 to C2-4) |
| `gec_4` | 73 | 17 | 90 | Appendices A, B and D (A-1 to A-10, B-1 to B-5, D-1, D-2) |
| `gec_7` | 78 | 11 | 89 | 3.22 and Appendices A, B, C and G |
| `micropile` | 132 | 10 | 142 | the sample problems' S1-1 to S1-7, S2-1 to S2-3 |
| `eurocode_7_2` | 19 | 2 | 21 | Annex B's B.4 and B.5 |

- Each row points at the page that prints the figure's label and caption
  and holds a picture or drawing; one row in five, by a seeded draw, was
  looked at on the rendered page. The caption is the one printed under the
  figure, where a List of Figures words it otherwise (GEC-5 12-24, GEC-13
  4-17). Captions whose symbols the text layer garbles were typed from the
  page (GEC-5 "su/σ′vc").
- Figures printed turned on the page carry `read_notes` saying which way to
  turn it: GEC-5 A2-6 and A2-9; FHWA NHI-06-089 A.2-9 to A.2-12 and A.4-3;
  micropile S1-2, S1-6 and S1-7.
- Placed by hand (`--overrides`) where the scan cannot: FHWA A.2-3 and
  GEC-6 B3-4, typed text in a box with no picture; FHWA A.7-2, filed under
  the number its text cites though its caption prints "A7-2"; EN 1997-2
  B.5, whose text layer reads "Figure B.S".
- Descriptions come from the chapter text that cites the figure; appendix
  figures, which have no chapter text, have none, as the appendix rows
  before them.
- `scripts/build_figure_catalog.py --add-missing <package>` finds the rows
  and adds them without touching the others (`find_missing`, `add_rows`);
  the full build is unchanged. Tests: `tests/test_catalog_added_rows.py`.

**Fixes from the 2026-11-10 review of the core layer.** Every page, number
and caption below was read off the rendered print.

- **A section number names one section** (core-01, core-08). Twenty-two
  numbers were held by two sections of one reference, and the two fetch
  layers returned different ones. GEC-13 chapter 1 is now numbered
  `1.<printed number>`, the AASHTO 1993 Guide's numbers carry their Part
  (`II-2.3.5`), and UFC 3-250-11's appendices are `A-1`, `B-1` and `C` as
  printed. Both fetches refuse a number two sections hold, and a
  `section_id` that is not text (7.10 sent as a number arrived as 7.1).
  - A GEC-13 number that chapter 1 prints names chapter 1's section, in
    both fetches. "8.2.7" still returns chapter 8's Jet Grouting, with a
    note that chapter 1 prints 8.2.7 too, as `1.8.2.7` Step 7: Consider
    Project Risks (p. 1-46). The error for "1.3" names `1.1.3` Focus and
    Scope (p. 1-4) first.
- **A figure number the catalog holds twice is never the first row**
  (core-02). `figure_get` and `resolve_pdf` take `pdf_page_index`, and a
  repeated number is refused without it, naming each row's page. GEC-11
  Figure 5-11 had been catalogued as a second 5-14, and GEC-12's Appendix D
  continuation sheets each had the first sheet's page.
  - `figure_search` gives a figure printed over several pages one hit: its
    best-ranked sheet, with `pages` listing each sheet's `pdf_page_index`
    and `printed_page` (GEC-12 D-1 to D-4, UFC 3-250-01 D-3). Rows of one
    number with different captions stay apart (UFC 3-250-01 F-21, GEC-13
    6-14). Before, the sheets took the places of other figures, so
    "driven pile design process flow chart" lost GEC-12 Figure 7-32 from
    its top ten. A list no figure repeats is unchanged.
- **`_linterp` refuses a NaN or infinite input** (core-04).
- **Search results say how they matched** (core-05). `reference_search` and
  `figure_search` hits that do not hold every word carry `match`
  (`"synonyms"`, or `"any word"` with `lacks`). A hit with every word but
  not a phrase of the query (a hyphenated term runs as the phrase of its
  parts: "5-2" as "5 2") is `"all words"` with `not_as_phrase`; it had been
  "any word" lacking nothing. This is worked out after the ranking, so no
  hit moves. With `max_chars` the result adds `matched` (the loosest mark:
  any word, synonyms, all words), `words_not_found` and a sentence on the
  note. An empty result names the scope, what was tried and the words
  nothing there holds.
- **An unknown reference or chapter is an error, and a reference name means
  one thing** (core-06, core-09). A search scoped to either returned `[]`.
  A figure lookup no longer reads a loose name ("FHWA", "pile") as every
  catalog it touches.
  - Both searches read a `reference` by one rule
    (`_retrieval_db.search_scope`): the id, another spelling of it
    (`GEC-10`), or a report number its files carry. A volume's own number
    searches that volume alone: `FHWA-NHI-06-089` is Soils and Foundations
    Vol II, and the result adds `report_number` and a note naming the id
    that searches every volume. Before, `figure_search` read the number as
    the whole manual and `reference_search` refused it. A name that is not
    an id adds `resolved_reference` in both.
  - `"dm7"` (the app's name for UFS 3-220-10 and UFC 3-220-20) is refused by
    both searches with the same error naming `dm7_1` and `dm7_2`;
    `figure_search` had searched both. `figure_get` still reads it by the
    figure asked for.
  - Every `figure_search` and `reference_search` hit carries
    `reference_id`, its volume's report number, so the plain list shows the
    volume a report-number scope kept to (only the `max_chars` form carries
    the note). `references_agent.reference_search` returns the `max_chars`
    form (14,000 characters, the app's size) and takes `offset`. It was a
    plain list of hits, which could not carry the scope note.
  - A report number matches by its designation as well as by the whole
    stored text. That is the text up to the first space after the number,
    and a standard's number with or without its year. So "FHWA-NHI-05-037"
    names fhwa_pavements (stored with its title after the number) and "EN
    1997-1" names eurocode_7_1 (stored as EN 1997-1:2004); both had been
    refused. Every stored id's designation resolves in both searches. A
    number that ends more than one designation is refused, naming them:
    "2-2007" (EN 1997-2:2007 and UFC 3-220-07) had searched both catalogs.
  - Every function that takes a reference reads it the same way:
    `reference_get`, `retrieve_section`, `search_sections`,
    `list_chapters`, `load_chapter`, `figure_get`, `resolve_pdf` and the
    agent's `lookup_reference`, as the searches do. `reference_get("gec12",
    "7.2")` had been refused. An unknown name, or `dm7` in a text fetch,
    gets the search's refusal, with each function's own error type (`KeyError`,
    or `FileNotFoundError` in `_retrieval`).
- **`search_sections` with no section holding every word** (core-07) returns
  the ranked search of that reference, each hit marked `match` ("all
  words", "synonyms", "any word" with `lacks`), 10 by default. The fitted
  result has no `total_hits`. A search that finds hits lists the same
  sections, except that hits of equal score are ordered by section id, so
  they reorder where core-01 renamed ids: `search_sections("aashto_1993",
  "layer coefficient")` ranks 5-7 and `search_sections("ufc_stabilization",
  "sulfate")` ranks 7-10.
- **A skipped local pack is named** (core-10). `list_indexed_references`
  gives a partly skipped pack its `problems`. It lists a pack skipped whole
  with no sections and its problems, and a search naming that pack quotes
  them. A manual whose volumes' files carry titles of their own is listed
  once, with `reference_titles`.
  - A pack folder named as a built-in reference (`gec_12`) has its problems
    filed under its path, not on the built-in's listing.
- **A database knows what it was built from** (core-11). Both search
  databases store a signature of their source files and are rebuilt when it
  differs. Before, a chapter file or catalog that was deleted, added or
  restored with an older date kept the old text. The text layout version
  is 4 (each section row stores its chapter file's `reference_id`); the
  figures database has `user_version` 1.
- **An unreadable built-in source fails the build** (core-12), naming the
  file and keeping the database already there. A local pack's file is still
  skipped and named.
- **Each volume is cited by its own cover's number** (core-13). GEC-11 Vol
  II rows are FHWA-NHI-10-025, GEC-12 Vol III rows and Appendix D are
  FHWA-NHI-16-064, and Soils and Foundations Vol II rows are
  FHWA-NHI-06-089. GEC-13 chapter 6's title says Volume II. GEC-12 Vol II's
  rows and chapters 9-18 are FHWA-NHI-16-010, the number on its Technical
  Report Documentation Page; its cover prints Vol I's 16-009, taken as a
  misprint, and a figure lookup by either number still finds them.
- **`load_chapter` finds a chapter file by its `chapter` field** (core-15),
  so the 17 files named otherwise (prologues, appendices, Eurocode 7 Part 2
  sections) load. A missing chapter's error lists the chapters in numeric
  order (it gave UFC 3-250-11's as "6, 7, 8, 1, 2, 3, 4, 5").
- **Catalog rows lead to their figure.**
  - Pages corrected: UFS 3-220-10 Figures 1-13, 3-1, 5-4, 6-9 (the figure
    is on the page before its caption), GEC-10 4-5, GEC-14 A-1 to A-3 and
    GEC-9 6-17.
  - Numbers as printed: UFC 3-250-01 C14-5B, and D-3 as four sheets.
    `figure_get` reads a bracketed part letter, so "Figure 9-37(a)" finds
    `9-37a`.
  - Chapters filled in: GEC-7 and GEC-8 rows had none, and GEC-4 rows had
    their own figure number as the chapter.

**Build of 2026-11-10: GEC-10 chapters 6 (Rebar Cages) and 8 (Drilled
Shaft Design Process) rewritten from the print (app backlog REF-81).** The
review found 9 of the 12 sections of chapter 6 and 2 of the 3 of chapter 8
written from memory. Both chapters now hold the printed sections in the
print's own wording, with a `[p. 6-5]` marker where each printed page
starts; Tables 6-1, 6-2, 6-3 and 8-1 to 8-4 and Eq. 8-1 are typed in from
the rendered pages, and each figure and table is listed under the section
that prints it. Printed Section 8.1 (pp. 8-1 to 8-17, Blocks 1 to 22 of
Figure 8-1) is over the tools' size limit and is stored as 8.1 and parts
8.1.a to 8.1.d (the letters are not printed). Statements that changed:

- 6.3: "maximum bar spacing should not exceed 6 inches" is gone. The print
  (p. 6-5) gives a minimum: clear distance not less than the greater of
  five times the maximum aggregate size and 5.0 in. (AASHTO Art.
  5.12.9.5.2); eight times the aggregate for tremie concrete (Dees and
  Mullins, 2005); where tremie placement is anticipated, many agencies
  require 5 in. and at least ten times the aggregate.
- 6.4: the unprinted spiral limits (3 in. minimum and 6 in. maximum pitch,
  No. 3 at 12 in., bar size by shaft diameter) are gone. Printed: a pitch
  under 5 in. causes flow problems (p. 6-8), Caltrans' bundled hoops give at
  least 5 in. clear, and the ACI development length is 0.04 A_b f_y/[(f'_c)^0.5]
  (p. 6-7). Transverse bar sizes for handling are in 6.7 (p. 6-17): No. 5
  from a 4 ft cage, No. 7 and No. 8 at 8 ft.
- 6.5: the unprinted 2 ft minimum lap and 125 % couplers are gone; printed:
  not more than 50 per cent of the splices at any one level (p. 6-9).
- 6.8 and 6.9: sizing hoops are fabrication guides spaced 8 to 10 ft
  (p. 6-17), not cover spacers; the cover is 3, 4 and 6 in. for shafts up to
  3 ft, between 3 and 5 ft, and 5 ft and larger, and the annular space at
  least five times the largest coarse aggregate (p. 6-18), where the old
  text said "typically 3 inches".
- 6.6, 6.7, 6.10, 6.11: statements the pages do not make are gone (precast
  column pockets, anchor bolts, storage on blocks, a required lifting
  analysis); the printed limits are stored: shaft cover around 6 in. and a
  shaft 6 in. larger than the column, No. 15 gauge tie wire as the minimum,
  internal bracing at a length to diameter ratio of 8 or more with No. 8
  bars, rigging connections at a factor of safety of 2 or more, Table 6-3.
- 8.1: the blocks are the printed Blocks 1 to 22 (Block 16 is plans and
  specifications; construction is Blocks 17 to 22); Tables 8-1 to 8-3 are
  typed in beside Table 8-4.
- 8.2: "minimum 5-10 load tests required" is gone: p. 8-17 gives no number.
  It says fitting to the ASD factor of safety is an interim approach and
  points to Allen et al. (2005) for the calibration steps.

Tests: `tests/test_gec10_ch06_ch08_printed.py` (64).

**FHWA lookups corrected against the print (review of 2026-11-10, findings
gec-NN).** Each lookup below now returns what its cited page prints. A key
that names no printed row, or more than one, is refused with the printed
rows instead of being answered from the first row that contains the words.

- **Micropile manual (FHWA-NHI-05-039).**
  - `figure_5_23_limiting_lateral_modulus` (Figure 5-23, p. 5-70): three
    bars were wrong. The 9.625"x0.47" 80 ksi casing is 71 psi (490 kPa; it
    returned 1096 kPa, the 7"x0.73" casing's value); hollow bar 73/53 is
    165 psi (1138 kPa; was 2414) and 103/51 is 350 psi (2413 kPa; was
    1138). The 7"x0.73" casing and the #20 bar are added. The result now
    carries the printed psi, the page and the rule of p. 5-68 (no further
    buckling check when Es LIMIT is less than the soil's Es); the docstring
    had the rule reversed. '5.5', '8', '10' and other partial keys are
    refused (gec-03).
  - `table_4_2_rebar_properties` (Table 4-2, p. 4-27): the yield strength
    is the printed column (#18 Grade 520: 1335 kN, was 1342.1; #8 Grade
    420: 211 kN, was 214.2) and the size is the printed 19 to 63 mm. Grade
    550 is the one printed bar, 63 mm (2.5 in), 1747 kN; Grade 550 #14 and
    #18, which the table does not print, are refused (gec-28).
  - `table_5_8_epsilon_50_stiff` (Table 5-8, p. 5-56): the value of the
    printed range, not an interpolation between ranges (su 75 kPa: 0.007,
    was 0.006; 150 kPa: 0.005, was 0.0045; 200 kPa: 0.005, was 0.004). The
    table has no row for 200 to 300 kPa; a strength there is refused
    (gec-18).
  - `table_5_10_soil_modulus_k_clay` (Table 5-10, p. 5-56): the cyclic k
    of soft and medium clay, which the table leaves blank, is refused (it
    returned the static 8140 and 27150 kPa/m) (gec-19).
  - `table_5_11_fixity` (Table 5-11, p. 5-58): the three columns in the
    print's words, with "300 mm or less" and "600 mm or more" and the
    footnote; `table_5_12_elastic_modulus` says where its two sand rows
    differ from the table's kPa column; the values held there, 29,000 -
    48,000 and 48,000 - 76,000 kPa, are the kPa the table prints for 600,
    1,000 and 1,600 ksf in its other rows (the note said "48 kPa per ksf",
    which gives 28,800 and 76,800) (gec-47).
  - `table_4_5_pipe_properties` (Table 4-5, p. 4-33): values unchanged.
    The table prints no Fy column; note (4) reads "Fy = 241 MPa (36 ksi)",
    and 36 ksi is the 248 MPa the lookup returns for ASTM A519/A106 and
    the table's printed yield strengths imply (the 139.7 x 12.7 row's
    1,270 kN implies 250.6 MPa). A519/A106 results now carry a
    `print_note` saying so and every result a `fy_basis` naming the note
    (gec-47, lead's ruling).
- **GEC-12 driven piles (FHWA-NHI-16-009 Vol I).**
  - `table_7_2_resistance_factor_field` (Table 7-2, p. 226): a key names
    one row. "static load test" and "dynamic testing" alone, which each
    returned the combined row's 0.80, are refused; a static load test
    without dynamic testing is 0.75 and dynamic testing of two piles per
    site condition 0.65, as printed (gec-04).
  - `table_7_16_soil_setup_factor` (Table 7-16, p. 299): mixed soils reach
    their own row. "silty clay" is Silt - Clay, recommended 1.0 (it
    returned Clay's 2.0); "sandy clay" is Sand - Clay, 1.5 (was 2.0);
    "silty sand" is Sand - Silt, 1.2 (was Silt's 1.5). The result names the
    row and carries the table's footnote and site counts (gec-05).
  - `table_7_11_eslami_fellenius_cs` and `figure_7_9_delta_phi_ratio`: a
    name that fits two rows or curves ("silt", "pile", "taper") is refused;
    `table_7_3_static_analysis_methods` refuses an unknown soil type
    instead of returning an empty list (gec-45, gec-37).
    `table_7_8_api_design_parameters` (Table 7-8, p. 253): a friction angle
    between the printed rows (15 to 35 degrees, by density class and soil)
    is still interpolated, and the result now says the interpolation is
    not printed (gec-45).
  - `table_7_10_brown_method_factors` (Table 7-10, p. 260): for
    compression in gravelly sand to boulders and in rock the table prints
    Bb equal to Ab (0.888 and 2.89 ksf/bpf); Bb is now 0.0, as the matching
    tension rows print it, and the result carries the printed value and a
    `print_note` (lead's ruling). At N60 = 30 in gravelly sand to boulders
    Eq. 7-21 now gives fs = 0.89 ksf (was 27.5, against Table 7-8's 2.4 ksf
    limit). The vibratory rows (Fvs 0.68) are answered under tension, where
    the table prints them; a vibratory compression lookup, which returned
    them, is refused (gec-06).
- **GEC-13 ground modification (FHWA-NHI-16-027 Vol I).**
  - `table_3_1_lightweight_fill` (Table 3-1, p. 3-1): rebuilt from the
    print, with the specific gravity column. Four of eight rows change:
    Tire Shreds 37 to 73 pcf (was 37 to 55); Cellular Concrete 20 to 80
    (was "Foamed Concrete" 24 to 55); Expanded Shale, Clay, and Slate 37 to
    65 (was 40 to 65); Expanded Air-Cooled Slag 69 to 94 (was "Blast
    Furnace Slag" 60 to 75). The `notes` field, whose statements the table
    does not print, is gone (gec-07).
  - `table_1_3_by_function` (Table 1-3, pp. 1-15 to 1-16): the ten printed
    functions with their printed technologies and comments. Increase
    drainage, accelerate consolidation, provide lateral stability and
    increase resistance to liquefaction listed technologies the table does
    not (earthquake drains, vacuum consolidation, compaction grouting) and
    left out ones it does (jet grouting for liquefaction); "decrease
    imposed loads" and "transfer embankment loads" were missing (gec-09).
  - `table_1_2_applicability`: two rows completed (gec-46). The eight
    filter lookups (`table_1_2`, `1_3`, `1_6`, `2_1`, `3_1`, `4_3`, `8_1`,
    `8_6`) refuse a filter that matches no row, naming the rows,
    instead of returning an empty list (gec-37). Table 1-2's and Table
    1-6's names as printed: "PVDs, with and without fill preloading"; Table
    1-6's two lightweight fill rows in full (Granular Fills was shortened to
    four materials); Table 1-2's compressible columns "All soil types except
    very soft soils low undrained shear strength" (the code added "with").
- **GEC-6 shallow foundations (FHWA-SA-02-054).** The three chart lookups
  are rebuilt from the rendered pages; the points read are in the comment
  above each data block.
  - `figure_5_19_hough_bearing_capacity_index` (Figure 5-19, p. 91): the six
    curves under the chart's own names, clean uniform medium sand highest
    and inorganic silt lowest. The old names of the four upper curves were
    not the chart's and their values were other curves' or no curve's:
    well graded silty sand and gravel at N' = 32 is 109 (the manual's own
    example reads 110; it returned 97), clean uniform medium sand at N' =
    40 is 176 (was 138), inorganic silt at N' = 50 is 84 (was 78). The
    curves start at N' = 4 (N' = 0 returned C' = 0) and the three upper
    ones leave the chart at N' = 56, 75 and 89; outside its curve a value
    is refused. 'coarse_sand' and 'clean_fine_to_medium_sand', which are
    not curves of the chart, and 'sand', 'gravel', 'silty sand' are
    refused (gec-01).
  - `figure_4_1_relative_density_spt` (Figure 4-1, p. 34): the 80 to 100 %
    curves were far right of the print. N = 30 at 1 k/ft2 is on the 100 %
    curve (it returned 87.5 %); N = 24 at 0.58 k/ft2 is 97 % (was 90). The
    curves are read from 0.25 to 6 k/ft2 (12 to 287 kPa); the chart draws
    them from 0, and the refusal below 0.25 k/ft2 is the library's, as the
    docstring and the message say. A point left of the 15 % curve or right
    of the 100 % curve is refused; it returned 15 or 100 (gec-10).
  - `figure_4_2_friction_angle_from_density` (Figure 4-2, p. 35): the
    printed mesh of relative density lines between the ML and GW lines. The
    0 % line is 27.5 degrees at 17.3 kN/m3 (it returned 30.0). A dry unit
    weight the chart does not plot at the given relative density (22.0
    kN/m3 at 0 %, which returned 33 degrees) is refused (gec-13). The
    docstring describes the shaded caution area as drawn: between the SW
    and GW lines up to the 100 % line, above a thin line from the SW line
    at 75 % through the GP label to the GW line at 50 % (it said "about the
    GP to GW range above 50 %").
  - `table_5_15_friction_factor` (Table 5-15, p. 99): a key names one row
    by a soil the row prints. "fine sand" is the Clean fine sand row, 0.35
    to 0.45 (it returned 0.45 to 0.55); "sand", which returned the clean
    gravel and coarse sand row's 0.55 to 0.60, and "gravel", "clay",
    "silty sand" are refused (gec-16).
  - `table_5_7_presumptive_bearing_rock` (Table 5-7, p. 68): "rock" and
    "hard", which returned the first row's 7.7 MPa, and "medium hard",
    "shale", "soft rock" are refused; each row answers to its own words and
    the rocks it lists (gec-31).
  - `table_5_9_rqd_bearing_capacity` (Table 5-9, p. 70): between two
    printed rows the quality is "between fair (RQD 75) and good (RQD 90)",
    not the lower row's word, and the result says the pressure was
    interpolated (gec-32).
  - `table_5_13_poissons_ratio_rock` and `table_5_14_youngs_modulus_rock`:
    a rock type by its printed name only ("s" returned diabase, "weathered
    granite" the intact granite row) (gec-40).
  - `table_5_12_shape_rigidity_factor`: values unchanged; the docstring
    says the linear interpolation between the printed length/width rows is
    not the table's and reads up to about 13.5 % below a logarithmic
    interpolation between the rows 10 and 100 (gec-33).
- **GEC-7 soil nail walls (FHWA-NHI-14-007).**
  - `figure_4_3_friction_angle_spt` (Figure 4.3, p. 79): the six curves
    rebuilt from the rendered page; the points read are in the comment
    above the data. On the curves sigma'vo/Pa = 0.5, 1.0, 1.5, 2.0, 2.5 and
    3.0 they were at most 8.3, 7.6, 5.9, 5.3, 4.9 and 3.9 degrees low
    (toward the high-N60 end of each curve) and at most 3.9, 3.5, 3.9, 3.9,
    3.3 and 3.4 degrees high (at the low-N60 start of each curve, up to
    N60 = 4.5, 6, 8, 10.5, 13 and 15.5 respectively). N60 = 22 at
    sigma'vo/Pa = 2.0 is 37.0 degrees (it returned 33.6); N60 = 31 at 1.0 is
    45.0 (was 38.2); N60 = 48 at 1.5 is 46.5 (was 40.6). A curve is read
    only where it is drawn, from phi 25 to where it leaves the top of the
    chart or ends: N60 = 50 at 0.5 (it returned 44; the curve reaches phi 50
    at N60 38.25), N60 = 5 at 2.0 (it returned 29.0; the curve starts at
    N60 6.1) and N60 = 0 are refused. Between curves the angle is linear in
    sigma'vo/Pa at the same N60 (gec-02).
  - `figure_5_11_basal_heave_nc` (Figure 5.11, p. 124): the three curves
    rebuilt from the rendered page. At H/Be = 0 they start at 5.20 (Be/Le =
    0), 5.69 (0.5) and 6.19 (1) (it returned 5.14 for all three); a long
    excavation at H/Be = 1.6 is 6.76 (was 5.74) and at H/Be = 5 is 7.45
    (was 6.2, 17 % low) (gec-11).
  - `table_4_2a_spt_soil_properties` (Table 4.2a, p. 78): the very loose
    and very dense rows print phi "< 30" and "> 45 (3)"; they returned 25
    to 30 and 45 to 50, bounds the table does not print, and now give no
    lower and no upper bound respectively, with the printed text in
    `phi_printed`. The result carries notes (1) to (3); note (3) holds
    sands to 40 degrees and gravelly soils to 45 (gec-22). N60 = 50 is
    Dense, the row that prints it ("30 to 50"; Very Dense is "> 50"); it
    returned very dense. At N60 = 4, 10 and 30, each printed in two rows,
    the upper row is returned as before and the result names the lower
    one (`also_printed_in`, `note`).
  - `table_4_3b_elastic_modulus_spt` (Table 4.3b, p. 82): "sand" returned
    the silts row, 8 (N1)60 ksf (7,661 kPa at (N1)60 = 20, where clean fine
    to medium sand is 13,406); it fits two rows and is refused. Each row
    answers to its printed name (gec-17).
  - `table_5_1_factors_of_safety` (Table 5.1, p. 108): short-term
    excavation prints 1.25-1.33 (3); `fs_static_max` 1.33 is added beside
    1.25. The Basal Heave row's seismic 2.3 carries note (5), long-term
    conditions; the short-term row returned it and now gives none. Rows
    with a note carry it ("basal heave" alone, which returned the
    short-term row, is refused) (gec-41).
  - A key names one printed row in `table_4_3a_elastic_properties`,
    `table_4_4a_bond_strength_coarse`, `table_4_4b_bond_strength_fine`,
    `table_4_5_bond_strength_rock`, `table_4_6_pullout_resistance`,
    `table_5_1_factors_of_safety`, `table_5_3_load_factors_permanent`,
    `table_5_resistance_factors` and `table_5_12_wall_displacement`. A word
    found in several rows was answered from the first: "clay" returned
    Table 4.3a's soft sensitive clay (2,394 to 14,364 kPa); rotary drilled
    "sand" Table 4.4a's Sand/gravel (103 to 179 kPa) though Silty sand is
    also printed; "shale" Weathered shale though Slate/Hard shale is
    printed; "eh" the active row; "basal heave" the short-term resistance
    factor 0.65 (long-term 0.50); "soil" the weathered rock and stiff soil
    column (C = 0.8). Each is refused with the printed rows; printed names
    and listed short names are taken. Table 4.3a's clay rows say their
    Poisson's ratio is undrained, and Table 4.4a's high-overburden rows and
    Table 4.6 carry their notes.
  - `table_4_9_site_coefficient_fpga` (Table 4.9, p. 94): GEC-7 heads its
    columns PGA <= 0.25, 0.5, 0.75, 1.0, >= 1.25, the Ss values that head
    the Fa table (GEC-12 Vol I Table 7-28); GEC-12 Table 7-27 (p. 380)
    prints the same F_PGA values under PGA < 0.1, 0.2, 0.3, 0.4, > 0.5, and
    the lookup now reads them there (lead's ruling). Site class D at PGA
    0.30 is 1.2 (it returned 1.56); E at 0.35 is 1.05 (was 2.18). The result
    is a dict with `F_pga`, a `print_note` naming both headings and the
    reference (it was a bare number); site class F is refused with the
    table's note (1), a site-specific analysis (gec-29).
  - `table_4_10_site_coefficient_fv` (Table 4.10, p. 95): values and
    headings unchanged (they match GEC-12 Table 7-29). Site class F is
    refused with the table's note (1), "A site-specific dynamic site
    response analysis must be performed in these cases." (it said
    "Unknown site_class"); Table 4.9's refusal quotes the same note. The
    docstring cites the table as headed, "(Kavazanjian 2011)" (it said
    AASHTO 2014).
- **GEC-10 drilled shafts (FHWA-NHI-18-024, 2018).**
  - `table_8_4_resistance_factor` (Table 8-4, p. 8-14): a key names one
    printed row. "side" returned cohesionless compression 0.55 and
    "uplift" 0.45, the first rows holding the word; these and "rock",
    "load test", "structural" are refused with the rows. Rock side
    resistance cites Eq. 10-21, as printed (it said Eq. 10-21 or 10-22);
    combined axial and flexure gives the printed range, 0.75 with
    `phi_max` 0.90 (gec-15). `table_8_4_by_category` refuses a category it
    does not have (it returned an empty list), and
    `table_9_1_lateral_resistance_factor` (Table 9-1, p. 9-22) no longer
    answers a name that holds a row's word ("group uplift" returned the
    group row's 0.8).
  - `aashto_reliability_index` is removed: GEC-10 prints no table of the
    reliability index against the probability of failure, and the
    function interpolated pF linearly between six points, 27 to 37 % high
    between them (gec-23, lead's ruling).
  - `table_11_2_group_efficiency_cohesionless`: values unchanged (0.65 at
    2.5 diameters, 0.80 at 3, 1.0 at 4 or more). GEC-10 prints them in the
    text of Section 11.4.1.2 (p. 11-6), not in a Table 11-2; the result
    cites that section and says when the value is interpolated. The name
    is kept (gec-24, lead's ruling).
  - `su_uu_to_ciuc` and `su_uc_to_ciuc` (Eqs. 10-17 and 10-16, p. 10-16):
    where the printed relation gives su/su(CIUC) of zero or less (su/
    sigma'vo of 0.0149 or less for UU, 0.0182 or less for UC) it is
    refused; su(UU) = 10 kPa at sigma'vo = 700 kPa returned -1,030 kPa.
    GEC-10 prints no range for the relations; above those points the
    answers are unchanged (Example 10-2: 2,000 psf at 3,697 psf gives
    2,571 psf) (gec-14).
  - `equation_10_22_caving_rock_side` (Table 10-3, p. 10-21): below RQD 20,
    where the table has no row, the RQD 20 row is still used and the
    result now says so. `equation_10_21_rock_socket_side`,
    `equation_10_22_caving_rock_side`, `figure_10_6_alpha_clay` and
    `table_10_2_nc_base_clay` docstrings quote the print: the resistance
    factor for rock side resistance is 0.50 in Table 8-4 and 0.55 in the
    text of p. 10-21 (the lookup returns the table's 0.50, ruling G1
    below); qu should not exceed
    the shaft concrete's strength (p. 10-21, not checked); Eq. 10-20 is in
    D, the depth of embedment (gec-43).
  - Lead's rulings G1-G3 on the review's three GEC-10 questions:
    `table_8_4_resistance_factor('side_rock_compression')` returns the
    table's 0.50 with a `print_note` quoting p. 10-21's 0.55 "as
    presented in Table 8-4" (G1). `equation_10_21_rock_socket_side`
    quotes pp. 10-21 to 10-22, "Kulhawy and Prakoso (2007) suggests a
    mean value of C = 1.9 with use of Equation 10-22 for roughened
    sockets", and says C appears only in Eq. 10-21; with C above 1.0 the
    result carries the page's recommendation to verify C by load tests or
    local experience (G2; values unchanged). `figure_10_6_alpha_clay`
    (Eq. 10-18, Figure 10-6, p. 10-17) refuses su(CIUC)/pa outside the
    drawn curve, 0.25 to 5.0 (25.3 to 506.6 kPa), read at 300 dpi; su/pa
    0.1 returned alpha 2.0 and su 10,000 kPa 0.302 (G3). The refusal
    prints the ratio to enough digits that a value just outside the curve
    does not show as one of its ends.

- **GEC-11 MSE walls (FHWA-NHI-10-024 Vol I).**
  - `table_2_1_min_reinforcement_length` (Table 2-1, p. 2-43): the three
    printed cases. Seismic loading is one row, "0.8 to 1.1"; it was two
    rows, "Seismic (low)" 0.8 and "Seismic (moderate to high)" 1.1. Each
    row gives the printed cell (`typical_min_L_over_H`) and its ends
    (`L_over_H_low`, `L_over_H_high`; the key `L_over_H` is gone). The 8 ft
    (2.5 m) minimum on every row is removed: the table does not print it;
    the docstring quotes where the text does (p. 4-11) (gec-21). The
    static row carries a `print_note`: the table prints "Static loading
    with or with traffic surcharge".
  - `table_4_4_traffic_surcharge` (Table 4-4, p. 4-17): the parameter is
    `abutment_height_ft` (was `wall_height_ft`), and every result says the
    table is for abutments perpendicular to traffic and that walls parallel
    to traffic take heq = 2.0 ft (p. 4-16). Below 5.0 ft the 5.0 ft row
    (4.0 ft) is still used, with a note. Values unchanged (gec-20).
  - `table_4_7_internal_resistance` (Table 4-7, p. 4-48): rows and keys as
    printed: `static_phi`, `combined_static_earthquake_phi`,
    `combined_static_traffic_barrier_phi`, with notes A to C. The key
    `combined_static_phi` (a copy of the static factor, 0.75 for strips,
    beside the printed combined static/earthquake 1.00) and the keys
    `earthquake_phi` and `traffic_barrier_phi` are gone; values unchanged
    (gec-34).
  - `table_3_4_electrochemical_geosynth` (Table 3-4, p. 3-10): the two
    printed rows, polyester (PET) 3 < pH < 9 and polyolefin (PP & HDPE)
    pH > 3, by AASHTO T-289; "polyolefin" returned an empty list.
  - The eleven filter lookups (Tables 2-1, 2-2, 3-4, 3-6, 3-8, 3-9, 3-11,
    4-1, 4-2, 4-5, 4-7) refuse a filter that matches no row, listing the
    rows by the library's labels, which the message says are not all
    worded as printed; they returned an empty list. A filter is matched as one
    phrase, then word by word, so "metallic strip" and "vertical earth
    pressure" find their printed rows (gec-37).
  - Notes as printed: Table 2-2's footnote (frost and scour depth); Table
    3-9's backfill types (Type 2: max. 3/4 in. (20 mm), D50 about #30; the
    docstring said "uniform fine sand to medium sand", 19 mm) and footnote
    a; Table 4-1's gamma_EQ note (the code said "typically 0.0 to 0.50",
    not printed); Table 4-2's types of load; Table 4-5's conditions (0.65
    also where the slope contains or supports a structural element).

- **GEC-9 laterally loaded deep foundations (FHWA-HIF-18-031).**
  - `table_7_1_p_multiplier` (Table 7-1, p. 104): beyond 5B the 5B row is
    still used, and the result now says the table has no row there (note
    (3) allows interpolation between 3B and 5B only); the table's notes
    come back as `print_notes`. The refusal below 3B no longer says "use
    Pm = 1.0 beyond 5B", which the table does not print (rows 2 and 3 are
    0.85 and 0.7 at 5B) (gec-25).
  - `table_a1_k_stiff_clay`, `table_a2_epsilon50_stiff_clay` (Tables A-1,
    A-2, p. 222): outside the printed Ca columns (0.5 to 4 ton/ft2) the
    end column is still used, with a note; Ca 100 (kPa passed as ton/ft2)
    gave 2,000 pci unsaid. The docstring's "for Ca > 4 ton/ft2 use k = 2000
    or 800" is removed: GEC-9 does not print it (gec-25).

- **GEC-4 ground anchors (FHWA-IF-99-015).**
  - `table_6_soil_anchor_transfer_load` (Table 6, p. 71): "very stiff" is
    refused; the silt-clay row prints Stiff (10-20) 30 kN/m and Hard
    (21-40) 60 kN/m only, and "very stiff" returned the Hard row's 60
    (gec-30).
  - `table_7_bond_stress_rock` (Table 7, p. 73): `recommended_FS` 3.0 on
    every row is gone (the table prints no factor of safety); the result
    quotes p. 74 instead: 3.0 on Table 8's transfer load in competent
    rock, 2.0 for intermediate geomaterials (qu 0.5 to 5.0 MPa) (gec-38).
  - `table_8_rock_anchor_transfer_load` (Table 8, p. 74): transfer loads
    unchanged. It returned a factor of safety of 3.0 on every row, soft
    shales included; p. 74 gives 3.0 "in competent rock" and 2.0 for weak
    rocks such as clay shales, "intermediate geomaterials" of unconfined
    compressive strength 0.5 to 5.0 MPa, and the table assigns neither to
    a row. Each row now returns both in `factor_of_safety_options`, each
    with its condition and allowable load per metre, the page's sentences
    in `print_note` and the printed row name (`factor_of_safety`,
    `allowable_load_per_m_kN` and `notes` are gone). Soft shales: 50 kN/m
    at 3.0 or 75 kN/m at 2.0 (lead).
  - `table_7_bond_stress_rock`, `table_8_rock_anchor_transfer_load`:
    "limestone" and "shale" are refused (each names two printed rows;
    they returned soft limestone and soft shales) (gec-39).
  - `table_20_corrosion_protection` (Table 20, p. 131): the table's words.
    The anchorage is "Trumpet" for both classes (was "attached to bearing
    plate with watertight weld"); Class I bond length "Grout-filled
    encapsulation or" / "Fusion-bonded epoxy" (was "Corrugated HDPE or
    polypropylene encapsulation"); Class II bond length "Grout". The source
    reads "modified after PTI, 1996", as printed (gec-39).

- **GEC-8 continuous flight auger piles (FHWA-HIF-07-03).**
  - `dd_pile_side_resistance_MPa` (Eq. 5.29, pp. 83-84): every result
    carries the print's conditions, N60 not depth corrected and
    cohesionless materials only (they were dropped); above N = 50 the
    result says N = 50 is used. Values unchanged (gec-42).

- **FHWA-NHI-05-037 Geotechnical Aspects of Pavements (`fhwa_pavements`).**
  - `cbr_from_dcp`, `resilient_modulus_from_dcp` (Table 5-34, p. 5-53): the
    parameter is `dcp_mm_per_blow` (was `dcp_index`, in./blow as Table 5-34
    prints). Read in inches, 0.5 in./blow gave CBR 634.7 and Mr 158,867
    psi; TM 3-34.48-2 (2016) Figure G-11 and WES GL-92-3 (1992) p. 17 give
    the relation in mm per blow, and TM 3-34.48-2 Table G-1 prints CBR 22
    at 10 mm/blow. `resilient_modulus_from_dcp` works Mr from the
    unrounded CBR (10 mm/blow: 18,553.9 psi; it used CBR 22.2, 18,580.5).
    A CBR over 100 % (DCP under 2.6 mm/blow) is refused;
    every result carries a `print_note` naming the sources (gec-08, lead's
    ruling 8).
  - `cbr_from_plasticity_gradation` (Table 5-34): `p200` is the fraction
    passing the No. 200 sieve as a decimal (0 to 1), wPI = P200 x PI being
    taken with P200 as a decimal fraction; a value above 1 is refused with
    the decimal to give. It took the percent: 0.35 was read as 0.35 % (CBR
    73.1 at PI 10; now 21.1)
    (lead's ruling 9). Table 5-34's lookup keeps the printed comments and
    adds a `library_note` for the DCP and P200 rows.
  - `modulus_subgrade_reaction_from_cbr` is removed: FHWA-NHI-05-037 does
    not print k = 1500 CBR / 19.4. AASHTO 1993 prints k = MR/19.4 (p.
    II-44); `aashto_1993.equations.modulus_subgrade_reaction_simple` holds
    it (gec-27, lead's ruling).
  - `table_5_49_drainage_modifier_mi` (p. 5-87): values as FHWA prints; the
    result notes that AASHTO 1993 Table 2.4, which it cites, prints Poor
    and Very Poor < 1 % as 1.15-1.05 and 1.05-0.95 (FHWA: 1.05-0.80 and
    0.95-0.75) (gec-26).
  - `effective_subgrade_modulus_from_relative_damage` is Eq. 5.12 as
    printed, Mr = 3015 uf^-0.431 (it computed the exact inverse of Eq. 5.11
    and cited Eq. 5.11; 3014.8 at uf 1.0, now 3015.0).
    `resilient_modulus_from_cbr_aashto93` warns above CBR 10, not at it
    (Eq. 5.13 is printed for CBR <= 10). `backcalculated_to_design_modulus`
    cites Table 5-31's commentary (pp. 5-48 to 5-49), where the factors are
    printed. The module docstrings say `pdf_page` is a 0-based page index
    (gec-48).
  - `resilient_modulus_from_r_value` cites Table 5-34 only (Mr = 1155 +
    555R, unchanged): its docstring called Eq. 5.15, Mr = 1000 + 555R (p.
    5-49), equivalent, and the chapter text said the function implements
    Eq. 5.15. `granular_resilient_modulus_bulk_stress` names Table 5-30
    (p. 5-46) for typical k1, k2 (it named Table 5-39, which is for Eq.
    5.17).

**DM 7.2 chapter text: equations as printed (build of 2026-11-10, app
BACKLOG REF-79).** The equations the review found stored in a form the
print does not have were read again from the rendered pages and point-fixed
in `dm7_2/text/` (body, key points and equation entries); no lookup
changes. Those that change a computed value: Eq. 2-10 (rho = q gamma_w /
delta p, it was divided by gamma_w), 3-2, 4-25 (qmax = 2R/(3 x0); the text
gave 2.25 times it), the six Table 4-7 cofferdam checks (sliding lost +PP,
rotation had the signs swapped, the interlock pressure and the sheeting
slippage were other formulas), 5-21 (- ic), 5-34 (lambda = fourth root of
ks B/(4 Ec I)), 5-39, 6-53, 6-60, 6-64 and 6-79 (tcap = Pui/12 + 30, it was
Pui/30 + 12). Eq. 5-5 to 5-7 keep the printed absolute values; P-2, 2-5,
2-6, 3-1, 3-7, 4-5, 4-12, 4-16 and 6-63 are in their printed forms. Filed
where printed: Eq. 4-20 to 4-22 (new section 4-4.4.3.2 Low Hydraulic
Conductivity Soils; three empty "force-injected" entries under 4-5.1.1
removed), 5-34 and its paragraphs (5-4.2.1), 6-38/6-39 with the
block-failure text (6-5.5), 7-6 (7-4.1.1) and 7-16 (7-4.4, the empty
7-4.5.2 entry removed); 7-4.1.1, 7-4.4 and 5-3.3.3 bodies completed from
the page. The Table 4-7 entries are named by the printed rows ("Table 4-7,
Sliding at Base" and so on), replacing ten unprinted ids. Key points:
Table 5-22 has eleven soil rows (not seven), Figure 4-54 note 3 (moments
80 % of simple span, not a pressure reduction), 2^n point-estimate cases.
Seven `implemented_in` links now name the equation's own function. Tests:
`tests/test_dm7_2_text_equations.py`.

Also in this build:
- Eq. 5-7 `corner_bearing_pressure` uses |eB| and |eL| as printed, so q1
  is the maximum corner pressure whatever signs are passed. It now returns
  a dict (`q1` to `q4` and a `note` that the magnitudes were used) instead
  of a 4-tuple. q_gross 10, eB -0.5, eL -1.0, B 6, L 12: q1 0 -> 20 (it
  was the minimum), q4 20 -> 0.
- `dry_unit_weight_from_saturation`: the docstring's first formula is the
  printed Eq. 3-2, gamma_w S / (w/100 + S/Gs); the computation is unchanged.
- Chapter text: the 5-3.6.2 applicability gives the printed H/B limits
  (strong layer below 0.7B, weak layer below 3B, no effect); the 5-6.2.2
  floor-slab key point keeps its printed condition (where heave of the slab
  is not a critical concern); 7-4.2.4 keeps the printed "beta = 4.26 (Pu =
  0.0001)" and adds a note, marked as not printed, that a standard normal
  distribution gives beta 3.72 at 1e-4 and 4.26 at about 1e-5. Eq. 6-79
  stays uncoded (`implemented_in` null).

**Build: UFC 3-250-01 Figure 10-1 retraced from the chart (pave-22).**
`ufc_pavement.figure_10_1_k_on_base` read the effective k on top of the
base up to 29 % low at mid thicknesses and, for the 25 to 75 pci curves
under bases thinner than about 10 in., up to 39 % high (the unsafe side):
its curves were read by eye at 10 in. steps and joined by straight lines
across their S-shaped start. Each curve is now traced from the chart
image (PDF 52, printed 32) column by column, calibrated on the chart's own
gridlines, which fit one thickness scale within 0.07 in. and one log k
scale within 0.7 %, and stored every 0.5 to 2 in.; stated tolerance 1 % of
k on a curve (2 % for the 200 curve past 55 in. and the 300 curve past
57 in., where they run together with the 150 curve and the 500 pci
frame). Between curves, log k on base is interpolated in log k on
subgrade (the library's rule; it was linear). Before and after, psi/in:
k 25 under 4 in. 41.0 -> 29.5; 100 under 10 in. 160.0 -> 194.4; 200
under 10 in. 255.0 -> 299.7 (the curve passes through the 300 gridline
there); 100 under 28 in. 246.0 -> 346.3; 300 under 10 in. 350.0 -> 357.7
(the review's note had misread this one as 385).
The limits are unchanged and were re-read from the trace: below the
25 pci curve refused, above 300 pci and past 60 in. held with a note.
Results also carry the chart's note and how the value was interpolated.
Nothing in the library or the app calls the function.

**Build of 2026-11-10: design and worked-example appendices built from
the print (app backlog REF-85).** The helper could not search or quote
these appendices: they were held as a condensed paraphrase or not at all.
Each is now stored in the print's own wording with a `[p. A-5]` marker
where each printed page starts; every equation, calculation line and table
is typed in from a rendered page, and figures are listed by printed
number. Where the print disagrees with itself the text keeps the print and
says so "(as printed; ...)". A printed section over the tools' size limit
is stored as the section and lettered parts (`A.2.a`; the letters are not
printed).

- **GEC-10 (FHWA-NHI-18-024)**: Appendix A, the design example (chapter
  19, pp. A-1 to A-29), replaces the three-section paraphrase: sections A,
  A.1, A.2 with parts A.2.a to A.2.g, A.3; Eqs. A-1 and A-2, Tables A-1 to
  A-10 and the calculation lines of Steps 10 to 13. New: Appendix B,
  challenging geomaterials (chapter 20, Tables B-1 and B-2); Appendix C,
  axial load-deformation response (chapter 21: Vesic 1977, the t-z method,
  Kulhawy and Carter 1992, Mayne and Harris 1993; Eqs. C-1 to C-42, Table
  C-1); Appendix G, alternative lateral models (chapter 25: Carter and
  Kulhawy, Zhang et al.; Eqs. G-1 to G-20); Appendix H, post-grouted
  shafts (chapter 26). Appendices D to F (guide specification, inspection
  checklist, forms) are not built; chapters 22 to 24 are left for them and
  the manifest says so. Print conflicts kept and noted include the example's
  RSN lines of pp. A-10 and A-11 (932 and 967 lb/ft² against fSN 936 and
  976 psf),
  Table A-7's axial 1,836,420 against 2,673.42 kips in the text, and p. C-10's
  example (a 2-ft socket, 870 psi, 1,751 kips) against Figure C-6 (a 6-ft
  socket, 2,500 psi).

Tests: `tests/test_gec10_appendices_printed.py` (116).

## 1.6.0

**Local reference packs (REF-64).** A deployment can add its own references
in the library's structured format without putting them in the public
repository or the wheel.

- Set `GEOTECH_REFERENCES_PACKS` to a pack folder or a folder of packs
  (several separated by `os.pathsep`). Each pack holds `pack.json`,
  `text/chapterNN.json` (the chapter schema the built-ins use) and
  optionally `figures_catalog.json` and its PDF. Pack ids start with
  `local_`. Packs hold no code.
- `reference_search`, `reference_get`, `reference_query`,
  `list_indexed_references`, `figure_search`, `figure_get`, `resolve_pdf`
  and the file-based `retrieve_section` family cover packs beside the
  built-in references, with the same ranking and synonym expansion.
- A pack names its PDFs by bare file name only (`pdf_files`, a catalog's
  `pdf_path`). For a pack figure, `resolve_pdf` looks in the pack folder,
  then `GEOTECH_REFERENCES_DOCS`, then raises `FileNotFoundError`; no path
  read from a pack leads outside those folders, and `figure_get` never
  returns a host path for a pack figure.
- A bad pack file cannot break search. A chapter file or catalog the
  indexes cannot take (unreadable JSON, a list or an object where text
  belongs, a PDF named by a path) is skipped and named in
  `_packs.problems()`. Each pack file is indexed under its own SQLite
  savepoint, so one that fails anyway is rolled back while the built-ins
  and the other packs still index.
- The search databases are keyed by the pack set as well as the package
  copy. With the setting unset, every key, every database and every result
  is unchanged.
- A figure catalog may give any figure two optional fields: `bbox` (the
  chart's box on the page, PDF points, top-left origin) and `read_notes` (at
  most 500 characters on how to read it). `figure_get` returns them where
  given; built-in figures carry neither.
- New: `python -m geotech_references.packs new|check|list|index|schema`.
  `check` exits 0 or 1. It checks the schema and the type of every field
  (reported as errors, never tracebacks), the catalog, pages and boxes
  against the PDF with PyMuPDF, print-fidelity warnings and a search smoke
  test. It refuses a pack inside the package or a public repository's work
  tree. `schema` prints the chapter-file schema.
- `chapter_schema.json` moved from `scripts/` into the package and ships in
  the wheel.
- Also new: `scripts/build_figure_catalog.py --pack`,
  `_packs.pack_records()` for build records, and `docs/REFERENCE_PACKS.md`
  (the format, the print-fidelity rules, a minimal chapter file, where packs
  live on each host).
- The chapter schema check moved from `scripts/audit_chapter_text.py` into
  `geotech_references/_schema.py`. The script imports it, and its results
  are unchanged.
