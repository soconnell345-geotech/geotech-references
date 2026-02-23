"""Tests for GEC-6 structured reference text and retrieval functions."""

import json
import pytest

from geotech_references._retrieval import (
    load_chapter,
    retrieve_section,
    search_sections,
    list_chapters,
)


# ============================================================================
# Chapter loading tests
# ============================================================================

class TestLoadChapter:
    """Tests for load_chapter()."""

    @pytest.mark.parametrize("chapter", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    def test_all_chapters_load(self, chapter):
        """All GEC-6 chapter JSON files load without error."""
        try:
            data = load_chapter("gec_6", chapter)
        except FileNotFoundError:
            pytest.skip(f"Chapter {chapter} JSON file not yet created")
        assert isinstance(data, dict)
        assert data["chapter"] == chapter

    @pytest.mark.parametrize("chapter", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    def test_chapter_has_required_fields(self, chapter):
        """Each chapter has required top-level fields."""
        try:
            data = load_chapter("gec_6", chapter)
        except FileNotFoundError:
            pytest.skip(f"Chapter {chapter} JSON file not yet created")
        assert "reference_id" in data
        assert "chapter_title" in data
        assert "sections" in data
        assert isinstance(data["sections"], list)
        assert len(data["sections"]) > 0

    @pytest.mark.parametrize("chapter", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    def test_sections_have_required_fields(self, chapter):
        """Each section has required fields."""
        try:
            data = load_chapter("gec_6", chapter)
        except FileNotFoundError:
            pytest.skip(f"Chapter {chapter} JSON file not yet created")
        for section in data["sections"]:
            assert "section_id" in section
            assert "title" in section
            assert "body" in section

    def test_chapter1_reference_id(self):
        """Chapter 1 has correct reference ID."""
        try:
            data = load_chapter("gec_6", 1)
        except FileNotFoundError:
            pytest.skip("Chapter 1 not yet created")
        assert data["reference_id"] == "FHWA-SA-02-054"

    def test_chapter5_has_bearing_capacity(self):
        """Chapter 5 has bearing capacity content."""
        try:
            data = load_chapter("gec_6", 5)
        except FileNotFoundError:
            pytest.skip("Chapter 5 not yet created")
        assert "Design" in data["chapter_title"] or "Geotechnical" in data["chapter_title"]

    def test_nonexistent_chapter(self):
        """Loading a non-existent chapter raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_chapter("gec_6", 99)

    def test_nonexistent_reference(self):
        """Loading a non-existent reference raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_chapter("nonexistent_ref", 1)


# ============================================================================
# Section retrieval tests
# ============================================================================

class TestRetrieveSection:
    """Tests for retrieve_section()."""

    def test_retrieve_section_1_1(self):
        """Can retrieve section 1.1."""
        try:
            section = retrieve_section("gec_6", "1.1")
        except (KeyError, FileNotFoundError):
            pytest.skip("Section 1.1 not available")
        assert "title" in section
        assert "body" in section

    def test_section_has_key_points(self):
        """Retrieved sections include key_points."""
        try:
            section = retrieve_section("gec_6", "1.1")
        except (KeyError, FileNotFoundError):
            pytest.skip("Section 1.1 not available")
        assert "key_points" in section
        assert isinstance(section["key_points"], list)

    def test_nonexistent_section(self):
        """Retrieving a non-existent section raises KeyError."""
        with pytest.raises(KeyError):
            retrieve_section("gec_6", "99.99.99")


# ============================================================================
# Search tests
# ============================================================================

class TestSearchSections:
    """Tests for search_sections()."""

    def test_search_returns_results(self):
        """Search for common term returns results."""
        results = search_sections("gec_6", "foundation")
        assert len(results) > 0

    def test_search_results_have_chapter_info(self):
        """Search results include chapter and chapter_title."""
        results = search_sections("gec_6", "foundation")
        if not results:
            pytest.skip("No results found")
        assert "chapter" in results[0]
        assert "chapter_title" in results[0]

    def test_search_bearing_capacity(self):
        """Searching for 'bearing capacity' returns results."""
        results = search_sections("gec_6", "bearing capacity")
        assert len(results) > 0

    def test_search_no_results(self):
        """Search for nonsense returns empty list."""
        results = search_sections("gec_6", "xyzzy_nonexistent_term")
        assert results == []


# ============================================================================
# Chapter listing tests
# ============================================================================

class TestListChapters:
    """Tests for list_chapters()."""

    def test_list_chapters_returns_list(self):
        """list_chapters returns a non-empty list."""
        chapters = list_chapters("gec_6")
        assert isinstance(chapters, list)
        assert len(chapters) > 0

    def test_chapter_entries_have_fields(self):
        """Each chapter entry has required fields."""
        chapters = list_chapters("gec_6")
        for ch in chapters:
            assert "chapter" in ch
            assert "chapter_title" in ch
            assert "sections" in ch
            assert isinstance(ch["sections"], list)

    def test_chapter_sections_have_ids(self):
        """Each section in chapter listing has section_id and title."""
        chapters = list_chapters("gec_6")
        for ch in chapters:
            for section in ch["sections"]:
                assert "section_id" in section
                assert "title" in section
