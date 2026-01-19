import yt_dlp
import concurrent.futures
import logging
from ytfetcher.models.channel import DLSnippet, Comment
from ytfetcher.utils.log import log
from ytfetcher.utils.state import should_disable_progress
from tqdm import tqdm
from abc import ABC, abstractmethod
from urllib.parse import urlparse, parse_qs
from typing import Any, cast

logger = logging.getLogger(__name__)
class ConcurrentYoutubeDLFetcher(ABC):
    def __init__(self, video_ids: list[str], info: str | None = None, description: str | None = None):
        self.video_ids = video_ids
        self.info = info
        self.description = description
    
    def fetch(self) -> list:
        logger.info(f"Starting to fetch {self.info} for {len(self.video_ids)} videos...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(self.fetch_single, video_id) for video_id in self.video_ids]

            results = []
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(self.video_ids), desc=self.description, disable=should_disable_progress()):
                res = future.result()
                if res is not None:
                    results.append(res)
                
            return results

    @abstractmethod
    def fetch_single(self, video_id: str):
        """Must be implemented by subclass"""
        pass

class CommentFetcher(ConcurrentYoutubeDLFetcher):
    def __init__(self, video_ids: list[str], max_comments: int = 20):
        super().__init__(video_ids, 'comments', 'Fetching Comments')
        self.max_comments = max_comments
            
    def fetch_single(self, video_id: str) -> list[Comment]:
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        
        ydl_opts_deep = {
            "quiet": True,
            "skip_download": True,
            "force_empty": True,
            "getcomments": True,
            "no_warnings": True,
            "extractor_args": {
                "youtube": {
                    "max_comments": [
                        str(self.max_comments),
                        "all",
                        "0",
                        "0"
                    ],
                    "comment_sort": "top"
                }
            }
        }
        try:       
            with yt_dlp.YoutubeDL(ydl_opts_deep) as ydl: #type: ignore[arg-type]
                info_dict = ydl.extract_info(video_url, download=False)
                data = cast(list[dict[str, Any]], info_dict.get('comments', None) or [])
                return self._safe_validate_comments(data)
        
        except Exception as e:
            logger.warning(f"Failed to fetch comments for {video_id}: {e}")
            return []
        
    def _safe_validate_comments(self, raw_comments: list[dict[str, Any]]) -> list[Comment]:
        """
        Handles comments with missing fields and returns completed data.
        """
        comments: list[Comment] = []

        for raw in raw_comments:
            try:
                comments.append(Comment.model_validate(raw))
            except Exception:
                continue

        return comments


class BaseYoutubeDLFetcher(ABC):
    """
    Abstract base class for YouTube data fetching using yt_dlp.

    Provides common setup utilities for subclasses that fetch
    metadata from channels, playlists, or specific videos.

    Attributes:
        max_results (int): The maximum number of results to fetch.
    """

    def __init__(self, max_results: int = 50):
        self.max_results = max_results

    @abstractmethod
    def fetch(self) -> list[DLSnippet]:
        """
        Abstract method to be implemented by subclasses.

        Should contain the logic to fetch data from YouTube.
        """
        pass

    def _setup_ydl_opts(self, **extra_opts) -> dict:
        """
        Prepare yt_dlp options with safe defaults for metadata extraction.

        Args:
            **extra_opts: Additional yt_dlp options to override or extend defaults.

        Returns:
            dict: The complete yt_dlp options dictionary.
        """
        base_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "no_warnings": True,
        }
        base_opts.update(extra_opts)
        return base_opts

    def _to_snippets(self, entries: list[dict[str, Any]]) -> list[DLSnippet]:
        """
        Convert yt_dlp raw entries into DLSnippet objects.

        Args:
            entries (list[dict]): List of yt_dlp video entries.

        Returns:
            list[DLSnippet]: List of structured DLSnippet objects.
        """
        return [DLSnippet.model_validate(entry) for entry in entries]


class ChannelFetcher(BaseYoutubeDLFetcher):
    """
    Fetches recent videos from a YouTube channel.

    Supports both direct channel handles (e.g. "@caseoh_")
    and full channel URLs.
    Args:
        channel_handle (str): The channel handle or URL.
        max_results (int): Maximum number of videos to fetch.
    """

    def __init__(self, channel_handle: str, max_results: int = 50):
        super().__init__(max_results)
        self.channel_handle = channel_handle

        if "https://" in channel_handle:
            self.channel_handle = self._find_channel_handle_from_url(channel_handle)

    def fetch(self) -> list[DLSnippet]:
        ydl_opts = self._setup_ydl_opts(playlistend=self.max_results)
        url = f"https://www.youtube.com/@{self.channel_handle.replace('@', '').strip()}/videos"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl: #type: ignore[arg-type]
            info = ydl.extract_info(url, download=False)
            entries = cast(list[dict[str, Any]], info.get("entries", []))
            return self._to_snippets(entries)

    @staticmethod
    def _find_channel_handle_from_url(url: str) -> str:
        """
        Extract the channel handle from a full YouTube channel URL.

        Handles URLs such as:
            - https://www.youtube.com/@handle
            - https://www.youtube.com/@handle/
            - https://www.youtube.com/@handle/featured
            - https://www.youtube.com/@handle/videos

        Args:
            url (str): Full YouTube channel URL.

        Returns:
            str: The extracted channel handle (e.g. "handle").

        Raises:
            ValueError: If no valid handle can be extracted.
        """
        logger.warning("Got full URL, trying to extract channel handle. If it fails, try providing only the handle.")

        parsed = urlparse(url)
        path = parsed.path

        if "@" in path:
            handle = path.split("@", 1)[1].split("/")[0]
            return handle.strip()

        raise ValueError(f"Could not extract channel handle from URL: {url}")


