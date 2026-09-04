"""GSA Alternate Path Analysis and Design Guidelines Chapters 1-2 --
Introduction and Applicability (printed pp. 1-6, pdf_page 13-18).

The GSA Guidelines (October 24, 2013, Revision 1, January 28, 2016) adopt
UFC 4-023-03's Alternate Path (AP) methodology "in its entirety" (Section
1.4/1.5) but replace UFC 4-023-03's story-count/Risk-Category applicability
trigger with GSA's own Facility Security Level (FSL) trigger (Section 2.3),
per the ISC Risk Management Process. Unlike UFC 4-023-03 (mandatory for all
new construction of 3+ stories, RC-based method combination), GSA's
Guidelines:
  - Do NOT apply at all to FSL I/II facilities, regardless of story count
    (Section 2.3.1).
  - Apply to FSL III/IV facilities only at 4 stories or more (Section
    2.3.2), requiring BOTH Alternate Path and Redundancy.
  - Apply to FSL V facilities at ANY story count (Section 2.3.3), requiring
    Alternate Path only -- Redundancy is not separately required because
    Section 3.2.9's FSL V removal scope already covers every floor level
    (Commentary C2.3).
  - Never require Tie Forces or Enhanced Local Resistance (removed in
    their entirety throughout the document -- see alternate_path.py and
    redundancy.py module docstrings).

Provides:
  - ``fsl_applicability`` -- Section 2.3 / Figure 2.1's applicability flow
    chart: whether these Guidelines apply, and if so whether Alternate
    Path and/or Redundancy are required, for a given Facility Security
    Level and story count.
  - ``counts_as_story`` -- Section 2.3.2's story-count exclusion (mechanical
    penthouses and parking are not counted).
  - ``addition_triggers_existing_building_evaluation`` -- Section 2.1's
    50%-of-existing-gross-area threshold (Commentary C2.1) at which a new
    addition's construction also triggers evaluation of the existing
    portion of the building.

Usage::

    from geotech_references.gsa_collapse.applicability import fsl_applicability
"""


# ============================================================================
# Section 2.3 / Figure 2.1 -- Facility Security Level (FSL) Applicability
# (printed pp. 4-6, pdf_page 16-18)
# ============================================================================

FSL_APPLICABILITY = {
    "I": {"applies": False, "minimum_stories": None},
    "II": {"applies": False, "minimum_stories": None},
    "III": {"applies": True, "minimum_stories": 4},
    "IV": {"applies": True, "minimum_stories": 4},
    "V": {"applies": True, "minimum_stories": 0},
}


