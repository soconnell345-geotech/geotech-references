"""GEC-13 printed tables typed into the chapter text (app BACKLOG REF-97).

Each table of FHWA-NHI-16-027 / -028 below was read off the printed page
(rendered at 300 dpi) and typed into its section's ``tables`` entry as
'Table N: caption (p. page) - columns: a; b. row; cell | row; cell. Notes: ...'.
The values asserted here are the printed ones: the header, the first and
last rows, rows between, each printed note, and each place where the print
itself slips (kept as printed and marked '[as printed; ...]').
"""
import json
import pathlib
import re

import pytest

from geotech_references._retrieval import retrieve_section

TEXT = pathlib.Path(__file__).resolve().parents[1] / "geotech_references" / "gec_13" / "text"

# (table, section, printed page, rows, cells and rows, notes, print slips, caption on the page when the stored caption differs)
CASES = [('2-2',
  '2.3.1.1',
  'p. 2-18',
  4,
  ['Installation Method; Method Options',
   'Static; 1. Chain Driven* 2. Sprocket Driven* 3. Cable Pull-down* 4. Heavy Weight 5. Hydraulic Piston '
   'Push',
   'Vibratory; 1. Offset Hammer - full supported mandrel* 2. Direct Hammer - offset mandrel* 3. Inside '
   'Mandrel with Enlarged Shoe',
   'Jetting; 1. Covered Mandrel with Outside Jets 2. Jet Probe with No Covering Mandrel',
   'System Combination; 1. Static with Vibratory* 2. Static with Jetting* 3. Vibratory with Jetting',
   '1. Static with Vibratory* 2. Static with Jetting* 3. Vibratory with Jetting'],
  ['* Currently used in the United States.'],
  [],
  None),
 ('2-3',
  '2.6.2',
  'p. 2-51',
  3,
  ['Site Category; Unit Price Range',
   'Small; $0.70 to $4.00 per lineal foot',
   'Medium; $0.50 to $1.00 per lineal foot',
   'Large; $0.30 to $0.50 per lineal foot',
   '$0.30 to $0.50 per lineal foot',
   'Large'],
  [],
  [],
  None),
 ('2-4',
  '2.7.1.4',
  'p. 2-53',
  4,
  ['Area; Estimated Linear feet; Estimated No',
   'of PVDs; Installed Linear feet; Installed No. of PVDs; No. of Days to Install. 3; 231,000; 6,600; '
   '129,494; 5,850; 9',
   '2; 374,000; 9,350; 234,192; 8,111; 13',
   '8; 85,750; 2,450; 74,391; 2,367; 4',
   'Total; 690,750; 18,400; 438,077; 16,328; 26',
   '26'],
  ['Source: Menard Group USA'],
  [],
  None),
 ('2-5',
  '2.7.3.4',
  'p. 2-62',
  1,
  ['Area; Estimated No',
   'of PVDs; Estimated Length of PVDs incl. Cut-Offs; Estimated Linear Feet of PVDs; Installed Linear Feet; '
   'No. of Installed PVDs; No. of Days to Install. 1; 12,468; 37; 461,316; 446,840; 12,468; 20',
   '20',
   '12,468',
   '446,840',
   '461,316'],
  [],
  [],
  None),
 ('3-2',
  '3.4.2.1.1',
  'p. 3-26',
  3,
  ['EPS Block Density (pcf); CBR (%); Young’s Modulus (psi); Resilient Modulus (psi)',
   '1.25; 2; 725; 725',
   '1.5; 3; 1015; 1015',
   '2.0; 4; 1450; 1450',
   '1450',
   '4'],
  [],
  [],
  None),
 ('3-3',
  '3.4.2.1.1',
  'p. 3-27',
  4,
  ['Item; Guideline',
   'Design Parameters; Density, Dry: 0.75 to 2.0 pcf Compressive and Flexural Strength: Varies with density, '
   '6 to14 psi Modulus of Elasticity: 580 to 1450 psi California Bearing Ratio (CBR): 2 to 4 Coefficient of '
   'Lateral Earth Pressure: Lateral pressures from adjacent soil mass may be reduced to a ratio of 0.1 of '
   'horizontal to vertical pressure (PIARC 1997).',
   'Environmental Considerations; There are no known environmental concerns. No decay of the material occurs '
   'when placed in the ground.',
   'Design Considerations; EPS blocks will absorb water when placed in the ground. Blocks placed below water '
   'have resulted in densities of 4.8 to 6.4 pcf after 10 years. Blocks above the water had densities of 1.9 '
   'to 3.2 pcf after 10 years. For settlement and stability analyses, use the highest densities to account '
   'for water absorption. Buoyancy forces must be considered for blocks situated below the water table. '
   'Adequate cover should be provided to result in a minimum safety factor of 1.3 against uplift. Because '
   'petroleum products will dissolve geofoam, a geomembrane or a reinforced concrete slab is used to cover '
   'the blocks in roadways in case of accidental spills. Differential icing potential of pavement, due to a '
   'cooler pavement surface above the EPS versus pavement above a soil only subgrade. Differential icing can '
   'be minimized by providing a sufficient thickness of soil between the EPS and top of pavement surface. '
   'Use side slopes less than or equal to 2H:1V and a minimum cover thickness of 0.8 feet. If a vertical '
   'face is needed, cover exposed face of blocks with shotcrete or other material to provide long-term UV '
   'protection.',
   'Construction Considerations; The subsoil should be leveled before placement of geofoam blocks. A layer '
   'of sand/gravel is frequently placed as a leveling course. When multiple layers of geofoam blocks are '
   'placed, the blocks should be placed at right angles to avoid continuous vertical joints and to promote '
   'interlocking. See Figure 3-9. A minimum of two layers of blocks must be used. Provide a mechanical '
   'connection between blocks using a galvanized barked plate for shear transfer. Place cover material over '
   'geofoam blocks as soon as possible to prevent displacement from wind or buoyancy. Avoid prolonged '
   'exposure to sunlight, which embrittles EPS.',
   'The subsoil should be leveled before placement of geofoam blocks. A layer of sand/gravel is frequently '
   'placed as a leveling course. When multiple layers of geofoam blocks are placed, the blocks should be '
   'placed at right angles to avoid continuous vertical joints and to promote interlocking. See Figure 3-9. '
   'A minimum of two layers of blocks must be used. Provide a mechanical connection between blocks using a '
   'galvanized barked plate for shear transfer. Place cover material over geofoam blocks as soon as possible '
   'to prevent displacement from wind or buoyancy. Avoid prolonged exposure to sunlight, which embrittles '
   'EPS.'],
  [],
  [],
  None),
 ('3-4',
  '3.4.2.1.2',
  'p. 3-30',
  4,
  ['Item; Guideline',
   'Design Parameters; Wet Density Range: 20 to 80 pcf Compressive Strength Range: 10 to 300 psi, depending '
   'on density Water Absorption:1.4 to 15 psf, depending on density Freeze-thaw Resistance, 100 Cycles: 92 '
   'to 98%, depending on density Coefficient of Lateral Earth Pressure: Negligible for vertical loads '
   'applied directly over the foamed concrete. Lateral pressures from adjacent soil mass may be transmitted '
   'undiminished.',
   'Environmental Considerations; There are no known environmental concerns.',
   'Design Considerations; Dry density values will be lower than wet density values. Buoyancy could be a '
   'problem if foamed concrete is placed below the water table and there is not sufficient vertical '
   'confinement. The lower compressive strength mixes are affected by freeze-thaw cycles. The product should '
   'be used below the zone of freezing or a higher compressive strength used. Densities greater than 37 pcf '
   'have reported excellent freeze-thaw resistance. There is some absorption of water into the voids, which '
   'could affect the density and compressive strength. Saturation by water should be prevented by '
   'construction of a drainage blanket and drains.',
   'Construction Considerations; A staging area is required for batching, mixing, and placing on site. The '
   'foamed concrete is very fluid; formwork should be tight to avoid flow of the mix through joints or gaps '
   'in the forms. Polyethylene film may be used to prevent leakage. If the foamed concrete is placed in a '
   'confined area, forms are not necessary, as the fluid mix will flow to completely fill the void. The lift '
   'thickness should not exceed 4 feet, as the heat of hydration would have an adverse effect on the foam. '
   'Allow a minimum 12-hour waiting period between lifts. No special provisions for cold joints are '
   'necessary, although each lift surface should be scarified and clean. If shaping is required, the lift '
   'thickness should be limited to 2 feet to allow workers to shape the surface while wading in the fluid '
   'mix.',
   'formwork should be tight to avoid flow of the mix through joints or gaps in the forms. Polyethylene film '
   'may be used to prevent leakage. If the foamed concrete is placed in a confined area, forms are not '
   'necessary, as the fluid mix will flow to completely fill the void. The lift thickness should not exceed '
   '4 feet, as the heat of hydration would have an adverse effect on the foam. Allow a minimum 12-hour '
   'waiting period between lifts. No special provisions for cold joints are necessary, although each lift '
   'surface should be scarified and clean. If shaping is required, the lift thickness should be limited to 2 '
   'feet to allow workers to shape the surface while wading in the fluid mix.'],
  [],
  [],
  None),
 ('3-5',
  '3.4.2.2',
  'p. 3-31',
  5,
  ['Item; Guideline',
   'Design Parameters; Dry Density: 21 to 53 pcf loose and 30-73 pcf compacted, with various of gradations '
   'and reporting sources Angle of Shearing Resistance: 19° to 30° Cohesion Intercept: 100 to 230 psf, use 0 '
   'for design Compressibility: 5 to 40 percent vertical strain over a range of 200 to 4,200 psf vertical '
   'stress Permeability: 0.5 to 60 cm/sec Type A Gradation (ASTM D6270): 8-inch maximum dimension; 100% '
   'passing 4-inch, a minimum of 95% passing 3-inch, a maximum of 50% passing the 1.5-inch, and a maximum of '
   '5% passing the 0.2-inch sieve Coefficient of Lateral Earth Pressure: 0.25 to 0.47',
   'Environmental Considerations; The design considerations listed below address minimizing leachate '
   'generation and transport from tire shred fills. See NCHRP 435 (Stroup-Gardiner and Wattenberg-Komas '
   '2013d), ASTM (2012), Minnesota DOT (Edstrom et al. 2008), Washington DOT (Baker et al. 2003) for '
   'additional information and discussion on environmental considerations.',
   'Combustion Potential; The tire shred gradation and design considerations were developed, in part, to '
   'prevent combustion of tire shred fills. These design details prevent or minimize the amount of '
   'infiltration of water and air into tire shred fill.',
   'Design Considerations; Limit layers to 10 feet in thickness. Keep the tire shred fill above the water '
   'table. Provide good surface drainage of roadway surface to avoid water seepage through the shredded-tire '
   'fill. Tire shreds should be separated from the surrounding soil by completely wrapping with a '
   'geotextile. Metal fragments must be firmly attached to the chips, with 98 percent embedded in the rubber '
   'to prevent exposed wire strands from puncturing tires or construction equipment. Place a minimum 3-foot '
   'thick soil cap on the top and side slopes of the tire chip fill to minimize pavement deflections and '
   'provide confinement. Place 2-foot soil surcharge for 60 days to minimize post construction settlement '
   'due to compressibility of tire shreds. Top of tire shred embankment should be a minimum of 5 feet below '
   'the top of subgrade elevation. Multiple 10-foot tire shred layers should be separated by 3 feet of soil '
   'fill. Drainage pipes beneath the fill should be located at least 3 feet below the bottom of the of the '
   'tire shred layer. Drainage features that could provide free access to air should be avoided at the '
   'bottom of the fill.',
   'Construction Considerations; Spread using a track-mounted dozer in a lift thickness of 3 foot or less. '
   'Compact using sheep’s foot rollers, smooth drum rollers, or by repeated passes with a D-8 dozer. Use '
   'multiple passes of compaction equipment, since compressibility decreases after 5 to 8 cycles of loading. '
   'Anticipate 35 percent volume reduction during compaction, plus 10 percent shrinkage under loading of '
   'soil cover and pavement base course.'],
  [],
  [],
  None),
 ('3-6',
  '3.4.2.2',
  'p. 3-32',
  4,
  ['Item; Guideline',
   'Design Parameters; Moist Density: 45 to 60 pcf Angle of Shearing Resistance: Sawdust – 25° to 27° '
   'Hogfuel – 31° Wood Chips – 30° to 49° Permeability: 1 x 10^-5m/s Compressibility: Loose volume reduces '
   '40 percent on compaction. Vertical subgrade reaction coefficient: 1300 to 1450 psi in top 2 feet, '
   'roughly corresponding to a CBR of 1',
   'Environmental Considerations; Potential environmental effects of the leachate include: depletion of '
   'available dissolved oxygen in groundwater. lowering of groundwater pH because of acidic nature of '
   'leachate, which has pH of 4 to 6. potential contamination of water with toxins. Methods to reduce '
   'contamination include: reducing water infiltration into wood fiber by drains and capping. treatment of '
   'leachate. barriers between wood fiber fill and adjacent bodies of water.',
   'Design Considerations; Restrict particle size to 6 inches maximum to prevent development of large voids. '
   'Less than 30 percent should be finer than 0.5 inches to minimize the use of fine uniform sawdust. Use '
   'fresh wood fiber to prolong the life of the fill. Use side slopes of 1.5H:1V or flatter. Employ surface '
   'treatment with cover material of thickness 2 feet or more to protect slope from erosion and minimize '
   'deterioration of wood fibers. Restrict height of fill to about 16 feet and reduce air penetration into '
   'wood to minimize the possibility of spontaneous combustion.',
   'Construction Considerations; Truck-mounted equipment is used to spread fiber in 12 to 20-inch lifts. Two '
   'passes with a fully loaded hauling truck weighing 33 kips or more is usually sufficient to properly '
   'compact wood fiber.',
   'Truck-mounted equipment is used to spread fiber in 12 to 20-inch lifts. Two passes with a fully loaded '
   'hauling truck weighing 33 kips or more is usually sufficient to properly compact wood fiber.'],
  [],
  [],
  None),
 ('3-7',
  '3.4.2.2',
  'p. 3-33',
  4,
  ['Item; Guideline',
   'Design Parameters; Dry Density, Compacted: 50 to 65 pcf Dry Density, Loose: 40 to 54 pcf Angle of '
   'Shearing Resistance: 35° loose, 37° to 44° compacted Grain Size Gradation: 3/16 to 1 inch Permeability: '
   'High Coefficient of Subgrade Reaction: 33 to 37 pci loose, 140 to 155 pci compacted',
   'Environmental Considerations; There are no known environmental concerns.',
   'Design Considerations; The material will absorb some water after placement, when continually submerged. '
   'Samples compacted at a water content of 8.5 percent have been found after 1 year to have a water content '
   'of 28 percent. Over a longer period of time, the estimated long-term water content would be about 34 '
   'percent. Side slopes of embankments should be covered with a minimum of 2.5 feet of soil cover. Use side '
   'slopes of 1.5H to 1V or flatter to confine the material and provide internal stability. For calculating '
   'lateral earth pressures, use an angle of shearing resistance of 35°.',
   'Construction Considerations; Particle degradation can occur from steel-tracked construction equipment. '
   'Use 2 to 4 passes with rubber-tired rollers and lift thickness of 3 feet or less. Fill should be '
   'unloaded at side of fill area, then distributed with lightweight equipment with a contact pressure of '
   '4.5 psi or less. Field density may be approximated in the laboratory by conducting a modified one-point '
   'AASHTO T 272 density test.',
   'Particle degradation can occur from steel-tracked construction equipment. Use 2 to 4 passes with '
   'rubber-tired rollers and lift thickness of 3 feet or less. Fill should be unloaded at side of fill area, '
   'then distributed with lightweight equipment with a contact pressure of 4.5 psi or less. Field density '
   'may be approximated in the laboratory by conducting a modified one-point AASHTO T 272 density test.'],
  [],
  [],
  None),
 ('3-8',
  '3.4.2.2.a',
  'p. 3-34',
  4,
  ['Item; Guideline',
   'Design Parameters; Density Range, Compacted: 70 to 90 pcf Shear Strength: 33° to 40°, c = 0, for Type F; '
   'Class C is self-hardening, so the shear strength will vary as it cures Permeability: Range of 1 x 10^-6 '
   'to 1 x 10^-9 m/s Compressibility: Cc = 0.05 to 0.37, Ccr = 0.006 to 0.04 Grain Size Range: 0.005 to '
   '0.074 mm Specific Gravity: 1.9 to 2.5 Atterberg Limits: Non-plastic',
   'Environmental Considerations; The leachate is alkaline, with pH of 6.2 to 11.5. Calcium, sulfate, and '
   'boron are soluble constituents, which can leach and migrate. The EPA (Rittenhouse 1993) has stated fly '
   'ash as non-hazardous.',
   'Design Considerations; Where the groundwater table is high, a drainage blanket should be provided below '
   'the fly ash fill to promote a capillary cutoff and prevent frost heave and resiliency of the subgrade. '
   'Runoff from paved surfaces should be discharged into a drainage system. Surface waters from peripheral '
   'areas should be diverted away from the embankment to minimize infiltration into the fly ash. The side '
   'slope of embankments should be covered with at least 2 feet of soil to prevent erosion. If concrete is '
   'to be formed directly on fly ash, a polyethylene barrier should be placed on the fly ash to prevent '
   'moisture absorption from the fresh concrete and to serve as a moisture barrier. Use fly ash in the '
   'concrete to reduce sulfate attack.',
   'Construction Considerations; Fly ash behaves like silt, thus, dusting will occur when dry, and '
   'compaction is difficult when wet. Some means for adding water should be available on site to keep the '
   'water content near optimum for compaction. Surface protection to minimize erosion may be required. '
   'Compaction is obtained with smooth drum vibratory rollers or self-propelled, pneumatic-tired rollers. '
   'Use 10-inch lifts and compact the fly ash immediately after spreading. The use of test strips to develop '
   'the most efficient compaction procedures is advisable.',
   'Fly ash behaves like silt, thus, dusting will occur when dry, and compaction is difficult when wet. Some '
   'means for adding water should be available on site to keep the water content near optimum for '
   'compaction. Surface protection to minimize erosion may be required. Compaction is obtained with smooth '
   'drum vibratory rollers or self-propelled, pneumatic-tired rollers. Use 10-inch lifts and compact the fly '
   'ash immediately after spreading. The use of test strips to develop the most efficient compaction '
   'procedures is advisable.'],
  [],
  [],
  None),
 ('3-9',
  '3.4.2.2.a',
  'p. 3-35',
  4,
  ['Item; Guideline',
   'Design Parameters; Compacted Moist Density: 70 to 94 pcf, varies with size and gradation Gradation: Can '
   'be graded to any specified size from 4 inches down. Angle of Shearing Resistance: 35° to 40° '
   'Permeability and Compressibility: Depends on final specified gradation. Generally similar to gravel and '
   'sand.',
   'Environmental Considerations; Slag contains small amounts of sulfur in combined alkaline compounds. The '
   'pH of water in contact with slag is generally in the range of 8 to 12, which tends to inhibit corrosion. '
   'Some washing of the aggregate may be required to control the pH to 11 or less to meet AASHTO '
   'specifications. There are no known environmental concerns.',
   'Design Considerations; The slag behavior is similar to natural angular gravel and sand deposits. The '
   'highest internal stability occurs for aggregate that is well graded with a maximum particle size of 16 '
   'inches. The amount passing #200 sieve should be limited to 5 to 7 percent. However, the density '
   'increases for well-graded materials. If lightweight fill is desirable, uniformly graded materials should '
   'be specified. Absorption in slag is usually in the range of 1 to 6 percent by weight. Slag is highly '
   'resistant to weathering and abrasion, and can be placed below the water table and next to lakes and '
   'rivers.',
   'Construction Considerations; Slag can be placed and compacted in the same manner as natural gravel and '
   'sand.',
   'Slag can be placed and compacted in the same manner as natural gravel and sand.'],
  [],
  [],
  None),
 ('3-10',
  '3.4.2.2.a',
  'p. 3-36',
  4,
  ['Item; Guideline',
   'Design Parameters; Dry Density, Loose: 60 to 78 pcf Dry Density, Compacted: 82 to 102 pcf Optimum '
   'Moisture: 8 to 20% (Stroup-Gardiner and Wattenberg-Komas 2013b) Angle of Shearing Resistance: 38° to 42° '
   'Coefficient of Permeability: 0.3 to 0.9 mm/s Grain Size Range (Percent Passing): 90 to 99% on #4, 62 to '
   '89% on #8, 16 to 46% on #16, 4 to 23% on #30, 2 to 12% on #50, 1 to 7% on #100, and 0 to 5% on #200 '
   '(Stroup-Gardiner and Wattenberg-Komas 2013b) Atterberg Limits: Non-plastic Compressibility: Comparable '
   'to sand, at same relative density',
   'Environmental Considerations; After 4 days of soaking, the pH of the water solution is generally in the '
   'range of 6.7 to 7.0. Barium has been detected by toxicity tests, but at levels well below the EPA '
   'specified standard. There are no known environmental concerns with the use of this material.',
   'Design Considerations; The aggregate is durable and satisfies acceptable limits for soundness tests. The '
   'aggregate works well as an underdrain filter material, provided the gradation requirements are met. Side '
   'slopes should be covered with a minimum of 2 feet of cover material since exposed material has low '
   'stability. Specify standard proctor compaction, AASHTO T 99, since some degradation occurs during '
   'laboratory compaction in accordance with AASHTO T 180.',
   'Construction Considerations; Compact with several passes of a pneumatic roller or a smooth-drum, '
   'vibratory roller. Keep water content at or above optimum water content, as determined by AASHTO T 99. 6 '
   'to 10 passes are usually sufficient. Material must be kept wet since there could be a loss in stability '
   'when material dries.',
   'Compact with several passes of a pneumatic roller or a smooth-drum, vibratory roller. Keep water content '
   'at or above optimum water content, as determined by AASHTO T 99. 6 to 10 passes are usually sufficient. '
   'Material must be kept wet since there could be a loss in stability when material dries.'],
  [],
  [],
  None),
 ('3-11',
  '3.6.1',
  'p. 3-41',
  1,
  ['Material; Material Cost/yd^3 FOB at source; Delivered Material Cost/yd^3 FOB at Project; In-Place '
   'Cost/yd^3',
   'EPS-block geofoam; $40 to $80; $40 to $80; $40 to $100 [as printed; Table 3-12 on the same page prints '
   '$40 to $60 at source and $60 to $125 delivered for EPS-block geofoam]',
   'Table 3-12 on the same page prints $40 to $60 at source and $60 to $125 delivered for EPS-block geofoam]',
   '$40 to $100 [as printed',
   '$40 to $80',
   'EPS-block geofoam'],
  [],
  ['[as printed; Table 3-12 on the same page prints $40 to $60 at source and $60 to $125 delivered for '
   'EPS-block geofoam]'],
  None),
 ('3-12',
  '3.6.1',
  'p. 3-41',
  9,
  ['Lightweight Fill; Material Cost/yd^3 FOB at source; Delivered Material Cost/yd^3 FOB at Project; '
   'In-Place Cost/yd^3',
   'EPS-block geofoam; $40 to $60; $60 to $125; $40 to $100',
   'Wood Fiber; n/d; $6 to $26; $8 to $30',
   'Expanded blast furnace slag; $11 to $15; n/d; n/d',
   'Fly ash; $12 to $16; n/d; n/d',
   'Tire shreds; n/d; $15 to $30; n/d'],
  ['n/d = no data'],
  [],
  None),
 ('3-13',
  '3.6.1',
  'p. 3-42',
  6,
  ['Material; Total Cost*',
   'Traditional Soil Fill; $563K',
   'Pumice Rock; $633K',
   'Expanded Shale Clay; $490K',
   'Wood Chips; $545K',
   'Tire-derived Aggregate; $334K'],
  ['* Total costs based on material, transportation and longevity costs; does not include installation costs '
   'or contractor’s overhead and profit. Source: Cheng 2016'],
  [],
  None),
 ('4-1',
  '4.2.2.3',
  'p. 4-34',
  4,
  ['Tamper Weight; Crawler Crane Size; Cable Size',
   '8 to 16 kips; 80 to 100 kips; ¾ to ⅞ inch',
   '16 to 28 kips; 100 to 200 kips; ⅞ to1 inch',
   '30 to 36 kips; 200 to 250 kips; 1 to 1⅛ inch',
   '36 to 50 kips; 300 to 350 kips; 1¼ to 1½ inch',
   '1¼ to 1½ inch'],
  [],
  [],
  None),
 ('4-2',
  '4.2.3.3.1',
  'p. 4-44',
  5,
  ['Soil Type; Standard Penetration Resistance (blows/12 inches); Static Cone Tip Resistance (tsf); '
   'Pressuremeter Limit Pressure (tsf)',
   'Pervious coarse-grained soil: sands and gravel; 30 to 50; 200 to 300; 20 to 25',
   'Semipervious soil: sandy silts; 25 to 35; 135 to 177; 14.6 to 20',
   'Semipervious soil: silts and clayey silts; 20 to 35; 104 to 135; 10.4 to 14.6',
   'Partially saturated impervious deposits: clay fill and mine spoil; 20 to 40*; N/A; 14.6 to 20',
   'Landfills; 15 to 40*; N/A; 5.2 to 10.4'],
  ['* Higher test values may occur because of large particles in the soil mass. Source: FHWA 1986'],
  [],
  None),
 ('4-4',
  '4.2.5.1',
  'p. 4-52',
  4,
  ['Size of Tamper Required kips; Unit Cost Dollars/ft^2',
   '4 to 8; 1.10 to 1.50',
   '8 to 16; 1.50 to 2.00',
   '16 to 20; 2.00 to 3.00',
   '20 to 90; Negotiated for each job',
   'Negotiated for each job'],
  [],
  [],
  None),
 ('4-5',
  '4.3.1.3.1',
  'p. 4-66',
  7,
  ['Soil Type; USCS; Comments on Suitability for VC',
   'Gravel, well graded; GW; Well suited for VC, potential penetration difficulties with less powerful '
   'machines',
   'Gravel, poorly graded; GP; If D60/D10 ≤ 2 compaction only marginal (trail compaction recommended)',
   'Sand, well graded; SW; Ideally suited',
   'Sand, silty; SM; Compaction inhibited if silt content >8%',
   'Sand, clayey; SC; Compaction inhibited if clay content >2%'],
  ['Sources: Kirsch and Kirsch 2010 and Degen 1997'],
  [],
  None),
 ('4-6',
  '4.3.2.1',
  'p. 4-70',
  8,
  ['Vibrator; Length m; Dia',
   'mm; Weight kg; Motor kW; Speed rpm; Ampl. mm; Dynamic Force kN. Bauer TR13; 3.1; 300; 1000; 105; 3250; '
   '6; 150',
   'Keller M; 3.3; 290; 1600; 50; 3000; 7.2; 150',
   'Keller A; 4.3; 290; 1900; 50; 2000; 13.8; 160',
   'Vibro V23; 3.6; 350; 2200; 130; 1800; 23; 300',
   'Vibro V32; 3.6; 350; 2200; 130; 1800; 32; 450'],
  ['Source: Layne Christiansen Company.', 'Note: See table at front of manual for SI conversions.'],
  [],
  None),
 ('4-7',
  '4.3.2.2',
  'p. 4-73',
  5,
  ['Suitability Number; Rating',
   '0 to 10; Excellent',
   '10 to 20; Good',
   '20 to 30; Fair',
   '30 to 40; Poor',
   '>50; Unsuitable [as printed; the rows leave suitability numbers from 40 to 50 without a rating]'],
  ['Source: Brown 1977'],
  ['[as printed; the rows leave suitability numbers from 40 to 50 without a rating]'],
  None),
 ('4-8',
  '4.3.3.1',
  'p. 4-74',
  7,
  ['Penetration Resistance; Very Loose; Loose; Medium Dense; Dense; Very Dense',
   'SPT N-value (blows/foot)*; < 4; 4 to 10; 10 to 30; 30 to 50; > 50',
   'CPT cone resistance (kg/cm^2 or tsf); < 50; 50 to 100; 100 to 150; 150 to 200; > 200',
   'Dry Unit Weight (pcf); < 90; 90 to 100; 100 to 115; 115 to 130; > 130',
   'Cyclic Stress Ratio Causing Liquefaction**; < 0.04; > 0.04 to 0.12; > 0.12 to 0.33; > 0.33 to 0.40; '
   '(empty)',
   'Shear Wave Velocity (ft/s)***; < 400; 400 to 525; 525 to 650; 650 to 740; > 750 [as printed; Dense ends '
   'at 740 and Very Dense starts above 750]'],
  ['* Normally consolidated sand.', '** Seed et al. 1983.', '*** Debats and Sims 1997'],
  ["[as printed; the page shows '30 to 3235', and the cells beside it, '< 30' and '35 to 40', leave 30 to 35 "
   'for Loose]',
   '[as printed; Dense ends at 740 and Very Dense starts above 750]'],
  None),
 ('4-9',
  '4.3.5.1',
  'p. 4-85',
  5,
  ['Category; Factors',
   'In situ Material; • Type of Material • In situ Density • In situ Cementation',
   'Backfill Material; • Type • Cost',
   'Densification Requirements; • Load Bearing • Degree of Densification 1. Average relative density 2. '
   'Minimum relative density',
   'Project Requirements; • Size • Depth of Densification • Overburden • Type 1. Footing compaction 2. Area '
   'compaction • Specifications • Location of Project 1. Labor and union considerations 2. Support equipment '
   'availability 3. Weather - freezing weather conditions',
   'Pricing; • Compaction Spacing • Unit Pricing 1. Linear foot 2. Cubic yard'],
  [],
  [],
  None),
 ('4-10',
  '4.3.5.2',
  'p. 4-86',
  3,
  ['Pay Item Description; Quantity Range; Unit; Low Unit Price; High Unit Price; Factors Which May '
   'Potentially Impact Costs',
   'Mobilization; 1; LUMP SUM; $20,000; $30,000; Mobilization cost increases for distances greater than 500 '
   'miles. Phased projects may require multiple mobilizations.',
   'Vibrocompaction; Greater than 2,500; LF; $5.00; $9.00; Production rates increase as depth increases. In '
   'situ density of soils impacts the average production rate.',
   'Granular Fill Material; –; TON; $7.00; $20.00; Material specifications and haul distance will impact '
   'unit costs.',
   'Material specifications and haul distance will impact unit costs.',
   '$20.00'],
  [],
  [],
  None),
 ('5-1',
  '5.5.2.3',
  'p. 5-57',
  10,
  ['Test; Granular; Cohesive; Comments',
   'Dynamic Cone; 2; 1; Too insensitive to reveal clay lenses. Can locate dense layers and buried features.',
   'Electric Cone; 4; 2; Particle size important. Can be affected by lateral earth pressures generated by '
   'treatment. Best test for seismic liquefaction evaluation.',
   'Pressuremeter; 3; 1; Rarely used.',
   'Large Plate Load Test; 2; 2; Better confining action.',
   'Full-Scale; 5; 5; Rare'],
  ['Note: Suitability ranking varies from 1 as least suitable to 5 as most suitable.'],
  [],
  None),
 ('5-2',
  '5.6.0',
  'p. 5-60',
  5,
  ['Pay Item Description; Quantity Range; Unit; Low Unit Price; High Unit Price; Factors that May Impact '
   'Costs',
   'Aggregate Columns; Greater than 1,000; LF; $20.00; $60.00; Cost of aggregate materials is sensitive to '
   'material specification and haul distance. Unit costs will decrease as total quantity increases. Typical '
   'price range is $20 to $40 per lineal foot.',
   'Mobilization; 1; Rig; $20,000; $100,000; Mobilization cost increases for distances greater than 500 '
   'miles. Phased construction may require multiple mobilizations. High price for rigs for moderate depth '
   'treatment is $40,000.',
   'Embankment; Greater than 5,000; CY; Use agency data; Use agency data; Use historical costs that are '
   'representative of the project quantity, project conditions and project location',
   'Working Platform Geosynthetic; Greater than 5,000; SY; $1.00; $3.50; Geogrids are more expensive than '
   'geotextiles Heavier geotextiles cost more Specified overlap widths impact the total quantity of material '
   'required.',
   'Granular Fill Material; Greater than 2,500; Tons; $7.00; $20.00; Material specification and haul cost '
   'will impact costs'],
  [],
  [],
  None),
 ('6-1',
  '6.3.1.1',
  'p. 6-15',
  12,
  ['Column Type; Range of Allowable Capacity (kips); Typical Lengths (feet); Typical Column Diameters '
   '(inches)',
   'Timber pile; 25 to 100; 20 to 60; 12 to 18',
   'Pre-cast concrete piles; 100 to 450; 30 to 50; 10 to 24',
   'Continuous Flight Auger piles; 75 to 150; 20 to 75; 12 to 24',
   'VCC; 50 to 300; 20 to 90; 18 to 24',
   'CMC; 50 to 150; 20 to 90; 12 to 24'],
  [],
  [],
  None),
 ('6-2',
  '6.4.7',
  'p. 6-39',
  5,
  ['Ω; Reinforcement Strain (ε)%', '2.07; 1', '1.47; 2', '1.23; 3', '1.08; 4', '0.97; 5'],
  ['Source: Young et al. 2003'],
  [],
  None),
 ('6-3',
  '6.7.2.2',
  'p. 6-51',
  6,
  ['Stratum; Description; N60 Avg',
   '(blows/ft); Depth from Existing Grade (ft). I; Mixture of Sand, Silt and Clay; 15; 0 to 50',
   'II; Slightly Organic Silty Clay Loam; 9; 50 to 110',
   'IV; Slightly Organic Silty Clay Loam; 11; 125 to 150',
   'V; Sand with some Gravel; 75+; 150 to 185',
   'VI; Bedrock; --; 185+'],
  [],
  [],
  'Brief Summary of US 61 Project Stratigraphy'),
 ('8-2',
  '8.2.3.5.2',
  'p. 8-38',
  9,
  ['Component; Grout A; Grout B; Grout C',
   'Water; 25 quarts (Liters); 86 quarts (Liters); 51 quarts (Liters)',
   'Grouting material*; 44 lbs. (20 kg); 132 lbs. (60 kg); (empty)',
   'Delvo; 0.8 quarts (Liters); (empty); (empty)',
   'Sodium silicate; (empty); (empty); 45 quarts (Liters)',
   'Grout hole positions; 1 – 3; 4 – 7; 8 – 12'],
  ['[as printed; each volume is one number for both quarts and liters, and the page prints no note for the '
   "asterisk on 'Grouting material*']"],
  ['[as printed; each volume is one number for both quarts and liters, and the page prints no note for the '
   "asterisk on 'Grouting material*']"],
  None),
 ('8-3',
  '8.2.4.5.2',
  'p. 8-46',
  6,
  ['Constituent; Weight',
   'Masonry sand; 1,350 lb.',
   'Top soil (silt); 1,350 lb.',
   'Fly Ash; 432 lb.',
   'Retarder; 24 ounces',
   'Water; 40 gallons'],
  [],
  [],
  'Grout Mix Used for Apache Trail Grouting'),
 ('8-4',
  '8.2.4.5.2',
  'p. 8-48',
  5,
  ['Seismic Volume Improvement Factor, SVIF (m/s); Pay Factor',
   'SVIF < -100; 0.90',
   '-100 < SVIF < -50; 0.95',
   '-50 < SVIF < 50; 1.0',
   '50 < SVIF < 100; 1.10',
   'SVIF > 100; 1.20'],
  [],
  [],
  None),
 ('8-5',
  '8.2.5.4.1',
  'p. 8-51',
  4,
  ['Material; Mix Proportions (lb./cubic feet); Mix Proportions (kg/m^3)',
   'Cement; 37 – 47; 600 – 750',
   'Fly ash; 11 – 14; 180 – 220',
   'Sand; 134 – 144; 2150 – 2300',
   'Water; 33 – 37; 525 – 600',
   '525 – 600'],
  [],
  [],
  None),
 ('8-7',
  '8.2.7.4',
  'p. 8-72',
  2,
  ["Description; Unlimited Headroom (< 36 feet) [as printed; the 'unlimited' headroom is given as less than "
   '36 feet]; Restricted Headroom (10 feet to 13 feet)',
   'Underpinning and excavation support 3.0 to 3.6 feet diameter per/yard of depth; $95 – $550; $490 – $650',
   'Seepage control 3.0 to 3.6 ft. diameter per/yard of depth; $30 – $115; $30 – $200',
   '$30 – $200',
   '$30 – $115',
   'Seepage control 3.0 to 3.6 ft. diameter per/yard of depth'],
  [],
  ["[as printed; the 'unlimited' headroom is given as less than 36 feet]"],
  None),
 ('8-8',
  '8.2.7.4',
  'p. 8-73',
  2,
  ['Pay Item Description; Quantity Range; Unit; Low Unit Price; High Unit Price; Factors Which May '
   'Potentially Impact Costs',
   'Mobilization; 1; LUMP SUM; $25,000; $150,000; Equipment mobilized includes: drill rig(s), compressor(s), '
   'grout mixers, and pumps. Mobilization cost increases for distances greater than 500 miles. Phased '
   'projects may require multiple mobilizations.',
   'Jet Grouting; Greater than 500; CY; $100; $750; Grout cost is sensitive to the grout mixture '
   'proportions, particularly the quantity of Portland cement required per cubic yard. Unit costs are far '
   'higher for locations which have headroom constraints.',
   'Grout cost is sensitive to the grout mixture proportions, particularly the quantity of Portland cement '
   'required per cubic yard. Unit costs are far higher for locations which have headroom constraints.',
   '$750',
   '$100'],
  [],
  [],
  None),
 ('8-9',
  '8.2.8.5.2',
  'p. 8-82',
  2,
  ['(empty); Downstage; Upstage',
   'Advantages; • Ground is consolidated from top down, aiding hole stability, packer seating, and allowing '
   'successively higher pressures to be used with depth without fear of surface leakage. • Depth of hole '
   'need not be pre-determined: grout take analyses may dictate changes from foreseen, and shortening or '
   'lengthening of hole can be easily accommodated. • Stage length can be adapted to conditions as '
   'encountered to allow “special” treatment.; • Drilling in one pass. • Grouting in one repetitive '
   'operation without significant delays. • Less wasteful of materials. • Permits materials to be varied '
   'readily. • Easier to control and program. • Stage length can be varied to treat “special” zones. • Often '
   'cheaper, since net drilling output rate is higher.',
   'Disadvantages; • Requires repeated moving of drilling rig and redrilling of set grout: therefore, '
   'process is discontinuous and may be more time consuming. • Relatively wasteful of materials, and so '
   'generally restricted to cement-based grouts. • May lead to significant hole deviation. • Collapsing '
   'strata will prevent effective grouting of whole stage, unless circuit grouting method can be deployed. • '
   'Weathered and/or highly variable strata problematical. • Packer may be difficult to seat in such '
   'conditions.; • Grouted depth predetermined. • Hole may collapse before packer introduced or after '
   'grouting starts, leading to stuck packers and incomplete treatment. • Grout may escape upwards into '
   '(nongrouted) upper layers or the overlying dam, either by hydrofracture or bypassing packer. Smaller '
   'fissures may not then be treated efficiently at depth. • Artesian conditions may pose problems. • '
   'Weathered and/or highly variable strata problematical.',
   '• Grouted depth predetermined. • Hole may collapse before packer introduced or after grouting starts, '
   'leading to stuck packers and incomplete treatment. • Grout may escape upwards into (nongrouted) upper '
   'layers or the overlying dam, either by hydrofracture or bypassing packer. Smaller fissures may not then '
   'be treated efficiently at depth. • Artesian conditions may pose problems. • Weathered and/or highly '
   'variable strata problematical.',
   '• Requires repeated moving of drilling rig and redrilling of set grout: therefore, process is '
   'discontinuous and may be more time consuming. • Relatively wasteful of materials, and so generally '
   'restricted to cement-based grouts. • May lead to significant hole deviation. • Collapsing strata will '
   'prevent effective grouting of whole stage, unless circuit grouting method can be deployed. • Weathered '
   'and/or highly variable strata problematical. • Packer may be difficult to seat in such conditions.',
   'Disadvantages'],
  [],
  [],
  None),
 ('8-10',
  '8.3.2',
  'p. 8-111',
  5,
  ['Description; Viscosity (cP) – w/c ratio; Toxicity; Strength; Material Cost/Quart; Remarks',
   'Colloidal Solution: Silicates; Low (> 6 cP); Low; Med; > $0.13; Penetrates fine fissures',
   'Solution Grout: Lignosulfites; Med (> 8 cP); High; Low; > $0.26; Penetrates fine fissures',
   'Solution Grout: Polyurethane; High (> 400 cP); High; High; > $1.32; Penetrates large fissures',
   'Solution Grout: Acrylamides; Low (1.2 cP); High; Low; > $0.53; Penetrates very fine fissures',
   'Solution Grout: Acrylates; Low (1.2 cP); Low; Low; > $0.53; Penetrates very fine fissures'],
  [],
  [],
  None),
 ('8-11',
  '8.3.2.3',
  'p. 8-116',
  4,
  ['Type of Resin; Nature of Ground; Use/Application',
   'Acrylic; Granular, very fine soils Finely fissured rock; • Waterproofing by mass treatment • Gas '
   'tightening (mines, storage) • Strengthening up to 220 psi Strengthening of a granular medium subjected '
   'to vibrations',
   'Phenol; Granular, very fine soils; • Strengthening',
   'Aminoplastic; Schists and coals; • Strengthening (by adherence to materials of organic origin)',
   'Polyurethane; Large voids; • Formation of a foam that forms a barrier against running water (using '
   'water-reactive resins) • Stabilization or localized filling (using two-component resins)',
   '• Formation of a foam that forms a barrier against running water (using water-reactive resins) • '
   'Stabilization or localized filling (using two-component resins)'],
  [],
  [],
  None),
 ('8-12',
  '8.4.1.5',
  'p. 8-119',
  2,
  ['Type of Risk; Causes',
   'Schedule and Budget Risk; • Contractual issues between general and specialty contractor • Late notice to '
   'proceed • Weather delays • Site access problems • Material supply and storage problems • Equipment '
   'availability issues • Different site conditions',
   'Geotechnical Issues and/or Poor Soil Conditions; • Slope instability • Settlement • Liquefaction • '
   'Contamination • Problem soils, e.g., expansive clays • Impact on adjacent, existing structures',
   '• Slope instability • Settlement • Liquefaction • Contamination • Problem soils, e.g., expansive clays • '
   'Impact on adjacent, existing structures',
   'Geotechnical Issues and/or Poor Soil Conditions',
   '• Contractual issues between general and specialty contractor • Late notice to proceed • Weather delays '
   '• Site access problems • Material supply and storage problems • Equipment availability issues • '
   'Different site conditions'],
  [],
  [],
  None),
 ('8-13',
  '8.5.3.5',
  'p. 8-135',
  12,
  ['Physical Property; Test Method; Unit; Values',
   'Weight (Double Layer); ASTM D3776; lbs./ft.; 7.5',
   'Grab Tensile Strength; ASTM D4632; lb. ft./s^2 (lbf); 320 Warp – 300 Fill',
   'Trapezoidal Tear Strength; ASTM D4522; lbf; 130 Warp – 130 Fill',
   'Coefficient of Permeability; ASTM D4491; in./s; 0.9',
   'Porosity; ASTM D737; in.^3/min/in.^2; 300'],
  ["[as printed; the units are the page's, among them a thickness of 23 in., a weight of 7.5 lbs./ft., a "
   'water flow rate of 105 ft^3/s and a coefficient of permeability of 0.9 in./s, which a geotextile cannot '
   'have; the page gives nothing to correct them from]'],
  ["[as printed; the units are the page's, among them a thickness of 23 in., a weight of 7.5 lbs./ft., a "
   'water flow rate of 105 ft^3/s and a coefficient of permeability of 0.9 in./s, which a geotextile cannot '
   'have; the page gives nothing to correct them from]'],
  'PennDOT Minimum Required Properties for Polypropylene Geotextiles'),
 ('9-1',
  '9.1.0',
  'p. 9-2',
  5,
  ['Stabilization Method; Soil Type; Improvement; Remarks',
   'Thicker gravel; Silts and clays; None; Reduces dynamic stress level',
   'Blending; Moderately plastic Low or non-plastic; None Improved gradation Reduced plasticity Reduced '
   'breakage; Too difficult to mix',
   'Geosynthetics; Silts and clays; Minimize disturbance Strength gain through consolidation; Fast, plus '
   'provides long-term separation',
   'Lightweight fill; Very weak silts, clays, peats; None Thermal barrier for frost protection; Fast, and '
   'reduces dynamic stress level',
   'Recycled material; Silts and clays; None; To replace or blend with gravel; may be lightweight'],
  ['Source: Rollings and Rollings 1996'],
  [],
  None),
 ('9-2',
  '9.1.0',
  'p. 9-3',
  11,
  ['Stabilization Method; Soil Type; Improvement; Remarks',
   'Portland cement; High plasticity Coarse-grained; (empty); Less pronounced hydration of cement with high '
   'plasticity soils Hydration of cement with coarse-grained soils',
   'Lime; Coarse with fines; Same as for high plastic soils; Dependent on quantity of plastic fines',
   'Lime-cement-fly ash; Same as lime; Same as lime; Covers broader range than lime or cement alone',
   'Bituminous; Fines; None; Cannot mix',
   'Other chemical admixtures; Plastic; Strength increase and volume stability; See vendor literature '
   'Difficult to mix'],
  ['Source: Rollings and Rollings 1996'],
  [],
  None),
 ('9-3',
  '9.1.0',
  'p. 9-3',
  2,
  ['Stabilization Method; Soil Type; Improvement; Remarks',
   'Improved drainage; Sand, silt and wet, low plastic clays; Decreased moisture, increased strength; '
   'Requires time and grade for runoff',
   'Partial and full encapsulation (e.g., with geomembranes); Plastic and collapsible; Reduced change in '
   'moisture; Long-term moisture migration problem',
   'Long-term moisture migration problem',
   'Reduced change in moisture',
   'Plastic and collapsible'],
  ['Source: Rollings and Rollings 1996'],
  [],
  None),
 ('9-4',
  '9.1.3',
  'p. 9-15',
  12,
  ['Stabilization Method; Increased Support; Uniform Subgrade Support; Improve Drainage; Frost Protection; '
   'Reduce Subgrade Rutting Potential; Reduce Pumping/Erosion - PCC; Materials & Equipment Readily '
   'Available; Prevent Base/Subgrade Mixing; Treats Highly Plastic Soils; Treats Granular Soils; Treats '
   'Silts/Fine Sands; Treats Low PI Clays; Reduce Moisture; Reduce Swell; Potential Dust Problem; '
   'Freeze-Thaw Deterioration; Leaching over Time; Design Procedure; Cost; Increased Excavation/Subcutting',
   'More Gravel – Thicker Section; X; X; ?; X; X; X; X; (empty); X; X; X; X; (empty); (empty); (empty); '
   '(empty); (empty); (empty); (empty); X',
   'Lightweight Fill; (empty); X; (empty); X; (empty); (empty); (empty); (empty); X; (empty); X; X; (empty); '
   '(empty); (empty); (empty); (empty); (empty); (empty); X',
   'Cement Treatment; (empty); X; (empty); X; X; X; (empty); X; (empty); X; X; X; X; (empty); X; (empty); X; '
   '(empty); (empty); (empty)',
   'LCF Stabilization; (empty); X; (empty); X; X; X; (empty); X; (empty); X; (empty); (empty); X; (empty); '
   'X; (empty); X; (empty); (empty); (empty)',
   'Mechanical Stabilization – Compaction; X; X; (empty); (empty); X; (empty); X; (empty); (empty); X; X; '
   '(empty); X; (empty); (empty); (empty); (empty); (empty); (empty); X'],
  ['X=A benefit of the respective stabilization method. ?=A possible benefit of the respective stabilization '
   'method'],
  [],
  None),
 ('9-5',
  '9.2.3.2.1',
  'p. 9-31',
  3,
  ['Reliability Level (%); Reliability Factor Fr', '50; 1.00', '70; 1.44', '90; 2.32', '2.32', '90'],
  [],
  [],
  None),
 ('9-6',
  '9.3.3.2.1',
  'pp. 9-53 to 9-54',
  7,
  ['Requirement; Property; ASTM Test Method; Units; Requirement for Geotextile Class 2^1 and Elongation < '
   '50%^2; Requirement for Geotextile Class 2^1 and Elongation > 50%^2',
   'Survivability; Grab Strength; D4632; lb (N); 250 (1100); 157 (700)',
   'Survivability; Sewn Seam Strength^3; D4632; lb (N); 220 (990); 140 (630)',
   'Survivability; Puncture Strength; D6241; lb (N); 495 (2200); 309 (1375)',
   'Drainage and Filtration^4; Apparent Opening Size; D4751; mm; < 0.6 for < 50% passing No. 200 sieve; < '
   '0.3 for > 50% passing No. 200 sieve (both elongation columns)',
   'Drainage and Filtration^4; Permittivity; D4491; sec^-1; > 0.02 and > Permittivity of soil (both '
   'elongation columns)'],
  ['Source: FHWA 2008 (after AASHTO 2014a, but pre-2008 version of these AASHTO specifications).',
   '1 Default geotextile selection. The engineer may specify a Class 3 geotextile for moderate survivability '
   'conditions, see AASHTO M 288.',
   '2 As measured in accordance with ASTM D4632.',
   '3 When seams are required. Values apply to both field and manufactured seams.',
   '4 Also, the geotextile permeability should be greater than the soil permeability.',
   'Printed after the table (p. 9-54): The following should be noted for Table 9-6: Acceptance of geotextile '
   'material shall be based on ASTM D4759. Acceptance shall be based upon testing of either conformance '
   'samples obtained using Procedure A of ASTM D4354, or based on manufacturer’s certifications and testing '
   'of quality assurance samples obtained using Procedure B of ASTM D4354. All values are minimum values; '
   'use the value in the weaker principal direction. All numerical values represent minimum average roll '
   'values (i.e., test results from any sampled roll in a lot shall meet or exceed the minimum values in the '
   'table). Lot samples according to ASTM D4354.'],
  [],
  None),
 ('9-7',
  '9.3.3.2.2',
  'p. 9-55',
  7,
  ['Requirement; Property; ASTM Test Method; Units; Requirement for Geotextile Class 1^1 and Elongation < '
   '50%^2; Requirement for Geotextile Class 1^1 and Elongation > 50%^2',
   'Survivability; Grab Strength; D4632; lb (N); 315 (1400); 200 (900)',
   'Survivability; Sewn Seam Strength^3; D4632; lb (N); 280 (1260); 180 (810)',
   'Survivability; Puncture Strength; D6241; lb (N); 620 (2750); 433 (1925)',
   'Drainage and Filtration^4; Apparent Opening Size; D4751; mm; < 0.43 for < 50% passing No. 200 sieve, < '
   '0.3 for > 50% passing No. 200 sieve (both elongation columns)',
   'Drainage and Filtration^4; Permittivity; D4491; sec^-1; 0.5 for < 15% passing No. 200 sieve, 0.2 for 15 '
   'to 50% passing No. 200 sieve, 0.1 for > 50% passing No. 200 sieve (both elongation columns)'],
  ['Source: AASHTO 2014a.',
   '1 Default geotextile selection. The engineer may specify a Class 2 geotextile for moderate survivability '
   'conditions (see Table 9-9). [as printed; Table 9-9, p. 9-69, is the pavement design parameters for '
   'lightweight fill, and the Class 2 requirements are printed in Table 9-6, p. 9-53]',
   '2 As measured in accordance with ASTM D4632.',
   '3 When seams are required. Values apply to both field and manufactured seams.',
   '4 The geotextile permeability should be greater than the soil permeability.'],
  ['[as printed; Table 9-9, p. 9-69, is the pavement design parameters for lightweight fill, and the Class 2 '
   'requirements are printed in Table 9-6, p. 9-53]'],
  None),
 ('9-8',
  '9.3.3.2.2',
  'p. 9-60',
  5,
  ['Property; Test Method; Units; Requirement for Geogrid Class 1^1; Requirement for Geogrid Class 2; '
   'Requirement for Geogrid Class 3',
   'Ultimate Multi-Rib Tensile Strength; ASTM D6637; lb/ft (kN/m); 1230 (18); 820 (12); 820 (12)',
   'Junction Strength^5; GSI GRI GG2; lb (N); 25^2 (110^5); 25 (110); 8 (35)',
   'Ultraviolet Stability; ASTM D4355; %; 50% retained strength after 500 hours of exposure; 50% retained '
   'strength after 500 hours of exposure; 50% retained strength after 500 hours of exposure',
   'Aperture Size; Direct measure; in. (mm); 0.5 to 3-inch and Aperture Size ≥ D50 and ≤ 2 (D85) of '
   'aggregate above geogrid; 0.5 to 3-inch and Aperture Size ≥ D50 and ≤ 2 (D85) of aggregate above geogrid; '
   '0.5 to 3-inch and Aperture Size ≥ D50 and ≤ 2 (D85) of aggregate above geogrid',
   'Separation; ASTM D422; mm; D15 of aggregate above geogrid < 5 (D85) subgrade Otherwise use separation '
   'geotextile with geogrid; D15 of aggregate above geogrid < 5 (D85) subgrade Otherwise use separation '
   'geotextile with geogrid; D15 of aggregate above geogrid < 5 (D85) subgrade Otherwise use separation '
   'geotextile with geogrid'],
  ['Source: FHWA 2008.',
   '1 Default geogrid selection. For stabilization of soils, the default is Class 1. The engineer may '
   'specify a Class 2 or 3 geogrid for moderate survivability conditions (e.g., light weight construction '
   'equipment), based on one or more of the following: (a) The Engineer has found the class of geogrid to '
   'have sufficient survivability based on field experience. (b) The Engineer has found the class of geogrid '
   'to have sufficient survivability based on laboratory testing and visual inspection of a geogrid sample '
   'removed from a field test section constructed under anticipated field conditions (see note 2).',
   '2 Junction strength requirements have not been fully supported by data, and until such data is '
   'established, manufacturers shall submit data from full scale installation damage tests in accordance '
   'with ASTM D5818 documenting integrity of junctions. For soft soil applications, a minimum of 6 in. (150 '
   'mm) of cover aggregate shall be placed over the geogrid and a loaded dump truck used to traverse the '
   'section a minimum number of passes to achieve 4 in. (100 mm) of rutting. A photographic record of the '
   'geogrid after exhumation shall be provided, which clearly shows that junctions have not been displaced '
   "or otherwise damaged during the installation process. [as printed; the table marks 'Junction Strength' "
   "and '(110' with a note 5, and the page prints notes 1 and 2 only]"],
  ["[as printed; the table marks 'Junction Strength' and '(110' with a note 5, and the page prints notes 1 "
   'and 2 only]'],
  None),
 ('9-9',
  '9.4.3.1',
  'p. 9-69',
  8,
  ['Fill Type; Compacted Density Range (pcf); CBR; Resilient Modulus, MR',
   'Geofoam (EPS); 1 - 2; 2 to 4; 725 – 1450 psi',
   'Wood Fiber; 45 – 60; 1; 1500 psi',
   'Expanded Shale, Clay and Slate; 50 – 65; (empty); Similar to gravel',
   'Boiler Slag; 50 - 65; > 250; Similar to or better than gravel',
   'Air-Cooled Slag; 70 – 94; > 250; Similar to or better than gravel'],
  ['* Depends on density, values are estimated from unconfined strengths for 25 to 62 pcf.',
   '** Class F & Class C soaked CBR, but if not soaked, Class C will set-up and increase with time (e.g., up '
   'to CBR > 100)'],
  [],
  None),
 ('9-10',
  '9.8.3.2.1',
  'p. 9-123',
  5,
  ['Property; ASTM Test Method; Units; Geotextile Class 1 and Elongation < 50%; Geotextile Class 1 and '
   'Elongation ≥ 50%; Geotextile Class 2 and Elongation < 50%; Geotextile Class 2 and Elongation ≥ 50%',
   'Grab Strength; D4632; lb; 315; 200; 250; 157',
   'Seam Strength; D4632; lb; 260 [as printed; Table 9-7, p. 9-55, prints 280 (1260) for the sewn seam '
   'strength of the same class and elongation]; 180; 220; 140',
   'Tear Strength; D4533; lb; 110; 80; 90; 56',
   'Puncture Strength; D6241; lb; 620; 433; 495; 309',
   'Ultraviolet Stability (Retained Strength); D4355; %; 50% after 500 hours of exposure; 50% after 500 '
   'hours of exposure; 50% after 500 hours of exposure; 50% after 500 hours of exposure'],
  ['Source: AASHTO 2014a.',
   'Note: Elongation measured in accordance with ASTM D4632 with < 50% typical of woven geotextiles and > '
   '50% typical of nonwoven geotextiles.'],
  ['[as printed; Table 9-7, p. 9-55, prints 280 (1260) for the sewn seam strength of the same class and '
   'elongation]'],
  None),
 ('10-1',
  '10.2.3.2',
  'p. 10-12',
  12,
  ['Criteria; Parameter; Property',
   'Design Requirements: Mechanical; Tensile strength; Wide width strength',
   'Design Requirements: Mechanical; Tension creep; Tension creep',
   'Design Requirements: Hydraulic; Permeability; Permeability',
   'Constructability Requirements; Tear resistance; Trapezoidal tear',
   "Longevity; Soil compatibility (where required); Chemical, Biological [printed 'Chemical; Biological' in "
   'one cell]'],
  [],
  [],
  None),
 ('10-5',
  '10.3.3.4',
  'p. 10-35',
  3,
  ['U.S',
   'Sieve Size; Percent Passing(a). 4 inches (102 mm)(a, b); 100',
   'No. 40 (0.425 mm); 0-60',
   'No. 200 (0.075 mm); 0-15',
   '0-15',
   'No. 200 (0.075 mm)'],
  ['a. To apply default F* values, Cu, should be greater than or equal to 4.',
   'b. The maximum particle size for these materials be reduced to ¾-inch for geosynthetics, and epoxy and '
   'PVC coated steel reinforcements unless construction damage assessment tests are or have been performed '
   'on the reinforcement with the specific or similarly graded large size granular fill.'],
  [],
  None),
 ('10-6',
  '10.3.3.4',
  'p. 10-36',
  3,
  ['Property; Requirement',
   'Angle of Friction(a): (AASHTO T 236(b)); > 34°',
   'Plasticity Index, PI: (AASHTO T 90); PI < 6',
   'Soundness: (AASHTO T 104); The materials shall be substantially free of shale or other soft, poor '
   'durability particles. The material shall have a magnesium sulfate soundness loss of less than 30 percent '
   'after four cycles',
   'The materials shall be substantially free of shale or other soft, poor durability particles. The '
   'material shall have a magnesium sulfate soundness loss of less than 30 percent after four cycles',
   'Soundness: (AASHTO T 104)'],
  ['a. No testing is required for fills where 80% of sizes are greater than ¾-inch, and use of 34°.',
   'b. On the portion finer than the No. 10 sieve, utilizing a sample of the material compacted to 95% per '
   'AASHTO T99, Methods C or D, at optimum moisture content.'],
  [],
  None),
 ('10-7',
  '10.3.3.4',
  'p. 10-36',
  5,
  ['Property; Criteria; Test Method',
   'Resistivity; > 3000 ohm-cm; AASHTO T 288',
   'pH; > 5 and < 10; AASHTO T 289',
   'Chlorides; < 100 ppm; ASTM D4327',
   'Sulfates; < 200 ppm; ASTM D4327',
   'Organic Content; 1% max.; AASHTO T 267'],
  [],
  [],
  None),
 ('10-8',
  '10.3.3.4',
  'p. 10-36',
  2,
  ['Base Polymer; Property; Criteria; Test Method',
   'Polyester (PET); pH; 3 < pH < 9; AASHTO T 289',
   'Polyolefin (PP & HDPE); pH; pH > 3; AASHTO T 289',
   'AASHTO T 289',
   'pH > 3',
   'pH'],
  [],
  [],
  None),
 ('10-9',
  '10.3.3.4',
  'p. 10-37',
  5,
  ['U.S',
   'Sieve Size; Percent Passing. ½ inches (12.5 mm); 100',
   '3/8 inches (9.5 mm); 85-100',
   'No. 4 ((4.75 mm); 10-30',
   'No. 8 (2.36 mm); 0-10',
   'No. 16 (1.18 mm); 0-5'],
  [],
  [],
  None),
 ('10-10',
  '10.3.3.4',
  'p. 10-37',
  6,
  ['U.S',
   'Sieve Size; Percent Passing. ½ inches (12.5 mm); 100',
   '3/8 inches (9.5 mm); 90-100',
   'No. 8 (2.36 mm); 5-30',
   'No. 16 (1.18 mm); 0-10',
   'No. 50 (0.30 mm); 0-5'],
  [],
  [],
  None),
 ('10-12',
  '10.4.2.4',
  'p. 10-52',
  4,
  ['U.S',
   'Sieve Size; Percent Passing(a). 4 inches (102 mm)(a,b); 100',
   'No. 4 (4.76 mm); 100 – 20',
   'No. 40 (0.425 mm); 0 – 60',
   'No. 200 (0.075 mm); 0 – 50',
   '0 – 50'],
  ['a. To apply default F* values, Cu, should be greater than or equal to 4.',
   'b. The maximum particle size for these materials should be reduced to ¾-inch for geosynthetics, and for '
   'epoxy and PVC coated steel reinforcements unless construction damage assessment tests are or have been '
   'performed on the reinforcement combination with the specific or similarly graded large size granular '
   'fill.'],
  [],
  None),
 ('10-13',
  '10.4.2.4',
  'p. 10-52',
  2,
  ['Property; Requirement',
   'Plasticity Index, PI: (AASHTO T 90); PI ≤ 20',
   'Soundness: (AASHTO T 104); The materials shall be substantially free of shale or other soft, poor '
   'durability particles. The material shall have a magnesium sulfate soundness loss of less than 30 percent '
   'after four cycles.',
   'The materials shall be substantially free of shale or other soft, poor durability particles. The '
   'material shall have a magnesium sulfate soundness loss of less than 30 percent after four cycles.',
   'Soundness: (AASHTO T 104)',
   'PI ≤ 20'],
  [],
  [],
  None)]


