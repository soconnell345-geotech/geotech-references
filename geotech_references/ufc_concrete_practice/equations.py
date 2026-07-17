"""UFC 3-250-04 (Standard Practice for Concrete Pavements) - equation lookups.

This is a construction-practice manual, almost entirely procedural/QC
narrative. Exactly one printed, closed-form formula was found across the
full document: the combined-aggregate coarseness factor / workability
factor pair used to plot a gradation on the aggregate proportioning guide
(Equation 7-1, printed in the source as "(7-9.1.5)"; Section 7-9.1.5,
pdf_page 80-81, printed pp.63-64).

PDF pages cited below are 0-based fitz page indices into
``docs/ufc_3_250_04_2024.pdf``; the printed UFC page is also given.
"""


def coarseness_factor(pct_retained_9_5mm, pct_retained_2_36mm) -> dict:
    """Combined-aggregate coarseness factor (Equation 7-1, Section 7-9.1.5).

    CF = 100 * (percent retained above the 9.5 mm [3/8 in.] sieve) /
    (percent retained above the 2.36 mm [No. 8] sieve).

    Used with ``workability_factor`` to plot a combined aggregate gradation
    on the aggregate proportioning guide (Figure 7-2) and workability box
    (Figure 7-3). The guide states the coarseness factor should not be
    greater than 80 nor less than 30; coarseness factors above 75 (chart
    Area E) produce gap-graded mixtures with inadequate workability and
    high segregation potential.

    Parameters
    ----------
    pct_retained_9_5mm : float
        Cumulative percent of the combined aggregate retained on the
        9.5 mm (3/8 in.) sieve.
    pct_retained_2_36mm : float
        Cumulative percent of the combined aggregate retained on the
        2.36 mm (No. 8) sieve. Must be > 0.

    Returns
    -------
    dict
        {'pct_retained_9_5mm', 'pct_retained_2_36mm', 'coarseness_factor',
         'in_recommended_range' (30-80), 'note'?, 'reference'}.

    Raises
    ------
    ValueError
        If pct_retained_2_36mm <= 0.
    """
    if pct_retained_2_36mm <= 0:
        raise ValueError(
            f"pct_retained_2_36mm must be > 0, got {pct_retained_2_36mm}"
        )
    cf = 100.0 * pct_retained_9_5mm / pct_retained_2_36mm
    out = {
        "pct_retained_9_5mm": pct_retained_9_5mm,
        "pct_retained_2_36mm": pct_retained_2_36mm,
        "coarseness_factor": round(cf, 1),
        "in_recommended_range": 30 <= cf <= 80,
        "reference": (
            "UFC 3-250-04, Equation 7-1 / Section 7-9.1.5 "
            "(pdf_page 80, printed p.63)"
        ),
    }
    if cf > 75:
        out["note"] = (
            "CF > 75 (chart Area E): gap-graded mixture with inadequate "
            "workability and high segregation potential."
        )
    elif not out["in_recommended_range"]:
        out["note"] = "Coarseness factor outside the recommended 30-80 range."
    return out


def workability_factor(pct_passing_2_36mm, cementitious_content_kg_m3) -> dict:
    """Combined-aggregate workability factor (Equation 7-1, Section 7-9.1.5).

    WF = (percent of combined aggregate passing the 2.36 mm [No. 8] sieve)
    + 2.5% for each 56 kg/m3 (94 lb/yd3) of cementitious material in excess
    of the 335 kg/m3 (564 lb/yd3) baseline. The adjustment is upward ONLY:
    335 kg/m3 is the minimum cementitious content permitted for rigid
    airfield pavement mix designs, so cementitious contents at or below the
    baseline receive no adjustment.

    Used with ``coarseness_factor`` to plot a combined aggregate gradation
    on the aggregate proportioning guide (Figure 7-2) and workability box
    (Figure 7-3).

    Parameters
    ----------
    pct_passing_2_36mm : float
        Cumulative percent of the combined aggregate passing the 2.36 mm
        (No. 8) sieve.
    cementitious_content_kg_m3 : float
        Total cementitious material content of the mixture, kg/m3.

    Returns
    -------
    dict
        {'pct_passing_2_36mm', 'cementitious_content_kg_m3',
         'workability_factor', 'reference'}.

    Raises
    ------
    ValueError
        If either input is negative.
    """
    if pct_passing_2_36mm < 0:
        raise ValueError(
            f"pct_passing_2_36mm must be >= 0, got {pct_passing_2_36mm}"
        )
    if cementitious_content_kg_m3 < 0:
        raise ValueError(
            "cementitious_content_kg_m3 must be >= 0, got "
            f"{cementitious_content_kg_m3}"
        )
    baseline = 335.0
    increment = 56.0
    excess = max(0.0, cementitious_content_kg_m3 - baseline)
    adjustment = 2.5 * (excess / increment)
    wf = pct_passing_2_36mm + adjustment
    return {
        "pct_passing_2_36mm": pct_passing_2_36mm,
        "cementitious_content_kg_m3": cementitious_content_kg_m3,
        "workability_factor": round(wf, 1),
        "reference": (
            "UFC 3-250-04, Equation 7-1 / Section 7-9.1.5 "
            "(pdf_page 80-81, printed p.63-64)"
        ),
    }
