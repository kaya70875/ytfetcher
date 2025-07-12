import httpx
from youtube_transcript_api import YouTubeTranscriptApi
from ytfetcher.youtube_v3 import YoutubeV3
from scripts.headers import get_realistic_headers

class YTFetcher:
    def __init__(self, yt_client: YoutubeV3, channel_name: str, proxy=None, max_results: int = 50, timeout: httpx.Timeout | None = None, headers: dict | None = None):
        self.yt_client = yt_client
        self.channel_name = channel_name
        self.proxy = proxy
        self.max_results = max_results

        self.headers = headers or get_realistic_headers()
        self.timeout = timeout or httpx.Timeout(10.0)
    
        self.yt_api = YouTubeTranscriptApi(http_client=httpx.Client(timeout=self.timeout, headers=self.headers))
    
    def fetch_transcripts(self):
        pass

    def fetch_transcripts_with_snippets(self):
        pass