"""UFC 3-301-01 Chapter 4 -- Evaluation and Retrofit of Existing Buildings.

Table 4-1(a)/(b) performance-objective lookups (REPLACE RP 10 Tables 2-1,
2-2, 2-3, printed pp. 72-75), the RP 10 evaluation-trigger cost thresholds
(paragraph 4-2.1, printed p. 69), the benchmark-building exemption
(paragraph 4-2.3.1, printed p. 76), and the IEBC high-wind roof-diaphragm
retrofit trigger (paragraph 503.12, printed pp. 83-84).

Performance-level abbreviations (Table 4-1(a) note 1 / Table 4-1(b) note 1,
printed pp. 73, 75):
    CP  = Collapse Prevention        LmS = Limited Safety
    LS  = Life Safety                DC  = Damage Control
    IO  = Immediate Occupancy        PR  = Position Retention
    OP  = Operational                HR  = Hazard Reduced
Seismic hazard levels (BSE = Basic Safety Earthquake; see [C] RP10 Section
2.1 [Supplement], printed p. 71): BSE-2N (2% probability of exceedance in
50 years), BSE-1N (2/3 of BSE-2N), BSE-2E (5%/50yr), BSE-1E (20%/50yr).

Table 4-2 (the ASCE 41-17 benchmark-building code-vintage cross-reference,
printed pp. 78-81) is NOT digitized here -- see the ``ufc_structural``
package docstring for why.
"""

PERFORMANCE_LEVEL_ABBREVIATIONS = {
    "CP": "Collapse Prevention", "LmS": "Limited Safety", "LS": "Life Safety",
    "DC": "Damage Control", "IO": "Immediate Occupancy",
    "PR": "Position Retention", "OP": "Operational", "HR": "Hazard Reduced",
}


def performance_level_definition(abbreviation):
    """Definition of a Table 4-1(a)/(b) performance-level abbreviation
    (Table 4-1(a) note 1, printed p. 73; Table 4-1(b) note 1, printed p. 75).

    Parameters
    ----------
    abbreviation : str
        A key of ``PERFORMANCE_LEVEL_ABBREVIATIONS`` (case-insensitive
        except for the 'm'/'M' distinguishing LmS from LS -- pass exactly
        as printed, e.g. 'LmS', 'CP', 'HR').

    Returns
    -------
    dict
        {'abbreviation', 'definition'}
    """
    if abbreviation not in PERFORMANCE_LEVEL_ABBREVIATIONS:
        match = next((k for k in PERFORMANCE_LEVEL_ABBREVIATIONS
                       if k.lower() == abbreviation.lower()), None)
        if match is None:
            raise ValueError(
                f"abbreviation must be one of {sorted(PERFORMANCE_LEVEL_ABBREVIATIONS)}, "
                f"got {abbreviation!r}"
            )
        abbreviation = match
    return {"abbreviation": abbreviation, "definition": PERFORMANCE_LEVEL_ABBREVIATIONS[abbreviation]}


# ============================================================================
# Table 4-1(a) -- Structural Performance Objectives (printed pp. 72-73,
# pdf_page 93-94). REPLACES RP 10 Tables 2-1/2-2/2-3.
#
# CAVEAT: the source table's Evaluation/Retrofit sub-columns for Risk
# Category I-or-II and III interact with footnote 3 (an AHJ-discretionary
# alternate Tier-3-at-BSE-1 evaluation option) in a way that produces
# genuinely multi-line cells in the printed table. Rather than guess at a
# forced single-value Evaluation/Retrofit split that the extracted text
# cannot fully disambiguate, each risk-category column below is stored as
# the LITERAL printed cell text (verbatim, including embedded line breaks)
# for both "evaluation" and "retrofit" -- transcribed, not interpreted.
# Consult the printed table (pp. 72-73) directly for the authoritative
# per-cell reading if resolving footnote 3's exact application matters for
# your project.
# ============================================================================

_TABLE_4_1A_N_LEVEL = {  # occupancy-change / addition-type / relocation triggers
    "rc1_2_evaluation": "CP in BSE-2N (footnote 3)",
    "rc1_2_retrofit": "LS in BSE-1N\nCP in BSE-2N",
    "rc3_evaluation": "LmS in BSE-2N (footnote 3)",
    "rc3_retrofit": "DC in BSE-1N\nLmS in BSE-2N",
    "rc4_evaluation": "IO in BSE-1N\nLS in BSE-2N",
    "rc4_retrofit": "IO in BSE-1N\nLS in BSE-2N",
}

