# REF-49: the GEC-12 chapter 7 charts checked against the print

`geotech_references/gec_12/figures.py`, 2026-10-31. Every chart the module
returns was read off the printed figure in `docs/GEC 12 vol 1.pdf`. The
figures are 150 dpi rasters inside the PDF: Fig. 7-9 (pdf page index 280),
Fig. 7-14 and 7-15 (283), Fig. 7-16 (284), Fig. 7-17 (293), Fig. 7-18 (294).
Each was extracted as it is and read column by column (row by row for Fig.
7-9) as the darkness-weighted centre of each drawn line, against the figure's
own gridlines. Page numbers below are the printed ones.

Only Fig. 7-15 had been measured before (2026-10-08). Every other chart held
values that do not come from the figure: C_F rising with phi where the
printed curves fall, alpha_t below 20 deg where no curve is drawn, a single
"typical" delta/phi per pile type where Fig. 7-9 draws a curve against V,
and Figs. 7-17 and 7-18 with the wrong shapes. All are now the printed
curves. They agree with the app's own readings of the same figures
(`axial_pile/nordlund.py`, `axial_pile/tomlinson.py`,
`geotech_common/alpha_method.py`, GM-121 / GM-229 / GM-282), node for node.
Fig. 7-9's curves d, e and g, which the app does not use, were read here.

Reading precision is about one pixel: 0.0023 in delta/phi (Fig. 7-9), 0.003
in C_F, 0.6 % in alpha_t (log axis), 1.3 % in N'q (log axis), 0.004 ksf in
Ca, 0.004 in alpha (Fig. 7-18).

## Per chart

| Chart | Before | Now (read off the figure again, library value against the print) |
|---|---|---|
| Fig. 7-16(b) N'q | 7 nodes (15 to 45 deg every 5): 28 / 60 / 150 / 500 at 30 / 35 / 40 / 45 deg, 4-7 % low at 30-40 deg | every degree, 15-45 deg: 30.1 / 63.8 / 160.4 / 475.0. Read again at every half degree: within 0.9 % of the nodes (worst 42.5 deg). The same nodes as `axial_pile` (GM-282); the two do not differ anywhere. |
| Fig. 7-16(a) alpha_t | 15-45 deg every 5; at D/b 30: 0.29 / 0.50 / 0.77 at 20 / 30 / 40 deg (made-up 15 deg values) | every degree, 20-45 deg (the curves start at 20 deg and merge at about 37): 0.257 / 0.531 / 0.750. Within 0.003 at all 69 reads where the curves are apart. Below 20 deg it is refused. |
| Fig. 7-14 C_F | rising with phi on the delta/phi < 1 curves (0.10 at 15 deg on the 0.2 curve, 0.70 on the 0.8) | falling with phi below 1.0 (0.815 at 15 deg on the 0.2 curve, 0.988 on the 0.8; 0.241 and 0.841 at 45 deg), rising on 1.2 and 1.4; every 2.5 deg, 15-45 deg. Within 0.007 at 42 reads. Above 45 deg (the old range ran to 50) it is refused. |
| Fig. 7-9 delta/phi | one "typical" ratio per pile type (pipe 0.70, H-pile 0.60, ...), no V | each curve against V: a-e and g from V = 0.3 to 1.9 ft^3/ft, f (H-piles and augercast piles) 0.08-0.52. The H-pile curve runs 0.73-0.98 (the old 0.60 is below it everywhere). Within 0.007 at 84 reads. |
| Fig. 7-17 Ca | concrete D = 10b peaking at 0.95 ksf near su 2.5-3 ksf, 33-36 % under the print at 1.8 ksf | the printed curves, peaking near su 2 ksf (solid D = 10b 1.369, D = 40b 1.819 at 2.2; dashed 1.170 and 1.581) and falling after it; each curve's own su range (0.25-3.45 ksf solid, 0.25-3.05 dashed; the solid D = 40b curve from 1.0). Within 0.011 ksf at 116 reads (four dashed reads fall in the dash gaps). |
| Fig. 7-18 alpha | every case from alpha 1.0 at su 0 down to 0.08-0.24 at 5 ksf; Case 1 "D < 10b" at 0.22 | Case 1 D < 10b at 1.0 across the chart, D = 20b level at 0.752 past 3 ksf, D > 40b at 0.390; Case 2 within its curves (0.45-4.56 and 0.52-4.76 ksf); Case 3 levelling at 0.238 and 0.300. Within 0.008 at 107 reads. Outside a curve's su range it is refused. |
| Tables 7-6 / 7-7 K_delta | as printed | unchanged: all 320 values match the printed tables exactly (read from the PDF text). The interpolation between columns is now log-linear in V, as Step 3 (c to e, p. 243) prints it; the printed columns are themselves that interpolation between the V = 0.1, 1.0 and 10 curves, to the tables' 0.01. Between columns this moves K_delta by up to 0.033 (phi 40, V = 1.5: 3.228, was 3.195). |
| Fig. 7-15 q_L | measured 2026-10-08 | unchanged; within 1 % in GM-282's check. |

## Calls that change

- `figure_7_9_delta_phi_ratio(pile_type, V)` now needs V (ft^3/ft) and
  returns `curve` and `V_range` besides `delta_phi_ratio` and `description`.
  The app's gec12 reference tool lists it from its signature; an agent call
  without V now fails with the missing argument named.
- Values the charts do not give are refused with the chart's range, as Fig.
  7-15 already was: Fig. 7-14 outside 15-45 deg, Fig. 7-16(a) below 20 deg,
  Fig. 7-17 below 0.25 ksf and past each family's end, Fig. 7-18 outside
  the curves read, Fig. 7-9 outside each curve's V.

## Checked, within reading precision, not changed

- Tables 7-6 and 7-7 (above) and Fig. 7-15.
- `tables.py`: Table 7-1 (compression and tension factors, block failure
  0.60, group uplift 0.50) and Table 7-9 (beta and Nt ranges by soil type)
  match the print (p. 224 and p. 256).

## Not in the library

- Figs. 7-10 to 7-13 for tapered piles (omega > 0): `figure_7_10_to_13_kd`
  refuses omega > 0 as before.
