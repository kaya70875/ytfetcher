import pytest
from unittest.mock import patch, MagicMock
from ytfetcher.models import DLSnippet
from ytfetcher import YTFetcher
from ytfetcher.filters import filter_by_title, min_views, min_duration
from ytfetcher.config.fetch_config import FetchOptions

@pytest.fixture
def sample_snippets():
    return [
        DLSnippet(
        video_id='id1',
        title="channel1",
        description="description1",
        url='https://youtube.com/videoid',
        duration=2800,
        view_count=20
        ),
        DLSnippet(
        video_id='id1',
        title="Namechannel1",
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
def mock_channel_fetcher_class(mocker, sample_snippets):
    mock_instance = MagicMock()
    mock_instance.fetch.return_value = sample_snippets

    mocker.patch('ytfetcher._core.ChannelFetcher', return_value=mock_instance)
    return mock_instance

@pytest.fixture
def mock_channel_fetcher_class_with_broken_snippets(mocker, sample_missing_snippets):
    mock_instance = MagicMock()
    mock_instance.fetch.return_value = sample_missing_snippets

    mocker.patch('ytfetcher._core.ChannelFetcher', return_value=mock_instance)
    return mock_instance

def test_filter_snippets_returns_filtered_data(mock_channel_fetcher_class, sample_snippets):
    fetcher = YTFetcher.from_channel(channel_handle='channel', options=FetchOptions(filters=[
        min_views(1000),
    ]))

    channel_data = fetcher.fetch_snippets()
    snippets = channel_data[0].metadata

    assert len(channel_data) == 1
    assert snippets == sample_snippets[1]

    fetcher = YTFetcher.from_channel(channel_handle='channel', options=FetchOptions(filters=[
        filter_by_title('name'),
    ]))

    assert len(channel_data) == 1
    assert snippets == sample_snippets[1]

def test_filter_snippets_returns_empty_list(mock_channel_fetcher_class, sample_snippets):
    fetcher = YTFetcher.from_channel(channel_handle='channel', options=FetchOptions(filters=[
        min_views(100000),
    ]))

    channel_data = fetcher.fetch_snippets()

    assert len(channel_data) == 0
    assert channel_data == []

def test_filter_snippets_with_multiple_filters(mock_channel_fetcher_class_with_broken_snippets, sample_missing_snippets):
    fetcher = YTFetcher.from_channel(channel_handle='channel', options=FetchOptions(filters=[
        min_duration(10000)
    ]))

    channel_data = fetcher.fetch_snippets()

    assert len(channel_data) == 0
    assert channel_data == []

    fetcher = YTFetcher.from_channel(channel_handle='channel', options=FetchOptions(filters=[
        min_duration(900)
    ]))

    channel_data = fetcher.fetch_snippets()
    snippets = channel_data[0].metadata

    assert len(channel_data) == 1
    assert snippets == sample_missing_snippets[1]

def test_filter_snippets_with_case_sensitivity(mock_channel_fetcher_class, sample_snippets):
    fetcher = YTFetcher.from_channel(channel_handle='channel', options=FetchOptions(filters=[
        filter_by_title('NAME')
    ]))

    channel_data = fetcher.fetch_snippets()
    snippets = channel_data[0].metadata

    assert len(fetcher.options.filters) == 1
    assert snippets == sample_snippets[1]

def test_filter_snippets_with_boundary_values(mock_channel_fetcher_class, sample_snippets):
    fetcher = YTFetcher.from_channel(channel_handle='channel', options=FetchOptions(filters=[
        min_duration(900),
        min_views(20)
    ]))

    channel_data = fetcher.fetch_snippets()

    assert len(channel_data) == 2
    assert len(fetcher.options.filters) == 2