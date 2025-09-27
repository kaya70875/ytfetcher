import yt_dlp
from yt_dlp.utils import DownloadError
from ytfetcher.models.channel import DLSnippet

class YoutubeDL:
    """
    Simple wrapper for fetching video IDs from a YouTube channel using yt-dlp.

    Raises:
        yt_dlp.utils.DownloadError: If the channel cannot be accessed or videos cannot be fetched.
    """
    def __init__(self, channel_handle: str, max_results: int = 50):
        self.channel_handle = channel_handle
        self.max_results = max_results

    def fetch(self) -> list[DLSnippet]:
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': 'in_playlist',
                'skip_download': True,
                'playlistend': self.max_results
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                full_url = f"https://www.youtube.com/@{self.channel_handle}/videos"

                info = ydl.extract_info(full_url, download=False)
                entries = [e for e in info['entries'] if e]

                return [
                    DLSnippet(
                        video_id=entry['id'],
                        title=entry['title'],
                        description=entry['description'],
                        url=entry['url'],
                        duration=entry['duration'],
                        view_count=entry['view_count'],
                        thumbnails=entry['thumbnails']
                    )
                    for entry in entries
                ]
        except DownloadError as download_err:
            raise download_err

        except Exception as exc:
            raise exc
