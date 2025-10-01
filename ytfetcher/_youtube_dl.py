import yt_dlp
from yt_dlp.utils import DownloadError
from ytfetcher.models.channel import DLSnippet

class YoutubeDL:
    """
    Simple wrapper for fetching video IDs from a YouTube channel using yt-dlp.

    Raises:
        yt_dlp.utils.DownloadError: If the channel cannot be accessed or videos cannot be fetched.
    """

    @staticmethod
    def fetch(channel_handle: str, max_results: int = 50) -> list[DLSnippet]:
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': 'in_playlist',
                'skip_download': True,
                'playlistend': max_results
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                full_url = f"https://www.youtube.com/@{channel_handle}/videos"

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
    
    @staticmethod
    def fetch_with_custom_video_ids(video_ids: list[str]) -> list[DLSnippet]:
        try:
            ydl_opts = {
                "quiet": True,
                "skip_download": True,
                "extract_flat": True,
                "no_warnings": True
            }

            results: list[DLSnippet] = []

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for video_id in video_ids:
                    URL = f'https://www.youtube.com/watch?v={video_id}'

                    info = ydl.extract_info(URL, download=False)
                    
                    if info:
                        results.append(
                            DLSnippet(
                                video_id=info.get("id"),
                                title=info.get("title"),
                                description=info.get("description"),
                                url=URL,
                                duration=info.get("duration"),
                                view_count=info.get("view_count"),
                            )
                        )
                        
            return results
        except DownloadError as download_err:
            raise download_err

        except Exception as exc:
            raise exc
