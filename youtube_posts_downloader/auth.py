"""
OAuth2 Authentication handler for YouTube API.
Manages credential flow and token storage.
"""

import os
from pathlib import Path
from typing import Optional

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from .config import Config


class AuthHandler:
    """Handles OAuth2 authentication with YouTube API."""

    def __init__(self, config: Config):
        """
        Initialize authentication handler.

        Args:
            config: Application configuration.
        """
        self.config = config
        self._credentials: Optional[Credentials] = None

    def get_credentials(self, force_refresh: bool = False) -> Credentials:
        """
        Get valid OAuth2 credentials.

        Args:
            force_refresh: Force credential refresh from stored token.

        Returns:
            Valid OAuth2 credentials.

        Raises:
            FileNotFoundError: If client secrets file not found.
            Exception: If authentication fails.
        """
        if not force_refresh and self._credentials and self._credentials.valid:
            return self._credentials

        self._credentials = self._load_or_refresh_credentials()
        return self._credentials

    def _load_or_refresh_credentials(self) -> Credentials:
        """
        Load credentials from file or perform new OAuth2 flow.

        Returns:
            OAuth2 credentials.

        Raises:
            FileNotFoundError: If client secrets file not found.
        """
        token_path = self.config.get_token_path()

        # Try to load existing token
        if token_path.exists():
            credentials = Credentials.from_authorized_user_info(
                self._load_token_json(token_path), self.config.scopes
            )
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                self._save_credentials(credentials)
                return credentials
            elif credentials and credentials.valid:
                return credentials

        # Perform new OAuth2 flow
        return self._run_oauth_flow()

    def _load_token_json(self, path: Path) -> dict:
        """Load token JSON from file."""
        import json
        with open(path, "r") as f:
            return json.load(f)

    def _save_credentials(self, credentials: Credentials) -> None:
        """Save credentials to token file."""
        import json
        token_path = self.config.get_token_path()
        token_path.parent.mkdir(parents=True, exist_ok=True)

        with open(token_path, "w") as f:
            json.dump({
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
            }, f)

    def _run_oauth_flow(self) -> Credentials:
        """
        Run OAuth2 authorization flow.

        Returns:
            OAuth2 credentials after user authorization.

        Raises:
            FileNotFoundError: If client secrets file not found.
        """
        if not self.config.client_secrets_path.exists():
            raise FileNotFoundError(
                f"Client secrets file not found: {self.config.client_secrets_path}\n"
                "Please download OAuth2 client credentials from Google Cloud Console."
            )

        flow = Flow.from_client_secrets_file(
            str(self.config.client_secrets_path),
            scopes=self.config.scopes,
        )

        # Run local server for authorization
        flow.run_local_server(
            port=8080,
            prompt="consent",
            authorization_prompt_message=(
                "Please visit this URL to authorize:\n{url}\n"
                "After authorization, the application will continue automatically."
            ),
        )

        # Save credentials for future use
        self._save_credentials(flow.credentials)
        return flow.credentials

    def revoke_credentials(self) -> None:
        """Revoke OAuth2 credentials."""
        if self._credentials:
            self._credentials.revoke()
            self._credentials = None

        # Remove token file
        token_path = self.config.get_token_path()
        if token_path.exists():
            token_path.unlink()

    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        if self._credentials and self._credentials.valid:
            return True

        # Check if valid token file exists
        token_path = self.config.get_token_path()
        if token_path.exists():
            try:
                credentials = Credentials.from_authorized_user_info(
                    self._load_token_json(token_path), self.config.scopes
                )
                return credentials.valid if credentials else False
            except Exception:
                return False

        return False