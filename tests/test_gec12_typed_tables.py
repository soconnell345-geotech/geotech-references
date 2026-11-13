"""Typed-in tables of GEC-12 Volume I (FHWA-NHI-16-009), chapters 2 to 8 (REF-97).

Each table below was read off the printed page (300 dpi render of
'docs/GEC 12 vol 1.pdf') and typed into the `tables` entry of the section
that prints it, in the form GEC-10 chapter 8 uses: caption (p. page) -
columns - rows separated by ' | ' - the table's printed notes. The cells
pinned here are the printed values; a print slip is kept as printed with
an "[as printed; ...]" note beside it.

TABLES: (table, chapter, section_id, printed page, body rows, cells/notes
that must stand in the entry word for word).
"""
import json
from pathlib import Path

import pytest

TEXT = Path(__file__).resolve().parents[1] / "geotech_references" / "gec_12" / "text"

TABLES = [('7-4',
  7,
  '7.2.1.2',
  230,
  5,
  ['Nordlund Method. - Approach: Semi-Empirical. Method of Obtaining Design Parameters: Charts provided by '
   'Nordlund. Estimate of soil friction angle is needed.',
   'Disadvantages: No limiting value on unit shaft resistance is recommended.',
   'Method of Obtaining Design Parameters: Nq selected from Table 7-8 based on soil type.',
   'Disadvantages: Results affected by range in β values and in particular by range in Nt chosen.',
   'Remarks: Simple method based on correlations with 71 static load test results. Details provided in '
   'Section 7.2.1.3.5.',
   'Disadvantages: Limitations on pushing cone into dense strata. Remarks: Good approach for design. Details '
   'provided in Sections 7.2.1.3.6 and 7.2.1.3.7.']),
 ('7-5',
  7,
  '7.2.1.2',
  231,
  4,
  ['α-Method (Tomlinson Method). - Approach: Empirical, total stress analysis.',
   'Adhesion calculated from Figures 7-17 and 7-18.',
   'Advantages: Developed specifically for large diameter open end pipe piles.',
   'β and Nt values are selected from Table 7-9 based on drained soil strength estimates.',
   'Disadvantages: Range in Nt values for hard cohesive soils such as glacial tills can be large.',
   'Remarks: Good approach for design. Details in Section 7.2.1.3.6 and Section 7.2.1.3.7.']),
 ('7-12',
  7,
  '7.2.1.3.7',
  264,
  4,
  ['columns: Type of Piles; Cf',
   'Precast Concrete; 0.012',
   'Timber; 0.018',
   'Steel Displacement; 0.012',
   'Open End Steel Pipe; 0.008']),
 ('7-13',
  7,
  '7.2.1.4',
  270,
  9,
  ['Slaty Mudstone; H-pile; 0.6; 1.',
   'Slaty Mudstone; H-pile; 3.3; 1.',
   'Mudstone; Pipe Pile; 2.6; 2.',
   '(Mercia Mudstone); Precast Concrete; 2.7; 3.',
   'Limestone; H-pile; 24.0; 4.',
   'Sandstone; H-pile; 20.0; 4.',
   'Shale; H-pile; 12.0; 4.',
   'Information sources: 1) George et al. (1976) 2) Tomlinson and Woodward (2015) 3) Leach and Mallard '
   '(1980) 4) Illinois DOT Geotechnical Pile Design Guide, AGMU 10.2 (2011)']),
 ('7-14',
  7,
  '7.2.1.4',
  271,
  5,
  ['Weak carbonate Siltstone/Sandstone (coral detrital limestone); N.A.; 106.7; 1.',
   'Limestone; H-pile; 240.0; 2.',
   'Weak calcareous Sandstone; Pipe Pile; 62.6; 1.',
   'Sandstone; H-pile; 200.0; 2.',
   'Shale; H-pile; 120.0; 2.',
   'Information sources: 1) Tomlinson and Woodward (2015) 2) Illinois DOT Geotechnical Pile Design Guide, '
   'AGMU 10.2 (2011)']),
 ('7-15',
  7,
  '7.2.1.5',
  275,
  19,
  ['AllPile; Navfac DM-7; No; No',
   'A-Pile; API-RP2A; Yes; No',
   'A-Pile; Lambda Method; No; Yes',
   'DrivenPiles; Nordlund Method; Yes; Yes',
   'FB-Deep; Schmertmann (CPT); Yes; Yes',
   'Unipile; Beta Method; Yes; Yes, but differs',
   'Unipile; Meyerhof (SPT); No; Yes']),
 ('7-17',
  7,
  '7.2.9',
  305,
  4,
  ['Scour Design Check Flood Frequency, QC. Q10; Q25; Q50',
   '| Q25; Q50; Q100',
   '| Q50; Q100; Q200',
   '| Q100; Q200; Q500',
   'columns: Hydraulic Design Flood Frequency, QD']),
 ('7-18',
  7,
  '7.3.1',
  310,
  2,
  ['Limiting Angular Distortion, Sd/Ls (radians)',
   'Multi-span bridges; 0.004',
   'Simple-span bridges; 0.005',
   'columns: Type of Bridge',
   '(p. 310)']),
 ('7-19',
  7,
  '7.3.5.4',
  326,
  9,
  ['Time Factor (T). 10; 0.008', '20; 0.031', '50; 0.197', '70; 0.403', '80; 0.567', '90; 0.848']),
 ('7-20',
  7,
  '7.3.5.6',
  333,
  14,
  ['Glacial Till; Very Dense to Dense; 1000-300; 1.0',
   'Gravel; ---; 400-40; 0.5',
   'Sand; Loose; 150-100; 0.5',
   'Silt; Dense; 200-80; 0.5',
   'Silty Clay & Clayey Silt; Hard-Stiff; 60-20; 0',
   'Marine Clay; Soft; 20-5; 0',
   'Peat; ---; 5-1; 0']),
 ('7-21',
  7,
  '7.3.7.3',
  358,
  5,
  ['Soft Clay; 0.25-0.50; 0.02',
   'Medium Clay; 0.50-1.0; 0.01',
   'Stiff Clay; 1.0-2.0; 0.007',
   'Very Stiff Clay; 2.0-4.0; 0.005',
   'Hard Clay; 4.0-8.0; 0.004']),
 ('7-22',
  7,
  '7.3.7.3',
  359,
  11,
  ['Soft Clay; 0.25-0.50; ---; 30; ---',
   'Stiff Clay; 1.0-2.0; ---; 500; 200',
   'Hard Clay; 4.0-8.0; ---; 2000; 1000',
   'Loose Sand; ---; Submerged; 20; 20',
   'Med Dense Sand; ---; Above; 90; 90',
   'Dense Sand; ---; Above; 225; 225']),
 ('7-23',
  7,
  '7.3.7.6',
  367,
  13,
  ['Stiff Clay; Field Study; 3b; 0.70, 0.50, 0.40; 2; Brown et al. (1987)',
   'Stiff Clay; Field Study; 3.3b; 0.82, 0.61, 0.45; 3.5; Rollins et al. (2006)',
   'Stiff Clay; Field Study; 5.65b; 0.95, 0.88, 0.77; 2.6; Rollins et al. (2006)',
   'Medium Clay; Scale Model-Cyclic Load; 3b; 0.60, 0.45, 0.40; 2.4 at 50 cycles; Moss (1997)',
   'V. Dense Sand; Field Study; 3b; 0.80, 0.40, 0.30; 1; Brown et al. (1988)',
   'Loose M. Sand; Centrifuge Model; 3b; 0.65, 0.45, 0.35; 3; McVay et al. (1995)',
   'Loose F. Sand; Field Study; 3b; 0.80, 0.70, 0.30; 1-3; Ruesta et al. (1997)']),
 ('7-24',
  7,
  '7.3.7.6.1',
  373,
  9,
  ['Jet grouting below cap.; 15’ x 10.5’ x 10’; 58.3; 282; 500; 160 [as printed',
   '38.1; 214; 398; 185',
   'Soil mixing adjacent to cap.; 4’ x 11’ x 10’; 16.3; 282; 170; 60',
   '13.5’ x 8.8’ x 6’; 26.4; 232; 24; 10',
   '14.6’ x 8.75’ x 3.5’; 16.6; 232; 40; 18',
   '13, 2.5 dia x 13’ deep; 29.5; 285; 40; 14',
   '13, 2.5’ dia. X 10.5 deep; 23.6; 50; 35; 70']),
 ('7-25',
  7,
  '7.3.7.6.1',
  373,
  9,
  ['Jet grouting below cap.; $28,500; $84,200; $55,700; 57',
   'Jet grouting adjacent to cap.; $38,000; $69,360; $31,360; 95',
   'Weak flowable fill below cap.; $3,180; $4,335; $1,155; 133',
   'Compacted fill to edge of cap.; $544; $4,335; $3,791; 24',
   '$4,225; $8,670; $4,445; 106',
   '$4,225; $8,670; $4,445; 121']),
 ('7-26',
  7,
  '7.4.2.1',
  379,
  6,
  ['A; Hard rock with measured shear wave velocity, v̄s > 5,000 ft/s.',
   'B; Rock with 2,500 ft/sec < v̄s < 5,000 ft/s.',
   'N̄ > 50 blows/ft, or s̄u > 2.0 ksf.',
   '15 < N̄ < 50 blows/ft, or 1.0 < s̄u < 2.0 ksf.',
   'PI > 20, w > 40 percent and s̄u < 0.5 ksf.',
   'Very thick soft/medium stiff clays (H >120 ft).',
   'v̄s = average shear wave velocity; N̄ = average SPT N- value; s̄u = averageundrained shear strength [as '
   'printed; no space between the two words]; w = moisture content; PI = Plasticity Index']),
 ('7-27',
  7,
  '7.4.2.1',
  380,
  6,
  ['Site Class; PGA < 0.1; PGA = 0.2; PGA = 0.3; PGA = 0.4; PGA > 0.5',
   'A; 0.8; 0.8; 0.8; 0.8; 0.8',
   'C; 1.2; 1.2; 1.1; 1.0; 1.0',
   'D; 1.6; 1.4; 1.2; 1.1; 1.0',
   'E; 2.5; 1.7; 1.2; 0.9; 0.9',
   'F; *; *; *; *; *']),
 ('7-28',
  7,
  '7.4.2.1',
  380,
  6,
  ['Site Class; Ss < 0.25; Ss = 0.5; Ss = 0.75; Ss = 1.0; Ss > 1.25',
   'A; 0.8; 0.8; 0.8; 0.8; 0.8',
   'C; 1.2; 1.2; 1.1; 1.0; 1.0',
   'D; 1.6; 1.4; 1.2; 1.1; 1.0',
   'E; 2.5; 1.7; 1.2; 0.9; 0.9',
   'F; *; *; *; *; *']),
 ('7-29',
  7,
  '7.4.2.1',
  380,
  6,
  ['Site Class; S1 < 0.1; S1 = 0.2; S1 = 0.3; S1 = 0.4; S1 > 0.5',
   'A; 0.8; 0.8; 0.8; 0.8; 0.8',
   'C; 1.7; 1.6; 1.5; 1.4; 1.3',
   'D; 2.4; 2.0; 1.8; 1.6; 1.5',
   'E; 3.5; 3.2; 2.8; 2.4; 2.4',
   'F; *; *; *; *; *']),
 ('7-30',
  7,
  '7.4.2.1',
  382,
  4,
  ['columns: Acceleration Coefficient, SD1; Seismic Zone',
   'SD1 ≤ 0.15; 1',
   '0.15 < SD1 ≤ 0.30; 2',
   '0.30 < SD1 ≤ 0.50; 3',
   '0.50 < SD1; 4']),
 ('7-31',
  7,
  '7.4.2.2',
  384,
  5,
  ['columns: Percent Passing #200 Sieve; Ncorr',
   '0-9; 0',
   '10-24; 1',
   '25-49; 2',
   '50-74; 4',
   '> 75; 5 [as printed']),
 ('7-32',
  7,
  '7.6',
  390,
  6,
  ['Q (kips); 200',
   'ϕdyn; 0.65',
   'Rn (kips); 308',
   'Rscour (kips); 50',
   'Rrelax (kips); 154',
   'Rndr (kips); 512'])]


