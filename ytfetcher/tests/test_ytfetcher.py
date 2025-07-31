import pytest
from ytfetcher.core import YTFetcher
from ytfetcher.types.channel import (
    ChannelData,
    Snippet,
    Thumbnails,
    Thumbnail,
    Transcript,
    VideoTranscript,
    VideoMetadata
)
from ytfetcher.config.http_config import HTTPConfig
from ytfetcher.exceptions import *
from ytfetcher.youtube_v3 import YoutubeV3
from ytfetcher.transcript_fetcher import TranscriptFetcher
from youtube_transcript_api.proxies import ProxyConfig
from httpx import Timeout
from scripts.headers import get_realistic_headers
from unittest.mock import AsyncMock, MagicMock, create_autospec
from pytest_mock import MockerFixture

# --- Fixtures for test setup ---
@pytest.fixture
def sample_video_ids():
    return ["video1", "video2"]

@pytest.fixture
def sample_channel_name():
    return "test_channel"

@pytest.fixture
def mock_http_config():
    return HTTPConfig()

@pytest.fixture
def sample_snippet():
    return Snippet(
        title="channelname1",
        description="description1",
        publishedAt="somedate1",
        channelId="id1",
        thumbnails=Thumbnails(
            default=Thumbnail(url="url1", width=1, height=1)
        ),
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
def patch_fetchers(mocker: MockerFixture, sample_video_ids, sample_snippet, sample_transcripts):
    mock_youtube_v3 = mocker.patch.object(YoutubeV3, 'fetch_channel_snippets', return_value=
        VideoMetadata(
            video_ids=sample_video_ids,
            metadata=[
                sample_snippet
            ]
        )
    )
    mock_transcript_fetcher = mocker.patch.object(TranscriptFetcher, 'fetch', return_value=[
        VideoTranscript(
            video_id="video_1",
            transcripts=sample_transcripts
        )
    ])

    return mock_youtube_v3, mock_transcript_fetcher

@pytest.fixture
def initialize_ytfetcher_with_channel_name(mock_http_config, sample_channel_name):
    fetcher = YTFetcher.from_channel(
        api_key="test_api_key",
        channel_handle=sample_channel_name,
        max_results=5,
        http_config=mock_http_config
    )

    return fetcher

@pytest.fixture
def initialize_ytfetcher_with_video_ids(mock_http_config, sample_video_ids):
    fetcher = YTFetcher.from_video_ids(
        api_key="test_api_key",
        video_ids=sample_video_ids,
        http_config=mock_http_config
    )

    return fetcher

# --- Tests ---
@pytest.mark.asyncio
async def test_fetch_youtube_data_from_video_ids(
    sample_video_ids,
    mock_http_config,
    patch_fetchers,
    initialize_ytfetcher_with_video_ids,
    mocker: MockerFixture
):
    fetcher = initialize_ytfetcher_with_video_ids
    results = await fetcher.fetch_youtube_data()
    print(results)
    
    assert len(results) == 1
    assert isinstance(results[0], ChannelData)
    assert results[0].metadata.channelId == 'id1'
    assert results[0].metadata.description == 'description1'
    assert results[0].transcripts[0].text == 'text1'


@pytest.mark.asyncio
async def test_fetch_youtube_data_from_channel_name(
    patch_fetchers,
    initialize_ytfetcher_with_channel_name,
    sample_channel_name,
    mock_http_config
):
    fetcher = initialize_ytfetcher_with_channel_name
    results = await fetcher.fetch_youtube_data()

    assert len(results) == 1
    assert isinstance(results[0], ChannelData)
    assert results[0].metadata.channelId == 'id1'
    assert results[0].metadata.description == 'description1'
    assert results[0].transcripts[0].text == 'text1'

@pytest.mark.asyncio
async def test_fetch_transcripts_method_with_channel_name(patch_fetchers, initialize_ytfetcher_with_channel_name):
    fetcher = initialize_ytfetcher_with_channel_name
    results = await fetcher.fetch_transcripts()

    assert len(results) == 1
    assert isinstance(results[0], VideoTranscript)
    assert isinstance(results[0].transcripts[0], Transcript)
    assert results[0].video_id == 'video_1'
    assert results[0].transcripts[0].text == 'text1'

def test_fetch_snippets_method_with_channel_name(patch_fetchers, initialize_ytfetcher_with_channel_name, sample_video_ids):
    fetcher = initialize_ytfetcher_with_channel_name
    results = fetcher.fetch_snippets()

    assert isinstance(results, VideoMetadata)
    assert isinstance(results.metadata[0], Snippet)
    assert results.video_ids == sample_video_ids
    assert results.metadata[0].title == 'channelname1'

@pytest.mark.asyncio
async def test_fetch_transcripts_method_with_video_ids(patch_fetchers, initialize_ytfetcher_with_video_ids):
    fetcher = initialize_ytfetcher_with_video_ids
    results = await fetcher.fetch_transcripts()

    assert len(results) == 1
    assert isinstance(results[0], VideoTranscript)
    assert isinstance(results[0].transcripts[0], Transcript)
    assert results[0].video_id == 'video_1'
    assert results[0].transcripts[0].text == 'text1'

def test_fetch_snippets_method_with_video_ids(patch_fetchers, initialize_ytfetcher_with_video_ids, sample_video_ids):
    fetcher = initialize_ytfetcher_with_video_ids
    results = fetcher.fetch_snippets()

    assert isinstance(results, VideoMetadata)
    assert isinstance(results.metadata[0], Snippet)
    assert results.video_ids == sample_video_ids
    assert results.metadata[0].title == 'channelname1'

def test_http_config(patch_fetchers, sample_channel_name):

    headers = get_realistic_headers()
    config = HTTPConfig(timeout=Timeout(2.0), headers=headers)

    fetcher = YTFetcher.from_channel(
        api_key="test_api_key",
        channel_handle=sample_channel_name,
        max_results=5,
        http_config=config
    )

    assert fetcher.http_config.headers == config.headers
    assert fetcher.http_config.timeout == config.timeout

def test_proxy_config(patch_fetchers, sample_channel_name, sample_video_ids):
    proxy_config_mock = create_autospec(ProxyConfig, instance=True)

    fetcher = YTFetcher(
        api_key="test_api_key",
        channel_handle=sample_channel_name,
        max_results=5,
        video_ids=sample_video_ids,
        http_config=HTTPConfig(),
        proxy_config=proxy_config_mock
    )

    assert fetcher.proxy_config is proxy_config_mock