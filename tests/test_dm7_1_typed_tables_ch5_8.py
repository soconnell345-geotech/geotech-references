"""UFS 3-220-10 (DM 7.1), chapters 5 to 8: the printed tables typed into the
chapter text (REF-97).

Every value asserted here was read off the printed page (rendered at 300 dpi),
the page named beside it.  Each case: the table's label, the section that
holds it, its printed page, cells including the first and the last row, and
each printed note.  Tables 5-6, 8-6, 8-9 and 8-24 are not here: coded lookups
return them and their entries stay labels.
"""
import json
from pathlib import Path

import pytest

TEXT = Path(__file__).resolve().parents[1] / "geotech_references" / "dm7_1" / "text"


def _entry(section_id, label):
    chapter = int(section_id.split("-")[0])
    data = json.loads((TEXT / f"chapter{chapter:02d}.json").read_text(encoding="utf-8"))
    sec = [s for s in data["sections"] if s["section_id"] == section_id]
    assert len(sec) == 1, section_id
    hits = [t for t in sec[0]["tables"]
            if t == label or t.startswith(label + ":") or t.startswith(label + " ")]
    assert len(hits) == 1, (section_id, label)
    return hits[0]


# label: (section, printed page as stored, cells / notes that must be there)
CASES = {
    # ---- chapter 5 ----
    "Table 5-1": ("5-1.4", "(p. 221)", [
        "Coarse-Grained; Short-Term; Distortion; Negligible to small; Semi-empirical immediate or “elastic” settlement",
        "Coarse-Grained; Short-Term; Consolidation; Small to moderate",
        "Coarse-Grained; Long-Term; Secondary Compression; Negligible to small; Semi-empirical methods",
        "Coarse-Grained; Other; Vibration, submergence; Small to moderate; Specialized methods",
        "Fine-Grained; Long-Term; Consolidation; Moderate to large; Primary consolidation calculations",
        "Fine-Grained; Long-Term; Secondary Compression; Small to large; Secondary consolidation calculations"]),
    "Table 5-2": ("5-4.1.1", "(p. 231)", [
        "Loose Sand, Dr = 40%; 200 to 400 ksf; 400 to 800 ksf",
        "Medium Dense Sand, Dr = 60%; 300 to 500 ksf; 500 to 1000 ksf",
        "Dense Sand, Dr = 80%; 400 to 600 ksf; 600 to 1200 ksf",
        "Dry or Moist Sand; Lower: Es = 11.5 (N′+7.5), Upper: Es = 15 (N′+30); Es = 20 (N′+42)",
        "Clayey, Silty, or Saturated Sand; Lower: Es = 5.6 (N′+9), Upper: Es = 7.7 (N′+15); Not available",
        "Note: Correlations provide values of Es in ksf units."]),
    "Table 5-3": ("5-4.1.2", "(p. 232)", [
        "Axisymmetric (L = B)", "Plane Strain (L/B > 10)",
        "Silt, sandy silt, slightly cohesive silt-sand mixtures; 10·N60; 14·N60",
        "Clean fine to medium sand, and slightly silty sand; 17.5·N60; 24.5·N60",
        "Coarse sand and sand with little gravel; 25·N60; 35·N60",
        "Sandy gravel; 30·N60; 42·N60"]),
    "Table 5-4": ("5-4.1.3", "(p. 234)", [
        "Terzaghi and Peck (1967); s = (6q0/N′)(B/(B+1))^2; s in inches, B in ft, q0 in ksf",
        "s = 2.5q0/((N′−1.5)CB)", "CB = 1.0 for B < 4 ft, Interpolate for 4 to 12 ft, 0.8 for B ≥ 12 ft",
        "s = B^0.75 (1.31/N′^1.4) q0Cs", "Cs = [1.25(L/B)/((L/B)+0.25)]^2", "Cs→1.56 for strip load",
        "A Settlement for load applied at the ground surface to normally consolidated sand."]),
    "Table 5-5": ("5-5.2.1", "(p. 240)", [
        "LL; Cc = 0.009·(LL – 10); Inorganic soils with sensitivity less than 4; Terzaghi and Peck (1967)",
        "e0; Cc = 1.15·(e0 – 0.35); All clays; Nishida (1956)",
        "e0; Cεc = 0.15·e0 + 0.017; All clays; Elnaggar and Krizek (1971)",
        "wn; Cεc =(0.1 + 0.006·(wn – 25)); Varved clays; Prior NAVFAC DM 7.1",
        "wn; Cc = 17.6×10^-5·wn^2 + 5.93×10^-3·wn – 0.135; Chicago clays; Peck and Reed (1954)",
        "wn; Cc = 0.01·wn – 0.05; Predominantly lean to fat clay; Azzouz et al. (1976)",
        "Note: Liquid limit (LL) and natural water content (wn) are in percent."]),
    "Table 5-7": ("5-6.2.1", "(pp. 257-258)", [
        "Small slab-on-grade structures – damage to structure; ---; 0.01; 1/100",
        "Steel frame with flexible siding; ---; 0.008; 1/125",
        "Safe limit – flexible brick walls (includes safety factor); > 4; 0.0067; 1/150",
        "Tilting of high buildings becomes visible; ---; 0.004; 1/250",
        "; ≥ 5; 0.002; 1/500", "; ≤ 3; 0.001; 1/1000",
        "Machinery sensitive to settlement; ---; 0.0013; 1/750",
        "Load-bearing brick, tile, or concrete block walls; ≥ 5; 0.0008; 1/1250",
        "Load-bearing brick, tile, or concrete block walls; ≤ 3; 0.0004; 1/2500"]),
    "Table 5-8": ("5-6.3", "(p. 260)", [
        "Circular; Km = 8 (Em(1−νs)^2/Es)(tm^3/B^3); Km ≤ 0.08; 0.08 ≤ Km ≤ 5; 5 ≤ Km",
        "Rectangular; Km = (4/3)(Em(1−νs)^2/(Es(1−νm)^2))(tm^3/B^3); Km ≤ 0.05; 0.05 ≤ Km ≤ 10; 10 ≤ Km",
        "Variables: Em = modulus of elasticity of mat, νm = Poisson’s ratio of mat",
        "tm = thickness of mat, B = diameter or width of mat (least dimension)"]),
    "Table 5-9": ("5-7", "(p. 261)", [
        "Reduce amount of soft soil; Removal and replacement, Partial displacement; Full or partial removal",
        "Reinforce soft soil; Column-supported embankments, Reinforced load transfer platforms",
        "Improve soft soil; Deep mixing methods, Vibro-compaction, Dynamic compaction",
        "Accelerate consolidation of soft soil; Surcharge, Pumping or vacuum, Electro-osmosis",
        "Prefabricated vertical drains (PVDs), Aggregate columns or sand drains; Vertical drainage elements",
        "Reduce applied load to soft soil; Balanced / compensated foundation, Lightweight granular fill, Geofoam or foamed concrete",
        "permanent excavation or the use of lightweight construction materials."]),
    "Table 5-10": ("5-8.3.1", "(p. 275)", [
        "1D Heave; Seed et al. (1962); X under Atterberg Limits, Grain-Size Distribution",
        "1D Heave; McCormack and Wilding (1975); X under Grain-Size Distribution, Initial State (γ, w)",
        "1D Heave; Cokca (2002); X under Atterberg Limits, Grain-Size Distribution, Initial Suction",
        "1D Heave; TXDOT (2014); X under Atterberg Limits, Grain-Size Distribution, Initial State (γ, w)",
        "Swell Pressure; Komornik and David (1969); X under Atterberg Limits, Initial State (γ, w)",
        "Swell Pressure; Sridharan and Gurtug (2004); X under Initial State (γ, w), Specific Gravity",
        "Swell Pressure; Erzin and Erol (2007); X under Atterberg Limits, Initial State (γ, w), Initial Suction"]),
    "Table 5-11": ("5-8.4", "(p. 277)", [
        "Alter the soil; Possible admixtures include lime, cement, or kiln dust.",
        "Wet compaction; Compaction on the “wet” side of the line of optimums results in degree of saturation greater than 80 to 85%.",
        "Control direction of swelling; Construct void zones within the foundation system, such as waffle slabs.",
        "Use a capillary break;", "Use a sealing compound; Asphaltic sealing compounds",
        "Balance swell pressure; For some structures",
        "may exceed the allowable bearing capacity of the soil."]),
    # ---- chapter 6 ----
    "Table 6-1": ("6-2.6.2", "(p. 294)", [
        "Specify head, Constant Head;", "Total head held at a constant value along the boundary",
        "Specify head, Constant Pressure;", "Seepage exits (pressure head = 0) Internal drains (pressure head = 0)",
        "Specify flow, No-Flow (impermeable boundary);", "Specify flow, Nodal Flow;", "Injection or extraction well",
        "Specify flow, Infiltration;",
        "Unknown or Variable; The boundary is set to be either a no-flow or constant pressure boundary",
        "such as the downstream slope of a dam or levee"]),
    "Table 6-2": ("6-2.6.2", "(p. 295)", [
        "Schematic of Seepage Regime; Model and Boundary Conditions",
        "Impermeable Dam; El.=100 upstream, El.=50 downstream", "Constant Head = 50",
        "Coffer Dam; El. = 100 outside each wall, El. = 40 between the walls", "Constant Head = 40 or Pressure = 0",
        "Permeable Dam or Levee; El. = 60", "Pressure =0",
        "No-flow boundary is appropriate if the model boundary represents the centerline of a river."]),
    "Table 6-3": ("6-3.3", "(p. 298)", [
        "Gravel, open-work; > 2", "Gravel (GP); 2x10^-1 to 2.", "Sand, medium (SP); 1x10^-3 to 1x10^-1",
        "Silt (ML); 1x10^-6 to 1x10^-3", "Clay (CL); < 3x10^-6",
        "Sandstone, medium; 1x10^-4 to 2x10^-1", "Granite, weathered; 2x10^-4 to 1x10^-5",
        "Limestone; < 1.5x10^-2", "Gneiss; < 2x10^-6",
        "Note: Materials with no indicated lower bound can range from practically impervious to the upper limit indicated in the table."]),
    "Table 6-4": ("6-3.3", "(pp. 298-299)", [
        "Core: GM-SM; < 1x10^-5", "SM-SC; < 3x10^-6", "ML-CL; < 1x10^-6", "MH; < 1x10^-7",
        "Shell: GP; 2x10^-3 to 1.0", "GW; 1x10^-3 to 1x10^-1", "SP (medium to coarse); 1x10^-2 to 2x10^-2",
        "SW; 3x10^-4 to 5x10^-3", "SM; 1x10^-5 to 5x10^-4.",
        "Note: Materials with no indicated lower bound can range from practically impervious to the upper limit indicated in the table."]),
    "Table 6-5": ("6-3.3", "(pp. 299-300)", [
        "βα (cm/sec/mm^2)",
        "Kenney et al. (1984); Sand and fine gravel, Cu = 1 to 12; 5; 1; 2",
        "Hazen (1892, 1911); Loose sands with D10 between 0.01 and 0.3 cm; 10; Varies by source from 0.01 to 10 Often taken to equal to 1; 2",
        "Slichter (1905) and (McCook 2010); Sands with D10 between 0.01 and 0.5 cm; 10; 0.0147 exp(9.3071e/(1 + e)); 2",
        "Chapuis (2004); Sand; 10; 2.4622(e^3/(1+e))^0.7825; 1.565",
        "Carrier (2003); Sand, assuming uniform spheres; 10; 5.52(e^3/(1+e)); 2",
        "Sherard et al. (1984); Sand and gravel with low fines content; 15; Average = 0.35, range = 0.2 to 0.6; 2",
        "Notes: k is estimated in cm/sec, Cu = coefficient of uniformity = D60 / D10, e = void ratio"]),
    "Table 6-6": ("6-3.4", "(p. 302)", [
        "Stratified Deposits; 10; 1000; Range of k for laminations",
        "Intact Soil or Rock; 1; 3; Particle shape and orientation",
        "Fractured Bedrock; 0.1; 10; Arrangement and orientation of apertures and joints",
        "Loess; 0.02; 2; Orientation of fissures and cracks that form during consolidation and desiccation",
        "kh / kv, Lower; kh / kv, Upper"]),
    "Table 6-7": ("6-3.4", "(p. 302)", [
        "Core Zone, USBR Compaction Procedures; 4; 9", "Core Zone, Standard Compaction Procedures; 9; 36",
        "Hydraulic Fill; 64; 225", "Embankment Shell, USBR Compaction Procedures; 4; 9",
        "Embankment Drains, USBR Compaction Procedures; 1; 4",
        "Note: USBR compaction procedures are based on Standard Proctor (ASTM D698).",
        "vary based on grain-size distribution and embankment height."]),
    "Table 6-8": ("6-5.1", "(p. 307)", [
        "q / hL / W (cfs per foot of head per foot of levee)",
        "> 2.2x10^-4; Heavy; Yes", "1.1x10^-4 to 2.2x10^-4; Medium; Possible",
        "2.2x10^-5 to 1.1x10^-4; Light; Marginal", "<2.2x10^-5; Negligible; Not Needed",
        "Notes: q = estimated volumetric flow rate, hL = head loss across the structure, W= width",
        "1 cfs/ft of head/ft. of levee = 44,883 gpm/ft of head/100 ft. of levee"]),
    "Table 6-9": ("6-5.2.1", "(pp. 309-310)", [
        "Steel Sheet Piles; Interlocking steel sheets are typically driven into the ground with a vibratory hammer",
        "Vinyl Sheet Piles; Interlocking vinyl sheets", "Continuous Slurry Trench Wall; Wall constructed in a continuous trench",
        "Element Slurry Wall; Continuous wall constructed by sequentially overlapping vertical elements.",
        "Vertical Membrane; Insertion of a geotextile membrane",
        "Deep Mixing Method; In situ soils are mixed in-place", "Deep mixing is limited to soil and very soft rock.",
        "Jet Grout Walls; Jet grout columns are constructed with a probe",
        "thus limiting its use to limited access and special needs projects."]),
    "Table 6-10": ("6-5.2.1", "(p. 311)", [
        "Soil-Bentonite (SB) Backfill; SB backfill consists of a mixture of the excavated soils and bentonite",
        "Cement-Bentonite (CB) Backfill; CB backfill is a self-hardening slurry",
        "Soil-Cement-Bentonite (SCB) Backfill; SCB backfill is often blended and placed similar to SB backfill",
        "Soil Cement; Soil cement is a term often used to describe the product of deep soil mixing.",
        "Plastic Concrete; Plastic concrete is conventional concrete with bentonite added",
        "Conventional Concrete; Conventional concrete adds a robust element",
        "resulting in cracking of the wall or surrounding soil."]),
    "Table 6-11": ("6-5.3.1", "(p. 320)", [
        "Percent Finer Than No. 200 Sieve (0.075-mm) (after re-grading where applicable)",
        "1; > 85; Fine silt and clays", "2; 40 –85; Sands, silts, clays, and silty sands",
        "3; 15 –39; Silty and clayey sands and gravels", "4; < 15; Sands and gravels"]),
    "Table 6-12": ("6-5.3.1", "(p. 320)", [
        "1; Max D15F ≤ 9·D85B, Max D15F ≥ 0.2 mm; Max D15F ≤ 6.5·D85B, Max D15F ≥ 0.2 mm",
        "2; Max D15F ≤ 0.7 mm; Max D15F ≤ 0.5 mm",
        "3; Max D15F ≤ [(40−A)/25][B−C]+C where: A = % passing No. 200 sieve, B = 4 × D85B ≥ 0.7 mm, and C = 0.7 mm",
        "B = 4 × D85B ≥ 0.5 mm, and C = 0.5 mm",
        "4; Max D15F ≤ 4·D85B; Max D15F ≤ 4·D85B",
        "Note: D85B and percent passing No. 200 sieve are determined after regrading."]),
    "Table 6-13": ("6-5.3.1", "(p. 321)", [
        "US Agency; Filter Permeability Criteria",
        "USBR; Min(D15F) ≥ 5·D15B", "USACE; Min(D15F) ≥ (3 to 5)·D15B", "NRCS; Min(D15F) ≥ (4 to 5)·D15B",
        "All; Min(D15F) ≥ 0.1 mm", "Note: D15B is determined prior to regrading."]),
    "Table 6-14": ("6-5.3.1", "(p. 321)", [
        "Minimum D10F (mm); Maximum D90F (mm)", "< 0.5; 20", "0.5 – 1.0; 25", "1.0 – 2.0; 30",
        "2.0 – 5.0; 40", "5.0 – 10; 50", "10 – 50; 60"]),
    "Table 6-15": ("6-5.3.2", "(p. 325)", [
        "Less than 10% fines and less than 90% gravel; Stable Soil (1 < Cc < 3)",
        "Widely Graded (C′u > 3); Loose Dr < 35%; O95 < (9/C′u) D′50B",
        "Medium dense 35% < Dr < 65%; O95 < (13.5/C′u) D′50B", "Dense 65% < Dr; O95 < (18/C′u) D′50B",
        "Unstable Soil (Cc < 1, 3 < Cc); Obtain Cu from straight line drawn through D30 and D10",
        "Uniformly Graded (C′u < 3); Loose Dr < 35%; O95 < C′u D′50B",
        "Medium dense 35% < Dr < 65%; O95 < 1.5·C′u D′50B", "Dense 65% < Dr; O95 < 2·C′u D′50B"]),
    # ---- chapter 7 ----
    "Table 7-1": ("7-3", "(p. 350)", [
        "Coarse-grained soils; Drained; s = σ′ff·tan(φ′);", "Coarse-grained soils; Undrained; s = ssu;",
        "Overconsolidated fine-grained soils; Drained; s = c′ + σ′ff·tan(φ′);",
        "Fine-grained soils (saturated); Undrained; s = su;",
        "Fine-grained soils (partially saturated); Undrained; s = c + σff·tan(φ);",
        "Note: σ′ff = effective stress on failure plane, φ′ = effective stress friction angle, c′ = effective cohesion",
        "ssu = undrained steady state shear strength, and su = undrained shear strength"]),
    "Table 7-2": ("7-8", "(p. 365)", [
        "Analysis Condition; Required Fmin; Slope",
        "End of Construction; 1.3; Upstream and downstream", "Steady state seepage (Long term); 1.5; Downstream",
        "Maximum pool level; 1.4; Downstream", "Rapid drawdown; 1.1 to 1.3; Upstream"]),
    "Table 7-3": ("7-8", "(p. 365)", [
        "determination of pore pressure and monitoring during construction.; 1.3",
        "during construction and no laboratory determination; 1.4",
        "End of construction; Undrained Strength; ; 1.3",
        "Steady-state seepage; Effective; Steady-state seepage under active conservation pool; 1.5",
        "Steady-state seepage under maximum reservoir level (during a probably maximum flood)",
        "Rapid drawdown from normal water surface to inactive water surface; 1.3",
        "probable maximum flood); 1.2",
        "Other; Effective or undrained; Drawdown at maximum outlet capacity (inoperable internal drainage; unusual drawdown); 1.2",
        "overall stability during construction).; 1.3"]),
    "Table 7-4": ("7-9.2", "(p. 368)", [
        "Slope < 1.2H:1V (θ < 40°) and H < 70 ft;", "4 in / 100, No. 4 / 20-100, No. 40 / 0-60, No. 200 / 0-50",
        "Plasticity Index ASTM D4318: PI ≤ 20",
        "1.2H:1V ≤ Slope < 0.36H:1V (40° ≤ θ ≤ 70°) and H < 70 ft;",
        "4 in / 100, No. 4 / 20-100, No. 40 / 0-60, No. 200 / 0-35", "Plasticity Index ASTM D4318: PI ≤ 10"]),
    "Table 7-5": ("7-9.2", "(p. 369)", [
        "Reinforcement; Primary and Secondary Reinforcement; Polyester (PET) and Polypropylene (PP) Geotextile",
        "Facing; Soft Armor Face (θ < 40°); Rolled Erosion Control Product (RECP)",
        "Facing; Hard Armor Face (θ ≥ 40°); Welded Wire Fabric (WWF)", "galvanized WWF 4x4-W4.0xW4.0 should be used",
        "Gravel; Fill soil immediately behind WWF; GP or GW with 1.0 in minimum particle size.",
        "Internal Drainage; Blanket Drain; Gravel; Drainage medium; Typically, ASTM C33 No. 57 or No. 67 stone.",
        "typically provide 33% to 75% coverage.",
        "External Drainage; Drainage Swale; RECP in form of Turf Reinforcement Mat (TRM)",
        "Locate swale 5 ft. to 10 ft. behind slope crest.", "Use bench with swale at mid-slope for H over 25 to 30 ft."]),
    "Table 7-6": ("7-9.5", "(p. 373)", [
        "Method of Including Reinforcement Strength; Factor of Safety Equation",
        "Method A (Active); F = shear strength / (shear stress required for equilibrum − reinforcement resistance)",
        "[as printed; 'equilibrum' for equilibrium]",
        "Method B (Passive); F = (soil strength+reinforcement resistance) / (shear stress required for equilibrium)"]),
    "Table 7-7": ("7-9.5", "(p. 374)", [
        "1; Draw a scaled cross section of the slope",
        "5; Select either Spencer’s method or the Morgenstern and Price method to analyses failure surfaces.",
        "then reduce the geogrid strength by FR = 1.3 or more.", "assume that Ci = 0.67.",
        "10; If the computer program provides an option, select 100% reinforcement coverage",
        "11; Assign layers of geosynthetic reinforcement to the cross section. Vertical spacing of 3 ft. is a good initial starting point.",
        "12; Set the length (L) of each layer of reinforcement to about 0.7·H.",
        "15; If a compound failure surface is indicated that has an unacceptably low F",
        "then increase the length of the reinforcement layers."]),
    "Table 7-8": ("7-10.8.2", "(p. 387)", [
        "Property; Criteria; Test Method", "Resistivity; >3000 ohm-cm; AASHTO T-288", "pH; >5 and <10; AASHTO T-289",
        "Chlorides; <100 ppm; ASTM D4327", "Sulfates; <200 ppm; ASTM D4327"]),
    # ---- chapter 8 ----
    "Table 8-1": ("8-2.1.1", "(p. 394)", [
        "Uniform sand, round grains; 27; 34", "Well-graded sand, angular grains; 33; 45", "Sandy gravel; 35; 50",
        "Silty sand; 27-33; 30-34", "Inorganic silt; 27-30; 30-35"]),
    "Table 8-2": ("8-2.1.1", "(p. 394)", [
        "Well-graded sand-gravel mixtures; GW; >38", "Poorly-graded sand-gravel mixtures; GP; >37",
        "Silty gravels, poorly-graded gravel-sand-silt; GM; >34", "Clayey gravels, poorly-graded gravel-sand-clay; GC; >31",
        "Well-graded clean sand, gravelly sand; SW; 38", "Poorly-graded clean sand, gravelly sand; SP; 37"]),
    "Table 8-3": ("8-2.1.2", "(p. 396)", [
        "Very Loose; < 20; < 4; < 20; < 30", "Loose; 20 - 40; 4 - 10; 20 - 40; 30 - 35",
        "Compact (Medium); 40 - 60; 10 - 30; 40 - 120; 35 - 40", "Dense; 60 - 80; 30 - 50; 120 - 200; 40 - 45",
        "Very Dense; > 80; > 50; > 200; > 45", "Static Cone Tip Resistance, qc (tsf)"]),
    "Table 8-4": ("8-2.1.2", "(p. 396)", [
        "V. Loose; < 15; < 4; < 50; < 30; < 14", "Loose; 15 - 35; 4 - 10; 50 - 100; 30 - 32; 14 - 16",
        "M. Dense; 35 - 65; 10 - 30; 100 - 150; 32 - 35; 16 - 18", "Dense; 65 - 85; 30 - 50; 150 - 200; 35 - 38; 18 - 20",
        "V. Dense; 85 - 100; > 50; > 200; > 38; > 20", "Dry Unit Weight (kN/m^3)",
        "^1 Freshly deposited, normally consolidated sand",
        "^2 Corrected to an effective vertical overburden pressure of 1 atm."]),
    "Table 8-5": ("8-2.1.3", "(p. 400)", [
        "Very loose; 0 – 26.1; 29 – 32", "Loose; 26.1 – 52.2; 32 – 35", "Medium; 52.2 – 104.4; 35 – 37",
        "Dense; 104.4 – 208.8; 37 – 40", "Very dense; > 208.8; 40 – 42"]),
    "Table 8-7": ("8-3.2", "(p. 423)", [
        "Mesri (1975); 0.22 ± 0.03; Collection of vane shear test results",
        "Jamiolkowski et al. (1985); 0.23 ± 0.04; Clays with PI less than 60",
        "Range: 0.16 to 0.33, High value: 0.74, Mean (all): 0.28, Mean (discard extreme values): 0.22 ± 0.05",
        "Sabatini et al. (2002); 0.16; Soils with horizontal layering or features",
        "Ladd and DeGroot (2004); 0.22+0.05(PI/100), Nominally 0.22;",
        "Ladd and DeGroot (2004); Nominally 0.25, Std. Dev. = 0.05; Sedimentary deposits of silts and organic soils",
        "Notes: PI = plasticity index, LI = liquid index.",
        "were not corrected as required by ASTM D2573 and may be too high."]),
    "Table 8-8": ("8-3.2", "(p. 423)", [
        "Less than 1; 0 – 0.1", "1; 0.10 – 0.25", "1 to 1.5; 0.26 – 0.50", "3; 0.51 – 1.00", "6; 1.00 – 4.00",
        "Greater than 6; > 4.00"]),
    "Table 8-10": ("8-3.4", "(p. 428)", [
        "Very soft; < 2; 300 [as printed;", "; -; < 250", "Soft; 2 – 4; 300 – 600; 250 – 500; 250 – 500",
        "Medium; 4 – 8; 600 – 1200; 500 – 1000; 500 – 1000", "Stiff; 8 – 15; 1200 – 2400; 1000 – 2000; 1000 – 2000",
        "Very stiff; 15 – 30; 2400 [as printed;", "Hard; > 30; > 4500; > 4000; > 4000"]),
    "Table 8-11": ("8-3.5", "(p. 429)", [
        "(su/σ′v)OC = (su/σ′v)NC (0.5KD)^1.25 ≈ 0.22(0.5KD)^1.25; Marchetti (1980)",
        "(su/σ′v)OC = 0.35(0.47KD)^1.14; Kamei and Iwasaki (1995)", "su = 0.018ED; Iwasaki and Kamei (1994)",
        "Undrained Strength Ratio or Undrained Shear Strength (kPa); Source",
        "Note: su = undrained shear strength in kPa, σ′v = vertical effective stress in kPa",
        "KD = horizontal stress index from dilatometer, and ED = dilatometer modulus in kPa."]),
    "Table 8-12": ("8-4.1.1", "(p. 430)", [
        "Boston Blue Clay, undisturbed (CL); 0.35; Lambe and Whitman (1969)", "Na-Montmorillonite (CH); 2.6;",
        "Organic silt and clayey silts (ML-MH); 1.5 – 4.0; Holtz and Kovacs (1981)", "Peat (Pt); 10 – 15;",
        "Mexico City Clay; 7 – 10;", "San Francisco Bay Mud (CL); 0.4 – 1.2;",
        "Uniform sand, loose (SP); 0.05 – 0.06; USACE (1990)", "Uniform silts (ML); 0.2; USACE (1990)"]),
    "Table 8-13": ("8-4.1.2", "(pp. 431-433)", [
        "Cc = 0.007(LL − 10); Remolded clays.; Skempton (1944)",
        "Cc = 0.009(LL − 10); Undisturbed clay of sensitivity less than 4. Reliability 30%; Terzaghi et al. (1996)",
        "Cc = 1.15(e0 − 0.91); All clays (Lower limit); Nishida (1956)",
        "Cc = 0.85(wn/100)^(3/2); Finnish muds and clays; Helenelund (1951)",
        "Cc = 0.135PI; Remolded clays; Wroth and Wood (1978)", "Cc = 0.005PI·Gs; ; [as printed;",
        "Cc = 0.5((1 + e0)/Gs)^2.4; Saturated clay; Al-Khafaji and Andersland (1992)",
        "Cc = 0.141Gs^1.2((1 + e0)/Gs)^2.382; Soils from nine states in USA; Rendon-Herrero (1983)"]),
    "Table 8-14": ("8-4.1.2", "(p. 434)", [
        "Cr = 0.0045LL; Marine clays of Southeast Asia; Cox (1968)", "Cr = 0.208e0 + 0.0083; Chicago clays; Peck and Reed (1954)",
        "Cr = 0.0043wnδVm; Marine clays of Southeast Asia; Cox (1968)",
        "Cr = 0.0039wn + 0.013 for wn < 100%; French clays; Vidalie (1977)", "Cr = PI/370; Remolded clays; Wroth and Wood (1978)",
        "Cr = 0.0033(e0wn + 12.5168) ) [as printed;",
        "Cr = 0.135(e0 + 0.01LL − 0.002wn − 0.06); Clays for Greece and USA; Azzouz et al. (1976)"]),
    "Table 8-15": ("8-4.2", "(p. 441)", [
        "Cεc = Cc / (1+e0) at Dr = 0%", "Medium to coarse sand (SW & SP); 0.010; 0.008; 0.006; 0.005; 0.003; 0.002",
        "Fine to coarse sand (SW); 0.011; 0.009; 0.007; 0.005; 0.003; 0.002",
        "Fine to medium sand (SW & SP); 0.013; 0.010; 0.008; 0.006; 0.004; 0.003",
        "Fine sand (SP); 0.015; 0.013; 0.010; 0.008; 0.005; 0.003",
        "Fine sand with little fine to coarse silt (SM); 0.017; 0.014; 0.012; 0.009; 0.006; 0.003"]),
    "Table 8-16": ("8-4.2", "(p. 441)", [
        "Monterrey 0; 0.854; 0.021; 0.085; 0.006", "Ticino; 0.917; 0.025; 0.130; 0.007",
        "Hokksund; 0.790; 0.018; 0.056; 0.005", "Ottawa; 0.560; 0.005; 0.100; 0.003",
        "Reid-Bedford; 0.650; 0.005; 0.019; 0.003", "Hilton Mines; 0.950; 0.038; 0.210; 0.009",
        "Hilton Mines; 0.732; 0.022; 0.100; 0.006"]),
    "Table 8-17": ("8-4.4", "(p. 447)", [
        "Inorganic clays and silts; Whangamarino clay; 0.03 – 0.04", "Inorganic clays and silts; Soft blue clay; 0.026",
        "Inorganic clays and silts; Hudson River silt; 0.03 – 0.06", "Organic clays and silts; Norfolk organic silt; 0.05",
        "Peats; Amorphous and fibrous peat; 0.035 – 0.083", "Peats; Canadian muskeg; 0.09 – 0.10",
        "Peats; Fibrous peat; 0.06 – 0.085"]),
    "Table 8-18": ("8-5.1", "(p. 449)", [
        "Parameter; E =; K =; G =; ν =", "E & G; ---; EG/(3(3G−E)); ---; (E−2G)/(2G)",
        "E & ν; ---; E/(3(1−2ν)); E/(2(1+ν)); ---", "E & K; ---; ---; 3KE/(9K−E); (3K−E)/(6K)",
        "G & ν; 2G(1+ν); 2G(1+ν)/(3(1−2ν)); ---; ---", "G & K; 9KG/(3K+G); ---; ---; (3K−2G)/(2(3K+G))",
        "K & ν; 3K(1−2ν); ---; 3K(1−2ν)/(2(1+ν)); ---"]),
    "Table 8-19": ("8-5.2.1", "(p. 450)", [
        "Very soft; 5 – 50; ", "Soft; 50 – 200; 15 – 40", "Medium; 200 – 500; 40 - 80",
        "Stiff or silty; 500 – 1000; 80 – 200", "Sandy; 250 – 2000; ", "Clay shale; 1000 – 2000; "]),
    "Table 8-20": ("8-5.3", "(p. 453)", [
        "Normalized Drained Young’s Modulus (Eu / Pa) [as printed;",
        "Loose; 100 – 200; 275 – 550; 100 – 250", "Medium; 200 – 500; 550 – 700; 250 – 1000",
        "Dense; 500 – 1000; 700 – 1100; 1000 – 2000", "Silty sand; ---; ---; 250 – 2000"]),
    "Table 8-21": ("8-5.3.1", "(p. 453)", [
        "E/Pa ≈ 7.1·(1 − ν^2)·N; Sandy soils; After Ferrent (1963)", "E/Pa ≈ 4.7(N+15); Sands; After Webb (1969)",
        "E/Pa ≈ 3.1(N+5); Clayey sands; After Webb (1969)",
        "E/Pa ≈ C(N+6); Silts with sand and gravels with sand with N < 15; Begemann (1974)",
        "E/Pa ≈ 39.5 + C(N−6); Silts with sand and gravels with sand with N ≥ 15; Begemann (1974)",
        "E/Pa ≈ 10N60; NC clean sands;", "E/Pa ≈ 15N60; OC clean sands; Kulhawy and Mayne (1990)",
        "Notes: E = drained Young’s modulus, Pa = atmospheric pressure (in same units as E)",
        "C = empirical coefficient equal to 3 for silts with sand and 12 for gravel with sand"]),
    "Table 8-22": ("8-6.1", "(p. 455)", [
        "CBR = 75/(1 + 0.728(FC × PI)); NCHRP (2001), FC×PI = 0", "CBR = 28.09·(D60)^0.358; NCHRP (2001), FC×PI = 0",
        "CBR = 95; NCHRP (2001), D60 ≥ 30 mm", "CBR = 5; NCHRP (2001), D60 ≤ 0.01 mm",
        "CBR = 23 + 1.42·γd − 0.213·PI − 0.916·w − 0.368·LL; George et al. (2009)",
        "CBR = 1.36×10^-8 (γm)^6.6141; Yashas et al. (2016)", "CBRsoaked = 1.93β − 31; Al-Hashemi and Bukhary (2016)",
        "Notes: FC = fines content = percent passing #200 sieve",
        "Gs = specific gravity of solids, and β = angle of repose"]),
    "Table 8-23": ("8-6.1", "(p. 455)", [
        "(after Singh et al. 2011)", "CBR = 33(γd/γd,max) − 5.5(w/wopt) − 1.15PL − 2.21",
        "CBRunsoaked = 24(γd/γd,max) − 67(w/wopt) − 2PL + 104.7",
        "γd,max = maximum dry unit weight from Modified Proctor test",
        "wopt = optimum water content from Modified Proctor test.",
        "Water contents should be either both in decimal or both in percentage form."]),
    "Table 8-25": ("8-7.1", "(p. 459)", [
        "Soil; Hydraulic Conductivity (m/sec); Relative Permeability", "Gravel; > 10^-3; High",
        "Sandy gravel; 10^-3 to 10^-5; Medium", "Dirty sand; 10^-5 to 10^-7; Low", "Silty clay; 10^-7 to 10^-9; Very low",
        "Clay; < 10^-9; Practically impermeable"]),
    "Table 8-26": ("8-8.1", "(p. 465)", [
        "131; 0.21; 0; Sand, use N60; Hasancebi and Ulusay (2007)", "89; 0.36; 0; Clay; Maheswari et al. (2010)",
        "57; 0.49; 0; Sand; Lee (1990)", "52; 0.52; 0; ; Iyisan (1996)", "59; 0.11; 0.43; ; Akin et al. (2011)",
        "69; 0.17; 0.20; Clay; Jamiolkowski et al. (1988)", "82; 0.25; 0.14; Gravel; Yoshida et al. (1988)"]),
    "Table 8-27": ("8-8.1", "(p. 465)", [
        "Equation; Reference", "Vs = 116(N+0.3185)^0.202; Jinan (1987)", "Vs,1 = 61.89(N1,60CS)^0.36; Ulmer et al. (2020)",
        "Vs,1 = normalized shear wave velocity = Vs·(Pa / σ′v)^0.25", "N1,60cs = N1,60 corrected for fine content"]),
    "Table 8-28": ("8-8.2", "(p. 467)", [
        "Vs = 134 + 0.0052qc; Sands; Sykora and Stokoe (1983)", "Vs = 0.1qc; Clays; Jaime and Romo (1988)",
        "Vs = (10.1log qc − 11.4)^1.67 (100fs/qc)^0.3; ; Hegazy and Mayne (1995)",
        "Vs = 1.75·qc^0.627; Clays; Mayne and Rix (1995)", "Vs = [10^(0.55Ic+1.68) (qt − σ′v/Pa)]^0.5; ; Robertson (2009)",
        "Vs,1 = 16.88(qc1NCS)^0.489; ; Ulmer et al. (2020)",
        "qc1 = normalized cone tip resistance = (qc / Pa) (Pa /σ′v)^n",
        "qc1NCS = normalized cone tip resistance as detailed by Boulanger and Idriss (2014)",
        "n = 0.5 for Ic < 2.6, else 0.75."]),
}


