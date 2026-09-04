"""UFC 3-301-01 Chapter 1 -- Introduction (general/administrative provisions).

The four modification-action definitions used throughout this UFC's IBC and
ASCE 7-22 section modifications (paragraph 1-6, printed p. 1), and the
Chapter 1 pointer paragraphs with narrow but real applicability
consequences: progressive-collapse analysis, the added Risk Category V,
and cybersecurity. Printed pp. 1-6 (pdf_page 22-27).
"""

# ============================================================================
# Paragraph 1-6 -- modification-action legend (printed p. 1, pdf_page 22)
# ============================================================================

MODIFICATION_ACTIONS = {
    "addition": (
        "Add new section, including new section number, not shown in 2024 "
        "IBC or ASCE 7-22."
    ),
    "deletion": (
        "Delete referenced 2024 IBC or ASCE 7-22 section or noted portion "
        "of a section."
    ),
    "replacement": (
        "Delete referenced 2024 IBC or ASCE 7-22 section or noted portion "
        "and replace it with the narrative shown."
    ),
    "supplement": (
        "Add narrative shown as a supplement to the narrative shown in the "
        "referenced section of 2024 IBC or ASCE 7-22."
    ),
}


def modification_action_definition(action):
    """Paragraph 1-6: definition of one of the four modification actions used
    throughout Chapters 2, 3, 6, and 7 of this UFC (printed p. 1).

    Parameters
    ----------
    action : str
        One of 'addition', 'deletion', 'replacement', 'supplement'
        (case-insensitive).

    Returns
    -------
    dict
        {'action', 'definition', 'paragraph': '1-6', 'printed_page': '1',
         'pdf_page': 22}
    """
    key = action.lower().strip()
    if key not in MODIFICATION_ACTIONS:
        raise ValueError(
            f"action must be one of {sorted(MODIFICATION_ACTIONS)}, got {action!r}"
        )
    return {
        "action": key, "definition": MODIFICATION_ACTIONS[key],
        "paragraph": "1-6", "printed_page": "1", "pdf_page": 22,
    }


# ============================================================================
# Paragraph 1-8.2 -- Progressive Collapse Analysis and Design
# (printed p. 5, pdf_page 26)
# ============================================================================

def progressive_collapse_applicability():
    """Paragraph 1-8.2: progressive-collapse applicability pointer (printed
    p. 5). This UFC prints NO trigger table of its own -- applicability
    triggers (occupancy/risk-category/story-count thresholds) live entirely
    in UFC 4-023-03, not in UFC 3-301-01.

    Returns
    -------
    dict
        {'requirement', 'governing_document': 'UFC 4-023-03', 'paragraph':
         '1-8.2', 'printed_page': '5', 'pdf_page': 26}
    """
    return {
        "requirement": (
            "When required, apply UFC 4-023-03, Design of Buildings to "
            "Resist Progressive Collapse."
        ),
        "governing_document": "UFC 4-023-03",
        "paragraph": "1-8.2", "printed_page": "5", "pdf_page": 26,
    }


# ============================================================================
# Paragraph 1-8.3 -- Design of Risk Category V Structures
# (printed p. 5, pdf_page 26)
# ============================================================================

def risk_category_v_note():
    """Paragraph 1-8.3: Risk Category V is a DoD addition to the 2024
    IBC/ASCE 7-22 risk-category scheme (printed p. 5), for national
    strategic military assets. RC V structures are designed to remain
    elastic during the MCER. The actual list of RC V occupancies is Table
    2-2 (``risk_category_and_loads.table_2_2_risk_category('V')``); full RC
    V design is governed by UFC 3-301-02, not this UFC.

    Returns
    -------
    dict
        {'note', 'risk_category_table': 'Table 2-2', 'design_document':
         'UFC 3-301-02', 'paragraph': '1-8.3', 'printed_page': '5',
         'pdf_page': 26}
    """
    return {
        "note": (
            "Risk Category V, not in the 2024 IBC/ASCE 7-22, was added to "
            "address national strategic military assets. RC V structures "
            "are designed to remain elastic during the MCER."
        ),
        "risk_category_table": "Table 2-2",
        "design_document": "UFC 3-301-02",
        "paragraph": "1-8.3", "printed_page": "5", "pdf_page": 26,
    }


# ============================================================================
# Paragraph 1-8.4 -- Cybersecurity (printed p. 5, pdf_page 26)
# ============================================================================

def cybersecurity_requirement():
    """Paragraph 1-8.4: facility-related control systems cybersecurity
    pointer (printed p. 5).

    Returns
    -------
    dict
        {'requirement', 'governing_document': 'UFC 4-010-06', 'paragraph':
         '1-8.4', 'printed_page': '5', 'pdf_page': 26}
    """
    return {
        "requirement": (
            "All facility-related control systems (including systems "
            "separate from a utility monitoring and control system) must "
            "be planned, designed, acquired, executed, and maintained in "
            "accordance with UFC 4-010-06, and as required by individual "
            "Service Implementation Policy."
        ),
        "governing_document": "UFC 4-010-06",
        "paragraph": "1-8.4", "printed_page": "5", "pdf_page": 26,
    }