_TABLE_4_1A_E_LEVEL = {  # alteration / repair / acquisition / lease triggers
    "rc1_2_evaluation": "CP in BSE-2E (footnote 3)",
    "rc1_2_retrofit": "LS in BSE-1E\nCP in BSE-2E",
    "rc3_evaluation": "LmS in BSE-2E (footnote 3)",
    "rc3_retrofit": "DC in BSE-1E\nLmS in BSE-2E",
    "rc4_evaluation": "IO in BSE-1E\nLS in BSE-2E",
    "rc4_retrofit": "IO in BSE-1E\nLS in BSE-2E",
}

TABLE_4_1A = {
    "a": {"description": "Change of Occupancy or use", **_TABLE_4_1A_N_LEVEL},
    "b_addition": {"description": "Addition", **_TABLE_4_1A_N_LEVEL},
    "b_alteration": {"description": "Alteration", **_TABLE_4_1A_E_LEVEL},
    "c_addition": {"description": "SDC C, Project Cost > 50% of Replacement Cost for Addition", **_TABLE_4_1A_N_LEVEL},
    "c_alteration_repair": {"description": "SDC C, Project Cost > 50% of Replacement Cost for Alteration and Repair", **_TABLE_4_1A_E_LEVEL},
    "d_addition": {"description": "SDC D-F, Project Cost > 30% of Replacement Cost for Addition", **_TABLE_4_1A_N_LEVEL},
    "d_alteration_repair": {"description": "SDC D-F, Project Cost > 30% of Replacement Cost for Alteration and Repair", **_TABLE_4_1A_E_LEVEL},
    "e": {"description": "Repair of substantial structural damage", **_TABLE_4_1A_E_LEVEL},
    "f": {"description": "Acquisition by purchase or donation", **_TABLE_4_1A_E_LEVEL},
    "g": {"description": "Lease or lease renewal", **_TABLE_4_1A_E_LEVEL},
    "h": {"description": "Relocation", **_TABLE_4_1A_N_LEVEL},
    "i": {
        "description": "Unacceptable risk exposure",
        "rc1_2_evaluation": "CP in BSE-1E", "rc1_2_retrofit": "LS in BSE-1E\nCP in BSE-2E",
        "rc3_evaluation": "CP in BSE-1E", "rc3_retrofit": "DC in BSE-1E\nLmS in BSE-2E",
        "rc4_evaluation": "CP in BSE-1E", "rc4_retrofit": "IO in BSE-1E\nLS in BSE-2E",
    },
    "screening": {"description": "RP 10 Section 1.2.2 Items (Screening Process)", **_TABLE_4_1A_E_LEVEL},
}


def table_4_1a_structural_performance_objective(trigger):
    """Table 4-1(a): structural performance objective for a given RP 10
    evaluation/retrofit trigger, REPLACING RP 10 Tables 2-1/2-2/2-3
    (printed pp. 72-73). See the module docstring caveat on the
    literal-cell-text representation of the Risk Category I/II and III
    columns.

    Parameters
    ----------
    trigger : str
        A key of ``TABLE_4_1A`` (e.g. 'a', 'b_addition', 'i', 'screening').

    Returns
    -------
    dict
        The trigger's row plus {'trigger', 'table': '4-1(a)',
        'printed_page': '72-73', 'pdf_page': '93-94'}.
    """
    key = trigger.lower().strip()
    if key not in TABLE_4_1A:
        raise ValueError(f"trigger must be one of {sorted(TABLE_4_1A)}, got {trigger!r}")
    row = dict(TABLE_4_1A[key])
    row.update({"trigger": key, "table": "4-1(a)", "printed_page": "72-73", "pdf_page": "93-94"})
    return row


# ============================================================================
# Table 4-1(b) -- Nonstructural Performance Objectives (printed pp. 74-75,
# pdf_page 95-96). REPLACES RP 10 Tables 2-1/2-2/2-3. Unlike Table 4-1(a),
# the Evaluation and Retrofit columns are IDENTICAL for every risk category
# in this table (confirmed via structured table extraction) -- each risk
# category gets one two-tier objective {lower_tier, higher_tier} applying
# to both evaluation and retrofit.
# ============================================================================

_TABLE_4_1B_N_LEVEL = {
    "rc1_2": {"lower_tier": "PR in BSE-1N (footnote 4)", "higher_tier": "HR in BSE-2N"},
    "rc3": {"lower_tier": "PR in BSE-1N", "higher_tier": "HR in BSE-2N"},
    "rc4": {"lower_tier": "OP in BSE-1N", "higher_tier": "HR in BSE-2N"},
}

