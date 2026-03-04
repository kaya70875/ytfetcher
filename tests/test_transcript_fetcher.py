import pytest
from pytest_mock import MockerFixture
from youtube_transcript_api._errors import NoTranscriptFound
from ytfetcher.models.channel import VideoTranscript, Transcript
from ytfetcher._transcript_fetcher import TranscriptFetcher
from ytfetcher.config.http_config import HTTPConfig
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

def test_decide_fetch_method_manual_branch(mocker):
    fetcher = TranscriptFetcher(
        video_ids=["abc"],
        manually_created=True,
        languages=["en"]
    )

    mock_manual = mocker.patch.object(
        fetcher,
        "_fetch_manual_transcript",
        return_value=["manual"]
    )

    mock_api = mocker.MagicMock()

    result = fetcher._decide_fetch_method(mock_api, "abc")

    assert result == ["manual"]
    mock_manual.assert_called_once_with(yt_api=mock_api, video_id="abc")

def test_decide_fetch_method_first_available_branch(mocker):
    fetcher = TranscriptFetcher(
        video_ids=["abc"],
        manually_created=False,
        languages=None
    )

    mock_first = mocker.patch.object(
        fetcher,
        "_fetch_first_available_transcript",
        return_value=["first"]
    )

    mock_api = mocker.MagicMock()

    result = fetcher._decide_fetch_method(mock_api, "abc")

    assert result == ["first"]
    mock_first.assert_called_once_with(yt_api=mock_api, video_id="abc")

def test_decide_fetch_method_by_languages_branch(mocker):
    fetcher = TranscriptFetcher(
        video_ids=["abc"],
        manually_created=False,
        languages=["en"]
    )

    mock_lang = mocker.patch.object(
        fetcher,
        "_fetch_by_languages",
        return_value=["lang"]
    )

    mock_api = mocker.MagicMock()

    result = fetcher._decide_fetch_method(mock_api, "abc")

    assert result == ["lang"]
    mock_lang.assert_called_once_with(yt_api=mock_api, video_id="abc")

def test_fetch_manual_transcript_no_transcript(mocker):
    video_id = "abc"

    mock_api = mocker.MagicMock()
    mock_list = mocker.MagicMock()

    mock_api.list.return_value = mock_list
    mock_list.find_manually_created_transcript.side_effect = NoTranscriptFound(video_id, requested_language_codes=['en'], transcript_data=None)

    fetcher = TranscriptFetcher(
        video_ids=[video_id],
        manually_created=True,
        languages=["en"]
    )

    result = fetcher._fetch_manual_transcript(mock_api, video_id)

    assert result is None

def test_fetch_first_available_transcript_empty(mocker):
    video_id = "abc"

    mock_api = mocker.MagicMock()
    mock_api.list.return_value = []

    fetcher = TranscriptFetcher(video_ids=[video_id])

    result = fetcher._fetch_first_available_transcript(mock_api, video_id)

    assert result is None
