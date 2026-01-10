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

## Fetching Comments
`ytfetcher` allows you fetch comments in bulk **with additional metadata and transcripts** or **just comments alone.**

!!! Note
    **Performance:** Comment fetching is a resource-intensive process. The speed of extraction depends significantly on the user's internet connection and the total volume of comments being retrieved.

### Fetch Comments With Transcripts And Metadata
To fetch comments alongside with transcripts and metadata you can use `fetch_with_comments` method.

```py
fetcher = YTFetcher.from_channel("TheOffice", max_results=5)

async def get_channel_data():
    channel_data_with_comments = await fetcher.fetch_with_comments(max_comments=10)
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

def get_comments() -> list[Comment]:
    comments = fetcher.fetch_comments(max_comments=20)
    print(comments)
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