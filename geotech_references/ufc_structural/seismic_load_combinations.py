"""UFC 3-301-01 Chapters 2/3/6/7 + Appendix B -- seismic load combinations
and related capacity-design checks.

Additional LRFD (ASCE 7-22 Section 2.3.6, printed pp. 43-45) and ASD
(Section 2.4.5, printed pp. 45-46) load combinations for the vertical-
ground-motion-sensitive members identified by
``risk_category_and_loads.vertical_ground_motion_threshold_check`` (SDS
> 0.6g); the Appendix B alternate Risk Category IV seismic load
combinations (Eq B-1/B-2, printed p. 112); the Chapter 2 coupling-beam
capacity-design shear check (paragraph 2106.2.3, printed pp. 36-37); and
the Chapter 7 healthcare structural-separation equation (Eq 12.12-1,
printed p. 100).
"""

# ============================================================================
# Vertical seismic effect, Ev0 (printed pp. 44, 46)
# ============================================================================

def vertical_seismic_effect_ev0(sds, d):
    """Ev0 = 0.67*SDS*D, one of two permitted ways to determine the
    vertical ground motion effect used in the additional seismic load
    combinations of paragraph 2.3.6/2.4.5 (printed pp. 44, 46). The
    alternative is to take Ev0 directly from the ASCE 7-22 Section 11.9
    design vertical response spectrum (not implemented here -- site/period
    dependent).

    Parameters
    ----------
    sds : float
        Design spectral response acceleration at short periods (g).
    d : float
        Dead load effect, D.

    Returns
    -------
    dict
        {'sds', 'd', 'ev0', 'printed_page': '44, 46', 'pdf_page': '65, 67'}
    """
    ev0 = 0.67 * sds * d
    return {"sds": sds, "d": d, "ev0": ev0, "printed_page": "44, 46", "pdf_page": "65, 67"}


# ============================================================================
# Eq under paragraph 2.3.6 -- additional LRFD combinations 8/9 for
# vertical-ground-motion-sensitive members (printed p. 44, pdf_page 65)
# ============================================================================

def basic_combination_with_vertical_seismic_lrfd(d, ev0, eh, l=0.0, s=0.0,
                                                   overstrength=False):
    """Paragraph 2.3.6 [Supplement]: additional LRFD seismic load
    combinations 8 and 9, required (in addition to ASCE 7-22's standard
    combinations 6/7) for the vertical-ground-motion-sensitive members of
    paragraph 1605.1.2 (printed p. 44).

    Without overstrength (E = f(Ev, Eh)):
        8. U = 1.2D + 1.0*Ev0 + 0.3*Eh + L + 0.2S
        9. U = 0.9D - 1.0*Ev0 + 0.3*Eh

    With overstrength (Em = f(Ev, Emh), Eh replaced by Emh):
        8. U = 1.2D + 1.0*Ev0 + 0.3*Emh + L + 0.2S
        9. U = 0.9D - 1.0*Ev0 + 0.3*Emh

    Parameters
    ----------
    d : float
        Dead load effect, D.
    ev0 : float
        Vertical seismic effect (``vertical_seismic_effect_ev0``, or from
        the ASCE 7-22 Section 11.9 vertical response spectrum).
    eh : float
        Horizontal seismic load effect, Eh (or Emh if overstrength=True).
    l : float, optional
        Live load effect, L. Default 0.
    s : float, optional
        Snow load effect, S. Default 0.
    overstrength : bool, optional
        If True, `eh` is interpreted as Emh (overstrength horizontal
        seismic effect) per ASCE 7-22 Section 12.4.3. Default False.

    Returns
    -------
    dict
        {'combination_8', 'combination_9', 'overstrength', 'paragraph':
         '2.3.6', 'printed_page': '44', 'pdf_page': 65}
    """
    combo_8 = 1.2 * d + 1.0 * ev0 + 0.3 * eh + l + 0.2 * s
    combo_9 = 0.9 * d - 1.0 * ev0 + 0.3 * eh
    return {
        "combination_8": combo_8, "combination_9": combo_9,
        "overstrength": overstrength, "paragraph": "2.3.6",
        "printed_page": "44", "pdf_page": 65,
    }


# ============================================================================
# Eq under paragraph 2.4.5 -- additional ASD combinations 11/12/13
# (printed pp. 45-46, pdf_page 66-67)
# ============================================================================

def basic_combination_with_vertical_seismic_asd(d, ev0, eh, l=0.0, s=0.0,
                                                  overstrength=False):
    """Paragraph 2.4.5 [Supplement]: additional ASD seismic load
    combinations 11, 12, and 13, required (in addition to ASCE 7-22's
    standard combinations 8/9/10) for the vertical-ground-motion-sensitive
    members of paragraph 1605.1.2 (printed pp. 45-46).

    Without overstrength (E = f(Ev, Eh)):
        11. U = 1.0D + 0.7*Ev0 + 0.21*Eh
        12. U = 1.0D + 0.525*Ev0 + 0.1575*Eh + 0.75L + 0.75S
        13. U = 0.6D - 0.7*Ev0 + 0.21*Eh

    With overstrength (Em = f(Ev, Emh), Eh replaced by Emh): same
    coefficients applied to Emh in place of Eh.

    Parameters
    ----------
    d, ev0, eh, l, s, overstrength
        As in ``basic_combination_with_vertical_seismic_lrfd``.

    Returns
    -------
    dict
        {'combination_11', 'combination_12', 'combination_13',
         'overstrength', 'paragraph': '2.4.5', 'printed_page': '45-46',
         'pdf_page': '66-67'}
    """
    combo_11 = 1.0 * d + 0.7 * ev0 + 0.21 * eh
    combo_12 = 1.0 * d + 0.525 * ev0 + 0.1575 * eh + 0.75 * l + 0.75 * s
    combo_13 = 0.6 * d - 0.7 * ev0 + 0.21 * eh
    return {
        "combination_11": combo_11, "combination_12": combo_12,
        "combination_13": combo_13, "overstrength": overstrength,
        "paragraph": "2.4.5", "printed_page": "45-46", "pdf_page": "66-67",
    }


