"""NOAA Frost Protected Shallow Foundations.

Provides:
  - Frost depth estimation (Stefan equation, modified Berggren method)
  - Soil thermal property tables (conductivity, latent heat, heat capacity)
  - Surface n-factor conversion tables
  - Simplified frost depth by soil type

Usage::

    from geotech_references.noaa_frost.equations import stefan_frost_depth_m
    from geotech_references.noaa_frost.tables import table_soil_thermal_conductivity
"""
