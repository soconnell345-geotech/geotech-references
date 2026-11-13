"""Tests for GEC-11 table lookup functions."""

import math

import pytest

from geotech_references.gec_11.tables import (
    table_2_1_min_reinforcement_length,
    table_2_2_min_embedment_depth,
    table_3_1_select_fill_gradation,
    table_3_3_electrochemical_steel,
    table_3_4_electrochemical_geosynth,
    table_3_6_pullout_parameters,
    table_3_7_galvanization,
    table_3_8_corrosion_rates,
    table_3_9_installation_damage,
    table_3_11_pet_durability,
    table_4_1_load_combinations,
    table_4_2_permanent_load_factors,
    table_4_4_traffic_surcharge,
    table_4_5_external_resistance,
    table_4_6_bearing_capacity_factors,
    table_4_7_internal_resistance,
)


# ============================================================================
# Table 2-1: Minimum Reinforcement Length
# ============================================================================

class TestTable21:
    """Tests for table_2_1_min_reinforcement_length()."""

    def test_rows_as_printed(self):
        """FHWA-NHI-10-024 Vol I Table 2-1, p. 2-43 (PDF page 83): three
        cases. The code held two seismic rows (0.8 'low', 1.1 'moderate to
        high') and an 8 ft minimum on every row (review finding gec-21)."""
        rows = [(r["condition"], r["typical_min_L_over_H"],
                 r["L_over_H_low"], r["L_over_H_high"])
                for r in table_2_1_min_reinforcement_length()]
        assert rows == [
            ("Static loading with or without traffic surcharge", "0.7", 0.7, 0.7),
            ("Sloping backfill surcharge", "0.8", 0.8, 0.8),
            ("Seismic loading", "0.8 to 1.1", 0.8, 1.1),
        ]
        for r in table_2_1_min_reinforcement_length():
            assert "min_length_ft" not in r and "min_length_m" not in r

    def test_static_row_print_note(self):
        """Table 2-1, p. 2-43 (PDF page 83), prints 'Static loading with or
        with traffic surcharge' (independent check)."""
        r = table_2_1_min_reinforcement_length("static")[0]
        assert "with or with traffic surcharge" in r["print_note"]
        others = table_2_1_min_reinforcement_length()[1:]
        assert all("print_note" not in o for o in others)

    def test_refusal_does_not_call_labels_printed(self):
        with pytest.raises(ValueError) as e:
            table_2_1_min_reinforcement_length("wind")
        assert "Printed rows" not in str(e.value)
        assert "not all worded as printed" in str(e.value)

    def test_static(self):
        results = table_2_1_min_reinforcement_length("static")
        assert len(results) == 1
        assert results[0]["L_over_H_low"] == 0.7

    def test_sloping(self):
        results = table_2_1_min_reinforcement_length("sloping")
        assert len(results) == 1
        assert results[0]["L_over_H_low"] == 0.8

    def test_seismic(self):
        results = table_2_1_min_reinforcement_length("seismic")
        assert len(results) == 1
        assert results[0]["typical_min_L_over_H"] == "0.8 to 1.1"

    def test_no_match(self):
        """A filter that matches no printed case is refused, naming the
        cases (review finding gec-37: it returned [])."""
        with pytest.raises(ValueError, match="Seismic loading"):
            table_2_1_min_reinforcement_length("nonexistent")


# ============================================================================
# Table 2-2: Minimum Embedment Depth
# ============================================================================

class TestTable22:
    """Tests for table_2_2_min_embedment_depth()."""

    def test_all_entries(self):
        results = table_2_2_min_embedment_depth()
        assert len(results) == 5

    def test_horizontal(self):
        results = table_2_2_min_embedment_depth("horizontal")
        assert len(results) == 2

    def test_abutment(self):
        results = table_2_2_min_embedment_depth("abutment")
        assert len(results) == 1
        assert results[0]["ratio_value"] == pytest.approx(0.1)

    def test_slope_2h_1v(self):
        results = table_2_2_min_embedment_depth("2H:1V")
        assert len(results) == 1
        assert results[0]["ratio_value"] == pytest.approx(1 / 7)

    def test_slope_1_5h_1v(self):
        results = table_2_2_min_embedment_depth("1.5H:1V")
        assert len(results) == 1
        assert results[0]["ratio_value"] == pytest.approx(0.2)

    def test_no_match(self):
        """'2:1 slope' is not how Table 2-2 (p. 2-43) names its rows; the
        refusal lists them (gec-37)."""
        with pytest.raises(ValueError, match="Slopes 2H:1V"):
            table_2_2_min_embedment_depth("2:1 slope")

    def test_footnote(self):
        """Table 2-2, p. 2-43: '* Minimum depth is the greater of applicable
        values listed, frost depth, or scour depth.'"""
        for r in table_2_2_min_embedment_depth():
            assert "frost depth, or scour depth" in r["notes"]


