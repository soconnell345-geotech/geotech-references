"""Wood Handbook Chapter 4 -- Moisture Relations and Physical Properties of
Wood (equilibrium moisture content, shrinkage, and density/specific-gravity
conversions).

Provides:
  - ``equilibrium_moisture_content`` / ``relative_humidity_from_emc`` --
    the Hailwood-Horrobin sorption model (Eq 4-5, Simpson 1973) that Table
    4-2 was calculated from, plus its inverse (Eq 4-7).
  - ``equilibrium_moisture_content_glass`` -- the alternative closed-form
    EMC model of Glass and others (2014) (Eq 4-6).
  - ``max_moisture_content`` / ``sink_moisture_content`` -- the maximum
    possible moisture content (Eq 4-3) and the moisture content at which
    wood just sinks in water (Eq 4-4), both functions of basic specific
    gravity.
  - ``shrinkage_at_moisture_content`` (Eq 4-9), ``convert_specific_gravity``
    (Eq 4-10), ``specific_gravity_from_basic`` (Eq 4-11/4-13),
    ``estimate_total_shrinkage_from_basic_sg`` (Eq 4-12) -- the
    shrinkage-moisture content-specific gravity relations.
  - ``density_from_specific_gravity`` (Eq 4-14),
    ``density_from_ovendry_density`` (Eq 4-15),
    ``estimate_total_shrinkage_from_ovendry_density`` (Eq 4-16) -- density
    at any moisture content.
  - ``thermal_conductivity`` (Eq 4-17).
  - ``table_4_1_green_moisture_content`` / ``table_4_3_shrinkage`` --
    printed-table lookups for the module's documented species subset (see
    ``mechanical_properties.py`` docstring for the subset rule).

All printed citations use the PRINTED page of General Technical Report
FPL-GTR-282 (2021 edition); ``pdf_page = printed_page + 93`` for Chapter 4
in this PDF (0-based PyMuPDF page index).

UNITS: this handbook is printed with both SI and inch-pound tables side by
side; this package digitizes the SI (metric) tables/equations throughout,
per repo convention. Temperatures in equilibrium_moisture_content are in
degrees Celsius.
"""

import math

# ============================================================================
# Table 4-1 -- Average moisture content of green wood, by species
# (printed p. 4-2). Heartwood/sapwood MC (%) for this module's species
# subset (see mechanical_properties.SPECIES_SUBSET_NOTE).
# ============================================================================

TABLE_4_1_GREEN_MC = {
    "ash, white": {"heartwood": 46, "sapwood": 44},
    "cherry, black": {"heartwood": 58, "sapwood": None},
    "maple, sugar": {"heartwood": 65, "sapwood": 72},
    "oak, northern red": {"heartwood": 80, "sapwood": 69},
    "oak, white": {"heartwood": 64, "sapwood": 78},
    "yellow-poplar": {"heartwood": 83, "sapwood": 106},
    "douglas-fir, coast": {"heartwood": 37, "sapwood": 115},
    "fir, balsam": {"heartwood": 88, "sapwood": 173},
    "fir, grand": {"heartwood": 91, "sapwood": 136},
    "hemlock, eastern": {"heartwood": 97, "sapwood": 119},
    "hemlock, western": {"heartwood": 85, "sapwood": 170},
    "larch, western": {"heartwood": 54, "sapwood": 119},
    "pine, loblolly": {"heartwood": 33, "sapwood": 110},
    "pine, lodgepole": {"heartwood": 41, "sapwood": 120},
    "pine, longleaf": {"heartwood": 31, "sapwood": 106},
    "spruce, engelmann": {"heartwood": 51, "sapwood": 173},
}


def table_4_1_green_moisture_content(species):
    """Table 4-1: average moisture content of green heartwood/sapwood, by
    species (printed p. 4-2).

    Parameters
    ----------
    species : str
        A key of ``TABLE_4_1_GREEN_MC`` (case-insensitive).

    Returns
    -------
    dict
        {'species', 'heartwood_mc_pct', 'sapwood_mc_pct', 'table': '4-1', ...}
    """
    key = species.lower().strip()
    if key not in TABLE_4_1_GREEN_MC:
        raise ValueError(
            f"species must be one of {sorted(TABLE_4_1_GREEN_MC)}, got {species!r}"
        )
    row = TABLE_4_1_GREEN_MC[key]
    return {
        "species": key, "heartwood_mc_pct": row["heartwood"],
        "sapwood_mc_pct": row["sapwood"], "table": "4-1",
        "printed_page": "4-2", "pdf_page": 95,
    }


