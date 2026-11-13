"""Typed-in tables of UFS 3-220-10 (DM 7.1), chapters 1 to 4 (REF-97).

Every value below was read off the printed page (rendered at 300 dpi) of
docs/ufc_3_220_10_2026.pdf; the page in each case is the printed page.
Each case: (chapter, section, table, printed page text, cells and notes
that the stored entry must hold; the first and last rows are among them).
"""
import json
from pathlib import Path

import pytest

TEXT = Path(__file__).resolve().parents[1] / "geotech_references" / "dm7_1" / "text"

CASES = [
    (1, "1-3.2.2.1", "1-3", "(p. 12)", [
        "Classification of Fine-grained Soils",
        "ML; None to low; Slow to rapid; Low or thread cannot be formed",
        "CL; Medium to high; None to slow; Medium",
        "MH; Low to medium; None to slow; Low to medium",
        "CH; High to very high; None; High"]),
    (1, "1-3.4", "1-5", "(p. 19)", [
        "A-1-a; ≤ 50; ≤ 30; ≤ 15; ; ≤ 6; Stone fragments, gravel and sand; Excellent to good",
        "A-3; ; ≥ 51; ≤ 10; ; NP^a; Fine sand",
        "A-2-6; ; ; ≤ 35; ≤ 40; ≥ 11",
        "A-5; ; ; ≥ 36; ≥ 41; ≤ 10; Silty soils; Fair to poor",
        "A-7-6; ; ; ≥ 36; ≥ 41; ≥ 11; Clayey soils; Fair to poor",
        "A-8; ; ; ; ; ; Peat or muck; Unsuitable",
        "A-7-5 has PI ≤ (LL – 30) and A-7-6 has PI > (LL – 30)",
        "NP soils have LL = PL, LL < PL, or PL that cannot be determined",
        "GI = (F–35)[0.2+0.005(LL–40)] + 0.01(F–15)(PI–10)",
        "Use only the second term in the GI equation for A-2-6 and A-2-7 soils"]),
    (1, "1-4.2.2", "1-9", "(p. 28)", [
        "Rock Color Descriptors (Geological Society of London 1977)",
        "Light, Dark", "Yellowish, Buff, Orangish", "Olive, Greenish, Greyish",
        "White, Yellow, Buff, Orange, Brown, Pink, Red, Blue, Green, Purple, Olive, Grey, Black"]),
    (1, "1-4.2.2", "1-10", "(p. 28)", [
        "Coarse-grained; > 5 mm; Coarse-grained; > 2 mm",
        "Medium-grained; 1 to 5 mm; Medium-grained; 0.06 to 2 mm",
        "Fine-grained; < 1 mm; Fine-grained; 0.002 to 0.06 mm",
        "Aphantic; Too small to be perceived by eye; Very fine-grained; < 0.002 mm",
        "Glassy; No grain form distinguishable"]),
    (1, "1-4.2.2", "1-11", "(p. 29)", [
        "< 0.003 in. (< 0.075 mm); Very Fine-Grained",
        "0.003 – 0.02 in. (0.075 – 0.425 mm); Fine-Grained",
        "0.02 – 0.8 in. (0.425 – 2 mm) [as printed, 2 mm is 0.08 in., not 0.8 in.]; Medium-Grained",
        "0.8 – 2 in. (2 – 4.75 mm) [as printed",
        "2 in. (> 4.75 mm) [as printed",
        "Very Coarse-Grained; Crystal boundaries are clearly visible, grains are distinguishable with the naked eye."]),
    (1, "1-4.2.3", "1-12", "(p. 29)", [
        "Fresh; F; I; No visible sign of decomposition or discoloration, rings under hammer impact",
        "Slightly Weathered; WS; II", "Moderately Weathered; WM; III", "Highly Weathered; WH; IV",
        "Completely Weathered; WC; V",
        "Residual Soil; RS; V [as printed",
        "large volume change", "Footnote 1: After FHWA (2017)."]),
    (1, "1-4.2.4", "1-13", "(p. 30)", [
        "Very thickly (bedded, foliated, or banded); > 6 feet; Very widely (fractured or jointed)",
        "Thickly; 2 to 6 feet; Widely", "Medium; 8 to 24 inches; Medium",
        "Thinly; 2.5 to 8 inches; Closely", "Very Thinly; 0.75 to 2.5 inches; Very Closely",
        "Intensely (laminated, foliated, or cleavage); 0.25 to 0.75 inch; Extremely close",
        "Very Intensely; < 0.25 inch;"]),
    (1, "1-4.2.5", "1-14", "(p. 30)", [
        "Approximate compressive strength (kg/cm^2 or tsf)",
        "I; Extremely hard; Many blows with geologic hammer required to break intact specimen; >2000",
        "II; Very hard", "1000 - 2000", "500 - 1000", "250 - 500",
        "too hard to hand trim for triaxial test specimen; 10 – 250"]),
    (1, "1-4.2.5", "1-15", "(p. 31)", [
        "R0; Extremely Weak Rock; Specimen can be indented by thumbnail; 2.5 – 10.8",
        "10.8 – 52.2", "52.2 – 252", "252 – 522", "522 – 1,044", "1,044 – 2,610",
        "R6; Extremely Strong Rock; Specimen can only be chipped with firm blows from the hammer end of a geological hammer; > 2,610"]),
    (1, "1-4.3.1", "1-16", "(p. 31)", [
        "RQD; Velocity Index; Rock Mass Quality",
        "90-100; 0.80-1.00; Excellent", "75-90; 0.60-0.80; Good", "50-75; 0.40-0.60; Fair",
        "25-50; 0.20-0.40; Poor", "0-25; 0.00-0.20; Very Poor"]),
    (1, "1-5.1.2", "1-18", "(p. 38)", [
        "Swelling Potential (Dakshanamurthy and Raman 1973)",
        "0 to 20; Non-Swelling", "20 to 35; Low-Swelling", "35 to 50; Medium-Swelling",
        "50 to 70; High Swelling", "70 to 90; Very High Swelling", "> 90; Extra High Swelling"]),
    (1, "1-5.1.2", "1-19", "(p. 38)", [
        "Colloidal Content (% < 1μm); Plasticity Index; Shrinkage Limit",
        "Very high; >30; > 28; >35; <11", "High; 20-30; 20-31; 25-41; 7-12",
        "Medium; 10-20; 13-23; 15-28; 10-16", "Low; <10; <15; <18; >15",
        "Footnote 1: Under a surcharge of 1 psi."]),
    (1, "1-5.1.2", "1-20", "(p. 40)", [
        "0-20; Very low", "21-50; Low", "51-90; Medium", "91-130; High", ">130; Very High"]),
    (1, "1-5.3.2", "1-21", "(p. 45)", [
        "Not frost-susceptible (NFS); Negligible to low; Gravels, crushed stone and rock; 0-1.5; GW, GP",
        "Possibly frost-susceptible (PFS); Possibly; Sands; 3-10; SW, SP",
        "S1; Very low to medium; Gravelly soils; 3-6; GW, GP, GW-GM, GP-GM",
        "F2; Medium to high; Sands; 6-15; SM, SW-SM, SP-SM",
        "F3; Low; Clays, PI >12; ; CL, CH",
        "F4; Low to very high; Very fine silty sands; >15; SM",
        "F4; Very low to very high; Varved clays and other fine-grained banded sediments; ; CL and ML, CL, ML, and SM, CL, CH, and ML, CL, CH, ML and SM."]),
    (2, "2-5.1.1", "2-9", "(pp. 68-69)", [
        "Bridge - shallow foundations; One location per pier if width of foundation is less than 100 ft.",
        "For L ≤ 2B, use depth of 2B • For 2B ≤ L ≤ 5B, use depth of 3B • For L ≥ 5B, use depth of 4B",
        "the greater of 20 ft. or 2x the maximum group dimension",
        "Extend below bottom of the wall 2x the wall height or 10 ft. into hard rock.",
        "Minimum depth of 15 ft. (4.5 m) below lowest cut elevation",
        "Pavements; Spacing of 100 to 300 ft.",
        "Poles, masts and towers; One boring at each foundation location; 30 ft. below the anticipated top of foundation in soil or 10 ft. of rock coring whichever is shallower.",
        "Footnote a: B = footing width and L = footing length"]),
    (2, "2-6.2", "2-13", "(p. 76)", [
        "EX; E; 1-13/16; 1-7/8; 1-7/16; 1-5/16; 1-1/2; 7/8",
        "AX; A; 2-1/4; 2-11/32; 1-27/32; 1-5/8; 1-7/8; 1-3/16",
        "BX; B; 2-7/8; 2-31/32; 2-5/16; 1-29/32; 2-3/8; 1-5/8",
        "NX; N; 3-1/2; 3-5/8; 2-15/16; 2-3/8; 3; 2-1/8",
        "Approx. Diameter of Corehole (in.); Approx. Diameter of Core (in.)"]),
    (2, "2-6.2", "2-14", "(p. 76)", [
        "Standard sizes: 1-1/2” to 3” OD, 7/8” to 2-1/8” core. Barrel lengths 5 to 10 feet for exploration.",
        "Rotary drilling using water or slurry",
        "Single Tube; Fractured rock. Rock too soft.; Primarily for strong, sound and uniform rock.",
        "Double Tube; Improper rotation or feed rate in fractured or soft rock.",
        "Triple Tube; Same as Double Tube; Same as Double Tube.; Differs from Double Tube by having an inner split tube liner. Intensely fractured rock core best preserved in this barrel."]),
    (2, "2-7.1.2", "2-16", "(p. 83)", [
        "Sampler driven above bottom of casing; Sampler driven in disturbed, artificially densified soil; Increases greatly",
        "Careless measure of drop; Hammer energy varies (generally variations cluster on low side); Increases",
        "Coarse gravel or cobbles in soil; Sampler becomes clogged or impeded; Increases",
        "Hammer weight inaccurate; Hammer energy varies (driller supplies weight, variations of 5 – 7% common); Increases or decreases",
        "Use of non-standard sampler; Correlations with standard sampler invalid; Increases or decreases",
        "Failure to maintain adequate head of water in borehole; Bottom of borehole may become quick; Decreases"]),
    (2, "2-9.3.2", "2-23", "(p. 111)", [
        "Lab Oven; 1.00; 0.995; 0.087", "Standard Microwave; 1.11; 0.973; 0.109",
        "Moisture Analyzer; 0.731; 0.915; 0.044", "Nuclear Density Gauge; 0.922; 0.970; 0.091",
        "Gas Pressure Tester; 1.405; 0.867; 0.056",
        "Electromagnetic Probe; 1.096; 0.857; ~0.10 (similar to NDG)",
        "slope > 1 indicates over-prediction, slope < 1 indicates under-prediction",
        "standard deviation approaches 0 for more precise results"]),
    (2, "2-9.4.3", "2-24", "(p. 115)", [
        "<1; Very Low; < 1 x 10^-5; Very Tight; <1",
        "1-5; Low; 1 x 10^-5 - 6 x 10^-5; Tight; ±0",
        "5-15; Moderate; 6 x 10^-5 - 2 x 10^-4; Few partly open; ±1",
        "15-50; Medium; 2 x 10^-4 - 6 x 10^-4; Some open; ±5",
        "50-100; High; 6 x 10^-4 - 1 x 10^-3; Many open; ±10",
        ">100; Very High; > 1 x 10^-3; Open closely spaced or voids; >100"]),
    (3, "3-2.1", "3-1", "(pp. 134-137)", [
        "D698; Laboratory Compaction Characteristics of Soil Using Standard Effort (12,400 ft-lbf/ft^3 (600 kN-m/m^3)); 23 kg (Methods A and B) 45 kg (Method C)",
        "D854; Specific Gravity of Soil Solids by Water Pycnometer; 100 g dry",
        "D2435; One-Dimensional Consolidation Properties of Soils Using Incremental Loading; 300 g",
        "D2487; Classification of Soils for Engineering Purposes (Unified Soil Classification System); Exact mass not provided in ASTM;  |",
        "D4318; Liquid Limit, Plastic Limit, and Plasticity Index of Soils; 150 - 200 g; Sample should be passing No 40 sieve.",
        "D4829; Expansion Index of Soils; 1 kg (dry)",
        "19 mm: 1.3 kg, 25.4 mm: 3 kg, 38.1 mm: 10 kg, 50.8 mm: 25 kg, 76.2 mm: 70 kg",
        "D7928; Particle- Size Distribution (Gradation) of Fine-Grained Soils Using the Sedimentation (Hydrometer) Analysis; 50 g (dry); Passing No. 10 sieve and retained on No. 200 sieve",
        "Footnote A: Moist sample size unless indicated otherwise"]),
    (3, "3-2.6.4", "3-7", "(p. 168)", [
        "0 – 20; Very Low", "21 – 50; Low", "51 – 90; Medium", "91 – 130; High", ">130; Very High"]),
    (4, "4-2.1.4", "4-1", "(p. 181)", [
        "At-rest, K0; Level, natural ground / Unyielding retaining wall; Estimate based on φ′ and OCR / Measure with field tests",
        "Active, KA; Near crest of slopes / Behind yielding retaining walls",
        "Passive, KP; Near toe of slopes / In front of retaining wall toe",
        "Calculate with analytical methods (see DM 7.2) / Estimate based on experience",
        "Lateral earth pressure coefficient; Example applications; Method to obtain"]),
    (4, "4-4.2.2", "4-4", "(p. 196)", [
        "0 to 1; 1.50; 1.75; 1.00; 1.50", "1 to 2; 1.35; 1.50; 1.00; 1.35",
        "2 to 3; 1.15; 1.50; 1.00; 1.35", "Over 3; 1.00; 1.35; 1.00; 1.15",
        "Highway; Railway; Runway; Taxiways and aprons"]),
    (4, "4-4.2.2", "4-5", "(p. 197)", [
        "1; 12.5; Not recommended; Not recommended", "2; 5.56; 26.39; 13.14",
        "8; 0.69; 11.11; 6.93", "10; NA; 7.64; 6.09", "24; NA; 1.74; 1.05",
        "26; NA; 1.39; NA", "30; NA; 0.69; NA"]),
    (4, "4-5.3.1", "4-6", "(pp. 201-202)", [
        "1. Hard and intact; 0; Sometimes spalling or popping occurs.",
        "2. Hard stratified or schistose; 0 to 0.5·B; Light pressures.",
        "4. Moderately blocky and seamy; 0.25·B to 0.35·(B+Ht); No side pressure.",
        "5. Very blocky and seamy; 0.35 to 1.10·(B+Ht)",
        "8. Squeezing rock, great depth; (2.10 to 4.50) ·(B+Ht); Heavy side pressure.",
        "9. Swelling rock; Up to 250 ft, not related to value of (B+Ht); Very heavy pressure.",
        "1. After Proctor and White (1977) based on observations by Terzaghi (1946).",
        "2. Rock loads apply to tunnels at depth greater than 1.5·(B + Ht).",
        "the values given for Conditions 4 to 6 can be reduced by fifty percent",
        "4. Some very dense clays which have not yet acquired properties of shale rock",
        "“very block and seamy.” [as printed"]),
    (4, "4-5.3.1", "4-7", "(p. 202)", [
        "1. Hard and intact; 95 to 100; ≥ 200; > 80",
        "2. Hard stratified or schistose; 90 to 99; 25 to 50; 65 to 75",
        "5. Very blocky and seamy; 30 to 75; 0.4 to 1; 40 to 50",
        "7. Squeezing rock, moderate depth; NA; 0.01 to 0.03; 10 to 20",
        "9. Swelling rock; NA; 0.001 to 0.003; 0",
        "Footnote A: After Barton et al. (1974)", "Footnote B: After Bieniawski (1990)"]),
    (4, "4-5.4.1", "4-8", "(p. 204)", [
        "Firm; Loess above water, hard clay, marl, lightly stressed cemented sand and gravel",
        "Raveling (slow to fast); Sand with clay binder (slow above water table, fast below), stiff fissured clays",
        "Stand-up time is zero.", "Flowing; Silt, sand, and gravel without clayey fines below water table",
        "Squeezing; Very soft to medium stiff clay at shallow depths",
        "Swelling; High OCR clays with swelling minerals and PI greater than about 30.",
        "Advances into opening occur due to an increase in volume allowed by stress relief."]),
    (4, "4-5.4.1", "4-10", "(p. 205)", [
        "Very fine clean sand; Loose (N < 10); Cohesive running; Flowing",
        "Very fine clean sand; Dense (N > 30); Fast raveling; Flowing",
        "Fine sand with clay binder; Dense (N > 30); Firm or slowly raveling; Slowly raveling",
        "Sand or sandy gravel with clay binder; Loose (N < 10); Rapid raveling; Rapid raveling or flowing",
        "Sand or sandy gravel with clay binder; Dense (N > 30); Firm; Firm or slow raveling",
        "Sandy gravel and medium to coarse sand; Any; Running; Flowing"]),
    (4, "4-5.4.2", "4-11", "(p. 208)", [
        "Running ground; min{H, B}; min{H, 2B}, See Note B",
        "Flowing ground in air free; min{H, 2B}; min{H, 4B}, See Note C",
        "Raveling ground above water table; min{H, B}; min{H, 2B}, See Notes B and C",
        "Raveling ground below water table; min{H, 2B}; min{H, 4B}, See Note C",
        "Squeezing ground; Depth to tunnel springline", "Swelling ground; Same as raveling ground",
        "Footnote A: B is the tunnel width",
        "Footnote B: Floor is required in a horseshoe tunnel if compressed air is used, otherwise ignore compressed air.",
        "Footnote C: Stiff floor required in horseshoe tunnel"]),
    (4, "4-5.4.2", "4-12", "(p. 209)", [
        "Running; Above water; Loose: 0.5·(B+Ht), Medium: 0.4·(B+Ht), Dense: 0.3·(B+Ht)",
        "Flowing; Free air; min{H, 2(B+Ht)}",
        "Raveling; Below water, compressed air; Using Hp for running ground: 2·((T−t)/T)·Hp − pc/γt",
        "Squeezing^A; Homogenous clay; H − pc/γt − H·su/[γt·(B+2Ht)]",
        "Squeezing^A; Stiff roof, soft sides; H − pc/γt − H·su/[γt·(B+6Ht)]",
        "Swelling^B; Fissured clay; Use Hp for raveling ground with same standup time",
        "Hp = design load in terms of depth (multiply by γt to determine design pressure)",
        "Footnote A: After complete blowout, pc = 0",
        "Footnote B: Permanent roof support should be completed within a few days after excavation"]),
    (4, "4-6.3", "4-13", "(p. 213)", [
        "K; Controls rate of increase of Ei with σ′3; Ei = K·Pa·(σ′3/Pa)^n",
        "n; Controls nonlinearity of Ei relationship",
        "Rf = (σ1−σ3)max/(σ1−σ3)ult",
        "Kb; Controls rate of increase in Bt with σ′3; Bt = Kb·Pa·(σ′3/Pa)^m",
        "m; Controls nonlinearity of Bt relationship",
        "Kur; Controls rate of increase of Eur with σ′3; Eur = Kur·Pa·(σ′3/Pa)^n"]),
]


