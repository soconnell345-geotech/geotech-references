"""Tests for GEC-10 structured reference text and retrieval functions."""

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

    @pytest.mark.parametrize("chapter", list(range(1, 24)))
    def test_all_chapters_load(self, chapter):
        """All GEC-10 chapter JSON files load without error."""
        try:
            data = load_chapter("gec_10", chapter)
        except FileNotFoundError:
            pytest.skip(f"Chapter {chapter} JSON file not yet created")
        assert isinstance(data, dict)
        assert data["chapter"] == chapter

    @pytest.mark.parametrize("chapter", list(range(1, 24)))
    def test_chapter_has_required_fields(self, chapter):
        """Each chapter has required top-level fields."""
        try:
            data = load_chapter("gec_10", chapter)
        except FileNotFoundError:
            pytest.skip(f"Chapter {chapter} JSON file not yet created")
        assert "reference_id" in data
        assert "chapter_title" in data
        assert "sections" in data
        assert isinstance(data["sections"], list)
        assert len(data["sections"]) > 0

    @pytest.mark.parametrize("chapter", list(range(1, 24)))
    def test_sections_have_required_fields(self, chapter):
        """Each section has required fields."""
        try:
            data = load_chapter("gec_10", chapter)
        except FileNotFoundError:
            pytest.skip(f"Chapter {chapter} JSON file not yet created")
        for section in data["sections"]:
            assert "section_id" in section
            assert "title" in section
            assert "body" in section

    def test_chapter10_reference_id(self):
        """Chapter 10 has correct reference ID."""
        try:
            data = load_chapter("gec_10", 10)
        except FileNotFoundError:
            pytest.skip("Chapter 10 not yet created")
        assert data["reference_id"] == "FHWA-NHI-10-016"

    def test_chapter13_has_design_content(self):
        """Chapter 13 covers geotechnical design."""
        try:
            data = load_chapter("gec_10", 13)
        except FileNotFoundError:
            pytest.skip("Chapter 13 not yet created")
        assert any(
            word in data["chapter_title"].lower()
            for word in ("design", "resistance", "geomaterial", "axial")
        )

    def test_nonexistent_chapter(self):
        """Loading a non-existent chapter raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_chapter("gec_10", 99)

    def test_nonexistent_reference(self):
        """Loading a non-existent reference raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_chapter("nonexistent_ref", 1)


# ============================================================================
# Section retrieval tests
# ============================================================================

class TestRetrieveSection:
    """Tests for retrieve_section()."""

    def test_retrieve_existing_section(self):
        """Can retrieve a section from an existing chapter."""
        chapters = list_chapters("gec_10")
        if not chapters:
            pytest.skip("No GEC-10 chapters available")
        first_ch = chapters[0]
        if not first_ch["sections"]:
            pytest.skip("First chapter has no sections")
        section_id = first_ch["sections"][0]["section_id"]
        section = retrieve_section("gec_10", section_id)
        assert "title" in section
        assert "body" in section

    def test_section_has_key_points(self):
        """Retrieved sections include key_points."""
        chapters = list_chapters("gec_10")
        if not chapters:
            pytest.skip("No GEC-10 chapters available")
        section_id = chapters[0]["sections"][0]["section_id"]
        section = retrieve_section("gec_10", section_id)
        assert "key_points" in section
        assert isinstance(section["key_points"], list)

    def test_nonexistent_section(self):
        """Retrieving a non-existent section raises KeyError."""
        with pytest.raises(KeyError):
            retrieve_section("gec_10", "99.99.99")


# ============================================================================
# Search tests
# ============================================================================

class TestSearchSections:
    """Tests for search_sections()."""

    def test_search_returns_results(self):
        """Search for common term returns results."""
        results = search_sections("gec_10", "drilled shaft")
        if not results:
            pytest.skip("No search results — chapters may not exist yet")
        assert len(results) > 0

    def test_search_results_have_chapter_info(self):
        """Search results include chapter and chapter_title."""
        results = search_sections("gec_10", "drilled shaft")
        if not results:
            pytest.skip("No search results")
        assert "chapter" in results[0]
        assert "chapter_title" in results[0]

    def test_search_resistance(self):
        """Searching for 'resistance' returns results."""
        results = search_sections("gec_10", "resistance")
        if not results:
            pytest.skip("No results — chapters may not exist yet")
        assert len(results) > 0

    def test_search_no_results(self):
        """Search for nonsense returns empty list."""
        results = search_sections("gec_10", "xyzzy_nonexistent_term_abc")
        assert results == []


# ============================================================================
# Chapter listing tests
# ============================================================================

class TestListChapters:
    """Tests for list_chapters()."""

    def test_list_chapters_returns_list(self):
        """list_chapters returns a list (may be empty if no chapters yet)."""
        chapters = list_chapters("gec_10")
        assert isinstance(chapters, list)

    def test_chapter_entries_have_fields(self):
        """Each chapter entry has required fields."""
        chapters = list_chapters("gec_10")
        if not chapters:
            pytest.skip("No GEC-10 chapters available yet")
        for ch in chapters:
            assert "chapter" in ch
            assert "chapter_title" in ch
            assert "sections" in ch
            assert isinstance(ch["sections"], list)

    def test_chapter_sections_have_ids(self):
        """Each section in chapter listing has section_id and title."""
        chapters = list_chapters("gec_10")
        if not chapters:
            pytest.skip("No GEC-10 chapters available yet")
        for ch in chapters:
            for section in ch["sections"]:
                assert "section_id" in section
                assert "title" in section