# ============================================================================
# Eq 4-3, 4-4 -- Maximum possible moisture content and sink moisture content
# (printed p. 4-3, pdf_page 96)
# ============================================================================

def max_moisture_content(basic_specific_gravity):
    """Eq 4-3: maximum possible moisture content MCmax (%), reached when
    both cell lumina and cell walls are completely saturated with water
    (printed p. 4-3).

        MCmax = 100*(1.54 - Gb) / (1.54*Gb)

    where 1.54 is the specific gravity of wood cell-wall substance.
    Ranges from ~267% at Gb=0.30 to ~44% at Gb=0.90 (both printed anchors).

    Parameters
    ----------
    basic_specific_gravity : float
        Gb, ovendry mass / green volume.

    Returns
    -------
    dict
        {'basic_specific_gravity', 'mc_max_pct', 'equation': '4-3', ...}
    """
    if basic_specific_gravity <= 0:
        raise ValueError("basic_specific_gravity must be > 0")
    mc_max = 100.0 * (1.54 - basic_specific_gravity) / (1.54 * basic_specific_gravity)
    return {
        "basic_specific_gravity": basic_specific_gravity, "mc_max_pct": mc_max,
        "equation": "4-3", "printed_page": "4-3", "pdf_page": 96,
    }


def sink_moisture_content(basic_specific_gravity):
    """Eq 4-4: moisture content at which wood will just sink in water,
    MCsink (%) (printed p. 4-3).

        MCsink = 100*(1 - Gb) / Gb

    Parameters
    ----------
    basic_specific_gravity : float
        Gb, ovendry mass / green volume.

    Returns
    -------
    dict
        {'basic_specific_gravity', 'mc_sink_pct', 'equation': '4-4', ...}
    """
    if basic_specific_gravity <= 0:
        raise ValueError("basic_specific_gravity must be > 0")
    mc_sink = 100.0 * (1.0 - basic_specific_gravity) / basic_specific_gravity
    return {
        "basic_specific_gravity": basic_specific_gravity, "mc_sink_pct": mc_sink,
        "equation": "4-4", "printed_page": "4-3", "pdf_page": 96,
    }


# ============================================================================
# Eq 4-5, 4-6, 4-7 -- Equilibrium moisture content (Table 4-2 was calculated
# from Eq 4-5) (printed pp. 4-3 to 4-4, pdf_page 96-97)
# ============================================================================

def equilibrium_moisture_content(temp_c, relative_humidity):
    """Eq 4-5: equilibrium moisture content (%) from the Hailwood-Horrobin
    sorption model (Simpson 1973), which Table 4-2 was calculated from
    (printed p. 4-3).

        EMC(%) = (1800/W) * [Kh/(1-Kh) + (K1*Kh + 2*K1*K2*(Kh)^2)
                              / (1 + K1*Kh + K1*K2*(Kh)^2)]

    with (T in degrees C):
        W  = 349 + 1.29*T + 0.0135*T^2
        K  = 0.805 + 0.000736*T - 0.00000273*T^2
        K1 = 6.27 - 0.00938*T - 0.000303*T^2
        K2 = 1.91 + 0.0407*T - 0.000293*T^2

    Parameters
    ----------
    temp_c : float
        Temperature (degrees C).
    relative_humidity : float
        Relative humidity as a decimal, 0 <= h < 1.

    Returns
    -------
    dict
        {'temp_c', 'relative_humidity', 'emc_pct', 'equation': '4-5', ...}
    """
    if not (0.0 <= relative_humidity < 1.0):
        raise ValueError("relative_humidity must be in [0, 1)")
    t = temp_c
    w = 349.0 + 1.29 * t + 0.0135 * t**2
    k = 0.805 + 0.000736 * t - 0.00000273 * t**2
    k1 = 6.27 - 0.00938 * t - 0.000303 * t**2
    k2 = 1.91 + 0.0407 * t - 0.000293 * t**2
    kh = k * relative_humidity
    emc = (1800.0 / w) * (
        kh / (1.0 - kh)
        + (k1 * kh + 2.0 * k1 * k2 * kh**2) / (1.0 + k1 * kh + k1 * k2 * kh**2)
    )
    return {
        "temp_c": temp_c, "relative_humidity": relative_humidity,
        "emc_pct": emc, "equation": "4-5", "printed_page": "4-3", "pdf_page": 96,
    }


