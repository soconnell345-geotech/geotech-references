"""UFC 3-220-04FA backfill equations.

From UFC 3-220-04FA, Backfill for Subsurface Structures, 16 January 2004
(the reproduced TM 5-818-4/AFM 88-5, Chap. 5). The manual states density
requirements as a percent of CE 55 maximum dry density (paragraph 5-1b(4),
printed p. 5-2, pdf_page_index 28).

Rebuilt 2026-11-10 (review pave-14): the Broms (1971) compaction-pressure
equation and the filter ratios that were here are not printed in this
manual (it gives compaction-induced pressure only as Figure 2-5, now
``tables.figure_2_5_compaction_induced_lateral_pressure``, and sends
filter design to TM 5-818-5, paragraph 2-3c, printed p. 2-6).
"""

from geotech_references import _units as _u


@_u.labelled(
    {"deficit_pct": "percent", "relative_compaction_pct": "percent",
     "required_pct": "percent"})
def relative_compaction_check(
    dry_density_kN_per_m3,
    max_dry_density_kN_per_m3,
    required_pct=95.0,
):
    """Degree of compaction, percent = field dry density / maximum dry
    density x 100, checked against a required percent; UFC 3-220-04FA states
    its density requirements as a percent of CE 55 maximum dry density by
    MIL-STD-621 (paragraph 5-1b(4), printed p. 5-2, pdf_page_index 28).

    Paragraph 5-1b(4) as printed: 90 percent in open areas where structures
    will not be constructed; 95 to 100 percent for cohesionless soils and
    at least 95 percent for cohesive soils beneath structures; 95 to 100
    percent for drainage blankets and filters
    (``tables.table_compaction_requirements``). The default 95 is the
    beneath-structures minimum; pass 90 for open areas.

    Parameters
    ----------
    dry_density_kN_per_m3 : float
        Field dry unit weight (any unit, the same as the maximum).
    max_dry_density_kN_per_m3 : float
        Maximum dry unit weight of the compaction test the specification
        names (the manual: CE 55 by MIL-STD-621).
    required_pct : float, optional
        Minimum required degree of compaction (%, default 95).

    Returns
    -------
    dict
        Keys: relative_compaction_pct, required_pct, passes (bool),
        deficit_pct (0 if passes, else shortfall), basis, reference.

    Raises
    ------
    ValueError
        If any input is non-positive or required_pct not in (0, 100].
    """
    if dry_density_kN_per_m3 <= 0:
        raise ValueError(
            f"dry_density_kN_per_m3 must be > 0, got {dry_density_kN_per_m3}"
        )
    if max_dry_density_kN_per_m3 <= 0:
        raise ValueError(
            f"max_dry_density_kN_per_m3 must be > 0, got {max_dry_density_kN_per_m3}"
        )
    if not (0 < required_pct <= 100):
        raise ValueError(f"required_pct must be in (0, 100], got {required_pct}")

    rc = (dry_density_kN_per_m3 / max_dry_density_kN_per_m3) * 100.0
    passes = rc >= required_pct
    deficit = 0.0 if passes else required_pct - rc

    return {
        "relative_compaction_pct": round(rc, 1),
        "required_pct": required_pct,
        "passes": passes,
        "deficit_pct": round(deficit, 1),
        "basis": ("percent of maximum dry density; UFC 3-220-04FA's "
                  "requirements are percents of CE 55 maximum dry density "
                  "(MIL-STD-621): 90 open areas, 95-100 cohesionless and "
                  ">= 95 cohesive beneath structures, 95-100 drainage "
                  "blankets and filters"),
        "reference": ("UFC 3-220-04FA (TM 5-818-4/AFM 88-5, Chap. 5), "
                      "16 January 2004, para 5-1b(4), printed p. 5-2 (pdf_page_index 28)"),
    }