def _entry(chapter, section, table):
    data = json.loads((TEXT / f"chapter{chapter:02d}.json").read_text(encoding="utf-8"))
    sec = [s for s in data["sections"] if s["section_id"] == section]
    assert len(sec) == 1, section
    hits = [t for t in sec[0]["tables"] if t.startswith(f"Table {table}: ")]
    assert len(hits) == 1, (section, table)
    return hits[0]


@pytest.mark.parametrize("chapter,section,table,page,cells", CASES,
                         ids=[c[2] for c in CASES])
def test_typed_table(chapter, section, table, page, cells):
    entry = _entry(chapter, section, table)
    assert page in entry
    assert " - " in entry
    assert len(cells) >= 5
    for cell in cells:
        assert cell in entry, cell


def test_each_table_is_typed_once():
    """A table listed under several sections is typed under one of them."""
    for chapter in (1, 2, 3, 4):
        data = json.loads((TEXT / f"chapter{chapter:02d}.json").read_text(encoding="utf-8"))
        typed = [t.split(":")[0] for s in data["sections"] for t in s.get("tables", [])
                 if "(p. " in t or "(pp. " in t]
        assert len(typed) == len(set(typed))
    assert len(CASES) == 32


def test_numeric_tables_follow_their_own_rules():
    # Table 4-5: live load pressure falls with depth of cover in each column.
    rows = _entry(4, "4-4.2.2", "4-5").split("gear assembly). ")[1].split(" | ")
    cols = list(zip(*[r.split("; ") for r in rows]))
    assert [int(d) for d in cols[0]] == sorted(int(d) for d in cols[0])
    for col in cols[1:]:
        vals = [float(v) for v in col if v not in ("NA", "Not recommended")]
        assert vals == sorted(vals, reverse=True)
    # Table 4-4: impact factor does not rise with depth of cover.
    rows = _entry(4, "4-4.2.2", "4-4").split("aprons. ")[1].split(" | ")
    for col in list(zip(*[r.split("; ") for r in rows]))[1:]:
        vals = [float(v) for v in col]
        assert vals == sorted(vals, reverse=True)
    # Table 2-13: each size is larger than the one before, in every column.
    def inch(s):
        whole, _, frac = s.rpartition("-")
        n, _, d = frac.partition("/")
        return (int(whole) if whole else 0) + (int(n) / int(d) if d else int(n))
    rows = _entry(2, "2-6.2", "2-13").split("(in.). ")[1].split(" | ")
    for col in list(zip(*[r.split("; ") for r in rows]))[2:]:
        vals = [inch(v) for v in col]
        assert vals == sorted(vals) and len(set(vals)) == 4