class PlaylistFetcher(BaseYoutubeDLFetcher):
    """
    Fetches all videos from a given YouTube playlist.

    Supports both playlist IDs and full playlist URLs.
    Args:
        playlist_id (str): The playlist ID or full URL.
        max_results (int): Maximum number of videos to fetch.
    """

    def __init__(self, playlist_id: str, max_results: int = 50):
        super().__init__(max_results)
        self.playlist_id = playlist_id

        if "https://" in playlist_id:
            self.playlist_id = self._find_playlist_id_from_url(url=playlist_id)

    def fetch(self) -> list[DLSnippet]:
        ydl_opts = self._setup_ydl_opts(playlistend=self.max_results)
        url = f"https://www.youtube.com/playlist?list={self.playlist_id.strip()}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl: #type: ignore[arg-type]
            info = ydl.extract_info(url, download=False)
            entries = cast(list[dict[str, Any]], info.get("entries", []))
            return self._to_snippets(entries)

    @staticmethod
    def _find_playlist_id_from_url(url: str) -> str:
        """
        Extract the playlist ID from a YouTube playlist URL.

        Handles URLs such as:
            - https://www.youtube.com/playlist?list=PL12345
            - https://www.youtube.com/playlist?list=PL12345&si=abcd
            - https://youtube.com/watch?v=abc123&list=PL12345

        Args:
            url (str): Full YouTube playlist URL.

        Returns:
            str: The extracted playlist ID (e.g. "PL12345").

        Raises:
            ValueError: If no valid playlist ID can be found.
        """
        logger.warning("Got full URL, trying to extract playlist ID. If it fails, try providing only playlist ID.")

        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        playlist_id_list = query_params.get("list")

        if playlist_id_list and len(playlist_id_list) > 0:
            return playlist_id_list[0].strip()

        raise ValueError(f"Could not extract playlist ID from URL: {url}")


class SearchFetcher(BaseYoutubeDLFetcher):
    """
    Fetches video snippets via yt-dlp search.
    """
    def __init__(self, query: str, max_results: int = 50):
        super().__init__(max_results)
        self.query = query

    def fetch(self) -> list[DLSnippet]:
        ydl_opts = self._setup_ydl_opts(default_search='ytsearch', no_playlist='True')

        search_query = f"ytsearch{self.max_results}:{self.query}"

        logger.info(f"Searching via yt-dlp: '{self.query}'")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl: #type: ignore[arg-type]
            info = ydl.extract_info(search_query, download=False)
            
            entries = cast(list[dict[str, Any]], info.get("entries", []))
            return self._to_snippets(entries)

class VideoListFetcher(ConcurrentYoutubeDLFetcher):
    """
    Fetches metadata for one or more specific YouTube videos.
    Args:
        video_ids (list[str]): List of YouTube video IDs.
    """

    def __init__(self, video_ids: list[str]):
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

def get_fetcher(
    channel_handle: str | None = None,
    playlist_id: str | None = None,
    video_ids: list[str] | None = None,
    query: str | None = None,
    max_results: int = 50,
) -> BaseYoutubeDLFetcher | ConcurrentYoutubeDLFetcher:
    """
    Factory function that returns the correct fetcher
    based on provided parameters.

    Args:
        channel_handle (str | None): YouTube channel handle or URL.
        playlist_id (str | None): YouTube playlist ID or URL.
        video_ids (list[str] | None): List of specific video IDs.
        max_results (int): Maximum number of videos to fetch.

    Returns:
        BaseYoutubeDLFetcher | ConcurrentYoutubeDLFetcher: An appropriate fetcher subclass instance.

    Raises:
        ValueError: If no valid input was provided.
    """
    if playlist_id:
        return PlaylistFetcher(playlist_id, max_results)
    elif channel_handle:
        return ChannelFetcher(channel_handle, max_results)
    elif video_ids:
        return VideoListFetcher(video_ids)
    elif query:
        return SearchFetcher(query, max_results)
    raise ValueError("No YoutubeDLFetcher found.")
