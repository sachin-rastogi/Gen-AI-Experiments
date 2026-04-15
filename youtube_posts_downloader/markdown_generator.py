"""
Markdown generator module for creating .md files from posts.
"""

import yaml
import os
import hashlib
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

from .api_client import YouTubeAPIClient


class MarkdownGenerator:
    """Generates markdown files from post data."""

    def __init__(self, api_client: Optional[YouTubeAPIClient] = None, download_images: bool = True):
        """
        Initialize markdown generator.

        Args:
            api_client: Optional YouTube API client for additional data.
            download_images: Whether to download images locally (default: True).
        """
        self.api_client = api_client
        self.download_images = download_images

    def generate_markdown(self, post: dict, filename: str, output_dir: Optional[str] = None) -> str:
        """
        Generate markdown content from post data.

        Args:
            post: Post data dictionary.
            filename: Filename for the markdown file.
            output_dir: Output directory path (required if download_images=True).

        Returns:
            Complete markdown string with YAML front matter.
        """
        # Build front matter
        front_matter = self._build_front_matter(post, filename)

        # Build content - pass output_dir for image downloading
        content = self._build_content(post, output_dir)

        return f"---\n{front_matter}---\n\n{content}"

    def _download_image(self, url: str, output_dir: str) -> Optional[str]:
        """
        Download image locally and return local path.

        Args:
            url: Image URL.
            output_dir: Output directory for images.

        Returns:
            Local file path relative to output_dir, or None if download fails.
        """
        if not url or not self.download_images:
            return None

        try:
            # Create images subdirectory
            images_dir = Path(output_dir) / "images"
            images_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename using hash of URL
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            ext = Path(url).suffix.split('?')[0]  # Remove query params
            if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                ext = '.jpg'
            
            local_filename = f"{url_hash}{ext}"
            local_path = images_dir / local_filename

            # Skip if already downloaded
            if local_path.exists():
                return str(local_path.relative_to(Path(output_dir)))

            # Download with user agent
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(local_path, 'wb') as f:
                    f.write(response.read())

            return str(local_path.relative_to(Path(output_dir)))

        except Exception as e:
            print(f"Warning: Failed to download image {url}: {e}")
            return None

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

        # Add media info if present (store original URLs)
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

    def _build_content(self, post: dict, output_dir: Optional[str] = None) -> str:
        """
        Build markdown content from post data.

        Args:
            post: Post data dictionary.
            output_dir: Output directory for downloading images.

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
            content_parts.append(self._format_media(media, output_dir))

        return "\n\n".join(content_parts)

    def _format_media(self, media: dict, output_dir: Optional[str] = None) -> str:
        """
        Format media as markdown.

        Args:
            media: Media info dictionary.
            output_dir: Output directory for downloading images.

        Returns:
            Markdown-formatted media section.
        """
        parts = []

        # Image - download locally if enabled
        if "image_url" in media:
            image_url = media["image_url"]
            alt_text = media.get("image_alt", "Image")
            
            if self.download_images and output_dir:
                local_path = self._download_image(image_url, output_dir)
                if local_path:
                    # Use relative path to local image
                    parts.append(f"![{alt_text}](images/{local_path})")
                else:
                    # Fallback to original URL
                    parts.append(f"![{alt_text}]({image_url})")
            else:
                parts.append(f"![{alt_text}]({image_url})")

        # Video - download thumbnail locally if enabled
        if "video_id" in media:
            video_title = media.get("video_title", "Video")
            video_id = media["video_id"]
            parts.append(f"\n### {video_title}")
            parts.append(f"\n[Watch on YouTube](https://www.youtube.com/watch?v={video_id})")

            if "video_thumbnail" in media and self.download_images and output_dir:
                thumbnail_url = media["video_thumbnail"]
                local_path = self._download_image(thumbnail_url, output_dir)
                if local_path:
                    parts.append(f"\n[![Video Thumbnail](images/{local_path})](https://www.youtube.com/watch?v={video_id})")
                else:
                    parts.append(f"\n[![Video Thumbnail]({thumbnail_url})](https://www.youtube.com/watch?v={video_id})")
            elif "video_thumbnail" in media:
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
        output_path = Path(output_dir) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        markdown_content = self.generate_markdown(post, filename, output_dir)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return str(output_path)