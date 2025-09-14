from ytfetcher._youtube_v3 import YoutubeV3
from ytfetcher._youtube_dl import YoutubeDL
from ytfetcher.models.channel import ChannelData, Snippet
from ytfetcher._transcript_fetcher import TranscriptFetcher
from ytfetcher.config.http_config import HTTPConfig
from youtube_transcript_api.proxies import ProxyConfig

class YTFetcher:
    """
    YTFetcher is a high-level interface for fetching YouTube video metadata and transcripts.

    It supports two modes of initialization:
    - From a channel handle (via `from_channel`)
    - From a list of specific video IDs (via `from_video_ids`)

    Internally, it uses the YouTube Data API v3 to retrieve video snippets and metadata,
    and the `youtube_transcript_api` (with optional proxy support) to fetch transcripts.

    Parameters:
        api_key (str | None): API key for accessing the YouTube Data API. YT-DLP will be used if not provided.
        http_config (HTTPConfig): Configuration for HTTP client behavior.
        max_results (int): Maximum number of videos to fetch.
        video_ids (list[str]): List of specific video IDs to fetch.
        channel_handle (str | None): Optional YouTube channel handle (used when fetching from channel).
        proxy_config (ProxyConfig | None): Optional proxy settings for transcript fetching.

    Example:
        fetcher = YTFetcher.from_channel(api_key="YOUR_KEY", channel_handle="@example")
        data = await fetcher.fetch_youtube_data()
    """
    def __init__(self, max_results: int, video_ids: list[str], api_key: str | None = None, channel_handle: str | None = None, proxy_config: ProxyConfig | None = None, http_config: HTTPConfig = HTTPConfig()):
        self.http_config = http_config
        self.proxy_config = proxy_config
        self.youtube_dl = None

        self.v3 = None
        self.snippets = []

        if api_key:
            self.v3 = YoutubeV3(api_key=api_key, channel_name=channel_handle, video_ids=video_ids, max_results=max_results, http_config=self.http_config)
            self.snippets = self.v3.fetch_channel_snippets()
        else:
            print('API key is not provided, using yt-dlp instead.')
            self.youtube_dl = YoutubeDL(channel_handle, max_results=max_results)

        self.fetcher = TranscriptFetcher(self._get_video_ids() if api_key else self.youtube_dl.video_ids, http_config=self.http_config, proxy_config=self.proxy_config)
        
    
    @classmethod
    def from_channel(cls, channel_handle: str, api_key: str | None = None, max_results: int = 50, http_config: HTTPConfig = HTTPConfig(), proxy_config: ProxyConfig | None = None) -> "YTFetcher":
        """
        Create a fetcher that pulls up to max_results from the channel.
        """
        return cls(api_key=api_key, http_config=http_config, max_results=max_results, video_ids=[], channel_handle=channel_handle, proxy_config=proxy_config)
    
    @classmethod
    def from_video_ids(cls, api_key: str | None = None, video_ids: list[str] = [], http_config: HTTPConfig = HTTPConfig(), proxy_config: ProxyConfig | None = None) -> "YTFetcher":
        """
        Create a fetcher that only fetches from given video ids.
        """
        return cls(api_key=api_key, http_config=http_config, max_results=len(video_ids), video_ids=video_ids, channel_handle=None, proxy_config=proxy_config)

    async def fetch_youtube_data(self) -> list[ChannelData]:
        """
        Asynchronously fetches transcript and metadata for all videos retrieved from the channel or video IDs.

        Returns:
            list[ChannelData]: A list of objects containing transcript text and associated metadata.
        """

        transcripts = await self.fetcher.fetch()

        if self.youtube_dl:
            return transcripts
        
        for transcript, snippet in zip(transcripts, self.snippets):
            transcript.metadata = snippet.metadata
        
        return transcripts
    
    async def fetch_transcripts(self) -> list[ChannelData]:
        """
        Returns only the transcripts from cached or freshly fetched YouTube data.

        Returns:
            list[ChannelData]: Transcripts only with video_id (excluding metadata).
        """
        
        return await self.fetcher.fetch()

    async def fetch_snippets(self) -> list[ChannelData] | None:
        """
        Returns the raw snippet data (metadata and video IDs) retrieved from the YouTube Data API.

        Returns:
            list[ChannelData] | None: An object containing video metadata and IDs.
        """

        return self.snippets

    @property
    def video_ids(self) -> list[str]:
        """
        List of video IDs fetched from the YouTube channel or provided directly.

        Returns:
            list[str]: Video ID strings.
        """
        if self.youtube_dl:
            return self.youtube_dl.video_ids
        
        return self.snippets.video_ids

    @property
    def metadata(self) -> list[Snippet] | None:
        """
        Metadata for each video, such as title, publish date, and description.

        Returns:
            list[Snippet] | None: List of Snippet objects containing video metadata.
        """
        return [snippet.metadata for snippet in self.snippets]
    
    def _get_video_ids(self) -> list[str]:
        """
        Returns list of channel video ids.
        Only works with YoutubeV3 API.
        """
        return [snippet.video_id for snippet in self.snippets]