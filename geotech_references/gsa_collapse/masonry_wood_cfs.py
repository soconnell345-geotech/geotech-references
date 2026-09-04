"""GSA Alternate Path Analysis and Design Guidelines Chapters 6-8 --
Masonry, Wood, and Cold-Formed Steel (printed pp. 47-50, pdf_page 59-62),
combined given how little material-specific numeric content each prints.

Chapters 6-8 of UFC 4-023-03 are each adopted with ONE printed
modification (the opening list of each chapter): all Tie Force and
Enhanced Local Resistance references are REMOVED IN THEIR ENTIRETY.
Unlike Chapters 4-5 (reinforced concrete, structural steel), these three
material chapters do NOT revise ASCE 41's performance level from Life
Safety to Collapse Prevention -- Commentary C6/C7/C8 explain this is due
to a lack of available test data supporting a Collapse-Prevention-level
change for masonry, wood, or cold-formed steel construction (printed
p. C23).

Provides the handful of printed numeric factors and pointers each chapter
carries:
  - ``masonry_material_basis`` / ``masonry_phi_basis`` -- Sections 6.1-6.2
    (ASCE 41 Table 11-1 over-strength factors; ACI 530 Phi factors).
  - ``wood_material_basis`` / ``wood_phi_basis`` -- Sections 7.1-7.2 (ASCE
    41 default expected strengths from AF&PA/ASCE 16; NDS Phi factors).
  - ``wood_time_effect_factor`` -- Section 7.3: the wood time-effect
    factor lambda = 1.0.
  - ``cfs_material_basis`` / ``cfs_phi_basis`` -- Sections 8.1-8.2 (ASCE
    41 default expected strengths for light-metal-framing shear walls;
    AISI Phi factors).
  - ``default_lower_bound_factor`` -- Sections 7.1/8.1: when default
    LOWER BOUND strength values are needed for wood or cold-formed steel
    (and no test/statistical data is available), multiply the default
    EXPECTED strength values by 0.85.
  - ``masonry_wood_cfs_performance_level`` -- all three chapters use ASCE
    41 Chapter 11 (masonry) / 12 (wood, cold-formed steel) Life Safety
    modeling parameters, nonlinear acceptance criteria, and linear
    m-factors for primary and secondary components (printed pp. 47, 49,
    50); this document does not print its own replacement tables for
    these three materials (contrast Chapters 4-5's Tables 6-11).
"""


def masonry_material_basis():
    """Section 6.1: over-strength factors for masonry are per ASCE 41
    Table 11-1 (printed p. 47).

    Returns
    -------
    dict
        {'basis': 'ASCE 41 Table 11-1', 'section': '6.1',
         'printed_page': '47', 'pdf_page': 59}
    """
    return {"basis": "ASCE 41 Table 11-1", "section": "6.1", "printed_page": "47", "pdf_page": 59}


def masonry_phi_basis():
    """Section 6.2: strength reduction factor Phi for masonry is per ACI
    530, Building Code Requirements for Masonry Structures (printed
    p. 47).

    Returns
    -------
    dict
        {'basis': 'ACI 530', 'section': '6.2', 'printed_page': '47',
         'pdf_page': 59}
    """
    return {"basis": "ACI 530", "section": "6.2", "printed_page": "47", "pdf_page": 59}


def wood_material_basis():
    """Section 7.1: default expected-strength values for wood materials
    are based on design resistance values from AF&PA/ASCE 16 (1996), per
    ASCE 41; ASCE 41 also provides default expected strengths for shear
    walls and wood diaphragms (printed p. 48).

    Returns
    -------
    dict
        {'basis': 'AF&PA/ASCE 16-96, via ASCE 41 defaults',
         'section': '7.1', 'printed_page': '48', 'pdf_page': 60}
    """
    return {"basis": "AF&PA/ASCE 16-96, via ASCE 41 defaults", "section": "7.1",
            "printed_page": "48", "pdf_page": 60}


def wood_phi_basis():
    """Section 7.2: strength reduction factor Phi for wood is per
    AF&PA/AWC National Design Specification (NDS) for Wood Construction
    (printed p. 48).

    Returns
    -------
    dict
        {'basis': 'AF&PA/AWC NDS', 'section': '7.2', 'printed_page': '48',
         'pdf_page': 60}
    """
    return {"basis": "AF&PA/AWC NDS", "section": "7.2", "printed_page": "48", "pdf_page": 60}