_TABLE_4_1B_E_LEVEL = {
    "rc1_2": {"lower_tier": "LS in BSE-1E", "higher_tier": "HR in BSE-2E"},
    "rc3": {"lower_tier": "PR in BSE-1E", "higher_tier": "HR in BSE-2E"},
    "rc4": {"lower_tier": "PR in BSE-1E", "higher_tier": "HR in BSE-2E"},
}

_TABLE_4_1B_NOT_REQUIRED = {
    "rc1_2": {"lower_tier": "Not required", "higher_tier": "Not required"},
    "rc3": {"lower_tier": "Not required", "higher_tier": "Not required"},
    "rc4": {"lower_tier": "Not required", "higher_tier": "Not required"},
}

TABLE_4_1B = {
    "a": {"description": "Change of Occupancy or Use", **_TABLE_4_1B_N_LEVEL},
    "b_addition": {"description": "Addition", **_TABLE_4_1B_N_LEVEL},
    "b_alteration": {"description": "Alteration", **_TABLE_4_1B_E_LEVEL},
    "c_addition": {"description": "SDC C, Project Cost > 50% of Replacement Cost for Addition", **_TABLE_4_1B_N_LEVEL},
    "c_alteration_repair": {"description": "SDC C, Project Cost > 50% of Replacement Cost for Alteration and Repair", **_TABLE_4_1B_E_LEVEL},
    "d_addition": {"description": "SDC D-F, Project Cost > 30% of Replacement Cost for Addition", **_TABLE_4_1B_N_LEVEL},
    "d_alteration_repair": {"description": "SDC D-F, Project Cost > 30% of Replacement Cost for Alteration and Repair", **_TABLE_4_1B_E_LEVEL},
    "e": {"description": "Repair of substantial structural damage", **_TABLE_4_1B_E_LEVEL},
    "f": {"description": "Acquisition by purchase or donation", **_TABLE_4_1B_E_LEVEL},
    "g": {"description": "Lease or lease renewal", **_TABLE_4_1B_E_LEVEL},
    "h": {"description": "Relocation", **_TABLE_4_1B_N_LEVEL},
    "i": {"description": "Unacceptable risk exposure", **_TABLE_4_1B_NOT_REQUIRED},
    "screening": {"description": "RP 10 Section 1.2.2 Items (Screening Process)", **_TABLE_4_1B_E_LEVEL},
}


def table_4_1b_nonstructural_performance_objective(trigger, risk_category):
    """Table 4-1(b): nonstructural performance objective for a given RP 10
    trigger and risk category, REPLACING RP 10 Tables 2-1/2-2/2-3 (printed
    pp. 74-75). The same two-tier objective applies to both evaluation and
    retrofit.

    Parameters
    ----------
    trigger : str
        A key of ``TABLE_4_1B`` (e.g. 'a', 'b_addition', 'i', 'screening').
    risk_category : str
        'I_II', 'III', or 'IV' (case-insensitive; 'I' and 'II' are grouped
        as in the printed table).

    Returns
    -------
    dict
        {'trigger', 'description', 'risk_category', 'lower_tier',
         'higher_tier', 'table': '4-1(b)', 'printed_page': '74-75',
         'pdf_page': '95-96'}
    """
    key = trigger.lower().strip()
    if key not in TABLE_4_1B:
        raise ValueError(f"trigger must be one of {sorted(TABLE_4_1B)}, got {trigger!r}")
    rc_key_map = {"i_ii": "rc1_2", "i": "rc1_2", "ii": "rc1_2", "iii": "rc3", "iv": "rc4"}
    rc_norm = risk_category.lower().strip().replace(" ", "_").replace("-", "_")
    if rc_norm not in rc_key_map:
        raise ValueError(f"risk_category must be one of I_II/III/IV, got {risk_category!r}")
    tier = TABLE_4_1B[key][rc_key_map[rc_norm]]
    return {
        "trigger": key, "description": TABLE_4_1B[key]["description"],
        "risk_category": risk_category, "lower_tier": tier["lower_tier"],
        "higher_tier": tier["higher_tier"], "table": "4-1(b)",
        "printed_page": "74-75", "pdf_page": "95-96",
    }


# ============================================================================
# Paragraph 4-2.1 -- RP 10 evaluation trigger cost thresholds
# (printed p. 69, pdf_page 90)
# ============================================================================

