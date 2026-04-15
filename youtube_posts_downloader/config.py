"""
Configuration management for YouTube Posts Downloader.
Handles API credentials, OAuth2 settings, and application configuration.
"""

import os
from pathlib import Path
from typing import Optional

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Default output directory for downloaded posts
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "downloaded_posts"

# OAuth2 configuration
OAUTH_CLIENT_SECRETS_FILE = "client_secrets.json"
OAUTH_TOKEN_FILE = "token.json"

# YouTube API configuration
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# YouTube Community Posts scope
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"

# Time range options (in days)
TIME_RANGE_OPTIONS = {
    "inception": None,  # No limit
    "5 years": 5 * 365,
    "3 years": 3 * 365,
    "1 year": 365,
    "6 months": 180,
    "1 month": 30,
    "daily": 1,
}

# Filename sanitization
MAX_FILENAME_LENGTH = 200
FILENAME_INVALID_CHARS = r'[<>:""|?*\\/]'


class Config:
    """Application configuration class."""

    def __init__(
        self,
        client_secrets_path: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize configuration.

        Args:
            client_secrets_path: Path to OAuth2 client secrets JSON file.
            output_dir: Directory to save downloaded posts.
        """
        self.client_secrets_path = client_secrets_path or self._get_default_secrets_path()
        self.output_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR

    def _get_default_secrets_path(self) -> Path:
        """Get default path for client secrets file."""
        return PROJECT_ROOT / OAUTH_CLIENT_SECRETS_FILE

    def get_token_path(self) -> Path:
        """Get path for OAuth token file."""
        return PROJECT_ROOT / OAUTH_TOKEN_FILE

    def ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def scopes(self) -> list[str]:
        """Get OAuth2 scopes."""
        return [YOUTUBE_READONLY_SCOPE]

    @property
    def api_service_name(self) -> str:
        """Get YouTube API service name."""
        return YOUTUBE_API_SERVICE_NAME

    @property
    def api_version(self) -> str:
        """Get YouTube API version."""
        return YOUTUBE_API_VERSION