# ============================================================================
# Table 3-1: Select Fill Gradation
# ============================================================================

class TestTable31:
    """Tests for table_3_1_select_fill_gradation()."""

    def test_returns_dict(self):
        result = table_3_1_select_fill_gradation()
        assert isinstance(result, dict)

    def test_has_gradation(self):
        result = table_3_1_select_fill_gradation()
        assert "gradation" in result
        assert len(result["gradation"]) == 3

    def test_pi_max(self):
        result = table_3_1_select_fill_gradation()
        assert result["PI_max"] == 6

    def test_no_200_limit(self):
        result = table_3_1_select_fill_gradation()
        no200 = [g for g in result["gradation"] if "200" in g["sieve"]]
        assert len(no200) == 1
        assert no200[0]["percent_passing_max"] == 15


# ============================================================================
# Table 3-3: Electrochemical Limits for Steel
# ============================================================================

class TestTable33:
    """Tests for table_3_3_electrochemical_steel()."""

    def test_returns_dict(self):
        result = table_3_3_electrochemical_steel()
        assert isinstance(result, dict)

    def test_resistivity(self):
        result = table_3_3_electrochemical_steel()
        assert result["resistivity_min_ohm_cm"] == 3000

    def test_ph_range(self):
        result = table_3_3_electrochemical_steel()
        assert result["pH_min"] == 5.0
        assert result["pH_max"] == 10.0

    def test_chlorides(self):
        result = table_3_3_electrochemical_steel()
        assert result["chlorides_max_ppm"] == 100

    def test_sulfates(self):
        result = table_3_3_electrochemical_steel()
        assert result["sulfates_max_ppm"] == 200


# ============================================================================
# Table 3-4: Electrochemical Limits for Geosynthetics
# ============================================================================

class TestTable34:
    """Tests for table_3_4_electrochemical_geosynth()."""

    def test_rows_as_printed(self):
        """FHWA-NHI-10-024 Vol I Table 3-4, p. 3-10 (PDF page 102): two rows.
        The print's own row name 'polyolefin' returned [] (gec-37)."""
        rows = [(r["polymer"], r["criteria"], r["test_method"])
                for r in table_3_4_electrochemical_geosynth()]
        assert rows == [
            ("Polyester (PET)", "3 < pH < 9", "AASHTO T-289"),
            ("Polyolefin (PP & HDPE)", "pH > 3", "AASHTO T-289"),
        ]
        assert table_3_4_electrochemical_geosynth("polyolefin")[0]["pH_max"] is None

    def test_pet(self):
        results = table_3_4_electrochemical_geosynth("PET")
        assert len(results) == 1
        assert results[0]["pH_min"] == 3.0
        assert results[0]["pH_max"] == 9.0

    def test_pp(self):
        results = table_3_4_electrochemical_geosynth("PP")
        assert len(results) == 1
        assert results[0]["polymer"] == "Polyolefin (PP & HDPE)"
        assert results[0]["pH_min"] == 3.0
        assert results[0]["pH_max"] is None

    def test_hdpe(self):
        results = table_3_4_electrochemical_geosynth("HDPE")
        assert len(results) == 1
        assert results[0]["polymer"] == "Polyolefin (PP & HDPE)"

    def test_no_match(self):
        with pytest.raises(ValueError, match="Polyolefin"):
            table_3_4_electrochemical_geosynth("PVC")


# ============================================================================
# Table 3-6: Pullout Capacity Parameters
# ============================================================================