def evaluation_trigger_cost_threshold(seismic_design_category):
    """RP 10 Section 1.2.1 Items c/d [Replacement]: project-cost threshold
    (as a fraction of pre-construction replacement cost, excluding tenant
    operational equipment/fit-outs/seismic mitigation) that triggers a
    mandatory seismic evaluation for an addition/alteration/repair project
    (printed p. 69).

    Parameters
    ----------
    seismic_design_category : str
        'C' (50% threshold) or 'D', 'E', or 'F' (30% threshold).

    Returns
    -------
    dict
        {'seismic_design_category', 'cost_threshold_fraction', 'paragraph':
         '4-2.1', 'printed_page': '69', 'pdf_page': 90}
    """
    sdc = seismic_design_category.upper().strip()
    if sdc == "C":
        fraction = 0.50
    elif sdc in ("D", "E", "F"):
        fraction = 0.30
    else:
        raise ValueError(f"seismic_design_category must be C/D/E/F, got {seismic_design_category!r}")
    return {
        "seismic_design_category": sdc, "cost_threshold_fraction": fraction,
        "paragraph": "4-2.1", "printed_page": "69", "pdf_page": 90,
    }


# ============================================================================
# Paragraph 4-2.3.1 -- RP 10 evaluation exemption (printed p. 76, pdf_page 97)
# ============================================================================

def rp10_incidental_occupancy_exemption():
    """RP 10 Section 1.3 Item e [Replacement]: the incidental-human-
    occupancy exemption threshold for Risk Category I/II building
    structures (printed p. 76).

    Returns
    -------
    dict
        {'max_persons_per_100_sf', 'max_hours_per_day', 'paragraph':
         '4-2.3.1', 'printed_page': '76', 'pdf_page': 97}
    """
    return {
        "max_persons_per_100_sf": 2, "max_hours_per_day": 2,
        "paragraph": "4-2.3.1", "printed_page": "76", "pdf_page": 97,
    }


# ============================================================================
# Paragraph 503.12 -- IEBC high-wind roof-diaphragm retrofit trigger
# (printed pp. 83-84, pdf_page 104-105)
# ============================================================================

_ROOF_DIAPHRAGM_EXEMPT_BUILDING_TYPES = [
    "reinforced concrete buildings with concrete diaphragms",
    "reinforced concrete masonry unit buildings with concrete diaphragms",
    "detached one- and two-family dwellings",
    "multiple single-family dwellings (townhouses) with fewer than 8 attached units, not more than 3 stories above grade",
    "Risk Category I buildings",
]


def roof_diaphragm_high_wind_retrofit_trigger(basic_wind_speed_mph, cost_fraction=None,
                                                reroofing_fraction=None):
    """IEBC Section 503.12 [Replacement]: determines whether an alteration/
    repair triggers a mandatory roof-diaphragm wind-load evaluation in a
    high-wind region (printed pp. 83-84). High-wind region: basic wind
    speed for RC II structures > 130 mph, or a special wind region per this
    UFC.

    The evaluation is triggered when the building is in a high-wind region
    AND at least one of the following applies: (1) alteration/repair cost
    exceeds 50% of replacement value, or (2) re-roofing an RC III/IV
    building removes more than 50% of the roofing material. If the
    diaphragm/connections cannot resist 75% of current UFC design wind
    loads, they must be replaced/strengthened.

    Parameters
    ----------
    basic_wind_speed_mph : float
        Basic wind speed for a Risk Category II structure at the site (mph).
    cost_fraction : float, optional
        Alteration/repair cost as a fraction of replacement value (0-1).
    reroofing_fraction : float, optional
        Fraction of roofing material removed during re-roofing (0-1), for
        RC III/IV buildings.

    Returns
    -------
    dict
        {'high_wind_region' (bool), 'cost_trigger' (bool or None),
         'reroofing_trigger' (bool or None), 'evaluation_required' (bool),
         'capacity_check_fraction': 0.75, 'exempt_building_types',
         'paragraph': '503.12', 'printed_page': '83-84', 'pdf_page': '104-105'}
    """
    high_wind_region = basic_wind_speed_mph > 130
    cost_trigger = None if cost_fraction is None else cost_fraction > 0.50
    reroofing_trigger = None if reroofing_fraction is None else reroofing_fraction > 0.50
    evaluation_required = high_wind_region and bool(cost_trigger or reroofing_trigger)
    return {
        "high_wind_region": high_wind_region, "cost_trigger": cost_trigger,
        "reroofing_trigger": reroofing_trigger,
        "evaluation_required": evaluation_required, "capacity_check_fraction": 0.75,
        "exempt_building_types": list(_ROOF_DIAPHRAGM_EXEMPT_BUILDING_TYPES),
        "paragraph": "503.12", "printed_page": "83-84", "pdf_page": "104-105",
    }
