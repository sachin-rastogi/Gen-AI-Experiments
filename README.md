# YouTube Posts Downloader

A Python CLI utility that downloads YouTube Community Posts from subscribed channels as individual Markdown files, with optional local image downloading.

## Features

- Interactive CLI with prompts for channel name and time range
- OAuth2 authentication with YouTube API
- Time range filtering (inception, 5 years, 3 years, 1 year, 6 months, 1 month, daily)
- Generates one `.md` file per post
- Filename based on post date and title
- Markdown files include YAML front matter with post metadata
- **Download images locally** - Images and video thumbnails are downloaded to a local `images/` folder
- **Offline viewing** - Markdown files work without internet connection (when images are local)

## Installation

```bash
pip install -r requirements.txt
```

## Setup

### 1. Create OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Go to Credentials > Create Credentials > OAuth2 Client ID
5. Create Desktop Application credentials
6. Download the JSON file and save as `client_secrets.json` in project root

### 2. Configure

The application expects `client_secrets.json` in the project root by default. You can specify a different path using the `--secrets` option.

## Usage

```bash
# Interactive mode (with local image downloading)
python -m youtube_posts_downloader

# Interactive mode without downloading images
python -m youtube_posts_downloader --no-images

# Specify output directory
python -m youtube_posts_downloader --output ./my-posts

# Specify custom secrets file
python -m youtube_posts_downloader --secrets ./my-secrets.json

# Combine options
python -m youtube_posts_downloader --output ./my-posts --no-images
```

### CLI Prompts

1. **Channel Name**: Enter the channel name/handle (e.g., `@username` or `Channel Name`)
2. **Time Range**: Select from available options:
   - 1. inception (all posts)
   - 2. 5 years
   - 3. 3 years
   - 4. 1 year
   - 5. 6 months
   - 6. 1 month
   - 7. daily
3. **Confirm**: Confirm download before starting

## Output

Each post is saved as a Markdown file with the format:

```
{date}_{sanitized-title}.md
```

Example: `2023-06-15_community-update.md`

### Directory Structure

```
output_directory/
├── 2023-06-15_post-1.md
├── 2023-06-16_post-2.md
├── 2023-06-17_post-3.md
└── images/
    ├── abc123def456.jpg    # Downloaded images
    ├── ghi789jkl012.jpg
    └── mno345pqr678.png    # Video thumbnails
```

### Markdown File Format

```markdown
---
title: Post Title
date: 2023-06-15 10:30:00
channel_id: UCxxxxx
channel_title: Channel Name
post_id: xxxxxx
filename: 2023-06-15_post-title.md
image_url: https://example.com/original-image.jpg
video_id: abc123
video_title: My Video
---

Post content here...

![Image](images/abc123def456.jpg)

### My Video

[Watch on YouTube](https://www.youtube.com/watch?v=abc123)

[![Video Thumbnail](images/ghi789jkl012.jpg)](https://www.youtube.com/watch?v=abc123)
```

## Options

| Option | Description |
|--------|-------------|
| `-o, --output DIR` | Output directory (default: ./downloaded_posts) |
| `-s, --secrets FILE` | OAuth2 client secrets JSON file |
| `--no-images` | Don't download images locally (keep remote URLs) |
| `--version` | Show version number |
| `-h, --help` | Show help message |

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=youtube_posts_downloader --cov-report=html

# Run specific test file
pytest tests/test_time_filter.py -v
```

## Project Structure

```
youtube_posts_downloader/
├── __init__.py          # Package init
├── config.py            # Configuration management
├── auth.py              # OAuth2 authentication
├── api_client.py        # YouTube API wrapper
├── time_filter.py       # Date range filtering
├── file_namer.py        # Filename generation
├── markdown_generator.py # Markdown file generation (with image download)
├── cli.py               # CLI interface
└── main.py              # Entry point

tests/
├── conftest.py          # Test fixtures
├── test_time_filter.py  # Time filter tests
├── test_file_namer.py   # File namer tests
├── test_markdown_generator.py
└── test_cli.py          # CLI tests
```

## License

MIT License
