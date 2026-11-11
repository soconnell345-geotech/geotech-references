"""EM 1110-1-1905 (2025) tables as lookups: the minimum factors of safety
(Table 2-1), the bearing capacity and correction factors of Tables 5-2 to 5-4
by both methods the manual prints (USACE, Meyerhof based; AASHTO (2020)/FHWA
(2002), Vesic based), the in situ bearing capacity factor k (Table 5-5) and
Menard's rheological factor (Table 7-6).

Every value and formula is as printed, each table compared cell by cell with
the rendered page. Units are the manual's (ft, kips, ksf, kcf, tsf, degrees).
Each function returns a dict with its values, ``units``, ``source`` (table and
printed page), ``valid_for`` and ``notes``, and raises ValueError for a value
outside what the table covers or a category it does not print; nothing is
clamped and nothing is assumed.
"""

from __future__ import annotations

import math

_REF = "EM 1110-1-1905 (2025)"

#: the two methods of Tables 5-2 to 5-4; "fhwa" names the second, as the
#: worked examples of Appendix B head its column
_METHODS = {"usace": "usace", "aashto": "aashto", "fhwa": "aashto"}

_METHOD_NAMES = {
    "usace": "USACE (Meyerhof based; Instructional Report K-82-7)",
    "aashto": "AASHTO (2020)/FHWA (2002) (Vesic based)",
}


def _source(obj: str, page) -> str:
    return f"{_REF} {obj}, p. {page}"


def _method(method: str) -> str:
    key = str(method).lower().strip()
    if key not in _METHODS:
        raise ValueError(
            f"Unknown method {method!r}: give 'usace' (Meyerhof based) or "
            f"'aashto' (AASHTO (2020)/FHWA (2002), Vesic based; 'fhwa' is "
            f"taken as the same), the two columns of Tables 5-2 to 5-4")
    return _METHODS[key]


def _positive(name: str, value) -> float:
    v = float(value)
    if not v > 0:
        raise ValueError(f"{name} must be > 0 (got {value})")
    return v


def _non_negative(name: str, value) -> float:
    v = float(value)
    if v < 0:
        raise ValueError(f"{name} must be >= 0 (got {value})")
    return v


def _ratio_b_over_l(B_eff, L_eff) -> float:
    """B'/L': 0 for a continuous footing (L_eff None), as the shape factors
    are 1 for a continuous footing (p. 106)."""
    B = _positive("B_eff", B_eff)
    if L_eff is None:
        return 0.0
    L = _positive("L_eff", L_eff)
    if L < B:
        raise ValueError(
            f"L_eff ({L_eff}) is less than B_eff ({B_eff}): B' is the "
            f"effective width and L' the effective length (p. 106)")
    return B / L


def _friction_angle(phi_deg) -> float:
    phi = float(phi_deg)
    if not 0 < phi < 90:
        raise ValueError(
            f"phi_deg = {phi_deg}: the drained factors of Tables 5-2 and 5-3 "
            f"need 0 < phi' < 90 degrees; for phi' = 0 use Table 5-4")
    return phi


# ---------------------------------------------------------------------------
# Table 2-1
# ---------------------------------------------------------------------------

_TABLE_2_1 = {
    "bearing capacity": (3.0, (
        "Note 1: Increases in allowable stress (for wind or seismic) must "
        "comply with the stipulated building code and UFC requirements "
        "(paragraph 2-8). Increases are not permitted where bearing soils "
        "are susceptible to shear strength loss (SSL), reference paragraph "
        "9-10a. If a FS < 3.0 is used for design, additional settlement "
        "could occur due to partial yielding or plastic flow.")),
    "sliding": (2.0, (
        "Note 2: Sliding (and passive resistance) are evaluated per "
        "paragraph 5-6. Factor of safety may be reduced to 1.1 for load "
        "combinations that include earthquake loads.")),
    "overturning moment and eccentricity": (None, (
        "Note 3: For overturning stability, the factor of safety concept "
        "does not strictly apply when the resultant moves beyond the third "
        "point; eccentricity governs and is required to be within the "
        "inside middle-third of the footing.")),
    "uplift": (1.5, ""),
}

_TABLE_2_1_ALIASES = {"bearing": "bearing capacity",
                      "overturning": "overturning moment and eccentricity",
                      "eccentricity": "overturning moment and eccentricity"}


def table_2_1_minimum_factor_of_safety(failure_mode: str) -> dict:
    """Minimum factor of safety a shallow foundation must meet for an
    ultimate limit state: 3.0 for bearing capacity, 2.0 for sliding (1.1
    allowed for load combinations with earthquake loads), 1.5 for uplift;
    overturning is governed by eccentricity, which must stay within the
    middle third of the footing, not by a factor of safety.

    Print check (Table 2-1, p. 10, rendered and compared cell by cell):

        ULS failure mode                       printed    here
        Bearing capacity                       3.0 (1)    3.0, note 1
        Sliding                                2.0 (2)    2.0, note 2
        Overturning moment and eccentricity    Note 3     None, note 3
        Uplift                                 1.5        1.5

    Parameters
    ----------
    failure_mode : str
        'bearing capacity', 'sliding', 'overturning moment and
        eccentricity' ('overturning' or 'eccentricity' for short) or
        'uplift'.

    Returns
    -------
    dict
        failure_mode, fs_min (None for overturning), note (the table's note
        for the row, word for word), units, source, valid_for, notes.

    Raises
    ------
    ValueError
        For a failure mode Table 2-1 does not list.
    """
    key = " ".join(str(failure_mode).lower().split())
    key = _TABLE_2_1_ALIASES.get(key, key)
    if key not in _TABLE_2_1:
        raise ValueError(f"Unknown failure mode {failure_mode!r}. Table 2-1 "
                         f"lists: {', '.join(_TABLE_2_1)}")
    fs, note = _TABLE_2_1[key]
    return {
        "failure_mode": key,
        "fs_min": fs,
        "note": note,
        "units": {"fs_min": "dimensionless"},
        "source": _source("Table 2-1", 10),
        "valid_for": ("Ultimate limit states of shallow foundations; "
                      "structures governed by EM 1110-2-2100 and "
                      "EM 1110-2-2502 are excepted (paragraph 2-6b(1))."),
        "notes": "",
    }


