import logging
from ytfetcher.models.channel import ChannelData, DLSnippet, VideoComments, VideoTranscript, FailedTranscript
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
from ytfetcher.cache import SQLiteCache
from ytfetcher.utils.constants import RETRYABLE_ERRORS
from typing import Literal
import time

logger = logging.getLogger(__name__)

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

        self._snippets: list[DLSnippet] | None = None
        self._cache: SQLiteCache | None = (
            SQLiteCache(cache_dir=self.options.cache_path, ttl=self.options.cache_ttl)
            if self.options.cache_enabled
            else None
        )
        self._failed_transcripts: list[FailedTranscript] = []
            
    @classmethod
    def from_channel(
        cls,
        channel_handle: str,
        max_results: int | None = 20,
        tab: Literal['videos', 'shorts', 'streams'] = 'videos',
        options: FetchOptions | None = None
        ) -> "YTFetcher":
        """
        Initialize a fetcher to retrieve transcripts from a specific YouTube channel.        

        Args:
            channel_handle (str): The handle or ID of the YouTube channel.
            max_results (int): The maximum number of videos to retrieve from the channel. 
            tab (Literal): The specific channel section to target. 
                Choose from 'videos', 'shorts', or 'streams'. Defaults to 'videos'.
            options (FetchOptions): Advanced settings for the fetcher.
        """
        return cls(
            youtube_dl_fetcher=ChannelFetcher(channel_handle=channel_handle, max_results=max_results, tab=tab),
            options=options
            )
    
    @classmethod
    def from_video_ids(
        cls,
        video_ids: list[str],
        options: FetchOptions | None = None
        ) -> "YTFetcher":
        """
        Initialize a fetcher for a specific list of YouTube video IDs.

        Args:
            video_ids (list[str]):A list of unique YouTube video identifiers (e.g., ['dQw4w9WgXcQ'])
            options (FetchOptions): Advanced settings for the fetcher.
        """
        return cls(
            youtube_dl_fetcher=VideoListFetcher(video_ids=video_ids),
            options=options
            )
    
    @classmethod
    def from_playlist_id(
        cls,playlist_id: str,
        max_results: int | None = 20,
        options: FetchOptions | None = None
        ) -> "YTFetcher":
        """
        Initialize a fetcher to retrieve transcripts from all videos in a playlist.

        Args:
            playlist_id (str): Youtube playlist id.
            max_results (int): The maximum number of videos to retrieve from the playlist. 
            options (FetchOptions): Advanced settings for the fetcher.
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
        Initialize a fetcher to retrieve transcripts based on a global YouTube search.

        Args:
            query (str): The search term used to find videos. (eg. "How to ride a horse.")
            max_results (int): max_results (int): The maximum number of videos to retrieve from the query results. Defaults to 20.
            options (FetchOptions): Advanced settings for the fetcher.
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
        transcripts = self._get_transcripts()
        
        return self._build_response(
            snippets=snippets,
            transcripts=transcripts
        )
    
    def fetch_with_comments(self, max_comments: int = 20, sort: Literal['top', 'new'] = ('top')) -> list[ChannelData]:
        """
        Retrieves a comprehensive dataset including transcripts, metadata, and comments.

        This method extends the standard fetcher by scraping user discussions for each 
        video. It is ideal for sentiment analysis or context-heavy data mining.

        Args:
            max_comments (int): The maximum number of comments to retrieve per video. 
                Higher limits may increase the number of API requests. Defaults to 20.
            sort (Literal['top', 'new']): The criteria for comment retrieval. 
                'top' fetches most-liked comments; 'new' fetches the most recent. 
                Defaults to 'top'.

        Returns:
            list[ChannelData]: A list of objects, each containing the transcript text, 
                video metadata, and the requested comments.
        """

        transcripts = self._get_transcripts()
        snippets = self._get_snippets()
        
        comment_fetcher = CommentFetcher(max_comments=max_comments, video_ids=self._get_video_ids(), sort=sort)
        full_comments: list[VideoComments] = comment_fetcher.fetch()

        return self._build_response(
            transcripts=transcripts,
            snippets=snippets,
            comments=full_comments
        )
    
    def fetch_comments(self, max_comments: int = 20, sort: Literal['top', 'new'] = ('top')) -> list[VideoComments]:
        """
        Retrieves comments for all identified videos, bypassing transcript extraction.

        This is a lightweight alternative to fetch_with_comments, useful when you 
        only need user feedback and engagement data without the video text.

        Args:
            max_comments (int): The maximum number of comments to retrieve per video. 
                Defaults to 20.
            sort (Literal['top', 'new']): Determines the order of retrieved comments. 
                Use 'top' for most relevant/liked or 'new' for latest. 
                Defaults to 'top'.

        Returns:
            list[VideoComments]: A list of objects containing the video identifiers 
                and their associated comment data.
        """
        comment_fetcher = CommentFetcher(max_comments=max_comments, video_ids=self._get_video_ids(), sort=sort)
        return comment_fetcher.fetch()

    def fetch_transcripts(self) -> list[VideoTranscript]:
        """
        Returns only the transcripts from cached or freshly fetched YouTube data.

        Returns:
            list[VideoTranscript]: A list of transcript objects.
        """
        
        return self._get_transcripts()
    
    def fetch_snippets(self) -> list[DLSnippet]:
        """
        Returns the raw snippet data (metadata and video IDs) retrieved from the YouTube Data API.

        Returns:
            list[DLSnippet]: A list of snippet objects containing video metadata and IDs.
        """

        return self._get_snippets()
    
    def get_failed_transcripts(self) -> list[FailedTranscript]:
        return self._failed_transcripts.copy()

    def _get_snippets(self) -> list[DLSnippet]:
        if self._snippets is None:
            snippets = self._youtube_dl.fetch()
            self._snippets = self._apply_filters(snippets)

        return self._snippets
    
    def _apply_filters(self, snippets: list[DLSnippet]) -> list[DLSnippet]:
        if not self.options.filters:
            return snippets
        
        filtered_snippets = [
            snippet for snippet in snippets
            if all(filter(snippet) for filter in self.options.filters)
        ]

        if not filtered_snippets:
            logger.warning('Could not find any videos for the current filters.')
            return []

        logger.info(
            f'Filters applied, total of {len(snippets) - len(filtered_snippets)} videos filtered.',
        )

        return filtered_snippets


    def _get_transcripts(self) -> list[VideoTranscript]:
        video_ids = self._get_video_ids()
        if self._cache:
            logger.debug("Attempting to retrieve transcripts from cache...")
            return self._get_or_fetch_transcripts(video_ids=video_ids)

        succeeded, failed = self._fetch_with_recovery_pass(video_ids=video_ids)
        self._failed_transcripts.extend(failed)
        return succeeded
    def _create_transcript_fetcher(self, video_ids: list[str]) -> TranscriptFetcher:
        return TranscriptFetcher(
            video_ids=video_ids,
            http_config=self.options.http_config,
            proxy_config=self.options.proxy_config,
            languages=self.options.languages,
            manually_created=self.options.manually_created,
            max_concurrent_requests=self.options.max_concurrent_requests
        )
    
    def _get_video_ids(self) -> list[str]:
        """
        Returns list of channel video ids.
        """
        return [snippet.video_id for snippet in self._get_snippets()]

    def _get_or_fetch_transcripts(self, video_ids: list[str]) -> list[VideoTranscript]:
        """
        Fetches transcripts from cache and merges with freshly fetched transcripts for missing video IDs.
        
        Args:
            video_ids: List of video IDs to fetch transcripts for.
            
        Returns:
            list[VideoTranscript]: A list of VideoTranscript objects, with cached and freshly fetched transcripts merged.
        """

        assert self._cache is not None

        cache_key = SQLiteCache.build_transcript_cache_key(
            languages= (
                list(self.options.languages)
                if self.options.languages
                else ["__auto__"] # First available language if not defined by user.
            ),
            manually_created=self.options.manually_created,
        )

        cached_successes, cached_failures = self._cache.get_cached_states(video_ids=video_ids, cache_key=cache_key)

        self._failed_transcripts.extend(cached_failures)

        known_ids = {t.video_id for t in cached_successes} | {f.video_id for f in cached_failures}
        missing_ids = [vid for vid in video_ids if vid not in known_ids]

        transcript_map = {t.video_id: t for t in cached_successes}
        
        if missing_ids:
            logger.debug(f"Cache miss for {len(missing_ids)} videos. Fetching missing transcripts...")
            new_successes, new_failures = self._fetch_with_recovery_pass(video_ids=missing_ids)
            
            # Any failures that are transient should not be marked as permanently failed in the cache, allowing for future retries.
            permanent_failures = [f for f in new_failures if f.is_permanent_exception]

            self._cache.upsert_transcripts(transcripts=new_successes, cache_key=cache_key)
            self._cache.upsert_failures(failures=permanent_failures, cache_key=cache_key)
            self._failed_transcripts.extend(new_failures)

            transcript_map.update({t.video_id: t for t in new_successes})
        
        return [transcript_map[vid] for vid in video_ids if vid in transcript_map]

    def _fetch_with_recovery_pass(self, video_ids: list[str]) -> tuple[list[VideoTranscript], list[FailedTranscript]]:
        result = self._create_transcript_fetcher(video_ids=video_ids).fetch()
        successes = result.success
        failures = result.failed

        if not self.options.with_recovery:
            return successes, failures

        retry_ids = [f.video_id for f in failures if f.reason in RETRYABLE_ERRORS]

        if retry_ids:
            logger.info(f"Retrying %d transient failures in {self.options.recovery_delay} seconds...", len(retry_ids))
            time.sleep(self.options.recovery_delay)

            retry_result = self._create_transcript_fetcher(video_ids=retry_ids).fetch()
            successes.extend(retry_result.success)
            final_failures = [f for f in failures if f.video_id not in retry_ids] + retry_result.failed
        else:
            final_failures = failures

        return successes, final_failures

    def _build_response(
            self,
            snippets: list[DLSnippet], # We need snippets to ensure the order of the response matches the order of the original video IDs.
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

            vid_transcripts = transcript_map.get(vid, [])
            vid_comments = comments_map.get(vid, [])

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
