from ytfetcher._youtube_dl import get_fetcher
from ytfetcher.models.channel import ChannelData, DLSnippet
from ytfetcher._transcript_fetcher import TranscriptFetcher
from ytfetcher._youtube_dl import CommentFetcher
from ytfetcher.config.http_config import HTTPConfig
from ytfetcher.config.fetch_config import FetchOptions
from youtube_transcript_api.proxies import ProxyConfig
from typing import Iterable, Callable, Literal

class YTFetcher:
    """
    YTFetcher is a high-level interface for fetching YouTube video metadata and transcripts.

    It supports three modes of initialization:
    - From a channel handle (via `from_channel`)
    - From a playlist ID (via `from_playlist_id`)
    - From a list of specific video IDs (via `from_video_ids`)
    - From a search query (via `from_search`)

    Internally, it uses the yt-dlp to retrieve video snippets and metadata,
    and the `youtube_transcript_api` (with optional proxy support) to fetch transcripts.

    Args:
        max_results (int): Maximum number of videos to fetch.
        video_ids (list[str]): List of specific video IDs to fetch.
        playlist_id (str | None) Playlist id to fetch from.
        channel_handle (str | None): Optional YouTube channel handle (used when fetching from channel).
        query (str | None): Optional search query to find videos across Youtube.
        http_config (HTTPConfig): Configuration for HTTP client behavior.
        proxy_config (ProxyConfig | None): Optional proxy settings for transcript fetching.
        languages (Iterable[str]): Preferred languages to fetch first, default to `en`
        manually_created (bool): Flag for fetching only manually created transcripts. Default to False
    """
    def __init__(
        self,
        max_results: int,
        video_ids: list[str] | None,
        playlist_id: str | None = None,
        channel_handle: str | None = None,
        query: str | None = None,
        options: FetchOptions | None = None
        ):

        self.options = options
        self.youtube_dl = get_fetcher(channel_handle, playlist_id, video_ids, query, max_results)
        self.snippets = self.youtube_dl.fetch()

        if self.filters:
            self.snippets = self._filter_snippets()

        self.fetcher = TranscriptFetcher(self._get_video_ids(), http_config=self.http_config, proxy_config=self.proxy_config, languages=languages, manually_created=manually_created)
            
    @classmethod
    def from_channel(
        cls,
        channel_handle: str,
        max_results: int = 50,
        options: FetchOptions | None = None
        ) -> "YTFetcher":
        """
        Create a fetcher that pulls up to max_results from the channel.
        """
        return cls(
            max_results=max_results,
            video_ids=None,
            channel_handle=channel_handle,
            options=options
            )
    
    @classmethod
    def from_video_ids(
        cls,
        video_ids: list[str] = [],
        options: FetchOptions | None = None
        ) -> "YTFetcher":
        """
        Create a fetcher that only fetches from given video ids.
        """
        return cls(
            max_results=len(video_ids),
            video_ids=video_ids,
            channel_handle=None,
            options=options
            )
    
    @classmethod
    def from_playlist_id(
        cls,playlist_id: str,
        max_results: int = 50,
        options: FetchOptions | None = None
        ) -> "YTFetcher":
        """
        Create a fetcher that fetches from given playlist id.
        """
        return cls(
            playlist_id=playlist_id,
            max_results=max_results,
            video_ids=None,
            options=options
            )
    
    @classmethod
    def from_search(
        cls,
        query: str,
        max_results: int = 50,
        options: FetchOptions | None = None
    ) -> "YTFetcher":
        """
        Create a fetcher that fetches from search query.
        """
        return cls(
            query=query,
            max_results=max_results,
            video_ids=None,
            options=options
        )

    def fetch_youtube_data(self) -> list[ChannelData]:
        """
        Synchronously fetches transcript and metadata for all videos retrieved from the channel or video IDs.

        Returns:
            list[ChannelData]: A list of objects containing transcript text and associated metadata.
        """

        transcripts = self.fetcher.fetch()
        
        for transcript, snippet in zip(transcripts, self.snippets):
            transcript.metadata = snippet if transcript.transcripts else None
        
        return transcripts
    
    def fetch_with_comments(self, max_comments: int = 20, sort: Literal['top', 'new'] = ('top')) -> list[ChannelData]:
        """
        Fetches comments, addition to transcripts and metadata.

        Args:
            max_comments: Max number of comments to fetch.

        Returns:
            list[ChannelData]: A list objects containing transcript text, metadata and comments.
        """

        transcripts = self.fetcher.fetch()
        
        commf = CommentFetcher(max_comments=max_comments, video_ids=self._get_video_ids(), sort=sort)
        full_comments = commf.fetch()

        for transcript, snippet, comments in zip(transcripts, self.snippets, full_comments):
            transcript.metadata = snippet if transcript.transcripts else None
            transcript.comments = comments
        
        return transcripts
    
    def fetch_comments(self, max_comments: int = 20, sort: Literal['top', 'new'] = ('top')) -> list[ChannelData]:
        """
        Fetches comments for all videos.

        Args:
            max_comments: Max number of comments to fetch.
            max_workers: Max number of workers for threads.

        Returns:
            list[ChannelData]: A list of objects containing only comments.
        """
        commf = CommentFetcher(max_comments=max_comments, video_ids=self._get_video_ids(), sort=sort)
        full_comments = commf.fetch()

        return [
            ChannelData(
                video_id=snippet.video_id,
                transcripts=None,
                metadata=snippet,
                comments=comments
            )
            for snippet, comments in zip(self.snippets, full_comments)
        ]
    
    def fetch_transcripts(self) -> list[ChannelData]:
        """
        Returns only the transcripts from cached or freshly fetched YouTube data.

        Returns:
            list[ChannelData]: Transcripts only with video_id (excluding metadata).
        """
        
        return self.fetcher.fetch()

    def fetch_snippets(self) -> list[ChannelData] | None:
        """
        Returns the raw snippet data (metadata and video IDs) retrieved from the YouTube Data API.

        Returns:
            list[ChannelData] | None: An object containing video metadata and IDs.
        """

        return [
            ChannelData(
                video_id=snippet.video_id,
                transcripts=None,
                metadata=snippet
            )
            for snippet in self.snippets
        ]

    @property
    def video_ids(self) -> list[str]:
        """
        List of video IDs fetched from the YouTube channel or provided directly.

        Returns:
            list[str]: Video ID strings.
        """
        
        return self._get_video_ids()

    @property
    def metadata(self) -> list[DLSnippet] | None:
        """
        Metadata for each video, such as title, duration, and description.

        Returns:
            list[DLSnippet] | None: List of Snippet objects containing video metadata.
        """
        return [snippet for snippet in self.snippets]

    def _get_video_ids(self) -> list[str]:
        """
        Returns list of channel video ids.
        """
        return [snippet.video_id for snippet in self.snippets]
    
    def _filter_snippets(self) -> list[DLSnippet]:
        """
        Returns filtered DLSnippet object based on defined callable filters.
        """
        return [
            snippet for snippet in self.snippets
            if all(filter(snippet) for filter in self.filters)
        ]