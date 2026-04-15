"""
Test configuration and fixtures.
"""

import pytest
import os
import tempfile
from pathlib import Path

from youtube_posts_downloader.config import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config(temp_dir):
    """Create a mock configuration for testing."""
    config = Config(output_dir=str(temp_dir))
    return config


@pytest.fixture
def sample_post():
    """Sample post data for testing."""
    return {
        "id": "post123",
        "title": "Test Post Title",
        "content": "This is the post content.",
        "published_at": "2023-06-15T10:30:00Z",
        "channel_id": "UC123",
        "channel_title": "Test Channel",
        "media": {
            "image_url": "https://example.com/image.jpg",
            "image_alt": "Test Image",
        },
    }


@pytest.fixture
def sample_posts_list():
    """Sample list of posts for testing."""
    return [
        {
            "id": "post1",
            "title": "Post 1",
            "content": "Content 1",
            "published_at": "2020-01-01T00:00:00Z",
            "channel_id": "UC123",
            "channel_title": "Test",
        },
        {
            "id": "post2",
            "title": "Post 2",
            "content": "Content 2",
            "published_at": "2023-06-15T10:30:00Z",
            "channel_id": "UC123",
            "channel_title": "Test",
        },
    ]