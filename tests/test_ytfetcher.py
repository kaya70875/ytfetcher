import pytest
from ytfetcher._core import YTFetcher
from ytfetcher.models.channel import (
    ChannelData,
    DLSnippet,
    Transcript,
    VideoTranscript
)
from ytfetcher.config.http_config import HTTPConfig
from ytfetcher.config.fetch_config import FetchOptions
from ytfetcher.exceptions import *
from ytfetcher._transcript_fetcher import TranscriptFetcher
from youtube_transcript_api.proxies import ProxyConfig
from ytfetcher.utils.headers import get_realistic_headers
from unittest.mock import create_autospec, MagicMock
from pytest_mock import MockerFixture

# --- Fixtures for test setup ---

@pytest.fixture
def mock_http_config():
    return HTTPConfig()

@pytest.fixture
def sample_snippet():
    return DLSnippet(
        video_id='id1',
        title="channelname1",
        description="description1",
        url='https://youtube.com/videoid',
        duration=25.400,
        view_count=2000
    )

@pytest.fixture
def sample_transcripts():
    return [
        Transcript(
            text='text1',
            start=1,
            duration=1
        ),
        Transcript(
            text='text2',
            start=2,
            duration=2
        )
    ]

# --- Helper to patch fetchers ---

@pytest.fixture
def mock_channel_fetcher_class(mocker, sample_snippet):
    mock_instance = MagicMock()
    mock_instance.fetch.return_value = [sample_snippet]

    mocker.patch('ytfetcher._core.ChannelFetcher', return_value=mock_instance)
    return mock_instance

@pytest.fixture
def mock_video_fetcher_class(mocker, sample_snippet):
    mock_instance = MagicMock()
    mock_instance.fetch.return_value = [sample_snippet]

    mocker.patch('ytfetcher._core.VideoListFetcher', return_value=mock_instance)
    return mock_instance

@pytest.fixture
def mock_search_fetcher_class(mocker, sample_snippet):
    mock_instance = MagicMock()
    mock_instance.fetch.return_value = [sample_snippet]

    mocker.patch('ytfetcher._core.SearchFetcher', return_value=mock_instance)
    return mock_instance

@pytest.fixture
def mock_transcript_fetcher(mocker: MockerFixture, sample_transcripts):
    mock_transcript_fetcher = mocker.patch.object(TranscriptFetcher, 'fetch', return_value=[
        VideoTranscript(
            video_id="id1",
            transcripts=sample_transcripts,
        )
    ])

    return mock_transcript_fetcher

@pytest.fixture
def initialize_ytfetcher_with_channel_name(mock_channel_fetcher_class):
    fetcher = YTFetcher.from_channel(
        channel_handle='test_channel',
        max_results=5,
    )

    return fetcher

@pytest.fixture
def initialize_ytfetcher_with_video_ids(mock_video_fetcher_class):
    fetcher = YTFetcher.from_video_ids(
        video_ids=['video1', 'video2'],
    )

    return fetcher

@pytest.fixture
def initialize_ytfetcher_with_search(mock_search_fetcher_class):
    fetcher = YTFetcher.from_search(
        query='query',
    )

    return fetcher

# --- Tests ---
def test_fetch_youtube_data_from_video_ids(
    mock_transcript_fetcher,
    initialize_ytfetcher_with_video_ids,
):
    fetcher = initialize_ytfetcher_with_video_ids
    results = fetcher.fetch_youtube_data()
    
    assert len(results) == 1
    assert isinstance(results[0], ChannelData)
    assert results[0].metadata.title == 'channelname1'
    assert results[0].metadata.description == 'description1'
    assert results[0].transcripts[0].text == 'text1'


def test_fetch_youtube_data_from_channel_name(
    mock_transcript_fetcher,
    initialize_ytfetcher_with_channel_name,
):
    fetcher = initialize_ytfetcher_with_channel_name
    results = fetcher.fetch_youtube_data()

    assert len(results) == 1
    assert isinstance(results[0], ChannelData)
    assert results[0].metadata.title == 'channelname1'
    assert results[0].metadata.description == 'description1'
    assert results[0].transcripts[0].text == 'text1'

def test_fetch_youtube_data_from_search(
    mock_transcript_fetcher,
    initialize_ytfetcher_with_search,
):
    fetcher = initialize_ytfetcher_with_search
    results = fetcher.fetch_youtube_data()

    assert len(results) == 1
    assert isinstance(results[0], ChannelData)
    assert results[0].metadata.title == 'channelname1'
    assert results[0].metadata.description == 'description1'
    assert results[0].transcripts[0].text == 'text1'

def test_fetch_transcripts_method_with_channel_name(mock_transcript_fetcher, initialize_ytfetcher_with_channel_name):
    fetcher = initialize_ytfetcher_with_channel_name
    results = fetcher.fetch_transcripts()

    assert len(results) == 1
    assert isinstance(results[0], ChannelData)
    assert isinstance(results[0].transcripts[0], Transcript)
    assert results[0].video_id == 'id1'
    assert results[0].transcripts[0].text == 'text1'
    assert results[0].metadata == None

def test_fetch_snippets_method_with_channel_name(initialize_ytfetcher_with_channel_name):
    fetcher = initialize_ytfetcher_with_channel_name
    results = fetcher.fetch_snippets()

    assert isinstance(results[0], ChannelData)
    assert results[0].video_id == 'id1'
    assert results[0].metadata.title == 'channelname1'

def test_fetch_transcripts_method_with_video_ids(mock_transcript_fetcher, initialize_ytfetcher_with_video_ids):
    fetcher = initialize_ytfetcher_with_video_ids
    results = fetcher.fetch_transcripts()

    assert len(results) == 1
    assert isinstance(results[0], ChannelData)
    assert isinstance(results[0].transcripts[0], Transcript)
    assert results[0].video_id == 'id1'
    assert results[0].transcripts[0].text == 'text1'
    assert results[0].metadata == None

def test_http_config(mock_transcript_fetcher):

    headers = get_realistic_headers()
    config = HTTPConfig(headers=headers)

    fetcher = YTFetcher.from_channel(
        channel_handle='channelname',
        max_results=5,
        options=FetchOptions(http_config=config)
    )

    assert fetcher.options.http_config.headers == config.headers

def test_proxy_config(mock_transcript_fetcher, mock_channel_fetcher_class):
    proxy_config_mock = create_autospec(ProxyConfig, instance=True)

    fetcher = YTFetcher(
        youtube_dl_fetcher=mock_channel_fetcher_class,
        options=FetchOptions(
            http_config=HTTPConfig(),
            proxy_config=proxy_config_mock
            )
    )

    assert fetcher.options.proxy_config is proxy_config_mock