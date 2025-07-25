from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import ProxyConfig
from ytfetcher.types.channel import Snippet
from ytfetcher.types.channel import FetchAndMetaResponse
from ytfetcher.config.http_config import HTTPConfig
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm  # type: ignore
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)


class TranscriptFetcher:
    """
    Asynchronously fetches transcripts for a list of YouTube video IDs using the YouTube Transcript API.

    Each transcript is paired with its associated metadata (snippet). Transcripts are fetched concurrently
    using threads, while optionally supporting proxy configurations and custom HTTP settings.

    Parameters:
        video_ids (list[str]): List of YouTube video IDs to fetch transcripts for.
        snippets (list[Snippet]): Corresponding metadata for each video.
        http_config (HTTPConfig): Optional HTTP configuration (e.g., headers, timeout).
        proxy_config (ProxyConfig | None): Optional proxy configuration for the YouTube Transcript API.
    """

    def __init__(self, video_ids: list[str], snippets: list[Snippet], http_config: HTTPConfig = HTTPConfig(), proxy_config: ProxyConfig | None = None):
        self.video_ids = video_ids
        self.snippets = snippets
        self.executor = ThreadPoolExecutor(max_workers=30)
        self.proxy_config = proxy_config
        self.httpx_client = httpx.Client(timeout=http_config.timeout, headers=http_config.headers)

    async def fetch(self) -> list[FetchAndMetaResponse]:
        """
        Asynchronously fetches transcripts for all provided video IDs.

        Transcripts are fetched using threads wrapped in asyncio. Results are streamed as they are completed,
        and errors like `NoTranscriptFound`, `TranscriptsDisabled`, or `VideoUnavailable` are silently handled.

        Returns:
            list[FetchAndMetaResponse]: A list of successful transcript and snippet pairs.
        """

        async def run_in_thread(vid: str, snip: Snippet):
            return await asyncio.to_thread(self._fetch_single, vid, snip)

        tasks = [run_in_thread(vid, snip) for vid, snip in zip(self.video_ids, self.snippets)]

        results = []
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Fetching transcripts", unit='transcript'):
            result = await coro
            if result:
                results.append(FetchAndMetaResponse(
                    video_id=result["video_id"],
                    transcript=result["transcript"],
                    snippet=Snippet(**result["snippet"])
                ))

        return results

    def _fetch_single(self, video_id: str, snippet: Snippet) -> dict | None:
        """
        Fetches a single transcript and returns structured data.

        Handles known errors from the YouTube Transcript API gracefully.
        Logs warnings for unavailable or disabled transcripts.

        Parameters:
            video_id (str): The ID of the YouTube video to fetch.
            snippet (Snippet): Metadata associated with the video.

        Returns:
            dict | None: A dictionary with video_id, transcript, and serialized snippet,
                         or None if transcript is unavailable.
        """
        try:
            yt_api = YouTubeTranscriptApi(http_client=self.httpx_client, proxy_config=self.proxy_config)
            transcript = yt_api.fetch(video_id).to_raw_data()
            logger.info(f'{video_id} fetched.')
            return {
                "video_id": video_id,
                "transcript": transcript,
                "snippet": snippet.model_dump()
            }
        except (NoTranscriptFound, VideoUnavailable, TranscriptsDisabled) as e:
            logger.warning(e)
            return None
        except Exception as e:
            print(f'Error while fetching transcript from video: {video_id} ', e)
            logger.warning(f'Error while fetching transcript from video: {video_id} ', e)
            return None
