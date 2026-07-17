"""UFC 3-250-03 Standard Practice Manual for Flexible Pavements - equations.

This is a construction-practice/QC manual, not a design-equation manual --
almost all of its content is narrative and procedural (see ``tables.py`` for
the genuinely lookup-worthy tables and ``text/`` for the full chapter
narrative). A few places in the source, however, carry real closed-form
formulas worth digitizing:

- Section 2-4.2.3.1 "Proportioning of Stockpile Samples" (pdf_page 39,
  printed p.26) -- the Fuller-Thompson 0.45-power maximum-density gradation
  curve, used to combine/check stockpile and hot-bin aggregate gradations.
- Section 2-4.2.8.1 "Equations Used for Calculation of Mixture Properties"
  (pdf_page 49, printed p.36) -- the standard Marshall/Superpave volumetric
  mixture-property relationships (bulk specific gravity, air voids, voids
  in mineral aggregate, voids filled with asphalt).
- Section 7-3.1 (pdf_page 125-126, printed p.112-113) -- the French
  "estimated optimum asphalt content" procedure used to seed the Resin
  Modified Pavement (RMP) open-graded mixture's Marshall trial asphalt
  contents, plus the same air-voids relationship applied to RMP specimens
  where volume is measured geometrically (pi/4 * D^2 * H) rather than by
  water displacement.
- Appendix B, Section B-1.2 "Surface Area Design Method" (pdf_page 136-138,
  printed p.123-125) -- the slurry-seal/micro-surfacing asphalt-content
  design procedure (surface area -> corrected surface area -> asphalt for
  film thickness -> total asphalt required, Equations B-1/B-2/B-3).

All units follow the source (SI primary, with US customary noted in
docstrings where the source itself gives a parenthetical conversion).

SOURCE-DOCUMENT ERRATA (verified against the printed page images, not just
the text layer, and cross-checked against the source's own worked example in
Section B-1.4.3):

The printed Equation B-1 metric coefficient reads "0.99941" (confirmed by
rendering pdf_page 136 as an image -- not an OCR artifact). Substituting the
source's own worked-example numbers (CSA=8.310 m2/kg, t=8 micrometers,
SGA=1.028) into the metric form with that coefficient gives SAA = 68.3,
but the source's own worked example (Section B-1.4.3, pdf_page 140) states
the answer is SAA = 6.83 -- almost exactly a factor of 10 different. The
parallel US-customary form (coefficient 0.02047) DOES reproduce the source's
stated 6.83 exactly from the equivalent ft2/lb inputs, and 0.02047 * 4.882
(the m2/kg -> ft2/lb conversion factor) = 0.09994, matching a metric
coefficient of ~0.099941, not 0.99941. This module uses the corrected
0.099941 metric coefficient (a missing "0" after the decimal point is the
most plausible explanation for the source's typo); the as-printed value is
recorded here for anyone auditing against the PDF directly.
"""

import math


def fuller_thompson_max_density_passing(sieve_size_mm, max_particle_size_mm,
                                        n=0.45):
    """Fuller-Thompson maximum-density gradation curve, percent passing (Section 2-4.2.3.1).

    ::

        P = 100 * (d / D)^n

    Used to construct (or check aggregate blends against) a theoretical
    maximum-density gradation curve when combining stockpile or hot-bin
    aggregate samples for HMA (or cold-mix, per Section 6-5.1.3.2, which
    references this Chapter 2 procedure).

    Parameters
    ----------
    sieve_size_mm : float
        Sieve opening size, d (mm). Must be > 0 and <= max_particle_size_mm.
    max_particle_size_mm : float
        Maximum aggregate particle size, D (mm). Must be > 0.
    n : float, optional
        Gradation exponent (default 0.45, the standard Fuller-Thompson
        maximum-density value).

    Returns
    -------
    dict
        {'sieve_size_mm', 'max_particle_size_mm', 'n', 'percent_passing',
         'reference'}.

    Raises
    ------
    ValueError
        If sieve_size_mm or max_particle_size_mm <= 0, or sieve_size_mm >
        max_particle_size_mm.
    """
    if sieve_size_mm <= 0:
        raise ValueError(f"sieve_size_mm must be > 0, got {sieve_size_mm}")
    if max_particle_size_mm <= 0:
        raise ValueError(
            f"max_particle_size_mm must be > 0, got {max_particle_size_mm}"
        )
    if sieve_size_mm > max_particle_size_mm:
        raise ValueError(
            f"sieve_size_mm ({sieve_size_mm}) must be <= max_particle_size_mm "
            f"({max_particle_size_mm})"
        )
    p = 100.0 * (sieve_size_mm / max_particle_size_mm) ** n
    return {
        "sieve_size_mm": sieve_size_mm,
        "max_particle_size_mm": max_particle_size_mm,
        "n": n,
        "percent_passing": round(p, 2),
        "reference": "UFC 3-250-03, Section 2-4.2.3.1 (pdf_page 39, printed p.26)",
    }


