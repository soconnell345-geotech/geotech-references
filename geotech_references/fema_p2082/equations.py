"""FEMA P-2082 (2020 NEHRP Provisions) seismic design equations.

Chapter 11 (Seismic Design Criteria) design spectral parameters:

  SDS = (2/3) * SMS            Eq. (11.4-1)
  SD1 = (2/3) * SM1            Eq. (11.4-2)

and the two-period design response spectrum (Section 11.4.5.2, Figure 11.4-1):

  T0 = 0.2 * (SD1 / SDS)
  Ts = SD1 / SDS
  Sa = SDS * (0.4 + 0.6*T/T0)          for T < T0          Eq. (11.4-3)
  Sa = SDS                              for T0 <= T <= Ts
  Sa = SD1 / T                          for Ts < T <= TL    Eq. (11.4-4)
  Sa = SD1 * TL / T^2                   for T > TL          Eq. (11.4-5)

NOTE: P-2082 prefers the multi-period design response spectrum read directly
from the USGS Seismic Design Geodatabase (Section 11.4.5.1, Sa = (2/3) * the
multi-period MCER spectrum). The two-period spectrum below is the fallback
"where values of the multi-period MCER response spectrum are not available."
P-2082 DELETED the ASCE 7-16 Fa/Fv site coefficients; SMS/SM1 are the
site-class-specific MCER values from the geodatabase, not Fa*SS / Fv*S1.

Source: FEMA P-2082-1 (2020), PDF pages 52-54 (printed pages 15-17).
"""


def design_spectral_acceleration_short(sms) -> dict:
    """Design spectral response acceleration at short periods, SDS (Eq. 11.4-1).

        SDS = (2/3) * SMS

    Parameters
    ----------
    sms : float
        5%-damped MCER spectral response acceleration at short periods, SMS
        (from the USGS Seismic Design Geodatabase for the site class).

    Returns
    -------
    dict
        {'sms': float, 'sds': float, 'equation': '11.4-1', 'reference': str}

    Raises
    ------
    ValueError
        If sms is negative.
    """
    if sms < 0:
        raise ValueError(f"sms must be >= 0, got {sms}")
    return {
        "sms": sms,
        "sds": round(2.0 / 3.0 * sms, 4),
        "equation": "11.4-1",
        "reference": "FEMA P-2082 (2020 NEHRP) Eq. (11.4-1)",
    }


def design_spectral_acceleration_1s(sm1) -> dict:
    """Design spectral response acceleration at a 1-s period, SD1 (Eq. 11.4-2).

        SD1 = (2/3) * SM1

    Parameters
    ----------
    sm1 : float
        5%-damped MCER spectral response acceleration at a 1-s period, SM1
        (from the USGS Seismic Design Geodatabase for the site class).

    Returns
    -------
    dict
        {'sm1': float, 'sd1': float, 'equation': '11.4-2', 'reference': str}

    Raises
    ------
    ValueError
        If sm1 is negative.
    """
    if sm1 < 0:
        raise ValueError(f"sm1 must be >= 0, got {sm1}")
    return {
        "sm1": sm1,
        "sd1": round(2.0 / 3.0 * sm1, 4),
        "equation": "11.4-2",
        "reference": "FEMA P-2082 (2020 NEHRP) Eq. (11.4-2)",
    }


def mcer_from_design_spectrum(sa_design) -> dict:
    """MCER spectral acceleration from the design value (Section 11.4.6).

        Sa(MCER) = 1.5 * Sa(design)

    The MCER response spectrum is the design response spectrum multiplied by 1.5
    (the inverse of the 2/3 design factor).

    Parameters
    ----------
    sa_design : float
        Design spectral response acceleration at any period, Sa.

    Returns
    -------
    dict
        {'sa_design': float, 'sa_mcer': float, 'reference': str}

    Raises
    ------
    ValueError
        If sa_design is negative.
    """
    if sa_design < 0:
        raise ValueError(f"sa_design must be >= 0, got {sa_design}")
    return {
        "sa_design": sa_design,
        "sa_mcer": round(1.5 * sa_design, 4),
        "reference": "FEMA P-2082 (2020 NEHRP) Section 11.4.6",
    }