# ---------------------------------------------------------------------------
# Table 5-2
# ---------------------------------------------------------------------------

def table_5_2_bearing_capacity_factors(phi_deg: float, method: str) -> dict:
    """Drained bearing capacity factors Nq, Nc and N-gamma for a continuous
    footing, from the flow number N = tan^2(45 + phi'/2). Nq and Nc are the
    same by both methods; N-gamma differs: (Nq - 1) tan(1.4 phi') by the
    USACE (Meyerhof) method and 2(Nq + 1) tan(phi') by the AASHTO/FHWA
    (Vesic) method. The manual recommends computing both and averaging when
    bearing capacity controls (paragraph 5-5e).

    Print check (Table 5-2, p. 107, rendered and compared cell by cell):

        factor  USACE as printed               AASHTO/FHWA as printed
        N       tan^2(45° + φ′/2)              same
                = (1 + sinφ′)/(1 − sinφ′)
        Nq      N · e^(π·tanφ′)                same
        Nc      (Nq − 1) · cotφ′               same
        Nγ      (Nq − 1) · tan(1.4φ′)          2(Nq + 1) · tan(φ′)

    Parameters
    ----------
    phi_deg : float
        Effective stress friction angle phi' of the soil in the shear zone,
        degrees.
    method : str
        'usace' or 'aashto' ('fhwa' is taken as the same).

    Returns
    -------
    dict
        N, Nq, Nc, N_gamma, method, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If phi' is not between 0 and 90 degrees, if 1.4 phi' reaches 90
        degrees for the USACE N-gamma (its tangent is undefined there), or
        for an unknown method.
    """
    m = _method(method)
    phi = _friction_angle(phi_deg)
    if m == "usace" and 1.4 * phi >= 90:
        raise ValueError(
            f"phi_deg = {phi_deg}: the USACE N-gamma, (Nq - 1) tan(1.4 phi'), "
            f"is undefined for 1.4 phi' >= 90 degrees")
    r = math.radians(phi)
    N = math.tan(math.radians(45 + phi / 2)) ** 2
    Nq = N * math.exp(math.pi * math.tan(r))
    Nc = (Nq - 1) / math.tan(r)
    if m == "usace":
        Ng = (Nq - 1) * math.tan(math.radians(1.4 * phi))
    else:
        Ng = 2 * (Nq + 1) * math.tan(r)
    return {
        "N": N, "Nq": Nq, "Nc": Nc, "N_gamma": Ng,
        "method": _METHOD_NAMES[m],
        "units": {k: "dimensionless" for k in ("N", "Nq", "Nc", "N_gamma")},
        "source": _source("Table 5-2", 107),
        "valid_for": ("Drained (effective stress) analysis with phi' > 0; "
                      "for phi' = 0 use Table 5-4 (Nc = 5.14)."),
        "notes": "N is the flow number, the principal stress ratio (p. 106).",
    }


def table_5_2_usace_shape_depth_factors(flow_number: float, B_eff: float,
                                        L_eff: float | None,
                                        Df: float) -> dict:
    """USACE (Meyerhof based) shape and depth correction factors for drained
    bearing capacity, from the flow number N: sq = s-gamma = 1 + 0.1 N B'/L',
    sc = 1 + 0.2 N B'/L', dq = d-gamma = 1 + 0.1 sqrt(N) Df/B',
    dc = 1 + 0.2 sqrt(N) Df/B'. The in situ test methods (equations 5-25 and
    5-26) use these factors with N = 3 where no friction angle is estimated
    (p. 115).

    Print check (Table 5-2, p. 107, rendered and compared cell by cell):

        factor  USACE as printed
        sq      1 + 0.1N (B′/L′)
        sc      1 + 0.2N (B′/L′)
        sγ      1 + 0.1N (B′/L′)
        dq      1 + 0.1√N (Df/B′)
        dc      1 + 0.2√N (Df/B′)
        dγ      1 + 0.1√N (Df/B′)

    Parameters
    ----------
    flow_number : float
        N = tan^2(45 + phi'/2) (``table_5_2_bearing_capacity_factors``), or
        3 for the in situ test methods without a friction angle (p. 115).
    B_eff : float
        Effective width B', ft.
    L_eff : float or None
        Effective length L', ft; None for a continuous footing, whose shape
        factors are 1 (p. 106).
    Df : float
        Depth of the footing base below the ground surface, ft.

    Returns
    -------
    dict
        sq, sc, s_gamma, dq, dc, d_gamma, B_over_L, Df_over_B, units,
        source, valid_for, notes.

    Raises
    ------
    ValueError
        If N < 1, B' or L' is not positive, L' < B', or Df < 0.
    """
    N = float(flow_number)
    if N < 1:
        raise ValueError(f"flow_number = {flow_number}: N = tan^2(45 + "
                         f"phi'/2) is at least 1")
    bl = _ratio_b_over_l(B_eff, L_eff)
    dfb = _non_negative("Df", Df) / float(B_eff)
    return {
        "sq": 1 + 0.1 * N * bl, "sc": 1 + 0.2 * N * bl,
        "s_gamma": 1 + 0.1 * N * bl,
        "dq": 1 + 0.1 * math.sqrt(N) * dfb, "dc": 1 + 0.2 * math.sqrt(N) * dfb,
        "d_gamma": 1 + 0.1 * math.sqrt(N) * dfb,
        "B_over_L": bl, "Df_over_B": dfb,
        "units": {k: "dimensionless" for k in
                  ("sq", "sc", "s_gamma", "dq", "dc", "d_gamma")},
        "source": _source("Table 5-2", 107),
        "valid_for": "Drained analysis, USACE (Meyerhof based) method.",
        "notes": ("Shape factors are 1 for a continuous footing (p. 106); "
                  "the in situ methods use N = 3 where no friction angle is "
                  "estimated (p. 115)."),
    }


