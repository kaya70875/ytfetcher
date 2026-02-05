from ytfetcher.models.channel import ChannelData, DLSnippet, VideoComments, VideoTranscript
from ytfetcher._transcript_fetcher import TranscriptFetcher
from ytfetcher._youtube_dl import (
    ChannelFetcher,
    VideoListFetcher,
    PlaylistFetcher,
    SearchFetcher,
    CommentFetcher,
    BaseYoutubeDLFetcher
)
from ytfetcher.config.fetch_config import FetchOptions
from typing import Literal

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
        youtube_dl_fetcher (BaseYoutubeDLFetcher) Relevant yt-dlp fetcher for example `ChannelFetcher`.
        options (FetchOptions | None) Optional fetcher options for controlling data and requests.
    """
    def __init__(
        self,
        youtube_dl_fetcher: BaseYoutubeDLFetcher,
        options: FetchOptions | None = None
        ):

        self._youtube_dl: BaseYoutubeDLFetcher = youtube_dl_fetcher
        self.options = options or FetchOptions()

        self._transcript_fetcher: TranscriptFetcher | None = None
        self._snippets: list[DLSnippet] | None = None
            
    @classmethod
    def from_channel(
        cls,
        channel_handle: str,
        max_results: int | None = 20,
        options: FetchOptions | None = None
        ) -> "YTFetcher":
        """
        Create a fetcher that pulls up to max_results from the channel.
        """
        return cls(
            youtube_dl_fetcher=ChannelFetcher(channel_handle=channel_handle, max_results=max_results),
            options=options
            )
    
    @classmethod
    def from_video_ids(
        cls,
        video_ids: list[str],
        options: FetchOptions | None = None
        ) -> "YTFetcher":
        """
        Create a fetcher that only fetches from given video ids.
        """
        return cls(
            youtube_dl_fetcher=VideoListFetcher(video_ids=video_ids),
            options=options
            )
    
    @classmethod
    def from_playlist_id(
        cls,playlist_id: str,
        max_results: int = 20,
        options: FetchOptions | None = None
        ) -> "YTFetcher":
        """
        Create a fetcher that fetches from given playlist id.
        """
        return cls(
            youtube_dl_fetcher=PlaylistFetcher(playlist_id=playlist_id, max_results=max_results),
            options=options
            )
    
    @classmethod
    def from_search(
        cls,
        query: str,
        max_results: int = 20,
        options: FetchOptions | None = None
    ) -> "YTFetcher":
        """
        Create a fetcher that fetches from search query.
        """
        return cls(
            youtube_dl_fetcher=SearchFetcher(query=query, max_results=max_results),
            options=options
        )

    def fetch_youtube_data(self) -> list[ChannelData]:
        """
        Synchronously fetches transcript and metadata for all videos retrieved from the channel or video IDs.

        Returns:
            list[ChannelData]: A list of objects containing transcript text and associated metadata.
        """
        snippets = self._get_snippets()
        transcripts = self._get_transcript_fetcher().fetch()
        
        return self._build_response(
            snippets=snippets,
            transcripts=transcripts
        )
    
    def fetch_with_comments(self, max_comments: int = 20, sort: Literal['top', 'new'] = ('top')) -> list[ChannelData]:
        """
        Fetches comments, addition to transcripts and metadata.

        Args:
            max_comments: Max number of comments to fetch.

        Returns:
            list[ChannelData]: A list objects containing transcript text, metadata and comments.
        """

        transcripts = self._get_transcript_fetcher().fetch()
        snippets = self._get_snippets()
        
        comment_fetcher = CommentFetcher(max_comments=max_comments, video_ids=self._get_video_ids(), sort=sort)
        full_comments: list[VideoComments] = comment_fetcher.fetch()

        return self._build_response(
            transcripts=transcripts,
            snippets=snippets,
            comments=full_comments
        )
    
    def fetch_comments(self, max_comments: int = 20, sort: Literal['top', 'new'] = ('top')) -> list[ChannelData]:
        """
        Fetches comments for all videos.

        Args:
            max_comments: Max number of comments to fetch.
            max_workers: Max number of workers for threads.

        Returns:
            list[ChannelData]: A list of objects containing only comments.
        """
        comment_fetcher = CommentFetcher(max_comments=max_comments, video_ids=self._get_video_ids(), sort=sort)
        full_comments: list[VideoComments] = comment_fetcher.fetch()

        snippets = self._get_snippets()

        return self._build_response(
            snippets=snippets,
            comments=full_comments
        )
    
    def fetch_transcripts(self) -> list[ChannelData]:
        """
        Returns only the transcripts from cached or freshly fetched YouTube data.

        Returns:
            list[ChannelData]: Transcripts only with video_id (excluding metadata).
        """
        
        transcripts = self._get_transcript_fetcher().fetch()
        return [
            ChannelData(
                video_id=transcript.video_id,
                metadata=None,
                transcripts=transcript.transcripts
            )
            for transcript in transcripts
        ]
    
    def fetch_snippets(self) -> list[ChannelData]:
        """
        Returns the raw snippet data (metadata and video IDs) retrieved from the YouTube Data API.

        Returns:
            list[ChannelData]: An object containing video metadata and IDs.
        """

        snippets = self._get_snippets()

        return [
            ChannelData(
                video_id=snippet.video_id,
                transcripts=None,
                metadata=snippet
            )
            for snippet in snippets
        ]

    def _get_snippets(self) -> list[DLSnippet]:
        if self._snippets is None:
            snippets = self._youtube_dl.fetch()

            if self.options.filters:
                snippets = [
                    snippet for snippet in snippets
                    if all(filter(snippet) for filter in self.options.filters)
                    ]

            self._snippets = snippets
        
        return self._snippets

    def _get_transcript_fetcher(self) -> TranscriptFetcher:
        if self._transcript_fetcher is None:
            video_ids = self._get_video_ids()
            self._transcript_fetcher = TranscriptFetcher(
                video_ids,
                http_config=self.options.http_config,
                proxy_config=self.options.proxy_config,
                languages=self.options.languages,
                manually_created=self.options.manually_created,
            )
        return self._transcript_fetcher
    
    def _get_video_ids(self) -> list[str]:
        """
        Returns list of channel video ids.
        """
        return [snippet.video_id for snippet in self._get_snippets()]
    
    def _build_response(
            self,
            snippets: list[DLSnippet],
            transcripts: list[VideoTranscript] | None = None,
            comments: list[VideoComments] | None = None
    ) -> list[ChannelData]:
        """
        Safely aligns data sources using 'video_id' as the key.
        Prevents misalignment if some transcripts/comments fail to fetch.
        """

        transcript_map = {t.video_id: t.transcripts for t in transcripts} if transcripts else {}
        comments_map = {c.video_id: c.comments for c in comments} if comments else {}

        results: list[ChannelData] = []

        for snippet in snippets:
            vid = snippet.video_id

            vid_transcripts = transcript_map.get(vid)
            vid_comments = comments_map.get(vid)

            results.append(
                ChannelData(
                    video_id=vid,
                    metadata=snippet,
                    transcripts=vid_transcripts,
                    comments=vid_comments
                )
            )

        return results
    
    @property
    def video_ids(self) -> list[str]:
        """
        List of video IDs fetched from the YouTube channel or provided directly.

        Returns:
            list[str]: Video ID strings.
        """
        
        return self._get_video_ids()

    @property
    def metadata(self) -> list[DLSnippet]:
        """
        Metadata for each video, such as title, duration, and description.

        Returns:
            list[DLSnippet] | None: List of Snippet objects containing video metadata.
        """
        return [snippet for snippet in self._get_snippets()]