def _entry(table, section_id):
    chapter = int(section_id.split(".")[0])
    data = json.loads((TEXT / f"chapter{chapter:02d}.json").read_text(encoding="utf-8"))
    section = next(s for s in data["sections"] if s["section_id"] == section_id)
    hits = [t for t in section["tables"] if t.startswith(f"Table {table}: ")]
    assert len(hits) == 1, (table, section_id)
    return hits[0]


IDS = [c[0] for c in CASES]


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_label_and_printed_page(case):
    table, section_id, page = case[:3]
    entry = _entry(table, section_id)
    assert re.match(rf"Table {table}: .+ \({re.escape(page)}\) - ", entry)
    assert " - columns: " in entry


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_cells_first_and_last_rows(case):
    table, section_id, _page, n_rows, cells = case[:5]
    entry = _entry(table, section_id)
    assert len(cells) >= 5
    for cell in cells:
        assert cell in entry, (table, cell)
    rows = entry.split(" - columns: ", 1)[1].split(". ", 1)[1]
    assert rows.startswith(cells[1])
    assert rows.count(" | ") >= n_rows - 1


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_notes_and_print_slips(case):
    table, section_id = case[:2]
    notes, slips, caption = case[5:]
    entry = _entry(table, section_id)
    for note in notes + slips:
        assert note in entry, (table, note)
    if caption:
        assert f"caption on the page: '{caption}'" in entry


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_section_fetch_returns_the_table(case):
    table, section_id = case[:2]
    got = retrieve_section("gec_13", section_id)
    assert _entry(table, section_id) in got["tables"]
    assert len(json.dumps(got, ensure_ascii=False)) < 14000