def table_5_2_aashto_shape_depth_factors(phi_deg: float, B_eff: float,
                                         L_eff: float | None,
                                         Df: float) -> dict:
    """AASHTO (2020)/FHWA (2002) (Vesic based) shape and depth correction
    factors for drained bearing capacity: sq = 1 + (B'/L') tan(phi),
    sc = 1 + (B'/L')(Nq/Nc), s-gamma = 1 - 0.4 (B'/L'),
    dq = 1 + 2 tan(phi') (1 - sin(phi'))^2 atan(Df/B') with atan in radians,
    dc = d-gamma = 1. The note to the table limits dq to 1.4 for AASHTO
    (2020), and the limit is applied as printed: where the formula gives
    more, dq = 1.4 is returned, with the formula's value in dq_unlimited
    and limit_governs True.

    Print check (Table 5-2, p. 107, rendered and compared cell by cell):

        factor  AASHTO/FHWA as printed
        sq      1 + ((B′/L′) tanφ)            (φ without a prime, as printed)
        sc      "sq = 1 + (B′/L′)(Nq/Nc)"     (the cell names it sq: sc meant)
        sγ      1 − 0.4 (B′/L′)
        dq      1 + 2tanφ′ (1 − sinφ′)^2 atan(Df/B′)
        dc      1
        dγ      1
        note a  dq for AASHTO (2020) ≤ 1.4, atan(D/B′) in radians,
                FHWA (2002) presents tabulated values
        here    the same; above 1.4, dq = 1.4 (note a), the formula's value
                in dq_unlimited

    Parameters
    ----------
    phi_deg : float
        Friction angle of the soil in the shear zone, degrees.
    B_eff : float
        Effective width B', ft.
    L_eff : float or None
        Effective length L', ft; None for a continuous footing (shape
        factors 1, p. 106).
    Df : float
        Depth of the footing base below the ground surface, ft.

    Returns
    -------
    dict
        sq, sc, s_gamma, dq, dq_unlimited, limit_governs, dc, d_gamma, Nq,
        Nc, B_over_L, Df_over_B, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If phi' is not between 0 and 90 degrees, B' or L' is not positive,
        L' < B', or Df < 0.
    """
    phi = _friction_angle(phi_deg)
    bl = _ratio_b_over_l(B_eff, L_eff)
    dfb = _non_negative("Df", Df) / float(B_eff)
    f = table_5_2_bearing_capacity_factors(phi, "aashto")
    r = math.radians(phi)
    dq_formula = 1 + 2 * math.tan(r) * (1 - math.sin(r)) ** 2 * math.atan(dfb)
    governs = dq_formula > 1.4
    notes = ("As printed, the sc cell reads 'sq = 1 + (B'/L')(Nq/Nc)' and "
             "the sq cell uses tan(phi) without a prime; FHWA (2002) presents "
             "tabulated depth factors (note a).")
    if governs:
        notes += (f" The formula gives dq = {dq_formula:.3f}; note a to Table "
                  f"5-2 (p. 107) reads 'dq for AASHTO (2020) <= 1.4', so dq "
                  f"= 1.4 is returned (dq_unlimited holds the formula's value).")
    return {
        "sq": 1 + bl * math.tan(r), "sc": 1 + bl * (f["Nq"] / f["Nc"]),
        "s_gamma": 1 - 0.4 * bl, "dq": min(dq_formula, 1.4),
        "dq_unlimited": dq_formula, "limit_governs": governs,
        "dc": 1.0, "d_gamma": 1.0,
        "Nq": f["Nq"], "Nc": f["Nc"], "B_over_L": bl, "Df_over_B": dfb,
        "units": {k: "dimensionless" for k in
                  ("sq", "sc", "s_gamma", "dq", "dq_unlimited", "dc",
                   "d_gamma")},
        "source": _source("Table 5-2", 107),
        "valid_for": ("Drained analysis, AASHTO (2020)/FHWA (2002) (Vesic "
                      "based) method; dq <= 1.4 (note a)."),
        "notes": notes,
    }


