"""EM 1110-2-2107 Chapter 3 -- Design Considerations.

Limit states, structure classification (normal/critical), service life and
target-reliability requirements (Table 3.1), and the usual/unusual/extreme
load-category classification by return period / annual exceedance probability
(AEP) (paragraph 3.3.4, Figure 3.1). Printed pages per the 1 August 2022
edition (pdf_page = printed_page + 8).
"""

import math

# ============================================================================
# Table 3.1 -- Target reliability for 100-year service life, beta
# (printed p. 11, pdf_page 19)
# ============================================================================

_TABLE_3_1 = {
    ("normal", "redundant"): 3.0,
    ("normal", "single"): 3.5,
    ("critical", "redundant"): 3.5,
    ("critical", "single"): 4.0,
}


def table_3_1_target_reliability(structure_class, load_path):
    """Table 3.1: target reliability index beta for a 100-year HSS service
    life (printed p. 11).

    Load factors in Chapter 4 (combined with AISC resistance/capacity
    factors) are developed for single-load-path structures and, per
    paragraph 3.2.5, "can be safely applied to redundant structures" too --
    ``load_path='single'`` is therefore the conservative default choice for
    most HSS.

    Parameters
    ----------
    structure_class : str
        'normal' or 'critical' (paragraph 3.2.3).
    load_path : str
        'redundant' or 'single' (paragraph 3.2.5 / 3.5.2).

    Returns
    -------
    dict
        {'structure_class', 'load_path', 'beta', 'table': '3.1',
         'printed_page': '11', 'pdf_page': 19}
    """
    key = (structure_class.lower(), load_path.lower())
    if key not in _TABLE_3_1:
        raise ValueError(
            "structure_class must be 'normal'/'critical' and load_path "
            f"'redundant'/'single'; got {structure_class!r}, {load_path!r}"
        )
    return {
        "structure_class": structure_class, "load_path": load_path,
        "beta": _TABLE_3_1[key], "table": "3.1",
        "printed_page": "11", "pdf_page": 19,
    }


# ============================================================================
# Paragraph 3.3.4 -- Probability of loading: usual/unusual/extreme
# (printed pp. 12-13, pdf_page 20-21, Figure 3.1)
# ============================================================================

# Upper bound of the unusual load category's return period, by structure
# class (paragraph 3.3.4.2): the boundary between "unusual" and "extreme".
_UNUSUAL_UPPER_TR = {"normal": 300.0, "critical": 750.0}
_USUAL_UPPER_TR = 10.0


def load_category_from_return_period(return_period_years, structure_class):
    """Paragraph 3.3.4: classify a load's probability-of-loading category
    (usual / unusual / extreme) from its mean return period Tr (printed
    pp. 12-13, Figure 3.1).

        usual:    Tr <= 10 yr                                  (AEP >= 0.10)
        unusual:  10 yr < Tr <= 300 yr (normal) / 750 yr (critical)
        extreme:  Tr >  300 yr (normal) / 750 yr (critical)

    Parameters
    ----------
    return_period_years : float
        Mean annual return period Tr of the predominant load (or combined
        loads), years.
    structure_class : str
        'normal' or 'critical' (``table_3_1_target_reliability``), which
        sets the unusual/extreme boundary.

    Returns
    -------
    dict
        {'return_period_years', 'structure_class', 'category'
         ('usual'/'unusual'/'extreme'), 'aep', 'printed_page': '12-13',
         'pdf_page': '20-21'}
    """
    sc = structure_class.lower()
    if sc not in _UNUSUAL_UPPER_TR:
        raise ValueError(f"structure_class must be 'normal' or 'critical', got {structure_class!r}")
    if return_period_years <= 0:
        raise ValueError(f"return_period_years must be > 0, got {return_period_years}")
    if return_period_years <= _USUAL_UPPER_TR:
        category = "usual"
    elif return_period_years <= _UNUSUAL_UPPER_TR[sc]:
        category = "unusual"
    else:
        category = "extreme"
    return {
        "return_period_years": return_period_years, "structure_class": structure_class,
        "category": category, "aep": 1.0 / return_period_years,
        "printed_page": "12-13", "pdf_page": "20-21",
    }


def aep_from_return_period(return_period_years):
    """Annual exceedance probability AEP = 1/Tr (paragraph 3.3.4, printed
    p. 12). A plain reciprocal, provided as a named helper because the
    manual's own category thresholds are quoted in both forms (e.g. "Tr <=
    10 years (AEP of 0.10)").
    """
    if return_period_years <= 0:
        raise ValueError(f"return_period_years must be > 0, got {return_period_years}")
    return {"return_period_years": return_period_years, "aep": 1.0 / return_period_years,
            "printed_page": "12", "pdf_page": 20}
