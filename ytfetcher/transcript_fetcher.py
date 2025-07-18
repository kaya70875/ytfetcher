from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import ProxyConfig
from ytfetcher.types.channel import Snippet
from ytfetcher.types.channel import FetchAndMetaResponse
from ytfetcher.config.http_config import HTTPConfig
from concurrent.futures import ThreadPoolExecutor
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

class TranscriptFetcher:
    def __init__(self, video_ids: list[str], snippets: list[Snippet], http_config: HTTPConfig, proxy_config: ProxyConfig | None = None):
        self.video_ids = video_ids
        self.snippets = snippets
        self.executor = ThreadPoolExecutor(max_workers=30)
        self.proxy_config = proxy_config
    
        self.httpx_client = httpx.Client(timeout=http_config.timeout, headers=http_config.headers)

    async def fetch(self) -> list[FetchAndMetaResponse]:
        async def run_in_thread(vid: str, snip: Snippet):
            return await asyncio.to_thread(self._fetch_single, vid, snip)

        tasks = [run_in_thread(vid, snip) for vid, snip in zip(self.video_ids, self.snippets)]
        results = await asyncio.gather(*tasks)

        return [
            FetchAndMetaResponse(
                video_id=result["video_id"],
                transcript=result["transcript"],
                snippet=Snippet(**result["snippet"])
            )
            for result in results if result
        ]

    def _fetch_single(self, video_id: str, snippet: Snippet) -> dict | None:
        try:
            yt_api = YouTubeTranscriptApi(http_client=self.httpx_client, proxy_config=self.proxy_config)
            transcript = yt_api.fetch(video_id).to_raw_data()
            logger.info(f'{video_id} fetched.')
            print(f'{video_id} fetched.')
            return {
                "video_id": video_id,
                "transcript": transcript,
                "snippet": snippet.model_dump()
            }
        except (NoTranscriptFound, VideoUnavailable, TranscriptsDisabled) as e:
            logger.warning(e)
            print("Error", e)
            return None
        except Exception as e:
            print('er', e)
            logger.warning(f"⚠️ Unexpected error: {e}")
            return None