def bulk_specific_gravity_gmb(wt_dry_air, wt_ssd, wt_submerged):
    """Bulk specific gravity of a compacted mixture, Gmb (Section 2-4.2.8.1).

    ::

        Gmb = Wdry / (Wssd - Wsubmerged)

    Parameters
    ----------
    wt_dry_air : float
        Dry weight of the specimen in air (g), Wdry.
    wt_ssd : float
        Saturated-surface-dry weight of the specimen (g), Wssd.
    wt_submerged : float
        Weight of the specimen submerged in water (g), Wsubmerged.

    Returns
    -------
    dict
        {'gmb', 'reference'}.

    Raises
    ------
    ValueError
        If wt_ssd <= wt_submerged (non-physical displaced volume).
    """
    if wt_ssd <= wt_submerged:
        raise ValueError(
            f"wt_ssd ({wt_ssd}) must be > wt_submerged ({wt_submerged})"
        )
    gmb = wt_dry_air / (wt_ssd - wt_submerged)
    return {
        "gmb": round(gmb, 4),
        "reference": "UFC 3-250-03, Section 2-4.2.8.1 (pdf_page 49, printed p.36)",
    }


def bulk_specific_gravity_gmb_geometric(wt_dry_air, diameter, height):
    """Bulk specific gravity from measured specimen geometry (Section 7-3.1, RMP).

    Used for Resin Modified Pavement (RMP) open-graded asphalt mixture
    Marshall specimens, where volume is measured geometrically rather than
    by water displacement (appropriate for open, free-draining specimens).

    ::

        Volume = (pi / 4) * D^2 * H
        Gmb = Wdry / Volume

    Parameters
    ----------
    wt_dry_air : float
        Dry weight of the specimen in air (g), WTair.
    diameter : float
        Specimen diameter, D (cm).
    height : float
        Specimen height, H (cm).

    Returns
    -------
    dict
        {'gmb', 'volume_cc', 'reference'}.

    Raises
    ------
    ValueError
        If diameter or height <= 0.
    """
    if diameter <= 0:
        raise ValueError(f"diameter must be > 0, got {diameter}")
    if height <= 0:
        raise ValueError(f"height must be > 0, got {height}")
    volume = (math.pi / 4.0) * diameter ** 2 * height
    gmb = wt_dry_air / volume
    return {
        "gmb": round(gmb, 4),
        "volume_cc": round(volume, 2),
        "reference": "UFC 3-250-03, Section 7-3.1 (pdf_page 126, printed p.113)",
    }


def air_voids_vtm(gmb, gmm):
    """Air voids in total mix, Vv / VTM, percent (Section 2-4.2.8.1).

    ::

        Vv = 100 * (1 - Gmb / Gmm)

    Parameters
    ----------
    gmb : float
        Bulk specific gravity of the compacted mixture.
    gmm : float
        Theoretical maximum specific gravity of the mixture (ASTM D2041).
        Must be > 0.

    Returns
    -------
    dict
        {'vv_percent', 'reference'}.

    Raises
    ------
    ValueError
        If gmm <= 0.
    """
    if gmm <= 0:
        raise ValueError(f"gmm must be > 0, got {gmm}")
    vv = 100.0 * (1.0 - gmb / gmm)
    return {
        "vv_percent": round(vv, 2),
        "reference": "UFC 3-250-03, Section 2-4.2.8.1 (pdf_page 49, printed p.36)",
    }