def test_real_symbols_not_text_layer_stand_ins():
    by = {c[0]: _entry(c[0], c[1]) for c in CASES}
    assert "D60/D10 ≤ 2" in by["4-5"]
    assert "Aperture Size ≥ D50 and ≤ 2 (D85)" in by["9-8"]
    assert "Elongation ≥ 50%" in by["9-10"]
    assert "> 34°" in by["10-6"]
    assert "PI ≤ 20" in by["10-13"]
    assert "Ω; Reinforcement Strain (ε)%" in by["6-2"]
    assert "¾ to ⅞ inch" in by["4-1"]


def test_checks_the_tables_allow():
    # Table 6-2: Ω falls as the strain rises.
    rows = re.findall(r"(\d\.\d\d); (\d)", _entry("6-2", "6.4.7"))
    assert [float(a) for a, _ in rows] == sorted((float(a) for a, _ in rows), reverse=True)
    assert [int(b) for _, b in rows] == [1, 2, 3, 4, 5]
    # Table 9-5: the reliability factor rises with the reliability level.
    rows = re.findall(r"(\d\d); (\d\.\d\d)", _entry("9-5", "9.2.3.2.1"))
    assert rows == [("50", "1.00"), ("70", "1.44"), ("90", "2.32")]
    # Table 4-6: eight vibrators, eight columns each.
    rows = _entry("4-6", "4.3.2.1").split("Dynamic Force kN. ", 1)[1].split(". Notes:")[0].split(" | ")
    assert len(rows) == 8 and all(len(r.split("; ")) == 8 for r in rows)
