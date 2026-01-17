from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import ProxyConfig
from ytfetcher.models.channel import ChannelData, VideoTranscript, Transcript
from ytfetcher.config.http_config import HTTPConfig
from ytfetcher.utils.log import log
from ytfetcher.utils.state import should_disable_progress
from concurrent import futures
from tqdm import tqdm  # type: ignore
from typing import Iterable
import requests
import logging
import re

logger = logging.getLogger(__name__)
class TranscriptFetcher:
    """
    Synchronously fetches transcripts for a list of YouTube video IDs 
    using the YouTube Transcript API.

    Transcripts are fetched concurrently using threads, while optionally 
    supporting proxy configurations and custom HTTP settings.

    Args:
        video_ids (list[str]): 
            List of YouTube video IDs to fetch transcripts for.

        http_config (HTTPConfig): 
            Optional HTTP configuration (e.g., headers, timeout).

        proxy_config (ProxyConfig | None): 
            Optional proxy configuration for the YouTube Transcript API.

        languages (Iterable[str]): 
            A list of language codes in descending priority. 
            For example, if this is set to ["de", "en"], it will first try 
            to fetch the German transcript ("de") and then the English one 
            ("en") if it fails. Defaults to ["en"].
    """

    def __init__(self, video_ids: list[str], http_config: HTTPConfig = HTTPConfig(), proxy_config: ProxyConfig | None = None, languages: Iterable[str] = ("en",), manually_created: bool = False):
        self.video_ids = video_ids
        self.languages = languages
        self.manually_created = manually_created
        self.executor = futures.ThreadPoolExecutor(max_workers=30)
        self.proxy_config = proxy_config
        self.http_client = requests.Session()

        # Initialize client
        self.http_client.headers = http_config.headers

    def fetch(self) -> list[ChannelData]:
        """
        Asynchronously fetches transcripts for all provided video IDs.

        Transcripts are fetched using threads wrapped in ThreadPoolExecutor. Results are streamed as they are completed,
        and errors like `NoTranscriptFound`, `TranscriptsDisabled`, or `VideoUnavailable` are silently handled.

        Returns:
            list[VideoTranscript]: A list of successful transcripts from list of videos with video_id information.
        """

        with self.executor as executor:
            futures = [executor.submit(self._fetch_single, video_id) for video_id in self.video_ids]

            channel_data = self._build_channel_data(futures)
            
            if not channel_data and self.manually_created: log("No manually created transcripts found!", level="ERROR")

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
            transcript: list[Transcript] | None = self._decide_fetch_method(yt_api, video_id)

            if not transcript: return None

            cleaned_transcript = self._clean_transcripts(transcript)
            logger.info(f'{video_id} fetched.')
            return VideoTranscript(
                video_id=video_id,
                transcripts=cleaned_transcript
            )
        except (NoTranscriptFound, VideoUnavailable, TranscriptsDisabled) as e:
            logger.warning(e)
            return None
        except Exception as e:
            logger.warning(f'Error while fetching transcript from video: {video_id} ', e)
            return None
    
    def _decide_fetch_method(self, yt_api: YouTubeTranscriptApi, video_id: str) -> list[Transcript] | None:
        """
        Decides correct fetch method based on manually created flag.
        Args:
            yt_api(YouTubeTranscriptApi): Ytt api instance.
            video_id(str): Video id for current video.
        Returns:
            Optional[list[Transcript]]:
                A list of transcript entries as dictionaries if available, 
                otherwise `None` when no transcript is found.
        """
        if self.manually_created:
            try:
                raw_transcripts = yt_api.list(video_id).find_manually_created_transcript(language_codes=self.languages).fetch().to_raw_data()
                return self._convert_to_transcript_object(raw_transcripts)
            except NoTranscriptFound:
                logger.info(f"Couldn't found manually created transcript for {video_id}")
                return None
        
        raw_transcripts = yt_api.fetch(video_id, languages=self.languages).to_raw_data()
        return self._convert_to_transcript_object(raw_transcripts)
    
    @staticmethod
    def _build_channel_data(tasks: list[futures.Future]) -> list[ChannelData]:
        """
        Builds list of `ChannelData` from all tasks from completed thread with progress support.
        Args:
            tasks: List of completed tasks.
        Returns:
            list[ChannelData]: ChannelData list contains transcripts.
        """
        channel_data: list[ChannelData] = []

        for future in tqdm(futures.as_completed(tasks), total=len(tasks), desc="Fetching transcripts", unit='transcript', disable=should_disable_progress()):
            result: VideoTranscript = future.result()
            if result:
                channel_data.append(
                    ChannelData(
                        video_id=result.video_id,
                        transcripts=result.transcripts,
                        metadata=None
                    )
                )
        return channel_data

    @staticmethod
    def _clean_transcripts(transcripts: list[Transcript]) -> list[Transcript]:
        """
        Cleans unnecessary text from transcripts like [Music], [Applause], etc.
        Returns:
            list[Transcript]: list of Transcript objects.
        """
        for entry in transcripts:

            # Remove unnecessary text patterns like [Music], [Applause], etc.
            cleaned_text = re.sub(r'\[.*?\]', '', entry.text)

            # Remove leading '>>' markers (and optional spaces)
            cleaned_text = re.sub(r'^\s*>>\s*', '', cleaned_text)

            # Remove extra whitespace
            cleaned_text = ' '.join(cleaned_text.split())

            # Update the transcript text
            entry.text = cleaned_text

        return transcripts
    
    @staticmethod
    def _convert_to_transcript_object(transcript_dict: list[dict]) -> list[Transcript]:
        # No need for exception handling, transcripts should be complete.
        return [Transcript.model_validate(transcript) for transcript in transcript_dict]