class TestTable36:
    """Tests for table_3_6_pullout_parameters(), pinned to the printed Table
    3-6 (FHWA-NHI-10-024 Vol I, p. 3-17) and Section 3.4.2 (pp. 3-16, 3-20,
    3-21; REF-42)."""

    def test_all_entries(self):
        results = table_3_6_pullout_parameters()
        assert len(results) == 5

    def test_original_keys_kept(self):
        for r in table_3_6_pullout_parameters():
            for k in ("reinforcement", "F_star_at_top", "F_star_at_6m",
                      "alpha", "notes"):
                assert k in r

    def test_ribbed(self):
        results = table_3_6_pullout_parameters("ribbed")
        assert len(results) == 1
        r = results[0]
        assert r["alpha"] == 1.0
        # Eq. 3-4 / 3-5: 1.2 + log Cu at the top (2.0 max), tan(phi) at 6 m
        assert r["F_star_at_top"] == "1.2 + log10(Cu), 2.0 maximum"
        assert r["F_star_at_6m"] == "tan(phi)"
        assert r["F_star_top_max"] == 2.0
        # Cu unknown -> Cu = 4 -> F* = 1.8 at the top (bold, p. 3-20)
        assert r["Cu_if_unknown"] == 4
        assert r["F_star_top_if_Cu_unknown"] == 1.8
        assert 1.2 + math.log10(4) == pytest.approx(1.8, abs=0.005)
        assert r["equations"] == ["3-4", "3-5"]

    def test_ribbed_is_not_tan_phi_at_all_depths(self):
        r = table_3_6_pullout_parameters("ribbed")[0]
        assert r["F_star_at_top"] != r["F_star_at_6m"]

    def test_smooth_strip_has_no_printed_default(self):
        r = table_3_6_pullout_parameters("smooth")[0]
        assert "0.4" not in r["F_star_at_top"]
        assert "no default printed" in r["F_star_at_top"]
        assert r["alpha"] == 1.0

    def test_steel_grid_equations_3_6_and_3_7(self):
        r = table_3_6_pullout_parameters("steel grid")[0]
        assert r["F_star_at_top"] == "20 * (t/St)"
        assert r["F_star_at_6m"] == "10 * (t/St)"
        assert r["alpha"] == 1.0
        assert r["equations"] == ["3-6", "3-7"]
        assert "24 in." in r["notes"]

    def test_geogrid(self):
        results = table_3_6_pullout_parameters("geogrid")
        assert len(results) == 1
        r = results[0]
        assert r["alpha"] == 0.8
        # Eq. 3-8: F* = (2/3) tan(phi) for geosynthetic sheets, no test data
        assert r["F_star_at_top"] == r["F_star_at_6m"] == "(2/3) * tan(phi)"
        assert r["equations"] == ["3-8"]

    def test_geotextile(self):
        results = table_3_6_pullout_parameters("geotextile")
        assert len(results) == 1
        r = results[0]
        assert r["alpha"] == 0.6
        assert r["F_star_at_top"] == r["F_star_at_6m"] == "(2/3) * tan(phi)"

    def test_note_i_on_every_row(self):
        for r in table_3_6_pullout_parameters():
            assert "Table 3-1" in r["default_fill_limit"]
            assert "Cu >= 4" in r["default_fill_limit"]
            assert "tests must be run" in r["default_fill_limit"]

    def test_no_match(self):
        with pytest.raises(ValueError, match="Table 3-6"):
            table_3_6_pullout_parameters("nonexistent")


# ============================================================================
# Table 3-7: Galvanization Thickness
# ============================================================================

class TestTable37:
    """Tests for table_3_7_galvanization()."""

    def test_returns_list(self):
        results = table_3_7_galvanization()
        assert isinstance(results, list)
        assert len(results) == 3

    def test_strip_thin(self):
        results = table_3_7_galvanization()
        thin = [r for r in results if "< 1/4" in r["component"]]
        assert len(thin) == 1
        assert thin[0]["thickness_um"] == 85

    def test_strip_thick(self):
        results = table_3_7_galvanization()
        thick = [r for r in results if ">= 1/4" in r["component"]]
        assert len(thick) == 1
        assert thick[0]["thickness_um"] == 100
        # p. 3-26 prints "> ¼ in."; the exact ¼ in. case is the library's
        assert '"> ¼ in."' in thick[0]["print_note"]

    def test_wire_row_carries_its_footnote(self):
        """p. 3-26: "Wire*" (all diameters) with "* For bar mats fabricated
        from uncoated steel wire.", the footnote as typed in the chapter
        text."""
        import json
        from pathlib import Path
        wire = [r for r in table_3_7_galvanization() if "Wire" in r["component"]]
        assert len(wire) == 1 and wire[0]["thickness_mils"] == 3.4
        assert wire[0]["footnote"] == "* For bar mats fabricated from uncoated steel wire."
        assert all(r["reference"].endswith("Table 3-7, p. 3-26")
                   for r in table_3_7_galvanization())
        ch3 = Path(__file__).resolve().parents[1] / "geotech_references" / \
            "gec_11" / "text" / "chapter03.json"
        body = ch3.read_text(encoding="utf-8")
        assert ("Wire* | All diameters | 3.4 mils (85 μm)\\n" + wire[0]["footnote"]) in body


