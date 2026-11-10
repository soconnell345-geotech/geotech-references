"""struct-05: every public em_2104 function documents each parameter on its
own numpydoc line, with the unit for strengths and lengths.

The app's helper is shown only a function's first paragraph and the
per-parameter descriptions it parses from "name : type" lines; a grouped
line ("b, d : float") gave it nothing. The flexure and design equations
take f'c and fy in ksi (the manual's worked examples, e.g. Appendix C-4,
EM_1110-2-2104_2025.pdf pdf 63 / printed 57: f'c = 4.0 ksi, fy = 60 ksi;
the code's default Es is 29,000 ksi) and the shear equations f'c in psi
(paragraph 5-4, pdf 43 / printed 37: "... sqrt(f'c) bd lbs").
"""

import inspect

import pytest

from geotech_references.em_2104 import (
    design, flexure_axial, loads, reinforcement, serviceability, shear,
)

MODULES = (design, flexure_axial, loads, reinforcement, serviceability, shear)


def _public_functions():
    for mod in MODULES:
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if fn.__module__ == mod.__name__ and not name.startswith("_"):
                yield f"{mod.__name__.rsplit('.', 1)[-1]}.{name}", fn


def _param_lines(fn):
    """{name: description} from the numpydoc Parameters section."""
    doc = inspect.getdoc(fn) or ""
    out, current, inside = {}, None, False
    for line in doc.splitlines():
        s = line.strip()
        if s.lower() == "parameters":
            inside = True
            continue
        if s.lower() in ("returns", "raises", "notes", "examples", "references"):
            inside = False
            continue
        if not inside or s.startswith("---"):
            continue
        if " : " in s:
            current = s.split(" : ")[0].strip()
            out[current] = ""
        elif current and s:
            out[current] = (out[current] + " " + s).strip()
    return out


FUNCTIONS = sorted(_public_functions())


@pytest.mark.parametrize("qualname,fn", FUNCTIONS, ids=[q for q, _ in FUNCTIONS])
def test_every_parameter_described(qualname, fn):
    described = _param_lines(fn)
    for p in inspect.signature(fn).parameters.values():
        if p.kind in (p.VAR_KEYWORD, p.VAR_POSITIONAL):
            continue
        assert described.get(p.name), f"{qualname}: no description for {p.name!r}"


@pytest.mark.parametrize("qualname,fn", FUNCTIONS, ids=[q for q, _ in FUNCTIONS])
def test_strengths_and_lengths_name_a_unit(qualname, fn):
    described = _param_lines(fn)
    units = {"fc_prime": ("ksi", "psi", "MPa"), "fy": ("ksi", "psi", "MPa"),
             "b": ("in.", "mm"), "d": ("in.", "mm"), "h": ("in.", "mm"),
             "dprime": ("in.",), "ag": ("sq in", "in^2"), "as_": ("sq in",),
             "mn": ("kip-in", "in-kip"), "pn": ("kips",), "nu": ("lbs", "N ")}
    for p in inspect.signature(fn).parameters:
        if p in units and p in described:
            assert any(u in described[p] for u in units[p]), (
                f"{qualname}: {p!r} names no unit: {described[p]!r}")


def test_flexure_in_ksi_shear_in_psi():
    # Appendix C-4 (printed p. 57) works in ksi; Eq 5-2 (printed p. 37) in psi.
    assert "ksi" in _param_lines(flexure_axial.tension_controlled_capacity_singly)["fc_prime"]
    assert "psi" in _param_lines(shear.shear_capacity_special_straight_member)["fc_prime"]
    assert "Not MPa" in _param_lines(flexure_axial.aci_beta1)["fc_prime"]


def test_kb_cites_its_printed_page():
    # Eq 4-3 is printed on p. 30 (EM_1110-2-2104_2025.pdf pdf 36), not p. 29.
    r = flexure_axial.balanced_strain_kb(beta1=0.85, fy=60.0)
    assert r["printed_page"] == "30"
    assert r["kb"] == pytest.approx(0.85 * 87.0 / (87.0 + 60.0))


def test_eccentricity_cites_both_printed_pages():
    # Eq 4-1 is printed on p. 29 (EM_1110-2-2104_2025.pdf pdf 35) and
    # Eq 4-2 on p. 30 (pdf 36); the function cited p. 29 for both.
    r = flexure_axial.eccentricity_ratio(mu=1200.0, pu=50.0, d=16.0, h=20.0)
    assert r["printed_page"] == "29-30"
    assert r["e_prime"] == pytest.approx(1200.0 / 50.0 + (16.0 - 10.0))
