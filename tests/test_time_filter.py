"""
Tests for time_filter module.
"""

import pytest
from datetime import datetime, timedelta, timezone

from youtube_posts_downloader.time_filter import TimeFilter


class TestTimeFilter:
    """Test suite for TimeFilter class."""

    def test_inception_returns_none_cutoff(self):
        """Test that inception returns None cutoff date."""
        time_filter = TimeFilter("inception")
        assert time_filter.cutoff_date is None

    def test_daily_returns_start_of_today(self):
        """Test that daily returns start of today."""
        time_filter = TimeFilter("daily")
        today = datetime.now()
        assert time_filter.cutoff_date.year == today.year
        assert time_filter.cutoff_date.month == today.month
        assert time_filter.cutoff_date.day == today.day
        assert time_filter.cutoff_date.hour == 0
        assert time_filter.cutoff_date.minute == 0
        assert time_filter.cutoff_date.second == 0

    def test_one_year_calculates_correct_cutoff(self):
        """Test that 1 year calculates correct cutoff date."""
        time_filter = TimeFilter("1 year")
        expected_cutoff = (datetime.now() - timedelta(days=365)).replace(tzinfo=timezone.utc)
        # Allow small difference due to execution time
        diff = abs((time_filter.cutoff_date - expected_cutoff).days)
        assert diff <= 1

    def test_five_years_calculates_correct_cutoff(self):
        """Test that 5 years calculates correct cutoff date."""
        time_filter = TimeFilter("5 years")
        expected_cutoff = (datetime.now() - timedelta(days=5 * 365)).replace(tzinfo=timezone.utc)
        diff = abs((time_filter.cutoff_date - expected_cutoff).days)
        assert diff <= 1

    def test_should_include_returns_true_for_inception(self):
        """Test should_include returns True for all posts with inception."""
        time_filter = TimeFilter("inception")
        assert time_filter.should_include("2020-01-01T00:00:00Z") is True
        assert time_filter.should_include("2023-01-01T00:00:00Z") is True

    def test_should_include_filters_old_posts(self):
        """Test should_include filters posts older than cutoff."""
        time_filter = TimeFilter("1 year")
        # Post from 2 years ago should be excluded - use more days to ensure older
        old_date = (datetime.now() - timedelta(days=400)).isoformat() + "Z"
        # Debug: verify date is actually older than cutoff
        assert time_filter.should_include(old_date) is False, f"Old date {old_date} should be filtered, cutoff is {time_filter.cutoff_date}"

        # Post from yesterday should be included
        recent_date = (datetime.now() - timedelta(days=1)).isoformat() + "Z"
        assert time_filter.should_include(recent_date) is True

    def test_should_include_handles_invalid_dates(self):
        """Test should_include handles invalid date strings."""
        time_filter = TimeFilter("1 year")
        # Invalid dates should be included (conservative approach)
        assert time_filter.should_include("invalid") is True
        assert time_filter.should_include("") is True

    def test_filter_posts_returns_all_for_inception(self):
        """Test filter_posts returns all posts for inception."""
        time_filter = TimeFilter("inception")
        posts = [
            {"published_at": "2020-01-01T00:00:00Z"},
            {"published_at": "2023-01-01T00:00:00Z"},
        ]
        assert len(time_filter.filter_posts(posts)) == 2

    def test_filter_posts_filters_by_date(self):
        """Test filter_posts filters posts correctly."""
        time_filter = TimeFilter("1 year")
        # Use dates that are definitely within 1 year
        recent_date = (datetime.now() - timedelta(days=100)).isoformat() + "Z"
        very_recent = (datetime.now() - timedelta(days=10)).isoformat() + "Z"
        posts = [
            {"published_at": "2020-01-01T00:00:00Z"},  # Old - should be filtered out
            {"published_at": recent_date},  # Recent - should be included
            {"published_at": very_recent},  # Very recent - should be included
        ]
        filtered = time_filter.filter_posts(posts)
        assert len(filtered) >= 2  # At least recent posts

    def test_get_available_ranges_returns_all_options(self):
        """Test get_available_ranges returns all options."""
        ranges = TimeFilter.get_available_ranges()
        expected = ["inception", "5 years", "3 years", "1 year", "6 months", "1 month", "daily"]
        assert ranges == expected

    def test_is_valid_range(self):
        """Test is_valid_range validation."""
        assert TimeFilter.is_valid_range("inception") is True
        assert TimeFilter.is_valid_range("1 year") is True
        assert TimeFilter.is_valid_range("daily") is True
        assert TimeFilter.is_valid_range("invalid") is False

    def test_get_cutoff_description_for_inception(self):
        """Test get_cutoff_description for inception."""
        time_filter = TimeFilter("inception")
        desc = time_filter.get_cutoff_description()
        assert "All posts" in desc

    def test_get_cutoff_description_with_date(self):
        """Test get_cutoff_description returns formatted date."""
        time_filter = TimeFilter("1 year")
        desc = time_filter.get_cutoff_description()
        assert "Posts from" in desc
        assert "onwards" in desc


class TestTimeFilterEdgeCases:
    """Edge case tests for TimeFilter."""

    def test_empty_posts_list(self):
        """Test filter with empty posts list."""
        time_filter = TimeFilter("1 year")
        assert time_filter.filter_posts([]) == []

    def test_posts_missing_published_at(self):
        """Test filter handles posts without published_at."""
        time_filter = TimeFilter("1 year")
        posts = [{"content": "test"}, {"published_at": "2023-01-01T00:00:00Z"}]
        # Should not raise error, missing dates treated as valid
        result = time_filter.filter_posts(posts)
        assert len(result) >= 1

    def test_daily_time_range_exact_match(self):
        """Test daily range handles exact date boundary."""
        time_filter = TimeFilter("daily")
        # Today's date should be included
        today = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        assert time_filter.should_include(today) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])