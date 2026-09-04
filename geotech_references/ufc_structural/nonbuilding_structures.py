"""UFC 3-301-01 Chapter 5 -- Nonbuilding Structures (printed pp. 85-86,
pdf_page 106-107).

This chapter prints NO design equations or tables of its own -- it is a
pure governing-standard pointer list for eleven nonbuilding structure types
(paragraphs 5-1 through 5-10; transmission towers and poles share paragraph
5-8 but cite different standards) not otherwise covered by Chapters 2/3.
Apply the referenced standard directly.
"""

NONBUILDING_STRUCTURE_STANDARDS = {
    "highway_bridge": {
        "paragraph": "5-1",
        "governing_standard": "AASHTO LRFD Bridge Design Specifications",
        "notes": "Design examples in the PCI Bridge Design Manual and FHWA LRFD design examples.",
    },
    "railroad_bridge": {
        "paragraph": "5-2",
        "governing_standard": "AREMA Manual for Railway Engineering",
    },
    "tanks_liquid_storage": {
        "paragraph": "5-3",
        "governing_standard": "NFPA 22, AWWA D100, AWWA D103, AWWA D107, AWWA D115, AWWA D110, AWWA D120 (as applicable)",
    },
    "tanks_petroleum_storage": {
        "paragraph": "5-4",
        "governing_standard": "UFC 3-460-01",
    },
    "environmental_engineering_concrete_structures": {
        "paragraph": "5-5",
        "governing_standard": "ACI CODE-350",
    },
    "prestressed_concrete_tanks": {
        "paragraph": "5-6",
        "governing_standard": "ACI 372R",
    },
    "water_treatment_facilities": {
        "paragraph": "5-7",
        "governing_standard": "Water Environment Federation (WEF) Manual of Practice (MOP) 8",
    },
    "transmission_towers": {
        "paragraph": "5-8",
        "governing_standard": "ASCE 10",
    },
    "transmission_poles": {
        "paragraph": "5-8",
        "governing_standard": "IEEE Standards Association's National Electric Safety Code",
    },
    "antenna_towers": {
        "paragraph": "5-9",
        "governing_standard": "ANSI/TIA-222-H",
    },
    "pedestrian_bridges": {
        "paragraph": "5-10",
        "governing_standard": "AASHTO LRFD Guide Specifications for Design of Pedestrian Bridges",
    },
}


def nonbuilding_structure_governing_standard(structure_type):
    """Chapter 5: the governing design standard for a nonbuilding structure
    type not otherwise covered by this UFC's Chapters 2/3 (printed
    pp. 85-86).

    Parameters
    ----------
    structure_type : str
        A key of ``NONBUILDING_STRUCTURE_STANDARDS`` (e.g.
        'highway_bridge', 'tanks_petroleum_storage').

    Returns
    -------
    dict
        {'structure_type', 'paragraph', 'governing_standard', 'notes'
         (if any), 'table': None, 'printed_page': '85-86', 'pdf_page':
         '106-107'}
    """
    key = structure_type.lower().strip()
    if key not in NONBUILDING_STRUCTURE_STANDARDS:
        raise ValueError(
            f"structure_type must be one of {sorted(NONBUILDING_STRUCTURE_STANDARDS)}, "
            f"got {structure_type!r}"
        )
    row = dict(NONBUILDING_STRUCTURE_STANDARDS[key])
    row.update({"structure_type": key, "printed_page": "85-86", "pdf_page": "106-107"})
    return row


def list_nonbuilding_structure_types():
    """Lists the nonbuilding structure type keys covered by Chapter 5."""
    return sorted(NONBUILDING_STRUCTURE_STANDARDS)
