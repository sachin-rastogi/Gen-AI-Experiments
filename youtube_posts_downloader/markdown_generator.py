"""
Markdown generator module for creating .md files from posts.
"""

import yaml
from datetime import datetime
from typing import Optional

from .api_client import YouTubeAPIClient


class MarkdownGenerator:
    """Generates markdown files from post data."""

    def __init__(self, api_client: Optional[YouTubeAPIClient] = None):
        """
        Initialize markdown generator.

        Args:
            api_client: Optional YouTube API client for additional data.
        """
        self.api_client = api_client

    def generate_markdown(self, post: dict, filename: str) -> str:
        """
        Generate markdown content from post data.

        Args:
            post: Post data dictionary.
            filename: Filename for the markdown file.

        Returns:
            Complete markdown string with YAML front matter.
        """
        # Build front matter
        front_matter = self._build_front_matter(post, filename)

        # Build content
        content = self._build_content(post)

        return f"---\n{front_matter}---\n\n{content}"

    def _build_front_matter(self, post: dict, filename: str) -> str:
        """
        Build YAML front matter.

        Args:
            post: Post data dictionary.
            filename: Filename for the markdown file.

        Returns:
            YAML-formatted front matter string.
        """
        # Parse the published date for proper formatting
        published_at = post.get("published_at", "")
        try:
            from dateutil import parser as date_parser
            dt = date_parser.parse(published_at)
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            formatted_date = published_at

        # Build metadata dictionary
        metadata = {
            "title": post.get("title", "Community Post"),
            "date": formatted_date,
            "channel_id": post.get("channel_id", ""),
            "channel_title": post.get("channel_title", ""),
            "post_id": post.get("id", ""),
            "filename": filename,
        }

        # Add media info if present
        media = post.get("media", {})
        if media:
            if "image_url" in media:
                metadata["image_url"] = media["image_url"]
            if "video_id" in media:
                metadata["video_id"] = media["video_id"]
                metadata["video_title"] = media.get("video_title", "")
                metadata["video_thumbnail"] = media.get("video_thumbnail", "")

        # Generate YAML with safe settings
        return yaml.dump(
            metadata,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=1000,  # Prevent line wrapping
        )

    def _build_content(self, post: dict) -> str:
        """
        Build markdown content from post data.

        Args:
            post: Post data dictionary.

        Returns:
            Markdown content string.
        """
        content_parts = []

        # Add main content
        post_content = post.get("content", "")
        if post_content:
            content_parts.append(post_content)

        # Add media section if present
        media = post.get("media", {})
        if media:
            content_parts.append(self._format_media(media))

        return "\n\n".join(content_parts)

    def _format_media(self, media: dict) -> str:
        """
        Format media as markdown.

        Args:
            media: Media info dictionary.

        Returns:
            Markdown-formatted media section.
        """
        parts = []

        # Image
        if "image_url" in media:
            alt_text = media.get("image_alt", "Image")
            parts.append(f"![{alt_text}]({media['image_url']})")

        # Video
        if "video_id" in media:
            video_title = media.get("video_title", "Video")
            video_id = media["video_id"]
            parts.append(f"### {video_title}")
            parts.append(f"\n[Watch on YouTube](https://www.youtube.com/watch?v={video_id})")

            if "video_thumbnail" in media:
                parts.append(f"\n[![Video Thumbnail]({media['video_thumbnail']})](https://www.youtube.com/watch?v={video_id})")

        return "\n".join(parts)

    def save_to_file(self, post: dict, filename: str, output_dir: str) -> str:
        """
        Generate markdown and save to file.

        Args:
            post: Post data dictionary.
            filename: Filename for the markdown file.
            output_dir: Output directory path.

        Returns:
            Full path to saved file.
        """
        from pathlib import Path

        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        markdown_content = self.generate_markdown(post, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return str(output_path)