# ---------------------------------------------------------------------------
# Table 5-3
# ---------------------------------------------------------------------------

def table_5_3_usace_load_inclination_factors(H: float, V: float,
                                             phi_deg: float) -> dict:
    """USACE (Meyerhof based) load inclination factors for drained bearing
    capacity: beta = atan(H/V), iq = ic = (1 - beta/90)^2,
    i-gamma = (1 - beta/phi')^2, beta and phi' in degrees.

    Print check (Table 5-3, p. 108, rendered and compared cell by cell):

        factor  USACE as printed
        β       atan(H/V)
        n       Not Applicable
        iq      [1 − β/(90°)]^2
        ic      ic = iq
        iγ      [1 − β/φ′]^2

    Parameters
    ----------
    H : float
        Horizontal component of the applied load, kips (kips/ft for a
        continuous footing).
    V : float
        Vertical load on the ground, same units as H.
    phi_deg : float
        Friction angle phi', degrees.

    Returns
    -------
    dict
        beta_deg, iq, ic, i_gamma, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If H < 0, V <= 0, phi' is not between 0 and 90 degrees, or beta
        exceeds phi' (the bracket of i-gamma turns negative; the table gives
        no value there).
    """
    _non_negative("H", H)
    _positive("V", V)
    phi = _friction_angle(phi_deg)
    beta = math.degrees(math.atan(float(H) / float(V)))
    if beta > phi:
        raise ValueError(
            f"beta = {beta:.2f} degrees exceeds phi' = {phi_deg}: Table 5-3 "
            f"(p. 108) gives i-gamma = [1 - beta/phi']^2, which reaches 0 at "
            f"beta = phi'; past it the bracket turns negative and the table "
            f"gives no value, so the load inclination must not exceed phi'")
    iq = (1 - beta / 90.0) ** 2
    return {
        "beta_deg": beta, "iq": iq, "ic": iq, "i_gamma": (1 - beta / phi) ** 2,
        "units": {"beta_deg": "degrees", "iq": "dimensionless",
                  "ic": "dimensionless", "i_gamma": "dimensionless"},
        "source": _source("Table 5-3", 108),
        "valid_for": "Drained analysis, USACE method; beta <= phi'.",
        "notes": "beta is the load inclination from vertical (Figure 5-9).",
    }


def table_5_3_aashto_load_inclination_factors(H: float, V: float,
                                              B_eff: float,
                                              L_eff: float | None,
                                              c: float, phi_deg: float,
                                              theta_deg: float) -> dict:
    """AASHTO (2020)/FHWA (2002) (Vesic based) load inclination factors for
    drained bearing capacity: beta = atan(H/(V + B'L' c cot(phi'))),
    n = nL cos^2(theta) + nB sin^2(theta), iq = (1 - tan(beta))^n,
    ic = iq - (1 - iq)/(Nq - 1), i-gamma = (1 - tan(beta))^(n+1).

    Print check (Table 5-3, p. 108, rendered and compared cell by cell):

        factor  AASHTO/FHWA as printed
        β       atan(H/(V + B′L′ · c · cotφ′))
        n       nB = (2 + L′/B′)/(1 + L′/B′); nL = (2 + B′/L′)/(1 + B′/L′);
                n = nL cos^2 θ + nB sin^2 θ
        iq      [1 − tanβ]^n
        ic      iq − (1 − iq)/(Nq − 1)
        iγ      "iq = [1 − tanβ]^(n+1)"   (the cell names it iq: iγ meant)

    Parameters
    ----------
    H : float
        Horizontal component of the applied load, kips.
    V : float
        Vertical load on the ground, kips.
    B_eff : float
        Effective width B', ft.
    L_eff : float or None
        Effective length L', ft. None for a continuous footing, where
        L'/B' tends to infinity: nB = 1 and nL = 2, the limits of the
        printed expressions, and B'L' in beta is per foot of length (B').
    c : float
        Cohesion c, ksf.
    phi_deg : float
        Friction angle phi', degrees.
    theta_deg : float
        Projected direction of the load in the plane of the footing,
        measured from the side of length L, degrees (Figure 5-9).

    Returns
    -------
    dict
        beta_deg, nB, nL, n, iq, ic, i_gamma, Nq, units, source, valid_for,
        notes.

    Raises
    ------
    ValueError
        If H < 0, V <= 0, c < 0, B' or L' is not positive, L' < B', phi' is
        not between 0 and 90 degrees, theta is outside 0 to 90 degrees, or
        tan(beta) > 1.
    """
    _non_negative("H", H)
    _positive("V", V)
    _non_negative("c", c)
    phi = _friction_angle(phi_deg)
    _ratio_b_over_l(B_eff, L_eff)
    th = float(theta_deg)
    if not 0 <= th <= 90:
        raise ValueError(f"theta_deg = {theta_deg}: give 0 to 90 degrees, "
                         f"measured from the side of length L (Figure 5-9)")
    B = float(B_eff)
    if L_eff is None:
        nB, nL, area = 1.0, 2.0, B
    else:
        L = float(L_eff)
        nB = (2 + L / B) / (1 + L / B)
        nL = (2 + B / L) / (1 + B / L)
        area = B * L
    n = nL * math.cos(math.radians(th)) ** 2 + nB * math.sin(math.radians(th)) ** 2
    r = math.radians(phi)
    t = float(H) / (float(V) + area * float(c) / math.tan(r))
    if t > 1:
        raise ValueError(f"tan(beta) = {t:.3f} > 1: [1 - tan(beta)]^n of "
                         f"Table 5-3 is not defined for it")
    Nq = table_5_2_bearing_capacity_factors(phi, "aashto")["Nq"]
    iq = (1 - t) ** n
    return {
        "beta_deg": math.degrees(math.atan(t)), "nB": nB, "nL": nL, "n": n,
        "iq": iq, "ic": iq - (1 - iq) / (Nq - 1), "i_gamma": (1 - t) ** (n + 1),
        "Nq": Nq,
        "units": {"beta_deg": "degrees", "n": "dimensionless",
                  "iq": "dimensionless", "ic": "dimensionless",
                  "i_gamma": "dimensionless"},
        "source": _source("Table 5-3", 108),
        "valid_for": "Drained analysis, AASHTO (2020)/FHWA (2002) method.",
        "notes": ("As printed, the i-gamma cell reads 'iq = [1 - tan(beta)]"
                  "^(n+1)'. For a continuous footing nB = 1 and nL = 2 are "
                  "the printed expressions' limits as L'/B' grows."),
    }


