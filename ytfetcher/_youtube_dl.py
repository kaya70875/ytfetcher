import yt_dlp

class YoutubeDL:
    """
    Simple wrapper for fetching video IDs from a YouTube channel using yt-dlp.

    Raises:
        yt_dlp.utils.DownloadError: If the channel cannot be accessed or videos cannot be fetched.
    """
    def __init__(self, channel_handle: str, max_results: int = 50):
        self.channel_handle = channel_handle
        self.max_results = max_results
        self.video_ids = self._get_video_ids()

    def _get_video_ids(self) -> list[str]:
        ydl_opts = {
            'quiet': True,
            'extract_flat': 'in_playlist',
            'skip_download': True,
            'playlistend': self.max_results
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            full_url = f"https://www.youtube.com/@{self.channel_handle}/videos"

            info = ydl.extract_info(full_url, download=False)
            return [e['id'] for e in info['entries'] if e.get('id')]
