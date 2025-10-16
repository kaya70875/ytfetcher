import yt_dlp
import logging
from yt_dlp.utils import DownloadError
from ytfetcher.models.channel import DLSnippet
from tqdm import tqdm
from abc import ABC, abstractmethod

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
    
    def fetch(self) -> list[DLSnippet]:
        ydl_opts = self._setup_ydl_opts(playlistend=self.max_results)
        url = f"https://www.youtube.com/@{self.channel_handle}/videos"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries: list[dict] = info.get("entries", [])
            return self._to_snippets(entries)

class PlaylistFetcher(BaseYoutubeDLFetcher):
    def __init__(self, playlist_id: str, max_results = 50):
        super().__init__(max_results)
        self.playlist_id = playlist_id
    
    def fetch(self) -> list[DLSnippet]:
        ydl_opts = self._setup_ydl_opts(playlistend=self.max_results)
        url = f"https://www.youtube.com/playlist?list={self.playlist_id}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries: list[dict] = info.get("entries", [])
            return self._to_snippets(entries)

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
        #print('res', results[0].keys())
        return self._to_snippets(entries=results)

def get_fetcher(channel_handle: str | None = None, playlist_id: str | None = None, video_ids: list[str] | None = None, max_results: int = 50) -> BaseYoutubeDLFetcher:
    if playlist_id:
        return PlaylistFetcher(playlist_id, max_results)
    elif channel_handle:
        return ChannelFetcher(channel_handle, max_results)
    elif video_ids:
        return VideoListFetcher(video_ids)
    raise ValueError("You must provide either channel_handle or a playlist id.")