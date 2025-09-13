# YTFetcher
[![codecov](https://codecov.io/gh/kaya70875/ytfetcher/branch/main/graph/badge.svg)](https://codecov.io/gh/kaya70875/ytfetcher)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/ytfetcher?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/ytfetcher)
[![PyPI version](https://img.shields.io/pypi/v/ytfetcher)](https://pypi.org/project/ytfetcher/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> ⚡ Turn hours of YouTube videos into clean, structured text in minutes.

**YTFetcher** is a Python tool for fetching YouTube video transcripts in bulk, along with metadata like titles, publish dates, and descriptions.  
Perfect for **NLP datasets, search indexes, or content analysis apps**.  
⭐ *If you find this useful, please star the repo!*

---

## 📚 Table of Contents
- [Installation](#installation)
- [Quick CLI Usage](#quick-cli-usage)
- [Features](#features)
- [Basic Usage (Python API)](#basic-usage-python-api)
- [Fetching With Custom Video IDs](#fetching-with-custom-video-ids)
- [Exporting](#exporting)
- [Other Methods](#other-methods)
- [Proxy Configuration](#proxy-configuration)
- [Advanced HTTP Configuration (Optional)](#advanced-http-configuration-optional)
- [CLI (Advanced)](#cli-advanced)
- [Contributing](#contributing)
- [Running Tests](#running-tests)
- [Related Projects](#related-projects)
- [License](#license)

---

## Installation
Install from PyPI:
```bash
pip install ytfetcher
```

---

## 🚀 Quick CLI Usage
Fetch 50 video transcripts + metadata from a channel and save as JSON:
```bash
ytfetcher from_channel --api-key YOUR_API_KEY -c TheOffice -m 50 -f json
```
👉 [Get an API Key here](https://console.cloud.google.com/apis/api/youtube.googleapis.com).

---

## ✨ Features
- Fetch full transcripts from a YouTube channel.
- Get video metadata: title, description, thumbnails, published date.
- Async support for high performance.
- Export fetched data as txt, csv or json.
- CLI support.

---

## Basic Usage (Python API)

**Note:** When specifying the channel, you must provide the exact **channel handle** without the `@` symbol, channel URL, or channel display name.  
For example, use `TheOffice` instead of `@TheOffice` or `https://www.youtube.com/c/TheOffice`.

### How to find the channel handle for a YouTube channel

1. Go to the YouTube channel page.
2. Look at the URL in your browser's address bar.
3. The handle is the part that comes right after `https://www.youtube.com/@`  

Ytfetcher uses **YoutubeV3 API** to get channel details and video id's so you have to create your API key from Google Cloud Console [In here](https://console.cloud.google.com/apis/api/youtube.googleapis.com).

Also keep in mind that you have a quota limit for **YoutubeV3 API**, but for basic usage quota isn't generally a concern.

Here how you can get transcripts and metadata informations like channel name, description, publishedDate etc. from a single channel with `from_channel` method:

```python
from ytfetcher import YTFetcher
from ytfetcher import ChannelData # Or ytfetcher.models import ChannelData
import asyncio

fetcher = YTFetcher.from_channel(
    api_key='your-youtubev3-api-key', 
    channel_handle="TheOffice", 
    max_results=2)

async def get_channel_data() -> list[ChannelData]:
    channel_data = await fetcher.fetch_youtube_data()
    return channel_data

if __name__ == '__main__':
    data = asyncio.run(get_channel_data())
    print(data)
```

---

This will return a list of `ChannelData`. Here's how it's looks like:

```python
[
ChannelData(
    video_id='video1',
    transcripts=[
        Transcript(
            text="Hey there",
            start=0.0,
            duration=1.54
        ),
        Transcript(
            text="Happy coding!",
            start=1.56,
            duration=4.46
        )
    ]
    metadata=Snippet(
        title='VideoTitle',
        description='VideoDescription',
        publishedAt='02.04.2025',
        channelId='id123',
        thumbnails=Thumbnails(
            default=Thumbnail(
                url:'thumbnail_url',
                width: 124,
                height: 124
            )
        )
    )
),
# Other ChannelData objects...
]
```

---

## Fetching With Custom Video IDs

You can also initialize `ytfetcher` with custom video id's using `from_video_ids` method.

```python
from ytfetcher import YTFetcher
import asyncio

fetcher = YTFetcher.from_video_ids(
    api_key='your-youtubev3-api-key', 
    video_ids=['video1', 'video2', 'video3'])

# Rest is same ...
```

---

## Exporting

To export data you can use `Exporter` class. Exporter allows you to export `ChannelData` with formats like **csv**, **json** or **txt**.

```python
from ytfetcher.services import Exporter

channel_data = await fetcher.fetch_youtube_data()

exporter = Exporter(
    channel_data=channel_data,
    allowed_metadata_list=['title', 'publishedAt'],   # You can customize this
    timing=True,                                      # Include transcript start/duration
    filename='my_export',                             # Base filename
    output_dir='./exports'                            # Optional export directory
)

exporter.export_as_json()  # or .export_as_txt(), .export_as_csv()
```

---

## Other Methods

You can also fetch only transcript data or metadata with video ID's using `fetch_transcripts` and `fetch_snippets` methods.

### Fetch Transcripts

```python
from ytfetcher import VideoTranscript

fetcher = YTFetcher.from_channel(
    api_key='your-youtubev3-api-key', 
    channel_handle="TheOffice", 
    max_results=2)

async def get_transcript_data() -> list[VideoTranscript]:
    transcript_data = await fetcher.fetch_transcripts()
    return transcript_data

if __name__ == '__main__':
    data = asyncio.run(get_transcript_data())
    print(data)
```

### Fetch Snippets

```python
from ytfetcher import VideoMetadata

# Init ytfetcher ...

def get_metadata() -> list[VideoMetadata]:
    metadata = fetcher.fetch_snippets()
    return metadata

if __name__ == '__main__':
    get_metadata()
```

---

## Proxy Configuration

`YTFetcher` supports proxy usage for fetching YouTube transcripts by leveraging the built-in proxy configuration support from [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/).

To configure proxies, you can pass a proxy config object from `ytfecher.config` directly to `YTFetcher`:

```python
from ytfetcher import YTFetcher
from ytfetcher.config import GenericProxyConfig, WebshareProxyConfig

fetcher = YTFetcher.from_channel(
    api_key="your-api-key",
    channel_handle="TheOffice",
    max_results=3,
    proxy_config=GenericProxyConfig() | WebshareProxyConfig()
)
```

---

## Advanced HTTP Configuration (Optional)

You can pass a custom timeout or headers (e.g., user-agent) to `YTFetcher` using `HTTPConfig`:

```python
from ytfetcher import YTFetcher
from ytfetcher.config import HTTPConfig

custom_config = HTTPConfig(
    timeout=4.0,
    headers={"User-Agent": "ytfetcher/1.0"}
)

fetcher = YTFetcher.from_channel(
    api_key="your-key",
    channel_handle="TheOffice",
    max_results=10,
    http_config=custom_config
)
```

---

## CLI (Advanced)

### Basic Usage

```bash
ytfetcher from_channel --api-key <API_KEY> -c <CHANNEL_HANDLE> -m <MAX_RESULTS> -f <FORMAT>
```

Example:

```bash
ytfetcher from_channel --api-key <API_KEY> -c <CHANNEL_HANDLE> -m 20 -f json
```

### Fetching by Video IDs

```bash
ytfetcher from_video_ids --api-key <API_KEY> -v video_id1 video_id2 ... -f json
```

### Output Example

```json
[
  {
    "video_id": "abc123",
    "metadata": {
      "title": "Video Title",
      "description": "Video Description",
      "publishedAt": "2023-07-01T12:00:00Z"
    },
    "transcripts": [
      {"text": "Welcome!", "start": 0.0, "duration": 1.2}
    ]
  }
]
```

### Setting API Key Globally In CLI

```bash
ytfetcher config <YOUR_API_KEY>
ytfetcher from_channel -c <CHANNEL_HANDLE>
```

### Using Webshare Proxy

```bash
ytfetcher from_channel --api-key <API_KEY> -c <CHANNEL_HANDLE> -f json   --webshare-proxy-username "<USERNAME>"   --webshare-proxy-password "<PASSWORD>"
```

### Using Custom Proxy

```bash
ytfetcher from_channel --api-key <API_KEY> -c <CHANNEL_HANDLE> -f json   --http-proxy "http://user:pass@host:port"   --https-proxy "https://user:pass@host:port"
```

### Using Custom HTTP Config

```bash
ytfetcher from_channel --api-key <API_KEY> -c <CHANNEL_HANDLE>   --http-timeout 4.2   --http-headers "{'key': 'value'}"
```

---

## Contributing

To install this project locally:

```bash
git clone https://github.com/kaya70875/ytfetcher.git
cd ytfetcher
poetry install
```

---

## Running Tests

```bash
poetry run pytest
```

---

## Related Projects

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

---

## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.

---

⭐ If you find this useful, please star the repo or open an issue with feedback!
