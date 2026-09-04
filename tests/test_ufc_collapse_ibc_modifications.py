"""Tests for geotech_references.ufc_collapse.ibc_modifications (Appendix H).

All anchors are PRINTED VALUE (Appendix H's enumerable Risk-Category and
material-keyed requirements, printed pp. 225-228).
"""

import pytest

from geotech_references.ufc_collapse.ibc_modifications import (
    construction_document_requirements,
    qa_plan_required,
    qa_plan_detailed_requirements,
    special_inspection_requirements,
    structural_observation_required,
)


class TestConstructionDocumentRequirements:
    def test_three_required_items(self):
        r = construction_document_requirements()
        assert len(r["required_items"]) == 3


class TestQaPlanRequired:
    def test_rc_i_no_qa_plan(self):
        r = qa_plan_required("I")
        assert r["qa_plan_required"] is False
        assert r["trigger_description"] is None

    def test_rc_ii_iii_iv_require_qa_plan(self):
        for rc in ("II", "III", "IV"):
            r = qa_plan_required(rc)
            assert r["qa_plan_required"] is True
            assert r["trigger_description"] is not None

    def test_invalid_category_raises(self):
        with pytest.raises(ValueError):
            qa_plan_required("V")

    def test_detailed_requirements_four_items(self):
        r = qa_plan_detailed_requirements()
        assert len(r["required_items"]) == 4


class TestSpecialInspectionRequirements:
    def test_structural_steel_awd_d1_1(self):
        r = special_inspection_requirements("structural_steel")
        assert "AWS D1.1" in r["requirement"]
        assert any("5/16" in e for e in r["exemptions"])

    def test_cast_in_place_concrete_continuous(self):
        r = special_inspection_requirements("cast_in_place_concrete")
        assert "continuous" in r["requirement"].lower()

    def test_wood_periodic(self):
        r = special_inspection_requirements("wood")
        assert "periodic" in r["requirement"].lower()

    def test_unknown_material_raises(self):
        with pytest.raises(ValueError):
            special_inspection_requirements("glass")


class TestStructuralObservationRequired:
    def test_rc_iv_unconditional(self):
        r = structural_observation_required(contracting_officer_requires=False, risk_category="IV")
        assert r["required"] is True

    def test_rc_ii_requires_contracting_officer(self):
        r = structural_observation_required(contracting_officer_requires=False, risk_category="II")
        assert r["required"] is False
        r2 = structural_observation_required(contracting_officer_requires=True, risk_category="II")
        assert r2["required"] is True