def wood_time_effect_factor():
    """Section 7.3: the wood time-effect factor lambda is 1.0 (printed
    p. 48) -- IDENTICAL to UFC 4-023-03's own printed value (see
    ``geotech_references.ufc_collapse``'s docstring reference to this
    factor).

    Returns
    -------
    dict
        {'lambda': 1.0, 'section': '7.3', 'printed_page': '48',
         'pdf_page': 60}
    """
    return {"lambda": 1.0, "section": "7.3", "printed_page": "48", "pdf_page": 60}


def cfs_material_basis():
    """Section 8.1: ASCE 41 provides default expected-strength values for
    light-metal-framing shear walls (printed p. 50).

    Returns
    -------
    dict
        {'basis': 'ASCE 41 defaults for light-metal-framing shear walls',
         'section': '8.1', 'printed_page': '50', 'pdf_page': 62}
    """
    return {"basis": "ASCE 41 defaults for light-metal-framing shear walls",
            "section": "8.1", "printed_page": "50", "pdf_page": 62}


def cfs_phi_basis():
    """Section 8.2: strength reduction factor Phi for cold-formed steel
    is per the AISI/COS/NASPEC North American Specification for the
    Design of Cold-Formed Steel Structural Members (printed p. 50).

    Returns
    -------
    dict
        {'basis': 'AISI/COS/NASPEC', 'section': '8.2',
         'printed_page': '50', 'pdf_page': 62}
    """
    return {"basis": "AISI/COS/NASPEC", "section": "8.2", "printed_page": "50", "pdf_page": 62}


def default_lower_bound_factor():
    """Sections 7.1 and 8.1: when default LOWER BOUND strength values are
    needed for wood or cold-formed steel construction (and statistically-
    determined values are unavailable), multiply the default EXPECTED
    strength values by 0.85 (printed pp. 48, 50).

    Returns
    -------
    dict
        {'factor': 0.85, 'applies_to': ['wood', 'cold_formed_steel'],
         'section': '7.1 / 8.1', 'printed_page': '48, 50',
         'pdf_page': '60, 62'}
    """
    return {"factor": 0.85, "applies_to": ["wood", "cold_formed_steel"],
            "section": "7.1 / 8.1", "printed_page": "48, 50", "pdf_page": "60, 62"}


def masonry_wood_cfs_performance_level(material):
    """Sections 6.4.2, 7.5.2, 8.4.2: masonry, wood, and cold-formed steel
    each use ASCE 41's LIFE SAFETY (not Collapse Prevention) modeling
    parameters, nonlinear acceptance criteria, and linear m-factors for
    primary and secondary components, from ASCE 41 Chapter 11 (masonry) or
    Chapter 12 (wood, cold-formed steel) (printed pp. 47, 49, 50).
    Commentary C6/C7/C8 (printed p. C23) attributes this to a lack of
    available test data supporting a change to Collapse Prevention for
    these materials -- contrast reinforced concrete and structural steel
    (Chapters 4-5), which DO use Collapse Prevention.

    Parameters
    ----------
    material : str
        'masonry', 'wood', or 'cold_formed_steel'.

    Returns
    -------
    dict
        {'material', 'performance_level': 'life_safety', 'asce_41_chapter'
         (11 or 12), 'commentary_basis': 'lack of available test data
         supporting Collapse Prevention', 'section', 'printed_page',
         'pdf_page'}
    """
    key = material.lower().strip()
    rows = {
        "masonry": {"asce_41_chapter": 11, "section": "6.4.2", "printed_page": "47", "pdf_page": 59},
        "wood": {"asce_41_chapter": 12, "section": "7.5.2", "printed_page": "49", "pdf_page": 61},
        "cold_formed_steel": {"asce_41_chapter": 12, "section": "8.4.2", "printed_page": "50", "pdf_page": 62},
    }
    if key not in rows:
        raise ValueError("material must be 'masonry', 'wood', or 'cold_formed_steel'")
    row = dict(rows[key])
    row.update({"material": key, "performance_level": "life_safety",
                "commentary_basis": "lack of available test data supporting Collapse Prevention"})
    return row
