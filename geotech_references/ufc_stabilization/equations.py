"""UFC 3-250-11, Soil Stabilization and Modification for Pavements -- equations.

The 6 printed equations/formulas in this document (30 Nov 2020 edition) are
none of them numbered by the source (e.g. no "Eq 3-1"); each is cited by its
originating paragraph/section number instead. All page citations are the
0-based fitz page index of ``docs/ufc_3_250_11_2020.pdf`` (cited as
``pdf_page`` in each docstring) plus the printed page number, related by
``pdf_page_index = printed_page + 7`` throughout this document (verified at
printed pp. 1, 8, 63, 69, 75 -- no roman-numeral front matter after the
table of contents).

UNITS: this document is US-customary native (inches, percent by weight);
mm is given parenthetically in the source. Per repo convention (GEC-12/
AASHTO-1993 precedent) source units are kept, not force-converted to SI.
"""


# ============================================================================
# Cement content for modifying soils to reduce PI (Section 3-1.4.1, printed
# p.16, pdf_page 23):  A = 100*B*C
# ============================================================================

def equation_cement_content_modifying_soils(percent_passing_no40, percent_cement_for_pi) -> dict:
    """Design cement content for soil modification (PI reduction), Sec 3-1.4.1.

        A = 100*B*C

    Where A = design cement content, percent of TOTAL sample weight; B =
    percent passing the No. 40 (0.425 mm) sieve, expressed as a decimal; C =
    percent cement required to obtain the desired PI of the minus No. 40
    sieve material, expressed as a decimal. The minimum cement content that
    yields the desired PI is first found by trial-and-error testing on the
    minus-No.-40 fraction (percent C); this equation adjusts that value back
    to a percentage of the TOTAL (unsieved) sample weight.

    Hand-verified against the task's worked check: B=0.60, C=0.08 -> A=4.8.

    Parameters
    ----------
    percent_passing_no40 : float
        B: fraction (0-1) of the soil sample passing the No. 40 (0.425 mm)
        sieve.
    percent_cement_for_pi : float
        C: fraction (0-1) cement (of the minus-No.-40 fraction) found by
        trial testing to yield the desired PI.

    Returns
    -------
    dict
        {'percent_passing_no40', 'percent_cement_for_pi',
         'design_cement_content_pct', 'equation', 'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If either input is not in [0, 1].
    """
    b, c = percent_passing_no40, percent_cement_for_pi
    if not (0 <= b <= 1):
        raise ValueError(f"percent_passing_no40 (B) must be a decimal fraction in [0,1], got {b}")
    if not (0 <= c <= 1):
        raise ValueError(f"percent_cement_for_pi (C) must be a decimal fraction in [0,1], got {c}")
    a = 100 * b * c
    return {
        "percent_passing_no40": b,
        "percent_cement_for_pi": c,
        "design_cement_content_pct": round(a, 4),
        "equation": "A = 100*B*C",
        "reference": "UFC 3-250-11, Sec 3-1.4.1, p.16",
        "pdf_page": 23,
    }


# ============================================================================
# Preliminary cutback-asphalt content for subgrade stabilization (Section
# 3-4.4, printed pp.25-26, pdf_page 32):
#   p = [0.02(a) + 0.07(b) + 0.15(c) + 0.20(d)] / (100 - S) * 100
# ============================================================================