def table_5_3_base_inclination_factors(alpha_b_deg: float,
                                       phi_deg: float) -> dict:
    """Base inclination factors for drained bearing capacity, the same by
    both methods: bq = b-gamma = (1 - alpha_b/57 * tan(phi'))^2 and
    bc = bq - (1 - bq)/(Nc tan(phi')), alpha_b the base inclination from
    horizontal in degrees. AASHTO (2020) does not present base inclination;
    FHWA (2002) does (note a).

    Print check (Table 5-3, p. 108, rendered and compared cell by cell):

        factor  USACE and AASHTO/FHWA as printed (identical cells)
        bq      [1 − αb/(57°) · tanφ′]^2
        bc      bq − [(1 − bq)/(Nc · tanφ′)]
        bγ      [1 − αb/(57°) · tanφ′]^2

    Parameters
    ----------
    alpha_b_deg : float
        Base inclination from horizontal, degrees (Figure 5-10).
    phi_deg : float
        Friction angle phi', degrees.

    Returns
    -------
    dict
        bq, bc, b_gamma, Nc, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If alpha_b < 0, phi' is not between 0 and 90 degrees, or the
        bracket turns negative.
    """
    a = _non_negative("alpha_b_deg", alpha_b_deg)
    phi = _friction_angle(phi_deg)
    t = math.tan(math.radians(phi))
    inner = 1 - a / 57.0 * t
    if inner < 0:
        raise ValueError(f"1 - alpha_b/57 * tan(phi') = {inner:.3f} < 0: "
                         f"Table 5-3 gives no value for it")
    Nc = table_5_2_bearing_capacity_factors(phi, "usace" if 1.4 * phi < 90
                                            else "aashto")["Nc"]
    bq = inner ** 2
    return {
        "bq": bq, "bc": bq - (1 - bq) / (Nc * t), "b_gamma": bq, "Nc": Nc,
        "units": {"bq": "dimensionless", "bc": "dimensionless",
                  "b_gamma": "dimensionless"},
        "source": _source("Table 5-3", 108),
        "valid_for": ("Drained analysis, both methods (AASHTO (2020) does "
                      "not present base inclination; FHWA (2002) does)."),
        "notes": "alpha_b is measured from horizontal (Figure 5-10).",
    }


def table_5_3_usace_ground_inclination_factors(alpha_g_deg: float,
                                               d_g: float, B_eff: float,
                                               phi_deg: float) -> dict:
    """USACE ground inclination factors for drained bearing capacity next
    to a slope: gq,0 = g-gamma,0 = (1 - tan(alpha_g))^2,
    gc,0 = gq,0 - (1 - gq,0)/(Nc tan(phi')), each rising linearly to 1 at a
    distance from the slope of 5B' (gx = min[1, gx,0 + (1 - gx,0) dg/(5B')]).
    The subscript 0 is for a footing directly next to a slope with FS > 1.3.
    The AASHTO/FHWA column says "See tables in AASHTO (2020)", which this
    manual does not print.

    Print check (Table 5-3, pp. 108-109, rendered and compared):

        factor  USACE as printed                AASHTO/FHWA as printed
        gq,0    [1 − tanαg]^2                   Not Applicable
        gq      min[1, gq,0 + (1 − gq,0) dg/(5B′)]   See tables in AASHTO (2020)
        gc,0    gq,0 − [(1 − gq,0)/(Nc · tanφ′)]     Not Applicable
        gc      min[1, gc,0 + (1 − gc,0) dg/(5B′)]   See tables in AASHTO (2020)
        gγ,0    [1 − tanαg]^2                   Not Applicable
        gγ      min[1, gγ,0 + (1 − gγ,0) dg/(5B′)]   See tables in AASHTO (2020)

    Parameters
    ----------
    alpha_g_deg : float
        Ground inclination from horizontal, degrees (Figure 5-11).
    d_g : float
        Distance from the edge of the footing to the edge of the sloping
        ground, ft.
    B_eff : float
        Effective width B', ft.
    phi_deg : float
        Friction angle phi', degrees.

    Returns
    -------
    dict
        gq0, gq, gc0, gc, g_gamma0, g_gamma, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        If alpha_g is outside 0 to 45 degrees (tan(alpha_g) above 1 turns
        the bracket negative), d_g < 0, B' is not positive, or phi' is not
        between 0 and 90 degrees.
    """
    a = float(alpha_g_deg)
    if not 0 <= a <= 45:
        raise ValueError(f"alpha_g_deg = {alpha_g_deg}: [1 - tan(alpha_g)]^2 "
                         f"needs 0 to 45 degrees")
    dg = _non_negative("d_g", d_g)
    B = _positive("B_eff", B_eff)
    phi = _friction_angle(phi_deg)
    Nc = table_5_3_base_inclination_factors(0, phi)["Nc"]
    g0 = (1 - math.tan(math.radians(a))) ** 2
    gc0 = g0 - (1 - g0) / (Nc * math.tan(math.radians(phi)))
    ramp = dg / (5 * B)
    return {
        "gq0": g0, "gq": min(1.0, g0 + (1 - g0) * ramp),
        "gc0": gc0, "gc": min(1.0, gc0 + (1 - gc0) * ramp),
        "g_gamma0": g0, "g_gamma": min(1.0, g0 + (1 - g0) * ramp),
        "units": {k: "dimensionless" for k in
                  ("gq0", "gq", "gc0", "gc", "g_gamma0", "g_gamma")},
        "source": _source("Table 5-3", 108),
        "valid_for": ("Drained analysis, USACE method, footing near ground "
                      "sloping away from it; the 0 values are for a footing "
                      "directly next to a slope with FS > 1.3 (note b)."),
        "notes": ("The AASHTO (2020)/FHWA (2002) column refers to tables in "
                  "AASHTO (2020), not printed in this manual."),
    }


