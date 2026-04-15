# YouTube Posts Downloader

A Python CLI utility that downloads YouTube Community Posts from subscribed channels as individual Markdown files.

## Features

- Interactive CLI with prompts for channel name and time range
- OAuth2 authentication with YouTube API
- Time range filtering (inception, 5 years, 3 years, 1 year, 6 months, 1 month, daily)
- Generates one `.md` file per post
- Filename based on post date and title
- Markdown files include YAML front matter with post metadata

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
# Interactive mode
python -m youtube_posts_downloader

# Specify output directory
python -m youtube_posts_downloader --output ./my-posts

# Specify custom secrets file
python -m youtube_posts_downloader --secrets ./my-secrets.json
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

### Markdown File Format

```markdown
---
title: Post Title
date: 2023-06-15 10:30:00
channel_id: UCxxxxx
channel_title: Channel Name
post_id: xxxxxx
filename: 2023-06-15_post-title.md
---

Post content here...

![Image](https://example.com/image.jpg)
```

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
├── markdown_generator.py # Markdown file generation
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
