# YTFetcher

**YTFetcher** is a Python tool for fetching YouTube video transcripts in bulk, along with rich metadata like titles, publish dates, and thumbnails. Ideal for building NLP datasets, search indexes, or powering content analysis apps.

---

## 🚀 Features

- Fetch full transcripts from a YouTube channel.
- Get video metadata: title, description, thumbnails, published date
- Async support for high performance

---

## 📦 Installation

```bash
git clone https://github.com/kaya70875/ytfetcher.git
cd ytfetcher
pip install -e .
```

## Basic Usage

Ytfetcher uses YoutubeV3 API to get channel details so you have to create your YoutubeV3 api key from Google Cloud Console [In here](https://console.cloud.google.com/apis/api/youtube.googleapis.com).
Also keep in mind that you have a quota limit for YoutubeV3 API for getting metadata from a channel, but for basic usage quota isn't generally a concern.

Here how you can get transcripts and metadata informations like channel name, description, publishedDate etc. from a single channel with from_channel function:

---

```python
from ytfetcher.core import YTFetcher
import asyncio

fetcher = YTFetcher.from_channel(api_key='your-youtubev3-api-key', channel_handle="TheOffice", max_results=50)

async def main():
    metadata = await fetcher.get_youtube_data()
    print(metadata)

asyncio.run(main())
```