# ---------------------------------------------------------------------------
# Table 5-4
# ---------------------------------------------------------------------------

def table_5_4_undrained_factors(method: str, B_eff: float,
                                L_eff: float | None, Df: float, H: float,
                                V: float, su: float, theta_deg: float | None,
                                alpha_b_deg: float, alpha_g_deg: float,
                                d_g: float | None) -> dict:
    """Undrained (phi' = 0) bearing capacity factor and correction factors:
    Nc = 2 + pi = 5.14; sc = 1 + 0.2 B'/L' by both methods;
    dc = 1 + 0.2 Df/B' (at most 1.5) by the USACE method and 1 by the
    AASHTO/FHWA method; ic = 1 - 1.3 H/V (USACE) or 1 - nH/(c B'L' Nc)
    (AASHTO/FHWA); bc = 1 - alpha_b/147.3; and the USACE ground factor
    gc = min[1, gc,0 + (1 - gc,0) dg/(2B')] with gc,0 = 1 - alpha_g/147.3.
    The factors for q (sq, dq, iq, bq, gq) are 1 by both methods (note a).
    The USACE limit dc <= 1.5 is applied as printed: where the formula gives
    more, dc = 1.5 is returned, with the formula's value in dc_unlimited and
    limit_governs True.

    Print check (Table 5-4, p. 109, rendered and compared cell by cell):

        factor  USACE as printed               AASHTO/FHWA as printed
        Nc      (2 + π) = 5.14                 (2 + π) = 5.14
        sc      1 + 0.2 B′/L′                  1 + 0.2 B′/L′
        dc      1 + 0.2 Df/B′ ≤ 1.5            1 (note b)
        n       N/A                            nB, nL, n as in Table 5-3
        ic      1 − 1.3 H/V                    1 − (n · H)/(cB′L′Nc)
        bc      1 − αb/(147.3°)                1 − αb/(147.3°)
        gc,0    1 − αg/(147.3°)                Not Applicable
        gc      min[1, gc,0 + (1 − gc,0) dg/(2B′)]   See tables in AASHTO (2020)
        here    the same; a USACE dc above 1.5 is 1.5, the formula's value
                in dc_unlimited

    Parameters
    ----------
    method : str
        'usace' or 'aashto' ('fhwa' is taken as the same).
    B_eff : float
        Effective width B', ft.
    L_eff : float or None
        Effective length L', ft; None for a continuous footing (sc = 1;
        for the AASHTO ic, nB = 1 and nL = 2 and B'L' is per foot, B').
    Df : float
        Depth of the footing base below the ground surface, ft.
    H : float
        Horizontal load, kips; 0 for a vertical load.
    V : float
        Vertical load, kips.
    su : float
        Undrained strength c = su, ksf (used by the AASHTO ic).
    theta_deg : float or None
        Direction of the horizontal load from the side of length L,
        degrees (Figure 5-9); needed only for the AASHTO ic with H > 0.
    alpha_b_deg : float
        Base inclination from horizontal, degrees; 0 for a flat base.
    alpha_g_deg : float
        Ground inclination from horizontal, degrees; 0 for level ground.
    d_g : float or None
        Distance from the footing edge to the edge of the slope, ft; needed
        only when alpha_g > 0 (USACE).

    Returns
    -------
    dict
        Nc, sc, dc, dc_unlimited, limit_governs, ic, bc, gc, gc0 (USACE
        with a slope), n (AASHTO with H > 0), method, units, source,
        valid_for, notes.

    Raises
    ------
    ValueError
        For an unknown method, a slope with the AASHTO/FHWA method (its ground factors are in AASHTO (2020), not
        printed here), theta or d_g missing where needed, or values out of
        range (H < 0, V <= 0, su <= 0, angles negative, ic < 0).
    """
    m = _method(method)
    bl = _ratio_b_over_l(B_eff, L_eff)
    B = float(B_eff)
    dfb = _non_negative("Df", Df) / B
    h = _non_negative("H", H)
    v = _positive("V", V)
    c = _positive("su", su)
    ab = _non_negative("alpha_b_deg", alpha_b_deg)
    ag = _non_negative("alpha_g_deg", alpha_g_deg)
    Nc = 2 + math.pi
    out = {"Nc": Nc, "sc": 1 + 0.2 * bl}
    limit_note = ""
    if m == "usace":
        dc = 1 + 0.2 * dfb
        out["dc"] = min(dc, 1.5)
        out["dc_unlimited"] = dc
        out["limit_governs"] = dc > 1.5
        if dc > 1.5:
            limit_note = (f" The formula gives dc = {dc:.3f}; Table 5-4 (p. "
                          f"109) prints the USACE depth factor as 'dc = 1 + "
                          f"0.2 Df/B' <= 1.5', so dc = 1.5 is returned "
                          f"(dc_unlimited holds the formula's value).")
        out["ic"] = 1 - 1.3 * h / v
    else:
        out["dc"] = 1.0
        out["dc_unlimited"] = 1.0
        out["limit_governs"] = False
        if h > 0:
            if theta_deg is None:
                raise ValueError("theta_deg is needed for the AASHTO ic "
                                 "when H > 0 (Figure 5-9)")
            th = float(theta_deg)
            if not 0 <= th <= 90:
                raise ValueError(f"theta_deg = {theta_deg}: give 0 to 90")
            if L_eff is None:
                nB, nL, area = 1.0, 2.0, B
            else:
                L = float(L_eff)
                nB = (2 + L / B) / (1 + L / B)
                nL = (2 + B / L) / (1 + B / L)
                area = B * L
            n = (nL * math.cos(math.radians(th)) ** 2
                 + nB * math.sin(math.radians(th)) ** 2)
            out["n"] = n
            out["ic"] = 1 - n * h / (c * area * Nc)
        else:
            out["ic"] = 1.0
    if out["ic"] < 0:
        raise ValueError(f"ic = {out['ic']:.3f} < 0: the load is too "
                         f"inclined for Table 5-4's expression")
    out["bc"] = 1 - ab / 147.3
    if ag > 0:
        if m != "usace":
            raise ValueError(
                "The AASHTO (2020)/FHWA (2002) ground inclination factor is "
                "'See tables in AASHTO (2020)' (Table 5-4), not printed in "
                "this manual")
        if d_g is None:
            raise ValueError("d_g is needed when alpha_g > 0")
        gc0 = 1 - ag / 147.3
        out["gc0"] = gc0
        out["gc"] = min(1.0, gc0 + (1 - gc0) * _non_negative("d_g", d_g) / (2 * B))
    else:
        out["gc"] = 1.0
    out.update({
        "method": _METHOD_NAMES[m],
        "units": {k: "dimensionless" for k in out if k != "limit_governs"},
        "source": _source("Table 5-4", 109),
        "valid_for": ("Undrained (phi' = 0) analysis, c = su; the factors "
                      "for q (sq, dq, iq, bq, gq) are 1 by both methods."),
        "notes": ("FHWA does not present depth factors for phi' = 0 and "
                  "states that 'the depth correction factors can be "
                  "conservatively omitted' (note b). The 0 ground value is "
                  "for a footing directly next to a slope with FS > 1.3, "
                  "rising linearly to 1 at a distance of 2B' (note d)."
                  + limit_note),
    })
    return out


