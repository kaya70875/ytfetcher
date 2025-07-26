import pytest
import asyncio
import time
import httpx
from pytest_mock import MockerFixture
from unittest.mock import MagicMock
from ytfetcher.types.channel import Snippet, Thumbnail, Thumbnails, FetchAndMetaResponse
from ytfetcher.transcript_fetcher import TranscriptFetcher
from ytfetcher.config.http_config import HTTPConfig
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._transcripts import FetchedTranscript, FetchedTranscriptSnippet
from youtube_transcript_api.proxies import GenericProxyConfig

@pytest.fixture
def mock_video_ids():
    return ['video1', 'video2']

@pytest.fixture
def mock_snippets():
    return [
        Snippet(
        title="channelname1",
        description="description1",
        publishedAt="somedate1",
        channelId="id1",
        thumbnails=Thumbnails(
            default=Thumbnail(url="url1", width=1, height=1)
        ),
    ), Snippet(
        title="channelname2",
        description="description2",
        publishedAt="somedate2",
        channelId="id2",
        thumbnails=Thumbnails(
            default=Thumbnail(url="url2", width=2, height=2)
        ),
    )
    ]

@pytest.mark.asyncio
async def test_fetch_method_returns_correct_data(mocker: MockerFixture, mock_video_ids, mock_snippets):

    fetcher = TranscriptFetcher(mock_video_ids, mock_snippets)
    mocker.patch.object(
        fetcher,
        "_fetch_single",
        return_value={
            "video_id": "video_id",
            "transcript": [{"text": "text1", "start": 1, "duration": 1}],
            "snippet": {
                "title": "channelname2",
                "description": "description2",
                "publishedAt": "somedate2",
                "channelId": "id2",
                "thumbnails": {
                    "default": {"url": "url2", "width": 2, "height": 2}
                }
            }
        }
    )
    
    results = await fetcher.fetch()

    assert isinstance(results[0], FetchAndMetaResponse)
    assert results[0].transcript[0]['text'] == 'text1'
    assert results[0].video_id == 'video_id'
    assert results[0].snippet.description == 'description2'
    assert results[0].snippet.channelId == 'id2'

def test_fetch_single_returns_correct_data(mocker: MockerFixture, mock_video_ids, mock_snippets):
    fetcher = TranscriptFetcher(mock_video_ids, mock_snippets)

    mocker.patch.object(YouTubeTranscriptApi, "fetch", 
        return_value=FetchedTranscript([FetchedTranscriptSnippet(text="text", start=1, duration=1)], fetcher.video_ids[0], "en", "", True)
    )

    results = fetcher._fetch_single(fetcher.video_ids[0], fetcher.snippets[0])

    assert results['video_id'] == fetcher.video_ids[0]
    assert results['transcript'][0] == {'text': 'text', 'start': 1, 'duration': 1}
    assert results['snippet'] == mock_snippets[0].model_dump()

def test_concurrent_fetching(mocker, mock_snippets, mock_video_ids):
    # Mock the YouTube API to simulate delayed responses
    mock_fetch = mocker.patch.object(
        YouTubeTranscriptApi, 
        "fetch",
        side_effect=lambda *args, **kwargs: MagicMock(
            to_raw_data=lambda: [{"text": "test", "start": 0, "duration": 1}]
        )
    )
    
    # Create a fetcher with 2 video IDs
    fetcher = TranscriptFetcher(mock_video_ids, mock_snippets)
    
    # Time the execution (should be ~1s, not 2s if parallel)
    start_time = time.time()
    results = asyncio.run(fetcher.fetch())
    elapsed = time.time() - start_time
    
    assert len(results) == 2
    assert elapsed < 1.5  # Should complete in ~1s if parallel
    assert mock_fetch.call_count == 2

def test_custom_ytt_api_client_initialized_correctly():
    fetcher = TranscriptFetcher(mock_video_ids, mock_snippets, http_config=HTTPConfig(timeout=httpx.Timeout(2.0)), proxy_config=GenericProxyConfig(
        http_url='http://test:800'
    ))
    ytt_api = YouTubeTranscriptApi(http_client=fetcher.http_client, proxy_config=fetcher.proxy_config)
    
    print(ytt_api._fetcher._http_client.proxies)

    assert ytt_api._fetcher._http_client.headers.get('User-Agent') is not None
    assert ytt_api._fetcher._http_client.headers.get("Referer") is not None
    assert ytt_api._fetcher._http_client.proxies == {'http': 'http://test:800', 'https': 'http://test:800'}