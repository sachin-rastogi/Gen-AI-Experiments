"""
YouTube Posts Downloader Package

A CLI utility that downloads YouTube Community Posts from subscribed channels
as individual markdown files.
"""

__version__ = "1.0.0"
__author__ = "YouTube Posts Downloader"

from .config import Config
from .auth import AuthHandler
from .api_client import YouTubeAPIClient
from .time_filter import TimeFilter
from .file_namer import FileNamer
from .markdown_generator import MarkdownGenerator
from .cli import CLI

__all__ = [
    "Config",
    "AuthHandler",
    "YouTubeAPIClient",
    "TimeFilter",
    "FileNamer",
    "MarkdownGenerator",
    "CLI",
]