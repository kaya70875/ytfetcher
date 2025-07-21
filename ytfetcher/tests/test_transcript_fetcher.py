import pytest
from pytest_mock import MockerFixture
from unittest.mock import MagicMock
from ytfetcher.types.channel import Snippet, Thumbnail, Thumbnails, Transcript, FetchAndMetaResponse
from ytfetcher.transcript_fetcher import TranscriptFetcher

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

def test_thread_behavior():
    pass

def test_fetch_single_returns_correct_data():
    pass