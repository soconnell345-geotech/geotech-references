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

**Build: the pavement references' chapter text read against the print
(app backlog REF-83).** Summaries and key points that said more than the
page, or put a stronger word on it, now restate the printed sentence;
equations were checked on the rendered pages. No lookup changed. Only
AASHTO 1993 changed section ids (listed under it below). Every line that
carries a formula, in text and in worked examples, was then read again
from a 200 dpi render and stored as typeset, because formulas taken from
the text layer had been found scrambled: 29 numbered formula lines and 6
unnumbered passages in UFC 3-250-01, the 6 formulas and 2 worked examples
of UFC 3-250-11, and every formula line of the rebuilt AASHTO chapters,
typed from the renders as they were built. `tests/test_pavement_text_scatter.py` (15
tests) looks in all three references for the signs a text-layer formula
leaves: a prime cut loose, a lone number line above a formula, a bracket
that does not pair, a sentence repeated in a body or down a table's rows.
It found none. Each printed case it allows was checked on the page.

- **UFC 3-250-01 (`ufc_pavement`, 21 chapters, 317 sections; 130
  sections changed: 95 summaries, 102 key-point lists, 21 bodies, 8
  equation lists).** Summaries and key points brought back to the print: "must"/"never"/
  "prohibited"/"mandatory" where the page says "should", "should not",
  "may" or "is required" (e.g. 4-0, 14-3, 16-2.2.1, 16-2.2.3, 17-1.2,
  17-1.4, 19-4, 19-7, 19-8.1, 20-2.7.2, 20-5.1, 21-4.4); conditions put
  back (18-4.1 to 18-4.3 bond, 19-9.3 stones, 20-5.3.1 frost pipe depth,
  20-3.4 exemptions); sentences that were not printed removed (2-2.4,
  5-3, 9-8, 9-9, 13-5, 13-6, 16-2.3.2.3, 19-12, 19-14, 21-8), as were
  the "Verified against Appendix G" key points. 16-6.2 said the special
  joint may be left out "below" 75 percent capacity; the page says at 75
  percent or less. The drainage-layer thickness paragraph and Eqs. 20-17
  and 20-18, printed under 20-3.4.3, had been stored under 20-3.4.1; they
  are back under 20-3.4.3. Eq. 20-13 is stored in its printed form
  (L = Lt sqrt(it^2 + ie^2) / it, the same value). Heading-only
  paragraphs 9-5, 10-2.1 and 14-2.1 carry the text printed under them.
  Print slips are kept as printed with a note: 4-3.1 "165 in (420 mm)";
  5-2 "cohesive fills at less than 90 percent" against 6-3; 9-5.2
  "Table 7-1" for the minimum thicknesses (Table 7-2); 15-7.2 "he" in the
  definition and hE in Eq. 15-4; 17-2 "paragraph 15-5" for joint sealing
  (16-5); 20-3.4.3 "equation 7-17"; 20-3.4.4 "become saturated"; Eqs.
  20-15 (mm/sec, 217.5) and 20-16 (ft/day, 6.214 x 10^5), which differ by
  a factor of about 10 once converted. The filter criteria of 20-2.5.2
  and 20-2.5.3 had been rearranged as products ("D15(filter) <= 5*D85");
  they are stored as the ratios printed on p. 101 ((15 percent size of
  drainage or filter material) / (85 percent size of material to be
  drained) <= 5, and so on). `tests/test_ufc_pavement_text_equations.py`
  pins the equations, limits and notes (38 tests).
- **UFC 3-250-11 (`ufc_stabilization`, 8 files, 101 sections; 85 sections
  changed: 57 bodies, 38 summaries, 71 key-point lists, 2 equation lists,
  4 applicability lines).** Every body now holds its printed text; printed
  sub-paragraphs with no section of their own stay in their parent with
  their numbers (2-1.1 now carries 2-1.1.1 to 2-1.1.6). Tables and figure
  labels are named, not run into the text; 4-1.4, 4-2.2 and 4-4.2, whose
  printed text is longer than a body can be, are verbatim extracts under
  13,100 characters with the gaps marked "[...]" (reference_query keeps
  whole rows within 13,300 characters of its 14,000; `tests/test_result_size.py`
  found the first two over it at 13,800, and 4-4.2, full text at 13,553,
  is now an extract too; no limit, number or "do not" was cut). Heading-only paragraphs (2-1.3, 2-2, 4-1, A-1 and
  others) say so and name their sub-paragraphs. 4-2.1 said deep mixing is
  "NOT routine for airfield projects"; that caution is printed under
  4-2.2.4 and is there now, and 4-2.1 holds the printed deep-stabilization
  approaches (24 in, then the top 6 to 12 in; 18 in by progressive cuts;
  8- to 9-in lifts near the surface; the frost caution). "Hard limit",
  "must" and "never" put back to the page's "do not", "should", "cannot
  ... and remain effective"; 2-1.2.2 states both printed sulfate sentences
  (one allows Pavements DWG authorization, one does not and adds lime).
  Print slips kept with notes: 4-1.4.7 "construct all layers to be less
  than 4 inches thick"; 4-2.1 "6 to 12 inches (130 to 300 mm)"; A-1.2.1 and
  A-1.2.2 millimetre arithmetic, and in both "0.52 inches * 2.3 = 1.12
  inches" (it is 1.196; the next steps carry 1.12); A-2 pH 12.1 against
  2-1.2.1's 12.0; A-3.1
  dilution "to 50 ml" then "take 100 ml" (the factor 411.6 fits 500 ml);
  A-3.1 oven-dry weight expression malformed; A-3.2 prints only a numeric
  example with "x 0.0338 percent" for "= 0.0338 percent".
  `tests/test_ufc_stabilization_text_equations.py` pins them (28 tests).