# ---------------------------------------------------------------------------
# Table 5-5
# ---------------------------------------------------------------------------

_TABLE_5_5 = {
    "spt": ("N60e · pref", 0.6, 0.35),
    "cpt": ("qne", 0.1, 0.35),
    "pmt": ("pne", 0.9, 0.7),
}


def table_5_5_in_situ_bearing_factor(test: str, drainage: str) -> dict:
    """Uncorrected bearing capacity factor k for the in situ test bearing
    capacity equations 5-25 (drained) and 5-26 (undrained): SPT 0.6 / 0.35
    on N60e times pref (pref = 2 ksf), CPT 0.1 / 0.35 on the equivalent net
    cone tip resistance qne, PMT 0.9 / 0.7 on the equivalent net limit
    pressure pne.

    Print check (Table 5-5, p. 116, rendered and compared cell by cell):

        in situ test  s parameter (ksf)  k drained  k undrained
        SPT           N60e · pref        0.6        0.35
        CPT           qne                0.1        0.35
        PMT           pne                0.9        0.7

    Parameters
    ----------
    test : str
        'SPT', 'CPT' or 'PMT'.
    drainage : str
        'drained' or 'undrained'.

    Returns
    -------
    dict
        test, drainage, k, s_parameter, units, source, valid_for, notes.

    Raises
    ------
    ValueError
        For a test or drainage condition the table does not list.
    """
    t = str(test).lower().strip()
    d = str(drainage).lower().strip()
    if t not in _TABLE_5_5:
        raise ValueError(f"Unknown test {test!r}: Table 5-5 lists SPT, CPT, PMT")
    if d not in ("drained", "undrained"):
        raise ValueError(f"Unknown drainage {drainage!r}: give 'drained' or "
                         f"'undrained'")
    s, kd, ku = _TABLE_5_5[t]
    return {
        "test": t.upper(), "drainage": d,
        "k": kd if d == "drained" else ku,
        "s_parameter": s,
        "units": {"k": "dimensionless", "s_parameter": "ksf"},
        "source": _source("Table 5-5", 116),
        "valid_for": ("Equations 5-25 and 5-26 with the USACE (Meyerhof "
                      "based) correction factors (paragraph 5-5i(4)); the "
                      "drainage during critical loading should be that of "
                      "the in situ test (paragraph 5-5i(3))."),
        "notes": ("After FHWA-IP-89-008; Mayne 2007a; Briaud 2013. pref = 2 "
                  "ksf; s is the geometric mean of the values in the shear "
                  "zone (equation 5-24)."),
    }