# ============================================================================
# Table 3-8: Steel Corrosion Rates
# ============================================================================

class TestTable38:
    """Tests for table_3_8_corrosion_rates()."""

    def test_all_entries(self):
        results = table_3_8_corrosion_rates()
        assert len(results) == 3

    def test_zinc(self):
        results = table_3_8_corrosion_rates("zinc")
        assert len(results) == 2
        rates = {r["rate_um_per_yr"] for r in results}
        assert 15.0 in rates
        assert 4.0 in rates

    def test_carbon_steel(self):
        results = table_3_8_corrosion_rates("carbon")
        assert len(results) == 1
        assert results[0]["rate_um_per_yr"] == 12.0

    def test_no_match(self):
        with pytest.raises(ValueError, match="Carbon steel"):
            table_3_8_corrosion_rates("nonexistent")


# ============================================================================
# Table 3-9: Installation Damage Reduction Factors
# ============================================================================

class TestTable39:
    """Tests for table_3_9_installation_damage()."""

    def test_all_entries(self):
        results = table_3_9_installation_damage()
        assert len(results) == 7

    def test_hdpe(self):
        results = table_3_9_installation_damage("HDPE")
        assert len(results) == 1
        assert results[0]["backfill_type1_low"] == 1.20
        assert results[0]["backfill_type1_high"] == 1.45

    def test_slit_film(self):
        results = table_3_9_installation_damage("slit film")
        assert len(results) == 1
        assert results[0]["backfill_type1_high"] == 3.00

    def test_pvc(self):
        results = table_3_9_installation_damage("PVC")
        assert len(results) == 1

    def test_backfill_types_and_footnote_as_printed(self):
        """Table 3-9, p. 3-32 (PDF page 124): the column heads define the
        backfills (Type 2: max 3/4 in. (20 mm), D50 about #30); footnote a
        on the three geotextile rows. 'polyester geogrid' names no row and
        is refused (gec-37)."""
        rows = table_3_9_installation_damage()
        assert all("D50 about #30 (0.7 mm)" in r["type2_backfill"] for r in rows)
        assert all("4 in. (100 mm)" in r["type1_backfill"] for r in rows)
        assert [r["geosynthetic"] for r in rows if "notes" in r] == [
            "Woven geotextile (PP and PET)",
            "Non-woven geotextile (PP and PET)",
            "Slit film woven PP geotextile",
        ]
        with pytest.raises(ValueError, match="PVC coated PET geogrid"):
            table_3_9_installation_damage("polyester geogrid")

    def test_type2_lower_than_type1(self):
        """Type 2 (finer) backfill always causes less damage."""
        results = table_3_9_installation_damage()
        for entry in results:
            assert entry["backfill_type2_low"] <= entry["backfill_type1_low"]
            assert entry["backfill_type2_high"] <= entry["backfill_type1_high"]


# ============================================================================
# Table 3-11: PET Durability Reduction Factors
# ============================================================================

class TestTable311:
    """Tests for table_3_11_pet_durability()."""

    def test_all_entries(self):
        results = table_3_11_pet_durability()
        assert len(results) == 2

    def test_rows_as_printed(self):
        """GEC-11 Vol I Table 3-11, p. 3-36: both rows, labels and values."""
        rows = [(r["product"], r["pH_5_to_8"], r["pH_3_to_5_or_8_to_9"])
                for r in table_3_11_pet_durability()]
        assert rows == [
            ("Geotextiles (Mn < 20,000, 40 < CEG < 50)", 1.6, 2.0),
            ("Coated geogrids, Geotextiles (Mn > 25,000, CEG < 30)", 1.15, 1.3),
        ]

    def test_geotextile(self):
        """The print lists geotextiles in both rows (by Mn and CEG)."""
        results = table_3_11_pet_durability("geotextile")
        assert [(r["pH_5_to_8"], r["pH_3_to_5_or_8_to_9"])
                for r in results] == [(1.6, 2.0), (1.15, 1.3)]

    def test_geogrid(self):
        results = table_3_11_pet_durability("geogrid")
        assert len(results) == 1
        assert results[0]["pH_5_to_8"] == 1.15
        assert results[0]["pH_3_to_5_or_8_to_9"] == 1.3

    def test_no_match(self):
        with pytest.raises(ValueError, match="Table 3-11"):
            table_3_11_pet_durability("strip")


