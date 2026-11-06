"""REF-12: the AASHTO 1993 esal_* lookups read the full Appendix D tables.

The four ``tables.esal_*`` functions used to hold only the SN = 5 / D = 9 in,
pt = 2.5 columns (Tables D.4, D.5, D.13, D.14) and refused anything else.
They now read ``lef.load_equivalency_factor``. The values below are what the
former functions returned (their own digitized curves, linear in load,
clamped at the printed ends), captured before the change; they must not move.
"""

import pytest

from geotech_references.aashto_1993 import lef
from geotech_references.aashto_1993 import tables as tb

# (axle load kips, LEF) returned before REF-12 at SN = 5 / D = 9 in, pt = 2.5.
FS = [(1, 0.0002), (2, 0.0002), (3, 0.0011), (7, 0.022), (9, 0.061),
      (12, 0.189), (15, 0.4915), (18, 1.0), (21, 1.845), (25, 3.56),
      (30, 7.0), (33, 10.05), (41, 23.35), (47, 40.85), (49, 48.75),
      (50, 53), (55, 53)]
FT = [(1, 0.0), (2, 0.0), (3, 0.0001), (9, 0.005), (17, 0.062),
      (25, 0.312), (33, 0.9735), (36, 1.38), (45, 3.275), (57, 7.9),
      (67, 14.55), (79, 27.6), (89, 44.7), (90, 46.8), (95, 46.8)]
RS = [(1, 0.0002), (2, 0.0002), (3, 0.0011), (7, 0.021), (9, 0.057),
      (12, 0.176), (15, 0.4725), (18, 1.0), (21, 1.955), (25, 4.015),
      (30, 8.28), (33, 12.15), (41, 29.25), (47, 52.05), (49, 62.3),
      (50, 67.8), (55, 67.8)]
RT = [(1, 0.0001), (2, 0.0001), (3, 0.0003), (9, 0.009), (17, 0.1075),
      (25, 0.533), (33, 1.705), (36, 2.43), (45, 6.005), (57, 15.25),
      (67, 29.45), (79, 59.3), (89, 100.0), (90, 105), (95, 105)]


@pytest.mark.parametrize("load,lef_before", FS)
def test_flexible_single_sn5_unchanged(load, lef_before):
    r = tb.esal_flexible_single_axle(float(load))
    assert r["lef"] == lef_before
    assert r["table"] == "Table D.4"


@pytest.mark.parametrize("load,lef_before", FT)
def test_flexible_tandem_sn5_unchanged(load, lef_before):
    r = tb.esal_flexible_tandem_axle(float(load))
    assert r["lef"] == lef_before
    assert r["table"] == "Table D.5"


@pytest.mark.parametrize("load,lef_before", RS)
def test_rigid_single_d9_unchanged(load, lef_before):
    r = tb.esal_rigid_single_axle(float(load))
    assert r["lef"] == lef_before
    assert r["table"] == "Table D.13"


@pytest.mark.parametrize("load,lef_before", RT)
def test_rigid_tandem_d9_unchanged(load, lef_before):
    r = tb.esal_rigid_tandem_axle(float(load))
    assert r["lef"] == lef_before
    assert r["table"] == "Table D.14"


def test_return_keys_kept_and_table_added():
    r = tb.esal_flexible_single_axle(18.0)
    assert set(r) == {"axle_load_kips", "sn", "pt", "lef", "table",
                      "reference"}
    r = tb.esal_rigid_tandem_axle(36.0)
    assert set(r) == {"axle_load_kips", "d_in", "pt", "lef", "table",
                      "reference"}


def test_spot_checks_off_the_printed_page():
    # Read off the rendered scan of docs/aashto1993.pdf:
    # Table D.4 (pdf_page 365, printed D-6), SN = 5: 12 kips 189 -> 0.189,
    # 30 kips 7 0 -> 7.0; Table D.5 (pdf_page 366, printed D-7), SN = 5:
    # 36 kips 1 38 -> 1.38, SN = 3 at 40 kips 2 06 -> 2.06.
    assert tb.esal_flexible_single_axle(12.0)["lef"] == 0.189
    assert tb.esal_flexible_single_axle(30.0)["lef"] == 7.0
    assert tb.esal_flexible_tandem_axle(36.0)["lef"] == 1.38
    assert tb.esal_flexible_tandem_axle(40.0, sn=3.0)["lef"] == 2.06


@pytest.mark.parametrize("pt,table", [(2.0, "Table D.1"), (2.5, "Table D.4"),
                                      (3.0, "Table D.7")])
def test_flexible_single_each_pt(pt, table):
    for sn in (1, 2, 3, 4, 5, 6, 2.5):
        r = tb.esal_flexible_single_axle(22.0, sn=sn, pt=pt)
        expected = lef.load_equivalency_factor("flexible", "single", 22.0,
                                               sn=sn, pt=pt)
        assert r["lef"] == expected["lef"]
        assert r["table"] == table


@pytest.mark.parametrize("pt,table", [(2.0, "Table D.11"),
                                      (2.5, "Table D.14"),
                                      (3.0, "Table D.17")])
def test_rigid_tandem_each_pt(pt, table):
    for d in (6, 7, 8, 9, 10, 11, 12, 13, 14, 8.5):
        r = tb.esal_rigid_tandem_axle(50.0, d_in=d, pt=pt)
        expected = lef.load_equivalency_factor("rigid", "tandem", 50.0,
                                               d_in=d, pt=pt)
        assert r["lef"] == expected["lef"]
        assert r["table"] == table


def test_flexible_tandem_and_rigid_single_other_columns():
    assert tb.esal_flexible_tandem_axle(40.0, sn=2.0, pt=3.0)["table"] == \
        "Table D.8"
    assert tb.esal_rigid_single_axle(30.0, d_in=12.0, pt=2.0)["table"] == \
        "Table D.10"


def test_clamped_column_carries_lef_note():
    r = tb.esal_flexible_single_axle(18.0, sn=7.0)
    assert "note" in r and "clamped" in r["note"]
    r = tb.esal_rigid_single_axle(60.0)
    assert "note" in r and "clamped" in r["note"]


@pytest.mark.parametrize("call,kw", [
    (tb.esal_flexible_single_axle, {"pt": 2.2}),
    (tb.esal_flexible_tandem_axle, {"sn": 0.0}),
    (tb.esal_rigid_single_axle, {"pt": 4.0}),
    (tb.esal_rigid_tandem_axle, {"d_in": -1.0}),
])
def test_refused_with_lefs_message(call, kw):
    pav = "flexible" if "flexible" in call.__name__ else "rigid"
    axle = "single" if "single" in call.__name__ else "tandem"
    lef_kw = dict(kw)
    lef_kw.setdefault("pt", 2.5)
    if pav == "flexible":
        lef_kw.setdefault("sn", 5.0)
    else:
        lef_kw.setdefault("d_in", 9.0)
    with pytest.raises(ValueError) as want:
        lef.load_equivalency_factor(pav, axle, 18.0, **lef_kw)
    with pytest.raises(ValueError) as got:
        call(18.0, **kw)
    assert str(got.value) == str(want.value)


def test_zero_load_refused_with_lefs_message():
    with pytest.raises(ValueError, match="axle_load_kips must be > 0"):
        tb.esal_rigid_tandem_axle(0.0)