def equilibrium_moisture_content_glass(temp_c, relative_humidity):
    """Eq 4-6: alternative EMC equation of Glass and others (2014)
    (printed p. 4-4). Uses kelvins internally.

        EMC(%) = 100 * [A*T*(1-T/Tc)^B * ln(1-h)] ^ (C*T^D)

    with parameters (T in kelvins, [K] = [degC] + 273.15):
        A = -0.000612, B = 2.43, C = 0.0577, D = 0.430, Tc = 647.1 K

    (A and ln(1-h) are both negative for 0<h<1, so the bracketed term is
    positive, as required before raising it to the C*T^D power.)

    Parameters
    ----------
    temp_c : float
        Temperature (degrees C).
    relative_humidity : float
        Relative humidity as a decimal, 0 <= h < 1.

    Returns
    -------
    dict
        {'temp_c', 'relative_humidity', 'emc_pct', 'equation': '4-6', ...}
    """
    if not (0.0 <= relative_humidity < 1.0):
        raise ValueError("relative_humidity must be in [0, 1)")
    a, b, c, d, t_c = -0.000612, 2.43, 0.0577, 0.430, 647.1
    t = temp_c + 273.15
    inner = a * t * (1.0 - t / t_c) ** b * math.log(1.0 - relative_humidity)
    emc = 100.0 * inner ** (c * t**d)
    return {
        "temp_c": temp_c, "relative_humidity": relative_humidity,
        "emc_pct": emc, "equation": "4-6", "printed_page": "4-4", "pdf_page": 97,
    }


def relative_humidity_from_emc(temp_c, emc_pct):
    """Eq 4-7: relative humidity from EMC, the inverted form of Equation
    (4-6) (Glass and others 2014) (printed p. 4-4).

        h = 1 - exp{ (1/(A*T)) * (1-T/Tc)^(-B) * (EMC/100)^((1/C)*T^(-D)) }

    Parameters
    ----------
    temp_c : float
        Temperature (degrees C).
    emc_pct : float
        Equilibrium moisture content (%).

    Returns
    -------
    dict
        {'temp_c', 'emc_pct', 'relative_humidity', 'equation': '4-7', ...}
    """
    a, b, c, d, t_c = -0.000612, 2.43, 0.0577, 0.430, 647.1
    t = temp_c + 273.15
    exponent = (1.0 / c) * t ** (-d)
    inner = (1.0 / (a * t)) * (1.0 - t / t_c) ** (-b) * (emc_pct / 100.0) ** exponent
    rh = 1.0 - math.exp(inner)
    return {
        "temp_c": temp_c, "emc_pct": emc_pct, "relative_humidity": rh,
        "equation": "4-7", "printed_page": "4-4", "pdf_page": 97,
    }


# ============================================================================
# Table 4-3 -- Shrinkage values of domestic woods (printed p. 4-8)
# Radial/tangential/volumetric shrinkage (%) from green to ovendry MC, for
# this module's documented species subset.
# ============================================================================