def two_period_spectrum_parameters(sds, sd1) -> dict:
    """Corner periods T0 and Ts of the two-period design spectrum (Sec 11.4.5.2).

        T0 = 0.2 * (SD1 / SDS)
        Ts = SD1 / SDS

    Parameters
    ----------
    sds : float
        Design spectral acceleration at short periods, SDS (> 0).
    sd1 : float
        Design spectral acceleration at a 1-s period, SD1.

    Returns
    -------
    dict
        {'sds': float, 'sd1': float, 't0_s': float, 'ts_s': float,
         'reference': str}

    Raises
    ------
    ValueError
        If sds <= 0 or sd1 < 0.
    """
    if sds <= 0:
        raise ValueError(f"sds must be > 0, got {sds}")
    if sd1 < 0:
        raise ValueError(f"sd1 must be >= 0, got {sd1}")
    ts = sd1 / sds
    return {
        "sds": sds,
        "sd1": sd1,
        "t0_s": round(0.2 * ts, 4),
        "ts_s": round(ts, 4),
        "reference": "FEMA P-2082 (2020 NEHRP) Section 11.4.5.2, Figure 11.4-1",
    }


def design_response_spectrum_sa(period, sds, sd1, tl: float = 8.0) -> dict:
    """Two-period design spectral acceleration Sa at a period T (Sec 11.4.5.2).

    Implements the two-period (Figure 11.4-1) design response spectrum:

        T < T0:        Sa = SDS * (0.4 + 0.6 * T/T0)        Eq. (11.4-3)
        T0 <= T <= Ts: Sa = SDS
        Ts < T <= TL:  Sa = SD1 / T                          Eq. (11.4-4)
        T > TL:        Sa = SD1 * TL / T^2                    Eq. (11.4-5)

    with T0 = 0.2*SD1/SDS and Ts = SD1/SDS.

    Parameters
    ----------
    period : float
        Structural period T (s), >= 0.
    sds : float
        Design spectral acceleration at short periods, SDS (> 0).
    sd1 : float
        Design spectral acceleration at a 1-s period, SD1.
    tl : float, optional
        Long-period transition period TL (s), from Figs. 22-14..22-17.
        Default 8.0 s (a common conterminous-US value).

    Returns
    -------
    dict
        {'period_s': float, 'sds': float, 'sd1': float, 't0_s': float,
         'ts_s': float, 'tl_s': float, 'sa': float, 'branch': str,
         'reference': str}

    Raises
    ------
    ValueError
        If inputs are invalid.
    """
    if period < 0:
        raise ValueError(f"period must be >= 0, got {period}")
    if sds <= 0:
        raise ValueError(f"sds must be > 0, got {sds}")
    if sd1 < 0:
        raise ValueError(f"sd1 must be >= 0, got {sd1}")
    if tl <= 0:
        raise ValueError(f"tl must be > 0, got {tl}")

    t0 = 0.2 * sd1 / sds
    ts = sd1 / sds

    if period < t0:
        sa = sds * (0.4 + 0.6 * period / t0) if t0 > 0 else sds
        branch = "ascending (Eq. 11.4-3)"
    elif period <= ts:
        sa = sds
        branch = "plateau (SDS)"
    elif period <= tl:
        sa = sd1 / period
        branch = "constant-velocity (Eq. 11.4-4)"
    else:
        sa = sd1 * tl / (period ** 2)
        branch = "constant-displacement (Eq. 11.4-5)"

    return {
        "period_s": period,
        "sds": sds,
        "sd1": sd1,
        "t0_s": round(t0, 4),
        "ts_s": round(ts, 4),
        "tl_s": tl,
        "sa": round(sa, 4),
        "branch": branch,
        "reference": "FEMA P-2082 (2020 NEHRP) Section 11.4.5.2, Figure 11.4-1",
    }