def equation_cutback_asphalt_content_estimate(
    percent_retained_no50, percent_no50_to_no100, percent_no100_to_no200,
    percent_passing_no200, percent_solvent,
) -> dict:
    """Preliminary cutback-asphalt content for subgrade stabilization, Sec 3-4.4.

        p = [0.02(a) + 0.07(b) + 0.15(c) + 0.20(d)] / (100 - S) * 100

    Where p = percent cutback asphalt by weight of dry aggregate; a = percent
    of mineral aggregate retained on the No. 50 (0.300 mm) sieve; b = percent
    passing No. 50 and retained on No. 100 (0.150 mm); c = percent passing
    No. 100 and retained on No. 200 (0.075 mm); d = percent passing No. 200;
    S = percent solvent (of the cutback asphalt). Estimating equation only --
    select the final design content from the Marshall Stability Test (min.
    500 lb / 227 kg for subgrades). No numeric worked example is printed for
    this equation in the source; digitized as printed (a,b,c,d,S given as
    percentages, 0-100, not decimal fractions).

    Parameters
    ----------
    percent_retained_no50 : float
        a, percent (0-100).
    percent_no50_to_no100 : float
        b, percent (0-100).
    percent_no100_to_no200 : float
        c, percent (0-100).
    percent_passing_no200 : float
        d, percent (0-100).
    percent_solvent : float
        S, percent solvent in the cutback asphalt (0-100, must be < 100).

    Returns
    -------
    dict
        {'a', 'b', 'c', 'd', 's', 'cutback_asphalt_pct', 'equation',
         'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If percent_solvent >= 100 (division by zero/negative) or any input
        is negative.
    """
    a, b, c, d, s = (percent_retained_no50, percent_no50_to_no100,
                     percent_no100_to_no200, percent_passing_no200,
                     percent_solvent)
    for name, val in (("a", a), ("b", b), ("c", c), ("d", d), ("s", s)):
        if val < 0:
            raise ValueError(f"{name} must be >= 0, got {val}")
    if s >= 100:
        raise ValueError(f"percent_solvent (S) must be < 100, got {s}")
    p = (0.02 * a + 0.07 * b + 0.15 * c + 0.20 * d) / (100 - s) * 100
    return {
        "a": a, "b": b, "c": c, "d": d, "s": s,
        "cutback_asphalt_pct": round(p, 3),
        "equation": "p = [0.02(a)+0.07(b)+0.15(c)+0.20(d)] / (100-S) * 100",
        "reference": "UFC 3-250-11, Sec 3-4.4, p.25-26",
        "pdf_page": 32,
    }


# ============================================================================
# Table 2-3 footnote (c): PI restriction for area 1C/2C item 2 (Portland
# cement), printed p.13, pdf_page 20
# ============================================================================

def equation_cement_pi_limit_table_2_3(percent_passing_no200) -> dict:
    """Maximum PI for portland cement in Table 2-3 areas 1C/2C (footnote c).

        PI(limit) = 20 + 50 - percent_passing_No200

    Hand-verified against the narrative worked example (Sec 2-1.5.2, printed
    p.9, pdf_page 16): a SC soil with 25% passing the No. 200 sieve and PI=9
    -> PI(limit) = 20+50-25 = 45; since 9 < 45, portland cement is confirmed
    a candidate stabilizer, matching the source's own conclusion.

    Parameters
    ----------
    percent_passing_no200 : float
        Percent of the soil passing the No. 200 (0.075 mm) sieve (0-100).

    Returns
    -------
    dict
        {'percent_passing_no200', 'pi_limit', 'equation', 'reference',
         'pdf_page'}.

    Raises
    ------
    ValueError
        If percent_passing_no200 is not in [0, 100].
    """
    p200 = percent_passing_no200
    if not (0 <= p200 <= 100):
        raise ValueError(f"percent_passing_no200 must be in [0,100], got {p200}")
    pi_limit = 20 + 50 - p200
    return {
        "percent_passing_no200": p200,
        "pi_limit": round(pi_limit, 3),
        "equation": "PI(limit) = 20 + 50 - percent_passing_No200",
        "reference": "UFC 3-250-11, Table 2-3 note (c), p.13",
        "pdf_page": 20,
    }


# ============================================================================
# Thickness-equivalency conversion for stabilized soil layers (Appendix
# A-1.2, printed p.64, pdf_page 71): T(stabilized) = T(conventional) / EF
# ============================================================================

def equation_stabilized_equivalent_thickness(conventional_thickness_in, equivalency_factor) -> dict:
    """Equivalent stabilized-layer thickness from a conventional design, Sec A-1.2.

        T(stabilized) = T(conventional) / EF

    An equivalency factor (Table A-1; see ``tables.table_a1_equivalency_factors``)
    is "the number of inches (mm) of a conventional base or subbase that can
    be replaced by 1 inch (25 mm) of stabilized material" -- so dividing the
    conventional layer thickness by EF gives the thinner stabilized-layer
    thickness with equal structural value.

    Hand-verified against both of Appendix A's printed worked examples
    (pdf_page 71, printed p.64):
      Example 1: 4 in conventional base, EF=1.15 (cement-stabilized GP,
        Table A-1) -> 4/1.15 = 3.48 in (printed: 3.48 in).
      Example 2: 16.88 in of conventional-equivalent subbase, EF=2.30
        (all-bituminous concrete, Table A-1) -> 16.88/2.30 = 7.34 in
        (printed: 7.34 in).

    Parameters
    ----------
    conventional_thickness_in : float
        Thickness of the conventional (unstabilized) base or subbase layer
        being replaced, inches, > 0.
    equivalency_factor : float
        EF from Table A-1 for the stabilizer type / soil group / layer
        (base or subbase), > 0.

    Returns
    -------
    dict
        {'conventional_thickness_in', 'equivalency_factor',
         'stabilized_thickness_in', 'equation', 'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If conventional_thickness_in <= 0 or equivalency_factor <= 0.
    """
    t, ef = conventional_thickness_in, equivalency_factor
    if t <= 0:
        raise ValueError(f"conventional_thickness_in must be > 0, got {t}")
    if ef <= 0:
        raise ValueError(f"equivalency_factor must be > 0, got {ef}")
    t_stab = t / ef
    return {
        "conventional_thickness_in": t,
        "equivalency_factor": ef,
        "stabilized_thickness_in": round(t_stab, 3),
        "equation": "T(stabilized) = T(conventional) / EF",
        "reference": "UFC 3-250-11, Sec A-1.2, p.64",
        "pdf_page": 71,
    }


