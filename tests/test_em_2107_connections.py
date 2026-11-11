"""Tests for geotech_references.em_2107.connections (Chapter 6)."""

import pytest

from geotech_references.em_2107.connections import (
    bolt_grade_check,
    welding_code_selection,
    faying_surface_class,
)


class TestBoltGradeCheck:
    def test_structural_grades_permitted(self):
        assert bolt_grade_check("ASTM F3125 Grade A325", "structural")["permitted"] is True
        assert bolt_grade_check("ASTM F3125 Grade A490", "structural")["permitted"] is True
        assert bolt_grade_check("ASTM F3148", "structural")["permitted"] is True

    def test_a307_not_structural(self):
        assert bolt_grade_check("ASTM A307", "structural")["permitted"] is False

    def test_a307_ok_nonstructural(self):
        assert bolt_grade_check("ASTM A307", "nonstructural")["permitted"] is True

    def test_case_insensitive(self):
        assert bolt_grade_check("astm f3125 grade a325", "structural")["permitted"] is True

    def test_bad_application(self):
        with pytest.raises(ValueError):
            bolt_grade_check("ASTM A307", "bogus")

    def test_unknown_grade_refused_not_answered(self):
        # Paragraph 6.1.3.4 (EM 1110-2-2107_2022.pdf pdf 47 / printed 38)
        # names the grades; "A325" alone or an unlisted grade used to come
        # back permitted=False, a default answer for an unknown key.
        with pytest.raises(ValueError, match="6.1.3.4"):
            bolt_grade_check("A325", "structural")
        with pytest.raises(ValueError, match="ASTM F3125 Grade A325"):
            bolt_grade_check("ISO 898 class 8.8", "nonstructural")

    def test_print_spelling_3148_names_the_grade_to_pass(self):
        # Paragraph 6.1.3.4 (pdf 47 / printed 38) reads "ASTM 3148".
        with pytest.raises(ValueError, match="reads 'ASTM 3148'.*'ASTM F3148'"):
            bolt_grade_check("ASTM 3148", "structural")


class TestWeldingCodeSelection:
    def test_cyclic_or_fcm_requires_d15(self):
        r = welding_code_selection(True)
        assert r["code"] == "AWS D1.5(M)"

    def test_redundant_noncyclic_allows_d11(self):
        r = welding_code_selection(False)
        assert "D1.1" in r["code"]


class TestFayingSurfaceClass:
    def test_clean_mill_scale_is_class_a(self):
        assert faying_surface_class("clean_mill_scale")["class"] == "Class A"

    def test_blast_cleaned_is_class_b(self):
        assert faying_surface_class("blast_cleaned")["class"] == "Class B"

    def test_invalid(self):
        with pytest.raises(ValueError):
            faying_surface_class("bogus")
