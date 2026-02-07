import pytest
import time
from pytest_mock import MockerFixture
from unittest.mock import MagicMock
from ytfetcher.models.channel import VideoTranscript, Transcript, ChannelData
from ytfetcher._transcript_fetcher import TranscriptFetcher
from ytfetcher.config.http_config import HTTPConfig
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._transcripts import FetchedTranscript, FetchedTranscriptSnippet
from youtube_transcript_api.proxies import GenericProxyConfig

@pytest.fixture
def mock_video_ids():
    return ['video1', 'video2']

@pytest.fixture
def mock_transcripts():
    return [
        Transcript(
                text='text1',
                duration=1,
                start=1
        ),
        Transcript(
                text='text2',
                duration=2,
                start=2
        )
    ]

def test_fetch_method_returns_correct_data(mocker: MockerFixture, mock_video_ids, mock_transcripts):

    fetcher = TranscriptFetcher(mock_video_ids)
    mocker.patch.object(
        fetcher,
        "_fetch_single",
        return_value=VideoTranscript(
            video_id='video_id',
            transcripts=mock_transcripts
        )
    )
    
    results = fetcher.fetch()

    assert isinstance(results[0], VideoTranscript)
    assert results[0].transcripts[0].text == 'text1'
    assert results[0].video_id == 'video_id'

def test_fetch_single_returns_correct_data(mocker: MockerFixture, mock_video_ids):
    fetcher = TranscriptFetcher(mock_video_ids)

    mocker.patch.object(YouTubeTranscriptApi, "fetch", 
        return_value=FetchedTranscript([FetchedTranscriptSnippet(text="text", start=1, duration=1)], fetcher.video_ids[0], "en", "", True)
    )

    results = fetcher._fetch_single(fetcher.video_ids[0])

    assert isinstance(results.transcripts[0], Transcript)
    assert results.video_id == fetcher.video_ids[0]
    assert results.transcripts[0] == Transcript(
        text='text',
        start=1,
        duration=1
    )
    assert results.transcripts[0].text == 'text'

def test_concurrent_fetching(mocker, mock_video_ids):
    mock_fetch = mocker.patch.object(
        YouTubeTranscriptApi, 
        "fetch",
        side_effect=lambda *args, **kwargs: MagicMock(
            to_raw_data=lambda: [{"text": "test", "start": 0, "duration": 1}]
        )
    )
    
    fetcher = TranscriptFetcher(mock_video_ids)
    
    start_time = time.time()
    results = fetcher.fetch()
    elapsed = time.time() - start_time
    
    assert len(results) == 2
    assert elapsed < 1.5
    assert mock_fetch.call_count == 2

def test_custom_ytt_api_client_initialized_correctly(mocker):
    mock_api = mocker.patch("ytfetcher._transcript_fetcher.YouTubeTranscriptApi")

    fetcher = TranscriptFetcher(
        mock_video_ids,
        http_config=HTTPConfig(),
        proxy_config=GenericProxyConfig(http_url="http://test:800"),
    )

    fetcher._fetch_single("video123")

    mock_api.assert_called_once()

    assert fetcher.http_config.headers.get('User-Agent') is not None
    assert fetcher.http_config.headers.get('Referer') is not None
    assert fetcher.proxy_config.to_requests_dict() == {
        "http": "http://test:800",
        "https": "http://test:800",
    }

def test_clean_transcripts():

    test_response = [
        Transcript(
            text="[Music] >> This is some text",
            duration=1,
            start=1
        )
    ]

    cleaned_response = TranscriptFetcher._clean_transcripts(test_response)

    assert cleaned_response[0].text == 'This is some text'

def test_clean_transcripts_with_multiple_text():
    test_response = [
        Transcript(
            text="[Music][Applause] and that happened!",
            duration=1,
            start=1
        )
    ]

    cleaned_response = TranscriptFetcher._clean_transcripts(test_response)
    
    assert cleaned_response[0].text == 'and that happened!'