# ============================================================================
# Appendix A-3 sulfate-in-soil determination -- oven-dry weight of the
# initial sample from its air-dry weight and air-dry moisture content
# (Section A-3.1.5 "Where:" block, printed p.67, pdf_page 74)
# ============================================================================

def equation_oven_dry_weight_from_air_dry(air_dry_weight_g, air_dry_moisture_content_pct) -> dict:
    """Oven-dry weight of a soil sample from its air-dry weight, Sec A-3.1.5.

        Ws = W(air-dry) / [1 + w(air-dry, percent)/100]

    NOTE ON SOURCE FIDELITY: the printed equation image (pdf_page 74,
    printed p.67) renders as a garbled/malformed nested fraction --
    literally "Oven-dry weight of initial sample = 1 + [air-dry weight of
    initial sample / air-dry moisture content(percent)] / 100 percent" --
    which is dimensionally inconsistent (it would return a near-unity,
    unitless value, not a weight) and does not reproduce the appendix's own
    worked example. This function instead implements the standard air-dry-
    to-oven-dry mass relationship universal to soil mechanics (moisture
    content w = mass of water / mass of oven-dry solids * 100, so
    W(air-dry) = Ws*(1+w/100)), which DOES reproduce the source's own A-3.2.4
    sample calculation to within rounding: air-dry weight 10.12 g, water
    content 9.36% -> Ws = 10.12/1.0936 = 9.25 g, vs. the source's stated
    "Weight of dry soil = 9.27 g" (pdf_page 75, printed p.68), a ~0.2%
    difference consistent with the intermediate values themselves being
    rounded in the printed example.

    Parameters
    ----------
    air_dry_weight_g : float
        Weight of the air-dried soil sample, g, > 0.
    air_dry_moisture_content_pct : float
        Moisture content of the air-dried sample, percent (>= 0).

    Returns
    -------
    dict
        {'air_dry_weight_g', 'air_dry_moisture_content_pct',
         'oven_dry_weight_g', 'equation', 'reference', 'pdf_page',
         'source_equation_note'}.

    Raises
    ------
    ValueError
        If air_dry_weight_g <= 0 or air_dry_moisture_content_pct < 0.
    """
    w_air, mc = air_dry_weight_g, air_dry_moisture_content_pct
    if w_air <= 0:
        raise ValueError(f"air_dry_weight_g must be > 0, got {w_air}")
    if mc < 0:
        raise ValueError(f"air_dry_moisture_content_pct must be >= 0, got {mc}")
    ws = w_air / (1 + mc / 100.0)
    return {
        "air_dry_weight_g": w_air,
        "air_dry_moisture_content_pct": mc,
        "oven_dry_weight_g": round(ws, 4),
        "equation": "Ws = W(air-dry) / [1 + w(air-dry,%)/100]",
        "reference": "UFC 3-250-11, Sec A-3.1.5, p.67",
        "pdf_page": 74,
        "source_equation_note": ("Source's own printed equation image is a "
                                  "malformed nested fraction; see docstring."),
    }


# ============================================================================
# Appendix A-3.1: gravimetric sulfate determination (printed p.66, pdf_page
# 73):  Percent SO4 = (Weight of residue / Oven-dry weight of initial
# sample) * 411.6
# ============================================================================