def voids_in_mineral_aggregate_vma(gmb, gsb, pb):
    """Voids in mineral aggregate, VMA, percent of total mixture volume (Section 2-4.2.8.1).

    ::

        VMA = 100 - (Gmb * (1 - Pb) / Gsb) * 100

    Parameters
    ----------
    gmb : float
        Bulk specific gravity of the compacted mixture.
    gsb : float
        Bulk specific gravity of the aggregate (ASTM C127/C128). Must be > 0.
    pb : float
        Asphalt content, decimal fraction of total mixture weight (e.g.
        0.05 for 5.0 percent). Must be in [0, 1).

    Returns
    -------
    dict
        {'vma_percent', 'reference'}.

    Raises
    ------
    ValueError
        If gsb <= 0 or pb not in [0, 1).
    """
    if gsb <= 0:
        raise ValueError(f"gsb must be > 0, got {gsb}")
    if not (0 <= pb < 1):
        raise ValueError(f"pb must be a decimal fraction in [0, 1), got {pb}")
    vma = 100.0 - (gmb * (1.0 - pb) / gsb) * 100.0
    return {
        "vma_percent": round(vma, 2),
        "reference": "UFC 3-250-03, Section 2-4.2.8.1 (pdf_page 49, printed p.36)",
    }


def voids_filled_with_asphalt_vfa(vma_percent, vv_percent):
    """Voids filled with asphalt, VFA, percent of VMA (Section 2-4.2.8.1).

    ::

        VFA = 100 * (VMA - Vv) / VMA

    Parameters
    ----------
    vma_percent : float
        Voids in mineral aggregate, percent (see
        ``voids_in_mineral_aggregate_vma``). Must be > 0.
    vv_percent : float
        Air voids in total mix, percent (see ``air_voids_vtm``).

    Returns
    -------
    dict
        {'vfa_percent', 'reference'}.

    Raises
    ------
    ValueError
        If vma_percent <= 0.
    """
    if vma_percent <= 0:
        raise ValueError(f"vma_percent must be > 0, got {vma_percent}")
    vfa = 100.0 * (vma_percent - vv_percent) / vma_percent
    return {
        "vfa_percent": round(vfa, 2),
        "reference": "UFC 3-250-03, Section 2-4.2.8.1 (pdf_page 49, printed p.36)",
    }


def rmp_specific_surface_area(pct_retained_no4, pct_passing_no4_retained_no30,
                              pct_passing_no30_retained_no200,
                              pct_passing_no200):
    """RMP open-graded mixture conventional specific surface area, Sigma (Section 7-3.1).

    French-method input to ``rmp_optimum_asphalt_content``.

    ::

        Sigma = 0.21*G + 5.4*S + 7.2*s + 135*f

    Parameters
    ----------
    pct_retained_no4 : float
        G: percentage of material retained on the 4.75 mm (No. 4) sieve.
    pct_passing_no4_retained_no30 : float
        S: percentage of material passing the 4.75 mm (No. 4) sieve and
        retained on the 600 um (No. 30) sieve.
    pct_passing_no30_retained_no200 : float
        s: percentage of material passing the 600 um (No. 30) sieve and
        retained on the 75 um (No. 200) sieve.
    pct_passing_no200 : float
        f: percentage of material passing the 75 um (No. 200) sieve.

    Returns
    -------
    dict
        {'sigma', 'reference'}.
    """
    sigma = (0.21 * pct_retained_no4 + 5.4 * pct_passing_no4_retained_no30
             + 7.2 * pct_passing_no30_retained_no200 + 135.0 * pct_passing_no200)
    return {
        "sigma": round(sigma, 3),
        "reference": "UFC 3-250-03, Section 7-3.1 (pdf_page 125, printed p.112)",
    }