# ============================================================================
# Eq B-1, B-2 -- Appendix B alternate RC IV seismic load combinations
# (printed p. 112, pdf_page 133)
# ============================================================================

def alternate_rc4_seismic_combination(d, l, s, e, combination="additive"):
    """Eq B-1/B-2: Appendix B alternate nonlinear-design seismic load
    combinations for Risk Category IV buildings, REPLACING ASCE 7-22
    Section 2.3.6 combinations 6/7 when the Appendix B alternate procedure
    is used (printed p. 112).

    Gravity and seismic additive (Eq B-1):
        U = 1.1*(D + 0.25*L + 0.15*S) + E
    Gravity and seismic counteractive (Eq B-2):
        U = 0.9*D + E

    Where E is the horizontal-and-vertical earthquake effect at the BSE-1N
    displacement (Delta_S) or MCER displacement (Delta_M) from the
    nonlinear analysis (paragraph B-18.1). Per the exception in paragraph
    B-5.2, S may be taken as zero if the ASCE 7-22 design flat-roof snow
    load is less than 40 psf.

    Parameters
    ----------
    d : float
        Dead load effect, D.
    l : float
        Unreduced design live load effect, L.
    s : float
        Design flat-roof snow load effect, S (per ASCE 7-22 for an RC IV
        building; may be taken as 0 if < 40 psf per the exception).
    e : float
        Horizontal-and-vertical earthquake effect, E, at the BSE-1N or
        MCER target displacement (from nonlinear analysis).
    combination : str, optional
        'additive' (Eq B-1, default) or 'counteractive' (Eq B-2).

    Returns
    -------
    dict
        {'u', 'equation', 'printed_page': '112', 'pdf_page': 133}
    """
    if combination == "additive":
        u = 1.1 * (d + 0.25 * l + 0.15 * s) + e
        equation = "B-1"
    elif combination == "counteractive":
        u = 0.9 * d + e
        equation = "B-2"
    else:
        raise ValueError(
            f"combination must be 'additive' or 'counteractive', got {combination!r}"
        )
    return {"u": u, "equation": equation, "printed_page": "112", "pdf_page": 133}


# ============================================================================
# Paragraph 2106.2.3 -- coupling-beam capacity-design shear check
# (printed pp. 36-37, pdf_page 57-58)
# ============================================================================

def coupling_beam_shear_demand(mn1, mn2, lc, vg):
    """Paragraph 2106.2.3 [Addition]: for coupling beams between shear
    walls in structures assigned to SDC D or higher, the required design
    shear strength must satisfy (printed pp. 36-37):

        phi*Vn >= 1.25*(Mn1 + Mn2)/Lc + 1.4*Vg

    This is a capacity-design check: the coupling beam must reach its
    moment/shear nominal strength before either adjoining shear wall
    reaches its own nominal strength.

    Parameters
    ----------
    mn1, mn2 : float
        Nominal moment strengths at the two ends of the coupling beam.
    lc : float
        Length of the beam between the shear walls.
    vg : float
        Unfactored shear force on the beam due to gravity loads.

    Returns
    -------
    dict
        {'mn1', 'mn2', 'lc', 'vg', 'required_phi_vn', 'paragraph':
         '2106.2.3', 'printed_page': '36-37', 'pdf_page': '57-58'}
    """
    required_phi_vn = 1.25 * (mn1 + mn2) / lc + 1.4 * vg
    return {
        "mn1": mn1, "mn2": mn2, "lc": lc, "vg": vg,
        "required_phi_vn": required_phi_vn,
        "paragraph": "2106.2.3", "printed_page": "36-37", "pdf_page": "57-58",
    }


# ============================================================================
# Eq 12.12-1 -- Chapter 7 healthcare structural separation
# (printed p. 100, pdf_page 121)
# ============================================================================

def structural_separation_healthcare(cd, delta_max):
    """Eq 12.12-1 [Replacement]: structural separation (maximum inelastic
    displacement) for critical healthcare facilities, replacing the ASCE
    7-16 Equation 12.12-1 form used in Chapter 7 (printed p. 100).

        delta_M = Cd * delta_max

    Parameters
    ----------
    cd : float
        Deflection amplification factor, Cd (Table 7-1).
    delta_max : float
        Maximum elastic displacement at the critical location, delta_max.

    Returns
    -------
    dict
        {'cd', 'delta_max', 'delta_m', 'equation': '12.12-1', 'printed_page':
         '100', 'pdf_page': 121}
    """
    delta_m = cd * delta_max
    return {"cd": cd, "delta_max": delta_max, "delta_m": delta_m,
            "equation": "12.12-1", "printed_page": "100", "pdf_page": 121}
