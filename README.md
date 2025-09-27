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

## Quick CLI Usage
Fetch 50 video transcripts + metadata from a channel and save as JSON:
```bash
ytfetcher from_channel -c TheOffice -m 50 -f json
```

---

## Features
- Fetch full transcripts from a YouTube channel.
- Get video metadata: title, description, thumbnails, published date.
- Async support for high performance.
- Export fetched data as txt, csv or json.
- CLI support.

---

## Basic Usage (Python API)

**Note:** When specifying the channel, you must provide the exact **channel handle** without the `@` symbol, channel URL, or display name.  
For example, use `TheOffice` instead of `@TheOffice` or `https://www.youtube.com/c/TheOffice`.

Here’s how you can get transcripts and metadata information like channel name, description, published date, etc. from a single channel with `from_channel` method:

```python
from ytfetcher import YTFetcher
from ytfetcher.models.channel import ChannelData
import asyncio

fetcher = YTFetcher.from_channel(
    channel_handle="TheOffice",
    max_results=2
)

async def get_channel_data() -> list[ChannelData]:
    channel_data = await fetcher.fetch_youtube_data()
    return channel_data

if __name__ == '__main__':
    data = asyncio.run(get_channel_data())
    print(data)
```

---

This will return a list of `ChannelData` with metadata in `DLSnippet` objects:

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
    metadata=DLSnippet(
        title='VideoTitle',
        description='VideoDescription',
        url='https://youtu.be/video1',
        duration=120,
        view_count=1000,
        thumbnails=[{'url': 'thumbnail_url'}]
    )
),
# Other ChannelData objects...
]
```

---

## Fetching With Custom Video IDs

You can also initialize `ytfetcher` with custom video IDs using `from_video_ids` method:

```python
from ytfetcher import YTFetcher
import asyncio

fetcher = YTFetcher.from_video_ids(
    video_ids=['video1', 'video2', 'video3']
)

# Rest is same ...
```

---

## Exporting

Use the `Exporter` class to export `ChannelData` in **csv**, **json**, or **txt**:

```python
from ytfetcher.services import Exporter

channel_data = asyncio.run(fetcher.fetch_youtube_data())

exporter = Exporter(
    channel_data=channel_data,
    allowed_metadata_list=['title'],   # You can customize this
    timing=True,                       # Include transcript start/duration
    filename='my_export',              # Base filename
    output_dir='./exports'             # Optional output directory
)

exporter.export_as_json()  # or .export_as_txt(), .export_as_csv()
```

---

## Other Methods

You can also fetch only transcript data or metadata with video IDs using `fetch_transcripts` and `fetch_snippets`.

### Fetch Transcripts

```python
fetcher = YTFetcher.from_channel(channel_handle="TheOffice", max_results=2)

async def get_transcript_data():
    return await fetcher.fetch_transcripts()

data = asyncio.run(get_transcript_data())
print(data)
```

### Fetch Snippets

```python
async def get_snippets():
    return await fetcher.fetch_snippets()

data = asyncio.run(get_snippets())
print(data)
```

---

## Proxy Configuration

`YTFetcher` supports proxy usage for fetching YouTube transcripts:

```python
from ytfetcher import YTFetcher
from ytfetcher.config import GenericProxyConfig

fetcher = YTFetcher.from_channel(
    channel_handle="TheOffice",
    max_results=3,
    proxy_config=GenericProxyConfig()
)
```

---

## Advanced HTTP Configuration (Optional)

```python
from ytfetcher import YTFetcher
from ytfetcher.config import HTTPConfig

custom_config = HTTPConfig(
    timeout=4.0,
    headers={"User-Agent": "ytfetcher/1.0"}
)

fetcher = YTFetcher.from_channel(
    channel_handle="TheOffice",
    max_results=10,
    http_config=custom_config
)
```

---

## CLI (Advanced)

### Basic Usage
```bash
ytfetcher from_channel -c <CHANNEL_HANDLE> -m <MAX_RESULTS> -f <FORMAT>
```

### Fetching by Video IDs
```bash
ytfetcher from_video_ids -v video_id1 video_id2 ... -f json
```

---

## Contributing

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

