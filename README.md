# YTFetcher

[![codecov](https://codecov.io/gh/kaya70875/ytfetcher/branch/main/graph/badge.svg)](https://codecov.io/gh/kaya70875/ytfetcher)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/ytfetcher?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/ytfetcher)
[![PyPI version](https://img.shields.io/pypi/v/ytfetcher)](https://pypi.org/project/ytfetcher/)
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
- [Filtering](#filtering)
- [Fetching Only Manually Created Transcripts](#fetching-only-manually-created-transcripts)
- [Exporting](#exporting)
- [Comments](#Fetching-Comments)
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
ytfetcher channel -c TheOffice -m 50 -f json
```

---

## Docker Quick Start

The recommended way to run or develop YTFetcher is using Docker to ensure a clean, stable environment without needing local Python or dependency management.

```bash
docker-compose build
```

Use `docker-compose run` to execute your desired command inside the container.

```bash
docker-compose run ytfetcher poetry run ytfetcher channel -c TheOffice -m 20 -f json
```

---

## CLI Overview

YTFetcher comes with a simple CLI so you can fetch data directly from your terminal.

```bash
ytfetcher -h
```

```bash
usage: ytfetcher [-h] {channel,playlist,video,search} ...

Fetch YouTube transcripts for a channel

positional arguments:
  {channel,playlist,video,search}
    channel        Fetch data from channel handle with max_results.
    playlist    Fetch data from a specific playlist id.
    video      Fetch data from your custom video ids.
    search     Fetch data from youtube with search query. 

options:
  -h, --help            show this help message and exit
```

---

## Features

- Fetch full **transcripts** from a YouTube channel.
- Get video **metadata: title, description, thumbnails, published date**.
- Support for fetching with **channel handle, playlist id, custom video id's or with a search query.**
- Fetch **comments** in bulk.
- Concurrent fetching for **high performance**.
- **Export** fetched data as txt, csv or json.
- **CLI** support.

---

## Basic Usage (Python API)

Here’s how you can get transcripts and metadata information like channel name, description, published date, etc. from a single channel with `from_channel` method:

```python
from ytfetcher import YTFetcher

fetcher = YTFetcher.from_channel(
    channel_handle="TheOffice",
    max_results=2
)

channel_data = fetcher.fetch_youtube_data()
print(channel_data)

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

You can also **preview** this data using `PreviewRenderer` class from `ytfetcher.services`.

```python
from ytfetcher.services import PreviewRenderer

channel_data = fetcher.fetch_with_comments(max_comments=10)
#print(channel_data)
preview = PreviewRenderer()
preview.render(data=channel_data, limit=4)
```

This will preview the first 4 results of the data in a beautifully formatted terminal view, including metadata, transcript snippets, and comments.

---

## Using Different Fetchers

`ytfetcher` supports various fetching options that includes:

- Fetching from a playlist id with `from_playlist_id` method.
- Fetching from video id's with `from_video_ids` method.
- Fetching from a search query with `from_search` method.

### Fetching from Playlist ID

Use `from_playlist_id` to retrieve metadata and transcripts for every video within a public or unlisted YouTube playlist.

```python
from ytfetcher import YTFetcher

fetcher = YTFetcher.from_playlist_id(
    playlist_id="playlistid1254"
)

# Rest is same ...
```

### Fetching With Custom Video IDs

If you already have specific video identifiers, `from_video_ids` allows you to target them directly.
This is the most efficient way to fetch data when you have an external list of URLs or IDs.

```python
from ytfetcher import YTFetcher

fetcher = YTFetcher.from_video_ids(
    video_ids=['video1', 'video2', 'video3']
)

# Rest is same ...
```

### Fetching With Search Query

The `from_search` method allows you to discover videos based on a keyword or phrase, similar to using the YouTube search bar. You can control the breadth of the search using the `max_results` parameter.

```py
from ytfetcher import YTFetcher

# Searches for the top 10 videos matching 'Artificial Intelligence'
fetcher = YTFetcher.from_search(
    query="Artificial Intelligence",
    max_results=10
)
```

---

## Retreive Different Languages

You can use the `languages` param to retrieve your desired language. (Default en)

```python
fetcher = YTFetcher.from_video_ids(video_ids=video_ids, languages=["tr", "en"])
```

Also here's a quick CLI command for `languages` param.

```bash
ytfetcher channel TheOffice -m 50 -f csv --languages tr en
```

`ytfetcher` first tries to fetch the `Turkish` transcript. If it's not available, it falls back to `English`.

---

## Filtering

`ytfetcher` allows you to filter videos **before** fetching transcripts, which helps you focus on specific content and save processing time. Filters are applied to video metadata (duration, view count, title) and work with all fetcher methods.

### Available Filter Functions

The following filter functions are available in `ytfetcher.filters`:

- **`min_duration(sec: float)`** - Filter videos with duration greater than or equal to specified seconds
- **`max_duration(sec: float)`** - Filter videos with duration less than or equal to specified seconds
- **`min_views(n: int)`** - Filter videos with view count greater than or equal to specified number
- **`max_views(n: int)`** - Filter videos with view count less than or equal to specified number
- **`filter_by_title(search_query: str)`** - Filter videos whose title contains the search query (case-insensitive)

### Using Filters in Python API

Pass a list of filter functions to the `filters` parameter when creating a fetcher:

```python
from ytfetcher import YTFetcher
from ytfetcher.filters import min_duration, min_views, filter_by_title

fetcher = YTFetcher.from_channel(
    channel_handle="TheOffice",
    max_results=50,
    filters=[
        min_views(5000),
        min_duration(600),  # At least 10 minutes
        filter_by_title("tutorial")
    ]
)
```

Filters also work with `from_video_ids` and `from_playlist_id`:

```python
fetcher = YTFetcher.from_playlist_id(
    playlist_id="playlistid1254",
    filters=[min_views(1000), max_duration(1800)]  # Max 30 minutes
)

fetcher = YTFetcher.from_video_ids(
    video_ids=['video1', 'video2', 'video3'],
    filters=[filter_by_title("python")]
)
```

### Using Filters in CLI

You can use filter arguments directly in the CLI:

```bash
# Filter by minimum views
ytfetcher channel TheOffice -m 50 -f json --min-views 1000

# Filter by minimum duration (in seconds)
ytfetcher channel TheOffice -m 50 -f csv --min-duration 300

# Filter by title substring
ytfetcher channel TheOffice -m 50 -f json --includes-title "episode"

# Combine multiple filters
ytfetcher channel TheOffice -m 50 -f json --min-views 1000 --min-duration 300 --includes-title "tutorial"
```

---

## Fetching Only Manually Created Transcripts

`ytfetcher` allows you to fetch **only manually created transcripts** from a channel which allows you to get more precise transcripts.

```python
fetcher = YTFetcher.from_channel(channel_handle="TEDx", manually_created=True) # Set manually_created flag to True
```

You can also easily enable this feature with `--manually-created` argument in CLI.

```bash
ytfetcher channel TEDx -f csv --manually-created
```

## Exporting

Use the `BaseExporter` class to export `ChannelData` in **csv**, **json**, or **txt**:

```python
from ytfetcher.services import JSONExporter # OR you can import other exporters: TXTExporter, CSVExporter

channel_data = fetcher.fetch_youtube_data()

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
ytfetcher channel TheOffice -m 20 -f json --no-timing --metadata title description
```

This command will **exclude** `timings` from transcripts and keep only `title` and `description` as metadata.

---

## Fetching Comments

`ytfetcher` allows you fetch comments in bulk with additional metadata and transcripts or just comments alone.

Performance: Comment fetching is a resource-intensive process. The speed of extraction depends significantly on the user's internet connection and the total volume of comments being retrieved.

### Fetch Comments With Transcripts And Metadata

To fetch comments alongside with transcripts and metadata you can use `fetch_with_comments` method.

```python
fetcher = YTFetcher.from_channel("TheOffice", max_results=5)

channel_data_with_comments = fetcher.fetch_with_comments(max_comments=10)
```

This will simply fetch **top 10 comments** for every video alongside with transcript data.

Here's an example structure:

```python
[
    ChannelData(
        video_id='id1',
        transcripts=list[Transcript(...)],
        metadata=DLSnippet(...),
        comments=list[Comment(
            text='Comment one.',
            like_count=20,
            author='@author',
            time_text='8 days ago'
        )]
    )
]
```

### Fetch Only Comments

To fetch comments without transcripts you can use `fetch_comments` method.

```python
fetcher = YTFetcher.from_channel("TheOffice", max_results=5)

comments = fetcher.fetch_comments(max_comments=20)
```

This will return list of `Comment` like this:

```python
[
    Comment(
        text='Comment one.',
        like_count=20,
        author='@author',
        time_text='8 days ago'
    )

    ## OTHER COMMENT OBJECTS...
]
```

### Fetching Comments With CLI

Fetching comments in `ytfetcher` with CLI is very easy.

To fetch comments with transcripts you can use `--comments` argument:

```bash
ytfetcher channel TheOffice -m 20 --comments 10 -f json
```

To fetch only comments with metadata you can use `--comments-only` argument:

```bash
ytfetcher channel TheOffice -m 20 --comments-only 10 -f json
```

## Other Methods

You can also fetch only transcript data or metadata with video IDs using `fetch_transcripts` and `fetch_snippets`.

### Fetch Transcripts

```python
fetcher = YTFetcher.from_channel(channel_handle="TheOffice", max_results=2)
data = fetcher.fetch_transcripts()

print(data)
```

### Fetch Snippets

```python
data = fetcher.fetch_snippets()
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
ytfetcher <CHANNEL_HANDLE> -m <MAX_RESULTS> -f <FORMAT>
```

### Fetching by Video IDs

```bash
ytfetcher video video_id1 video_id2 ... -f json
```

### Fetching From Playlist Id

```bash
ytfetcher playlist playlistid123 -f csv -m 25
```

### Fetching with Search Method
```bash
ytfetcher search "AI Getting Jobs" -f json -m 25
```

### Using Webshare Proxy

```bash
ytfetcher <CHANNEL_HANDLE> -f json --webshare-proxy-username "<USERNAME>" --webshare-proxy-password "<PASSWORD>"
```

### Using Custom Proxy

```bash
ytfetcher <CHANNEL_HANDLE> -f json --http-proxy "http://user:pass@host:port" --https-proxy "https://user:pass@host:port"
```

### Using Custom HTTP Config

```bash
ytfetcher <CHANNEL_HANDLE> --http-timeout 4.2 --http-headers "{'key': 'value'}"
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
