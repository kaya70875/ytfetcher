# YTFetcher

**Build structured YouTube datasets at scale.** Effortlessly fetch transcripts, metadata, and comments for NLP, ML, and AI workflows.

---

## Why YTFetcher?
Most YouTube scrapers are either slow, break easily, or only give you raw text. YTFetcher is built for **speed** and **structure**:

* 🚀 **Async-first:** Fetches thousands of videos in minutes.
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

channel_data = await fetcher.fetch_youtube_data(max_comments=10)
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
import asyncio

fetcher = YTFetcher.from_playlist_id(
    playlist_id="playlistid1254"
)

async def get_channel_data() -> list[ChannelData]:
    channel_data = await fetcher.fetch_youtube_data()
    return channel_data
```

### Fetching With Custom Video IDs
Initialize `ytfetcher` with custom video IDs using `from_video_ids` method:
```py
from ytfetcher import YTFetcher
import asyncio

fetcher = YTFetcher.from_video_ids(
    video_ids=['video1', 'video2', 'video3']
)

async def get_channel_data() -> list[ChannelData]:
    channel_data = await fetcher.fetch_youtube_data()
    return channel_data
```