# ---------------------------------------------------------------------------
# Table 7-6
# ---------------------------------------------------------------------------

#: soil -> state -> (E/P*L range as printed, alpha); the ranges are kept as
#: printed text, since the table gives no value between or beyond them
_TABLE_7_6 = {
    "peat": {"normally consolidated": ("For all values", 1.0)},
    "clay": {"overconsolidated": (">16", 1.0),
             "normally consolidated": ("9 to 16", 2 / 3),
             "weathered and/or remolded": ("7 to 9", 1 / 2)},
    "silt": {"overconsolidated": (">14", 2 / 3),
             "normally consolidated": ("8 to 14", 1 / 2),
             "weathered and/or remolded": ("–", 1 / 2)},
    "sand": {"overconsolidated": (">12", 1 / 2),
             "normally consolidated": ("7 to 12", 1 / 3),
             "weathered and/or remolded": ("–", 1 / 3)},
    "sand and gravel": {"overconsolidated": (">10", 1 / 3),
                        "normally consolidated": ("6 to 10", 1 / 4),
                        "weathered and/or remolded": ("–", 1 / 4)},
    "rock": {"extremely fractured": ("–", 1 / 3),
             "other": ("–", 1 / 2),
             "slightly fractured or extremely weathered": ("–", 2 / 3)},
}


def table_7_6_menard_rheological_factor(soil: str, state: str) -> dict:
    """Menard's rheological factor alpha for the pressuremeter settlement
    equations 7-11 and 7-12, by soil type and state of consolidation, with
    the range of E/P*L the table prints for each (Briaud 1992): from 1 for
    peat and overconsolidated clay to 1/4 for normally consolidated or
    weathered sand and gravel. The ratio E/P*L that places a soil in a state
    is given back as printed; the choice of state is the engineer's.

    Print check (Table 7-6, p. 170, rendered and compared cell by cell):

        state                       peat         clay       silt       sand       sand+gravel
                                    E/P*L  α     E/P*L  α   E/P*L  α   E/P*L  α   E/P*L  α
        Over-consolidated           –      –     >16   1    >14  2/3   >12  1/2   >10  1/3
        Normally consolidated       all    1     9-16 2/3   8-14 1/2   7-12 1/3   6-10 1/4
        Weathered and/or remolded   –      –     7-9  1/2   –    1/2   –    1/3   –    1/4
        Rock: Extremely Fractured α = 1/3; Other α = 1/2; Slightly
        Fractured or Extremely Weathered α = 2/3

    Parameters
    ----------
    soil : str
        'peat', 'clay', 'silt', 'sand', 'sand and gravel' or 'rock'.
    state : str
        For soils 'overconsolidated', 'normally consolidated' or
        'weathered and/or remolded' ('weathered' or 'remolded' for short);
        for rock 'extremely fractured', 'other' or 'slightly fractured or
        extremely weathered'.

    Returns
    -------
    dict
        soil, state, alpha, E_over_PL_range (as printed), units, source,
        valid_for, notes.

    Raises
    ------
    ValueError
        For a soil or state the table does not give a factor for (peat is
        printed only as normally consolidated).
    """
    s = " ".join(str(soil).lower().split())
    st = " ".join(str(state).lower().replace("-", "").split())
    st = {"over consolidated": "overconsolidated", "weathered": "weathered "
          "and/or remolded", "remolded": "weathered and/or remolded"}.get(st, st)
    if s not in _TABLE_7_6:
        raise ValueError(f"Unknown soil {soil!r}. Table 7-6 lists: "
                         f"{', '.join(_TABLE_7_6)}")
    if st not in _TABLE_7_6[s]:
        raise ValueError(f"Table 7-6 gives no factor for {s} in state "
                         f"{state!r}; it gives: {', '.join(_TABLE_7_6[s])}")
    rng, alpha = _TABLE_7_6[s][st]
    return {
        "soil": s, "state": st, "alpha": alpha, "E_over_PL_range": rng,
        "units": {"alpha": "dimensionless", "E_over_PL_range": "dimensionless"},
        "source": _source("Table 7-6", 170),
        "valid_for": ("Equations 7-11 and 7-12 (Menard and Rousseau "
                      "pressuremeter method, Table 7-5)."),
        "notes": ("Briaud 1992. The table's notes: E = Ec, Ed and EL as "
                  "applicable (tsf), P*L = net limit pressure (tsf); alpha = "
                  "alpha_c, alpha_d, alpha_L per Ec/pne, Ed/pne and EL/pne "
                  "respectively. For rock the table prints no E/P*L range."),
    }
