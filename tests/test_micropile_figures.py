"""Tests for micropile figure lookup functions."""

import pytest

from geotech_references.micropile.figures import (
    figure_5_23_limiting_lateral_modulus,
)


# ============================================================================
# Figure 5-23: Limiting Lateral Modulus Values
# FHWA-NHI-05-039, p. 5-70 (PDF page 162): a bar chart, each bar with its
# value in psi printed above it. The rule is on p. 5-68 (PDF page 160).
# ============================================================================

# (key, label printed under the bar, psi printed above the bar)
PRINTED_BARS = [
    ("5.5x0.36_n80", '5.5"x0.36" 80 ksi casing', 97),
    ("7x0.5_n80", '7"x0.5" 80 ksi casing', 105),
    ("7x0.73_n80", '7"x0.73" 80 ksi casing', 159),
    ("9.625x0.47_n80", '9.625"x0.47" 80 ksi casing', 71),
    ("5.5_a519", "5 1/2-inch casing", 27),
    ("6.625_a519", "6 5/8-inch casing", 23),
    ("8_a519", "8-inch casing", 19),
    ("10.75_a519", "10 3/4-inch casing", 17),
    ("#10", "#10 Bar", 610),
    ("#11", "#11 Bar", 610),
    ("#14", "#14 Bar", 610),
    ("#18", "#18 Bar", 610),
    ("#20", "#20 Bar", 610),
    ("#28", "#28 Bar", 610),
    ("30/16", "30/16", 295),
    ("32/20", "32/20", 253),
    ("40/20", "40/20", 310),
    ("52/26", "52/26", 343),
    ("73/53", "73/53", 165),
    ("103/51", "103/51", 350),
]


class TestFigure523:
    """Tests for figure_5_23_limiting_lateral_modulus()."""

    @pytest.mark.parametrize("key, label, psi", PRINTED_BARS)
    def test_every_printed_bar(self, key, label, psi):
        r = figure_5_23_limiting_lateral_modulus(key)
        assert r["section"] == key
        assert r["description"] == label
        assert r["es_limit_psi"] == psi
        assert r["es_limit_kpa"] == round(psi * 6.894757)

    def test_three_bars_that_were_wrong(self):
        """9.625"x0.47" is 71 psi (it held the 7"x0.73" casing's 159); the
        73/53 and 103/51 hollow bars are 165 and 350 psi (they were swapped)."""
        assert figure_5_23_limiting_lateral_modulus(
            "9.625x0.47_n80")["es_limit_kpa"] == 490
        assert figure_5_23_limiting_lateral_modulus("73/53")["es_limit_kpa"] == 1138
        assert figure_5_23_limiting_lateral_modulus("103/51")["es_limit_kpa"] == 2413

    def test_casing_n80(self):
        r = figure_5_23_limiting_lateral_modulus("5.5x0.36_n80")
        assert r["es_limit_kpa"] == 669

    def test_bar_14(self):
        r = figure_5_23_limiting_lateral_modulus("#14")
        assert r["es_limit_kpa"] == 4206  # 610 psi x 6.894757

    def test_rule_is_the_printed_one(self):
        """p. 5-68: no further check when Es LIMIT is LESS than Es."""
        r = figure_5_23_limiting_lateral_modulus("7x0.5_n80")
        assert "Es LIMIT is less than" in r["rule"]
        assert "does not need to be considered further" in r["rule"]
        assert "greater than Es, buckling should be evaluated" in r["rule"]
        assert "p. 5-70" in r["reference"]

    def test_listed_aliases(self):
        assert figure_5_23_limiting_lateral_modulus(
            "7x0.73")["section"] == "7x0.73_n80"
        assert figure_5_23_limiting_lateral_modulus(
            "#20 Bar")["section"] == "#20"
        assert figure_5_23_limiting_lateral_modulus(
            "10.75")["section"] == "10.75_a519"

    @pytest.mark.parametrize("partial", ["5.5", "8", "10", "20", "n80",
                                         "a519", "7", "#1", "casing"])
    def test_partial_key_is_refused(self, partial):
        """A key must name one bar: '5.5' is two casings, '10' a casing or a
        bar; neither is answered from the first match."""
        with pytest.raises(ValueError, match="Figure 5-23"):
            figure_5_23_limiting_lateral_modulus(partial)

    def test_all_returns_categories(self):
        r = figure_5_23_limiting_lateral_modulus("all")
        assert len(r["casings"]) == 8
        assert len(r["bars"]) == 6
        assert len(r["hollow_bars"]) == 6
        assert r["casings"]["9.625x0.47_n80"]["es_limit_psi"] == 71
        assert "rule" in r and "reference" in r

    def test_empty_returns_all(self):
        r = figure_5_23_limiting_lateral_modulus("")
        assert "casings" in r

    def test_invalid_section(self):
        with pytest.raises(ValueError):
            figure_5_23_limiting_lateral_modulus("nonexistent_bar")

    def test_returns_int(self):
        r = figure_5_23_limiting_lateral_modulus("#10")
        assert isinstance(r["es_limit_kpa"], int)
