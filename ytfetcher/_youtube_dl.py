import yt_dlp
import concurrent.futures
import logging
from ytfetcher.models.channel import DLSnippet, Comment, VideoComments
from ytfetcher.utils.state import should_disable_progress
from tqdm import tqdm
from abc import ABC, abstractmethod
from urllib.parse import urlparse, parse_qs
from typing import Any, cast, Literal

logger = logging.getLogger(__name__)

class BaseYoutubeDLFetcher(ABC):
    """
    Abstract base class for YouTube data fetching using yt_dlp.
    """

    def __init__(self, max_results: int | None = 20):
        """
        Initialize the base fetcher.

        Args:
            max_results (int | None): The maximum number of results to fetch. 
                Set to None to fetch all available entries. Defaults to 20.
        """
        self.max_results = max_results

    @abstractmethod
    def fetch(self) -> list[DLSnippet]:
        """Abstract method to be implemented by subclasses."""
        pass

    def _setup_ydl_opts(self, **extra_opts) -> dict:
        """Prepare yt_dlp options with safe defaults for metadata extraction."""
        base_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "no_warnings": True,
        }
        base_opts.update(extra_opts)
        return base_opts

    def _to_snippets(self, entries: list[dict[str, Any]]) -> list[DLSnippet]:
        """Convert yt_dlp raw entries into DLSnippet objects."""
        snippets: list[DLSnippet] = []
        for entry in entries:
            try:
                snippets.append(DLSnippet.model_validate(entry))
            except Exception:
                logger.debug("Failed to validate a snippet, skipping.")
                continue
        return snippets


class ConcurrentYoutubeDLFetcher(BaseYoutubeDLFetcher):
    """
    Base class for fetchers that utilize thread pools for concurrent extraction.
    """
    def __init__(self, video_ids: list[str], info: str | None = None, description: str | None = None):
        """
        Initialize the concurrent fetcher.

        Args:
            video_ids (list[str]): List of YouTube video IDs to process.
            info (str | None): Short name for the type of data being fetched (for logging).
            description (str | None): Description text for the tqdm progress bar.
        """
        self.video_ids = video_ids
        self.info = info
        self.description = description
    
    def fetch(self) -> list:
        logger.info(f"Starting to fetch {self.info} for {len(self.video_ids)} videos...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(self.fetch_single, video_id) for video_id in self.video_ids]
            results = []
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(self.video_ids), 
                              desc=self.description, disable=should_disable_progress()):
                try:
                    res = future.result()
                    if res is not None:
                        results.append(res)
                except Exception:
                    logger.exception("Thread encountered an unexpected error while fetching data.")
            return results

    @abstractmethod
    def fetch_single(self, video_id: str):
        """Must be implemented by subclass"""
        pass


class CommentFetcher(ConcurrentYoutubeDLFetcher):
    """
    Concurrent fetcher specifically for retrieving YouTube comments.
    """
    def __init__(self, video_ids: list[str], max_comments: int = 20, sort: Literal['top', 'new'] = 'top'):
        """
        Initialize the CommentFetcher.

        Args:
            video_ids (list[str]): List of YouTube video IDs.
            max_comments (int): Max number of comments to retrieve per video. Defaults to 20.
            sort (Literal['top', 'new']): Criteria for sorting comments. 
                Use 'top' for relevance or 'new' for date. Defaults to 'top'.
        """
        super().__init__(video_ids, 'comments', 'Fetching Comments')
        self.max_comments = max_comments
        self.sort = sort
            
    def fetch_single(self, video_id: str) -> VideoComments | None:
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        ydl_opts_deep = {
            "quiet": True,
            "skip_download": True,
            "force_empty": True,
            "getcomments": True,
            "no_warnings": True,
            "extractor_args": {
                "youtube": {
                    "max_comments": [str(self.max_comments)],
                    "comment_sort": [self.sort]
                }
            }
        }
        try:       
            with yt_dlp.YoutubeDL(ydl_opts_deep) as ydl: #type: ignore[arg-type]
                info_dict = ydl.extract_info(video_url, download=False)
                data = cast(list[dict[str, Any]], info_dict.get('comments', None) or [])
                validated_comments = self._safe_validate_comments(raw_comments=data)
                return VideoComments(video_id=video_id, comments=validated_comments)
        except Exception as e:
            logger.exception(f"Failed to fetch comments for {video_id}: {e}")
            return None
        
    def _safe_validate_comments(self, raw_comments: list[dict[str, Any]]) -> list[Comment]:
        """Handles comments with missing fields and returns completed data."""
        comments: list[Comment] = []
        for raw in raw_comments:
            try:
                comments.append(Comment.model_validate(raw))
            except Exception:
                logger.debug("Couldn't validate a comment.")
                continue
        return comments


