"""Tests for GEC-13 structured reference text and retrieval functions."""

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

    @pytest.mark.parametrize("chapter", list(range(1, 12)))
    def test_all_chapters_load(self, chapter):
        """All 11 GEC-13 chapter JSON files load without error."""
        data = load_chapter("gec_13", chapter)
        assert isinstance(data, dict)
        assert data["chapter"] == chapter

    @pytest.mark.parametrize("chapter", list(range(1, 12)))
    def test_chapter_has_required_fields(self, chapter):
        """Each chapter has required top-level fields."""
        data = load_chapter("gec_13", chapter)
        assert "reference_id" in data
        assert data["reference_id"] == "FHWA-NHI-16-027"
        assert "chapter_title" in data
        assert "sections" in data
        assert isinstance(data["sections"], list)
        assert len(data["sections"]) > 0

    @pytest.mark.parametrize("chapter", list(range(1, 12)))
    def test_sections_have_required_fields(self, chapter):
        """Each section has required fields."""
        data = load_chapter("gec_13", chapter)
        for section in data["sections"]:
            assert "section_id" in section
            assert "title" in section
            assert "body" in section

    @pytest.mark.parametrize("chapter", list(range(1, 7)))
    def test_vol1_chapters_have_volume_1(self, chapter):
        """Volume I chapters (1-6) carry volume=1."""
        data = load_chapter("gec_13", chapter)
        assert data.get("volume") == 1

    @pytest.mark.parametrize("chapter", list(range(7, 12)))
    def test_vol2_chapters_have_volume_2(self, chapter):
        """Volume II chapters (7-11) carry volume=2."""
        data = load_chapter("gec_13", chapter)
        assert data.get("volume") == 2

    def test_chapter1_reference_id(self):
        """Chapter 1 has correct reference ID."""
        data = load_chapter("gec_13", 1)
        assert data["reference_id"] == "FHWA-NHI-16-027"

    def test_chapter2_has_drain_content(self):
        """Chapter 2 covers vertical drains."""
        data = load_chapter("gec_13", 2)
        assert any(
            word in data["chapter_title"].lower()
            for word in ("drain", "vertical", "consolidation")
        )

    def test_chapter6_column_supported_embankments(self):
        """Chapter 6 covers column-supported embankments."""
        data = load_chapter("gec_13", 6)
        assert any(
            word in data["chapter_title"].lower()
            for word in ("column", "embankment", "supported")
        )

    def test_chapter7_deep_mixing(self):
        """Chapter 7 (Vol II) covers deep mixing."""
        data = load_chapter("gec_13", 7)
        assert any(
            word in data["chapter_title"].lower()
            for word in ("deep", "mixing", "mix")
        )

    def test_chapter11_geosynthetic(self):
        """Chapter 11 (Vol II) covers geosynthetic reinforcement."""
        data = load_chapter("gec_13", 11)
        assert any(
            word in data["chapter_title"].lower()
            for word in ("geosynthetic", "reinforcement", "geogrid")
        )

    def test_nonexistent_chapter(self):
        """Loading a non-existent chapter raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_chapter("gec_13", 99)

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
        section = retrieve_section("gec_13", "1.0")
        assert "title" in section
        assert "body" in section

    def test_retrieve_vol2_section(self):
        """Can retrieve a section from a Vol II chapter."""
        section = retrieve_section("gec_13", "7.1")
        assert "title" in section
        assert "deep" in section["body"].lower() or "mixing" in section["body"].lower()

    def test_section_has_key_points(self):
        """Retrieved sections include key_points."""
        section = retrieve_section("gec_13", "1.0")
        assert "key_points" in section
        assert isinstance(section["key_points"], list)

    def test_nonexistent_section(self):
        """Retrieving a non-existent section raises KeyError."""
        with pytest.raises(KeyError):
            retrieve_section("gec_13", "99.99.99")


# ============================================================================
# Search tests
# ============================================================================

class TestSearchSections:
    """Tests for search_sections()."""

    def test_search_returns_results(self):
        """Search for common term returns results."""
        results = search_sections("gec_13", "ground modification")
        assert len(results) > 0

    def test_search_results_have_chapter_info(self):
        """Search results include chapter and chapter_title."""
        results = search_sections("gec_13", "ground modification")
        assert "chapter" in results[0]
        assert "chapter_title" in results[0]

    def test_search_vertical_drain(self):
        """Searching for 'vertical drain' returns results."""
        results = search_sections("gec_13", "vertical drain")
        assert len(results) > 0

    def test_search_deep_mixing(self):
        """Searching for 'deep mixing' returns Vol II results."""
        results = search_sections("gec_13", "deep mixing")
        assert len(results) > 0
        assert any(r["chapter"] >= 7 for r in results)

    def test_search_geosynthetic(self):
        """Searching for 'geosynthetic' returns results."""
        results = search_sections("gec_13", "geosynthetic")
        assert len(results) > 0

    def test_search_no_results(self):
        """Search for nonsense returns empty list."""
        results = search_sections("gec_13", "xyzzy_nonexistent_term_abc")
        assert results == []


# ============================================================================
# Chapter listing tests
# ============================================================================

class TestListChapters:
    """Tests for list_chapters()."""

    def test_list_chapters_returns_list(self):
        """list_chapters returns a list (may be empty if no chapters yet)."""
        chapters = list_chapters("gec_13")
        assert isinstance(chapters, list)

    def test_chapter_entries_have_fields(self):
        """Each chapter entry has required fields."""
        chapters = list_chapters("gec_13")
        if not chapters:
            pytest.skip("No GEC-13 chapters available yet")
        for ch in chapters:
            assert "chapter" in ch
            assert "chapter_title" in ch
            assert "sections" in ch
            assert isinstance(ch["sections"], list)

    def test_chapter_sections_have_ids(self):
        """Each section in chapter listing has section_id and title."""
        chapters = list_chapters("gec_13")
        if not chapters:
            pytest.skip("No GEC-13 chapters available yet")
        for ch in chapters:
            for section in ch["sections"]:
                assert "section_id" in section
                assert "title" in section
