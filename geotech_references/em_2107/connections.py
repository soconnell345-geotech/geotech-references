"""EM 1110-2-2107 Chapter 6 -- Connections and Detailing.

This chapter is ENTIRELY qualitative/procedural guidance -- material and
bolt-grade selection rules, welding-code selection, faying-surface
preparation classes, and detailing practices for fatigue/fracture/
corrosion/fabrication -- with no printed numeric design equations at all
(no slip-coefficient values, no bolt shear/bearing capacity formulas; those
live in AISC 360/RCSC S348 by reference, paragraph 6.1.3.8.1). The lookups
below digitize the chapter's few concrete, enumerable design RULES (which
bolt/weld standard applies to which situation) as callable functions;
nothing here is a computed quantity. Printed pages per the 1 August 2022
edition (pdf_page = printed_page + 8).
"""

# ============================================================================
# Paragraph 6.1.3.4 -- structural bolt grades (printed p. 38, pdf_page 46)
# ============================================================================

STRUCTURAL_BOLT_GRADES = ["ASTM F3125 Grade A325", "ASTM F3125 Grade A490", "ASTM F3148"]
NONSTRUCTURAL_BOLT_GRADES = ["ASTM A307", "SAE J429 Grade 5", "SAE J429 Grade 8"]


def bolt_grade_check(grade, application="structural"):
    """Paragraph 6.1.3.4/6.1.3.10: allowed bolt grades by application
    (printed pp. 38, 41).

    Structural connections in HSS must use ASTM F3125 Grade A325, ASTM
    F3125 Grade A490, or ASTM F3148 bolts (with compatible nuts/washers).
    ASTM A307 or graded bolts (SAE J429 Grade 5/8) may be used only for
    NON-structural applications, per AISC and RCSC S348.

    Parameters
    ----------
    grade : str
        A bolt grade designation (matched case-insensitively against
        ``STRUCTURAL_BOLT_GRADES``/``NONSTRUCTURAL_BOLT_GRADES``).
    application : str, optional
        'structural' (default) or 'nonstructural'.

    Returns
    -------
    dict
        {'grade', 'application', 'permitted' (bool), 'printed_page',
         'pdf_page'}
    """
    g = grade.strip().lower()
    structural_ok = any(g == s.lower() for s in STRUCTURAL_BOLT_GRADES)
    nonstructural_ok = structural_ok or any(g == s.lower() for s in NONSTRUCTURAL_BOLT_GRADES)
    if application == "structural":
        permitted, page = structural_ok, "38"
    elif application == "nonstructural":
        permitted, page = nonstructural_ok, "41"
    else:
        raise ValueError(f"application must be 'structural' or 'nonstructural', got {application!r}")
    return {"grade": grade, "application": application, "permitted": permitted,
            "printed_page": page, "pdf_page": int(page) + 8}


# ============================================================================
# Paragraph 6.1.2.1 -- welding code selection (printed p. 38, pdf_page 46)
# ============================================================================

def welding_code_selection(cyclically_loaded_or_fcm):
    """Paragraph 6.1.2.1: welding code selection (printed p. 38).

    Cyclically loaded members and Fracture Critical Members (FCM) must be
    designed/fabricated per AWS D1.5(M) (the bridge welding code) -- and it
    "should be used for fabrication of all HSS." AWS D1.1(M) (the building
    welding code) may be used ONLY on redundant, non-cyclically-loaded HSS
    where fatigue and fracture are not design considerations.

    Parameters
    ----------
    cyclically_loaded_or_fcm : bool
        True if the member is cyclically loaded or is a Fracture Critical
        Member.

    Returns
    -------
    dict
        {'cyclically_loaded_or_fcm', 'code', 'printed_page': '38',
         'pdf_page': 46}
    """
    code = "AWS D1.5(M)" if cyclically_loaded_or_fcm else "AWS D1.5(M) (preferred) or AWS D1.1(M) (permitted for redundant, non-cyclic HSS only)"
    return {"cyclically_loaded_or_fcm": cyclically_loaded_or_fcm, "code": code,
            "printed_page": "38", "pdf_page": 46}


# ============================================================================
# Paragraph 6.1.3.8.2 -- faying-surface preparation classes
# (printed p. 39, pdf_page 47)
# ============================================================================

FAYING_SURFACE_CLASSES = {
    "clean_mill_scale": "Class A",
    "blast_cleaned": "Class B",
}


def faying_surface_class(surface_condition):
    """Paragraph 6.1.3.8.2: AISC/RCSC S348 faying-surface classification as
    referenced in this manual (printed p. 39). This manual gives no numeric
    slip coefficient for either class -- see AISC 360/RCSC S348 directly;
    it only notes that clean mill scale and blast-cleaned steel qualify as
    Class A/B respectively, and recommends priming connection faying
    surfaces for HSS corrosion protection regardless (with a qualified slip-
    critical primer, since vinyl paint alone does not qualify, paragraph
    6.1.3.8).

    Parameters
    ----------
    surface_condition : str
        'clean_mill_scale' or 'blast_cleaned'.

    Returns
    -------
    dict
        {'surface_condition', 'class', 'printed_page': '39', 'pdf_page': 47}
    """
    if surface_condition not in FAYING_SURFACE_CLASSES:
        raise ValueError(
            f"surface_condition must be one of {sorted(FAYING_SURFACE_CLASSES)}, "
            f"got {surface_condition!r}"
        )
    return {"surface_condition": surface_condition,
            "class": FAYING_SURFACE_CLASSES[surface_condition],
            "printed_page": "39", "pdf_page": 47}