# ============================================================================
# Table 4-1: LRFD Load Combinations
# ============================================================================

class TestTable41:
    """Tests for table_4_1_load_combinations()."""

    def test_all_entries(self):
        results = table_4_1_load_combinations()
        assert len(results) == 4

    def test_strength_i(self):
        results = table_4_1_load_combinations("strength")
        assert len(results) == 1
        assert results[0]["LL_LS"] == 1.75

    def test_extreme_event(self):
        results = table_4_1_load_combinations("extreme")
        assert len(results) == 2

    def test_service(self):
        results = table_4_1_load_combinations("service")
        assert len(results) == 1
        assert results[0]["EH_ES_EV"] == 1.00

    def test_extreme_event_i_note_as_printed(self):
        """Table 4-1, p. 4-4 (PDF page 146) defines gamma_EQ and prints no
        typical range for it (the code said 0.0 to 0.50)."""
        row = table_4_1_load_combinations("extreme event i")[0]
        assert "0.50" not in row["notes"]
        assert "simultaneously with seismic loads" in row["notes"]
        with pytest.raises(ValueError, match="Service I"):
            table_4_1_load_combinations("strength ii")

    def test_cells_as_printed_dashes_kept(self):
        """Every cell agrees with Table 4-1 as typed in from p. 4-4 (the
        chapter text): the printed dashes are dashes, not 0.0."""
        import json
        from pathlib import Path
        ch4 = Path(__file__).resolve().parents[1] / "geotech_references" / \
            "gec_11" / "text" / "chapter04.json"
        body = "\n".join(s["body"] for s in json.loads(
            ch4.read_text(encoding="utf-8"))["sections"])
        typed = body.split("[Table 4-1, typed in from p. 4-4, row by row:]\n")[1]
        rows = [ln.split(" | ") for ln in typed.split("\n")[1:5]]
        sym = {"γp": "gamma_p", "γEQ": "gamma_EQ", "–": "–"}
        for printed, row in zip(rows, table_4_1_load_combinations()):
            assert printed[0] == row["limit_state"].upper()
            for cell, key in zip(printed[1:], ("EH_ES_EV", "LL_LS", "EQ", "CT")):
                expect = sym[cell] if cell in sym else float(cell)
                assert row[key] == expect, (row["limit_state"], key)
            assert "use one of these at a time" in row["print_note"]
        assert sum(r[k] == "–" for r in table_4_1_load_combinations()
                   for k in ("EQ", "CT")) == 6


# ============================================================================
# Table 4-2: Permanent Load Factors
# ============================================================================

class TestTable42:
    """Tests for table_4_2_permanent_load_factors()."""

    def test_all_entries(self):
        results = table_4_2_permanent_load_factors()
        assert len(results) == 5

    def test_dc(self):
        results = table_4_2_permanent_load_factors("DC")
        assert len(results) == 1
        assert results[0]["gamma_max"] == 1.25
        assert results[0]["gamma_min"] == 0.90

    def test_eh(self):
        results = table_4_2_permanent_load_factors("EH")
        assert len(results) == 1
        assert results[0]["gamma_max"] == 1.50

    def test_ev(self):
        results = table_4_2_permanent_load_factors("EV")
        assert len(results) == 2

    def test_es(self):
        results = table_4_2_permanent_load_factors("ES")
        assert len(results) == 1
        assert results[0]["gamma_max"] == 1.50
        assert results[0]["gamma_min"] == 0.75

    def test_printed_type_of_load(self):
        """Table 4-2, p. 4-4: 'EV: Vertical Earth Pressure' (two rows) was not
        found by its printed name (gec-37); unknown loads are refused."""
        rows = table_4_2_permanent_load_factors("vertical earth pressure")
        assert [(r["gamma_max"], r["gamma_min"]) for r in rows] == [
            (1.00, None), (1.35, 1.00)]
        assert "Retaining Walls and Abutments" in rows[1]["description"]
        with pytest.raises(ValueError, match="EV Overall Stability"):
            table_4_2_permanent_load_factors("live load")


