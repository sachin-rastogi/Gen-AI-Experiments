"""
Tests for markdown_generator module.
"""

import pytest
import yaml
from datetime import datetime
from io import StringIO

from youtube_posts_downloader.markdown_generator import MarkdownGenerator


class TestMarkdownGenerator:
    """Test suite for MarkdownGenerator class."""

    def test_generate_markdown_basic(self):
        """Test basic markdown generation."""
        gen = MarkdownGenerator()
        post = {
            "id": "post123",
            "title": "Test Post Title",
            "content": "This is the post content.",
            "published_at": "2023-06-15T10:30:00Z",
            "channel_id": "UC123",
            "channel_title": "Test Channel",
        }
        filename = "2023-06-15_test-post-title.md"
        result = gen.generate_markdown(post, filename)

        assert "---" in result
        assert "title: Test Post Title" in result
        # Check for date - format varies (may be quoted)
        assert "2023" in result
        assert "This is the post content" in result

    def test_generate_markdown_includes_front_matter(self):
        """Test markdown includes YAML front matter."""
        gen = MarkdownGenerator()
        post = {
            "id": "post123",
            "title": "My Post",
            "content": "Content here",
            "published_at": "2023-06-15T10:30:00Z",
            "channel_id": "UC123",
            "channel_title": "My Channel",
        }
        result = gen.generate_markdown(post, "test.md")

        # Split on front matter markers
        parts = result.split("---")
        assert len(parts) >= 3  # ---front_matter---content

    def test_front_matter_contains_metadata(self):
        """Test front matter contains required metadata."""
        gen = MarkdownGenerator()
        post = {
            "id": "abc123",
            "title": "Test Title",
            "content": "Test content",
            "published_at": "2023-06-15T10:30:00Z",
            "channel_id": "UCxyz",
            "channel_title": "Channel Name",
        }
        result = gen.generate_markdown(post, "test.md")

        # Extract front matter
        start = result.index("---") + 3
        end = result.index("---", start)
        front_matter = result[start:end].strip()

        # Parse YAML
        metadata = yaml.safe_load(front_matter)

        assert metadata["title"] == "Test Title"
        assert metadata["channel_id"] == "UCxyz"
        assert metadata["post_id"] == "abc123"
        assert metadata["filename"] == "test.md"

    def test_content_section_formatting(self):
        """Test content section is properly formatted."""
        gen = MarkdownGenerator()
        post = {
            "id": "post123",
            "title": "Test",
            "content": "First paragraph.\n\nSecond paragraph.",
            "published_at": "2023-06-15T10:30:00Z",
            "channel_id": "UC123",
            "channel_title": "Test",
        }
        result = gen.generate_markdown(post, "test.md")

        assert "First paragraph" in result
        assert "Second paragraph" in result

    def test_empty_content_handling(self):
        """Test handling of empty content."""
        gen = MarkdownGenerator()
        post = {
            "id": "post123",
            "title": "Test",
            "content": "",
            "published_at": "2023-06-15T10:30:00Z",
            "channel_id": "UC123",
            "channel_title": "Test",
        }
        result = gen.generate_markdown(post, "test.md")
        # Should not crash, should have empty content section

    def test_format_media_with_image(self):
        """Test media formatting with image."""
        gen = MarkdownGenerator()
        media = {
            "image_url": "https://example.com/image.jpg",
            "image_alt": "Test Image",
        }
        result = gen._format_media(media)

        assert "https://example.com/image.jpg" in result
        assert "Test Image" in result

    def test_format_media_with_video(self):
        """Test media formatting with video."""
        gen = MarkdownGenerator()
        media = {
            "video_id": "abc123",
            "video_title": "Test Video",
            "video_thumbnail": "https://example.com/thumb.jpg",
        }
        result = gen._format_media(media)

        assert "abc123" in result
        assert "Test Video" in result
        assert "youtube.com/watch" in result

    def test_format_media_empty(self):
        """Test media formatting with empty media."""
        gen = MarkdownGenerator()
        result = gen._format_media({})
        assert result == ""

    def test_generate_markdown_with_media(self):
        """Test markdown generation includes media."""
        gen = MarkdownGenerator()
        post = {
            "id": "post123",
            "title": "Test",
            "content": "Check out this image!",
            "published_at": "2023-06-15T10:30:00Z",
            "channel_id": "UC123",
            "channel_title": "Test",
            "media": {
                "image_url": "https://example.com/img.jpg",
                "image_alt": "Description",
            },
        }
        result = gen.generate_markdown(post, "test.md")

        assert "https://example.com/img.jpg" in result

    def test_generate_markdown_with_video(self):
        """Test markdown generation includes video."""
        gen = MarkdownGenerator()
        post = {
            "id": "post123",
            "title": "Test",
            "content": "Check out this video!",
            "published_at": "2023-06-15T10:30:00Z",
            "channel_id": "UC123",
            "channel_title": "Test",
            "media": {
                "video_id": "vid123",
                "video_title": "My Video",
            },
        }
        result = gen.generate_markdown(post, "test.md")

        assert "vid123" in result
        assert "youtube.com/watch" in result


class TestMarkdownGeneratorEdgeCases:
    """Edge case tests for MarkdownGenerator."""

    def test_date_parsing_fallback(self):
        """Test fallback for unparseable dates."""
        gen = MarkdownGenerator()
        post = {
            "id": "post123",
            "title": "Test",
            "content": "Content",
            "published_at": "invalid-date",
            "channel_id": "UC123",
            "channel_title": "Test",
        }
        result = gen.generate_markdown(post, "test.md")
        # Should not crash, uses fallback date

    def test_missing_optional_fields(self):
        """Test handling of missing optional fields."""
        gen = MarkdownGenerator()
        post = {
            "id": "post123",
            "title": "Test",
            "content": "Content",
            "published_at": "2023-06-15T10:30:00Z",
            # Missing channel_id and channel_title
        }
        result = gen.generate_markdown(post, "test.md")
        # Should not crash

    def test_unicode_content(self):
        """Test handling of unicode content."""
        gen = MarkdownGenerator()
        post = {
            "id": "post123",
            "title": "测试",
            "content": "Emoji 🎉 and unicode ✓",
            "published_at": "2023-06-15T10:30:00Z",
            "channel_id": "UC123",
            "channel_title": "Test",
        }
        result = gen.generate_markdown(post, "test.md")
        assert "测试" in result
        assert "🎉" in result

    def test_yaml_special_characters_in_content(self):
        """Test handling of YAML special characters."""
        gen = MarkdownGenerator()
        post = {
            "id": "post123",
            "title": "Test",
            "content": "Special chars: : # - [ ] { }",
            "published_at": "2023-06-15T10:30:00Z",
            "channel_id": "UC123",
            "channel_title": "Test",
        }
        result = gen.generate_markdown(post, "test.md")
        # Should not crash, YAML should handle these in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])