TABLE_4_3_SHRINKAGE = {
    # Hardwoods
    "ash, white": {"radial": 4.9, "tangential": 7.8, "volumetric": 13.3},
    "cherry, black": {"radial": 3.7, "tangential": 7.1, "volumetric": 11.5},
    "maple, sugar": {"radial": 4.8, "tangential": 9.9, "volumetric": 14.7},
    "oak, northern red": {"radial": 4.0, "tangential": 8.6, "volumetric": 13.7},
    "oak, white": {"radial": 5.6, "tangential": 10.5, "volumetric": 16.3},
    "yellow-poplar": {"radial": 4.6, "tangential": 8.2, "volumetric": 12.7},
    # Softwoods -- Douglas-fir
    "douglas-fir, coast": {"radial": 4.8, "tangential": 7.6, "volumetric": 12.4},
    "douglas-fir, interior north": {"radial": 3.8, "tangential": 6.9, "volumetric": 10.7},
    "douglas-fir, interior west": {"radial": 4.8, "tangential": 7.5, "volumetric": 11.8},
    # Softwoods -- Fir (Hem-Fir true-fir constituents + balsam/subalpine)
    "fir, balsam": {"radial": 2.9, "tangential": 6.9, "volumetric": 11.2},
    "fir, california red": {"radial": 4.5, "tangential": 7.9, "volumetric": 11.4},
    "fir, grand": {"radial": 3.4, "tangential": 7.5, "volumetric": 11.0},
    "fir, noble": {"radial": 4.3, "tangential": 8.3, "volumetric": 12.4},
    "fir, pacific silver": {"radial": 4.4, "tangential": 9.2, "volumetric": 13.0},
    "fir, subalpine": {"radial": 2.6, "tangential": 7.4, "volumetric": 9.4},
    "fir, white": {"radial": 3.3, "tangential": 7.0, "volumetric": 9.8},
    # Softwoods -- Hemlock (Hem-Fir constituent)
    "hemlock, eastern": {"radial": 3.0, "tangential": 6.8, "volumetric": 9.7},
    "hemlock, mountain": {"radial": 4.4, "tangential": 7.1, "volumetric": 11.1},
    "hemlock, western": {"radial": 4.2, "tangential": 7.8, "volumetric": 12.4},
    # Softwoods -- Larch (Douglas Fir-Larch group)
    "larch, western": {"radial": 4.5, "tangential": 9.1, "volumetric": 14.0},
    # Softwoods -- Pine (Southern Pine group + SPF constituents)
    "pine, jack": {"radial": 3.7, "tangential": 6.6, "volumetric": 10.3},
    "pine, loblolly": {"radial": 4.8, "tangential": 7.4, "volumetric": 12.3},
    "pine, lodgepole": {"radial": 4.3, "tangential": 6.7, "volumetric": 11.1},
    "pine, longleaf": {"radial": 5.1, "tangential": 7.5, "volumetric": 12.2},
    "pine, shortleaf": {"radial": 4.6, "tangential": 7.7, "volumetric": 12.3},
    "pine, slash": {"radial": 5.4, "tangential": 7.6, "volumetric": 12.1},
    # Softwoods -- Spruce (SPF constituent)
    "spruce, engelmann": {"radial": 3.8, "tangential": 7.1, "volumetric": 11.0},
}


def table_4_3_shrinkage(species):
    """Table 4-3: radial/tangential/volumetric shrinkage (%) from green to
    ovendry moisture content, for the module's documented species subset
    (printed p. 4-8). Values are S0 in Equation (4-9).

    Parameters
    ----------
    species : str
        A key of ``TABLE_4_3_SHRINKAGE`` (case-insensitive).

    Returns
    -------
    dict
        {'species', 'radial_pct', 'tangential_pct', 'volumetric_pct',
         'table': '4-3', ...}
    """
    key = species.lower().strip()
    if key not in TABLE_4_3_SHRINKAGE:
        raise ValueError(
            f"species must be one of {sorted(TABLE_4_3_SHRINKAGE)}, got {species!r}"
        )
    row = TABLE_4_3_SHRINKAGE[key]
    return {
        "species": key, "radial_pct": row["radial"],
        "tangential_pct": row["tangential"], "volumetric_pct": row["volumetric"],
        "table": "4-3", "printed_page": "4-8", "pdf_page": 101,
    }


# ============================================================================
# Eq 4-9 to 4-13 -- Shrinkage-moisture content-specific gravity relations
# (printed pp. 4-10 to 4-12, pdf_page 103-105)
# ============================================================================

def shrinkage_at_moisture_content(s0_pct, moisture_content_pct, mc_fs=30.0):
    """Eq 4-9: percent shrinkage Sx from the green condition to a final
    moisture content x, assuming shrinkage begins at the fiber saturation
    point and dimensions decrease linearly with decreasing MC below it
    (printed p. 4-10).

        Sx = S0 * (1 - x/MCfs)

    Parameters
    ----------
    s0_pct : float
        S0, percent shrinkage from green to ovendry (radial, tangential, or
        volumetric; from Table 4-3/4-4, e.g. ``table_4_3_shrinkage``).
    moisture_content_pct : float
        x, final moisture content (%); should be <= mc_fs for the linear
        assumption to apply.
    mc_fs : float, optional
        Fiber saturation point (%, default 30, the printed approximation
        when MCfs is not known for the species).

    Returns
    -------
    dict
        {'s0_pct', 'moisture_content_pct', 'mc_fs', 'shrinkage_pct',
         'equation': '4-9', ...}
    """
    sx = s0_pct * (1.0 - moisture_content_pct / mc_fs)
    return {
        "s0_pct": s0_pct, "moisture_content_pct": moisture_content_pct,
        "mc_fs": mc_fs, "shrinkage_pct": sx, "equation": "4-9",
        "printed_page": "4-10", "pdf_page": 103,
    }


