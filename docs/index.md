# YTFetcher

**Build structured YouTube datasets at scale.** Effortlessly fetch transcripts, metadata, and comments for NLP, ML, and AI workflows.

---

## Why YTFetcher?
Most YouTube scrapers are either slow, break easily, or only give you raw text. YTFetcher is built for **speed** and **structure**:

* 🚀 **High performance:** Fetches thousands of videos in minutes.
* 📦 **Structured Data:** Returns clean Pydantic models (metadata, transcripts, comments).
* 🛠️ **CLI & API:** Use it in your terminal or integrate it into your Python pipeline.
* 🛡️ **Built-in Proxy Support:** Avoid rate limits with Generic or Webshare proxies.
* 💾 **Export Options:** Save results as JSON, CSV, or TXT formats.
* 📊 **Rich CLI Preview:** Beautiful Rich tables for easy data inspection in terminal.

## Quick Start

### Installation
```bash
pip install ytfetcher
```

### Basic Usage (Python API)

Here’s how you can get transcripts and metadata information like **channel name, description, published date**, etc. from a channel with `from_channel` method:
```python
from ytfetcher import YTFetcher

fetcher = YTFetcher.from_channel(
    channel_handle="TheOffice",
    max_results=2
)

channel_data = fetcher.fetch_youtube_data()
print(channel_data)

```

!!! Note
    `ytfetcher` handles **full channel url** and channel handles without `@` symbol. So you can pass a full url like `https://www.youtube.com/@TheOffice` directly to terminal or to `channel_handle` parameter.

This will return a list of `ChannelData` with metadata in `DLSnippet` objects:
```py
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

### Preview Data
You can also preview this data using `PreviewRenderer` class from `ytfetcher.services`:
```py
from ytfetcher.services import PreviewRenderer

channel_data = fetcher.fetch_youtube_data(max_comments=10)
#print(channel_data)
preview = PreviewRenderer()
preview.render(data=channel_data, limit=4)
```

This will preview the first 4 results of the data in a **beautifully formatted terminal view, including metadata, transcript snippets, and comments**.

## Using Different Fetchers
`ytfetcher` supports different fetchers so you can fetch with using `channel_handle`, custom `video_ids` or from a `playlist_id` directly.

### Fetching From Playlist ID

Here's how you can fetch bulk transcripts from a specific `playlist_id` using `ytfetcher`.
```py
from ytfetcher import YTFetcher

fetcher = YTFetcher.from_playlist_id(
    playlist_id="playlistid1254"
)

data = fetcher.fetch_youtube_data()

### Fetching With Custom Video IDs
Initialize `ytfetcher` with custom video IDs using `from_video_ids` method:
```py
from ytfetcher import YTFetcher

fetcher = YTFetcher.from_video_ids(
    video_ids=['video1', 'video2', 'video3']
)

data = fetcher.fetch_youtube_data()
```

## Transcript Options

YTFetcher provides **flexible transcript fetching with support for multiple languages and fallback mechanisms.** You can customize how transcripts are retrieved to match your specific needs.

### Retrieve Different Languages
You can use the `languages` param to **retrieve your desired language.** (Default en)

```py
fetcher = YTFetcher.from_video_ids(video_ids=video_ids, languages=["tr", "en"])
```

`ytfetcher` first tries to fetch the `Turkish` transcript. If it's not available, it falls back to `English`.

### Fetching Only Manually Created Transcripts

`ytfetcher` allows you to fetch only manually created transcripts from a channel which allows you to get more precise transcripts.
```py
fetcher = YTFetcher.from_channel(channel_handle="TEDx", manually_created=True)
```

!!! Note
    As default `ytfetcher` already tries to fetch manually created transcripts first, but if you want get **only manually created ones** you can use this flag.

!!! Tip
    Also it makes sense to use this flag to fetch channels like `TEDx` which naturally has more **manually created** transcripts.

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

## Fetching Comments
`ytfetcher` allows you fetch comments in bulk **with additional metadata and transcripts** or **just comments alone.**

!!! Note
    **Performance:** Comment fetching is a resource-intensive process. The speed of extraction depends significantly on the user's internet connection and the total volume of comments being retrieved.

### Fetch Comments With Transcripts And Metadata
To fetch comments alongside with transcripts and metadata you can use `fetch_with_comments` method.

```py
fetcher = YTFetcher.from_channel("TheOffice", max_results=5)
comments = fetcher.fetch_with_comments(max_comments=10)
```

This will simply fetch **top 10 comments for every video** alongside with transcript data.

Here's an example structure:

```py
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
```py
fetcher = YTFetcher.from_channel("TheOffice", max_results=5)
comments = fetcher.fetch_comments(max_comments=20)
```

This will return list of `Comment` like this:

```py
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


## Proxy and Configuration

YTFetcher provides built-in support for proxy servers and custom HTTP configuration to help you avoid rate limits and customize request behavior when fetching YouTube data at scale.

### Proxy Configuration

When fetching large amounts of data, YouTube may rate limit your requests. Using a proxy helps distribute requests across different IP addresses, significantly reducing the risk of being blocked. YTFetcher supports two types of proxy configurations:

**Generic Proxy Configuration**

Use custom HTTP/HTTPS proxy servers with `GenericProxyConfig`:

```python
from ytfetcher import YTFetcher
from ytfetcher.config import GenericProxyConfig

proxy_config = GenericProxyConfig(
    http_url="http://user:pass@host:port",
    https_url="https://user:pass@host:port"
)

fetcher = YTFetcher.from_channel(
    channel_handle="TheOffice",
    max_results=50,
    proxy_config=proxy_config
)
```

**Webshare Proxy Configuration**

For Webshare proxy service users, use `WebshareProxyConfig`:

```python
from ytfetcher import YTFetcher
from ytfetcher.config import WebshareProxyConfig

proxy_config = WebshareProxyConfig(
    proxy_username="your_webshare_username",
    proxy_password="your_webshare_password"
)

fetcher = YTFetcher.from_channel(
    channel_handle="TheOffice",
    max_results=50,
    proxy_config=proxy_config
)
```

!!! Tip
    You can find your Webshare proxy credentials at [https://dashboard.webshare.io/proxy/settings](https://dashboard.webshare.io/proxy/settings)

### HTTP Configuration

YTFetcher automatically uses realistic browser-like headers to mimic real browser behavior. However, you can customize HTTP settings including timeout and custom headers:

```python
from ytfetcher import YTFetcher
from ytfetcher.config import HTTPConfig

http_config = HTTPConfig(
    timeout=4.0,  # Request timeout in seconds
    headers={"User-Agent": "Custom-Agent/1.0"}  # Custom headers
)

fetcher = YTFetcher.from_channel(
    channel_handle="TheOffice",
    max_results=10,
    http_config=http_config
)
```

!!! Note
    If you don't provide custom headers, YTFetcher will automatically use realistic browser headers to avoid detection.
