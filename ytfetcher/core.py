from ytfetcher.youtube_v3 import YoutubeV3
from ytfetcher.types.channel import ChannelData, FetchAndMetaResponse, Transcript
from ytfetcher.transcript_fetcher import TranscriptFetcher
from ytfetcher.config.http_config import HTTPConfig

class YTFetcher:
    def __init__(self, api_key: str, http_config: HTTPConfig, max_results: int, video_ids: list[str], channel_handle: str | None = None):
        self.v3 = YoutubeV3(api_key=api_key, channel_name=channel_handle, video_ids=video_ids, max_results=max_results)
        self.snippets = self.v3.fetch_channel_snippets()
        self.http_config = http_config
        self._fetcher: TranscriptFetcher | None = None

    def _get_fetcher(self) -> TranscriptFetcher:
        if self._fetcher is None:
            print('Fetcher initialized.')
            self._fetcher = TranscriptFetcher(self.snippets.video_ids, self.snippets.metadata, http_config=self.http_config)
        return self._fetcher
    
    @classmethod
    def from_channel(cls, api_key: str, channel_handle: str, max_results: int = 50, http_config: HTTPConfig = HTTPConfig()) -> "YTFetcher":
        """
        Create a fetcher that pulls up to max_results from the channel.
        """
        return cls(api_key=api_key, http_config=http_config, max_results=max_results, video_ids=[], channel_handle=channel_handle)
    
    @classmethod
    def from_video_ids(cls, api_key: str, video_ids: list[str] = [], http_config: HTTPConfig = HTTPConfig()) -> "YTFetcher":
        """
        Create a fetcher that only fetches from given video ids.
        """
        return cls(api_key=api_key, http_config=http_config, max_results=len(video_ids), video_ids=video_ids, channel_name=None)

    async def get_transcripts(self) -> Transcript:
        return [x.transcript for x in await self._get_fetcher().fetch()]

    async def get_transcripts_with_metadata(self) -> list[FetchAndMetaResponse]:
        return await self._get_fetcher().fetch()
    
    def get_channel_data(self) -> ChannelData:
        return self.snippets
    
    def get_video_ids(self) -> list[str]:
        return self.snippets.video_ids