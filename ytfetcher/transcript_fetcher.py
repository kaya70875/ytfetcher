from ytfetcher.types.channel import Snippet
from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled, IpBlocked
from youtube_transcript_api import YouTubeTranscriptApi
from concurrent.futures import ThreadPoolExecutor
from ytfetcher.types.channel import FetchAndMetaResponse, Transcript
from ytfetcher.config.http_config import HTTPConfig
import asyncio
import httpx

class TranscriptFetcher:
    def __init__(self, video_ids: list[str], snippets: list[Snippet], http_config: HTTPConfig):
        self.video_ids = video_ids
        self.snippets = snippets
        self.executor = ThreadPoolExecutor(max_workers=30)
    
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
            yt_api = YouTubeTranscriptApi(http_client=self.httpx_client)
            transcript = yt_api.fetch(video_id).to_raw_data()
            print(f'{video_id} fetched.')
            return {
                "video_id": video_id,
                "transcript": transcript,
                "snippet": snippet.model_dump()
            }
        except (NoTranscriptFound, VideoUnavailable, TranscriptsDisabled):
            return None
        except(IpBlocked):
            print('Youtube is blocking your ip...')
            return None
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            return None