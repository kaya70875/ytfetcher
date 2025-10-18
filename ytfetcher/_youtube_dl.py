import yt_dlp
import logging
from ytfetcher.models.channel import DLSnippet
from tqdm import tqdm
from abc import ABC, abstractmethod
from urllib.parse import urlparse, parse_qs
from ytfetcher.utils.log import log

logger = logging.getLogger(__name__)

class BaseYoutubeDLFetcher(ABC):
    def __init__(self, max_results: int = 50):
        self.max_results = max_results
    
    @abstractmethod
    def fetch(self) -> list[DLSnippet]:
        """
        Main fetch logic for subclasses.
        """
        pass
    
    def _setup_ydl_opts(self, **extra_opts) -> dict:
        base_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "no_warnings": True,
        }
        base_opts.update(extra_opts)
        return base_opts

    def _to_snippets(self, entries: list[dict]) -> list[DLSnippet]:
        return [
                DLSnippet(
                    video_id=entry['id'],
                    title=entry['title'],
                    description=entry['description'],
                    url=entry['url'] or f"https://youtube.com/watch?v={entry.get('id')}",
                    duration=entry['duration'],
                    view_count=entry['view_count'],
                    thumbnails=entry['thumbnails']
                )
                for entry in entries
            ]

class ChannelFetcher(BaseYoutubeDLFetcher):
    def __init__(self, channel_handle: str, max_results = 50):
        super().__init__(max_results)
        self.channel_handle = channel_handle

        if "https://" in channel_handle:
            self.channel_handle = self._find_channel_handle_from_url(channel_handle)
    
    def fetch(self) -> list[DLSnippet]:
        ydl_opts = self._setup_ydl_opts(playlistend=self.max_results)
        url = f"https://www.youtube.com/@{self.channel_handle.replace('@', '').strip()}/videos"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries: list[dict] = info.get("entries", [])
            return self._to_snippets(entries)
    
    @staticmethod
    def _find_channel_handle_from_url(url: str) -> str:
        """
        Extract the channel handle from a full YouTube channel URL.

        Handles URLs like:
        - https://www.youtube.com/@handle
        - https://www.youtube.com/@handle/
        - https://www.youtube.com/@handle/featured
        - https://www.youtube.com/@handle/videos

        Args:
            url (str): The full YouTube channel URL.

        Returns:
            str: Extracted channel handle (e.g. 'handle').
        """
        log("Got full URL, trying to extract channel handle. If it fails, try providing only the handle.", level="WARNING")

        parsed = urlparse(url)
        path = parsed.path

        # Find the '@' segment and extract only the handle portion
        if '@' in path:
            handle = path.split('@', 1)[1].split('/')[0]
            return handle.strip()

        raise ValueError(f"Could not extract channel handle from URL: {url}")

class PlaylistFetcher(BaseYoutubeDLFetcher):
    def __init__(self, playlist_id: str, max_results = 50):
        super().__init__(max_results)
        self.playlist_id = playlist_id

        if "https://" in playlist_id:
            self.playlist_id = self._find_playlist_id_from_url(url=playlist_id)
    
    def fetch(self) -> list[DLSnippet]:
        ydl_opts = self._setup_ydl_opts(playlistend=self.max_results)
        url = f"https://www.youtube.com/playlist?list={self.playlist_id.strip()}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries: list[dict] = info.get("entries", [])
            return self._to_snippets(entries)
        
    @staticmethod
    def _find_playlist_id_from_url(url: str) -> str:
        """
        Extracts a YouTube playlist ID from a full playlist URL.

        Handles URLs like:
        - https://www.youtube.com/playlist?list=PL12345
        - https://www.youtube.com/playlist?list=PL12345&si=abcd
        - https://youtube.com/watch?v=abc123&list=PL12345

        Args:
            url (str): The full YouTube playlist URL.

        Returns:
            str: The extracted playlist ID (e.g., 'PL12345').

        Raises:
            ValueError: If the URL does not contain a 'list' parameter.
        """
        log("Got full URL, trying to extract playlist ID. If it fails, try providing only playlist ID.", level="WARNING")

        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        playlist_id_list = query_params.get("list")

        if playlist_id_list and len(playlist_id_list) > 0:
            return playlist_id_list[0].strip()

        raise ValueError(f"Could not extract playlist ID from URL: {url}")


class VideoListFetcher(BaseYoutubeDLFetcher):
    def __init__(self, video_ids: list[str], max_results = 50):
        super().__init__(max_results)
        self.video_ids = video_ids
    
    def fetch(self):
        ydl_opts = self._setup_ydl_opts()
        results = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for video_id in tqdm(self.video_ids, desc="Extracting metadata", unit="video"):
                url = f"https://www.youtube.com/watch?v={video_id}"
                info = ydl.extract_info(url, download=False)
                if info:
                    results.append(info)
        return self._to_snippets(entries=results)

def get_fetcher(channel_handle: str | None = None, playlist_id: str | None = None, video_ids: list[str] | None = None, max_results: int = 50) -> BaseYoutubeDLFetcher:
    if playlist_id:
        return PlaylistFetcher(playlist_id, max_results)
    elif channel_handle:
        return ChannelFetcher(channel_handle, max_results)
    elif video_ids:
        return VideoListFetcher(video_ids)
    raise ValueError("No YoutubeDLFetcher found.")