def _sections(sections):
    for s in sections:
        yield s
        yield from _sections(s.get("subsections") or [])


def _entry(chapter, section_id, table):
    data = json.loads((TEXT / f"chapter{chapter:02d}.json").read_text(encoding="utf-8"))
    for s in _sections(data["sections"]):
        if s["section_id"] == section_id:
            hits = [t for t in s.get("tables") or [] if t.startswith(f"Table {table}:")]
            assert len(hits) == 1, f"Table {table} not listed once in {section_id}"
            return hits[0]
    raise AssertionError(f"section {section_id} not in chapter {chapter}")


_IDS = [t[0] for t in TABLES]


@pytest.mark.parametrize("table,chapter,section_id,page,rows,cells", TABLES, ids=_IDS)
def test_label_and_printed_page(table, chapter, section_id, page, rows, cells):
    entry = _entry(chapter, section_id, table)
    assert entry.startswith(f"Table {table}: ")
    assert f"(p. {page})" in entry


@pytest.mark.parametrize("table,chapter,section_id,page,rows,cells", TABLES, ids=_IDS)
def test_printed_cells_and_notes(table, chapter, section_id, page, rows, cells):
    entry = _entry(chapter, section_id, table)
    assert len(cells) >= 5
    for cell in cells:
        assert cell in entry, f"Table {table}: {cell!r} not in the stored entry"


@pytest.mark.parametrize("table,chapter,section_id,page,rows,cells", TABLES, ids=_IDS)
def test_row_count(table, chapter, section_id, page, rows, cells):
    entry = _entry(chapter, section_id, table)
    assert entry.count(" | ") >= rows - 1


def test_every_table_listed_once():
    assert len(set(_IDS)) == len(_IDS)
