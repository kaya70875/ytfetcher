import pytest
import time
from pytest_mock import MockerFixture
from unittest.mock import MagicMock
from ytfetcher.models.channel import VideoTranscript, Transcript
from ytfetcher._transcript_fetcher import TranscriptFetcher
from ytfetcher.config.http_config import HTTPConfig
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._transcripts import FetchedTranscript, FetchedTranscriptSnippet, TranscriptList
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

def test_fetch_single_returns_correct_data(mocker, mock_video_ids):
    fetcher = TranscriptFetcher(mock_video_ids)

    video_id = mock_video_ids[0]

    mock_transcripts = [
        Transcript(text="text", start=1, duration=1)
    ]

    mocker.patch.object(
        fetcher,
        "_decide_fetch_method",
        return_value=mock_transcripts
    )

    result = fetcher._fetch_single(video_id)

    assert isinstance(result, VideoTranscript)
    assert result.video_id == video_id
    assert result.transcripts == mock_transcripts
    assert result.transcripts[0].text == "text"


def test_concurrent_fetching(mocker, mock_video_ids):
    fetcher = TranscriptFetcher(mock_video_ids)

    mock_result = VideoTranscript(
        video_id="dummy",
        transcripts=[Transcript(text="test", start=0, duration=1)]
    )

    mock_fetch_single = mocker.patch.object(
        fetcher,
        "_fetch_single",
        return_value=mock_result
    )

    results = fetcher.fetch()

    assert len(results) == len(mock_video_ids)
    assert mock_fetch_single.call_count == len(mock_video_ids)


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