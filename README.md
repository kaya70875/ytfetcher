# YTFetcher

**YTFetcher** is a Python tool for fetching YouTube video transcripts in bulk, along with rich metadata like titles, publish dates, and descriptions. Ideal for building NLP datasets, search indexes, or powering content analysis apps.

---

## 📚 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Fetching With Custom Video IDs](#fetching-with-custom-video-ids)
- [Exporting](#exporting)
- [Proxy Configuration](#proxy-configuration)
- [Advanced HTTP Configuration](#advanced-http-configuration-optional)
- [CLI](#cli)
- [Contributing](#contributing)
- [Running Tests](#running-tests)
- [Related Projects](#related-projects)
- [License](#license)

---

## Features

- Fetch full transcripts from a YouTube channel.
- Get video metadata: title, description, thumbnails, published date.
- Async support for high performance.
- Export fetched data as txt, csv or json.
- CLI support.

---

## Installation

It is recommended to install this package by using pip:

```bash
pip install ytfetcher
```

## Basic Usage

Ytfetcher uses **YoutubeV3 API** to get channel details and video id's so you have to create your API key from Google Cloud Console [In here](https://console.cloud.google.com/apis/api/youtube.googleapis.com).

Also keep in mind that you have a quota limit for **YoutubeV3 API**, but for basic usage quota isn't generally a concern.

Here how you can get transcripts and metadata informations like channel name, description, publishedDate etc. from a single channel with `from_channel` method:

```python
from ytfetcher import YTFetcher
import asyncio

fetcher = YTFetcher.from_channel(
    api_key='your-youtubev3-api-key', 
    channel_handle="TheOffice", 
    max_results=2)

async def get_channel_data() -> ChannelData:
    channel_data = await fetcher.fetch_youtube_data()

if __name__ == '__main__':
    asyncio.run(get_channel_data())
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

## Fetching With Custom Video IDs

You can also initialize `ytfetcher` with custom video id's using `from_video_ids` method.

```python
from ytfetcher import YTFetcher
import asyncio

fetcher = YTFetcher.from_video_ids(
    api_key='your-youtubev3-api-key', 
    video_ids=['video1', 'video2', 'video3']) # Here we initialized ytfetcher with from_video_ids method.

# Rest is same ...
```

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

## Proxy Configuration

`YTFetcher` supports proxy usage for fetching YouTube transcripts by leveraging the built-in proxy configuration support from [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/).

To configure proxies, you can pass a proxy config object from `youtube_transcript_api.proxies` directly to `YTFetcher`:

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

## Advanced HTTP Configuration (Optional)

You can pass a custom timeout or headers (e.g., user-agent) to `YTFetcher` using `HTTPConfig`:

```python
from ytfetcher import YTFetcher
from ytfetcher.config import HTTPConfig
import httpx

custom_config = HTTPConfig(
    timeout=httpx.Timeout(4.0),
    headers={"User-Agent": "ytfetcher/1.0"} # Doesn't recommended to change this unless you have a custom strong headers.
)

fetcher = YTFetcher.from_channel(
    api_key="your-key",
    channel_handle="TheOffice",
    max_results=10,
    http_config=custom_config
)
```

## CLI

### Basic Usage

```bash
ytfetcher from_channel <API_KEY> -c <CHANNEL_HANDLE> -m <MAX_RESULTS> -f <FORMAT>
```

Basic usage example:

```bash
ytfetcher from_channel your-api-key -c "channelname" -m 20 -f json
```

### Output Example

```json
[
  {
    "video_id": "abc123",
    "metadata": {
      "title": "Video Title",
      "description": "Video Description"
      "publishedAt": "2023-07-01T12:00:00Z"
    },
    "transcripts": [
      {"text": "Welcome!", "start": 0.0, "duration": 1.2}
    ]
  }
]
```

### Using Webshare Proxy

```bash
ytfetcher from_channel <API_KEY> -c "channel" -f json \
  --webshare-proxy-username "<USERNAME>" \
  --webshare-proxy-password "<PASSWORD>"

```

### Using Custom Proxy

```bash
ytfetcher from_channel <API_KEY> -c "channel" -f json \
  --http-proxy "http://user:pass@host:port" \
  --https-proxy "https://user:pass@host:port"

```

### Fetching by Video IDs

```bash
ytfetcher from_video_ids <API_KEY> -v video_id1 video_id2 ... -f json
```

---

## Contributing

To insall this project locally:

```bash
git clone https://github.com/kaya70875/ytfetcher.git
cd ytfetcher
poetry install
```

## Running Tests

```bash
poetry run pytest
```

## Related Projects

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.