- **AASHTO 1993 (`aashto_1993`, 11 chapter files, 44 sections before, 80
  now).** The stored text was a paraphrase holding statements the Guide
  does not print (Part I ch 5's "14 major considerations enumerated in the
  Preface"; II-1.2's chart solutions "somewhat less precise than the
  corresponding computer solution"; 4.5's "98.3% per stage"). Bodies are
  now the Guide's own words read from 200 and 300 dpi renders of the scan,
  with [p. II-56] page markers: all of Part II chapters 1 to 4 (pp. II-3 to
  II-86) and Part I's held sections (1.1, 1.2, 1.9, 2.1, 3.1 to 3.3, 3.9
  with 3.9.1 to 3.9.3, 4.1, 4.2.1 to 4.2.3, 4.3 to 4.5, chapter 5; the
  other Part I sections, e.g. 1.3 to 1.8 and 3.4 to 3.8, are not held). Tables are typed cell by cell (Part I Table 4.1;
  Part II Tables 2.1 to 2.10, 3.1 to 3.9, 4.1 to 4.10 with 4.8(a), 4.8(b),
  4.9(a) and 4.9(b), and the unnumbered tables), figures described from
  the renders, equations typed from them (all seven of 3.9.1 to 3.9.7,
  where one was stored as words; the CRCP nomograph equations; DBS = D̄BS
  + (0.5 × GL)). Parts III and IV are stubs that say so and list their
  contents with pages. III keeps the remaining-life equations where the
  print has them (Section 5.3.3, p. III-89: RL, CF, SNeff); the old stub put
  RL in Chapter 4 and gave "Deff = CF*D", which is not printed there. IV no
  longer says mechanistic procedures were "not incorporated"; p. IV-4 says
  the Guide uses them indirectly. Ids: I-5.1 renamed I-5 (chapter 5 numbers
  no sections); I-4.2 and II-4.1 removed (their headings have no text of
  their own; I-4.2 is held as its printed 4.2.1 to 4.2.3); added I-3.2,
  I-3.3, I-3.9.1 to I-3.9.3, I-4.2.1 to I-4.2.3, II-1.3, II-1.4, II-2,
  II-2.1.4, II-2.5.1, II-2.5.2, II-3, II-3.1, II-3.2, II-3.3.1 to
  II-3.3.3, II-3.4.1, II-3.4.2.a to II-3.4.2.c, II-3.4.3, II-3.5.1 to
  II-3.5.6, II-4, II-4.1.1, II-4.1.2, II-4.2 and II-4.2.1 to II-4.2.3. The
  one printed Section 3.4.2 is stored in three lettered parts (inputs and
  limiting criteria; procedure; example), the letters not printed. Every
  fetch is under the app's 16,000 characters, measured with the Guide's
  symbols escaped (`tests/test_subsection_retrieval.py`); for II-2.3.5,
  whose id is pinned, the record drops key points and equation notes it
  held twice. implemented_in: Eq. 4.2.3 no longer points at
  `tables.standard_normal_deviate_zr` (a Table 4.1 lookup), nor
  MR = k1θ^k2 at `tables.unbound_k1_k2` (it returns k1 and k2); SN on
  II-2.4.1, ΔPSITR and the mean ur now point at the functions that compute
  them (each opened). Print slips kept with notes, e.g. the "t = 1" limit of
  the sum in Eq. 3.9.3 (p. I-50), δ(NTwt) (p. I-57), no closing parenthesis
  after "1 1/4 inch" (p. II-25), "D/φ/²" in Nmin and Nmax (p. II-56), k-value
  ranges that leave 350 to 400 pci unassigned (p. II-81), Table 4.7's
  2.7-3.3 against Table 4.6's 2.9-3.1 (p. II-80).
  `tests/test_aashto_1993_text.py` pins them (22 tests).

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
  - Every `figure_search` hit carries `reference_id`, its volume's report
    number.
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
