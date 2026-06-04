"""Tests for GEC-9 figures module (FHWA-HIF-18-031).

GEC-9 figures are graphical charts handled by the figure-catalog vision tools.
This test file verifies the module is importable and has the expected structure.
"""

import geotech_references.gec_9.figures as gec9_figs


def test_figures_module_importable():
    assert gec9_figs is not None


def test_figures_module_has_docstring():
    assert gec9_figs.__doc__ is not None
    assert len(gec9_figs.__doc__) > 0