def convert_specific_gravity(gx_prime, sx_prime_pct, sx_double_prime_pct):
    """Eq 4-10: convert specific gravity from one moisture-content volume
    basis x' to another x'' using the volumetric shrinkage at each basis
    (printed p. 4-11).

        Gx'' = Gx' * (100 - Sx') / (100 - Sx'')

    Parameters
    ----------
    gx_prime : float
        Specific gravity referenced to volume at moisture content x'.
    sx_prime_pct : float
        Percent volumetric shrinkage from green to x' (Eq 4-9).
    sx_double_prime_pct : float
        Percent volumetric shrinkage from green to x'' (Eq 4-9).

    Returns
    -------
    dict
        {'gx_prime', 'sx_prime_pct', 'sx_double_prime_pct',
         'gx_double_prime', 'equation': '4-10', ...}
    """
    gx2 = gx_prime * (100.0 - sx_prime_pct) / (100.0 - sx_double_prime_pct)
    return {
        "gx_prime": gx_prime, "sx_prime_pct": sx_prime_pct,
        "sx_double_prime_pct": sx_double_prime_pct, "gx_double_prime": gx2,
        "equation": "4-10", "printed_page": "4-11", "pdf_page": 104,
    }


def specific_gravity_from_basic(basic_specific_gravity, moisture_content_pct,
                                 volumetric_s0_pct=None, mc_fs=30.0):
    """Eq 4-11 (with S0 given) or Eq 4-13 (with S0 estimated from Gb via
    Eq 4-12): specific gravity Gx referenced to volume at moisture content
    x, below the fiber saturation point, computed from basic specific
    gravity Gb (printed p. 4-12).

        Eq 4-11: Gx = Gb / (1 - Sx/100), with Sx from Eq 4-9
        Eq 4-13: Gx = Gb / [1 - 0.265*Gb*(1 - x/MCfs)]  (S0 = 26.5*Gb, Eq 4-12)

    Parameters
    ----------
    basic_specific_gravity : float
        Gb, ovendry mass / green volume.
    moisture_content_pct : float
        x, moisture content (%) at which Gx is wanted (<= mc_fs).
    volumetric_s0_pct : float, optional
        S0, percent volumetric shrinkage from green to ovendry (Table 4-3).
        If omitted, S0 is estimated from Gb via Eq 4-12 (S0 = 26.5*Gb),
        giving the closed-form Eq 4-13.
    mc_fs : float, optional
        Fiber saturation point (%, default 30).

    Returns
    -------
    dict
        {'basic_specific_gravity', 'moisture_content_pct', 'gx',
         'equation': '4-11' or '4-13', ...}
    """
    if volumetric_s0_pct is not None:
        sx = shrinkage_at_moisture_content(volumetric_s0_pct, moisture_content_pct, mc_fs)["shrinkage_pct"]
        gx = basic_specific_gravity / (1.0 - sx / 100.0)
        equation = "4-11"
    else:
        gx = basic_specific_gravity / (
            1.0 - 0.265 * basic_specific_gravity * (1.0 - moisture_content_pct / mc_fs)
        )
        equation = "4-13"
    return {
        "basic_specific_gravity": basic_specific_gravity,
        "moisture_content_pct": moisture_content_pct, "gx": gx,
        "equation": equation, "printed_page": "4-12", "pdf_page": 105,
    }


def estimate_total_shrinkage_from_basic_sg(basic_specific_gravity):
    """Eq 4-12: estimate total volumetric shrinkage S0 (green to ovendry,
    %) from basic specific gravity when S0 is not known for the species
    (Stamm 1964) (printed p. 4-12).

        S0 = 26.5 * Gb

    Parameters
    ----------
    basic_specific_gravity : float
        Gb, ovendry mass / green volume.

    Returns
    -------
    dict
        {'basic_specific_gravity', 's0_pct', 'equation': '4-12', ...}
    """
    s0 = 26.5 * basic_specific_gravity
    return {
        "basic_specific_gravity": basic_specific_gravity, "s0_pct": s0,
        "equation": "4-12", "printed_page": "4-12", "pdf_page": 105,
    }


# ============================================================================
# Eq 4-14 to 4-16 -- Density at any moisture content
# (printed pp. 4-12 to 4-13, pdf_page 105-106)
# ============================================================================

RHO_WATER_KG_M3 = 1000.0


