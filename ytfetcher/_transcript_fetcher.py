from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled, AgeRestricted
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import ProxyConfig
from ytfetcher.models.channel import VideoTranscript, Transcript
from ytfetcher.config.http_config import HTTPConfig
from ytfetcher.utils.state import should_disable_progress
from ytfetcher.utils import log
from concurrent import futures
from tqdm import tqdm
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

    When `manually_created=True`, the fetcher only retrieves manually created
    transcripts and skips auto-generated ones. This is useful for videos where
    you only want creator-provided transcripts and not AI-generated ones.

    Args:
        video_ids (list[str]):
            List of YouTube video IDs to fetch transcripts for.

        http_config (HTTPConfig):
            Optional HTTP configuration (e.g., headers, timeout).

        proxy_config (ProxyConfig | None):
            Optional proxy configuration for the YouTube Transcript API.

        languages (Iterable[str] | None):
            A list of language codes in descending priority.
            For example, if this is set to ["de", "en"], it will first try
            to fetch the German transcript ("de") and then the English one
            ("en") if it fails. Defaults to None.

        manually_created (bool):
            If True, only fetch manually created transcripts (skips auto-generated).
            If False, fetches auto-generated transcripts. Defaults to False.
    """

    def __init__(
        self,
        video_ids: list[str],
        http_config: HTTPConfig | None = None,
        proxy_config: ProxyConfig | None = None,
        languages: Iterable[str] | None = None,
        manually_created: bool = False
    ):
        """
        Initialize the TranscriptFetcher.

        Args:
            video_ids: List of YouTube video IDs to fetch transcripts for.
            http_config: Optional HTTP configuration (e.g., headers, timeout).
            proxy_config: Optional proxy configuration for the YouTube Transcript API.
            languages: List of language codes in descending priority. Defaults to ("en",).
            manually_created: If True, only fetch manually created transcripts
                and skip auto-generated ones. When True and no manual transcripts
                are found, logs an error. Defaults to False.
        """
        self.http_config = http_config or HTTPConfig()
        self.proxy_config = proxy_config
        self.video_ids = video_ids
        self.languages = languages
        self.manually_created = manually_created

        if manually_created and not languages:
            raise ValueError(
                "You must provide a language when using manually_created."
            )

    def fetch(self) -> list[VideoTranscript]:
        """
        Synchronously fetches transcripts for all provided video IDs.

        Transcripts are fetched using threads wrapped in ThreadPoolExecutor. Results are streamed as they are completed,
        and errors like `NoTranscriptFound`, `TranscriptsDisabled`, or `VideoUnavailable` are silently handled.

        Returns:
            list[VideoTranscript]: A list of successful transcripts from list of videos with video_id information.
        """

        with futures.ThreadPoolExecutor(max_workers=30) as executor:
            tasks = [executor.submit(self._fetch_single, video_id) for video_id in self.video_ids]
            video_transcript = self._collect_results(tasks)
            
        if not video_transcript and self.manually_created: 
            log(f'No manually created transcripts found for requested languages: {self.languages}', level='WARNING')
            logger.info("No manually created transcripts found!")

        return video_transcript

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
            session = requests.Session()
            session.headers.update(self.http_config.headers)
            yt_api = YouTubeTranscriptApi(http_client=session, proxy_config=self.proxy_config)
            transcript: list[Transcript] | None = self._decide_fetch_method(yt_api, video_id)

            if not transcript: return None

            cleaned_transcript = self._clean_transcripts(transcript)
            logger.debug(f'{video_id} fetched.')
            return VideoTranscript(
                video_id=video_id,
                transcripts=cleaned_transcript
            )
        except (VideoUnavailable, TranscriptsDisabled, AgeRestricted) as e:
            logger.warning(str(e).replace(e.GITHUB_REFERRAL, ''))
            return None
        except Exception as e:
            logger.exception(f'Error while fetching transcript from video: {video_id}')
            return None
    
    def _decide_fetch_method(self, yt_api: YouTubeTranscriptApi, video_id: str) -> list[Transcript] | None:
        """
        Selects and executes the appropriate transcript retrieval strategy.

        Strategy selection is based on the instance configuration:

        - If `manually_created` is True, attempts to fetch only manually created
        transcripts for the configured languages.
        - If `languages` is None, fetches the first available transcript
        regardless of language or origin.
        - Otherwise, fetches a transcript matching the configured language
        priority using the API's built-in selection logic.

        Args:
            yt_api: Initialized YouTubeTranscriptApi instance.
            video_id: YouTube video ID to retrieve transcripts for.

        Returns:
            A list of validated Transcript objects if successful,
            otherwise None when no suitable transcript is found.
        """
        if self.manually_created:
            return self._fetch_manual_transcript(yt_api=yt_api, video_id=video_id)
        
        elif self.languages is None:
            return self._fetch_first_available_transcript(yt_api=yt_api, video_id=video_id)
        
        return self._fetch_by_languages(yt_api=yt_api, video_id=video_id)
    
    def _fetch_manual_transcript(
        self,
        yt_api: YouTubeTranscriptApi,
        video_id: str
    ) -> list[Transcript] | None:
        """
        Fetches manually created transcripts for the given video.

        Attempts to retrieve a manually created transcript matching the
        configured language priority. If no such transcript exists,
        returns None without raising an exception.

        Args:
            yt_api: Initialized YouTubeTranscriptApi instance.
            video_id: YouTube video ID.

        Returns:
            A list of validated Transcript objects if a manually created
            transcript is found, otherwise None.
        """

        assert self.languages is not None, "languages must not be None here."

        try:
            transcript = (
                yt_api
                .list(video_id)
                .find_manually_created_transcript(language_codes=self.languages)
            )
            raw = transcript.fetch().to_raw_data()
            return self._convert_to_transcript_object(raw)

        except NoTranscriptFound:
            logger.info(f"No manually created transcript found for {video_id}")
            return None

    def _fetch_first_available_transcript(
        self,
        yt_api: YouTubeTranscriptApi,
        video_id: str
    ) -> list[Transcript] | None:
        """
        Fetches the first available transcript for a video.

        Iterates through the transcript list returned by the API and
        retrieves the first transcript encountered, regardless of language
        or whether it is manually created or auto-generated.

        Args:
            yt_api: Initialized YouTubeTranscriptApi instance.
            video_id: YouTube video ID.

        Returns:
            A list of validated Transcript objects if any transcript
            is available, otherwise None.
        """

        transcript_list = yt_api.list(video_id)

        for transcript in transcript_list:
            raw = transcript.fetch().to_raw_data()
            return self._convert_to_transcript_object(raw)

        return None

    def _fetch_by_languages(
        self,
        yt_api: YouTubeTranscriptApi,
        video_id: str
    ) -> list[Transcript] | None:
        """
        Fetches a transcript matching the configured language priority.

        Uses the YouTubeTranscriptApi `fetch` method to automatically
        select a transcript based on the provided language codes in
        descending priority.

        Args:
            yt_api: Initialized YouTubeTranscriptApi instance.
            video_id: YouTube video ID.

        Returns:
            A list of validated Transcript objects corresponding to
            the matched language selection.

        Raises:
            NoTranscriptFound: If no transcript matches the language criteria.
            Other API-related exceptions may propagate to the caller.
        """

        assert self.languages is not None, "languages must not be None here."

        try:
            raw = yt_api.fetch(
                video_id=video_id,
                languages=self.languages
            ).to_raw_data()

            return self._convert_to_transcript_object(raw)
        except NoTranscriptFound:
            logger.info(f'No transcript found for {video_id} with languages {self.languages}')
            return None

    @staticmethod
    def _collect_results(tasks: list[futures.Future]) -> list[VideoTranscript]:
        """
        Collects successful VideoTranscript objects from completed futures.

        Iterates over completed futures from the thread pool, extracts
        non-None results, and returns them as a list. Progress is displayed
        using a tqdm progress bar unless disabled.

        Args:
            tasks: List of Future objects representing in-progress transcript
                fetch operations.

        Returns:
            List of successfully fetched VideoTranscript objects.
        """
        results: list[VideoTranscript] = []

        for future in tqdm(futures.as_completed(tasks), total=len(tasks), desc="Fetching transcripts", unit='transcript', disable=should_disable_progress()):
            result: VideoTranscript = future.result()
            if result:
                results.append(result)
        return results

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
        """
        Converts raw transcript dictionaries to Transcript model objects.

        Uses Pydantic model validation to ensure each dictionary conforms to
        the Transcript model schema. Assumes all input dictionaries are valid
        and complete.

        Args:
            transcript_dict: List of dictionaries containing raw transcript data
                with fields like text, start, and duration.

        Returns:
            List of validated Transcript model objects.
        """
        # No need for exception handling, transcripts should be complete.
        return [Transcript.model_validate(transcript) for transcript in transcript_dict]

