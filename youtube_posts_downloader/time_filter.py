"""
Time filter module for filtering posts by date range.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from dateutil import parser as date_parser


class TimeFilter:
    """Handles date range filtering for posts."""

    # Time range options in days
    RANGE_OPTIONS = {
        "inception": None,  # No limit - all posts
        "5 years": 5 * 365,
        "3 years": 3 * 365,
        "1 year": 365,
        "6 months": 180,
        "1 month": 30,
        "daily": 1,
    }

    def __init__(self, time_range: str = "inception"):
        """
        Initialize time filter.

        Args:
            time_range: Time range option string.
        """
        self.time_range = time_range
        self.cutoff_date = self._calculate_cutoff_date()

    def _calculate_cutoff_date(self) -> Optional[datetime]:
        """
        Calculate cutoff date based on time range option.

        Returns:
            Cutoff datetime or None for inception (no limit).
        """
        days = self.RANGE_OPTIONS.get(self.time_range)

        if days is None:
            # Inception - no cutoff
            return None

        if self.time_range == "daily":
            # For daily, get start of today
            today = datetime.now()
            return today.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

        # Calculate cutoff date
        cutoff = datetime.now() - timedelta(days=days)
        return cutoff.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

    def should_include(self, published_at: str) -> bool:
        """
        Check if a post should be included based on its publish date.

        Args:
            published_at: ISO 8601 date string.

        Returns:
            True if post should be included, False otherwise.
        """
        if self.cutoff_date is None:
            # Inception - include all
            return True

        try:
            # Parse ISO 8601 date string
            post_date = date_parser.parse(published_at)
            return post_date >= self.cutoff_date
        except (ValueError, TypeError):
            # If we can't parse the date, include the post
            return True

    def filter_posts(self, posts: list[dict]) -> list[dict]:
        """
        Filter posts by date range.

        Args:
            posts: List of post dictionaries with 'published_at' key.

        Returns:
            Filtered list of posts.
        """
        if self.cutoff_date is None:
            return posts

        return [post for post in posts if self.should_include(post.get("published_at", ""))]

    @classmethod
    def get_available_ranges(cls) -> list[str]:
        """
        Get list of available time range options.

        Returns:
            List of time range option strings.
        """
        return list(cls.RANGE_OPTIONS.keys())

    @classmethod
    def is_valid_range(cls, time_range: str) -> bool:
        """
        Check if time range option is valid.

        Args:
            time_range: Time range option string.

        Returns:
            True if valid, False otherwise.
        """
        return time_range in cls.RANGE_OPTIONS

    def get_cutoff_description(self) -> str:
        """
        Get human-readable description of the cutoff date.

        Returns:
            Description string.
        """
        if self.cutoff_date is None:
            return "All posts (inception)"

        return f"Posts from {self.cutoff_date.strftime('%Y-%m-%d')} onwards"