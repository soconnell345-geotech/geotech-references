"""UFC 4-023-03 Appendix H -- International Building Code Modifications
for Construction of Buildings to Resist Progressive Collapse (printed
pp. 225-228, pdf_page 240-243).

A narrative [Addition]/[Replacement] modification to IBC 2015 Chapters 16
(Construction Documents) and 17 (Structural Tests and Special
Inspections), requiring construction-document notes, a quality-assurance
plan, and material-specific special inspections for buildings designed to
this UFC. This module digitizes the enumerable, Risk-Category-and-
material-keyed criteria; the narrative contractor-responsibility and
structural-observation procedural text (Sections 1710.2, 1710.3) is not
reprinted here -- consult the printed appendix directly.
"""


# ============================================================================
# Section 1603.1.9 -- Construction Document Requirements (printed p. 225,
# pdf_page 240)
# ============================================================================

def construction_document_requirements():
    """Section 1603.1.9 [Addition]: information that must be indicated on
    the construction documents for a building designed to this UFC
    (printed p. 225).

    Returns
    -------
    dict
        {'required_items' (list of str), 'section': '1603.1.9',
         'printed_page': '225', 'pdf_page': 240}
    """
    return {
        "required_items": [
            "General note: 'Design of the building is in accordance with "
            "UFC 4-023-03, DD/MM/YYYY. Future additions or alterations to "
            "this structure shall not jeopardize the requirements for "
            "progressive collapse resistance.'",
            "Risk Category II, III, or IV.",
            "Method(s) of progressive collapse resistance (Tie Force, "
            "Alternate Path, Enhanced Local Resistance, or combinations "
            "thereof).",
        ],
        "section": "1603.1.9", "printed_page": "225", "pdf_page": 240,
    }


# ============================================================================
# Section 1710.1.1 -- Quality Assurance Plan Trigger by Risk Category
# (printed pp. 225-226, pdf_page 240-241)
# ============================================================================

_QA_PLAN_TRIGGERS = {
    "II": (
        "Structural elements provide horizontal and vertical Tie Force "
        "capacity plus Enhanced Local Resistance (corner/penultimate "
        "first-story columns/walls), OR the Alternate Path method is "
        "used to bridge over deficient elements."
    ),
    "III": (
        "Horizontal and vertical Tie Forces, Alternate Path design, and "
        "Enhanced Local Resistance (first two perimeter stories designed "
        "for increased flexural and shear resistance)."
    ),
    "IV": (
        "Design based on the results of a systematic risk assessment of "
        "the building."
    ),
}


def qa_plan_required(risk_category):
    """Section 1710.1.1 [Addition]: a quality-assurance plan is required
    for structures designed to progressive-collapse Risk Category II,
    III, or IV; RC I requires no QA plan (printed pp. 225-226).

    Parameters
    ----------
    risk_category : str
        'I', 'II', 'III', or 'IV'.

    Returns
    -------
    dict
        {'qa_plan_required' (bool), 'trigger_description' (str or None),
         'risk_category', 'section': '1710.1.1', 'printed_page': '225-226',
         'pdf_page': '240-241'}
    """
    key = str(risk_category).upper().strip()
    if key not in ("I", "II", "III", "IV"):
        raise ValueError(f"risk_category must be one of I/II/III/IV, got {risk_category!r}")
    return {
        "qa_plan_required": key != "I",
        "trigger_description": _QA_PLAN_TRIGGERS.get(key),
        "risk_category": key, "section": "1710.1.1",
        "printed_page": "225-226", "pdf_page": "240-241",
    }


