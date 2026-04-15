"""
Tests for file_namer module.
"""

import pytest
from datetime import datetime

from youtube_posts_downloader.file_namer import FileNamer


class TestFileNamer:
    """Test suite for FileNamer class."""

    def test_generate_filename_basic(self):
        """Test basic filename generation."""
        namer = FileNamer()
        filename = namer.generate_filename("Test Post", "2023-06-15T10:30:00Z")
        assert filename.endswith(".md")
        assert "2023-06-15" in filename
        assert "test-post" in filename

    def test_generate_filename_with_different_dates(self):
        """Test filename with different dates."""
        namer = FileNamer()
        filename = namer.generate_filename("My Post", "2023-01-01T00:00:00Z")
        assert "2023-01-01" in filename

    def test_sanitize_title_removes_invalid_chars(self):
        """Test sanitization removes invalid characters."""
        namer = FileNamer()
        filename = namer.generate_filename("Test <file> name", "2023-06-15T10:30:00Z")
        assert "<" not in filename
        assert ">" not in filename

    def test_sanitize_title_handles_pipes(self):
        """Test sanitization handles pipe characters."""
        namer = FileNamer()
        filename = namer.generate_filename("Test | pipe", "2023-06-15T10:30:00Z")
        assert "|" not in filename

    def test_sanitize_title_replaces_spaces_with_hyphens(self):
        """Test sanitization replaces spaces with hyphens."""
        namer = FileNamer()
        filename = namer.generate_filename("Test Title Here", "2023-06-15T10:30:00Z")
        assert "test-title-here" in filename
        assert " " not in filename

    def test_sanitize_title_converts_to_lowercase(self):
        """Test sanitization converts to lowercase."""
        namer = FileNamer()
        filename = namer.generate_filename("UPPERCASE TITLE", "2023-06-15T10:30:00Z")
        assert filename.islower()

    def test_sanitize_title_removes_leading_trailing_hyphens(self):
        """Test sanitization removes leading/trailing hyphens."""
        namer = FileNamer()
        filename = namer.generate_filename("--title--", "2023-06-15T10:30:00Z")
        assert not filename.startswith("-")
        assert filename.count("---") == 0

    def test_sanitize_title_handles_empty_title(self):
        """Test sanitization handles empty title."""
        namer = FileNamer()
        filename = namer.generate_filename("", "2023-06-15T10:30:00Z")
        assert "untitled" in filename

    def test_sanitize_title_handles_whitespace_only_title(self):
        """Test sanitization handles whitespace-only title."""
        namer = FileNamer()
        filename = namer.generate_filename("   ", "2023-06-15T10:30:00Z")
        assert "untitled" in filename

    def test_handle_collision_different_filenames(self):
        """Test collision handling with different filenames."""
        namer = FileNamer()
        f1 = namer.generate_filename("Test", "2023-06-15T10:30:00Z")
        f2 = namer.generate_filename("Test", "2023-06-16T10:30:00Z")
        assert f1 != f2  # Different dates = different files

    def test_handle_collision_same_date_different_title(self):
        """Test collision handling with same date different titles."""
        namer = FileNamer()
        namer.reset()  # Reset to test collision handling
        f1 = namer.generate_filename("Test Post", "2023-06-15T10:30:00Z")
        f2 = namer.generate_filename("Test Post", "2023-06-15T10:30:00Z")
        assert f1 != f2
        assert f2.endswith("_1.md")

    def test_handle_collision_multiple_same(self):
        """Test collision handling with multiple identical inputs."""
        namer = FileNamer()
        namer.reset()
        filenames = []
        for _ in range(3):
            filenames.append(namer.generate_filename("Same", "2023-06-15T10:30:00Z"))

        assert filenames[0] != filenames[1]
        assert filenames[1] != filenames[2]
        assert filenames[0] == "2023-06-15_same.md"
        assert filenames[1] == "2023-06-15_same_1.md"
        assert filenames[2] == "2023-06-15_same_2.md"

    def test_reset_clears_used_filenames(self):
        """Test reset clears used filenames."""
        namer = FileNamer()
        namer.generate_filename("Test", "2023-06-15T10:30:00Z")
        namer.reset()
        assert namer.get_used_count() == 0

    def test_get_used_count(self):
        """Test get_used_count returns correct count."""
        namer = FileNamer()
        assert namer.get_used_count() == 0
        namer.generate_filename("Test1", "2023-06-15T10:30:00Z")
        assert namer.get_used_count() == 1
        namer.generate_filename("Test2", "2023-06-16T10:30:00Z")
        assert namer.get_used_count() == 2


class TestFileNamerEdgeCases:
    """Edge case tests for FileNamer."""

    def test_very_long_title_truncation(self):
        """Test truncation of very long titles."""
        namer = FileNamer()
        long_title = "A" * 300
        filename = namer.generate_filename(long_title, "2023-06-15T10:30:00Z")
        # Should be truncated but still valid
        assert len(filename) <= 200
        assert filename.endswith(".md")

    def test_special_characters_in_title(self):
        """Test handling of special characters."""
        namer = FileNamer()
        # Various special characters that should be handled
        filename = namer.generate_filename(
            "Test: with/slashes \\ and *stars*?",
            "2023-06-15T10:30:00Z"
        )
        assert ":" not in filename
        assert "/" not in filename
        assert "\\" not in filename
        assert "?" not in filename

    def test_unicode_in_title(self):
        """Test handling of unicode in title."""
        namer = FileNamer()
        filename = namer.generate_filename("标题测试 emoji 🎉", "2023-06-15T10:30:00Z")
        # Should not crash and should contain sanitized version
        assert filename.endswith(".md")

    def test_multiple_consecutive_hyphens(self):
        """Test handling of multiple consecutive hyphens."""
        namer = FileNamer()
        filename = namer.generate_filename("Test---Multiple---Hyphens", "2023-06-15T10:30:00Z")
        assert "---" not in filename

    def test_filename_with_custom_extension(self):
        """Test generation with custom extension."""
        namer = FileNamer()
        filename = namer.generate_filename("Test", "2023-06-15T10:30:00Z", extension=".txt")
        assert filename.endswith(".txt")
        assert not filename.endswith(".md")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])