def fsl_applicability(fsl, num_stories=None):
    """Section 2.3 and Figure 2.1 (Applicability Flow Chart): determines
    whether these Guidelines apply to a facility of a given Facility
    Security Level (FSL), and if so which design procedures are required
    (printed pp. 4-6).

    - FSL I & II (Section 2.3.1): NOT applicable, regardless of the number
      of floors, given the low occupancy and risk level of these facilities.
    - FSL III & IV (Section 2.3.2): applicable to buildings with 4 stories
      or more (measured from the lowest point of exterior grade to the
      highest point of elevation; unoccupied floors such as mechanical
      penthouses or parking are not counted -- see ``counts_as_story``).
      Both the Alternate Path AND Redundancy Requirements (Section 3.4)
      must be implemented.
    - FSL V (Section 2.3.3): applicable regardless of the number of floors.
      Only the Alternate Path method is required; Redundancy Requirements
      need not be separately applied (Commentary C2.3: FSL V's removal
      scope already covers every floor level up the height of the
      building, per ``alternate_path.removal_locations``, so the intent of
      Redundancy is inherently met).

    Parameters
    ----------
    fsl : str
        'I', 'II', 'III', 'IV', or 'V'.
    num_stories : int, optional
        Number of stories (per ``counts_as_story``), counted from the
        lowest point of exterior grade to the highest point of elevation.
        Required to resolve applicability for FSL III/IV; unused for
        FSL I/II/V.

    Returns
    -------
    dict
        {'fsl', 'applies' (bool), 'alternate_path_required' (bool),
         'redundancy_required' (bool), 'minimum_stories' (int or None),
         'basis' (str), 'section': '2.3', 'printed_page': '4-6',
         'pdf_page': '16-18'}
    """
    key = str(fsl).upper().strip()
    if key not in FSL_APPLICABILITY:
        raise ValueError(f"fsl must be one of I/II/III/IV/V, got {fsl!r}")
    row = FSL_APPLICABILITY[key]

    if key in ("I", "II"):
        return {
            "fsl": key, "applies": False, "alternate_path_required": False,
            "redundancy_required": False, "minimum_stories": None,
            "basis": "Section 2.3.1: not required for FSL I/II regardless of story count",
            "section": "2.3", "printed_page": "4-6", "pdf_page": "16-18",
        }
    if key == "V":
        return {
            "fsl": key, "applies": True, "alternate_path_required": True,
            "redundancy_required": False, "minimum_stories": 0,
            "basis": "Section 2.3.3: applies at any story count; Alternate Path only",
            "section": "2.3", "printed_page": "4-6", "pdf_page": "16-18",
        }
    # FSL III/IV
    if num_stories is None:
        raise ValueError("num_stories is required to resolve applicability for FSL III/IV")
    applies = num_stories >= row["minimum_stories"]
    return {
        "fsl": key, "applies": applies,
        "alternate_path_required": applies, "redundancy_required": applies,
        "minimum_stories": row["minimum_stories"],
        "basis": (
            f"Section 2.3.2: FSL {key} applies at {row['minimum_stories']}+ stories "
            f"({num_stories} stories {'meets' if applies else 'does not meet'} the threshold); "
            "both Alternate Path and Redundancy required"
        ),
        "section": "2.3", "printed_page": "4-6", "pdf_page": "16-18",
    }


def counts_as_story(is_mechanical_penthouse_or_parking):
    """Section 2.3.2: a mechanical penthouse or parking level is NOT
    counted as a "story" toward the FSL III/IV 4-story applicability
    threshold (printed p. 5).

    Parameters
    ----------
    is_mechanical_penthouse_or_parking : bool
        True if the level is an unoccupied mechanical penthouse or a
        parking level.

    Returns
    -------
    dict
        {'counts_as_story' (bool), 'section': '2.3.2', 'printed_page': '5',
         'pdf_page': 17}
    """
    return {"counts_as_story": not bool(is_mechanical_penthouse_or_parking),
            "section": "2.3.2", "printed_page": "5", "pdf_page": 17}


# ============================================================================
# Section 2.1 -- New Construction and Building Additions (printed p. 4,
# pdf_page 16; threshold per Commentary C2.1, printed p. C4, pdf_page 80)
# ============================================================================

def addition_triggers_existing_building_evaluation(
        addition_gross_area, existing_gross_area, existing_undergoing_major_renovation):
    """Section 2.1 / Commentary C2.1: a new building addition is always
    itself designed to these Guidelines' new-construction requirements
    (per the applicable FSL). The requirement does NOT extend to the
    EXISTING portion of the building unless the addition is 50% or more of
    the existing building's gross area AND the existing portion is
    undergoing a major structural renovation -- in which case the existing
    portion must also be evaluated under these Guidelines' existing-
    building provisions (printed p. C4).

    Parameters
    ----------
    addition_gross_area : float
        Gross floor area of the new addition (ft2 or m2).
    existing_gross_area : float
        Gross floor area of the existing building (same units).
    existing_undergoing_major_renovation : bool
        True if the existing portion is undergoing a major structural
        renovation concurrently with the addition (see ``B1`` definition
        of "Major Modernization").

    Returns
    -------
    dict
        {'area_ratio', 'existing_portion_must_be_evaluated' (bool),
         'section': '2.1', 'printed_page': '4 (C4)', 'pdf_page': '16 (80)'}
    """
    ratio = addition_gross_area / existing_gross_area
    triggers = (ratio >= 0.5) and bool(existing_undergoing_major_renovation)
    return {
        "area_ratio": ratio, "existing_portion_must_be_evaluated": triggers,
        "section": "2.1", "printed_page": "4 (C4)", "pdf_page": "16 (80)",
    }
