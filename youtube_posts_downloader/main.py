#!/usr/bin/env python3
"""
YouTube Posts Downloader - Main Entry Point

A CLI utility that downloads YouTube Community Posts from subscribed channels
as individual markdown files.
"""

import sys
import argparse
from pathlib import Path

from youtube_posts_downloader.config import Config
from youtube_posts_downloader.cli import CLI


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Download YouTube Community Posts as Markdown files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m youtube_posts_downloader              # Interactive mode
  python -m youtube_posts_downloader --output ./posts  # Custom output directory
  python -m youtube_posts_downloader --secrets ./secrets.json  # Custom secrets file
        """
    )

    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output directory for downloaded posts (default: ./downloaded_posts)",
    )

    parser.add_argument(
        "-s", "--secrets",
        default=None,
        help="Path to OAuth2 client secrets JSON file",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="YouTube Posts Downloader v1.0.0",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Create configuration
    config = Config(
        client_secrets_path=args.secrets,
        output_dir=args.output,
    )

    # Run CLI
    cli = CLI(config)
    cli.run()


if __name__ == "__main__":
    main()