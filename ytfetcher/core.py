from ytfetcher.youtube_v3 import YoutubeV3
from ytfetcher.types.channel import ChannelData
from ytfetcher.transcript_fetcher import TranscriptFetcher
import httpx

timeout = httpx.Timeout(connect=2.0, read=2.0, write=2.0, pool=2.0)

class YTFetcher:
    def __init__(self, yt_client: YoutubeV3):
        self.yt_client = yt_client
        self.channel_data = self.yt_client.fetch_channel_snippets()
        self.fetcher = TranscriptFetcher(self.channel_data.video_ids, self.channel_data.metadata, timeout=timeout)

    def fetch_transcripts(self):
        pass

    async def fetch_transcripts_with_metadata(self):
        return await self.fetcher.fetch()
    
    def get_channel_data(self) -> ChannelData:
        return self.channel_data