def rmp_optimum_asphalt_content(sigma, apparent_sg_combined_aggregate):
    """RMP open-graded mixture estimated optimum asphalt content (Section 7-3.1, French method).

    Seeds the trial asphalt contents (typically the estimate +/- two 0.2-0.4
    percent increments) used for the Marshall specimen evaluation of the RMP
    open-graded asphalt mixture. Verified directly against the printed page
    (pdf_page 125): a worked example of 4.2 percent optimum content leading
    to trial contents 3.8/4.0/4.2/4.4/4.6 percent is given immediately after
    this formula in the source.

    ::

        alpha = 2.65 / SG
        Optimum asphalt content (percent) = 3.25 * alpha * Sigma^0.2

    Parameters
    ----------
    sigma : float
        Conventional specific surface area (see ``rmp_specific_surface_area``).
        Must be > 0.
    apparent_sg_combined_aggregate : float
        SG: apparent specific gravity of the combined aggregates. Must be > 0.

    Returns
    -------
    dict
        {'alpha', 'sigma', 'optimum_asphalt_content_pct', 'reference'}.

    Raises
    ------
    ValueError
        If sigma <= 0 or apparent_sg_combined_aggregate <= 0.
    """
    if sigma <= 0:
        raise ValueError(f"sigma must be > 0, got {sigma}")
    if apparent_sg_combined_aggregate <= 0:
        raise ValueError(
            f"apparent_sg_combined_aggregate must be > 0, got "
            f"{apparent_sg_combined_aggregate}"
        )
    alpha = 2.65 / apparent_sg_combined_aggregate
    oac = 3.25 * alpha * sigma ** 0.2
    return {
        "alpha": round(alpha, 4),
        "sigma": sigma,
        "optimum_asphalt_content_pct": round(oac, 2),
        "reference": "UFC 3-250-03, Section 7-3.1 (pdf_page 125, printed p.112)",
    }


def slurry_seal_surface_area(pct_passing_by_sieve_mm):
    """Total surface area of slurry-seal job aggregate, SA (Appendix B-1.2.1).

    Sums percent-passing (as a fraction of 100) times the Table B-1 surface
    area factor for each sieve. Verified end-to-end against the source's own
    worked example (Section B-1.4.3, Table B-2): this function, chained with
    ``slurry_seal_corrected_surface_area`` and
    ``slurry_seal_asphalt_for_film_thickness`` (corrected coefficient) and
    ``slurry_seal_total_asphalt_required``, reproduces the source's stated
    AR = 12.53 percent from its stated inputs.

    Parameters
    ----------
    pct_passing_by_sieve_mm : dict
        Mapping of sieve size (mm, matching
        ``tables.table_b1_surface_area_factor`` keys: 9.5, 4.75, 2.36,
        1.18, 0.60, 0.30, 0.15, 0.075) to percent passing that sieve
        (0-100).

    Returns
    -------
    dict
        {'surface_area_m2_per_kg', 'reference'}.

    Raises
    ------
    ValueError
        If pct_passing_by_sieve_mm is empty or contains an untabulated
        sieve size.
    """
    from .tables import table_b1_surface_area_factor

    if not pct_passing_by_sieve_mm:
        raise ValueError("pct_passing_by_sieve_mm must not be empty")
    sa = 0.0
    for sieve_mm, pct_passing in pct_passing_by_sieve_mm.items():
        factor = table_b1_surface_area_factor(sieve_mm)["factor_m2_per_kg"]
        sa += (pct_passing / 100.0) * factor
    return {
        "surface_area_m2_per_kg": round(sa, 3),
        "reference": "UFC 3-250-03, Section B-1.2.1 (pdf_page 137, printed p.124)",
    }