def equation_gravimetric_percent_so4(weight_of_residue_g, oven_dry_weight_g) -> dict:
    """Percent sulfate (as SO4) in soil, gravimetric BaSO4 method, Sec A-3.1.5.

        Percent SO4 = (Weight of residue / Oven-dry weight of initial sample) * 411.6

    Weight of residue is the ignited BaSO4 precipitate mass (g); 411.6 is the
    method's printed gravimetric conversion factor (BaSO4 -> SO4, scaled for
    the method's fixed aliquot/dilution steps). Detects as little as 0.05%
    sulfate as SO4 (Sec A-3.1.1 scope).

    Parameters
    ----------
    weight_of_residue_g : float
        Ignited BaSO4 precipitate weight, g, >= 0.
    oven_dry_weight_g : float
        Oven-dry weight of the initial soil sample, g, > 0 (see
        ``equation_oven_dry_weight_from_air_dry``).

    Returns
    -------
    dict
        {'weight_of_residue_g', 'oven_dry_weight_g', 'percent_so4',
         'equation', 'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If weight_of_residue_g < 0 or oven_dry_weight_g <= 0.
    """
    wr, ws = weight_of_residue_g, oven_dry_weight_g
    if wr < 0:
        raise ValueError(f"weight_of_residue_g must be >= 0, got {wr}")
    if ws <= 0:
        raise ValueError(f"oven_dry_weight_g must be > 0, got {ws}")
    pct = (wr / ws) * 411.6
    return {
        "weight_of_residue_g": wr,
        "oven_dry_weight_g": ws,
        "percent_so4": round(pct, 4),
        "equation": "Percent SO4 = (Weight of residue / Oven-dry weight of initial sample) * 411.6",
        "reference": "UFC 3-250-11, Sec A-3.1.5, p.66",
        "pdf_page": 73,
    }


# ============================================================================
# Appendix A-3.2: turbidimetric sulfate determination sample calculation
# (printed p.68, pdf_page 75):
#   Percent SO4 = (C * V * 100) / (1,000 * 1,000 * W)
# ============================================================================

def equation_turbidimetric_percent_so4(concentration_ppm, total_volume_ml, dry_weight_g) -> dict:
    """Percent sulfate (as SO4) in soil, turbidimetric method, Sec A-3.2.4.

        Percent SO4 = (C * V * 100) / (1,000 * 1,000 * W)

    Where C = sulfate concentration of the ORIGINAL extracting solution
    (parts per million, read from the standard curve and corrected for the
    aliquot dilution factor -- see ``figures_catalog.json`` Figure A-1);
    V = total volume of extracting solution (ml); W = oven-dry weight of the
    soil sample (g).

    Hand-verified against the source's own printed sample calculation (Sec
    A-3.2.4, pdf_page 75, printed p.68): C=80.0 ppm, V=39.1 ml, W=9.27 g ->
    Percent SO4 = (80.0*39.1*100)/(1,000*1,000*9.27) = 0.0337, matching the
    source's printed answer of 0.0338 percent to within rounding of the
    intermediate 16.0 ppm transmission-curve reading.

    Parameters
    ----------
    concentration_ppm : float
        C: sulfate concentration of the original (undiluted-aliquot)
        extracting solution, ppm, >= 0.
    total_volume_ml : float
        V: total volume of extracting solution obtained from the soil-to-
        solution extraction, ml, > 0.
    dry_weight_g : float
        W: oven-dry weight of the soil sample, g, > 0.

    Returns
    -------
    dict
        {'concentration_ppm', 'total_volume_ml', 'dry_weight_g',
         'percent_so4', 'equation', 'reference', 'pdf_page'}.

    Raises
    ------
    ValueError
        If concentration_ppm < 0, or total_volume_ml/dry_weight_g <= 0.
    """
    c, v, w = concentration_ppm, total_volume_ml, dry_weight_g
    if c < 0:
        raise ValueError(f"concentration_ppm must be >= 0, got {c}")
    if v <= 0:
        raise ValueError(f"total_volume_ml must be > 0, got {v}")
    if w <= 0:
        raise ValueError(f"dry_weight_g must be > 0, got {w}")
    pct = (c * v * 100) / (1000 * 1000 * w)
    return {
        "concentration_ppm": c,
        "total_volume_ml": v,
        "dry_weight_g": w,
        "percent_so4": round(pct, 5),
        "equation": "Percent SO4 = (C*V*100) / (1,000*1,000*W)",
        "reference": "UFC 3-250-11, Sec A-3.2.4, p.68",
        "pdf_page": 75,
    }
