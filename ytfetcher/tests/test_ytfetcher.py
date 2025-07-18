import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, create_autospec
from pytest_mock import MockerFixture
from ytfetcher.core import YTFetcher
from ytfetcher.types.channel import (
    FetchAndMetaResponse,
    Snippet,
    Thumbnails,
    Thumbnail,
)
from ytfetcher.config.http_config import HTTPConfig
from youtube_transcript_api.proxies import ProxyConfig
from ytfetcher.youtube_v3 import YoutubeV3
from ytfetcher.exceptions import *
from httpx import Timeout
from scripts.headers import get_realistic_headers

# --- Fixtures for test setup ---
@pytest.fixture
def mock_video_ids():
    return ["video1", "video2"]

@pytest.fixture
def mock_channel_name():
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
def mock_transcript_response(sample_snippet):
    return [
        FetchAndMetaResponse(
            video_id="video1",
            transcript=[{"text": "text1", "start": 0, "duration": 0}],
            snippet=sample_snippet
        )
    ]

# --- Helper to patch fetchers ---
@pytest.fixture
def patch_fetchers(mocker: MockerFixture, mock_video_ids, mock_transcript_response):
    mock_youtube_v3 = mocker.patch("ytfetcher.core.YoutubeV3")
    mock_transcript_fetcher = mocker.patch("ytfetcher.core.TranscriptFetcher")

    mock_youtube_v3.return_value.fetch_channel_snippets.return_value = MagicMock(
        video_ids=mock_video_ids,
        metadata=[{"video_id": vid, "title": f"Video {vid}"} for vid in mock_video_ids],
    )

    mock_transcript_fetcher.return_value.fetch = AsyncMock(return_value=mock_transcript_response)

    return mock_youtube_v3, mock_transcript_fetcher


# --- Tests ---
@pytest.mark.asyncio
async def test_get_youtube_data_from_video_ids(
    patch_fetchers,
    mock_video_ids,
    mock_http_config
):
    fetcher = YTFetcher.from_video_ids(
        api_key="test_api_key",
        video_ids=mock_video_ids,
        http_config=mock_http_config,
    )
    results = await fetcher.get_youtube_data()
    
    assert len(results) == 1
    assert isinstance(results[0], FetchAndMetaResponse)
    assert results[0].snippet.channelId == 'id1'
    assert results[0].snippet.description == 'description1'
    assert results[0].transcript[0]['text'] == 'text1'


@pytest.mark.asyncio
async def test_get_youtube_data_from_channel_name(
    patch_fetchers,
    mock_channel_name,
    mock_video_ids,
    mock_http_config
):
    fetcher = YTFetcher.from_channel(
        api_key="test_api_key",
        channel_handle=mock_channel_name,
        max_results=5,
        http_config=mock_http_config
    )
    results = await fetcher.get_youtube_data()

    assert len(results) == 1
    assert isinstance(results[0], FetchAndMetaResponse)
    assert results[0].snippet.channelId == 'id1'
    assert results[0].snippet.description == 'description1'
    assert results[0].transcript[0]['text'] == 'text1'

def test_http_config(patch_fetchers, mock_channel_name, mock_video_ids):

    headers = get_realistic_headers()
    config = HTTPConfig(timeout=Timeout(2.0), headers=headers)

    fetcher = YTFetcher.from_channel(
        api_key="test_api_key",
        channel_handle=mock_channel_name,
        max_results=5,
        http_config=config
    )

    assert fetcher.http_config.headers == config.headers
    assert fetcher.http_config.timeout == config.timeout

def test_proxy_config(patch_fetchers, mock_channel_name, mock_video_ids):
    proxy_config_mock = create_autospec(ProxyConfig, instance=True)

    fetcher = YTFetcher(
        api_key="test_api_key",
        channel_handle=mock_channel_name,
        max_results=5,
        video_ids=mock_video_ids,
        http_config=HTTPConfig(),
        proxy_config=proxy_config_mock
    )

    assert fetcher.proxy_config is proxy_config_mock

def test_invalid_api_key_with_403(mocker: MockerFixture):
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 403

    mock_get = mocker.patch("httpx.Client.get", return_value=mock_response)
    youtube = YoutubeV3(api_key="fake", channel_name="channel")

    with pytest.raises(InvalidApiKey):
        youtube._get_channel_id()
    
    mock_get.assert_called_once()

def test_invalid_api_key_with_400(mocker: MockerFixture):
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 400

    mock_get = mocker.patch("httpx.Client.get", return_value=mock_response)
    youtube = YoutubeV3(api_key="fake", channel_name="channel")

    with pytest.raises(InvalidApiKey):
        youtube._get_channel_id()
    
    mock_get.assert_called_once()

def test_invalid_channel_name(mocker: MockerFixture):
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {'kind': 'youtube#channelListResponse', 'etag': 'RuuXzTIr0OoDqI4S0RU6n4FqKEM', 'pageInfo': {'totalResults': 0, 'resultsPerPage': 5}}

    mock_get = mocker.patch("httpx.Client.get", return_value=mock_response)
    youtube = YoutubeV3("api_key", "none_channel")

    with pytest.raises(InvalidChannel):
        youtube._get_channel_id()
    
    mock_get.assert_called_once()