def slurry_seal_corrected_surface_area(surface_area_m2_per_kg,
                                       apparent_sg_aggregate):
    """Corrected surface area of slurry-seal aggregate, CSA (Appendix B-1.2.1).

    ::

        CSA = SA * 2.65 / ASG

    Parameters
    ----------
    surface_area_m2_per_kg : float
        SA, total surface area (see ``slurry_seal_surface_area``), m^2/kg.
    apparent_sg_aggregate : float
        ASG: apparent specific gravity of the aggregate. Must be > 0.

    Returns
    -------
    dict
        {'csa_m2_per_kg', 'reference'}.

    Raises
    ------
    ValueError
        If apparent_sg_aggregate <= 0.
    """
    if apparent_sg_aggregate <= 0:
        raise ValueError(
            f"apparent_sg_aggregate must be > 0, got {apparent_sg_aggregate}"
        )
    csa = surface_area_m2_per_kg * 2.65 / apparent_sg_aggregate
    return {
        "csa_m2_per_kg": round(csa, 3),
        "reference": "UFC 3-250-03, Section B-1.2.1 (pdf_page 137, printed p.124)",
    }


def slurry_seal_asphalt_for_film_thickness(csa_m2_per_kg, film_thickness_um,
                                           sg_asphalt):
    """Asphalt content to coat aggregate to a target film thickness, SAA (Equation B-1).

    Metric form (SI units: CSA in m^2/kg, film thickness in micrometers).

    ::

        SAA = CSA * t * 0.099941 * SGa

    NOTE: the source PDF prints this metric coefficient as "0.99941" (pdf_page
    136), but that value does not reproduce the source's own worked example
    (Section B-1.4.3: CSA=8.310, t=8, SGA=1.028 -> stated SAA=6.83). The
    corrected coefficient 0.099941 (verified against both the worked example
    and the internally-consistent US-customary form, coefficient 0.02047)
    is used here -- see the module docstring for the full derivation. This is
    flagged as a probable decimal-point typo in the source, not an extraction
    error.

    Parameters
    ----------
    csa_m2_per_kg : float
        CSA, corrected surface area (see
        ``slurry_seal_corrected_surface_area``), m^2/kg.
    film_thickness_um : float
        t: desired asphalt film thickness, micrometers (source design
        default: 8 micrometers / 3.15e-4 in.).
    sg_asphalt : float
        SGa: specific gravity of the asphalt. If unknown, the source
        permits assuming SGa = 1.0 without materially affecting the
        design (per Appendix B-1.2.1).

    Returns
    -------
    dict
        {'saa_pct', 'reference', 'note'}. SAA is percent of dry aggregate
        weight.
    """
    saa = csa_m2_per_kg * film_thickness_um * 0.099941 * sg_asphalt
    return {
        "saa_pct": round(saa, 3),
        "reference": "UFC 3-250-03, Equation B-1 (pdf_page 136, printed p.123)",
        "note": ("Uses corrected coefficient 0.099941; the source PDF prints "
                "0.99941, which does not reproduce its own worked example -- "
                "see module docstring."),
    }


def slurry_seal_total_asphalt_required(saa_pct, ka_pct):
    """Total asphalt required for a slurry seal mixture, AR (Equations B-2/B-3).

    ::

        AR = SAA + KA

    Parameters
    ----------
    saa_pct : float
        SAA: asphalt content to coat the aggregate surface area to the
        target film thickness, percent of dry aggregate weight (see
        ``slurry_seal_asphalt_for_film_thickness``).
    ka_pct : float
        KA: kerosene absorbed by the aggregate in the centrifuge kerosene
        equivalent (CKE) test (ASTM D5148 sand-absorption cone per ASTM
        C128), percent of dry aggregate weight -- taken as the asphalt
        absorption requirement.

    Returns
    -------
    dict
        {'ar_pct', 'reference'}. AR is percent of dry aggregate weight; the
        required percent emulsion = AR * 100 / (percent asphalt residue in
        the emulsion).
    """
    ar = saa_pct + ka_pct
    return {
        "ar_pct": round(ar, 3),
        "reference": "UFC 3-250-03, Equations B-2/B-3 (pdf_page 138, printed p.125)",
    }
