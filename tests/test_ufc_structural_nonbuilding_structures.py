"""Tests for geotech_references.ufc_structural.nonbuilding_structures
(Chapter 5 governing-standard pointer list)."""

import pytest

from geotech_references.ufc_structural.nonbuilding_structures import (
    nonbuilding_structure_governing_standard,
    list_nonbuilding_structure_types,
    NONBUILDING_STRUCTURE_STANDARDS,
)


class TestNonbuildingStructureStandards:
    """Anchors: printed Chapter 5 pointers (pp. 85-86)."""

    def test_highway_bridge_is_aashto(self):
        r = nonbuilding_structure_governing_standard("highway_bridge")
        assert "AASHTO LRFD Bridge Design Specifications" in r["governing_standard"]

    def test_railroad_bridge_is_arema(self):
        r = nonbuilding_structure_governing_standard("railroad_bridge")
        assert "AREMA" in r["governing_standard"]

    def test_petroleum_tanks_point_to_ufc(self):
        r = nonbuilding_structure_governing_standard("tanks_petroleum_storage")
        assert r["governing_standard"] == "UFC 3-460-01"

    def test_pedestrian_bridges(self):
        r = nonbuilding_structure_governing_standard("pedestrian_bridges")
        assert "Pedestrian Bridges" in r["governing_standard"]

    def test_every_type_has_a_paragraph_citation(self):
        for structure_type in NONBUILDING_STRUCTURE_STANDARDS:
            r = nonbuilding_structure_governing_standard(structure_type)
            assert r["paragraph"].startswith("5-")

    def test_unknown_structure_type_raises(self):
        with pytest.raises(ValueError):
            nonbuilding_structure_governing_standard("dam")

    def test_list_all_ten_types(self):
        assert len(list_nonbuilding_structure_types()) == 11  # towers + poles both under 5-8