def density_from_specific_gravity(gx, moisture_content_pct,
                                   rho_water=RHO_WATER_KG_M3):
    """Eq 4-14 (Method 1): density (including water) at moisture content x,
    from specific gravity Gx referenced to volume at that same MC
    (printed p. 4-12).

        rho_x = rho_w * Gx * (1 + x/100)

    Parameters
    ----------
    gx : float
        Specific gravity referenced to volume at moisture content x (e.g.
        from ``specific_gravity_from_basic``).
    moisture_content_pct : float
        x (%).
    rho_water : float, optional
        Density of water (kg/m^3, default 1000).

    Returns
    -------
    dict
        {'gx', 'moisture_content_pct', 'density_kg_m3', 'equation': '4-14', ...}
    """
    rho_x = rho_water * gx * (1.0 + moisture_content_pct / 100.0)
    return {
        "gx": gx, "moisture_content_pct": moisture_content_pct,
        "density_kg_m3": rho_x, "equation": "4-14",
        "printed_page": "4-12", "pdf_page": 105,
    }


def density_from_ovendry_density(rho_0, moisture_content_pct, s0_pct,
                                  mc_fs=30.0):
    """Eq 4-15 (Method 2): density (including water) at moisture content x,
    from ovendry density rho_0 (printed p. 4-13).

        rho_x = rho_0 * (1 + x/100) * (100 - S0) / (100 - Sx)

    with Sx from Equation (4-9).

    Parameters
    ----------
    rho_0 : float
        Ovendry density (ovendry mass / ovendry volume, kg/m^3).
    moisture_content_pct : float
        x (%), <= mc_fs.
    s0_pct : float
        S0, percent volumetric shrinkage green-to-ovendry (Table 4-3, or
        ``estimate_total_shrinkage_from_ovendry_density``).
    mc_fs : float, optional
        Fiber saturation point (%, default 30).

    Returns
    -------
    dict
        {'rho_0', 'moisture_content_pct', 's0_pct', 'density_kg_m3',
         'equation': '4-15', ...}
    """
    sx = shrinkage_at_moisture_content(s0_pct, moisture_content_pct, mc_fs)["shrinkage_pct"]
    rho_x = rho_0 * (1.0 + moisture_content_pct / 100.0) * (100.0 - s0_pct) / (100.0 - sx)
    return {
        "rho_0": rho_0, "moisture_content_pct": moisture_content_pct,
        "s0_pct": s0_pct, "density_kg_m3": rho_x, "equation": "4-15",
        "printed_page": "4-13", "pdf_page": 106,
    }


def estimate_total_shrinkage_from_ovendry_density(rho_0, rho_water=RHO_WATER_KG_M3):
    """Eq 4-16: estimate total volumetric shrinkage S0 (%) from ovendry
    density, the ovendry-density form of Equation (4-12) (printed p. 4-13).

        S0 = 26.5*rho_0 / (rho_w + 0.265*rho_0)

    Parameters
    ----------
    rho_0 : float
        Ovendry density (kg/m^3).
    rho_water : float, optional
        Density of water (kg/m^3, default 1000).

    Returns
    -------
    dict
        {'rho_0', 's0_pct', 'equation': '4-16', ...}
    """
    s0 = 26.5 * rho_0 / (rho_water + 0.265 * rho_0)
    return {
        "rho_0": rho_0, "s0_pct": s0, "equation": "4-16",
        "printed_page": "4-13", "pdf_page": 106,
    }


# ============================================================================
# Eq 4-17 -- Thermal conductivity across the grain (printed p. 4-13)
# ============================================================================

def thermal_conductivity(gx, moisture_content_pct):
    """Eq 4-17: approximate thermal conductivity k (W/(m*K)) across the
    grain, for Gx > 0.3, temperatures around 24 degC, and MC < 25%
    (printed p. 4-13).

        k = Gx*(B + C*x) + A
        A = 0.01864, B = 0.1941, C = 0.004064   (k in W/(m*K))

    Parameters
    ----------
    gx : float
        Specific gravity based on ovendry mass and volume at moisture
        content x.
    moisture_content_pct : float
        x (%), < 25.

    Returns
    -------
    dict
        {'gx', 'moisture_content_pct', 'k_w_per_mK', 'equation': '4-17', ...}
    """
    a, b, c = 0.01864, 0.1941, 0.004064
    k = gx * (b + c * moisture_content_pct) + a
    return {
        "gx": gx, "moisture_content_pct": moisture_content_pct,
        "k_w_per_mK": k, "equation": "4-17",
        "printed_page": "4-13", "pdf_page": 106,
    }
