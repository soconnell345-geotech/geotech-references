# Changelog

Releases before 1.6.0 are described in their release commits (`git log`).

## Unreleased

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
