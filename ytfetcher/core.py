from ytfetcher.youtube_v3 import YoutubeV3
from ytfetcher.types.channel import ChannelData, FetchAndMetaResponse, Transcript
from ytfetcher.transcript_fetcher import TranscriptFetcher
import httpx

class YTFetcher:
    def __init__(self, api_key: str, channel_handle:str, max_results: int, timeout: httpx.Timeout):
        self.v3 = YoutubeV3(api_key, channel_handle, max_results)
        self.snippets = self.v3.fetch_channel_snippets()
        self.fetcher = TranscriptFetcher(self.snippets.video_ids, self.snippets.metadata, timeout=timeout)

    async def get_transcripts(self) -> Transcript:
        data = await self.fetcher.fetch()
        transcripts = [x.transcript for x in data]

        return transcripts

    async def get_transcripts_with_metadata(self) -> list[FetchAndMetaResponse]:
        return await self.fetcher.fetch()
    
    def get_channel_data(self) -> ChannelData:
        return self.snippets
    
    def get_video_ids(self) -> list[str]:
        return self.snippets.video_ids