# ============================================================================
# Table 4-4: Traffic Surcharge
# ============================================================================

class TestTable44:
    """Tests for table_4_4_traffic_surcharge()."""

    def test_full_table(self):
        result = table_4_4_traffic_surcharge()
        assert "table" in result
        assert len(result["table"]) == 3

    def test_abutments_only(self):
        """FHWA-NHI-10-024 Vol I Table 4-4, p. 4-17 (PDF page 159) is for
        abutments perpendicular to traffic; p. 4-16 (PDF page 158) gives
        heq = 2.0 ft for walls parallel to traffic. The function took a
        'wall height' and said neither (review finding gec-20)."""
        result = table_4_4_traffic_surcharge(abutment_height_ft=10.0)
        assert result["h_eq_ft"] == 3.0
        assert "perpendicular to traffic" in result["applies_to"]
        assert "parallel to traffic: heq = 2.0 ft" in result["print_note"]
        assert "note" not in result
        assert "perpendicular" in table_4_4_traffic_surcharge()["applies_to"]

    def test_5ft_wall(self):
        result = table_4_4_traffic_surcharge(5.0)
        assert result["h_eq_ft"] == 4.0

    def test_10ft_wall(self):
        result = table_4_4_traffic_surcharge(10.0)
        assert result["h_eq_ft"] == 3.0

    def test_20ft_wall(self):
        result = table_4_4_traffic_surcharge(20.0)
        assert result["h_eq_ft"] == 2.0

    def test_interpolated(self):
        """15 ft wall should interpolate between 3.0 and 2.0."""
        result = table_4_4_traffic_surcharge(15.0)
        assert result["h_eq_ft"] == 2.5

    def test_short_wall(self):
        """Below the 5.0 ft row the table has no row; the 5.0 ft row (4.0 ft)
        is used and the result says so (gec-20)."""
        result = table_4_4_traffic_surcharge(3.0)
        assert result["h_eq_ft"] == 4.0
        assert "no row below an abutment height of 5.0 ft" in result["note"]

    def test_tall_wall(self):
        """Walls taller than 20 ft use 2.0 ft."""
        result = table_4_4_traffic_surcharge(30.0)
        assert result["h_eq_ft"] == 2.0


# ============================================================================
# Table 4-5: External Stability Resistance Factors
# ============================================================================

class TestTable45:
    """Tests for table_4_5_external_resistance()."""

    def test_all_entries(self):
        results = table_4_5_external_resistance()
        assert len(results) == 4

    def test_bearing(self):
        results = table_4_5_external_resistance("bearing")
        assert len(results) == 1
        assert results[0]["phi_factor"] == 0.65

    def test_sliding(self):
        results = table_4_5_external_resistance("sliding")
        assert len(results) == 1
        assert results[0]["phi_factor"] == 1.0

    def test_global(self):
        results = table_4_5_external_resistance("global")
        assert len(results) == 2
        phi_vals = {r["phi_factor"] for r in results}
        assert 0.75 in phi_vals
        assert 0.65 in phi_vals

    def test_conditions_as_printed(self):
        """Table 4-5, p. 4-19 (PDF page 161): 0.65 also where the slope
        contains or supports a structural element (the code's note said
        only 'limited subsurface data'). 'eccentricity' is not in the
        table and is refused (gec-37)."""
        rows = table_4_5_external_resistance("structural element")
        assert len(rows) == 2
        low = [r for r in rows if r["phi_factor"] == 0.65][0]
        assert "contains or supports a structural element" in low["condition"]
        with pytest.raises(ValueError, match="Sliding"):
            table_4_5_external_resistance("eccentricity")


# ============================================================================
# Table 4-6: Bearing Capacity Factors
# ============================================================================

