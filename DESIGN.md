# YouTube Posts Downloader - Design Document

## Overview

This document describes the architecture and design of the YouTube Posts Downloader, a CLI utility that downloads YouTube Community Posts from subscribed channels as individual Markdown files.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph UI_Layer
        CLI[CLI Interface]
        Main[Main Entry Point]
    end

    subgraph Business_Logic_Layer
        TF[Time Filter]
        FN[File Namer]
        MG[Markdown Generator]
    end

    subgraph Data_Layer
        Auth[Auth Handler]
        API[YouTube API Client]
        FS[File System]
    end

    CLI --> TF
    CLI --> FN
    CLI --> MG
    TF --> API
    FN --> API
    MG --> API
    Auth --> API
    API --> FS

    Main --> CLI
```

### Module Structure

```mermaid
classDiagram
    class Config {
        +client_secrets_path
        +output_dir
        +scopes
        +api_service_name
        +ensure_output_dir()
    }

    class AuthHandler {
        +config: Config
        +get_credentials() Credentials
        +revoke_credentials()
        +is_authenticated() bool
    }

    class YouTubeAPIClient {
        +config: Config
        +auth_handler: AuthHandler
        +get_channel_by_name(str) dict
        +get_community_posts(str) Generator
    }

    class TimeFilter {
        +time_range: str
        +cutoff_date: datetime
        +should_include(str) bool
        +filter_posts(list) list
    }

    class FileNamer {
        +generate_filename(str, str) str
        +_sanitize_title(str) str
        +_handle_collision(str) str
    }

    class MarkdownGenerator {
        +generate_markdown(dict, str) str
        +_build_front_matter(dict, str) str
        +_build_content(dict) str
    }

    class CLI {
        +config: Config
        +prompt_channel_name() str
        +prompt_time_range() str
        +run()
    }

    Config --> AuthHandler
    AuthHandler --> YouTubeAPIClient
    YouTubeAPIClient --> TimeFilter
    YouTubeAPIClient --> FileNamer
    TimeFilter --> MarkdownGenerator
    FileNamer --> MarkdownGenerator
    CLI --> Config
    CLI --> AuthHandler
    CLI --> YouTubeAPIClient
```

## User Flow

### Main CLI Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant AuthHandler
    participant YouTubeAPIClient
    participant TimeFilter
    participant FileNamer
    participant MarkdownGenerator

    User->>CLI: Run application
    CLI->>AuthHandler: Initialize
    AuthHandler->>User: OAuth2 flow (browser)
    
    User->>CLI: Enter channel name
    CLI->>YouTubeAPIClient: get_channel_by_name()
    YouTubeAPIClient->>User: Return channel info
    
    User->>CLI: Select time range
    CLI->>TimeFilter: Initialize with range
    
    YouTubeAPIClient->>YouTubeAPIClient: get_all_community_posts()
    YouTubeAPIClient->>CLI: Return all posts
    
    CLI->>TimeFilter: filter_posts()
    TimeFilter->>CLI: Return filtered posts
    
    CLI->>User: Confirm download
    
    loop For each post
        CLI->>FileNamer: generate_filename()
        FileNamer->>CLI: Return filename
        
        CLI->>MarkdownGenerator: save_to_file()
        MarkdownGenerator->>CLI: Save .md file
    end
    
    CLI->>User: Download complete
```

### Authentication Flow

```mermaid
flowchart TD
    A[Start] --> B{Token file exists?}
    B -->|Yes| C{Credentials valid?}
    C -->|Yes| D[Return credentials]
    C -->|No| E{Has refresh token?}
    E -->|Yes| F[Refresh credentials]
    E -->|No| G[Run OAuth2 flow]
    F --> D
    B -->|No| G
    G --> H[Open browser for auth]
    H --> I[User authorizes]
    I --> J[Save token file]
    J --> D
```

## Data Models

### Post Data Structure

```mermaid
erDiagram
    POST ||--o| MEDIA : contains
    POST {
        string id
        string title
        string content
        string published_at
        string channel_id
        string channel_title
    }
    MEDIA {
        string image_url
        string image_alt
        string video_id
        string video_title
        string video_thumbnail
    }
```

### Configuration Settings

```mermaid
erDiagram
    CONFIG ||--|| OAUTH_CONFIG : contains
    CONFIG ||--|| API_CONFIG : contains
    
    CONFIG {
        path client_secrets_path
        path output_dir
        path token_path
    }
    
    OAUTH_CONFIG {
        list scopes
        string token_file
    }
    
    API_CONFIG {
        string service_name
        string api_version
    }
```

## File Output Format

### Markdown File Structure

```mermaid
graph LR
    subgraph "Generated Markdown File"
        FM[YAML Front Matter]
        CT[Content Section]
        
        FM --> MT[Title]
        FM --> MD[Date]
        FM --> MC[Channel Info]
        FM --> MP[Post ID]
        
        CT --> TX[Post Text]
        CT --> MG[Media Gallery]
    end
```

Example output:

```markdown
---
title: Post Title
date: 2023-06-15 10:30:00
channel_id: UC123
channel_title: Test Channel
post_id: post123
filename: 2023-06-15_post-title.md
image_url: https://example.com/image.jpg
video_id: abc123
video_title: My Video
---

Post content here...

![Image](https://example.com/image.jpg)

### My Video

[Watch on YouTube](https://www.youtube.com/watch?v=abc123)
```

## Error Handling

```mermaid
flowchart TD
    A[Operation] --> B{Success?}
    B -->|Yes| C[Continue]
    B -->|No| D{Error Type?}
    
    D -->|Auth Error| E[Show auth instructions]
    D -->|API Error| F[Show API error message]
    D -->|File Error| G[Show file error]
    D -->|Validation Error| H[Show validation message]
    
    E --> I[Exit]
    F --> C
    G --> C
    H --> C
```

## Time Range Options

| Option | Days | Description |
|--------|------|-------------|
| inception | None | All posts from channel creation |
| 5 years | 1825 | Posts from last 5 years |
| 3 years | 1095 | Posts from last 3 years |
| 1 year | 365 | Posts from last year |
| 6 months | 180 | Posts from last 6 months |
| 1 month | 30 | Posts from last month |
| daily | 1 | Posts from today only |

## Dependencies

```
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
oauth2client>=4.1.3
python-dateutil>=2.8.2
pyyaml>=6.0
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
python-dotenv>=1.0.0
```

## Configuration Files

### OAuth2 Client Secrets (client_secrets.json)

```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID",
    "project_id": "YOUR_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost:8080"]
  }
}
```

## Security Considerations

1. **OAuth2 Tokens**: Stored in `token.json` with user read/write permissions only
2. **Client Secrets**: Never committed to version control
3. **API Keys**: Used via OAuth2, no exposed API keys
4. **File Permissions**: Output files created with standard umask

## Future Enhancements

- [ ] Download images locally and update paths
- [ ] Support for video post downloads
- [ ] Batch download multiple channels
- [ ] Export to other formats (PDF, HTML)
- [ ] Progress bar for large downloads
- [ ] Resume interrupted downloads