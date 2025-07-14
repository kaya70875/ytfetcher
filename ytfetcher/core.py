from ytfetcher.youtube_v3 import YoutubeV3
from ytfetcher.types.channel import ChannelData, FetchAndMetaResponse, Transcript
from ytfetcher.transcript_fetcher import TranscriptFetcher
from ytfetcher.config.http_config import HTTPConfig

class YTFetcher:
    def __init__(self, api_key: str, http_config: HTTPConfig, max_results: int, video_ids: list[str]):
        self.v3 = YoutubeV3(api_key=api_key, channel_name=None, video_ids=video_ids, max_results=max_results)
        self.snippets = self.v3.fetch_channel_snippets()
        self.fetcher = TranscriptFetcher(self.snippets.video_ids, self.snippets.metadata, http_config=http_config)
    
    @classmethod
    def from_channel(cls, api_key: str, channel_handle: str, max_results: int = 50, http_config: HTTPConfig = HTTPConfig()) -> "YTFetcher":
        """
        Create a fetcher that pulls up to max_results from the channel.
        """

        inst = cls.__new__(cls)
        inst.v3 = YoutubeV3(api_key=api_key, channel_name=channel_handle, max_results=max_results, video_ids=[])
        inst.snippets = inst.v3.fetch_channel_snippets()
        inst.fetcher = TranscriptFetcher(inst.snippets.video_ids, inst.snippets.metadata, http_config=http_config)
        return inst
    
    @classmethod
    def from_video_ids(cls, api_key: str, video_ids: list[str] = [], http_config: HTTPConfig = HTTPConfig()) -> "YTFetcher":
        """
        Create a fetcher that only fetches from given video ids.
        """

        inst = cls.__new__(cls)
        inst.v3 = YoutubeV3(api_key=api_key, channel_name=None, max_results=len(video_ids), video_ids=video_ids)
        inst.snippets = inst.v3.fetch_channel_snippets()
        inst.fetcher = TranscriptFetcher(inst.snippets.video_ids, inst.snippets.metadata, http_config=http_config)
        return inst

    async def get_transcripts(self) -> Transcript:
        return [x.transcript for x in await self.fetcher.fetch()]

    async def get_transcripts_with_metadata(self) -> list[FetchAndMetaResponse]:
        return await self.fetcher.fetch()
    
    def get_channel_data(self) -> ChannelData:
        return self.snippets
    
    def get_video_ids(self) -> list[str]:
        return self.snippets.video_ids