def qa_plan_detailed_requirements():
    """Section 1710.1.2 [Addition]: when a QA plan is required, it must
    provide for these four items (printed p. 226).

    Returns
    -------
    dict
        {'required_items' (list of str), 'section': '1710.1.2',
         'printed_page': '226', 'pdf_page': 241}
    """
    return {
        "required_items": [
            "Horizontal and vertical tie force connections, as required by material type.",
            "Roof and floor diaphragm systems, including transverse, longitudinal, and peripheral ties.",
            "Vertical progressive-collapse-resisting systems, including vertical ties and bridging connections.",
            "Perimeter ground-floor columns and walls with enhanced ductility requirements ensuring shear strength exceeds flexural strength.",
        ],
        "section": "1710.1.2", "printed_page": "226", "pdf_page": 241,
    }


# ============================================================================
# Section 1711 -- Special Inspections by Material (printed pp. 227-228,
# pdf_page 242-243)
# ============================================================================

_SPECIAL_INSPECTIONS = {
    "structural_steel": {
        "requirement": "Continuous special inspection for structural welding per AWS D1.1, including floor and roof deck welding.",
        "exemptions": ["Single-pass fillet welds not exceeding 5/16-in (7.9 mm) in size."],
        "section": "1711.2",
    },
    "wood": {
        "requirement": "Periodic special inspections during nailing, bolting, anchoring, and other fastening of components within the progressive-collapse-resisting system, including horizontal tie force elements, vertical tie force elements, and bridging elements.",
        "exemptions": [],
        "section": "1711.3",
    },
    "cold_formed_steel": {
        "requirement": "Periodic special inspections during welding operations, screw attachment, bolting, anchoring, and other fastening of components within the progressive-collapse-resisting system, including horizontal tie force elements, vertical tie force elements, and bridging elements.",
        "exemptions": [],
        "section": "1711.4",
    },
    "cast_in_place_concrete": {
        "requirement": "Continuous special inspection for reinforcing steel placement, with particular emphasis on reinforcing steel anchorages, laps, and other details within the progressive-collapse-resisting system, including horizontal tie force elements, vertical tie force elements, and bridging elements.",
        "exemptions": [],
        "section": "1711.5",
    },
}


def special_inspection_requirements(material):
    """Section 1711 [Addition]: material-specific special inspection
    requirements for the progressive-collapse-resisting system (printed
    pp. 227-228). Special inspections under 1711.2-1711.5 apply to
    structures designed for RC II, III, or IV per the same triggers as
    ``qa_plan_required``.

    Parameters
    ----------
    material : str
        A key of the requirements table: 'structural_steel', 'wood',
        'cold_formed_steel', or 'cast_in_place_concrete'.

    Returns
    -------
    dict
        The row data plus {'material', 'printed_page': '227-228',
        'pdf_page': '242-243'}.
    """
    key = material.lower().strip()
    if key not in _SPECIAL_INSPECTIONS:
        raise ValueError(f"material must be one of {sorted(_SPECIAL_INSPECTIONS)}, got {material!r}")
    row = dict(_SPECIAL_INSPECTIONS[key])
    row.update({"material": key, "printed_page": "227-228", "pdf_page": "242-243"})
    return row


def structural_observation_required(contracting_officer_requires=False, risk_category="II"):
    """Section 1712.1 [Addition]: structural observations of the
    progressive-collapse-resisting system are required when the
    contracting officer requires them, OR unconditionally for Risk
    Category IV structures (printed p. 228).

    Parameters
    ----------
    contracting_officer_requires : bool, optional
        True if the contracting officer has required structural
        observation. Default False.
    risk_category : str, optional
        'I', 'II', 'III', or 'IV'. Default 'II'.

    Returns
    -------
    dict
        {'required' (bool), 'reason', 'section': '1712.1',
         'printed_page': '228', 'pdf_page': 243}
    """
    key = str(risk_category).upper().strip()
    if key == "IV":
        return {"required": True, "reason": "Risk Category IV (unconditional)",
                "section": "1712.1", "printed_page": "228", "pdf_page": 243}
    required = bool(contracting_officer_requires)
    reason = "contracting officer requirement" if required else "not triggered"
    return {"required": required, "reason": reason, "section": "1712.1",
            "printed_page": "228", "pdf_page": 243}
