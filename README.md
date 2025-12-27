# YTFetcher
[![codecov](https://codecov.io/gh/kaya70875/ytfetcher/branch/main/graph/badge.svg)](https://codecov.io/gh/kaya70875/ytfetcher)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/ytfetcher?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/ytfetcher)
[![PyPI version](https://img.shields.io/pypi/v/ytfetcher)](https://pypi.org/project/ytfetcher/)
[![Documentation Status](https://readthedocs.org/projects/ytfetcher/badge/?version=latest)](https://ytfetcher.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> ⚡ Build structured YouTube datasets for NLP, ML, sentiment analysis & RAG in minutes.

A python tool for fetching thousands of videos fast from a Youtube channel along with structured transcripts and additional metadata. Export data easily as CSV, TXT, or JSON.

---

## 📚 Table of Contents
- [Installation](#installation)
- [Quick CLI Usage](#quick-cli-usage)
- [Docker Quick Start](#docker-quick-start)
- [Features](#features)
- [Basic Usage (Python API)](#basic-usage-python-api)
- [Using Different Fetchers](#using-different-fetchers)
- [Retreive Different Languages](#retreive-different-languages)
- [Fetching Only Manually Created Transcripts](#fetching-only-manually-created-transcripts)
- [Exporting](#exporting)
- [Other Methods](#other-methods)
- [Proxy Configuration](#proxy-configuration)
- [Advanced HTTP Configuration (Optional)](#advanced-http-configuration-optional)
- [CLI (Advanced)](#cli-advanced)
- [Contributing](#contributing)
- [Running Tests](#running-tests)
- [Related Projects](#related-projects)
- [License](#license)
- [Contributors](#contributors)

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

## Docker Quick Start
The recommended way to run or develop YTFetcher is using Docker to ensure a clean, stable environment without needing local Python or dependency management.

```bash
docker-compose build
```

Use `docker-compose run` to execute your desired command inside the container.
```bash
docker-compose run ytfetcher poetry run ytfetcher from_channel -c TheOffice -m 20 -f json
```

---

## CLI Overview
YTFetcher comes with a simple CLI so you can fetch data directly from your terminal.

```bash
ytfetcher -h
```

```bash
usage: ytfetcher [-h] {from_channel,from_video_ids} ...

Fetch YouTube transcripts for a channel

positional arguments:
  {from_channel,from_video_ids}
    from_channel        Fetch data from channel handle with max_results.
    from_playlist_id    Fetch data from a specific playlist id.
    from_video_ids      Fetch data from your custom video ids.

options:
  -h, --help            show this help message and exit
```

---

## Features
- Fetch full **transcripts** from a YouTube channel.
- Get video **metadata: title, description, thumbnails, published date**.
- Async support for **high performance**.
- **Export** fetched data as txt, csv or json.
- **CLI** support.

---

## Basic Usage (Python API)

**Note:** When specifying the channel, you should provide the exact **channel handle** without the `@` symbol, channel URL, or display name.  
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
        video_id='video1',
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

## Using Different Fetchers

`ytfetcher` also supports different fetcher so you can fetch with `channel_handle`, custom `video_ids` or from a `playlist_id`

### Fetching from Playlist ID

Here's how you can fetch bulk transcripts from a specific `playlist_id` using `ytfetcher`.

```python
from ytfetcher import YTFetcher
import asyncio

fetcher = YTFetcher.from_playlist_id(
    playlist_id="playlistid1254"
)

# Rest is same ...
```

### Fetching With Custom Video IDs

Initialize `ytfetcher` with custom video IDs using `from_video_ids` method:

```python
from ytfetcher import YTFetcher
import asyncio

fetcher = YTFetcher.from_video_ids(
    video_ids=['video1', 'video2', 'video3']
)

# Rest is same ...
```

---

## Retreive Different Languages

You can use the `languages` param to retrieve your desired language. (Default en)

```python
fetcher = YTFetcher.from_video_ids(video_ids=video_ids, languages=["tr", "en"])
```

Also here's a quick CLI command for `languages` param.
```bash
ytfetcher from_channel -c TheOffice -m 50 -f csv --print --languages tr en
```

`ytfetcher` first tries to fetch the `Turkish` transcript. If it's not available, it falls back to `English`.

---

## Fetching Only Manually Created Transcripts

`ytfetcher` allows you to fetch **only manually created transcripts** from a channel which allows you to get more precise transcripts.

```python
fetcher = YTFetcher.from_channel(channel_handle="TEDx", manually_created=True) # Set manually_created flag to True
```

You can also easily enable this feature with `--manually-created` argument in CLI.

```bash
ytfetcher from_channel -c TEDx -f csv --manually-created
```

## Exporting

Use the `BaseExporter` class to export `ChannelData` in **csv**, **json**, or **txt**:

```python
from ytfetcher.services import JSONExporter #OR you can import other exporters: TXTExporter, CSVExporter

channel_data = asyncio.run(fetcher.fetch_youtube_data())

exporter = JSONExporter(
    channel_data=channel_data,
    allowed_metadata_list=['title'],   # You can customize this
    timing=True,                       # Include transcript start/duration
    filename='my_export',              # Base filename
    output_dir='./exports'             # Optional output directory
)

exporter.write()
```

### Exporting With CLI

You can also specify arguments when exporting which allows you to decide whether to exclude `timings` and choose desired `metadata`.
```bash
ytfetcher from_channel -c TheOffice -m 20 -f json --no-timing --metadata title description
```

This command will **exclude** `timings` from transcripts and keep only `title` and `description` as metadata.

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
from ytfetcher.config import GenericProxyConfig, WebshareProxyConfig

fetcher = YTFetcher.from_channel(
    channel_handle="TheOffice",
    max_results=3,
    proxy_config=GenericProxyConfig() | WebshareProxyConfig()
)
```

---

## Advanced HTTP Configuration (Optional)
`YTfetcher` already uses custom headers for mimic real browser behavior but if you want to change it, you can use a custom `HTTPConfig` class.

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

### Fetching From Playlist Id
```bash
ytfetcher from_playlist_id -p playlistid123 -f csv -m 25
```

### Using Webshare Proxy

```bash
ytfetcher from_channel -c <CHANNEL_HANDLE> -f json --webshare-proxy-username "<USERNAME>" --webshare-proxy-password "<PASSWORD>"
```

### Using Custom Proxy

```bash
ytfetcher from_channel -c <CHANNEL_HANDLE> -f json --http-proxy "http://user:pass@host:port" --https-proxy "https://user:pass@host:port"
```

### Using Custom HTTP Config

```bash
ytfetcher from_channel -c <CHANNEL_HANDLE> --http-timeout 4.2 --http-headers "{'key': 'value'}"
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

## Running Type Check
You should be passing all type checks to contribute `ytfetcher`.

```bash
poetry run mypy ytfetcher
```

---

## Related Projects

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

---

## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.

## Contributors

Thanks to everyone who has contributed to **ytfetcher** ❤️

[![Contributors](https://contrib.rocks/image?repo=kaya70875/ytfetcher)](https://github.com/kaya70875/ytfetcher/graphs/contributors)

---

⭐ If you find this useful, please star the repo or open an issue with feedback!

