"""
File naming module for generating filenames from post content.
"""

import re
from datetime import datetime
from typing import Optional

from .config import MAX_FILENAME_LENGTH, FILENAME_INVALID_CHARS


class FileNamer:
    """Handles filename generation from post content."""

    def __init__(self):
        """Initialize file namer."""
        self._used_names = set()

    def generate_filename(
        self,
        title: str,
        published_at: str,
        extension: str = ".md",
    ) -> str:
        """
        Generate a filename from post title and date.

        Args:
            title: Post title/content.
            published_at: ISO 8601 date string.

        Returns:
            Sanitized filename with extension.
        """
        # Extract date from ISO 8601 string
        date_str = self._extract_date(published_at)

        # Generate base name from title
        base_name = self._sanitize_title(title)

        # Truncate if too long
        max_base_length = MAX_FILENAME_LENGTH - len(date_str) - len(extension) - 1
        if len(base_name) > max_base_length:
            base_name = base_name[:max_base_length].rstrip()

        # Build filename
        filename = f"{date_str}_{base_name}{extension}"

        # Handle collisions
        filename = self._handle_collision(filename)

        return filename

    def _extract_date(self, published_at: str) -> str:
        """
        Extract date string from ISO 8601 date.

        Args:
            published_at: ISO 8601 date string.

        Returns:
            Date string in YYYY-MM-DD format.
        """
        try:
            from dateutil import parser as date_parser
            dt = date_parser.parse(published_at)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            # Fallback to today's date
            return datetime.now().strftime("%Y-%m-%d")

    def _sanitize_title(self, title: str) -> str:
        """
        Sanitize title for use in filename.

        Args:
            title: Raw title string.

        Returns:
            Sanitized title string.
        """
        if not title or not title.strip():
            return "untitled"

        # Remove or replace invalid characters
        sanitized = re.sub(FILENAME_INVALID_CHARS, "", title)

        # Replace spaces and multiple hyphens with single hyphen
        sanitized = re.sub(r"[\s\-]+", "-", sanitized)

        # Remove leading/trailing hyphens
        sanitized = sanitized.strip("-")

        # Convert to lowercase
        sanitized = sanitized.lower()

        # If resulting string is empty, use default
        if not sanitized:
            return "untitled"

        return sanitized

    def _handle_collision(self, filename: str) -> str:
        """
        Handle filename collision by appending a counter.

        Args:
            filename: Proposed filename.

        Returns:
            Unique filename.
        """
        if filename not in self._used_names:
            self._used_names.add(filename)
            return filename

        # Split filename and extension
        base, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        counter = 1

        while True:
            new_filename = f"{base}_{counter}.{ext}" if ext else f"{base}_{counter}"
            if new_filename not in self._used_names:
                self._used_names.add(new_filename)
                return new_filename
            counter += 1

    def reset(self) -> None:
        """Reset used filenames (for new channel downloads)."""
        self._used_names.clear()

    def get_used_count(self) -> int:
        """
        Get count of used filenames.

        Returns:
            Number of unique filenames generated.
        """
        return len(self._used_names)