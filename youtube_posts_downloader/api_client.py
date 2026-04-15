"""
YouTube API client wrapper.
Handles channel and community post fetching.
"""

from datetime import datetime
from typing import Optional, Generator

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import Config
from .auth import AuthHandler


class YouTubeAPIClient:
    """YouTube Data API v3 client wrapper."""

    def __init__(self, config: Config, auth_handler: AuthHandler):
        """
        Initialize YouTube API client.

        Args:
            config: Application configuration.
            auth_handler: OAuth2 authentication handler.
        """
        self.config = config
        self.auth_handler = auth_handler
        self._service = None

    @property
    def service(self):
        """Get or build YouTube API service."""
        if self._service is None:
            credentials = self.auth_handler.get_credentials()
            self._service = build(
                self.config.api_service_name,
                self.config.api_version,
                credentials=credentials,
                cache_discovery=False,
            )
        return self._service

    def get_channel_by_name(self, channel_name: str) -> Optional[dict]:
        """
        Get channel ID by handle/username.

        Args:
            channel_name: Channel name/handle (e.g., '@username' or 'username').

        Returns:
            Channel data dict or None if not found.
        """
        # Handle different channel name formats
        if not channel_name.startswith("@"):
            search_query = channel_name
        else:
            search_query = channel_name[1:]

        try:
            response = self.service.search().list(
                part="snippet",
                q=search_query,
                type="channel",
                maxResults=5,
            ).execute()

            channels = response.get("items", [])
            for channel in channels:
                # Match by exact handle or title
                channel_handle = channel["snippet"].get("customUrl", "").lower()
                channel_title = channel["snippet"].get("title", "").lower()
                search_lower = search_query.lower()

                if channel_handle == f"@{search_lower}" or search_lower in channel_title:
                    return {
                        "id": channel["snippet"]["channelId"],
                        "title": channel["snippet"]["title"],
                        "description": channel["snippet"].get("description", ""),
                    }

            # Return first result if no exact match
            if channels:
                return {
                    "id": channels[0]["snippet"]["channelId"],
                    "title": channels[0]["snippet"]["title"],
                    "description": channels[0]["snippet"].get("description", ""),
                }

            return None

        except HttpError as e:
            raise Exception(f"Failed to search channel: {e.error_details}")

    def get_channel_id_from_handle(self, channel_handle: str) -> Optional[str]:
        """
        Get channel ID from channel handle.

        Args:
            channel_handle: Channel handle (e.g., '@username').

        Returns:
            Channel ID or None if not found.
        """
        if not channel_handle.startswith("@"):
            channel_handle = f"@{channel_handle}"

        try:
            # Use search to find the channel
            response = self.service.search().list(
                part="snippet",
                q=channel_handle[1:],  # Remove @ prefix
                type="channel",
                maxResults=1,
            ).execute()

            items = response.get("items", [])
            if items:
                return items[0]["snippet"]["channelId"]

            return None

        except HttpError as e:
            raise Exception(f"Failed to get channel ID: {e.error_details}")

    def get_community_posts(
        self,
        channel_id: str,
        max_results: int = 50,
    ) -> Generator[dict, None, None]:
        """
        Fetch community posts from a channel.

        Args:
            channel_id: YouTube channel ID.
            max_results: Maximum number of posts to fetch per request.

        Yields:
            Post data dictionaries.
        """
        next_page_token = None

        while True:
            try:
                response = self.service.activities().list(
                    part="contentDetails,snippet",
                    channelId=channel_id,
                    mine=False,
                    maxResults=max_results,
                    pageToken=next_page_token,
                ).execute()

                for item in response.get("items", []):
                    # Only yield items with community post content
                    if "contentDetails" in item:
                        community = item["contentDetails"].get("community")
                        if community:
                            yield self._parse_community_post(item)

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break

            except HttpError as e:
                raise Exception(f"Failed to fetch posts: {e.error_details}")

    def _parse_community_post(self, item: dict) -> dict:
        """
        Parse community post from API response.

        Args:
            item: Activity item from YouTube API.

        Returns:
            Parsed post data dictionary.
        """
        snippet = item.get("snippet", {})
        community = item["contentDetails"].get("community", {})

        # Extract post text
        post_text = ""
        if "post" in community:
            post_text = community["post"].get("message", "")

        # Extract media if present
        media_info = {}
        if "image" in community:
            images = community["image"]
            if "items" in images and images["items"]:
                media_info["image_url"] = images["items"][0].get("url")
                media_info["image_alt"] = images["items"][0].get("altText", "")

        if "video" in community:
            video = community["video"]
            media_info["video_id"] = video.get("videoId")
            media_info["video_title"] = video.get("title")
            media_info["video_thumbnail"] = video.get("thumbnails", {}).get("medium", {}).get("url")

        # Extract creation time
        published_at = snippet.get("publishedAt", "")

        return {
            "id": item.get("id", ""),
            "title": post_text.split("\n")[0][:100] if post_text else "Community Post",
            "content": post_text,
            "published_at": published_at,
            "channel_id": snippet.get("channelId", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "media": media_info,
        }

    def get_all_community_posts(self, channel_id: str) -> list[dict]:
        """
        Get all community posts from a channel.

        Args:
            channel_id: YouTube channel ID.

        Returns:
            List of post data dictionaries.
        """
        posts = list(self.get_community_posts(channel_id))
        return posts