@pytest.mark.parametrize("label", sorted(CASES))
def test_table_is_typed_in(label):
    section, page, cells = CASES[label]
    entry = _entry(section, label)
    head = entry.split(" - column", 1)[0]
    assert head.endswith(page), head
    assert len(cells) >= 5 or label in ("Table 7-6", "Table 5-8"), label
    for cell in cells:
        assert cell in entry, (label, cell)


def test_number_of_typed_tables():
    assert len(CASES) == 58


def test_rows_counts():
    # rows are separated by " | "; counts read off the print
    rows = {"Table 5-7": 19, "Table 5-10": 22, "Table 8-12": 23, "Table 8-13": 56,
            "Table 8-14": 24, "Table 8-16": 12, "Table 8-17": 20, "Table 8-26": 31,
            "Table 8-28": 19, "Table 7-7": 15, "Table 6-14": 6}
    for label, n in rows.items():
        entry = _entry(CASES[label][0], label)
        assert entry.count(" | ") == n - 1, label


def test_monotonic_trends():
    import re
    # Table 6-14: the maximum D90F rises with the minimum D10F
    e = _entry("6-5.3.1", "Table 6-14").split("columns: ", 1)[1]
    d90 = [int(r.rsplit("; ", 1)[1]) for r in e.split(". ", 1)[1].split(" | ")]
    assert d90 == sorted(d90) == [20, 25, 30, 40, 50, 60]
    # Table 8-15: the modified compression index falls as Dr rises, for each sand
    e = _entry("8-4.2", "Table 8-15")
    for row in e.split("Dr = 100%. ", 1)[1].split(" | "):
        vals = [float(v) for v in row.split("; ")[1:]]
        assert len(vals) == 6 and vals == sorted(vals, reverse=True)
    # Table 5-7: the decimal is the ratio (single-valued rows)
    e = _entry("5-6.2.1", "Table 5-7")
    for dec, den in re.findall(r"; (0\.\d+); 1/(\d+)(?= \||$)", e):
        assert abs(float(dec) - 1 / int(den)) < 0.00006, (dec, den)


def test_lookup_tables_stay_labels():
    for section, label in (("5-5.4", "Table 5-6"), ("8-2.2.2", "Table 8-6"), ("8-6.2", "Table 8-24")):
        assert _entry(section, label) == label
    assert _entry("8-3.2", "Table 8-9") == "Table 8-9 Typical Values of m"


def test_repeated_labels_are_typed_once():
    assert _entry("5-1.2", "Table 5-1") == "Table 5-1" and _entry("5-4", "Table 5-1") == "Table 5-1"
    assert _entry("6-5", "Table 6-8") == "Table 6-8"
    assert _entry("8-7", "Table 8-25") == "Table 8-25" and _entry("5-8.5", "Table 5-11") == "Table 5-11"
