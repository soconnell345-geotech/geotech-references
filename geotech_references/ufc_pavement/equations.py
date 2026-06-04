"""UFC 3-250-01 pavement design equations.

Pavement Design for Roads and Parking Areas (14 November 2016).
Covers roads, streets, walks, and open storage areas — NOT airfields
(airfields are in UFC 3-260-02).

Primary design tool is PCASE software; this module provides the
supporting calculations that can be implemented analytically.
"""

import math


def cbr_to_k_psi_per_in(cbr):
    """Estimate modulus of subgrade reaction k from CBR (empirical).

    UFC 3-250-01 Table 10-1 provides tabulated k values by soil type and
    moisture content as the primary reference.  This equation provides a
    first estimate for preliminary design where Table 10-1 cannot be
    entered without detailed soil data.

    Correlation (consistent with Table 10-1 ranges)::

        k (psi/in) ≈ 26 × CBR^0.7     (USACE empirical correlation)

    Use Table 10-1 directly when soil type and moisture content are known.
    Conversion: k (kPa/mm) = k (psi/in) × 0.271.

    Parameters
    ----------
    cbr : float
        California Bearing Ratio (%).  Valid range 2–100.

    Returns
    -------
    dict
        {'cbr': float, 'k_psi_in': float, 'k_kPa_mm': float,
         'note': str}

    Raises
    ------
    ValueError
        If cbr is outside valid range.
    """
    if cbr < 2:
        raise ValueError(f"cbr must be >= 2, got {cbr}")
    if cbr > 100:
        raise ValueError(f"cbr must be <= 100, got {cbr}")

    k_psi = 26.0 * cbr ** 0.7
    k_kPa_mm = k_psi * 0.271

    return {
        "cbr": cbr,
        "k_psi_in": round(k_psi, 1),
        "k_kPa_mm": round(k_kPa_mm, 1),
        "note": (
            "Preliminary estimate only; use UFC 3-250-01 Table 10-1 "
            "when soil type and moisture content are known"
        ),
    }


def stabilized_layer_thickness_mm(
    conventional_thickness_mm,
    equivalency_factor,
):
    """Stabilized layer thickness from UFC 3-250-01 Table 9-1.

    When a stabilized layer replaces conventional granular base or subbase,
    the design starts with a conventional flexible pavement thickness and
    then divides that thickness by the equivalency factor to get the
    stabilized layer thickness::

        t_stab = t_conventional / E

    where *E* is from Table 9-1 (``table_9_1_equivalency_factor``).

    A conventional pavement must first be designed to determine the
    required conventional base/subbase thickness.  The stabilized thickness
    must also be checked against minimum thickness requirements of Table 7-2.

    Parameters
    ----------
    conventional_thickness_mm : float
        Thickness of conventional base or subbase course required (mm).
    equivalency_factor : float
        Equivalency factor from Table 9-1 for the stabilized material,
        USCS classification, and layer type.  Must be > 0.
        Typical range: 1.0–2.3.

    Returns
    -------
    dict
        {'conventional_thickness_mm': float,
         'equivalency_factor': float,
         'stabilized_thickness_mm': float,
         'note': str}

    Raises
    ------
    ValueError
        If inputs are not positive.
    """
    if conventional_thickness_mm <= 0:
        raise ValueError(
            f"conventional_thickness_mm must be > 0, "
            f"got {conventional_thickness_mm}"
        )
    if equivalency_factor <= 0:
        raise ValueError(
            f"equivalency_factor must be > 0, got {equivalency_factor}"
        )

    t_stab = conventional_thickness_mm / equivalency_factor

    return {
        "conventional_thickness_mm": conventional_thickness_mm,
        "equivalency_factor": equivalency_factor,
        "stabilized_thickness_mm": round(t_stab, 1),
        "note": (
            "Check against Table 7-2 minimum thickness requirements; "
            "cement content limited to ≤ 4% by weight to prevent "
            "reflective cracking"
        ),
    }


def free_draining_layer_required(
    bound_layer_thickness_in,
    design_freezing_index,
):
    """Check UFC 3-250-01 frost free-draining layer requirement.

    In frost areas, if the combined thickness of pavement plus contiguous
    bound base courses is less than 0.09 × DFI (degree-Fahrenheit-days),
    at least 4 in (100 mm) of free-draining material must be placed directly
    beneath the lowest bound layer.  The free-draining material must contain
    ≤ 2.0% by weight passing the No. 200 sieve.

    This limits the design freezing index at the bottom of the bound base
    to about 20 degree-Fahrenheit-days.

    Parameters
    ----------
    bound_layer_thickness_in : float
        Combined thickness of pavement plus contiguous bound base courses
        (inches).
    design_freezing_index : float
        Design air freezing index (degree-Fahrenheit-days).  Use the
        average of the three coldest years in 30 years (or coldest winter
        in 10 years).

    Returns
    -------
    dict
        {'required': bool,
         'bound_layer_thickness_in': float,
         'threshold_thickness_in': float,
         'design_freezing_index': float,
         'min_free_draining_layer_in': float,
         'note': str}

    Raises
    ------
    ValueError
        If inputs are not positive.
    """
    if bound_layer_thickness_in < 0:
        raise ValueError(
            f"bound_layer_thickness_in must be >= 0, "
            f"got {bound_layer_thickness_in}"
        )
    if design_freezing_index <= 0:
        raise ValueError(
            f"design_freezing_index must be > 0, got {design_freezing_index}"
        )

    threshold = 0.09 * design_freezing_index
    required = bound_layer_thickness_in < threshold

    return {
        "required": required,
        "bound_layer_thickness_in": bound_layer_thickness_in,
        "threshold_thickness_in": round(threshold, 1),
        "design_freezing_index": design_freezing_index,
        "min_free_draining_layer_in": 4.0,
        "note": (
            "Free-draining material must have ≤ 2.0% fines passing No. 200 "
            "sieve; check filter criteria for conformance with adjacent layers"
        ),
    }
