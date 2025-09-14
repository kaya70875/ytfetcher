from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import ProxyConfig
from ytfetcher.models.channel import Transcript, ChannelData, VideoTranscript
from ytfetcher.config.http_config import HTTPConfig
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm  # type: ignore
import asyncio
import requests
import logging

logger = logging.getLogger(__name__)


class TranscriptFetcher:
    """
    Asynchronously fetches transcripts for a list of YouTube video IDs using the YouTube Transcript API.

    Transcripts are fetched concurrently using threads, while optionally supporting proxy configurations and custom HTTP settings.

    Parameters:
        video_ids (list[str]): List of YouTube video IDs to fetch transcripts for.
        http_config (HTTPConfig): Optional HTTP configuration (e.g., headers, timeout).
        proxy_config (ProxyConfig | None): Optional proxy configuration for the YouTube Transcript API.
    """

    def __init__(self, video_ids: list[str], http_config: HTTPConfig = HTTPConfig(), proxy_config: ProxyConfig | None = None):
        self.video_ids = video_ids
        self.executor = ThreadPoolExecutor(max_workers=30)
        self.proxy_config = proxy_config
        self.http_client = requests.Session()

        # Initialize client
        self.http_client.headers = http_config.headers

    async def fetch(self) -> list[ChannelData]:
        """
        Asynchronously fetches transcripts for all provided video IDs.

        Transcripts are fetched using threads wrapped in asyncio. Results are streamed as they are completed,
        and errors like `NoTranscriptFound`, `TranscriptsDisabled`, or `VideoUnavailable` are silently handled.

        Returns:
            list[VideoTranscript]: A list of successful transcripts from list of videos with video_id information.
        """

        async def run_in_thread(video_id: str):
            return await asyncio.to_thread(self._fetch_single, video_id)

        tasks = [run_in_thread(video_id) for video_id in self.video_ids]

        channel_data: list[ChannelData] = []
        
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Fetching transcripts", unit='transcript'):
            result: VideoTranscript = await coro
            if result:
                channel_data.append(
                    ChannelData(
                        video_id=result.video_id,
                        transcripts=result.transcripts,
                        metadata=None
                    )
                )

        return channel_data

    def _fetch_single(self, video_id: str) -> VideoTranscript | None:
        """
        Fetches a single transcript and returns structured data.

        Handles known errors from the YouTube Transcript API gracefully.
        Logs warnings for unavailable or disabled transcripts.

        Parameters:
            video_id (str): The ID of the YouTube video to fetch.

        Returns:
            VideoTranscript | None: A dictionary with transcript and video_id,
                         or None if transcript is unavailable.
        """
        try:
            yt_api = YouTubeTranscriptApi(http_client=self.http_client, proxy_config=self.proxy_config)
            transcript: list[Transcript] = yt_api.fetch(video_id).to_raw_data()
            logger.info(f'{video_id} fetched.')
            return VideoTranscript(
                video_id=video_id,
                transcripts=transcript
            )
        except (NoTranscriptFound, VideoUnavailable, TranscriptsDisabled) as e:
            logger.warning(e)
            return None
        except Exception as e:
            print(f'Error while fetching transcript from video: {video_id} ', e)
            logger.warning(f'Error while fetching transcript from video: {video_id} ', e)
            return None