class TestTable46:
    """Tests for table_4_6_bearing_capacity_factors()."""

    def test_full_table(self):
        result = table_4_6_bearing_capacity_factors()
        assert "table" in result
        assert len(result["table"]) == 46

    def test_phi_0(self):
        """Row 0 as printed on p. 4-29 (Nc to two decimals there)."""
        result = table_4_6_bearing_capacity_factors(0)
        assert (result["Nc"], result["Nq"], result["Ngamma"]) == (5.14, 1.0, 0.0)

    def test_phi_30(self):
        """Row 30 as printed on p. 4-29."""
        result = table_4_6_bearing_capacity_factors(30)
        assert (result["Nc"], result["Nq"], result["Ngamma"]) == (30.1, 18.4, 22.4)

    def test_phi_45(self):
        """Row 45 as printed on p. 4-29."""
        result = table_4_6_bearing_capacity_factors(45)
        assert (result["Nc"], result["Nq"], result["Ngamma"]) == (133.9, 134.9, 271.8)

    def test_interpolation(self):
        """phi = 32.5 lies between the printed rows 32 (35.5, 23.2, 30.2) and
        33 (38.6, 26.1, 35.2); the result is rounded to one decimal."""
        result = table_4_6_bearing_capacity_factors(32.5)
        assert (result["Nc"], result["Nq"], result["Ngamma"]) == (37.1, 24.7, 32.7)
        result = table_4_6_bearing_capacity_factors(38.5)
        assert (result["Nc"], result["Nq"], result["Ngamma"]) == (64.7, 52.5, 85.2)

    def test_cells_are_the_typed_table(self):
        """Every cell equals the typed Table 4-6 in the chapter text (p. 4-29)
        except Nc at phi = 39 (printed 37.9, the library's 67.9)."""
        import json
        import pathlib
        from geotech_references.gec_11 import tables
        path = pathlib.Path(tables.__file__).parent / "text" / "chapter04.json"
        sections = json.loads(path.read_text(encoding="utf-8"))["sections"]
        body = next(s["body"] for s in sections if s["section_id"] == "4.4.6.c")
        head = "[Table 4-6, typed in from p. 4-29, row by row:]\nφ | Nc | Nq | Nγ\n"
        lines = body.split(head, 1)[1].split("\n")[:46]
        printed = {int(r.split(" | ")[0]): [float(v) for v in r.split(" | ")[1:]]
                   for r in lines}
        assert sorted(printed) == list(range(46))
        differ = []
        for row in table_4_6_bearing_capacity_factors()["table"]:
            got = [row["Nc"], row["Nq"], row["Ngamma"]]
            if got != printed[row["phi_deg"]]:
                differ.append((row["phi_deg"], got, printed[row["phi_deg"]]))
        assert differ == [(39, [67.9, 56.0, 92.3], [37.9, 56.0, 92.3])]

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError, match="between 0 and 45"):
            table_4_6_bearing_capacity_factors(-5)
        with pytest.raises(ValueError, match="between 0 and 45"):
            table_4_6_bearing_capacity_factors(50)

    def test_phi_39_misprint_note(self):
        """p. 4-29 prints Nc = 37.9 at phi = 39; the lookup returns 67.9 and
        says, wherever the phi = 39 row is used, that 67.9 is not printed and
        where it comes from.

        The counts in the note were measured on 2026-11-12 by a script
        comparing the relation Nq = e^(pi tan phi) tan^2(45 + phi/2),
        Nc = (Nq - 1) cot(phi) with the printed cells, each rounded half up
        to the printed decimal: Nq 46 of 46; Nc 43 of 46 (phi 39: 67.867
        against the printed 37.9; phi 10: 8.345 against 8.4; phi 23: 18.049
        against 18.1). Midpoint of the printed neighbours 61.4 and 75.3:
        68.35."""
        result = table_4_6_bearing_capacity_factors(39)
        assert result["Nc"] == 67.9
        note = result["note"]
        for phrase in (
            "Table 4-6 (p. 4-29) prints Nc = 37.9 at phi = 39, which cannot be "
            "right between 61.4 at 38 and 75.3 at 40",
            "This function returns 67.9",
            "That value is NOT printed in the manual",
            "Nc = (Nq - 1) cot(phi), with Nq = e^(pi tan phi) tan^2(45 + phi/2), "
            "gives at 39 (67.87)",
            "The manual does not print that relation; it names AASHTO (2007) "
            "Table 10.6.3.1.2a-1 as the table's source",
            "reproduces all 46 printed Nq cells and 43 of the other 45 printed "
            "Nc cells to the printed decimal",
            "phi 10: 8.345 against the printed 8.4; phi 23: 18.049 against 18.1",
            "0.1 off in the last digit, as rounding twice would give",
            "Straight-line interpolation between the printed neighbours would "
            "give 68.4",
        ):
            assert phrase in note, phrase
        assert table_4_6_bearing_capacity_factors(38.5)["note"] == note
        assert table_4_6_bearing_capacity_factors(39.5)["note"] == note
        assert note in table_4_6_bearing_capacity_factors()["note"]
        for phi in (30, 38, 40):
            assert "note" not in table_4_6_bearing_capacity_factors(phi)
        assert note in " ".join(table_4_6_bearing_capacity_factors.__doc__.split())

    def test_phi_31_ngamma_note(self):
        """p. 4-29 prints Ngamma = 25.9 at phi = 31; the lookup returns it
        uncorrected and says so wherever the phi = 31 row is used."""
        note = ("Table 4-6 (p. 4-29) prints Ngamma = 25.9 at phi = 31, within "
                "the run of its column (22.4 at 30, 30.2 at 32); this function "
                "returns the printed 25.9, not corrected")
        result = table_4_6_bearing_capacity_factors(31)
        assert result["Ngamma"] == 25.9
        assert result["note"] == note
        assert table_4_6_bearing_capacity_factors(30.5)["note"] == note
        assert table_4_6_bearing_capacity_factors(31.5)["note"] == note
        assert note in table_4_6_bearing_capacity_factors()["note"]
        for phi in (30, 32, 35):
            assert "note" not in table_4_6_bearing_capacity_factors(phi)
        assert note in " ".join(table_4_6_bearing_capacity_factors.__doc__.split())

    def test_increasing_with_phi(self):
        """All factors should increase with friction angle."""
        for phi in [0, 10, 20, 30, 40]:
            r1 = table_4_6_bearing_capacity_factors(phi)
            r2 = table_4_6_bearing_capacity_factors(phi + 5)
            assert r2["Nc"] > r1["Nc"]
            assert r2["Nq"] > r1["Nq"]
            assert r2["Ngamma"] >= r1["Ngamma"]


