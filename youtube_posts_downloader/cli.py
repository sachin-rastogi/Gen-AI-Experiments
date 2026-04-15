"""
Command-line interface for YouTube Posts Downloader.
Handles user prompts and interactions.
"""

import sys
from typing import Optional

from .config import Config, TIME_RANGE_OPTIONS
from .time_filter import TimeFilter
from .api_client import YouTubeAPIClient
from .auth import AuthHandler
from .file_namer import FileNamer
from .markdown_generator import MarkdownGenerator


class CLI:
    """Interactive command-line interface for the downloader."""

    def __init__(self, config: Optional[Config] = None, download_images: bool = True):
        """
        Initialize CLI.

        Args:
            config: Optional configuration object.
            download_images: Whether to download images locally (default: True).
        """
        self.config = config or Config()
        self.download_images = download_images
        self.auth_handler = None
        self.api_client = None

    def initialize(self) -> None:
        """Initialize API client and authenticate."""
        self.auth_handler = AuthHandler(self.config)
        self.api_client = YouTubeAPIClient(self.config, self.auth_handler)

    def prompt_channel_name(self) -> str:
        """
        Prompt user for channel name.

        Returns:
            Channel name string.
        """
        print("\n" + "=" * 50)
        print("YouTube Posts Downloader")
        print("=" * 50)
        print("\nEnter the channel name/handle to download posts from.")
        print("Examples: '@username' or 'Channel Name'")
        print("\nPress Ctrl+C to exit at any time.")
        print("-" * 50)

        while True:
            channel_name = input("\nChannel name: ").strip()

            if channel_name:
                return channel_name

            print("Error: Please enter a valid channel name.")

    def prompt_time_range(self) -> str:
        """
        Prompt user for time range option.

        Returns:
            Time range option string.
        """
        print("\n" + "-" * 50)
        print("Select time range for posts:")
        print("-" * 50)

        ranges = TimeFilter.get_available_ranges()
        for i, option in enumerate(ranges, 1):
            print(f"  {i}. {option}")

        print()

        while True:
            choice = input("Enter option number (1-{}): ".format(len(ranges))).strip()

            try:
                index = int(choice) - 1
                if 0 <= index < len(ranges):
                    return ranges[index]
                print(f"Please enter a number between 1 and {len(ranges)}")
            except ValueError:
                print("Please enter a valid number.")

    def confirm_download(
        self,
        channel_name: str,
        time_range: str,
        post_count: int,
    ) -> bool:
        """
        Confirm download with user.

        Args:
            channel_name: Channel name.
            time_range: Selected time range.
            post_count: Number of posts to download.

        Returns:
            True if user confirms, False otherwise.
        """
        print("\n" + "-" * 50)
        print("Download Summary:")
        print("-" * 50)
        print(f"  Channel: {channel_name}")
        print(f"  Time Range: {time_range}")
        print(f"  Posts to download: {post_count}")
        print("-" * 50)

        while True:
            confirm = input("\nProceed with download? (y/n): ").strip().lower()

            if confirm in ("y", "yes"):
                return True
            elif confirm in ("n", "no"):
                return False
            print("Please enter 'y' or 'n'.")

    def run(self) -> None:
        """Run the CLI application."""
        try:
            # Initialize and authenticate
            print("\nInitializing...")
            self.initialize()

            # Get channel name
            channel_name = self.prompt_channel_name()

            # Get time range
            time_range = self.prompt_time_range()

            # Search for channel
            print(f"\nSearching for channel: {channel_name}...")
            channel = self.api_client.get_channel_by_name(channel_name)

            if not channel:
                print(f"\nError: Channel '{channel_name}' not found.")
                return

            print(f"\nFound channel: {channel['title']}")

            # Fetch posts
            print("\nFetching community posts...")
            all_posts = self.api_client.get_all_community_posts(channel["id"])
            print(f"Found {len(all_posts)} total posts")

            # Filter by time range
            time_filter = TimeFilter(time_range)
            filtered_posts = time_filter.filter_posts(all_posts)
            print(f"Filtered to {len(filtered_posts)} posts ({time_filter.get_cutoff_description()})")

            if not filtered_posts:
                print("\nNo posts found in the selected time range.")
                return

            # Confirm download
            if not self.confirm_download(channel["title"], time_range, len(filtered_posts)):
                print("\nDownload cancelled.")
                return

            # Ensure output directory exists
            self.config.ensure_output_dir()

            # Generate files
            file_namer = FileNamer()
            markdown_gen = MarkdownGenerator(self.api_client, download_images=self.download_images)

            print(f"\nSaving files to: {self.config.output_dir}")
            print("-" * 50)

            for post in filtered_posts:
                filename = file_namer.generate_filename(
                    post["title"],
                    post["published_at"],
                )
                saved_path = markdown_gen.save_to_file(
                    post,
                    filename,
                    str(self.config.output_dir),
                )
                print(f"  Saved: {filename}")

            print("-" * 50)
            print(f"\nDownload complete! {len(filtered_posts)} files saved.")

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            print(f"\nError: {str(e)}")
            sys.exit(1)