class ChannelFetcher(BaseYoutubeDLFetcher):
    """
    Fetches recent videos from a YouTube channel via handles or URLs.
    """

    def __init__(self, channel_handle: str, max_results: int | None = 20, tab: Literal['videos', 'shorts', 'streams'] = 'videos'):
        """
        Initialize the ChannelFetcher.

        Args:
            channel_handle (str): The channel handle (e.g. "@caseoh_") or full channel URL.
            max_results (int | None): Maximum number of videos to fetch. 
                Set to None to fetch all available videos. Defaults to 20.
            tab (Literal): The channel tab to fetch from. 
                Options: 'videos', 'shorts', or 'streams'. Defaults to 'videos'.
        """
        super().__init__(max_results)
        self.channel_handle = channel_handle
        self.tab = tab

        if "https://" in channel_handle:
            self.channel_handle = self._find_channel_handle_from_url(channel_handle)

    def fetch(self) -> list[DLSnippet]:
        ydl_opts = self._setup_ydl_opts()
        if self.max_results is not None:
            ydl_opts["playlistend"] = self.max_results

        url = f"https://www.youtube.com/@{self.channel_handle.replace('@', '').strip()}/{self.tab}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: #type: ignore[arg-type]
            info = ydl.extract_info(url, download=False)
            entries = cast(list[dict[str, Any]], info.get("entries", []))
            return self._to_snippets(entries)

    @staticmethod
    def _find_channel_handle_from_url(url: str) -> str:
        """Extract the channel handle from a full YouTube channel URL."""
        logger.debug("Extracting channel handle from URL...")
        parsed = urlparse(url)
        path = parsed.path
        if "@" in path:
            handle = path.split("@", 1)[1].split("/")[0]
            return handle.strip()
        raise ValueError(f"Could not extract channel handle from URL: {url}")


class PlaylistFetcher(BaseYoutubeDLFetcher):
    """
    Fetches all videos from a given YouTube playlist.
    """

    def __init__(self, playlist_id: str, max_results: int | None = 20):
        """
        Initialize the PlaylistFetcher.

        Args:
            playlist_id (str): The unique playlist ID or the full playlist URL.
            max_results (int | None): Maximum number of videos to retrieve from the playlist.
                Set to None for the entire playlist. Defaults to 20.
        """
        super().__init__(max_results)
        self.playlist_id = playlist_id

        if "https://" in playlist_id:
            self.playlist_id = self._find_playlist_id_from_url(url=playlist_id)

    def fetch(self) -> list[DLSnippet]:
        ydl_opts = self._setup_ydl_opts()
        if self.max_results is not None:
            ydl_opts["playlistend"] = self.max_results

        url = f"https://www.youtube.com/playlist?list={self.playlist_id.strip()}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: #type: ignore[arg-type]
            info = ydl.extract_info(url, download=False)
            entries = cast(list[dict[str, Any]], info.get("entries", []))
            return self._to_snippets(entries)

    @staticmethod
    def _find_playlist_id_from_url(url: str) -> str:
        """Extract the playlist ID from a YouTube playlist URL."""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        playlist_id_list = query_params.get("list")
        if playlist_id_list and len(playlist_id_list) > 0:
            return playlist_id_list[0].strip()
        raise ValueError(f"Could not extract playlist ID from URL: {url}")


class SearchFetcher(BaseYoutubeDLFetcher):
    """
    Fetches video snippets via global YouTube search.
    """
    def __init__(self, query: str, max_results: int = 20):
        """
        Initialize the SearchFetcher.

        Args:
            query (str): The search keywords (e.g., "Python tutorials").
            max_results (int): Total number of results to retrieve from search. Defaults to 20.
        """
        super().__init__(max_results)
        self.query = query

    def fetch(self) -> list[DLSnippet]:
        ydl_opts = self._setup_ydl_opts(default_search='ytsearch', no_playlist=True)
        search_query = f"ytsearch{self.max_results}:{self.query}"
        logger.info(f"Searching via yt-dlp: '{self.query}'")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: #type: ignore[arg-type]
            info = ydl.extract_info(search_query, download=False)
            entries = cast(list[dict[str, Any]], info.get("entries", []))
            return self._to_snippets(entries)


class VideoListFetcher(ConcurrentYoutubeDLFetcher):
    """
    Fetches detailed metadata for a specific list of YouTube video IDs.
    """

    def __init__(self, video_ids: list[str]):
        """
        Initialize the VideoListFetcher.

        Args:
            video_ids (list[str]): A list of unique YouTube video identifiers.
        """
        super().__init__(video_ids, 'metadata', 'Extracting Metadata')

    def fetch_single(self, video_id: str) -> DLSnippet | None:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: #type: ignore[arg-type]
            url = f"https://www.youtube.com/watch?v={video_id}"
            metadata = cast(dict[str, Any], ydl.extract_info(url, download=False))
            if not metadata: return None
        return DLSnippet.model_validate(metadata)