# ============================================================================
# Table 4-7: Internal Stability Resistance Factors
# ============================================================================

class TestTable47:
    """Tests for table_4_7_internal_resistance()."""

    def test_all_entries(self):
        results = table_4_7_internal_resistance()
        assert len(results) == 4

    def test_rows_as_printed(self):
        """FHWA-NHI-10-024 Vol I Table 4-7, p. 4-48 (PDF page 190): static,
        combined static/earthquake, combined static/traffic barrier impact.
        The key combined_static_phi (a copy of the static factor, no printed
        column) stood beside the print's combined static/earthquake 1.00
        (review finding gec-34)."""
        rows = [(r["static_phi"], r["combined_static_earthquake_phi"],
                 r["combined_static_traffic_barrier_phi"])
                for r in table_4_7_internal_resistance()]
        assert rows == [(0.75, 1.00, 1.00), (0.65, 0.85, 0.85),
                        (0.90, 1.20, 1.20), (0.90, 1.20, 1.00)]
        for r in table_4_7_internal_resistance():
            assert "combined_static_phi" not in r
            assert any(n.startswith("B.") for n in r["notes"])
        grid = table_4_7_internal_resistance("grid")[0]
        assert any("flexible facing mat" in n for n in grid["notes"])
        with pytest.raises(ValueError, match="Geosynthetic reinforcement"):
            table_4_7_internal_resistance("steel")

    def test_metallic_strip(self):
        results = table_4_7_internal_resistance("metallic strip")
        assert len(results) == 1
        assert results[0]["static_phi"] == 0.75
        assert results[0]["combined_static_earthquake_phi"] == 1.00

    def test_geosynthetic(self):
        """'geosynthetic' names the geosynthetic tensile row and the pullout
        row (printed 'metallic and geosynthetic')."""
        results = table_4_7_internal_resistance("geosynthetic")
        assert [(r["static_phi"], r["combined_static_earthquake_phi"],
                 r["combined_static_traffic_barrier_phi"])
                for r in results] == [(0.90, 1.20, 1.20), (0.90, 1.20, 1.00)]

    def test_pullout(self):
        results = table_4_7_internal_resistance("pullout")
        assert len(results) == 1
        assert results[0]["static_phi"] == 0.90

    def test_metallic_grid(self):
        results = table_4_7_internal_resistance("grid")
        assert len(results) == 1
        assert results[0]["static_phi"] == 0.65
