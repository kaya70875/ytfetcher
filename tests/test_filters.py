import pytest
from unittest.mock import patch
from ytfetcher.models import DLSnippet
from ytfetcher import YTFetcher
from ytfetcher.filters import filter_by_title, min_views, min_duration

@pytest.fixture
def sample_snippets():
    return [
        DLSnippet(
        video_id='id1',
        title="channelname1",
        description="description1",
        url='https://youtube.com/videoid',
        duration=2800,
        view_count=20
        ),
        DLSnippet(
        video_id='id1',
        title="namechannel1",
        description="description1",
        url='https://youtube.com/videoid',
        duration=900,
        view_count=2000
        )
    ]

@pytest.fixture
def sample_missing_snippets():
    return [
        DLSnippet(
        video_id='id1',
        title="channelname1",
        description="description1",
        url='https://youtube.com/videoid',
        duration=None,
        view_count=None
        ),
        DLSnippet(
        video_id='id1',
        title="channelname1",
        description="description1",
        url='https://youtube.com/videoid',
        duration=1000,
        view_count=None
        )
    ]

@pytest.fixture
def setup_mock_fetcher():
    def _setup(mock_get_fetcher, snippets):
        mock_instance = mock_get_fetcher.return_value
        mock_instance.fetch.return_value = snippets
        return mock_instance
    return _setup

@patch('ytfetcher._core.get_fetcher')
def test_filter_snippets_returns_filtered_data(mock_get_ytfetcher, setup_mock_fetcher, sample_snippets):
    setup_mock_fetcher(mock_get_ytfetcher, sample_snippets)
    fetcher = YTFetcher.from_channel(channel_handle='channel', filters=[
        min_views(1000),
    ])

    assert len(fetcher.snippets) == 1
    assert fetcher.snippets[0] == sample_snippets[1]

    fetcher = YTFetcher.from_channel(channel_handle='channel', filters=[
        filter_by_title('name'),
    ])

    assert len(fetcher.snippets) == 1
    assert fetcher.snippets[0] == sample_snippets[1]

@patch('ytfetcher._core.get_fetcher')
def test_filter_snippets_returns_empty_list(mock_get_ytfetcher, setup_mock_fetcher, sample_snippets):
    setup_mock_fetcher(mock_get_ytfetcher, sample_snippets)
    fetcher = YTFetcher.from_channel(channel_handle='channel', filters=[
        min_views(100000),
    ])

    assert len(fetcher.snippets) == 0
    assert fetcher.snippets == []

@patch('ytfetcher._core.get_fetcher')
def test_filter_snippets_with_multiple_filters(mock_get_ytfetcher, setup_mock_fetcher, sample_missing_snippets):
    setup_mock_fetcher(mock_get_ytfetcher, sample_missing_snippets)
    fetcher = YTFetcher.from_channel(channel_handle='channel', filters=[
        min_duration(10000)
    ])

    assert len(fetcher.snippets) == 0
    assert fetcher.snippets == []

    fetcher = YTFetcher.from_channel(channel_handle='channel', filters=[
        min_duration(900)
    ])

    assert len(fetcher.snippets) == 1
    assert fetcher.snippets[0] == sample_missing_snippets[1]